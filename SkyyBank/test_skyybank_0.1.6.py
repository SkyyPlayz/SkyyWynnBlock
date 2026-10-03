"""Bare-JVM harness for SkyyBank 0.1.6 - the fix of Skyy's "deposit all got buggy" (2026-10-02 ~05:00 UTC: the /bank page stayed
dimmed under the client's "Loading..." box). Carried forward from SkyyBank/test_skyybank_0.1.5.py; keep it next to the build so the
build docstring's CHECKED claims can be re-run instead of trusted.

    python SkyyBank/test_skyybank_0.1.6.py [--jar <SkyyBank-0.1.6.jar>] [--old <SkyyBank-0.1.5.jar>] [--coins <SkyyCoins jar>]
                                           [--profiles <SkyyProfiles jar>] [--dir <scratch folder>] [--keep]

Build first (python tools/bank_0_1_6_patch.py, then python SkyyBank/build_skyybank_0.1.6.py). ONE JVM (the game's JRE, -Xverify:all,
-XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; SkyyBank 0.1.5 - the live SET pin -, SkyyBank 0.1.6, the
REAL SkyyCoins 0.1.5 and the REAL SkyyProfiles 0.1.5 each in its own class loader). The page runs through the ENGINE'S OWN
PageManager (openCustomPage, handleEvent, updateCustomPage, setPage, clearCustomPageAcknowledgements - wired with init(playerRef,
windowManager) as the engine does) on a stand-in Skyy: a Store that answers getComponent from a map (PlayerRef + Player holding that
PageManager), a recording packet handler, stand-in Universe / EntityModule instances carrying the component types, recording worlds.
The coins move through the REAL SkyyCoins CoinFn objects (coins:fn:get / add / take) and the REAL SkyyProfiles KeyFn
(profile:fn:key) + ProfStore.publish on scratch data: Skyy's profile 3 "Banana" (Priest) with purse 14,700 and bank 87,722 (the
numbers on Skyy's screenshot and in the live files), profiles 1, 2, 4 as in the live players file. A model client acknowledges
what the real one does (inferred from the engine - see R): every CustomPage it applies, a SetPage that closes the page it shows;
nothing while it shows no page; it drops its page at a world change. A click is the binding's own EventData from the last page
packet the client applied, "@BAmount" filled with the typed amount (so the click token travels exactly as in game).
  A  every class of the four jars loads, verifies and initialises
  B  class compare 0.1.5 -> 0.1.6: the 10 money / command classes byte-identical; SkyyBankPlugin only setup (BankWatch.STOP, EXEC =
     HytaleServer.SCHEDULED_EXECUTOR, the ready constant) and shutdown (BankWatch.STOP); BankPage: 0.1.5's fields + the 0.1.6 ones,
     12 methods instruction-identical (byte offsets read as instruction numbers: the bigger constant pool turns a few ldc into ldc_w)
     (jsonStr, fmt, colorOf, textOf, dur, every, subText, rateText, nextText, gainText, payoutOn, typed), changed <init> / build /
     handleDataEvent, new who / name / onDismiss / watchFail / profileStill / coinClick / answer / watchTick; BankWatch new
  R  ROOT CAUSE on the engine: (1) healthy - /bank, the client's ack, DEPOSIT ALL: 0.1.5 and 0.1.6 move 14,700 into the bank
     (102,422) and answer. (2) Skyy's session - a page open, a world change (the server keeps the page, only the counter is
     cleared), then a bench opening (setPage Bench) or SkyyMenu's CloseTask (setPage None): the counter stays at 1; /bank draws;
     0.1.5: Deposit all / Deposit / Withdraw / Withdraw all / Refresh / Close all DROPPED by PageManager.handleEvent (the page's
     handler never runs, no packet, no log line, coins untouched, the client keeps waiting = "Loading..."), reopening /bank does not
     help, Esc works, the next world change fixes it - Skyy's screenshot and logs exactly. 0.1.6 in the same state: the first click
     is dropped too (by the engine), the page check finds it (its test click does not arrive), logs one [SkyyBank] WARNING, resets
     the acknowledgements and answers (the client stops waiting); the next Deposit all moves 14,700 once. (3) the bank page itself
     open across a world change: 0.1.5 leaves it stale and the next bench gets the counter stuck; 0.1.6's check forgets it on the
     server (Dismiss: no packet, no counter change) and the bench + the next page stay healthy. (4) the late-found bridges: the bank
     set up with an empty bridge, SkyyCoins / SkyyProfiles registered afterwards - found on the first click
  W  the page check's real timer: without a scheduler (plugin not set up) the page works and the missing check is logged once;
     then BankWatch.EXEC = a scheduler built exactly like HytaleServer.SCHEDULED_EXECUTOR (Executors.newSingleThreadScheduledExecutor
     (ThreadUtil.daemon("Scheduler")) - the real field cannot initialise in a bare JVM, it needs the server's command-line options),
     handed over as setup() does: the hop on that thread hands the check to the player's world (World.execute, recorded), the check
     run as the world thread would: a healthy page sends nothing and is checked again; a stray page packet the client never
     acknowledges -> the next check heals (one WARNING) and the next click moves once; the player in another world -> the check runs
     on the NEW world and forgets the page; between worlds -> it waits; player gone / STOP / page closed or replaced -> it ends
  E  every button through the engine with Skyy's numbers on the real SkyyCoins / SkyyProfiles files: Deposit all, Withdraw all,
     Deposit 500, Withdraw 2k, too much, empty, not a number, Refresh, Enter, Close; zero purse / empty bank; a double click (the
     second click with the first click's token - also with the engine's gate cleared, and straight into the page): coins move ONCE;
     no SkyyCoins; SkyyCoins failing (get / take / add throwing or answering null, an unreadable purse file - never overwritten):
     nothing created or lost, a failed withdraw puts the coins back; the account file breaking after the purse was charged: the purse
     is refunded (logged); unknown / malformed / forged clicks answered; a failing rebuild still answers in short (logged); a profile
     switch after the page was drawn (real SkyyProfiles file + publish): refused,
     nothing moved, the page then shows profile 4 and the next click moves only profile 4's coins; a switch DURING the purse call
     (bracket result 2: booked on the start profile, logged) and during the purse read (refused by the purse); two pages (the
     replaced page refuses coins and sends nothing). After EVERY step: purse + bank of all profiles conserved, the client is not
     waiting, every error has a [SkyyBank] line
  D  page builds 0.1.5 vs 0.1.6 in the 0.1.5 harness's 10 states x 7 result marks / amount boxes: the same appends (byte for byte)
     and b.set lines in order, the same 7 bindings except the click token "t" on exactly the four coin buttons (a hex token, new on
     every build and page); 0.1.6's markup passes SUI.check_markup / check_page / assert_proven, no underscore ids
  F  text fit: every result text 0.1.6 can show (the new ones + every one seen in R / E) wraps to <= 2 lines in #SkyyBInfo on the
     client's NunitoSans tables (box read back out of the built markup; skipped when the client is not installed)
  P  every page packet 0.1.6 sent in R / E / W serializes with the engine's own codec (CustomPage.serialize -> toObject: same key,
     isInitial, clear, commands, bindings; size <= MAX_SIZE)
  S  start twice on a scratch COPY of the live data (UserData\\Saves\\HUD mod\\mods, read-only; the synthetic set if absent), the way
     setup() starts (BankConfig.load) + the worker's first interest sweep, 0.1.5 and 0.1.6 on two copies: the same balances; the
     second start writes nothing (every file byte-identical; with more than 24 periods due the catch-up takes one start per 24)
  G  the page id: BANK_PAGE_ID of the kit's page NOW == BANK_PAGE_CHECKED in the generated script == the page id in the ready line
  X  engine-access audit with the JVM's own rules: every class / field / method / constructor reference of the 0.1.6 jar looked up
     with MethodHandles.Lookup in its referencing class (a protected engine member only from a subclass) - 0 refused; control: a
     class calling BankPage.rebuild from outside is refused AND throws IllegalAccessError when run
Not testable without the game (UNVERIFIED in the build docstring): the client's own acknowledgement code (modelled from the engine's
rule and the logs), how it draws the "Loading..." box, the real world thread / packet handler / scheduler timing around the calls.
Also not in this harness: the whole SET in one JVM (the cross-check's job; done once in scratch for the 0.1.6 build: 24 jars, 1061
classes, -Xverify:all). Nothing is deployed. Default scratch folder tools/dev/scratch/test-bank-0.1.6 (deleted at the end unless
--keep; the engine's zstd native library, extracted into its tmp by part P, stays held by the JVM until the process ends); TEMP / TMP and
java.io.tmpdir point into it and the JVM's working directory is it. --dir must name a folder INSIDE tools/dev/scratch that is new,
empty or an earlier run's (it carries this harness's marker file): anything else is refused, so the end-of-run delete can only
remove a folder this harness made. Live data is only READ (copied). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.6", "0.1.5"
OLD_PAGE_ID = "50138aaed439"            # the 0.1.5 page: checked by test_skyybank_0.1.5.py, live, seen in game
PKG = "com.skyy.bank."
SCRIPT = os.path.join(HERE, "build_skyybank_%s.py" % VERSION)
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"          # Skyy's player UUID (the live files' names)
PURSE0, BANK0 = 14700, 87722                            # Skyy's profile 3 on the screenshot / in the live files
P4_PURSE, P4_BANK = 4368, 22361                         # profile 4 (Watermelon) in the live files
MARK = ".skyybank-0.1.6-harness"
TXT = {   # the 0.1.6 texts (tools/bank_0_1_6_patch.py); the harness reads what the page really shows and compares
    "err": "-Something went wrong - check your purse and bank above. The server log has the details.",
    "old": "=That click was for an older copy of this page, so nothing was moved. The page is up to date now - click again if you meant it.",
    "profile": "=Your profile changed after this page opened, so nothing was moved. The page now shows your current profile - click again.",
    "unknown": "=That button is not part of this page any more - the page was redrawn. Nothing was moved.",
    "heal": "=The game was holding back this page's clicks (a hiccup after a teleport) - fixed. If a click did nothing, nothing was moved - click again.",
    "closefail": "-The page could not be closed from here - press Esc.",
    "short": "Something went wrong drawing the bank page - press Esc and open /bank again.",
    "closed": "=This bank page was already closed, so nothing was moved.",
}


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "test-bank-0.1.6"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyBank-%s.jar" % OLD_VERSION)))
COINS = os.path.abspath(arg("--coins", os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.5.jar")))
PROFS = os.path.abspath(arg("--profiles", os.path.join(ROOT, "SkyyProfiles", "SkyyProfiles-0.1.5.jar")))
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


def claim_scratch():
    """the scratch folder must sit inside tools/dev/scratch and be new, empty or this harness's own (marker file)"""
    if os.path.commonpath([SCRATCH, SCRATCH_ROOT]) != SCRATCH_ROOT or SCRATCH == SCRATCH_ROOT:
        raise SystemExit("--dir must be a folder inside %s (got %s)" % (SCRATCH_ROOT, SCRATCH))
    if os.path.isdir(SCRATCH) and os.listdir(SCRATCH) and not os.path.isfile(os.path.join(SCRATCH, MARK)):
        raise SystemExit("refusing %s: not empty and not made by this harness (no %s)" % (SCRATCH, MARK))
    os.makedirs(SCRATCH, exist_ok=True)
    open(os.path.join(SCRATCH, MARK), "w").write("SkyyBank 0.1.6 harness scratch - safe to delete\n")


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
    """[(type, id or None, own text, parent index or None)] of every element in a rendered markup, in order"""
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


def hsum(d):
    return d.get("Left", 0) + d.get("Right", 0) + 2 * (d.get("Horizontal", 0) + d.get("Full", 0))


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
    best = 0.0
    for kind in (("regular", "bold") if bold else ("regular",)):
        adv = F[kind][0]
        best = max(best, sum(adv.get(ord(c), adv.get(ord("?"), 0.6)) for c in text) * size)
    return best


def wrap_lines(F, text, size, bold, width):
    lines, cur = 1, ""
    for word in text.split(" "):
        trial = (cur + " " + word) if cur else word
        if text_w(F, trial, size, bold) <= width or not cur:
            cur = trial
        else:
            lines += 1
            cur = word
    return lines


# ------------------------------------------------------------------------------------------------ scratch data (no JVM)
PLAYERS_FILE = """#SkyyProfiles player - profile list (edit only while the player is offline)
active=3
epoch=11
p.1.class=Archer
p.1.created=1790252693719
p.1.inv=1
p.1.lastPlayed=1790814665312
p.1.name=Strawberry
p.2.class=Warrior
p.2.created=1790253085025
p.2.inv=1
p.2.lastPlayed=1790814820601
p.2.name=Zucchini
p.3.class=Priest
p.3.created=1790772115598
p.3.lastPlayed=1791003473111
p.3.name=Banana
p.4.class=Warrior
p.4.created=1790814820591
p.4.inv=1
p.4.lastPlayed=1790816642133
p.4.name=Watermelon
prompted=1
switches=7
username=SkyLordPlayz
"""
COIN_FILES = {SKYY: 4750, SKYY + "-p2": 11500, SKYY + "-p3": PURSE0, SKYY + "-p4": P4_PURSE}
BANK_FILES = {SKYY: 222424, SKYY + "-p3": BANK0, SKYY + "-p4": P4_BANK}


def write_bal(path, v, head):
    open(path, "w", encoding="ascii").write("#%s\nbalance=%s\n" % (head, v))


def read_bal(path):
    if not os.path.exists(path):
        return None
    for ln in open(path, encoding="latin-1"):
        if ln.startswith("balance="):
            try:
                return int(ln.split("=", 1)[1].strip())
            except ValueError:
                return "bad"
    return None


def make_data(d, last_ms):
    """Skyy's data, synthetic and deterministic (modelled on the live files of 2026-10-02 22:57): players file (active 3, epoch 11),
    purses p1 4,750 / p2 11,500 / p3 14,700 / p4 4,368, banks p1 222,424 / p3 87,722 / p4 22,361, bank config 2% / 60 min / 10M"""
    shutil.rmtree(d, ignore_errors=True)
    for sub in ("Skyy_SkyyCoins/balances", "Skyy_SkyyBank/accounts", "Skyy_SkyyProfiles/players"):
        os.makedirs(os.path.join(d, sub))
    for k, v in COIN_FILES.items():
        write_bal(os.path.join(d, "Skyy_SkyyCoins", "balances", k + ".properties"), v, "SkyyCoins")
    for k, v in BANK_FILES.items():
        write_bal(os.path.join(d, "Skyy_SkyyBank", "accounts", k + ".properties"), v, "SkyyBank")
    open(os.path.join(d, "Skyy_SkyyProfiles", "players", SKYY + ".properties"), "w", encoding="ascii").write(PLAYERS_FILE)
    open(os.path.join(d, "Skyy_SkyyBank", "config.properties"), "w", encoding="ascii").write(
        "#SkyyBank config\ninterestPercent=2\nintervalMinutes=60\nlastInterestMillis=%d\nmaxPrincipal=10000000\n" % last_ms)


def live_dir():
    import skyybuild as B
    return os.path.join(B.USERDATA, "Saves", "HUD mod", "mods")


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride, JByte
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(hcls, exist_ok=True)
    SUI, K = kit_page()
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    os.chdir(SCRATCH)                     # any relative path the engine might touch lands in the scratch folder
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST, hcls], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    JARS = {"old": OLD, "new": JAR, "coins": COINS, "prof": PROFS}
    L = dict((k, loader(v)) for k, v in JARS.items())
    CB = dict((k, classes(v)) for k, v in JARS.items())

    # ---------------- A. load + verify + init
    for k in ("old", "new", "coins", "prof"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                tally("A " + k)
                OKS[0] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised (-Xverify:all): SkyyBank %s %d, SkyyBank %s %d, SkyyCoins %d, SkyyProfiles %d classes" % (
        OLD_VERSION, COUNT.get("A old", 0), VERSION, COUNT.get("A new", 0), COUNT.get("A coins", 0), COUNT.get("A prof", 0)))
    if FAILS:
        return

    # ---------------- B. class compare
    CPc = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IPc = JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        return CPc(False).makeClass(BAIS(b))

    BR_RE = re.compile(r"^(if\w*|goto(?:_w)?|jsr(?:_w)?) (\d+)$")

    def code_of(m):
        """a method's instructions with constant-pool indices resolved and every byte offset turned into an instruction number:
        0.1.6's constant pool is bigger, so a few `ldc` became `ldc_w` (one byte longer) and every later branch offset moved -
        an encoding difference, not a code difference"""
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, raw = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            raw.append((pos, str(IPc.instructionString(it, pos, cp))))
        at = dict((pos, i) for i, (pos, _t) in enumerate(raw))
        at[int(ca.getCodeLength())] = len(raw)
        out = []
        for pos, t in raw:
            t = re.sub(r"#\d+ = ", "", t).replace("ldc_w ", "ldc ")
            mm = BR_RE.match(t)
            if mm:
                t = "%s @%d" % (mm.group(1), at.get(int(mm.group(2)), -1))
            elif t.startswith("tableswitch") or t.startswith("lookupswitch"):
                t = re.sub(r"(default|-?\d+): (\d+)", lambda x: "%s: @%d" % (x.group(1), at.get(int(x.group(2)), -1)), t)
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%d @%d @%d %s" % (at.get(et.startPc(i), -1), at.get(et.endPc(i), -1), at.get(et.handlerPc(i), -1),
                                              cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        return dict((str(m.getMethodInfo().getName()) + str(m.getSignature()), code_of(m))
                    for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()))

    old, new = CB["old"], CB["new"]
    check(sorted(set(new) - set(old)) == [PKG + "BankWatch"] and not set(old) - set(new),
          "B. 0.1.6 = 0.1.5's 12 classes + BankWatch: %s / %s" % (sorted(set(new) - set(old)), sorted(set(old) - set(new))))
    same_bytes = sorted(n for n in old if n in new and old[n] == new[n])
    want_same = sorted(PKG + c for c in ("BankStore", "BankConfig", "BankTick", "BankJob", "BankCmd", "BankActionCmd", "BankAmountCmd",
                                         "BankConfigCmd", "BankConfigSetCmd", "BankConfigSetMaxCmd"))
    check(same_bytes == want_same, "B. the 10 money / command classes are byte-identical to 0.1.5: %s" % [n.rsplit(".", 1)[1] for n in same_bytes])
    po, pn = methods(ct(old[PKG + "SkyyBankPlugin"])), methods(ct(new[PKG + "SkyyBankPlugin"]))
    chg = sorted(k.split("(")[0] for k in po if k in pn and po[k] != pn[k])
    check(sorted(po) == sorted(pn) and chg == ["setup", "shutdown"], "B. SkyyBankPlugin: only setup / shutdown changed: %s" % chg)
    add_s = [l for l in pn["setup()V"] if l not in po["setup()V"]]
    add_d = [l for l in pn["shutdown()V"] if l not in po["shutdown()V"]]
    _ns = pn["setup()V"]
    _ex = [i for i in range(1, len(_ns)) if "putstatic" in _ns[i] and "BankWatch.EXEC" in _ns[i] and "getstatic" in _ns[i - 1]
           and "HytaleServer.SCHEDULED_EXECUTOR" in _ns[i - 1]]
    check(any("BankWatch.STOP" in l for l in add_s) and len(_ex) == 1 and any("BankWatch.STOP" in l for l in add_d),
          "B. setup writes BankWatch.STOP + EXEC (= HytaleServer.SCHEDULED_EXECUTOR), shutdown BankWatch.STOP: %s | %s" % (add_s[:6], add_d[:4]))
    ready_old = [e for e in cp_utf8(old[PKG + "SkyyBankPlugin"]) if ("] %s ready" % OLD_VERSION).encode() in e[2]]
    ready_new = [e for e in cp_utf8(new[PKG + "SkyyBankPlugin"]) if ("] %s ready" % VERSION).encode() in e[2]]
    LOG_NEW = ready_new[0][2].decode("utf8") if len(ready_new) == 1 else ""
    check(len(ready_old) == 1 and len(ready_new) == 1 and ("page %s)" % OLD_PAGE_ID) in ready_old[0][2].decode("utf8"),
          "B. one ready constant each; 0.1.5's names the checked page %s" % OLD_PAGE_ID)
    check(re.fullmatch(r"\[SkyyBank\] 0\.1\.6 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page [0-9a-f]{12}\) - /bank \(page\), interest ", LOG_NEW)
          is not None, "B. the 0.1.6 ready constant names the kit and the page id: %r" % LOG_NEW)
    co, cn = ct(old[PKG + "BankPage"]), ct(new[PKG + "BankPage"])
    fo = set((str(f.getName()), str(f.getSignature())) for f in co.getDeclaredFields())
    fn_ = set((str(f.getName()), str(f.getSignature())) for f in cn.getDeclaredFields())
    NEWF = {"tok", "seq", "base", "builtKey", "builtEpoch", "lastSend", "world", "watching", "dismissed", "probeNonce", "probeSeen",
            "handled", "heals", "watchFails", "SETTLE"}
    check(fo <= fn_ and set(n for n, _s in fn_ - fo) == NEWF, "B. BankPage: 0.1.5's fields + %s: %s" % (sorted(NEWF), sorted(fn_ - fo)))
    mo, mn = methods(co), methods(cn)
    same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
    changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
    added = sorted(k.split("(")[0] for k in mn if k not in mo)
    gone = sorted(k for k in mo if k not in mn)
    check(same == sorted(["jsonStr", "fmt", "colorOf", "textOf", "dur", "every", "subText", "rateText", "nextText", "gainText",
                          "payoutOn", "typed"]), "B. BankPage: 12 methods instruction-identical to 0.1.5: %s" % same)
    check(changed == ["<init>", "build", "handleDataEvent"] and not gone, "B. BankPage changed: %s (gone %s)" % (changed, gone))
    check(added == sorted(["who", "name", "onDismiss", "watchFail", "profileStill", "coinClick", "answer", "watchTick"]),
          "B. BankPage new methods: %s" % added)
    mw = methods(ct(new[PKG + "BankWatch"]))
    check(set(k.split("(")[0] for k in mw) - {"<clinit>"} == {"<init>", "hop", "run", "schedule"}, "B. BankWatch: %s" % sorted(mw))
    print("B. %d classes byte-identical to %s; SkyyBankPlugin: setup + shutdown (BankWatch.STOP, ready line); BankPage: %d methods "
          "identical, changed %s, new %s; BankWatch new" % (len(same_bytes), OLD_VERSION, len(same), changed, added))

    # ---------------- the engine stand-ins
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    HP = CPc(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
    HP.appendClassPath(JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def hclass(name, sup, ctor, fields=(), meths=(), ifaces=()):
        c = HP.makeClass(name, HP.get(sup)) if sup else HP.makeClass(name)
        for i_ in ifaces:
            c.addInterface(HP.get(i_))
        for s_ in fields:
            c.addField(CtField.make(s_, c))
        if ctor:
            c.addConstructor(CtNewConstructor.make(ctor, c))
        for s_ in meths:
            c.addMethod(CtNewMethod.make(s_, c))
        c.writeFile(hcls)

    hclass("skyybankharness.Net", "com.hypixel.hytale.server.core.io.PacketHandler",
           "public Net() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
           ["public java.util.ArrayList sent;"],
           ["public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean c) {\n"
            "  if (this.sent == null) this.sent = new java.util.ArrayList();\n  this.sent.add(p);\n  return true;\n}",
            "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
            "public String getIdentifier() { return \"skyybankharness\"; }"])
    hclass("com.hypixel.hytale.component.SkyyBankTestStore", "com.hypixel.hytale.component.Store",
           "public SkyyBankTestStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
           "(com.hypixel.hytale.component.IResourceStorage) null); }",
           ["public java.util.IdentityHashMap comps;"],
           ["public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
            "com.hypixel.hytale.component.ComponentType t) {\n  if (this.comps == null) return null;\n"
            "  java.util.Map m = (java.util.Map) this.comps.get(r);\n  if (m == null) return null;\n"
            "  return (com.hypixel.hytale.component.Component) m.get(t);\n}"])
    # a recording world: what is handed to its thread (World.execute) is kept and run by the harness, in order, as the thread would
    hclass("skyybankharness.World", "com.hypixel.hytale.server.core.universe.world.World",
           "public World() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }",
           ["public java.util.concurrent.ConcurrentLinkedQueue tasks;"],
           ["public void execute(java.lang.Runnable r) {\n  if (this.tasks == null) this.tasks = new java.util.concurrent.ConcurrentLinkedQueue();\n"
            "  this.tasks.add(r);\n}"])
    # "some other custom page" (the SkyWynn Menu in Skyy's session)
    hclass("skyybankharness.OtherPage", "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
           "public OtherPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, "
           "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime.CanDismiss); }",
           [], ["public void build(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b, "
                "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder e, com.hypixel.hytale.component.Store s) { "
                "b.appendInline((String) null, \"Group #SkyyMStandIn { Anchor: (Width: 100, Height: 100); }\"); "
                "e.addEventBinding(com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType.Activating, \"#SkyyMStandIn\", "
                "com.hypixel.hytale.server.core.ui.builder.EventData.of(\"m\", \"tile\")); }"])
    hclass("skyybankharness.LookupIn", None, None, [],
           ["public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
            "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}"])
    # X control: the 0.3 SkyyUiProbe mistake - a class that is no page calling a page's protected rebuild(); written to its own
    # folder (not on the JVM class path) and loaded under the 0.1.6 jar's loader, so it resolves BankPage like the mod's classes do
    hcls2 = os.path.join(SCRATCH, "hclasses2")
    os.makedirs(hcls2, exist_ok=True)
    bad = HP.makeClass("skyybankharness.BadCaller")
    bad.addMethod(CtNewMethod.make("public static void poke(com.skyy.bank.BankPage p) { p.rebuild(); }", bad))
    bad.writeFile(hcls2)
    NET, TSC, HW, OTHER = (JClass("skyybankharness.Net"), JClass("com.hypixel.hytale.component.SkyyBankTestStore"),
                           JClass("skyybankharness.World"), JClass("skyybankharness.OtherPage"))
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    STc = JClass("com.hypixel.hytale.component.Store")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    CPE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent")
    CPT = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType")
    PAGE_E = JClass("com.hypixel.hytale.protocol.packets.interface_.Page")
    CPK = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    System = JClass("java.lang.System")
    nxt = [900]

    def ctype():
        c = CTc()
        nxt[0] += 1
        jf(CTc.class_, "index").setInt(c, nxt[0])
        jf(CTc.class_, "hashCode").setInt(c, nxt[0])
        return c

    CT_PR, CT_PLA = ctype(), ctype()
    uni = U.allocateInstance(Uni.class_)
    jf(Uni.class_, "playerRefComponentType").set(uni, CT_PR)
    WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
    jf(Uni.class_, "worldsByUuid").set(uni, WORLDS)
    jf(Uni.class_, "players").set(uni, JClass("java.util.ArrayList")())
    jf(Uni.class_, "instance").set(None, uni)
    em = U.allocateInstance(EMc.class_)
    jf(EMc.class_, "playerComponentType").set(em, CT_PLA)
    jf(EMc.class_, "instance").set(None, em)

    def world():
        w = U.allocateInstance(HW.class_)
        u = UUID.randomUUID()
        WORLDS.put(u, w)
        return w, u

    W1, W1U = world()
    W2, W2U = world()
    SK = UUID.fromString(SKYY)
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
    RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(RECS)

    def logs():
        out = []
        for i in range(int(RECS.size())):
            r = RECS.get(i)
            try:
                out.append("%s %s" % (r.getLevel(), r.getMessage()))
            except Exception:
                out.append(str(r))
        return [x for x in out if "[Skyy" in x]

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    CS, CF = JClass("com.skyy.coins.CoinStore", loader=L["coins"]), JClass("com.skyy.coins.CoinFn", loader=L["coins"])
    PS, KF = JClass("com.skyy.profiles.ProfStore", loader=L["prof"]), JClass("com.skyy.profiles.KeyFn", loader=L["prof"])
    JClass("com.skyy.profiles.ProfCfg", loader=L["prof"]).LOG = HL.get("SkyyProfilesHarness")
    CS.LOG = HL.get("SkyyCoinsHarness")
    for k in ("old", "new"):
        jc(k, "BankStore").LOG = HL.get("SkyyBankHarness" + k)
    jc("new", "BankWatch").STOP = True                    # no background checks unless a part starts them (W)
    REAL = {}

    def bridge_real():
        for key in ("get", "add", "take"):
            REAL[key] = CF(key)
            BR.put("coins:fn:" + key, REAL[key])
        REAL["key"] = KF()
        BR.put("profile:fn:key", REAL["key"])
        PS.publish(SK)

    def fresh(tag, k, bridge=True):
        """a scratch copy of Skyy's data, the three mods (version k of SkyyBank) pointed at it; returns (dir, BankStore, BankConfig)"""
        d = os.path.join(SCRATCH, "data", k, tag)
        make_data(d, int(System.currentTimeMillis()) - 600000)      # interest last paid 10 min ago: nothing due during a part
        BR.clear()
        RECS.clear()
        CS.DIR = Paths.get(os.path.join(d, "Skyy_SkyyCoins", "balances"))
        CS.BAL.clear()
        CS.LOADED.clear()
        PS.DIR = Paths.get(os.path.join(d, "Skyy_SkyyProfiles", "players"))
        PS.DATA.clear()
        BS, BC = jc(k, "BankStore"), jc(k, "BankConfig")
        BS.DIR = Paths.get(os.path.join(d, "Skyy_SkyyBank", "accounts"))
        BS.BAL.clear()
        BS.LOADED.clear()
        BS.EPOCH.clear()
        BC.FILE = Paths.get(os.path.join(d, "Skyy_SkyyBank", "config.properties"))
        BC.load()
        if bridge:
            bridge_real()
        return d, BS, BC

    def money(d):
        """{profile: (purse, bank)} straight from the files"""
        out = {}
        for p, key in (("p1", SKYY), ("p2", SKYY + "-p2"), ("p3", SKYY + "-p3"), ("p4", SKYY + "-p4")):
            out[p] = (read_bal(os.path.join(d, "Skyy_SkyyCoins", "balances", key + ".properties")),
                      read_bal(os.path.join(d, "Skyy_SkyyBank", "accounts", key + ".properties")))
        return out

    def total(m):
        """every readable purse + bank (an unreadable file counts nothing)"""
        return sum(v for pair in m.values() for v in pair if isinstance(v, int))

    TOTAL0 = sum(COIN_FILES.values()) + sum(BANK_FILES.values())

    def player(w=None, wu=None):
        """a stand-in Skyy in world w: Store + Ref + PlayerRef + Player holding the engine's own PageManager / WindowManager"""
        st = U.allocateInstance(TSC.class_)
        ref = U.allocateInstance(REFc.class_)
        jf(REFc.class_, "store").set(ref, st)
        pr = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(pr, SK)
        jf(PR.class_, "username").set(pr, "SkyLordPlayz")
        net = U.allocateInstance(NET.class_)
        jf(PR.class_, "packetHandler").set(pr, net)
        jf(PR.class_, "entity").set(pr, ref)
        jf(PR.class_, "worldUuid").set(pr, wu if wu is not None else W1U)
        pl = U.allocateInstance(PLAc.class_)
        wm = WMc()
        wm.init(pr)
        pm = PMc()
        pm.init(pr, wm)
        jf(PLAc.class_, "windowManager").set(pl, wm)
        jf(PLAc.class_, "pageManager").set(pl, pm)
        comps = JClass("java.util.IdentityHashMap")()
        comps.put(CT_PR, pr)
        comps.put(CT_PLA, pl)
        allc = JClass("java.util.IdentityHashMap")()
        allc.put(ref, comps)
        st.comps = allc
        es = U.allocateInstance(ESc.class_)
        jf(ESc.class_, "world").set(es, w if w is not None else W1)
        jf(STc.class_, "externalData").set(st, es)
        return pr, ref, st, pm, net

    def acks(pm):
        return int(jf(PMc.class_, "customPageRequiredAcknowledgments").get(pm).get())

    def sent(net):
        return [] if net.sent is None else [net.sent.get(i) for i in range(int(net.sent.size()))]

    PACKETS = []                           # every CustomPage 0.1.6 sent (P)

    class Client:
        """the game client as far as the engine's acknowledgement rule needs it (inferred - see the docstring)"""

        def __init__(s, pm, ref, st, net, ver):
            s.pm, s.ref, s.st, s.net, s.ver = pm, ref, st, net, ver
            s.page, s.seen, s.waiting, s.binds, s.errors = None, 0, False, {}, []

        def ack(s):
            try:
                s.pm.handleEvent(s.ref, s.st, CPE(CPT.Acknowledge, None))
            except Exception as e:
                s.errors.append(str(e))

        def pump(s):
            ps = sent(s.net)
            for p in ps[s.seen:]:
                kind = str(p.getClass().getSimpleName())
                if kind == "CustomPage":
                    if s.ver == "new" and str(p.key) == PKG + "BankPage":
                        PACKETS.append(p)
                    if bool(p.isInitial) or (s.page is not None and str(p.key) == s.page):
                        s.page, s.waiting = str(p.key), False
                        if bool(p.clear) or bool(p.isInitial):
                            s.binds = dict((str(e.selector), None if e.data is None else str(e.data)) for e in p.eventBindings)
                        s.ack()
                elif kind == "SetPage":
                    if s.page is not None:
                        s.page, s.waiting = None, False
                        s.ack()
            s.seen = len(ps)

        def press(s, sel, amount="", binds=None):
            """click `sel` as the client does: the binding's EventData, '@'-keys filled with the element value"""
            b = (binds or s.binds).get(sel)
            if b is None:
                raise KeyError("no binding for %s" % sel)
            d = json.loads(b)
            for key in list(d):
                if key.startswith("@"):
                    d[key] = amount
            s.waiting = True
            s.pm.handleEvent(s.ref, s.st, CPE(CPT.Data, json.dumps(d)))
            s.pump()

        def esc(s):
            if s.page is not None:
                s.page, s.waiting = None, False
                s.pm.handleEvent(s.ref, s.st, CPE(CPT.Dismiss, None))

        def world_change(s):
            """the player changes world: the client drops its page; World.onSetupPlayerJoining clears the server's counter only"""
            s.page, s.waiting = None, False
            s.pm.clearCustomPageAcknowledgements()

    def open_bank(k, pr, ref, st, pm, cl):
        pg = jc(k, "BankPage")(pr)
        pm.openCustomPage(ref, st, pg)
        cl.pump()
        return pg

    def cur(pm, pg):
        c = pm.getCustomPage()
        return c is not None and c.equals(pg)

    def info(pg):
        return str(pg.info)

    def settle(pg):
        """as if 1.5 s passed since the page's last packet (the check waits BankPage.SETTLE after it)"""
        pg.lastSend = int(System.currentTimeMillis()) - 1500

    SEEN_INFO = set()

    def note(pg):
        SEEN_INFO.add(info(pg))

    # ---------------- R. the root cause on the engine
    # (4) the late-found bridges: SkyyBank first (nothing in the bridge yet), SkyyCoins / SkyyProfiles register afterwards
    for k in ("old", "new"):
        d, BS, BC = fresh("late-" + k, k, bridge=False)
        check(not bool(BS.coinsReady()) and str(BS.pkey(SK)) == SKYY, "R4. %s: at start the bank finds no coins / profiles bridge "
              "(the ready line's 'NOT found yet')" % k)
        bridge_real()
        check(bool(BS.coinsReady()) and str(BS.pkey(SK)) == SKYY + "-p3", "R4. %s: registered later, found on the next call (key %s)"
              % (k, BS.pkey(SK)))
        pr, ref, st, pm, net = player()
        cl = Client(pm, ref, st, net, k)
        pg = open_bank(k, pr, ref, st, pm, cl)
        cl.press("#SkyyBDepAll")
        m = money(d)
        check(m["p3"] == (0, BANK0 + PURSE0) and not cl.waiting and info(pg).startswith("+Deposited %d coins" % PURSE0),
              "R1. %s healthy: /bank -> ack -> DEPOSIT ALL moved %d into the bank (%s), answered (%r)" % (k, PURSE0, m["p3"], info(pg)[:60]))
        check(acks(pm) == 0 and not cl.errors, "R1. %s: every page packet acknowledged (%d pending, %s)" % (k, acks(pm), cl.errors))
        check(total(m) == TOTAL0, "R1. %s: coins conserved (%d / %d)" % (k, total(m), TOTAL0))
        note(pg)
    # (2) Skyy's session: a page open, a world change, then a bench / the menu's close -> /bank -> every button
    for trig in ("bench", "menuclose"):
        for k in ("old", "new"):
            d, BS, BC = fresh("stuck-%s-%s" % (trig, k), k)
            pr, ref, st, pm, net = player()
            cl = Client(pm, ref, st, net, k)
            menu = OTHER(pr)
            pm.openCustomPage(ref, st, menu)
            cl.pump()
            cl.world_change()                                      # /island from the menu
            stale = cur(pm, menu)
            n0 = len(sent(net))
            if trig == "bench":
                pm.setPage(ref, st, PAGE_E.Bench, True)            # setPageWithWindows(Bench, ...) runs this first
            else:
                pm.setPage(ref, st, PAGE_E.valueOf("None"))        # SkyyMenu CloseTask -> MenuPage.closePage
            cl.pump()
            check(stale and acks(pm) == 1, "R2. %s/%s: the page stays open on the server across the world change (%s) and the %s "
                  "leaves 1 acknowledgement the client never sends (%d pending)" % (trig, k, stale, trig, acks(pm)))
            pg = open_bank(k, pr, ref, st, pm, cl)
            check(cl.page is not None and cur(pm, pg), "R2. %s/%s: /bank draws the page" % (trig, k))
            if k == "old":
                for sel, amt in (("#SkyyBDepAll", ""), ("#SkyyBDep", "500"), ("#SkyyBWd", "500"), ("#SkyyBWdAll", ""),
                                 ("#SkyyBRefresh", ""), ("#SkyyBClose", "")):
                    n0, i0 = len(sent(net)), info(pg)
                    cl.press(sel, amt)
                    check(info(pg) == i0 and len(sent(net)) == n0 and cl.waiting and cur(pm, pg),
                          "R2. %s/0.1.5: %s is DROPPED by the engine - the handler never ran, no packet, the client keeps waiting "
                          "('Loading...')" % (trig, sel))
                    cl.waiting = False
                check(money(d)["p3"] == (PURSE0, BANK0) and not logs(), "R2. %s/0.1.5: coins untouched (%s), no SkyyBank line (%s)" % (
                    trig, money(d)["p3"], logs()))
                cl.esc()
                check(pm.getCustomPage() is None, "R2. %s/0.1.5: Esc still closes the page" % trig)
                pg2 = open_bank(k, pr, ref, st, pm, cl)
                cl.press("#SkyyBDepAll")
                check(info(pg2) == "" and cl.waiting and acks(pm) == 1, "R2. %s/0.1.5: /bank again - still dropped (%d pending)" % (
                    trig, acks(pm)))
                cl.world_change()                                  # e.g. /hub: the only reset
                pg3 = open_bank(k, pr, ref, st, pm, cl)
                cl.press("#SkyyBDepAll")
                check(money(d)["p3"] == (0, BANK0 + PURSE0) and not cl.waiting, "R2. %s/0.1.5: after the next world change Deposit "
                      "all works again (%s)" % (trig, money(d)["p3"]))
            else:
                n0 = len(sent(net))
                cl.press("#SkyyBDepAll")
                check(cl.waiting and len(sent(net)) == n0 and money(d)["p3"] == (PURSE0, BANK0),
                      "R2. %s/0.1.6: the first Deposit all is still dropped by the engine (nothing moved, client waiting)" % trig)
                settle(pg)
                again = bool(pg.watchTick(W1))
                cl.pump()
                lw = [l for l in logs() if "WARNING" in l and "dropping" in l]
                check(again and not cl.waiting and info(pg) == TXT["heal"] and len(lw) == 1 and int(pg.heals) == 1,
                      "R2. %s/0.1.6: the page check finds the dropped clicks, logs one WARNING, resets and ANSWERS - the client stops "
                      "waiting (%r, %s)" % (trig, info(pg)[:50], lw))
                check(acks(pm) == 0 and not cl.errors, "R2. %s/0.1.6: acknowledgements back in step (%d pending, %s)" % (
                    trig, acks(pm), cl.errors))
                note(pg)
                cl.press("#SkyyBDepAll")
                m = money(d)
                check(m["p3"] == (0, BANK0 + PURSE0) and not cl.waiting and info(pg).startswith("+Deposited %d" % PURSE0),
                      "R2. %s/0.1.6: the next Deposit all moved %d ONCE (%s) and answered" % (trig, PURSE0, m["p3"]))
                check(total(m) == TOTAL0, "R2. %s/0.1.6: coins conserved" % trig)
                settle(pg)
                n0 = len(sent(net))
                check(bool(pg.watchTick(W1)) and len(sent(net)) == n0 and int(pg.heals) == 1,
                      "R2. %s/0.1.6: a healthy page's check sends nothing" % trig)
    # (3) the bank page ITSELF open across a world change
    for k in ("old", "new"):
        d, BS, BC = fresh("bankstale-" + k, k)
        pr, ref, st, pm, net = player()
        cl = Client(pm, ref, st, net, k)
        pg = open_bank(k, pr, ref, st, pm, cl)
        cl.world_change()
        jf(PR.class_, "worldUuid").set(pr, W2U)
        if k == "new":
            n0, a0 = len(sent(net)), acks(pm)
            settle(pg)
            again = bool(pg.watchTick(W2))
            check(not again and pm.getCustomPage() is None and len(sent(net)) == n0 and acks(pm) == a0 and bool(pg.dismissed)
                  and any("world change" in l and "INFO" in l for l in logs()),
                  "R3. 0.1.6: the check on the new world forgets the stale bank page on the server (Dismiss: no packet, counter "
                  "unchanged, one INFO line) and ends")
        pm.setPage(ref, st, PAGE_E.Bench, True)
        cl.pump()
        pend = acks(pm)
        pg2 = open_bank(k, pr, ref, st, pm, cl)
        cl.press("#SkyyBDepAll")
        if k == "old":
            check(pend == 1 and cl.waiting and money(d)["p3"] == (PURSE0, BANK0),
                  "R3. 0.1.5: the bank page left open across the world change + a bench -> stuck, the next Deposit all is dropped")
        else:
            check(pend == 0 and not cl.waiting and money(d)["p3"] == (0, BANK0 + PURSE0),
                  "R3. 0.1.6: the bench after it stays in step (0 pending) and the next Deposit all works (%s)" % (money(d)["p3"],))
    print("R. root cause: healthy Deposit all = 14,700 -> bank 102,422 on both jars; after a world change + a bench / the menu's close "
          "0.1.5 drops all 6 buttons silently (Skyy's screenshot), 0.1.6 heals on its next check and answers; a stale bank page is "
          "forgotten on the new world; the late-found bridges are found on the first click")

    # ---------------- W. the page check's real timer (HytaleServer.SCHEDULED_EXECUTOR -> World.execute -> watchTick)
    BW = jc("new", "BankWatch")
    # no scheduler handed over (SkyyBank not set up): the page still works, the check is off, said once a minute
    BW.STOP = False
    BW.EXEC = None
    BW.WARNED = 0
    d, BS, BC = fresh("noexec", "new")
    pr, ref, st, pm, net = player()
    cl = Client(pm, ref, st, net, "new")
    pg = open_bank("new", pr, ref, st, pm, cl)
    pg2 = open_bank("new", pr, ref, st, pm, cl)
    lw = [l for l in logs() if "could not be scheduled" in l]
    cl.press("#SkyyBDepAll")
    check(len(lw) == 1 and money(d)["p3"] == (0, BANK0 + PURSE0) and not cl.waiting,
          "W. without a scheduler the page still works and the check's absence is logged once (%d line(s))" % len(lw))
    # the engine's scheduler, built the way HytaleServer.<clinit> builds SCHEDULED_EXECUTOR (the real class cannot initialise in a
    # bare JVM: it needs the server's command-line options); handed over as SkyyBankPlugin.setup() does
    try:
        TF = JClass("com.hypixel.hytale.server.core.util.concurrent.ThreadUtil").daemon("Scheduler")
        EXEC = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(TF)
    except Exception as e:
        print("   (ThreadUtil.daemon unavailable: %s - plain scheduler)" % e)
        EXEC = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()
    BW.EXEC = EXEC

    def wait_task(w, secs=3.5):
        t_end = time.time() + secs
        while time.time() < t_end:
            if w.tasks is not None and not w.tasks.isEmpty():
                return w.tasks.poll()
            time.sleep(0.05)
        return None

    def drain(*ws):
        for w in ws:
            if w.tasks is not None:
                w.tasks.clear()

    try:
        d, BS, BC = fresh("watch", "new")
        drain(W1, W2)
        pr, ref, st, pm, net = player()
        cl = Client(pm, ref, st, net, "new")
        pg = open_bank("new", pr, ref, st, pm, cl)
        t0 = time.time()
        task = wait_task(W1)
        check(task is not None and str(task.getClass().getName()) == PKG + "BankWatch" and task.target is not None
              and task.target.equals(W1) and time.time() - t0 >= 0.8,
              "W. ~1 s after the open the scheduler-thread hop handed a BankWatch for the player's world to World.execute (%.2f s)"
              % (time.time() - t0))
        n0 = len(sent(net))
        if task is not None:
            task.run()                                         # what the world thread does with it
        check(len(sent(net)) == n0 and int(pg.heals) == 0 and not cl.waiting, "W. healthy page: the check sent nothing")
        task = wait_task(W1)
        check(task is not None, "W. ... and it checks again a second later")
        # a stray page packet the client never acknowledges (another mod updating a page the client does not show)
        stray = CPK("skyybankharness.Elsewhere", False, True, pg.getLifetime(), JArray(JClass("com.hypixel.hytale.protocol.packets.interface_.CustomUICommand"))(0),
                    JArray(JClass("com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBinding"))(0))
        pm.updateCustomPage(stray)
        cl.pump()
        check(acks(pm) == 1, "W. a stray page packet leaves 1 acknowledgement pending (%d)" % acks(pm))
        cl.press("#SkyyBDep", "500")
        check(cl.waiting and money(d)["p3"] == (PURSE0, BANK0), "W. ... so the engine drops a Deposit 500 click")
        if task is not None:
            task.run()
        cl.pump()
        check(not cl.waiting and info(pg) == TXT["heal"] and int(pg.heals) == 1 and acks(pm) == 0,
              "W. the next timer check heals it: answered (%r), 0 pending" % info(pg)[:40])
        cl.press("#SkyyBDep", "500")
        check(money(d)["p3"] == (PURSE0 - 500, BANK0 + 500) and not cl.waiting, "W. ... and the click after it moves 500 once (%s)"
              % (money(d)["p3"],))
        # the player moves to another world with the page open: the check follows the player and forgets the page there
        drain(W1, W2)
        cl.world_change()
        jf(PR.class_, "worldUuid").set(pr, W2U)
        task = wait_task(W2)
        check(task is not None and task.target.equals(W2) and (W1.tasks is None or W1.tasks.isEmpty()),
              "W. after a world change the hop hands the check to the NEW world")
        n0 = len(sent(net))
        if task is not None:
            task.run()
        check(pm.getCustomPage() is None and len(sent(net)) == n0 and bool(pg.dismissed), "W. ... which forgets the page (no packet)")
        check(wait_task(W1, 2.2) is None and wait_task(W2, 0.1) is None, "W. ... and the check ends (nothing more queued)")
        # between worlds (no world for the player's world id): it waits, then finds the world
        jf(PR.class_, "worldUuid").set(pr, W1U)
        pg = open_bank("new", pr, ref, st, pm, cl)
        jf(PR.class_, "worldUuid").set(pr, UUID.randomUUID())
        check(wait_task(W1, 1.6) is None, "W. between worlds (unknown world id): nothing handed to any world")
        jf(PR.class_, "worldUuid").set(pr, W1U)
        task = wait_task(W1, 2.5)
        check(task is not None, "W. ... and once the player is in a world again, the check reaches it")
        # closed / replaced page: ends
        if task is not None:
            cl.esc()
            task.run()
            check(wait_task(W1, 2.2) is None, "W. Esc (Dismiss) ends the check")
        pg = open_bank("new", pr, ref, st, pm, cl)
        pg_b = open_bank("new", pr, ref, st, pm, cl)                  # a second /bank replaces it
        check(bool(pg.dismissed) and not bool(pg_b.dismissed), "W. a replaced page is dismissed (onDismiss)")
        task = wait_task(W1)
        if task is not None and task.page.equals(pg):
            task.run()
            task = wait_task(W1)
        check(task is not None and task.page.equals(pg_b), "W. only the open page keeps a check")
        # player gone (the open page's check is running: one more check, then the player leaves)
        if task is not None:
            task.run()
        jf(PR.class_, "entity").set(pr, None)
        drain(W1)
        check(wait_task(W1, 2.2) is None, "W. the player left (PlayerRef invalid): the check ends")
        jf(PR.class_, "entity").set(pr, ref)
        # STOP (plugin shutdown)
        pg = open_bank("new", pr, ref, st, pm, cl)
        BW.STOP = True
        drain(W1)
        check(wait_task(W1, 2.2) is None, "W. BankWatch.STOP (shutdown): no more checks")
        check(total(money(d)) == TOTAL0, "W. coins conserved")
    finally:
        BW.STOP = True
        time.sleep(1.2)
        drain(W1, W2)
        try:
            EXEC.shutdownNow()
        except Exception:
            pass
    print("W. the page check's timer: hop on the engine's scheduler thread -> World.execute -> the check; healthy = silent, a stray "
          "packet healed on the next check, follows the player to a new world and forgets the page there, waits between worlds, "
          "ends on Esc / replace / leave / STOP")

    # ---------------- E. every button with Skyy's numbers (0.1.6), through the engine, real SkyyCoins / SkyyProfiles
    def step(tag, d, cl, pg, want_p3=None, text=None, prefix=None, t=None, others=None):
        m = money(d)
        ok = True
        if want_p3 is not None:
            ok = check(m["p3"] == want_p3, "E. %s: profile 3 purse / bank %s, want %s" % (tag, m["p3"], want_p3)) and ok
        if text is not None:
            ok = check(info(pg) == text, "E. %s: result %r, want %r" % (tag, info(pg), text)) and ok
        if prefix is not None:
            ok = check(info(pg).startswith(prefix), "E. %s: result %r, want it to start %r" % (tag, info(pg), prefix)) and ok
        ok = check(not cl.waiting, "E. %s: answered (the client is not left waiting)" % tag) and ok
        ok = check(total(m) == (TOTAL0 if t is None else t), "E. %s: coins conserved (%d, want %d)" % (tag, total(m), TOTAL0 if t is None else t)) and ok
        ok = check(not cl.errors, "E. %s: no unexpected acknowledgement (%s)" % (tag, cl.errors)) and ok
        if others is not None:
            ok = check(dict((p, m[p]) for p in others) == others, "E. %s: the other profiles untouched %s" % (tag, m)) and ok
        note(pg)
        tally("E steps")
        return ok

    def session(tag):
        d, BS, BC = fresh(tag, "new")
        pr, ref, st, pm, net = player()
        cl = Client(pm, ref, st, net, "new")
        pg = open_bank("new", pr, ref, st, pm, cl)
        return d, BS, pr, ref, st, pm, net, cl, pg

    OTHERS = {"p1": (4750, 222424), "p2": (11500, None), "p4": (P4_PURSE, P4_BANK)}
    d, BS, pr, ref, st, pm, net, cl, pg = session("buttons")
    cl.press("#SkyyBDepAll")
    step("Deposit all", d, cl, pg, (0, 102422), "+Deposited 14700 coins. Bank: 102422  |  Purse: 0", others=OTHERS)
    cl.press("#SkyyBWdAll")
    step("Withdraw all", d, cl, pg, (102422, 0), "+Withdrew 102422 coins. Bank: 0  |  Purse: 102422", others=OTHERS)
    cl.press("#SkyyBDep", "87,722")
    step("Deposit 87,722", d, cl, pg, (PURSE0, BANK0), "+Deposited 87722 coins. Bank: 87722  |  Purse: 14700")
    check(str(pg.keepAmount) == "", "E. the amount box is cleared after a done move")
    cl.press("#SkyyBDep", "500")
    step("Deposit 500", d, cl, pg, (PURSE0 - 500, BANK0 + 500), "+Deposited 500 coins. Bank: 88222  |  Purse: 14200")
    cl.press("#SkyyBWd", "2k")
    step("Withdraw 2k", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500), "+Withdrew 2000 coins. Bank: 86222  |  Purse: 16200")
    cl.press("#SkyyBDep", "1.5m")
    step("Deposit 1.5m (too much)", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500), "-Not enough coins in your purse (16200).")
    check(str(pg.keepAmount) == "1.5m", "E. a refused amount stays in the box")
    cl.press("#SkyyBWd", "")
    step("Withdraw (empty box)", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500),
         "=Type an amount in the box first (500, 2k, 1.5m or all), then click Withdraw.")
    cl.press("#SkyyBWd", "abc")
    step("Withdraw abc", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500), "-That is not a number. Use e.g. 500, 2k, 1.5m or all.")
    cl.press("#SkyyBRefresh")
    step("Refresh", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500), "")
    cl.press("#SkyyBAmount", "250")
    step("Enter 250", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500), "=Click Deposit or Withdraw to move 250 coins. Enter alone never moves coins.")
    cl.press("#SkyyBAmount", "")
    step("Enter (empty)", d, cl, pg, (PURSE0 + 1500, BANK0 - 1500), "=Type an amount (500, 2k, 1.5m or all), then click Deposit or Withdraw.")
    cl.press("#SkyyBWd", "all")
    step("Withdraw all (typed)", d, cl, pg, (PURSE0 + BANK0, 0), "+Withdrew 86222 coins. Bank: 0  |  Purse: 102422")
    # unknown / malformed clicks are answered too
    for data, label in (('{"a":"bogus","@BAmount":"5"}', "an unknown action"), ('{"@BAmount":"5"}', "no action"), ("not json", "malformed"),
                        ('{"a":"skyybankcheck","n":"forged"}', "a forged check click")):
        cl.waiting = True
        pm.handleEvent(ref, st, CPE(CPT.Data, data))
        cl.pump()
        step("click with %s" % label, d, cl, pg, (PURSE0 + BANK0, 0), TXT["unknown"])
    n0 = len(sent(net))
    cl.press("#SkyyBClose")
    check(pm.getCustomPage() is None and cl.page is None and str(sent(net)[-1].getClass().getSimpleName()) == "SetPage" and acks(pm) == 0,
          "E. Close: the page closes (SetPage None, acknowledged)")
    check(money(d)["p3"] == (PURSE0 + BANK0, 0), "E. Close moved nothing")
    # zero purse / empty bank
    d, BS, pr, ref, st, pm, net, cl, pg = session("zero")
    write_bal(os.path.join(d, "Skyy_SkyyCoins", "balances", SKYY + "-p3.properties"), 0, "SkyyCoins")
    CS.BAL.clear()
    CS.LOADED.clear()
    cl.press("#SkyyBDepAll")
    step("Deposit all, purse 0", d, cl, pg, (0, BANK0), "-Nothing to deposit.", t=TOTAL0 - PURSE0)
    cl.press("#SkyyBWdAll")
    step("Withdraw all", d, cl, pg, (BANK0, 0), prefix="+Withdrew 87722", t=TOTAL0 - PURSE0)
    cl.press("#SkyyBWdAll")
    step("Withdraw all, bank 0", d, cl, pg, (BANK0, 0), "-Nothing to withdraw.", t=TOTAL0 - PURSE0)
    # double click: the second click carries the first click's token
    for how in ("gate", "direct"):
        d, BS, pr, ref, st, pm, net, cl, pg = session("double-" + how)
        b1 = dict(cl.binds)
        cl.press("#SkyyBDepAll")
        tok1 = json.loads(b1["#SkyyBDepAll"])["t"]
        if how == "gate":
            pm.clearCustomPageAcknowledgements()      # as if the engine's own gate were open (a world change / the check's reset)
            cl.press("#SkyyBDepAll", binds=b1)
        else:
            pg.handleDataEvent(ref, st, json.dumps({"a": "depall", "@BAmount": "", "t": tok1}))
            cl.pump()
        step("double click (%s)" % how, d, cl, pg, (0, BANK0 + PURSE0), TXT["old"])
        b2 = dict(cl.binds)
        cl.press("#SkyyBDep", "500")                     # nothing left to deposit: refused, but a fresh token works
        cl.press("#SkyyBWd", "1k")
        b3 = dict(cl.binds)
        cl.press("#SkyyBWd", "1k")
        pg.handleDataEvent(ref, st, json.dumps({"a": "withdraw", "@BAmount": "1k", "t": json.loads(b3["#SkyyBWd"])["t"]}))
        cl.pump()
        step("double Withdraw 1k (%s)" % how, d, cl, pg, (2000, BANK0 + PURSE0 - 2000), TXT["old"])
        check(json.loads(b1["#SkyyBDepAll"])["t"] != json.loads(b2["#SkyyBDepAll"])["t"], "E. every answer carries a new click token")
    # no SkyyCoins
    d, BS, pr, ref, st, pm, net, cl, pg = session("nocoins")
    for key in ("get", "add", "take"):
        BR.remove("coins:fn:" + key)
    cl.press("#SkyyBDepAll")
    step("no SkyyCoins: Deposit all", d, cl, pg, (PURSE0, BANK0), "-SkyyCoins is not loaded, the bank cannot move coins.")
    cl.press("#SkyyBWd", "500")
    step("no SkyyCoins: Withdraw 500", d, cl, pg, (PURSE0, BANK0), "-SkyyCoins is not loaded, the bank cannot move coins.")
    # SkyyCoins failing
    FAIL = {"mode": None}

    @JImplements("java.util.function.Function")
    class Flaky:
        def __init__(self, key):
            self.key = key

        @JOverride
        def apply(self, a):
            if FAIL["mode"] == self.key + ":throw":
                raise JClass("java.lang.IllegalStateException")("harness: coins:fn:%s throws" % self.key)
            if FAIL["mode"] == self.key + ":null":
                return None
            return REAL[self.key].apply(a)

    def flaky():
        for key in ("get", "add", "take"):
            BR.put("coins:fn:" + key, Flaky(key))

    PURSE_BAD = "-Your purse cannot be read right now, nothing was moved. Try again; if it keeps happening tell an admin (server log)."
    for mode, sel, amt in (("take:throw", "#SkyyBDepAll", ""), ("take:null", "#SkyyBDep", "500"), ("get:null", "#SkyyBDepAll", ""),
                           ("add:null", "#SkyyBWdAll", ""), ("add:throw", "#SkyyBWd", "500")):
        d, BS, pr, ref, st, pm, net, cl, pg = session("flaky-" + mode.replace(":", "-"))
        flaky()
        FAIL["mode"] = mode
        cl.press(sel, amt)
        FAIL["mode"] = None
        step("SkyyCoins %s on %s" % (mode, sel), d, cl, pg, (PURSE0, BANK0), PURSE_BAD)
    # the REAL SkyyCoins with an unreadable purse file (coins:fn:* answer null, CoinStore writes nothing)
    d, BS, pr, ref, st, pm, net, cl, pg = session("purse-unreadable")
    pf = os.path.join(d, "Skyy_SkyyCoins", "balances", SKYY + "-p3.properties")
    open(pf, "w", encoding="ascii").write("balance=not a number\n")
    CS.BAL.clear()
    CS.LOADED.clear()
    before = open(pf, "rb").read()
    for sel, amt in (("#SkyyBDepAll", ""), ("#SkyyBDep", "500"), ("#SkyyBWd", "500"), ("#SkyyBWdAll", "")):
        cl.press(sel, amt)
        step("unreadable purse file: %s" % sel, d, cl, pg, ("bad", BANK0), PURSE_BAD, t=TOTAL0 - PURSE0)
    check(open(pf, "rb").read() == before, "E. the unreadable purse file was never overwritten")
    # the account file turns unreadable AFTER the purse was charged (BankStore.deposit: creditK refuses, the purse is refunded)
    d, BS, pr, ref, st, pm, net, cl, pg = session("account-breaks")
    af = os.path.join(d, "Skyy_SkyyBank", "accounts", SKYY + "-p3.properties")

    def break_account():
        open(af, "w", encoding="ascii").write("balance=broken" + chr(10))
        BS.BAL.clear()
        BS.LOADED.clear()

    for k2 in ("get", "add", "take"):
        BR.put("coins:fn:" + k2, REAL[k2])
    HOOK0 = {"on": True}

    @JImplements("java.util.function.Function")
    class TakeThenBreak:
        @JOverride
        def apply(self, a):
            r = REAL["take"].apply(a)
            if HOOK0["on"]:
                HOOK0["on"] = False
                break_account()
            return r

    BR.put("coins:fn:take", TakeThenBreak())
    cl.press("#SkyyBDepAll")
    step("account unreadable after the purse was charged", d, cl, pg, (PURSE0, "bad"),
         "-Your bank account file cannot be read right now, nothing was moved. Try again; if it keeps happening tell an admin (server log).",
         t=TOTAL0 - BANK0)
    check(any("could not be read after the purse was charged - the coins went back to the purse" in l for l in logs()),
          "E. the refund is logged with a [SkyyBank] WARNING")
    # profile switch after the page was drawn (the real SkyyProfiles file + reload + publish, as a switch leaves them)
    def switch_to(d, n, epoch):
        f = os.path.join(d, "Skyy_SkyyProfiles", "players", SKYY + ".properties")
        txt = open(f, encoding="ascii").read()
        txt = re.sub(r"(?m)^active=\d+$", "active=%d" % n, txt)
        txt = re.sub(r"(?m)^epoch=\d+$", "epoch=%d" % epoch, txt)
        open(f, "w", encoding="ascii").write(txt)
        PS.reload(SK)
        PS.publish(SK)

    d, BS, pr, ref, st, pm, net, cl, pg = session("switch-after")
    switch_to(d, 4, 12)
    check(str(BR.get("profile:fn:key").apply(SK)) == SKYY + "-p4" and int(BR.get("profile:epoch:" + SKYY)) == 12,
          "E. the real SkyyProfiles now answers profile 4, epoch 12")
    cl.press("#SkyyBDepAll")
    step("profile switched after the page was drawn", d, cl, pg, (PURSE0, BANK0), TXT["profile"],
         others={"p4": (P4_PURSE, P4_BANK)})
    cl.press("#SkyyBDepAll")
    m = money(d)
    step("Deposit all on profile 4", d, cl, pg, (PURSE0, BANK0), "+Deposited %d coins. Bank: %d  |  Purse: 0" % (P4_PURSE, P4_BANK + P4_PURSE),
         others={"p4": (0, P4_BANK + P4_PURSE)})
    # a switch DURING the purse call (impossible in game - both run on the world thread - the 0.1.2 bracket is the backstop)
    HOOK = {"on": None}

    @JImplements("java.util.function.Function")
    class Hooked:
        def __init__(self, key):
            self.key = key

        @JOverride
        def apply(self, a):
            r = REAL[self.key].apply(a)
            if HOOK["on"] == self.key:
                HOOK["on"] = None
                HOOK["fn"]()
            return r

    def hooked(key, fn):
        for k2 in ("get", "add", "take"):
            BR.put("coins:fn:" + k2, Hooked(k2) if k2 == key else REAL[k2])
        HOOK["on"], HOOK["fn"] = key, fn

    d, BS, pr, ref, st, pm, net, cl, pg = session("switch-during-take")
    hooked("take", lambda: switch_to(d, 4, 12))
    cl.press("#SkyyBDepAll")
    step("profile switch during the purse take", d, cl, pg, (0, BANK0 + PURSE0),
         "=Your profile changed during this deposit: the %d coins went into the bank of the profile you started it on." % PURSE0,
         others={"p4": (P4_PURSE, P4_BANK)})
    check(any("profile switched during a deposit" in l for l in logs()), "E. the straddle is logged with a [SkyyBank] WARNING")
    d, BS, pr, ref, st, pm, net, cl, pg = session("switch-during-get")
    hooked("get", lambda: switch_to(d, 4, 12))
    cl.press("#SkyyBDepAll")
    step("profile switch during the purse read", d, cl, pg, (PURSE0, BANK0), "-Not enough coins in your purse (%d)." % P4_PURSE,
         others={"p4": (P4_PURSE, P4_BANK)})
    # two pages: the replaced one refuses coins and sends nothing
    d, BS, pr, ref, st, pm, net, cl, pg = session("twopages")
    ba = dict(cl.binds)
    pg_b = open_bank("new", pr, ref, st, pm, cl)
    n0 = len(sent(net))
    pg.handleDataEvent(ref, st, json.dumps({"a": "depall", "@BAmount": "", "t": json.loads(ba["#SkyyBDepAll"])["t"]}))
    check(len(sent(net)) == n0 and money(d)["p3"] == (PURSE0, BANK0) and info(pg) == TXT["closed"]
          and any("not sent: the page is already closed" in l for l in logs()),
          "E. two pages: the replaced page refuses the coin click (%r) and sends nothing" % info(pg))
    cl.press("#SkyyBDepAll", binds=ba)                     # the engine routes it to the open page: an older copy's token
    step("two pages: the old page's token on the new page", d, cl, pg_b, (PURSE0, BANK0), TXT["old"])
    cl.press("#SkyyBDepAll")
    step("two pages: the new page's own click", d, cl, pg_b, (0, BANK0 + PURSE0), prefix="+Deposited 14700")
    # errors are logged: a page whose player has no Player component right now (the rebuild fails) still answers in short
    d, BS, pr, ref, st, pm, net, cl, pg = session("answer-fails")
    comps = st.comps.get(ref)
    pl_saved = comps.get(CT_PLA)
    pm_saved = pm
    comps.remove(CT_PLA)
    n0 = len(sent(net))
    try:
        pg.handleDataEvent(ref, st, json.dumps({"a": "refresh", "@BAmount": ""}))
    except Exception as e:
        check(False, "E. a failing rebuild must not throw out of the handler: %s" % e)
    lw = [l for l in logs() if "failed, sending the short answer" in l]
    check(len(lw) == 1, "E. a failing rebuild is logged with a [SkyyBank] line: %s" % lw)
    comps.put(CT_PLA, pl_saved)
    print("E. %d steps: every button with Skyy's numbers (14,700 / 87,722) answered; double clicks moved once; no / failing SkyyCoins "
          "moved nothing; profile switches refused or bracketed; two pages safe; coins conserved after every step" % COUNT.get("E steps", 0))

    # ---------------- D. page builds 0.1.5 vs 0.1.6 (fake coins: the 0.1.5 harness's 10 states x 5 marks)
    PURSE = {}

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

    FCOINS = (CoinsGet(), CoinsAdd(), CoinsTake())
    FPROF = ProfKey()
    UID = UUID.fromString("00000000-0000-0000-0000-0000000000b1")
    US = str(UID)
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
    MARKS = [("", ""), ("+Deposited 2,000 coins. Bank: 7,000 coins.", ""), ("-Not enough coins in your purse (12,500).", "999999"),
             ("=Type an amount in the box first (500, 2k, 1.5m or all), then click Deposit.", "2k"), ("plain text", "1.5m"),
             (TXT["heal"], ""), (TXT["old"], "500")]

    def setup(k, stt):
        name, purse, bank, prof, pct, mins, mx, ago = stt
        Store, Cfg = jc(k, "BankStore"), jc(k, "BankConfig")
        dd = os.path.join(SCRATCH, "accounts", k, name)
        shutil.rmtree(dd, ignore_errors=True)
        os.makedirs(dd)
        Store.DIR = Paths.get(dd)
        Store.BAL.clear()
        Store.LOADED.clear()
        Store.EPOCH.clear()
        BR.clear()
        PURSE.clear()
        PKEY.clear()
        if purse != "none":
            BR.put("coins:fn:get", FCOINS[0])
            BR.put("coins:fn:add", FCOINS[1])
            BR.put("coins:fn:take", FCOINS[2])
            PURSE[US] = purse
        key = US
        if prof is not None:
            key = US + "-p2"
            PKEY[US] = key
            BR.put("profile:fn:key", FPROF)
            BR.put("profile:name:" + US, prof[0])
            BR.put("profile:class:" + US, prof[1])
            BR.put("profile:epoch:" + US, Long.valueOf(3))
        if bank == "bad":
            open(os.path.join(dd, key + ".properties"), "w").write("balance=not-a-number\n")
        elif bank is not None:
            open(os.path.join(dd, key + ".properties"), "w").write("#SkyyBank\nbalance=%d\n" % bank)
        Cfg.PERCENT = pct
        Cfg.MINUTES = mins
        Cfg.MAX_PRINCIPAL = mx
        Cfg.LAST = 0 if ago is None else int(System.currentTimeMillis()) - ago
        return Store, key

    def pref(u):
        p = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(p, u)
        return p

    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def build(pg_):
        b, ev = UCB(), UEB()
        pg_.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    DUR = re.compile(r"in \d+ h \d+ min|in \d+ min \d+ s|in \d+ s")

    def sets_of(cmds):
        return [(sel, DUR.sub("in <t>", data or "")) for typ, sel, text, data in cmds if "append" not in typ.lower()]

    def appends_of(cmds):
        return [(sel, text) for typ, sel, text, data in cmds if "append" in typ.lower()]

    COIN_SELS = {"#SkyyBDepAll", "#SkyyBWdAll", "#SkyyBDep", "#SkyyBWd"}
    FIRST = {}
    toks = set()
    for stt in STATES:
        for inf, keep in MARKS:
            res = {}
            for k in ("old", "new"):
                setup(k, stt)
                pg_ = jc(k, "BankPage")(pref(UID))
                pg_.info = inf
                pg_.keepAmount = keep
                res[k] = build(pg_)
                if k == "new":
                    again = build(pg_)
                    t1 = [json.loads(dd)["t"] for _t, s_, dd, _l in res[k][1] if s_ in COIN_SELS]
                    t2 = [json.loads(dd)["t"] for _t, s_, dd, _l in again[1] if s_ in COIN_SELS]
                    check(len(set(t1)) == 1 and len(set(t2)) == 1 and t1[0] != t2[0] and re.fullmatch(r"[0-9a-f]+", t1[0]),
                          "D. the four coin buttons carry one hex token per build, new on every build (%s / %s)" % (t1[:1], t2[:1]))
                    toks.add(t1[0])
            tag = "%s / %r / %r" % (stt[0], inf[:12], keep)
            (co_, eo), (cn_, en) = res["old"], res["new"]
            check(appends_of(co_) == appends_of(cn_), "D. %s: the appended markup differs from 0.1.5" % tag)
            check(sets_of(co_) == sets_of(cn_), "D. %s: b.set lines differ (in order)" % tag)
            strip = []
            for (ty, se, da, lk) in en:
                dj = json.loads(da) if da else None
                if dj is not None and se in COIN_SELS:
                    check("t" in dj, "D. %s: %s carries the token" % (tag, se))
                    dj.pop("t", None)
                elif dj is not None:
                    check("t" not in dj, "D. %s: %s carries no token" % (tag, se))
                strip.append((ty, se, dj, lk))
            check(strip == [(ty, se, json.loads(da) if da else None, lk) for ty, se, da, lk in eo] and len(en) == 7,
                  "D. %s: the 7 bindings are 0.1.5's apart from the token" % tag)
            aps = appends_of(cn_)
            runtime = []
            for sel, text in aps:
                try:
                    SUI.check_markup(text, prefix=K["BANK_PREFIX"], root=(sel is None))
                    tally("D markups")
                except ValueError as e:
                    check(False, "D. %s: check_markup: %s" % (tag, e))
                ids = re.findall(r"#([A-Za-z0-9_]+)\s*\{", text)
                check(all("_" not in i for i in ids), "D. %s: underscore in an id: %s" % (tag, ids))
                runtime.append((None if sel is None else sel[1:], text))
            try:
                SUI.check_page(runtime, prefix=K["BANK_PREFIX"])
                SUI.assert_proven([t_ for _p, t_ in runtime], what="bank page " + tag)
                tally("D pages")
            except ValueError as e:
                check(False, "D. %s: check_page / assert_proven: %s" % (tag, e))
            if not FIRST:
                FIRST["new"] = runtime
            tally("D builds", 2)
    check(len(toks) == len(STATES) * len(MARKS), "D. every page gets its own token base (%d distinct of %d)" % (len(toks), len(STATES) * len(MARKS)))
    print("D. %d page builds (%d states x %d marks x 2 jars): appends + b.set lines identical to 0.1.5, bindings 0.1.5's + the token on "
          "the 4 coin buttons; %d markups check_markup, %d pages check_page + assert_proven" % (
              COUNT.get("D builds", 0), len(STATES), len(MARKS), COUNT.get("D markups", 0), COUNT.get("D pages", 0)))

    # ---------------- F. text fit (#SkyyBInfo, two lines)
    F = fonts()
    if F is None:
        print("F. skipped: no client font tables in", FONT_DIR)
    else:
        EL = []
        for parent, r in FIRST["new"]:
            els = elements(r)
            for typ, ident, own, up in els:
                EL.append((parent if up is None else els[up][1], typ, ident, own))
        BY = dict((i, (p, t, o)) for p, t, i, o in EL if i)

        def box_w(ident):
            p, _t, own = BY[ident]
            a, pd = own_anchor(own), own_padding(own)
            w = a["Width"] if "Width" in a else box_w(p) - hsum(dict((k2, v) for k2, v in a.items() if k2 not in ("Width", "Height")))
            return w - hsum(pd)

        p_, _t, own = BY["SkyyBInfo"]
        size, h, room = own_font(own), own_anchor(own).get("Height"), box_w("SkyyBInfo")
        bold = "RenderBold: true" in own
        lh = F["regular"][1]
        texts = set(v[1:] if v[:1] in "+-=" else v for v in list(TXT.values()) + list(SEEN_INFO) if v)
        worst = 0
        for t_ in sorted(texts):
            nl = wrap_lines(F, t_, size, bold, room)
            worst = max(worst, nl)
            check(nl <= 2 and nl * size * lh <= h, "F. #SkyyBInfo: %r wraps to %d lines (%.1f px) in %d x %d px" % (t_, nl, nl * size * lh, room, h))
        COUNT["F texts"] = len(texts)
        print("F. text fit: %d result texts in #SkyyBInfo (%d px wide, %d px high, %d px %s) - at most %d lines" % (
            len(texts), room, h, size, "bold" if bold else "regular", worst))

    # ---------------- P. every 0.1.6 page packet through the engine's own codec
    MS = JClass("java.lang.foreign.MemorySegment")
    n_ok, biggest = 0, 0
    for p in PACKETS:
        try:
            size = int(p.computeSize())
            arr = JArray(JByte)(size)
            seg = MS.ofArray(arr)
            wrote = int(p.serialize(seg, 0))
            q = CPK.toObject(seg)
            ok = (wrote == size and str(q.key) == str(p.key) and bool(q.isInitial) == bool(p.isInitial) and bool(q.clear) == bool(p.clear)
                  and len(q.commands) == len(p.commands) and len(q.eventBindings or []) == len(p.eventBindings or [])
                  and size <= int(CPK.MAX_SIZE))
            biggest = max(biggest, size)
            if check(ok, "P. a page packet does not round-trip the engine codec (%d bytes)" % size):
                n_ok += 1
        except Exception as e:
            check(False, "P. codec: %s" % e)
    check(n_ok >= 20, "P. at least 20 page packets checked (%d)" % n_ok)
    print("P. %d page packets serialize + deserialize with the engine's CustomPage codec (largest %d bytes, max %d)" % (
        n_ok, biggest, int(CPK.MAX_SIZE)))

    # ---------------- S. start twice on a scratch copy of the live data
    LV = live_dir()
    src = "live"
    if not all(os.path.isdir(os.path.join(LV, m_)) for m_ in ("Skyy_SkyyBank", "Skyy_SkyyCoins", "Skyy_SkyyProfiles")):
        src = "synthetic"

    def snapshot(dd):
        out = {}
        for root_, _ds, fs in os.walk(dd):
            for f_ in fs:
                p_ = os.path.join(root_, f_)
                out[os.path.relpath(p_, dd)] = (open(p_, "rb").read(), os.path.getmtime(p_))
        return out

    starts = {}
    try:
        _cfg = open(os.path.join(LV, "Skyy_SkyyBank", "config.properties"), encoding="latin-1").read() if src == "live" else ""
        _last = int(re.search(r"(?m)^lastInterestMillis=(\d+)", _cfg).group(1)) if _cfg else 1791000675076
        _mins = int(re.search(r"(?m)^intervalMinutes=(\d+)", _cfg).group(1)) if _cfg else 60
    except Exception:
        _last, _mins = 1791000675076, 60
    due0 = max(0, (int(System.currentTimeMillis()) - _last) // (_mins * 60000))
    for k in ("old", "new"):
        dd = os.path.join(SCRATCH, "start", k)
        shutil.rmtree(dd, ignore_errors=True)
        if src == "live":
            for m_ in ("Skyy_SkyyBank", "Skyy_SkyyCoins", "Skyy_SkyyProfiles"):
                shutil.copytree(os.path.join(LV, m_), os.path.join(dd, m_))         # READ-only source: copied
        else:
            make_data(dd, 1791000675076)
        BS, BC, BT = jc(k, "BankStore"), jc(k, "BankConfig"), jc(k, "BankTick")
        BR.clear()
        bridge_real()
        CS.DIR = Paths.get(os.path.join(dd, "Skyy_SkyyCoins", "balances"))
        CS.BAL.clear()
        CS.LOADED.clear()
        PS.DIR = Paths.get(os.path.join(dd, "Skyy_SkyyProfiles", "players"))
        PS.DATA.clear()
        PS.publish(SK)
        res = []
        for n_start in (1, 2, 3, 4):
            BS.DIR = Paths.get(os.path.join(dd, "Skyy_SkyyBank", "accounts"))
            BS.BAL.clear()
            BS.LOADED.clear()
            BS.EPOCH.clear()
            BC.FILE = Paths.get(os.path.join(dd, "Skyy_SkyyBank", "config.properties"))
            before = snapshot(dd)
            time.sleep(0.05)
            BC.load()                                      # setup()
            BT.SWEEPING = False
            BT.interest()                                  # the worker's first due sweep (BankTick hands it over on its 30th run)
            after = snapshot(dd)
            vals = dict((rel, read_bal(os.path.join(dd, rel))) for rel in after if rel.endswith(".properties") and "accounts" in rel)
            res.append((before, after, vals, int(BC.LAST)))
            if after == before:
                break
        starts[k] = res
        quiet = [i + 1 for i, (b_, a_, _v, _l) in enumerate(res) if a_ == b_]
        check(quiet and quiet[0] == len(res) and len(res) <= 2 + int(due0 // 24),
              "S. %s: start %s writes nothing (every file byte-identical, same mtimes) - %d start(s) before it caught up %d due "
              "interest period(s)" % (k, quiet, len(res) - 1, due0))
    check(starts["old"][0][2] == starts["new"][0][2] and starts["old"][0][3] == starts["new"][0][3],
          "S. 0.1.5 and 0.1.6 make the same balances and interest time on the first start: %s / %s" % (starts["old"][0][2], starts["new"][0][2]))
    print("S. start on a copy of the %s data (%d interest period(s) due): first start %s (the catch-up, as 0.1.5), start %d writes "
          "nothing; 0.1.5 = 0.1.6" % (src, due0, dict((r_.split(os.sep)[-1][:44], v_) for r_, v_ in starts["new"][0][2].items()),
                                       len(starts["new"])))

    # ---------------- G. the page id
    pid, chk = K["BANK_PAGE_ID"], K["BANK_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready line names the page the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW))
    check(pid == chk, "G. the page the kit makes now (%s) is the checked page BANK_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/bank_0_1_6_patch.py, regenerate and rebuild" % (pid, chk, pid))
    COUNT["G"] = (pid, chk, SUI.kit_id())
    print("G. page id %s, checked %s, kit %s" % (pid, chk, SUI.kit_id()))

    # ---------------- X. engine-access audit (MethodHandles.Lookup in each referencing class)
    LIN = JClass("skyybankharness.LookupIn")
    MTc = JClass("java.lang.invoke.MethodType")
    CPool = JClass("javassist.bytecode.ConstPool")
    JMod_ = JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def audit(cn, ldr, pool):
        def jvm_class(name):
            return Cls.forName(name.replace("/", "."), False, ldr)
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = pool.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", ldr).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)),
                                                 str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, ldr)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    refused.append("%s: %s" % (where, ex_))
        return refused, n

    xp = CPc(False)
    xp.appendSystemPath()
    xp.appendClassPath(B.SERVER_JAR)
    xp.appendClassPath(JAR)
    xref, xn = [], 0
    for cn_ in sorted(CB["new"]):
        r_, n_ = audit(cn_, L["new"], xp)
        xref += r_
        xn += n_
    check(not xref and xn > 500, "X. all %d references in the %d classes of the 0.1.6 jar pass MethodHandles.Lookup in their own class "
          "(the JVM's access rules): refused %s" % (xn, len(CB["new"]), xref[:5]))
    xb = CPc(False)
    xb.appendSystemPath()
    xb.appendClassPath(B.SERVER_JAR)
    xb.appendClassPath(JAR)
    xb.appendClassPath(hcls2)
    u2 = JArray(URL)(1)
    u2[0] = File(hcls2).toURI().toURL()
    BADL = URLCL(u2, L["new"])
    br_, bn_ = audit("skyybankharness.BadCaller", BADL, xb)
    check(len(br_) == 1 and "rebuild" in br_[0], "X. control: a class calling BankPage.rebuild from outside is refused by the audit: %s" % br_)
    try:
        jpbad = JClass("skyybankharness.BadCaller", loader=BADL)
        jpbad.poke(jc("new", "BankPage")(pref(UID)))
        err = ""
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, e)
    check("IllegalAccessError" in err and "rebuild" in err, "X. control: running that call throws the game's IllegalAccessError (%s)" % err[:200])
    print("X. access audit: %d references, %d refused (control refused %d)" % (xn, len(xref), len(br_)))


def main():
    for j in (JAR, OLD, COINS, PROFS):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    claim_scratch()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyBank %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        os.chdir(ROOT)
        shutil.rmtree(SCRATCH, ignore_errors=True)
        if os.path.exists(SCRATCH):
            left = sum(len(fs) for _r, _d, fs in os.walk(SCRATCH))
            print("note: %d file(s) the running JVM still holds stay in %s (the engine's zstd native library, extracted into the "
                  "scratch tmp by part P) - delete that folder once this process has ended" % (left, SCRATCH))
    sys.stdout.flush()
    os._exit(code)
