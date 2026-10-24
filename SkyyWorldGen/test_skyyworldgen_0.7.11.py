"""Harness for SkyyWorldGen 0.7.11 (round wg0711: structures over the void - black grass, zone match, spacing, height, floating islands;
tools/worldgen_0_7_11_patch.py). Build first:
    python tools/worldgen_0_7_11_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.11.py

    python SkyyWorldGen/test_skyyworldgen_0.7.11.py [--keep] [--server]   (--server = the S phase; main session only)

Phases (fresh child JVMs, tools/harness_kit.py; scratch tools/dev/scratch/wg0711/h):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.10 -> 0.7.11: the planned members only (+ the 10 void classes)
  T    tint     ROOT CAUSE on a scratch COPY of NewBetaTest's skywynn_zones2 chunks: the stored void-structure chunks (tavern_house 288 -422,
               Big_Tower_Goblin 609 -124) have ONE tint = 0 (black); land chunks are green with alpha 0xFF. 0.7.10's void chunk
               (WgIsle.emptyChunk) = tint 0 in all 1024 columns; 0.7.11's WgZ2Void never 0; WgVTint.blur = vanilla's radius-4 mean,
               alpha 0xFF; the heal (toChunk) changes ONLY the black columns, a second run changes nothing (run once per chunk)
  V    void     the StructureV2 filter on the REAL live layout (scratch copy): land = vanilla's answer, another zone's class refused,
               switched off refused, the spawn disk (28 % of a square, never closer than 0.4 x spacing), one structure per square (from
               StructureV2's own record), one lift per square in -30..+60 (capped at y 150); today's record (75 rows, a copy taken
               before the reset) -> how many void structures the new rules keep; the dresser's record parse / next / podloze merge /
               keys / done file (write, read back, never twice)
  J    islet    WgVJob on a stand-in world (a javassist WgVAcc): a StructureV2-style square soil slab + a house over the void ->
               a ROUND island (bbox fill + axis / diagonal reach), grass top, dirt under the slab, rock at the bottom, a tapered
               underside (deep in the middle, thin at the rim), trees >= 5 blocks off the slab on grass, a plant without a slab
               under it stands on living soil (grass; desert = DIRT), only air ever filled, foreign land next to it untouched; a
               floating structure / chunks not loaded / a too-big box are left alone
  L    live     START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen: WgCfg.load, WgStore.read, WgRZ.boot, WgVIsle.load - no file
               changed; the void rows run on their defaults; a config with the rows set reads them (clamped)
  S    server   (game closed only; tools/smoke_test.py, offline, a scratch COPY of NewBetaTest; a test probe plugin): the heal on a real
               chunk load (a stored black void chunk loads with no black column), a NEW void chunk generated with vanilla's grass
               colour, the filter seen from a StructureV2-package caller on the world thread (land unchanged, another zone's point
               refused, an allowed void point lifted by its square's lift), the 5 s dresser ran + read StructureV2's record, and a
               REAL floating island under the real tavern_house over the void (blocks placed, trees, only air filled, soil under it,
               the done file written)
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, time, zipfile, shutil, json, subprocess, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.11"
OLD_VERSION = "0.7.10"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg0711", "h")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
SAVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest")
LIVE_WG = os.path.join(SAVE, "mods", "Skyy_SkyyWorldGen")
ZW = "skywynn_zones2"
WSEED = 20261014
# StructureV2's record as it was on 2026-10-24 10:29 (75 rows; the live file is empty since the Zone 1 reset + undo) - a scratch copy
# made by the first builder of this round (round wglight), read only here
OLD_SPAWNS = os.path.join(ROOT, "tools", "dev", "scratch", "wglight", "lay", "structurev2-spawns.json")
ADDED = ["WgVoid", "WgVTint", "WgZ2Void", "WgVHeal", "WgVAcc", "WgVAccW", "WgVJob", "WgVRun", "WgVPoll", "WgVIsle"]
EXPECT = {
    "WgZ2Gen": ["+m generateHeightBetween", "+m getHeight", "+m getZoneBiomeResultAt", "+m voidChunk", "~m generateWith"],
    "WgZoneGen": ["+m voidChunk", "~m generate"], "WgIsleGen": ["+m voidChunk", "~m generate"],
    "WgCfg": ["~m apply", "~m load", "~m reloadAll"], "WgZSeed": ["~m save"], "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "SkyyWorldGenPlugin": ["~m setup", "~m shutdown", "~m start"], "WgStore": ["~m markCreated"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            ok = "manifest.json" in got and all(n in ("manifest.json", LANG) or n.endswith("/instance.bson") for n in got)
            if ok and LANG in got:
                a = zipfile.ZipFile(OLD_JAR).read(LANG).decode("utf8").splitlines()
                b = zipfile.ZipFile(HK.arg("--jar", JAR)).read(LANG).decode("utf8").splitlines()
                ok = len(a) == len(b) and [i for i in range(len(a)) if a[i] != b[i]] == [0] and a[0].replace(OLD_VERSION, VERSION) == b[0]
            return self.check(ok, "C: non-class entries changed = manifest.json + instance templates + server.lang header (version text only): %s" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def unsafe():
    from jpype import JClass
    fu = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    return fu.get(None)


def u32(v):
    return int(v) & 0xFFFFFFFF


# ------------------------------------------------------------------------------------------- T: the tint (root cause + fix)
def run_tint(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass, JArray, JInt, JLong
    J = lambda n: JClass(PKG + n)
    Vt, Vd, Isle, Z2V, Z2G = J("WgVTint"), J("WgVoid"), J("WgIsle"), J("WgZ2Void"), J("WgZ2Gen")
    CU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
    BC = JClass("com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk")
    fb = int(Vd.FALLBACK)
    K.check(fb != 0 and u32(fb) >> 24 == 0xFF, "T the fallback tint is opaque, never 0 (0x%08X)" % u32(fb))
    # ---- the stored chunks (a scratch COPY; the live world is only read by the copy)
    src = os.path.join(SAVE, "universe", "worlds", ZW, "chunks")
    cdir = os.path.join(scratch, "tchunks")
    want = set()
    for (bx, bz) in ((288, -422), (609, -124), (-300, 100), (-100, 300)):
        want.add("%d.%d.region.bin" % ((bx >> 5) >> 5, (bz >> 5) >> 5))
    os.makedirs(cdir)
    for n in sorted(want):
        if os.path.isfile(os.path.join(src, n)):
            shutil.copyfile(os.path.join(src, n), os.path.join(cdir, n))
    Paths = JClass("java.nio.file.Paths")
    st = J("WgRStore")(None, None, Paths.get(cdir))
    BU = JClass("com.hypixel.hytale.server.core.util.BsonUtil")
    BB = JClass("java.nio.ByteBuffer")
    IBP = JClass("com.hypixel.hytale.server.core.universe.world.chunk.palette.IntBytePalette")
    MS = JClass("java.lang.foreign.MemorySegment")

    def tints(bx, bz):
        b = st.read(JLong(int(CU.indexChunk(bx >> 5, bz >> 5))))
        if b is None:
            return None
        d = BU.readFromBuffer(BB.wrap(b))
        data = d.get("Components").asDocument().get("BlockChunk").asDocument().get("Data").asBinary().getData()
        last = None
        for off in (1, 0, 2):
            try:
                p = IBP()
                p.deserialize(MS.ofArray(data), off)
                return set(u32(p.get(i, j)) for i in range(32) for j in range(32))
            except Exception as e:
                last = e
        return "unreadable: %s" % last
    for name, bx, bz in (("tavern_house (void)", 288, -422), ("Big_Tower_Goblin (void)", 609, -124)):
        t = tints(bx, bz)
        if t is None:
            K.notes.append("T %s: chunk not stored in the live world (not visited) - root-cause proof skipped" % name)
            continue
        K.check(t == {0}, "T ROOT CAUSE: the stored chunk of the %s structure has ONE tint for all 1024 columns = 0 (black grass): %s" % (name, sorted(t)[:4] if isinstance(t, set) else t))
    for name, bx, bz in (("land A", -300, 100), ("land B", -100, 300)):
        t = tints(bx, bz)
        if t is None:
            continue
        K.check(isinstance(t, set) and len(t) > 1 and all(v >> 24 == 0xFF for v in t), "T a Zone 1 land chunk (%s) has many opaque grass tints (alpha 0xFF): %d keys" % (name, len(t) if isinstance(t, set) else -1))
    st.close()
    # ---- 0.7.10's void chunk: tint 0 everywhere; 0.7.11's WgZ2Void: never 0
    gc = Isle.emptyChunk(JLong(int(CU.indexChunk(40, 40))), 40, 40)
    z0 = sum(1 for x in range(32) for z in range(32) if int(gc.getBlockChunk().getTint(x, z)) == 0)
    K.eq(z0, 1024, "T 0.7.10's void chunk (WgIsle.emptyChunk, kept as is) starts every column at tint 0 = the black grass")
    U = unsafe()
    g = U.allocateInstance(Z2G.class_)          # no vanilla worldgen in a bare JVM: the biome look-up fails -> the fallback green
    c2 = Z2V(g, WSEED, JLong(int(CU.indexChunk(40, 40))), 40, 40).get()
    vals = set(u32(c2.getBlockChunk().getTint(x, z)) for x in range(32) for z in range(32))
    K.check(0 not in vals and all(v >> 24 == 0xFF for v in vals), "T 0.7.11's void chunk (WgZ2Void) has no tint-0 column, all opaque: %s" % ["%08X" % v for v in sorted(vals)[:3]])
    K.check(int(Vd.NEWT.get()) == 1, "T the new-void-chunk counter counts it")
    for gn in ("WgZoneGen", "WgIsleGen"):     # review fix 6: skywynn_zones + skywynn_proof2 void chunks are tinted too
        go = U.allocateInstance(J(gn).class_)
        try:
            c3 = go.voidChunk(WSEED, JLong(int(CU.indexChunk(41, 40))), 41, 40).get()
            v3 = set(u32(c3.getBlockChunk().getTint(x, z)) for x in range(32) for z in range(32))
            K.check(0 not in v3 and all(v >> 24 == 0xFF for v in v3), "T %s.voidChunk has no tint-0 column (fix 6)" % gn)
        except Exception as e:
            K.check(False, "T %s.voidChunk: %s" % (gn, e))
    # ---- the blur: vanilla's radius-4 mean, alpha 0xFF
    raw = JArray(JInt)([0x336699] * 1600)
    o = JArray(JInt)(1024)
    Vt.blur(raw, o)
    K.check(all(u32(o[i]) == 0xFF336699 for i in range(1024)), "T blur of a flat colour = that colour with alpha 0xFF")
    r2 = [(0xFF0000 if i < 20 else 0x0000FF) for i in range(40) for k in range(40)]
    Vt.blur(JArray(JInt)(r2), o)
    mid = u32(o[(20 - 4) * 32 + 10])
    K.check(((mid >> 16) & 255) > 0 and (mid & 255) > 0 and u32(o[0]) == 0xFFFF0000 and u32(o[31 * 32]) == 0xFF0000FF,
            "T blur mixes across a colour edge (mid %08X) and keeps the far sides pure" % mid)
    # ---- the heal on a BlockChunk: only black columns change, a second pass changes nothing
    bc = BC(5, 7)
    K.check(bool(Vt.blackish(bc)) and int(Vt.zeros(bc)) == 1024, "T a never-tinted BlockChunk is blackish (1024 zero columns)")
    bc.setTint(3, 4, JInt(-16711936))     # one column already green (0xFF00FF00)
    t = JArray(JInt)([int(fb)] * 1024)
    n1 = int(Vt.toChunk(bc, t))
    K.eq(n1, 1023, "T the heal changes ONLY the 1023 black columns")
    K.check(u32(bc.getTint(3, 4)) == 0xFF00FF00 and u32(bc.getTint(0, 0)) == u32(fb), "T the coloured column is kept exactly; a black one gets the tint")
    n2 = int(Vt.toChunk(bc, t))
    K.check(n2 == 0 and not bool(Vt.blackish(bc)) and int(Vt.zeros(bc)) == 0, "T a second heal changes nothing (the tint is its own run-once marker)")
    K.save()


# ------------------------------------------------------------------------------------------- V: the filter + the dresser's record
def live_layout(scratch):
    """a scratch copy of the live layout files -> (dir)"""
    d = os.path.join(scratch, "vlay")
    os.makedirs(d)
    for n in os.listdir(LIVE_WG):
        if n.startswith("zone2_") and os.path.isfile(os.path.join(LIVE_WG, n)):
            shutil.copyfile(os.path.join(LIVE_WG, n), os.path.join(d, n))
    return d


def run_void(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass, JArray, JDouble, JInt
    J = lambda n: JClass(PKG + n)
    Vd, Isl, Sd, RZ, Vi = J("WgVoid"), J("WgZ2Isles"), J("WgZSeed"), J("WgRZ"), J("WgVIsle")
    Paths = JClass("java.nio.file.Paths")
    d = live_layout(scratch)
    Isl.LAYDIR = Paths.get(d)
    Sd.load(Isl.SEED)
    L = RZ.bootLayout()
    K.check(L is not None and not bool(L.failed), "V the live layout loads from its scratch copy (zones gen %s)" % Sd.sig())
    if L is None:
        K.save()
        return
    m = JArray(JDouble)(1)
    member = lambda x, z: int(Isl.member(L, float(x) + 0.5, float(z) + 0.5, m))
    owner = lambda x, z: int(Isl.ownerOf(L, x >> 5, z >> 5))
    lx, lz = int(math.floor(L.lx[0])), int(math.floor(L.lz[0]))
    K.check(member(lx, lz) >= 0, "V the Zone 1 landing is land")
    S = int(Vd.SPACING)
    K.check(S == 500 and int(Vd.LIFT_MIN) == -30 and int(Vd.LIFT_MAX) == 60 and abs(float(Vd.DISK) - 0.3) < 1e-9,
            "V defaults: spacing 500 (today's median 219), lift -30..+60, disk 0.3")
    K.eq(int(Vd.verdict(L, lx, lz, 3, False)), 0, "V a land point = 0 (vanilla's answer, whatever its class)")
    # void points owned by Zone 1 (a ring 150-700 blocks off the coast)
    cx0, cz0 = float(L.cx[0]), float(L.cz[0])
    pts = []
    for a in range(0, 360, 3):
        for r in range(900, 2200, 24):
            x = int(cx0 + r * math.cos(math.radians(a)))
            z = int(cz0 + r * math.sin(math.radians(a)))
            if member(x, z) < 0 and owner(x, z) == 0:
                pts.append((x, z))
    K.check(len(pts) > 200, "V void points owned by Zone 1 found: %d" % len(pts))
    zc = int(Isl.Z_CLS[0])
    other = 2 if zc != 2 else 3
    ind = [p for p in pts if bool(Vd.inDisk(p[0], p[1], S))]
    vs = [int(Vd.verdict(L, x, z, other, False)) for (x, z) in pts]
    K.check(all(v == 3 for v in vs), "V every Zone 1 void point refuses another zone's class (%d) = 3 (no Zone 2 desert off Zone 1): %s" % (other, sorted(set(vs))))
    vs2 = [int(Vd.verdict(L, x, z, zc, True)) for (x, z) in pts]
    K.check(all(v == 1 for v in vs2), "V StructureV2's chunk pre-filter (pre) with the zone's own class: allowed everywhere (zone test only)")
    vs3 = [int(Vd.verdict(L, x, z, zc, False)) for (x, z) in pts]
    ld = dict(((x, z), float(Vd.landDist(L, x, z))) for (x, z) in pts)
    near = [p for p in pts if ld[p] < 60.0]
    K.check(all((v == 1) == (bool(Vd.inDisk(x, z, S)) and ld[(x, z)] >= 60.0) for v, (x, z) in zip(vs3, pts)) and set(vs3) <= {1, 4},
            "V the zone's own class: allowed exactly inside the square's disk AND 60+ blocks off land, else 4 (%d of %d in a disk, %d near land)" % (len(ind), len(pts), len(near)))
    K.check(len(near) > 0 and all(int(Vd.verdict(L, x, z, zc, False)) == 4 for (x, z) in near), "V review fix 1: no void anchor within 60 blocks of land")
    K.check(all(0.0 < ld[p] < 1.0e8 for p in pts), "V landDist over the void is > 0 (land = 0): %.0f..%.0f" % (min(ld.values()), max(ld.values())))
    K.check(int(Vd.verdict(L, pts[0][0], pts[0][1], 0, False)) in (1, 4), "V no vanilla zone (class 0) is never refused for its zone")
    Vd.ON = False
    K.check(all(int(Vd.verdict(L, x, z, zc, False)) == 2 for (x, z) in pts[:50]) and int(Vd.verdict(L, lx, lz, zc, False)) == 0,
            "V switched off: every void point = 2, land still 0")
    Vd.ON = True
    Vd.MATCH = False
    K.check(all(int(Vd.verdict(L, x, z, other, True)) == 1 for (x, z) in pts[:50]), "V zone match off: another zone's class is allowed")
    Vd.MATCH = True
    # the disk: 28 % of the square, the square's middle in, its corners out, never closer than 0.4 x spacing across squares
    import random
    rnd = random.Random(7)
    smp = [(rnd.randint(-40000, 40000), rnd.randint(-40000, 40000)) for _ in range(20000)]
    frac = sum(1 for (x, z) in smp if bool(Vd.inDisk(x, z, S))) / float(len(smp))
    K.check(abs(frac - math.pi * 0.09) < 0.02, "V the disk covers %.3f of each square (pi x 0.3^2 = 0.283)" % frac)
    K.check(bool(Vd.inDisk(250, 250, S)) and not bool(Vd.inDisk(0, 0, S)) and not bool(Vd.inDisk(499, 10, S)), "V the square's middle is in, its corner / edge out")
    K.check(abs(2 * (0.5 - 0.3) * S - 200) < 1e-6, "V two disks of neighbouring squares are >= 0.4 x 500 = 200 blocks apart")
    # one lift per square, in range, capped
    lifts = [int(Vd.liftOf(rnd.randint(-40000, 40000), rnd.randint(-40000, 40000))) for _ in range(4000)]
    K.check(min(lifts) == -30 and max(lifts) == 60 and len(set(lifts)) > 60, "V lifts spread over -30..+60 (%d values, %d..%d)" % (len(set(lifts)), min(lifts), max(lifts)))
    K.check(all(int(Vd.liftOf(1000 + i, 1000 + 3 * i)) == int(Vd.liftOf(1000, 1000)) for i in range(0, 499 - 3 * 0, 7) if 1000 + 3 * i < 1500),
            "V one lift for a whole square (a structure moves together)")
    farp = [p for p in pts if ld[p] >= 60.0 and int(Vd.liftOf(p[0], p[1])) != 0]
    x, z = farp[0]
    off = int(Vd.liftOf(x, z))
    K.eq(int(Vd.lift(L, x, z, 110)), max(1, (min(110 + off, max(110, 150)) if off > 0 else 110 + off)), "V a void height 60+ off land gets its square's full lift (%+d)" % off)
    # review fix 1: the ramp - a walk from the coast outward never steps more than a few blocks per block walked
    big = [p for p in pts if abs(int(Vd.liftOf(p[0], p[1]))) >= 30 and 0.0 < ld[p] < 12.0]
    if big:
        bx, bz = big[0]
        o2 = int(Vd.liftOf(bx, bz))
        h2 = int(Vd.lift(L, bx, bz, 100)) - 100
        K.check(abs(h2) <= abs(o2) * 0.12 + 1, "V the lift ramps in from the coast: %.0f blocks off land the lift is %+d of %+d" % (ld[(bx, bz)], h2, o2))
    half = [p for p in pts if 28.0 <= ld[p] <= 32.0 and abs(int(Vd.liftOf(p[0], p[1]))) >= 20]
    if half:
        hx, hz = half[0]
        o3 = int(Vd.liftOf(hx, hz))
        h3 = int(Vd.lift(L, hx, hz, 100)) - 100
        K.check(abs(h3 - o3 * 0.5) <= abs(o3) * 0.12 + 1, "V half way up the ramp (%.0f blocks) about half the lift: %+d of %+d" % (ld[(hx, hz)], h3, o3))
    K.eq(int(Vd.lift(L, lx, lz, 110)), 110, "V a land height is never lifted")
    hi = [p for p in pts if int(Vd.liftOf(p[0], p[1])) > 30]
    if hi:
        K.eq(int(Vd.lift(L, hi[0][0], hi[0][1], 140)), 150, "V a lift never takes the anchor above y 150")
    # ---- review fix 2: the caller CLASS (StackWalker) instead of a stack trace per call - two stand-in StructureV2 classes
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(B.SERVER_JAR)
    cp.insertClassPath(JAR)
    CtM = JClass("javassist.CtNewMethod")
    lp = cp.makeClass("com.joszza.structurev2.zzt.Loop")
    lp.addMethod(CtM.make("public static Class inner() { return com.skyy.worldgen.WgVoid.SW.getCallerClass(); }", lp))
    lp.addMethod(CtM.make("""public static long timeSW(int n) {
  long t0 = System.nanoTime();
  int ok = 0;
  for (int i = 0; i < n; i++) if (com.skyy.worldgen.WgVoid.who(inner()) == 1) ok++;
  return ok == n ? System.nanoTime() - t0 : -1L;
}""", lp))
    lp.addMethod(CtM.make("""public static long timeST(int n) {
  long t0 = System.nanoTime();
  int ok = 0;
  for (int i = 0; i < n; i++) if (com.skyy.worldgen.WgVoid.sv2() == 1) ok++;
  return ok == n ? System.nanoTime() - t0 : -1L;
}""", lp))
    lp.addMethod(CtM.make("""public static long deep(int d, int n, boolean sw) {
  if (d > 0) return deep(d - 1, n, sw);
  return sw ? timeSW(n) : timeST(n);
}""", lp))
    tcd = os.path.join(scratch, "tcls")
    lp.writeFile(tcd)
    cl = cp.makeClass("com.joszza.structurev2.zzt.ChunkPlacementListener")
    cl.addMethod(CtM.make("public static int entryCouldApplyNearChunk() { return com.skyy.worldgen.WgVoid.whoZ(Class.forName(\"com.joszza.structurev2.zzt.ChunkPlacementListener\")); }", cl))
    cl.addMethod(CtM.make("public static int considerPoint() { return com.skyy.worldgen.WgVoid.whoZ(Class.forName(\"com.joszza.structurev2.zzt.ChunkPlacementListener\")); }", cl))
    cl.writeFile(tcd)
    URL = JClass("java.net.URL")
    ucl = JClass("java.net.URLClassLoader")(JArray(URL)([JClass("java.io.File")(tcd).toURI().toURL()]), JClass(PKG + "WgVoid").class_.getClassLoader())
    Loop = JClass(ucl.loadClass("com.joszza.structurev2.zzt.Loop"))
    CPL = JClass(ucl.loadClass("com.joszza.structurev2.zzt.ChunkPlacementListener"))
    n = 20000
    Loop.timeSW(2000)
    Loop.timeST(2000)
    # the world thread calls StructureV2 ~60 frames deep (tick -> drain -> place -> considerPoint / TerrainSuitability): same depth here
    tsw = int(Loop.deep(60, n, True))
    tst = int(Loop.deep(60, n, False))
    K.check(tsw > 0 and tst > 0, "V the caller class of a com.joszza.structurev2.* caller is recognised (both ways)")
    K.check(tsw * 5 < tst and tsw / 1e3 / n < 5.0, "V review fix 2 TIMING (60 frames deep): %d calls - caller class %.2f ms (%.2f us each) vs stack trace %.2f ms (%.2f us each) = %.0fx faster"
            % (n, tsw / 1e6, tsw / 1e3 / n, tst / 1e6, tst / 1e3 / n, tst / max(1.0, tsw)))
    K.notes.append("caller-class check %.2f us vs stack trace %.2f us per call" % (tsw / 1e3 / n, tst / 1e3 / n))
    K.check(int(Vd.who(JClass(PKG + "WgVoid").class_)) == 0 and int(Vd.who(None)) == 0, "V our own / no caller class = not StructureV2")
    K.check(int(CPL.entryCouldApplyNearChunk()) == 2 and int(CPL.considerPoint()) == 1, "V ChunkPlacementListener: its chunk pre-filter = 2, considerPoint = 1")
    # ---- StructureV2's record (today's copy, 75 rows): rows, the taken squares, what the new rules keep
    if not os.path.isfile(OLD_SPAWNS):
        K.notes.append("V no copy of the 2026-10-24 StructureV2 record - record checks on a minimal file only")
        txt = json.dumps({"version": 1, "spawns": []})
    else:
        txt = open(OLD_SPAWNS, encoding="utf8").read()
    rows = json.loads(txt)["spawns"]
    n = int(Vi.parse(txt, ZW, L))
    K.eq(n, len(rows), "V parse reads every row of StructureV2's record")
    voidr = [r for r in rows if member(r["x"], r["z"]) < 0]
    skip = [str(s) for s in Vi.SKIP]
    dress = [r for r in voidr if not any(s in r["prefabName"] for s in skip)]
    notc = [str(s) for s in Vi.NOTC]
    counted = [r for r in voidr if not any(s in r["prefabName"] for s in notc)]
    sq = set(((r["x"] // S), (r["z"] // S)) for r in counted)
    K.eq(int(Vd.OCC.size()), len(sq), "V the taken squares = one per square with a void structure (podloze / bridges not counted)")
    if counted:
        r0 = counted[0]
        K.check(not bool(Vd.occupied(r0["x"], r0["z"], S)) and not bool(Vd.occupied(r0["x"] + 5, r0["z"] - 3, S)),
                "V a structure's own point (its multi-chunk paste asks again) is not 'taken'")
        sx, sz = (r0["x"] // S) * S, (r0["z"] // S) * S
        far = [(sx + a, sz + b) for a in range(0, S, 37) for b in range(0, S, 41) if abs(sx + a - r0["x"]) > 8 or abs(sz + b - r0["z"]) > 8]
        K.check(all(bool(Vd.occupied(px, pz, S)) for (px, pz) in far[:40]), "V any other point of that square is taken (5 = one per square)")

    def nn(lst):
        ds = []
        for a in lst:
            b = min((math.hypot(a[0] - c[0], a[1] - c[1]) for c in lst if c is not a), default=None)
            if b is not None:
                ds.append(b)
        ds.sort()
        return (ds[len(ds) // 2], ds[0]) if ds else (0, 0)
    cv = [(r["x"], r["z"]) for r in counted]
    kept, used = [], set()
    for (x, z) in cv:
        if bool(Vd.inDisk(x, z, S)) and float(Vd.landDist(L, x, z)) >= 60.0 and (x // S, z // S) not in used:
            used.add((x // S, z // S))
            kept.append((x, z))
    md0, mn0 = nn(cv)
    md1, mn1 = nn(kept)
    K.check(len(cv) == 0 or (mn1 >= 0.4 * S - 1 and md1 > 2 * md0 * 0.9) or len(kept) < 3,
            "V today's %d void structures (nearest neighbour median %.0f, closest %.0f) -> under the new rules at most %d kept (median %.0f, closest %.0f)"
            % (len(cv), md0, mn0, len(kept), md1, mn1))
    K.notes.append("today's void structures %d (median %.0f closest %.0f) -> new rules %d (median %.0f closest %.0f)" % (len(cv), md0, mn0, len(kept), md1, mn1))
    # ---- the dresser: next / merge / key / done file
    dd = os.path.join(scratch, "vdone")
    os.makedirs(dd)
    Vi.DONE.clear()
    Vi.load(Paths.get(dd))
    K.check(Vi.DONE.size() == 0 and str(Vi.FILE).endswith("void-islets.properties"), "V no done file yet = nothing done")
    p = Vi.next(L)
    if dress:
        K.check(p is not None, "V next() picks a void structure to dress")
    if p is not None:
        key, pf, v, k = str(p[0]), str(p[1]), [int(a) for a in p[2]], int(p[3])
        K.check(not any(s in pf for s in skip) and member(v[0], v[2]) < 0 and k == owner(v[0], v[2]),
                "V ... over the void, not a flying island / ship / sub-piece, its owner zone %d: %s" % (k + 1, key))
        K.check(re.match(r"^z%dg%d\|%s\|-?\d+,-?\d+,-?\d+$" % (k + 1, int(Sd.GEN[k]), re.escape(pf)), key) is not None, "V the key names zone + reset gen: %s" % key)
        src = [r for r in rows if r["prefabName"] == pf and r["x"] == v[0] and r["z"] == v[2]][0]
        pod = [r for r in rows if "podloze" in r["prefabName"] and abs(r["x"] - v[0]) <= 48 and abs(r["z"] - v[2]) <= 48]
        want = [min([src["minX"]] + [r["minX"] for r in pod]), max([src["maxX"]] + [r["maxX"] for r in pod])]
        K.check(v[3] == want[0] and v[6] == want[1], "V its box joins its podloze slab(s) (%d): x %d..%d (structure alone %d..%d)" % (len(pod), v[3], v[6], src["minX"], src["maxX"]))
        Vi.record(key, "1|10|1|ok")
        K.check(os.path.isfile(os.path.join(dd, "void-islets.properties")), "V record() writes the done file")
        p2 = Vi.next(L)
        K.check(p2 is None or str(p2[0]) != key, "V a done structure is never picked again")
        Vi.DONE.clear()
        Vi.load(Paths.get(dd))
        K.check(str(Vi.DONE.get(key)) == "1|10|1|ok", "V the done file reads back after a restart")
        p3 = Vi.next(L)
        K.check(p3 is None or str(p3[0]) != key, "V ... and the structure stays done after the restart")
        txt2 = open(os.path.join(dd, "void-islets.properties"), encoding="utf8").read()
        K.check(txt2.startswith("# SkyyWorldGen 0.7.11") and txt2.count(key) == 1, "V the done file has its header + one line")
        j = Vi.job(None, L, p, None)
        K.check(int(j.cls) == int(Isl.Z_CLS[k]) and int(j.maxTrees) == 6, "V job(): no generator = the owner zone's class %d, 6 trees" % int(j.cls))
    # a fresh structure (younger than 20 s) waits for StructureV2's paste to finish
    if dress:
        r = dict(dress[0])
        r["timestampMs"] = int(time.time() * 1000)
        Vi.DONE.clear()
        Vi.parse(json.dumps({"spawns": [r]}), ZW, L)
        K.check(Vi.next(L) is None, "V a structure recorded under 20 s ago is not dressed yet")
        r["worldName"] = "other_world"
        r["timestampMs"] = 1
        Vi.parse(json.dumps({"spawns": [r]}), ZW, L)
        K.check(Vi.ROWS.size() == 0, "V another world's rows are ignored")
    K.save()


# ------------------------------------------------------------------------------------------- J: the islet builder on a stand-in world
FAKE = {
    "get": """public int get(int x, int y, int z) {
  if (y < 0) return 0 - 1;
  Object o = this.m.get(Long.valueOf(k(x, y, z)));
  return o == null ? 0 : ((Integer) o).intValue();
}""",
    "put": """public boolean put(int x, int y, int z, int id, int rot) {
  if (get(x, y, z) != 0) this.over++;
  this.m.put(Long.valueOf(k(x, y, z)), Integer.valueOf(id));
  this.puts++;
  return true;
}""",
    "k": """public static long k(int x, int y, int z) { return ((((long) x) & 2097151L) << 42) | ((((long) y) & 2097151L) << 21) | (((long) z) & 2097151L); }""",
    "loaded": "public boolean loaded(int cx, int cz) { return this.load; }",
    "idOf": """public int idOf(String n) {
  Object o = this.ids.get(n);
  if (o != null) return ((Integer) o).intValue();
  int i = this.names.size();
  this.names.add(n);
  this.ids.put(n, Integer.valueOf(i));
  return i;
}""",
    "tint": "public void tintChunk(int cx, int cz) { this.tints++; }",
    "relight": "public void relight(int cx, int cz) { this.relights++; }",
    "fill": """public void fill(int x0, int x1, int y0, int y1, int z0, int z1, String n) {
  int id = idOf(n);
  for (int x = x0; x <= x1; x++) for (int y = y0; y <= y1; y++) for (int z = z0; z <= z1; z++) {
    if (id == 0) this.m.remove(Long.valueOf(k(x, y, z))); else this.m.put(Long.valueOf(k(x, y, z)), Integer.valueOf(id));
  }
}""",
    "snap": """public void snap() {
  int n = this.m.size();
  this.sk = new long[n];
  this.sv = new int[n];
  java.util.Iterator it = this.m.keySet().iterator();
  int i = 0;
  while (it.hasNext()) { Long kk = (Long) it.next(); this.sk[i] = kk.longValue(); this.sv[i] = ((Integer) this.m.get(kk)).intValue(); i++; }
}""",
    "nm": "public String nm(int id) { return id < 0 || id >= this.names.size() ? \"?\" : (String) this.names.get(id); }",
}


def fake_class():
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(B.SERVER_JAR)
    cp.insertClassPath(JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fa = cp.makeClass(PKG + "WgTFake", cp.get(PKG + "WgVAcc"))
    for f in ("public java.util.HashMap m = new java.util.HashMap();", "public java.util.HashMap ids = new java.util.HashMap();",
              "public java.util.ArrayList names = new java.util.ArrayList();", "public boolean load = true;", "public int puts = 0;",
              "public int over = 0;", "public int tints = 0;", "public int relights = 0;", "public long[] sk;", "public int[] sv;"):
        fa.addField(CtF.make(f, fa))
    fa.addConstructor(CtC.make("public WgTFake() { super(); this.names.add(\"Empty\"); this.ids.put(\"Empty\", Integer.valueOf(0)); }", fa))
    for k in ("k", "get", "put", "loaded", "idOf", "tint", "relight", "fill", "snap", "nm"):
        fa.addMethod(CtM.make(FAKE[k], fa))
    return JClass(fa.toClass(JClass(PKG + "WgVAcc").class_))


def dec(kk):
    def s21(v):
        return v - (1 << 21) if v >= (1 << 20) else v
    return s21((kk >> 42) & 0x1FFFFF), s21((kk >> 21) & 0x1FFFFF), s21(kk & 0x1FFFFF)


def blocks(f):
    f.snap()
    return dict((dec(int(a)), int(b)) for a, b in zip(f.sk, f.sv))


def run_islet(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass, JArray, JInt
    Job, Vi = JClass(PKG + "WgVJob"), JClass(PKG + "WgVIsle")
    Fake = fake_class()
    for c in (1, 2, 3, 4):
        t = [str(x) for x in Vi.treesOf(c)]
        K.check(len(t) >= 2 and all("|" in x for x in t), "J zone class %d: %d vanilla tree shapes baked in the jar" % (c, len(t)))

    def scene(cls, plant_hole=True, foreign=True):
        f = Fake()
        f.fill(0, 29, 99, 99, 0, 29, "Soil_Dirt")          # StructureV2's square soil slab (podloze): 30 x 30, 2 thick
        f.fill(0, 29, 100, 100, 0, 29, "Soil_Grass")
        f.fill(8, 19, 101, 108, 8, 19, "Wood_Oak_Planks")  # the house
        if plant_hole:
            f.fill(4, 4, 99, 100, 4, 4, "Empty")           # a hole in the slab with a plant standing in it
            f.fill(4, 4, 100, 100, 4, 4, "Plant_Grass_Lush")
        if foreign:
            f.fill(-14, -11, 95, 100, 10, 14, "Rock_Stone")   # other land next to it (inside the scanned box, outside the structure)
        return f
    v = JArray(JInt)([15, 100, 15, 0, 99, 0, 29, 108, 29])

    def run(f, cls, vv=v, trees=6):
        j = Job(f, "z1g0|Structure.test|15,100,15", "Structure.test", vv, cls, trees)
        n = 0
        while not bool(j.step()):
            n += 1
            if n > 200000:
                break
        return j, n
    # ---- A: Zone 1 (grass)
    f = scene(1)
    b0 = blocks(f)
    j, steps = run(f, 1)
    b1 = blocks(f)
    nm = lambda i: str(f.nm(i))
    K.check(int(j.state) == 6 and str(j.why) == "" and int(j.placed) > 500, "J A finished: %d blocks, %d tree(s), %d slices, about %d across, %d deep (%s)" % (int(j.placed), int(j.trees), steps, round(float(j.rout) * 2), round(float(j.depth)), j.why))
    K.check(int(f.over) == 0 and all(b1.get(p) == i for p, i in b0.items()), "J A only AIR was filled: every block that was there is unchanged (%d puts, %d over a block)" % (int(f.puts), int(f.over)))
    new = dict((p, i) for p, i in b1.items() if p not in b0)
    cols = {}
    for (x, y, z), i in new.items():
        c = cols.setdefault((x, z), [y, y, i, i])
        if y > c[0]:
            c[0], c[2] = y, i
        if y < c[1]:
            c[1], c[3] = y, i
    T = int(j.T)
    K.eq(T, 100, "J A the structure's ground T = the slab's top (median near the anchor)")
    slab = lambda x, z: 0 <= x <= 29 and 0 <= z <= 29
    ring = [(x, z) for (x, z) in cols if not slab(x, z) and cols[(x, z)][0] >= T - 2 and cols[(x, z)][0] <= T + 2]
    K.check(len(ring) > 400 and all(nm(cols[c][2]) == "Soil_Grass" for c in ring), "J A the island round the slab has a grass top (%d columns)" % len(ring))
    # round, not square
    xs = [c[0] for c in ring]
    zs = [c[1] for c in ring]
    area = len(ring) + 900
    bbox = (max(xs) - min(xs) + 1) * (max(zs) - min(zs) + 1)
    fill = area / float(bbox)
    cxm, czm = 14.5, 14.5
    reach = {}
    for (x, z) in ring:
        a = (math.degrees(math.atan2(z + 0.5 - czm, x + 0.5 - cxm)) + 360.0) % 360.0
        r = math.hypot(x + 0.5 - cxm, z + 0.5 - czm)
        reach[int(a // 5)] = max(reach.get(int(a // 5), 0), r)
    axis = [reach.get(b, 0) for b in (0, 18, 36, 54, 71, 17, 35, 53)]
    diag = [reach.get(b, 0) for b in (9, 27, 45, 63)]
    ratio = (sum(diag) / len(diag)) / (sum(axis) / len(axis))
    K.check(fill < 0.88, "J A ROUND, not square: the island fills %.2f of its bounding box (a square 1.00, a circle 0.79)" % fill)
    K.check(ratio < 1.2, "J A ... the diagonal reaches %.2f x the axis reach (a square slab with an even margin ~1.3, a circle 1.0)" % ratio)
    rs = sorted(reach.values())
    K.check(rs[-1] - rs[0] > 3.0, "J A ... and the rim is irregular (reach %.1f..%.1f)" % (rs[0], rs[-1]))
    # under the slab: dirt; at the bottom: rock; deep in the middle, thin at the rim
    under = [(x, z) for x in range(0, 30) for z in range(0, 30) if not (x == 4 and z == 4)]
    K.check(all(nm(b1.get((x, 98, z), 0)) in ("Soil_Dirt", "Soil_Grass") for (x, z) in under), "J A the slab stands on soil (y 98 under every slab column)")
    cm = cols.get((14, 14))
    K.check(cm is not None and nm(cm[3]) == "Rock_Stone" and cm[1] <= T - 2 - 0.6 * float(j.depth), "J A the middle column ends in rock %d blocks under the top (depth %.0f)" % (T - (cm[1] if cm else T), float(j.depth)))
    rim = sorted(ring, key=lambda c: -math.hypot(c[0] + 0.5 - cxm, c[1] + 0.5 - czm))[:40]
    rimd = sum(T - cols[c][1] for c in rim) / float(len(rim))
    K.check(rimd < 0.45 * (T - cm[1]), "J A a TAPERED underside: the rim is %.1f deep, the middle %d (teardrop like the balloon-town island)" % (rimd, T - cm[1]))
    # the plant in the hole: living soil right under it
    K.check(nm(b1.get((4, 99, 4), 0)) == "Soil_Grass" and nm(b1.get((4, 100, 4), 0)) == "Plant_Grass_Lush", "J A a plant without slab under it stands on grass (living soil)")
    # trees: on grass, >= 5 blocks off the slab, none inside the house
    tn = int(j.tn)
    K.check(int(j.trees) >= 1 and tn >= 1, "J A trees planted: %d" % int(j.trees))
    ok = True
    for i in range(tn):
        tx, ty, tz = int(j.tx[i]), int(j.ty[i]), int(j.tz[i])
        dch = max(0 - tx if tx < 0 else (tx - 29 if tx > 29 else 0), 0 - tz if tz < 0 else (tz - 29 if tz > 29 else 0))
        if dch < 5 or nm(b1.get((tx, ty - 1, tz), 0)) != "Soil_Grass" or b1.get((tx, ty, tz), 0) == 0:
            ok = False
            print("tree", i, tx, ty, tz, dch, nm(b1.get((tx, ty - 1, tz), 0)))
    K.check(ok, "J A every tree stands on grass >= 5 blocks off the slab (doors stay clear) with its trunk placed")
    K.check(not any(8 <= x <= 19 and 8 <= z <= 19 and y > 100 for (x, y, z) in new), "J A nothing new inside / on the house")
    K.check(not any(-14 <= x <= -11 and 10 <= z <= 14 for (x, y, z) in new), "J A the foreign land next to it is untouched (no block in its columns)")
    K.check(int(f.tints) > 0 and int(f.relights) > 0, "J A the chunks are re-tinted + relit after (%d / %d)" % (int(f.tints), int(f.relights)))
    K.notes.append("islet A: %d blocks, %d trees, fill %.2f, diag/axis %.2f, depth mid %d rim %.1f" % (int(j.placed), int(j.trees), fill, ratio, T - cm[1], rimd))
    # ---- B: a desert structure: sand round it, DIRT under its plants
    f = scene(2)
    j, _s = run(f, 2)
    b2 = blocks(f)
    nm = lambda i: str(f.nm(i))
    K.check(int(j.state) == 6 and int(j.placed) > 500, "J B desert finished (%d blocks, %d trees)" % (int(j.placed), int(j.trees)))
    K.check(nm(b2.get((4, 99, 4), 0)) == "Soil_Dirt", "J B DESERT: the plant without slab under it stands on DIRT, not sand (Skyy: 'no dirt so all the trees died')")
    tops = [nm(b2.get((x, 100, z), 0)) for x in range(-12, -2) for z in range(-6, 2)]
    K.check("Soil_Sand" in tops and "Soil_Grass" not in tops, "J B the desert island's rim is sand")
    K.check(int(f.over) == 0, "J B only air filled")
    # ---- C: a structure that floats by design (no ground near its anchor) - left alone
    f = Fake()
    f.fill(0, 20, 140, 150, 0, 20, "Wood_Oak_Planks")
    j, _s = run(f, 1, JArray(JInt)([10, 100, 10, 0, 140, 0, 20, 150, 20]))
    K.check(int(j.state) == 6 and int(j.placed) == 0 and int(f.puts) == 0 and "no ground" in str(j.why), "J C a floating structure gets nothing: %s" % j.why)
    # ---- D: chunks not loaded -> not now (tried again later)
    f = scene(1)
    f.load = False
    j, _s = run(f, 1)
    K.check(int(j.state) == 7 and int(f.puts) == 0 and "not loaded" in str(j.why), "J D chunks not loaded: state 7, nothing placed (%s)" % j.why)
    # ---- E: a box over 190 blocks
    f = Fake()
    j, _s = run(f, 1, JArray(JInt)([100, 100, 100, 0, 90, 0, 200, 140, 50]))
    K.check(int(j.state) == 6 and "too big" in str(j.why) and int(f.puts) == 0, "J E a box over 190 blocks is left alone: %s" % j.why)
    # ---- G (review fix 4): a chunk unloads while the island is placed -> state 7, nothing recorded, the retry finishes it
    f = scene(1)
    j = Job(f, "z1g0|Structure.test|15,100,15", "Structure.test", v, 1, 6)
    n = 0
    while not bool(j.step()):
        n += 1
        if int(j.state) == 3 and int(j.cur) > 0:
            f.load = False
    K.check(int(j.state) == 7 and "unloaded" in str(j.why) and 0 < int(j.placed), "J G a chunk unloads mid-build: state 7 (%s) after %d blocks - not done" % (j.why, int(j.placed)))
    f.load = True
    f.lost = False
    j2, _s = run(f, 1)
    K.check(int(j2.state) == 6 and int(f.over) == 0, "J G the retry a minute later finishes it (%d more blocks), still only air" % int(j2.placed))
    f = scene(1)
    f.lost = True
    j = Job(f, "k", "Structure.test", v, 1, 6)
    j.step()
    K.check(not bool(j.step()) or int(j.state) == 7, "J G a read of a missing section (lost) stops the job")
    K.check(int(j.state) == 7, "J G ... with state 7")
    # ---- H (review fix 3): every world slice ends within its 15 ms budget (the plan, state 2, runs off the world thread)
    f = scene(1)
    j = Job(f, "k", "Structure.test", v, 1, 6)
    worst = {}
    while True:
        st0 = int(j.state)
        t0 = time.perf_counter()
        fin = bool(j.step())
        dt = (time.perf_counter() - t0) * 1000.0
        worst[st0] = max(worst.get(st0, 0.0), dt)
        if fin:
            break
    K.check(int(j.state) == 6 and all(worst[k] < 25.0 for k in worst if k != 2), "J H slice times (ms, worst per state; 2 = the plan, off the world thread): %s"
            % dict((k, round(v_, 1)) for k, v_ in sorted(worst.items())))
    K.eq(int(Vi.SLICE_NS), 15000000, "J H the slice budget is 15 ms")
    # ---- F: trees off -> none
    f = scene(1)
    j, _s = run(f, 1, v, 0)
    K.check(int(j.trees) == 0 and int(j.placed) > 500, "J F zones.voidTrees 0 = an island without trees")
    K.save()


# ------------------------------------------------------------------------------------------- L: start twice on the live copy
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass
    Cfg, St, Isl, Sd, RZ, Vd, Vi = (JClass(PKG + n) for n in ("WgCfg", "WgStore", "WgZ2Isles", "WgZSeed", "WgRZ", "WgVoid", "WgVIsle"))
    Paths = JClass("java.nio.file.Paths")
    if not (home and os.path.isdir(home)):
        K.check(False, "L no live copy")
        K.save()
        return

    def tree():
        o = {}
        for r, _ds, fs in os.walk(home):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, home)] = open(p, "rb").read()
        return o
    t0 = tree()
    for s in (1, 2):
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        St.FILE = Paths.get(os.path.join(home, "worlds.properties"))
        Cfg.load()
        St.read()
        Isl.LAYDIR = Paths.get(home)
        Sd.load(Isl.SEED)
        b = str(RZ.boot(Paths.get(home), Paths.get(os.path.dirname(home))))
        Vi.DONE.clear()
        Vi.load(Paths.get(home))
        K.check("no unfinished reset" in b and Vi.DONE.size() == 0, "L start %d: boot ran (%s), no void islets recorded yet" % (s, b[:160]))
    K.check(tree() == t0, "L start twice: the live copy is byte-identical (no row / file written at start) - %d files" % len(t0))
    K.check(bool(Vd.ON) and bool(Vd.MATCH) and int(Vd.SPACING) == 500 and int(Vd.LIFT_MIN) == -30 and int(Vd.LIFT_MAX) == 60 and bool(Vd.ISLETS) and int(Vd.TREES) == 6,
            "L the live config (no void rows yet) runs on the defaults: %s" % Vd.text())
    # a config with the rows set (a separate scratch file)
    cf = os.path.join(scratch, "cfgtest.properties")
    open(cf, "w", encoding="utf8").write(open(os.path.join(home, "config.properties"), encoding="utf8").read()
                                          + "\nzones.voidStructures=false\nzones.voidZoneMatch=false\nzones.voidSpacing=800\nzones.voidLiftMin=-90\n"
                                            "zones.voidLiftMax=120\nzones.voidIslets=false\nzones.voidTrees=3\n")
    Cfg.FILE = Paths.get(cf)
    Cfg.load()
    K.check(not bool(Vd.ON) and not bool(Vd.MATCH) and int(Vd.SPACING) == 800 and int(Vd.LIFT_MIN) == -60 and int(Vd.LIFT_MAX) == 90
            and not bool(Vd.ISLETS) and int(Vd.TREES) == 3, "L the void rows read from config (lift clamped -60 / 90): %s" % Vd.text())
    K.save()


# ------------------------------------------------------------------------------------------- S: the real server (probe plugin)
PROBE_SRC = r'''
import os, sys
TOOLS = %(tools)r
sys.path.insert(0, TOOLS)
import skyybuild as B
J = B.start(server_jar=B.SERVER_JAR)
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
pool.insertClassPath(%(jar)r)
W = "com.skyy.worldgen."
T = {"W": W, "WLD": "com.hypixel.hytale.server.core.universe.world.World", "UNI": "com.hypixel.hytale.server.core.universe.Universe",
     "CU": "com.hypixel.hytale.math.util.ChunkUtil", "GC": "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk",
     "OUT": %(out)r, "CS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore", "REF": "com.hypixel.hytale.component.Ref",
     "BSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
     "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
     "ZBR": "com.hypixel.hytale.server.worldgen.chunk.ZoneBiomeResult",
     "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType", "LOG": "com.hypixel.hytale.logger.HytaleLogger"}
def jv(s):
    for k in sorted(T, key=len, reverse=True):
        s = s.replace("@%%s@" %% k, T[k])
    return s
def M(c, s):
    try: c.addMethod(CtNewMethod.make(jv(s), c))
    except Exception as e: raise SystemExit("compile %%s: %%s\n%%s" %% (c.getName(), e, jv(s)[:3000]))
def F(c, s): c.addField(CtField.make(jv(s), c))
run = pool.makeClass("wgv.Run")
run.addInterface(pool.get("java.lang.Runnable"))
F(run, "public static @LOG@ LOG;")
F(run, "public static final StringBuffer OUTB = new StringBuffer();")
F(run, "public static volatile int OK = 0;")
F(run, "public static volatile int BAD = 0;")
run.addConstructor(CtNewConstructor.make("public Run() { }", run))
M(run, r"""
public static void log(String m) {
  OUTB.append(m).append('\n');
  try { LOG.at(java.util.logging.Level.INFO).log("[SkyyWgProbe] " + m); } catch (Throwable t) { }
}""")
M(run, r"""
public static void check(boolean c, String what) { if (c) { OK++; log("OK " + what); } else { BAD++; log("FAIL " + what); } }""")
M(run, r"""
public static void flush() {
  try {
    java.nio.file.Path d = java.nio.file.Paths.get("@OUT@", new String[0]);
    java.nio.file.Files.createDirectories(d, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(d.resolve("probe.txt"), OUTB.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
  } catch (Throwable t) { }
}""")
# a StructureV2-package caller (scratch probe only - its class name starts com.joszza.structurev2., like the pack mod's own frames)
ask = pool.makeClass("com.joszza.structurev2.zzprobe.Ask")
ask.addInterface(pool.get("java.lang.Runnable"))
for f in ("public @W@WgZ2Gen g;", "public int s;", "public int x;", "public int z;", "public volatile Object r;", "public volatile int h;", "public volatile boolean done;", "public volatile String err;"):
    F(ask, f)
ask.addConstructor(CtNewConstructor.make(jv("public Ask(@W@WgZ2Gen g, int s, int x, int z) { this.g = g; this.s = s; this.x = x; this.z = z; }"), ask))
M(ask, "public void run() { try { this.r = this.g.getZoneBiomeResultAt(this.s, this.x, this.z); this.h = this.g.getHeight(this.s, this.x, this.z); } catch (Throwable t) { this.err = String.valueOf(t); } this.done = true; }")
# world-thread jobs: tint zeros of a loaded chunk; the non-air blocks of a box (before / after)
wt = pool.makeClass("wgv.WT")
wt.addInterface(pool.get("java.lang.Runnable"))
for f in ("public @WLD@ w;", "public int mode;", "public int a;", "public int b;", "public int c;", "public int d;", "public int e;", "public int f;", "public int g2;",
          "public volatile Object res;", "public volatile boolean done;", "public volatile String err;"):
    F(wt, f)
wt.addConstructor(CtNewConstructor.make(jv("public WT(@WLD@ w, int mode, int a, int b, int c, int d, int e, int f, int g2) { this.w = w; this.mode = mode; this.a = a; this.b = b; this.c = c; this.d = d; this.e = e; this.f = f; this.g2 = g2; }"), wt))
M(wt, r"""
public void run() {
  try {
    @CS@ cs = this.w.getChunkStore();
    if (this.mode == 0) {
      @REF@ r = cs.getChunkReference(@CU@.indexChunk(this.a, this.b));
      if (r == null || !r.isValid()) { this.res = Integer.valueOf(-1); }
      else {
        @BCH@ bc = (@BCH@) cs.getStore().getComponent(r, @BCH@.getComponentType());
        this.res = Integer.valueOf(bc == null ? -2 : @W@WgVTint.zeros(bc));
      }
    } else {
      java.util.HashMap m = new java.util.HashMap();
      java.util.HashMap sec = new java.util.HashMap();
      for (int x = this.a; x <= this.d; x++) {
        for (int z = this.c; z <= this.f; z++) {
          for (int y = this.b; y <= this.e; y++) {
            long sk = ((((long) (x >> 5)) & 16777215L) << 32) | ((((long) (z >> 5)) & 16777215L) << 8) | ((long) ((y >> 5) & 255));
            Long kk = Long.valueOf(sk);
            Object o = sec.get(kk);
            if (o == null) {
              @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
              if (r == null || !r.isValid()) continue;
              o = cs.getStore().getComponent(r, @BSEC@.getComponentType());
              if (o == null) continue;
              sec.put(kk, o);
            }
            int id = ((@BSEC@) o).get(x, y, z);
            if (id != 0) m.put(Long.valueOf(((((long) x) & 2097151L) << 42) | ((((long) y) & 2097151L) << 21) | (((long) z) & 2097151L)), Integer.valueOf(id));
          }
        }
      }
      this.res = m;
    }
  } catch (Throwable t) { this.err = String.valueOf(t); }
  this.done = true;
}""")
M(run, r"""
public static Object onW(@WLD@ w, Runnable r, long ms) throws Exception {
  w.execute(r);
  long end = System.currentTimeMillis() + ms;
  while (System.currentTimeMillis() < end) {
    if (r instanceof wgv.WT && ((wgv.WT) r).done) return ((wgv.WT) r).res;
    if (r instanceof com.joszza.structurev2.zzprobe.Ask && ((com.joszza.structurev2.zzprobe.Ask) r).done) return r;
    Thread.sleep(20L);
  }
  return null;
}""")
M(run, r"""
public static String bname(int id) {
  try { Object t = @BTY@.getAssetMap().getAsset(id); return t instanceof @BTY@ ? String.valueOf(((@BTY@) t).getId()) : "?"; } catch (Throwable t) { return "?"; }
}""")
M(run, r"""
public static void load(@WLD@ w, int cx0, int cz0, int cx1, int cz1) {
  for (int cx = cx0; cx <= cx1; cx++) for (int cz = cz0; cz <= cz1; cz++) {
    try { w.getChunkStore().getChunkReferenceAsync(@CU@.indexChunk(cx, cz)).get(120L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { log("chunk " + cx + "," + cz + " load: " + t); }
  }
}""")
M(run, open(%(body)r, encoding="utf8").read().split("#BODY\n", 1)[1])
pl = pool.makeClass("wgv.SkyyWgProbePlugin", pool.get("com.hypixel.hytale.server.core.plugin.JavaPlugin"))
pl.addConstructor(CtNewConstructor.make("public SkyyWgProbePlugin(com.hypixel.hytale.server.core.plugin.JavaPluginInit init) { super(init); }", pl))
M(pl, "public void setup() { wgv.Run.LOG = getLogger(); wgv.Run.log(\"1.0.0 ready (TEST PROBE wg0711 - never deploy)\"); Thread t = new Thread(new wgv.Run(), \"SkyyWgProbeV\"); t.setDaemon(true); t.start(); }")
out = os.path.join(%(pdir)r, "classes")
import shutil
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
for c in (run, ask, wt, pl):
    c.writeFile(out)
man = B.manifest("SkyyWgProbe", "1.0.0", "TEST PROBE wg0711 (scratch only, never deployed)", "wgv.SkyyWgProbePlugin")
man["IncludesAssetPack"] = False
man["Dependencies"] = {%(key)r: "*"}
B.assemble(os.path.join(%(pdir)r, "SkyyWgProbe-1.0.0.jar"), man, out)
'''

PROBE_BODY = r'''#BODY
public void run() {
  try {
    @UNI@ u = null;
    for (int i = 0; i < 1200; i++) { try { u = @UNI@.get(); if (u != null && u.getDefaultWorld() != null) break; } catch (Throwable t) { } Thread.sleep(250L); }
    Thread.sleep(4000L);
    @WLD@ w = u.getWorld("skywynn_zones2");
    if (w == null) w = (@WLD@) u.loadWorld("skywynn_zones2").get(240L, java.util.concurrent.TimeUnit.SECONDS);
    @W@WgZ2Gen g = @W@WgZ2Isles.genOf(w);
    int s = (int) w.getWorldConfig().getSeed();
    @W@WgZ2Layout L = g.layoutReady(s);
    if (L == null) L = g.layoutNow(s);
    for (int i = 0; i < 600 && @W@WgVoid.ZW != w; i++) Thread.sleep(100L);
    for (int i = 0; i < 100 && @W@WgVoid.ZT == null; i++) Thread.sleep(100L);
    check(@W@WgVoid.ZW == w && @W@WgVoid.ZT != null, "S0 the heal listener saw the zone world and knows its thread (" + @W@WgVoid.ZT + ")");
    // ---- S1 the heal: a stored black void chunk (tavern_house 288 -422 = chunk 9,-14; Big_Tower_Goblin 609 -124 = 19,-4) loads healed
    long h0 = @W@WgVoid.HEALC.get();
    int[] hc = new int[] { 9, -14, 19, -4 };
    for (int i = 0; i < 4; i += 2) {
      load(w, hc[i], hc[i + 1], hc[i], hc[i + 1]);
      Object z = onW(w, new wgv.WT(w, 0, hc[i], hc[i + 1], 0, 0, 0, 0, 0), 20000L);
      check(z instanceof Integer && ((Integer) z).intValue() == 0, "S1 chunk " + hc[i] + "," + hc[i + 1] + " (a void structure, stored black) loads with 0 black columns (" + z + ")");
    }
    check(@W@WgVoid.HEALC.get() > 0L, "S1 black chunks healed so far: " + @W@WgVoid.HEALC.get() + " (" + @W@WgVoid.HEALN.get() + " columns; +" + (@W@WgVoid.HEALC.get() - h0) + " by these loads)");
    // ---- S2 a NEW void chunk (never stored) gets vanilla's grass colour
    double[] mm = new double[1];
    int vx = 0;
    int vz = 0;
    boolean got = false;
    for (int r = 1400; r < 2600 && !got; r += 64) {
      for (int a = 0; a < 360 && !got; a += 15) {
        int x = (int) (L.cx[0] + r * Math.cos(Math.toRadians((double) a)));
        int z = (int) (L.cz[0] + r * Math.sin(Math.toRadians((double) a)));
        if (@W@WgZ2Isles.member(L, x + 0.5, z + 0.5, mm) < 0 && @W@WgZ2Isles.ownerOf(L, x >> 5, z >> 5) == 0) {
          long ix = @CU@.indexChunk(x >> 5, z >> 5);
          @GC@ gc = (@GC@) g.generateWith(L, s, ix, x >> 5, z >> 5, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
          int zero = 0;
          int c0 = gc.getBlockChunk().getTint(16, 16);
          boolean fb = true;
          for (int i = 0; i < 32; i++) for (int k = 0; k < 32; k++) { int t = gc.getBlockChunk().getTint(i, k); if (t == 0) zero++; if (t != @W@WgVoid.FALLBACK) fb = false; }
          check(zero == 0 && ((c0 >>> 24) & 255) == 255, "S2 a NEW void chunk " + (x >> 5) + "," + (z >> 5) + " has no black column, colour " + Integer.toHexString(c0) + (fb ? " (= the fallback green)" : " (vanilla's biome tint)"));
          check(!fb, "S2 ... from vanilla's own biome tint (not only the fallback)");
          vx = x;
          vz = z;
          got = true;
        }
      }
    }
    check(got, "S2 a void chunk owned by Zone 1 was found to generate");
    // ---- S3 the filter as StructureV2 sees it (a com.joszza.structurev2.* caller on the world thread) vs a plain caller
    int lx = (int) Math.floor(L.lx[0]);
    int lz = (int) Math.floor(L.lz[0]);
    long a0 = @W@WgVoid.ASK.get();
    com.joszza.structurev2.zzprobe.Ask q = (com.joszza.structurev2.zzprobe.Ask) onW(w, new com.joszza.structurev2.zzprobe.Ask(g, s, lx, lz), 20000L);
    @ZBR@ pl0 = g.getZoneBiomeResultAt(@W@WgZ2Isles.seedAt(L, lx >> 5, lz >> 5, s), lx, lz);
    int ph0 = g.getHeight(@W@WgZ2Isles.seedAt(L, lx >> 5, lz >> 5, s), lx, lz);
    check(q != null && q.err == null && q.r != null && pl0 != null && @W@WgVoid.clsOf((@ZBR@) q.r) == @W@WgVoid.clsOf(pl0) && q.h == ph0,
          "S3 land (the Zone 1 landing): StructureV2 gets vanilla's zone + height unchanged (h " + (q == null ? -1 : q.h) + " = " + ph0 + ")");
    check(@W@WgVoid.ASK.get() > a0, "S3 the filter counted StructureV2's call (the stack check works)");
    int cz1 = @W@WgZ2Isles.Z_CLS[0];
    int nOther = 0;
    int nOtherNull = 0;
    int nSame = 0;
    int nSameOk = 0;
    int nLift = 0;
    String ex = "";
    for (int r = 1150; r < 2200; r += 48) {
      for (int a = 0; a < 360; a += 10) {
        int x = (int) (L.cx[0] + r * Math.cos(Math.toRadians((double) a)));
        int z = (int) (L.cz[0] + r * Math.sin(Math.toRadians((double) a)));
        if (@W@WgZ2Isles.member(L, x + 0.5, z + 0.5, mm) >= 0 || @W@WgZ2Isles.ownerOf(L, x >> 5, z >> 5) != 0) continue;
        int sd = @W@WgZ2Isles.seedAt(L, x >> 5, z >> 5, s);
        int cls = @W@WgVoid.clsOf(g.getZoneBiomeResultAt(sd, x, z));
        if (cls > 0 && cls != cz1 && nOther < 6) {
          q = (com.joszza.structurev2.zzprobe.Ask) onW(w, new com.joszza.structurev2.zzprobe.Ask(g, s, x, z), 20000L);
          nOther++;
          if (q != null && q.err == null && q.r == null) nOtherNull++;
          if (ex.length() == 0) ex = "class " + cls + " at " + x + " " + z;
        }
        if (cls == cz1 && @W@WgVoid.inDisk(x, z, @W@WgVoid.SPACING) && !@W@WgVoid.occupied(x, z, @W@WgVoid.SPACING) && nSame < 6) {
          q = (com.joszza.structurev2.zzprobe.Ask) onW(w, new com.joszza.structurev2.zzprobe.Ask(g, s, x, z), 20000L);
          nSame++;
          int ph = g.getHeight(sd, x, z);
          int want = @W@WgVoid.lift(L, x, z, ph);
          if (q != null && q.err == null && q.r != null) nSameOk++;
          if (q != null && q.h == want) nLift++;
          if (nSame == 1) log("S3 an allowed void point " + x + " " + z + ": vanilla height " + ph + ", StructureV2 sees " + (q == null ? -1 : q.h) + " (square lift " + @W@WgVoid.liftOf(x, z) + ")");
        }
      }
    }
    check(nOther == 0 || nOtherNull == nOther, "S3 another zone's vanilla land under the void off Zone 1 (" + ex + "): refused for StructureV2 " + nOtherNull + " of " + nOther);
    if (nOther == 0) log("S3 no other-zone class found under Zone 1's void in the sampled ring (the zone test is proved in the V phase)");
    check(nSame > 0 && nSameOk == nSame && nLift == nSame, "S3 Zone 1's own class inside a free spawn disk: allowed " + nSameOk + " of " + nSame + ", height = vanilla + the square's lift " + nLift + " of " + nSame);
    log("S3 " + @W@WgVoid.stats());
    // ---- S4 the 5 s dresser ran and read StructureV2's record (empty in this copy)
    for (int i = 0; i < 300 && @W@WgVIsle.POLLS < 2; i++) Thread.sleep(100L);
    check(@W@WgVIsle.POLLS >= 2, "S4 the 5-second dresser runs (" + @W@WgVIsle.POLLS + " polls)");
    // ---- S5 a REAL floating island under the real tavern_house over the void (its record row + podloze, from today's copy)
    String rec = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(%(rows)r, new String[0])), "UTF-8");
    @W@WgVIsle.parse(rec, "skywynn_zones2", L);
    int[] v = null;
    java.util.ArrayList rows = @W@WgVIsle.ROWS;
    for (int i = 0; i < rows.size(); i++) {
      Object[] rr = (Object[]) rows.get(i);
      int[] vv = (int[]) rr[1];
      if ("Structure.tavern_house".equals(rr[0]) && vv[0] == 288 && vv[2] == -422) v = vv;
    }
    check(v != null && @W@WgZ2Isles.member(L, v[0] + 0.5, v[2] + 0.5, mm) < 0, "S5 the tavern_house row (288 124 -422) is over the void on this layout");
    if (v != null) {
      int[] u2 = @W@WgVIsle.merge(rows, v);
      int k = @W@WgZ2Isles.ownerOf(L, v[0] >> 5, v[2] >> 5);
      String key = @W@WgVIsle.keyOf(L, k, "Structure.tavern_house", v);
      @W@WgVJob j = @W@WgVIsle.job(g, L, new Object[] { key, "Structure.tavern_house", u2, Integer.valueOf(k) }, new @W@WgVAccW(w, g));
      log("S5 job box " + j.x0 + ".." + (j.x0 + j.w) + " x " + j.z0 + ".." + (j.z0 + j.h) + ", y " + j.yBot + ".." + j.yTop + ", zone class " + j.cls);
      load(w, j.x0 >> 5, j.z0 >> 5, (j.x0 + j.w - 1) >> 5, (j.z0 + j.h - 1) >> 5);
      java.util.HashMap b0 = (java.util.HashMap) onW(w, new wgv.WT(w, 1, j.x0, j.yBot, j.z0, j.x0 + j.w - 1, j.yTop, j.z0 + j.h - 1, 0), 120000L);
      check(b0 != null && b0.size() > 1000, "S5 the structure's blocks read before: " + (b0 == null ? -1 : b0.size()));
      @W@WgVIsle.BUSY = true;
      new @W@WgVRun(w, j).run();
      for (int i = 0; i < 3000 && @W@WgVIsle.BUSY; i++) Thread.sleep(100L);
      check(!@W@WgVIsle.BUSY && j.state == 6, "S5 the job finished on the world thread: state " + j.state + ", " + j.placed + " blocks, " + j.trees + " tree(s), why '" + j.why + "', T " + j.T + ", " + Math.round(j.rout * 2.0) + " across, " + Math.round(j.depth) + " deep");
      check(j.placed > 1000 && j.trees >= 1, "S5 a real floating island: " + j.placed + " blocks, " + j.trees + " tree(s)");
      java.util.HashMap b1 = (java.util.HashMap) onW(w, new wgv.WT(w, 1, j.x0, j.yBot, j.z0, j.x0 + j.w - 1, j.yTop, j.z0 + j.h - 1, 0), 120000L);
      int changed = 0;
      java.util.Iterator it = b0.keySet().iterator();
      while (it.hasNext()) { Object kk = it.next(); if (!b0.get(kk).equals(b1.get(kk))) changed++; }
      int added = b1.size() - b0.size();
      check(changed == 0, "S5 only AIR was filled: every one of the " + b0.size() + " blocks there before is unchanged (" + changed + " changed)");
      check(added >= j.placed, "S5 the new blocks are in the world: +" + added + " (placed " + j.placed + " + trees)");
      java.util.HashMap cnt = new java.util.HashMap();
      it = b1.keySet().iterator();
      while (it.hasNext()) { Object kk = it.next(); if (b0.containsKey(kk)) continue; String n = bname(((Integer) b1.get(kk)).intValue()); Integer c = (Integer) cnt.get(n); cnt.put(n, Integer.valueOf(c == null ? 1 : c.intValue() + 1)); }
      log("S5 new blocks by type: " + cnt);
      check(cnt.containsKey("Soil_Grass") && cnt.containsKey("Soil_Dirt") && cnt.containsKey("Rock_Stone"), "S5 grass top, dirt, rock underside");
      check(@W@WgVIsle.DONE.containsKey(key) && java.nio.file.Files.exists(@W@WgVIsle.FILE, new java.nio.file.LinkOption[0]), "S5 recorded in " + @W@WgVIsle.FILE + " (" + key + ")");
      for (int i = 0; i < 2; i++) {
        Object z = onW(w, new wgv.WT(w, 0, (j.x0 >> 5) + i, j.z0 >> 5, 0, 0, 0, 0, 0), 20000L);
        check(z instanceof Integer && ((Integer) z).intValue() == 0, "S5 the island's chunk " + ((j.x0 >> 5) + i) + "," + (j.z0 >> 5) + " has no black grass column (" + z + ")");
      }
      log("S5 " + @W@WgVoid.stats());
    }
  } catch (Throwable t) { log("probe FAILED " + t); BAD++; }
  log("RESULT ok=" + OK + " fail=" + BAD);
  flush();
}'''


def server_phase():
    # Skyy 2026-10-24: builders never run smoke_test.py - the main session runs this phase (one server at a time) with --server
    if "--server" not in sys.argv or "--no-smoke" in sys.argv:
        print("S. skipped (run with --server, main session only, game closed) - the live path is UNVERIFIED by this run")
        return
    import deploy_set as DS
    if DS.server_running():
        print("S. NOT RUN: a HytaleServer is running (the game / another smoke test) - the live path is UNVERIFIED by this run")
        HK.check(False, "S not run: a HytaleServer is running")
        return
    if not os.path.isfile(OLD_SPAWNS):
        HK.check(False, "S needs the record copy %s" % OLD_SPAWNS)
        return
    pdir = os.path.join(SCRATCH, "probe")
    odir = os.path.join(SCRATCH, "probe-out")
    os.makedirs(pdir, exist_ok=True)
    rows = os.path.join(pdir, "rows.json")
    shutil.copyfile(OLD_SPAWNS, rows)
    key = "Skyy:%s SkyyWorldGen" % VERSION
    body = os.path.join(pdir, "body.txt")
    open(body, "w", encoding="utf8").write(PROBE_BODY.replace("%(rows)r", json.dumps(rows.replace("\\", "/"))))
    open(os.path.join(pdir, "pb.py"), "w", encoding="utf8").write(PROBE_SRC % {"tools": os.path.join(ROOT, "tools"), "jar": JAR, "out": odir.replace("\\", "/"),
                                                                                 "pdir": pdir, "key": key, "body": body})
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    r1 = subprocess.run([sys.executable, os.path.join(pdir, "pb.py")], cwd=pdir, env=env, capture_output=True, text=True, timeout=900)
    pj = os.path.join(pdir, "SkyyWgProbe-1.0.0.jar")
    okb = r1.returncode == 0 and os.path.isfile(pj)
    HK.check(okb, "S the test probe builds: %s" % (r1.stdout + r1.stderr)[-1500:])
    if not okb:
        return
    smoke = os.path.join(ROOT, "tools", "dev", "scratch", "smoke")
    before = set(os.listdir(smoke)) if os.path.isdir(smoke) else set()
    args = [sys.executable, os.path.join(ROOT, "tools", "smoke_test.py"), "--linger", "480", "--xmx", "6G", "--allow-pack-api", "--jar", JAR, "--jar", pj]
    t0 = time.time()
    r2 = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=3600)
    open(os.path.join(SCRATCH, "smoke-out.txt"), "w", encoding="utf8").write(r2.stdout + r2.stderr)
    new = sorted(set(os.listdir(smoke)) - before) if os.path.isdir(smoke) else []
    ml = re.search(r"^  log: (.+\.log)\s*$", r2.stdout or "", re.M)
    logs = [os.path.basename(ml.group(1).strip())] if ml and os.path.isfile(ml.group(1).strip()) and os.path.basename(ml.group(1).strip()) in new else []
    txt = open(os.path.join(odir, "probe.txt"), encoding="utf8").read() if os.path.isfile(os.path.join(odir, "probe.txt")) else ""
    for l in txt.splitlines():
        print("   S " + l[:400])
    m = re.search(r"RESULT ok=(\d+) fail=(\d+)", txt)
    HK.check(m is not None and int(m.group(2)) == 0 and int(m.group(1)) >= 12, "S the probe on the REAL server: %s (%.0f s)" % (m.group(0) if m else "no RESULT", time.time() - t0))
    for l in txt.splitlines():
        if l.startswith("FAIL "):
            HK.check(False, "S " + l)
    so = r2.stdout or ""
    ours = [l for l in so.splitlines() if l.strip().startswith("FAIL") and "SkyyWgProbe" not in l]
    HK.check(not ours and ("SMOKE TEST PASS" in so or "no ready line: SkyyWgProbe" in so), "S smoke: every SET ready line, no Skyy SEVERE: %s" % ours[:5])
    if logs:
        lg = open(os.path.join(smoke, logs[-1]), encoding="utf-8", errors="replace").read()
        sev = [l for l in lg.splitlines() if ("SEVERE" in l or "ERROR" in l) and "SkyyWorldGen" in l]
        HK.check(not sev, "S no SEVERE / ERROR line of SkyyWorldGen in the server log: %s" % sev[:3])
        wl = [l for l in lg.splitlines() if "SkyyWorldGen" in l and ("void" in l.lower() or "WARN" in l)]
        for l in wl[:25]:
            print("   LOG " + l[:300])
        shutil.copyfile(os.path.join(smoke, logs[-1]), os.path.join(SCRATCH, "server.log"))
        try:
            os.remove(os.path.join(smoke, logs[-1]))
        except OSError:
            pass


if __name__ == "__main__":
    _run0 = HK.run

    def _run_with_server(*a, **kw):
        _exit0 = sys.exit

        def _exit(code=0):
            sys.exit = _exit0
            if "--phase" not in sys.argv:
                server_phase()
                print("SkyyWorldGen %s harness (with the server phase): %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
                for f in HK.FAILS:
                    print("FAIL:", f)
                _exit0(1 if HK.FAILS else 0)
            _exit0(code)
        sys.exit = _exit
        return _run0(*a, **kw)
    _run_with_server("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
                     [("tint", run_tint), ("void", run_void), ("islet", run_islet), ("live", run_live)], __file__, live=(LIVE_WG, "Skyy_SkyyWorldGen"))
