"""Bare-JVM harness for SkyyCollections 0.2.9 (tools/collections_0_2_9_patch.py; research/Bags-v2-Spec.md round 0; Skyy 2026-10-10:
"still have it upgrade from collection, but its based on the total number of items in that category you have collected.")
  coll:fn:catTotal {UUID, category} -> Long (cached per profile, updated on collect) + the sacks:v2 bag switch.

    python SkyyCollections/test_skyycollections_0.2.9.py [--jar <SkyyCollections-0.2.9.jar>] [--old <SkyyCollections-0.2.8.jar>]
                                                         [--dir <scratch>] [--live <Skyy_SkyyCollections folder>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), every jar in its own
class loader; a FRESH loader of a jar = one server start (static state empty, like a restart).
  A  every class of both jars loads, verifies and initialises
  B  class bytes 0.2.8 -> 0.2.9: the same classes + CollCat; every other class byte-identical / version-constants-only / only the
     DECLARED methods changed or added (CollUnlocks.compute0 = 0.2.8's compute, instruction for instruction); manifest Version / Name only
  E  engine-access audit: every engine (com.hypixel) reference new in 0.2.9 resolved by reflection against HytaleServer.jar
  C  the page id in the ready line == COLL_PAGE_CHECKED == the page the kit makes now (the page is 0.2.8's)
  T  coll:fn:catTotal on the real default registry: every category == an independent Python model built from the COLLECTION sums
     (CollStore.sum per collection, spec 2.1 by collection id: Fishing = Raw Fish, Smithing = the 3 hides + 4 scraps + the metal ores,
     Crystal in Mining); argument shapes (either order, UUID String, case / spaces, junk -> null, never throws); no registry / an
     unreadable counts file -> null; the cache (one build, then none; addLocked updates every category of the item: ore = Mining +
     Smithing, hide = Combat + Smithing, fish = Fishing, crystal = Mining, wood = Foraging; a non-registry item, a negative change, a
     registry reload, another CollData object each drop / rebuild correctly; String values; saturation at Long.MAX_VALUE); the
     plugin's setup puts and shutdown removes coll:fn:catTotal; PROFILE SWITCH (profile:fn:key flips -> the other profile's totals,
     each cached on its own, back again)
  K  sacks:v2 absent vs present (Boolean TRUE, String "true", Boolean FALSE, junk): recipesAt, compute (tiers, kept Mining bags),
     rewardText / rewardLines (chat), coll:fn:where, the coin-unlock text, the collection page tier rows, the Unlocked and Locked
     recipe lists; absent = 0.2.8 exactly (compute == the 0.2.8 jar's compute on the same files), present = absent minus every bag
  V  CollSaver.v2Tick / run(): first look absent -> no republish; key set -> coll:recipes drops the bags + the epoch bumps; key gone ->
     the bags come back; no change -> nothing
  S  START TWICE on a scratch COPY of Skyy's live Skyy_SkyyCollections folder (the plugin's setup order, fresh loader each start):
     0.2.9 writes nothing (the 0.2.8 jar on a second copy neither), every profile's 0.2.9 unlock set (key absent) == 0.2.8's, key
     present == 0.2.8's minus bags, catTotal of every live profile (switching profile:fn:key across them) == the model; the live
     folder untouched
Nothing outside the scratch folder is written (default tools/dev/scratch/coll029/harness, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.9", "0.2.8"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "coll029", "harness")))
assert SCRATCH.lower().startswith(SCRATCH_ROOT.lower() + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
BAGCATS = ["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]
SMITH_IDS = {"HideLight", "HideMedium", "HideHeavy", "Linen", "Wool", "Shadoweave", "Cindercloth",
             "Copper", "Iron", "Silver", "Gold", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"}
BAG_RE = re.compile(r"(Normal|Unique|Rare|Legendary) (Mining|Foraging|Farming|Combat|Smithing) Bag|Mythic Omni Bag")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def kit_page():
    import skyyui as SUI
    SUI.verify(quiet=True)
    text = open(SCRIPT, encoding="utf8").read()
    a, b = text.index("# ---- COLL PAGE BLOCK START"), text.index("# ---- COLL PAGE BLOCK END")
    data = None
    for n in ast.parse(text).body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "UI_DATA_COLORS" for t in n.targets):
            data = ast.literal_eval(n.value)
    ns = {"SUI": SUI, "re": re, "KIT_ID": SUI.kit_id(), "UI_DATA_COLORS": data}
    exec(compile(text[a:b], SCRIPT, "exec"), ns)
    return SUI, ns


def script_const(name):
    text = open(SCRIPT, encoding="utf8").read()
    for n in ast.parse(text).body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return ast.literal_eval(n.value)
    return None


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


def classes(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n[:-6].replace("/", "."), z.read(n)) for n in z.namelist() if n.endswith(".class"))
    z.close()
    return out


def manifest(jar):
    z = zipfile.ZipFile(jar)
    m = json.loads(z.read("manifest.json").decode("utf8"))
    z.close()
    return m


def snap(dd):
    out = {}
    for root, _ds, fs in os.walk(dd):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, dd).replace(os.sep, "/")] = open(p, "rb").read()
    return out


ID_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{")


def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    SUI, K = kit_page()
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    CB = {"old": classes(OLD), "new": classes(JAR)}

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

    # ---------------- B. class bytes
    old, new = CB["old"], CB["new"]
    check(sorted(set(new) - set(old)) == [PKG + "CollCat"] and not (set(old) - set(new)),
          "B. the same classes + CollCat: %s" % sorted(set(old) ^ set(new)))
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, rows = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            rows.append((pos, re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp)))))
        idx = dict((p, i) for i, (p, _t) in enumerate(rows))
        idx[int(ca.getCodeLength())] = len(rows)
        out = []
        for _p, t in rows:
            t = re.sub(r"^ldc_w ", "ldc ", t)
            mm = re.match(r"^(if\w*|goto(?:_w)?|jsr(?:_w)?) (\d+)$", t)
            if mm:
                t = "%s @%d" % (mm.group(1), idx[int(mm.group(2))])
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%d @%d @%d %s" % (idx[et.startPc(i)], idx[et.endPc(i)], idx[et.handlerPc(i)], cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        ci = c.getClassInitializer()
        if ci is not None:
            out["<clinit>"] = code_of(ci)
        return out

    def vonly(a, b):
        return len(a) == len(b) and all(x == y or x.replace(OLD_VERSION, VERSION) == y for x, y in zip(a, b))

    DECLARED = {
        "CollReg": ["recipesAt"],
        "CollUnlocks": ["compute"],
        "CollStore": ["addLocked"],
        "CollFn": ["apply"],
        "CollSaver": ["run"],
        "CollKit": ["bagLadder"],   # fixer: Server Setup Magic Bags rows while sacks:v2
        "SkyyCollectionsPlugin": ["setup", "shutdown"],
    }
    ADDED = {
        "CollUnlocks": ["compute0(Lcom/skyy/collections/CollData;)Ljava/util/TreeSet;"],
        "CollStore": ["catTotal(Ljava/lang/String;Lcom/skyy/collections/CollData;Lcom/skyy/collections/RegData;I)J"],
        "CollFn": ["catTotal(Ljava/lang/Object;)Ljava/lang/Object;"],
        "CollSaver": ["v2Tick()V"],
    }
    kinds = {}
    MO, MN = {}, {}
    for n in sorted(set(old) & set(new)):
        short = n[len(PKG):]
        if old[n] == new[n]:
            kinds[short] = "identical"
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        if len(co) == len(cn):
            rebuilt, okv = new[n], True
            for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
                if t0 == t1:
                    continue
                if t0.decode("utf8").replace(OLD_VERSION, VERSION) != t1.decode("utf8"):
                    okv = False
                    break
                rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
            if okv and rebuilt == old[n]:
                kinds[short] = "version constants"
                continue
        po, pn = ct(old[n]), ct(new[n])
        fo = set(str(f.getName()) for f in po.getDeclaredFields())
        fn = set(str(f.getName()) for f in pn.getDeclaredFields())
        check(fo == fn, "B. %s: fields added / gone: %s" % (short, sorted(fo ^ fn)))
        mo, mn = methods(po), methods(pn)
        MO[short], MN[short] = mo, mn
        check(not (set(mo) - set(mn)) and sorted(set(mn) - set(mo)) == sorted(ADDED.get(short, [])),
              "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        vers = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and vonly(mo[k], mn[k]))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        kinds[short] = "methods %s + version only %s" % (changed, vers)
    for k in DECLARED:
        check(k in kinds and kinds[k].startswith("methods"), "B. %s is one of the changed classes: %s" % (k, kinds.get(k)))
    c0 = "compute(Lcom/skyy/collections/CollData;)Ljava/util/TreeSet;"
    check(MO["CollUnlocks"][c0] == MN["CollUnlocks"]["compute0(Lcom/skyy/collections/CollData;)Ljava/util/TreeSet;"],
          "B. CollUnlocks.compute0 is 0.2.8's compute, instruction for instruction")
    mo_, mn_ = manifest(OLD), manifest(JAR)
    check(mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyyCollections"
          and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) == dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")),
          "B. manifest: only Version / Name changed")
    setup_code = " ".join(MN["SkyyCollectionsPlugin"]["setup()V"])
    shut_code = " ".join(MN["SkyyCollectionsPlugin"]["shutdown()V"])
    check(re.search(r'ldc "coll:fn:catTotal" new com\.skyy\.collections\.CollFn dup ldc "catTotal" invokespecial', setup_code.replace("\n", " ")) is not None
          or ('"coll:fn:catTotal"' in setup_code and '"catTotal"' in setup_code), "B. setup() puts coll:fn:catTotal = new CollFn(\"catTotal\")")
    check('"coll:fn:catTotal"' in shut_code and "remove" in shut_code, "B. shutdown() removes coll:fn:catTotal")
    check(re.search(r"CollCat\W+v2", setup_code) is not None and "no collection tier unlocks these Magic Bags" in setup_code,
          "B. setup(): the Magic Bags gaps warning is guarded by CollCat.v2() (fixer)")
    ident = sorted(k for k, v in kinds.items() if v == "identical")
    print("B. %d classes byte-identical; version constants only: %s; method-level: %s" % (
        len(ident), sorted(k for k, v in kinds.items() if v == "version constants"),
        dict((k, v) for k, v in kinds.items() if v.startswith("methods"))))

    # ---------------- E. engine-access audit
    def engine_refs(blobs):
        out = set()
        for _n, b in blobs.items():
            cf = ct(b).getClassFile()
            cp = cf.getConstPool()
            for i in range(1, int(cp.getSize())):
                try:
                    tag = int(cp.getTag(i))
                except Exception:
                    continue
                if tag in (10, 11):
                    kind = "M"
                    cl = str(cp.getMethodrefClassName(i)) if tag == 10 else str(cp.getInterfaceMethodrefClassName(i))
                    nm = str(cp.getMethodrefName(i)) if tag == 10 else str(cp.getInterfaceMethodrefName(i))
                    ty = str(cp.getMethodrefType(i)) if tag == 10 else str(cp.getInterfaceMethodrefType(i))
                elif tag == 9:
                    kind, cl, nm, ty = "F", str(cp.getFieldrefClassName(i)), str(cp.getFieldrefName(i)), str(cp.getFieldrefType(i))
                else:
                    continue
                if cl.startswith("com.hypixel."):
                    out.add((kind, cl, nm, ty))
        return out
    eo, en = engine_refs(old), engine_refs(new)
    added = sorted(en - eo)
    MH = JClass("java.lang.invoke.MethodType")
    for kind, cl, nm, ty in added:
        c_ = Cls.forName(cl, False, sysl)
        found = False
        k_ = c_
        while k_ is not None and not found:
            if kind == "M":
                for m in list(k_.getDeclaredMethods()) + list(k_.getDeclaredConstructors()):
                    nm_ = "<init>" if m.getClass().getSimpleName() == "Constructor" else str(m.getName())
                    if nm_ != nm:
                        continue
                    rt = JClass("java.lang.Void").TYPE if nm_ == "<init>" else m.getReturnType()
                    if str(MH.methodType(rt, m.getParameterTypes()).toMethodDescriptorString()) == ty:
                        found = True
            else:
                for f in k_.getDeclaredFields():
                    if str(f.getName()) == nm:
                        found = True
            k_ = k_.getSuperclass()
        check(found, "E. engine reference resolves: %s %s.%s%s" % (kind, cl, nm, ty))
    cat_refs = engine_refs({PKG + "CollCat": new[PKG + "CollCat"]})
    print("E. engine-access audit: %d engine references new in 0.2.9 (all resolved): %s; CollCat references %d engine members"
          % (len(added), ["%s.%s" % (c.split(".")[-1], n) for _k, c, n, _t in added], len(cat_refs)))
    check(not cat_refs, "E. CollCat uses no engine class (plain java.* + this mod): %s" % sorted(cat_refs))

    # ---------------- C. page id
    chk = script_const("COLL_PAGE_CHECKED")
    plug = new[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mm = re.search(r"0\.2\.9 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug)
    plug_old = old[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mo2 = re.search(r"0\.2\.8 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug_old)
    check(mm is not None and mm.group(1) == chk and K["COLL_PAGE_ID"] == chk and mo2 is not None and mo2.group(1) == chk,
          "C. page id: ready line %s == checked %s == the kit now %s == 0.2.8's %s" % (mm and mm.group(1), chk, K["COLL_PAGE_ID"], mo2 and mo2.group(1)))
    check(MO["CollPage"] == MN["CollPage"] if "CollPage" in MO else kinds.get("CollPage") in ("identical", "version constants"),
          "C. CollPage is 0.2.8's: %s" % kinds.get("CollPage"))

    # ---------------- the 0.2.9 world
    Paths, Long, HashMap = JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.util.HashMap")
    Bool, JString, UUID = JClass("java.lang.Boolean"), JClass("java.lang.String"), JClass("java.util.UUID")
    System = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    @JImplements("java.util.function.Function")
    class KeyFn:
        def __init__(self):
            self.key = None

        @JOverride
        def apply(self, u):
            return self.key

    KF = KeyFn()

    def jc(name, k="new"):
        return JClass(PKG + name, loader=L[k])

    def jfield(c_, name):
        f = c_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    UID = UUID.fromString("00000000-0000-0000-0000-0000000000c9")
    US = str(UID)

    def pref():
        p = U.allocateInstance(PR.class_)
        jfield(PR.class_, "uuid").set(p, UID)
        return p

    def recipes_from_rewards(Reg):
        R = Reg.D
        rec = HashMap()
        for c in range(R.n):
            for t in range(1, int(Reg.maxTier(R, c)) + 1):
                toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
                if toks is None:
                    continue
                ids = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
                if ids:
                    rec.put("%d.%d" % (c, t), JArray(JString)(ids))
        Reg.RECIPES = rec
        Reg.VALIDATED = True

    Reg, Store, Util, Unl, Cat, Fn = jc("CollReg"), jc("CollStore"), jc("CollUtil"), jc("CollUnlocks"), jc("CollCat"), jc("CollFn")
    Page, Saver, Byp = jc("CollPage"), jc("CollSaver"), jc("CollBypass")
    wbase = os.path.join(SCRATCH, "world", "mods", "Skyy_SkyyCollections")
    os.makedirs(wbase)
    Reg.BASE = Paths.get(wbase)
    Store.DIR = Paths.get(wbase).resolve("counts")
    lmsg = str(Reg.loadAll())
    recipes_from_rewards(Reg)
    R = Reg.D
    for c in range(R.n):
        R.iconOk[c] = True
    BYID = dict((str(R.id[c]), c) for c in range(R.n))
    COB, IRON = BYID["Cobblestone"], BYID["Iron"]
    CATS = [str(x) for x in Reg.CATS]

    def thr(c, t):
        return int(Reg.threshold(R, c, t))

    def mx(c):
        return int(Reg.maxTier(R, c))

    def write_counts(key, items, meta=None, folder=None):
        cd = os.path.join(folder or wbase, "counts")
        os.makedirs(cd, exist_ok=True)
        ls = ["_schema=2"] + ["%s=%d" % kv for kv in sorted(items.items()) if kv[1]] + ["%s=%d" % kv for kv in sorted((meta or {}).items())]
        open(os.path.join(cd, key + ".properties"), "w").write("\n".join(ls) + "\n")

    def reset_store():
        Store.DATA.clear()
        Store.BROKEN.clear()
        Store.DIRTY.clear()
        Cat.CACHE.clear()

    def model(Reg_, Store_, d_):
        """spec 2.1 by COLLECTION (independent of CollCat's per-item prefix rules): sum of CollStore.sum of each category's collections"""
        R_ = Reg_.D
        t = dict((c, 0) for c in BAGCATS)
        for c in range(R_.n):
            cid, cat = str(R_.id[c]), str(Reg_.CATS[R_.cat[c]])
            sm = int(Store_.sum(d_, R_, c))
            if cid == "RawFish":
                t["Fishing"] += sm
            elif cid == "Crystal":
                t["Mining"] += sm
            else:
                t[cat] += sm
            if cid in SMITH_IDS:
                t["Smithing"] += sm
        return t

    def ct_(u, cat):
        return Fn.catTotal(JArray(JObject)([u, cat]))

    def totals(u):
        return dict((c, None if ct_(u, c) is None else int(ct_(u, c))) for c in BAGCATS)

    # ---------------- T. coll:fn:catTotal
    import random
    rnd = random.Random(29)
    allc = {}
    for c in range(R.n):
        for it in [str(x) for x in R.items[c]]:
            allc[it] = rnd.randint(0, 5000) if rnd.random() < 0.8 else 0
    # the spec's own items get a count for sure
    for it in ("Food_Fish_Raw", "Food_Fish_Raw_Epic", "Ingredient_Crystal_Blue", "Ingredient_Hide_Heavy", "Ingredient_Fabric_Scrap_Wool",
               "Ore_Copper", "Ore_Mithril", "Rock_Stone_Cobble", "Wood_Oak_Trunk", "Plant_Crop_Wheat_Item", "Ingredient_Bone_Fragment"):
        if it in allc:
            allc[it] = rnd.randint(1, 5000)
    check(all(i in allc for i in ("Food_Fish_Raw", "Ore_Copper", "Ingredient_Hide_Light", "Ingredient_Fabric_Scrap_Linen")), "T0 registry has the spec items")
    check(any(i.startswith("Ingredient_Crystal_") for i in allc), "T0 registry has crystals")
    reset_store()
    write_counts(US, allc)
    d = Store.data(UID)
    want = model(Reg, Store, d)
    got = totals(UID)
    check(got == want, "T1 every category == the collection sums (spec 2.1): got %s want %s" % (got, want))
    check(all(isinstance(ct_(UID, c), JClass("java.lang.Long")) or type(ct_(UID, c)).__name__ in ("Long", "JLong", "int") for c in BAGCATS),
          "T1 the answer is a java.lang.Long")
    rf = int(Store.sum(d, R, BYID["RawFish"]))
    check(want["Fishing"] == rf and rf > 0 and bool(R.hidden[BYID["RawFish"]]), "T1 Fishing = the hidden Raw Fish collection (%d)" % rf)
    smith = sum(int(Store.sum(d, R, BYID[i])) for i in SMITH_IDS)
    check(want["Smithing"] == smith and smith > 0, "T1 Smithing = hides + scraps + metal ores (%d)" % smith)
    check(int(ct_(UID, "Mining")) >= int(Store.sum(d, R, BYID["Crystal"])) > 0, "T1 crystals count in Mining")
    # argument shapes
    b0 = int(Cat.BUILDS)
    m = int(want["Mining"])
    check(int(Fn.catTotal(JArray(JObject)(["mining", UID]))) == m and int(Fn.catTotal(JArray(JObject)([US, "  MINING "]))) == m
          and int(Fn.catTotal(JArray(JObject)([" " + US + " ", "Mining"]))) == m, "T2 either order, UUID String, case and spaces")
    junk = [None, "x", JArray(JObject)([]), JArray(JObject)([UID]), JArray(JObject)([UID, "Nope"]), JArray(JObject)([UID, JObject(5, JClass("java.lang.Integer"))]),
            JArray(JObject)(["Mining", "not-a-uuid"]), JArray(JObject)([None, "Mining"]), JArray(JObject)([UID, None]), JArray(JObject)(["Mining", "Fishing"])]
    res = []
    for a_ in junk:
        try:
            res.append(Fn.catTotal(a_))
        except Exception as e:
            res.append("THREW %s" % e)
    check(all(r is None for r in res), "T2 junk arguments -> null, never a throw: %s" % res)
    fnobj = Fn("catTotal")
    check(int(fnobj.apply(JArray(JObject)([UID, "Smithing"]))) == want["Smithing"] and fnobj.apply("junk") is None and fnobj.apply(None) is None,
          "T2 the bridge Function (CollFn(\"catTotal\").apply) answers and never throws")
    check(int(Cat.BUILDS) == b0, "T3 cached: the answers above built nothing new (%d -> %d)" % (b0, int(Cat.BUILDS)))
    # no registry -> null
    keepD = Reg.D
    Reg.D = None
    check(ct_(UID, "Mining") is None, "T2 no registry -> null")
    Reg.D = keepD
    # unreadable counts file -> null (a directory where the file should be)
    bad = UUID.fromString("00000000-0000-0000-0000-0000000000ba")
    os.makedirs(os.path.join(wbase, "counts", str(bad) + ".properties"))
    check(ct_(bad, "Mining") is None, "T2 a counts file that cannot be read -> null")
    shutil.rmtree(os.path.join(wbase, "counts", str(bad) + ".properties"))
    # a player with no file -> 0 everywhere
    nof = UUID.fromString("00000000-0000-0000-0000-0000000000bb")
    check(totals(nof) == dict((c, 0) for c in BAGCATS), "T2 a new player -> 0 in every category")
    # cache updated on collect: addLocked (the one path every counted item takes)
    key = str(Util.pkey(UID))
    before = totals(UID)
    b1 = int(Cat.BUILDS)
    adds = [("Ore_Copper", 7, {"Mining", "Smithing"}), ("Ingredient_Hide_Light", 5, {"Combat", "Smithing"}),
            ("Food_Fish_Raw_Rare", 3, {"Fishing"}), ("Ingredient_Crystal_Blue", 11, {"Mining"}), ("Wood_Oak_Trunk", 13, {"Foraging"}),
            ("Plant_Crop_Wheat_Item", 17, {"Farming"}), ("Ingredient_Fabric_Scrap_Cindercloth", 2, {"Combat", "Smithing"}),
            ("Ingredient_Bone_Fragment", 19, {"Combat"})]
    for it, q, cats in adds:
        c = int(R.itemColl.get(it))
        Store.addLocked(d, key, R, c, it, Long(q))
        nowt = totals(UID)
        check(all(nowt[x] == before[x] + (q if x in cats else 0) for x in BAGCATS), "T3 collect %d %s -> +%d in %s only: %s -> %s" % (q, it, q, sorted(cats), before, nowt))
        before = nowt
    check(int(Cat.BUILDS) == b1, "T3 every collect updated the cache, no rebuild (%d -> %d)" % (b1, int(Cat.BUILDS)))
    check(totals(UID) == model(Reg, Store, d), "T3 the updated cache == a full recount")
    # an item outside the registry: nothing changes, entry kept
    Store.addLocked(d, key, R, COB, "Skyy_Not_A_Registry_Item", Long(5))
    check(totals(UID) == before and int(Cat.BUILDS) == b1, "T3 a non-registry item changes no total, keeps the cache")
    # a negative change drops the entry -> rebuilt, still exact
    Store.addLocked(d, key, R, COB, "Rock_Stone_Cobble", Long(-4))
    check(Cat.CACHE.get(key) is None, "T4 a negative change drops the cached totals")
    check(totals(UID) == model(Reg, Store, d) and int(Cat.BUILDS) == b1 + 1, "T4 rebuilt once, exact")
    # addLocked before any catTotal of a key (no entry) -> nothing cached, no error
    k2 = "nocache-key"
    d2 = jc("CollData")()
    Store.addLocked(d2, k2, R, COB, "Rock_Stone_Cobble", Long(3))
    check(Cat.CACHE.get(k2) is None and int(d2.items.get("Rock_Stone_Cobble")) == 3, "T4 collect with no cached totals: count kept, nothing cached")
    # another CollData object under the same key -> rebuilt from it; addLocked with a stale RegData -> dropped
    b2 = int(Cat.BUILDS)
    check(int(Store.catTotal(key, d2, R, 0)) == 3 and int(Cat.BUILDS) == b2 + 1, "T4 another CollData under the key -> rebuilt from it")
    Store.addLocked(d2, key, R, COB, "Rock_Stone_Cobble", Long(1))
    check(int(Store.catTotal(key, d2, R, 0)) == 4 and int(Cat.BUILDS) == b2 + 1, "T4 then updated on collect")
    Reg.loadAll()
    recipes_from_rewards(Reg)
    R2 = Reg.D
    check(R2 is not None and not R2.equals(R), "T5 reload makes a new RegData")
    Store.addLocked(d2, key, R2, COB, "Rock_Stone_Cobble", Long(1))
    check(Cat.CACHE.get(key) is None, "T5 a collect against the reloaded registry drops the old cache entry")
    reset_store()
    write_counts(US, allc)
    d = Store.data(UID)
    b3 = int(Cat.BUILDS)
    check(totals(UID) == model(Reg, Store, d) and int(Cat.BUILDS) == b3 + 1, "T5 after the reload: exact, built once")
    R = Reg.D
    for c in range(R.n):
        R.iconOk[c] = True
    # a stale entry for the old RegData is rebuilt (entry RegData != the live one)
    Cat.CACHE.put(key, JArray(JObject)([keepD, d, JArray(JClass("long"))([1, 1, 1, 1, 1, 1])]))
    check(totals(UID) == model(Reg, Store, d), "T5 an entry of an old registry is rebuilt, never answered")
    # String values (CollStore.sumMap's rule) + saturation at Long.MAX_VALUE
    d3 = jc("CollData")()
    d3.items.put("Rock_Stone_Cobble", JString("12"))
    d3.items.put("Rock_Stone_Cobble_Mossy", JString("oops"))
    t3 = Cat.compute(d3, R)
    check(int(t3[0]) == 12, "T6 a String count is read, a bad String is 0: %s" % list(t3))
    d3.items.put("Rock_Stone_Cobble", Long(Long.MAX_VALUE - 5))
    d3.items.put("Rock_Sandstone_Cobble", Long(100))
    t3 = Cat.compute(d3, R)
    check(int(t3[0]) == int(Long.MAX_VALUE), "T6 saturates at Long.MAX_VALUE: %s" % t3[0])
    Cat.CACHE.put("satkey", JArray(JObject)([R, d3, t3]))
    Cat.onAdd("satkey", d3, R, "Rock_Stone_Cobble", Long(50))
    check(int(t3[0]) == int(Long.MAX_VALUE), "T6 onAdd saturates too")
    Cat.onAdd(None, d3, R, "Rock_Stone_Cobble", Long(1))
    Cat.CACHE.put("badkey", JArray(JObject)([R, d3, JString("not long[]")]))
    Cat.onAdd("badkey", d3, R, "Rock_Stone_Cobble", Long(1))
    check(Cat.CACHE.get("badkey") is None, "T6 a broken cache entry is dropped, never thrown")
    check(Cat.compute(None, R) is not None and all(int(x) == 0 for x in Cat.compute(None, R)) and int(Cat.masks(None).size()) == 0,
          "T6 null data / registry -> zeros")
    check(int(Cat.maskOf(None, "Mining")) == 0 and int(Cat.maskOf("Fish_Trout", "Farming")) == 1 << 3 and int(Cat.maskOf("Ore_Iron", "Mining")) == (1 | 32)
          and int(Cat.maskOf("Ingredient_Crystal_Red", "Combat")) == 1 and int(Cat.maskOf("Ingredient_Hide_Light", "Combat")) == (16 | 32)
          and int(Cat.maskOf("Anything", "NoSuchCat")) == 0, "T6 maskOf rules (Fish_* even from Farming -> Fishing only)")
    # PROFILE SWITCH: profile:fn:key flips the key (SkyyProfiles); each profile has its own totals and cache
    reset_store()
    p2 = dict((k_, (v_ * 3 + 1) % 977) for k_, v_ in allc.items())
    write_counts(US, allc)
    write_counts(US + "-p2", p2)
    BR.put("profile:fn:key", KF)
    KF.key = None
    w1 = totals(UID)
    KF.key = US + "-p2"
    w2 = totals(UID)
    d_p2 = Store.dataK(US + "-p2")
    check(w2 == model(Reg, Store, d_p2) and w2 != w1, "T7 profile switch -> profile 2's totals: %s" % w2)
    c_p2 = int(R.itemColl.get("Ore_Iron"))
    Store.addLocked(d_p2, US + "-p2", R, c_p2, "Ore_Iron", Long(9))
    w2b = totals(UID)
    check(w2b["Mining"] == w2["Mining"] + 9 and w2b["Smithing"] == w2["Smithing"] + 9, "T7 a collect on profile 2 updates profile 2")
    KF.key = None
    check(totals(UID) == w1, "T7 back to profile 1: its own totals, untouched by profile 2's collect")
    KF.key = US + "-p2"
    check(totals(UID) == w2b, "T7 profile 2 again: still cached and exact")
    BR.remove("profile:fn:key")
    print("T. catTotal: model match on %d items; cache builds %d; argument shapes; profile switch" % (len(allc), int(Cat.BUILDS)))

    # ---------------- K. sacks:v2 absent vs present
    reset_store()
    BR.clear()
    MINING = ["Skyy_Sack_Mining_%s_Recipe_Generated_0" % s for s in ("Small", "Medium", "Rare", "Large")]
    prof = {"Rock_Stone_Cobble": thr(COB, 7), "Plant_Crop_Wheat_Item": thr(BYID["Wheat"], 3), "Wood_Oak_Trunk": thr(BYID["OakLog"], 1)}
    write_counts(US, prof, meta={"_keptbag.Mining": 15})
    d = Store.data(UID)

    def state(v):
        if v is None:
            BR.remove("sacks:v2")
        else:
            BR.put("sacks:v2", v)

    def bagless(xs):
        return [x for x in xs if not str(x).startswith("Skyy_Sack_")]

    abs_rec = dict(((c, t), [str(x) for x in Reg.recipesAt(c, t)]) for c in range(R.n) for t in range(1, mx(c) + 1))
    abs_set = set(str(x) for x in Unl.compute(d))
    check(set(MINING) <= abs_set and any("Skyy_Sack_" in x for xs in abs_rec.values() for x in xs), "K1 key absent: bags in recipesAt + compute (0.2.8)")
    check(all(Reg.recipesAt(c, t) is not None for (c, t) in abs_rec), "K1 recipesAt never null")
    # absent == the 0.2.8 jar on the same files
    Reg_o, Store_o, Unl_o = jc("CollReg", "old"), jc("CollStore", "old"), jc("CollUnlocks", "old")
    Reg_o.BASE = Paths.get(wbase)
    Store_o.DIR = Paths.get(wbase).resolve("counts")
    Reg_o.loadAll()
    recipes_from_rewards(Reg_o)
    Store_o.DATA.clear()
    old_set = set(str(x) for x in Unl_o.compute(Store_o.dataK(US)))
    check(abs_set == old_set, "K1 key absent: compute == the 0.2.8 jar's (%d recipes): %s" % (len(abs_set), sorted(abs_set ^ old_set)))
    texts_abs = dict(((c, t), str(Reg.rewardText(R, c, t))) for (c, t) in abs_rec)
    texts_old = dict(((c, t), str(Reg_o.rewardText(Reg_o.D, c, t))) for (c, t) in abs_rec)
    check(texts_abs == texts_old, "K1 key absent: every tier's reward text == 0.2.8's")
    wh_abs = Fn.where(JArray(JObject)([UID, MINING[1]]))
    check(wh_abs is not None and str(wh_abs).startswith("Cobblestone|"), "K1 key absent: coll:fn:where finds the bag: %s" % wh_abs)
    for v, name in ((Bool(True), "Boolean TRUE"), (JString("true"), "String \"true\""), (JString(" TRUE "), "String \" TRUE \"")):
        state(v)
        check(bool(Cat.v2()), "K2 %s counts as set" % name)
        pre = dict(((c, t), [str(x) for x in Reg.recipesAt(c, t)]) for c in range(R.n) for t in range(1, mx(c) + 1))
        check(all(pre[k_] == bagless(abs_rec[k_]) for k_ in abs_rec), "K2 %s: recipesAt = 0.2.8's minus every bag, order kept" % name)
        st = set(str(x) for x in Unl.compute(d))
        check(st == set(bagless(abs_set)) and not any(x.startswith("Skyy_Sack_") for x in st), "K2 %s: compute = 0.2.8's minus bags (kept Mining bags too)" % name)
    for v, name in ((Bool(False), "Boolean FALSE"), (JString("no"), "String \"no\""), (JObject(1, JClass("java.lang.Integer")), "Integer 1")):
        state(v)
        check(not bool(Cat.v2()) and set(str(x) for x in Unl.compute(d)) == abs_set, "K3 %s = absent" % name)
    state(Bool(True))
    texts_pre = dict(((c, t), str(Reg.rewardText(R, c, t))) for (c, t) in abs_rec)
    check(not any(BAG_RE.search(x) for x in texts_pre.values()) and any(BAG_RE.search(x) for x in texts_abs.values()),
          "K4 reward texts: bags only while the key is absent")
    check("Copper Pickaxe recipe" in texts_pre[(COB, 1)] and "coins" in texts_pre[(COB, 1)], "K4 Cobblestone I keeps the pickaxe + coins: %s" % texts_pre[(COB, 1)])
    lines_pre = [str(x) for x in Reg.rewardLines(R, COB, 1)]
    check(not any(BAG_RE.search(x) for x in lines_pre) and any("Copper Pickaxe" in x for x in lines_pre), "K4 tier-up chat lines: no bag: %s" % lines_pre)
    check(Fn.where(JArray(JObject)([UID, MINING[1]])) is None and Fn.where(JArray(JObject)([UID, "Tool_Pickaxe_Copper_Recipe_Generated_0"])) is not None,
          "K4 coll:fn:where: no bag, other recipes as before")
    ut = str(Byp.unlockText(COB, 3))
    state(None)
    ut_abs = str(Byp.unlockText(COB, 3))
    check(BAG_RE.search(ut_abs) is not None and BAG_RE.search(ut) is None, "K4 coin-unlock text: bag only when absent: %s / %s" % (ut_abs, ut))
    # fixer (critic LOW 1): Server Setup > Magic Bags rows (CollKit.bagLadder) + the setup gaps warning
    Kit_n, Kit_o = jc("CollKit"), jc("CollKit", "old")
    lad_abs = dict((t_, str(Kit_n.bagLadder(t_))) for t_ in ("Mining", "Foraging", "Farming", "Combat", "Fishing"))
    lad_old = dict((t_, str(Kit_o.bagLadder(t_))) for t_ in lad_abs)
    check(lad_abs == lad_old and "Cobblestone" in lad_abs["Mining"], "K6 key absent: Magic Bags rows == 0.2.8's: %s" % lad_abs)
    state(Bool(True))
    lad_pre = dict((t_, str(Kit_n.bagLadder(t_))) for t_ in lad_abs)
    check(all(v_ == "none - bags now level up in the SkyySacks Pocket Dimension" for v_ in lad_pre.values()), "K6 key set: Magic Bags rows say the Pocket Dimension: %s" % lad_pre)
    check(str(Kit_n.customGet("bags.Mining")) == lad_pre["Mining"], "K6 key set: customGet(bags.Mining) goes through bagLadder")
    state(None)
    check(str(Kit_n.bagLadder("Mining")) == lad_old["Mining"], "K6 key gone again: Mining row back to 0.2.8's")

    # the page (no /craft on this server: plain rows)
    def page(view=0, coll=-1, cat=0):
        pg = Page(pref())
        pg.view, pg.coll, pg.cat = view, coll, cat
        return pg

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        return cmds

    def blob(cmds):
        return "\n".join("%s %s" % (t or "", dd or "") for _ty, _s, t, dd in cmds)

    def click(pg, a):
        pg.handleDataEvent(None, None, json.dumps({"a": a}))

    def pages_text():
        out = []
        out.append(blob(build(page(2, COB))))
        out.append(blob(build(page(2, BYID["Wheat"]))))
        pg = page(0)
        build(pg)
        click(pg, "crecipes")
        out.append(blob(build(pg)))
        pg = page(0)
        build(pg)
        click(pg, "clocked")
        for _i in range(6):
            out.append(blob(build(pg)))
            click(pg, "crnext")
        out.append(blob(build(page(0))))
        return "\n".join(out)

    reset_store()
    write_counts(US, {"Rock_Stone_Cobble": thr(COB, 3), "Plant_Crop_Wheat_Item": 20}, meta={"_keptbag.Mining": 4})
    state(None)
    pa = pages_text()
    state(Bool(True))
    pp = pages_text()
    check(BAG_RE.search(pa) is not None, "K5 pages, key absent: the bag rewards / lists show (0.2.8)")
    check(BAG_RE.search(pp) is None, "K5 pages, key present: no bag anywhere (tier rows, Unlocked, Locked lists): %s" % (BAG_RE.search(pp) and pp[max(0, BAG_RE.search(pp).start() - 80):BAG_RE.search(pp).end() + 40]))
    check("Copper Pickaxe" in pp, "K5 pages, key present: the other rewards still show")
    state(None)
    print("K. sacks:v2: absent = 0.2.8 (compute + reward texts compared with the 0.2.8 jar), present = no bag anywhere")

    # ---------------- V. CollSaver.v2Tick
    reset_store()
    BR.clear()
    write_counts(US, {"Rock_Stone_Cobble": thr(COB, 3)})
    Unl.PUBLISHED.clear()
    Unl.SIG.clear()
    Unl.publish(UID)
    rk, ek = "coll:recipes:" + US, "coll:epoch:" + US
    e0 = BR.get(ek)
    check(MINING[0] in str(BR.get(rk)) and e0 is not None, "V1 published with the bags (key absent): %s" % BR.get(rk))
    Cat.V2 = -1
    Saver.v2Tick()
    check(int(Cat.V2) == 0 and BR.get(ek) == e0, "V1 first look, key absent: nothing republished")
    Saver.v2Tick()
    check(BR.get(ek) == e0, "V1 no change -> nothing")
    state(Bool(True))
    Saver.v2Tick()
    e1 = BR.get(ek)
    check(int(Cat.V2) == 1 and "Skyy_Sack_" not in str(BR.get(rk)) and "Tool_Pickaxe_Copper_Recipe_Generated_0" in str(BR.get(rk)) and int(e1) == int(e0) + 1,
          "V2 key set -> coll:recipes without bags, epoch %s -> %s: %s" % (e0, e1, BR.get(rk)))
    state(None)
    Saver().run()     # the 1 s saver: v2Tick first (the engine calls after it are caught in a bare JVM)
    e2 = BR.get(ek)
    check(int(Cat.V2) == 0 and MINING[0] in str(BR.get(rk)) and int(e2) == int(e1) + 1, "V3 key gone (through CollSaver.run) -> the bags are back, epoch %s" % e2)
    Cat.V2 = -1
    state(Bool(True))
    Saver.v2Tick()
    check(int(Cat.V2) == 1 and "Skyy_Sack_" not in str(BR.get(rk)), "V4 first look with the key set -> republished without bags")
    state(None)
    BR.clear()
    print("V. v2Tick: republish on every switch, never otherwise")

    # ---------------- S. start twice on a scratch COPY of the live data
    def start(folder, jar):
        lo = loader(jar)

        def j(n):
            return JClass(PKG + n, loader=lo)
        R_, S_ = j("CollReg"), j("CollStore")
        R_.BASE = Paths.get(folder)
        S_.DIR = Paths.get(folder).resolve("counts")
        j("CollBagMigrate").run(Paths.get(folder))
        j("CollBypassMig").run(Paths.get(folder))
        R_.loadAll()
        msg = str(j("CollCobMig").run(Paths.get(folder)))
        j("CfgPub").start(Paths.get(os.path.dirname(folder)), None)
        j("CfgPub").shutdown()
        return lo, msg

    def world(lo, folder):
        R_ = JClass(PKG + "CollReg", loader=lo)
        S_ = JClass(PKG + "CollStore", loader=lo)
        R_.BASE = Paths.get(folder)
        S_.DIR = Paths.get(folder).resolve("counts")
        R_.loadAll()
        recipes_from_rewards(R_)
        S_.DATA.clear()
        return R_, S_

    def counts_keys(folder):
        cd = os.path.join(folder, "counts")
        return sorted(f[:-11] for f in os.listdir(cd) if f.endswith(".properties")) if os.path.isdir(cd) else []

    if os.path.isdir(LIVE):
        live_before = snap(LIVE)
        dn = os.path.join(SCRATCH, "s-new", "mods", "Skyy_SkyyCollections")
        do = os.path.join(SCRATCH, "s-old", "mods", "Skyy_SkyyCollections")
        shutil.copytree(LIVE, dn)
        shutil.copytree(LIVE, do)
        b0 = snap(dn)
        lo_o1, mo1 = start(do, OLD)
        _lo_o2, mo2 = start(do, OLD)
        ao = snap(do)
        lo_n1, mn1 = start(dn, JAR)
        a1 = snap(dn)
        lo_n2, mn2 = start(dn, JAR)
        a2 = snap(dn)
        chg1 = sorted(k_ for k_ in set(b0) | set(a1) if b0.get(k_) != a1.get(k_))
        chg_o = sorted(k_ for k_ in set(b0) | set(ao) if b0.get(k_) != ao.get(k_))
        check(chg1 == chg_o, "S1 start 1 of 0.2.9 changes what 0.2.8 changes on the same copy: %s / %s" % (chg1, chg_o))
        check(a2 == a1 and mn2 == "", "S1 start 2 writes nothing: %s" % sorted(k_ for k_ in set(a1) | set(a2) if a1.get(k_) != a2.get(k_)))
        check(chg1 == [], "S1 the live data is already 0.2.8: start 1 writes nothing either (%s)" % chg1)
        keys = counts_keys(dn)
        Rn, Sn = world(lo_n2, dn)
        Ro, So = world(lo_o1, do)
        Un, Uo = JClass(PKG + "CollUnlocks", loader=lo_n2), JClass(PKG + "CollUnlocks", loader=lo_o1)
        Fn2, Cat2 = JClass(PKG + "CollFn", loader=lo_n2), JClass(PKG + "CollCat", loader=lo_n2)
        nprof = 0
        for k_ in keys:
            dn_, do_ = Sn.dataK(k_), So.dataK(k_)
            if dn_ is None or do_ is None:
                check(False, "S2 %s reads" % k_)
                continue
            BR.clear()
            sn, so = set(str(x) for x in Un.compute(dn_)), set(str(x) for x in Uo.compute(do_))
            check(sn == so, "S2 %s: key absent, 0.2.9 unlocks == 0.2.8 (%d): %s" % (k_, len(so), sorted(sn ^ so)))
            BR.put("sacks:v2", Bool(True))
            sv = set(str(x) for x in Un.compute(dn_))
            check(sv == set(bagless(so)), "S2 %s: key present = 0.2.8 minus bags (%d bags hidden)" % (k_, len(so) - len(sv)))
            BR.clear()
            # catTotal through the profile key: the uuid part + profile:fn:key = this file's key
            m_ = re.match(r"^([0-9a-f-]{36})(-p\d+)?$", k_)
            if not m_:
                continue
            BR.put("profile:fn:key", KF)
            KF.key = k_
            u_ = UUID.fromString(m_.group(1))
            got_ = dict((c, int(Fn2.catTotal(JArray(JObject)([u_, c])))) for c in BAGCATS)
            want_ = model(Rn, Sn, dn_)
            check(got_ == want_, "S3 live profile %s: catTotal == the collection sums: %s / %s" % (k_, got_, want_))
            nprof += 1
            BR.clear()
        # switching back and forth across the live profiles of one player answers each profile's own numbers (cached)
        multi = [k_ for k_ in keys if re.match(r"^[0-9a-f-]{36}-p\d+$", k_)]
        if multi:
            base_u = multi[0][:36]
            same = [base_u] + [k_ for k_ in keys if k_.startswith(base_u + "-p")]
            BR.put("profile:fn:key", KF)
            u_ = UUID.fromString(base_u)
            first = {}
            for k_ in same:
                KF.key = k_
                first[k_] = int(Fn2.catTotal(JArray(JObject)([u_, "Mining"])))
            bb = int(Cat2.BUILDS)
            for k_ in reversed(same):
                KF.key = k_
                check(int(Fn2.catTotal(JArray(JObject)([u_, "Mining"]))) == first[k_], "S3 profile %s again: same Mining total" % k_)
            check(int(Cat2.BUILDS) == bb, "S3 switching back over %d live profiles rebuilt nothing" % len(same))
            BR.clear()
        check(snap(LIVE) == live_before, "S4 the live folder is untouched")
        print("S. live copy: 2 starts of 0.2.9 (and 0.2.8) write nothing; %d profiles: unlocks == 0.2.8 (absent) / minus bags (present); catTotal == model on %d"
              % (len(keys), nprof))
    else:
        print("note: no live Skyy_SkyyCollections folder - S skipped")


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (python tools/collections_0_2_9_patch.py, python SkyyCollections/build_skyycollections_0.2.9.py)")
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
    print("SkyyCollections %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f[:400])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
