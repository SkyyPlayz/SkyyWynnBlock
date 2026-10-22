"""SkyySkills 0.4.61 - harness for BALANCE PASS P7 ECONOMY P7b (level-up coins on the coin curve; research/Balance-P7-Economy-Spec.md 2.1 / 9;
tools/skills_0_4_61_patch.py). Build first: python tools/skills_0_4_61_patch.py && python SkyySkills/build_skyyskills_0.4.61.py

    python SkyySkills/test_skyyskills_0.4.61.py [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes, line endings kept, setup order BmMigP8c -> SkMigP7 -> SkillCfg.load, two new classes
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.60 -> 0.4.61: + LvCoins, SkMigP7; only the planned members differ
  LC   EXECUTED LvCoins: the table at Lv 1 / 10 / 15 / 20 / 50 / 90 / 100 / 150 (clamp) = the model (p7_level_coins + p7_round); a
       coins:fn:curve stand-in (x2 everywhere, a broken one, a negative one) scales / falls back; parse / check (good, empty, bad); read()
       of an empty line = the old coinsPerLevel x level (incl. 0 and overflow), a bad line = WARN + the default; the Server Setup row
  PAY  EXECUTED SkillStore.payOwedK with a stand-in coins:fn:add: levels 9 -> 12 pay at(10) + at(11) + at(12); x0.8 after 1 rebirth; an
       empty levelCoins = 100 x level; a 0 point = the level counts as paid, no coins; the Stats page "+N coins when you reach level"
  PM   SkMigP7.plan / sameAfter: the 0.4.60 jar's default file -> exactly the 0.4.61 one; coinsPerLevel=250 -> levelCoins= (empty) + note;
       coinsPerLevel=100 -> the table; a file that has levelCoins keeps it; the marker = null; CRLF; the change-log row
  LIVE61 every one-time update in setup() order (0.4.60's list + SkMigP7) on a scratch COPY of the live data + SkillCfg.load, started TWICE
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
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp7b", "sk")]
T60 = _mod(os.path.join(HERE, "test_skyyskills_0.4.60.py"), "test_skyyskills_0_4_60")
T58, T57, T48, T53 = T60.T58, T60.T57, T60.T48, T60.T53
VERSION = "0.4.61"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.60.py")
PATCH = os.path.join(TOOLS, "skills_0_4_61_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.60.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T58.LIVE_DIR
ADDED = ["LvCoins", "SkMigP7"]
EXPECT = {}   # filled in below (checked by hand)
LC_TEXT = BM.P7_LEVEL_COINS_TEXT
ZERO_SLOTS = set(["Beastmastery", "Beastmastery.paid", "Combat.Spellblade", "Combat.Spellblade.paid"])   # 0.4.43 / 0.4.60 slots a save adds at 0
MARK_ID = "Balance P7 economy (SkyySkills 0.4.61)"
_props = T58._props


def model(L):
    return BM.p7_round(BM.p7_level_coins(min(100, max(1, L))))


def _old_defaults():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "SkillCfg", loader=ld).DEFAULTS)


def _fn(JClass, JImplements, JOverride, f):
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
    K.check(g.startswith('"""SkyySkills 0.4.61 - build script') and g.count('VERSION = "0.4.61"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 2 and ", bm60, lvc61, skm61, lvf," in g, "S two new classes (LvCoins, SkMigP7), written out")
    su = g[g.index("{PKG}.CurveP3Mig.run(base)"):]
    K.check(su.index("{PKG}.BmMigP8c.run();") < su.index("{PKG}.SkMigP7.run();") < su.index("SkillCfg.load"), "S setup: BmMigP8c -> SkMigP7 -> SkillCfg.load")
    K.check("SkillCfg.COINS_PER_LEVEL * " not in g and g.count("{PKG}.LvCoins.at(") >= 5, "S every level-coin amount (pay, chat, Stats page) goes through LvCoins.at")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_lc(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = T57.boot(K)
    T57.fresh_load(J, Cfg, os.path.join(scratch, "lc"))
    LC, ST = J("LvCoins"), J("SkillStore")
    br = ST.bridge()
    br.remove("coins:fn:curve")
    lv = (1, 2, 9, 10, 15, 20, 21, 30, 40, 41, 50, 55, 60, 70, 80, 81, 90, 95, 100)
    got = [int(LC.at(L)) for L in lv]
    K.eq(got, [model(L) for L in lv], "LC LvCoins.at = the model (p7_level_coins + p7_round) at %s" % (lv,))
    K.eq([int(LC.at(L)) for L in (10, 50, 90)], [60, 2800, 50500], "LC spec 2.1: Lv 10 60, Lv 50 2,800, Lv 90 50,500")
    K.eq([int(LC.at(L)) for L in (0, -3, 150, 1000)], [0, 0, 95000, 95000], "LC level 0 / negative = 0; above 100 = the Lv 100 point")
    D = JClass("java.lang.Double")
    br.put("coins:fn:curve", _fn(JClass, JImplements, JOverride, lambda a: D.valueOf(2.0 * float(LC.curveOwn(int(a)))) if not hasattr(a, "__len__") else None))
    K.eq([int(LC.at(L)) for L in (10, 50, 90)], [120, 5600, 100000], "LC a coins:fn:curve twice the default -> level coins x2, rounded (Lv 90 101,000 -> 100,000: the 5,000 step)")
    br.put("coins:fn:curve", _fn(JClass, JImplements, JOverride, lambda a: D.valueOf(-1.0)))
    K.eq(int(LC.at(50)), 2800, "LC a negative curve answer = the built-in curve (x1)")

    def boom(a):
        raise RuntimeError("x")
    br.put("coins:fn:curve", _fn(JClass, JImplements, JOverride, boom))
    K.eq(int(LC.at(50)), 2800, "LC a throwing coins:fn:curve = the built-in curve")
    br.remove("coins:fn:curve")
    # the SkyyCoins 0.1.10 jar's real coins:fn:curve answers exactly the built-in copy
    cj = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.10.jar")
    K.check(abs(float(LC.curveOwn(10)) - 1.0) < 1e-9 and abs(float(LC.curveOwn(50)) - 36.8) < 1e-9 and abs(float(LC.curveOwn(44)) - (13.8 * 30.3) ** 0.5) / (13.8 * 30.3) ** 0.5 < 0.01,
            "LC the built-in curve: Lv 10 x1, Lv 50 x36.8, Lv 44 = sqrt(13.8 x 30.3) +-1 %")
    # parse / check
    for v, ok in (("1:30,10:60", True), (LC_TEXT, True), ("", True), ("  ", True), ("10:60,5:30", False), ("0:5", False), ("101:5", False), ("a:b", False),
                  ("10:-1", False), ("10:60,", True), ("10", False), (",", False)):   # a trailing comma is tolerated (String.split)
        r = LC.check("levelCoins", v)
        K.check((r is None) == ok, "LC check %r -> %s" % (v, "fine" if r is None else r))
    Props = JClass("java.util.Properties")

    def rd(txt):
        p = Props()
        p.load(JClass("java.io.StringReader")(txt))
        return str(LC.read(p))
    t = rd("levelCoins=\ncoinsPerLevel=100\n")
    Cfg.COINS_PER_LEVEL = 100
    K.check(LC.L is None and int(LC.at(10)) == 1000 and int(LC.at(37)) == 3700 and "coinsPerLevel" in t, "LC levelCoins empty -> the old 100 x level (%s)" % t)
    Cfg.COINS_PER_LEVEL = 0
    K.eq(int(LC.at(10)), 0, "LC empty + coinsPerLevel 0 = no coins")
    Cfg.COINS_PER_LEVEL = 9000000000000000000
    K.eq(int(LC.at(10)), 0, "LC empty + an overflowing coinsPerLevel = no coins (the 0.4.60 overflow rule)")
    Cfg.COINS_PER_LEVEL = 100
    t2 = rd("levelCoins=10:5,5:1\n")
    K.check(LC.L is not None and int(LC.at(50)) == 2800, "LC a bad levelCoins line = the default table (WARN): %s" % t2)
    rd("levelCoins=1:100,100:100\n")
    K.eq([int(LC.at(L)) for L in (1, 50, 100)], [100, 100, 100], "LC an admin's flat table pays 100 a level")
    rd("levelCoins=1:0,11:1000\n")
    K.eq([int(LC.at(L)) for L in (1, 6, 11)], [0, 500, 1000], "LC a 0 point interpolates linearly (no log of 0)")
    rd("")
    K.eq(int(LC.at(90)), 50500, "LC no line = the default table")
    # fix 1 (critic 1): no levelCoins line + an admin's coinsPerLevel (Undo of the SkMigP7 row, or the update skipped) = their linear rule
    Cfg.COINS_PER_LEVEL = 0
    t3 = rd("coinsPerLevel=0\n")
    K.check(LC.L is None and int(LC.at(10)) == 0 and int(LC.at(90)) == 0, "FIX1 no levelCoins + coinsPerLevel=0 (switched off) -> still no coins (%s)" % t3)
    Cfg.COINS_PER_LEVEL = 250
    rd("coinsPerLevel=250\n")
    K.check(LC.L is None and int(LC.at(10)) == 2500, "FIX1 no levelCoins + coinsPerLevel=250 -> 250 x level, never the table")
    Cfg.COINS_PER_LEVEL = 100
    rd("coinsPerLevel=100\n")
    K.eq(int(LC.at(50)), 2800, "FIX1 no levelCoins + coinsPerLevel=100 (the default) -> the table")
    # fix (second critic): at() reads only the one volatile T = { levels, coins } - a torn L / C pair (a reload on another thread) never pays linear
    K.check(LC.T is not None and len(LC.T[0]) == len(LC.T[1]) == len(LC.L), "FIX2B read() publishes T = { L, C } together")
    _l0 = LC.L
    from jpype import JArray as _JA, JInt as _JI
    LC.L = _JA(_JI)([1])
    K.eq(int(LC.at(50)), 2800, "FIX2B a torn L (other length than C) is ignored: at() uses T -> still 2,800 at Lv 50, never 100 x 50")
    LC.L = _l0
    rd("levelCoins=\ncoinsPerLevel=100\n")
    K.check(LC.T is None and int(LC.at(50)) == 5000, "FIX2B levelCoins empty -> T null -> 100 x level")
    rd("coinsPerLevel=100\n")
    rows_ = dict((str(r[0]), [str(x) for x in list(r)]) for r in J("CfgRows").header()[7])
    r_ = rows_.get("levelCoins")
    gen = open(GEN, encoding="utf8").read()
    K.check(r_ is not None and r_[2] == "general" and r_[3] == "text" and r_[4] == LC_TEXT and len(r_[10]) <= 100 and '"reload;check=LvCoins.check"),' in gen,
            "LC Server Setup row Skills -> General: Level-up coins by level (text, the table, check=LvCoins.check): %s" % r_)
    K.check("Only while" in rows_["coinsPerLevel"][10], "LC the coinsPerLevel row says it pays only while levelCoins is empty")
    K.check(str(Cfg.DEFAULTS).count(MARK_ID) == 1 and ("\nlevelCoins=" + LC_TEXT + "\n") in str(Cfg.DEFAULTS) and "\ncoinsPerLevel=100\n" in str(Cfg.DEFAULTS),
            "LC the fresh file: levelCoins=<table>, coinsPerLevel=100, the marker once")
    K.save()


def run_pay(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = T57.boot(K)
    T57.fresh_load(J, Cfg, os.path.join(scratch, "pay"))
    SD, ST, LC = J("SkillDefs"), J("SkillStore"), J("LvCoins")
    br = ST.bridge()
    br.remove("coins:fn:curve")
    Integer, Long = JClass("java.lang.Integer"), JClass("java.lang.Long")
    N = int(SD.N)
    paid = []

    def add(o):
        paid.append(int(o[1]))
        return Long(1)
    br.put("coins:fn:add", _fn(JClass, JImplements, JOverride, add))
    FOR, FISH = int(SD.FORAGING), int(SD.FISHING)
    u = T57._uuid(61001)
    k = str(u)
    cm = [int(x) for x in SD.cumOf(FOR)]
    for n_, f_ in ((0, 1.0), (1, 0.8), (2, 0.64)):
        d = ST.dataK(k, u)
        ST.wr(d, FOR, cm[12] + 1)
        ST.wr(d, N + FOR, 9)
        del paid[:]
        br.put("rebirth:fn:count", _fn(JClass, JImplements, JOverride, lambda o, n_=n_: Integer(n_)))
        r = ST.payOwedK(k, u, FOR)
        want = [int(round(model(L) * f_)) for L in (10, 11, 12)]
        K.check(paid == want and int(d[N + FOR]) == 12 and r is not None and int(r[2]) == sum(want),
                "PAY levels 9 -> 12 at %d rebirth(s): pay at(10) / at(11) / at(12) x%.2f = %s: %s" % (n_, f_, want, paid))
    br.put("rebirth:fn:count", _fn(JClass, JImplements, JOverride, lambda o: Integer(0)))
    Props = JClass("java.util.Properties")
    p = Props()
    p.load(JClass("java.io.StringReader")("levelCoins=\n"))
    LC.read(p)
    d = ST.dataK(k, u)
    ST.wr(d, N + FOR, 9)
    del paid[:]
    ST.payOwedK(k, u, FOR)
    K.eq(paid, [1000, 1100, 1200], "PAY levelCoins empty: the old coinsPerLevel 100 x level")
    p = Props()
    p.load(JClass("java.io.StringReader")("levelCoins=1:0,100:0\n"))
    LC.read(p)
    ST.wr(d, N + FOR, 9)
    del paid[:]
    ST.payOwedK(k, u, FOR)
    K.check(not paid and int(d[N + FOR]) == 12, "PAY a 0 table: the levels count as paid, no coins")
    LC.read(Props())
    # the Stats page: "+N coins when you reach level ..." = the same number
    SP = J("StatsPage")
    nxt = [str(x) for x in SP.lines(u, FISH, 9, True)]
    fm = lambda n: str(SD.fmt(n))
    K.check(("+%s coins when you reach level 10" % fm(model(10))) in nxt, "PAY Stats page (Fishing 9, next): %s" % nxt)
    nb = [str(x) for x in SP.lines(u, int(SD.BEASTMASTERY), 49, True)]
    K.check(any(x == "+%s coins when you reach level 50" % fm(2800) for x in nb), "PAY Stats page (Beastmastery 49, next): %s" % nb)
    nm = [str(x) for x in SP.lines(u, int(SD.MINING), 89, True)]
    K.check(any(x == "+%s coins when you reach level 90" % fm(50500) for x in nm), "PAY Stats page (Mining 89, next): %s" % nm)
    K.save()


def run_pm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    M, Cfg = JClass(PKG + "SkMigP7"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    OLD = _old_defaults()
    NEW = str(Cfg.DEFAULTS)
    K.check("\nlevelCoins=" not in OLD and "\ncoinsPerLevel=100\n" in OLD and MARK_ID not in OLD, "PM the 0.4.60 jar's file: no levelCoins, coinsPerLevel=100")
    r = M.plan(JString(OLD))
    K.check(r is not None and _props(str(r[0])) == _props(NEW), "PM the 0.4.60 jar's default file -> exactly the 0.4.61 one (Properties)")
    K.eq([str(x) for x in r[1]], ["levelCoins", "(none)", LC_TEXT], "PM one change-log row (the line added; Undo)")
    K.check(bool(M.sameAfter(JString(OLD).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r)), "PM sameAfter: only levelCoins added")
    nb = str(r[0])
    K.check(nb.startswith(OLD) and nb.endswith("# " + MARK_ID + ": level-up coins follow the coin curve (levelCoins)\n") and str(r[3]) == "",
            "PM bytes: the old file untouched, the block appended, the marker last, no note")
    K.check(M.plan(r[0]) is None and M.plan(JString(NEW)) is None, "PM the marker: a second plan / a fresh file = null")
    hand = OLD.replace("\ncoinsPerLevel=100\n", "\ncoinsPerLevel=250\n")
    rh = M.plan(JString(hand))
    ph = _props(str(rh[0]))
    K.check(ph["levelCoins"] == "" and ph["coinsPerLevel"] == "250" and "coinsPerLevel=250 kept" in str(rh[3]) and [str(x) for x in rh[1]] == ["levelCoins", "(none)", ""]
            and bool(M.sameAfter(JString(hand).getBytes("ISO-8859-1"), JString(str(rh[0])).getBytes("ISO-8859-1"), rh)),
            "PM coinsPerLevel 250 (an admin's): levelCoins= EMPTY (their linear rule keeps paying) + note: %s" % str(rh[3])[:140])
    h0 = OLD.replace("\ncoinsPerLevel=100\n", "\ncoinsPerLevel = 100.0\n")
    K.check(_props(str(M.plan(JString(h0))[0]))["levelCoins"] == "", "PM coinsPerLevel '100.0' is not the exact default -> treated as an admin's (empty levelCoins)")
    nol = OLD.replace("\ncoinsPerLevel=100\n", "\n")
    K.eq(_props(str(M.plan(JString(nol))[0]))["levelCoins"], LC_TEXT, "PM no coinsPerLevel line (code default 100) -> the table")
    has = OLD + "levelCoins=1:5\n"
    rf = M.plan(JString(has))
    K.check(_props(str(rf[0]))["levelCoins"] == "1:5" and str(rf[0]).count("levelCoins=") == 1 and len(list(rf[1])) == 0,
            "PM a file that already has levelCoins keeps it (no row; the marker only)")
    crlf = OLD.replace("\n", "\r\n")
    rc = M.plan(JString(crlf))
    K.check(_props(str(rc[0])) == _props(NEW) and "\n" not in str(rc[0]).replace("\r\n", ""), "PM CRLF: same settings, every line ending CRLF")
    K.save()


def run_live61(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy61")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, M4, M8, M9, M7, LC = (J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"),
                                                                J("CurveP3Mig"), J("P3Mig"), J("P4Mig"), J("PlMigP8"), J("BmMigP8c"), J("SkMigP7"), J("LvCoins"))
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
        r["SkMigP7"] = str(M7.run())
        r["load"] = str(Cfg.load())
        return r
    before = _props(open(xp, encoding="latin-1").read())
    r1 = start()
    s1 = T53.snapd(lc)
    K.notes.append("LIVE61 start 1: SkMigP7: %s" % r1["SkMigP7"][:200])
    K.check("updated for 0.4.61" in r1["SkMigP7"], "LIVE61 start 1: SkMigP7 ran: %s" % r1["SkMigP7"][:160])
    after = _props(open(xp, encoding="latin-1").read())
    cpl = before.get("coinsPerLevel")
    want = LC_TEXT if cpl in (None, "100") else ""
    K.eq(after.get("levelCoins"), want, "LIVE61 the live copy: levelCoins = %s (live coinsPerLevel %s)" % ("the table" if want else "empty", cpl))
    K.check(int(LC.at(10)) == (60 if want else 100 * 10), "LIVE61 SkillCfg.load of the migrated copy: Lv 10 pays %s" % LC.at(10))
    other = sorted(k for k in set(before) | set(after) if after.get(k) != before.get(k) and k != "levelCoins")
    K.check(not other, "LIVE61 only levelCoins changed: %s" % other[:12])
    txt = open(xp, encoding="latin-1").read()
    K.check(txt.count(MARK_ID) == 1 and txt.count("\nlevelCoins=") == 1, "LIVE61 the marker once, one levelCoins line")
    cl = s1.get("config-changes.log", b"").decode("utf-8", "replace")
    K.check(cl.count("\tSkyySkills 0.4.61\t") == 1 and "levelCoins" in cl, "LIVE61 one change-log row (Undo in Server Setup -> Changes)")
    K.check(any(b"Balance P7 economy (SkyySkills" not in open(os.path.join(r_, f_), "rb").read() and b"Balance P8c" in open(os.path.join(r_, f_), "rb").read()
                for r_, _d, fs in os.walk(os.path.join(lc, "config-history")) for f_ in fs), "LIVE61 config-history holds the pre-P7 xp.properties")
    # saved player data untouched: every live profile loads and saves byte-identical keys
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
        Sto.install(kk, u, got)
        sp = Sto.snap(kk)
        new = dict((str(x), str(sp.getProperty(x))) for x in sp.stringPropertyNames())
        changed = sorted(x for x in set(old) & set(new) if old[x] != new[x])
        added = sorted(set(new) - set(old))
        if changed or set(old) - set(new) or not set(added) <= ZERO_SLOTS or any(new[x] != "0" for x in added):
            bad.append((fn, changed[:5], added))
    K.check(n >= 1 and not bad, "LIVE61 %d live profile file(s): no saved key changes (levels already paid stay paid); only the 0.4.60 slots a file lacked are added at 0: %s" % (n, bad[:3]))
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(all(s1.get(x) == s2.get(x) for x in set(s1) | set(s2)) and r2["SkMigP7"] == "", "LIVE61 start 2 changes nothing")
    K.save()


# checked by hand 2026-10-22 (first run): the members this round changes on purpose
EXPECT.update({'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
               'CurveP3Mig': ['~m run'], 'SkillCfg': ['~m load'], 'SkillStore': ['~m payLocked'], 'SkillXp': ['~m gain4'], 'SkyySkillsPlugin': ['~m setup'],
               'StatsPage': ['~m lines0']})

if __name__ == "__main__":
    phases = [("static", run_static), ("lc", run_lc), ("pay", run_pay), ("pm", run_pm), ("live61", run_live61)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
