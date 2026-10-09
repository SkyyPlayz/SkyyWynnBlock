"""Bare-JVM harness for SkyyCollections 0.2.8 (tools/collections_0_2_8_patch.py; Skyy 2026-10-09, docs/answered/bags.md LOCKED):
  1. "any unlocked recopies shown here should open in the crafter if i click it."      -> CRAFT buttons (/craft <words> as the player)
  2. "we have unlocked recopies, we need a locked recopies tab, that tells you which collection you unlock something in."  -> LOCKED RECIPES
  3. "the mining bag should come from cobble collection, not iron"                     -> the Mining bag ladder on Cobblestone + CollCobMig
  4. "move normal bags to tier 1"   -> U9 / M1: every Normal bag at its collection's tier I (Unique III, Rare V, Legendary VII), 5 types

    python SkyyCollections/test_skyycollections_0.2.8.py [--jar <SkyyCollections-0.2.8.jar>] [--old <SkyyCollections-0.2.7.jar>]
                                                         [--dir <scratch>] [--live <Skyy_SkyyCollections folder>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), every jar in its own
class loader; a FRESH loader of the 0.2.8 jar = one server start (static state empty, like a restart).
  A  every class of both jars loads, verifies and initialises
  B  class bytes 0.2.7 -> 0.2.8: the same classes + CollCraft + CollCobMig; every other class byte-identical / version-constants-only /
     only the DECLARED methods changed or added; manifest: Version / Name / the "Mining bags from" words only
  E  engine-access audit: every engine (com.hypixel) method / field the 0.2.8 jar references that 0.2.7 did not is listed and resolved
     by reflection against HytaleServer.jar (name + descriptor)
  C  the page id in the ready line == COLL_PAGE_CHECKED == the page the kit makes now
  P  PAGES on the real registry (a fresh 0.2.8 world, the default rewards table): P1 /craft absent (no SkyySacks) -> no CRAFT button or
     ccraft / crcraft binding anywhere (detail + unlocked list); P2 /craft present (a fake CommandManager + a fake /craft command) -> a
     CRAFT button exactly on the DONE / BOUGHT rows with an unlocked recipe, plain rows elsewhere, non-locking bindings; P3 clicks: a
     CRAFT click runs "craft <words>" as the player (the words match the recipe item), a forged click on a locked tier / no permission /
     /craft gone -> the result line, no command; P4 the unlocked list (rows = the Python model, CRAFT per row, crcraft click); P5 the
     LOCKED list: contents, order (closest first), "<Collection> tier <roman>" + "count / threshold", paging both ways, free bags count
     as unlocked; P6 OPEN on a locked row -> that collection's page with "< Back to list", Back -> the list; P7 every built page passes
     check_markup / check_page / assert_proven, no underscore ids, ids unique; text fit of every CRAFT row's rewards text and the list
     cells (the client's font tables)
  U  UNLOCKS: Mining bags unlock from Cobblestone tiers 1/3/5/7 (threshold - 1 locked, threshold unlocked), Iron alone unlocks none on
     a fresh world, coll:fn:where -> Cobblestone, the read-only Server Setup row "Cobblestone I / III / V / VII", no bag gaps
  M  THE MIGRATION (CollCobMig.run in the plugin's setup order: CollBagMigrate -> CollBypassMig -> loadAll -> CollCobMig -> CfgPub
     start / shutdown; every start a fresh loader): M1 a COPY of Skyy's live Skyy_SkyyCollections folder: start 1 changes exactly
     rewards.properties (the expected text, built here independently: Iron bag lines gone, Cobblestone lines added / appended, the
     comment lines, the marker; every other byte and LF kept), config-history (a .bak = the old bytes + index.log), config-changes.log
     (one ok line per changed entry, Undo-able), migration-bags.log, and the counts files of profiles that had a Mining bag through Iron
     (_keptbag.Mining); every profile's 0.2.7 unlock set is inside its 0.2.8 set (never take away) and the only new recipes are Mining
     bags from Cobblestone; start 2 writes nothing; M2 edited copies (hand-edited Iron / Cobblestone lines kept + logged, a missing
     Iron line, Cobblestone already listing the bag, CRLF + a non-ASCII byte, no final newline, a fresh 0.2.8 file, a 0.2.2 file through
     CollBagMigrate) each started twice; M3 config-history unwritable -> nothing written, retried; M4 a counts file that cannot be
     written -> nothing written (no rewards change), retried; M5 kept bits (count tiers, bought tiers within / above bagMax, an
     existing bit OR-ed, a 0.1 file skipped)
Nothing outside the scratch folder is written (default tools/dev/scratch/coll028/harness, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, stat, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.8", "0.2.7"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "coll028", "harness")))
assert SCRATCH.lower().startswith(SCRATCH_ROOT.lower() + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                   "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}
MINING = ["Skyy_Sack_Mining_%s_Recipe_Generated_0" % s for s in ("Small", "Medium", "Rare", "Large")]
RAR = ["Normal", "Unique", "Rare", "Legendary"]
LADDER = [1, 3, 5, 7]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def tally(k, n=1):
    COUNT[k] = COUNT.get(k, 0) + n


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
    from jpype import JClass, JArray, JObject
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
    check(sorted(set(new) - set(old)) == [PKG + "CollCobMig", PKG + "CollCraft"] and not (set(old) - set(new)),
          "B. the same classes + CollCobMig + CollCraft: %s" % sorted(set(old) ^ set(new)))
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

    # what 0.2.8 changes (patch parts 1-3); anything else differing is a failure
    DECLARED = {
        "CollBagMigrate": ["<clinit>", "run"],                           # part 3: the 0.2.8 marker; C_OLD / C_NEW empty (no ore merge)
        "CollReg": ["rewardsText"],                          # part 3: the default rewards table
        "CollUnlocks": ["compute"],                                      # part 3: the kept bags
        "CollKit": ["customSet"],                                        # part 3: "entries like Cobblestone.3"
        "CollPage": ["build", "buildDetail", "buildHome", "buildRecipes", "handleDataEvent"],   # parts 1 + 2
        "SkyyCollectionsPlugin": ["setup"],                              # part 3: CollCobMig.run + the ready line
        "CfgRows": ["<clinit>"],                                         # the Tier rewards help text
    }
    ADDED = {
        "CollPage": ["bindFree(Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Ljava/lang/String;Ljava/lang/String;)V",
                     "craftClick(I)V", "lockCmp([Ljava/lang/Object;[Ljava/lang/Object;)I",
                     "lockedRows(Lcom/skyy/collections/CollData;Lcom/skyy/collections/RegData;)Ljava/util/ArrayList;",
                     "rowCraft(I)V", "rowOpen(I)V",
                     "unlockedRows(Lcom/skyy/collections/CollData;Lcom/skyy/collections/RegData;)Ljava/util/ArrayList;"],
    }
    NEWFIELDS = {"CollPage": ["CRAFTREW", "LISTBACK", "RLROWS", "back", "fcol", "ftier", "rcol", "rpage", "rrid"]}
    kinds = {}
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
        check(not (fo - fn) and sorted(fn - fo) == NEWFIELDS.get(short, []), "B. %s: fields added / gone: %s" % (short, sorted(fo ^ fn)))
        mo, mn = methods(po), methods(pn)
        check(not (set(mo) - set(mn)) and sorted(set(mn) - set(mo)) == sorted(ADDED.get(short, [])),
              "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        vers = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and vonly(mo[k], mn[k]))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        kinds[short] = "methods %s + version only %s" % (changed, vers)
    for k in DECLARED:
        check(k in kinds and kinds[k].startswith("methods"), "B. %s is one of the changed classes: %s" % (k, kinds.get(k)))
    mo_, mn_ = manifest(OLD), manifest(JAR)
    check(mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyyCollections"
          and mo_["Description"].replace("(Mining bags from Iron Ore)", "(Mining bags from Cobblestone)") == mn_["Description"]
          and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name", "Description")) == dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name", "Description")),
          "B. manifest: only Version / Name / the Mining bag words changed")
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
                for i_ in k_.getInterfaces():
                    for m in i_.getDeclaredMethods():
                        if str(m.getName()) == nm and str(MH.methodType(m.getReturnType(), m.getParameterTypes()).toMethodDescriptorString()) == ty:
                            found = True
            else:
                for f in k_.getDeclaredFields():
                    if str(f.getName()) == nm:
                        found = True
            k_ = k_.getSuperclass()
        check(found, "E. engine reference resolves: %s %s.%s%s" % (kind, cl, nm, ty))
    print("E. engine-access audit: %d engine references new in 0.2.8, all resolved: %s" % (len(added), ["%s.%s" % (c.split(".")[-1], n) for _k, c, n, _t in added]))

    # ---------------- C. page id
    text = open(SCRIPT, encoding="utf8").read()
    chk = script_const("COLL_PAGE_CHECKED")
    plug = new[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mm = re.search(r"0\.2\.8 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug)
    check(mm is not None and mm.group(1) == chk and K["COLL_PAGE_ID"] == chk,
          "C. page id: ready line %s == checked %s == the kit now %s (set PAGE_CHECKED in tools/collections_0_2_8_patch.py, regenerate, rebuild)"
          % (mm and mm.group(1), chk, K["COLL_PAGE_ID"]))

    # ---------------- the 0.2.8 world
    Paths, Long, HashMap, HashSet = JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.util.HashMap"), JClass("java.util.HashSet")
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

    def jc(name, k="new"):
        return JClass(PKG + name, loader=L[k])

    def jfield(c_, name):
        f = c_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    UID = UUID.fromString("00000000-0000-0000-0000-0000000000c8")
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

    Reg, Store, Util, Unl, Kit = jc("CollReg"), jc("CollStore"), jc("CollUtil"), jc("CollUnlocks"), jc("CollKit")
    Cob, Craft, Page = jc("CollCobMig"), jc("CollCraft"), jc("CollPage")
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
    VIS = [c for c in range(R.n) if not R.hidden[c]]

    def thr(c, t):
        return int(Reg.threshold(R, c, t))

    def mx(c):
        return int(Reg.maxTier(R, c))

    def first_item(c):
        return str(R.items[c][0])

    def data(counts, bought=None, meta=None):
        d = jc("CollData")()
        for c, n in counts.items():
            if n:
                d.items.put(first_item(c), Long.valueOf(n))
        for c, b in (bought or {}).items():
            d.meta.put("_bought." + str(R.id[c]), Long.valueOf(b))
        for k, v in (meta or {}).items():
            d.meta.put(k, Long.valueOf(v))
        return d

    def unl(d):
        return set(str(x) for x in Unl.compute(d))


    # Skyy 2026-10-09 "move normal bags to tier 1": every type's Normal (Small) bag at its collection's tier I, Unique III, Rare V,
    # Legendary VII, and nowhere else (BAG_COLL 0.2.8: Mining = Cobblestone)
    LADDER_WANT = {}
    for _ty, _co in (("Mining", "Cobblestone"), ("Foraging", "OakLog"), ("Farming", "Wheat"), ("Combat", "Bone"), ("Smithing", "HideLight")):
        for _sfx, _t in (("Small", 1), ("Medium", 3), ("Rare", 5), ("Large", 7)):
            LADDER_WANT["Skyy_Sack_%s_%s_Recipe_Generated_0" % (_ty, _sfx)] = [(_co.lower(), _t)]

    def bag_places_text(txt):
        got = {}
        for l in txt.replace("\r\n", "\n").split("\n"):
            l = l.strip()
            m = re.match(r"^([A-Za-z0-9_]+)\.(\d+)\s*=(.*)$", l)
            if not m:
                continue
            for tok in m.group(3).split(","):
                tok = tok.strip().replace("recipe: ", "recipe:")
                if tok.startswith("recipe:Skyy_Sack_"):
                    got.setdefault(tok[7:], []).append((m.group(1).lower(), int(m.group(2))))
        return dict((k, sorted(v)) for k, v in got.items())

    # ---------------- U. unlocks from Cobblestone
    for j, t in enumerate(LADDER):
        below, at = unl(data({COB: thr(COB, t) - 1})), unl(data({COB: thr(COB, t)}))
        check(MINING[j] not in below and MINING[j] in at, "U1 %s Mining Bag: locked at %d cobble, unlocked at %d (Cobblestone tier %d)" % (RAR[j], thr(COB, t) - 1, thr(COB, t), t))
        check([m for m in MINING if m in at] == MINING[:j + 1], "U1 at Cobblestone tier %d exactly the lower Mining bags" % t)
    check("Tool_Pickaxe_Copper_Recipe_Generated_0" in unl(data({COB: thr(COB, 1)})), "U1 Cobblestone I still gives the Copper Pickaxe")
    check(not any(m in unl(data({IRON: thr(IRON, mx(IRON))})) for m in MINING), "U2 a fresh world: Iron at its last tier unlocks no Mining bag")
    check(all(m in unl(data({}, meta={"_keptbag.Mining": 15})) for m in MINING) and unl(data({}, meta={"_keptbag.Mining": 5})) >= {MINING[0], MINING[2]}
          and MINING[1] not in unl(data({}, meta={"_keptbag.Mining": 5})), "U3 _keptbag.Mining bits -> exactly those bags")
    Reg.BYP_BAGMAX = 2
    bb = unl(data({}, bought={COB: 7}))
    check(MINING[0] in bb and MINING[1] in bb and MINING[2] not in bb, "U4 Cobblestone bought to VII, bagMax Unique -> Normal + Unique only")
    wh = jc("CollFn").where(JArray(JObject)([UID, MINING[1]]))
    check(wh is not None and str(wh).startswith("Cobblestone|Cobblestone|3|%d|" % thr(COB, 3)), "U5 coll:fn:where Unique Mining Bag -> %s" % wh)
    check(str(Kit.customGet("bags.Mining")) == "Cobblestone I / III / V / VII", "U6 Server Setup Magic Bags row: %s" % Kit.customGet("bags.Mining"))
    check(str(jc("CollBagMigrate").gaps()) == "", "U7 no bag gaps: %s" % jc("CollBagMigrate").gaps())
    rt = str(Reg.rewardText(R, COB, 1))
    check("Copper Pickaxe recipe" in rt and "Normal Mining Bag recipe" in rt, "U8 Cobblestone I row text: %s" % rt)
    got_reg = {}
    for c in range(R.n):
        for t in range(1, mx(c) + 1):
            for rid in [str(x) for x in Reg.recipesAt(c, t)]:
                if rid.startswith("Skyy_Sack_") and not rid.startswith("Skyy_Sack_Omni"):
                    got_reg.setdefault(rid, []).append((str(R.id[c]).lower(), t))
    check(dict((k, sorted(v)) for k, v in got_reg.items()) == LADDER_WANT,
          "U9 fresh default table: every Normal bag at tier I, Unique III, Rare V, Legendary VII (5 types): %s" % sorted(got_reg.items()))
    for _ty, _co in (("Mining", COB), ("Foraging", BYID["OakLog"]), ("Farming", BYID["Wheat"]), ("Combat", BYID["Bone"]), ("Smithing", BYID["HideLight"])):
        n_ = "Skyy_Sack_%s_Small_Recipe_Generated_0" % _ty
        check(n_ not in unl(data({_co: thr(_co, 1) - 1})) and n_ in unl(data({_co: thr(_co, 1)})), "U9 Normal %s Bag unlocks exactly at %s tier I" % (_ty, R.id[_co]))
    print("U. Mining bags unlock from Cobblestone I / III / V / VII; Normal bags of all 5 types at tier I; %s" % lmsg)

    # ---------------- fakes: CommandManager + /craft
    jp = CP(True)
    jp.appendClassPath(B.SERVER_JAR)
    CMGR = JClass("com.hypixel.hytale.server.core.command.system.CommandManager")
    ACMD = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fm = jp.makeClass("com.hypixel.hytale.server.core.command.system.SkyyTestFakeCmdMgr", jp.get(CMGR.class_.getName()))
    fm.addField(JClass("javassist.CtField").make("public static java.util.List LINES = new java.util.ArrayList();", fm))
    fm.addMethod(JClass("javassist.CtNewMethod").make(
        "public java.util.concurrent.CompletableFuture handleCommand(com.hypixel.hytale.server.core.command.system.CommandSender s, String line) {"
        " LINES.add(line); return java.util.concurrent.CompletableFuture.completedFuture(null); }", fm))
    FakeMgr = fm.toClass(CMGR.class_)
    fc = jp.makeClass("com.hypixel.hytale.server.core.command.system.SkyyTestFakeCraft", jp.get(ACMD.class_.getName()))
    fc.addField(JClass("javassist.CtField").make("public static boolean ALLOW = true;", fc))
    fc.addMethod(JClass("javassist.CtNewMethod").make(
        "public boolean hasPermission(com.hypixel.hytale.server.core.command.system.CommandSender s) { return ALLOW; }", fc))
    fc.addMethod(JClass("javassist.CtNewMethod").make(
        "protected java.util.concurrent.CompletableFuture execute(com.hypixel.hytale.server.core.command.system.CommandContext c) { return null; }", fc))
    FakeCraft = fc.toClass(ACMD.class_)
    FM = JClass(FakeMgr.getName(), loader=FakeMgr.getClassLoader())
    FCr = JClass(FakeCraft.getName(), loader=FakeCraft.getClassLoader())
    mgr = U.allocateInstance(FakeMgr)
    reg_ = HashMap()
    reg_.put("craft", U.allocateInstance(FakeCraft))
    jfield(CMGR.class_, "commandRegistration").set(mgr, reg_)
    jfield(CMGR.class_, "aliases").set(mgr, HashMap())
    inst = jfield(CMGR.class_, "instance")
    keep_inst = inst.get(None)

    def craft_on(on):
        inst.set(None, mgr if on else keep_inst)

    def lines():
        return [str(x) for x in FM.LINES]

    # ---------------- page helpers
    def setup_player(counts, bought=None, meta=None, freebags=None):
        Store.DATA.clear()
        Store.BROKEN.clear()
        Store.DIRTY.clear()
        BR.clear()
        if freebags is not None:
            BR.put("sacks:freebags", Bool(freebags))
        cd = os.path.join(wbase, "counts")
        shutil.rmtree(cd, ignore_errors=True)
        os.makedirs(cd)
        ls = ["_schema=2"]
        for c, n in counts.items():
            if n:
                ls.append("%s=%d" % (first_item(c), n))
        for c, b in (bought or {}).items():
            ls.append("_bought.%s=%d" % (R.id[c], b))
        for k, v in (meta or {}).items():
            ls.append("%s=%d" % (k, v))
        open(os.path.join(cd, US + ".properties"), "w").write("\n".join(ls) + "\n")
        return Store.data(UID)

    def page(view=0, coll=-1, cat=0):
        pg = Page(pref())
        pg.view, pg.coll, pg.cat = view, coll, cat
        return pg

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        check_markups(cmds)
        return cmds, evs

    def appends_of(cmds):
        return [(None if sel is None else sel.lstrip("#"), text) for typ, sel, text, data in cmds if "append" in typ.lower()]

    def sets_of(cmds):
        out = {}
        for typ, sel, text, data in cmds:
            if "append" in typ.lower() or not sel or not sel.endswith(".Text"):
                continue
            d = json.loads(data)
            out[sel[1:-5]] = d.get("0") if isinstance(d, dict) else d
        return out

    def ids_of(cmds):
        return [i for _p, t in appends_of(cmds) for i in ID_RE.findall(t)]

    SEEN = set()

    def check_markups(cmds):
        h = hashlib.sha1(repr(cmds).encode("utf8")).hexdigest()
        if h in SEEN:
            return
        SEEN.add(h)
        aps = appends_of(cmds)
        for p, t in aps:
            try:
                SUI.check_markup(t, prefix=K["COLL_PREFIX"], root=(p is None))
            except ValueError as e:
                check(False, "P7 check_markup: %s: %s" % (e, t[:120]))
            check(all("_" not in x for x in ID_RE.findall(t)), "P7 underscore in an id")
        whole = SUI.Appends(aps)
        try:
            SUI.check_page(whole, prefix=K["COLL_PREFIX"])
        except ValueError as e:
            check(False, "P7 check_page: %s" % e)
        try:
            SUI.assert_proven([t for _p, t in aps], what="0.2.8 page")
        except ValueError as e:
            check(False, "P7 assert_proven: %s" % e)
        ids = ids_of(cmds)
        check(len(ids) == len(set(ids)), "P7 duplicate ids: %s" % sorted(set(i for i in ids if ids.count(i) > 1)))
        tally("P7 pages checked")

    def evdata(evs):
        return [(e[1], json.loads(e[2]).get("a") if e[2] else None, e[3]) for e in evs]

    def click(pg, a):
        pg.handleDataEvent(None, None, json.dumps({"a": a}))

    # ---------------- P1 / P2 / P3 detail page
    cob3 = thr(COB, 3)
    craft_on(False)
    setup_player({COB: cob3, BYID["Wheat"]: thr(BYID["Wheat"], 1)})
    pg = page(2, COB)
    cmds, evs = build(pg)
    check(not any(i.endswith("Go") for i in ids_of(cmds)) and not any("craft" in (a or "") for _s, a, _l in evdata(evs)),
          "P1 /craft absent: no CRAFT button, no craft binding on the Cobblestone page")
    pg3 = page(3)
    cmds3, evs3 = build(pg3)
    check(not any(i.endswith("Go") for i in ids_of(cmds3)) and not any("craft" in (a or "") for _s, a, _l in evdata(evs3)),
          "P1 /craft absent: no CRAFT button on the unlocked list")
    s3 = sets_of(cmds3)
    check("Collections tab" in s3.get("SkyyCRSub", ""), "P1 unlocked list says where to craft without /craft: %s" % s3.get("SkyyCRSub"))
    click(pg, "ccraft1")
    check(lines() == [] and str(pg.status) == "Crafting (/craft) is not on this server.", "P1 a forged CRAFT click without /craft: %s" % pg.status)

    craft_on(True)
    cmds, evs = build(page(2, COB))
    gos = sorted(i for i in ids_of(cmds) if i.startswith("SkyyCTr") and i.endswith("Go"))
    rec_tiers = [t for t in range(1, mx(COB) + 1) if len(Reg.recipesAt(COB, t)) > 0]
    want = ["SkyyCTr%dGo" % t for t in sorted(t for t in rec_tiers if t <= 3)]
    check(gos == sorted(want), "P2 CRAFT buttons exactly on the reached rows with recipes %s: %s" % (want, gos))
    eg = [x for x in evdata(evs) if (x[1] or "").startswith("ccraft")]
    check(sorted(x[1] for x in eg) == sorted("ccraft%d" % t for t in rec_tiers if t <= 3) and all(x[2] is False for x in eg),
          "P2 ccraft bindings, not locking the interface: %s" % eg)
    st = sets_of(cmds)
    check(st.get("SkyyCTr2S") == "DONE" and "SkyyCTr2Go" not in gos and st.get("SkyyCTr4S") in ("NEXT", "LOCKED") and "SkyyCTr4Go" not in gos,
          "P2 tier II (no recipe) and IV (locked) stay plain: %s / %s" % (st.get("SkyyCTr2S"), st.get("SkyyCTr4S")))
    # bought rows: Cobblestone bought to V (bagMax Unique) -> III (bag, Unique) has a CRAFT button, V (Rare, above bagMax) does not
    setup_player({COB: thr(COB, 1)}, bought={COB: 5})
    cmds_b, _e = build(page(2, COB))
    gob = sorted(i for i in ids_of(cmds_b) if i.endswith("Go"))
    check("SkyyCTr3Go" in gob and "SkyyCTr5Go" not in gob and "SkyyCTr4Go" in gob,
          "P2 bought rows: III (Unique bag) + IV (brick) CRAFT, V (Rare above bagMax) plain: %s" % gob)
    # P3 clicks
    setup_player({COB: cob3})
    pg = page(2, COB)
    build(pg)
    del FM.LINES[:]
    click(pg, "ccraft3")
    check(lines() == ["craft skyy sack mining medium"], "P3 CRAFT tier III -> /craft skyy sack mining medium: %s" % lines())
    # review fix (finding 2): Cobblestone I = Copper Pickaxe + Normal Mining Bag share no word -> CRAFT opens the tier's CHOOSER
    del FM.LINES[:]
    click(pg, "ccraft1")
    check(lines() == [] and int(pg.view) == 3 and int(pg.ftier) == 1 and int(pg.fcol) == COB and int(pg.rpage) == 0,
          "FIX2 CRAFT on a 2-recipe row (pickaxe + bag) opens the chooser, no command: view %s ftier %s %s" % (pg.view, pg.ftier, lines()))
    cmdsc, evsc = build(pg)
    stc = sets_of(cmdsc)
    rowsc = [stc.get("SkyyCRr%dN" % i) for i in range(14) if ("SkyyCRr%dN" % i) in stc]
    check(sorted(rowsc) == ["Copper Pickaxe", "Normal Mining Bag"], "FIX2 the chooser lists exactly the row's 2 unlocked recipes: %s" % rowsc)
    check(len([i for i in ids_of(cmdsc) if i.startswith("SkyyCRr") and i.endswith("Go")]) == 2
          and len([x for x in evdata(evsc) if (x[1] or "").startswith("crcraft") and x[2] is False]) == 2, "FIX2 one CRAFT per chooser row")
    check(stc.get("SkyyCRSub", "").startswith("Cobblestone tier I: 2 unlocked recipe(s)"), "FIX2 chooser sub line: %s" % stc.get("SkyyCRSub"))
    for i_, n_ in enumerate(rowsc):
        del FM.LINES[:]
        click(pg, "crcraft%d" % i_)
        want_ = {"Copper Pickaxe": "craft tool pickaxe copper", "Normal Mining Bag": "craft skyy sack mining small"}[n_]
        check(lines() == [want_], "FIX2 chooser CRAFT %s -> %s" % (n_, lines()))
    click(pg, "cback")
    check(int(pg.view) == 2 and int(pg.coll) == COB and int(pg.ftier) == 0, "FIX2 chooser Back -> the Cobblestone page (view %s)" % pg.view)
    click(pg, "ccraft1")
    click(pg, "chome")
    click(pg, "crecipes")
    cmdsh, _e = build(pg)
    check(int(pg.ftier) == 0 and len([k_ for k_ in sets_of(cmdsh) if k_.startswith("SkyyCRr") and k_.endswith("N")]) > 2,
          "FIX2 Home -> Unlocked recipes shows the whole list again")
    # every 2-recipe row of the default table: one() decides search vs chooser (Cobblestone I, Wheat I, Oak Log I -> chooser)
    nchoose = 0
    for c in VIS:
        for t in range(1, mx(c) + 1):
            rs_ = Reg.recipesAt(c, t)
            if len(rs_) < 2:
                continue
            if not bool(Craft.one(rs_, HashSet(JClass("java.util.Arrays").asList(rs_)))):
                nchoose += 1
    check(nchoose >= 3, "FIX2 default rows needing the chooser (Cobblestone I, Wheat I, Oak Log I, ...): %d" % nchoose)
    print("   FIX2: %d default tier rows open the chooser" % nchoose)
    pg = page(2, COB)
    build(pg)
    del FM.LINES[:]
    click(pg, "ccraft5")
    check(lines() == [] and str(pg.status) == "That recipe is not unlocked yet.", "P3 forged CRAFT on locked tier V: %s" % pg.status)
    FCr.ALLOW = False
    click(pg, "ccraft3")
    check(lines() == [] and "permission" in str(pg.status), "P3 no permission for /craft: %s" % pg.status)
    FCr.ALLOW = True
    q = Craft.query(JArray(JString)(["Tool_Hoe_Copper_Recipe_Generated_0", "Tool_Sickle_Copper_Recipe_Generated_0"]),
                    HashSet(JClass("java.util.Arrays").asList(JArray(JString)(["Tool_Hoe_Copper_Recipe_Generated_0", "Tool_Sickle_Copper_Recipe_Generated_0"]))))
    check(str(q) == "tool copper", "P3 two unlocked recipes share 2 words -> 'tool copper': %s" % q)
    check(bool(Craft.one(JArray(JString)(["Tool_Hoe_Copper_Recipe_Generated_0", "Tool_Sickle_Copper_Recipe_Generated_0"]),
                         HashSet(JClass("java.util.Arrays").asList(JArray(JString)(["Tool_Hoe_Copper_Recipe_Generated_0", "Tool_Sickle_Copper_Recipe_Generated_0"]))))),
          "FIX2 2 shared words -> one search (no chooser)")
    check([str(x) for x in Craft.words("Weapon_Arrow_Crude_Recipe_Generated_0")] == ["weapon", "arrow", "crude"], "P3 words of a recipe id")
    print("P1-P3. CRAFT buttons only with /craft, only on unlocked rows; clicks run /craft <words> as the player")

    # ---------------- P4 unlocked list
    prof = {COB: cob3, BYID["Wheat"]: thr(BYID["Wheat"], 3), BYID["OakLog"]: thr(BYID["OakLog"], 1), IRON: thr(IRON, 3)}
    d = setup_player(prof, meta={"_keptbag.Mining": 1 | 2 | 4})
    un = sorted(unl(d))
    pg = page(0)
    build(pg)
    click(pg, "crecipes")
    check(int(pg.view) == 3 and int(pg.rpage) == 0, "P4 Unlocked recipes button -> view 3")
    cmds, evs = build(pg)
    st = sets_of(cmds)
    # the Python model of unlockedRows: per visible collection / reached tier its recipes, then the rest of compute()
    model, seen = [], set()
    for c in VIS:
        ctc = int(Reg.tierOf(R, c, Store.sum(d, R, c)))
        eff = int(Store.effTier(d, R, c))
        for t in range(1, eff + 1):
            for rid in [str(x) for x in Reg.recipesAt(c, t)]:
                if t > ctc and int(Util.bagRank(rid)) > int(Reg.BYP_BAGMAX):
                    continue
                if rid in seen:
                    continue
                seen.add(rid)
                model.append((str(Util.clip(Util.prettyRecipe(rid), 44)), "%s tier %s" % (R.name[c], Util.roman(t)) + (" (bought)" if t > ctc else "")))
    for rid in un:
        if rid not in seen:
            seen.add(rid)
            model.append((str(Util.clip(Util.prettyRecipe(rid), 44)), "Iron Ore - kept (unlocked before 0.2.8)" if rid in MINING else "auto rule"))
    got = [(st.get("SkyyCRr%dN" % i), st.get("SkyyCRr%dW" % i)) for i in range(14) if ("SkyyCRr%dN" % i) in st]
    check(got == model[:14] and len(model) <= 14, "P4 unlocked rows = the model (%d): %s / %s" % (len(model), got[:4], model[:4]))
    check(("Rare Mining Bag", "Iron Ore - kept (unlocked before 0.2.8)") in got and ("Unique Mining Bag", "Cobblestone tier III") in got
          and ("Normal Mining Bag", "Cobblestone tier I") in got, "P4 the kept Rare bag + the Cobblestone bags listed: %s" % got)
    check(st.get("SkyyCRSub", "").startswith("%d recipe(s). CRAFT opens /craft" % len(model)), "P4 sub line: %s" % st.get("SkyyCRSub"))
    check("Nothing matches? Use its Collections tab" in st.get("SkyyCRSub", ""), "FIX1 the list tells the player where a not-found recipe is: %s" % st.get("SkyyCRSub"))
    gos = [i for i in ids_of(cmds) if i.startswith("SkyyCRr") and i.endswith("Go")]
    check(len(gos) == len(model), "P4 one CRAFT per row: %d" % len(gos))
    check(all(x[2] is False for x in evdata(evs) if (x[1] or "").startswith("crcraft")), "P4 crcraft bindings do not lock")
    k = [n for n, _w in got].index("Unique Mining Bag")
    del FM.LINES[:]
    click(pg, "crcraft%d" % k)
    check(lines() == ["craft skyy sack mining medium"], "P4 CRAFT on the list row -> %s" % lines())
    # a stale row: the recipe is no longer unlocked (kept bit dropped + cobble gone)
    d.meta.remove("_keptbag.Mining")
    d.items.clear()
    del FM.LINES[:]
    click(pg, "crcraft%d" % k)
    check(lines() == [] and str(pg.status) == "That recipe is not unlocked yet.", "P4 stale CRAFT re-checked: %s" % pg.status)

    # ---------------- P5 locked list
    def locked_model(d, free=False):
        unl_ = unl(d)
        best, order = {}, []
        for c in VIS:
            sm = int(Store.sum(d, R, c))
            ctc = int(Reg.tierOf(R, c, sm))
            for t in range(ctc + 1, mx(c) + 1):
                for rid in [str(x) for x in Reg.recipesAt(c, t)]:
                    if rid in unl_ or (free and bool(Util.isBag(rid))):
                        continue
                    e = (rid, c, t, sm, thr(c, t))
                    if rid not in best:
                        best[rid] = e
                        order.append(rid)
                    else:
                        o = best[rid]
                        if (e[3] / e[4], -(e[4] - e[3])) > (o[3] / o[4], -(o[4] - o[3])):
                            best[rid] = e
        rows = []
        for rid in order:
            rid_, c, t, sm, th = best[rid]
            rows.append(((-(sm / th), th - sm, str(Util.clip(Util.prettyRecipe(rid), 40))),
                         (str(Util.clip(Util.prettyRecipe(rid), 40)), str(Util.clip("%s tier %s" % (R.name[c], Util.roman(t)), 36)),
                          "%s / %s" % (Util.fmt(sm), Util.fmt(th)), c)))
        rows.sort(key=lambda x: x[0])
        return [r for _k, r in rows]

    d = setup_player({COB: 38, BYID["Wheat"]: 120, IRON: 3})
    pg = page(0)
    cmds, evs = build(pg)
    check("SkyyCLocked" in ids_of(cmds) and any(x == ("#SkyyCLocked", "clocked", True) for x in evdata(evs)),
          "P5 home: LOCKED RECIPES button bound")
    click(pg, "clocked")
    check(int(pg.view) == 4, "P5 clocked -> view 4")
    lm = locked_model(d)
    pages = (len(lm) + 13) // 14
    seen_rows = []
    for pn in range(pages):
        cmds, evs = build(pg)
        st = sets_of(cmds)
        rows = [(st.get("SkyyCRr%dN" % i), st.get("SkyyCRr%dW" % i), st.get("SkyyCRr%dP" % i)) for i in range(14) if ("SkyyCRr%dN" % i) in st]
        check(rows == [r[:3] for r in lm[pn * 14:pn * 14 + 14]], "P5 locked page %d = the model: %s / %s" % (pn, rows[:2], lm[pn * 14:pn * 14 + 2]))
        check(st.get("SkyyCRPage") == "Page %d / %d" % (pn + 1, pages), "P5 page caption: %s" % st.get("SkyyCRPage"))
        check(not any(i.endswith("Go") and "craft" in i for i in ids_of(cmds)) and
              len([x for x in evdata(evs) if (x[1] or "").startswith("crgo")]) == 2 * len(rows), "P5 two crgo bindings per row (row + OPEN)")
        eb = evdata(evs)
        check(all(("#SkyyCRr%dSel" % i, "crgo%d" % i, True) in eb and ("#SkyyCRr%dGo" % i, "crgo%d" % i, True) in eb for i in range(len(rows))),
              "FIX3 every locked row: the whole row (#SkyyCRr<i>Sel) and OPEN both send crgo<i>")
        apx = " ".join(t for _p, t in appends_of(cmds))
        check(all(("Button #SkyyCRr%dSel " % i) in apx for i in range(len(rows))) and SUI.row_style("normal") in apx,
              "FIX3 the locked row is the vanilla list-row Button (kit row_style)")
        seen_rows += rows
        if pn == 0:
            check(st.get("SkyyCRSub", "").startswith("%d recipe(s) still locked, closest first" % len(lm)), "P5 sub: %s" % st.get("SkyyCRSub"))
            p0 = pg
            cmds0 = cmds
        click(pg, "crnext")
    check(len(seen_rows) == len(lm) and len(lm) > 14, "P5 every locked recipe listed once over %d pages (%d)" % (pages, len(lm)))
    click(pg, "crnext")
    cmds, _e = build(pg)
    check(int(pg.rpage) == pages - 1, "P5 next past the end stays on the last page")
    for _i in range(pages + 2):
        click(pg, "crprev")
    check(int(pg.rpage) == 0, "P5 prev back to page 1")
    # closest first: the first row's ratio is the highest; the Normal Mining Bag at Cobblestone tier I (38 / 50) and its progress text
    # (Cobblestone.1 = the Copper Pickaxe + the Normal Mining Bag: both 38 / 50, equal rows sort by name)
    top = [x for x in lm if x[1:3] == lm[0][1:3]]
    check(lm[0][1] == "Cobblestone tier I" and lm[0][2] == "38 / 50" and "Normal Mining Bag" in [x[0] for x in top]
          and [x[0] for x in top] == sorted(x[0] for x in top), "P5 closest first: %s" % (top,))
    ratios = [int(x[2].split(" / ")[0].replace(",", "")) / int(x[2].split(" / ")[1].replace(",", "")) for x in lm]
    check(all(a >= b for a, b in zip(ratios, ratios[1:])), "P5 rows sorted closest first")
    # free bags count as unlocked
    lmf = locked_model(d, free=True)
    setup_player({COB: 38, BYID["Wheat"]: 120, IRON: 3}, freebags=True)
    pgf = page(4)
    stf = sets_of(build(pgf)[0])
    check(not any("Bag" in x[0] for x in lmf) and stf.get("SkyyCRr0N") == lmf[0][0] and stf.get("SkyyCRSub", "").startswith("%d recipe(s)" % len(lmf)),
          "P5 free bags: no bag in the locked list (%d rows, %d with bags)" % (len(lmf), len(lm)))
    # nothing locked
    setup_player(dict((c, thr(c, mx(c))) for c in VIS))
    stn = sets_of(build(page(4))[0])
    check(stn.get("SkyyCRSub") == "No locked recipes - every recipe the collections unlock is yours." and "SkyyCRr0N" not in stn, "P5 everything maxed: empty list")

    # ---------------- P6 OPEN -> collection page -> Back to the list
    d = setup_player({COB: 38, BYID["Wheat"]: 120, IRON: 3})
    pg = page(4)
    build(pg)
    cmds6, evs6 = build(pg)
    sel0 = [x for x in evdata(evs6) if x[0] == "#SkyyCRr0Sel"]
    check(len(sel0) == 1 and sel0[0][1] == "crgo0", "FIX3 row 0 click binding: %s" % sel0)
    click(pg, sel0[0][1])
    check(int(pg.view) == 2 and int(pg.coll) == COB and int(pg.back) == 4, "P6 a click on row 0 -> Cobblestone page (view %s coll %s)" % (pg.view, pg.coll))
    cmds, _e = build(pg)
    txt = " ".join(t for _p, t in appends_of(cmds))
    check("Back to list" in txt, "P6 the collection page offers '< Back to list'")
    click(pg, "cback")
    check(int(pg.view) == 4, "P6 Back -> the locked list")
    click(pg, "chome")
    click(pg, "ccat1")
    build(pg)
    click(pg, "ccard0")
    cmds, _e = build(pg)
    check(int(pg.view) == 2 and int(pg.back) == 0 and "Back to list" not in " ".join(t for _p, t in appends_of(cmds)), "P6 a card click -> the category Back again")
    click(pg, "cback")
    check(int(pg.view) == 1, "P6 Back from a card -> the category")
    pg.rcol = None
    pg.view = 4
    click(pg, "crgo3")
    check(int(pg.view) == 4 and "not available" in str(pg.status), "P6 a stale OPEN -> result line: %s" % pg.status)

    # ---------------- P7 text fit
    W = K["COLL_TR_REW_GO"]
    worst = 0
    CUTS = []
    # FIX4 unit: whole parts drop first; a single too-wide part is cut inside it
    fx4 = str(Craft.fitPx("Copper Hoe - Unique Farming Bag - +500 coins - +40 Farming XP", 300))
    check(fx4 in ("Copper Hoe - ...", "Copper Hoe - Unique Farming Bag - ...") and SUI.text_width(fx4, 16) <= 300, "FIX4 fitPx drops whole parts: %s" % fx4)
    one_ = str(Craft.fitPx("A" * 200, 100))
    check(one_.endswith("...") and SUI.text_width(one_, 16) <= 100, "FIX4 one too-wide part cut inside: %s" % one_)
    # the longest sub lines of the lists fit the page width
    for sub_ in ("999 recipe(s). CRAFT opens /craft searching for it (Nothing matches? Use its Collections tab).",
                 "999 recipe(s) still locked, closest first. Click a row to see that collection.",
                 "Tree Sap tier VIII: 9 unlocked recipe(s) - CRAFT the one you want. Back returns to Tree Sap."):
        check(SUI.text_width(sub_, 16) <= K["COLL_IW"], "FIX sub line fits %d px: %s (%d)" % (K["COLL_IW"], sub_, SUI.text_width(sub_, 16)))
    for c in VIS:
        for t in range(1, mx(c) + 1):
            if len(Reg.recipesAt(c, t)) == 0:
                continue
            for b in (False, True):
                tx = str(Reg.rewardTextB(R, c, t, b)) + ("  (paid when reached)" if b else "")
                fx = str(Craft.fitPx(tx, W))   # the CRAFT row's cell text (CollPage.buildDetail: CollCraft.fitPx(rtx, CRAFTREW))
                w = SUI.text_width(fx, 16)
                worst = max(worst, w)
                check(w <= W and (fx == tx if SUI.text_width(tx, 16) <= W else
                                  ((fx.endswith(" - ...") and tx.startswith(fx[:-6] + " - ")) or (fx.endswith("...") and tx.startswith(fx[:-3])))),
                      "P7 CRAFT row text fits %d px: %s %d %s -> %s (%d px)" % (W, R.id[c], t, tx, fx, w))
                labels = [str(Util.recipeLabel(x)) for x in Reg.recipesAt(c, t)]
                names = tx.split(" - +")[0]
                if SUI.text_width(names + " - ...", 16) <= W:
                    check(all(l_ in fx for l_ in labels) and (fx == tx or fx.endswith(" - ...")),
                          "FIX4 the cut never hides a recipe name: %s %d: %s -> %s" % (R.id[c], t, tx, fx))
                else:
                    tally("FIX4 names alone too wide")
                if fx != tx:
                    COUNT["P7 cut"] = COUNT.get("P7 cut", 0) + 1
                    CUTS.append("%s %d%s: %s" % (R.id[c], t, " bought" if b else "", fx))
    wl = K["COLL_RL_SPEC"]["lk"].widths
    zero = locked_model(data({}))
    for n_, w_, p_, _c in zero:
        check(SUI.text_width(n_, 16) <= wl[0] and SUI.text_width(w_, 16) <= wl[1], "P7 locked row fits: %s / %s" % (n_, w_))
    check(SUI.text_width("99,999,999 / 99,999,999", 16) <= wl[2], "P7 the widest progress text fits %d px" % wl[2])
    for c_ in CUTS:
        print("   cut: " + c_)
    print("P4-P7. lists, paging, OPEN / Back, %d page builds checked (markup, ids, proven), widest CRAFT row text %d of %d px (%d cut with ...)" % (COUNT.get("P7 pages checked", 0), worst, W, COUNT.get("P7 cut", 0)))
    craft_on(False)
    BR.clear()

    # ---------------- M. the migration
    RW_OLD_JAR = str(jc("CollReg", "old").rewardsText())

    def start(folder, jar=JAR):
        """one server start in a FRESH loader (static state empty): the plugin's setup order; returns (loader, CollCobMig message)"""
        lo = loader(jar)

        def j(n):
            return JClass(PKG + n, loader=lo)
        R_, S_ = j("CollReg"), j("CollStore")
        R_.BASE = Paths.get(folder)
        S_.DIR = Paths.get(folder).resolve("counts")
        j("CollBagMigrate").run(Paths.get(folder))
        j("CollBypassMig").run(Paths.get(folder))
        R_.loadAll()
        msg = str(j("CollCobMig").run(Paths.get(folder))) if jar == JAR else ""
        j("CfgPub").start(Paths.get(os.path.dirname(folder)), None)
        j("CfgPub").shutdown()
        return lo, msg

    def compute_with(lo, folder, key):
        R_ = JClass(PKG + "CollReg", loader=lo)
        S_ = JClass(PKG + "CollStore", loader=lo)
        R_.BASE = Paths.get(folder)
        S_.DIR = Paths.get(folder).resolve("counts")
        R_.loadAll()
        recipes_from_rewards(R_)
        S_.DATA.clear()
        d_ = S_.dataK(key)
        return set(str(x) for x in JClass(PKG + "CollUnlocks", loader=lo).compute(d_))

    def expected_live(txt):
        """the 0.2.8 rewards text for a 0.2.7 file, built here line by line (independent of the Java)"""
        out = []
        ls = txt.split("\n")
        cob = {}
        for i, l in enumerate(ls):
            m = re.match(r"^(\w+)\.(\d+)=(.*)$", l)
            if m and m.group(1) == "Cobblestone":
                cob[int(m.group(2))] = i
        moved_to_new = {}
        for i, l in enumerate(ls):
            m = re.match(r"^Iron\.(\d+)=(recipe:Skyy_Sack_Mining_(\w+)_Recipe_Generated_0)$", l)
            if m and int(m.group(1)) in LADDER:
                t = int(m.group(1))
                if t in cob:
                    moved_to_new[i] = None
                    ls[cob[t]] = ls[cob[t]] + "," + m.group(2)
                else:
                    moved_to_new[i] = "Cobblestone.%d=%s" % (t, m.group(2))
        note = [x for x in ls if x.startswith("# Iron.3 and Iron.5 below also carry the Mining bag")]
        for i, l in enumerate(ls):
            if i in moved_to_new:
                if moved_to_new[i]:
                    out.append(moved_to_new[i])
                continue
            if l in note:
                continue
            l2 = re.sub(r"^#Iron\.(3|5)=recipe:Skyy_Sack_Mining_\w+_Recipe_Generated_0,", r"#Iron.\1=", l)
            l2 = l2.replace("# Mining from Iron, ", "# Mining from Cobblestone, ")
            out.append(l2)
            if l == "# bags: rarity ladder (0.2.3)":
                out.append("# bags: Mining from Cobblestone (0.2.8)")
        return "\n".join(out)

    def counts_keys(folder):
        cd = os.path.join(folder, "counts")
        return sorted(f[:-11] for f in os.listdir(cd) if f.endswith(".properties")) if os.path.isdir(cd) else []

    def props(path):
        out = {}
        for l in open(path, encoding="latin-1").read().split("\n"):
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k_, v_ = l.split("=", 1)
                out[k_] = v_
        return out

    if os.path.isdir(LIVE):
        live_before = snap(LIVE)
        lm_ = os.path.join(SCRATCH, "m1", "mods")
        d1 = os.path.join(lm_, "Skyy_SkyyCollections")
        shutil.copytree(LIVE, d1)
        orig = os.path.join(SCRATCH, "m1-orig", "mods", "Skyy_SkyyCollections")
        shutil.copytree(LIVE, orig)
        b0 = snap(d1)
        # the 0.2.7 unlock sets of every profile (old jar, the original copy)
        lo_old = loader(OLD)
        olds = dict((k_, compute_with(lo_old, orig, k_)) for k_ in counts_keys(orig))
        lo1, msg1 = start(d1)
        a1 = snap(d1)
        chg = sorted(k_ for k_ in set(b0) | set(a1) if b0.get(k_) != a1.get(k_))
        rw_old = b0["rewards.properties"].decode("latin-1")
        rw_new = a1["rewards.properties"].decode("latin-1")
        exp = expected_live(rw_old)
        check(rw_new == exp, "M1 live copy: rewards.properties = the expected text\n--- got\n%s\n--- want\n%s" % (rw_new[:3000], exp[:3000]))
        check(b"\r\n" not in a1["rewards.properties"] or b"\r\n" in b0["rewards.properties"], "M1 line endings kept")
        bp0, bp1 = bag_places_text(rw_old), bag_places_text(rw_new)
        print("M1. live copy before: Normal bags at %s" % sorted((k.split("_")[2], v) for k, v in bp0.items() if "_Small_" in k))
        check(bp1 == LADDER_WANT, "M1 live copy after: every Normal bag at tier I, Unique III, Rare V, Legendary VII, Mining on Cobblestone: %s" % sorted(bp1.items()))
        hist = [k_ for k_ in chg if k_.startswith("config-history/") and k_.endswith(".bak")]
        check(len(hist) == 1 and a1[hist[0]] == b0["rewards.properties"] and "rewards.properties" in hist[0], "M1 History: one .bak = the old bytes: %s" % hist)
        check("config-history/index.log" in chg and "0.2.8 Mining bag move" in a1["config-history/index.log"].decode("utf8"), "M1 History index line")
        cl = a1.get("config-changes.log", b"").decode("utf8")[len(b0.get("config-changes.log", b"").decode("utf8")):]
        cll = [l.split("\t") for l in cl.split("\n") if l]
        want_rows = []
        for t, tok in zip(LADDER, MINING):
            want_rows.append(("rewards[Iron.%d]" % t, "recipe:" + tok, "(none)"))
        check(all(any(r[1] == "SkyyCollections 0.2.8" and r[3] == "update" and (r[4], r[5], r[6]) == w and r[7] == "ok" for r in cll) for w in want_rows)
              and any(r[4] == "rewards[Cobblestone.1]" and r[6] == r[5] + ",recipe:" + MINING[0] for r in cll)
              and all(any(r[4] == "rewards[Cobblestone.%d]" % t and r[5] == "(none)" and r[6] == "recipe:" + MINING[j] for r in cll) for j, t in enumerate(LADDER) if j > 0)
              and len(cll) == 8, "M1 config-changes.log: 8 ok lines (4 Iron removals, Cobblestone.1 append, 3 adds): %s" % cll)
        check("migration-bags.log" in chg and "0.2.8: the Mining bag ladder moves" in a1["migration-bags.log"].decode("utf8"), "M1 migration-bags.log block")
        # kept bits per profile: the Python model of 0.2.7's rule on the original counts
        thr_iron = [thr(IRON, t) for t in range(1, mx(IRON) + 1)]
        kept_expect = {}
        for k_ in counts_keys(orig):
            p_ = props(os.path.join(orig, "counts", k_ + ".properties"))
            if p_.get("_schema") != "2":
                continue
            s_ = sum(int(p_.get(it, "0") or 0) for it in [str(x) for x in R.items[IRON]])
            ct_ = len([x for x in thr_iron if s_ >= x])
            b_ = min(int(p_.get("_bought.Iron", "0") or 0), mx(IRON))
            bits = 0
            for j, t in enumerate(LADDER):
                if t <= ct_ or (t <= b_ and j + 1 <= 2):
                    bits |= 1 << j
            if bits:
                kept_expect[k_] = bits
        cchg = sorted(k_ for k_ in chg if k_.startswith("counts/"))
        check(cchg == sorted("counts/%s.properties" % k_ for k_ in kept_expect), "M1 counts files written = profiles with an Iron Mining bag: %s / %s" % (cchg, kept_expect))
        for k_, bits in kept_expect.items():
            p1 = props(os.path.join(d1, "counts", k_ + ".properties"))
            p0 = props(os.path.join(orig, "counts", k_ + ".properties"))
            check(p1.get("_keptbag.Mining") == str(bits) and dict((a, b) for a, b in p1.items() if a != "_keptbag.Mining") == p0,
                  "M1 %s: _keptbag.Mining=%s, every other value kept" % (k_, bits))
        check(sorted(chg) == sorted(["rewards.properties", "config-changes.log", "config-history/index.log", "migration-bags.log"] + hist + cchg),
              "M1 start 1 changed exactly the expected files: %s" % chg)
        check("Mining bags now unlock from Cobblestone" in msg1, "M1 INFO line: %s" % msg1)
        # never take away; only Mining bags new
        for k_ in counts_keys(d1):
            nw = compute_with(lo1, d1, k_)
            check(olds[k_] <= nw, "M1 %s: every 0.2.7 recipe still unlocked (lost %s)" % (k_, sorted(olds[k_] - nw)))
            check(all(x in MINING for x in nw - olds[k_]), "M1 %s: only Mining bags are new: %s" % (k_, sorted(nw - olds[k_])))
        _lo2, msg2 = start(d1)
        a2 = snap(d1)
        check(a2 == a1 and msg2 == "", "M1 start 2 writes nothing: %s" % sorted(k_ for k_ in set(a1) | set(a2) if a1.get(k_) != a2.get(k_)))
        check(snap(LIVE) == live_before, "M1 the live folder is untouched")
        print("M1. live copy: %s; kept: %s" % (msg1, kept_expect))
    else:
        print("note: no live Skyy_SkyyCollections folder - M1 skipped")

    # ---------------- M2 edited copies
    def folder(name, rewards_bytes, counts=None):
        dd = os.path.join(SCRATCH, "m2", name, "mods", "Skyy_SkyyCollections")
        os.makedirs(os.path.join(dd, "counts"))
        if rewards_bytes is not None:
            open(os.path.join(dd, "rewards.properties"), "wb").write(rewards_bytes)
        for k_, body in (counts or {}).items():
            open(os.path.join(dd, "counts", k_ + ".properties"), "w").write(body)
        return dd

    def twice(dd):
        b_ = snap(dd)
        _l, m1 = start(dd)
        a_ = snap(dd)
        _l, m2 = start(dd)
        a2_ = snap(dd)
        check(a2_ == a_ and m2 == "", "M2 %s: the second start writes nothing" % os.path.basename(os.path.dirname(os.path.dirname(dd))))
        return b_, a_, m1

    base_txt = RW_OLD_JAR
    # (a) the 0.2.7 default file -> the 0.2.8 default table (same entries as a fresh 0.2.8 file)
    dd = folder("default027", base_txt.encode("latin-1"))
    b_, a_, m_ = twice(dd)
    new_txt = a_["rewards.properties"].decode("latin-1")
    lo_ = loader(JAR)
    tbl = JClass(PKG + "CollCobMig", loader=lo_)
    fresh_rw = str(JClass(PKG + "CollReg", loader=lo_).rewardsText())
    t_new = tbl.table(JArray(JString)(new_txt.split("\n")))
    t_fresh = tbl.table(JArray(JString)(fresh_rw.split("\n")))
    check(t_new.equals(t_fresh), "M2 the 0.2.7 default file -> exactly the 0.2.8 default table")
    check(sorted(l for l in new_txt.split("\n") if l.startswith("#")) == sorted(l for l in fresh_rw.split("\n") if l.startswith("#")),
          "M2 0.2.7 default -> the 0.2.8 default comment lines")
    # (b) hand-edited Iron.3 and Cobblestone.1 -> both rarities stay; the others move
    t2 = base_txt.replace("Iron.3=recipe:%s\n" % MINING[1], "Iron.3=recipe:%s,coins:5\n" % MINING[1]).replace(
        "Cobblestone.1=recipe:Tool_Pickaxe_Copper_Recipe_Generated_0\n", "Cobblestone.1=recipe:Tool_Pickaxe_Copper_Recipe_Generated_0,coins:10\n")
    check(t2 != base_txt, "M2 (b) the fixture really edits the file")
    dd = folder("hand", t2.encode("latin-1"))
    b_, a_, m_ = twice(dd)
    nt = a_["rewards.properties"].decode("latin-1")
    nls = nt.split("\n")
    check("Iron.3=recipe:%s,coins:5" % MINING[1] in nls and "Iron.1=recipe:%s" % MINING[0] in nls
          and "Cobblestone.1=recipe:Tool_Pickaxe_Copper_Recipe_Generated_0,coins:10" in nls
          and not any(l.startswith(("Iron.5=", "Iron.7=", "Cobblestone.3=")) for l in nls)
          and "Cobblestone.5=recipe:%s" % MINING[2] in nls and "Cobblestone.7=recipe:%s" % MINING[3] in nls,
          "M2 (b) hand-edited Iron.3 / Cobblestone.1 kept, Rare / Legendary moved: %s" % [l for l in nls if l.startswith(("Iron", "Cobble"))])
    lg = a_["migration-bags.log"].decode("utf8")
    check(lg.count("kept hand-edited line") == 2 and "2 of 4 moved" in m_ and "2 hand-edited line(s) kept" in m_, "M2 (b) logged: %s" % m_)
    # (c) Iron.5 missing + Cobblestone.3 already lists the bag
    t3 = base_txt.replace("Iron.5=recipe:%s\n" % MINING[2], "").replace("Cobblestone.4=", "Cobblestone.3=recipe:%s\nCobblestone.4=" % MINING[1])
    dd = folder("missing", t3.encode("latin-1"))
    b_, a_, m_ = twice(dd)
    nt = a_["rewards.properties"].decode("latin-1")
    check("Iron." not in "\n".join(l for l in nt.split("\n") if not l.startswith("#")) and nt.count("Cobblestone.3=") == 1
          and "Cobblestone.5=" not in nt and "3 of 4 moved" in m_, "M2 (c) Iron.5 missing -> Rare left; Cobblestone.3 already had it -> Iron.3 removed only: %s" % m_)
    # (d) CRLF + a non-ASCII byte, no final newline
    t4 = (base_txt.rstrip("\n").replace("\n", "\r\n").replace("# SkyyCollections 0.2 - tier rewards", "# SkyyCollections 0.2 - tier rewards \xe9")).encode("latin-1")
    dd = folder("crlf", t4)
    b_, a_, m_ = twice(dd)
    nb = a_["rewards.properties"]
    check(nb.count(b"\n") == nb.count(b"\r\n") and b"\xe9" in nb and not nb.endswith(b"\n") and "4 of 4 moved" in m_,
          "M2 (d) CRLF kept on every line, the non-ASCII byte kept, no final newline added: %s" % m_)
    exp_d = tbl.update(base_txt.rstrip("\n").replace("\n", "\r\n"))
    check(str(exp_d[0]).replace("\r\n", "\n") == tbl.update(base_txt.rstrip("\n"))[0], "M2 (d) CRLF text = the LF text's result")
    # (e) a fresh 0.2.8 folder (the loader writes the default) and (f) a 0.2.2 file through CollBagMigrate
    dd = folder("fresh", None)
    b_, a_, m_ = twice(dd)
    check(m_ == "" and "# bags: Mining from Cobblestone (0.2.8)" in a_["rewards.properties"].decode("latin-1"), "M2 (e) a fresh folder: the 0.2.8 default, no update")
    rw022 = open(os.path.join(SCRATCH, "m1-orig", "mods", "Skyy_SkyyCollections", "rewards-0.2.properties"), "rb").read() if os.path.isfile(os.path.join(SCRATCH, "m1-orig", "mods", "Skyy_SkyyCollections", "rewards-0.2.properties")) else None
    if rw022 is not None:
        dd = folder("v022", rw022)
        b_, a_, m_ = twice(dd)
        nt = a_["rewards.properties"].decode("latin-1")
        ent = tbl.table(JArray(JString)(nt.split("\n")))
        check(m_ == "" and nt.count("# bags: Mining from Cobblestone (0.2.8)") == 1 and nt.count("# bags: rarity ladder (0.2.3)") == 1
              and all(MINING[j] in [str(x)[7:] for x in (ent.get("cobblestone.%d" % t) or [])] for j, t in enumerate(LADDER))
              and not any("Mining" in str(x) for t in LADDER for x in (ent.get("iron.%d" % t) or [])),
              "M2 (f) Skyy's 0.2.2 file through CollBagMigrate -> Mining ladder on Cobblestone, both markers, no 0.2.8 update")
    # pure step corner cases
    check(tbl.update(fresh_rw) is None, "M2 the marker -> nothing to do")
    r0 = tbl.update("Iron.1=recipe:%s" % MINING[0])
    check(str(r0[0]) == "# bags: Mining from Cobblestone (0.2.8)\nIron.1=recipe:%s" % MINING[0] and bool(r0[5]) and int(r0[3]) == 0
          and "Cobblestone.1: no line (an admin removed it)" in str(r0[2]), "M2 a one-line file (Cobblestone.1 removed by hand -> the bag stays): %r" % str(r0[0]))
    r0 = tbl.update("Cobblestone.1=recipe:Tool_Pickaxe_Copper_Recipe_Generated_0\nIron.3=recipe:%s" % MINING[1])
    check(str(r0[0]) == "# bags: Mining from Cobblestone (0.2.8)\nCobblestone.1=recipe:Tool_Pickaxe_Copper_Recipe_Generated_0\nCobblestone.3=recipe:%s" % MINING[1]
          and int(r0[3]) == 2 and bool(r0[5]), "M2 two lines: Iron.3 -> Cobblestone.3 in place: %r" % str(r0[0]))
    r1 = tbl.update("")
    check(str(r1[0]) == "# bags: Mining from Cobblestone (0.2.8)\n" or str(r1[0]) == "# bags: Mining from Cobblestone (0.2.8)", "M2 an empty file: %r" % str(r1[0]))
    print("M2. edited copies: hand edits kept + logged, missing / present lines, CRLF + non-ASCII + no final newline, fresh, 0.2.2 - each started twice")

    # ---------------- M3 History unwritable; M4 a counts file that cannot be written
    def iron_counts(n):
        return "_schema=2\nOre_Iron=%d\n" % n
    dd = folder("nohist", base_txt.encode("latin-1"))
    open(os.path.join(dd, "config-history"), "w").write("not a folder")
    b_ = snap(dd)
    _l, m_ = start(dd)
    a_ = snap(dd)
    check(a_["rewards.properties"] == b_["rewards.properties"] and m_ == "", "M3 config-history unwritable -> rewards.properties untouched")
    os.remove(os.path.join(dd, "config-history"))
    _l, m_ = start(dd)
    check("4 of 4 moved" in m_ and "# bags: Mining from Cobblestone (0.2.8)" in open(os.path.join(dd, "rewards.properties"), encoding="latin-1").read(),
          "M3 retried at the next start once it can be written: %s" % m_)
    dd = folder("rocounts", base_txt.encode("latin-1"), {US: iron_counts(thr(IRON, 3))})
    cf = os.path.join(dd, "counts", US + ".properties")
    os.chmod(cf, stat.S_IREAD)
    rocd = os.path.join(dd, "counts")
    b_ = snap(dd)
    try:
        _l, m_ = start(dd)
    finally:
        os.chmod(cf, stat.S_IREAD | stat.S_IWRITE)
    a_ = snap(dd)
    check(a_.get("rewards.properties") == b_.get("rewards.properties") and m_ == "" and not any(k_.endswith(".bak") for k_ in a_),
          "M4 a counts file that cannot be written -> nothing moved, no History")
    _l, m_ = start(dd)
    check("1 profile(s) keep" in m_ and props(cf).get("_keptbag.Mining") == "3", "M4 retried: the profile keeps Normal + Unique: %s" % m_)

    # ---------------- M5 kept bits
    cases = {
        "count3": (iron_counts(thr(IRON, 3)), "3"),
        "count7": (iron_counts(thr(IRON, 7)), "15"),
        "count2": (iron_counts(thr(IRON, 2)), "1"),
        "none": (iron_counts(thr(IRON, 1) - 1), None),
        "bought5": ("_schema=2\n_bought.Iron=5\n", "3"),
        "bought5rare": ("_schema=2\n_bought.Iron=5\nOre_Iron=%d\n" % thr(IRON, 5), "7"),
        "or": ("_schema=2\nOre_Iron=%d\n_keptbag.Mining=8\n" % thr(IRON, 1), "9"),
        "old01": ("Ore_Iron=99999\n", None),
    }
    dd = folder("kept", base_txt.encode("latin-1"), dict((k_, v[0]) for k_, v in cases.items()))
    _l, m_ = start(dd)
    for k_, (_body, want) in cases.items():
        got_ = props(os.path.join(dd, "counts", k_ + ".properties")).get("_keptbag.Mining")
        check(got_ == want, "M5 %s: _keptbag.Mining %s (want %s)" % (k_, got_, want))
    check("6 profile(s) keep" in m_ and "1 old 0.1 counts file(s) skipped" in m_, "M5 summary: %s" % m_)
    lo_k = loader(JAR)
    for k_, (_body, want) in cases.items():
        if k_ == "old01":
            continue
        nw = compute_with(lo_k, dd, k_)
        bits = int(want or 0)
        check(all((MINING[j] in nw) == bool(bits & (1 << j)) for j in range(4)), "M5 %s: compute gives exactly the kept bags %s" % (k_, sorted(nw & set(MINING))))
    print("M3-M5. History / counts failures leave everything untouched and retry; kept bits per profile")


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (python tools/collections_0_2_8_patch.py, python SkyyCollections/build_skyycollections_0.2.8.py)")
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
