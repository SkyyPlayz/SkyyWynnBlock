"""Bare-JVM page harness for SkyyBank 0.1.5 - BankPage's layout + size change (Skyy 2026-09-30 on the live 0.1.4 page: the amount
box between Deposit and Withdraw, the page ~10% bigger). Carried forward from SkyyBank/test_skyybank_0.1.4.py (committed next to the
build so the build docstring's CHECKED claims can be re-run instead of trusted); copy it to the next version and keep it passing.

    python SkyyBank/test_skyybank_0.1.5.py [--jar <SkyyBank-0.1.5.jar>] [--old <SkyyBank-0.1.4.jar>] [--dir <scratch>] [--keep]

Build first (python tools/bank_0_1_5_patch.py, then python SkyyBank/build_skyybank_0.1.5.py). One JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; EACH SkyyBank jar in its own class loader,
so 0.1.4 - the live SET pin - and 0.1.5 run side by side in one process) checks:
  A  every class of both jars loads, verifies and initialises
  B  the layout-only contract in bytes: the 10 classes other than BankPage and SkyyBankPlugin are byte-identical to 0.1.4;
     SkyyBankPlugin is byte-identical once its one ready-log constant is swapped back (that constant names the kit and the page
     id; 0.1.4's names the checked 0.1.4 page a838d325f680); BankPage (javassist, constant-pool indices resolved): the same fields
     and methods, every method but build() instruction-identical
  C  payoutOn(readable, bank, pct, max) is true exactly when gainText(...) returns its payout line (grid of balances, rates, caps)
  D  differential page builds, 0.1.4 vs 0.1.5, in 10 states (readable purse + profile, a long profile name + class, an
     unreadable purse, no SkyyCoins, an unreadable account file, interest off, a bank above the principal cap, no profile + an
     empty bank, a bank too small to earn, interest due now) x 5 result marks / amount-box states = 50 builds per jar, with the
     engine's own UICommandBuilder / UIEventBuilder and a PlayerRef allocated without a constructor: the same b.set lines IN THE
     SAME ORDER (targets and values, incl. #SkyyBAmount.Value), the same 7 event bindings (+ EventData, locks) in the same order,
     the same element ids and the same static texts (Text / PlaceholderText); every 0.1.5 appendInline equals the markup the kit
     makes NOW from the generated script's bank_page() (J() slots filled), every markup passes SUI.check_markup, every build
     SUI.check_page and SUI.assert_proven, no underscore ids, only kit colours; the runtime colours: #SkyyBGain green for a
     payout, label grey for a hint, error red for an unreadable account; #SkyyBInfo by its mark; all 25 0.1.3 ids
  E  clicks through handleDataEvent (the real page method; its rebuild() / close() fail harmlessly outside a server and are
     caught by the page itself) in 4 states x 13 clicks on both jars: identical result line, amount box, purse and bank after
     every click (the same coin moves; "Enter alone never moves coins"), and identical b.set lines, in order, on the rebuilt page
  F  text fit with the client's font tables (Client/Data/Shared/UI/Fonts, read-only; skipped when the client is not installed),
     every box width read back out of the 0.1.5 markup (Width, or the parent's content width minus margins; minus Padding):
     every button label fits its button minus the 2 x 24 px padding, every one-line text (static or seen at run time) fits its
     box, every wrapped text fits its box's height (#SkyyBSub / #SkyyBInfo: at most two 18 px lines), the typed amounts fit
     the amount box
  G  the page id: BANK_PAGE_ID of the kit's page NOW == BANK_PAGE_CHECKED in the generated script == the page id in the jar's
     ready log line
  H  Skyy's two asks: the controls row is Deposit all | Deposit | Amount | Withdraw | Withdraw all (0.1.4: Deposit all | Amount |
     Deposit | Withdraw | Withdraw all) and each caption spans its controls (x positions from the built markup); the page root
     is <= 980 px and fits 1080 with its 12 / 6 px ornaments; every sized element (by id, or an anonymous label by its text) is
     1.08 - 1.15 x its 0.1.4 Width / Height / FontSize / Padding Full - except the vanilla title bar (38 px), its 15 px title and
     the kit's 17 px button labels, which must stay 0.1.4's
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the bigger page and the new row order.
Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/test-bank, deleted at the end
unless --keep; TEMP / TMP and java.io.tmpdir point into it). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.5", "0.1.4"
OLD_PAGE_ID = "a838d325f680"            # the 0.1.4 page that test_skyybank_0.1.4.py checked and Skyy saw in game
PKG = "com.skyy.bank."
SCRIPT = os.path.join(HERE, "build_skyybank_%s.py" % VERSION)
SIZE_RATIO = (1.08, 1.15)               # "size the menu up like 10%": every scaled size within this of 0.1.4's


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "test-bank")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyBank-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def tally(key, n=1):
    COUNT[key] = COUNT.get(key, 0) + n


# ------------------------------------------------------------------------------------------------ the kit's page, NOW (no JVM)
def kit_page():
    """Run the generated script's page code (its BANK_* constants, bank_* functions, the build source and the page id) on the
    CURRENT kit, without the rest of the build: returns (SUI, namespace)."""
    import skyyui as SUI
    SUI.verify(quiet=True)
    tree = ast.parse(open(SCRIPT, encoding="utf8").read())
    body = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name.startswith("bank_"):
            body.append(n)
        elif isinstance(n, ast.Assign) and all(isinstance(t, (ast.Name, ast.Tuple)) for t in n.targets):
            names = [x.id for t in n.targets for x in (t.elts if isinstance(t, ast.Tuple) else [t]) if isinstance(x, ast.Name)]
            if names and all(x.startswith("BANK_") for x in names):
                body.append(n)
    ns = {"SUI": SUI, "re": re, "hashlib": __import__("hashlib")}
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


# ------------------------------------------------------------------------------------------------ markup reading (no JVM)
_ELEM = re.compile(r"([A-Z][A-Za-z]*)(?: #([A-Za-z0-9]+))? \{")
_NUMS = r"(Width|Height|Left|Right|Top|Bottom|Horizontal|Vertical|Full): (-?\d+)"


def strip_quoted(s):
    return re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: '"' + "x" * (len(m.group(0)) - 2) + '"', s)


def elements(r):
    """[(type, id or None, own text, parent index or None)] of every element in a rendered markup, in order; own = the text up to
    the next element (the kit writes an element's own properties before its children); parent index = the enclosing element in
    this list (brace nesting), None = the markup's root element"""
    bare = strip_quoted(r)
    ms = list(_ELEM.finditer(bare))
    at = dict((m.end() - 1, n) for n, m in enumerate(ms))
    parent, stack = {}, []
    for pos, ch in enumerate(bare):
        if ch == "{":
            n = at.get(pos)
            if n is None:
                raise ValueError("a brace that opens no element at %d: %s" % (pos, bare[max(0, pos - 40):pos + 1]))
            parent[n] = stack[-1] if stack else None
            stack.append(n)
        elif ch == "}":
            stack.pop()
    if stack:
        raise ValueError("unbalanced markup: %s" % r[:80])
    out = []
    for n, m in enumerate(ms):
        end = ms[n + 1].start() if n + 1 < len(ms) else len(r)
        out.append((m.group(1), m.group(2), r[m.end():end], parent[n]))
    return out


def own_anchor(own):
    m = re.search(r"Anchor: \(([^)]*)\)", own)
    return dict((k, int(v)) for k, v in re.findall(_NUMS, m.group(1))) if m else {}


def own_padding(own):
    m = re.search(r"Padding: \(([^)]*)\)", own)
    return dict((k, int(v)) for k, v in re.findall(_NUMS, m.group(1))) if m else {}


def own_font(own):
    m = re.search(r"FontSize: (\d+)", own)
    return int(m.group(1)) if m else None


def own_text(own):
    m = re.search(r'(?<![A-Za-z])Text: "((?:[^"\\]|\\.)*)"', own)
    return m.group(1) if m else None


def hsum(d):
    return d.get("Left", 0) + d.get("Right", 0) + 2 * (d.get("Horizontal", 0) + d.get("Full", 0))


def sized(appends):
    """{key: {"Width", "Height", "FontSize", "Pad"}} of every element with an id (key = the id) and every anonymous Label with a
    static text (key = "text:" + its text), from (parent, rendered markup) appends"""
    out = {}
    for _p, r in appends:
        for typ, ident, own, _up in elements(r):
            key = ident if ident else ("text:" + own_text(own) if typ == "Label" and own_text(own) else None)
            if key is None:
                continue
            a, pd = own_anchor(own), own_padding(own)
            out[key] = {"type": typ, "Width": a.get("Width"), "Height": a.get("Height"), "FontSize": own_font(own),
                        "Pad": pd.get("Full")}
    return out


# ------------------------------------------------------------------------------------------------ the client's font tables
FONT_DIR = None


def fonts():
    """{"regular": (advances, lineHeight), "bold": ...} from the client's NunitoSans tables (the game's Default font), or None"""
    global FONT_DIR
    import skyybuild as B
    FONT_DIR = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Client", "Data", "Shared", "UI", "Fonts")
    out = {}
    for kind, name in (("regular", "NunitoSans-Medium.json"), ("bold", "NunitoSans-ExtraBold.json")):
        p = os.path.join(FONT_DIR, name)
        if not os.path.isfile(p):
            return None
        d = json.load(open(p, encoding="utf8"))
        out[kind] = (dict((g["unicode"], float(g["advance"])) for g in d["glyphs"]), float(d["metrics"]["lineHeight"]))
    return out


def text_w(F, text, size, bold):
    """px width of one line: the wider of the regular and (for bold text) the extra-bold advances - the conservative reading"""
    best = 0.0
    for kind in (("regular", "bold") if bold else ("regular",)):
        adv = F[kind][0]
        best = max(best, sum(adv.get(ord(c), adv.get(ord("?"), 0.6)) for c in text) * size)
    return best


def wrap_lines(F, text, size, bold, width):
    """greedy word wrap: the number of lines `text` takes in `width` px"""
    lines, cur = 1, ""
    for word in text.split(" "):
        trial = (cur + " " + word) if cur else word
        if text_w(F, trial, size, bold) <= width or not cur:
            cur = trial
        else:
            lines += 1
            cur = word
    return lines


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride
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

    # ---------------- A. load + verify + init, both jars
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                tally("A classes " + k)
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: %s %d, %s %d classes (-Xverify:all)" % (
        OLD_VERSION, COUNT.get("A classes old", 0), VERSION, COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. the layout-only contract in bytes
    old, new = CB["old"], CB["new"]
    check(sorted(old) == sorted(new), "B. the same class names: %s" % sorted(set(old) ^ set(new)))
    page_c, plug_c = PKG + "BankPage", PKG + "SkyyBankPlugin"
    for n in sorted(old):
        if n in (page_c, plug_c) or n not in new:
            continue
        if check(old[n] == new[n], "B. %s is byte-identical to %s" % (n, OLD_VERSION)):
            tally("B identical")
    ready_old = [e for e in cp_utf8(old[plug_c]) if ("] %s ready" % OLD_VERSION).encode() in e[2]]
    ready_new = [e for e in cp_utf8(new[plug_c]) if ("] %s ready" % VERSION).encode() in e[2]]
    if check(len(ready_old) == 1 and len(ready_new) == 1, "B. one ready-log constant in each SkyyBankPlugin"):
        s0, e0, t0 = ready_old[0]
        s1, e1, t1 = ready_new[0]
        swapped = new[plug_c][:s1] + old[plug_c][s0:e0] + new[plug_c][e1:]
        check(swapped == old[plug_c], "B. SkyyBankPlugin = %s's bytes once the ready-log constant is swapped back" % OLD_VERSION)
        LOG_NEW = t1.decode("utf8")
        check(re.fullmatch(r"\[SkyyBank\] 0\.1\.4 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page %s\) - /bank \(page\), interest " % OLD_PAGE_ID,
                           t0.decode("utf8")) is not None, "B. the 0.1.4 jar is the checked 0.1.4 page %s: %r" % (OLD_PAGE_ID, t0))
        check(re.fullmatch(r"\[SkyyBank\] 0\.1\.5 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page [0-9a-f]{12}\) - /bank \(page\), interest ",
                           LOG_NEW) is not None, "B. the 0.1.5 ready constant names the kit and the page id: %r" % LOG_NEW)
    else:
        LOG_NEW = ""
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        pool = CP(False)
        return pool.makeClass(BAIS(b))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, out = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            out.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp))))
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try %d %d %d %s" % (et.startPc(i), et.endPc(i), et.handlerPc(i), cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        return out

    po, pn = ct(old[page_c]), ct(new[page_c])
    check(sorted((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
          == sorted((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields()), "B. BankPage fields unchanged")
    check(str(po.getClassFile().getSuperclass()) == str(pn.getClassFile().getSuperclass()), "B. BankPage superclass unchanged")
    mo, mn = methods(po), methods(pn)
    gone = sorted(k for k in mo if k not in mn)
    added = sorted(k for k in mn if k not in mo)
    check(not gone and not added, "B. BankPage: the same methods (gone %s, new %s)" % (gone, added))
    changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
    same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
    check(changed == ["build"], "B. BankPage: only build() changed: %s" % changed)
    for keep in ("<init>", "jsonStr", "fmt", "colorOf", "textOf", "dur", "every", "subText", "rateText", "nextText", "gainText",
                 "payoutOn", "typed", "handleDataEvent"):
        check(keep in same, "B. BankPage.%s is instruction-identical to %s" % (keep, OLD_VERSION))
    COUNT["B page same"] = len(same)
    print("B. %d classes byte-identical, SkyyBankPlugin = %s but its ready constant, BankPage: %d methods instruction-identical "
          "(%s), changed %s" % (COUNT.get("B identical", 0), OLD_VERSION, len(same), ", ".join(same), changed))

    # ---------------- common Java objects
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    System = JClass("java.lang.System")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def field(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    # ---------------- C. payoutOn == "gainText returned its payout line"
    Pn = jc("new", "BankPage")
    n_grid = 0
    bad = []
    for rd in (True, False):
        for bank in (0, 1, 33, 49, 50, 51, 99, 100, 101, 4999, 5000, 9999999, 10000000, 10000001, 20000000, 10 ** 12):
            for pct in (0, 1, 2, 3, 7, 50, 99, 100):
                for mx in (0, 1, 50, 99, 100, 5000, 10000000, 10 ** 12):
                    g = str(Pn.gainText(rd, bank, pct, mx))
                    p = bool(Pn.payoutOn(rd, bank, pct, mx))
                    n_grid += 1
                    if p != g.startswith("Your next payout"):
                        bad.append((rd, bank, pct, mx, p, g[:40]))
    check(not bad, "C. payoutOn == gainText's payout line on %d inputs; differ: %s" % (n_grid, bad[:5]))
    COUNT["C grid"] = n_grid
    print("C. payoutOn vs gainText: %d inputs, %d differ" % (n_grid, len(bad)))

    # ---------------- the bridge (one map for both jars: System property skyy.bridge) and the fake SkyyCoins / SkyyProfiles
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    PURSE = {}                            # uuid -> coins, None = the purse cannot be read (SkyyCoins returns null)

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

    PKEY = {}

    @JImplements("java.util.function.Function")
    class ProfKey:
        @JOverride
        def apply(self, u):
            return PKEY.get(str(u), str(u))

    COINS = (CoinsGet(), CoinsAdd(), CoinsTake())
    PROF = ProfKey()
    UID = UUID.fromString("00000000-0000-0000-0000-0000000000b1")
    US = str(UID)

    # the states: name, purse (None = unreadable, "none" = no SkyyCoins), bank (None = no file, "bad" = unreadable file), profile
    # (None or (name, class)), pct, minutes, max principal, LAST offset (ms before now; None = 0 = due now)
    STATES = [
        ("readable", 12500, 5000, ("Main", "Warrior"), 2, 60, 10000000, 600000),
        ("longname", 12500, 5000, ("Averyveryverylongprofilename", "Arcanist of the Sunken Library"), 2, 60, 10000000, 600000),
        ("purseunread", None, 5000, ("Main", "Warrior"), 2, 60, 10000000, 600000),
        ("nocoins", "none", 5000, None, 2, 60, 10000000, 600000),
        ("accountunread", 12500, "bad", ("Main", "Warrior"), 2, 60, 10000000, 600000),
        ("interestoff", 12500, 5000, None, 0, 60, 10000000, 600000),
        ("abovecap", 999999, 20000000, ("Main", "Warrior"), 2, 60, 10000000, 600000),
        ("empty", 0, None, None, 2, 60, 10000000, 600000),
        ("toosmall", 300, 10, None, 2, 60, 10000000, 600000),
        ("duenow", 12500, 5000, None, 3, 90, 10000000, None),
    ]
    # result line / amount box variants for the builds
    MARKS = [("", ""), ("+Deposited 2,000 coins. Bank: 7,000 coins.", ""), ("-Not enough coins in your purse (12,500).", "999999"),
             ("=Type an amount in the box first (500, 2k, 1.5m or all), then click Deposit.", "2k"), ("plain text", "1.5m")]

    def setup(k, st):
        name, purse, bank, prof, pct, mins, mx, ago = st
        Store, Cfg = jc(k, "BankStore"), jc(k, "BankConfig")
        d = os.path.join(SCRATCH, "accounts", k, name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        Store.DIR = Paths.get(d)
        Store.BAL.clear()
        Store.LOADED.clear()
        Store.EPOCH.clear()
        BR.clear()
        PURSE.clear()
        PKEY.clear()
        if purse != "none":
            BR.put("coins:fn:get", COINS[0])
            BR.put("coins:fn:add", COINS[1])
            BR.put("coins:fn:take", COINS[2])
            PURSE[US] = purse
        key = US
        if prof is not None:
            key = US + "-p2"
            PKEY[US] = key
            BR.put("profile:fn:key", PROF)
            BR.put("profile:name:" + US, prof[0])
            BR.put("profile:class:" + US, prof[1])
            BR.put("profile:epoch:" + US, Long.valueOf(3))
        if bank == "bad":
            open(os.path.join(d, key + ".properties"), "w").write("balance=not-a-number\n")
        elif bank is not None:
            open(os.path.join(d, key + ".properties"), "w").write("#SkyyBank\nbalance=%d\n" % bank)
        Cfg.PERCENT = pct
        Cfg.MINUTES = mins
        Cfg.MAX_PRINCIPAL = mx
        Cfg.LAST = 0 if ago is None else int(System.currentTimeMillis()) - ago
        return Store, key

    def pref(u):
        p = U.allocateInstance(PR.class_)
        field(PR, "uuid").set(p, u)
        return p

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    DUR = re.compile(r"in \d+ h \d+ min|in \d+ min \d+ s|in \d+ s")

    def sets_of(cmds):
        """the b.set lines IN ORDER (the next-interest countdown normalised)"""
        return [(sel, DUR.sub("in <t>", data or "")) for typ, sel, text, data in cmds if "append" not in typ.lower()]

    def appends_of(cmds):
        return [(sel, text) for typ, sel, text, data in cmds if "append" in typ.lower()]

    def ids_of(cmds):
        return sorted(i for _s, t in appends_of(cmds) for _ty, i, _o, _up in elements(t) if i)

    def texts_of(cmds):
        return sorted(re.findall(r'(?<![A-Za-z])(?:Text|PlaceholderText): "((?:[^"\\]|\\.)*)"', "\n".join(t for _s, t in appends_of(cmds))))

    def set_text(cmds, ident):
        v = [data for typ, sel, text, data in cmds if sel == "#%s.Text" % ident]
        if len(v) != 1:
            return None
        d = json.loads(v[0])           # the engine keeps a set value as {"0": value}
        return d.get("0") if isinstance(d, dict) else d

    # the kit's expected appends, as patterns (J() slots = captured runtime values)
    exp = list(K["BANK_SH"].appends)

    def pattern(mk):
        parts, pos, slots = [], 0, []
        for m in SUI._J_RE.finditer(mk):
            parts.append(re.escape(mk[pos:m.start()]))
            parts.append("(.*?)")
            slots.append(m.group(1))
            pos = m.end()
        parts.append(re.escape(mk[pos:]))
        return re.compile(r"\A" + "".join(parts) + r"\Z", re.S), slots

    PATS = [(p, pattern(mk)) for p, mk in exp]
    ALLOWED = set(SUI.allowed_colors())
    COL = SUI.COLOR
    IDS013 = list(K["BANK_IDS_013"])

    def expect_gain(st, readable, bank_now=None):
        name, purse, bank, prof, pct, mins, mx, ago = st
        if not readable:
            return COL["error"]
        b = bank_now if bank_now is not None else (bank if isinstance(bank, int) else 0)
        return COL["success"] if pct > 0 and min(b, mx) * pct // 100 > 0 else COL["text"]

    def expect_info(info):
        return SUI.STATUS.get(info[:1], COL["text"]) if info else COL["text"]

    def check_new_build(tag, st, info, cmds, bank_now=None):
        """0.1.5: the appends equal the kit markup NOW; markup rules; proven properties; runtime colours (bank_now = the balance
        after clicks). Returns the built page as (parent id or None, markup) pairs."""
        aps = appends_of(cmds)
        if not check(len(aps) == len(PATS), "D. %s: %d appends, the kit makes %d" % (tag, len(aps), len(PATS))):
            return []
        runtime = []
        readable = st[2] != "bad"
        for (sel, text), (parent, (pat, slots)) in zip(aps, PATS):
            want_sel = None if parent is None else "#" + parent
            check(sel == want_sel, "D. %s: append parent %r, the kit says %r" % (tag, sel, want_sel))
            m = pat.match(text)
            if not check(m is not None, "D. %s: an append differs from the kit markup: %s" % (tag, text[:160])):
                continue
            for expr, val in zip(slots, m.groups()):
                check(SUI.norm_color(val) in ALLOWED, "D. %s: runtime colour %s is not a kit colour" % (tag, val))
                if "payoutOn" in expr:
                    want = expect_gain(st, readable, bank_now)
                    check(val == want, "D. %s: #SkyyBGain colour %s, want %s" % (tag, val, want))
                    tally("D gain " + {COL["success"]: "green", COL["text"]: "grey", COL["error"]: "red"}.get(val, val))
                elif "colorOf(this.info)" in expr:
                    check(val == expect_info(info), "D. %s: #SkyyBInfo colour %s, want %s" % (tag, val, expect_info(info)))
                else:
                    check(False, "D. %s: unknown runtime slot %s" % (tag, expr))
            try:
                SUI.check_markup(text, prefix=K["BANK_PREFIX"], root=(sel is None))
                tally("D markups")
            except ValueError as e:
                check(False, "D. %s: check_markup: %s" % (tag, e))
            ids = re.findall(r"#([A-Za-z0-9_]+)\s*\{", text)
            check(all("_" not in i for i in ids), "D. %s: underscore in an id: %s" % (tag, ids))
            bare = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
            check("@" not in bare and "$" not in bare, "D. %s: a document variable inline" % tag)
            runtime.append((None if sel is None else sel[1:], text))
        try:
            SUI.check_page(runtime, prefix=K["BANK_PREFIX"])
            tally("D pages")
        except ValueError as e:
            check(False, "D. %s: check_page: %s" % (tag, e))
        try:
            SUI.assert_proven([t for _p, t in runtime], what="bank page " + tag)
            tally("D proven")
        except ValueError as e:
            check(False, "D. %s: assert_proven: %s" % (tag, e))
        have = set(i for _p, t in runtime for i in re.findall(r"#([A-Za-z0-9]+)\s*\{", t))
        check(all(i in have for i in IDS013), "D. %s: 0.1.3 ids missing: %s" % (tag, [i for i in IDS013 if i not in have]))
        g = set_text(cmds, "SkyyBGain") or ""
        if readable:
            check(g.startswith("Your next payout") == (expect_gain(st, True, bank_now) == COL["success"]),
                  "D. %s: payout text vs colour: %r" % (tag, g))
        return runtime

    # ---------------- D. differential builds
    SEEN = {}                              # id -> set of texts seen (for F)
    FIRST = {}                             # the first build of each jar, (parent, markup) pairs (for H)
    n_builds = 0
    for st in STATES:
        for info, keep in MARKS:
            res = {}
            for k in ("old", "new"):
                setup(k, st)
                pg = jc(k, "BankPage")(pref(UID))
                pg.info = info
                pg.keepAmount = keep
                res[k] = build(pg)
                n_builds += 1
            tag = "%s / %r / %r" % (st[0], info[:12], keep)
            (co, eo), (cn, en) = res["old"], res["new"]
            check(sets_of(co) == sets_of(cn), "D. %s: b.set lines differ (in order):\n  %s %s\n  %s %s" % (
                tag, OLD_VERSION, sets_of(co), VERSION, sets_of(cn)))
            check(eo == en, "D. %s: event bindings differ (in order)" % tag)
            check(len(en) == 7, "D. %s: 7 event bindings (%d)" % (tag, len(en)))
            check(ids_of(co) == ids_of(cn), "D. %s: element ids differ: %s" % (tag, sorted(set(ids_of(co)) ^ set(ids_of(cn)))))
            check(texts_of(co) == texts_of(cn), "D. %s: static texts differ: %s | %s" % (tag, texts_of(co), texts_of(cn)))
            check(bool(keep) == any(sel == "#SkyyBAmount.Value" for typ, sel, text, data in cn), "D. %s: the amount box value" % tag)
            check_new_build(tag, st, info, cn)
            if not FIRST:                  # what each JAR built (not the kit's page): F and H read these
                FIRST["old"] = [(None if s is None else s[1:], t) for s, t in appends_of(co)]
                FIRST["new"] = [(None if s is None else s[1:], t) for s, t in appends_of(cn)]
            for typ, sel, text, data in cn:
                if sel and sel.endswith(".Text"):
                    SEEN.setdefault(sel[1:-5], set()).add(set_text(cn, sel[1:-5]))
    COUNT["D builds"] = n_builds
    print("D. %d page builds (%d states x %d marks x 2 jars): b.set lines + bindings in order, ids, static texts identical; %d %s "
          "markups checked in %d pages (%d assert_proven); payout line %s" % (
              n_builds, len(STATES), len(MARKS), COUNT.get("D markups", 0), VERSION, COUNT.get("D pages", 0),
              COUNT.get("D proven", 0), dict((k[7:], v) for k, v in COUNT.items() if k.startswith("D gain "))))

    # ---------------- E. clicks (handleDataEvent), identical on both jars
    CLICKS = [("refresh", ""), ("deposit", ""), ("deposit", "2k"), ("withdraw", "1,500"), ("deposit", "999999999"),
              ("withdraw", "abc"), ("amount", ""), ("amount", "250"), ("depall", ""), ("wdall", ""), ("withdraw", "all"),
              ("bogus", "5"), ("close", "")]
    n_clicks = 0
    for st in [s for s in STATES if s[0] in ("readable", "nocoins", "purseunread", "accountunread")]:
        trace = {}
        for k in ("old", "new"):
            Store, key = setup(k, st)
            pg = jc(k, "BankPage")(pref(UID))
            steps = []
            for a, t in CLICKS:
                before = (PURSE.get(US, "none"), int(Store.getKey(key)) if bool(Store.ready(key)) else "unreadable")
                pg.handleDataEvent(None, None, json.dumps({"a": a, "@BAmount": t}))
                n_clicks += 1
                bank = int(Store.getKey(key)) if bool(Store.ready(key)) else "unreadable"
                cmds, evs = build(pg)
                steps.append((a, t, str(pg.info), str(pg.keepAmount), PURSE.get(US, "none") if st[1] != "none" else "none", bank,
                              sets_of(cmds), evs))
                if a == "amount" and k == "new":
                    check((PURSE.get(US, "none"), bank) == before, "E. %s: Enter (amount %r) moved coins" % (st[0], t))
                if k == "new":
                    check_new_build("E. %s after %s %r" % (st[0], a, t), st, str(pg.info), cmds, bank if isinstance(bank, int) else None)
                    for typ, sel, text, data in cmds:
                        if sel and sel.endswith(".Text"):
                            SEEN.setdefault(sel[1:-5], set()).add(set_text(cmds, sel[1:-5]))
            trace[k] = steps
        for so, sn in zip(trace["old"], trace["new"]):
            check(so == sn, "E. %s: after %s %r: %s %s | %s %s" % (st[0], so[0], so[1], OLD_VERSION, so[2:6], VERSION, sn[2:6]))
        moved = [s for s in trace["new"] if s[2].startswith("+")]
        tally("E moves", len(moved))
    COUNT["E clicks"] = n_clicks
    print("E. %d clicks (4 states x %d clicks x 2 jars), %d coin moves, identical result / amount box / purse / bank / page; "
          "Enter alone moved nothing" % (n_clicks, len(CLICKS), COUNT.get("E moves", 0)))

    # ---------------- F. text fit (the client's font tables, read-only), every box read back out of the 0.1.5 markup
    F = fonts()
    page = FIRST.get("new", [])
    EL = []                                # (parent id, type, id, own) of every element of the built page, in order
    for parent, r in page:
        els = elements(r)
        for typ, ident, own, up in els:
            EL.append((parent if up is None else els[up][1], typ, ident, own))
    BY_ID = dict((i, (p, t, o)) for p, t, i, o in EL if i)

    def box_w(ident):
        """the width an element's content gets: its Width, else its parent's content width minus its own margins; minus Padding"""
        p, _t, own = BY_ID[ident]
        a, pd = own_anchor(own), own_padding(own)
        w = a["Width"] if "Width" in a else box_w(p) - hsum(dict((k, v) for k, v in a.items() if k != "Width" and k != "Height"))
        return w - hsum(pd)

    def content_w(parent, own):
        a, pd = own_anchor(own), own_padding(own)
        w = a["Width"] if "Width" in a else box_w(parent) - hsum(dict((k, v) for k, v in a.items() if k not in ("Width", "Height")))
        return w - hsum(pd)

    if F is None:
        print("F. skipped: no client font tables in", FONT_DIR)
    elif not page:
        check(False, "F. no 0.1.5 page was built")
    else:
        lh = F["regular"][1]
        n_fit, FIT, worst = 0, [], {}
        for parent, typ, ident, own in EL:
            size = own_font(own)
            bold = "RenderBold: true" in own
            upper = "RenderUppercase: true" in own
            if typ == "TextButton":
                a, pd = own_anchor(own), own_padding(own)
                text = own_text(own)
                tw = text_w(F, text.upper() if upper else text, size, True)
                room = a["Width"] - hsum(pd)
                n_fit += 1
                tally("F buttons")
                check(tw <= room, "F. button #%s %r: %.1f px of label, %d px of room" % (ident, text, tw, room))
                FIT.append("%s %.0f/%d" % (text, tw, room))
                continue
            if typ == "TextField":
                room = content_w(parent, own)
                for t in ["Amount"] + [kp for _i, kp in MARKS] + [t for _a, t in CLICKS]:
                    n_fit += 1
                    check(text_w(F, t, size, False) <= room, "F. #%s %r at %d px in %d px" % (ident, t, size, room))
                continue
            if typ != "Label":
                continue
            texts = set([own_text(own)] if own_text(own) else []) | set(t for t in SEEN.get(ident, ()) if t)
            if not texts:
                continue
            room = content_w(parent, own)
            h = own_anchor(own).get("Height")
            for t in texts:
                n_fit += 1
                t2 = t.upper() if upper else t
                if "Wrap: true" in own:
                    nl = wrap_lines(F, t2, size, bold, room)
                    worst[ident or t] = max(worst.get(ident or t, 0), nl)
                    check(nl * size * lh <= h, "F. #%s wraps to %d lines of %d px (%.1f px) in a %d px box: %r" % (
                        ident, nl, size, nl * size * lh, h, t))
                else:
                    check(text_w(F, t2, size, bold) <= room, "F. %s one line %r: %.0f px > %d px" % (
                        "#" + ident if ident else "label", t, text_w(F, t2, size, bold), room))
        check(COUNT.get("F buttons", 0) == 6, "F. 6 buttons measured (%d)" % COUNT.get("F buttons", 0))
        two = K["BANK_TWO_LINES"]
        for ident in ("SkyyBSub", "SkyyBInfo"):
            sz = own_font(BY_ID[ident][2])
            check(2 * sz * lh <= two and worst.get(ident, 0) <= 2, "F. #%s: two %d px lines (%.1f px) fit %d px; most lines %d" % (
                ident, sz, 2 * sz * lh, two, worst.get(ident, 0)))
        COUNT["F texts"] = n_fit
        print("F. text fit: %d buttons and texts measured (NunitoSans, line height %.3f); two-line boxes %.1f of %d px; most lines: %s"
              % (n_fit, lh, 2 * own_font(BY_ID["SkyyBSub"][2]) * lh, two,
                 dict((k, v) for k, v in worst.items() if k in ("SkyyBSub", "SkyyBInfo"))))
        print("   button labels (px of label / px of room): " + ", ".join(FIT))

    # ---------------- G. the page id
    pid, chk = K["BANK_PAGE_ID"], K["BANK_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready log line names the page the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW))
    check(pid == chk, "G. the page the kit makes now (%s) is the checked page BANK_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/bank_0_1_5_patch.py, regenerate and rebuild" % (pid, chk, pid))
    kit_in_log = SUI.kit_id() in LOG_NEW
    COUNT["G"] = (pid, chk, SUI.kit_id(), kit_in_log)
    print("G. page id %s, checked %s, kit %s%s" % (pid, chk, SUI.kit_id(), "" if kit_in_log else " (the jar was built on another kit file)"))

    # ---------------- H. Skyy's two asks: the row order + captions, and ~10% bigger (from the BUILT pages of both jars)
    if not page:
        check(False, "H. no 0.1.5 page was built")
        return

    def spans(pairs, row):
        out, x = [], 0
        for p, r in pairs:
            if p != row:
                continue
            typ, ident, own, _up = elements(r)[0]
            a = own_anchor(own)
            x0 = x + a.get("Left", 0)
            out.append((ident, x0, x0 + a["Width"]))
            x = x0 + a["Width"] + a.get("Right", 0)
        return out

    want_order = ["SkyyBDepAll", "SkyyBDep", "SkyyBAmtBox", "SkyyBWd", "SkyyBWdAll"]
    ctl_new, ctl_old = spans(page, "SkyyBCtl"), spans(FIRST["old"], "SkyyBCtl")
    check([i for i, _a, _b in ctl_old] == ["SkyyBDepAll", "SkyyBAmtBox", "SkyyBDep", "SkyyBWd", "SkyyBWdAll"],
          "H. the 0.1.4 row is Deposit all | Amount | Deposit | Withdraw | Withdraw all: %s" % ctl_old)
    check([i for i, _a, _b in ctl_new] == want_order, "H. the 0.1.5 row is Deposit all | Deposit | Amount | Withdraw | Withdraw all: %s"
          % [i for i, _a, _b in ctl_new])
    at = dict((i, (a, b)) for i, a, b in ctl_new)
    caps = spans(page, "SkyyBCap")
    cap_want = [at["SkyyBDepAll"], (at["SkyyBDep"][0], at["SkyyBWd"][1]), at["SkyyBWdAll"]]
    check([(a, b) for _i, a, b in caps] == cap_want, "H. each caption spans its controls: %s vs %s" % (caps, cap_want))
    cap_texts = [own_text(elements(r)[0][2]) for p, r in page if p == "SkyyBCap"]
    check(cap_texts == ["your whole purse", "", "your whole bank"] and caps[1][0] == "SkyyBCapMid",
          "H. captions: your whole purse | #SkyyBCapMid | your whole bank: %s" % cap_texts)
    root_old, root_new = own_anchor(elements(FIRST["old"][0][1])[0][2]), own_anchor(elements(page[0][1])[0][2])
    tall = root_new["Height"] - SUI.DECO_TOP - SUI.DECO_BOTTOM
    check(root_new["Height"] <= SUI.MAX_PAGE_H and tall <= 1080, "H. the page is %d px high, %d px with the ornaments (<= %d / 1080)"
          % (root_new["Height"], tall, SUI.MAX_PAGE_H))
    so, sn = sized(FIRST["old"]), sized(page)
    FIXED = {("SkyyBankFBar", "Height"), ("SkyyBankFTitle", "FontSize")}      # the vanilla title bar texture and its title
    n_size, off = 0, []
    RATIOS = []
    for key in sorted(set(so) & set(sn)):
        for prop in ("Width", "Height", "FontSize", "Pad"):
            a, b = so[key][prop], sn[key][prop]
            if a is None and b is None:
                continue
            n_size += 1
            if a is None or b is None:
                off.append("%s.%s %s -> %s" % (key, prop, a, b))
                continue
            if (key, prop) in FIXED or (prop == "FontSize" and sn[key]["type"] == "TextButton"):
                if a != b:
                    off.append("%s.%s %s -> %s (must stay vanilla)" % (key, prop, a, b))
                continue
            RATIOS.append(float(b) / a)
            if not (SIZE_RATIO[0] <= float(b) / a <= SIZE_RATIO[1]):
                off.append("%s.%s %s -> %s (x %.3f)" % (key, prop, a, b, float(b) / a))
    check(not off, "H. every sized element %.2f - %.2f x its 0.1.4 size: %s" % (SIZE_RATIO[0], SIZE_RATIO[1], off))
    check(set(so) == set(sn), "H. the same sized elements: %s" % sorted(set(so) ^ set(sn)))
    COUNT["H sizes"] = n_size
    print("H. row %s, captions under their controls; page %d x %d (0.1.4 %d x %d), %d px with the ornaments; %d sizes compared, "
          "scaled ones x %.3f - %.3f" % (" | ".join(i for i, _a, _b in ctl_new), root_new["Width"], root_new["Height"],
                                          root_old["Width"], root_old["Height"], tall, n_size, min(RATIOS), max(RATIOS)))
    fonts_new = sorted(set((sn[k]["type"], sn[k]["FontSize"]) for k in sn if sn[k]["FontSize"]))
    print("   font sizes 0.1.5: %s" % ", ".join("%s %d" % t for t in fonts_new))


def main():
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    os.makedirs(SCRATCH, exist_ok=True)
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
    print("SkyyBank %s page harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
