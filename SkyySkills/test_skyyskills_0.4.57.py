"""SkyySkills 0.4.57 - harness for BALANCE PASS P3 - XP (research/Balance-P3-XP-Spec.md; tools/skills_0_4_57_patch.py; tools/balance_model.py).
Build first: python tools/skills_0_4_57_patch.py && python SkyySkills/build_skyyskills_0.4.57.py

    python SkyySkills/test_skyyskills_0.4.57.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.56 -> 0.4.57: + P3Xp, P3Mig, CurveP3Mig; only the planned members differ
  P3  EXECUTED on a fresh default file: the one curve (the spec list x 120 %, class skills on it, no own lists, curve-size row 120), the
      XP rows (ores / trunks / crops / alchemy / smithing / acro / ranching), P3Xp: the level factor, catch-up (a class + skill levels in
      SkillStore.DATA), the past-life boost (a fake rebirth:fn:count + rebirth:fn:cap: rebirth 0..7, below / at the last cap), the server
      multiplier table, Exploration never; the gain paths' maths: BridgeXp.paidY / paidX / own (a SkyyFishing catch = earned XP, a Collections
      grant stays exact), SkillBonus.xpBonus + the "rebirth" source on Fishing / Acrobatics (not in xpSkills) and never Exploration, SkillV3
      without the rebirth xp.combat, RbStat Combat Echo (a fake rebirth:fn:stat) -> P3Xp.echo; SkillRb.facts arm.acrobatics; the Stats
      page lines; rebirth:reads:SkyySkills
  PM  P3Mig.plan / sameAfter / run: the 0.4.56 jar's default file -> exactly the 0.4.57 one; admin values kept; CRLF; marker = once;
      History + change-log rows (table rows as table[entry]); a fresh file untouched
  CM  CurveP3Mig on synthetic profiles: levels + progress kept on every changed slot, XP past the cap keeps its ratio (fake rebirth cap,
      rebirth 2), unknown cap -> by level, the floors file, History byte copies, a hand-edited levels= list keeps those slots, a failed
      rename puts every moved file back, run twice = once
      FIX ROUND: staged rebirth files (rebirth/<pkey>.rb-<txid>.properties x.<Slot>) moved with the same mapping + History; a crash between a
      rename and its marker -> the next start recognises the moved file (never moved twice); a file changed since History -> stop, untouched;
      a run that stops before any move forgets its History copy; an admin's short old list + unknown / raised cap keeps the shown level;
      no SkyyRebirth -> the base cap; the Stats P3 lines LAST and only while the 7-line list has room; the "Level curve size" label;
      the levels change-log rows carry the warning
  LIVE57  every one-time update in setup() order on a scratch COPY of the live data (NewBetaTest) + SkillCfg.load, started TWICE: every
      profile's every slot shows the same level on the new tables as on the old ones; start 2 changes nothing
  LC  0.4.53's level-cap phase on this jar
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import balance_model as BM


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T56 = _mod("test_skyyskills_0.4.56.py", "test_skyyskills_0_4_56")
T54 = T56.T54
T53, T49, T48 = T54.T53, T54.T49, T54.T48
VERSION = "0.4.57"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.56.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "balp3", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySkills")
ADDED = ["P3Xp", "P3Mig", "CurveP3Mig"]
EXPECT = {"AcroCfg": ["~m read"], "AlchCfg": ["~<clinit>", "~m defaultsMap", "~m read"], "BridgeXp": ["+m own", "+m paidY", "~m offerX", "~m paidX"],
          "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "FellCredit": ["~m one"],
          "GatherPace": ["~<clinit>", "~m read"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "MobXp": ["~m kill", "~m kill2"],
          "PDodge": ["~m read"], "PartyXp": ["~m one3"], "Ranch": ["~m read"], "RanchTask": ["~m run"], "RbStat": ["+m combatEcho", "~m cached", "~m fetch"],
          "SkillBonus": ["+m srcVal", "~m xpBonus"], "SkillCfg": ["+f P3PEND", "+m p3pend", "~<clinit>", "~m ensureCurve", "~m load", "~m upgradeLevels"],
          "SkillDefs": ["+f DEFAULT_056", "+f DEFAULT_RUN", "~<clinit>"], "SkillKit": ["~m customRead"], "SkillRb": ["~<clinit>"], "SkillV3": ["~m classXp"],
          "SkillXp": ["~m gain4"], "SkyySkillsPlugin": ["~m setup", "~m shutdown"], "SmithCfg": ["~m defaultsMap"], "StatsPage": ["+m lines0", "~m lines"]}
jpath, snapd, boot, fresh_load = T48.jpath, T53.snapd, T53.boot, T53.fresh_load
MIGS = T56.MIGS
f_lv = BM.f_lv


def old_defaults():
    """the 0.4.56 jar's default xp.properties (its own loader: parent = the platform loader, so the 0.4.57 jar on the class path never answers)"""
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "SkillCfg", loader=ld).DEFAULTS)


def _uuid(n):
    from jpype import JClass
    return JClass("java.util.UUID").fromString("00000000-0000-0000-0000-%012d" % n)


# ============================================================================================ P3: the curve, the rows, P3Xp, the bonus paths
def run_p3(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    r0 = fresh_load(J, Cfg, os.path.join(scratch, "p3"))
    SD, ST, P3, SB, BX, RB, V3, SC, KIT = J("SkillDefs"), J("SkillStore"), J("P3Xp"), J("SkillBonus"), J("BridgeXp"), J("RbStat"), J("SkillV3"), J("SkillCap"), J("SkillKit")
    br = ST.bridge()
    N = int(SD.N)
    names = [str(x) for x in SD.NAMES]
    # ---- the curve
    K.eq([int(x) for x in SD.DEFAULT_PER], BM.P3_BASE, "P3 SkillDefs.DEFAULT_PER = the spec list (100 %)")
    K.eq([int(x) for x in SD.DEFAULT_RUN], BM.P3_LEVELS, "P3 SkillDefs.DEFAULT_RUN = the spec list x 120 %")
    K.eq([int(x) for x in SD.PER], BM.P3_LEVELS, "P3 a fresh file loads the 120 % list")
    K.check(bool(SD.SAME), "P3 levels.class.sameAsOthers true on a fresh file (class skills on the same list)")
    ARCH, MIN, FOR, FARM, FISH, ACRO, EXP, ALC, SMI, COOK = (int(SD.indexOf("Archer")), int(SD.MINING), int(SD.FORAGING), int(SD.FARMING), int(SD.FISHING),
                                                         int(SD.ACROBATICS), int(SD.EXPLORATION), int(SD.ALCHEMY), int(SD.SMITHING), int(SD.COOKING))
    cum = [sum(BM.P3_LEVELS[:L]) for L in range(101)]
    for s in (ARCH, MIN, FARM, FISH, ACRO, EXP, int(SD.indexOf("Mage"))):
        K.eq([int(SD.cumOf(s)[L]) for L in (1, 20, 50, 100)], [cum[1], cum[20], cum[50], cum[100]], "P3 %s levels on the one list (no own list, class = others)" % names[s])
    K.check(int(SD.levelOf(ARCH, cum[20])) == 20 and int(SD.levelOf(ARCH, cum[20] - 1)) == 19 and int(SD.levelOf(MIN, cum[1])) == 1, "P3 level 20 at exactly its total")
    K.eq(str(KIT.customGet("levels.scale")), "120", "P3 Server Setup: the curve-size row reads 120 %")
    K.eq(str(KIT.customGet("levels.max")), "100", "P3 Server Setup: max level 100")
    # ---- the XP rows
    def rule(i):
        r = Cfg.resolve(i)
        return (names[int(r[0])] if int(r[0]) >= 0 and int(r[0]) < N else int(r[0]), int(r[1]))
    for i, want in (("Ore_Copper_Stone", 50), ("Ore_Iron_Stone", 105), ("Ore_Thorium_Stone", 245), ("Ore_Cobalt_Basalt", 610), ("Ore_Adamantite_Stone", 1150),
                    ("Ore_Mithril_Stone", 1800), ("Ore_Onyxium_Stone", 2650), ("Ore_Lead_Sandstone_SkyWynn", 370), ("Ore_Chromium_Shale_SkyWynn", 800)):
        K.eq(rule(i), ("Mining", want), "P3 Mining XP %s" % i)
    K.eq(rule("Rock_Stone"), ("Mining", 1), "P3 stone stays 1")
    for i, want in (("Wood_Oak_Trunk", 35), ("Wood_Birch_Trunk", 35), ("Wood_Beech_Trunk", 70), ("Wood_Maple_Trunk", 120), ("Wood_Redwood_Trunk", 650),
                    ("Wood_Bamboo_Trunk", 1200), ("Wood_Crystal_Trunk", 1600), ("Wood_Stormbark_Trunk", 1600), ("Wood_Fire_Trunk", 1050)):
        K.eq(rule(i), ("Foraging", want), "P3 Foraging XP %s" % i)
    for i, want in (("Plant_Crop_Wheat_Block", 40), ("Plant_Crop_Lettuce_Block", 80), ("Plant_Crop_Carrot_Block", 135), ("Plant_Crop_Onion_Block", 1600),
                    ("Plant_Crop_Health1_Block", 80)):
        K.eq(rule(i), ("Farming", want), "P3 Farming XP %s" % i)
    AL, SM, AC, PD, RC = J("AlchCfg"), J("SmithCfg"), J("AcroCfg"), J("PDodge"), J("Ranch")
    K.eq([int(x) for x in AL.TIER], [1500, 7400, 18200, 33900, 54400], "P3 alchemy.tierXp")
    K.eq([int(AL.XP.get(k)) for k in ("Potion_Health_Lesser", "Potion_Antidote", "Potion_Health_Small", "Potion_Health", "Potion_Health_Greater", "Weapon_Bomb_Popberry")],
         [1500, 2400, 7400, 18200, 33900, 10], "P3 alchemy.xp rows (the bomb stays 10: the craft-loop guard)")
    K.eq([float(AC.SPRINT), float(AC.RUN), float(AC.WALK), float(AC.JUMP_XP), float(AC.DODGE_XP), float(AC.FALL_DMG_XP), int(PD.XP)],
         [0.4, 0.25, 0.08, 3.0, 5.0, 15.0, 8], "P3 Acrobatics x1.5 + perfect dodge 8")
    K.check("Food_Egg:30" in str(Cfg.DEFAULTS) and str(J("GatherPace").TEXT) == "", "P3 ranching x10 (Food_Egg 30); no gathering pace skill")
    K.check(str(r0).startswith("") and "catch-up +10% a level past 5" in str(P3.loadText()), "P3 P3Xp read: %s" % P3.loadText())
    # ---- a player: Archer class 30, Mining 20 (gap 10 -> +50 %), Foraging 26 (gap 4 -> none), Fishing 3
    u = _uuid(57001)
    k = str(u)
    d = JArray(JClass("long"))(2 * N)
    lv = {ARCH: 30, MIN: 20, FOR: 26, FISH: 3, ACRO: 10, EXP: 5, ALC: 1}
    for s, L in lv.items():
        d[s] = cum[L] + 1
    ST.DATA.put(k, d)
    br.put("class:" + k, "Archer")
    K.eq([int(ST.level(u, s)) for s in (ARCH, MIN, FOR, FISH)], [30, 20, 26, 3], "P3 the test profile's levels")
    K.check(abs(float(P3.catchup(u, MIN)) - 1.5) < 1e-9 and float(P3.catchup(u, FOR)) == 1.0 and float(P3.catchup(u, ARCH)) == 1.0 and float(P3.catchup(u, EXP)) == 1.0,
            "P3 catch-up: Mining 10 behind = +50 %%, Foraging 4 behind = none, the class / Exploration never (%s)" % P3.catchup(u, MIN))
    d[MIN] = 1
    K.check(abs(float(P3.catchup(u, MIN)) - 2.0) < 1e-9, "P3 catch-up max +100 %% (30 behind): %s" % P3.catchup(u, MIN))
    d[MIN] = cum[20] + 1
    br.remove("class:" + k)
    K.check(float(P3.catchup(u, MIN)) == 1.0, "P3 no class = no catch-up")
    br.put("class:" + k, "Archer")
    K.check(abs(float(P3.levelF(u, FISH)) - f_lv(3)) < 1e-9 and abs(float(P3.levelF(u, ACRO)) - f_lv(10)) < 1e-9 and float(P3.levelF(u, MIN)) == 1.0,
            "P3 the own-level factor: Fishing x f(3), Acrobatics x f(10), Mining none")
    cf = float(P3.catchup(u, FISH))
    K.check(cf == 2.0 and abs(float(P3.mult(u, FISH, True)) - f_lv(3) * cf) < 1e-9 and abs(float(P3.mult(u, FISH, False)) - cf) < 1e-9,
            "P3 Fishing 27 behind: catch-up x2 (max); the level factor only on own XP")
    K.check(float(P3.mult(u, EXP, True)) == 1.0, "P3 Exploration: never a P3 multiplier")
    # ---- past-life boost: fake rebirth:fn:count + rebirth:fn:cap (base + 10 n)
    NREB = {"n": 0}

    @JImplements("java.util.function.Function")
    class Cnt(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer").valueOf(NREB["n"])

    @JImplements("java.util.function.Function")
    class Cap(object):
        @JOverride
        def apply(self, a):
            if str(a[1]) == "Exploration":
                return a[2]
            return JClass("java.lang.Integer").valueOf(int(a[2]) + 10 * NREB["n"])
    br.put("rebirth:fn:count", Cnt())
    br.put("rebirth:fn:cap", Cap())
    got = []
    for n in range(0, 8):
        NREB["n"] = n
        P3.RBN.clear()
        SC.CACHE.clear()
        got.append((n, int(P3.prevCap(k, MIN, n)), float(P3.pastLife(u, MIN)), float(P3.pastLife(u, ARCH))))
    K.eq([(g[0], g[1]) for g in got], [(0, 0), (1, 50), (2, 60), (3, 70), (4, 80), (5, 90), (6, 100), (7, 100)], "P3 the last run's cap by rebirth 0..7 (6+: the 100 clamp)")
    K.eq([g[2] for g in got], [1.0, 1.2, 1.45, 1.8, 2.25, 2.8, 2.8, 2.8], "P3 past-life boost on Mining 20 by rebirth (past the list: the last)")
    NREB["n"] = 1
    P3.RBN.clear()
    SC.CACHE.clear()
    d[MIN] = cum[50] + 5
    K.check(float(P3.pastLife(u, MIN)) == 1.0 and int(ST.level(u, MIN)) == 50, "P3 rebirth 1: Mining 50 = at the last cap -> first-time pace (no boost)")
    d[MIN] = cum[49] + 5
    K.check(float(P3.pastLife(u, MIN)) == 1.2, "P3 rebirth 1: Mining 49 -> x1.2")
    K.check(float(P3.pastLife(u, EXP)) == 1.0, "P3 Exploration never gets the past-life boost")
    NREB["n"] = 6
    P3.RBN.clear()
    SC.CACHE.clear()
    d[MIN] = cum[95] + 5
    K.check(float(P3.pastLife(u, MIN)) == 2.8, "P3 rebirth 6 (cap clamped at 100): level 95 still x2.8 - every level is a past-life level")
    NREB["n"] = 0
    P3.RBN.clear()
    SC.CACHE.clear()
    d[MIN] = cum[20] + 1
    # times(): chance rounding
    K.check(int(P3.times(JLong(100), 1.5)) == 150 and int(P3.times(JLong(10), 1.0)) == 10 and int(P3.times(JLong(0), 3.0)) == 0, "P3 times: exact products")
    tot = sum(int(P3.times(JLong(1), 1.25)) for _ in range(4000))
    K.check(4600 < tot < 5400, "P3 times: 1 x 1.25 pays 1.25 on average by chance (%d / 4000)" % tot)
    # ---- the server multiplier table
    t = "xp.skillMult.Mining=2\nxp.skillMult.Class=0.5\nxp.skillMult.Exploration=3\ncatchup.enabled=false\nrebirth.pastLifeXp=1.5,9\n"
    Props = JClass("java.util.Properties")
    p = Props()
    p.load(JClass("java.io.StringReader")(t))
    P3.read(p)
    K.check(float(P3.skillMult(MIN)) == 2.0 and float(P3.skillMult(ARCH)) == 0.5 and float(P3.skillMult(int(SD.indexOf("Mage")))) == 0.5 and float(P3.skillMult(EXP)) == 1.0,
            "P3 xp.skillMult: Mining x2, Class = every class skill x0.5, Exploration refused")
    K.check(float(P3.catchup(u, MIN)) == 1.0 and list(P3.PAST) == [1.5, 9.0] and abs(float(P3.mult(u, MIN, True)) - 2.0) < 1e-9, "P3 catchup.enabled=false; a custom past-life list")
    K.check(P3.checkPast("rebirth.pastLifeXp", "1.2,0.5") is not None and P3.checkPast("rebirth.pastLifeXp", "1.2,2") is None
            and P3.checkSkills("catchup.skills", "Mining,Exploration") is not None and P3.checkSkills("catchup.skills", "Mining, Fishing") is None
            and P3.checkMult("xp.skillMult[Class]", "2") is None and P3.checkMult("xp.skillMult[Nope]", "2") is not None, "P3 the check= hooks")
    p2 = Props()
    P3.read(p2)
    K.check(bool(P3.CATCH_ON) and list(P3.PAST) == [1.2, 1.45, 1.8, 2.25, 2.8] and float(P3.skillMult(MIN)) == 1.0, "P3 back to the defaults (no lines)")
    # ---- BridgeXp: a Fishing catch is earned XP (level factor), a Collections Fishing grant stays exact; Cooking grants get catch-up
    K.check(bool(BX.own(FISH, "fishing")) and not bool(BX.own(FISH, "collections")) and not bool(BX.own(MIN, "fishing")), "P3 BridgeXp.own: only a SkyyFishing catch into Fishing")
    fx = int(BX.paidY(u, FISH, JLong(1000), False, True, True))
    gx = int(BX.paidY(u, FISH, JLong(1000), True, True, False))
    K.check(abs(fx - 1000 * f_lv(3) * float(P3.catchup(u, FISH))) <= 1 and gx == round(1000 * float(P3.catchup(u, FISH))),
            "P3 paidY: a catch 1000 -> %d (x f(3) x catch-up), a Collections grant -> %d (catch-up only)" % (fx, gx))
    K.check(int(BX.paidX(u, EXP, JLong(500), True, True)) == 500, "P3 paidX: Exploration exact")
    # ---- SkillBonus: the rebirth source on skills outside bridge.bonus.xpSkills; Exploration never; SkillV3 drops the rebirth xp.combat
    HM = JClass("java.util.HashMap")
    D = JClass("java.lang.Double")
    src = HM()
    rb = HM()
    for kk, vv in (("xp.fishing", 0.3), ("xp.acrobatics", 0.2), ("xp.exploration", 0.5), ("xp.mining", 0.1), ("xp.combat", 0.25)):
        rb.put(kk, D.valueOf(vv))
    tr = HM()
    tr.put("xp.fishing", D.valueOf(0.7))
    tr.put("xp.combat", D.valueOf(0.04))
    src.put("rebirth", rb)
    src.put("trees", tr)
    br.put("skill:bonus:" + k, src)
    K.check(abs(float(SB.xpBonus(u, FISH)) - 0.3) < 1e-9, "P3 xpBonus Fishing (not in xpSkills): the rebirth source only (0.3), never the trees' 0.7")
    K.check(abs(float(SB.xpBonus(u, ACRO)) - 0.2) < 1e-9 and float(SB.xpBonus(u, EXP)) == 0.0, "P3 xpBonus Acrobatics 0.2 (rebirth), Exploration 0")
    K.check(abs(float(SB.xpBonus(u, MIN)) - 0.1) < 1e-9, "P3 xpBonus Mining (in xpSkills): every source, as before")
    K.check(abs(float(V3.classXp(u)) - 0.04) < 1e-9, "P3 SkillV3.classXp: the trees' xp.combat 0.04, not the rebirth Combat Echo 0.25 (now on kill XP)")
    J("BridgeCfg").BONUS = False
    K.check(float(SB.xpBonus(u, FISH)) == 0.0, "P3 bridge.bonus.enabled=false: no rebirth source either")
    J("BridgeCfg").BONUS = True
    # ---- Combat Echo via rebirth:fn:stat
    ST_ = {"combatxp": 37.0, "allxp": 12.0, "all": 3.0, "classxp": 15.0, "health": 0.0, "mana": 0.0}

    @JImplements("java.util.function.Function")
    class Stat(object):
        @JOverride
        def apply(self, a):
            return D.valueOf(ST_.get(str(a[1]), 0.0))
    br.put("rebirth:fn:stat", Stat())
    RB.refresh(u)
    K.check(abs(float(RB.combatEcho(u)) - 0.25) < 1e-9 and abs(float(RB.classXp(u)) - 0.15) < 1e-9, "P3 RbStat: Combat Echo = combatxp - allxp = 25 %%, Class Wisdom 15 %% kept")
    K.check(int(P3.echo(u, JLong(400))) == 500 and int(P3.echo(u, JLong(0))) == 0, "P3 P3Xp.echo: kill XP 400 -> 500")
    del ST_["combatxp"]
    RB.refresh(u)
    K.check(float(RB.combatEcho(u)) == 0.0 and abs(float(RB.classXp(u)) - 0.15) < 1e-9, "P3 an older SkyyRebirth (no combatxp): no Echo, the rest unchanged")
    # ---- the facts carry arm.acrobatics; the reader list; the Stats page lines
    f = J("SkillRb").facts(k, u, d)
    K.check(f.getProperty("arm.acrobatics") is not None and f.getProperty("arm.orchard") is not None, "P3 rebirth facts: arm.acrobatics = %s" % f.getProperty("arm.acrobatics"))
    P3.reads(True)
    K.eq(str(br.get("rebirth:reads:SkyySkills")), "xp.combat,xp.alchemy,xp.smithing,xp.fishing,xp.acrobatics", "P3 rebirth:reads:SkyySkills")
    P3.reads(False)
    K.check(br.get("rebirth:reads:SkyySkills") is None, "P3 the reader list removed at shutdown")
    NREB["n"] = 1
    P3.RBN.clear()
    SC.CACHE.clear()
    d[MIN] = cum[20] + 1
    lines = [str(x) for x in J("StatsPage").lines(u, MIN, 20, False)]
    K.check(any("Catch-up XP +50%" in x and "10 levels behind" in x for x in lines) and any("Past-life XP x1.2 below level 50" in x for x in lines),
            "P3 Stats page Mining: %s" % [x for x in lines if "Catch" in x or "Past" in x])
    lines = [str(x) for x in J("StatsPage").lines(u, FISH, 3, False)]
    K.check(any("grows with this skill" in x for x in lines), "P3 Stats page Fishing: the level factor line")
    # fix round: the P3 lines come LAST and only while the 7-line list has room
    lines = [str(x) for x in J("StatsPage").lines(u, MIN, 20, False)]
    isp3 = lambda x: x.startswith("Catch-up XP") or x.startswith("Past-life XP") or x.startswith("XP grows with") or x.startswith("Server XP multiplier")
    fp3 = [i for i, x in enumerate(lines) if isp3(x)]
    K.check(len(lines) <= 7 and fp3 and all(isp3(x) for x in lines[fp3[0]:]) and not any(isp3(x) for x in [str(y) for y in J("StatsPage").lines0(u, MIN, 20, False)]),
            "P3 fix: Stats P3 lines at the end (%s)" % lines)
    AL = JClass("java.util.ArrayList")
    full = AL()
    for i_ in range(7):
        full.add("line %d" % i_)
    P3.stats(u, MIN, full, 7)
    six = AL()
    for i_ in range(6):
        six.add("line %d" % i_)
    P3.stats(u, MIN, six, 7)
    K.check(full.size() == 7 and six.size() == 7 and str(six.get(6)).startswith("Catch-up XP"), "P3 fix: a full list gets no P3 line, a list with one free row gets one (%s)" % str(six.get(6)))
    src = open(os.path.join(HERE, "build_skyyskills_0.4.57.py"), encoding="utf-8").read()
    K.check('("levels.scale", "Level curve size", "levels"' in src and "Level curve size, other skills" not in src, "P3 fix: the row label is 'Level curve size'")
    K.save()


# ============================================================================================ PM: P3Mig
def run_pm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    M, Cfg, Hist, CLog, Rows = J("P3Mig"), J("SkillCfg"), J("CfgHist"), J("CfgLog"), J("CfgRows")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    S = lambda x: JString(x)
    MARK = str(M.MARK)
    NEW = str(Cfg.DEFAULTS)
    OLD = old_defaults()
    K.check("levels.class.sameAsOthers=false" in OLD and "prefix.Ore_Copper=Mining:5" in OLD, "the 0.4.56 default file read from the 0.4.56 jar")
    K.check(MARK in NEW and M.plan(S(NEW)) is None, "PM the 0.4.57 default file carries the marker -> never migrated")
    r = M.plan(S(OLD))
    got = (str(r[0]) if r is not None else "").replace("# SkyySkills 0.4.56 - XP rules.", "# SkyySkills 0.4.57 - XP rules.", 1)   # the version in the head comment
    import difflib
    dif = [x for x in difflib.unified_diff(NEW.split("\n"), got.split("\n"), lineterm="", n=0)][:12]
    K.check(r is not None and got == NEW, "PM P3Mig.plan(the 0.4.56 default file) = the 0.4.57 default file: %s" % dif)
    rows = [str(x) for x in r[1]]
    keys = rows[0::3]
    K.check(len(r[1]) % 3 == 0 and "levels" in keys and "levels.class.sameAsOthers" in keys and "levels.skill[Mining]" in keys and "prefix[Ore_Copper]" in keys
            and "block[Wood_Oak_Trunk]" in keys and "alchemy.xp[Potion_Health_Lesser]" in keys and "acro.jumpXp" in keys, "PM change-log rows: %d" % (len(rows) // 3))
    i = keys.index("levels.skill[Mining]")
    K.check(rows[3 * i + 2] == "(none)" and keys.count("block[Wood_Oak_Trunk]") == 1 and rows[3 * keys.index("block[Wood_Oak_Trunk]") + 1] == "(none)",
            "PM a removed own list logs -> (none), an added trunk row logs (none) ->")
    K.check(bool(M.sameAfter(S(OLD).getBytes("ISO-8859-1"), S(str(r[0])).getBytes("ISO-8859-1"), r)), "PM sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(S(OLD).getBytes("ISO-8859-1"), S(str(r[0]).replace("multiplier=1.0", "multiplier=2.0")).getBytes("ISO-8859-1"), r)), "PM sameAfter refuses another change (control)")
    # admin values kept
    hand = OLD.replace("prefix.Ore_Copper=Mining:5\n", "prefix.Ore_Copper=Mining:7\n").replace("levels.skill.Mining=", "levels.skill.Mining=9,")
    r2 = M.plan(S(hand))
    t2 = str(r2[0])
    K.check("prefix.Ore_Copper=Mining:7\n" in t2 and "levels.skill.Mining=9," in t2 and "prefix.Ore_Iron=Mining:105\n" in t2 and "kept" in str(r2[3]),
            "PM an admin's Copper XP and Mining list kept (INFO): %s" % str(r2[3])[:200])
    r3 = M.plan(S(OLD.replace("\n", "\r\n")))
    K.check(str(r3[0]) == str(r[0]).replace("\n", "\r\n"), "PM a CRLF file keeps CRLF (the same plan)")
    K.check(M.plan(S("a=1\n" + MARK + "\nlevels=5\n")) is None, "PM the marker -> nothing again")
    r4 = M.plan(S("gather.boost.skills=Foraging, Farming\nprefix.Ore_=Mining:5\\\n0\n"))
    K.check(str(r4[0]).startswith("gather.boost.skills=\nprefix.Ore_=Mining:5\\\n0\n"), "PM the spaced old pace list -> empty; a continued entry never rewritten")

    def start(d):
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        return str(M.run())
    for tag, txt in (("lf", OLD), ("crlf", OLD.replace("\n", "\r\n"))):
        d = os.path.join(scratch, "pm", tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snapd(d)
        r1 = start(d)
        s1 = snapd(d)
        want = (str(r[0]) if tag == "lf" else str(r3[0]))
        K.check(s1["xp.properties"].decode("latin-1") == want, "PM run %s: the planned file written" % tag)
        hist = [x for x in s1 if x.startswith("config-history/") and s1[x] == s0["xp.properties"]]
        K.check(len(hist) == 1, "PM run %s: the old file is in config-history" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("SkyySkills 0.4.57") == len(rows) // 3 and "\tlevels.skill[Mining]\t" in lg, "PM run %s: %d change-log rows" % (tag, lg.count("SkyySkills 0.4.57")))
        K.check("Undo" in r1, "PM run %s INFO: %s" % (tag, r1[:160]))
        K.check(start(d) == "" and snapd(d) == s1, "PM run %s: a second start changes nothing" % tag)
    d = os.path.join(scratch, "pm", "fresh")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(NEW.encode("latin-1"))
    s0 = snapd(d)
    K.check(start(d) == "" and snapd(d) == s0, "PM a fresh 0.4.57 file is untouched")
    K.save()


# ============================================================================================ CM: CurveP3Mig on synthetic profiles
def run_cm(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    C, M, Cfg, SD, ST, Hist, CLog, Rows = J("CurveP3Mig"), J("P3Mig"), J("SkillCfg"), J("SkillDefs"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = old_defaults()
    K.check("levels.class.sameAsOthers=false" in OLD and "prefix.Ore_Copper=Mining:5" in OLD, "the 0.4.56 default file read from the 0.4.56 jar")
    Props = JClass("java.util.Properties")

    def props(t):
        p = Props()
        p.load(JClass("java.io.StringReader")(t))
        return p
    to = C.tables(props(OLD), SD.DEFAULT_056, False)
    tn = C.tables(props(str(M.plan(JString(OLD))[0])), SD.DEFAULT_RUN, True)
    names = [str(x) for x in SD.NAMES]
    N = len(names)
    ARCH, MIN, FOR, FARM, EXP, ACRO = int(SD.indexOf("Archer")), int(SD.MINING), int(SD.FORAGING), int(SD.FARMING), int(SD.EXPLORATION), int(SD.ACROBATICS)
    oc = lambda s: [int(x) for x in to[s]]
    nc = lambda s: [int(x) for x in tn[s]]
    K.check(nc(MIN) == nc(ARCH) == nc(FOR) == [sum(BM.P3_LEVELS[:L]) for L in range(101)], "CM new tables: every slot on the P3 list")
    K.check(oc(MIN)[10] == 955 and oc(ARCH)[20] == 21540 and oc(FOR)[19] == sum([50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000]),
            "CM old tables: Mining's own list (10 at 955), the class table (20 at 21540), the general list")

    def lvl(c, x):
        L = 0
        while L + 1 < len(c) and x >= c[L + 1]:
            L += 1
        return L
    # remapX: level + progress kept, ratio past the cap
    import random
    rnd = random.Random(57)
    bad = 0
    for s in (MIN, FOR, ARCH, FARM, EXP):
        for _ in range(300):
            x = rnd.randint(1, oc(s)[-1] * 2)
            nx = int(C.remapX(x, to[s], tn[s], -1))
            if lvl(oc(s), x) != lvl(nc(s), nx):
                bad += 1
    K.check(bad == 0, "CM remapX (no cap known): 1500 random totals keep their level (%d moved)" % bad)
    x = oc(FOR)[12] + (oc(FOR)[13] - oc(FOR)[12]) // 4
    nx = int(C.remapX(x, to[FOR], tn[FOR], -1))
    p_new = (nx - nc(FOR)[12]) / (nc(FOR)[13] - nc(FOR)[12])
    K.check(lvl(nc(FOR), nx) == 12 and abs(p_new - 0.25) < 0.01, "CM Foraging 12 + 25 %% -> 12 + %.3f" % p_new)
    xc = oc(ARCH)[50] * 3
    K.eq(int(C.remapX(xc, to[ARCH], tn[ARCH], 50)), round(3 * nc(ARCH)[50]), "CM past the cap 50: the ratio (x3 the cap total) is kept")
    K.check(int(C.remapX(0, to[MIN], tn[MIN], 50)) == 0, "CM 0 XP stays 0")
    # ---- the full run: profiles, floors, fake rebirth cap (p2 = rebirth 2)
    base = os.path.join(scratch, "cm", "a")
    pdir = os.path.join(base, "players")
    os.makedirs(pdir)
    open(os.path.join(base, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    files = {
        "p1": "#SkyySkills\n#Thu Oct 15 23:14:06 MDT 2026\n%s=%d\n%s.paid=4\n%s=%d\n%s=%d\n%s=%d\n%s=%d\nquiet=false\n" % (
            names[MIN], oc(MIN)[7] + 3, names[MIN], names[FOR], oc(FOR)[9] + 77, names[ARCH], oc(ARCH)[15] + 1000, names[EXP], oc(EXP)[8] + 10, names[ACRO], 1862),
        "p2": "%s=%d\r\n%s=%d\r\n%s=%d\r\n" % (names[ARCH], oc(ARCH)[50] * 2, names[MIN], oc(MIN)[64] + 5, names[FARM], 0),
        "p3-p2": "%s=%d\n" % (names[FOR], oc(FOR)[55] + 9),
        "p4": "%s=%d\n" % (names[MIN], oc(MIN)[50] * 3),
    }
    for kf, t in files.items():
        open(os.path.join(pdir, kf + ".properties"), "wb").write(t.encode("latin-1"))
    os.makedirs(os.path.join(base, "rebirth"))
    staged = "#SkyySkills rebirth tx1 - staged\n#Mon Oct 19 10:00:00 MDT 2026\narm.class=1/2/3/4\ntx=tx1\nx.%s=%d\nx.%s=%d\nx.%s=0\n" % (names[ARCH], oc(ARCH)[50] * 2, names[MIN], oc(MIN)[64] + 5, names[FARM])
    open(os.path.join(base, "rebirth", "p2.rb-tx1.properties"), "wb").write(staged.encode("latin-1"))
    open(os.path.join(base, "rebirth", "p2.rb-tx1.properties.tmp"), "wb").write(b"torn")
    open(os.path.join(base, "level-floors.properties"), "w", newline="\n").write("# floors\np3-p2/%s=55,%d,\n" % (names[FOR], oc(FOR)[55]))
    NREB = {"p2": 2}

    @JImplements("java.util.function.Function")
    class Cap(object):
        @JOverride
        def apply(self, a):
            if str(a[1]) == "Exploration":
                return a[2]
            return JClass("java.lang.Integer").valueOf(int(a[2]) + 10 * NREB.get(str(a[0]), 0))
    ST.bridge().put("rebirth:fn:cap", Cap())

    def setup(b):
        Cfg.FILE = jpath(os.path.join(b, "xp.properties"))
        ST.DIR = jpath(os.path.join(b, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
    setup(base)
    s0 = snapd(base)
    ok = bool(C.run(jpath(base)))
    s1 = snapd(base)
    K.check(ok and int(C.MOVED) == 5, "CM run: done, 4 player files + 1 staged rebirth file moved (%s)" % C.LAST)
    hist = [k_ for k_ in s1 if k_.startswith("history/curve-p3/")]
    K.check(sorted(h.split("/")[-1] for h in hist) == sorted(["p1.properties", "p2.properties", "p3-p2.properties", "p4.properties", "level-floors.properties", "p2.rb-tx1.properties"])
            and all(s1[h] == s0[h.split("/", 3)[-1] if "players" not in h else "players/" + h.split("/")[-1]] for h in hist), "CM History: byte copies of every file")
    np = dict((kf, props(s1["players/%s.properties" % kf].decode("latin-1"))) for kf in files)
    gv = lambda kf, s: int(np[kf].getProperty(names[s]))
    K.check(lvl(nc(MIN), gv("p1", MIN)) == 7 and lvl(nc(FOR), gv("p1", FOR)) == 9 and lvl(nc(ARCH), gv("p1", ARCH)) == 15 and lvl(nc(EXP), gv("p1", EXP)) == 8,
            "CM p1: Mining 7, Foraging 9, Archery 15, Exploration 8 kept")
    K.check(np["p1"].getProperty(names[MIN] + ".paid") == "4" and np["p1"].getProperty("quiet") == "false", "CM p1: .paid and other lines kept")
    K.check(s1["players/p1.properties"].decode("latin-1").startswith("#SkyySkills\n#Thu Oct 15 23:14:06 MDT 2026\n"), "CM p1: the header comment bytes kept")
    xa = oc(ARCH)[50] * 2
    K.check(gv("p2", ARCH) == int(C.remapX(xa, to[ARCH], tn[ARCH], 70)) and lvl(nc(ARCH), gv("p2", ARCH)) == lvl(oc(ARCH), xa) and lvl(nc(MIN), gv("p2", MIN)) == 64
            and b"\r\n" in s1["players/p2.properties"] and gv("p2", FARM) == 0, "CM p2 (rebirth 2: cap 70 from the fake rebirth:fn:cap): Archery + Mining 64 by level, 0 stays, CRLF kept")
    K.eq(gv("p4", MIN), round(3 * nc(MIN)[50]), "CM p4 (no rebirth, cap 50): Mining 3x the cap total keeps the ratio (VP overflow unchanged)")
    K.check(lvl(nc(FOR), gv("p3-p2", FOR)) == 55, "CM p3-p2: Foraging 55 (a floor above the cap 50) kept")
    fl = s1["level-floors.properties"].decode("latin-1")
    K.check(("p3-p2/%s=55,%d,\n" % (names[FOR], nc(FOR)[55])) in fl and fl.startswith("# floors\n"), "CM floors: XP then -> newCum(55): %r" % fl)
    st = s1["curve-p3.properties"].decode("latin-1")
    K.check("complete=" in st and "done.p1=1" in st and "history=history/curve-p3/" in st, "CM marker file")
    lg = s1.get("curve-p3.log", b"").decode("utf-8")
    K.check(lg.count("\n") == 1 and "Undo" in lg and "5 profile file(s)" in lg and "rebirth-backup" in lg and "levels rows alone" in lg, "CM curve-p3.log: one line with the Undo: %s" % lg[:200])
    sp_ = props(s1["rebirth/p2.rb-tx1.properties"].decode("latin-1"))
    K.check(int(sp_.getProperty("x." + names[ARCH])) == gv("p2", ARCH) and int(sp_.getProperty("x." + names[MIN])) == gv("p2", MIN) and sp_.getProperty("x." + names[FARM]) == "0"
            and sp_.getProperty("arm.class") == "1/2/3/4" and sp_.getProperty("tx") == "tx1" and s1["rebirth/p2.rb-tx1.properties"].decode("latin-1").startswith("#SkyySkills rebirth tx1 - staged\n")
            and s1["rebirth/p2.rb-tx1.properties.tmp"] == b"torn",
            "CM fix: the staged rebirth file's x.<Slot> moved exactly like the player file (a commit's 'XP now - XP at prepare' stays ~0); other lines + the .tmp untouched")
    K.check("done.rb/p2.rb-tx1.properties=1" in st, "CM fix: the staged file has its own done marker")
    K.check(s1["xp.properties"] == s0["xp.properties"], "CM xp.properties untouched by CurveP3Mig (P3Mig does it after)")
    ok2 = bool(C.run(jpath(base)))
    K.check(ok2 and snapd(base) == s1, "CM a second start changes nothing (run once)")
    # ---- fix round: an admin's SHORT old list (50 levels) on a slot moving to the 100-level list: banked XP past its max
    SL = J("SkillLv")
    short = ",".join(str(v) for v in BM.P3_LEVELS[:50])
    ocs = SL.cum(C.parseLv(short))
    xs = int(int(ocs[50]) * 1.3)
    nxu = int(C.remapX(xs, ocs, tn[MIN], -1))
    nx70 = int(C.remapX(xs, ocs, tn[MIN], 70))
    nx50 = int(C.remapX(xs, ocs, tn[MIN], 50))
    K.check(int(C.shown(ocs, xs, -1)) == int(C.shown(tn[MIN], nxu, -1)) == 50 and int(C.shown(ocs, xs, 70)) == int(C.shown(tn[MIN], nx70, 70)) == 50
            and nx50 == round(1.3 * nc(MIN)[50]),
            "CM fix: a 50-level old list, XP x1.3 its max: cap unknown -> %d (Lv 50), cap 70 -> %d (Lv 50), cap 50 -> the ratio %d" % (nxu, nx70, nx50))
    K.eq(int(C.capOf("nobody", MIN, 100, props(OLD), to[MIN], None, None, 0)), 50, "CM fix: no SkyyRebirth (no rebirth:fn:cap) -> the base cap 50, not unknown")
    C.RB_DATA = True
    K.eq(int(C.capOf("nobody", MIN, 100, props(OLD), to[MIN], None, None, 0)), -1, "CM fix 2: Skyy_SkyyRebirth data but no rebirth:fn:cap yet (load order) -> unknown cap")
    C.RB_DATA = False
    # ---- fix round: a crash between a rename and its done marker
    b5 = os.path.join(scratch, "cm", "crash")
    os.makedirs(os.path.join(b5, "players"))
    open(os.path.join(b5, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    for i_ in range(3):
        open(os.path.join(b5, "players", "c%d.properties" % i_), "w").write("%s=%d\n%s=%d\n" % (names[FOR], 5000 + i_, names[ARCH], 30000 + i_))
    setup(b5)
    K.check(bool(C.run(jpath(b5))), "CM crash: first run done")
    a5 = snapd(os.path.join(b5, "players"))
    mk5 = os.path.join(b5, "curve-p3.properties")
    m5 = open(mk5, encoding="latin-1").read()
    open(mk5, "w", encoding="latin-1", newline="").write("".join(l_ for l_ in m5.splitlines(True) if not l_.startswith("complete=") and not l_.startswith("done.c1=") and not l_.startswith("floors.done")))
    K.check(bool(C.run(jpath(b5))) and snapd(os.path.join(b5, "players")) == a5 and int(C.SEEN) == 1 and int(C.MOVED) == 0 and "done.c1=1" in open(mk5, encoding="latin-1").read(),
            "CM fix: the next start sees c1 already moved (equals the plan from its History copy): never moved twice, marked, complete (%s)" % C.LAST)
    # ---- fix round: a file that differs from its History copy and from the plan -> stop, nothing changed
    m5 = open(mk5, encoding="latin-1").read()
    open(mk5, "w", encoding="latin-1", newline="").write("".join(l_ for l_ in m5.splitlines(True) if not l_.startswith("complete=") and not l_.startswith("done.c2=")))
    open(os.path.join(b5, "players", "c2.properties"), "w").write("%s=%d\n" % (names[FOR], 777))
    a6 = snapd(b5)
    h6 = [l_.split("=", 1)[1].strip() for l_ in open(mk5, encoding="latin-1").read().splitlines() if l_.startswith("history=")][0]
    ok6 = bool(C.run(jpath(b5)))
    a7 = snapd(b5)
    m6 = "".join(l_ for l_ in open(mk5, encoding="latin-1").read().splitlines(True) if not l_.startswith("#"))
    K.check(not ok6 and a7["players/c2.properties"] == a6["players/c2.properties"] and all(a7["players/c%d.properties" % i_] == a6[h6 + "/players/c%d.properties" % i_] for i_ in (0, 1))
            and "history=" not in m6 and "done." not in m6 and a7["xp.properties"] == a6["xp.properties"],
            "CM fix (fix 2): a file changed since History (not the plan): false, that file untouched, the moved files put back from History (no new-list XP after a false return), History forgotten")
    # ---- a hand-edited levels= list keeps those slots; class + own lists still move
    b2 = os.path.join(scratch, "cm", "hand")
    os.makedirs(os.path.join(b2, "players"))
    hand = OLD.replace("\nlevels=50,125,", "\nlevels=60,125,")
    open(os.path.join(b2, "xp.properties"), "wb").write(hand.encode("latin-1"))
    open(os.path.join(b2, "players", "h1.properties"), "w").write("%s=%d\n%s=%d\n%s=%d\n" % (names[FOR], 12345, names[ARCH], 54321, names[MIN], 999))
    setup(b2)
    K.check(bool(C.run(jpath(b2))), "CM hand: done")
    hp = props(open(os.path.join(b2, "players", "h1.properties")).read())
    K.check(hp.getProperty(names[FOR]) == "12345" and hp.getProperty(names[ARCH]) != "54321" and hp.getProperty(names[MIN]) != "999",
            "CM hand-edited levels=: Foraging (general list kept) not moved; Archery (class -> the admin's list) and Mining (own list dropped) moved")
    # ---- a failed rename puts the moved files back
    b3 = os.path.join(scratch, "cm", "fail")
    os.makedirs(os.path.join(b3, "players"))
    open(os.path.join(b3, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    for i_ in range(3):
        open(os.path.join(b3, "players", "f%d.properties" % i_), "w").write("%s=%d\n" % (names[FOR], 5000 + i_))
    setup(b3)
    t0 = snapd(os.path.join(b3, "players"))
    C.FAIL_RENAME = 2
    ok3 = bool(C.run(jpath(b3)))
    C.FAIL_RENAME = -1
    t1 = snapd(os.path.join(b3, "players"))
    m3 = open(os.path.join(b3, "curve-p3.properties")).read()
    m3b = "".join(l_ for l_ in m3.splitlines(True) if not l_.startswith("#"))
    K.check("history=" not in m3b and "done." not in m3b, "CM fix: the failed run moved nothing in the end -> its History copy is forgotten (the next start copies afresh)")
    K.check(not ok3 and t1 == t0 and "\ncomplete=" not in m3,
            "CM a failed rename: false, every player file back as it was, not complete (%s; %s)" % (ok3, dict((k_, (t0.get(k_), t1.get(k_))) for k_ in set(t0) | set(t1) if t0.get(k_) != t1.get(k_))))
    K.check(bool(C.run(jpath(b3))) and snapd(os.path.join(b3, "players")) != t0, "CM the next start finishes it")
    # ---- fix 2: SkyyRebirth's data folder present, rebirth:fn:cap not published (SkyyRebirth sets up later) -> unknown cap, levels kept
    capfn = ST.bridge().remove("rebirth:fn:cap")
    b7 = os.path.join(scratch, "cm", "rbx", "Skyy_SkyySkills")
    os.makedirs(os.path.join(b7, "players"))
    os.makedirs(os.path.join(scratch, "cm", "rbx", "Skyy_SkyyRebirth"))
    open(os.path.join(b7, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    x55 = oc(ARCH)[55] + 123   # a rebirthed Archer at Lv 55 (cap 60): the base cap 50 would take the ratio branch
    open(os.path.join(b7, "players", "r1.properties"), "w").write("%s=%d\n" % (names[ARCH], x55))
    setup(b7)
    ok7 = bool(C.run(jpath(b7)))
    n7 = int(props(open(os.path.join(b7, "players", "r1.properties")).read()).getProperty(names[ARCH]))
    K.check(ok7 and bool(C.RB_DATA) and int(C.UNKNOWN) >= 1 and lvl(nc(ARCH), n7) == lvl(oc(ARCH), x55) == 55,
            "CM fix 2: no rebirth:fn:cap but Skyy_SkyyRebirth exists -> unknown cap, moved by level: Lv %d -> %d (%s)" % (lvl(oc(ARCH), x55), lvl(nc(ARCH), n7), C.LAST))
    ST.bridge().put("rebirth:fn:cap", capfn)
    # ---- fix 2: a failed rename after an UNCHANGED file (done marker) -> every marker gone, History forgotten (never stuck)
    b8 = os.path.join(scratch, "cm", "fail2")
    os.makedirs(os.path.join(b8, "players"))
    open(os.path.join(b8, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    open(os.path.join(b8, "players", "a0.properties"), "w").write("quiet=true\n")
    for i_ in range(2):
        open(os.path.join(b8, "players", "f%d.properties" % i_), "w").write("%s=%d\n" % (names[FOR], 7000 + i_))
    setup(b8)
    t8 = snapd(os.path.join(b8, "players"))
    C.FAIL_RENAME = 2
    ok8 = bool(C.run(jpath(b8)))
    C.FAIL_RENAME = -1
    m8 = "".join(l_ for l_ in open(os.path.join(b8, "curve-p3.properties")).read().splitlines(True) if not l_.startswith("#"))
    K.check(not ok8 and snapd(os.path.join(b8, "players")) == t8 and "done." not in m8 and "history=" not in m8,
            "CM fix 2: a failed rename after an unchanged file: false, files back, no done marker, History forgotten: %r" % m8)
    open(os.path.join(b8, "players", "f0.properties"), "w").write("%s=%d\n" % (names[FOR], 7500))   # played on the old list meanwhile
    K.check(bool(C.run(jpath(b8))) and lvl(nc(FOR), int(props(open(os.path.join(b8, "players", "f0.properties")).read()).getProperty(names[FOR]))) == lvl(oc(FOR), 7500),
            "CM fix 2: the next start copies afresh and finishes (no 'differs from its copy' stop)")
    # ---- fix 2: a crash left a moved file marked done, then this start fails -> that file too goes back (no moved file after a false return)
    b9 = os.path.join(scratch, "cm", "crash2")
    os.makedirs(os.path.join(b9, "players"))
    open(os.path.join(b9, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    for i_ in range(3):
        open(os.path.join(b9, "players", "d%d.properties" % i_), "w").write("%s=%d\n" % (names[FOR], 6000 + i_))
    setup(b9)
    t9 = snapd(os.path.join(b9, "players"))
    K.check(bool(C.run(jpath(b9))), "CM crash2: first run done")
    mk9 = os.path.join(b9, "curve-p3.properties")
    m9 = open(mk9, encoding="latin-1").read()
    open(mk9, "w", encoding="latin-1", newline="").write("".join(l_ for l_ in m9.splitlines(True) if not l_.startswith("complete=") and not l_.startswith("done.d1=") and not l_.startswith("done.d2=") and not l_.startswith("floors.done")))
    shutil.copyfile(os.path.join(b9, [h for h in snapd(b9) if h.startswith("history/") and h.endswith("d1.properties")][0]), os.path.join(b9, "players", "d1.properties"))
    shutil.copyfile(os.path.join(b9, [h for h in snapd(b9) if h.startswith("history/") and h.endswith("d2.properties")][0]), os.path.join(b9, "players", "d2.properties"))
    C.FAIL_RENAME = 0
    ok9 = bool(C.run(jpath(b9)))
    C.FAIL_RENAME = -1
    m9b = "".join(l_ for l_ in open(mk9).read().splitlines(True) if not l_.startswith("#"))
    K.check(not ok9 and snapd(os.path.join(b9, "players")) == t9 and "done." not in m9b and "history=" not in m9b,
            "CM fix 2: d0 moved by a crashed start + this start fails -> d0 put back too, markers + History forgotten: %r" % m9b)
    # ---- fix 2: P3Mig fails after the saved XP moved -> this start loads the 0.4.57 lists from memory
    b10 = os.path.join(scratch, "cm", "pend")
    os.makedirs(os.path.join(b10, "players"))
    open(os.path.join(b10, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    open(os.path.join(b10, "players", "q1.properties"), "w").write("%s=%d\n" % (names[FOR], 9000))
    setup(b10)
    K.check(bool(C.run(jpath(b10))), "CM pend: saved XP moved")
    C.after(jpath(b10))   # P3Mig.run NOT called = its update failed
    K.check(bool(Cfg.P3PEND) and "xp=" not in open(os.path.join(b10, "curve-p3.properties")).read(), "CM fix 2: the xp.properties update did not land -> P3PEND, no xp= marker")
    Cfg.load()
    K.check(int(SD.cumOf(FOR)[50]) == sum(BM.P3_LEVELS[:50]) and int(SD.cumOf(ARCH)[50]) == sum(BM.P3_LEVELS[:50]) and open(os.path.join(b10, "xp.properties"), "rb").read() == OLD.encode("latin-1"),
            "CM fix 2: load() uses the planned 0.4.57 lists from memory (class + skills on the P3 list), the file untouched")
    K.check(str(M.run()).startswith("xp.properties updated"), "CM pend: the next try updates the file")
    C.after(jpath(b10))
    K.check(not bool(Cfg.P3PEND) and "xp=" in open(os.path.join(b10, "curve-p3.properties")).read(), "CM fix 2: landed -> P3PEND off, xp= in the marker")
    # ---- fix 2: the guard - a pre-0.4.57 xp.properties put back after the move
    xpnew = open(os.path.join(b10, "xp.properties"), "rb").read()
    hq = [h for h in snapd(b10) if h.startswith("history/curve-p3/") and h.endswith("q1.properties")][0]
    q1new = open(os.path.join(b10, "players", "q1.properties"), "rb").read()
    open(os.path.join(b10, "xp.properties"), "wb").write(OLD.encode("latin-1"))   # (a) only xp.properties put back
    g1 = bool(C.run(jpath(b10)))
    K.check(g1 and open(os.path.join(b10, "players", "q1.properties"), "rb").read() == q1new and "complete=" in open(os.path.join(b10, "curve-p3.properties")).read(),
            "CM fix 2 guard: only xp.properties put back (saved XP still moved) -> true, nothing moved (P3Mig updates the file again)")
    shutil.copyfile(os.path.join(b10, hq), os.path.join(b10, "players", "q1.properties"))   # (b) everything put back (+ a newer profile)
    open(os.path.join(b10, "players", "q2.properties"), "w").write("%s=%d\n" % (names[FOR], 4242))
    g2 = bool(C.run(jpath(b10)))
    m10 = open(os.path.join(b10, "curve-p3.properties")).read()
    K.check(g2 and open(os.path.join(b10, "players", "q1.properties"), "rb").read() == q1new and "keep.done.q2=1" in m10 and "rerun=" in m10 and "complete=" in m10
            and "q2.properties" in str(os.listdir(os.path.join(b10, "players"))) and props(open(os.path.join(b10, "players", "q2.properties")).read()).getProperty(names[FOR]) == "4242",
            "CM fix 2 guard: xp.properties + players put back -> moved again (q1 = the same new file), the newer q2 kept as it is: %r" % m10[-300:])
    K.check(str(M.run()).startswith("xp.properties updated"), "CM guard: P3Mig updates the put-back file again")
    C.after(jpath(b10))
    open(os.path.join(b10, "xp.properties"), "wb").write(OLD.encode("latin-1"))   # (c) everything put back, then played on 0.4.56
    hq2 = [l_.split("=", 1)[1].strip() for l_ in open(os.path.join(b10, "curve-p3.properties")).read().splitlines() if l_.startswith("history=")][0] + "/players/q1.properties"
    shutil.copyfile(os.path.join(b10, hq2), os.path.join(b10, "players", "q1.properties"))
    open(os.path.join(b10, "players", "q1.properties"), "a").write("played=1\n")
    s10 = snapd(os.path.join(b10, "players"))
    g3 = bool(C.run(jpath(b10)))
    K.check(not g3 and snapd(os.path.join(b10, "players")) == s10, "CM fix 2 guard: put back + played since -> cannot tell: false, nothing moved (WARN)")
    # ---- nothing to do
    b4 = os.path.join(scratch, "cm", "none")
    os.makedirs(b4)
    open(os.path.join(b4, "xp.properties"), "wb").write(str(Cfg.DEFAULTS).encode("latin-1"))
    setup(b4)
    K.check(bool(C.run(jpath(b4))) and "no level list changes" in open(os.path.join(b4, "curve-p3.properties")).read(), "CM a 0.4.57 file: nothing to move, marked complete")
    K.save()


# ============================================================================================ LIVE57: the live copy, every update in setup() order, twice
def run_live57(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy57")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, SD, C, M = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("SkillDefs"), J("CurveP3Mig"), J("P3Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Props = JClass("java.util.Properties")
    names = [str(x) for x in SD.NAMES]

    def props_file(f):
        p = Props()
        p.load(JClass("java.io.StringReader")(open(f, encoding="latin-1").read()))
        return p
    pdir = os.path.join(lc, "players")
    before = {}
    po = props_file(os.path.join(lc, "xp.properties"))
    to = C.tables(po, SD.DEFAULT_056, False)
    for fn in sorted(os.listdir(pdir)):
        if fn.endswith(".properties"):
            p = props_file(os.path.join(pdir, fn))
            before[fn] = dict((s, int(p.getProperty(names[s]) or 0)) for s in range(len(names)) if p.getProperty(names[s]) is not None)

    def start():
        Cfg.FILE = T48.jpath(os.path.join(lc, "xp.properties"))
        Sto.DATA.clear()
        Sto.DIR = T48.jpath(pdir)
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in MIGS)
        ok = bool(C.run(T48.jpath(lc)))
        r["CurveP3Mig"] = str(C.LAST) + (" ok" if ok else " NOT DONE")
        r["P3Mig"] = str(M.run()) if ok else ""
        if ok:
            C.after(T48.jpath(lc))   # fix 2: setup() order
        r["load"] = str(Cfg.load())
        return r
    s0 = snapd(lc)
    r1 = start()
    s1 = snapd(lc)
    K.notes.append("LIVE57 start 1: CurveP3Mig: %s | P3Mig: %s" % (r1["CurveP3Mig"][:300], r1["P3Mig"][:300]))
    K.check(r1["CurveP3Mig"].endswith(" ok") and "updated for 0.4.57" in r1["P3Mig"], "LIVE57 start 1: both updates ran")
    moved, same, total = 0, 0, 0
    for fn, b in before.items():
        p = props_file(os.path.join(pdir, fn))
        for s, x in b.items():
            nx = int(p.getProperty(names[s]))
            total += 1
            lo = int(SD.levelIn(to[s], x))
            ln = int(SD.levelOf(s, nx))
            if lo == ln:
                same += 1
            else:
                K.check(False, "LIVE57 %s %s: level %d before, %d after (XP %d -> %d)" % (fn, names[s], lo, ln, x, nx))
            if nx != x:
                moved += 1
    K.check(total > 0 and same == total, "LIVE57 every slot of every profile shows the same level on the new list (%d slots, %d totals moved, %d profiles)" % (total, moved, len(before)))
    K.check(abs(int(SD.cumOf(SD.MINING)[50]) - sum(BM.P3_LEVELS[:50])) == 0 and bool(SD.SAME), "LIVE57 the live copy now loads the P3 list (class skills on it)")
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "xp.properties" or k == "config-changes.log" or k.startswith("config-history/") or k.startswith("history/curve-p3/")
                or k.startswith("players/") or k.startswith("rebirth/") or k in ("curve-p3.properties", "curve-p3.log", "level-floors.properties") for k in ch),
            "LIVE57 start 1 changes only xp.properties, players' totals, History, the logs, the marker: %s" % [k for k in ch if not k.startswith("players/") and not k.startswith("history/") and not k.startswith("config-history/")])
    K.check(b"\nxp=" in s1.get("curve-p3.properties", b"") and not bool(Cfg.P3PEND), "LIVE57 fix 2: the xp.properties update landed -> xp= in the marker, P3PEND off")
    cl = s1.get("config-changes.log", b"").decode("utf-8", "replace")
    lvrows = [l_ for l_ in cl.splitlines() if "\tupdate\tlevels" in l_]
    K.check(lvrows and all(str(M.WHO_LV) in l_ for l_ in lvrows) and len(str(M.WHO_LV)) <= 40, "LIVE57 fix: the %d levels change-log row(s) point at curve-p3.log (short who, fix 2)" % len(lvrows))
    r2 = start()
    s2 = snapd(lc)
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2["P3Mig"] == "" and r2["CurveP3Mig"].strip() == "ok", "LIVE57 start 2 changes nothing")
    K.notes.append("LIVE57 load: %s" % r2["load"][:300])
    K.save()


if __name__ == "__main__":
    phases = [("p3", run_p3), ("pm", run_pm), ("cm", run_cm), ("live57", run_live57), ("lc", T53.run_lc)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
