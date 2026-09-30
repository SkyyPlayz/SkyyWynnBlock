"""Bare-JVM page harness for SkyyVault 0.1.4 - the look-only restyle of VaultPage and the move of the VBuyDlg confirm window onto the
shared UI kit tools/skyyui.py. Committed next to the build so the build docstring's CHECKED claims can be re-run instead of trusted;
copy it to the next version and keep it passing (the SkyyBank 0.1.4 harness pattern).

    python SkyyVault/test_skyyvault_0.1.4.py [--jar <SkyyVault-0.1.4.jar>] [--old <SkyyVault-0.1.3.jar>] [--dir <scratch>] [--keep]

Build first (python SkyyVault/build_skyyvault_0.1.4.py). One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar +
tools/javassist.jar on the classpath; EACH SkyyVault jar in its own class loader, so 0.1.3 - the live SET pin - and 0.1.4 run side by
side in one process) checks:
  A  every class of both jars loads, verifies and initialises
  B  the restyle contract in bytes: every class but VaultPage / VBuyDlg / SkyyVaultPlugin is byte-identical to 0.1.3 once the
     embedded version string "0.1.4" reads "0.1.3" again (VStore.toDoc's file "version", the config kit's CfgRows / CfgFn - and
     nothing else may differ in them); SkyyVaultPlugin = 0.1.3's bytes once its one ready-log constant is swapped back (that
     constant names the kit and the page id); VaultPage and VBuyDlg (javassist, constant-pool indices resolved): the same fields
     (VBuyDlg: 0.1.3's BTNP / BTNS style strings gone), every method but build / colorOf / textOf instruction-identical,
     VaultPage.style gone, nothing new
  C  differential VaultPage builds, 0.1.3 vs 0.1.4, in 17 vault states (a fresh vault, page mode showing / not showing the page,
     locked next / far pages, all bought, more pages than maxPages, 30-page windows at the start / middle / end, a free next page,
     a 12.5k price (a dot in the Buy label, inline as 0.1.3), arrowLayout inside, a one-page vault, pages holding items, the
     unreadable file, sel 0) x 5 result lines, with the engine's own UICommandBuilder / UIEventBuilder and a PlayerRef allocated
     without a constructor: identical b.set lines, identical event bindings (type, id, EventData, lock, order), identical inline
     TextButton labels per id, this.sel / this.offer identical after the build, every 0.1.3 element id created; every 0.1.4
     appendInline equals a markup the kit makes NOW from the build script's vault_page() (J() slots filled), every markup passes
     SUI.check_markup (the runtime button labels: equal to 0.1.3's instead of the text rule) and every page SUI.check_page, only
     kit colours, the result line coloured by its mark, the body filled exactly (SUI.used_height of the markup as sent), the page
     tabs centred in the well by the first tab's Anchor Left, no LayoutMode Left row with a Padding (the kit 1.4 button_row
     centring, probe base4 - not needed any more). Review fixes: WHICH look each state gets is asserted per element (tab n =
     on screen when n == sel, owned when n <= unlocked, else locked; Open live iff sel <= unlocked; Buy live iff the next page is
     <= maxPages, and this.offer = that page; Prev live iff sel > 1; Next live iff sel < max) - the markup must match exactly
     that one kit look of its family; the b.set lines come in 0.1.3's ORDER (not only the same set) and every command on #Id
     comes after the append that creates #Id
  D  the confirm window, 0.1.3 vs 0.1.4, in 6 states (Buy rich / poor / purse unreadable / no SkyyCoins, Unlock free, no vault
     file): identical b.set lines and bindings, and the SAME LOOK: both markups parsed into element trees and compared property
     by property (only the kit's extra button states - Disabled, ShrinkTextToFit - and the Buy / Cancel pair centred by Buy's
     Anchor Left 154 in a LayoutMode Left row instead of LayoutMode Center may differ); Buy / Unlock picked by the price; the
     b.set order and set-after-append as in C
  E  clicks through handleDataEvent on both jars (VaultPage: prev / next / num / open / buy (a cheap page bought at once, then the
     1.5 s guard, a dear page that asks for the window) / close / junk in 4 states; VBuyDlg: Buy / Cancel / junk / double click):
     identical result line, selection, offer, purse, owned pages, vault file (its "version" / "savedAt" aside) and vault.log BUY
     lines after every click, and the page rebuilt after it passes the C checks
  F  text fit with the client's font tables (SUI.text_width; skipped when the client is not installed): every button label seen
     fits its button minus the padding, the one-line texts fit their boxes, the two-line boxes hold every result seen
  G  the page id: VAULT_PAGE_ID of the kit's pages NOW == VAULT_PAGE_CHECKED in the build script == the id in the jar's ready line
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the pages, the textures / sounds, the real
PageManager, rebuild() / close() on a live page, the page opened with the vault window (openCustomPageWithWindows).
Nothing is deployed and nothing outside the scratch folder is written. --dir (default tools/dev/scratch/test-vault) must lie under
tools/dev/scratch (anything else is refused); the harness works in a FRESH sub-folder it makes inside it (run-*; TEMP / TMP and
java.io.tmpdir point into it) and deletes only that sub-folder at the end (unless --keep), plus --dir itself when the harness made it
and it is empty then - an existing folder passed as --dir is never deleted. Exit code 1 on any failure, 2 on a refused --dir.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, hashlib, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.4", "0.1.3"
PKG = "com.skyy.vault."
SCRIPT = os.path.join(HERE, "build_skyyvault_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.join(TOOLS, "dev", "scratch")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "test-vault")))
WORK = None                        # the fresh run-* folder inside SCRATCH (main); the only thing the harness deletes
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyVault-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}


def scratch_ok(path):
    """review fix: --dir must be a folder UNDER tools/dev/scratch (the brief's only scratch place)"""
    root = os.path.normcase(os.path.abspath(SCRATCH_ROOT)).rstrip("\\/") + os.sep
    return os.path.normcase(os.path.abspath(path)).startswith(root)


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def tally(key, n=1):
    COUNT[key] = COUNT.get(key, 0) + n


# ------------------------------------------------------------------------------------------------ the kit's pages, NOW (no JVM)
def kit_pages():
    """Run the build script's page code (its VAULT_* / VDLG_* constants, vault_* functions, the build sources and the page id) on
    the CURRENT kit, without the rest of the build: returns (SUI, namespace)."""
    import skyyui as SUI
    SUI.verify(quiet=True)
    tree = ast.parse(open(SCRIPT, encoding="utf8").read())
    body = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name.startswith("vault_"):
            body.append(n)
        elif isinstance(n, ast.Assign) and all(isinstance(t, (ast.Name, ast.Tuple)) for t in n.targets):
            names = [x.id for t in n.targets for x in (t.elts if isinstance(t, ast.Tuple) else [t]) if isinstance(x, ast.Name)]
            if names and all(x.startswith(("VAULT_", "VDLG_")) for x in names):
                body.append(n)
    ns = {"SUI": SUI, "re": re, "hashlib": hashlib, "KIT_ID": SUI.kit_id(), "VERSION": VERSION}
    exec(compile(ast.Module(body=body, type_ignores=[]), SCRIPT, "exec"), ns)
    return SUI, ns


# ------------------------------------------------------------------------------------------------ class-file helpers (no JVM)
def cp_utf8(b):
    """[(start, end, bytes)] of every CONSTANT_Utf8 entry of a class file (start = its tag byte)"""
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


# ------------------------------------------------------------------------------------------------ inline markup -> element tree
def _scan_to(s, i, stop_chars, track_paren=True):
    """index of the first char in stop_chars at bracket depth 0 outside quotes, from i"""
    depth, q, n = 0, False, len(s)
    while i < n:
        c = s[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                q = False
        elif c == '"':
            q = True
        elif c in "({":
            depth += 1
        elif c in ")}":
            if depth == 0 and c in stop_chars:
                return i
            depth -= 1
        elif depth == 0 and c in stop_chars:
            return i
        i += 1
    return n


def _split_top(s, sep=","):
    out, i, start = [], 0, 0
    while True:
        j = _scan_to(s, i, sep)
        out.append(s[start:j])
        if j >= len(s):
            break
        i = start = j + 1
    return [x for x in out if x.strip()]


def pval(v):
    """a property value: "(a: b, c: (d: e))" / "Name(...)" -> dict (key "@type" = the constructor name), else the stripped text"""
    v = v.strip()
    m = re.match(r"\A([A-Za-z]*)\((.*)\)\Z", v, re.S)
    if m and _scan_to(v, len(m.group(1)) + 1, ")") == len(v) - 1:
        d = {}
        if m.group(1):
            d["@type"] = m.group(1)
        for part in _split_top(m.group(2)):
            k, _s, x = part.partition(":")
            d[k.strip()] = pval(x)
        return d
    return v


ELEM_RE = re.compile(r"\s*([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9]+))?\s*\{")
PROP_RE = re.compile(r"\s*([A-Za-z][A-Za-z0-9]*)\s*:")


def parse_elems(s):
    """[{type, id, props, kids}] of a markup string (one or more elements)"""
    out, i, n = [], 0, len(s)
    while i < n and s[i:].strip():
        m = ELEM_RE.match(s, i)
        if not m:
            raise ValueError("no element at %d: %r" % (i, s[i:i + 60]))
        j = m.end()
        k = _scan_to(s, j, "}")
        props, kids = parse_body(s[j:k])
        out.append({"type": m.group(1), "id": m.group(2), "props": props, "kids": kids})
        i = k + 1
    return out


def parse_body(inner):
    props, kids, i, n = {}, [], 0, len(inner)
    while i < n and inner[i:].strip():
        if ELEM_RE.match(inner, i):
            m = ELEM_RE.match(inner, i)
            k = _scan_to(inner, m.end(), "}")
            kids.extend(parse_elems(inner[i:k + 1]))
            i = k + 1
            continue
        m = PROP_RE.match(inner, i)
        if not m:
            raise ValueError("no property at %d: %r" % (i, inner[i:i + 60]))
        k = _scan_to(inner, m.end(), ";")
        props[m.group(1)] = pval(inner[m.end():k])
        i = k + 1
    return props, kids


def page_tree(appends):
    """{path: (type, props)} of a whole page from its (parent selector or None, markup) appends; path = #id, or the parent's path +
    /Type<n> for an anonymous element (n = its index among the parent's anonymous children of that type)"""
    flat, anon = {}, {}
    idpath = {}

    def put(parent_path, el):
        if el["id"]:
            path = "#" + el["id"]
        else:
            key = (parent_path, el["type"])
            anon[key] = anon.get(key, 0) + 1
            path = "%s/%s%d" % (parent_path, el["type"], anon[key])
        flat[path] = (el["type"], el["props"], parent_path)
        if el["id"]:
            idpath[el["id"]] = path
        for kid in el["kids"]:
            put(path, kid)
    for parent, text in appends:
        pp = "" if parent is None else idpath.get(parent.lstrip("#"), parent)
        for el in parse_elems(text):
            put(pp, el)
    return flat


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
    import skyybuild as B
    tmp = os.path.join(WORK, "tmp")
    os.makedirs(tmp, exist_ok=True)
    SUI, K = kit_pages()
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

    # ---------------- A. load + verify + init, both jars
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                tally("A classes " + k)
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: 0.1.3 %d, 0.1.4 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. the restyle contract in bytes
    old, new = CB["old"], CB["new"]
    check(sorted(old) == sorted(new), "B. the same class names: %s" % sorted(set(old) ^ set(new)))
    page_c, dlg_c, plug_c = PKG + "VaultPage", PKG + "VBuyDlg", PKG + "SkyyVaultPlugin"
    ver_only = []
    for n in sorted(old):
        if n in (page_c, dlg_c, plug_c) or n not in new:
            continue
        if old[n] == new[n]:
            tally("B identical")
            OKS[0] += 1
            continue
        swapped = new[n].replace(b"0.1.4", b"0.1.3")
        if check(swapped == old[n], "B. %s differs from 0.1.3 by more than its embedded version string" % n):
            ver_only.append(n.rsplit(".", 1)[1])
    check("VStore" in ver_only and set(ver_only) <= {"VStore", "CfgFn", "CfgRows", "CfgPub"},
          "B. only VStore (the file's version field) and the config kit carry the version string: %s" % ver_only)
    ready_old = [e for e in cp_utf8(old[plug_c]) if b"] 0.1.3 ready" in e[2]]
    ready_new = [e for e in cp_utf8(new[plug_c]) if b"] 0.1.4 ready" in e[2]]
    LOG_NEW = ""
    if check(len(ready_old) == 1 and len(ready_new) == 1, "B. one ready-log constant in each SkyyVaultPlugin"):
        s0, e0, t0 = ready_old[0]
        s1, e1, t1 = ready_new[0]
        swapped = new[plug_c][:s1] + old[plug_c][s0:e0] + new[plug_c][e1:]
        check(swapped == old[plug_c], "B. SkyyVaultPlugin = 0.1.3's bytes once the ready-log constant is swapped back")
        LOG_NEW = t1.decode("utf8")
        check(t0.decode("utf8") == "[SkyyVault] 0.1.3 ready - /vault (shared by all profiles), /vaultadmin; ",
              "B. 0.1.3 ready constant: %r" % t0)
        check(re.fullmatch(r"\[SkyyVault\] 0\.1\.4 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page [0-9a-f]{12}\) - /vault \(shared by all "
                           r"profiles\), /vaultadmin; ", LOG_NEW) is not None, "B. the 0.1.4 ready constant names the kit and the page "
                                                                               "id: %r" % LOG_NEW)
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    BRANCH = re.compile(r"\A(if\w*|goto|goto_w|jsr|jsr_w) (\d+)\Z")

    def code_of(m):
        """the method's instructions with constant-pool indices resolved to what they name, ldc_w read as ldc and every branch /
        exception-table target as an INSTRUCTION index: a class whose constant pool shrank (0.1.4 dropped VaultPage.style /
        VBuyDlg.BTNP-BTNS, so some constants moved below index 256: ldc_w -> ldc, 1 byte shorter) compares equal when the
        instructions are the same (switches are compared as printed)"""
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, raw = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            raw.append((pos, re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp)))))
        idx = dict((p, i) for i, (p, _t) in enumerate(raw))
        idx[ca.getCodeLength()] = len(raw)
        out = []
        for _p, t in raw:
            t = re.sub(r"\Aldc_w ", "ldc ", t)
            m2 = BRANCH.match(t)
            if m2:
                t = "%s @%s" % (m2.group(1).replace("_w", ""), idx.get(int(m2.group(2)), "?" + m2.group(2)))
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%s @%s @%s %s" % (idx.get(et.startPc(i)), idx.get(et.endPc(i)), idx.get(et.handlerPc(i)),
                                               cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        ci = c.getClassInitializer()
        if ci is not None:
            out["<clinit>"] = code_of(ci)
        return out

    def fields(c):
        return sorted((str(f.getName()), str(f.getSignature())) for f in c.getDeclaredFields())

    for cname, look, keep, gone_want, fgone in (
            (page_c, ("build", "colorOf", "textOf"), ("<init>", "safe", "jsonStr", "refreshWith", "refresh", "handleDataEvent",
                                                      "onDismiss"), ["style"], []),
            (dlg_c, ("build",), ("<init>", "live", "question", "note", "handleDataEvent", "onDismiss"), [],
             [("BTNP", "Ljava/lang/String;"), ("BTNS", "Ljava/lang/String;")])):
        short = cname.rsplit(".", 1)[1]
        co, cn = ct(old[cname]), ct(new[cname])
        fo, fn = fields(co), fields(cn)
        check([f for f in fo if f not in fn] == fgone and [f for f in fn if f not in fo] == [],
              "B. %s fields: gone %s (want %s), new %s" % (short, [f for f in fo if f not in fn], fgone, [f for f in fn if f not in fo]))
        check(str(co.getClassFile().getSuperclass()) == str(cn.getClassFile().getSuperclass()), "B. %s superclass unchanged" % short)
        mo, mn = methods(co), methods(cn)
        gone = sorted(k.split("(")[0] for k in mo if k not in mn)
        added = sorted(k.split("(")[0] for k in mn if k not in mo)
        check([g for g in gone if g != "<clinit>"] == gone_want, "B. %s: gone %s (want %s)" % (short, gone, gone_want))
        check(added == [], "B. %s: nothing new (%s)" % (short, added))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
        same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
        check(all(c in look for c in changed), "B. %s: only the look methods changed: %s" % (short, changed))
        for kp in keep:
            check(kp in same, "B. %s.%s is instruction-identical to 0.1.3" % (short, kp))
        COUNT["B %s" % short] = (len(same), changed, gone)
        # the signatures of the kept look methods (colorOf / textOf are called by the same names)
        for lm in look:
            so = sorted(k for k in mo if k.startswith(lm + "("))
            sn = sorted(k for k in mn if k.startswith(lm + "("))
            check(so == sn, "B. %s.%s keeps its signature: %s / %s" % (short, lm, so, sn))
    print("B. %d classes byte-identical, %s differ only by the version string, SkyyVaultPlugin = 0.1.3 but its ready constant; "
          "VaultPage %s; VBuyDlg %s" % (COUNT.get("B identical", 0), ver_only, COUNT.get("B VaultPage"), COUNT.get("B VBuyDlg")))

    # ---------------- common Java objects
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    System = JClass("java.lang.System")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    ISC = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def field(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    def stack(item, qty):
        """an ItemStack without the item asset store (the constructor needs it): itemId + quantity set by reflection"""
        s = U.allocateInstance(ISC.class_)
        field(ISC, "itemId").set(s, item)
        field(ISC, "quantity").setInt(s, qty)
        field(ISC, "maxDurability").setDouble(s, 0.0)
        return s

    # ---------------- the bridge (one map for both jars: System property skyy.bridge) and the fake SkyyCoins
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    PURSE = {}                            # uuid -> coins, None = the purse cannot be read

    @JImplements("java.util.function.Function")
    class CoinsGet:
        @JOverride
        def apply(self, u):
            v = PURSE.get(str(u), 0)
            return None if v is None else Long.valueOf(v)

    @JImplements("java.util.function.Function")
    class CoinsAdd:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if PURSE.get(u, 0) is None:
                return None
            PURSE[u] = PURSE.get(u, 0) + n
            return Long.valueOf(PURSE[u])

    @JImplements("java.util.function.Function")
    class CoinsTake:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            have = PURSE.get(u, 0)
            if have is None:
                return None
            if have < n:
                return Boolean.FALSE
            PURSE[u] = have - n
            return Boolean.TRUE

    COINS = (CoinsGet(), CoinsAdd(), CoinsTake())
    UID = UUID.fromString("00000000-0000-0000-0000-0000000000c1")
    US = str(UID)

    def pref(u):
        p = U.allocateInstance(PR.class_)
        field(PR, "uuid").set(p, u)
        return p

    # a vault state: dict(name, free, max, price, step, confirm, layout, unlocked (None = unreadable file), cap, items {page: n},
    # sess (None | ("page" or "chest", page shown)), sel, purse (None = unreadable, "none" = no SkyyCoins))
    def S(name, **kw):
        d = dict(name=name, free=2, max=10, price=50000, step=25000, confirm=50000, layout="row", arrows=True, unlocked=2, cap=36,
                 items={}, sess=None, sel=1, purse=1000000)
        d.update(kw)
        return d
    STATES = [
        S("fresh"), S("showing", sess=("page", 1)), S("notshowing", sess=("page", 2), sel=1, items={1: 5, 2: 36}),
        S("nextlocked", sel=3), S("farlocked", sel=6), S("allbought", unlocked=10, sel=10, items={10: 1}),
        S("overmax", unlocked=12, sel=12), S("window-start", max=30, unlocked=20, sel=2), S("window-mid", max=30, unlocked=20, sel=15),
        S("window-end", max=30, unlocked=30, sel=30, sess=("page", 30)), S("freenext", price=0, step=0),
        S("dotprice", price=12500, step=2500, confirm=100000), S("inside", layout="inside"), S("onepage", free=1, max=1, unlocked=1),
        S("items", unlocked=4, sel=4, items={1: 36, 3: 12, 4: 7}, sess=("page", 4)), S("unreadable", unlocked=None), S("sel0", sel=0),
    ]
    MARKS = ["", "+Bought vault page 3 for 50,000 coins - you now own 3 of 10 pages.",
             "-Vault page 5 is locked - you own 2 of 10 pages. Page 3 costs 50,000 coins - /vault buy",
             "=Page 4 is locked. Buy page 3 first.", "a line without a mark"]

    def setup(k, st, tag=""):
        Cfg, Store, Ses, Dat = jc(k, "VCfg"), jc(k, "VStore"), jc(k, "VSession"), jc(k, "VData")
        d = os.path.join(WORK, "data", k, st["name"] + tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.join(d, "vaults"))
        Cfg.DIR = Paths.get(d)
        Cfg.VDIR = Paths.get(d).resolve("vaults")
        Cfg.FILE = Paths.get(d).resolve("config.properties")
        Cfg.LOGF = Paths.get(d).resolve("vault.log")
        Cfg.NAMESF = Paths.get(d).resolve("names.properties")
        Cfg.FREE_PAGES, Cfg.MAX_PAGES, Cfg.SLOTS = st["free"], st["max"], st["cap"]
        Cfg.PRICE, Cfg.STEP, Cfg.BUY_CONFIRM = st["price"], st["step"], st["confirm"]
        Cfg.ARROWS, Cfg.ARROW_LAYOUT = st["arrows"], st["layout"]
        for m in ("CACHE", "PENDING", "BUYING", "LASTBUY", "NAMES"):
            getattr(Store, m).clear()
        Store.SAVER = None
        BR.clear()
        PURSE.clear()
        if st["purse"] != "none":
            BR.put("coins:fn:get", COINS[0])
            BR.put("coins:fn:add", COINS[1])
            BR.put("coins:fn:take", COINS[2])
            PURSE[US] = st["purse"]
        vd = None
        if st["unlocked"] is None:
            open(os.path.join(d, "vaults", US + ".json"), "w").write("{ this is not json")
        else:
            vd = Dat(UID, st["cap"])
            vd.unlocked = st["unlocked"]
            vd.page(st["unlocked"])
            for pg, n in st["items"].items():
                arr = vd.page(pg)
                for i in range(n):
                    arr[i] = stack("Food_Bread", 1 + i % 5)
            Store.CACHE.put(UID, vd)
        sess = None
        if st["sess"] is not None:
            sess = Ses()
            sess.owner = UID
            sess.viewer = UID
            sess.page = st["sess"][1]
            sess.mode = 1 if st["sess"][0] == "page" else 2
            sess.usable = Cfg.usable(st["cap"])
            sess.closed = False
        return vd, sess

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    def sets_of(cmds):
        return sorted((sel, data or "") for typ, sel, text, data in cmds if "append" not in typ.lower())

    def sets_seq(cmds):
        """review fix: the b.set lines IN ORDER (sets_of sorts them)"""
        return [(sel, data or "") for typ, sel, text, data in cmds if "append" not in typ.lower()]

    def order_problems(cmds):
        """review fix: every command on #Id.<prop> comes after the append that creates #Id (command index order)"""
        made, bad = {}, []
        for i, (typ, sel, text, data) in enumerate(cmds):
            if "append" in typ.lower():
                for ident in re.findall(r"#([A-Za-z0-9]+)\s*\{", text or ""):
                    made.setdefault(ident, i)
            elif sel:
                ident = sel.lstrip("#").split(".")[0]
                if ident not in made:
                    bad.append("%s (command %d) before / without the append of #%s" % (sel, i, ident))
        return bad

    def check_order(tag, cmds):
        bad = order_problems(cmds)
        if check(not bad, "%s: set before its append: %s" % (tag, bad[:4])):
            tally("order " + tag[:1], sum(1 for c in cmds if "append" not in c[0].lower()))

    def appends_of(cmds):
        return [(None if sel is None else sel[1:], text) for typ, sel, text, data in cmds if "append" in typ.lower()]

    def set_text(cmds, ident):
        v = [data for typ, sel, text, data in cmds if sel == "#%s.Text" % ident]
        if len(v) != 1:
            return None
        d = json.loads(v[0])
        return d.get("0") if isinstance(d, dict) else d

    def btn_texts(aps):
        out = {}
        for _p, text in aps:
            for m in re.finditer(r'TextButton #([A-Za-z0-9]+) \{[^{}]*?Text: "((?:[^"\\]|\\.)*)"', text):
                out[m.group(1)] = m.group(2)
        return out

    def ids_of(aps):
        return set(i for _p, t in aps for i in re.findall(r"#([A-Za-z0-9]+)\s*\{", t))

    # ---- the kit's expected markups NOW, as patterns (J() slots = captured runtime values)
    def pattern(mk):
        parts, pos, slots = [], 0, []
        for m in SUI._J_RE.finditer(mk):
            parts.append(re.escape(mk[pos:m.start()]))
            parts.append("(.*?)")
            slots.append(m.group(1))
            pos = m.end()
        parts.append(re.escape(mk[pos:]))
        return re.compile(r"\A" + "".join(parts) + r"\Z", re.S), slots

    def variants(mk):
        return list(mk.variants()) if isinstance(mk, SUI.Choice) else [mk]

    # (parent, regex, slots, piece name, look): look = the piece name, "<piece>:on" / ":off" for the two variants of a choose()
    # (on = its condition true: the pager's live Prev / Next), or the runtime-label button's look (numsel / numon / numoff, openon /
    # openoff, buyon / buyoff)
    PATS = []
    for nm, apc in K["VAULT_PIECES"].items():
        for parent, mk in apc:
            for vi, v in enumerate(variants(mk)):
                rx, sl = pattern(v)
                look = ("%s:%s" % (nm, ("on", "off")[vi])) if isinstance(mk, SUI.Choice) else nm
                PATS.append((None if parent is None else SUI.render(parent), rx, sl, nm, look))
    for nm, mk in K["VAULT_RT"].items():
        rx, sl = pattern(mk)
        PATS.append(("SkyyVNums" if nm.startswith("num") else "SkyyVAct", rx, sl, nm, nm))
    DPATS, DLG_CHOICE = [], []
    for ai, (parent, mk) in enumerate(K["VDLG_SH"].appends):
        for vi, v in enumerate(variants(mk)):
            rx, sl = pattern(v)
            look = ("dlg%d:%s" % (ai, ("on", "off")[vi])) if isinstance(mk, SUI.Choice) else "dlg%d" % ai
            DPATS.append((parent, rx, sl, "dlg", look))
        if isinstance(mk, SUI.Choice):
            DLG_CHOICE.append(ai)
    ALLOWED = set(SUI.allowed_colors())
    COL = SUI.COLOR
    SH = K["VAULT_SH"]
    W, BW = SH.inner_w, K["VAULT_BOX_W"]
    RT_IDS = ("SkyyVOpen", "SkyyVBuy")          # buttons whose inline label is a runtime value (+ the SkyyVNum<n> tabs)

    def expect_info(info):
        return SUI.STATUS.get(info[:1], COL["text"]) if info else COL["text"]

    def match_kit(tag, aps, pats, info=None, extra_slots=None):
        """every append equals a kit markup (J() slots filled); returns [(element id, {look of EVERY kit markup it matches})]"""
        used = []
        for parent, text in aps:
            hits = []
            for pp, rx, sl, nm, look in pats:
                if pp != parent:
                    continue
                m = rx.match(text)
                if m:
                    hits.append((m, sl, nm, look))
            em = re.match(r"\s*[A-Za-z]+ #([A-Za-z0-9]+)", text)
            used.append((em.group(1) if em else None, set(h[3] for h in hits)))
            if not check(hits, "C/D. %s: an append matches no kit markup: #%s %s" % (tag, parent, text[:160])):
                continue
            m, sl, nm, _look = hits[0]
            for expr, val in zip(sl, m.groups()):
                if "colorOf(this.info)" in expr:
                    check(val == expect_info(info), "C. %s: #SkyyVInfo colour %s, want %s" % (tag, val, expect_info(info)))
                    tally("C info " + {COL["success"]: "green", COL["error"]: "red", SUI.STATUS["="]: "blue",
                                       COL["text"]: "grey"}.get(val, val))
                elif "poor" in expr:
                    check(SUI.norm_color(val) in ALLOWED, "D. %s: note colour %s is not a kit colour" % (tag, val))
                    if extra_slots is not None:
                        extra_slots["note"] = val
                elif extra_slots is not None:
                    extra_slots.setdefault(expr, []).append(val)
        return used

    LOOK_FAMS = {"num": ("numsel", "numon", "numoff"), "SkyyVOpen": ("openon", "openoff"), "SkyyVBuy": ("buyon", "buyoff"),
                 "SkyyVPrev": ("nav:on", "nav:off"), "SkyyVNext": ("nav:on", "nav:off")}

    def check_looks(tag, used, ex):
        """review fix: WHICH look each stateful button gets, from the vault state after the build (ex: sel, unlocked, maxPages):
        tab n = numsel when n == sel, numon when n <= unlocked, else numoff; Open live iff sel <= unlocked; Buy live iff the next
        page is <= maxPages (and this.offer = that page, else 0); Prev live iff sel > 1; Next live iff sel < max(unlocked,
        maxPages). The append must match exactly that ONE look of its family (not the other variants)."""
        sel, unlocked, maxp = ex["sel"], ex["unlocked"], ex["maxp"]
        mx = unlocked if unlocked > maxp else maxp
        want_offer = unlocked + 1 if unlocked + 1 <= maxp else 0
        check(ex["offer"] == want_offer, "C. %s: this.offer %d, want %d" % (tag, ex["offer"], want_offer))
        seen = set()
        for ident, looks in used:
            m = re.fullmatch(r"SkyyVNum(\d+)", ident or "")
            if m:
                n = int(m.group(1))
                fam, want = LOOK_FAMS["num"], ("numsel" if n == sel else ("numon" if n <= unlocked else "numoff"))
                seen.add("SkyyVNum")
            elif ident in LOOK_FAMS:
                fam = LOOK_FAMS[ident]
                on = {"SkyyVOpen": sel <= unlocked, "SkyyVBuy": want_offer > 0, "SkyyVPrev": sel > 1, "SkyyVNext": sel < mx}[ident]
                want = fam[0] if on else fam[1]
                seen.add(ident)
            else:
                continue
            got = sorted(looks & set(fam))
            if check(got == [want], "C. %s: #%s has the look %s, want %s (sel %d, unlocked %d, maxPages %d)" % (
                    tag, ident, got, want, sel, unlocked, maxp)):
                tally("C looks " + (want if m or not want.startswith("nav") else ident[5:].lower() + want[3:]))
        check(seen == {"SkyyVNum", "SkyyVOpen", "SkyyVBuy", "SkyyVPrev", "SkyyVNext"}, "C. %s: stateful buttons seen: %s" % (tag, sorted(seen)))

    def check_new_vault(tag, st, info, cmds, old_cmds=None, ex=None):
        """0.1.4 VaultPage: kit markup, the look per state (ex), markup rules, the body budget, tabs centred, kit colours, command
        order"""
        aps = appends_of(cmds)
        slots = {}
        used = match_kit(tag, aps, PATS, info, slots)
        if ex is not None:
            check_looks(tag, used, ex)
        check_order("C/E. " + tag, cmds)
        for parent, text in aps:
            for m in re.finditer(r"Group #([A-Za-z0-9]+) \{[^{}]*LayoutMode: Left;[^{}]*\}", SUI._strip_quoted(text)):
                check("Padding:" not in m.group(0), "C. %s: row #%s has a Padding (kit 1.4 button_row, probe base4)" % (tag, m.group(1)))
        old_btn = btn_texts(appends_of(old_cmds)) if old_cmds is not None else {}
        for parent, text in aps:
            tb = re.match(r'\s*TextButton #([A-Za-z0-9]+) ', text)
            rtb = tb and (tb.group(1) in RT_IDS or re.fullmatch(r"SkyyVNum\d+", tb.group(1)))
            probe = text
            if rtb:
                # the runtime label is 0.1.3's text (compared in C); check the rest of the markup with a proven sample label
                probe = re.sub(r'Text: "(?:[^"\\]|\\.)*";', 'Text: "7";', text, count=1)
            try:
                SUI.check_markup(probe, prefix="SkyyV", root=(parent is None))
                tally("C markups")
            except ValueError as e:
                check(False, "C. %s: check_markup: %s" % (tag, e))
            for c in re.findall(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?(?![0-9A-Za-z])", SUI._strip_quoted(text)):
                check(SUI.norm_color(c) in ALLOWED, "C. %s: colour %s is not a kit colour" % (tag, c))
        try:
            probe_page = [(p, re.sub(r'(TextButton #(?:SkyyVOpen|SkyyVBuy|SkyyVNum\d+) \{[^{}]*?)Text: "(?:[^"\\]|\\.)*";',
                                     r'\1Text: "7";', t)) for p, t in aps]
            SUI.check_page(probe_page, prefix="SkyyV")
            tally("C pages")
        except ValueError as e:
            check(False, "C. %s: check_page: %s" % (tag, e))
        try:
            left = SUI.fit([SUI.used_height(aps, "SkyyVault")], SH.inner_h)
            check(left == 0, "C. %s: the body is filled exactly (%d px left)" % (tag, left))
        except ValueError as e:
            check(False, "C. %s: body budget: %s" % (tag, e))
        if st["unlocked"] is not None:
            tabs = [t for p, t in aps if p == "SkyyVNums"]
            row = [t for p, t in aps if re.match(r"\s*Group #SkyyVNums ", t)]
            if check(len(row) == 1 and tabs, "C. %s: one #SkyyVNums row with tabs" % tag):
                first = re.search(r"Anchor: \([^)]*\bLeft: (\d+)", tabs[0])
                pad = int(first.group(1)) if first else -1
                wide = SUI.used_width([("SkyyVNums", t) for t in tabs], "SkyyVNums")      # the first tab's Left + tabs + gaps
                check(pad >= 0 and abs((BW - wide) - pad) <= 1, "C. %s: page tabs centred in the well by the first tab's Anchor Left "
                                                                "(left %d, right %d, well %d)" % (tag, pad, BW - wide, BW))
        return aps

    # ---------------- C. differential VaultPage builds
    SEEN = {}
    n_builds = 0
    for st in STATES:
        for info in MARKS:
            res, pages = {}, {}
            for k in ("old", "new"):
                vd, sess = setup(k, st)
                pg = jc(k, "VaultPage")(pref(UID), sess, st["sel"])
                pg.info = info
                res[k] = build(pg)
                pages[k] = (int(pg.sel), int(pg.offer))
                n_builds += 1
            ex = None if st["unlocked"] is None else dict(sel=pages["new"][0], offer=pages["new"][1], unlocked=st["unlocked"],
                                                          maxp=st["max"])
            tag = "%s / %r" % (st["name"], info[:14])
            (co, eo), (cn, en) = res["old"], res["new"]
            check(sets_of(co) == sets_of(cn), "C. %s: b.set lines differ:\n  0.1.3 %s\n  0.1.4 %s" % (tag, sets_of(co), sets_of(cn)))
            check(sets_seq(co) == sets_seq(cn), "C. %s: the b.set lines come in another order than 0.1.3's" % tag)
            check(eo == en, "C. %s: event bindings differ:\n  0.1.3 %s\n  0.1.4 %s" % (tag, eo, en))
            check(pages["old"] == pages["new"], "C. %s: sel / offer after the build: %s / %s" % (tag, pages["old"], pages["new"]))
            ao, an = appends_of(co), appends_of(cn)
            check(btn_texts(ao) == btn_texts(an), "C. %s: button labels differ:\n  0.1.3 %s\n  0.1.4 %s" % (tag, btn_texts(ao), btn_texts(an)))
            missing = sorted(i for i in ids_of(ao) if i not in ids_of(an))
            check(not missing, "C. %s: 0.1.3 ids missing in 0.1.4: %s" % (tag, missing))
            check_new_vault(tag, st, info, cn, co, ex)
            tally("C bindings", len(en))
            for typ, sel, text, data in cn:
                if sel and sel.endswith(".Text"):
                    SEEN.setdefault(sel[1:-5], set()).add(set_text(cn, sel[1:-5]))
            for i, t in btn_texts(an).items():
                SEEN.setdefault("btn:" + re.sub(r"\d+$", "", i) if i.startswith("SkyyVNum") else "btn:" + i, set()).add(t)
    COUNT["C builds"] = n_builds
    print("C. %d VaultPage builds (%d states x %d result lines x 2 jars): %d 0.1.4 markups checked in %d pages, %d bindings "
          "compared; result line %s" % (n_builds, len(STATES), len(MARKS), COUNT.get("C markups", 0), COUNT.get("C pages", 0),
                                        COUNT.get("C bindings", 0),
                                        dict((k[7:], v) for k, v in COUNT.items() if k.startswith("C info "))))

    # ---------------- D. the confirm window: same texts, same bindings, SAME LOOK
    def norm_btn_style(v):
        if not isinstance(v, dict):
            return v
        out = {}
        for st_name, st_val in v.items():
            if st_name == "Disabled":
                continue
            if isinstance(st_val, dict) and isinstance(st_val.get("LabelStyle"), dict):
                st_val = dict(st_val)
                ls = dict(st_val["LabelStyle"])
                ls.pop("ShrinkTextToFit", None)
                ls.pop("MinShrinkTextToFitFontSize", None)
                st_val["LabelStyle"] = ls
            out[st_name] = st_val
        return out

    DSTATES = [("buy-rich", 3, 50000, 1000000, "ok"), ("buy-poor", 3, 50000, 1200, "ok"), ("buy-unread", 4, 75000, None, "ok"),
               ("buy-nocoins", 3, 50000, "none", "ok"), ("unlock-free", 3, 0, 500, "ok"), ("no-vault-file", 3, 50000, 1000, "bad")]
    n_dlg = 0
    DLG_W = K["VDLG_SH"].inner_w
    for name, page_no, cost, purse, vault in DSTATES:
        res, trees = {}, {}
        for k in ("old", "new"):
            st = S("dlg-" + name, purse=purse, unlocked=None if vault == "bad" else 2)
            setup(k, st)
            dg = jc(k, "VBuyDlg")(pref(UID), page_no, cost, 1, 1)
            res[k] = build(dg)
            trees[k] = page_tree([(None if p is None else "#" + p, t) for p, t in appends_of(res[k][0])])
            n_dlg += 1
        (co, eo), (cn, en) = res["old"], res["new"]
        check(sets_of(co) == sets_of(cn), "D. %s: b.set lines differ:\n  0.1.3 %s\n  0.1.4 %s" % (name, sets_of(co), sets_of(cn)))
        check(sets_seq(co) == sets_seq(cn), "D. %s: the b.set lines come in another order than 0.1.3's" % name)
        check(eo == en and len(en) == 2, "D. %s: event bindings differ: %s / %s" % (name, eo, en))
        check_order("D. " + name, cn)
        slots = {}
        dused = match_kit("dlg " + name, appends_of(cn), DPATS, None, slots)
        # review fix: the Buy / Unlock look by the price (the window's one choose())
        if check(len(DLG_CHOICE) == 1, "D. the window has one choose() (Buy / Unlock): %s" % DLG_CHOICE):
            want = "dlg%d:%s" % (DLG_CHOICE[0], "on" if cost > 0 else "off")
            got = sorted(lk for ident, looks in dused if ident == "SkyyVDlgBuy" for lk in looks if lk.startswith("dlg%d:" % DLG_CHOICE[0]))
            if check(got == [want], "D. %s: #SkyyVDlgBuy has the look %s, want %s (cost %d)" % (name, got, want, cost)):
                tally("D looks " + ("buy" if cost > 0 else "unlock"))
        poor = (set_text(cn, "SkyyVDlgNote") or "").endswith("not enough.")
        check(slots.get("note") == (COL["outOfStock"] if poor else COL["text"]), "D. %s: note colour %s (poor %s)" % (name, slots.get("note"), poor))
        try:
            SUI.check_page(appends_of(cn), prefix="SkyyVDlg")
            tally("D pages")
        except ValueError as e:
            check(False, "D. %s: check_page: %s" % (name, e))
        to, tn = trees["old"], trees["new"]
        check(sorted(to) == sorted(tn), "D. %s: the element trees differ: 0.1.3 only %s, 0.1.4 only %s" % (
            name, sorted(set(to) - set(tn)), sorted(set(tn) - set(to))))
        for path in sorted(set(to) & set(tn)):
            (ty0, p0, par0), (ty1, p1, par1) = to[path], tn[path]
            check(ty0 == ty1 and par0 == par1, "D. %s: %s is %s in %s / %s in %s" % (name, path, ty0, par0, ty1, par1))
            p0, p1 = dict(p0), dict(p1)
            if ty0 == "TextButton":
                p0["Style"], p1["Style"] = norm_btn_style(p0.get("Style")), norm_btn_style(p1.get("Style"))
            if path == "#SkyyVDlgBtns":
                check(p0.pop("LayoutMode", None) == "Center" and p1.pop("LayoutMode", None) == "Left", "D. %s: row layout" % name)
                check("Padding" not in p1, "D. %s: the button row has no Padding (kit 1.4 button_row, probe base4): %s" % (name, p1))
            if path == "#SkyyVDlgBuy":
                # the pair is centred by Buy's own Anchor Left (the pager's centring margin) - 0.1.3's LayoutMode Center did it
                want = (DLG_W - 2 * (K["VDLG_BTN_W"] + K["VDLG_BTN_GAP"])) // 2
                a1 = dict(p1.get("Anchor") or {})
                check(a1.pop("Left", None) == str(want) and "Left" not in (p0.get("Anchor") or {}),
                      "D. %s: Buy centres the pair by Anchor Left %d: %s" % (name, want, p1.get("Anchor")))
                p1["Anchor"] = a1
            if check(p0 == p1, "D. %s: %s looks different:\n  0.1.3 %s\n  0.1.4 %s" % (name, path, p0, p1)):
                tally("D elements")
        for typ, sel, text, data in cn:
            if sel and sel.endswith(".Text"):
                SEEN.setdefault(sel[1:-5], set()).add(set_text(cn, sel[1:-5]))
        tally("D notes " + ("red" if poor else "grey"))
    COUNT["D builds"] = n_dlg
    print("D. %d confirm window builds (%d states x 2 jars): identical texts / bindings (same order, each after its append), %d "
          "elements compared property by property, notes %s, Buy / Unlock %s" % (
              n_dlg, len(DSTATES), COUNT.get("D elements", 0), dict((k[8:], v) for k, v in COUNT.items() if k.startswith("D notes ")),
              dict((k[8:], v) for k, v in COUNT.items() if k.startswith("D looks "))))

    # ---------------- E. clicks (handleDataEvent), identical on both jars
    def vault_file(k, st, tag):
        f = os.path.join(WORK, "data", k, st["name"] + tag, "vaults", US + ".json")
        if not os.path.exists(f):
            return None
        try:
            d = json.loads(open(f, encoding="utf8").read())
        except ValueError:
            return "unreadable"
        d.pop("savedAt", None)
        if d.get("version") in (VERSION, OLD_VERSION):
            d["version"] = "<v>"
        return json.dumps(d, sort_keys=True)

    def log_lines(k, st, tag):
        f = os.path.join(WORK, "data", k, st["name"] + tag, "vault.log")
        if not os.path.exists(f):
            return []
        return [re.sub(r"^\S+ ", "", ln.strip()) for ln in open(f, encoding="utf8") if ln.strip()]

    CLICKS = ["prev", "next", "next", "num:1", "num:3", "num:9", "num:11", "prev", "open", "buy", "buy", "num:3", "buy", "num:0",
              "bogus", "", "close"]
    ESTATES = [S("click-cheap", price=10000, step=5000, confirm=50000), S("click-dear"),
               S("click-live", sess=("page", 1), price=0, step=0), S("click-unread", unlocked=None),
               S("click-poor", price=10000, step=5000, confirm=50000, purse=500)]
    n_clicks = 0
    for st in ESTATES:
        trace = {}
        for k in ("old", "new"):
            vd, sess = setup(k, st, "-e")
            pg = jc(k, "VaultPage")(pref(UID), sess, st["sel"])
            steps = []
            for a in CLICKS:
                data = json.dumps({"a": a}) if a else "{}"
                pg.handleDataEvent(None, None, data)
                n_clicks += 1
                Store = jc(k, "VStore")
                d = Store.CACHE.get(UID)
                cmds, evs = build(pg)
                steps.append((a, str(pg.info), int(pg.sel), int(pg.offer), PURSE.get(US, "none") if st["purse"] != "none" else "none",
                              None if d is None else int(d.unlocked), vault_file(k, st, "-e"), log_lines(k, st, "-e"), sets_of(cmds), evs))
                if k == "new":
                    ex = None if d is None else dict(sel=int(pg.sel), offer=int(pg.offer), unlocked=int(d.unlocked), maxp=st["max"])
                    check_new_vault("E. %s after %r" % (st["name"], a), st, str(pg.info), cmds, None, ex)
                    for typ, sel, text, data2 in cmds:
                        if sel and sel.endswith(".Text"):
                            SEEN.setdefault(sel[1:-5], set()).add(set_text(cmds, sel[1:-5]))
            trace[k] = steps
        for so, sn in zip(trace["old"], trace["new"]):
            check(so == sn, "E. %s: after %r:\n  0.1.3 %s\n  0.1.4 %s" % (st["name"], so[0], so[1:8], sn[1:8]))
        bought = [s for s in trace["new"] if s[1].startswith("+Bought")]
        tally("E buys", len(bought))
    # the confirm window's own clicks: Buy, Cancel, junk, a double click on Buy
    DCLICKS = [("buy", ["dlgbuy"]), ("cancel", ["dlgno"]), ("junk", ["x", "{}", "dlgbuyy"]), ("double", ["dlgbuy", "dlgbuy", "dlgno"])]
    for name, seq in DCLICKS:
        trace = {}
        for k in ("old", "new"):
            st = S("dlgclick-" + name, price=50000)
            setup(k, st, "-d")
            dg = jc(k, "VBuyDlg")(pref(UID), 3, 50000, 1, 2)
            steps = []
            for a in seq:
                dg.handleDataEvent(None, None, json.dumps({"a": a}) if a not in ("{}",) else "{}")
                n_clicks += 1
                d = jc(k, "VStore").CACHE.get(UID)
                steps.append((a, bool(dg.done), PURSE.get(US), None if d is None else int(d.unlocked), vault_file(k, st, "-d"),
                              log_lines(k, st, "-d")))
            trace[k] = steps
        check(trace["old"] == trace["new"], "E. confirm window %s: 0.1.3 %s | 0.1.4 %s" % (name, trace["old"], trace["new"]))
        if trace["new"] and any(x.startswith("BUY ") for x in trace["new"][-1][5]):
            tally("E window buys")
    COUNT["E clicks"] = n_clicks
    print("C + E. looks per state: %s; %d b.set lines after their append (C + E)" % (
        dict(sorted((k[8:], v) for k, v in COUNT.items() if k.startswith("C looks "))), COUNT.get("order C", 0)))
    print("E. %d clicks (%d page states x %d clicks + %d window sequences, both jars): identical result, selection, offer, purse, "
          "pages, vault file and log; %d page purchases from the page, %d from the window" % (
              n_clicks, len(ESTATES), len(CLICKS), len(DCLICKS), COUNT.get("E buys", 0), COUNT.get("E window buys", 0)))

    # ---------------- F. text fit (the client's font tables through the kit; read-only)
    if SUI.font_table("Default", False) is None:
        print("F. skipped: no client font tables")
    else:
        n_fit = 0
        lh = SUI.line_height(16)
        one = {"SkyyVSub": (16, False, W), "SkyyVUsed": (16, True, BW), "SkyyVPageLbl": (16, True, K["VAULT_CAPTION_W"]),
               "SkyyVHelp0": (16, False, W), "SkyyVHelp1": (16, False, W), "SkyyVHelp2": (16, False, W),
               "SkyyVDlgQ": (30, False, DLG_W), "SkyyVDlgNote": (14, False, DLG_W)}
        for ident, (size, bold, width) in one.items():
            for t in SEEN.get(ident, ()):
                if not t:
                    continue
                n_fit += 1
                tw = SUI.text_width(t, size, bold)
                check(tw <= width, "F. #%s one line %r: %.0f px > %d px" % (ident, t, tw, width))
        wrap = {"SkyyVInfo": (16, True, W, 2), "SkyyVErr": (16, True, W - 2 * SUI.WELL_PAD, 3), "SkyyVDlgMsg": (16, False, DLG_W, 2)}
        most = {}
        for ident, (size, bold, width, mx) in wrap.items():
            for t in SEEN.get(ident, ()):
                if not t:
                    continue
                n_fit += 1
                nl = SUI.text_lines(t, width, size, bold)
                most[ident] = max(most.get(ident, 0), nl)
                check(nl <= mx, "F. #%s wraps to %d lines (at most %d): %r" % (ident, nl, mx, t))
        check(2 * lh <= K["VAULT_TWO_LINES"], "F. two 16 px lines (%.1f px) fit the %d px result line" % (2 * lh, K["VAULT_TWO_LINES"]))
        FIT = []
        for key, size, width, pad in (("btn:SkyyVBuy", 17, K["VAULT_BUY_W"], SUI.BTN_PAD), ("btn:SkyyVOpen", 17, K["VAULT_OPEN_W"], SUI.BTN_PAD),
                                      ("btn:SkyyVNum", 17, K["VAULT_NUM_W"], SUI.BTN_PAD), ("btn:SkyyVPrev", 14, 150, SUI.BTN_SMALL_PAD),
                                      ("btn:SkyyVNext", 14, 150, SUI.BTN_SMALL_PAD), ("btn:SkyyVClose", 17, SUI.BTN_MIN_W, SUI.BTN_PAD)):
            worst = (0, "")
            for t in SEEN.get(key, ()):
                n_fit += 1
                tw = SUI.text_width(t, size, True, upper=True)
                worst = max(worst, (tw, t))
                check(tw <= width - 2 * pad, "F. %s label %r: %.0f px, %d px of room" % (key[4:], t, tw, width - 2 * pad))
            FIT.append("%s %.0f/%d (%r)" % (key[4:], worst[0], width - 2 * pad, worst[1]))
        COUNT["F texts"] = n_fit
        print("F. text fit: %d texts / labels measured; most lines %s; widest labels: %s" % (n_fit, most, ", ".join(FIT)))

    # ---------------- G. the page id
    pid, chk = K["VAULT_PAGE_ID"], K["VAULT_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready log line names the pages the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW))
    check(pid == chk, "G. the pages the kit makes now (%s) are the checked pages VAULT_PAGE_CHECKED (%s): if everything else passed, "
                      "set VAULT_PAGE_CHECKED = %r in SkyyVault/build_skyyvault_0.1.4.py and rebuild" % (pid, chk, pid))
    kit_in_log = SUI.kit_id() in LOG_NEW
    print("G. page id %s, checked %s, kit %s%s" % (pid, chk, SUI.kit_id(), "" if kit_in_log else " (the jar was built on another kit file)"))
    # H. the build-time proofs again on the current kit: every state of both pages is proven-properties only
    for name, ap in K["VAULT_STATES"].items():
        try:
            SUI.assert_proven(ap)
            SUI.check_page(ap, "SkyyV")
            OKS[0] += 1
        except ValueError as e:
            check(False, "H. vault page state %s: %s" % (name, e))
    try:
        SUI.assert_proven(K["VDLG_SH"].appends)
        OKS[0] += 1
    except ValueError as e:
        check(False, "H. confirm window: %s" % e)
    print("H. assert_proven + check_page on the kit's page states: vault %s, confirm window" % sorted(K["VAULT_STATES"]))


def main():
    global WORK
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    if not scratch_ok(SCRATCH):
        print("refused: --dir %s is not under %s (the harness only works in the project's scratch folder)" % (SCRATCH, SCRATCH_ROOT))
        return 2
    os.makedirs(SCRATCH, exist_ok=True)
    WORK = tempfile.mkdtemp(prefix="run-", dir=SCRATCH)
    tmp = os.path.join(WORK, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyVault %s page harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAIL", f[:600])
    return 1 if FAILS else 0


if __name__ == "__main__":
    made_scratch = not os.path.exists(SCRATCH)
    code = main()
    if WORK is not None:
        if KEEP:
            print("kept", WORK)
        else:
            shutil.rmtree(WORK, ignore_errors=True)          # only the fresh run-* folder this run made
            if made_scratch and os.path.isdir(SCRATCH) and not os.listdir(SCRATCH):
                os.rmdir(SCRATCH)                             # --dir itself only when this run made it and it is empty now
    sys.stdout.flush()
    os._exit(code)
