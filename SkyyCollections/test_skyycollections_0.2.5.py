"""Bare-JVM harness for SkyyCollections 0.2.5 - Skyy's rule "coins never skip collections or bags" (tools/coll_0_2_5_patch.py; OPEN-QUESTIONS
"Q&A with Skyy 2026-10-02" R3 LOCKED): coin unlocks OFF by default, the buy well hidden while off, the Server Setup row kept (it asks
before switching ON), no take-backs, and the one-time CollBypassMig update of an existing config.properties. Copied forward from
SkyyCollections/test_skyycollections_0.2.4.py (its page machinery: kit_page, the engine's UICommandBuilder / UIEventBuilder, the markup
rules and layout model, the font-table fit); committed next to the build so the build docstring's CHECKED claims can be re-run.

    python SkyyCollections/test_skyycollections_0.2.5.py [--jar <SkyyCollections-0.2.5.jar>] [--old <SkyyCollections-0.2.4.jar>]
                                                         [--live <Skyy_SkyyCollections folder>] [--dir <scratch>] [--keep]

Build first: python tools/coll_0_2_5_patch.py, then python SkyyCollections/build_skyycollections_0.2.5.py (and, on a fresh checkout,
python SkyyCollections/build_skyycollections_0.2.4.py - jars are git-ignored; --old needs SkyyCollections-0.2.4.jar = the SET pin). One
JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath); every jar in its own class
loader, a FRESH loader of the 0.2.5 jar = one server start (its static state starts empty, like a restart). The live world is READ ONLY:
its Skyy_SkyyCollections folder is copied into the scratch folder and only the copy is ever written (the harness checks the live
config.properties bytes before and after).
  A  every class of both jars loads, verifies and initialises
  B  class bytes 0.2.4 -> 0.2.5: the same classes + CollBypassMig; every class byte-identical, or identical once its "0.2.4" constants
     read "0.2.5" (version only), or - declared - only these methods differ: CollReg <clinit> (exactly BYPASS true -> false), loadConfig
     (review fix: exactly the bypass.enabled statement - now CollReg.bypassOn(String.valueOf(getProperty("bypass.enabled", "false"))) -
     every other instruction and try range of it the same), configText, + the two new CollReg helpers onOff / bypassOn (nothing else
     added); CollPage buildDetail; SkyyCollectionsPlugin setup; CfgRows <clinit> (the row table); version-only methods anywhere else;
     every other method instruction-identical
  C  texts and the loader: statusColor = 0.2.4's on every result text; configText = 0.2.4's with the marker line and false; the static
     default (BYPASS before any file is read: 0.2.4 true, 0.2.5 false); CollReg.loadConfig on 33 config files (review fix, finding 1:
     the config kit's ON / OFF words in several cases, spaces / a tab, escapes, continued lines, empty, odd words, a missing line):
     0.2.5 reads coin unlocks ON exactly when the config kit's own CfgRows.validate (= Server Setup) reads ON, 0.2.4 read anything but
     false as on (the files where they differ are exactly the expected ones: missing, off / no / 0 ..., empty, odd words); a WARN only
     for a word that is neither ON nor OFF (captured from the logger); every other setting reads the same on both jars (auto and
     bridge.add.felled keep 0.2.4's reading); CollBypassMig.isOff = "not ON" on every value
  D  differential page builds 0.2.4 vs 0.2.5 on the real registry (the 0.2.4 harness matrix: error views, home x 3 profiles, every
     category page + past the end, collection views incl. bought tiers / maxed / undiscovered / no icon / free bags / bagMax none and
     legendary / a bazaar price / a 20-tier curve / fallbacks, unlocked recipes none / some / 40 / 41 / 57+, every result text):
     D1 coin unlocks ON on both jars -> the engine command lists (type, selector, text, data), the event bindings and the page state are
     IDENTICAL; D2 OFF on both jars -> identical except every collection view, where 0.2.5 = 0.2.4 with the buy well (#SkyyCBuyRow) turned
     into the 96 px spacer, its children / b.set lines dropped and no cbuy binding; no 0.2.5 OFF page shows a buy / coin-unlock text
     (the result line aside), and the BOUGHT rows are still there; every 0.2.5 build: check_markup, check_page, assert_proven, kit /
     data colours only, the layout model (the body filled exactly, every fixed row / column holds its children)
  E  clicks through handleDataEvent: E1 ON - the 0.2.4 sequences (browsing + the pager ends, the two-click coin buy, a refused buy) give
     identical page state, purse, counts file, bypass.log and rebuilt page on both jars; E2 OFF - forged / stale cbuy clicks are refused
     ("Coin unlocks are turned off on this server.") with no coins taken and nothing saved or logged, on both jars, and the rebuilt
     0.2.5 page has no buy well; E3 an admin turns coin unlocks back on through the config kit (a fresh 0.2.5 world on its default file:
     off -> Server Setup set true asks first -> yes -> the file says true, RELOAD ran) and the buy sequence is then identical to 0.2.4's;
     set false again asks nothing and hides the well; E4 (review fix) a hand-edited bypass.enabled=off / no / 0 / OFF / flase / empty:
     the loader reads OFF and the kit (Server Setup) says OFF, the collection page has no buy well, forged cbuy clicks are refused with
     no coins taken and nothing saved, "set false" answers "already OFF" (true now) and "set true" asks first; on 0.2.4 the same off /
     no / 0 files read ON while its kit said OFF (the bug the fix closes)
  K  the Server Setup rows (CfgRows): the same keys in the same order, every element 0.2.4's except bypass.enabled (default false, the
     help, confirm=on); the kit on a fresh 0.2.5 world: get = false, set true asks "Turn Coin unlocks ON for everyone on this server?
     <help>", yes = ok, set false asks nothing; export "changed" holds bypass.enabled only while it is on; on 0.2.4 the part switch asks
     before OFF (the change, shown)
  M  CollBypassMig on scratch COPIES in the plugin's start order (CollBagMigrate.run -> CollBypassMig.run -> CollReg.loadAll ->
     CfgPub.start), each start in a fresh loader: (1) Skyy's live folder: start 1 changes exactly config.properties (the marker line +
     bypass.enabled false, every other byte and LF kept), config-history (a .bak = the old bytes + its index.log line) and
     config-changes.log (one "SkyyCollections 0.2.5 / update / bypass.enabled / true / false / ok" line the kit lists for Undo); start 2
     writes nothing; Undo (the kit's set back to true) restores the value, start 3 keeps it on; (2) edited copies: yes / True / on / 1 /
     a continued line kept and logged (coin unlocks stay on), false / FALSE silent, review fix: off / no / 0 / OFF / flase / an empty
     value / a last line "off" under a "true" silent too (they read OFF - never "kept ... stay ON"), a missing line (code default off),
     CRLF + a non-ASCII byte, two lines, " : " separator, no final newline, an empty file - each started twice; (3) config-history
     unwritable: untouched, retried at
     the next start once it can be written; (4) a value java.util.Properties cannot read: untouched (the Properties guard); (5) a fresh
     folder: the 0.2.5 default file (marker + false) is written by the loader and never updated
  U  no take-backs: profiles with bought tiers (Wheat / Iron / Cobblestone / OakLog, bags inside and above bagMax) - CollUnlocks.compute
     and the published coll:recipes:<uuid> / coll:<uuid> are identical on 0.2.4 and 0.2.5 with coin unlocks on AND off (bagMax unique and
     legendary), the bought Normal / Unique bags unlocked, a Rare bag above bagMax not
  F  text fit with the client's font tables (read-only; skipped without the client): every static button label and every text the
     0.2.5 page shows fits its label
  G  the page id: COLL_PAGE_ID of the kit's page NOW == COLL_PAGE_CHECKED in the generated script == the page id in the jar's ready line
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the page, the real PageManager, the SkyyMenu
Server Setup page drawing the confirm question, an admin's real UUID through the permission check (the bare JVM has no PermissionsModule:
Undo / set run as the console here).
Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/coll025/harness, deleted at the end
unless --keep; --dir must be a folder inside tools/dev/scratch/; TEMP / TMP and java.io.tmpdir point into it). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, difflib, base64, zlib, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.2.5", "0.2.4"
PKG = "com.skyy.collections."
SCRIPT = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.abspath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "coll025", "harness")))
assert SCRATCH.lower().startswith(SCRATCH_ROOT.lower() + os.sep), "--dir must be a folder INSIDE tools/dev/scratch/: " + SCRATCH
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}
OFF_TEXT = "Coin unlocks are turned off on this server."
# a 0.2.5 page with coin unlocks off shows none of these anywhere (the result line aside: it answers a stale / forged Buy click)
COIN_TEXT = re.compile(r"\bBuy\b|\bbuy|[Cc]oin unlock|coins unlock|turned off|coin wall|coin limit|for buying")


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


def script_consts():
    """MG_MARK / MG_MARK_ID / MG_WHO and the CFG default lines of the generated script (literals, read with ast)."""
    text = open(SCRIPT, encoding="utf8").read()
    out = {}
    for n in ast.parse(text).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            name = n.targets[0].id
            if name in ("MG_MARK", "MG_MARK_ID", "MG_WHO"):
                out[name] = ast.literal_eval(n.value)
    return out


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


def manifest(jar):
    z = zipfile.ZipFile(jar)
    m = json.loads(z.read("manifest.json").decode("utf8"))
    z.close()
    return m


# ------------------------------------------------------------------------------------------------ markup helpers (concrete markup)
TEXT_RE = re.compile(r'(?<![A-Za-z])Text: "((?:[^"\\]|\\.)*)"')
ID_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{")
OWN_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{([^{}]*)")      # an element's id and its own properties (up to its first child)


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


def snap(d):
    """{relative path: bytes} of every file under d"""
    return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                for r, _ds, fs in os.walk(d) for fn in fs)


def diff_lines(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            out.append([op, [x.decode("latin-1") for x in la[i1:i2]], [x.decode("latin-1") for x in lb[j1:j2]]])
    return out


def export_text(code):
    """the key=value text inside a SKYY1 export code (base64url of zlib, CONFIG-CONTRACT 'Export and import codes')"""
    parts = code.split(".")
    b = parts[2]
    data = base64.urlsafe_b64decode(b + "=" * (-len(b) % 4))
    return zlib.decompress(data).decode("utf8")


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride, JObject
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    SUI, K = kit_page()
    SC = script_consts()
    LIVE_BEFORE = open(os.path.join(LIVE_DIR, "config.properties"), "rb").read()
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
    print("A. loaded + verified + initialised: 0.2.4 %d, 0.2.5 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return

    # ---------------- B. class bytes
    old, new = CB["old"], CB["new"]
    check(sorted(set(new) - set(old)) == [PKG + "CollBypassMig"] and not (set(old) - set(new)),
          "B. the same classes + CollBypassMig: %s" % sorted(set(old) ^ set(new)))
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
        # instruction-identical MODULO the constant-pool numbering (constants compared by value, ldc_w read as ldc, branch targets and
        # exception ranges as instruction indices) - the 0.2.4 harness's comparison
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

    DECLARED = {"CollReg": ["<clinit>", "configText", "loadConfig"], "CollPage": ["buildDetail"], "SkyyCollectionsPlugin": ["setup"],
                "CfgRows": ["<clinit>"]}
    # review fix (finding 1): the only methods 0.2.5 adds to a 0.2.4 class - the loader's ON / OFF reading (= the Server Setup row)
    ADDED = {"CollReg": ["bypassOn(Ljava/lang/String;)Z", "onOff(Ljava/lang/String;)I"]}
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
        check(str(po.getClassFile().getSuperclass()) == str(pn.getClassFile().getSuperclass()), "B. %s: superclass changed" % short)
        mo, mn = methods(po), methods(pn)
        check(not (set(mo) - set(mn)) and sorted(set(mn) - set(mo)) == ADDED.get(short, []),
              "B. %s: methods added / gone: %s (new allowed: %s)" % (short, sorted(set(mo) ^ set(mn)), ADDED.get(short, [])))
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and not vonly(mo[k], mn[k]))
        vers = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k] and vonly(mo[k], mn[k]))
        check(changed == DECLARED.get(short, []), "B. %s: changed methods %s, declared %s" % (short, changed, DECLARED.get(short, [])))
        kinds[short] = "methods %s%s%s" % (changed, (" + version only %s" % vers) if vers else "",
                                           (" + new %s" % [x.split("(")[0] for x in ADDED[short]]) if short in ADDED else "")
        if short == "CollReg":
            # <clinit>: exactly BYPASS = true -> false; loadConfig: exactly the bypass.enabled statement (review fix, below)
            ci_o, ci_n = mo["<clinit>"], mn["<clinit>"]
            ops = [(op, ci_o[i1:i2], ci_n[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ci_o, ci_n, autojunk=False).get_opcodes() if op != "equal"]
            at = [j1 for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ci_o, ci_n, autojunk=False).get_opcodes() if op != "equal"]
            check(ops == [("replace", ["iconst_1"], ["iconst_0"])] and "BYPASS" in ci_n[at[0] + 1],
                  "B. CollReg <clinit>: only BYPASS true -> false: %s" % ops)
            # review fix (finding 1): loadConfig differs in exactly the bypass.enabled statement - the instructions between "putstatic
            # CAP_MINUTE" and "putstatic BYPASS" - now BYPASS = bypassOn(String.valueOf(p.getProperty("bypass.enabled", "false")))
            # (0.2.4: !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bypass.enabled", "true")).trim())); the instructions before
            # it are identical, the ones after it identical with their branch targets taken relative to the tail, and every try range
            # after it moved by exactly the statement's size change (-6)
            lk = [k for k in mo if k.startswith("loadConfig(")][0]
            lo, ln = mo[lk], mn[lk]
            io, inn = [t for t in lo if not t.startswith("try ")], [t for t in ln if not t.startswith("try ")]
            CAPM, BYPS = "putstatic Field %sCollReg.CAP_MINUTE(J)" % PKG, "putstatic Field %sCollReg.BYPASS(Z)" % PKG
            ao, bo_, an, bn = io.index(CAPM), io.index(BYPS), inn.index(CAPM), inn.index(BYPS)
            GETP = "invokevirtual Method java.util.Properties.getProperty((Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;)"
            VALOF = "invokestatic Method java.lang.String.valueOf((Ljava/lang/Object;)Ljava/lang/String;)"
            want_new = ["aload_1", 'ldc "bypass.enabled"', 'ldc "false"', GETP, VALOF, "invokestatic Method %sCollReg.bypassOn((Ljava/lang/String;)Z)" % PKG, BYPS]
            want_old = ['ldc "false"', "aload_1", 'ldc "bypass.enabled"', 'ldc "true"', GETP, VALOF, "invokevirtual Method java.lang.String.trim(()Ljava/lang/String;)",
                        "invokevirtual Method java.lang.String.equalsIgnoreCase((Ljava/lang/String;)Z)"]

            def tail(lst, start):
                return [re.sub(r" @(\d+)$", lambda mm: " @+%d" % (int(mm.group(1)) - start), t) for t in lst[start:]]

            def tries(lst):
                return [re.match(r"^try @(\d+) @(\d+) @(\d+) (.*)$", t).groups() for t in lst if t.startswith("try ")]
            delta = (bn - an) - (bo_ - ao)
            to_, tn_ = tries(lo), tries(ln)
            tries_ok = len(to_) == len(tn_) == 2 and all(
                x[3] == y[3] and all(int(b) == (int(a) if int(x[0]) <= ao else int(a) + delta) for a, b in zip(x[:3], y[:3]))
                for x, y in zip(to_, tn_))
            check(io[:ao + 1] == inn[:an + 1] and inn[an + 1:bn + 1] == want_new and io[ao + 1:ao + 1 + len(want_old)] == want_old
                  and tail(io, bo_ + 1) == tail(inn, bn + 1) and delta == -6 and tries_ok,
                  "B. CollReg.loadConfig: only the bypass.enabled statement changed (now bypassOn, default false): %s / %s / tries %s / %s" % (
                      io[ao + 1:bo_ + 1], inn[an + 1:bn + 1], to_, tn_))
    bpm = ct(new[PKG + "CollBypassMig"])
    bms = sorted(set(k.split("(")[0] for k in methods(bpm)))
    check(bms == ["<clinit>", "<init>", "fileIdx", "isOff", "mgIdx", "mgKit", "mgLog", "mgSaved", "mgUpdate", "run", "sameAfter"],
          "B. CollBypassMig methods: %s" % bms)
    ident = sorted(k for k, v in kinds.items() if v == "identical")
    print("B. %d classes byte-identical, version constants only: %s; method-level: %s; new: CollBypassMig %s" % (
        len(ident), sorted(k for k, v in kinds.items() if v == "version constants"),
        dict((k, v) for k, v in kinds.items() if v.startswith("methods")), bms))
    COUNT["B"] = (len(ident), kinds)
    mo_, mn_ = manifest(OLD), manifest(JAR)
    check(mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyyCollections" and "coin unlocks" not in mn_["Description"]
          and mo_["Description"].replace("coin unlocks for early tiers; ", "") == mn_["Description"]
          and dict((k, v) for k, v in mo_.items() if k not in ("Version", "Name", "Description")) == dict((k, v) for k, v in mn_.items() if k not in ("Version", "Name", "Description")),
          "B. manifest: only Version / Name and the dropped 'coin unlocks for early tiers' changed")

    # ---------------- common Java objects
    UUID, Paths, Long, Boolean, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
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

    def path(p):
        return Paths.get(p)

    def op(k, *a):
        """the config kit's op function of loader k (CfgFn, CONFIG-CONTRACT): a Python list / string result"""
        r = jc(k, "CfgFn")().apply(JArray(JObject)(list(a)))
        if r is None:
            return None
        if isinstance(r, str):
            return str(r)
        return [None if x is None else (str(x) if not hasattr(x, "__len__") or isinstance(x, str) else [str(y) for y in x]) for x in r]

    # ---------------- C. texts and the loader
    COL = SUI.COLOR
    STATUS_SAMPLES = [("", COL["info"]), ("Your collections could not be read right now.", COL["error"]),
                      ("Click Buy again within 10 s to pay 1,500 coins for the tier III unlocks of Wheat.", COL["info"]),
                      ("Coin unlocks need SkyyCoins, which is not loaded.", COL["error"]),
                      ("You need 1,500 coins in your purse.", COL["error"]),
                      ("Could not save the purchase - your coins were refunded.", COL["error"]),
                      ("Could not save the purchase and the refund failed - tell an admin (bypass.log).", COL["error"]),
                      ("Bought the tier III unlocks of Wheat for 1,500 coins. Gather to tier III for its coins and XP.", COL["success"]),
                      (OFF_TEXT, COL["error"]), ("Collections are not loaded.", COL["error"]),
                      ("Coin unlocks are not available for this collection.", COL["error"]),
                      ("Collect one first - coin unlocks need a discovered collection.", COL["error"]),
                      ("Every tier is unlocked.", COL["error"]),
                      ("Coin unlocks are not available for Elite collections - gather it.", COL["error"]),
                      ("Tier VI must be gathered - coins unlock up to tier V here.", COL["error"]),
                      ("Nothing more here can be bought with coins - gather it.", COL["error"])]
    for t, want in STATUS_SAMPLES:
        got_n, got_o = str(jc("new", "CollPage").statusColor(t)), str(jc("old", "CollPage").statusColor(t))
        check(got_n == want and got_o == want, "C. statusColor(%r) = %s / %s, want %s" % (t[:40], got_o, got_n, want))
    ct_o, ct_n = str(jc("old", "CollReg").configText()), str(jc("new", "CollReg").configText())
    want_ct = ct_o.replace("\n# coin-bypass: buy only", "\n" + SC["MG_MARK"] + "\n# coin-bypass: buy only", 1).replace("\nbypass.enabled=true\n", "\nbypass.enabled=false\n", 1)
    check(ct_n == want_ct and ct_n != ct_o, "C. configText = 0.2.4's + the marker line, bypass.enabled=false")
    check(ct_n.count(SC["MG_MARK_ID"]) == 1 and "\n" + SC["MG_MARK"] + "\n# coin-bypass:" in ct_n, "C. the default file carries the marker once, above the coin-bypass comment")
    fresh = {}
    for k, jar in (("old", OLD), ("new", JAR)):
        fl = loader(jar)
        fresh[k] = bool(JClass(PKG + "CollReg", loader=fl).BYPASS)
    check(fresh == {"old": True, "new": False}, "C. CollReg.BYPASS before any file is read: %s" % fresh)
    # review fix (finding 1): CollReg.loadConfig on config files that differ only in their bypass.enabled text (v = the file text after
    # "bypass.enabled=", None = no line). The 0.2.5 reading must be the config kit's own (CfgRows.validate of the 0.2.5 jar - what Server
    # Setup and the Mods list show - on the value java.util.Properties reads; no line = the row default false); 0.2.4 read anything but
    # "false" as on. The other lines hold values 0.2.4 and 0.2.5 must read the same (auto / bridge.add.felled keep 0.2.4's reading).
    CASES = [("missing", None), ("true", "true"), ("false", "false"), ("FALSE", "FALSE"), ("yes", "yes"), ("on", "on"), ("1", "1"),
             ("True", "True"), ("flase", "flase"), ("empty", ""), ("continued", "tr\\\n  ue"),
             ("off", "off"), ("no", "no"), ("0", "0"), ("OFF", "OFF"), ("No", "No"), ("oFf", "oFf"), ("YES", "YES"), ("On", "On"),
             ("TRUE", "TRUE"), ("spaces true", "   true   "), ("tab off", "\toff"), ("spaces 0", " 0 "), ("escaped on", "\\u006fn"),
             ("continued off", "of\\\n  f"), ("n", "n"), ("f", "f"), ("disabled", "disabled"), ("enabled", "enabled"),
             ("false # off", "false # off"), ("2", "2"), ("t", "t"), ("long", "x" * 300 + "\\nnext line")]
    # the files where 0.2.5 reads differently from 0.2.4 (written out by hand, independent of both jars and the kit): no line, the kit's
    # OFF words and every value that is neither ON nor OFF
    DIFFER = {"missing", "flase", "empty", "off", "no", "0", "OFF", "No", "oFf", "tab off", "spaces 0", "continued off", "n", "f",
              "disabled", "enabled", "false # off", "2", "t", "long"}
    NEITHER = {"flase", "empty", "n", "f", "disabled", "enabled", "false # off", "2", "t", "long"}       # the kit: "not ON/OFF" -> WARN
    REST = "auto=on\nbridge.add.felled=off\nbypass.bagMax=Rare\ncap.perMinute=123\nbypass.walls=6,4,3,0\n"
    Rows_n = jc("new", "CfgRows")
    bi_c = int(Rows_n.index("bypass.enabled"))
    Props, FIS = JClass("java.util.Properties"), JClass("java.io.FileInputStream")
    HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
    RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(RECS)
    for k in ("old", "new"):
        jc(k, "CollUtil").LOG = HL.get("SkyyCollectionsHarness")
    WARN_TAIL = " is not ON or OFF (true, on, yes, 1 / false, off, no, 0) - coin unlocks stay OFF"
    lc, others, warns, kit_on = {}, {}, {}, {}
    for ci, (name, v) in enumerate(CASES):
        for k in ("old", "new"):
            d = os.path.join(SCRATCH, "loader", "%02d" % ci, k)          # numbered: "false" / "FALSE" are one folder on Windows
            os.makedirs(d)
            body = "# test\nmigrate=convert\n" + ("" if v is None else "bypass.enabled=" + v + "\n") + REST
            fp = os.path.join(d, "config.properties")
            open(fp, "wb").write(body.encode("latin-1"))
            Reg = jc(k, "CollReg")
            Reg.BASE = path(d)
            RECS.clear()
            msg = str(Reg.loadConfig())
            warns[(name, k)] = [str(r.getMessage()) for r in RECS if "bypass.enabled=" in str(r.getMessage())]
            lc[(name, k)] = bool(Reg.BYPASS)
            others[(name, k)] = (re.sub(r" bypass=(true|false) ", " ", msg), str(Reg.MIGRATE), bool(Reg.AUTO), sorted(str(x) for x in Reg.EXCLUDE),
                                 int(Reg.CAP_CREDIT), int(Reg.CAP_MINUTE), float(Reg.BYP_MULT), int(Reg.BYP_MIN), [int(x) for x in Reg.BYP_FALLBACK],
                                 [int(x) for x in Reg.BYP_WALL], sorted(str(x) for x in Reg.ADD_SOURCES), int(Reg.BYP_BAGMAX))
        pv = None
        if v is not None:
            pr = Props()
            fis = FIS(fp)
            pr.load(fis)
            fis.close()
            pv = str(pr.getProperty("bypass.enabled"))
        canon = Rows_n.validate(bi_c, pv if pv is not None else str(Rows_n.DEFS[bi_c]))[0]
        kit_on[name] = canon is not None and str(canon) == "true"
        neither = canon is None
        old_want = pv is None or pv.strip().lower() != "false"
        check(lc[(name, "new")] == kit_on[name], "C. bypass.enabled=%r: 0.2.5 reads %s, the config kit (Server Setup) %s" % (v, lc[(name, "new")], kit_on[name]))
        check(lc[(name, "old")] == old_want, "C. bypass.enabled=%r: 0.2.4 read %s (anything but false = on)" % (v, lc[(name, "old")]))
        check((lc[(name, "old")] != lc[(name, "new")]) == (name in DIFFER) and (not lc[(name, "new")] if name in DIFFER else True),
              "C. bypass.enabled=%r: 0.2.4 %s / 0.2.5 %s - %s" % (v, lc[(name, "old")], lc[(name, "new")], "differs (0.2.5 off)" if name in DIFFER else "the same"))
        check(neither == (name in NEITHER), "C. bypass.enabled=%r: the kit calls it %s" % (v, "neither ON nor OFF" if neither else canon))
        w = warns[(name, "new")]
        if name in NEITHER:
            shown = pv.strip().replace("\n", " ").replace("\r", " ")
            shown = shown if len(shown) <= 60 else shown[:57] + "..."
            check(w == ["[SkyyCollections] config.properties: bypass.enabled=" + shown + WARN_TAIL],
                  "C. bypass.enabled=%r: one WARN naming the value (one line, clipped): %s" % (v[:40], w))
        else:
            check(w == [], "C. bypass.enabled=%r: no WARN for an ON / OFF word or no line: %s" % (v, w))
        check(warns[(name, "old")] == [], "C. bypass.enabled=%r: 0.2.4 never warned about it: %s" % (v, warns[(name, "old")]))
        check(others[(name, "old")] == others[(name, "new")], "C. bypass.enabled=%r: every other setting reads the same on both jars: %s / %s" % (
            v, others[(name, "old")], others[(name, "new")]))
        if v is not None:
            check(bool(jc("new", "CollBypassMig").isOff(pv)) == (not kit_on[name]), "C. CollBypassMig.isOff(%r) = not ON" % pv[:40])
    # the rest of the file as 0.2.4 read it (not part of this fix): auto=on reads off, bridge.add.felled=off keeps felled logs counted
    o1 = others[("true", "new")]
    check(o1[2] is False and "skills:felled" in o1[10] and o1[11] == 3 and o1[5] == 123 and o1[9] == [6, 4, 3, 0],
          "C. the other lines read as 0.2.4 reads them (auto=on off, bridge.add.felled=off counted, bagMax Rare, cap 123, walls): %s" % (o1,))
    Reg_n = jc("new", "CollReg")
    oo = [int(Reg_n.onOff(x)) for x in (None, "", " YES ", "No", "0", "1", "maybe", "\tOn\t", "FALSE")]
    check(oo == [-1, -1, 1, 0, 0, 1, -1, 1, 0], "C. CollReg.onOff on raw texts: %s" % oo)
    check(bool(Reg_n.bypassOn(None)) is False and bool(Reg_n.bypassOn("ON")) is True and bool(Reg_n.bypassOn("x\ny" * 50)) is False,
          "C. CollReg.bypassOn: null / ON / a long two-line word")
    HLB.unsubscribe(RECS)
    for k in ("old", "new"):
        jc(k, "CollUtil").LOG = None
    n_diff = len([n for n, _v in CASES if lc[(n, "old")] != lc[(n, "new")]])
    print("C. statusColor: %d result texts on both jars; configText = 0.2.4's + marker + false; static default 0.2.4 on / 0.2.5 off; "
          "loadConfig on %d files: 0.2.5 = the config kit's reading on every file (%d read ON), 0.2.4 differs on %d (all now OFF), %d WARNs "
          "(neither ON nor OFF), every other setting the same" % (len(STATUS_SAMPLES), len(CASES), len([n for n in kit_on if kit_on[n]]), n_diff,
                                                                  len([n for n, _v in CASES if warns[(n, "new")]])))

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

    REG = {}          # per loader key: (CollReg, CollStore, RegData, recipe table, loadAll message, base folder)

    def world(k):
        """CollReg.loadAll into scratch/world/<k>/mods/Skyy_SkyyCollections (the jar's default files), the recipe table from the rewards
        table (validate() without the asset stores), every icon marked a game item except each 7th collection."""
        Reg, Store = jc(k, "CollReg"), jc(k, "CollStore")
        base = os.path.join(SCRATCH, "world", k, "mods", "Skyy_SkyyCollections")
        shutil.rmtree(os.path.dirname(os.path.dirname(base)), ignore_errors=True)
        os.makedirs(base)
        Reg.BASE = path(base)
        Store.DIR = path(base).resolve("counts")
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
        REG[k] = (Reg, Store, R, rec, msg, base)

    for k in ("old", "new"):
        world(k)
    Reg0, _s, R0, REC0, MSG0, _b = REG["old"]
    INFO = [dict(id=str(R0.id[c]), cat=int(R0.cat[c]), name=str(R0.name[c]), item=str(R0.items[c][0]), curve=int(R0.curve[c]),
                 hidden=bool(R0.hidden[c]), mx=int(Reg0.maxTier(R0, c)), thr=[int(Reg0.threshold(R0, c, t)) for t in range(1, int(Reg0.maxTier(R0, c)) + 1)])
            for c in range(R0.n)]
    m_new = REG["new"][4]
    check(MSG0.replace("bypass=true", "bypass=false") == m_new and "bypass=true" in MSG0 and "bypass=false" in m_new,
          "D. both jars read the same registry, 0.2.5's default file has coin unlocks off: %s / %s" % (MSG0, m_new))
    BYID = dict((x["id"], i) for i, x in enumerate(INFO))
    print("   registry: %s; %d recipe tiers" % (m_new, REC0.size()))
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
        if name in ("mixed", "bought"):
            for cid, cnt, bt in (("Wheat", 60, 2), ("Iron", 30, 0), ("OakLog", 300, 4), ("Bone", 0, 0), ("Cobblestone", 1, 0)):
                if cid in BYID:
                    out[BYID[cid]] = (cnt, bt)
        if name == "bought":                                               # U: bags inside and above bagMax bought
            for cid, cnt, bt in (("Wheat", 60, 3), ("Iron", 30, 3), ("OakLog", 300, 5), ("Cobblestone", 1, 4), ("HideLight", 0, 0)):
                if cid in BYID:
                    out[BYID[cid]] = (cnt, bt)
        return out

    def setup(k, prof, broken=False, noreg=False, cfg=None, bridge=None, thr20=False, extra_rec=0, keep_cfg=False):
        Reg, Store, R, rec, _m, base = REG[k]
        Store.DATA.clear()
        Store.BROKEN.clear()
        Store.DIRTY.clear()
        jc(k, "CollBypass").ARM.clear()
        BR.clear()
        BR.put("coins:fn:take", COINS[0])
        BR.put("coins:fn:add", COINS[1])
        for kk, v in (bridge or {}).items():
            BR.put(kk, v)
        cd = os.path.join(base, "counts")
        shutil.rmtree(cd, ignore_errors=True)
        os.makedirs(cd)
        if not keep_cfg:
            for kk, v in dict(DEF, **(cfg or {})).items():
                setattr(Reg, kk, v)
        R.thr[0] = JArray(JLong)([10 * (i + 1) for i in range(20)] if thr20 else [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000])
        newrec = HashMap(rec)
        for c in range(min(extra_rec, R.n)):
            newrec.put("%d.1" % c, JArray(JString)(["Skyy_Test_Extra_%d_Recipe_Generated_0" % c] + list(rec.get("%d.1" % c) or [])))
        Reg.RECIPES = newrec
        Reg.VALIDATED = True
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

    def all_texts(cmds, skip=("SkyyCStatus",)):
        """every text the page shows (inline Text values + b.set .Text values), the ids in `skip` left out"""
        out = []
        for _p, t in appends_of(cmds):
            for m in OWN_RE.finditer(t):
                tm = TEXT_RE.search(m.group(2))
                if tm and tm.group(1) and m.group(1) not in skip:
                    out.append(tm.group(1))
            for m in re.finditer(r"(?:Label|TextButton) \{[^{}]*?Text: \"((?:[^\"\\]|\\.)*)\"", t):     # anonymous labels
                if m.group(1):
                    out.append(m.group(1))
        for ident, v in sets_of(cmds):
            if v and ident not in skip:
                out.append(v)
        return out

    ALLOWED = set(SUI.allowed_colors()) | set(SUI.norm_color(c) for c in K["UI_DATA_COLORS"])
    SEEN = []                                  # (label id, text) of every 0.2.5 text, for F
    LABELS = {}                                # label id -> (markup, parent) as last seen
    CHECKED_NEW = set()

    def check_new(tag, cmds):
        """0.2.5 markup rules and the layout model on one concrete build (memoised per command list)."""
        h = hashlib.sha1(repr(cmds).encode("utf8")).hexdigest()
        if h in CHECKED_NEW:
            return
        CHECKED_NEW.add(h)
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
        kids, own = {}, {}
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
            sizes = [outer(kk)[axis] for kk in kids[cid]]
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

    SPACER = SUI.render(SUI.spacer(w=K["COLL_IW"], h=K["COLL_BUY_H"] + 8))

    def strip_buy(cmds, evs):
        """0.2.4's collection view with coin unlocks OFF -> what 0.2.5 must send: the buy well #SkyyCBuyRow becomes the 96 px spacer,
        the appends into it and every #SkyyCBuy* b.set go, and no cbuy binding (0.2.4 binds it only when a buy is offered)."""
        out = []
        for typ, sel, text, data in cmds:
            if "append" in typ.lower():
                if sel is not None and sel.lstrip("#") in ("SkyyCBuyRow", "SkyyCBuyTxt"):
                    continue
                if text is not None and re.match(r"\s*Group #SkyyCBuyRow\b", text):
                    out.append((typ, sel, SPACER, data))
                    continue
            elif sel is not None and sel.startswith("#SkyyCBuy"):
                continue
            out.append((typ, sel, text, data))
        return out, [e for e in evs if "cbuy" not in (e[2] or "")]

    def first_diff(a, b):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return "at %d: %r / %r" % (i, str(x)[:160], str(y)[:160])
        return "lengths %d / %d" % (len(a), len(b))

    def page(k, view=0, cat=0, page_no=0, coll=-1, status=""):
        pg = jc(k, "CollPage")(pref())
        pg.view, pg.cat, pg.pageNo, pg.coll, pg.status = view, cat, page_no, coll, status
        return pg

    def no_coin_text(tag, cmds):
        bad = [t for t in all_texts(cmds) if COIN_TEXT.search(t)]
        ids = sorted(i for i in ids_of(cmds) if i.startswith("SkyyCBuy"))
        check(not bad and not ids, "D. %s: coin unlocks off but the page shows %s %s" % (tag, bad[:3], ids))
        tally("D off pages scanned")

    def both(tag, prof, mode, view=0, cat=0, page_no=0, coll=-1, status="", **kw):
        res = {}
        for k in ("old", "new"):
            setup(k, profile(prof) if isinstance(prof, str) else prof, cfg=dict(kw.get("cfg") or {}, BYPASS=(mode == "on")),
                  **dict((a, b) for a, b in kw.items() if a != "cfg"))
            pg = page(k, view, cat, page_no, coll, status)
            cmds, evs = build(pg)
            res[k] = (cmds, evs, state_of(pg))
        (co, eo, so), (cn, en, sn) = res["old"], res["new"]
        check(so == sn, "D. %s %s: page state after build differs: %s / %s" % (mode, tag, so, sn))
        if mode == "off" and so[0] == 2:
            co, eo = strip_buy(co, eo)
            tally("D off collection views")
        check(eo == en, "D. %s %s: event bindings differ: %s" % (mode, tag, first_diff(eo, en)))
        check(co == cn, "D. %s %s: engine commands differ %s" % (mode, tag, first_diff(co, cn)))
        tally("D builds", 2)
        tally("D %s states" % mode)
        tally("D commands compared", len(cn))
        check_new("%s %s" % (mode, tag), cn)
        if mode == "off":
            no_coin_text("%s %s" % (mode, tag), cn)
            check(not any("cbuy" in (e[2] or "") for e in en), "D. off %s: a cbuy binding" % tag)
        return res

    # ---------------- D. differential builds (D1 on, D2 off)
    VIS = [c for c, x in enumerate(INFO) if not x["hidden"]]
    CAT_N = [len([c for c in VIS if INFO[c]["cat"] == cat]) for cat in range(4)]
    wheat = BYID.get("Wheat", VIS[0])
    iron = BYID.get("Iron", VIS[1])
    det = sorted(set([VIS[i] for i in range(0, len(VIS), 5)] + [BYID[x] for x in ("Wheat", "Iron", "OakLog", "Bone", "Cobblestone") if x in BYID]))
    bulk = [c for c in VIS if INFO[c]["curve"] == 0]
    hid = [c for c, x in enumerate(INFO) if x["hidden"]]
    for mode in ("on", "off"):
        both("error: no registry", "mixed", mode, noreg=True)
        both("error: counts unreadable", "mixed", mode, broken=True)
        for prof in ("empty", "mixed", "maxall"):
            both("home %s" % prof, prof, mode)
            for cat in range(4):
                pages = max(1, (CAT_N[cat] + 11) // 12)
                for pn in list(range(pages)) + [pages + 3]:
                    both("cat %d page %d %s" % (cat, pn, prof), prof, mode, view=1, cat=cat, page_no=pn)
        both("cat -1 falls back home", "mixed", mode, view=1, cat=-1)
        both("cat 4 (Fishing) falls back home", "mixed", mode, view=1, cat=4)
        for prof in ("empty", "mixed", "maxall", "bought"):
            for c in det:
                both("detail %s %s" % (INFO[c]["id"], prof), prof, mode, view=2, coll=c)
        for label, kw in (("bags free", {"bridge": {"sacks:freebags": Boolean.TRUE}}), ("bagMax none", {"cfg": {"BYP_BAGMAX": 0}}),
                          ("bagMax legendary", {"cfg": {"BYP_BAGMAX": 4}}),
                          ("bazaar price", {"bridge": {"bazaar:buy:" + INFO[iron]["item"]: Long.valueOf(7)}})):
            for c in (wheat, iron):
                both("detail %s %s" % (INFO[c]["id"], label), "mixed", mode, view=2, coll=c, **kw)
        if bulk:
            for cnt in (0, 55, 205):
                both("detail %s 20 tiers count %d" % (INFO[bulk[0]]["id"], cnt), {bulk[0]: (cnt, 0)}, mode, view=2, coll=bulk[0], thr20=True)
        if hid:
            both("detail of a hidden collection falls back home", "mixed", mode, view=2, coll=hid[0])
        both("detail coll out of range falls back home", "mixed", mode, view=2, coll=9999)
        for prof, extra in (("empty", 0), ("mixed", 0), ("maxall", 0), ("maxall", 60), ("bought", 0)):
            both("recipes %s +%d" % (prof, extra), prof, mode, view=3, extra_rec=extra)
        for want in (40, 41):
            for extra in range(0, 120):
                setup("old", profile("maxall"), extra_rec=extra)
                cmds, _e = build(page("old", 3))
                sub = [v for i, v in sets_of(cmds) if i == "SkyyCRSub"][0]
                m = re.match(r"(\d+) recipe", sub)
                if m and int(m.group(1)) == want:
                    both("recipes exactly %d lines" % want, "maxall", mode, view=3, extra_rec=extra)
                    break
        for t, _c in STATUS_SAMPLES:
            both("status %r home" % t[:30], "mixed", mode, status=t)
            both("status %r detail" % t[:30], "mixed", mode, view=2, coll=wheat, status=t)
    # the OFF collection view of a bought collection still shows its BOUGHT rows and the bought line (no take-backs)
    r = both("detail Wheat bought (no take-backs shown)", "bought", "off", view=2, coll=wheat)
    # the scanner itself: 0.2.4's page in the same state shows the "turned off" line in its buy well - the scan finds it there
    hits4 = [t for t in all_texts(r["old"][0]) if COIN_TEXT.search(t)]
    check(OFF_TEXT in hits4 and any(i.startswith("SkyyCBuy") for i in ids_of(r["old"][0])), "D. the coin-text scan finds 0.2.4's off line: %s" % hits4)
    tx = id_texts(r["new"][0])
    check(tx.get("SkyyCTr3S") == "BOUGHT" and "(recipes bought up to tier III)" in (tx.get("SkyyCDTier") or "")
          and "(paid when reached)" in (tx.get("SkyyCRew3") or ""), "D. off: Wheat bought to III still shows BOUGHT III: %s / %s / %s"
          % (tx.get("SkyyCTr3S"), tx.get("SkyyCDTier"), tx.get("SkyyCRew3")))
    rr = both("recipes bought (no take-backs shown)", "bought", "off", view=3)
    lines = [v for i, v in sets_of(rr["new"][0]) if i.startswith("SkyyCRn")]
    check(any("Unique Mining Bag" in x and "bought" in x for x in lines) or any("Mining" in x and "bought" in x for x in lines),
          "D. off: the Unlocked recipes view still lists the bought Mining bag tiers: %s" % [x for x in lines if "bought" in x][:4])
    # the ON collection view of Wheat (mixed: bought II, count 60) offers tier III: the buy well with BUY, the cost line and the cbuy binding
    ro = both("detail Wheat mixed buy offered", "mixed", "on", view=2, coll=wheat)
    tn = id_texts(ro["new"][0])
    check(str(tn.get("SkyyCBuyLbl", "")).startswith("Buy tier III unlocks - ") and any("cbuy" in (e[2] or "") for e in ro["new"][1]),
          "D. on: the buy well is offered as in 0.2.4: %s" % tn.get("SkyyCBuyLbl"))
    print("D. %d page builds (%d on + %d off states x 2 jars): every command list identical (%d commands; %d off collection views = "
          "0.2.4 minus the buy well), %d 0.2.5 markups in %d distinct pages, %d layout checks, %d off pages without buy / coin-unlock text" % (
              COUNT.get("D builds", 0), COUNT.get("D on states", 0), COUNT.get("D off states", 0), COUNT.get("D commands compared", 0),
              COUNT.get("D off collection views", 0), COUNT.get("D markups", 0), COUNT.get("D pages", 0), COUNT.get("D layout", 0),
              COUNT.get("D off pages scanned", 0)))

    # ---------------- E. clicks (handleDataEvent)
    def files(k):
        base = REG[k][5]
        cd = os.path.join(base, "counts", US + ".properties")
        txt = open(cd).read() if os.path.isfile(cd) else ""
        props = sorted(ln for ln in txt.split("\n") if ln and not ln.startswith("#"))
        lg = os.path.join(base, "bypass.log")
        logl = [re.sub(r"^.*?  (BUY|FAILED-SAVE) ", r"\1 ", ln) for ln in open(lg).read().split("\n") if ln] if os.path.isfile(lg) else []
        return props, logl

    def play(k, prof, purse, seq, keep_cfg=False, mode="on"):
        setup(k, profile(prof), cfg={"BYPASS": mode == "on"}, keep_cfg=keep_cfg)
        PURSE.clear()
        PURSE[US] = purse
        lg = os.path.join(REG[k][5], "bypass.log")
        if os.path.isfile(lg):
            os.remove(lg)
        pg = page(k)
        steps = []
        for a in seq:
            pg.handleDataEvent(None, None, json.dumps({"a": a}))
            cmds, evs = build(pg)
            steps.append((a, state_of(pg), PURSE.get(US), files(k), evs, cmds))
            tally("E clicks")
        return steps

    def compare_steps(name, so_, sn_, mode):
        for so, sn in zip(so_, sn_):
            a = so[0]
            check(so[1] == sn[1], "E. %s after %s: page state %s / %s" % (name, a, so[1], sn[1]))
            check(so[2] == sn[2], "E. %s after %s: purse %s / %s" % (name, a, so[2], sn[2]))
            check(so[3] == sn[3], "E. %s after %s: counts file / bypass.log differ:\n %s\n %s" % (name, a, so[3], sn[3]))
            co, eo = so[5], so[4]
            if mode == "off" and so[1][0] == 2:
                co, eo = strip_buy(co, eo)
            check(eo == sn[4], "E. %s after %s: bindings differ %s" % (name, a, first_diff(eo, sn[4])))
            check(co == sn[5], "E. %s after %s: rebuilt page differs %s" % (name, a, first_diff(co, sn[5])))
            check_new("E %s after %s" % (name, a), sn[5])
            if mode == "off":
                no_coin_text("E %s after %s" % (name, a), sn[5])

    SEQS = [
        ("browse", "mixed", 0, ["ccat0", "cnext", "cnext", "cnext", "cprev", "cprev", "cprev", "ccard0", "cback", "ccard11", "ccard5", "chome",
                                "ccat2", "cnext", "ccard3", "cback", "cback", "crecipes", "cback", "crefresh", "ccat3", "ccard1", "chome",
                                "bogus", "cclose"]),
        ("buy", "mixed", 5000, ["ccat0", "ccard0", "cbuy", "cbuy", "cbuy", "crefresh", "cback", "chome"]),
        ("buy-poor", "mixed", 10, ["ccat1", "ccard0", "cbuy", "cbuy", "chome"]),
    ]
    buys = 0
    for name, prof, purse, seq in SEQS:
        so_, sn_ = play("old", prof, purse, seq), play("new", prof, purse, seq)
        compare_steps("on " + name, so_, sn_, "on")
        buys += len([s for s in sn_ if s[1][4] and s[1][4].startswith("Bought the tier ")])
    check(buys >= 1, "E1. at least one coin buy went through with coin unlocks on (%d)" % buys)
    # E2: coin unlocks off - a stale page / forged clicks: refused, nothing taken, nothing saved or logged
    OFFSEQ = ["ccat0", "ccard0", "cbuy", "cbuy", "crefresh", "cbuy", "cback", "ccard0", "cbuy", "chome", "cbuy"]
    so_, sn_ = play("old", "mixed", 5000, OFFSEQ, mode="off"), play("new", "mixed", 5000, OFFSEQ, mode="off")
    compare_steps("off forged", so_, sn_, "off")
    base_files = sn_[0][3]                     # after the first click (ccat0 saves nothing): the counts file as written by setup()
    check(not base_files[1] and any(p.startswith("_bought.") for p in base_files[0]), "E2. the profile starts with bought tiers, no bypass.log")
    for s in sn_:
        if s[0] == "cbuy":
            check(s[1][4] == OFF_TEXT and s[2] == 5000 and s[3] == base_files,
                  "E2. a cbuy click with coin unlocks off is refused, no coins, nothing saved or logged: %s / %s / %s" % (s[1][4], s[2], s[3][1]))
        else:
            check(s[1][4] == "", "E2. other clicks clear the result line: %s %r" % (s[0], s[1][4]))
    # E3: an admin turns coin unlocks back on through the config kit on a fresh 0.2.5 world (its default file: off)
    L["new3"] = loader(JAR)
    world("new3")
    Reg3 = jc("new3", "CollReg")
    e3 = {"start_off": bool(Reg3.BYPASS)}
    jc("new3", "CfgPub").start(path(os.path.dirname(REG["new3"][5])), None)
    e3["get0"] = op("new3", "get", "bypass.enabled")
    r1 = op("new3", "set", "bypass.enabled", "true", None, "console", "", "console")
    e3["ask_on"] = r1
    e3["still_off"] = bool(Reg3.BYPASS)
    r2 = op("new3", "set", "bypass.enabled", "true", None, "console", "yes", "console")
    e3["set_on"] = r2
    jc("new3", "CfgPub").flush()
    cfgtxt = open(os.path.join(REG["new3"][5], "config.properties"), "rb").read()
    e3["file_on"] = b"\nbypass.enabled=true\n" in cfgtxt and b"bypass.enabled=false" not in cfgtxt
    e3["reloaded_on"] = bool(Reg3.BYPASS)
    check(e3["start_off"] is False and e3["get0"] == "false", "E3. a fresh 0.2.5 world starts with coin unlocks off: %s" % e3)
    check(e3["ask_on"][0] == "confirm" and e3["ask_on"][2] == "Turn Coin unlocks ON for everyone on this server? " + str(jc("new3", "CfgRows").HELPS[int(jc("new3", "CfgRows").index("bypass.enabled"))])
          and e3["still_off"] is False, "E3. Server Setup: switching Coin unlocks ON asks first, nothing changes before yes: %s" % e3["ask_on"])
    check(e3["set_on"][0] == "ok" and e3["file_on"] and e3["reloaded_on"], "E3. yes = on: the file says true and the RELOAD routine turned BYPASS on: %s" % e3)
    # the harness world again on the new registry the reload made (RECIPES / icons as the other worlds), the switch as the kit left it
    REG["new3"] = (Reg3, REG["new3"][1], REG["new3"][2], REG["new3"][3], REG["new3"][4], REG["new3"][5])
    s_old = play("old", "mixed", 5000, SEQS[1][3])
    s_new3 = play("new3", "mixed", 5000, SEQS[1][3], keep_cfg=True)
    check(bool(Reg3.BYPASS), "E3. the switch stays on through the buy")
    compare_steps("E3 back on: buy", s_old, s_new3, "on")
    check(any(s[1][4] and s[1][4].startswith("Bought the tier ") for s in s_new3), "E3. a coin buy went through after the admin turned it on")
    r3 = op("new3", "set", "bypass.enabled", "false", None, "console", "", "console")
    jc("new3", "CfgPub").flush()
    e3["set_off"] = r3
    check(r3[0] == "ok" and not bool(Reg3.BYPASS), "E3. switching it off again asks nothing and turns it off: %s" % r3)
    s_off3 = play("new3", "mixed", 5000, ["ccat0", "ccard0"], keep_cfg=True)
    check(not any(i.startswith("SkyyCBuy") for i in ids_of(s_off3[-1][5])), "E3. the buy well is gone again")
    # E4 (review fix, finding 1): an admin hand-edits bypass.enabled to an OFF word (or a word that is neither): a fresh 0.2.5 world
    # whose config.properties says so -> the loader and the kit both read OFF, the page offers no buy, forged clicks are refused with no
    # coins taken and nothing saved / logged, Server Setup "set false" answers "already OFF" (true now), "set true" asks first.
    # 0.2.4 on the same off / no / 0 files sold tiers (BYPASS on) while its kit said OFF - the bug the fix closes.
    E4SEQ = ["ccat0", "ccard0", "cbuy", "cbuy", "crefresh", "cbuy", "cback", "ccard0", "cbuy"]
    e4n = 0
    for wi, word in enumerate(("off", "no", "0", "OFF", "flase", "")):
        key = "new4%d" % wi
        L[key] = loader(JAR)
        world(key)
        Reg4 = jc(key, "CollReg")
        cfgp = os.path.join(REG[key][5], "config.properties")
        t0 = open(cfgp, "rb").read()
        open(cfgp, "wb").write(t0.replace(b"\nbypass.enabled=false\n", b"\nbypass.enabled=" + word.encode("latin-1") + b"\n", 1))
        Reg4.loadConfig()
        jc(key, "CfgPub").start(path(os.path.dirname(REG[key][5])), None)
        g4 = op(key, "get", "bypass.enabled")
        check(t0.count(b"\nbypass.enabled=false\n") == 1 and not bool(Reg4.BYPASS) and g4 == ("false" if word.lower() in ("off", "no", "0") else word),
              "E4. bypass.enabled=%r: the loader reads OFF, the kit shows %r" % (word, g4))
        st4 = play(key, "mixed", 5000, E4SEQ, keep_cfg=True)
        start_files = st4[0][3]
        for s in st4:
            check(not any(i.startswith("SkyyCBuy") for i in ids_of(s[5])) and not any("cbuy" in (e[2] or "") for e in s[4]),
                  "E4. bypass.enabled=%r: no buy well / cbuy binding after %s" % (word, s[0]))
            no_coin_text("E4 %r after %s" % (word, s[0]), s[5])
            if s[0] == "cbuy":
                e4n += 1
                check(s[1][4] == OFF_TEXT and s[2] == 5000 and s[3] == start_files and not s[3][1],
                      "E4. bypass.enabled=%r: a forged cbuy is refused, no coins, nothing saved or logged: %s / %s / %s" % (word, s[1][4], s[2], s[3][1]))
        check(any(s[1][0] == 2 for s in st4), "E4. bypass.enabled=%r: the sequence reached a collection view" % word)
        tb = open(cfgp, "rb").read()
        rf = op(key, "set", "bypass.enabled", "false", None, "console", "", "console")
        jc(key, "CfgPub").flush()
        t1 = open(cfgp, "rb").read()
        if word.lower() in ("off", "no", "0"):
            check(rf[0] == "ok" and rf[2] == "Coin unlocks is already OFF." and t1 == tb and b"\nbypass.enabled=" + word.encode("latin-1") + b"\n" in t1,
                  "E4. bypass.enabled=%r: set false answers already OFF (true now) and writes nothing: %s" % (word, rf))
        else:
            check(rf[0] == "ok" and b"\nbypass.enabled=false\n" in t1, "E4. bypass.enabled=%r: set false writes false: %s" % (word, rf))
        check(not bool(Reg4.BYPASS), "E4. bypass.enabled=%r: still off after set false" % word)
        rn = op(key, "set", "bypass.enabled", "true", None, "console", "", "console")
        check(rn[0] == "confirm" and rn[2].startswith("Turn Coin unlocks ON for everyone on this server? ") and not bool(Reg4.BYPASS),
              "E4. bypass.enabled=%r: set true asks first, nothing changes before yes: %s" % (word, rn))
    # 0.2.4 on the same hand-edited off words: its loader read them ON while its kit (Server Setup) said OFF
    e4old = {}
    for wi, word in enumerate(("off", "no", "0")):
        key = "old4%d" % wi
        L[key] = loader(OLD)
        world(key)
        Reg4 = jc(key, "CollReg")
        cfgp = os.path.join(REG[key][5], "config.properties")
        t0 = open(cfgp, "rb").read()
        open(cfgp, "wb").write(t0.replace(b"\nbypass.enabled=true\n", b"\nbypass.enabled=" + word.encode("latin-1") + b"\n", 1))
        Reg4.loadConfig()
        jc(key, "CfgPub").start(path(os.path.dirname(REG[key][5])), None)
        e4old[word] = (t0.count(b"\nbypass.enabled=true\n"), bool(Reg4.BYPASS), op(key, "get", "bypass.enabled"))
    check(all(v == (1, True, "false") for v in e4old.values()), "E4. 0.2.4: off / no / 0 read ON while its kit said OFF: %s" % e4old)
    print("E. %d clicks: E1 on - %d sequences identical on both jars (%d coin buys); E2 off - %d forged clicks refused, no coins, "
          "nothing saved; E3 back on through the kit (asks first) = 0.2.4's buy, off again hides it; E4 hand-edited off / no / 0 / OFF / "
          "flase / empty: the loader and the kit read OFF, no buy well, %d forged clicks refused, set false = already OFF, set true asks "
          "(0.2.4 read off / no / 0 ON)" % (COUNT.get("E clicks", 0), len(SEQS), buys, OFFSEQ.count("cbuy"), e4n))

    # ---------------- K. the Server Setup rows and the kit's answers
    ARRS = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS", "VTYPES")

    def rows(k):
        Rw = jc(k, "CfgRows")
        out = dict((a, [str(x) for x in getattr(Rw, a)]) for a in ARRS)
        out["BCONF"] = [int(x) for x in Rw.BCONF]
        return out

    ro_, rn_ = rows("old"), rows("new")
    check(ro_["KEYS"] == rn_["KEYS"], "K. the same row keys in the same order")
    bi = rn_["KEYS"].index("bypass.enabled")
    diffs = sorted((a, rn_["KEYS"][i]) for a in list(ARRS) + ["BCONF"] for i in range(len(rn_["KEYS"])) if ro_[a][i] != rn_[a][i])
    check(diffs == [("BCONF", "bypass.enabled"), ("DEFS", "bypass.enabled"), ("HELPS", "bypass.enabled")],
          "K. only bypass.enabled's default, help and confirm changed: %s" % diffs)
    check(rn_["DEFS"][bi] == "false" and ro_["DEFS"][bi] == "true" and rn_["BCONF"][bi] == 1 and ro_["BCONF"][bi] == 0
          and rn_["FLAGS"][bi] == "live,part,danger" and rn_["LABELS"][bi] == "Coin unlocks" and len(rn_["HELPS"][bi]) <= 100,
          "K. bypass.enabled: default false, confirm=on, flags / label kept: %s %s %s %s" % (rn_["DEFS"][bi], rn_["BCONF"][bi], rn_["FLAGS"][bi], rn_["HELPS"][bi]))
    check([rn_["KEYS"][i] for i in range(len(rn_["KEYS"])) if rn_["CATS"][i] == "bypass"] ==
          ["bypass.enabled", "bypass.multiplier", "bypass.minPrice", "bypass.fallback", "bypass.walls", "bypass.bagMax"],
          "K. the Coin unlocks category keeps all six rows")
    kr = {}
    for k, jar in (("oldk", OLD), ("newk", JAR)):
        L[k] = loader(jar)
        world(k)
        jc(k, "CfgPub").start(path(os.path.dirname(REG[k][5])), None)
        kr[k] = {"get": op(k, "get", "bypass.enabled"), "status": op(k, "status")}
        kr[k]["export0"] = export_text(op(k, "export", "changed"))
    # 0.2.4 default on: switching OFF asks (a part switch); 0.2.5 default off: switching ON asks, OFF does not
    kr["oldk"]["off"] = op("oldk", "set", "bypass.enabled", "false", None, "console", "", "console")
    kr["newk"]["on"] = op("newk", "set", "bypass.enabled", "true", None, "console", "", "console")
    kr["newk"]["on_yes"] = op("newk", "set", "bypass.enabled", "true", None, "console", "yes", "console")
    jc("newk", "CfgPub").flush()
    kr["newk"]["export_on"] = export_text(op("newk", "export", "changed"))
    kr["newk"]["off"] = op("newk", "set", "bypass.enabled", "false", None, "console", "", "console")
    jc("newk", "CfgPub").flush()
    kr["newk"]["export_off"] = export_text(op("newk", "export", "changed"))
    kr["newk"]["get_end"] = op("newk", "get", "bypass.enabled")
    kr["newk"]["denied"] = op("newk", "set", "bypass.enabled", "true", UUID.fromString("00000000-0000-0000-0000-00000000ad01"), "Admin", "yes", "undo")
    check(kr["oldk"]["get"] == "true" and kr["newk"]["get"] == "false", "K. the kit reads the default file: 0.2.4 %s, 0.2.5 %s" % (kr["oldk"]["get"], kr["newk"]["get"]))
    check(kr["oldk"]["off"][0] == "confirm" and kr["oldk"]["off"][2].startswith("Turn Coin unlocks OFF"), "K. 0.2.4: switching OFF asked: %s" % kr["oldk"]["off"])
    check(kr["newk"]["on"][0] == "confirm" and kr["newk"]["on"][2] == "Turn Coin unlocks ON for everyone on this server? " + rn_["HELPS"][bi],
          "K. 0.2.5: switching ON asks: %s" % kr["newk"]["on"])
    check(kr["newk"]["on_yes"][0] == "ok" and kr["newk"]["off"][0] == "ok" and kr["newk"]["get_end"] == "false",
          "K. 0.2.5: yes = on; switching OFF asks nothing: %s / %s" % (kr["newk"]["on_yes"], kr["newk"]["off"]))
    check("bypass.enabled" not in kr["newk"]["export0"] and "bypass.enabled=true" in kr["newk"]["export_on"] and "bypass.enabled" not in kr["newk"]["export_off"],
          "K. export 'changed' holds bypass.enabled only while it differs from the 0.2.5 default (off)")
    check(kr["newk"]["denied"][0] == "denied", "K. a real UUID without the node is denied in a bare JVM (no PermissionsModule): %s" % kr["newk"]["denied"])
    check(kr["newk"]["status"][0] == "ok", "K. the kit status on a fresh 0.2.5 world is ok: %s" % kr["newk"]["status"])
    print("K. %d Server Setup rows: same keys / order, only bypass.enabled changed (default false, help, confirm=on); kit: get false, "
          "ON asks ('%s...'), OFF does not; export changed only while on; 0.2.4 asked before OFF" % (len(rn_["KEYS"]), kr["newk"]["on"][2][:48]))

    # ---------------- M. CollBypassMig on scratch copies (each start = a fresh loader of the 0.2.5 jar, the plugin's order)
    def start(base):
        ld = loader(JAR)
        C = lambda n: JClass(PKG + n, loader=ld)
        Reg, Store = C("CollReg"), C("CollStore")
        b = path(base)
        Reg.BASE = b
        Store.DIR = b.resolve("counts")
        Store.DATA.clear()
        bm = str(C("CollBagMigrate").run(b))
        cm = str(C("CollBypassMig").run(b))
        s = str(Reg.loadAll())
        C("CfgPub").start(b.getParent(), None)
        out = {"bm": bm, "cm": cm, "load": s, "bypass": bool(Reg.BYPASS), "loader": ld, "C": C}
        return out

    def case(name, body):
        tally("M cases")
        base = os.path.join(SCRATCH, "m", "%02d-%s" % (COUNT["M cases"], re.sub(r"[^a-z0-9]+", "-", name.lower())), "mods", "Skyy_SkyyCollections")
        os.makedirs(base)
        if body is not None:
            open(os.path.join(base, "config.properties"), "wb").write(body)
        return base

    MK = SC["MG_MARK"]
    LOGRE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\tSkyyCollections 0\.2\.5\t-\tupdate\tbypass\.enabled\ttrue\tfalse\tok$")
    M = {}
    # (1) Skyy's live folder, copied (read-only source)
    lc_ = os.path.join(SCRATCH, "m", "live", "mods", "Skyy_SkyyCollections")
    shutil.copytree(LIVE_DIR, lc_)
    s0 = snap(lc_)
    check(s0["config.properties"] == LIVE_BEFORE, "M. the copy is the live config.properties")
    r1 = start(lc_)
    s1 = snap(lc_)
    r2 = start(lc_)
    s2 = snap(lc_)
    x0, x1 = s0["config.properties"], s1["config.properties"]
    changed1 = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    newbak = [k for k in changed1 if k.startswith("config-history/") and k.endswith(".bak")]
    idx = s1.get("config-history/index.log", b"").decode("utf8").strip().split("\n")
    clog = s1.get("config-changes.log", b"").decode("utf8").strip().split("\n")
    d1 = diff_lines(x0, x1)
    M["live"] = {"cm1": r1["cm"], "cm2": r2["cm"], "changed1": changed1, "changed2": sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)),
                 "diff": d1, "bypass": (r1["bypass"], r2["bypass"])}
    check(changed1 == sorted(["config.properties", "config-changes.log", "config-history/index.log"] + newbak) and len(newbak) == 1,
          "M live: start 1 writes only config.properties, config-history (one .bak + index.log) and config-changes.log: %s" % changed1)
    check(len(newbak) == 1 and s1[newbak[0]] == x0, "M live: the History copy holds the old bytes")
    check(len(idx) == 1 and idx[0].startswith("Skyy_SkyyCollections~config.properties#") and idx[0].endswith("\tSkyy_SkyyCollections/config.properties\t" + idx[0].split("\t")[2] + "\tSkyyCollections 0.2.5\tbefore the 0.2.5 coin unlocks update"),
          "M live: the index.log line: %s" % idx)
    check(len(clog) == 1 and LOGRE.match(clog[0]) is not None, "M live: one config-changes.log line in the kit's format: %s" % clog)
    want_diff = [["insert", [], [MK]], ["replace", ["bypass.enabled=true"], ["bypass.enabled=false"]]]
    check(d1 == want_diff, "M live: exactly the marker line + true -> false: %s" % d1)
    check(x1.count(b"\r") == 0 and x0.count(b"\r") == 0 and x1.replace((MK + "\n").encode("latin-1"), b"").replace(b"bypass.enabled=false\n", b"bypass.enabled=true\n") == x0,
          "M live: every other byte kept (LF)")
    lines1 = x1.decode("latin-1").split("\n")
    check(lines1.index(MK) + 1 == lines1.index("# coin-bypass: buy only the NEXT tier's recipe unlocks (never its coins, XP, score or leaderboard count), one tier at a time")
          and lines1.index(MK) + 2 == lines1.index("bypass.enabled=false"), "M live: the marker sits above the coin-bypass comment")
    check(r1["cm"].startswith("config.properties: coin unlocks are OFF now") and "bypass.enabled true -> false" in r1["cm"] and r2["cm"] == "",
          "M live: the INFO line once, nothing at start 2: %r / %r" % (r1["cm"][:80], r2["cm"]))
    check(M["live"]["changed2"] == [] and r1["bypass"] is False and r2["bypass"] is False, "M live: start 2 writes nothing; coin unlocks off: %s" % M["live"])
    check(r1["bm"] == "bags: rewards already on the rarity ladder", "M live: the bag migration is untouched (%s)" % r1["bm"])
    # what SkyyMenu's Changes view needs for Undo: the kit lists the line as ok, and the current value is its new value
    C2 = r2["C"]
    lg = C2("CfgFn")().apply(JArray(JObject)(["log", Integer.valueOf(20)]))
    lg = [str(x) for x in lg]
    mine = [x for x in lg if "\tSkyyCollections 0.2.5\t" in x]
    check(len(mine) == 1 and mine[0].split("\t")[4:8] == ["bypass.enabled", "true", "false", "ok"], "M live: the kit's log op lists the update line for Undo: %s" % mine)
    gv = str(C2("CfgFn")().apply(JArray(JObject)(["get", "bypass.enabled"])))
    check(gv == "false", "M live: get bypass.enabled = false (= the line's new value: SkyyMenu offers Undo): %s" % gv)
    # Undo = a set back to the old value (SkyyMenu sends set <key> <old> ... "yes" "undo"; the bare JVM has no PermissionsModule, so the
    # console path runs the same kit set): the file says true again (only that value), the RELOAD routine turns coin unlocks on
    ur = C2("CfgFn")().apply(JArray(JObject)(["set", "bypass.enabled", "true", None, "console", "yes", "console"]))
    C2("CfgPub").flush()
    s3 = snap(lc_)
    x3 = s3["config.properties"]
    check(str(ur[0]) == "ok" and x3 == x1.replace(b"bypass.enabled=false\n", b"bypass.enabled=true\n") and bool(C2("CollReg").BYPASS),
          "M live: Undo puts bypass.enabled back to true (marker kept), coin unlocks on: %s" % [str(x) for x in ur])
    r4 = start(lc_)
    s4 = snap(lc_)
    check(r4["cm"] == "" and r4["bypass"] is True and s4["config.properties"] == x3, "M live: a start after the Undo keeps coin unlocks on (runs once): %r %s" % (r4["cm"], r4["bypass"]))
    # (2) edited copies
    base_txt = x0
    EDITS = [
        ("yes", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=yes\n"), "kept", True),
        ("True", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=True\n"), "kept", True),
        ("false", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=false\n"), "already", False),
        ("FALSE", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=FALSE\n"), "already", False),
        ("missing", base_txt.replace(b"bypass.enabled=true\n", b""), "missing", False),
        ("continued", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=tr\\\n    ue\n"), "kept", True),
        ("crlf", (b"# caf\xe9 - an admin's note\n" + base_txt).replace(b"\n", b"\r\n"), "migrated", False),
        ("two lines", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=false\n") + b"bypass.enabled=true\n", "migrated", False),
        ("two lines last yes", base_txt + b"bypass.enabled=yes\n", "kept", True),
        ("colon", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled : true\n"), "migrated", False),
        ("no final newline", b"# a short file\nbypass.enabled=true", "migrated", False),
        ("empty", b"", "missing", False),
        # review fix (finding 1): the migration reads a value like the loader (CollReg.onOff): an ON word other than the exact old default
        # is an admin's value (kept, logged, coin unlocks stay on); an OFF word or any other word already reads OFF (silent, no Undo line)
        ("on", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=on\n"), "kept", True),
        ("1", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=1\n"), "kept", True),
        ("off", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=off\n"), "already", False),
        ("no", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=no\n"), "already", False),
        ("0", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=0\n"), "already", False),
        ("OFF", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=OFF\n"), "already", False),
        ("flase", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=flase\n"), "already", False),
        ("empty value", base_txt.replace(b"bypass.enabled=true\n", b"bypass.enabled=\n"), "already", False),
        ("two lines last off", base_txt + b"bypass.enabled=off\n", "already", False),
    ]
    for name, body, want, on in EDITS:
        base = case(name, body)
        a = start(base)
        t1 = snap(base)
        b = start(base)
        t2 = snap(base)
        y1 = t1["config.properties"]
        ok = a["bypass"] == on and b["bypass"] == on and b["cm"] == "" and t1 == t2 and y1.count(MK.encode("latin-1")) == 1
        baks = [k for k in t1 if k.endswith(".bak")]
        ok = ok and len(baks) == 1 and t1[baks[0]] == body
        cl = t1.get("config-changes.log", b"").decode("utf8").strip()
        if want == "migrated":
            ok = ok and a["cm"].startswith("config.properties: coin unlocks are OFF now") and LOGRE.match(cl) is not None and len(cl.split("\n")) == 1
        else:
            ok = ok and cl == ""
            ok = ok and {"kept": "holds an admin's value - kept, coin unlocks stay ON", "already": "was already off - no value changed",
                         "missing": "has no bypass.enabled line: coin unlocks follow the 0.2.5 default - OFF"}[want] in a["cm"]
        if want == "kept":
            ok = ok and "kept (an admin's value: coin unlocks stay ON on this server)" in a["cm"]
        if want == "already":                  # review fix: an OFF word is never logged as "kept ... coin unlocks stay ON"
            ok = ok and "stay ON" not in a["cm"] and "kept" not in a["cm"]
        dl = diff_lines(body, y1)
        if name == "crlf":
            ok = ok and y1.count(b"\r\n") == y1.count(b"\n") and y1.startswith(b"# caf\xe9 - an admin's note\r\n") and (MK + "\r\n").encode("latin-1") in y1 \
                and b"bypass.enabled=false\r\n" in y1 and y1.replace((MK + "\r\n").encode("latin-1"), b"").replace(b"bypass.enabled=false", b"bypass.enabled=true") == body
        elif name == "two lines":
            ok = ok and y1.count(b"bypass.enabled=false\n") == 2 and b"bypass.enabled=true" not in y1
        elif name == "two lines last yes":
            ok = ok and b"bypass.enabled=true\n" in y1 and b"bypass.enabled=yes\n" in y1
        elif name == "colon":
            ok = ok and b"bypass.enabled : false\n" in y1
        elif name == "no final newline":
            ok = ok and y1 == (MK + "\n# a short file\nbypass.enabled=false").encode("latin-1")
        elif name in ("missing", "empty"):
            ok = ok and y1 == (MK + "\n").encode("latin-1") + body
        elif want in ("kept", "already"):
            ok = ok and y1.replace((MK + "\n").encode("latin-1"), b"") == body
        check(ok, "M edit %s: %s, coin unlocks %s, once: cm=%r diff=%s log=%r" % (name, want, "on" if on else "off", a["cm"][:120], dl[:3], cl[:80]))
        M["edit " + name] = ok
        tally("M edits")
    # (3) config-history cannot be written (a FILE named config-history): untouched, nothing logged; the next start (blocker gone) updates
    base = case("nohist", x0)
    open(os.path.join(base, "config-history"), "wb").write(b"not a folder")
    a = start(base)
    untouched = open(os.path.join(base, "config.properties"), "rb").read() == x0 and not os.path.exists(os.path.join(base, "config-changes.log"))
    os.remove(os.path.join(base, "config-history"))
    b = start(base)
    check(a["cm"] == "" and untouched and a["bypass"] is True and b["cm"].startswith("config.properties: coin unlocks are OFF now") and b["bypass"] is False,
          "M history unwritable: untouched (coin unlocks still on), retried at the next start: %r / %r" % (a["cm"], b["cm"][:60]))
    # (4) a value java.util.Properties cannot read: the Properties guard refuses, the file stays untouched
    bad = x0.replace(b"bypass.enabled=true\n", b"bypass.enabled=true\nbroken.key=\\uZZZZ\n")
    base = case("badprops", bad)
    a = start(base)
    check(a["cm"] == "" and open(os.path.join(base, "config.properties"), "rb").read() == bad and not os.path.exists(os.path.join(base, "config-history")),
          "M unreadable value: untouched, no history: %r" % a["cm"])
    # (5) a fresh folder: the loader writes the 0.2.5 default (marker + false); it is never updated
    base = case("fresh", None)
    a = start(base)
    f1 = open(os.path.join(base, "config.properties"), "rb").read()
    b = start(base)
    f2 = open(os.path.join(base, "config.properties"), "rb").read()
    check(a["cm"] == "" and b["cm"] == "" and f1 == f2 and f1.decode("utf8") == ct_n and a["bypass"] is False and not os.path.exists(os.path.join(base, "config-history")),
          "M fresh: the 0.2.5 default file, coin unlocks off, never updated: %r %r" % (a["cm"], b["cm"]))
    # the pure text step on a CRLF copy of the live file = the LF result with CRLF
    tc = JClass(PKG + "CollBypassMig", loader=L["new"]).mgUpdate(x0.decode("latin-1").replace("\n", "\r\n"))
    check(str(tc[0]).encode("latin-1") == x1.replace(b"\n", b"\r\n"), "M the text step on CRLF = the LF result, CRLF kept")
    check(open(os.path.join(LIVE_DIR, "config.properties"), "rb").read() == LIVE_BEFORE, "M the LIVE config.properties is untouched")
    print("M. live copy: start 1 -> marker + true -> false (LF kept), History = old bytes + index line, 1 Undo line; start 2 nothing; Undo -> "
          "true, start 3 keeps it; %d edited copies twice each; history unwritable -> retried; unreadable value -> untouched; fresh -> default "
          "file never updated; the live file untouched" % COUNT.get("M edits", 0))

    # ---------------- U. no take-backs: the coll:recipes publish is the same with the switch on and off, on both jars
    U_ = {}
    for bm in (2, 4):
        for k in ("old", "new"):
            for mode in (True, False):
                setup(k, profile("bought"), cfg={"BYPASS": mode, "BYP_BAGMAX": bm})
                Unl = jc(k, "CollUnlocks")
                Unl.PUBLISHED.clear()
                Unl.SIG.clear()
                d = jc(k, "CollStore").data(UID)
                comp = sorted(str(x) for x in Unl.compute(d))
                Unl.publish(UID)
                U_[(bm, k, mode)] = (comp, str(BR.get("coll:recipes:" + US)), str(BR.get("coll:" + US)))
        vals = [U_[(bm, k, m)] for k in ("old", "new") for m in (True, False)]
        check(all(v == vals[0] for v in vals), "U. bagMax %d: compute / coll:recipes / coll: identical on 0.2.4 and 0.2.5, on and off" % bm)
        comp = vals[0][0]
        has = lambda rid: rid in comp
        check(has("Skyy_Sack_Mining_Small_Recipe_Generated_0") and has("Skyy_Sack_Mining_Medium_Recipe_Generated_0")
              and has("Skyy_Sack_Farming_Medium_Recipe_Generated_0") and has("Rock_Stone_Brick_Recipe_Generated_0"),
              "U. bagMax %d: the bought Normal / Unique bags and the bought brick stay unlocked: %s" % (bm, [x for x in comp if "Sack" in x]))
        check(has("Skyy_Sack_Foraging_Rare_Recipe_Generated_0") == (bm >= 3), "U. bagMax %d: the bought Rare Foraging bag %s" % (bm, "unlocked" if bm >= 3 else "not unlocked (above bagMax)"))
        check(vals[0][1] == ",".join(comp), "U. bagMax %d: coll:recipes lists exactly the computed ids" % bm)
    print("U. no take-backs: %d recipe ids (bagMax unique) / %d (legendary) published the same on 0.2.4 and 0.2.5 with coin unlocks on and off"
          % (len(U_[(2, "new", False)][0]), len(U_[(4, "new", False)][0])))

    # ---------------- F. text fit (the client's font tables through the kit, read-only)
    if not os.path.isdir(SUI.FONT_DIR):
        print("F. skipped: no client font tables in", SUI.FONT_DIR)
    else:
        badf = []
        n_fit = 0
        for mk in K["COLL_CATOPEN"] + K["COLL_CATBACK"] + [K["COLL_CLOSE"], K["COLL_HOMEB"], K["COLL_BACK"]]:
            rr_ = SUI.render(mk)
            w = int(re.search(r"Anchor: \(Width: (\d+)", rr_).group(1))
            pad = int(re.search(r"Padding: \(Horizontal: (\d+)\)", rr_).group(1))
            text = re.search(r'Text: "([^"]*)"', rr_).group(1)
            tw = SUI.text_width(text, 17, bold=True, upper=True)
            n_fit += 1
            if tw > w - 2 * pad:
                badf.append("button %r %.0f > %d" % (text, tw, w - 2 * pad))
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
                w = PARENT_W.get(parent)
            if w is None:
                continue
            w -= a.get("Left", 0) + a.get("Right", 0)
            h = a.get("Height", 0)
            for t in texts_:
                n_fit += 1
                if wrap:
                    lines_ = SUI.text_lines(t, w, size, bold)
                    if lines_ * SUI.line_height(size, bold=bold) > h + 0.5:
                        badf.append("#%s wraps to %d lines in %d px: %r" % (ident, lines_, h, t))
                elif SUI.text_width(t, size, bold) > w:
                    badf.append("#%s %.0f px > %d: %r" % (ident, SUI.text_width(t, size, bold), w, t))
        COUNT["F"] = (n_fit, badf)
        check(not badf, "F. text fit (%d texts): %s" % (n_fit, badf[:12]))
        print("F. text fit: %d button labels and shown texts measured (NunitoSans), %d too wide" % (n_fit, len(badf)))

    # ---------------- G. the page id
    pid, chk = K["COLL_PAGE_ID"], K["COLL_PAGE_CHECKED"]
    pl = new[PKG + "SkyyCollectionsPlugin"]
    log_new = [t.decode("utf8") for _s, _e, t in cp_utf8(pl) if t.startswith(b"[SkyyCollections] 0.2.5 ready (")]
    check(len(log_new) == 1 and ("page %s)" % pid) in log_new[0], "G. the jar's ready log line names the page the kit makes now (%s): %s - rebuild the jar" % (pid, log_new))
    check(pid == chk, "G. the page the kit makes now (%s) is the checked page COLL_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/coll_0_2_5_patch.py, regenerate and rebuild" % (pid, chk, pid))
    print("G. page id %s, checked %s, kit %s" % (pid, chk, SUI.kit_id()))


PARENT_W = {}      # container id -> inner width, for labels that fill their parent (filled from the kit's page constants)


def main():
    for j, how in ((JAR, "python tools/coll_0_2_5_patch.py, then python SkyyCollections/build_skyycollections_0.2.5.py"),
                   (OLD, "python SkyyCollections/build_skyycollections_0.2.4.py (jars are git-ignored)")):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first:", how)
            return 1
    if not os.path.isfile(os.path.join(LIVE_DIR, "config.properties")):
        print("no live config.properties in", LIVE_DIR, "- pass --live <a Skyy_SkyyCollections folder>")
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
