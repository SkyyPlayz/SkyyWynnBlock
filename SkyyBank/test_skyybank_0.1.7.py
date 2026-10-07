"""Bare-JVM harness for SkyyBank 0.1.7 - bank interest once per real day, in brackets over all of a player's profiles (Skyy
2026-10-06, docs/answered/economy.md LOCKED; research/cloud/Bank-Tab-Calibration.md option E + the section 1.5 one-time update).
Keep it next to the build so the build docstring's CHECKED claims can be re-run instead of trusted.

    python SkyyBank/test_skyybank_0.1.7.py [--jar <SkyyBank-0.1.7.jar>] [--old <SkyyBank-0.1.6.jar>] [--profiles <SkyyProfiles jar>]
                                           [--dir <scratch folder>] [--keep]

Build first (python tools/bank_0_1_7_patch.py, then python SkyyBank/build_skyybank_0.1.7.py). ONE JVM (-Xverify:all,
-XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; SkyyBank 0.1.6 - the live SET pin -, SkyyBank 0.1.7 and
the REAL SkyyProfiles 0.1.5 each in its own class loader). Every money path runs for real (BankTick.sweep, BankStore.payGroup /
split / nextGain, BankMig.run, BankConfig.load, the config kit) on scratch folders; the clock is moved by setting the stored
clock back, never by touching the computer's clock.
  A  every class of the three jars loads, verifies and initialises
  B  class compare 0.1.6 -> 0.1.7, method by method (instructions with their constants; constant-pool numbers and branch offsets
     read as instruction numbers): the money path (deposit / withdraw / creditK / debitK / the purse calls / move / run), the page
     check (BankWatch, watchTick, handleDataEvent, coinClick, answer), BankJob and the five command classes are unchanged; every
     changed / added / removed method is listed and must be one the patch meant to change
  M  the payout: (1) bracket edges, one profile, one day: 0, 49, 50, 999,999 ... 10,000,001, 50,000,000 against a Python reference
     (2) several profiles, account-wide: Skyy's live four banks (2,298,875 -> 32,988 split exactly), plus a second player; paid once
     (a second sweep changes no byte); scope=profile pays each alone; nextGain() = what the payout then pays (3) back-pay: 3.5 days
     -> 3 whole days compounding, the half day waits; 30 days -> the 24-day cap (the clock moves to the last whole day); cap 5
     (4) the clock: ahead by more than a payout (turned back) -> no pay, restart at now, one WARNING; ahead by less -> nothing; a
     restart mid-day (caches dropped, config + clock re-read) -> nothing (5) a crash between paying the files and saving the clock:
     the clock and one file put back -> the rerun pays only that file, exactly what an uncrashed run gives; clock only -> nothing
     (6) deleted profiles: pending + archived (a stand-in profile:fn:state and the REAL SkyyProfiles 0.1.5 StateFn on a players
     file) are left out (bytes untouched, not in the sum); restored -> paid from the next payout, no back-pay (7) rounding: 3000
     random splits (sum exact, each share floor / floor+1 of the exact share, the leftover to the largest remainders) and 120 random
     group sweeps against the reference (8) an unreadable account in a group: left out, untouched (9) every rate 0: nothing paid,
     the clock still moves
  U  THE UPDATE on scratch COPIES of the live Skyy_SkyyBank folder (read-only source): run twice - the second run changes no byte
     anywhere; the history copy = the old bytes; one change-log line (intervalSeconds 3600 -> 86400 ok); state.properties = the
     old lastInterestMillis; only the two planned lines differ (CRLF kept); hand-edited values (intervalMinutes=30, interestPercent=5,
     maxPrincipal=20000000) kept; an LF file stays LF; no config / nothing at all; a blocked config-history = nothing rewritten, no
     marker, the next start finishes it; then the loader, the first daily payout on the live balances (0.1.6 on the same copy paid
     ~1.6x the hourly-24 catch-up), and the config kit: Server Setup header published, get / set (Undo = intervalSeconds 3600 written
     in place), the check= hook refusing a bracket top out of order
  P  page builds 0.1.6 vs 0.1.7 (the engine's UICommandBuilder / UIEventBuilder): the same appends (markup) and bindings (click
     token aside); only #SkyyBRate / #SkyyBNext / #SkyyBGain differ; the payout line shows nextGain(); the texts fit (client font)
  G  the page id: the kit's page NOW == BANK_PAGE_CHECKED in the generated script == the id in the jar's ready line
Not here: the whole SET in one JVM and the engine-access / command audit (python tools/ci/crosscheck.py --jar ... --baseline).
Nothing is deployed; live data is only READ (copied). --dir must be inside tools/dev/scratch and new, empty or this harness's
own (marker file); it is deleted at the end unless --keep. Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, zipfile, random, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.7", "0.1.6"
PKG = "com.skyy.bank."
SCRIPT = os.path.join(HERE, "build_skyybank_%s.py" % VERSION)
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"
OTHER = "b942734e-90b8-4e4b-986c-cd725d975b9e"
MARK = ".skyybank-0.1.7-harness"
DAY = 86400000


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "test-bank-0.1.7"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyBank-%s.jar" % OLD_VERSION)))
PROFS = os.path.abspath(arg("--profiles", os.path.join(ROOT, "SkyyProfiles", "SkyyProfiles-0.1.5.jar")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def claim_scratch():
    if os.path.commonpath([SCRATCH, SCRATCH_ROOT]) != SCRATCH_ROOT or SCRATCH == SCRATCH_ROOT:
        raise SystemExit("--dir must be a folder inside %s (got %s)" % (SCRATCH_ROOT, SCRATCH))
    if os.path.isdir(SCRATCH) and os.listdir(SCRATCH) and not os.path.isfile(os.path.join(SCRATCH, MARK)):
        raise SystemExit("refusing %s: not empty and not made by this harness (no %s)" % (SCRATCH, MARK))
    os.makedirs(SCRATCH, exist_ok=True)
    open(os.path.join(SCRATCH, MARK), "w").write("SkyyBank 0.1.7 harness scratch - safe to delete\n")


# ------------------------------------------------------------------------------------------------ the Python reference (no JVM)
def ppm(p):
    if not p > 0:
        return 0
    if p >= 100:
        return 1000000
    x = p * 10000.0
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)       # Math.round for these positive values


CFG0 = dict(p1=2.0, e1=1000000, p2=1.0, e2=5000000, p3=0.5, m=10000000)


def ref_interest(s, c=CFG0):
    if s <= 0:
        return 0
    m = min(max(c["m"], 0), 10 ** 12)
    e1 = min(max(c["e1"], 0), m)
    e2 = min(max(c["e2"], e1), m)
    p1 = min(s, e1)
    p2 = 0 if s <= e1 else min(s, e2) - e1
    p3 = 0 if s <= e2 else min(s, m) - e2
    return (p1 * ppm(c["p1"]) + p2 * ppm(c["p2"]) + p3 * ppm(c["p3"])) // 1000000


def ref_split(g, bs):
    n, s = len(bs), sum(b for b in bs if b > 0)
    sh = [0] * n
    if g <= 0 or s <= 0:
        return sh
    rem = [-1] * n
    for i, b in enumerate(bs):
        if b > 0:
            sh[i], rem[i] = divmod(g * b, s)
    left = g - sum(sh)
    while left > 0:
        best = -1
        for i in range(n):
            if rem[i] >= 0 and (best < 0 or rem[i] > rem[best]):
                best = i
        if best < 0:
            break
        sh[best] += 1
        rem[best] = -1
        left -= 1
    return sh


def ref_group(bals, days, c=CFG0, account=True):
    """{index: gain} of `days` compounding payouts on the group balances bals (account-wide or each alone)"""
    sim = list(bals)
    gain = [0] * len(bals)
    for _ in range(days):
        if account:
            sh = ref_split(ref_interest(sum(sim), c), sim)
        else:
            sh = [ref_interest(b, c) for b in sim]
        for i in range(len(sim)):
            sim[i] += sh[i]
            gain[i] += sh[i]
    return gain


# ------------------------------------------------------------------------------------------------ files (no JVM)
def write_acc(home, key, bal, extra=""):
    d = os.path.join(home, "accounts")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, key + ".properties"), "w", encoding="ascii", newline="").write("#SkyyBank\r\nbalance=%s\r\n%s" % (bal, extra))


def read_props(path):
    out = {}
    if not os.path.exists(path):
        return None
    for ln in open(path, encoding="latin-1"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def acc(home, key):
    p = read_props(os.path.join(home, "accounts", key + ".properties"))
    return None if p is None else int(p["balance"])


def snapshot(d):
    out = {}
    for base, _dirs, files in os.walk(d):
        for f in files:
            p = os.path.join(base, f)
            out[os.path.relpath(p, d)] = open(p, "rb").read()
    return out


def live_bank():
    import skyybuild as B
    return os.path.join(B.USERDATA, "Saves", "HUD mod", "mods")


# ------------------------------------------------------------------------------------------------ the kit's page, NOW (no JVM)
def kit_page():
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
    ns = {"SUI": SUI, "re": re, "hashlib": hashlib, "json": json}
    exec(compile(ast.Module(body=body, type_ignores=[]), SCRIPT, "exec"), ns)
    return SUI, ns


def classes(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n[:-6].replace("/", "."), z.read(n)) for n in z.namelist() if n.endswith(".class"))
    z.close()
    return out


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
    os.chdir(SCRATCH)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    JARS = {"old": OLD, "new": JAR, "prof": PROFS}
    L = dict((k, loader(v)) for k, v in JARS.items())
    CB = dict((k, classes(v)) for k, v in JARS.items())

    # ---------------- A. load + verify + init
    na = {}
    for k in ("old", "new", "prof"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                na[k] = na.get(k, 0) + 1
                OKS[0] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised (-Xverify:all): SkyyBank %s %d, SkyyBank %s %d, SkyyProfiles %d classes" % (
        OLD_VERSION, na.get("old", 0), VERSION, na.get("new", 0), na.get("prof", 0)))
    if FAILS:
        return

    # ---------------- B. class compare
    CPc = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    BRANCH = set(range(153, 169)) | {198, 199, 200, 168, 201}

    def methods(raw_bytes):
        cp = CPc(False)
        cc = cp.makeClass(BAIS(raw_bytes))
        out = {}
        for m in cc.getDeclaredBehaviors():
            mi = m.getMethodInfo()
            key = "%s%s" % (mi.getName(), mi.getDescriptor())
            ca = mi.getCodeAttribute()
            if ca is None:
                out[key] = []
                continue
            it = ca.iterator()
            pos = []
            while it.hasNext():
                pos.append(int(it.next()))
            idx = dict((p, i) for i, p in enumerate(pos))
            ins = []
            it2 = ca.iterator()
            cpool = mi.getConstPool()
            for p in pos:
                txt = str(IP.instructionString(it2, p, cpool))
                op = ca.getCode()[p] & 0xff
                txt = re.sub(r"#\d+ = ", "", txt).replace("ldc_w", "ldc").replace("goto_w", "goto")
                if op in BRANCH:
                    txt = re.sub(r"(-?\d+)$", lambda mm: "@%s" % idx.get(int(mm.group(1)), "?"), txt)
                ins.append(txt)
            out[key] = ins
        return out

    same_cls, diff = [], {}
    for n in sorted(set(CB["old"]) | set(CB["new"])):
        if n in CB["old"] and n in CB["new"] and CB["old"][n] == CB["new"][n]:
            same_cls.append(n)
            continue
        if n not in CB["old"]:
            diff[n] = "new class"
            continue
        if n not in CB["new"]:
            diff[n] = "removed class"
            continue
        mo, mn = methods(CB["old"][n]), methods(CB["new"][n])
        ch = sorted(k for k in mo if k in mn and mo[k] != mn[k])
        ad = sorted(k for k in mn if k not in mo)
        rm = sorted(k for k in mo if k not in mn)
        diff[n] = (ch, ad, rm)
    short = lambda n: n.replace(PKG, "")
    print("B. byte-identical classes: %s" % ", ".join(short(n) for n in same_cls))
    for n, d in sorted(diff.items()):
        if isinstance(d, str):
            print("B. %s: %s" % (short(n), d))
        else:
            print("B. %s: changed %s; added %s; removed %s" % (short(n), [k.split("(")[0] for k in d[0]], [k.split("(")[0] for k in d[1]],
                                                              [k.split("(")[0] for k in d[2]]))
    for c in ("BankWatch", "BankJob", "BankCmd", "BankActionCmd", "BankAmountCmd", "BankConfigSetCmd", "BankConfigSetMaxCmd"):
        if c == "BankCmd":
            d = diff.get(PKG + c)
            check(d is not None and not isinstance(d, str) and [k.split("(")[0] for k in d[0]] == ["status"] and not d[1] and not d[2],
                  "B. BankCmd: only status changed (%s)" % (d,))
        else:
            check(PKG + c in same_cls, "B. %s byte-identical to 0.1.6" % c)
    EXPECT = {
        "BankStore": ({"<clinit>", "loadKey", "setKey"}, {"pstate", "earns", "payKey", "split", "payGroup", "payAll", "groupOf", "nextGain"}, {"payInterest"}),
        "BankTick": ({"sweep", "due", "epochs"}, {"payText"}, set()),
        "BankConfigCmd": ({"apply"}, set(), set()),
        "BankPage": ({"rateText", "nextText", "gainText", "payoutOn", "build"}, set(), set()),
        "SkyyBankPlugin": ({"setup", "shutdown"}, set(), set()),
        "BankConfig": ({"<clinit>", "load"}, {"top", "edge1", "edge2", "ppm", "interval", "catchUp", "account", "interestOf", "on",
                                              "pctText", "num", "coinsShort", "cadence", "durText", "bracketText", "describe", "check",
                                              "saveState", "readState", "decOf", "longOf"}, {"save"}),
    }
    for c, (ch_, ad_, rm_) in EXPECT.items():
        d = diff.get(PKG + c)
        if not check(d is not None and not isinstance(d, str), "B. %s changed as planned" % c):
            continue
        ch = set(k.split("(")[0] for k in d[0])
        ad = set(k.split("(")[0] for k in d[1])
        rm = set(k.split("(")[0] for k in d[2])
        if c == "BankPage":     # the three text methods and payoutOn changed their signature: added + removed under the same name
            check(ch == {"build"} and ad == {"rateText", "nextText", "gainText", "payoutOn"} and rm == ad | {"every"},
                  "B. BankPage: build changed, the 4 interest text helpers re-signed, the dead every() removed, nothing else (%s / %s / %s)" % (ch, ad, rm))
        else:
            check(ch == ch_ and ad == ad_ and rm == rm_, "B. %s: changed %s added %s removed %s" % (c, ch, ad, rm))
    bp = diff.get(PKG + "BankPage")
    if bp and not isinstance(bp, str):
        mo, mn = methods(CB["old"][PKG + "BankPage"]), methods(CB["new"][PKG + "BankPage"])
        for k in ("handleDataEvent", "coinClick", "watchTick", "answer", "typed", "jsonStr", "fmt", "dur", "subText"):
            ko = [x for x in mo if x.startswith(k + "(")]
            check(ko and all(mo[x] == mn.get(x) for x in ko), "B. BankPage.%s instruction-identical" % k)
    bs = diff.get(PKG + "BankStore")
    if bs and not isinstance(bs, str):
        mo, mn = methods(CB["old"][PKG + "BankStore"]), methods(CB["new"][PKG + "BankStore"])
        for k in ("deposit", "withdraw", "creditK", "debitK", "purseTake", "purseAdd", "purseOr", "pkey", "owner", "keyOf",
                  "allAccounts", "getKey", "ready", "replaceFile", "sameProfile", "publish", "publishIfActive", "get", "set"):
            ko = [x for x in mo if x.startswith(k + "(")]
            check(ko and all(mo[x] == mn.get(x) for x in ko), "B. BankStore.%s instruction-identical (the money path)" % k)
    nb = [n for n in diff if isinstance(diff[n], str) and diff[n] == "new class"]
    check(sorted(short(n) for n in nb) == sorted(["BankMig", "BankNotice", "CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile",
                                                  "CfgFn", "CfgPub"]), "B. new classes: BankMig, BankNotice + the 7 kit classes (%s)" % nb)
    check(not [n for n in diff if diff[n] == "removed class"], "B. no class removed")

    # ---------------- shared JVM state
    System = JClass("java.lang.System")
    Paths = JClass("java.nio.file.Paths")
    UUID = JClass("java.util.UUID")
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
        return [x for x in out if "[SkyyBank]" in x or "config " in x]

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    BS, BC, BT, BM = jc("new", "BankStore"), jc("new", "BankConfig"), jc("new", "BankTick"), jc("new", "BankMig")
    BS.LOG = HL.get("SkyyBankHarness")
    jc("old", "BankStore").LOG = HL.get("SkyyBankHarnessOld")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    STATES = {}
    ACTIVE = {}
    BR_KEY = Fn(lambda u: ACTIVE.get(str(u), str(u)))
    BR_STATE = Fn(lambda k: STATES.get(str(k)))

    def bridge(state=True):
        BR.clear()
        BR.put("profile:fn:key", BR_KEY)
        if state:
            BR.put("profile:fn:state", BR_STATE)

    def fresh(tag, cfg=None, scope="account", catch=24, interval=DAY):
        """a scratch bank home; BankStore / BankConfig pointed at it, caches dropped, the settings set"""
        home = os.path.join(SCRATCH, "m", tag)
        if os.path.isdir(home):
            shutil.rmtree(home)
        os.makedirs(os.path.join(home, "accounts"))
        restart(home)
        c = dict(CFG0)
        c.update(cfg or {})
        BC.PCT1, BC.EDGE1, BC.PCT2, BC.EDGE2, BC.PCT3, BC.MAX_PRINCIPAL = c["p1"], c["e1"], c["p2"], c["e2"], c["p3"], c["m"]
        BC.INTERVAL_MS = interval
        BC.CATCH_UP = catch
        BC.SCOPE = scope
        STATES.clear()
        ACTIVE.clear()
        bridge()
        RECS.clear()
        return home

    def restart(home):
        BS.DIR = Paths.get(os.path.join(home, "accounts"))
        BC.FILE = Paths.get(os.path.join(home, "config.properties"))
        BC.STATE = Paths.get(os.path.join(home, "state.properties"))
        for mp in (BS.BAL, BS.LOADED, BS.PAID, BS.GAIN, BS.EPOCH):
            mp.clear()

    def now():
        return int(System.currentTimeMillis())

    def due_in(days, extra=5000, interval=DAY):
        """set the clock so that `days` whole payouts (+ extra ms) are due"""
        BC.LAST = now() - days * interval - extra
        return int(BC.LAST)

    def sweep():
        BT.sweep()

    def next_day(home):
        """one day passes: the clock and every account's paidThrough move one day back (as if the computer's clock moved on)"""
        BC.LAST = int(BC.LAST) - DAY
        d = os.path.join(home, "accounts")
        for f in os.listdir(d):
            p = os.path.join(d, f)
            b = open(p, "rb").read()
            b2 = re.sub(rb"paidThrough=(\d+)", lambda mm: b"paidThrough=%d" % (int(mm.group(1)) - DAY), b)
            if b2 != b:
                open(p, "wb").write(b2)
        restart(home)

    def state_last(home):
        p = read_props(os.path.join(home, "state.properties"))
        return None if p is None else int(p["lastInterestMillis"])

    # ---------------- M1. bracket edges, one profile, one payout
    edges = [0, 1, 49, 50, 51, 999999, 1000000, 1000001, 1000099, 4800000, 4999999, 5000000, 5000001, 9999999, 10000000, 10000001,
             50000000, 999999999999]
    for b in edges:
        home = fresh("edge")
        write_acc(home, SKYY, b)
        last = due_in(1)
        sweep()
        want = b + ref_interest(b)
        check(acc(home, SKYY) == want, "M1. bank %d: one payout -> %d (got %s)" % (b, want, acc(home, SKYY)))
        p = read_props(os.path.join(home, "accounts", SKYY + ".properties"))
        if ref_interest(b) > 0:
            check(p.get("paidThrough") == str(last + DAY), "M1. bank %d: paidThrough = the payout (%s)" % (b, p.get("paidThrough")))
        check(state_last(home) == last + DAY and int(BC.LAST) == last + DAY, "M1. bank %d: the clock moved one day" % b)
        before = snapshot(home)
        sweep()
        check(snapshot(home) == before, "M1. bank %d: a second sweep the same day changes no byte" % b)
    for b, w in ((10000000, 85000), (4800000, 58000), (1000000, 20000), (5000000, 60000), (49, 0), (50, 1), (20000000, 85000)):
        check(ref_interest(b) == w, "M1. reference: %d -> %d a day (%d)" % (b, w, ref_interest(b)))
    print("M1. bracket edges: %d balances, one payout each, paid once" % len(edges))

    # ---------------- M2. several profiles, account-wide (Skyy's live banks) + a second player
    LIVE4 = {SKYY: 1375171, SKYY + "-p3": 608522, SKYY + "-p4": 138140, SKYY + "-p5": 177042}
    keys = sorted(LIVE4)
    home = fresh("acct")
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    write_acc(home, OTHER, 3000000)
    ACTIVE[SKYY] = SKYY + "-p3"
    ng = int(BS.nextGain(UUID.fromString(SKYY)))
    due_in(1)
    sweep()
    g = ref_group([LIVE4[k] for k in keys], 1)
    got = [acc(home, k) - LIVE4[k] for k in keys]
    check(got == g, "M2. Skyy's four banks: shares %s = reference %s" % (got, g))
    check(sum(got) == ref_interest(sum(LIVE4.values())) == 32988, "M2. the shares add up to exactly the account's interest: %d (32,988)" % sum(got))
    check(ng == got[keys.index(SKYY + "-p3")], "M2. nextGain() for the active profile (p3) = what the payout paid: %d / %d" % (
        ng, got[keys.index(SKYY + "-p3")]))
    check(acc(home, OTHER) == 3000000 + ref_interest(3000000), "M2. the other player is a group of his own: +%d" % ref_interest(3000000))
    before = snapshot(home)
    sweep()
    check(snapshot(home) == before, "M2. paid once: a second sweep changes no byte")
    # 0.1.6 on the same four banks, one day after its last payout (24 hourly periods at 2% each, per file)
    o = 0
    for v in LIVE4.values():
        b = v
        for _ in range(24):
            b += min(b, 10000000) * 2 // 100
        o += b - v
    print("M2. Skyy's live banks (2,298,875 over four profiles): 0.1.7 pays %d a day (%s); 0.1.6 paid %d for the same day" % (sum(got), got, o))
    home = fresh("acctp", scope="profile")
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    due_in(1)
    sweep()
    got = [acc(home, k) - LIVE4[k] for k in keys]
    check(got == [ref_interest(LIVE4[k]) for k in keys], "M2. scope=profile: each bank alone %s" % got)
    print("M2. scope=profile pays %d on the same banks" % sum(got))
    # four alts at 10M: account-wide = one 10M bank
    home = fresh("alts")
    for i in (1, 2, 3, 4):
        write_acc(home, SKYY + ("" if i == 1 else "-p%d" % i), 10000000)
    due_in(1)
    sweep()
    tot = sum(acc(home, SKYY + ("" if i == 1 else "-p%d" % i)) - 10000000 for i in (1, 2, 3, 4))
    check(tot == 85000, "M2. four alts at 10,000,000 earn 85,000 together (got %d; 0.1.6: 4 x 4.8M a day)" % tot)

    # ---------------- M3. back-pay
    home = fresh("back")
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    last = now() - int(3.5 * DAY)
    BC.LAST = last
    sweep()
    g = ref_group([LIVE4[k] for k in keys], 3)
    check([acc(home, k) - LIVE4[k] for k in keys] == g, "M3. 3.5 days off: 3 whole days compounding %s" % g)
    check(int(BC.LAST) == last + 3 * DAY and state_last(home) == last + 3 * DAY, "M3. the half day waits (clock at the 3rd day)")
    before = snapshot(home)
    sweep()
    check(snapshot(home) == before, "M3. nothing more until the 4th day")
    home = fresh("cap")
    write_acc(home, SKYY, 500000)
    last = now() - 30 * DAY - 1000
    BC.LAST = last
    sweep()
    check(acc(home, SKYY) == 500000 + ref_group([500000], 24)[0], "M3. 30 days off: the 24-day cap (+%d)" % ref_group([500000], 24)[0])
    check(int(BC.LAST) == last + 30 * DAY, "M3. the clock moves to the 30th day (the 6 older days are dropped, not paid later)")
    before = snapshot(home)
    sweep()
    check(snapshot(home) == before, "M3. a true cap: nothing paid 30 s later (0.1.6 paid the rest)")
    home = fresh("cap5", catch=5)
    write_acc(home, SKYY, 500000)
    due_in(9)
    sweep()
    check(acc(home, SKYY) == 500000 + ref_group([500000], 5)[0], "M3. catchUpPeriods=5: 9 days off pay 5")
    home = fresh("hourly", interval=3600000)
    write_acc(home, SKYY, 500000)
    due_in(2, interval=3600000)
    sweep()
    check(acc(home, SKYY) == 500000 + ref_group([500000], 2)[0], "M3. intervalSeconds=3600 (the Undo): two hourly payouts, brackets")

    # ---------------- M4. the clock
    home = fresh("ahead")
    write_acc(home, SKYY, 500000)
    BC.LAST = now() + 2 * DAY
    sweep()
    check(acc(home, SKYY) == 500000 and abs(int(BC.LAST) - now()) < 60000 and abs(state_last(home) - now()) < 60000,
          "M4. clock 2 days ahead (turned back): nothing paid, the clock restarts at now")
    check(any("ahead of this computer's clock" in x for x in logs()), "M4. one WARNING says so")
    t = now() + DAY // 2
    BC.LAST = t
    sweep()
    check(acc(home, SKYY) == 500000 and int(BC.LAST) == t, "M4. clock half a day ahead: nothing, the clock kept")
    check(not BT.due(), "M4. due() false while less than a payout is on the clock")
    BC.LAST = now() + 3 * DAY
    check(bool(BT.due()), "M4. due() true for a clock more than a payout ahead (so the worker restarts it)")
    # restart mid-day: a real config file + clock, caches dropped, BankConfig.load
    home = fresh("restart")
    open(os.path.join(home, "config.properties"), "w", newline="").write(K_DEFAULT.replace("\n", "\r\n"))
    write_acc(home, SKYY, 777777)
    last = due_in(1)
    sweep()
    paid1 = acc(home, SKYY)
    restart(home)
    BC.LAST = 0
    BC.load()
    check(int(BC.LAST) == last + DAY, "M4. restart mid-day: the clock is read back from state.properties")
    before = snapshot(home)
    sweep()
    check(snapshot(home) == before and paid1 == 777777 + ref_interest(777777), "M4. restart mid-day: nothing paid again")

    # ---------------- M5. a crash between paying the files and saving the clock
    def crash_case(tag, restore_file):
        home = fresh(tag)
        for k, v in LIVE4.items():
            write_acc(home, k, v)
        last = due_in(2)
        open(os.path.join(home, "state.properties"), "w").write("lastInterestMillis=%d\n" % last)
        pre = snapshot(home)
        sweep()
        good = dict((k, acc(home, k)) for k in keys)
        # the crash: the clock was never saved (and maybe one file never written)
        open(os.path.join(home, "state.properties"), "wb").write(pre["state.properties"])
        if restore_file:
            rel = os.path.join("accounts", restore_file + ".properties")
            open(os.path.join(home, rel), "wb").write(pre[rel])
        restart(home)
        BC.LAST = 0
        BC.load()
        check(int(BC.LAST) == last, "M5. %s: after the crash the clock is the old one" % tag)
        sweep()
        return home, good

    home, good = crash_case("crash1", SKYY + "-p4")
    check(dict((k, acc(home, k)) for k in keys) == good, "M5. a file not written before the crash: the rerun pays only it, exactly the "
          "uncrashed result %s" % [good[k] - LIVE4[k] for k in keys])
    home, good = crash_case("crash0", None)
    check(dict((k, acc(home, k)) for k in keys) == good, "M5. every file written, only the clock lost: the rerun pays nothing twice")

    # ---------------- M6. deleted profiles
    home = fresh("deleted")
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    STATES[SKYY + "-p4"] = "pending"
    STATES[SKYY + "-p5"] = "archived"
    STATES[SKYY] = "active"
    STATES[SKYY + "-p3"] = "inactive"
    pre = snapshot(home)
    due_in(1)
    sweep()
    live2 = [SKYY, SKYY + "-p3"]
    g = ref_group([LIVE4[k] for k in live2], 1)
    check([acc(home, k) - LIVE4[k] for k in live2] == g, "M6. pending + archived left out of the sum: %s" % g)
    for k in (SKYY + "-p4", SKYY + "-p5"):
        rel = os.path.join("accounts", k + ".properties")
        check(open(os.path.join(home, rel), "rb").read() == pre[rel], "M6. %s (deleted) untouched" % k)
    check(any("deleted profile(s) left out" in x for x in logs()), "M6. the sweep line counts them")
    STATES[SKYY + "-p4"] = "inactive"           # restored
    b4 = dict((k, acc(home, k)) for k in keys)
    next_day(home)
    sweep()
    g = ref_group([b4[k] for k in sorted([SKYY, SKYY + "-p3", SKYY + "-p4"])], 1)
    got = [acc(home, k) - b4[k] for k in sorted([SKYY, SKYY + "-p3", SKYY + "-p4"])]
    check(got == g, "M6. restored p4 earns from the next payout, no back-pay for its deleted day: %s" % got)
    check(acc(home, SKYY + "-p5") == LIVE4[SKYY + "-p5"], "M6. archived p5 still untouched")
    # without SkyyProfiles (no state function): every file earns
    home = fresh("nostate")
    bridge(state=False)
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    due_in(1)
    sweep()
    check([acc(home, k) - LIVE4[k] for k in keys] == ref_group([LIVE4[k] for k in keys], 1), "M6. no profile:fn:state: all four earn")
    # the REAL SkyyProfiles 0.1.5 state function on a players file: p.4 deleted (pending), gone.5 (archived)
    PS, SF = JClass("com.skyy.profiles.ProfStore", loader=L["prof"]), JClass("com.skyy.profiles.StateFn", loader=L["prof"])
    JClass("com.skyy.profiles.ProfCfg", loader=L["prof"]).LOG = HL.get("SkyyProfilesHarness")
    pdir = os.path.join(SCRATCH, "m", "players")
    os.makedirs(pdir, exist_ok=True)
    open(os.path.join(pdir, SKYY + ".properties"), "w").write(
        "active=1\nepoch=14\np.1.class=Archer\np.1.name=Strawberry\np.3.class=Priest\np.3.name=Banana\n"
        "p.4.class=Warrior\np.4.name=Watermelon\np.4.deleted=1791000000000\np.4.until=%d\np.4.slots=4\ngone.5=1791115590284\n"
        "gone.5.dir=5-1791115590284\nusername=SkyLordPlayz\n" % (now() + DAY))
    PS.DIR = Paths.get(pdir)
    PS.DATA.clear()
    home = fresh("realstate")
    BR.put("profile:fn:state", SF())
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    st = dict((k, SF().apply(k)) for k in keys)
    check(st == {SKYY: "active", SKYY + "-p3": "inactive", SKYY + "-p4": "pending", SKYY + "-p5": "archived"},
          "M6. the real StateFn: %s" % st)
    due_in(1)
    sweep()
    g = ref_group([LIVE4[k] for k in live2], 1)
    check([acc(home, k) - LIVE4[k] for k in live2] == g and acc(home, SKYY + "-p4") == LIVE4[SKYY + "-p4"]
          and acc(home, SKYY + "-p5") == LIVE4[SKYY + "-p5"], "M6. with the real SkyyProfiles state: only p1 + p3 earn %s" % g)

    # ---------------- M7. rounding
    rnd = random.Random(20261006)
    JL = JArray(JClass("long"))
    JB = JArray(JClass("boolean"))
    nsplit = 0
    for _ in range(3000):
        n = rnd.randint(1, 7)
        bs = [rnd.choice([0, rnd.randint(1, 100), rnd.randint(1, 10 ** 6), rnd.randint(1, 10 ** 9), rnd.randint(1, 3 * 10 ** 12)])
              for _ in range(n)]
        s = sum(bs)
        if s >= 2 ** 63:
            continue
        g = rnd.choice([ref_interest(s), rnd.randint(0, 10 ** 6), rnd.randint(0, 10 ** 12)])
        sh = list(BS.split(g, JL(bs), JB([True] * n), s))
        want = ref_split(g, bs)
        ok = [int(x) for x in sh] == want and (s == 0 or sum(want) == g)
        for i, b in enumerate(bs):
            if s > 0 and b > 0:
                ex = g * b // s
                ok = ok and ex <= want[i] <= ex + 1
        check(ok, "M7. split %d over %s" % (g, bs))
        nsplit += 1
    ng = 0
    for case in range(120):
        home = fresh("fuzz")
        n = rnd.randint(1, 5)
        ks = [SKYY] + [SKYY + "-p%d" % i for i in range(2, 2 + n - 1)]
        vals = dict((k, rnd.choice([rnd.randint(0, 3000), rnd.randint(0, 2 * 10 ** 6), rnd.randint(0, 2 * 10 ** 7)])) for k in ks)
        for k, v in vals.items():
            write_acc(home, k, v)
        days = rnd.randint(1, 4)
        due_in(days)
        sweep()
        sk = sorted(ks)
        g = ref_group([vals[k] for k in sk], days)
        check([acc(home, k) - vals[k] for k in sk] == g, "M7. sweep %d: %s over %d days -> %s" % (case, [vals[k] for k in sk], days, g))
        ng += 1
    print("M7. rounding: %d random splits, %d random group sweeps against the reference" % (nsplit, ng))

    # ---------------- M8. an unreadable account in a group
    home = fresh("broken")
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    bad = os.path.join(home, "accounts", SKYY + "-p5.properties")
    open(bad, "w").write("#SkyyBank\nbalance=not a number\n")
    badb = open(bad, "rb").read()
    due_in(1)
    sweep()
    k3 = [SKYY, SKYY + "-p3", SKYY + "-p4"]
    check([acc(home, k) - LIVE4[k] for k in k3] == ref_group([LIVE4[k] for k in k3], 1) and open(bad, "rb").read() == badb,
          "M8. an unreadable file: left out of the sum, never written")

    # ---------------- M9. interest switched off
    home = fresh("off", cfg=dict(p1=0.0, p2=0.0, p3=0.0))
    write_acc(home, SKYY, 500000)
    last = due_in(2)
    sweep()
    check(acc(home, SKYY) == 500000 and int(BC.LAST) == last + 2 * DAY, "M9. every rate 0: nothing paid, the clock still moves")
    check(not BC.on() and str(jc("new", "BankPage").rateText(False)) == "Interest is switched off on this server.", "M9. off texts")

    # ---------------- U. THE UPDATE on scratch copies of the live bank folder
    src = os.path.join(live_bank(), "Skyy_SkyyBank")
    if not os.path.isdir(src):
        print("U. live bank folder not found - a synthetic 0.1.6 folder is used")
    CR = JClass(PKG + "CfgRows", loader=L["new"])
    CH = JClass(PKG + "CfgHist", loader=L["new"])
    CL = JClass(PKG + "CfgLog", loader=L["new"])

    def ucopy(tag, cfg_text=None, nocfg=False, empty=False):
        home = os.path.join(SCRATCH, "u", tag, "mods", "Skyy_SkyyBank")
        if os.path.isdir(os.path.dirname(os.path.dirname(home))):
            shutil.rmtree(os.path.dirname(os.path.dirname(home)))
        if empty:
            os.makedirs(home)
        elif os.path.isdir(src):
            shutil.copytree(src, home)
        else:
            os.makedirs(os.path.join(home, "accounts"))
            open(os.path.join(home, "config.properties"), "wb").write(
                b"#SkyyBank config\r\n#Tue Oct 06 18:11:23 MDT 2026\r\ninterestPercent=2\r\nintervalMinutes=60\r\n"
                b"lastInterestMillis=1791331875076\r\nmaxPrincipal=10000000\r\n")
            for k, v in LIVE4.items():
                write_acc(home, k, v)
        if cfg_text is not None:
            open(os.path.join(home, "config.properties"), "wb").write(cfg_text)
        if nocfg and os.path.exists(os.path.join(home, "config.properties")):
            os.remove(os.path.join(home, "config.properties"))
        restart(home)
        CR.HOME = None
        CH.DIR = None
        CL.FILE = None
        BC.LAST = 0
        BC.NOTICE = 0
        RECS.clear()
        return home

    def umig(home):
        return str(BM.run(Paths.get(home)))

    home = ucopy("live")
    old_cfg = open(os.path.join(home, "config.properties"), "rb").read()
    old_acc = dict((k, v) for k, v in snapshot(home).items() if k.startswith("accounts"))
    mlast = int(re.search(rb"lastInterestMillis=(\d+)", old_cfg).group(1))
    t0 = now()
    msg = umig(home)
    new_cfg = open(os.path.join(home, "config.properties"), "rb").read()
    want = re.sub(rb"lastInterestMillis=\d+\r?\n", b"", old_cfg).replace(b"intervalMinutes=60", b"intervalSeconds=86400")
    check(new_cfg == want, "U. live copy: only intervalMinutes=60 -> intervalSeconds=86400 and the lastInterestMillis line removed")
    check(old_cfg.count(b"\r\n") - 1 == new_cfg.count(b"\r\n") and b"\n" not in new_cfg.replace(b"\r\n", b""), "U. CRLF kept")
    check(state_last(home) == mlast, "U. state.properties = 0.1.6's last payout (%d)" % mlast)
    stp = read_props(os.path.join(home, "state.properties"))
    check(stp is not None and int(stp.get("noticeDaily1", "0")) >= t0, "U. the one-time chat line is armed (noticeDaily1)")
    hist = os.path.join(home, "config-history")
    baks = [f for f in os.listdir(hist) if f.endswith(".bak")] if os.path.isdir(hist) else []
    check(len(baks) == 1 and open(os.path.join(hist, baks[0]), "rb").read() == old_cfg, "U. one History copy = the old bytes (%s)" % baks)
    check(os.path.exists(os.path.join(hist, "index.log")) and "before the 0.1.7 daily interest update" in open(os.path.join(hist, "index.log"), encoding="utf8").read(),
          "U. config-history/index.log names the update")
    chl = open(os.path.join(home, "config-changes.log"), encoding="utf8").read().splitlines() if os.path.exists(os.path.join(home, "config-changes.log")) else []
    check(len(chl) == 1 and chl[0].split("\t")[1:] == ["SkyWynn update 0.1.7", "-", "update", "intervalSeconds", "3600", "86400", "ok"],
          "U. one change-log line for Undo: %s" % chl)
    check(os.path.exists(os.path.join(home, "migrations", "bank-daily-1.done")), "U. the marker")
    check(dict((k, v) for k, v in snapshot(home).items() if k.startswith("accounts")) == old_acc, "U. account files untouched")
    check("intervalSeconds 3600 -> 86400" in msg, "U. the INFO line says what changed")
    after1 = snapshot(home)
    msg2 = umig(home)
    check(snapshot(home) == after1 and msg2 == "", "U. second run: nothing changes anywhere (%d files byte-identical)" % len(after1))
    restart(home)
    BC.LAST = 0
    BC.load()
    check(int(BC.INTERVAL_MS) == DAY and float(BC.PCT1) == 2.0 and int(BC.MAX_PRINCIPAL) == 10000000 and str(BC.SCOPE) == "account"
          and int(BC.LAST) == mlast, "U. the loader: once a day, 2 / 1 / 0.5%, account-wide, the clock = the last hourly payout")
    check(snapshot(home) == after1, "U. the loader writes nothing on an updated server")
    # the first daily payout on the live balances (the clock set back one day: the day has passed)
    bals = dict((k[len("accounts") + 1:-len(".properties")], acc(home, k[len("accounts") + 1:-len(".properties")]))
                for k in old_acc if k.endswith(".properties"))
    groups = {}
    for k in sorted(bals):
        groups.setdefault(k[:36], []).append(k)
    ACTIVE.clear()
    STATES.clear()
    bridge()
    BC.LAST = int(BC.LAST) - DAY if now() - int(BC.LAST) < DAY else int(BC.LAST)
    full = (now() - int(BC.LAST)) // DAY
    sweep()
    tot_new = 0
    for o_, ks in groups.items():
        g = ref_group([bals[k] for k in ks], min(full, 24))
        got = [acc(home, k) - bals[k] for k in ks]
        check(got == g, "U. first daily payout for %s: %s" % (o_, got))
        tot_new += sum(got)
    # 0.1.6 on a second copy, one day after its last payout (what Skyy would have got per day with the hourly rule)
    home6 = ucopy("live016")
    BS6, BC6, BT6 = jc("old", "BankStore"), jc("old", "BankConfig"), jc("old", "BankTick")
    BS6.DIR = Paths.get(os.path.join(home6, "accounts"))
    BC6.FILE = Paths.get(os.path.join(home6, "config.properties"))
    for mp in (BS6.BAL, BS6.LOADED, BS6.EPOCH):
        mp.clear()
    BC6.load()
    BC6.LAST = now() - DAY
    BT6.sweep()
    tot_old = sum(acc(home6, k) - bals[k] for k in bals)
    print("U. live copy %s: one day = %d coins now (%s); 0.1.6 paid %d in its 24-hour catch-up sweep" % (
        dict((k[-3:] if "-p" in k else "p1", v) for k, v in bals.items()), tot_new, full, tot_old))
    check(tot_new < tot_old / 2, "U. the new day pays far less than 0.1.6's hourly day")

    # hand-edited values, LF file
    hand = (b"#SkyyBank config\n#Tue Oct 06 18:11:23 MDT 2026\ninterestPercent=5\nintervalMinutes=30\nlastInterestMillis=1791331875076\n"
            b"maxPrincipal=20000000\n")
    home = ucopy("hand", cfg_text=hand)
    msg = umig(home)
    cfgb = open(os.path.join(home, "config.properties"), "rb").read()
    check(cfgb == hand.replace(b"lastInterestMillis=1791331875076\n", b""), "U. hand-edited: values kept, only the clock line moved; LF kept")
    check(not os.path.exists(os.path.join(home, "config-changes.log")), "U. hand-edited: no change-log line (nothing to undo)")
    check(all(x in msg for x in ("kept hand-edited intervalMinutes=30", "kept hand-edited interestPercent=5", "kept hand-edited maxPrincipal=20000000")),
          "U. hand-edited: one INFO line per kept value")
    a1 = snapshot(home)
    check(umig(home) == "" and snapshot(home) == a1, "U. hand-edited: second run changes nothing")
    restart(home)
    BC.load()
    check(int(BC.INTERVAL_MS) == 1800000 and float(BC.PCT1) == 5.0 and int(BC.MAX_PRINCIPAL) == 20000000,
          "U. hand-edited: the loader keeps 30 minutes, 5%, 20M (now in brackets)")
    # a file that already says intervalSeconds (hand-made): kept
    home = ucopy("secs", cfg_text=b"intervalSeconds=7200\r\nintervalMinutes=60\r\n")
    umig(home)
    check(open(os.path.join(home, "config.properties"), "rb").read() == b"intervalSeconds=7200\r\nintervalMinutes=60\r\n",
          "U. intervalSeconds already present: nothing rewritten")
    # no config.properties, but accounts: defaults + a fresh clock + the notice; nothing at all: the marker only
    home = ucopy("nocfg", nocfg=True)
    t0 = now()
    umig(home)
    check(os.path.exists(os.path.join(home, "migrations", "bank-daily-1.done")) and not os.path.exists(os.path.join(home, "config.properties"))
          and state_last(home) >= t0, "U. no config.properties: marker + a fresh clock (the loader writes the defaults)")
    restart(home)
    BC.load()
    cfgt = open(os.path.join(home, "config.properties"), "rb").read()
    check(cfgt == K_DEFAULT.replace("\n", os.linesep).encode("ascii") and int(BC.INTERVAL_MS) == DAY, "U. the loader wrote the 0.1.7 default file")
    home = ucopy("empty", empty=True)
    umig(home)
    check(sorted(os.listdir(home)) == ["migrations"], "U. a new server: only the marker")
    # a blocked config-history: nothing rewritten, no marker; the next start finishes
    home = ucopy("blocked")
    oldb = open(os.path.join(home, "config.properties"), "rb").read()
    open(os.path.join(home, "config-history"), "w").write("a file where the folder should be")
    umig(home)
    check(open(os.path.join(home, "config.properties"), "rb").read() == oldb and not os.path.exists(os.path.join(home, "migrations")),
          "U. History copy impossible: config.properties untouched, no marker")
    check(any("NOT updated" in x for x in logs()), "U. ... and one WARNING")
    check(state_last(home) == mlast, "U. ... the clock already moved (idempotent: the next run keeps it)")
    restart(home)
    BC.LAST = 0
    BC.load()
    check(int(BC.INTERVAL_MS) == DAY and int(BC.LAST) == mlast,
          "FIX F1. an update stopped half-way (config still intervalMinutes=60): the loader pays ONCE A DAY, clock = the last hourly payout (%d ms)" % int(BC.INTERVAL_MS))
    os.remove(os.path.join(home, "config-history"))
    restart(home)
    umig(home)
    check(open(os.path.join(home, "config.properties"), "rb").read() == want and os.path.exists(os.path.join(home, "migrations", "bank-daily-1.done")),
          "U. unblocked: the next start finishes the update")

    # the config kit on the updated live copy (Server Setup -> Bank)
    home = os.path.join(SCRATCH, "u", "live", "mods", "Skyy_SkyyBank")
    restart(home)
    BC.load()
    CP, CF = JClass(PKG + "CfgPub", loader=L["new"]), JClass(PKG + "CfgFn", loader=L["new"])
    CP.start(Paths.get(os.path.dirname(home)), HL.get("SkyyBankKit"))
    hdr = BR.get("config:def:SkyyBank")
    rows = [str(r[0]) for r in hdr[7]] if hdr is not None else []
    check(rows == ["intervalSeconds", "interestPercent", "bracket1Coins", "bracket2Percent", "bracket2Coins", "bracket3Percent",
                   "maxPrincipal", "scope", "catchUpPeriods"], "U. Server Setup -> Bank: 9 rows %s" % rows)
    vals = dict((k, str(CF.cmdGet(k))) for k in rows)
    check(vals == {"intervalSeconds": "86400", "interestPercent": "2", "bracket1Coins": "1000000", "bracket2Percent": "1",
                   "bracket2Coins": "5000000", "bracket3Percent": "0.5", "maxPrincipal": "10000000", "scope": "account",
                   "catchUpPeriods": "24"}, "U. kit get = the running values %s" % vals)
    r = str(CF.cmdSetConsole("bracket1Coins", "6000000"))
    check("Bracket 1 top must be at most Bracket 2 top" in r and int(BC.EDGE1) == 1000000, "U. check= hook refuses bracket 1 above bracket 2: %s" % r)
    r = str(CF.cmdSetConsole("intervalSeconds", "3600"))
    CP.flush()
    cfgu = open(os.path.join(home, "config.properties"), "rb").read()
    check(int(BC.INTERVAL_MS) == 3600000 and cfgu == want.replace(b"intervalSeconds=86400", b"intervalSeconds=3600"),
          "U. Undo (intervalSeconds 3600): the field and the one line in place (%s)" % r)
    r = str(CF.cmdSetConsole("scope", "profile"))
    check(str(BC.SCOPE) == "profile" and not BC.account(), "U. scope=profile through the kit: %s" % r)
    CF.cmdSetConsole("scope", "account")
    CF.cmdSetConsole("intervalSeconds", "86400")
    CP.flush()

    # ---------------- FIX ROUND (critics 2026-10-06)
    # F2: bracket 1 interest stays a whole number (0.1.6 reads it with Integer.parseInt; a fraction = an endless catch-up after a rollback)
    r = str(CF.cmdSetConsole("interestPercent", "2.5"))
    check("whole number" in r and float(BC.PCT1) == 2.0, "FIX F2. the kit refuses interestPercent 2.5: %s" % r)
    r = str(CF.cmdSetConsole("interestPercent", "3"))
    CP.flush()
    check(float(BC.PCT1) == 3.0 and b"interestPercent=3" in open(os.path.join(home, "config.properties"), "rb").read(),
          "FIX F2. a whole 3 is taken (confirm implied for console): %s" % r)
    CF.cmdSetConsole("interestPercent", "2")
    CP.flush()
    # ... and the 0.1.6 loader reads what the kit wrote
    BC6 = jc("old", "BankConfig")
    BC6.FILE = Paths.get(os.path.join(home, "config.properties"))
    BC6.LAST = 0
    BC6.load()
    check(int(BC6.PERCENT) == 2 and int(BC6.LAST) > 0, "FIX F2. SkyyBank 0.1.6 reads the kit-written config (percent %d, clock set)" % int(BC6.PERCENT))

    # F1: rollback to the REAL 0.1.6 and forward again: nothing paid twice, still daily, no file to delete
    home = ucopy("rollback")
    umig(home)
    restart(home)
    BC.LAST = 0
    BC.load()
    stale = int(BC.LAST)
    BS6, BT6 = jc("old", "BankStore"), jc("old", "BankTick")
    BS6.DIR = Paths.get(os.path.join(home, "accounts"))
    BC6.FILE = Paths.get(os.path.join(home, "config.properties"))
    for mp in (BS6.BAL, BS6.LOADED, BS6.EPOCH):
        mp.clear()
    BC6.LAST = 0
    BC6.load()
    check(int(BC6.MINUTES) == 60, "FIX F1. rollback: 0.1.6 on the updated file is hourly again (%d min) - the documented rollback cost" % int(BC6.MINUTES))
    BC6.LAST = now() - 3 * 3600000 - 5000           # three hours of 0.1.6 running
    BT6.sweep()
    t6 = int(BC6.LAST)
    c6 = open(os.path.join(home, "config.properties"), "rb").read()
    check(b"intervalMinutes=60" in c6 and (b"lastInterestMillis=%d" % t6) in c6 and b"intervalSeconds" not in c6,
          "FIX F1. 0.1.6 rewrote config.properties (intervalMinutes=60, its clock %d)" % t6)
    acc6 = dict((k, v) for k, v in snapshot(home).items() if k.startswith("accounts"))
    check(umig(home) == "", "FIX F1. forward again: the marker is there, no second update")
    restart(home)
    RECS.clear()
    BC.LAST = 0
    BC.load()
    check(int(BC.INTERVAL_MS) == DAY, "FIX F1. forward again: intervalMinutes=60 (0.1.6's rewrite) is read as ONCE A DAY (%d ms)" % int(BC.INTERVAL_MS))
    check(int(BC.LAST) == t6 and state_last(home) == t6 and stale < t6,
          "FIX F1. forward again: the clock = 0.1.6's last payout (%d), not the stale state.properties (%d); saved" % (t6, stale))
    check(any("newer lastInterestMillis" in x for x in logs()), "FIX F1. ... with one WARNING")
    sweep()
    check(dict((k, v) for k, v in snapshot(home).items() if k.startswith("accounts")) == acc6,
          "FIX F1. forward again: the first sweep pays nothing (0.1.6 already paid those hours; critic: ~24 x 45k before)")
    # the old advice (delete the marker): BankMig moves a stale state.properties up to 0.1.6's clock before removing the line
    os.remove(os.path.join(home, "migrations", "bank-daily-1.done"))
    open(os.path.join(home, "state.properties"), "w").write("lastInterestMillis=%d\n" % stale)
    restart(home)
    umig(home)
    c7 = open(os.path.join(home, "config.properties"), "rb").read()
    check(state_last(home) == t6 and b"lastInterestMillis" not in c7 and b"intervalSeconds=86400" in c7,
          "FIX F1. marker deleted + stale state: the update re-runs and moves the clock up to 0.1.6's (%s)" % state_last(home))
    restart(home)
    BC.LAST = 0
    BC.load()
    sweep()
    check(int(BC.LAST) == t6 and dict((k, v) for k, v in snapshot(home).items() if k.startswith("accounts")) == acc6,
          "FIX F1. ... and the sweep after it pays nothing")

    # F4 / F5 / F2: load() warnings + the unreadable clock kept
    home = ucopy("warn", cfg_text=b"intervalSeconds=86400\r\ninterestPercent=2.5\r\nbracket1Coins=6000000\r\nbracket2Coins=5000000\r\n")
    open(os.path.join(home, "state.properties"), "w").write("lastInterestMillis=not a number\n")
    BC.LAST = 0
    BC.load()
    lg = logs()
    check(any("bracket tops are out of order" in x for x in lg), "FIX F4. a hand-typed bracket order the kit refuses: a WARNING at load")
    check(any("interestPercent=2.5 is not a whole number" in x for x in lg), "FIX F2. a hand-typed fractional interestPercent: a WARNING at load")
    check(os.path.exists(os.path.join(home, "state.properties.unreadable")) and
          open(os.path.join(home, "state.properties.unreadable")).read() == "lastInterestMillis=not a number\n"
          and any("cannot be read - a copy is kept" in x for x in lg) and abs(int(BC.LAST) - now()) < 60000,
          "FIX F5. an unreadable state.properties: copied to state.properties.unreadable, one WARNING, the clock restarts at now")

    # F7: a forward clock jump while running is said loudly (paid as back-pay, the lock)
    home = fresh("jump")
    write_acc(home, SKYY, 500000)
    BC.STARTED = now() - 10 * DAY
    due_in(3)
    sweep()
    check(any("came due at once while the server was running" in x for x in logs()) and acc(home, SKYY) == 500000 + ref_group([500000], 3)[0],
          "FIX F7. 3 payouts due while running: a WARNING, paid as back-pay")
    home = fresh("jump0")
    write_acc(home, SKYY, 500000)
    BC.STARTED = now()
    due_in(3)
    sweep()
    check(not any("came due at once" in x for x in logs()), "FIX F7. 3 days off before this start: no warning (plain back-pay)")

    # F8: every group of a sweep in one lock hold
    Mod = JClass("java.lang.reflect.Modifier")
    pa = [m for m in BS.class_.getDeclaredMethods() if str(m.getName()) == "payAll"]
    check(len(pa) == 1 and Mod.isSynchronized(pa[0].getModifiers()) and Mod.isStatic(pa[0].getModifiers()),
          "FIX F8. BankStore.payAll is static synchronized (one lock hold for the whole sweep)")
    home = fresh("payall")
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    write_acc(home, OTHER, 3000000)
    due_in(1)
    sweep()
    check([acc(home, k) - LIVE4[k] for k in keys] == ref_group([LIVE4[k] for k in keys], 1) and acc(home, OTHER) == 3000000 + ref_interest(3000000),
          "FIX F8. the sweep through payAll pays both players exactly as before")

    # F3 / F9 / F10: the chat texts, through a real PlayerRef whose packet handler records the packets
    CtPool = JClass("javassist.ClassPool")
    cpool = CtPool(True)
    phc = cpool.makeClass("skyyharness.CapPH", cpool.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    phc.addField(JClass("javassist.CtField").make("public static java.util.List OUT = new java.util.concurrent.CopyOnWriteArrayList();", phc))
    phc.addMethod(JClass("javassist.CtNewMethod").make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", phc))
    capd = os.path.join(SCRATCH, "capph")
    phc.writeFile(capd)
    CapPH = JClass("skyyharness.CapPH", loader=loader(capd))
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Unsafe0 = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    Unsafe0.setAccessible(True)
    U0 = Unsafe0.get(None)
    cpr = U0.allocateInstance(PRc.class_)
    f_ = PRc.class_.getDeclaredField("uuid")
    f_.setAccessible(True)
    f_.set(cpr, UUID.fromString(SKYY))
    f_ = PRc.class_.getDeclaredField("packetHandler")
    f_.setAccessible(True)
    f_.set(cpr, U0.allocateInstance(CapPH.class_))

    def said(fn):
        CapPH.OUT.clear()
        try:
            fn()
        except Exception as ex:
            return "EXC %s" % ex
        return " | ".join(str(p.message.rawText) for p in CapPH.OUT)

    home = fresh("chat")
    open(os.path.join(home, "config.properties"), "w", newline="").write(K_DEFAULT.replace("\n", "\r\n"))
    for k, v in LIVE4.items():
        write_acc(home, k, v)
    ACTIVE[SKYY] = SKYY + "-p3"
    BC.LAST = now()
    ADM, CMD = jc("new", "BankConfigCmd"), jc("new", "BankCmd")
    cfg0 = open(os.path.join(home, "config.properties"), "rb").read()
    t = said(lambda: ADM.apply(cpr, "2", "60", None))
    check("Nothing changed" in t and int(BC.INTERVAL_MS) == DAY and open(os.path.join(home, "config.properties"), "rb").read() == cfg0,
          "FIX F3. /bankconfig 2 60 (the old habit) is refused, nothing changed: %r" % t)
    t = said(lambda: ADM.apply(cpr, "2", "2880", None))
    check("Nothing changed" not in t and "(2880 min = 172800 s)" in t, "FIX F3. a LONGER interval goes on to the kit (here denied: no admin in the harness): %r" % t)
    t = said(lambda: ADM.apply(cpr, None, None, None))
    check(re.search(r"next payout in 2[34] h \d+ min\.", t) is not None and "~" not in t, "FIX F3. /bankconfig shows the wait as h / min: %r" % t)
    BC.LAST = now() - DAY - 5000
    t = said(lambda: ADM.apply(cpr, None, None, None))
    check("next payout any moment now" in t and "-" not in t.split("next payout")[1][:20], "FIX F3. a due payout reads 'any moment now', never a negative wait: %r" % t)
    BC.LAST = now()
    ngc = int(BS.nextGain(UUID.fromString(SKYY)))
    t = said(lambda: CMD.status(cpr, UUID.fromString(SKYY)))
    check(("Your next payout: +%d coins in 2" % ngc) in t and "this profile's share" in t, "FIX F10. /bank status: the amount, when, and the share note: %r" % t)
    print("FIX. /bank status: %s" % t)
    BC.SCOPE = "profile"
    t = said(lambda: CMD.status(cpr, UUID.fromString(SKYY)))
    check("this profile's share" not in t and " in 2" in t, "FIX F10. scope=profile: no share note: %r" % t)
    BC.SCOPE = "account"
    BTk = jc("new", "BankTick")
    t = str(BTk.payText(8732, 32988, 1, 617254, DAY - 30000))
    check(t == "[Bank] You earned 8732 coins interest - this profile's share; all your profiles earned 32988. Bank balance: 617254. Next payout in 23 h 59 min.",
          "FIX F9. the payout chat line: %r" % t)
    t = str(BTk.payText(500, 500, 3, 1000, 0))
    check(t == "[Bank] You earned 500 coins interest (3 days). Bank balance: 1000. Next payout any moment now.", "FIX F9. one profile, back-pay: %r" % t)

    # ---------------- P. page builds 0.1.6 vs 0.1.7
    Unsafe = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    Unsafe.setAccessible(True)
    U_ = Unsafe.get(None)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    fu = PRc.class_.getDeclaredField("uuid")
    fu.setAccessible(True)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def build(k):
        pr = U_.allocateInstance(PRc.class_)
        fu.set(pr, UUID.fromString(SKYY))
        pg = jc(k, "BankPage")(pr)
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else re.sub(r'"t": ?"[0-9a-f]+"', '"t":"<tok>"', str(e.data)))
               for e in ev.getEvents()]
        return cmds, evs

    phome = fresh("page")
    for k, v in LIVE4.items():
        write_acc(phome, k, v)
    ACTIVE[SKYY] = SKYY + "-p3"
    jc("old", "BankStore").DIR = BS.DIR
    for mp in (jc("old", "BankStore").BAL, jc("old", "BankStore").LOADED):
        mp.clear()
    BC6 = jc("old", "BankConfig")
    BC6.LAST = now()
    BC.LAST = now()
    jc("new", "BankWatch").STOP = True
    c6, e6 = build("old")
    c7, e7 = build("new")
    app = lambda cs: [(s_, t_) for ty, s_, t_, d_ in cs if "append" in ty.lower()]
    sets = lambda cs: dict((s_, d_) for ty, s_, t_, d_ in cs if "append" not in ty.lower())
    check(app(c6) == app(c7), "P. the same markup appends (%d)" % len(app(c7)))
    check(e6 == e7, "P. the same 7 bindings (click token aside)%s" % ("" if e6 == e7 else ": %s / %s" % ([x for x in e6 if x not in e7], [x for x in e7 if x not in e6])))
    s6, s7 = sets(c6), sets(c7)
    dif = sorted(k for k in set(s6) | set(s7) if s6.get(k) != s7.get(k))
    check(dif == ["#SkyyBGain.Text", "#SkyyBNext.Text", "#SkyyBRate.Text"] or dif == ["#SkyyBGain.Style.TextColor", "#SkyyBGain.Text", "#SkyyBNext.Text", "#SkyyBRate.Text"]
          or set(dif) <= {"#SkyyBGain.Text", "#SkyyBNext.Text", "#SkyyBRate.Text", "#SkyyBGain.TextColor", "#SkyyBGain.Style.TextColor"},
          "P. only the interest lines differ: %s" % dif)
    ng = int(BS.nextGain(UUID.fromString(SKYY)))
    def jt(v):
        try:
            v = json.loads(v)
        except Exception:
            return v
        return v.get("0") if isinstance(v, dict) else v
    rate, nxt, gain = jt(s7.get("#SkyyBRate.Text")), jt(s7.get("#SkyyBNext.Text")), jt(s7.get("#SkyyBGain.Text"))
    print("P. 0.1.6: %r | %r" % (jt(s6.get("#SkyyBRate.Text")), jt(s6.get("#SkyyBGain.Text"))))
    print("P. 0.1.7: %r | %r | %r" % (rate, nxt, gain))
    check(rate == "Interest once a day: 2% up to 1M, 1% up to 5M, 0.5% up to 10M - all your profiles together", "P. rate line: %r" % rate)
    check(gain.startswith("Your next payout: +%s coins" % format(ng, ",")), "P. payout line = nextGain() %d: %r" % (ng, gain))
    check(re.match(r"Next interest: in 2[34] h \d+ min", nxt or "") is not None, "P. next payout in ~24 h: %r" % nxt)
    W = K["BANK_W"] - 2 * K["BANK_PAD"] - 2 * K["bank_px"](SUI.WELL_PAD)
    for t_, fs in ((rate, K["BANK_FS"]["heading"]), (gain, K["BANK_FS"]["text"]), (nxt, K["BANK_FS"]["text"])):
        check(SUI.text_width(t_, fs, bold=True) <= W, "P. fits one line (%d px): %r" % (W, t_))
    due_in(1)
    sweep()
    check(acc(phome, SKYY + "-p3") - LIVE4[SKYY + "-p3"] == ng, "P. the payout then pays what the page showed (%d)" % ng)
    PO = jc("new", "BankPage")
    for rd, gn, on in ((True, 5, True), (True, 0, True), (False, 5, True), (True, 5, False), (True, -1, True)):
        txt = str(PO.gainText(rd, 100, gn, on))
        check(bool(PO.payoutOn(rd, gn, on)) == txt.startswith("Your next payout"), "P. payoutOn == the payout line (%s %s %s)" % (rd, gn, on))
    # the one-time chat line (BankNotice): maybe() -> the worker -> the told file; once per player; not after 30 days; not without
    # the update's noticeDaily1
    st = str(jc("new", "BankNotice").text())
    check("once a day" in st and "2% up to 1M" in st, "P. the one-time chat line: %r" % st)
    BN = jc("new", "BankNotice")
    Ex = JClass("java.util.concurrent.Executors")
    BT.WORKER = Ex.newSingleThreadExecutor()
    BN.load(Paths.get(phome))
    BN.TOLD.clear()
    tf = os.path.join(phome, "notice-daily-1.txt")
    BC.NOTICE = 0
    BN.maybe(None, UUID.fromString(SKYY))
    time.sleep(0.3)
    check(not os.path.exists(tf) and BN.TOLD.size() == 0, "P. notice: nothing without the update's noticeDaily1")
    BC.NOTICE = now() - 31 * DAY
    BN.maybe(None, UUID.fromString(SKYY))
    time.sleep(0.3)
    check(not os.path.exists(tf), "P. notice: nothing 31 days after the update")
    BC.NOTICE = now()
    for _ in range(3):
        BN.maybe(None, UUID.fromString(SKYY))
        BN.maybe(None, UUID.fromString(OTHER))
    time.sleep(0.5)
    told = open(tf, encoding="utf8").read().split() if os.path.exists(tf) else []
    check(sorted(told) == sorted([SKYY, OTHER]), "P. notice: each player once, written to notice-daily-1.txt (%s)" % told)
    BN.TOLD.clear()
    BN.load(Paths.get(phome))
    BN.maybe(None, UUID.fromString(SKYY))
    time.sleep(0.3)
    check(open(tf, encoding="utf8").read().split() == told, "P. notice: after a restart the told list is read back (no second line)")
    BT.WORKER.shutdown()
    BT.WORKER = None

    # ---------------- G. the page id
    pid = K["BANK_PAGE_ID"]
    chk = re.search(r'BANK_PAGE_CHECKED = "([^"]+)"', open(SCRIPT, encoding="utf8").read()).group(1)
    ready = CB["new"][PKG + "SkyyBankPlugin"]
    check(("page %s)" % pid).encode() in ready, "G. the jar's ready line carries the kit's page id %s" % pid)
    check(chk == pid, "G. BANK_PAGE_CHECKED (%s) = the page now (%s)" % (chk, pid))
    print("G. page id %s (checked: %s)" % (pid, chk))


K_DEFAULT = None


def main():
    global K_DEFAULT
    claim_scratch()
    for f in (JAR, OLD, PROFS):
        if not os.path.isfile(f):
            raise SystemExit("missing " + f)
    tree = ast.parse(open(SCRIPT, encoding="utf8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BANK_CFG_TEXT" for t in n.targets):
            K_DEFAULT = eval(compile(ast.Expression(n.value), SCRIPT, "eval"))
    assert K_DEFAULT and "intervalSeconds=86400" in K_DEFAULT
    t0 = time.time()
    try:
        run()
    except Exception:
        import traceback
        traceback.print_exc()
        FAILS.append("harness crashed")
    print("%d checks, %d fail(s) in %.0f s" % (OKS[0] + len(FAILS), len(FAILS), time.time() - t0))
    os.chdir(ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
