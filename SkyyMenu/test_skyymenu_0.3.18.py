"""SkyyMenu 0.3.18 - bare-JVM harness for THE HYTALE 0.7.0 PORT (tools/menu_0_3_18_patch.py). Child JVMs run the game's own JRE with the
0.7.0 HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. Nothing outside
the scratch folder is written (the live Skyy_SkyyMenu folder is only READ - copied into scratch for ST - and checked afterwards).

    python SkyyMenu/test_skyymenu_0.3.18.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyMenu-0.3.18.jar] [--prev SkyyMenu-0.3.17.jar]

SECTIONS
  CC  CLASS COMPARE 0.3.17 -> 0.3.18 (javassist text of every method): + exactly SpawnTask; structural changes only MenuPage.doSpawn /
      teleport / watchTick + the new moveTo / spawnResolved, PageGuard.forget; MenuData.<clinit> only the Mods-row icon
      (Furniture_Ancient_Chest_Large_Treasure -> Furniture_Ancient_Chest_Large); every other change = the version / patch-name constants
  JT  jar entries: 0.3.17's assets byte for byte but the manifest (version); class files = 0.3.17's + SpawnTask
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7.0 engine
  E   EXECUTED through the 0.7.0 engine's OWN PageManager (handleLegacyCustomPageEvent / clearLegacyCustomPageAcknowledgements):
        P1 a real menu opened (openCustomPage -> build), every packet acknowledged through handleLegacyCustomPageEvent
        P2 watchTick, healthy: the test click reaches the menu (probeSeen), nothing sent, no heal
        P3 watchTick, STUCK (an acknowledgement the client never sends): the counter is reset by clearLegacyCustomPageAcknowledgements,
           heals 1, the answer (the "Clicks were stuck" status redraw) sent, and the NEXT click works; after HEAL_ANSWERS heals a silent reset
        P4 PageGuard.forget: the menu forgotten like Esc (onDismiss + no current page), no packet, the counter untouched
        P5 watchTick after a world change: forgotten (no packet), the check ends
        P6 CONTROL: the 0.3.17 jar's PageGuard.forget / watchTick on 0.7.0 throw NoSuchMethodError (what the port fixes)
        S1 Spawn tile, a provider that answers at once (vanilla GlobalSpawnProvider): doSpawn queues ONE SpawnTask on the player's world
           (World.execute), nothing teleports before it runs; it runs -> Teleport to the main world at the spawn point, the TeleportHistory
           entry "Menu: Spawn" (the old position), the menu closed (SetPage None), the chat line
        S2 an ASYNC provider (a future that finishes later on ANOTHER thread): nothing queued / nothing waits until it finishes; then the
           task hops to the world (queued by that other thread) and teleports
        S3 the menu closed before the answer: the teleport still happens (moveTo + the chat line), no page packet
        S4 no spawn point (the future gives null): the open menu shows "The main world has no spawn point.", no teleport
        S5 the future fails: the open menu shows "The spawn point could not be found - try again.", a warning, no teleport
        S6 the player left that world before the answer: nothing happens
        S7 already teleporting: "You are already teleporting." (0.3.17's guard), no second Teleport
        S8 CONTROL: the 0.3.17 jar's doSpawn on 0.7.0 throws NoSuchMethodError
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyMenu folder (the layout store + settings loads, a menu opened each time): no file
      written by either start
  AA  python tools/ci/crosscheck.py --jar <0.3.18> --baseline: no FAIL for SkyyMenu, the command / permission tree identical to 0.3.17
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.18", "0.3.17"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pages07", "menu")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
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


# ============================================================================================ child: A + E + ST (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass, JImplements, JOverride
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
        # ---- engine stand-ins (0.7.0 shapes): a packet sink, a component store, worlds, the universe, an async spawn provider
        hclass("skyymenu07.Net", PH + "server.core.io.PacketHandler",
               "public Net() { super((" + PH + "protocol.io.ChannelConnection) null, (" + PH + "server.core.io.ProtocolVersion) null); }",
               ["public java.util.ArrayList sent;"],
               ["public void rec(Object p) { if (this.sent == null) this.sent = new java.util.ArrayList(); this.sent.add(p); }",
                "public boolean writePacket(" + PH + "protocol.ToClientPacket p, boolean c) { rec(p); return true; }",
                "public void write(" + PH + "protocol.ToClientPacket p) { rec(p); }",
                "public void write(" + PH + "protocol.ToClientPacket[] ps) { for (int i = 0; i < ps.length; i++) rec(ps[i]); }",
                "public void write(" + PH + "protocol.ToClientPacket[] ps, " + PH + "protocol.ToClientPacket p) { for (int i = 0; i < ps.length; i++) rec(ps[i]); rec(p); }",
                "public void writeNoCache(" + PH + "protocol.ToClientPacket p) { rec(p); }",
                "public void accept(" + PH + "protocol.ToServerPacket p) { }",
                "public String getIdentifier() { return \"skyymenu07\"; }"])
        hclass(PH + "component.SkyyMenu07Store", PH + "component.Store",
               "public SkyyMenu07Store() { super((" + PH + "component.ComponentRegistry) null, 0, (Object) null, (" + PH + "component.IResourceStorage) null); }",
               ["public java.util.IdentityHashMap comps;", "public java.util.ArrayList added;", "public " + PH + "component.ComponentType histType;"],
               ["public java.util.Map row(" + PH + "component.Ref r) {\n"
                "  if (this.comps == null) this.comps = new java.util.IdentityHashMap();\n"
                "  java.util.Map m = (java.util.Map) this.comps.get(r);\n"
                "  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }\n  return m;\n}",
                "public " + PH + "component.Component getComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t) {\n"
                "  return (" + PH + "component.Component) row(r).get(t);\n}",
                "public void addComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t, " + PH + "component.Component c) {\n"
                "  if (this.added == null) this.added = new java.util.ArrayList();\n  this.added.add(c);\n  row(r).put(t, c);\n}",
                "public " + PH + "component.Component ensureAndGetComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t) {\n"
                "  Object o = row(r).get(t);\n"
                "  if (o == null && t == this.histType) { o = new " + PH + "builtin.teleport.components.TeleportHistory(); row(r).put(t, o); }\n"
                "  return (" + PH + "component.Component) o;\n}"])
        hclass("skyymenu07.World", PH + "server.core.universe.world.World",
               "public World() { super((String) null, (java.nio.file.Path) null, (" + PH + "server.core.universe.world.WorldConfig) null); }",
               ["public java.util.concurrent.ConcurrentLinkedQueue tasks;", "public java.util.ArrayList by;"],
               ["public void execute(java.lang.Runnable r) {\n"
                "  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
                "  if (this.by == null) this.by = new java.util.ArrayList();\n"
                "  this.tasks.add(r);\n  synchronized (this.by) { this.by.add(Thread.currentThread().getName()); }\n}"])
        hclass("skyymenu07.Uni", PH + "server.core.universe.Universe",
               "public Uni() { super((" + PH + "server.core.plugin.JavaPluginInit) null); }",
               ["public static " + PH + "server.core.universe.world.World DEF;"],
               ["public " + PH + "server.core.universe.world.World getDefaultWorld() { return DEF; }"])
        hclass("skyymenu07.LaterSpawn", None, "public LaterSpawn() { }",
               ["public java.util.concurrent.CompletableFuture f;", "public int asked;"],
               ["public java.util.concurrent.CompletableFuture getSpawnPointAsync(" + PH + "server.core.universe.world.World w, java.util.UUID u) {\n"
                "  this.asked = this.asked + 1;\n  this.f = new java.util.concurrent.CompletableFuture();\n  return this.f;\n}",
                "public " + PH + "math.vector.Transform[] getSpawnPoints() { return new " + PH + "math.vector.Transform[0]; }",
                "public boolean isWithinSpawnDistance(org.joml.Vector3d p, double d) { return false; }"],
               [PH + "server.core.universe.world.spawn.ISpawnProvider"])
        hclass("skyymenu07.Finish", None, "public Finish(java.util.concurrent.CompletableFuture f, Object v, Throwable e) { this.f = f; this.v = v; this.e = e; }",
               ["public java.util.concurrent.CompletableFuture f;", "public Object v;", "public Throwable e;"],
               ["public void run() { if (this.e != null) this.f.completeExceptionally(this.e); else this.f.complete(this.v); }"],
               ["java.lang.Runnable"])
        hclass("skyymenu07.Cmd", PH + "server.core.command.system.AbstractCommand", "public Cmd() { super(\"x\", \"y\"); }", [],
               ["public boolean hasPermission(" + PH + "server.core.command.system.CommandSender s) { return true; }",
                "protected java.util.concurrent.CompletableFuture execute(" + PH + "server.core.command.system.CommandContext c) { return null; }"])
        hclass("skyymenu07.Cmds", PH + "server.core.command.system.CommandManager", "public Cmds() { super(); }",
               ["public java.util.HashMap cmds;", "public java.util.ArrayList lines;"],
               ["public " + PH + "server.core.command.system.AbstractCommand resolveCommand(String n) {\n"
                "  return this.cmds == null ? null : (" + PH + "server.core.command.system.AbstractCommand) this.cmds.get(n);\n}",
                "public java.util.concurrent.CompletableFuture handleCommand(" + PH + "server.core.command.system.CommandSender s, String line) {\n"
                "  if (this.lines == null) this.lines = new java.util.ArrayList();\n  this.lines.add(line);\n"
                "  return new java.util.concurrent.CompletableFuture();\n}"])
        hclass("skyymenu07.ItemMap", PH + "assetstore.map.DefaultAssetMap", "public ItemMap() { super(); }",
               ["public " + PH + "assetstore.JsonAsset item;"],
               ["public " + PH + "assetstore.JsonAsset getAsset(Object k) { return this.item; }"])
        hclass("skyymenu07.Items", PH + "assetstore.AssetStore", "public Items() { super((" + PH + "assetstore.AssetStore$Builder) null); }",
               ["public " + PH + "assetstore.AssetMap map;"],
               ["public " + PH + "assetstore.AssetMap getAssetMap() { return this.map; }"])

        UUID, Paths, ArrayList, HashMap, HashSet = (JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"),
                                                    JClass("java.util.HashMap"), JClass("java.util.HashSet"))
        # the engine's asset store registry (no asset loaded): WorldConfig / GameplayConfig's codecs ask it while they initialise
        from jpype import JArray, JString
        JClass(PH + "server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
        HSV = JClass(PH + "server.core.HytaleServer")
        hs = U.allocateInstance(HSV.class_)
        jf(HSV.class_, "eventBus").set(hs, JClass(PH + "event.EventBus")(False))
        jf(HSV.class_, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
        jf(HSV.class_, "instance").set(None, hs)
        JClass(PH + "server.core.asset.AssetRegistryLoader").init()
        NET, TSC, HW = JClass("skyymenu07.Net"), JClass(PH + "component.SkyyMenu07Store"), JClass("skyymenu07.World")
        PMc = JClass(PH + "server.core.entity.entities.player.pages.PageManager")
        WMc = JClass(PH + "server.core.entity.entities.player.windows.WindowManager")
        UniC, UniH = JClass(PH + "server.core.universe.Universe"), JClass("skyymenu07.Uni")
        EMc = JClass(PH + "server.core.modules.entity.EntityModule")
        TPLc = JClass(PH + "builtin.teleport.TeleportPlugin")
        ESc = JClass(PH + "server.core.universe.world.storage.EntityStore")
        STc = JClass(PH + "component.Store")
        CTc = JClass(PH + "component.ComponentType")
        REFc = JClass(PH + "component.Ref")
        PLAc = JClass(PH + "server.core.entity.entities.Player")
        PR = JClass(PH + "server.core.universe.PlayerRef")
        CPE = JClass(PH + "protocol.packets.interface_.CustomPageEvent")
        CPT = JClass(PH + "protocol.packets.interface_.CustomPageEventType")
        CMGRc = JClass(PH + "server.core.command.system.CommandManager")
        PMOD = JClass(PH + "server.core.permissions.PermissionsModule")
        WCFG = JClass(PH + "server.core.universe.world.WorldConfig")
        GSP = JClass(PH + "server.core.universe.world.spawn.GlobalSpawnProvider")
        TRF = JClass(PH + "math.vector.Transform")
        TPc = JClass(PH + "server.core.modules.entity.teleport.Teleport")
        TCc = JClass(PH + "server.core.modules.entity.component.TransformComponent")
        THc = JClass(PH + "builtin.teleport.components.TeleportHistory")
        nxt = [900]

        def ctype():
            c = CTc()
            nxt[0] += 1
            jf(CTc.class_, "index").setInt(c, nxt[0])
            jf(CTc.class_, "hashCode").setInt(c, nxt[0])
            return c
        CT_PR, CT_PLA, CT_TP, CT_TC, CT_HR, CT_HIST = ctype(), ctype(), ctype(), ctype(), ctype(), ctype()
        uni = U.allocateInstance(UniH.class_)
        jf(UniC.class_, "playerRefComponentType").set(uni, CT_PR)
        WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
        jf(UniC.class_, "worldsByUuid").set(uni, WORLDS)
        jf(UniC.class_, "worlds").set(uni, JClass("java.util.concurrent.ConcurrentHashMap")())
        jf(UniC.class_, "players").set(uni, ArrayList())
        jf(UniC.class_, "playersByUuid").set(uni, JClass("java.util.concurrent.ConcurrentHashMap")())
        jf(UniC.class_, "instance").set(None, uni)
        em = U.allocateInstance(EMc.class_)
        for fn_, ct_ in (("playerComponentType", CT_PLA), ("teleportComponentType", CT_TP), ("transformComponentType", CT_TC),
                         ("headRotationComponentType", CT_HR)):
            jf(EMc.class_, fn_).set(em, ct_)
        jf(EMc.class_, "instance").set(None, em)
        tpl = U.allocateInstance(TPLc.class_)
        jf(TPLc.class_, "teleportHistoryComponentType").set(tpl, CT_HIST)
        jf(TPLc.class_, "instance").set(None, tpl)

        def mkworld(name):
            w = U.allocateInstance(HW.class_)
            wu = UUID.randomUUID()
            jf(JClass(PH + "server.core.universe.world.World").class_, "name").set(w, name)
            cfg = U.allocateInstance(WCFG.class_)      # the class is initialised (asset registry above); no default codecs needed
            jf(JClass(PH + "server.core.universe.world.World").class_, "worldConfig").set(w, cfg)
            WORLDS.put(wu, w)
            return w, wu, cfg
        W1, W1U, W1C = mkworld("harness_home")
        WD, WDU, WDC = mkworld("harness_main")
        W2, W2U, W2C = mkworld("harness_other")
        UniH.DEF = WD
        SPAWN = TRF(10.5, 70.0, -20.5, 0.0, 90.0, 0.0)
        WDC.setSpawnProvider(GSP(SPAWN))
        CM = U.allocateInstance(JClass("skyymenu07.Cmds").class_)
        CM.cmds = HashMap()
        CM.lines = ArrayList()
        for cn_ in ("island", "hub", "sacks", "accessories", "skymenu", "spawn"):
            CM.cmds.put(cn_, U.allocateInstance(JClass("skyymenu07.Cmd").class_))
        jf(CMGRc.class_, "instance").set(None, CM)
        ITc = JClass(PH + "server.core.asset.type.item.config.Item")
        IMAP = U.allocateInstance(JClass("skyymenu07.ItemMap").class_)
        IMAP.item = U.allocateInstance(ITc.class_)
        ISTORE = U.allocateInstance(JClass("skyymenu07.Items").class_)
        ISTORE.map = IMAP
        jf(ITc.class_, "ASSET_STORE").set(None, ISTORE)
        PLAIN = UUID.fromString("00000000-0000-0000-0000-0000000000c1")
        OP = UUID.fromString("00000000-0000-0000-0000-0000000000c2")
        USERS = {str(PLAIN): ["hytale:Adventurer"], str(OP): ["hytale:Admin"]}
        GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

        def jset(*xs):
            st_ = HashSet()
            for x in xs:
                st_.add(x)
            return st_

        @JImplements(PH + "server.core.permissions.provider.PermissionProvider")
        class Prov:
            @JOverride
            def getName(self): return "menu0318-test"
            @JOverride
            def getUserPermissions(self, u): return jset()
            @JOverride
            def getGroupsForUser(self, u): return jset(*USERS.get(str(u), []))
            @JOverride
            def getGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
            @JOverride
            def getEffectiveGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
            @JOverride
            def getGroupParent(self, g): return None
            @JOverride
            def getAllRegisteredGroups(self): return jset(*GROUPS.keys())
            @JOverride
            def getUsersWithPermission(self, n): return HashSet()
            @JOverride
            def removeUserPermissionFromAll(self, n): return HashSet()
            @JOverride
            def addUserPermissions(self, *a): return HashSet()
            @JOverride
            def removeUserPermissions(self, *a): return None
            @JOverride
            def addUserToGroup(self, *a): return None
            @JOverride
            def addGroupPermissions(self, *a): return None
            @JOverride
            def removeGroupPermissions(self, *a): return None
            @JOverride
            def removeUserFromGroup(self, *a): return None
            @JOverride
            def setUserGroup(self, *a): return None
        pmod = U.allocateInstance(PMOD.class_)
        provs = ArrayList()
        provs.add(Prov())
        jf(PMOD.class_, "providers").set(pmod, provs)
        jf(PMOD.class_, "virtualGroups").set(pmod, HashMap())
        jf(PMOD.class_, "instance").set(None, pmod)

        def JV(k, n):
            return JClass(PKG + n, loader=L[k])
        mods = os.path.join(SCRATCH, "world", "mods")
        for k in ("new", "prev"):
            JV(k, "PageGuard").STOP = False
            JV(k, "PageGuard").EXEC = None
            JV(k, "SetStore").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "settings-" + k))
            JV(k, "Tips").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "notips-" + k))
            JV(k, "PetTile").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyPets", "pets"))
            JV(k, "MenuLayout").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "layouts-" + k))
            JV(k, "MenuLayout").DEF_FILE = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "layout-default-" + k + ".properties"))
        WARN = []

        class Pl:
            pass

        def player(uid=PLAIN, world_u=None):
            P = Pl()
            P.pr = U.allocateInstance(PR.class_)
            jf(PR.class_, "uuid").set(P.pr, uid)
            jf(PR.class_, "username").set(P.pr, "SkyyHarness")
            P.net = U.allocateInstance(NET.class_)
            jf(PR.class_, "packetHandler").set(P.pr, P.net)
            jf(PR.class_, "worldUuid").set(P.pr, world_u or W1U)
            P.pl = U.allocateInstance(PLAc.class_)
            P.wm = WMc()
            P.wm.init(P.pr)
            P.pm = PMc()
            P.pm.init(P.pr, P.wm)
            jf(PLAc.class_, "windowManager").set(P.pl, P.wm)
            jf(PLAc.class_, "pageManager").set(P.pl, P.pm)
            st = U.allocateInstance(TSC.class_)
            st.histType = CT_HIST
            ref = U.allocateInstance(REFc.class_)
            jf(REFc.class_, "store").set(ref, st)
            jf(REFc.class_, "index").setInt(ref, 7)
            st.row(ref).put(CT_PR, P.pr)
            st.row(ref).put(CT_PLA, P.pl)
            tc = U.allocateInstance(TCc.class_)
            jf(TCc.class_, "position").set(tc, JClass("org.joml.Vector3d")(1.0, 64.0, 2.0))
            st.row(ref).put(CT_TC, tc)
            es = U.allocateInstance(ESc.class_)
            jf(ESc.class_, "world").set(es, W1)
            jf(STc.class_, "externalData").set(st, es)
            P.ref, P.st = ref, st
            jf(PR.class_, "entity").set(P.pr, P.ref)
            P.seen = 0
            return P

        def sent(P):
            return [] if P.net.sent is None else [P.net.sent.get(i) for i in range(int(P.net.sent.size()))]

        def kinds(P, frm=0):
            return [str(p.getClass().getSimpleName()) for p in sent(P)[frm:]]

        def acks(P):
            return int(jf(PMc.class_, "customPageRequiredAcknowledgments").get(P.pm).get())

        def pump(P):
            """the client: acknowledge every page packet since the last pump (through the 0.7.0 engine's own handler)"""
            for p in sent(P)[P.seen:]:
                if str(p.getClass().getSimpleName()) in ("CustomPage", "SetPage"):
                    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, CPE(CPT.Acknowledge, None))
            P.seen = len(sent(P))

        def run_world(w):
            n = 0
            while w.tasks is not None and not w.tasks.isEmpty():
                w.tasks.poll().run()
                n += 1
            return n

        JStrC, CollC, ModC = JClass("java.lang.String"), JClass("java.util.Collection"), JClass("java.lang.reflect.Modifier")

        def deep(o, acc, depth=0):
            """every String reachable through the fields / arrays / collections of a packet (the chat text of a ServerMessage)"""
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

        def strs_of(P, frm=0):
            acc = []
            for p in sent(P)[frm:]:
                deep(p, acc)
            return "\n".join(acc)

        def menu(k, uid=PLAIN, view="main"):
            P = player(uid)
            pg = JV(k, "MenuPage")(P.pr, view)
            P.pm.openCustomPage(P.ref, P.st, pg)
            pump(P)
            return pg, P
        E = {}
        # ================================================================================ P: the page events
        pg, P = menu("new")
        E["p1"] = [P.pm.getCustomPage() == pg, acks(P), kinds(P)]
        n0 = len(sent(P))
        pg.lastSend = 0
        r2 = bool(pg.watchTick(W1))
        E["p2"] = [r2, bool(pg.probeSeen), int(pg.heals), len(sent(P)) - n0, acks(P)]
        # P3 stuck: one acknowledgement the client will never send
        jf(PMc.class_, "customPageRequiredAcknowledgments").get(P.pm).set(1)
        n1 = len(sent(P))
        pg.lastSend = 0
        r3 = bool(pg.watchTick(W1))
        after = kinds(P, n1)
        st3 = str(pg.status)
        acks_after_answer = acks(P)
        pump(P)
        pg.lastSend = 0
        r3b = bool(pg.watchTick(W1))
        E["p3"] = [r3, int(pg.heals), after, st3, acks_after_answer, acks(P), r3b, bool(pg.probeSeen)]
        # the third heal is the last one with an answer; the fourth resets silently
        silent = []
        for i_ in range(3):
            jf(PMc.class_, "customPageRequiredAcknowledgments").get(P.pm).set(1)
            nn = len(sent(P))
            pg.lastSend = 0
            pg.watchTick(W1)
            silent.append([int(pg.heals), kinds(P, nn), acks(P)])
            pump(P)
        E["p3s"] = silent
        # P4 PageGuard.forget
        pg4, P4 = menu("new")
        n4, a4 = len(sent(P4)), acks(P4)
        f4 = bool(JV("new", "PageGuard").forget(P4.pm, P4.ref, P4.st, pg4))
        E["p4"] = [f4, P4.pm.getCustomPage() is None, len(sent(P4)) - n4, acks(P4) == a4,
                   bool(JV("new", "PageGuard").forget(P4.pm, P4.ref, P4.st, pg4))]
        # P5 world change
        pg5, P5 = menu("new")
        n5 = len(sent(P5))
        r5 = bool(pg5.watchTick(W2))
        E["p5"] = [r5, P5.pm.getCustomPage() is None, len(sent(P5)) - n5]
        # P6 control: 0.3.17 on 0.7.0
        pgo, Po = menu("prev")
        ctl = []
        try:
            JV("prev", "PageGuard").forget(Po.pm, Po.ref, Po.st, pgo)
            ctl.append("no error")
        except Exception as e_:
            ctl.append(str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_))
        pgo.lastSend = 0
        try:
            pgo.watchTick(W1)
            ctl.append("no error")
        except Exception as e_:
            ctl.append(str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_))
        E["p6"] = ctl
        # ================================================================================ S: the Spawn tile
        TPT = TPc.getComponentType()

        def tp_of(P):
            t = P.st.getComponent(P.ref, TPT)
            if t is None:
                return None
            pos = jf(TPc.class_, "position").get(t)
            return [str(jf(TPc.class_, "world").get(t).getName()), round(float(pos.x()), 2), round(float(pos.y()), 2), round(float(pos.z()), 2)]

        def hist(P):
            h = P.st.getComponent(P.ref, CT_HIST)
            if h is None:
                return []
            b = jf(THc.class_, "back").get(h)
            return [str(x.toString()) for x in b.toArray()]
        # S1 instant provider
        WDC.setSpawnProvider(GSP(SPAWN))
        pgs, Ps = menu("new", OP)
        ns = len(sent(Ps))
        pgs.doSpawn(Ps.ref, Ps.st)
        q1 = 0 if W1.tasks is None else int(W1.tasks.size())
        before = tp_of(Ps)
        ran = run_world(W1)
        E["s1"] = [q1, before, ran, tp_of(Ps), hist(Ps), kinds(Ps, ns), Ps.pm.getCustomPage() is None, strs_of(Ps, ns)]
        # S2 async provider: finished later on another thread
        LS = JClass("skyymenu07.LaterSpawn")()
        WDC.setSpawnProvider(LS)
        pga, Pa = menu("new", OP)
        na = len(sent(Pa))
        pga.doSpawn(Pa.ref, Pa.st)
        q_before = 0 if W1.tasks is None else int(W1.tasks.size())
        tp_before = tp_of(Pa)
        W1.by.clear()
        th = JClass("java.lang.Thread")(JClass("skyymenu07.Finish")(LS.f, TRF(-3.0, 80.0, 4.0, 0.0, 0.0, 0.0), None), "harness-spawn-io")
        th.start()
        th.join()
        q_after = int(W1.tasks.size())
        who = [str(x) for x in W1.by]
        ran2 = run_world(W1)
        E["s2"] = [int(LS.asked), q_before, tp_before, q_after, who, ran2, tp_of(Pa), Pa.pm.getCustomPage() is None, kinds(Pa, na)]
        # S3 menu closed (Esc) before the answer
        pgc, Pc = menu("new", OP)
        pgc.doSpawn(Pc.ref, Pc.st)
        Pc.pm.handleLegacyCustomPageEvent(Pc.ref, Pc.st, CPE(CPT.Dismiss, None))
        nc = len(sent(Pc))
        LS.f.complete(TRF(5.0, 66.0, 6.0, 0.0, 0.0, 0.0))
        run_world(W1)
        E["s3"] = [tp_of(Pc), kinds(Pc, nc), strs_of(Pc, nc), hist(Pc)]
        # S4 no spawn point
        pgn, Pn = menu("new", OP)
        pgn.doSpawn(Pn.ref, Pn.st)
        nn4 = len(sent(Pn))
        LS.f.complete(None)
        run_world(W1)
        E["s4"] = [tp_of(Pn), str(pgn.status), kinds(Pn, nn4), Pn.pm.getCustomPage() == pgn]
        # S5 the future fails
        pge, Pe = menu("new", OP)
        pge.doSpawn(Pe.ref, Pe.st)
        ne = len(sent(Pe))
        LS.f.completeExceptionally(JClass("java.lang.IllegalStateException")("harness: chunk load failed"))
        run_world(W1)
        E["s5"] = [tp_of(Pe), str(pge.status), kinds(Pe, ne)]
        # S6 the player left the world before the answer
        pgl, Pl_ = menu("new", OP)
        pgl.doSpawn(Pl_.ref, Pl_.st)
        jf(PR.class_, "worldUuid").set(Pl_.pr, W2U)
        nl = len(sent(Pl_))
        LS.f.complete(TRF(9.0, 70.0, 9.0, 0.0, 0.0, 0.0))
        ranl = run_world(W1)
        E["s6"] = [ranl, tp_of(Pl_), kinds(Pl_, nl)]
        # S7 already teleporting
        WDC.setSpawnProvider(GSP(SPAWN))
        pgt, Pt = menu("new", OP)
        Pt.st.row(Pt.ref).put(TPT, TPc.createForPlayer(W2, TRF(0.0, 1.0, 0.0, 0.0, 0.0, 0.0)))
        pgt.doSpawn(Pt.ref, Pt.st)
        run_world(W1)
        E["s7"] = [str(pgt.status), tp_of(Pt), 0 if Pt.st.added is None else int(Pt.st.added.size())]
        # S8 control
        pgo2, Po2 = menu("prev", OP)
        try:
            pgo2.doSpawn(Po2.ref, Po2.st)
            E["s8"] = "no error"
        except Exception as e_:
            E["s8"] = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
        # ================================================================================ ST: start twice on a COPY of the live data
        st = {}
        copy = os.path.join(SCRATCH, "livecopy", "Skyy_SkyyMenu")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, copy)
        else:
            os.makedirs(copy)
        st["live_files"] = len(snap(copy))
        ML = JV("new", "MenuLayout")
        ML.DIR = Paths.get(os.path.join(copy, "layouts"))
        ML.DEF_FILE = Paths.get(os.path.join(copy, "layout-default.properties"))
        JV("new", "SetStore").DIR = Paths.get(os.path.join(copy, "settings"))
        b0 = snap(copy)
        res = []
        for n_ in range(2):
            for m_ in (ML.OWN, ML.NAMES, ML.DIRTY, ML.BROKEN, ML.WARNED, ML.ERRAT):
                m_.clear()
            ML.loadDefault()
            pgx, Px = menu("new", UUID.fromString("d8ddde89-98b2-4739-983e-a39773d582b6"))
            time.sleep(0.6)
            ML.flushAll()
            res.append([Px.pm.getCustomPage() == pgx, snap(copy) == b0])
        st["starts"] = res
        E["st"] = st
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    p1 = E["p1"]
    check(p1[0] and p1[1] == 0 and "CustomPage" in p1[2], "P1: a real menu opened through the 0.7.0 PageManager, every packet acknowledged "
          "through handleLegacyCustomPageEvent: %s" % p1)
    check(E["p2"] == [True, True, 0, 0, 0], "P2: watchTick healthy - the test click reaches the menu, nothing sent, no heal: %s" % E["p2"])
    p3 = E["p3"]
    check(p3[0] and p3[1] == 1 and p3[2] == ["CustomPage"] and "Clicks were stuck" in p3[3] and p3[4] == 1 and p3[5] == 0 and p3[6] and p3[7],
          "P3: STUCK - clearLegacyCustomPageAcknowledgements reset the counter, heal 1, the answer (status redraw) sent and acknowledged, the "
          "next test click works: %s" % p3)
    s = E["p3s"]
    check([x[0] for x in s] == [2, 3, 4] and s[0][1] == ["CustomPage"] and s[1][1] == ["CustomPage"] and s[2][1] == [] and s[2][2] == 0,
          "P3: heals 2 and 3 answer, the 4th resets silently (HEAL_ANSWERS 3): %s" % s)
    check(E["p4"] == [True, True, 0, True, False], "P4: PageGuard.forget = the 0.7.0 Dismiss: forgotten, no packet, counter untouched; a second "
          "forget does nothing: %s" % E["p4"])
    check(E["p5"] == [False, True, 0], "P5: watchTick after a world change forgets the menu (no packet) and ends: %s" % E["p5"])
    check(E["p6"] == ["java.lang.NoSuchMethodError"] * 2, "P6: CONTROL - 0.3.17's PageGuard.forget / watchTick throw on 0.7.0: %s" % E["p6"])
    s1 = E["s1"]
    check(s1[0] == 1 and s1[1] is None and s1[2] == 1 and s1[3] == ["harness_main", 10.5, 70.0, -20.5]
          and len(s1[4]) == 1 and "Menu: Spawn" in s1[4][0] and "SetPage" in s1[5] and s1[6] and "Teleporting to Spawn" in s1[7],
          "S1: instant provider - ONE SpawnTask queued on the player's world, no teleport before it runs; then Teleport to the main world's "
          "spawn, the TeleportHistory entry, the menu closed, the chat line: %s" % s1[:7])
    s2 = E["s2"]
    check(s2[0] == 1 and s2[1] == 0 and s2[2] is None and s2[3] == 1 and s2[4] == ["harness-spawn-io"] and s2[5] == 1
          and s2[6] == ["harness_main", -3.0, 80.0, 4.0] and s2[7],
          "S2: async provider - nothing queued or waiting until the future finishes on ANOTHER thread, which queues the task on the world; "
          "it teleports there: %s" % s2)
    s3 = E["s3"]
    check(s3[0] == ["harness_main", 5.0, 66.0, 6.0] and "SetPage" not in s3[1] and "CustomPage" not in s3[1] and "Teleporting to Spawn" in s3[2]
          and len(s3[3]) == 1, "S3: the menu closed before the answer - the teleport (moveTo + history) and the chat line, no page packet: %s" % s3[:2])
    s4 = E["s4"]
    check(s4[0] is None and s4[1] == "The main world has no spawn point." and "CustomPage" in s4[2] and s4[3],
          "S4: no spawn point - the 0.3.17 status on the open menu, no teleport: %s" % s4)
    s5 = E["s5"]
    check(s5[0] is None and s5[1] == "The spawn point could not be found - try again." and "CustomPage" in s5[2],
          "S5: the future fails - the status line, no teleport: %s" % s5)
    check(E["s6"][0] == 1 and E["s6"][1] is None and E["s6"][2] == [], "S6: the player left the world - the task runs and does nothing: %s" % E["s6"])
    check(E["s7"][0] == "You are already teleporting." and E["s7"][1][0] == "harness_other" and E["s7"][2] == 0,
          "S7: already teleporting - 0.3.17's guard, no second Teleport: %s" % E["s7"])
    check(E["s8"] == "java.lang.NoSuchMethodError", "S8: CONTROL - 0.3.17's doSpawn throws on 0.7.0: %s" % E["s8"])
    st = E["st"]
    check(st["starts"] == [[True, True], [True, True]], "ST: two starts on a COPY of the live Skyy_SkyyMenu (%d files): a menu opens, no file "
          "written: %s" % (st["live_files"], st["starts"]))


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
        rules = [[r"menu_0_3_18_patch", "menu_0_3_17_patch"], [r'"Furniture_Ancient_Chest_Large"', '"Furniture_Ancient_Chest_Large_Treasure"']]
        # the ready line names the UI kit's blob (skyyui.py changed this round: SUI.verify for 0.7.0) - map the new kit id to the old one
        kid = [re.search(rb"skyyui \d+\.\d+ [0-9a-f]{12}", zipfile.ZipFile(j_).read("com/skyy/menu/SkyyMenuPlugin.class")) for j_ in (JAR, PREV_JAR)]
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
            check(cc["added"] == ["SpawnTask"] and cc["gone"] == [], "CC: + exactly SpawnTask, none gone: %s %s" % (cc["added"], cc["gone"]))
            check(not [c for c, v in cls_.items() if v["fields_new"] or v["fields_gone"]] and all(v["same_shape"] for v in cls_.values()),
                  "CC: no field added / removed in any 0.3.17 class, same supers / interfaces")
            struct = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else "") for x in v["structural"])) for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            print("CC. 0.3.17 -> 0.3.18 structural %s; constants only %s" % (struct, const))
            check(struct == {"MenuPage": ["doSpawn", "moveTo (new)", "spawnResolved (new)", "teleport", "watchTick"], "PageGuard": ["forget"]},
                  "CC: structural changes = MenuPage doSpawn / teleport / watchTick + moveTo / spawnResolved, PageGuard.forget only: %s" % struct)
            check(all(c == "SkyyMenuPlugin" or c == "MenuData" for c in const), "CC: other changes = constants (version, the Mods-row icon): %s" % const)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn, np_ = set(n for n in zj.namelist() if not n.endswith(".class")), set(n for n in zp.namelist() if not n.endswith(".class"))
        check(nn == np_, "JT: the same asset files as 0.3.17: %s" % sorted(nn ^ np_))
        chg = sorted(n for n in np_ & nn if zj.read(n) != zp.read(n))
        check(chg == ["manifest.json"], "JT: every 0.3.17 asset byte-identical but the manifest: %s" % chg)
        mn, mpn = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mpn, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.17's but the version")
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(cn - cp_ == {"com/skyy/menu/SpawnTask.class"} and not (cp_ - cn), "JT: class files = 0.3.17's + SpawnTask: %s %s" % (sorted(cn - cp_), sorted(cp_ - cn)))
        # ---- A + E + ST
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
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyMenu " in ln]
        check("access:" in aa and not mine, "AA: crosscheck --jar 0.3.18: no FAIL for SkyyMenu on 0.7.0 (%s): %s"
              % ([ln for ln in aa.splitlines() if ln.startswith("access:")], mine[:3]))
        check("baseline SkyyMenu %s -> %s: command / permission tree identical" % (PREV_VERSION, VERSION) in aa, "AA: the command / permission tree = 0.3.17's")
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        check(not chg, "the live Skyy_SkyyMenu folder is unchanged: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyMenu %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
