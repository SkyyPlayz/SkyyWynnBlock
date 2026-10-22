"""SkyySkills 0.4.60 - harness for BALANCE PASS P8c (the Beastmastery skill; research/Balance-P8-Rebirth-Spec.md 4.4 / 5; tools/skills_0_4_60_patch.py).
Build first: python tools/skills_0_4_60_patch.py && python SkyySkills/build_skyyskills_0.4.60.py

    python SkyySkills/test_skyyskills_0.4.60.py [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes, line endings kept, setup order PlMigP8 -> BmMigP8c -> SkillCfg.load, one new class
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.59 -> 0.4.60: + BmMigP8c; only the planned members differ
  BM   EXECUTED: slot 20 Beastmastery (N 21, NAMES / LABELS / indexOf, /skills row after Exploration, always grantable, resets on rebirth,
       levels on the P3 general table with the run cap); BridgeXp.paidY: no server multiplier, catch-up (in the default catchup.skills) +
       past-life apply, the skill:bonus sources only when bridge.bonus.addxpSkills lists it (xpBonus 0 otherwise; the Stats rebirth line
       shows past-life only); beastBase (x beast.xpFactor 1 / 2 / 0.5 / 0); SkillXp.petXp never reports Beastmastery to pets:fn:onxp; the
       Stats page lines + how-to; treeName / treeAvailable (SkyyTrees' tree:names); the rebirth facts (x.Beastmastery, arm.beastmastery); a
       0.4.59 staged rebirth without x.Beastmastery; the Server Setup row; P3Xp.read of beast.xpFactor; BridgeTask's no-chat-line rule
  SKIP EXECUTED on a REAL EntityStatMap: RbStat / ClassStat flatMax skip skyygear_hp, skyypet_health, skyypet_mana -> ClassStat.health takes
       the class Health % of the flat max only (a player with gear + pet Health %)
  PM   BmMigP8c.plan / sameAfter: the 0.4.59 jar's default file -> exactly the 0.4.60 one; a hand-edited catchup.skills kept + noted; no line
       = nothing rewritten; a half-migrated file; CRLF; the marker once; the change-log row carries the exact old line (Undo)
  LIVE60 every one-time update in setup() order (0.4.59's list + BmMigP8c) on a scratch COPY of the live data + SkillCfg.load, started TWICE;
       every live player file loads with Beastmastery 0 XP / level 0 / nothing owed, and its next save adds exactly Beastmastery=0 +
       Beastmastery.paid=0 (every other line unchanged)
  PAIR SkyySkills 0.4.60 + SkyyPets 0.4.9 + SkyyTrees 0.4.7 in ONE JVM (all classes load with -Xverify:all): SkyyTrees' TreeV3.level of the
       Beastmastery tree = SkyySkills' real skill:fn:level (Beastmastery 12 -> 12 points); SkyyPets' PetBm reaches SkyySkills' real
       skill:fn:addxp (an offline player is refused there - FALSE, counted, no exception)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp8c", "sk")]
T59 = _mod(os.path.join(HERE, "test_skyyskills_0.4.59.py"), "test_skyyskills_0_4_59")
T58, T57 = T59.T58, T59.T57
T48, T53 = T57.T48, T57.T53
VERSION = "0.4.60"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.59.py")
PATCH = os.path.join(TOOLS, "skills_0_4_60_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.59.jar")
PETS_JAR = os.path.join(ROOT, "SkyyPets", "SkyyPets-0.4.9.jar")
TREES_JAR = os.path.join(ROOT, "SkyyTrees", "SkyyTrees-0.4.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T58.LIVE_DIR
ADDED = ["BmMigP8c"]
EXPECT = {}   # filled in below after the first run (checked by hand)
OLD_CATCH = "Mining,Foraging,Farming,Fishing,Alchemy,Smithing,Cooking,Acrobatics"
NEW_CATCH = OLD_CATCH + ",Beastmastery"
MARK_ID = "Balance P8c Beastmastery (SkyySkills 0.4.60)"
_props = T58._props


def _old_defaults():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "SkillCfg", loader=ld).DEFAULTS)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.60 - build script') and g.count('VERSION = "0.4.60"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 1 and ", plm8, bm60, lvf," in g, "S one new class (BmMigP8c), written out")
    su = g[g.index("{PKG}.CurveP3Mig.run(base)"):]
    K.check(su.index("{PKG}.P4Mig.run();") < su.index("{PKG}.PlMigP8.run();") < su.index("{PKG}.BmMigP8c.run();") < su.index("SkillCfg.load"),
            "S setup: P4Mig -> PlMigP8 -> BmMigP8c -> SkillCfg.load")
    K.check("this.slot != {PKG}.SkillDefs.EXPLORATION && this.slot != {PKG}.SkillDefs.BEASTMASTERY, false);" in g,
            "S BridgeTask: no '+N XP' chat line for Beastmastery grants (as Exploration)")
    ox = g[g.index("public static long offerX("):]
    ox = ox[:ox.index('}}""", bxp))')]
    K.check(ox.index("PER_CALL") < ox.index("P3Xp.beastBase(base)") < ox.index("paidY("), "S offerX: beast.xpFactor on the pets source after the per-call guard, before paidY")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_bm(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = T57.boot(K)
    T57.fresh_load(J, Cfg, os.path.join(scratch, "bm"))
    SD, ST, P3, SB, BX, BC, SC, XP = J("SkillDefs"), J("SkillStore"), J("P3Xp"), J("SkillBonus"), J("BridgeXp"), J("BridgeCfg"), J("SkillCap"), J("SkillXp")
    br = ST.bridge()
    N = int(SD.N)
    BEAST = int(SD.BEASTMASTERY)
    K.check(N == 21 and BEAST == 20 and str(SD.NAMES[20]) == "Beastmastery" and str(SD.LABELS[20]) == "Beastmastery" and int(SD.indexOf("Beastmastery")) == 20
            and int(SD.indexOf("beastmastery")) == 20, "BM slot 20 Beastmastery (N 21; NAMES / LABELS / indexOf)")
    rows = [int(x) for x in SD.ROW_SLOTS]
    K.check(len(rows) == 13 and rows.index(20) == rows.index(int(SD.EXPLORATION)) + 1 and rows[-1] == int(SD.COMBAT), "BM /skills rows: Beastmastery after Exploration, 13 rows: %s" % rows)
    K.check(bool(BC.GRANT[BEAST]) and "Beastmastery" in str(BC.GRANT_TEXT), "BM always grantable through skill:fn:addxp (%s)" % BC.GRANT_TEXT)
    K.check(bool(SD.rebirthResets(BEAST)) and bool(SD.boostable(BEAST)) and not bool(SD.isClass(BEAST)) and int(SD.perkRow(BEAST)) == -1,
            "BM resets on rebirth, boostable, not a class, no perk row")
    K.check(bool(P3.CATCH[BEAST]) and str(P3.CATCH_TEXT).endswith("Beastmastery"), "BM in the catchup.skills default: %s" % P3.CATCH_TEXT)
    cum = [sum(int(x) for x in list(SD.PER)[:L]) for L in range(101)]
    K.check(int(SD.levelOf(BEAST, cum[20])) == 20 and int(SD.levelOf(BEAST, cum[20] - 1)) == 19, "BM levels on the P3 general table")
    # a player: Archer 30, Beastmastery 2 (28 behind the class -> catch-up x2)
    ARCH, MIN, FISH = int(SD.indexOf("Archer")), int(SD.MINING), int(SD.FISHING)
    u = T57._uuid(60001)
    k = str(u)
    d = JArray(JClass("long"))(2 * N)
    d[ARCH] = cum[30] + 1
    d[BEAST] = cum[2] + 1
    ST.DATA.put(k, d)
    br.put("class:" + k, "Archer")
    K.eq(int(ST.level(u, BEAST)), 2, "BM the test profile's Beastmastery level 2")
    K.check(abs(float(P3.catchup(u, BEAST)) - 2.0) < 1e-9, "BM catch-up: 28 behind the class -> x2 (the max)")
    Cfg.MULT = 3.0
    pb = int(BX.paidY(u, BEAST, 1000, True, True, False))
    pf = int(BX.paidY(u, FISH, 1000, True, True, False))
    K.check(pb == 2000 and pf == int(BX.paidY(u, FISH, 1000, True, True, False)) and pf >= 3000,
            "BM paidY: Beastmastery 1000 pet XP -> 2000 (catch-up x2; NOT the server multiplier x3 - a Fishing grant gets it: %d): %d" % (pf, pb))
    Cfg.MULT = 1.0
    # past-life on replayed levels
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

    def at(n):
        NREB["n"] = n
        P3.RBN.clear()
        SC.CACHE.clear()
    at(1)
    K.check(int(P3.prevCap(k, BEAST, 1)) == 50 and abs(float(P3.pastLife(u, BEAST)) - 1.1) < 1e-9, "BM rebirth 1: Beastmastery 2 < the last cap 50 -> past-life x1.1")
    K.check(int(BX.paidY(u, BEAST, 1000, True, True, False)) == 2200, "BM rebirth 1: 1000 -> 2200 (x2 catch-up x1.1 past-life)")
    # the skill:bonus sources: only when bridge.bonus.addxpSkills lists it
    HM, D_ = JClass("java.util.HashMap"), JClass("java.lang.Double")
    src, rb = HM(), HM()
    rb.put("xp.beastmastery", D_.valueOf(0.5))
    src.put("rebirth", rb)
    br.put("skill:bonus:" + k, src)
    K.check(float(SB.xpBonus(u, BEAST)) == 0.0 and int(BX.paidY(u, BEAST, 1000, True, True, False)) == 2200,
            "BM default: SkyyRebirth's xp.beastmastery (Insight + keep + Echo) is NOT added again - the pet XP carries it (xpBonus 0)")
    sl = P3.rbLine(u, BEAST)
    K.eq(str(sl), "Rebirth XP x1.1: past-life x1.1 below Lv 50", "BM the Stats rebirth line shows past-life only")
    gx = BC.BONUS_ADDXP
    gx[BEAST] = True
    K.check(abs(float(SB.xpBonus(u, BEAST)) - 0.5) < 1e-9 and int(BX.paidY(u, BEAST, 1000, True, True, False)) == 3300,
            "BM an admin lists Beastmastery in bridge.bonus.addxpSkills -> the bonus applies (2200 x 1.5)")
    gx[BEAST] = False
    br.remove("skill:bonus:" + k)
    at(0)
    # beastBase / P3Xp.read of beast.xpFactor
    K.check(int(P3.beastBase(1000)) == 1000 and int(P3.beastBase(0)) == 0, "BM beastBase x1 (default)")
    Props = JClass("java.util.Properties")
    for txt, want in (("beast.xpFactor=2\n", 2.0), ("beast.xpFactor=0.5\n", 0.5), ("beast.xpFactor=0\n", 0.0), ("beast.xpFactor=-1\n", 0.0),
                      ("beast.xpFactor=abc\n", 1.0), ("beast.xpFactor=50\n", 10.0), ("", 1.0)):
        p = Props()
        p.load(JClass("java.io.StringReader")(txt))
        P3.read(p)
        K.check(abs(float(P3.BEAST_F) - want) < 1e-9, "BM P3Xp.read %r -> %s" % (txt.strip(), want))
    P3.BEAST_F = 2.0
    K.check(int(P3.beastBase(1000)) == 2000, "BM beast.xpFactor 2: 1000 pet XP -> 2000")
    P3.BEAST_F = 0.0
    K.check(int(P3.beastBase(1000)) == 0, "BM beast.xpFactor 0: nothing")
    P3.BEAST_F = 1.0
    # no pet XP loop
    seen = []

    @JImplements("java.util.function.Function")
    class OnXp(object):
        @JOverride
        def apply(self, a):
            seen.append(str(a[1]))
            return JClass("java.lang.Boolean").TRUE
    br.put("pets:fn:onxp", OnXp())
    XP.petXp(u, BEAST, 100)
    XP.petXp(u, MIN, 100)
    K.eq(seen, ["Mining"], "BM SkillXp.petXp: Mining is reported to pets:fn:onxp, Beastmastery never (no pet XP loop)")
    # the Stats page
    SP = J("StatsPage")
    lines = [str(x) for x in SP.lines(u, BEAST, 2, False)]
    nxt = [str(x) for x in SP.lines(u, BEAST, 2, True)]
    K.check(lines[:2] == ["2 Beastmastery tree points - 1 a level (/tree beasts)", "Beastmastery XP per pet XP: x1"] and any(x.startswith("Catch-up XP") for x in lines),
            "BM Stats page now: %s" % lines)
    K.check(nxt and nxt[0] == "+1 Beastmastery tree point at level 3", "BM Stats page next: %s" % nxt)
    K.check("pets gain XP" in str(SP.how(BEAST)), "BM how-to: %s" % SP.how(BEAST))
    # the tree button
    K.eq(str(SB.treeName(BEAST)), "beastmastery", "BM treeName -> /tree beastmastery")

    @JImplements("java.util.function.Function")
    class TL(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer").valueOf(0)
    br.put("tree:fn:level", TL())
    br.put("tree:names", "Mining,Foraging,Combat,Beastmastery,Farming")
    K.check(bool(SB.treeAvailable(BEAST)), "BM a Tree button while SkyyTrees lists Beastmastery in tree:names")
    br.put("tree:names", "Mining,Foraging")
    K.check(not bool(SB.treeAvailable(BEAST)), "BM no Tree button without it")
    # the rebirth participant: facts
    RBF = J("SkillRb")
    f = RBF.facts(k, u, d)
    K.check(str(f.getProperty("x.Beastmastery")) == str(cum[2] + 1) and str(f.getProperty("arm.beastmastery")).startswith(str(cum[2] + 1) + "/"),
            "BM rebirth facts: x.Beastmastery + arm.beastmastery: %s / %s" % (f.getProperty("x.Beastmastery"), f.getProperty("arm.beastmastery")))
    # Server Setup row
    rows_ = dict((str(r[0]), [str(x) for x in list(r)]) for r in J("CfgRows").header()[7])
    r_ = rows_.get("beast.xpFactor")
    K.check(r_ is not None and r_[2] == "levels" and r_[3] == "dec" and r_[4] == "1" and r_[5] == "0" and r_[6] == "10" and len(r_[10]) <= 100,
            "BM Server Setup row Skills -> Levels: Beastmastery XP per pet XP (dec 0-10, default 1): %s" % r_)
    K.eq(rows_.get("catchup.skills", [None] * 5)[4], NEW_CATCH, "BM the catch-up row's default lists Beastmastery")
    K.check(str(Cfg.DEFAULTS).count(MARK_ID) == 1 and ("\nbeast.xpFactor=1\n") in str(Cfg.DEFAULTS) and ("\ncatchup.skills=" + NEW_CATCH + "\n") in str(Cfg.DEFAULTS),
            "BM the fresh file: beast.xpFactor=1, catchup.skills + Beastmastery, the marker once")
    K.save()


def run_skip(out, jar, scratch, _home):
    from jpype import JClass, JInt, JFloat, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    TP = _mod(os.path.join(ROOT, "SkyyPets", "test_skyypets_0.4.8.py"), "test_skyypets_0_4_8_x")
    TP.fake_stats(JClass)
    J, Cfg = T57.boot(K)
    T57.fresh_load(J, Cfg, os.path.join(scratch, "skip"))
    RB, CS = J("RbStat"), J("ClassStat")
    for kk in ("skyygear_hp", "skyypet_health", "skyypet_mana", "skyyskill_classhp", "skyyacc_hp"):
        K.check(bool(RB.skip(JString(kk))) and bool(CS.skip(JString(kk))), "SKIP %s is a percent layer (RbStat + ClassStat skip it)" % kk)
    K.check(not bool(CS.skip(JString("skyyskill_health"))) and not bool(CS.skip(JString("armor_hp"))), "SKIP flat layers still count")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    HPI, MNI = int(DST.getHealth()), int(DST.getMana())
    m = ESM()
    m.update()
    m.putModifier(JInt(HPI), "armor_flat", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(100.0)))
    flat = float(CS.flatMax(m.get(JInt(HPI)), JInt(HPI)))
    m.putModifier(JInt(HPI), "skyygear_hp", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(40.0)))
    m.putModifier(JInt(HPI), "skyypet_health", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(25.0)))
    m.putModifier(JInt(MNI), "skyypet_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(30.0)))
    K.check(abs(float(CS.flatMax(m.get(JInt(HPI)), JInt(HPI))) - flat) < 1e-4 and abs(float(RB.flatMax(m.get(JInt(HPI)), JInt(HPI))) - flat) < 1e-4,
            "SKIP flatMax with gear Health %% (+40) and pet Health %% (+25): the base stays %.1f (0.4.59 counted %.1f)" % (flat, flat + 65))
    mn = float(RB.flatMax(m.get(JInt(MNI)), JInt(MNI)))
    K.check(abs(mn - float(J("Overall").typeMax(JInt(MNI)))) < 1e-4, "SKIP pet Mana %% (+30) is not in the Mana %% base: %.1f" % mn)
    # the class Health % on the flat max only (a Warrior: class.health from the class table)
    u = T57._uuid(60010)
    J("SkillStore").bridge().put("class:" + str(u), "Warrior")
    pct = float(CS.healthPct(J("Overall").classOf(u)))
    CS.health(u, m)
    cur = m.getModifier(JInt(HPI), str(CS.KEY_HP))
    want = round(flat * pct) / 100.0
    K.check(pct != 0.0 and cur is not None and abs(float(cur.getAmount()) - want) < 0.011,
            "SKIP ClassStat.health: Warrior %+.1f %% of the flat %.1f = %.2f (not of %.1f with the gear / pet layers): %s" % (pct, flat, want, flat + 65, None if cur is None else cur.getAmount()))
    K.save()


def run_pm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    M, Cfg = JClass(PKG + "BmMigP8c"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = _old_defaults()
    NEW = str(Cfg.DEFAULTS)
    K.check(("\ncatchup.skills=" + OLD_CATCH + "\n") in OLD and "Balance P8 rebirth (SkyySkills 0.4.59)" in OLD and MARK_ID not in OLD, "PM the 0.4.59 jar's file holds the old catch-up list")
    r = M.plan(JString(OLD))
    K.check(r is not None and _props(str(r[0])) == _props(NEW), "PM the 0.4.59 jar's default file -> exactly the 0.4.60 one (Properties)")
    K.eq([str(x) for x in r[1]], ["catchup.skills", OLD_CATCH, NEW_CATCH, "beast.xpFactor", "(none)", "1"], "PM change-log rows: the list moved (old line exact = Undo) + the row added")
    K.check(bool(M.sameAfter(JString(OLD).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r)), "PM sameAfter: only the planned keys differ")
    nb = str(r[0])
    K.check(nb.replace("\ncatchup.skills=" + NEW_CATCH + "\n", "\ncatchup.skills=" + OLD_CATCH + "\n", 1).startswith(OLD)
            and nb.endswith("# " + MARK_ID + ": the Beastmastery skill - its XP per pet XP and its catch-up\n"), "PM bytes: only the value text changed, the block appended, the marker last")
    K.check(M.plan(r[0]) is None and M.plan(JString(NEW)) is None, "PM the marker: a second plan / a fresh file = null")
    hand = OLD.replace("\ncatchup.skills=" + OLD_CATCH + "\n", "\ncatchup.skills=Mining,Foraging\n")
    rh = M.plan(JString(hand))
    ph = _props(str(rh[0]))
    K.check(ph["catchup.skills"] == "Mining,Foraging" and "catchup.skills=Mining,Foraging kept" in str(rh[3]) and ph["beast.xpFactor"] == "1"
            and [str(x) for x in rh[1]] == ["beast.xpFactor", "(none)", "1"], "PM a hand-edited list kept + noted, only the row added: %s" % str(rh[3])[:160])
    nol = OLD.replace("\ncatchup.skills=" + OLD_CATCH + "\n", "\n")
    rn = M.plan(JString(nol))
    pn = _props(str(rn[0]))
    K.check("catchup.skills" not in pn and pn["beast.xpFactor"] == "1" and str(rn[3]) == "", "PM no list line = nothing written for it (the new code default applies)")
    half = OLD + "beast.xpFactor=3\n"
    rf = M.plan(JString(half))
    pf = _props(str(rf[0]))
    K.check(pf["beast.xpFactor"] == "3" and pf["catchup.skills"] == NEW_CATCH and str(rf[0]).count("beast.xpFactor=") == 1 and str(rf[0]).rstrip("\n").endswith("catch-up"),
            "PM half-migrated (the row already there, no marker): the row kept, the list moved, the marker last")
    multi = OLD.replace("\ncatchup.skills=" + OLD_CATCH + "\n", "\ncatchup.skills=Mining,Foraging,Farming,Fishing,\\\n  Alchemy,Smithing,Cooking,Acrobatics\n")
    rm = M.plan(JString(multi))
    K.check(_props(str(rm[0]))["catchup.skills"] == OLD_CATCH and "kept" in str(rm[3]), "PM a continued (multi-line) list = an admin's: kept")
    crlf = OLD.replace("\n", "\r\n")
    rc = M.plan(JString(crlf))
    K.check(_props(str(rc[0])) == _props(NEW) and "\n" not in str(rc[0]).replace("\r\n", ""), "PM CRLF: same settings, every line ending CRLF")
    K.save()


def run_live60(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy60")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, M4, M8, M9, P3, SD = (J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"),
                                                                J("CurveP3Mig"), J("P3Mig"), J("P4Mig"), J("PlMigP8"), J("BmMigP8c"), J("P3Xp"), J("SkillDefs"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    xp = os.path.join(lc, "xp.properties")

    def start():
        Cfg.FILE = T48.jpath(xp)
        Sto.DATA.clear()
        Sto.DIR = T48.jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in T57.MIGS)
        ok = bool(C.run(T48.jpath(lc)))
        r["P3Mig"] = str(M.run()) if ok else ""
        if ok:
            C.after(T48.jpath(lc))
        r["P4Mig"] = str(M4.run())
        r["PlMigP8"] = str(M8.run())
        r["BmMigP8c"] = str(M9.run())
        r["load"] = str(Cfg.load())
        return r
    before = _props(open(xp, encoding="latin-1").read())
    r1 = start()
    s1 = T53.snapd(lc)
    K.notes.append("LIVE60 start 1: BmMigP8c: %s" % r1["BmMigP8c"][:200])
    K.check("updated for 0.4.60" in r1["BmMigP8c"], "LIVE60 start 1: BmMigP8c ran: %s" % r1["BmMigP8c"][:160])
    after = _props(open(xp, encoding="latin-1").read())
    K.eq((after.get("catchup.skills"), after.get("beast.xpFactor")), (NEW_CATCH, "1"), "LIVE60 the live copy: catchup.skills + Beastmastery, beast.xpFactor=1")
    K.check(bool(P3.CATCH[20]) and abs(float(P3.BEAST_F) - 1.0) < 1e-12, "LIVE60 SkillCfg.load of the migrated copy: Beastmastery in catch-up, factor 1")
    planned = set(["catchup.skills", "beast.xpFactor"])
    other = sorted(k for k in set(before) | set(after) if after.get(k) != before.get(k) and k not in planned)
    K.check(not other, "LIVE60 only the planned keys changed: %s" % other[:12])
    txt = open(xp, encoding="latin-1").read()
    K.check(txt.count(MARK_ID) == 1 and txt.count("\ncatchup.skills=") == 1, "LIVE60 the marker once, one catch-up line")
    cl = s1.get("config-changes.log", b"").decode("utf-8", "replace")
    K.check(cl.count("\tSkyySkills 0.4.60\t") == 2 and "catchup.skills" in cl and "beast.xpFactor" in cl, "LIVE60 two change-log rows (Undo in Server Setup -> Changes)")
    K.check(any(b"Balance P8c" not in open(os.path.join(r_, f_), "rb").read() and b"Balance P8 rebirth" in open(os.path.join(r_, f_), "rb").read()
                for r_, _d, fs in os.walk(os.path.join(lc, "config-history")) for f_ in fs), "LIVE60 config-history holds the pre-P8c xp.properties")
    # every live player file: Beastmastery 0, nothing owed; the next save adds exactly Beastmastery=0 + Beastmastery.paid=0
    pd = os.path.join(lc, "players")
    bad, n = [], 0
    UUID = JClass("java.util.UUID")
    for fn in sorted(os.listdir(pd)):
        if not fn.endswith(".properties"):
            continue
        n += 1
        kk = fn[:-11]
        u = UUID.fromString(kk[:36])
        old = _props(open(os.path.join(pd, fn), "rb").read())
        got = Sto.readFile(kk, u)
        dd = got[0]
        if int(dd[20]) != 0 or int(dd[int(SD.N) + 20]) != 0 or "Beastmastery" in old:
            bad.append((fn, int(dd[20]), int(dd[int(SD.N) + 20])))
            continue
        Sto.install(kk, u, got)
        sp = Sto.snap(kk)
        new = dict((str(x), str(sp.getProperty(x))) for x in sp.stringPropertyNames())
        added = sorted(set(new) - set(old))
        changed = sorted(x for x in set(old) & set(new) if old[x] != new[x])
        if "Beastmastery" not in added or "Beastmastery.paid" not in added or new["Beastmastery"] != "0" or new["Beastmastery.paid"] != "0" or changed:
            bad.append((fn, added, changed[:5]))
    K.check(n >= 1 and not bad, "LIVE60 %d live profile file(s): Beastmastery starts at 0 XP (nothing owed); a save adds only Beastmastery=0 + .paid=0: %s" % (n, bad[:3]))
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(all(s1.get(x) == s2.get(x) for x in set(s1) | set(s2)) and r2["BmMigP8c"] == "", "LIVE60 start 2 changes nothing")
    K.save()


def run_pair(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, PETS_JAR, TREES_JAR], verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    bad, n = [], 0
    for j in (jar, PETS_JAR, TREES_JAR):
        for c in HK.jar_classes(j):
            try:
                Cls.forName(c, True, loader)
                n += 1
            except Exception as e:
                bad.append((os.path.basename(j), c, str(e)[:120]))
    K.check(not bad and n > 250, "PAIR the three jars' classes load + initialise together with -Xverify:all (%d classes): %s" % (n, bad[:3]))
    J = lambda nm: JClass(PKG + nm)
    J("SkillCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    T57.fresh_load(J, J("SkillCfg"), os.path.join(scratch, "pair", "sk"))
    SD, ST = J("SkillDefs"), J("SkillStore")
    K.check(ST.bridge() is br or ST.bridge().equals(br), "PAIR SkyySkills uses the shared skyy.bridge map")
    br.put("skill:fn:level", J("SkillFn")())
    br.put("skill:fn:addxp", J("SkillAddFn")())
    N = int(SD.N)
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000060020")
    k = str(ST.pkey(u))
    cum = [sum(int(x) for x in list(SD.PER)[:L]) for L in range(101)]
    d = JArray(JClass("long"))(2 * N)
    d[20] = cum[12] + 5
    ST.DATA.put(k, d)
    # SkyyTrees: the Beastmastery tree's points = SkyySkills' real Beastmastery level
    V = JClass("com.skyy.trees.TreeV3")
    tv = [t for t in range(len(V.TNAME)) if str(V.TNAME[t]) == "Beastmastery"][0]
    K.check(int(V.level(u, tv)) == 12 and int(V.points(u, tv)) == 12, "PAIR SkyyTrees TreeV3.level of the Beastmastery tree = SkyySkills' skill:fn:level (12): %s" % V.level(u, tv))
    # SkyyPets: PetBm -> SkyySkills' real skill:fn:addxp (an offline player is refused there)
    PB = JClass("com.skyy.pets.PetBm")
    PS = JClass("com.skyy.pets.PetStore")
    r0 = int(PB.REFUSED.get())
    sent = int(PB.add(u, 7.5))
    K.check(sent == 0 and int(PB.REFUSED.get()) == r0 + 7, "PAIR PetBm -> SkillAddFn.apply {UUID, Beastmastery, 7, pets, key}: an offline player is refused (FALSE), no exception (%d refused)" % (int(PB.REFUSED.get()) - r0))
    K.save()


# checked by hand 2026-10-22: the planned members + every method that reads SkillDefs.N (a static final int = 21 now, inlined by the compiler
# as a constant: bipush 20 -> 21, N + 1 21 -> 22, 2 x N 40 -> 42) - the NF phase proves those differ ONLY in that constant
EXPECT.update({'BridgeCfg': ['~m read'], 'BridgeTask': ['~m run'], 'BridgeXp': ['~m grantSlot', '~m offerX', '~m paidY'], 'CfgFile': ['~<clinit>'],
               'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'ClassMana': ['~m amountFor'], 'ClassPower': ['~m boostRegen', '~m classLevel'],
               'CurveP3Mig': ['~m guard', '~m remapFile', '~m remapFloors', '~m run', '~m tables'], 'Fell': ['~m end'], 'GatherPace': ['~m read'],
               'LvFloor': ['~m scanText'], 'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'], 'ManaRegen': ['~m classPct'],
               'Overall': ['~m listText', '~m maxLevel', '~m sums'], 'OverallCfg': ['~m exactSlot'], 'OwnCurve': ['~m deliver', '~m moves', '~m start'],
               'P3Mig': ['~<clinit>'], 'P3Xp': ['+f BEAST_F', '+m beastBase', '~<clinit>', '~m bonusP8', '~m flags', '~m lvl', '~m mult', '~m rbLine', '~m rbRaw',
                                                '~m rbSrc', '~m read', '~m slotOf', '~m stats', '~m text'],
               'PartyXp': ['~m add', '~m note', '~m routed', '~m text'], 'RbStat': ['~m skip'], 'SkillBonus': ['~m treeAvailable', '~m treeName'],
               'SkillCap': ['~m cap', '~m capT', '~m extra', '~m fetch', '~m level', '~m lvD', '~m lvK'], 'SkillCfg': ['~m load'],
               'SkillClass': ['~m argSlot', '~m skillName'], 'SkillDefs': ['+f BEASTMASTERY', '~<clinit>', '~m rebirthResets', '~m setOwn'],
               'SkillKit': ['~m checkSkills'], 'SkillLv': ['~m checkEntry', '~m parseTable', '~m slotOf'], 'SkillMsg': ['~m note', '~m takeArr'],
               'SkillRb': ['~<clinit>', '~m commit', '~m facts'], 'SkillRunFn': ['~m apply'],
               'SkillStore': ['~m level', '~m moveLegacy', '~m owesK', '~m payLocked', '~m rbReset0', '~m readFile', '~m seedTop', '~m snap', '~m topPut'],
               'SkillTop': ['~<clinit>'], 'SkillXp': ['~m gain4', '~m petXp'], 'SkillsPage': ['~m build', '~m handleDataEvent', '~m subRow'],
               'SkyySkillsPlugin': ['~m setup'], 'StatsCmd': ['~c '], 'StatsPage': ['~m build', '~m how', '~m lines0'], 'TopCmd': ['~c '], 'XpCmd': ['~c ']})
# the members this round changes on purpose (code / texts); every OTHER changed method must differ only by the inlined N
NF_PLANNED = {"BridgeCfg.read", "BridgeTask.run", "BridgeXp.offerX", "BridgeXp.paidY", "P3Xp.bonusP8", "P3Xp.rbSrc", "P3Xp.read", "RbStat.skip",
              "SkillBonus.treeName", "SkillXp.petXp", "StatsPage.how", "StatsPage.lines0", "SkyySkillsPlugin.setup", "SkillCfg.load", "CurveP3Mig.run",
              "CfgFn.opExport", "CfgRows.header", "ManaGuard.armReport2", "ManaGuard.intReport", "ManaGuard.packReport", "SkillClass.argSlot",
              "SkillLv.checkEntry", "StatsCmd.StatsCmd", "TopCmd.TopCmd", "XpCmd.XpCmd"}
NF_PAIRS = {("bipush 20", "bipush 21"), ("bipush 21", "bipush 22"), ("bipush 40", "bipush 42")}


def run_nfold(out, jar, scratch, _home):
    import re, zipfile
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc, IP = JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter")

    def pool(j):
        p = CPc(False)
        p.appendSystemPath()
        p.appendClassPath(B.SERVER_JAR)
        p.appendClassPath(j)
        return p

    def code(b):
        mi = b.getMethodInfo()
        ca = mi.getCodeAttribute()
        if ca is None:
            return []
        it, cpl, o = ca.iterator(), mi.getConstPool(), []
        while it.hasNext():
            pos = it.next()
            ln = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cpl))))
            o.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln))
        return o
    pa, pb = pool(OLD_JAR), pool(jar)
    nonly, odd = 0, []
    for cn in HK.jar_classes(jar):
        try:
            ca = pa.get(cn)
        except Exception:
            continue
        cb = pb.get(cn)
        for m, kind in [(m, "m") for m in cb.getDeclaredMethods()] + [(m, "c") for m in cb.getDeclaredConstructors()]:
            key = cn.split(".")[-1] + "." + str(m.getName())
            try:
                mo = ca.getMethod(m.getName(), m.getSignature()) if kind == "m" else ca.getConstructor(m.getSignature())
            except Exception:
                continue
            a, b = code(mo), code(m)
            if a == b or key in NF_PLANNED:
                continue
            if len(a) == len(b) and all(x == y or (x, y) in NF_PAIRS for x, y in zip(a, b)):
                nonly += 1
            else:
                odd.append(key)
    K.check(nonly > 40 and not odd, "NF %d changed methods outside the planned ones differ ONLY by the inlined SkillDefs.N (20 -> 21, N + 1, 2 x N): other %s" % (nonly, sorted(set(odd))))
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("nfold", run_nfold), ("bm", run_bm), ("skip", run_skip), ("pm", run_pm), ("live60", run_live60), ("pair", run_pair)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
