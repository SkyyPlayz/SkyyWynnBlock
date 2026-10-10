"""SkyyMenu 0.3.16 - bare-JVM harness for LAYOUT D + OWN TILE ICONS + PER-TILE VISIBILITY RULES (tools/menu_0_3_16_patch.py). Derived from
test_skyymenu_0.3.15.py. Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all (A / D), -XX:-UsePerfData,
TEMP / TMP / java.io.tmpdir in the scratch folder. Nothing outside the scratch folder is written (the live Skyy_SkyyMenu folder is
checked afterwards).

    python SkyyMenu/test_skyymenu_0.3.16.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyMenu-0.3.16.jar] [--prev SkyyMenu-0.3.15.jar]

SECTIONS
  CC  CLASS COMPARE 0.3.15 -> 0.3.16 (javassist text of every method): no class added / gone; new fields only MenuData E_PERM / E_OPEN /
      E_NEED / E_UNLOCK / TILE_WARNED; new methods only MenuPage.tileVisible + openBridge; structural changes only MenuData.<clinit>,
      MenuPage.fillStatic, MenuPage.click; MenuPage.build differs only in the hint constant (the speech bubble)
  JT  jar assets: + exactly the 22 icon items (Server/Item/Items/Utility/Skyy_Menu_Icon_<Name>.json: Variant, no Categories / Recipe /
      Interactions, Icon = its PNG) + their PNGs (= art/menu-icons byte for byte = its manifest sha256 + bytes; no vanilla path); the bag
      PNG (0.3.11) = art/menu-icons' copy; every 0.3.15 asset byte-identical but the lang file (+ 22 names) and the manifest (version)
  A   every class of both jars loads, verifies (-Xverify:all) and initialises
  D   LAYOUT D + RULES, EXECUTED through the engine's own PageManager (openCustomPage -> MenuPage.build -> fillStatic -> tileVisible ->
      put -> new ItemStack; grid clicks -> handleDataEvent -> click -> openBridge / view), a real PermissionsModule with a fake provider:
        D1 a normal player: every tile at its D slot, wearing its own icon (the icon ids asked), the same tiles / texts as 0.3.15 (by
           name); Server Setup + Wardrobe + Pets (no SkyyPets) absent; their slots EMPTY (44, 36, 3), the free slots 27 / 39 / 41 empty
        D2 menu.modsHelp off: a normal player loses Mods (35 empty), nothing shifts; an admin (op, "*") keeps Mods + Server Setup (44)
        D3 an admin sees Server Setup at 44 = 0.3.15's tile; 0.3.15 had it at 41
        D4 the Bank unlock rule: no key -> shown; a Function answering FALSE -> 21 empty; TRUE -> shown; throwing -> hidden + exactly one
           warning (TILE_WARNED); a non-Function value -> shown
        D5 a non-admin perm rule (E_PERM set to a test node for the run): holder sees the tile, a plain player not, a personal deny not
        D6 the Wardrobe: no wardrobe:fn:open -> 36 empty; a Function -> "Wardrobe" at 36; click -> apply(the player's UUID) once, the grid
           emptied first; FALSE -> the menu says so; the Function gone before the click -> "not on this server"; (fix round) a Function
           that OPENS another page and then answers FALSE / throws -> that page stays, the menu sends NOTHING more (no status, no
           rebuild); the hover text promises nothing unbuilt (no "hotbar"); the /modconfig warning names the Server Setup tile, not a book
        D7 Teleport at 13: click -> the Teleport view; Back -> the main view at the same layout
        D8 the Pets tile (SkyyPets present, no pet file) -> slot 3 with our own collar icon Skyy_Menu_Icon_Pets
  V   the ENGINE'S OWN ASSET VALIDATORS (test_skyymenu_0.3.12.py run_v) on the jar + every Skyy_Menu_Icon_<Name> in the item store
  AA  THE ENGINE-ACCESS AUDIT: every class / field / method reference of every class in the jar resolved with
      MethodHandles.privateLookupIn (the JVM's own access rules); a control class with a protected call is refused
  CF  CARRY-FORWARD: the 0.3.15 harness (every check since 0.3.x, nested) on the 0.3.16 jar next to its control run on the 0.3.15 jar:
      the only new fails are the class-compare / asset / manifest / main-layout checks the new layout + icons change by design
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, hashlib, ast

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.16", "0.3.15"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menu0316", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
ASSETS_ZIP = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
V_HARNESS = os.path.join(HERE, "test_skyymenu_0.3.12.py")
ART = os.path.join(ROOT, "art", "menu-icons")
ICONS = ["YourProfile", "Pets", "HoverTooltips", "Teleport", "PocketDimension", "AccessoryBag", "HudEditor", "Crafting", "Skills",
         "Collections", "IslandMenu", "Bank", "Vault", "Bazaar", "AuctionHouse", "Reforge", "Identify", "Players", "Party", "Guild",
         "Settings", "Mods", "ServerSetup"]
NEW_ICONS = [n for n in ICONS if n != "AccessoryBag"]
# Skyy's layout D (docs/answered/ui.md 2026-10-10): tile -> slot (row * 9 + col)
D_SLOT = {"Pets": 3, "Skills": 4, "Accessory Bag": 5, "Island Menu": 12, "Teleport": 13, "Crafting": 14, "Bank": 21, "Bazaar": 22,
          "Auction House": 23, "Vault": 29, "Reforge": 30, "Identify": 31, "Pocket Dimension": 32, "Your Profile": 33, "Collections": 40,
          "Players": 0, "Party": 9, "Guild": 18, "Wardrobe": 36, "Hover Tooltips": 8, "Settings": 17, "HUD Editor": 26, "Mods": 35,
          "Server Setup": 44}
TILE_ICON = {"Your Profile": "YourProfile", "Pets": "Pets", "Hover Tooltips": "HoverTooltips", "Teleport": "Teleport",
             "Pocket Dimension": "PocketDimension", "Accessory Bag": "AccessoryBag", "HUD Editor": "HudEditor", "Crafting": "Crafting",
             "Skills": "Skills", "Collections": "Collections", "Island Menu": "IslandMenu", "Bank": "Bank", "Vault": "Vault",
             "Bazaar": "Bazaar", "Auction House": "AuctionHouse", "Reforge": "Reforge", "Identify": "Identify", "Players": "Players",
             "Party": "Party", "Guild": "Guild", "Settings": "Settings", "Mods": "Mods", "Server Setup": "ServerSetup"}
FREE = (27, 39, 41)
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


def base_name(n):
    """a tile name without the decorations fillStatic adds (Hover Tooltips: ON, (not installed), (update needed))"""
    n = re.sub(r" \((not installed|update needed)\)$", "", n)
    return re.sub(r": (ON|OFF)$", "", n)


# ============================================================================================ child: D (one JVM, -Xverify:all)
def run_d(out):
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

        def hclass(name, sup, ctor, fields=(), meths=()):
            c = HP.makeClass(name, HP.get(sup)) if sup else HP.makeClass(name)
            for s_ in fields:
                c.addField(CtField.make(s_, c))
            if ctor:
                c.addConstructor(CtNewConstructor.make(ctor, c))
            for s_ in meths:
                c.addMethod(CtNewMethod.make(s_, c))
            c.writeFile(hcls)

        # the stand-ins of test_skyymenu_0.3.14.py (packet sink, store, world, command system, item assets)
        hclass("skyymenuharness.Net", "com.hypixel.hytale.server.core.io.PacketHandler",
               "public Net() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
               ["public java.util.ArrayList sent;"],
               ["public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
                "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}",
                "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
                "public String getIdentifier() { return \"skyymenuharness\"; }"])
        hclass("com.hypixel.hytale.component.SkyyMenuTestStore", "com.hypixel.hytale.component.Store",
               "public SkyyMenuTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
               "(com.hypixel.hytale.component.IResourceStorage) null); }",
               ["public java.util.IdentityHashMap comps;"],
               ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
                "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
                "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
        hclass("skyymenuharness.World", "com.hypixel.hytale.server.core.universe.world.World",
               "public World() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }",
               ["public java.util.concurrent.ConcurrentLinkedQueue tasks;"],
               ["public void execute(java.lang.Runnable r) {\n  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
                "  this.tasks.add(r);\n}"])
        hclass("skyymenuharness.RecFuture", "java.util.concurrent.CompletableFuture", "public RecFuture() { super(); }",
               ["public java.util.function.BiConsumer act;"],
               ["public java.util.concurrent.CompletableFuture whenComplete(java.util.function.BiConsumer a) { this.act = a; return this; }"])
        hclass("skyymenuharness.Cmd", "com.hypixel.hytale.server.core.command.system.AbstractCommand", "public Cmd() { super(\"x\", \"y\"); }", [],
               ["public boolean hasPermission(com.hypixel.hytale.server.core.command.system.CommandSender s) { return true; }",
                "protected java.util.concurrent.CompletableFuture execute(com.hypixel.hytale.server.core.command.system.CommandContext c) { return null; }"])
        hclass("skyymenuharness.Cmds", "com.hypixel.hytale.server.core.command.system.CommandManager", "public Cmds() { super(); }",
               ["public java.util.HashMap cmds;", "public java.util.ArrayList lines;", "public skyymenuharness.RecFuture last;"],
               ["public com.hypixel.hytale.server.core.command.system.AbstractCommand resolveCommand(String n) {\n"
                "  return this.cmds == null ? null : (com.hypixel.hytale.server.core.command.system.AbstractCommand) this.cmds.get(n);\n}",
                "public java.util.concurrent.CompletableFuture handleCommand(com.hypixel.hytale.server.core.command.system.CommandSender s, String line) {\n"
                "  if (this.lines == null) this.lines = new java.util.ArrayList();\n  this.lines.add(line);\n"
                "  this.last = new skyymenuharness.RecFuture();\n  return this.last;\n}"])
        hclass("skyymenuharness.ItemMap", "com.hypixel.hytale.assetstore.map.DefaultAssetMap", "public ItemMap() { super(); }",
               ["public com.hypixel.hytale.assetstore.JsonAsset item;", "public java.util.ArrayList asked;"],
               ["public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object k) {\n"
                "  if (this.asked == null) this.asked = new java.util.ArrayList();\n  this.asked.add(k);\n  return this.item;\n}"])
        hclass("skyymenuharness.Items", "com.hypixel.hytale.assetstore.AssetStore",
               "public Items() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }",
               ["public com.hypixel.hytale.assetstore.AssetMap map;"],
               ["public com.hypixel.hytale.assetstore.AssetMap getAssetMap() { return this.map; }"])

        UUID, Paths, ArrayList, HashMap, IdMap, HashSet = (JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"),
                                                           JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"), JClass("java.util.HashSet"))
        JBool = JClass("java.lang.Boolean")
        NET, TSC, HW = JClass("skyymenuharness.Net"), JClass("com.hypixel.hytale.component.SkyyMenuTestStore"), JClass("skyymenuharness.World")
        PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
        WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
        Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
        EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
        STc = JClass("com.hypixel.hytale.component.Store")
        CTc = JClass("com.hypixel.hytale.component.ComponentType")
        REFc = JClass("com.hypixel.hytale.component.Ref")
        PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        CPE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent")
        CPT = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType")
        CMGRc = JClass("com.hypixel.hytale.server.core.command.system.CommandManager")
        PMOD = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
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
        WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
        jf(Uni.class_, "worldsByUuid").set(uni, WORLDS)
        jf(Uni.class_, "players").set(uni, ArrayList())
        jf(Uni.class_, "instance").set(None, uni)
        em = U.allocateInstance(EMc.class_)
        jf(EMc.class_, "playerComponentType").set(em, CT_PLA)
        jf(EMc.class_, "instance").set(None, em)
        W1 = U.allocateInstance(HW.class_)
        W1U = UUID.randomUUID()
        WORLDS.put(W1U, W1)
        CM = U.allocateInstance(JClass("skyymenuharness.Cmds").class_)
        CM.cmds = HashMap()
        CM.lines = ArrayList()
        for cn_ in ("island", "hub", "sacks", "accessories", "skymenu"):
            CM.cmds.put(cn_, U.allocateInstance(JClass("skyymenuharness.Cmd").class_))
        jf(CMGRc.class_, "instance").set(None, CM)
        ITc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        IMAP = U.allocateInstance(JClass("skyymenuharness.ItemMap").class_)
        IMAP.item = U.allocateInstance(ITc.class_)
        ISTORE = U.allocateInstance(JClass("skyymenuharness.Items").class_)
        ISTORE.map = IMAP
        jf(ITc.class_, "ASSET_STORE").set(None, ISTORE)

        # ---- a REAL PermissionsModule behind PermissionsModule.get() with one fake provider (test_skyymenu_0.3.12.py section B)
        PLAIN = UUID.fromString("00000000-0000-0000-0000-0000000000b1")    # hytale:Adventurer, no nodes
        OP = UUID.fromString("00000000-0000-0000-0000-0000000000b2")       # hytale:Admin = "*"
        RANK = UUID.fromString("00000000-0000-0000-0000-0000000000b3")     # holds skyytest.rank
        DENY = UUID.fromString("00000000-0000-0000-0000-0000000000b4")     # op with a personal deny -skyytest.rank
        USERS = {str(PLAIN): ([], ["hytale:Adventurer"]), str(OP): ([], ["hytale:Admin"]), str(RANK): (["skyytest.rank"], ["hytale:Adventurer"]),
                 str(DENY): (["-skyytest.rank"], ["hytale:Admin"])}
        GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

        def jset(*xs):
            st_ = HashSet()
            for x in xs:
                st_.add(x)
            return st_

        @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
        class Prov:
            @JOverride
            def getName(self): return "menu0316-test"
            @JOverride
            def getUserPermissions(self, u): return jset(*USERS.get(str(u), ([], []))[0])
            @JOverride
            def getGroupsForUser(self, u): return jset(*USERS.get(str(u), ([], []))[1])
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
            def addUserPermissions(self, *a): return None
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
        R["perm_engine"] = [bool(PMOD.get().hasPermission(OP, "skyymenu.modconfig")), bool(PMOD.get().hasPermission(PLAIN, "skyymenu.modconfig")),
                            bool(PMOD.get().hasPermission(RANK, "skyytest.rank")), bool(PMOD.get().hasPermission(DENY, "skyytest.rank"))]

        def JV(k, n):
            return JClass(PKG + n, loader=L[k])
        mods = os.path.join(SCRATCH, "world", "mods")
        for k in ("new", "prev"):
            JV(k, "PageGuard").STOP = False
            JV(k, "PageGuard").EXEC = None
            JV(k, "SetStore").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "settings-" + k))
            JV(k, "Tips").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "notips-" + k))
            JV(k, "PetTile").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyPets", "pets"))
        BRG = JV("new", "MenuUtil").bridge()
        MDn, CFGn, CFGp = JV("new", "MenuData"), JV("new", "MenuCfg"), JV("prev", "MenuCfg")

        class Pl:
            pass

        def player(uid=PLAIN):
            P = Pl()
            P.pr = U.allocateInstance(PR.class_)
            jf(PR.class_, "uuid").set(P.pr, uid)
            jf(PR.class_, "username").set(P.pr, "SkyyHarness")
            P.net = U.allocateInstance(NET.class_)
            jf(PR.class_, "packetHandler").set(P.pr, P.net)
            jf(PR.class_, "worldUuid").set(P.pr, W1U)
            P.pl = U.allocateInstance(PLAc.class_)
            P.wm = WMc()
            P.wm.init(P.pr)
            P.pm = PMc()
            P.pm.init(P.pr, P.wm)
            jf(PLAc.class_, "windowManager").set(P.pl, P.wm)
            jf(PLAc.class_, "pageManager").set(P.pl, P.pm)
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
            jf(ESc.class_, "world").set(es, W1)
            jf(STc.class_, "externalData").set(st, es)
            P.ref, P.st = ref, st
            jf(PR.class_, "entity").set(P.pr, P.ref)
            P.seen, P.binds = 0, {}
            return P

        def sent(P):
            return [] if P.net.sent is None else [P.net.sent.get(i) for i in range(int(P.net.sent.size()))]

        def pump(P):
            for p in sent(P)[P.seen:]:
                kind = str(p.getClass().getSimpleName())
                if kind == "CustomPage":
                    if bool(p.clear) or bool(p.isInitial):
                        P.binds = dict((str(e.selector), None if e.data is None else str(e.data)) for e in p.eventBindings)
                    P.pm.handleEvent(P.ref, P.st, CPE(CPT.Acknowledge, None))
                elif kind == "SetPage":
                    P.pm.handleEvent(P.ref, P.st, CPE(CPT.Acknowledge, None))
            P.seen = len(sent(P))

        def press(P, sel, slot):
            d = json.loads(P.binds[sel]) if P.binds.get(sel) else {}
            d["SlotIndex"] = slot
            P.pm.handleEvent(P.ref, P.st, CPE(CPT.Data, json.dumps(d, separators=(",", ":"))))
            pump(P)

        def tiles_of(pg):
            t = {}
            for i in range(54):
                a = pg.acts[i]
                if a is not None:
                    t[i] = [str(a), str(pg.names[i]), str(pg.bodies[i])]
            return t

        def menu(k, uid=PLAIN, view="main"):
            """a fresh menu of jar k opened through the engine -> (page, slot -> [act, name, body], icon ids asked, player)"""
            P = player(uid)
            IMAP.asked = ArrayList()
            pg = JV(k, "MenuPage")(P.pr, view)
            P.pm.openCustomPage(P.ref, P.st, pg)
            pump(P)
            asked = [str(IMAP.asked.get(i)) for i in range(int(IMAP.asked.size()))]
            return pg, tiles_of(pg), asked, P

        D = {}
        # ---- D1 a normal player
        pg, tn, an, P = menu("new")
        _pg, tp, ap, _P = menu("prev")
        D["d1"] = {"new": tn, "prev": tp, "asked": an, "asked_prev": ap,
                   "hint": str(pg.getClass().getName())}
        # ---- D2 modsHelp off
        CFGn.MODS_HELP = False
        CFGp.MODS_HELP = False
        _pg, t2, _a, _P = menu("new")
        _pg, t2p, _a, _P = menu("prev")
        _pg, t2a, _a, _P = menu("new", OP)
        D["d2"] = {"plain": t2, "plain_prev": t2p, "admin": t2a}
        CFGn.MODS_HELP = True
        CFGp.MODS_HELP = True
        # ---- D3 an admin
        _pg, t3, a3, _P = menu("new", OP)
        _pg, t3p, _a, _P = menu("prev", OP)
        D["d3"] = {"admin": t3, "admin_prev": t3p, "asked": a3}
        # ---- D4 the Bank unlock rule
        calls = []

        @JImplements("java.util.function.Function")
        class Unlock:
            def __init__(self, ans):
                self.ans = ans

            @JOverride
            def apply(self, u):
                calls.append(str(u))
                if self.ans == "throw":
                    raise RuntimeError("unlock check broke")
                return JBool.TRUE if self.ans else JBool.FALSE
        d4 = {}
        BRG.remove("bank:fn:unlocked")
        d4["absent"] = 21 in menu("new")[1]
        BRG.put("bank:fn:unlocked", Unlock(False))
        _pg, t4f, _a, _P = menu("new")
        d4["false"] = [21 in t4f, dict((i, v) for i, v in t4f.items() if i != 21) == dict((i, v) for i, v in tn.items() if i != 21)]
        BRG.put("bank:fn:unlocked", Unlock(True))
        _pg, t4t, _a, _P = menu("new")
        d4["true"] = [t4t.get(21), t4t == tn]
        warned0 = int(MDn.TILE_WARNED.size())
        BRG.put("bank:fn:unlocked", Unlock("throw"))
        _pg, t4x, _a, _P = menu("new")
        menu("new")
        d4["throw"] = [21 in t4x, int(MDn.TILE_WARNED.size()) - warned0, bool(MDn.TILE_WARNED.containsKey("bank:fn:unlocked"))]
        BRG.put("bank:fn:unlocked", "not a function")
        d4["string"] = 21 in menu("new")[1]
        BRG.remove("bank:fn:unlocked")
        d4["calls"] = [len(calls), sorted(set(calls)) == [str(PLAIN)]]
        D["d4"] = d4
        # ---- D5 a non-admin perm rule (the data hook ranks will use): Bank gets the test node for this run only
        names = [str(x) for x in MDn.E_NAME]
        bi = [i for i, n_ in enumerate(names) if n_ == "Bank" and str(MDn.E_VIEW[i]) == "main"][0]
        old = str(MDn.E_PERM[bi])
        MDn.E_PERM[bi] = "skyytest.rank"
        D["d5"] = {"rank": 21 in menu("new", RANK)[1], "plain": 21 in menu("new", PLAIN)[1], "deny": 21 in menu("new", DENY)[1],
                   "op_other": 44 in menu("new", RANK)[1], "old": old}
        MDn.E_PERM[bi] = old
        # ---- D6 the Wardrobe
        wcalls = []

        @JImplements("java.util.function.Function")
        class Ward:
            def __init__(self, ans):
                self.ans = ans

            @JOverride
            def apply(self, u):
                wcalls.append(str(u))
                if self.ans in ("swapF", "swapX"):
                    Ph = whold["P"]
                    whold["other"] = JV("new", "MenuPage")(Ph.pr, "tp")
                    Ph.pm.openCustomPage(Ph.ref, Ph.st, whold["other"])
                    whold["mark"] = len(sent(Ph))
                    if self.ans == "swapX":
                        raise RuntimeError("wardrobe broke after opening its page")
                    return JBool.FALSE
                return JBool.TRUE if self.ans else JBool.FALSE
        whold = {}
        d6 = {}
        BRG.remove("wardrobe:fn:open")
        d6["absent"] = 36 in menu("new")[1]
        BRG.put("wardrobe:fn:open", Ward(True))
        pg6, t6, a6, P6 = menu("new")
        d6["present"] = [t6.get(36), "Furniture_Village_Wardrobe" in a6, dict((i, v) for i, v in t6.items() if i != 36) == tn]
        press(P6, "#SkyyMGrid", 36)
        d6["click"] = [list(wcalls), bool(pg6.cleared), str(pg6.status)]
        wcalls[:] = []
        BRG.put("wardrobe:fn:open", Ward(False))
        pg6b, _t, _a, P6b = menu("new")
        press(P6b, "#SkyyMGrid", 36)
        d6["false"] = [list(wcalls), str(pg6b.status), 13 in tiles_of(pg6b)]
        pg6c, _t, _a, P6c = menu("new")
        BRG.remove("wardrobe:fn:open")
        press(P6c, "#SkyyMGrid", 36)
        d6["gone"] = [str(pg6c.status), 36 in tiles_of(pg6c)]
        for ans in ("swapF", "swapX"):
            wcalls[:] = []
            BRG.put("wardrobe:fn:open", Ward(ans))
            pgs, _t, _a, Ps = menu("new")
            whold.clear()
            whold["P"] = Ps
            press(Ps, "#SkyyMGrid", 36)
            cur = Ps.pm.getCustomPage()
            d6[ans] = [len(wcalls), "other" in whold and cur is not None and bool(cur.equals(whold["other"])),
                       len(sent(Ps)) - whold.get("mark", -999), str(pgs.status)]
        BRG.remove("wardrobe:fn:open")
        D["d6"] = d6
        # ---- D7 Teleport at 13 -> the Teleport view -> Back
        pg7, t7, _a, P7 = menu("new")
        press(P7, "#SkyyMGrid", 13)
        d7 = {"view": str(pg7.view), "tp_tiles": tiles_of(pg7)}
        _pgp, ttp, _a, _P = menu("prev", PLAIN, "tp")
        d7["tp_prev"] = ttp
        press(P7, "#SkyyMGrid", 45)
        d7["back"] = [str(pg7.view), tiles_of(pg7) == tn]
        D["d7"] = d7
        # ---- D8 the Pets tile with SkyyPets present (no pet file) -> our collar icon
        @JImplements("java.util.function.Function")
        class Onxp:
            @JOverride
            def apply(self, u):
                return None
        BRG.put("pets:fn:onxp", Onxp())
        CM.cmds.put("pets", U.allocateInstance(JClass("skyymenuharness.Cmd").class_))
        _pg, t8, a8, _P = menu("new")
        D["d8"] = [t8.get(3), "Skyy_Menu_Icon_Pets" in a8, "Farming_Collar" in a8, str(MDn.ICON_PETS)]
        BRG.remove("pets:fn:onxp")
        CM.cmds.remove("pets")
        # ---- D9 every other view = 0.3.15's (the Mods view: the version text aside; the players view)
        for vw in ("mods", "players"):
            _pg, tv, av_, _P = menu("new", PLAIN, vw)
            _pg, tvp, avp, _P = menu("prev", PLAIN, vw)
            D["d9_" + vw] = [tv, tvp, av_, avp]
        R["D"] = D
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: CL line diff (run_cl of 0.3.15)
def run_cl(out):
    """the javassist instruction text of every method of both jars, line by line for the methods that differ"""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", "-Djava.io.tmpdir=" + os.path.join(SCRATCH, "tmp"), classpath=[B.JAVASSIST], convertStrings=True)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def text(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        if ca is None:
            return []
        it, pool, lines = ca.iterator(), mi.getConstPool(), []
        while it.hasNext():
            lines.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it, it.next(), pool))).replace("ldc_w ", "ldc "))
        return lines
    res = {}
    for tag, jp in (("new", JAR), ("prev", PREV_JAR)):
        cp = JClass("javassist.ClassPool")(False)
        cp.appendSystemPath()
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendClassPath(jp)
        d = {}
        for n in [x[:-6].replace("/", ".") for x in zipfile.ZipFile(jp).namelist() if x.endswith(".class")]:
            cc = cp.get(n)
            for m in list(cc.getDeclaredMethods()):
                d["%s.%s%s" % (n.rsplit(".", 1)[-1], m.getName(), m.getSignature())] = text(m)
        res[tag] = d
    N, P = res["new"], res["prev"]
    diff = {}
    for k in sorted(set(N) & set(P)):
        a, b = P[k], N[k]
        if a == b:
            continue
        if len(a) != len(b):
            diff[k] = {"shape": [len(a), len(b)]}
            continue
        diff[k] = {"lines": [[x, y] for x, y in zip(a, b) if x != y]}
    json.dump(diff, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: AA (the engine-access audit)
def run_aa(out):
    from jpype import JClass
    import skyybuild as B
    S = sk()
    hcls = os.path.join(SCRATCH, "aaclasses")
    os.makedirs(hcls, exist_ok=True)
    # the helper classes first (javassist only, no JVM class loading of them yet)
    import jpype
    S.jvm_start([hcls, JAR])
    HP = JClass("javassist.ClassPool")(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
    CtNewMethod = JClass("javassist.CtNewMethod")
    lk = HP.makeClass("skyymenuaudit.LookupIn")
    lk.addMethod(CtNewMethod.make("public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
                                  "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(hcls)
    ba = HP.makeClass("skyymenuaudit.BadAccess")
    ba.addMethod(CtNewMethod.make("public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
                                  "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(hcls)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR, hcls):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass("skyymenuaudit.LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)
    cs_ = set()

    def lookup_audit(cn):
        Dc = jvm_class(cn)
        lkp = LIN.lookupIn(Dc)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                name = None
                mt = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lkp.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lkp.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lkp.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(Dc.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lkp.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lkp.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lkp.findSpecial(C_, name, mt, Dc)
                        else:
                            lkp.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None and mt is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, str(ex_)[:200]))
        return refused, n
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, str(ex_)[:200])], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit("skyymenuaudit.BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: V (the engine's asset validators)
def run_v(out):
    spec = importlib.util.spec_from_file_location("tm0312", V_HARNESS)
    m = importlib.util.module_from_spec(spec)
    vdir = os.path.join(SCRATCH, "v")
    os.makedirs(vdir, exist_ok=True)
    saved = list(sys.argv)
    sys.argv = [V_HARNESS, "--jar", JAR, "--dir", vdir]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    R = {}
    try:
        m.run_v()
        from jpype import JClass
        ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        st = {}
        for n in ["Skyy_Menu_Icon_" + x for x in ICONS]:
            it = ITEM.getAssetMap().getAsset(n)
            if it is None:
                st[n] = None
                continue
            pk = it.toPacket()
            st[n] = [None if pk.icon is None else str(pk.icon), None if pk.model is None else str(pk.model)]
        R["icons"] = st
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    R["fails"], R["oks"] = list(m.FAILS), m.OKS[0]
    json.dump(R, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================ parent
def fails_of(text):
    return set(ln[len("FAIL "):] for ln in text.splitlines() if ln.startswith("FAIL "))


def nested(text):
    """the fails the 0.3.15 harness lists as unexpected new-only fails of ITS carry-forward (the 0.3.14 harness and below)"""
    out = set()
    for ln in text.splitlines():
        if ln.startswith("FAIL CF: on the 0.3.15 jar only") and "beyond the control: " in ln:
            rest = ln.split("beyond the control: ", 1)[1]
            try:
                i = rest.index("] [") + 1
                out |= set(ast.literal_eval(rest[:i])) | set(ast.literal_eval(rest[i + 1:]))
            except Exception:
                out.add(ln)
    return out


# the 0.3.15 harness's checks that layout D + the icons change BY DESIGN on the 0.3.16 jar (each reason in the comment)
CF_EXPECTED = [
    r"^CC: ",                                           # its class compare is 0.3.14 -> <jar>: the tile rules, the new methods / fields
    r"^JT: \+ exactly the 3 emblem files",              # + the 22 icon items + PNGs
    r"^JT: every 0\.3\.14 asset byte-identical",        # the lang file has 22 more names
    r"^JT: manifest = 0\.3\.14's but the version",      # the version is 0.3.16
    r"^MR: the main menu = 0\.3\.14's",                 # layout D + the own icons
    r"^MR: every Mods tile's action / name / text = 0\.3\.14's \(version aside\)",   # its norm knows 0.3.15 / 0.3.14 only: the SkyyMenu
    # row says 0.3.16 (D9 checks the Mods view = 0.3.15's with the version normalised)
]
CF_NESTED_EXPECTED = [
    r"^CC: ", r"^JT: ", r"^PT1\b", r"^PT2\b", r"^PT3\b", r"^PT4\b", r"^PT6\b", r"^PT7\b",   # the 0.3.14 harness: compares / assets / the Pets
    # tile at slot 5 + the vanilla collar fallback (0.3.16: slot 3, our own collar icon - D8 checks it)
    r"^K\. ", r"^K[4-7]\b", r"^F\. 0\.3\.7: 26 mods \(SkyyMenu 0\.3\.16\)",              # the 0.3.12 harness: K compares + the version
    r"^IC\b", r"^V\b.*Voidheart", r"^H\. ",                                               # its icon-item / held-look / main-slot checks
]


def carry_forward(env):
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyymenu_0.3.15.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        res[tag] = (fails_of(p.stdout or ""), p.stdout or "")
        open(os.path.join(SCRATCH, "..", "cf-%s.log" % tag), "w", encoding="utf8").write(p.stdout or "")
    fn_, fc_ = res["new"][0], res["ctl"][0]
    extra = sorted(f for f in fn_ - fc_ if not f.startswith("CF: on the 0.3.15 jar only"))
    bad = [f for f in extra if not any(re.search(p_, f) for p_ in CF_EXPECTED)]
    nx = sorted(nested(res["new"][1]) - nested(res["ctl"][1]))
    nbad = [f for f in nx if not any(re.search(p_, f) for p_ in CF_NESTED_EXPECTED)]
    tot = re.search(r"SkyyMenu 0\.3\.15 harness: (\d+) ok, (\d+) fail", res["new"][1])
    totc = re.search(r"SkyyMenu 0\.3\.15 harness: (\d+) ok, (\d+) fail", res["ctl"][1])
    print("CF: 0.3.15 harness on 0.3.16: %s ok / %s fail; on 0.3.15 (control): %s ok / %s fail" % (
        tot.group(1) if tot else "?", tot.group(2) if tot else "?", totc.group(1) if totc else "?", totc.group(2) if totc else "?"))
    print("CF: control fails %d: %s" % (len(fc_), [f[:90] for f in sorted(fc_)]))
    print("CF: new-only fails %d: %s" % (len(extra), [e[:110] for e in extra]))
    print("CF: nested new-only %d: %s" % (len(nx), [e[:110] for e in nx]))
    check(tot is not None and totc is not None, "CF: both 0.3.15 harness runs finished")
    check(not bad and not nbad, "CF: on the 0.3.16 jar only the expected compare / asset / manifest / layout checks fail beyond the control: %s %s"
          % ([b_[:300] for b_ in bad], [b_[:300] for b_ in nbad]))


def check_d(D):
    d1 = D["d1"]
    tn = dict((int(k), v) for k, v in d1["new"].items())
    tp = dict((int(k), v) for k, v in d1["prev"].items())
    byname = dict((base_name(v[1]), (i, v)) for i, v in tn.items() if i < 45)
    byname_p = dict((base_name(v[1]), (i, v)) for i, v in tp.items() if i < 45)
    print("D1. normal player main view 0.3.16: %s" % sorted((i, base_name(v[1])) for i, v in tn.items()))
    print("D1. normal player main view 0.3.15: %s" % sorted((i, base_name(v[1])) for i, v in tp.items()))
    expect = dict((n, s) for n, s in D_SLOT.items() if n not in ("Server Setup", "Wardrobe", "Pets"))
    check(sorted(byname) == sorted(expect) and len(byname) == len([i for i in tn if i < 45]),
          "D1 a normal player sees exactly the D tiles without Server Setup / Wardrobe / Pets: %s" % sorted(set(byname) ^ set(expect)))
    for n, s in expect.items():
        check(byname.get(n, (None,))[0] == s, "D1 %s at slot %d (layout D): %s" % (n, s, byname.get(n, (None,))[0]))
    check(set(byname) == set(byname_p), "D1 the same tiles as 0.3.15 for a normal player (just moved): %s" % sorted(set(byname) ^ set(byname_p)))
    same = [n for n in byname if byname[n][1] == byname_p.get(n, (0, None))[1]]
    check(len(same) == len(byname), "D1 every tile's action / name / text = 0.3.15's: %s" % sorted(set(byname) - set(same)))
    check(all(s not in tn for s in (3, 36, 44) + FREE), "D1 the hidden tiles' slots (Pets 3, Wardrobe 36, Server Setup 44) and the free slots 27 / 39 / 41 are EMPTY")
    check(tn.get(13, [None])[0] == "view:tp" and base_name(tn[13][1]) == "Teleport", "D1 Teleport on slot 13 (under the mouse)")
    asked = d1["asked"]
    for n in expect:
        ic = "Skyy_Menu_Icon_" + TILE_ICON[n]
        check(ic in asked, "D1 the %s tile draws its own icon %s" % (n, ic))
    vanilla_old = ["Instance_Gateway", "Deco_Map", "Bench_WorkBench", "Furniture_Village_Painting_1x1", "Plant_Sapling_Oak", "Rock_Gem_Emerald",
                   "Deco_Book_Pile_Large", "Furniture_Crude_Torch", "Furniture_Ancient_Bookshelf", "Furniture_Village_Sign", "Deco_Scroll"]
    check(not [x for x in vanilla_old if x in asked] and [x for x in vanilla_old if x in d1["asked_prev"]],
          "D1 none of 0.3.15's vanilla tile icons is drawn any more: %s" % [x for x in vanilla_old if x in asked])
    check(49 in tn and tn[49][0] == "close" and 45 not in tn, "D1 Close at 49 as before, no Back on the main view")
    d2 = D["d2"]
    pl = dict((int(k), v) for k, v in d2["plain"].items())
    plp = dict((int(k), v) for k, v in d2["plain_prev"].items())
    ad = dict((int(k), v) for k, v in d2["admin"].items())
    check(35 not in pl and dict((i, v) for i, v in tn.items() if i != 35) == pl, "D2 menu.modsHelp off: a normal player loses Mods (35 empty), nothing shifts")
    check(not [v for v in plp.values() if v[0] == "view:mods"], "D2 (0.3.15 hid Mods the same way)")
    check(ad.get(35, [None])[0] == "view:mods" and ad.get(44, [None])[0] == "admin", "D2 an admin keeps Mods (35) + Server Setup (44) with modsHelp off")
    d3 = D["d3"]
    t3 = dict((int(k), v) for k, v in d3["admin"].items())
    t3p = dict((int(k), v) for k, v in d3["admin_prev"].items())
    check(t3.get(44) is not None and t3[44][0] == "admin" and t3[44] == t3p.get(41), "D3 an admin sees Server Setup at 44 = 0.3.15's tile (was 41)")
    check(set(t3) == set(tn) | {44} and "Skyy_Menu_Icon_ServerSetup" in d3["asked"], "D3 admin = the player's tiles + Server Setup (own icon)")
    d4 = D["d4"]
    check(d4["absent"] is True, "D4 no bank:fn:unlocked -> Bank shown (as today)")
    check(d4["false"] == [False, True], "D4 unlock FALSE -> slot 21 empty, every other tile unchanged: %s" % d4["false"])
    check(d4["true"][0] is not None and d4["true"][1] is True, "D4 unlock TRUE -> Bank shown, the menu = the no-rule menu")
    check(d4["throw"] == [False, 1, True], "D4 a throwing unlock -> hidden + exactly one warning over two draws: %s" % d4["throw"])
    check(d4["string"] is True, "D4 a non-Function value -> shown (as today)")
    check(d4["calls"][0] >= 4 and d4["calls"][1], "D4 the unlock Function got the player's UUID: %s" % d4["calls"])
    d5 = D["d5"]
    check(d5["rank"] is True and d5["plain"] is False and d5["deny"] is False and d5["old"] == "",
          "D5 a perm rule: the node holder sees the tile, a plain player and a personal deny do not: %s" % d5)
    check(d5["op_other"] is False, "D5 a non-admin rank holder still does not see Server Setup")
    d6 = D["d6"]
    check(d6["absent"] is False, "D6 no wardrobe:fn:open -> slot 36 empty")
    check(d6["present"][0] is not None and d6["present"][0][0] == "bridge:wardrobe:fn:open" and d6["present"][0][1] == "Wardrobe"
          and d6["present"][1] and d6["present"][2], "D6 the Function present -> Wardrobe at 36 (stand-in icon), nothing else changes: %s" % d6["present"][:1])
    check(d6["click"][0] == ["00000000-0000-0000-0000-0000000000b1"] and d6["click"][1] is True and d6["click"][2] == "",
          "D6 click -> apply(the player's UUID) once, the grid emptied first, no error: %s" % d6["click"])
    check(d6["false"][0] == ["00000000-0000-0000-0000-0000000000b1"] and "could not be opened" in d6["false"][1] and d6["false"][2],
          "D6 the Function answers FALSE -> the menu stays and says so: %s" % d6["false"])
    check("not on this server" in d6["gone"][0], "D6 the Function gone before the click -> says so: %s" % d6["gone"])
    print("D6. (fix) open-then-FALSE %s, open-then-throw %s, hover %r" % (d6["swapF"], d6["swapX"], d6["present"][0][2] if d6["present"][0] else None))
    for ans, how in (("swapF", "answers FALSE"), ("swapX", "throws")):
        check(d6[ans] == [1, True, 0, ""], "D6 (fix) the Function opens its page then %s -> that page stays, the menu sends nothing more "
              "(no status, no rebuild): [calls, other page current, packets after, status] %s" % (how, d6[ans]))
    body36 = d6["present"][0][2] if d6["present"][0] else ""
    check(body36 and "hotbar" not in body36.lower() and "loadout" in body36.lower(),
          "D6 (fix) the Wardrobe hover text promises nothing unbuilt (no hotbar / pets / abilities list): %s" % body36)
    d7 = D["d7"]
    check(d7["view"] == "tp" and d7["tp_tiles"] == d7["tp_prev"], "D7 Teleport (13) opens the Teleport view = 0.3.15's: %s" % d7["view"])
    check(d7["back"] == ["main", True], "D7 Back -> the main view, same layout")
    for vw in ("mods", "players"):
        tv, tvp, av_, avp = D["d9_" + vw]
        norm = lambda t: dict((i, [s_.replace(VERSION, "V").replace(PREV_VERSION, "V") for s_ in v]) for i, v in t.items())
        check(norm(tv) == norm(tvp) and av_ == avp and (len(tv) >= 20 or vw == "players"),
              "D9 the %s view = 0.3.15's (version text aside; same icons asked): %d tiles" % (vw, len(tv)))
    d8 = D["d8"]
    check(d8[0] is not None and d8[0][0] == "cmdc:pets" and d8[1] and not d8[2] and d8[3] == "Skyy_Menu_Icon_Pets",
          "D8 SkyyPets present -> the Pets tile at slot 3 with our own collar icon (no vanilla Farming_Collar): %s" % d8)


def main():
    if "--d" in sys.argv:
        return run_d(arg("--out"))
    if "--aa" in sys.argv:
        return run_aa(arg("--out"))
    if "--cl" in sys.argv:
        return run_cl(arg("--out"))
    if "--v" in sys.argv:
        return run_v(arg("--out"))
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

    def child(args_, out_, env_=None):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env_ or env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---- CC
        rules = [[r"menu_0_3_16_patch", "menu_0_3_15_patch"]]
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
            check(cc["added"] == [] and cc["gone"] == [], "CC: no class added or gone: %s %s" % (cc["added"], cc["gone"]))
            fn = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            fg = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(fn == {"MenuData": ["E_NEED:[Ljava/lang/String;", "E_OPEN:[Ljava/lang/String;", "E_PERM:[Ljava/lang/String;",
                                      "E_UNLOCK:[Ljava/lang/String;", "TILE_WARNED:Ljava/util/concurrent/ConcurrentHashMap;"]} and not fg,
                  "CC: new fields only MenuData E_PERM / E_OPEN / E_NEED / E_UNLOCK / TILE_WARNED, none gone: %s %s" % (fn, fg))
            check(all(v["same_shape"] for v in cls_.values()), "CC: same supers / interfaces")
            struct = dict((c, sorted(v["structural"])) for c, v in cls_.items() if v["structural"])
            want = {"MenuData": ["<clinit>"], "PetTile": ["icon([Ljava/lang/String;)Ljava/lang/String;"],
                    "MenuPage": ["build(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;"
                                 "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V", "click(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;ILjava/lang/String;)V",
                                                           "fillStatic(Ljava/util/ArrayList;)V", "openBridge(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V (new)",
                                                           "tileVisible(IZ)Z (new)"],
                    "MenuUtil": ["checkAdminCmd()V"]}
            check(struct == want, "CC: structural changes = MenuData.<clinit>, MenuPage.fillStatic / click / build (the hint), MenuUtil.checkAdminCmd (the warning text, fix), PetTile.icon (the inlined "
                  "ICON_PETS) + the new tileVisible / openBridge only: %s" % struct)
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            print("CC. 0.3.15 -> 0.3.16 structural %s; constants only %s" % (struct, const))
            check(all(m_.split("(")[0] in ("build", "<init>") or c == "SkyyMenuPlugin" or (c, m_.split("(")[0]) == ("MenuUtil", "checkAdminCmd")
                      for c, ms in const.items() for m_ in ms if c != "MenuData"),
                  "CC: the other constant-only changes are the version strings / the hint (MenuPage.build) / the admin-command warning: %s" % const)
        cl = child(["--cl"], os.path.join(SCRATCH, "cl.json"))
        check(cl is not None, "CC: the line-diff child ran")
        if cl is not None:
            pt = [k for k in cl if k.startswith("PetTile.icon(")]
            check(len(pt) == 1 and "lines" in cl[pt[0]] and cl[pt[0]]["lines"] and all(ab == ['ldc "Farming_Collar"', 'ldc "Skyy_Menu_Icon_Pets"'] for ab in cl[pt[0]]["lines"]),
                  "CC: PetTile.icon differs only in the inlined ICON_PETS constant Farming_Collar -> Skyy_Menu_Icon_Pets: %s" % [cl.get(k) for k in pt])
            bd = [k for k in cl if k.startswith("MenuPage.build(")]
            check(len(bd) == 1 and "lines" in cl[bd[0]] and [ab for ab in cl[bd[0]]["lines"] if "speech bubble" not in ab[1]] == []
                  and len(cl[bd[0]]["lines"]) == 1 and "the book at the top right" in cl[bd[0]]["lines"][0][0],
                  "CC: MenuPage.build differs only in the hint constant (the book -> the speech bubble): %s" % [cl.get(k) for k in bd])
            ac = [k for k in cl if k.startswith("MenuUtil.checkAdminCmd(")]
            check(len(ac) == 1 and "lines" in cl[ac[0]] and len(cl[ac[0]]["lines"]) == 1 and "SkyWynn Menu book" in cl[ac[0]]["lines"][0][0]
                  and "Server Setup tile in the SkyWynn Menu" in cl[ac[0]]["lines"][0][1],
                  "CC: (fix) MenuUtil.checkAdminCmd differs only in the warning text (the book -> the Server Setup tile): %s" % [cl.get(k) for k in ac])
            print("CC. instruction-level differences: %s" % sorted(cl))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn, np_ = set(n for n in zj.namelist() if not n.endswith(".class")), set(n for n in zp.namelist() if not n.endswith(".class"))
        want_new = set(["Server/Item/Items/Utility/Skyy_Menu_Icon_%s.json" % n for n in NEW_ICONS] +
                       ["Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % n for n in NEW_ICONS])
        check(nn - np_ == want_new and not (np_ - nn), "JT: + exactly the 22 icon items + PNGs, nothing gone: %s %s" % (sorted((nn - np_) ^ want_new)[:6], sorted(np_ - nn)))
        check(set(n for n in zj.namelist() if n.endswith(".class")) == set(n for n in zp.namelist() if n.endswith(".class")), "JT: the same class files")
        chg = sorted(n for n in np_ if zj.read(n) != zp.read(n))
        check(chg == ["Server/Languages/en-US/server.lang", "manifest.json"], "JT: every 0.3.15 asset byte-identical but the lang file + the manifest: %s" % chg)
        lang_n = zj.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines()
        lang_p = zp.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines()
        want_l = set(lang_p) | set("%sitems.Skyy_Menu_Icon_%s.name=%s" % (pre, n, dict((v, k) for k, v in TILE_ICON.items())[n]) for n in NEW_ICONS for pre in ("", "server."))
        check(set(lang_n) == want_l and len(lang_n) == len(lang_p) + 44, "JT: the lang file = 0.3.15's + the 2 name lines (tile name) of each new icon item: %s" % sorted(set(lang_n) ^ want_l)[:4])
        man = json.load(open(os.path.join(ART, "manifest.json"), encoding="utf8"))
        ents = dict((f["path"], f) for f in man["files"])
        av = zipfile.ZipFile(ASSETS_ZIP)
        van = set(av.namelist())
        for n in NEW_ICONS:
            p_ = "Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % n
            data = zj.read(p_)
            art = open(os.path.join(ART, *p_.split("/")), "rb").read()
            check(data == art and hashlib.sha256(data).hexdigest() == ents[p_]["sha256"] and len(data) == ents[p_]["bytes"],
                  "JT: %s = art/menu-icons byte for byte = its manifest sha256 + bytes" % p_)
            js_p = "Server/Item/Items/Utility/Skyy_Menu_Icon_%s.json" % n
            js = json.loads(zj.read(js_p))
            check(js.get("Icon") == "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % n and js.get("Variant") is True and "Categories" not in js
                  and "Recipe" not in js and "Interactions" not in js and js.get("MaxStack") == 1,
                  "JT: %s is a hidden icon-only item (Variant, no Categories / Recipe / Interactions), Icon = its PNG" % js_p)
            check(p_ not in van and js_p not in van and not [v for v in van if v.endswith("/Skyy_Menu_Icon_%s.json" % n)],
                  "JT: Skyy_Menu_Icon_%s is no vanilla id / path" % n)
        bag = zj.read("Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png")
        check(bag == open(os.path.join(ART, "Common", "Icons", "ItemsGenerated", "Skyy_Menu_Icon_AccessoryBag.png"), "rb").read(),
              "JT: the 0.3.11 bag icon = art/menu-icons' Skyy_Menu_Icon_AccessoryBag byte for byte (all 23 approved icons ship)")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.15's but the version")
        # ---- A + D
        r = child(["--d"], os.path.join(SCRATCH, "d.json"))
        check(r is not None and "error" not in r, "D ran: %s" % (r or {}).get("error", "")[-2500:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check(r["perm_engine"] == [True, False, True, False], "D: the engine's hasPermission: op yes, plain no, holder yes, deny no: %s" % r["perm_engine"])
            check_d(r["D"])
        # ---- V
        envv = dict(env)
        envv.pop("JAVA_TOOL_OPTIONS", None)
        v = child(["--v"], os.path.join(SCRATCH, "v.json"), envv)
        check(v is not None and "error" not in v, "V ran: %s" % (v or {}).get("error", "")[-2500:])
        if v:
            print("V. engine validators (test_skyymenu_0.3.12 run_v) on 0.3.16: %d ok, %d fail(s)%s" % (v["oks"], len(v["fails"]),
                  (": " + str([f_[:200] for f_ in v["fails"]])) if v["fails"] else ""))
            check(not v["fails"] and v["oks"] >= 5, "V: the engine's asset validators accept the 0.3.16 jar: %s" % v["fails"][:4])
            ic = v.get("icons") or {}
            miss = [n for n in ["Skyy_Menu_Icon_" + x for x in ICONS] if not ic.get(n)]
            check(not miss, "V: every Skyy_Menu_Icon_<Name> is in the engine's item store: missing %s" % miss)
            check(all(ic[n][0] == ("Icons/ItemsGenerated/%s.png" % n if n != "Skyy_Menu_Icon_AccessoryBag" else "Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png")
                      for n in ic if ic.get(n)), "V: each icon item's packet Icon = its own PNG")
        # ---- AA
        aa = child(["--aa"], os.path.join(SCRATCH, "aa.json"))
        check(aa is not None, "AA: the audit child ran")
        if aa:
            print("AA. engine-access audit: %d references in %d classes (MenuPage %s), refused %d; control refused %d; caller-sensitive %s" % (
                aa["refs"], aa["classes"], aa["per"].get("MenuPage"), len(aa["refused"]), len(aa["control"]), aa["caller_sensitive"]))
            check(not aa["refused"] and aa["refs"] > 1000, "AA: every class / member reference resolves under the JVM's own access rules: %s" % aa["refused"][:5])
            check(len(aa["control"]) >= 1, "AA: the control (a protected sendUpdate from another package) is refused")
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        ours = [c_ for c_ in chg if "0000000000b" in c_ or "0000000000a8" in c_ or "0000000000a7" in c_]
        if chg:
            print("NOTE: live files changed during the run (the game is running?): %s" % chg[:12])
        check(not ours, "the live Skyy_SkyyMenu folder got nothing from the harness: %s" % ours)
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
