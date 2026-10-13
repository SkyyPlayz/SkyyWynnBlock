"""Harness for SkyyExploration 0.2.7 (lag fixes: the SkyyExploration-IO writer, luggage write-ahead acts, one luggage pass per world,
change-driven title publishing, ExpStore.snap off the monitor, lock-free bridge; tools/exploration_0_2_7_patch.py).
Build first: python tools/exploration_0_2_7_patch.py && python SkyyExploration/build_skyyexploration_0.2.7.py

    python SkyyExploration/test_skyyexploration_0.2.7.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.2.6 -> 0.2.7: exactly the planned members differ (+ LgAct, LgIO)
  X  exec     EVERY NEW CODE PATH (-Xverify:all): bridge0 / bridge (every bridge() of the jar lock-free); static: Thread.sleep only in
              ExpIO.moveRetry; LgReg.write0 only under WLOCK; saveSoon -> ExpIO.exec; use(): the claim is saved (saveGen) before any loot,
              claimOk = loot, then vanish, then save; ExpTick.second hashes before check / publish; LgIO thread factory (SkyyExploration-IO,
              daemon); ExpIO.exec on the writer + its shared-scheduler fallback; LgReg.saveGen with IO running (returns at once while the
              writer is held, generation numbers, done / failed / settled, the file written by SkyyExploration-IO, newest text wins);
              WRITE-AHEAD through the writer: spawn = the line first, the block only after done() (runActs), a FAILED write = the new
              site dropped and never placed, retryFailed writes the newest text; respawn the same (placed after the write, count 3);
              sweep leaves a pending site alone; actFail of a claim (undone + the hour slot back); worldPass once per world per second
              (900 ms gate), near marks from every collected position, respawn skipped while nothing is due; known() remembers "no file"
              until a file is written; ready() reads a world's file on the writer; ExpTitles.hash changes with its inputs only;
              ExpIO.stop + synchronous saves after it; FIX 1 (review): a saved claim whose claimer is gone when its act runs is UNDONE
              (claim + hour slot back, registry saved), runActs / dropActs take an act with remove(act), flushAll undoes every act still
              waiting at shutdown (the claim claimable again, the new site dropped) before the last saves
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyyExploration: every player record read by 0.2.6 AND 0.2.7 (own loaders)
              gives the same snap() (the off-monitor build = the same properties); every luggage registry read on the writer and saved
              back byte-identical; no other file changes
  AA engine-access audit
Behaviour regression (separately, same jar): python SkyyExploration/test_skyyexploration_0.2.6.py --jar SkyyExploration/SkyyExploration-0.2.7.jar
(245 ok; its only fails: its 0.2.5 -> 0.2.6 class compare / manifest, the migration log line naming 0.2.7, and its X15 bytecode check
that looks for loot / vanish inside use() - they moved to claimOk, which X here checks).
Scratch: tools/dev/scratch/perfworld/exploration (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.2.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfworld", "exploration")))
PKG = "com.skyy.explore."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyExploration")

EXPECT = {
    "ExpIO": ["+f BRIDGE", "+f EXEC", "+f STOPPING", "+m bridge0", "~m bridge", "+m exec", "+m stop", "~<clinit>"],
    "ExpStore": ["+m head", "~m snap", "~m saveSoon"],
    "SpotReg": ["~m saveSoon"],
    "ExpState": ["+f pubHash", "+f pubAt"],
    "ExpTitles": ["+m hash"],
    "ExpTick": ["~m second"],
    "ExpSaver": ["~m run"],
    "LgSite": ["+f pend"],
    "LgReg": ["+f PEND", "+f QUEUED", "+f BUSY", "+f DONE", "+f FAILED", "+f SEQ", "+f ACTS", "+f NOFILE", "+f LOADING", "+f WLOCK",
              "+f WRITES", "+f LASTW", "+m text", "+m write0", "+m writeOne0", "+m writeOne", "+m queue", "+m seq", "+m saveGen", "~m save",
              "+m done", "+m failed", "+m settled", "+m has", "+m kick", "+m later", "+m runWrite", "+m retryFailed", "+m ready",
              "+m runLoad", "~m known", "~<clinit>"],
    "LgCore": ["+f POS", "+f PASS", "+f PASSES", "+m capDrop", "+m act", "+m placeNow", "+m release", "+m whoUndo", "+m whoLast", "~m spawn", "~m sweep", "~m respawn",
               "+m addPos", "+m anyDue", "+m worldPass", "~m second", "+m claimOk", "+m undo", "+m claimLost", "+m claimLater", "+m actOk",
               "+m actFail", "+m runActs", "+m dropActs", "~m flushAll", "~m use", "~<clinit>"],
    "SkyyExplorationPlugin": ["~m setup", "~m shutdown"],
    "ExpLgMig": ["~m logLine", "~m migrate"],   # its WHO constant (inlined) names the version ("SkyyExploration 0.2.7")
    # the config kit (tools/skyycfg.py, rebuilt): its lock-free CfgRows.bridge (2026-10-13)
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header", "~<clinit>"],
    "CfgFn": ["~m opExport"],
    "ExpCfg": ["~m load"],      # the kit's default config text (a constant) changed with the kit
}
ADDED = ["LgAct", "LgIO"]


def sim(state):
    from jpype import JImplements, JOverride, JArray, JObject, JInt
    G = state["ground"]

    @JImplements(PKG + "LgApi")
    class Sim(object):
        @JOverride
        def blockId(self, w, x, y, z):
            if (x, y, z) in state["placed"]:
                return state["placed"][(x, y, z)]
            return G if y <= 64 else "Empty"
        @JOverride
        def height(self, w, x, z): return 64
        @JOverride
        def hasEntity(self, w, x, y, z): return False
        @JOverride
        def fluid(self, w, x, y, z): return False
        @JOverride
        def place(self, w, x, y, z, id_):
            state["placed"][(x, y, z)] = str(id_)
            state["log"].append(("place", x, y, z))
            return True
        @JOverride
        def clear(self, w, x, y, z):
            state["placed"].pop((x, y, z), None)
            state["log"].append(("clear", x, y, z))
            return True
        @JOverride
        def levelAt(self, wn, x, y, z): return JArray(JObject)([JInt(5), JInt(9)])
        @JOverride
        def occupied(self, w, x, y, z): return False
        @JOverride
        def sound(self, w, x, y, z): state["log"].append(("sound", x, y, z))
        @JOverride
        def poof(self, w, x, y, z): pass
    return Sim()


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, synchronized
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    EIO, Reg, Core, Site, Act, LIO, Eng, Cfg, Ttl, Sto, Dat = (P("ExpIO"), P("LgReg"), P("LgCore"), P("LgSite"), P("LgAct"), P("LgIO"),
                                                               P("LgEng"), P("ExpCfg"), P("ExpTitles"), P("ExpStore"), P("ExpData"))
    Sys, Paths, Executors, Thread = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.lang.Thread")
    me = str(Thread.currentThread().getName())
    # ---- A: bridge
    K.check(EIO.BRIDGE is None, "X bridge: BRIDGE empty before the first call")
    m1 = EIO.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1) and Sys.identityHashCode(EIO.BRIDGE) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(EIO.bridge()) == Sys.identityHashCode(m1) and Sys.identityHashCode(EIO.bridge0()) == Sys.identityHashCode(m1),
            "X bridge: created once, cached in BRIDGE, the same map")
    PW.bridge_static(K, jar)
    g = PW.calls(jar)
    K.eq([m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")], ["ExpIO.moveRetry"], "X static: Thread.sleep only in ExpIO.moveRetry")
    K.eq(PW.callers(g, "LgReg.write0", PKG), ["LgReg.writeOne0"], "X static: LgReg.write0 only from writeOne0")
    K.eq(PW.callers(g, "LgReg.writeOne0", PKG), ["LgReg.writeOne"], "X static: writeOne0 only under WLOCK (writeOne)")
    K.check(PKG + "ExpIO.exec" in g["ExpStore.saveSoon"] and PKG + "ExpIO.exec" in g["SpotReg.saveSoon"]
            and not any("ScheduledExecutorService" in c for c in g["ExpStore.saveSoon"] | g["SpotReg.saveSoon"]),
            "X static: ExpStore.saveSoon / SpotReg.saveSoon hand their task to ExpIO.exec (the writer)")
    K.check(PKG + "LgReg.save" not in g["LgCore.use"] and PKG + "LgReg.saveGen" in g["LgCore.use"] and PKG + "LgCore.loot" not in g["LgCore.use"]
            and PKG + "LgCore.claimOk" in g["LgCore.use"] and PKG + "LgReg.later" in g["LgCore.use"],
            "X static: use() saves the claim (saveGen) and gives the loot only through claimOk (now when written, else later)")
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def bc(cn, m):
        o_ = []
        for mm in CP.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == m:
                bos = JClass("java.io.ByteArrayOutputStream")()
                IP(JClass("java.io.PrintStream")(bos)).print_(mm)
                o_.append(str(bos.toString()))
        return "\n".join(o_)
    ck = bc("LgCore", "claimOk")
    K.check("LgCore.loot" in ck and "LgCore.vanish" in ck and "LgReg.save" in ck and ck.index("LgCore.loot") < ck.index("LgCore.vanish") < ck.rindex("LgReg.save"),
            "X static: claimOk = the loot, then the vanish, then the save (0.2.5's order)")
    tk = bc("ExpTick", "second")
    K.check("ExpTitles.hash" in tk and tk.index("ExpTitles.hash") < tk.index("ExpTitles.check") and tk.rindex("ExpTitles.hash") < tk.index("ExpTitles.publish"),
            "X static: ExpTick.second hashes the inputs before check / publish")
    sn = bc("ExpStore", "snap")
    K.check("monitorenter" not in sn and "ExpStore.head" in sn and "synchronized" in str(JClass("java.lang.reflect.Modifier").toString(CP.get(PKG + "ExpStore").getDeclaredMethod("head").getModifiers())),
            "X static: ExpStore.snap holds no monitor (head() does, briefly)")
    # ---- the writer
    t = LIO(9, None).newThread(LIO(1, "none"))
    K.check(str(t.getName()) == "SkyyExploration-IO" and t.isDaemon(), "X LgIO.newThread: SkyyExploration-IO, daemon")
    names = []

    @JImplements("java.lang.Runnable")
    class R(object):
        @JOverride
        def run(self):
            names.append(str(Thread.currentThread().getName()))
    EIO.EXEC = Executors.newSingleThreadScheduledExecutor(LIO(9, None))
    getattr(EIO, "exec_")(R())
    K.check(PW.wait_until(lambda: names == ["SkyyExploration-IO"]), "X ExpIO.exec runs on SkyyExploration-IO (%s)" % names)
    # ---- LgReg + LgCore through the writer
    d = os.path.join(scratch, "x")
    Reg.DIR = Paths.get(os.path.join(d, "luggage"))
    ground = str(Cfg.LG_GROUND).split(",")[0].strip() + "_Test"
    state = {"placed": {}, "log": [], "ground": ground}
    Eng.API = sim(state)
    CR_ = P("ChestReg")
    WF = str(CR_.wf("w1"))
    NF = str(CR_.wf("nofile"))
    K.check(Reg.ready("w1") is False, "X ready: false at first (the read is queued on the writer)")
    K.check(PW.wait_until(lambda: Reg.W.containsKey(WF)) and Reg.ready("w1"), "X ready: read by SkyyExploration-IO, then true")
    sites = Reg.sites("w1")
    now = int(time.time() * 1000)
    n0 = Core.N[0]
    with synchronized(Reg.WLOCK):
        w0 = Reg.WRITES.get()
        t0 = time.time()
        s = Core.spawn(None, "w1", sites, 10, 65, 10, 1, 7, now)
        dt = time.time() - t0
        K.check(s is not None and s.pend == 1 and not state["placed"] and Reg.WRITES.get() == w0 and dt < 0.5,
                "X spawn (IO on): the site waits (pend 1), NO block yet, nothing written by the caller (%.1f ms)" % (dt * 1000))
        gen = Reg.seq(WF).get()
        K.check(not Reg.done("w1", gen) and not Reg.settled("w1") and Reg.ACTS.get(WF).size() == 1, "X spawn: not done, one act waiting")
        K.check(Core.runActs(WF) == 0 and not state["placed"], "X runActs before the write: nothing runs")
    K.check(PW.wait_until(lambda: Reg.done("w1", gen)), "X the writer wrote generation %d" % gen)
    K.check(str(Reg.LASTW) == "SkyyExploration-IO", "X written by SkyyExploration-IO (%s)" % Reg.LASTW)
    f1 = os.path.join(d, "luggage", WF + ".tsv")
    K.check(str(s.line()) in open(f1, encoding="utf8").read(), "X the line is on disk before the block exists")
    K.check(Core.runActs(WF) == 1 and (10, 65, 10) in state["placed"] and s.pend == 0 and Core.N[0] == n0 + 1,
            "X runActs after the write: the block placed, pend 0, counted 'placed'")
    # a failed write: the new site is dropped, never placed
    open(os.path.join(d, "blocked"), "w").write("x")
    Reg.DIR = Paths.get(os.path.join(d, "blocked", "luggage"))
    s2 = Core.spawn(None, "w1", sites, 50, 65, 50, 2, 7, now)
    g2 = Reg.seq(WF).get()
    K.check(s2 is not None and PW.wait_until(lambda: Reg.failed("w1", g2)), "X a write into a blocked folder FAILS (failed(gen))")
    K.check(Core.runActs(WF) == 1 and (50, 65, 50) not in state["placed"] and not Reg.has(sites, s2), "X failed: the act's undo - the site dropped, never placed")
    PW.wait_until(lambda: Reg.FAILED.containsKey(WF) and not Reg.QUEUED.containsKey(WF) and not Reg.BUSY.containsKey(WF))
    os.remove(os.path.join(d, "blocked"))
    Reg.DIR = Paths.get(os.path.join(d, "luggage"))
    K.check(Reg.retryFailed() >= 1 and PW.wait_until(lambda: Reg.settled("w1")), "X retryFailed writes the newest text (settled)")
    txt = open(f1, encoding="utf8").read()
    K.check(str(s.line()) in txt and "\t50\t" not in txt.split("\n", 1)[1], "X the file holds the first site, not the dropped one")
    # sweep leaves a pending site alone
    with synchronized(Reg.WLOCK):
        s3 = Core.spawn(None, "w1", sites, 90, 65, 90, 1, 7, now)
        Core.SWEPT.clear()
        Core.sweep(None, "w1", sites, now + 5000)
        K.check(Reg.has(sites, s3) and s3.pend == 1, "X sweep leaves a site whose block waits for its write alone")
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    K.check((90, 65, 90) in state["placed"], "X ... and it is placed after the write")
    # respawn through the writer
    resp = int(Cfg.LG_RESPAWN_S) * 1000
    s.state, s.lootedAt = 2, now - resp - 10
    state["placed"].pop((10, 65, 10), None)
    n3 = Core.N[3]
    with synchronized(Reg.WLOCK):
        r = Core.respawn(None, "w1", sites, 12.0, 12.0, now)
        K.check(r == 1 and s.state == 0 and s.pend == 1 and (10, 65, 10) not in state["placed"], "X respawn (IO on): back in the registry, the block waits")
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    K.check((10, 65, 10) in state["placed"] and Core.N[3] == n3 + 1 and s.pend == 0, "X respawn: placed after the write, counted 'came back'")
    # claim undo (actFail kind 1)
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("00000000-0000-4000-8000-000000000042")
    a = Core.act(1, None, "w1", s, 999999)
    a.u, a.at, a.oldWho, a.oldState, a.oldAt = u, now, "", 0, 0
    s.who, s.state, s.lootedAt = "x", 1, now
    Core.capAdd(u, now)
    Core.actFail(a)
    K.check(str(s.who) == "" and s.state == 0 and s.lootedAt == 0 and Core.capOk(u, now) and Core.HOUR.get(u).size() == 0,
            "X actFail(claim): the claim undone and the hour slot given back")
    PW.wait_until(lambda: Reg.settled("w1"))
    # FIX 1a: the claim's write lands but the claimer is gone (pr None = no reference) -> undone, never kept without loot
    K.check(any(str(c).endswith("ConcurrentLinkedQueue.remove") for c in g["LgCore.runActs"]) and PKG + "LgCore.undo" in g["LgCore.claimLost"]
            and PKG + "LgCore.claimLost" in g["LgCore.claimLater"] and PKG + "LgCore.dropActs" in g["LgCore.flushAll"],
            "X FIX 1 static: runActs takes an act with remove(act); claimLater -> claimLost -> undo; flushAll -> dropActs")
    n1 = Core.N[1]
    with synchronized(Reg.WLOCK):
        ow, ost, oat = str(s.who), s.state, s.lootedAt
        s.claim(u, now, 600000)
        s.state, s.lootedAt = 1, now
        ga = Reg.saveGen("w1")
        Core.capAdd(u, now)
        a1 = Core.act(1, None, "w1", s, ga)
        a1.u, a1.at, a1.oldWho, a1.oldState, a1.oldAt = u, now, ow, ost, oat
        Reg.later("w1", a1)
        K.check(not Core.capOk(u, now) or Core.HOUR.get(u).size() == 1, "X FIX 1a setup: the claim is pending, its hour slot used")
    K.check(PW.wait_until(lambda: Reg.done("w1", ga)), "X FIX 1a: the claim's write landed")
    K.check(Core.runActs(WF) == 1, "X FIX 1a: runActs ran the claim act")
    PW.wait_until(lambda: Reg.settled("w1"))
    txt = open(f1, encoding="utf8").read()
    K.check(str(s.who) == ow and s.state == ost and s.lootedAt == oat and Core.HOUR.get(u).size() == 0 and Core.N[1] == n1
            and str(s.line()) in txt and Reg.ACTS.get(WF).isEmpty(),
            "X FIX 1a: claimer gone -> the claim undone on disk too, the hour slot back, no claim counted, nothing left waiting")
    # FIX 2 (review 2): a waiting claim raises pend (the sweep cannot vanish it), the claim keeps its profile key, undo removes only its own entry
    ub = bc("LgCore", "use")
    K.check("ExpIO.pkey" in ub and "LgAct.k" in ub and "LgAct.newWho" in ub and "LgAct.hold" in ub and "LgSite.pend" in ub
            and ub.rindex("LgSite.pend") < ub.rindex("LgReg.later") and ub.index("LgReg.saveGen") < ub.index("LgSite.pend"),
            "X FIX 2 static: use() stores the profile key + its claims text and raises pend (after the save, before later)")
    cl = bc("LgCore", "claimLater")
    K.check("ExpIO.busy" in cl and "ExpIO.switchWait" in cl and "ExpIO.pkey" in cl and "LgAct.k" in cl
            and cl.index("ExpIO.pkey") < cl.rindex("LgCore.claimOk") and cl.count("LgCore.claimLost") >= 4,
            "X FIX 2 static: claimLater re-checks the profile (busy / switchWait / key) before claimOk, else claimLost")
    K.check(PKG + "LgCore.release" in g["LgCore.claimOk"] and PKG + "LgCore.release" in g["LgCore.undo"] and PKG + "LgCore.whoUndo" in g["LgCore.undo"],
            "X FIX 2 static: claimOk and undo release the claim's pend; undo uses whoUndo")
    ow, ost, oat = str(s.who), s.state, s.lootedAt
    K.check(ost == 0 and (10, 65, 10) in state["placed"], "X FIX 2a setup: the luggage is out (state 0, block placed)")
    with synchronized(Reg.WLOCK):
        s.claim(u, now, 600000)
        s.state, s.lootedAt = 1, now
        gc = Reg.saveGen("w1")
        Core.capAdd(u, now)
        a2 = Core.act(1, None, "w1", s, gc)
        a2.u, a2.at, a2.oldWho, a2.oldState, a2.oldAt, a2.newWho, a2.k = u, now, ow, ost, oat, s.who, str(u)
        a2.hold = 1
        s.pend = s.pend + 1
        Reg.later("w1", a2)
        Core.SWEPT.clear()
        Core.sweep(None, "w1", sites, now + 5000)
        K.check(s.state == 1 and s.pend == 1 and (10, 65, 10) in state["placed"],
                "X FIX 2a: the sweep (share 0, claim due) leaves a luggage whose claim waits for its write alone")
    K.check(PW.wait_until(lambda: Reg.done("w1", gc)) and Core.runActs(WF) == 1, "X FIX 2a: the write landed, the claim act ran (claimer gone)")
    K.check(s.pend == 0 and a2.hold == 0 and s.state == ost and str(s.who) == ow and Core.HOUR.get(u).size() == 0,
            "X FIX 2a: undone - pend released once, the claim and the hour slot back")
    Core.release(a2)
    K.check(s.pend == 0, "X FIX 2a: a second release changes nothing")
    Core.SWEPT.clear()
    Core.sweep(None, "w1", sites, now + 7000)
    K.check(s.state == 0 and Reg.has(sites, s) and (10, 65, 10) in state["placed"], "X FIX 2a: after the next sweep the luggage is still out and claimable")
    PW.wait_until(lambda: Reg.settled("w1"))
    # FIX 2b: share time > 0, A and B claim while A's write waits; A's undo keeps B's claim (and the claimed state)
    sh0 = Cfg.LG_SHARE_S
    Cfg.LG_SHARE_S = 60
    ub_ = UUID.fromString("00000000-0000-4000-8000-0000000000b2")
    w0_, st0, at0 = str(s.who), s.state, s.lootedAt
    s.claim(u, now, 600000)
    s.state, s.lootedAt = 1, now
    aA = Core.act(1, None, "w1", s, 999998)
    aA.u, aA.at, aA.oldWho, aA.oldState, aA.oldAt, aA.newWho, aA.hold = u, now, w0_, st0, at0, s.who, 1
    s.pend = s.pend + 1
    Core.capAdd(u, now)
    wA, stA, atA = str(s.who), s.state, s.lootedAt
    s.claim(ub_, now + 3, 600000)
    aB = Core.act(1, None, "w1", s, 999999)
    aB.u, aB.at, aB.oldWho, aB.oldState, aB.oldAt, aB.newWho, aB.hold = ub_, now + 3, wA, stA, atA, s.who, 1
    s.pend = s.pend + 1
    Core.capAdd(ub_, now + 3)
    Core.undo(aA, False)
    K.check(s.claimedAt(ub_) == now + 3 and s.claimedAt(u) == 0 and s.state == 1 and s.lootedAt == now and s.pend == 1
            and Core.HOUR.get(u).size() == 0 and Core.HOUR.get(ub_).size() == 1,
            "X FIX 2b: A's undo removes only A's claim - B's claim, the claimed state and B's hour slot stay (%s)" % s.who)
    Core.undo(aB, False)
    K.check(str(s.who) == "" and s.state == 0 and s.lootedAt == 0 and s.pend == 0 and Core.HOUR.get(ub_).size() == 0,
            "X FIX 2b: then B's undo too -> nobody's claim left, the luggage out again (%s / %d)" % (s.who, s.state))
    old_ = "%s:%d;x:5" % (u, now - 99999)
    K.check(str(Core.whoUndo("x:5;%s:%d;y:7" % (u, now), old_, u, now)) == "%s:%d;x:5;y:7" % (u, now - 99999),
            "X FIX 2b: whoUndo drops only uuid:at and brings back the claimer's older entry (the cooldown record)")
    K.check(Core.whoLast("a:5;b:9;c:7") == 9 and Core.whoLast("") == 0, "X FIX 2b: whoLast = the newest claim time")
    Cfg.LG_SHARE_S = sh0
    # worldPass
    Core.PASS.clear()
    Core.POS.clear()
    s.lastNear = 0
    s3.lastNear = 0
    Core.addPos("w1", 500.0, 500.0)
    Core.addPos("w1", 15.0, 15.0)
    p0 = Core.PASSES.get()
    K.check(Core.worldPass(None, "w1", sites, now) and not Core.worldPass(None, "w1", sites, now + 500) and Core.PASSES.get() == p0 + 1,
            "X worldPass: once per world per second (the second call 500 ms later is skipped)")
    K.check(s.lastNear == now and s3.lastNear != now, "X worldPass: near marks from every collected position (the 2nd player's)")
    K.check(Core.POS.get("w1") is None, "X worldPass: the positions are consumed")
    nb = len(state["log"])
    K.check(not Core.anyDue(sites, now), "X anyDue: nothing gone is due")
    Core.addPos("w1", 15.0, 15.0)
    K.check(Core.worldPass(None, "w1", sites, now + 1000) and len(state["log"]) == nb, "X worldPass: no respawn work while nothing is due")
    # known() + NOFILE
    K.check(not Reg.known("nofile") and Reg.NOFILE.containsKey(NF), "X known(): no file -> remembered")
    open(os.path.join(d, "luggage", NF + ".tsv"), "w").write("")
    K.check(not Reg.known("nofile"), "X known(): the remembered answer (no stat)")
    Reg.W.put(NF, JClass("java.util.ArrayList")())
    Reg.save("nofile")
    PW.wait_until(lambda: Reg.settled("nofile"))
    Reg.W.remove(NF)
    K.check(not Reg.NOFILE.containsKey(NF) and Reg.known("nofile"), "X known(): a write clears it")
    # ExpTitles.hash
    dd = Dat()
    dd.key = "k1"
    dd.zones = JClass("java.util.concurrent.ConcurrentHashMap")()
    h1 = Ttl.hash(u, dd, 5)
    K.check(Ttl.hash(u, dd, 5) == h1, "X hash: stable for the same inputs")
    dd.chests = dd.chests + 1
    h2 = Ttl.hash(u, dd, 5)
    dd.zones.put("Zone1", JClass("java.lang.Boolean").TRUE)
    h3 = Ttl.hash(u, dd, 5)
    dd.title = "explorer"
    h4 = Ttl.hash(u, dd, 5)
    K.check(len({h1, h2, h3, h4, Ttl.hash(u, dd, 6)}) == 5, "X hash: changes with chests, zones, title, level")
    # stop + synchronous saves
    with synchronized(Reg.WLOCK):
        s.lastNear = 1
        Reg.save("w1")
        # FIX 1b: a claim + a new site still waiting when the server stops
        ow3, ost3, oat3 = str(s3.who), s3.state, s3.lootedAt
        s3.claim(u, now, 600000)
        s3.state, s3.lootedAt = 1, now
        gb = Reg.saveGen("w1")
        Core.capAdd(u, now)
        a3 = Core.act(1, None, "w1", s3, gb)
        a3.u, a3.at, a3.oldWho, a3.oldState, a3.oldAt = u, now, ow3, ost3, oat3
        Reg.later("w1", a3)
        s4 = Core.spawn(None, "w1", sites, 130, 65, 130, 1, 7, now)
        K.check(s4 is not None and s4.pend == 1 and Reg.ACTS.get(WF).size() == 2, "X FIX 1b setup: a claim and a new site wait for the write")
    EIO.STOPPING = True
    EIO.stop()
    K.check(EIO.EXEC is None and Reg.settled("w1"), "X ExpIO.stop: the writer's queue done")
    K.check(Reg.ACTS.get(WF).size() == 2, "X FIX 1b: after stop both acts still wait (their World.execute never ran)")
    Core.flushAll()
    txt = open(f1, encoding="utf8").read()
    K.check(Reg.ACTS.get(WF).isEmpty() and str(s3.who) == ow3 and s3.state == ost3 and s3.lootedAt == oat3 and Core.HOUR.get(u).size() == 0
            and str(s3.line()) in txt, "X FIX 1b: flushAll undid the waiting claim (claimable again, hour slot back) and saved it")
    K.check(not Reg.has(sites, s4) and (130, 65, 130) not in state["placed"] and "\t130\t" not in txt.split("\n", 1)[1],
            "X FIX 1b: the waiting new site dropped (no line, no block)")
    gl = Reg.saveGen("w1")
    K.check(gl > 0 and Reg.done("w1", gl) and str(Reg.LASTW) == me, "X after stop: saveGen writes synchronously (0.2.6)")
    K.save()


def loader_for(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths, Executors, UUID = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.util.UUID")
    h0 = HK.tree_hash(home)
    pd = os.path.join(home, "players")
    keys = sorted(n[:-11] for n in os.listdir(pd) if n.endswith(".properties")) if os.path.isdir(pd) else []
    for start in (1, 2):
        Lo, Ln = loader_for(OLD_JAR), loader_for(jar)
        So, Sn = JClass(PKG + "ExpStore", loader=Lo), JClass(PKG + "ExpStore", loader=Ln)
        for S_ in (So, Sn):
            S_.DIR = Paths.get(pd)
        diff = []
        for k in keys:
            uu = UUID.fromString(k[:36]) if len(k) >= 36 else UUID.randomUUID()
            So.dataK(k, uu)
            Sn.dataK(k, uu)
            po, pn = So.snap(k), Sn.snap(k)
            if (po is None) != (pn is None) or (po is not None and not po.equals(pn)):
                diff.append(k)
        K.check(not diff and len(keys) > 0, "D start %d: %d live records: 0.2.7 snap() = 0.2.6 snap() (diffs %s)" % (start, len(keys), diff[:3]))
        Reg, EIO, LIO = JClass(PKG + "LgReg", loader=Ln), JClass(PKG + "ExpIO", loader=Ln), JClass(PKG + "LgIO", loader=Ln)
        ld = os.path.join(home, "luggage")
        Reg.DIR = Paths.get(ld)
        EIO.EXEC = Executors.newSingleThreadScheduledExecutor(LIO(9, None))
        worlds = []
        for n in (sorted(os.listdir(ld)) if os.path.isdir(ld) else []):
            if n.endswith(".tsv"):
                hd = open(os.path.join(ld, n), encoding="utf8").readline()
                worlds.append(hd.split(" - world ", 1)[1].rsplit(": x y z", 1)[0])
        for wn in worlds:
            Reg.ready(wn)
        K.check(PW.wait_until(lambda: all(Reg.W.containsKey(JClass(PKG + "ChestReg", loader=Ln).wf(w)) for w in worlds)),
                "D start %d: every luggage registry read on the writer (%s)" % (start, worlds))
        for wn in worlds:
            Reg.save(wn)
        EIO.STOPPING = True
        EIO.stop()
        h1 = HK.tree_hash(home)
        K.check(h1 == h0, "D start %d: every file byte-identical (records read twice, registries saved back): %s"
                % (start, sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))[:8]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyExploration"))
