"""SkyyHud 0.3.16 - bare-JVM harness for the minimap fix round (tools/hud_0_3_16_patch.py: blank island, arrow in blocks, default spot).

    python SkyyHud/test_skyyhud_0.3.16.py [--jar <SkyyHud-0.3.16.jar>] [--old <SkyyHud-0.3.15.jar>] [--live <Skyy_SkyyHud folder>]
                                          [--dir <scratch>] [--keep]

Build the jar first (python SkyyHud/build_skyyhud_0.3.16.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, java.io.tmpdir + TEMP/TMP in the scratch folder) with HytaleServer.jar + the HUD jar. Stand-ins (javassist classes made
HERE, never in a jar): the network (records packets), the world (queues its tasks), the store - the REAL engine classes do the rest
(HudManager, CustomUIHud, MapImage / BitFieldArr, ClearWorldMap / UpdateWorldMap, CommonAsset, UICommandBuilder). Every check EXECUTES
the jar's own code:
  A  every class of the 0.3.16 jar (and the 0.3.15 jar) loads + initializes under -Xverify:all
  I  THE TWO-WORLD REPRO (Skyy 2026-10-06, log 18-40-21): the hub (13 x 13 window of distinct real pieces + markers) filled, then the
     engine's world change exactly as it runs (resetHud -> ClearWorldMap -> the island's burst -> ready): a Void island whose window is
     ALL-transparent pieces (the engine's rgba 0 void columns, many of them the hub's chunk coordinates) except chunk (0,0) = the island.
     0.3.16: no slot shows a hub picture, the island picture sits in chunk (0,0) under the player (grid maths), every void slot is the
     backdrop, no void picture is encoded or sent, the fill line says "1 of 169 ... 168 empty", hub markers gone, the arrow (8 px) is
     smaller than the island's 15 px piece. The same with a tick between the burst and ready (the race), and with NO ClearWorldMap
     (defensive: forgotten + one log line). A world with ONLY void pieces: no attach, one log line, attaches when the island piece comes.
     The 0.3.15 jar on the same repro (the bug): attaches on void only, counts void as drawn pieces, 24 px arrow over the 15 px island.
  R  ARROW in world blocks: all 6 zooms x 7 sizes = the Python formula (16 blocks x clip / (2 x radius), even, 8-32 px); zooming in grows
     it, out shrinks it (down to 8); the cached document's #SkyyMmArrow anchor = that size, centred; the admin row (32 blocks) doubles it
     and re-lays out; config: a missing / bad mm.arrowBlocks = 16
  Q  square mode + ring (Skyy liked it): square mask fully opaque, square ring band at the edge + gold north tick, the document carries
     the ring at full size and the arrow centred; the round ring still hollow
  O  DEFAULT SPOT at 1080p: built-in layout -> tr 8,40 (unchanged, overlaps nothing); a file without a Minimap line whose own widgets sit
     top-right (Skyy's 18:40 layout) -> moved to a spot touching no shown widget (box + 4 px), right half, on screen; a SAVED Minimap line
     is never moved (even overlapping); a server default with a Minimap entry wins; hidden widgets do not count; 300 random layouts never
     overlap after the move; loading writes nothing
  K  the Server Setup row hud.mm.arrowBlocks (kit: 4-64 taken, 3 / 65 refused), the bound field, the file line, after= re-layout
  L  the saved files: start twice on a scratch COPY of the live Skyy_SkyyHud (read only): nothing written, every saved line loads as
     saved; the 0.3.15 jar reads a 0.3.16 config.properties (mm.arrowBlocks ignored)
  F  class bytes 0.3.15 vs 0.3.16: only the expected classes differ, none added or removed
  Z  the engine-access audit (every reference resolved from its own class: 0 refused)
  X  fix round: a keys-only burst (2704 void pieces) stays hidden, one WITH the island piece attaches (the tap's flag); both arrow
     sets delivered, the 16 x 16 set at <= 16 px; ready in a new world forgets the old one before any packet; ClearWorldMap /
     forget re-draw at once (s.more); the content key = CRC32 + Adler32
Not testable without the game (UNVERIFIED): how the island / arrow look on screen, the client scaling the 32 px arrow picture to 8 px.
Default scratch folder: tools/dev/scratch/hud0316/harness (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, subprocess, zipfile, math, random, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3.16", "0.3.15"
PKG = "com.skyy.hud."
KEY, Z = "SkyyHudMinimap", 5
RADII = [64, 96, 128, 160, 224, 320]
STEPS = [50, 75, 100, 125, 150, 175, 200]
ISLAND = "skyy-island-d8ddde89-98b2-4739-983e-a39773d582b6"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0316", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                  "Saves", "HUD mod", "mods", "Skyy_SkyyHud")))
KEEP = "--keep" in sys.argv
FAILS, OKS, SKIPS = [], [0], []


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


def harness_module(fname, alias):
    spec = importlib.util.spec_from_file_location(alias, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


def arrow_ref(S, r, blocks=16):
    """the Python reference of MmCfg.arrowPx (Java Math.round = floor(x + 0.5))"""
    C = S - 2 * max(3, S // 40)
    b = min(64, max(4, blocks))
    px = b * C / (2.0 * r)
    a = 2 * int(math.floor(px / 2.0 + 0.5))
    return min(32, max(8, a))


def overlaps(a, b, gap=0):
    return a[0] < b[0] + b[2] + gap and b[0] < a[0] + a[2] + gap and a[1] < b[1] + b[3] + gap and b[1] < a[1] + a[3] + gap


# ======================================================================================================== child (either jar)
def run_child(jar, out, mode):
    import jpype
    from jpype import JClass, JArray, JInt, JLong, JByte, JString, JDouble, JFloat
    import skyybuild as B
    hcls = os.path.join(SCRATCH, "hclasses-" + mode)
    shutil.rmtree(hcls, ignore_errors=True)
    os.makedirs(hcls)
    _jvm_start([jar], [B.JAVASSIST, hcls])
    NEW = mode == "new"
    res = {"checks": [], "report": {}, "scen": {}}

    def chk(cond, what):
        res["checks"].append([bool(cond), what])
        if not cond:
            print("  child FAIL:", what)

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
    if fails:
        json.dump(res, open(out, "w"), indent=1)
        return
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

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

    def fake(name, sup, ctor, neighbor, fields=(), methods=()):
        c = CP.makeClass(name, CP.get(sup))
        for fsrc in fields:
            c.addField(CtField.make(fsrc, c))
        c.addConstructor(CtNewConstructor.make(ctor, c))
        for msrc in methods:
            c.addMethod(CtNewMethod.make(msrc, c))
        return c.toClass(neighbor)

    # ---- stand-ins (harness only): the network, the world thread, the store (the 0.3.14 harness's)
    net_ = CP.makeClass("skyyhudharness16.HarnessNet", CP.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    for fsrc in ("public java.util.ArrayList sent;", "public int writes;"):
        net_.addField(CtField.make(fsrc, net_))
    net_.addConstructor(CtNewConstructor.make(
        "public HarnessNet() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }", net_))
    net_.addMethod(CtNewMethod.make(
        "public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}", net_))
    net_.addMethod(CtNewMethod.make(
        "public void write(com.hypixel.hytale.protocol.ToClientPacket[] ps) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.writes++;\n"
        "  for (int i = 0; i < ps.length; i++) this.sent.add(ps[i]);\n}", net_))
    net_.addMethod(CtNewMethod.make("public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }", net_))
    net_.addMethod(CtNewMethod.make("public String getIdentifier() { return \"harness\"; }", net_))
    net_.writeFile(hcls)
    hw = CP.makeClass("skyyhudharness16.HarnessWorld", CP.get("com.hypixel.hytale.server.core.universe.world.World"))
    for fsrc in ("public java.util.ArrayList tasks;", "public int count;"):
        hw.addField(CtField.make(fsrc, hw))
    hw.addConstructor(CtNewConstructor.make(
        "public HarnessWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", hw))
    hw.addMethod(CtNewMethod.make(
        "public void execute(java.lang.Runnable r) {\n  if (this.tasks == null) this.tasks = new java.util.ArrayList();\n  this.tasks.add(r);\n  this.count++;\n}", hw))
    hw.writeFile(hcls)
    NET, HW = JClass("skyyhudharness16.HarnessNet"), JClass("skyyhudharness16.HarnessWorld")
    STOREc, REFc = JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.component.Ref")
    TSC = fake("com.hypixel.hytale.component.SkyyHudTestStore16", "com.hypixel.hytale.component.Store",
               "public SkyyHudTestStore16() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
               "(com.hypixel.hytale.component.IResourceStorage) null); }", STOREc.class_,
               fields=["public java.util.IdentityHashMap comps;"],
               methods=["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                        "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
                        "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
                        "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])

    H = lambda n: JClass(PKG + n)
    MM, MP, MS, MC, WL, Wid, LS, Cfg = (H("Minimap"), H("MmPng"), H("MmSess"), H("MmCfg"), H("WLayout"), H("Widgets"), H("LayoutStore"),
                                         H("HudCfg"))
    UUID, System, CHM = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths = JClass("java.nio.file.Paths")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Transform, Rot3 = JClass("com.hypixel.hytale.math.vector.Transform"), JClass("com.hypixel.hytale.math.vector.Rotation3f")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    MIMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapImage")
    MCHc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapChunk")
    UWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMap")
    CWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.ClearWorldMap")
    MMKc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapMarker")
    PTr, PPos = JClass("com.hypixel.hytale.protocol.Transform"), JClass("com.hypixel.hytale.protocol.Position")
    BFA = JClass("com.hypixel.hytale.server.core.universe.world.chunk.palette.BitFieldArr")
    HMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.hud.HudManager")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    WMMc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager")
    WMSc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapSettings")
    UWMSc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMapSettings")
    IEc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager$ImageEntry")
    L2O = JClass("com.hypixel.fastutil.longs.Long2ObjectConcurrentHashMap")
    CHU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
    WORLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    rnd = random.Random(20261006)

    def s32(v):
        v &= 0xffffffff
        return v - (1 << 32) if v >= (1 << 31) else v

    def tail():
        return [str(x) for x in MM.tail()]

    def engine_image(w, h, pal, idx=None, bits=None):
        ncol = len(pal)
        if bits is None:
            bits = 4 if ncol <= 16 else 8
        if idx is None:
            idx = [rnd.randrange(ncol) for _i in range(w * h)]
        bf = BFA(JInt(bits), JInt(w * h))
        for i, v in enumerate(idx):
            bf.set(JInt(i), JInt(v))
        return MIMc(JInt(w), JInt(h), JArray(JInt)([s32(p) for p in pal]), JByte(bits), bf.get())

    def rand_pal(n):
        return [s32((rnd.randrange(1 << 24) << 8) | 255) for _ in range(n)]

    nxt = [4000]

    def ctype():
        c_ = CTc()
        nxt[0] += 1
        field(CTc, "index").setInt(c_, nxt[0])
        field(CTc, "hashCode").setInt(c_, nxt[0])
        return c_
    saved_static = [(jf(Uni.class_, "instance"), jf(Uni.class_, "instance").get(None)), (jf(EMc.class_, "instance"), jf(EMc.class_, "instance").get(None))]
    CT_PR, CT_PLA = ctype(), ctype()
    uni = U.allocateInstance(Uni.class_)
    field(Uni, "playerRefComponentType").set(uni, CT_PR)
    PBU = CHM()
    field(Uni, "playersByUuid").set(uni, PBU)
    jf(Uni.class_, "instance").set(None, uni)
    em = U.allocateInstance(EMc.class_)
    field(EMc, "playerComponentType").set(em, CT_PLA)
    jf(EMc.class_, "instance").set(None, em)

    def map_manager(enabled):
        m_ = U.allocateInstance(WMMc.class_)
        imgs = L2O()
        field(WMMc, "images").set(m_, imgs)
        sp = UWMSc()
        sp.enabled = enabled
        field(WMMc, "worldMapSettings").set(m_, WMSc(None, JFloat(0.5), JFloat(1.0), JInt(1), JInt(64), sp))
        return m_, imgs

    def put_engine(imgs, cx, cz, im):
        if int(CHU.indexChunk(JInt(cx), JInt(cz))) != -1:
            imgs.put(JLong(int(CHU.indexChunk(JInt(cx), JInt(cz)))), IEc(im))

    WUUIDS = {}

    def make_world(name, mm):
        w = U.allocateInstance(HW.class_)
        jf(WORLDc.class_, "worldMapManager").set(w, mm)
        jf(WORLDc.class_, "name").set(w, name)
        WUUIDS[name] = WUUIDS.get(name) or UUID.randomUUID()
        return w

    def run_world(w):
        n = 0
        while w.tasks is not None and int(w.tasks.size()) > 0:
            t_ = w.tasks.get(0)
            w.tasks.subList(0, 1).clear()
            t_.run()
            n += 1
        return n

    def move_to(o, world, x, z, yaw=0.0):
        pr = o["pr"]
        field(PRc, "transform").set(pr, Transform(JDouble(x), JDouble(129.0), JDouble(z)))
        field(PRc, "headRotation").set(pr, Rot3(JFloat(0.0), JFloat(yaw), JFloat(0.0)))
        field(PRc, "worldUuid").set(pr, WUUIDS[str(world.getName())])
        if world is not o.get("w"):
            o["w"] = world
            es = U.allocateInstance(ESc.class_)
            field(ESc, "world").set(es, world)
            st = U.allocateInstance(TSC)
            ref = o["ref"]
            field(REFc, "store").set(ref, st)
            comps = JClass("java.util.IdentityHashMap")()
            comps.put(CT_PR, pr)
            comps.put(CT_PLA, o["pl"])
            allc = JClass("java.util.IdentityHashMap")()
            allc.put(ref, comps)
            st.comps = allc
            field(STOREc, "externalData").set(st, es)
            o["st"] = st

    def player(n, name, world, x, z):
        pr = U.allocateInstance(PRc.class_)
        field(PRc, "uuid").set(pr, UUID(0x5ce16, n))
        field(PRc, "username").set(pr, name)
        net = U.allocateInstance(NET.class_)
        field(PRc, "packetHandler").set(pr, net)
        ref = U.allocateInstance(REFc.class_)
        pl = U.allocateInstance(PLAc.class_)
        hm = HMc()
        field(PLAc, "hudManager").set(pl, hm)
        field(PRc, "entity").set(pr, ref)
        PBU.put(pr.getUuid(), pr)
        o = {"pr": pr, "net": net, "ref": ref, "pl": pl, "hm": hm}
        move_to(o, world, x, z)
        return o

    def sent(o, i0=0):
        n_ = o["net"]
        return [] if n_.sent is None else [n_.sent.get(i) for i in range(i0, int(n_.sent.size()))]

    def mark(o):
        return 0 if o["net"].sent is None else int(o["net"].sent.size())

    def assets_in(ps):
        return [str(p_.asset.name) for p_ in ps if str(p_.getClass().getSimpleName()) == "AssetInitialize"]

    def upd(chunks, added=()):
        arr = JArray(MCHc)(len(chunks))
        for i, c in enumerate(chunks):
            arr[i] = MCHc(JInt(c[0]), JInt(c[1]), c[2])
        am = None
        if added:
            am = JArray(MMKc)(len(added))
            for i, (mid, img, x, z) in enumerate(added):
                am[i] = MMKc(mid, None, img, PTr(PPos(JDouble(x), JDouble(64.0), JDouble(z)), None), None, None)
        return UWMc(arr, am, None)

    STPE = JClass("java.util.concurrent.ScheduledThreadPoolExecutor")
    parked = STPE(1)

    def reset_mm():
        MM.shutdown0()
        MM.REQ.clear()
        MM.CACHE.clear()
        MM.GEN.clear()
        MM.DOCS.clear()
        MM.NOSTREAM.clear()
        MM.TAIL.clear()
        MM.RELAYOUT = False
        MM.EXEC = parked
        MC.BM = 1

    work = os.path.join(SCRATCH, "child-" + mode)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)

    def use_dir(name):
        d = os.path.join(work, name)
        os.makedirs(d, exist_ok=True)
        LS.DIR = Paths.get(os.path.join(d, "layouts"))
        LS.CACHE.clear()
        return d

    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()
    System.getProperties().put("skyy.bridge", CHM())

    def tick_until_filled(sess, o, worlds, n=40):
        for _ in range(n):
            sess.nextPanAt = 0
            MM.tick()
            for w_ in worlds:
                run_world(w_)
            if sess.hud is not None and bool(sess.hud.attached) and bool(sess.fillLogged):
                return True
        return False

    def slot_of(sess, cx, cz):
        return int(MM.slot(JInt(cx), JInt(cz), JInt(int(sess.w))))

    VOID = s32(0x00000000)
    GRASS, SAND, STONE = s32(0x4f8a2eff), s32(0xd8c47aff), s32(0x8a8a8aff)

    def void_piece():
        return engine_image(32, 32, [VOID], idx=[0] * (32 * 32), bits=1)

    def island_piece():
        # the island: ~20 blocks of grass / sand / stone in a void chunk (the rest transparent), like SkyWynn_Z1_Small at spawn 8.5
        idx = []
        for z in range(32):
            for x in range(32):
                d = math.hypot(x - 9.5, z - 9.5)
                idx.append(1 if d < 6 else (2 if d < 9 else (3 if d < 10.5 else 0)))
        return engine_image(32, 32, [VOID, GRASS, SAND, STONE], idx=idx)

    # ================================================================================== I: the two-world repro (hub -> Void island)
    def two_world(tag, race=False, clear=True):
        reset_mm()
        use_dir("i-" + tag)
        mmH, imgsH = map_manager(True)
        WH = make_world("default", mmH)
        p = player(1 + len(res["scen"]), "SkyLordPlayz", WH, -270.5, 80.85)
        MM.hello(p["pr"])
        hub = {}
        for cx in range(-20, 3):
            for cz in range(-6, 11):
                hub[(cx, cz)] = engine_image(32, 32, rand_pal(rnd.randrange(3, 14)))
                put_engine(imgsH, cx, cz, hub[(cx, cz)])
        MM.tap(p["pr"], CWMc())
        MM.tap(p["pr"], upd([(cx, cz, im) for (cx, cz), im in hub.items()],
                            added=[("hub-warp", "Warp.png", -250.0, 90.0), ("hub-spawn", "Spawn.png", -280.0, 70.0)]))
        MM.ready(p["pr"], p["st"])
        s = MM.SESS.get(p["pr"].getUuid())
        ok = tick_until_filled(s, p, [WH])
        w = int(s.w)
        hub_paths = set(str(x) for x in s.slotPath if x is not None and str(x) != str(s.dark))
        sc = {"hub_filled": ok, "hub_real": len(hub_paths), "w": w, "hub_markers": int(s.markers.size())}
        # the engine's world change: HudManager.resetHud (onRemove) -> World.onFinishPlayerJoining -> WorldMapTracker.clear
        # (ClearWorldMap) -> the island's map burst -> PlayerReady (SkyyHud's AttachTask -> Minimap.ready)
        p["hm"].resetHud(p["pr"])
        mmI, imgsI = map_manager(True)
        WI = make_world(ISLAND, mmI)
        move_to(p, WI, 8.5, 8.5)
        isl = island_piece()
        burst = []
        for cx in range(-9, 10):
            for cz in range(-9, 10):
                im = isl if (cx, cz) == (0, 0) else void_piece()
                burst.append((cx, cz, im))
                put_engine(imgsI, cx, cz, im)
        i0 = mark(p)
        if clear:
            MM.tap(p["pr"], CWMc())
        MM.tap(p["pr"], upd(burst))
        if race:
            MM.tick()              # the burst drained BEFORE the ready request (the other order)
        MM.ready(p["pr"], p["st"])
        MM.TAIL.clear()
        ok2 = tick_until_filled(s, p, [WH, WI])
        paths = [None if x is None else str(x) for x in s.slotPath]
        dark = str(s.dark)
        isl_png = MP.tilePng(isl, JInt(int(s.det)))
        isl_name = str(MM.asset(JString(""), isl_png).getName())
        void_name = str(MM.asset(JString(""), MP.tilePng(void_piece(), JInt(int(s.det)))).getName())
        sl0 = slot_of(s, 0, 0)
        others = [paths[i] for i in range(len(paths)) if i != sl0]
        sent_isl = assets_in(sent(p, i0))
        fill = [l_ for l_ in tail() if l_.startswith("minimap: first fill")]
        # the grid maths: where the player's point sits in the grid vs the island tile's anchor
        t = int(s.t)
        tile_x, tile_z = int(MM.tilePos(JInt(0), JInt(int(s.bx)), JInt(t))), int(MM.tilePos(JInt(0), JInt(int(s.bz)), JInt(t)))
        C = int(s.C)
        px_in_grid, pz_in_grid = C / 2.0 - int(s.gl), C / 2.0 - int(s.gt)
        sc.update({"island_filled": ok2, "attached": s.hud is not None and bool(s.hud.attached),
                   "hud_on_client": p["hm"].getCustomHud(KEY) is not None,
                   "slot00": paths[sl0], "island_name": isl_name, "void_name": void_name, "dark": dark,
                   "others_dark": all(x == dark for x in others), "hub_leak": sorted(set(paths) & hub_paths)[:3],
                   "sent": sent_isl, "fill": fill, "t": t, "ap": int(s.ap), "S": int(s.S),
                   "island_under_player": tile_x <= px_in_grid < tile_x + t and tile_z <= pz_in_grid < tile_z + t,
                   "markers_after": int(s.markers.size()), "known_hub": sum(1 for k_ in s.known.keySet() if int(MM.keyX(JLong(int(k_)))) < -10),
                   "voids": int(s.voids) if NEW else None, "tail": tail()[:6]})
        res["scen"]["two_world_" + tag] = sc
        return sc

    a = two_world("A")
    if NEW:
        chk(a["hub_filled"] and a["hub_real"] == a["w"] * a["w"] and a["hub_markers"] == 2,
            "I. hub: the 13 x 13 window filled with its own distinct pieces (%d real) + 2 markers" % a["hub_real"])
        chk(a["island_filled"] and a["attached"] and a["hud_on_client"], "I. island (ClearWorldMap -> burst -> ready): the minimap attaches (the island piece is real)")
        chk(not a["hub_leak"], "I. NO hub picture in any island slot (no cross-world reuse): %s" % a["hub_leak"])
        chk(a["slot00"] == a["island_name"], "I. chunk (0,0) shows the island's OWN picture %s (got %s)" % (a["island_name"], a["slot00"]))
        chk(a["others_dark"], "I. every void slot keeps the backdrop (no picture for an all-transparent piece)")
        chk(a["sent"] == [a["island_name"]], "I. on the island ONLY the island picture is sent (no void picture): %s" % a["sent"])
        chk(a["island_under_player"], "I. grid maths: the island tile (0,0) lies under the player's point at the clip centre")
        chk(a["ap"] < a["t"], "I. the arrow (%d px) is smaller than the island's piece (%d px) - it no longer hides it" % (a["ap"], a["t"]))
        chk(len(a["fill"]) == 1 and " 1 of 169 pieces " in a["fill"][0] and " 168 empty)" in a["fill"][0],
            "I. the island fill line: 1 of 169 drawn, 168 empty: %s" % a["fill"])
        chk(a["markers_after"] == 0 and a["known_hub"] == 0, "I. the hub's markers and pieces are gone after the ClearWorldMap")
        b = two_world("B", race=True)
        chk(b["attached"] and not b["hub_leak"] and b["slot00"] == b["island_name"] and b["others_dark"] and b["sent"] == [b["island_name"]],
            "I. the race (burst drained a tick before ready): the same island result")
        c = two_world("C", clear=False)
        chk(c["attached"] and not c["hub_leak"] and c["slot00"] == c["island_name"] and c["others_dark"] and c["markers_after"] == 0
            and c["known_hub"] == 0,
            "I. defensive: a world change WITHOUT ClearWorldMap: the tap's world-boundary marker forgets the hub, the island is drawn")
    else:
        res["scen"]["old_bug"] = {"ap": a["ap"], "t": a["t"], "fill": a["fill"], "sent": a["sent"], "slot00_is_island": a["slot00"] == a["island_name"]}
        chk(a["ap"] > a["t"], "I-old. 0.3.15: the arrow (%d px) is BIGGER than the island's piece (%d px) - it hides the island" % (a["ap"], a["t"]))
        chk(len(a["fill"]) == 1 and " 169 of 169 pieces " in a["fill"][0] and a["void_name"] in a["sent"],
            "I-old. 0.3.15: the void pieces count as drawn ('169 of 169') and the transparent void picture is sent: %s" % a["fill"])

    # ---- a world with ONLY void pieces (an island before its ground is on the map)
    reset_mm()
    use_dir("void")
    mmV, imgsV = map_manager(True)
    WV = make_world("skyy-island-void", mmV)
    pv = player(90, "Nia", WV, 8.5, 8.5)
    MM.hello(pv["pr"])
    MM.tap(pv["pr"], CWMc())
    MM.tap(pv["pr"], upd([(cx, cz, void_piece()) for cx in range(-7, 8) for cz in range(-7, 8)]))
    MM.ready(pv["pr"], pv["st"])
    for _ in range(4):
        MM.tick()
        run_world(WV)
    sv = MM.SESS.get(pv["pr"].getUuid())
    att_void = pv["hm"].getCustomHud(KEY) is not None
    if NEW:
        chk(not att_void and sv.hud is None and bool(sv.pending), "I. a world with ONLY void pieces: no attach - nothing drawn (spec: hide until real tiles)")
        sv.pendingSince = int(System.currentTimeMillis()) - 16000
        MM.TAIL.clear()
        MM.tick()
        MM.tick()
        chk(tail() == ["minimap: only empty (void) map pieces in world 'skyy-island-void' so far - not shown there (it shows once real ground is on the map)"],
            "I. ... after 15 s ONE log line: %s" % tail())
        MM.tap(pv["pr"], upd([(0, 0, island_piece())]))
        ok = tick_until_filled(sv, pv, [WV])
        chk(ok and pv["hm"].getCustomHud(KEY) is not None and str(sv.slotPath[slot_of(sv, 0, 0)]) != str(sv.dark),
            "I. ... the island piece arrives: the minimap attaches and draws it")
    else:
        chk(att_void, "I-old. 0.3.15 attaches in a world with ONLY void pieces (the empty disc)")
        res["scen"]["old_void_attached"] = att_void

    if NEW:
        # ============================================================================== X: the fix round (critic findings)
        import zlib
        reset_mm()
        use_dir("x")
        mmX, imgsX = map_manager(True)
        WX = make_world("skyy-island-big", mmX)
        px_ = player(95, "Big", WX, 8.5, 8.5)
        MM.hello(px_["pr"])
        vp = void_piece()
        isl_x = island_piece()
        big = [(cx, cz, vp) for cx in range(-26, 26) for cz in range(-26, 26)]          # 2704 pieces > the 2048 image bound
        for cx, cz, im in big:
            put_engine(imgsX, cx, cz, im)
        i0x = mark(px_)
        MM.tap(px_["pr"], CWMc())
        MM.tap(px_["pr"], upd(big))
        MM.ready(px_["pr"], px_["st"])
        for _ in range(4):
            MM.tick()
            run_world(WX)
        sx = MM.SESS.get(px_["pr"].getUuid())
        chk(int(sx.keysOnly.get()) >= 1 and sx.hud is None and px_["hm"].getCustomHud(KEY) is None and bool(sx.pending)
            and not bool(sx.realSeen),
            "X1. a keys-only burst (2704 void pieces, past the image bound) does NOT count as real: hidden (keysOnly %d)" % int(sx.keysOnly.get()))
        put_engine(imgsX, 0, 0, isl_x)
        big2 = [(cx, cz, (isl_x if (cx, cz) == (0, 0) else vp)) for cx in range(-26, 26) for cz in range(-26, 26)]
        MM.tap(px_["pr"], upd(big2))
        okx = tick_until_filled(sx, px_, [WX])
        chk(okx and int(sx.keysOnly.get()) >= 2 and px_["hm"].getCustomHud(KEY) is not None
            and str(sx.slotPath[slot_of(sx, 0, 0)]) != str(sx.dark),
            "X1. ... a keys-only burst WITH the island piece: real (the tap's flag), attaches, chunk 0,0 drawn from the engine cache")
        an = set(assets_in(sent(px_, i0x)))
        small = [str(MM.gen(JString("arrowS:%d" % k)).getName()) for k in range(16)]
        large = [str(MM.gen(JString("arrow:%d" % k)).getName()) for k in range(16)]
        chk(all(n_ in an for n_ in small + large) and len(set(small) | set(large)) == 32,
            "X4. statics: both arrow sets (16 x 32 px + 16 x 16 px, 32 distinct pictures) go in the first delivery")
        chk(int(sx.ap) <= 16 and [str(x) for x in sx.arrows] == small,
            "X4. an arrow of %d px uses the 16 x 16 set" % int(sx.ap))
        sp_ = [int(v) & 0xffffffff for v in MP.arrowSm(JInt(0))]
        lp_ = [int(v) & 0xffffffff for v in MP.arrow(JInt(0))]
        fillc = lp_[16 * 32 + 16]
        outc = set(v for v in lp_ if v != 0 and v != fillc)
        chk(len(sp_) == 256 and sp_[8 * 16 + 8] == fillc and any(v in outc for v in sp_) and sp_[0] == 0,
            "X4. the 16 x 16 arrow: filled centre, its own outline colour, clear corners")
        # X3: ready in a new world with nothing of it queued yet - the old world is forgotten there
        mmY, imgsY = map_manager(True)
        WY = make_world("skyy-island-other", mmY)
        before = int(sx.known.size()) + int(sx.streamed.size())
        move_to(px_, WY, 8.5, 8.5)
        MM.ready(px_["pr"], px_["st"])
        MM.tick()                  # the minimap thread handles the ready request (nothing of the new world queued)
        chk(before > 0 and int(sx.known.size()) == 0 and int(sx.streamed.size()) == 0 and not bool(sx.realSeen)
            and str(sx.drainW) == str(WUUIDS["skyy-island-other"]),
            "X3. ready in a new world before any of its packets: the old world's pieces are forgotten (%d before)" % before)
        isl_y = island_piece()
        put_engine(imgsY, 0, 0, isl_y)
        MM.tap(px_["pr"], CWMc())
        MM.tap(px_["pr"], upd([(0, 0, isl_y), (1, 0, vp), (0, 1, vp)]))
        oky = tick_until_filled(sx, px_, [WX, WY])
        chk(oky and str(sx.slotPath[slot_of(sx, 0, 0)]) != str(sx.dark), "X3. ... then the new world's own piece is drawn")
        # X2: a ClearWorldMap while attached re-draws at once (s.more), no stale piece stays painted
        sx.more = False
        MM.tap(px_["pr"], CWMc())
        MM.drain(sx)
        more_after = bool(sx.more)
        sx.attachAt = int(System.currentTimeMillis())
        sx.nextPanAt = 0
        MM.tick()
        run_world(WY)
        left = [str(x) for x in sx.slotPath if x is not None and str(x) != str(sx.dark)]
        chk(more_after and not left, "X2. ClearWorldMap while attached: s.more set and every slot back to the backdrop (left: %s)" % left[:2])
        sx.more = False
        MM.forget(sx)
        chk(bool(sx.more), "X2. forget() sets s.more")
        # X5: the content key = CRC32 + Adler32 over palette (big-endian) + packed bytes
        pal = [int(v) & 0xffffffff for v in isl_x.palette]
        pb = b"".join(v.to_bytes(4, "big") for v in pal) + bytes((int(b_) & 255) for b_ in isl_x.packedIndices)
        want_k = "%dx%db%dp%dn%dc%xa%x/3" % (int(isl_x.width), int(isl_x.height), int(isl_x.bitsPerIndex) & 255, len(pal),
                                            len(isl_x.packedIndices), zlib.crc32(pb), zlib.adler32(pb))
        got_k = str(MM.contentKey(isl_x, JInt(3)))
        chk(got_k == want_k, "X5. content key carries CRC32 + Adler32: %s (want %s)" % (got_k, want_k))

    if not NEW:
        # L: the 0.3.15 jar reads a 0.3.16 config.properties (mm.arrowBlocks unknown to it)
        f_ = os.path.join(cfgdir, "config16.properties")
        open(f_, "w", encoding="latin-1").write("defaultLayout=\nmm.maxRadius=320\nmm.arrowBlocks=40\n")
        Cfg.FILE = Paths.get(f_)
        Cfg.load()
        chk(str(MC.MAX_RADIUS) == "320", "L. ROLLBACK: the 0.3.15 jar reads a 0.3.16 config.properties (mm.arrowBlocks ignored)")
        for f_, v_ in saved_static:
            f_.set(None, v_)
        json.dump(res, open(out, "w"), indent=1)
        return

    # ================================================================================== R: the arrow in world blocks
    reset_mm()
    use_dir("r")
    rp = player(200, "Arrow", WV, 8.5, 8.5)
    defm = Wid.class_.getDeclaredMethod("def", JClass("java.lang.String").class_)
    bad, sizes = [], {}
    for r_ in RADII:
        for st_ in STEPS:
            l = defm.invoke(None, JString("Minimap"))
            l.scale = st_
            l.mm = MC.enc(JArray(JInt)([r_, 0, 500, 1, 1]), JString("def"))
            g = MS(rp["pr"])
            MC.MAX_RADIUS = "320"
            MM.geometry(g, l)
            want = arrow_ref(int(g.S), r_)
            sizes["%d/%d" % (r_, st_)] = int(g.ap)
            if int(g.ap) != want:
                bad.append((r_, st_, int(g.ap), want))
    chk(not bad, "R. arrow px = 16 blocks x clip / (2 x radius), even, 8-32 px, for all 6 zooms x 7 sizes: %s" % bad[:4])
    chk(sizes["160/100"] == 8 and sizes["64/100"] == 20 and sizes["96/100"] == 12 and sizes["128/100"] == 10 and sizes["320/100"] == 8
        and sizes["128/200"] == 20, "R. at 100 %%: zoom 64 = 20, 96 = 12, 128 = 10, 160 = 8 (was 24), 320 = 8; Skyy's 200 %% zoom 128 = 20 (was 48): %s"
        % dict((k_, v_) for k_, v_ in sizes.items() if k_.endswith("/100") or k_ == "128/200"))
    mono = all(sizes["%d/%d" % (RADII[i], st_)] >= sizes["%d/%d" % (RADII[i + 1], st_)] for st_ in STEPS for i in range(len(RADII) - 1))
    chk(mono, "R. zooming out never grows the arrow, zooming in never shrinks it (every size)")
    res["report"]["arrow_px"] = sizes
    # the document carries it, centred
    ATTR = None
    for r_, st_ in ((160, 100), (64, 200), (320, 50)):
        l = defm.invoke(None, JString("Minimap"))
        l.scale = st_
        l.mm = MC.enc(JArray(JInt)([r_, 1, 500, 1, 1]), JString("def"))
        g = MS(rp["pr"])
        MM.geometry(g, l)
        MM.pictures(g)
        d_ = MM.doc(g, JString("(Top: 40, Right: 8, Width: %d, Height: %d)" % (int(g.S), int(g.S))))
        txt = [str(c.text) for c in d_.getCommands() if c.text is not None and "#SkyyMmArrow" in str(c.text)]
        S_, ap_ = int(g.S), int(g.ap)
        want = "Anchor: (Left: %d, Top: %d, Width: %d, Height: %d)" % ((S_ - ap_) // 2, (S_ - ap_) // 2, ap_, ap_)
        chk(len(txt) == 1 and want in txt[0], "R. zoom %d size %d: the document's arrow = %s (%s)" % (r_, st_, want, txt[:1]))
    # the admin row's field + re-layout
    MC.ARROW_BLOCKS = 32
    l = defm.invoke(None, JString("Minimap"))
    g = MS(rp["pr"])
    MM.geometry(g, l)
    chk(int(g.ap) == arrow_ref(160, 160, 32) == 16, "R. Server Setup 'Your arrow's width' 32 blocks: 16 px at zoom 160 (twice the default)")
    MC.ARROW_BLOCKS = 16
    for txt_, want in (("defaultLayout=\n", 16), ("defaultLayout=\nmm.arrowBlocks=40\n", 40), ("defaultLayout=\nmm.arrowBlocks=999\n", 16),
                       ("defaultLayout=\nmm.arrowBlocks=x\n", 16), ("defaultLayout=\nmm.arrowBlocks=3\n", 16)):
        f_ = os.path.join(cfgdir, "arrow.properties")
        open(f_, "w", encoding="latin-1").write(txt_)
        before = open(f_, "rb").read()
        Cfg.FILE = Paths.get(f_)
        Cfg.load()
        chk(int(MC.ARROW_BLOCKS) == want and open(f_, "rb").read() == before, "R. config %r -> arrowBlocks %d, the file untouched" % (txt_.strip(), want))
    MC.ARROW_BLOCKS = 16

    # ================================================================================== Q: square mode + ring
    for shape in (1, 0):
        l = defm.invoke(None, JString("Minimap"))
        l.scale = 125
        l.mm = MC.enc(JArray(JInt)([128, shape, 250, 1, 0]), JString("def"))
        l.col = "gold"
        g = MS(rp["pr"])
        MM.geometry(g, l)
        MM.pictures(g)
        d_ = MM.doc(g, JString("(Top: 5, Right: 163, Width: %d, Height: %d)" % (int(g.S), int(g.S))))
        texts = [str(c.text) for c in d_.getCommands() if c.text is not None]
        ring = [t_ for t_ in texts if "#SkyyMmRing" in t_]
        S_, rw = int(g.S), int(g.rw)
        mk = [int(v) & 0xffffffff for v in MP.mask(JInt(int(g.C)), JInt(shape))]
        rc = int(MP.rgbaOf(Wid.hexOf(JString("gold"))))
        px = [int(v) & 0xffffffff for v in MP.ring(JInt(S_), JInt(rw), JInt(shape), JInt(rc))]
        corner_band = px[(rw // 2) * S_ + (rw // 2)] != 0
        centre_clear = px[(S_ // 2) * S_ + S_ // 2] == 0
        nm = "square" if shape else "round"
        chk(len(ring) == 1 and ("Width: %d, Height: %d" % (S_, S_)) in ring[0] and "#SkyyMmArrow" in " ".join(texts),
            "Q. %s + ring: the document carries the ring at %d px and the arrow" % (nm, S_))
        if shape == 1:
            chk(all(v == 0xffffffff for v in mk) and corner_band and centre_clear,
                "Q. square: the mask is fully opaque, the ring band reaches the corners, the centre is clear")
        else:
            chk(mk[0] == 0 and mk[(int(g.C) // 2) * int(g.C) + int(g.C) // 2] == 0xffffffff and centre_clear and not corner_band,
                "Q. round: the mask clips the corners, the ring is hollow, no band in the corner")
        top_mid = px[(rw // 2) * S_ + S_ // 2]
        chk(top_mid != 0 and top_mid != (rc & 0xffffffff), "Q. %s: the north tick (not the ring colour) at the top centre" % nm)

    # ================================================================================== O: the default spot at 1080p
    def boxes_of(m, skip_mm=True):
        out = []
        for wid_ in [str(x) for x in Wid.IDS]:
            if skip_mm and wid_ == "Minimap":
                continue
            o = m.get(wid_)
            if o is None or not bool(o.en):
                continue
            ow = int(o.bw) * int(o.scale) // 100
            oh = int(Wid.hMax(o))
            p_ = Wid.screenPosWH(o, JInt(ow), JInt(oh))
            out.append((wid_, (int(p_[0]), int(p_[1]), ow, oh)))
        return out

    def mm_box(m):
        o = m.get("Minimap")
        S_ = int(o.bw) * int(o.scale) // 100
        p_ = Wid.screenPosWH(o, JInt(S_), JInt(S_))
        return (int(p_[0]), int(p_[1]), S_, S_)

    def layout_dir(name, lines, uid):
        d = use_dir(name)
        ld = os.path.join(d, "layouts")
        os.makedirs(ld, exist_ok=True)
        u = UUID(0x5ce160, uid)
        if lines is not None:
            open(os.path.join(ld, str(u) + ".properties"), "w", encoding="latin-1").write("#SkyyHud layout\n" + "\n".join(lines) + "\n")
        return ld, u

    def tree(d):
        o = {}
        for dp, dn, fn in os.walk(d):
            for f in fn:
                p_ = os.path.join(dp, f)
                o[os.path.relpath(p_, d)] = open(p_, "rb").read()
        return o

    ld, u = layout_dir("o1", None, 1)
    m = LS.get(u)
    mm1 = str(m.get("Minimap").ser())
    hits = [w_ for w_, b_ in boxes_of(m) if overlaps(mm_box(m), b_)]
    chk(mm1 == "1,tr,8,40,100,1" and not hits, "O. built-in layout (new player): the minimap stays at tr 8,40 and overlaps nothing: %s %s" % (mm1, hits))
    chk(not os.path.isdir(ld) or not os.listdir(ld), "O. ... loading wrote nothing")
    skyy_1840 = ["Coins=1,br,8,633,200,0,gold,1,0,0,def", "Combat=1,bl,183,8,180,0,aqua,1,0,1,black,0", "Coords=1,tl,0,5,170,0,aqua,1,0,1,blue",
                 "Day=1,tr,0,120,150,0,lime,1,0,0,def", "Gclock=1,bl,0,5,170,0", "Guild=1,tl,8,274,170,0,gold,1,0,0,def",
                 "Online=1,tr,0,45,150,0,lime,1,0,0,def", "Party=1,br,418,0,160,0,gold,1,0,0,def", "Rclock=0,br,0,439,160,0",
                 "Session=1,br,0,0,160,0,red,1,0,0,def", "Skills=1,r,8,65,150,0,purple,1,0,1,black,1,1023", "Zone=1,tr,0,0,170,0,blue,1,0,0,def"]
    ld, u = layout_dir("o2", skyy_1840, 2)
    t0 = tree(ld)
    m = LS.get(u)
    before_hits = []
    dflt = defm.invoke(None, JString("Minimap"))
    S0 = 160
    dbox = (1920 - S0 - 8, 40, S0, S0)
    before_hits = [w_ for w_, b_ in boxes_of(m) if overlaps(dbox, b_)]
    mb = mm_box(m)
    hits = [w_ for w_, b_ in boxes_of(m) if overlaps(mb, b_, 4)]
    chk(sorted(before_hits) == ["Day", "Online", "Zone"], "O. Skyy's 18:40 layout: the old default tr 8,40 covered %s" % before_hits)
    chk(not hits and mb[0] >= 960 and mb[0] + mb[2] <= 1920 and mb[1] >= 8 and mb[1] + mb[3] <= 1072,
        "O. ... the never-placed minimap moved to %s (box %s): touches no shown widget (+4 px), right half, on screen: %s"
        % (str(m.get("Minimap").ser()), mb, hits))
    chk(tree(ld) == t0, "O. ... loading wrote nothing (the spot is saved only when the player saves their HUD)")
    res["report"]["skyy_1840_spot"] = str(m.get("Minimap").ser())
    ld, u = layout_dir("o3", skyy_1840 + ["Minimap=1,tr,8,40,100,1"], 3)
    m = LS.get(u)
    chk(str(m.get("Minimap").ser()) == "1,tr,8,40,100,1", "O. a SAVED Minimap line is never moved (even overlapping): %s" % str(m.get("Minimap").ser()))
    ld, u = layout_dir("o4", skyy_1840 + ["Minimap=1,tr,163,5,200,1,gold,1,0,0,def,1,-,def,z128.sq.u250.g1.k0.cblue"], 4)
    m = LS.get(u)
    chk(str(m.get("Minimap").ser()) == "1,tr,163,5,200,1,gold,1,0,0,def,1,-,def,z128.sq.u250.g1.k0.cblue", "O. Skyy's saved square minimap loads exactly as saved")
    hidden = [ln.replace("=1,", "=0,", 1) if ln.split("=")[0] in ("Zone", "Online", "Day") else ln for ln in skyy_1840]
    ld, u = layout_dir("o5", hidden, 5)
    m = LS.get(u)
    chk(str(m.get("Minimap").ser()) == "1,tr,8,40,100,1", "O. hidden widgets do not count: with Zone / Online / Day off it stays at tr 8,40")
    # the server default places the minimap -> it wins
    f_ = os.path.join(cfgdir, "def.properties")
    open(f_, "w", encoding="latin-1").write("defaultLayout=Minimap=1:tl:300:300:100:1\n")
    Cfg.FILE = Paths.get(f_)
    Cfg.load()
    ld, u = layout_dir("o6", skyy_1840, 6)
    m = LS.get(u)
    chk(str(m.get("Minimap").ser()) == "1,tl,300,300,100,1", "O. a server default with a Minimap entry wins: %s" % str(m.get("Minimap").ser()))
    open(f_, "w", encoding="latin-1").write("defaultLayout=Zone=1:tr:8:60:150:1\n")
    Cfg.load()
    ld, u = layout_dir("o7", None, 7)
    m = LS.get(u)
    mb = mm_box(m)
    chk(not [w_ for w_, b_ in boxes_of(m) if overlaps(mb, b_, 4)] and str(m.get("Minimap").ser()) != "1,tr,8,40,100,1",
        "O. a server default that puts Zone under the old spot (no Minimap entry): a new player's minimap moves off it: %s" % str(m.get("Minimap").ser()))
    open(f_, "w", encoding="latin-1").write("defaultLayout=\n")
    Cfg.load()
    # random layouts
    anchors = ["tl", "t", "tr", "l", "c", "r", "bl", "b", "br"]
    ids = [str(x) for x in Wid.IDS if str(x) not in ("Minimap",)]
    bad_r, moved, stayed = [], 0, 0
    for k in range(300):
        lines = []
        for wid_ in ids:
            if rnd.random() < 0.35:
                continue
            lines.append("%s=%d,%s,%d,%d,%d,1" % (wid_, 1 if rnd.random() < 0.8 else 0, rnd.choice(["tr", "tr", "r", "t"] + anchors),
                                                   rnd.randrange(0, 400), rnd.randrange(0, 500), rnd.choice([50, 100, 150, 200])))
        ld, u = layout_dir("rnd", lines, 1000 + k)
        m = LS.get(u)
        mb = mm_box(m)
        hit = [w_ for w_, b_ in boxes_of(m) if overlaps(mb, b_, 4)]
        if str(m.get("Minimap").ser()) == "1,tr,8,40,100,1":
            stayed += 1
            dhit = [w_ for w_, b_ in boxes_of(m) if overlaps(mb, b_, 4)]
            if dhit:
                # stayed while overlapping = no free spot at all: prove it by brute force on the same candidate grid
                free = False
                for dx in range(8, 961 - 160, 8):
                    for dy in range(8, 1080 - 8 - 160 + 1, 8):
                        bx_ = (1920 - 160 - dx, dy, 160, 160)
                        if not any(overlaps(bx_, b_, 4) for w_, b_ in boxes_of(m)):
                            free = True
                            break
                    if free:
                        break
                if free:
                    bad_r.append(("stayed but a spot was free", lines))
        else:
            moved += 1
            if hit or mb[0] < 960 or mb[1] < 8 or mb[1] + mb[3] > 1072:
                bad_r.append((str(m.get("Minimap").ser()), hit, lines))
    chk(not bad_r, "O. 300 random layouts: a moved minimap never touches a shown widget and stays in the right half on screen (%d moved, %d kept): %s"
        % (moved, stayed, bad_r[:1]))
    res["report"]["random_moved"] = moved

    # ================================================================================== K: the Server Setup row
    kdir = os.path.join(work, "k")
    kmods = os.path.join(kdir, "mods")
    os.makedirs(os.path.join(kmods, "Skyy_SkyyHud"))
    f_ = os.path.join(kmods, "Skyy_SkyyHud", "config.properties")
    open(f_, "w", encoding="latin-1").write("# a 0.3.15 file\ndefaultLayout=\nmm.maxRadius=224\n")
    Cfg.FILE = Paths.get(f_)
    Cfg.load()
    Pub = JClass(PKG + "CfgPub")
    Pub.start(Paths.get(kmods), None)
    Fn = JClass(PKG + "CfgFn")
    rows = [str(r_[0]) for r_ in JClass(PKG + "CfgRows").rows()] if hasattr(JClass(PKG + "CfgRows"), "rows") else []
    chk(not rows or "hud.mm.arrowBlocks" in rows, "K. the row hud.mm.arrowBlocks is published (%d rows)" % len(rows))
    MM.RELAYOUT = False
    for key_, val_, ok_ in (("hud.mm.arrowBlocks", "3", False), ("hud.mm.arrowBlocks", "65", False), ("hud.mm.arrowBlocks", "4", True),
                            ("hud.mm.arrowBlocks", "64", True), ("hud.mm.arrowBlocks", "24", True)):
        try:
            r_ = Fn.set(key_, val_, None, "Console", "yes", "console")
            got = str(r_[0]) if r_ is not None else None
        except Exception as ex:
            got = "threw %s" % ex
        chk((got == "ok") == ok_, "K. the kit %s %s = %s (%s)" % ("takes" if ok_ else "refuses", key_, val_, got))
    chk(int(MC.ARROW_BLOCKS) == 24 and bool(MM.RELAYOUT), "K. the kit wrote ARROW_BLOCKS = 24 and asked every minimap to re-lay out")
    Pub.flush()
    ktext = open(f_, encoding="latin-1").read()
    chk("mm.arrowBlocks=24" in ktext and "mm.maxRadius=224" in ktext, "K. config.properties got mm.arrowBlocks=24, old lines kept")
    MC.ARROW_BLOCKS = 16

    # ================================================================================== L: start twice on a scratch COPY of the live data
    if os.path.isdir(LIVE):
        mods = os.path.join(work, "live")
        shutil.copytree(LIVE, os.path.join(mods, "Skyy_SkyyHud"))
        hdir = os.path.join(mods, "Skyy_SkyyHud")
        lyd = os.path.join(hdir, "layouts")
        players_ = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []

        def ttree():
            o = {}
            for dp, dn, fn in os.walk(mods):
                for f in fn:
                    p_ = os.path.join(dp, f)
                    o[os.path.relpath(p_, mods)] = (open(p_, "rb").read(), os.path.getmtime(p_))
            return o

        def start():
            LS.CACHE.clear()
            LS.DIR = Paths.get(lyd)
            Cfg.FILE = Paths.get(os.path.join(hdir, "config.properties"))
            r_ = {"cfg": str(Cfg.load()), "arrow": int(MC.ARROW_BLOCKS)}
            Pub.start(Paths.get(mods), None)
            for us in players_:
                mp = LS.get(UUID.fromString(us))
                r_[us] = dict((w_, str(mp.get(w_).ser())) for w_ in [str(x) for x in Wid.IDS])
                mb_ = mm_box(mp)
                r_[us + "|hits"] = [w_ for w_, b_ in boxes_of(mp) if overlaps(mb_, b_)]
            Pub.flush()
            return r_
        t0_ = ttree()
        time.sleep(1.1)
        r1 = start()
        t1_ = ttree()
        chk(t1_ == t0_, "L. start 1 on the live copy writes nothing")
        for us in players_:
            fl = {}
            for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
                if "=" in ln and not ln.startswith("#"):
                    k_, v_ = ln.strip().split("=", 1)
                    fl[k_] = v_
            chk(all(r1[us][w_] == fl[w_] for w_ in r1[us] if w_ in fl), "L. %s...: every saved line loads exactly as saved" % us[:8])
            if "Minimap" not in fl:
                chk(not r1[us + "|hits"], "L. %s... (no Minimap line): the minimap's spot %s overlaps none of their widgets" % (us[:8], r1[us]["Minimap"]))
            res["report"]["live_" + us[:8]] = r1[us]["Minimap"]
        chk(r1["arrow"] == 16, "L. the live config.properties (no mm.arrowBlocks yet) -> 16 blocks, nothing written")
        time.sleep(1.1)
        r2 = start()
        chk(r2 == r1 and ttree() == t1_, "L. start 2: same layouts, no file churn")
        res["live_players"] = len(players_)
    else:
        res["live_players"] = -1
    for f_, v_ in saved_static:
        f_.set(None, v_)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--run" in sys.argv:
        run_child(arg("--run"), arg("--out"), arg("--mode"))
        return
    if "--bytecode" in sys.argv:
        harness_module("test_skyyhud_0.3.13.py", "hud0313h").run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"), arg("--ov"), arg("--nv"))
        return
    if "--audit" in sys.argv:
        harness_module("test_skyyhud_0.3.13.py", "hud0313h").run_audit(arg("--audit"), arg("--out"))
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
    common = ["--dir", SCRATCH, "--live", LIVE]
    res = {}
    for mode, jar, ver in (("new", JAR, VERSION), ("old", OLD_JAR, OLD_VERSION)):
        o = os.path.join(SCRATCH, "child-%s.json" % mode)
        p = subprocess.run([sys.executable, me, "--run", jar, "--out", o, "--mode", mode] + common, env=env)
        check(p.returncode == 0 and os.path.isfile(o), "child JVM for the %s jar ran (exit %s)" % (ver, p.returncode))
        if not os.path.isfile(o):
            return finish()
        res[mode] = json.load(open(o))
        check(not res[mode]["load_fails"], "A. %d classes of the %s jar load + initialize under -Xverify:all %s"
              % (res[mode]["classes"], ver, res[mode]["load_fails"][:3]))
    for mode in ("new", "old"):
        for ok, what in res[mode]["checks"]:
            check(ok, what)
    new, old = res["new"], res["old"]
    print("A-L. %d checks in the child JVMs (%d failed); live copy players: %s" % (
        len(new["checks"]) + len(old["checks"]), sum(1 for ok, w in new["checks"] + old["checks"] if not ok), new.get("live_players")))
    if new.get("live_players", -1) < 0:
        SKIPS.append("L (start twice on a copy of the live data): no live Skyy_SkyyHud folder at %s" % LIVE)
    a = new["scen"].get("two_world_A", {})
    print("  island 0.3.16: fill %s | arrow %s px, island piece %s px | sent %s" % (a.get("fill"), a.get("ap"), a.get("t"), a.get("sent")))
    print("  island 0.3.15 (the bug): %s" % old["scen"].get("old_bug"))
    for k, v in sorted(new["report"].items()):
        print("  %s: %s" % (k, v))
    # F: class bytes
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if os.path.isfile(bco):
        bc = json.load(open(bco))
        expect = {"LayoutStore", "Minimap", "MmCfg", "MmPng", "MmSess", "SkyyHudPlugin", "Widgets", "HudCfg"}
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
        check(zn == zo, "F. no class added or removed: %s %s" % (sorted(zn - zo), sorted(zo - zn)))
        check(not any(n.lower().endswith(".ui") for n in zipfile.ZipFile(JAR).namelist()), "F. the jar ships no .ui file")
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
    for s_ in SKIPS:
        print("  SKIPPED:", s_)
    for f in FAILS:
        print("  FAILED:", f)
    print("SkyyHud %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
