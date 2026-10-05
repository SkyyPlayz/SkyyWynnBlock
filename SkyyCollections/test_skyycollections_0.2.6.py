"""Bare-JVM harness for SkyyCollections 0.2.6 (lean) - leaderboards skip deleted and archived profiles (tools/coll_0_2_6_patch.py;
SkyyProfiles 0.1.5 profile:fn:state, tools/PROFILES-CONTRACT.md). Extends SkyyCollections/test_skyycollections_0.2.5.py (its class-file
comparison and JVM set-up, copied forward); the 0.2.5 harness itself still covers everything 0.2.6 leaves byte-identical.

    python SkyyCollections/test_skyycollections_0.2.6.py [--jar <SkyyCollections-0.2.6.jar>] [--old <SkyyCollections-0.2.5.jar>]
                                                         [--dir <scratch>] [--keep]

One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath), every jar in its own
class loader.
  A  every class of both jars loads, verifies and initialises
  B  class bytes 0.2.5 -> 0.2.6: the same classes; every class byte-identical or identical once its "0.2.5" constants read "0.2.6",
     except CollTop: only all() changed + the new stateFn() / gone(); SkyyCollectionsPlugin only version-only; manifest: only
     Version / Name
  C  the page id in the jar's ready line == COLL_PAGE_CHECKED of the generated script (the page is 0.2.5's)
  L  CollTop.all(board) for a collection board and the score board (-1), on 0.2.5 and 0.2.6 side by side, on scratch counts files +
     the in-memory overlay: (1) SkyyProfiles absent -> 0.2.6 == 0.2.5 row for row; (2) live (active / inactive / null legacy uuid key)
     shown, deleted (pending = inside the undo window) and archived left out, the order otherwise 0.2.5's, an in-memory pending key
     left out too; (3) restored (pending -> active) shows again once the 30 s cache is cleared, cached lists unchanged before;
     (4) the bridge Function throwing for every key / for one key, (5) not a Function, (6) odd answers ("PENDING", "deleted", a
     Boolean, "") -> shown (0.2.5's list); (7) cost: one profile:fn:state call per listed key (value > 0) per board build, none on a
     cache hit, never for a value-0 key; (8) nothing saved changes: every counts file byte-identical, the in-memory data unchanged
Nothing outside the scratch folder is written (default tools/dev/scratch/coll026/harness, deleted at the end unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.6", "0.2.5"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "coll026", "harness")))
assert SCRATCH.startswith(SCRATCH_ROOT + os.sep), "--dir must be inside tools/dev/scratch/"
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def cp_utf8(b):
    """[(start, end, bytes)] of every CONSTANT_Utf8 entry of a class file"""
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


def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
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

    # ---------------- B
    old, new = CB["old"], CB["new"]
    check(set(old) == set(new), "B. the same classes: %s" % sorted(set(old) ^ set(new)))
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

    DECLARED = {"CollTop": ["all"]}
    ADDED = {"CollTop": ["gone(Ljava/util/function/Function;Ljava/lang/String;)Z", "stateFn()Ljava/util/function/Function;"]}
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
        fo = sorted((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
        fn = sorted((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields())
        check(fo == fn, "B. %s: fields changed: %s" % (short, sorted(set(fo) ^ set(fn))))
        mo, mn = methods(po), methods(pn)
        check(not (set(mo) - set(mn)) and sorted(set(mn) - set(mo)) == ADDED.get(short, []),
              "B. %s: methods added / gone: %s" % (short, sorted(set(mo) ^ set(mn))))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        vers = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and vonly(mo[k], mn[k]))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        kinds[short] = "methods %s + version only %s" % (changed, vers)
    check("CollTop" in kinds and kinds["CollTop"].startswith("methods ['all']"), "B. CollTop changed: %s" % kinds.get("CollTop"))
    mo_, mn_ = manifest(OLD), manifest(JAR)
    check(mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyyCollections"
          and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name")) == dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name")),
          "B. manifest: only Version / Name changed")
    ident = sorted(k for k, v in kinds.items() if v == "identical")
    print("B. %d classes byte-identical; version constants only: %s; method-level: %s" % (
        len(ident), sorted(k for k, v in kinds.items() if v == "version constants"),
        dict((k, v) for k, v in kinds.items() if v.startswith("methods"))))

    # ---------------- C. page id
    text = open(SCRIPT, encoding="utf8").read()
    chk = None
    for nd in ast.parse(text).body:
        if isinstance(nd, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "COLL_PAGE_CHECKED" for t in nd.targets):
            chk = ast.literal_eval(nd.value)
    plug = new[PKG + "SkyyCollectionsPlugin"].decode("latin1")
    mm = re.search(r"0\.2\.6 ready \(skyyui [^,]*, page ([0-9a-f]{12})\)", plug)
    check(chk == "be0dca34bcb2" and mm is not None and mm.group(1) == chk, "C. page id in the ready line %s == checked %s" % (mm and mm.group(1), chk))

    # ---------------- L. leaderboards
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    System = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    U = ["00000000-0000-0000-0000-0000000000%02x" % i for i in range(1, 12)]
    # key -> (name, count multiplier, state)
    PROF = [
        (U[0], "Alpha", 9, None),                 # legacy uuid key, no SkyyProfiles entry (null)
        (U[1], "Bravo", 8, "active"),
        (U[1] + "-p2", "Bravo", 7, "inactive"),
        (U[2], "Charlie", 6, "pending"),          # deleted, inside the 6 h undo window
        (U[3] + "-p3", "Delta", 5, "archived"),
        (U[4], "Echo", 4, "pending"),             # restored later
        (U[5], "Foxtrot", 3, "active"),
        (U[6], "Golf", 0, "pending"),             # value 0: never listed, never asked
        (U[7] + "-p2", "Hotel", 10, "archived"),  # top value, archived
    ]
    MEM = [(U[8], "India", 11, "pending"), (U[9], "Juliet", 2, "active")]   # in-memory overlay (CollStore.DATA)
    STATE = dict((k, st) for k, _n, _c, st in PROF + MEM)
    CALLS = []

    @JImplements("java.util.function.Function")
    class StateFn:
        def __init__(self, mode="ok", bad=None, answers=None):
            self.mode, self.bad, self.answers = mode, bad, answers

        @JOverride
        def apply(self, a):
            key = str(a)
            CALLS.append(key)
            if self.mode == "throw" or key == self.bad:
                raise JClass("java.lang.IllegalStateException")("profiles broken")
            if self.answers is not None:
                return self.answers.get(key)
            return STATE.get(key)

    W = {}
    for k in ("old", "new"):
        Reg, Store = jc(k, "CollReg"), jc(k, "CollStore")
        base = os.path.join(SCRATCH, "world", k, "Skyy_SkyyCollections")
        os.makedirs(base)
        Reg.BASE = Paths.get(base)
        Store.DIR = Paths.get(base).resolve("counts")
        msg = str(Reg.loadAll())
        R = Reg.D
        check(R is not None and R.n > 2, "L. %s registry loaded: %s" % (k, msg))
        c0 = [c for c in range(R.n) if not R.hidden[c]][0]
        cd = os.path.join(base, "counts")
        os.makedirs(cd, exist_ok=True)
        item = str(R.items[c0][0])
        for key, nm, mul, _st in PROF:
            lines = ["_schema=2", "_name=" + nm]
            if mul:
                lines.append("%s=%d" % (item, 100 * mul + 7))
            open(os.path.join(cd, key + ".properties"), "w").write("\n".join(lines) + "\n")
        Store.DATA.clear()
        for key, nm, mul, _st in MEM:
            d = jc(k, "CollData")()
            d.name = nm
            d.items.put(item, Long.valueOf(100 * mul + 7))
            Store.DATA.put(key, d)
        W[k] = (Reg, Store, R, c0, cd)

    def files(k):
        cd = W[k][4]
        return dict((f, open(os.path.join(cd, f), "rb").read()) for f in sorted(os.listdir(cd)))

    def mem(k):
        D = W[k][1].DATA
        return sorted((str(e.getKey()), str(e.getValue().name), str(e.getValue().items)) for e in D.entrySet())

    BEFORE = {"old": (files("old"), mem("old")), "new": (files("new"), mem("new"))}

    def rows(k, board, fn=None, clear=True):
        Top = jc(k, "CollTop")
        if clear:
            Top.CACHE.clear()
        BR.clear()
        if fn is not None:
            BR.put("profile:fn:state", fn)
        return [(str(r[0]), int(r[1]), str(r[2])) for r in Top.all(board)]

    LISTED = [key for key, _n, mul, _s in PROF + MEM if mul]
    HIDE = set(k for k, st in STATE.items() if st in ("pending", "archived"))
    for bname, board in (("collection", None), ("score", -1)):
        b = W["new"][3] if board is None else board
        # (1) SkyyProfiles absent
        o, n = rows("old", b), rows("new", b)
        check(n == o and len(n) == len(LISTED), "L1 %s: absent -> 0.2.6 == 0.2.5 (%d rows): %s / %s" % (bname, len(n), n, o))
        check(set(r[2] for r in n) == set(LISTED), "L1 %s: every profile with a value listed" % bname)
        # (2) live / deleted / archived
        del CALLS[:]
        n2 = rows("new", b, StateFn())
        o2 = rows("old", b, StateFn())
        want = [r for r in o if r[2] not in HIDE]
        check(n2 == want, "L2 %s: pending / archived left out, order kept: %s" % (bname, n2))
        check(o2 == o, "L2 %s: 0.2.5 ignores profile:fn:state (shows everyone)" % bname)
        check(sorted(r[2] for r in n2) == sorted([U[0], U[1], U[1] + "-p2", U[5], U[9]]), "L2 %s: live keys shown: %s" % (bname, [r[2] for r in n2]))
        check(U[8] not in [r[2] for r in n2], "L2 %s: an in-memory pending profile left out" % bname)
        check(any(r[0] == "Bravo (profile 2)" for r in n2), "L2 %s: labels unchanged (Bravo (profile 2))" % bname)
        # (7) cost: exactly one call per listed key on the 0.2.6 build (0.2.5 asks nothing), none for value-0 keys, none on a cache hit
        new_calls = CALLS[:len(LISTED)]
        check(sorted(new_calls) == sorted(LISTED) and len(CALLS) == len(LISTED), "L7 %s: one call per listed key per build: %s" % (bname, CALLS))
        check(U[6] not in CALLS, "L7 %s: a value-0 key is never asked" % bname)
        del CALLS[:]
        n2b = rows("new", b, StateFn(), clear=False)
        check(n2b == n2 and CALLS == [], "L7 %s: a cached list asks nothing (%d calls)" % (bname, len(CALLS)))
        # (3) restore: Echo pending -> active
        STATE[U[4]] = "active"
        n3c = rows("new", b, StateFn(), clear=False)
        check(n3c == n2, "L3 %s: inside the 30 s cache the list is unchanged" % bname)
        n3 = rows("new", b, StateFn())
        check(U[4] in [r[2] for r in n3] and [r for r in o if r[2] not in HIDE - {U[4]}] == n3, "L3 %s: restored profile shows again: %s" % (bname, n3))
        STATE[U[4]] = "pending"
        # undo window over -> archived: still hidden
        STATE[U[2]] = "archived"
        check(rows("new", b, StateFn()) == want, "L3 %s: pending -> archived stays hidden" % bname)
        STATE[U[2]] = "pending"
        # (4) throwing
        check(rows("new", b, StateFn("throw")) == o, "L4 %s: profile:fn:state throwing for every key -> everyone shown" % bname)
        n4 = rows("new", b, StateFn(bad=U[2]))
        check(n4 == [r for r in o if r[2] not in HIDE - {U[2]}], "L4 %s: throwing for one (pending) key -> that key shown, the rest filtered" % bname)
        # (5) not a Function
        check(rows("new", b, JClass("java.lang.String")("pending")) == o, "L5 %s: profile:fn:state not a Function -> everyone shown" % bname)
        # (6) odd answers
        for ans in ("PENDING", "deleted", "", "Archived "):
            check(rows("new", b, StateFn(answers=dict((k, ans) for k in STATE))) == o, "L6 %s: answer %r -> shown" % (bname, ans))
        check(rows("new", b, StateFn(answers=dict((k, Boolean.TRUE) for k in STATE))) == o, "L6 %s: a Boolean answer -> shown" % bname)
        check(rows("new", b, StateFn(answers={})) == o, "L6 %s: null for every key -> shown" % bname)
    # (8) nothing saved changes
    for k in ("old", "new"):
        check(files(k) == BEFORE[k][0], "L8 %s: every counts file byte-identical" % k)
        check(mem(k) == BEFORE[k][1], "L8 %s: in-memory data unchanged" % k)
    BR.clear()
    print("L. leaderboards: %d profiles (%d listed, %d deleted / archived), collection + score boards" % (len(PROF + MEM), len(LISTED), len(HIDE)))


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first (python tools/coll_0_2_6_patch.py, python SkyyCollections/build_skyycollections_0.2.6.py;"
                  " the 0.2.5 jar: python SkyyCollections/build_skyycollections_0.2.5.py)")
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
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
