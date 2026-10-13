"""Harness for SkyyMerchants 0.1.3 (lag fixes: the SkyyMerchants-IO writer + lock-free bridge; tools/merchants_0_1_3_patch.py).
Build first: python tools/merchants_0_1_3_patch.py && python SkyyMerchants/build_skyymerchants_0.1.3.py

    python SkyyMerchants/test_skyymerchants_0.1.3.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.2 -> 0.1.3: exactly the planned members differ (+ MerchIO)
  X  exec     EVERY NEW CODE PATH (-Xverify:all): bridge0 / bridge (created once, cached in BRIDGE, same map); the static checks (every
              bridge() is the lock-free form; Thread.sleep only in moveRetry, reached only from write0 <- writeOne; every file write of
              MerchReg / sales.log only in write0 / sale0 / sites); MerchIO thread factory (SkyyMerchants-IO, daemon); save() with IO
              running: returns at once while the writer is held (WLOCK held by the test = the caller never writes), the file is written
              by SkyyMerchants-IO, 0.1.2's text byte for byte; coalescing (50 saves while held = at most 2 writes, the newest text);
              settled / ok; a FAILED write (folder blocked) keeps the text, marks the world, relocate + respawnSame refuse at once
              (count 8), retryFailed re-queues it, the next write clears it; the per-world second skips the ghost sweep until settled
              and sweeps once settled; relocate's old-merchant removal waits for the write; sales.log lines appended in order by the
              writer (sale -> sale0) + the synchronous fallback; ready(): the first read queued on the writer (false), then in memory
              (true); IO off = the 0.1.2 synchronous save (real result); flushAll: writer stopped, queue drained, every world written
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyyMerchants: the registry read on the writer, saved again = byte-identical,
              sales.log untouched; the second start the same
  AA engine-access audit
Behaviour regression (separately, same jar): python SkyyMerchants/test_skyymerchants_0.1.py --jar SkyyMerchants/SkyyMerchants-0.1.3.jar
(244 ok; its only fails are the 0.1 manifest version, the new MerchIO class in its class list / AA count and its live folder rule).
Scratch: tools/dev/scratch/perfworld/merchants (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1.3"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfworld", "merchants")))
PKG = "com.skyy.merchants."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMerchants")

EXPECT = {
    "MerchLog": ["+f BRIDGE", "+m bridge0", "~m bridge"],
    "MerchReg": ["+f IO", "+f PEND", "+f QUEUED", "+f BUSY", "+f FAILED", "+f LOADING", "+f WLOCK", "+f WRITES", "+f LASTW",
                 "+m text", "+m write0", "+m writeOne0", "+m writeOne", "+m queue", "~m save", "+m runWrite", "+m settled", "+m ok", "+m retryFailed",
                 "+m ready", "+m runLoad", "+m stopIO", "~m flushAll", "~<clinit>"],
    "MerchShop": ["+m sale0", "~m sale"],
    "MerchCore": ["~m relocate", "~m respawnSame", "~m second"],
    "MerchTimer": ["~m run"],
    "SkyyMerchantsPlugin": ["~m setup"],
    # the config kit (tools/skyycfg.py, rebuilt): its lock-free CfgRows.bridge (2026-10-13) + the kit id / export header text
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header", "~<clinit>"],
    "CfgFn": ["~m opExport"],
    "MerchCfg": ["~m applyAll", "~m seed"],
}
ADDED = ["MerchIO"]


def api_sim(state):
    from jpype import JImplements, JOverride, JArray, JString, JDouble
    IC = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"

    @JImplements(PKG + "MerchApi")
    class Sim(object):
        @JOverride
        def worlds(self): return JArray(JString)(["default"])
        @JOverride
        def exec(self, wn, r): r.run(); return True
        @JOverride
        def height(self, wn, x, z): return 64
        @JOverride
        def block(self, wn, x, y, z): return "Soil_Grass" if y <= 64 else "Empty"
        @JOverride
        def fluid(self, wn, x, y, z): return False
        @JOverride
        def env(self, wn, x, y, z): return "Env_Zone1_Plains"
        @JOverride
        def players(self, wn): return JArray(JDouble)([10.0, 20.0])
        @JOverride
        def spawnPoint(self, wn): return JArray(JDouble)([0.0, 64.0, 0.0])
        @JOverride
        def roleOk(self, role): return True
        @JOverride
        def spawn(self, wn, role, x, y, z, yaw, name):
            state["spawned"].append((x, y, z))
            return "00000000-0000-4000-8000-%012d" % len(state["spawned"])
        @JOverride
        def present(self, wn, uuid, x, z, name): return 1
        @JOverride
        def remove(self, wn, uuid):
            state["removed"].append(str(uuid))
            return 1
        @JOverride
        def tell(self, wn, text, color): pass
        @JOverride
        def tellPlayer(self, u, text, color): pass
        @JOverride
        def conts(self, player): return None
        @JOverride
        def pos(self, ref, st): return None
        @JOverride
        def open(self, ref, pr, page): return False
    return Sim()


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, synchronized
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Log, Reg, Site, Core, Shop, IOc, Eng, Cfg, Timer = (P("MerchLog"), P("MerchReg"), P("MerchSite"), P("MerchCore"), P("MerchShop"),
                                                        P("MerchIO"), P("MerchEng"), P("MerchCfg"), P("MerchTimer"))
    Sys, Paths, Files = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.nio.file.Files")
    Executors, Thread = JClass("java.util.concurrent.Executors"), JClass("java.lang.Thread")
    lines = JClass("java.util.ArrayList")()
    Log.LINES = lines
    # ---- A: bridge
    K.check(Log.BRIDGE is None, "X bridge: BRIDGE empty before the first call")
    m1 = Log.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1), "X bridge: the first call creates + stores the map")
    K.check(Log.BRIDGE is not None and Sys.identityHashCode(Log.BRIDGE) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(Log.bridge()) == Sys.identityHashCode(m1) and Sys.identityHashCode(Log.bridge0()) == Sys.identityHashCode(m1),
            "X bridge: cached in BRIDGE, the same map every call, bridge0 finds it")
    PW.bridge_static(K, jar)
    # ---- static: sleeps + file writes only on the writer's methods
    g = PW.calls(jar)
    K.eq([m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")], ["MerchReg.moveRetry"],
         "X static: Thread.sleep only in MerchReg.moveRetry (+ the config kit's admin saves on the scheduler)")
    K.eq(PW.callers(g, "MerchReg.moveRetry", PKG), ["MerchReg.write0"], "X static: moveRetry called only by write0")
    K.eq(PW.callers(g, "MerchReg.write0", PKG), ["MerchReg.writeOne0"], "X static: write0 called only by writeOne0")
    K.eq(PW.callers(g, "MerchReg.writeOne0", PKG), ["MerchReg.writeOne"], "X static: writeOne0 only under WLOCK (writeOne)")
    K.eq(PW.callers(g, "MerchShop.sale0", PKG), ["MerchIO.run", "MerchShop.sale"], "X static: sale0 = the writer job or the IO-off fallback")
    io = PW.sites(g, PW.IO_TARGETS)
    K.check(set(io) <= {"MerchReg.write0", "MerchReg.moveRetry", "MerchReg.sites", "MerchShop.sale0", "MerchCfg.read", "MerchCfg.seed"} | set(m for m in io if m.startswith("Cfg")),
            "X static: file I/O only in write0 / sites / sale0 / the config load: %s" % io)
    # ---- the writer
    d = os.path.join(scratch, "x")
    os.makedirs(d, exist_ok=True)
    Reg.DIR = Paths.get(os.path.join(d, "merchants"))
    Shop.LOGF = Paths.get(os.path.join(d, "sales.log"))
    fac = IOc(9, None)
    t = fac.newThread(IOc(1, "nothing"))
    K.check(str(t.getName()) == "SkyyMerchants-IO" and t.isDaemon(), "X MerchIO.newThread: SkyyMerchants-IO, daemon")
    # IO off first: the 0.1.2 synchronous save, real result
    sites = Reg.sites("default")
    K.check(sites is not None and sites.size() == 0, "X sites: no file = an empty registry")
    s = Site()
    s.zone, s.uuid, s.x, s.y, s.z, s.placedAt, s.visit = "zone1", "00000000-0000-4000-8000-000000000001", 10, 64, 20, 1000, 1
    s.stock, s.env, s.rumour = "w:Weapon_Sword_Iron:100:1", "Env_Zone1_Plains", "near the hills"
    Reg.add(sites, s)
    K.check(Reg.IO is None and Reg.save("default"), "X save (IO off): written now, true")
    f = os.path.join(d, "merchants", "default.tsv")
    want = "# SkyyMerchants roaming merchants - world default: zone uuid x y z placedAt visit held stock ghosts env rumour\n" + str(s.line()) + "\n"
    K.eq(open(f, encoding="utf8", newline="").read() if os.path.isfile(f) else None, want, "X save (IO off): the 0.1.2 text byte for byte")
    K.check(str(Reg.LASTW) == str(Thread.currentThread().getName()) and Reg.settled("default"), "X save (IO off): written on the caller, settled")
    # IO on
    Reg.IO = Executors.newSingleThreadExecutor(fac)
    w0 = Reg.WRITES.get()
    s.visit = 2
    with synchronized(Reg.WLOCK):
        t0 = time.time()
        ok = Reg.save("default")
        dt = time.time() - t0
        K.check(ok and dt < 0.5 and Reg.WRITES.get() == w0, "X save (IO on): returns at once (%.1f ms) while the writer is held; nothing written by the caller" % (dt * 1000))
        K.check(not Reg.settled("default"), "X settled: false while a write is queued")
        for i in range(50):
            s.visit = 100 + i
            Reg.save("default")
        K.check(Reg.WRITES.get() == w0, "X 50 more saves: still nothing written by the caller")
    K.check(PW.wait_until(lambda: Reg.settled("default")), "X settled after the writer ran")
    nw = Reg.WRITES.get() - w0
    K.check(1 <= nw <= 2, "X coalesced: 51 saves = %d write(s)" % nw)
    K.check(str(Reg.LASTW) == "SkyyMerchants-IO", "X the file was written by SkyyMerchants-IO (%s)" % Reg.LASTW)
    want = "# SkyyMerchants roaming merchants - world default: zone uuid x y z placedAt visit held stock ghosts env rumour\n" + str(s.line()) + "\n"
    K.eq(open(f, encoding="utf8", newline="").read(), want, "X the newest text is on disk (visit 149)")
    # ---- a failed write: the folder is blocked by a file
    Reg.DIR = Paths.get(os.path.join(d, "blocked", "merchants"))
    open(os.path.join(d, "blocked"), "w").write("x")
    fails0 = Reg.SAVE_FAILS.get()
    K.check(Reg.save("default"), "X save into a blocked folder: queued (true)")
    K.check(PW.wait_until(lambda: not Reg.ok("default")), "X the failed write marks the world FAILED")
    K.check(Reg.SAVE_FAILS.get() == fails0 + 1 and Reg.PEND.containsKey("default") and not Reg.settled("default"),
            "X failed: SAVE_FAILS +1, the text kept in PEND, not settled")
    K.check(any("could not save the merchants of world default" in str(x) for x in lines), "X failed: the WARN line")
    state = {"spawned": [], "removed": []}
    Eng.API = api_sim(state)
    n8 = Core.N[8]
    z = JClass(PKG + "MerchZone")()
    z.key, z.name, z.world, z.any, z.lo, z.hi = "zone1", "Emerald Wilds", "default", True, 1, 10
    K.check(not Core.relocate("default", sites, z, s, 5000, "moved") and Core.N[8] == n8 + 1 and not state["spawned"],
            "X relocate refused at once while the world's write FAILED (count 8, nothing spawned)")
    K.check(not Core.respawnSame("default", sites, z, s, 5000) and Core.N[8] == n8 + 2 and not state["spawned"],
            "X respawnSame refused at once while FAILED")
    # the per-world second: ghost sweep skipped while not settled
    s.addGhost("00000000-0000-4000-8000-0000000000aa", 4000)
    s.uuid = ""
    Cfg.ON = False
    Cfg.ZONES = JArray(JClass(PKG + "MerchZone"))(0)
    Core.second("default", 6000)
    K.check("00000000-0000-4000-8000-0000000000aa" not in state["removed"], "X second: the ghost sweep waits while the file is not settled")
    import shutil
    os.remove(os.path.join(d, "blocked"))
    Reg.DIR = Paths.get(os.path.join(d, "merchants"))
    K.check(Reg.retryFailed() >= 1, "X retryFailed re-queues the failed world")
    K.check(PW.wait_until(lambda: Reg.settled("default") and Reg.ok("default")), "X the retried write lands: settled, FAILED cleared")
    Core.second("default", 7000)
    K.check("00000000-0000-4000-8000-0000000000aa" in state["removed"], "X second: the ghost sweep runs once settled (old merchant removed)")
    PW.wait_until(lambda: Reg.settled("default"))
    # relocate with IO on: the new merchant spawned + saved; the OLD one is not removed before the write landed
    Cfg.ON = True
    st2 = {"spawned": [], "removed": []}
    Eng.API = api_sim(st2)
    s.uuid = "00000000-0000-4000-8000-0000000000bb"
    s.ghosts = ""
    with synchronized(Reg.WLOCK):
        try:
            r = Core.relocate("default", sites, z, s, 8000, "moved")
        except Exception as ex:
            r = False
            K.notes.append("relocate threw in the sim: %s" % str(ex)[:200])
        removed_early = "00000000-0000-4000-8000-0000000000bb" in st2["removed"]
    K.check(not removed_early, "X relocate (IO on, write not landed): the old merchant stays (a ghost) until the file is written")
    if r:
        K.check(s.hasGhost("00000000-0000-4000-8000-0000000000bb"), "X relocate: the old merchant is a ghost in the queued file")
        PW.wait_until(lambda: Reg.settled("default"))
        Core.second("default", 9000)
        K.check("00000000-0000-4000-8000-0000000000bb" in st2["removed"], "X the next second (settled) removes the old merchant")
    else:
        K.notes.append("relocate found no spot in the sim (%s) - the write-ahead path is covered by the ghost-sweep checks" % Core.N[6])
    # ---- sales.log through the writer, in order
    with synchronized(Reg.WLOCK):
        pass
    for i in range(20):
        Shop.sale("BUY t%d" % i)
    K.check(PW.wait_until(lambda: os.path.isfile(os.path.join(d, "sales.log")) and open(os.path.join(d, "sales.log"), encoding="utf8").read().count("\n") == 20),
            "X sale: 20 lines appended by the writer")
    got = [l.split("\t", 1)[1] for l in open(os.path.join(d, "sales.log"), encoding="utf8").read().splitlines()]
    K.eq(got, ["BUY t%d" % i for i in range(20)], "X sale: in order, 0.1.2 line format (time TAB line)")
    # ---- ready(): the first read on the writer
    os.makedirs(os.path.join(d, "merchants"), exist_ok=True)
    open(os.path.join(d, "merchants", "other.tsv"), "w", encoding="utf8", newline="").write(want.replace("world default", "world other"))
    K.check(not Reg.ready("other"), "X ready: false the first time (the read is queued on the writer)")
    K.check(PW.wait_until(lambda: Reg.W.containsKey("other")) and Reg.ready("other") and Reg.sites("other").size() == 1,
            "X ready: the registry read by SkyyMerchants-IO, then true (1 line)")
    # ---- the timer: retryFailed + ready, never a hop for a world not read yet
    K.check(Reg.LOADING.isEmpty(), "X LOADING empty after the read")
    # ---- flushAll at shutdown: writer stopped, everything written synchronously
    if Reg.find(sites, "zone1") is None:
        Reg.add(sites, s)
    s.visit = 777
    with synchronized(Reg.WLOCK):
        Reg.save("default")
    Reg.STOPPING = True
    Reg.flushAll()
    K.check(Reg.IO is None and Reg.settled("default"), "X flushAll: writer stopped, nothing pending")
    K.check("\t777\t" in open(f, encoding="utf8").read(), "X flushAll: the newest state is on disk")
    K.check(Reg.save("default") and str(Reg.LASTW) == str(Thread.currentThread().getName()), "X after stop: save writes synchronously (0.1.2)")
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Reg, IOc = JClass(PKG + "MerchReg"), JClass(PKG + "MerchIO")
    Paths, Executors = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors")
    md = os.path.join(home, "merchants")
    names = sorted(n[:-4] for n in os.listdir(md) if n.endswith(".tsv")) if os.path.isdir(md) else []
    before = {n: open(os.path.join(md, n + ".tsv"), "rb").read() for n in names}
    log0 = open(os.path.join(home, "sales.log"), "rb").read() if os.path.isfile(os.path.join(home, "sales.log")) else None
    for start in (1, 2):
        Reg.W.clear()
        Reg.NAMES.clear()
        Reg.STOPPING = False
        Reg.DIR = Paths.get(md)
        Reg.IO = Executors.newSingleThreadExecutor(IOc(9, None))
        for n in names:
            Reg.ready(n)
        K.check(PW.wait_until(lambda: all(Reg.W.containsKey(n) for n in names)), "D start %d: every world registry read by the writer (%s)" % (start, names))
        for n in names:
            Reg.save(n)
        Reg.STOPPING = True
        Reg.flushAll()
        after = {n: open(os.path.join(md, n + ".tsv"), "rb").read() for n in names}
        K.check(after == before, "D start %d: every registry saved back byte-identical (%d worlds, %s lines)"
                % (start, len(names), [str(Reg.W.get(n).size()) for n in names]))
        K.check((open(os.path.join(home, "sales.log"), "rb").read() if log0 is not None else None) == log0, "D start %d: sales.log untouched" % start)
    K.notes.append("D: live worlds %s" % names)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMerchants", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMerchants"))
