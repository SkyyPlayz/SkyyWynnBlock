"""SkyyHud 0.3.15 - bare-JVM harness for the SEASONS mover (tools/hud_0_3_15_patch.py: Dynamic Seasons' own widget in the layout editor).

    python SkyyHud/test_skyyhud_0.3.15.py [--jar <SkyyHud-0.3.15.jar>] [--old <SkyyHud-0.3.14.jar>] [--dir <scratch>] [--keep]

Build the jar first (python SkyyHud/build_skyyhud_0.3.15.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, java.io.tmpdir + TEMP/TMP in the scratch folder) with HytaleServer.jar + the HUD jar. Stand-ins (javassist classes made
HERE, never in any jar): the network (records packets), the world (queues its tasks), the store, and a FAKE of Dynamic Seasons'
DynamicSeasons.ui.SeasonsDisplay (same class name, key "DynSeasons_hud", zOrder 0, a build that appends their document path) - the REAL
engine classes do the rest (HudManager, CustomUIHud.update, the CustomHud packet, UICommandBuilder, Anchor). Every check EXECUTES the jar:
  A  every class of the 0.3.15 jar (and the 0.3.14 jar) loads + initializes under -Xverify:all
  D  Dynamic Seasons missing (no PluginManager answer): DS = 2, ready / tick / relayout do nothing, the editor, Widgets / Settings and the
     Settings page leave Seasons out; 40 players at their default spot with DS present: the tick queues NOTHING
  U  the command path against the fake HUD through the real HudManager: default = no packet; a move = ONE CustomHud (DynSeasons_hud,
     zOrder 0, clear = false) with ONE Set #HudBackground.Anchor carrying the SkyyHud anchor; ticks with nothing new send nothing (one
     task at most queued per player); DS re-creates its HUD -> the Set is re-sent once to the NEW object; Hide = off screen; back to the
     default spot = one Set with their anchor, then no task at all; another class under that key / no Player / another world's store ->
     nothing; a world change -> ready re-sends at once; the HUD object is never replaced (their full document never re-sent by us)
  E  the editor: Seasons box 96 x 320 drawn, dragged (layout moves, the mover is asked), no Size- / Size+ for it (other widgets keep them),
     Size clicks keep 100 %
  S  the Seasons settings page (kit markup proven, no underscores, 9 Snap to + Show + Default spot + Reset + Back bindings) and its clicks
  L  layout: the Seasons line saves / loads / exports / imports (fixed size 100 % always); skyyhud_main never draws it; the 0.3.14 jar reads
     a 0.3.15 file with every old widget intact and ignores Seasons (rollback)
  F  class bytes 0.3.14 vs 0.3.15: only the expected classes differ
  Z  the engine-access audit (every reference resolved from its own class: 0 refused)
Not testable without the game (UNVERIFIED): the client applying a Set Anchor on another plugin's HUD document, a negative anchor hiding it.
Default scratch folder: tools/dev/scratch/hud0315/harness (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3.15", "0.3.14"
PKG = "com.skyy.hud."
KEY, CLS = "DynSeasons_hud", "DynamicSeasons.ui.SeasonsDisplay"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0315", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


def old_harness():
    spec = importlib.util.spec_from_file_location("hud0313h", os.path.join(HERE, "test_skyyhud_0.3.13.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


def load_all(jar, res):
    from jpype import JClass
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    fails = []
    for n in names:
        try:
            Cls.forName(n, True, loader)
        except Exception as e:
            fails.append("%s: %s" % (n, e))
    res["classes"], res["load_fails"] = len(names), fails
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    return fu.get(None)


def fake_items(U, CPf, JClass):
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fk = CPf.makeClass("com.hypixel.hytale.assetstore.SkyyHudTestAssets15", CPf.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyHudTestAssets15() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    store = U.allocateInstance(fk.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)


# ======================================================================================================== child: the NEW jar
def run_new(jar, out):
    from jpype import JClass, JFloat, JDouble
    import skyybuild as B
    import skyyui as SUI
    hcls = os.path.join(SCRATCH, "hclasses")
    shutil.rmtree(hcls, ignore_errors=True)
    os.makedirs(hcls)
    _jvm_start([jar], [B.JAVASSIST, hcls])
    res = {"checks": [], "scen": {}}

    def chk(cond, what):
        res["checks"].append([bool(cond), what])
        if not cond:
            print("  child FAIL:", what)

    U = load_all(jar, res)
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return

    def jf(jcls, name):
        c = jcls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    def field(cls, name):
        return jf(cls.class_, name)

    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def make(name, sup, ctor, fields=(), methods=()):
        c = CP.makeClass(name, CP.get(sup))
        for fsrc in fields:
            c.addField(CtField.make(fsrc, c))
        c.addConstructor(CtNewConstructor.make(ctor, c))
        for msrc in methods:
            c.addMethod(CtNewMethod.make(msrc, c))
        c.writeFile(hcls)

    # ---- stand-ins (harness only)
    make("skyyhudharness.HarnessNet", "com.hypixel.hytale.server.core.io.PacketHandler",
         "public HarnessNet() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
         ["public java.util.ArrayList sent;"],
         ["public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
          "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}",
          "public void write(com.hypixel.hytale.protocol.ToClientPacket[] ps) {\n"
          "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  for (int i = 0; i < ps.length; i++) this.sent.add(ps[i]);\n}",
          "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
          "public String getIdentifier() { return \"harness\"; }"])
    make("skyyhudharness.HarnessWorld", "com.hypixel.hytale.server.core.universe.world.World",
         "public HarnessWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }",
         ["public java.util.ArrayList tasks;"],
         ["public void execute(java.lang.Runnable r) {\n  if (this.tasks == null) this.tasks = new java.util.ArrayList();\n  this.tasks.add(r);\n}"])
    make("com.hypixel.hytale.component.SkyyHudTestStore15", "com.hypixel.hytale.component.Store",
         "public SkyyHudTestStore15() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
         "(com.hypixel.hytale.component.IResourceStorage) null); }",
         ["public java.util.IdentityHashMap comps;"],
         ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
          "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
          "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
          "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
    # the FAKE of Dynamic Seasons' HUD class (its name, key and zOrder - harness only, never shipped)
    make(CLS, "com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud",
         "public SeasonsDisplay(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, \"%s\", 0); }" % KEY, [],
         ["protected void build(com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b) { b.append(\"Hud/SeasonsHUD.ui\"); }"])
    make("skyyhudharness.OtherHud", "com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud",
         "public OtherHud(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, \"%s\", 0); }" % KEY, [],
         ["protected void build(com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b) { }"])
    NET, HW = JClass("skyyhudharness.HarnessNet"), JClass("skyyhudharness.HarnessWorld")
    TSC = JClass("com.hypixel.hytale.component.SkyyHudTestStore15")
    SD, OH = JClass(CLS), JClass("skyyhudharness.OtherHud")
    fake_items(U, CP, JClass)

    H = lambda n: JClass(PKG + n)
    DL, DS_, DU, WL, Wid, LS, HMain, SP, EP, WP, Cfg, Plugin = (H("DsLink"), H("DsState"), H("DsUi"), H("WLayout"), H("Widgets"),
                                                               H("LayoutStore"), H("HudMain"), H("SettingsPage"), H("EditorPage"),
                                                               H("WidgetsPage"), H("HudCfg"), H("SkyyHudPlugin"))
    UUID, CHM, Paths = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    PRc, REFc, STOREc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef"), JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    HMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.hud.HudManager")
    WORLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    Transform = JClass("com.hypixel.hytale.math.vector.Transform")
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    JClass("java.lang.System").getProperties().put("skyy.bridge", CHM())

    nxt = [9000]

    def ctype():
        c_ = CTc()
        nxt[0] += 1
        field(CTc, "index").setInt(c_, nxt[0])
        field(CTc, "hashCode").setInt(c_, nxt[0])
        return c_
    CT_PR, CT_PLA = ctype(), ctype()
    uni = U.allocateInstance(Uni.class_)
    field(Uni, "playerRefComponentType").set(uni, CT_PR)
    field(Uni, "playersByUuid").set(uni, CHM())
    jf(Uni.class_, "instance").set(None, uni)
    em = U.allocateInstance(EMc.class_)
    field(EMc, "playerComponentType").set(em, CT_PLA)
    jf(EMc.class_, "instance").set(None, em)

    def make_world(name):
        w = U.allocateInstance(HW.class_)
        jf(WORLDc.class_, "name").set(w, name)
        return w

    def tasks(w):
        return 0 if w.tasks is None else int(w.tasks.size())

    def run_world(w):
        n = 0
        while w.tasks is not None and int(w.tasks.size()) > 0:
            t_ = w.tasks.get(0)
            w.tasks.subList(0, 1).clear()
            t_.run()
            n += 1
        return n

    def new_store(o, world):
        st = U.allocateInstance(TSC)
        comps = JClass("java.util.IdentityHashMap")()
        comps.put(CT_PR, o["pr"])
        if o.get("pl") is not None:
            comps.put(CT_PLA, o["pl"])
        allc = JClass("java.util.IdentityHashMap")()
        allc.put(o["ref"], comps)
        st.comps = allc
        es = U.allocateInstance(ESc.class_)
        field(ESc, "world").set(es, world)
        field(STOREc, "externalData").set(st, es)
        field(REFc, "store").set(o["ref"], st)
        o["st"], o["w"] = st, world
        return st

    def player(n, name, world, with_player=True):
        pr = U.allocateInstance(PRc.class_)
        field(PRc, "uuid").set(pr, UUID(0x5ce0, n))
        field(PRc, "username").set(pr, name)
        net = U.allocateInstance(NET.class_)
        field(PRc, "packetHandler").set(pr, net)
        field(PRc, "transform").set(pr, Transform(JDouble(0.5), JDouble(64.0), JDouble(0.5)))
        ref = U.allocateInstance(REFc.class_)
        field(PRc, "entity").set(pr, ref)
        pl, hm = None, None
        if with_player:
            pl = U.allocateInstance(PLAc.class_)
            hm = HMc()
            field(PLAc, "hudManager").set(pl, hm)
        o = {"pr": pr, "net": net, "ref": ref, "pl": pl, "hm": hm}
        new_store(o, world)
        return o

    IHC = JClass("java.lang.System")

    def same(x, y):
        return x is not None and y is not None and int(IHC.identityHashCode(x)) == int(IHC.identityHashCode(y))

    def mark(o):
        return 0 if o["net"].sent is None else int(o["net"].sent.size())

    def huds_since(o, i0):
        n_ = o["net"]
        ps = [] if n_.sent is None else [n_.sent.get(i) for i in range(i0, int(n_.sent.size()))]
        return [p_ for p_ in ps if str(p_.getClass().getSimpleName()) == "CustomHud"]

    def as4(c):
        return (str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                None if c.text is None else str(c.text))

    def anchor_of(p_):
        """the one Set #HudBackground.Anchor of a CustomHud update -> dict of its margins"""
        cs = [as4(c) for c in p_.commands]
        if len(cs) != 1 or cs[0][0] != "Set" or cs[0][1] != "#HudBackground.Anchor":
            return {"bad": cs}
        d = json.loads(cs[0][2])
        a = d.get("0", d)
        if isinstance(a, dict) and "Anchor" in a:
            a = a["Anchor"]
        return dict((k, int(v)) for k, v in a.items() if k in ("Top", "Bottom", "Left", "Right", "Width", "Height")) or {"raw": cs[0][2]}

    def one_update(o, i0):
        hs = huds_since(o, i0)
        if len(hs) != 1:
            return None, "%d CustomHud packets" % len(hs)
        p_ = hs[0]
        if str(p_.hudId) != KEY or int(p_.zOrder) != 0 or bool(p_.clear):
            return None, "packet %s z%d clear=%s" % (p_.hudId, int(p_.zOrder), bool(p_.clear))
        return anchor_of(p_), "ok"

    work = os.path.join(SCRATCH, "child-new")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()

    def use_dir(name):
        d = os.path.join(work, name)
        os.makedirs(d, exist_ok=True)
        LS.DIR = Paths.get(os.path.join(d, "layouts"))
        LS.CACHE.clear()
        return d

    plugin = U.allocateInstance(Plugin.class_)
    field(Plugin, "huds").set(plugin, CHM())

    def reset_ds(v, ver="6.1.2"):
        DL.ST.clear()
        DL.DS = v
        DL.DSV = ver

    def ds_attach(o):
        """Dynamic Seasons' own show(): a NEW SeasonsDisplay through the real HudManager (their full document, clear = true)"""
        h = SD(o["pr"])
        o["hm"].addCustomHud(o["pr"], h)
        return h

    # ======================================================================== D: Dynamic Seasons missing
    use_dir("d1")
    W1 = make_world("default")
    a = player(1, "Ash", W1)
    reset_ds(0, "")
    DL.check()
    chk(int(DL.DS) == 2 and not bool(DL.present()), "D. no PluginManager answer -> DS = 2 (Dynamic Seasons missing), present() false")
    ds_attach(a)
    i0 = mark(a)
    DL.ready(a["pr"], a["st"])
    LS.get(a["pr"].getUuid()).get("Seasons").anchor = "tl"
    DL.relayout(a["pr"].getUuid())
    DL.tick()
    chk(DL.ST.isEmpty() and tasks(W1) == 0 and not huds_since(a, i0), "D. without Dynamic Seasons: ready / relayout / tick do nothing (no state, no task, no packet)")
    ids = [str(x) for x in Wid.edIds()]
    chk("Seasons" not in ids and "Minimap" in ids and len(ids) == len(list(Wid.IDS)) - 1, "D. the editor's widget list leaves Seasons out: %s" % ids)
    ep = EP(a["pr"], plugin)
    b_, ev_ = UCB(), UEB()
    ep.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    chk(not any(c[3] and "Seasons" in c[3] for c in cm) and not any("Seasons" in str(e.data) for e in ev_.getEvents()),
        "D. the editor page has no Seasons box / button / binding")
    wp = WP(a["pr"], plugin)
    b_, ev_ = UCB(), UEB()
    wp.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    chk(not any(c[3] and "SkyyWRowSeasons" in c[3] for c in cm), "D. Widgets / Settings has no Seasons row")
    sp_ = SP(a["pr"], plugin, "Seasons")
    b_, ev_ = UCB(), UEB()
    sp_.build(None, b_, ev_, None)
    chk(len(list(b_.getCommands())) == 0, "D. the Seasons Settings page builds nothing without Dynamic Seasons")
    chk("not installed" in str(DL.statusText()), "D. status text: %s" % DL.statusText())

    # ======================================================================== U: the command path against the fake HUD
    use_dir("u1")
    reset_ds(1)
    W1.tasks = None
    b = player(2, "Bea", W1)
    u = b["pr"].getUuid()
    h1 = ds_attach(b)
    full = huds_since(b, 0)
    chk(len(full) == 1 and bool(full[0].clear) and str(full[0].hudId) == KEY, "U. setup: the fake Dynamic Seasons HUD sent its full document once")
    i0 = mark(b)
    DL.ready(b["pr"], b["st"])
    chk(not huds_since(b, i0) and DL.ST.containsKey(u), "U1. at their own spot: ready sends nothing (state kept)")
    for _ in range(5):
        DL.tick()
    chk(tasks(W1) == 0, "U1. at their own spot: the tick queues NO task (zero cost)")
    # move via the settings page
    chk(int(DU.click(b["pr"], '{"a":"ds:an:tl"}')) == 2, "U2. Snap to TL saved")
    lay = LS.get(u).get("Seasons")
    chk(str(lay.anchor) == "tl" and int(lay.dx) == 8 and int(lay.dy) == 8, "U2. layout tl 8,8")
    DL.relayout(u)
    DL.relayout(u)
    DL.tick()
    chk(tasks(W1) == 1, "U2. a move queues ONE world task even when asked 3 times (got %d)" % tasks(W1))
    run_world(W1)
    a_, why = one_update(b, i0)
    chk(a_ == {"Top": 8, "Left": 8, "Width": 96, "Height": 320}, "U2. ONE update (DynSeasons_hud, z0, clear false) with ONE Set #HudBackground.Anchor (Top 8, Left 8, 96 x 320): %s %s" % (a_, why))
    chk(same(b["hm"].getCustomHud(KEY), h1), "U2. their HUD object is never replaced")
    i1 = mark(b)
    for _ in range(4):
        DL.tick()
        run_world(W1)
    chk(not huds_since(b, i1), "U3. ticks with nothing new send nothing")
    # Dynamic Seasons re-creates its HUD (their hide + show, or /season hud): a NEW object -> re-send once
    b["hm"].removeCustomHud(b["pr"], KEY)
    h2 = ds_attach(b)
    i2 = mark(b)
    DL.tick()
    run_world(W1)
    a_, why = one_update(b, i2)
    chk(a_ == {"Top": 8, "Left": 8, "Width": 96, "Height": 320} and not same(h2, h1), "U4. a NEW Dynamic Seasons HUD object gets the Set again once: %s %s" % (a_, why))
    DL.tick()
    run_world(W1)
    chk(len(huds_since(b, i2)) == 1, "U4. ... and only once")
    # Hide = off screen (their Visible flag untouched)
    i3 = mark(b)
    chk(int(DU.click(b["pr"], '{"a":"ds:en:0"}')) == 2 and not bool(LS.get(u).get("Seasons").en), "U5. Show Off saved")
    DL.relayout(u)
    run_world(W1)
    a_, why = one_update(b, i3)
    chk(a_ == {"Top": -4000, "Left": -4000, "Width": 96, "Height": 320}, "U5. hidden = ONE Set to off screen: %s %s" % (a_, why))
    cmds = [as4(c) for p_ in huds_since(b, i3) for c in p_.commands]
    chk(not any(c[1] and "Visible" in c[1] for c in cmds), "U5. their #HudBackground.Visible is never sent by us")
    # other anchors: every Snap to preset = the SkyyHud anchor maths
    chk(int(DU.click(b["pr"], '{"a":"ds:en:1"}')) == 2, "U6. Show On")
    # SkyyHud's own maths (Widgets.anchorSrcWH): a centred axis goes out as the nearest-edge margin, an exact tie to Right / Bottom
    want = {"tr": {"Top": 8, "Right": 8}, "bl": {"Bottom": 8, "Left": 8}, "br": {"Bottom": 8, "Right": 8},
            "t": {"Top": 8, "Right": 912}, "c": {"Bottom": 380, "Right": 912}, "b": {"Bottom": 8, "Right": 912},
            "l": {"Bottom": 380, "Left": 8}, "r": {"Bottom": 380, "Right": 8}}
    bad = []
    for an, wv in want.items():
        i4 = mark(b)
        DU.click(b["pr"], '{"a":"ds:an:%s"}' % an)
        DL.relayout(u)
        run_world(W1)
        a_, why = one_update(b, i4)
        wv = dict(wv, Width=96, Height=320)
        if a_ != wv:
            bad.append((an, a_, wv, why))
    chk(not bad, "U6. the 8 other Snap to presets send their anchor (centres resolved to the nearest edge): %s" % bad[:2])
    # back to their spot: one Set with THEIR anchor, then no task at all
    i5 = mark(b)
    chk(int(DU.click(b["pr"], '{"a":"ds:home"}')) == 2, "U7. Default spot saved")
    lay = LS.get(u).get("Seasons")
    chk(str(lay.anchor) == "br" and int(lay.dx) == 0 and int(lay.dy) == 250, "U7. layout = br 0,250")
    DL.relayout(u)
    run_world(W1)
    a_, why = one_update(b, i5)
    chk(a_ == {"Bottom": 250, "Right": 0, "Width": 96, "Height": 320}, "U7. ONE Set with their own anchor (Bottom 250, Right 0): %s %s" % (a_, why))
    for _ in range(5):
        DL.tick()
    chk(tasks(W1) == 0 and DL.ST.get(u).anc is None, "U7. then the tick queues nothing again")
    # another class under that key -> never touched
    DU.click(b["pr"], '{"a":"ds:an:tl"}')
    b["hm"].addCustomHud(b["pr"], OH(b["pr"]))
    i6 = mark(b)
    DL.relayout(u)
    run_world(W1)
    chk(not huds_since(b, i6) and DL.ST.get(u).hud is None, "U8. another plugin's HUD under that key (not their class): nothing sent")
    b["hm"].removeCustomHud(b["pr"], KEY)
    i6 = mark(b)
    DL.tick()
    run_world(W1)
    chk(not huds_since(b, i6), "U8. no Dynamic Seasons HUD at all: nothing sent")
    h3 = ds_attach(b)
    i7 = mark(b)
    DL.tick()
    run_world(W1)
    a_, why = one_update(b, i7)
    chk(a_ == {"Top": 8, "Left": 8, "Width": 96, "Height": 320}, "U8. it comes back -> the Set follows: %s" % (a_,))
    # world change: a task queued for the old world finds another store -> nothing; ready on the new world re-sends at once
    W2 = make_world("skywynn_z1")
    DL.relayout(u)
    new_store(b, W2)
    i8 = mark(b)
    run_world(W1)
    chk(not huds_since(b, i8), "U9. a task of the old world after a world change: store mismatch -> nothing")
    DL.ready(b["pr"], b["st"])
    a_, why = one_update(b, i8)
    chk(a_ == {"Top": 8, "Left": 8, "Width": 96, "Height": 320} and same(DL.ST.get(u).world, W2), "U9. ready in the new world re-sends at once: %s %s" % (a_, why))
    DL.tick()
    run_world(W2)
    chk(len(huds_since(b, i8)) == 1, "U9. ... once")
    # a player without a Player component / an invalid ref
    c = player(3, "Cid", W1, with_player=False)
    DL.ready(c["pr"], c["st"])
    LS.get(c["pr"].getUuid()).get("Seasons").anchor = "tl"
    DL.relayout(c["pr"].getUuid())
    run_world(W1)
    chk(not huds_since(c, 0), "U10. no Player component: nothing sent, no throw")
    # a reconnect (new PlayerRef, same uuid): a clean state - its client has their default spot
    b2 = player(2, "Bea", W1)
    ds_attach(b2)
    DL.ready(b2["pr"], b2["st"])
    a_, why = one_update(b2, 1)
    chk(same(DL.ST.get(u).pr, b2["pr"]) and a_ == {"Top": 8, "Left": 8, "Width": 96, "Height": 320}, "U11. a reconnect: new state, the Set sent to the new client: %s %s" % (a_, why))
    # a departed player is dropped by the tick
    field(PRc, "entity").set(b2["pr"], None)
    DL.tick()
    chk(not DL.ST.containsKey(u) or bool(b2["pr"].isValid()), "U12. an invalid PlayerRef is dropped by the tick (isValid=%s)" % bool(b2["pr"].isValid()))
    # 40 players at their own spot with Dynamic Seasons here: the tick queues nothing
    use_dir("u2")
    reset_ds(1)
    W3 = make_world("crowd")
    for k in range(40):
        o = player(100 + k, "P%d" % k, W3)
        ds_attach(o)
        DL.ready(o["pr"], o["st"])
    for _ in range(10):
        DL.tick()
    chk(tasks(W3) == 0 and int(DL.ST.size()) == 40, "U13. 40 players at their own spot: 10 ticks queue 0 tasks")
    res["scen"]["sent"] = int(DL.SENT.get())

    # ======================================================================== E: the editor
    use_dir("e1")
    reset_ds(1)
    W1.tasks = None
    e = player(5, "Eve", W1)
    ue = e["pr"].getUuid()
    ds_attach(e)
    DL.ready(e["pr"], e["st"])
    chk(list(Wid.edIds()) == list(Wid.IDS) and str(list(Wid.IDS)[-1]) == "Seasons", "E. with Dynamic Seasons the editor lists every widget, Seasons last")
    ep = EP(e["pr"], plugin)
    b_, ev_ = UCB(), UEB()
    ep.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    pv = [c[3] for c in cm if c[3] and "Group #SkyyEPvSeasons " in c[3]]
    chk(len(pv) == 1 and "Width: 64, Height: 213" in pv[0], "E. the editor draws the Seasons box at 2/3 of 96 x 320: %s" % (pv[:1],))
    chk(any('"sel:Seasons"' in str(e_.data) for e_ in ev_.getEvents()), "E. Select row has Seasons")
    cells = [i for i in range(576) if ep.cellWidget[i] is not None and str(ep.cellWidget[i]) == "Seasons"]
    chk(len(cells) == 1, "E. Seasons has a drag handle cell: %s" % cells)
    if cells:
        frm = cells[0]
        to = 2 * 32 + 1
        i0 = mark(e)
        ep.handleDataEvent(None, None, '{"a":"drop","SourceSlotId":%d,"SlotIndex":%d}' % (frm, to))
        ly = LS.get(ue).get("Seasons")
        chk(str(ly.anchor) == "tl" and int(ly.scale) == 100, "E. a drag moves Seasons to the top-left (anchor %s, %s, %s)" % (ly.anchor, ly.dx, ly.dy))
        chk(tasks(W1) == 1, "E. the drag asks the mover (one world task)")
        run_world(W1)
        a_, why = one_update(e, i0)
        chk(a_ is not None and a_.get("Top") == int(ly.dy) and a_.get("Left") == int(ly.dx), "E. ... and the Set follows the drag: %s %s" % (a_, why))
    ep.sel = "Seasons"
    b_, ev_ = UCB(), UEB()
    ep.build(None, b_, ev_, None)
    ids_ = [str(e_.selector) for e_ in ev_.getEvents()]
    chk("#SkyyEBSm" not in ids_ and "#SkyyEBSp" not in ids_ and "#SkyyEBCog" in ids_ and "#SkyyEBHide" in ids_,
        "E. Seasons selected: no Size- / Size+, Settings + Hide there")
    ep.handleDataEvent(None, None, '{"a":"act:Sp"}')
    chk(int(LS.get(ue).get("Seasons").scale) == 100, "E. a Size+ click on Seasons keeps 100 %")
    ep.sel = "Gclock"
    b_, ev_ = UCB(), UEB()
    ep.build(None, b_, ev_, None)
    ids_ = [str(e_.selector) for e_ in ev_.getEvents()]
    chk("#SkyyEBSm" in ids_ and "#SkyyEBSp" in ids_, "E. other widgets keep Size- / Size+")
    ep.sel = "Seasons"
    ep.handleDataEvent(None, None, '{"a":"act:Hide"}')
    chk(not bool(LS.get(ue).get("Seasons").en), "E. Hide from the editor")
    ep.handleDataEvent(None, None, '{"a":"show:Seasons"}')
    chk(bool(LS.get(ue).get("Seasons").en), "E. Show from the Hidden row")
    wp = WP(e["pr"], plugin)
    b_, ev_ = UCB(), UEB()
    wp.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    root = [c[3] for c in cm if c[3] and "Group #SkyyWidgets " in c[3]]
    chk(any(c[3] and "SkyyWRowSeasons" in c[3] for c in cm) and root and "Height: %d" % (150 + 62 * 14) in root[0],
        "E. Widgets / Settings lists Seasons (page %s)" % (root[0][:80] if root else None))

    # ======================================================================== S: the settings page
    sp_ = SP(e["pr"], plugin, "Seasons")
    b_, ev_ = UCB(), UEB()
    sp_.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    evs = [(str(x.selector), str(x.data)) for x in ev_.getEvents()]
    aps = [c for c in cm if c[0] == "AppendInline"]
    bad_mk = []
    for c in aps:
        try:
            SUI.check_markup(c[3], root=c[1] is None)
        except Exception as ex:
            bad_mk.append(str(ex)[:100])
    try:
        SUI.assert_proven([c[3] for c in aps], what="seasons settings as sent")
        prov = True
    except Exception as ex:
        prov = str(ex)[:200]
    chk(aps and not bad_mk and prov is True, "S. the Seasons page as sent: kit markup checks + every token proven: %s %s" % (bad_mk[:2], prov))
    chk(not any("_" in (c[3] or "").split("{")[0] for c in aps), "S. no underscore in an element id")
    pays = sorted(d for s_, d in evs)
    want_p = sorted(['{"a":"ds:%s"}' % p for p in ["en:1", "en:0", "home", "back", "reset"] + ["an:" + x for x in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br")]])
    chk([p.replace(" ", "") for p in pays] == want_p or len(evs) == 14, "S. 14 bindings: Show On / Off, 9 Snap to, Default spot, Reset, Back: %d %s" % (len(evs), pays[:3]))
    sets_ = dict((c[1], c[2]) for c in cm if c[0] == "Set")
    chk(any("6.1.2 found" in (v or "") for v in sets_.values()), "S. the status line says Dynamic Seasons 6.1.2 found")
    click = lambda p: int(DU.click(e["pr"], '{"a":"%s"}' % p))
    chk(click("ds:an:c") == 2 and str(LS.get(ue).get("Seasons").anchor) == "c", "S. Snap to C")
    chk(click("ds:an:zz") == 0 and click("ds:nope") == 0 and click("garbage") == 0 and int(DU.click(e["pr"], None)) == 0, "S. bad payloads -> 0")
    chk(click("ds:back") == 1, "S. Back = 1")
    click("ds:en:0")
    chk(click("ds:reset") == 2 and bool(LS.get(ue).get("Seasons").en) and str(LS.get(ue).get("Seasons").anchor) == "br"
        and int(LS.get(ue).get("Seasons").dy) == 250, "S. Reset = shown at their spot")

    # ======================================================================== L: layout
    d = use_dir("l1")
    lu = UUID(0x5ce0, 77)
    m = LS.get(lu)
    sl = m.get("Seasons")
    chk(bool(sl.en) and str(sl.anchor) == "br" and int(sl.dx) == 0 and int(sl.dy) == 250 and int(sl.bw) == 96 and int(sl.bh) == 320
        and bool(sl.fixed) and str(sl.ser()) == "1,br,0,250,100,1", "L. a new player's Seasons layout = their spot, 96 x 320, fixed: %s" % sl.ser())
    sl.anchor, sl.dx, sl.dy = "tl", 30, 40
    LS.save(lu)
    txt = open(os.path.join(d, "layouts", str(lu) + ".properties"), encoding="latin-1").read()
    chk("Seasons=1,tl,30,40,100,1" in txt, "L. saved line: %s" % [x for x in txt.splitlines() if x.startswith("Seasons")])
    open(os.path.join(d, "layouts", str(lu) + ".properties"), "w", encoding="latin-1").write(txt.replace("Seasons=1,tl,30,40,100,1", "Seasons=1,tl,30,40,170,1"))
    LS.CACHE.clear()
    sl = LS.get(lu).get("Seasons")
    chk(int(sl.scale) == 100 and bool(sl.fixed) and str(sl.anchor) == "tl" and int(sl.dx) == 30, "L. a hand-edited size 170 loads as 100 (fixed)")
    code = str(LS.export(lu))
    chk("Seasons=1:tl:30:40:100:1" in code, "L. export carries Seasons: %s" % code[-60:])
    n_ = int(LS.importCode(lu, "Seasons=1:bl:20:30:150:1"))
    sl = LS.get(lu).get("Seasons")
    chk(n_ == 1 and str(sl.anchor) == "bl" and int(sl.scale) == 100 and bool(sl.fixed) and int(sl.bh) == 320, "L. import: Seasons at bl, size forced 100, fixed")
    res["scen"]["line_for_old"] = "1,tl,30,40,100,1"
    # skyyhud_main never draws Seasons
    hm_ = HMain(e["pr"])
    i9 = mark(e)
    try:
        hm_.showNow()
        cm = [as4(c) for p_ in huds_since(e, i9) for c in p_.commands]
        chk(any(c[3] and "#SkyyWCoords" in c[3] for c in cm) and not any(c[3] and "SkyyWSeasons" in c[3] for c in cm),
            "L. skyyhud_main builds its widgets but never Seasons")
    except Exception as ex:
        chk(False, "L. HudMain.build threw %s" % ex)
    json.dump(res, open(out, "w"), indent=1)


# ======================================================================================================== child: the OLD jar
def run_old(jar, out, line):
    from jpype import JClass
    import skyybuild as B
    _jvm_start([jar], [B.JAVASSIST])
    res = {"checks": [], "scen": {}}

    def chk(cond, what):
        res["checks"].append([bool(cond), what])
    U = load_all(jar, res)
    fake_items(U, JClass("javassist.ClassPool")(True), JClass)
    H = lambda n: JClass(PKG + n)
    LS, Cfg = H("LayoutStore"), H("HudCfg")
    Paths = JClass("java.nio.file.Paths")
    work = os.path.join(SCRATCH, "child-old")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    Cfg.FILE = Paths.get(os.path.join(work, "config.properties"))
    Cfg.load()
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    d = os.path.join(work, "rb", "layouts")
    os.makedirs(d)
    u = JClass("java.util.UUID")(0x5ce0, 4242)
    old_lines = ["Coords=1,tl,8,8,120,1,gold,1,1,1,black", "Minimap=1,tr,8,40,125,1", "Gclock=1,bl,0,0,170,1"]
    open(os.path.join(d, str(u) + ".properties"), "w", encoding="latin-1").write("#x\n" + "\n".join(old_lines + ["Seasons=" + line]) + "\n")
    LS.DIR = Paths.get(d)
    LS.CACHE.clear()
    m = LS.get(u)
    got = dict((ln.split("=", 1)[0], str(m.get(ln.split("=", 1)[0]).ser())) for ln in old_lines)
    chk(all(got[ln.split("=", 1)[0]] == ln.split("=", 1)[1] for ln in old_lines) and m.get("Seasons") is None,
        "L. ROLLBACK: the 0.3.14 jar reads a 0.3.15 file: every old widget intact, Seasons ignored: %s" % got)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--run" in sys.argv:
        if arg("--mode") == "new":
            run_new(arg("--run"), arg("--out"))
        else:
            run_old(arg("--run"), arg("--out"), arg("--line"))
        return
    if "--bytecode" in sys.argv:
        old_harness().run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"), arg("--ov"), arg("--nv"))
        return
    if "--audit" in sys.argv:
        old_harness().run_audit(arg("--audit"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    common = ["--dir", SCRATCH]
    on = os.path.join(SCRATCH, "child-new.json")
    p = subprocess.run([sys.executable, me, "--run", JAR, "--out", on, "--mode", "new"] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(on), "child JVM for the %s jar ran (exit %s)" % (VERSION, p.returncode))
    if FAILS:
        return finish()
    new = json.load(open(on))
    check(not new["load_fails"], "A. %d classes of the %s jar load under -Xverify:all %s" % (new["classes"], VERSION, new["load_fails"][:3]))
    if new["load_fails"]:
        return finish()
    oo = os.path.join(SCRATCH, "child-old.json")
    p = subprocess.run([sys.executable, me, "--run", OLD_JAR, "--out", oo, "--mode", "old", "--line", new["scen"].get("line_for_old", "1,br,0,250,100,1")] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(oo), "child JVM for the %s jar ran (exit %s)" % (OLD_VERSION, p.returncode))
    old = json.load(open(oo)) if os.path.isfile(oo) else {"checks": [], "load_fails": ["missing"], "classes": 0}
    check(not old["load_fails"], "A. %d classes of the %s jar load under -Xverify:all" % (old["classes"], OLD_VERSION))
    for ok, what in new["checks"] + old["checks"]:
        check(ok, what)
    print("A-L. %d checks in the child JVMs (%d failed); Set updates sent in U: %s" % (len(new["checks"]) + len(old["checks"]),
          sum(1 for ok, w in new["checks"] + old["checks"] if not ok), new["scen"].get("sent")))
    # F: class bytes
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if os.path.isfile(bco):
        bc = json.load(open(bco))
        expect = {"WLayout", "Widgets", "HudMain", "EditorPage", "SettingsPage", "WidgetsPage", "SkyyHudPlugin", "TickTask", "AttachTask",
                  "LayoutStore", "HudCfg"}
        unexpected = []
        for n, r in bc.items():
            short = n.split("/")[-1][:-6]
            if short.startswith("Cfg"):
                if not r["version_only"] and short not in ("CfgRows", "CfgFn") and not (short == "CfgFile" and r["changed"] == ["<clinit>()V"]):
                    unexpected.append(short)
                continue
            if short not in expect:
                unexpected.append(short)
        check(not unexpected, "F. class bytes %s -> %s differ only in the expected classes: %s" % (OLD_VERSION, VERSION, unexpected))
        print("F. changed classes: %s" % ", ".join("%s (%d methods changed, %d new)" % (n.split("/")[-1][:-6], len(r["changed"]), len(r["new"]))
                                                  for n, r in sorted(bc.items())))
        zn = set(n for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class"))
        zo = set(n for n in zipfile.ZipFile(OLD_JAR).namelist() if n.endswith(".class"))
        added = sorted(n.split("/")[-1][:-6] for n in zn - zo)
        check(added == ["DsCheck", "DsLink", "DsState", "DsUi"] and not (zo - zn), "F. new classes DsCheck, DsLink, DsState, DsUi only; none removed: %s %s" % (added, sorted(zo - zn)))
        names = [n for n in zipfile.ZipFile(JAR).namelist()]
        check(not any("DynamicSeasons" in n or n.lower().endswith(".ui") for n in names), "F. the jar ships no Dynamic Seasons class and no .ui file")
    # Z: the engine-access audit
    auo = os.path.join(SCRATCH, "audit.json")
    p = subprocess.run([sys.executable, me, "--audit", JAR, "--out", auo] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran")
    if os.path.isfile(auo):
        au = json.load(open(auo))
        check(not au["refused"], "Z. engine-access audit: %d classes, %d references, 0 refused: %s" % (au["classes"], au["refs"], au["refused"][:3]))
        print("Z. audit: %d classes, %d references, %d refused" % (au["classes"], au["refs"], len(au["refused"])))
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    print("SkyyHud %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
