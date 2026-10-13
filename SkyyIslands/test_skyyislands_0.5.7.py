"""Harness for SkyyIslands 0.5.7 (lag fixes: island files + notices on the SkyyIslands-IO writer, lock-free bridge;
tools/islands_0_5_7_patch.py). Build first: python tools/islands_0_5_7_patch.py && python SkyyIslands/build_skyyislands_0.5.7.py

    python SkyyIslands/test_skyyislands_0.5.7.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all on the 0.7 server jar
  C  compare  0.5.6 -> 0.5.7: exactly the planned members differ (+ IslandIO); IslandMenuPage identical
  X  exec     EVERY NEW CODE PATH (-Xverify:all): bridge0 / bridge (created once, cached in BRIDGE; every bridge() of the jar is the
              lock-free form); static: Thread.sleep only in store0 / noteStore0 (the writer's file writes), read0 (a failed read's
              retries, as 0.5.6) and the start-up config writes; store0 reached only through storeLocked (WLOCK) from write0's IO-off path,
              runWrite and flushPending; IslandIO (SkyyIslands-IO daemon); write0 with IO running: returns at once while the writer is held
              (nothing written by the caller), the file written by SkyyIslands-IO; read0 answers from PEND (every read-modify-write sees
              the newest content); SAME ANSWERS: 400 random island mutations (setProps / joinCoop / leaveCoop / setAdmin / trustKey /
              untrustKey / banUuid / unbanUuid / clearCoop / setWorldName) run synchronously (IO off = 0.5.6) on one folder and through
              the writer (held at random moments) on another: every return value equal, every file's properties equal, the settings
              cache equal; a FAILED write (folder blocked): true, kept in PEND (reads see it), FAILED + one WARN, retryFailed after the
              folder is back writes it; notices through the writer (noticeAdd / noticeTake) + the IO-off fallback; shutdown (STOPPING,
              stopIO, flushPending): every pending island + the notices written
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyyIslands: the start-up load (IO off, as setup) then IO on and every
              island read through the store: no file written either time
  AA engine-access audit
Scratch: tools/dev/scratch/perfworld/islands (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.5.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfworld", "islands")))
PKG = "com.skyy.islands."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyIslands")

EXPECT = {
    "IslandStore": ["+f BRIDGE", "+f IO", "+f STOPPING", "+f PEND", "+f QUEUED", "+f FAILED", "+f NOTE_PEND", "+f WLOCK", "+f WRITES",
                    "+f LASTW", "+m bridge0", "~m bridge", "~m read0", "+m store0", "+m storeLocked", "+m queue", "~m write0",
                    "+m runWrite", "+m retryFailed", "+m settled", "+m noteStore0", "+m noteLocked", "~m noteSave0", "+m runNotes",
                    "+m stopIO", "+m flushPending", "~<clinit>"],
    "SeenTick": ["~m run"],
    "SkyyIslandsPlugin": ["~m setup", "~m shutdown"],
    # the config kit (tools/skyycfg.py, rebuilt): its lock-free CfgRows.bridge (2026-10-13) + the kit id / export header text
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header", "~<clinit>"],
    "CfgFn": ["~m opExport"],
    "IslandCfg": ["~m load"],
}
ADDED = ["IslandIO"]


def props_of(path):
    d = {}
    if not os.path.isfile(path):
        return None
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        d[k] = v
    return d


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, synchronized
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    St, IOc = JClass(PKG + "IslandStore"), JClass(PKG + "IslandIO")
    Sys, Paths, Executors, Thread = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.lang.Thread")
    me = str(Thread.currentThread().getName())
    # ---- A: bridge
    K.check(St.BRIDGE is None, "X bridge: BRIDGE empty before the first call")
    m1 = St.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(St.BRIDGE) == Sys.identityHashCode(m1) and Sys.identityHashCode(St.bridge()) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(St.bridge0()) == Sys.identityHashCode(m1), "X bridge: created once, cached in BRIDGE, same map")
    PW.bridge_static(K, jar)
    g = PW.calls(jar)
    sl = [m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")]
    K.eq(sl, ["IslandCfg.writeText", "IslandStore.noteStore0", "IslandStore.read0", "IslandStore.store0"],
         "X static: Thread.sleep only in store0 / noteStore0 (writer), read0 (failed-read retries) and the start-up config write")
    K.eq(PW.callers(g, "IslandStore.store0", PKG), ["IslandStore.storeLocked"], "X static: store0 only under WLOCK (storeLocked)")
    K.eq(PW.callers(g, "IslandStore.storeLocked", PKG), ["IslandStore.flushPending", "IslandStore.runWrite", "IslandStore.write0"],
         "X static: storeLocked = the writer job, shutdown, or write0's IO-off path")
    K.eq(PW.callers(g, "IslandStore.noteStore0", PKG), ["IslandStore.noteLocked"], "X static: noteStore0 only under WLOCK (noteLocked)")
    t = IOc(9, None).newThread(IOc(1, None))
    K.check(str(t.getName()) == "SkyyIslands-IO" and t.isDaemon(), "X IslandIO.newThread: SkyyIslands-IO, daemon")
    # ---- sync (IO off) vs async: the same answers
    da, db = os.path.join(scratch, "xa", "islands"), os.path.join(scratch, "xb", "islands")
    os.makedirs(da, exist_ok=True)
    os.makedirs(db, exist_ok=True)
    rnd = random.Random(7)
    owners = ["00000000-0000-4000-8000-%012d" % i for i in range(1, 5)]
    players = ["10000000-0000-4000-8000-%012d" % i for i in range(1, 9)]

    def S(xs):
        return JArray(JString)(xs)

    ops = []
    for i in range(400):
        ok = rnd.choice(owners)
        k = rnd.choice(players)
        ops.append((rnd.randrange(10), ok, k, "Name%d" % rnd.randrange(5), rnd.random() < 0.5, i))

    def apply(op):
        c, ok, k, nm, flag, i = op
        if c == 0:
            return bool(St.setProps(ok, S(["visit.limit", "pvp"]), S([str(i % 9 + 1), "1" if flag else "0"])))
        if c == 1:
            return int(St.joinCoop(ok, k, nm, 4))
        if c == 2:
            return int(St.leaveCoop(ok, k))
        if c == 3:
            return int(St.setAdmin(ok, k, flag))
        if c == 4:
            return int(St.trustKey(ok, k, nm, 5))
        if c == 5:
            return int(St.untrustKey(ok, k))
        if c == 6:
            return int(St.banUuid(ok, k, nm, 3))
        if c == 7:
            return int(St.unbanUuid(ok, k))
        if c == 8:
            r = St.clearCoop(ok)
            return None if r is None else str(r)
        return int(St.setWorldName(ok, "skyy-island-%s-%d" % (ok[-2:], i % 3)))

    def snap(d):
        return {f[:-11]: {k: v for k, v in props_of(os.path.join(d, f)).items() if k not in ("created", "resetAt") and not k.startswith("coopSince.")}
                for f in sorted(os.listdir(d)) if f.endswith(".properties")}

    def cache():
        out_ = {}
        for o in owners:
            s_ = St.SETTINGS.get(o)
            out_[o] = None if s_ is None else (str(s_.members), str(s_.admins), str(s_.trusted), str(s_.banned), int(s_.limit), bool(s_.pvp), str(s_.world))
        return out_

    St.DIR = Paths.get(da)
    St.IO = None
    w0 = St.WRITES.get()
    res_a = [apply(op) for op in ops]
    K.check(St.WRITES.get() > w0 and str(St.LASTW) == me and St.PEND.isEmpty(), "X IO off: written on the caller (0.5.6), nothing pending")
    snap_a, cache_a = snap(da), cache()
    St.SETTINGS.clear()
    St.DIR = Paths.get(db)
    St.IO = Executors.newSingleThreadExecutor(IOc(9, None))
    res_b = []
    held = 0
    i = 0
    while i < len(ops):
        n = rnd.randrange(1, 30)
        if rnd.random() < 0.5:
            with synchronized(St.WLOCK):
                wb = St.WRITES.get()
                for op in ops[i:i + n]:
                    res_b.append(apply(op))
                held += 1
                K.check(St.WRITES.get() == wb, "X IO on: %d ops while the writer is held wrote nothing on the caller" % len(ops[i:i + n])) if held < 4 else None
        else:
            for op in ops[i:i + n]:
                res_b.append(apply(op))
        i += n
    K.eq(res_b, res_a, "X SAME ANSWERS: the 400 mutations answer the same through the writer as synchronously")
    K.eq(cache(), cache_a, "X SAME ANSWERS: the settings cache is the same")
    K.check(PW.wait_until(lambda: St.PEND.isEmpty() and St.QUEUED.isEmpty()), "X the writer drains every pending island")
    K.check(str(St.LASTW) == "SkyyIslands-IO", "X files written by SkyyIslands-IO (%s)" % St.LASTW)
    sb_ = snap(db)
    K.check(sb_ == snap_a, "X SAME FILES: every island file's properties equal to the synchronous run (times aside): %s"
            % sorted(k for k in set(sb_) | set(snap_a) if sb_.get(k) != snap_a.get(k)))
    # ---- read0 answers from PEND
    ko = owners[0]
    with synchronized(St.WLOCK):
        St.setProps(ko, S(["ownerName"]), S(["PendingName"]))
        K.check(St.PEND.containsKey(ko) and str(St.read0(ko, 1, 0).getProperty("ownerName")) == "PendingName"
                and str(St.settings(ko).ownerName) == "PendingName", "X read0 / settings see the pending change before it is on disk")
        K.check("PendingName" not in open(os.path.join(db, ko + ".properties"), encoding="latin-1").read(), "X ... and it is not on disk yet")
    K.check(PW.wait_until(lambda: St.settled(ko)) and "PendingName" in open(os.path.join(db, ko + ".properties"), encoding="latin-1").read(),
            "X then the writer puts it on disk")
    # ---- a failed write
    blocked = os.path.join(scratch, "xc")
    open(blocked, "w").write("x")
    St.DIR = Paths.get(os.path.join(blocked, "islands"))
    lines = []
    K.check(bool(St.setProps(ko, S(["ownerName"]), S(["FailName"]))), "X write into a blocked folder: true (queued)")
    K.check(PW.wait_until(lambda: St.FAILED.containsKey(ko)), "X the failed write marks the island FAILED")
    K.check(St.PEND.containsKey(ko) and str(St.read0(ko, 1, 0).getProperty("ownerName")) == "FailName", "X failed: kept in PEND, reads see it")
    os.remove(blocked)
    St.DIR = Paths.get(os.path.join(blocked, "islands"))
    K.check(St.retryFailed() == 1, "X retryFailed re-queues it")
    K.check(PW.wait_until(lambda: St.settled(ko) and not St.FAILED.containsKey(ko))
            and "FailName" in open(os.path.join(blocked, "islands", ko + ".properties"), encoding="latin-1").read(),
            "X the retried write lands, FAILED cleared")
    St.DIR = Paths.get(db)
    # ---- notices
    UUID = JClass("java.util.UUID")
    u1 = UUID.fromString(players[0])
    nf = os.path.join(scratch, "xb", "notices.properties")
    with synchronized(St.WLOCK):
        K.check(St.noticeAdd(u1, "hello one") and St.noticeAdd(u1, "hello two"), "X noticeAdd (IO on): true")
        K.check(not os.path.isfile(nf), "X noticeAdd: nothing written by the caller")
    K.check(PW.wait_until(lambda: os.path.isfile(nf) and St.NOTE_PEND.get() is None) and str(St.LASTW) == "SkyyIslands-IO",
            "X notices written by SkyyIslands-IO")
    from jpype import JClass as _J
    P = _J("java.util.Properties")()
    FIS = _J("java.io.FileInputStream")(nf)
    P.load(FIS)
    FIS.close()
    K.eq(str(P.getProperty(players[0])), "hello one\nhello two", "X notices content")
    K.eq(str(St.noticeTake(u1)), "hello one\nhello two", "X noticeTake answers from memory")
    K.check(PW.wait_until(lambda: St.NOTE_PEND.get() is None and players[0] not in open(nf, encoding="latin-1").read()), "X noticeTake saved through the writer")
    # ---- shutdown
    with synchronized(St.WLOCK):
        St.setProps(owners[1], S(["ownerName"]), S(["AtShutdown"]))
        St.noticeAdd(u1, "late notice")
    St.STOPPING = True
    St.stopIO()
    n = St.flushPending()
    K.check(St.IO is None and St.PEND.isEmpty() and St.NOTE_PEND.get() is None, "X shutdown: writer stopped, nothing pending (%d flushed)" % n)
    K.check("AtShutdown" in open(os.path.join(db, owners[1] + ".properties"), encoding="latin-1").read() and "late notice" in open(nf, encoding="latin-1").read(),
            "X shutdown: the last island change + notice are on disk")
    K.check(bool(St.setProps(owners[1], S(["ownerName"]), S(["AfterStop"]))) and str(St.LASTW) == me, "X after stop: write0 writes synchronously (0.5.6)")
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    St, IOc = JClass(PKG + "IslandStore"), JClass(PKG + "IslandIO")
    Paths, Executors = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors")
    h0 = HK.tree_hash(home)
    for start in (1, 2):
        St.SETTINGS.clear()
        St.STOPPING = False
        St.IO = None
        St.DIR = Paths.get(os.path.join(home, "islands"))
        St.loadIslandWorlds()
        St.IO = Executors.newSingleThreadExecutor(IOc(9, None))
        keys = St.islandKeys()
        w0 = St.WRITES.get()
        bad = 0
        for i in range(keys.size()):
            s_ = St.settings(keys.get(i))
            if s_.bad:
                bad += 1
            St.read0(keys.get(i), 1, 0)
        St.STOPPING = True
        St.stopIO()
        St.flushPending()
        K.check(St.WRITES.get() == w0 and bad == 0, "D start %d: %d islands read, none unreadable, nothing written" % (start, keys.size()))
        K.check(HK.tree_hash(home) == h0, "D start %d: every file byte-identical" % start)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
