"""SkyyHud 0.3.19 harness - THE LAG-FIX ROUND (tools/hud_0_3_19_patch.py; research/Code-Structure-Audit.md findings 4 + 8). Built on
tools/harness_kit.py (each phase a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the
scratch folder). The 0.3.18 widget harness (W: the real HudMain build / fill / tick for every Abilities state) is run on this jar too:
    python SkyyHud/test_skyyhud_0.3.18.py --jar SkyyHud/SkyyHud-0.3.19.jar --dir <scratch>
(its F class list names the 0.3.19 classes and its R re-run of the 0.3.16 harness fails on Hytale 0.7.0's MapMarker constructor for the
0.3.18 jar as well - both expected; everything else passes).

    python SkyyHud/test_skyyhud_0.3.19.py [--jar SkyyHud-0.3.19.jar] [--old SkyyHud-0.3.18.jar] [--dir <scratch>] [--keep]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.18 -> 0.3.19: HudThreads + WTime added; exactly the listed classes / members differ; non-class entries: the manifest
  X   exec     X1 HudThreads EXECUTED: one daemon thread "SkyyHud-Tick"; later() runs there; LayoutStore.save writes ON that thread (not the
               caller's), in order, the same bytes as 0.3.18's inline save (but the date comment line); stop() lets queued writes finish; no
               thread -> the inline write (0.3.18 path)
               X2 WTime EXECUTED on a World stand-in with a real WorldTimeResource: on the world's own thread = read now ("HH:MM", "Day N" =
               0.3.18's formulas); any other thread = the last world-thread read, never the store (a store that throws off-thread is not
               touched); want() = one queued task per world until it ran; run() fills the cache
               X3 hubWorld: the bridge key island:hubWorld wins; else the last hub.properties read; hubRefresh reads the file at most every
               15 s; hubWorld is no longer synchronized and reads no file
               X4 minimap bounds: the REAL Minimap.tap on a session: per player 20,000 packets (0.3.18's bound, kept) / 1,024 pieces; the GLOBAL piece bound
               (4,096) sends a packet keys-only even when the player's own count is low; the global packet bound drops; drain / drop give
               the counts back; resync() = the sum over the sessions
               X5 bytecode: setup schedules TickTask on HudThreads (no HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate); TickTask.run calls
               hubRefresh + resync; Widgets.text reads the world time only through WTime.get; WTime.read is the only Store.getResource;
               LayoutStore.save -> HudThreads.write; AttachTask.later -> HudThreads.later; shutdown -> HudThreads.stop
  ST  live     START TWICE on a scratch COPY of the live Skyy_SkyyHud (HudCfg.load, the config kit, every saved layout): nothing written
  AA  audit    the engine-access audit
Scratch: tools/dev/scratch/perfgear/hud19 (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PWK

VERSION, PREV = "0.3.19", "0.3.18"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "perfgear", "hud19")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")

EXPECT = {
    "Widgets": ["+m hubRefresh", "~f HUBAT", "~f HUBW", "~m hubWorld", "~m text"],
    "LayoutStore": ["~m save"],
    "HudMain": ["+m wantsTime", "~m tick"],
    "SkyyHudPlugin": ["~m setup", "~m shutdown", "~m tickAll"],
    "TickTask": ["~m run"],
    "AttachTask": ["~m later"],
    "Minimap": ["+f GQC", "+f GQN", "+m resync", "~<clinit>", "~m drain", "~m drop", "~m tap"],
    # the version text + the kit's lock-free CfgRows.bridge (tools/skyycfg.py gained it after 0.3.18 was built)
    "CfgFn": ["~m opExport"], "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"],
}
ADDED = ["HudThreads", "WTime"]


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JInt, JLong, JByte, JArray, JString, JBoolean, JImplements, JOverride
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls], verify=True)
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    SYS = JClass("java.lang.ClassLoader").getSystemClassLoader()

    def loader(j):
        a = JArray(URL)(1)
        a[0] = File(j).toURI().toURL()
        return URLCL(a, SYS)
    LD = {"new": loader(JAR), "old": loader(OLD_JAR)}
    P = lambda t_, n: JClass(PKG + n, loader=LD[t_])
    Paths = JClass("java.nio.file.Paths")
    UUID, CHM, Thread = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.Thread")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    # ------------------------------------------------------------------------------------ X1 HudThreads + LayoutStore.save
    HT, LSn, LSo, WLn = P("new", "HudThreads"), P("new", "LayoutStore"), P("old", "LayoutStore"), P("new", "Widgets")
    u1 = UUID.fromString("00000000-0000-0000-0000-00000319a001")
    d_new, d_old = os.path.join(scratch, "lay-new"), os.path.join(scratch, "lay-old")
    LSn.DIR = Paths.get(d_new)
    LSo.DIR = Paths.get(d_old)
    for L_ in (LSn, LSo):
        m_ = L_.get(u1)
        m_.get("Gclock").dx = 77
        m_.get("Coins").en = False
    LSn.save(u1)                                         # no thread yet -> inline (the 0.3.18 path)
    inline_ok = os.path.isfile(os.path.join(d_new, str(u1) + ".properties"))
    os.remove(os.path.join(d_new, str(u1) + ".properties"))
    e = HT.start()
    seen = {}

    @JImplements("java.lang.Runnable")
    class Probe:
        def __init__(self, k):
            self.k = k

        @JOverride
        def run(self):
            t_ = Thread.currentThread()
            seen[self.k] = (str(t_.getName()), bool(t_.isDaemon()))
    HT.later(Probe("later"), JLong(20))
    w0 = int(HT.WRITES.get())
    LSn.save(u1)
    LSo.save(u1)
    PWK.wait_until(lambda: int(HT.WRITES.get()) > w0 and "later" in seen, 5.0)
    fn_, fo_ = os.path.join(d_new, str(u1) + ".properties"), os.path.join(d_old, str(u1) + ".properties")

    def body(p_):
        return [ln for ln in open(p_, encoding="latin-1").read().split("\n") if not ln.startswith("#") or ln.startswith("#SkyyHud")]
    K.check(inline_ok and seen.get("later") == ("SkyyHud-Tick", True) and int(HT.WRITES.get()) == w0 + 1 and os.path.isfile(fn_)
            and body(fn_) == body(fo_) and not os.path.exists(fn_ + ".tmp"),
            "X1: HudThreads: no thread -> inline save; later() runs on the daemon 'SkyyHud-Tick' (%s); LayoutStore.save written ON that thread "
            "(writes %d), the same lines as 0.3.18's inline save (but the date), no .tmp" % (seen.get("later"), int(HT.WRITES.get()) - w0))
    # writes in order, a burst queued behind a slow task, all done after stop()

    @JImplements("java.lang.Runnable")
    class Slow:
        @JOverride
        def run(self):
            time.sleep(0.4)
    e.execute(Slow())
    w1 = int(HT.WRITES.get())
    for i in range(20):
        LSn.get(u1).get("Gclock").dx = 100 + i
        LSn.save(u1)
    pending = int(HT.WRITES.get()) - w1
    HT.stop()
    last = [ln for ln in open(fn_, encoding="latin-1") if ln.startswith("Gclock=")]
    K.check(pending == 0 and int(HT.WRITES.get()) - w1 == 20 and last and last[0].split("=", 1)[1].split(",")[2].strip() == "119",
            "X1: 20 saves queued behind a busy thread return at once (written %d before stop); stop() lets all 20 finish, in order (the file "
            "holds the last: %s)" % (pending, last[0].strip() if last else None))
    LSn.save(u1)                                         # stopped -> inline again
    K.check(int(HT.WRITES.get()) - w1 == 20 and [ln for ln in open(fn_, encoding="latin-1") if ln.startswith("Gclock=")][0].split("=", 1)[1].split(",")[2].strip() == "119",
            "X1: after stop() a save writes inline (the 0.3.18 path)")
    # ------------------------------------------------------------------------------------ X2 WTime
    WT = P("new", "WTime")
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CtM = JClass("javassist.CtNewMethod")
    WN = "com.hypixel.hytale.server.core.universe.world.World"
    fw = CP.makeClass("skyyhud319.FakeWorld", CP.get(WN))
    fw.addField(JClass("javassist.CtField").make("public static java.util.ArrayList RAN = new java.util.ArrayList();", fw))
    fw.addMethod(CtM.make("public void execute(Runnable r) { RAN.add(r); }", fw))
    fw.writeFile(hcls)
    FW = JClass("skyyhud319.FakeWorld")
    STc = JClass("com.hypixel.hytale.component.Store")
    RTc = JClass("com.hypixel.hytale.component.ResourceType")
    RESc = JClass("com.hypixel.hytale.component.Resource")
    WTR = JClass("com.hypixel.hytale.server.core.modules.time.WorldTimeResource")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    TTc = JClass("com.hypixel.hytale.server.core.util.thread.TickingThread")
    RUNc = JClass("com.hypixel.hytale.server.core.util.thread.TickingThread$Run")
    AR = JClass("java.util.concurrent.atomic.AtomicReference")
    TMc = JClass("com.hypixel.hytale.server.core.modules.time.TimeModule")
    rt = U.allocateInstance(RTc.class_)                  # index 0, no registry (Store.getResource: validateRegistry + resources[index])
    if TMc.get() is None:                                # WorldTimeResource.getResourceType() = TimeModule.get().getWorldTimeResourceType()
        jf(TMc, "instance").set(None, U.allocateInstance(TMc.class_))
    jf(TMc, "worldTimeResourceType").set(TMc.get(), rt)
    tr = WTR()
    Inst = JClass("java.time.Instant")
    tr.setGameTime0(Inst.parse("0001-01-05T07:04:00Z"))
    st = U.allocateInstance(STc.class_)
    reg = U.allocateInstance(JClass("com.hypixel.hytale.component.ComponentRegistry").class_)
    jf(STc, "registry").set(st, reg)
    jf(RTc, "registry").set(rt, reg)

    def put_res(r_):
        a_ = JArray(RESc)(1)
        a_[0] = r_
        jf(STc, "resources").set(st, a_)
    put_res(tr)
    es = U.allocateInstance(ESc.class_)
    jf(ESc, "store").set(es, st)
    w = U.allocateInstance(FW.class_)
    jf(FW, "entityStore").set(w, es)
    jf(FW, "name").set(w, "harness-world")
    run_ = U.allocateInstance(RUNc.class_)
    jf(RUNc, "thread").set(run_, Thread.currentThread())
    jf(TTc, "currentRun").set(w, AR(run_))
    WT.T.clear()
    try:
        WT.read(w)
    except Exception as ex_:
        K.check(False, "X2: WTime.read on the stand-in world threw: %s" % str(ex_)[:400])
        import traceback
        traceback.print_exc()
    on = [str(x) for x in (WT.get(w) or [])]
    reads_on = 1
    # the old formulas (0.3.18 Widgets.text) on the same resource
    days = int(JClass("java.time.temporal.ChronoUnit").DAYS.between(WTR.ZERO_YEAR, tr.getGameTime())) + 1
    dt = tr.getGameDateTime()
    want = ["%02d:%02d" % (int(dt.getHour()), int(dt.getMinute())), "Day %d" % days]
    run2 = U.allocateInstance(RUNc.class_)
    jf(RUNc, "thread").set(run2, Thread())               # another thread is the world's
    jf(TTc, "currentRun").set(w, AR(run2))
    tr9 = WTR()
    tr9.setGameTime0(Inst.parse("0001-04-10T01:02:00Z"))
    put_res(tr9)                                         # the store moved on: an off-thread get must NOT see it
    off = [str(x) for x in WT.get(w)]
    reads_off = 0 if off == want else 1
    WT.T.clear()
    off_none = WT.get(w)
    FW.RAN.clear()
    WT.Q.clear()
    WT.want(w)
    WT.want(w)
    WT.want(w)
    n_q = int(FW.RAN.size())
    tr.setGameTime0(Inst.parse("0001-01-09T23:59:00Z"))
    put_res(tr)
    FW.RAN.get(0).run()
    after = [str(x) for x in WT.get(w)]
    q_clear = not WT.Q.containsKey("harness-world")
    WT.want(w)
    K.check(on == want and reads_on == 1 and off == want and reads_off == 0 and off_none is None and n_q == 1 and q_clear
            and after == ["23:59", "Day 9"] and int(FW.RAN.size()) == 2,
            "X2: WTime on the world's thread = read now %s (= 0.3.18's formulas %s); off the thread = the last read, the store untouched (%d "
            "reads), nothing known = null ('--:--'); want() x3 = ONE queued task; its run() refreshes the cache %s and frees the slot"
            % (on, want, reads_off, after))
    # fix round F1: a queued read whose task never ran (the world stopped) blocks for at most Q_STALE_MS, a fresh one still blocks
    Lng = JClass("java.lang.Long")
    Sysc = JClass("java.lang.System")
    FW.RAN.clear()
    WT.Q.clear()
    WT.Q.put("harness-world", Lng.valueOf(Sysc.currentTimeMillis() - 60000))      # a lost task from a stopped world
    WT.want(w)
    n_stale = int(FW.RAN.size())
    WT.want(w)                                                                       # now fresh -> blocks
    n_fresh = int(FW.RAN.size())
    WT.Q.put("harness-world", Lng.valueOf(Sysc.currentTimeMillis() + 60000))       # a clock that jumped back -> not trusted
    WT.want(w)
    n_future = int(FW.RAN.size())
    FW.RAN.get(n_future - 1).run()
    K.check(n_stale == 1 and n_fresh == 1 and n_future == 2 and not WT.Q.containsKey("harness-world") and int(WT.Q_STALE_MS) == 5000,
            "X2b (fix F1): a Q entry 60 s old (its task never ran) no longer blocks: want() queues (%d); a fresh entry still blocks (%d); a "
            "future stamp re-queues (%d); run() frees it" % (n_stale, n_fresh, n_future))
    # ------------------------------------------------------------------------------------ X3 hubWorld
    hub = os.path.join(scratch, "hub.properties")
    open(hub, "w").write("world=HubWorldA\n")
    WLn.HUBFILE = Paths.get(hub)
    WLn.HUBAT = 0
    WLn.HUBW = None
    a0 = WLn.hubWorld()
    WLn.hubRefresh()
    a1 = str(WLn.hubWorld())
    open(hub, "w").write("world=HubWorldB\n")
    WLn.hubRefresh()
    a2 = str(WLn.hubWorld())
    WLn.HUBAT = 1
    WLn.hubRefresh()
    a3 = str(WLn.hubWorld())
    br.put("island:hubWorld", "BridgeHub")
    a4 = str(WLn.hubWorld())
    br.remove("island:hubWorld")
    Mod = JClass("java.lang.reflect.Modifier")
    hw = WLn.class_.getDeclaredMethod("hubWorld")
    K.check(a0 is None and a1 == "HubWorldA" and a2 == "HubWorldA" and a3 == "HubWorldB" and a4 == "BridgeHub" and not Mod.isSynchronized(hw.getModifiers()),
            "X3: hubWorld: the file only through hubRefresh (at most every 15 s: %s -> %s -> %s), the bridge key island:hubWorld wins (%s), no "
            "longer synchronized" % (a1, a2, a3, a4))
    # ------------------------------------------------------------------------------------ X4 the minimap queue bounds (the REAL tap)
    MM, MS = P("new", "Minimap"), P("new", "MmSess")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    MIMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapImage")
    MCHc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapChunk")
    UWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMap")
    BFA = JClass("com.hypixel.hytale.server.core.universe.world.chunk.palette.BitFieldArr")

    def img():
        bf = BFA(JInt(1), JInt(4))
        return MIMc(JInt(2), JInt(2), JArray(JInt)([0x4f8a2eff]), JByte(1), bf.get())

    def upd(n, x0=0):
        arr = JArray(MCHc)(n)
        for i in range(n):
            arr[i] = MCHc(JInt(x0 + i), JInt(0), img())
        return UWMc(arr, None, None)

    def player(n):
        pr = U.allocateInstance(PRc.class_)
        jf(PRc, "uuid").set(pr, UUID(0x319, n))
        jf(PRc, "username").set(pr, "P%d" % n)
        s = MS(pr)
        MM.SESS.put(pr.getUuid(), s)
        return pr, s
    MM.SESS.clear()
    MM.GQN.set(0)
    MM.GQC.set(0)
    MM.TAPS = 1
    p1, s1 = player(1)
    for i in range(3):
        MM.tap(p1, upd(300, i * 300))
    c_ok = int(s1.qn.get()) == 3 and int(s1.qc.get()) == 900 and int(MM.GQN.get()) == 3 and int(MM.GQC.get()) == 900 and int(s1.keysOnly.get()) == 0
    MM.tap(p1, upd(300, 900))                            # 1,200 > 1,024 per player -> keys only
    k1 = int(s1.keysOnly.get()) == 1 and int(s1.qc.get()) == 900 and int(MM.GQC.get()) == 900
    p2, s2 = player(2)
    MM.GQC.set(4090)                                     # the other players hold 4,090 pieces: the global bound
    MM.tap(p2, upd(10))
    k2 = int(s2.keysOnly.get()) == 1 and int(s2.qc.get()) == 0 and int(MM.GQC.get()) == 4090
    e_rs = (int(s1.qn.get()) + int(s2.qn.get()), int(s1.qc.get()) + int(s2.qc.get()))
    MM.resync()
    rs = (int(MM.GQN.get()), int(MM.GQC.get()))
    MM.GQN.set(50000)
    d0 = int(s2.dropped.get())
    MM.tap(p2, upd(1))
    dropped_g = int(s2.dropped.get()) - d0 == 1 and int(MM.GQN.get()) == 50000
    MM.resync()
    n2 = int(s2.qn.get())
    for _i in range(21000):
        MM.tap(p2, UWMc(JArray(MCHc)(0), None, None))
    per_cap = int(s2.qn.get()) == 20000
    MM.drain(s1)
    dr = (int(s1.qn.get()), int(s1.qc.get()))
    MM.resync()
    g_after = (int(MM.GQN.get()), int(MM.GQC.get()))
    MM.drop(s2)
    g_drop = (int(MM.GQN.get()), int(MM.GQC.get()))
    K.check(c_ok and k1 and k2 and rs == e_rs == (5, 900) and dropped_g and per_cap and dr == (0, 0) and g_after[0] == 20000
            and g_after[1] == 0 and g_drop == (0, 0),
            "X4: the REAL tap: counts per player + global; 1,200 pieces > 1,024 -> keys only (%s); the GLOBAL piece bound sends a 10-piece packet "
            "keys only for a player holding none (%s); resync = the sum over the sessions %s; the global packet bound drops (%s); 20,000 packets "
            "a player (%s); drain gives back (%s), drop gives back %s" % (k1, k2, rs, dropped_g, per_cap, dr, g_drop))
    MM.SESS.clear()
    MM.TAPS = 0
    # ------------------------------------------------------------------------------------ X5a the tick + attach paths EXECUTED (stand-ins)
    PLc, TTk, HMc, ATc = P("new", "SkyyHudPlugin"), P("new", "TickTask"), P("new", "HudMain"), P("new", "AttachTask")
    plug = U.allocateInstance(PLc.class_)
    jf(PLc, "huds").set(plug, CHM())
    WLn.HUBAT = 0
    open(hub, "w").write("world=TickHub" + chr(10))
    TTk(plug).run()                                      # hubRefresh + tickAll (nobody) + resync + watchdog + DsLink.tick
    hm = U.allocateInstance(HMc.class_)
    for f_ in ("built", "shape", "models", "texts", "last", "wb", "narrow"):
        try:
            fld_ = jf(HMc, f_)
            fld_.set(hm, JClass(str(fld_.getType().getName()))())
        except Exception:
            pass
    wt0 = bool(hm.wantsTime())
    hm.tick()                                            # nothing shown -> returns at once (no PlayerRef needed)
    jf(HMc, "built").get(hm).put("Day", JClass("java.lang.Integer").valueOf(0))
    wt1 = bool(hm.wantsTime())
    HT.EXEC = None
    HT.start()
    pr_a = U.allocateInstance(PRc.class_)
    jf(PRc, "uuid").set(pr_a, UUID(0x319, 99))
    att = ATc(plug, pr_a)
    att.later(JLong(10))                                 # SkyyHud's thread; its run() sees an invalid player and stops
    time.sleep(0.3)
    HT.stop()
    K.check(str(WLn.hubWorld()) == "TickHub" and not wt0 and wt1 and int(MM.GQN.get()) == 0,
            "X5a: TickTask.run EXECUTED on a stand-in plugin (the hub file read there: %s); HudMain.tick with nothing shown returns at once; "
            "wantsTime follows the shown Game Clock / Day; AttachTask.later runs on SkyyHud's thread" % WLn.hubWorld())
    # ------------------------------------------------------------------------------------ X5 bytecode facts
    G = PWK.calls(JAR)
    chk = lambda m_, c_: c_ in G.get(m_, set())
    K.check(chk("SkyyHudPlugin.setup", "com.skyy.hud.HudThreads.start") and not any("SCHEDULED_EXECUTOR" in c for c in G.get("SkyyHudPlugin.setup", set()))
            and chk("SkyyHudPlugin.shutdown", "com.skyy.hud.HudThreads.stop") and chk("TickTask.run", "com.skyy.hud.Widgets.hubRefresh")
            and chk("TickTask.run", "com.skyy.hud.Minimap.resync") and chk("Widgets.text", "com.skyy.hud.WTime.get")
            and not chk("Widgets.text", "com.hypixel.hytale.component.Store.getResource")
            and [m_ for m_, cs in G.items() if "com.hypixel.hytale.component.Store.getResource" in cs] == ["WTime.read"]
            and chk("LayoutStore.save", "com.skyy.hud.HudThreads.write") and chk("AttachTask.later", "com.skyy.hud.HudThreads.later")
            and chk("SkyyHudPlugin.tickAll", "com.skyy.hud.WTime.want") and not any("Files" in c for c in G.get("Widgets.hubWorld", set())),
            "X5: bytecode: the tick on HudThreads; TickTask -> hubRefresh + resync; the world time only via WTime.get (Store.getResource only in "
            "WTime.read: %s); save -> HudThreads.write; AttachTask.later -> HudThreads.later; hubWorld reads no file"
            % [m_ for m_, cs in G.items() if "com.hypixel.hytale.component.Store.getResource" in cs])
    o_get = [m_ for m_, cs in PWK.calls(OLD_JAR).items() if "com.hypixel.hytale.component.Store.getResource" in cs]
    K.check(o_get == ["Widgets.text"], "X5: control - 0.3.18 read the store in Widgets.text (the 1 s tick thread): %s" % o_get)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    LS, Cfg, Pub, Wid = P("LayoutStore"), P("HudCfg"), P("CfgPub"), P("Widgets")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    lyd = os.path.join(home, "layouts")
    players = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []
    res = []
    for _n in range(2):
        b0 = HK.tree_hash(mods)
        LS.CACHE.clear()
        LS.DIR = Paths.get(lyd)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Wid.HUBFILE = Paths.get(os.path.join(mods, "Skyy_SkyyIslands", "hub.properties"))
        Cfg.load()
        Pub.start(Paths.get(mods), None)
        r_ = {}
        for us in players:
            mp = LS.get(UUID.fromString(us))
            r_[us] = dict((str(w_), str(mp.get(w_).ser())) for w_ in Wid.IDS)
        Pub.flush()
        a0 = HK.tree_hash(mods)
        res.append((r_, sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))))
    K.check(res[0][1] == [] and res[1][1] == [] and res[0][0] == res[1][0],
            "ST: two starts on a COPY of the live Skyy_SkyyHud (%d layouts): nothing written, the same layouts: %s" % (len(players), [r[1] for r in res]))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("exec", run_exec), ("live", run_live)], os.path.abspath(__file__),
           live=(LIVE_DIR, "Skyy_SkyyHud"))
