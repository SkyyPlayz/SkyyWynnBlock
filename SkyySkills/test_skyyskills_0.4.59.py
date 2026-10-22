"""SkyySkills 0.4.59 - harness for BALANCE PASS P8a (research/Balance-P8-Rebirth-Spec.md 5.4; tools/skills_0_4_59_patch.py; tools/balance_rebirth.py).
Build first: python tools/skills_0_4_59_patch.py && python SkyySkills/build_skyyskills_0.4.59.py

    python SkyySkills/test_skyyskills_0.4.59.py [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S   static   the patch re-runs to identical bytes, line endings kept, setup order P4Mig -> PlMigP8 -> SkillCfg.load, one new class
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.58 -> 0.4.59: + PlMigP8; only the planned members differ
  P8  EXECUTED: the fresh file's list = balance_rebirth.PAST_LIFE_P8; pastLife for rebirth 1..12 (11-12 = 2.7) with the last run's cap
      50/60/70/80/90/100/100...; Exploration never; RbStat class XP 300 % -> 3.0 (no longer 2.0), 700 % -> 5.0, Health / Mana % still 200;
      cutRb (9.3 / 2.7 / 3.0 -> 2.444; 0 / NaN / negative = no cut); SkillBonus.xpBonus through the new body: ceiling off = the 0.4.58 sum,
      on = the rebirth part cut, the tree part never cut, a skill outside bridge.bonus.xpSkills, a class slot; the Stats line (combined, at the
      ceiling); the Server Setup row (default 0, 0-100, help); P3Xp.read of rebirth.xpMultMax (0 / 9.3 / -1 / NaN / 500)
  P4  the whole 0.4.58 P4 phase against the 0.4.59 jar (class stats, Mana timing - unchanged)
  PM  PlMigP8.plan / sameAfter: the 0.4.58 jar's default file -> exactly the 0.4.59 one; a hand-edited list kept + noted; no line = nothing
      rewritten (only the row + marker); a half-migrated file (row present, no marker); CRLF; the marker once; the change-log row carries the
      exact old line (Undo)
  LIVE59  every one-time update in setup() order (0.4.58's list + PlMigP8) on a scratch COPY of the live data + SkillCfg.load, started TWICE
  PAIR  SkyySkills 0.4.59 + SkyyRebirth 0.4.2 in ONE JVM: SkyyRebirth's real rebirth:fn:stat for a profile holding 1000 VP + Insight 5 + Class
      Echo 5 (338 %) -> SkyySkills RbStat class part 3.38 (0.4.58 stopped at 2.0) -> xpBonus of a class slot 3.38; the ceiling 9.3 at
      past-life 2.7 cuts it to 2.444
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, shutil, subprocess, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import balance_rebirth as BR


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp8a", "sk")]
T58 = _mod("test_skyyskills_0.4.58.py", "test_skyyskills_0_4_58")
T57 = T58.T57
T48, T53 = T57.T48, T57.T53
VERSION = "0.4.59"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.58.py")
PATCH = os.path.join(TOOLS, "skills_0_4_59_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.58.jar")
RB_JAR = os.path.join(ROOT, "SkyyRebirth", "SkyyRebirth-0.4.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T58.LIVE_DIR
T58.JAR, T58.VERSION = JAR, VERSION
ADDED = ["PlMigP8"]
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "CurveP3Mig": ["~m run"],   # the inlined fresh default file (+ the P8 block, the P8 list in P3's block)
          "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],   # the version in its report texts
          "P3Xp": ["+f XP_MULT_MAX", "+m bonusP8", "+m cutRb", "+m rbLine", "+m rbRaw", "+m rbSrc", "~<clinit>", "~m checkPast", "~m read", "~m stats"],
          "P3Mig": ["~<clinit>"],   # its ADDV: rebirth.pastLifeXp = the P8 list
          "RbStat": ["+f CLASSXP_MAX", "+m clampClass", "~m fetch"], "SkillBonus": ["~m xpBonus"],
          "SkillCfg": ["~m load"], "SkyySkillsPlugin": ["~m setup"]}
P8_PAST = BR.PAST_LIFE_P8
OLD_LIST = "1.2,1.45,1.8,2.25,2.8"
NEW_LIST = "1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7"
old_defaults, _props = T58.old_defaults, T58._props


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
    K.check(g.startswith('"""SkyySkills 0.4.59 - build script') and g.count('VERSION = "0.4.59"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 1 and ", cst, p4m, plm8, lvf," in g, "S one new class (PlMigP8), written out")
    su = g[g.index("{PKG}.CurveP3Mig.run(base)"):]
    K.check(su.index("P3Mig.run()") < su.index("{PKG}.P4Mig.run();") < su.index("{PKG}.PlMigP8.run();") < su.index("SkillCfg.load"),
            "S setup: the P3 updates -> P4Mig -> PlMigP8 -> SkillCfg.load")
    K.check(g.index('sbn.getDeclaredMethod("xpBonus").setBody(') > g.index("public static double bonusP8(") > g.index("public static double pastLife("),
            "S xpBonus gets its body after P3Xp.pastLife / bonusP8 exist")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_p8(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = T57.boot(K)
    T57.fresh_load(J, Cfg, os.path.join(scratch, "p8"))
    SD, ST, P3, SB, RB, SC, V3 = J("SkillDefs"), J("SkillStore"), J("P3Xp"), J("SkillBonus"), J("RbStat"), J("SkillCap"), J("SkillV3")
    br = ST.bridge()
    N = int(SD.N)
    D = str(Cfg.DEFAULTS)
    dp = _props(D)
    K.eq(dp.get("rebirth.pastLifeXp"), NEW_LIST, "P8 the fresh file: rebirth.pastLifeXp = the P8 list")
    K.eq(dp.get("rebirth.xpMultMax"), "0", "P8 the fresh file: rebirth.xpMultMax=0 (off)")
    K.check(D.count("Balance P8 rebirth (SkyySkills 0.4.59)") == 1 and D.count("\nrebirth.pastLifeXp=") == 1, "P8 the fresh file: the marker once, one list line")
    K.eq([float(x) for x in P3.PAST], P8_PAST, "P8 P3Xp.PAST = balance_rebirth.PAST_LIFE_P8")
    K.eq(str(P3.DEF_PAST), NEW_LIST, "P8 the code default (a file without the line)")
    K.check(float(P3.XP_MULT_MAX) == 0.0, "P8 the ceiling is off on a fresh file")
    _cp = str(P3.checkPast("rebirth.pastLifeXp", "x,y"))   # fix round 2
    K.check(NEW_LIST in _cp and "1.2,1.45" not in _cp and P3.checkPast("rebirth.pastLifeXp", NEW_LIST) is None,
            "P8 FIX2 the row's error message gives the P8 list as its example (and the P8 list itself passes): %r" % _cp)
    cum = [sum(int(x) for x in list(SD.PER)[:L]) for L in range(101)]
    ARCH, MIN, EXP, FISH = int(SD.indexOf("Archer")), int(SD.MINING), int(SD.EXPLORATION), int(SD.FISHING)
    u = T57._uuid(59001)
    k = str(u)
    d = JArray(JClass("long"))(2 * N)
    for s, L in ((ARCH, 30), (MIN, 20), (EXP, 5), (FISH, 10)):
        d[s] = cum[L] + 1
    ST.DATA.put(k, d)
    br.put("class:" + k, "Archer")
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
    got = []
    for n in range(0, 13):
        at(n)
        got.append((n, int(P3.prevCap(k, MIN, n)), float(P3.pastLife(u, MIN)), float(P3.pastLife(u, ARCH)), float(P3.pastLife(u, EXP))))
    K.eq([g[1] for g in got], [0, 50, 60, 70, 80, 90, 100, 100, 100, 100, 100, 100, 100], "P8 the last run's cap by rebirth 0..12 (6+: the 100 clamp)")
    K.eq([g[2] for g in got], [1.0] + P8_PAST + [2.7, 2.7], "P8 past-life on Mining 20 by rebirth 0..12 (11-12 = the last entry 2.7)")
    K.eq([g[3] for g in got], [1.0] + P8_PAST + [2.7, 2.7], "P8 past-life on the class (Archer 30) the same list")
    K.check(all(g[4] == 1.0 for g in got), "P8 Exploration never gets the past-life boost")
    # ---- RbStat: the class XP part up to 500 %, the stats still 200
    D_ = JClass("java.lang.Double")
    STV = {"all": 3.0, "health": 0.0, "mana": 0.0, "classxp": 300.0, "combatxp": 0.0, "allxp": 0.0}

    @JImplements("java.util.function.Function")
    class Stat(object):
        @JOverride
        def apply(self, a):
            return D_.valueOf(STV.get(str(a[1]), 0.0))
    br.put("rebirth:fn:stat", Stat())
    RB.refresh(u)
    K.check(abs(float(RB.classXp(u)) - 3.0) < 1e-9, "P8 RbStat: class XP 300 %% -> 3.0 (0.4.58 clamped it at 2.0): %s" % RB.classXp(u))
    STV.update(classxp=700.0, all=250.0, health=10.0)
    RB.refresh(u)
    v = list(RB.cached(u, ST.pkey(u)))
    K.check(abs(float(RB.classXp(u)) - 5.0) < 1e-9 and float(v[0]) == 200.0 and float(v[1]) == 200.0 and float(v[2]) == 200.0,
            "P8 RbStat: class XP 700 %% -> 5.0 (the new +500 %% limit); Health / Mana / Stamina %% still clamp at 200: %s" % v[:4])
    K.check(float(RB.MAXPCT) == 200.0 and float(RB.CLASSXP_MAX) == 500.0 and float(RB.clampClass(float("nan"))) == 0.0 and float(RB.clampClass(-5.0)) == 0.0,
            "P8 MAXPCT stays 200, CLASSXP_MAX 500; NaN / negative = 0")
    STV.update(classxp=300.0, all=3.0, health=0.0)
    RB.refresh(u)
    # ---- cutRb (spec 5.4 check 3)
    K.check(abs(float(P3.cutRb(3.0, 2.7, 9.3)) - (9.3 / 2.7 - 1.0)) < 1e-12 and abs(float(P3.cutRb(3.0, 2.7, 9.3)) - 2.444) < 0.001,
            "P8 cutRb: past-life 2.7 x rb 3.0 at the ceiling 9.3 -> rb' = %.4f" % float(P3.cutRb(3.0, 2.7, 9.3)))
    K.check(float(P3.cutRb(3.0, 2.7, 0.0)) == 3.0 and float(P3.cutRb(3.0, 2.7, float("nan"))) == 3.0 and float(P3.cutRb(3.0, 2.7, -1.0)) == 3.0,
            "P8 cutRb: ceiling 0 / NaN / negative = no cut")
    K.check(float(P3.cutRb(1.0, 2.7, 9.3)) == 1.0 and float(P3.cutRb(3.0, 12.0, 9.3)) == 0.0 and float(P3.cutRb(3.0, 1.0, 2.0)) == 1.0
            and float(P3.cutRb(-1.0, 2.0, 9.3)) == 0.0 and float(P3.cutRb(float("nan"), 2.0, 9.3)) == 0.0,
            "P8 cutRb: under the ceiling untouched; past-life above the ceiling = rb 0 (never below 0); no past-life = ceiling - 1")
    # ---- xpBonus through the new body
    HM = JClass("java.util.HashMap")
    src, rb, tr = HM(), HM(), HM()
    for kk, vv in (("xp.mining", 2.0), ("xp.fishing", 1.5)):
        rb.put(kk, D_.valueOf(vv))
    for kk, vv in (("xp.mining", 0.25), ("xp.fishing", 0.7), ("xp.combat", 0.04)):
        tr.put(kk, D_.valueOf(vv))
    src.put("rebirth", rb)
    src.put("trees", tr)
    br.put("skill:bonus:" + k, src)
    at(9)   # rebirth 9: past-life 2.55 below Lv 100 (Mining 20, Archer 30)
    pl9 = float(P3.pastLife(u, MIN))
    K.check(pl9 == 2.55, "P8 rebirth 9 past-life 2.55")
    P3.XP_MULT_MAX = 0.0
    K.check(abs(float(SB.xpBonus(u, MIN)) - 2.25) < 1e-9, "P8 xpBonus Mining, ceiling off: every source as 0.4.58 (2.0 + 0.25)")
    K.check(abs(float(SB.xpBonus(u, FISH)) - 1.5) < 1e-9, "P8 xpBonus Fishing (not in xpSkills), off: the rebirth source only")
    K.check(abs(float(SB.xpBonus(u, ARCH)) - (3.0 + 0.04)) < 1e-9, "P8 xpBonus Archer, off: RbStat 3.0 (no 2.0 clamp) + the tree's xp.combat 0.04: %s" % SB.xpBonus(u, ARCH))
    K.check(float(SB.xpBonus(u, EXP)) == 0.0, "P8 xpBonus Exploration 0")
    P3.XP_MULT_MAX = 6.0
    cut = 6.0 / 2.55 - 1.0
    K.check(abs(float(SB.xpBonus(u, MIN)) - (cut + 0.25)) < 1e-9, "P8 ceiling 6: Mining rebirth part 2.0 -> %.4f, the tree 0.25 never cut: %s" % (cut, SB.xpBonus(u, MIN)))
    K.check(abs(float(SB.xpBonus(u, FISH)) - min(1.5, cut)) < 1e-9, "P8 ceiling 6: Fishing (rebirth source only) 1.5 -> %.4f" % min(1.5, cut))
    K.check(abs(float(SB.xpBonus(u, ARCH)) - (cut + 0.04)) < 1e-9, "P8 ceiling 6: Archer class part 3.0 -> %.4f + tree 0.04" % cut)
    K.check(abs(pl9 * (1.0 + float(SB.xpBonus(u, MIN)) - 0.25) - 6.0) < 1e-9, "P8 ceiling 6: past-life x (1 + rebirth part) = exactly 6")
    P3.XP_MULT_MAX = 20.0
    K.check(abs(float(SB.xpBonus(u, MIN)) - 2.25) < 1e-9, "P8 ceiling 20 (above today's x7.6): no cut")
    # ---- the Stats line
    P3.XP_MULT_MAX = 0.0
    sl = str(P3.rbLine(u, MIN))
    K.eq(sl, "Rebirth XP x7.7: past-life x2.55 below Lv 100, Void x3", "P8 the combined Stats line (2.55 x 3 = 7.65)")
    lines = [str(x) for x in J("StatsPage").lines(u, MIN, 20, False)]
    K.check(any(x == sl for x in lines) and not any(x.startswith("Past-life XP") for x in lines), "P8 the Stats page carries it (the old line gone): %s" % lines[-3:])
    P3.XP_MULT_MAX = 6.0
    K.eq(str(P3.rbLine(u, MIN)), "Rebirth XP x6: past-life x2.55 below Lv 100, Void x2.35, at the server's fastest rebirth", "P8 the Stats line at the ceiling")
    P3.XP_MULT_MAX = 0.0
    at(0)
    K.check(P3.rbLine(u, MIN) is not None and str(P3.rbLine(u, MIN)) == "Rebirth XP x3: Void x3", "P8 rebirth 0 with VP-style rebirth XP only: %s" % P3.rbLine(u, MIN))
    br.remove("skill:bonus:" + k)
    STV.update(classxp=0.0)
    RB.refresh(u)
    K.check(P3.rbLine(u, MIN) is None and P3.rbLine(u, ARCH) is None, "P8 no rebirth boost at all = no line")
    # ---- the row + P3Xp.read
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in J("CfgRows").header()[7])
    r_ = rows.get("rebirth.xpMultMax")
    K.check(r_ is not None and r_[2] == "levels" and r_[3] == "dec" and r_[4] == "0" and r_[5] == "0" and r_[6] == "100" and "9.3" in r_[10] and len(r_[10]) <= 100,
            "P8 Server Setup row Skills -> Levels: Fastest rebirth (dec 0-100, default 0, help names 9.3): %s" % r_)
    K.eq(rows.get("rebirth.pastLifeXp", [None] * 5)[4], NEW_LIST, "P8 the past-life row's default = the P8 list")
    Props = JClass("java.util.Properties")
    for txt, want in (("rebirth.xpMultMax=9.3\n", 9.3), ("rebirth.xpMultMax=-1\n", 0.0), ("rebirth.xpMultMax=abc\n", 0.0), ("rebirth.xpMultMax=500\n", 100.0), ("", 0.0)):
        p = Props()
        p.load(JClass("java.io.StringReader")(txt))
        P3.read(p)
        K.check(abs(float(P3.XP_MULT_MAX) - want) < 1e-9, "P8 P3Xp.read %r -> %s" % (txt.strip(), want))
    K.eq([float(x) for x in P3.PAST], P8_PAST, "P8 no line = the P8 list")
    K.save()


def run_pm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    M, Cfg = JClass(PKG + "PlMigP8"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = _old_defaults()
    NEW = str(Cfg.DEFAULTS)
    K.check(("\nrebirth.pastLifeXp=" + OLD_LIST + "\n") in OLD and "Balance P4 combat (SkyySkills 0.4.58)" in OLD, "PM the 0.4.58 jar's file holds the old list")
    r = M.plan(JString(OLD))
    K.check(r is not None and _props(str(r[0])) == _props(NEW), "PM the 0.4.58 jar's default file -> exactly the 0.4.59 one (Properties)")
    rows = [str(x) for x in r[1]]
    K.eq(rows, ["rebirth.pastLifeXp", OLD_LIST, NEW_LIST, "rebirth.xpMultMax", "(none)", "0"], "PM change-log rows: the list moved (old line exact = Undo) + the row added")
    K.check(bool(M.sameAfter(JString(OLD).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r)), "PM sameAfter: only the planned keys differ")
    nb = str(r[0])
    K.check(nb.replace("\nrebirth.pastLifeXp=" + NEW_LIST + "\n", "\nrebirth.pastLifeXp=" + OLD_LIST + "\n", 1).startswith(OLD) and nb.endswith("# Balance P8 rebirth (SkyySkills 0.4.59): the past-life XP list for rebirths 1-10 and the fastest-rebirth ceiling (off)\n"),
            "PM bytes: only the value text changed, the block appended, the marker last")
    K.check(M.plan(r[0]) is None and M.plan(JString(NEW)) is None, "PM the marker: a second plan / a fresh file = null")
    hand = OLD.replace("\nrebirth.pastLifeXp=" + OLD_LIST + "\n", "\nrebirth.pastLifeXp=1.5,2,3\n")
    rh = M.plan(JString(hand))
    ph = _props(str(rh[0]))
    K.check(ph["rebirth.pastLifeXp"] == "1.5,2,3" and "rebirth.pastLifeXp=1.5,2,3 kept" in str(rh[3]) and ph["rebirth.xpMultMax"] == "0" and [str(x) for x in rh[1]] == ["rebirth.xpMultMax", "(none)", "0"],
            "PM a hand-edited list kept + noted, only the row added: %s" % str(rh[3])[:160])
    nol = OLD.replace("\nrebirth.pastLifeXp=" + OLD_LIST + "\n", "\n")
    rn = M.plan(JString(nol))
    pn = _props(str(rn[0]))
    K.check("rebirth.pastLifeXp" not in pn and pn["rebirth.xpMultMax"] == "0" and str(rn[3]) == "", "PM no list line = nothing written for it (the new code default applies)")
    half = OLD + "rebirth.xpMultMax=4\n"
    rf = M.plan(JString(half))
    pf = _props(str(rf[0]))
    K.check(pf["rebirth.xpMultMax"] == "4" and pf["rebirth.pastLifeXp"] == NEW_LIST and str(rf[0]).count("rebirth.xpMultMax=") == 1 and str(rf[0]).rstrip("\n").endswith("(off)"),
            "PM half-migrated (the row already there, no marker): the row kept, the list moved, the marker last")
    multi = OLD.replace("\nrebirth.pastLifeXp=" + OLD_LIST + "\n", "\nrebirth.pastLifeXp=1.2,1.45,\\\n  1.8,2.25,2.8\n")
    rm = M.plan(JString(multi))
    K.check(_props(str(rm[0]))["rebirth.pastLifeXp"] == OLD_LIST and "kept" in str(rm[3]), "PM a continued (multi-line) list = an admin's: kept")
    crlf = OLD.replace("\n", "\r\n")
    rc = M.plan(JString(crlf))
    K.check(_props(str(rc[0])) == _props(NEW) and "\n" not in str(rc[0]).replace("\r\n", ""), "PM CRLF: same settings, every line ending CRLF")
    K.save()


def run_live59(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy59")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, M4, M8, P3 = (J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"),
                                                        J("CurveP3Mig"), J("P3Mig"), J("P4Mig"), J("PlMigP8"), J("P3Xp"))
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
        r["load"] = str(Cfg.load())
        return r
    s0 = T53.snapd(lc)
    before = _props(open(xp, encoding="latin-1").read())
    r1 = start()
    s1 = T53.snapd(lc)
    K.notes.append("LIVE59 start 1: P3Mig %s | PlMigP8: %s" % (r1["P3Mig"][:120], r1["PlMigP8"][:200]))
    K.check("updated for 0.4.59" in r1["PlMigP8"], "LIVE59 start 1: PlMigP8 ran: %s" % r1["PlMigP8"][:160])
    after = _props(open(xp, encoding="latin-1").read())
    K.eq((after.get("rebirth.pastLifeXp"), after.get("rebirth.xpMultMax")), (NEW_LIST, "0"), "LIVE59 the live copy holds the P8 list + the ceiling row (off)")
    K.eq([float(x) for x in P3.PAST], P8_PAST, "LIVE59 SkillCfg.load of the migrated copy: P3Xp.PAST = the P8 list")
    K.check(float(P3.XP_MULT_MAX) == 0.0, "LIVE59 the ceiling is off")
    planned = set(str(k) for k in M8.KEYS) | set(str(k) for k in M8.ADDK) | set(str(k) for k in M4.KEYS) | set(str(k) for k in M4.ADDK) | \
        set(str(k) for k in M.KEYS) | set(str(k) for k in M.ADDK) | set(["bridge.bonus.xpSkills"])
    other = sorted(k for k in set(before) | set(after) if after.get(k) != before.get(k) and k not in planned)
    K.check(not other, "LIVE59 only the P3 / P4 / P8 planned keys changed: %s" % other[:12])
    txt = open(xp, encoding="latin-1").read()
    K.check(txt.count("Balance P8 rebirth (SkyySkills 0.4.59)") == 1 and txt.count("\nrebirth.pastLifeXp=") == 1, "LIVE59 the marker once, one list line")
    cl = s1.get("config-changes.log", b"").decode("utf-8", "replace")
    n8 = cl.count("\tSkyySkills 0.4.59\t")
    K.check(n8 >= 1 and "rebirth.xpMultMax" in cl, "LIVE59 change-log rows for the P8 update (%d; the live file got the P8 list from P3Mig directly)" % n8)
    K.check(any(b"Balance P8" not in open(os.path.join(r_, f_), "rb").read() and b"Balance P4" in open(os.path.join(r_, f_), "rb").read()
                for r_, _d, fs in os.walk(os.path.join(lc, "config-history")) for f_ in fs), "LIVE59 config-history holds the pre-P8 xp.properties")
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2["PlMigP8"] == "", "LIVE59 start 2 changes nothing")
    K.save()


def run_pair(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, RB_JAR], verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    bad, n = [], 0
    for j in (jar, RB_JAR):
        for c in HK.jar_classes(j):
            try:
                Cls.forName(c, True, loader)
                n += 1
            except Exception as e:
                bad.append((os.path.basename(j), c, str(e)[:120]))
    K.check(not bad and n > 150, "PAIR both jars' classes load + initialise together with -Xverify:all (%d classes): %s" % (n, bad[:3]))
    J = lambda nm: JClass(PKG + nm)
    R = lambda nm: JClass("com.skyy.rebirth." + nm)
    J("SkillCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    P_ = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "pair", "Skyy_SkyyRebirth")
    os.makedirs(os.path.join(home, "players"))
    RC, RS = R("RbCfg"), R("RbStore")
    RC.BRIDGE = br
    RC.DIR = P_.get(home)
    RC.FILE = P_.get(os.path.join(home, "config.properties"))
    RC.loadCfg(False)
    RS.DIR = P_.get(os.path.join(home, "players"))
    RS.IO = None
    T57.fresh_load(J, J("SkillCfg"), os.path.join(scratch, "pair", "sk"))
    u = T57._uuid(59002)
    k = str(u)
    open(os.path.join(home, "players", k + ".properties"), "w").write("n=9\nv=4\nvp=1000\nvpSpent=300\nnode.Void.insight=5\nnode.Class.echo=5\n")
    RS.CACHE.clear()
    br.put("rebirth:fn:stat", R("RbFn")(6))
    br.put("rebirth:fn:count", R("RbFn")(0))
    br.put("rebirth:fn:cap", R("RbFn")(1))
    O = JClass("java.lang.Object")
    cx = float(R("RbFn")(6).apply(JArray(O)([u, JClass("java.lang.String")("classxp")])))
    K.check(abs(cx - (250.0 + 52.0 + 36.0)) < 1e-9, "PAIR SkyyRebirth's rebirth:fn:stat classxp = keep 250 + Insight 52 + Class Echo 36 = %s %%" % cx)
    SD, ST, RB, SB, P3 = J("SkillDefs"), J("SkillStore"), J("RbStat"), J("SkillBonus"), J("P3Xp")
    N = int(SD.N)
    ARCH = int(SD.indexOf("Archer"))
    d = JArray(JClass("long"))(2 * N)
    ST.DATA.put(k, d)
    br.put("class:" + k, "Archer")
    RB.refresh(u)
    K.check(abs(float(RB.classXp(u)) - cx / 100.0) < 1e-9, "PAIR SkyySkills RbStat class part = %.2f (0.4.58 stopped at 2.0)" % float(RB.classXp(u)))
    K.check(abs(float(SB.xpBonus(u, ARCH)) - cx / 100.0) < 1e-9, "PAIR xpBonus of the class slot = %.2f (no tree ranks)" % float(SB.xpBonus(u, ARCH)))
    P3.XP_MULT_MAX = 9.3
    pl = float(P3.pastLife(u, ARCH))
    want = min(cx / 100.0, max(0.0, 9.3 / max(pl, 1.0) - 1.0))
    K.check(pl == 2.55, "PAIR SkyyRebirth's real count / cap: rebirth 9, the class at 0 < 100 -> past-life 2.55 (%s)" % pl)
    K.check(abs(float(SB.xpBonus(u, ARCH)) - want) < 1e-9, "PAIR the ceiling 9.3 at past-life %s cuts the class part to %.3f" % (pl, want))
    P3.XP_MULT_MAX = 0.0
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("p8", run_p8), ("p4", T58.run_p4), ("pm", run_pm), ("live59", run_live59), ("pair", run_pair)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
