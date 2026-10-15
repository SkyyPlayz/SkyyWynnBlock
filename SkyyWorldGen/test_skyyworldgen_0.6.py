"""SkyyWorldGen 0.6 - harness for THE ZONE ISLANDS (tools/worldgen_0_6_patch.py). Bare child JVMs: the game's own JRE, the CACHED 0.7
HytaleServer.jar (tools/serverjar.py), -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The 0.7 engine
stand-ins (packet sink, store, worlds with a task queue, Universe, an async spawn provider) come from SkyyProfiles/test_skyyprofiles_0.1.10.py
(engine()); the shared JVM helpers from SkySkills/test_skyyskills_0.4.27.py (both read only). The live Skyy_SkyyWorldGen folder is only
READ (copied into scratch) and checked afterwards. Plus ONE offline server start (section VP, through tools/smoke_test.py - the only allowed
start) when no HytaleServer runs; while the game is open VP is NOT RUN and says so.

    python SkyyWorldGen/test_skyyworldgen_0.6.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-smoke]
         [--jar SkyyWorldGen-0.6.jar] [--prev SkyyWorldGen-0.5.1.jar]

SECTIONS
  CC  CLASS COMPARE 0.5.1 -> 0.6: + exactly the 9 zone classes (WgZoneArrive: fix round); the 0.5 generator classes (WgIsle, WgIsleGen, WgMaskFn, WgMaskHop,
      WgIsleProvider, WgIsleSupplier) and WgSpawnTask / WgDone / WgApplyLanding / WgReady / WgStore / WgLog byte-for-byte unchanged in
      behaviour (= the old worlds' chunks keep generating exactly as before); the structural changes listed
  JT  jar entries: 0.5.1's + the 9 classes + exactly 3 new files (the SkyWynn_Zones template + its InstanceData, our ore block); every
      old non-class entry byte-identical but the manifest and the version in the templates' comments
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7 engine
  MK  the zone island maths on a SYNTHETIC zone map (a compiled IntBinaryOperator): the picker (Zone 1 at the spawn, Zones 2-5 in their
      own class's land, the full gap, a too-shallow islet skipped), membership vs the map's truth away from the coasts (the radius cap,
      a big foreign hole kept as void, a small lake filled), the holes / filled counters, bottomOf = an independent Python formula,
      chunkOutside never skips a chunk holding an island column, determinism; a SYNTHETIC GeneratedChunk through maskWith (void columns
      empty + Env_Void id, the underside cut, the 2-block shell, decorations only on the zone's ground into air, hanging roots only
      under the rim, lava cracks replace ground, Zone 5 ores only in host rock of the Zone 5 island); WgZoneFn failure path (an EMPTY
      chunk + one SEVERE); WgZoneHop both paths; WgZoneProvider offline (the vanilla generator cannot load in a bare JVM -> SEVERE +
      WorldGenLoadException); the codec
  Z   the /zone paths EXECUTED with engine stand-ins: /zone 3 from the main world (loaded zone world -> the landing, up to the engine's
      teleport call), /zone 2 on the zone world (Teleport at the Zone 2 landing), a missing Zone 5 island, the 0.6 switch off (/zone 3
      refused, /zone 1 = the old test island), /zone old, /zone world, /zone 9, /zone info / list texts, setlanding refused, WgCfg.apply,
      WgCheck, the hooks, WgZones.index / label / isIsland, WgApplyLanding leaves the zone world's spawn alone, the template decode
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen (WgCfg.load, WgStore.read, the config kit): no file changed
  VP  the REAL vanilla 0.7 generator: a test probe jar (scratch only) + this jar on an offline server copy (tools/smoke_test.py): the zone
      world made by /zone's own code, the layout picked from the REAL zone map (5 islands, purity, gaps, landings, spawn), ~60 sample
      chunks masked vs plain vanilla of the same seed voxel by voxel, decorations / features / ores per island, a void chunk skipped,
      determinism across a fresh generator, the saved config decodes back, the /zone texts; smoke PASS (--allow-pack-api)
  AA  python tools/ci/crosscheck.py --jar <0.6> --baseline: no FAIL for SkyyWorldGen on 0.7, the command tree = 0.5.1's
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time, math, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.6", "0.5.1"
PKG = "com.skyy.worldgen."
NEW_CLASSES = ["WgZoneArrive", "WgZoneFn", "WgZoneGen", "WgZoneHop", "WgZoneIsles", "WgZoneLayout", "WgZoneProvider", "WgZoneSampler", "WgZoneSupplier"]
FROZEN = ["WgIsle", "WgIsleGen", "WgMaskFn", "WgMaskHop", "WgIsleProvider", "WgIsleSupplier", "WgSpawnTask", "WgDone", "WgApplyLanding",
          "WgReady", "WgStore", "WgLog"]
ZSEED = 20261014


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "zones06", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyWorldGen-%s.jar" % PREV_VERSION)))
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


def fake_dist_to_edge(x, z):
    """distance from (x, z) to the nearest disk border (for 'far from any coast' samples)"""
    return min(abs(math.hypot(x - cx, z - cz) - r) for cx, cz, r, _c in FAKE_DISKS)


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JInt
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
        N = TP.engine(S, B, hcls, "skyywg06")
        jf, U = N["jf"], N["U"]
        # the synthetic zone map class
        HPool = JClass("javassist.ClassPool")(False)
        HPool.appendSystemPath()
        Ctm, Ctc, Ctf = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
        fm = HPool.makeClass("skyywg06.FakeMap")
        fm.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        fm.addField(Ctf.make("public int calls;", fm))
        fm.addConstructor(Ctc.make("public FakeMap() { }", fm))
        body = "public int applyAsInt(int x, int z) {\n  this.calls = this.calls + 1;\n"
        for cx, cz, r, c in FAKE_DISKS:
            body += "  if (((double) x - %r) * ((double) x - %r) + ((double) z - %r) * ((double) z - %r) <= %r) return %d;\n" % (cx, cx, cz, cz, r * r, c)
        body += "  return 0;\n}"
        fm.addMethod(Ctm.make(body, fm))
        fh = HPool.makeClass("skyywg06.FlatH")
        fh.addInterface(HPool.get("java.util.function.IntBinaryOperator"))
        fh.addField(Ctf.make("public int h;", fh))
        fh.addConstructor(Ctc.make("public FlatH(int h) { this.h = h; }", fh))
        fh.addMethod(Ctm.make("public int applyAsInt(int x, int z) { return this.h; }", fh))
        GCN = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"
        fl = HPool.makeClass("skyywg06.Fill")
        fl.addConstructor(Ctc.make("public Fill() { }", fl))
        fl.addMethod(Ctm.make("public static " + GCN + " make(int cx, int cz, int ground, int h) {\n"
                              "  " + GCN + " g = new " + GCN + "();\n"
                              "  g.getBlockChunk().setCoordinates(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx, cz), cx, cz);\n"
                              "  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) for (int y = 0; y < h; y++) g.getBlockChunk().setBlock(x, y, z, y < h - 1 ? 7 : ground, 0, 0);\n"
                              "  return g;\n}", fl))
        fl.addMethod(Ctm.make("public static int[] dump(" + GCN + " g) {\n"
                              "  int[] a = new int[32 * 32 * 320];\n"
                              "  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) for (int y = 0; y < 320; y++) a[(x * 32 + z) * 320 + y] = g.getBlockChunk().getBlock(x, y, z);\n"
                              "  return a;\n}", fl))
        fl.addMethod(Ctm.make("public static int[] envs(" + GCN + " g) {\n"
                              "  int[] a = new int[32 * 32];\n"
                              "  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) a[x * 32 + z] = g.getBlockChunk().getEnvironment(x, 200, z);\n"
                              "  return a;\n}", fl))
        for c_ in (fm, fh, fl):
            c_.writeFile(hcls)
        FakeMap, FlatH = JClass("skyywg06.FakeMap"), JClass("skyywg06.FlatH")
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
        Isl, Lay, Gen = jc("new", "WgZoneIsles"), jc("new", "WgZoneLayout"), jc("new", "WgZoneGen")
        E = {}
        # ================================================================================ MK: the maths on the synthetic map
        smp = FakeMap()
        t0 = time.time()
        Lz = Isl.layout(smp, 0.5, 0.5, 777)
        lay_s = time.time() - t0
        n = int(Lz.n)
        found = [bool(Lz.found[i]) for i in range(n)]
        cen = [[round(float(Lz.cx[i]), 1), round(float(Lz.cz[i]), 1)] for i in range(n)]
        gaps = [float(Lz.gapUsed[i]) for i in range(n)]
        cls = [int(Lz.cls[i]) for i in range(n)]
        rad = [float(Lz.rad[i]) for i in range(n)]
        holes = [int(Lz.holes[i]) for i in range(n)]
        filled = [int(Lz.filled[i]) for i in range(n)]
        lands = [[float(Lz.lx[i]), float(Lz.lz[i])] for i in range(n)]
        E["mk_layout"] = dict(found=found, cen=cen, gaps=gaps, cls=cls, rad=rad, holes=holes, filled=filled, lands=lands, secs=round(lay_s, 1),
                              calls=int(smp.calls), spawnCls=int(Lz.spawnCls), text=str(Isl.layoutText(Lz)), ms=int(Lz.ms))
        # membership vs the map truth, away from any coast (radius cap +- wobble 30 + coast wobble 7.5 + grid 8 + interpolation)
        rng = random.Random(6)
        m1 = JArray(jpype.JDouble)(1)
        bad, tested, insides = [], 0, [0] * 5
        for _ in range(6000):
            x = rng.uniform(-5200.0, 5200.0)
            z = rng.uniform(-5200.0, 5600.0)
            if fake_dist_to_edge(x, z) < 24.0:
                continue
            c = fake_class(x, z)
            want = -1
            for i in range(n):
                if not found[i]:
                    continue
                d = math.hypot(x - cen[i][0], z - cen[i][1])
                if c == cls[i] and d <= rad[i] - 30.0 - 24.0:
                    # the piece connected to the centre: every disk is convex, so all of its land within the cap is connected
                    want = i
                elif c == cls[i] and d < rad[i] + 30.0 + 24.0:
                    want = -2          # near the radius cap: either
            if want == -1 and c == 0 and math.hypot(x + 400.0, z + 300.0) < 30.0:
                want = 0
            if c == 4 and math.hypot(x + 3000.0, z - 600.0) <= 150.0:
                want = -1          # the shallow islet: land of the class, but not the piece connected to the Zone 4 centre
            if want == -2:
                continue
            got = int(Isl.member(Lz, x, z, m1))
            tested += 1
            if got >= 0:
                insides[got] += 1
            if got != want:
                bad.append([round(x), round(z), c, want, got])
        lake = int(Isl.member(Lz, -400.0, -300.0, m1))
        desert = int(Isl.member(Lz, 300.0, 200.0, m1))
        E["mk_member"] = dict(tested=tested, bad=bad[:8], nbad=len(bad), insides=insides, lake=lake, desert=desert)
        # bottomOf = the independent formula (the noise terms read from the jar's WgIsle.vnoise: this checks the composition)
        Old = jc("new", "WgIsle")
        P6 = dict(SKIRT=float(Isl.SKIRT), KEEL=float(Isl.KEEL), RIM=float(Isl.RIM_BOT), MT=float(Isl.MIN_THICK), RA=float(Isl.RA), RS=float(Isl.RS),
                  DRIP=float(Isl.DRIP), DT=float(Isl.DRIP_T), DS=float(Isl.DRIP_S))
        bb = []
        for _ in range(3000):
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
        drips = sum(1 for _ in range(1))
        E["mk_bottom"] = dict(bad=bb[:5], nbad=len(bb))
        # chunkOutside is conservative: a chunk with ANY island column is never skipped
        rb, nchunks, nskip = [], 0, 0
        for i in range(n):
            if not found[i]:
                continue
            for k in range(28):
                a = 2.0 * math.pi * k / 28.0
                dd = rad[i] + rng.uniform(-60.0, 80.0)
                cxw, czw = cen[i][0] + dd * math.cos(a), cen[i][1] + dd * math.sin(a)
                ccx, ccz = int(math.floor(cxw / 32.0)), int(math.floor(czw / 32.0))
                nchunks += 1
                skip = bool(Isl.chunkOutside(Lz, ccx, ccz))
                if skip:
                    nskip += 1
                    anyin = False
                    for lx in range(0, 32, 1):
                        for lz in range(0, 32, 1):
                            if int(Isl.member(Lz, ccx * 32 + lx + 0.5, ccz * 32 + lz + 0.5, m1)) >= 0:
                                anyin = True
                                break
                        if anyin:
                            break
                    if anyin:
                        rb.append([ccx, ccz])
        far = bool(Isl.chunkOutside(Lz, 60, 60))       # (1920, 1920): between Zone 1 and the others
        E["mk_outside"] = dict(chunks=nchunks, skipped=nskip, bad=rb[:5], far=far)
        Lz2 = Isl.layout(FakeMap(), 0.5, 0.5, 777)
        same = all(float(Lz.cx[i]) == float(Lz2.cx[i]) and float(Lz.cz[i]) == float(Lz2.cz[i]) for i in range(n)) and all(
            JClass("java.util.Arrays").equals(Lz.sd[i], Lz2.sd[i]) for i in range(n) if Lz.sd[i] is not None)
        E["mk_det"] = same
        # ---- fix 3: the saved layout (save -> load = identical; wrong seed refused; a bare generator with NO vanilla map reuses it)
        ldir = os.path.join(SCRATCH, "lay")
        os.makedirs(ldir, exist_ok=True)
        Isl.LAYDIR = Paths.get(ldir)
        lf = Isl.layoutFile(777)
        saved_ok = bool(Isl.saveLayout(Lz, lf))
        L3 = Isl.loadLayout(lf, 777)
        Arr_ = JClass("java.util.Arrays")

        def same_lay(A, B_):
            if A is None or B_ is None or int(A.n) != int(B_.n) or int(A.seed) != int(B_.seed) or float(A.spx) != float(B_.spx) \
                    or float(A.spz) != float(B_.spz) or int(A.spawnCls) != int(B_.spawnCls):
                return False
            for f_ in ("cx", "cz", "rad", "cls", "found", "gapUsed", "gx0", "gz0", "gn", "lx", "lz", "area", "filled", "holes", "maxsd",
                       "minX", "maxX", "minZ", "maxZ"):
                if not Arr_.equals(getattr(A, f_), getattr(B_, f_)):
                    return False
            return all(Arr_.equals(A.sd[i], B_.sd[i]) for i in range(int(A.n)))
        L3same = same_lay(Lz, L3)
        wrong = Isl.loadLayout(lf, 778)
        wrong_err = str(Isl.LAST_ERR)
        RECS.clear()
        genS = U.allocateInstance(Gen.class_)
        LS = genS.layoutNow(777)
        E["mk_save"] = dict(saved=saved_ok, size=os.path.getsize(str(lf)) if os.path.isfile(str(lf)) else -1, same=L3same,
                            fromFile=None if L3 is None else bool(L3.fromFile), wrong=wrong is None, wrong_err=wrong_err,
                            reuse=[same_lay(Lz, LS), bool(LS.fromFile), bool(genS.laid), [x for x in logs() if "the saved island layout" in x][:1]],
                            name=os.path.basename(str(lf)))
        # a corrupt saved file: KEPT (never overwritten), the pick runs again (offline it fails) -> a FAILED layout, not cached
        cf = str(Isl.layoutFile(779))
        open(cf, "wb").write(b"junk")
        RECS.clear()
        genC = U.allocateInstance(Gen.class_)
        LC = genC.layoutNow(779)
        n_pick1 = len([x for x in logs() if "picking the islands failed" in x])
        fut = genC.generate(779, 0, 0, 0, None, None)
        fut_failed = bool(fut.isCompletedExceptionally())
        try:
            fut.get(5, JClass("java.util.concurrent.TimeUnit").SECONDS)
            fut_msg = "no error"
        except Exception as e_:
            fut_msg = str(e_)
        LC2 = genC.layoutNow(779)
        n_pick2 = len([x for x in logs() if "picking the islands failed" in x])
        genC.retryAt = 0
        LC3 = genC.layoutNow(779)
        n_pick3 = len([x for x in logs() if "picking the islands failed" in x])
        SysC = JClass("java.lang.System")
        E["mk_fail"] = dict(failed=bool(LC.failed), laid=bool(genC.laid), kept=open(cf, "rb").read() == b"junk",
                            unread=[x for x in logs() if "could not be read" in x and "KEPT" in x][:1], fut=[fut_failed, fut_msg[:200]],
                            cached=SysC.identityHashCode(LC2) == SysC.identityHashCode(LC), picks=[n_pick1, n_pick2, n_pick3],
                            retried=bool(LC3.failed) and SysC.identityHashCode(LC3) != SysC.identityHashCode(LC),
                            files=sorted(os.listdir(ldir)))
        # a failed pick with NO saved file never writes one
        genF = U.allocateInstance(Gen.class_)
        LF = genF.layoutNow(780)
        E["mk_fail"]["nofile"] = [bool(LF.failed), not os.path.exists(str(Isl.layoutFile(780))), sorted(os.listdir(ldir))]
        Isl.LAYDIR = None
        # ---- a SYNTHETIC chunk through maskWith (fake block ids: stone 7 = the seal + the only ore host, ground per zone 11-15)
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
        # LegacyModule stand-in: FluidSection's component type registered on the real ChunkStore.REGISTRY (0.5's MK recipe)
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
        GCc = JClass("com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk")
        ROOTS = 31 + int(Isl.D_ROOTS)
        CRACK = 31 + int(Isl.D_CRACK)

        Fill = JClass("skyywg06.Fill")

        def synth(cx, cz, ground, h):
            return Fill.make(cx, cz, ground, h)

        def survey(g, cx, cz, h, island_want):
            arr = list(Fill.dump(g))
            env = list(Fill.envs(g))
            r = dict(voidBad=0, belowBad=0, shellBad=0, roots=0, deco=0, decoBad=0, cracks=0, ores=0, oreBad=0, envBad=0, cols_in=0, cols_out=0,
                     oreIds=set(), decoIds=set())
            ndeco = 31 + len(list(Isl.DECO_NAMES))
            for lx in range(32):
                for lz in range(32):
                    x, z = cx * 32 + lx, cz * 32 + lz
                    ii = int(Isl.member(Lz, x + 0.5, z + 0.5, m1))
                    base = (lx * 32 + lz) * 320
                    col = arr[base:base + 320]
                    if ii < 0:
                        r["cols_out"] += 1
                        if any(col):
                            r["voidBad"] += 1
                        if env[lx * 32 + lz] != 99:
                            r["envBad"] += 1
                        continue
                    r["cols_in"] += 1
                    b = int(Isl.bottomOf(float(m1[0]), h, x + 0.5, z + 0.5))
                    for y in range(0, b):
                        if col[y] == ROOTS:
                            r["roots"] += 1
                        elif col[y] != 0:
                            r["belowBad"] += 1
                    if col[b] == 0 or col[b + 1] == 0:
                        r["shellBad"] += 1
                    for y in range(b, 320):
                        v = col[y]
                        if y < h - 1:
                            if v in (61, 62):
                                r["ores"] += 1
                                r["oreIds"].add(v)
                                if ii not in (3, 4) or y < 8 or y > 120:
                                    r["oreBad"] += 1
                            elif v != 7:
                                r["oreBad"] += 1
                        elif y == h - 1:
                            if v == CRACK:
                                r["cracks"] += 1
                            elif v != 11 + ii:
                                r["decoBad"] += 1
                        elif v != 0:
                            r["deco"] += 1
                            r["decoIds"].add(v)
                            if not (21 <= v < ndeco) or y > h + 16:
                                r["decoBad"] += 1
            r["oreIds"] = sorted(r["oreIds"])
            r["decoIds"] = sorted(r["decoIds"])
            return r
        res = {}
        # Zone 1 coast (east, through the radius cap), Zone 4 coast, Zone 5 interior (ores)
        z1x = int(math.floor((cen[0][0] + rad[0] - 10.0) / 32.0))
        cases = [("z1coast", z1x, 0, 0, 140), ("z1in", 3, 5, 0, 140), ("z4in", int(math.floor(cen[3][0] / 32.0)), int(math.floor(cen[3][1] / 32.0)), 3, 150),
                 ("z5in", int(math.floor(cen[4][0] / 32.0)), int(math.floor(cen[4][1] / 32.0)), 4, 170),
                 ("z2coast", int(math.floor((cen[1][0] + 870.0) / 32.0)), int(math.floor(cen[1][1] / 32.0)), 1, 140),
                 ("z3in", int(math.floor(cen[2][0] / 32.0)), int(math.floor(cen[2][1] / 32.0)), 2, 160)]
        for name, ccx, ccz, ii, h in cases:
            g = synth(ccx, ccz, 11 + ii, h)
            nin = int(Isl.maskWith(g, ccx, ccz, Lz, FlatH(h)))
            res[name] = dict(survey(g, ccx, ccz, h, ii), nin=nin)
        # every zone's decorations over more chunks (a pillar / boulder chance is ~0.1% per column)
        many = {}
        for ii in range(5):
            tot, ids, oids, on_ = 0, set(), set(), 0
            for k in range(6):
                ccx = int(math.floor(cen[ii][0] / 32.0)) + (k % 3) - 1
                ccz = int(math.floor(cen[ii][1] / 32.0)) + (k // 3)
                g = synth(ccx, ccz, 11 + ii, 150)
                Isl.maskWith(g, ccx, ccz, Lz, FlatH(150))
                s_ = survey(g, ccx, ccz, 150, ii)
                tot += s_["deco"] + s_["cracks"]
                ids |= set(s_["decoIds"])
                oids |= set(s_["oreIds"])
                on_ += s_["ores"]
            many[ii] = [tot, sorted(ids), on_, sorted(oids)]
        E["mk_chunk"] = dict(res=res, many=many, deco_n=int(Isl.DECO_N.get()), ore_n=int(Isl.ORE_N.get()))
        # emptyChunk / WgZoneFn failure path / WgZoneHop
        Fn, Hop = jc("new", "WgZoneFn"), jc("new", "WgZoneHop")
        genA = U.allocateInstance(Gen.class_)
        genA.lay = Lz
        genA.laid = True
        genA.lseed = 0
        RECS.clear()
        fn = Fn(genA, 0, z1x, 0)          # a coast chunk: its columns ask vanilla's height (the allocated generator throws)
        g0 = synth(fn.cx, fn.cz, 11, 140)
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
        fut = hop.apply(synth(9999, 9999, 11, 100))
        r1 = fut.get(30, JClass("java.util.concurrent.TimeUnit").SECONDS)
        hop2 = Hop(fn2, None, ex)
        r2 = hop2.apply(synth(9999, 9999, 11, 100)).get(30, JClass("java.util.concurrent.TimeUnit").SECONDS)
        ex.shutdown()
        e_bc = r1.getBlockChunk()
        E["mk_fn"] = dict(failed=failed, hopped=int(Isl.HOPPED.get()) - h0, empty1=all(int(e_bc.getBlock(0, y, 0)) == 0 for y in range(0, 320)),
                          empty2=all(int(r2.getBlockChunk().getBlock(5, y, 5)) == 0 for y in range(0, 320)))
        # the provider offline: the vanilla generator cannot load in a bare JVM -> SEVERE + WorldGenLoadException
        Prov = jc("new", "WgZoneProvider")
        RECS.clear()
        try:
            Prov().getGenerator()
            perr = "no error"
        except Exception as e_:
            perr = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
        E["mk_prov"] = [perr, [x for x in logs() if "could not be loaded for the zone islands world" in x][:1], Prov.CODEC is not None,
                        str(Prov().toString())]
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
        ZW, ZWU, ZWC = world(WN[2], U.allocateInstance(jc("new", "WgZoneProvider").class_))
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
        for i in range(3):
            Chk.OK[i] = True
        U1 = UUID.fromString("00000000-0000-0000-0000-0000000000e6")

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
        E["z1"] = [int(Open.decide(2, HUB))] + go(P, HUB, "3")
        P = on(ZW, ZWU)
        E["z2"] = [int(Open.decide(2, ZW))] + go(P, ZW, "2")
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
            return [bool(Cfg.NEW06), str(Cfg.LOADED)]
        E["z12"] = [apply("zones.islands06=false\n"), apply("zones.islands06=true\n"), apply("part.zones=true\n"), apply("zones.islands06=off\n")]
        Cfg.NEW06 = True
        Chk.OK[2] = False
        Isl.REGISTERED = False
        z13a = Chk.structureProblem(2)
        Isl.REGISTERED = True
        z13b = Chk.structureProblem(2)
        E["z13"] = [None if z13a is None else str(z13a), None if z13b is None else str(z13b)]
        Hk = jc("new", "WgHooks")
        E["z14"] = [str(Hk.customGet("info.zworld")), str(Hk.customGet("info.zsizes")), str(Hk.customGet("info.world"))]
        E["z15"] = [int(Zn.index(a)) for a in ("zones", "06", "world", "old", "classic", "1", "proof", "nope")] + [
            str(Zn.label(2)), bool(Zn.isIsland(2, ZW)), bool(Zn.isIsland(2, HUB)), int(Zn.islandIndex(ZW)), str(Zn.ringAt(2, 0.0, 0.0)),
            [str(x) for x in Zn.WORLDS], [str(x) for x in Zn.TEMPLATES], [str(x) for x in Zn.STRUCTURES]]
        ZWC.setSpawnProvider(GSP(TRF(5.5, 130.0, 5.5, 0.0, 0.0, 0.0)))
        E["z18"] = [bool(jc("new", "WgApplyLanding").applyTo(ZW)), Cfg.landing(2) is None]
        # d == 4 (no zone world loaded, no folder): the refusal / creation path as far as a bare JVM goes
        byname.remove(WN[2].lower())
        P = on(HUB, HUBU)
        try:
            d4 = int(Open.decide(2, HUB))
        except Exception as e_:
            d4 = "error " + str(e_)
        Arr = jc("new", "WgZoneArrive")
        Arr.HOPS.clear()
        E["z8"] = [d4] + go(P, HUB, "4")
        h8 = Arr.HOPS.get(str(U1))
        E["z8hop"] = None if h8 is None else [int(h8[0]), int(h8[1]) - int(JClass("java.lang.System").currentTimeMillis())]
        byname.put(WN[2].lower(), ZW)
        # ---- fix 4: the arrival hop (PlayerReadyEvent in the zone world -> moved on to the island asked for)
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
        Arr.HOPS.put(str(U1), JLongArr([3, nowms - 1]))
        P = on(ZW, ZWU)
        Arr().accept(ready(P))
        E["z20"] = [N["run_world"](ZW), N["tp_of"](P), int(Arr.HOPS.size())]
        Arr.HOPS.put(str(U1), JLongArr([2, nowms + 60000]))
        P = on(HUB, HUBU)
        Arr().accept(ready(P))
        E["z21"] = [N["run_world"](HUB), N["tp_of"](P), int(Arr.HOPS.size())]
        P = on(HUB, HUBU)
        go(P, HUB, "3")
        E["z22"] = int(Arr.HOPS.size())
        Arr.HOPS.clear()
        # the template through WorldConfig.load (our provider type registered on the engine codec like setup() does)
        tdir = os.path.join(SCRATCH, "tpl")
        os.makedirs(tdir, exist_ok=True)
        tp_ = os.path.join(tdir, "zones.bson")
        with zipfile.ZipFile(JAR) as zj:
            open(tp_, "wb").write(zj.read("Server/Instances/SkyWynn_Zones/instance.bson"))
        IWG = JClass("com.hypixel.hytale.server.core.universe.world.worldgen.provider.IWorldGenProvider")
        try:
            IWG.CODEC.register(str(Isl.TYPE), Prov.class_, Prov.CODEC)
            wc = WCFGc.load(Paths.get(tp_)).get(30, JClass("java.util.concurrent.TimeUnit").SECONDS)
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
            made = Store.createdText(jc("new", "WgZones").WORLDS[2])
            Pub.shutdown()
            a0 = snap(home)
            starts.append([sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), None if made is None else str(made), str(Cfg.LOADED)[:120],
                           bool(Cfg.NEW06)])
        E["st"] = [starts, len(snap(home)), "zones.islands06" in open(os.path.join(home, "config.properties"), encoding="latin-1").read()
                   if os.path.isfile(os.path.join(home, "config.properties")) else None]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    ml = E["mk_layout"]
    print("MK. synthetic layout: %s (%.1f s, %d samples)" % (ml["text"], ml["secs"], ml["calls"]))
    check(ml["found"] == [True] * 5 and ml["cls"] == [1, 2, 3, 4, 4] and ml["spawnCls"] == 1, "MK: the picker finds all 5 zones (classes 1,2,3,4,4): %s" % ml["found"])
    c = ml["cen"]
    check(c[0] == [0.5, 0.5], "MK: Zone 1 = the spawn point: %s" % c[0])
    check(math.hypot(c[1][0] - 4000.0, c[1][1]) < 900 and math.hypot(c[2][0], c[2][1] - 4500.0) < 1000 and math.hypot(c[3][0] + 4200.0, c[3][1]) < 700
          and math.hypot(c[4][0], c[4][1] + 4200.0) < 600, "MK: Zones 2-5 sit in their own class's land (Zone 5 = the second class-4 land, never the "
          "too-shallow islet): %s" % c[1:])
    check(ml["gaps"] == [1100.0] * 5, "MK: every island placed with the full 1,100-block gap: %s" % ml["gaps"])
    pair = min(math.hypot(c[i][0] - c[j][0], c[i][1] - c[j][1]) - ml["rad"][i] - ml["rad"][j] for i in range(5) for j in range(i + 1, 5))
    check(pair >= 1100.0 - 1e-6, "MK: radius circles at least 1,100 apart: %.0f" % pair)
    check(ml["holes"][0] >= 1 and ml["filled"][0] >= 1, "MK: Zone 1 keeps the big desert as a void hole and fills the small lake: holes %s filled %s"
          % (ml["holes"], ml["filled"]))
    mm = E["mk_member"]
    check(mm["tested"] > 2500 and mm["nbad"] == 0, "MK: membership = the map's truth at %d points away from coasts (radius cap, foreign hole, "
          "filled lake, the islet, every island): %d wrong %s" % (mm["tested"], mm["nbad"], mm["bad"]))
    check(all(x > 0 for x in mm["insides"]) and mm["lake"] == 0 and mm["desert"] == -1, "MK: points on every island %s; the lake centre is land "
          "(%d), the desert centre void (%d)" % (mm["insides"], mm["lake"], mm["desert"]))
    check(E["mk_bottom"]["nbad"] == 0, "MK: bottomOf = the independent formula (skirt, rough, drips, min thickness, keel) on 3,000 points: %s"
          % E["mk_bottom"]["bad"])
    mo = E["mk_outside"]
    check(mo["chunks"] >= 100 and mo["bad"] == [] and mo["skipped"] > 0 and mo["far"], "MK: chunkOutside never skips a chunk holding an island "
          "column (%d coast chunks, %d skipped, all truly void) and skips a chunk far in the void: %s" % (mo["chunks"], mo["skipped"], mo["bad"]))
    check(E["mk_det"], "MK: the layout is deterministic (same map -> same centres + identical coast grids)")
    ms_ = E["mk_save"]
    check(ms_["saved"] and ms_["size"] > 1000 and ms_["same"] and ms_["fromFile"] and ms_["wrong"] and "seed 777" in ms_["wrong_err"]
          and ms_["name"] == "zone_layout_777.bin", "MK (fix 3): the island layout saves to zone_layout_<seed>.bin (%d bytes) and loads back "
          "IDENTICAL (centres, radii, every coast grid); a file for another seed is refused (%s)" % (ms_["size"], ms_["wrong_err"]))
    check(ms_["reuse"][0] and ms_["reuse"][1] and ms_["reuse"][2] and ms_["reuse"][3], "MK (fix 3): a fresh generator with NO vanilla zone map "
          "(= a later boot after a vanilla patch) reuses the saved layout unchanged - nothing re-read from vanilla: %s" % ms_["reuse"])
    mf_ = E["mk_fail"]
    check(mf_["failed"] and not mf_["laid"] and mf_["kept"] and mf_["unread"], "MK (fix 3): an unreadable saved layout is KEPT (not overwritten) "
          "+ one SEVERE, the pick runs again: %s" % {k: mf_[k] for k in ("failed", "laid", "kept", "unread")})
    check(mf_["fut"][0] and "no island layout" in mf_["fut"][1], "MK (fix 2): with no layout, generate() returns a FAILED future (the engine "
          "retries the chunk; no void chunk is saved): %s" % mf_["fut"])
    check(mf_["cached"] and mf_["picks"][0] == 1 and mf_["picks"][1] == 1 and mf_["picks"][2] == 2 and mf_["retried"],
          "MK (fix 2): a failed pick is NOT cached as the world's layout - inside the 15 s back-off the same failed result, after it a new pick: "
          "%s" % mf_["picks"])
    check(mf_["nofile"][0] and mf_["nofile"][1] and mf_["files"] == ["zone_layout_777.bin", "zone_layout_779.bin"],
          "MK (fix 2/3): a failed pick never writes a layout file: %s / %s" % (mf_["nofile"], mf_["files"]))
    res = E["mk_chunk"]["res"]
    for name, r in sorted(res.items()):
        print("MK. synthetic chunk %s: %s" % (name, dict((k, v) for k, v in r.items() if k not in ("decoIds", "oreIds"))))
        check(r["voidBad"] == 0 and r["belowBad"] == 0 and r["shellBad"] == 0 and r["envBad"] == 0 and r["decoBad"] == 0 and r["oreBad"] == 0,
              "MK: maskWith on the synthetic chunk %s: void columns empty + Env_Void, nothing under the underside but roots, the 2-block shell, "
              "decorations only on the zone's ground into air (or a crack in the ground), ores only Zone 4-5 host rock: %s" % (name, r))
    check(res["z1coast"]["cols_in"] > 0 and res["z1coast"]["cols_out"] > 0, "MK: the Zone 1 coast chunk holds land and void: %s / %s"
          % (res["z1coast"]["cols_in"], res["z1coast"]["cols_out"]))
    many_ = E["mk_chunk"]["many"]
    check(all(res[k]["ores"] > 0 for k in ("z4in", "z5in")) and all(res[k]["ores"] == 0 for k in res if k not in ("z4in", "z5in"))
          and all(many_[str(k)][3] == [61, 62] for k in (3, 4)) and all(many_[str(k)][2] == 0 for k in (0, 1, 2)),
          "MK (fix 1): Onyxium + Mithril veins in the rock of the Zone 4 AND Zone 5 islands (both ores on each over 6 chunks), none on Zones 1-3: %s; "
          "6-chunk ores per island %s" % (dict((k, res[k]["ores"]) for k in res), dict((k, many_[k][2:]) for k in many_)))
    many = E["mk_chunk"]["many"]
    check(all(many[k][0] > 0 for k in many), "MK: decorations on every zone's island (6 chunks each): %s" % dict((k, v[0]) for k, v in many.items()))
    check(any(res[k]["roots"] > 0 for k in ("z1coast", "z2coast")), "MK: hanging roots under a Zone 1-2 rim: %s" % dict((k, res[k]["roots"]) for k in res))
    check(res["z4in"]["cracks"] + res["z5in"]["cracks"] > 0, "MK: lava cracks in the volcanic ground of Zones 4-5: %s / %s"
          % (res["z4in"]["cracks"], res["z5in"]["cracks"]))
    f = E["mk_fn"]
    check(f["failed"][0] == 1 and f["failed"][1] and f["failed"][2] and f["failed"][3] == "not a chunk", "MK (fix 2): WgZoneFn - a mask failure "
          "THROWS (= a failed future: the engine logs it, backs off and generates the chunk again; nothing saved, never a permanent void hole) + one "
          "SEVERE; a non-chunk passes through: %s" % f["failed"])
    check(f["hopped"] == 1 and f["empty1"] and f["empty2"], "MK: WgZoneHop - on the caller's thread the mask hops to the pool (1 hop), elsewhere it "
          "runs in place; both masked a void chunk empty: %s" % f)
    p = E["mk_prov"]
    check(p[0] == "com.hypixel.hytale.server.core.universe.world.worldgen.WorldGenLoadException" and p[1] and p[2] and "SkyWynnZones" in p[3],
          "MK: WgZoneProvider offline - the vanilla generator cannot load in a bare JVM: its SEVERE + WorldGenLoadException; the codec: %s" % p)
    # ---- Z
    z1 = E["z1"]
    check(z1[0] == 1 and "Teleporting to the Zone 3 island (Whisperfrost Frontiers) in the zone islands world..." in z1[2],
          "Z: /zone 3 from the main world (zone world loaded): decide 1, the landing computed, up to the engine's teleport call: %s" % z1)
    z2 = E["z2"]
    lz = E["mk_layout"]["lands"][1]
    check(z2[0] == 2 and z2[1] == ["skywynn_zones", math.floor(lz[0]) + 0.5, 122.0, math.floor(lz[1]) + 0.5] and "Teleporting to the Zone 2 island" in z2[2],
          "Z: /zone 2 on the zone world: a Teleport to the Zone 2 landing (ground fallback 120 + 2 offline): %s" % z2)
    check(E["z3"][0] is None and "has no Zone 5 island" in E["z3"][1], "Z: a seed with no Zone 5 island -> refused in plain words: %s" % E["z3"])
    check(E["z4a"][0] is None and "switched off" in E["z4a"][1], "Z: 0.6 switch OFF - /zone 3 refused: %s" % E["z4a"][1])
    check(E["z4b"][0] == ["skywynn_z1", 0.5, 144.0, 344.5] and "Back to the landing point" in E["z4b"][1], "Z: 0.6 switch OFF - /zone 1 = the old "
          "test island (its landing): %s" % E["z4b"])
    check(E["z5"][0] == ["skywynn_z1", 0.5, 144.0, 344.5], "Z: /zone old = the old test island with the switch on: %s" % E["z5"])
    check(E["z6"][0] == ["skywynn_zones", 0.5, 122.0, 0.5] and "Zone 1 island" in E["z6"][1], "Z: /zone world = the Zone 1 island landing (the spawn): %s" % E["z6"])
    l4 = E["mk_layout"]["lands"][3]
    check(E["z6b"][0] == ["skywynn_zones", math.floor(l4[0]) + 0.5, 122.0, math.floor(l4[1]) + 0.5], "Z: /zone z4 = the Zone 4 landing: %s" % E["z6b"])
    check(E["z7"][0] is None and "There is no zone '9'" in E["z7"][1], "Z: /zone 9 - the zone list: %s" % E["z7"][1])
    z9 = " | ".join(E["z9"])
    check("The Zone islands world (world 'skywynn_zones')" in z9 and "Islands: Zone 1 Emerald Wilds at 1 1" in z9 and "Generator SkyWynnZones" in z9
          and "one floating island per zone" in z9, "Z: /zone info on the zone world: %s" % z9[:600])
    check("no landing point to set" in E["z10"], "Z: /zone setlanding refused on the zone world: %s" % E["z10"])
    l_on, l_off = " | ".join(E["z11"][0]), " | ".join(E["z11"][1])
    check("/zone old  Zone 1 - Emerald Wilds" in l_on and "/zone world  The Zone islands world" in l_on and "the Zone 1-5 islands of world skywynn_zones" in l_on
          and "/zone 1  Zone 1 - Emerald Wilds" in l_off and "are OFF" in l_off, "Z: /zone lists the zone world + /zone old (on) / /zone 1 (off): %s || %s"
          % (l_on[:400], l_off[:300]))
    z12 = E["z12"]
    check([x[0] for x in z12] == [False, True, True, False] and "old test island" in z12[0][1] and "0.6 zone islands world" in z12[1][1],
          "Z: WgCfg.apply - zones.islands06 false / true / missing (= true) / off: %s" % z12)
    check(E["z13"][0] is not None and "not registered" in E["z13"][0] and E["z13"][1] is None, "Z: WgCheck - the zone type unregistered -> refused, "
          "registered -> ok: %s" % E["z13"])
    check(E["z14"][0] == "skywynn_zones (seed %d)" % ZSEED and "Zone 5 r900" in E["z14"][1] and E["z14"][2] == "skywynn_z1", "Z: the read-only "
          "Server Setup rows: %s" % E["z14"])
    z15 = E["z15"]
    check(z15[:8] == [2, 2, 2, 0, 0, 0, 1, -1] and z15[8] == "The Zone islands world" and z15[9] and not z15[10] and z15[11] == 2
          and z15[13] == ["skywynn_z1", "skywynn_proof2", "skywynn_zones"] and z15[14][2] == "SkyWynn_Zones" and z15[15][2] == "SkyWynnZones",
          "Z: WgZones - index aliases, label, isIsland only for the zone provider, the third world: %s" % z15)
    check(E["z18"] == [False, True], "Z: WgApplyLanding leaves the zone world's spawn alone (no landing point): %s" % E["z18"])
    print("Z. d == 4 path offline: %s; hop recorded %s" % (E["z8"], E["z8hop"]))
    if E["z8"][2] and "Creating the zone islands world" in E["z8"][2]:
        check(E["z8hop"] is not None and E["z8hop"][0] == 3 and 290000 < E["z8hop"][1] <= 300000 and "moved on to Zone 4" in E["z8"][2],
              "Z (fix 4): /zone 4 while the world is still being made records the hop to Zone 4 (5 min) and says so: %s / %s" % (E["z8hop"], E["z8"][2]))
    else:
        check(E["z8hop"] is None, "Z (fix 4): /zone 4 that could not start a trip records no hop: %s" % (E["z8hop"],))
    l4_ = E["mk_layout"]["lands"][3]
    z19 = E["z19"]
    check(z19[0] == 1 and z19[1] == ["skywynn_zones", math.floor(l4_[0]) + 0.5, 122.0, math.floor(l4_[1]) + 0.5] and "Moving you on to the Zone 4 island"
          in z19[2] and z19[3] == 0 and z19[4] == 1, "Z (fix 4): arriving in the zone world with a recorded hop -> one world-thread task, a Teleport to "
          "the Zone 4 landing, the hop used up: %s" % z19)
    check(E["z20"] == [0, None, 0], "Z (fix 4): an expired hop (older than 5 min) is dropped, no move: %s" % E["z20"])
    check(E["z21"] == [0, None, 1], "Z (fix 4): arriving in ANOTHER world keeps the hop for the zone world arrival: %s" % E["z21"])
    check(E["z22"] == 0, "Z (fix 4): a new /zone command clears an old hop: %s" % E["z22"])
    q = E["qz"]
    if q and q[0] != "error":
        check(q[0] == PKG + "WgZoneProvider" and q[1] == ZSEED and q[2] == "SkyWynn - zone islands" and q[3] and q[4] == "Adventure",
              "QZ: the SkyWynn_Zones template decodes through WorldConfig.load: WgZoneProvider, seed %d, no spawn provider, Adventure: %s" % (ZSEED, q))
    else:
        NOTES.append("QZ: the template decode needs more engine set-up offline (%s) - covered by VP's saved config decode on the real server" % (q,))
    st, nfiles, has6 = E["st"]
    check(len(st) == 2 and all(s_[0] == [] for s_ in st) and st[0][1:] == st[1][1:] and st[0][3] is True and has6 is False,
          "ST: two starts on a COPY of the live Skyy_SkyyWorldGen (%d files): no file changed (the new row is NOT written into the existing "
          "config - its default 'on' applies), the same state read: %s" % (nfiles, st))


PROBE_SRC = r'''# The SkyyWgProbe6 test plugin (NEVER shipped): built into a scratch jar, run next to SkyyWorldGen 0.6 on an OFFLINE server started by
# tools/smoke_test.py. It creates the zone islands world through SkyyWorldGen's own /zone code, checks the island layout picked from the
# REAL vanilla 0.7 zone map, generates sample chunks with the REAL wrapped generator AND a plain vanilla generator of the same seed,
# compares them voxel by voxel and logs the results.
PROBE_VERSION = "0.6"
PROBE_PKG = "com.skyy.wgprobe6"
W = "com.skyy.worldgen."
GC = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"
GBC = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedBlockChunk"
FS = "com.hypixel.hytale.server.core.universe.world.chunk.section.FluidSection"
HOLD = "com.hypixel.hytale.component.Holder"
CG = "com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
TRF = "com.hypixel.hytale.math.vector.Transform"
CF = "java.util.concurrent.CompletableFuture"
EWE = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedEntityChunk$EntityWrapperEntry"
BT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
FL = "com.hypixel.hytale.server.core.asset.type.fluid.Fluid"
ZL = W + "WgZoneLayout"
ZI = W + "WgZoneIsles"
VORES = ["Ore_Copper_Stone", "Ore_Iron_Stone", "Ore_Gold_Stone", "Ore_Silver_Stone", "Ore_Thorium_Sandstone", "Ore_Cobalt_Shale",
         "Ore_Adamantite_Magma_Cracked", "Ore_Iron_Volcanic", "Ore_Gold_Volcanic", "Ore_Silver_Volcanic", "Ore_Copper_Sandstone",
         "Ore_Iron_Sandstone", "Ore_Cobalt_Slate_Cracked", "Ore_Iron_Basalt", "Ore_Copper_Shale", "Ore_Iron_Shale", "Ore_Gold_Sandstone",
         "Ore_Silver_Sandstone", "Ore_Gold_Calcite", "Ore_Iron_Basalt_Cracked", "Ore_Adamantite_Magma"]

PROBE_METHODS = [
    r"""
public static void log(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyWgProbe6] " + m); else System.out.println("[SkyyWgProbe6] " + m); } catch (Throwable t) { }
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
    r"""public static int bid(String n) { try { return %(BT)s.getAssetMap().getIndexOrDefault(n, -1); } catch (Throwable t) { return -1; } }""",
    r"""
public static boolean in(int[] a, int v) {
  if (a == null || v <= 0) return false;
  for (int i = 0; i < a.length; i++) if (a[i] == v) return true;
  return false;
}""",
    # the column plan: [0..1155] bottom (100000 = void), [1156..] ground h, [2312..] island index, using the mask's own maths
    r"""
public static int[] plan(%(W)sWgZoneGen g, %(ZL)s L, int seed, int cx, int cz) {
  int[] p = new int[34 * 34 * 3];
  double[] m = new double[1];
  for (int i = 0; i < 34; i++) for (int k = 0; k < 34; k++) {
    int x = cx * 32 + i - 1;
    int z = cz * 32 + k - 1;
    int idx = i * 34 + k;
    int ii = %(ZI)s.member(L, x + 0.5, z + 0.5, m);
    p[2 * 34 * 34 + idx] = ii;
    if (ii >= 0) {
      int h = g.getHeight(seed, x, z);
      p[idx] = %(ZI)s.bottomOf(m[0], h, x + 0.5, z + 0.5);
      p[34 * 34 + idx] = h;
    } else p[idx] = 100000;
  }
  return p;
}""",
    # st: 0 outsideBad 1 belowBad 2 changedBad 3 sealed 4 identical 5 exposedFluid 6 shellBad 7 lavaKept 8 fluidKept 9 deco 10 insideCols
    #     11 outsideCols 12 ore 13 entsOutside 14 entsMasked 15 entsVanilla 16 envBad 17 rootsBelow 18 caveAir 19 vanillaOres 20 surface
    #     21 onyx 22 mithril 23 decoOutsideZone
    # pi (per island, stride 8): 0 cols 1 deco 2 ore 3 lava 4 vanillaOres 5 surface 6 caveAir 7 sealed
    r"""
public static void cmp(%(GC)s m, %(GC)s r, int[] p, int lava1, int lava2, int stone, int envVoid, int[] vores, long[] st, long[] pi, int cx, int cz) {
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
      for (int y = 0; y < 320; y++) {
        if (mb.getBlock(lx, y, lz) != 0 || fl(mf, lx, y, lz) != e) { st[0]++; break; }
      }
      if (envVoid >= 0 && mb.getEnvironment(lx, 200, lz) != envVoid) st[16]++;
      continue;
    }
    st[10]++;
    int ii = p[2 * 34 * 34 + idx];
    int h = p[34 * 34 + idx];
    pi[ii * 8]++;
    for (int y = 0; y < 320; y++) {
      int a = mb.getBlock(lx, y, lz);
      int fa = fl(mf, lx, y, lz);
      int c = rb.getBlock(lx, y, lz);
      int fc = fl(rf, lx, y, lz);
      if (y < b) {
        if (a == roots && roots > 0 && fa == e) { st[17]++; continue; }
        if (a != 0 || fa != e) st[1]++;
        continue;
      }
      if (a == c && fa == fc) {
        st[4]++;
        if (in(vores, a)) { st[19]++; pi[ii * 8 + 4]++; }
        if (a != 0 && y > h) { st[20]++; pi[ii * 8 + 5]++; }
        if (a == 0 && fa == e && y < h - 8 && y > b + 2) { st[18]++; pi[ii * 8 + 6]++; }
      } else if (a == stone && fa == e && (c == 0 || fc != e)) { st[3]++; pi[ii * 8 + 7]++; }
      else if (fa == e && fc == e && c == 0 && (in(deco, a) || in(flw, a))) { st[9]++; pi[ii * 8 + 1]++; }
      else if (fa == e && a == crack && crack > 0 && c != 0) { st[9]++; pi[ii * 8 + 1]++; }
      else if (fa == e && in(ore, a) && in(host, c)) {
        st[12]++; pi[ii * 8 + 2]++;
        if (a == ore[0]) st[21]++; else st[22]++;
      } else {
        st[2]++;
        if (st[2] <= 12L) log("CHANGED chunk " + cx + " " + cz + " local " + lx + " " + y + " " + lz + " island " + ii + ": masked block " + a + " " + nm(a) + " fluid " + fa + ", vanilla block " + c + " " + nm(c) + " fluid " + fc + " (bottom " + b + ", ground " + h + ", vanilla below " + nm(rb.getBlock(lx, Math.max(0, y - 1), lz)) + ", masked below " + nm(mb.getBlock(lx, Math.max(0, y - 1), lz)) + ")");
      }
      if (fa != e) {
        st[8]++;
        if (fa == lava1 || fa == lava2) { st[7]++; pi[ii * 8 + 3]++; }
        boolean ex = y - 1 < b || y < p[idx - 34] || y < p[idx + 34] || y < p[idx - 1] || y < p[idx + 1];
        if (ex) st[5]++;
      }
    }
    if (mb.getBlock(lx, b, lz) == 0 || (b + 1 < 320 && mb.getBlock(lx, b + 1, lz) == 0)) st[6]++;
  }
  java.util.Iterator it = m.getEntityChunk().getEntities().iterator();
  double[] mm = new double[1];
  while (it.hasNext()) {
    %(EWE)s w = (%(EWE)s) it.next();
    st[14]++;
    org.joml.Vector3i v = w.offset();
    if (%(ZI)s.member(LAY, v.x + 0.5, v.z + 0.5, mm) < 0) st[13]++;
  }
  st[15] += r.getEntityChunk().getEntities().size();
}""",
    r"""
public static void one(%(W)sWgZoneGen g, %(CG)s v, %(ZL)s L, int seed, int cx, int cz, int lava1, int lava2, int stone, int envVoid, int[] vores, long[] st, long[] tm, long[] pi) throws Throwable {
  long idx = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cx, cz);
  long t0 = System.nanoTime();
  %(GC)s m = (%(GC)s) g.generate(seed, idx, cx, cz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  long t1 = System.nanoTime();
  %(GC)s r = (%(GC)s) v.generate(seed, idx, cx, cz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
  long t2 = System.nanoTime();
  tm[0] += t1 - t0; tm[1] += t2 - t1; tm[2]++;
  if (m == null || r == null) { fail("chunk " + cx + " " + cz + ": a null chunk (masked " + (m == null) + ", vanilla " + (r == null) + ")"); return; }
  int[] p = plan(g, L, seed, cx, cz);
  long[] s1 = new long[st.length];
  cmp(m, r, p, lava1, lava2, stone, envVoid, vores, s1, pi, cx, cz);
  for (int i = 0; i < st.length; i++) st[i] += s1[i];
  if (s1[0] + s1[1] + s1[2] + s1[5] + s1[6] + s1[13] + s1[16] > 0) fail("chunk " + cx + " " + cz + ": outsideBad " + s1[0] + " belowBad " + s1[1] + " changedBad " + s1[2] + " exposedFluid " + s1[5] + " shellBad " + s1[6] + " entsOutside " + s1[13] + " envBad " + s1[16]);
}""",
    # sample chunks per island: the landing, the coast in 4 directions (+ 40 blocks inland = the skirt), 2 interior points;
    # Zone 5: 8 more around its landing (ore counts)
    r"""
public static int[] samples(%(ZL)s L) {
  java.util.ArrayList l = new java.util.ArrayList();
  double[] m = new double[1];
  int[] dx = new int[] { 1, 0, 0, 0 };
  for (int i = 0; i < L.n; i++) {
    if (!L.found[i]) continue;
    double x0 = Math.floor(L.lx[i]) + 0.5;
    double z0 = Math.floor(L.lz[i]) + 0.5;
    l.add(new int[] { (int) Math.floor(x0 / 32.0), (int) Math.floor(z0 / 32.0) });
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
    if (i == 4) {
      for (int a = 0 - 1; a <= 1; a++) for (int b = 0 - 1; b <= 1; b++) if (a != 0 || b != 0) l.add(new int[] { (int) Math.floor((x0 + a * 96.0) / 32.0), (int) Math.floor((z0 + b * 96.0) / 32.0) });
    }
  }
  java.util.LinkedHashSet seen = new java.util.LinkedHashSet();
  java.util.ArrayList out = new java.util.ArrayList();
  for (int j = 0; j < l.size(); j++) {
    int[] c = (int[]) l.get(j);
    String k = c[0] + "," + c[1];
    if (seen.add(k)) out.add(c);
  }
  int[] r = new int[out.size() * 2];
  for (int j = 0; j < out.size(); j++) { int[] c = (int[]) out.get(j); r[2 * j] = c[0]; r[2 * j + 1] = c[1]; }
  return r;
}""",
    # the largest distance of an island's land from its centre (grid cells inside)
    r"""
public static double ext(%(ZL)s L, int i) {
  float[] s = L.sd[i];
  int n = L.gn[i];
  double mx = 0.0;
  for (int p = 0; p < s.length; p++) {
    if (s[p] <= 0.0f) continue;
    double x = L.gx0[i] + (p %% n) * 8.0 - L.cx[i];
    double z = L.gz0[i] + (p / n) * 8.0 - L.cz[i];
    double d = Math.sqrt(x * x + z * z);
    if (d > mx) mx = d;
  }
  return mx + 8.0;
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
    log("default world '" + d.getName() + "' up - creating the zone islands world through SkyyWorldGen's /zone code (WgOpen.startCreate)");
    check(%(ZI)s.REGISTERED, "SkyyWorldGen registered the generator type " + %(ZI)s.TYPE);
    check(%(W)sWgCheck.structureProblem(2) == null && %(W)sWgCheck.templateOk(2), "WgCheck: /zone 1-5 may open (type registered, template in the jar)");
    int dec = %(W)sWgOpen.decide(2, d);
    check(dec == 4, "decide(zones) on a fresh copy = 4 (create): " + dec);
    long tc = System.currentTimeMillis();
    %(CF)s f = %(W)sWgOpen.startCreate(2, d, new %(TRF)s(0.0, 100.0, 0.0), null);
    %(WLD)s w = (%(WLD)s) f.get(300L, java.util.concurrent.TimeUnit.SECONDS);
    log("TIME world created in " + (System.currentTimeMillis() - tc) + " ms");
    check(w != null && w.getName().equals("skywynn_zones"), "the zone islands world exists: " + (w == null ? null : w.getName()));
    check(%(W)sWgZones.isIsland(2, w) && %(W)sWgZones.islandIndex(w) == 2, "WgZones: the new world is THE zone islands world (its provider is WgZoneProvider)");
    %(W)sWgZoneGen g = %(ZI)s.genOf(w);
    check(g != null, "the world's chunk generator is WgZoneGen (a vanilla ChunkGenerator subclass): " + (w.getChunkStore().getGenerator() == null ? null : w.getChunkStore().getGenerator().getClass().getName()));
    if (g == null) return;
    int seed = (int) w.getWorldConfig().getSeed();
    check(seed == %(SEED)d, "the world seed = the template's " + seed);
    %(ZL)s L = g.layoutNow(seed);
    LAY = L;
    java.nio.file.Path lfile = %(ZI)s.layoutFile(seed);
    check(!L.fromFile && lfile != null && java.nio.file.Files.isRegularFile(lfile, new java.nio.file.LinkOption[0]), "fix 3: the first pick on the real server is saved: " + lfile);
    log("LAYOUT " + %(ZI)s.layoutText(L));
    int nf = 0;
    for (int i = 0; i < L.n; i++) if (L.found[i] && L.sd[i] != null) nf++;
    check(nf == 5, "the picker found an island for every zone 1-5 on the REAL vanilla 0.7 map: " + nf);
    check(L.spawnCls == 1, "the vanilla spawn point stands on Zone 1 land (class " + L.spawnCls + ")");
    double minGap = 1.0E9;
    String gaps = "";
    for (int i = 0; i < L.n; i++) for (int j = i + 1; j < L.n; j++) {
      if (!L.found[i] || !L.found[j]) continue;
      double dx = L.cx[i] - L.cx[j];
      double dz = L.cz[i] - L.cz[j];
      double gap = Math.sqrt(dx * dx + dz * dz) - ext(L, i) - ext(L, j);
      gaps = gaps + " " + (i + 1) + "-" + (j + 1) + ":" + Math.round(gap);
      if (gap < minGap) minGap = gap;
    }
    log("GAPS land-to-land lower bounds:" + gaps);
    check(minGap >= 900.0, "void between every two islands (land to land, lower bound) >= 900 blocks: min " + Math.round(minGap));
    for (int i = 0; i < L.n; i++) check(L.gapUsed[i] >= %(ZI)s.GAP, "Zone " + (i + 1) + " placed with the full gap (no fallback): " + L.gapUsed[i]);
    %(W)sWgZoneSampler smp = new %(W)sWgZoneSampler(g.getZonePatternGenerator(seed), seed, g.getZonePatternProvider().getZones());
    for (int i = 0; i < L.n; i++) {
      if (!L.found[i]) continue;
      float[] s = L.sd[i];
      int n = L.gn[i];
      long inside = 0L;
      long same = 0L;
      for (int p = 0; p < s.length; p += 3) {
        if (s[p] <= 0.0f) continue;
        inside++;
        if (smp.applyAsInt(L.gx0[i] + (p %% n) * 8, L.gz0[i] + (p / n) * 8) == L.cls[i]) same++;
      }
      double pur = inside == 0L ? 0.0 : (double) same / (double) inside;
      log("ISLAND " + (i + 1) + " " + %(ZI)s.Z_NAMES[i] + ": centre " + Math.round(L.cx[i]) + " " + Math.round(L.cz[i]) + ", land " + L.area[i] + " m2, extent " + Math.round(ext(L, i)) + ", max depth " + Math.round(L.maxsd[i]) + ", filled cells " + L.filled[i] + ", void holes " + L.holes[i] + ", purity " + Math.round(pur * 1000.0) / 10.0 + "%%");
      check(pur >= 0.97, "Zone " + (i + 1) + " island = its own vanilla zone's land (purity >= 97%%): " + Math.round(pur * 1000.0) / 10.0 + "%%");
      check(L.area[i] >= 200000L, "Zone " + (i + 1) + " island has real size (>= 0.2 km2): " + L.area[i] + " m2");
      %(TRF)s lt = g.landingOf(seed, i);
      double[] mm = new double[1];
      int li = lt == null ? -1 : %(ZI)s.member(L, lt.getPosition().x, lt.getPosition().z, mm);
      check(lt != null && li == i, "Zone " + (i + 1) + " landing (/zone " + (i + 1) + ") stands on its own island: " + (lt == null ? null : lt.getPosition()) + " island " + li);
      LANDS[i] = lt;
    }
    %(TRF)s sp = (%(TRF)s) w.getWorldConfig().getSpawnProvider().getSpawnPointAsync(w, java.util.UUID.randomUUID()).get(60L, java.util.concurrent.TimeUnit.SECONDS);
    double[] m0 = new double[1];
    check(sp != null && %(ZI)s.member(L, sp.getPosition().x, sp.getPosition().z, m0) == 0, "the world spawn point (vanilla's own provider) stands on the Zone 1 island: " + (sp == null ? null : sp.getPosition()));
    %(CG)s v = (%(CG)s) new com.hypixel.hytale.server.worldgen.HytaleWorldGenProvider().getGenerator();
    int lava1 = %(FL)s.getAssetMap().getIndexOrDefault("Lava_Source", -9);
    int lava2 = %(FL)s.getAssetMap().getIndexOrDefault("Lava", -9);
    int stone = bid("Rock_Stone");
    int envVoid = com.hypixel.hytale.server.core.asset.type.environment.config.Environment.getAssetMap().getIndexOrDefault("Env_Void", -9);
    int[] vores = new int[VORE_NAMES.length];
    for (int i = 0; i < vores.length; i++) vores[i] = bid(VORE_NAMES[i]);
    %(ZI)s.ids();
    int miss = 0;
    for (int i = 0; i < %(ZI)s.DECO.length; i++) if (%(ZI)s.DECO[i] <= 0) { miss++; log("MISSING deco block " + %(ZI)s.DECO_NAMES[i]); }
    for (int i = 0; i < %(ZI)s.ORE.length; i++) if (%(ZI)s.ORE[i] <= 0) { miss++; log("MISSING ore block " + %(ZI)s.ORE_NAMES[i]); }
    check(miss == 0, "every decoration + ore block id is loaded on the real server (incl. our Ore_Onyxium_SkyWynn): " + miss + " missing");
    long[] st = new long[24];
    long[] tm = new long[3];
    long[] pi = new long[40];
    int[] cs = samples(L);
    log("sampling " + (cs.length / 2) + " chunks");
    for (int i = 0; i + 1 < cs.length; i += 2) one(g, v, L, seed, cs[i], cs[i + 1], lava1, lava2, stone, envVoid, vores, st, tm, pi);
    log("STATS chunks " + tm[2] + " outsideBad " + st[0] + " belowBad " + st[1] + " changedBad " + st[2] + " sealed " + st[3] + " identical " + st[4] + " exposedFluid " + st[5] + " shellBad " + st[6] + " lavaKept " + st[7] + " fluidKept " + st[8] + " deco " + st[9] + " insideCols " + st[10] + " outsideCols " + st[11] + " ore " + st[12] + " entsOutside " + st[13] + " entsMasked " + st[14] + " entsVanilla " + st[15] + " envBad " + st[16] + " rootsBelow " + st[17] + " caveAir " + st[18] + " vanillaOres " + st[19] + " surface " + st[20] + " onyx " + st[21] + " mithril " + st[22]);
    for (int i = 0; i < 5; i++) log("PERISLAND " + (i + 1) + " cols " + pi[i * 8] + " deco " + pi[i * 8 + 1] + " ore " + pi[i * 8 + 2] + " lava " + pi[i * 8 + 3] + " vanillaOres " + pi[i * 8 + 4] + " surface " + pi[i * 8 + 5] + " caveAir " + pi[i * 8 + 6] + " sealed " + pi[i * 8 + 7]);
    log("TIME masked " + (tm[0] / Math.max(1L, tm[2]) / 1000000L) + " ms avg, vanilla " + (tm[1] / Math.max(1L, tm[2]) / 1000000L) + " ms avg over " + tm[2] + " chunks");
    check(st[0] == 0L && st[1] == 0L && st[13] == 0L && st[16] == 0L, "outside the islands / under the underside: nothing left (blocks, fluid, entity groups; only hanging roots under a rim), Env_Void");
    check(st[2] == 0L, "inside the islands every voxel is vanilla's own, sealing stone, a decoration on vanilla air, a lava crack on vanilla ground or a Zone 5 ore in vanilla rock");
    check(st[5] == 0L && st[6] == 0L, "sealed: no kept fluid beside / over the void, the 2 bottom blocks of every island column solid");
    check(st[10] > 5000L && st[11] > 2000L && st[4] > 1000000L, "the sample covers island and void columns: " + st[10] + " / " + st[11]);
    int deco5 = 0;
    int feat5 = 0;
    for (int i = 0; i < 5; i++) {
      if (pi[i * 8 + 1] > 0L) deco5++;
      if (pi[i * 8 + 5] > 0L && pi[i * 8 + 6] > 0L && pi[i * 8 + 4] > 0L) feat5++;
    }
    check(deco5 == 5, "richer looks: decorations placed on EVERY island (vanilla blocks): " + deco5 + " / 5");
    check(feat5 == 5, "vanilla features on EVERY island: vanilla ores, caves and surface features (trees / plants / structures) kept: " + feat5 + " / 5");
    check(st[7] > 0L, "vanilla lava kept inside the islands: " + st[7] + " voxels");
    check(st[14] > 0L, "vanilla prefab entity groups (NPC spawn markers / structures) kept on the islands: " + st[14] + " of " + st[15]);
    check(st[21] > 0L && st[22] > 0L && pi[3 * 8 + 2] > 0L && pi[4 * 8 + 2] > 0L && pi[3 * 8 + 2] + pi[4 * 8 + 2] == st[12], "Zone 4 + 5 ores (fix 1): Onyxium " + st[21] + " + Mithril " + st[22] + " blocks, Zone 4 island " + pi[3 * 8 + 2] + " + Zone 5 island " + pi[4 * 8 + 2] + " of " + st[12] + ", none on Zones 1-3");
    check(st[17] >= 0L, "hanging roots under the rims: " + st[17]);
    java.util.concurrent.Executor gp = g.poolNow();
    check(gp instanceof java.util.concurrent.ThreadPoolExecutor, "WgZoneGen found vanilla's own generator pool for the mask hop: " + (gp == null ? null : gp.getClass().getName()) + "; hops " + %(ZI)s.HOPPED.get());
    long sk0 = %(ZI)s.SKIPPED.get();
    double fx = (L.cx[0] + L.cx[1]) / 2.0;
    double fz = (L.cz[0] + L.cz[1]) / 2.0;
    %(GC)s far = (%(GC)s) g.generate(seed, 0L, (int) Math.floor(fx / 32.0), (int) Math.floor(fz / 32.0), null, null).get(60L, java.util.concurrent.TimeUnit.SECONDS);
    check(far != null && %(ZI)s.SKIPPED.get() == sk0 + 1L, "a chunk in the void between Zone 1 and Zone 2 is skipped (an empty void chunk, vanilla never runs)");
    %(W)sWgZoneGen g2 = (%(W)sWgZoneGen) new %(W)sWgZoneProvider().getGenerator();
    %(ZL)s L2 = g2.layoutNow(seed);
    boolean same = true;
    for (int i = 0; i < L.n; i++) {
      if (L.found[i] != L2.found[i] || L.cx[i] != L2.cx[i] || L.cz[i] != L2.cz[i]) same = false;
      if (L.sd[i] != null && !java.util.Arrays.equals(L.sd[i], L2.sd[i])) same = false;
    }
    check(same && L2.fromFile, "fix 3: a fresh generator (= the next server start) REUSES the saved layout (fromFile " + L2.fromFile + "): the same islands with identical coast grids");
    %(ZL)s L4 = %(ZI)s.layout(new %(W)sWgZoneSampler(g2.getZonePatternGenerator(seed), seed, g2.getZonePatternProvider().getZones()), L.spx, L.spz, seed);
    boolean same4 = true;
    for (int i = 0; i < L.n; i++) {
      if (L.found[i] != L4.found[i] || L.cx[i] != L4.cx[i] || L.cz[i] != L4.cz[i]) same4 = false;
      if (L.sd[i] != null && !java.util.Arrays.equals(L.sd[i], L4.sd[i])) same4 = false;
    }
    check(same4, "determinism: a fresh pick from the real vanilla map gives the SAME islands as the saved layout (vanilla unchanged)");
    long diffs = 0L;
    for (int i = 0; i < 4 && i + 1 < cs.length; i += 2) {
      long idx = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(cs[i], cs[i + 1]);
      %(GC)s a = (%(GC)s) g.generate(seed, idx, cs[i], cs[i + 1], null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
      %(GC)s b = (%(GC)s) g2.generate(seed, idx, cs[i], cs[i + 1], null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
      for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) for (int y = 0; y < 320; y++) if (a.getBlockChunk().getBlock(x, y, z) != b.getBlockChunk().getBlock(x, y, z)) diffs++;
    }
    check(diffs == 0L, "determinism: the same chunks from the fresh generator are identical block for block: " + diffs + " differences");
    // fix round (review finding 4): a FAIR end-to-end time - two idle, warmed generators (g2 masked, v plain), NEW chunks, the order
    // alternating, so cold start / the live world's busy pool / which side ran first cannot skew it
    long tMask = 0L;
    long tVan = 0L;
    int nT = 0;
    for (int i = 0; i < 12 && i + 1 < cs.length; i += 2) {
      int qx = cs[i] + 3;
      int qz = cs[i + 1] - 2;
      if (%(ZI)s.chunkOutside(L2, qx, qz)) continue;
      long qi = com.hypixel.hytale.math.util.ChunkUtil.indexChunk(qx, qz);
      long a0 = System.nanoTime();
      if ((i / 2) %% 2 == 0) {
        g2.generate(seed, qi, qx, qz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
        long a1 = System.nanoTime();
        v.generate(seed, qi, qx, qz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
        tMask += a1 - a0;
        tVan += System.nanoTime() - a1;
      } else {
        v.generate(seed, qi, qx, qz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
        long a1 = System.nanoTime();
        g2.generate(seed, qi, qx, qz, null, null).get(120L, java.util.concurrent.TimeUnit.SECONDS);
        tVan += a1 - a0;
        tMask += System.nanoTime() - a1;
      }
      nT++;
    }
    log("TIME fair (idle warmed generators, order alternating, " + nT + " new chunks): masked " + (tMask / Math.max(1, nT) / 1000000L) + " ms avg, vanilla " + (tVan / Math.max(1, nT) / 1000000L) + " ms avg; the mask pass itself " + (%(ZI)s.MASK_NS.get() / Math.max(1L, %(ZI)s.MASKED.get()) / 100000L) / 10.0 + " ms per chunk");
    try { g2.shutdown(); } catch (Throwable t) { }
    java.nio.file.Path cfgp = %(W)sWgOpen.folderOf("skywynn_zones").resolve("config.json");
    com.hypixel.hytale.server.core.universe.world.WorldConfig wc = (com.hypixel.hytale.server.core.universe.world.WorldConfig) com.hypixel.hytale.server.core.universe.world.WorldConfig.load(cfgp).get(30L, java.util.concurrent.TimeUnit.SECONDS);
    check(wc != null && wc.getWorldGenProvider() instanceof %(W)sWgZoneProvider, "the saved config.json decodes back to the SkyWynnZones provider (a restart reopens the same world)");
    for (int i = 0; i < 5; i++) if (LANDS[i] != null) log("PLACE zone " + (i + 1) + ": " + %(ZI)s.placeAt(w, LANDS[i].getPosition().x, LANDS[i].getPosition().y, LANDS[i].getPosition().z));
    log("PLACE void: " + %(ZI)s.placeAt(w, fx, 150.0, fz));
    log("STATUS " + %(ZI)s.statusText(w));
    String[] il = %(W)sWgCmds.infoLines(null, null, null, w);
    for (int i = 0; i < il.length; i++) log("INFO " + il[i]);
    String[] ll = %(W)sWgCmds.listLines();
    for (int i = 0; i < ll.length; i++) log("LIST " + ll[i]);
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


def build_probe(J, out_dir, jar_path, seed, B):
    pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
    sub = {"FS": FS, "GC": GC, "GBC": GBC, "HOLD": HOLD, "CG": CG, "WLD": WLD, "UNI": UNI, "TRF": TRF, "CF": CF, "EWE": EWE, "W": W, "SEED": seed,
           "BT": BT, "FL": FL, "ZL": ZL, "ZI": ZI}
    run = pool.makeClass(PROBE_PKG + ".Run")
    run.addInterface(pool.get("java.lang.Runnable"))
    run.addField(CtField.make("public static com.hypixel.hytale.logger.HytaleLogger LOG;", run))
    run.addField(CtField.make("public static volatile int OKS = 0;", run))
    run.addField(CtField.make("public static volatile int FAILS = 0;", run))
    run.addField(CtField.make("public static %s LAY;" % ZL, run))
    run.addField(CtField.make("public static %s[] LANDS = new %s[5];" % (TRF, TRF), run))
    run.addField(CtField.make("public static final String[] VORE_NAMES = new String[] { %s };" % ", ".join('"%s"' % v for v in VORES), run))
    run.addConstructor(CtNewConstructor.make("public Run() { }", run))
    for src in PROBE_METHODS:
        body = src % sub
        try:
            run.addMethod(CtNewMethod.make(body, run))
        except Exception as e:
            raise SystemExit("probe compile failed: %s --- %s" % (e, body[:3000]))
    pl = pool.makeClass(PROBE_PKG + ".SkyyWgProbe6Plugin", pool.get("com.hypixel.hytale.server.core.plugin.JavaPlugin"))
    pl.addConstructor(CtNewConstructor.make("public SkyyWgProbe6Plugin(com.hypixel.hytale.server.core.plugin.JavaPluginInit init) { super(init); }", pl))
    pl.addMethod(CtNewMethod.make(r"""
public void setup() {
  %s.Run.LOG = getLogger();
  %s.Run.log("%s ready (TEST PROBE - never deploy)");
  Thread t = new Thread(new %s.Run(), "SkyyWgProbe6");
  t.setDaemon(true);
  t.start();
}""" % (PROBE_PKG, PROBE_PKG, PROBE_VERSION, PROBE_PKG), pl))
    for c in (run, pl):
        c.writeFile(out_dir)
    man = B.manifest("SkyyWgProbe6", PROBE_VERSION, "TEST PROBE for SkyyWorldGen 0.6 (scratch only, never deployed)", PROBE_PKG + ".SkyyWgProbe6Plugin")
    man["IncludesAssetPack"] = False
    man["Dependencies"] = {"Skyy:0.6 SkyyWorldGen": "*"}
    B.assemble(jar_path, man, out_dir)
'''


# ================================================================= VP. the REAL vanilla 0.7 generator through the mod on an offline server
PROBE_BUILD = r'''import os, sys
sys.path.insert(0, %(tools)r)
sys.path.insert(0, %(pdir)r)
import skyybuild as B
J = B.start()
J["pool"].insertClassPath(%(jar)r)
import probe_src as P
os.makedirs(os.path.join(%(pdir)r, "classes"), exist_ok=True)
P.build_probe(J, os.path.join(%(pdir)r, "classes"), os.path.join(%(pdir)r, "SkyyWgProbe6-0.6.jar"), %(seed)d, B)
'''


def vp():
    if "--no-smoke" in sys.argv:
        NOTES.append("VP skipped (--no-smoke): the real wrapped vanilla generator did NOT run in this harness run - UNVERIFIED by it")
        return
    import deploy_set as DS
    if DS.server_running():
        NOTES.append("VP NOT RUN: a HytaleServer java process is running (the game / a world is open) - the real-generator run is UNVERIFIED "
                     "by this harness run; re-run with the game closed")
        print("VP. NOT RUN - the game is running")
        return
    pdir = os.path.join(SCRATCH, "probe")
    os.makedirs(pdir, exist_ok=True)
    with open(os.path.join(pdir, "probe_src.py"), "w", encoding="utf-8") as f_:
        f_.write(PROBE_SRC)
    with open(os.path.join(pdir, "probe_build.py"), "w", encoding="utf-8") as f_:
        f_.write(PROBE_BUILD % {"tools": TOOLS, "pdir": pdir, "jar": JAR, "seed": ZSEED})
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    r1 = subprocess.run([sys.executable, os.path.join(pdir, "probe_build.py")], cwd=pdir, env=env, capture_output=True, text=True, timeout=900)
    pj = os.path.join(pdir, "SkyyWgProbe6-0.6.jar")
    if not check(r1.returncode == 0 and os.path.isfile(pj), "VP. the test probe jar builds (scratch only): %s" % (r1.stdout + r1.stderr)[-300:]):
        return
    smoke = os.path.join(TOOLS, "dev", "scratch", "smoke")
    before = set(os.listdir(smoke)) if os.path.isdir(smoke) else set()
    t0 = time.time()
    r2 = subprocess.run([sys.executable, os.path.join(TOOLS, "smoke_test.py"), "--light", "--linger", "420", "--xmx", "6G", "--allow-pack-api",
                         "--jar", JAR, "--jar", pj], cwd=ROOT, env=env, capture_output=True, text=True, timeout=2400)
    # other agents may run smoke tests at the same time: the log is the new one that holds the probe's lines
    logs, txt = [], ""
    for n_ in sorted(n_ for n_ in (set(os.listdir(smoke)) - before) if n_.endswith(".log")):
        t_ = open(os.path.join(smoke, n_), encoding="utf-8", errors="replace").read()
        if "[SkyyWgProbe6]" in t_:
            logs, txt = [n_], t_
    plines = [l_.split("[SkyyWgProbe6] ", 1)[1] for l_ in txt.splitlines() if "[SkyyWgProbe6] " in l_]
    res = [l_ for l_ in plines if l_.startswith("RESULT ")]
    fails = [l_ for l_ in plines if l_.startswith("FAIL ")]
    oks = [l_ for l_ in plines if l_.startswith("OK ")]
    m_ = re.match(r"RESULT ok=(\d+) fail=(\d+)", res[-1]) if res else None
    smoke_out = (r2.stdout or "")
    ours = [l_ for l_ in smoke_out.splitlines() if "SkyyWgProbe6" not in l_]
    check(r2.returncode == 0 or ("FAIL no ready line: SkyyWgProbe6" in smoke_out and "SMOKE TEST FAIL" in smoke_out and
                                 not [l_ for l_ in ours if l_.strip().startswith("FAIL")]),
          "VP. the smoke test (offline server, scratch copy of the live world, the SET with this jar + the probe) PASSES for every SET mod "
          "(the probe prints no SET ready line): exit %d, %s" % (r2.returncode, smoke_out[-600:].replace("\n", " | ")))
    check(m_ is not None and int(m_.group(2)) == 0 and int(m_.group(1)) >= 30 and not fails,
          "VP. the probe on the REAL vanilla 0.7 generator: %s (%d OK lines) %s" % (res[-1] if res else "no RESULT line", len(oks), fails[:6]))
    for l_ in plines:
        if l_.startswith(("LAYOUT", "GAPS", "ISLAND", "STATS", "PERISLAND", "TIME", "PLACE", "INFO", "CHANGED", "MISSING", "FAIL", "RESULT", "sampling",
                          "STATUS")):
            NOTES.append("VP " + l_[:900])
    print("VP. real server run %.0f s: %s; log %s" % (time.time() - t0, res[-1] if res else "no result", logs[-1] if logs else "-"))


# ============================================================================================ parent
def main():
    if "--e" in sys.argv:
        return run_e(arg("--out"))
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
    try:
        # ---- CC
        rules = [[r"worldgen_0_6_patch", "worldgen_0_5_1_patch"]]
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
            check(sorted(cc["added"]) == NEW_CLASSES and cc["gone"] == [], "CC: + exactly the 9 zone classes (fix 4: + WgZoneArrive), none gone: %s %s" % (cc["added"], cc["gone"]))
            struct = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else " (gone)" if x.endswith("(gone)") else "") for x in v["structural"]))
                          for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            fnew = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            fgone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            print("CC. 0.5.1 -> 0.6 structural %s; constants only %s; fields new %s" % (struct, const, fnew))
            frozen = [c for c in FROZEN if c in struct or c in const or c in fnew or c in fgone]
            check(not frozen, "CC: the 0.5 generator + spawn / store / log classes are UNCHANGED (old worlds generate exactly as before): %s" % frozen)
            check(not fgone and all(v["same_shape"] for v in cls_.values()), "CC: no field removed, same supers / interfaces: %s" % fgone)
            allowed = {"WgZones", "WgCheck", "WgCfg", "WgOpen", "WgCmds", "WgHereTask", "WgHooks", "SkyyWorldGenPlugin", "ZoneGoCmd", "ZoneCmd",
                       "CfgDef", "CfgFn", "CfgPub", "CfgRows", "CfgUi", "CfgHist", "CfgStore"}
            check(set(struct) <= allowed | set(c for c in cls_ if c.startswith("Cfg")), "CC: structural changes only in the zone table / check / config / "
                  "open / commands / hooks / plugin (+ the config kit's rows): %s" % sorted(struct))
            check(struct.get("WgOpen") == ["go", "goZone (new)"], "CC: WgOpen = go (routes the zone world) + goZone (new): %s" % struct.get("WgOpen"))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(sorted(cn - cp_) == ["com/skyy/worldgen/%s.class" % c for c in NEW_CLASSES] and not (cp_ - cn), "JT: class files = 0.5.1's + the 9: %s %s"
              % (sorted(cn - cp_), sorted(cp_ - cn)))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        added = sorted(nn - np_)
        check(added == ["Server/Instances/SkyWynn_Zones/instance.bson", "Server/Instances/SkyWynn_Zones/resources/InstanceData.json",
                        "Server/Item/Items/SkyWynn/Ore_Onyxium_SkyWynn.json"] and not (np_ - nn), "JT: + exactly the zone world template + our "
              "ore block: %s %s" % (added, sorted(np_ - nn)))
        norm = lambda b_: b_.replace(b"(SkyyWorldGen %s)" % VERSION.encode(), b"(SkyyWorldGen %s)" % PREV_VERSION.encode())
        diff = sorted(n for n in np_ if n != "manifest.json" and norm(zj.read(n)) != zp.read(n))
        check(not diff, "JT: every old non-class entry byte-identical but the version in a template comment (the Zone 1 island + both proof "
              "worlds' files unchanged): %s" % diff[:4])
        ore = json.loads(zj.read("Server/Item/Items/SkyWynn/Ore_Onyxium_SkyWynn.json"))
        bt = ore["BlockType"]
        drops = [c_["Item"]["ItemId"] for c_ in bt["Gathering"]["Breaking"]["DropList"]["Container"]["Containers"]]
        check(bt["Gathering"]["Breaking"]["Quality"] == 6 and drops == ["Ore_Onyxium", "Rock_Basalt_Cobble"] and bt["Material"] == "Solid",
              "JT: the Onyxium ore block - Rocks quality 6 (Mithril pickaxe), drops vanilla Ore_Onyxium + basalt cobble: %s" % drops)
        tz = json.loads(zj.read("Server/Instances/SkyWynn_Zones/instance.bson"))
        check(tz["WorldGen"] == {"Type": "SkyWynnZones"} and tz["Seed"] == ZSEED and "SpawnProvider" not in tz and tz["Death"] == {"ItemsLossMode": "None"}
              and tz["Plugin"] == {"Instance": {"RemovalConditions": []}} and tz["DeleteOnUniverseStart"] is False, "JT: the zone world template - "
              "SkyWynnZones, seed %d, vanilla spawn, deaths keep items, kept forever: %s" % (ZSEED, {k: tz[k] for k in ("WorldGen", "Seed", "Death")}))
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
        # ---- VP
        try:
            vp()
        except Exception as e:
            check(False, "VP crashed: %s" % e)
        # ---- AA
        out_aa = os.path.join(SCRATCH, "aa.log")
        with open(out_aa, "wb") as lf:
            subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                           stderr=subprocess.STDOUT, cwd=ROOT)
        aa = open(out_aa, encoding="utf8", errors="replace").read()
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyWorldGen " in ln]
        check("access:" in aa and not mine, "AA: crosscheck --jar 0.6: no FAIL for SkyyWorldGen on 0.7: %s" % mine[:3])
        bl = [ln for ln in aa.splitlines() if "baseline SkyyWorldGen" in ln]
        print("AA. %s" % bl[:3])
        check(any("command / permission tree identical" in ln for ln in bl), "AA: the command / permission tree = 0.5.1's: %s" % bl[:3])
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
