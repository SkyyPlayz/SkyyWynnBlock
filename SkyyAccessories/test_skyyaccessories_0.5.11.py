"""Bare-JVM harness for SkyyAccessories 0.5.11 - THE LANTERN ITEM TEXTURES (tools/accessories_0_5_11_patch.py; the log-scan fix of the
client lines "Cannot use Blocks/Decorative_Sets/<set>/Lantern_Texture.png as texture for item Skyy_Talisman_Lantern_<rarity>" x4).

    python SkyyAccessories/test_skyyaccessories_0.5.11.py [--jar <0.5.11 jar>] [--old <0.5.10 jar>] [--dir <scratch>] [--live <folder>] [--keep]

JVM 1 (the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in the scratch folder), each jar in its own class loader:
  A  every class of both jars loads, verifies and initialises
  B  0.5.10 -> 0.5.11 class compare: the same classes, each byte-identical or version constants only (NO class change); the jar files:
     added exactly the 4 Lantern textures, changed exactly the 4 Lantern item JSONs (ONLY "Texture") and manifest.json (Version); every
     other file (server.lang, the other item JSONs, icons, the bag art, qualities) byte-identical
  T  THE TEXTURES: each new file = the vanilla lantern block texture of that rarity's look byte for byte (Assets.zip, read-only), a PNG of
     the same size, at Items/SkyyAccessories/... (not a vanilla path, not under Blocks/); the item's Model unchanged (the vanilla lantern
     blockymodel, its UVs see the same pixels); NO item JSON of the jar has a Texture under Blocks/ (the client refuses those); control:
     0.5.10 had exactly the 4 Lantern items on Blocks/ textures (= the 4 client log lines)
  L  start twice on a scratch COPY of the live Skyy_SkyyAccessories folder: no file changed
JVM 2 (V - the ENGINE ASSET VALIDATORS, the 0.5.8 / 0.5.9 section): the vanilla pack, then the jar as its own pack into the real stores:
  no failed store, no SEVERE / WARNING; every jar item in the Item store; the Accessory Bag look; NEW: the four Lantern items in the store
  carry OUR texture path and their model, toPacket() works and the packet carries our texture path; NEGATIVE CONTROLS (a one-entry
  Parallel, a missing Model / Texture / Icon, a LANTERN item whose texture file is missing) must be refused.
Nothing outside the scratch folder is written (default tools/dev/scratch/acc0511/acc-harness, deleted at the end unless --keep).
Exit code 1 on any failure. Not testable here: the client's own texture rule (no client in a bare JVM) - see the in-game steps.
"""
import os, sys, re, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.11", "0.5.10"
PKG = "com.skyy.accessories."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "acc0511", "acc-harness")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LAN_IDS = ["Skyy_Talisman_Lantern_%s" % w for w in ("Common", "Uncommon", "Rare", "Epic")]
LAN_LOOKS = ["Deco_Lantern", "Furniture_Kweebec_Lantern", "Furniture_Desert_Lantern", "Furniture_Temple_Light_Lantern"]
LAN_TEX = ["Items/SkyyAccessories/SkyyAccessories_Lantern_%s_Texture.png" % r for r in ("Normal", "Unique", "Rare", "Legendary")]
ASSETS_ZIP = os.path.join(os.environ.get("APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming")), "Hytale", "install",
                          "release", "package", "game", "latest", "Assets.zip")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def cp_utf8(b):
    n = struct.unpack(">H", b[8:10])[0]
    i, k, out = 10, 1, []
    while k < n:
        tag = b[i]
        if tag == 1:
            ln = struct.unpack(">H", b[i + 1:i + 3])[0]
            out.append((i, i + 3 + ln, b[i + 3:i + 3 + ln]))
            i += 3 + ln
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 5
        elif tag in (5, 6):
            i += 9
            k += 1
        elif tag in (7, 8, 16, 19, 20):
            i += 3
        elif tag == 15:
            i += 4
        else:
            raise ValueError("constant pool tag %d" % tag)
        k += 1
    return out


def jarfiles(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n, z.read(n)) for n in z.namelist() if not n.endswith("/"))
    z.close()
    return out


def snap(dd):
    out = {}
    for root, _ds, fs in os.walk(dd):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, dd)] = open(p, "rb").read()
    return out


def run():
    import jpype
    from jpype import JClass, JArray
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    Paths = JClass("java.nio.file.Paths")
    System = JClass("java.lang.System")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    F = {"old": jarfiles(OLD), "new": jarfiles(JAR)}
    CB = dict((k, dict((n[:-6].replace("/", "."), b) for n, b in F[k].items() if n.endswith(".class"))) for k in ("old", "new"))
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)

    # ---------------- A
    na = {"old": 0, "new": 0}
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                na[k] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: %s %d, %s %d classes (-Xverify:all)" % (OLD_VERSION, na["old"], VERSION, na["new"]))
    if FAILS:
        return

    # ---------------- B. no class change: byte-identical, or only "0.5.10" -> "0.5.11" constant pool strings
    old, new = CB["old"], CB["new"]
    check(set(new) == set(old), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
    same, vonly, other = 0, [], []
    for n in sorted(set(old) & set(new)):
        if old[n] == new[n]:
            same += 1
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        ok = len(co) == len(cn)
        rebuilt = new[n]
        if ok:
            for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
                if t0 == t1:
                    continue
                if t0.decode("utf8").replace(OLD_VERSION, VERSION) != t1.decode("utf8"):
                    ok = False
                    break
                rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
        if ok and rebuilt == old[n]:
            vonly.append(n[len(PKG):] if n.startswith(PKG) else n)
        else:
            other.append(n)
    check(not other, "B. no class changed beyond the version string: %s" % other)
    check(same + len(vonly) == len(new) and len(new) > 30, "B. every class accounted for (%d)" % len(new))
    print("B. classes: %d byte-identical, %d version string only (%s), %d other" % (same, len(vonly), ", ".join(vonly), len(other)))
    fo_ = dict((k, v) for k, v in F["old"].items() if not k.endswith(".class"))
    fn_ = dict((k, v) for k, v in F["new"].items() if not k.endswith(".class"))
    added, removed = sorted(set(fn_) - set(fo_)), sorted(set(fo_) - set(fn_))
    check(added == sorted("Common/" + p for p in LAN_TEX) and not removed, "B. added exactly the 4 Lantern textures, nothing removed: +%s -%s" % (added, removed))
    diff = sorted(k for k in fo_ if k in fn_ and fo_[k] != fn_[k])
    want = sorted(["manifest.json"] + ["Server/Item/Items/Utility/%s.json" % i for i in LAN_IDS])
    check(diff == want, "B. changed exactly manifest.json + the 4 Lantern item JSONs: %s" % diff)
    for t, i in enumerate(LAN_IDS):
        p = "Server/Item/Items/Utility/%s.json" % i
        a, b = json.loads(fo_[p]), json.loads(fn_[p])
        ka = dict((k, v) for k, v in a.items() if k != "Texture")
        kb = dict((k, v) for k, v in b.items() if k != "Texture")
        check(ka == kb and list(a) == list(b) and a["Texture"].startswith("Blocks/") and b["Texture"] == LAN_TEX[t],
              "B. %s: only Texture changed %s -> %s" % (i, a.get("Texture"), b.get("Texture")))
    mo_, mn_ = json.loads(fo_["manifest.json"]), json.loads(fn_["manifest.json"])
    check(mn_["Version"] == VERSION and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) ==
          dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")), "B. manifest: only Version / Name")
    print("B. jar files: +4 Lantern textures; changed: manifest.json + 4 Lantern JSONs (Texture only); %d others byte-identical" % (
        len(set(fo_) & set(fn_)) - len(diff)))

    # ---------------- T. the textures
    az = zipfile.ZipFile(ASSETS_ZIP)
    vitems = {}
    for n in az.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            vitems[os.path.basename(n)[:-5]] = n
    vcommon = set(n for n in az.namelist() if n.startswith("Common/"))
    for t, i in enumerate(LAN_IDS):
        node = json.loads(fn_["Server/Item/Items/Utility/%s.json" % i])
        bt = json.loads(az.read(vitems[LAN_LOOKS[t]]).decode("utf-8-sig"))["BlockType"]
        van = "Common/" + bt["CustomModelTexture"][0]["Texture"]
        ours = "Common/" + node["Texture"]
        vb, ob = az.read(van), fn_.get(ours)
        check(ob is not None and ob == vb, "T1 %s: %s = %s byte for byte (%s bytes)" % (i, ours, van, None if ob is None else len(ob)))
        check(ob is not None and ob[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", ob[16:24]) == struct.unpack(">II", vb[16:24]),
              "T2 %s: a PNG of the vanilla size %s" % (i, struct.unpack(">II", vb[16:24])))
        check(ours not in vcommon and node["Texture"].startswith("Items/SkyyAccessories/"), "T3 %s: our own item path, not a vanilla file" % i)
        check(node["Model"] == bt["CustomModel"] and "Common/" + node["Model"] in vcommon, "T4 %s: the model is still the vanilla %s" % (i, node["Model"]))
    blk = []
    for n, b in fn_.items():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            tx = str(json.loads(b).get("Texture", ""))
            if tx.startswith("Blocks/") or (tx and "Common/" + tx not in vcommon and "Common/" + tx not in fn_):
                blk.append((n, tx))
    check(not blk, "T5 no item of the jar uses a Blocks/ texture, every Texture resolves (vanilla or the jar): %s" % blk[:4])
    old_blk = sorted(os.path.basename(n)[:-5] for n, b in fo_.items() if n.startswith("Server/Item/Items/") and n.endswith(".json")
                     and str(json.loads(b).get("Texture", "")).startswith("Blocks/"))
    check(old_blk == sorted(LAN_IDS), "T6 control: 0.5.10 had exactly the 4 Lantern items on Blocks/ textures (the 4 client lines): %s" % old_blk)
    print("T. 4 Lantern textures = the vanilla pixels at our item path; no Blocks/ texture left (0.5.10 had %d)" % len(old_blk))

    # ---------------- L. start twice on a scratch copy of the live folder
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
        return
    J = lambda n, k="new": JClass(PKG + n, loader=L[k])
    lm = os.path.join(SCRATCH, "l-mods")
    dlive = os.path.join(lm, "Skyy_SkyyAccessories")
    shutil.copytree(LIVE, dlive)
    before0 = snap(dlive)
    notes = []
    for rnd in range(2):
        J("AccStore").DIR = Paths.get(os.path.join(dlive, "bags"))
        J("AccCfg").FILE = Paths.get(os.path.join(dlive, "config.properties"))
        m51 = str(J("AccCfg").migrate051())
        m55 = str(J("AccCfg").migrate055())
        cs = str(J("AccCfg").load(True))
        J("AccNotice").FILE = Paths.get(os.path.join(dlive, "notices.properties"))
        J("AccNotice").load()
        J("AccLantern").pubLamp()
        J("CfgPub").start(Paths.get(lm), None)
        J("CfgPub").shutdown()
        notes.append((m51, m55, cs[:90], bool(J("AccDefs").LAN_HELMET), str(BR.get("acc:lamp"))))
    after = snap(dlive)
    chg = sorted(k for k in set(before0) | set(after) if before0.get(k) != after.get(k))
    check(not chg, "L two starts on a copy of the live data: no file changed (%d files) %s" % (len(before0), chg[:4]))
    print("L. two starts on the live copy: %d files unchanged; %s" % (len(before0), notes[-1]))
    BR.clear()


# ============================================================================================================== V (0.5.8)
def run_v():
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

    def pwalk(x):
        if isinstance(x, dict):
            if x.get("Type") == "OpenCustomUI" and isinstance(x.get("Page"), dict):
                pages.add(x["Page"]["Id"])
            for v in x.values():
                pwalk(v)
        elif isinstance(x, list):
            for v in x:
                pwalk(v)
    for n in zj.namelist():
        if n.startswith("Server/") and n.endswith(".json"):
            pwalk(json.loads(zj.read(n)))
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
    check(IPA.getAssetMap().getAsset("Block") is not None and ITEM.getAssetMap().getAssetMap().size() > 1000,
          "V: the vanilla Block set and the vanilla items (%d) are in the real stores" % ITEM.getAssetMap().getAssetMap().size())
    # ---- THE JAR
    pack_name = "Skyy:%s SkyyAccessories" % VERSION
    add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    bad = [r for r in rec if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:12]:
        print("   V:", r[0], r[1][:500].replace(chr(10), " / "))
    check(not fail and not bad, "V: the %s jar loads into the real stores: no failed store (%s), no SEVERE / WARNING line (%d)" % (VERSION, fail, len(bad)))
    jar_items = sorted(os.path.basename(n)[:-5] for n in zj.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    in_store = sorted(str(k) for k in ITEM.getAssetMap().getKeysForPack(pack_name))
    check(in_store == jar_items, "V: every one of the jar's %d items is in the Item store from this pack (%d): %s"
          % (len(jar_items), len(in_store), sorted(set(jar_items) ^ set(in_store))[:4]))
    node = json.loads(zj.read("Server/Item/Items/Utility/Skyy_Accessory_Bag.json"))
    it = ITEM.getAssetMap().getAsset("Skyy_Accessory_Bag")
    vals = {"Model": str(it.getModel()), "Texture": str(jf(ITEM, "texture").get(it)), "Icon": str(jf(ITEM, "icon").get(it))}
    try:
        it.toPacket()
        pk = True
    except Exception as e:
        pk = str(e)[:150]
    check(all(vals[k] == node[k] for k in vals) and jf(ITEM, "animation").get(it) is None and pk is True,
          "V: the Accessory Bag in the store = the jar's Model / Texture / Icon, no item animation, toPacket() works: %s %s" % (vals, pk))
    print("V. %s loaded into the real asset stores: 0 failed stores, 0 SEVERE / WARNING; %d items; the Accessory Bag look in the store"
          % (VERSION, len(in_store)))
    # ---- 0.5.11: the four Lantern items in the real Item store carry OUR texture (an item path in this jar) and the vanilla model
    lan_rows = []
    for t_, lid in enumerate(LAN_IDS):
        ln_ = json.loads(zj.read("Server/Item/Items/Utility/%s.json" % lid))
        li_ = ITEM.getAssetMap().getAsset(lid)
        tex_ = None if li_ is None else str(jf(ITEM, "texture").get(li_))
        ptex, pk_ = None, None
        try:
            pkt = li_.toPacket()
            pk_ = True
            for fn_ in ("texture",):
                try:
                    ptex = str(jf(pkt.getClass(), fn_).get(pkt))
                except Exception:
                    pass
        except Exception as e:
            pk_ = str(e)[:150]
        lan_rows.append((lid, tex_, ptex))
        check(li_ is not None and tex_ == LAN_TEX[t_] == ln_["Texture"] and str(li_.getModel()) == ln_["Model"] and pk_ is True and
              ptex == LAN_TEX[t_] and ("Common/" + tex_) in zj.namelist(),
              "V: %s in the store: Texture %s (packet %s) = our jar file, Model %s, toPacket %s" % (lid, tex_, ptex, li_ and li_.getModel(), pk_))
    print("V. the Lantern items in the store: %s" % "; ".join("%s -> %s" % (a, b) for a, b, _c in lan_rows))
    # ---- NEGATIVE CONTROLS (one-file packs in scratch): the validators really run
    base = dict(node)
    base.pop("Recipe", None)
    base.pop("Interactions", None)

    def item_with(**kv):
        d = json.loads(json.dumps(base))
        d.update(kv)
        return json.dumps(d)
    lan_base = json.loads(zj.read("Server/Item/Items/Utility/%s.json" % LAN_IDS[0]))
    lan_base.pop("Recipe", None)
    ctl = [
        ("Lantern texture file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Lantern.json",
         json.dumps(dict(lan_base, Texture="Items/SkyyAccessories/SkyyTestCtl_NoSuchLantern.png")), "SkyyTestCtl_NoSuchLantern.png", True),
        ("one-entry Parallel", "Server/Item/Interactions/SkyyTestCtl/SkyyTestCtl_Parallel.json",
         json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple", "RunTime": 0.1}]}]}}),
         "Array size is invalid", True),
        ("Model file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Model.json", item_with(Model="Items/SkyyAccessories/SkyyTestCtl_NoSuch.blockymodel"),
         "SkyyTestCtl_NoSuch.blockymodel", True),
        ("Texture file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Tex.json", item_with(Texture="Items/SkyyAccessories/SkyyTestCtl_NoSuchT.png"),
         "SkyyTestCtl_NoSuchT.png", True),
        ("Icon file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Icon.json", item_with(Icon="Icons/ItemsGenerated/SkyyTestCtl_NoSuchI.png"),
         "SkyyTestCtl_NoSuchI.png", True),
    ]
    caught = {}
    for i, (what, path, text, needle, must) in enumerate(ctl):
        zp = os.path.join(SCRATCH, "v-ctl%d.jar" % i)
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr(path, text)
        f_, r_ = loadpack(zp, "Skyy:test ctl%d" % i, False)
        hit = [r for r in r_ if r[0] in ("SEVERE", "WARNING") and needle in r[1]]
        caught[what] = ("refused (SEVERE)" if any(r[0] == "SEVERE" for r in hit) else "warned" if hit else "NOT caught") + (" + store failed" if f_ else "")
        if must:
            check(hit and any(r[0] == "SEVERE" for r in hit), "V CONTROL: %s must be refused by the engine validator: %s" % (what, caught[what]))
    print("V. negative controls: " + "; ".join("%s -> %s" % (k, v) for k, v in caught.items()))


def main():
    if "--child-v" in sys.argv:
        try:
            run_v()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("V harness error: %s" % e)
        print("V: %d ok, %d fail(s)" % (OKS[0], len(FAILS)))
        for f in FAILS[:20]:
            print("  FAIL", f)
        return 1 if FAILS else 0
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (tools/accessories_0_5_11_patch.py + build_skyyaccessories_0.5.11.py)")
            return 1
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    import subprocess
    sys.stdout.flush()
    env = dict(os.environ)
    env.pop("JAVA_TOOL_OPTIONS", None)
    print("---- JVM 2: the engine asset validators (V)")
    sys.stdout.flush()
    rcv = subprocess.call([sys.executable, os.path.abspath(__file__), "--child-v"] + sys.argv[1:], env=env, cwd=ROOT)
    if rcv:
        FAILS.append("V (the engine asset validators) failed - see above")
    else:
        OKS[0] += 1
    print("SkyyAccessories %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP and "--child-v" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
