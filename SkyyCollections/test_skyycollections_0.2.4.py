"""Bare-JVM page harness for SkyyCollections 0.2.4 - the look-only restyle of the /collections page (CollPage) on the shared UI kit
tools/skyyui.py. Committed next to the build so the build docstring's CHECKED claims can be re-run instead of trusted; copy it to the
next version and keep it passing. Modelled on SkyyBank/test_skyybank_0.1.4.py (the pilot's harness).

    python SkyyCollections/test_skyycollections_0.2.4.py [--jar <SkyyCollections-0.2.4.jar>] [--old <SkyyCollections-0.2.3.jar>]
                                                         [--dir <scratch>] [--keep]

Build first: python tools/coll_0_2_4_patch.py, then python SkyyCollections/build_skyycollections_0.2.4.py - and, on a fresh checkout,
python SkyyCollections/build_skyycollections_0.2.3.py too (jars are git-ignored; --old needs SkyyCollections-0.2.3.jar). One JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; EACH SkyyCollections jar in its own class
loader, so 0.2.3 - the live SET pin - and 0.2.4 run side by side in one process) checks:
  A  every class of both jars loads, verifies and initialises
  B  the restyle contract in bytes: the same class names; every class but CollPage is byte-identical to 0.2.3 once its differing
     CONSTANT_Utf8 entries are swapped back, and every such entry is the version string (0.2.3 -> 0.2.4: the config kit classes) or
     the ready log line (SkyyCollectionsPlugin: + the kit id and the page id); CollPage (javassist, constant-pool indices resolved):
     0.2.3's fields + the static CATOPEN / CATBACK, the constructor / bind / closePage / handleDataEvent / openFor instruction-identical
     (constants compared by value: ldc / ldc_w and the offsets that follow from the bigger constant pool are normalised),
     bs / btn / lab / sp / bar / icon gone, statusColor (+ <clinit>) new, only the page methods changed
  C  statusColor on every CollBypass result text (success green / info blue / error red) and on "" (info blue)
  D  differential page builds, 0.2.3 vs 0.2.4, with the engine's own UICommandBuilder / UIEventBuilder, a PlayerRef allocated without
     a constructor and the real registry (collections / rewards / config files written by CollReg.loadAll into the scratch folder;
     the recipe table filled like CollReg.validate without the asset stores): the error views (no registry, an unreadable counts
     file), home (empty / mixed / all maxed), every category x its pages (+ a page number past the end), collection views (every
     tier state, bought tiers, maxed, undiscovered, no icon, coin unlocks off, bags free, bagMax none / legendary, a 20-tier curve, a
     hidden collection falling back to home), unlocked recipes (none / some / exactly 40 / 57 lines), and every result text on the
     status line. Per build: identical event bindings (type, selector, EventData, lock flag, order), identical page state after the
     build (view, cat, pageNo, coll, status, cards[12]); every 0.2.3 element id still created; every 0.2.3 text still shown (inline
     or b.set; 0.2.3's inline texts went through safe()) AND, per element id, the same text in the same id (no text where 0.2.3
     showed none) - except the two
     declared moves: #SkyyCCard<n> held the collection name and says "Open" now (the name must be in #SkyyCCd<n>Nm), #SkyyCBuy held
     "Buy tier .. unlocks - .. coins" and says "Buy" now (that text must be in #SkyyCBuyLbl); the 0.2.4 markup: SUI.check_markup on every append (the root as a page
     root), SUI.check_page on the page, SUI.assert_proven (no FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Center, Right,
     Full, nothing UNVERIFIED), no underscore ids, only kit / rarity / data colours, the root 1120 x 826, and a layout model from the
     concrete markup: the body's children fill it exactly and every fixed LayoutMode Left row / Top column holds its children
  E  clicks through handleDataEvent (the real page method; its rebuild() / close() fail harmlessly outside a server and are caught by
     the page itself) in scripted sequences on both jars: identical page state, purse, bought tier, saved counts file and bypass.log
     after every click, and an identical rebuilt page (bindings, ids, texts) - including the two-click coin buy, a refused buy (not
     enough coins) and the pager at its ends
  F  text fit with the client's font tables (skyyui.text_width / text_lines, read-only; skipped without the client): every static
     button label fits its button, and every text 0.2.4 shows fits its label (one line: its width; wrapped: its lines x the line height);
     it prints the widest tier rewards text against its one-line cell (the build docstring's width budget)
  G  the page id: COLL_PAGE_ID of the kit's page NOW == COLL_PAGE_CHECKED in the generated script == the page id in the jar's ready line
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the page, the textures / sounds, the real
PageManager, rebuild() and close() on a live page, the TopScrolling tier list on this client.
Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/test-coll024, deleted at the end
unless --keep; TEMP / TMP and java.io.tmpdir point into it). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.4", "0.2.3"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "test-coll024")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)))
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
    """Run the generated script's COLL PAGE block (its constants, coll_* functions, the page sources and the page id) on the CURRENT
    kit, without the rest of the build: returns (SUI, namespace)."""
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


def safe(t):
    """CollUtil.safe (0.2.3 put its inline texts through it)"""
    for a, b in ((":", " "), (";", " "), (",", " "), ("{", "("), ("}", ")"), ('"', " "), ("\\", " "), ("\n", " ")):
        t = t.replace(a, b)
    return t


# ------------------------------------------------------------------------------------------------ markup helpers (concrete markup)
TEXT_RE = re.compile(r'(?<![A-Za-z])Text: "((?:[^"\\]|\\.)*)"')
ID_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{")
OWN_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{([^{}]*)")      # an element's id and its own properties (up to its first child)
# the two 0.2.3 ids whose text moved (declared in the build docstring): id pattern -> (the 0.2.4 text, the id that shows the old text)
MOVED = [(re.compile(r"SkyyCCard(\d+)"), "Open", lambda m: "SkyyCCd%sNm" % m.group(1)),
         (re.compile(r"SkyyCBuy"), "Buy", lambda m: "SkyyCBuyLbl")]


def own_props(mk):
    """(type, id, own property text) of a markup's outer element (the text before its first child)."""
    m = re.match(r"\s*([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9]+))?\s*\{([^{}]*)", mk)
    return (m.group(1), m.group(2), m.group(3)) if m else (None, None, "")


def anchor_of(own):
    m = re.search(r"Anchor: \(([^)]*)\)", own)
    return dict((k, int(v)) for k, v in re.findall(r"(Width|Height|Left|Right|Top|Bottom|Horizontal|Vertical|Full): (-?\d+)",
                                                   m.group(1))) if m else {}


def padding_of(own):
    m = re.search(r"Padding: \(([^)]*)\)", own)
    return dict((k, int(v)) for k, v in re.findall(r"(Left|Right|Top|Bottom|Horizontal|Vertical|Full): (\d+)", m.group(1))) if m else {}


def inner(own):
    """(inner width, inner height) of a fixed-size container (None where it sets no Width / Height)."""
    a, p = anchor_of(own), padding_of(own)
    w = a["Width"] - p.get("Left", 0) - p.get("Right", 0) - 2 * (p.get("Horizontal", 0) + p.get("Full", 0)) if "Width" in a else None
    h = a["Height"] - p.get("Top", 0) - p.get("Bottom", 0) - 2 * (p.get("Vertical", 0) + p.get("Full", 0)) if "Height" in a else None
    return w, h


def outer(own):
    a = anchor_of(own)
    hm = a.get("Left", 0) + a.get("Right", 0) + 2 * (a.get("Horizontal", 0) + a.get("Full", 0))
    vm = a.get("Top", 0) + a.get("Bottom", 0) + 2 * (a.get("Vertical", 0) + a.get("Full", 0))
    return (a["Width"] + hm if "Width" in a else None), (a["Height"] + vm if "Height" in a else None)


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
    print("A. loaded + verified + initialised: 0.2.3 %d, 0.2.4 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. the restyle contract in bytes
    old, new = CB["old"], CB["new"]
    check(sorted(old) == sorted(new), "B. the same class names: %s" % sorted(set(old) ^ set(new)))
    page_c, plug_c = PKG + "CollPage", PKG + "SkyyCollectionsPlugin"
    LOG_NEW = ""
    swapped_kinds = {}
    for n in sorted(old):
        if n == page_c or n not in new:
            continue
        if old[n] == new[n]:
            tally("B identical")
            continue
        co, cn = cp_utf8(old[n]), cp_utf8(new[n])
        if not check(len(co) == len(cn), "B. %s: a different number of Utf8 constants" % n):
            continue
        rebuilt, ok = new[n], True
        for (s0, e0, t0), (s1, e1, t1) in reversed(list(zip(co, cn))):
            if t0 == t1:
                continue
            a, b = t0.decode("utf8"), t1.decode("utf8")
            if a.replace("0.2.3", "0.2.4") == b:
                swapped_kinds.setdefault(n, []).append("version")
            elif n == plug_c and a.startswith("[SkyyCollections] 0.2.3 ready - "):
                m = re.fullmatch(r"\[SkyyCollections\] 0\.2\.4 ready \((skyyui [0-9.]+ [0-9a-f]{12}), page ([0-9a-f]{12})\) - (.*)", b, re.S)
                ok = check(m is not None and m.group(3) == a[len("[SkyyCollections] 0.2.3 ready - "):],
                           "B. the 0.2.4 ready line = 0.2.3's + the kit id and the page id: %r" % b[:120]) and ok
                LOG_NEW = b
                swapped_kinds.setdefault(n, []).append("ready line")
            else:
                ok = check(False, "B. %s: an unexplained constant change %r -> %r" % (n, a[:80], b[:80])) and ok
            rebuilt = rebuilt[:s1] + old[n][s0:e0] + rebuilt[e1:]
        if check(rebuilt == old[n], "B. %s = 0.2.3's bytes once its version / ready constants are swapped back" % n) and ok:
            tally("B swapped")
    check(bool(LOG_NEW), "B. the ready log constant was found in SkyyCollectionsPlugin")
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
        # instruction-identical MODULO the constant-pool numbering: a class with a bigger pool may load the same constant with
        # ldc_w instead of ldc (3 bytes, not 2), which shifts every later offset - so the constants are compared by value,
        # ldc_w reads as ldc and branch targets / exception ranges as instruction indices
        it, rows = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            rows.append((pos, re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp)))))
        idx = dict((p, i) for i, (p, _t) in enumerate(rows))
        idx[int(ca.getCodeLength())] = len(rows)
        out = []
        for _p, t in rows:
            t = re.sub(r"^ldc_w ", "ldc ", t)
            m = re.match(r"^(if\w*|goto(?:_w)?|jsr(?:_w)?) (\d+)$", t)
            if m:
                t = "%s @%d" % (m.group(1), idx[int(m.group(2))])
            if "switch" in t:
                t = "SWITCH " + t                  # (no switch in the compared methods; kept verbatim if one appears)
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

    po, pn = ct(old[page_c]), ct(new[page_c])
    fo = sorted((str(f.getName()), str(f.getSignature())) for f in po.getDeclaredFields())
    fn = sorted((str(f.getName()), str(f.getSignature())) for f in pn.getDeclaredFields())
    check(all(f in fn for f in fo) and sorted(set(fn) - set(fo)) == [("CATBACK", "[Ljava/lang/String;"), ("CATOPEN", "[Ljava/lang/String;")],
          "B. CollPage fields: 0.2.3's + CATOPEN / CATBACK: %s" % sorted(set(fn) ^ set(fo)))
    check(str(po.getClassFile().getSuperclass()) == str(pn.getClassFile().getSuperclass()), "B. CollPage superclass unchanged")
    mo, mn = methods(po), methods(pn)
    gone = sorted(k.split("(")[0] for k in mo if k not in mn)
    added = sorted(k.split("(")[0] for k in mn if k not in mo)
    changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
    same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
    check(gone == ["bar", "bs", "btn", "icon", "lab", "sp"], "B. CollPage: only the markup helpers are gone: %s" % gone)
    check(added == ["<clinit>", "statusColor"], "B. CollPage: only statusColor (+ the static field initialiser) is new: %s" % added)
    check(changed == sorted(["build", "buildCat", "buildDetail", "buildHome", "buildRecipes", "card", "catCard"]),
          "B. CollPage: only the page methods changed: %s" % changed)
    for keep in ("<init>", "bind", "closePage", "handleDataEvent", "openFor"):
        check(keep in same, "B. CollPage.%s is instruction-identical to 0.2.3" % keep)
    COUNT["B page"] = (same, changed, gone, added)
    print("B. %d classes byte-identical, %d identical once version / ready constants are swapped back (%s); CollPage: identical %s, "
          "changed %s, gone %s, new %s" % (COUNT.get("B identical", 0), COUNT.get("B swapped", 0),
                                           ", ".join("%s: %s" % (n.split(".")[-1], "/".join(sorted(set(v)))) for n, v in sorted(swapped_kinds.items())),
                                           same, changed, gone, added))

    # ---------------- common Java objects
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    JLong, HashMap, JString = JClass("long"), JClass("java.util.HashMap"), JClass("java.lang.String")
    System = JClass("java.lang.System")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    def pfield(name):
        f = PR.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    # ---------------- C. statusColor on every result text
    COL = SUI.COLOR
    Pn = jc("new", "CollPage")
    STATUS_SAMPLES = [("", COL["info"]), ("Your collections could not be read right now.", COL["error"]),
                      ("Click Buy again within 10 s to pay 1,500 coins for the tier III unlocks of Wheat.", COL["info"]),
                      ("Coin unlocks need SkyyCoins, which is not loaded.", COL["error"]),
                      ("You need 1,500 coins in your purse.", COL["error"]),
                      ("Could not save the purchase - your coins were refunded.", COL["error"]),
                      ("Could not save the purchase and the refund failed - tell an admin (bypass.log).", COL["error"]),
                      ("Bought the tier III unlocks of Wheat for 1,500 coins. Gather to tier III for its coins and XP.", COL["success"]),
                      ("Coin unlocks are turned off on this server.", COL["error"]), ("Collections are not loaded.", COL["error"]),
                      ("Coin unlocks are not available for this collection.", COL["error"]),
                      ("Collect one first - coin unlocks need a discovered collection.", COL["error"]),
                      ("Every tier is unlocked.", COL["error"]),
                      ("Coin unlocks are not available for Elite collections - gather it.", COL["error"]),
                      ("Tier VI must be gathered - coins unlock up to tier V here.", COL["error"]),
                      ("Nothing more here can be bought with coins - gather it.", COL["error"])]
    for t, want in STATUS_SAMPLES:
        got = str(Pn.statusColor(t))
        check(got == want, "C. statusColor(%r) = %s, want %s" % (t[:40], got, want))
    check(str(Pn.statusColor(None)) == COL["info"], "C. statusColor(null) = the info blue")
    print("C. statusColor: %d result texts + null" % len(STATUS_SAMPLES))

    # ---------------- the world: registry, recipe table, bridge, counts
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    PURSE = {}

    @JImplements("java.util.function.Function")
    class CoinsTake:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            have = PURSE.get(u, 0)
            if have < n:
                return Boolean.FALSE
            PURSE[u] = have - n
            return Boolean.TRUE

    @JImplements("java.util.function.Function")
    class CoinsAdd:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            PURSE[u] = PURSE.get(u, 0) + n
            return Long.valueOf(PURSE[u])

    COINS = (CoinsTake(), CoinsAdd())
    UID = UUID.fromString("00000000-0000-0000-0000-0000000000c0")
    US = str(UID)

    def pref():
        p = U.allocateInstance(PR.class_)
        pfield("uuid").set(p, UID)
        return p

    REG = {}          # per jar: the Java objects; plus "info" = the registry read back once (both jars write the same files)

    def world(k):
        """CollReg.loadAll into scratch/<k>/base (the default files), the recipe table from the rewards table (validate() without
        the asset stores), every icon marked a game item except each 7th collection."""
        Reg, Store = jc(k, "CollReg"), jc(k, "CollStore")
        base = os.path.join(SCRATCH, "world", k)
        shutil.rmtree(base, ignore_errors=True)
        os.makedirs(base)
        Reg.BASE = Paths.get(base)
        Store.DIR = Paths.get(base).resolve("counts")
        msg = str(Reg.loadAll())
        R = Reg.D
        rec = HashMap()
        for c in range(R.n):
            mx = int(Reg.maxTier(R, c))
            for t in range(1, mx + 1):
                toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
                if toks is None:
                    continue
                ids = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
                if ids:
                    rec.put("%d.%d" % (c, t), JArray(JString)(ids))
        Reg.RECIPES = rec
        Reg.VALIDATED = True
        for c in range(R.n):
            R.iconOk[c] = (c % 7) != 3
        REG[k] = (Reg, Store, R, rec, msg)

    for k in ("old", "new"):
        world(k)
    Reg0, _s, R0, REC0, MSG0 = REG["old"]
    INFO = [dict(id=str(R0.id[c]), cat=int(R0.cat[c]), name=str(R0.name[c]), item=str(R0.items[c][0]), curve=int(R0.curve[c]),
                 hidden=bool(R0.hidden[c]), mx=int(Reg0.maxTier(R0, c)), thr=[int(Reg0.threshold(R0, c, t)) for t in range(1, int(Reg0.maxTier(R0, c)) + 1)])
            for c in range(R0.n)]
    check(MSG0 == REG["new"][4], "D. both jars read the same registry: %s / %s" % (MSG0, REG["new"][4]))
    BYID = dict((x["id"], i) for i, x in enumerate(INFO))
    print("   registry: %s; %d recipe tiers" % (MSG0, REC0.size()))
    DEF = {"BYPASS": True, "BYP_BAGMAX": 2}

    def profile(name):
        """{collection index: (count, bought tier)} for a data profile."""
        out = {}
        if name == "empty":
            return out
        for cat in range(4):
            idx = [c for c, x in enumerate(INFO) if x["cat"] == cat and not x["hidden"]]
            for j, c in enumerate(idx):
                x = INFO[c]
                if name == "maxall":
                    out[c] = (x["thr"][-1], 0)
                    continue
                r = j % 6
                if r == 0:
                    continue                                              # undiscovered
                out[c] = [(1, 0), (x["thr"][2], 0), (x["thr"][-1], 0), (x["thr"][0] + 5, 3), (x["thr"][1], 1)][r - 1]
        if name == "mixed":
            for cid, cnt, bt in (("Wheat", 60, 2), ("Iron", 30, 0), ("OakLog", 300, 4), ("Bone", 0, 0), ("Cobblestone", 1, 0)):
                if cid in BYID:
                    out[BYID[cid]] = (cnt, bt)
        return out

    def setup(k, prof, broken=False, noreg=False, cfg=None, bridge=None, thr20=False, extra_rec=0):
        Reg, Store, R, rec, _m = REG[k]
        Store.DATA.clear()
        Store.BROKEN.clear()
        Store.DIRTY.clear()
        jc(k, "CollBypass").ARM.clear()
        BR.clear()
        BR.put("coins:fn:take", COINS[0])
        BR.put("coins:fn:add", COINS[1])
        for kk, v in (bridge or {}).items():
            BR.put(kk, v)
        cd = os.path.join(SCRATCH, "world", k, "counts")
        shutil.rmtree(cd, ignore_errors=True)
        os.makedirs(cd)
        for kk, v in dict(DEF, **(cfg or {})).items():
            setattr(Reg, kk, v)
        R.thr[0] = JArray(JLong)([10 * (i + 1) for i in range(20)] if thr20 else [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000])
        newrec = HashMap(rec)
        for c in range(min(extra_rec, R.n)):
            newrec.put("%d.1" % c, JArray(JString)(["Skyy_Test_Extra_%d_Recipe_Generated_0" % c] + list(rec.get("%d.1" % c) or [])))
        Reg.RECIPES = newrec
        Reg.D = None if noreg else R
        if broken:
            os.makedirs(os.path.join(cd, US + ".properties"))                  # a counts "file" that cannot be read
            return
        lines = ["_schema=2"]
        for c, (cnt, bt) in sorted(prof.items()):
            if cnt > 0:
                lines.append("%s=%d" % (INFO[c]["item"], cnt))
            if bt > 0:
                lines.append("_bought.%s=%d" % (INFO[c]["id"], bt))
        open(os.path.join(cd, US + ".properties"), "w").write("\n".join(lines) + "\n")

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    def appends_of(cmds):
        return [(None if sel is None else sel.lstrip("#"), text) for typ, sel, text, data in cmds if "append" in typ.lower()]

    def sets_of(cmds):
        out = []
        for typ, sel, text, data in cmds:
            if "append" in typ.lower() or not sel or not sel.endswith(".Text"):
                continue
            d = json.loads(data)
            out.append((sel[1:-5], d.get("0") if isinstance(d, dict) else d))
        return out

    def state_of(pg):
        return (int(pg.view), int(pg.cat), int(pg.pageNo), int(pg.coll), None if pg.status is None else str(pg.status),
                [int(x) for x in pg.cards])

    def texts(cmds, inline_safe):
        """every text the page shows: inline Text values (0.2.3's went through safe()) + the b.set .Text values (non-empty)"""
        out = set()
        for p, t in appends_of(cmds):
            for m in TEXT_RE.finditer(t):
                if m.group(1):
                    out.add(m.group(1))
        for ident, v in sets_of(cmds):
            if v:
                out.add(v)
        return out

    def ids_of(cmds):
        return set(i for _p, t in appends_of(cmds) for i in ID_RE.findall(t))

    def id_texts(cmds):
        """element id -> the text it shows after the build: its own inline Text (None without one), then its last b.set .Text"""
        out = {}
        for _p, t in appends_of(cmds):
            for m in OWN_RE.finditer(t):
                tm = TEXT_RE.search(m.group(2))
                out[m.group(1)] = tm.group(1) if tm else None
        for ident, v in sets_of(cmds):
            out[ident] = v
        return out

    def same_text(old_t, new_t):
        return new_t is not None and (new_t == old_t or safe(new_t) == old_t)

    def compare_ids(tag, co, cn):
        """per element id: every 0.2.3 id shows the same text in 0.2.4 (none where it showed none), except the two MOVED ids (their
        0.2.4 text is fixed and their 0.2.3 text must be in the named 0.2.4 id)"""
        to, tn = id_texts(co), id_texts(cn)
        for ident in sorted(to):
            old_t = to[ident]
            tally("D id texts")
            if not old_t:
                check(not tn.get(ident), "D. %s: #%s showed no text in 0.2.3, 0.2.4 shows %r" % (tag, ident, tn.get(ident)))
                continue
            mv = [(m, txt, where) for rx, txt, where in MOVED for m in [rx.fullmatch(ident)] if m]
            if mv:
                m, txt, where = mv[0]
                tally("D id texts moved")
                check(tn.get(ident) == txt, "D. %s: #%s shows %r, want %r (declared move)" % (tag, ident, tn.get(ident), txt))
                check(same_text(old_t, tn.get(where(m))), "D. %s: 0.2.3's #%s text %r is not in #%s (%r)"
                      % (tag, ident, old_t, where(m), tn.get(where(m))))
            else:
                check(same_text(old_t, tn.get(ident)), "D. %s: #%s shows %r in 0.2.4, 0.2.3 showed %r" % (tag, ident, tn.get(ident), old_t))

    NEWTEXTS = set()                           # the texts 0.2.4 shows that 0.2.3 did not (digits folded), reported in D
    ALLOWED = set(SUI.allowed_colors()) | set(SUI.norm_color(c) for c in K["UI_DATA_COLORS"])
    SEEN = []                                  # (label id, text) of every 0.2.4 text, for F
    LABELS = {}                                # label id -> (markup, parent) as last seen

    def check_new(tag, cmds):
        """0.2.4 markup rules and the layout model on one concrete build."""
        aps = appends_of(cmds)
        if not check(aps and aps[0][0] is None, "D. %s: the first append is the page root" % tag):
            return
        for i, (p, t) in enumerate(aps):
            try:
                SUI.check_markup(t, prefix=K["COLL_PREFIX"], root=(p is None))
                tally("D markups")
            except ValueError as e:
                check(False, "D. %s: check_markup: %s: %s" % (tag, e, t[:120]))
            check(all("_" not in x for x in ID_RE.findall(t)), "D. %s: underscore in an id" % tag)
            for c in re.findall(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?(?:\([0-9.]+\))?", re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)):
                check(SUI.norm_color(c) in ALLOWED, "D. %s: colour %s is no kit / rarity / data colour" % (tag, c))
            for m in re.finditer(r"Label #([A-Za-z0-9]+) \{[^{}]*\}", t):
                LABELS[m.group(1)] = (m.group(0), p)
        whole = SUI.Appends(aps)
        whole.sets = [(i, "Text", v) for i, v in sets_of(cmds)]
        try:
            SUI.check_page(whole, prefix=K["COLL_PREFIX"])
            tally("D pages")
        except ValueError as e:
            check(False, "D. %s: check_page: %s" % (tag, e))
        try:
            SUI.assert_proven([t for _p, t in aps], what=tag)
        except ValueError as e:
            check(False, "D. %s: %s" % (tag, e))
        root = own_props(aps[0][1])
        check(anchor_of(root[2]) == {"Width": K["COLL_W"], "Height": K["COLL_H"]}, "D. %s: the root is %s" % (tag, anchor_of(root[2])))
        # the layout model: the body filled exactly, every fixed Left row / Top column holds its appended children
        kids = {}
        own = {}
        for p, t in aps:
            typ, ident, props = own_props(t)
            if ident:
                own[ident] = props
            if p is not None:
                kids.setdefault(p, []).append(props)
        for cid, props in own.items():
            if inner(props)[0] is not None:
                PARENT_W[cid] = inner(props)[0]
            elif cid == K["COLL_SHELL"].body:
                PARENT_W[cid] = K["COLL_IW"]
            lay = re.search(r"LayoutMode: (Left|Top);", props)
            if not lay or cid not in kids:
                continue
            iw, ih = inner(props)
            if cid == K["COLL_SHELL"].body:
                ih = K["COLL_IH"]
            axis = 0 if lay.group(1) == "Left" else 1
            room = iw if axis == 0 else ih
            if room is None:
                continue
            sizes = [outer(k)[axis] for k in kids[cid]]
            if None in sizes:
                check(False, "D. %s: #%s has a child without a fixed %s" % (tag, cid, "Width" if axis == 0 else "Height"))
                continue
            if cid == K["COLL_SHELL"].body:
                check(sum(sizes) == room, "D. %s: the body holds %d px of %d" % (tag, sum(sizes), room))
            else:
                check(sum(sizes) <= room, "D. %s: #%s holds %d px of %d" % (tag, cid, sum(sizes), room))
            tally("D layout")
        for ident, v in sets_of(cmds):
            if v:
                SEEN.append((ident, v))

    def compare(tag, res):
        (co, eo, so), (cn, en, sn) = res["old"], res["new"]
        check(eo == en, "D. %s: event bindings differ:\n  0.2.3 %s\n  0.2.4 %s" % (tag, eo, en))
        check(so == sn, "D. %s: page state after build differs: %s / %s" % (tag, so, sn))
        miss = sorted(ids_of(co) - ids_of(cn))
        check(not miss, "D. %s: 0.2.3 ids missing in 0.2.4: %s" % (tag, miss))
        to, tn = texts(co, True), texts(cn, False)
        tn_all = tn | set(safe(x) for x in tn)
        lost = sorted(t for t in to if t not in tn_all)
        check(not lost, "D. %s: 0.2.3 texts not shown by 0.2.4: %s" % (tag, lost))
        tally("D texts", len(to))
        extra = tn - to - set(safe(x) for x in to)
        tally("D new texts", len(extra))
        NEWTEXTS.update(re.sub(r"\d", "9", x) for x in extra)
        compare_ids(tag, co, cn)
        check_new(tag, cn)

    def page(k, view=0, cat=0, page_no=0, coll=-1, status=""):
        pg = jc(k, "CollPage")(pref())
        pg.view, pg.cat, pg.pageNo, pg.coll, pg.status = view, cat, page_no, coll, status
        return pg

    def both(tag, prof, view=0, cat=0, page_no=0, coll=-1, status="", **kw):
        res = {}
        for k in ("old", "new"):
            setup(k, profile(prof) if isinstance(prof, str) else prof, **kw)
            pg = page(k, view, cat, page_no, coll, status)
            cmds, evs = build(pg)
            res[k] = (cmds, evs, state_of(pg))
        compare(tag, res)
        tally("D builds", 2)
        return res

    # ---------------- D. differential builds
    VIS = [c for c, x in enumerate(INFO) if not x["hidden"]]
    CAT_N = [len([c for c in VIS if INFO[c]["cat"] == cat]) for cat in range(4)]
    both("error: no registry", "mixed", noreg=True)
    both("error: counts unreadable", "mixed", broken=True)
    for prof in ("empty", "mixed", "maxall"):
        both("home %s" % prof, prof)
        for cat in range(4):
            pages = max(1, (CAT_N[cat] + 11) // 12)
            for pn in list(range(pages)) + [pages + 3]:
                both("cat %d page %d %s" % (cat, pn, prof), prof, view=1, cat=cat, page_no=pn)
    both("cat -1 falls back home", "mixed", view=1, cat=-1)
    both("cat 4 (Fishing) falls back home", "mixed", view=1, cat=4)
    det = sorted(set([VIS[i] for i in range(0, len(VIS), 5)] + [BYID[x] for x in ("Wheat", "Iron", "OakLog", "Bone", "Cobblestone") if x in BYID]))
    for prof in ("empty", "mixed", "maxall"):
        for c in det:
            both("detail %s %s" % (INFO[c]["id"], prof), prof, view=2, coll=c)
    wheat = BYID.get("Wheat", VIS[0])
    iron = BYID.get("Iron", VIS[1])
    for label, kw in (("coin unlocks off", {"cfg": {"BYPASS": False}}), ("bags free", {"bridge": {"sacks:freebags": Boolean.TRUE}}),
                      ("bagMax none", {"cfg": {"BYP_BAGMAX": 0}}), ("bagMax legendary", {"cfg": {"BYP_BAGMAX": 4}}),
                      ("bazaar price", {"bridge": {"bazaar:buy:" + INFO[iron]["item"]: Long.valueOf(7)}})):
        for c in (wheat, iron):
            both("detail %s %s" % (INFO[c]["id"], label), "mixed", view=2, coll=c, **kw)
    bulk = [c for c in VIS if INFO[c]["curve"] == 0]
    if bulk:
        for cnt in (0, 55, 205):
            both("detail %s 20 tiers count %d" % (INFO[bulk[0]]["id"], cnt), {bulk[0]: (cnt, 0)}, view=2, coll=bulk[0], thr20=True)
    hid = [c for c, x in enumerate(INFO) if x["hidden"]]
    if hid:
        both("detail of a hidden collection falls back home", "mixed", view=2, coll=hid[0])
    both("detail coll out of range falls back home", "mixed", view=2, coll=9999)
    for prof, extra in (("empty", 0), ("mixed", 0), ("maxall", 0), ("maxall", 60)):
        both("recipes %s +%d" % (prof, extra), prof, view=3, extra_rec=extra)
    # exactly 40 lines: add fake unlocks until the list is 40 long (0.2.3: all 40 shown, no "more" line)
    for want in (40, 41):
        setup("old", profile("maxall"))
        base_lines = None
        for extra in range(0, 120):
            setup("old", profile("maxall"), extra_rec=extra)
            pg = page("old", 3)
            cmds, _e = build(pg)
            n_lines = len([1 for i, v in sets_of(cmds) if i.startswith("SkyyCRn")]) + (1 if any(i == "SkyyCRMore" for i, v in sets_of(cmds)) else 0)
            sub = [v for i, v in sets_of(cmds) if i == "SkyyCRSub"][0]
            m = re.match(r"(\d+) recipe", sub)
            if m and int(m.group(1)) == want:
                both("recipes exactly %d lines" % want, "maxall", view=3, extra_rec=extra)
                break
    for t, _c in STATUS_SAMPLES:
        both("status %r home" % t[:30], "mixed", status=t)
        both("status %r detail" % t[:30], "mixed", view=2, coll=wheat, status=t)
    print("D. %d page builds (%d states x 2 jars): %d 0.2.4 markups in %d pages, %d layout checks, %d 0.2.3 texts all shown, %d new "
          "texts" % (COUNT.get("D builds", 0), COUNT.get("D builds", 0) // 2, COUNT.get("D markups", 0),
                                                            COUNT.get("D pages", 0), COUNT.get("D layout", 0), COUNT.get("D texts", 0),
                                                            COUNT.get("D new texts", 0)))
    print("   per-id texts: %d 0.2.3 id texts compared in the page builds, %d of them the two declared moves (#SkyyCCard<n>, #SkyyCBuy)"
          % (COUNT.get("D id texts", 0), COUNT.get("D id texts moved", 0)))
    check(COUNT.get("D id texts moved", 0) > 0, "D. the declared id-text moves were exercised")
    print("   texts 0.2.4 adds: %s" % sorted(NEWTEXTS))
    check(NEWTEXTS <= {"Open", "Buy", "State", "Tier", "Needed", "Rewards", "Collections"},
          "D. 0.2.4 shows only the new button labels / column heads / window title besides 0.2.3's texts: %s" % sorted(NEWTEXTS))

    # ---------------- E. clicks (handleDataEvent), identical on both jars
    def files(k):
        cd = os.path.join(SCRATCH, "world", k, "counts", US + ".properties")
        txt = open(cd).read() if os.path.isfile(cd) else ""
        props = sorted(ln for ln in txt.split("\n") if ln and not ln.startswith("#"))
        lg = os.path.join(SCRATCH, "world", k, "bypass.log")
        logl = [re.sub(r"^.*?  (BUY|FAILED-SAVE) ", r"\1 ", ln) for ln in open(lg).read().split("\n") if ln] if os.path.isfile(lg) else []
        return props, logl

    SEQS = [
        ("browse", "mixed", 0, [("ccat0", ""), ("cnext", ""), ("cnext", ""), ("cnext", ""), ("cprev", ""), ("cprev", ""), ("cprev", ""),
                                ("ccard0", ""), ("cback", ""), ("ccard11", ""), ("ccard5", ""), ("chome", ""), ("ccat2", ""),
                                ("cnext", ""), ("ccard3", ""), ("cback", ""), ("cback", ""), ("crecipes", ""), ("cback", ""),
                                ("crefresh", ""), ("ccat3", ""), ("ccard1", ""), ("chome", ""), ("bogus", ""), ("cclose", "")]),
        ("buy", "mixed", 5000, [("ccat0", ""), ("ccard%d" % 0, ""), ("cbuy", ""), ("cbuy", ""), ("cbuy", ""), ("crefresh", ""),
                                ("cback", ""), ("chome", "")]),
        ("buy-poor", "mixed", 10, [("ccat1", ""), ("ccard0", ""), ("cbuy", ""), ("cbuy", ""), ("chome", "")]),
    ]
    n_clicks = 0
    for name, prof, purse, seq in SEQS:
        trace = {}
        for k in ("old", "new"):
            setup(k, profile(prof))
            PURSE.clear()
            PURSE[US] = purse
            lg = os.path.join(SCRATCH, "world", k, "bypass.log")
            if os.path.isfile(lg):
                os.remove(lg)
            pg = page(k)
            steps = []
            for a, t in seq:
                pg.handleDataEvent(None, None, json.dumps({"a": a}))
                n_clicks += 1
                cmds, evs = build(pg)
                st = state_of(pg)
                steps.append((a, st, PURSE.get(US), files(k), evs, sorted(ids_of(cmds)) if k == "old" else None, cmds))
            trace[k] = steps
        for so, sn in zip(trace["old"], trace["new"]):
            a = so[0]
            check(so[1] == sn[1], "E. %s after %s: page state %s / %s" % (name, a, so[1], sn[1]))
            check(so[2] == sn[2], "E. %s after %s: purse %s / %s" % (name, a, so[2], sn[2]))
            check(so[3] == sn[3], "E. %s after %s: counts file / bypass.log differ:\n %s\n %s" % (name, a, so[3], sn[3]))
            res = {"old": (so[6], so[4], so[1]), "new": (sn[6], sn[4], sn[1])}
            compare("E. %s after %s" % (name, a), res)
        moved = [s for s in trace["new"] if s[1][4] and s[1][4].startswith("Bought the tier ")]
        tally("E buys", len(moved))
    check(COUNT.get("E buys", 0) >= 1, "E. at least one coin buy went through (%d)" % COUNT.get("E buys", 0))
    print("E. %d clicks (%d sequences x 2 jars): identical page state, purse, counts file, bypass.log and rebuilt page; %d coin buys"
          % (n_clicks, len(SEQS), COUNT.get("E buys", 0)))
    print("   per-id texts with the rebuilt pages: %d 0.2.3 id texts compared in all, %d declared moves"
          % (COUNT.get("D id texts", 0), COUNT.get("D id texts moved", 0)))

    # ---------------- F. text fit (the client's font tables through the kit, read-only)
    if not os.path.isdir(SUI.FONT_DIR):
        print("F. skipped: no client font tables in", SUI.FONT_DIR)
    else:
        bad = []
        n_fit = 0
        for mk in K["COLL_CATOPEN"] + K["COLL_CATBACK"] + [K["COLL_CLOSE"], K["COLL_HOMEB"], K["COLL_BACK"]]:
            r = SUI.render(mk)
            w = int(re.search(r"Anchor: \(Width: (\d+)", r).group(1))
            pad = int(re.search(r"Padding: \(Horizontal: (\d+)\)", r).group(1))
            text = re.search(r'Text: "([^"]*)"', r).group(1)
            tw = SUI.text_width(text, 17, bold=True, upper=True)
            n_fit += 1
            if tw > w - 2 * pad:
                bad.append("button %r %.0f > %d" % (text, tw, w - 2 * pad))
        seen = {}
        for ident, text in SEEN:
            seen.setdefault(ident, set()).add(text)
        for ident, texts_ in seen.items():
            if ident not in LABELS:
                continue
            mk, parent = LABELS[ident]
            own = mk[mk.index("{") + 1:]
            a = anchor_of(own)
            size = int(re.search(r"FontSize: (\d+)", own).group(1))
            bold = "RenderBold: true" in own
            wrap = "Wrap: true" in own
            w = a.get("Width")
            if w is None:
                w = PARENT_W.get(parent)           # a label without a Width fills its LayoutMode Top parent
            if w is None:
                continue
            w -= a.get("Left", 0) + a.get("Right", 0)
            h = a.get("Height", 0)
            for t in texts_:
                n_fit += 1
                if wrap:
                    lines = SUI.text_lines(t, w, size, bold)
                    if lines * SUI.line_height(size, bold=bold) > h + 0.5:
                        bad.append("#%s wraps to %d lines in %d px: %r" % (ident, lines, h, t))
                elif SUI.text_width(t, size, bold) > w:
                    bad.append("#%s %.0f px > %d: %r" % (ident, SUI.text_width(t, size, bold), w, t))
        COUNT["F"] = (n_fit, bad)
        check(not bad, "F. text fit (%d texts): %s" % (n_fit, bad[:12]))
        print("F. text fit: %d button labels and shown texts measured (NunitoSans), %d too wide" % (n_fit, len(bad)))
        # the one-line tier rewards cell (runtime text, fit=False at build time): its widest reachable text and its headroom
        rew = [(SUI.text_width(t, 16), t) for ident, t in SEEN if re.fullmatch(r"SkyyCRew\d+", ident)]
        if check(bool(rew), "F. tier rewards texts were seen"):
            widest = max(rew)
            cell = K["COLL_TR_SPEC"].widths[3]
            check(widest[0] <= cell, "F. the widest rewards text fits its cell: %.0f > %d: %r" % (widest[0], cell, widest[1]))
            print("   widest tier rewards text %.0f px of the %d px cell (%.0f px headroom): %r" % (widest[0], cell, cell - widest[0], widest[1]))

    # ---------------- G. the page id
    pid, chk = K["COLL_PAGE_ID"], K["COLL_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready log line names the page the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW[:120]))
    check(pid == chk, "G. the page the kit makes now (%s) is the checked page COLL_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/coll_0_2_4_patch.py, regenerate and rebuild" % (pid, chk, pid))
    kit_in_log = SUI.kit_id() in LOG_NEW
    print("G. page id %s, checked %s, kit %s%s" % (pid, chk, SUI.kit_id(), "" if kit_in_log else " (the jar was built on another kit file)"))


PARENT_W = {}      # container id -> inner width, for labels that fill their parent (filled from the kit's page constants)


def main():
    for j, how in ((JAR, "python tools/coll_0_2_4_patch.py, then python SkyyCollections/build_skyycollections_0.2.4.py"),
                   (OLD, "python SkyyCollections/build_skyycollections_0.2.3.py (jars are git-ignored)")):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first:", how)
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
    print("SkyyCollections %s page harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
