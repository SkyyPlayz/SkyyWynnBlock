"""Harness for SkyyBazaar 0.1.8 (BzTick lag fix + lock-free bridge; tools/bazaar_0_1_8_patch.py).
Build first: python tools/bazaar_0_1_8_patch.py && python SkyyBazaar/build_skyybazaar_0.1.8.py

    python SkyyBazaar/test_skyybazaar_0.1.8.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.7 -> 0.1.8: exactly the listed members differ
  X  exec     0.1.7 and 0.1.8 side by side (each in its own class loader, each on its own data folder, the same simulated clock):
              400 random steps (trades = Market.apply, decays 10 s .. 2 h apart, resets, ticks = decay + flush): after EVERY step
              every product's demand factor, buy-1 and sell-1 quote and lifetime counters are identical on both jars. EVERY NEW PATH:
              BzUtil.bridge0 / bridge (cached, same map) + the kit's CfgRows.bridge, decay's moved list (MOVED = the ids whose factor
              changed, an id snapped to 1.0 included; an idle market publishes nothing; an unchanged id is NOT re-put), PEND / SAVED
              (a decay-only change is not written until 5 minutes after the last write; a trade is written by the next tick, together
              with lastDecayMillis), forcePending (shutdown), load resets PEND, publishAll's CSV re-put only on a changed text,
              unpublishAll. RESTARTS: at 25 random points both data folders are copied and started in FRESH loaders: the 0.1.8 restart
              (whose file may be up to 5 minutes behind) gives the same factors (1e-9) and the SAME quotes as 0.1.8 in memory and as the
              0.1.7 restart. ROLLBACK: 0.1.7 started on 0.1.8's folder = the same quotes.
  D  live     start twice on a scratch COPY of the live Skyy_SkyyBazaar with 0.1.7 and 0.1.8: the same products, factors and quotes;
              no file changes beyond 0.1.7's own (market.properties' lastDecayMillis / decayed factors)
  AA engine-access audit
Scratch: tools/dev/scratch/perfecon/bazaar (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, random, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfecon", "bazaar")))
PKG = "com.skyy.bazaar."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")
EXPECT = {
    "BzUtil": ["+f BRIDGE", "+m bridge0", "~m bridge"],
    "Market": ["+f PEND", "+f SAVED", "+f PEND_MS", "+f CSV", "+f MOVED", "~m decay", "+m forcePending", "~m snapshot", "~m load",
               "~m publishAll", "~m unpublishAll", "~<clinit>"],
    "SkyyBazaarPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"],   # header: the version text "0.1.8" (kit constant inlined)
    "CfgFn": ["~m opExport"],                                            # opExport: the same version text
}
ADDED = []


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Bz(object):
    """one jar's Market / Catalog / BzCfg in its own loader, started on folder d like SkyyBazaarPlugin.setup() (data steps)"""

    def __init__(self, jar, d):
        from jpype import JClass
        self.L = loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.M, self.C, self.Cfg, self.U = g("Market"), g("Catalog"), g("BzCfg"), g("BzUtil")
        P = JClass("java.nio.file.Paths")
        dp = P.get(d)
        os.makedirs(d, exist_ok=True)
        self.C.FILE = dp.resolve("products.properties")
        self.C.PFILE = dp.resolve("pricing.properties")
        self.M.FILE = dp.resolve("market.properties")
        self.M.LOGFILE = dp.resolve("trades.log")
        self.Cfg.load(dp)
        self.C.migrate()
        self.C.migrate14()
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        self.ids = [str(p.id) for p in self.C.all()]

    def state(self):
        return {i: (float(self.M.factor(i)), int(self.M.quote(i, 1, True)), int(self.M.quote(i, 1, False)),
                    int(self.M.getBought(i)), int(self.M.getSold(i))) for i in self.ids}

    def tick(self, now):
        self.M.decay(now)
        self.M.flush()
        self.C.tick()


def counting_map(real):
    """a java.util.Map (JPype proxy) over the real bridge that counts put() per key - proves what a call publishes"""
    from jpype import JImplements, JOverride

    @JImplements("java.util.Map")
    class CountMap(object):
        def __init__(self):
            self.puts = {}

        @JOverride
        def size(self): return real.size()
        @JOverride
        def isEmpty(self): return real.isEmpty()
        @JOverride
        def containsKey(self, k): return real.containsKey(k)
        @JOverride
        def containsValue(self, v): return real.containsValue(v)
        @JOverride
        def get(self, k): return real.get(k)

        @JOverride
        def put(self, k, v):
            self.puts[str(k)] = self.puts.get(str(k), 0) + 1
            return real.put(k, v)
        @JOverride
        def remove(self, k): return real.remove(k)
        @JOverride
        def putAll(self, m): return real.putAll(m)
        @JOverride
        def clear(self): return real.clear()
        @JOverride
        def keySet(self): return real.keySet()
        @JOverride
        def values(self): return real.values()
        @JOverride
        def entrySet(self): return real.entrySet()
        @JOverride
        def equals(self, o): return real.equals(o)
        @JOverride
        def hashCode(self): return real.hashCode()
    return CountMap()


def mfile(d):
    p = os.path.join(d, "market.properties")
    return open(p, "rb").read() if os.path.exists(p) else None


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    d7, d8 = os.path.join(scratch, "x7"), os.path.join(scratch, "x8")
    b7 = Bz(OLD_JAR, d7)
    b8 = Bz(jar, d8)
    br = Sys.getProperties().get("skyy.bridge")
    K.check(br is not None, "X: the bridge exists")
    K.eq(Sys.identityHashCode(b8.U.bridge()), Sys.identityHashCode(br), "X BzUtil.bridge = the System map")
    K.eq(Sys.identityHashCode(b8.U.BRIDGE), Sys.identityHashCode(br), "X BzUtil.BRIDGE caches it")
    K.eq(Sys.identityHashCode(b8.U.bridge0()), Sys.identityHashCode(br), "X bridge0 finds it")
    CR = JClass(PKG + "CfgRows", loader=b8.L)
    K.eq(Sys.identityHashCode(CR.bridge()), Sys.identityHashCode(br), "X the kit's CfgRows.bridge = the same map")
    K.eq(Sys.identityHashCode(CR.BRIDGE), Sys.identityHashCode(br), "X CfgRows.BRIDGE caches it")
    K.eq(b8.n, b7.n, "X the same catalog size (%d)" % b7.n)
    K.eq(b8.ids, b7.ids, "X the same products in the same order")
    K.eq(b8.state(), b7.state(), "X the same quotes after the start")
    # CSV: re-put only when the text changed (a counting proxy as 0.1.8's cached bridge map)
    cm = counting_map(br)
    b8.U.BRIDGE = cm
    b8.M.publishAll()
    K.eq(cm.puts.get("bazaar:products", 0), 0, "X publishAll with an unchanged catalog does not re-put the CSV")
    K.eq(cm.puts.get("bazaar:buy:" + b8.ids[0], 0), 1, "X publishAll still re-quotes every product (catalog / price changes)")
    br.put("bazaar:products", "changed-by-someone")
    b8.M.publishAll()
    K.eq(cm.puts.get("bazaar:products", 0), 1, "X a CSV someone replaced is put back")
    b8.U.BRIDGE = br
    K.eq(str(br.get("bazaar:products")), ",".join(b8.ids), "X the CSV = every product id")
    b8.M.unpublishAll()
    K.check(br.get("bazaar:products") is None and b8.M.CSV is None, "X unpublishAll removes the CSV")
    b8.M.publishAll()
    K.eq(str(br.get("bazaar:products")), ",".join(b8.ids), "X publishAll puts it back")
    rnd = random.Random(818)
    T = int(Sys.currentTimeMillis())
    # first decay: LAST was 0 (fresh) on both
    b7.tick(T)
    b8.tick(T)
    ids = b8.ids
    diffs = restarts = writes8 = writes7 = 0
    for step in range(400):
        r = rnd.random()
        if r < 0.40:
            i, q, buy = rnd.choice(ids), rnd.choice([1, 5, 64, 400]), rnd.random() < 0.5
            b7.M.apply(i, q, buy)
            b8.M.apply(i, q, buy)
            what = "apply %s %d %s" % (i, q, buy)
        elif r < 0.43:
            i = rnd.choice(ids + [None])
            b7.M.reset(i)
            b8.M.reset(i)
            what = "reset %s" % i
        else:
            T += rnd.choice([1000, 10000, 10000, 10000, 60000, 300000, 900000, 7200000])
            f8_before = {i: float(b8.M.factor(i)) for i in ids}
            m7, m8 = mfile(d7), mfile(d8)
            dirty_before, saved_before = bool(b8.M.DIRTY), int(b8.M.SAVED)
            b7.tick(T)
            cm = counting_map(br)
            b8.U.BRIDGE = cm
            b8.M.decay(T)
            b8.U.BRIDGE = br
            moved_ids = sorted(i for i in ids if float(b8.M.factor(i)) != f8_before[i])
            moved = len(moved_ids)
            K.eq(sorted(set(k.split(":", 2)[2] for k in cm.puts)), moved_ids, "X step %d: the decay put exactly the moved ids" % step)
            K.check(all(v == 1 for v in cm.puts.values()) and "bazaar:products" not in cm.puts, "X step %d: one put per moved quote, no CSV" % step)
            if not K.eq(int(b8.M.MOVED), moved, "X step %d: decay publishes exactly the ids that moved" % step):
                pass
            due = dirty_before or (T - saved_before >= 300000)
            b8.M.flush()
            b8.C.tick()
            if mfile(d8) != m8:
                writes8 += 1
                b8.M.SAVED = T      # the harness clock (the tick's own clock is System.currentTimeMillis)
            elif due:
                K.check(False, "X step %d: a due write did not happen" % step)
            if mfile(d7) != m7:
                writes7 += 1
            K.check(due or mfile(d8) == m8, "X step %d: a decay-only change < 5 min after the last write is not written" % step)
            what = "tick +%d" % (T - 0)
        s7, s8 = b7.state(), b8.state()
        if s7 != s8:
            diffs += 1
            if diffs <= 3:
                bad = [i for i in ids if s7[i] != s8[i]][:3]
                K.check(False, "X step %d (%s): 0.1.7 %r vs 0.1.8 %r" % (step, what, [s7[i] for i in bad], [s8[i] for i in bad]))
        if rnd.random() < 0.07:
            restarts += 1
            m8 = mfile(d8)
            b7.M.flush()
            b8.M.flush()          # what the next tick would write (trades); a decay-only change stays deferred
            if mfile(d8) != m8:
                b8.M.SAVED = T
            r7, r8 = os.path.join(scratch, "r7-%d" % step), os.path.join(scratch, "r8-%d" % step)
            shutil.copytree(d7, r7)
            shutil.copytree(d8, r8)
            n7, n8 = Bz(OLD_JAR, r7), Bz(jar, r8)
            n7.M.decay(T)
            n8.M.decay(T)
            t7, t8 = n7.state(), n8.state()
            # a restart = the factors decayed from the file's lastDecayMillis to now: equal to memory within float rounding,
            # quotes identical; trades of the last tick that were not flushed yet are lost on BOTH (same 10 s window as 0.1.7)
            fd = max(abs(t8[i][0] - s8[i][0]) for i in ids)
            qd = [i for i in ids if t8[i][1:] != s8[i][1:]]
            K.check(fd < 1e-9, "X restart %d: 0.1.8 factors from its (deferred) file = memory (max diff %g)" % (step, fd))
            K.check(not qd, "X restart %d: 0.1.8 quotes after a restart = memory (%s)" % (step, qd[:3]))
            K.check(all(t8[i][1:3] == t7[i][1:3] for i in ids), "X restart %d: 0.1.8 restart quotes = 0.1.7 restart quotes" % step)
            # rollback: 0.1.7 on 0.1.8's folder
            rb = os.path.join(scratch, "rb-%d" % step)
            shutil.copytree(d8, rb)
            o7 = Bz(OLD_JAR, rb)
            o7.M.decay(T)
            K.check(all(o7.state()[i][1:3] == t8[i][1:3] for i in ids), "X rollback %d: 0.1.7 on 0.1.8's files = the same quotes" % step)
            for x in (r7, r8, rb):
                shutil.rmtree(x, ignore_errors=True)
            # the restarts re-published into the shared bridge with their own state: republish the live 0.1.8 values
            b8.M.publishAll()
    K.eq(diffs, 0, "X: 400 steps, every factor / quote / counter identical on 0.1.7 and 0.1.8")
    K.check(writes8 < writes7, "X: 0.1.8 wrote market.properties %d times, 0.1.7 %d times" % (writes8, writes7))
    K.notes.append("X: 400 steps, %d restarts, market.properties writes 0.1.7 %d / 0.1.8 %d" % (restarts, writes7, writes8))
    # idle market: nothing published, nothing written for 5 minutes, then one write; an unchanged id is not re-put
    b8.M.reset(None)
    b8.M.flush()
    b8.M.SAVED = T
    T += 10000
    b8.M.decay(T)
    K.eq(int(b8.M.MOVED), 0, "X idle: a decay with every factor at 1.0 publishes nothing")
    m = mfile(d8)
    b8.M.flush()
    K.check(mfile(d8) == m and bool(b8.M.PEND), "X idle: nothing written, PEND set")
    T += 280000
    b8.M.decay(T)
    b8.M.flush()
    K.check(mfile(d8) == m, "X idle: still nothing at 290 s since the write")
    T += 10000
    b8.M.decay(T)
    b8.M.flush()
    K.check(mfile(d8) != m and not bool(b8.M.PEND), "X idle: written once 5 minutes passed (lastDecayMillis), PEND cleared")
    K.check(("lastDecayMillis=%d" % T).encode() in mfile(d8), "X idle: the written lastDecayMillis is the latest")
    # an unchanged id is not re-put; a moved one is
    i1, i2 = ids[0], ids[1]
    b8.M.apply(i1, 50, True)
    br.remove("bazaar:buy:" + i2)
    T += 10000
    b8.M.decay(T)
    K.check(br.get("bazaar:buy:" + i2) is None, "X an id whose factor did not move is not re-put")
    K.eq(int(br.get("bazaar:buy:" + i1)), int(b8.M.quote(i1, 1, True)), "X the moved id is published with its new quote")
    K.eq(int(b8.M.MOVED), 1, "X MOVED = 1")
    b8.M.publish(i2)
    # trade -> DIRTY -> written by the next flush with the current lastDecayMillis
    m = mfile(d8)
    b8.M.apply(i1, 1, False)
    b8.M.flush()
    b8.M.SAVED = T
    K.check(mfile(d8) != m and ("lastDecayMillis=%d" % T).encode() in mfile(d8), "X a trade is written at the next flush with the current lastDecayMillis")
    # forcePending (shutdown)
    T += 10000
    b8.M.decay(T)
    m = mfile(d8)
    b8.M.flush()
    K.check(mfile(d8) == m and bool(b8.M.PEND), "X a pending decay waits")
    b8.M.forcePending()
    b8.M.flush()
    K.check(mfile(d8) != m and not bool(b8.M.PEND), "X forcePending (shutdown) writes it")
    b8.M.forcePending()
    K.check(not bool(b8.M.DIRTY), "X forcePending with nothing pending marks nothing")
    # load resets PEND
    T += 10000
    b8.M.decay(T)
    K.check(bool(b8.M.PEND), "X PEND before load")
    b8.M.load()
    K.check(not bool(b8.M.PEND) and bool(b8.M.DIRTY), "X load: PEND cleared, DIRTY (0.1.7's load behaviour)")
    K.eq(int(b8.M.PEND_MS), 300000, "X PEND_MS = 5 minutes")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    base = os.path.dirname(home)
    d7 = os.path.join(base, "live7")
    shutil.copytree(home, d7)
    before7, before8 = HK.tree_hash(d7), HK.tree_hash(home)
    res = []
    for start in (1, 2):
        a = Bz(OLD_JAR, d7)
        b = Bz(jar, home)
        now = int(Sys.currentTimeMillis())
        a.tick(now)
        b.M.decay(now)
        b.M.flush()
        b.C.tick()
        sa, sb = a.state(), b.state()
        K.eq(b.ids, a.ids, "D%d: the same products" % start)
        K.check(all(abs(sa[i][0] - sb[i][0]) < 1e-9 and sa[i][1:] == sb[i][1:] for i in a.ids), "D%d: the same factors, quotes and counters" % start)
        res.append((len(a.ids), sum(1 for i in a.ids if sa[i][0] != 1.0)))
        # shutdown
        b.M.decay(now)
        b.M.forcePending()
        b.M.flush()
        b.C.flushIfDirty()
        a.M.decay(now)
        a.M.flush()
        a.C.flushIfDirty()
    a7, a8 = HK.tree_hash(d7), HK.tree_hash(home)
    ch7 = sorted(k for k in set(before7) | set(a7) if before7.get(k) != a7.get(k))
    ch8 = sorted(k for k in set(before8) | set(a8) if before8.get(k) != a8.get(k))
    K.check(set(ch8) <= set(ch7) | {"market.properties"}, "D: 0.1.8 changes no file 0.1.7 does not (0.1.7 %s, 0.1.8 %s)" % (ch7, ch8))
    K.check(set(ch8) <= {"market.properties", "trades.log"}, "D: only market.properties / trades.log can change (%s)" % ch8)
    K.notes.append("D: %d products, %d with a demand factor away from 1.0; changed files 0.1.7 %s / 0.1.8 %s" % (res[0][0], res[0][1], ch7, ch8))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
