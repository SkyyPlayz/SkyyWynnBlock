"""Harness for SkyyTrees 0.6.5 (Wide Sowing = AOE seed bags, a Farming tree node SkyyTrees applies itself; tools/trees_0_6_5_patch.py).
Build first:
    python tools/trees_0_6_5_patch.py && python SkyyTrees/build_skyytrees_0.6.5.py
    python SkyyTrees/test_skyytrees_0.6.5.py [--keep] [--expect-dump]
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.4 -> 0.6.5 / engine-access audit around them):
  static  the generated script = the patch's output (re-run to identical bytes), 0.6.4's patch still regenerates 0.6.4 byte for byte, header /
          version, + 3 classes + 1 system (TreeSeedSys) and no command, line endings kept, tools/trees_v3_data.py + trees_v3_effects.py
          untouched (git: no diff - every other build reads the tables unchanged)
  g64     the 0.6.4 jar's TreeV3 gate tables (GATES / ROWCAP) dumped for "data"
  data    EXECUTED on the 0.6.5 jar: Wide Sowing = Skill.Farming.b1.r2c in Farming branch 1 row 2 (3 upgrades there now), 2 ranks, no hook,
          live only while tree:reads:SkyyTrees lists it (TreeSk.READS does), the gate tables = 0.6.4's (no gate moves), TreeSk's last row
          (effect sow, per 1, most 2), the seed table (38 seed bags incl. 14 Eternal, crops / soil groups, no sapling / Mushroom), soil
          lines (tilled + planters; crystal soil)
  sow     EXECUTED TreeSeed (TEST map instead of a world, real TreeSk ranks, fake SkyySacks take / put / commit Functions):
          rank 0 = nothing; rank 1 = the 8 cells of the 3x3 (nearest ring), only air above the seed's soil (stone / grass / a crop / another
          height skipped), hand stack first then the Pocket Dimension (take -> commit), out of both = stop; a refused cell (protection)
          is skipped and its Pocket seed put back; REFUSE_MAX refusals stop; a hand plant that did not land = nothing; rank 2 = 5x5 (24);
          the Server Setup rows (most 1 -> 3x3; per 9 -> the hard cap 4); Eternal bags plant Eternal crops; crystal seeds only on crystal
          soil; our own plants never chain (ACTIVE); profile:busy = nothing; a non-seed / sapling = nothing; the Tree bonus line
  jar     the Wide Sowing icon item (64x64 PNG = the build's composite, item json, lang name), no other non-class entry but map pictures
  path / mig / integ   0.6.4's EXEC phases on the 0.6.5 jar (class trees unchanged)
  farm / sap  0.6.3's EXEC phases on the 0.6.5 jar (unchanged behaviour)
  live    start twice on a scratch COPY of the live Skyy_SkyyTrees (+ Skyy_SkyyClasses): every migration in setup's order, every file
          reads, start 2 changes nothing, every player x layout map painted with shipped pictures
NOT COVERED (UNVERIFIED in game): TreeSeedSys.handle (needs a real PlaceBlockEvent) and the real-world half of TreeSeed (famAt in a loaded
world, BlockPlaceUtils.placeBlock taking the seed from the hand slot, SkyyIslands / SkyyZones / SkyyShards refusing a cell, SkyySacks'
real take / commit / put) - compiled + -Xverify:all + engine-access audit + member probe only.
"""
import os, sys, json, subprocess, importlib.util, zipfile, re, shutil, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "aoeseed", "trees")]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_4", os.path.join(HERE, "test_skyytrees_0.6.4.py"))
T64 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T64)
sys.argv[:] = _argv
T63, T60 = T64.T63, T64.T60

VERSION = "0.6.5"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.4.jar")
CJAR = T64.CJAR
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.4.py")
PATCH = os.path.join(TOOLS, "trees_0_6_5_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T60, T63, T64):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
T60.VERSION = VERSION
SOW_KEY = "Skill.Farming.b1.r2c"
ICON = "Skyy_NodeIcon_Farming_B1R2c"
EXPECT = {   # checked 2026-10-25 (the class compare 0.6.4 -> 0.6.5 on the jars without the map / icon / lang entries): the table classes
    # (TreeV3 / TreeMap / TreeData / TreeV3Mig / TreePage sizes and inlined counts - one more upgrade, one more icon, the Gathering pin),
    # TreeSk's new row (V3P29 / V3X29, the reader list), the kit's default tree-effects.properties text (CfgFile / CfgRows), the version
    # strings (CfgFn / SkyyTreesPlugin / TreeCfg) and setup's new registerSystem; + the 3 new classes (ADDED)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['~m load'],
    'TreeData': ['~c '],
    'TreeMap': ['~<clinit>', '~m cand', '~m nodeRow', '~m nodeTv', '~m paint', '~m tex', '~m texRespec'],
    'TreePage': ['~m abClick'],
    'TreeSk': ['+f V3P29', '+f V3X29', '~<clinit>', '~m loadV3', '~m reads', '~m v3most', '~m v3per'],
    'TreeV3': ['~<clinit>', '~m buyText', '~m cellSub', '~m count', '~m detCost', '~m detHow', '~m detName', '~m detNeed', '~m detNext', '~m detNow', '~m detState', '~m effText', '~m fxLive', '~m fxNow', '~m live', '~m pathLocked', '~m r3bLive', '~m ustate'],
    'TreeV3Mig': ['~m readV3', '~m writeV3'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["TreeSeed", "TreeSeedSys", "TreeSeedTask"]
U1 = "65656565-0000-0000-0000-000000000001"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.5 - build script') and g.count('VERSION = "0.6.5"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand("), "S no new command")
    K.check(g.count("registerSystem(") == o.count("registerSystem(") + 1 and "registerSystem(new @PKG@.TreeSeedSys())" in g, "S + 1 system (TreeSeedSys)")
    K.check(g.count("makeClass(") == o.count("makeClass(") + 3, "S + 3 classes (TreeSeedTask, TreeSeed, TreeSeedSys)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_4_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    p = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "tools/trees_v3_data.py", "tools/trees_v3_effects.py"], cwd=ROOT)
    K.check(p.returncode == 0, "S tools/trees_v3_data.py + trees_v3_effects.py are untouched (the node lives in this build only)")
    K.save()


def run_g64(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=True)
    from jpype import JClass
    V = JClass(PKG + "TreeV3")
    d = {"GATES": [int(x) for x in V.GATES], "ROWCAP": [int(x) for x in V.ROWCAP], "TNAME": [str(x) for x in V.TNAME], "UKEY": [str(x) for x in V.UKEY]}
    json.dump(d, open(os.path.join(scratch, "g64-gates.json"), "w"))
    K.check(SOW_KEY not in d["UKEY"], "G the 0.6.4 jar has no Wide Sowing")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def _env(scratch, tag):
    from jpype import JClass, JImplements, JOverride
    E, J, V, T, br, d0 = T64._env(scratch, tag, [])
    return E, J, V, T, br, d0


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E, J, V, T, br, d0 = _env(scratch, "da")
    Sk, Sd = J("TreeSk"), J("TreeSeed")
    g64 = json.load(open(os.path.join(scratch, "g64-gates.json")))
    K.check(SOW_KEY in T["UKEY"], "DA Wide Sowing is an upgrade")
    x = T["UKEY"].index(SOW_KEY)
    fi = T["TNAME"].index("Farming")
    row = T["UROW"][x]
    K.check(T["UT"][x] == fi and T["BN"][T["RB"][row]] == 1 and T["RNUM"][row] == 2 and T["UMAX"][x] == 2 and T["UHK"][x] == 0 and T["UCOST"][x] == 1,
            "DA Farming branch 1 (Harvester) row 2, 2 ranks of 1 point, no hook (applier row)")
    K.eq(T["UNAME"][x], "Wide Sowing", "DA its name")
    same = [T["UNAME"][u] for u in range(T["NU"]) if T["UROW"][u] == row]
    K.eq(same, ["Wide Sweep", "Swift Sweep", "Wide Sowing"], "DA row 2 holds Wide Sweep, Swift Sweep, Wide Sowing")
    K.check("3x3" in str(V.UTEXT[x]) and "5x5" in str(V.UTEXT[x]), "DA its text names 3x3 / 5x5: %s" % V.UTEXT[x])
    K.check(bool(V.live(x)), "DA live while tree:reads:SkyyTrees lists it (TreeSk.reads)")
    rd = str(br.get("tree:reads:SkyyTrees"))
    K.check(SOW_KEY in rd.split(","), "DA tree:reads:SkyyTrees names it")
    Sk.reads(False)
    K.check(not bool(V.live(x)), "DA without the reader list it is coming soon (the R3b contract)")
    Sk.reads(True)
    K.eq([int(v) for v in V.GATES], g64["GATES"], "DA the row gates = 0.6.4's (no gate moves)")
    K.eq([int(v) for v in V.ROWCAP], g64["ROWCAP"], "DA the row-above caps = 0.6.4's")
    K.eq([k for k in T["UKEY"] if k not in g64["UKEY"]], [SOW_KEY], "DA the only new upgrade key")
    keys = [str(k) for k in Sk.KEY]
    effs = [str(e) for e in Sk.EFF]
    K.check(keys[-1] == SOW_KEY and effs[-1] == "sow" and effs.count("sow") == 1, "DA TreeSk's last row = Wide Sowing, effect sow")
    i = len(keys) - 1
    K.check(abs(float(Sk.v3per(i)) - 1.0) < 1e-9 and abs(float(Sk.v3most(i)) - 2.0) < 1e-9, "DA built-in numbers: +1 radius a rank, most 2")
    # fixer (fidelity critic 2): the two Server Setup rows say "Radius", take only 0..4 (= TreeSeed.RMAX) and explain 3x3 / 5x5 / the cap
    CR = JClass(PKG + "CfgRows")
    ck = [str(k) for k in CR.KEYS]
    sr = [ck.index("tree.Farming.b1.r2c.sow.per"), ck.index("tree.Farming.b1.r2c.sow.max")]
    K.eq([str(CR.LABELS[j]) for j in sr], ["Farming Wide Sowing Radius a rank", "Farming Wide Sowing Radius most"], "DA FIX the Server Setup row labels say Radius")
    K.eq([(str(CR.MINS[j]), str(CR.MAXS[j]), str(CR.DEFS[j])) for j in sr], [("0", "4", "1"), ("0", "4", "2")], "DA FIX the rows take 0..4 (defaults 1 / 2)")
    K.check(int(Sd.RMAX) == 4, "DA FIX the row bound 4 = TreeSeed.RMAX")
    K.check(all("3x3" in str(CR.HELPS[j]) and "5x5" in str(CR.HELPS[j]) and "9x9" in str(CR.HELPS[j]) and "radius" in str(CR.HELPS[j]) for j in sr),
            "DA FIX the hints say radius, 3x3 / 5x5 and the 9x9 cap: %s" % [str(CR.HELPS[j]) for j in sr])
    K.check(not [str(CR.LABELS[j]) for j in range(len(ck)) if "Wide Sowing Area" in str(CR.LABELS[j])], "DA FIX no row says Wide Sowing Area")
    seeds = [str(s) for s in Sd.SEED]
    crops = [str(c) for c in Sd.CROP]
    K.check(len(seeds) == 38 and seeds == sorted(seeds) and sum(1 for s in seeds if s.endswith("_Eternal")) == 14, "DA 38 seed bags (14 Eternal), sorted")
    K.check(all(c.startswith("Plant_Crop_") for c in crops) and crops[seeds.index("Plant_Seeds_Wheat")] == "Plant_Crop_Wheat_Block"
            and crops[seeds.index("Plant_Seeds_Wheat_Eternal")] == "Plant_Crop_Wheat_Block_Eternal" and crops[seeds.index("Plant_Seeds_Mana2")] == "Plant_Crop_Mana2_Block",
            "DA every seed plants its crop (Eternal -> the Eternal crop)")
    K.check(not [s for s in seeds if s in ("Plant_Seeds_Oak", "Plant_Seeds_Mushroom", "Plant_Seeds_Sunflower", "Plant_Seeds_Test_Tree", "Plant_Seeds_Pine")],
            "DA no sapling / tree seed, no Mushroom spores, no Sunflower / test seeds")
    soil = [str(s) for s in Sd.SOIL]
    K.check("0|Soil_Dirt_Tilled" in soil and "0|Furniture_Village_Planter" in soil and "1|Soil_Dirt_Crystal" in soil and "0|Soil_Dirt" not in soil and soil == sorted(soil),
            "DA soil lines: tilled soil + planters / crystal soil (sorted): %s" % soil)
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_sow(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E, J, V, T, br, d0 = _env(scratch, "so")
    UUID, Long, HashMap, HashSet, ArrayList = (JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.util.HashMap"),
                                               JClass("java.util.HashSet"), JClass("java.util.ArrayList"))
    St, Sk, Sd, Msg = J("TreeStore"), J("TreeSk"), J("TreeSeed"), J("TreeMsg")
    u = UUID.fromString(U1)
    d = St.data(u)
    x = T["UKEY"].index(SOW_KEY)
    si = int(Sd.seedIdx("Plant_Seeds_Wheat"))
    sie = int(Sd.seedIdx("Plant_Seeds_Wheat_Eternal"))
    sic = int(Sd.seedIdx("Plant_Seeds_Mana1"))
    K.check(si >= 0 and sie >= 0 and sic >= 0 and int(Sd.seedIdx("Plant_Sapling_Oak")) < 0 and int(Sd.seedIdx("Plant_Seeds_Oak")) < 0 and int(Sd.seedIdx(None)) < 0
            and int(Sd.seedIdx("Plant_Crop_Wheat_Item")) < 0, "SO seedIdx: seed bags yes; saplings / tree seeds / crops / null no")
    # the fake Pocket Dimension (SkyySacks' contract: take -> Long removed, put -> Long returned, commit -> Long cleared)
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

    def field(soil="Soil_Dirt_Tilled", r=2, crop="Plant_Crop_Wheat_Block", extra=None):
        m = HashMap()
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                m.put("%d|%d|%d" % (dx, CY - 1, dz), soil)
        m.put("0|%d|0" % CY, crop)   # the hand plant landed
        for k, v in (extra or {}).items():
            m.put(k, v)
        return m

    def go(seed="Plant_Seeds_Wheat", hand=3, pocket=0, deny=(), blocks=None, rank=1):
        d.rk[x] = rank
        POCK["n"] = pocket
        del CALLS[:]
        Sd.TEST_BLOCKS = blocks if blocks is not None else field()
        Sd.TEST_HAND = jpype.JArray(jpype.JInt)([hand])
        ds = HashSet()
        for c in deny:
            ds.add(c)
        Sd.TEST_DENY = ds
        lg = ArrayList()
        Sd.TEST_LOG = lg
        p0 = int(Sd.PLANTED)
        r = int(Sd.onPlace0(u, None, None, "w", seed, 0, CY, 0))
        return r, [str(s) for s in lg], int(Sd.PLANTED) - p0, int(Sd.TEST_HAND[0]), Sd.TEST_BLOCKS
    # rank 0: nothing
    r, lg, n, h, m = go(rank=0)
    K.check(r == 0 and lg == [] and n == 0 and h == 3 and int(Sd.radius(u)) == 0, "SO rank 0: a hand plant stays one cell")
    # rank 1: 3 from the hand, then 5 from the Pocket Dimension (8 cells), nearest ring, commit each
    r, lg, n, h, m = go(hand=3, pocket=9)
    K.check(int(Sd.radius(u)) == 1 and r == 2 and n == 8 and h == 0 and POCK["n"] == 4, "SO rank 1: the 3x3 - 8 extra cells (r %d n %d hand %d pocket %d)" % (r, n, h, POCK["n"]))
    K.eq([s.split(" ")[0] for s in lg], ["hand"] * 3 + ["pocket"] * 5, "SO the stack in hand first, then the Pocket Dimension")
    K.eq(sorted(" ".join(s.split(" ")[1:]) for s in lg), sorted("%d %d %d" % (dx, CY, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)), "SO exactly the 8 cells around the clicked one")
    K.check(all(str(m.get("%d|%d|%d" % (dx, CY, dz))) == "Plant_Crop_Wheat_Block" for dx in (-1, 0, 1) for dz in (-1, 0, 1)), "SO every cell holds the wheat crop")
    K.eq(CALLS, [("take", "Plant_Seeds_Wheat", 1), ("commit", "Plant_Seeds_Wheat", 1)] * 5, "SO the Pocket: take 1 -> commit 1 per cell (SkyySacks' refund ledger)")
    pend = Msg.PEND.get(u)
    K.check(pend is not None and "seeds sown (Wide Sowing)" in [str(k) for k in pend.keySet()], "SO one Tree bonus line: + seeds sown (Wide Sowing)")
    # out of seeds: the hand has 2, the Pocket none -> 2 cells, stop (a take that gives 0)
    r, lg, n, h, m = go(hand=2, pocket=0)
    K.check(n == 2 and h == 0 and CALLS == [("take", "Plant_Seeds_Wheat", 1)], "SO out of seeds: 2 from the hand, the Pocket gives none -> stop (%d, %s)" % (n, CALLS))
    # only air above the seed's own soil, at the same height
    ex = {"1|%d|0" % (CY - 1): "Soil_Dirt", "-1|%d|0" % (CY - 1): "Rock_Stone", "0|%d|1" % CY: "Plant_Crop_Carrot_Block", "0|%d|-1" % CY: "Plant_Grass_Lush",
          "1|%d|1" % (CY - 1): "Furniture_Village_Planter"}
    r, lg, n, h, m = go(hand=20, blocks=field(extra=ex))
    got = sorted(" ".join(s.split(" ")[1:]) for s in lg)
    K.eq(got, sorted(["-1 %d -1" % CY, "-1 %d 1" % CY, "1 %d -1" % CY, "1 %d 1" % CY]), "SO plain dirt / stone below, a crop or grass in the cell = skipped; a planter counts as soil")
    # protection: a refused cell is skipped (the hand seed goes to the next cell); a refused Pocket cell puts its seed back
    r, lg, n, h, m = go(hand=1, pocket=9, deny=["-1|%d|-1" % CY, "0|%d|1" % CY])
    K.check(n == 6 and h == 0 and lg[0] == "refused -1 %d -1" % CY and lg[1] == "hand -1 %d 0" % CY and lg[4] == "refused 0 %d 1" % CY,
            "SO a refused cell (protection) is skipped, the seed goes to the next cell: %s" % lg)
    K.eq(CALLS, [("take", "Plant_Seeds_Wheat", 1), ("commit", "Plant_Seeds_Wheat", 1)] * 2 + [("take", "Plant_Seeds_Wheat", 1), ("put", "Plant_Seeds_Wheat", 1)]
         + [("take", "Plant_Seeds_Wheat", 1), ("commit", "Plant_Seeds_Wheat", 1)] * 3, "SO the refused Pocket seed went back (take -> put), the others committed")
    K.eq(POCK["n"], 9 - 5, "SO the Pocket paid exactly the 5 Pocket cells planted")
    K.check(str(m.get("0|%d|1" % CY)) in ("", "None") and m.get("0|%d|1" % CY) is None, "SO the refused cell stays empty")
    # REFUSE_MAX refusals stop the area
    deny = ["%d|%d|%d" % (dx, CY, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)]
    r, lg, n, h, m = go(hand=20, deny=deny)
    K.check(n == 0 and len(lg) == int(Sd.REFUSE_MAX) == 4 and h == 20, "SO %d refusals stop the planting (no spam), nothing taken" % int(Sd.REFUSE_MAX))
    # the hand plant did not land (cancelled / refused by protection): nothing
    mi0 = int(Sd.MISSED)
    r, lg, n, h, m = go(hand=20, blocks=field(crop=""))
    K.check(n == 0 and lg == [] and int(Sd.MISSED) == mi0 + 1, "SO the clicked cell has no crop (the hand plant did not land) = nothing")
    # rank 2: 5x5 (24), ring 1 first
    r, lg, n, h, m = go(hand=64, rank=2)
    K.check(int(Sd.radius(u)) == 2 and n == 24 and h == 40, "SO rank 2: the 5x5 - 24 extra cells")
    K.check(all(max(abs(int(s.split(" ")[1])), abs(int(s.split(" ")[3]))) == 1 for s in lg[:8]) and all(max(abs(int(s.split(" ")[1])), abs(int(s.split(" ")[3]))) == 2 for s in lg[8:]),
            "SO the nearest ring first")
    # Server Setup rows: most 1 -> 3x3 for rank 2; per 9 / most 99 -> the hard cap 4 (9x9)
    i = [str(k) for k in Sk.KEY].index(SOW_KEY)
    setattr(Sk, "V3X%d" % i, 1.0)
    r, lg, n, h, m = go(hand=64, rank=2)
    K.check(int(Sd.radius(u)) == 1 and n == 8, "SO Server Setup 'most' 1: rank 2 plants the 3x3 only")
    setattr(Sk, "V3X%d" % i, 99.0)
    setattr(Sk, "V3P%d" % i, 9.0)
    r, lg, n, h, m = go(hand=200, rank=2, blocks=field(r=6))
    K.check(int(Sd.radius(u)) == 4 and n == 80, "SO a huge Server Setup radius is capped at 4 (9x9 = 80 cells): %d" % n)
    setattr(Sk, "V3P%d" % i, 1.0)
    setattr(Sk, "V3X%d" % i, 2.0)
    # Eternal seed bags plant the Eternal crop
    r, lg, n, h, m = go(seed="Plant_Seeds_Wheat_Eternal", hand=20, blocks=field(crop="Plant_Crop_Wheat_Block_Eternal"))
    K.check(n == 8 and str(m.get("1|%d|1" % CY)) == "Plant_Crop_Wheat_Block_Eternal", "SO Eternal seed bags sow Eternal crops")
    # crystal seeds: crystal soil only
    r, lg, n, h, m = go(seed="Plant_Seeds_Mana1", hand=20, blocks=field(crop="Plant_Crop_Mana1_Block"))
    K.check(n == 0, "SO a crystal seed never plants on tilled soil")
    r, lg, n, h, m = go(seed="Plant_Seeds_Mana1", hand=20, blocks=field(soil="Soil_Dirt_Crystal", crop="Plant_Crop_Mana1_Block"))
    K.check(n == 8 and str(m.get("0|%d|1" % CY)) == "Plant_Crop_Mana1_Block", "SO ... and fills crystal soil")
    # no chain: while our own plants run (ACTIVE) a plant event does nothing; profile busy = nothing; a sapling = nothing
    Sd.ACTIVE.put(u, JClass("java.lang.Boolean").TRUE)
    r, lg, n, h, m = go(hand=20)
    Sd.ACTIVE.remove(u)
    K.check(r == 0 and n == 0, "SO our own extra plants never start another area (ACTIVE)")
    br.put("profile:busy:" + U1, "x")
    r, lg, n, h, m = go(hand=20)
    br.remove("profile:busy:" + U1)
    K.check(r == 0 and n == 0, "SO nothing while the profile switches (profile:busy)")
    r, lg, n, h, m = go(seed="Plant_Sapling_Oak", hand=20)
    K.check(r == 0 and n == 0, "SO a sapling plant does nothing")
    K.check(Sd.ACTIVE.isEmpty(), "SO ACTIVE is empty after every run")
    K.check("extra seeds sown" in str(Sd.counts()), "SO the counts line: %s" % Sd.counts())
    for f in ("TEST_BLOCKS", "TEST_HAND", "TEST_DENY", "TEST_LOG"):
        setattr(Sd, f, None)
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    want = {"Common/Icons/ItemsGenerated/%s.png" % ICON, "Server/Item/Items/Utility/%s.json" % ICON}
    add = nb - na
    K.check(want <= add and not [n for n in na - nb if not n.startswith(T60.MAPDIR)], "J the Wide Sowing icon item is shipped (png + item json); nothing removed but renumbered map pictures (%d added)" % len(add))
    png = zb.read("Common/Icons/ItemsGenerated/%s.png" % ICON)
    K.check(png[:8] == b"\x89PNG\r\n\x1a\n" and png[16:24] == b"\x00\x00\x00\x40\x00\x00\x00\x40", "J the icon is a 64 x 64 PNG")
    sys.path.insert(0, TOOLS)
    import skyyart as A
    im = A.png_decode(png)
    blue = sum(1 for y in range(64) for x in range(64) if im.get(x, y)[3] > 200 and im.get(x, y)[2] > im.get(x, y)[0] + 25)
    green = sum(1 for y in range(64) for x in range(64) if im.get(x, y)[3] > 200 and im.get(x, y)[1] > im.get(x, y)[2] + 20)
    K.check(blue > 100 and green > 60, "J the icon holds the four blue arrows + the green sprout (%d / %d px)" % (blue, green))
    others = [zb.read(n) for n in nb if n.startswith("Common/Icons/ItemsGenerated/Skyy_NodeIcon_") and n.endswith(".png") and ICON not in n]
    K.check(png not in others, "J its own picture (no other node icon has the same bytes)")
    js = json.loads(zb.read("Server/Item/Items/Utility/%s.json" % ICON).decode("utf8"))
    K.check(js["Icon"] == "Icons/ItemsGenerated/%s.png" % ICON and "Recipe" not in js and "Categories" not in js and "Interactions" not in js, "J the icon-only item json")
    lang = zb.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check(("items.%s.name=Wide Sowing" % ICON) in lang, "J the icon name in server.lang")
    other = sorted(n for n in add - want if not (n.startswith(T60.MAPDIR) or n.endswith(".class")))
    K.eq(other, [], "J no other new non-class entry")
    K.save()


HK.run_compare = T60._compare

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("g64", run_g64), ("data", run_data), ("sow", run_sow), ("jar", run_jar),
                   ("path", T64.run_path), ("mig", T64.run_mig), ("integ", T64.run_integ),
                   ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
