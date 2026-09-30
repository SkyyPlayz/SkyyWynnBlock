"""Bare-JVM harness for SkyyVault 0.1.5 - THE ARROW CLICK (Skyy in game, 0.1.4 live, 2026-09-30: "arrow button works, but not when i
click it, i have to set it back down"; research/Vault-Arrow-Click-Research.md). Copy + edit of test_skyyvault_0.1.4.py; committed next
to the build so the build docstring's CHECKED claims can be re-run instead of trusted. Copy it to the next version and keep it passing.

    python SkyyVault/test_skyyvault_0.1.5.py [--jar <SkyyVault-0.1.5.jar>] [--old <SkyyVault-0.1.4.jar>] [--dir <scratch>]
                                             [--live <a Skyy_SkyyVault data folder>] [--keep]

Build first (python SkyyVault/build_skyyvault_0.1.5.py). One JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar +
tools/javassist.jar on the classpath; EACH SkyyVault jar in its own class loader, so 0.1.4 - the live SET pin - and 0.1.5 run side by
side in one process) checks:
  A  every class of both jars loads, verifies and initialises
  B  the 0.1.5 contract in bytes: the class names are 0.1.4's + VDropSys; every class is byte-identical to 0.1.4 except CfgFn /
     CfgRows (only the embedded version string) and VStore (the version string, then - review fix - infoLines' help line) / VBtn /
     VaultPage / VSessions / VWindow / SkyyVaultPlugin, whose changes are pinned
     method by method: which methods changed / are new (VStore.infoLines, VBtn.row, VaultPage.build, VSessions.open2 + resync + new
     dropKey / dropEvent, VWindow + resend, SkyyVaultPlugin.setup), which string constants went / came (only the hint texts and the
     ready line), which
     engine / field references went / came (only the Drop-key system registration, the arrows switch read in VaultPage.build and the
     resend fix); VDropSys's shape (EntityEventSystem on DropItemEvent$PlayerRequest, query Player, shouldProcessEvent = true, the
     handle order); nothing in the jar ever un-cancels an event; no protected / package / private ENGINE member is referenced from a
     class that may not access it (0.1.4: exactly one - VSessions.resync -> the protected Window.invalidate(), an IllegalAccessError
     swallowed at run time; 0.1.5: none); the non-class entries differ only in server.lang (3 arrow descriptions) and the manifest
  C  differential VaultPage builds, 0.1.4 vs 0.1.5, in 20 vault states x 5 result lines: every appended markup IDENTICAL (so the look
     the 0.1.4 harness proved is unchanged), identical event bindings, sel / offer and b.set lines in the same order - except the
     three help lines, which must be exactly the new texts (page with arrow slots; chest mode's /vault pages page with arrows) or
     exactly 0.1.4's (pageArrows off, the unreadable file); every markup still equals the kit's (check_new_vault, as in 0.1.4)
  D  the confirm window: identical texts, bindings and element trees on both jars (VBuyDlg is byte-identical)
  E  clicks through handleDataEvent on both jars (6 states x 17 clicks + 4 window sequences): identical result, selection, offer,
     purse, owned pages, vault file and vault.log after every click; the help lines as in C
  F  text fit with the client's font tables (every help line on one line of its box, every label as in 0.1.4)
  G  the page id: VAULT_PAGE_ID of the kit's pages NOW == VAULT_PAGE_CHECKED in the build script == the id in the jar's ready line
  H  assert_proven + check_page on the kit's page states
  I  THE TRIGGERS, END TO END, both jars: a real /vault (VSessions.open2 with a stand-in page manager that accepts the window), the
     real VView / VBtnFilter / VDropSys / VBtnTask / btnBatch / btnClick / swap, a stand-in world whose execute() queues the task (run
     by the harness like the world thread would) and a stand-in store / chunk for the ECS dispatch (EntityEventSystem.handleInternal,
     exactly what Store.invoke calls). Every gesture goes through the engine's own container calls (MoveItemStack =
     moveItemStackFromSlotToSlot, SmartMoveItemStack = moveItemStackFromSlot, DropItemStack = the DropItemEvent$PlayerRequest dispatch,
     then - if not cancelled - removeItemStackFromSlot, mirrored from InventoryPacketHandler.lambda$handle$4 offsets 46-255). Per
     gesture: the page after, the chat lines, coins, owned pages, the engine warnings, whether the request was cancelled; item counts
     before / after (vault pages + inventory + thrown, per item id); no vault arrow item outside the control row DURING the gesture
     (before the batch runs) and after it; the control row canonical; 0.1.4 vs 0.1.5 identical except the Drop key (0.1.5 cancels the
     request: no engine WARNING; a request another system / the game mode already refused still turns the page) and the window
     re-send (0.1.5 marks the window dirty after every click batch). Plus the opening chat line, the in-chest tooltips and the /vault
     info lines (0.1.4's except the planned help-line tail with arrows on; identical with arrows off and for admins).
  J  START TWICE on a scratch COPY of the live Skyy_SkyyVault folder (read-only source, both jars): config load, names, every vault
     file; an open / close with no change writes nothing; a forced save, then a second start reads exactly what the first one saw and
     its save is the same file (savedAt / rev aside); config.properties + names.properties untouched; 0.1.4 and 0.1.5 read and write
     the same (the file's "version" aside)
Not testable without the game (UNVERIFIED in the build docstring): whether the client sends SmartMoveItemStack / DropItemStack on the
PRESS, how it draws a refused move, the real PageManager / WindowManager packets, the tooltips on screen.
Nothing is deployed and nothing outside the scratch folder is written (the live folder is only read and copied). --dir (default
tools/dev/scratch/test-vault) must lie under tools/dev/scratch (anything else is refused); the harness works in a FRESH sub-folder it
makes inside it (run-*; TEMP / TMP and java.io.tmpdir point into it) and deletes only that sub-folder at the end (unless --keep), plus
--dir itself when the harness made it and it is empty then. Exit code 1 on any failure, 2 on a refused --dir.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, hashlib, tempfile, collections, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.5", "0.1.4"
PKG = "com.skyy.vault."
SCRIPT = os.path.join(HERE, "build_skyyvault_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def default_live():
    """the live world's Skyy_SkyyVault folder (tools/deploy_set.py WORLD) - only read and copied"""
    try:
        import skyybuild as B
        w = re.search(r'^WORLD\s*=\s*"([^"]+)"', open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf8").read(), re.M).group(1)
        return os.path.join(B.USERDATA, "Saves", w, "mods", "Skyy_SkyyVault")
    except Exception:
        return ""


SCRATCH_ROOT = os.path.join(TOOLS, "dev", "scratch")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "test-vault")))
WORK = None                        # the fresh run-* folder inside SCRATCH (main); the only thing the harness deletes
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyVault-%s.jar" % OLD_VERSION)))
LIVE = arg("--live", None) or default_live()
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}

# ---- the 0.1.5 hint texts (the task: say exactly what to do) and 0.1.4's, as the jars must send them
HELP = {
    "old-live": ["Drag items between your inventory and the vault slots. Close or Esc saves your vault.",
                 "Vault slots not showing next to this page? Click Open as chest.",
                 "Commands: /vault 2 opens page 2, /vault next and /vault prev switch pages, /vault info"],
    "old-pages": ["Pick a page, then click Open to see its items as a chest.",
                  "In the chest: drag items in and out - Esc saves. /vault 2 or /vault next switches pages.",
                  "Every profile opens this same vault. Commands: /vault buy, /vault info"],
    "new-live": ["Drag items in and out - Esc saves. No vault slots next to this page? Click Open as chest.",
                 "One click turns pages: < Prev / Next > or a page number above. In the slots: shift-click an arrow.",
                 "A plain click on an arrow only lifts it - the page turns when you put it back. Drop key works too."],
    "new-pages": ["Pick a page, then click Open to see its items as a chest.",
                  "In the chest: shift-click an arrow (or press Drop on it) to turn pages at once - Esc saves.",
                  "Every profile opens this same vault. Commands: /vault buy, /vault info"],
}
OPEN_OLD = ("=Vault page %d of %d (shared by all your profiles): the arrows in the bottom row turn pages, Esc saves. /vault <page> "
            "jumps.")
OPEN_NEW = ("=Vault page %d of %d (shared by all your profiles): shift-click an arrow (or press Drop on it) to turn pages at once, or "
            "click it twice. Esc saves. /vault <page> jumps.")
OPEN_NOARROWS = "=Vault page %d of %d (shared by all your profiles): drag items in and out, Esc saves. /vault next or /vault <page> switches pages."
TIP_HOW2 = "Your Drop key on it works too."
TIP_HOW3 = "A plain click lifts it - the page turns when you put it back."
TIP_INFO = ["Arrows: shift-click one, or press your Drop key on it, to turn at once.",
            "A plain click lifts an arrow - the page turns when you put it back."]
# /vault info's help line (VStore.infoLines, player view): 0.1.4's, and 0.1.5's with arrows on (review fix: it names the gestures too)
INFO_HELP = "=/vault opens it, /vault 2 opens page 2, /vault next | prev switch pages, /vault pages shows the page buttons."
INFO_ARROWS_OLD = " The arrows in the vault window turn pages too."
INFO_ARROWS_NEW = " The arrows in the vault window turn pages too. Shift-click one, or press Drop on it, to turn at once."
LANG_NEW = (("Prev", "Shift-click or press Drop: turns the vault window to the previous page."),
            ("Next", "Shift-click or press Drop: turns the vault window to the next page."),
            ("Buy", "Shift-click or press Drop: buys (or asks to confirm) the next vault page."))


def want_help(k, live, layout, arrows):
    if k == "old":
        return HELP["old-live"] if live else HELP["old-pages"]
    if live:
        return HELP["new-live"] if layout != 0 else HELP["old-live"]
    return HELP["new-pages"] if arrows else HELP["old-pages"]


def scratch_ok(path):
    """--dir must be a folder UNDER tools/dev/scratch (the brief's only scratch place)"""
    root = os.path.normcase(os.path.abspath(SCRATCH_ROOT)).rstrip("\\/") + os.sep
    return os.path.normcase(os.path.abspath(path)).startswith(root)


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what[:800])
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


def entries(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n, z.read(n)) for n in z.namelist())
    z.close()
    return out


def classes(jar):
    return dict((n[:-6].replace("/", "."), b) for n, b in entries(jar).items() if n.endswith(".class"))


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
    """{path: (type, props)} of a whole page from its (parent selector or None, markup) appends"""
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
    from jpype import JClass, JArray, JImplements, JOverride, JShort, JInt
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
    print("A. loaded + verified + initialised: 0.1.4 %d, 0.1.5 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. the 0.1.5 contract in bytes
    old, new = CB["old"], CB["new"]
    check(sorted(set(new) - set(old)) == [PKG + "VDropSys"] and not (set(old) - set(new)),
          "B. class names = 0.1.4's + VDropSys: new %s, gone %s" % (sorted(set(new) - set(old)), sorted(set(old) - set(new))))
    CODE = ("VStore", "VBtn", "VaultPage", "VSessions", "VWindow", "SkyyVaultPlugin")
    ver_only, n_same = [], 0
    for n in sorted(old):
        short = n.rsplit(".", 1)[1]
        if short in CODE or n not in new:
            continue
        if old[n] == new[n]:
            n_same += 1
            OKS[0] += 1
            continue
        swapped = new[n].replace(VERSION.encode(), OLD_VERSION.encode())
        if check(swapped == old[n], "B. %s differs from 0.1.4 by more than its embedded version string" % n):
            ver_only.append(short)
    check(sorted(ver_only) == ["CfgFn", "CfgRows"], "B. only the config kit's CfgFn / CfgRows differ by nothing but the version "
                                                  "string: %s" % ver_only)
    for short in CODE:
        check(old[PKG + short] != new[PKG + short], "B. %s changed as planned" % short)
    # VStore carries the file's version string too: compare its methods with 0.1.5 swapped back to 0.1.4 (same length, a valid class)
    NEWB = dict(new)
    NEWB[PKG + "VStore"] = new[PKG + "VStore"].replace(VERSION.encode(), OLD_VERSION.encode())
    check(NEWB[PKG + "VStore"] != new[PKG + "VStore"], "B. VStore embeds the file's version string")
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    Mod = JClass("javassist.Modifier")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    BRANCH = re.compile(r"\A(if\w*|goto|goto_w|jsr|jsr_w) (\d+)\Z")

    def code_of(m):
        """the method's instructions with constant-pool indices resolved, ldc_w read as ldc, branch targets as instruction indices"""
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

    REF_RE = re.compile(r"\A(invoke\w+|getstatic|putstatic|getfield|putfield|new|checkcast|instanceof) ")
    READY = '"[SkyyVault] '
    S_ROW_MINUS = {'"Click to turn to page "': 4, '"."': 4, '"Click - a window asks you to confirm."': 1, '"Click to buy it."': 1,
                   '"Click to unlock it."': 1}
    S_ROW_PLUS = {'"%s"' % TIP_HOW2: 1, '"%s"' % TIP_HOW3: 1, '"Shift-click to turn to page "': 4, '" at once."': 4,
                  '"Shift-click - a window asks you to confirm."': 1, '"Shift-click to buy it at once."': 1,
                  '"Shift-click to unlock it at once."': 1, '"A plain click lifts it - the window opens when you put it back."': 1,
                  '"A plain click lifts it - it buys when you put it back."': 1,
                  '"A plain click lifts it - it unlocks when you put it back."': 1, '"%s"' % TIP_INFO[0]: 1, '"%s"' % TIP_INFO[1]: 1}
    S_PAGE_PLUS = dict(('"%s"' % t, 1) for t in HELP["new-live"] + HELP["new-pages"][1:2])
    S_PAGE_PLUS['"%s"' % HELP["new-pages"][0]] = 1      # 0.1.4 had this line in one branch; 0.1.5 has it in two
    S_PAGE_PLUS['"%s"' % HELP["new-pages"][2]] = 1
    OPEN_TAIL_OLD = '" (shared by all your profiles): the arrows in the bottom row turn pages, Esc saves. /vault <page> jumps."'
    OPEN_TAIL_NEW = '"%s"' % OPEN_NEW.split("%d", 2)[2]
    WINV = "invokevirtual Method com.hypixel.hytale.server.core.entity.entities.player.windows.Window.invalidate(()V)"
    B_EXPECT = {
        "VStore": dict(changed=["infoLines"], added=[], smin={'"%s"' % INFO_ARROWS_OLD: 1}, splus={'"%s"' % INFO_ARROWS_NEW: 1},
                       rmin={}, rplus={}),
        "VBtn": dict(changed=["row"], added=[], smin=S_ROW_MINUS, splus=S_ROW_PLUS, rmin={}, rplus={}),
        "VaultPage": dict(changed=["build"], added=[], smin={}, splus=S_PAGE_PLUS, rmin={}, rplus={
            "getfield Field com.skyy.vault.VaultPage.sess(Lcom/skyy/vault/VSession;)": 1,
            "getfield Field com.skyy.vault.VSession.layout(I)": 1, "getstatic Field com.skyy.vault.VCfg.ARROWS(Z)": 1}),
        "VSessions": dict(changed=["open2", "resync"], added=["dropEvent", "dropKey"], smin={OPEN_TAIL_OLD: 1},
                          splus={OPEN_TAIL_NEW: 1}, rmin={WINV: 1}, rplus={"invokevirtual Method com.skyy.vault.VWindow.resend(()V)": 1}),
        "VWindow": dict(changed=[], added=["resend"], smin={}, splus={}, rmin={}, rplus={}),
        "SkyyVaultPlugin": dict(changed=["setup"], added=[], smin={}, splus={
            '"the vault Drop-key system could not be registered (Drop on an arrow still turns the page through the arrow filter): "': 1},
            rmin={}, rplus={
                "invokevirtual Method com.hypixel.hytale.server.core.plugin.PluginBase.getEntityStoreRegistry(()Lcom/hypixel/hytale/component/ComponentRegistryProxy;)": 1,
                "new Class com.skyy.vault.VDropSys": 1, "invokespecial Method com.skyy.vault.VDropSys.<init>(()V)": 1,
                "invokevirtual Method com.hypixel.hytale.component.ComponentRegistryProxy.registerSystem((Lcom/hypixel/hytale/component/system/ISystem;)V)": 1,
                "new Class java.lang.StringBuffer": 1, "invokespecial Method java.lang.StringBuffer.<init>(()V)": 1,
                "invokevirtual Method java.lang.StringBuffer.append((Ljava/lang/String;)Ljava/lang/StringBuffer;)": 1,
                "invokevirtual Method java.lang.StringBuffer.append((Ljava/lang/Object;)Ljava/lang/StringBuffer;)": 1,
                "invokevirtual Method java.lang.StringBuffer.toString(()Ljava/lang/String;)": 1,
                "invokestatic Method com.skyy.vault.VCfg.warn((Ljava/lang/String;)V)": 1}),
    }
    READY_LINES = {}
    for short, ex in B_EXPECT.items():
        co, cn = ct(old[PKG + short]), ct(NEWB[PKG + short])
        check(fields(co) == fields(cn), "B. %s: the same fields" % short)
        check(str(co.getClassFile().getSuperclass()) == str(cn.getClassFile().getSuperclass()), "B. %s: superclass unchanged" % short)
        check(sorted(co.getClassFile().getInterfaces()) == sorted(cn.getClassFile().getInterfaces()), "B. %s: interfaces unchanged" % short)
        mo, mn = methods(co), methods(cn)
        gone = sorted(k2.split("(")[0] for k2 in mo if k2 not in mn)
        added = sorted(k2.split("(")[0] for k2 in mn if k2 not in mo)
        changed = sorted(k2.split("(")[0] for k2 in mo if k2 in mn and mo[k2] != mn[k2])
        same = sum(1 for k2 in mo if k2 in mn and mo[k2] == mn[k2])
        check(gone == [] and added == ex["added"] and changed == ex["changed"],
              "B. %s: gone %s / new %s (want %s) / changed %s (want %s)" % (short, gone, added, ex["added"], changed, ex["changed"]))
        so, sn, ro, rn = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
        for k2 in mo:
            if k2 in mn and mo[k2] != mn[k2]:
                for t in mo[k2]:
                    if t.startswith('ldc "'):
                        so[t[4:]] += 1
                    elif REF_RE.match(t):
                        ro[t] += 1
                for t in mn[k2]:
                    if t.startswith('ldc "'):
                        sn[t[4:]] += 1
                    elif REF_RE.match(t):
                        rn[t] += 1
        for tag, cc in (("old", so), ("new", sn)):
            for t in list(cc):
                if t.startswith(READY):
                    READY_LINES.setdefault(tag, []).append(t[1:-1])
                    del cc[t]
        check(dict(so - sn) == ex["smin"], "B. %s: string constants gone %s\n   want %s" % (short, dict(so - sn), ex["smin"]))
        check(dict(sn - so) == ex["splus"], "B. %s: string constants new %s\n   want %s" % (short, dict(sn - so), ex["splus"]))
        check(dict(ro - rn) == ex["rmin"], "B. %s: references gone %s (want %s)" % (short, dict(ro - rn), ex["rmin"]))
        check(dict(rn - ro) == ex["rplus"], "B. %s: references new %s\n   want %s" % (short, dict(rn - ro), ex["rplus"]))
        COUNT["B " + short] = (same, changed, added)
    r_old, r_new = READY_LINES.get("old", []), READY_LINES.get("new", [])
    LOG_NEW = r_new[0] if len(r_new) == 1 else ""
    check(len(r_old) == 1 and re.fullmatch(r"\[SkyyVault\] 0\.1\.4 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page 80f113b82aa1\) - /vault "
                                           r"\(shared by all profiles\), /vaultadmin; ", r_old[0]) is not None,
          "B. 0.1.4 ready constant: %s" % r_old)
    check(re.fullmatch(r"\[SkyyVault\] 0\.1\.5 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page [0-9a-f]{12}\) - /vault \(shared by all "
                       r"profiles\), /vaultadmin; ", LOG_NEW) is not None, "B. the 0.1.5 ready constant names the kit and the page id: %r"
          % LOG_NEW)
    # VWindow.resend = its own protected invalidate()
    rs = [v for k2, v in methods(ct(new[PKG + "VWindow"])).items() if k2.startswith("resend(")]
    check(len(rs) == 1 and rs[0][0] == "aload_0" and "invalidate(()V)" in rs[0][1] and rs[0][2] == "return" and len(rs[0]) == 3,
          "B. VWindow.resend() = this.invalidate(): %s" % rs)
    # VDropSys: its shape
    ds = ct(new[PKG + "VDropSys"])
    check(str(ds.getClassFile().getSuperclass()) == "com.hypixel.hytale.component.system.EntityEventSystem", "B. VDropSys extends "
                                                                                                        "EntityEventSystem")
    check(fields(ds) == [], "B. VDropSys has no fields")
    dm = methods(ds)
    check(sorted(dm) == sorted(["<init>()V", "getQuery()Lcom/hypixel/hytale/component/query/Query;",
                                "shouldProcessEvent(Lcom/hypixel/hytale/component/system/EcsEvent;)Z",
                                "handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;"
                                "Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"]),
          "B. VDropSys methods: %s" % sorted(dm))
    init = dm.get("<init>()V", [])
    check(any("DropItemEvent$PlayerRequest" in t for t in init) and any("EntityEventSystem.<init>((Ljava/lang/Class;)V)" in t for t in init),
          "B. VDropSys() = super(DropItemEvent$PlayerRequest.class): %s" % init)
    spe = dm.get("shouldProcessEvent(Lcom/hypixel/hytale/component/system/EcsEvent;)Z", [])
    check(spe == ["iconst_1", "ireturn"], "B. VDropSys.shouldProcessEvent = true (also a request another system refused): %s" % spe)
    for m in ds.getDeclaredMethods():
        if str(m.getName()) == "shouldProcessEvent":
            check(Mod.isProtected(m.getModifiers()), "B. VDropSys.shouldProcessEvent stays protected (it overrides a protected method)")
    gq = dm.get("getQuery()Lcom/hypixel/hytale/component/query/Query;", [])
    check(any("Player.getComponentType" in t for t in gq), "B. VDropSys query = the Player component type: %s" % gq)
    hd = [t for k2, v in dm.items() if k2.startswith("handle(") for t in v]
    order = ["VSessions.SESSIONS", "isEmpty", "getInventorySectionId", "getReferenceTo", "PlayerRef.getComponentType",
             "Player.getComponentType", "VSessions.dropEvent"]
    pos, ok_order = -1, True
    for key in order:
        hits = [i for i, t in enumerate(hd) if key in t and i > pos]
        if not hits:
            ok_order = False
            break
        pos = hits[0]
    check(ok_order and any("try" in t and "java.lang.Throwable" in t for t in hd), "B. VDropSys.handle: fast exits (no vault open, "
                                                                                 "section <= 0) before it touches the chunk, then "
                                                                                 "the player, then VSessions.dropEvent, all in a try")
    # nothing in 0.1.5 ever un-cancels an event: every setCancelled call is fed a constant true
    n_set = 0
    for n, b in new.items():
        c = ct(b)
        for k2, v in methods(c).items():
            for i, t in enumerate(v):
                if "setCancelled((Z)V)" in t:
                    n_set += 1
                    check(i > 0 and v[i - 1] == "iconst_1", "B. %s.%s calls setCancelled with something else than true: %s" % (
                        n, k2, v[max(0, i - 3):i + 1]))
    check(n_set == 1, "B. exactly one setCancelled call (VSessions.dropEvent): %d" % n_set)
    # engine members referenced from a class that may not access them (the JVM throws IllegalAccessError at run time)
    OP = JClass("javassist.bytecode.Opcode")
    FOPS = (OP.GETFIELD, OP.PUTFIELD, OP.GETSTATIC, OP.PUTSTATIC)

    def access_problems(jar):
        pool = CP(True)
        pool.appendClassPath(B.SERVER_JAR)
        pool.appendClassPath(jar)
        bad, n_refs = [], 0
        for cn in sorted(classes(jar)):
            cc = pool.get(cn)
            for m in list(cc.getDeclaredMethods()) + list(cc.getDeclaredConstructors()):
                ca = m.getMethodInfo().getCodeAttribute()
                if ca is None:
                    continue
                cpool = m.getMethodInfo().getConstPool()
                it = ca.iterator()
                while it.hasNext():
                    p0 = it.next()
                    op = it.byteAt(p0)
                    if op not in FOPS and op not in (OP.INVOKEVIRTUAL, OP.INVOKESPECIAL, OP.INVOKESTATIC):
                        continue
                    ix = it.u16bitAt(p0 + 1)
                    if op in FOPS:
                        owner, name, desc = cpool.getFieldrefClassName(ix), cpool.getFieldrefName(ix), cpool.getFieldrefType(ix)
                    else:
                        owner, name, desc = cpool.getMethodrefClassName(ix), cpool.getMethodrefName(ix), cpool.getMethodrefType(ix)
                    if str(owner).startswith(("com.skyy.", "java.", "javax.")):
                        continue
                    n_refs += 1
                    try:
                        oc = pool.get(owner)
                        if op in FOPS:
                            mem, c2 = None, oc
                            while c2 is not None and mem is None:
                                try:
                                    mem = c2.getDeclaredField(name)
                                except Exception:
                                    c2 = c2.getSuperclass()
                        elif str(name) == "<init>":
                            mem = oc.getConstructor(desc)
                        else:
                            mem = oc.getMethod(name, desc)
                    except Exception:
                        continue
                    if mem is None:
                        continue
                    mods, decl = mem.getModifiers(), mem.getDeclaringClass()
                    same_pkg = str(decl.getPackageName()) == str(cc.getPackageName())
                    if Mod.isPrivate(mods) or (Mod.isPackage(mods) and not same_pkg) or (Mod.isProtected(mods) and not same_pkg
                                                                                       and not cc.subclassOf(decl)):
                        bad.append("%s.%s -> %s %s.%s%s" % (cn.rsplit(".", 1)[1], m.getName(), Mod.toString(mods),
                                                             decl.getName(), name, desc))
        return sorted(set(bad)), n_refs
    bad_old, n_old = access_problems(OLD)
    bad_new, n_new = access_problems(JAR)
    check(bad_old == ["VSessions.resync -> protected com.hypixel.hytale.server.core.entity.entities.player.windows.Window.invalidate()V"],
          "B. 0.1.4's one inaccessible engine call is VSessions.resync -> Window.invalidate(): %s" % bad_old)
    check(bad_new == [], "B. 0.1.5 references no engine member it may not access: %s" % bad_new)
    # the non-class entries
    eo, en = entries(OLD), entries(JAR)
    check(sorted(n for n in eo if not n.endswith(".class")) == sorted(n for n in en if not n.endswith(".class")),
          "B. the same non-class entries")
    diff_e = sorted(n for n in eo if not n.endswith(".class") and n in en and eo[n] != en[n])
    check(diff_e == ["Server/Languages/en-US/server.lang", "manifest.json"], "B. only server.lang + manifest.json differ: %s" % diff_e)
    lo = eo["Server/Languages/en-US/server.lang"].decode("utf8").splitlines()
    ln = en["Server/Languages/en-US/server.lang"].decode("utf8").splitlines()
    want_lang = {}
    for kind, txt in LANG_NEW:
        for pre in ("items.", "server.items."):
            want_lang[pre + "Skyy_Vault_%s.description" % kind] = txt
    ok_lang = len(lo) == len(ln)
    for a, b in zip(lo, ln):
        if a != b:
            key = b.split("=", 1)[0]
            ok_lang = ok_lang and a.split("=", 1)[0] == key and want_lang.get(key) == b.split("=", 1)[1]
            want_lang.pop(key, None)
    check(ok_lang and not want_lang, "B. server.lang: only the 3 arrow descriptions (x2 keys) changed, to the gesture texts (%s left)"
          % want_lang)
    mo_, mn_ = json.loads(eo["manifest.json"]), json.loads(en["manifest.json"])
    check(mn_.get("Version") == VERSION and mn_.get("Name") == "0.1.5 SkyyVault" and
          dict((k2, v) for k2, v in mo_.items() if k2 not in ("Version", "Name")) ==
          dict((k2, v) for k2, v in mn_.items() if k2 not in ("Version", "Name")), "B. manifest: only Name / Version")
    print("B. %d classes byte-identical, %s differ only by the version string; changed as pinned: %s; VDropSys shaped as planned; "
          "setCancelled only with true; inaccessible engine calls 0.1.4 %s -> 0.1.5 %s (%d / %d engine refs); server.lang 6 lines, "
          "manifest" % (n_same, sorted(ver_only), dict((s2, COUNT["B " + s2][1:]) for s2 in CODE), len(bad_old), len(bad_new), n_old,
                        n_new))

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

    # a vault state: dict(name, free, max, price, step, confirm, layout, arrows, unlocked (None = unreadable file), cap, items
    # {page: n}, sess (None | ("page" or "chest", page shown)), sel, purse (None = unreadable, "none" = no SkyyCoins))
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
        # 0.1.5: which help text each kind of page gets
        S("live-arrowsoff", arrows=False, sess=("page", 1)), S("pages-arrowsoff", arrows=False),
        S("inside-live", layout="inside", unlocked=3, sel=2, sess=("page", 2)),
    ]
    MARKS = ["", "+Bought vault page 3 for 50,000 coins - you now own 3 of 10 pages.",
             "-Vault page 5 is locked - you own 2 of 10 pages. Page 3 costs 50,000 coins - /vault buy",
             "=Page 4 is locked. Buy page 3 first.", "a line without a mark"]

    def layout_of(st):
        return 0 if not st["arrows"] else (2 if st["layout"] == "inside" else 1)

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
            sess.layout = layout_of(st)          # 0.1.5: the page's help text follows the window's arrow layout
        return vd, sess

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    def is_help(sel):
        return bool(sel) and re.match(r"#SkyyVHelp\d\.Text\Z", sel) is not None

    def sets_of(cmds, mask=False):
        return sorted((sel, data or "") for typ, sel, text, data in cmds if "append" not in typ.lower() and not (mask and is_help(sel)))

    def sets_seq(cmds, mask=False):
        """the b.set lines IN ORDER (sets_of sorts them)"""
        return [(sel, data or "") for typ, sel, text, data in cmds if "append" not in typ.lower() and not (mask and is_help(sel))]

    def order_problems(cmds):
        """every command on #Id.<prop> comes after the append that creates #Id (command index order)"""
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

    def help_of(cmds):
        return [set_text(cmds, "SkyyVHelp%d" % i) for i in range(3)]

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
    DPATS = []
    for ai, (parent, mk) in enumerate(K["VDLG_SH"].appends):
        for vi, v in enumerate(variants(mk)):
            rx, sl = pattern(v)
            look = ("dlg%d:%s" % (ai, ("on", "off")[vi])) if isinstance(mk, SUI.Choice) else "dlg%d" % ai
            DPATS.append((parent, rx, sl, "dlg", look))
    ALLOWED = set(SUI.allowed_colors())
    COL = SUI.COLOR
    SH = K["VAULT_SH"]
    W, BW = SH.inner_w, K["VAULT_BOX_W"]
    RT_IDS = ("SkyyVOpen", "SkyyVBuy")

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
                elif extra_slots is not None:
                    extra_slots.setdefault(expr, []).append(val)
        return used

    LOOK_FAMS = {"num": ("numsel", "numon", "numoff"), "SkyyVOpen": ("openon", "openoff"), "SkyyVBuy": ("buyon", "buyoff"),
                 "SkyyVPrev": ("nav:on", "nav:off"), "SkyyVNext": ("nav:on", "nav:off")}

    def check_looks(tag, used, ex):
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
            if check(got == [want], "C. %s: #%s has the look %s, want %s" % (tag, ident, got, want)):
                tally("C looks")
        check(seen == {"SkyyVNum", "SkyyVOpen", "SkyyVBuy", "SkyyVPrev", "SkyyVNext"}, "C. %s: stateful buttons seen: %s" % (tag, sorted(seen)))

    def check_new_vault(tag, st, info, cmds, ex=None):
        """the 0.1.5 VaultPage is still the kit's markup (the 0.1.4 harness's checks)"""
        aps = appends_of(cmds)
        used = match_kit(tag, aps, PATS, info, {})
        if ex is not None:
            check_looks(tag, used, ex)
        check_order("C/E. " + tag, cmds)
        for parent, text in aps:
            tb = re.match(r'\s*TextButton #([A-Za-z0-9]+) ', text)
            rtb = tb and (tb.group(1) in RT_IDS or re.fullmatch(r"SkyyVNum\d+", tb.group(1)))
            probe = re.sub(r'Text: "(?:[^"\\]|\\.)*";', 'Text: "7";', text, count=1) if rtb else text
            try:
                SUI.check_markup(probe, prefix="SkyyV", root=(parent is None))
                tally("C markups")
            except ValueError as e:
                check(False, "C. %s: check_markup: %s" % (tag, e))
        try:
            left = SUI.fit([SUI.used_height(aps, "SkyyVault")], SH.inner_h)
            check(left == 0, "C. %s: the body is filled exactly (%d px left)" % (tag, left))
        except ValueError as e:
            check(False, "C. %s: body budget: %s" % (tag, e))
        return aps

    # ---------------- C. differential VaultPage builds
    SEEN = {}
    n_builds = 0
    for st in STATES:
        for info in MARKS:
            res, pages, lives = {}, {}, {}
            for k in ("old", "new"):
                vd, sess = setup(k, st)
                pg = jc(k, "VaultPage")(pref(UID), sess, st["sel"])
                pg.info = info
                res[k] = build(pg)
                pages[k] = (int(pg.sel), int(pg.offer))
                lives[k] = sess is not None
                n_builds += 1
            ex = None if st["unlocked"] is None else dict(sel=pages["new"][0], offer=pages["new"][1], unlocked=st["unlocked"],
                                                          maxp=st["max"])
            tag = "%s / %r" % (st["name"], info[:14])
            (co, eo), (cn, en) = res["old"], res["new"]
            check(appends_of(co) == appends_of(cn), "C. %s: an appended markup differs from 0.1.4's" % tag)
            check(sets_of(co, True) == sets_of(cn, True), "C. %s: b.set lines (help aside) differ:\n  0.1.4 %s\n  0.1.5 %s" % (
                tag, sets_of(co, True), sets_of(cn, True)))
            check(sets_seq(co, True) == sets_seq(cn, True), "C. %s: the b.set lines come in another order than 0.1.4's" % tag)
            check(sets_seq(co) != sets_seq(cn) or st["unlocked"] is None or want_help("new", lives["new"], layout_of(st), st["arrows"])
                  == want_help("old", lives["old"], layout_of(st), st["arrows"]), "C. %s: help differs where planned" % tag)
            check(eo == en, "C. %s: event bindings differ" % tag)
            check(pages["old"] == pages["new"], "C. %s: sel / offer after the build: %s / %s" % (tag, pages["old"], pages["new"]))
            if st["unlocked"] is not None:
                for k2, cmds in (("old", co), ("new", cn)):
                    want = want_help(k2, lives[k2], layout_of(st), st["arrows"])
                    if check(help_of(cmds) == want, "C. %s: %s help lines %s, want %s" % (tag, k2, help_of(cmds), want)):
                        tally("C help %s %s" % (k2, [n for n, v in HELP.items() if v == want][0]))
            else:
                check(help_of(cn) == [None, None, None] and help_of(co) == [None, None, None], "C. %s: no help lines" % tag)
            check_new_vault(tag, st, info, cn, ex)
            tally("C bindings", len(en))
            for typ, sel, text, data in cn:
                if sel and sel.endswith(".Text"):
                    SEEN.setdefault(sel[1:-5], set()).add(set_text(cn, sel[1:-5]))
            for i, t in btn_texts(appends_of(cn)).items():
                SEEN.setdefault("btn:" + re.sub(r"\d+$", "", i) if i.startswith("SkyyVNum") else "btn:" + i, set()).add(t)
    COUNT["C builds"] = n_builds
    print("C. %d VaultPage builds (%d states x %d result lines x 2 jars): every appended markup identical to 0.1.4's, %d bindings "
          "identical, b.set lines identical in order but the help lines; help texts %s; %d markups still the kit's" % (
              n_builds, len(STATES), len(MARKS), COUNT.get("C bindings", 0),
              dict((k2[7:], v) for k2, v in COUNT.items() if k2.startswith("C help ")), COUNT.get("C markups", 0)))

    # ---------------- D. the confirm window: identical (VBuyDlg is byte-identical to 0.1.4)
    check(old[PKG + "VBuyDlg"] == new[PKG + "VBuyDlg"], "D. VBuyDlg is byte-identical to 0.1.4")
    DSTATES = [("buy-rich", 3, 50000, 1000000, "ok"), ("buy-poor", 3, 50000, 1200, "ok"), ("buy-unread", 4, 75000, None, "ok"),
               ("buy-nocoins", 3, 50000, "none", "ok"), ("unlock-free", 3, 0, 500, "ok"), ("no-vault-file", 3, 50000, 1000, "bad")]
    n_dlg = 0
    for name, page_no, cost, purse, vault in DSTATES:
        res = {}
        for k in ("old", "new"):
            st = S("dlg-" + name, purse=purse, unlocked=None if vault == "bad" else 2)
            setup(k, st)
            dg = jc(k, "VBuyDlg")(pref(UID), page_no, cost, 1, 1)
            res[k] = build(dg)
            n_dlg += 1
        check(res["old"] == res["new"], "D. %s: the confirm window differs from 0.1.4's" % name)
        match_kit("dlg " + name, appends_of(res["new"][0]), DPATS, None, {})
        for typ, sel, text, data in res["new"][0]:
            if sel and sel.endswith(".Text"):
                SEEN.setdefault(sel[1:-5], set()).add(set_text(res["new"][0], sel[1:-5]))
    print("D. %d confirm window builds (%d states x 2 jars): identical commands and bindings, every markup the kit's" % (n_dlg, len(DSTATES)))

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
               S("click-poor", price=10000, step=5000, confirm=50000, purse=500),
               S("click-live-off", sess=("page", 1), arrows=False)]
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
                d = jc(k, "VStore").CACHE.get(UID)
                cmds, evs = build(pg)
                live = pg.sess is not None and not pg.sess.closed
                if d is not None:
                    want = want_help(k, live, layout_of(st) if live else 0, st["arrows"])
                    if check(help_of(cmds) == want, "E. %s %s after %r: help %s, want %s" % (st["name"], k, a, help_of(cmds), want)):
                        tally("E help")
                steps.append((a, str(pg.info), int(pg.sel), int(pg.offer), PURSE.get(US, "none") if st["purse"] != "none" else "none",
                              None if d is None else int(d.unlocked), vault_file(k, st, "-e"), log_lines(k, st, "-e"),
                              sets_of(cmds, True), evs, [t for _p, t in appends_of(cmds)]))
                if k == "new":
                    ex = None if d is None else dict(sel=int(pg.sel), offer=int(pg.offer), unlocked=int(d.unlocked), maxp=st["max"])
                    check_new_vault("E. %s after %r" % (st["name"], a), st, str(pg.info), cmds, ex)
                    for typ, sel, text, data2 in cmds:
                        if sel and sel.endswith(".Text"):
                            SEEN.setdefault(sel[1:-5], set()).add(set_text(cmds, sel[1:-5]))
            trace[k] = steps
        for so, sn in zip(trace["old"], trace["new"]):
            check(so == sn, "E. %s: after %r:\n  0.1.4 %s\n  0.1.5 %s" % (st["name"], so[0], so[1:8], sn[1:8]))
        tally("E buys", len([s for s in trace["new"] if s[1].startswith("+Bought")]))
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
        check(trace["old"] == trace["new"], "E. confirm window %s: 0.1.4 %s | 0.1.5 %s" % (name, trace["old"], trace["new"]))
        if trace["new"] and any(x.startswith("BUY ") for x in trace["new"][-1][5]):
            tally("E window buys")
    COUNT["E clicks"] = n_clicks
    print("E. %d clicks (%d page states x %d clicks + %d window sequences, both jars): identical result, selection, offer, purse, "
          "pages, vault file, log and markup; help lines right after every click (%d); %d page purchases, %d from the window" % (
              n_clicks, len(ESTATES), len(CLICKS), len(DCLICKS), COUNT.get("E help", 0), COUNT.get("E buys", 0),
              COUNT.get("E window buys", 0)))

    # ---------------- F. text fit (the client's font tables through the kit; read-only)
    if SUI.font_table("Default", False) is None:
        print("F. skipped: no client font tables")
    else:
        n_fit = 0
        widest = {}
        one = {"SkyyVSub": (16, False, W), "SkyyVUsed": (16, True, BW), "SkyyVPageLbl": (16, True, K["VAULT_CAPTION_W"]),
               "SkyyVHelp0": (16, False, W), "SkyyVHelp1": (16, False, W), "SkyyVHelp2": (16, False, W)}
        for ident, (size, bold, width) in one.items():
            for t in SEEN.get(ident, ()):
                if not t:
                    continue
                n_fit += 1
                tw = SUI.text_width(t, size, bold)
                widest[ident] = max(widest.get(ident, (0, ""))[0], tw), width
                check(tw <= width, "F. #%s one line %r: %.0f px > %d px" % (ident, t, tw, width))
        for t in HELP["new-live"] + HELP["new-pages"]:
            check(t in SEEN.get("SkyyVHelp0", set()) | SEEN.get("SkyyVHelp1", set()) | SEEN.get("SkyyVHelp2", set()),
                  "F. the help line %r was measured" % t)
        wrap = {"SkyyVInfo": (16, True, W, 2), "SkyyVErr": (16, True, W - 2 * SUI.WELL_PAD, 3)}
        for ident, (size, bold, width, mx) in wrap.items():
            for t in SEEN.get(ident, ()):
                if not t:
                    continue
                n_fit += 1
                nl = SUI.text_lines(t, width, size, bold)
                check(nl <= mx, "F. #%s wraps to %d lines (at most %d): %r" % (ident, nl, mx, t))
        for key, size, width, pad in (("btn:SkyyVBuy", 17, K["VAULT_BUY_W"], SUI.BTN_PAD), ("btn:SkyyVOpen", 17, K["VAULT_OPEN_W"], SUI.BTN_PAD),
                                      ("btn:SkyyVNum", 17, K["VAULT_NUM_W"], SUI.BTN_PAD)):
            for t in SEEN.get(key, ()):
                n_fit += 1
                tw = SUI.text_width(t, size, True, upper=True)
                check(tw <= width - 2 * pad, "F. %s label %r: %.0f px, %d px of room" % (key[4:], t, tw, width - 2 * pad))
        COUNT["F texts"] = n_fit
        print("F. text fit: %d texts / labels measured; widest help lines %s" % (
            n_fit, dict((k2, "%.0f/%d" % v) for k2, v in sorted(widest.items()) if k2.startswith("SkyyVHelp"))))

    # ---------------- G. the page id
    pid, chk = K["VAULT_PAGE_ID"], K["VAULT_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready log line names the pages the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW))
    check(pid == chk, "G. the pages the kit makes now (%s) are the checked pages VAULT_PAGE_CHECKED (%s): if everything else passed, "
                      "set VAULT_PAGE_CHECKED = %r in SkyyVault/build_skyyvault_0.1.5.py and rebuild" % (pid, chk, pid))
    print("G. page id %s, checked %s, kit %s" % (pid, chk, SUI.kit_id()))
    # H. the build-time proofs again on the current kit
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

    trigger_section(locals())
    live_section(locals())


# ------------------------------------------------------------------------------------------------ I. the triggers, end to end
def trigger_section(E):
    from jpype import JClass, JShort, JInt
    import skyybuild as B
    U, jc, BR, PURSE, COINS, UID, US = E["U"], E["jc"], E["BR"], E["PURSE"], E["COINS"], E["UID"], E["US"]
    Paths, Long, UUID, ISC = E["Paths"], E["Long"], E["UUID"], E["ISC"]

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

    def setf(obj, name, val):
        jf(obj.getClass(), name).set(obj, val)

    def sets(jcls, name, val):
        jf(jcls.class_, name).set(None, val)

    CtPool = JClass("javassist.ClassPool")(True)
    CtPool.appendClassPath(B.SERVER_JAR)
    CtNM, CtNC, CtF = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def fake(name, sup, ctor, fields, methods, neighbor):
        """a stand-in subclass of an engine class, defined next to it; never constructed (Unsafe.allocateInstance)"""
        c = CtPool.makeClass(name, CtPool.get(sup))
        for f in fields:
            c.addField(CtF.make(f, c))
        c.addConstructor(CtNC.make(ctor, c))
        for m in methods:
            c.addMethod(CtNM.make(m, c))
        return c.toClass(neighbor)

    # the item asset store: an empty map (Item.UNKNOWN for every id) so ItemStack constructors run (the SkyyGear harness pattern)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    FS = fake("com.hypixel.hytale.assetstore.SkyyVaultTestAssets", "com.hypixel.hytale.assetstore.AssetStore",
              "public SkyyVaultTestAssets() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", [], [], AS.class_)
    st0 = U.allocateInstance(FS)
    jf(AS.class_, "assetMap").set(st0, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    sets(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item"), "ASSET_STORE", st0)
    RF, SF_, CMP, CTY = ("com.hypixel.hytale.component.Ref", "com.hypixel.hytale.component.Store", "com.hypixel.hytale.component.Component",
                         "com.hypixel.hytale.component.ComponentType")
    StoreC = JClass(SF_)
    TS = fake("com.hypixel.hytale.component.SkyyVaultTestStore", SF_,
              "public SkyyVaultTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
              "(com.hypixel.hytale.component.IResourceStorage) null); }",
              ["public static java.util.IdentityHashMap M = new java.util.IdentityHashMap();"],
              ["public %s getComponent(%s r, %s t) { java.util.Map m = (java.util.Map) M.get(r); if (m == null) return null; "
               "return (%s) m.get(t); }" % (CMP, RF, CTY, CMP)], StoreC.class_)
    ACh = JClass("com.hypixel.hytale.component.ArchetypeChunk")
    TC = fake("com.hypixel.hytale.component.SkyyVaultTestChunk", "com.hypixel.hytale.component.ArchetypeChunk",
              "public SkyyVaultTestChunk() { super((%s) null, (com.hypixel.hytale.component.Archetype) null); }" % SF_,
              ["public static %s R = null;" % RF], ["public %s getReferenceTo(int i) { return R; }" % RF], ACh.class_)
    PHc = JClass("com.hypixel.hytale.server.core.io.PacketHandler")
    TPH = fake("com.hypixel.hytale.server.core.io.SkyyVaultTestPH", "com.hypixel.hytale.server.core.io.PacketHandler",
               "public SkyyVaultTestPH() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, "
               "(com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
               ["public static java.util.ArrayList OUT = new java.util.ArrayList();"],
               ["public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }"], PHc.class_)
    P_ = "com.hypixel.hytale.server.core.entity.entities.player."
    WIN_A = P_ + "windows.Window[]"
    TPM = fake(P_ + "pages.SkyyVaultTestPM", P_ + "pages.PageManager", "public SkyyVaultTestPM() { super(); }",
               ["public static Object CUR = null;", "public static java.util.ArrayList OPENED = new java.util.ArrayList();"],
               ["public boolean setPageWithWindows(%s r, %s s, com.hypixel.hytale.protocol.packets.interface_.Page pg, boolean b, %s w) { "
                "CUR = null; for (int i = 0; i < w.length; i++) OPENED.add(w[i]); return true; }" % (RF, SF_, WIN_A),
                "public boolean openCustomPageWithWindows(%s r, %s s, %spages.CustomUIPage p, %s w) { CUR = p; "
                "for (int i = 0; i < w.length; i++) OPENED.add(w[i]); return true; }" % (RF, SF_, P_, WIN_A),
                "public void openCustomPage(%s r, %s s, %spages.CustomUIPage p) { CUR = p; }" % (RF, SF_, P_),
                "public %spages.CustomUIPage getCustomPage() { return (%spages.CustomUIPage) CUR; }" % (P_, P_)],
               JClass(P_ + "pages.PageManager").class_)
    TSc, TCc = JClass("com.hypixel.hytale.component.SkyyVaultTestStore"), JClass("com.hypixel.hytale.component.SkyyVaultTestChunk")
    OUT = JClass("com.hypixel.hytale.server.core.io.SkyyVaultTestPH").OUT
    PMS = JClass(P_ + "pages.SkyyVaultTestPM")
    # the universe (one world whose execute() queues the task), the entity module, the component types
    CT = JClass(CTY)
    CT_PR, CT_PLA = CT(), CT()
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(Uni.class_)
    WU = UUID.fromString("00000000-0000-0000-0000-0000000000d1")
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    world = U.allocateInstance(World.class_)
    setf(world, "acceptingTasks", JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    Q = JClass("java.util.concurrent.LinkedBlockingDeque")()
    setf(world, "taskQueue", Q)
    setf(world, "name", "vaulttest")
    wmap = JClass("java.util.HashMap")()
    wmap.put(WU, world)
    setf(uni, "worldsByUuid", wmap)
    setf(uni, "playerRefComponentType", CT_PR)
    sets(Uni, "instance", uni)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    setf(em, "playerComponentType", CT_PLA)
    sets(EM, "instance", em)
    STORE = U.allocateInstance(TS)
    CHUNK = U.allocateInstance(TC)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Pla = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    WMc = JClass(P_ + "windows.WindowManager")
    WinC = JClass(P_ + "windows.Window")
    IdM = JClass("java.util.IdentityHashMap")

    def mkplayer(u, name):
        ref = U.allocateInstance(JClass(RF).class_)
        setf(ref, "store", STORE)
        pr = U.allocateInstance(PRc.class_)
        setf(pr, "uuid", u)
        setf(pr, "worldUuid", WU)
        setf(pr, "entity", ref)
        setf(pr, "username", name)
        setf(pr, "packetHandler", U.allocateInstance(TPH))
        p = U.allocateInstance(Pla.class_)
        setf(p, "pageManager", U.allocateInstance(TPM))
        comp = IdM()
        comp.put(CT_PR, pr)
        comp.put(CT_PLA, p)
        TSc.M.put(ref, comp)
        return pr, p, ref

    PRX, PX, REFX = mkplayer(UID, "Tester")
    U2 = UUID.fromString("00000000-0000-0000-0000-0000000000c2")
    PR2, P2, REF2 = mkplayer(U2, "Other")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    DIRQ = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
    DSYS = jc("new", "VDropSys")()
    WID = 7

    def chat():
        out = []
        for pk in OUT:
            if str(pk.getClass().getSimpleName()) == "ServerMessage":
                out.append(str(pk.message.rawText))
        return out

    def fresh_wm(p):
        wm = WMc()
        jf(WMc.class_, "windowId").get(wm).set(100)
        setf(p, "windowManager", wm)
        return wm

    def tsetup(k, name, layout="row", mode=2, unlocked=3, page=2, price=50000, confirm=50000, purse=1000000, arrows=True, full=False,
               busy=False, switched=False, extra=None, stock=4):
        Cfg, Store, VS, Dat = jc(k, "VCfg"), jc(k, "VStore"), jc(k, "VSessions"), jc(k, "VData")
        d = os.path.join(WORK, "trig", k, name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.join(d, "vaults"))
        Cfg.DIR = Paths.get(d)
        Cfg.VDIR = Paths.get(d).resolve("vaults")
        Cfg.FILE = Paths.get(d).resolve("config.properties")
        Cfg.LOGF = Paths.get(d).resolve("vault.log")
        Cfg.NAMESF = Paths.get(d).resolve("names.properties")
        Cfg.FREE_PAGES, Cfg.MAX_PAGES, Cfg.SLOTS = 2, 10, 36
        Cfg.PRICE, Cfg.STEP, Cfg.BUY_CONFIRM = price, 25000, confirm
        Cfg.ARROWS, Cfg.ARROW_LAYOUT = arrows, layout
        Cfg.PAGE_MODE, Cfg.OPEN_MODE = mode == 1, ("page" if mode == 1 else "chest")
        Cfg.AFTER_SWITCH_MS, Cfg.BUY_GUARD_MS, Cfg.SAVE_DELAY_MS = 30000, 1500, 1000
        Cfg.WARNED.clear()
        for m in ("CACHE", "PENDING", "BUYING", "LASTBUY", "NAMES"):
            getattr(Store, m).clear()
        Store.SAVER = None
        Store.STOPPING = False
        for m in ("SESSIONS", "LAST", "EPOCHS", "SWITCHED", "BUSYSEEN", "ONLINE"):
            getattr(VS, m).clear()
        BR.clear()
        PURSE.clear()
        BR.put("coins:fn:get", COINS[0])
        BR.put("coins:fn:add", COINS[1])
        BR.put("coins:fn:take", COINS[2])
        PURSE[US] = purse
        vd = Dat(UID, 36)
        vd.unlocked = unlocked
        vd.page(unlocked)
        for pg in range(1, unlocked + 1):
            arr = vd.page(pg)
            for i in range(36 if full else stock):
                arr[i] = ISC("Test_P%d_S%d" % (pg, i), 1 + i % 5)
        if extra:
            for (pg, i), (iid, q) in extra.items():
                vd.page(pg)[i] = ISC(iid, q)
        Store.CACHE.put(UID, vd)
        Q.clear()
        OUT.clear()
        PMS.CUR = None
        PMS.OPENED.clear()
        wm = fresh_wm(PX)
        wm2 = fresh_wm(P2)
        TCc.R = REFX
        line = VS.open2(PRX, REFX, STORE, page, mode, None)
        s = VS.current(UID)
        win = PMS.OPENED.get(0) if PMS.OPENED.size() > 0 else None
        if win is not None:
            wm.setWindow(WID, win)                 # the engine's own registration: id, init, the container change listener
            jf(WinC.class_, "isDirty").get(win).set(False)     # the engine's first window send consumed it
        box = SIC(JShort(36))
        box.setItemStackForSlot(JShort(0), ISC("Test_Inv_0", 2), False)
        box.setItemStackForSlot(JShort(1), ISC("Test_Inv_1", 1), False)
        hot = SIC(JShort(9))
        if busy:
            BR.put("profile:busy:" + US, Boolean.TRUE)
        if switched:
            VS.SWITCHED.put(UID, Long.valueOf(int(time.time() * 1000)))
        n_open_tasks = drain()                     # the close sweep of nothing, etc.
        OUT.clear()
        return dict(k=k, VS=VS, Store=Store, Btn=jc(k, "VBtn"), Cfg=Cfg, s=s, win=win, wm=wm, wm2=wm2, box=box, hot=hot, thrown=collections.Counter(),
                    warn=[], line=None if line is None else str(line), tasks=0, open_tasks=n_open_tasks, dir=d)

    Boolean = JClass("java.lang.Boolean")

    def drain():
        n = 0
        while Q.size() > 0 and n < 60:
            t = Q.poll()
            t.run()
            n += 1
        return n

    def ctrl_idx(s):
        return [i for i in range(s.base, s.base + s.span) if s.ctrlLive(i)]

    def counts(ctx):
        """real items per id (every vault page in VData + inventory + thrown) and vault arrow items outside the control row"""
        s, VS, Btn = ctx["s"], ctx["VS"], ctx["Btn"]
        if s is not None and not s.closed:
            VS.syncView(s)
        d = ctx["Store"].CACHE.get(UID)
        real = collections.Counter()
        stray = 0
        for pg in range(1, int(d.unlocked) + 1):
            for x in d.pageCopy(pg):
                if x is None or x.isEmpty():
                    continue
                if Btn.isButton(x):
                    stray += 1
                else:
                    real[str(x.getItemId())] += int(x.getQuantity())
        for c in (ctx["box"], ctx["hot"]):
            for i in range(int(c.getCapacity())):
                x = c.getItemStack(JShort(i))
                if x is None or x.isEmpty():
                    continue
                if Btn.isButton(x):
                    stray += 1
                else:
                    real[str(x.getItemId())] += int(x.getQuantity())
        for iid, q in ctx["thrown"].items():
            if iid.startswith("Skyy_Vault_"):
                stray += q
            else:
                real[iid] += q
        if s is not None:
            for i in range(int(s.view.getCapacity())):
                if s.isStorage(i) and Btn.isButton(s.view.getItemStack(JShort(i))):
                    stray += 1
        return real, stray

    def row_ok(ctx):
        """every live control slot of the session holds its canonical button (item, quantity, kind, window serial)"""
        s, Btn = ctx["s"], ctx["Btn"]
        if s is None or s.layout == 0:
            return True
        c = s.ctrl
        return all(Btn.same(s.view.getItemStack(JShort(i)), c[i - s.base]) for i in ctrl_idx(s))

    def row_kinds(ctx):
        s, Btn = ctx["s"], ctx["Btn"]
        if s is None or s.layout == 0:
            return []
        return [int(Btn.kindOf(s.view.getItemStack(JShort(i)))) for i in ctrl_idx(s)]

    def tips(ctx):
        """the canonical control row's per-stack tooltip JSON (ItemDisplayMetadata inside the item metadata)"""
        s = ctx["s"]
        if s is None or s.layout == 0:
            return {}
        out = {}
        for i in ctrl_idx(s):
            x = s.ctrl[i - s.base]
            out[i] = "" if x is None or x.getMetadata() is None else str(x.getMetadata().toJson())
        return out

    def section_of(ctx, sec, other=False):
        if other:
            w = ctx["wm2"].getWindow(JInt(sec)) if sec > 0 else None      # the other player has no vault window open
            return None if w is None else w.getItemContainer()
        if sec == -2:
            return ctx["box"]
        if sec == -1:
            return ctx["hot"]
        if sec > 0:
            w = ctx["wm"].getWindow(JInt(sec))
            return None if w is None else w.getItemContainer()
        return None

    def engine_drop(ctx, sec, slot, qty, pre=False, who=None):
        """InventoryPacketHandler.lambda$handle$4 (DropItemStack) offsets 46-255: the request event (pre = the game mode prevents drops,
        or another system refused), Store.invoke -> every EntityEventSystem.handleInternal (0.1.5: VDropSys), then - not cancelled -
        the section by id, removeItemStackFromSlot(slot, qty) and the throw"""
        e = DIRQ(JInt(sec), JShort(slot))
        e.setCancelled(pre)
        TCc.R = REFX if who is None else who
        if ctx["k"] == "new":
            DSYS.handleInternal(0, CHUNK, STORE, None, e)
        TCc.R = REFX
        ctx["cancelled"] = bool(e.isCancelled())
        if e.isCancelled():
            return
        c = section_of(ctx, sec, who is not None)
        if c is None:
            ctx["warn"].append("invalid section")
            return
        tx = c.removeItemStackFromSlot(JShort(slot), JInt(qty))
        o = tx.getOutput()
        if o is None or o.isEmpty():
            ctx["warn"].append("empty")
            return
        ctx["thrown"][str(o.getItemId())] += int(o.getQuantity())

    def mv(c1, a, q, c2, b):
        """MoveItemStack (a click / drag that puts the item down): InventoryUtils.moveItem -> moveItemStackFromSlotToSlot"""
        return bool(c1.moveItemStackFromSlotToSlot(JShort(a), JInt(q), c2, JShort(b)).succeeded())

    def smart(c1, a, q, c2):
        """SmartMoveItemStack (shift-click / Transfer) from a window slot: InventoryUtils.smartMoveItem -> moveItemStackFromSlot"""
        return bool(c1.moveItemStackFromSlot(JShort(a), JInt(q), c2).succeeded())

    def take_all(ctx):
        v = ctx["s"].view
        for i in range(int(v.getCapacity())):
            x = v.getItemStack(JShort(i))
            if x is not None and not x.isEmpty():
                smart(v, i, int(x.getQuantity()), ctx["box"])

    def twice_buy(ctx):
        smart(ctx["s"].view, 44, 1, ctx["box"])
        ctx["tasks"] += drain()
        ctx["mid"] = (int(ctx["s"].page), int(ctx["Store"].CACHE.get(UID).unlocked), PURSE.get(US))
        smart(ctx["s"].view, 44, 1, ctx["box"])

    def retire_then_drop(ctx):
        ctx["VS"].retire(ctx["s"])
        ctx["tasks"] += drain()
        engine_drop(ctx, WID, 44, 1)

    V = lambda ctx: ctx["s"].view
    NEXT3 = ["[Vault] Vault page 3 of 3."]
    PAGE1 = ["[Vault] Vault page 1 of 3."]
    # (name, scene, action, expectations on the observation for 0.1.5; "old": the ones that differ on 0.1.4)
    G = [
        ("lift the arrow (plain click): no packet exists", {}, lambda c: None, dict(page=2, chat=[], tasks=0)),
        ("put it back on its own slot", {}, lambda c: c.__setitem__("ok", mv(V(c), 44, 1, V(c), 44)), dict(page=3, chat=NEXT3, ok=False)),
        ("put it down on an empty vault slot", {}, lambda c: c.__setitem__("ok", mv(V(c), 44, 1, V(c), 30)), dict(page=3, chat=NEXT3, ok=False)),
        ("put it down on a stored stack", {}, lambda c: c.__setitem__("ok", mv(V(c), 44, 1, V(c), 0)), dict(page=3, chat=NEXT3, ok=False)),
        ("put it down in the inventory", {}, lambda c: c.__setitem__("ok", mv(V(c), 44, 1, c["box"], 20)), dict(page=3, chat=NEXT3, ok=False)),
        ("shift-click Next", {}, lambda c: c.__setitem__("ok", smart(V(c), 44, 1, c["box"])), dict(page=3, chat=NEXT3, ok=False)),
        ("Drop key on Next (or click outside the window)", {}, lambda c: engine_drop(c, WID, 44, 1),
         dict(page=3, chat=NEXT3, cancelled=True, warn=[]), dict(cancelled=False, warn=["empty"])),
        ("Drop key on Next while drops are refused (game mode / another mod)", {}, lambda c: engine_drop(c, WID, 44, 1, pre=True),
         dict(page=3, chat=NEXT3, cancelled=True, warn=[]), dict(page=2, chat=[], cancelled=True, warn=[], tasks=0,
                                                                 kinds=[1, 7, 7, 7, 6, 7, 7, 7, 3])),
        ("shift-click Prev", {}, lambda c: smart(V(c), 36, 1, c["box"]), dict(page=1, chat=PAGE1)),
        ("Drop key on Prev", {}, lambda c: engine_drop(c, WID, 36, 1), dict(page=1, chat=PAGE1, cancelled=True, warn=[]),
         dict(cancelled=False, warn=["empty"])),
        ("shift-click the info item", {}, lambda c: smart(V(c), 40, 1, c["box"]),
         dict(page=2, chat=["[Vault] Vault page 2 of 3 - 4 of 36 slots used. /vault <page> jumps to a page."])),
        ("shift-click a filler", {}, lambda c: smart(V(c), 37, 1, c["box"]), dict(page=2, chat=[])),
        ("Drop key on a filler", {}, lambda c: engine_drop(c, WID, 41, 1), dict(page=2, chat=[], cancelled=True, warn=[]),
         dict(cancelled=False, warn=["empty"])),
        ("Take All (every slot, arrows too)", {}, take_all, dict(page=2, chat=[], vault_p2=0)),
        ("Take All on an empty page (only the arrow row answers - nothing changes)", dict(stock=0), take_all,
         dict(page=2, chat=[], vault_p2=0)),
        ("storage: shift-click a stack out", {}, lambda c: c.__setitem__("ok", smart(V(c), 1, 2, c["box"])), dict(page=2, tasks=0, ok=True)),
        ("storage: move a stack inside the vault", {}, lambda c: c.__setitem__("ok", mv(V(c), 1, 2, V(c), 20)), dict(page=2, tasks=0, ok=True)),
        ("storage: inventory -> vault", {}, lambda c: c.__setitem__("ok", mv(c["box"], 0, 2, V(c), 25)), dict(page=2, tasks=0, ok=True)),
        ("inventory stack onto the Next arrow", {}, lambda c: c.__setitem__("ok", mv(c["box"], 0, 2, V(c), 44)), dict(page=2, tasks=0, ok=False)),
        ("vault stack onto the Next arrow", {}, lambda c: c.__setitem__("ok", mv(V(c), 2, 3, V(c), 44)), dict(page=2, tasks=0, ok=False)),
        ("Drop key on a stored stack (a normal drop)", {}, lambda c: engine_drop(c, WID, 3, 4),
         dict(page=2, tasks=0, cancelled=False, warn=[], thrown={"Test_P2_S3": 4})),
        ("Drop key in another window", {}, lambda c: engine_drop(c, WID + 1, 44, 1), dict(page=2, tasks=0, cancelled=False, warn=["invalid section"])),
        ("Drop key in the own inventory", {}, lambda c: engine_drop(c, -2, 0, 2), dict(page=2, tasks=0, cancelled=False, warn=[], thrown={"Test_Inv_0": 2})),
        ("another player's Drop key on window 7 of their own", {}, lambda c: engine_drop(c, WID, 44, 1, who=REF2),
         dict(page=2, tasks=0, cancelled=False, warn=["invalid section"])),
        ("Drop key on the arrow after the vault closed", {}, retire_then_drop, dict(cancelled=False, warn=["empty"], closed=True)),
        ("gold Buy arrow (cheap page): shift-click, then again at once", dict(page=2, unlocked=2, price=10000), twice_buy,
         dict(page=3, unlocked=3, coins=990000, mid=(3, 3, 990000))),
        ("gold Buy arrow (cheap page): Drop key", dict(page=2, unlocked=2, price=10000), lambda c: engine_drop(c, WID, 44, 1),
         dict(page=3, unlocked=3, coins=990000, cancelled=True, warn=[]), dict(cancelled=False, warn=["empty"])),
        ("gold Buy arrow at buyConfirmCoins: shift-click opens the window", dict(page=2, unlocked=2), lambda c: smart(V(c), 44, 1, c["box"]),
         dict(unlocked=2, coins=1000000, cur="VBuyDlg", closed=True)),
        ("page mode: shift-click Next", dict(mode=1), lambda c: smart(V(c), 44, 1, c["box"]), dict(page=3, chat=NEXT3, cur="VaultPage")),
        ("page mode: Drop key on Next", dict(mode=1), lambda c: engine_drop(c, WID, 44, 1), dict(page=3, chat=NEXT3, cancelled=True, warn=[]),
         dict(cancelled=False, warn=["empty"])),
        ("arrowLayout inside: Drop key on Next (slot 35)", dict(layout="inside"), lambda c: engine_drop(c, WID, 35, 1),
         dict(page=3, chat=NEXT3, cancelled=True, warn=[]), dict(cancelled=False, warn=["empty"])),
        ("arrowLayout inside: shift-click Prev (slot 27)", dict(layout="inside"), lambda c: smart(V(c), 27, 1, c["box"]), dict(page=1, chat=PAGE1)),
        ("arrowLayout inside: Drop key on a stored stack (slot 26)", dict(layout="inside", extra={(2, 26): ("Test_Keep", 3)}),
         lambda c: engine_drop(c, WID, 26, 3), dict(page=2, tasks=0, cancelled=False, warn=[], thrown={"Test_Keep": 3})),
        ("arrowLayout inside, vault full: Drop key on the blocked arrow slot (a stored stack)", dict(layout="inside", full=True),
         lambda c: engine_drop(c, WID, 35, 1), dict(page=2, cancelled=False, warn=[], thrown={"Test_P2_S35": 1}, relived=True)),
        ("profile busy: shift-click Next", dict(busy=True), lambda c: smart(V(c), 44, 1, c["box"]),
         dict(page=2, chat=["[Vault] Your profile is still loading - try /vault again in a moment."])),
        ("profile just switched: Drop key on Next", dict(switched=True), lambda c: engine_drop(c, WID, 44, 1),
         dict(page=2, chat_prefix="[Vault] Your profile just changed - your vault opens in ", cancelled=True, warn=[]),
         dict(cancelled=False, warn=["empty"])),
        ("pageArrows off: Drop key on a stored stack", dict(arrows=False), lambda c: engine_drop(c, WID, 3, 4),
         dict(page=2, tasks=0, cancelled=False, warn=[], thrown={"Test_P2_S3": 4}, line=OPEN_NOARROWS % (2, 3))),
    ]
    SKIP_DIFF = {"cancelled", "warn", "dirty", "line", "tips"}
    UNSENT = []
    n_g, n_moves, dirty_old_bad = 0, 0, 0
    for gi, gg in enumerate(G):
        name, scene, action, want = gg[0], gg[1], gg[2], gg[3]
        want_old = dict(want)
        want_old.update(gg[4] if len(gg) > 4 else {})
        obs = {}
        for k in ("old", "new"):
            ctx = tsetup(k, "g%02d" % gi, **scene)
            if not check(ctx["s"] is not None and ctx["win"] is not None, "I. %s %s: the vault opened (%s)" % (name, k, ctx["line"])):
                continue
            before, stray0 = counts(ctx)
            tip0 = tips(ctx)
            ctx["cancelled"] = None
            err = None
            try:
                action(ctx)
            except Exception as ex_:          # an engine exception on a gesture (0.1.1: shift-click / Take All NPE) is a failure
                err = str(ex_)[:200]
            check(err is None, "I. %s [%s]: the gesture threw %s" % (name, k, err))
            # DURING: the engine refused before anything moved - no arrow outside the row, the row still canonical
            _r, stray_during = counts(ctx)
            row_during = row_ok(ctx)
            ctx["tasks"] += drain()
            after, stray1 = counts(ctx)
            s2 = ctx["VS"].current(UID)
            cur = PMS.CUR
            o = dict(page=int(ctx["s"].page), chat=chat(), coins=PURSE.get(US), unlocked=int(ctx["Store"].CACHE.get(UID).unlocked),
                     tasks=ctx["tasks"], cancelled=ctx["cancelled"], warn=list(ctx["warn"]), thrown=dict(ctx["thrown"]),
                     closed=bool(ctx["s"].closed), cur=None if cur is None else str(cur.getClass().getSimpleName()),
                     kinds=row_kinds(ctx), ok=ctx.get("ok"), mid=ctx.get("mid"), line=ctx["line"], tips=tip0,
                     dirty=bool(jf(WinC.class_, "isDirty").get(ctx["win"]).get()),
                     vault_p2=sum(1 for x in ctx["Store"].CACHE.get(UID).pageCopy(2) if x is not None and not x.isEmpty()),
                     relived=bool(ctx["s"].layout == 2 and ctx["s"].ctrlLive(35)))
            obs[k] = o
            n_moves += 1
            tag = "I. %s [%s]" % (name, k)
            check(stray0 == 0 and stray_during == 0 and stray1 == 0, "%s: vault arrow items outside the control row: before %d, during %d, "
                                                                    "after %d" % (tag, stray0, stray_during, stray1))
            check(row_during, "%s: the control row changed DURING the gesture (an arrow left its slot)" % tag)
            if not o["closed"]:
                check(row_ok(ctx), "%s: the control row is not canonical after the batch" % tag)
            check(before == after, "%s: item counts before / after differ:\n   before %s\n   after  %s" % (tag, dict(before), dict(after)))
            wk = want if k == "new" else want_old
            for key, val in wk.items():
                if key == "chat_prefix":
                    check(len(o["chat"]) == 1 and o["chat"][0].startswith(val), "%s: chat %s, want %r..." % (tag, o["chat"], val))
                elif key == "tasks" and val == 0:
                    check(o["tasks"] == 0, "%s: %d world task(s) queued, want none" % (tag, o["tasks"]))
                else:
                    check(o.get(key) == val, "%s: %s = %r, want %r" % (tag, key, o.get(key), val))
            if o["tasks"] > 0 and k == "new":
                check(o["dirty"], "%s: the window was not marked for a re-send after the click batch" % tag)
            if o["tasks"] > 0 and k == "old" and not o["dirty"]:
                dirty_old_bad += 1
                UNSENT.append(name)
            if ctx["line"] is not None and "line" not in wk and ctx["s"].layout != 0:
                want_line = (OPEN_NEW if k == "new" else OPEN_OLD) % (scene.get("page", 2), scene.get("unlocked", 3))
                check(ctx["line"] == want_line, "%s: the opening chat line %r, want %r" % (tag, ctx["line"], want_line))
        if len(obs) == 2:
            a = dict((x, y) for x, y in obs["old"].items() if x not in SKIP_DIFF)
            b = dict((x, y) for x, y in obs["new"].items() if x not in SKIP_DIFF)
            planned = gg[4] if len(gg) > 4 else {}
            for key in set(a) | set(b):
                if key in planned:
                    continue
                check(a.get(key) == b.get(key), "I. %s: 0.1.4 and 0.1.5 differ in %s: %r / %r" % (name, key, a.get(key), b.get(key)))
            n_g += 1
            tally("I turned" if obs["new"]["page"] != 2 else "I stayed")
    # the tooltips of the row the vault opens with (page 2 of 3, row layout) and the gold Buy arrow in both confirm states
    for k in ("old", "new"):
        ctx = tsetup(k, "tips", page=2)
        t = tips(ctx)
        if k == "new":
            for i, lines in ((36, ["Shift-click to turn to page 1 of 3 at once.", TIP_HOW2, TIP_HOW3]),
                             (44, ["Shift-click to turn to page 3 of 3 at once.", TIP_HOW2, TIP_HOW3]),
                             (40, ["4 of 36 slots used", "Shared by all your profiles",
                                   "/vault <page> jumps to a page"] + TIP_INFO)):
                pos, ok = -1, True
                for ln in lines:
                    p2 = t.get(i, "").find(json.dumps(ln)[1:-1], pos + 1)
                    ok = ok and p2 > pos
                    pos = p2
                check(ok, "I. tooltip of slot %d (0.1.5) holds %s in order: %s" % (i, lines, t.get(i, "")[:400]))
        else:
            check("Click to turn to page 3 of 3." in t.get(44, "") and "Shift-click" not in t.get(44, ""), "I. 0.1.4 tooltip unchanged")
        for cf, lines in ((10000, ["10,000 coins from your active profile.", "Shift-click to buy it at once.", TIP_HOW2,
                                   "A plain click lifts it - it buys when you put it back."]),
                          (50000, ["50,000 coins from your active profile.", "Shift-click - a window asks you to confirm.", TIP_HOW2,
                                   "A plain click lifts it - the window opens when you put it back."]),
                          (0, ["Free - no coins needed.", "Shift-click to unlock it at once.", TIP_HOW2,
                               "A plain click lifts it - it unlocks when you put it back."])):
            if k == "old":
                continue
            ctx = tsetup(k, "tipbuy%d" % cf, page=2, unlocked=2, price=cf)
            tb = tips(ctx).get(44, "")
            pos, ok = -1, True
            for ln in lines:
                p2 = tb.find(json.dumps(ln)[1:-1], pos + 1)
                ok = ok and p2 > pos
                pos = p2
            check(ok, "I. the gold arrow's tooltip at price %d holds %s in order: %s" % (cf, lines, tb[:400]))
    # /vault info (VStore.infoLines): 0.1.4's lines except the planned help-line tail with arrows on (review fix: the gestures named);
    # arrows off and the admin view (no help line) identical on both jars
    INFO = {}
    for k in ("old", "new"):
        for arrows in (False, True):         # arrows on LAST: VCfg.ARROWS is static and J's config file has no pageArrows key
            ctx = tsetup(k, "info%d" % int(arrows), page=2, arrows=arrows)
            for admin in (False, True):
                INFO[(k, arrows, admin)] = [str(x) for x in ctx["Store"].infoLines(UID, 2, admin)]
    for arrows in (True, False):
        for admin in (False, True):
            lo, ln = INFO[("old", arrows, admin)], INFO[("new", arrows, admin)]
            if admin:
                check(lo == ln and len(ln) > 1 and not any(x.startswith(INFO_HELP[:12]) for x in ln),
                      "I. /vault info, admin view (arrows %s): identical on both jars, no player help line:\n   %s\n   %s" % (
                          arrows, lo, ln))
            else:
                want_o = INFO_HELP + (INFO_ARROWS_OLD if arrows else "")
                want_n = INFO_HELP + (INFO_ARROWS_NEW if arrows else "")
                check(len(lo) == len(ln) > 1 and lo[:-1] == ln[:-1] and lo[-1] == want_o and ln[-1] == want_n,
                      "I. /vault info (arrows %s): 0.1.4 = 0.1.5 except the help line, which ends as planned:\n   %s\n   %s" % (
                          arrows, lo, ln))
    # VDropSys's fast exits touch nothing: no vault open anywhere / a player section / a closed vault
    for k in ("new",):
        ctx = tsetup(k, "fast", page=2)
        VS = ctx["VS"]
        VS.SESSIONS.clear()
        for sec in (WID, -1, -2, 0):
            e = DIRQ(JInt(sec), JShort(44))
            DSYS.handleInternal(0, None, None, None, e)          # null chunk / store: a fast exit never reaches them
            check(not e.isCancelled(), "I. VDropSys with no vault open (section %d): not cancelled" % sec)
        check("drop" not in [str(x) for x in ctx["Cfg"].WARNED.keySet()], "I. VDropSys fast exits never reach the chunk (no warning)")
        ctx = tsetup(k, "fast2", page=2)
        e = DIRQ(JInt(-1), JShort(3))
        DSYS.handleInternal(0, None, None, None, e)
        check(not e.isCancelled() and "drop" not in [str(x) for x in ctx["Cfg"].WARNED.keySet()], "I. VDropSys: a player section "
                                                                                                  "(hotbar) is never looked at")
        e = DIRQ(JInt(WID), JShort(44))
        DSYS.handleInternal(0, None, STORE, None, e)             # a broken chunk: caught, warned once, the request left alone
        check(not e.isCancelled() and "drop" in [str(x) for x in ctx["Cfg"].WARNED.keySet()], "I. VDropSys: an engine failure is caught "
                                                                                              "(warned once), the request left alone")
    COUNT["I gestures"] = n_g
    print("I. %d gestures x 2 jars end to end (%d runs): pages turned %d / stayed %d on 0.1.5; no arrow ever outside the control row "
          "(before, during, after); item counts equal before / after in every run; 0.1.4 = 0.1.5 except the planned Drop-key rows; "
          "0.1.5 re-sends the window after every click batch (0.1.4 left it unsent in %d runs: %s); opening line + tooltips + /vault info "
          "as planned" % (
              n_g, n_moves, COUNT.get("I turned", 0), COUNT.get("I stayed", 0), dirty_old_bad, UNSENT))
    check(dirty_old_bad >= 1, "I. the re-send check bites: 0.1.4 left the window unsent after at least one click batch")


# ------------------------------------------------------------------------------------------------ J. start twice on the live data
def live_section(E):
    from jpype import JClass, JShort
    U, jc, UID, UUID, Paths, PR, field = E["U"], E["jc"], E["UID"], E["UUID"], E["Paths"], E["PR"], E["field"]
    if not LIVE or not os.path.isdir(LIVE):
        print("J. skipped: no live Skyy_SkyyVault folder (%s)" % LIVE)
        return
    src_files = {}
    for root, _d, files in os.walk(LIVE):
        for f in files:
            p = os.path.join(root, f)
            src_files[os.path.relpath(p, LIVE)] = open(p, "rb").read()
    check(any(n.startswith("vaults") for n in src_files), "J. the live folder holds vault files: %s" % sorted(src_files))
    RESULT = {}
    for k in ("old", "new"):
        Cfg, Store, VS, Btn = jc(k, "VCfg"), jc(k, "VStore"), jc(k, "VSessions"), jc(k, "VBtn")
        dst = os.path.join(WORK, "live", k)
        shutil.copytree(LIVE, dst)
        runs = []
        for run_i in (1, 2):
            Cfg.DIR = Paths.get(dst)
            Cfg.VDIR = Paths.get(dst).resolve("vaults")
            Cfg.FILE = Paths.get(dst).resolve("config.properties")
            Cfg.LOGF = Paths.get(dst).resolve("vault.log")
            Cfg.NAMESF = Paths.get(dst).resolve("names.properties")
            Cfg.WARNED.clear()
            for m in ("CACHE", "PENDING", "BUYING", "LASTBUY", "NAMES"):
                getattr(Store, m).clear()
            Store.SAVER = None
            Store.STOPPING = False
            for m in ("SESSIONS", "LAST", "EPOCHS", "SWITCHED", "BUSYSEEN", "ONLINE"):
                getattr(VS, m).clear()
            before = dict((n, open(os.path.join(dst, n), "rb").read()) for n in sorted(src_files))
            summary = str(Cfg.load())
            Store.loadNames()
            recs = {}
            for n in sorted(os.listdir(os.path.join(dst, "vaults"))):
                if not n.endswith(".json"):
                    continue
                u = UUID.fromString(n[:-5])
                d = Store.load(u)
                if not check(d is not None, "J. %s run %d: vault %s reads" % (k, run_i, n)):
                    continue
                slots = []
                for pg in range(1, int(d.unlocked) + 1):
                    for i, x in enumerate(d.pageCopy(pg)):
                        if x is not None and not x.isEmpty():
                            md = x.getMetadata()
                            slots.append((pg, i, str(x.getItemId()), int(x.getQuantity()), float(x.getDurability()),
                                          float(x.getMaxDurability()), None if md is None else str(md.toJson())))
                recs[n] = (int(d.unlocked), int(d.cap), slots, str(d.orphans))
                # an open / close of page 1 with no change (a /vault that only looks): nothing is written
                pr = U.allocateInstance(PR.class_)
                field(PR, "uuid").set(pr, u)
                field(PR, "username").set(pr, "LiveCopy")
                s = VS.newSession(pr, u, d, 1, 2)
                if check(s is not None, "J. %s run %d: a session opens on the live vault" % (k, run_i)):
                    VS.SESSIONS.put(u, s)
                    view_btns = sum(1 for i in range(int(s.view.getCapacity())) if Btn.isButton(s.view.getItemStack(JShort(i))))
                    check(view_btns == (9 if s.layout == 1 else 0) or s.layout == 2, "J. %s: the live vault opens with its arrow row" % k)
                    VS.retire(s)
            after_look = dict((n, open(os.path.join(dst, n), "rb").read()) for n in sorted(src_files))
            check(after_look == before, "J. %s run %d: a start + an open / close with no change writes nothing: %s" % (
                k, run_i, [n for n in before if before[n] != after_look.get(n)]))
            # a forced save (what the first real change would write)
            for n in recs:
                d = Store.CACHE.get(UUID.fromString(n[:-5]))
                d.rev = d.rev + 1
            Store.flushAll()
            written = {}
            for n in recs:
                doc = json.loads(open(os.path.join(dst, "vaults", n), encoding="utf8").read())
                for x in ("savedAt", "rev"):
                    doc.pop(x, None)
                written[n] = doc
            runs.append(dict(summary=summary, recs=recs, written=written,
                             cfg=open(os.path.join(dst, "config.properties"), "rb").read(),
                             names=open(os.path.join(dst, "names.properties"), "rb").read() if os.path.exists(os.path.join(dst, "names.properties")) else None))
        if len(runs) == 2:
            check(runs[0]["recs"] == runs[1]["recs"], "J. %s: the second start reads exactly what the first one saw" % k)
            check(runs[0]["written"] == runs[1]["written"], "J. %s: the second start's save is the same file (savedAt / rev aside)" % k)
            check(runs[0]["summary"] == runs[1]["summary"], "J. %s: the same config both starts" % k)
            check(runs[1]["cfg"] == src_files.get("config.properties") and runs[1]["names"] == src_files.get("names.properties"),
                  "J. %s: config.properties + names.properties untouched" % k)
            for n, doc in runs[0]["written"].items():
                live_doc = json.loads(src_files[os.path.join("vaults", n)].decode("utf8"))
                n_live = sum(len(p.get("slots", [])) for p in live_doc.get("content", [])) + len(live_doc.get("orphans", []))
                n_read = len(runs[0]["recs"][n][2])
                check(n_live == n_read and doc.get("version") == (VERSION if k == "new" else OLD_VERSION),
                      "J. %s: %s - %d stacks in the live file, %d read and written back (version %s)" % (k, n, n_live, n_read, doc.get("version")))
                tally("J stacks " + k, n_read)
        RESULT[k] = runs
    if len(RESULT) == 2 and len(RESULT["old"]) == 2 and len(RESULT["new"]) == 2:
        check(RESULT["old"][0]["recs"] == RESULT["new"][0]["recs"], "J. 0.1.4 and 0.1.5 read the live vaults the same")
        strip = lambda w: dict((n, dict((x, y) for x, y in d.items() if x != "version")) for n, d in w.items())
        check(strip(RESULT["old"][0]["written"]) == strip(RESULT["new"][0]["written"]), "J. 0.1.4 and 0.1.5 write the same file (version aside)")
        check(RESULT["old"][0]["summary"] == RESULT["new"][0]["summary"], "J. the same config summary: %s" % RESULT["new"][0]["summary"])
    print("J. start twice on a copy of %s (%d files): %d / %d stacks read, an open / close writes nothing, the second start = the first, "
          "0.1.4 = 0.1.5; config: %s" % (LIVE, len(src_files), COUNT.get("J stacks old", 0), COUNT.get("J stacks new", 0),
                                         RESULT.get("new", [{}])[0].get("summary") if RESULT.get("new") else "-"))


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
    print("SkyyVault %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
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
