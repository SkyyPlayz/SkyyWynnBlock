"""Bare-JVM harness for SkyyCollections 0.2.10 (tools/collections_0_2_10_patch.py; research/Code-Structure-Audit.md "Data-safety fixes
found" + 9e; Skyy 2026-10-13: "lets audit the code structure, and make sure they are working together in the smoothest easiest lag free
way possible"). Derived from test_skyycollections_0.2.9.py: every 0.2.9 section runs again on 0.2.10 (regression), B / C re-aimed at
0.2.9 -> 0.2.10, plus the new W and P sections.

    python SkyyCollections/test_skyycollections_0.2.10.py [--jar <SkyyCollections-0.2.10.jar>] [--old <SkyyCollections-0.2.9.jar>]
                                                          [--dir <scratch>] [--live <Skyy_SkyyCollections folder>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), every jar in its own
class loader; a FRESH loader of a jar = one server start.
  A  every class of both jars loads, verifies and initialises
  B  class bytes 0.2.9 -> 0.2.10: the same classes (+ the fixer's CollThreads, CollFlushJob); changed = exactly CollIO (bodies moved to *0 methods, per-file locks; field LOCKS;
     added lockOf / read0 / write0 / writeText0 / moveReplace0 / append0 / copyIfMissing0) and CollUnlocks.publishLocked; every other
     class byte-identical / version constants (the shared UI kit hash in the ready line tolerated; the config kit's Cfg* classes follow
     tools/skyycfg.py - listed); manifest Version / Name only; every non-class file byte-identical; CollReg (the default registry /
     rewards / config texts) = 0.2.9 (the Hytale 0.7.0 assets' new ids are left out)
  E  engine-access audit of every engine reference new in 0.2.10
  C  the page id = COLL_PAGE_CHECKED = the kit's page now = 0.2.9's
  T / K / V  0.2.9's catTotal, sacks:v2 and v2Tick sections, EXECUTED on 0.2.10 (regression)
  W  CollIO EXECUTED: write = tmp + FileOutputStream + getFD().sync() + ATOMIC_MOVE (bytecode), the file round-trips (counts + _paid /
     _paidxp markers), no .tmp left; a stale .tmp from a crash is overwritten; a held target (java.io.FileInputStream = no share-delete on
     Windows, the virus-scanner case) makes write retry 5 x 20 ms and THROW with the old file intact; WHILE that write retries, another
     profile's write / read / log append finishes at once (0.2.9 control: blocked behind the global lock); two threads x 200 writes of
     the SAME file never interleave; CollStore.save of a paid marker -> a fresh load has it; a failed save keeps the key DIRTY and the
     next flush writes it
  P  publish only on change: a counting skyy.bridge map - publish() again on the same data puts coll:recipes / coll: / coll:score /
     coll:epoch ONCE; a collect below the next tier re-puts no recipes and bumps no epoch; crossing a tier puts coll:recipes again + the
     epoch bumps once; the values = 0.2.9's publish on the same file (control: 0.2.9 re-puts on every call)
  W6 FIXER (review): the 10 s flush on the PRIVATE writer, EXECUTED - CollSaver.run on its 10th tick hands the flush to the daemon
     "SkyyCollections-writer" and returns at once while that flush waits on a held file (the caller never does the fsync / retry);
     FLUSHQ keeps at most one flush queued; the flush writes the paid marker; no writer = inline (0.2.9); bytecode: setup makes the
     writer, shutdown stops it (awaitTermination) BEFORE the inline flushes; the Buy click keeps its own inline save
  W7 FIXER 2 (review): CollRewards.settle that paid -> CollStore.saveKeySoon: the _paid / _paidxp markers are on disk at once (one key
     job on the writer, no 10 s flush); a fresh load right after (= a crash) pays the tier NOT twice; no writer = inline; a save waiting
     on the file lock takes its snapshot after it gets the lock (the newer _bought is written, never an older snapshot)
  S  START TWICE on a scratch COPY of Skyy's live Skyy_SkyyCollections folder (0.2.9's section) + S5 every live profile publishes the
     same coll:recipes / coll: / coll:score on 0.2.9 and 0.2.10
Nothing outside the scratch folder is written (default tools/dev/scratch/perfstore/coll0210, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.10", "0.2.9"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "perfstore", "coll0210")))
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

    # ---------------- B. class bytes (0.2.9 -> 0.2.10)
    old, new = CB["old"], CB["new"]
    check(set(new) - set(old) == {PKG + "CollFlushJob", PKG + "CollThreads", PKG + "CollKeySaveJob"} and not (set(old) - set(new)),
          "B. the same classes + the fixer's CollThreads / CollFlushJob / CollKeySaveJob: %s" % sorted(set(old) ^ set(new)))
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    SKYYUI = re.compile(r"skyyui [0-9.]+ [0-9a-f]{12}")

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

    def nv(x):
        # the Hytale 0.7.0 engine declares getChunkSectionReferenceAtBlock in ChunkGrid (ChunkStore's superclass): recompiling the same
        # 0.2.9 source against it names the declaring class - the JVM resolves the 0.2.9 ref to the same method (CollDrops.decoAt)
        x = x.replace("storage.ChunkGrid.getChunkSectionReferenceAtBlock", "storage.ChunkStore.getChunkSectionReferenceAtBlock").replace("storage.ChunkGrid.getStore", "storage.ChunkStore.getStore")
        return SKYYUI.sub("skyyui #", x.replace(OLD_VERSION, VERSION))

    def vonly(a, b):
        return len(a) == len(b) and all(x == y or nv(x) == nv(y) for x, y in zip(a, b))

    P_ = "Ljava/nio/file/Path;"
    DECLARED = {
        "CollIO": ["append", "copyIfMissing", "moveReplace", "read", "readLines", "write", "writeText"],
        "CollUnlocks": ["publishLocked"],
        "CollStore": ["<clinit>", "save"], "CollSaver": ["run"], "SkyyCollectionsPlugin": ["setup", "shutdown"],   # fixer: the private flush writer
        "CollRewards": ["settle"],   # fixer 2: the paid markers saved right after a payout
    }
    ADDED = {
        "CollIO": sorted(["lockOf(%s)Ljava/lang/Object;" % P_, "read0(%s)Ljava/util/Properties;" % P_,
                          "write0(%sLjava/lang/String;Ljava/util/Properties;)V" % P_, "writeText0(%sLjava/lang/String;)V" % P_,
                          "moveReplace0(%s%s)V" % (P_, P_), "append0(%sLjava/lang/String;)V" % P_, "copyIfMissing0(%s%s)Z" % (P_, P_),
                          "<clinit>"]),
    }
    ADDED["CollStore"] = ["flushSoon()V", "save0(Ljava/lang/String;)Z", "saveKeySoon(Ljava/lang/String;)V"]   # fixer (+ fixer 2)
    FIELDS = {"CollIO": ["LOCKS"], "CollStore": ["FLUSHES", "FLUSHQ", "KEYQ", "KEYSAVES", "WRITER"]}
    kinds, kit = {}, []
    MO, MN = {}, {}
    for n in sorted(set(old) & set(new)):
        short = n[len(PKG):]
        if old[n] == new[n]:
            kinds[short] = "identical"
            continue
        po, pn = ct(old[n]), ct(new[n])
        fo = set(str(f.getName()) for f in po.getDeclaredFields())
        fn = set(str(f.getName()) for f in pn.getDeclaredFields())
        mo, mn = methods(po), methods(pn)
        MO[short], MN[short] = mo, mn
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        if short.startswith("Cfg"):
            kit.append(short)
            kinds[short] = "config kit (tools/skyycfg.py)"
            continue
        check(sorted(fn - fo) == FIELDS.get(short, []) and not (fo - fn), "B. %s: fields added / gone: %s" % (short, sorted(fo ^ fn)))
        check(not (set(mo) - set(mn)) and sorted(set(mn) - set(mo)) == ADDED.get(short, []),
              "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        kinds[short] = ("methods %s" % changed) if changed else "version constants"
    for k in DECLARED:
        check(k in kinds and kinds[k].startswith("methods"), "B. %s is one of the changed classes: %s" % (k, kinds.get(k)))
    check(kinds.get("CollReg") in ("identical", "version constants"), "B. CollReg (the default registry / rewards / config texts) = 0.2.9: %s"
          % kinds.get("CollReg"))
    io_o, io_n = MO["CollIO"], MN["CollIO"]
    for nm in ("read", "writeText", "moveReplace", "append", "copyIfMissing"):
        ko = [k for k in io_o if k.startswith(nm + "(")][0]
        kn = [k for k in io_n if k.startswith(nm + "0(")][0]
        check(io_o[ko] == io_n[kn], "B. CollIO.%s0 is 0.2.9's %s body, instruction for instruction" % (nm, nm))
    w0 = " ".join(io_n[[k for k in io_n if k.startswith("write0(")][0]])
    check("FileDescriptor.sync" in w0 and "getFD" in w0 and "moveReplace0" in w0 and "Files.newOutputStream" not in w0,
          "B. CollIO.write0: FileOutputStream + getFD().sync() then moveReplace0 (REPLACE_EXISTING + ATOMIC_MOVE)")
    mr0 = " ".join(io_n[[k for k in io_n if k.startswith("moveReplace0(")][0]])
    check("ATOMIC_MOVE" in mr0 and "Thread.sleep" in mr0, "B. moveReplace0: ATOMIC_MOVE first, the 5 x 20 ms retry")
    for nm in ("read", "write", "readLines", "writeText", "moveReplace", "append", "copyIfMissing"):
        k = [x for x in io_n if x.startswith(nm + "(")][0]
        code = " ".join(io_n[k])
        check("monitorenter" in code and "CollIO.lockOf" in code and "Thread.sleep" not in code,
              "B. CollIO.%s: synchronized on lockOf(path) only" % nm)
    sync_ = [str(m.getName()) for m in ct(new[PKG + "CollIO"]).getDeclaredMethods() if int(m.getModifiers()) & 0x20]
    check(not sync_, "B. no CollIO method is synchronized on the class any more: %s" % sync_)
    pl_ = " ".join(MN["CollUnlocks"]["publishLocked(Ljava/util/UUID;)I"])
    check(pl_.count("String.equals") >= 2 and "Long.equals" in pl_, "B. publishLocked compares before each put")
    mo_, mn_ = manifest(OLD), manifest(JAR)
    check(mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyyCollections"
          and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) == dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")),
          "B. manifest: only Version / Name changed")
    zo_, zn_ = zipfile.ZipFile(OLD), zipfile.ZipFile(JAR)
    nc_ = sorted(n_ for n_ in set(zo_.namelist()) | set(zn_.namelist()) if not n_.endswith(".class") and not n_.endswith("/") and n_ != "manifest.json"
                 and (n_ not in zo_.namelist() or n_ not in zn_.namelist() or zo_.read(n_) != zn_.read(n_)))
    check(not nc_, "B. every non-class file byte-identical: %s" % nc_)
    ident = sorted(k for k, v in kinds.items() if v == "identical")
    print("B. %d classes byte-identical; version constants only: %s; method-level: %s; config kit: %s" % (
        len(ident), sorted(k for k, v in kinds.items() if v == "version constants"),
        dict((k, v) for k, v in kinds.items() if v.startswith("methods")), kit))

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
    print("E. engine-access audit: %d engine references new in 0.2.10 (all resolved): %s"
          % (len(added), ["%s.%s" % (c.split(".")[-1], n) for _k, c, n, _t in added]))

    # ---------------- C. page id
    chk = script_const("COLL_PAGE_CHECKED")
    plug = new[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mm = re.search(r"0\.2\.10 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug)
    plug_old = old[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mo2 = re.search(r"0\.2\.9 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug_old)
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

    # ---------------- W. CollIO (0.2.10): fsync + atomic move, per-file locks, the retry outside the global lock
    import threading, time as _time
    Files_, Props = JClass("java.nio.file.Files"), JClass("java.util.Properties")
    FIS = JClass("java.io.FileInputStream")
    IO_n, IO_o = jc("CollIO"), jc("CollIO", "old")
    wdir = os.path.join(SCRATCH, "w-io")
    os.makedirs(wdir)
    wp = Paths.get(wdir)

    def props(d_):
        p_ = Props()
        for k_, v_ in d_.items():
            p_.setProperty(k_, str(v_))
        return p_

    def fileprops(path_):
        out_ = {}
        for ln in open(path_, encoding="latin-1").read().splitlines():
            if ln and not ln.startswith("#") and "=" in ln:
                a_, b_ = ln.split("=", 1)
                out_[a_] = b_
        return out_

    IO_n.write(wp, "k1", props({"Rock_Stone_Cobble": 5, "_paid.Cobblestone": 3, "_paidxp.Cobblestone": 3, "_schema": 2}))
    f1 = os.path.join(wdir, "k1.properties")
    check(fileprops(f1) == {"Rock_Stone_Cobble": "5", "_paid.Cobblestone": "3", "_paidxp.Cobblestone": "3", "_schema": "2"}
          and not os.path.exists(f1 + ".tmp"), "W1 write: the counts + paid markers round-trip, no .tmp left")
    rd_ = IO_n.read(Paths.get(f1))
    check(str(rd_.getProperty("_paid.Cobblestone")) == "3", "W1 read() through the per-file lock")
    open(os.path.join(wdir, "k1.properties.tmp"), "w").write("garbage from a crash")
    IO_n.write(wp, "k1", props({"Rock_Stone_Cobble": 6, "_paid.Cobblestone": 4, "_schema": 2}))
    check(fileprops(f1).get("_paid.Cobblestone") == "4" and not os.path.exists(f1 + ".tmp"), "W2 a stale .tmp left by a crash is overwritten")
    # the held target: a java.io.FileInputStream (no FILE_SHARE_DELETE on Windows) blocks the replace -> retries, then throws, old file kept
    IO_n.write(wp, "k2", props({"_paid.Oak": 1}))
    f2 = os.path.join(wdir, "k2.properties")

    def blocked(IO_, key_):
        """hold k2; one thread writes k2 (retries ~100 ms then throws), the main thread meanwhile writes / reads / appends other files"""
        hold = FIS(f2)
        res_ = {}

        def slow():
            t0 = _time.perf_counter()
            try:
                IO_.write(wp, "k2", props({"_paid.Oak": 2}))
                res_["slow"] = "no throw"
            except Exception as e:
                res_["slow"] = "threw %s" % type(e).__name__
            res_["slow_ms"] = (_time.perf_counter() - t0) * 1000.0
        jt = threading.Thread(target=slow)
        jt.start()
        _time.sleep(0.015)
        t0 = _time.perf_counter()
        IO_.write(wp, key_, props({"_paid.Iron": 1}))
        IO_.read(Paths.get(os.path.join(wdir, key_ + ".properties")))
        IO_.append(Paths.get(os.path.join(wdir, key_ + ".log")), "line\n")
        res_["other_ms"] = (_time.perf_counter() - t0) * 1000.0
        jt.join()
        hold.close()
        return res_
    rn = blocked(IO_n, "k3")
    check(rn["slow"].startswith("threw") and rn["slow_ms"] >= 60.0 and fileprops(f2).get("_paid.Oak") == "1",
          "W3 a held target: the write retries (%.0f ms) and throws (%s), the old file is intact (paid 1)" % (rn["slow_ms"], rn["slow"]))
    check(rn["other_ms"] < 40.0, "W3 meanwhile ANOTHER profile's write + read + log append finished in %.1f ms (not behind the retry)" % rn["other_ms"])
    ro = blocked(IO_o, "k4")
    check(ro["other_ms"] >= 40.0, "W3 control: on 0.2.9 the same other-profile work waited %.0f ms behind the global lock" % ro["other_ms"])
    # the same file from two threads: never interleaved (each read-back is one whole generation)
    errs = []

    def hammer(tag):
        for i in range(200):
            try:
                IO_n.write(wp, "k5", props(dict(("x%d" % j, "%s-%d" % (tag, i)) for j in range(20))))
                g = IO_n.read(Paths.get(os.path.join(wdir, "k5.properties")))
                vals_ = set(str(g.getProperty("x%d" % j)) for j in range(20))
                if len(vals_) != 1:
                    errs.append(sorted(vals_)[:3])
            except Exception as e:
                errs.append("threw %s" % e)
    ths = [threading.Thread(target=hammer, args=(t_,)) for t_ in ("a", "b")]
    for t_ in ths:
        t_.start()
    for t_ in ths:
        t_.join()
    check(not errs, "W4 two threads x 200 writes + reads of the SAME file: every read-back is one whole generation: %s" % errs[:3])
    # CollStore.save / dirty on failure (through the real store)
    reset_store()
    BR.clear()
    write_counts(US, {"Rock_Stone_Cobble": thr(COB, 2)}, {"_paid.Cobblestone": 2, "_paidxp.Cobblestone": 2})
    d5 = Store.dataK(US)
    Store.setMeta(d5, US, "_paid.Cobblestone", 3)
    Store.flushDirty()
    reset_store()
    d6 = Store.dataK(US)
    check(int(Store.meta(d6, "_paid.Cobblestone")) == 3, "W5 CollStore.save -> a fresh load has the new paid marker (3)")
    cf = os.path.join(wbase, "counts", US + ".properties")
    hold = FIS(cf)
    Store.setMeta(d6, US, "_paid.Cobblestone", 4)
    Store.flushDirty()
    still = bool(Store.DIRTY.containsKey(US))
    hold.close()
    check(still and fileprops(cf).get("_paid.Cobblestone") == "3", "W5 a save that cannot replace the file keeps the key DIRTY, the file keeps paid 3")
    Store.flushDirty()
    check(fileprops(cf).get("_paid.Cobblestone") == "4" and not Store.DIRTY.containsKey(US), "W5 the next flush writes it (paid 4)")
    # ---------------- W6 (fixer): the 10 s flush on the private writer
    import time as _t6
    Exs6 = JClass("java.util.concurrent.Executors")
    Thr6 = jc("CollThreads")
    Store.WRITER = Exs6.newSingleThreadExecutor(Thr6())
    try:
        @JImplements("java.util.concurrent.Callable")
        class TName6(object):
            @JOverride
            def call(self):
                th = JClass("java.lang.Thread").currentThread()
                return str(th.getName()) + "|" + str(th.isDaemon())
        nm6 = str(Store.WRITER.submit(TName6()).get())
        check(nm6 == "SkyyCollections-writer|True", "W6 the writer is a daemon thread named SkyyCollections-writer: %s" % nm6)
        d7 = Store.dataK(US)
        Store.setMeta(d7, US, "_paid.Cobblestone", 5)
        f0 = int(Store.FLUSHES.get())
        hold6 = FIS(cf)        # the flush on the writer now retries 5 x 20 ms on the held file
        sv = Saver()
        sv.ticks = 9
        t0 = _t6.perf_counter()
        sv.run()               # the 10th tick: the flush is handed to the writer
        ms_run = (_t6.perf_counter() - t0) * 1000.0
        for _i in range(5):
            Store.flushSoon()  # while that flush is queued / running: no second job
        _t6.sleep(0.4)
        busy_f = int(Store.FLUSHES.get()) - f0
        hold6.close()
        still6 = bool(Store.DIRTY.containsKey(US))
        Store.flushSoon()      # the writer is free again: the next flush writes paid 5
        Store.WRITER.submit(TName6()).get()
        check(ms_run < 60 and busy_f == 1 and still6 and fileprops(cf).get("_paid.Cobblestone") == "5" and not Store.DIRTY.containsKey(US)
              and int(Store.FLUSHES.get()) - f0 == 2 and not bool(Store.FLUSHQ.get()),
              "W6 CollSaver.run returned in %.1f ms while its flush retried on the writer; 5 more calls meanwhile = %d job; the failed flush kept "
              "the key dirty and the next flush wrote paid 5 (jobs %d)" % (ms_run, busy_f, int(Store.FLUSHES.get()) - f0))
    finally:
        ex6 = Store.WRITER
        Store.WRITER = None
        ex6.shutdown()
        ex6.awaitTermination(3, JClass("java.util.concurrent.TimeUnit").SECONDS)
    d8 = Store.dataK(US)
    Store.setMeta(d8, US, "_paid.Cobblestone", 6)
    f1 = int(Store.FLUSHES.get())
    Store.flushSoon()
    check(fileprops(cf).get("_paid.Cobblestone") == "6" and int(Store.FLUSHES.get()) == f1, "W6 no writer: flushSoon flushes inline (0.2.9's path)")
    setup6 = " ".join(MN["SkyyCollectionsPlugin"][[k for k in MN["SkyyCollectionsPlugin"] if k.startswith("setup(")][0]])
    shut6 = " ".join(MN["SkyyCollectionsPlugin"][[k for k in MN["SkyyCollectionsPlugin"] if k.startswith("shutdown(")][0]])
    run6 = " ".join(MN["CollSaver"][[k for k in MN["CollSaver"] if k.startswith("run(")][0]])
    check("CollThreads" in setup6 and "newSingleThreadExecutor" in setup6 and 0 <= shut6.find("awaitTermination") < shut6.find("CollStore.flushDirty")
          and "CollStore.flushSoon" in run6 and "CollStore.flushDirty" not in run6,
          "W6 bytecode: setup makes the writer; shutdown awaits it BEFORE the inline flushes; CollSaver.run only hands the flush over")
    check(kinds.get("CollBypass") in ("identical", "version constants"), "W6 the Buy click is 0.2.9's (its inline durable save before the confirmation): %s"
          % kinds.get("CollBypass"))
    print("W6. the 10 s flush runs on SkyyCollections-writer: CollSaver.run returned in %.1f ms during a held-file flush; one job at a time; "
          "no writer = inline; shutdown awaits the writer first" % ms_run)
    # ---------------- W7 (fixer 2): the paid markers on disk right after a payout; the save snapshot inside the file lock
    PAID7 = {"coins": 0, "xp": 0}

    @JImplements("java.util.function.Function")
    class Coins7(object):
        @JOverride
        def apply(self, a):
            PAID7["coins"] += 1
            return JClass("java.lang.Long")(1)

    @JImplements("java.util.function.Function")
    class Xp7(object):
        @JOverride
        def apply(self, a):
            PAID7["xp"] += 1
            return JClass("java.lang.Boolean").TRUE
    Rew7 = jc("CollRewards")
    BR.put("coins:fn:add", Coins7())
    BR.put("skill:fn:addxp", Xp7())
    reset_store()
    write_counts(US, {"Rock_Stone_Cobble": thr(COB, 3)}, {"_paid.Cobblestone": 2, "_paidxp.Cobblestone": 2})
    Store.WRITER = Exs6.newSingleThreadExecutor(Thr6())
    try:
        d9 = Store.dataK(US)
        k0 = int(Store.KEYSAVES.get())
        r9 = Rew7.settle(d9, R, COB, UID, US)
        Store.WRITER.submit(TName6()).get()      # the writer has run everything queued before this
        fp9 = fileprops(cf)
        ks9 = int(Store.KEYSAVES.get()) - k0
        check((int(r9[0]) > 0 or int(r9[1]) > 0) and fp9.get("_paid.Cobblestone") == "3" and fp9.get("_paidxp.Cobblestone") == "3"
              and ks9 == 1 and not Store.DIRTY.containsKey(US) and not Store.KEYQ.containsKey(US),
              "W7 a payout (coins %d, xp %d) saves that key on the writer at once: the file has paid 3 / paidxp 3 with NO flush (%d key job)"
              % (int(r9[0]), int(r9[1]), ks9))
        # the crash right after: a fresh load (= the next server start) pays nothing again
        c9, x9 = PAID7["coins"], PAID7["xp"]
        reset_store()
        d10 = Store.dataK(US)
        r10 = Rew7.settle(d10, R, COB, UID, US)
        check(int(r10[0]) == 0 and int(r10[1]) == 0 and PAID7["coins"] == c9 and PAID7["xp"] == x9,
              "W7 crash right after the payout (no 10 s flush ran): a fresh load pays the tier NOT twice")
        # a settle that pays nothing queues nothing
        Store.WRITER.submit(TName6()).get()
        check(int(Store.KEYSAVES.get()) - k0 == 1, "W7 a settle that pays nothing queues no save")
    finally:
        ex7 = Store.WRITER
        Store.WRITER = None
        ex7.shutdown()
        ex7.awaitTermination(3, JClass("java.util.concurrent.TimeUnit").SECONDS)
    # no writer: the payout saves inline
    reset_store()
    write_counts(US, {"Rock_Stone_Cobble": thr(COB, 4)}, {"_paid.Cobblestone": 3, "_paidxp.Cobblestone": 3})
    d11 = Store.dataK(US)
    r11 = Rew7.settle(d11, R, COB, UID, US)
    fp11 = fileprops(cf)
    check((int(r11[0]) > 0 or int(r11[1]) > 0) and fp11.get("_paid.Cobblestone") == "4" and not Store.DIRTY.containsKey(US),
          "W7 no writer: the payout saves the key inline (paid 4 on disk)")
    BR.remove("coins:fn:add")
    BR.remove("skill:fn:addxp")
    # the snapshot inside the file lock: hold the file's lock, start a save (it must wait), change the data, release -> the NEWER data is written
    reset_store()
    write_counts(US, {"Rock_Stone_Cobble": 5}, {"_paid.Cobblestone": 1})
    d12 = Store.dataK(US)
    lk12 = IO_n.lockOf(Paths.get(cf))
    res12 = {}

    def save12():
        res12["ok"] = bool(Store.save(US))
    with jpype.synchronized(lk12):
        th12 = threading.Thread(target=save12)
        th12.start()
        _t6.sleep(0.3)
        waited12 = th12.is_alive() and "ok" not in res12
        Store.setMeta(d12, US, "_bought.Cobblestone", 2)   # the world thread's Buy change while the writer's save waits
    th12.join(5)
    fp12 = fileprops(cf)
    check(waited12 and res12.get("ok") is True and fp12.get("_bought.Cobblestone") == "2" and fp12.get("_paid.Cobblestone") == "1",
          "W7 a save waiting on the file lock snapshots AFTER it gets the lock: the newer _bought 2 is written (not the older snapshot)")
    sv12 = " ".join(MN["CollStore"][[k for k in MN["CollStore"] if k.startswith("save(")][0]])
    st12 = " ".join(MN["CollRewards"][[k for k in MN["CollRewards"] if k.startswith("settle(")][0]])
    check("monitorenter" in sv12 and "CollIO.lockOf" in sv12 and "CollStore.save0" in sv12 and "CollStore.saveKeySoon" in st12,
          "W7 bytecode: save = synchronized (lockOf) { save0 }; settle calls saveKeySoon")
    print("W7. a payout's paid markers reach disk at once on the writer (crash right after = not paid twice); no writer = inline; the save "
          "snapshot is taken inside the file lock")
    reset_store()
    print("W. CollIO: fsync + atomic move, round-trip, stale tmp, held target retry + throw (%.0f ms) while another profile's IO took %.1f ms "
          "(0.2.9: %.0f ms), 2 x 200 same-file writes whole, dirty kept on a failed save" % (rn["slow_ms"], rn["other_ms"], ro["other_ms"]))

    # ---------------- P. publish only on change
    cdir_ = os.path.join(SCRATCH, "cls")
    CP_ = JClass("javassist.ClassPool")(True)
    cm_ = CP_.makeClass("skyycolltest.CountMap", CP_.get("java.util.concurrent.ConcurrentHashMap"))
    cm_.addField(JClass("javassist.CtField").make("public static final java.util.concurrent.ConcurrentHashMap PUTS = new java.util.concurrent.ConcurrentHashMap();", cm_))
    cm_.addMethod(JClass("javassist.CtNewMethod").make(
        "public Object put(Object k, Object v) { Integer c = (Integer) PUTS.get(k); PUTS.put(k, Integer.valueOf(c == null ? 1 : c.intValue() + 1)); return super.put(k, v); }", cm_))
    cm_.addConstructor(JClass("javassist.CtNewConstructor").make("public CountMap() { super(); }", cm_))
    cm_.writeFile(cdir_)
    urls_ = JArray(URL)(1)
    urls_[0] = File(cdir_).toURI().toURL()
    CMc = URLCL(urls_, sysl).loadClass("skyycolltest.CountMap")
    PUTS = CMc.getDeclaredField("PUTS").get(None)
    CM = CMc.getDeclaredConstructor().newInstance()
    System.getProperties().put("skyy.bridge", CM)
    rk_, sk_, ck_, ek_ = "coll:recipes:" + US, "coll:" + US, "coll:score:" + US, "coll:epoch:" + US

    def puts(k_):
        v_ = PUTS.get(k_)
        return 0 if v_ is None else int(v_)
    try:
        reset_store()
        write_counts(US, {"Rock_Stone_Cobble": thr(COB, 1)})
        Unl.PUBLISHED.clear()
        Unl.SIG.clear()
        PUTS.clear()
        Unl.publish(UID)
        p1 = (puts(rk_), puts(sk_), puts(ck_), puts(ek_))
        v1 = str(CM.get(rk_))
        Unl.publish(UID)
        Unl.publish(UID)
        p2 = (puts(rk_), puts(sk_), puts(ck_), puts(ek_))
        check(p1 == (1, 1, 1, 1) and p2 == p1, "P1 publish twice more on the same data: coll:recipes / coll: / coll:score / epoch put once each "
              "(%s -> %s)" % (p1, p2))
        # a collect that changes no tier (more cobblestone, still below tier II): recipes stay -> no recipes put, no epoch bump
        reset_store()
        write_counts(US, {"Rock_Stone_Cobble": thr(COB, 1) + 1})
        Unl.publish(UID)
        p3 = (puts(rk_), puts(ek_))
        check(p3 == (1, 1) and str(CM.get(rk_)) == v1, "P2 a collect below the next tier: coll:recipes not re-put, epoch not bumped (%s)" % (p3,))
        # cross tier 3 of Cobblestone (the Mining bag) -> recipes change: put again + epoch +1
        reset_store()
        write_counts(US, {"Rock_Stone_Cobble": thr(COB, 3)})
        Unl.publish(UID)
        p4 = (puts(rk_), puts(ek_))
        check(p4 == (2, 2) and str(CM.get(rk_)) != v1 and MINING[0] in str(CM.get(rk_)), "P3 crossing tier III: coll:recipes put again, "
              "the epoch bumped once (%s)" % (p4,))
        new_vals = (str(CM.get(rk_)), str(CM.get(sk_)), str(CM.get(ck_)))
        # the control: 0.2.9's publish on the same file gives the same values
        Unl_o2, Store_o2, Reg_o2 = jc("CollUnlocks", "old"), jc("CollStore", "old"), jc("CollReg", "old")
        Reg_o2.BASE = Paths.get(wbase)
        Store_o2.DIR = Paths.get(wbase).resolve("counts")
        Reg_o2.loadAll()
        recipes_from_rewards(Reg_o2)
        Store_o2.DATA.clear()
        Unl_o2.PUBLISHED.clear()
        Unl_o2.SIG.clear()
        CM.clear()
        PUTS.clear()
        Unl_o2.publish(UID)
        old_vals = (str(CM.get(rk_)), str(CM.get(sk_)), str(CM.get(ck_)))
        check(new_vals == old_vals, "P4 the published values == 0.2.9's on the same file: %s / %s" % (new_vals[1], old_vals[1]))
        Unl_o2.publish(UID)
        check(puts(rk_) == 2, "P4 control: 0.2.9 re-puts coll:recipes on every publish (%d puts for 2 calls)" % puts(rk_))
    finally:
        System.getProperties().put("skyy.bridge", BR)
        reset_store()
    print("P. publish only on change: same data -> one put per key; below-tier collect -> none; a new tier -> one put + one epoch bump; "
          "values = 0.2.9's")

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
        # 0.2.10: every live profile publishes the same coll:recipes / coll: / coll:score on 0.2.9 and 0.2.10
        npub = 0
        for k_ in keys:
            m_ = re.match(r"^([0-9a-f-]{36})(-p\d+)?$", k_)
            if not m_:
                continue
            u_ = UUID.fromString(m_.group(1))
            vals = []
            for lo_ in (lo_n2, lo_o1):
                BR.clear()
                BR.put("profile:fn:key", KF)
                KF.key = k_
                U_ = JClass(PKG + "CollUnlocks", loader=lo_)
                U_.PUBLISHED.clear()
                U_.SIG.clear()
                U_.publish(u_)
                vals.append(tuple(str(BR.get(x_ + str(u_))) for x_ in ("coll:recipes:", "coll:", "coll:score:")))
            check(vals[0] == vals[1] and vals[0][0] != "None", "S5 %s: 0.2.10 publishes what 0.2.9 publishes: %s / %s" % (k_, vals[0][1], vals[1][1]))
            npub += 1
        BR.clear()
        print("S5. %d live profiles publish the same values on 0.2.9 and 0.2.10" % npub)
        check(snap(LIVE) == live_before, "S4 the live folder is untouched")
        print("S. live copy: 2 starts of 0.2.9 (and 0.2.8) write nothing; %d profiles: unlocks == 0.2.8 (absent) / minus bags (present); catTotal == model on %d"
              % (len(keys), nprof))
    else:
        print("note: no live Skyy_SkyyCollections folder - S skipped")


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (python tools/collections_0_2_10_patch.py, python SkyyCollections/build_skyycollections_0.2.10.py)")
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
