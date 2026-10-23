"""SkyySkills 0.4.62 - harness for BALANCE PASS P9 FIXES F1-F4 (research/Balance-P9-Check.md; tools/skills_0_4_62_patch.py).
Build first: python tools/skills_0_4_62_patch.py && python SkyySkills/build_skyyskills_0.4.62.py

    python SkyySkills/test_skyyskills_0.4.62.py [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes, line endings kept, setup order SkMigP7 -> CurveP9Mig -> P9Mig -> after -> SkillCfg.load
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.61 -> 0.4.62: + P9Mig, CurveP9Mig; only the planned members differ
  DF   EXECUTED the new defaults: a fresh file loads the P9 list (DEFAULT_PER / RUN / P3, cumOf, curve-size row 120 %), XpEven / P3Xp code
       defaults on an empty file (Mining x1, felled logs 100 %, catch-up max 20 %, Beastmastery x1.5, the P9 past-life list), catch-up
       capped at +20 % on a real profile, beastBase x1.5, the past-life boost by rebirth 1..7, the Server Setup rows
  PM   P9Mig.plan / sameAfter: the 0.4.61 jar's default file -> exactly the 0.4.62 one (6 rows); hand-edited / not-exact / multi-line
       values kept + note; a missing line writes nothing; the marker = null; CRLF
  CM   CurveP9Mig on synthetic profiles: Lv 61-100 totals keep level + progress (rebirth caps 70 / 80 / 100 from a fake rebirth:fn:cap),
       below Lv 60 = byte-identical, XP past the cap 50 keeps its ratio, Exploration by level, a staged rebirth file, floors; History,
       curve-p9.log, run once; the P3 precondition (P3PEND / a pre-P3 file = nothing); P9PEND (file update failed -> load from memory);
       the guard (a pre-P9 xp.properties put back -> updated again, XP not moved twice); no xp.properties; CurveP3Mig's no-file tables
  LIVE62 every one-time update in setup() order on a scratch COPY of the live data + SkillCfg.load, started TWICE
  HUD62 (fix round, critic: the pre-P3 chain was never run) the same on a scratch COPY of the "HUD mod" world's Skyy_SkyySkills (an old
       pre-0.4.57 xp.properties) + one synthetic profile above Lv 60 (Mining 70 + 30 %, Archer 85 + 50 %, Foraging 62, rebirth cap 90):
       ONE start ends on the P9 list, every slot keeps its level (+ progress), one curve-p3 + one curve-p9 marker / History; start 2 = nothing
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
import balance_model as BM


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "p9fixfix2", "sk")]
T61 = _mod(os.path.join(HERE, "test_skyyskills_0.4.61.py"), "test_skyyskills_0_4_61")
T58, T57, T48, T53 = T61.T58, T61.T57, T61.T48, T61.T53
VERSION = "0.4.62"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.61.py")
PATCH = os.path.join(TOOLS, "skills_0_4_62_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.61.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T58.LIVE_DIR
ADDED = ["P9Mig", "CurveP9Mig"]
EXPECT = {}   # filled in below (checked by hand)
MARK_ID = "Balance P9 first-run fixes (SkyySkills 0.4.62)"
P9_PAST = [1.1, 1.52, 2.05, 3.35, 4.92, 2.92, 3.08, 3.25, 3.44, 3.67]
P8_PAST_T = "1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7"
P9_PAST_T = "1.1,1.52,2.05,3.35,4.92,2.92,3.08,3.25,3.44,3.67"
P3_T = ",".join(str(x) for x in BM.P3_LEVELS)
P9_T = ",".join(str(x) for x in BM.P9_LEVELS)
KEYS = [("beast.xpFactor", "1", "1.5"), ("mining.xpMultiplier", "1.25", "1"), ("fell.otherLogsPercent", "70", "100"), ("catchup.max", "100", "20"),
        ("levels", P3_T, P9_T), ("rebirth.pastLifeXp", P8_PAST_T, P9_PAST_T)]
CUM3 = [sum(BM.P3_LEVELS[:L]) for L in range(101)]
CUM9 = [sum(BM.P9_LEVELS[:L]) for L in range(101)]
ZERO_SLOTS = T61.ZERO_SLOTS
_props = T58._props
jpath = T48.jpath


def lvl(c, x):
    L = 0
    while L + 1 < len(c) and x >= c[L + 1]:
        L += 1
    return L


def _old_defaults():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "SkillCfg", loader=ld).DEFAULTS)


def _fn(f):
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.62 - build script') and g.count('VERSION = "0.4.62"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 2 and ", skm61, p9m62, cp962, lvf," in g, "S two new classes (P9Mig, CurveP9Mig), written out")
    su = g[g.index("{PKG}.CurveP3Mig.run(base)"):]
    K.check(su.index("{PKG}.SkMigP7.run();") < su.index("{PKG}.CurveP9Mig.run(base)") < su.index("{PKG}.P9Mig.run();") < su.index("{PKG}.CurveP9Mig.after(base)")
            < su.index("SkillCfg.load"), "S setup: SkMigP7 -> CurveP9Mig.run -> P9Mig.run -> CurveP9Mig.after -> SkillCfg.load")
    K.check("if ({PKG}.CurveP9Mig.run(base)) {{ {PKG}.P9Mig.run(); {PKG}.CurveP9Mig.after(base); }}" in g, "S P9Mig only after the saved XP moved (the P3 chain shape)")
    K.check(g.count("  if (r == null) { levelsUndone(txt); return 1; }") == 1 and g.index("public static boolean levelsUndone(String txt)") < g.index("public static int guard(java.nio.file.Path base", g.index("levelsUndone")),
            "S fix round: CurveP9Mig.guard WARNs (levelsUndone) when only the levels row was undone; the method comes before its caller")
    K.check(g.count("    P9STALE = p9stale();") == 1 and g.count("  if ({PKG}.SkillCfg.P9STALE) return new long[]") == 1
            and g.index("public static boolean p9stale()") < g.index("public static synchronized String load()") < g.index("public static long[] payLocked("),
            "S fix round 2: SkillCfg.load sets P9STALE; payLocked holds the coins while it is set; p9stale comes before load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_df(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = T57.boot(K)
    r0 = T57.fresh_load(J, Cfg, os.path.join(scratch, "df"))
    SD, ST, P3, SC, KIT, XE = J("SkillDefs"), J("SkillStore"), J("P3Xp"), J("SkillCap"), J("SkillKit"), J("XpEven")
    br = ST.bridge()
    N = int(SD.N)
    names = [str(x) for x in SD.NAMES]
    K.eq([int(x) for x in SD.DEFAULT_PER], BM.P9_BASE, "DF SkillDefs.DEFAULT_PER = the P9 base (P3 x1.5 Lv 61-80, x1.9 Lv 81-100)")
    K.eq([int(x) for x in SD.DEFAULT_RUN], BM.P9_LEVELS, "DF SkillDefs.DEFAULT_RUN = the P9 base x 120 %")
    K.eq([int(x) for x in SD.DEFAULT_P3], BM.P3_LEVELS, "DF SkillDefs.DEFAULT_P3 = the 0.4.57 - 0.4.61 list")
    K.eq([int(x) for x in SD.PER], BM.P9_LEVELS, "DF a fresh file loads the P9 list")
    ARCH, MIN, FOR, EXP, BEAST = int(SD.indexOf("Archer")), int(SD.MINING), int(SD.FORAGING), int(SD.EXPLORATION), int(SD.BEASTMASTERY)
    for s in (ARCH, MIN, FOR, EXP, BEAST):
        K.eq([int(SD.cumOf(s)[L]) for L in (20, 50, 60, 61, 80, 100)], [CUM9[L] for L in (20, 50, 60, 61, 80, 100)], "DF %s levels on the P9 list" % names[s])
    K.check(CUM9[60] == CUM3[60] and CUM9[100] > CUM3[100] and BM.P9_LEVELS[60] == round(BM.P3_BASE[60] * 1.5 * 1.2) and BM.P9_LEVELS[99] == round(BM.P3_BASE[99] * 1.9 * 1.2),
            "DF Lv 1-60 unchanged; Lv 61 needs %d (was %d), Lv 100 %d (was %d)" % (BM.P9_LEVELS[60], BM.P3_LEVELS[60], BM.P9_LEVELS[99], BM.P3_LEVELS[99]))
    K.eq(str(KIT.customGet("levels.scale")), "120", "DF Server Setup: the curve-size row still reads 120 % (the P9 base is its reference)")
    t = str(Cfg.DEFAULTS)
    K.check(all(("\n%s=%s\n" % (k, n)) in t and t.count("\n%s=" % k) == 1 for k, o, n in KEYS) and t.count(MARK_ID) == 1, "DF the fresh file: the 6 new values once each + the marker")
    # code defaults with no line
    Props = JClass("java.util.Properties")
    XE.read(Props())
    K.check(float(XE.MINE) == 1.0 and float(XE.FELL_PCT) == 100.0, "DF XpEven code defaults: Mining XP x1, other felled logs 100 %% (%s)" % XE.text())
    K.check(int(XE.mine(40)) == 40 and int(XE.fellLog(33.0)) == 33, "DF XpEven.mine(40) = 40, fellLog(33) = 33 (x1 / 100 %%)")
    P3.read(Props())
    K.check(abs(float(P3.CATCH_MAX) - 0.2) < 1e-12 and float(P3.BEAST_F) == 1.5 and [float(x) for x in P3.PAST] == P9_PAST and str(P3.DEF_PAST) == P9_PAST_T,
            "DF P3Xp code defaults: catch-up max 20 %%, Beastmastery x1.5, the P9 past-life list (%s)" % P3.loadText())
    K.check("1.1,1.52,2.05" in str(P3.checkPast("rebirth.pastLifeXp", "x")), "DF the past-life row's error message shows the P9 list")
    K.check(int(P3.beastBase(100)) == 150 and int(P3.beastBase(0)) == 0, "DF beastBase: 100 pet XP -> 150 Beastmastery XP")
    T57.fresh_load(J, Cfg, os.path.join(scratch, "df"))
    # catch-up on a real profile: Archer class 40, Mining 20 (gap 20 -> 10 % x 15 = 150 % -> capped 20 %), Mining 27 (gap 13 -> 80 % -> 20 %),
    # Mining 33 (gap 7 -> +20 %, at the cap), Mining 34 (gap 6 -> +10 %)
    u = T57._uuid(62001)
    k = str(u)
    d = JArray(JClass("long"))(2 * N)
    d[ARCH] = CUM9[40] + 1
    ST.DATA.put(k, d)
    br.put("class:" + k, "Archer")
    got = []
    for L in (20, 27, 33, 34, 35, 40):
        d[MIN] = CUM9[L] + 1
        got.append(round(float(P3.catchup(u, MIN)), 9))
    K.eq(got, [1.2, 1.2, 1.2, 1.1, 1.0, 1.0], "DF catch-up on Mining 20 / 27 / 33 / 34 / 35 / 40 behind an Archer 40: capped at +20 %")
    # the past-life boost by rebirth 1..7 (fake rebirth:fn:count + rebirth:fn:cap = base + 10 n), Mining 20 (below every last cap)
    NREB = {"n": 0}
    br.put("rebirth:fn:count", _fn(lambda a: JClass("java.lang.Integer").valueOf(NREB["n"])))
    br.put("rebirth:fn:cap", _fn(lambda a: a[2] if str(a[1]) == "Exploration" else JClass("java.lang.Integer").valueOf(int(a[2]) + 10 * NREB["n"])))
    d[MIN] = CUM9[20] + 1
    pl = []
    for n in range(0, 12):
        NREB["n"] = n
        P3.RBN.clear()
        SC.CACHE.clear()
        pl.append(round(float(P3.pastLife(u, MIN)), 9))
    K.eq(pl, [1.0] + P9_PAST + [P9_PAST[-1]], "DF past-life boost on Mining 20 by rebirth 0..11 = the P9 list (past the end: the last)")
    NREB["n"] = 0
    P3.RBN.clear()
    SC.CACHE.clear()
    rows_ = dict((str(r[0]), [str(x) for x in list(r)]) for r in J("CfgRows").header()[7])
    K.check([rows_[kk][4] for kk, o, n in KEYS] == [n for kk, o, n in KEYS], "DF Server Setup row defaults = the 6 new values")
    K.check("20 = at most +20%" in rows_["catchup.max"][10] and "P3" not in rows_["levels.scale"][10], "DF row help: catch-up max 20, the curve-size row")
    K.notes.append("DF load: %s" % str(r0)[:240])
    K.save()


def run_pm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    M, Cfg = JClass(PKG + "P9Mig"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = _old_defaults()
    NEW = str(Cfg.DEFAULTS)
    po, pn = _props(OLD), _props(NEW)
    K.check(all(po.get(k) == o and pn.get(k) == n for k, o, n in KEYS) and MARK_ID not in OLD, "PM the 0.4.61 jar's file holds the 6 old defaults; the 0.4.62 file the new")
    r = M.plan(JString(OLD))
    K.check(r is not None and _props(str(r[0])) == pn, "PM the 0.4.61 jar's default file -> exactly the 0.4.62 one (Properties)")
    K.eq(str(r[0]).replace("# SkyySkills 0.4.61 - XP rules.", "# SkyySkills 0.4.62 - XP rules.", 1), NEW,
         "PM ... byte for byte (values replaced in place, the block + marker appended; only the fresh file's version header differs)")
    rows = [str(x) for x in r[1]]
    K.eq([tuple(rows[i:i + 3]) for i in range(0, len(rows), 3)], [(k, o, n) for k, o, n in KEYS], "PM six change-log rows (old -> new; Undo)")
    K.check(bool(M.sameAfter(JString(OLD).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r)), "PM sameAfter: only the 6 keys differ")
    K.check(M.plan(r[0]) is None and M.plan(JString(NEW)) is None, "PM the marker: a second plan / a fresh file = null")
    hand = OLD.replace("\nbeast.xpFactor=1\n", "\nbeast.xpFactor=2\n").replace("\ncatchup.max=100\n", "\ncatchup.max = 100.0\n")
    rh = M.plan(JString(hand))
    ph = _props(str(rh[0]))
    K.check(ph["beast.xpFactor"] == "2" and ph["catchup.max"] == "100.0" and ph["levels"] == P9_T and "beast.xpFactor=2 kept" in str(rh[3]) and "catchup.max=100.0 kept" in str(rh[3])
            and len(list(rh[1])) == 12 and bool(M.sameAfter(JString(hand).getBytes("ISO-8859-1"), JString(str(rh[0])).getBytes("ISO-8859-1"), rh)),
            "PM an admin's beast.xpFactor 2 / a not-exact catchup.max 100.0 kept + note; the other 4 move: %s" % str(rh[3])[:160])
    nol = OLD.replace("\nmining.xpMultiplier=1.25\n", "\n").replace("\nfell.otherLogsPercent=70\n", "\n")
    rn = M.plan(JString(nol))
    K.check("mining.xpMultiplier" not in _props(str(rn[0])) and "fell.otherLogsPercent" not in _props(str(rn[0])) and len(list(rn[1])) == 12,
            "PM no mining / felled-log line (the live NewBetaTest file) -> nothing written for them (the new code default applies)")
    i = OLD.index("\nlevels=") + 1
    j = OLD.index("\n", i)
    cut = OLD[i:j].split(",")
    multi = OLD[:i] + ",".join(cut[:50]) + ",\\\n  " + ",".join(cut[50:]) + OLD[j:]
    K.eq(_props(multi)["levels"], P3_T, "PM (setup) a levels= split over two lines reads the old list")
    rm = M.plan(JString(multi))
    K.check(_props(str(rm[0]))["levels"] == P3_T and "levels=" in str(rm[3]), "PM a multi-line levels entry is kept (only one-line entries move) + note")
    crlf = OLD.replace("\n", "\r\n")
    rc = M.plan(JString(crlf))
    K.check(_props(str(rc[0])) == pn and "\n" not in str(rc[0]).replace("\r\n", ""), "PM CRLF: same settings, every line ending CRLF")
    K.save()


def run_cm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    C, M, C3, M3, Cfg, SD, ST, Hist, CLog, Rows = (J("CurveP9Mig"), J("P9Mig"), J("CurveP3Mig"), J("P3Mig"), J("SkillCfg"), J("SkillDefs"), J("SkillStore"),
                                                   J("CfgHist"), J("CfgLog"), J("CfgRows"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = _old_defaults()
    Props = JClass("java.util.Properties")

    def props(t):
        p = Props()
        p.load(JClass("java.io.StringReader")(t))
        return p
    to = C.tables(props(OLD), SD.DEFAULT_P3, True)
    tn = C.tables(props(str(M.plan(JString(OLD))[0])), SD.DEFAULT_RUN, True)
    names = [str(x) for x in SD.NAMES]
    ARCH, MIN, FOR, FARM, EXP = int(SD.indexOf("Archer")), int(SD.MINING), int(SD.FORAGING), int(SD.FARMING), int(SD.EXPLORATION)
    oc = lambda s: [int(x) for x in to[s]]
    nc = lambda s: [int(x) for x in tn[s]]
    K.check(oc(MIN) == oc(ARCH) == oc(EXP) == CUM3 and nc(MIN) == nc(ARCH) == nc(EXP) == CUM9, "CM old tables = the P3 list, new = the P9 list (every slot, class too)")
    import random
    rnd = random.Random(62)
    bad, same = 0, 0
    for s in (MIN, FOR, ARCH, FARM, EXP):
        for _ in range(400):
            x = rnd.randint(1, CUM3[100] * 2)
            nx = int(C.remapX(x, to[s], tn[s], -1))
            bad += lvl(CUM3, x) != lvl(CUM9, nx)
            same += (x < CUM3[60]) and nx != x
    K.check(bad == 0 and same == 0, "CM remapX (no cap known): 2000 random totals keep their level; every total below Lv 60 maps to itself (%d / %d)" % (bad, same))
    x = CUM3[70] + (CUM3[71] - CUM3[70]) * 3 // 10
    nx = int(C.remapX(x, to[MIN], tn[MIN], 80))
    K.check(lvl(CUM9, nx) == 70 and abs((nx - CUM9[70]) / (CUM9[71] - CUM9[70]) - 0.3) < 0.001, "CM Mining 70 + 30 %% (cap 80) -> 70 + %.4f" % ((nx - CUM9[70]) / (CUM9[71] - CUM9[70])))
    K.eq(int(C.remapX(CUM3[50] * 3, to[MIN], tn[MIN], 50)), CUM9[50] * 3, "CM past the cap 50: 3x the cap total stays 3x (the cap total did not change)")
    K.eq(int(C.remapX(CUM3[80] * 2, to[MIN], tn[MIN], 80)), round(2 * CUM9[80]), "CM past the cap 80: the ratio (x2 the cap total) is kept")
    # ---- the full run
    base = os.path.join(scratch, "cm", "a")
    pdir = os.path.join(base, "players")
    os.makedirs(pdir)
    open(os.path.join(base, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    files = {
        "p1": "#SkyySkills\n#Thu Oct 22 10:00:00 MDT 2026\n%s=%d\n%s.paid=45\n%s=%d\n%s=%d\nquiet=false\n" % (names[MIN], CUM3[45] + 77, names[MIN], names[ARCH], CUM3[50] * 2, names[EXP], CUM3[30] + 1),
        "p2": "%s=%d\r\n%s=%d\r\n%s=%d\r\n%s=%d\r\n" % (names[ARCH], CUM3[70] + 999, names[MIN], CUM3[75] + 5, names[FARM], 0, names[EXP], CUM3[65] + 3),
        "p3": "%s=%d\n%s=%d\n" % (names[FOR], CUM3[95] + (CUM3[96] - CUM3[95]) // 2, names[ARCH], CUM3[100] + 12345),
    }
    for kf, t in files.items():
        open(os.path.join(pdir, kf + ".properties"), "wb").write(t.encode("latin-1"))
    os.makedirs(os.path.join(base, "rebirth"))
    staged = "#SkyySkills rebirth tx1 - staged\n#Thu Oct 22 10:00:00 MDT 2026\ntx=tx1\nx.%s=%d\nx.%s=%d\n" % (names[ARCH], CUM3[70] + 999, names[MIN], CUM3[75] + 5)
    open(os.path.join(base, "rebirth", "p2.rb-tx1.properties"), "wb").write(staged.encode("latin-1"))
    open(os.path.join(base, "level-floors.properties"), "w", newline="\n").write("# floors\np3/%s=95,%d,\np1/%s=45,%d,\n" % (names[FOR], CUM3[95], names[MIN], CUM3[45]))
    NREB = {"p2": 3, "p3": 5}
    ST.bridge().put("rebirth:fn:cap", _fn(lambda a: a[2] if str(a[1]) == "Exploration" else JClass("java.lang.Integer").valueOf(int(a[2]) + 10 * NREB.get(str(a[0]), 0))))

    def setup(b):
        Cfg.FILE = jpath(os.path.join(b, "xp.properties"))
        ST.DIR = jpath(os.path.join(b, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        Cfg.P3PEND = False
        Cfg.P9PEND = False
    setup(base)
    s0 = T53.snapd(base)
    # the precondition: P3PEND / a pre-P3 xp.properties -> nothing
    Cfg.P3PEND = True
    K.check(not bool(C.run(jpath(base))) and T53.snapd(base) == s0, "CM P3PEND (the P3 file update did not land) -> not done, nothing changed")
    Cfg.P3PEND = False
    pre = "\n".join(ln for ln in OLD.split("\n") if "Balance P3" not in ln or not ln.startswith("#"))
    K.check(M3.plan(JString(pre)) is not None, "CM (setup) without the P3 marker P3Mig would still plan an update")
    open(os.path.join(base, "xp.properties"), "wb").write(pre.encode("latin-1"))
    K.check(not bool(C.run(jpath(base))) and all(T53.snapd(base)[x] == s0[x] for x in s0 if x != "xp.properties") and "curve-p9.properties" not in T53.snapd(base),
            "CM a pre-P3 xp.properties -> not done, no file moved, no marker (retried next start)")
    open(os.path.join(base, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    ok = bool(C.run(jpath(base)))
    s1 = T53.snapd(base)
    K.check(ok and int(C.MOVED) == 3, "CM run: done, 2 player files + 1 staged rebirth file moved, p1 (all below Lv 60 / at the cap 50) not (%s)" % C.LAST)
    K.check(s1["players/p1.properties"] == s0["players/p1.properties"], "CM p1 (Mining 45, Archery 2x the cap-50 total, Exploration 30): byte-identical")
    hist = [k_ for k_ in s1 if k_.startswith("history/curve-p9/")]
    K.check(sorted(h.split("/")[-1] for h in hist) == sorted(["p1.properties", "p2.properties", "p3.properties", "level-floors.properties", "p2.rb-tx1.properties"]),
            "CM History: byte copies of every file first: %s" % sorted(h.split("/")[-1] for h in hist))
    np = dict((kf, props(s1["players/%s.properties" % kf].decode("latin-1"))) for kf in files)
    gv = lambda kf, s: int(np[kf].getProperty(names[s]))
    K.check(lvl(CUM9, gv("p2", ARCH)) == 70 and lvl(CUM9, gv("p2", MIN)) == 75 and gv("p2", FARM) == 0 and lvl(CUM9, gv("p2", EXP)) == 65
            and b"\r\n" in s1["players/p2.properties"] and gv("p2", ARCH) == int(C.remapX(CUM3[70] + 999, to[ARCH], tn[ARCH], 80)),
            "CM p2 (rebirth 3: cap 80): Archery 70, Mining 75, Exploration 65 (no cap, by level) kept; 0 stays; CRLF kept")
    K.check(lvl(CUM9, gv("p3", FOR)) == 95 and abs((gv("p3", FOR) - CUM9[95]) / (CUM9[96] - CUM9[95]) - 0.5) < 0.001
            and gv("p3", ARCH) == round((CUM3[100] + 12345) / CUM3[100] * CUM9[100]), "CM p3 (rebirth 5: cap 100): Foraging 95 + 50 %% kept; Archery past 100 keeps its ratio")
    sp_ = props(s1["rebirth/p2.rb-tx1.properties"].decode("latin-1"))
    K.check(int(sp_.getProperty("x." + names[ARCH])) == gv("p2", ARCH) and int(sp_.getProperty("x." + names[MIN])) == gv("p2", MIN) and sp_.getProperty("tx") == "tx1",
            "CM the staged rebirth file's x.<Slot> moved exactly like the player file")
    fl = s1["level-floors.properties"].decode("latin-1")
    K.check(("p3/%s=95,%d,\n" % (names[FOR], CUM9[95])) in fl and ("p1/%s=45,%d,\n" % (names[MIN], CUM3[45])) in fl and fl.startswith("# floors\n"), "CM floors: XP then -> newCum(level): %r" % fl)
    st = s1["curve-p9.properties"].decode("latin-1")
    K.check("complete=" in st and "done.p2=1" in st and "history=history/curve-p9/" in st and "0.4.62 Balance P9" in st, "CM marker file curve-p9.properties")
    lg = s1.get("curve-p9.log", b"").decode("utf-8")
    K.check(lg.count("\n") == 1 and "Undo" in lg and "3 profile file(s)" in lg and "0.4.61" in lg and "curve-p9.properties" in lg, "CM curve-p9.log: one line with the Undo: %s" % lg[:220])
    K.check(s1["xp.properties"] == s0["xp.properties"], "CM xp.properties untouched by CurveP9Mig (P9Mig does it after)")
    K.check(bool(C.run(jpath(base))) and T53.snapd(base) == s1, "CM a second start (P9Mig not run yet) changes nothing")
    # P9Mig + after: the file lands, xp= in the marker
    msg = str(M.run())
    C.after(jpath(base))
    s2 = T53.snapd(base)
    K.check("updated for 0.4.62" in msg and not bool(Cfg.P9PEND) and _props(s2["xp.properties"])["levels"] == P9_T and "xp=" in s2["curve-p9.properties"].decode("latin-1"),
            "CM P9Mig.run + after: xp.properties on the P9 list, P9PEND off, xp= in the marker: %s" % msg[:120])
    # the guard: a pre-P9 xp.properties put back (players still moved) -> updated again, XP not moved twice
    open(os.path.join(base, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    ok3 = bool(C.run(jpath(base)))
    s3 = T53.snapd(base)
    K.check(ok3 and all(s3[x] == s2[x] for x in s2 if x.startswith("players/") or x.startswith("rebirth/")), "CM guard: the old xp.properties put back -> done, the moved XP is NOT moved again")
    msg2 = str(M.run())
    K.check("updated for 0.4.62" in msg2 and _props(open(os.path.join(base, "xp.properties"), "rb").read())["levels"] == P9_T, "CM guard: P9Mig updates the put-back file again")
    # fix round (critic LOW 1): Server Setup -> Changes -> Undo of ONLY the levels row after the move -> a WARN every start, nothing changed
    t9 = open(os.path.join(base, "xp.properties"), "rb").read().decode("latin-1")
    und = t9.replace("\nlevels=%s" % P9_T, "\nlevels=%s" % P3_T)
    K.check(und != t9 and M.plan(JString(und)) is None and bool(C.levelsUndone(JString(und))) and not bool(C.levelsUndone(JString(t9)))
            and not bool(C.levelsUndone(JString(und.replace("\nlevels=%s" % P3_T, "\nlevels=%s,1" % P3_T)))) and not bool(C.levelsUndone(JString(OLD + "\nlevels=" + P9_T + "\n"))),
            "CM levelsUndone: true only for the exact 0.4.61 list (not the P9 list, not an admin's own list)")
    open(os.path.join(base, "xp.properties"), "wb").write(und.encode("latin-1"))
    s4 = T53.snapd(base)
    K.check(bool(C.run(jpath(base))) and T53.snapd(base) == s4 and M.plan(JString(und)) is None, "CM the levels row undone alone: run = done, WARN only, nothing moved or rewritten")
    # fix round 2 (second critic MEDIUM): while the levels row is undone alone, SkillCfg.load sets P9STALE and payLocked pays NO level-up coins
    paid_ = []
    ST.bridge().put("coins:fn:add", _fn(lambda a: (paid_.append(int(a[1])), JClass("java.lang.Long").valueOf(1))[1]))
    UID = JClass("java.util.UUID").randomUUID()
    NN = int(SD.N)

    def dat(total, mark):
        d_ = JArray(JLong)(3 * NN)
        d_[MIN] = total
        d_[NN + MIN] = mark
        return d_
    from jpype import JArray, JLong
    Cfg.load()
    stale = bool(Cfg.P9STALE)
    d1 = dat(CUM9[70] + 5, 70)
    lv_shown = int(J("SkillCap").level("p3", MIN, d1[MIN]))
    r1_ = ST.payLocked("p3", UID, MIN, d1)
    K.check(stale and [int(x) for x in SD.PER] == BM.P3_LEVELS and lv_shown == lvl(CUM3, CUM9[70] + 5) > 70 and int(r1_[0]) == -1 and int(r1_[4]) == 0
            and int(d1[NN + MIN]) == 70 and not paid_ and T53.snapd(base) == s4,
            "CM fix round 2: levels row undone alone -> P9STALE; a Mining total shown at Lv %d (70 on the P9 list) gets NO coins, paid marker stays 70, no file written" % lv_shown)
    open(os.path.join(base, "xp.properties"), "wb").write(t9.encode("latin-1"))
    Cfg.load()
    d2 = dat(CUM9[70] + 5, 70)
    r2_ = ST.payLocked("p3", UID, MIN, d2)
    d3 = dat(CUM9[70] + 5, 65)
    r3_ = ST.payLocked("p3", UID, MIN, d3)
    K.check(not bool(Cfg.P9STALE) and int(r2_[0]) == -1 and int(d2[NN + MIN]) == 70 and int(r3_[0]) == 66 and int(r3_[1]) == 70 and int(d3[NN + MIN]) == 70 and len(paid_) == 5,
            "CM fix round 2: the 0.4.62 row back -> P9STALE off, Lv 70 (already paid) gets nothing more; a marker at 65 pays exactly 66-70 (the coin path works): %s" % paid_)
    ST.bridge().remove("coins:fn:add")
    b0 = os.path.join(scratch, "cm", "z")
    os.makedirs(b0)
    open(os.path.join(b0, "xp.properties"), "wb").write(und.encode("latin-1"))
    Cfg.FILE = jpath(os.path.join(b0, "xp.properties"))
    Cfg.load()
    K.check(not bool(Cfg.P9STALE), "CM fix round 2: the 0.4.61 list with no curve-p9.properties (XP never moved) -> coins NOT held")
    setup(base)
    open(os.path.join(base, "xp.properties"), "wb").write(t9.encode("latin-1"))
    # P9PEND: the saved XP moved but the xp.properties update did not land -> this start loads the planned text from memory
    b2 = os.path.join(scratch, "cm", "b")
    os.makedirs(os.path.join(b2, "players"))
    open(os.path.join(b2, "xp.properties"), "wb").write(OLD.encode("latin-1"))
    open(os.path.join(b2, "players", "p2.properties"), "wb").write(files["p2"].encode("latin-1"))
    setup(b2)
    ok4 = bool(C.run(jpath(b2)))
    C.after(jpath(b2))
    pend = bool(Cfg.P9PEND)
    Cfg.load()
    K.check(ok4 and pend and [int(x) for x in SD.PER] == BM.P9_LEVELS and _props(open(os.path.join(b2, "xp.properties"), "rb").read())["levels"] == P3_T
            and abs(float(J("P3Xp").CATCH_MAX) - 0.2) < 1e-12 and float(J("P3Xp").BEAST_F) == 1.5,
            "CM P9PEND: the file update skipped after the XP moved -> load() uses the planned P9 text (P9 list, catch-up 20 %%, x1.5); the file still old")
    M.run()
    C.after(jpath(b2))
    Cfg.load()
    K.check(not bool(Cfg.P9PEND) and [int(x) for x in SD.PER] == BM.P9_LEVELS, "CM P9PEND clears once the file holds the update")
    # no xp.properties: the 0.4.61 code defaults are the old tables (P3 -> P9), and CurveP3Mig's no-file tables = the 0.4.61 default file's
    b3 = os.path.join(scratch, "cm", "c")
    os.makedirs(os.path.join(b3, "players"))
    open(os.path.join(b3, "players", "p2.properties"), "wb").write(files["p2"].encode("latin-1"))
    setup(b3)
    ok5 = bool(C.run(jpath(b3)))
    p5 = props(open(os.path.join(b3, "players", "p2.properties"), "rb").read().decode("latin-1"))
    K.check(ok5 and lvl(CUM9, int(p5.getProperty(names[ARCH]))) == 70 and int(p5.getProperty(names[ARCH])) == gv("p2", ARCH), "CM no xp.properties: P3 -> P9 move, Archery 70 kept")
    t3a = C3.tables(props(""), SD.DEFAULT_P3, True)
    t3b = C3.tables(props(OLD), SD.DEFAULT_P3, True)
    K.check(all([int(v) for v in t3a[s]] == [int(v) for v in t3b[s]] for s in range(int(SD.N))), "CM CurveP3Mig with no file: its new tables = the 0.4.61 default file's (unchanged behaviour)")
    K.save()


def run_live62(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy62")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, SD = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("CurveP3Mig"), J("P3Mig"), J("SkillDefs")
    C9, M9 = J("CurveP9Mig"), J("P9Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    xp = os.path.join(lc, "xp.properties")
    names = [str(x) for x in SD.NAMES]

    def start():
        Cfg.FILE = jpath(xp)
        Sto.DATA.clear()
        Sto.DIR = jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in T57.MIGS)
        ok = bool(C.run(jpath(lc)))
        r["P3Mig"] = str(M.run()) if ok else ""
        if ok:
            C.after(jpath(lc))
        for nm in ("P4Mig", "PlMigP8", "BmMigP8c", "SkMigP7"):
            r[nm] = str(J(nm).run())
        ok9 = bool(C9.run(jpath(lc)))
        r["CurveP9Mig"] = str(C9.LAST) + (" ok" if ok9 else " NOT DONE")
        r["P9Mig"] = str(M9.run()) if ok9 else ""
        if ok9:
            C9.after(jpath(lc))
        r["load"] = str(Cfg.load())
        return r
    before = _props(open(xp, encoding="latin-1").read())
    pdir = os.path.join(lc, "players")
    p_before = dict((fn, _props(open(os.path.join(pdir, fn), "rb").read())) for fn in os.listdir(pdir) if fn.endswith(".properties"))
    r1 = start()
    s1 = T53.snapd(lc)
    K.notes.append("LIVE62 start 1: CurveP9Mig: %s | P9Mig: %s" % (r1["CurveP9Mig"][:240], r1["P9Mig"][:300]))
    K.check(r1["CurveP9Mig"].endswith(" ok") and "updated for 0.4.62" in r1["P9Mig"], "LIVE62 start 1: both P9 updates ran")
    after = _props(open(xp, encoding="latin-1").read())
    want = dict((k, (n if before.get(k) == o else before.get(k))) for k, o, n in KEYS)
    K.check(all(after.get(k) == want[k] for k, o, n in KEYS), "LIVE62 each P9 key: the 0.4.61 default -> the new value, a missing line stays missing, an admin's kept: %s" % (
        dict((k, (before.get(k, "(none)")[:12], after.get(k, "(none)")[:12])) for k, o, n in KEYS)))
    K.notes.append("LIVE62 live file before: " + ", ".join("%s=%s" % (k, before.get(k, "(no line)")[:16]) for k, o, n in KEYS))
    lc61 = "levelCoins" not in before   # the live world has not started 0.4.61 yet: SkMigP7 (0.4.61) adds levelCoins in the same start
    other = sorted(k for k in set(before) | set(after) if after.get(k) != before.get(k) and k not in want and not (lc61 and k == "levelCoins"))
    K.check(not other, "LIVE62 nothing else in xp.properties changed: %s" % other[:12])
    txt = open(xp, encoding="latin-1").read()
    K.check(txt.count(MARK_ID) == 1, "LIVE62 the P9 marker once")
    cl = s1.get("config-changes.log", b"").decode("utf-8", "replace")
    nmig = sum(1 for k, o, n in KEYS if before.get(k) == o)
    K.check(cl.count("\tSkyySkills 0.4.62\t") == nmig, "LIVE62 one change-log row per changed key (%d; Undo in Server Setup -> Changes)" % nmig)
    K.check(any(MARK_ID.encode() not in open(os.path.join(r_, f_), "rb").read() and b"Balance P7 economy" in open(os.path.join(r_, f_), "rb").read()
                for r_, _d, fs in os.walk(os.path.join(lc, "config-history")) for f_ in fs), "LIVE62 config-history holds the pre-P9 xp.properties")
    K.check("complete=" in s1.get("curve-p9.properties", b"").decode("latin-1"), "LIVE62 curve-p9.properties complete")
    # every live profile: every slot shows the same level on the new list as before on the old one
    bad, n, moved = [], 0, 0
    for fn, ob in sorted(p_before.items()):
        nb = _props(open(os.path.join(pdir, fn), "rb").read())
        n += 1
        for s in names:
            if s in ob:
                try:
                    xo, xn = int(ob[s]), int(nb[s])
                except Exception:
                    continue
                moved += xo != xn
                if lvl(CUM3, xo) != lvl(CUM9, xn):
                    bad.append((fn, s, xo, xn))
        if set(ob) != set(nb) or any(ob[k_] != nb[k_] for k_ in ob if k_ not in names):
            bad.append((fn, "other keys changed"))
    K.check(n >= 1 and not bad, "LIVE62 %d live profile file(s): every slot keeps its level (%d total(s) moved, the rest above Lv 60 none): %s" % (n, moved, bad[:3]))
    K.notes.append("LIVE62 live levels: " + "; ".join("%s %s" % (fn[:12], " ".join("%s %d" % (s[:5], lvl(CUM3, int(ob[s]))) for s in names if s in ob and ob[s].isdigit() and int(ob[s]) > 0))
                                                      for fn, ob in sorted(p_before.items())))
    K.check([int(x) for x in SD.PER] == ([int(v) for v in after["levels"].split(",")]) and float(J("P3Xp").BEAST_F) == float(want["beast.xpFactor"] or 1.5)
            and abs(float(J("P3Xp").CATCH_MAX) * 100.0 - float(want["catchup.max"] or 20)) < 1e-9 and float(J("XpEven").MINE) == float(want["mining.xpMultiplier"] or 1)
            and float(J("XpEven").FELL_PCT) == float(want["fell.otherLogsPercent"] or 100), "LIVE62 SkillCfg.load of the migrated copy reads the new numbers: %s" % r1["load"][:160])
    # saved player data loads + saves the same keys
    UUID = JClass("java.util.UUID")
    bad2 = []
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".properties"):
            continue
        kk = fn[:-11]
        u = UUID.fromString(kk[:36])
        old = _props(open(os.path.join(pdir, fn), "rb").read())
        got = Sto.readFile(kk, u)
        Sto.install(kk, u, got)
        sp = Sto.snap(kk)
        new = dict((str(x), str(sp.getProperty(x))) for x in sp.stringPropertyNames())
        changed = sorted(x for x in set(old) & set(new) if old[x] != new[x])
        added = sorted(set(new) - set(old))
        if changed or set(old) - set(new) or not set(added) <= ZERO_SLOTS or any(new[x] != "0" for x in added):
            bad2.append((fn, changed[:5], added))
    K.check(not bad2, "LIVE62 every live profile loads + saves the same keys: %s" % bad2[:3])
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(all(s1.get(x) == s2.get(x) for x in set(s1) | set(s2)) and r2["P9Mig"] == "" and r2["CurveP9Mig"].strip() == "ok", "LIVE62 start 2 changes nothing")
    K.save()


HUD_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")   # read-only: copied into scratch below
SYN = "00000000-0000-4000-8000-000000006201"   # the synthetic profile above Lv 60 (no live profile is that high)


def run_hud62(out, jar, scratch, _home):
    """Fix round (critic MEDIUM 1 + 2): the combined chain on an old world - CurveP3Mig + P3Mig (pre-0.4.57 -> P3), then CurveP9Mig + P9Mig
    (P3 -> P9) in ONE start, with a real saved-XP move above Lv 60 (a synthetic profile next to the HUD-mod world's own 10)."""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    root = os.path.join(scratch, "hud62")
    lc = os.path.join(root, "Skyy_SkyySkills")
    shutil.copytree(HUD_DIR, lc)
    os.makedirs(os.path.join(root, "Skyy_SkyyRebirth"))   # like the real world: rebirth data present -> the cap comes from rebirth:fn:cap
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, SD = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("CurveP3Mig"), J("P3Mig"), J("SkillDefs")
    C9, M9 = J("CurveP9Mig"), J("P9Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    xp = os.path.join(lc, "xp.properties")
    pdir = os.path.join(lc, "players")
    names = [str(x) for x in SD.NAMES]
    N = len(names)
    txt0 = open(xp, encoding="latin-1").read()
    K.check(M.plan(JString(txt0)) is not None and _props(txt0).get("levels") not in (P3_T, P9_T) and "curve-p3.properties" not in os.listdir(lc),
            "HUD62 (setup) the HUD-mod copy is a pre-0.4.57 world (P3Mig would update it; levels= neither P3 nor P9; no curve-p3 marker)")

    def env():
        Cfg.FILE = jpath(xp)
        Sto.DATA.clear()
        Sto.DIR = jpath(pdir)
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        Cfg.P3PEND = False
        Cfg.P9PEND = False
        LF.NEW_FARM = False

    def start():
        env()
        r = dict((nm, str(J(nm).run())) for nm in T57.MIGS)
        ok = bool(C.run(jpath(lc)))
        r["CurveP3Mig"] = str(C.LAST) + (" ok" if ok else " NOT DONE")
        r["P3Mig"] = str(M.run()) if ok else ""
        if ok:
            C.after(jpath(lc))
        for nm in ("P4Mig", "PlMigP8", "BmMigP8c", "SkMigP7"):
            r[nm] = str(J(nm).run())
        ok9 = bool(C9.run(jpath(lc)))
        r["CurveP9Mig"] = str(C9.LAST) + (" ok" if ok9 else " NOT DONE")
        r["P9Mig"] = str(M9.run()) if ok9 else ""
        if ok9:
            C9.after(jpath(lc))
        r["load"] = str(Cfg.load())
        return r
    # the pre-0.4.57 one-time updates first (run-once; start() runs them again as no-ops, so this is still ONE start of the P3 + P9 chain):
    # the old tables are what CurveP3Mig reads at that point (its own tables(.., DEFAULT_056, false): the generic, own-skill and class lists)
    env()
    for nm in T57.MIGS:
        J(nm).run()
    pre = open(xp, encoding="latin-1").read()
    to = C.tables(C.props(JString(pre)), SD.DEFAULT_056, False)
    oc = [[int(v) for v in to[s]] for s in range(N)]
    MIN, FOR, ARCH = int(SD.MINING), int(SD.FORAGING), int(SD.indexOf("Archer"))
    K.check(len(oc[MIN]) == 101 and len(oc[ARCH]) == 101 and oc[MIN] != oc[FOR], "HUD62 (setup) old tables: 100 levels; Mining has its own list (levels.skill.Mining)")
    at = lambda s, Lv, f: oc[s][Lv] + int((oc[s][Lv + 1] - oc[s][Lv]) * f)
    syn = {names[MIN]: (MIN, at(MIN, 70, 0.3)), names[ARCH]: (ARCH, at(ARCH, 85, 0.5)), names[FOR]: (FOR, at(FOR, 62, 0.0) + 7)}
    open(os.path.join(pdir, SYN + ".properties"), "wb").write(
        ("#SkyySkills\n#Thu Oct 22 10:00:00 MDT 2026\n" + "".join("%s=%d\n%s.paid=%d\n" % (k_, v_[1], k_, lvl(oc[v_[0]], v_[1])) for k_, v_ in sorted(syn.items()))
         + "quiet=false\n").encode("latin-1"))
    # rebirth cap 90 for the synthetic profile (base 50 + 40), the base cap for the live ones
    Sto.bridge().put("rebirth:fn:cap", _fn(lambda a: a[2] if str(a[1]) == "Exploration" else JClass("java.lang.Integer").valueOf(int(a[2]) + (40 if str(a[0]).startswith(SYN) else 0))))
    p_before = dict((fn, _props(open(os.path.join(pdir, fn), "rb").read())) for fn in os.listdir(pdir) if fn.endswith(".properties"))
    r1 = start()
    s1 = T53.snapd(lc)
    K.notes.append("HUD62 start 1: CurveP3Mig: %s | P3Mig: %s | CurveP9Mig: %s | P9Mig: %s" % (r1["CurveP3Mig"][:160], r1["P3Mig"][:120], r1["CurveP9Mig"][:160], r1["P9Mig"][:160]))
    fin = s1["xp.properties"].decode("latin-1")
    after = _props(fin)
    tn = C9.tables(C9.props(JString(fin)), SD.DEFAULT_RUN, True)
    nc = [[int(v) for v in tn[s]] for s in range(N)]
    K.check(r1["CurveP3Mig"].endswith(" ok") and r1["CurveP9Mig"].endswith(" ok") and "updated for 0.4.62" in r1["P9Mig"] and after.get("levels") == P9_T
            and not bool(Cfg.P3PEND) and not bool(Cfg.P9PEND) and [int(x) for x in SD.PER] == BM.P9_LEVELS and nc[MIN] == nc[ARCH] == nc[FOR] == CUM9,
            "HUD62 ONE start: pre-P3 -> P3 -> P9, xp.properties ends on the P9 list (every slot), nothing pending, SkillCfg.load reads the P9 list")
    K.check("complete=" in s1.get("curve-p3.properties", b"").decode("latin-1") and "complete=" in s1.get("curve-p9.properties", b"").decode("latin-1")
            and "xp=" in s1["curve-p9.properties"].decode("latin-1"), "HUD62 one curve-p3.properties + one curve-p9.properties, both complete")
    h3 = sorted(set(k_.split("/")[2] for k_ in s1 if k_.startswith("history/curve-p3/")))
    h9 = sorted(set(k_.split("/")[2] for k_ in s1 if k_.startswith("history/curve-p9/")))
    K.check(len(h3) == 1 and len(h9) == 1, "HUD62 one History copy each (curve-p3: %s, curve-p9: %s)" % (h3, h9))
    hs3 = _props(s1.get("history/curve-p3/%s/players/%s.properties" % ((h3 or ["?"])[0], SYN), b""))
    hs9 = _props(s1.get("history/curve-p9/%s/players/%s.properties" % ((h9 or ["?"])[0], SYN), b""))
    K.check(all(int(hs3.get(k_, -1)) == v_[1] for k_, v_ in syn.items()) and all(lvl(CUM3, int(hs9.get(k_, -1))) == lvl(oc[v_[0]], v_[1]) for k_, v_ in syn.items()),
            "HUD62 History: curve-p3 holds the original totals, curve-p9 the totals as the P3 move left them (same levels on the P3 list)")
    bad, moved, seen = [], 0, 0
    for fn, ob in sorted(p_before.items()):
        nb = _props(s1["players/" + fn])
        for s in range(N):
            k_ = names[s]
            if k_ in ob and ob[k_].isdigit():
                xo, xn = int(ob[k_]), int(nb[k_])
                seen += 1
                moved += xo != xn
                if lvl(oc[s], xo) != lvl(nc[s], xn):
                    bad.append((fn[:12], k_, xo, lvl(oc[s], xo), xn, lvl(nc[s], xn)))
        if set(ob) != set(nb) or any(ob[k_] != nb[k_] for k_ in ob if k_ not in names):
            bad.append((fn[:12], "other keys changed"))
    K.check(len(p_before) >= 2 and not bad, "HUD62 %d profile file(s) (%d live + the synthetic one): all %d slot totals keep their level across both moves (%d moved): %s" % (
        len(p_before), len(p_before) - 1, seen, moved, bad[:4]))
    sp = _props(s1["players/%s.properties" % SYN])
    prog = lambda c, x: (x - c[lvl(c, x)]) / float(c[lvl(c, x) + 1] - c[lvl(c, x)])
    got = dict((k_, (lvl(CUM9, int(sp[k_])), round(prog(CUM9, int(sp[k_])), 4))) for k_ in syn)
    K.check(got[names[MIN]][0] == 70 and abs(got[names[MIN]][1] - 0.3) < 0.002 and got[names[ARCH]][0] == 85 and abs(got[names[ARCH]][1] - 0.5) < 0.002
            and got[names[FOR]][0] == 62 and got[names[FOR]][1] < 0.002 and all(int(sp[k_]) != v_[1] for k_, v_ in syn.items()),
            "HUD62 the synthetic profile: Mining 70 + 30 %%, Archer 85 + 50 %%, Foraging 62 + 0 kept on the P9 list (XP moved): %s" % got)
    K.check(all(sp[k_ + ".paid"] == str(lvl(oc[v_[0]], v_[1])) for k_, v_ in syn.items()), "HUD62 the level-up paid markers are untouched (no free level coins)")
    lg9 = s1.get("curve-p9.log", b"").decode("utf-8")
    K.check(lg9.count("\n") == 1 and "Undo" in lg9 and s1.get("curve-p3.log", b"").decode("utf-8").count("\n") == 1, "HUD62 one curve-p3.log + one curve-p9.log line")
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(all(s1.get(x) == s2.get(x) for x in set(s1) | set(s2)) and r2["P9Mig"] == "" and r2["CurveP9Mig"].strip() == "ok",
            "HUD62 start 2 changes nothing (XP never moved twice): %s" % sorted(x for x in set(s1) | set(s2) if s1.get(x) != s2.get(x))[:6])
    K.save()


# checked by hand 2026-10-22 (first run): the members this round changes on purpose
EXPECT.update({'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'CurveP3Mig': ['~m guard', '~m run'],
               'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'], 'P3Xp': ['~<clinit>', '~m checkPast', '~m read'],
               'SkillCfg': ['+f P9PEND', '+f P9STALE', '+m p9pend', '+m p9stale', '~<clinit>', '~m load'], 'SkillDefs': ['+f DEFAULT_P3', '~<clinit>'], 'SkillStore': ['~m payLocked'], 'SkyySkillsPlugin': ['~m setup'],
               'XpEven': ['~<clinit>', '~m read']})

if __name__ == "__main__":
    phases = [("static", run_static), ("df", run_df), ("pm", run_pm), ("cm", run_cm), ("live62", run_live62), ("hud62", run_hud62)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
