"""SkyyMenu 0.3.14 - bare-JVM harness for THE PETS TILE IN THE TOP BAR (tools/menu_0_3_14_patch.py).
Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in
the scratch folder; every jar gets its own class loader and they share the one skyy.bridge map. Nothing outside the scratch folder is
written (the live Skyy_SkyyMenu + Skyy_SkyyPets folders are checked afterwards).

    python SkyyMenu/test_skyymenu_0.3.14.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyMenu-0.3.14.jar] [--prev SkyyMenu-0.3.13.jar]

SECTIONS
  A   every class of both menu jars + SkyyPets 0.2 loads, verifies (-Xverify:all) and initialises
  CC  CLASS COMPARE 0.3.13 -> 0.3.14 (javassist text of every method): added only PetTile; structural only MenuPage.fillStatic (the
      tile), SkyyMenuPlugin.setup (PetTile.DIR) and MenuData.<clinit> (the tile + PET_KIND / PET_ICON / ICON_PETS); the rest = constants
  JT  jar assets: + the 15 pet icon items (Server/Item/Items/Utility/Skyy_Menu_Icon_Pet_<Pet>.json, Variant, no Categories / Recipe /
      Interactions) + their PNGs (byte-identical to art/pets, under Icons/ItemsGenerated/SkyyMenu_Pet_<Pet>.png - never SkyyPets' names),
      the lang names; every 0.3.13 asset unchanged but the lang file + the manifest version
  PT  THE PETS TILE, EXECUTED through the engine's own PageManager (openCustomPage -> MenuPage.build -> fillStatic, the grid click ->
      MenuPage.click -> runCmd -> CommandManager.handleCommand), pet records written by the REAL SkyyPets 0.2 PetStore.save:
        PT1 SkyyPets absent (no pets:fn:onxp, no /pets), only another mod's /pets, only the bridge function -> slot 5 empty, every other
            main-menu slot = 0.3.13's (acts, names, icons asked)
        PT2 SkyyPets loaded, profile 1 (Rare Wolf Lv 12 in the pet slot, "Blinky" the Uncommon Void Eye Lv 5 in the summon slot):
            slot 5 = "Pets - Wolf Lv 12", the Wolf icon item, body lines (profile name, pet slot, summon slot, owned 2), all under 80
        PT3 click slot 5 -> /pets run as the player (the grid emptied first, the menu not closed: the Accessory Bag pattern)
        PT4 PROFILE SWITCH (profile:fn:key -> <uuid>-p2): "Pets - Fox Lv 3", the collar icon (no Fox art), owned 1; profile 3 (no file)
            -> "Pets", "Pet slot: empty", owned 0; back to profile 1 -> the Wolf again (per-profile, never the account)
        PT5 the record changes (REAL PetStore level 13) -> the next menu shows Lv 13 (cache by modified time + size)
        PT6 a bad record (no v=1, 0 bytes, a folder, over 1 MB) -> "Pets" + "could not be read", collar; PetTile.DIR null -> "none"
        PT7 a custom pet name with markup / quote characters -> made safe, cut to 24; a kind id with no art -> the collar
        PT8 the menu never writes the pet folder (bytes before = after)
  CF  CARRY-FORWARD: the 0.3.13 harness (every check since 0.3.x) on the 0.3.14 jar next to its control run on the 0.3.13 jar: the only
      new fails are its version / class-compare / asset-identical / manifest checks
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.14", "0.3.13"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menu0314", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREV_VERSION)))
PETS_JAR = os.path.join(ROOT, "SkyyPets", "SkyyPets-0.2.jar")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
LIVE_PETS = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyPets")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
PET_ART = ["Bear", "Boar", "Camel", "Chicken", "Goat", "Hawk", "Horse", "Mouflon", "Rabbit", "Ram", "Skrill", "Turkey", "Tusker",
           "Warthog", "Wolf"]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


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


# ============================================================================================ child: A + PT (one JVM)
def run_pt(out):
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import skyybuild as B
    S = sk()
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    S.jvm_start([hcls])
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR), ("pets", PETS_JAR)):
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

        # the stand-ins of test_skyymenu_0.3.10.py (packet sink, store, world, command system, item assets)
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

        UUID, Paths, ArrayList, HashMap, IdMap = (JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"),
                                                  JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"))
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
        for cn_ in ("island", "hub", "sacks", "accessories"):
            CM.cmds.put(cn_, U.allocateInstance(JClass("skyymenuharness.Cmd").class_))
        jf(CMGRc.class_, "instance").set(None, CM)
        ITc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        IMAP = U.allocateInstance(JClass("skyymenuharness.ItemMap").class_)
        IMAP.item = U.allocateInstance(ITc.class_)
        ISTORE = U.allocateInstance(JClass("skyymenuharness.Items").class_)
        ISTORE.map = IMAP
        jf(ITc.class_, "ASSET_STORE").set(None, ISTORE)

        def JV(k, n):
            return JClass(PKG + n, loader=L[k])
        mods = os.path.join(SCRATCH, "world", "mods")
        petdir = os.path.join(mods, "Skyy_SkyyPets", "pets")
        os.makedirs(petdir, exist_ok=True)
        for k in ("new", "prev"):
            JV(k, "PageGuard").STOP = False
            JV(k, "PageGuard").EXEC = None
            JV(k, "SetStore").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "settings-" + k))
            JV(k, "Tips").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "notips-" + k))
        PT_ = JV("new", "PetTile")
        PT_.DIR = Paths.get(petdir)
        BRG = JV("new", "MenuUtil").bridge()

        SKP = UUID.fromString("00000000-0000-0000-0000-0000000000a7")
        us = str(SKP)

        class Pl:
            pass

        def player():
            P = Pl()
            P.pr = U.allocateInstance(PR.class_)
            jf(PR.class_, "uuid").set(P.pr, SKP)
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

        def menu(k, P=None):
            """a fresh main menu of jar k opened through the engine -> (page, slot -> (act, name, body), the icon ids asked)"""
            P = P or player()
            IMAP.asked = ArrayList()
            pg = JV(k, "MenuPage")(P.pr, "main")
            P.pm.openCustomPage(P.ref, P.st, pg)
            pump(P)
            asked = [str(IMAP.asked.get(i)) for i in range(int(IMAP.asked.size()))]
            tiles = {}
            for i in range(54):
                a = pg.acts[i]
                if a is not None:
                    tiles[i] = (str(a), str(pg.names[i]), str(pg.bodies[i]))
            return pg, tiles, asked, P

        # ---- the pet records, written by the REAL SkyyPets 0.2 PetStore (its own Properties format, v=1, seq, sorted lines)
        PS, PRec = JClass("com.skyy.pets.PetStore", loader=L["pets"]), JClass("com.skyy.pets.PetRec", loader=L["pets"])
        PS.ROOT = Paths.get(os.path.join(mods, "Skyy_SkyyPets"))
        PS.DIR = Paths.get(petdir)

        def write(key, kv):
            r = PRec(key)
            for k_, v_ in kv.items():
                r.set(k_, v_)
            ok = bool(PS.save(r))
            return ok, r
        K1, K2, K3 = us, us + "-p2", us + "-p3"
        ok1, rec1 = write(K1, {"active.1": "wolf0001", "active.2": "eye00002", "pet.wolf0001.kind": "Wolf", "pet.wolf0001.level": "12",
                               "pet.wolf0001.rarity": "3", "pet.wolf0001.xp": "40", "pet.eye00002.kind": "VoidEye", "pet.eye00002.level": "5",
                               "pet.eye00002.rarity": "2", "pet.eye00002.name": "Blinky"})
        ok2, _r2 = write(K2, {"active.1": "fox00003", "pet.fox00003.kind": "Fox", "pet.fox00003.level": "3", "pet.fox00003.rarity": "1"})
        R["write"] = [ok1, ok2, sorted(os.listdir(petdir))]
        PROFILE = {"key": K1}

        @JImplements("java.util.function.Function")
        class KeyFn:
            @JOverride
            def apply(self, u):
                return PROFILE["key"]
        BRG.put("profile:fn:key", KeyFn())
        BRG.put("profile:name:" + us, "Apple")

        # ---- PT1 absent
        D = {}
        BRG.remove("pets:fn:onxp")
        _pg, tn, an, _P = menu("new")
        _pg, tp, ap, _P = menu("prev")
        D["absent"] = [5 in tn, tn == tp, sorted(set(an)) == sorted(set(ap)), sorted(tn)]
        CM.cmds.put("pets", U.allocateInstance(JClass("skyymenuharness.Cmd").class_))
        _pg, t1, _a, _P = menu("new")
        D["cmd_only"] = [5 in t1, t1 == tp]
        CM.cmds.remove("pets")
        BRG.put("pets:fn:onxp", JClass("com.skyy.pets.PetXpFn", loader=L["pets"])())
        _pg, t2, _a, _P = menu("new")
        D["bridge_only"] = [5 in t2, t2 == tp]
        # ---- PT2 present, profile 1
        CM.cmds.put("pets", U.allocateInstance(JClass("skyymenuharness.Cmd").class_))
        pg, t, a, P = menu("new")
        D["p1"] = [t.get(5), "Skyy_Menu_Icon_Pet_Wolf" in a, dict((i, v) for i, v in t.items() if i != 5) == tp,
                   [ln for ln in t[5][2].split("\n") if len(ln) >= 80] if 5 in t else None]
        # ---- PT3 click
        CM.lines.clear()
        press(P, "#SkyyMGrid", 5)
        D["click"] = [[str(CM.lines.get(i)) for i in range(int(CM.lines.size()))], bool(pg.cleared), P.pm.getCustomPage() is not None and bool(P.pm.getCustomPage().equals(pg)),
                      CM.last is not None and CM.last.act is not None and str(CM.last.act.getClass().getSimpleName()) == "CloseTask"]
        # ---- PT4 profile switch
        PROFILE["key"] = K2
        BRG.put("profile:name:" + us, "Banana")
        _pg, t, a, _P = menu("new")
        D["p2"] = [t.get(5), "Farming_Collar" in a, [x for x in a if x.startswith("Skyy_Menu_Icon_Pet_")]]
        PROFILE["key"] = K3
        BRG.remove("profile:name:" + us)
        _pg, t, a, _P = menu("new")
        D["p3"] = [t.get(5), "Farming_Collar" in a]
        PROFILE["key"] = K1
        BRG.put("profile:name:" + us, "Apple")
        _pg, t, a, _P = menu("new")
        D["back1"] = [t.get(5), "Skyy_Menu_Icon_Pet_Wolf" in a]
        # ---- PT5 a change by SkyyPets itself
        reads0 = int(PT_.READS)
        menu("new")
        D["cached"] = int(PT_.READS) == reads0
        time.sleep(0.05)
        rec1.set("pet.wolf0001.level", "13")
        D["save13"] = bool(PS.save(rec1))
        _pg, t, a, _P = menu("new")
        D["lv13"] = t.get(5)
        # ---- PT6 bad records
        bad = {}
        snap_before = snap(petdir)
        for what, maker in (("no v", lambda p: open(p, "w").write("pet.x.kind=Wolf\nactive.1=x\n")),
                            ("0 bytes", lambda p: open(p, "w").write("")),
                            ("v=2", lambda p: open(p, "w").write("v=2\nactive.1=x\npet.x.kind=Wolf\n")),
                            ("folder", lambda p: os.makedirs(p)),
                            ("2 MB", lambda p: open(p, "w").write("v=1\n" + "#" * 2100000 + "\n"))):
            kk = us + "-p9"
            fp = os.path.join(petdir, kk + ".properties")
            maker(fp)
            PROFILE["key"] = kk
            _pg, t, a, _P = menu("new")
            bad[what] = [t.get(5), "Farming_Collar" in a]
            if os.path.isdir(fp):
                os.rmdir(fp)
            else:
                os.remove(fp)
        D["bad"] = bad
        PROFILE["key"] = K1
        PT_.DIR = None
        D["nodir"] = list(PT_.of(SKP))
        PT_.DIR = Paths.get(petdir)
        # ---- PT7 a custom name with unsafe characters, a kind without art
        write(us + "-p4", {"active.1": "odd00004", "pet.odd00004.kind": "Mouse", "pet.odd00004.level": "250", "pet.odd00004.rarity": "9",
                           "pet.odd00004.name": 'Mr "Squeak" <b>{x};\\ the very long named mouse'})
        PROFILE["key"] = us + "-p4"
        _pg, t, a, _P = menu("new")
        D["odd"] = [t.get(5), "Farming_Collar" in a]
        PROFILE["key"] = K1
        R["PT"] = D
        R["pets_after"] = sorted(snap(petdir))
        R["unchanged_by_menu"] = all(snap(petdir).get(k_) == v_ for k_, v_ in snap_before.items())
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ parent
def fails_of(text):
    return set(ln[len("FAIL "):] for ln in text.splitlines() if ln.startswith("FAIL "))


def nested(text):
    """the 0.3.12 harness fails the 0.3.13 harness lists as unexpected (its own carry-forward line), as a set"""
    import ast as _ast
    for ln in text.splitlines():
        if ln.startswith("FAIL CF: on the 0.3.13 jar only") and "unexpected " in ln:
            try:
                return set(_ast.literal_eval(ln.split("unexpected ", 1)[1]))
            except Exception:
                return set([ln])
    return set()


def carry_forward(env):
    """the 0.3.13 harness on the 0.3.14 jar next to its control run on the 0.3.13 jar. The control is NOT clean today (SET moved on since
    0.3.13 was built: Mods-list-behind-SET + settings-rows drift, F. SkyyMenu version 0.3.13 (SET)) - so the rule is: every fail of the new
    run that the control does not have must be an expected one (the class compares / asset-identical / manifest / version checks that a
    new tile + 30 new asset files change by design), including the 0.3.12-level fails the 0.3.13 harness lists as unexpected."""
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyymenu_0.3.13.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        res[tag] = (fails_of(p.stdout or ""), p.stdout or "")
    fn_, fc_ = res["new"][0], res["ctl"][0]
    extra = sorted(f for f in fn_ - fc_ if not f.startswith("CF: on the 0.3.13 jar only"))
    pats = [r"^CC: ", r"^JT: every asset file byte-identical", r"^JT: manifest = ", r"^JT2: "]
    bad = [f for f in extra if not any(re.search(p_, f) for p_ in pats)]
    nx = sorted(nested(res["new"][1]) - nested(res["ctl"][1]))
    npats = [r"^K\. ", r"^F\. 0\.3\.7: 26 mods \(SkyyMenu 0\.3\.14\)"]
    nbad = [f for f in nx if not any(re.search(p_, f) for p_ in npats)]
    m = re.search(r"checks passed per part: (.*)", res["new"][1])
    print("CF: control fails %d (SET drift); new-only fails %d: %s; nested new-only %d: %s; parts passed on 0.3.14: %s" % (
        len(fc_), len(extra), [e[:70] for e in extra], len(nx), [e[:70] for e in nx], (m.group(1)[:400] if m else "?")))
    check(len(fc_) <= 3, "CF: the control run on 0.3.13 has only the known SET-drift fails: %s" % [f[:120] for f in sorted(fc_)])
    check(not bad and not nbad, "CF: on the 0.3.14 jar only expected compare / asset / manifest / version checks fail beyond the control: %s %s"
          % ([b_[:300] for b_ in bad], [b_[:300] for b_ in nbad]))


def main():
    if "--pt" in sys.argv:
        return run_pt(arg("--out"))
    if "--cc" in sys.argv:
        return sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    for j in (JAR, PREV_JAR, PETS_JAR):
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
    live_before, livep_before = snap(LIVE), snap(LIVE_PETS)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---- CC
        rules = [[r"menu_0_3_14_patch", "menu_0_3_13_patch"]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})], os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            struct = dict((c, sorted(v["structural"])) for c, v in cls_.items() if v["structural"])
            check(cc["added"] == ["PetTile"] and not cc["gone"], "CC: added only PetTile: %s %s" % (cc["added"], cc["gone"]))
            check(all(v["same_shape"] and not v["fields_gone"] for v in cls_.values())
                  and dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"]) == {"MenuData": ["ICON_PETS:Ljava/lang/String;", "PET_ICON:[Ljava/lang/String;", "PET_KIND:[Ljava/lang/String;"]},
                  "CC: new fields only MenuData PET_KIND / PET_ICON / ICON_PETS: %s" % dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"]))
            check(struct == {"MenuData": ["<clinit>"], "MenuPage": ["fillStatic(Ljava/util/ArrayList;)V"], "SkyyMenuPlugin": ["setup()V"]},
                  "CC: structural changes = MenuPage.fillStatic, SkyyMenuPlugin.setup, MenuData.<clinit> only: %s" % struct)
            print("CC. 0.3.13 -> 0.3.14 changed: " + "; ".join("%s %s" % (c, [m.split("(")[0] for m in v["const_only"] + v["structural"]]) for c, v in sorted(cls_.items())))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn, np_ = set(n for n in zj.namelist() if not n.endswith(".class")), set(n for n in zp.namelist() if not n.endswith(".class"))
        want = set(["Server/Item/Items/Utility/Skyy_Menu_Icon_Pet_%s.json" % p for p in PET_ART] + ["Common/Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % p for p in PET_ART])
        check(nn - np_ == want and not (np_ - nn), "JT: + exactly the 15 pet icon items and PNGs: %s" % sorted((nn - np_) ^ want)[:6])
        check(all(zj.read(n) == zp.read(n) for n in np_ if n not in ("manifest.json", "Server/Languages/en-US/server.lang")),
              "JT: every 0.3.13 asset byte-identical (but the lang file + the manifest)")
        check(not [n for n in zj.namelist() if "SkyyPets_" in n], "JT: no SkyyPets_* file name in the jar (never SkyyPets' ids / files)")
        okp, oki = [], []
        for p in PET_ART:
            art = open(os.path.join(ROOT, "art", "pets", "Common", "Icons", "ItemsGenerated", "SkyyPets_Pet_%s.png" % p), "rb").read()
            okp.append(zj.read("Common/Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % p) == art)
            d = json.loads(zj.read("Server/Item/Items/Utility/Skyy_Menu_Icon_Pet_%s.json" % p))
            oki.append(d.get("Icon") == "Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % p and d.get("Variant") is True and
                       not any(k in d for k in ("Categories", "Recipe", "Interactions")))
        check(all(okp) and all(oki), "JT: the pet PNGs = art/pets byte for byte; items hidden (Variant, no Categories / Recipe / Interactions)")
        lg_n = zj.read("Server/Languages/en-US/server.lang").decode()
        lg_p = zp.read("Server/Languages/en-US/server.lang").decode()
        check(set(lg_p.splitlines()) <= set(lg_n.splitlines()) and all("server.items.Skyy_Menu_Icon_Pet_%s.name=%s" % (p, p) in lg_n for p in PET_ART),
              "JT: lang = 0.3.13's lines + the pet names")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.13's but the version")
        # ---- A + PT
        r = child(["--pt"], os.path.join(SCRATCH, "pt.json"))
        check(r is not None and "error" not in r, "PT ran: %s" % (r or {}).get("error", "")[-2500:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify, initialise %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            D = r["PT"]
            print("PT. records written by SkyyPets 0.2:", r["write"])
            check(r["write"][0] and r["write"][1], "PT: the REAL SkyyPets PetStore.save wrote both records")
            check(D["absent"][0] is False and D["absent"][1] and D["absent"][2] and 4 in D["absent"][3],
                  "PT1 SkyyPets absent: no slot 5, every other tile + icon = 0.3.13's: %s" % D["absent"])
            check(D["cmd_only"] == [False, True] and D["bridge_only"] == [False, True],
                  "PT1 another mod's /pets alone / the bridge function alone -> hidden: %s %s" % (D["cmd_only"], D["bridge_only"]))
            t5 = D["p1"][0]
            print("PT2. tile:", t5)
            check(t5 is not None and t5[0] == "cmdc:pets" and t5[1] == "Pets - Wolf Lv 12", "PT2 slot 5 = Pets - Wolf Lv 12, /pets: %s" % (t5,))
            body = t5[2] if t5 else ""
            check(body.split("\n") == ["Your pets on this profile (Apple). Click to see them all.", "Pet slot: Rare Wolf Lv 12",
                                       "Summon slot: Blinky (Uncommon Void Eye) Lv 5", "Pets owned: 2",
                                       "Pets stay on this profile - every profile has its own.", "Command: /pets (or /pet)"],
                  "PT2 the hover text: %r" % body)
            check(D["p1"][1] and D["p1"][2] and D["p1"][3] == [], "PT2 the Wolf icon item; every other tile = 0.3.13's; lines under 80: %s" % D["p1"][1:])
            check(D["click"][0] == ["pets"] and D["click"][1] and D["click"][2] and D["click"][3],
                  "PT3 click -> /pets run as the player, the grid emptied, the menu NOT closed (the page replaces it; CloseTask chained only on the command): %s" % D["click"])
            p2 = D["p2"][0]
            check(p2 is not None and p2[1] == "Pets - Fox Lv 3" and "(Banana)" in p2[2] and "Pet slot: Common Fox Lv 3" in p2[2]
                  and "Pets owned: 1" in p2[2] and "Summon slot" not in p2[2] and D["p2"][1] and not D["p2"][2],
                  "PT4 profile 2: Fox Lv 3, the collar (no Fox art), owned 1, no summon line: %s" % D["p2"])
            p3 = D["p3"][0]
            check(p3 is not None and p3[1] == "Pets" and "Pet slot: empty" in p3[2] and "Pets owned: 0" in p3[2]
                  and p3[2].startswith("Your pets on this profile. ") and D["p3"][1], "PT4 profile 3 (no file): Pets, empty, 0: %s" % D["p3"])
            check(D["back1"][0] is not None and D["back1"][0][1] == "Pets - Wolf Lv 12" and D["back1"][1], "PT4 back to profile 1: Wolf: %s" % D["back1"])
            check(D["cached"] and D["save13"] and D["lv13"] is not None and D["lv13"][1] == "Pets - Wolf Lv 13",
                  "PT5 an unchanged file is not read again; SkyyPets saves Lv 13 -> the next menu shows it: %s" % [D["cached"], D["lv13"]])
            for what, (tile, coll) in sorted(D["bad"].items()):
                check(tile is not None and tile[1] == "Pets" and "could not be read" in tile[2] and coll, "PT6 bad record (%s): %s" % (what, tile))
            check(D["nodir"][0] == "none", "PT6 no pet folder -> none: %s" % D["nodir"])
            od = D["odd"][0]
            check(od is not None and od[1].startswith("Pets - Mr 'Squeak' [b](x),/") and od[1].endswith(" Lv 100") and len(od[1]) <= len("Pets - ") + 24 + 7
                  and not re.search(r'["{};\\<>]', od[1] + od[2]) and "Mythic Mouse" in od[2] and D["odd"][1],
                  "PT7 an unsafe custom name made safe + cut to 24, level clamped 100, rarity clamped Mythic, Mouse -> the collar: %s" % (od,))
            check(r["unchanged_by_menu"], "PT8 the menu never wrote a pet record")
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        # the game may be running (Skyy playing: SkyyPets flushes XP every 30 s, SkyyMenu saves settings) - so the rule is: nothing of
        # OURS lands there (no file named after or containing the harness player / profile keys), every change is listed
        chg = []
        for d_, before in ((LIVE, live_before), (LIVE_PETS, livep_before)):
            after = snap(d_)
            chg += [os.path.basename(d_) + "/" + k_ for k_ in sorted(set(before) | set(after)) if before.get(k_) != after.get(k_)]
        ours = [c_ for c_ in chg if "0000000000a7" in c_ or (os.path.isfile(os.path.join(os.path.dirname(LIVE), c_)) and
                b"0000000000a7" in open(os.path.join(os.path.dirname(LIVE), c_), "rb").read())]
        if chg:
            print("NOTE: live files changed during the run (the game is running?): %s" % chg[:12])
        check(not ours, "the live Skyy_SkyyMenu + Skyy_SkyyPets folders got nothing from the harness: %s" % ours)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyMenu %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
