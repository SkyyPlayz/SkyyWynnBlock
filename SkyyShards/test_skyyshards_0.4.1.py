"""Harness for SkyyShards 0.4.1 (REAL MODELS FOR THE 6 TOTEM MODIFIERS; tools/shards_0_4_1_patch.py) = the 0.4 harness's exec / live phases on
the 0.4.1 jar + C41 / T41 / ENG.
Build first: python tools/shards_0_4_1_patch.py && python SkyyShards/build_skyyshards_0.4.1.py

    python SkyyShards/test_skyyshards_0.4.1.py [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C41  compare  0.4 -> 0.4.1: no class added / removed; the only classes that differ hold the version text; non-class entries changed =
                the manifest + the 6 modifier item documents (each = its 0.4 document + Model / Texture / Scale only), added = the 6
                generated modifier textures; nothing else
  T41  assets   ASSET AUDIT: every item JSON in the jar names a Model + Texture (a block item: CustomModel + its textures) that exists in
                the jar or Assets.zip (= no "Missing model for item"); the 6 modifiers: the vanilla Life Essence model BY PATH (not in the
                jar), their own texture = a PNG the size of the vanilla Life Essence texture, recoloured (not the vanilla bytes), the
                vanilla item's Scale; icons unchanged
  ENG  THE ENGINE ASSET VALIDATORS (the SkyyFishing 0.1.2 harness's engine_boot: the vanilla pack store by store, then THE JAR as its own
                pack): no failed store; no SEVERE / WARNING line that names a modifier, a missing model or texture (the only lines left
                are the shard pages a bare JVM never registers); the 6 modifiers are in the Item store and their packets carry the model
  X / D the 0.4 harness's exec + live phases on this jar
  AA   engine-access audit
Scratch: tools/dev/scratch/fish018/shards (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.1"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fish018", "shards")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
_sp = importlib.util.spec_from_file_location("test_skyyshards_0_4", os.path.join(HERE, "test_skyyshards_0.4.py"))
T04 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T04)          # it sets HK.run_compare to its 0.3.2 -> 0.4 compare: replaced below
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
MODS = ["Wider", "Faster", "Replant", "Compost", "Storage", "RareFinder"]
MOD_JSON = ["Server/Item/Items/SkyyShards/Totems/Skyy_TotemMod_%s.json" % m for m in MODS]
MOD_TEX = ["Common/Items/SkyyShards/TotemMod_%s.png" % m for m in MODS]


def _png_size(b):
    assert b[:8] == b"\x89PNG\r\n\x1a\n"
    return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")


def run_compare41(out, jar, old_jar, pkg, expect, added, removed=()):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), [], "C41: no class added")
    K.eq(sorted(set(na) - set(nb)), [], "C41: no class removed")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    import re

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
            return str(b_.getModifiers()) + "\n" + "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    kit = lambda x: re.sub(r"skyyui [0-9.]+ [0-9a-f]{12}", "skyyui KIT", x)   # the ready line names the UI kit it was built with (1.4 -> 1.5)
    differ, other = [], []
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if not dd:
            continue
        differ.append(cn[len(pkg):])
        for k in dd:
            if k not in ma or k not in mb or kit(mb[k].replace("0.4.1", "0.4")) != kit(ma[k]):
                other.append((cn[len(pkg):], k))
    print("C41. classes that differ: %s" % differ)
    K.check(differ and not other, "C41: the classes that differ (%s) differ ONLY in the version text 0.4 -> 0.4.1 (+ the kit id in the ready line): other changes %s" % (differ, other[:5]))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    K.eq(sorted(eb - ea), sorted(MOD_TEX), "C41: added non-class entries = the 6 generated modifier textures")
    K.eq(sorted(ea - eb), [], "C41: no non-class entry removed")
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    K.eq(changed, sorted(["manifest.json"] + MOD_JSON), "C41: changed = the manifest + the 6 modifier item documents")
    for n, t in zip(MOD_JSON, MOD_TEX):
        a, b = json.loads(za.read(n)), json.loads(zb.read(n))
        add = dict((k, b.pop(k)) for k in ("Model", "Texture", "Scale") if k in b)
        K.check(a == b and add.get("Texture") == t[len("Common/"):] and add.get("Model", "").endswith(".blockymodel"),
                "C41: %s = its 0.4 document + Model / Texture / Scale only: %s" % (os.path.basename(n), add))
    K.save()


HK.run_compare = run_compare41


def run_assets41(out, jar, scratch, _home):
    K = HK.Child(out)
    az = zipfile.ZipFile(AZ_PATH)
    azn = set(az.namelist())
    jz = zipfile.ZipFile(jar)
    jn = set(jz.namelist())
    have = lambda p: ("Common/" + p) in jn or ("Common/" + p) in azn
    bad, n = [], 0
    for nm in sorted(jn):
        if not (nm.startswith("Server/Item/Items/") and nm.endswith(".json")):
            continue
        n += 1
        d = json.loads(jz.read(nm).decode("utf-8-sig"))
        if "BlockType" in d:
            bt = d["BlockType"]
            texs = [t.get("Texture") for t in bt.get("CustomModelTexture", [])]
            if bt.get("DrawType") == "Model" and (not bt.get("CustomModel") or not have(bt["CustomModel"]) or not texs or not all(t and have(t) for t in texs)):
                bad.append((nm, "block", bt.get("CustomModel"), texs))
            continue
        if not d.get("Model") or not d.get("Texture") or not have(d["Model"]) or not have(d["Texture"]):
            bad.append((nm, d.get("Model"), d.get("Texture")))
    K.check(n > 30 and not bad, "T41 ASSET AUDIT: all %d item JSONs name a Model + Texture (blocks: CustomModel + textures) found in the jar or "
            "Assets.zip - no 'Missing model for item': %s" % (n, bad[:4]))
    le = json.loads(az.read([x for x in azn if x.endswith("/Ingredient_Life_Essence.json") and x.startswith("Server/Item/Items/")][0]).decode("utf-8-sig"))
    vt = az.read("Common/" + le["Texture"])
    for nm, t in zip(MOD_JSON, MOD_TEX):
        d = json.loads(jz.read(nm))
        tb = jz.read(t)
        K.check(d["Model"] == le["Model"] and ("Common/" + le["Model"]) not in jn and d["Texture"] == t[len("Common/"):] and t not in azn
                and _png_size(tb) == _png_size(vt) and tb != vt and d.get("Scale") == le.get("Scale", 1)
                and ("Common/" + d["Icon"]) in jn,
                "T41 %s: the vanilla Life Essence model by path, our recoloured texture (%dx%d, not the vanilla bytes), Scale %s, its icon"
                % (os.path.basename(nm), _png_size(tb)[0], _png_size(tb)[1], d.get("Scale")))
    K.save()


def run_eng(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    sp = importlib.util.spec_from_file_location("t012", os.path.join(ROOT, "SkyyFishing", "test_skyyfishing_0.1.2.py"))
    T12 = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(T12)
    T12.JAR, T12.SCRATCH, T12.VERSION = jar, os.path.join(scratch, "eng"), VERSION
    os.makedirs(T12.SCRATCH, exist_ok=True)
    T12._jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)
    # the shard pages, registered the way setup() does (OpenCustomUIInteraction.registerSimple -> PAGE_CODEC) before the assets load -
    # the 0.1.2 engine_boot registers only one page id (the fishing bench)
    from jpype import JImplements, JOverride
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
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
    ids = set()
    jz = zipfile.ZipFile(jar)
    for nm in jz.namelist():
        if nm.startswith("Server/") and nm.endswith(".json"):
            for part in jz.read(nm).decode("utf-8").split('"Page": {')[1:]:
                pid = part.split('"Id": "', 1)[1].split('"', 1)[0] if '"Id": "' in part else None
                if pid:
                    ids.add(pid)
    for pid in sorted(ids):
        OCUc.PAGE_CODEC.register(pid, CPSc.class_, BCc.builder(CPSc.class_, SupOf()).build())
    K.notes.append("ENG: shard pages registered first: %s" % sorted(ids))
    E = T12.engine_boot(K)
    bad = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING")]
    pages = ("SkyyShard", "SkyyTotemBench")
    ours = [r for r in bad if "TotemMod" in r[1] or ".blockymodel" in r[1] or ".png" in r[1]]
    other = [r for r in bad if r not in ours and not any(p in r[1] for p in pages)]
    for r in (ours + other)[:8]:
        print("   ENG:", r[0], r[1][:400].replace("\n", " / "))
    K.check(not ours and not other, "ENG: the 0.4.1 jar as a pack: no SEVERE / WARNING naming a modifier, a model or a texture (%d), no other line "
            "besides the shard pages a bare JVM does not register (%d); %d page lines" % (len(ours), len(other), len(bad) - len(ours) - len(other)))
    K.check("ItemType" not in str(E["fail"]) and "Item" not in [str(x) for x in E["fail"]], "ENG: the Item store did not fail (failed stores: %s)" % E["fail"])
    miss = []
    for m in MODS:
        it = E["ITEM"].getAssetMap().getAsset("Skyy_TotemMod_" + m)
        try:
            pk = it.toPacket() if it is not None else None
            mdl = str(pk.model) if pk is not None and pk.model is not None else None
        except Exception as e:
            mdl = "EXC %s" % str(e)[:100]
        if mdl is None or not mdl.endswith("Essence.blockymodel"):
            miss.append((m, mdl))
    K.check(not miss, "ENG: the 6 modifiers are in the Item store; their packets carry the Life Essence model: %s" % miss)
    K.notes.append("ENG failed stores (bare JVM): %s; page lines %d" % (E["fail"], len(bad)))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect={}, added=[],
           phases=[("assets41", run_assets41), ("eng", run_eng), ("exec", T04.run_exec), ("live", T04.run_live)], script=__file__,
           live=(os.path.join(T04.LIVE_DIR, "Skyy_SkyyShards"), "mods/Skyy_SkyyShards"))
