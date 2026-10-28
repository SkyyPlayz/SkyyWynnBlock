"""Harness for SkyyTrees 0.6.6 (Wide Sowing plants free in Creative; tools/trees_0_6_6_patch.py).
Build first:
    python tools/trees_0_6_6_patch.py && python SkyyTrees/build_skyytrees_0.6.6.py
    python SkyyTrees/test_skyytrees_0.6.6.py [--keep] [--expect-dump]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.5 -> 0.6.6 / engine-access audit around them):
  static    the generated script = the patch's output (re-run to identical bytes), 0.6.5's patch still regenerates 0.6.5 byte for byte, header /
            version, no new class / system / command, line endings kept
  creative  EXECUTED TreeSeed (TEST map, real TreeSk ranks, fake SkyySacks Functions) with TEST_MODE: Creative = the 8 / 24 cells sown with
            NO hand seed taken and NO Pocket call (take / put / commit) even with an empty hand; a refused cell costs nothing and
            REFUSE_MAX still stops; FREE counts; GameMode unknown (-1) = no area plant; Adventure (0) = hand first then Pocket (0.6.5)
  g64 / data / sow / jar   0.6.5's phases on the 0.6.6 jar (Adventure behaviour unchanged - sow runs with TEST_MODE 0, the default)
  path / mig / integ / farm / sap / live   the older EXEC phases on the 0.6.6 jar (unchanged behaviour)
NOT COVERED (UNVERIFIED in game): TreeSeed.creative on a real Player (getGameMode) and BlockPlaceUtils.placeBlock with a fresh stack in
Creative - compiled + -Xverify:all + engine-access audit + member probe only.
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.6.6"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "trees066", "trees")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_5", os.path.join(HERE, "test_skyytrees_0.6.5.py"))
T65 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T65)
sys.argv[:] = _argv
T64, T63, T60 = T65.T64, T65.T63, T65.T60

PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.5.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.5.py")
PATCH = os.path.join(TOOLS, "trees_0_6_6_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T60, T63, T64, T65):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
T60.VERSION = VERSION
SOW_KEY = T65.SOW_KEY
EXPECT = {   # checked 2026-10-27 (the class compare 0.6.5 -> 0.6.6): the version strings (CfgFn / CfgRows / SkyyTreesPlugin / TreeCfg) and
    # TreeSeed's Creative path + TreeSeedTask.cr - nothing else
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['~m load'],
    'TreeSeed': ['+f FREE', '+f TEST_MODE', '+m creative', '~<clinit>', '~m counts', '~m one', '~m plant'],
    'TreeSeedTask': ['+f cr'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1 = T65.U1


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.6 - build script') and g.count('VERSION = "0.6.6"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass("), "S no new command / system / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_5_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_creative(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T, br, d0 = T65._env(scratch, "cr")
    UUID, Long, HashMap, HashSet, ArrayList = (JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.util.HashMap"),
                                               JClass("java.util.HashSet"), JClass("java.util.ArrayList"))
    St, Sd = J("TreeStore"), J("TreeSeed")
    u = UUID.fromString(U1)
    d = St.data(u)
    x = T["UKEY"].index(SOW_KEY)
    K.eq(int(Sd.TEST_MODE), 0, "CR TEST_MODE defaults to 0 (Adventure) - the 0.6.5 sow phase runs unchanged")
    POCK = {"n": 0}
    CALLS = []

    def take(a):
        CALLS.append(("take", str(a[1]), int(a[2])))
        g = min(POCK["n"], int(a[2]))
        POCK["n"] -= g
        return Long(g)

    def put(a):
        CALLS.append(("put", str(a[1]), int(a[2])))
        POCK["n"] += int(a[2])
        return Long(int(a[2]))

    def commit(a):
        CALLS.append(("commit", str(a[1]), int(a[2])))
        return Long(int(a[2]))
    br.put("sacks:fn:take", T60._fn(JImplements, JOverride, take))
    br.put("sacks:fn:put", T60._fn(JImplements, JOverride, put))
    br.put("sacks:fn:commit", T60._fn(JImplements, JOverride, commit))
    CY = 64

    def field(r=2):
        m = HashMap()
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                m.put("%d|%d|%d" % (dx, CY - 1, dz), "Soil_Dirt_Tilled")
        m.put("0|%d|0" % CY, "Plant_Crop_Wheat_Block")
        return m

    def go(mode, hand=3, pocket=9, deny=(), rank=1):
        d.rk[x] = rank
        POCK["n"] = pocket
        del CALLS[:]
        Sd.TEST_MODE = mode
        Sd.TEST_BLOCKS = field()
        Sd.TEST_HAND = jpype.JArray(jpype.JInt)([hand])
        ds = HashSet()
        for c in deny:
            ds.add(c)
        Sd.TEST_DENY = ds
        lg = ArrayList()
        Sd.TEST_LOG = lg
        p0, f0 = int(Sd.PLANTED), int(Sd.FREE)
        r = int(Sd.onPlace0(u, None, None, "w", "Plant_Seeds_Wheat", 0, CY, 0))
        return r, [str(s) for s in lg], int(Sd.PLANTED) - p0, int(Sd.TEST_HAND[0]), int(Sd.FREE) - f0, Sd.TEST_BLOCKS
    # Creative, empty hand, full Pocket: 8 cells, no Pocket call at all, Pocket untouched
    r, lg, n, h, f, m = go(1, hand=0, pocket=9)
    K.check(n == 8 and f == 8 and POCK["n"] == 9 and CALLS == [], "CR Creative, empty hand: the 3x3 sown free - no Pocket take / commit (n %d free %d pocket %d calls %s)" % (n, f, POCK["n"], CALLS))
    K.eq([s.split(" ")[0] for s in lg], ["creative"] * 8, "CR every cell logged creative")
    K.check(all(str(m.get("%d|%d|%d" % (dx, CY, dz))) == "Plant_Crop_Wheat_Block" for dx in (-1, 0, 1) for dz in (-1, 0, 1)), "CR every cell holds the wheat crop")
    # Creative with seeds in hand: the hand stack is never taken from
    r, lg, n, h, f, m = go(1, hand=3, pocket=0)
    K.check(n == 8 and h == 3 and CALLS == [], "CR Creative, 3 in hand: 8 cells, the hand keeps its 3, no Pocket call (hand %d)" % h)
    # Creative rank 2 = 5x5, still free
    r, lg, n, h, f, m = go(1, hand=0, pocket=0, rank=2)
    K.check(n == 24 and f == 24 and CALLS == [], "CR Creative rank 2: the 5x5 (24) sown free with nothing in hand or Pocket")
    # Creative refusals: skipped, nothing put back (nothing was taken); REFUSE_MAX still stops
    r, lg, n, h, f, m = go(1, hand=0, pocket=9, deny=["-1|%d|-1" % CY, "0|%d|1" % CY])
    K.check(n == 6 and CALLS == [] and POCK["n"] == 9 and lg.count("refused -1 %d -1" % CY) == 1, "CR Creative refused cells cost nothing: %s" % lg)
    deny = ["%d|%d|%d" % (dx, CY, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)]
    r, lg, n, h, f, m = go(1, hand=0, deny=deny)
    K.check(n == 0 and len(lg) == int(Sd.REFUSE_MAX) and CALLS == [], "CR Creative: REFUSE_MAX refusals still stop the planting")
    # GameMode unknown: no area plant, nothing taken
    r, lg, n, h, f, m = go(-1, hand=3, pocket=9)
    K.check(n == 0 and lg == [] and h == 3 and CALLS == [] and POCK["n"] == 9, "CR GameMode unknown = no area plant, nothing taken")
    # Adventure: 0.6.5 exactly (3 from the hand, then 5 from the Pocket: take -> commit)
    r, lg, n, h, f, m = go(0, hand=3, pocket=9)
    K.check(n == 8 and f == 0 and h == 0 and POCK["n"] == 4, "CR Adventure: hand first then Pocket (n %d hand %d pocket %d)" % (n, h, POCK["n"]))
    K.eq([s.split(" ")[0] for s in lg], ["hand"] * 3 + ["pocket"] * 5, "CR Adventure log = 0.6.5's")
    K.eq(CALLS, [("take", "Plant_Seeds_Wheat", 1), ("commit", "Plant_Seeds_Wheat", 1)] * 5, "CR Adventure Pocket calls = 0.6.5's")
    K.check("free in Creative" in str(Sd.counts()), "CR the counts line names the Creative cells: %s" % Sd.counts())
    K.check(Sd.ACTIVE.isEmpty(), "CR ACTIVE is empty after every run")
    Sd.TEST_MODE = 0
    for fl in ("TEST_BLOCKS", "TEST_HAND", "TEST_DENY", "TEST_LOG"):
        setattr(Sd, fl, None)
    K.save()
    sys.stdout.flush()
    os._exit(0)


HK.run_compare = T60._compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("creative", run_creative), ("g64", T65.run_g64), ("data", T65.run_data), ("sow", T65.run_sow),
                   ("jar", T65.run_jar), ("path", T64.run_path), ("mig", T64.run_mig), ("integ", T64.run_integ),
                   ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
