"""Harness for SkyyExploration 0.3.3 (tools/exploration_0_3_3_patch.py): Balance P7 economy P7b - Loot Bag / supply drop coins on the zone
curve (5 level bands), airdrop.zoneMult, Wanderer + Cartographer (coins only), ExpP7Mig. Build first:
    python tools/exploration_0_3_3_patch.py && python SkyyExploration/build_skyyexploration_0.3.3.py
    python SkyyExploration/test_skyyexploration_0.3.3.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; two classes added; setup ExpP3Mig -> ExpP7Mig -> ExpCfg.load; ExpV3 is called only by
                LgCore's coin code (never by an XP path); every coin roll goes through LgCore.zoneMult
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.2 -> 0.3.3: + ExpP7Mig, ExpV3; only the planned members differ
  CFG  EXECUTED ExpCfg.load (fresh): the five bands, airdrop.zoneMult; zm5 (4 numbers = the 0.3.2 zones; bad -> default); check() takes 4 or 5;
       the Server Setup rows (coinZoneMult help, airdrop.zoneMult, the 4 Skill trees rows)
  COIN EXECUTED LgCore.loot (stand-in world, tools LgApi seam of 0.2.8): a tier I bag at Lv 10 / 19 / 20 / 39 / 40 / 59 / 60 / 79 / 80 / 150 pays
       100 x 1 / 5.2 / 36.8 / 130 / 466; a supply drop x the band, x1 with airdrop.zoneMult off; Wanderer rank 5 x1.2 (rank 9 = the 20 %
       ceiling; a Server Setup field change applies at once); Cartographer rank 3 = ~15 % a second coin find (its own reveal card), rank 0
       never, 100 % always; the spare-find coin roll uses the same band; no tree:fn:level = x1; loadV3 seeds trees.properties; tree:reads
  MIG  ExpP7Mig.plan / migrate: the 0.3.2 default file -> the 0.3.3 settings (+ airdrop.zoneMult only in a fresh file); an admin's 1,2,3,4
       kept + INFO; CRLF; History, one change-log row, start 2 nothing
  LIVE every one-time update (ExpLgMig, ExpNcMig, ExpP3Mig, ExpP7Mig) + ExpCfg.load on a scratch COPY of the live data, twice
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK
import skyybuild as B
import trees_v3_effects as V3E

_cmp = HK.run_compare
_argv = list(sys.argv)
_s = importlib.util.spec_from_file_location("test_skyyexploration_0_2_12", os.path.join(HERE, "test_skyyexploration_0.2.12.py"))
T212 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T212)          # its T28 (the stand-in world); it swaps HK.run_compare - put the kit's own back
HK.run_compare = _cmp
sys.argv[:] = _argv
T28 = T212.T28
import perfworld_kit as PW

VERSION, OLD = "0.3.3", "0.3.2"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyexploration_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyexploration_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "exploration_0_3_3_patch.py")
PKG = "com.skyy.explore."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "balp7b", "expl")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyExploration")
ZM = [1.0, 5.2, 36.8, 130.0, 466.0]
KEYS = ["Skill.Exploration.b1.r1a", "Skill.Exploration.b1.r3a"]
EXPECT = {}
ADDED = ["ExpP7Mig", "ExpV3"]


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def reset(J):
    J("CfgHist").DIR = None
    J("CfgRows").HOME = None
    J("CfgLog").FILE = None
    J("CfgLog").Q.clear()


def old_text():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "ExpCfg", loader=ld).DEFAULTS)


def _props(t):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(t))
    return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyExploration 0.3.3 - build script') and g.count('VERSION = "0.3.3"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 2 and "LG_CLASSES.append(p7mig)" in g and "LG_CLASSES.append(expv3)" in g, "S two classes added, written out")
    su = g[g.index("@PKG@.ExpP3Mig.migrate();"):]
    K.check(su.index("@PKG@.ExpP7Mig.migrate();") < su.index("@PKG@.ExpCfg.load();") < su.index("@PKG@.ExpV3.loadV3(base)") < su.index("@PKG@.ExpV3.reads(true)"),
            "S setup: ExpP3Mig -> ExpP7Mig -> ExpCfg.load -> ExpV3.loadV3 -> tree:reads")
    K.check("LG_COIN_ZM[" not in g.replace("zm[(z <= zm.length ? z : zm.length) - 1]", ""), "S every coin roll goes through LgCore.zoneMult")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    # who calls ExpV3: only LgCore's coin code (the XP paths never read the tree coin rows - Skyy's no-boost rule)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=False)
    cg = PW.calls(jar)
    users = sorted(m for m, cs in cg.items() if any(c.startswith(PKG + "ExpV3.") for c in cs) and not m.startswith("ExpV3."))
    K.check(set(users) <= {"LgCore.coinMult", "LgCore.loot", "SkyyExplorationPlugin.setup", "SkyyExplorationPlugin.shutdown"} and "LgCore.loot" in users and "LgCore.coinMult" in users,
            "S ExpV3 is used only by LgCore.coinMult / loot + setup / shutdown: %s" % users)
    xp = [m for m, cs in cg.items() if "ExpXp" in m or "ExpAward" in m or "ExpSkill.addXp" in m]
    K.check(not [m for m in xp if any(c.startswith(PKG + "ExpV3.") for c in cg[m])], "S no XP method reads ExpV3")
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg = J("ExpCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Paths = JClass("java.nio.file.Paths")
    d = os.path.join(scratch, "cfg")
    os.makedirs(d)
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    Cfg.load()
    K.eq([float(x) for x in Cfg.LG_COIN_ZM], ZM, "CFG a fresh file: luggage.coinZoneMult 1 / 5.2 / 36.8 / 130 / 466")
    K.check(bool(Cfg.AIR_ZM), "CFG airdrop.zoneMult true")
    t = open(os.path.join(d, "config.properties"), encoding="latin-1").read()
    K.check("\nluggage.coinZoneMult=1,5.2,36.8,130,466\n" in t and "\nairdrop.zoneMult=true\n" in t and str(J("ExpP7Mig").MARK) in t, "CFG the fresh file: both lines + the P7 marker")
    K.eq([float(x) for x in Cfg.zm5(JString("1,1.5,2,3"))], [1.0, 1.5, 2.0, 3.0], "CFG zm5: a 0.3.2 file's 4 numbers load as they are (fix 2: the 0.3.2 zones)")
    K.eq(str(Cfg.ZM4_SEEN), "1,1.5,2,3", "FIXB zm5 remembers the 4-number text it logged (the INFO line once per distinct text)")
    K.eq([float(x) for x in Cfg.zm5(JString("1,1.5,2,3"))], [1.0, 1.5, 2.0, 3.0], "FIXB zm5 the same 4 numbers again (a reload): same values, no new INFO line")
    K.eq([float(x) for x in Cfg.zm5(JString("2,4,6,8,10"))], [2.0, 4.0, 6.0, 8.0, 10.0], "CFG zm5: 5 numbers as they are")
    K.eq([float(x) for x in Cfg.zm5(JString("1,2,3"))], ZM, "CFG zm5: 3 numbers = WARN + the default")
    K.eq([float(x) for x in Cfg.zm5(JString("1,2,x,4"))], [1.0, 1.5, 2.0, 3.0], "CFG zm5: a bad 4-number list = the 0.3.2 default (4 numbers)")
    for v, ok in (("1,5.2,36.8,130,466", True), ("1,1.5,2,3", True), ("1,2,3", False), ("1,2,3,4,5,6", False), ("1,2,3,4,2000", False)):
        K.check((Cfg.check("luggage.coinZoneMult", v) is None) == ok, "CFG check luggage.coinZoneMult %r -> %s" % (v, Cfg.check("luggage.coinZoneMult", v)))
    Props = JClass("java.util.Properties")
    pp = Props()
    pp.setProperty("airdrop.zoneMult", "false")
    pp.setProperty("luggage.coinZoneMult", "1, 1.5, 2, 3")
    Cfg.apply(pp)
    K.check(not bool(Cfg.AIR_ZM) and [float(x) for x in Cfg.LG_COIN_ZM] == [1.0, 1.5, 2.0, 3.0], "CFG apply: airdrop.zoneMult false; a spaced 4-list (kept as 4: the 0.3.2 zones)")
    Cfg.apply(Props())
    K.check(bool(Cfg.AIR_ZM) and [float(x) for x in Cfg.LG_COIN_ZM] == ZM, "CFG apply: no lines = the defaults")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in J("CfgRows").header()[7])
    K.check(rows["luggage.coinZoneMult"][4] == "1,5.2,36.8,130,466" and "Five numbers" in rows["luggage.coinZoneMult"][10], "CFG row luggage.coinZoneMult: %s" % rows["luggage.coinZoneMult"][10])
    K.check(rows.get("airdrop.zoneMult", [""] * 5)[2:5] == ["airdrops", "bool", "true"], "CFG row airdrop.zoneMult (Magic Boxes, bool, true)")
    tr = [k for k in rows if k.startswith("tree.Exploration.")]
    K.eq(sorted(tr), sorted(r[0] for r in V3E.cfg_rows("SkyyExploration", "ExpV3", "Skyy_SkyyExploration/trees.properties", "trees")), "CFG the 4 Skill trees rows")
    K.save()


def run_coin(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JInt, JLong, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg, Core, Site, Eng, EIO, V3 = P("ExpCfg"), P("LgCore"), P("LgSite"), P("LgEng"), P("ExpIO"), P("ExpV3")
    Props, UUID, AL, Sys, Paths = JClass("java.util.Properties"), JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.lang.System"), JClass("java.nio.file.Paths")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Cfg.apply(Props())
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    EIO.BRIDGE = None
    state = {"placed": {}, "log": [], "ground": "Soil_Grass", "given": []}
    Eng.API = T28.sim(state)
    paid = []

    @JImplements("java.util.function.Function")
    class CoinAdd:
        @JOverride
        def apply(self, a):
            paid.append(int(a[1]))
            return JLong(1)
    br.put("coins:fn:add", CoinAdd())
    RANK = {KEYS[0]: 0, KEYS[1]: 0}

    @JImplements("java.util.function.Function")
    class TreeLv:
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer")(RANK.get(str(a[1]), 0))
    Dbl = JArray(JDouble)
    Cfg.LG_BAGS = Dbl([0.0, 0.0, 0.0, 0.0])
    Cfg.LG_XP = Dbl([0.0, 0.0, 0.0, 0.0])
    Cfg.LG_COIN_MIN = Dbl([100.0, 100.0, 100.0, 100.0])
    Cfg.LG_COIN_MAX = Dbl([100.0, 100.0, 100.0, 100.0])
    Cfg.AIR_BAGS, Cfg.AIR_XP, Cfg.AIR_COIN_MIN, Cfg.AIR_COIN_MAX = 0.0, 0, 200, 200
    Cfg.LG_VANILLA = False
    u = UUID.fromString("00000000-0000-4000-8000-0000000003c3")

    def claim(tier, lvl):
        s1 = Site.parse("1\t65\t1\t%d\t%d\t0\t10\t0\t10\t7\t" % (tier, lvl))
        cards = AL()
        del paid[:]
        got = str(Core.loot(None, None, None, None, u, s1, cards))
        return list(paid), [(str(c[0]), str(c[2])) for c in cards], got
    lvls = [10, 19, 20, 39, 40, 59, 60, 79, 80, 150]
    want = [100, 100, 520, 520, 3680, 3680, 13000, 13000, 46600, 46600]
    K.eq([claim(1, L)[0] for L in lvls], [[w] for w in want], "COIN a tier I bag (100 coins) at Lv %s pays x the band 1 / 5.2 / 36.8 / 130 / 466" % lvls)
    K.eq([int(Core.coinZone(L)) for L in (1, 19, 20, 39, 40, 59, 60, 79, 80, 100, 500)], [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5], "COIN coinZone bands")
    K.eq([int(Core.zoneOf(L)) for L in (19, 25, 44, 80)], [1, 2, 3, 4], "COIN zoneOf (tables / tiers / XP) unchanged")
    K.eq(claim(5, 45)[0], [7360], "COIN a supply drop (200) at Lv 45 x36.8")
    Cfg.AIR_ZM = False
    K.eq((claim(5, 45)[0], claim(1, 45)[0]), ([200], [3680]), "COIN airdrop.zoneMult off: the supply drop x1, the bag still x36.8")
    Cfg.AIR_ZM = True
    Cfg.LG_COIN_ZM = Dbl([1.0, 1.5, 2.0, 3.0])
    K.eq(claim(1, 90)[0], [300], "COIN a 4-number zone list in memory: Lv 90 uses its last number (no index error)")
    # fix 2 (critic 2): an admin's 4-number line pays on the 0.3.2 zones (Lv 1-19 / 20-29 / 30-44 / 45+), not the new bands
    Cfg.LG_COIN_ZM = Cfg.zm5(JString("1,2,4,8"))
    K.eq([claim(1, L)[0][0] for L in (19, 20, 29, 30, 39, 44, 45, 59, 79, 90)], [100, 200, 200, 400, 400, 400, 800, 800, 800, 800],
         "FIX2 a 4-number line 1,2,4,8: Lv 19/20/29/30/39/44/45/59/79/90 pay on the 0.3.2 zones")
    Cfg.LG_COIN_ZM = Cfg.zm5(JString("1,2,4,8,16"))
    K.eq([claim(1, L)[0][0] for L in (19, 20, 39, 40, 60, 80)], [100, 200, 200, 400, 800, 1600], "FIX2 a 5-number line uses the new bands")
    Cfg.apply(Props())
    Cfg.LG_BAGS, Cfg.LG_XP, Cfg.LG_VANILLA = Dbl([0.0] * 4), Dbl([0.0] * 4), False
    Cfg.LG_COIN_MIN, Cfg.LG_COIN_MAX = Dbl([100.0] * 4), Dbl([100.0] * 4)
    Cfg.AIR_BAGS, Cfg.AIR_XP, Cfg.AIR_COIN_MIN, Cfg.AIR_COIN_MAX = 0.0, 0, 200, 200
    # the tree rows: no SkyyTrees = x1; Wanderer 5 = x1.2; Cartographer
    K.eq(claim(1, 10)[0], [100], "COIN no tree:fn:level: no tree bonus")
    br.put("tree:fn:level", TreeLv())
    RANK[KEYS[0]] = 5
    K.eq(claim(1, 30)[0], [624], "COIN Wanderer rank 5: +20 % (520 -> 624)")
    RANK[KEYS[0]] = 9
    K.eq(claim(1, 30)[0], [624], "COIN Wanderer rank 9 (over the max): the 20 % ceiling holds")
    V3.V3P0 = 10.0
    V3.V3X0 = 100.0
    K.eq(claim(1, 30)[0], [988], "COIN a Server Setup change (10 % a rank, ceiling 100 %) applies at once: rank 9 = +90 %")
    d = os.path.join(scratch, "coin")
    os.makedirs(d)
    r0 = str(V3.loadV3(Paths.get(d)))
    K.check(open(os.path.join(d, "trees.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyExploration") and "read" in r0
            and abs(float(V3.V3P0) - 4.0) < 1e-9 and abs(float(V3.V3X0) - 20.0) < 1e-9, "COIN loadV3 seeds trees.properties and puts the built-in numbers back: %s" % r0)
    RANK[KEYS[0]] = 0
    RANK[KEYS[1]] = 3
    import random
    n2, N = 0, 4000
    for _ in range(N):
        c, cards, got = claim(1, 10)
        if len(c) == 2:
            n2 += 1
            if n2 == 1:
                K.check(c == [100, 100] and cards[-1] == ("Ingredient_Bar_Gold", "Cartographer") and "(Cartographer)" in got,
                        "COIN Cartographer: a second coin find of the same roll, its own reveal card + chat words: %s / %s" % (cards, got))
        elif len(c) != 1:
            K.check(False, "COIN a claim paid %s" % c)
    K.check(0.13 <= n2 / float(N) <= 0.17, "COIN Cartographer rank 3: a second coin find in %.1f %% of %d claims (want ~15 %%)" % (100.0 * n2 / N, N))
    RANK[KEYS[1]] = 0
    K.check(all(len(claim(1, 10)[0]) == 1 for _ in range(300)), "COIN Cartographer rank 0: never a second find")
    RANK[KEYS[1]] = 1
    V3.V3P1, V3.V3X1 = 100.0, 100.0
    K.check(all(claim(5, 85)[0] == [93200, 93200] for _ in range(50)), "COIN Cartographer at 100 %: a supply drop (Lv 85, x466) always pays twice")
    RANK[KEYS[0]] = 5
    K.eq(claim(1, 85)[0], [55920, 55920], "COIN Wanderer + Cartographer together: both rolls x1.2 (46,600 -> 55,920)")
    # the spare-find coin roll (a vanilla list with only gear) uses the same band x Wanderer
    V3.V3P1, V3.V3X1 = 5.0, 15.0
    RANK[KEYS[1]] = 0
    K.check(int(V3.N_BOOST) > 0 and int(V3.N_SECOND) > 0 and "Wanderer" in str(V3.text()), "COIN counters + text(): %s" % V3.text())
    V3.reads(True)
    K.eq(str(br.get("tree:reads:SkyyExploration")), V3E.reads_csv("SkyyExploration"), "COIN reads(true): tree:reads:SkyyExploration = the 2 keys")
    V3.reads(False)
    K.check(br.get("tree:reads:SkyyExploration") is None, "COIN reads(false) removes our value")
    br.put("tree:reads:SkyyExploration", JString("someone else"))
    V3.reads(False)
    K.check(str(br.get("tree:reads:SkyyExploration")) == "someone else", "COIN reads(false) never removes another value")

    def boom(a):
        raise RuntimeError("x")

    @JImplements("java.util.function.Function")
    class Boom:
        @JOverride
        def apply(self, a):
            raise RuntimeError("x")
    br.put("tree:fn:level", Boom())
    K.eq(claim(1, 10)[0], [100], "COIN a throwing tree:fn:level = no bonus (logged once)")
    Eng.API = None
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, M = J("ExpCfg"), J("ExpP7Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Paths = JClass("java.nio.file.Paths")
    OLDT = old_text()
    NEWT = str(Cfg.DEFAULTS)
    pr = M.plan(JString(OLDT))
    pn, pw = _props(str(pr[0])), _props(NEWT)
    pw.pop("airdrop.zoneMult")
    K.check(pn == pw, "MIG ExpP7Mig.plan(the 0.3.2 default file) = the 0.3.3 settings (airdrop.zoneMult only in a fresh file)")
    K.eq([str(x) for x in pr[1]], ["luggage.coinZoneMult", "1,1.5,2,3", "1,5.2,36.8,130,466"], "MIG one change-log row (Undo)")
    K.check("coin zone multipliers Lv 1-19/20-39/40-59/60-79/80+" in str(pr[0]) and "coin zone multipliers 1-4" not in str(pr[0]), "MIG the help comment rewritten 1:1")
    K.check(M.plan(pr[0]) is None and M.plan(JString(NEWT)) is None, "MIG the marker: a second plan / a fresh file = null")
    hand = OLDT.replace("\nluggage.coinZoneMult=1,1.5,2,3\n", "\nluggage.coinZoneMult=1,2,3,4\n")
    p2 = M.plan(JString(hand))
    K.check("\nluggage.coinZoneMult=1,2,3,4\n" in str(p2[0]) and "kept" in str(p2[3]) and len(p2[1]) == 0, "MIG an admin's 1,2,3,4 kept + INFO: %s" % str(p2[3])[:120])
    sp = OLDT.replace("\nluggage.coinZoneMult=1,1.5,2,3\n", "\nluggage.coinZoneMult=1, 1.5, 2, 3\n")
    K.check("\nluggage.coinZoneMult=1,5.2,36.8,130,466\n" in str(M.plan(JString(sp))[0]), "MIG the spaced old default moves too")
    pr3 = M.plan(JString(OLDT.replace("\n", "\r\n")))
    K.check(str(pr3[0]) == str(pr[0]).replace("\n", "\r\n"), "MIG CRLF kept")
    for tag, txt in (("lf", OLDT), ("crlf", OLDT.replace("\n", "\r\n"))):
        dm = os.path.join(scratch, "mig", tag)
        os.makedirs(dm)
        open(os.path.join(dm, "config.properties"), "wb").write(txt.encode("latin-1"))
        Cfg.FILE = Paths.get(os.path.join(dm, "config.properties"))
        reset(J)
        s0 = snapd(dm)
        r1 = str(M.migrate())
        s1 = snapd(dm)
        K.check(s1["config.properties"].decode("latin-1") == (str(pr[0]) if tag == "lf" else str(pr3[0])), "MIG migrate %s: the planned file" % tag)
        K.check(sum(1 for k in s1 if k.startswith("config-history/") and s1[k] == s0["config.properties"]) == 1, "MIG migrate %s: History" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("SkyyExploration 0.3.3") == 1 and "\tluggage.coinZoneMult\t1,1.5,2,3\t1,5.2,36.8,130,466\tok" in lg, "MIG migrate %s: the change-log row" % tag)
        reset(J)
        K.check(str(M.migrate()) == "" and snapd(dm) == s1, "MIG migrate %s: start 2 nothing" % tag)
        Cfg.load()
        K.eq([float(x) for x in Cfg.LG_COIN_ZM], ZM, "MIG migrate %s: the migrated file pays the curve bands" % tag)
        K.check("0.3.3" in r1, "MIG migrate %s INFO: %s" % (tag, r1[:120]))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg = J("ExpCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Cfg.FILE = JClass("java.nio.file.Paths").get(os.path.join(home, "config.properties"))

    def start():
        reset(J)
        rs = [str(J(m).migrate()) for m in ("ExpLgMig", "ExpNcMig", "ExpP3Mig", "ExpP7Mig")]
        Cfg.load()
        return rs
    s0 = snapd(home)
    r1 = start()
    s1 = snapd(home)
    r2 = start()
    s2 = snapd(home)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "config.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch), "LIVE start 1 changes only the config + History: %s" % ch)
    po, pn = _props(s0["config.properties"].decode("latin-1")), _props(s1["config.properties"].decode("latin-1"))
    dk = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(dk in ([], ["luggage.coinZoneMult"]), "LIVE only luggage.coinZoneMult may change: %s" % dk)
    K.check(s1 == s2 and r2[3] == "", "LIVE start 2 changes nothing")
    K.check([float(x) for x in Cfg.LG_COIN_ZM] == ZM or "kept" in r1[3], "LIVE the live config pays the curve bands (or an admin value was kept): %s" % r1[3][:200])
    K.notes.append("LIVE: %s" % r1[3][:300])
    K.save()


EXPECT.update({   # checked by hand 2026-10-22: the kit's second file (trees.properties: CfgFile.init, CfgRows DL1 / defLines), the version texts
                 # (CfgFn, CfgRows header, the migrations' inlined WHO), ExpCfg's bands / airdrop.zoneMult / zm5 / check / LIVE map, LgCore's coin code,
                 # setup (ExpP7Mig, loadV3, reads) + shutdown (reads false)
    "CfgFile": ["~<clinit>", "~m init"], "CfgFn": ["~m opExport"], "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],
    "ExpCfg": ["+f AIR_ZM", "+f ZM4_SEEN", "+m zm5", "~<clinit>", "~m apply", "~m check", "~m live", "~m load"], "ExpLgMig": ["~m logLine", "~m migrate"],
    "ExpNcMig": ["~m logLine", "~m migrate"], "ExpP3Mig": ["~m migrate"], "LgCore": ["+m coinMult", "+m coinZone", "+m zoneMult", "~m loot"],
    "SkyyExplorationPlugin": ["~m setup", "~m shutdown"]})

if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("cfg", run_cfg), ("coin", run_coin), ("mig", run_mig), ("live", run_live)], script=__file__,
           live=(LIVE, "Skyy_SkyyExploration"))
