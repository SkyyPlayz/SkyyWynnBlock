"""Harness for SkyyAccessories 0.5.30 (tools/accessories_0_5_30_patch.py = Balance P5: six rarities per line, Health in % of max Health, the Power
numbers, gathering Fortune that grows with the skill, the Fabled / Mythic upgrades, the one-time migrateP5). Build first:
    python tools/accessories_0_5_30_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.30.py
    python SkyyAccessories/test_skyyaccessories_0.5.30.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, no new command / system
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.29 -> 0.5.30: only the planned members differ (EXPECT); assets: the 20 new items + the lang + manifest
  DEFS  AccDefs: BOOST (stride 7) = the P5 ladder; LINE_IDS 60 = six per line; tierOf / rarityOf of Fabled / Mythic = 5 / 6 (a bench IV, the
        Lantern Legendary and Eternal Flame stay 4); statParts at Mythic; bestTiers / activeTiers with a Mythic in the bag; the gear:extra text
        (textOf2) of a Mythic Brawler + Razorfang = the P5 numbers; idOf / rarityIndex 1..6; the loader: a hand-edited 4-number line still loads
        (Fabled / Mythic repeat its Legendary), a 6-number line reads as written; checkBoost wants six numbers
  POW   AccPower: the pw.<Power>.hp numbers (% per 100 AP); tick() of a Mythic Health + Balance bag: c[0] = the Power's Health % (+ Plates at
        rank 3 x 5 = +7.5); gathering Fortune = pw.Mining.dd x M x (1 + Mining level / 10) through tick's skill:bonus source (fake
        skill:fn:level); power.gatherLevel 0 = no growth; the model check: Balance best / plain = x1.25 +- 0.05 (DPS and EHP, the jar's own
        numbers through tools/balance_model.py's formulas); gathering Fortune vs the 1.1 budget +- 15 %% at Lv 17 / 95
  PCT   AccEffects.hpPct on a REAL EntityStatMap: +8 %% of the max without it, not compounding, a lower pct at once, a base shrink waits 3 s, a
        negative pct never takes the max below 1, 0 removes it
  ITEM  the jar's 20 new items: quality Skyy_Acc_Fabled / Mythic, the recipe (the rarity below + 4 Ench Cobalt + the Legendary materials x2 /
        4 Ench Adamantite + 2 Ench Mithril) in the bag's Craft tab, names + tooltips in the lang file (the Legendary names its Fabled step)
  MIG   mp5Update (pure text) on config.properties + power.properties shapes: the 0.5.29 defaults move (CRLF kept), boost.Health.flat at its
        default becomes a comment (hand-set = kept, unused, noted), a hand-edited boost line kept + noted, a marked file untouched; mp5Same
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyAccessories (every update in setup's order + both loaders): only the planned keys
        change in each file (Properties), History copies, change-log lines; the second start changes nothing
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, subprocess, hashlib, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp5", "acc")]
import harness_kit as HK
import skyybuild as B
import balance_model as BM
import skyyonce_harness as OH

VERSION, OLD = "0.5.30", "0.5.29"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_30_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.accessories."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
NEW_IDS = ["Skyy_Talisman_%s_%s" % (f, w) for f in ("Vitality", "Endurance", "Intelligence", "Regeneration", "Speed") for w in ("Fabled", "Mythic")] + \
          ["Skyy_Talisman_%s_T%d" % (f, t) for f in ("Strength", "MagicPower", "Defense", "Crit", "Feather") for t in (5, 6)]
HK.run_compare = OH.compare_allowing(lambda n: n == "Server/Languages/en-US/server.lang" or any(n == "Server/Item/Items/Utility/%s.json" % i for i in NEW_IDS)
                                     or n.startswith("Server/Item/Items/Utility/Skyy_Talisman_"))
EXPECT = {   # checked by hand 2026-10-21: the version / default texts (CfgFn, CfgRows, CfgFile, writeDefaults), the six-rarity tables (AccDefs),
             # the loader + check (AccCfg), the % Health (AccEffects), the stride (AccGear, AccPage), the gather growth (AccPower), Plates hpp (AccV3)
    "AccAdmin": ["~m giveCmd"],
    "AccCfg": ["+f MP5P_MARK", "+f MP5_ACT", "+f MP5_HCOM", "+f MP5_KEY", "+f MP5_MARK", "+f MP5_MARK_ID", "+f MP5_NC", "+f MP5_NEW", "+f MP5_OLD",
               "+f MP5_WHO", "+m migrateP5", "+m mp5File", "+m mp5Is", "+m mp5Lk", "+m mp5Same", "+m mp5Saved", "+m mp5Update", "~<clinit>", "~m boostIn",
               "~m checkBoost", "~m load", "~m writeDefaults"],
    "AccDefs": ["~<clinit>", "~m bestTiers", "~m defsText", "~m hasFall", "~m idOf", "~m linesText", "~m rarityIndex", "~m rarityOf", "~m sendsGear",
                "~m statParts"],
    "AccEffects": ["+f HP_LOW", "+f HP_LOW_MS", "+f HP_PCT", "+m flatMax", "+m flatOf", "+m hpPct", "+m pctKey", "+m pctWant", "~<clinit>", "~m manaMod", "~m manaMod2", "~m tick"],
    "AccGear": ["~m textOf", "~m textOf2"], "AccPage": ["~m effects"],
    "AccPower": ["+f GLEVEL", "+f GLV", "+m gatherMult", "+m skillLevel", "~<clinit>", "~m load", "~m tick"],
    "AccV3": ["~<clinit>", "~m hp", "~m loadV3", "~m v3most", "~m v3per"],
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyAccessoriesPlugin": ["~m setup"]}
P5_BOOST = ["2,3.2,4.4,5.6,6.8,8", "3,4.8,6.6,8.4,10.2,12", "2.5,4,5.5,7,8.5,10", "6,9.6,13.2,16.8,20.4,24", "1,1.6,2.2,2.8,3.4,4",
            "0.25,0.4,0.55,0.7,0.85,1", "2.5,4,5.5,7,8.5,10", "3,5,7,8,10,12", "3,5,7,8,10,12", "3,5,7,8,10,12", "2,3,4,6,7,8",
            "4,6,9,11,14,16", "10,16,22,28,34,40", "5,8,11,14,17,20"]


def _props(b):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.ByteArrayInputStream")(b))
    return {str(k): str(p.getProperty(k)) for k in p.stringPropertyNames()}


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def fake_stats(JClass, names=("Health", "Oxygen", "Stamina", "Mana", "SignatureEnergy", "Ammo")):
    """a bare JVM has no EntityStatType asset store: one with the six default stats (min / max 0; the test's MAX modifiers give the max)"""
    from jpype import JInt, JArray, JImplements, JOverride, JObject, JString
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestStatStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestStatStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    FKC = fk.toClass(AS.class_)

    def fld(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    C = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    @JImplements("java.util.function.IntFunction")
    class Arr(object):
        @JOverride
        def apply(self, n):
            return JArray(C)(int(n))
    m = ILT(Arr())
    arr = JArray(C)(len(names))
    kti = fld(ILT, "keyToIndex").get(m)
    for i, n in enumerate(names):
        o = US.allocateInstance(C.class_)
        fld(C, "id").set(o, JString(n))
        arr[i] = o
        kti.put(JObject(JString(n), JClass("java.lang.Object")), JInt(i))
    fld(ILT, "array").set(m, arr)
    nf = fld(ILT, "nextIndex")
    if "AtomicInteger" in str(nf.getType()):
        nf.set(m, JClass("java.util.concurrent.atomic.AtomicInteger")(len(names)))
    else:
        nf.setInt(m, JInt(len(names)))
    st = US.allocateInstance(FKC)
    fld(AS, "tClass").set(st, C.class_)
    fld(AS, "assetMap").set(st, m)
    fld(JClass("com.hypixel.hytale.assetstore.AssetRegistry"), "storeMap").get(None).put(C.class_, st)
    fld(C, "ASSET_STORE").set(None, st)
    JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes").update()


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.30 - build script') and g.count('VERSION = "0.5.30"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    su = g[g.index("public void setup() {"):]
    K.check(su.index("migrate0518();") < su.index("migrateP5(@PKG@.AccCfg.FILE, false)") < su.index("AccCfg.load(true)")
            < su.index("migrateP5(@PKG@.AccPower.FILE, true)") < su.index("AccPower.load()"), "S setup: 0518 -> P5 config -> load -> P5 power -> power load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_defs(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    D, Cfg, Gear = JClass(PKG + "AccDefs"), JClass(PKG + "AccCfg"), JClass(PKG + "AccGear")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    ek = [str(x) for x in D.E_KEYS]
    bo = [float(x) for x in D.BOOST]
    got = [",".join("%g" % round(bo[e * 7 + t], 4) for t in range(1, 7)) for e in range(len(ek))]
    K.eq(got, P5_BOOST, "DEFS BOOST stride 7 = the P5 ladder (Normal x 1 / 1.6 / 2.2 / 2.8 / 3.4 / 4; whole-point lines rounded)")
    K.check(ek[0] == "Health.pct" and all(bo[e * 7] == 0.0 for e in range(len(ek))), "DEFS the Health entry is Health.pct; tier 0 = 0")
    ids = [str(x) for x in D.LINE_IDS]
    K.check(len(ids) == 60 and all(i in ids for i in NEW_IDS) and ids[5] == "Skyy_Talisman_Vitality_Mythic" and ids[4] == "Skyy_Talisman_Vitality_Fabled",
            "DEFS LINE_IDS = 60, six per line (Vitality Fabled / Mythic at 4 / 5)")
    K.check(all(int(D.tierOf(i)) == (5 if i.endswith(("_Fabled", "_T5")) else 6) and int(D.rarityOf(i)) == int(D.tierOf(i)) for i in NEW_IDS),
            "DEFS tierOf / rarityOf of the 20 new ids = 5 / 6")
    K.eq([int(D.rarityOf(x)) for x in ("Skyy_Accessory_Workbench_T7", "Skyy_Talisman_Lantern_Epic", "Skyy_Charm_Furnace_Eternal", "Skyy_Talisman_Vitality_Epic")],
         [4, 4, 4, 4], "DEFS a bench VII, the Lantern Legendary, Eternal Flame and a Legendary charm stay rarity 4")
    K.eq([str(D.DISPLAY[int(D.rarityOf(i))]) for i in ("Skyy_Talisman_Crit_T5", "Skyy_Talisman_Speed_Mythic")], ["Fabled", "Mythic"], "DEFS names")
    li_h, li_c = int(D.lineOf("Health")), int(D.lineOf("Crit"))
    K.eq([str(x) for x in D.statParts(li_h, 6)], ["+8% max Health"], "DEFS statParts Health Mythic")
    K.eq([str(x) for x in D.statParts(li_c, 5)], ["+7% Crit Chance, +14% Crit Damage"], "DEFS statParts Razorfang Fabled")
    K.check(len(D.statParts(li_h, 7)) == 0, "DEFS statParts above 6 = nothing")
    best = [int(x) for x in D.bestTiers(S("Skyy_Talisman_Vitality_Mythic", "Skyy_Talisman_Vitality_Epic", "Skyy_Talisman_Strength_T6", "Skyy_Talisman_Crit_T6"))]
    K.check(best[li_h] == 6 and best[int(D.lineOf("Strength"))] == 6, "DEFS bestTiers: a Mythic beats the Legendary of its line: %s" % best)
    K.eq(str(Gear.textOf2(JArray(JClass("int"))(best), None)), "cc:8,cd:16,str:12", "DEFS gear:extra of a Mythic Brawler + Razorfang = cc 8, cd 16, str 12")
    K.eq((str(D.idOf(li_h, 6)), D.idOf(li_h, 7), int(D.rarityIndex("Mythic")), int(D.rarityIndex("6")), int(D.rarityIndex("7"))),
         ("Skyy_Talisman_Vitality_Mythic", None, 6, 6, -1), "DEFS idOf / rarityIndex 1..6")
    K.check(bool(D.isBoosterId("Skyy_Talisman_Feather_T6")) and "Skyy_Talisman_Vitality_Mythic" in str(D.defsText()), "DEFS isBoosterId + acc:defs list the new ids")
    # the loader: 6 numbers read as written; a hand-edited 4-number line loads with Fabled / Mythic = its Legendary
    e_s = ek.index("Strength.flat")
    r6 = [float(x) for x in Cfg.boostIn("1,2,3,4,5,6", e_s)]
    r4 = [float(x) for x in Cfg.boostIn("2,4,6,9", e_s)]
    rb = [float(x) for x in Cfg.boostIn("nonsense", e_s)]
    K.eq((r6, r4, rb), ([1, 2, 3, 4, 5, 6], [2, 4, 6, 9, 9, 9], [3, 5, 7, 8, 10, 12]), "DEFS boostIn: 6 numbers / a 4-number hand edit (pads) / junk = built-in")
    K.check(Cfg.checkBoost("boost[Strength.flat]", "1,2,3,4,5,6") is None and "6 numbers" in str(Cfg.checkBoost("boost[Strength.flat]", "1,2,3,4")),
            "DEFS checkBoost wants six numbers")
    K.save()


def run_pow(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pw, V3, D = JClass(PKG + "AccPower"), JClass(PKG + "AccV3"), JClass(PKG + "AccDefs")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    home = os.path.join(scratch, "pow")
    os.makedirs(os.path.join(home, "power"), exist_ok=True)
    Pw.FILE = Paths.get(os.path.join(home, "power.properties"))
    Pw.DIR = Paths.get(os.path.join(home, "power"))
    Pw.load()
    t0 = open(os.path.join(home, "power.properties"), encoding="latin-1").read()
    K.check("pw.Balance.hp=2.5" in t0 and "pw.Tank.hp=6" in t0 and "pw.Mining.dd.mining=10.5" in t0 and "pw.Farming.dd.farming=15.75" in t0
            and "power.gatherLevel=10" in t0 and "Balance P5 power (SkyyAccessories 0.5.30)" not in t0, "POW the fresh power.properties: the P5 numbers")
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    LV = {"Mining": 17, "Combat": 30}
    RANK = {}

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return JObject(LV.get(str(a[1]), 0), "java.lang.Integer")

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            return JObject(RANK.get(str(a[1]), 0), "java.lang.Integer")
    br.put("skill:fn:level", Lv())
    br.put("tree:fn:level", Tr())
    u = UUID.fromString("00000000-0000-0000-0000-00000000b530")
    k = str(u)
    Pw.pick(u, k, "Balance", 1000000, False)
    bag = S("Skyy_Talisman_Vitality_Mythic", "Skyy_Talisman_Speed_Common")
    ap = int(Pw.apOf(bag))
    m = float(Pw.mult(ap))
    c = [float(x) for x in Pw.tick(u, bag)]
    K.check(ap == 35 and abs(c[0] - round(2.5 * m * 10) / 10.0) < 1e-9, "POW Balance at AP %d (M %.3f): c[0] = the Power's Health %% %.1f (2.5 per 100 AP)" % (ap, m, c[0]))
    import trees_v3_effects as V3E
    kp = V3E.key("Combat", 2, "r4a")
    RANK[kp] = 3
    big = S(*["Skyy_Talisman_%s_Common" % f for f in ("Vitality", "Speed", "Endurance", "Intelligence", "Regeneration", "Strength")])
    cb = [float(x) for x in Pw.tick(u, big)]
    RANK[kp] = 0
    cb0 = [float(x) for x in Pw.tick(u, big)]
    K.check(abs(cb[0] - cb0[0] - 7.5) < 1e-6, "POW Combat Accessory Plates rank 3 x 5 accessories = +7.5 %% max Health on c[0] (%.2f -> %.2f)" % (cb0[0], cb[0]))
    # gathering: the Mining Power, Mining 17 -> x2.7
    Pw.pick(u, k, "Mining", 2000000, False)
    gb = S("Skyy_Talisman_Vitality_Rare", "Skyy_Talisman_Speed_Rare", "Skyy_Talisman_Endurance_Rare")
    gap = int(Pw.apOf(gb))
    gm = float(Pw.mult(gap))
    Pw.tick(u, gb)
    src = br.get("skill:bonus:" + k).get("accessories")
    dd = float(src.get("dd.mining"))
    want = round(10.5 * gm) / 100.0 * (1 + 17 / 10.0)
    K.check(abs(dd - want) < 1e-9, "POW Mining Power at AP %d, Mining 17: dd.mining %.4f = round(10.5 x %.3f) / 100 x 2.7 (skill:bonus 'accessories')" % (gap, dd, gm))
    Pw.GLEVEL = 0
    Pw.GLV.clear()
    Pw.tick(u, gb)
    dd0 = float(br.get("skill:bonus:" + k).get("accessories").get("dd.mining"))
    K.check(abs(dd0 - round(10.5 * gm) / 100.0) < 1e-9, "POW power.gatherLevel 0 = no growth (%.4f)" % dd0)
    Pw.GLEVEL = 10
    LV["Mining"] = 0
    Pw.GLV.clear()
    Pw.tick(u, gb)
    K.check(abs(float(br.get("skill:bonus:" + k).get("accessories").get("dd.mining")) - round(10.5 * gm) / 100.0) < 1e-9, "POW Mining 0 / unknown = x1")
    # the model check on the jar's own numbers: plain = Normal lines + Balance at AP 100, best = Mythic lines + Balance at AP 393
    ek = [str(x) for x in D.E_KEYS]
    bo = [float(x) for x in D.BOOST]
    ev = dict((str(Pw.E_KEY[e]), float(Pw.E_VAL[e])) for e in range(len(Pw.E_PW)) if str(Pw.PW_ID[int(Pw.E_PW[e])]) == "Balance")

    def kit(t, ap_):
        mm = float(Pw.mult(ap_))
        g = lambda key: bo[ek.index(key) * 7 + t]
        tt = {"hpp": g("Health.pct") + ev["hp"] * mm, "str": g("Strength.flat") + ev["str"] * mm, "def": g("Defense.flat") + ev["def"] * mm,
              "cc": g("Crit.chancePct") + ev["cc"] * mm, "cd": g("Crit.damagePct") + ev["cd"] * mm}
        return BM.p5_dps(tt), BM.p5_ehp(tt)
    pd, pe = kit(1, 100)
    bd, be = kit(6, 393)
    K.check(abs(bd / pd - 1.25) <= 0.05 and abs(be / pe - 1.25) <= 0.05, "POW model: Balance best / plain = DPS x%.3f, EHP x%.3f (target 1.25 +- 0.05)" % (bd / pd, be / pe))
    rows = []
    for nm in ("Tank", "Slayer", "Lucky", "Fortress", "Harmony", "GlassCannon", "Jackpot"):
        ev2 = dict((str(Pw.E_KEY[e]), float(Pw.E_VAL[e])) for e in range(len(Pw.E_PW)) if str(Pw.PW_ID[int(Pw.E_PW[e])]) == nm)
        mm = float(Pw.mult(393))
        tt = {"hpp": ev2.get("hp", 0) * mm, "str": ev2.get("str", 0) * mm, "def": ev2.get("def", 0) * mm, "cc": ev2.get("cc", 0) * mm, "cd": ev2.get("cd", 0) * mm}
        rows.append("%s DPS x%.2f EHP x%.2f" % (nm, BM.p5_dps(tt), BM.p5_ehp(tt)))
    K.notes.append("POW Powers alone at AP 393: " + "; ".join(rows))
    f17 = BM.p5_gather_fortune("mining", 210, 17)
    f95 = BM.p5_gather_fortune("mining", 490, 95)
    K.check(abs(f17 - 51) <= 0.15 * 51 + 1e-9 and abs(f95 - 257) <= 0.15 * 257, "POW fix: gathering Fortune vs the 1.1 budget +-15 %% (spec 7.4): end of Zone 1 %.0f (51), end of Zone 5 %.0f (257) - dd fitted 10.5" % (f17, f95))
    K.check(abs(float(dict((str(Pw.PW_ID[int(Pw.E_PW[e])]) + "." + str(Pw.E_KEY[e]), float(Pw.E_VAL[e])) for e in range(len(Pw.E_PW)))["Mining.dd.mining"]) - BM.P5_GATHER_DD["mining"]) < 1e-9,
            "POW fix: the jar's pw.Mining.dd.mining = tools/balance_model.py P5_GATHER_DD (10.5)")
    K.save()


def run_pct(out, jar, scratch, _home):
    from jpype import JClass, JInt, JFloat, JDouble, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    fake_stats(JClass)
    E = JClass(PKG + "AccEffects")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    HPI = int(DST.getHealth())
    m = ESM()
    m.update()
    m.putModifier(JInt(HPI), "acc530test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(150.0)))
    amt = lambda: (lambda c: None if c is None else float(c.getAmount()))(m.getModifier(JInt(HPI), "skyyacc_health"))
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(8.0), JLong(1000))
    a1 = amt()
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(8.0), JLong(2000))
    K.check(abs(a1 - 12.0) < 0.02 and abs(amt() - a1) < 1e-6 and abs(float(m.get(JInt(HPI)).getMax()) - 162.0) < 0.05,
            "PCT +8 %% of the max without it (12 of 150), no compounding the next second, max 162 (%.2f)" % a1)
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(4.0), JLong(3000))
    K.check(abs(amt() - 6.0) < 0.02, "PCT a lower pct (8 -> 4) at once: %.2f" % amt())
    m.putModifier(JInt(HPI), "acc530test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(100.0)))
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(4.0), JLong(10000))
    w1 = amt()
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(4.0), JLong(12000))
    w2 = amt()
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(4.0), JLong(13500))
    K.check(abs(w1 - 6.0) < 0.02 and abs(w2 - 6.0) < 0.02 and abs(amt() - 4.0) < 0.02, "PCT the base shrinking (150 -> 100) waits 3 s, then lowers: %.2f %.2f %.2f" % (w1, w2, amt()))
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(-200.0), JLong(20000))
    K.check(abs(float(m.get(JInt(HPI)).getMax()) - 1.0) < 0.05, "PCT a -200 %% debuff never takes the max below 1 (%.2f)" % float(m.get(JInt(HPI)).getMax()))
    E.hpPct(m, JInt(HPI), "skyyacc_health", JDouble(0.0), JLong(21000))
    K.check(amt() is None, "PCT 0 removes the modifier")
    # fix round (critic: Health % compounding): % of the FLAT max = type max + flat additive modifiers; SkyyGear / SkyyPets / SkyySkills % layers ignored
    ET = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    hf = ET.class_.getDeclaredField("max")
    hf.setAccessible(True)
    hf.setFloat(ET.getAssetMap().getAsset(JInt(HPI)), JFloat(100.0))
    m2 = ESM()
    m2.update()
    for k_, v_ in (("Armor", 50.0), ("skyygear_hp", 40.0), ("skyypet_health", 20.0), ("skyyskill_classhp", 10.0), ("skyyskill_rebirthhp", 5.0)):
        m2.putModifier(JInt(HPI), k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    K.eq(round(float(E.flatMax(m2.get(JInt(HPI)), JInt(HPI))), 2), 150.0, "PCT fix: flatMax = type max 100 + Armor 50 (Gear / Pets / Skills %% layers skipped)")
    for t_ in range(5):
        E.hpPct(m2, JInt(HPI), "skyyacc_health", JDouble(20.0), JLong(30000 + 1000 * t_))
    a2 = float(m2.getModifier(JInt(HPI), "skyyacc_health").getAmount())
    K.check(abs(a2 - 30.0) < 0.02, "PCT fix: 20 %% = 30 of the 150 flat max, steady with SkyyGear / SkyyPets / SkyySkills %% on top (%.2f; the old rule gave %.2f)" % (a2, 0.2 * (float(m2.get(JInt(HPI)).getMax()) - a2)))
    hf.setFloat(ET.getAssetMap().getAsset(JInt(HPI)), JFloat(0.0))
    # fix round 2 (critic): the Mana % reads the FLAT max too - SkyyPets' skyypet_mana + SkyySkills' rebirth Mana % do not feed it
    MPI = int(DST.getMana())
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MPI)), JFloat(100.0))
    m3 = ESM()
    m3.update()
    for k_, v_ in (("skyyskill_classmana", 50.0), ("skyypet_mana", 31.5), ("skyyskill_rebirthmana", 15.0)):
        m3.putModifier(JInt(MPI), k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    ma = []
    for t_ in range(3):
        E.manaMod(m3, JInt(MPI), "skyyacc_mana", JFloat(10.0), JFloat(0.0))
        ma.append(round(float(m3.getModifier(JInt(MPI), "skyyacc_mana").getAmount()), 2))
    for t_ in range(3):
        E.manaMod2(m3, JInt(MPI), "skyyacc_mana", JFloat(10.0), JFloat(0.0), JFloat(2.0))
        ma.append(round(float(m3.getModifier(JInt(MPI), "skyyacc_mana").getAmount()), 2))
    K.eq(ma, [15.0, 15.0, 15.0, 17.0, 17.0, 17.0], "PCT fix 2: Mana 10 %% = 15 of the 150 flat max (type 100 + class 50; pet / rebirth Mana %% skipped), steady; + a Power's flat 2 = 17")
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MPI)), JFloat(0.0))
    K.save()


def run_item(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    lmap = dict(l.split("=", 1) for l in lang.split("\n") if "=" in l)
    bad = []
    for i in NEW_IDS:
        p = "Server/Item/Items/Utility/%s.json" % i
        if p not in names:
            bad.append((i, "missing"))
            continue
        n = json.loads(z.read(p))
        fab = i.endswith(("_Fabled", "_T5"))
        q = "Skyy_Acc_Fabled" if fab else "Skyy_Acc_Mythic"
        ins = [(x.get("ItemId") or x.get("ResourceTypeId"), x["Quantity"]) for x in n["Recipe"]["Input"]]
        bench = n["Recipe"]["BenchRequirement"][0]["Id"]
        prev = i.replace("_Fabled", "_Epic").replace("_T5", "_T4") if fab else i.replace("_Mythic", "_Fabled").replace("_T6", "_T5")
        ok = n["Quality"] == q and ins[0] == (prev, 1) and bench == "SkyyAccessoryBag" and (
            ("Skyy_Ench_Cobalt", 4) in ins and len(ins) >= 3 if fab else ins[1:] == [("Skyy_Ench_Adamantite", 4), ("Skyy_Ench_Mithril", 2)])
        nm = lmap.get("items.%s.name" % i, "")
        ok = ok and nm.startswith("Fabled " if fab else "Mythic ") and nm.endswith(" Accessory") and ("items.%s.description" % i) in lmap
        if not ok:
            bad.append((i, n["Quality"], ins, nm))
    K.check(not bad, "ITEM the 20 Fabled / Mythic items: quality, recipe (the rarity below + Ench metals), bag Craft tab, names: %s" % bad[:3])
    leg = json.loads(z.read("Server/Item/Items/Utility/Skyy_Talisman_Vitality_Fabled.json"))
    K.check(("Ingredient_Bar_Thorium", 20) in [(x.get("ItemId"), x["Quantity"]) for x in leg["Recipe"]["Input"]], "ITEM Fabled Health: the Legendary materials x2 (Thorium 20)")
    d4 = lmap["items.Skyy_Talisman_Vitality_Epic.description"]
    d6 = lmap["items.Skyy_Talisman_Vitality_Mythic.description"]
    d34 = lmap["items.Skyy_Talisman_Crit_T4.description"]
    K.check(d4.startswith('<color is="#7ee08a">+5.6% max Health</color>') and d6.startswith('<color is="#7ee08a">') and d34.startswith('<color is="#7ee08a">')
            and not any('<color is="#ffffff">' in v_ for k_, v_ in lmap.items() if k_.startswith(("items.Skyy_Talisman_", "items.Skyy_Accessory_Lantern"))),
            "ITEM fix 2: every Void Charm stat value is green #7ee08a (Style Guide 15), none white")
    K.check("Next: Fabled Health Accessory" in d4 and "+5.6% max Health" in d4 and "Mythic is the top rarity" in d6 and "+8% max Health" in d6
            and "Next: Fabled Razorfang Accessory (upgrade it in the Craft tab" in d34, "ITEM tooltips: Legendary -> Fabled, Mythic is the top, Health in %%")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Cfg = JClass(PKG + "AccCfg")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    MK, MKP = str(Cfg.MP5_MARK), str(Cfg.MP5P_MARK)

    def upd(t, pc):
        r = Cfg.mp5Update(JString(t), pc)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]], [str(x) for x in r[4]])
    old = ["6,12,18,24", "3,6,9,12", "2.5,5,7.5,10", "6,12,18,24", "1,2,3,4", "0.25,0.5,0.75,1", "2.5,5,7.5,10", "3,6,9,12", "3,6,9,12", "3,6,9,12",
           "2,4,6,8", "4,8,12,16", "10,20,30,40", "5,10,15,20"]
    keys = ["Health.flat", "Stamina.flat", "Stamina.regenPct", "Mana.pct", "Mana.floor", "Regeneration.pct", "Speed.pct", "Strength.flat",
            "MagicPower.flat", "Defense.flat", "Crit.chancePct", "Crit.damagePct", "Feather.fallPct", "Feather.jumpPct"]
    src = "slots=18\n# Booster numbers\n" + "".join("boost.%s=%s\n" % (k, v) for k, v in zip(keys, old)) + "x=1\n"
    r = upd(src, False)
    pn = dict(l.split("=", 1) for l in r[0].split("\n") if "=" in l and not l.startswith("#"))
    K.check(r[0].count(MK) == 1 and r[0].index(MK) < r[0].index("boost.") and "boost.Health.flat" not in pn and len(r[3]) == 3 * 14 and r[4] == ["boost.Health.flat"]
            and [pn["boost." + k] for k in keys[1:]] == P5_BOOST[1:] and "# boost.Health.flat 6,12,18,24 was the 0.5.29 flat Health line" in r[0],
            "MIG config: the 13 boost lines move to six numbers, Health.flat at its default becomes a comment, the marker above")
    K.check(bool(Cfg.mp5Same(JString(src).getBytes("ISO-8859-1"), JString(r[0]).getBytes("ISO-8859-1"), r[3], r[4])), "MIG config: mp5Same passes")
    rc = upd(src.replace("\n", "\r\n"), False)
    K.check(rc[0] == r[0].replace("\n", "\r\n"), "MIG config: CRLF kept")
    rh = upd(src.replace("boost.Health.flat=6,12,18,24", "boost.Health.flat=30,40,50,60").replace("boost.Strength.flat=3,6,9,12", "boost.Strength.flat=4,8,12,16"), False)
    K.check("boost.Health.flat=30,40,50,60" in rh[0] and "boost.Strength.flat=4,8,12,16" in rh[0] and len(rh[2]) == 2 and "UNUSED" in rh[2][0] + rh[2][1],
            "MIG config: a hand-set Health.flat kept + noted UNUSED, a hand-edited Strength kept + noted: %s" % rh[2])
    K.check(upd("a=1\n" + MK + "\nboost.Strength.flat=3,6,9,12\n", False) is None, "MIG config: a marked file is left alone")
    psrc = "power.enabled=true\npw.Tank.hp=12\npw.Balance.hp=5\npw.Mining.dd.mining=6\npw.Farming.dd.farming=9\npw.Fishing.dd.fishing=2\npw.Tank.def=6\n"
    rp = upd(psrc, True)
    pp = dict(l.split("=", 1) for l in rp[0].split("\n") if "=" in l and not l.startswith("#"))
    K.check((pp["pw.Tank.hp"], pp["pw.Balance.hp"], pp["pw.Mining.dd.mining"], pp["pw.Farming.dd.farming"], pp["pw.Fishing.dd.fishing"], pp["pw.Tank.def"])
            == ("6", "2.5", "10.5", "15.75", "3.5", "6") and rp[0].count(MKP) == 1, "MIG power: hp halved (%), the gathering dd rows, nothing else")
    # fix round (critic: Undo): change-log keys in the kit's table form
    K.eq([str(Cfg.mp5Lk(x)) for x in ("boost.Strength.flat", "pw.Tank.hp", "pw.Mining.dd.mining", "power.gatherLevel")],
         ["boost[Strength.flat]", "pw[Tank.hp]", "pw[Mining.dd.mining]", "power.gatherLevel"], "MIG fix: mp5Lk - boost[<entry>] / pw[<entry>] (CONFIG-CONTRACT 1.4.6)")
    K.check(upd("pw.Tank.hp=12\n", False)[1] == "" and upd("boost.Strength.flat=3,6,9,12\n", True)[1] == "", "MIG each file moves only its own keys")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    J = lambda n: JClass(PKG + n)
    fc, fp = os.path.join(home, "config.properties"), os.path.join(home, "power.properties")
    lp = os.path.join(home, "config-changes.log")
    l0 = open(lp, "rb").read() if os.path.isfile(lp) else b""
    mids = {}

    def start(n):
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(fc)
        for m in ("migrate051", "migrate055", "migrate0518"):
            getattr(J("AccCfg"), m)()
        mids.setdefault(n, {})["c"] = open(fc, "rb").read()
        a = str(J("AccCfg").migrateP5(J("AccCfg").FILE, False))
        J("AccCfg").load(True)
        J("AccPower").FILE = Paths.get(fp)
        J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
        mids[n]["p"] = open(fp, "rb").read()
        b = str(J("AccCfg").migrateP5(J("AccPower").FILE, True))
        J("AccPower").load()
        return a, b
    a1, b1 = start(1)
    print("   live config:", a1[:200])
    print("   live power:", b1[:200])
    c1, p1 = open(fc, "rb").read(), open(fp, "rb").read()
    po, pn = _props(mids[1]["c"]), _props(c1)
    ch = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(pn.get("boost.Health.pct") == P5_BOOST[0], "LIVE the loader appended boost.Health.pct with its default (a key the file lacked)")
    ch = [c for c in ch if c != "boost.Health.pct"]
    K.eq(ch, sorted(["boost." + k for k in ("Health.flat", "Stamina.flat", "Stamina.regenPct", "Mana.pct", "Mana.floor", "Regeneration.pct", "Speed.pct",
                                            "Strength.flat", "MagicPower.flat", "Defense.flat", "Crit.chancePct", "Crit.damagePct", "Feather.fallPct", "Feather.jumpPct")]),
         "LIVE config.properties: exactly the 14 booster lines changed (Health.flat gone, a comment)")
    qo, qn = _props(mids[1]["p"]), _props(p1)
    chp = sorted(k for k in set(qo) | set(qn) if qo.get(k) != qn.get(k))
    K.check(len(chp) == 15 and all(k.startswith("pw.") and (k.endswith(".hp") or ".dd." in k) for k in chp), "LIVE power.properties: the 15 pw rows changed: %s" % chp)
    D = J("AccDefs")
    K.check(abs(float(D.BOOST[0 * 7 + 6]) - 8.0) < 1e-6 and abs(float(J("AccPower").E_VAL[0]) - 6.0) < 1e-9, "LIVE the loaders read the P5 numbers (Health Mythic 8 %, Tank hp 6)")
    lg = open(lp, "rb").read()[len(l0):].decode("utf-8")
    K.eq(lg.count("\tSkyyAccessories 0.5.30\t-\tupdate\t"), 14 + 15, "LIVE one change-log line per change (14 + 15)")
    lks = [ln.split("\t") for ln in lg.split("\n") if "\tSkyyAccessories 0.5.30\t-\tupdate\t" in ln]
    badk = [c[4] for c in lks if not ((c[4].startswith("boost[") or c[4].startswith("pw[")) and c[4].endswith("]") and ("boost." + c[4][6:-1] in ch + ["boost.Health.flat"] or "pw." + c[4][3:-1] in chp))]
    gone = [c for c in lks if c[4] == "boost[Health.flat]"]
    K.check(not badk and len(gone) == 1 and gone[0][6] == "(none)", "LIVE fix: every change-log key is boost[<entry>] / pw[<entry>] (Undo-able), Health.flat logged as removed (none): bad %s" % badk[:4])
    hist = [open(os.path.join(r_, f_), "rb").read() for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs]
    K.check(mids[1]["c"] in hist and mids[1]["p"] in hist, "LIVE History copies of both files before the P5 update")
    h1 = tree_hash(home)
    a2, b2 = start(2)
    K.check(a2 == "" and b2 == "" and tree_hash(home) == h1, "LIVE start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("defs", run_defs), ("pow", run_pow), ("pct", run_pct), ("item", run_item), ("mig", run_mig), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
