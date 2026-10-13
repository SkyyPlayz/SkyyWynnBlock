"""Harness for SkyyMenu 0.3.19 (lag fixes + the hub hotkey; tools/menu_0_3_19_patch.py).
Build first: python tools/menu_0_3_19_patch.py && python SkyyMenu/build_skyymenu_0.3.19.py

    python SkyyMenu/test_skyymenu_0.3.19.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, the 0.7.0 HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch
folder; the exec phase runs with -Xverify:all, 0.3.18 and 0.3.19 each in its own class loader over stand-ins of the engine (0.7.0 shapes,
the SkyyMenu 0.3.18 harness's): a recording packet sink, a component store, recording worlds, the Universe, the real PageManager /
WindowManager, a stand-in item store, a permissions provider):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.18 -> 0.3.19: exactly the listed members differ, + MenuIO, MenuIdx, GivenSave, MenuHotkey, HotkeyOpen
  X  exec
     SCAN    the bytecode: HytaleServer.SCHEDULED_EXECUTOR is read by exactly the page timers (PageGuard / StaleTask / MenuWatch EXEC set in
             setup, RefreshTask, CloseTask) - no longer by SetStore.saveSoon, SetLoadTask.preload, MenuLayout.preload / saveSoon,
             AdmSaveTask.save, Given.schedule, GrantTask.later, the tickers or the kit's CfgFile.schedule (all on 0.3.18 = CONTROL);
             the bridge key-set scans: SetReg.drain (setup) + MenuIdx.scan only
     BRIDGE  MenuUtil.bridge() = the System property map (same identity), cached; answers while System.class's monitor is held (0.3.18 waits)
     IO      MenuIO: a daemon thread named SkyyMenu-IO, schedule / every run there, stop() lets a pending save finish, then schedule = false
             (the callers' inline fallback), begin() starts again
     WRITES  with a RECORDING SkyyMenu-IO: a settings change (SetStore.set -> saveSoon 500 ms), the join preload (SetLoadTask), a layout
             swap (LayoutSaveTask 300 ms) + the layout preload, a Server Setup export (AdmSaveTask), SkyyMenu's own Server Setup row save
             (the kit's CfgSaveTask through CfgFile.schedule), a menu-item record (GivenSave), the grant (GrantTask), the index (MenuIdx),
             the tickers (SeenTick, GivenTick) - each lands on SkyyMenu-IO with 0.3.18's delay; run there, the files are written
             byte-for-byte as 0.3.18 writes them; MenuIO stopped -> each runs inline as 0.3.18's refused path did
     GRANT   the menu-item grant step by step (the IO thread and the world thread driven by hand): the file checks run on SkyyMenu-IO
             (the record, the 0.1-0.3.3 legacy flag migration), the world hop happens only when an item may be needed, the world thread
             only counts + gives, the record is written back on SkyyMenu-IO; a recorded profile = no world hop; an item already held =
             recorded, no second item; SkyyProfiles busy = retry on IO; a profile switch between the two steps = back to the file check
             with the new key; no world = retry; GIVE_ITEM off; 30 tries at most; MenuIO stopped = PENDING released; the chat line names
             the hotkey; the same items + records as 0.3.18's grant for the same cases (CONTROL)
     FIXR    (fix round) a refused Given.schedule (a task pending) forgets EPOCH -> the next tick schedules; a GrantTask that ends
             unfinished (30 tries used up) forgets EPOCH -> GivenTick schedules again; the hotkey refuses over an open window and while
             profile:busy (REFUSED counted, nothing sent); the timing follows MenuCfg (Server Setup rows menu.hotkeyGapMs /
             menu.hotkeyCooldownMs in the published header, config.properties read + clamped by MenuCfg.load)
     EPOCH   GivenTick asks profile:fn:key only on a profile:epoch change (first tick, a switch, a new profile), every tick without an
             epoch; 0.3.18 asks every tick (CONTROL)
     WATCH   a real menu through the 0.7.0 PageManager: healthy checks back off 1 s, 1 s, 1 s, 2 s, 2 s ... (FIX ROUND: 2 s at most); a page packet (a
             redraw) starts over at 1 s; a STUCK page is still healed at once and starts over; MenuWatch's world step schedules the next
             check with watchDelay on the page scheduler
     INDEX   MenuIdx: scan = the settings:def:* keys + config:def:<Mod> names; no rescan while nothing changed; a new key (size change)
             -> a rescan on SkyyMenu-IO (at most every 2 s), an old index (60 s) -> rescan; the first use builds it in place; the
             Settings page's drainIdx registers a settings:def key put without register (0.3.18's drain did too); AdminPage.cfgMods =
             0.3.18's cfgMods on the same bridge (the real kit headers of SkyyMenu + SkyyBank + SkyyProfiles + junk keys)
     HOTKEY  step(): two presses within 0.4 s fire once; a slow second press re-arms; 1.5 s cooldown; a press while not still disarms;
             holding crouch never fires; still() for every movement state; tick() through a stand-in ArchetypeChunk + Store with the
             real MovementStatesComponent: no state kept for a player who never crouches, double tap -> ONE HotkeyOpen queued on the
             player's world (never opened inside the tick); HotkeyOpen opens the SkyWynn Menu (main view) through the real PageManager;
             not with another page open, not with menu.hotkey OFF, not after shutdown (ON false); prune drops dead refs; the switch is
             registered (General, ON by default) and in the defaults template
  D  live     start twice on a scratch COPY of the live Skyy_SkyyMenu (layout default + a player's layout + settings load + a menu opened +
              the index built): no file written by either start
  AA engine-access audit
Scratch: tools/dev/scratch/perfmenu/menu (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, time, threading, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.19"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.18.jar")
BANK_JAR = os.path.join(ROOT, "SkyyBank", "SkyyBank-0.1.9.jar")
PROF_JAR = os.path.join(ROOT, "SkyyProfiles", "SkyyProfiles-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfmenu", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
EXPECT = {}            # filled from the compare phase's own listing below (EXPECT_FILE) - see the constant after it
ADDED = ["MenuIO", "MenuIdx", "GivenSave", "MenuHotkey", "HotkeyOpen"]
EXPECT = {
    "MenuUtil": ["+f BRIDGE", "+m bridge0", "~m bridge"],
    "Given": ["+f EPOCH", "~<clinit>", "~m forget", "~m retainOnline", "-m plan", "+m planFiles", "+m planHeld", "+m markLater", "~m schedule", "~m claim"],
    "SetStore": ["~m saveSoon"],
    "SetLoadTask": ["~m preload"],
    "SetReg": ["+m drainIdx", "~m loadAdmin"],                                  # loadAdmin: the defaults template text (+ #menu.hotkey=true)
    "SettingsPage": ["~m build"],
    "AdminPage": ["~m cfgMods"],
    "MenuLayout": ["~m preload", "~m saveSoon"],
    "AdmSaveTask": ["~m save"],
    "MenuWatch": ["+m scheduleIn", "~m run"],
    "MenuPage": ["+f healthy", "+f seenSend", "+m watchDelay", "~m watchTick"],
    "GrantTask": ["+f key", "~c ", "+m later", "-m later", "~m grantNow", "~m step", "~m run"],   # later: void -> boolean; run: FIX ROUND EPOCH
    "MenuCfg": ["+f HOTKEY_GAP_MS", "+f HOTKEY_COOLDOWN_MS", "+m num", "~m load", "~<clinit>", "~m init"],  # FIX ROUND: the hotkey timing rows (init: the inlined config.properties template text only)
    "MenuReady": ["~m accept"],
    "GivenTick": ["~m run"],
    "SeenTick": ["~m run"],
    "SkyyMenuPlugin": ["~m setup", "~m shutdown"],
    "MenuData": ["+f HOTKEY_KEY", "~<clinit>"],                                  # the switch key, the settings tables, the Mods line
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header", "~<clinit>"],  # the kit's lock-free bridge + the version / template texts
    "CfgFile": ["~m schedule", "~<clinit>"],                                     # 0.3.19 B: the kit's save task on SkyyMenu-IO; FIX ROUND: the template text
    "CfgFn": ["~m opExport"],                                                    # the version text
    "SetDefCfg": [],                                                             # placeholder: removed below when identical
}


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


class Eng(object):
    pass


def engine(scratch, hcls):
    """the SkyyMenu 0.3.18 harness's 0.7.0 engine stand-ins (+ a recording executor and an ArchetypeChunk helper)"""
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JString
    E = Eng()
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    E.U = U

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    E.jf = jf
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
    hclass("skyymenu19.Net", PH + "server.core.io.PacketHandler",
           "public Net() { super((" + PH + "protocol.io.ChannelConnection) null, (" + PH + "server.core.io.ProtocolVersion) null); }",
           ["public java.util.ArrayList sent;"],
           ["public void rec(Object p) { if (this.sent == null) this.sent = new java.util.ArrayList(); this.sent.add(p); }",
            "public boolean writePacket(" + PH + "protocol.ToClientPacket p, boolean c) { rec(p); return true; }",
            "public void write(" + PH + "protocol.ToClientPacket p) { rec(p); }",
            "public void write(" + PH + "protocol.ToClientPacket[] ps) { for (int i = 0; i < ps.length; i++) rec(ps[i]); }",
            "public void write(" + PH + "protocol.ToClientPacket[] ps, " + PH + "protocol.ToClientPacket p) { for (int i = 0; i < ps.length; i++) rec(ps[i]); rec(p); }",
            "public void writeNoCache(" + PH + "protocol.ToClientPacket p) { rec(p); }",
            "public void accept(" + PH + "protocol.ToServerPacket p) { }",
            "public String getIdentifier() { return \"skyymenu19\"; }"])
    hclass(PH + "component.SkyyMenu19Store", PH + "component.Store",
           "public SkyyMenu19Store() { super((" + PH + "component.ComponentRegistry) null, 0, (Object) null, (" + PH + "component.IResourceStorage) null); }",
           ["public java.util.IdentityHashMap comps;"],
           ["public java.util.Map row(" + PH + "component.Ref r) {\n"
            "  if (this.comps == null) this.comps = new java.util.IdentityHashMap();\n"
            "  java.util.Map m = (java.util.Map) this.comps.get(r);\n"
            "  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }\n  return m;\n}",
            "public " + PH + "component.Component getComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t) {\n"
            "  return (" + PH + "component.Component) row(r).get(t);\n}"])
    hclass("skyymenu19.World", PH + "server.core.universe.world.World",
           "public World() { super((String) null, (java.nio.file.Path) null, (" + PH + "server.core.universe.world.WorldConfig) null); }",
           ["public java.util.concurrent.ConcurrentLinkedQueue tasks;", "public java.util.ArrayList by;"],
           ["public void execute(java.lang.Runnable r) {\n"
            "  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
            "  if (this.by == null) this.by = new java.util.ArrayList();\n"
            "  this.tasks.add(r);\n  synchronized (this.by) { this.by.add(Thread.currentThread().getName()); }\n}"])
    hclass("skyymenu19.Uni", PH + "server.core.universe.Universe", "public Uni() { super((" + PH + "server.core.plugin.JavaPluginInit) null); }",
           ["public static " + PH + "server.core.universe.world.World DEF;", "public static java.util.ArrayList PL;"],
           ["public " + PH + "server.core.universe.world.World getDefaultWorld() { return DEF; }",
            "public java.util.List getPlayers() { return PL == null ? new java.util.ArrayList() : PL; }"])
    hclass("skyymenu19.Cmd", PH + "server.core.command.system.AbstractCommand", "public Cmd() { super(\"x\", \"y\"); }", [],
           ["public boolean hasPermission(" + PH + "server.core.command.system.CommandSender s) { return true; }",
            "protected java.util.concurrent.CompletableFuture execute(" + PH + "server.core.command.system.CommandContext c) { return null; }"])
    hclass("skyymenu19.Cmds", PH + "server.core.command.system.CommandManager", "public Cmds() { super(); }",
           ["public java.util.HashMap cmds;", "public java.util.ArrayList lines;"],
           ["public " + PH + "server.core.command.system.AbstractCommand resolveCommand(String n) {\n"
            "  return this.cmds == null ? null : (" + PH + "server.core.command.system.AbstractCommand) this.cmds.get(n);\n}",
            "public java.util.concurrent.CompletableFuture handleCommand(" + PH + "server.core.command.system.CommandSender s, String line) {\n"
            "  if (this.lines == null) this.lines = new java.util.ArrayList();\n  this.lines.add(line);\n"
            "  return new java.util.concurrent.CompletableFuture();\n}"])
    hclass("skyymenu19.ItemMap", PH + "assetstore.map.DefaultAssetMap", "public ItemMap() { super(); }",
           ["public " + PH + "assetstore.JsonAsset item;"],
           ["public " + PH + "assetstore.JsonAsset getAsset(Object k) { return this.item; }"])
    hclass("skyymenu19.Items", PH + "assetstore.AssetStore", "public Items() { super((" + PH + "assetstore.AssetStore$Builder) null); }",
           ["public " + PH + "assetstore.AssetMap map;"],
           ["public " + PH + "assetstore.AssetMap getAssetMap() { return this.map; }"])
    # a RECORDING one-thread scheduler (stands in for SkyyMenu-IO / the page scheduler): keeps (task, delay ms), runs nothing
    hclass("skyymenu19.RecEx", "java.util.concurrent.ScheduledThreadPoolExecutor", "public RecEx() { super(1); }",
           ["public java.util.ArrayList tasks;", "public java.util.ArrayList delays;"],
           ["public synchronized void keep(Runnable r, long ms) {\n"
            "  if (this.tasks == null) { this.tasks = new java.util.ArrayList(); this.delays = new java.util.ArrayList(); }\n"
            "  this.tasks.add(r);\n  this.delays.add(Long.valueOf(ms));\n}",
            "public java.util.concurrent.ScheduledFuture schedule(Runnable r, long d, java.util.concurrent.TimeUnit u) { keep(r, u.toMillis(d)); return null; }",
            "public java.util.concurrent.ScheduledFuture scheduleWithFixedDelay(Runnable r, long a, long b, java.util.concurrent.TimeUnit u) { keep(r, -u.toMillis(b)); return null; }",
            "public java.util.concurrent.ScheduledFuture scheduleAtFixedRate(Runnable r, long a, long b, java.util.concurrent.TimeUnit u) { keep(r, -u.toMillis(b)); return null; }"])
    E.JC = JClass
    UUID, Paths, ArrayList, HashMap, HashSet = (JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"),
                                                JClass("java.util.HashMap"), JClass("java.util.HashSet"))
    E.UUID, E.Paths, E.ArrayList, E.HashMap = UUID, Paths, ArrayList, HashMap
    JClass(PH + "server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    HSV = JClass(PH + "server.core.HytaleServer")
    hs = U.allocateInstance(HSV.class_)
    jf(HSV.class_, "eventBus").set(hs, JClass(PH + "event.EventBus")(False))
    jf(HSV.class_, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
    jf(HSV.class_, "instance").set(None, hs)
    JClass(PH + "server.core.asset.AssetRegistryLoader").init()
    E.NET, E.TSC, E.HW = JClass("skyymenu19.Net"), JClass(PH + "component.SkyyMenu19Store"), JClass("skyymenu19.World")
    E.RecEx = JClass("skyymenu19.RecEx")
    PMc = JClass(PH + "server.core.entity.entities.player.pages.PageManager")
    WMc = JClass(PH + "server.core.entity.entities.player.windows.WindowManager")
    UniC, UniH = JClass(PH + "server.core.universe.Universe"), JClass("skyymenu19.Uni")
    EMc = JClass(PH + "server.core.modules.entity.EntityModule")
    ESc = JClass(PH + "server.core.universe.world.storage.EntityStore")
    STc = JClass(PH + "component.Store")
    CTc = JClass(PH + "component.ComponentType")
    REFc = JClass(PH + "component.Ref")
    PLAc = JClass(PH + "server.core.entity.entities.Player")
    PR = JClass(PH + "server.core.universe.PlayerRef")
    E.PMc, E.REFc, E.PLAc, E.PR, E.STc, E.ESc = PMc, REFc, PLAc, PR, STc, ESc
    E.CPE = JClass(PH + "protocol.packets.interface_.CustomPageEvent")
    E.CPT = JClass(PH + "protocol.packets.interface_.CustomPageEventType")
    CMGRc = JClass(PH + "server.core.command.system.CommandManager")
    PMOD = JClass(PH + "server.core.permissions.PermissionsModule")
    WCFG = JClass(PH + "server.core.universe.world.WorldConfig")
    nxt = [900]

    def ctype():
        c = CTc()
        nxt[0] += 1
        jf(CTc.class_, "index").setInt(c, nxt[0])
        jf(CTc.class_, "hashCode").setInt(c, nxt[0])
        return c
    CT_PR, CT_PLA, CT_TP, CT_TC, CT_HR, CT_MSC = ctype(), ctype(), ctype(), ctype(), ctype(), ctype()
    E.CT_PLA, E.CT_PR, E.CT_MSC = CT_PLA, CT_PR, CT_MSC
    uni = U.allocateInstance(UniH.class_)
    jf(UniC.class_, "playerRefComponentType").set(uni, CT_PR)
    WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
    jf(UniC.class_, "worldsByUuid").set(uni, WORLDS)
    jf(UniC.class_, "worlds").set(uni, JClass("java.util.concurrent.ConcurrentHashMap")())
    E.PLAYERS = ArrayList()
    jf(UniC.class_, "players").set(uni, E.PLAYERS)
    jf(UniC.class_, "playersByUuid").set(uni, JClass("java.util.concurrent.ConcurrentHashMap")())
    jf(UniC.class_, "instance").set(None, uni)
    UniH.PL = ArrayList()
    E.UniH = UniH
    em = U.allocateInstance(EMc.class_)
    for fn_, ct_ in (("playerComponentType", CT_PLA), ("teleportComponentType", CT_TP), ("transformComponentType", CT_TC),
                     ("headRotationComponentType", CT_HR)):
        jf(EMc.class_, fn_).set(em, ct_)
    for f_ in EMc.class_.getDeclaredFields():           # the movement states component type (its field name differs between builds)
        if str(f_.getType().getName()) == PH + "component.ComponentType" and "ovementStates" in str(f_.getName()):
            f_.setAccessible(True)
            f_.set(em, CT_MSC)
    jf(EMc.class_, "instance").set(None, em)
    MSCc = JClass(PH + "server.core.entity.movement.MovementStatesComponent")
    E.MSCc = MSCc
    E.MSC_TYPE_OK = MSCc.getComponentType() == CT_MSC

    def mkworld(name):
        w = U.allocateInstance(E.HW.class_)
        wu = UUID.randomUUID()
        jf(JClass(PH + "server.core.universe.world.World").class_, "name").set(w, name)
        cfg = U.allocateInstance(WCFG.class_)
        jf(JClass(PH + "server.core.universe.world.World").class_, "worldConfig").set(w, cfg)
        WORLDS.put(wu, w)
        return w, wu
    E.W1, E.W1U = mkworld("harness_home")
    E.W2, E.W2U = mkworld("harness_other")
    UniH.DEF = E.W1
    CM = U.allocateInstance(JClass("skyymenu19.Cmds").class_)
    CM.cmds = HashMap()
    CM.lines = ArrayList()
    for cn_ in ("island", "hub", "sacks", "accessories", "skymenu", "spawn", "bank", "skills"):
        CM.cmds.put(cn_, U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    jf(CMGRc.class_, "instance").set(None, CM)
    E.CM = CM
    ITc = JClass(PH + "server.core.asset.type.item.config.Item")
    IMAP = U.allocateInstance(JClass("skyymenu19.ItemMap").class_)
    IMAP.item = U.allocateInstance(ITc.class_)
    ISTORE = U.allocateInstance(JClass("skyymenu19.Items").class_)
    ISTORE.map = IMAP
    jf(ITc.class_, "ASSET_STORE").set(None, ISTORE)
    E.PLAIN = UUID.fromString("00000000-0000-0000-0000-0000000000c1")
    E.OP = UUID.fromString("00000000-0000-0000-0000-0000000000c2")
    USERS = {str(E.PLAIN): ["hytale:Adventurer"], str(E.OP): ["hytale:Admin"]}
    GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

    def jset(*xs):
        st_ = HashSet()
        for x in xs:
            st_.add(x)
        return st_

    @JImplements(PH + "server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "menu0319-test"
        @JOverride
        def getUserPermissions(self, u): return jset()
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(str(u), ["hytale:Adventurer"]))
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
    E.prov = Prov()
    pmod = U.allocateInstance(PMOD.class_)
    provs = ArrayList()
    provs.add(E.prov)
    jf(PMOD.class_, "providers").set(pmod, provs)
    jf(PMOD.class_, "virtualGroups").set(pmod, HashMap())
    jf(PMOD.class_, "instance").set(None, pmod)
    INVN = PH + "server.core.inventory.InventoryComponent"
    INVc = JClass(PH + "server.core.inventory.Inventory")
    JShort = jpype.JShort

    class Pl:
        pass

    def player(uid=None, world_u=None, world=None, name="SkyyHarness"):
        P = Pl()
        uid = uid or E.PLAIN
        P.pr = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(P.pr, uid)
        jf(PR.class_, "username").set(P.pr, name)
        P.net = U.allocateInstance(E.NET.class_)
        jf(PR.class_, "packetHandler").set(P.pr, P.net)
        jf(PR.class_, "worldUuid").set(P.pr, world_u or E.W1U)
        P.pl = U.allocateInstance(PLAc.class_)
        P.wm = WMc()
        P.wm.init(P.pr)
        P.pm = PMc()
        P.pm.init(P.pr, P.wm)
        jf(PLAc.class_, "windowManager").set(P.pl, P.wm)
        jf(PLAc.class_, "pageManager").set(P.pl, P.pm)
        inv = INVc()
        P.slots = {}
        for fld, kind, n in (("storage", "Storage", 36), ("hotbar", "Hotbar", 9), ("backpack", "Backpack", 0), ("utility", "Utility", 4),
                             ("tools", "Tool", 4), ("armor", "Armor", 4)):
            c_ = JClass(INVN + "$" + kind)(JShort(n))
            jf(INVc.class_, fld).set(inv, c_)
            P.slots[fld] = c_
        jf(PLAc.class_, "inventory").set(P.pl, inv)
        P.inv = inv
        st = U.allocateInstance(E.TSC.class_)
        ref = U.allocateInstance(REFc.class_)
        jf(REFc.class_, "store").set(ref, st)
        jf(REFc.class_, "index").setInt(ref, 7)
        st.row(ref).put(CT_PR, P.pr)
        st.row(ref).put(CT_PLA, P.pl)
        es = U.allocateInstance(ESc.class_)
        jf(ESc.class_, "world").set(es, world or E.W1)
        jf(STc.class_, "externalData").set(st, es)
        P.ref, P.st = ref, st
        jf(PR.class_, "entity").set(P.pr, P.ref)
        P.seen = 0
        return P
    E.player = player

    def sent(P):
        return [] if P.net.sent is None else [P.net.sent.get(i) for i in range(int(P.net.sent.size()))]
    E.sent = sent

    def kinds(P, frm=0):
        return [str(p.getClass().getSimpleName()) for p in sent(P)[frm:]]
    E.kinds = kinds

    def pump(P):
        for p in sent(P)[P.seen:]:
            if str(p.getClass().getSimpleName()) in ("CustomPage", "SetPage"):
                P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Acknowledge, None))
        P.seen = len(sent(P))
    E.pump = pump

    def run_world(w):
        n = 0
        while w.tasks is not None and not w.tasks.isEmpty():
            w.tasks.poll().run()
            n += 1
        return n
    E.run_world = run_world

    def queued(w):
        return [] if w.tasks is None else [str(t.getClass().getSimpleName()) for t in w.tasks.toArray()]
    E.queued = queued
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

    def strs_of(P, frm=0):
        acc = []
        for p in sent(P)[frm:]:
            deep(p, acc)
        return "\n".join(acc)
    E.strs_of = strs_of

    def count(P, iid):
        n = 0
        for c_ in P.slots.values():
            ic = c_.getInventory()
            for i in range(int(ic.getCapacity())):
                s_ = ic.getItemStack(JShort(i))
                if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == iid:
                    n += int(s_.getQuantity())
        return n
    E.count = count
    return E


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JString, JObject
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls], verify=True)
    E = engine(scratch, hcls)
    L = {"new": loader_for(jar), "old": loader_for(OLD_JAR)}

    def JV(k, n):
        return JClass(PKG + n, loader=L[k])
    Sys = JClass("java.lang.System")
    Paths = E.Paths
    mods = os.path.join(scratch, "world", "mods")
    for k in ("new", "old"):
        JV(k, "PageGuard").STOP = False
        JV(k, "PageGuard").EXEC = None
        JV(k, "SetStore").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "settings-" + k))
        JV(k, "Tips").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "notips-" + k))
        JV(k, "PetTile").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyPets", "pets"))
        JV(k, "MenuLayout").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "layouts-" + k))
        JV(k, "MenuLayout").DEF_FILE = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "layout-default-" + k + ".properties"))
        JV(k, "Given").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "given-profile-" + k))
        JV(k, "Given").LEGACY = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "given-" + k))
        JV(k, "AdmSaveTask").BASE = Paths.get(os.path.join(mods, "Skyy_SkyyMenu-" + k))
        JV(k, "AdmSaveTask").ensureDirs()
    K.check(bool(E.MSC_TYPE_OK), "X: the stand-in EntityModule hands out the movement states component type")
    BR = Sys.getProperties().get("skyy.bridge")
    if BR is None:
        BR = JClass("java.util.concurrent.ConcurrentHashMap")()
        Sys.getProperties().put("skyy.bridge", BR)
    for k in ("new", "old"):
        JV(k, "SetReg").registerOwn()
    MIO = JV("new", "MenuIO")

    def rec_io():
        """SkyyMenu-IO replaced by a RECORDING executor (tasks kept, nothing run)"""
        r = E.RecEx()
        MIO.begin()
        MIO.EX = r
        return r

    def io_tasks(r, frm=0):
        if r.tasks is None:
            return []
        return [(str(r.tasks.get(i).getClass().getSimpleName()), int(r.delays.get(i))) for i in range(int(r.tasks.size()))][frm:]

    def run_io(r, name=None, once=False):
        """run (and drop) the recorded tasks, oldest first (only those of class `name` when given; only the first one when once) -
        what SkyyMenu-IO would do"""
        n = 0
        while r.tasks is not None and r.tasks.size() > 0 and not (once and n >= 1):
            idx = None
            for i in range(int(r.tasks.size())):
                if name is None or str(r.tasks.get(i).getClass().getSimpleName()) == name:
                    idx = i
                    break
            if idx is None:
                break
            ts_ = [r.tasks.get(i) for i in range(int(r.tasks.size()))]
            ds_ = [r.delays.get(i) for i in range(int(r.delays.size()))]
            t = ts_.pop(idx)
            ds_.pop(idx)
            r.tasks.clear()
            r.delays.clear()
            for x_, y_ in zip(ts_, ds_):
                r.tasks.add(x_)
                r.delays.add(y_)
            t.run()
            n += 1
        return n

    # ------------------------------------------------------------------ SCAN: who reads HytaleServer.SCHEDULED_EXECUTOR
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    BOS, PS = JClass("java.io.ByteArrayOutputStream"), JClass("java.io.PrintStream")

    def readers(jar_, needle):
        p_ = JClass("javassist.ClassPool")(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(jar_)
        out_ = set()
        for n in zipfile.ZipFile(jar_).namelist():
            if not n.endswith(".class"):
                continue
            c = p_.get(n[:-6].replace("/", "."))
            for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
                bos = BOS()
                try:
                    IP(PS(bos)).print_(m)
                except Exception:
                    continue
                if needle in str(bos.toString()):
                    out_.add("%s.%s" % (n[:-6].rsplit("/", 1)[-1], m.getName()))
        return out_
    sx_new, sx_old = readers(jar, "HytaleServer.SCHEDULED_EXECUTOR"), readers(OLD_JAR, "HytaleServer.SCHEDULED_EXECUTOR")
    gone = sorted(sx_old - sx_new)
    K.eq(gone, sorted(["SetStore.saveSoon", "SetLoadTask.preload", "MenuLayout.preload", "MenuLayout.saveSoon", "AdmSaveTask.save",
                       "Given.schedule", "GrantTask.later", "CfgFile.schedule"]),
         "SCAN: the file / grant / kit-save tasks no longer touch HytaleServer.SCHEDULED_EXECUTOR (0.3.18 = CONTROL)")
    K.eq(sorted(sx_new - sx_old), [], "SCAN: nothing new on HytaleServer.SCHEDULED_EXECUTOR")
    K.check(all(not x.startswith(("SetStore", "MenuLayout", "AdmSaveTask", "Given", "GrantTask", "Cfg", "GivenTick", "SeenTick", "MenuIdx",
                                    "MenuIO", "GivenSave", "MenuHotkey", "HotkeyOpen")) for x in sx_new),
            "SCAN: what still reads it = the page timers + setup's PageGuard.EXEC only: %s" % sorted(sx_new))
    K.check("SkyyMenuPlugin.setup" in sx_new, "SCAN: setup still hands the page timers the shared scheduler (PageGuard.EXEC)")
    br_scans = sorted(x for x in readers(jar, "Map.keySet") if x in ("SetReg.drain", "MenuIdx.scan", "AdminPage.cfgMods", "SetReg.drainIdx"))
    K.eq(br_scans, ["MenuIdx.scan", "SetReg.drain"], "SCAN: the bridge key-set scans are setup's drain + MenuIdx.scan (AdminPage.cfgMods and "
         "the page drain read the index)")

    # ------------------------------------------------------------------ BRIDGE
    MU = JV("new", "MenuUtil")
    MU.BRIDGE = None
    m1 = MU.bridge()
    K.check(Sys.identityHashCode(m1) == Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) and Sys.identityHashCode(MU.BRIDGE) == Sys.identityHashCode(m1),
            "BRIDGE: MenuUtil.bridge() = the System property map, cached in BRIDGE")

    def run_bg(fn):
        box = {}

        def t():
            try:
                box["r"] = fn()
            except Exception as e:
                box["e"] = str(e)[:300]
        th = threading.Thread(target=t, daemon=True)
        th.start()
        return th, box
    with jpype.synchronized(Sys.class_):
        th, box = run_bg(lambda: MU.bridge())
        th.join(5.0)
        K.check(not th.is_alive() and Sys.identityHashCode(box.get("r")) == Sys.identityHashCode(m1), "BRIDGE: answers while System.class's monitor is held")
        th2, _b2 = run_bg(lambda: JV("old", "MenuUtil").bridge())
        th2.join(0.6)
        K.check(th2.is_alive(), "BRIDGE CONTROL: 0.3.18 waits for System.class's monitor")
    th2.join(5.0)

    # ------------------------------------------------------------------ IO: the real SkyyMenu-IO thread
    MIO.stop(500)
    MIO.begin()
    MIO.EX = None
    names = []

    @JImplements("java.lang.Runnable")
    class Probe:
        def __init__(self, tag):
            self.tag = tag

        @JOverride
        def run(self):
            t = JClass("java.lang.Thread").currentThread()
            names.append((self.tag, str(t.getName()), bool(t.isDaemon()), bool(MIO.onIO())))
    K.check(bool(MIO.schedule(Probe("a"), 0)), "IO: schedule accepted")
    fut = MIO.every(Probe("b"), 10, 30)
    time.sleep(0.4)
    K.check(fut is not None and len([n for n in names if n[0] == "b"]) >= 3, "IO: every() runs repeatedly (%d)" % len([n for n in names if n[0] == "b"]))
    fut.cancel(False)
    K.check(names and all(n[1] == "SkyyMenu-IO" and n[2] and n[3] for n in names), "IO: every task runs on the daemon thread SkyyMenu-IO: %s" % names[:3])
    del names[:]
    K.check(bool(MIO.schedule(Probe("late"), 300)), "IO: a task 300 ms later accepted")
    t0 = time.time()
    MIO.stop(2000)
    K.check([n[0] for n in names] == ["late"] and time.time() - t0 >= 0.2, "IO: stop() lets the pending task (a save) run first: %s" % names)
    K.check(not bool(MIO.schedule(Probe("x"), 0)) and MIO.every(Probe("y"), 0, 10) is None and bool(MIO.STOPPED),
            "IO: after stop() nothing is taken (the callers' inline fallback runs)")
    MIO.begin()
    del names[:]
    K.check(bool(MIO.schedule(Probe("again"), 0)), "IO: begin() takes tasks again")
    time.sleep(0.3)
    K.eq([n[0] for n in names], ["again"], "IO: ... and runs them")
    MIO.stop(1000)

    # ------------------------------------------------------------------ WRITES on the recording SkyyMenu-IO
    r = rec_io()
    SS, SLT, ML, AST, GV, MI, CFF = (JV("new", "SetStore"), JV("new", "SetLoadTask"), JV("new", "MenuLayout"), JV("new", "AdmSaveTask"),
                                     JV("new", "Given"), JV("new", "MenuIdx"), JV("new", "CfgFile"))
    PW = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000d1"))
    uw = PW.pr.getUuid()
    SLT.preload(PW.pr)
    K.eq(io_tasks(r), [("SetLoadTask", 0)], "WRITES: the settings join preload -> SetLoadTask on SkyyMenu-IO at once")
    run_io(r)
    res = int(SS.set(uw, "menu.tooltips", False, False))
    K.eq(io_tasks(r), [("SetSaveTask", 500)], "WRITES: a settings change -> SetSaveTask on SkyyMenu-IO, 500 ms (%d)" % res)
    sf = os.path.join(mods, "Skyy_SkyyMenu", "settings-new", str(uw) + ".properties")
    K.check(not os.path.exists(sf), "WRITES: nothing written before the task runs")
    run_io(r)
    K.check(os.path.exists(sf) and "menu.tooltips=false" in open(sf).read(), "WRITES: the task writes the player's settings file")
    # the same change on 0.3.18 writes the same bytes (its scheduler is the shared one: run it by hand via saveNow)
    SSo = JV("old", "SetStore")
    SSo.NAMES.put(str(uw), "SkyyHarness")
    SS.NAMES.put(str(uw), "SkyyHarness")
    SSo.set(uw, "menu.tooltips", False, False)
    SSo.saveNow(str(uw))
    SS.saveNow(str(uw))
    sfo = os.path.join(mods, "Skyy_SkyyMenu", "settings-old", str(uw) + ".properties")
    K.eq(open(sf, "rb").read(), open(sfo, "rb").read(), "WRITES: the settings file = 0.3.18's byte for byte")
    ML.preload(uw)
    K.eq(io_tasks(r), [("LayoutSaveTask", 0)], "WRITES: the layout join preload -> LayoutSaveTask(load) on SkyyMenu-IO")
    run_io(r)
    ML.saveSoon(str(uw))
    K.eq(io_tasks(r), [("LayoutSaveTask", 300)], "WRITES: a layout change -> LayoutSaveTask on SkyyMenu-IO, 300 ms")
    run_io(r)
    AST.save("exports/harness.txt", "hello")
    K.eq(io_tasks(r), [("AdmSaveTask", 0)], "WRITES: a Server Setup export -> AdmSaveTask on SkyyMenu-IO")
    run_io(r)
    ef = os.path.join(mods, "Skyy_SkyyMenu-new", "exports", "harness.txt")
    K.check(os.path.exists(ef) and open(ef).read() == "hello", "WRITES: the export file written")
    CFF.schedule(0, 75)
    K.eq(io_tasks(r), [("CfgSaveTask", 75)], "WRITES: SkyyMenu's own Server Setup row save (the kit's CfgSaveTask) -> SkyyMenu-IO, same delay")
    r.tasks.clear()
    r.delays.clear()
    GV.markLater("00000000-0000-0000-0000-0000000000d1")
    K.eq(io_tasks(r), [("GivenSave", 0)], "WRITES: a menu-item record -> GivenSave on SkyyMenu-IO")
    run_io(r)
    gf = os.path.join(mods, "Skyy_SkyyMenu", "given-profile-new", "00000000-0000-0000-0000-0000000000d1.txt")
    K.check(os.path.exists(gf) and open(gf).read().startswith("menu item given "), "WRITES: GivenSave writes the record (0.3.18's text)")
    MI.SET = None
    MI.prime()
    K.eq(io_tasks(r), [("MenuIdx", 0)], "WRITES: the index build at the first arrival -> MenuIdx on SkyyMenu-IO")
    run_io(r)
    K.check(MI.SET is not None and int(MI.SCANS) >= 1, "WRITES: ... and it builds the index")
    # MenuIO stopped -> the inline fallbacks (0.3.18's refused path)
    MIO.stop(100)
    res = int(SS.set(uw, "menu.tooltips", True, False))
    K.check("menu.tooltips=true" in open(sf).read(), "WRITES: MenuIO stopped - the settings save runs inline (0.3.18's refused path)")
    ML.saveSoon(str(uw))
    K.check(not ML.DIRTY.containsKey(str(uw)), "WRITES: MenuIO stopped - the layout save runs inline")
    AST.save("exports/harness2.txt", "two")
    K.check(os.path.exists(os.path.join(mods, "Skyy_SkyyMenu-new", "exports", "harness2.txt")), "WRITES: MenuIO stopped - the export runs inline")
    GV.markLater("00000000-0000-0000-0000-0000000000d2")
    K.check(os.path.exists(gf.replace("d1.txt", "d2.txt")), "WRITES: MenuIO stopped - the record is written inline")
    JV("new", "CfgPub").start(Paths.get(mods), None)          # the kit started on the scratch world (the row save then really runs)
    CFF.schedule(0, 400)
    K.check(any(str(t.getName()) == "SkyyCfg-SkyyMenu" for t in JClass("java.lang.Thread").getAllStackTraces().keySet()),
            "WRITES: MenuIO stopped - the kit's own fallback thread (SkyyCfg-SkyyMenu) takes the row save")
    MIO.begin()
    r = rec_io()

    # ------------------------------------------------------------------ GRANT (IO and world steps driven by hand)
    GT, GVn, MC = JV("new", "GrantTask"), JV("new", "Given"), JV("new", "MenuCfg")
    GTo, GVo = JV("old", "GrantTask"), JV("old", "Given")
    keys = {}
    calls = [0]

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            calls[0] += 1
            return keys.get(str(u), str(u))
    BR = Sys.getProperties().get("skyy.bridge")
    BR.put("profile:fn:key", KeyFn())

    def item_count(P):
        return E.count(P, "Skyy_Menu")

    def recs(k):
        d = os.path.join(mods, "Skyy_SkyyMenu", "given-profile-" + k)
        return sorted(os.listdir(d)) if os.path.isdir(d) else []

    def fresh_given(Gv):
        for m_ in (Gv.SESSION, Gv.INFLIGHT, Gv.CHECKED, Gv.READY, Gv.PENDING):
            m_.clear()
        try:
            Gv.EPOCH.clear()
        except Exception:
            pass
    # G1: the normal grant
    fresh_given(GVn)
    P1 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e1"))
    E.UniH.PL.clear()
    E.UniH.PL.add(P1.pr)
    E.W1.tasks = None
    K.check(bool(GVn.schedule(P1.pr, 4000)), "GRANT 1: Given.schedule claims the player")
    K.eq(io_tasks(r), [("GrantTask", 4000)], "GRANT 1: ONE GrantTask on SkyyMenu-IO, 4 s after the trigger (0.3.18's delay)")
    rec0 = recs("new")
    run_io(r)
    K.eq(E.queued(E.W1), ["GrantTask"], "GRANT 1: the IO step checked the files and hopped to the player's world thread")
    K.eq(item_count(P1), 0, "GRANT 1: no inventory change on the IO step")
    K.eq(recs("new"), rec0, "GRANT 1: no record yet")
    n0 = len(E.sent(P1))
    E.run_world(E.W1)
    K.eq(item_count(P1), 1, "GRANT 1: the world step gave ONE menu item")
    K.check("double-tap crouch" in E.strs_of(P1, n0) and "Hub hotkey switch is on in /settings" in E.strs_of(P1, n0),
            "GRANT 1: the chat line names the hotkey and its /settings switch")
    K.eq(io_tasks(r), [("GivenSave", 0)], "GRANT 1: the record is written back on SkyyMenu-IO")
    run_io(r)
    K.check(str(P1.pr.getUuid()) + ".txt" in recs("new"), "GRANT 1: the record exists")
    K.check(not GVn.PENDING.containsKey(P1.pr.getUuid()), "GRANT 1: PENDING released")
    K.check(not bool(GVn.wants(P1.pr.getUuid())), "GRANT 1: the profile's session mark is set")
    GVn.schedule(P1.pr, 4000)
    run_io(r, "GrantTask", once=True)
    K.eq((E.queued(E.W1), io_tasks(r), item_count(P1)), ([], [], 1), "GRANT 1: a second trigger this session does nothing (no world hop, no item)")
    r.tasks.clear()
    r.delays.clear()
    # G2: a recorded profile -> no world hop at all
    fresh_given(GVn)
    K.check(bool(GVn.schedule(P1.pr, 4000)), "GRANT 2: scheduled")
    run_io(r, "GrantTask")
    K.eq(E.queued(E.W1), [], "GRANT 2: the profile already has its record - nothing on the world thread")
    K.check(bool(GVn.SESSION.containsKey(str(P1.pr.getUuid()))), "GRANT 2: the session mark set on SkyyMenu-IO")
    # G3: an item already held, no record -> recorded (on IO), no second item
    fresh_given(GVn)
    P3 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e3"))
    P3.slots["hotbar"].getInventory().addItemStack(JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Skyy_Menu", 1))
    GVn.schedule(P3.pr, 4000)
    run_io(r, "GrantTask")
    E.run_world(E.W1)
    K.eq(item_count(P3), 1, "GRANT 3: an item already held - no second one")
    K.eq(io_tasks(r), [("GivenSave", 0)], "GRANT 3: ... and its record goes to SkyyMenu-IO")
    run_io(r)
    K.check(str(P3.pr.getUuid()) + ".txt" in recs("new"), "GRANT 3: the record exists")
    # G4: SkyyProfiles busy on the IO step -> retry on IO in 1 s, no world hop
    fresh_given(GVn)
    P4 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e4"))
    BR.put("profile:busy:" + str(P4.pr.getUuid()), True)
    GVn.schedule(P4.pr, 4000)
    run_io(r, "GrantTask", once=True)
    K.eq((E.queued(E.W1), io_tasks(r)), ([], [("GrantTask", 1000)]), "GRANT 4: SkyyProfiles busy - back on SkyyMenu-IO in 1 s, no world hop")
    BR.remove("profile:busy:" + str(P4.pr.getUuid()))
    run_io(r, "GrantTask")
    E.run_world(E.W1)
    K.eq(item_count(P4), 1, "GRANT 4: given once the profile settled")
    run_io(r)
    # G5: a profile switch between the IO step and the world step -> back to the file check with the new key
    fresh_given(GVn)
    P5 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e5"))
    u5 = str(P5.pr.getUuid())
    GVn.schedule(P5.pr, 4000)
    run_io(r, "GrantTask", once=True)
    keys[u5] = u5 + "-p2"
    E.run_world(E.W1)
    K.eq((item_count(P5), io_tasks(r)), (0, [("GrantTask", 1000)]), "GRANT 5: the profile switched before the world step - nothing given, "
         "back to SkyyMenu-IO (the key is checked on the world thread)")
    run_io(r, "GrantTask", once=True)
    E.run_world(E.W1)
    run_io(r)
    K.eq(item_count(P5), 1, "GRANT 5: given for the NEW profile")
    K.check(u5 + "-p2.txt" in recs("new") and u5 + ".txt" not in recs("new"), "GRANT 5: recorded under the new storage key")
    # G6: no world for the player -> retry; 30 tries at most, then PENDING released
    fresh_given(GVn)
    P6 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e6"), world_u=E.UUID.fromString("00000000-0000-0000-0000-00000000ffff"))
    GVn.schedule(P6.pr, 4000)
    n = 0
    while io_tasks(r) and n < 40:
        run_io(r, "GrantTask", once=True)
        n += 1
    K.check(n == 30 and not GVn.PENDING.containsKey(P6.pr.getUuid()) and E.queued(E.W1) == [],
            "GRANT 6: no world - retried on SkyyMenu-IO, at most 30 tries, then PENDING released (%d)" % n)
    # G7: GIVE_ITEM off -> nothing
    fresh_given(GVn)
    MC.GIVE_ITEM = False
    P7 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e7"))
    GVn.schedule(P7.pr, 4000)
    run_io(r, "GrantTask")
    K.eq((E.queued(E.W1), item_count(P7)), ([], 0), "GRANT 7: the menu item switched off - nothing, no world hop")
    MC.GIVE_ITEM = True
    # G8: legacy flag (0.1 - 0.3.3) migrated on the IO step
    fresh_given(GVn)
    P8 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e8"))
    os.makedirs(os.path.join(mods, "Skyy_SkyyMenu", "given-new"), exist_ok=True)
    open(os.path.join(mods, "Skyy_SkyyMenu", "given-new", str(P8.pr.getUuid()) + ".txt"), "w").write("x")
    GVn.schedule(P8.pr, 4000)
    run_io(r, "GrantTask")
    K.check(E.queued(E.W1) == [] and str(P8.pr.getUuid()) + ".txt" in recs("new") and item_count(P8) == 0,
            "GRANT 8: a 0.3.3 per-player flag is migrated on SkyyMenu-IO, nothing given, no world hop")
    # G9: MenuIO stopped -> the grant is not scheduled and the claim released
    fresh_given(GVn)
    MIO.stop(100)
    P9 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000e9"))
    K.check(not bool(GVn.schedule(P9.pr, 4000)) and not GVn.PENDING.containsKey(P9.pr.getUuid()), "GRANT 9: MenuIO stopped - not scheduled, PENDING released")
    MIO.begin()
    r = rec_io()
    # FIX ROUND 2: Given.claim (world thread, MenuReady) never takes the Given.class monitor the IO-thread file helpers hold
    fresh_given(GVn)
    _cm = [m_ for m_ in GVn.class_.getDeclaredMethods() if str(m_.getName()) == "claim"]
    K.check(len(_cm) == 1 and not jpype.JClass("java.lang.reflect.Modifier").isSynchronized(_cm[0].getModifiers()), "CLAIM: Given.claim is not synchronized (no Given.class monitor)")
    U_c = E.UUID.fromString("00000000-0000-0000-0000-0000000000c1")
    K.check(bool(GVn.claim(U_c, 1000)) and not bool(GVn.claim(U_c, 1000 + 89999)), "CLAIM: one claim per player within 90 s")
    K.check(bool(GVn.claim(U_c, 1000 + 90000)) and int(GVn.PENDING.get(U_c).longValue()) == 91000, "CLAIM: a 90 s old entry is stale and taken over")
    K.check(not bool(GVn.claim(None, 5)), "CLAIM: null player refused")
    _res = []
    def _hold_and_claim():
        import threading
        lk, done = threading.Event(), threading.Event()
        def _holder():
            with jpype.synchronized(GVn.class_):
                lk.set()
                done.wait(5)
        th = threading.Thread(target=_holder)
        th.start()
        lk.wait(5)
        t0 = time.time()
        U_d = E.UUID.fromString("00000000-0000-0000-0000-0000000000c2")
        _res.append(bool(GVn.claim(U_d, 2000)))
        _res.append(time.time() - t0)
        done.set()
        th.join(5)
    _hold_and_claim()
    K.check(_res[0] and _res[1] < 1.0, "CLAIM: claim answers at once while another thread holds the Given.class monitor (an IO-thread file write)")
    GVn.PENDING.clear()
    # CONTROL 0.3.18: the same normal grant gives the same item + record (its world step does the file checks)
    fresh_given(GVo)
    P10 = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000ea"))
    to = GTo(P10.pr)
    to.run()
    E.run_world(E.W1)
    K.check(item_count(P10) == 1 and str(P10.pr.getUuid()) + ".txt" in recs("old"), "GRANT CONTROL: 0.3.18 gives the same one item + record")

    # ------------------------------------------------------------------ EPOCH (GivenTick)
    E.UniH.PL.clear()
    E.PLAYERS.clear()
    pE = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000f1"))
    E.UniH.PL.add(pE.pr)
    E.PLAYERS.add(pE.pr)
    uE = pE.pr.getUuid()
    for k_ in ("new", "old"):
        fresh_given(JV(k_, "Given"))
        JV(k_, "Given").READY.put(uE, True)
        JV(k_, "Given").SESSION.put(str(uE), True)          # nothing to give: only the key-function calls are counted
    BR.put("profile:epoch:" + str(uE), JClass("java.lang.Long")(5))
    res = {}
    for k_ in ("new", "old"):
        tk = JV(k_, "GivenTick")()
        seq = []
        for step in ("first", "same", "same", "switch", "same", "noepoch", "noepoch"):
            if step == "switch":
                BR.put("profile:epoch:" + str(uE), JClass("java.lang.Long")(6))
            if step == "noepoch":
                BR.remove("profile:epoch:" + str(uE))
            c0 = calls[0]
            tk.run()
            seq.append(calls[0] - c0)
        BR.put("profile:epoch:" + str(uE), JClass("java.lang.Long")(5))
        res[k_] = seq
    K.eq(res["new"], [1, 0, 0, 1, 0, 1, 1], "EPOCH: 0.3.19 asks profile:fn:key on the first tick, at an epoch change, and every tick without an epoch")
    K.eq(res["old"], [1, 1, 1, 1, 1, 1, 1], "EPOCH CONTROL: 0.3.18 asks every tick")

    # ------------------------------------------------------------------ FIXR: the profile watch never uses up an epoch it did not act on
    GVn_, GTn_ = JV("new", "Given"), JV("new", "GrantTask")
    fresh_given(GVn_)
    GVn_.READY.put(uE, True)
    BR.put("profile:epoch:" + str(uE), JClass("java.lang.Long")(7))
    GVn_.PENDING.put(uE, JClass("java.lang.Long")(int(Sys.currentTimeMillis())))      # a task still pending (e.g. the join task)
    r.tasks = None
    r.delays = None
    tkE = JV("new", "GivenTick")()
    tkE.run()
    K.check(not GVn_.EPOCH.containsKey(uE) and io_tasks(r) == [], "FIXR: a refused schedule (task pending) forgets EPOCH, nothing queued")
    GVn_.PENDING.remove(uE)
    tkE.run()
    K.check(GVn_.EPOCH.containsKey(uE) and [t_ for t_ in io_tasks(r)] == [("GrantTask", 4000)],
            "FIXR: the next tick (pending gone) schedules the grant for the new profile: %s" % io_tasks(r))
    # a GrantTask that ends unfinished (its 30 tries used up) forgets EPOCH, so the profile watch tries again
    gtE = GTn_(pE.pr)
    gtE.tries = 29
    E.UniH.PL.clear()
    jf_wu = E.jf(E.PR.class_, "worldUuid")
    wu_keep = jf_wu.get(pE.pr)
    jf_wu.set(pE.pr, E.UUID.fromString("00000000-0000-0000-0000-00000000dead"))      # no such world -> later(1000) -> 30th try = give up
    GVn_.PENDING.put(uE, JClass("java.lang.Long")(int(Sys.currentTimeMillis())))
    gtE.run()
    jf_wu.set(pE.pr, wu_keep)
    K.check(not GVn_.PENDING.containsKey(uE) and not GVn_.EPOCH.containsKey(uE),
            "FIXR: a GrantTask that used up its 30 tries releases PENDING and forgets EPOCH")
    E.UniH.PL.add(pE.pr)
    r.tasks = None
    r.delays = None
    tkE.run()
    K.eq(io_tasks(r), [("GrantTask", 4000)], "FIXR: ... and the next profile-watch tick schedules it again")
    GVn_.SESSION.put(str(uE), True)
    gtE2 = GTn_(pE.pr)
    GVn_.EPOCH.put(uE, JClass("java.lang.Long")(7))
    GVn_.PENDING.put(uE, JClass("java.lang.Long")(int(Sys.currentTimeMillis())))
    gtE2.run()
    K.check(GVn_.EPOCH.containsKey(uE) and not GVn_.PENDING.containsKey(uE), "FIXR: a task that ends done (nothing wanted) keeps EPOCH")
    fresh_given(GVn_)
    BR.put("profile:epoch:" + str(uE), JClass("java.lang.Long")(5))

    # ------------------------------------------------------------------ WATCH: the menu's safety net backs off
    pex = E.RecEx()
    JV("new", "PageGuard").EXEC = pex
    PWt = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000a7"))
    pg = JV("new", "MenuPage")(PWt.pr, "main")
    PWt.pm.openCustomPage(PWt.ref, PWt.st, pg)
    E.pump(PWt)
    pg.lastSend = 0
    delays = []
    for _i in range(8):
        K.check(bool(pg.watchTick(E.W1)) and bool(pg.probeSeen), "WATCH: healthy check %d" % _i)
        delays.append(int(pg.watchDelay()))
    K.eq(delays, [1000, 1000, 2000, 2000, 2000, 2000, 2000, 2000], "WATCH: healthy checks back off 1 s -> 2 s, never more (fix round)")
    pg.lastSend = int(Sys.currentTimeMillis()) - 5000
    pg.watchTick(E.W1)
    K.eq(int(pg.watchDelay()), 1000, "WATCH: a page packet since the last check starts over at 1 s")
    for _i in range(6):
        pg.watchTick(E.W1)
    K.eq(int(pg.watchDelay()), 2000, "WATCH: backed off again (2 s at most)")
    # STUCK: an acknowledgement the client never sends -> healed at once, starts over
    jf_ack = E.jf(E.PMc.class_, "customPageRequiredAcknowledgments")
    jf_ack.get(PWt.pm).incrementAndGet()
    h0 = int(pg.heals)
    K.check(bool(pg.watchTick(E.W1)) and int(pg.heals) == h0 + 1 and int(jf_ack.get(PWt.pm).get()) >= 0, "WATCH: a stuck page is still healed at once")
    K.eq(int(pg.watchDelay()), 1000, "WATCH: ... and the checks start over at 1 s")
    E.pump(PWt)
    # MenuWatch's world step schedules the next check with watchDelay
    for _i in range(7):
        pg.watchTick(E.W1)
    pex.tasks = None
    pex.delays = None
    mw = JV("new", "MenuWatch")(pg, E.W1)
    mw.run()
    K.eq(io_tasks(pex), [("MenuWatch", int(pg.watchDelay()))], "WATCH: MenuWatch's world step schedules the next check after watchDelay (%d)" % int(pg.watchDelay()))
    JV("new", "PageGuard").EXEC = None

    # ------------------------------------------------------------------ INDEX
    MI.SET = None
    MI.CFG = None
    MI.BUSY.set(False)
    for kk in [str(k) for k in BR.keySet()]:
        if kk.startswith(("settings:def:", "config:def:", "config:fn:", "config:epoch:")):
            BR.remove(kk)
    JV("new", "CfgPub").publish()
    LB, LP = loader_for(BANK_JAR), loader_for(PROF_JAR)
    JClass("com.skyy.bank.CfgPub", loader=LB).publish()
    JClass("com.skyy.profiles.CfgPub", loader=LP).publish()
    BR.put("config:def:Junk", "not a header")
    BR.put("config:def:../bad", JArray(JObject)(3))
    for k_ in ("new", "old"):
        JV(k_, "SetReg").registerOwn()
    s0 = int(MI.SCANS)
    keys_ = list(MI.settingsKeys())
    K.check(int(MI.SCANS) == s0 + 1 and "settings:def:menu.hotkey" in keys_ and "settings:def:menu.tooltips" in keys_,
            "INDEX: the first use builds the index in place (the settings:def keys)")
    cm = list(MI.configMods())
    K.check(set(["SkyyMenu", "SkyyBank", "SkyyProfiles", "Junk", "../bad"]) <= set(cm), "INDEX: the config:def:<Mod> names: %s" % cm)
    r.tasks = None
    r.delays = None
    MI.settingsKeys()
    K.eq((int(MI.SCANS), io_tasks(r)), (s0 + 1, []), "INDEX: nothing changed - no rescan, no task")
    BR.put("settings:def:harness.extra", JArray(JObject)([JString("SkyyHarness"), JString("harness.extra"), JString("Extra"), JString("general"),
                                                         JClass("java.lang.Boolean").TRUE, JString("help")]))
    MI.AT = int(Sys.currentTimeMillis()) - 500
    MI.settingsKeys()
    K.eq(io_tasks(r), [], "INDEX: a new key within 2 s of the last scan - no rescan yet")
    MI.AT = int(Sys.currentTimeMillis()) - 3000
    MI.settingsKeys()
    K.eq(io_tasks(r), [("MenuIdx", 0)], "INDEX: a new key (bridge size changed) -> a rescan on SkyyMenu-IO")
    MI.settingsKeys()
    K.eq(len(io_tasks(r)), 1, "INDEX: one rescan queued at a time")
    run_io(r)
    K.check("settings:def:harness.extra" in list(MI.settingsKeys()), "INDEX: the rescan sees the new key")
    MI.AT = int(Sys.currentTimeMillis()) - 61000
    MI.settingsKeys()
    K.eq(io_tasks(r), [("MenuIdx", 0)], "INDEX: an index older than 60 s -> a rescan on SkyyMenu-IO")
    run_io(r)
    SRn = JV("new", "SetReg")
    SRn.DEFS.remove("harness.extra")
    SRn.drainIdx()
    K.check(SRn.DEFS.containsKey("harness.extra"), "INDEX: the Settings page's drainIdx registers a settings:def key put without register")
    APn, APo = JV("new", "AdminPage"), JV("old", "AdminPage")
    K.eq(list(APn.cfgMods()), list(APo.cfgMods()), "INDEX: AdminPage.cfgMods = 0.3.18's on the same bridge (real kit headers + junk)")
    K.check(set(list(APn.cfgMods())) >= set(["SkyyMenu", "SkyyBank", "SkyyProfiles"]), "INDEX: the three real kit mods listed: %s" % list(APn.cfgMods()))

    # ------------------------------------------------------------------ HOTKEY
    HK_, HO = JV("new", "MenuHotkey"), JV("new", "HotkeyOpen")
    MVS = JClass("com.hypixel.hytale.protocol.MovementStates")
    MCn = JV("new", "MenuCfg")
    GAP, CD = int(MCn.HOTKEY_GAP_MS), int(MCn.HOTKEY_COOLDOWN_MS)
    K.eq((GAP, CD), (400, 1500), "HOTKEY: 0.4 s between the presses, 1.5 s between opens (MenuCfg defaults)")

    def st3():
        return JArray(jpype.JLong)(3)

    def seq(events):
        s_ = st3()
        return [bool(HK_.step(s_, c_, ok_, t_)) for c_, ok_, t_ in events]
    K.eq(seq([(True, True, 1000), (False, True, 1100), (True, True, 1300)]), [False, False, True], "HOTKEY: two presses 0.3 s apart fire")
    K.eq(seq([(True, True, 1000), (False, True, 1100), (True, True, 1500)]), [False, False, False], "HOTKEY: 0.5 s apart - no (re-armed)")
    K.eq(seq([(True, True, 1000), (False, True, 1100), (True, True, 1500), (False, True, 1600), (True, True, 1800)]),
         [False, False, False, False, True], "HOTKEY: a slow second press re-arms, the next quick one fires")
    K.eq(seq([(True, True, 1000), (True, True, 1100), (True, True, 1200), (True, True, 1300)]), [False] * 4, "HOTKEY: holding crouch never fires")
    K.eq(seq([(True, True, 1000), (False, True, 1100), (True, False, 1200), (False, True, 1250), (True, True, 1300)]),
         [False, False, False, False, False], "HOTKEY: a press while not standing still disarms")
    K.eq(seq([(True, True, 1000), (False, True, 1050), (True, True, 1100), (False, True, 1150), (True, True, 1200), (False, True, 1250),
              (True, True, 1300), (False, True, 2650), (True, True, 2700), (False, True, 2750), (True, True, 2800)]),
         [False, False, True, False, False, False, False, False, False, False, True], "HOTKEY: 1.5 s cooldown between opens (a quick pair "
         "inside it only re-arms; the next pair after it fires)")
    K.eq(seq([(True, True, 5000), (False, True, 5050), (True, True, 4000)]), [False, False, False], "HOTKEY: a clock that went back never fires")
    # FIXR: the timing is live from MenuCfg (Server Setup)
    MCn.HOTKEY_GAP_MS = 200
    K.eq(seq([(True, True, 1000), (False, True, 1100), (True, True, 1300)]), [False, False, False], "FIXR: gap 200 ms - a 0.3 s pair no longer fires")
    K.eq(seq([(True, True, 1000), (False, True, 1050), (True, True, 1150)]), [False, False, True], "FIXR: gap 200 ms - a 0.15 s pair fires")
    MCn.HOTKEY_GAP_MS = 400
    MCn.HOTKEY_COOLDOWN_MS = 5000
    K.eq(seq([(True, True, 1000), (False, True, 1050), (True, True, 1100), (False, True, 1150), (True, True, 3000), (False, True, 3050),
              (True, True, 3100)]), [False, False, True, False, False, False, False], "FIXR: cooldown 5 s - a pair 2 s later does not fire")
    MCn.HOTKEY_COOLDOWN_MS = 1500
    # FIXR: MenuCfg.load reads + clamps hotkeyGapMs / hotkeyCooldownMs; the Server Setup header carries both rows
    cfgf = os.path.join(scratch, "fixr-config.properties")
    keepF = MCn.FILE
    for txt_, want_ in (("hotkeyGapMs=250\nhotkeyCooldownMs=3000\n", (250, 3000)), ("hotkeyGapMs=50\nhotkeyCooldownMs=99999\n", (200, 10000)),
                        ("hotkeyGapMs=abc\n", (400, 1500)), ("giveItem=true\n", (400, 1500))):
        open(cfgf, "w").write(txt_)
        MCn.FILE = E.Paths.get(cfgf)
        MCn.load()
        K.eq((int(MCn.HOTKEY_GAP_MS), int(MCn.HOTKEY_COOLDOWN_MS)), want_, "FIXR: config.properties %r -> %s" % (txt_.strip(), want_))
    MCn.FILE = keepF
    MCn.HOTKEY_GAP_MS = 400
    MCn.HOTKEY_COOLDOWN_MS = 1500
    JV("new", "CfgPub").publish()
    hdr = BR.get("config:def:SkyyMenu")
    rows_ = dict((str(rw[0]), [str(x) for x in rw]) for rw in hdr[7])
    K.check("menu.hotkeyGapMs" in rows_ and rows_["menu.hotkeyGapMs"][3:10] == ["int", "400", "200", "800", "step=50", "ms", "live,adv"],
            "FIXR: Server Setup row menu.hotkeyGapMs (int ms 200-800, default 400): %s" % rows_.get("menu.hotkeyGapMs"))
    K.check("menu.hotkeyCooldownMs" in rows_ and rows_["menu.hotkeyCooldownMs"][3:10] == ["int", "1500", "500", "10000", "step=100", "ms", "live,adv"],
            "FIXR: Server Setup row menu.hotkeyCooldownMs (int ms 500-10000, default 1500): %s" % rows_.get("menu.hotkeyCooldownMs"))
    K.check("hotkeyGapMs=400" in str(JV("new", "MenuData").MENU_CFG_TEXT) and "hotkeyCooldownMs=1500" in str(JV("new", "MenuData").MENU_CFG_TEXT),
            "FIXR: the config.properties template lists both")

    def mvs(**kw):
        m = MVS()
        m.onGround = True
        for k_, v_ in kw.items():
            setattr(m, k_, v_)
        return m
    K.check(bool(HK_.still(mvs())), "HOTKEY: still() on the ground")
    for fld in ("sprinting", "sliding", "rolling", "mantling", "climbing", "flying", "gliding", "swimming", "inFluid", "mounting", "sitting", "sleeping"):
        K.check(not bool(HK_.still(mvs(**{fld: True}))), "HOTKEY: not still while %s" % fld)
    K.check(not bool(HK_.still(mvs(onGround=False))) and not bool(HK_.still(None)), "HOTKEY: not still in the air / without states")
    K.check(HK_().getQuery() == E.CT_PLA, "HOTKEY: the system runs on every Player entity")
    K.check(str(JV("new", "MenuHotkey").class_.getSuperclass().getName()) == "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
            "HOTKEY: an EntityTickingSystem")
    # tick() through a stand-in chunk + store with the real MovementStatesComponent
    PH_ = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000b7"))
    msc = E.MSCc()
    ms_ = mvs()
    msc.setMovementStates(ms_)
    PH_.st.row(PH_.ref).put(E.CT_MSC, msc)
    ACH = JClass("com.hypixel.hytale.component.ArchetypeChunk")
    ch = E.U.allocateInstance(ACH.class_)
    E.jf(ACH.class_, "refs").set(ch, JArray(E.REFc)([PH_.ref]))
    E.jf(ACH.class_, "entitiesSize").setInt(ch, 1)
    sysm = HK_()
    HK_.ST.clear()
    HK_.ON = True
    E.W1.tasks = None
    for _i in range(30):
        sysm.tick(0.033, 0, ch, PH_.st, None)
    K.eq(int(HK_.ST.size()), 0, "HOTKEY: no state is kept for a player who never crouches")

    def tap():
        ms_.crouching = True
        sysm.tick(0.033, 0, ch, PH_.st, None)
        time.sleep(0.05)
        ms_.crouching = False
        sysm.tick(0.033, 0, ch, PH_.st, None)
        time.sleep(0.05)
    f0 = int(HK_.FIRED)
    tap()
    tap()
    K.eq((int(HK_.FIRED) - f0, E.queued(E.W1)), (1, ["HotkeyOpen"]), "HOTKEY: a double tap queues ONE HotkeyOpen on the player's world")
    K.check(PH_.pm.getCustomPage() is None, "HOTKEY: nothing opened inside the system's tick")
    E.run_world(E.W1)
    cp = PH_.pm.getCustomPage()
    K.check(cp is not None and str(cp.getClass().getName()) == PKG + "MenuPage" and str(cp.view) == "main" and "CustomPage" in E.kinds(PH_),
            "HOTKEY: HotkeyOpen opens the SkyWynn Menu (main view) through the real PageManager")
    E.pump(PH_)
    time.sleep(1.6)
    tap()
    tap()
    n1 = len(E.sent(PH_))
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() == cp and len(E.sent(PH_)) == n1, "HOTKEY: another page already open - nothing opened, nothing sent")
    PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    K.check(PH_.pm.getCustomPage() is None, "HOTKEY: (the page dismissed like Esc)")
    # FIXR: an open container window (getCustomPage() stays null) -> refused, nothing sent
    CWc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    wins_ = E.jf(E.JC("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager").class_, "windows").get(PH_.wm)
    wins_.put(jpype.JInt(5), E.U.allocateInstance(CWc.class_))
    rf0 = int(HO.REFUSED)
    n2 = len(E.sent(PH_))
    HO(PH_.pr).run()
    K.check(PH_.pm.getCustomPage() is None and len(E.sent(PH_)) == n2 and int(HO.REFUSED) == rf0 + 1,
            "FIXR: a container window open (no custom page) - the hotkey opens nothing, sends nothing, counts a refusal")
    wins_.remove(jpype.JInt(5))
    # FIXR: SkyyProfiles busy with the player -> refused
    BR.put("profile:busy:" + str(PH_.pr.getUuid()), True)
    HO(PH_.pr).run()
    K.check(PH_.pm.getCustomPage() is None and len(E.sent(PH_)) == n2 and int(HO.REFUSED) == rf0 + 2,
            "FIXR: profile:busy - the hotkey opens nothing (same rule as /skymenu)")
    BR.remove("profile:busy:" + str(PH_.pr.getUuid()))
    HO(PH_.pr).run()
    K.check(PH_.pm.getCustomPage() is not None and int(HO.REFUSED) == rf0 + 2, "FIXR: no window, not busy - it opens again")
    E.pump(PH_)
    PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    K.check(PH_.pm.getCustomPage() is None, "FIXR: (dismissed)")
    SS.set(PH_.pr.getUuid(), "menu.hotkey", False, False)
    time.sleep(1.6)
    tap()
    tap()
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is None, "HOTKEY: menu.hotkey OFF - nothing opens")
    SS.set(PH_.pr.getUuid(), "menu.hotkey", True, False)
    HK_.ON = False
    time.sleep(1.6)
    f1 = int(HK_.FIRED)
    tap()
    tap()
    K.check(int(HK_.FIRED) == f1 and E.queued(E.W1) == [], "HOTKEY: after shutdown (ON false) the system does nothing")
    HK_.ON = True
    K.check(int(HK_.ST.size()) == 1, "HOTKEY: one state for the crouching player")
    E.jf(E.REFc.class_, "index").setInt(PH_.ref, -2147483648)
    HK_.prune()
    K.eq(int(HK_.ST.size()), 0, "HOTKEY: prune drops a dead ref")
    SRn = JV("new", "SetReg")
    d = SRn.DEFS.get("menu.hotkey")
    K.check(d is not None and str(d[3]) == "general" and bool(d[4]) and str(d[0]) == "SkyyMenu", "HOTKEY: the switch menu.hotkey is registered (General, ON)")
    K.check("#menu.hotkey=true" in str(JV("new", "MenuData").SET_TEMPLATE), "HOTKEY: the defaults template lists it")
    K.check(bool(HO.wanted(E.UUID.fromString("00000000-0000-0000-0000-0000000000b8"))), "HOTKEY: a player who never chose = ON")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses_live")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls], verify=True)
    E = engine(scratch, hcls)
    Ln = loader_for(jar)

    def JV(n):
        return JClass(PKG + n, loader=Ln)
    Paths = E.Paths
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("Given").DIR = Paths.get(os.path.join(home, "given-profile"))
    JV("Given").LEGACY = Paths.get(os.path.join(home, "given"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    b0 = snap(home)
    res = []
    for n_ in range(2):
        JV("MenuIO").begin()
        for m_ in (ML.OWN, ML.NAMES, ML.DIRTY, ML.BROKEN, ML.WARNED, ML.ERRAT):
            m_.clear()
        ML.loadDefault()
        JV("SetReg").loadAdmin(True)
        JV("SetReg").registerOwn()
        JV("SetReg").drain()
        P = E.player(E.UUID.fromString("d8ddde89-98b2-4739-983e-a39773d582b6"))
        JV("SetLoadTask").preload(P.pr)
        ML.preload(P.pr.getUuid())
        pg = JV("MenuPage")(P.pr, "main")
        P.pm.openCustomPage(P.ref, P.st, pg)
        JV("MenuIdx").SET = None
        JV("MenuIdx").settingsKeys()
        time.sleep(0.8)
        ML.flushAll()
        JV("SetStore").flushAll()
        JV("MenuIO").stop(2000)
        res.append([P.pm.getCustomPage() == pg, snap(home) == b0])
    K.eq(res, [[True, True], [True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu (%d files): a menu opens, the preloads + index "
         "run on SkyyMenu-IO, no file written" % len(b0))
    K.save()


if __name__ == "__main__":
    EXPECT.pop("SetDefCfg", None)
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
