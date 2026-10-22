"""Harness for SkyyGear 0.3.37 (Balance P7 costs on the coin curve + combat gear into Smithing + craft rarity + boss list - tools/gear_0_3_37_patch.py).
Build first:
    python tools/gear_0_3_37_patch.py && python SkyyGear/build_skyygear_0.3.37.py
    python SkyyGear/test_skyygear_0.3.37.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system, setup order migrateP6 -> migrateP7 -> load,
              the bench veto sits in GearCraftPreSys (after the Mythic / UT pack block, before the lifelong-tool refusal), the Smithing craft rolls
              through smithDoc, bossRoll / points read loot.notBosses
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.36 -> 0.3.37 (EXPECT below)
  X  exec     EXECUTES the new paths in a bare JVM:
              X1 the coin curve: GearCfg.curveOwn = tools/balance_model.py p7_curve_from_text at every level 0..200; coinCurve takes SkyyCoins'
                 coins:fn:curve (stand-in), junk / missing -> the own copy; p7round 10 / 100 / 500 / 5,000
              X2 the costs: costReforge / costLevelUp / costIdentify of every rarity at Lv 1, 10, 28, 50, 64, 90, 100 = the model's p7_gear_cost
                 (Rare reforge 420 / 15,500 / 195,000 at Lv 10 / 50 / 90); cost.curve off = base + per x level; a per-level column still adds
              X3 Smithing combat: SMC_IDS sorted + binary search, plain weapons / armor in, Mining / Foraging / tools / named weapons out; the bench
                 veto benchWhy (plain -> Smithing tab, named -> loot only, gathering / tools / UT -> null, smith.combat off -> null); offBench;
                 GearSmith.shown (0 / 2 only with smith.combat)
              X4 craft rarity: craftRarityMob 20,000 rolls follow the MOB odds (Normal .. Fabled), never Mythic / Set / Untiered; with every weight
                 on Mythic / Untiered / Set it is capped to Fabled / Normal; the bench roll (craftRarity) never Mythic / Untiered either
              X5 Sigils: a Mythic Sigil on a crafted piece (src craft) is refused (CRAFTMY), on a dropped piece it works; Fabled on crafted works
              X6 elites: notBoss (Skeleton_Elite, Skeleton_Elite_Phase_2 yes; Goblin_Duke, Trork_Chieftain, Dragon_Fire no; patterns); GearLuck.points
                 of a boss-ranked Skeleton_Elite = the elite points (not 0)
              X7 hp7Update on the REAL 0.3.36 default file: only the 24 cost rows move + cost.curve=true appended (Properties), marker, a second
                 run null, a hand-edited cost row kept + noted -> cost.curve=false appended, CRLF kept, p7Same; hp7Log rows as cost.reforge[rare]
  D  live     migrate0330 + migrateP4 + migrateP5 + migrateP6 + migrateP7 on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear/config.properties:
              migrateP7 changes only planned keys, config-history copy, change-log lines; a SECOND start changes nothing; the file loads (Rare
              reforge Lv 50 = 15,500 when the rows were untouched)
  AA engine-access audit
Scratch: tools/dev/scratch/balp7/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, math, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.37"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "gear")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.36.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_37_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.36.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],
          "GearCfg": ["+f COST_CURVE", "+f CV_F", "+f CV_LV", "+f HP7_ADDK", "+f HP7_ADDV", "+f HP7_KEYS", "+f HP7_MARK", "+f HP7_MARK_ID", "+f HP7_NEW", "+f HP7_OLD",
                      "+f HP7_TBK", "+f HP7_TBL", "+f HP7_WHO", "+f NOT_BOSS", "+f SMITH_COMBAT", "+m coinCurve", "+m curveOwn", "+m curveTag", "+m curved", "+m hp7Lk",
                      "+m hp7Log", "+m hp7Lv", "+m hp7Update", "+m migrateP7", "+m p7Same", "+m p7round", "~<clinit>", "~m apply", "~m costIdentify", "~m costLevelUp",
                      "~m costReforge", "~m defaultsText"],
          "GearCraftPreSys": ["~m handle"], "GearLuck": ["~m points"],
          "GearPack": ["+f LOOT_IDS", "+f SMC_ASETS", "+f SMC_IDS", "+f SMC_MET", "+f SMC_N", "+m benchWhy", "+m combatGear", "+m combatId", "+m gearInput", "+m glob",
                       "+m inLoot", "+m notBoss", "+m offBench", "+m smcText", "+m smithOn",
                       "~<clinit>", "~m bossRoll"],
          "GearRoll": ["+m craftRarityMob"], "GearSigil": ["+f CRAFTMY", "~m why"],
          "GearSmith": ["+m smithDoc", "~<clinit>", "~m craft", "~m groups", "~m lockWhy", "~m shown"],
          "IdentifyPage": ["~m detail"], "ReforgePage": ["~m anHelp", "~m anvil"],          # the cost lists say "at Lv 10"
          "SkyyGearPlugin": ["~m setup"], "SmithFn": ["~m apply"], "SmithPage": ["~m build", "~m left"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


_saved_run = HK.run
HK.run = lambda *a, **k: None          # the 0.3.36 harness module calls HK.run at import - a no-op while it is loaded as a helper
T36 = tmod(os.path.join(HERE, "test_skyygear_0.3.36.py"), "tg0336")
HK.run = _saved_run
HK.run_compare = T36._RC          # the kit's own compare (0.3.37 changes no asset file)
T36.OLD_JAR = OLD_JAR
BM = T36.BM
_props = T36._props


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.37 - build script') and g.count('VERSION = "0.3.37"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", 'mk("'):
        K.check(g.count(w) == o.count(w), "S no new %s text" % w)
    su = g[g.index("@PKG@.GearCfg.migrate02();"):]
    K.check(su.index("migrateP6();") < su.index("migrateP7();") < su.index("@PKG@.GearCfg.load();"), "S setup: migrateP6 -> migrateP7 -> load")
    pre = g[g.index('event_system(gcrp, "GearCraftPreSys"'):]
    K.check(pre.index("GearPackId.special(id0)") < pre.index("GearPack.benchWhy(rc0, id0)") < pre.index("GearLL.noCraft(id0)"), "S the bench veto: after the Mythic / UT block, before the tool refusal")
    K.check(g.count("d = smithDoc(out, u, lvl);") == 1 and g.count("@PKG@.GearRoll.craftDoc(out, u, lvl);") == 1, "S the Smithing craft rolls through smithDoc (bench crafts keep craftDoc)")
    K.check("if (notBoss(role)) { SMC_N[2] = SMC_N[2] + 1L; return 0; }" in g and "@PKG@.GearPack.notBoss(role) ? pv[0] :" in g, "S bossRoll skips elites; the UT meter counts them as elites")
    K.check('if (@PKG@.GearPack.offBench((String) a[1])) return Boolean.FALSE;' in g, "S /craft (gear:fn:classShow) hides combat gear")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString, JArray, JDouble
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg = JClass(PKG + "GearCfg")
    Gp = JClass(PKG + "GearPack")
    Rl = JClass(PKG + "GearRoll")
    Sm = JClass(PKG + "GearSmith")
    Df = JClass(PKG + "GearDefs")
    # ---- X1 the curve
    worst = max(abs(float(Cfg.curveOwn(lv)) / BM.p7_curve_from_text(BM.P7_CURVE_TEXT, lv) - 1) for lv in range(0, 201))
    K.check(worst < 1e-9, "X1 curveOwn = the model's coin curve at every level (worst %.1e)" % worst)

    @JImplements("java.util.function.Function")
    class Cv(object):
        def __init__(self, a):
            self.a = a

        @JOverride
        def apply(self, x):
            return self.a
    br.put("coins:fn:curve", Cv(JClass("java.lang.Double")(3.0)))
    K.check(abs(float(Cfg.coinCurve(50)) - 3.0) < 1e-12, "X1 coinCurve takes SkyyCoins' coins:fn:curve (stand-in 3.0)")
    br.put("coins:fn:curve", Cv("junk"))
    K.check(abs(float(Cfg.coinCurve(50)) - 36.8) < 1e-9, "X1 a junk answer -> the own copy")
    br.remove("coins:fn:curve")
    K.check([int(Cfg.p7round(x)) for x in (624.0, 6256.0, 15456.0, 195720.0)] == [620, 6300, 15500, 195000], "X1 p7round 10 / 100 / 500 / 5,000")
    # ---- X2 the costs (fresh defaults: GearCfg's own field defaults = the build's P7 bases)
    R = list(BM.P7_RARITY_X)
    rid = [str(x) for x in Df.R_ID]
    K.eq([int(x) for x in Cfg.CR_BASE], [BM.P7_GEAR_BASE["reforge"][r] for r in rid], "X2 reforge bases (Lv 10) = P7_GEAR_BASE")
    K.eq([int(x) for x in Cfg.LU_BASE], [BM.P7_GEAR_BASE["levelUp"][r] for r in rid], "X2 level-up bases = P7_GEAR_BASE")
    K.eq([int(x) for x in Cfg.CI_BASE], [BM.P7_GEAR_BASE["identify"][r] for r in rid], "X2 identify bases = P7_GEAR_BASE")
    K.check(all(int(x) == 0 for x in list(Cfg.CR_PER) + list(Cfg.LU_PER) + list(Cfg.CI_PER)), "X2 every per-level column 0")
    Cfg.COST_CURVE = True
    bad = []
    for i, r in enumerate(rid):
        for L in (1, 10, 28, 50, 64, 90, 100):
            for kind, fn in (("reforge", Cfg.costReforge), ("levelUp", Cfg.costLevelUp), ("identify", Cfg.costIdentify)):
                got, want = int(fn(i, L)), BM.p7_gear_cost(kind, r, L)
                if got != want:
                    bad.append((kind, r, L, got, want))
    K.check(not bad, "X2 every cost = the model's p7_gear_cost (8 rarities x 7 levels x 3 kinds): off %s" % bad[:5])
    ri = rid.index("rare")
    K.eq([int(Cfg.costReforge(ri, L)) for L in (10, 50, 90)], [420, 15500, 195000], "X2 Rare reforge Lv 10 / 50 / 90 = 420 / 15,500 / 195,000")
    K.eq(int(Cfg.costReforge(ri, 0)), int(Cfg.costReforge(ri, 1)), "X2 level 0 counts as Lv 1")
    Cfg.CR_PER[ri] = 5
    K.eq(int(Cfg.costReforge(ri, 50)), 15500 + 250, "X2 a per-level column still adds per x level")
    Cfg.CR_PER[ri] = 0
    Cfg.COST_CURVE = False
    K.check(int(Cfg.costReforge(ri, 50)) == 420 and int(Cfg.costLevelUp(ri, 90)) == 170, "X2 cost.curve off = base + per x level (flat 420 / 170)")
    Cfg.COST_CURVE = True
    K.check(str(Cfg.curveTag()).startswith(" at Lv 10"), "X2 the cost lists say the base is the Lv 10 one")
    # ---- X3 the Smithing combat list + the bench veto
    ids = [str(x) for x in Gp.SMC_IDS]
    K.check(ids == sorted(ids) and len(ids) >= 140 and all(bool(Gp.combatId(i)) for i in ids), "X3 SMC_IDS (the bag-pool part) sorted, %d plain pieces, each passes combatId" % len(ids))
    lo = [str(x) for x in Gp.LOOT_IDS]
    K.check(lo == sorted(lo) and bool(Gp.inLoot("Weapon_Sword_Frost")) and not bool(Gp.inLoot("Weapon_Wand_Lead_SkyWynn")), "X3 LOOT_IDS sorted; Frost sword drops, the Lead wand does not")
    for i in ("Weapon_Sword_Iron", "Weapon_Sword_Lead_SkyWynn", "Weapon_Spellbook_Iron", "Weapon_Wand_Lead_SkyWynn", "Armor_Leather_Light_Chest", "Armor_Cloth_Silk_Head", "Weapon_Sword_Crude"):
        K.check(bool(Gp.combatId(i)), "X3 %s is a plain Smithing piece" % i)
    for i in ("Armor_Iron_Chest", "Armor_Mining_Lead_Chest", "Tool_Pickaxe_Iron", "Weapon_Spear_Adamantite_Saurian", "Weapon_Daggers_Fang_Doomed", "Sword_Iron_Green",
              "Weapon_Battleaxe_Iron_Blue", "Weapon_Sword_Frost", "Weapon_Sword_UT_Iron", "Weapon_Fist_Wraps_Linen", "Armor_Leather_Light", "Weapon_Wand_Soul_Cage_Iron"):
        K.check(not bool(Gp.combatId(i)), "X3 %s is no plain Smithing piece" % i)
    K.check(bool(Gp.combatId("Weapon_Wand_SoulCage_Iron")) and bool(Gp.combatId("Weapon_Fist_Gauntlets_Lead_SkyWynn")) and bool(Gp.combatId("Weapon_Crossbow_Mithril_Wynn")),
            "X3 the family words Fist_<x> / <x>_SoulCage and the _Wynn suffix")
    Cfg.SMITH_COMBAT = True
    SKF = ("sacks:fn:craftList", "sacks:fn:craftPay", "sacks:fn:craftRefund", "sacks:fn:craftCommit")
    K.check(Gp.benchWhy(None, "Weapon_Sword_Iron") is None and not bool(Gp.offBench("Weapon_Sword_Iron")) and "MISSING" in str(Gp.smcText()),
            "X3 fix: no SkyySacks craft bridges = no Smithing tab -> the bench keeps the plain weapon (never uncraftable): %s" % Gp.smcText())
    K.check(Gp.benchWhy(None, "Weapon_Sword_Frost") is not None and bool(Gp.offBench("Weapon_Sword_Frost")), "X3 fix: ... a loot-only weapon stays refused without SkyySacks")
    for k_ in SKF[:3]:
        br.put(k_, Cv(None))
    K.check(Gp.benchWhy(None, "Weapon_Sword_Iron") is None, "X3 fix: three of the four craft bridges = still no Smithing tab, the bench crafts")
    br.put(SKF[3], Cv(None))
    w1 = Gp.benchWhy(None, "Weapon_Sword_Iron")
    K.check(w1 is not None and "Smithing tab" in str(w1) and "Weapons" in str(w1), "X3 bench: a plain weapon -> the Smithing tab: %s" % w1)
    w2 = Gp.benchWhy(None, "Armor_Leather_Light_Chest")
    K.check(w2 is not None and "Combat armor" in str(w2), "X3 bench: a plain armor piece -> Smithing Combat armor: %s" % w2)
    w3 = Gp.benchWhy(None, "Weapon_Sword_Frost")
    K.check(w3 is not None and "loot only" in str(w3), "X3 bench: a named weapon is loot only: %s" % w3)
    K.check(Gp.benchWhy(None, "Weapon_Wand_Skyy_Test_Named") is None, "X3 bench: a named weapon with no drop source keeps its recipe (never unobtainable)")
    K.check(not bool(Gp.combatId("Armor_Bronze_Ornate_Head")) and Gp.benchWhy(None, "Armor_Bronze_Ornate_Head") is None and not bool(Gp.inLoot("Armor_Bronze_Ornate_Chest")),
            "X3 fix: Ornate Bronze is no Smithing combat piece and not loot (Bronze armor = the Mining set only; its bench recipe stays)")
    for i in ("Armor_Mining_Lead_Chest", "Armor_Iron_Chest", "Tool_Pickaxe_Iron", "Ingredient_Bar_Iron", "Tool_Hatchet_Pickaxe_Multitool_Copper"):
        K.check(Gp.benchWhy(None, i) is None, "X3 bench: %s (gathering / tool / material) is not refused" % i)
    K.check(bool(Gp.offBench("Weapon_Sword_Iron")) and not bool(Gp.offBench("Armor_Mining_Lead_Chest")), "X3 offBench (/craft hides combat gear only)")
    K.check(bool(Sm.shown(0)) and bool(Sm.shown(2)) and bool(Sm.shown(1)) and not bool(Sm.shown(3)), "X3 Smithing shows Combat armor + Weapons with smith.combat")
    Cfg.SMITH_COMBAT = False
    K.check(Gp.benchWhy(None, "Weapon_Sword_Iron") is None and not bool(Gp.offBench("Weapon_Sword_Iron")) and not bool(Sm.shown(0)) and not bool(Sm.shown(2)) and bool(Sm.shown(1)),
            "X3 smith.combat off = 0.3.36: benches craft, the Smithing tab gathering only")
    Cfg.SMITH_COMBAT = True
    K.check(str(Gp.smcText()).startswith("Smithing combat on (") and "MISSING" not in str(Gp.smcText()), "X3 the ready-line part: %s" % Gp.smcText())
    # fix (2nd critic): part.smithing OFF (the Smithing page switched off) = no Smithing route -> the benches keep the plain pieces
    son = bool(Cfg.SMITH_ON)
    Cfg.SMITH_ON = False
    K.check(Gp.benchWhy(None, "Weapon_Sword_Iron") is None and not bool(Gp.offBench("Weapon_Sword_Iron")) and not bool(Gp.smithOn())
            and Gp.benchWhy(None, "Weapon_Sword_Frost") is not None and "part.smithing" in str(Gp.smcText()),
            "X3 fix: part.smithing=false -> the bench crafts the plain weapon, loot-only still refused: %s" % Gp.smcText())
    Cfg.SMITH_ON = son
    K.check(bool(Gp.smithOn()) and Gp.benchWhy(None, "Weapon_Sword_Iron") is not None, "X3 part.smithing back on -> the veto again")
    for k_ in SKF:
        br.remove(k_)
    # ---- X4 craft rarity
    UU = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000c0de1")
    n = 20000
    cnt = [0] * 8
    for _ in range(n):
        cnt[int(Rl.craftRarityMob(UU))] += 1
    om = [float(x) for x in Cfg.O_MOB]
    tot5 = sum(om[:5])
    exp = [om[k] / tot5 for k in range(5)]
    got = [cnt[k] / float(n) for k in range(5)]
    K.check(cnt[5] == cnt[6] == cnt[7] == 0 and all(abs(got[k] - exp[k]) < 0.015 for k in range(5)),
            "X4 craftRarityMob follows the mob odds %s (got %s), never Mythic / Set / Untiered %s" % (["%.3f" % x for x in exp], ["%.3f" % x for x in got], cnt[5:]))
    keep = list(Cfg.O_MOB)
    for hot, want in ((int(Df.R_MY), 4), (int(Df.R_UT), 4), (int(Df.R_SET), 0)):
        w = [0.0] * len(keep)
        w[hot] = 100.0
        Cfg.O_MOB = JArray(JDouble)(w)
        rs = set(int(Rl.craftRarityMob(UU)) for _ in range(300))
        K.check(rs == {want}, "X4 every mob weight on %s -> %s (got %s)" % (rid[hot], rid[want], sorted(rs)))
    Cfg.O_MOB = JArray(JDouble)([float(x) for x in keep])
    keepc = list(Cfg.O_CRAFT)
    for hot in (int(Df.R_MY), int(Df.R_UT)):
        w = [0.0] * len(keepc)
        w[hot] = 100.0
        Cfg.O_CRAFT = JArray(JDouble)(w)
        rs = set(int(Rl.craftRarity(UU, None)) for _ in range(300))
        K.check(not (rs & {int(Df.R_MY), int(Df.R_UT)}), "X4 the bench roll with every craft weight on %s never makes it (got %s)" % (rid[hot], sorted(rs)))
    Cfg.O_CRAFT = JArray(JDouble)([float(x) for x in keepc])
    K.check(int(Cfg.craftMax()) <= 4, "X4 craft.maxRarity is at most Fabled (%d)" % int(Cfg.craftMax()))
    # ---- X5 Sigils on crafted gear
    T36.fake_items(JClass, ["Weapon_Sword_Iron", "Skyy_Sigil_Mythic", "Skyy_Sigil_Fabled"])
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Sg = JClass(PKG + "GearSigil")
    Cfg.SIG_ON, Cfg.SIG_MY = True, True
    dc = Rl.newDoc("Weapon_Sword_Iron", 2, True, "craft", 12)
    dd = Rl.newDoc("Weapon_Sword_Iron", 2, True, "drop", 12)
    it = IS("Weapon_Sword_Iron", 1)
    K.eq(str(Sg.why(it, dc, int(Df.R_MY))), str(Sg.CRAFTMY), "X5 a Mythic Sigil on a crafted piece is refused (drop-only)")
    K.check(Sg.why(it, dd, int(Df.R_MY)) is None, "X5 a Mythic Sigil on a dropped piece works: %s" % Sg.why(it, dd, int(Df.R_MY)))
    K.check(Sg.why(it, dc, 4) is None, "X5 a Fabled Sigil on a crafted piece works: %s" % Sg.why(it, dc, 4))
    # ---- X6 elites
    Cfg.NOT_BOSS = "Skeleton_Elite*"
    for role, want in (("Skeleton_Elite", True), ("Skeleton_Elite_Phase_2", True), ("skeleton_elite", True), ("Goblin_Duke", False),
                       ("Goblin_Duke_Phase_2", False), ("Trork_Chieftain", False), ("Dragon_Fire", False), ("Elite_Skeleton", False), ("", False), (None, False)):
        K.check(bool(Gp.notBoss(role)) == want, "X6 notBoss(%r) = %s" % (role, want))
    Cfg.NOT_BOSS = "*_Elite*, Trork_*"
    K.check(bool(Gp.notBoss("Skeleton_Elite_Knight")) and bool(Gp.notBoss("Trork_Chieftain")) and not bool(Gp.notBoss("Goblin_Duke")), "X6 patterns: *_Elite*, Trork_*")
    Cfg.NOT_BOSS = ""
    K.check(not bool(Gp.notBoss("Skeleton_Elite")), "X6 an empty list: nobody")
    Cfg.NOT_BOSS = "Skeleton_Elite*"
    Lk = JClass(PKG + "GearLuck")
    pv = [float(x) for x in Cfg.UT_PV]
    K.check(float(Lk.points("default", "Skeleton_Elite", "boss")) == pv[0] and float(Lk.points("default", "Goblin_Duke", "boss")) == 0.0
            and float(Lk.points("default", "Skeleton_Elite", "elite")) == pv[0], "X6 a boss-ranked Skeleton_Elite = elite points %s; Goblin Duke outside a dungeon 0" % pv[0])
    # ---- X7 hp7Update on the 0.3.36 default file
    old = T36._old_default_text()
    po = _props(old)
    keys = [str(x) for x in Cfg.HP7_KEYS]
    K.check(len(keys) == 24 and all(po.get(k) == str(o) for k, o in zip(keys, Cfg.HP7_OLD)), "X7 the 0.3.36 default file holds every old cost row")
    r = Cfg.hp7Update(old)
    pn = _props(str(r[0]))
    want = dict(po)
    want.update(dict(zip(keys, [str(x) for x in Cfg.HP7_NEW])))
    want["cost.curve"] = "true"
    K.eq(sorted(k for k in set(pn) | set(want) if pn.get(k) != want.get(k)), [], "X7 hp7Update: the 24 cost rows move + cost.curve=true appended, nothing else")
    K.check(str(Cfg.HP7_MARK_ID) in str(r[0]) and len(r[2]) == 0 and len(r[3]) == 3 * 25, "X7 the marker + one change-log row each, no notes")
    K.check(Cfg.hp7Update(str(r[0])) is None, "X7 a second update = null (marker)")
    K.check(bool(Cfg.p7Same(JString(old).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r[3])), "X7 p7Same")
    lgs = [str(Cfg.hp7Log(k_, o_, n_)).split("\t")[4:7] for k_, o_, n_ in (("cost.reforge.rare", "1000,40", "420,0"), ("cost.curve", "(none)", "true"))]
    K.eq(lgs, [["cost.reforge[rare]", "1000|40", "420|0"], ["cost.curve", "(none)", "true"]], "X7 hp7Log: table rows as cost.reforge[rare]")
    rc = Cfg.hp7Update(old.replace("\n", "\r\n"))
    K.check(_props(str(rc[0])) == want and "\n" not in str(rc[0]).replace("\r\n", ""), "X7 CRLF kept")
    hand = old.replace("\ncost.reforge.rare=1000,40\n", "\ncost.reforge.rare=999,40\n")
    K.check(hand != old, "X7 the hand-edit test line exists")
    rh = Cfg.hp7Update(hand)
    ph = _props(str(rh[0]))
    K.check(ph["cost.reforge.rare"] == "999,40" and ph["cost.curve"] == "false" and len(rh[2]) == 3,
            "X7 a hand-set cost row kept + noted, cost.curve=false appended: %s" % [str(x)[:90] for x in rh[2]])
    # fix (critic): with one admin row EVERY other cost row keeps its 0.3.36 value (curve off + "<base>,0" would be a flat Lv 10 price)
    want_h = dict(_props(hand))
    want_h["cost.curve"] = "false"
    K.eq(sorted(k for k in set(ph) | set(want_h) if ph.get(k) != want_h.get(k)), [],
         "X7 one hand-set row: none of the 24 cost rows moves, only cost.curve=false is appended")
    K.check(any("23 other cost rows kept" in str(x) for x in rh[2]) and len(rh[3]) == 3, "X7 one hand-set row: the 23-kept note + one change-log row (cost.curve)")
    rd = Cfg.hp7Update(old.replace("\ncost.reforge.rare=1000,40\n", "\ncost.reforge.rare=1000,\\\n    40\n"))
    K.check(_props(str(rd[0])).get("cost.curve") == "false" and _props(str(rd[0])).get("cost.levelUp.rare") == po.get("cost.levelUp.rare"),
            "X7 a default row this update cannot rewrite (a continued line) = the whole cost set kept, cost.curve=false")
    # fix 2 (2nd critic): an admin row + an ABSENT cost row -> the absent row is written at its 0.3.36 value (never a flat "<Lv 10 base>,0")
    kz = keys[-1]
    ha = hand.replace("\n" + kz + "=", "\n#gone." + kz + "=")
    K.check(ha != hand and _props(ha).get(kz) is None, "X7 the absent-row test file")
    ra = Cfg.hp7Update(ha)
    pa = _props(str(ra[0]))
    K.check(pa.get(kz) == str(Cfg.HP7_OLD[len(keys) - 1]) and pa.get("cost.curve") == "false" and pa.get("cost.reforge.rare") == "999,40"
            and any("had no line" in str(x) for x in ra[2]) and len(ra[3]) == 6,
            "X7 fix: kept + an absent cost row (%s) = the row added at its 0.3.36 value %s, cost.curve=false, two change-log rows" % (kz, pa.get(kz)))
    ra0 = Cfg.hp7Update(old.replace("\n" + kz + "=", "\n#gone." + kz + "="))
    K.check(_props(str(ra0[0])).get(kz) is None and _props(str(ra0[0])).get("cost.curve") == "true",
            "X7 no admin row + an absent row = the in-code P7 default, curve on (no line added)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    P = JClass("java.nio.file.Paths")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = P.get(fc)
    lgp = os.path.join(home, "config-changes.log")
    oc = open(fc, "rb").read()
    msgs = [str(getattr(Cfg, m)()) for m in ("migrate0330", "migrateP4", "migrateP5", "migrateP6")]
    mid = open(fc, "rb").read()
    log0 = open(lgp, "rb").read() if os.path.isfile(lgp) else b""
    msg = str(Cfg.migrateP7())
    nc = open(fc, "rb").read()
    K.check("0.3.37" in msg, "D start 1: %s" % msg[:300].replace("\n", " | "))
    pm, pn = _props(mid.decode("latin-1")), _props(nc.decode("latin-1"))
    changed = sorted(k for k in set(pm) | set(pn) if pm.get(k) != pn.get(k))
    allowed = set(str(x) for x in Cfg.HP7_KEYS) | set(str(x) for x in Cfg.HP7_ADDK)
    K.check(changed and set(changed) <= allowed, "D migrateP7 changes only planned keys: %d (%s)" % (len(changed), [k for k in changed if k not in allowed][:5]))
    K.notes.append("D live rows moved by migrateP7: %s; cost.curve=%s; notes: %s" % (len(changed), pn.get("cost.curve"), msg[:400]))
    K.notes.append("D the older migrations on the live copy first: %s" % [m_[:120] for m_ in msgs if m_])
    K.check(str(Cfg.HP7_MARK_ID).encode() in nc, "D the marker is in the live file")
    found = any(open(os.path.join(r_, f_), "rb").read() == mid for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs)
    K.check(found, "D the config-history copy holds the bytes before migrateP7")
    lg = open(lgp, "rb").read()[len(log0):].decode("utf-8")
    K.eq(lg.count("\tSkyyGear 0.3.37\t-\tupdate\t"), len(changed), "D one change-log line per changed row")
    K.check((b"\r\n" in oc) == (b"\r\n" in nc), "D line endings kept")
    s1 = open(fc, "rb").read()
    msg2 = "".join(str(getattr(Cfg, m)()) for m in ("migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7"))
    K.check(msg2 == "" and open(fc, "rb").read() == s1, "D start 2: nothing changes (%r)" % msg2[:120])
    Cfg.load()
    ri = [str(x) for x in JClass(PKG + "GearDefs").R_ID].index("rare")
    if pn.get("cost.reforge.rare") == "420,0" and pn.get("cost.curve") == "true":
        K.eq(int(Cfg.costReforge(ri, 50)), 15500, "D the live file loads: Rare reforge Lv 50 = 15,500")
    K.check(bool(Cfg.SMITH_COMBAT) and str(Cfg.NOT_BOSS) == "Skeleton_Elite*", "D the live file loads: smith.combat on, loot.notBosses Skeleton_Elite*")
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
