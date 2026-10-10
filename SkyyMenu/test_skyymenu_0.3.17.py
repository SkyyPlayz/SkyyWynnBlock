"""SkyyMenu 0.3.17 - bare-JVM harness for THE MENU LAYOUT EDITOR (tools/menu_0_3_17_patch.py). Derived from test_skyymenu_0.3.16.py (its
engine stand-ins are copied verbatim into run_e). Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all
(A / E), -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. Nothing outside the scratch folder is written (the live
Skyy_SkyyMenu folder is only READ - copied into scratch for ST - and checked afterwards).

    python SkyyMenu/test_skyymenu_0.3.17.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyMenu-0.3.17.jar] [--prev SkyyMenu-0.3.16.jar]

SECTIONS
  CC  CLASS COMPARE 0.3.16 -> 0.3.17 (javassist text of every method): + exactly MenuLayout + LayoutSaveTask; new fields only MenuData
      (E_KEY, LAY_GRID, EDIT_SLOT, CTRL_*, ICON_* of the editor, the editor texts) + MenuPage (editing, editSel, lay, occ, hid); structural
      changes only MenuData.<clinit>, MenuPage <init> / fillStatic / nav / fill / build / click + the new editTile / editMarks / editInfo /
      startEdit / editClick, SeenTick.run, MenuReady.accept (the layout preload - fix round), SkyyMenuPlugin.setup / shutdown
  JT  jar assets = 0.3.16's byte for byte but the manifest (version); class files = 0.3.16's + MenuLayout + LayoutSaveTask
  A   every class of both jars loads, verifies (-Xverify:all) and initialises
  E   THE EDITOR, EXECUTED through the engine's own PageManager (openCustomPage -> build -> fillStatic -> MenuLayout.of -> put; grid
      clicks -> handleDataEvent -> click -> editClick -> MenuLayout.swap / reset / saveDefault / clearDefault -> LayoutSaveTask /
      saveNow -> atomicWrite), a real PermissionsModule with a fake provider, MenuLayout.DIR / DEF_FILE in the scratch folder:
        E1 no file: the main view = 0.3.16's (slots 0 - 52) + the Edit layout tile at 53 whose text says dragging does NOT work
        E2 Edit layout -> edit mode: title / hint / info box say no dragging; every slot 0 - 44 clickable but the slots of tiles this
           player cannot see (Pets 3, Wardrobe 36, Server Setup 44: NOT drawn, no "Kept slot" - fix round), Empty slots; Done 52, 53 empty
           (a double-click on Edit layout stays in edit mode - fix round), Reset 45, no admin buttons for a player; Close 49 unchanged
        E3 SWAP: Teleport (13) <-> Bazaar (22) -> saved in layouts/<uuid>.properties (_v=1, _name, teleport=22, bazaar=13); a fresh
           menu draws it; Teleport still opens the Teleport view from its new slot (no special lock)
        E4 CANCEL: the picked-up tile again -> nothing moved, nothing written
        E5 an EMPTY slot as target: the tile moves, its old slot is empty
        E6 HIDDEN slot: not clickable, never picked up, never a target (a stale / forged click gets KEPT_MSG, the selection stays); an
           empty slot first -> "click a tile first"
        E7 PER PLAYER: another player still has layout D; only the editor's file exists
        E8 RESET: one click arms, a different click disarms, two clicks -> the file is deleted, layout D again
        E9 DONE: edit mode off, the tiles run their action again, Edit layout back at 53
        E10 SERVER DEFAULT: an admin's buttons (46 / 47), two clicks each; layout-default.properties written; a player without an own
            layout gets it, a player with one keeps theirs; a player's forged esrvsave is refused; 47 twice -> the file deleted, layout D
        E11 HIDDEN TILE keeps its saved slot: Bank saved at slot 1 + unlock FALSE -> slot 1 not drawn (not a target), 21 free; unlock
            TRUE -> Bank drawn at 1; the file keeps bank=1
        E12 UNKNOWN / NEW / DOUBLED tiles: an unknown key ignored (its slot stays empty), a tile missing from the file (a NEW tile) and the
            loser of a doubled slot take the first free slots (lowest index, entry order), a slot out of range is dropped
        E13 CORRUPT files: garbage / _v=1 without tiles / a folder in place of the file / the server default file -> the default layout +
            exactly ONE warning per file over two opens, the file untouched; the first change keeps the old one as .bad, a second broken
            file later goes to .bad-<time> (the first .bad kept - fix round); a READ ERROR (a folder in place of the file, a VALID file
            locked by another process) = layout D, editing refused (EDIT_WAIT), the file never renamed, read again later (fix round)
        E14 SeenTick upkeep: pruneOffline (synchronized - fix round) drops cached layouts of players who left (never a pending save);
            flushAll retries
        E16 HOVER TOOLTIPS OFF (fix round): the first click on Edit layout shows its no-dragging text in the info box and asks again; the
            second click enters edit mode
        E17 PRELOAD (fix round): MenuLayout.preload (MenuReady) reads the layout file on the scheduler thread, not on the first draw
        E15 the other views (tp / mods / players) = 0.3.16's; no Edit layout tile there
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyMenu folder: start (loadDefault) -> a player edits -> stop (flushAll) -> start
      again -> the layout is still there; a start alone writes nothing; the live folder unchanged
  V   the ENGINE'S OWN ASSET VALIDATORS (the 0.3.16 harness's run_v) on the 0.3.17 jar
  AA  THE ENGINE-ACCESS AUDIT (the 0.3.16 harness's run_aa) on the 0.3.17 jar
  CF  CARRY-FORWARD: the 0.3.16 harness (every check since 0.3.x, nested) on the 0.3.17 jar next to its control run on the 0.3.16 jar:
      the only new fails are the class-compare / class-file / manifest checks the editor changes by design
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, hashlib, ast, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.17", "0.3.16"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menu0317", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
H16 = os.path.join(HERE, "test_skyymenu_0.3.16.py")
# layout D (docs/answered/ui.md 2026-10-10): tile -> slot; the saved-file key of each tile = its name, lower case, letters / digits
D_SLOT = {"Pets": 3, "Skills": 4, "Accessory Bag": 5, "Island Menu": 12, "Teleport": 13, "Crafting": 14, "Bank": 21, "Bazaar": 22,
          "Auction House": 23, "Vault": 29, "Reforge": 30, "Identify": 31, "Pocket Dimension": 32, "Your Profile": 33, "Collections": 40,
          "Players": 0, "Party": 9, "Guild": 18, "Wardrobe": 36, "Hover Tooltips": 8, "Settings": 17, "HUD Editor": 26, "Mods": 35,
          "Server Setup": 44}
KEY = dict((n, re.sub(r"[^a-z0-9]", "", n.lower())) for n in D_SLOT)
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
    n = re.sub(r"^\[Moving\] ", "", n)
    n = re.sub(r" \((not installed|update needed)\)$", "", n)
    return re.sub(r": (ON|OFF)$", "", n)


def layout_file(text):
    out = {}
    for ln in text.splitlines():
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            out[k] = v
    return out


# ============================================================================================ child: E + ST (one JVM, -Xverify:all)
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
        # ================================================================================ 0.3.17: the layout editor
        ML, MDn = JV("new", "MenuLayout"), JV("new", "MenuData")
        LDIR = os.path.join(mods, "Skyy_SkyyMenu", "layouts")
        DEFF = os.path.join(mods, "Skyy_SkyyMenu", "layout-default.properties")
        ML.DIR = Paths.get(LDIR)
        ML.DEF_FILE = Paths.get(DEFF)
        JStr = JClass("java.lang.String")
        UUID = JClass("java.util.UUID")
        E = {}

        def ownf(uid):
            return os.path.join(LDIR, str(uid) + ".properties")

        def settle():
            """the 300 ms LayoutSaveTask (or its inline fallback) has run; then flush anything left"""
            time.sleep(0.6)
            ML.flushAll()

        def fresh():
            """a server restart for the layout store: memory forgotten, the default file read again"""
            settle()
            for m_ in (ML.OWN, ML.NAMES, ML.DIRTY, ML.BROKEN, ML.ERRAT):
                m_.clear()
            ML.loadDefault()

        def by_name(t, lo=0, hi=45):
            return dict((base_name(v[1]), i) for i, v in t.items() if lo <= i < hi)

        def strs(o, depth=0, acc=None):
            """every String reachable through public fields / arrays / lists of a packet (to find the hint text)"""
            acc = [] if acc is None else acc
            if o is None or depth > 5:
                return acc
            try:
                if isinstance(o, str):
                    acc.append(o)
                    return acc
                cls_ = o.getClass()
                if cls_.isArray():
                    for x in o:
                        strs(x, depth + 1, acc)
                    return acc
                if str(cls_.getName()).startswith("java.lang.String"):
                    acc.append(str(o))
                    return acc
                if JClass("java.util.Collection").class_.isInstance(o):
                    for x in o.toArray():
                        strs(x, depth + 1, acc)
                    return acc
                if not str(cls_.getName()).startswith("com.hypixel"):
                    return acc
                for f_ in cls_.getFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    strs(f_.get(o), depth + 1, acc)
            except Exception:
                pass
            return acc

        def page_strs(P, last=1):
            got = []
            for p in sent(P)[-last:]:
                got += strs(p)
            return got

        # ---- E1 no file: 0.3.16's main view + the Edit layout tile at 53
        pg1, t1, a1, P1 = menu("new")
        _pp, t1p, _ap, _Pp = menu("prev")
        E["e1"] = {"new": t1, "prev": t1p, "asked": a1, "files": sorted(os.listdir(LDIR)) if os.path.isdir(LDIR) else [],
                   "edit_body": str(MDn.EDIT_BODY), "edit_foot": str(MDn.EDIT_FOOT)}
        # ---- E2 enter edit mode
        press(P1, "#SkyyMGrid", 53)
        t2 = tiles_of(pg1)
        E["e2"] = {"editing": bool(pg1.editing), "title": str(pg1.title), "status": str(pg1.status), "info": str(pg1.infoName),
                   "infobody": str(pg1.infoBody), "tiles": t2, "hint_sent": any(str(MDn.EDIT_HINT) in x_ for x_ in page_strs(P1)),
                   "hint": str(MDn.EDIT_HINT), "asked": [str(IMAP.asked.get(i)) for i in range(int(IMAP.asked.size()))]}
        press(P1, "#SkyyMGrid", 53)                        # fix round: a double-click on Edit layout (53 is empty in edit mode)
        E["e2"]["dbl"] = [bool(pg1.editing), pg1.acts[53] is None, str(pg1.status)]
        # ---- E3 swap Teleport (13) <-> Bazaar (22)
        w0 = int(ML.WRITES)
        press(P1, "#SkyyMGrid", 13)
        e3 = {"sel": int(pg1.editSel), "name13": str(pg1.names[13]), "info": str(pg1.infoName), "status_pick": str(pg1.status),
              "foot22": str(pg1.names[22])}
        press(P1, "#SkyyMGrid", 22)
        e3.update({"sel_after": int(pg1.editSel), "status": str(pg1.status), "t": tiles_of(pg1)})
        settle()
        e3["file"] = open(ownf(PLAIN), encoding="utf8").read() if os.path.isfile(ownf(PLAIN)) else None
        e3["writes"] = int(ML.WRITES) - w0
        _pg, e3["fresh"], _a, P3 = menu("new")
        press(P3, "#SkyyMGrid", 22)
        e3["tp_view"] = str(_pg.view)
        E["e3"] = e3
        # ---- E4 cancel
        w0 = int(ML.WRITES)
        lay0 = list(pg1.lay)
        press(P1, "#SkyyMGrid", 4)
        press(P1, "#SkyyMGrid", 4)
        settle()
        E["e4"] = {"sel": int(pg1.editSel), "status": str(pg1.status), "writes": int(ML.WRITES) - w0, "same": list(pg1.lay) == lay0,
                   "name4": str(pg1.names[4])}
        # ---- E5 to an empty slot: Skills (4) -> 1
        press(P1, "#SkyyMGrid", 4)
        press(P1, "#SkyyMGrid", 1)
        E["e5"] = {"status": str(pg1.status), "t": tiles_of(pg1)}
        # ---- E6 kept slots
        e6 = {}
        st0 = str(pg1.status)
        press(P1, "#SkyyMGrid", 44)                        # not drawn -> the engine click carries no action: nothing happens
        e6["press_hidden"] = [int(pg1.editSel), str(pg1.status) == st0, pg1.acts[44] is None]
        pg1.editClick(44, JStr("eslot"), None)             # a stale / forged click on it
        pump(P1)
        e6["pick_kept"] = [int(pg1.editSel), str(pg1.status)]
        press(P1, "#SkyyMGrid", 27)
        e6["pick_empty"] = [int(pg1.editSel), str(pg1.status)]
        press(P1, "#SkyyMGrid", 0)
        press(P1, "#SkyyMGrid", 44)
        e6["press_to_hidden"] = int(pg1.editSel)
        pg1.editClick(44, JStr("eslot"), None)
        pump(P1)
        e6["to_kept"] = [int(pg1.editSel), str(pg1.status), str(pg1.names[0])]
        press(P1, "#SkyyMGrid", 0)
        e6["cancel"] = int(pg1.editSel)
        settle()
        e6["file"] = layout_file(open(ownf(PLAIN), encoding="utf8").read())
        E["e6"] = e6
        # ---- E7 per player
        _pg, t7, _a, _P = menu("new", RANK)
        E["e7"] = {"rank": t7, "files": sorted(os.listdir(LDIR)), "plain_own": bool(ML.hasOwn(PLAIN)), "rank_own": bool(ML.hasOwn(RANK))}
        # ---- E8 reset (arm, disarm, reset)
        e8 = {}
        press(P1, "#SkyyMGrid", 45)
        e8["arm"] = [str(pg1.status), str(pg1.cfgArm)]
        press(P1, "#SkyyMGrid", 4)
        press(P1, "#SkyyMGrid", 4)
        e8["disarmed"] = str(pg1.cfgArm)
        press(P1, "#SkyyMGrid", 45)
        settle()
        e8["after_one"] = os.path.isfile(ownf(PLAIN))
        press(P1, "#SkyyMGrid", 45)
        e8["status"] = str(pg1.status)
        settle()
        e8["after_two"] = os.path.isfile(ownf(PLAIN))
        e8["t"] = tiles_of(pg1)
        _pg, e8["fresh"], _a, _P = menu("new")
        E["e8"] = e8
        # ---- E9 done (52)
        press(P1, "#SkyyMGrid", 52)
        e9 = {"editing": bool(pg1.editing), "status": str(pg1.status), "t": tiles_of(pg1), "title": str(pg1.title)}
        press(P1, "#SkyyMGrid", 13)
        e9["view"] = str(pg1.view)
        E["e9"] = e9
        # ---- E10 server default
        e10 = {}
        pga, _t, _a, PA = menu("new", OP)
        press(PA, "#SkyyMGrid", 53)
        ta = tiles_of(pga)
        e10["admin_ctrl"] = [ta.get(46), ta.get(47), ta.get(45), ta.get(52)]
        e10["admin_info"] = str(pga.infoBody)
        press(PA, "#SkyyMGrid", 13)
        press(PA, "#SkyyMGrid", 14)
        press(PA, "#SkyyMGrid", 46)
        e10["arm"] = [str(pga.status), os.path.isfile(DEFF), ML.DEF is None]
        press(PA, "#SkyyMGrid", 46)
        e10["saved"] = str(pga.status)
        settle()
        e10["file"] = layout_file(open(DEFF, encoding="utf8").read()) if os.path.isfile(DEFF) else None
        _pg, e10["rank"], _a, _P = menu("new", RANK)
        # PLAIN makes an own layout (Players 0 <-> Party 9) -> keeps it, not the server default
        pgp, _t, _a, PP = menu("new")
        press(PP, "#SkyyMGrid", 53)
        e10["plain_ctrl"] = [tiles_of(pgp).get(46), tiles_of(pgp).get(47)]
        press(PP, "#SkyyMGrid", 0)
        press(PP, "#SkyyMGrid", 9)
        _pg, e10["plain"], _a, _P = menu("new")
        # a player's forged admin click (the button is not drawn for them)
        d0 = None if ML.DEF is None else list(ML.DEF)
        pgp.editClick(46, JStr("esrvsave"), JStr("esrvsave"))
        e10["forged"] = [str(pgp.status), d0 is not None and ML.DEF is not None and list(ML.DEF) == d0]
        pgp.editClick(47, JStr("esrvclear"), JStr("esrvclear"))
        e10["forged2"] = [str(pgp.status), ML.DEF is not None and list(ML.DEF) == d0]
        # a restart reads the server default file
        fresh()
        _pg, e10["rank_restart"], _a, _P = menu("new", RANK)
        # back to layout D
        pga2, _t, _a, PA2 = menu("new", OP)
        press(PA2, "#SkyyMGrid", 53)
        press(PA2, "#SkyyMGrid", 47)
        e10["arm2"] = [str(pga2.status), os.path.isfile(DEFF)]
        press(PA2, "#SkyyMGrid", 47)
        e10["cleared"] = str(pga2.status)
        settle()
        e10["file_after"] = os.path.isfile(DEFF)
        _pg, e10["rank_d"], _a, _P = menu("new", RANK)
        E["e10"] = e10
        # ---- E11 a hidden tile keeps its saved slot
        @JImplements("java.util.function.Function")
        class Unlock:
            def __init__(self, ans):
                self.ans = ans

            @JOverride
            def apply(self, u):
                return JBool.TRUE if self.ans else JBool.FALSE
        keys = [str(x) for x in MDn.E_KEY]
        body = "_v=1\n" + "".join("%s=%d\n" % (KEY[n], (1 if n == "Bank" else s_)) for n, s_ in D_SLOT.items())
        settle()
        open(ownf(PLAIN), "w", encoding="utf8").write(body)
        fresh()
        BRG.put("bank:fn:unlocked", Unlock(False))
        pgh, th, _a, PH = menu("new")
        e11 = {"locked": th}
        press(PH, "#SkyyMGrid", 53)
        e11["edit"] = tiles_of(pgh)
        press(PH, "#SkyyMGrid", 13)
        press(PH, "#SkyyMGrid", 1)
        pgh.editClick(1, JStr("eslot"), None)
        pump(PH)
        e11["to_kept"] = [int(pgh.editSel), str(pgh.status)]
        press(PH, "#SkyyMGrid", 13)
        BRG.put("bank:fn:unlocked", Unlock(True))
        _pg, e11["open"], _a, _P = menu("new")
        BRG.remove("bank:fn:unlocked")
        settle()
        e11["file"] = layout_file(open(ownf(PLAIN), encoding="utf8").read())
        E["e11"] = e11
        # ---- E12 unknown / new / doubled / out-of-range lines
        lines = ["_v=1", "quests=27", "notatile=2"]
        for n, s_ in D_SLOT.items():
            if n == "Collections":
                continue                                   # a NEW tile: not in the file
            if n == "HUD Editor":
                s_ = 13                                    # doubled with Teleport (Teleport is the earlier entry)
            if n == "Guild":
                s_ = 99                                    # out of range
            lines.append("%s=%d" % (KEY[n], s_))
        open(ownf(PLAIN), "w", encoding="utf8").write("\n".join(lines) + "\n")
        fresh()
        _pg, t12, _a, _P = menu("new")
        E["e12"] = {"t": t12, "keys": keys, "lay": list(_pg.lay), "names": [str(x) for x in MDn.E_NAME], "view": [str(x) for x in MDn.E_VIEW]}
        # ---- E13 corrupt files
        e13 = {}
        bad_cases = [("garbage", b"\x00\xff\xfe this is not = a layout\n{{{\n"), ("notiles", b"_v=1\nquests=4\n"), ("future", b"_v=2\nteleport=1\n")]
        for tag, data in bad_cases:
            open(ownf(PLAIN), "wb").write(data)
            fresh()
            ML.WARNED.clear()                              # one warning per file per session: each case = a new session
            w0 = int(ML.WARNS)
            _pg, ta_, _a, _P = menu("new")
            _pg, tb_, _a, _P = menu("new")
            for m_ in (ML.OWN,):
                m_.clear()
            _pg, tc_, _a, _P = menu("new")
            e13[tag] = {"first": ta_, "second": tb_, "third": tc_, "warns": int(ML.WARNS) - w0,
                        "untouched": open(ownf(PLAIN), "rb").read() == data}
        # the first change keeps the unreadable file as .bad
        open(ownf(PLAIN), "wb").write(bad_cases[0][1])
        fresh()
        pgc, _t, _a, PC = menu("new")
        press(PC, "#SkyyMGrid", 53)
        press(PC, "#SkyyMGrid", 13)
        press(PC, "#SkyyMGrid", 1)
        settle()
        e13["bad_kept"] = open(ownf(PLAIN) + ".bad", "rb").read() == bad_cases[0][1] if os.path.isfile(ownf(PLAIN) + ".bad") else False
        e13["new_file"] = layout_file(open(ownf(PLAIN), encoding="utf8").read()) if os.path.isfile(ownf(PLAIN)) else None
        # fix round: a second broken file later -> .bad-<time>, the first .bad stays as it was
        open(ownf(PLAIN), "wb").write(b"second broken one\n")
        fresh()
        ML.WARNED.clear()
        pgc2, _t, _a, PC2 = menu("new")
        press(PC2, "#SkyyMGrid", 53)
        press(PC2, "#SkyyMGrid", 13)
        press(PC2, "#SkyyMGrid", 1)
        settle()
        bads = sorted(f_ for f_ in os.listdir(LDIR) if f_.startswith(os.path.basename(ownf(PLAIN)) + ".bad"))
        e13["bad2"] = {"names": bads, "first_kept": open(ownf(PLAIN) + ".bad", "rb").read() == bad_cases[0][1],
                       "second": [open(os.path.join(LDIR, f_), "rb").read() == b"second broken one\n" for f_ in bads if f_.startswith(os.path.basename(ownf(PLAIN)) + ".bad-")]}
        for f_ in bads:
            os.remove(os.path.join(LDIR, f_))
        # a folder where the file should be (an IO error): layout D, editing refused, nothing renamed
        os.remove(ownf(PLAIN))
        os.makedirs(ownf(PLAIN))
        fresh()
        ML.WARNED.clear()
        w0 = int(ML.WARNS)
        _pg, td_, _a, _P = menu("new")
        ML.OWN.clear()
        r0 = int(ML.READS)
        pgf, td2_, _a, PF = menu("new")
        e13["folder"] = {"t": td_, "t2": td2_, "warns": int(ML.WARNS) - w0, "reread_gated": int(ML.READS) == r0}
        press(PF, "#SkyyMGrid", 53)
        e13["folder"]["edit"] = [bool(pgf.editing), str(pgf.status), bool(ML.unreadable(PLAIN)), ML.OWN.containsKey(JStr(str(PLAIN))),
                                 int(ML.BROKEN.size())]
        settle()
        e13["folder"]["still_dir"] = os.path.isdir(ownf(PLAIN)) and not [f_ for f_ in os.listdir(LDIR) if ".bad" in f_]
        os.rmdir(ownf(PLAIN))
        # a VALID file that cannot be read right now (another process holds a lock on it - antivirus / backup): layout D, editing refused,
        # NOT renamed; once it reads again (the 30 s re-read; here ERRAT cleared) the player's own layout is back
        import msvcrt
        good = "_v=1\n" + "".join("%s=%d\n" % (KEY[n], {"Teleport": 22, "Bazaar": 13}.get(n, s_)) for n, s_ in D_SLOT.items())
        open(ownf(PLAIN), "w", encoding="utf8").write(good)
        gb = open(ownf(PLAIN), "rb").read()
        fresh()
        ML.WARNED.clear()
        lf_ = open(ownf(PLAIN), "r+b")
        msvcrt.locking(lf_.fileno(), msvcrt.LK_NBLCK, len(gb))
        try:
            pgl, tl_, _a, PL_ = menu("new")
            press(PL_, "#SkyyMGrid", 53)
            e13["locked"] = {"t": tl_, "edit": [bool(pgl.editing), str(pgl.status)], "err": bool(ML.unreadable(PLAIN))}
            pgl.editClick(13, JStr("eslot"), None)        # a stale edit-mode click while unreadable
            pump(PL_)
            e13["locked"]["stale"] = [str(pgl.status), int(ML.DIRTY.size())]
        finally:
            lf_.seek(0)
            msvcrt.locking(lf_.fileno(), msvcrt.LK_UNLCK, len(gb))
            lf_.close()
        settle()
        e13["locked"]["untouched"] = open(ownf(PLAIN), "rb").read() == gb and not [f_ for f_ in os.listdir(LDIR) if ".bad" in f_]
        ML.ERRAT.clear()                                   # = 30 s later
        _pg, e13["locked"]["after"], _a, _P = menu("new")
        os.remove(ownf(PLAIN))
        # an unreadable server default
        open(DEFF, "wb").write(b"teleport=nope\n")
        ML.WARNED.clear()
        w0d = int(ML.WARNS)
        fresh()                                            # a start: loadDefault reads it
        ML.loadDefault()                                   # and again (still one warning)
        e13["def"] = {"def_none": ML.DEF is None, "broken": bool(ML.DEF_BROKEN), "warns": int(ML.WARNS) - w0d}
        _pg, e13["def"]["rank"], _a, _P = menu("new", RANK)
        pgd, _t, _a, PD = menu("new", OP)
        press(PD, "#SkyyMGrid", 53)
        press(PD, "#SkyyMGrid", 46)
        press(PD, "#SkyyMGrid", 46)
        settle()
        e13["def"]["bad_kept"] = os.path.isfile(DEFF + ".bad") and open(DEFF + ".bad", "rb").read() == b"teleport=nope\n"
        e13["def"]["new"] = layout_file(open(DEFF, encoding="utf8").read()) if os.path.isfile(DEFF) else None
        press(PD, "#SkyyMGrid", 47)
        press(PD, "#SkyyMGrid", 47)
        settle()
        e13["def"]["gone"] = not os.path.isfile(DEFF)
        E["e13"] = e13
        # ---- E14 upkeep: pruneOffline / flushAll
        ML.OWN.clear()
        ML.DIRTY.clear()
        ML.own(JStr(str(PLAIN)))
        ML.OWN.put(JStr(str(RANK)), JStr("none"))
        ML.DIRTY.put(JStr(str(RANK)), JBool.TRUE)
        online = HashSet()
        ML.pruneOffline(online)
        e14 = {"left": sorted(str(k) for k in ML.OWN.keySet())}
        ML.flushAll()
        e14["dirty"] = int(ML.DIRTY.size())
        ML.pruneOffline(online)
        e14["left2"] = sorted(str(k) for k in ML.OWN.keySet())
        Mod = JClass("java.lang.reflect.Modifier")
        e14["sync"] = [bool(Mod.isSynchronized(m_.getModifiers())) for m_ in ML.class_.getDeclaredMethods() if str(m_.getName()) in ("pruneOffline", "saveNow")]
        ML.ERRAT.put(JStr(str(RANK)), JClass("java.lang.Long")(1))
        ML.pruneOffline(online)
        e14["errat"] = int(ML.ERRAT.size())
        E["e14"] = e14
        # ---- E16 Hover Tooltips OFF: the Edit layout text in the info box first
        TIPSU = UUID.fromString("00000000-0000-0000-0000-0000000000b9")
        JV("new", "Tips").setOff(TIPSU, True)
        e16 = {"off": bool(JV("new", "Tips").isOff(TIPSU))}
        pgt, _t, _a, PT = menu("new", TIPSU)
        press(PT, "#SkyyMGrid", 53)
        e16["first"] = [bool(pgt.editing), str(pgt.cfgArm), str(pgt.infoName), str(pgt.infoBody), str(pgt.status)]
        press(PT, "#SkyyMGrid", 53)
        e16["second"] = [bool(pgt.editing), str(pgt.title)]
        E["e16"] = e16
        # ---- E17 the preload (MenuReady -> MenuLayout.preload -> LayoutSaveTask(load) on the scheduler)
        PREU = UUID.fromString("00000000-0000-0000-0000-0000000000ba")
        open(ownf(PREU), "w", encoding="utf8").write("_v=1\nteleport=40\ncollections=13\n")
        r0 = int(ML.READS)
        ML.preload(PREU)
        time.sleep(0.6)
        e17 = {"cached": ML.OWN.get(JStr(str(PREU))) is not None, "reads": int(ML.READS) - r0}
        try:
            ex_ = JClass("com.hypixel.hytale.server.core.HytaleServer").SCHEDULED_EXECUTOR
            e17["exec"] = "none" if ex_ is None else ("shutdown" if ex_.isShutdown() else "running")
        except Exception as x_:
            e17["exec"] = "error: " + str(x_)[:160]
        if not e17["cached"]:
            # the harness JVM has no running server scheduler: run the task the preload schedules (load mode) on this (non-world) thread
            JV("new", "LayoutSaveTask")(JStr(str(PREU)), True).run()
            e17["direct"] = [ML.OWN.get(JStr(str(PREU))) is not None, int(ML.READS) - r0]
        r1 = int(ML.READS)
        _pg, t17, _a, _P = menu("new", PREU)
        e17["draw_reads"] = int(ML.READS) - r1
        e17["t40"] = (t17.get(40) or [None])[0]
        ML.preload(PREU)                                   # cached: nothing scheduled
        time.sleep(0.3)
        e17["again"] = int(ML.READS) - r1
        os.remove(ownf(PREU))
        E["e17"] = e17
        # ---- E15 the other views
        for vw in ("tp", "mods", "players"):
            _pg, tv, av_, _P = menu("new", PLAIN, vw)
            _pg, tvp, avp, _P = menu("prev", PLAIN, vw)
            E["e15_" + vw] = [tv, tvp, av_, avp]
        # ================================================================================ ST: start twice on a COPY of the live data
        st = {}
        copy = os.path.join(SCRATCH, "livecopy", "Skyy_SkyyMenu")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, copy)
        else:
            os.makedirs(copy)
        st["live_files"] = len(snap(copy))
        ML.DIR = Paths.get(os.path.join(copy, "layouts"))
        ML.DEF_FILE = Paths.get(os.path.join(copy, "layout-default.properties"))
        settle()
        for m_ in (ML.OWN, ML.NAMES, ML.DIRTY, ML.BROKEN, ML.WARNED, ML.ERRAT):
            m_.clear()
        b0 = snap(copy)
        ML.loadDefault()
        _pg, st["start1"], _a, _P = menu("new")
        settle()
        st["start_writes_nothing"] = snap(copy) == b0
        pgs, _t, _a, PS = menu("new")
        press(PS, "#SkyyMGrid", 53)
        press(PS, "#SkyyMGrid", 13)
        press(PS, "#SkyyMGrid", 14)
        ML.flushAll()                                     # = shutdown()
        settle()
        b1 = snap(copy)
        for m_ in (ML.OWN, ML.NAMES, ML.DIRTY, ML.BROKEN, ML.WARNED, ML.ERRAT):
            m_.clear()
        ML.loadDefault()                                  # second start
        _pg, st["start2"], _a, _P = menu("new")
        settle()
        st["start2_writes_nothing"] = snap(copy) == b1
        st["changed"] = sorted(k for k in set(b0) | set(b1) if b0.get(k) != b1.get(k))
        st["warns"] = int(ML.WARNS)
        E["st"] = st
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ parent
def fails_of(text):
    return set(ln[len("FAIL "):] for ln in text.splitlines() if ln.startswith("FAIL "))


def nested(text):
    """the fails the 0.3.16 harness lists as unexpected new-only fails of ITS carry-forward (the 0.3.15 harness and below)"""
    out = set()
    for ln in text.splitlines():
        if ln.startswith("FAIL CF: on the 0.3.16 jar only") and "beyond the control: " in ln:
            rest = ln.split("beyond the control: ", 1)[1]
            try:
                i = rest.index("] [") + 1
                out |= set(ast.literal_eval(rest[:i])) | set(ast.literal_eval(rest[i + 1:]))
            except Exception:
                out.add(ln)
    return out


# the 0.3.16 harness's checks that the editor changes BY DESIGN on the 0.3.17 jar (each reason in the comment)
CF_EXPECTED = [
    r"^D9 the mods view = 0\.3\.15's",                # its norm knows 0.3.16 / 0.3.15 only: the SkyyMenu row says 0.3.17 (E15 checks the
    #                                                     Mods view = 0.3.16's with the version normalised)
    r"^CC: ",                                           # its class compare is 0.3.15 -> <jar>: + MenuLayout / LayoutSaveTask, the editor's
    #                                                     fields / methods, MenuPage.build (the edit-mode hint), nav / fill / click / ...
    r"^JT: the same class files",                       # + MenuLayout.class + LayoutSaveTask.class
    r"^JT: manifest = 0\.3\.15's but the version",      # its norm turns 0.3.15 into 0.3.16 only: this manifest says 0.3.17
]
CF_NESTED_EXPECTED = [
    r"^JT: the same class files",                       # the 0.3.15 harness (nested in the 0.3.16 one): + the two new class files
]


def carry_forward(env):
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, H16, "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        res[tag] = (fails_of(p.stdout or ""), p.stdout or "")
        open(os.path.join(SCRATCH, "..", "cf17-%s.log" % tag), "w", encoding="utf8").write(p.stdout or "")
    fn_, fc_ = res["new"][0], res["ctl"][0]
    extra = sorted(f for f in fn_ - fc_ if not f.startswith("CF: on the 0.3.16 jar only"))
    bad = [f for f in extra if not any(re.search(p_, f) for p_ in CF_EXPECTED)]
    nx = sorted(nested(res["new"][1]) - nested(res["ctl"][1]))
    nbad = [f for f in nx if not any(re.search(p_, f) for p_ in CF_NESTED_EXPECTED)]
    tot = re.search(r"SkyyMenu 0\.3\.16 harness: (\d+) ok, (\d+) fail", res["new"][1])
    totc = re.search(r"SkyyMenu 0\.3\.16 harness: (\d+) ok, (\d+) fail", res["ctl"][1])
    print("CF: 0.3.16 harness on 0.3.17: %s ok / %s fail; on 0.3.16 (control): %s ok / %s fail" % (
        tot.group(1) if tot else "?", tot.group(2) if tot else "?", totc.group(1) if totc else "?", totc.group(2) if totc else "?"))
    print("CF: control fails %d: %s" % (len(fc_), [f[:90] for f in sorted(fc_)]))
    print("CF: new-only fails %d: %s" % (len(extra), [e[:140] for e in extra]))
    print("CF: nested new-only %d: %s" % (len(nx), [e[:140] for e in nx]))
    check(tot is not None and totc is not None, "CF: both 0.3.16 harness runs finished")
    check(not bad and not nbad, "CF: on the 0.3.17 jar only the expected compare / class-file / manifest checks fail beyond the control: %s %s"
          % ([b_[:300] for b_ in bad], [b_[:300] for b_ in nbad]))


def check_e(E):
    ints = lambda t: dict((int(k), v) for k, v in t.items())
    # ---- E1
    e1 = E["e1"]
    tn, tp = ints(e1["new"]), ints(e1["prev"])
    check(dict((i, v) for i, v in tn.items() if i != 53) == tp, "E1 no saved layout: the main view = 0.3.16's (every slot but 53): %s" %
          sorted(set(tn) ^ set(tp)))
    t53 = tn.get(53)
    check(t53 is not None and t53[0] == "edit" and t53[1] == "Edit layout" and "Tool_Hammer_Iron" in e1["asked"],
          "E1 the Edit layout tile at 53 (bottom right, hammer icon): %s" % t53)
    body = (t53 or ["", "", ""])[2]
    check("Dragging does NOT work" in body and "click a tile, then click the slot you want it in - the two swap" in body
          and "Reset puts everything back" in body and "no dragging" in e1["edit_foot"],
          "E1 (Skyy LOCKED) the Edit layout text says plainly that dragging does not work, click + click swaps, Reset puts it back: %r" % body)
    check(tn.get(49, [None])[0] == "close" and 45 not in tn, "E1 Close stays at 49, nothing at 45 on the normal main view")
    check(e1["files"] == [], "E1 opening the menu writes no layout file: %s" % e1["files"])
    print("E1. Edit layout tooltip: %r / foot %r" % (body, e1["edit_foot"]))
    # ---- E2
    e2 = E["e2"]
    t2 = ints(e2["tiles"])
    check(e2["editing"] and e2["title"] == "Edit layout - SkyWynn Menu" and "no dragging" in e2["status"].lower()
          and e2["info"] == "Editing your layout" and "No dragging here" in e2["infobody"] and "You are using: the standard layout." in e2["infobody"],
          "E2 edit mode: title, status and info box say no dragging (+ which layout): %s / %s / %s" % (e2["title"], e2["status"], e2["info"]))
    check(e2["hint_sent"], "E2 the hint line sent to the client = the edit-mode hint (%r)" % e2["hint"])
    check(all(t2.get(i, [None])[0] == "eslot" for i in range(45) if i not in (3, 36, 44)), "E2 every visible slot 0 - 44 is clickable in edit mode: %s" %
          [i for i in range(45) if t2.get(i, [None])[0] != "eslot"])
    kept = sorted(i for i in range(45) if i not in t2)
    empty = sorted(i for i in range(45) if i in t2 and t2[i][1] == "Empty slot")
    check(kept == [3, 36, 44] and not any("Kept" in v[1] or "admins only" in v[2] for v in t2.values()),
          "E2 (fix round) the slots of tiles a player cannot see (Pets 3, Wardrobe 36, Server Setup 44) are NOT drawn - no Kept slot, nothing named: %s" % kept)
    check(empty == sorted(set(range(45)) - set(D_SLOT.values())), "E2 every other free slot is an Empty slot (27 / 39 / 41 too): %s" % empty)
    check([base_name(t2[s][1]) for s in (13, 22, 0)] == ["Teleport", "Bazaar", "Players"] and "No dragging" in t2[13][2],
          "E2 the tiles stay where they are, with the click-then-click text")
    check(t2.get(52, [None])[:2] == ["edone", "Done"] and 53 not in t2 and t2.get(45, [None])[:2] == ["ereset", "Reset to default"] and 46 not in t2
          and 47 not in t2 and t2.get(49, [None])[0] == "close", "E2 row 5: Reset 45, Close 49, Done 52, 53 empty; no admin buttons for a player")
    check("Editor_Empty" in e2["asked"] and "Editor_Block" not in e2["asked"], "E2 the empty markers draw their icon; no kept marker")
    check(e2["dbl"][0] and e2["dbl"][1], "E2 (fix round) a double-click on Edit layout stays in edit mode (53 is empty there): %s" % e2["dbl"])
    # ---- E3
    e3 = E["e3"]
    t3 = ints(e3["t"])
    check(e3["sel"] == 13 and e3["name13"] == "[Moving] Teleport" and e3["info"] == "Moving: Teleport" and "Picked up Teleport" in e3["status_pick"],
          "E3 the first click picks Teleport up (marked [Moving], info + status): %s" % [e3["sel"], e3["name13"], e3["info"]])
    check(e3["sel_after"] == -1 and e3["status"] == "Teleport and Bazaar swapped places." and base_name(t3[22][1]) == "Teleport"
          and base_name(t3[13][1]) == "Bazaar", "E3 the second click swaps Teleport (13) and Bazaar (22): %s" % e3["status"])
    f3 = layout_file(e3["file"] or "")
    want3 = dict((KEY[n], str(s_)) for n, s_ in D_SLOT.items())
    want3.update({"teleport": "22", "bazaar": "13"})
    check(f3.get("_v") == "1" and f3.get("_name") == "SkyyHarness" and dict((k, v) for k, v in f3.items() if not k.startswith("_")) == want3,
          "E3 saved in layouts/<uuid>.properties: _v=1, _name, every tile=slot with the swap: %s" % sorted(set(f3.items()) ^ set(want3.items()))[:6])
    check(e3["writes"] >= 1, "E3 the save ran (LayoutSaveTask / saveNow): %d" % e3["writes"])
    fr = ints(e3["fresh"])
    check(fr.get(22, [None])[0] == "view:tp" and base_name(fr.get(13, [None, ""])[1]) == "Bazaar" and e3["tp_view"] == "tp",
          "E3 a fresh menu draws the saved layout; Teleport (no lock) works from slot 22: %s" % e3["tp_view"])
    # ---- E4
    e4 = E["e4"]
    check(e4["sel"] == -1 and e4["status"] == "Cancelled - nothing moved." and e4["writes"] == 0 and e4["same"] and base_name(e4["name4"]) == "Skills",
          "E4 clicking the picked-up tile again cancels: nothing moved, nothing written: %s" % e4)
    # ---- E5
    e5 = E["e5"]
    t5 = ints(e5["t"])
    check(e5["status"] == "Skills moved." and base_name(t5[1][1]) == "Skills" and t5[4][1] == "Empty slot",
          "E5 an empty slot as target: Skills moves 4 -> 1, slot 4 is empty: %s" % e5["status"])
    # ---- E6
    e6 = E["e6"]
    check(e6["press_hidden"] == [-1, True, True], "E6 (fix round) a hidden tile's slot is not clickable (no action, nothing happens): %s" % e6["press_hidden"])
    check(e6["pick_kept"][0] == -1 and "cannot be used" in e6["pick_kept"][1], "E6 a stale click cannot pick a hidden slot up: %s" % e6["pick_kept"])
    check(e6["pick_empty"][0] == -1 and "Click a tile first" in e6["pick_empty"][1], "E6 an empty slot first -> click a tile first: %s" % e6["pick_empty"])
    check(e6["press_to_hidden"] == 0 and e6["to_kept"][0] == 0 and "cannot be used" in e6["to_kept"][1] and e6["to_kept"][2] == "[Moving] Players",
          "E6 a hidden slot is no target; the picked-up tile stays picked up: %s" % e6["to_kept"])
    check(e6["cancel"] == -1 and e6["file"].get("serversetup") == "44" and e6["file"].get("players") == "0",
          "E6 nothing moved: Server Setup keeps 44, Players 0")
    # ---- E7
    e7 = E["e7"]
    t7 = ints(e7["rank"])
    check(dict((i, v) for i, v in t7.items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45),
          "E7 another player still sees layout D (layouts are per player)")
    check(e7["files"] == ["00000000-0000-0000-0000-0000000000b1.properties"] and e7["plain_own"] and not e7["rank_own"],
          "E7 only the editing player's file exists (account uuid): %s" % e7["files"])
    # ---- E8
    e8 = E["e8"]
    check("again" in e8["arm"][0] and e8["arm"][1] == "ereset" and e8["disarmed"] in ("None", "null") and e8["after_one"],
          "E8 Reset: one click only asks, another click disarms, the file stays: %s" % e8["arm"])
    check(not e8["after_two"] and e8["status"] == "Every tile is back in its default slot.", "E8 two clicks: the player's file is deleted: %s" % e8["status"])
    t8 = ints(e8["t"])
    check(all(base_name(t8[s_][1]) == n for n, s_ in D_SLOT.items() if n not in ("Pets", "Wardrobe", "Server Setup")),
          "E8 every tile is back at its layout D slot (in edit mode)")
    check(dict((i, v) for i, v in ints(e8["fresh"]).items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45),
          "E8 a fresh menu after Reset = layout D")
    # ---- E9
    e9 = E["e9"]
    t9 = ints(e9["t"])
    check(not e9["editing"] and "saved" in e9["status"] and t9.get(53, [None])[0] == "edit" and t9.get(13, [None])[0] == "view:tp"
          and e9["title"] == "SkyWynn Menu" and e9["view"] == "tp", "E9 Done: edit mode off, the tiles work again (Teleport opens its view): %s" % e9)
    # ---- E10
    e10 = E["e10"]
    c = e10["admin_ctrl"]
    check(c[0] and c[0][:2] == ["esrvsave", "Save as server default"] and c[1] and c[1][:2] == ["esrvclear", "Server default: standard"]
          and c[2][0] == "ereset" and c[3][0] == "edone" and "Admins: Save as server default" in e10["admin_info"],
          "E10 an admin sees Save as server default (46) + Server default: standard (47): %s" % [x[:2] if x else x for x in c])
    check("Click again" in e10["arm"][0] and not e10["arm"][1] and e10["arm"][2], "E10 one click only asks: %s" % e10["arm"])
    check("Saved" in e10["saved"], "E10 two clicks save the admin's layout as the server default: %s" % e10["saved"])
    fd = e10["file"] or {}
    check(fd.get("_v") == "1" and fd.get("teleport") == "14" and fd.get("crafting") == "13" and "_name" not in fd,
          "E10 layout-default.properties holds the admin's layout (Teleport 14, Crafting 13): %s" % sorted(fd.items())[:5])
    tr = ints(e10["rank"])
    check(tr.get(14, [None])[0] == "view:tp" and base_name(tr.get(13, [None, ""])[1]) == "Crafting",
          "E10 a player without an own layout gets the server default")
    check(e10["plain_ctrl"] == [None, None], "E10 a player has no server-default buttons")
    tpl = ints(e10["plain"])
    check(base_name(tpl.get(9, [None, ""])[1]) == "Players" and base_name(tpl.get(0, [None, ""])[1]) == "Party"
          and base_name(tpl.get(13, [None, ""])[1]) == "Crafting",
          "E10 a player who edits starts from the server default and keeps their own layout (Players <-> Party)")
    check("Only admins" in e10["forged"][0] and e10["forged"][1] and "Only admins" in e10["forged2"][0] and e10["forged2"][1],
          "E10 a player's forged esrvsave / esrvclear is refused (the node is re-checked): %s %s" % (e10["forged"], e10["forged2"]))
    check(ints(e10["rank_restart"]).get(14, [None])[0] == "view:tp", "E10 after a restart the server default is read from its file")
    check("Click again" in e10["arm2"][0] and e10["arm2"][1] and "layout D" in e10["cleared"] and not e10["file_after"],
          "E10 Server default: standard, two clicks -> the file is deleted: %s" % e10["cleared"])
    check(dict((i, v) for i, v in ints(e10["rank_d"]).items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45),
          "E10 the player without an own layout is back on layout D")
    # ---- E11
    e11 = E["e11"]
    tl, te, to_ = ints(e11["locked"]), ints(e11["edit"]), ints(e11["open"])
    check(1 not in tl and 21 not in tl, "E11 Bank locked (unlock FALSE): its saved slot 1 is empty, 21 too")
    check(1 not in te and te.get(21, [None, ""])[1] == "Empty slot", "E11 edit mode: slot 1 (the locked Bank) not drawn, 21 = Empty slot")
    check(e11["to_kept"][0] == 13 and "cannot be used" in e11["to_kept"][1], "E11 the hidden tile's slot is no target: %s" % e11["to_kept"])
    check(base_name(to_.get(1, [None, ""])[1]) == "Bank" and 21 not in to_, "E11 unlock TRUE: Bank drawn at its saved slot 1")
    check(e11["file"].get("bank") == "1" and e11["file"].get("teleport") == "13", "E11 the file keeps bank=1 (nothing moved): %s" % e11["file"].get("bank"))
    # ---- E12
    e12 = E["e12"]
    t12 = ints(e12["t"])
    nm12 = dict((base_name(v[1]), i) for i, v in t12.items() if i < 45)
    # expected: the resolve rule in plain Python (entry order; doubled -> the earlier entry keeps it; out of range dropped; missing -> first free)
    names, view = e12["names"], e12["view"]
    base = {}
    for n, s_ in D_SLOT.items():
        if n == "Collections":
            continue
        base[n] = 13 if n == "HUD Editor" else (99 if n == "Guild" else s_)
    used, want = set(), {}
    order = [names[i] for i in range(len(names)) if view[i] == "main"]
    for n in order:
        s_ = base.get(n, -1)
        if 0 <= s_ < 45 and s_ not in used:
            want[n] = s_
            used.add(s_)
    for n in order:
        if n not in want:
            f_ = min(x for x in range(45) if x not in used)
            want[n] = f_
            used.add(f_)
    check(want["Teleport"] == 13 and want["HUD Editor"] == 1 and want["Collections"] == 2 and want["Guild"] == 6 and 27 not in used,
          "E12 (the rule itself) doubled / out-of-range / new tiles -> the first free slots in entry order: %s" %
          [(n, want[n]) for n in ("HUD Editor", "Guild", "Collections")])
    vis = dict((n, s_) for n, s_ in want.items() if n not in ("Pets", "Wardrobe", "Server Setup"))
    check(nm12 == vis, "E12 the player's view of that file = the rule: %s" % sorted(set(nm12.items()) ^ set(vis.items())))
    check(27 not in t12 and 26 not in t12, "E12 the unknown key quests=27 is ignored (27 stays empty); HUD Editor lost 13 to Teleport (26 empty)")
    check(all(e12["lay"][i] == want[names[i]] for i in range(len(names)) if view[i] == "main"), "E12 MenuLayout.of = the rule for every main tile")
    # ---- E13
    e13 = E["e13"]
    for tag in ("garbage", "notiles", "future"):
        x = e13[tag]
        same = lambda t: dict((i, v) for i, v in ints(t).items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45)
        check(same(x["first"]) and same(x["second"]) and same(x["third"]) and x["warns"] == 1 and x["untouched"],
              "E13 an unreadable layout file (%s) = layout D + exactly one warning over three opens, the file untouched: warns %d" % (tag, x["warns"]))
    check(e13["bad_kept"] and e13["new_file"] and e13["new_file"].get("teleport") == "1" and e13["new_file"].get("_v") == "1",
          "E13 the first change keeps the unreadable file as .bad and writes a fresh one: %s" % (e13["new_file"] or {}).get("teleport"))
    b2 = e13["bad2"]
    check(len(b2["names"]) == 2 and b2["first_kept"] and b2["second"] == [True],
          "E13 (fix round) a second broken file goes to .bad-<time>; the first .bad is not overwritten: %s" % b2["names"])
    fo = e13["folder"]
    check(fo["warns"] == 1 and dict((i, v) for i, v in ints(fo["t"]).items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45)
          and fo["t"] == fo["t2"] and fo["reread_gated"], "E13 a folder where the file should be (read error) = layout D + one warning, not re-read each draw: %d" % fo["warns"])
    check(not fo["edit"][0] and "cannot be read right now" in fo["edit"][1] and fo["edit"][2] and not fo["edit"][3] and fo["edit"][4] == 0
          and fo["still_dir"], "E13 (fix round) a read error: editing refused, nothing cached as 'no layout', nothing renamed: %s" % fo["edit"])
    lk = e13["locked"]
    same_d = dict((i, v) for i, v in ints(lk["t"]).items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45)
    check(same_d and lk["err"] and not lk["edit"][0] and "cannot be read right now" in lk["edit"][1],
          "E13 (fix round) a VALID file locked by another process: layout D shown, Edit layout refused: %s" % lk["edit"])
    check("cannot be read right now" in lk["stale"][0] and lk["stale"][1] == 0 and lk["untouched"],
          "E13 (fix round) ... a stale edit click changes nothing; the valid file is NOT renamed to .bad: %s" % lk["stale"])
    la = ints(lk["after"])
    check(la.get(22, [None])[0] == "view:tp" and base_name(la.get(13, [None, ""])[1]) == "Bazaar",
          "E13 (fix round) once it reads again the player's own layout is back (Teleport 22)")
    dd = e13["def"]
    check(dd["def_none"] and dd["broken"] and dd["warns"] == 1, "E13 an unreadable server default = layout D + one warning: %s" % dd)
    check(ints(dd["rank"]).get(13, [None])[0] == "view:tp", "E13 players then get layout D")
    check(dd["bad_kept"] and dd["new"] and dd["new"].get("_v") == "1" and dd["gone"],
          "E13 an admin's save keeps the unreadable default as .bad; 47 twice deletes the new file")
    # ---- E14
    e14 = E["e14"]
    check(e14["left"] == ["00000000-0000-0000-0000-0000000000b3"] and e14["dirty"] == 0 and e14["left2"] == [],
          "E14 pruneOffline drops cached layouts of players who left but never a pending save; flushAll saves it: %s" % e14)
    check(e14["sync"] == [True, True] and e14["errat"] == 0,
          "E14 (fix round) pruneOffline + saveNow share the class lock; read-error marks of players who left are dropped: %s" % e14["sync"])
    # ---- E16
    e16 = E["e16"]
    f16 = e16["first"]
    check(e16["off"] and not f16[0] and f16[1] == "edit" and f16[2] == "Edit layout" and "Dragging does NOT work" in f16[3]
          and "no dragging" in f16[4], "E16 (fix round) tooltips OFF: the first click shows the no-dragging text in the info box and asks again: %s" % f16[:3])
    check(e16["second"][0] and e16["second"][1] == "Edit layout - SkyWynn Menu", "E16 the second click enters edit mode: %s" % e16["second"])
    # ---- E17
    e17 = E["e17"]
    print("E17. preload: %s" % e17)
    check(((e17["cached"] and e17["reads"] == 1) or (e17["exec"] != "running" and e17.get("direct") == [True, 1]))
          and e17["draw_reads"] == 0 and e17["t40"] == "view:tp" and e17["again"] == 0,
          "E17 (fix round) the join preload reads the file on the scheduler; the first draw reads nothing; a cached player is not re-read: %s" % e17)
    # ---- E15
    for vw in ("tp", "mods", "players"):
        tv, tvp, av_, avp = E["e15_" + vw]
        norm = lambda t: dict((i, [s_.replace(VERSION, "V").replace(PREV_VERSION, "V") for s_ in v]) for i, v in t.items())
        check(norm(tv) == norm(tvp) and av_ == avp and "53" not in tv, "E15 the %s view = 0.3.16's, no Edit layout tile: %d tiles" % (vw, len(tv)))
    # ---- ST
    st = E["st"]
    print("ST. live Skyy_SkyyMenu copy: %d files; changed by the edit: %s" % (st["live_files"], st["changed"]))
    check(st["start_writes_nothing"] and st["start2_writes_nothing"], "ST a start + opening the menu writes nothing (twice)")
    check(st["changed"] == ["layouts/00000000-0000-0000-0000-0000000000b1.properties"], "ST the edit wrote only that player's layout file: %s" % st["changed"])
    s2 = ints(st["start2"])
    check(s2.get(14, [None])[0] == "view:tp" and base_name(s2.get(13, [None, ""])[1]) == "Crafting", "ST after the second start the layout is still there")
    check(dict((i, v) for i, v in ints(st["start1"]).items() if i < 45) == dict((i, v) for i, v in tn.items() if i < 45) or st["live_files"] > 0,
          "ST the first start on the copy draws layout D (no layout files live yet)")


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

    def child(script, args_, out_, env_=None):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, script] + args_ + ["--out", out_, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env_ or env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---- CC
        rules = [[r"menu_0_3_17_patch", "menu_0_3_16_patch"]]
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
            check(cc["added"] == ["LayoutSaveTask", "MenuLayout"] and cc["gone"] == [], "CC: + exactly MenuLayout + LayoutSaveTask, none gone: %s %s"
                  % (cc["added"], cc["gone"]))
            fn = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            fg = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            mp = ["editSel:I", "editing:Z", "hid:[Z", "lay:[I", "occ:[I"]
            md = fn.get("MenuData", [])
            md_ok = ("E_KEY:[Ljava/lang/String;" in md and "LAY_GRID:I" in md and "EDIT_SLOT:I" in md and "EDIT_BODY:Ljava/lang/String;" in md
                     and all(re.match(r"^(E_KEY|LAY_GRID|EDIT_SLOT|CTRL_[A-Z]+|ICON_(EDIT|DONE|RESET|SRVSAVE|SRVCLEAR|EMPTY|KEPT)|[A-Z_]+_(NAME|BODY|FOOT|FOOT_PICK|FOOT_MOVE|MSG|INFO|INFO_NAME|INFO_ADMIN|TITLE|HINT|MOVING|ARM|WAIT)|EDIT_INFO|EDIT_HINT|EDIT_TITLE|EDIT_MOVING|KEPT_MSG):", f_) for f_ in md))
            check(sorted(fn) == ["MenuData", "MenuPage"] and fn["MenuPage"] == mp and md_ok and not fg,
                  "CC: new fields only MenuData (the editor's keys / slots / icons / texts) + MenuPage editing / editSel / lay / occ / hid, none gone: %s %s"
                  % (dict((k, v) for k, v in fn.items() if k != "MenuData"), [f_ for f_ in md][:4]))
            check(all(v["same_shape"] for v in cls_.values()), "CC: same supers / interfaces")
            struct = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else "") for x in v["structural"])) for c, v in cls_.items() if v["structural"])
            want = {"MenuData": ["<clinit>"],
                    "MenuPage": ["<init>", "build", "click", "editClick (new)", "editInfo (new)", "editMarks (new)", "editTile (new)",
                                 "fill", "fillStatic", "nav", "startEdit (new)"],
                    "SeenTick": ["run"], "MenuReady": ["accept"], "SkyyMenuPlugin": ["setup", "shutdown"]}
            print("CC. 0.3.16 -> 0.3.17 structural %s; constants only %s" % (struct, dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])))
            check(struct == want, "CC: structural changes = MenuData.<clinit>, MenuPage <init> / build / click / fill / fillStatic / nav + the new edit "
                  "methods, SeenTick.run, MenuReady.accept, SkyyMenuPlugin.setup / shutdown only: %s" % struct)
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            check(all(c == "SkyyMenuPlugin" or m_.startswith("<init>") for c, ms in const.items() for m_ in ms),
                  "CC: the other constant-only changes are the version strings: %s" % const)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn, np_ = set(n for n in zj.namelist() if not n.endswith(".class")), set(n for n in zp.namelist() if not n.endswith(".class"))
        check(nn == np_, "JT: the same asset files as 0.3.16: %s" % sorted(nn ^ np_))
        chg = sorted(n for n in np_ & nn if zj.read(n) != zp.read(n))
        check(chg == ["manifest.json"], "JT: every 0.3.16 asset byte-identical but the manifest: %s" % chg)
        mn, mpn = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mpn, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.16's but the version")
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(cn - cp_ == {"com/skyy/menu/MenuLayout.class", "com/skyy/menu/LayoutSaveTask.class"} and not (cp_ - cn),
              "JT: class files = 0.3.16's + MenuLayout + LayoutSaveTask: %s %s" % (sorted(cn - cp_), sorted(cp_ - cn)))
        # ---- A + E + ST
        r = child(me, ["--e"], os.path.join(SCRATCH, "e.json"))
        check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-2500:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check(r["perm_engine"] == [True, False, True, False], "E: the engine's hasPermission: op yes, plain no, holder yes, deny no: %s" % r["perm_engine"])
            check_e(r["E"])
        # ---- V (the 0.3.16 harness's validator child on the new jar)
        envv = dict(env)
        envv.pop("JAVA_TOOL_OPTIONS", None)
        v = child(H16, ["--v"], os.path.join(SCRATCH, "v.json"), envv)
        check(v is not None and "error" not in v, "V ran: %s" % (v or {}).get("error", "")[-2500:])
        if v:
            print("V. engine validators on 0.3.17: %d ok, %d fail(s)%s" % (v["oks"], len(v["fails"]), (": " + str([f_[:200] for f_ in v["fails"]])) if v["fails"] else ""))
            check(not v["fails"] and v["oks"] >= 5, "V: the engine's asset validators accept the 0.3.17 jar: %s" % v["fails"][:4])
            check(all((v.get("icons") or {}).values()) and len(v.get("icons") or {}) == 23, "V: every Skyy_Menu_Icon_<Name> is in the engine's item store")
        # ---- AA (the 0.3.16 harness's audit child on the new jar)
        aa = child(H16, ["--aa"], os.path.join(SCRATCH, "aa.json"))
        check(aa is not None, "AA: the audit child ran")
        if aa:
            print("AA. engine-access audit: %d references in %d classes (MenuPage %s, MenuLayout %s, LayoutSaveTask %s), refused %d; control refused %d; caller-sensitive %s" % (
                aa["refs"], aa["classes"], aa["per"].get("MenuPage"), aa["per"].get("MenuLayout"), aa["per"].get("LayoutSaveTask"), len(aa["refused"]),
                len(aa["control"]), aa["caller_sensitive"]))
            check(not aa["refused"] and aa["refs"] > 1000 and aa["per"].get("MenuLayout", 0) > 50 and aa["per"].get("LayoutSaveTask", 0) > 0,
                  "AA: every class / member reference (MenuLayout + LayoutSaveTask too) resolves under the JVM's own access rules: %s" % aa["refused"][:5])
            check(len(aa["control"]) >= 1, "AA: the control (a protected sendUpdate from another package) is refused")
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        ours = [c_ for c_ in chg if "0000000000b" in c_ or "layout" in c_]
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
