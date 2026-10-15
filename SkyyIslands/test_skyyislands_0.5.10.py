"""Harness for SkyyIslands 0.5.10 (THE 3 STARTER ISLANDS; tools/islands_0_5_10_patch.py). Build first:
python tools/islands_0_5_10_patch.py && python SkyyIslands/build_skyyislands_0.5.10.py

    python SkyyIslands/test_skyyislands_0.5.10.py [--dir <folder inside tools/dev/scratch/>] [--no-server] [--keep]

  S   (game closed only; --no-server or a running game = NOT RUN, said so) the REAL server through tools/smoke_test.py with a scratch-only
      probe plugin built here: a NEW island made the /island way (spawnInstance SkyyIsland -> IslandBuild) with the default design =
      EVERY block of the 3 islands at its place (block for block = the build's s3_layout()), the starter chest holding the kit, the
      island's own log lines (12 / 12 chunks relit); a second fill of that world changes nothing; starter.design=classic -> the next new
      island is the 0.5.9 classic island (516 blocks, block for block); back to three + ChunkFill.load on that CLASSIC world changes
      nothing (an existing island is never filled again); every section of the 3 islands switched to ticking (what a player near does)
      -> the blocks stay (no support pop); island:places + island:fn:place on the real bridge; FIX ROUND 2: the fill runs in several
      world-thread slices and the engine logs no "Task took" WARN for a 3-island FillTask; H9 = the retry pass on an island whose kit is
      already in the chest (what RelightTask's late kit between the passes leaves) -> the chest keeps exactly ONE kit, no block changes
  S3  (bare JVM, -Xverify:all) the jar's StarterIsles data decodes to exactly the build's layout; the DESIGN checks (each island 3.5-5x
      the classic 140 columns, gaps 8-12 blocks of sky, gatherables per island, the copper cave, ruins, portal frame, plank stubs, chest +
      spawn, chunks / sections, every block breakable per Assets.zip); three() / placeOf / PlaceFn / publish / afterDesign / reloadCfg;
      config.properties (a fresh file lists starter.design, a 0.5.9 file without it = three, classic read, junk = three); the Server
      Setup row; STATIC: ChunkFill.load is called only by IslandBuild.apply, FillTask is made only by ChunkFill.load, IslandBuild only by
      /island's creation (IslandCmd.go) and /island reset (IslandCoop.resetNow); FillTask.run checks the spawn block BEFORE it fills
  A / C / AA  verify, class compare 0.5.9 -> 0.5.10, engine-access audit
  SND, X, D   every 0.5.9 phase on the 0.5.10 jar (D = START TWICE on a scratch COPY of the live Skyy_SkyyIslands, nothing written)
Exit code 1 on any failure.
"""
import os, sys, re, json, glob, math, shutil, zipfile, subprocess, importlib.util, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK

_spec = importlib.util.spec_from_file_location("test_skyyislands_0_5_9", os.path.join(HERE, "test_skyyislands_0.5.9.py"))
T59 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T59)
T58 = T59.T58

VERSION = "0.5.10"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "islands3", "h")))
SRV = os.path.join(os.path.dirname(SCRATCH), "srv")
PKG = "com.skyy.islands."
PROBE_NAME, PROBE_VER = "SkyyIslands3Probe", "0.1"
KEY_A, KEY_B = "00000000-0000-4000-8000-0000000a0510", "00000000-0000-4000-8000-0000000b0510"
KEY_C = "00000000-0000-4000-8000-0000000c0510"     # fix round: the partly loaded fill -> one retry
EXPECT = {
    "IslandCfg": ["+f STARTER_DESIGN", "~<clinit>", "~m load"],
    "FillTask": ["+f three", "+f tries", "+f at", "+f placed", "+f slices", "+f runs", "+f fin", "+m has", "+m next", "~m run"],
    "ChunkFill": ["~m load"],
    "RelightNow": ["~m run"],
    "IslandHooks": ["+m afterDesign", "~m reloadCfg"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyyIslandsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["PlaceFn", "StarterIsles"]


def layout():
    """the build script's s3_layout() data (S3_ONLY=1 stops the script right before the JVM / the build)"""
    os.environ["S3_ONLY"] = "1"
    sp = importlib.util.spec_from_file_location("build_skyyislands_0_5_10_s3", os.path.join(HERE, "build_skyyislands_0.5.10.py"))
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except ImportError as e:
        assert "S3_ONLY" in str(e), e
    finally:
        del os.environ["S3_ONLY"]
    return m


def classic_layout():
    """the classic (0.5.5 - 0.5.9) FillTask layout, the same loops in the same order (test_skyyislands_0.5.6.py island_layout)"""
    L = {}
    for x in range(2, 14):
        for z in range(2, 14):
            if (x in (2, 13)) and (z in (2, 13)):
                continue
            L[(x, 128, z)] = "Soil_Grass"
            L[(x, 127, z)] = "Soil_Dirt"
            if 3 <= x <= 12 and 3 <= z <= 12:
                L[(x, 126, z)] = "Soil_Dirt"
            if 4 <= x <= 11 and 4 <= z <= 11:
                L[(x, 125, z)] = "Rock_Stone"
            if 6 <= x <= 9 and 6 <= z <= 9:
                L[(x, 124, z)] = "Rock_Stone"
    for y in range(129, 134):
        L[(11, y, 11)] = "Wood_Oak_Trunk"
    for x in range(9, 14):
        for z in range(9, 14):
            for y in range(132, 135):
                if x == 11 and z == 11 and y <= 133:
                    continue
                edge = (x in (9, 13)) and (z in (9, 13))
                if edge or (y == 134 and (x in (9, 13) or z in (9, 13))):
                    continue
                L[(x, y, z)] = "Plant_Leaves_Oak"
    L[(11, 135, 11)] = "Plant_Leaves_Oak"
    L[(4, 129, 4)] = "Furniture_Crude_Chest_Small"
    return L


def bbox(L, pad):
    xs = [k[0] for k in L]
    ys = [k[1] for k in L]
    zs = [k[2] for k in L]
    return (min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad, min(zs) - pad, max(zs) + pad)


# ================================================================================================ S3: the design + the jar's data (bare JVM)
def design_checks(K, m):
    L, P, tops, isle = m.S3_L, m.S3_PLACES, m.S3_TOPS, m.S3_ISLE
    by = {}
    for (x, y, z), b in L.items():
        by.setdefault(isle.get((x, z), "sky"), {}).setdefault(b, 0)
        by[isle.get((x, z), "sky")][b] += 1
    cols = dict((n, [p for p, v in isle.items() if v == n]) for n in ("island1", "island2", "island3"))
    for n, c in sorted(cols.items()):
        K.check(4.0 <= len(c) / 144.0 and len(c) / 140.0 <= 5.0, "DESIGN %s: %d columns = %.2fx the classic island's 144 (12 x 12) / %.2fx its 140 grass columns (Skyy: 4x-5x, still small; fix round: island 3 was 3.7x)" % (n, len(c), len(c) / 144.0, len(c) / 140.0))

    def gap(a, b):
        return min(math.hypot(p[0] - q[0], p[1] - q[1]) for p in cols[a] for q in cols[b])
    g12, g23, g13 = gap("island1", "island2"), gap("island2", "island3"), gap("island1", "island3")
    K.check(8 <= g12 <= 12 and 8 <= g23 <= 12 and g13 > 30, "DESIGN gaps of open sky: 1-2 %.1f, 2-3 %.1f (8-12 = bridge it), 1-3 %.1f" % (g12, g23, g13))
    sky = by.get("sky", {})
    K.eq(sky, {"Wood_Softwood_Planks": 9}, "DESIGN only the broken plank stubs hang over the gaps (9 planks)")
    i1, i2, i3 = by["island1"], by["island2"], by["island3"]
    g = lambda d, *ids: sum(d.get(i, 0) for i in ids)
    K.check(g(i1, "Wood_Oak_Trunk") >= 10 and g(i1, "Plant_Bush", "Plant_Bush_Green") >= 10 and g(i1, "Wood_Sticks") >= 4
            and g(i1, "Rubble_Stone", "Rubble_Stone_Mossy") >= 8 and g(i1, "Ore_Copper_Stone") >= 5 and g(i1, "Rock_Stone") >= 100
            and g(i1, "Soil_Dirt_Tilled") == 12 and g(i1, "Plant_Crop_Wheat_Block") == 9,
            "DESIGN island 1 gatherables (chop 10 logs, bushes = fibre + sticks, stick piles, rubble, copper 5+, stone, the plot): %s" % i1)
    plot = [(x, z) for x in range(11, 14) for z in range(2, 6)]
    K.check(all(L.get((x, 128, z)) == "Soil_Dirt_Tilled" for x, z in plot)
            and sorted((x, z) for x, z in plot if L.get((x, 129, z)) == "Plant_Crop_Wheat_Block") == [(x, z) for x in range(11, 14) for z in range(2, 5)]
            and all((x, 129, 5) not in L for x in range(11, 14)),
            "DESIGN fix round: the starter plot = 12 tilled cells, 9 freshly planted wheat crops on them (task 7's seed source - the kit has no seeds), the z=5 row free")
    K.check(g(i2, "Ore_Copper_Stone") >= 4 and g(i2, "Ore_Iron_Stone") >= 2 and g(i2, "Deco_Campfire_Off") == 1 and g(i2, "Wood_Oak_Trunk") >= 5
            and g(i2, "Plant_Bush", "Plant_Bush_Green") >= 5 and g(i2, "Rubble_Stone", "Rubble_Stone_Mossy") >= 5,
            "DESIGN island 2: the ruined camp, ore knoll, trees, bushes, rubble: %s" % i2)
    K.check(g(i3, "Rock_Stone_Brick_Pillar_Base") == 6 and g(i3, "Ore_Copper_Stone") + g(i3, "Ore_Iron_Stone") >= 4
            and g(i3, "Rubble_Stone", "Rubble_Stone_Mossy") >= 5 and g(i3, "Rock_Stone_Brick_Decorative") == 3,
            "DESIGN island 3: 6 broken pillars, the portal frame, ore, rubble: %s" % i3)
    ruins = lambda d: g(d, "Rock_Stone_Brick", "Rock_Stone_Brick_Mossy", "Rock_Stone_Cobble", "Rock_Stone_Cobble_Mossy", "Rock_Stone_Brick_Pillar_Base",
                        "Rock_Stone_Brick_Pillar_Middle", "Rock_Stone_Brick_Half", "Rock_Stone_Brick_Decorative", "Rock_Stone_Brick_Smooth")
    K.check(ruins(i1) >= 15 and ruins(i2) >= 25 and ruins(i3) >= 20, "DESIGN old broken structures on every island (%d / %d / %d ruin blocks)" % (ruins(i1), ruins(i2), ruins(i3)))
    cave_air = [(x, y, z) for x in range(12, 19) for z in (15, 16) for y in (129, 130) if (x, y, z) not in L and tops.get((x, z), 0) > y]
    K.check(len(cave_air) >= 10 and all(L.get((x, 128, z)) in ("Rock_Stone", "Ore_Copper_Stone") for x, _y, z in cave_air),
            "DESIGN the copper cave: %d air blocks under a roof, stone floor" % len(cave_air))
    K.check(L.get((4, 129, 4)) == "Furniture_Crude_Chest_Small" and L.get((8, 128, 8)) == "Soil_Grass" and (8, 129, 8) not in L and (8, 130, 8) not in L,
            "DESIGN the starter chest at 4,129,4 (FillTask.starterKit) and the spawn 8.5,129,8.5 on grass, clear above (= the classic island)")
    K.check(all(-1 <= x >> 5 <= 2 and -1 <= z >> 5 <= 1 and 96 <= y <= 159 for x, y, z in L),
            "DESIGN every block in chunks cx -1..2, cz -1..1, sections y 96-159 (relight / tint / loads cover them)")
    under = [(x, y, z) for (x, y, z), b in L.items() if b == "Soil_Grass" and L.get((x, y + 1, z), "").startswith(("Rock_", "Ore_", "Wood_Oak_Trunk"))]
    K.check(not under and sum(1 for (x, y, z), b in L.items() if b == "Soil_Dirt" and L.get((x, y + 1, z), "").startswith(("Rock_", "Ore_", "Wood_Oak_Trunk"))) >= 40,
            "DESIGN fix round: dirt (not grass) under every ruin / ore / trunk block (vanilla turns covered grass to dirt - seen in H6): grass left %s" % under[:5])
    K.eq(sorted(P), ["boss", "camp", "cave", "island1", "island2", "island3", "plot", "portal"], "DESIGN the named places")
    for k, n in (("island1", "island1"), ("island2", "island2"), ("camp", "island2"), ("island3", "island3"), ("boss", "island3"), ("portal", "island3"), ("plot", "island1")):
        x, y, z, _l = P[k]
        c = (int(math.floor(x)), int(math.floor(z)))
        K.check(isle.get(c) == n and (c[0], int(y), c[1]) not in L and (c[0], int(y) - 1, c[1]) in L,
                "DESIGN place %s stands on %s (%s)" % (k, n, P[k]))
    # every id: an item of Assets.zip (read only) whose block players can break
    z = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    nm = dict((os.path.basename(n)[:-5], n) for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    bad = []
    for b in sorted(set(L.values())):
        c, gth, unb = b, False, False
        while c:
            if c not in nm:
                bad.append(b)
                break
            j = json.loads(z.read(nm[c]))
            gth = gth or "Gathering" in j.get("BlockType", {})
            unb = unb or "Unbreakable" in json.dumps(j)
            c = j.get("Parent")
        if not gth or unb:
            bad.append(b)
    K.check(not bad, "DESIGN all %d block ids are vanilla blocks with a Gathering (breakable) and no Unbreakable: bad %s" % (len(set(L.values())), bad))
    K.check(not any(n.startswith("Server/Prefabs/") for n in zipfile.ZipFile(JAR).namelist()), "DESIGN no prefab file in the jar (designs as data)")


def run_s3(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    m = layout()
    design_checks(K, m)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    S3, Cfg, PF, Hooks, Rows, Fn = P("StarterIsles"), P("IslandCfg"), P("PlaceFn"), P("IslandHooks"), P("CfgRows"), P("CfgFn")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    # ---------------- the jar's data = the build's layout
    r = list(S3.decode())
    pal = [str(x) for x in S3.PAL]
    got = {}
    for i in range(int(S3.RUNS)):
        p, x, y, z, n = r[i * 5:i * 5 + 5]
        for k in range(n):
            got[(x + k, y, z)] = pal[p]
    K.check(got == m.S3_L and int(S3.BLOCKS) == len(m.S3_L), "DATA StarterIsles.decode() = the build's s3_layout() block for block (%d blocks, %d runs)" % (len(got), int(S3.RUNS)))
    K.eq(list(S3.CHUNKS), [v for c in m.S3_CHUNKS for v in c], "DATA chunks")
    K.eq(list(S3.SECTS), [v for c in m.S3_SECTS for v in c], "DATA sections")
    K.eq((int(S3.CX0), int(S3.CX1), int(S3.CZ0), int(S3.CZ1)), (-1, 2, -1, 1), "DATA relight bounds")
    # ---------------- three() / placeOf / PlaceFn / publish
    for v, want in (("three", True), ("classic", False), (" Classic ", False), (None, True), ("junk", True)):
        Cfg.STARTER_DESIGN = v
        K.eq(bool(S3.three()), want, "three() for starter.design %r" % v)
    Cfg.STARTER_DESIGN = "three"
    for k, (x, y, z, lab) in m.S3_PLACES.items():
        K.eq(str(S3.placeOf(k)), "island|%s|%s|%s|%s" % (x, y, z, lab), "placeOf(%s)" % k)
    K.check(S3.placeOf("nowhere") is None and S3.placeOf(None) is None, "placeOf: unknown / null = null")
    pf = PF()
    u = UUID.fromString("00000000-0000-0000-0000-0000000000a3")
    K.eq(str(pf.apply(JString("island2"))), str(S3.placeOf("island2")), "PlaceFn String id")
    K.eq(str(pf.apply(JArray(JObject)([u, JString("portal")]))), str(S3.placeOf("portal")), "PlaceFn Object[] {UUID, id} (the spec shape)")
    K.check(pf.apply(JClass("java.lang.Integer")(3)) is None and pf.apply(None) is None and pf.apply(JString("nowhere")) is None, "PlaceFn: bad input / unknown = null, no throw")
    Cfg.STARTER_DESIGN = "classic"
    K.check(pf.apply(JString("island2")) is None, "PlaceFn: classic design = null")
    br.put("island:places", "stale")
    S3.publish()
    K.check(not br.containsKey("island:places"), "publish(): classic = island:places removed")
    Cfg.STARTER_DESIGN = "three"
    Hooks.afterDesign("starter.design")
    K.eq(str(br.get("island:places")), m.S3_PLACES_TEXT, "afterDesign (Server Setup change) -> island:places published")
    # ---------------- config.properties
    home = os.path.join(scratch, "s3", "Skyy_SkyyIslands")
    os.makedirs(home, exist_ok=True)
    cf = os.path.join(home, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.load("")
    txt = open(cf, encoding="utf-8").read()
    K.check("starter.design=three" in txt and str(Cfg.STARTER_DESIGN) == "three", "CFG a fresh config.properties lists starter.design=three")
    old = "\n".join(l for l in txt.splitlines() if not l.startswith("starter.design")) + "\n"
    for extra, want in (("", "three"), ("starter.design=classic\n", "classic"), ("starter.design=CLASSIC\n", "classic"), ("starter.design=junk\n", "three")):
        open(cf, "w", encoding="utf-8").write(old + extra)
        Cfg.STARTER_DESIGN = "x"
        Cfg.load("")
        K.eq(str(Cfg.STARTER_DESIGN), want, "CFG %r -> %s (a 0.5.9 file without the line = three)" % (extra.strip(), want))
    open(cf, "w", encoding="utf-8").write(old + "starter.design=classic\n")
    br.put("island:places", "x")
    Hooks.reloadCfg()
    K.check(str(Cfg.STARTER_DESIGN) == "classic" and not br.containsKey("island:places"), "CFG reloadCfg (hand edit + reload) -> classic, island:places removed")
    open(cf, "w", encoding="utf-8").write(txt)
    Hooks.reloadCfg()
    K.check(str(Cfg.STARTER_DESIGN) == "three" and str(br.get("island:places")) == m.S3_PLACES_TEXT, "CFG reloadCfg back to three -> island:places published")
    rows = SK.kit_rows(Rows)
    K.eq(rows.get("starter.design", [None] * 11)[1:10], ["Starter islands", "starter", "choice", "three", "", "", "three|3 starter islands,classic|Classic island", "", "new"],
         "ROW Server Setup -> Islands -> Starter kit -> Starter islands (choice, default three, new islands only)")
    # ---------------- static
    g = PW.calls(jar)
    K.eq(PW.callers(g, "ChunkFill.load", PKG), ["IslandBuild.apply"], "STATIC ChunkFill.load is called only by IslandBuild.apply (island creation / reset)")
    K.eq(PW.callers(g, "FillTask.<init>", PKG), ["ChunkFill.load"], "STATIC a FillTask is made only by ChunkFill.load")
    K.eq(PW.callers(g, "IslandBuild.<init>", PKG), ["IslandCmd.go", "IslandCoop.resetNow"], "STATIC IslandBuild only from /island's creation branch and /island reset")
    K.eq(PW.callers(g, "StarterIsles.fill", PKG), ["FillTask.run"], "STATIC StarterIsles.fill only from FillTask.run")
    K.eq(PW.callers(g, "StarterIsles.loads", PKG), ["ChunkFill.load", "FillTask.run"], "STATIC StarterIsles.loads only from ChunkFill.load (+ fix round: FillTask.run's one retry)")
    K.eq(PW.callers(g, "FillTask.has", PKG), ["StarterIsles.fill"], "STATIC FillTask.has only from StarterIsles.fill (the retry pass)")
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                IP(PS(bos)).print_(mm)
        return str(bos.toString())
    run = code("FillTask", "run")
    K.check(0 <= run.find("FillTask.blockAt") < run.find("StarterIsles.fill") and run.count("StarterIsles.fill") == 1,
            "STATIC FillTask.run: the 'already built' spawn-block check comes BEFORE the 3-island fill (an existing island is never filled)")
    K.check(0 <= run.find("FillTask.tries") < run.find("FillTask.blockAt") and run.find("StarterIsles.fill") < run.find("StarterIsles.loads") < run.find("FillTask.starterKit"),
            "STATIC fix round: FillTask.run - only the retry (tries) skips the spawn-block guard; the retry's loads come after the fill and before the starter kit")
    nx = code("FillTask", "next")
    K.check(0 <= run.find("FillTask.at") < run.find("FillTask.blockAt") and "FillTask.next" in run and "delayedExecutor" in nx and "whenCompleteAsync" in nx
            and run.find("StarterIsles.fill") < run.find("StarterIsles.tintOne") < run.find("FillTask.starterKit"),
            "STATIC fix round 2: FillTask.run - later slices (at > 0) skip the checks; the next slice goes through delayedExecutor -> accept")
    K.check(0 <= run.find("StarterIsles.fill") < run.find("IslandStore.KITDONE") < run.find("FillTask.starterKit"),
            "STATIC fix round 2: the 3-island kit is gated on IslandStore.KITDONE (no second kit after RelightTask's late kit)")
    sf = code("StarterIsles", "fill")
    K.check(0 <= sf.find("FillTask.has") < sf.find("FillTask.put") and "System.nanoTime" in sf and int(S3.SLICE_NS) <= 20000000,
            "STATIC fix round 2: StarterIsles.fill - the retry checks has() BEFORE put (an existing block, e.g. the kitted chest, is never re-placed); time-boxed slices of %d ms" % (int(S3.SLICE_NS) // 1000000))
    ld = code("ChunkFill", "load")
    K.check(0 <= ld.find("StarterIsles.three") < ld.find("StarterIsles.loads"), "STATIC ChunkFill.load fixes the design (three()) before it loads")
    K.save()


# ================================================================================================ S: the REAL server + a probe (game closed)
DUMP = r"""
public void run() {
  try {
    if (this.mode == 2) {
      com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs2 = this.world.getChunkStore();
      int[] sc = (int[]) Class.forName("com.skyy.islands.StarterIsles", true, this.cl).getField("SECTS").get(null);
      int n = 0;
      for (int i = 0; i < sc.length / 3; i++) { cs2.getChunkSectionReferenceAsync(sc[i * 3], sc[i * 3 + 1], sc[i * 3 + 2], 4); n++; }
      com.skyy.islands3probe.ProbePlugin.log(this.tag + " switched " + n + " sections to ticking (getChunkSectionReferenceAsync flag 4 - what a nearby player causes)");
      this.latch.countDown();
      return;
    }
    java.lang.reflect.Method ba = Class.forName("com.skyy.islands.FillTask", true, this.cl).getMethod("blockAt", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, Integer.TYPE, Integer.TYPE, Integer.TYPE });
    StringBuilder sb = new StringBuilder();
    int n = 0;
    int miss = 0;
    for (int y = this.b[2]; y <= this.b[3]; y++) for (int z = this.b[4]; z <= this.b[5]; z++) for (int x = this.b[0]; x <= this.b[1]; x++) {
      int id = ((Integer) ba.invoke(null, new Object[] { this.world, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) })).intValue();
      if (id < 0) { miss++; continue; }
      if (id == 0) continue;
      com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType bt = (com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType) com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType.getAssetMap().getAsset(id);
      sb.append(x).append(',').append(y).append(',').append(z).append('=').append(bt == null ? ("#" + id) : bt.getId()).append(';');
      n++;
    }
    com.skyy.islands3probe.ProbePlugin.log(this.tag + " blocks " + n + " (positions in unloaded sections " + miss + ")");
    String s = sb.toString();
    int parts = (s.length() + 1799) / 1800;
    for (int i = 0; i < parts; i++) com.skyy.islands3probe.ProbePlugin.log(this.tag + " dump " + (i + 1) + "/" + parts + " " + s.substring(i * 1800, Math.min(s.length(), (i + 1) * 1800)));
    if (this.mode == 1) {
      java.lang.reflect.Method be = Class.forName("com.skyy.islands.FillTask", true, this.cl).getMethod("blockEntity", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, Integer.TYPE, Integer.TYPE, Integer.TYPE });
      java.lang.reflect.Method bh = Class.forName("com.skyy.islands.FillTask", true, this.cl).getMethod("blockHolder", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, Integer.TYPE, Integer.TYPE, Integer.TYPE });
      com.hypixel.hytale.component.Ref r = (com.hypixel.hytale.component.Ref) be.invoke(null, new Object[] { this.world, Integer.valueOf(4), Integer.valueOf(129), Integer.valueOf(4) });
      Object comp = null;
      String kind = "none";
      if (r != null && r.isValid()) { comp = this.world.getChunkStore().getStore().getComponent(r, com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock.getComponentType()); kind = "entity"; }
      else {
        com.hypixel.hytale.component.Holder h = (com.hypixel.hytale.component.Holder) bh.invoke(null, new Object[] { this.world, Integer.valueOf(4), Integer.valueOf(129), Integer.valueOf(4) });
        if (h != null) { comp = h.getComponent(com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock.getComponentType()); kind = "holder"; }
      }
      if (!(comp instanceof com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock)) com.skyy.islands3probe.ProbePlugin.log(this.tag + " chest " + kind + ": no ItemContainerBlock at 4,129,4");
      else {
        com.hypixel.hytale.server.core.inventory.container.ItemContainer c = ((com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock) comp).getItemContainer();
        StringBuilder k = new StringBuilder();
        int cap = c.getCapacity();
        for (int i = 0; i < cap; i++) {
          com.hypixel.hytale.server.core.inventory.ItemStack is = c.getItemStack((short) i);
          if (is != null && !is.isEmpty()) k.append(is.getItemId()).append(" x").append(is.getQuantity()).append(';');
        }
        com.skyy.islands3probe.ProbePlugin.log(this.tag + " chest " + kind + " capacity " + cap + ": " + k.toString());
      }
    }
  } catch (Throwable t) { com.skyy.islands3probe.ProbePlugin.log(this.tag + " dump FAILED: " + t); }
  this.latch.countDown();
}"""

MAIN = r"""
public void run() {
  if (this.mode == 0) {
    if (STARTED) return;
    try {
      TRIES++;
      com.hypixel.hytale.server.core.universe.Universe u = com.hypixel.hytale.server.core.universe.Universe.get();
      com.hypixel.hytale.server.core.universe.world.World dw = u == null ? null : u.getDefaultWorld();
      java.util.Map b = (java.util.Map) System.getProperties().get("skyy.bridge");
      Object pf = b == null ? null : b.get("island:fn:place");
      if (dw == null || pf == null || com.hypixel.hytale.builtin.instances.InstancesPlugin.get() == null) {
        if (TRIES > 120) { STARTED = true; com.skyy.islands3probe.ProbePlugin.log("H0 gave up: no default world / island:fn:place after 240 s"); }
        return;
      }
      STARTED = true;
      new Thread(new com.skyy.islands3probe.ProbeTask(1), "SkyyIslands3Probe").start();
    } catch (Throwable t) { STARTED = true; com.skyy.islands3probe.ProbePlugin.log("H0 FAILED: " + t); }
    return;
  }
  try {
    com.hypixel.hytale.server.core.universe.world.World dw = com.hypixel.hytale.server.core.universe.Universe.get().getDefaultWorld();
    java.util.Map b = (java.util.Map) System.getProperties().get("skyy.bridge");
    Object pf = b.get("island:fn:place");
    ClassLoader cl = pf.getClass().getClassLoader();
    java.lang.reflect.Field fd = Class.forName("com.skyy.islands.IslandCfg", true, cl).getField("STARTER_DESIGN");
    Object pl = b.get("island:places");
    com.skyy.islands3probe.ProbePlugin.log("H7 design " + fd.get(null) + "; island:places " + (pl instanceof String ? ((String) pl).length() + " chars" : "MISSING") + "; island:fn:place island2 = " + ((java.util.function.Function) pf).apply("island2"));
    // H1: a NEW island, default design
    com.hypixel.hytale.server.core.universe.world.World wa = make(dw, cl, "@KA@");
    Thread.sleep(7000L);
    com.skyy.islands3probe.DumpTask.on(wa, cl, "H2", 1, new int[] { @BA@ });
    java.util.concurrent.CompletableFuture f2 = (java.util.concurrent.CompletableFuture) Class.forName("com.skyy.islands.ChunkFill", true, cl).getMethod("load", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class }).invoke(null, new Object[] { wa });
    com.skyy.islands3probe.ProbePlugin.log("H3 second ChunkFill.load completed: " + (f2.get(60L, java.util.concurrent.TimeUnit.SECONDS) == wa));
    com.skyy.islands3probe.DumpTask.on(wa, cl, "H3", 0, new int[] { @BA@ });
    // H4: classic
    fd.set(null, "classic");
    com.hypixel.hytale.server.core.universe.world.World wb = make(dw, cl, "@KB@");
    Thread.sleep(7000L);
    com.skyy.islands3probe.DumpTask.on(wb, cl, "H4", 1, new int[] { @BB@ });
    // H5: back to three - the CLASSIC island (an existing island) is never filled again
    fd.set(null, "three");
    java.util.concurrent.CompletableFuture f5 = (java.util.concurrent.CompletableFuture) Class.forName("com.skyy.islands.ChunkFill", true, cl).getMethod("load", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class }).invoke(null, new Object[] { wb });
    com.skyy.islands3probe.ProbePlugin.log("H5 ChunkFill.load on the classic island with design three completed: " + (f5.get(60L, java.util.concurrent.TimeUnit.SECONDS) == wb));
    com.skyy.islands3probe.DumpTask.on(wb, cl, "H5", 0, new int[] { @BA@ });
    // H6: every section of the 3 islands ticking (a player near) -> the blocks stay
    com.skyy.islands3probe.DumpTask.on(wa, cl, "H6", 2, null);
    Thread.sleep(6000L);
    // nobody is near, so the engine may unload (and save) those chunks meanwhile: load them again through the engine, then look
    java.util.concurrent.CompletableFuture[] lp = (java.util.concurrent.CompletableFuture[]) Class.forName("com.skyy.islands.StarterIsles", true, cl).getMethod("loads", new Class[] { com.hypixel.hytale.server.core.universe.world.storage.ChunkStore.class }).invoke(null, new Object[] { wa.getChunkStore() });
    java.util.concurrent.CompletableFuture.allOf(lp).get(120L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islands3probe.ProbePlugin.log("H6 the 3 islands' chunks + sections loaded again (" + lp.length + " futures)");
    com.skyy.islands3probe.DumpTask.on(wa, cl, "H6", 1, new int[] { @BA@ });
    // H8 (fix round): a 3-island fill that finds only chunk (0,0) loaded (the classic 3 loads) -> one retry loads the rest and fills it all
    com.hypixel.hytale.server.core.universe.world.World wc = (com.hypixel.hytale.server.core.universe.world.World) com.hypixel.hytale.builtin.instances.InstancesPlugin.get().spawnInstance("SkyyIsland", "skyy-island-@KC@", dw, new com.hypixel.hytale.math.vector.Transform(0.0, 128.0, 0.0)).get(180L, java.util.concurrent.TimeUnit.SECONDS);
    Class ftc = Class.forName("com.skyy.islands.FillTask", true, cl);
    java.util.concurrent.CompletableFuture dn = new java.util.concurrent.CompletableFuture();
    Object ft = ftc.getConstructor(new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, java.util.concurrent.CompletableFuture.class }).newInstance(new Object[] { wc, dn });
    ftc.getField("three").setBoolean(ft, true);
    com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs8 = wc.getChunkStore();
    java.util.concurrent.CompletableFuture[] p8 = new java.util.concurrent.CompletableFuture[3];
    p8[0] = cs8.getChunkReferenceAsync(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(0, 0));
    p8[1] = cs8.getChunkSectionReferenceAsync(0, 3, 0);
    p8[2] = cs8.getChunkSectionReferenceAsync(0, 4, 0);
    java.util.concurrent.CompletableFuture.allOf(p8).whenComplete((java.util.function.BiConsumer) ft);
    dn.get(180L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islands3probe.ProbePlugin.log("H8 partly loaded fill finished, tries " + ftc.getField("tries").getInt(ft));
    com.skyy.islands3probe.DumpTask.on(wc, cl, "H8", 0, new int[] { @BA@ });
    // H9 (fix round 2): the retry pass on island A, whose kit is already in the chest (= RelightTask's late kit between the passes)
    java.util.Map kd = (java.util.Map) Class.forName("com.skyy.islands.IslandStore", true, cl).getField("KITDONE").get(null);
    com.skyy.islands3probe.ProbePlugin.log("H9 KITDONE has island A: " + kd.containsKey("@KA@"));
    java.util.concurrent.CompletableFuture dn9 = new java.util.concurrent.CompletableFuture();
    Object ft9 = ftc.getConstructor(new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, java.util.concurrent.CompletableFuture.class }).newInstance(new Object[] { wa, dn9 });
    ftc.getField("three").setBoolean(ft9, true);
    ftc.getField("tries").setInt(ft9, 1);
    java.util.concurrent.CompletableFuture[] p9 = (java.util.concurrent.CompletableFuture[]) Class.forName("com.skyy.islands.StarterIsles", true, cl).getMethod("loads", new Class[] { com.hypixel.hytale.server.core.universe.world.storage.ChunkStore.class }).invoke(null, new Object[] { wa.getChunkStore() });
    java.util.concurrent.CompletableFuture.allOf(p9).whenComplete((java.util.function.BiConsumer) ft9);
    dn9.get(180L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islands3probe.ProbePlugin.log("H9 retry pass on the kitted island finished, slices " + ftc.getField("slices").getInt(ft9) + ", placed " + ftc.getField("placed").getInt(ft9));
    com.skyy.islands3probe.DumpTask.on(wa, cl, "H9", 1, new int[] { @BA@ });
    com.skyy.islands3probe.ProbePlugin.log("DONE");
  } catch (Throwable t) { com.skyy.islands3probe.ProbePlugin.log("PROBE FAILED: " + t); }
}"""
MAKE = r"""
public static com.hypixel.hytale.server.core.universe.world.World make(com.hypixel.hytale.server.core.universe.world.World dw, ClassLoader cl, String key) throws Exception {
  Object fn = Class.forName("com.skyy.islands.IslandBuild", true, cl).getConstructor(new Class[] { String.class }).newInstance(new Object[] { key });
  com.skyy.islands3probe.ProbePlugin.log("H1 making island " + key + " the /island way (spawnInstance SkyyIsland -> IslandBuild)");
  long t0 = System.currentTimeMillis();
  java.util.concurrent.CompletableFuture f = com.hypixel.hytale.builtin.instances.InstancesPlugin.get().spawnInstance("SkyyIsland", "skyy-island-" + key, dw, new com.hypixel.hytale.math.vector.Transform(0.0, 128.0, 0.0));
  f = f.thenCompose((java.util.function.Function) fn);
  com.hypixel.hytale.server.core.universe.world.World w = (com.hypixel.hytale.server.core.universe.world.World) f.get(180L, java.util.concurrent.TimeUnit.SECONDS);
  com.skyy.islands3probe.ProbePlugin.log("H1 IslandBuild finished: " + w.getName() + " in " + (System.currentTimeMillis() - t0) + " ms");
  return w;
}"""


def build_probe(out_dir):
    m = layout()
    ba = ", ".join(str(v) for v in bbox(m.S3_L, 2))
    bb = ", ".join(str(v) for v in bbox(classic_layout(), 2))
    J = B.start()
    pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
    P = "com.skyy.islands3probe."
    cls_dir = os.path.join(out_dir, "probe_classes")
    shutil.rmtree(cls_dir, ignore_errors=True)
    os.makedirs(cls_dir)
    pl = pool.makeClass(P + "ProbePlugin", pool.get("com.hypixel.hytale.server.core.plugin.JavaPlugin"))
    pt = pool.makeClass(P + "ProbeTask")
    dt = pool.makeClass(P + "DumpTask")
    for f in ("public static com.hypixel.hytale.logger.HytaleLogger LOG;", "public static java.util.concurrent.ScheduledFuture TICK;"):
        pl.addField(CtField.make(f, pl))
    pl.addConstructor(CtNewConstructor.make("public ProbePlugin(com.hypixel.hytale.server.core.plugin.JavaPluginInit init) { super(init); }", pl))
    pl.addMethod(CtNewMethod.make(r"""
public static void log(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyIslands3Probe] " + s); } catch (Throwable t) { }
}""", pl))
    dt.addInterface(pool.get("java.lang.Runnable"))
    for f in ("public com.hypixel.hytale.server.core.universe.world.World world;", "public ClassLoader cl;", "public String tag;", "public int mode;",
              "public int[] b;", "public java.util.concurrent.CountDownLatch latch = new java.util.concurrent.CountDownLatch(1);"):
        dt.addField(CtField.make(f, dt))
    dt.addConstructor(CtNewConstructor.make("public DumpTask(com.hypixel.hytale.server.core.universe.world.World w, ClassLoader c, String t, int m, int[] bx) { this.world = w; this.cl = c; this.tag = t; this.mode = m; this.b = bx; }", dt))
    dt.addMethod(CtNewMethod.make(DUMP, dt))
    dt.addMethod(CtNewMethod.make(r"""
public static com.skyy.islands3probe.DumpTask on(com.hypixel.hytale.server.core.universe.world.World w, ClassLoader c, String tag, int mode, int[] bx) throws Exception {
  com.skyy.islands3probe.DumpTask d = new com.skyy.islands3probe.DumpTask(w, c, tag, mode, bx);
  w.execute(d);
  if (!d.latch.await(120L, java.util.concurrent.TimeUnit.SECONDS)) com.skyy.islands3probe.ProbePlugin.log(tag + " world thread did not run the dump in 120 s");
  return d;
}""", dt))
    pt.addInterface(pool.get("java.lang.Runnable"))
    for f in ("public static volatile boolean STARTED = false;", "public static int TRIES = 0;", "public int mode;"):
        pt.addField(CtField.make(f, pt))
    pt.addConstructor(CtNewConstructor.make("public ProbeTask(int m) { this.mode = m; }", pt))
    pt.addMethod(CtNewMethod.make(MAKE, pt))
    pt.addMethod(CtNewMethod.make(MAIN.replace("@KA@", KEY_A).replace("@KB@", KEY_B).replace("@KC@", KEY_C).replace("@BA@", ba).replace("@BB@", bb), pt))
    pl.addMethod(CtNewMethod.make(r"""
public void setup() {
  LOG = getLogger();
  log("%s ready - scratch-only engine probe for SkyyIslands %s (built by SkyyIslands/test_skyyislands_%s.py, never deployed)");
  TICK = com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new com.skyy.islands3probe.ProbeTask(0), 3L, 2L, java.util.concurrent.TimeUnit.SECONDS);
}""" % (PROBE_VER, VERSION, VERSION), pl))
    for c in (pl, dt, pt):
        c.writeFile(cls_dir)
    jar = os.path.join(out_dir, "%s-%s.jar" % (PROBE_NAME, PROBE_VER))
    mf = B.manifest(PROBE_NAME, PROBE_VER, "Scratch-only engine probe for SkyyIslands %s (harness; never deployed)." % VERSION, P + "ProbePlugin")
    mf["IncludesAssetPack"] = False
    B.assemble(jar, mf, cls_dir)
    print("probe built:", jar)


def chk(cond, what):
    HK.check(cond, what)          # HK.check answers None - this answers the condition
    return cond


def server_running():
    try:
        sys.path.insert(0, TOOLS)
        import deploy_set as D
        return bool(D.server_running())
    except Exception:
        return False


def run_server():
    if server_running():
        print("S. NOT RUN: the game / a HytaleServer is running (Skyy is play-testing) - the real-server phase is skipped")
        return "NOT RUN"
    os.makedirs(os.path.join(SRV, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SRV, "tmp")
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--probe-build", SRV], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    pjar = os.path.join(SRV, "%s-%s.jar" % (PROBE_NAME, PROBE_VER))
    if not chk(r.returncode == 0 and os.path.isfile(pjar), "S. probe jar built: %s" % (r.stdout[-400:] + r.stderr[-1500:])):
        return "FAIL"
    smoke_dir = os.path.join(TOOLS, "dev", "scratch", "smoke")
    before = set(glob.glob(os.path.join(smoke_dir, "*.log")))
    print("S. starting the real server through tools/smoke_test.py (a few minutes) ...", flush=True)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "smoke_test.py"), "--jar", JAR, "--jar", pjar, "--linger", "150", "--allow-pack-api"],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    if r.returncode == 2:
        print("S. NOT RUN (smoke_test): %s" % out[-400:])
        return "NOT RUN"
    new_logs = sorted(set(glob.glob(os.path.join(smoke_dir, "*.log"))) - before)
    # other builders run smoke tests in parallel: take OUR log (the one with this probe's lines), not just the newest
    new_logs = [f for f in new_logs if ("[%s]" % PROBE_NAME) in open(f, encoding="utf-8", errors="replace").read()] or new_logs
    if not chk(bool(new_logs), "S. the smoke log was written"):
        return "FAIL"
    lines = open(new_logs[-1], encoding="utf-8", errors="replace").read().splitlines()
    print("S. smoke exit %d, log %s" % (r.returncode, os.path.relpath(new_logs[-1], ROOT)))
    text = "\n".join(lines)
    HK.check(re.search(r"\[SkyyIslands\] %s ready\b" % re.escape(VERSION), text) is not None, "S. [SkyyIslands] %s ready in the real server log" % VERSION)
    HK.check(re.search(r"\[%s\] %s ready\b" % (PROBE_NAME, re.escape(PROBE_VER)), text) is not None, "S. the probe loaded")
    bad = [ln for ln in lines if ("com.skyy.islands." in ln or "[SkyyIslands]" in ln) and re.search(r"SEVERE|Exception|Error:|NoSuchMethod", ln)]
    HK.check(not bad, "S. no SkyyIslands SEVERE / exception line: %s" % bad[:4])
    PR = [re.sub(r"^.*?\[%s\] " % PROBE_NAME, "", ln) for ln in lines if "[%s]" % PROBE_NAME in ln]
    IS = [re.sub(r"^.*?\[SkyyIslands\] ", "", ln) for ln in lines if "[SkyyIslands]" in ln]
    for ln in PR:
        if " dump " not in ln:
            print("   probe:", ln[:260])
    HK.check("DONE" in PR and not any("FAILED" in ln or "gave up" in ln or "did not run" in ln for ln in PR), "S. the probe ran to the end: %s" % [ln for ln in PR if "FAIL" in ln or "gave up" in ln][:3])
    m = layout()
    wa, wb = "skyy-island-" + KEY_A, "skyy-island-" + KEY_B

    def dump(tag):
        parts = sorted((int(mm.group(1)), mm.group(3)) for mm in (re.match(r"%s dump (\d+)/(\d+) (.*)$" % tag, ln) for ln in PR) if mm)
        s = "".join(p for _i, p in parts)
        d = {}
        for it in s.split(";"):
            if "=" in it:
                k, v = it.split("=", 1)
                x, y, z = (int(a) for a in k.split(","))
                d[(x, y, z)] = v
        return d
    readyl = [ln for ln in IS if " ready " in ln and "new islands: 3 starter islands (%d blocks)" % len(m.S3_L) in ln]
    HK.check(bool(readyl), "S. the ready line names the 3 starter islands (%d blocks)" % len(m.S3_L))
    h7 = [ln for ln in PR if ln.startswith("H7 design three; island:places %d chars; island:fn:place island2 = %s" % (len(m.S3_PLACES_TEXT), "island|%s|%s|%s|%s" % m.S3_PLACES["island2"]))]
    HK.check(bool(h7), "S. on the real bridge: design three, island:places, island:fn:place island2: %s" % [ln for ln in PR if ln.startswith("H7")])
    placed = [ln for ln in IS if ln.startswith("3 starter islands placed in %s (%d of %d blocks)" % (wa, len(m.S3_L), len(m.S3_L)))]
    HK.check(len(placed) == 1, "S. one '3 starter islands placed in %s (%d of %d blocks)' line: %s" % (wa, len(m.S3_L), len(m.S3_L), [ln for ln in IS if "placed in" in ln]))
    HK.check(any(ln.startswith("starter kit placed in %s" % wa) for ln in IS), "S. the starter kit placed in the 3-island world")
    rel = [ln for ln in IS if ln.startswith("relight queued for %s" % wa)]
    HK.check(bool(rel) and all("(12/12 chunks)" in ln for ln in rel), "S. RelightNow on the 3-island world: 12/12 chunks: %s" % rel)
    d2, d3, d6 = dump("H2"), dump("H3"), dump("H6")
    diff = sorted(set(m.S3_L.items()) ^ set(d2.items()))
    HK.check(d2 == m.S3_L, "S. H2 EVERY block of the 3 islands at its place on the real server = s3_layout() (%d blocks): diff %s" % (len(m.S3_L), diff[:8]))
    HK.check(d3 == d2 and bool(d3), "S. H3 a second fill of the same world changes nothing")
    chest = [ln for ln in PR if ln.startswith("H2 chest ")]
    HK.check(bool(chest) and "Bench_WorkBench x1" in chest[0], "S. H2 the starter chest at 4,129,4 holds the kit: %s" % chest[:1])
    c = classic_layout()
    d4, d5 = dump("H4"), dump("H5")
    HK.check(d4 == c, "S. H4 starter.design=classic -> the next new island = the classic 0.5.9 island block for block (%d): diff %s" % (len(c), sorted(set(c.items()) ^ set(d4.items()))[:6]))
    HK.check(any(ln.startswith("starter island placed in %s (%d blocks)" % (wb, len(c))) for ln in IS), "S. H4 the classic fill's own log line")
    HK.check(d5 == d4 and bool(d5), "S. H5 design three + ChunkFill.load on that EXISTING classic island: nothing changes (old islands untouched)")
    d6diff = sorted(set(d2.items()) ^ set(d6.items()))
    HK.check(d6 == d2, "S. H6 every 3-island section ticking for 6 s: every block stays (no support pop): diff %s" % d6diff[:10])
    tick = [ln for ln in PR if ln.startswith("H6 switched")]
    HK.check(bool(tick) and ("switched %d sections" % len(m.S3_SECTS)) in tick[0], "S. H6 all %d sections switched: %s" % (len(m.S3_SECTS), tick))
    # H8 (fix round): the partly loaded fill retried once and then placed every block
    wc = "skyy-island-" + KEY_C
    short = [ln for ln in IS if ln.startswith("3 starter islands in %s: " % wc) and "one retry" in ln]
    HK.check(len(short) == 1, "S. H8 a 3-island fill with only chunk (0,0) loaded warns once and retries: %s" % [ln for ln in IS if wc in ln][:4])
    HK.check(any(ln.startswith("3 starter islands placed in %s (%d of %d blocks, after one retry)" % (wc, len(m.S3_L), len(m.S3_L))) for ln in IS),
             "S. H8 the retry placed (or found) every block: %s" % [ln for ln in IS if ln.startswith("3 starter islands placed in %s" % wc)])
    HK.check(any(ln == "H8 partly loaded fill finished, tries 1" for ln in PR), "S. H8 FillTask.tries = 1 (exactly one retry)")
    d8 = dump("H8")
    HK.check(d8 == m.S3_L, "S. H8 after the retry EVERY block of the 3 islands is in place: diff %s" % sorted(set(m.S3_L.items()) ^ set(d8.items()))[:8])
    HK.check(any(ln.startswith("starter kit placed in %s" % wc) for ln in IS) and len([ln for ln in IS if ln.startswith("starter kit placed in %s" % wc)]) == 1,
             "S. H8 the starter kit went in ONCE (after the retry pass, not before)")
    # fix round 2: slices, no slow-task WARN, H9
    sl = [re.search(r"in (\d+) world-thread slices$", ln) for ln in IS if ln.startswith("3 starter islands placed in %s (" % wa) and "retry" not in ln]
    HK.check(bool(sl) and all(x is not None and int(x.group(1)) >= 2 for x in sl), "S. fix round 2: the 3-island fill ran in several world-thread slices: %s" % [ln for ln in IS if ln.startswith("3 starter islands placed in")])
    slow = [ln for ln in lines if "Task took" in ln and "FillTask" in ln and KEY_B not in ln]
    HK.check(not slow, "S. fix round 2: no engine 'Task took' WARN for a 3-island FillTask (the classic island B may still warn, 0.5.9 as is): %s" % slow[:3])
    print("S. classic FillTask slow-task WARNs (0.5.9 unchanged): %d" % len([ln for ln in lines if "Task took" in ln and "FillTask" in ln and KEY_B in ln]))
    HK.check("H9 KITDONE has island A: true" in PR, "S. H9 island A's kit is marked given before the retry pass")
    tn = [ln for ln in lines if "Task took" in ln and "com.skyy.islands." in ln and KEY_B not in ln]
    HK.check(not tn, "S. fix round 2: no 'Task took' WARN for any SkyyIslands task on the 3-island worlds: %s" % tn[:3])
    h9 = [ln for ln in PR if ln.startswith("H9 retry pass on the kitted island finished")]
    HK.check(bool(h9) and ("placed %d" % len(m.S3_L)) in h9[0], "S. H9 the retry pass found every block in place: %s" % h9)
    HK.check(any(ln.startswith("starter kit already in the chest of %s" % wa) for ln in IS), "S. H9 the retry pass saw the kit already given and added none")
    HK.check(len([ln for ln in IS if ln.startswith("starter kit placed in %s" % wa)]) == 1, "S. H9 island A's starter kit went in exactly ONCE in the whole run")
    c2 = [ln[len("H2 chest "):] for ln in PR if ln.startswith("H2 chest ")]
    c9 = [ln[len("H9 chest "):] for ln in PR if ln.startswith("H9 chest ")]
    HK.check(bool(c2) and bool(c9) and c9[0].split(":", 1)[-1] == c2[0].split(":", 1)[-1], "S. H9 the chest holds the same single kit as after the build (no second kit, nothing wiped): %s | %s" % (c2[:1], c9[:1]))
    d9 = dump("H9")
    HK.check(d9 == m.S3_L, "S. H9 the retry pass changed no block: diff %s" % sorted(set(m.S3_L.items()) ^ set(d9.items()))[:8])
    mk = [ln for ln in PR if ln.startswith("H1 IslandBuild finished: %s" % wa)]
    print("S. %s" % (mk[0] if mk else "no build time"))
    return "PASS" if not HK.FAILS else "FAIL"


if __name__ == "__main__":
    if "--probe-build" in sys.argv:
        build_probe(os.path.abspath(HK.arg("--probe-build")))
        sys.exit(0)
    srv = None
    if "--phase" not in sys.argv:
        srv = "SKIPPED (--no-server)" if "--no-server" in sys.argv else run_server()
        print("S. real-server phase: %s" % srv)
        if "--keep" not in sys.argv:
            shutil.rmtree(SRV, ignore_errors=True)
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("s3", run_s3), ("snd", T59.run_snd), ("exec", T58.run_exec), ("live", T58.run_live)], script=__file__,
           live=(T58.LIVE_DIR, "Skyy_SkyyIslands"))
