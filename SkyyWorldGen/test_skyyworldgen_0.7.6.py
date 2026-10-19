"""Harness for SkyyWorldGen 0.7.6 (round wg76: no world-thread island pick + the background landing pre-load, beta bug 4 lag part 4;
tools/worldgen_0_7_6_patch.py). Build first:
    python tools/worldgen_0_7_6_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.6.py

    python SkyyWorldGen/test_skyyworldgen_0.7.6.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.5 -> 0.7.6: exactly the EXPECTED members differ (WgZ2Gen generate split + pickFor + landingOf cache, WgDone / WgWeather
               triggers, WgCfg PREGEN_R, the new config row, version texts); added classes WgZ2Pick / WgZ2Then / WgZ2Pre; non-class entries:
               manifest.json + the instance templates (version only)
  F    func     on the real classes (server jar on the class path):
               - WgZ2Gen.generate never runs layoutNow on the calling thread (bytecode: generate has no layoutNow call; live: a generate() on
                 a generator with no layout returns at once, the pick runs on another thread, the chunk future fails like 0.7.5's
                 (failed layout -> failed future), a later call makes a fresh pick, a READY layout goes straight to generateWith (no pick))
               - landingOf uses the cached landing height (y = cache + 2) and falls back to getHeight when unknown
               - WgZ2Pre.ring / centres / wanted: (2r+1)^2 distinct chunks nearest first, spawn landing first, stored chunks left out, overlaps once
               - WgCfg: zones.pregenRadius default 3 (file + field), clamped 0..8, a file without the line keeps the running value
               - kick() ignores null / other worlds and starts nothing
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.6"
OLD_VERSION = "0.7.5"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg76", "wg")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyWorldGenPlugin": ["~m setup"], "WgStore": ["~m markCreated"],
    "WgCfg": ["+f PREGEN_R", "~<clinit>", "~m apply", "~m load", "~m reloadAll"],
    "WgDone": ["~m accept"], "WgWeather": ["~m tick"],
    "WgZ2Gen": ["+<clinit>", "+f PICKS", "+f PICK_THREAD", "+f WAITED", "+f landY", "+f landYSeed", "+f pick", "+f pickSeed",
                "+m generateWith", "+m pickFor", "~c ", "~m generate", "~m landingOf"],      # ~c = the two "= 0" field initialisers
}
ADDED = ["WgZ2Pick", "WgZ2Then", "WgZ2Pre"]
if "--expect-dump" in sys.argv:
    EXPECT = {}

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            ok = "manifest.json" in got and all(n in ("manifest.json", LANG) or n.endswith("/instance.bson") for n in got)
            if ok and LANG in got:      # server.lang: only its header comment names the version
                a = zipfile.ZipFile(OLD_JAR).read(LANG).decode("utf8").splitlines()
                b = zipfile.ZipFile(HK.arg("--jar", JAR)).read(LANG).decode("utf8").splitlines()
                ok = len(a) == len(b) and [i for i in range(len(a)) if a[i] != b[i]] == [0] and a[0].replace(OLD_VERSION, VERSION) == b[0]
            return self.check(ok, "C: non-class entries changed = manifest.json + instance templates + server.lang header (version text only): %s" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def run_func(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    from jpype import JClass, JArray, JLong, JDouble, JInt
    Gen = JClass(PKG + "WgZ2Gen")
    Lay = JClass(PKG + "WgZ2Layout")
    Pre = JClass(PKG + "WgZ2Pre")
    Cfg = JClass(PKG + "WgCfg")
    CU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
    Thread = JClass("java.lang.Thread")
    TU = JClass("java.util.concurrent.TimeUnit")

    # --- bytecode: generate() has no layoutNow call; generateWith has none either; pickFor uses supplyAsync
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    PS, BOS = JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cls, name):
        res = []
        for m in CP.get(PKG + cls).getDeclaredMethods():
            if str(m.getName()) == name:
                b = BOS()
                IP(PS(b)).print_(m)
                res.append(str(b.toString()))
        return "\n".join(res)
    g_code, gw_code, pf_code = code("WgZ2Gen", "generate"), code("WgZ2Gen", "generateWith"), code("WgZ2Gen", "pickFor")
    K.check(g_code and "layoutNow" not in g_code and "pickFor" in g_code and "generateWith" in g_code,
            "F generate(): no layoutNow call (pickFor + generateWith only)")
    K.check(gw_code and "layoutNow" not in gw_code and "WgZ2Hop" in gw_code, "F generateWith(): no layoutNow call, the 0.7 hop kept")
    K.check("supplyAsync" in pf_code and "isCompletedExceptionally" in pf_code, "F pickFor(): one supplyAsync per seed, a failed pick replaced")
    K.check(CP.get(PKG + "WgZ2Gen").getDeclaredMethod("pickFor").getModifiers() & 0x20 != 0
            and CP.get(PKG + "WgZ2Gen").getDeclaredMethod("layoutNow").getModifiers() & 0x8 == 0,
            "F pickFor is static synchronized (class lock) while layoutNow is an instance method (its own monitor) - a caller never waits on a pick")

    # --- live: a generator instance without its constructor (no vanilla world-gen needed): the pick fails like a broken vanilla map
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    g = U.allocateInstance(Gen.class_)
    seed = 4242
    p0 = int(Gen.PICKS.get())
    me = str(Thread.currentThread().getName())
    import time
    t0 = time.time()
    f1 = g.generate(seed, JLong(0), 0, 0, None, None)
    dt = time.time() - t0
    K.check(dt < 0.5, "F generate() with no layout returns at once (%.3f s)" % dt)
    failed = False
    try:
        f1.get(30, TU.SECONDS)
    except Exception:
        failed = True
    K.check(failed and f1.isCompletedExceptionally(), "F the chunk future fails when the pick fails (the engine backs off and retries, as 0.7.5)")
    K.eq(int(Gen.PICKS.get()) - p0, 1, "F exactly one pick ran")
    K.check(str(Gen.PICK_THREAD) != me and str(Gen.PICK_THREAD) != "", "F the pick ran off the calling thread (%s, caller %s)" % (Gen.PICK_THREAD, me))
    K.check(g.lay is not None and bool(g.lay.failed) and not bool(g.laid), "F the failed layout is kept with laid = false (the retry gate)")
    f2 = g.generate(seed, JLong(0), 0, 0, None, None)
    try:
        f2.get(30, TU.SECONDS)
    except Exception:
        pass
    K.eq(int(Gen.PICKS.get()) - p0, 2, "F a later chunk after a FAILED pick starts a fresh pick (layoutNow's own 15 s gate answers it at once)")
    K.check(f2.isCompletedExceptionally(), "F ... and its chunk fails too")
    # a READY layout: generate goes straight to generateWith - no pick (here the layout is marked failed, so the chunk fails synchronously)
    L = Lay(5)
    L.failed = True
    g.lay, g.lseed, g.laid = L, seed, True
    f3 = g.generate(seed, JLong(0), 0, 0, None, None)
    K.check(f3.isDone() and f3.isCompletedExceptionally(), "F a laid layout: generate() answers on the calling thread (no future chain)")
    K.eq(int(Gen.PICKS.get()) - p0, 2, "F ... and starts no pick")

    # --- landingOf: cached height + 2, unknown -> vanilla getHeight (fails on this bare instance -> 120 + 2)
    L2 = Lay(5)
    L2.failed = False
    L2.found[0] = True
    L2.found[1] = True
    L2.lx[0], L2.lz[0], L2.lx[1], L2.lz[1] = -746.3, 526.8, 900.0, -40.0
    g.lay, g.lseed, g.laid = L2, seed, True
    ys = JArray(JInt)([77, -2147483648, -2147483648, -2147483648, -2147483648])
    g.landYSeed = seed
    g.landY = ys
    t = g.landingOf(seed, 0)
    K.check(t is not None and float(t.getPosition().y()) == 79.0 and float(t.getPosition().x()) == -746.5 and float(t.getPosition().z()) == 526.5,
            "F landingOf uses the cached landing height: %s" % (t and (t.getPosition().x(), t.getPosition().y(), t.getPosition().z()),))
    t1 = g.landingOf(seed, 1)
    K.check(t1 is not None and float(t1.getPosition().y()) == 122.0, "F an unknown cached height falls back to getHeight (bare instance: 120 + 2): %s" % (t1 and t1.getPosition().y()))
    g.landYSeed = seed + 1
    t2 = g.landingOf(seed, 0)
    K.check(float(t2.getPosition().y()) == 122.0, "F a cache for another seed is ignored")
    K.check(g.landingOf(seed, 2) is None, "F a zone without a landing -> null (as 0.7.5)")

    # --- WgZ2Pre pure parts
    K.eq(len(Pre.ring(3, 4, 0)), 1, "F ring r0 = 1 chunk")
    K.eq(len(Pre.ring(3, 4, -1)), 0, "F ring r<0 = none")
    for r in (1, 3, 8):
        rg = [int(x) for x in Pre.ring(5, -3, r)]
        pts = [(int(CU.xOfChunkIndex(JLong(i))), int(CU.zOfChunkIndex(JLong(i)))) for i in rg]
        d = [max(abs(x - 5), abs(z + 3)) for x, z in pts]
        K.check(len(rg) == (2 * r + 1) ** 2 and len(set(rg)) == len(rg) and d == sorted(d) and max(d) == r and pts[0] == (5, -3),
                "F ring r%d: %d distinct chunks, nearest first, centre first" % (r, len(rg)))
    sp = JArray(JDouble)([-746.5, 123.0, 525.5, 0.0])
    cs = [int(x) for x in Pre.centres(L2, sp)]
    K.eq(cs, [int(CU.indexChunkFromBlock(-747, 525)), int(CU.indexChunkFromBlock(-747, 526)), int(CU.indexChunkFromBlock(900, -40))],
         "F centres: the set Zone 1 landing first, then each found landing (missing zones skipped)")
    K.eq(len(Pre.centres(L2, None)), 2, "F centres without a set landing = the found landings")
    HS = JClass("java.util.HashSet")
    have = HS()
    a = int(CU.indexChunk(0, 0))
    b = int(CU.indexChunk(1, 1))
    have.add(JClass("java.lang.Long")(a))
    w = [int(x) for x in Pre.wanted(JArray(JLong)([CU.indexChunk(0, 0), CU.indexChunk(1, 0)]), 1, have)]
    K.check(len(w) == 12 - 1 and a not in w and b in w and len(set(w)) == len(w), "F wanted: 2 overlapping r1 rings = 12 chunks once, minus the stored one (%d)" % len(w))
    K.eq(len(Pre.wanted(JArray(JLong)([CU.indexChunk(0, 0)]), 2, None)), 25, "F wanted without a stored list = the whole ring")
    K.check(not Pre.kick(None), "F kick(null) starts nothing")
    K.eq(int(Pre.RUNS.get()), 0, "F no pre-load ran")

    # --- the setting
    K.eq(int(Cfg.PREGEN_R), 3, "F PREGEN_R starts at 3")
    props = Cfg.props(Cfg.DEF_CFG)
    K.eq(str(props.getProperty("zones.pregenRadius")), "3", "F the default file has zones.pregenRadius=3")
    for v, want in (("20", 8), ("-4", 0), ("0", 0), ("5", 5), ("x", 5)):
        props.setProperty("zones.pregenRadius", v)
        Cfg.apply(props)
        K.eq(int(Cfg.PREGEN_R), want, "F zones.pregenRadius=%s -> %d" % (v, want))
    props.remove("zones.pregenRadius")
    Cfg.apply(props)
    K.eq(int(Cfg.PREGEN_R), 5, "F a file without the line keeps the running value")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("func", run_func)], __file__)
