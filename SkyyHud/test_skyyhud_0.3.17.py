"""SkyyHud 0.3.17 - harness for the icon round (tools/hud_0_3_17_patch.py).

    python SkyyHud/test_skyyhud_0.3.17.py [--jar <SkyyHud-0.3.17.jar>] [--old <SkyyHud-0.3.16.jar>] [--old2 <SkyyHud-0.3.15.jar>]
                                          [--live <Skyy_SkyyHud folder>] [--dir <scratch>] [--keep]

Build the jar first (python SkyyHud/build_skyyhud_0.3.17.py). Every JVM is a fresh child (the game's own JRE, -XX:-UsePerfData,
java.io.tmpdir + TEMP/TMP in the scratch folder; the class checks also -Xverify:all).
  P  THE ICON: the jar's root icon-256.png is a valid 256 x 256 PNG (SkyyHud/make_icon.check_icon: signature, every chunk CRC, IHDR,
     IDAT inflates to the exact row bytes) = SkyyHud/icon-256.png = a fresh render of make_icon.py (deterministic: two renders, same
     bytes); fully decoded: opaque centre, transparent corners (rounded panel). NEGATIVE CONTROLS on check_icon: the 0.3.16 jar's
     64 x 64 icon (the client's warning), a bad CRC, a truncated file, a non-PNG, a 255 x 255 PNG - all refused. THE BUILD GUARD
     (the 0.3.17 build script's own icon block, cut out of the script and executed): passes the shipped icon, stops on the 64 x 64 one.
  C  the client's rule (HytaleClient.exe, read only): it names "icon-256.png" and the 256 check message - the file name we ship.
  J  the jar files: the same entries as 0.3.16 (manifest.json, Common/UI/Custom/SkyyHud/dot.png, icon-256.png); dot.png identical;
     manifest.json = 0.3.16's with only the version changed; no .ui file; the icon is NOT under Common/ (no client asset cache entry)
  R  REGRESSION: the whole 0.3.16 harness re-run on the 0.3.17 jar (-Xverify:all class loading of every class, the two-world minimap
     repro, arrows, placement, the kit rows, START TWICE ON A SCRATCH COPY OF THE LIVE DATA (nothing written), engine-access audit)
  F  class compare 0.3.16 -> 0.3.17: no class added or removed; every class that differs differs ONLY in the version text
  V  THE ENGINE ASSET VALIDATORS (the SkyySacks 0.7.14 V child: real asset stores, the vanilla pack loaded store by store, then the jar
     as its own pack): no failed store, not one SEVERE / WARNING line for the jar; P0 no one-entry Parallel in the jar's server JSON
     (the jar has none); NEGATIVE CONTROL: a one-entry Parallel pack MUST be refused ("Array size is invalid") - the validators run.
Not testable without the game (UNVERIFIED): the client's mod list showing the new icon and the warning gone.
Default scratch folder: tools/dev/scratch/hudicon01/harness (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, subprocess, zipfile, struct, zlib, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION, OLD2_VERSION = "0.3.17", "0.3.16", "0.3.15"
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
ASSETS_ZIP = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
CLIENT_EXE = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Client", "HytaleClient.exe")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "hudicon01", "harness"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
OLD2_JAR = os.path.abspath(arg("--old2", os.path.join(HERE, "SkyyHud-%s.jar" % OLD2_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyHud")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def png_chunks(data):
    p, out = 8, []
    while p + 12 <= len(data):
        ln = struct.unpack(">I", data[p:p + 4])[0]
        out.append((data[p + 4:p + 8], data[p + 8:p + 8 + ln]))
        p += 12 + ln
    return out


def decode_rgba(data):
    """RGBA rows of an 8-bit RGBA non-interlaced PNG (all five filter types)"""
    ch = png_chunks(data)
    w, h = struct.unpack(">II", ch[0][1][:8])
    raw = zlib.decompress(b"".join(b for t, b in ch if t == b"IDAT"))
    bpp, st = 4, w * 4
    rows, prev = [], bytearray(st)
    for y in range(h):
        f = raw[y * (st + 1)]
        line = bytearray(raw[y * (st + 1) + 1:(y + 1) * (st + 1)])
        for i in range(st):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, rows


def mkpng(w, h, raw):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


# ======================================================================================================== P / C / J (plain Python)
def run_icon():
    MI = load_module(os.path.join(HERE, "make_icon.py"), "skyyhud_make_icon")
    zj, zo = zipfile.ZipFile(JAR), zipfile.ZipFile(OLD_JAR)
    icon = zj.read("icon-256.png")
    check(MI.check_icon(icon, 256) is None, "P. the jar's icon-256.png is a valid 256 x 256 PNG: %s" % MI.check_icon(icon, 256))
    check(icon == open(os.path.join(HERE, "icon-256.png"), "rb").read(), "P. the jar's icon = SkyyHud/icon-256.png")
    r1 = MI.png(MI.W, MI.W, MI.render())
    r2 = MI.png(MI.W, MI.W, MI.render())
    check(r1 == r2 == icon, "P. make_icon.py renders the same bytes twice, = the shipped icon (deterministic, original art from code)")
    w, h, rows = decode_rgba(icon)
    px = lambda x, y: rows[y][4 * x:4 * x + 4]
    check((w, h) == (256, 256) and px(0, 0)[3] == 0 and px(255, 255)[3] == 0 and px(128, 128)[3] == 255 and px(64, 128)[3] == 255,
          "P. decoded: transparent corners, opaque panel (%s %s %s)" % (px(0, 0).hex(), px(128, 128).hex(), px(64, 128).hex()))
    colours = set()
    for y in range(0, 256, 4):
        for x in range(0, 256, 4):
            colours.add(px(x, y))
    check(len(colours) > 40, "P. a real picture, not a flat fill (%d colours on a 4 px grid)" % len(colours))
    # negative controls
    old = zo.read("icon-256.png")
    e_old = MI.check_icon(old, 256)
    check(e_old is not None and "64x64" in e_old, "P CONTROL: the 0.3.16 icon is refused: %s" % e_old)
    bad_crc = bytearray(icon)
    bad_crc[40] ^= 0xFF
    e_crc = MI.check_icon(bytes(bad_crc), 256)
    check(e_crc is not None and "CRC" in e_crc, "P CONTROL: a flipped byte is refused: %s" % e_crc)
    e_tr = MI.check_icon(icon[:len(icon) // 2], 256)
    check(e_tr is not None, "P CONTROL: a truncated icon is refused: %s" % e_tr)
    e_np = MI.check_icon(b"GIF89a" + b"\0" * 64, 256)
    check(e_np is not None and "signature" in e_np, "P CONTROL: a non-PNG is refused: %s" % e_np)
    e_255 = MI.check_icon(mkpng(255, 255, b"".join(b"\0" + b"\0" * 1020 for _ in range(255))), 256)
    check(e_255 is not None and "255x255" in e_255, "P CONTROL: a 255 x 255 PNG is refused: %s" % e_255)
    e_sh = MI.check_icon(mkpng(256, 256, b"\0" * 100), 256)
    check(e_sh is not None and "IDAT" in e_sh, "P CONTROL: a 256 x 256 header with too few pixel bytes is refused: %s" % e_sh)
    # THE BUILD GUARD: the 0.3.17 script's own icon block, executed with the shipped icon and with the old one
    src = open(os.path.join(HERE, "build_skyyhud_%s.py" % VERSION), encoding="utf8").read().replace("\r\n", "\n")
    a = src.index("png_root = open(os.path.join(HERE, \"icon-256.png\"), \"rb\").read()\n")
    b = src.index("png_dot = ", a)
    block = src[a:b].split("\n", 1)[1]
    check("check_icon(png_root, 256)" in block and "assert _icon_err is None" in block, "P. the build script's icon guard block found")
    for data, want in ((icon, True), (old, False)):
        g = {"os": os, "sys": sys, "HERE": HERE, "png_root": data}
        try:
            exec(compile(block, "build_skyyhud_%s.py (icon block)" % VERSION, "exec"), g)
            ok = True
        except AssertionError as e:
            ok = False
            msg = str(e)
        check(ok == want, "P. the build guard %s the %s icon%s" % ("passes" if want else "stops on", "shipped" if want else "64 x 64",
                                                                   "" if ok else " (" + msg + ")"))
    # C: the client's rule
    if os.path.isfile(CLIENT_EXE):
        exe = open(CLIENT_EXE, "rb").read()
        u = lambda t: t.encode("utf-16-le")
        check(u("icon-256.png") in exe and u("has an icon.png with wrong dimensions ({1}x{2}, expected {3}x{3})") in exe,
              "C. HytaleClient.exe names icon-256.png and the 'wrong dimensions ... expected {3}x{3}' check")
    else:
        print("C. skipped: no client at", CLIENT_EXE)
    # J: the jar files
    nn = sorted(n for n in zj.namelist() if not n.endswith(".class"))
    no = sorted(n for n in zo.namelist() if not n.endswith(".class"))
    check(nn == no == ["Common/UI/Custom/SkyyHud/dot.png", "icon-256.png", "manifest.json"], "J. the same non-class entries as 0.3.16: %s" % nn)
    check(zj.read("Common/UI/Custom/SkyyHud/dot.png") == zo.read("Common/UI/Custom/SkyyHud/dot.png"), "J. dot.png identical")
    mn, mo = json.loads(zj.read("manifest.json")), json.loads(zo.read("manifest.json"))
    diff = sorted(k for k in set(mn) | set(mo) if mn.get(k) != mo.get(k))
    check(diff == ["Name", "Version"] or diff == ["Version"], "J. manifest.json differs only in the version: %s" % diff)
    check(json.dumps(mn).replace(VERSION, "V") == json.dumps(mo).replace(OLD_VERSION, "V"), "J. manifest.json = 0.3.16's with the version text replaced")
    check(not any(n.lower().endswith(".ui") for n in zj.namelist()), "J. no .ui file in the jar")
    print("P/C/J. icon 256 x 256, %d bytes (was %s, 64 x 64); %d colours; jar entries %s" % (len(icon), len(old), len(colours), nn))


# ======================================================================================================== V (child)
def run_v():
    # (copied from SkyySacks/test_skyysacks_0.7.14.py run_v: the real asset stores + the vanilla pack, store by store)
    import time, hashlib
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JString, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-XX:-UsePerfData", "-Xmx6g", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "v-universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    # a bare server + universe (the stores ask HytaleServer.get() / Universe.get())
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = us.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
    jf(HS, "instance").set(None, hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = us.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    jf(UNI, "playersByUuid").set(uni, pbu)
    jf(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    jf(UNI, "worlds").set(uni, wmap)
    jf(UNI, "worldsByUuid").set(uni, CHM())
    jf(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jf(UNI, "instance").set(None, uni)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)

    def records(start=0):
        out = []
        for r in list(CAPLOG)[start:]:
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                th = r.getThrown()
                if th is not None:
                    msg += " | " + str(th)[:300]
                out.append((str(r.getLevel()), msg))
            except Exception as e:
                out.append(("?", str(e)))
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")

    def reg_ilt(c, path, codec, unknown=False):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        AR.register(b_.build())
    # the stores InteractionModule registers in the game (the SkyyArmory 0.1.10 harness pattern)
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True)
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)
    AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPool = JClass("javassist.bytecode.ConstPool")
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(idx)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jf(C_, "CODEC").get(None))
    PRJIc = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    INTc.CODEC.register("Projectile", PRJIc.class_, PRJIc.CODEC)
    SPCc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsConfig")
    JClass("com.hypixel.hytale.server.core.modules.projectile.config.PhysicsConfig").CODEC.register("Standard", SPCc.class_, SPCc.CODEC)
    check(len(regs) >= 70 and "Simple" in [a for a, b in regs] and "Parallel" in [a for a, b in regs],
          "V: the interaction Type codecs registered from InteractionModule.setup's bytecode (%d)" % len(regs))
    # the bag pages, the way the plugin's setup() registers them (OpenCustomUIInteraction.registerSimple -> PAGE_CODEC) before assets load
    OCUc = JClass(PI + "server.OpenCustomUIInteraction")
    CPSn = PI + "server.OpenCustomUIInteraction$CustomPageSupplier"
    CPSc = JClass(CPSn)
    BCc = JClass("com.hypixel.hytale.codec.builder.BuilderCodec")

    @JImplements(CPSn)
    class PageSup:
        @JOverride
        def tryCreate(self, a, b, c, d): return None

    @JImplements("java.util.function.Supplier")
    class SupOf:
        @JOverride
        def get(self): return PageSup()
    zj = zipfile.ZipFile(JAR)
    pages = set()
    for n in zj.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            for x in json.loads(zj.read(n))["Interactions"]["Secondary"]["Interactions"]:
                if x.get("Type") == "OpenCustomUI":
                    pages.add(x["Page"]["Id"])
    for pid in sorted(pages):
        OCUc.PAGE_CODEC.register(pid, CPSc.class_, BCc.builder(CPSc.class_, SupOf()).build())
    # the common assets (the CommonAssetModule's job in the game): every Common/ file of Assets.zip and of the jar, at its zip path
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    Paths, FSs, HashMap = JClass("java.nio.file.Paths"), JClass("java.nio.file.FileSystems"), JClass("java.util.HashMap")
    ZFS = {}

    def zfs(zpath):
        if zpath not in ZFS:
            ZFS[zpath] = FSs.newFileSystem(Paths.get(zpath), HashMap())
        return ZFS[zpath]

    def add_common(pack, zpath, real):
        n = 0
        fs = zfs(zpath)
        with zipfile.ZipFile(zpath) as z:
            for nm in z.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    h = hashlib.sha256(z.read(nm)).hexdigest() if real else "0" * 64
                    CAR.addCommonAsset(pack, FCA(fs.getPath("/" + nm), nm[len("Common/"):], h, None))
                    n += 1
        return n
    AP = JClass("com.hypixel.hytale.assetstore.AssetPack")
    Files, LinkOption = JClass("java.nio.file.Files"), JClass("java.nio.file.LinkOption")

    def store_order():
        stores = dict((st.getAssetClass(), st) for st in AR.getStoreMap().values())
        done, order = set(), []

        def visit(c, stack):
            if c in done or c not in stores or c in stack:
                return
            stack.add(c)
            for d in stores[c].getLoadsAfter():
                visit(d, stack)
            done.add(c)
            order.append(stores[c])
        for c in list(stores):
            visit(c, set())
        return order

    def loadpack(zpath, name, immutable):
        """AssetRegistryLoader.loadAssets0's per-store step: loadAssetsFromDirectory(pack, <root>/Server/<store path>) in dependency order"""
        n0 = len(CAPLOG)
        pack = AP(Paths.get(zpath), name, zfs(zpath).getPath("/"), zfs(zpath), immutable, None, None)
        srv = pack.getRoot().resolve("Server")
        failed = []
        for st in store_order():
            d = srv.resolve(st.getPath())
            if not Files.isDirectory(d, JArray(LinkOption)(0)):
                continue
            try:
                if st.loadAssetsFromDirectory(name, d).hasFailed():
                    failed.append(str(st.getAssetClass().getSimpleName()))
            except Exception as e:
                failed.append("%s EXC %s" % (st.getAssetClass().getSimpleName(), str(e)[:200]))
        return failed, records(n0)
    t0 = time.time()
    nv = add_common("Hytale:Hytale", ASSETS_ZIP, False)
    vfail, vrec = loadpack(ASSETS_ZIP, "Hytale:Hytale", True)
    print("V. vanilla pack loaded (%d common files, %.0f s; %d SEVERE lines from stores a bare JVM lacks codecs for - not ours)"
          % (nv, time.time() - t0, len([r for r in vrec if r[0] == "SEVERE"])))
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IPA = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    PSY = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    PSP = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSpawner")
    check(IPA.getAssetMap().getAsset("Block") is not None and ITEM.getAssetMap().getAssetMap().size() > 1000,
          "V: the vanilla Block set and the vanilla items (%d) are in the real stores" % ITEM.getAssetMap().getAssetMap().size())
    # ---- THE JAR (SkyyHud: no server assets; its Common/ picture goes into the common registry, the pack into every store)
    zj = zipfile.ZipFile(JAR)
    pack_name = "Skyy:%s SkyyHud" % VERSION
    nc = add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    bad = [r for r in rec if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:12]:
        print("   V:", r[0], r[1][:500].replace("\n", " / "))
    check(not fail and not bad, "V: the %s jar loads as a pack into the real stores: no failed store (%s), no SEVERE / WARNING line (%d)" % (VERSION, fail, len(bad)))
    check(nc == 1, "V: the jar's common assets registered: %d (dot.png; the icon is a root file, not an asset)" % nc)
    shortp, nj = [], [0]

    def walk(p, x):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                shortp.append(p)
            for v in x.values():
                walk(p, v)
        elif isinstance(x, list):
            for v in x:
                walk(p, v)
    for n in zj.namelist():
        if n.startswith("Server/") and n.endswith(".json"):
            walk(n, json.loads(zj.read(n)))
            nj[0] += 1
    check(not shortp, "V (P0): no Parallel with fewer than 2 entries in the jar's %d server JSON files" % nj[0])
    # NEGATIVE CONTROL: a one-entry Parallel MUST be refused (the SkyyArmory 0.1.9 failure) - proves the validators run
    zp = os.path.join(SCRATCH, "v-ctl-parallel.jar")
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("Server/Item/Interactions/SkyyTestCtl/SkyyTestCtl_Parallel.json",
                   json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple", "RunTime": 0.1}]}]}}))
    f_, r_ = loadpack(zp, "Skyy:test ctl", False)
    hit = [r for r in r_ if r[0] == "SEVERE" and "Array size is invalid" in r[1]]
    check(bool(hit), "V CONTROL: a one-entry Parallel pack is refused by the engine validator (%d SEVERE, store failed: %s)" % (len(hit), f_))
    print("V. %s as a pack: %d common asset, 0 failed stores, %d SEVERE / WARNING; P0 clean (%d server JSON); control refused: %s"
          % (VERSION, nc, len(bad), nj[0], bool(hit)))


# ======================================================================================================== parent
def main():
    if "--child-v" in sys.argv:
        try:
            run_v()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("crash: %s" % e)
        print("%d ok, %d fail" % (OKS[0], len(FAILS)))
        sys.exit(1 if FAILS else 0)
    if "--bytecode" in sys.argv:
        m = load_module(os.path.join(HERE, "test_skyyhud_0.3.13.py"), "hud0313h")
        m.SCRATCH = SCRATCH
        m.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"), arg("--ov"), arg("--nv"))
        return
    for j in (JAR, OLD_JAR, OLD2_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not (SCRATCH + os.sep).startswith(SCRATCH_ROOT + os.sep) or SCRATCH == SCRATCH_ROOT:
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"), PYTHONDONTWRITEBYTECODE="1")
    env.pop("JAVA_TOOL_OPTIONS", None)
    me = os.path.abspath(__file__)
    run_icon()
    # R: the 0.3.16 harness on the 0.3.17 jar
    print("---- R: the 0.3.16 harness re-run on the %s jar" % VERSION)
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyhud_0.3.16.py"), "--jar", JAR, "--old", OLD2_JAR, "--live", LIVE,
                        "--dir", os.path.join(SCRATCH, "h16")], env=env, capture_output=True, text=True, encoding="utf8", errors="replace")
    tail = [ln for ln in p.stdout.splitlines() if ln.startswith(("A-L.", "F.", "Z.", "  FAILED", "  SKIPPED", "SkyyHud 0.3.16 harness", "FAIL"))
            or "checks passed" in ln]
    for ln in tail:
        print("  " + ln[:300])
    check(p.returncode == 0 and "SkyyHud 0.3.16 harness: PASS" in p.stdout and "SKIPPED" not in p.stdout,
          "R. the whole 0.3.16 harness passes on the %s jar, live-copy start twice included (exit %s)" % (VERSION, p.returncode))
    # F: class compare
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION,
                        "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "F. bytecode child ran")
    if os.path.isfile(bco):
        bc = json.load(open(bco))
        notv = sorted(n for n, r in bc.items() if not r["version_only"] or r["new"] or r["gone"] or r["fields_new"] or r["fields_gone"])
        check(not notv, "F. every class that differs 0.3.16 -> 0.3.17 differs ONLY in the version text: %s" % notv)
        zn = set(n for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class"))
        zo = set(n for n in zipfile.ZipFile(OLD_JAR).namelist() if n.endswith(".class"))
        check(zn == zo, "F. no class added or removed: %s %s" % (sorted(zn - zo), sorted(zo - zn)))
        print("F. %d classes; differing (version text only): %s" % (len(zn), ", ".join(n.split("/")[-1][:-6] for n in sorted(bc)) or "none"))
    # V: the engine asset validators
    print("---- V: the engine asset validators")
    rc = subprocess.call([sys.executable, me, "--child-v", "--dir", SCRATCH, "--jar", JAR], env=env, cwd=ROOT)
    check(rc == 0, "V. the engine asset validator child passed (exit %d)" % rc)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    print("SkyyHud %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
