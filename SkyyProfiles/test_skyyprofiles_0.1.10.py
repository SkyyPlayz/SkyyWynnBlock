"""SkyyProfiles 0.1.10 - bare-JVM harness for THE HYTALE 0.7.0 PORT (tools/profiles_0_1_10_patch.py). Child JVM: the game's own JRE, the
0.7.0 HytaleServer.jar, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The live Skyy_SkyyProfiles folder
is only READ (copied into scratch) and checked afterwards.

    python SkyyProfiles/test_skyyprofiles_0.1.10.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyProfiles-0.1.10.jar] [--prev SkyyProfiles-0.1.9.jar]

SECTIONS
  CC  CLASS COMPARE 0.1.9 -> 0.1.10: + exactly ProfSpawnTask; structural changes only ProfSwitch.travel; the rest = version constants
  JT  jar entries: 0.1.9's classes + ProfSpawnTask; every non-class entry byte-identical but the manifest (version)
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7.0 engine
  T   ProfSwitch.travel EXECUTED (the fallback after a profile switch when /island cannot be resolved = SkyyIslands missing):
        T1 a provider that answers at once (vanilla GlobalSpawnProvider): ONE ProfSpawnTask queued on the player's world (World.execute),
           no teleport before it runs; it runs -> Teleport to the main world at its spawn point + the 0.1.9 chat line
        T2 an ASYNC provider finished later on ANOTHER thread: nothing queued until then; that thread queues the task; it teleports
        T3 the player left that world before the answer -> nothing        T4 a teleport already pending -> nothing (0.1.9's guard)
        T5 no spawn point (null) -> nothing        T6 the future fails -> the 0.1.9 warning "fallback teleport after a switch failed"
        T7 /island resolvable -> /island is run, no spawn point asked        T8 islandOnSwitch off -> nothing at all
        T9 CONTROL: 0.1.9's travel on 0.7.0 -> its catch logs "fallback teleport after a switch failed: java.lang.NoSuchMethodError"
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyProfiles (setup()'s data steps: upgradeDefault, capMigrate, load, the data
      folders, scanIndex, the bridge, the config kit): no file changed by either start
  AA  python tools/ci/crosscheck.py --jar <0.1.10> --baseline: no FAIL for SkyyProfiles on 0.7.0, the command tree identical to 0.1.9
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.1.10", "0.1.9"
PKG = "com.skyy.profiles."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pages07", "profiles")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyProfiles-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyProfiles")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")     # the shared JVM helpers (read only)
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def sk():
    spec = importlib.util.spec_from_file_location("ts0427", SKILLS_HARNESS)
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


# ============================================================================================ the 0.7.0 engine stand-ins (shared shape)
def engine(S, B, hcls, tag):
    """packet sink, component store (getComponent / addComponent), worlds with a task queue, a Universe whose default world is set,
    an async spawn provider, a CommandManager; the Universe / EntityModule singletons pointed at them. Returns a namespace dict."""
    from jpype import JClass, JArray, JString
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    HP = JClass("javassist.ClassPool")(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
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
    PH = "com.hypixel.hytale."
    T = tag
    hclass(T + ".Net", PH + "server.core.io.PacketHandler",
           "public Net() { super((" + PH + "protocol.io.ChannelConnection) null, (" + PH + "server.core.io.ProtocolVersion) null); }",
           ["public java.util.ArrayList sent;"],
           ["public void rec(Object p) { if (this.sent == null) this.sent = new java.util.ArrayList(); this.sent.add(p); }",
            "public boolean writePacket(" + PH + "protocol.ToClientPacket p, boolean c) { rec(p); return true; }",
            "public void write(" + PH + "protocol.ToClientPacket p) { rec(p); }",
            "public void write(" + PH + "protocol.ToClientPacket[] ps) { for (int i = 0; i < ps.length; i++) rec(ps[i]); }",
            "public void write(" + PH + "protocol.ToClientPacket[] ps, " + PH + "protocol.ToClientPacket p) { for (int i = 0; i < ps.length; i++) rec(ps[i]); rec(p); }",
            "public void writeNoCache(" + PH + "protocol.ToClientPacket p) { rec(p); }",
            "public void accept(" + PH + "protocol.ToServerPacket p) { }",
            "public String getIdentifier() { return \"" + T + "\"; }"])
    hclass(PH + "component." + T.capitalize() + "Store", PH + "component.Store",
           "public " + T.capitalize() + "Store() { super((" + PH + "component.ComponentRegistry) null, 0, (Object) null, (" + PH + "component.IResourceStorage) null); }",
           ["public java.util.IdentityHashMap comps;", "public java.util.ArrayList added;"],
           ["public java.util.Map row(" + PH + "component.Ref r) {\n"
            "  if (this.comps == null) this.comps = new java.util.IdentityHashMap();\n"
            "  java.util.Map m = (java.util.Map) this.comps.get(r);\n"
            "  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }\n  return m;\n}",
            "public " + PH + "component.Component getComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t) {\n"
            "  return (" + PH + "component.Component) row(r).get(t);\n}",
            "public void addComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t, " + PH + "component.Component c) {\n"
            "  if (this.added == null) this.added = new java.util.ArrayList();\n  this.added.add(c);\n  row(r).put(t, c);\n}"])
    hclass(T + ".World", PH + "server.core.universe.world.World",
           "public World() { super((String) null, (java.nio.file.Path) null, (" + PH + "server.core.universe.world.WorldConfig) null); }",
           ["public java.util.concurrent.ConcurrentLinkedQueue tasks;", "public java.util.ArrayList by;"],
           ["public void execute(java.lang.Runnable r) {\n"
            "  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
            "  if (this.by == null) this.by = new java.util.ArrayList();\n"
            "  this.tasks.add(r);\n  synchronized (this.by) { this.by.add(Thread.currentThread().getName()); }\n}"])
    hclass(T + ".Uni", PH + "server.core.universe.Universe", "public Uni() { super((" + PH + "server.core.plugin.JavaPluginInit) null); }",
           ["public static " + PH + "server.core.universe.world.World DEF;"],
           ["public " + PH + "server.core.universe.world.World getDefaultWorld() { return DEF; }"])
    hclass(T + ".LaterSpawn", None, "public LaterSpawn() { }",
           ["public java.util.concurrent.CompletableFuture f;", "public int asked;"],
           ["public java.util.concurrent.CompletableFuture getSpawnPointAsync(" + PH + "server.core.universe.world.World w, java.util.UUID u) {\n"
            "  this.asked = this.asked + 1;\n  this.f = new java.util.concurrent.CompletableFuture();\n  return this.f;\n}",
            "public " + PH + "math.vector.Transform[] getSpawnPoints() { return new " + PH + "math.vector.Transform[] { new " + PH + "math.vector.Transform(7.0, 77.0, 7.0) }; }",
            "public boolean isWithinSpawnDistance(org.joml.Vector3d p, double d) { return false; }"],
           [PH + "server.core.universe.world.spawn.ISpawnProvider"])
    hclass(T + ".Finish", None, "public Finish(java.util.concurrent.CompletableFuture f, Object v, Throwable e) { this.f = f; this.v = v; this.e = e; }",
           ["public java.util.concurrent.CompletableFuture f;", "public Object v;", "public Throwable e;"],
           ["public void run() { if (this.e != null) this.f.completeExceptionally(this.e); else this.f.complete(this.v); }"], ["java.lang.Runnable"])
    hclass(T + ".Cmd", PH + "server.core.command.system.AbstractCommand", "public Cmd() { super(\"x\", \"y\"); }", [],
           ["public boolean hasPermission(" + PH + "server.core.command.system.CommandSender s) { return true; }",
            "protected java.util.concurrent.CompletableFuture execute(" + PH + "server.core.command.system.CommandContext c) { return null; }"])
    hclass(T + ".Cmds", PH + "server.core.command.system.CommandManager", "public Cmds() { super(); }",
           ["public java.util.HashMap cmds;", "public java.util.ArrayList lines;"],
           ["public " + PH + "server.core.command.system.AbstractCommand resolveCommand(String n) {\n"
            "  return this.cmds == null ? null : (" + PH + "server.core.command.system.AbstractCommand) this.cmds.get(n);\n}",
            "public java.util.concurrent.CompletableFuture handleCommand(" + PH + "server.core.command.system.CommandSender s, String line) {\n"
            "  if (this.lines == null) this.lines = new java.util.ArrayList();\n  this.lines.add(line);\n"
            "  return new java.util.concurrent.CompletableFuture();\n}"])
    UUID, ArrayList, HashMap = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.util.HashMap")
    JClass(PH + "server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HSV = JClass(PH + "server.core.HytaleServer")
    hs = U.allocateInstance(HSV.class_)
    jf(HSV.class_, "eventBus").set(hs, JClass(PH + "event.EventBus")(False))
    jf(HSV.class_, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
    jf(HSV.class_, "instance").set(None, hs)
    JClass(PH + "server.core.asset.AssetRegistryLoader").init()      # WorldConfig's codecs ask the store registry while they initialise
    CTc = JClass(PH + "component.ComponentType")
    nxt = [700]

    def ctype():
        c = CTc()
        nxt[0] += 1
        jf(CTc.class_, "index").setInt(c, nxt[0])
        jf(CTc.class_, "hashCode").setInt(c, nxt[0])
        return c
    CT = dict((k, ctype()) for k in ("pr", "pla", "tp", "tc", "hr"))
    UniC, UniH = JClass(PH + "server.core.universe.Universe"), JClass(T + ".Uni")
    uni = U.allocateInstance(UniH.class_)
    jf(UniC.class_, "playerRefComponentType").set(uni, CT["pr"])
    WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
    jf(UniC.class_, "worldsByUuid").set(uni, WORLDS)
    jf(UniC.class_, "worlds").set(uni, JClass("java.util.concurrent.ConcurrentHashMap")())
    jf(UniC.class_, "players").set(uni, ArrayList())
    jf(UniC.class_, "playersByUuid").set(uni, JClass("java.util.concurrent.ConcurrentHashMap")())
    jf(UniC.class_, "instance").set(None, uni)
    EMc = JClass(PH + "server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EMc.class_)
    for fn_, k_ in (("playerComponentType", "pla"), ("teleportComponentType", "tp"), ("transformComponentType", "tc"), ("headRotationComponentType", "hr")):
        jf(EMc.class_, fn_).set(em, CT[k_])
    jf(EMc.class_, "instance").set(None, em)
    WCFG = JClass(PH + "server.core.universe.world.WorldConfig")
    WLDc = JClass(PH + "server.core.universe.world.World")

    def mkworld(name):
        w = U.allocateInstance(JClass(T + ".World").class_)
        wu = UUID.randomUUID()
        jf(WLDc.class_, "name").set(w, name)
        cfg = U.allocateInstance(WCFG.class_)
        jf(WLDc.class_, "worldConfig").set(w, cfg)
        WORLDS.put(wu, w)
        return w, wu, cfg
    CM = U.allocateInstance(JClass(T + ".Cmds").class_)
    CM.cmds = HashMap()
    CM.lines = ArrayList()
    jf(JClass(PH + "server.core.command.system.CommandManager").class_, "instance").set(None, CM)
    PR = JClass(PH + "server.core.universe.PlayerRef")
    REFc = JClass(PH + "component.Ref")
    ESc = JClass(PH + "server.core.universe.world.storage.EntityStore")
    STc = JClass(PH + "component.Store")
    TPc = JClass(PH + "server.core.modules.entity.teleport.Teleport")

    class Pl:
        pass

    def player(uid, world, world_u):
        P = Pl()
        P.pr = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(P.pr, uid)
        jf(PR.class_, "username").set(P.pr, "SkyyHarness")
        P.net = U.allocateInstance(JClass(T + ".Net").class_)
        jf(PR.class_, "packetHandler").set(P.pr, P.net)
        jf(PR.class_, "worldUuid").set(P.pr, world_u)
        st = U.allocateInstance(JClass(PH + "component." + T.capitalize() + "Store").class_)
        ref = U.allocateInstance(REFc.class_)
        jf(REFc.class_, "store").set(ref, st)
        jf(REFc.class_, "index").setInt(ref, 7)
        st.row(ref).put(CT["pr"], P.pr)
        es = U.allocateInstance(ESc.class_)
        jf(ESc.class_, "world").set(es, world)
        jf(STc.class_, "externalData").set(st, es)
        P.ref, P.st = ref, st
        jf(PR.class_, "entity").set(P.pr, ref)
        return P

    def tp_of(P):
        t = P.st.getComponent(P.ref, CT["tp"])
        if t is None:
            return None
        pos = jf(TPc.class_, "position").get(t)
        return [str(jf(TPc.class_, "world").get(t).getName()), round(float(pos.x()), 2), round(float(pos.y()), 2), round(float(pos.z()), 2)]

    def run_world(w):
        n = 0
        while w.tasks is not None and not w.tasks.isEmpty():
            w.tasks.poll().run()
            n += 1
        return n
    JStrC, CollC, ModC = JClass("java.lang.String"), JClass("java.util.Collection"), JClass("java.lang.reflect.Modifier")

    def deep(o, acc, depth=0):
        if o is None or depth > 6:
            return acc
        try:
            if isinstance(o, str):
                acc.append(o)
                return acc
            c_ = o.getClass()
            if c_ == JStrC.class_:
                acc.append(str(o))
                return acc
            if c_.isArray():
                if not c_.getComponentType().isPrimitive():
                    for x in o:
                        deep(x, acc, depth + 1)
                return acc
            if CollC.class_.isInstance(o):
                for x in o.toArray():
                    deep(x, acc, depth + 1)
                return acc
            if not str(c_.getName()).startswith("com.hypixel"):
                return acc
            k_ = c_
            while k_ is not None and str(k_.getName()).startswith("com.hypixel"):
                for f_ in k_.getDeclaredFields():
                    if ModC.isStatic(f_.getModifiers()) or f_.getType().isPrimitive():
                        continue
                    f_.setAccessible(True)
                    deep(f_.get(o), acc, depth + 1)
                k_ = k_.getSuperclass()
        except Exception:
            pass
        return acc

    def chat(P):
        acc = []
        for i in range(0 if P.net.sent is None else int(P.net.sent.size())):
            deep(P.net.sent.get(i), acc)
        return "\n".join(acc)
    return dict(U=U, jf=jf, CT=CT, UniH=UniH, mkworld=mkworld, CM=CM, player=player, tp_of=tp_of, run_world=run_world, chat=chat, TPc=TPc,
                LaterSpawn=JClass(T + ".LaterSpawn"), Finish=JClass(T + ".Finish"), Cmd=JClass(T + ".Cmd"))


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass
    import skyybuild as B
    S = sk()
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
        N = engine(S, B, hcls, "skyyprof07")
        UUID, Paths, Thread = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Thread")
        TRF = JClass("com.hypixel.hytale.math.vector.Transform")
        GSP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider")
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
            jc(k, "ProfCfg").LOG = HL.get("SkyyProfilesHarness" + k)
        W1, W1U, _c1 = N["mkworld"]("harness_home")
        WD, WDU, WDC = N["mkworld"]("harness_main")
        W2, W2U, _c2 = N["mkworld"]("harness_other")
        N["UniH"].DEF = WD
        SPAWN = TRF(12.5, 71.0, -8.5, 0.0, 45.0, 0.0)
        WDC.setSpawnProvider(GSP(SPAWN))
        SW = jc("new", "ProfSwitch")
        U1 = UUID.fromString("00000000-0000-0000-0000-0000000000d1")
        E = {}

        def travel(k="new"):
            P = N["player"](U1, W1, W1U)
            jc(k, "ProfSwitch").travel(P.st, P.ref, P.pr)
            return P
        # T1 instant provider
        P = travel()
        q = 0 if W1.tasks is None else int(W1.tasks.size())
        b = N["tp_of"](P)
        ran = N["run_world"](W1)
        E["t1"] = [q, b, ran, N["tp_of"](P), "SkyyIslands is not installed - you were sent to the world spawn." in N["chat"](P)]
        # T2 async provider, finished on another thread
        LS = N["LaterSpawn"]()
        WDC.setSpawnProvider(LS)
        P = travel()
        q0 = 0 if W1.tasks is None else int(W1.tasks.size())
        W1.by.clear()
        th = Thread(N["Finish"](LS.f, TRF(-4.0, 81.0, 3.0, 0.0, 0.0, 0.0), None), "harness-spawn-io")
        th.start()
        th.join()
        q1 = int(W1.tasks.size())
        who = [str(x) for x in W1.by]
        N["run_world"](W1)
        E["t2"] = [int(LS.asked), q0, q1, who, N["tp_of"](P), "sent to the world spawn" in N["chat"](P)]
        # T3 left the world
        P = travel()
        N["jf"](JClass("com.hypixel.hytale.server.core.universe.PlayerRef").class_, "worldUuid").set(P.pr, W2U)
        LS.f.complete(TRF(1.0, 2.0, 3.0, 0.0, 0.0, 0.0))
        E["t3"] = [N["run_world"](W1), N["tp_of"](P), N["chat"](P) == ""]
        # T4 a teleport pending
        P = travel()
        P.st.row(P.ref).put(N["CT"]["tp"], N["TPc"].createForPlayer(W2, TRF(0.0, 1.0, 0.0, 0.0, 0.0, 0.0)))
        LS.f.complete(TRF(1.0, 2.0, 3.0, 0.0, 0.0, 0.0))
        N["run_world"](W1)
        E["t4"] = [N["tp_of"](P)[0], 0 if P.st.added is None else int(P.st.added.size()), N["chat"](P) == ""]
        # T5 null
        P = travel()
        LS.f.complete(None)
        N["run_world"](W1)
        E["t5"] = [N["tp_of"](P), N["chat"](P) == ""]
        # T6 failure
        RECS.clear()
        P = travel()
        LS.f.completeExceptionally(JClass("java.lang.IllegalStateException")("harness: chunk load failed"))
        N["run_world"](W1)
        E["t6"] = [N["tp_of"](P), [x for x in logs() if "fallback teleport after a switch failed" in x]]
        # T7 /island resolvable
        N["CM"].cmds.put("island", N["Cmd"]())
        asked0 = int(LS.asked)
        P = travel()
        E["t7"] = [[str(x) for x in N["CM"].lines], int(LS.asked) - asked0, 0 if W1.tasks is None else int(W1.tasks.size())]
        N["CM"].cmds.remove("island")
        # T8 islandOnSwitch off
        jc("new", "ProfCfg").ISLAND_ON_SWITCH = False
        asked0 = int(LS.asked)
        P = travel()
        E["t8"] = [int(LS.asked) - asked0, N["tp_of"](P)]
        jc("new", "ProfCfg").ISLAND_ON_SWITCH = True
        # T9 control
        WDC.setSpawnProvider(GSP(SPAWN))
        RECS.clear()
        P = travel("prev")
        E["t9"] = [N["tp_of"](P), [x for x in logs() if "fallback teleport after a switch failed" in x]]
        # ================================================================================ ST: two starts on a COPY of the live data
        home = os.path.join(SCRATCH, "st", "mods", "Skyy_SkyyProfiles")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        Cfg, Store, Del, Pub, KeyFn = jc("new", "ProfCfg"), jc("new", "ProfStore"), jc("new", "ProfDel"), jc("new", "CfgPub"), jc("new", "KeyFn")
        Files, Attr = JClass("java.nio.file.Files"), JClass("java.nio.file.attribute.FileAttribute")
        from jpype import JArray
        starts = []
        for n_ in range(2):
            b0 = snap(home)
            Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
            Store.DIR, Store.SWDIR = Paths.get(os.path.join(home, "players")), Paths.get(os.path.join(home, "switching"))
            Store.INVDIR, Store.LOGF = Paths.get(os.path.join(home, "inventories")), Paths.get(os.path.join(home, "switches.log"))
            Del.ARCDIR = Paths.get(os.path.join(home, "archive"))
            up = Cfg.upgradeDefault()
            capm = Cfg.capMigrate()
            summ = str(Cfg.load())
            for d in (Store.DIR, Store.SWDIR, Store.INVDIR):
                Files.createDirectories(d, JArray(Attr)(0))
            waiting = int(Del.scanIndex())
            Cfg.bridge().put("profile:fn:key", KeyFn())
            Pub.start(Paths.get(os.path.dirname(home)), None)
            Pub.flush()
            time.sleep(0.4)
            Pub.flush()
            key = str(KeyFn().apply(UUID.fromString("d8ddde89-98b2-4739-983e-a39773d582b6")))
            Pub.shutdown()
            a0 = snap(home)
            starts.append([sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), up is None, capm is None, summ[:80], waiting, key])
        E["st"] = [starts, len(snap(home))]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    t1 = E["t1"]
    check(t1 == [1, None, 1, ["harness_main", 12.5, 71.0, -8.5], True], "T1: instant provider - ONE ProfSpawnTask on the player's world, no "
          "teleport before it runs, then Teleport to the main world's spawn + the 0.1.9 chat line: %s" % t1)
    t2 = E["t2"]
    check(t2 == [1, 0, 1, ["harness-spawn-io"], ["harness_main", -4.0, 81.0, 3.0], True], "T2: async provider - nothing queued until the future "
          "finishes on ANOTHER thread, which queues the task; it teleports: %s" % t2)
    check(E["t3"] == [1, None, True], "T3: the player left the world - nothing: %s" % E["t3"])
    check(E["t4"] == ["harness_other", 0, True], "T4: a teleport already pending - nothing (0.1.9's guard): %s" % E["t4"])
    check(E["t5"] == [None, True], "T5: no spawn point - nothing: %s" % E["t5"])
    check(E["t6"][0] is None and len(E["t6"][1]) == 1 and "harness: chunk load failed" in E["t6"][1][0], "T6: the future fails - the 0.1.9 "
          "warning: %s" % E["t6"])
    check(E["t7"] == [["island"], 0, 0], "T7: /island resolvable - /island runs, no spawn point asked: %s" % E["t7"])
    check(E["t8"] == [0, None], "T8: islandOnSwitch off - nothing: %s" % E["t8"])
    check(E["t9"][0] is None and len(E["t9"][1]) == 1 and "NoSuchMethodError" in E["t9"][1][0], "T9: CONTROL - 0.1.9's travel on 0.7.0 logs "
          "the NoSuchMethodError and nobody moves: %s" % E["t9"])
    st, nfiles = E["st"]
    check(len(st) == 2 and all(s_[0] == [] for s_ in st) and st[0][5] == st[1][5], "ST: two starts on a COPY of the live Skyy_SkyyProfiles "
          "(%d files): no file changed, the same active key: %s" % (nfiles, [s_[:1] + s_[3:] for s_ in st]))


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
        rules = []
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
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            check(cc["added"] == ["ProfSpawnTask"] and cc["gone"] == [], "CC: + exactly ProfSpawnTask, none gone: %s %s" % (cc["added"], cc["gone"]))
            check(not [c for c, v in cls_.items() if v["fields_new"] or v["fields_gone"]] and all(v["same_shape"] for v in cls_.values()),
                  "CC: no field added / removed, same supers / interfaces")
            struct = dict((c, sorted(x.split("(")[0] for x in v["structural"])) for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            print("CC. 0.1.9 -> 0.1.10 structural %s; constants only %s" % (struct, const))
            check(struct == {"ProfSwitch": ["travel"]}, "CC: the only structural change = ProfSwitch.travel: %s" % struct)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(cn - cp_ == {"com/skyy/profiles/ProfSpawnTask.class"} and not (cp_ - cn), "JT: class files = 0.1.9's + ProfSpawnTask: %s %s"
              % (sorted(cn - cp_), sorted(cp_ - cn)))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and all(zj.read(n) == zp.read(n) for n in nn if n != "manifest.json"),
              "JT: every non-class entry byte-identical but the manifest")
        mn, mpn = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mpn, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.1.9's but the version")
        # ---- A + T + ST
        out_e = os.path.join(SCRATCH, "e.json")
        with open(out_e + ".log", "wb") as lf:
            subprocess.run([sys.executable, me, "--e", "--out", out_e, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env, stdout=lf, stderr=subprocess.STDOUT)
        r = json.load(open(out_e)) if os.path.isfile(out_e) else None
        if r is None:
            print(open(out_e + ".log", encoding="utf8", errors="replace").read()[-3000:])
        check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-3000:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 40, "A (%s): %d classes load, verify (-Xverify:all), initialise on 0.7.0 %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check_e(r["E"])
        # ---- AA
        out_aa = os.path.join(SCRATCH, "aa.log")
        with open(out_aa, "wb") as lf:
            subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                           stderr=subprocess.STDOUT, cwd=ROOT)
        aa = open(out_aa, encoding="utf8", errors="replace").read()
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyProfiles " in ln]
        check("access:" in aa and not mine, "AA: crosscheck --jar 0.1.10: no FAIL for SkyyProfiles on 0.7.0: %s" % mine[:3])
        check("baseline SkyyProfiles %s -> %s: command / permission tree identical" % (PREV_VERSION, VERSION) in aa, "AA: the command / permission tree = 0.1.9's")
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        check(not chg, "the live Skyy_SkyyProfiles folder is unchanged: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyProfiles %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
