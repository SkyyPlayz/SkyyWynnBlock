"""SkyyExploration 0.2.3 - bare-JVM harness for the page guard (tools/exploration_0_2_3_patch.py).

    python SkyyExploration/test_skyyexploration_0.2.3.py [--jar <SkyyExploration-0.2.3.jar>] [--old <SkyyExploration-0.2.2.jar>]
                                                         [--dir <scratch folder>] [--keep]

Build first: python tools/exploration_0_2_3_patch.py, then python SkyyExploration/build_skyyexploration_0.2.3.py. The old jar defaults to
SkyyExploration-0.2.2.jar next to this file (the live SET pin; rebuild it with build_skyyexploration_0.2.2.py on a fresh checkout).
Carried forward: test_skyyexploration_0.2.2.py's child steps (its run_states / run_bytecode / compare_state, loaded from that file).
Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + ONE mod jar):
  A  every class of the 0.2.3 jar AND of the 0.2.2 jar loads and initializes under -Xverify:all
  B  the 17 ExplorePage + 15 AdminPage states of the 0.2.2 harness are IDENTICAL on both jars (every UI command and event binding);
     C / D of the 0.2.2 harness run on them (ids, b.set values, inline texts, check_markup / check_page / assert_proven, layout fit)
  E  msgColor / stColor answer exactly as 0.2.2's
  F  class bytes 0.2.2 vs 0.2.3: only ExplorePage + AdminPage (changed build / handleDataEvent only; new changedWorld / isOpen / answer /
     watchTick + the guard fields), SkyyExplorationPlugin (setup / shutdown), the version string (ExpCfg, CfgRows) and manifest.json
     differ; new classes ExGuard + ExWatch only
  P  THE PAGE FLOWS on the ENGINE'S OWN PageManager (init(playerRef, windowManager) as the engine does) for both jars, with stand-ins
     (a Store answering getComponent from a map, a recording packet handler, stand-in Universe / EntityModule / worlds with a task queue,
     a recording scheduler) and a model client (the SkyyMenu 0.3.6 / SkyyBank 0.1.6 harness model: it acknowledges every CustomPage for
     the page it shows and a SetPage that closes it, nothing while it shows no page, drops its page at a world change; a click = the
     binding's own EventData; it WAITS ("Loading...") after every click until a page packet comes). A world change runs the engine's
     order: removeFromStore -> AddPlayerToWorldEvent (0.2.3: ExGuard.accept) -> clearCustomPageAcknowledgements + the client drops its
     page -> addToStore (a new ref in the new world's store). NO SkyyMenu here (its PageGuard is not loaded): Exploration on its own.
       P1 SKYY'S REPORT (same world): Zones, then Overview within 1 s - 0.2.2 drops the Overview click silently (the client waits,
          0 acknowledgements pending: NOT the engine's counter), a re-opened /explore works (as Skyy saw); 0.2.3 shows Overview at once.
          A title click within 1 s: 0.2.2 silent, 0.2.3 answered WITHOUT acting (the result line unchanged); after 1 s it acts on both.
       P2 a page left open across a world change + a page close on the new world (a bench / another mod's setPage(None)): 0.2.2 1
          acknowledgement pending, the re-opened /explore drops every click; 0.2.3 forgets the page at the join (no packet) -> 0 pending.
       P3 the safety net: a stray +1 while the page is open (both jars drop the next click); 0.2.3's own check (the ExWatch the page's
          first build scheduled -> World.execute -> watchTick) heals: one WARNING, the counter reset, the page answered (the heal line),
          the next click works, the check keeps running; at most 3 heal answers per page.
       P4 a healthy page: the check sends nothing, its test click acts on nothing; P5 a world change without the event: the check
          forgets the page on the new world (no packet); P6 ExGuard: Exploration pages forgotten at the event, a foreign page left alone
          (SkyyMenu's job), world joins counted; P7 no answer to a closed page (Esc, then answer()); P8 the admin page: a quick tab
          acts, other quick clicks are answered without acting, an unknown click is answered; Teleport (closes the page) sends no answer.
       P9 the real timer chain with a real scheduled executor (1 s): scheduler thread -> World.execute -> watchTick.
Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyexploration-023 (git-ignored), deleted at the end unless --keep;
TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, zipfile, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.3", "0.2.2"
PKG = "com.skyy.explore."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyexploration-023")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyExploration-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
FAILS = []
OKS = [0]

# the 0.2.2 harness (its child steps + comparisons), pointed at this run's scratch folder and versions
_spec = importlib.util.spec_from_file_location("test_skyyexploration_022", os.path.join(HERE, "test_skyyexploration_0.2.2.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
H.SCRATCH, H.VERSION, H.OLD_VERSION, H.FAILS, H.OKS = SCRATCH, VERSION, OLD_VERSION, FAILS, OKS


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ============================================================================================ child: the page flows of one jar
def run_pages(jar, tag, out):
    import jpype
    import skyybuild as B
    from jpype import JClass, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    hcls = os.path.join(SCRATCH, "hclasses-" + tag)
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(hcls, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST, hcls], convertStrings=True)
    NEW = tag == "new"
    R = {"tag": tag, "jar": jar}
    CPc = JClass("javassist.ClassPool")
    HP = CPc(False)
    HP.appendSystemPath()
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def hclass(name, sup, ctor, fields=(), meths=(), ifaces=()):
        c = HP.makeClass(name, HP.get(sup)) if sup else HP.makeClass(name)
        for i_ in ifaces:
            c.addInterface(HP.get(i_))
        for s_ in fields:
            c.addField(CtField.make(s_, c))
        if ctor:
            c.addConstructor(CtNewConstructor.make(ctor, c))
        for s_ in meths:
            c.addMethod(CtNewMethod.make(s_, c))
        c.writeFile(hcls)

    PGE = "com.hypixel.hytale.server.core.entity.entities.player.pages"
    hclass("skyyexharness.Net", "com.hypixel.hytale.server.core.io.PacketHandler",
           "public Net() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
           ["public java.util.ArrayList sent;"],
           ["public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
            "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}",
            "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
            "public String getIdentifier() { return \"skyyexharness\"; }"])
    hclass("com.hypixel.hytale.component.SkyyExTestStore", "com.hypixel.hytale.component.Store",
           "public SkyyExTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
           "(com.hypixel.hytale.component.IResourceStorage) null); }",
           ["public java.util.IdentityHashMap comps;"],
           ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
            "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null || t == null) return null;\n"
            "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
            "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
    hclass("com.hypixel.hytale.component.SkyyExTestHolder", "com.hypixel.hytale.component.Holder", "public SkyyExTestHolder() { super(); }",
           ["public java.util.IdentityHashMap comps;"],
           ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.ComponentType t) {\n"
            "  if (this.comps == null) return null;\n  return (com.hypixel.hytale.component.Component) this.comps.get(t);\n}"])
    hclass("skyyexharness.World", "com.hypixel.hytale.server.core.universe.world.World",
           "public World() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }",
           ["public java.util.concurrent.ConcurrentLinkedQueue tasks;"],
           ["public void execute(java.lang.Runnable r) {\n  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
            "  this.tasks.add(r);\n}"])
    # an admin (hasPermission true) for the admin page flows
    hclass("skyyexharness.AdminRef", "com.hypixel.hytale.server.core.universe.PlayerRef", None, [],
           ["public boolean hasPermission(String n) { return true; }"])
    # a foreign page with the engine's empty onDismiss (another mod's page: ExGuard must leave it to SkyyMenu)
    hclass("skyyexharness.PlainPage", PGE + ".CustomUIPage",
           "public PlainPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, "
           "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime.CanDismiss); }", ["public int clicks;"],
           ["public void build(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b, "
            "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder e, com.hypixel.hytale.component.Store s) { "
            "b.appendInline((String) null, \"Group #SkyyPStandIn { Anchor: (Width: 100, Height: 100); }\"); "
            "e.addEventBinding(com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType.Activating, \"#SkyyPStandIn\", "
            "com.hypixel.hytale.server.core.ui.builder.EventData.of(\"m\", \"tile\")); }",
            "public void handleDataEvent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, String d) { "
            "this.clicks = this.clicks + 1; rebuild(); }"])
    # a scheduler that records what is scheduled (the flows run each step by hand, in the engine threads' order)
    hclass("skyyexharness.RecExec", "java.util.concurrent.ScheduledThreadPoolExecutor", "public RecExec() { super(1); }",
           ["public java.util.ArrayList tasks;", "public java.util.ArrayList delays;"],
           ["public java.util.concurrent.ScheduledFuture schedule(java.lang.Runnable r, long d, java.util.concurrent.TimeUnit u) {\n"
            "  if (this.tasks == null) { this.tasks = new java.util.ArrayList(); this.delays = new java.util.ArrayList(); }\n"
            "  this.tasks.add(r);\n  this.delays.add(Long.valueOf(u.toMillis(d)));\n  return null;\n}"])

    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Cls = JClass("java.lang.Class")
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    load_fails = []
    for n in names:
        try:
            Cls.forName(n, True, loader)
        except Exception as e:
            load_fails.append("%s: %s" % (n, e))
    R["load_fails"] = load_fails

    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    NET, TSC, THL, HW = (JClass("skyyexharness.Net"), JClass("com.hypixel.hytale.component.SkyyExTestStore"),
                         JClass("com.hypixel.hytale.component.SkyyExTestHolder"), JClass("skyyexharness.World"))
    ADMINREF, PLAIN, RECEXEC = JClass("skyyexharness.AdminRef"), JClass("skyyexharness.PlainPage"), JClass("skyyexharness.RecExec")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    STc = JClass("com.hypixel.hytale.component.Store")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    CPE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent")
    CPT = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType")
    PAGE_E = JClass("com.hypixel.hytale.protocol.packets.interface_.Page")
    PNONE = PAGE_E.None_
    ATW = JClass("com.hypixel.hytale.server.core.event.events.player.AddPlayerToWorldEvent")
    IdMap, CHM, UUID, Paths = (JClass("java.util.IdentityHashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.UUID"),
                               JClass("java.nio.file.Paths"))
    Cfg, Store_, Reg, Chest, Data = (JClass(PKG + n) for n in ("ExpCfg", "ExpStore", "SpotReg", "ChestReg", "ExpData"))
    ExPage, XaPage = JClass(PKG + "ExplorePage"), JClass(PKG + "AdminPage")
    Guard = JClass(PKG + "ExGuard") if NEW else None
    Watch = JClass(PKG + "ExWatch") if NEW else None

    base = os.path.join(SCRATCH, "pdata-" + tag)
    Reg.DIR = Paths.get(os.path.join(base, "worlds"), [])
    Store_.DIR = Paths.get(os.path.join(base, "players"), [])
    Chest.DIR = Paths.get(os.path.join(base, "chests"), [])
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"), [])
    nxt = [900]

    def ctype():
        c = CTc()
        nxt[0] += 1
        jf(CTc.class_, "index").setInt(c, nxt[0])
        jf(CTc.class_, "hashCode").setInt(c, nxt[0])
        return c

    CT_PR, CT_PLA = ctype(), ctype()
    uni = U.allocateInstance(Uni.class_)
    jf(Uni.class_, "playerRefComponentType").set(uni, CT_PR)
    WORLDS, PLAYERS = CHM(), CHM()
    jf(Uni.class_, "worldsByUuid").set(uni, WORLDS)
    jf(Uni.class_, "playersByUuid").set(uni, PLAYERS)
    jf(Uni.class_, "players").set(uni, PLAYERS.values())
    jf(Uni.class_, "instance").set(None, uni)
    em = U.allocateInstance(EMc.class_)
    jf(EMc.class_, "playerComponentType").set(em, CT_PLA)
    jf(EMc.class_, "instance").set(None, em)
    # the mod's log lines (ExpCfg.LOG -> one subscriber)
    HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
    RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(RECS)
    Cfg.LOG = HL.get("SkyyExHarness" + tag)

    def logs():
        out_ = []
        for i in range(int(RECS.size())):
            r = RECS.get(i)
            try:
                out_.append("%s %s" % (r.getLevel(), r.getMessage()))
            except Exception:
                out_.append(str(r))
        return [x for x in out_ if "[SkyyExploration]" in x]

    def world(name):
        w = U.allocateInstance(HW.class_)
        jf(WLDc.class_, "name").set(w, name)
        u = UUID.randomUUID()
        WORLDS.put(u, w)
        return w, u

    W1, W1U = world("skyworld")
    W2, W2U = world("hub")
    W3, W3U = world("zone1")
    REX = RECEXEC()
    if NEW:
        Guard.STOP = False
        Guard.EXEC = REX

    class Pl:
        pass

    def store_for(P, w):
        st = U.allocateInstance(TSC.class_)
        ref = U.allocateInstance(REFc.class_)
        jf(REFc.class_, "store").set(ref, st)
        jf(REFc.class_, "index").setInt(ref, 7)
        comps = IdMap()
        comps.put(CT_PR, P.pr)
        comps.put(CT_PLA, P.pl)
        allc = IdMap()
        allc.put(ref, comps)
        st.comps = allc
        es = U.allocateInstance(ESc.class_)
        jf(ESc.class_, "world").set(es, w)
        jf(STc.class_, "externalData").set(st, es)
        return ref, st

    nplayer = [0]

    def player(w=W1, wu=W1U, admin=False):
        """a stand-in player in world w: Store + Ref + PlayerRef + Player holding the engine's own PageManager / WindowManager"""
        P = Pl()
        nplayer[0] += 1
        u = UUID(0xe0e0, nplayer[0])
        P.u = u
        P.pr = U.allocateInstance((ADMINREF if admin else PR).class_)
        jf(PR.class_, "uuid").set(P.pr, u)
        jf(PR.class_, "username").set(P.pr, "SkyyHarness%d" % nplayer[0])
        P.net = U.allocateInstance(NET.class_)
        jf(PR.class_, "packetHandler").set(P.pr, P.net)
        jf(PR.class_, "worldUuid").set(P.pr, wu)
        P.pl = U.allocateInstance(PLAc.class_)
        P.wm = WMc()
        P.wm.init(P.pr)
        P.pm = PMc()
        P.pm.init(P.pr, P.wm)
        jf(PLAc.class_, "windowManager").set(P.pl, P.wm)
        jf(PLAc.class_, "pageManager").set(P.pl, P.pm)
        P.ref, P.st = store_for(P, w)
        jf(PR.class_, "entity").set(P.pr, P.ref)
        P.world = w
        PLAYERS.put(u, P.pr)
        d = Data()
        d.key = str(u)
        Store_.DATA.put(d.key, d)
        P.cl = Client(P)
        return P

    def acks(pm):
        return int(jf(PMc.class_, "customPageRequiredAcknowledgments").get(pm).get())

    def stray(pm):
        """+1 the client never acknowledges (what a page packet to a page the client no longer shows does)"""
        jf(PMc.class_, "customPageRequiredAcknowledgments").get(pm).incrementAndGet()

    def sent(net):
        return [] if net.sent is None else [net.sent.get(i) for i in range(int(net.sent.size()))]

    def kinds(ps):
        out_ = []
        for p in ps:
            k = str(p.getClass().getSimpleName())
            if k == "CustomPage":
                out_.append("CustomPage(%s%s)" % (str(p.key).rsplit(".", 1)[-1], ",clear" if bool(p.clear) else ""))
            elif k == "SetPage":
                out_.append("SetPage(%s)" % p.page)
            else:
                out_.append(k)
        return out_

    class Client:
        """the game client as far as the engine's acknowledgement rule needs it (inferred - the SkyyMenu 0.3.6 / SkyyBank 0.1.6 model)"""

        def __init__(s, P):
            s.P = P
            s.page, s.seen, s.waiting, s.binds, s.sets = None, 0, False, {}, {}

        def ack(s):
            s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Acknowledge, None))

        def pump(s):
            ps = sent(s.P.net)
            for p in ps[s.seen:]:
                kind = str(p.getClass().getSimpleName())
                if kind == "CustomPage":
                    if bool(p.isInitial) or (s.page is not None and str(p.key) == s.page):
                        s.page, s.waiting = str(p.key), False
                        if bool(p.clear) or bool(p.isInitial):
                            s.binds = dict((str(e.selector), (str(e.type), None if e.data is None else str(e.data), bool(e.locksInterface)))
                                           for e in p.eventBindings)
                            s.sets = {}
                        for c in (p.commands or []):
                            if str(c.type.name()) == "Set" and c.selector is not None:
                                s.sets[str(c.selector)] = None if c.data is None else str(c.data)
                        s.ack()
                elif kind == "SetPage":
                    if s.page is not None:
                        s.page, s.waiting = None, False
                        s.ack()
            s.seen = len(ps)

        def find(s, needle):
            for sel, b in s.binds.items():
                if b[1] and needle in b[1]:
                    return sel
            raise KeyError("no binding with %s in %s" % (needle, sorted(v[1] for v in s.binds.values())))

        def press(s, needle, extra=None):
            """click the binding whose EventData holds `needle`, as the client does; the client waits until a page packet comes"""
            sel = s.find(needle)
            d = json.loads(s.binds[sel][1])
            if extra:
                d.update(extra)
            s.waiting = True
            s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Data, json.dumps(d, separators=(",", ":"))))
            s.pump()
            return s.binds.get(sel, (None, None, None))[2]

        def raw(s, data):
            s.waiting = True
            s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Data, data))
            s.pump()

        def esc(s):
            if s.page is not None:
                s.page, s.waiting = None, False
                s.P.pm.handleEvent(s.P.ref, s.P.st, CPE(CPT.Dismiss, None))

    def leave(P, w, wu, event=True):
        """the first half of a world change in the engine's order: PlayerRef.removeFromStore (the old ref invalid, the holder kept), then
        World.addPlayer = the new world id + AddPlayerToWorldEvent (0.2.3: the registered ExGuard listener runs here)"""
        jf(REFc.class_, "index").setInt(P.ref, -2147483648)
        jf(PR.class_, "entity").set(P.pr, None)
        h = U.allocateInstance(THL.class_)
        hc = IdMap()
        hc.put(CT_PR, P.pr)
        hc.put(CT_PLA, P.pl)
        h.comps = hc
        jf(PR.class_, "holder").set(P.pr, h)
        jf(PR.class_, "worldUuid").set(P.pr, wu)
        P.ev_counter, P.ev_sent = acks(P.pm), len(sent(P.net))
        if NEW and event:
            Guard().accept(ATW(h, w, None))
        P.ev_after, P.ev_sent_after, P.ev_page = acks(P.pm), len(sent(P.net)), P.pm.getCustomPage()

    def arrive(P, w):
        """the second half: onSetupPlayerJoining (clearCustomPageAcknowledgements; the client's JoinWorld drops its page), then
        onFinishPlayerJoining (addToStore: a new ref in the new world's store)"""
        P.pm.clearCustomPageAcknowledgements()
        P.cl.page, P.cl.waiting = None, False
        P.ref, P.st = store_for(P, w)
        jf(PR.class_, "entity").set(P.pr, P.ref)
        jf(PR.class_, "holder").set(P.pr, None)
        P.world = w

    def world_change(P, w, wu, event=True):
        leave(P, w, wu, event)
        arrive(P, w)

    def run_world(w):
        n = 0
        while w.tasks is not None and not w.tasks.isEmpty():
            w.tasks.poll().run()
            n += 1
        return n

    def drain_exec():
        if REX.tasks is not None:
            REX.tasks.clear()
            REX.delays.clear()

    def open_page(P, pg):
        P.pm.openCustomPage(P.ref, P.st, pg)
        P.cl.pump()
        return pg

    def age(pg):
        """the page's last build (and send) is older than the 1 s guard / SETTLE"""
        pg.lastBuild = pg.lastBuild - 5000
        if NEW:
            pg.lastSend = pg.lastSend - 5000

    def run_checks(pg):
        """run the page's checks the scheduler holds (ExWatch: scheduler hop -> World.execute -> watchTick), one round"""
        if REX.tasks is None:
            return 0
        ts = [REX.tasks.get(i) for i in range(int(REX.tasks.size()))]
        drain_exec()
        n = 0
        for t in ts:
            if t.page != pg:
                continue
            t.run()
            n += 1
        for w in (W1, W2, W3):
            run_world(w)
        return n

    def checks_for(pg):
        if REX.tasks is None:
            return 0
        return sum(1 for i in range(int(REX.tasks.size())) if REX.tasks.get(i).page == pg)

    for w in (W1, W2, W3):
        if w.tasks is not None:
            w.tasks.clear()
    msg_sel = "#SkyyExMsg.Text"

    # ---- P1 SKYY'S REPORT: Zones, then Overview within 1 s (same world)
    P = player()
    pg = open_page(P, ExPage(P.pr, 0))
    R["p1_open"] = [P.cl.page is not None and P.cl.page.endswith("ExplorePage"), acks(P.pm)]
    age(pg)
    locks = P.cl.press("extab1")
    R["p1_zones"] = [int(pg.tab), P.cl.waiting, acks(P.pm), bool(locks)]
    n0 = len(sent(P.net))
    P.cl.press("extab0")                                   # within 1 s of the Zones build
    R["p1_overview"] = [int(pg.tab), P.cl.waiting, acks(P.pm), kinds(sent(P.net)[n0:])]
    # 0.2.2: the page is stuck on "Loading..."; a re-opened /explore works (Skyy: "/explore worked")
    pg2 = open_page(P, ExPage(P.pr, 0))
    age(pg2)
    P.cl.press("extab1")
    R["p1_reopen"] = [int(pg2.tab), P.cl.waiting, acks(P.pm)]
    # a title click within 1 s: not acted on; answered on 0.2.3
    age(pg2)
    P.cl.press("extab2")
    msg_before = str(pg2.msg)
    n0 = len(sent(P.net))
    P.cl.press("exnone")
    R["p1_title_quick"] = [str(pg2.msg) == msg_before, P.cl.waiting, kinds(sent(P.net)[n0:]), P.cl.sets.get(msg_sel), acks(P.pm)]
    age(pg2)
    P.cl.press("exnone")
    R["p1_title_late"] = [str(pg2.msg), P.cl.waiting, acks(P.pm)]
    # an unknown / malformed click on the page (a stale binding): 0.2.2 silent, 0.2.3 answered
    age(pg2)
    P.cl.raw('{"a":"exnosuchbutton"}')
    R["p1_unknown"] = [P.cl.waiting, acks(P.pm)]
    P.cl.esc()
    drain_exec()

    # ---- P2 a page left open across a world change + a page close on the new world (no SkyyMenu)
    P = player()
    pg = open_page(P, ExPage(P.pr, 0))
    world_change(P, W2, W2U)
    R["p2_event"] = [P.ev_page is None, P.ev_counter, P.ev_after, P.ev_sent_after - P.ev_sent]
    n0 = len(sent(P.net))
    P.pm.setPage(P.ref, P.st, PNONE)                # a bench / another mod's setPage(None) on the new world
    P.cl.pump()
    R["p2_close"] = [kinds(sent(P.net)[n0:]), acks(P.pm)]
    pg2 = open_page(P, ExPage(P.pr, 0))                     # /explore again, same world
    age(pg2)
    P.cl.press("extab1")
    R["p2_reopen"] = [int(pg2.tab), P.cl.waiting, acks(P.pm)]
    P.cl.esc()
    drain_exec()

    # ---- P3 the safety net: a stray +1 while the page is open
    P = player()
    pg = open_page(P, ExPage(P.pr, 0))
    R["p3_scheduled"] = checks_for(pg)
    age(pg)
    stray(P.pm)
    P.cl.press("extab1")
    R["p3_dropped"] = [int(pg.tab), P.cl.waiting, acks(P.pm)]
    w0 = len([x for x in logs() if x.startswith("WARNING")])
    n0 = len(sent(P.net))
    ran = run_checks(pg) if NEW else 0
    P.cl.pump()
    R["p3_heal"] = [ran, kinds(sent(P.net)[n0:]), acks(P.pm), P.cl.waiting, str(pg.msg) if NEW else None,
                    len([x for x in logs() if x.startswith("WARNING")]) - w0, checks_for(pg)]
    age(pg)
    P.cl.press("extab1")
    R["p3_next"] = [int(pg.tab), P.cl.waiting, acks(P.pm)]
    # at most HEAL_ANSWERS answers per page: 5 more stray counts, each healed; answers stop after 3
    answers = []
    for _ in range(5):
        stray(P.pm)
        age(pg)
        n0 = len(sent(P.net))
        if NEW:
            run_checks(pg)
        P.cl.pump()
        answers.append([len(sent(P.net)) - n0, acks(P.pm)])
    R["p3_more"] = [answers, int(pg.heals) if NEW else None]
    P.cl.esc()
    drain_exec()

    # ---- P4 a healthy page: the check sends nothing and acts on nothing
    P = player()
    pg = open_page(P, ExPage(P.pr, 2))
    age(pg)
    n0 = len(sent(P.net))
    ran = run_checks(pg) if NEW else 0
    R["p4_healthy"] = [ran, len(sent(P.net)) - n0, int(pg.tab), str(pg.msg), int(pg.heals) if NEW else None, checks_for(pg), acks(P.pm)]
    P.cl.esc()
    ran = run_checks(pg) if NEW else 0
    R["p4_after_esc"] = [ran, checks_for(pg)]          # the check ends once the page is closed
    drain_exec()

    # ---- P5 a world change WITHOUT the event: the check forgets the page on the new world (no packet)
    P = player()
    pg = open_page(P, ExPage(P.pr, 0))
    world_change(P, W3, W3U, event=False)
    n0 = len(sent(P.net))
    ran = run_checks(pg) if NEW else 0
    R["p5_forget"] = [ran, P.pm.getCustomPage() is None, len(sent(P.net)) - n0, acks(P.pm), checks_for(pg)]
    n0 = len(sent(P.net))
    P.pm.setPage(P.ref, P.st, PNONE)
    R["p5_close_after"] = [kinds(sent(P.net)[n0:]), acks(P.pm)]
    drain_exec()

    # ---- P6 ExGuard at the world join: Exploration pages forgotten, a foreign page left alone, joins counted
    P = player()
    j0 = int(Guard.joins(P.u)) if NEW else 0
    open_page(P, PLAIN(P.pr))
    world_change(P, W2, W2U)
    R["p6_foreign"] = [P.ev_page is not None and str(P.ev_page.getClass().getName()) == "skyyexharness.PlainPage", P.ev_sent_after - P.ev_sent]
    A = player(admin=True)
    open_page(A, XaPage(A.pr, 0))
    world_change(A, W2, W2U)
    R["p6_admin"] = [A.ev_page is None, A.ev_counter, A.ev_after, A.ev_sent_after - A.ev_sent]
    R["p6_joins"] = [j0, int(Guard.joins(P.u)) if NEW else 0, int(Guard.FORGOT) if NEW else 0]
    drain_exec()

    # ---- P7 no answer to a closed page
    P = player()
    pg = open_page(P, ExPage(P.pr, 0))
    P.cl.esc()
    n0 = len(sent(P.net))
    if NEW:
        pg.answer()
    R["p7_closed"] = [len(sent(P.net)) - n0, acks(P.pm)]
    drain_exec()

    # ---- P8 the admin page: a quick tab acts, other quick clicks are answered without acting; unknown click answered; Teleport
    A = player(admin=True)
    ap = open_page(A, XaPage(A.pr, 0))
    age(ap)
    A.cl.press("xtab1")
    n0 = len(sent(A.net))
    A.cl.press("xtab2")                                   # quick tab
    R["p8_tab"] = [int(ap.tab), A.cl.waiting, kinds(sent(A.net)[n0:])]
    n0 = len(sent(A.net))
    A.cl.press("xrefresh")                                # quick non-tab click
    R["p8_quick"] = [int(ap.tab), A.cl.waiting, kinds(sent(A.net)[n0:]), acks(A.pm)]
    age(ap)
    A.cl.raw('{"a":"xnosuchthing"}')
    R["p8_unknown"] = [A.cl.waiting, acks(A.pm)]
    age(ap)
    A.cl.raw('{"a":""}')
    R["p8_empty"] = [A.cl.waiting, acks(A.pm)]
    # Teleport with no spot selected: refused (a "-" result) -> answered by the redraw on both jars
    age(ap)
    A.cl.raw('{"a":"xtp"}')
    R["p8_tp_refused"] = [A.cl.waiting, str(ap.msg)[:1]]
    A.cl.esc()
    drain_exec()

    # ---- P9 the real timer chain (0.2.3): a real single-thread scheduled executor, as HytaleServer.SCHEDULED_EXECUTOR
    if NEW:
        EX = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()
        Guard.EXEC = EX
        P = player()
        pg = open_page(P, ExPage(P.pr, 0))
        stray(P.pm)
        pg.lastSend = pg.lastSend - 5000
        t0 = time.time()
        got = 0
        while time.time() - t0 < 6 and got == 0:
            time.sleep(0.2)
            got = run_world(W1)
        P.cl.pump()
        R["p9_real"] = [got, acks(P.pm), int(pg.heals), round(time.time() - t0, 1)]
        Guard.STOP = True
        EX.shutdownNow()
        Guard.EXEC = REX
        Guard.STOP = False
    R["logs"] = logs()
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--run" in sys.argv:
        H.run_states(arg("--run"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        H.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--pages" in sys.argv:
        run_pages(arg("--pages"), arg("--tag"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM (states) for %s ran" % j)
        outs["p" + tag] = os.path.join(SCRATCH, "pages-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--pages", j, "--tag", tag, "--out", outs["p" + tag], "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs["p" + tag]), "child JVM (page flows) for %s ran" % j)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if FAILS:
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    # B-D: every page state identical; the 0.2.2 harness's C / D checks on them
    import skyyui as SUI
    SUI.verify(quiet=True)
    same = 0
    for key, states, prefix, pw, ph, body in (("ex", H.EX_STATES, "SkyyEx", H.EX_W, H.EX_H, "SkyyExRoot"),
                                              ("xa", H.XA_STATES, "SkyyXa", H.XA_W, H.XA_H, "SkyyXaRoot")):
        counts = dict(states=0, bindings=0, ids=0, new_ids=0, sets=0, new_sets=0, inline=0, placeholders=0, colours=0, check_page=0,
                      proven=0, appends=0, fills=0, body_exact=0, columns=0, rows=0, min_row_slack=10 ** 6, clipped=0, maxlen=0,
                      enums=0, text_fit=0, wrap_fit=0, unmeasured=0, min_text_slack=10 ** 6)
        for st in states:
            o, n = old[key].get(st), new[key].get(st)
            check(o is not None and n is not None, "B: %s state %s built by both jars" % (key, st))
            if o is None or n is None:
                continue
            check(o["error"] is None and n["error"] is None and o["commands"] == n["commands"] and o["events"] == n["events"],
                  "B: %s/%s: 0.2.3 sends exactly 0.2.2's page (commands + bindings)" % (key, st))
            same += 1
            H.compare_state("%s/%s" % (key, st), o, n, SUI, counts, prefix, pw, ph, body, False)
        print("B-D %s: %d states identical to 0.2.2; %d bindings, %d b.set values, %d appends through check_markup, %d check_page, "
              "%d assert_proven, %d one-line + %d wrapped texts fit" % ("ExplorePage" if key == "ex" else "AdminPage", counts["states"],
                                                                       counts["bindings"], counts["sets"], counts["appends"],
                                                                       counts["check_page"], counts["proven"], counts["text_fit"],
                                                                       counts["wrap_fit"]))
    # E
    check(new.get("msg") == old.get("msg") and new.get("st") == old.get("st") and new.get("msg") and new.get("st"),
          "E: msgColor / stColor answer exactly as 0.2.2")
    print("E. msgColor on %d texts, stColor on %d marks: as 0.2.2" % (len(new.get("msg") or []), len(new.get("st") or [])))
    # F
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    added = sorted(set(zn.namelist()) - set(zo.namelist()))
    check(added == ["com/skyy/explore/ExGuard.class", "com/skyy/explore/ExWatch.class"] and not set(zo.namelist()) - set(zn.namelist()),
          "F: new entries = ExGuard + ExWatch only, none gone: %s" % added)
    diff = sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    bc = json.load(open(bco))
    EP, XP, PL = "com/skyy/explore/ExplorePage.class", "com/skyy/explore/AdminPage.class", "com/skyy/explore/SkyyExplorationPlugin.class"
    vonly = sorted(n for n in diff if n in bc and bc[n].get("version_only") and not bc[n]["new"] and not bc[n]["gone"] and bc[n]["fields_same"])
    rest = sorted(set(diff) - set(vonly) - {EP, XP, PL, "manifest.json"})
    check(not rest and {EP, XP, PL} <= set(diff), "F: only the pages, the plugin, manifest.json and version-string classes differ: %s" % rest)
    B_SIG = "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;" \
            "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V"
    H_SIG = "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V"
    FIELDS = sorted(["world Lcom/hypixel/hytale/server/core/universe/world/World;", "joinSeen I", "lastSend J", "watching Z",
                     "probeNonce Ljava/lang/String;", "probeSeen Z", "heals I", "SETTLE J", "HEAL_ANSWERS I"])
    for n_, nm in ((EP, "ExplorePage"), (XP, "AdminPage")):
        c = bc.get(n_, {})
        check(sorted(c.get("changed", [])) == sorted(["build" + B_SIG, "handleDataEvent" + H_SIG]) and not c.get("gone")
              and sorted(m.split("(")[0] for m in c.get("new", [])) == ["answer", "changedWorld", "isOpen", "watchTick"]
              and sorted(c.get("fields_new", [])) == FIELDS and not c.get("fields_gone"),
              "F: %s: only build + handleDataEvent changed, answer / changedWorld / isOpen / watchTick + the guard fields new: %s"
              % (nm, dict((x, c.get(x)) for x in ("changed", "new", "gone", "fields_new", "fields_gone"))))
    c = bc.get(PL, {})
    check(sorted(c.get("changed", [])) == ["setup()V", "shutdown()V"] and not c.get("new") and not c.get("gone") and c.get("fields_same"),
          "F: SkyyExplorationPlugin: only setup / shutdown changed: %s" % c)
    print("F. %d entries identical; differ: %s; version string only: %s; new: %s" % (
        len(set(zo.namelist()) & set(zn.namelist())) - len(diff), ", ".join(x.split("/")[-1] for x in sorted(set(diff) - set(vonly))),
        ", ".join(x.split("/")[-1][:-6] for x in vonly), ", ".join(x.split("/")[-1][:-6] for x in added)))
    # P
    po, pn = json.load(open(outs["pold"])), json.load(open(outs["pnew"]))
    for r in (po, pn):
        check(not r["load_fails"], "P: %s classes load in the flows JVM: %s" % (r["tag"], r["load_fails"]))
    for r, v in ((po, OLD_VERSION), (pn, VERSION)):
        check(r["p1_open"] == [True, 0] and r["p1_zones"][:3] == [1, False, 0],
              "P1 %s: /explore opens, Zones answers (%s %s)" % (v, r["p1_open"], r["p1_zones"]))
    check(po["p1_overview"] == [1, True, 0, []], "P1 0.2.2 REPRODUCES SKYY'S REPORT: Overview within 1 s of the Zones build is dropped "
          "silently - no packet, the client stays on 'Loading...', 0 acknowledgements pending (not the engine's counter): %s" % po["p1_overview"])
    check(po["p1_reopen"] == [1, False, 0], "P1 0.2.2: a re-opened /explore works again (Skyy: '/explore worked'): %s" % po["p1_reopen"])
    check(pn["p1_overview"][:3] == [0, False, 0] and pn["p1_overview"][3] == ["CustomPage(ExplorePage,clear)"],
          "P1 0.2.3: Overview within 1 s shows at once (one redraw, acknowledged): %s" % pn["p1_overview"])
    check(po["p1_title_quick"][:3] == [True, True, []], "P1 0.2.2: a title click within 1 s is dropped silently: %s" % po["p1_title_quick"])
    check(pn["p1_title_quick"][0] is True and pn["p1_title_quick"][1] is False and pn["p1_title_quick"][2] == ["CustomPage(ExplorePage)"]
          and pn["p1_title_quick"][4] == 0, "P1 0.2.3: a title click within 1 s is answered (one short update) WITHOUT acting: %s" % pn["p1_title_quick"])
    check(po["p1_title_late"][1:] == [False, 0] and pn["p1_title_late"] == po["p1_title_late"],
          "P1: after 1 s the title click acts on both jars, the same result (%s / %s)" % (po["p1_title_late"], pn["p1_title_late"]))
    check(po["p1_unknown"] == [True, 0] and pn["p1_unknown"] == [False, 0],
          "P1: an unknown click: 0.2.2 silent (%s), 0.2.3 answered (%s)" % (po["p1_unknown"], pn["p1_unknown"]))
    check(po["p2_event"][0] is False and po["p2_close"] == [["SetPage(None)"], 1] and po["p2_reopen"] == [0, True, 1],
          "P2 0.2.2 REPRODUCES THE STUCK COUNTER: the page left open across the world change, a page close on the new world = 1 "
          "acknowledgement the client never sends, the re-opened /explore drops the Zones click (%s %s %s)" % (po["p2_event"], po["p2_close"], po["p2_reopen"]))
    check(pn["p2_event"] == [True, 0, 0, 0] and pn["p2_close"] == [["SetPage(None)"], 0] and pn["p2_reopen"] == [1, False, 0],
          "P2 0.2.3: ExGuard forgot the page AT the world join (no packet, counter untouched), the close adds nothing, 0 pending, the "
          "re-opened page works (%s %s %s)" % (pn["p2_event"], pn["p2_close"], pn["p2_reopen"]))
    check(po["p3_dropped"] == [0, True, 1] and pn["p3_dropped"] == [0, True, 1], "P3: a stray +1 drops the next click on both jars")
    check(po["p3_scheduled"] == 0 and pn["p3_scheduled"] == 1, "P3: the first build of a 0.2.3 page schedules its check (0.2.2: none)")
    check(po["p3_next"] == [0, True, 1], "P3 0.2.2: no safety net - every click stays dropped: %s" % po["p3_next"])
    hl = pn["p3_heal"]
    check(hl[0] == 1 and hl[1] == ["CustomPage(ExplorePage,clear)"] and hl[2] == 0 and hl[3] is False and hl[4].startswith("Clicks were stuck")
          and hl[5] == 1 and hl[6] == 1, "P3 0.2.3: the check healed - one WARNING, counter reset, the page answered with the heal line, "
          "the client stops waiting, the check runs on: %s" % hl)
    check(pn["p3_next"] == [1, False, 0], "P3 0.2.3: the next click works: %s" % pn["p3_next"])
    ans = pn["p3_more"]
    check([a[0] for a in ans[0]] == [1, 1, 0, 0, 0] and all(a[1] == 0 for a in ans[0]) and ans[1] == 6,
          "P3 0.2.3: at most 3 heal answers per page (later heals reset silently): %s" % ans)
    check(pn["p4_healthy"][:2] == [1, 0] and pn["p4_healthy"][2:5] == [2, "", 0] and pn["p4_healthy"][5:] == [1, 0],
          "P4 0.2.3: a healthy page - the check sends nothing, acts on nothing, runs on: %s" % pn["p4_healthy"])
    check(pn["p4_after_esc"] == [1, 0], "P4 0.2.3: the check ends after Esc: %s" % pn["p4_after_esc"])
    check(pn["p5_forget"] == [1, True, 0, 0, 0] and pn["p5_close_after"] == [["SetPage(None)"], 0],
          "P5 0.2.3: without the event the check forgets the page on the new world (no packet), a later close adds nothing: %s %s"
          % (pn["p5_forget"], pn["p5_close_after"]))
    check(po["p5_close_after"] == [["SetPage(None)"], 1], "P5 0.2.2: the same path leaves 1 pending: %s" % po["p5_close_after"])
    check(pn["p6_foreign"] == [True, 0] and pn["p6_admin"] == [True, 0, 0, 0] and pn["p6_joins"][1] == pn["p6_joins"][0] + 1,
          "P6 0.2.3: ExGuard leaves a foreign page to SkyyMenu, forgets the admin page at the event, counts the join: %s %s %s"
          % (pn["p6_foreign"], pn["p6_admin"], pn["p6_joins"]))
    check(pn["p7_closed"] == [0, 0], "P7 0.2.3: no answer to a closed page: %s" % pn["p7_closed"])
    check(po["p8_tab"][0] == 1 and po["p8_tab"][1] is True and pn["p8_tab"] == [2, False, ["CustomPage(AdminPage,clear)"]],
          "P8: a quick admin tab - 0.2.2 dropped (%s), 0.2.3 acts (%s)" % (po["p8_tab"], pn["p8_tab"]))
    check(pn["p8_quick"] == [2, False, ["CustomPage(AdminPage)"], 0] and po["p8_quick"][1] is True,
          "P8: a quick admin click - 0.2.3 answered without acting (%s), 0.2.2 silent (%s)" % (pn["p8_quick"], po["p8_quick"]))
    check(pn["p8_unknown"] == [False, 0] and po["p8_unknown"] == [True, 0] and pn["p8_empty"] == [False, 0] and po["p8_empty"] == [True, 0],
          "P8: unknown / empty admin clicks - 0.2.3 answered, 0.2.2 silent (%s %s / %s %s)" % (pn["p8_unknown"], pn["p8_empty"], po["p8_unknown"], po["p8_empty"]))
    check(pn["p8_tp_refused"] == [False, "-"] and po["p8_tp_refused"] == [False, "-"], "P8: a refused Teleport is answered on both jars")
    check(pn.get("p9_real", [0])[0] >= 1 and pn["p9_real"][1] == 0 and pn["p9_real"][2] == 1,
          "P9 0.2.3: the real timer chain (scheduler thread -> World.execute -> watchTick) heals within ~1 s: %s" % pn.get("p9_real"))
    warn_lines = [x for x in pn["logs"] if x.startswith("WARNING")]
    check(all("dropping" in x for x in warn_lines), "P: 0.2.3 logs no WARNING but the heal lines: %s" % warn_lines)
    print("P. page flows on the engine PageManager: 0.2.2 reproduces both ways ('Loading...' after a quick click: no packet, 0 pending; "
          "the stuck counter after a world change: 1 pending); 0.2.3 answers every click, forgets stale pages at the join, heals (%d WARNING "
          "lines, all heals); P9 real timer heal after %ss" % (len(warn_lines), pn.get("p9_real", [0, 0, 0, "?"])[3]))
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyExploration %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
