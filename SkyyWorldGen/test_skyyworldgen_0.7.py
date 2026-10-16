"""SkyyWorldGen 0.7 - harness for NATURAL ZONE ISLANDS (tools/worldgen_0_7_patch.py). Bare child JVMs: the game's own JRE, the CACHED 0.7
HytaleServer.jar (tools/serverjar.py), -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The engine
stand-ins (packet sink, store, worlds with a task queue, Universe) come from SkyyProfiles/test_skyyprofiles_0.1.10.py (engine()); the
shared JVM helpers from SkyySkills/test_skyyskills_0.4.27.py (both read only). The live Skyy_SkyyWorldGen folder is only READ (copied into
scratch) and checked afterwards. Plus ONE offline server start (section VP, through tools/smoke_test.py - the only allowed start) when no
HytaleServer runs; while the game is open VP is NOT RUN and says so.

    python SkyyWorldGen/test_skyyworldgen_0.7.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-smoke] [--only-vp]
         [--jar SkyyWorldGen-0.7.jar] [--prev SkyyWorldGen-0.6.jar] [--png-out <folder for the 3 preview PNGs>]

SECTIONS
  CC  CLASS COMPARE 0.6 -> 0.7: + exactly the 8 WgZ2 classes; the 0.5 generator classes AND the 0.6 zone generator classes (WgZoneLayout,
      WgZoneIsles, WgZoneGen, WgZoneFn, WgZoneHop, WgZoneProvider, WgZoneSupplier, WgZoneSampler) + WgSpawnTask / WgDone / WgApplyLanding /
      WgReady / WgStore / WgLog unchanged (= skywynn_zones and the older worlds keep generating exactly as before)
  JT  jar entries: 0.6's + the 8 classes + exactly 2 new files (the SkyWynn_Zones2 template + its InstanceData)
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7 engine
  MK  the 0.7 maths on a SYNTHETIC zone map: the picker, the IRREGULAR outline (purity, spawn disk, cap, connectivity - no slivers, much
      less round than 0.6 on the same map), the islets (count, sizes, near / far, heights, clear of everything, own class), the saved
      layout v2, determinism, chunkOutside; SYNTHETIC chunks through maskWith: a high plateau at the coast is LOWERED (slopes, varied tops,
      vanilla surface re-laid, interior untouched), a lake at the coast gets a natural RIM (no water beside the void), a RIVER keeps its
      mouth open (and is capped with the waterfall switch off), an ISLET column is the vanilla column moved by dy, void columns empty;
      WgZ2Fn failure path, WgZ2Hop, WgZ2Provider offline
  Z   the /zone paths EXECUTED with engine stand-ins: /zone 3 / 2 / 5 / world / old6 / old / 9, the switch off, info / list texts, the
      arrival hop to the 0.7 world, WgCfg.apply (waterfalls, islet counts), WgCheck, the hooks, WgZones.index / label / isIsland
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen (WgCfg.load, WgStore.read, the config kit): no file changed
  VP  the REAL vanilla 0.7 generator: a test probe jar (scratch only) + this jar on an offline server copy (tools/smoke_test.py): the 0.7
      world made by /zone's own code, the layout from the REAL zone map (5 islands + islets, purity, gaps, roundness vs 0.6), sample chunks
      masked vs plain vanilla, a mountain edge / a lake edge / a river mouth found on the coast and dumped, the river mouth LOADED in the
      live world and its waterfall measured over 90 s (fluid voxels, ticking blocks); renders wg07-zone1-map.png / wg07-edges.png /
      wg07-waterfall.png; smoke PASS (--allow-pack-api)
  AA  python tools/ci/crosscheck.py --jar <0.7> --baseline: no FAIL for SkyyWorldGen, the command tree = 0.6's
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time, math, random, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.7", "0.6"
PKG = "com.skyy.worldgen."
NEW_CLASSES = ["WgZ2Fn", "WgZ2Gen", "WgZ2Hop", "WgZ2Isles", "WgZ2Layout", "WgZ2Provider", "WgZ2River", "WgZ2Supplier"]
FROZEN = ["WgIsle", "WgIsleGen", "WgMaskFn", "WgMaskHop", "WgIsleProvider", "WgIsleSupplier", "WgSpawnTask", "WgDone", "WgApplyLanding",
          "WgReady", "WgStore", "WgLog", "WgZoneLayout", "WgZoneIsles", "WgZoneGen", "WgZoneFn", "WgZoneHop", "WgZoneProvider", "WgZoneSupplier",
          "WgZoneSampler"]
ZSEED = 20261014


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "wg07", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyWorldGen-%s.jar" % PREV_VERSION)))
PNG_OUT = os.path.abspath(arg("--png-out", HERE))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyWorldGen")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")     # the shared JVM helpers (read only)
PROF_HARNESS = os.path.join(ROOT, "SkyyProfiles", "test_skyyprofiles_0.1.10.py")   # engine() - the 0.7 stand-ins
FAILS, OKS, NOTES = [], [0], []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ PNG (no PIL here)
class Img:
    def __init__(self, w, h, bg=(0, 0, 0)):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(int(max(0, min(255, v))) for v in c)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return tuple(self.px[i:i + 3])

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.put(x, y, c)

    def paste(self, other, ox, oy):
        for y in range(other.h):
            if 0 <= oy + y < self.h:
                for x in range(other.w):
                    if 0 <= ox + x < self.w:
                        self.put(ox + x, oy + y, other.get(x, y))

    def save(self, path):
        row = self.w * 3
        raw = b"".join(b"\x00" + bytes(self.px[y * row:(y + 1) * row]) for y in range(self.h))

        def ch(t, b):
            return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
                    + ch(b"IDAT", zlib.compress(raw, 6)) + ch(b"IEND", b""))


# the synthetic zone map (Java, compiled in the child): Zone 1 disk at the origin with a big desert hole + a small lake, one disk per
# other class, a second class-4 disk for Zone 5 and a too-shallow class-4 islet
FAKE_DISKS = [  # (cx, cz, r, class) - first match wins
    (300.0, 200.0, 120.0, 2), (-400.0, -300.0, 30.0, 0), (0.0, 0.0, 1500.0, 1), (4000.0, 0.0, 900.0, 2), (0.0, 4500.0, 1000.0, 3),
    (-4200.0, 0.0, 700.0, 4), (0.0, -4200.0, 600.0, 4), (-3000.0, 600.0, 150.0, 4)]


def fake_class(x, z):
    for cx, cz, r, c in FAKE_DISKS:
        if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
            return c
    return 0


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass, JArray, JInt
    import skyybuild as B
    S = mod(SKILLS_HARNESS, "ts0427")
    TP = mod(PROF_HARNESS, "tp0110")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    S.jvm_start([hcls])
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR)):
        L[tag] = S.loader(j)
        R["load"][tag] = S.load_all(j, L[tag])
    try:
        N = TP.engine(S, B, hcls, "skyywg07")
        jf, U = N["jf"], N["U"]
        HPool = JClass("javassist.ClassPool")(False)
        HPool.appendSystemPath()
        Ctm, Ctc, Ctf = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
        fm = HPool.makeClass("skyywg07.FakeMap")
        fm.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        fm.addField(Ctf.make("public int calls;", fm))
        fm.addConstructor(Ctc.make("public FakeMap() { }", fm))
        body = "public int applyAsInt(int x, int z) {\n  this.calls = this.calls + 1;\n"
        for cx, cz, r, c in FAKE_DISKS:
            body += "  if (((double) x - %r) * ((double) x - %r) + ((double) z - %r) * ((double) z - %r) <= %r) return %d;\n" % (cx, cx, cz, cz, r * r, c)
        body += "  return 0;\n}"
        fm.addMethod(Ctm.make(body, fm))
        fh = HPool.makeClass("skyywg07.FlatH")
        fh.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        fh.addField(Ctf.make("public int h;", fh))
        fh.addConstructor(Ctc.make("public FlatH(int h) { this.h = h; }", fh))
        fh.addMethod(Ctm.make("public int applyAsInt(int x, int z) { return this.h; }", fh))
        hc = HPool.makeClass("skyywg07.HCol")
        hc.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        hc.addField(Ctf.make("public int[] hs;", hc))
        hc.addField(Ctf.make("public int cx;", hc))
        hc.addField(Ctf.make("public int cz;", hc))
        hc.addConstructor(Ctc.make("public HCol(int[] hs, int cx, int cz) { this.hs = hs; this.cx = cx; this.cz = cz; }", hc))
        hc.addMethod(Ctm.make("public int applyAsInt(int x, int z) { int lx = x - this.cx * 32; int lz = z - this.cz * 32; if (lx < 0) lx = 0; if (lz < 0) lz = 0; if (lx > 31) lx = 31; if (lz > 31) lz = 31; return this.hs[lx * 32 + lz]; }", hc))
        hr = HPool.makeClass("skyywg07.HRing")
        hr.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        hr.addField(Ctf.make("public int[] hs;", hr))
        hr.addField(Ctf.make("public int cx;", hr))
        hr.addField(Ctf.make("public int cz;", hr))
        hr.addField(Ctf.make("public int out;", hr))
        hr.addConstructor(Ctc.make("public HRing(int[] hs, int cx, int cz, int out) { this.hs = hs; this.cx = cx; this.cz = cz; this.out = out; }", hr))
        hr.addMethod(Ctm.make("public int applyAsInt(int x, int z) { int lx = x - this.cx * 32; int lz = z - this.cz * 32; if (lx < 0 || lz < 0 || lx > 31 || lz > 31) return this.out; return this.hs[lx * 32 + lz]; }", hr))
        rv = HPool.makeClass("skyywg07.Riv")
        rv.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        rv.addField(Ctf.make("public int v;", rv))
        rv.addField(Ctf.make("public int calls;", rv))
        rv.addConstructor(Ctc.make("public Riv(int v) { this.v = v; }", rv))
        rv.addMethod(Ctm.make("public int applyAsInt(int x, int z) { this.calls = this.calls + 1; return this.v; }", rv))
        GCN = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"
        FSN = "com.hypixel.hytale.server.core.universe.world.chunk.section.FluidSection"
        fl = HPool.makeClass("skyywg07.Fill")
        fl.addConstructor(Ctc.make("public Fill() { }", fl))
        # a synthetic column: stone below h-3, 3 dirt, the ground block at h, a marker block at my (if under the dirt), water wb..wt (fid)
        fl.addMethod(Ctm.make("public static " + GCN + " make(int cx, int cz, int[] hs, int ground, int dirt, int stone, int marker, int my, int wb, int wt, int fid, boolean[] wet) {\n"
                              "  " + GCN + " g = new " + GCN + "();\n"
                              "  g.getBlockChunk().setCoordinates(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx, cz), cx, cz);\n"
                              "  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) {\n"
                              "    int h = hs[x * 32 + z];\n"
                              "    for (int y = 0; y <= h; y++) g.getBlockChunk().setBlock(x, y, z, y == h ? ground : (y >= h - 3 ? dirt : (y == my ? marker : stone)), 0, 0);\n"
                              "    if (wet != null && wet[x * 32 + z]) {\n"
                              "      for (int y = wb; y <= wt; y++) {\n"
                              "        " + FSN + " f = (" + FSN + ") g.getSections()[y >> 5].ensureAndGetComponent(" + FSN + ".getComponentType());\n"
                              "        f.setFluid(x, y, z, fid, (byte) 8);\n"
                              "      }\n"
                              "    }\n"
                              "  }\n"
                              "  return g;\n}", fl))
        fl.addMethod(Ctm.make("public static int[] dump(" + GCN + " g) {\n"
                              "  int[] a = new int[32 * 32 * 320];\n"
                              "  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) for (int y = 0; y < 320; y++) a[(x * 32 + z) * 320 + y] = g.getBlockChunk().getBlock(x, y, z);\n"
                              "  return a;\n}", fl))
        fl.addMethod(Ctm.make("public static int[] dumpF(" + GCN + " g) {\n"
                              "  int[] a = new int[32 * 32 * 320];\n"
                              "  for (int s = 0; s < 10; s++) {\n"
                              "    com.hypixel.hytale.component.Holder h = g.getSections()[s];\n"
                              "    " + FSN + " f = h == null ? null : (" + FSN + ") h.getComponent(" + FSN + ".getComponentType());\n"
                              "    if (f == null) continue;\n"
                              "    for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) for (int y = s * 32; y < s * 32 + 32; y++) a[(x * 32 + z) * 320 + y] = f.getFluidId(x, y, z);\n"
                              "  }\n"
                              "  return a;\n}", fl))
        fl.addMethod(Ctm.make("public static int[] envs(" + GCN + " g) {\n"
                              "  int[] a = new int[32 * 32];\n"
                              "  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) a[x * 32 + z] = g.getBlockChunk().getEnvironment(x, 200, z);\n"
                              "  return a;\n}", fl))
        for c_ in (fm, fh, hc, hr, rv, fl):
            c_.writeFile(hcls)
        FakeMap, FlatH, Riv, Fill = JClass("skyywg07.FakeMap"), JClass("skyywg07.FlatH"), JClass("skyywg07.Riv"), JClass("skyywg07.Fill")
        HCol = JClass("skyywg07.HCol")
        HRing = JClass("skyywg07.HRing")
        UUID, Paths, Thread = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Thread")
        TRF = JClass("com.hypixel.hytale.math.vector.Transform")
        GSP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider")
        WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
        WCFGc = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
        UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
        AB = JClass("java.util.concurrent.atomic.AtomicBoolean")
        HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
        RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
        HLB.subscribe(RECS)
        Arr_ = JClass("java.util.Arrays")
        TU = JClass("java.util.concurrent.TimeUnit")

        def sdeq(a, b):
            if a is None or b is None:
                return a is None and b is None
            return bool(Arr_.equals(a, b))

        def logs():
            out_ = []
            for i in range(int(RECS.size())):
                r = RECS.get(i)
                try:
                    out_.append("%s %s" % (r.getLevel(), r.getMessage()))
                except Exception:
                    out_.append(str(r))
            return out_

        def jc(k, n):
            return JClass(PKG + n, loader=L[k])
        for k in ("new", "prev"):
            jc(k, "WgLog").LOG = HL.get("SkyyWorldGenHarness" + k)
        Isl, Lay, Gen = jc("new", "WgZ2Isles"), jc("new", "WgZ2Layout"), jc("new", "WgZ2Gen")
        Isl6 = jc("new", "WgZoneIsles")
        E = {}
        m1 = JArray(jpype.JDouble)(1)
        # ================================================================================ MK: the 0.7 maths on the synthetic map
        smp = FakeMap()
        t0 = time.time()
        Lz = Isl.layout(smp, FlatH(125), 0.5, 0.5, 777, JArray(JInt)([6, 3, 3, 3, 3]))
        lay_s = time.time() - t0
        n = int(Lz.n)
        nm = int(Lz.nMain)
        found = [bool(Lz.found[i]) for i in range(n)]
        cen = [[round(float(Lz.cx[i]), 1), round(float(Lz.cz[i]), 1)] for i in range(n)]
        rad = [float(Lz.rad[i]) for i in range(n)]
        zone = [int(Lz.zone[i]) for i in range(n)]
        dys = [int(Lz.dy[i]) for i in range(n)]
        cells = [int(Lz.cell[i]) for i in range(n)]
        E["mk_layout"] = dict(n=n, nm=nm, found=found, cen=cen, rad=rad, zone=zone, dy=dys, cell=cells, gaps=[float(Lz.gapUsed[i]) for i in range(n)],
                              cls=[int(Lz.cls[i]) for i in range(n)], holes=[int(Lz.holes[i]) for i in range(nm)], filled=[int(Lz.filled[i]) for i in range(nm)],
                              lands=[[float(Lz.lx[i]), float(Lz.lz[i])] for i in range(n)], secs=round(lay_s, 1), spawnCls=int(Lz.spawnCls),
                              text=str(Isl.layoutText(Lz)), lowY=[int(Lz.lowY[i]) for i in range(n)], area=[int(Lz.area[i]) for i in range(n)],
                              size=[max(int(Lz.maxX[i]) - int(Lz.minX[i]), int(Lz.maxZ[i]) - int(Lz.minZ[i])) + int(Lz.cell[i]) for i in range(n)])
        # purity + caps + spawn disk: random points on every main island are its class's land (or the filled small lake), inside the cap
        rng = random.Random(7)
        bad, tested, ins = [], 0, [0] * nm
        for _ in range(9000):
            x = rng.uniform(-5200.0, 5200.0)
            z = rng.uniform(-5200.0, 5600.0)
            ii = int(Isl.member(Lz, x, z, m1))
            if ii < 0 or ii >= nm:
                continue
            tested += 1
            ins[ii] += 1
            c = fake_class(x, z)
            d = math.hypot(x - cen[ii][0], z - cen[ii][1])
            near_edge = min(abs(math.hypot(x - cx, z - cz) - r) for cx, cz, r, _c in FAKE_DISKS) < 16.0
            lake = math.hypot(x + 400.0, z + 300.0) < 30.0
            if (c != int(Lz.cls[ii]) and not lake and not near_edge) or d > rad[ii] + 20.0:
                bad.append([round(x), round(z), c, ii, round(d)])
        spawn_bad = 0
        for _ in range(800):
            a, r_ = rng.uniform(0, 2 * math.pi), 280.0 * math.sqrt(rng.random())
            px_, pz_ = 0.5 + r_ * math.cos(a), 0.5 + r_ * math.sin(a)
            if fake_class(px_, pz_) != 1 or math.hypot(px_ - 300.0, pz_ - 200.0) < 140.0:
                continue            # the big foreign (desert) hole near the spawn stays void, as in 0.6
            if int(Isl.member(Lz, px_, pz_, m1)) != 0:
                spawn_bad += 1
        around = [int(Isl.member(Lz, -400.0 + dx, -300.0 + dz, m1)) for dx, dz in ((60, 0), (-60, 0), (0, 60), (0, -60))]
        E["mk_member"] = dict(tested=tested, bad=bad[:8], nbad=len(bad), insides=ins, spawn_bad=spawn_bad, around=around,
                              lake=int(Isl.member(Lz, -400.0, -300.0, m1)), desert=int(Isl.member(Lz, 300.0, 200.0, m1)))

        # Zone 1 raster (4 blocks): connectivity (no slivers / bits), circularity vs 0.6 on the same map
        def raster(member_fn, idx, cxy, rr, step):
            nn_ = int(2 * rr / step)
            g = bytearray(nn_ * nn_)
            for j in range(nn_):
                for k in range(nn_):
                    if int(member_fn(cxy[0] - rr + j * step + 0.5, cxy[1] - rr + k * step + 0.5)) == idx:
                        g[k * nn_ + j] = 1
            return g, nn_

        def stats(g, nn_, step):
            area = sum(g)
            per = 0
            comp, seen, sizes = 0, bytearray(nn_ * nn_), []
            for p in range(nn_ * nn_):
                if not g[p]:
                    continue
                x, z = p % nn_, p // nn_
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, zz = x + dx, z + dz
                    if xx < 0 or zz < 0 or xx >= nn_ or zz >= nn_ or not g[zz * nn_ + xx]:
                        per += 1
                if not seen[p]:
                    comp += 1
                    st_, cnt = [p], 0
                    seen[p] = 1
                    while st_:
                        q = st_.pop()
                        cnt += 1
                        qx, qz = q % nn_, q // nn_
                        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            xx, zz = qx + dx, qz + dz
                            if 0 <= xx < nn_ and 0 <= zz < nn_ and g[zz * nn_ + xx] and not seen[zz * nn_ + xx]:
                                seen[zz * nn_ + xx] = 1
                                st_.append(zz * nn_ + xx)
                    sizes.append(cnt)
            a_ = area * step * step
            p_ = per * step
            return dict(area=a_, per=p_, circ=round(4 * math.pi * a_ / max(1, p_ * p_), 3), comps=comp, sizes=sorted(sizes)[-4:])
        L6 = Isl6.layout(FakeMap(), 0.5, 0.5, 777)
        g7, n7 = raster(lambda x, z: Isl.member(Lz, x, z, m1), 0, (0.5, 0.5), 1180.0, 4.0)
        g6, n6 = raster(lambda x, z: Isl6.member(L6, x, z, m1), 0, (0.5, 0.5), 1180.0, 4.0)
        E["mk_shape"] = dict(s7=stats(g7, n7, 4.0), s6=stats(g6, n6, 4.0))
        # the synthetic top-down map (for the record; the real one is VP's)
        im = Img(n7 // 2, n7 // 2)
        for j in range(0, n7, 2):
            for k in range(0, n7, 2):
                c7, c6 = g7[k * n7 + j], g6[k * n7 + j]
                im.put(j // 2, k // 2, (70, 140, 60) if c7 else ((55, 55, 65) if c6 else (15, 15, 25)))
        im.save(os.path.join(SCRATCH, "mk_shape.png"))
        # islets: each own class's land, at its deepest point, clear of every main island (>= 8 blocks after the wobble) and other islets
        il = []
        for i in range(nm, n):
            if not found[i]:
                il.append(None)
                continue
            lx_, lz_ = float(Lz.lx[i]), float(Lz.lz[i])
            own = int(Isl.member(Lz, lx_ + 0.5, lz_ + 0.5, m1))
            sdl = list(Lz.sd[i])
            gn_, gx0_, gz0_, cs_ = int(Lz.gn[i]), int(Lz.gx0[i]), int(Lz.gz0[i]), int(Lz.cell[i])
            mind, minother = 1e9, 1e9
            for p_, v_ in enumerate(sdl):
                if v_ <= 0.0:
                    continue
                x, z = gx0_ + (p_ % gn_) * cs_, gz0_ + (p_ // gn_) * cs_
                for j in range(n):
                    if j == i or not found[j]:
                        continue
                    d_ = -float(Isl.sdAt(Lz, j, float(x), float(z)))
                    if j == zone[i]:
                        mind = min(mind, d_)
                    else:
                        minother = min(minother, d_)
            il.append(dict(i=i, zone=zone[i], own=own, cls=fake_class(lx_, lz_), dy=dys[i], size=E["mk_layout"]["size"][i], r=rad[i],
                           gap=float(Lz.gapUsed[i]), mind=round(mind, 1), minother=round(minother, 1), area=int(Lz.area[i])))
        E["mk_islets"] = il
        # bottomOf (main) = the independent formula (as 0.6)
        Old = jc("new", "WgIsle")
        P6 = dict(SKIRT=float(Isl.SKIRT), KEEL=float(Isl.KEEL), RIM=float(Isl.RIM_BOT), MT=float(Isl.MIN_THICK), RA=float(Isl.RA), RS=float(Isl.RS),
                  DRIP=float(Isl.DRIP), DT=float(Isl.DRIP_T), DS=float(Isl.DRIP_S))
        bb = []
        for _ in range(2000):
            e = rng.uniform(0.0, 200.0)
            h = rng.randint(90, 230)
            x = rng.uniform(-9000, 9000)
            z = rng.uniform(-9000, 9000)
            t = min(1.0, max(0.0, 1.0 - e / P6["SKIRT"]))
            sm = t * t * (3.0 - 2.0 * t)
            b = P6["KEEL"] + (P6["RIM"] - P6["KEEL"]) * sm + P6["RA"] * float(Old.vnoise(x, z, P6["RS"], 37)) * sm
            if sm > 0.0:
                dv = float(Old.vnoise(x, z, P6["DS"], 83))
                if dv > P6["DT"]:
                    q = (dv - P6["DT"]) / (1.0 - P6["DT"])
                    b = b - P6["DRIP"] * q * q * min(1.0, sm * 3.0)
                b = min(b, h - P6["MT"])
            b = max(b, P6["KEEL"])
            if int(math.floor(b)) != int(Isl.bottomOf(e, h, x, z)):
                bb.append([round(e, 2), h])
        # islet underside: under the ground by >= ISLE_THICK, >= 1, deeper inside than at the edge
        ib = []
        for i in range(nm, n):
            if not found[i]:
                continue
            h_ = 125 + dys[i]
            b_edge = int(Isl.bottomIsle(Lz, i, 0.5, h_, float(Lz.lx[i]), float(Lz.lz[i])))
            b_in = int(Isl.bottomIsle(Lz, i, rad[i] * 0.9, h_, float(Lz.lx[i]), float(Lz.lz[i])))
            ib.append([i, b_edge, b_in, h_, float(Lz.refY[i]), float(Lz.depth[i])])
        E["mk_bottom"] = dict(bad=bb[:5], nbad=len(bb), islets=ib)
        # chunkOutside is conservative: a chunk with ANY island / islet column is never skipped
        rb, nchunks, nskip = [], 0, 0
        for i in range(n):
            if not found[i]:
                continue
            for k in range(28 if i < nm else 10):
                a = 2.0 * math.pi * k / (28.0 if i < nm else 10.0)
                dd = rad[i] * (1.0 if i >= nm else rng.uniform(0.4, 1.0)) + rng.uniform(-30.0, 40.0)
                cxw, czw = cen[i][0] + dd * math.cos(a), cen[i][1] + dd * math.sin(a)
                ccx, ccz = int(math.floor(cxw / 32.0)), int(math.floor(czw / 32.0))
                nchunks += 1
                if bool(Isl.chunkOutside(Lz, ccx, ccz)):
                    nskip += 1
                    anyin = any(int(Isl.member(Lz, ccx * 32 + lx + 0.5, ccz * 32 + lz + 0.5, m1)) >= 0 for lx in range(32) for lz in range(32))
                    if anyin:
                        rb.append([ccx, ccz])
        E["mk_outside"] = dict(chunks=nchunks, skipped=nskip, bad=rb[:5], far=bool(Isl.chunkOutside(Lz, 60, 60)))
        Lz2 = Isl.layout(FakeMap(), FlatH(125), 0.5, 0.5, 777, JArray(JInt)([6, 3, 3, 3, 3]))
        E["mk_det"] = all(float(Lz.cx[i]) == float(Lz2.cx[i]) and float(Lz.cz[i]) == float(Lz2.cz[i]) and int(Lz.dy[i]) == int(Lz2.dy[i])
                          and bool(Lz.found[i]) == bool(Lz2.found[i]) for i in range(n)) and all(
            sdeq(Lz.sd[i], Lz2.sd[i]) for i in range(n))
        Lz0 = Isl.layout(FakeMap(), FlatH(125), 0.5, 0.5, 777, JArray(JInt)([0, 0, 0, 0, 0]))
        E["mk_noislets"] = [int(Lz0.n), all(sdeq(Lz.sd[i], Lz0.sd[i]) for i in range(nm))]
        # the saved layout v2 (save -> load = identical incl. islets; wrong seed refused; a bare generator reuses it)
        ldir = os.path.join(SCRATCH, "lay")
        os.makedirs(ldir, exist_ok=True)
        Isl.LAYDIR = Paths.get(ldir)
        lf = Isl.layoutFile(777)
        saved_ok = bool(Isl.saveLayout(Lz, lf))
        L3 = Isl.loadLayout(lf, 777)

        def same_lay(A, B_):
            if A is None or B_ is None or int(A.n) != int(B_.n) or int(A.nMain) != int(B_.nMain) or int(A.seed) != int(B_.seed) \
                    or float(A.spx) != float(B_.spx) or int(A.spawnCls) != int(B_.spawnCls):
                return False
            for f_ in ("cx", "cz", "rad", "cls", "found", "gapUsed", "gx0", "gz0", "gn", "lx", "lz", "area", "filled", "holes", "maxsd",
                       "minX", "maxX", "minZ", "maxZ", "zone", "cell", "dy", "lowY", "refY", "depth", "wob", "hmin", "hmax"):
                if not Arr_.equals(getattr(A, f_), getattr(B_, f_)):
                    return False
            return all(sdeq(A.sd[i], B_.sd[i]) for i in range(int(A.n)))
        L3same = same_lay(Lz, L3)
        wrong = Isl.loadLayout(lf, 778)
        wrong_err = str(Isl.LAST_ERR)
        # a 0.6 layout file under the 0.7 name is refused (format), never misread
        lf6 = os.path.join(ldir, "zone2_layout_781.bin")
        Isl6.saveLayout(L6, Paths.get(lf6))
        w6 = Isl.loadLayout(Paths.get(lf6), 781)
        w6_err = str(Isl.LAST_ERR)
        RECS.clear()
        genS = U.allocateInstance(Gen.class_)
        LS = genS.layoutNow(777)
        E["mk_save"] = dict(saved=saved_ok, size=os.path.getsize(str(lf)) if os.path.isfile(str(lf)) else -1, same=L3same,
                            fromFile=None if L3 is None else bool(L3.fromFile), wrong=wrong is None, wrong_err=wrong_err, v6=[w6 is None, w6_err],
                            reuse=[same_lay(Lz, LS), bool(LS.fromFile), bool(genS.laid), [x for x in logs() if "the saved island layout" in x][:1]],
                            name=os.path.basename(str(lf)))
        os.remove(lf6)
        cf = str(Isl.layoutFile(779))
        open(cf, "wb").write(b"junk")
        RECS.clear()
        genC = U.allocateInstance(Gen.class_)
        LC = genC.layoutNow(779)
        fut = genC.generate(779, 0, 0, 0, None, None)
        fut_failed = bool(fut.isCompletedExceptionally())
        try:
            fut.get(5, TU.SECONDS)
            fut_msg = "no error"
        except Exception as e_:
            fut_msg = str(e_)
        E["mk_fail"] = dict(failed=bool(LC.failed), laid=bool(genC.laid), kept=open(cf, "rb").read() == b"junk",
                            unread=[x for x in logs() if "could not be read" in x and "KEPT" in x][:1], fut=[fut_failed, fut_msg[:200]],
                            files=sorted(os.listdir(ldir)))
        Isl.LAYDIR = None
        # ---- SYNTHETIC chunks through maskWith (fake ids: stone 7 = the seal, dirt 9, ground 11-15 per zone, marker 77, water fluid 3)
        Isl.IDS = True
        Isl.STONE = 7
        Isl.ENVV = 99
        Isl.FLE = int(JClass("com.hypixel.hytale.server.core.asset.type.fluid.Fluid").EMPTY_ID)
        IntArr = JArray(JInt)
        gr = JArray(IntArr)(5)
        for i in range(5):
            gr[i] = IntArr([11 + i])
        Isl.GROUND = gr
        Isl.FLOWERS = IntArr(list(range(21, 31)))
        Isl.DECO = IntArr(list(range(31, 31 + len(list(Isl.DECO_NAMES)))))
        Isl.ORE = IntArr([61, 62])
        Isl.HOST = IntArr([7])
        Isl.SHORE = IntArr([9, 41, 7, 42, 42])
        Isl.DIRT = 9
        Isl.WATER = IntArr([3, 4])
        kind = JArray(jpype.JByte)(128)
        for k_ in range(1, 128):
            kind[k_] = 1 if k_ in (7, 9, 11, 12, 13, 14, 15, 41, 42) else 2
        Isl.KIND = kind
        CSr = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore")
        LMc = JClass("com.hypixel.hytale.server.core.modules.LegacyModule")
        lm_ = LMc.get()
        if lm_ is None:
            lm_ = U.allocateInstance(LMc.class_)
            jf(LMc.class_, "instance").set(None, lm_)
        P_s = "com.hypixel.hytale.server.core.universe.world.chunk.section."
        for fld_, cn_, key_ in (("fluidSectionComponentType", P_s + "FluidSection", "Fluid"),
                                ("blockComponentSectionComponentType", P_s + "BlockComponentSection", "BlockComponent")):
            if jf(LMc.class_, fld_).get(lm_) is None:
                C_s = JClass(cn_)
                jf(LMc.class_, fld_).set(lm_, CSr.REGISTRY.registerComponent(C_s.class_, key_, jf(C_s.class_, "CODEC").get(None)))
        ROOTS = 31 + int(Isl.D_ROOTS)
        WATER = 3

        def chunk_at(x, z):
            return int(math.floor(x / 32.0)), int(math.floor(z / 32.0))

        def coast_chunk(i, ang_deg):
            """the chunk holding island i's coast on a ray from its centre (last inside point)"""
            ux, uz = math.cos(math.radians(ang_deg)), math.sin(math.radians(ang_deg))
            last = None
            t = 0.0
            while t < rad[i] + 60:
                x, z = cen[i][0] + ux * t, cen[i][1] + uz * t
                if int(Isl.member(Lz, x, z, m1)) == i:
                    last = (x, z)
                t += 2.0
            return chunk_at(*last), last

        def plan_cols(ccx, ccz):
            P = {}
            for lx in range(32):
                for lz in range(32):
                    ii = int(Isl.member(Lz, ccx * 32 + lx + 0.5, ccz * 32 + lz + 0.5, m1))
                    P[(lx, lz)] = (ii, float(m1[0]) if ii >= 0 else -1.0)
            return P

        def run_chunk(ccx, ccz, hs_col, ground, wet=None, wb=0, wt=0, fid=WATER, river=0, my=-1, hop=None, pre=None):
            hs = IntArr(hs_col)
            wa = JArray(jpype.JBoolean)(wet) if wet is not None else None
            g = Fill.make(ccx, ccz, hs, ground, 9, 7, 77, my, wb, wt, fid, wa)
            if pre is not None:
                pre(g)
            rr = Riv(river)
            nin = int(Isl.maskWith(g, ccx, ccz, Lz, hop if hop is not None else FlatH(hs_col[0]), rr))
            return g, list(Fill.dump(g)), list(Fill.dumpF(g)), list(Fill.envs(g)), int(rr.calls), nin

        def top_of(col):
            for y in range(319, -1, -1):
                if col[y] != 0:
                    return y
            return -1
        res = {}
        # T1: a HIGH plateau (y 200, the island floor ~y 125) at a Zone 1 coast -> lowered toward the rim, varied, surface kept
        # a Zone 1 coast chunk with void AND land 25+ blocks in (the irregular coast: try rays until one fits)
        for ang in range(10, 370, 10):
            (cx1, cz1), pt1 = coast_chunk(0, float(ang))
            P1 = plan_cols(cx1, cz1)
            if max(e for ii, e in P1.values()) >= 25.0 and sum(1 for ii, e in P1.values() if ii < 0) > 50:
                break
        g, A, F, ENV, _rc, nin = run_chunk(cx1, cz1, [200] * 1024, 11)
        tops, band_out, edge_tops, surf_bad, void_bad, below_bad, shell_bad = [], [], [], 0, 0, 0, 0
        low_n = 0
        floor = int(Lz.lowY[0])
        for (lx, lz), (ii, e) in P1.items():
            col = A[(lx * 32 + lz) * 320:(lx * 32 + lz + 1) * 320]
            if ii < 0:
                if any(col) or ENV[lx * 32 + lz] != 99:
                    void_bad += 1
                continue
            b = int(Isl.bottom2(Lz, ii, e, 200, cx1 * 32 + lx + 0.5, cz1 * 32 + lz + 0.5))
            if any(v not in (0, ROOTS) for v in col[:b]):
                below_bad += 1
            if col[b] == 0 or col[b + 1] == 0:
                shell_bad += 1
            t_ = top_of(col)
            gt = t_
            while gt > 0 and not (col[gt] in (11, 9, 7)):
                gt -= 1
            if e < 40.0:
                tops.append((e, gt))
                if gt < 199:
                    low_n += 1
                    if col[gt] != 11 or col[gt - 1] != 9:
                        surf_bad += 1
                if e < 2.0:
                    edge_tops.append(gt)
            elif gt != 200 or col[200] != 11:
                band_out.append([lx, lz, round(e, 1), gt])
        near = [t for e, t in tops if e < 4.0]
        mid = [t for e, t in tops if 12.0 <= e < 20.0]
        res["t1"] = dict(chunk=[cx1, cz1], floor=floor, nin=nin, low_n=low_n, ncols=len(tops), edge=[min(edge_tops) if edge_tops else None,
                         max(edge_tops) if edge_tops else None, round(sum(edge_tops) / max(1, len(edge_tops)), 1),
                         round((sum((t - sum(edge_tops) / max(1, len(edge_tops))) ** 2 for t in edge_tops) / max(1, len(edge_tops))) ** 0.5, 2)],
                         near=round(sum(near) / max(1, len(near)), 1), mid=round(sum(mid) / max(1, len(mid)), 1), surf_bad=surf_bad,
                         band_out=band_out[:4], void_bad=void_bad, below_bad=below_bad, shell_bad=shell_bad, lowered=int(Isl.LOWERED.get()))
        # T2: a LAKE (bed y 136, water 137-141) across a Zone 1 coast -> a natural rim (shore block, one above the water), no water by the void
        (cx2, cz2), pt2 = coast_chunk(0, 200.0)
        P2 = plan_cols(cx2, cz2)

        def lake_check(A, F, P, ccx, ccz, river):
            rim, kept, exposed, mouth, rim_bad, inner_dry = 0, 0, 0, 0, 0, 0
            for (lx, lz), (ii, e) in P.items():
                if ii < 0:
                    continue
                base = (lx * 32 + lz) * 320
                wcol = F[base:base + 320]
                bcol = A[base:base + 320]
                has_w = any(wcol[137:142])
                voidn = any(P.get((lx + dx, lz + dz), (0, 0))[0] < 0 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
                            if (lx + dx, lz + dz) in P)
                if has_w:
                    kept += 1
                    if voidn:
                        if river:
                            mouth += 1
                        else:
                            exposed += 1
                elif e < 6.0:
                    rim += 1
                    if not (all(bcol[y] == 9 for y in range(137, 142)) and bcol[142] == 11):
                        rim_bad += 1
                if e > 6.0 and not has_w:
                    inner_dry += 1
            return dict(rim=rim, kept=kept, exposed=exposed, mouth=mouth, rim_bad=rim_bad, inner_dry=inner_dry)
        wet = [True] * 1024
        g, A, F, ENV, rc, nin = run_chunk(cx2, cz2, [136] * 1024, 9, wet, 137, 141, WATER, 0)
        res["t2"] = dict(lake_check(A, F, P2, cx2, cz2, False), chunk=[cx2, cz2], rcalls=rc, rimmed=int(Isl.RIMMED.get()))
        # T3: the same water as a RIVER (biome test = 1) -> the mouth stays open (water beside the void), nothing rimmed; switch off -> rim
        Isl.MOUTH_N.set(0)
        g, A, F, ENV, rc, nin = run_chunk(cx2, cz2, [136] * 1024, 9, wet, 137, 141, WATER, 1)
        under = 0
        for (lx, lz), (ii, e) in P2.items():
            if ii < 0:
                continue
            b = int(Isl.bottom2(Lz, ii, e, 136, cx2 * 32 + lx + 0.5, cz2 * 32 + lz + 0.5))
            col = F[(lx * 32 + lz) * 320:(lx * 32 + lz + 1) * 320]
            if any(col[:137]) or (col[b] if b < 320 else 0):
                under += 1
        res["t3"] = dict(lake_check(A, F, P2, cx2, cz2, True), rcalls=rc, mouths=int(Isl.MOUTH_N.get()), under=under)
        g, A, F, ENV, rc, nin = run_chunk(cx2, cz2, [136] * 1024, 9, wet, 137, 141, 5, 1)
        res["t3lava"] = dict(lake_check(A, F, P2, cx2, cz2, False), rcalls=rc)
        Isl.WATERFALLS = False
        g, A, F, ENV, rc, nin = run_chunk(cx2, cz2, [136] * 1024, 9, wet, 137, 141, WATER, 1)
        res["t3off"] = dict(lake_check(A, F, P2, cx2, cz2, False), rcalls=rc)
        Isl.WATERFALLS = True
        # T4: an ISLET column = the vanilla column moved by dy (marker y 100 -> 100 + dy, ground 130 -> 130 + dy away from its edge)
        isl_i = max((i for i in range(nm, n) if found[i]), key=lambda i: int(Lz.area[i]), default=None)
        if isl_i is not None:
            lx0, lz0 = float(Lz.lx[isl_i]), float(Lz.lz[isl_i])
            cx4, cz4 = chunk_at(lx0, lz0)
            P4 = plan_cols(cx4, cz4)
            dy = dys[isl_i]
            icols = [(lx, lz) for (lx, lz), (ii, e) in P4.items() if ii == isl_i]

            def pre4(g_):
                bc_ = g_.getBlockChunk()
                for lx, lz in icols:
                    bc_.setEnvironmentColumn(lx, lz, 8)
                    for y in range(0, 111):
                        bc_.setEnvironment(lx, y, lz, 5)
            g, A, F, ENV, rc, nin = run_chunk(cx4, cz4, [130] * 1024, 11, my=120, hop=FlatH(130), pre=pre4)
            bc4 = g.getBlockChunk()
            env_bad = [[lx, lz, int(bc4.getEnvironment(lx, y, lz))] for lx, lz in icols for y in (max(0, 100 + dy), min(319, 132 + dy), 300)
                       if int(bc4.getEnvironment(lx, y, lz)) != 8]
            moved, mbad, top_ok, top_n, cols, below_bad4 = 0, [], 0, 0, 0, 0
            for (lx, lz), (ii, e) in P4.items():
                if ii != isl_i:
                    continue
                cols += 1
                col = A[(lx * 32 + lz) * 320:(lx * 32 + lz + 1) * 320]
                b = int(Isl.bottom2(Lz, ii, e, 130 + dy, cx4 * 32 + lx + 0.5, cz4 * 32 + lz + 0.5))
                if any(v not in (0, ROOTS) for v in col[:b]):
                    below_bad4 += 1
                if b <= 120 + dy - 1:
                    if col[120 + dy] == 77:
                        moved += 1
                    else:
                        mbad.append([lx, lz, b, col[120 + dy]])
                if e >= 10.0:
                    top_n += 1
                    if col[130 + dy] == 11 and col[131 + dy] in (0,) + tuple(range(21, 31 + len(list(Isl.DECO_NAMES)))):
                        top_ok += 1
            res["t4"] = dict(islet=isl_i, dy=dy, cols=cols, moved=moved, mbad=mbad[:4], top_ok=top_ok, top_n=top_n, below_bad=below_bad4,
                             shifted=int(Isl.SHIFTED.get()), env_cols=len(icols), env_bad=env_bad[:4], env_nbad=len(env_bad))
        else:
            res["t4"] = None
        # T5: a stream (y 141-143 over a y 140 bed, columns lx 14-16) through the high plateau at the coast: the banks next to it are never
        # lowered under its water (no sideways spill along the coast); banks far from it are lowered as in T1
        hs5 = [140 if 14 <= lx <= 16 else 170 for lx in range(32) for lz in range(32)]
        wet5 = [14 <= lx <= 16 for lx in range(32) for lz in range(32)]
        g, A, F, ENV, rc, nin = run_chunk(cx1, cz1, hs5, 11, wet5, 141, 143, WATER, 0, hop=jc("new", "WgZ2Isles") and HCol(IntArr(hs5), cx1, cz1))
        near_low, far_low, near_n, far_n = [], [], 0, 0
        for (lx, lz), (ii, e) in P1.items():
            if ii < 0 or e >= 30.0:
                continue
            col = A[(lx * 32 + lz) * 320:(lx * 32 + lz + 1) * 320]
            gt = top_of(col)
            while gt > 0 and not (col[gt] in (11, 9, 7)):
                gt -= 1
            dl = abs(lx - 15)
            # "near" = an ISLAND stream column within WATER_KEEP (3) - at an irregular coast the stream's own columns may be void there
            wet_near = any(P1[(a_, b_)][0] >= 0 for a_ in range(14, 17) for b_ in range(max(0, lz - 3), min(31, lz + 3) + 1) if abs(a_ - lx) <= 3)
            if 2 <= dl <= 4 and wet_near:
                near_n += 1
                if gt < 144:
                    near_low.append([lx, lz, round(e, 1), gt])
            elif dl >= 8 and e < 10.0:
                far_n += 1
                if gt > 160:
                    far_low.append([lx, lz, round(e, 1), gt])
        res["t5"] = dict(near_n=near_n, near_low=near_low[:5], far_n=far_n, far_high=far_low[:5])
        # T6 (fix round, critic: a lake beside a chunk border spilled into the neighbour's lowered bank): the T1 coast chunk at y 170, a
        # 1-wide lake (bed 140, water 141-143) along the edge whose neighbour columns lowTarget lowers most; the ring across = y 170 banks
        best6 = None
        for edge in range(4):
            cnt, exp_ = 0, []
            for t_ in range(32):
                lx, lz = ((0, t_), (31, t_), (t_, 0), (t_, 31))[edge]
                nx, nz = ((-1, t_), (32, t_), (t_, -1), (t_, 32))[edge]
                x, z = cx1 * 32 + nx, cz1 * 32 + nz
                ii = int(Isl.member(Lz, x + 0.5, z + 0.5, m1))
                if ii < 0:
                    continue
                e6 = float(m1[0])
                b6 = int(Isl.bottom2(Lz, ii, e6, 170 + dys[ii], x + 0.5, z + 0.5))
                nt = int(Isl.lowTarget(Lz, ii, x, z, e6, 170 + dys[ii], b6))
                if nt < 170 and nt <= 143:
                    cnt += 1
                    exp_.append((lx, lz))
            if best6 is None or cnt > best6[1]:
                best6 = (edge, cnt, exp_)
        edge6, cnt6, exp6 = best6
        row6 = set(((0, t_), (31, t_), (t_, 0), (t_, 31))[edge6] for t_ in range(32))
        hs6 = [140 if (lx, lz) in row6 else 170 for lx in range(32) for lz in range(32)]
        wet6 = [(lx, lz) in row6 for lx in range(32) for lz in range(32)]
        br0 = int(Isl.BORDER_RIM.get())
        g, A, F, ENV, rc, nin = run_chunk(cx1, cz1, hs6, 11, wet6, 141, 143, WATER, 0, hop=HRing(IntArr(hs6), cx1, cz1, 170))
        left_exp, kept_safe, coast_rim = [], 0, 0
        for (lx, lz) in sorted(row6):
            ii, e6 = P1[(lx, lz)]
            if ii < 0:
                continue
            base = (lx * 32 + lz) * 320
            has_w = any(F[base + 141:base + 144])
            if (lx, lz) in exp6:
                if has_w:
                    left_exp.append([lx, lz])
            elif has_w:
                kept_safe += 1
        res["t6"] = dict(edge=edge6, exposed=len(exp6), left=left_exp[:5], nleft=len(left_exp), kept_safe=kept_safe,
                         border_rims=int(Isl.BORDER_RIM.get()) - br0)
        E["mk_chunk"] = res
        # WgZ2Fn failure path / WgZ2Hop / provider offline
        Fn, Hop = jc("new", "WgZ2Fn"), jc("new", "WgZ2Hop")
        genA = U.allocateInstance(Gen.class_)
        genA.lay = Lz
        genA.laid = True
        genA.lseed = 0
        RECS.clear()
        fn = Fn(genA, 0, cx1, cz1)
        g0 = Fill.make(cx1, cz1, IntArr([140] * 1024), 11, 9, 7, 77, -1, 0, 0, 0, None)
        f0 = int(Isl.FAILED.get())
        try:
            fn.apply(g0)
            thrown = None
        except Exception as e_:
            thrown = str(e_)
        failed = [int(Isl.FAILED.get()) - f0, thrown is not None and "the engine retries it" in thrown,
                  [x for x in logs() if "masking chunk" in x and "NOT saved" in x][:1], str(fn.apply("not a chunk"))]
        ex = JClass("java.util.concurrent.Executors").newSingleThreadExecutor()
        fn2 = Fn(genA, 0, 9999, 9999)
        hop = Hop(fn2, Thread.currentThread(), ex)
        h0 = int(Isl.HOPPED.get())
        r1 = hop.apply(Fill.make(9999, 9999, IntArr([100] * 1024), 11, 9, 7, 77, -1, 0, 0, 0, None)).get(30, TU.SECONDS)
        r2 = Hop(fn2, None, ex).apply(Fill.make(9999, 9999, IntArr([100] * 1024), 11, 9, 7, 77, -1, 0, 0, 0, None)).get(30, TU.SECONDS)
        ex.shutdown()
        E["mk_fn"] = dict(failed=failed, hopped=int(Isl.HOPPED.get()) - h0, empty1=all(int(r1.getBlockChunk().getBlock(0, y, 0)) == 0 for y in range(320)),
                          empty2=all(int(r2.getBlockChunk().getBlock(5, y, 5)) == 0 for y in range(320)))
        Prov = jc("new", "WgZ2Provider")
        RECS.clear()
        try:
            Prov().getGenerator()
            perr = "no error"
        except Exception as e_:
            perr = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
        E["mk_prov"] = [perr, [x for x in logs() if "could not be loaded for the zone islands world" in x][:1], Prov.CODEC is not None, str(Prov().toString())]
        # ================================================================================ Z: the /zone paths with engine stand-ins
        WN = [str(x) for x in jc("new", "WgZones").WORLDS]
        uni = UniC.get()
        byname = jf(UniC.class_, "worlds").get(uni)

        def world(name, gen=None):
            w, wu, cfg = N["mkworld"](name)
            jf(WLDc.class_, "alive").set(w, AB(True))
            byname.put(name.lower(), w)
            if gen is not None:
                jf(WCFGc.class_, "worldGenProvider").set(cfg, gen)
            return w, wu, cfg
        HUB, HUBU, HUBC = world("harness_main")
        ZW, ZWU, ZWC = world(WN[3], U.allocateInstance(jc("new", "WgZ2Provider").class_))
        OW, OWU, OWC = world(WN[2], U.allocateInstance(jc("new", "WgZoneProvider").class_))
        CSc = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore")
        cs = U.allocateInstance(CSc.class_)
        jf(CSc.class_, "generatorLock").set(cs, JClass("java.util.concurrent.locks.StampedLock")())
        jf(CSc.class_, "generator").set(cs, genA)
        jf(WLDc.class_, "chunkStore").set(ZW, cs)
        HPc = JClass("com.hypixel.hytale.builtin.hytalegenerator.plugin.HandleProvider")
        hp = U.allocateInstance(HPc.class_)
        hp.setWorldStructureName(str(jc("new", "WgZones").STRUCTURES[0]))
        Z1, Z1U, Z1C = world(WN[0], hp)
        N["UniH"].DEF = HUB
        HUBC.setSpawnProvider(GSP(TRF(0.5, 120.0, 0.5, 0.0, 0.0, 0.0)))
        Chk, Cfg, Cmds, Open, Zn = jc("new", "WgCheck"), jc("new", "WgCfg"), jc("new", "WgCmds"), jc("new", "WgOpen"), jc("new", "WgZones")
        Isl.REGISTERED = True
        Isl6.REGISTERED = True
        for i in range(4):
            Chk.OK[i] = True
        U1 = UUID.fromString("00000000-0000-0000-0000-0000000000e7")

        def on(w, wu):
            return N["player"](U1, w, wu)

        def go(P, w, a):
            try:
                Cmds.goCmd(P.st, P.ref, P.pr, w, a)
                err = None
            except Exception as e_:
                err = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
            return [N["tp_of"](P), N["chat"](P), err]
        Cfg.NEW06 = True
        P = on(HUB, HUBU)
        E["z1"] = [int(Open.decide(3, HUB))] + go(P, HUB, "3")
        P = on(ZW, ZWU)
        E["z2"] = [int(Open.decide(3, ZW))] + go(P, ZW, "2")
        Lz.found[4] = False
        P = on(ZW, ZWU)
        E["z3"] = go(P, ZW, "5")
        Lz.found[4] = True
        Cfg.NEW06 = False
        P = on(HUB, HUBU)
        E["z4a"] = go(P, HUB, "3")
        P = on(Z1, Z1U)
        E["z4b"] = go(P, Z1, "1")
        Cfg.NEW06 = True
        P = on(Z1, Z1U)
        E["z5"] = go(P, Z1, "old")
        P = on(ZW, ZWU)
        E["z6"] = go(P, ZW, "world")
        P = on(ZW, ZWU)
        E["z6b"] = go(P, ZW, "z4")
        P = on(HUB, HUBU)
        E["z6c"] = go(P, HUB, "old6")
        P = on(HUB, HUBU)
        E["z7"] = go(P, HUB, "9")
        P = on(ZW, ZWU)
        E["z9"] = [str(x) for x in Cmds.infoLines(P.st, P.ref, P.pr, ZW)]
        E["z10"] = str(jc("new", "WgHereTask").setHere(P.st, P.ref, P.pr, ZW))
        E["z11"] = [[str(x) for x in Cmds.listLines()]]
        Cfg.NEW06 = False
        E["z11"].append([str(x) for x in Cmds.listLines()])
        Props = JClass("java.util.Properties")

        def apply(txt):
            p_ = Props()
            p_.load(JClass("java.io.StringReader")(txt))
            Cfg.apply(p_)
            return [bool(Cfg.NEW06), bool(Isl.WATERFALLS), int(Isl.ISLETS1), int(Isl.ISLETS25), str(Cfg.LOADED)]
        E["z12"] = [apply("zones.islands06=false\n"), apply("zones.islands06=true\nzones.waterfalls=false\nzones.islets1=9\nzones.islets25=0\n"),
                    apply("zones.waterfalls=on\nzones.islets1=99\nzones.islets25=x\n"), apply("part.zones=true\nzones.islets1=6\nzones.islets25=3\n")]
        Cfg.NEW06 = True
        Isl.WATERFALLS = True
        Chk.OK[3] = False
        Isl.REGISTERED = False
        z13a = Chk.structureProblem(3)
        Isl.REGISTERED = True
        z13b = Chk.structureProblem(3)
        E["z13"] = [None if z13a is None else str(z13a), None if z13b is None else str(z13b)]
        Hk = jc("new", "WgHooks")
        E["z14"] = [str(Hk.customGet("info.zworld")), str(Hk.customGet("info.zsizes")), str(Hk.customGet("info.world"))]
        E["z15"] = [int(Zn.index(a)) for a in ("zones", "06", "old6", "world", "07", "zones2", "old", "1", "proof", "nope")] + [
            str(Zn.label(3)), bool(Zn.isIsland(3, ZW)), bool(Zn.isIsland(3, OW)), bool(Zn.isIsland(2, OW)), int(Zn.islandIndex(ZW)), str(Zn.ringAt(3, 0.0, 0.0)),
            [str(x) for x in Zn.WORLDS], [str(x) for x in Zn.TEMPLATES], [str(x) for x in Zn.STRUCTURES], [str(x) for x in Zn.IDS]]
        ZWC.setSpawnProvider(GSP(TRF(5.5, 130.0, 5.5, 0.0, 0.0, 0.0)))
        E["z18"] = [bool(jc("new", "WgApplyLanding").applyTo(ZW)), Cfg.landing(3) is None, Cfg.landing(2) is None]
        byname.remove(WN[3].lower())
        P = on(HUB, HUBU)
        try:
            d4 = int(Open.decide(3, HUB))
        except Exception as e_:
            d4 = "error " + str(e_)
        Arr = jc("new", "WgZoneArrive")
        Arr.HOPS.clear()
        E["z8"] = [d4] + go(P, HUB, "4")
        h8 = Arr.HOPS.get(str(U1))
        E["z8hop"] = None if h8 is None else [int(h8[0]), int(h8[1]) - int(JClass("java.lang.System").currentTimeMillis())]
        byname.put(WN[3].lower(), ZW)
        PREc = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
        PLYc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        JLongArr = JArray(jpype.JLong)
        nowms = int(JClass("java.lang.System").currentTimeMillis())

        def ready(P_):
            ply = U.allocateInstance(PLYc.class_)
            jf(PLYc.class_, "playerRef").set(ply, P_.pr)
            return PREc(P_.ref, ply, 1)
        N["run_world"](ZW)
        N["run_world"](HUB)
        Arr.HOPS.clear()
        Arr.HOPS.put(str(U1), JLongArr([3, nowms + 60000]))
        P = on(ZW, ZWU)
        m0 = int(Arr.MOVED.get())
        Arr().accept(ready(P))
        ran = N["run_world"](ZW)
        E["z19"] = [ran, N["tp_of"](P), N["chat"](P), int(Arr.HOPS.size()), int(Arr.MOVED.get()) - m0]
        Arr.HOPS.put(str(U1), JLongArr([2, nowms + 60000]))
        P = on(OW, OWU)
        Arr().accept(ready(P))
        E["z21"] = [N["run_world"](OW), N["tp_of"](P), int(Arr.HOPS.size())]
        Arr.HOPS.clear()
        tdir = os.path.join(SCRATCH, "tpl")
        os.makedirs(tdir, exist_ok=True)
        tp_ = os.path.join(tdir, "zones2.bson")
        with zipfile.ZipFile(JAR) as zj:
            open(tp_, "wb").write(zj.read("Server/Instances/SkyWynn_Zones2/instance.bson"))
        IWG = JClass("com.hypixel.hytale.server.core.universe.world.worldgen.provider.IWorldGenProvider")
        try:
            IWG.CODEC.register(str(Isl.TYPE), Prov.class_, Prov.CODEC)
            wc = WCFGc.load(Paths.get(tp_)).get(30, TU.SECONDS)
            gp = wc.getWorldGenProvider()
            E["qz"] = [None if gp is None else str(gp.getClass().getName()), int(wc.getSeed()), str(wc.getDisplayName()),
                       jf(WCFGc.class_, "spawnProvider").get(wc) is None, str(wc.getGameMode())]
        except Exception as e_:
            E["qz"] = ["error", str(e_)[:300]]
        # ================================================================================ ST: two starts on a COPY of the live data
        home = os.path.join(SCRATCH, "st", "mods", "Skyy_SkyyWorldGen")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        Store, Pub = jc("new", "WgStore"), jc("new", "CfgPub")
        starts = []
        for n_ in range(2):
            b0 = snap(home)
            Cfg.DIR = Paths.get(home)
            Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
            Store.FILE = Paths.get(os.path.join(home, "worlds.properties"))
            Cfg.load()
            Store.read()
            Pub.start(Paths.get(os.path.dirname(home)), None)
            Pub.flush()
            time.sleep(0.4)
            Pub.flush()
            made = Store.createdText(jc("new", "WgZones").WORLDS[3])
            made6 = Store.createdText(jc("new", "WgZones").WORLDS[2])
            Pub.shutdown()
            a0 = snap(home)
            starts.append([sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), None if made is None else str(made),
                           None if made6 is None else str(made6), str(Cfg.LOADED)[:160], bool(Cfg.NEW06), bool(Isl.WATERFALLS), int(Isl.ISLETS1)])
        E["st"] = [starts, len(snap(home)), "zones.waterfalls" in open(os.path.join(home, "config.properties"), encoding="latin-1").read()
                   if os.path.isfile(os.path.join(home, "config.properties")) else None]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    ml = E["mk_layout"]
    nm, n = ml["nm"], ml["n"]
    print("MK. synthetic layout: %s (%.1f s)" % (ml["text"], ml["secs"]))
    check(ml["found"][:5] == [True] * 5 and ml["cls"][:5] == [1, 2, 3, 4, 4] and ml["spawnCls"] == 1 and nm == 5 and n == 5 + 6 + 12,
          "MK: the picker finds all 5 zones (classes 1,2,3,4,4) + 18 islet slots: %s n %d" % (ml["found"][:5], n))
    c = ml["cen"]
    check(c[0] == [0.5, 0.5] and math.hypot(c[1][0] - 4000.0, c[1][1]) < 900 and math.hypot(c[2][0], c[2][1] - 4500.0) < 1000
          and math.hypot(c[3][0] + 4200.0, c[3][1]) < 700 and math.hypot(c[4][0], c[4][1] + 4200.0) < 600,
          "MK: Zone 1 = the spawn point, Zones 2-5 in their own class's land (the 0.6 picker unchanged): %s" % c[:5])
    check(ml["gaps"][:5] == [1100.0] * 5, "MK: every zone island placed with the full 1,100-block gap: %s" % ml["gaps"][:5])
    mm = E["mk_member"]
    check(mm["tested"] > 500 and mm["nbad"] == 0 and all(x > 0 for x in mm["insides"]),
          "MK: every sampled island point is its own zone class's land inside its radius cap (%d points, per island %s): %d wrong %s"
          % (mm["tested"], mm["insides"], mm["nbad"], mm["bad"]))
    check(mm["spawn_bad"] == 0 and (mm["lake"] == 0 or (mm["lake"] == -1 and mm["around"] != [0, 0, 0, 0])) and mm["desert"] == -1, "MK: the 280-block disk around the Zone 1 spawn is all island "
          "(%d misses); the small lake is filled (%d), the big foreign hole stays void (%d)" % (mm["spawn_bad"], mm["lake"], mm["desert"]))
    sh = E["mk_shape"]
    print("MK. Zone 1 shape 0.7 %s | 0.6 %s" % (sh["s7"], sh["s6"]))
    check(sh["s7"]["comps"] == 1, "MK: the Zone 1 island is ONE connected piece on a 4-block raster - no slivers or detached bits: %s" % sh["s7"])
    check(sh["s7"]["circ"] < 0.75 * sh["s6"]["circ"] and sh["s7"]["circ"] < 0.45, "MK: clearly less round than 0.6 on the same map - circularity "
          "4 pi A / P^2 %.3f vs 0.6 %.3f (a disk = 1)" % (sh["s7"]["circ"], sh["s6"]["circ"]))
    check(0.4 * sh["s6"]["area"] < sh["s7"]["area"] <= sh["s6"]["area"] * 1.02, "MK: still ONE big Zone 1 island - %.2f km2 vs 0.6 %.2f km2"
          % (sh["s7"]["area"] / 1e6, sh["s6"]["area"] / 1e6))
    il = [x for x in E["mk_islets"] if x]
    z1 = [x for x in il if x["zone"] == 0]
    print("MK. islets: %s" % [(x["i"], x["zone"], x["size"], x["dy"], round(x["gap"]), x["mind"] if x["mind"] < 1e8 else None) for x in il])
    check(len(z1) >= 5 and len(il) >= 10, "MK: islets placed - Zone 1 %d of 6, all zones %d of 18" % (len(z1), len(il)))
    check(all(x["own"] == x["i"] and x["cls"] == ml["cls"][x["zone"]] for x in il), "MK: every islet stands on its own zone class's vanilla land "
          "(its deepest point is the islet itself): %s" % [(x["i"], x["own"], x["cls"]) for x in il if x["own"] != x["i"] or x["cls"] != ml["cls"][x["zone"]]])
    check(all(8 <= x["size"] <= 170 for x in il) and max(x["size"] for x in il) >= 60, "MK: islet sizes ~12-160 blocks across (+ a grid cell): %s" % sorted(x["size"] for x in il))
    z1s = sorted(x["size"] for x in z1)
    check(len(z1s) >= 5 and z1s[0] <= 40 and sum(1 for v_ in z1s if v_ >= 60) >= 2, "MK (fix round): Zone 1 islets of VARIOUS sizes - small "
          "(<= 40 across) up to at least two medium ones (>= 60 across): %s" % z1s)
    check(any(x["dy"] > 0 for x in z1) and any(x["dy"] < 0 for x in z1) and all(20 <= abs(x["dy"]) <= 75 for x in il),
          "MK: islets at different heights - Zone 1 up and down, |dy| 20-75: %s" % [x["dy"] for x in il])
    check(any(x["mind"] < 60 for x in z1) and any(x["mind"] >= 63 for x in z1), "MK: some Zone 1 islets close (a jump / bridge from the coast), "
          "some further out: land gap to Zone 1 per islet %s (64 = 64 or more)" % [x["mind"] for x in z1])
    check(all(x["mind"] >= 10.0 and x["minother"] >= 16.0 for x in il), "MK: no islet touches its island (land gap >= 10) or another island / "
          "islet (>= 16): %s" % [(x["i"], x["mind"], x["minother"]) for x in il if x["mind"] < 10.0 or x["minother"] < 16.0])
    check(E["mk_bottom"]["nbad"] == 0, "MK: bottomOf (main islands) = the 0.6 formula on 2,000 points: %s" % E["mk_bottom"]["bad"])
    ib = E["mk_bottom"]["islets"]
    check(all(1 <= b_in <= b_edge <= h_ - 5 for _i, b_edge, b_in, h_, _r, _d in ib), "MK: islet undersides - a teardrop (deeper inside than at the "
          "edge), >= 5 under the ground, above y 0: %s" % ib[:6])
    mo = E["mk_outside"]
    check(mo["chunks"] >= 100 and mo["bad"] == [] and mo["far"], "MK: chunkOutside never skips a chunk holding an island / islet column (%d chunks, "
          "%d skipped) and skips a chunk far in the void: %s" % (mo["chunks"], mo["skipped"], mo["bad"]))
    check(E["mk_det"], "MK: the layout is deterministic (centres, islets, heights, every grid)")
    check(E["mk_noislets"][0] == 5 and E["mk_noislets"][1], "MK: islet counts 0 -> 5 entries and the SAME main islands: %s" % E["mk_noislets"])
    ms_ = E["mk_save"]
    check(ms_["saved"] and ms_["size"] > 1000 and ms_["same"] and ms_["fromFile"] and ms_["wrong"] and "seed 777" in ms_["wrong_err"]
          and ms_["name"] == "zone2_layout_777.bin" and ms_["v6"][0], "MK: the layout (format 2, + islets) saves to zone2_layout_<seed>.bin (%d bytes) "
          "and loads back IDENTICAL; another seed refused (%s); a 0.6-format file refused (%s)" % (ms_["size"], ms_["wrong_err"], ms_["v6"][1]))
    check(all(ms_["reuse"][:3]) and ms_["reuse"][3], "MK: a fresh generator with NO vanilla map reuses the saved layout: %s" % ms_["reuse"])
    mf_ = E["mk_fail"]
    check(mf_["failed"] and not mf_["laid"] and mf_["kept"] and mf_["unread"] and mf_["fut"][0] and "no island layout" in mf_["fut"][1],
          "MK: an unreadable saved layout is KEPT + one SEVERE, no layout -> a FAILED future (the engine retries): %s" % mf_)
    res = E["mk_chunk"]
    t1 = res["t1"]
    print("MK. T1 high plateau at the coast: %s" % t1)
    check(t1["void_bad"] == 0 and t1["below_bad"] == 0 and t1["shell_bad"] == 0, "MK T1: void columns empty + Env_Void, nothing under the "
          "underside, the 2-block shell: %s" % t1)
    check(t1["low_n"] > 40 and t1["edge"][1] is not None and t1["edge"][1] <= t1["floor"] + 3 + 3 + 5 + 2 and t1["edge"][0] >= t1["floor"] - 10,
          "MK T1 (no flat wall): the y 200 plateau is LOWERED at the coast to the island floor (y %d + 3 +- noise): coast tops %s (min, max, mean, "
          "std), %d columns lowered" % (t1["floor"], t1["edge"], t1["low_n"]))
    check(t1["edge"][3] >= 0.6, "MK T1: the edge tops vary column to column (crags / ledges, not one plane): std %.2f" % t1["edge"][3])
    check(t1["near"] + 15 < t1["mid"], "MK T1: the ground climbs inland (slope): mean top at e<4 %.1f, at e 12-20 %.1f" % (t1["near"], t1["mid"]))
    check(t1["surf_bad"] == 0 and t1["band_out"] == [], "MK T1: every lowered column keeps its vanilla surface (ground on dirt); columns past the "
          "band untouched: %s / %s" % (t1["surf_bad"], t1["band_out"]))
    t2 = res["t2"]
    print("MK. T2 lake at the coast: %s | T3 river %s | T3 lava %s | T3 waterfalls off %s" % (t2, res["t3"], res["t3lava"], res["t3off"]))
    check(t2["rim"] > 10 and t2["rim_bad"] == 0 and t2["exposed"] == 0 and t2["kept"] > 50 and t2["inner_dry"] == 0,
          "MK T2 (lake rim): lake water at the coast becomes a natural rim (the zone's shore block to one above the water, grass on a dirt rim), "
          "no water beside the void, the lake behind it kept: %s" % t2)
    t3 = res["t3"]
    check(t3["mouth"] > 0 and t3["exposed"] == 0 and t3["rim"] == 0 and t3["mouths"] > 0 and t3["under"] == 0,
          "MK T3 (waterfall): a RIVER keeps its mouth open - water beside the void (%d mouth columns), nothing rimmed, still nothing under the "
          "underside: %s" % (t3["mouth"], t3))
    check(res["t3lava"]["exposed"] == 0 and res["t3lava"]["rim"] > 10 and res["t3lava"]["rcalls"] == 0, "MK T3: lava in a river spot is never "
          "opened (rimmed): %s" % res["t3lava"])
    check(res["t3off"]["exposed"] == 0 and res["t3off"]["rim"] > 10 and res["t3off"]["rcalls"] == 0, "MK T3: waterfalls switched OFF -> the river "
          "mouth is rimmed like a lake: %s" % res["t3off"])
    t5 = res["t5"]
    check(t5["near_n"] > 20 and t5["near_low"] == [] and t5["far_n"] > 5 and t5["far_high"] == [], "MK T5: the banks within 3 blocks of a "
          "stream are never lowered under its water (no spill along the coast), banks far from it are lowered: %s" % t5)
    t4 = res["t4"]
    print("MK. T4 islet column: %s" % t4)
    check(t4 is not None and t4["cols"] > 20 and t4["moved"] > 20 and t4["mbad"] == [] and t4["below_bad"] == 0
          and t4["top_ok"] >= 0.9 * t4["top_n"] > 0, "MK T4 (islet): the vanilla column moved by dy %s (marker y 120 -> %s in %d columns, ground "
          "y 130 -> %s in %d of %d inner columns), nothing under its underside: %s" % (
              t4 and t4["dy"], t4 and 120 + t4["dy"], t4 and t4["moved"], t4 and 130 + t4["dy"], t4 and t4["top_ok"], t4 and t4["top_n"], t4))
    check(t4 is not None and t4["env_cols"] > 20 and t4["env_nbad"] == 0, "MK T4 (fix round): every islet column takes the vanilla SURFACE "
          "environment over its whole height (a vanilla cave environment below y 110 never ends up on the moved surface): %s columns, %s wrong %s"
          % (t4 and t4["env_cols"], t4 and t4["env_nbad"], t4 and t4["env_bad"]))
    t6 = res["t6"]
    print("MK. T6 lake on a chunk edge: %s" % t6)
    check(t6["exposed"] >= 3 and t6["nleft"] == 0 and t6["border_rims"] >= 1 and t6["kept_safe"] + t6["exposed"] > 0,
          "MK T6 (fix round): a lake on a chunk EDGE whose bank across the border the neighbour chunk lowers under the water is RIMMED on "
          "this side (no sideways spill into the neighbour); water beside a bank that stays high is kept: %s" % t6)
    f = E["mk_fn"]
    check(f["failed"][0] == 1 and f["failed"][1] and f["failed"][2] and f["failed"][3] == "not a chunk", "MK: WgZ2Fn - a mask failure THROWS "
          "(the engine retries; nothing saved) + one SEVERE; a non-chunk passes through: %s" % f["failed"])
    check(f["hopped"] == 1 and f["empty1"] and f["empty2"], "MK: WgZ2Hop - hops to the pool on the caller's thread, in place elsewhere: %s" % f)
    p = E["mk_prov"]
    check(p[0] == "com.hypixel.hytale.server.core.universe.world.worldgen.WorldGenLoadException" and p[1] and p[2] and "SkyWynnZones2" in p[3],
          "MK: WgZ2Provider offline - SEVERE + WorldGenLoadException; the codec: %s" % p)
    # ---- Z
    z1 = E["z1"]
    check(z1[0] == 1 and "Teleporting to the Zone 3 island (Whisperfrost Frontiers) in the zone islands world..." in z1[2],
          "Z: /zone 3 from the main world (0.7 world loaded): decide 1, up to the engine's teleport call: %s" % z1)
    z2 = E["z2"]
    lz = ml["lands"][1]
    check(z2[0] == 2 and z2[1] == ["skywynn_zones2", math.floor(lz[0]) + 0.5, 122.0, math.floor(lz[1]) + 0.5] and "Teleporting to the Zone 2 island" in z2[2],
          "Z: /zone 2 on the 0.7 world: a Teleport to the Zone 2 landing: %s" % z2)
    check(E["z3"][0] is None and "has no Zone 5 island" in E["z3"][1], "Z: no Zone 5 island -> refused in plain words: %s" % E["z3"])
    check(E["z4a"][0] is None and "switched off" in E["z4a"][1], "Z: switch OFF - /zone 3 refused: %s" % E["z4a"][1])
    check(E["z4b"][0] == ["skywynn_z1", 0.5, 144.0, 344.5], "Z: switch OFF - /zone 1 = the old test island: %s" % E["z4b"])
    check(E["z5"][0] == ["skywynn_z1", 0.5, 144.0, 344.5], "Z: /zone old = the old test island: %s" % E["z5"])
    check(E["z6"][0] == ["skywynn_zones2", 0.5, 122.0, 0.5] and "Zone 1 island" in E["z6"][1], "Z: /zone world = the 0.7 world's Zone 1 landing: %s" % E["z6"])
    l4 = ml["lands"][3]
    check(E["z6b"][0] == ["skywynn_zones2", math.floor(l4[0]) + 0.5, 122.0, math.floor(l4[1]) + 0.5], "Z: /zone z4 = the Zone 4 landing: %s" % E["z6b"])
    check(E["z6c"][2] is None and re.search(r"skywynn_zones(?!2)", E["z6c"][1]) is not None,
          "Z: /zone old6 = the 0.6 zone islands world (kept, its own generator): %s" % E["z6c"])
    check(E["z7"][0] is None and "There is no zone '9'" in E["z7"][1] and "old6" in E["z7"][1], "Z: /zone 9 - the zone list names old6: %s" % E["z7"][1])
    z9 = " | ".join(E["z9"])
    check("(world 'skywynn_zones2')" in z9 and "Islands: Zone 1 Emerald Wilds at 1 1" in z9 and "islets:" in z9 and "Generator SkyWynnZones2" in z9
          and "waterfalls" in z9, "Z: /zone info on the 0.7 world: %s" % z9[:700])
    check("no landing point to set" in E["z10"], "Z: /zone setlanding refused on the 0.7 world: %s" % E["z10"])
    l_on, l_off = " | ".join(E["z11"][0]), " | ".join(E["z11"][1])
    check("/zone old  Zone 1 - Emerald Wilds" in l_on and "/zone world  The Zone islands world" in l_on and "/zone old6  The Zone islands 0.6 world" in l_on
          and "islands of world skywynn_zones2" in l_on and "/zone 1  Zone 1 - Emerald Wilds" in l_off and "is OFF" in l_off,
          "Z: /zone lists the 0.7 world, /zone old6 + /zone old (on) / /zone 1 (off): %s || %s" % (l_on[:500], l_off[:300]))
    z12 = E["z12"]
    check(z12[0][0] is False and z12[1][:4] == [True, False, 9, 0] and z12[2][1:4] == [True, 12, 0] and z12[3][1:4] == [True, 6, 3]
          and "waterfalls off" in z12[1][4], "Z: WgCfg.apply - islands06, zones.waterfalls, islet counts (clamped 0-12, junk keeps the value): %s"
          % [x[:4] for x in z12])
    check(E["z13"][0] is not None and "not registered" in E["z13"][0] and E["z13"][1] is None, "Z: WgCheck - the 0.7 type unregistered -> refused: %s" % E["z13"])
    check(E["z14"][0].startswith("skywynn_zones2 (seed %d)" % ZSEED) and "old6" in E["z14"][0] and "islets" in E["z14"][1] and E["z14"][2] == "skywynn_z1",
          "Z: the read-only Server Setup rows: %s" % E["z14"])
    z15 = E["z15"]
    check(z15[:10] == [2, 2, 2, 3, 3, 3, 0, 0, 1, -1] and z15[10] == "The Zone islands world" and z15[11] and not z15[12] and z15[13] and z15[14] == 3
          and z15[16] == ["skywynn_z1", "skywynn_proof2", "skywynn_zones", "skywynn_zones2"] and z15[17][3] == "SkyWynn_Zones2"
          and z15[18][3] == "SkyWynnZones2" and z15[19][2:] == ["old6", "world"],
          "Z: WgZones - aliases (zones/06/old6 -> 0.6, world/07/zones2 -> 0.7), label, isIsland per provider, the 4 worlds: %s" % z15)
    check(E["z18"] == [False, True, True], "Z: WgApplyLanding leaves the 0.7 world's spawn alone; no landing point for either zone world: %s" % E["z18"])
    print("Z. d == 4 path offline: %s; hop recorded %s" % (E["z8"], E["z8hop"]))
    if E["z8"][2] and "Creating the zone islands world" in E["z8"][2]:
        check(E["z8hop"] is not None and E["z8hop"][0] == 3, "Z: /zone 4 while the 0.7 world is made records the hop to Zone 4: %s" % (E["z8hop"],))
    else:
        check(E["z8hop"] is None, "Z: /zone 4 that could not start a trip records no hop: %s" % (E["z8hop"],))
    z19 = E["z19"]
    check(z19[0] == 1 and z19[1] == ["skywynn_zones2", math.floor(l4[0]) + 0.5, 122.0, math.floor(l4[1]) + 0.5] and "Moving you on to the Zone 4 island"
          in z19[2] and z19[3] == 0 and z19[4] == 1, "Z: arriving in the 0.7 world with a hop -> moved on to the Zone 4 landing: %s" % z19)
    check(E["z21"] == [0, None, 1], "Z: arriving in the 0.6 world keeps the hop (it targets the 0.7 world only): %s" % E["z21"])
    q = E["qz"]
    if q and q[0] != "error":
        check(q[0] == PKG + "WgZ2Provider" and q[1] == ZSEED and q[2] == "SkyWynn - zone islands" and q[3] and q[4] == "Adventure",
              "QZ: the SkyWynn_Zones2 template decodes: WgZ2Provider, seed %d, no spawn provider, Adventure: %s" % (ZSEED, q))
    else:
        NOTES.append("QZ: the template decode needs more engine set-up offline (%s) - covered by VP's saved config decode" % (q,))
    st, nfiles, haswf = E["st"]
    check(len(st) == 2 and all(s_[0] == [] for s_ in st) and st[0][1:] == st[1][1:] and st[0][4] is True and st[0][5] is True and haswf is False,
          "ST: two starts on a COPY of the live Skyy_SkyyWorldGen (%d files): no file changed (the new rows are NOT written into the existing "
          "config - their defaults apply), the same state read: %s" % (nfiles, st))


# ================================================================= VP. the REAL vanilla 0.7 generator through the mod on an offline server
PROBE_SRC = r'''# The SkyyWgProbe7 test plugin (NEVER shipped): built into a scratch jar, run next to SkyyWorldGen 0.7 on an OFFLINE server started by
# tools/smoke_test.py. It creates the 0.7 zone islands world through SkyyWorldGen's own /zone code, checks the layout picked from the REAL
# vanilla 0.7 zone map, compares sample chunks with plain vanilla, dumps a mountain edge / a lake edge / a river mouth, loads the river
# mouth in the live world and measures its waterfall, and writes the map data for the harness's renders into OUTDIR.
PROBE_VERSION = "0.7"
PROBE_PKG = "com.skyy.wgprobe7"
W = "com.skyy.worldgen."
GC = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"
GBC = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedBlockChunk"
FS = "com.hypixel.hytale.server.core.universe.world.chunk.section.FluidSection"
BS = "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection"
HOLD = "com.hypixel.hytale.component.Holder"
CG = "com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
TRF = "com.hypixel.hytale.math.vector.Transform"
CF = "java.util.concurrent.CompletableFuture"
EWE = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedEntityChunk$EntityWrapperEntry"
BT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
FL = "com.hypixel.hytale.server.core.asset.type.fluid.Fluid"
ZL = W + "WgZ2Layout"
ZI = W + "WgZ2Isles"
VORES = ["Ore_Copper_Stone", "Ore_Iron_Stone", "Ore_Gold_Stone", "Ore_Silver_Stone", "Ore_Thorium_Sandstone", "Ore_Cobalt_Shale",
         "Ore_Adamantite_Magma_Cracked", "Ore_Iron_Volcanic", "Ore_Gold_Volcanic", "Ore_Silver_Volcanic", "Ore_Copper_Sandstone",
         "Ore_Iron_Sandstone", "Ore_Cobalt_Slate_Cracked", "Ore_Iron_Basalt", "Ore_Copper_Shale", "Ore_Iron_Shale", "Ore_Gold_Sandstone",
         "Ore_Silver_Sandstone", "Ore_Gold_Calcite", "Ore_Iron_Basalt_Cracked", "Ore_Adamantite_Magma"]

LIVE_METHODS = [
    r"""
public void run() {
  try {
    %(ST)s st = this.w.getChunkStore().getStore();
    long[] r = new long[6];
    r[2] = 100000L;
    for (int a = 0; a < 3; a++) for (int c = 0; c < 3; c++) for (int s = 0; s < 10; s++) {
      int bx = this.x0 + a * 32;
      int bz = this.z0 + c * 32;
      %(REF)s ref = this.w.getChunkStore().getChunkSectionReferenceAtBlock(bx, s * 32, bz);
      if (ref == null || !ref.isValid()) { r[4]++; continue; }
      %(BS)s bs = (%(BS)s) st.getComponent(ref, %(BS)s.getComponentType());
      %(FS)s fs = (%(FS)s) st.getComponent(ref, %(FS)s.getComponentType());
      if (bs != null) r[3] += bs.getTickingBlocksCount();
      for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) {
        int col = (a * 32 + x) * 96 + (c * 32 + z);
        for (int y = s * 32; y < s * 32 + 32; y++) {
          int b = bs == null ? 0 : bs.get(bx + x, y, bz + z);
          int f = fs == null ? 0 : fs.getFluidId(bx + x, y, bz + z);
          if (f != 0) {
            r[5]++;
            if (this.voidCol[col]) { r[0]++; if (y < r[2]) r[2] = y; if (y > r[1]) r[1] = y; }
          }
          if (this.dump) { this.blocks[col * 320 + y] = (short) b; this.fluids[col * 320 + y] = (byte) f; }
        }
      }
    }
    this.res = r;
  } catch (Throwable t) {
    this.err = String.valueOf(t);
  }
  this.done = true;
}""",
]

PROBE_METHODS = [
    r"""
public static void log(String m) {
  if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyWgProbe7] " + m);
}""",
    r"""public static void fail(String m) { FAILS++; log("FAIL " + m); }""",
    r"""public static void ok(String m) { OKS++; log("OK " + m); }""",
    r"""public static void check(boolean c, String m) { if (c) ok(m); else fail(m); }""",
    r"""
public static %(FS)s[] fsOf(%(GC)s g) {
  %(FS)s[] fs = new %(FS)s[10];
  %(HOLD)s[] secs = g.getSections();
  for (int s = 0; s < 10; s++) {
    %(HOLD)s h = secs == null || s >= secs.length ? null : secs[s];
    fs[s] = h == null ? null : (%(FS)s) h.getComponent(%(FS)s.getComponentType());
  }
  return fs;
}""",
    r"""
public static int fl(%(FS)s[] fs, int x, int y, int z) {
  if (y < 0 || y > 319) return %(FL)s.EMPTY_ID;
  %(FS)s f = fs[y >> 5];
  return f == null ? %(FL)s.EMPTY_ID : f.getFluidId(x, y, z);
}""",
    r"""
public static String nm(int id) {
  try { Object o = %(BT)s.getAssetMap().getAsset(id); return o == null ? "?" : ((%(BT)s) o).getId(); } catch (Throwable t) { return "?" + id; }
}""",
    r"""
public static String fnm(int id) {
  try { Object o = %(FL)s.getAssetMap().getAsset(id); return o == null ? "?" : ((%(FL)s) o).getId(); } catch (Throwable t) { return "?" + id; }
}""",
    r"""public static int bid(String n) { try { return %(BT)s.getAssetMap().getIndexOrDefault(n, -1); } catch (Throwable t) { return -1; } }""",
    r"""
public static boolean in(int[] a, int v) {
  if (a == null || v <= 0) return false;
  for (int i = 0; i < a.length; i++) if (a[i] == v) return true;
  return false;
}""",
    r"""
public static boolean gnd(int id) {
  if (id <= 0) return false;
  String n = nm(id);
  return (n.startsWith("Soil_") || n.startsWith("Rock_")) && n.indexOf("Ore") < 0 && n.indexOf("Crystal") < 0;
}""",
    r"""
public static int gtop(%(GBC)s b, int lx, int lz, int from) {
  for (int y = Math.min(319, from); y >= 0; y--) if (gnd(b.getBlock(lx, y, lz))) return y;
  return 0 - 1;
}""",
    # the column plan: [0] bottom (100000 = void), [1] ground (moved), [2] entry, [3] e * 16, [4] vanilla ground
    r"""
public static int[] plan(%(W)sWgZ2Gen g, %(ZL)s L, int seed, int cx, int cz) {
  int[] p = new int[34 * 34 * 5];
  double[] m = new double[1];
  for (int i = 0; i < 34; i++) for (int k = 0; k < 34; k++) {
    int x = cx * 32 + i - 1;
    int z = cz * 32 + k - 1;
    int idx = i * 34 + k;
    int ii = %(ZI)s.member(L, x + 0.5, z + 0.5, m);
    p[2 * 1156 + idx] = ii;
    if (ii >= 0) {
      int hv = g.getHeight(seed, x, z);
      int h = hv + L.dy[ii];
      p[idx] = %(ZI)s.bottom2(L, ii, m[0], h, x + 0.5, z + 0.5);
      p[1156 + idx] = h;
      p[3 * 1156 + idx] = (int) Math.floor(m[0] * 16.0);
      p[4 * 1156 + idx] = hv;
    } else p[idx] = 100000;
  }
  return p;
}""",
    # st: 0 outsideBad 1 belowBad 2 changedBad 3 sealed 4 identical 5 exposedFluid 6 shellBad 7 lavaKept 8 fluidKept 9 deco 10 insideCols
    #     11 outsideCols 12 ore 13 entsOutside 14 entsMasked 15 entsVanilla 16 envBad 17 rootsBelow 18 mouthFluid 19 loweredCols
    #     20 loweredGround 21 isletCols 22 isletBad 23 rimCols 24 bandCols 25 interiorCols
    r"""
public static void cmp(%(GC)s m, %(GC)s r, int[] p, java.util.function.IntBinaryOperator rv, int lava1, int lava2, int stone, int envVoid, long[] st, int cx, int cz) {
  %(GBC)s mb = m.getBlockChunk();
  %(GBC)s rb = r.getBlockChunk();
  %(FS)s[] mf = fsOf(m);
  %(FS)s[] rf = fsOf(r);
  int e = %(FL)s.EMPTY_ID;
  int[] deco = %(ZI)s.DECO;
  int[] flw = %(ZI)s.FLOWERS;
  int[] ore = %(ZI)s.ORE;
  int[] host = %(ZI)s.HOST;
  int roots = deco[%(ZI)s.D_ROOTS];
  int crack = deco[%(ZI)s.D_CRACK];
  for (int lx = 0; lx < 32; lx++) for (int lz = 0; lz < 32; lz++) {
    int idx = (lx + 1) * 34 + (lz + 1);
    int b = p[idx];
    if (b >= 100000) {
      st[11]++;
      for (int y = 0; y < 320; y++) if (mb.getBlock(lx, y, lz) != 0 || fl(mf, lx, y, lz) != e) { st[0]++; break; }
      if (envVoid >= 0 && mb.getEnvironment(lx, 200, lz) != envVoid) st[16]++;
      continue;
    }
    st[10]++;
    int ii = p[2 * 1156 + idx];
    int h = p[1156 + idx];
    double ev = p[3 * 1156 + idx] / 16.0;
    int hv = p[4 * 1156 + idx];
    int dy = LAY.dy[ii];
    boolean voidN = p[idx - 34] >= 100000 || p[idx + 34] >= 100000 || p[idx - 1] >= 100000 || p[idx + 1] >= 100000;
    for (int y = 0; y < b; y++) {
      int a = mb.getBlock(lx, y, lz);
      if (a == roots && roots > 0 && fl(mf, lx, y, lz) == e) { st[17]++; continue; }
      if (a != 0 || fl(mf, lx, y, lz) != e) st[1]++;
    }
    if (mb.getBlock(lx, b, lz) == 0 || (b + 1 < 320 && mb.getBlock(lx, b + 1, lz) == 0)) st[6]++;
    boolean rq = false;
    boolean river = false;
    for (int y = b; y < 320; y++) {
      int fa = fl(mf, lx, y, lz);
      if (fa == e) continue;
      st[8]++;
      if (fa == lava1 || fa == lava2) st[7]++;
      if (y - 1 < b || voidN) {
        if (!rq) { river = rv != null && rv.applyAsInt(cx * 32 + lx, cz * 32 + lz) != 0; rq = true; }
        if (river && voidN && y >= b + 2 && fa != lava1 && fa != lava2) st[18]++;
        else {
          st[5]++;
          if (st[5] <= 6L) log("EXPOSED chunk " + cx + " " + cz + " local " + lx + " " + y + " " + lz + " fluid " + fnm(fa) + " entry " + ii + " e " + ev + " bottom " + b + " voidN " + voidN + " river " + river);
        }
      }
    }
    if (ev < 40.0) {
      st[24]++;
      int vt = hv + dy;
      int mg = gtop(mb, lx, lz, vt + 2);
      if (mg >= 0 && mg < vt - 1 && fl(rf, lx, hv + 1, lz) == e) { st[19]++; if (gnd(mb.getBlock(lx, mg, lz))) st[20]++; }
      if (fl(rf, lx, hv + 1, lz) != e && fl(mf, lx, hv + 1 + dy, lz) == e && mb.getBlock(lx, hv + 1 + dy, lz) != 0) st[23]++;
    }
    if (ii >= LAY.nMain) {
      st[21]++;
      int ve = rb.getEnvironment(lx, Math.max(0, Math.min(319, hv + 2)), lz);
      int me1 = mb.getEnvironment(lx, Math.max(0, Math.min(319, h + 2)), lz);
      int me2 = mb.getEnvironment(lx, Math.max(0, Math.min(319, h - 12)), lz);
      if (me1 != ve || me2 != ve) { st[26]++; if (st[26] <= 4L) log("ISLETENV chunk " + cx + " " + cz + " local " + lx + " " + lz + ": masked env " + me1 + " / " + me2 + ", vanilla surface env " + ve); }
      int mg = gtop(mb, lx, lz, h + 2);
      // the coast band may LOWER an islet column too (its surface re-laid, decoration on top): compare only under the lowered top
      double[] me_ = new double[1];
      %(ZI)s.member(LAY, cx * 32 + lx + 0.5, cz * 32 + lz + 0.5, me_);
      int ntb = %(ZI)s.lowTarget(LAY, ii, cx * 32 + lx, cz * 32 + lz, me_[0], h, b);
      int top = Math.min(Math.min(mg, h), ntb) - 6;
      for (int y = b + 3; y <= top && y <= 319; y++) {
        int yv = y - dy;
        if (yv < 0 || yv > 319) continue;
        int a = mb.getBlock(lx, y, lz);
        int c = rb.getBlock(lx, yv, lz);
        if (a == c) continue;
        if (a == stone && (c == 0 || fl(rf, lx, yv, lz) != e)) continue;
        if (c == 0 && in(%(ZI)s.SHORE, a) && ev < 40.0) continue;
        // a lake / lava rim at the islet's coast: its bed block (or the shore block) from the fluid's bottom to one above its top
        if (ev < 40.0 && c == 0 && gnd(a) && (fl(rf, lx, yv, lz) != e || (yv > 0 && fl(rf, lx, yv - 1, lz) != e))) continue;
        if (in(ore, a) && in(host, c)) continue;
        if (c != 0 && rb.getBlock(lx, yv, lz) != 0 && r.getState(lx, yv, lz) != null && a == 0) continue;
        st[22]++;
        if (st[22] <= 6L) log("ISLETDIFF chunk " + cx + " " + cz + " local " + lx + " " + y + " " + lz + " entry " + ii + " dy " + dy + ": masked " + nm(a) + ", vanilla y " + yv + " " + nm(c));
      }
      continue;
    }
    if (ev < 42.0) continue;
    st[25]++;
    for (int y = b; y < 320; y++) {
      int a = mb.getBlock(lx, y, lz);
      int fa = fl(mf, lx, y, lz);
      int c = rb.getBlock(lx, y, lz);
      int fc = fl(rf, lx, y, lz);
      if (a == c && fa == fc) st[4]++;
      else if (a == stone && fa == e && (c == 0 || fc != e)) st[3]++;
      else if (fa == e && fc == e && c == 0 && (in(deco, a) || in(flw, a))) st[9]++;
      else if (fa == e && a == crack && crack > 0 && c != 0) st[9]++;
      else if (fa == e && in(ore, a) && in(host, c)) st[12]++;
      else {
        st[2]++;
        if (st[2] <= 8L) log("CHANGED chunk " + cx + " " + cz + " local " + lx + " " + y + " " + lz + " entry " + ii + " e " + ev + ": masked " + nm(a) + " fluid " + fa + ", vanilla " + nm(c) + " fluid " + fc + " (bottom " + b + ", ground " + h + ")");
      }
    }
  }
  java.util.Iterator it = m.getEntityChunk().getEntities().iterator();
  double[] mm = new double[1];
  while (it.hasNext()) {
    %(EWE)s w = (%(EWE)s) it.next();
    st[14]++;
    org.joml.Vector3i v = w.offset();
    int ii = %(ZI)s.member(LAY, v.x + 0.5, v.z + 0.5, mm);
    if (ii < 0 || ii >= LAY.nMain) st[13]++;
  }
  st[15] += r.getEntityChunk().getEntities().size();
}""",
    r"""
public static void one(%(W)sWgZ2Gen g, %(CG)s v, %(ZL)s L, int seed, int cx, int cz, java.util.function.IntBinaryOperator rv, int lava1, int lava2, int stone, int envVoid, long[] st, long[] tm) throws Throwable {
  long idx = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx, cz);
  long t0 = System.nanoTime();
  %(GC)s m = (%(GC)s) g.generate(seed, idx, cx, cz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  long t1 = System.nanoTime();
  %(GC)s r = (%(GC)s) v.generate(seed, idx, cx, cz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  long t2 = System.nanoTime();
  tm[0] += t1 - t0; tm[1] += t2 - t1; tm[2]++;
  if (m == null || r == null) { fail("chunk " + cx + " " + cz + ": a null chunk"); return; }
  int[] p = plan(g, L, seed, cx, cz);
  long[] s1 = new long[st.length];
  cmp(m, r, p, rv, lava1, lava2, stone, envVoid, s1, cx, cz);
  for (int i = 0; i < st.length; i++) st[i] += s1[i];
  if (s1[0] + s1[1] + s1[2] + s1[5] + s1[6] + s1[13] + s1[16] + s1[22] + s1[26] > 0) fail("chunk " + cx + " " + cz + ": outsideBad " + s1[0] + " belowBad " + s1[1] + " changedBad " + s1[2] + " exposedFluid " + s1[5] + " shellBad " + s1[6] + " entsOutside " + s1[13] + " envBad " + s1[16] + " isletBad " + s1[22] + " isletEnvBad " + s1[26]);
}""",
    # the sample chunks: per main island the landing, the coast in 4 directions (+ 40 inland), 2 inner points; per islet its centre + its edge
    r"""
public static int[] samples(%(ZL)s L) {
  java.util.ArrayList l = new java.util.ArrayList();
  double[] m = new double[1];
  for (int i = 0; i < L.n; i++) {
    if (!L.found[i]) continue;
    double x0 = Math.floor(L.lx[i]) + 0.5;
    double z0 = Math.floor(L.lz[i]) + 0.5;
    l.add(new int[] { (int) Math.floor(x0 / 32.0), (int) Math.floor(z0 / 32.0) });
    if (i >= L.nMain) {
      double t = 0.0;
      while (t < 200.0 && %(ZI)s.member(L, x0 + t, z0, m) == i) t += 2.0;
      l.add(new int[] { (int) Math.floor((x0 + t) / 32.0), (int) Math.floor(z0 / 32.0) });
      continue;
    }
    for (int d = 0; d < 4; d++) {
      double ux = d == 0 ? 1.0 : (d == 1 ? 0.0 - 1.0 : 0.0);
      double uz = d == 2 ? 1.0 : (d == 3 ? 0.0 - 1.0 : 0.0);
      double t = 0.0;
      while (t < 3000.0 && %(ZI)s.member(L, x0 + ux * t, z0 + uz * t, m) == i) t += 8.0;
      double cxw = x0 + ux * t;
      double czw = z0 + uz * t;
      l.add(new int[] { (int) Math.floor(cxw / 32.0), (int) Math.floor(czw / 32.0) });
      l.add(new int[] { (int) Math.floor((cxw - ux * 40.0) / 32.0), (int) Math.floor((czw - uz * 40.0) / 32.0) });
    }
    l.add(new int[] { (int) Math.floor((x0 + 150.0) / 32.0), (int) Math.floor((z0 + 90.0) / 32.0) });
    l.add(new int[] { (int) Math.floor((x0 - 120.0) / 32.0), (int) Math.floor((z0 - 160.0) / 32.0) });
  }
  java.util.LinkedHashSet seen = new java.util.LinkedHashSet();
  java.util.ArrayList out = new java.util.ArrayList();
  for (int j = 0; j < l.size(); j++) {
    int[] c = (int[]) l.get(j);
    if (seen.add(c[0] + "," + c[1])) out.add(c);
  }
  int[] r = new int[out.size() * 2];
  for (int j = 0; j < out.size(); j++) { int[] c = (int[]) out.get(j); r[2 * j] = c[0]; r[2 * j + 1] = c[1]; }
  return r;
}""",
    # circularity 4 pi A / P^2 of entry i's grid (cells with sd > 0; the perimeter = inside cells' outside edges)
    r"""
public static double circ(float[] s, int n, double cs) {
  long a = 0L;
  long p = 0L;
  for (int k = 0; k < n; k++) for (int j = 0; j < n; j++) {
    if (s[k * n + j] <= 0.0f) continue;
    a++;
    if (j == 0 || s[k * n + j - 1] <= 0.0f) p++;
    if (j == n - 1 || s[k * n + j + 1] <= 0.0f) p++;
    if (k == 0 || s[(k - 1) * n + j] <= 0.0f) p++;
    if (k == n - 1 || s[(k + 1) * n + j] <= 0.0f) p++;
  }
  double A = a * cs * cs;
  double P = p * cs;
  return P <= 0.0 ? 0.0 : 4.0 * Math.PI * A / (P * P);
}""",
    # the share of entry i's coast cells lying within 4 %% of its radius cap circle (1.0 = a round cut along the cap everywhere)
    r"""
public static double arcShare(float[] s, int n, int gx0, int gz0, double cs, double cx, double cz, double r) {
  long b = 0L;
  long a = 0L;
  for (int k = 1; k < n - 1; k++) for (int j = 1; j < n - 1; j++) {
    if (s[k * n + j] <= 0.0f) continue;
    if (s[k * n + j - 1] > 0.0f && s[k * n + j + 1] > 0.0f && s[(k - 1) * n + j] > 0.0f && s[(k + 1) * n + j] > 0.0f) continue;
    b++;
    double dx = gx0 + j * cs - cx;
    double dz = gz0 + k * cs - cz;
    if (Math.sqrt(dx * dx + dz * dz) >= 0.96 * r) a++;
  }
  return b == 0L ? 0.0 : (double) a / (double) b;
}""",
    # the map for the render: Zone 1 + its islets every STEP blocks: entry (255 void), 0.6 Zone 1 member, the moved ground height
    r"""
public static void writeMap(%(W)sWgZ2Gen g, %(ZL)s L, %(W)sWgZoneLayout L6, int seed, String path) throws Throwable {
  double x0 = L.minX[0];
  double x1 = L.maxX[0];
  double z0 = L.minZ[0];
  double z1 = L.maxZ[0];
  for (int i = L.nMain; i < L.n; i++) {
    if (!L.found[i] || L.zone[i] != 0) continue;
    x0 = Math.min(x0, (double) L.minX[i]); x1 = Math.max(x1, (double) L.maxX[i]); z0 = Math.min(z0, (double) L.minZ[i]); z1 = Math.max(z1, (double) L.maxZ[i]);
  }
  x0 = Math.min(x0, (double) L6.minX[0]); x1 = Math.max(x1, (double) L6.maxX[0]); z0 = Math.min(z0, (double) L6.minZ[0]); z1 = Math.max(z1, (double) L6.maxZ[0]);
  x0 -= 60.0; x1 += 60.0; z0 -= 60.0; z1 += 60.0;
  int step = 4;
  int w = (int) ((x1 - x0) / step) + 1;
  int h = (int) ((z1 - z0) / step) + 1;
  java.io.DataOutputStream o = new java.io.DataOutputStream(new java.io.BufferedOutputStream(new java.io.FileOutputStream(path)));
  o.writeInt((int) x0); o.writeInt((int) z0); o.writeInt(step); o.writeInt(w); o.writeInt(h);
  double[] m = new double[1];
  for (int k = 0; k < h; k++) {
    for (int j = 0; j < w; j++) {
      double x = x0 + j * step + 0.5;
      double z = z0 + k * step + 0.5;
      int ii = %(ZI)s.member(L, x, z, m);
      int o6 = %(W)sWgZoneIsles.member(L6, x, z, m);
      o.writeByte(ii < 0 ? 255 : ii);
      o.writeByte(o6 == 0 ? 1 : 0);
      int hh = ii >= 0 || o6 == 0 ? g.getHeight(seed, (int) Math.floor(x), (int) Math.floor(z)) + (ii >= 0 ? L.dy[ii] : 0) : 0;
      o.writeShort(hh);
    }
  }
  o.close();
}""",
    # fix round: a water voxel of the masked chunks (vanilla water there too) with AIR beside it where vanilla had a solid block, the
    # neighbour column on the island (not the void: that is the seal / a waterfall) = a lake that spills into a lowered bank;
    # sp[0] all, sp[1] across a chunk border, sp[2] water voxels looked at
    r"""
public static void spill(%(W)sWgZ2Gen g, %(CG)s v, %(ZL)s L, int seed, int cx0, int cz0, long[] sp, int lava1, int lava2) throws Throwable {
  %(GC)s[] mm = new %(GC)s[9];
  %(GC)s[] rr = new %(GC)s[9];
  for (int a = 0; a < 3; a++) for (int c = 0; c < 3; c++) {
    long idx = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx0 + a, cz0 + c);
    mm[a * 3 + c] = (%(GC)s) g.generate(seed, idx, cx0 + a, cz0 + c, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
    rr[a * 3 + c] = (%(GC)s) v.generate(seed, idx, cx0 + a, cz0 + c, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  }
  %(FS)s[][] mf = new %(FS)s[9][];
  %(FS)s[][] rf = new %(FS)s[9][];
  for (int k = 0; k < 9; k++) { mf[k] = fsOf(mm[k]); rf[k] = fsOf(rr[k]); }
  double[] m = new double[1];
  int[] ent = new int[96 * 96];
  for (int x = 0; x < 96; x++) for (int z = 0; z < 96; z++) ent[x * 96 + z] = %(ZI)s.member(L, cx0 * 32 + x + 0.5, cz0 * 32 + z + 0.5, m);
  int e = %(FL)s.EMPTY_ID;
  for (int x = 1; x < 95; x++) for (int z = 1; z < 95; z++) {
    int ii = ent[x * 96 + z];
    if (ii < 0 || ii >= L.nMain) continue;
    int k = (x / 32) * 3 + z / 32;
    for (int y = 1; y < 319; y++) {
      int fa = fl(mf[k], x %% 32, y, z %% 32);
      if (fa == e || fa == lava1 || fa == lava2) continue;
      if (fl(rf[k], x %% 32, y, z %% 32) == e) continue;
      sp[2]++;
      for (int d = 0; d < 4; d++) {
        int x2 = x + (d == 0 ? 0 - 1 : (d == 1 ? 1 : 0));
        int z2 = z + (d == 2 ? 0 - 1 : (d == 3 ? 1 : 0));
        if (ent[x2 * 96 + z2] < 0) continue;
        int k2 = (x2 / 32) * 3 + z2 / 32;
        if (mm[k2].getBlockChunk().getBlock(x2 %% 32, y, z2 %% 32) != 0 || fl(mf[k2], x2 %% 32, y, z2 %% 32) != e) continue;
        if (rr[k2].getBlockChunk().getBlock(x2 %% 32, y, z2 %% 32) == 0) continue;
        sp[0]++;
        if (k2 != k) sp[1]++;
        if (sp[0] <= 6L) log("SPILL water at " + (cx0 * 32 + x) + " " + y + " " + (cz0 * 32 + z) + " has air beside it at " + (cx0 * 32 + x2) + " " + (cz0 * 32 + z2) + " where vanilla is solid (" + (k2 != k ? "across a chunk border" : "same chunk") + ")");
      }
    }
  }
}""",
    # a 96 x 96 region (3 x 3 chunks from chunk cx0, cz0) of the masked + the vanilla generator: per column the entry + dy, per voxel block + fluid
    r"""
public static void dumpRegion(%(W)sWgZ2Gen g, %(CG)s v, %(ZL)s L, int seed, int cx0, int cz0, String path, boolean[] seenB, boolean[] seenF) throws Throwable {
  java.io.DataOutputStream o = new java.io.DataOutputStream(new java.io.BufferedOutputStream(new java.io.FileOutputStream(path)));
  o.writeInt(cx0 * 32); o.writeInt(cz0 * 32);
  %(GC)s[] mm = new %(GC)s[9];
  %(GC)s[] rr = new %(GC)s[9];
  for (int a = 0; a < 3; a++) for (int c = 0; c < 3; c++) {
    long idx = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx0 + a, cz0 + c);
    mm[a * 3 + c] = (%(GC)s) g.generate(seed, idx, cx0 + a, cz0 + c, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
    rr[a * 3 + c] = (%(GC)s) v.generate(seed, idx, cx0 + a, cz0 + c, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  }
  double[] m = new double[1];
  for (int x = 0; x < 96; x++) for (int z = 0; z < 96; z++) {
    int ii = %(ZI)s.member(L, cx0 * 32 + x + 0.5, cz0 * 32 + z + 0.5, m);
    o.writeByte(ii < 0 ? 255 : ii);
    o.writeShort(ii < 0 ? 0 : L.dy[ii]);
  }
  for (int pass = 0; pass < 2; pass++) {
    for (int x = 0; x < 96; x++) for (int z = 0; z < 96; z++) {
      %(GC)s gc = pass == 0 ? mm[(x / 32) * 3 + z / 32] : rr[(x / 32) * 3 + z / 32];
      %(GBC)s b = gc.getBlockChunk();
      %(FS)s[] fs = fsOf(gc);
      for (int y = 0; y < 320; y++) {
        int id = b.getBlock(x %% 32, y, z %% 32);
        int f = fl(fs, x %% 32, y, z %% 32);
        o.writeShort(id);
        o.writeByte(f);
        if (id >= 0 && id < seenB.length) seenB[id] = true;
        if (f >= 0 && f < seenF.length) seenF[f] = true;
      }
    }
  }
  o.close();
}""",
    r"""
public static void writeNames(boolean[] seenB, boolean[] seenF, String path) throws Throwable {
  java.io.PrintWriter o = new java.io.PrintWriter(new java.io.FileWriter(path));
  for (int i = 0; i < seenB.length; i++) if (seenB[i]) o.println("B " + i + " " + nm(i));
  for (int i = 0; i < seenF.length; i++) if (seenF[i]) o.println("F " + i + " " + fnm(i));
  o.close();
}""",
    # the live world: load 3 x 3 chunks TICKING (flag 4 = what a nearby player's chunk tracker asks), read them on the world thread
    r"""
public static long[] live(%(WLD)s w, int x0, int z0, boolean[] voidCol, boolean dump, short[] blocks, byte[] fluids) throws Throwable {
  for (int a = 0; a < 3; a++) for (int c = 0; c < 3; c++) w.getChunkStore().getChunkReferenceAsync(com.hypixel.hytale.math.util.ChunkUtil.indexChunk((x0 >> 5) + a, (z0 >> 5) + c), 4).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  %(PP)s.Live lv = new %(PP)s.Live();
  lv.w = w; lv.x0 = x0; lv.z0 = z0; lv.voidCol = voidCol; lv.dump = dump; lv.blocks = blocks; lv.fluids = fluids;
  w.execute(lv);
  for (int i = 0; i < 600 && !lv.done; i++) Thread.sleep(50L);
  if (!lv.done) { fail("the live world read did not run on the world thread in 30 s"); return null; }
  if (lv.err != null) { fail("the live world read failed: " + lv.err); return null; }
  return lv.res;
}""",
    r"""
public void run() {
  try {
    %(UNI)s u = null;
    %(WLD)s d = null;
    for (int i = 0; i < 600; i++) {
      u = %(UNI)s.get();
      d = u == null ? null : u.getDefaultWorld();
      if (d != null && d.isAlive()) break;
      Thread.sleep(500L);
    }
    if (d == null) { fail("no default world after 300 s"); return; }
    Thread.sleep(3000L);
    log("default world '" + d.getName() + "' up - creating the 0.7 zone islands world through SkyyWorldGen's /zone code (WgOpen.startCreate)");
    check(%(ZI)s.REGISTERED && %(W)sWgZoneIsles.REGISTERED, "SkyyWorldGen registered both generator types (0.7 " + %(ZI)s.TYPE + " + 0.6 " + %(W)sWgZoneIsles.TYPE + ")");
    check(%(W)sWgCheck.structureProblem(3) == null && %(W)sWgCheck.templateOk(3), "WgCheck: /zone 1-5 may open (type registered, template in the jar)");
    int dec = %(W)sWgOpen.decide(3, d);
    check(dec == 4, "decide(zones2) on a fresh copy = 4 (create): " + dec);
    long tc = System.currentTimeMillis();
    %(CF)s f = %(W)sWgOpen.startCreate(3, d, new %(TRF)s(0.0, 100.0, 0.0), null);
    %(WLD)s w = (%(WLD)s) f.get(300L, java.util.concurrent.TimeUnit.SECONDS);
    log("TIME world created in " + (System.currentTimeMillis() - tc) + " ms");
    check(w != null && w.getName().equals("skywynn_zones2"), "the 0.7 zone islands world exists: " + (w == null ? null : w.getName()));
    check(%(W)sWgZones.isIsland(3, w) && %(W)sWgZones.islandIndex(w) == 3, "WgZones: the new world is the 0.7 zone islands world (WgZ2Provider)");
    %(W)sWgZ2Gen g = %(ZI)s.genOf(w);
    check(g != null, "the world's chunk generator is WgZ2Gen: " + (w.getChunkStore().getGenerator() == null ? null : w.getChunkStore().getGenerator().getClass().getName()));
    if (g == null) return;
    int seed = (int) w.getWorldConfig().getSeed();
    check(seed == %(SEED)d, "the world seed = the 0.6 seed (the same vanilla map): " + seed);
    %(ZL)s L = g.layoutNow(seed);
    LAY = L;
    java.nio.file.Path lfile = %(ZI)s.layoutFile(seed);
    check(!L.fromFile && lfile != null && lfile.getFileName().toString().equals("zone2_layout_" + seed + ".bin") && java.nio.file.Files.isRegularFile(lfile, new java.nio.file.LinkOption[0]), "the first pick is saved to zone2_layout_<seed>.bin: " + lfile);
    log("LAYOUT " + %(ZI)s.layoutText(L));
    int nf = 0;
    for (int i = 0; i < L.nMain; i++) if (L.found[i] && L.sd[i] != null) nf++;
    check(nf == 5, "an island for every zone 1-5 on the REAL vanilla 0.7 map: " + nf);
    check(L.spawnCls == 1, "the vanilla spawn point stands on Zone 1 land (class " + L.spawnCls + ")");
    %(W)sWgZoneSampler smp = new %(W)sWgZoneSampler(g.getZonePatternGenerator(seed), seed, g.getZonePatternProvider().getZones());
    double[] mm = new double[1];
    for (int i = 0; i < L.n; i++) {
      if (!L.found[i]) { if (i >= L.nMain) log("ISLET " + i + " zone " + (L.zone[i] + 1) + " NOT PLACED"); continue; }
      float[] s = L.sd[i];
      int n = L.gn[i];
      long inside = 0L;
      long same = 0L;
      for (int p = 0; p < s.length; p += 3) {
        if (s[p] <= 0.0f) continue;
        inside++;
        if (smp.applyAsInt(L.gx0[i] + (p %% n) * L.cell[i], L.gz0[i] + (p / n) * L.cell[i]) == L.cls[i]) same++;
      }
      double pur = inside == 0L ? 0.0 : (double) same / (double) inside;
      int sz = Math.max(L.maxX[i] - L.minX[i], L.maxZ[i] - L.minZ[i]) + L.cell[i];
      if (i < L.nMain) {
        log("ISLAND " + (i + 1) + " " + %(ZI)s.Z_NAMES[i] + ": centre " + Math.round(L.cx[i]) + " " + Math.round(L.cz[i]) + ", land " + L.area[i] + " m2, " + sz + " blocks across, floor y " + L.lowY[i] + " (heights " + L.hmin[i] + "-" + L.hmax[i] + "), holes " + L.holes[i] + ", purity " + Math.round(pur * 1000.0) / 10.0 + "%%, circularity " + Math.round(circ(L.sd[i], L.gn[i], (double) L.cell[i]) * 1000.0) / 1000.0);
        check(pur >= 0.97, "Zone " + (i + 1) + " island = its own vanilla zone's land (purity >= 97%%): " + Math.round(pur * 1000.0) / 10.0 + "%%");
        check(L.area[i] >= 200000L, "Zone " + (i + 1) + " island has real size (>= 0.2 km2): " + L.area[i] + " m2");
        %(TRF)s lt = g.landingOf(seed, i);
        int li = lt == null ? -1 : %(ZI)s.member(L, lt.getPosition().x, lt.getPosition().z, mm);
        check(lt != null && li == i, "Zone " + (i + 1) + " landing (/zone " + (i + 1) + ") stands on its own island: " + (lt == null ? null : lt.getPosition()) + " island " + li);
      } else {
        double near = 1.0E9;
        int n2 = L.gn[L.zone[i]];
        for (int p = 0; p < s.length; p++) {
          if (s[p] <= 0.0f) continue;
          double sd = %(ZI)s.sdAt(L, L.zone[i], (double) (L.gx0[i] + (p %% n) * L.cell[i]), (double) (L.gz0[i] + (p / n) * L.cell[i]));
          if (0.0 - sd < near) near = 0.0 - sd;
        }
        log("ISLET " + i + " zone " + (L.zone[i] + 1) + ": centre " + Math.round(L.cx[i]) + " " + Math.round(L.cz[i]) + ", " + sz + " blocks across, dy " + L.dy[i] + " (vanilla heights " + L.hmin[i] + "-" + L.hmax[i] + ", underside rim y " + Math.round(L.refY[i]) + ", depth " + Math.round(L.depth[i]) + "), land gap to its island " + (near >= 63.0 ? ">= 64" : String.valueOf(Math.round(near))) + " (planned " + Math.round(L.gapUsed[i]) + "), purity " + Math.round(pur * 1000.0) / 10.0 + "%%");
        check(pur >= 0.9, "islet " + i + " = its zone's vanilla land (purity >= 90%%): " + Math.round(pur * 1000.0) / 10.0 + "%%");
        check(near >= 10.0, "islet " + i + " is clear of its island (land gap >= 10): " + near);
      }
    }
    int z1n = 0;
    int z1up = 0;
    int z1dn = 0;
    for (int i = L.nMain; i < L.n; i++) if (L.found[i] && L.zone[i] == 0) { z1n++; if (L.dy[i] > 0) z1up++; else z1dn++; }
    check(z1n >= 4 && z1up > 0 && z1dn > 0, "Zone 1 islets on the real map: " + z1n + " of 6 (" + z1up + " raised, " + z1dn + " lowered)");
    double minGap = 1.0E9;
    for (int i = 0; i < L.nMain; i++) for (int j = i + 1; j < L.nMain; j++) {
      double dx = L.cx[i] - L.cx[j];
      double dz = L.cz[i] - L.cz[j];
      double gap = Math.sqrt(dx * dx + dz * dz) - L.rad[i] - L.rad[j];
      if (gap < minGap) minGap = gap;
    }
    check(minGap >= 1100.0, "the zone radius circles stay >= 1100 apart (the 0.6 GAP rule): " + Math.round(minGap));
    %(W)sWgZoneLayout L6 = %(W)sWgZoneIsles.layout(smp, L.spx, L.spz, seed);
    double c7 = circ(L.sd[0], L.gn[0], (double) L.cell[0]);
    double c6 = circ(L6.sd[0], L6.gn[0], 8.0);
    double a7 = arcShare(L.sd[0], L.gn[0], L.gx0[0], L.gz0[0], (double) L.cell[0], L.cx[0], L.cz[0], L.rad[0]);
    double a6 = arcShare(L6.sd[0], L6.gn[0], L6.gx0[0], L6.gz0[0], 8.0, L6.cx[0], L6.cz[0], L.rad[0]);
    log("ROUND Zone 1 circularity 0.7 " + Math.round(c7 * 1000.0) / 1000.0 + " vs 0.6 " + Math.round(c6 * 1000.0) / 1000.0 + "; area 0.7 " + L.area[0] + " vs 0.6 " + L6.area[0] + " m2; coast along the cap circle 0.7 " + Math.round(a7 * 100.0) + "%% vs 0.6 " + Math.round(a6 * 100.0) + "%%");
    check(a7 < 0.15, "fix round: no long round arcs - only " + Math.round(a7 * 100.0) + "%% of Zone 1's coast lies within 4%% of the cap circle (0.6: " + Math.round(a6 * 100.0) + "%%)");
    check(c7 < c6 * 0.75, "Zone 1 is clearly less round than 0.6 on the real map (circularity " + Math.round(c7 * 1000.0) / 1000.0 + " vs " + Math.round(c6 * 1000.0) / 1000.0 + ")");
    check(L.area[0] * 100L >= L6.area[0] * 80L, "fix round: Zone 1 stays the BIG main island - " + L.area[0] + " m2 = " + Math.round(L.area[0] * 100.0 / L6.area[0]) + "%% of the 0.6 island (>= 80%%)");
    int z1big = 0;
    int z1small = 0;
    String z1sz = "";
    for (int i = L.nMain; i < L.n; i++) {
      if (!L.found[i] || L.zone[i] != 0) continue;
      int sz = Math.max(L.maxX[i] - L.minX[i], L.maxZ[i] - L.minZ[i]) + L.cell[i];
      z1sz = z1sz + " " + sz;
      if (sz >= 60) z1big++;
      if (sz <= 40) z1small++;
    }
    check(z1big >= 2 && z1small >= 1, "fix round: Zone 1 islets of VARIOUS sizes on the real map - blocks across:" + z1sz + " (" + z1big + " of 60+, " + z1small + " of 40 or less)");
    writeMap(g, L, L6, seed, OUTDIR + "/map.bin");
    java.io.PrintWriter iw = new java.io.PrintWriter(new java.io.FileWriter(OUTDIR + "/islets.txt"));
    for (int i = L.nMain; i < L.n; i++) if (L.found[i]) iw.println(i + " " + L.dy[i] + " " + L.zone[i]);
    iw.close();
    log("MAP written");
    %(CG)s v = (%(CG)s) new com.hypixel.hytale.server.worldgen.HytaleWorldGenProvider().getGenerator();
    int lava1 = %(FL)s.getAssetMap().getIndexOrDefault("Lava_Source", -9);
    int lava2 = %(FL)s.getAssetMap().getIndexOrDefault("Lava", -9);
    int stone = bid("Rock_Stone");
    int envVoid = com.hypixel.hytale.server.core.asset.type.environment.config.Environment.getAssetMap().getIndexOrDefault("Env_Void", -9);
    %(ZI)s.ids();
    int miss = 0;
    for (int i = 0; i < %(ZI)s.SHORE.length; i++) if (%(ZI)s.SHORE[i] <= 0) miss++;
    for (int i = 0; i < %(ZI)s.WATER.length; i++) if (%(ZI)s.WATER[i] <= 0) miss++;
    check(miss == 0, "the shore blocks + the vanilla water fluids are loaded: " + miss + " missing");
    %(W)sWgZ2River rv = new %(W)sWgZ2River(g, seed);
    long[] st = new long[28];
    long[] tm = new long[3];
    int[] cs = samples(L);
    log("sampling " + (cs.length / 2) + " chunks");
    for (int i = 0; i + 1 < cs.length; i += 2) one(g, v, L, seed, cs[i], cs[i + 1], rv, lava1, lava2, stone, envVoid, st, tm);
    // ---- the coast: find a mountain edge, a lake edge, a river mouth (Zone 1 first, then the other islands)
    double[] best = new double[] { 0.0 - 1.0, 0.0, 0.0, 0.0, 0.0 };
    double[] lake = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0 };
    double[] riv = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0 };
    int scanned = 0;
    for (int zi = 0; zi < L.nMain && (riv[0] <= 0.0 || lake[0] <= 0.0); zi++) {
      if (!L.found[zi]) continue;
      for (int a = 0; a < 240; a++) {
        double ang = a * 6.283185307179586 / 240.0;
        double ux = Math.cos(ang);
        double uz = Math.sin(ang);
        double t = 0.0;
        double lx = 0.0;
        double lz = 0.0;
        boolean got = false;
        while (t < L.rad[zi] + 40.0) {
          double x = L.cx[zi] + ux * t;
          double z = L.cz[zi] + uz * t;
          if (%(ZI)s.member(L, x, z, mm) == zi) { lx = x; lz = z; got = true; }
          t += 2.0;
        }
        if (!got) continue;
        int hx = (int) Math.floor(lx);
        int hz = (int) Math.floor(lz);
        int hv = g.getHeight(seed, hx, hz);
        double rel = hv - L.lowY[zi];
        if (zi == 0 && rel > best[0]) { best[0] = rel; best[1] = lx; best[2] = lz; best[3] = ux; best[4] = uz; }
        if (a %% 3 != 0) continue;
        scanned++;
        int cx = hx >> 5;
        int cz = hz >> 5;
        %(GC)s r = (%(GC)s) v.generate(seed, com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx, cz), cx, cz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
        %(FS)s[] rf = fsOf(r);
        int wcols = 0;
        for (int dx = 0 - 3; dx <= 3; dx++) for (int dz = 0 - 3; dz <= 3; dz++) {
          int x = hx + dx;
          int z = hz + dz;
          if ((x >> 5) != cx || (z >> 5) != cz) continue;
          int h2 = g.getHeight(seed, x, z);
          int f2 = fl(rf, x & 31, h2 + 1, z & 31);
          if (f2 != %(FL)s.EMPTY_ID && f2 != lava1 && f2 != lava2) wcols++;
        }
        if (wcols < 4) continue;
        boolean isr = rv.applyAsInt(hx, hz) != 0;
        if (isr && wcols > riv[0]) { riv[0] = wcols; riv[1] = lx; riv[2] = lz; riv[3] = ux; riv[4] = uz; }
        if (!isr && wcols > lake[0]) { lake[0] = wcols; lake[1] = lx; lake[2] = lz; lake[3] = ux; lake[4] = uz; }
      }
    }
    log("SPOTS scanned " + scanned + " coast chunks: mountain rel " + Math.round(best[0]) + " at " + Math.round(best[1]) + " " + Math.round(best[2]) + "; lake " + Math.round(lake[0]) + " water columns at " + Math.round(lake[1]) + " " + Math.round(lake[2]) + "; river " + Math.round(riv[0]) + " at " + Math.round(riv[1]) + " " + Math.round(riv[2]));
    boolean[] seenB = new boolean[65536];
    boolean[] seenF = new boolean[256];
    java.io.PrintWriter sp = new java.io.PrintWriter(new java.io.FileWriter(OUTDIR + "/spots.txt"));
    String[] snm = new String[] { "mountain", "lake", "river" };
    for (int k = 0; k < 3; k++) {
      double[] q = k == 0 ? best : (k == 1 ? lake : riv);
      if ((k == 0 && q[0] < 0.0) || (k > 0 && q[0] <= 0.0)) { sp.println(snm[k] + " none"); continue; }
      int cx = ((int) Math.floor(q[1]) >> 5) - 1;
      int cz = ((int) Math.floor(q[2]) >> 5) - 1;
      dumpRegion(g, v, L, seed, cx, cz, OUTDIR + "/" + snm[k] + ".bin", seenB, seenF);
      for (int a = 0; a < 3; a++) for (int c = 0; c < 3; c++) one(g, v, L, seed, cx + a, cz + c, rv, lava1, lava2, stone, envVoid, st, tm);
      sp.println(snm[k] + " " + q[1] + " " + q[2] + " " + q[3] + " " + q[4] + " " + q[0] + " " + cx + " " + cz);
    }
    sp.close();
    long[] spl = new long[3];
    for (int k = 0; k < 3; k++) {
      double[] q = k == 0 ? best : (k == 1 ? lake : riv);
      if (q[0] <= 0.0) continue;
      spill(g, v, L, seed, ((int) Math.floor(q[1]) >> 5) - 1, ((int) Math.floor(q[2]) >> 5) - 1, spl, lava1, lava2);
    }
    for (int a = 0; a < 16; a++) {
      double ang = a * 6.283185307179586 / 16.0 + 0.1;
      double t = 0.0;
      double lx = 0.0;
      double lz = 0.0;
      boolean got = false;
      while (t < L.rad[0] + 40.0) {
        double x = L.cx[0] + Math.cos(ang) * t;
        double z = L.cz[0] + Math.sin(ang) * t;
        if (%(ZI)s.member(L, x, z, mm) == 0) { lx = x; lz = z; got = true; }
        t += 2.0;
      }
      if (got) spill(g, v, L, seed, ((int) Math.floor(lx) >> 5) - 1, ((int) Math.floor(lz) >> 5) - 1, spl, lava1, lava2);
    }
    log("SPILLS " + spl[0] + " newly exposed water voxels inside the islands (" + spl[1] + " across a chunk border) among " + spl[2] + " water voxels in 19 coast regions; chunk border rims so far " + %(ZI)s.BORDER_RIM.get());
    check(spl[2] > 0L && spl[0] == 0L, "fix round: no lake / river beside a LOWERED bank (no sideways spill inside the island, within or across chunk borders): " + spl[0] + " exposed voxels (" + spl[1] + " across a border) of " + spl[2]);
    check(best[0] >= 0.0 && lake[0] > 0.0, "found a mountain edge (" + Math.round(best[0]) + " above the floor) and a lake at the coast (" + Math.round(lake[0]) + " water columns) to render");
    log("STATS chunks " + tm[2] + " outsideBad " + st[0] + " belowBad " + st[1] + " changedBad " + st[2] + " sealed " + st[3] + " identical " + st[4] + " exposedFluid " + st[5] + " shellBad " + st[6] + " lavaKept " + st[7] + " fluidKept " + st[8] + " deco " + st[9] + " insideCols " + st[10] + " outsideCols " + st[11] + " ore " + st[12] + " entsOutside " + st[13] + " entsMasked " + st[14] + " entsVanilla " + st[15] + " envBad " + st[16] + " rootsBelow " + st[17] + " mouthFluid " + st[18] + " loweredCols " + st[19] + " loweredGround " + st[20] + " isletCols " + st[21] + " isletBad " + st[22] + " rimCols " + st[23] + " bandCols " + st[24] + " interiorCols " + st[25] + " isletEnvBad " + st[26] + " borderRims " + %(ZI)s.BORDER_RIM.get());
    log("TIME masked " + (tm[0] / Math.max(1L, tm[2]) / 1000000L) + " ms avg, vanilla " + (tm[1] / Math.max(1L, tm[2]) / 1000000L) + " ms avg over " + tm[2] + " chunks; the mask pass " + (%(ZI)s.MASK_NS.get() / Math.max(1L, %(ZI)s.MASKED.get()) / 100000L) / 10.0 + " ms per chunk");
    check(st[0] == 0L && st[1] == 0L && st[13] == 0L && st[16] == 0L, "outside the islands / under the undersides: nothing left (blocks, fluid, entity groups; only roots under a rim), Env_Void");
    check(st[2] == 0L, "island interiors (40+ blocks from the coast) are vanilla's own voxel for voxel (+ sealing stone, decoration, Zone 4-5 ores)");
    check(st[5] == 0L && st[6] == 0L, "sealed: no lake / lava / cave fluid beside the void or on the underside (river mouths aside), the 2 bottom blocks solid");
    check(st[21] > 0L && st[22] == 0L, "islet columns = the vanilla column moved by dy (" + st[21] + " columns)");
    check(st[19] > 0L && st[20] >= st[19] * 9L / 10L, "the coast band LOWERED high ground (" + st[19] + " columns) and kept a natural ground top on " + st[20]);
    check(st[23] > 0L, "lake water at the coast got a natural shore rim (" + st[23] + " columns)");
    check(st[10] > 5000L && st[11] > 2000L, "the sample covers island and void columns: " + st[10] + " / " + st[11]);
    // ---- the waterfall in the LIVE world: the river mouth's 3 x 3 chunks loaded TICKING, the void columns' water measured over time
    if (riv[0] > 0.0) {
      int cx = ((int) Math.floor(riv[1]) >> 5) - 1;
      int cz = ((int) Math.floor(riv[2]) >> 5) - 1;
      boolean[] vc = new boolean[96 * 96];
      for (int x = 0; x < 96; x++) for (int z = 0; z < 96; z++) vc[x * 96 + z] = %(ZI)s.member(L, cx * 32 + x + 0.5, cz * 32 + z + 0.5, mm) < 0;
      int[] at = new int[] { 2, 8, 20, 40, 60, 90, 120, 150 };
      long tk0 = w.getTick();
      log("FALLW world tick " + tk0 + ", paused " + w.isPaused() + ", ticking " + w.isTicking());
      if (w.isPaused()) { w.setPaused(false); log("FALLW the world was paused (no player on it) - unpaused for this test (scratch copy of the world)"); }
      long t0 = System.currentTimeMillis();
      java.io.PrintWriter fo = new java.io.PrintWriter(new java.io.FileWriter(OUTDIR + "/fall.txt"));
      long[] last = null;
      long[] prev = null;
      for (int k = 0; k < at.length; k++) {
        while (System.currentTimeMillis() - t0 < at[k] * 1000L) Thread.sleep(200L);
        long[] r = live(w, cx * 32, cz * 32, vc, false, null, null);
        if (r == null) break;
        prev = last;
        last = r;
        String line = "FALL t " + at[k] + " s: water in void columns " + r[0] + " voxels (y " + (r[0] > 0L ? r[2] + ".." + r[1] : "-") + "), all fluid voxels " + r[5] + ", ticking blocks " + r[3] + ", sections not loaded " + r[4] + ", world ticks since start " + (w.getTick() - tk0) + " (paused " + w.isPaused() + ")";
        log(line);
        fo.println(at[k] + " " + r[0] + " " + r[1] + " " + r[2] + " " + r[3] + " " + r[5] + " " + r[4]);
      }
      fo.close();
      if (last != null) {
        check(last[0] > 0L, "the river mouth spilled off the edge: " + last[0] + " water voxels in the void columns after 90 s");
        check(prev != null && last[0] - prev[0] <= Math.max(64L, prev[0] / 20L) && last[3] <= prev[3] + 64L, "the waterfall settles: void water " + (prev == null ? -1 : prev[0]) + " -> " + last[0] + " voxels and ticking blocks " + (prev == null ? -1 : prev[3]) + " -> " + last[3] + " between 120 s and 150 s (no runaway)");
        long tks = w.getTick() - tk0;
        log("FALLW " + tks + " world ticks in the watch; the fall's lowest water y " + last[2] + (last[2] <= 2L ? " (reached the bottom and parked)" : " (did NOT reach the bottom)"));
        check(tks > 100L, "fix round: the world really ticked during the waterfall watch (" + tks + " ticks), so the fall was watched live, not only the chunk's 100-tick pre-process");
        short[] lb = new short[96 * 96 * 320];
        byte[] lf = new byte[96 * 96 * 320];
        live(w, cx * 32, cz * 32, vc, true, lb, lf);
        java.io.DataOutputStream o = new java.io.DataOutputStream(new java.io.BufferedOutputStream(new java.io.FileOutputStream(OUTDIR + "/live.bin")));
        o.writeInt(cx * 32); o.writeInt(cz * 32);
        for (int i = 0; i < lb.length; i++) {
          o.writeShort(lb[i]);
          o.writeByte(lf[i]);
          int bi = lb[i] & 65535;
          if (bi < seenB.length) seenB[bi] = true;
          int fi = lf[i] & 255;
          seenF[fi] = true;
        }
        o.close();
      }
    } else {
      log("FALL no river mouth found on the coasts - waterfall live test NOT RUN");
    }
    writeNames(seenB, seenF, OUTDIR + "/names.txt");
    java.util.concurrent.Executor gp = g.poolNow();
    check(gp instanceof java.util.concurrent.ThreadPoolExecutor, "WgZ2Gen found vanilla's own generator pool for the mask hop; hops " + %(ZI)s.HOPPED.get());
    long sk0 = %(ZI)s.SKIPPED.get();
    double fx = (L.cx[0] + L.cx[1]) / 2.0;
    double fz = (L.cz[0] + L.cz[1]) / 2.0;
    %(GC)s far = (%(GC)s) g.generate(seed, 0L, (int) Math.floor(fx / 32.0), (int) Math.floor(fz / 32.0), null, null).get(60L, java.util.concurrent.TimeUnit.SECONDS);
    check(far != null && %(ZI)s.SKIPPED.get() == sk0 + 1L, "a chunk in the void between Zone 1 and Zone 2 is skipped");
    %(W)sWgZ2Gen g2 = (%(W)sWgZ2Gen) new %(W)sWgZ2Provider().getGenerator();
    %(ZL)s L2 = g2.layoutNow(seed);
    boolean same = L2.n == L.n;
    for (int i = 0; same && i < L.n; i++) {
      if (L.found[i] != L2.found[i] || L.cx[i] != L2.cx[i] || L.cz[i] != L2.cz[i] || L.dy[i] != L2.dy[i]) same = false;
      if (L.sd[i] != null && !java.util.Arrays.equals(L.sd[i], L2.sd[i])) same = false;
    }
    check(same && L2.fromFile, "a fresh generator (= the next server start) REUSES the saved layout (fromFile " + L2.fromFile + ")");
    %(ZL)s L4 = %(ZI)s.layout(new %(W)sWgZoneSampler(g2.getZonePatternGenerator(seed), seed, g2.getZonePatternProvider().getZones()), new %(W)sWgZ2Fn(g2, seed, 0, 0), L.spx, L.spz, seed, %(ZI)s.counts());
    boolean same4 = L4.n == L.n;
    for (int i = 0; same4 && i < L.n; i++) {
      if (L.found[i] != L4.found[i] || L.cx[i] != L4.cx[i] || L.cz[i] != L4.cz[i] || L.dy[i] != L4.dy[i]) same4 = false;
      if (L.sd[i] != null && !java.util.Arrays.equals(L.sd[i], L4.sd[i])) same4 = false;
    }
    check(same4, "determinism: a fresh pick from the real vanilla map gives the SAME islands + islets");
    long diffs = 0L;
    for (int i = 0; i < 6 && i + 1 < cs.length; i += 2) {
      long idx = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cs[i], cs[i + 1]);
      %(GC)s a = (%(GC)s) g.generate(seed, idx, cs[i], cs[i + 1], null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
      %(GC)s b = (%(GC)s) g2.generate(seed, idx, cs[i], cs[i + 1], null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
      for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) for (int y = 0; y < 320; y++) if (a.getBlockChunk().getBlock(x, y, z) != b.getBlockChunk().getBlock(x, y, z)) diffs++;
    }
    check(diffs == 0L, "determinism: the same chunks from the fresh generator are identical block for block: " + diffs + " differences");
    try { g2.shutdown(); } catch (Throwable t) { }
    java.nio.file.Path cfgp = %(W)sWgOpen.folderOf("skywynn_zones2").resolve("config.json");
    com.hypixel.hytale.server.core.universe.world.WorldConfig wc = (com.hypixel.hytale.server.core.universe.world.WorldConfig) com.hypixel.hytale.server.core.universe.world.WorldConfig.load(cfgp).get(30L, java.util.concurrent.TimeUnit.SECONDS);
    check(wc != null && wc.getWorldGenProvider() instanceof %(W)sWgZ2Provider, "the saved config.json decodes back to the SkyWynnZones2 provider");
    for (int i = 0; i < L.nMain; i++) { %(TRF)s lt = g.landingOf(seed, i); if (lt != null) log("PLACE zone " + (i + 1) + ": " + %(ZI)s.placeAt(w, lt.getPosition().x, lt.getPosition().y, lt.getPosition().z)); }
    for (int i = L.nMain; i < L.n; i++) if (L.found[i]) { log("PLACE islet " + i + ": " + %(ZI)s.placeAt(w, L.lx[i], 150.0, L.lz[i])); break; }
    log("STATUS " + %(ZI)s.statusText(w));
    String[] il = %(W)sWgCmds.infoLines(null, null, null, w);
    for (int i = 0; i < il.length; i++) log("INFO " + il[i]);
    v.shutdown();
  } catch (Throwable t) {
    fail("probe crashed: " + t);
    StackTraceElement[] es = t.getStackTrace();
    for (int i = 0; i < es.length && i < 14; i++) log("   at " + es[i]);
  } finally {
    log("RESULT ok=" + OKS + " fail=" + FAILS);
  }
}""",
]


def build_probe(J, out_dir, jar_path, seed, B, outdir):
    pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
    sub = {"FS": FS, "BS": BS, "GC": GC, "GBC": GBC, "HOLD": HOLD, "CG": CG, "WLD": WLD, "UNI": UNI, "TRF": TRF, "CF": CF, "EWE": EWE, "W": W,
           "SEED": seed, "BT": BT, "FL": FL, "ZL": ZL, "ZI": ZI, "PP": PROBE_PKG, "ST": "com.hypixel.hytale.component.Store",
           "REF": "com.hypixel.hytale.component.Ref"}
    lv = pool.makeClass(PROBE_PKG + ".Live")
    lv.addInterface(pool.get("java.lang.Runnable"))
    for f_ in ("public %s w;" % WLD, "public int x0;", "public int z0;", "public boolean[] voidCol;", "public boolean dump;", "public short[] blocks;",
               "public byte[] fluids;", "public volatile long[] res;", "public volatile String err;", "public volatile boolean done;"):
        lv.addField(CtField.make(f_, lv))
    lv.addConstructor(CtNewConstructor.make("public Live() { }", lv))
    for src in LIVE_METHODS:
        lv.addMethod(CtNewMethod.make(src % sub, lv))
    run = pool.makeClass(PROBE_PKG + ".Run")
    run.addInterface(pool.get("java.lang.Runnable"))
    run.addField(CtField.make("public static com.hypixel.hytale.logger.HytaleLogger LOG;", run))
    run.addField(CtField.make("public static volatile int OKS = 0;", run))
    run.addField(CtField.make("public static volatile int FAILS = 0;", run))
    run.addField(CtField.make("public static %s LAY;" % ZL, run))
    run.addField(CtField.make("public static final String OUTDIR = \"%s\";" % outdir.replace("\\", "/"), run))
    run.addConstructor(CtNewConstructor.make("public Run() { }", run))
    for src in PROBE_METHODS:
        body = src % sub
        try:
            run.addMethod(CtNewMethod.make(body, run))
        except Exception as e:
            raise SystemExit("probe compile failed: %s --- %s" % (e, body[:3000]))
    pl = pool.makeClass(PROBE_PKG + ".SkyyWgProbe7Plugin", pool.get("com.hypixel.hytale.server.core.plugin.JavaPlugin"))
    pl.addConstructor(CtNewConstructor.make("public SkyyWgProbe7Plugin(com.hypixel.hytale.server.core.plugin.JavaPluginInit init) { super(init); }", pl))
    pl.addMethod(CtNewMethod.make(r"""
public void setup() {
  %s.Run.LOG = getLogger();
  %s.Run.log("%s ready (TEST PROBE - never deploy)");
  Thread t = new Thread(new %s.Run(), "SkyyWgProbe7");
  t.setDaemon(true);
  t.start();
}""" % (PROBE_PKG, PROBE_PKG, PROBE_VERSION, PROBE_PKG), pl))
    for c in (lv, run, pl):
        c.writeFile(out_dir)
    man = B.manifest("SkyyWgProbe7", PROBE_VERSION, "TEST PROBE for SkyyWorldGen 0.7 (scratch only, never deployed)", PROBE_PKG + ".SkyyWgProbe7Plugin")
    man["IncludesAssetPack"] = False
    man["Dependencies"] = {"Skyy:0.7 SkyyWorldGen": "*"}
    B.assemble(jar_path, man, out_dir)
'''

PROBE_BUILD = r'''import os, sys
sys.path.insert(0, %(tools)r)
sys.path.insert(0, %(pdir)r)
import skyybuild as B
J = B.start()
J["pool"].insertClassPath(%(jar)r)
import probe_src as P
os.makedirs(os.path.join(%(pdir)r, "classes"), exist_ok=True)
P.build_probe(J, os.path.join(%(pdir)r, "classes"), os.path.join(%(pdir)r, "SkyyWgProbe7-0.7.jar"), %(seed)d, B, %(out)r)
'''


# ============================================================================================ renders (the harness LOOKS at these)
def block_color(name):
    n = name or "?"
    table = [("Water", (60, 110, 220)), ("Lava", (240, 110, 30)), ("Leaves", (50, 110, 45)), ("Grass", (95, 150, 60)), ("Snow", (240, 240, 245)),
             ("Ice", (170, 200, 240)), ("Sand_Red", (190, 100, 60)), ("Sandstone_Red", (170, 90, 55)), ("Sandstone", (210, 190, 130)),
             ("Sand", (220, 200, 140)), ("Dirt", (120, 85, 55)), ("Mud", (95, 75, 55)), ("Clay", (150, 110, 90)), ("Gravel", (140, 135, 130)),
             ("Basalt", (60, 60, 66)), ("Volcanic", (70, 55, 55)), ("Ash", (90, 88, 88)), ("Magma", (140, 60, 40)), ("Ore_", (180, 140, 90)),
             ("Wood", (110, 80, 50)), ("Log", (110, 80, 50)), ("Trunk", (110, 80, 50)), ("Plant_Flower", (200, 80, 140)), ("Plant", (100, 165, 70)),
             ("Crystal", (220, 60, 60)), ("Shale", (90, 95, 105)), ("Slate", (85, 90, 100)), ("Calcite", (200, 200, 190)), ("Marble", (215, 215, 210)),
             ("Quartzite", (190, 185, 180)), ("Moss", (80, 120, 60)), ("Stone", (125, 125, 130)), ("Rock", (120, 120, 125)), ("Rubble", (130, 125, 120))]
    for k, c in table:
        if k in n:
            return c
    h = zlib.crc32(n.encode()) & 0xffffff
    return (90 + (h & 127), 90 + ((h >> 8) & 127), 90 + ((h >> 16) & 127))


def load_names(path):
    B_, F_ = {}, {}
    if os.path.isfile(path):
        for ln in open(path, encoding="utf-8", errors="replace"):
            p = ln.split()
            if len(p) >= 3:
                (B_ if p[0] == "B" else F_)[int(p[1])] = p[2]
    return B_, F_


def read_region(path, live=False):
    d = open(path, "rb").read()
    x0, z0 = struct.unpack(">ii", d[:8])
    o = 8
    ent = dy = None
    if not live:
        ent, dy = [0] * 9216, [0] * 9216
        for i in range(9216):
            ent[i] = d[o]
            dy[i] = struct.unpack(">h", d[o + 1:o + 3])[0]
            o += 3
    vols = []
    for _p in range(1 if live else 2):
        blk = [0] * (9216 * 320)
        flu = bytearray(9216 * 320)
        mv = memoryview(d)[o:o + 9216 * 320 * 3]
        for i in range(9216 * 320):
            j = i * 3
            blk[i] = (mv[j] << 8) | mv[j + 1]
            flu[i] = mv[j + 2]
        o += 9216 * 320 * 3
        vols.append((blk, flu))
    return x0, z0, ent, dy, vols


def side_view(blk, flu, names, fnames, ux, uz, scale=3, y_lo=None, y_hi=None, keep=None):
    """an orthographic view from the void side (outward direction ux, uz) into the island: per (u, y) the first voxel hit"""
    alongx = abs(ux) >= abs(uz)
    ys = range(320)
    lo, hi = 319, 0
    for c in range(9216):
        for y in range(320):
            if blk[c * 320 + y] or flu[c * 320 + y]:
                lo, hi = min(lo, y), max(hi, y)
    if y_lo is not None:
        lo, hi = y_lo, y_hi
    lo, hi = max(0, lo - 6), min(319, hi + 6)
    H = hi - lo + 1
    im = Img(96 * scale, H * scale, (18, 20, 30))
    for u in range(96):
        for y in range(lo, hi + 1):
            col = None
            for t in range(96):
                if alongx:
                    x = 95 - t if ux > 0 else t
                    z = u
                else:
                    z = 95 - t if uz > 0 else t
                    x = u
                c = x * 96 + z
                if keep is not None and not keep(c):
                    continue
                i = c * 320 + y
                if flu[i]:
                    col = block_color(fnames.get(flu[i], "Water"))
                elif blk[i]:
                    col = block_color(names.get(blk[i], "?"))
                if col:
                    sh = 1.0 - min(0.55, t / 120.0)
                    col = tuple(v * sh for v in col)
                    break
            if col:
                uu = (95 - u) if ((alongx and ux > 0) or (not alongx and uz < 0)) else u
                im.rect(uu * scale, (hi - y) * scale, uu * scale + scale, (hi - y) * scale + scale, col)
    return im, lo, hi


def top_view(blk, flu, names, fnames, scale=3):
    im = Img(96 * scale, 96 * scale, (18, 20, 30))
    for x in range(96):
        for z in range(96):
            c = x * 96 + z
            for y in range(319, -1, -1):
                i = c * 320 + y
                if flu[i] or blk[i]:
                    col = block_color(fnames.get(flu[i], "Water")) if flu[i] else block_color(names.get(blk[i], "?"))
                    sh = 0.55 + 0.45 * (y / 319.0)
                    im.rect(x * scale, z * scale, x * scale + scale, z * scale + scale, tuple(v * min(1.2, sh * 1.3) for v in col))
                    break
    return im


def planar_cut(ent, dy, vol):
    """what a 0.6-style mask makes of the same spot: vanilla inside the 0.7 outline (moved by dy), nothing outside - the flat cut"""
    blk, flu = vol
    b2, f2 = [0] * len(blk), bytearray(len(flu))
    for c in range(9216):
        if ent[c] == 255:
            continue
        d_ = dy[c]
        for y in range(320):
            yv = y - d_
            if 0 <= yv < 320:
                b2[c * 320 + y] = blk[c * 320 + yv]
                f2[c * 320 + y] = flu[c * 320 + yv]
    return b2, f2


def render_vp(vdir):
    names, fnames = load_names(os.path.join(vdir, "names.txt"))
    out = {}
    # (a) the map
    mp = os.path.join(vdir, "map.bin")
    if os.path.isfile(mp):
        d = open(mp, "rb").read()
        x0, z0, step, w, h = struct.unpack(">iiiii", d[:20])
        o = 20
        ent, o6, hh = bytearray(w * h), bytearray(w * h), [0] * (w * h)
        for i in range(w * h):
            ent[i], o6[i] = d[o], d[o + 1]
            hh[i] = struct.unpack(">h", d[o + 2:o + 4])[0]
            o += 4
        land = [hh[i] for i in range(w * h) if ent[i] != 255]
        UP = set()
        isf = os.path.join(vdir, "islets.txt")
        if os.path.isfile(isf):
            UP = set(int(ln.split()[0]) for ln in open(isf) if ln.split() and int(ln.split()[1]) > 0)
        hmin, hmax = (min(land), max(land)) if land else (100, 200)
        sc = max(1, min(3, 1400 // max(w, h)))
        im = Img(w * sc, h * sc, (14, 16, 26))
        for k in range(h):
            for j in range(w):
                i = k * w + j
                e = ent[i]
                if e != 255:
                    t = (hh[i] - hmin) / max(1.0, hmax - hmin)
                    base = (70, 150, 60) if e == 0 else ((235, 160, 50) if False else (200, 170, 90))
                    if e >= 5:
                        base = (240, 150, 40) if e in UP else (70, 130, 235)
                    # hill shading from the east neighbour
                    jn = min(w - 1, j + 1)
                    slope = hh[i] - hh[k * w + jn] if ent[k * w + jn] != 255 else 0
                    lit = 0.65 + 0.45 * t + max(-0.25, min(0.25, slope * 0.04))
                    col = tuple(v * lit for v in base)
                elif o6[i]:
                    col = (48, 50, 62)
                else:
                    col = (14, 16, 26)
                # the 0.6 outline in light grey
                if o6[i] and ((j + 1 < w and not o6[i + 1]) or (j > 0 and not o6[i - 1]) or (k + 1 < h and not o6[i + w]) or (k > 0 and not o6[i - w])):
                    col = (200, 200, 210)
                im.rect(j * sc, k * sc, j * sc + sc, k * sc + sc, col)
        p = os.path.join(vdir, "wg07-zone1-map.png")
        im.save(p)
        out["map"] = p
    # (b) the edges: mountain + lake, before (0.6-style planar cut of vanilla) and after (0.7)
    spots = {}
    if os.path.isfile(os.path.join(vdir, "spots.txt")):
        for ln in open(os.path.join(vdir, "spots.txt")):
            p = ln.split()
            if len(p) >= 8:
                spots[p[0]] = [float(v) for v in p[1:8]]
    panels = []
    for nm_ in ("mountain", "lake"):
        rp = os.path.join(vdir, nm_ + ".bin")
        if nm_ not in spots or not os.path.isfile(rp):
            continue
        x0, z0, ent, dy, vols = read_region(rp)
        ux, uz = spots[nm_][2], spots[nm_][3]
        after, lo, hi = side_view(vols[0][0], vols[0][1], names, fnames, ux, uz)
        b2, f2 = planar_cut(ent, dy, vols[1])
        before, _l, _h = side_view(b2, f2, names, fnames, ux, uz, y_lo=lo + 6, y_hi=hi - 6)
        panels.append((nm_, before, after))
    if panels:
        W_ = max(p[1].w + p[2].w + 24 for p in panels)
        H_ = sum(max(p[1].h, p[2].h) + 16 for p in panels) + 8
        im = Img(W_, H_, (8, 8, 12))
        y = 8
        for nm_, b_, a_ in panels:
            im.paste(b_, 8, y)
            im.paste(a_, b_.w + 16, y)
            y += max(b_.h, a_.h) + 16
        p = os.path.join(vdir, "wg07-edges.png")
        im.save(p)
        out["edges"] = p
    # (c) the waterfall: live world (side view from the void + top view) and the generated mouth (before the engine let it flow)
    lp = os.path.join(vdir, "live.bin")
    if "river" in spots and os.path.isfile(lp):
        x0, z0, _e, _d, vols = read_region(lp, live=True)
        ux, uz = spots["river"][2], spots["river"][3]
        sv, lo, hi = side_view(vols[0][0], vols[0][1], names, fnames, ux, uz, scale=3)
        tv = top_view(vols[0][0], vols[0][1], names, fnames, scale=3)
        im = Img(sv.w + tv.w + 24, max(sv.h, tv.h) + 16, (8, 8, 12))
        im.paste(sv, 8, 8)
        im.paste(tv, sv.w + 16, 8)
        p = os.path.join(vdir, "wg07-waterfall.png")
        im.save(p)
        out["waterfall"] = p
    return out


def vp():
    if "--no-smoke" in sys.argv:
        NOTES.append("VP skipped (--no-smoke): the real wrapped vanilla generator did NOT run in this harness run - UNVERIFIED by it")
        return
    import deploy_set as DS
    if DS.server_running():
        NOTES.append("VP NOT RUN: a HytaleServer java process is running (the game / a world is open) - the real-generator run, the renders "
                     "and the live waterfall measurement are UNVERIFIED by this harness run; re-run with the game closed")
        print("VP. NOT RUN - the game is running")
        return
    pdir = os.path.join(SCRATCH, "probe")
    vdir = os.path.join(SCRATCH, "vp")
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(pdir, "probe_src.py"), "w", encoding="utf-8") as f_:
        f_.write(PROBE_SRC)
    with open(os.path.join(pdir, "probe_build.py"), "w", encoding="utf-8") as f_:
        f_.write(PROBE_BUILD % {"tools": TOOLS, "pdir": pdir, "jar": JAR, "seed": ZSEED, "out": vdir})
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    r1 = subprocess.run([sys.executable, os.path.join(pdir, "probe_build.py")], cwd=pdir, env=env, capture_output=True, text=True, timeout=900)
    pj = os.path.join(pdir, "SkyyWgProbe7-0.7.jar")
    if not check(r1.returncode == 0 and os.path.isfile(pj), "VP. the test probe jar builds (scratch only): %s" % (r1.stdout + r1.stderr)[-1500:]):
        return
    smoke = os.path.join(TOOLS, "dev", "scratch", "smoke")
    before = set(os.listdir(smoke)) if os.path.isdir(smoke) else set()
    t0 = time.time()
    r2 = subprocess.run([sys.executable, os.path.join(TOOLS, "smoke_test.py"), "--light", "--linger", "600", "--xmx", "6G", "--allow-pack-api",
                         "--jar", JAR, "--jar", pj], cwd=ROOT, env=env, capture_output=True, text=True, timeout=3000)
    logs, txt = [], ""
    for n_ in sorted(n_ for n_ in (set(os.listdir(smoke)) - before) if n_.endswith(".log")):
        t_ = open(os.path.join(smoke, n_), encoding="utf-8", errors="replace").read()
        if "[SkyyWgProbe7]" in t_:
            logs, txt = [n_], t_
    plines = [l_.split("[SkyyWgProbe7] ", 1)[1] for l_ in txt.splitlines() if "[SkyyWgProbe7] " in l_]
    res = [l_ for l_ in plines if l_.startswith("RESULT ")]
    fails = [l_ for l_ in plines if l_.startswith("FAIL ")]
    oks = [l_ for l_ in plines if l_.startswith("OK ")]
    m_ = re.match(r"RESULT ok=(\d+) fail=(\d+)", res[-1]) if res else None
    smoke_out = (r2.stdout or "")
    ours = [l_ for l_ in smoke_out.splitlines() if "SkyyWgProbe7" not in l_]
    check(r2.returncode == 0 or ("FAIL no ready line: SkyyWgProbe7" in smoke_out and "SMOKE TEST FAIL" in smoke_out and
                                 not [l_ for l_ in ours if l_.strip().startswith("FAIL")]),
          "VP. the smoke test (offline server, scratch copy of the live world, the SET with this jar + the probe) PASSES for every SET mod "
          "(the probe prints no SET ready line): exit %d, %s" % (r2.returncode, smoke_out[-600:].replace("\n", " | ")))
    check(m_ is not None and int(m_.group(2)) == 0 and int(m_.group(1)) >= 30 and not fails,
          "VP. the probe on the REAL vanilla 0.7 generator: %s (%d OK lines) %s" % (res[-1] if res else "no RESULT line", len(oks), fails[:8]))
    for l_ in plines:
        if l_.startswith(("LAYOUT", "ISLAND", "ISLET", "ROUND", "STATS", "TIME", "PLACE", "INFO", "CHANGED", "EXPOSED", "SPOTS", "FALL", "FAIL",
                          "RESULT", "sampling", "STATUS", "MAP")):
            NOTES.append("VP " + l_[:900])
    print("VP. real server run %.0f s: %s; log %s" % (time.time() - t0, res[-1] if res else "no result", logs[-1] if logs else "-"))
    try:
        out = render_vp(vdir)
    except Exception as e_:
        import traceback
        out = {}
        check(False, "VP. the renders: %s" % traceback.format_exc()[-800:])
    for k, p in out.items():
        dst = os.path.join(PNG_OUT, os.path.basename(p))
        shutil.copyfile(p, dst)
        NOTES.append("VP render %s -> %s" % (k, dst))
    check(set(out) >= {"map", "edges"}, "VP. the renders exist: %s" % sorted(out))


# ============================================================================================ parent
def main():
    if "--e" in sys.argv:
        return run_e(arg("--out"))
    if "--render" in sys.argv:            # re-render an existing VP folder (no server)
        print(render_vp(arg("--render")))
        return
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)
    only_vp = "--only-vp" in sys.argv
    try:
        if not only_vp:
            # ---- CC
            rules = [[r"worldgen_0_7_patch", "worldgen_0_6_patch"]]
            kid = [re.search(rb"skyyui \d+\.\d+ [0-9a-f]{12}", b"".join(zipfile.ZipFile(j_).read(n) for n in zipfile.ZipFile(j_).namelist() if n.endswith("Plugin.class")))
                   for j_ in (JAR, PREV_JAR)]
            if kid[0] and kid[1]:
                rules.append([re.escape(kid[0].group(0).decode()), kid[1].group(0).decode()])
            out_cc = os.path.join(SCRATCH, "cc.json")
            with open(out_cc + ".log", "wb") as lf:
                subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import importlib.util as u; "
                                "s = u.spec_from_file_location('ts', %r); m = u.module_from_spec(s); sys.argv = ['x', '--dir', %r]; "
                                "s.loader.exec_module(m); m.SCRATCH = %r; m.run_cc(%r, %r, %r, %r)" % (
                                    TOOLS, SKILLS_HARNESS, SCRATCH, SCRATCH, JAR, PREV_JAR, out_cc,
                                    json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules}))],
                               env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
            cc = json.load(open(out_cc)) if os.path.isfile(out_cc) else None
            if cc is None:
                print(open(out_cc + ".log", encoding="utf8", errors="replace").read()[-2000:])
            check(cc is not None, "CC: the compare child ran")
            if cc:
                cls_ = cc["classes"]
                check(sorted(cc["added"]) == NEW_CLASSES and cc["gone"] == [], "CC: + exactly the 8 WgZ2 classes, none gone: %s %s" % (cc["added"], cc["gone"]))
                struct_ = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else " (gone)" if x.endswith("(gone)") else "") for x in v["structural"]))
                               for c, v in cls_.items() if v["structural"])
                const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
                fnew = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
                fgone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
                print("CC. 0.6 -> 0.7 structural %s; constants only %s; fields new %s" % (struct_, const, fnew))
                frozen = [c for c in FROZEN if c in struct_ or c in const or c in fnew or c in fgone]
                check(not frozen, "CC: the 0.5 + 0.6 generator classes and the spawn / store / log classes are UNCHANGED (skywynn_zones and the "
                      "older worlds generate exactly as before): %s" % frozen)
                check(not fgone and all(v["same_shape"] for v in cls_.values()), "CC: no field removed, same supers / interfaces: %s" % fgone)
                allowed = {"WgZones", "WgCheck", "WgCfg", "WgOpen", "WgCmds", "WgHereTask", "WgHooks", "SkyyWorldGenPlugin", "ZoneGoCmd", "ZoneCmd",
                           "WgZoneArrive"}
                check(set(struct_) <= allowed | set(c for c in cls_ if c.startswith("Cfg")), "CC: structural changes only in the zone table / "
                      "check / config / open / commands / hooks / plugin / arrival hop (+ the config kit): %s" % sorted(struct_))
                check(struct_.get("WgOpen") == ["go", "goZone2 (new)"], "CC: WgOpen = go (routes both zone worlds) + goZone2 (new): %s" % struct_.get("WgOpen"))
            # ---- JT
            zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
            cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
            check(sorted(cn - cp_) == ["com/skyy/worldgen/%s.class" % c for c in NEW_CLASSES] and not (cp_ - cn), "JT: class files = 0.6's + the 8: %s %s"
                  % (sorted(cn - cp_), sorted(cp_ - cn)))
            nn = set(n for n in zj.namelist() if not n.endswith(".class"))
            np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
            added = sorted(nn - np_)
            check(added == ["Server/Instances/SkyWynn_Zones2/instance.bson", "Server/Instances/SkyWynn_Zones2/resources/InstanceData.json"]
                  and not (np_ - nn), "JT: + exactly the 0.7 world template: %s %s" % (added, sorted(np_ - nn)))
            norm = lambda b_: b_.replace(b"(SkyyWorldGen %s)" % VERSION.encode(), b"(SkyyWorldGen %s)" % PREV_VERSION.encode())
            diff = sorted(n for n in np_ if n != "manifest.json" and norm(zj.read(n)) != zp.read(n))
            check(not diff, "JT: every old non-class entry byte-identical but the version in a template comment: %s" % diff[:4])
            tz = json.loads(zj.read("Server/Instances/SkyWynn_Zones2/instance.bson"))
            check(tz["WorldGen"] == {"Type": "SkyWynnZones2"} and tz["Seed"] == ZSEED and "SpawnProvider" not in tz and tz["Death"] == {"ItemsLossMode": "None"}
                  and tz["Plugin"] == {"Instance": {"RemovalConditions": []}} and tz["DeleteOnUniverseStart"] is False, "JT: the 0.7 world template - "
                  "SkyWynnZones2, seed %d (= 0.6's), vanilla spawn, deaths keep items, kept forever: %s" % (ZSEED, {k: tz[k] for k in ("WorldGen", "Seed", "Death")}))
            t6 = json.loads(zj.read("Server/Instances/SkyWynn_Zones/instance.bson"))
            check(t6["WorldGen"] == {"Type": "SkyWynnZones"}, "JT: the 0.6 world template is kept (type SkyWynnZones): %s" % t6["WorldGen"])
            # ---- A + MK + Z + ST
            out_e = os.path.join(SCRATCH, "e.json")
            with open(out_e + ".log", "wb") as lf:
                subprocess.run([sys.executable, me, "--e", "--out", out_e, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                               env=env, stdout=lf, stderr=subprocess.STDOUT)
            r = json.load(open(out_e)) if os.path.isfile(out_e) else None
            if r is None or "error" in r:
                print(open(out_e + ".log", encoding="utf8", errors="replace").read()[-3000:])
            check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-3000:])
            if r:
                for tag, (n_, f_) in r["load"].items():
                    check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise on 0.7 %s" % (tag, n_, f_[:3]))
            if r and "error" not in r:
                check_e(r["E"])
            if os.path.isfile(os.path.join(SCRATCH, "mk_shape.png")):
                shutil.copyfile(os.path.join(SCRATCH, "mk_shape.png"), os.path.join(os.path.dirname(SCRATCH), "mk_shape_last.png"))
        # ---- VP
        try:
            vp()
        except Exception as e:
            check(False, "VP crashed: %s" % e)
        if not only_vp:
            # ---- AA
            out_aa = os.path.join(SCRATCH, "aa.log")
            with open(out_aa, "wb") as lf:
                subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                               stderr=subprocess.STDOUT, cwd=ROOT)
            aa = open(out_aa, encoding="utf8", errors="replace").read()
            mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyWorldGen " in ln]
            check("access:" in aa and not mine, "AA: crosscheck --jar 0.7: no FAIL for SkyyWorldGen on 0.7: %s" % mine[:3])
            bl = [ln for ln in aa.splitlines() if "baseline SkyyWorldGen" in ln]
            print("AA. %s" % bl[:3])
            check(any("command / permission tree identical" in ln for ln in bl), "AA: the command / permission tree = 0.6's: %s" % bl[:3])
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        check(not chg, "the live Skyy_SkyyWorldGen folder is unchanged: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    for n_ in NOTES:
        print("NOTE:", n_)
    print("SkyyWorldGen %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
