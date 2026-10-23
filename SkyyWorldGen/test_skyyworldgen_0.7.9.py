"""Harness for SkyyWorldGen 0.7.9 (the StructureV2 freeze fix: WgZ2Gen / WgZoneGen / WgIsleGen.getUniquePrefabs never throws;
tools/worldgen_0_7_9_patch.py). Build first:
    python tools/worldgen_0_7_9_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.9.py

    python SkyyWorldGen/test_skyyworldgen_0.7.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.8 -> 0.7.9: exactly the EXPECTED members differ (the three generators: + getUniquePrefabs + uniqueRaw; the version
               texts); the one added class is WgUniq
  U    unique   the REAL override on all three generators (instances without their vanilla constructor; vanilla's REAL UniquePrefabCache
               put in the private field, its function a stand-in that - like vanilla's - only works on a ChunkWorker thread; the pool =
               vanilla's REAL ChunkWorkerThreadFactory): (1) a call from a plain (non-worker) thread with no pool -> the empty array, no
               throw, ONE log line per world type; (2) with the pool -> the pool's entries (the work ran on a ChunkWorker), and the next
               call is a plain cache hit (no rescue); (3) a call ON a ChunkWorker -> super's result unchanged (no rescue); (4) the pool
               fails too -> empty, then a 30 s back-off: the next call returns at once (no 5 s wait); a pool result that finished during
               the back-off is used; (5) a pool slower than 5 s -> empty after ~5 s, the next call at once, and once the pool finished
               the cache answers again; (6) super failing ON a ChunkWorker -> empty at once (never waits on its own pool)
  L    live     START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen (WgCfg.load, WgStore.read): no file changed
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED here): that StructureV2 0.1.7 with worldgen ON no longer freezes the zone world after 5 min, and
that its structures still appear (it only uses the array for its "not near a unique prefab" check).
Exit code 1 on any failure.
"""
import os, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.9"
OLD_VERSION = "0.7.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg079", "wg")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
LIVE_WG = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyWorldGen")
UPE = "com.hypixel.hytale.server.worldgen.container.UniquePrefabContainer$UniquePrefabEntry"
_GEN = ["+m getUniquePrefabs", "+m uniqueRaw"]
EXPECT = {
    "WgZ2Gen": _GEN, "WgZoneGen": _GEN, "WgIsleGen": _GEN,
    # the version texts only (VERSION in the plugin setup line, the config kit header / export, the store's created-by line)
    "SkyyWorldGenPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "WgCfg": ["~m load", "~m reloadAll"],
    "WgStore": ["~m markCreated"],
}
ADDED = ["WgUniq"]
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


# ------------------------------------------------------------------------------------------- U: the override, executed
def run_unique(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride, JString
    # vanilla's caches read the server options in their static init (Constants): parse a scratch universe first
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    Uq = JClass(PKG + "WgUniq")
    Lg = JClass(PKG + "WgLog")
    CG = JClass("com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator")
    UPC = JClass("com.hypixel.hytale.server.worldgen.cache.UniquePrefabCache")
    CWTF = JClass("com.hypixel.hytale.server.worldgen.util.ChunkWorkerThreadFactory")
    Ex = JClass("java.util.concurrent.Executors")
    Thread = JClass("java.lang.Thread")
    UPEc = JClass(UPE)
    fu = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    fcache = CG.class_.getDeclaredField("uniquePrefabCache")
    fcache.setAccessible(True)
    K.check(Lg.LOG is None, "U WgLog.LOG is unset in a bare JVM (the once-log prints to stdout)")

    # mode: "worker" = like vanilla (works only on a ChunkWorker), "never" = always fails, "slow" = a ChunkWorker after 6 s
    @JImplements("com.hypixel.hytale.server.worldgen.cache.UniquePrefabCache$UniquePrefabFunction")
    class Fn(object):
        def __init__(self, mode):
            self.mode, self.calls, self.threads = mode, 0, []

        @JOverride
        def get(self, seed):
            self.calls += 1
            t = Thread.currentThread()
            self.threads.append(str(t.getClass().getName()))
            if self.mode == "never" or "ChunkWorker" not in str(t.getClass().getName()):
                raise JClass("java.lang.NullPointerException")("stand-in: no worldgen resource on thread " + str(t.getName()))
            if self.mode == "slow":
                time.sleep(6.0)
            return JArray(UPEc)(2)

    @JImplements("java.util.concurrent.Callable")
    class Call(object):
        def __init__(self, g, seed):
            self.g, self.seed = g, seed

        @JOverride
        def call(self):
            return self.g.getUniquePrefabs(self.seed)

    def gen(cn, mode, pool=False):
        g = U.allocateInstance(JClass(PKG + cn).class_)
        f = Fn(mode)
        fcache.set(g, UPC(f, 16, 300))
        g.gpoolTried = True
        g.gpool = Ex.newFixedThreadPool(2, CWTF(g, "SkyyWgTest")) if pool else None
        return g, f

    def call(g, seed=20261014):
        t0 = time.time()
        try:
            r = g.getUniquePrefabs(seed)
            return (len(r) if r is not None else None), time.time() - t0, None
        except Exception as e:
            return None, time.time() - t0, str(e)

    def cnt():
        return int(Uq.RESCUES.get()), int(Uq.HOPPED.get()), int(Uq.EMPTY.get()), int(Uq.SKIPPED.get()), int(Uq.LOGGED.get())

    pools = []
    for cn, tag in (("WgZ2Gen", "z2"), ("WgZoneGen", "zone"), ("WgIsleGen", "isle")):
        # (1) a plain thread, no pool -> empty, no throw, one log line per world type
        g, f = gen(cn, "worker")
        c0 = cnt()
        n, dt, err = call(g)
        c1 = cnt()
        K.check(err is None and n == 0, "U1 %s: a plain-thread call with no pool returns the empty array, never throws (%s, %s)" % (cn, n, err))
        K.check(c1[0] == c0[0] + 1 and c1[2] == c0[2] + 1 and c1[4] == c0[4] + 1 and bool(Lg.ONCE.containsKey("uniq" + tag)),
                "U1 %s: one rescue, one empty, ONE log line (key uniq%s): %s -> %s" % (cn, tag, c0, c1))
        K.check(tag + ": no generator pool" in str(Uq.LAST), "U1 %s: the reason is recorded: %s" % (cn, str(Uq.LAST)[:160]))
        n, dt, err = call(g)
        c2 = cnt()
        K.check(err is None and n == 0 and c2[4] == c1[4] and c2[2] == c1[2] + 1, "U1 %s: a second failing call: empty again, no second log line" % cn)
        # (2) with vanilla's ChunkWorker pool -> the pool's entries; the next call = a plain cache hit
        g, f = gen(cn, "worker", pool=True)
        pools.append(g.gpool)
        c0 = cnt()
        n, dt, err = call(g)
        c1 = cnt()
        K.check(err is None and n == 2, "U2 %s: a plain-thread call returns the entries made on vanilla's pool (%s, %s)" % (cn, n, err))
        K.check(c1[0] == c0[0] + 1 and c1[1] == c0[1] + 1 and c1[2] == c0[2], "U2 %s: one rescue, one hop, no empty: %s -> %s" % (cn, c0, c1))
        K.check(any("ChunkWorker" in t for t in f.threads) and f.calls == 2, "U2 %s: super's work ran on a ChunkWorker thread: %s" % (cn, f.threads))
        n, dt, err = call(g)
        c2 = cnt()
        K.check(n == 2 and c2 == c1 and f.calls == 2, "U2 %s: the next call is a plain cache hit (no rescue, no recompute)" % cn)
        # (3) ON a ChunkWorker: super's result unchanged
        g, f = gen(cn, "worker", pool=True)
        pools.append(g.gpool)
        c0 = cnt()
        r = g.gpool.submit(Call(g, 7)).get()
        K.check(r is not None and len(r) == 2 and cnt() == c0, "U3 %s: a call on a ChunkWorker returns super's result, no rescue" % cn)
        # (4) the pool fails too -> empty, back-off (no second 5 s wait); a finished pool result is used during the back-off
        g, f = gen(cn, "never", pool=True)
        pools.append(g.gpool)
        c0 = cnt()
        n, dt, err = call(g)
        c1 = cnt()
        K.check(err is None and n == 0 and c1[2] == c0[2] + 1 and c1[1] == c0[1], "U4 %s: pool failed too -> empty, no throw (%s)" % (cn, err))
        k = str(Uq.keyOf(g, 20261014, tag))
        K.check(Uq.BACKOFF.get(k) is not None, "U4 %s: the back-off is set" % cn)
        n, dt, err = call(g)
        c2 = cnt()
        K.check(err is None and n == 0 and dt < 1.0 and c2[3] == c1[3] + 1, "U4 %s: the next call during the back-off returns at once (%.3f s), skipped" % (cn, dt))
        done = JClass("java.util.concurrent.CompletableFuture").completedFuture(JArray(UPEc)(3))
        Uq.INFLIGHT.put(k, done)
        n, dt, err = call(g)
        c3 = cnt()
        K.check(n == 3 and c3[1] == c2[1] + 1 and Uq.BACKOFF.get(k) is None, "U4 %s: a pool result that finished during the back-off is used (%s)" % (cn, n))
    # (5) a pool slower than 5 s (once - it costs ~6 s): empty after ~5 s, the next call at once, then the cache answers
    g, f = gen("WgZ2Gen", "slow", pool=True)
    pools.append(g.gpool)
    c0 = cnt()
    n, dt, err = call(g)
    c1 = cnt()
    K.check(err is None and n == 0 and 4.5 <= dt < 6.0 and c1[2] == c0[2] + 1, "U5 a pool slower than 5 s: empty after %.2f s (the world thread waits at most 5 s), no throw" % dt)
    K.check("took over 5000 ms" in str(Uq.LAST), "U5 the reason: %s" % str(Uq.LAST)[:160])
    n, dt, err = call(g)
    c2 = cnt()
    K.check(n == 0 and dt < 1.0 and c2[3] == c1[3] + 1, "U5 the next call during the back-off returns at once (%.3f s)" % dt)
    time.sleep(2.0)
    c3 = cnt()
    n, dt, err = call(g)
    K.check(n == 2 and cnt() == c3, "U5 once the slow pool task finished, its entries sit in vanilla's cache: a plain hit (%s)" % n)
    # (6) super failing ON a ChunkWorker: empty at once, never waits on its own pool
    g, f = gen("WgZ2Gen", "never", pool=True)
    pools.append(g.gpool)
    c0 = cnt()
    t0 = time.time()
    r = g.gpool.submit(Call(g, 9)).get()
    dt = time.time() - t0
    c1 = cnt()
    K.check(r is not None and len(r) == 0 and dt < 1.0 and c1[1] == c0[1] and c1[2] == c0[2] + 1 and "generator thread" in str(Uq.LAST),
            "U6 super failing on a ChunkWorker: empty in %.3f s, no hop (%s)" % (dt, str(Uq.LAST)[:120]))
    # WgUniq.get on a foreign generator: refused (never a silent wrong answer)
    try:
        Uq(None, 1).get()
        K.check(False, "U WgUniq.get on a null generator throws")
    except Exception as e:
        K.check("not one of our generators" in str(e), "U WgUniq.get on a foreign generator is refused: %s" % str(e)[:100])
    K.eq(int(Uq.LOGGED.get()), 3, "U exactly one log line per world type (z2, zone, isle) over the whole run")
    K.eq(int(Uq.WAIT_MS), 5000, "U the world thread waits at most 5000 ms")
    for p in pools:
        p.shutdownNow()
    K.save()


# ------------------------------------------------------------------------------------------- L: start twice on the live copy
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass
    Cfg, St = JClass(PKG + "WgCfg"), JClass(PKG + "WgStore")
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
        K.check(True, "L start %d on the live copy ran" % s)
    K.check(tree() == t0, "L start twice: the live copy is byte-identical (nothing written; 0.7.9 adds no setting / saved data) - %d files" % len(t0))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("unique", run_unique), ("live", run_live)], __file__, live=(LIVE_WG, "Skyy_SkyyWorldGen"))
