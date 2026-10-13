"""Harness for SkyyCoins 0.1.6 (write-behind ledger + lock-free bridge; tools/coins_0_1_6_patch.py).
Build first: python tools/coins_0_1_6_patch.py && python SkyyCoins/build_skyycoins_0.1.6.py

    python SkyyCoins/test_skyycoins_0.1.6.py [--keep]

Phases (each a fresh child JVM, the game's JRE, -Xverify:all where it matters, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.5 -> 0.1.6: exactly the listed members differ (+ CoinIO, CoinEvents)
  X  exec     EVERY NEW CODE PATH: bridge0 / bridge (creation, identity, cached), readK / installK / loadK0 / loadK (no file, a balance,
              an unreadable file = frozen, retried, never written over), setK -> DIRTY (no write on the caller), takeBatch, flush0 /
              flushNow (journal -> files -> journal gone; 0.1.5 format byte for byte), coalescing (200 changes = 1 write), redirty +
              ioWarn (an unwritable folder), recover (no journal / a journal / a bad journal kept), keyOk, prefetch (no publish),
              CoinIO (flush + prefetch + the SkyyCoins-IO daemon thread), CoinEvents (quit = flush now), ioRun, stopIO (writer stopped,
              synchronous flush, the WARN when a balance cannot be written), the public ops reading before the lock, CoinFn
  K  CRASH AT EVERY STEP: a batch (a /pay transfer + another purse) stopped at each flush step (STOP_AT) and restarted in a FRESH class
              loader on what is on disk: every purse is all-old or all-new together, the transfer's two sides never split, no coin made
              or lost
  KK KILL THE WRITER: a child JVM runs 8 threads of random /pay transfers while SkyyCoins-IO flushes every second; the parent KILLS the
              process at a random moment (5 rounds); a fresh JVM recovers: the sum of every purse is exactly the starting sum, every file
              reads, the journal (if any) was replayed
  R  ROLLBACK + IDENTITY: the same 3,000 random ops (get / add / take / set / transfer / refused takes / unreadable file) on 0.1.5 and 0.1.6
              in their own loaders: the same answers and balances after every op; 0.1.5 reads every file 0.1.6 wrote (and 0.1.6 0.1.5's)
  S  STRESS: 8 Python threads x 2,000 transfers through CoinStore.transfer while the real writer runs: disk = memory, sum conserved
  F  FIX ROUND (critic findings): F1 a STALE journal (a 0.1.5 run after a rollback wrote a purse later with another value) is NOT
              replayed (kept as balances-journal.stale-*.properties; no spent coin comes back) while a journal whose newer files hold
              its own values still replays; F2 a change after stopIO() is written at once (add + transfer + take); F3 coins:fn:flush
              writes every dirty purse now (Integer count, 0 when clean); F4 firstSeen publishes coins:<uuid> for a prefetched
              (unpublished) purse and grants starter coins once for a new key
  G  SECOND FIX ROUND: G1 a replay whose 2nd balance write fails (crash hook) keeps both sides in memory + a SUPERSET journal on disk:
              a later batch never drops its keys, a crash then still replays both sides, a later flush finishes it; G2 the same failing
              before the new journal leaves the old journal byte for byte; G3 an unreadable journal = RECOVER_PENDING: loads frozen, no
              flush, CoinIO(0) retries it, replayed once readable; G4 10 failures move it aside (balances-journal.failed-*); G5 a batch of
              one purse skips the journal, two purses write it
  D  START TWICE on a scratch COPY of the live Skyy_SkyyCoins: recover (nothing), every purse read by 0.1.5 and 0.1.6 = the same, a flush
              writes nothing, no file changes on either start
  AA engine-access audit
Scratch: tools/dev/scratch/perfecon/coins (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, random, subprocess, time, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.6"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCoins-0.1.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfecon", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCoins")

EXPECT = {
    "CoinStore": ["+f BRIDGE", "+f DIRTY", "+f IO", "+f IOLOCK", "+f IOWARN", "+f JOURNAL", "+f STEPS", "+f STOP_AT", "+f WRITES",
                  "+m bridge0", "~m bridge", "+m readK", "+m installK", "+m loadK0", "~m loadK", "-m saveK", "+m step", "+m writeProps",
                  "+m writeKey", "+m keyOk", "+m takeBatch", "+m redirty", "+m ioWarn", "+m flush0", "+m flushNow", "+m recover",
                  "+m ioRun", "~m setK", "~m known", "~m get", "~m set", "~m add", "~m take", "~m transfer", "~m publish",
                  "+m prefetch", "+m stopIO", "~<clinit>",
                  # fix round (D): stale journal, late changes, first-sight publish
                  "+f STOPPED", "+m staleKey", "~m recheck", "+m firstSeen",
                  # second fix round (D2): a start-up journal that cannot be replayed stays + is retried
                  "+f RECOVER_PENDING", "+f RECOVER_TRIES", "+m foldK", "+m recoverFail", "+m ioTick"],
    "CoinTick": ["~m dispatch"],
    "CoinTask": ["~m run"],
    "CoinFn": ["~m apply"],
    "SkyyCoinsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["CoinIO", "CoinEvents"]


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    F = JClass("java.io.File")
    arr = JArray(URL)(1)
    arr[0] = F(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def store_in(loader, d):
    """a fresh CoinStore (its own loader = a server restart) on balances dir d"""
    from jpype import JClass
    CS = JClass(PKG + "CoinStore", loader=loader)
    Paths = JClass("java.nio.file.Paths")
    CS.DIR = Paths.get(os.path.join(d, "balances"))
    try:
        CS.JOURNAL = Paths.get(os.path.join(d, "balances-journal.properties"))
    except AttributeError:
        pass
    return CS


def disk(d):
    out = {}
    bd = os.path.join(d, "balances")
    if not os.path.isdir(bd):
        return out
    for f in os.listdir(bd):
        if f.endswith(".properties"):
            txt = open(os.path.join(bd, f), encoding="latin-1").read()
            v = [l.split("=", 1)[1].strip() for l in txt.splitlines() if l.startswith("balance=")]
            try:
                out[f[:-11]] = int(v[0]) if v else None
            except ValueError:
                out[f[:-11]] = "BAD " + v[0]
    return out


def uu(i):
    return "%08d-0000-4000-8000-%012d" % (i, i)


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    UUID = JClass("java.util.UUID")
    Long = JClass("java.lang.Long")
    d = os.path.join(scratch, "x")
    os.makedirs(d, exist_ok=True)
    # ---- bridge: created on the first call (no map yet), the same map every time, cached in BRIDGE, the System property holds it
    K.check(Sys.getProperties().get("skyy.bridge") is None, "X bridge: no map before the first call")
    L = loader_for(jar)
    CS = store_in(L, d)
    m1 = CS.bridge()
    K.check(Sys.getProperties().get("skyy.bridge") is not None and Sys.getProperties().get("skyy.bridge").equals(m1) and
            Sys.getProperties().get("skyy.bridge") == m1, "X bridge: the first call creates + stores the map")
    K.check(CS.bridge() is m1 or CS.bridge().equals(m1), "X bridge: the same map on the next call")
    K.check(CS.BRIDGE is not None and JClass("java.lang.System").identityHashCode(CS.BRIDGE) == JClass("java.lang.System").identityHashCode(m1), "X bridge: cached in BRIDGE")
    L2 = loader_for(jar)
    CS2 = store_in(L2, os.path.join(scratch, "x2"))
    K.check(Sys.identityHashCode(CS2.bridge()) == Sys.identityHashCode(m1), "X bridge: a second jar (another loader) finds the same map")
    K.check(Sys.identityHashCode(CS.bridge0()) == Sys.identityHashCode(m1), "X bridge0 returns the existing map")
    br = m1
    a, b, c = UUID.fromString(uu(1)), UUID.fromString(uu(2)), UUID.fromString(uu(3))
    # ---- reads: no file / a balance / unreadable
    K.check(CS.get(a) == 0 and not CS.known(a), "X loadK: no file = no balance (0, unknown)")
    K.check(str(br.get("coins:" + str(a))) == "0", "X loadK publishes coins:<uuid> on the first load")
    os.makedirs(os.path.join(d, "balances"), exist_ok=True)
    open(os.path.join(d, "balances", uu(2) + ".properties"), "w").write("#SkyyCoins\nbalance=4242\n")
    K.eq(int(CS.get(b)), 4242, "X loadK: a balance file")
    open(os.path.join(d, "balances", uu(3) + ".properties"), "w").write("balance=notanumber\n")
    bad_bytes = open(os.path.join(d, "balances", uu(3) + ".properties"), "rb").read()
    try:
        CS.get(c)
        K.check(False, "X unreadable: get must throw")
    except Exception as e:
        K.check("unreadable" in str(e), "X unreadable: get throws (%s)" % str(e)[:80])
    K.check(not CS.LOADED.containsKey(uu(3)), "X unreadable: never cached as loaded")
    r = CS.readK(uu(3))
    K.check(r is not None and JClass("java.lang.Throwable").class_.isInstance(r), "X readK returns the Throwable for an unreadable file")
    K.check(not CS.installK(c, uu(3), r, True), "X installK refuses an unreadable read")
    Fn = JClass(PKG + "CoinFn", loader=L)
    arr = JArray(JObject)(2)
    arr[0] = c
    arr[1] = Long.valueOf(5)
    K.check(Fn("take").apply(arr) is None and Fn("add").apply(arr) is None, "X unreadable: coins:fn:take / add answer null")
    # ---- writes: memory first, nothing on disk until a flush (no write on the caller's thread)
    w0 = int(CS.WRITES)
    K.eq(int(CS.add(a, 1000)), 1000, "X add")
    K.check(CS.take(a, 300), "X take")
    K.check(not CS.take(a, 10 ** 9), "X a take above the balance is refused")
    K.check(CS.transfer(a, b, 200), "X transfer")
    try:
        CS.transfer(a, c, 1)
        K.check(False, "X a transfer to an unreadable purse must throw")
    except Exception as e:
        K.check("unreadable" in str(e), "X a transfer to an unreadable purse is refused before anything moves")
    K.eq((int(CS.get(a)), int(CS.get(b))), (500, 4442), "X balances in memory")
    K.eq(int(CS.WRITES), w0, "X no file written by the ops (write-behind)")
    K.check(not os.path.exists(os.path.join(d, "balances", uu(1) + ".properties")), "X the new purse has no file yet")
    K.check(CS.DIRTY.containsKey(uu(1)) and CS.DIRTY.containsKey(uu(2)) and not CS.DIRTY.containsKey(uu(3)), "X DIRTY = the changed keys")
    K.eq(int(CS.flushNow()), 2, "X flushNow writes the 2 dirty keys")
    K.eq(disk(d).get(uu(1)), 500, "X file a")
    K.eq(disk(d).get(uu(2)), 4442, "X file b")
    K.check(open(os.path.join(d, "balances", uu(3) + ".properties"), "rb").read() == bad_bytes, "X the unreadable file is untouched")
    K.check(not os.path.exists(os.path.join(d, "balances-journal.properties")), "X the journal is gone after a full flush")
    txt = open(os.path.join(d, "balances", uu(1) + ".properties"), encoding="latin-1").read().splitlines()
    K.check(txt[0] == "#SkyyCoins" and txt[1].startswith("#") and txt[2] == "balance=500" and len(txt) == 3, "X the 0.1.5 file format: %r" % txt)
    K.eq(int(CS.flushNow()), 0, "X nothing dirty = nothing written")
    # coalescing
    w1 = int(CS.WRITES)
    for i in range(200):
        CS.add(a, 1)
    K.eq(int(CS.flushNow()), 1, "X 200 changes of one purse = 1 key")
    K.eq(int(CS.WRITES) - w1, 1, "X ... = 1 file write")
    K.eq(disk(d).get(uu(1)), 700, "X coalesced value")
    # set + known + starterK + publish
    CS.set(a, 900)
    K.check(CS.known(a), "X known")
    e = UUID.fromString(uu(5))
    K.check(CS.starterK(e, uu(5), 10000) and not CS.starterK(e, uu(5), 10000), "X starter coins once")
    CS.publish(e)
    K.eq(str(br.get("coins:" + str(e))), "10000", "X publish")
    # prefetch: loaded without a publish
    open(os.path.join(d, "balances", uu(6) + ".properties"), "w").write("balance=66\n")
    f6 = UUID.fromString(uu(6))
    br.remove("coins:" + str(f6))
    IO = JClass(PKG + "CoinIO", loader=L)
    IO(1, f6).run()
    K.check(CS.LOADED.containsKey(uu(6)) and br.get("coins:" + str(f6)) is None, "X prefetch loads the purse and does not publish")
    K.eq(int(CS.get(f6)), 66, "X a prefetched purse")
    IO(0, None).run()
    K.check(CS.DIRTY.isEmpty(), "X CoinIO(0) flushes")
    K.check(CS.keyOk(uu(1)) and CS.keyOk(uu(1) + "-p2") and not CS.keyOk("..\\x") and not CS.keyOk("a/b") and not CS.keyOk("") and not CS.keyOk(None), "X keyOk")
    # ---- the IO thread + events + stopIO
    t = IO(0, None).newThread(JClass("java.lang.Thread")())
    K.check(str(t.getName()) == "SkyyCoins-IO" and t.isDaemon(), "X the writer thread: SkyyCoins-IO, daemon")
    Ex = JClass("java.util.concurrent.Executors")
    TU = JClass("java.util.concurrent.TimeUnit")
    ex = Ex.newSingleThreadScheduledExecutor(IO(0, None))
    ex.scheduleWithFixedDelay(IO(0, None), 1000, 1000, TU.MILLISECONDS)
    CS.IO = ex
    CS.add(a, 5)
    Ev = JClass(PKG + "CoinEvents", loader=L)
    Ev(True).accept(None)
    deadline = time.time() + 5
    while time.time() < deadline and disk(d).get(uu(1)) != 905:
        time.sleep(0.05)
    K.eq(disk(d).get(uu(1)), 905, "X CoinEvents(quit) -> the writer flushes at once")
    names = [str(x.getName()) for x in JClass("java.lang.Thread").getAllStackTraces().keySet()]
    K.check("SkyyCoins-IO" in names, "X a live SkyyCoins-IO thread")
    Ev(False).accept(JObject("not an event"))
    K.check(True, "X CoinEvents(ready) ignores a wrong event (no throw)")
    CS.add(b, 1)
    time.sleep(1.6)
    K.eq(disk(d).get(uu(2)), 4443, "X the 1 s schedule flushes")
    CS.add(b, 1)
    CS.stopIO()
    K.check(CS.IO is None and ex.isShutdown(), "X stopIO stops the writer")
    K.eq(disk(d).get(uu(2)), 4444, "X stopIO flushes synchronously")
    CS.ioRun(IO(0, None))
    K.check(True, "X ioRun with no writer = no-op")
    # a balance that cannot be written: redirty + ioWarn + the stopIO WARN path (STOPPED reset: after stopIO every op flushes at
    # once - phase F2 - and this block needs the change to stay dirty until the explicit flush)
    CS.STOPPED = False
    CS.add(a, 1)
    blocker = os.path.join(scratch, "blockfile")
    open(blocker, "w").write("x")
    old_dir = CS.DIR
    CS.DIR = JClass("java.nio.file.Paths").get(os.path.join(blocker, "balances"))
    CS.IOWARN = 0
    K.eq(int(CS.flushNow()), -1, "X an unwritable folder: flush fails")
    K.check(CS.DIRTY.containsKey(uu(1)) and int(CS.IOWARN) > 0, "X the batch is back in DIRTY + one WARN")
    CS.stopIO()
    K.check(CS.DIRTY.containsKey(uu(1)), "X stopIO with an unwritable folder keeps it dirty (WARN)")
    CS.DIR = old_dir
    K.eq(int(CS.flushNow()), 1, "X written once the folder works")
    # ---- recover: none / a journal / a bad journal
    K.eq(int(CS.recover()), 0, "X recover: no journal")
    jp = os.path.join(d, "balances-journal.properties")
    open(jp, "w").write("count=2\nk.0=%s\nv.0=111\nk.1=%s\nv.1=222\n" % (uu(1), uu(2)))
    K.eq(int(CS.recover()), 2, "X recover replays a journal")
    K.eq((disk(d).get(uu(1)), disk(d).get(uu(2))), (111, 222), "X ... into the balance files")
    K.check(not os.path.exists(jp), "X ... and deletes it")
    for bad in ("count=1\nk.0=../../evil\nv.0=5\n", "count=2\nk.0=%s\nv.0=5\n" % uu(1), "count=1\nk.0=%s\nv.0=-4\n" % uu(1), "garbage"):
        open(jp, "w").write(bad)
        K.eq(int(CS.recover()), -1, "X a bad journal is refused (%r)" % bad[:20])
        K.check(os.path.exists(jp), "X ... and KEPT")
        K.eq(disk(d).get(uu(1)), 111, "X ... nothing written from it")
    os.remove(jp)
    CS.RECOVER_PENDING = False
    CS.RECOVER_TRIES = 0
    # step(): the test hook is off by default
    K.eq(int(CS.STOP_AT), 0, "X STOP_AT is off by default")
    K.save()


# ====================================================================================================== K: crash at every step
def run_crash(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    a, b, c = UUID.fromString(uu(11)), UUID.fromString(uu(12)), UUID.fromString(uu(13))
    OLD, NEW = (1000, 500, 7), (700, 800, 12)
    for stop in range(1, 7):
        d = os.path.join(scratch, "k%d" % stop)
        CS = store_in(loader_for(jar), d)
        CS.set(a, OLD[0]); CS.set(b, OLD[1]); CS.set(c, OLD[2])
        K.eq(int(CS.flushNow()), 3, "K%d: the starting state is on disk" % stop)
        K.check(CS.transfer(a, b, 300), "K%d: /pay 300" % stop)
        CS.add(c, 5)
        CS.STEPS = 0
        CS.STOP_AT = stop
        r = int(CS.flushNow())
        state = disk(d)
        got = (state.get(uu(11)), state.get(uu(12)), state.get(uu(13)))
        has_j = os.path.exists(os.path.join(d, "balances-journal.properties"))
        if stop <= 5:
            K.eq(r, -1, "K%d: the flush stopped" % stop)
        # restart: a fresh loader on the disk as the crash left it
        CS2 = store_in(loader_for(jar), d)
        rec = int(CS2.recover())
        after = (int(CS2.get(a)), int(CS2.get(b)), int(CS2.get(c)))
        K.check(after in (OLD, NEW), "K%d: after the restart every purse is all-old or all-new: %r (disk before %r, journal %s, replayed %d)" % (stop, after, got, has_j, rec))
        K.eq(after[0] + after[1], 1500, "K%d: the transfer's two sides never split (no coin made or lost)" % stop)
        want = OLD if stop == 1 else NEW
        K.eq(after, want, "K%d: the expected side of the crash" % stop)
        K.check(not os.path.exists(os.path.join(d, "balances-journal.properties")), "K%d: no journal left after the restart" % stop)
        K.notes.append("K stop at %d: disk %r journal=%s -> replayed %d -> %r" % (stop, got, has_j, rec, after))
    K.save()


# ====================================================================================================== KK: kill the writer process
def run_killer(out, jar, scratch, _home):
    """child: 8 threads of random transfers + the real writer; runs until killed"""
    from jpype import JClass, JImplements, JOverride
    HK.jvm([B.SERVER_JAR], verify=False)
    d = HK.arg("--kdir")
    UUID = JClass("java.util.UUID")
    L = loader_for(jar)
    CS = store_in(L, d)
    CS.recover()
    us = [UUID.fromString(uu(100 + i)) for i in range(12)]
    for u in us:
        CS.get(u)
    IO = JClass(PKG + "CoinIO", loader=L)
    ex = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(IO(0, None))
    ex.scheduleWithFixedDelay(IO(0, None), 50, 50, JClass("java.util.concurrent.TimeUnit").MILLISECONDS)
    CS.IO = ex
    open(os.path.join(d, "ready"), "w").write("1")
    import threading

    def worker(seed):
        rnd = random.Random(seed)
        while True:
            x, y = rnd.sample(us, 2)
            try:
                CS.transfer(x, y, rnd.randint(1, 40))
            except Exception:
                pass
    for i in range(8):
        threading.Thread(target=worker, args=(i,), daemon=True).start()
    time.sleep(60)


def run_killcheck(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    for rnd in range(5):
        d = os.path.join(scratch, "kill%d" % rnd)
        CS = store_in(loader_for(jar), d)
        has_j = os.path.exists(os.path.join(d, "balances-journal.properties"))
        rec = int(CS.recover())
        tot = sum(int(CS.get(UUID.fromString(uu(100 + i)))) for i in range(12))
        K.eq(tot, 12 * 1000, "KK%d: after the kill + restart the sum of every purse is the starting sum" % rnd)
        K.check(rec >= 0, "KK%d: the recovery ran (journal %s, replayed %d)" % (rnd, has_j, rec))
        dk = disk(d)
        K.check(all(isinstance(v, int) for v in dk.values()), "KK%d: every balance file reads" % rnd)
        K.check(any(v != 1000 for v in dk.values()), "KK%d: the killed run had saved transfers (not the starting files)" % rnd)
        K.notes.append("KK%d: journal at kill %s, replayed %d, files %d, sum %d" % (rnd, has_j, rec, len(disk(d)), tot))
    K.save()


# ====================================================================================================== R: identical to 0.1.5 + rollback
def run_identity(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    d5, d6 = os.path.join(scratch, "r5"), os.path.join(scratch, "r6")
    for dd in (d5, d6):
        os.makedirs(os.path.join(dd, "balances"), exist_ok=True)
        open(os.path.join(dd, "balances", uu(209) + ".properties"), "w").write("balance=xx\n")   # an unreadable purse in both
    S5, S6 = store_in(loader_for(OLD_JAR), d5), store_in(loader_for(jar), d6)
    us = [UUID.fromString(uu(200 + i)) for i in range(10)]
    rnd = random.Random(1013)
    diffs = 0

    def call(S, op, x, y, n):
        try:
            if op == "get":
                return int(S.get(x))
            if op == "add":
                return int(S.add(x, n))
            if op == "take":
                return bool(S.take(x, n))
            if op == "set":
                S.set(x, n)
                return int(S.get(x))
            if op == "transfer":
                return bool(S.transfer(x, y, n))
            if op == "known":
                return bool(S.known(x))
        except Exception as e:
            return "EXC " + str(e).split(":")[0][:60]
    for i in range(3000):
        op = rnd.choice(["get", "add", "add", "take", "take", "set", "transfer", "transfer", "known"])
        x, y = rnd.choice(us), rnd.choice(us)
        n = rnd.choice([0, 1, 5, 50, 500, 5000, 10 ** 6, -30])
        r5, r6 = call(S5, op, x, y, n), call(S6, op, x, y, n)
        if r5 != r6:
            diffs += 1
            if diffs < 5:
                K.check(False, "R op %d %s(%s,%s,%d): 0.1.5 %r vs 0.1.6 %r" % (i, op, x, y, n, r5, r6))
        if i % 500 == 499:
            S6.flushNow()
    K.eq(diffs, 0, "R: 3,000 random ops answer the same on 0.1.5 and 0.1.6")
    good = [u for u in us if str(u) != uu(209)]
    m5 = {str(u): int(S5.get(u)) for u in good}
    m6 = {str(u): int(S6.get(u)) for u in good}
    K.eq(m6, m5, "R: the same balances in memory")
    S6.flushNow()
    K.eq({k: v for k, v in disk(d6).items() if k != uu(209)}, {k: v for k, v in disk(d5).items() if k != uu(209)}, "R: the same balance files")
    K.check(open(os.path.join(d6, "balances", uu(209) + ".properties")).read() == "balance=xx\n", "R: the unreadable purse is untouched")
    # rollback: 0.1.5 reads 0.1.6's files, 0.1.6 reads 0.1.5's
    R5 = store_in(loader_for(OLD_JAR), d6)
    K.eq({str(u): int(R5.get(u)) for u in good}, m6, "R: ROLLBACK - 0.1.5 reads every purse 0.1.6 wrote")
    R6 = store_in(loader_for(jar), d5)
    K.eq({str(u): int(R6.get(u)) for u in good}, m5, "R: 0.1.6 reads every purse 0.1.5 wrote")
    # byte format: a file written by 0.1.5 and by 0.1.6 for the same value differ only in the date comment
    l5 = [l for l in open(os.path.join(d5, "balances", uu(200) + ".properties")).read().splitlines() if not l.startswith("#") or l == "#SkyyCoins"]
    l6 = [l for l in open(os.path.join(d6, "balances", uu(200) + ".properties")).read().splitlines() if not l.startswith("#") or l == "#SkyyCoins"]
    K.eq(l6, l5, "R: the file format is 0.1.5's (besides the date comment)")
    K.save()


# ====================================================================================================== S: stress
def run_stress(out, jar, scratch, _home):
    from jpype import JClass
    import threading
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    d = os.path.join(scratch, "s")
    L = loader_for(jar)
    CS = store_in(L, d)
    us = [UUID.fromString(uu(300 + i)) for i in range(16)]
    for u in us:
        CS.set(u, 1000)
    IO = JClass(PKG + "CoinIO", loader=L)
    ex = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(IO(0, None))
    ex.scheduleWithFixedDelay(IO(0, None), 20, 20, JClass("java.util.concurrent.TimeUnit").MILLISECONDS)
    CS.IO = ex
    errs = []

    def worker(seed):
        rnd = random.Random(seed)
        for _ in range(2000):
            x, y = rnd.sample(us, 2)
            try:
                CS.transfer(x, y, rnd.randint(1, 60))
            except Exception as e:
                errs.append(str(e))
    ts = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    CS.stopIO()
    mem = {str(u): int(CS.get(u)) for u in us}
    K.eq(errs, [], "S: no errors")
    K.eq(sum(mem.values()), 16000, "S: memory sum conserved")
    dk = disk(d)
    K.eq({k: dk.get(k) for k in mem}, mem, "S: disk = memory after stopIO")
    K.check(int(CS.WRITES) > 16, "S: the writer ran (%d writes)" % int(CS.WRITES))
    K.notes.append("S: 16,000 transfers, %d file writes" % int(CS.WRITES))
    K.save()


# ====================================================================================================== F: fix round
def run_fixes(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    a, b = UUID.fromString(uu(401)), UUID.fromString(uu(402))
    # ---- F1: stale journal after a rollback round trip (0.1.6 crash -> 0.1.5 runs -> 0.1.6 again)
    d = os.path.join(scratch, "f1")
    CS = store_in(loader_for(jar), d)
    CS.set(a, 500); CS.set(b, 500)
    K.eq(int(CS.flushNow()), 2, "F1: start state on disk")
    jp = os.path.join(d, "balances-journal.properties")
    open(jp, "w").write("count=2\nk.0=%s\nv.0=200\nk.1=%s\nv.1=800\n" % (uu(401), uu(402)))   # a crash right after a /pay 300's journal
    t_j = time.time() - 30
    os.utime(jp, (t_j, t_j))
    for f in (uu(401), uu(402)):
        os.utime(os.path.join(d, "balances", f + ".properties"), (t_j - 30, t_j - 30))
    O5 = store_in(loader_for(OLD_JAR), d)                  # the rollback: 0.1.5 ignores the journal, the player spends 100
    K.check(O5.take(a, 100), "F1: 0.1.5 takes 100 from a (old file 500)")
    K.eq(disk(d).get(uu(401)), 400, "F1: 0.1.5 wrote a = 400")
    C2 = store_in(loader_for(jar), d)                      # 0.1.6 deployed again
    K.eq(int(C2.recover()), 0, "F1: the stale journal is NOT replayed")
    K.eq((disk(d).get(uu(401)), disk(d).get(uu(402))), (400, 500), "F1: no spent coin came back, nothing credited from the stale journal")
    K.check(not os.path.exists(jp), "F1: the journal is moved away")
    st = [f for f in os.listdir(d) if f.startswith("balances-journal.stale-") and f.endswith(".properties")]
    K.eq(len(st), 1, "F1: kept as balances-journal.stale-<millis>.properties")
    K.eq((int(C2.get(a)), int(C2.get(b))), (400, 500), "F1: purses after the restart")
    # F1b: a normal crash mid-batch - the journal's own batch file is NEWER but holds the journal value -> replayed
    d = os.path.join(scratch, "f1b")
    CS = store_in(loader_for(jar), d)
    CS.set(a, 500); CS.set(b, 500)
    CS.flushNow()
    jp = os.path.join(d, "balances-journal.properties")
    open(jp, "w").write("count=2\nk.0=%s\nv.0=200\nk.1=%s\nv.1=800\n" % (uu(401), uu(402)))
    os.utime(jp, (time.time() - 30, time.time() - 30))
    os.utime(os.path.join(d, "balances", uu(402) + ".properties"), (time.time() - 60, time.time() - 60))
    open(os.path.join(d, "balances", uu(401) + ".properties"), "w").write("#SkyyCoins\nbalance=200\n")   # written after the journal
    C2 = store_in(loader_for(jar), d)
    K.eq(int(C2.recover()), 2, "F1b: a journal whose newer file holds its own value replays")
    K.eq((disk(d).get(uu(401)), disk(d).get(uu(402))), (200, 800), "F1b: both sides of the /pay")
    K.check(not os.path.exists(jp) and not [f for f in os.listdir(d) if "stale" in f], "F1b: journal deleted, no stale copy")
    # F1c: a newer but unreadable file is not called stale (the replay writes over it, as before)
    d = os.path.join(scratch, "f1c")
    os.makedirs(os.path.join(d, "balances"), exist_ok=True)
    jp = os.path.join(d, "balances-journal.properties")
    open(jp, "w").write("count=1\nk.0=%s\nv.0=77\n" % uu(401))
    os.utime(jp, (time.time() - 30, time.time() - 30))
    open(os.path.join(d, "balances", uu(401) + ".properties"), "w").write("balance=zz\n")
    C3 = store_in(loader_for(jar), d)
    K.eq(int(C3.recover()), 1, "F1c: an unreadable newer file does not block the replay")
    K.eq(disk(d).get(uu(401)), 77, "F1c: replayed value")
    # ---- F2: changes after stopIO are written at once
    d = os.path.join(scratch, "f2")
    CS = store_in(loader_for(jar), d)
    CS.set(a, 1000); CS.set(b, 0)
    CS.stopIO()
    K.check(bool(CS.STOPPED), "F2: STOPPED after stopIO")
    K.eq((disk(d).get(uu(401)), disk(d).get(uu(402))), (1000, 0), "F2: the shutdown flush")
    CS.add(a, 5)
    K.eq(disk(d).get(uu(401)), 1005, "F2: an add after the shutdown flush is written at once")
    K.check(CS.transfer(a, b, 105), "F2: a late transfer")
    K.eq((disk(d).get(uu(401)), disk(d).get(uu(402))), (900, 105), "F2: both sides of a late transfer written at once")
    K.check(CS.take(b, 5) and disk(d).get(uu(402)) == 100, "F2: a late take is written at once")
    K.check(CS.DIRTY.isEmpty(), "F2: nothing left dirty")
    # ---- F3: coins:fn:flush
    d = os.path.join(scratch, "f3")
    L = loader_for(jar)
    CS = store_in(L, d)
    Fn = JClass(PKG + "CoinFn", loader=L)
    CS.set(a, 321)
    K.check(disk(d).get(uu(401)) is None, "F3: the change is only in memory")
    r = Fn("flush").apply(None)
    K.check(r is not None and int(r) == 1, "F3: coins:fn:flush -> Integer 1 (%r)" % (r,))
    K.eq(disk(d).get(uu(401)), 321, "F3: the purse is on disk right after coins:fn:flush")
    K.eq(int(Fn("flush").apply("x")), 0, "F3: nothing dirty -> 0 (any argument)")
    # ---- F4: firstSeen
    d = os.path.join(scratch, "f4")
    L = loader_for(jar)
    CS = store_in(L, d)
    br = CS.bridge()
    os.makedirs(os.path.join(d, "balances"), exist_ok=True)
    open(os.path.join(d, "balances", uu(403) + ".properties"), "w").write("balance=4567\n")
    c = UUID.fromString(uu(403))
    br.remove("coins:" + str(c))
    JClass(PKG + "CoinIO", loader=L)(1, c).run()
    K.check(br.get("coins:" + str(c)) is None, "F4: the prefetch did not publish")
    K.check(not CS.firstSeen(c, uu(403), 10000), "F4: an existing purse gets no starter coins")
    K.eq(str(br.get("coins:" + str(c))), "4567", "F4: firstSeen publishes the prefetched purse (HUD without SkyyProfiles)")
    e = UUID.fromString(uu(404))
    br.remove("coins:" + str(e))
    K.check(CS.firstSeen(e, uu(404), 10000), "F4: a new key gets starter coins")
    K.eq(str(br.get("coins:" + str(e))), "10000", "F4: ... and they are published")
    K.check(not CS.firstSeen(e, uu(404), 10000) and int(CS.get(e)) == 10000, "F4: only once")
    K.save()


# ====================================================================================================== G: second fix round
def jprops(path):
    out = {}
    for l in open(path, encoding="latin-1").read().splitlines():
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def jkeys(path):
    j = jprops(path)
    return {j["k.%d" % i]: int(j["v.%d" % i]) for i in range(int(j["count"]))}


def run_fix2(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    a, b, c = UUID.fromString(uu(501)), UUID.fromString(uu(502)), UUID.fromString(uu(503))

    def setup(name):
        d = os.path.join(scratch, name)
        CS = store_in(loader_for(jar), d)
        CS.set(a, 500); CS.set(b, 500)
        K.eq(int(CS.flushNow()), 2, "%s: start state on disk" % name)
        jp = os.path.join(d, "balances-journal.properties")
        open(jp, "w").write("count=2\nk.0=%s\nv.0=200\nk.1=%s\nv.1=800\n" % (uu(501), uu(502)))   # a crash right after a /pay 300's journal
        t = time.time() - 30
        for f in (uu(501), uu(502)):
            os.utime(os.path.join(d, "balances", f + ".properties"), (t - 30, t - 30))
        os.utime(jp, (t, t))
        return d, jp
    # ---- G1: the replay's 2nd balance write fails (the critic's half-replay)
    d, jp = setup("g1")
    C2 = store_in(loader_for(jar), d)
    C2.STEPS = 0
    C2.STOP_AT = 3                       # 1 = before the journal, 2 = after it, 3 = after the 1st balance file
    K.eq(int(C2.recover()), 2, "G1: the journal is folded into memory (2 balances)")
    K.check(not bool(C2.RECOVER_PENDING), "G1: not pending (the values are in memory, dirty)")
    on = disk(d)
    K.check(sorted([on.get(uu(501)), on.get(uu(502))]) in ([200, 500], [500, 800]), "G1: the disk is half-written as the hook wanted: %r" % on)
    K.eq((int(C2.get(a)), int(C2.get(b))), (200, 800), "G1: memory holds BOTH sides of the /pay")
    K.check(C2.DIRTY.containsKey(uu(501)) and C2.DIRTY.containsKey(uu(502)), "G1: both still dirty (retried)")
    K.eq(jkeys(jp), {uu(501): 200, uu(502): 800}, "G1: a journal with both sides is on disk")
    C2.add(c, 7)
    C2.STEPS = 0
    C2.STOP_AT = 2                       # the next batch stops right after ITS journal
    K.eq(int(C2.flushNow()), -1, "G1: the next flush stops after its journal")
    K.eq(jkeys(jp), {uu(501): 200, uu(502): 800, uu(503): 7}, "G1: the new journal is a SUPERSET (the /pay's keys are never dropped)")
    C3 = store_in(loader_for(jar), d)    # crash here -> restart
    K.eq(int(C3.recover()), 3, "G1: a crash now replays all three")
    K.eq((int(C3.get(a)), int(C3.get(b)), int(C3.get(c))), (200, 800, 7), "G1: after the crash: both sides of the /pay, no coin made or lost")
    K.eq((disk(d).get(uu(501)), disk(d).get(uu(502)), disk(d).get(uu(503))), (200, 800, 7), "G1: ... on disk")
    K.check(not os.path.exists(jp), "G1: journal gone after the replay")
    C2.STOP_AT = 0
    K.eq(int(C2.flushNow()), 3, "G1: without the crash the next flush finishes the replay")
    K.eq((disk(d).get(uu(501)), disk(d).get(uu(502))), (200, 800), "G1: both sides on disk")
    # ---- G2: the replay fails BEFORE its new journal: the old journal stays byte for byte
    d, jp = setup("g2")
    before = open(jp, "rb").read()
    C2 = store_in(loader_for(jar), d)
    C2.STEPS = 0
    C2.STOP_AT = 1
    K.eq(int(C2.recover()), 2, "G2: folded")
    K.check(open(jp, "rb").read() == before, "G2: the old journal is untouched")
    K.eq((disk(d).get(uu(501)), disk(d).get(uu(502))), (500, 500), "G2: no balance file written")
    K.eq((int(C2.get(a)), int(C2.get(b))), (200, 800), "G2: memory = the journal")
    C3 = store_in(loader_for(jar), d)
    K.eq(int(C3.recover()), 2, "G2: a crash now still replays it")
    K.eq((disk(d).get(uu(501)), disk(d).get(uu(502))), (200, 800), "G2: both sides after the restart")
    # ---- G3: an unreadable journal (a folder in its place) = RECOVER_PENDING
    d = os.path.join(scratch, "g3")
    L = loader_for(jar)
    CS = store_in(L, d)
    os.makedirs(os.path.join(d, "balances"), exist_ok=True)
    open(os.path.join(d, "balances", uu(501) + ".properties"), "w").write("#SkyyCoins\nbalance=500\n")
    jp = os.path.join(d, "balances-journal.properties")
    os.makedirs(jp)
    K.eq(int(CS.recover()), -1, "G3: an unreadable journal cannot be replayed")
    K.check(bool(CS.RECOVER_PENDING) and int(CS.RECOVER_TRIES) == 1, "G3: RECOVER_PENDING, 1 try")
    try:
        CS.get(a)
        K.check(False, "G3: a load must wait")
    except Exception as e:
        K.check("unreadable" in str(e), "G3: every purse load waits (refused, nothing changed)")
    K.check(not CS.LOADED.containsKey(uu(501)), "G3: nothing loaded")
    CS.DIRTY.put(uu(509), JClass("java.lang.Boolean").TRUE)
    K.eq(int(CS.flushNow()), -1, "G3: no flush while pending")
    K.check(CS.DIRTY.containsKey(uu(509)), "G3: DIRTY untouched")
    CS.DIRTY.remove(uu(509))
    IO = JClass(PKG + "CoinIO", loader=L)
    IO(0, None).run()
    IO(0, None).run()
    K.check(bool(CS.RECOVER_PENDING) and int(CS.RECOVER_TRIES) == 3, "G3: CoinIO(0) retries it (3 tries)")
    K.check(os.path.isdir(jp), "G3: the journal is never overwritten")
    os.rmdir(jp)
    open(jp, "w").write("count=1\nk.0=%s\nv.0=321\n" % uu(501))
    IO(0, None).run()
    K.check(not bool(CS.RECOVER_PENDING) and int(CS.RECOVER_TRIES) == 0, "G3: replayed once readable (pending cleared)")
    K.eq(disk(d).get(uu(501)), 321, "G3: the journal value is on disk")
    K.check(not os.path.exists(jp), "G3: journal gone")
    K.eq(int(CS.get(a)), 321, "G3: loads work again")
    # ---- G4: 10 failures move it aside
    d = os.path.join(scratch, "g4")
    L = loader_for(jar)
    CS = store_in(L, d)
    os.makedirs(os.path.join(d, "balances"), exist_ok=True)
    open(os.path.join(d, "balances", uu(501) + ".properties"), "w").write("#SkyyCoins\nbalance=500\n")
    jp = os.path.join(d, "balances-journal.properties")
    open(jp, "w").write("garbage")
    K.eq(int(CS.recover()), -1, "G4: a malformed journal")
    IO = JClass(PKG + "CoinIO", loader=L)
    for i in range(8):
        IO(0, None).run()
    K.check(bool(CS.RECOVER_PENDING) and os.path.exists(jp), "G4: still pending + kept after 9 tries")
    IO(0, None).run()
    K.check(not bool(CS.RECOVER_PENDING) and not os.path.exists(jp), "G4: the 10th failure moves it aside")
    fl = [f for f in os.listdir(d) if f.startswith("balances-journal.failed-") and f.endswith(".properties")]
    K.eq(len(fl), 1, "G4: kept as balances-journal.failed-<millis>.properties")
    K.eq(open(os.path.join(d, fl[0])).read(), "garbage", "G4: its bytes kept for an admin")
    K.eq(int(CS.get(a)), 500, "G4: the purses go on from balances/")
    # ---- G5: one purse = no journal; two = a journal
    d = os.path.join(scratch, "g5")
    CS = store_in(loader_for(jar), d)
    jp = os.path.join(d, "balances-journal.properties")
    CS.set(a, 10)
    CS.STEPS = 0
    CS.STOP_AT = 2
    K.eq(int(CS.flushNow()), -1, "G5: one purse, stopped after the journal step")
    K.check(not os.path.exists(jp), "G5: a single-purse batch writes no journal")
    CS.STOP_AT = 0
    K.eq(int(CS.flushNow()), 1, "G5: ... and its file on the retry")
    K.eq(disk(d).get(uu(501)), 10, "G5: on disk")
    K.check(CS.transfer(a, b, 4), "G5: a /pay")
    CS.STEPS = 0
    CS.STOP_AT = 2
    K.eq(int(CS.flushNow()), -1, "G5: two purses, stopped after the journal")
    K.eq(jkeys(jp), {uu(501): 6, uu(502): 4}, "G5: a two-purse batch writes the journal")
    CS.STOP_AT = 0
    CS.add(a, 1)
    K.eq(int(CS.flushNow()), 2, "G5: the retry (still 2 dirty) finishes")
    K.check(not os.path.exists(jp), "G5: journal gone")
    CS.add(a, 1)
    CS.STEPS = 0
    CS.STOP_AT = 2
    jp_open = open(jp, "w")
    jp_open.write("count=1\nk.0=%s\nv.0=7\n" % uu(501))
    jp_open.close()
    K.eq(int(CS.flushNow()), -1, "G5: one purse while a journal is on disk")
    K.eq(jkeys(jp), {uu(501): 8}, "G5: ... still replaces the journal first (never left older than its file)")
    K.save()


# ====================================================================================================== D: live copy, start twice
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID = JClass("java.util.UUID")
    base = os.path.dirname(home)
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "balances")) if f.endswith(".properties"))
    h0 = HK.tree_hash(home)
    res = []
    for start in (1, 2):
        CS = store_in(loader_for(jar), home)
        K.eq(int(CS.recover()), 0, "D%d: no journal to replay" % start)
        vals = {}
        for k in keys:
            u = UUID.fromString(k[:36])
            try:
                CS.loadK(u, k)
                vals[k] = int(CS.getK(u, k))
            except Exception as e:
                vals[k] = "EXC " + str(e)[:40]
        K.eq(int(CS.flushNow()), 0, "D%d: reading writes nothing" % start)
        K.eq(HK.tree_hash(home), h0, "D%d: no file changed" % start)
        res.append(vals)
    C5 = store_in(loader_for(OLD_JAR), home)
    v5 = {}
    for k in keys:
        u = UUID.fromString(k[:36])
        try:
            C5.loadK(u, k)
            v5[k] = int(C5.getK(u, k))
        except Exception as e:
            v5[k] = "EXC " + str(e)[:40]
    K.eq(res[0], res[1], "D: both starts read the same")
    K.eq(res[0], v5, "D: 0.1.6 reads every live purse exactly like 0.1.5")
    K.notes.append("D: %d live purses, total %d coins" % (len(keys), sum(v for v in res[0].values() if isinstance(v, int))))
    K.check(len(keys) > 0, "D: the live copy has purses")
    K.save()


def run_killrounds(out, jar, scratch, _home):
    """parent-side helper phase is not a JVM: launch the killer child 5 times and kill it"""
    K = HK.Child(out)
    env = dict(os.environ)
    for rnd in range(5):
        d = os.path.join(scratch, "kill%d" % rnd)
        os.makedirs(os.path.join(d, "balances"), exist_ok=True)
        for i in range(12):
            open(os.path.join(d, "balances", uu(100 + i) + ".properties"), "w").write("#SkyyCoins\nbalance=1000\n")
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--phase", "killer", "--out", os.path.join(scratch, "k.json"),
                              "--dir", scratch, "--jar", jar, "--kdir", d], env=env)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "ready")) and time.time() - t0 < 60:
            time.sleep(0.05)
        os.remove(os.path.join(d, "ready")) if os.path.exists(os.path.join(d, "ready")) else None
        time.sleep(random.Random(rnd).uniform(0.7, 2.5))
        p.kill()
        p.wait()
        K.check(p.returncode != 0, "KK%d: the writer process was killed (rc %s)" % (rnd, p.returncode))
    K.save()


if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") == "killer":
        run_killer(None, JAR, SCRATCH, None)
        sys.exit(0)
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("crash", run_crash), ("killrounds", run_killrounds), ("killcheck", run_killcheck),
                   ("identity", run_identity), ("stress", run_stress), ("fixes", run_fixes), ("fix2", run_fix2), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
