"""SkyySkills 0.4.53 - harness for NO XP CAPS + FORTUNE NO CAP + LEVEL CAP 50 (+10 a rebirth) + ALLOY SMITHING XP + FARMING LEVEL LIST
(tools/skills_0_4_53_patch.py). Build first: python tools/skills_0_4_53_patch.py && python SkyySkills/build_skyyskills_0.4.53.py

    python SkyySkills/test_skyyskills_0.4.53.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.52 -> 0.4.53: + Nc53Mig, Fa53Mig, LvFloor; only the planned members differ
  MG / ZO / FL / LIVE50 / MN / LIVE52  the 0.4.48 - 0.4.52 phases on this jar (older updates + their live-copy runs); FO (0.4.48) is left
      out: exactly its 2 "doubleDropMax 1.0" checks fail by design (Fortune no cap), every other FO check passes on this jar
  NC  no caps: the defaults (file, code fields, rows), big XP gains pass every former cap (falls, moves, kills, mob-level kills, heals,
      perfect dodges, ranching, bridge per call + per minute), 0 = no cap everywhere, an admin's positive value still caps (control);
      Fortune above 100 % from perks (perk.doubleDropMax 0, extras = floor + chance, perk.fortuneGuard stop, an admin's 0.5 caps);
      alloy Smithing XP (SkyyAlloy recipe, 2 bars out -> the table value once; Furnace 2 out -> x2; Enchanted alloy -> smeltDefault once);
      Nc53Mig plan + run (old defaults -> 0, '1' / '1.0' spellings, hand edits kept, CRLF, last entry wins, multi-line untouched, marker,
      History, change log + Undo, second run nothing, fresh file untouched, no file nothing)
  LC  level cap: levels.runCap 50, rebirth 0..6 -> 50 / 60 / 70 / 80 / 90 / 100 / 110 (a fake rebirth:fn:cap = base + 10 n), class skills
      the same, Exploration = its table, XP keeps counting, MAX at the cap; runCap 0 = the table; LvFloor: a scanned profile at Mining 70 keeps
      70 (never lowered), more XP stays 70 at rebirth 0, 80 at rebirth 3, a rebirth reset ends the floor, Farming floor = its general level
      when this start added Farming's list, the file is read back and never rescanned; lvD / lvK (Overall / Mana readers) capped, a not-
      loaded array = the table level
  FA  Farming list: the default list, levels / hour = Mining's at Lv 5 / 15 / 30 (the model), Fa53Mig plan + run (LF / CRLF, an admin's
      own Farming list kept, marker, History, NEW_FARM, second run nothing, fresh file untouched)
  LIVE53  every one-time update in setup() order + LvFloor on a scratch COPY of the live data, twice
  PK / PG  0.4.47's asset-pack + page phases on this jar (skip with --no-old)
  AA  engine-access audit
NOT COVERED: the feel in game (Skyy's tests), Server Setup pages (one new row), SkyyRebirth's real rebirth:fn:cap (a fake with the same rule).
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T52 = _mod("test_skyyskills_0.4.52.py", "test_skyyskills_0_4_52")
T50, T49, T48 = T52.T50, T52.T49, T52.T48
VERSION = "0.4.53"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.52.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "sk53", "h")))
LIVE_DIR = T52.LIVE_DIR
ADDED = ["Nc53Mig", "Fa53Mig", "LvFloor"]
EXPECT = {"Acro": ["~m falls", "~m takeFall"],                                                    # fall caps: 0 = no cap
          "AcroCfg": ["~<clinit>", "~m ensureDefaults", "~m migrateFall", "~m read"],              # defaults 0 + the 0 floors
          "BridgeCfg": ["~<clinit>", "~m ensureDefaults", "~m read"], "DivCfg": ["~<clinit>", "~m ensureDefaults", "~m read"],
          "PDodge": ["~<clinit>", "~m read"], "Ranch": ["~<clinit>", "~m read"], "HealMig": ["~<clinit>"],   # HealMig's new value 0
          "PerkCfg": ["~<clinit>", "~m ensureDefaults", "~m read"], "Perks": ["~m chance", "~m chanceU", "~m fortune"],
          "MobXp": ["~m lvBase"], "SkillCfg": ["~<clinit>", "~m combatXp2", "~m load"],                 # combat.max 0 + levels.runCap
          "RecipeXp": ["~m classify"],                                                               # SkyyAlloy
          "SkillDefs": ["+f RUN_CAP", "~<clinit>", "~m capMax", "~m levelCap"],
          "SkillCap": ["+m capT", "+m lvD", "+m lvK", "+m runBase", "+m totalOf", "~m cap", "~m fetch", "~m into", "~m level", "~m need", "~m progress"],
          "Farm3": ["~m lvIn"], "Overall": ["~m listText", "~m sums"], "ClassMana": ["~m amountFor"], "ClassPower": ["~m boostRegen", "~m classLevel"],
          "ManaRegen": ["~m classPct"], "ClassCurve": ["~m deliver"], "OwnCurve": ["~m deliver"], "SkillRb": ["~m facts"], "SkillRunFn": ["~m apply"],
          "CfgFile": ["~<clinit>"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],   # the new row levels.runCap
          "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "SkyySkillsPlugin": ["~m setup"]}   # + version texts, the setup calls
jpath, loader_for = T48.jpath, T48.loader_for

NC_KEYS = [("acro.jumpCooldownMs", "800", "0"), ("acro.fallXpMax", "2000|2000.0", "0"), ("acro.fallMaxXpPerMinute", "3000|3000.0", "0"),
           ("acro.dodgeCooldownMs", "400", "0"), ("combat.max", "500", "0"), ("divinity.healXpMaxPerMinute", "900", "0"),
           ("bridge.maxXpPerCall", "500000", "0"), ("bridge.maxXpPerMinute", "3000000", "0"),
           ("acro.perfectDodge.maxXpPerMinute", "1000000", "0"), ("ranching.maxXpPerMinute", "1000000", "0"),
           ("perk.doubleDropMax", "1.0|1|1.00", "0")]
OLD_TXT = "".join("%s=%s\n" % (k, o.split("|")[0]) for k, o, n in NC_KEYS)
NEW_TXT = "".join("%s=%s\n" % (k, n) for k, o, n in NC_KEYS)


def mining(L):
    return (21 + 10 * L + 3 * L * L) // 2


def pace(L):
    return 3.0 if L <= 10 else (1.5 if L >= 20 else 3.0 - 1.5 * (L - 10) / 10.0)


def snapd(d):
    return dict((os.path.relpath(os.path.join(r_, fn), d).replace(os.sep, "/"), open(os.path.join(r_, fn), "rb").read())
                for r_, ds, fs in os.walk(d) for fn in fs)


def boot(K):
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    Cfg = J("SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    return J, Cfg


def fresh_load(J, Cfg, d):
    os.makedirs(d, exist_ok=True)
    Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
    J("CfgHist").DIR = None
    J("CfgRows").HOME = None
    J("CfgLog").FILE = None
    J("CfgLog").Q.clear()
    return str(Cfg.load())


# ============================================================================================ NC: no XP caps + Fortune + alloys + Nc53Mig
def run_nc(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong, JArray, JInt, JFloat
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    S = lambda x: JString(x)
    M = J("Nc53Mig")
    D = str(Cfg.DEFAULTS)
    for k, o, n in NC_KEYS:
        K.check(("\n%s=%s\n" % (k, n)) in ("\n" + D) and ("\n" + D).count("\n" + k + "=") == 1, "NC default file: %s=%s" % (k, n))
    K.check(D.count(str(M.MARK_ID)) == 1 and M.plan(S(D)) is None, "NC the default file carries the Nc53Mig marker -> never migrated")
    rows = dict((str(r[0]), r) for r in []) if False else None
    K.eq([str(x) for x in M.KEYS], [k for k, o, n in NC_KEYS], "NC Nc53Mig.KEYS")
    K.eq([str(x) for x in M.OLDS], [o for k, o, n in NC_KEYS], "NC Nc53Mig.OLDS")
    K.eq([str(x) for x in M.NEWS], [n for k, o, n in NC_KEYS], "NC Nc53Mig.NEWS")
    fresh_load(J, Cfg, os.path.join(scratch, "nc", "fresh"))
    AC, PC, DV, BC, PD, RC, SD = J("AcroCfg"), J("PerkCfg"), J("DivCfg"), J("BridgeCfg"), J("PDodge"), J("Ranch"), J("SkillDefs")
    K.check(int(AC.JUMP_CD) == 0 and int(AC.DODGE_CD) == 0 and float(AC.FALL_MAX) == 0.0 and float(AC.FALL_PER_MIN) == 0.0 and float(AC.MAX_PER_MIN) == 0.0,
            "NC loaded: jump / dodge cooldown 0, fall per landing / per minute 0, move per minute 0 (%s %s %s %s)" % (AC.JUMP_CD, AC.DODGE_CD, AC.FALL_MAX, AC.FALL_PER_MIN))
    K.check(int(Cfg.C_MAX) == 0 and int(DV.MAX_MIN) == 0 and int(BC.PER_MIN) == 0 and int(BC.PER_CALL) == 9223372036854775807 and int(PD.MAX_PM) == 0
            and int(RC.PER_MIN) == 0 and float(PC.DD_MAX) == 0.0 and int(PC.GUARD) == 100,
            "NC loaded: combat.max 0, heal / bridge / perfect dodge / ranching per minute 0, per call none, doubleDropMax 0, fortuneGuard 100")
    # ---- big XP gains pass every former cap
    Acro = J("Acro")
    s = JArray(JClass("double"))(400)
    now = 1700000000000
    K.check(float(Acro.takeFall(s, JLong(now), 5000000.0)) == 5000000.0 and float(Acro.takeFall(s, JLong(now + 10), 5000000.0)) == 5000000.0,
            "NC fall XP: 5 million twice in one second is paid (no per-minute cap; was 3000)")
    K.check(float(Acro.take(s, JLong(now), 9000000.0)) == 9000000.0, "NC move XP: 9 million in one go is paid (acro.maxXpPerMinute 0)")
    K.check(int(Cfg.combatXp2(None, JFloat(10000000.0), -1.0)) == 2000000, "NC kill XP: a 10 million HP NPC pays 2 million (no combat.max 500)")
    MX = J("MobXp")
    K.check(float(MX.lvBase(1000000.0, 1, 1.0)) > 100000.0, "NC mob-level kill XP above the old 500 maximum: %s" % MX.lvBase(1000000.0, 1, 1.0))
    U = JClass("java.util.UUID").randomUUID()
    HX = J("HealXp")
    K.check(int(HX.grant(U, JLong(50000000), DV.MAX_MIN, JLong(now))) == 50000000 and int(HX.grant(U, JLong(50000000), DV.MAX_MIN, JLong(now + 5))) == 50000000,
            "NC heal XP: 50 million twice in a minute is paid (no 900 cap)")
    K.check(int(PD.allowXp(U, JLong(70000000), JLong(now))) == 70000000 and int(RC.allow(U, JLong(70000000), JLong(now))) == 70000000,
            "NC perfect dodge + ranching: 70 million a minute each passes")
    BX = J("BridgeXp")
    K.check(bool(BX.allow(U, JLong(900000000000))) and bool(BX.allow(U, JLong(900000000000))), "NC bridge XP: 900 billion twice in a minute passes")
    K.check(900000000000 <= int(BC.PER_CALL), "NC bridge per call: 900 billion is under PER_CALL (no cap)")
    # control: an admin's positive cap still caps
    AC.FALL_PER_MIN = 100.0
    s2 = JArray(JClass("double"))(400)
    K.check(float(Acro.takeFall(s2, JLong(now), 5000.0)) == 100.0, "NC control: an admin's acro.fallMaxXpPerMinute 100 still caps (100 of 5000)")
    AC.FALL_PER_MIN = 0.0
    Cfg.C_MAX = 500
    K.check(int(Cfg.combatXp2(None, JFloat(10000000.0), -1.0)) == 500, "NC control: an admin's combat.max 500 still caps")
    Cfg.C_MAX = 0
    # ---- Fortune above 100 % from perks
    Pk = J("Perks")
    PC.DD[0] = 0.03   # 3 % a Mining level -> 300 % at level 100
    K.check(abs(float(Pk.chance(0, 100)) - 3.0) < 1e-9 and abs(float(Pk.fortune(U, 0, 100)) - 3.0) < 1e-9,
            "NC Fortune: the level perk alone gives 300 %% (no doubleDropMax 1.0 cap): chance %s fortune %s" % (Pk.chance(0, 100), Pk.fortune(U, 0, 100)))
    K.check(int(Pk.extras(3.0, 0.99)) == 3 and int(Pk.extras(1.5, 0.4)) == 2 and int(Pk.extras(1.5, 0.6)) == 1 and int(Pk.extras(250.0, 0.0)) == 100,
            "NC Fortune maths: 300 %% = 3 extra, 150 %% = 1 + 50 %% for a 2nd, the fortuneGuard 100 stop")
    PC.DD_MAX = 0.5
    K.check(abs(float(Pk.chance(0, 100)) - 0.5) < 1e-9 and abs(float(Pk.fortune(U, 0, 100)) - 0.5) < 1e-9, "NC control: an admin's doubleDropMax 0.5 still caps")
    PC.DD_MAX = 0.0
    PC.DD[0] = 0.005
    # ---- alloy Smithing XP (RecipeXp.classify)
    try:
        MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
        BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
        BT = JClass("com.hypixel.hytale.protocol.BenchType")
        CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
        RX = J("RecipeXp")

        def rec(bench, out_id, qty):
            po = MQ(out_id, None, None, qty, None)
            ins = JArray(MQ)([MQ("Ingredient_Bar_Thorium", None, None, 1, None), MQ("Ingredient_Bar_Lead_SkyWynn", None, None, 1, None)])
            br = JArray(BR)([BR(BT.Processing, bench, None, 1, None)])
            return CR(ins, po, JArray(MQ)([po]), qty, br, 5.0, False, 0)
        r = RX.classify(rec("SkyyAlloy", "Ingredient_Bar_Dusk_SkyWynn", 2))
        K.check(r is not None and int(r[0]) == int(SD.SMITHING) and int(r[1]) == 45, "NC alloy: a SkyyAlloy Dusk smelt (2 bars out) pays 45 Smithing once (0.4.52: nothing): %s" % (list(r) if r is not None else None))
        r = RX.classify(rec("SkyyAlloy", "Ingredient_Bar_Bronze", 2))
        K.check(r is not None and int(r[1]) == 16, "NC alloy: Bronze (Copper + Iron, 2 out) pays 16 once")
        r = RX.classify(rec("Furnace", "Ingredient_Bar_Dusk_SkyWynn", 2))
        K.check(r is not None and int(r[1]) == 90, "NC control: a Furnace recipe with 2 out still pays per bar (90)")
        r = RX.classify(rec("SkyyAlloy", "Skyy_Ench_Dusk", 2))
        K.check(r is not None and int(r[1]) == int(J("SmithCfg").DEFAULT), "NC Enchanted alloy: smithing.smeltDefault once (%s)" % (list(r) if r is not None else None))
        r = RX.classify(rec("Workbench", "Ingredient_Bar_Dusk_SkyWynn", 2))
        K.check(r is None, "NC control: a Workbench recipe pays no Smithing")
    except Exception as e:
        K.check(False, "NC alloy: could not build a CraftingRecipe: %s" % e)
    # ---- Nc53Mig plan
    old = "a=1\n# keep me\n" + OLD_TXT + "z=2\n"
    want = "a=1\n# keep me\n" + NEW_TXT + "z=2\n" + str(M.MARK) + "\n"
    r = M.plan(S(old))
    K.check(str(r[0]) == want, "NC plan: the 11 old defaults -> 0, every other byte kept, the marker at the end: %r" % str(r[0])[-300:])
    K.eq([str(x) for x in r[1]], [x for k, o, n in NC_KEYS for x in (k, o.split("|")[0], n)], "NC plan: one change-log row per key (old value as written)")
    K.check(str(r[3]) == "", "NC plan: nothing reported as kept")
    K.check(bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(str(r[0])).getBytes("ISO-8859-1"), r[2])), "NC sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(str(r[0]).replace("z=2", "z=3")).getBytes("ISO-8859-1"), r[2])), "NC sameAfter refuses another change")
    r = M.plan(S("perk.doubleDropMax=1\nacro.fallXpMax = 2000.0\n"))
    K.check(str(r[0]).startswith("perk.doubleDropMax=0\nacro.fallXpMax = 0\n") and len(r[1]) == 6, "NC plan: the '1' and '2000.0' spellings migrate too: %r" % str(r[0])[:80])
    hand = old.replace("combat.max=500", "combat.max = 800").replace("bridge.maxXpPerMinute=3000000", "bridge.maxXpPerMinute=5")
    r = M.plan(S(hand))
    b2 = str(r[0])
    K.check("combat.max = 800\n" in b2 and "bridge.maxXpPerMinute=5\n" in b2 and "acro.fallXpMax=0\n" in b2 and "combat.max=800 kept" in str(r[3])
            and "bridge.maxXpPerMinute=5 kept" in str(r[3]), "NC plan: an admin's own values are kept + reported: %s" % str(r[3])[:200])
    r = M.plan(S("acro.fallXpMax=0\nperk.doubleDropMax=0\nbridge.maxXpPerCall=0\nacro.fallMaxXpPerMinute=0\n"))
    K.check(len(r[1]) == 0 and all(("%s=0 kept - since 0.4.53 0 means NO CAP" % k) in str(r[3]) for k in ("acro.fallXpMax", "perk.doubleDropMax", "bridge.maxXpPerCall", "acro.fallMaxXpPerMinute"))
            and str(r[0]).startswith("acro.fallXpMax=0\nperk.doubleDropMax=0\n"), "NC plan: an existing 0 where 0 used to mean OFF is kept + gets the INFO line: %s" % str(r[3])[:200])
    r = M.plan(S("combat.max=0\nacro.jumpCooldownMs=800\n"))
    K.check(str(r[0]).startswith("combat.max=0\nacro.jumpCooldownMs=0\n") and str(r[3]) == "", "NC plan: a line already at 0 is left and not reported")
    r = M.plan(S(old.replace("\n", "\r\n")))
    K.check(str(r[0]) == want.replace("\n", "\r\n"), "NC plan: a CRLF file stays CRLF")
    K.check(M.plan(S(old + "# " + str(M.MARK_ID) + " x\n")) is None, "NC plan: the marker -> nothing (run once)")
    r = M.plan(S("combat.max=500\ncombat.max=600\n"))
    K.check(str(r[0]).startswith("combat.max=500\ncombat.max=600\n") and len(r[1]) == 0, "NC plan: the LAST entry decides (an admin's later 600 wins)")
    r = M.plan(S("combat.max=5\\\n00\n"))
    K.check(str(r[0]).startswith("combat.max=5\\\n00\n") and len(r[1]) == 0, "NC plan: a continued (multi-line) value is never touched")
    # ---- run end to end
    Hist, Rows, CLog = J("CfgHist"), J("CfgRows"), J("CfgLog")

    def start(d):
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        return str(M.run())
    for tag, txt in (("lf", old), ("crlf", old.replace("\n", "\r\n"))):
        d = os.path.join(scratch, "nc", tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snapd(d)
        r1 = start(d)
        s1 = snapd(d)
        nl = "\r\n" if tag == "crlf" else "\n"
        K.check(s1["xp.properties"].decode("latin-1") == want.replace("\n", nl), "NC run %s: the file = the plan" % tag)
        K.check(any(k.startswith("config-history/") and v == s0["xp.properties"] for k, v in s1.items()), "NC run %s: the old file is in config-history" % tag)
        logs = [v.decode("latin-1") for k, v in s1.items() if k.endswith("config-changes.log")]
        K.check(logs and all(k in logs[0] for k, o, n in NC_KEYS), "NC run %s: a change-log line per key (Undo)" % tag)
        K.check("Undo" in r1 and "0.4.53" in r1, "NC run %s: the INFO line: %s" % (tag, r1[:160]))
        K.check(start(d) == "" and snapd(d) == s1, "NC run %s: a second start changes nothing" % tag)
    d = os.path.join(scratch, "nc", "fresh2")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(D.encode("latin-1"))
    s0 = snapd(d)
    K.check(start(d) == "" and snapd(d) == s0, "NC run fresh: a fresh default file is untouched")
    d = os.path.join(scratch, "nc", "none")
    os.makedirs(d)
    K.check(start(d) == "" and snapd(d) == {}, "NC run none: no file -> nothing")
    K.save()


# ============================================================================================ LC: the level cap + LvFloor
def run_lc(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    base = os.path.join(scratch, "lc")
    fresh_load(J, Cfg, base)
    SD, SC, LF, ST = J("SkillDefs"), J("SkillCap"), J("LvFloor"), J("SkillStore")
    MIN, EXP = int(SD.MINING), int(SD.EXPLORATION)
    ARCH = int(SD.indexOf("Archer"))
    K.check(int(SD.RUN_CAP) == 50 and int(SD.maxOf(MIN)) == 100 and ARCH >= 0, "LC levels.runCap 50 on a fresh file (Mining table 100, Archer slot %d)" % ARCH)
    big = 10 ** 12
    K.check(int(SC.level("p-none", MIN, big)) == 50 and int(SC.cap("p-none", MIN)) == 50 and str(SC.progress("p-none", MIN, big)) == "MAX"
            and int(SC.need("p-none", MIN, big)) == 0, "LC no SkyyRebirth: Mining caps at 50 (MAX)")
    K.check(int(SC.level("p-none", ARCH, big)) == 50, "LC no SkyyRebirth: Archery caps at 50")
    K.check(int(SC.level("p-none", EXP, big)) == int(SD.maxOf(EXP)), "LC Exploration keeps its table max (%d)" % SD.maxOf(EXP))
    lv49 = int(SD.cumAt(MIN, 49))
    K.check(int(SC.level("p-none", MIN, lv49)) == 49 and str(SC.progress("p-none", MIN, lv49)) != "MAX", "LC below the cap: the table level (49), progress shown")
    # a fake SkyyRebirth: today's base + 10 x n (SkyyRebirth 0.3.5's RbMath.cap, caps.levels 10)
    NREB = {}

    @JImplements("java.util.function.Function")
    class FakeCap(object):
        @JOverride
        def apply(self, a):
            n = NREB.get(str(a[0]), 0)
            if str(a[1]) == "Exploration":
                return a[2]
            return JClass("java.lang.Integer").valueOf(int(a[2]) + 10 * n)
    br = ST.bridge()
    fake = FakeCap()
    br.put("rebirth:fn:cap", fake)
    got = []
    for n in range(0, 7):
        NREB["p-r"] = n
        SC.CACHE.clear()
        got.append((int(SC.level("p-r", MIN, big)), int(SC.level("p-r", ARCH, big))))
    K.eq(got, [(50, 50), (60, 60), (70, 70), (80, 80), (90, 90), (100, 100), (110, 110)], "LC rebirth 0..6: Mining + Archery caps 50 / 60 / ... / 100 / 110")
    K.notes.append("LC caps by rebirth: %s" % got)
    NREB["p-r"] = 2
    SC.CACHE.clear()
    l55 = int(SD.cumAt(MIN, 55))
    K.check(int(SC.level("p-r", MIN, l55)) == 55 and int(SC.level("p-r", MIN, l55 * 10)) == 70, "LC rebirth 2: XP for 55 -> 55; more XP stops at 70 (XP keeps counting)")
    SD.RUN_CAP = 0
    SC.CACHE.clear()
    NREB["p-r"] = 0
    K.check(int(SC.level("p-r", MIN, big)) == 100, "LC levels.runCap 0 = the table max (100)")
    SD.RUN_CAP = 50
    # ---- LvFloor: never lowered
    pdir = os.path.join(base, "players")
    os.makedirs(pdir, exist_ok=True)
    x70 = int(SD.cumAt(MIN, 70)) + 5
    names = [str(n) for n in SD.NAMES]
    FARM = int(SD.FARMING)
    xf = int(SD.cumAt(FARM, 100)) + 7   # Farming's OWN list says 100 - the general list says much less
    gen_f = int(SD.generalLevel(xf))
    xa = int(SD.cumAt(ARCH, 64))
    open(os.path.join(pdir, "u1.properties"), "w").write("%s=%d\n%s=%d\n%s=%d\n%s=%d\n" % (names[MIN], x70, names[FARM], xf, names[ARCH], xa, names[EXP], big))
    open(os.path.join(pdir, "u2.properties"), "w").write("%s=%d\n" % (names[MIN], int(SD.cumAt(MIN, 30))))
    ST.DIR = jpath(pdir)
    LF.NEW_FARM = True
    r = str(LF.start(jpath(base)))
    ff = os.path.join(base, "level-floors.properties")
    txt = open(ff).read() if os.path.isfile(ff) else ""
    K.check(("u1/%s=70,%d,\n" % (names[MIN], x70)) in txt and ("u1/%s=64," % names[ARCH]) in txt and "u2/" not in txt and ("/" + names[EXP] + "=") not in txt,
            "LC LvFloor: Mining 70 + Archery 64 recorded, a level-30 profile and Exploration not: %r" % txt[-300:])
    K.check(((("u1/%s=%d," % (names[FARM], gen_f)) in txt) if gen_f > 50 else (("u1/" + names[FARM] + "=") not in txt)),
            "LC LvFloor: Farming's floor = its general-list level %d (the new own list says 100) when Fa53Mig added the list this start" % gen_f)
    K.check("scanned 2 profile" in r, "LC LvFloor INFO: %s" % r)
    NREB.clear()
    SC.CACHE.clear()
    K.check(int(SC.level("u1", MIN, x70)) == 70 and int(SC.level("u1", MIN, x70 * 3)) == 70 and int(SC.capT("u1", MIN, x70)) == 70,
            "LC never lowered: u1's Mining 70 stays 70 at rebirth 0 (cap 50), more XP stays 70")
    K.check(int(SC.level("u1", ARCH, xa)) == 64, "LC never lowered: u1's Archery 64")
    K.check(int(SC.level("u2", MIN, x70)) == 50, "LC control: another profile with the same XP caps at 50")
    NREB["u1"] = 3
    SC.CACHE.clear()
    K.check(int(SC.level("u1", MIN, x70 * 3)) == 80, "LC u1 at rebirth 3: cap 80 beats the floor 70")
    NREB["u1"] = 1
    SC.CACHE.clear()
    small = int(SD.cumAt(MIN, 12))
    K.check(int(SC.level("u1", MIN, small)) == 12 and int(SC.capT("u1", MIN, small)) == 60, "LC a rebirth reset (XP below the floor's total) ends the floor: cap 60")
    ST.RBTX.put("u1", "tx-after-scan")
    K.check(int(SC.level("u1", MIN, x70 * 3)) == 60 and int(LF.floorOf("u1", MIN, x70 * 3)) == 0,
            "LC a rebirth since the scan (rb.lastTx changed) ends the floor even when the XP is back above its total: cap 60")
    ST.RBTX.remove("u1")
    NREB.clear()
    SC.CACHE.clear()
    # read back, never rescanned
    open(os.path.join(pdir, "u3.properties"), "w").write("%s=%d\n" % (names[MIN], x70))
    t0 = open(ff, "rb").read()
    LF.NEW_FARM = False
    r2 = str(LF.start(jpath(base)))
    K.check(open(ff, "rb").read() == t0 and int(SC.level("u1", MIN, x70)) == 70 and int(SC.level("u3", MIN, x70)) == 50 and "read" in r2,
            "LC LvFloor: the second start reads the file, never rescans (a new profile is not added): %s" % r2)
    # lvD / lvK: the Overall / Mana readers
    d = JArray(JClass("long"))(2 * int(SD.N))
    d[MIN] = x70 * 0 + int(SD.cumAt(MIN, 80))
    ST.DATA.put("p-load", d)
    K.check(int(SC.lvD(d, MIN, d[MIN])) == 50 and int(SC.lvK("p-load", MIN, d[MIN])) == 50, "LC lvD / lvK: a loaded array caps at 50 (Overall, Mana per level, class power)")
    d2 = JArray(JClass("long"))(2 * int(SD.N))
    d2[MIN] = d[MIN]
    K.check(int(SC.lvD(d2, MIN, d2[MIN])) == 80, "LC lvD: an array not in SkillStore.DATA = the table level (0.4.52 exactly)")
    d[ARCH] = int(SD.cumAt(ARCH, 90))
    K.check(int(J("ClassPower").classLevel("Archer", d)) == 50, "LC ClassPower.classLevel: Archery 90 by XP counts 50")
    K.check(int(J("Farm3").lvIn(d, MIN)) == 50, "LC Farm3.lvIn (re-bodied after SkillCap): capped")
    # the pure maths
    K.check(int(SD.levelCap(MIN, big, 50)) == 50 and int(SD.capMax(MIN, 50)) == 50 and int(SD.capMax(MIN, 120)) == 120 and int(SD.levelCap(MIN, 0, 50)) == 0,
            "LC SkillDefs.levelCap / capMax honour a cap below the table")
    K.save()


# ============================================================================================ FA: the Farming level list + Fa53Mig
def run_fa(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    S = lambda x: JString(x)
    M = J("Fa53Mig")
    D = str(Cfg.DEFAULTS)
    fresh_load(J, Cfg, os.path.join(scratch, "fa", "fresh"))
    SD = J("SkillDefs")
    FARM = int(SD.FARMING)
    lst = [int(x) for x in str(M.VALS[0]).split(",")]
    want = [max(1, int(mining(L) * (80.0 / (30 * (0.85 + 0.15 * 6.5) * 1.25)) * pace(L - 1) + 0.5)) for L in range(1, 101)]
    want[0] = 50   # level 1 = the general list's 50 (review fix)
    gen = [int(x) for x in str(Cfg.DEFAULTS).split("\nlevels=")[1].split("\n")[0].split(",")]
    cf = cg = 0
    worst = 0
    for i in range(100):
        cf += lst[i]
        cg += gen[i]
        worst = max(worst, cf - cg)
    K.check(worst <= 0 and lst[0] == 50, "FA the new Farming list never needs more XP than the general list for any level (no level drops): worst %d" % worst)
    for x in (50, 59, 141, 1000, 50000):
        K.check(int(SD.levelOf(FARM, x)) >= int(SD.generalLevel(x)), "FA %d Farming XP: own-list level %s >= general %s" % (x, SD.levelOf(FARM, x), SD.generalLevel(x)))
    K.eq(lst, want, "FA the Farming list = Mining's x 1.169 x the pace (100 levels)")
    K.check(bool(SD.hasOwn(FARM)) and int(SD.maxOf(FARM)) == 100 and int(SD.levelOf(FARM, sum(lst[:10]))) == 10 and int(SD.levelOf(FARM, sum(lst[:10]) - 1)) == 9,
            "FA a fresh file: Farming levels on its own list (level 10 at %d XP)" % sum(lst[:10]))
    rates = []
    for L in (5, 15, 30):
        mine = 30 * (0.85 + 0.15 * 6.5) * 1.25 * 60 / mining(L + 1)
        farm = 80 * pace(L) * 60 / (int(SD.cumAt(FARM, L + 1)) - int(SD.cumAt(FARM, L)))
        rates.append((L, round(mine, 2), round(farm, 2)))
        K.check(abs(farm / mine - 1.0) < 0.02, "FA Lv %d: Farming %.2f levels an hour = Mining %.2f (the model)" % (L, farm, mine))
    K.notes.append("FA levels an hour (Mining, Farming): %s" % rates)
    head = str(M.HEAD)
    K.check(str(M.MARK_ID) in head and D.count(str(M.MARK_ID)) == 1 and M.plan(S(D)) is None, "FA the default file carries the Fa53 block (marker) -> never migrated")
    old = "a=1\nlevels.skill.Mining=1,2,3\n"
    r = M.plan(S(old))
    K.check(str(r[0]) == old + "\n" + head + "levels.skill.Farming=" + str(M.VALS[0]) + "\n" and list(r[1]) == ["levels.skill.Farming"],
            "FA plan: the block (marker head + the list) appended after a blank line")
    r = M.plan(S(old.replace("\n", "\r\n")))
    K.check(str(r[0]) == (old + "\n" + head + "levels.skill.Farming=" + str(M.VALS[0]) + "\n").replace("\n", "\r\n"), "FA plan: CRLF kept")
    r = M.plan(S(old + "levels.skill.Farming=5,6\n"))
    K.check(len(r[1]) == 0 and "levels.skill.Farming=5,6\n" in str(r[0]) and str(r[0]).count("levels.skill.Farming=") == 1,
            "FA plan: an admin's own Farming list is kept (only the marker block)")
    K.check(M.plan(S(old + "# " + str(M.MARK_ID) + "\n")) is None, "FA plan: the marker -> nothing")
    Hist, Rows, CLog, LF = J("CfgHist"), J("CfgRows"), J("CfgLog"), J("LvFloor")
    for tag, txt in (("lf", old), ("crlf", old.replace("\n", "\r\n"))):
        d = os.path.join(scratch, "fa", tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snapd(d)
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        LF.NEW_FARM = False
        r1 = str(M.run())
        s1 = snapd(d)
        K.check("levels.skill.Farming=" in s1["xp.properties"].decode("latin-1") and bool(LF.NEW_FARM) and "0.4.53" in r1, "FA run %s: added, NEW_FARM set: %s" % (tag, r1[:120]))
        K.check(any(k.startswith("config-history/") and v == s0["xp.properties"] for k, v in s1.items()), "FA run %s: the old file in config-history" % tag)
        LF.NEW_FARM = False
        K.check(str(M.run()) == "" and snapd(d) == s1 and not bool(LF.NEW_FARM), "FA run %s: a second start changes nothing" % tag)
    d = os.path.join(scratch, "fa", "fresh2")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(D.encode("latin-1"))
    s0 = snapd(d)
    Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
    K.check(str(M.run()) == "" and snapd(d) == s0, "FA run fresh: untouched")
    K.save()


# ============================================================================================ LIVE53: every update in setup() order on a COPY of the live data
def run_live53(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy53")
    shutil.copytree(home, lc)
    L = loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, SD, LF, SC = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("SkillDefs"), J("LvFloor"), J("SkillCap")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    migs = T49.OLD_MIGS + ["Zo49Mig", "Fl50Mig", "Mn52Mig", "Nc53Mig", "Fa53Mig"]

    def start():
        Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
        Sto.DATA.clear()
        Sto.DIR = jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in migs)
        r["load"] = str(Cfg.load())
        r["floor"] = str(LF.start(jpath(lc)))
        return r
    s0 = snapd(lc)
    r1 = start()
    s1 = snapd(lc)
    vals = (int(SD.RUN_CAP), int(Cfg.C_MAX), float(J("PerkCfg").DD_MAX), float(J("AcroCfg").FALL_MAX), bool(SD.hasOwn(SD.FARMING)))
    r2 = start()
    s2 = snapd(lc)
    K.notes.append("LIVE53: Nc53Mig: %s | Fa53Mig: %s | floors: %s | now runCap/combat.max/doubleDropMax/fallXpMax/Farming own = %s"
                   % (r1.get("Nc53Mig", "")[:500], r1.get("Fa53Mig", "")[:200], r1.get("floor", ""), vals))
    xp0 = s0.get("xp.properties", b"").decode("latin-1").replace("\r", "")
    xp1 = s1["xp.properties"].decode("latin-1").replace("\r", "")
    for k, o, n in NC_KEYS:
        lines = [ln for ln in xp0.split("\n") if ln.split("=", 1)[0].strip() == k]
        if lines and lines[-1].split("=", 1)[1].strip() in o.split("|"):
            nowv = [ln for ln in xp1.split("\n") if ln.split("=", 1)[0].strip() == k][-1]
            K.check(nowv == "%s=%s" % (k, n), "LIVE53: the live copy's untouched %s=%s is now %s" % (k, lines[-1].split("=", 1)[1].strip(), n))
    K.check(("levels.skill.Farming=" in xp1) and bool(SD.hasOwn(SD.FARMING)), "LIVE53: Farming's own list added and loaded")
    K.check(vals[0] == 50 and vals[1] == 0 and vals[2] == 0.0 and vals[3] == 0.0, "LIVE53: runCap 50, combat.max 0, doubleDropMax 0, fallXpMax 0 loaded: %s" % (vals,))
    K.check("level-floors.properties" in s1 and "level-floors.properties" not in s0, "LIVE53: level-floors.properties written once")
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2.get("Nc53Mig") == "" and r2.get("Fa53Mig") == "", "LIVE53: start 2 changes nothing")
    K.check(all(s0.get(k) == s1.get(k) for k in s0 if k.startswith("players/")), "LIVE53: player files untouched")
    # every live profile: no level went down (the capped level is the old table level wherever it was <= 50, the floor above)
    pdir = os.path.join(lc, "players")
    worst = []
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".properties"):
            continue
        k = fn[:-11]
        p = {}
        for ln in open(os.path.join(pdir, fn), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                p[ln.split("=", 1)[0].strip()] = ln.split("=", 1)[1].strip()
        for s in range(int(SD.N)):
            nm = str(SD.NAMES[s])
            try:
                x = int(p.get(nm, "0"))
            except ValueError:
                continue
            if x <= 0:
                continue
            before = int(SD.generalLevel(x)) if s == int(SD.FARMING) else int(SD.levelOf(s, x))
            if s == int(SD.EXPLORATION) or before <= 50:
                continue
            now = int(SC.level(k, s, x))
            worst.append((k, nm, before, now))
            K.check(now >= before, "LIVE53: %s %s %d not lowered (now %d)" % (k, nm, before, now))
    K.notes.append("LIVE53: live levels above 50: %s" % (worst or "none"))
    K.save()


if __name__ == "__main__":
    # the 0.4.48 - 0.4.52 phases on this jar (older updates + their live-copy runs), then this round's
    # FO (0.4.48) left out: on 0.4.53 exactly its 2 doubleDropMax-1.0 checks fail by design (Fortune no cap: "doubleDropMax 1" is 0 now,
    # base 0.5 + 0.8 is no longer cut to 1.0 -> 2.8 instead of 2.5); every other FO check passed on this jar (run 2026-10-18)
    phases = [("mg", T48.run_mg), ("zo", T49.run_zo), ("fl", T50.run_fl), ("live50", T50.run_live50),
              ("mn", T52.run_mn), ("live52", T52.run_live52), ("nc", run_nc), ("lc", run_lc), ("fa", run_fa), ("live53", run_live53)]
    if "--no-old" not in sys.argv:
        T47 = _mod("test_skyyskills_0.4.47.py", "test_skyyskills_0_4_47")
        phases += [("pack", T47.T46.run_pack), ("pages", T47.run_pages)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
