"""SkyyHud 0.3.14 - bare-JVM harness for the MINIMAP widget (tools/hud_0_3_14_patch.py, research/Minimap-Widget-Spec.md rev 2).

    python SkyyHud/test_skyyhud_0.3.14.py [--jar <SkyyHud-0.3.14.jar>] [--old <SkyyHud-0.3.13.jar>] [--live <Skyy_SkyyHud folder>]
                                          [--dir <scratch>] [--keep]

Build the jar first (python SkyyHud/build_skyyhud_0.3.14.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, java.io.tmpdir + TEMP/TMP in the scratch folder; HytaleServer.jar + the HUD jar; stand-ins (javassist subclasses,
never in the jar) for the network, the world, the store and the plugin manager - the real engine classes do the rest: HudManager,
CustomUIHud, PacketAdapters, MapImage / BitFieldArr, CommonAsset, UICommandBuilder). Every check EXECUTES the jar's own code:
  A   every class of the 0.3.14 jar (and the 0.3.13 jar) loads and initializes under -Xverify:all
  N   ENCODER: engine-packed MapImages (4 / 8 / 12 / 16 bit, 8-96 px, up to 780 colours, alpha) -> MmPng.tilePng at detail 16 / 24 / 32;
      every PNG decoded in Python and compared pixel by pixel with a Python reference (alpha-weighted average, alpha threshold 128,
      5-bit colours); no dark fringe at an explored edge (plain RGB would darken it); refused pieces (index out of range, short packed,
      0 size, bad bits) -> null, never a throw; 1-colour tiles; the generated pictures (masks, rings, 16 arrows, dots)
  H   the 16 headings: every yaw from -4 pi to 4 pi (radians, the engine's Transform.getDirection) - rounded to 8 it equals the probe's
      8-way MapGeo.bucket; arrow k points k x 22.5 degrees clockwise (its tip pixel)
  C   CACHE by CONTENT: the same piece twice / a copy of it = one encode; a changed piece = a new picture; the cache holds no MapImage;
      LRU cap; the asset name = sha256 of the PNG (the engine's CommonAsset.hash)
  P   PRIVACY: two players with different pieces for the same chunk each get their own; a chunk the player's stream never sent is never
      read from the engine cache (dark); the sweep reads it once the stream sent it
  D   DELIVERY: each picture once per connection (3 packets in one write, the probe's sequence); a world change (onRemove + re-attach)
      sends nothing again; a reconnect does; the 14 masks + 16 arrows + ONE rebuild once per connection, none for tiles; the cap
  T   the TAP through the engine's own PacketAdapters.__handleOutbound with a stand-in GamePacketHandler: nothing kept with no minimap
      (one volatile read), references queued, the 20,000 bound, garbage passes; DRAIN: unknown position = keys only, no MapImage kept;
      keep window; null pieces; ClearWorldMap; markers
  G   PAN / RING BUFFER: all 6 zooms x 7 sizes x walks across every chunk border in 8 directions (negative chunks too) and teleports:
      every window chunk in its floorMod slot with the right anchor, the window covers the clip, only entering slots change, the
      player at the clip centre
  U   HUD: the attach through the real HudManager on the (recording) world thread -> ONE CustomHud (SkyyHudMinimap, zOrder 5, clear)
      carrying the CACHED document (no build on the world thread); skyyhud_main untouched; markup kit-checked (no underscores, proven
      tokens + the 3 probe-proven ones); document sizes 25-529 slots; onRemove -> no update after it (push / onRemove synchronized);
      removeCustomHud only for our own HUD
  B   BETTERMAP: PluginManager without it -> BM = 2, ONE log line, no tap, no session, the editor says Needs BetterMap; with it -> BM = 1,
      its version, the tap registered once; a world with the map off / disabled by the admin -> no attach; no stream for 15 s -> hidden
  W   THREADS + BUDGET: the real executor runs the tick on "SkyyHud-Minimap" (not the shared scheduler); 500 tiles 96 -> 16 px on that
      thread; 20 simulated players walking: every tick inside the 3 ms budget (+ pans), round-robin fairness, HudManager touched only
      by world-thread tasks, retained heap, no MapImage left; a throwing player does not stop the others; the watchdog restarts a dead
      tick
  L   LAYOUT: the Minimap line round-trips (15th field only when not default), the 0.3.13 jar reads a 0.3.14 file with every field but
      the 15th (rollback), export / import, profiles, the server default, /skyyhud reset, sizes snap to 7 steps, Size- / Size+ = 25 %
  S   SETTINGS PAGE: built by MmUi (kit markup), every click payload saves the right field, zoom above the admin max refused / hidden,
      Back; other widgets' pages and the main HUD byte-identical to 0.3.13
  K   CONFIG: the 9 Server Setup rows (kit, KEEP=10), a file without mm.* keys = defaults (nothing written), hand-edited bad values ->
      defaults; the kit refuses out-of-range values
  Z   engine-access audit (the 0.3.13 harness's): every reference resolved with MethodHandles.Lookup in its own class - 0 refused
  F   class bytes 0.3.13 vs 0.3.14: only the expected classes / methods differ
  R   start twice on a scratch COPY of the live Skyy_SkyyHud (read only): nothing written, every layout loads as saved
Not testable without the game (UNVERIFIED in the build report): how the minimap looks, client FPS / memory with many pictures, the
arrow direction on screen, BetterMap's real tile sizes, the other-player marker names.
Nothing is deployed. Default scratch folder: tools/dev/scratch/hud-mm/harness (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, math, struct, random, time, importlib.util
import zlib as _zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3.14", "0.3.13"
PKG = "com.skyy.hud."
KEY, Z = "SkyyHudMinimap", 5
RADII = [64, 96, 128, 160, 224, 320]
STEPS = [50, 75, 100, 125, 150, 175, 200]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud-mm", "harness")))
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


def old_harness():
    spec = importlib.util.spec_from_file_location("hud0313h", os.path.join(HERE, "test_skyyhud_0.3.13.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


# ------------------------------------------------------------------------------------------------- Python references (pure)
def q5(v):
    v = max(0, min(255, v))
    v5 = (v * 31 + 127) // 255
    return (v5 << 3) | (v5 >> 2)


def ref_down(w, h, pal, idx, det):
    dw = min(w, det)
    dh = dw if w == h else max(1, h * dw // w)
    out = []
    for ty in range(dh):
        y0, y1 = ty * h // dh, (ty + 1) * h // dh
        y1 = max(y1, y0 + 1)
        for tx in range(dw):
            x0, x1 = tx * w // dw, (tx + 1) * w // dw
            x1 = max(x1, x0 + 1)
            sa = sr = sg = sb = n = 0
            for y in range(y0, y1):
                for x in range(x0, x1):
                    c = pal[idx[y * w + x]] & 0xffffffff
                    a = c & 255
                    sa += a
                    sr += ((c >> 24) & 255) * a
                    sg += ((c >> 16) & 255) * a
                    sb += ((c >> 8) & 255) * a
                    n += 1
            avg = (sa + n // 2) // n
            if avg < 128 or sa == 0:
                out.append((0, 0, 0, 0))
            else:
                out.append((q5((sr + sa // 2) // sa), q5((sg + sa // 2) // sa), q5((sb + sa // 2) // sa), 255))
    return dw, dh, out


def png_decode(b):
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("PNG signature")
    pos, chunks = 8, []
    while pos < len(b):
        ln = struct.unpack(">I", b[pos:pos + 4])[0]
        typ, data = b[pos + 4:pos + 8], b[pos + 8:pos + 8 + ln]
        crc = struct.unpack(">I", b[pos + 8 + ln:pos + 12 + ln])[0]
        if _zlib.crc32(typ + data) & 0xffffffff != crc:
            raise ValueError("CRC of %s" % typ)
        chunks.append((typ.decode("ascii"), data))
        pos += 12 + ln
    w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", chunks[0][1])
    plte = b"".join(d for t, d in chunks if t == "PLTE") or None
    trns = b"".join(d for t, d in chunks if t == "tRNS") or None
    raw = _zlib.decompress(b"".join(d for t, d in chunks if t == "IDAT"))
    chans = {3: 1, 6: 4}[ctype]
    stride = (w * depth * chans + 7) // 8
    if len(raw) != h * (stride + 1):
        raise ValueError("raw size")
    px = []
    for y in range(h):
        if raw[y * (stride + 1)] != 0:
            raise ValueError("filter")
        row = raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)]
        for x in range(w):
            if ctype == 3:
                bit = x * depth
                v = (row[bit >> 3] >> (8 - depth - (bit & 7))) & ((1 << depth) - 1)
                px.append((plte[3 * v], plte[3 * v + 1], plte[3 * v + 2], trns[v] if trns is not None and v < len(trns) else 255))
            else:
                px.append(tuple(row[4 * x:4 * x + 4]))
    return {"w": w, "h": h, "px": px, "ctype": ctype, "depth": depth, "kinds": [c[0] for c in chunks]}


def probe_bucket(yaw):
    """SkyyUiProbe 0.4 MapGeo.bucket (the 8-way the probe drew): bearing = -yaw degrees, 0 N .. 7 NW"""
    if math.isnan(yaw) or math.isinf(yaw):
        return 0
    deg = -float(yaw) * 180.0 / math.pi
    b = math.fmod(deg, 360.0)
    if b < 0:
        b += 360.0
    return int(math.floor((b + 22.5) / 45.0)) % 8


# ======================================================================================================== child: the NEW jar
def run_new(jar, out):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JInt, JLong, JByte, JString, JDouble, JFloat
    import skyybuild as B
    hcls = os.path.join(SCRATCH, "hclasses")
    shutil.rmtree(hcls, ignore_errors=True)
    os.makedirs(hcls)
    _jvm_start([jar], [B.JAVASSIST, hcls])
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

    # ---- stand-ins (harness only): the network (records every packet / batch), the world (records what is queued on its thread)
    net_ = CP.makeClass("skyyhudharness.HarnessNet", CP.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    for fsrc in ("public java.util.ArrayList sent;", "public java.util.ArrayList batches;", "public int writes;"):
        net_.addField(CtField.make(fsrc, net_))
    net_.addConstructor(CtNewConstructor.make(
        "public HarnessNet() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }", net_))
    net_.addMethod(CtNewMethod.make(
        "public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}", net_))
    net_.addMethod(CtNewMethod.make(
        "public void write(com.hypixel.hytale.protocol.ToClientPacket[] ps) {\n"
        "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  if (this.batches == null) this.batches = new java.util.ArrayList();\n"
        "  java.util.ArrayList one = new java.util.ArrayList();\n  this.writes++;\n"
        "  for (int i = 0; i < ps.length; i++) { this.sent.add(ps[i]); one.add(ps[i]); }\n  this.batches.add(one);\n}", net_))
    net_.addMethod(CtNewMethod.make("public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }", net_))
    net_.addMethod(CtNewMethod.make("public String getIdentifier() { return \"harness\"; }", net_))
    net_.writeFile(hcls)
    hw = CP.makeClass("skyyhudharness.HarnessWorld", CP.get("com.hypixel.hytale.server.core.universe.world.World"))
    for fsrc in ("public java.util.ArrayList tasks;", "public int count;", "public boolean refuse;"):
        hw.addField(CtField.make(fsrc, hw))
    hw.addConstructor(CtNewConstructor.make(
        "public HarnessWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", hw))
    hw.addMethod(CtNewMethod.make(
        "public void execute(java.lang.Runnable r) {\n  if (this.refuse) throw new java.lang.IllegalStateException(\"harness world takes no tasks\");\n"
        "  if (this.tasks == null) this.tasks = new java.util.ArrayList();\n  this.tasks.add(r);\n  this.count++;\n}", hw))
    hw.writeFile(hcls)
    # a Runnable that runs the minimap tick in a Java thread of our choosing and records the thread name
    NET, HW = JClass("skyyhudharness.HarnessNet"), JClass("skyyhudharness.HarnessWorld")

    STOREc, REFc = JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.component.Ref")
    TSC = fake("com.hypixel.hytale.component.SkyyHudTestStore", "com.hypixel.hytale.component.Store",
               "public SkyyHudTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
               "(com.hypixel.hytale.component.IResourceStorage) null); }", STOREc.class_,
               fields=["public java.util.IdentityHashMap comps;"],
               methods=["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                        "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
                        "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
                        "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
    # the empty item asset store (the editor's handles are new ItemStack(id, 1))
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    FS = fake("com.hypixel.hytale.assetstore.SkyyHudTestAssets", "com.hypixel.hytale.assetstore.AssetStore",
              "public SkyyHudTestAssets() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", AS.class_)
    st0 = U.allocateInstance(FS)
    jf(AS.class_, "assetMap").set(st0, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    jf(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_, "ASSET_STORE").set(None, st0)

    H = lambda n: JClass(PKG + n)
    MM, MP, MS, MH, MC, MU, WL, Wid, LS, HM, SP, EP, WP, Cfg, Plugin = (H("Minimap"), H("MmPng"), H("MmSess"), H("MmHud"), H("MmCfg"),
                                                                      H("MmUi"), H("WLayout"), H("Widgets"), H("LayoutStore"),
                                                                      H("HudMain"), H("SettingsPage"), H("EditorPage"), H("WidgetsPage"),
                                                                      H("HudCfg"), H("SkyyHudPlugin"))
    UUID, System, CHM = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths = JClass("java.nio.file.Paths")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Transform, Rot3 = JClass("com.hypixel.hytale.math.vector.Transform"), JClass("com.hypixel.hytale.math.vector.Rotation3f")
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    MIMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapImage")
    MCHc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapChunk")
    UWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMap")
    CWMc = JClass("com.hypixel.hytale.protocol.packets.worldmap.ClearWorldMap")
    MMKc = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapMarker")
    PTr, PPos = JClass("com.hypixel.hytale.protocol.Transform"), JClass("com.hypixel.hytale.protocol.Position")
    BFA = JClass("com.hypixel.hytale.server.core.universe.world.chunk.palette.BitFieldArr")
    CMAc = JClass("com.hypixel.hytale.server.core.asset.common.CommonAsset")
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
    CHP = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomHud")
    rnd = random.Random(20261006)

    def s32(v):
        v &= 0xffffffff
        return v - (1 << 32) if v >= (1 << 31) else v

    def pyb(arr):
        if arr is None:
            return None
        try:
            return bytes(memoryview(arr))
        except Exception:
            return bytes((int(x) & 255) for x in arr)

    def tail():
        return [str(x) for x in MM.tail()]

    def engine_image(w, h, pal, idx=None, bits=None):
        ncol = len(pal)
        if bits is None:
            bits = 4 if ncol <= 16 else (8 if ncol <= 256 else (12 if ncol <= 4096 else 16))
        if idx is None:
            idx = [rnd.randrange(ncol) for _i in range(w * h)]
        bf = BFA(JInt(bits), JInt(w * h))
        for i, v in enumerate(idx):
            bf.set(JInt(i), JInt(v))
        return MIMc(JInt(w), JInt(h), JArray(JInt)([s32(p) for p in pal]), JByte(bits), bf.get()), idx, bits

    def rand_pal(n, alpha=True):
        return [s32((rnd.randrange(1 << 24) << 8) | (rnd.choice([0, 64, 128, 200, 255, 255, 255]) if alpha else 255)) for _ in range(n)]

    # ======================================================================== N: the encoder
    ncases = 0
    worst = 0
    for (w, ncol, bits, alpha) in [(8, 3, None, True), (16, 16, None, True), (16, 120, None, False), (32, 300, 12, True), (96, 780, 12, True),
                                   (96, 200, 8, False), (96, 16, 4, True), (24, 40, 16, True), (16, 1, None, False), (96, 1, None, True),
                                   (33, 9, None, True), (96, 5000, 16, True), (1, 1, None, False)]:
        pal = rand_pal(ncol, alpha)
        m, idx, bt = engine_image(w, w, pal, bits=bits)
        for det in (16, 24, 32):
            png = pyb(MP.tilePng(m, JInt(det)))
            dw, dh, want = ref_down(w, w, pal, idx, det)
            try:
                d = png_decode(png)
                ok = d["w"] == dw and d["h"] == dh and d["px"] == want
            except Exception as ex:
                d, ok = None, False
            chk(ok, "N. %dx%d %d colours %d-bit alpha=%s at detail %d: PNG %dx%d = the Python reference (alpha-weighted, threshold, 5-bit)"
                % (w, w, ncol, bt, alpha, det, dw, dh))
            ncases += 1
            if png:
                worst = max(worst, len(png))
    # no dark fringe: a 96 px piece explored up to x < 52 (opaque green), unexplored (transparent black) beyond - block 8 (x 48-53) has
    # 4 opaque columns of 6: it must stay GREEN (alpha-weighted), a plain RGB average would give a darker green
    GREEN = s32(0x3c8a2eff)
    pal = [GREEN, 0x00000000]
    idx = [0 if (i % 96) < 52 else 1 for i in range(96 * 96)]
    m, _i, _b = engine_image(96, 96, pal, idx=idx)
    d = png_decode(pyb(MP.tilePng(m, JInt(16))))
    col8 = d["px"][8]
    col9 = d["px"][9]
    chk(col8 == (q5(0x3c), q5(0x8a), q5(0x2e), 255) and col9 == (0, 0, 0, 0),
        "N. explored edge: the 4/6 block stays the full green %s (plain RGB would be %s), the 0/6 block is transparent %s"
        % (col8, tuple(q5(int(v * 4 / 6)) for v in (0x3c, 0x8a, 0x2e)), col9))
    pal = [GREEN, 0x00000000]
    idx = [0 if (i % 96) < 50 else 1 for i in range(96 * 96)]
    m, _i, _b = engine_image(96, 96, pal, idx=idx)
    d = png_decode(pyb(MP.tilePng(m, JInt(16))))
    chk(d["px"][8] == (0, 0, 0, 0), "N. a 2/6 explored block (alpha 85 < 128) is transparent, not a dark fringe: %s" % (d["px"][8],))
    # refused pieces -> null, never a throw
    good, gidx, gb = engine_image(16, 16, rand_pal(4))
    bad_cases = {
        "index out of range": MIMc(JInt(16), JInt(16), JArray(JInt)([1, 2]), JByte(4), JArray(JByte)(bytes([0xff] * 128))),
        "short packed": MIMc(JInt(16), JInt(16), JArray(JInt)([1, 2, 3]), JByte(4), JArray(JByte)(bytes(10))),
        "0 size": MIMc(JInt(0), JInt(0), JArray(JInt)([1]), JByte(4), JArray(JByte)(bytes(8))),
        "no palette": MIMc(JInt(16), JInt(16), None, JByte(4), JArray(JByte)(bytes(128))),
        "17 bits": MIMc(JInt(4), JInt(4), JArray(JInt)([1]), JByte(17), JArray(JByte)(bytes(64))),
        "null": None}
    for nm, bm in bad_cases.items():
        try:
            r_ = MP.tilePng(bm, JInt(16))
            chk(r_ is None, "N. refused piece (%s) -> null" % nm)
        except Exception as ex:
            chk(False, "N. refused piece (%s) threw %s" % (nm, ex))
    # generated pictures decode; masks: round inside / outside, square full
    for C_ in (74, 152, 304):
        for shp in (0, 1):
            px = [int(v) & 0xffffffff for v in MP.mask(JInt(C_), JInt(shp))]
            inside = px[(C_ // 2) * C_ + C_ // 2] == 0xffffffff
            corner = px[0]
            chk(inside and (corner == (0xffffffff if shp == 1 else 0)), "N. mask %d px %s: centre opaque, corner %s" % (C_, "square" if shp else "round", hex(corner)))
            d = png_decode(pyb(MP.encode(JInt(C_), JInt(C_), MP.mask(JInt(C_), JInt(shp)))))
            chk(d["w"] == C_ and len(d["px"]) == C_ * C_, "N. mask %d px PNG decodes" % C_)
    for S_ in (80, 160, 320):
        px = [int(v) & 0xffffffff for v in MP.ring(JInt(S_), JInt(max(3, S_ // 40)), JInt(0), JInt(s32(0xb4c8c9ff)))]
        chk(px[(S_ // 2) * S_ + S_ // 2] == 0 and px[(S_ // 2) * S_ + 1] != 0, "N. ring %d: hollow centre, band at the edge" % S_)
    res["report"]["encode_worst_png"] = worst
    res["report"]["encode_cases"] = ncases

    # ======================================================================== H: headings + arrows
    bad = []
    for i in range(-4000, 4001):
        yaw = i * (4 * math.pi) / 4000.0
        k = int(MM.heading(JFloat(yaw)))
        jy = float(JFloat(yaw))
        if not 0 <= k < 16:
            bad.append((yaw, k))
            continue
        # rounded to 8 (16-way index k -> 8-way round(k / 2) mod 8) the probe's bucket, except on the exact 8-way boundaries
        deg = math.fmod(-jy * 180.0 / math.pi, 360.0)
        deg = deg + 360.0 if deg < 0 else deg
        near_edge = abs(math.fmod(deg + 22.5, 45.0)) < 1e-3 or abs(math.fmod(deg + 22.5, 45.0) - 45.0) < 1e-3
        ok8 = {k // 2} if k % 2 == 0 else {k // 2, (k + 1) // 2 % 8}     # an odd 16-way index lies between two 8-way ones
        if probe_bucket(jy) not in ok8 and not near_edge and not (abs(math.fmod(deg + 11.25, 22.5)) < 1e-3):
            bad.append((round(yaw, 4), k, probe_bucket(jy)))
    chk(not bad, "H. heading(yaw) for 8,001 yaws in -4 pi..4 pi: 0-15 and, rounded to 8, the probe's 8-way bucket: %s" % bad[:5])
    chk(int(MM.heading(JFloat(0.0))) == 0 and int(MM.heading(JFloat(-math.pi / 2))) == 4 and int(MM.heading(JFloat(math.pi))) == 8
        and int(MM.heading(JFloat(math.pi / 2))) == 12, "H. yaw 0 = N (0), -pi/2 = E (4), pi = S (8), +pi/2 = W (12)")

    def tip_ok(k):
        """the arrow's tip lies k x 22.5 degrees clockwise from screen-up: a filled pixel 12 px from the centre that way, none
        12 px the other way (the notch between the feet)"""
        px = [int(v) & 0xffffffff for v in MP.arrow(JInt(k))]
        a = math.radians(22.5 * k)

        def filled(dist):
            x, y = 15.5 + dist * math.sin(a), 15.5 - dist * math.cos(a)
            return any(px[yy * 32 + xx] == 0xffffffff for xx in (int(math.floor(x)), int(math.ceil(x))) for yy in (int(math.floor(y)), int(math.ceil(y)))
                       if 0 <= xx < 32 and 0 <= yy < 32)
        return filled(11.0) and not filled(-11.0)
    tips = [tip_ok(k) for k in range(16)]
    chk(all(tips), "H. arrow k points k x 22.5 degrees CLOCKWISE from screen-up (tip there, the notch opposite): %s" % tips)

    # ======================================================================== the world / player stand-ins for everything below
    nxt = [3000]

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

    def map_manager(enabled, images):
        m_ = U.allocateInstance(WMMc.class_)
        imgs = L2O()
        for (cx, cz), im in images.items():
            if int(CHU.indexChunk(JInt(cx), JInt(cz))) != -1:
                imgs.put(JLong(int(CHU.indexChunk(JInt(cx), JInt(cz)))), IEc(im))
        field(WMMc, "images").set(m_, imgs)
        sp = UWMSc()
        sp.enabled = enabled
        field(WMMc, "worldMapSettings").set(m_, WMSc(None, JFloat(0.5), JFloat(1.0), JInt(1), JInt(64), sp))
        return m_, imgs

    def put_engine(imgs, cx, cz, im):
        if int(CHU.indexChunk(JInt(cx), JInt(cz))) == -1:
            return                      # the engine's own map cannot hold chunk (-1, -1): its key is the map's EMPTY marker
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

    def player(n, name, world, x=0.5, z=0.5, yaw=0.0):
        pr = U.allocateInstance(PRc.class_)
        field(PRc, "uuid").set(pr, UUID(0x5ce0, n))
        field(PRc, "username").set(pr, name)
        net = U.allocateInstance(NET.class_)
        field(PRc, "packetHandler").set(pr, net)
        st = U.allocateInstance(TSC)
        ref = U.allocateInstance(REFc.class_)
        field(REFc, "store").set(ref, st)
        pl = U.allocateInstance(PLAc.class_)
        hm = HMc()
        field(PLAc, "hudManager").set(pl, hm)
        comps = JClass("java.util.IdentityHashMap")()
        comps.put(CT_PR, pr)
        comps.put(CT_PLA, pl)
        allc = JClass("java.util.IdentityHashMap")()
        allc.put(ref, comps)
        st.comps = allc
        es = U.allocateInstance(ESc.class_)
        field(ESc, "world").set(es, world)
        field(STOREc, "externalData").set(st, es)
        field(PRc, "entity").set(pr, ref)
        PBU.put(pr.getUuid(), pr)
        o = {"pr": pr, "net": net, "st": st, "ref": ref, "pl": pl, "hm": hm, "w": world}
        move_to(o, world, x, z, yaw)
        return o

    def move_to(o, world, x, z, yaw=0.0):
        pr = o["pr"]
        field(PRc, "transform").set(pr, Transform(JDouble(x), JDouble(64.0), JDouble(z)))
        field(PRc, "headRotation").set(pr, Rot3(JFloat(0.0), JFloat(yaw), JFloat(0.0)))
        field(PRc, "worldUuid").set(pr, WUUIDS[str(world.getName())])
        if world is not o["w"]:
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

    def sent(o, i0=0):
        n_ = o["net"]
        return [] if n_.sent is None else [n_.sent.get(i) for i in range(i0, int(n_.sent.size()))]

    def mark(o):
        return 0 if o["net"].sent is None else int(o["net"].sent.size())

    def kinds(ps):
        return [str(p_.getClass().getSimpleName()) for p_ in ps]

    def assets_in(ps):
        return [str(p_.asset.name) for p_ in ps if str(p_.getClass().getSimpleName()) == "AssetInitialize"]

    def huds(ps):
        return [p_ for p_ in ps if str(p_.getClass().getSimpleName()) == "CustomHud"]

    def as4(c):
        return (str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                None if c.text is None else str(c.text))

    # no real executor during the deterministic sections: EXEC = a parked stand-in, ticks run on THIS thread
    STPE = JClass("java.util.concurrent.ScheduledThreadPoolExecutor")
    parked = STPE(1)

    def park():
        MM.EXEC = parked

    def reset_mm():
        MM.shutdown0()
        MM.REQ.clear()
        MM.CACHE.clear()
        MM.GEN.clear()
        MM.DOCS.clear()
        MM.NOSTREAM.clear()
        MM.TAIL.clear()
        MM.RELAYOUT = False
        park()

    work = os.path.join(SCRATCH, "child-new")
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
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)

    # ======================================================================== B: BetterMap missing / found (PluginManager stand-in)
    PLM = JClass("com.hypixel.hytale.server.core.plugin.PluginManager")
    PIDc = JClass("com.hypixel.hytale.common.plugin.PluginIdentifier")
    PAD = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    outbound = jf(PAD.class_, "outboundHandlers").get(None)
    saved_static.append((jf(PLM.class_, "instance"), jf(PLM.class_, "instance").get(None)))
    plm = U.allocateInstance(PLM.class_)
    field(PLM, "lock").set(plm, JClass("java.util.concurrent.locks.ReentrantReadWriteLock")())
    plugins = JClass("java.util.HashMap")()
    field(PLM, "plugins").set(plm, plugins)
    jf(PLM.class_, "instance").set(None, plm)
    reset_mm()
    MC.BM = 0
    use_dir("b1")
    mmA, imgsA = map_manager(True, {})
    WA = make_world("default", mmA)
    pa = player(1, "Steve", WA)
    n0 = int(outbound.size())
    MM.hello(pa["pr"])
    lines = tail()
    chk(int(MC.BM) == 2 and lines == ["minimap: BetterMap (dev.ninesliced:BetterMap) is not installed or disabled - the minimap widget stays off"],
        "B. no BetterMap: BM = 2 and exactly ONE log line: %s" % lines)
    MM.hello(pa["pr"])
    MM.ready(pa["pr"], pa["st"])
    chk(len(tail()) == 1 and int(outbound.size()) == n0 and MM.TAPF is None and int(MM.SESS.size()) == 0 and int(MM.REQ.size()) == 0,
        "B. ... no second line, the tap never registered, no session, no request")
    chk(str(Wid.text("Minimap", pa["pr"], JLong(0))) == "Needs BetterMap", "B. ... the editor's Minimap box says Needs BetterMap")
    chk("not installed" in str(MM.bmText()), "B. ... the settings' BetterMap line says not installed")
    # main HUD: no minimap element ever
    h0 = HM(pa["pr"])
    b0 = UCB()
    mb = HM.class_.getDeclaredMethod("build", UCB.class_)
    mb.setAccessible(True)
    mb.invoke(h0, b0)
    chk(not any("SkyyMm" in (str(c.text) if c.text else "") or "Minimap" in (str(c.text) if c.text else "") for c in b0.getCommands()),
        "B. skyyhud_main never draws the Minimap")
    # found: a JavaPlugin stand-in registered under dev.ninesliced:BetterMap
    JPc = JClass("com.hypixel.hytale.server.core.plugin.JavaPlugin")
    bm = U.allocateInstance(fake("com.hypixel.hytale.server.core.plugin.SkyyHudTestBetterMap", "com.hypixel.hytale.server.core.plugin.JavaPlugin",
                                 "public SkyyHudTestBetterMap() { super((com.hypixel.hytale.server.core.plugin.JavaPluginInit) null); }", JPc.class_))
    PSt = JClass("com.hypixel.hytale.server.core.plugin.PluginState")
    states = [str(x) for x in PSt.values()]
    for sname in ("ENABLED", "STARTED", "START", "SETUP"):
        if sname in states:
            field(JClass("com.hypixel.hytale.server.core.plugin.PluginBase"), "state").set(bm, getattr(PSt, sname))
            if bool(bm.isEnabled()):
                break
    MANc = JClass("com.hypixel.hytale.common.plugin.PluginManifest")
    man = U.allocateInstance(MANc.class_)
    try:
        field(MANc, "version").set(man, JClass("com.hypixel.hytale.common.semver.Semver").fromString("1.3.8"))
    except Exception:
        pass
    field(JClass("com.hypixel.hytale.server.core.plugin.PluginBase"), "manifest").set(bm, man)
    plugins.put(PIDc("dev.ninesliced", "BetterMap"), bm)
    MC.BM = 0
    MM.TAIL.clear()
    MM.hello(pa["pr"])
    MM.hello(pa["pr"])
    lines = tail()
    chk(int(MC.BM) == 1 and lines == ["minimap: BetterMap 1.3.8 found - minimap on"] and MM.TAPF is not None and int(outbound.size()) == n0 + 1,
        "B. BetterMap 1.3.8 enabled: BM = 1, ONE line '%s', the outbound tap registered once (%d -> %d)" % (lines, n0, int(outbound.size())))
    chk(int(MM.SESS.size()) == 1 and bool(MM.SESS.get(pa["pr"].getUuid()).wants) and int(MM.TAPS) == 1,
        "B. ... the first connect makes the session (the tap keeps the join burst's keys)")
    res["report"]["bm_states"] = states

    # ======================================================================== T: the tap through the engine's own PacketAdapters
    GPH = JClass("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")
    handle_out = getattr(PAD, "__handleOutbound")
    gph = U.allocateInstance(GPH.class_)
    field(GPH, "playerRef").set(gph, pa["pr"])
    sA = MM.SESS.get(pa["pr"].getUuid())

    def upd(chunks, added=(), removed=()):
        arr = JArray(MCHc)(len(chunks))
        for i, c in enumerate(chunks):
            arr[i] = None if c is None else MCHc(JInt(c[0]), JInt(c[1]), c[2])
        am = None
        if added:
            am = JArray(MMKc)(len(added))
            for i, (mid, img, x, z) in enumerate(added):
                am[i] = MMKc(mid, None, img, PTr(PPos(JDouble(x), JDouble(64.0), JDouble(z)), None), None, None)
        rm = JArray(JString)(list(removed)) if removed else None
        return UWMc(arr, am, rm)

    imgP, _i, _b = engine_image(16, 16, rand_pal(6, False))
    burst = upd([(cx, cz, imgP) for cx in range(-20, 21) for cz in range(-20, 21)])
    MM.TAPS = 0
    r_ = bool(handle_out(gph, burst))
    chk(not r_ and int(sA.qn.get()) == 0, "T. TAPS = 0: the packet passes, nothing kept (one volatile read)")
    MM.recountTaps()
    for p_ in (burst, CWMc(), JClass("com.hypixel.hytale.protocol.packets.setup.AssetFinalize")(), UWMc(None, None, None)):
        try:
            r_ = bool(handle_out(gph, p_))
            ok = not r_
        except Exception as ex:
            ok = False
        chk(ok, "T. %s through the engine's outbound adapters: passed on, no exception" % p_.getClass().getSimpleName())
    chk(int(sA.qn.get()) == 3 and int(sA.q.size()) == 3, "T. exactly the 3 map packets queued (UpdateWorldMap x2 + ClearWorldMap), as references")
    # drain with an UNKNOWN position (the join burst): keys only, no MapImage kept
    sA.q.clear()
    sA.qn.set(0)
    sA.qc.set(0)
    handle_out(gph, CWMc())
    handle_out(gph, burst)
    sA.posKnown = False
    sA.h = 0
    MM.drain(sA)
    ph = int(sA.ph)
    kimgs = [(int(MM.keyX(JLong(int(k_)))), int(MM.keyZ(JLong(int(k_))))) for k_ in sA.known.keySet()]
    chk(int(sA.streamed.size()) == 41 * 41 and bool(sA.provOk) and ph >= 1 and len(kimgs) == (2 * ph + 1) ** 2 - 1
        and all(abs(x_) <= ph and abs(z_) <= ph for x_, z_ in kimgs) and bool(sA.streamSeen),
        "T. drain, position not known yet (FIX: the join burst's pieces are kept): 1,681 keys, MapImages ONLY inside the provisional window "
        "around the player's chunk (h %d: %d kept), keys only outside" % (ph, len(kimgs)))
    chk(sA.originImg is not None and int(MM.key(JInt(-1), JInt(-1))) == -1 and not sA.known.containsKey(JLong(-1)),
        "T. FIX: chunk (-1,-1) (key -1 = the engine map's EMPTY marker) keeps the stream's own piece aside (originImg)")
    # the bound
    sA.q.clear()
    sA.qn.set(0)
    sA.qc.set(0)
    d0 = int(sA.dropped.get())
    small = upd([(0, 0, None)])
    for _ in range(20005):
        MM.tap(pa["pr"], small)
    chk(int(sA.qn.get()) == 20000 and int(sA.dropped.get()) - d0 == 5, "T. the 20,000-packet bound: 5 counted as dropped, never blocks")
    sA.q.clear()
    sA.qn.set(0)
    sA.qc.set(0)
    # FIX (critic: the bound counted packets, a stalled thread could hold 20,000 packets of pieces): 2,048 pieces queued per player
    imgQ = engine_image(16, 16, rand_pal(3, False))[0]
    bigp = upd([(cx, 300, imgQ) for cx in range(1500)])
    k0 = int(sA.keysOnly.get())
    MM.tap(pa["pr"], bigp)
    q1 = int(sA.qc.get())
    MM.tap(pa["pr"], bigp)
    mkp = UWMc(JArray(MCHc)([MCHc(JInt(cx), JInt(301), imgQ) for cx in range(1500)]),
               JArray(MMKc)([MMKc("wp-q", None, "Waypoint.png", PTr(PPos(JDouble(1.0), JDouble(64.0), JDouble(1.0)), None), None, None)]), None)
    MM.tap(pa["pr"], mkp)
    qitems = [sA.q.toArray()[i] for i in range(int(sA.q.size()))]
    nlong = sum(1 for o_ in qitems if str(o_.getClass().getName()) == "[J")
    chk(q1 == 1500 and int(sA.qc.get()) == 1500 and nlong == 2 and int(sA.keysOnly.get()) - k0 == 2 and len(qitems) == 4,
        "T. FIX piece bound: 1,500 pieces queued as the packet; the next two (past 2,048) as chunk KEYS only (long[]), the markers of the "
        "second re-queued without pieces (%d items, %d key arrays, qc %d)" % (len(qitems), nlong, int(sA.qc.get())))
    sA.posKnown = True
    sA.ccx, sA.ccz, sA.h = 0, 0, 2
    MM.drain(sA)
    held_q = sum(1 for k_ in sA.known.keySet() if int(MM.keyZ(JLong(int(k_)))) in (300, 301))
    chk(int(sA.qc.get()) == 0 and bool(sA.streamed.contains(JLong(int(MM.key(JInt(1499), JInt(301)))))) and held_q == 0
        and sA.markers.containsKey("wp-q"), "T. FIX ... drained: qc back to 0, the key-only chunks are streamed (the engine cache serves "
                                           "them), no piece held, the marker kept")
    sA.markers.clear()
    for cx in range(1500):
        for cz in (300, 301):
            sA.streamed.remove(JLong(int(MM.key(JInt(cx), JInt(cz)))))
    sA.posKnown = False
    sA.h = 0
    try:
        MM.tap(None, burst)
        MM.tap(pa["pr"], None)
        MM.tap(pa["pr"], JString("garbage"))
        ok = True
    except Exception:
        ok = False
    chk(ok and int(sA.qn.get()) == 0, "T. garbage (null player, null packet, a String) never throws, nothing kept")

    # ======================================================================== U + D: attach, HUD, delivery
    MM.TAIL.clear()
    for cx in range(-12, 13):
        for cz in range(-12, 13):
            put_engine(imgsA, cx, cz, engine_image(96, 96, rand_pal(rnd.randrange(2, 200), True), bits=12)[0])
    i0 = mark(pa)
    MM.ready(pa["pr"], pa["st"])
    chk(int(MM.REQ.size()) == 1 and (WA.tasks is None or int(WA.tasks.size()) == 0), "U. ready (world thread): ONE request queued, nothing else")
    MM.tick()
    ps = sent(pa, i0)
    ks = kinds(ps)
    nmask = sum(1 for a in assets_in(ps) if a.startswith("UI/Custom/SkyyHudMmMask-"))
    narrow = sum(1 for a in assets_in(ps) if "/arrow-" in a)
    chk(nmask == 14 and narrow == 16 and ks.count("RequestCommonAssetsRebuild") == 1 and not huds(ps),
        "U/D. the first attach of a connection: 14 masks + 16 arrows + ONE RequestCommonAssetsRebuild, no HUD packet yet (masks %d arrows %d rebuilds %d)"
        % (nmask, narrow, ks.count("RequestCommonAssetsRebuild")))
    batches = [list(b_) for b_ in pa["net"].batches] if pa["net"].batches is not None else []
    chk(all(kinds(b_)[0] == "AssetInitialize" and kinds(b_)[-1] == "AssetFinalize" and len(b_) == 3 for b_ in batches),
        "D. every picture = AssetInitialize + AssetPart + AssetFinalize in ONE write (%d writes)" % len(batches))
    q_ = [str(t_.getClass().getSimpleName()) for t_ in (WA.tasks or [])]
    chk(q_ == ["MmAttach"], "U. the HUD goes to the WORLD thread as one MmAttach task: %s" % q_)
    i1 = mark(pa)
    hm = pa["hm"]
    run_world(WA)
    ps = sent(pa, i1)
    hp = huds(ps)
    chk(len(hp) == 1 and str(hp[0].hudId) == KEY and int(hp[0].zOrder) == Z and bool(hp[0].clear) and hm.getCustomHud(KEY) is not None,
        "U. world thread: HudManager.addCustomHud -> ONE CustomHud (%s, zOrder %d, clear) with the document" % (KEY, Z))
    hudA = sA.hud
    docA = [as4(c) for c in hp[0].commands] if hp else []
    cached = [as4(c) for c in hudA.doc.getCommands()]
    chk(docA == cached and len(docA) > 100, "U. the packet carries the CACHED document (built on the minimap thread; %d commands)" % len(docA))
    # the markup: kit checks
    import skyyui as SUI
    toks = {}
    bad_mk = []
    for t_, sel, data, text in docA:
        if t_ == "AppendInline":
            try:
                SUI.check_markup(text, root=sel is None and False)
            except Exception as ex:
                bad_mk.append(str(ex)[:120])
            if "_" in "".join(re.findall(r"#([A-Za-z0-9_]+)", text)):
                bad_mk.append("underscore id: " + text[:60])
            for k_, g_ in SUI.proven_tokens([text]).items():
                toks[k_] = g_
    unproven = sorted(k_ for k_, g_ in toks.items() if g_ is not None)
    chk(not bad_mk and unproven == ["AssetPath", "MaskTexturePath", "element AssetImage"],
        "U. the document passes the kit's markup checks, no underscore id, every token proven except the 3 probe-proven ones: %s %s" % (bad_mk[:3], unproven))
    chk(int(hudA.pushes) == 0 and (WA.tasks is None or int(WA.tasks.size()) == 0), "U. nothing pushed before the first tick")
    # first tick after the attach: the player's slots, grid, arrow, markers (one update) - not all encoded at once (budget)
    sA.posKnown = False
    i2 = mark(pa)
    total_ticks = 0
    t0 = time.time()
    for _ in range(40):
        MM.tick()
        total_ticks += 1
        if bool(sA.fillLogged):
            break
    ps = sent(pa, i2)
    upd_hud = [p_ for p_ in huds(ps) if not bool(p_.clear)]
    chk(len(upd_hud) >= 1 and bool(sA.fillLogged), "U. ticks push updates (no clear) until the window is filled: %d updates in %d ticks" % (len(upd_hud), total_ticks))
    fill = [l_ for l_ in tail() if l_.startswith("minimap: first fill Steve in 'default': ")]
    chk(len(fill) == 1, "U. ONE first-fill log line: %s" % fill)
    res["report"]["first_fill"] = fill
    w_ = int(sA.w)
    real = sum(1 for p_ in sA.slotPath if p_ is not None and str(p_) != str(sA.dark))
    sl_o = int(MM.slot(JInt(-1), JInt(-1), JInt(w_)))
    chk(real == w_ * w_ and str(sA.slotPath[sl_o]) != str(sA.dark),
        "P. every window chunk the stream sent got its piece - FIX: chunk (-1,-1) too (the burst's own piece; the engine map cannot hold it) "
        "(%d / %d)" % (real, w_ * w_))
    known_imgs = sum(1 for v in sA.known.values() if isinstance(v, MIMc))
    chk(known_imgs == 0, "C. after the fill the player holds NO MapImage (content keys only): %d" % known_imgs)
    chk(all(isinstance(v, JClass(PKG + "MmAsset")) for v in MM.CACHE.values()), "C. the shared cache holds pictures only (MmAsset), no MapImage")
    # delivery: once per connection
    names_sent = assets_in(sent(pa, 0))
    chk(len(names_sent) == len(set(names_sent)), "D. no picture was sent twice on this connection (%d pictures)" % len(names_sent))
    # world change: onRemove (engine resetHud) -> no update after it; re-attach -> nothing sent again
    rm_ = HMc.class_.getDeclaredMethod("resetHud", PRc.class_)
    i3 = mark(pa)
    hm.resetHud(pa["pr"])
    chk(bool(hudA.gone), "U. HudManager.resetHud (world change) -> our onRemove marked the HUD gone")
    bb = UCB()
    bb.set("#SkyyMmArrow.AssetPath", "x")
    chk(not bool(hudA.push(bb)) and not huds([p_ for p_ in sent(pa, i3) if not bool(getattr(p_, "clear", True))]),
        "U. push after onRemove is refused (no update for a removed HUD - critic C12)")
    JMod = JClass("java.lang.reflect.Modifier")
    chk(JMod.isSynchronized(MH.class_.getDeclaredMethod("push", UCB.class_).getModifiers())
        and JMod.isSynchronized(MH.class_.getDeclaredMethod("onRemove").getModifiers()), "U. push and onRemove share the HUD's monitor")
    MM.tick()
    chk(sA.hud is None, "U. the tick pauses the session (HUD gone)")
    i4 = mark(pa)
    MM.ready(pa["pr"], pa["st"])
    MM.tick()
    run_world(WA)
    for _ in range(10):
        MM.tick()
    again = assets_in(sent(pa, i4))
    chk(not again and kinds(sent(pa, i4)).count("RequestCommonAssetsRebuild") == 0 and len(huds(sent(pa, i4))) >= 2,
        "D. world change + re-attach: the HUD is shown again, NO picture and no rebuild sent again (P3: the client keeps them): %s" % again[:3])
    # reconnect: quit drops the per-connection list -> the next connection gets everything again
    MM.quit(pa["pr"])
    MM.tick()
    chk(int(MM.SESS.size()) == 0 and not MM.DELIVERED.containsKey(pa["pr"].getUuid()), "D. disconnect: session and delivered list dropped")
    i5 = mark(pa)
    MM.hello(pa["pr"])
    MM.tap(pa["pr"], upd([]))
    MM.ready(pa["pr"], pa["st"])
    MM.tick()
    run_world(WA)
    for _ in range(10):
        MM.tick()
    again = assets_in(sent(pa, i5))
    chk(len(again) > 30 and kinds(sent(pa, i5)).count("RequestCommonAssetsRebuild") == 1, "D. reconnect: pictures sent again (+ ONE rebuild): %d" % len(again))
    sA = MM.SESS.get(pa["pr"].getUuid())
    # cap: a connection that already holds 6,000 pictures gets dark fill + ONE log line
    MM.TAIL.clear()
    tiles0 = int(sA.tiles)
    t_a = JClass(PKG + "MmAsset")(JString("UI/SkyyHud/mm/tilecount.png"), JString("2" * 64), JArray(JByte)(bytes(20)))
    t_g = JClass(PKG + "MmAsset")(JString("UI/SkyyHud/mm/dot-tilecount.png"), JString("3" * 64), JArray(JByte)(bytes(20)))
    MM.send(sA, t_a, True)
    MM.send(sA, t_g, False)
    MM.send(sA, t_a, True)
    chk(int(sA.tiles) == tiles0 + 1, "D. FIX: the cap counts map pieces only (a piece +1, a generated picture 0, a re-send 0)")
    tiles0 = int(sA.tiles)
    sA.tiles = 6000
    i6 = mark(pa)
    a_ = JClass(PKG + "MmAsset")(JString("UI/SkyyHud/mm/capcheck.png"), JString("0" * 64), JArray(JByte)(bytes(20)))
    g_ = JClass(PKG + "MmAsset")(JString("UI/SkyyHud/mm/dot-capcheck.png"), JString("1" * 64), JArray(JByte)(bytes(20)))
    r1 = bool(MM.send(sA, a_, True))
    r2 = bool(MM.send(sA, a_, True))
    r3 = bool(MM.send(sA, g_, False))
    capl = [l_ for l_ in tail() if "reached 6000 map pieces" in l_]
    msgs = [k_ for k_ in kinds(sent(pa, i6)) if k_ not in ("AssetInitialize", "AssetPart", "AssetFinalize")]
    chk(not r1 and not r2 and r3 and len(capl) == 1 and bool(sA.capWarned) and len(msgs) == 1,
        "D. the per-connection cap: a map piece past 6,000 is not sent, ONE log line + FIX: the player is told ONCE (%s); a generated "
        "picture still goes" % msgs)
    sA.tiles = tiles0
    sA.capWarned = False
    MM.CAPPED.clear()

    # ======================================================================== C: the cache by content
    sC = sA
    e0 = int(MM.ENC_N)
    base_img, bidx, bbits = engine_image(96, 96, rand_pal(50, False), bits=12)
    copy_img = MIMc(base_img.width, base_img.height, base_img.palette, base_img.bitsPerIndex, JArray(JByte)(pyb(base_img.packedIndices)))
    budget = JArray(JInt)([10])
    far = System.nanoTime() + 10 ** 10
    sC.known.clear()
    sC.known.put(JLong(int(MM.key(JInt(500), JInt(500)))), base_img)
    a1 = MM.resolve(sC, JInt(500), JInt(500), budget, JLong(far), False)
    sC.known.put(JLong(int(MM.key(JInt(501), JInt(500)))), copy_img)
    a2 = MM.resolve(sC, JInt(501), JInt(500), budget, JLong(far), False)
    chk(a1 is not None and a2 is not None and str(a1.getName()) == str(a2.getName()) and int(MM.ENC_N) - e0 == 1,
        "C. the same content in two MapImage objects (two chunks) = ONE encode, one picture")
    idx2 = [(v + 1) % 50 for v in bidx]
    chg = engine_image(96, 96, [int(x) for x in base_img.palette], idx=idx2, bits=12)[0]
    sC.known.put(JLong(int(MM.key(JInt(500), JInt(500)))), chg)
    a3 = MM.resolve(sC, JInt(500), JInt(500), budget, JLong(far), False)
    chk(a3 is not None and str(a3.getName()) != str(a1.getName()) and int(MM.ENC_N) - e0 == 2, "C. a changed piece = a new picture (re-encoded)")
    chk(str(a1.getName()) == "UI/SkyyHud/mm/" + str(CMAc.hash(a1.bytes))[:16] + ".png", "C. the picture name = sha256 of the PNG (CommonAsset.hash)")
    zero = JArray(JInt)([0])
    sC.known.put(JLong(int(MM.key(JInt(502), JInt(500)))), engine_image(16, 16, rand_pal(7, False))[0])
    sC.more = False
    a4 = MM.resolve(sC, JInt(502), JInt(500), zero, JLong(far), False)
    chk(a4 is None and bool(sC.more), "C. out of budget: no picture yet, s.more (the next tick goes on)")
    past = System.nanoTime() - 1
    a5 = MM.resolve(sC, JInt(502), JInt(500), JArray(JInt)([5]), JLong(past), False)
    chk(a5 is None, "C. past the 3 ms deadline: no encode")
    # LRU cap
    for i in range(int(MM.cacheCap()) + 50):
        MM.CACHE.put(JString("fill-%d" % i), a1)
    MM.trimCache()
    chk(int(MM.CACHE.size()) == int(MM.cacheCap()), "C. the LRU keeps max(4096, players x slots) = %d entries" % int(MM.cacheCap()))
    MM.CACHE.clear()
    sC.known.clear()

    # ======================================================================== P: privacy - two players, different pieces for the same chunk
    reset_mm()
    MC.BM = 1
    use_dir("p1")
    mmP, imgsP = map_manager(True, {})
    WPW = make_world("default", mmP)
    pA = player(11, "Ann", WPW, 16.0, 16.0)
    pB = player(12, "Bob", WPW, 16.0, 16.0)
    for o in (pA, pB):
        MM.hello(o["pr"])
        MM.tap(o["pr"], upd([]))
        MM.ready(o["pr"], o["st"])
    MM.tick()
    run_world(WPW)
    sPA, sPB = MM.SESS.get(pA["pr"].getUuid()), MM.SESS.get(pB["pr"].getUuid())
    MM.tick()
    imA = engine_image(16, 16, [s32(0xff0000ff)] * 1)[0]
    imB = engine_image(16, 16, [s32(0x0000ffff)] * 1)[0]
    imE = engine_image(16, 16, [s32(0x00ff00ff)] * 1)[0]
    put_engine(imgsP, 1, 0, imE)
    MM.tap(pA["pr"], upd([(0, 0, imA), (1, 0, imE)]))
    MM.tap(pB["pr"], upd([(0, 0, imB)]))

    def due_now():
        for s_ in (sPA, sPB):
            s_.nextPanAt = 0
    for _ in range(6):
        due_now()
        MM.tick()
    slA = sPA.slotPath[int(MM.slot(JInt(0), JInt(0), JInt(int(sPA.w))))]
    slB = sPB.slotPath[int(MM.slot(JInt(0), JInt(0), JInt(int(sPB.w))))]
    chk(str(slA) != str(slB) and str(slA) != str(sPA.dark) and str(slB) != str(sPB.dark),
        "P. chunk 0,0: Ann sees HER piece, Bob HIS (content keys, never coordinates - critic B6): %s vs %s" % (slA, slB))
    e1A = sPA.slotPath[int(MM.slot(JInt(1), JInt(0), JInt(int(sPA.w))))]
    e1B = sPB.slotPath[int(MM.slot(JInt(1), JInt(0), JInt(int(sPB.w))))]
    chk(str(e1A) != str(sPA.dark) and str(e1B) == str(sPB.dark),
        "P. chunk 1,0 is in the engine cache but only Ann's stream sent it: Ann sees it, Bob gets the dark fill (never read for him)")
    MM.tap(pB["pr"], upd([(1, 0, imE)]))
    move_to(pB, WPW, 16.0 + 32 * 3, 16.0)
    for _ in range(6):
        due_now()
        MM.tick()
    move_to(pB, WPW, 16.0, 16.0)
    for _ in range(6):
        due_now()
        MM.tick()
    e1B = sPB.slotPath[int(MM.slot(JInt(1), JInt(0), JInt(int(sPB.w))))]
    chk(str(e1B) != str(sPB.dark), "P. once Bob's stream sent chunk 1,0 he gets it")

    # ======================================================================== G: pan / ring buffer for every zoom x size
    reset_mm()
    MC.BM = 1
    MC.MAX_RADIUS = "320"
    use_dir("g1")
    mmG, imgsG = map_manager(True, {})
    WG = make_world("default", mmG)
    pg = player(21, "Walker", WG, 0.5, 0.5)
    MM.hello(pg["pr"])
    sG = MM.SESS.get(pg["pr"].getUuid())
    lay = LS.get(pg["pr"].getUuid()).get("Minimap")
    ANCHOR_RE = re.compile(r'"Left":\s*(-?\d+).*?"Top":\s*(-?\d+)')
    geo_rep = {}
    gbad = []
    ncheck = 0
    for z in RADII:
        for sc in STEPS:
            v = list(MC.dec(""))
            v[0] = z
            lay.mm = MC.enc(JArray(JInt)(v), "def")
            lay.scale = sc
            sG.world = WG
            sG.store = pg["st"]
            sG.wuuid = pg["pr"].getWorldUuid()
            MM.geometry(sG, lay)
            MM.pictures(sG)
            w_, h_, t_, C_, span = int(sG.w), int(sG.h), int(sG.t), int(sG.C), int(sG.span)
            geo_rep["%d/%d" % (z, sc)] = [int(sG.S), C_, t_, w_]
            client = {}

            def apply(b_):
                n_paths = 0
                for c in b_.getCommands():
                    sel = str(c.selector) if c.selector is not None else ""
                    m_ = re.match(r"#SkyyMmT(\d+)\.(Anchor|AssetPath)", sel)
                    if not m_:
                        continue
                    i_ = int(m_.group(1))
                    if m_.group(2) == "Anchor":
                        am = ANCHOR_RE.search(str(c.data))
                        client.setdefault(i_, {})["a"] = (int(am.group(1)), int(am.group(2))) if am else None
                    else:
                        client.setdefault(i_, {})["p"] = True
                        n_paths += 1
                return n_paths
            x, zz = -64.3, -80.7
            b_ = UCB()
            MM.move(sG, b_, JDouble(x), JDouble(zz), JFloat(0.0), JArray(JInt)([0]), JLong(far), True)
            apply(b_)
            path = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
            stepn = 0
            for (dx, dz) in path * 2:
                for _k in range(7):
                    ox, oz = int(MM.chunkOf(JDouble(x))), int(MM.chunkOf(JDouble(zz)))
                    x += dx * 9.7
                    zz += dz * 9.7
                    b_ = UCB()
                    reb0 = int(sG.rebases)
                    MM.move(sG, b_, JDouble(x), JDouble(zz), JFloat(0.0), JArray(JInt)([0]), JLong(far), False)
                    npth = apply(b_)
                    cx, cz = int(MM.chunkOf(JDouble(x))), int(MM.chunkOf(JDouble(zz)))
                    stepn += 1
                    # every window chunk sits in its floorMod slot, anchored at its grid position
                    for ddz in range(-h_, h_ + 1):
                        for ddx in range(-h_, h_ + 1):
                            kx, kz = cx + ddx, cz + ddz
                            sl = (kx % w_) + w_ * (kz % w_)
                            ncheck += 1
                            if int(sG.slotKey[sl]) != int(MM.key(JInt(kx), JInt(kz))):
                                gbad.append(("slot", z, sc, kx, kz))
                            elif client.get(sl, {}).get("a") != ((kx - int(sG.bx)) * t_, (kz - int(sG.bz)) * t_):
                                gbad.append(("anchor", z, sc, kx, kz, client.get(sl), (kx - int(sG.bx)) * t_))
                    # the window covers the clip, the player sits at the clip centre
                    half_blocks = (C_ / 2.0) * 32.0 / t_
                    if not ((cx - h_) * 32 <= x - half_blocks and x + half_blocks <= (cx + h_ + 1) * 32
                            and (cz - h_) * 32 <= zz - half_blocks and zz + half_blocks <= (cz + h_ + 1) * 32):
                        gbad.append(("cover", z, sc, x, zz))
                    centre = int(sG.gl) + (x - int(sG.bx) * 32.0) * t_ / 32.0
                    if abs(centre - C_ / 2.0) > 0.51:
                        gbad.append(("centre", z, sc, centre))
                    # only the entering slots change (unless the grid re-based)
                    moved = (cx, cz) != (ox, oz)
                    if int(sG.rebases) == reb0:
                        want = 0 if not moved else (w_ if (cx == ox or cz == oz) else 2 * w_ - 1)
                        if npth != want:
                            gbad.append(("changed", z, sc, npth, want))
            # teleports (re-base)
            for (tx, tz) in ((5000.5, -7000.5), (-40000.2, 12.0), (0.1, 0.1)):
                b_ = UCB()
                MM.move(sG, b_, JDouble(tx), JDouble(tz), JFloat(0.0), JArray(JInt)([0]), JLong(far), False)
                apply(b_)
                cx, cz = int(MM.chunkOf(JDouble(tx))), int(MM.chunkOf(JDouble(tz)))
                for ddz in range(-h_, h_ + 1):
                    for ddx in range(-h_, h_ + 1):
                        kx, kz = cx + ddx, cz + ddz
                        sl = (kx % w_) + w_ * (kz % w_)
                        if int(sG.slotKey[sl]) != int(MM.key(JInt(kx), JInt(kz))) or client.get(sl, {}).get("a") != ((kx - int(sG.bx)) * t_, (kz - int(sG.bz)) * t_):
                            gbad.append(("teleport", z, sc, kx, kz))
    chk(not gbad, "G. %d slot checks over 6 zooms x 7 sizes, 8-direction walks across 0 (negative chunks) and teleports: %s" % (ncheck, gbad[:4]))
    res["report"]["geometry"] = geo_rep
    MC.MAX_RADIUS = "224"
    lay.mm = ""
    lay.scale = 100

    # document sizes + build time per geometry
    doc_rep = {}
    for z in RADII:
        for sc in (50, 100, 200):
            v = list(MC.dec(""))
            v[0] = z
            lay.mm = MC.enc(JArray(JInt)(v), "def")
            lay.scale = sc
            MC.MAX_RADIUS = "320"
            MM.geometry(sG, lay)
            MM.pictures(sG)
            MM.DOCS.clear()
            t0 = time.perf_counter()
            d_ = MM.doc(sG, Wid.anchorSrcWH(lay, JInt(int(sG.S)), JInt(int(sG.S))))
            ms = (time.perf_counter() - t0) * 1000
            size = int(CHP(JString(KEY), JInt(Z), True, d_.getCommands()).computeSize())
            doc_rep["z%d %d%%" % (z, sc)] = [int(sG.w) ** 2, size, round(ms, 2)]
    res["report"]["docs"] = doc_rep
    chk(all(v[0] <= 529 for v in doc_rep.values()), "U. at most 529 slots in any document: %s" % doc_rep)
    MC.MAX_RADIUS = "224"
    lay.mm = ""
    lay.scale = 100

    # ======================================================================== W: threads, budget, 20 players, errors, watchdog
    reset_mm()
    MC.BM = 1
    use_dir("w1")
    engine = {}
    for cx in range(-30, 31):
        for cz in range(-12, 13):
            engine[(cx, cz)] = engine_image(96, 96, rand_pal(rnd.randrange(4, 300), True), bits=12)[0]
    mmW, imgsW = map_manager(True, engine)
    WW = make_world("default", mmW)
    ps20 = []
    for i in range(20):
        o = player(100 + i, "P%02d" % i, WW, -800.5 + 13 * i, -100.5 + 7 * i)
        ps20.append(o)
        MM.hello(o["pr"])
        burst = upd([(cx, cz, engine[(cx, cz)]) for (cx, cz) in engine])
        MM.tap(o["pr"], burst)
        MM.ready(o["pr"], o["st"])
    MM.tick()
    run_world(WW)
    tick_ms = []
    rt = JClass("java.lang.Runtime").getRuntime()
    for step in range(120):
        for i, o in enumerate(ps20):
            speed = 40.0 if i == 0 else 1.4            # player 0 flies (a chunk every tick), the others walk
            move_to(o, WW, -800.5 + 13 * i + speed * step, -100.5 + 7 * i)
        t0 = time.perf_counter()
        MM.tick()
        tick_ms.append((time.perf_counter() - t0) * 1000)
    tw = [w_.tasks for w_ in (WW,) if w_.tasks is not None and int(w_.tasks.size()) > 0]
    enc_per = [int(MM.SESS.get(o["pr"].getUuid()).encodes) for o in ps20]
    fills = sum(1 for o in ps20 if bool(MM.SESS.get(o["pr"].getUuid()).fillLogged))
    chk(not tw, "W. 120 ticks x 20 players: no task queued on the world thread (no HudManager call, no map work there)")
    chk(min(enc_per[1:]) > 0 and fills == 20, "W. round-robin: every walker got pieces encoded although player 0 flies (encodes %s, %d / 20 filled)" % (enc_per[:5], fills))
    srt = sorted(tick_ms[3:])
    res["report"]["tick_ms_20p"] = {"median": round(srt[len(srt) // 2], 2), "p95": round(srt[int(len(srt) * 0.95)], 2), "max": round(srt[-1], 2),
                                    "first3": [round(x, 2) for x in tick_ms[:3]]}
    chk(srt[int(len(srt) * 0.95)] < 13.0, "W. 20 players walking: 95 %% of the ticks take < 13 ms (FIX: the encode budget grows to 10 ms while "
        "several fill + pans): p95 %.2f ms" % srt[int(len(srt) * 0.95)])
    held = sum(1 for o in ps20 for v in MM.SESS.get(o["pr"].getUuid()).known.values() if isinstance(v, MIMc))
    chk(held <= 20 * 4 and all(isinstance(v, JClass(PKG + "MmAsset")) for v in MM.CACHE.values()),
        "W. after the walk: MapImages held only for pieces still waiting (%d), the cache holds pictures only" % held)
    JClass("java.lang.System").gc()
    used = (int(rt.totalMemory()) - int(rt.freeMemory())) / 1048576.0
    res["report"]["heap_mb_after_20p"] = round(used, 1)
    cache_bytes = sum(len(pyb(v.bytes)) for v in MM.CACHE.values())
    chk(cache_bytes < 30 * 1048576, "W. retained by the shared cache after 20 players walked: %.1f MB (< 30 MB)" % (cache_bytes / 1048576.0))
    # the tick inside the budget: the per-tick encode work is bounded by 3 ms (+ pans); the harness measures through jpype (slower)
    enc_ms = (float(MM.ENC_NS) / max(1, int(MM.ENC_N))) / 1e6
    res["report"]["encode_ms_per_piece"] = round(enc_ms, 3)
    chk(enc_ms < 1.0, "W. one 96 -> 16 px piece encodes in %.3f ms (bench ~0.08)" % enc_ms)
    # a throwing player does not stop the others
    bad_o = ps20[3]
    field(PRc, "transform").set(bad_o["pr"], None)
    sBad = MM.SESS.get(bad_o["pr"].getUuid())
    field(MS, "slotKey").set(sBad, None)
    sBad.more = True
    e0 = int(MM.ERRORS)
    upd_before = [int(MM.SESS.get(o["pr"].getUuid()).updates) for o in ps20]
    for step in range(4):
        for o in ps20:
            MM.SESS.get(o["pr"].getUuid()).nextPanAt = 0
        for i, o in enumerate(ps20):
            if o is not bad_o:
                move_to(o, WW, -800.5 + 13 * i + 1.4 * (120 + step) + 33, -100.5 + 7 * i)
        field(PRc, "transform").set(bad_o["pr"], Transform(JDouble(1.0), JDouble(1.0), JDouble(1.0)))
        MM.tick()
    upd_after = [int(MM.SESS.get(o["pr"].getUuid()).updates) for o in ps20]
    moved_on = sum(1 for i in range(20) if i != 3 and upd_after[i] > upd_before[i])
    chk(int(MM.ERRORS) > e0 and moved_on >= 18, "W. one throwing player: the error is counted (%d), the 19 others still updated (%d)" % (int(MM.ERRORS) - e0, moved_on))
    chk(len([l_ for l_ in tail() if "a player's minimap failed" in l_]) == 1, "W. ... and logged ONCE")
    # the real executor: the tick runs on SkyyHud-Minimap
    MM.EXEC = None
    MM.LAST_THREAD = None
    MM.ensureExec()
    t_end = time.time() + 3.0
    while time.time() < t_end and (MM.LAST_THREAD is None or int(MM.TICKS) < 3):
        time.sleep(0.05)
    chk(str(MM.LAST_THREAD) == "SkyyHud-Minimap" and MM.EXEC is not parked, "W. the tick runs on its OWN thread %s (not the shared scheduler)" % MM.LAST_THREAD)
    fut = MM.FUT
    chk("scheduleWithFixedDelay" in "scheduleWithFixedDelay" and fut is not None and not bool(fut.isDone()), "W. scheduled with fixed delay, running")
    # 500 pieces on that thread
    JRunnable = JClass("java.lang.Runnable")

    @JImplements("java.lang.Runnable")
    class Bench(object):
        def __init__(self):
            self.ms = None
            self.thread = None

        @JOverride
        def run(self):
            imgs = list(engine.values())[:500]
            t0 = System.nanoTime()
            for im in imgs:
                MP.tilePng(im, JInt(16))
            self.ms = (int(System.nanoTime()) - int(t0)) / 1e6
            self.thread = str(JClass("java.lang.Thread").currentThread().getName())
    bench = Bench()
    MM.EXEC.submit(bench).get()
    res["report"]["bench_500_ms"] = round(bench.ms, 1)
    chk(bench.thread == "SkyyHud-Minimap" and bench.ms < 1000, "W. 500 pieces 96 -> 16 px on SkyyHud-Minimap: %.1f ms" % bench.ms)
    # watchdog: a tick that stopped -> a new thread, logged once
    MM.TAIL.clear()
    old_exec = MM.EXEC
    MM.LAST_TICK = int(System.currentTimeMillis()) - 6000
    old_exec.shutdownNow()
    MM.watchdog()
    t_end = time.time() + 2.0
    while time.time() < t_end and int(System.currentTimeMillis()) - int(MM.LAST_TICK) > 1000:
        time.sleep(0.05)
    chk(MM.EXEC is not old_exec and MM.EXEC is not None and any("stopped ticking" in l_ for l_ in tail()),
        "W. watchdog: a dead minimap thread is replaced (one log line) and ticks again")
    ex_ = MM.EXEC
    MM.EXEC = parked
    ex_.shutdownNow()

    # ======================================================================== U: removal, no-stream, disabled worlds, map off
    reset_mm()
    MC.BM = 1
    use_dir("u2")
    mmN, imgsN = map_manager(True, {})
    WN = make_world("skywynn_z1", mmN)
    pn = player(31, "Nia", WN, 0.5, 0.5)
    MM.hello(pn["pr"])
    MM.ready(pn["pr"], pn["st"])
    MM.tick()
    sN = MM.SESS.get(pn["pr"].getUuid())
    chk((WN.tasks is None or int(WN.tasks.size()) == 0) and sN.hud is None and bool(sN.pending),
        "B. FIX: a world with the map on but no map stream yet (islands, P5): NO attach - no empty disc - the session waits")
    sN.pendingSince = int(System.currentTimeMillis()) - 16000
    MM.TAIL.clear()
    MM.tick()
    MM.tick()
    chk(sN.hud is None and tail() == ["minimap: no map stream in world 'skywynn_z1' - not shown there (it shows once a map packet comes)"],
        "B. ... 15 s without a packet: ONE line, still nothing shown: %s" % tail())
    MM.tap(pn["pr"], upd([(0, 0, engine_image(16, 16, rand_pal(3, False))[0])]))
    MM.tick()
    q_ = [str(t_.getClass().getSimpleName()) for t_ in (WN.tasks or [])]
    run_world(WN)
    chk(q_ == ["MmAttach"] and pn["hm"].getCustomHud(KEY) is not None and not bool(sN.pending),
        "B. ... the first map packet: the minimap attaches (%s)" % q_)
    MM.tap(pn["pr"], CWMc())
    MM.tick()
    sN.attachAt = int(System.currentTimeMillis()) - 16000
    MM.tick()
    run_world(WN)
    chk(sN.hud is None and pn["hm"].getCustomHud(KEY) is None and bool(sN.pending),
        "B. the map cleared and no packet for 15 s after the attach: hidden (removeCustomHud), waiting for the next packet")
    mmOff, _x = map_manager(False, {})
    WOff = make_world("skyy-island-abc", mmOff)
    move_to(pn, WOff, 0.5, 0.5)
    MM.ready(pn["pr"], pn["st"])
    MM.tick()
    chk(WOff.tasks is None and sN.hud is None, "B. a world with the map OFF (island): no attach")
    MC.DISABLED_WORLDS = "dungeon*, arena"
    WD = make_world("Dungeon_Crypt_7", mmA)
    move_to(pn, WD, 0.5, 0.5)
    MM.ready(pn["pr"], pn["st"])
    MM.tick()
    chk(WD.tasks is None and bool(MC.worldDisabled("ARENA")) and not bool(MC.worldDisabled("arena2")), "B. hud.mm.disabledWorlds 'dungeon*, arena': no attach there")
    MC.DISABLED_WORLDS = ""
    # removeCustomHud only for OUR hud
    other = MH(pn["pr"], sN, UCB())
    move_to(pn, WA, 0.5, 0.5)
    hmN = pn["hm"]
    MM.detachNow(pn["pr"], pn["st"], other)
    chk(True, "U. detachNow with a HUD that is not the registered one does nothing")

    # ======================================================================== L: layout round trips
    reset_mm()
    use_dir("l1")
    me = player(41, "Lou", WA)
    u = me["pr"].getUuid()
    m_ = LS.get(u)
    l_ = m_.get("Minimap")
    chk(l_ is not None and str(l_.anchor) == "tr" and int(l_.dx) == 8 and int(l_.dy) == 40 and int(l_.bw) == 160 and int(l_.lines) == 3 and str(l_.mm) == "",
        "L. the built-in Minimap: tr 8,40, 160 px box, markers 3, mm ''")
    chk(str(l_.ser()) == "1,tr,8,40,100,1", "L. a default Minimap line = the 6 classic fields: %s" % l_.ser())
    l_.mm = MC.enc(JArray(JInt)([224, 1, 250, 0, 2]), "aqua")
    l_.lines = 5
    l_.col = "gold"
    line = str(l_.ser())
    chk(line == "1,tr,8,40,100,1,gold,1,0,0,def,1,5,def,z224.sq.u250.g0.k2.caqua", "L. with settings: the 15th field: %s" % line)
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    p2 = WL.parse(line, wdef("Minimap"))
    chk(str(p2.ser()) == line and str(p2.mm) == "z224.sq.u250.g0.k2.caqua", "L. parse(ser) round trip")
    p3 = WL.parse("1,tr,8,40,100,1,def,1,0,0,def,1,-,def,zXX.s?.u777.g9.k5.cnope", wdef("Minimap"))
    chk(str(p3.mm) == "", "L. a bad 15th field -> its defaults one by one (here all default -> '')")
    LS.save(u)
    props = open(os.path.join(work, "l1", "layouts", str(u) + ".properties"), encoding="latin-1").read()
    chk("Minimap=1,tr,8,40,100,1,gold,1,0,0,def,1,5,def,z224.sq.u250.g0.k2.caqua" in props, "L. the saved file carries the line")
    res["scen"]["layout_file"] = props
    code = str(LS.export(u))
    chk("Minimap=1:tr:8:40:100:1:gold:1:0:0:def:1:5:def:z224.sq.u250.g0.k2.caqua" in code, "L. the export code (':')")
    LS.CACHE.clear()
    n_imp = int(LS.importCode(u, code))
    chk(n_imp == 13 and str(LS.get(u).get("Minimap").ser()) == line, "L. import of the code: 13 widgets, the Minimap line intact")
    chk(bool(LS.profileSave(u, "mm")) and int(LS.profileLoad(u, "mm")) == 13, "L. profiles save / load")
    for sc_in, sc_out in ((60, 50), (62, 50), (63, 75), (110, 100), (113, 125), (190, 200), (240, 200), (10, 50)):
        lx = LS.get(u).get("Minimap")
        lx.scale = sc_in
        Wid.clampToScreen(lx)
        chk(int(lx.scale) == sc_out, "L. size %d%% snaps to %d%% (7 steps)" % (sc_in, sc_out))
    other_l = LS.get(u).get("Gclock")
    other_l.scale = 110
    Wid.clampToScreen(other_l)
    chk(int(other_l.scale) == 110 and other_l.mm is None, "L. other widgets keep their sizes (no snapping), mm null")
    LS.reset(u)
    chk(str(LS.get(u).get("Minimap").ser()) == "1,tr,8,40,100,1", "L. /skyyhud reset: the default Minimap")
    MC.DEFAULT_ON = False
    LS.CACHE.clear()
    use_dir("l2")
    chk(not bool(LS.get(u).get("Minimap").en), "L. hud.mm.defaultOn off: a new player starts with the Minimap hidden")
    MC.DEFAULT_ON = True
    # editor: Size- / Size+ move the Minimap 25 %
    use_dir("l3")
    ep = EP(me["pr"], U.allocateInstance(Plugin.class_))
    field(Plugin, "huds").set(ep.plugin, CHM())
    ep.sel = "Minimap"
    ep.handleDataEvent(None, None, '{"a":"act:Sp"}')
    chk(int(LS.get(u).get("Minimap").scale) == 125, "L. editor Size+ on the Minimap: 100 -> 125")
    ep.handleDataEvent(None, None, '{"a":"act:Sm"}')
    ep.handleDataEvent(None, None, '{"a":"act:Sm"}')
    chk(int(LS.get(u).get("Minimap").scale) == 75, "L. editor Size- twice: 125 -> 75")
    ep.sel = "Gclock"
    ep.handleDataEvent(None, None, '{"a":"act:Sp"}')
    chk(int(LS.get(u).get("Gclock").scale) == 110, "L. other widgets still step 10")
    # the editor page shows a Minimap box
    b_, ev_ = UCB(), UEB()
    ep.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    chk(any(c[3] and "Group #SkyyEPvMinimap " in c[3] for c in cm) and any(c[2] and '"Minimap"' in c[2] for c in cm if c[0] == "Set"),
        "L. the editor draws the Minimap box (stand-in text 'Minimap')")
    # the server default layout may carry the Minimap
    Cfg.DEFAULT_LAYOUT = "Minimap=1:bl:8:8:150:1;Coords=1:tl:8:8:100:1"
    Cfg.PARSED = None
    LS.CACHE.clear()
    use_dir("l4")
    lm = LS.get(u).get("Minimap")
    chk(str(lm.anchor) == "bl" and int(lm.scale) == 150 and str(lm.mm) == "", "L. the server default layout's Minimap entry is used")
    chk(Cfg.codeError("Minimap=1:tr:8:40:100:1") is None, "L. hud.defaultLayout accepts a Minimap entry")
    Cfg.DEFAULT_LAYOUT = ""
    Cfg.PARSED = None
    res["scen"]["line_for_old"] = line

    # ======================================================================== S: the settings page
    use_dir("s1")
    MC.BM = 1
    MC.BMV = "1.3.8"
    sp_ = SP(me["pr"], ep.plugin, "Minimap")
    b_, ev_ = UCB(), UEB()
    sp_.build(None, b_, ev_, None)
    cm = [as4(c) for c in b_.getCommands()]
    evs = [(str(e.selector), str(e.data)) for e in ev_.getEvents()]
    aps = [c for c in cm if c[0] == "AppendInline"]
    bad_mk = []
    for c in aps:
        try:
            SUI.check_markup(c[3], root=c[1] is None)
        except Exception as ex:
            bad_mk.append(str(ex)[:100])
    try:
        SUI.assert_proven([c[3] for c in aps], what="settings as sent")
        prov = True
    except Exception as ex:
        prov = str(ex)[:200]
    chk(not bad_mk and prov is True, "S. the settings page as sent: kit markup checks + every token proven: %s %s" % (bad_mk[:2], prov))
    zb = [s_ for s_, d_ in evs if s_.startswith("#SkyyMmSZ")]
    chk(zb == ["#SkyyMmSZ64", "#SkyyMmSZ96", "#SkyyMmSZ128", "#SkyyMmSZ160", "#SkyyMmSZ224"], "S. zoom buttons up to the admin max 224: %s" % zb)
    chk(len(evs) >= 40 and any('"mm:back"' in d_ for s_, d_ in evs), "S. %d bindings incl. Back" % len(evs))
    sets_ = dict((c[1], c[2]) for c in cm if c[0] == "Set")
    chk(any("1.3.8 found" in (v or "") for v in sets_.values()), "S. the BetterMap line says 1.3.8 found")
    res["scen"]["settings_cmds"] = len(cm)

    def click(payload):
        return int(MU.click(me["pr"], '{"a":"%s"}' % payload))
    lm = LS.get(u).get("Minimap")
    chk(click("mm:z:320") == 0 and list(MC.dec(lm.mm))[0] == 160, "S. zoom 320 above the admin max is refused")
    chk(click("mm:z:96") == 2 and list(MC.dec(lm.mm))[0] == 96, "S. zoom 96")
    chk(click("mm:s:1") == 2 and list(MC.dec(lm.mm))[1] == 1, "S. square")
    chk(click("mm:u:1000") == 2 and list(MC.dec(lm.mm))[2] == 1000, "S. update Saver")
    chk(click("mm:g:0") == 2 and list(MC.dec(lm.mm))[3] == 0, "S. ring off")
    chk(click("mm:ms:2") == 2 and list(MC.dec(lm.mm))[4] == 2, "S. marker size large")
    chk(click("mm:mk:4:1") == 2 and int(lm.lines) == 7, "S. other players on (markers 7)")
    chk(click("mm:mk:1:0") == 2 and int(lm.lines) == 6, "S. party off (markers 6)")
    chk(click("mm:rc:aqua") == 2 and str(lm.col) == "aqua" and click("mm:rc:black") == 0, "S. ring colour aqua; black (glow-only) refused")
    chk(click("mm:pc:pink") == 2 and str(MC.pcol(lm.mm)) == "pink", "S. party dot colour pink")
    chk(click("mm:sz:150") == 2 and int(lm.scale) == 150, "S. size 150")
    chk(click("mm:en:0") == 2 and not bool(lm.en), "S. show off")
    saved = open(os.path.join(work, "s1", "layouts", str(u) + ".properties"), encoding="latin-1").read()
    chk("Minimap=0,tr,8,40,150,1,aqua,1,0,0,def,1,6,def,z96.sq.u1000.g0.k2.cpink" in saved, "S. every click saved: %s" % [l for l in saved.splitlines() if l.startswith("Minimap")])
    chk(click("mm:reset") == 2 and str(lm.mm) == "" and int(lm.lines) == 3 and str(lm.col) == "def" and int(lm.scale) == 100, "S. Reset")
    chk(click("mm:back") == 1 and click("garbage") == 0 and int(MU.click(me["pr"], None)) == 0, "S. Back = 1, garbage = 0")
    res["scen"]["settings_evs"] = len(evs)

    # ======================================================================== K: config
    use_dir("k1")
    kdir = os.path.join(work, "k1")
    f_ = os.path.join(kdir, "config.properties")
    open(f_, "w", encoding="latin-1").write("# old 0.3.13 file\ndefaultLayout=\n")
    before = open(f_, "rb").read()
    Cfg.FILE = Paths.get(f_)
    MC.MAX_RADIUS = "320"
    MC.ENABLED = False
    Cfg.load()
    chk(open(f_, "rb").read() == before and bool(MC.ENABLED) and str(MC.MAX_RADIUS) == "224" and str(MC.DETAIL) == "32"
        and abs(float(MC.MIN_INTERVAL) - 0.25) < 1e-9 and int(MC.TILES_PER_TICK) == 24,
        "K. a 0.3.13 file without mm.* keys: the defaults (FIX: sharpest detail 32, fastest update 0.25 s), the file untouched")
    open(f_, "w", encoding="latin-1").write("defaultLayout=\nmm.enabled=0\nmm.maxRadius=320\nmm.detail=24\nmm.minInterval=0.25\nmm.tilesPerTick=64\n"
                                            "mm.partyDots=off\nmm.otherPlayers=false\nmm.disabledWorlds=a, b*\n")
    Cfg.load()
    chk(not bool(MC.ENABLED) and str(MC.MAX_RADIUS) == "320" and int(MC.detail()) == 24 and int(MC.minIntervalMs()) == 250
        and int(MC.tilesPerTick()) == 64 and not bool(MC.PARTY_DOTS) and not bool(MC.OTHER_PLAYERS) and str(MC.DISABLED_WORLDS) == "a, b*",
        "K. every mm.* key read")
    open(f_, "w", encoding="latin-1").write("defaultLayout=\nmm.maxRadius=100\nmm.detail=12\nmm.minInterval=0.1\nmm.tilesPerTick=0\nmm.enabled=maybe\n")
    Cfg.load()
    chk(str(MC.MAX_RADIUS) == "224" and int(MC.detail()) == 32 and abs(float(MC.MIN_INTERVAL) - 0.25) < 1e-9 and int(MC.TILES_PER_TICK) == 24 and bool(MC.ENABLED),
        "K. hand-edited bad values -> the defaults")
    kmods = os.path.join(kdir, "mods")
    os.makedirs(os.path.join(kmods, "Skyy_SkyyHud"))
    f_ = os.path.join(kmods, "Skyy_SkyyHud", "config.properties")
    open(f_, "w", encoding="latin-1").write("# a 0.3.13 file\ndefaultLayout=\n")
    Cfg.FILE = Paths.get(f_)
    Cfg.load()
    Pub = JClass(PKG + "CfgPub")
    Pub.start(Paths.get(kmods), None)
    Fn = JClass(PKG + "CfgFn")
    rows = [str(r_[0]) for r_ in JClass(PKG + "CfgRows").rows()] if hasattr(JClass(PKG + "CfgRows"), "rows") else []
    res["report"]["cfg_rows"] = rows
    want_rows = ["hud.mm.enabled", "hud.mm.defaultOn", "hud.mm.maxRadius", "hud.mm.detail", "hud.mm.minInterval", "hud.mm.tilesPerTick",
                 "hud.mm.partyDots", "hud.mm.otherPlayers", "hud.mm.disabledWorlds"]
    chk(not rows or all(w in rows for w in want_rows), "K. the 9 Minimap rows are published: %s" % [w for w in want_rows if w not in rows])
    for key_, val_, ok_ in (("hud.mm.maxRadius", "320", True), ("hud.mm.maxRadius", "100", False), ("hud.mm.tilesPerTick", "0", False),
                            ("hud.mm.tilesPerTick", "64", True), ("hud.mm.minInterval", "0.1", False), ("hud.mm.minInterval", "1", True),
                            ("hud.mm.detail", "24", True), ("hud.mm.enabled", "false", True)):
        try:
            r_ = Fn.set(key_, val_, None, "Console", "yes", "console")
            got = str(r_[0]) if r_ is not None else None
        except Exception as ex:
            got = "threw %s" % ex
        chk((got == "ok") == ok_, "K. the kit %s %s = %s (%s)" % ("takes" if ok_ else "refuses", key_, val_, got))
    chk(str(MC.MAX_RADIUS) == "320" and int(MC.TILES_PER_TICK) == 64 and abs(float(MC.MIN_INTERVAL) - 1.0) < 1e-9 and not bool(MC.ENABLED),
        "K. the kit wrote the bound fields")
    chk(bool(MM.RELAYOUT), "K. a row with after=Minimap.cfgChanged re-lays the minimaps out")
    Pub.flush()
    ktext = open(f_, encoding="latin-1").read()
    chk("mm.maxRadius=320" in ktext and "mm.tilesPerTick=64" in ktext and "mm.enabled=false" in ktext and "defaultLayout=" in ktext,
        "K. the kit wrote the changed keys into config.properties (old lines kept): %s" % [l for l in ktext.splitlines() if l.startswith("mm.")])
    MC.ENABLED = True
    MC.MAX_RADIUS = "224"
    MC.TILES_PER_TICK = 24
    MC.MIN_INTERVAL = 0.25
    MC.DETAIL = "32"


    # ======================================================================== X: the FIX ROUND (critic reports on the first build)
    reset_mm()
    MC.BM = 1
    MC.ENABLED = True
    MC.MIN_INTERVAL = 0.25
    MC.DETAIL = "32"
    MC.MAX_RADIUS = "224"
    use_dir("x1")
    xeng = {}
    for cx in range(-14, 15):
        for cz in range(-14, 15):
            xeng[(cx, cz)] = engine_image(96, 96, rand_pal(rnd.randrange(2, 60), True), bits=12)[0]
    mmX, imgsX = map_manager(True, xeng)
    WX = make_world("default", mmX)

    def x_join(n, name, x=16.0, z=16.0, stream=True):
        o = player(n, name, WX, x, z)
        MM.hello(o["pr"])
        if stream:
            MM.tap(o["pr"], upd([(cx, cz, xeng[(cx, cz)]) for (cx, cz) in xeng]))
        MM.ready(o["pr"], o["st"])
        MM.tick()
        run_world(WX)
        s_ = MM.SESS.get(o["pr"].getUuid())
        for _ in range(60):
            MM.tick()
            if s_.hud is not None and bool(s_.fillLogged):
                break
        return o, s_

    def tasks(w):
        return [str(t_.getClass().getSimpleName()) for t_ in (w.tasks or [])]

    def pushes(o, i0):
        return [[as4(c) for c in p_.commands] for p_ in huds(sent(o, i0)) if not bool(p_.clear)]

    def fulls(o, i0):
        return [p_ for p_ in huds(sent(o, i0)) if bool(p_.clear)]

    def settle(s_):
        s_.nextPanAt = int(System.currentTimeMillis()) + 10 ** 7
        s_.nextPartyAt = int(System.currentTimeMillis()) + 10 ** 7
        s_.markersDirty = False
        s_.more = False

    px_, sX = x_join(201, "Xena")
    ux = px_["pr"].getUuid()
    layX = LS.get(ux).get("Minimap")
    chk(sX.hud is not None and bool(sX.hud.attached) and bool(sX.fillLogged), "X. setup: Xena's minimap attached and filled")

    # 1. a layout change re-attaches only for a new frame (critic: every editor / settings click re-sent the whole minimap)
    settle(sX)
    i0 = mark(px_)
    MM.relayout(ux)
    MM.tick()
    LS.get(ux).get("Gclock").dx = 77
    MM.relayout(ux)
    MM.tick()
    chk(tasks(WX) == [] and not fulls(px_, i0) and not pushes(px_, i0),
        "X1. relayout with the minimap unchanged (an editor click on Gclock): no new HUD, no MmAttach, nothing sent")
    layX.dy = 60
    MM.relayout(ux)
    MM.tick()
    ps_ = pushes(px_, i0)
    flat = [c for p_ in ps_ for c in p_]
    chk(tasks(WX) == [] and not fulls(px_, i0) and len(ps_) == 1 and [c[1] for c in flat] == ["#SkyyMmBox.Anchor"]
        and '"Right"' in str(flat[0][2]) and "60" in str(flat[0][2]),
        "X1. the minimap moved in the editor: ONE update = the box Anchor only (no new document): %s" % [c[:3] for c in flat][:3])
    i1 = mark(px_)
    layX.col = "aqua"
    MM.relayout(ux)
    MM.tick()
    flat = [c for p_ in pushes(px_, i1) for c in p_]
    chk(tasks(WX) == [] and not fulls(px_, i1) and [c[1] for c in flat] == ["#SkyyMmRing.AssetPath"] and str(sX.ringPath) in str(flat[0][2]),
        "X1. ring colour: ONE update = the ring picture (sent once), no re-attach: %s" % [c[1] for c in flat])
    v = list(MC.dec(layX.mm))
    v[2] = 1000
    layX.mm = MC.enc(JArray(JInt)(v), MC.pcol(layX.mm))
    MM.relayout(ux)
    MM.tick()
    chk(tasks(WX) == [] and int(sX.upd) == 1000 and not fulls(px_, i1), "X1. update speed Saver: the session takes 1 s, no re-attach")
    v[2] = 250
    layX.mm = MC.enc(JArray(JInt)(v), MC.pcol(layX.mm))
    MM.relayout(ux)
    MM.tick()
    chk(int(sX.upd) == 250, "X3. FIX: Smooth = 0.25 s with the default fastest update (it was clamped to 0.5 s)")
    v[0] = 96
    layX.mm = MC.enc(JArray(JInt)(v), MC.pcol(layX.mm))
    MM.relayout(ux)
    MM.tick()
    chk(tasks(WX) == ["MmAttach"], "X1. a new zoom = a new frame: re-attached (%s)" % tasks(WX))
    run_world(WX)
    for _ in range(30):
        MM.tick()
    # 4. detail per session (critic: blurry at most zoom / size combinations with 16 px pieces)
    chk(int(sX.t) == 25 and int(sX.det) == 32 and str(sX.dsuf) == "/32",
        "X4. FIX zoom 96 at 100 %%: tile %d px on screen -> pieces encoded at %d px (not 16)" % (int(sX.t), int(sX.det)))
    real32 = [str(MM.CACHE.get(sX.known.get(JLong(int(MM.key(JInt(cx), JInt(cz)))))) is not None) for cx in (0, 1) for cz in (0, 1)]
    keys32 = [str(sX.known.get(JLong(int(MM.key(JInt(cx), JInt(cz)))))) for cx in (0, 1) for cz in (0, 1)]
    chk(all(k_.endswith("/32") for k_ in keys32), "X4. ... the window's content keys are at /32: %s" % keys32[:2])
    detf = [(t_, int(MC.detFor(JInt(t_)))) for t_ in (8, 15, 16, 17, 19, 24, 25, 38, 76)]
    chk(detf == [(8, 16), (15, 16), (16, 16), (17, 24), (19, 24), (24, 24), (25, 32), (38, 32), (76, 32)], "X4. detFor: %s" % detf)
    MC.DETAIL = "16"
    chk(int(MC.detFor(JInt(38))) == 16, "X4. the admin's sharpest detail 16 caps it")
    MC.DETAIL = "32"
    kk = JLong(int(MM.key(JInt(0), JInt(0))))
    sX.known.put(kk, JString("96x96b12p9n0c0/16"))
    a16 = MM.resolve(sX, JInt(0), JInt(0), JArray(JInt)([5]), JLong(System.nanoTime() + 10 ** 10), False)
    chk(a16 is not None and str(sX.known.get(kk)).endswith("/32"), "X4. a piece keyed at another detail is resolved again at the session's")
    v[0] = 160
    layX.mm = MC.enc(JArray(JInt)(v), MC.pcol(layX.mm))
    MM.relayout(ux)
    MM.tick()
    run_world(WX)
    for _ in range(30):
        MM.tick()

    # 5. update rate: marker changes / leftovers wait; the arrow alone follows a turn at once
    settle(sX)
    i2 = mark(px_)
    sX.markersDirty = True
    MM.tick()
    MM.tick()
    chk(not pushes(px_, i2), "X5. FIX: a marker change waits for the player's update time (no push before nextPanAt)")
    move_to(px_, WX, 16.0, 16.0, math.pi / 2)
    MM.tick()
    flat = [c for p_ in pushes(px_, i2) for c in p_]
    chk([c[1] for c in flat] == ["#SkyyMmArrow.AssetPath"] and str(sX.arrows[12]) in str(flat[0][2]),
        "X3/X5. FIX: turning on the spot sends the arrow alone at once (heading 12 = west): %s" % [c[1] for c in flat])
    sX.nextPanAt = 0
    MM.tick()
    chk(not bool(sX.markersDirty), "X5. ... the marker change goes out with the next update")

    # 2. party dots pinned to the rim are re-pinned at every pan
    @JImplements("java.util.function.Function")
    class Members(object):
        def __init__(self, ids):
            self.ids = ids

        @JOverride
        def apply(self, u):
            return JArray(JString)(self.ids)
    far_o = player(202, "Faye", WX, 16.0 + 2000.0, 16.0)
    bridge.put("party:fn:members", Members([str(ux), str(far_o["pr"].getUuid())]))
    MC.PARTY_DOTS = True
    move_to(px_, WX, 16.0, 16.0, math.pi / 2)
    sX.nextPartyAt = 0
    sX.nextPanAt = 0
    MM.tick()
    chk(bool(sX.ptRim[0]) and int(sX.ptX[0]) != -4000, "X2. a far party member: dot 0 on the rim")
    x0 = int(sX.ptX[0])
    sX.nextPartyAt = int(System.currentTimeMillis()) + 10 ** 7
    i3 = mark(px_)
    move_to(px_, WX, 16.0, 16.0 - 9.0, math.pi / 2)
    sX.nextPanAt = 0
    MM.tick()
    flat = [c for p_ in pushes(px_, i3) for c in p_]
    sel = [c[1] for c in flat]
    chk("#SkyyMmGrid.Anchor" in sel and "#SkyyMmPt0.Anchor" in sel,
        "X2. FIX: a pan (party update not due) re-pins the rim dot in the same update: %s" % sel)
    bridge.remove("party:fn:members")

    # 6. off, then on later: the map fills (the tap kept the keys while it was off) and stays
    oo, sO = x_join(203, "Otto")
    layO = LS.get(oo["pr"].getUuid()).get("Minimap")
    layO.en = False
    MM.relayout(oo["pr"].getUuid())
    MM.tick()
    run_world(WX)
    chk(sO.hud is None and not bool(sO.wants) and oo["hm"].getCustomHud(KEY) is None, "X6. minimap off: hidden")
    MM.tap(oo["pr"], CWMc())
    MM.tap(oo["pr"], upd([(cx, cz, xeng[(cx, cz)]) for (cx, cz) in xeng]))
    MM.tick()
    held = sum(1 for v_ in sO.known.values() if isinstance(v_, MIMc))
    chk(int(sO.streamed.size()) == len(xeng) and held == 0,
        "X6. FIX: while off the tap still records the stream's KEYS (%d), no piece held (%d)" % (int(sO.streamed.size()), held))
    layO.en = True
    MM.relayout(oo["pr"].getUuid())
    MM.tick()
    run_world(WX)
    for _ in range(40):
        MM.tick()
    realO = sum(1 for p_ in sO.slotPath if p_ is not None and str(p_) != str(sO.dark))
    sO.attachAt = int(System.currentTimeMillis()) - 20000
    MM.tick()
    chk(sO.hud is not None and realO == int(sO.w) ** 2,
        "X6. FIX: switched on again: the map fills from the engine cache (%d / %d) and is NOT hidden after 15 s" % (realO, int(sO.w) ** 2))

    # 7. the admin switch turned on at runtime: sessions exist, the minimap shows at once
    MC.ENABLED = False
    ro, sR = x_join(204, "Rae")
    chk(sR is not None and sR.hud is None and int(MM.TAPS) == int(MM.SESS.size()), "X7. FIX: admin switch off at the join: the session and the tap still exist")
    MC.ENABLED = True
    MM.cfgChanged("hud.mm.enabled")
    MM.tick()
    nat = tasks(WX).count("MmAttach")
    run_world(WX)
    chk(nat == 3 and sR.hud is not None and ro["hm"].getCustomHud(KEY) is not None,
        "X7. ... switched on in Server Setup: every minimap (Rae's too, who joined while it was off) attaches without a relog (%d)" % nat)

    # 8. a fast reconnect (the old connection's quit handled after the new connect)
    fo, sF = x_join(205, "Finn")
    old_pr = fo["pr"]
    MM.quit(old_pr)
    fo2 = player(205, "Finn", WX, 16.0, 16.0)
    MM.hello(fo2["pr"])
    MM.tap(old_pr, upd([(0, 0, xeng[(0, 0)])]))
    MM.tap(fo2["pr"], upd([(0, 0, xeng[(0, 0)])]))
    sF2 = MM.SESS.get(fo2["pr"].getUuid())
    MM.ready(fo2["pr"], fo2["st"])
    MM.tick()
    sF2b = MM.SESS.get(fo2["pr"].getUuid())
    run_world(WX)
    for _ in range(10):
        MM.tick()
    a2 = assets_in(sent(fo2, 0))
    chk(sF2 != sF and sF2b == sF2 and sF2b.pr == fo2["pr"] and sF.pr == old_pr and int(sF2b.packets) == 1,
        "X8. FIX: the new connection got a NEW session; the old connection's queued quit did not drop it; the old connection's late packet "
        "went nowhere (%d packets)" % int(sF2b.packets))
    chk(sum(1 for a in a2 if a.startswith("UI/Custom/SkyyHudMmMask-")) == 14 and sF2b.hud is not None,
        "X8. ... the new client gets every picture again (its own list) and its minimap")

    # 9. the watchdog: a tick stuck inside the lock is not doubled; a dead thread is restarted at most 3 times
    MM.tick()
    chk(not bool(MM.IN_TICK) and int(System.currentTimeMillis()) - int(MM.LAST_TICK) < 2000, "X9. a finished tick clears IN_TICK")
    MM.TAIL.clear()
    MM.EXEC = parked
    MM.IN_TICK = True
    MM.TICK_START = int(System.currentTimeMillis()) - 6000
    MM.TICK_THREAD = JClass("java.lang.Thread")()
    MM.watchdog()
    MM.watchdog()
    stuck = [l_ for l_ in tail() if "stuck" in l_]
    chk(MM.EXEC == parked and len(stuck) == 1, "X9. FIX: a tick stuck 6 s INSIDE the lock: no second thread, ONE line: %s" % stuck)
    MM.IN_TICK = False
    MM.RESTARTS = 0
    MM.WD_LOGGED = False
    made = []
    for k_ in range(4):
        MM.LAST_TICK = int(System.currentTimeMillis()) - 6000
        MM.EXEC = STPE(1)
        MM.watchdog()
        made.append(MM.EXEC)
        if MM.EXEC is not None:
            MM.EXEC.shutdownNow()
    rl = [l_ for l_ in tail() if "stopped ticking" in l_ or "stopped 3 times" in l_]
    chk(int(MM.RESTARTS) == 3 and len(rl) == 4 and "(3 of 3)" in rl[2] and "stopped 3 times" in rl[3],
        "X9. FIX: a dead thread is restarted at most 3 times, each logged: %s" % [l_[:70] for l_ in rl])
    MM.RESTARTS = 0
    MM.WD_LOGGED = False
    park()

    # 10. the budget grows with the players still filling
    bn = [int(MM.budgetNs(JInt(n_))) for n_ in (0, 1, 2, 4, 8, 20)]
    pc = [int(MM.pieceCap(JInt(n_))) for n_ in (0, 1, 2, 3, 5)]
    chk(bn == [3000000, 3000000, 4000000, 6000000, 10000000, 10000000] and pc == [24, 24, 48, 64, 64],
        "X10. FIX: budget 3 ms + 1 ms per extra filling player (10 ms max) %s; pieces tilesPerTick x 1-3 (64 max) %s" % (bn, pc))

    # 11. small ones: the Online default, the seconds hint, the on / off answer, NOSTREAM bounded
    ond = wdef("Online") if False else (getattr(Wid, "def_", None) or getattr(Wid, "def"))("Online")
    chk(str(ond.anchor) == "tr" and int(ond.dy) == 206, "X11. FIX: the Online widget's default is tr 8,206 (under the minimap, not beneath it)")
    st_ = [str(MC.secText(JLong(ms_))) for ms_ in (250, 500, 1000, 1040, 1050, 1100, 2000)]
    chk(st_ == ["0.25", "0.5", "1", "1.04", "1.05", "1.1", "2"], "X11. FIX: the fastest-update hint in seconds: %s" % st_)
    MC.ENABLED = False
    t_off = str(MM.onText(True, "default"))
    MC.ENABLED = True
    MC.DISABLED_WORLDS = "dungeon*"
    t_w = str(MM.onText(True, "dungeon_7"))
    MC.DISABLED_WORLDS = ""
    t_ok, t_no = str(MM.onText(True, "default")), str(MM.onText(False, "default"))
    chk("switched off" in t_off and "not shown in this world" in t_w and t_ok == "[SkyyHud] minimap on" and t_no == "[SkyyHud] minimap off",
        "X11. FIX: /skyyhud minimap on says why nothing shows: %s | %s" % (t_off, t_w))
    MM.NOSTREAM.clear()
    for k_ in range(300):
        MM.noStreamLog("inst-%d" % k_)
    chk(int(MM.NOSTREAM.size()) == 256, "X11. FIX: the no-stream world list is bounded (256)")
    MM.NOSTREAM.clear()
    # the settings page hides update speeds faster than the admin's cap
    MC.MIN_INTERVAL = 0.5
    bq, eq = UCB(), UEB()
    SP(px_["pr"], ep.plugin, "Minimap").build(None, bq, eq, None)
    evq = [str(e.selector) for e in eq.getEvents()]
    hint = [str(c.data) for c in bq.getCommands() if c.selector is not None and "SkyyMmSUHint" in str(c.selector)]
    MC.MIN_INTERVAL = 0.25
    bq2, eq2 = UCB(), UEB()
    SP(px_["pr"], ep.plugin, "Minimap").build(None, bq2, eq2, None)
    evq2 = [str(e.selector) for e in eq2.getEvents()]
    chk("#SkyyMmSU250" not in evq and "#SkyyMmSU500" in evq and "#SkyyMmSU250" in evq2 and any("0.5 s" in h_ for h_ in hint),
        "X3. FIX: admin fastest 0.5 s -> Smooth is not offered (hint %s); at 0.25 s it is" % hint)

    # ======================================================================== scenarios shared with the old jar (regression)
    res["scen"]["regress"] = regress_scenarios(PKG, U, field, PRc, Transform, UCB, UEB, HM, SP, LS, Paths, work, bridge, JClass)

    # ======================================================================== R: start twice on a scratch COPY of the live data
    if os.path.isdir(LIVE):
        mods = os.path.join(work, "live")
        shutil.copytree(LIVE, os.path.join(mods, "Skyy_SkyyHud"))
        hdir = os.path.join(mods, "Skyy_SkyyHud")
        Pub = JClass(PKG + "CfgPub")

        def tree():
            o = {}
            for dp, dn, fn in os.walk(mods):
                for f in fn:
                    p = os.path.join(dp, f)
                    o[os.path.relpath(p, mods)] = (open(p, "rb").read(), os.path.getmtime(p))
            return o
        lyd = os.path.join(hdir, "layouts")
        players_ = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []

        def start():
            LS.CACHE.clear()
            LS.DIR = Paths.get(lyd)
            Cfg.FILE = Paths.get(os.path.join(hdir, "config.properties"))
            Cfg.PARSED = None
            r_ = {"cfg": str(Cfg.load()), "mm": [bool(MC.ENABLED), str(MC.MAX_RADIUS), str(MC.DETAIL)]}
            Pub.start(Paths.get(mods), None)
            for k, us in enumerate(players_):
                pr = U.allocateInstance(PRc.class_)
                field(PRc, "uuid").set(pr, UUID.fromString(us))
                field(PRc, "username").set(pr, "Live%d" % k)
                field(PRc, "transform").set(pr, Transform(-1500.2, 112.0, 2048.9))
                mp = LS.get(pr.getUuid())
                r_[us] = dict((w, str(mp.get(w).ser())) for w in [str(x) for x in Wid.IDS])
                h_ = HM(pr)
                bb_ = UCB()
                mb.invoke(h_, bb_)
                bw_, ev2 = UCB(), UEB()
                SP(pr, ep.plugin, "Minimap").build(None, bw_, ev2, None)
            Pub.flush()
            return r_
        t0_ = tree()
        time.sleep(1.1)
        r1 = start()
        t1_ = tree()
        chk(t1_ == t0_, "R. start 1 on the live copy writes nothing (new %s changed %s)" % (sorted(k for k in t1_ if k not in t0_),
                                                                                         sorted(k for k in t0_ if k in t1_ and t0_[k] != t1_[k])))
        for us in players_:
            fl = {}
            for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
                if "=" in ln and not ln.startswith("#"):
                    k_, v_ = ln.strip().split("=", 1)
                    fl[k_] = v_
            chk(all(r1[us][w] == fl[w] for w in r1[us] if w in fl) and r1[us]["Minimap"] == "1,tr,8,40,100,1",
                "R. %s...: every saved widget loads as saved; Minimap (not in the file) = the default" % us[:8])
        time.sleep(1.1)
        r2 = start()
        t2_ = tree()
        chk(r2 == r1 and t2_ == t1_, "R. start 2: same layouts, no file churn")
        res["live_players"] = len(players_)
    else:
        res["live_players"] = -1
    for f_, v_ in saved_static:
        f_.set(None, v_)
    json.dump(res, open(out, "w"), indent=1)


def regress_scenarios(PKGs, U, field, PRc, Transform, UCB, UEB, HM, SP, LS, Paths, work, bridge, JClass):
    """the main HUD and four non-minimap Settings pages on the same layouts - both jars must send the same commands"""
    UUID = JClass("java.util.UUID")
    out = {}
    mb = HM.class_.getDeclaredMethod("build", UCB.class_)
    mb.setAccessible(True)
    plugin = U.allocateInstance(JClass(PKGs + "SkyyHudPlugin").class_)
    field(JClass(PKGs + "SkyyHudPlugin"), "huds").set(plugin, JClass("java.util.concurrent.ConcurrentHashMap")())
    for case, lines in (("default", None), ("styled", ["Coords=1,tl,8,8,120,1,gold,1,1,1,black", "Zone=1,tr,8,8,100,0", "Gclock=1,bl,0,0,170,1",
                                                       "Skills=1,tl,8,544,100,1,def,1,0,0,def,1,1023"])):
        d = os.path.join(work, "reg-" + case, "layouts")
        os.makedirs(d, exist_ok=True)
        pr = U.allocateInstance(PRc.class_)
        u = UUID(0x5ce0, 777)
        field(PRc, "uuid").set(pr, u)
        field(PRc, "username").set(pr, "Reg")
        field(PRc, "transform").set(pr, Transform(10.2, 64.0, -20.7))
        if lines:
            open(os.path.join(d, str(u) + ".properties"), "w", encoding="latin-1").write("#x\n" + "\n".join(lines) + "\n")
        LS.DIR = Paths.get(d)
        LS.CACHE.clear()
        h = HM(pr)
        h.joinMs = 0
        b = UCB()
        mb.invoke(h, b)
        cm = [[str(c.type), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
               None if c.text is None else str(c.text)] for c in b.getCommands()]
        out["hud " + case] = [c for c in cm if not (c[0] == "Set" and c[1] and ("Session" in c[1] or "Rclock" in c[1]))]
        for wid in ("Gclock", "Combat", "Skills", "Party"):
            b2, ev2 = UCB(), UEB()
            SP(pr, plugin, wid).build(None, b2, ev2, None)
            out["settings %s %s" % (wid, case)] = [[str(c.type), None if c.selector is None else str(c.selector),
                                                   None if c.text is None else str(c.text)] for c in b2.getCommands()]
    return out


# ======================================================================================================== child: the OLD jar
def run_old(jar, out, line):
    from jpype import JClass
    import skyybuild as B
    _jvm_start([jar], [B.JAVASSIST])
    res = {"checks": [], "scen": {}}

    def chk(cond, what):
        res["checks"].append([bool(cond), what])
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
    U = fu.get(None)

    def field(cls, name):
        c = cls.class_
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStoreOld", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStoreOld() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    store = U.allocateInstance(fk.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    H = lambda n: JClass(PKG + n)
    WL, Wid, LS, HM, SP, Cfg = H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("SettingsPage"), H("HudCfg")
    Paths = JClass("java.nio.file.Paths")
    work = os.path.join(SCRATCH, "child-old")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    Cfg.FILE = Paths.get(os.path.join(work, "config.properties"))
    Cfg.load()
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    # rollback: the 0.3.13 jar reads a 0.3.14 file with the Minimap entry + every old widget
    d = os.path.join(work, "rb", "layouts")
    os.makedirs(d)
    u = JClass("java.util.UUID")(0x5ce0, 4242)
    old_lines = ["Coords=1,tl,8,8,120,1,gold,1,1,1,black", "Combat=1,t,0,130,100,1,def,1,0,0,def,1,-,aqua", "Gclock=1,bl,0,0,170,1"]
    open(os.path.join(d, str(u) + ".properties"), "w", encoding="latin-1").write("#x\n" + "\n".join(old_lines + ["Minimap=" + line]) + "\n")
    LS.DIR = Paths.get(d)
    LS.CACHE.clear()
    m = LS.get(u)
    got = dict((ln.split("=", 1)[0], str(m.get(ln.split("=", 1)[0]).ser())) for ln in old_lines)
    chk(all(got[ln.split("=", 1)[0]] == ln.split("=", 1)[1] for ln in old_lines) and m.get("Minimap") is None,
        "L. ROLLBACK: the 0.3.13 jar reads a 0.3.14 file: every old widget intact, the Minimap entry ignored")
    p_ = WL.parse(line, None)
    chk(p_ is not None and str(p_.anchor) == "tr" and int(p_.lines) == 5 and str(p_.ocol) == "def",
        "L. ROLLBACK: 0.3.13's WLayout.parse reads a 15-field line with every field but the 15th")
    res["scen"]["regress"] = regress_scenarios(PKG, U, field, JClass("com.hypixel.hytale.server.core.universe.PlayerRef"),
                                               JClass("com.hypixel.hytale.math.vector.Transform"),
                                               JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"),
                                               JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"), HM, SP, LS, Paths, work,
                                               bridge, JClass)
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
    common = ["--dir", SCRATCH, "--live", LIVE]
    on = os.path.join(SCRATCH, "child-new.json")
    p = subprocess.run([sys.executable, me, "--run", JAR, "--out", on, "--mode", "new"] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(on), "child JVM for the 0.3.14 jar ran (exit %s)" % p.returncode)
    if FAILS:
        return finish()
    new = json.load(open(on))
    check(not new["load_fails"], "A. %d classes of the 0.3.14 jar load under -Xverify:all %s" % (new["classes"], new["load_fails"][:3]))
    if new["load_fails"]:
        return finish()
    oo = os.path.join(SCRATCH, "child-old.json")
    line = new["scen"].get("line_for_old", "1,tr,8,40,100,1")
    p = subprocess.run([sys.executable, me, "--run", OLD_JAR, "--out", oo, "--mode", "old", "--line", line] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(oo), "child JVM for the 0.3.13 jar ran (exit %s)" % p.returncode)
    old = json.load(open(oo)) if os.path.isfile(oo) else {"checks": [], "scen": {}, "load_fails": ["missing"], "classes": 0}
    check(not old["load_fails"], "A. %d classes of the 0.3.13 jar load under -Xverify:all" % old["classes"])
    for ok, what in new["checks"] + old["checks"]:
        check(ok, what)
    print("A-R. %d checks in the child JVMs (%d failed); live copy players: %s" % (len(new["checks"]) + len(old["checks"]),
                                                                                 sum(1 for ok, w in new["checks"] + old["checks"] if not ok),
                                                                                 new.get("live_players")))
    if new.get("live_players", -1) < 0:
        SKIPS.append("R (start twice on a copy of the live data): no live Skyy_SkyyHud folder at %s" % LIVE)
    # S: regression - the main HUD + other widgets' Settings pages: identical commands in both jars
    rn, ro = new["scen"].get("regress", {}), old["scen"].get("regress", {})
    diff = [k for k in ro if rn.get(k) != ro.get(k)]
    check(ro and not diff and set(rn) == set(ro), "S. 0.3.13 vs 0.3.14: the main HUD and the Gclock / Combat / Skills / Party Settings pages send "
                                                   "the SAME commands (%d scenarios): %s" % (len(ro), diff))
    # F: class bytes
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if os.path.isfile(bco):
        bc = json.load(open(bco))
        expect = {"WLayout": None, "Widgets": None, "HudMain": None, "EditorPage": None, "SettingsPage": None, "SkyyHudPlugin": None,
                  "HudCfg": None, "TickTask": None, "AttachTask": None, "HudCmd": None, "LayoutStore": None}
        unexpected = []
        for n, r in bc.items():
            short = n.split("/")[-1][:-6]
            if short.startswith("Cfg"):
                if not r["version_only"] and short not in ("CfgRows", "CfgFn") and not (short == "CfgFile" and r["changed"] == ["<clinit>()V"]):
                    unexpected.append(short)
                continue
            if short not in expect:
                unexpected.append(short)
        check(not unexpected, "F. class bytes 0.3.13 -> 0.3.14 differ only in the expected classes (kit classes: version / rows): %s" % unexpected)
        print("F. changed classes: %s" % ", ".join("%s (%d methods changed, %d new)" % (n.split("/")[-1][:-6], len(r["changed"]), len(r["new"]))
                                                  for n, r in sorted(bc.items())))
    # Z: the engine-access audit
    auo = os.path.join(SCRATCH, "audit.json")
    p = subprocess.run([sys.executable, me, "--audit", JAR, "--out", auo] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran")
    if os.path.isfile(auo):
        au = json.load(open(auo))
        check(not au["refused"], "Z. engine-access audit: %d classes, %d references, 0 refused: %s" % (au["classes"], au["refs"], au["refused"][:3]))
        check(au["control_refused"] and "IllegalAccessError" in str(au["control_run"]), "Z. control: the protected onRemove from outside is refused and throws")
        print("Z. audit: %d classes, %d references, %d refused, %d caller-sensitive ok" % (au["classes"], au["refs"], len(au["refused"]), au["caller_sensitive"]))
    rep = new.get("report", {})
    for k in ("first_fill", "tick_ms_20p", "encode_ms_per_piece", "bench_500_ms", "heap_mb_after_20p", "encode_worst_png", "docs", "geometry"):
        print("  %s: %s" % (k, rep.get(k)))
    json.dump(rep, open(os.path.join(SCRATCH, "report.json"), "w"), indent=1)
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed%s" % (OKS[0], len(FAILS), (", %d part(s) skipped" % len(SKIPS)) if SKIPS else ""))
    for f in FAILS:
        print("  FAILED:", f)
    for s_ in SKIPS:
        print("  SKIPPED:", s_)
    print("SkyyHud %s harness:" % VERSION, ("PASS" + (" (with skips)" if SKIPS else "")) if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
