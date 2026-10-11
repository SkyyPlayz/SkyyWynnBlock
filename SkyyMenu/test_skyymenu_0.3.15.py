"""SkyyMenu 0.3.15 - bare-JVM harness for THE MENU ITEM WEARS THE NEW SKYWYNN EMBLEM (tools/menu_0_3_15_patch.py). Derived from
test_skyymenu_0.3.14.py. Child JVMs run the game's own JRE with HytaleServer.jar on the class path, -Xverify:all (A / MR), -XX:-UsePerfData,
TEMP / TMP / java.io.tmpdir in the scratch folder. Nothing outside the scratch folder is written (the live Skyy_SkyyMenu folder is
checked afterwards).

    python SkyyMenu/test_skyymenu_0.3.15.py --dir <empty folder inside tools/dev/scratch/> [--keep] [--no-cf]
         [--jar SkyyMenu-0.3.15.jar] [--prev SkyyMenu-0.3.14.jar]

SECTIONS
  CC  CLASS COMPARE 0.3.14 -> 0.3.15 (javassist text of every method): no class added / gone, no field added / gone, no method added /
      gone; the ONLY text difference beyond the version strings is MenuData.<clinit>'s one constant "Ingredient_Voidheart" -> "Skyy_Menu"
      (the Mods row icon) - checked line by line
  JT  jar assets: + exactly Common/Items/SkyyMenu/Skyy_Menu.blockymodel, Common/Items/SkyyMenu/Skyy_Menu_Texture.png,
      Common/Icons/ItemsGenerated/Skyy_Menu.png (= art/menu-emblem byte for byte = its manifest sha256 + bytes; none a vanilla path);
      Skyy_Menu.json: same path (same item id), same key order, only Icon / Model / Texture / Light colour changed to the fixed fields,
      Scale / PlayerAnimationsId / IconProperties / Light radius = the vanilla Voidheart's; every other asset byte-identical but the
      manifest (version only); no file names the Voidheart
  A   every class of both jars loads, verifies (-Xverify:all) and initialises
  MR  THE MODS ROW, EXECUTED through the engine's own PageManager (openCustomPage -> MenuPage.build -> fillMods -> put -> new ItemStack):
      the Mods view of 0.3.15 asks the item store for Skyy_Menu exactly where 0.3.14 asked for Ingredient_Voidheart, every other icon /
      name / body / action the same (version text aside); the main menu = 0.3.14's
  V   the ENGINE'S OWN ASSET VALIDATORS (test_skyymenu_0.3.12.py run_v: the vanilla pack, then the jar as its own pack - no failed store,
      no SEVERE / WARNING, every item in the store, Skyy_Menu's Model / Texture / Icon = the jar's, toPacket(), negative controls) + NEW:
      Skyy_Menu's packet carries the emblem Model / Texture / Icon, Scale 1.2, the Item animations, the icon framing and the #432 light
  CF  CARRY-FORWARD: the 0.3.14 harness (every check since 0.3.x, nested) on the 0.3.15 jar next to its control run on the 0.3.14 jar:
      the only new fails are the class-compare / asset-identical / manifest / version / menu-item-JSON checks the new look changes by design
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, hashlib, ast

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.15", "0.3.14"
PKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menu0315", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyMenu-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMenu")
ASSETS_ZIP = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
V_HARNESS = os.path.join(HERE, "test_skyymenu_0.3.12.py")
ART = os.path.join(ROOT, "art", "menu-emblem")
EMBLEM = ["Common/Items/SkyyMenu/Skyy_Menu.blockymodel", "Common/Items/SkyyMenu/Skyy_Menu_Texture.png", "Common/Icons/ItemsGenerated/Skyy_Menu.png"]
FIELDS = {"Icon": "Icons/ItemsGenerated/Skyy_Menu.png", "Model": "Items/SkyyMenu/Skyy_Menu.blockymodel",
          "Texture": "Items/SkyyMenu/Skyy_Menu_Texture.png", "Scale": 1.2, "PlayerAnimationsId": "Item",
          "IconProperties": {"Scale": 0.9, "Rotation": [0, 0, 0], "Translation": [0, -13]}, "Light": {"Color": "#432", "Radius": 1}}
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


# ============================================================================================ child: CC line diff of MenuData.<clinit>
def run_cl(out):
    """the javassist instruction text of every method of both jars (run_cc's text), line by line for the methods that differ"""
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
            for c in list(cc.getDeclaredConstructors()):
                d["%s.<init>%s" % (n.rsplit(".", 1)[-1], c.getSignature())] = text(c)
            ci = cc.getClassInitializer()
            if ci is not None:
                d["%s.<clinit>" % n.rsplit(".", 1)[-1]] = text(ci)
        res[tag] = d
    N, P = res["new"], res["prev"]
    diff = {}
    for k in sorted(set(N) | set(P)):
        a, b = P.get(k), N.get(k)
        if a == b:
            continue
        if a is None or b is None or len(a) != len(b):
            diff[k] = {"shape": [None if a is None else len(a), None if b is None else len(b)]}
            continue
        diff[k] = {"lines": [[x, y] for x, y in zip(a, b) if x != y]}
    json.dump(diff, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: A + MR (one JVM, -Xverify:all)
def run_mr(out):
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
        hclass("skyymenuharness.Cmd", "com.hypixel.hytale.server.core.command.system.AbstractCommand", "public Cmd() { super(\"x\", \"y\"); }", [],
               ["public boolean hasPermission(com.hypixel.hytale.server.core.command.system.CommandSender s) { return true; }",
                "protected java.util.concurrent.CompletableFuture execute(com.hypixel.hytale.server.core.command.system.CommandContext c) { return null; }"])
        hclass("skyymenuharness.Cmds", "com.hypixel.hytale.server.core.command.system.CommandManager", "public Cmds() { super(); }",
               ["public java.util.HashMap cmds;", "public java.util.ArrayList lines;"],
               ["public com.hypixel.hytale.server.core.command.system.AbstractCommand resolveCommand(String n) {\n"
                "  return this.cmds == null ? null : (com.hypixel.hytale.server.core.command.system.AbstractCommand) this.cmds.get(n);\n}",
                "public java.util.concurrent.CompletableFuture handleCommand(com.hypixel.hytale.server.core.command.system.CommandSender s, String line) {\n"
                "  if (this.lines == null) this.lines = new java.util.ArrayList();\n  this.lines.add(line);\n"
                "  return new java.util.concurrent.CompletableFuture();\n}"])
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
        for cn_ in ("island", "hub", "sacks", "accessories", "skymenu"):
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
        for k in ("new", "prev"):
            JV(k, "PageGuard").STOP = False
            JV(k, "PageGuard").EXEC = None
            JV(k, "SetStore").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "settings-" + k))
            JV(k, "Tips").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMenu", "notips-" + k))
            JV(k, "PetTile").DIR = Paths.get(os.path.join(mods, "Skyy_SkyyPets", "pets"))
        SKP = UUID.fromString("00000000-0000-0000-0000-0000000000a8")

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
            P.seen = 0
            return P

        def sent(P):
            return [] if P.net.sent is None else [P.net.sent.get(i) for i in range(int(P.net.sent.size()))]

        def pump(P):
            for p in sent(P)[P.seen:]:
                kind = str(p.getClass().getSimpleName())
                if kind in ("CustomPage", "SetPage"):
                    P.pm.handleEvent(P.ref, P.st, CPE(CPT.Acknowledge, None))
            P.seen = len(sent(P))

        def menu(k, view):
            """a fresh menu view of jar k opened through the engine -> (slot -> (act, name, body), the icon ids asked in draw order)"""
            P = player()
            IMAP.asked = ArrayList()
            pg = JV(k, "MenuPage")(P.pr, view)
            P.pm.openCustomPage(P.ref, P.st, pg)
            pump(P)
            asked = [str(IMAP.asked.get(i)) for i in range(int(IMAP.asked.size()))]
            tiles = {}
            for i in range(54):
                a = pg.acts[i]
                if a is not None:
                    tiles[i] = [str(a), str(pg.names[i]), str(pg.bodies[i])]
            sizes = [len(str(p.toString())) for p in sent(P) if str(p.getClass().getSimpleName()) == "CustomPage"]
            return tiles, asked, sizes
        D = {}
        for view in ("mods", "main"):
            tn, an, sn = menu("new", view)
            tp, ap, sp = menu("prev", view)
            D[view] = {"new": [tn, an, sn], "prev": [tp, ap, sp]}
        D["mod_icon"] = [str(x) for x in JV("new", "MenuData").MOD_ICON]
        D["mod_icon_prev"] = [str(x) for x in JV("prev", "MenuData").MOD_ICON]
        D["mod_name"] = [str(x) for x in JV("new", "MenuData").MOD_NAME]
        R["MR"] = D
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1)
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
        it = ITEM.getAssetMap().getAsset("Skyy_Menu")
        pk = it.toPacket()
        f = {}
        for n in ("model", "texture", "icon", "scale", "playerAnimationsId", "light", "iconProperties", "id"):
            try:
                v = getattr(pk, n)
                f[n] = None if v is None else str(v)
            except Exception as e:
                f[n] = "ERR %s" % str(e)[:100]
        R["packet"] = f

        def fields(o):
            """the declared instance fields of a protocol object, as text (ColorLight, AssetIconProperties)"""
            if o is None:
                return None
            d, c = {}, o.getClass()
            for fd in c.getDeclaredFields():
                if JClass("java.lang.reflect.Modifier").isStatic(fd.getModifiers()):
                    continue
                fd.setAccessible(True)
                v = fd.get(o)
                if v is not None and v.getClass().isArray():
                    v = [str(x) for x in v]
                elif v is not None and v.getClass().getName().startswith("com.hypixel"):
                    v = fields(v)
                else:
                    v = None if v is None else str(v)
                d[str(fd.getName())] = v
            return d
        R["light"], R["iconProps"] = fields(pk.light), fields(pk.iconProperties)
        R["packet_class"] = str(pk.getClass().getName())
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    R["fails"], R["oks"], R["known"] = list(m.FAILS), m.OKS[0], list(getattr(m, "KNOWN", []))
    json.dump(R, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================ parent
def fails_of(text):
    return set(ln[len("FAIL "):] for ln in text.splitlines() if ln.startswith("FAIL "))


def nested(text):
    """the fails the 0.3.14 harness lists as unexpected new-only fails of ITS carry-forward (the 0.3.13 harness and below)"""
    out = set()
    for ln in text.splitlines():
        if ln.startswith("FAIL CF: on the 0.3.14 jar only") and "beyond the control: " in ln:
            rest = ln.split("beyond the control: ", 1)[1]
            try:
                i = rest.index("] [") + 1
                out |= set(ast.literal_eval(rest[:i])) | set(ast.literal_eval(rest[i + 1:]))
            except Exception:
                out.add(ln)
    return out


# the 0.3.14 harness's checks the new look changes BY DESIGN on the 0.3.15 jar (each reason in the comment)
CF_EXPECTED = [
    r"^CC: ",                                           # its class compare is 0.3.13 -> <jar>: the version constant + the Mods row icon
    r"^JT: \+ exactly the 15 pet icon items and PNGs",  # + the 3 emblem files
    r"^JT: every 0\.3\.13 asset byte-identical",        # Skyy_Menu.json has the new look
    r"^JT: manifest = 0\.3\.13's but the version",      # the version is 0.3.15
]
CF_NESTED_EXPECTED = [
    r"^CC: ", r"^JT: every asset file byte-identical", r"^JT: manifest = ", r"^JT2: ",   # the 0.3.13 harness: compare / assets / manifest
    r"^K\. ", r"^K[4-7]\b", r"^F\. 0\.3\.7: 26 mods \(SkyyMenu 0\.3\.15\)",              # the 0.3.12 harness: K compares + the version
    r"^IC\b.*held look", r"^IC\b.*Voidheart", r"^V\b.*Voidheart",
]


def carry_forward(env):
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyymenu_0.3.14.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=env, capture_output=True, encoding="utf8", errors="replace")
        res[tag] = (fails_of(p.stdout or ""), p.stdout or "")
        open(os.path.join(SCRATCH, "..", "cf-%s.log" % tag), "w", encoding="utf8").write(p.stdout or "")
    fn_, fc_ = res["new"][0], res["ctl"][0]
    extra = sorted(f for f in fn_ - fc_ if not f.startswith("CF: on the 0.3.14 jar only"))
    bad = [f for f in extra if not any(re.search(p_, f) for p_ in CF_EXPECTED)]
    nx = sorted(nested(res["new"][1]) - nested(res["ctl"][1]))
    nbad = [f for f in nx if not any(re.search(p_, f) for p_ in CF_NESTED_EXPECTED)]
    tot = re.search(r"SkyyMenu 0\.3\.14 harness: (\d+) ok, (\d+) fail", res["new"][1])
    totc = re.search(r"SkyyMenu 0\.3\.14 harness: (\d+) ok, (\d+) fail", res["ctl"][1])
    print("CF: 0.3.14 harness on 0.3.15: %s ok / %s fail; on 0.3.14 (control): %s ok / %s fail" % (
        tot.group(1) if tot else "?", tot.group(2) if tot else "?", totc.group(1) if totc else "?", totc.group(2) if totc else "?"))
    print("CF: control fails %d: %s" % (len(fc_), [f[:90] for f in sorted(fc_)]))
    print("CF: new-only fails %d: %s" % (len(extra), [e[:110] for e in extra]))
    print("CF: nested new-only %d: %s" % (len(nx), [e[:110] for e in nx]))
    check(tot is not None and totc is not None, "CF: both 0.3.14 harness runs finished")
    check(not bad and not nbad, "CF: on the 0.3.15 jar only the expected compare / asset / manifest / version checks fail beyond the control: %s %s"
          % ([b_[:300] for b_ in bad], [b_[:300] for b_ in nbad]))


def main():
    if "--cl" in sys.argv:
        return run_cl(arg("--out"))
    if "--mr" in sys.argv:
        return run_mr(arg("--out"))
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
        # ---- CC (run_cc of the SkyySkills harness: classes / fields / methods) + the line diff
        rules = [[r"menu_0_3_15_patch", "menu_0_3_14_patch"]]
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
            check(all(v["same_shape"] and not v["fields_gone"] and not v["fields_new"] for v in cls_.values()),
                  "CC: no field added / gone, same supers: %s" % dict((c, (v["fields_new"], v["fields_gone"])) for c, v in cls_.items() if v["fields_new"] or v["fields_gone"]))
            struct = dict((c, sorted(v["structural"])) for c, v in cls_.items() if v["structural"])
            check(struct in ({}, {"MenuData": ["<clinit>"]}), "CC: at most MenuData.<clinit> differs beyond the version strings: %s" % struct)
            print("CC. 0.3.14 -> 0.3.15 changed: " + "; ".join("%s %s" % (c, [m.split("(")[0] for m in v["const_only"] + v["structural"]]) for c, v in sorted(cls_.items())))
        cl = child(["--cl"], os.path.join(SCRATCH, "cl.json"))
        check(cl is not None, "CC: the line-diff child ran")
        if cl is not None:
            other = {}
            for k, v in cl.items():
                if "shape" in v:
                    other[k] = v
                    continue
                rest = [ab for ab in v["lines"] if ab[0].replace(PREV_VERSION, "V").replace("menu_0_3_14_patch", "P")
                        != ab[1].replace(VERSION, "V").replace("menu_0_3_15_patch", "P")]
                if k == "MenuData.<clinit>":
                    check(rest == [['ldc "Ingredient_Voidheart"', 'ldc "Skyy_Menu"']],
                          "CC: MenuData.<clinit> differs in exactly one constant, the Mods row icon Ingredient_Voidheart -> Skyy_Menu: %s" % rest[:4])
                elif rest:
                    other[k] = rest[:3]
            check(not other, "CC: every other method of every class = 0.3.14's but the version strings (same length, same instructions): %s" % other)
            print("CC. instruction-level differences: %s" % sorted(cl))
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn, np_ = set(n for n in zj.namelist() if not n.endswith(".class")), set(n for n in zp.namelist() if not n.endswith(".class"))
        check(nn - np_ == set(EMBLEM) and not (np_ - nn), "JT: + exactly the 3 emblem files, nothing gone: %s %s" % (sorted(nn - np_), sorted(np_ - nn)))
        check(set(n for n in zj.namelist() if n.endswith(".class")) == set(n for n in zp.namelist() if n.endswith(".class")), "JT: the same class files")
        chg = sorted(n for n in np_ if zj.read(n) != zp.read(n))
        check(chg == ["Server/Item/Items/Utility/Skyy_Menu.json", "manifest.json"], "JT: every 0.3.14 asset byte-identical but Skyy_Menu.json + the manifest: %s" % chg)
        man = json.load(open(os.path.join(ART, "manifest.json"), encoding="utf8"))
        ents = dict((f["path"], f) for f in man["files"])
        av = zipfile.ZipFile(ASSETS_ZIP)
        van = set(av.namelist())
        for n in EMBLEM:
            data = zj.read(n)
            art = open(os.path.join(ART, *n.split("/")), "rb").read()
            check(data == art and hashlib.sha256(data).hexdigest() == ents[n]["sha256"] and len(data) == ents[n]["bytes"],
                  "JT: %s = art/menu-emblem byte for byte = its manifest sha256 + bytes" % n)
            check(n not in van, "JT: %s is no vanilla path (never overrides a vanilla file)" % n)
        check(not [n for n in zj.namelist() if "Voidheart" in n] and b"Voidheart" not in zj.read("Server/Item/Items/Utility/Skyy_Menu.json"),
              "JT: no jar file / item JSON names the Voidheart")
        y, x = json.loads(zj.read("Server/Item/Items/Utility/Skyy_Menu.json")), json.loads(zp.read("Server/Item/Items/Utility/Skyy_Menu.json"))
        vh = json.loads(av.read("Server/Item/Items/Ingredient/Ingredient_Voidheart.json").decode("utf-8-sig"))
        dk = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
        check(list(y) == list(x) and dk == ["Icon", "Light", "Model", "Texture"], "JT: Skyy_Menu.json = 0.3.14's keys in order; only Icon / Light / Model / Texture differ: %s" % dk)
        check(all(y[k] == v for k, v in FIELDS.items()), "JT: Skyy_Menu.json carries the fixed fields: %s" % dict((k, y.get(k)) for k in FIELDS))
        check(set(FIELDS) <= set(vh) and all(y[k] == vh[k] for k in ("Scale", "PlayerAnimationsId", "IconProperties")) and y["Light"]["Radius"] == vh["Light"]["Radius"]
              and set(y["Light"]) == set(vh["Light"]), "JT: every field is a vanilla Voidheart key; Scale / animations / icon framing / light radius = the Voidheart's")
        check(all(y[k] == x[k] for k in ("TranslationProperties", "Categories", "Quality", "Tags", "MaxStack", "Interactions")),
              "JT: same item id + path, name, description, quality, tags, MaxStack, right-click page (players' items just change look)")
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.14's but the version")
        # ---- A + MR
        r = child(["--mr"], os.path.join(SCRATCH, "mr.json"))
        check(r is not None and "error" not in r, "MR ran: %s" % (r or {}).get("error", "")[-2500:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            D = r["MR"]
            k = D["mod_name"].index("SkyyMenu")
            check(D["mod_icon"][k] == "Skyy_Menu" and D["mod_icon_prev"][k] == "Ingredient_Voidheart"
                  and [a for i, a in enumerate(D["mod_icon"]) if i != k] == [a for i, a in enumerate(D["mod_icon_prev"]) if i != k],
                  "MR: MenuData.MOD_ICON - only the SkyyMenu row changed (Ingredient_Voidheart -> Skyy_Menu)")
            tn, an, sn = D["mods"]["new"]
            tp, ap, sp = D["mods"]["prev"]
            print("MR. Mods view: %d tiles; icons asked 0.3.15 %d / 0.3.14 %d; SkyyMenu tile %s" % (
                len(tn), len(an), len(ap), [v[1] for v in tn.values() if v[1].startswith("SkyyMenu")]))
            check("Skyy_Menu" in an and "Ingredient_Voidheart" not in an and "Ingredient_Voidheart" in ap and "Skyy_Menu" not in ap,
                  "MR: the Mods view of 0.3.15 draws new ItemStack(\"Skyy_Menu\") (0.3.14: the Voidheart)")
            check([("Ingredient_Voidheart" if a_ == "Skyy_Menu" else a_) for a_ in an] == ap,
                  "MR: in the same draw position, every other icon the same: %s" % [(i, a_, b_) for i, (a_, b_) in enumerate(zip(an, ap)) if a_ != b_][:4])
            norm = lambda t: dict((i, [s_.replace(VERSION, "V").replace(PREV_VERSION, "V") for s_ in v]) for i, v in t.items())
            check(norm(tn) == norm(tp) and len(tn) >= 26, "MR: every Mods tile's action / name / text = 0.3.14's (version aside): %d tiles" % len(tn))
            mt, ma, _ms = D["main"]["new"]
            pt, pa, _ps = D["main"]["prev"]
            check(norm(mt) == norm(pt) and ma == pa and len(mt) > 10, "MR: the main menu = 0.3.14's (tiles + icons asked)")
            check(bool(sn) and bool(sp), "MR: both pages went out as CustomPage packets: %s %s" % (sn, sp))
        # ---- V
        envv = dict(env)
        envv.pop("JAVA_TOOL_OPTIONS", None)
        v = child(["--v"], os.path.join(SCRATCH, "v.json"), envv)
        check(v is not None and "error" not in v, "V ran: %s" % (v or {}).get("error", "")[-2500:])
        if v:
            print("V. engine validators (test_skyymenu_0.3.12 run_v) on 0.3.15: %d ok, %d fail(s)%s" % (v["oks"], len(v["fails"]),
                  (": " + str([f_[:200] for f_ in v["fails"]])) if v["fails"] else ""))
            check(not v["fails"] and v["oks"] >= 5, "V: the engine's asset validators accept the 0.3.15 jar (store load, items, Model / Texture / Icon, toPacket, controls): %s" % v["fails"][:4])
            if "packet" in v:
                f = v["packet"]
                print("V. Skyy_Menu packet (%s): %s" % (v.get("packet_class"), f))
                check(f.get("model") == FIELDS["Model"] and f.get("texture") == FIELDS["Texture"] and f.get("icon") == FIELDS["Icon"],
                      "V: Skyy_Menu's packet = the emblem Model / Texture / Icon: %s" % f)
                check(f.get("scale") is not None and abs(float(f["scale"]) - 1.2) < 1e-6 and f.get("playerAnimationsId") == "Item",
                      "V: Skyy_Menu's packet Scale 1.2, PlayerAnimationsId Item: %s %s" % (f.get("scale"), f.get("playerAnimationsId")))
                lt, ip = v.get("light") or {}, v.get("iconProps") or {}
                print("V. Skyy_Menu packet light %s, icon framing %s" % (lt, ip))
                # the engine's ColorLight: radius + a light LEVEL per channel (one hex digit each, 0 - 15): #432 = red 4, green 3, blue 2
                rgb = [int(lt.get(c_, "x")) if str(lt.get(c_, "x")).lstrip("-").isdigit() else None for c_ in ("red", "green", "blue")]
                check(str(lt.get("radius")) == "1" and rgb == [4, 3, 2], "V: Skyy_Menu's packet light = radius 1, levels red 4 / green 3 / blue 2 (#432): %s" % lt)
                check(ip and abs(float(ip.get("scale", "nan")) - 0.9) < 1e-6, "V: Skyy_Menu's packet icon framing scale 0.9 (+ translation / rotation): %s" % ip)
        # ---- CF
        if "--no-cf" not in sys.argv:
            carry_forward(env)
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        ours = [c_ for c_ in chg if "0000000000a8" in c_ or "0000000000a7" in c_]
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
