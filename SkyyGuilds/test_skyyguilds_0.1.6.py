"""SkyyGuilds 0.1.6 - bare-JVM harness: the leave / kick refund (Skyy, OPEN-QUESTIONS.md LOCKED 2026-10-01: "some of it but not all.
like 30%-40% of what they donated."). Derived from test_skyyguilds_0.1.5.py; copy it to the next version.

    python SkyyGuilds/test_skyyguilds_0.1.6.py [--jar <SkyyGuilds-0.1.6.jar>] [--old <SkyyGuilds-0.1.5.jar>] [--coins <SkyyCoins jar>]
                                               [--live <Skyy_SkyyGuilds folder>] [--dir <scratch>] [--keep]

Build first (python tools/guilds_0_1_6_patch.py, then python SkyyGuilds/build_skyyguilds_0.1.6.py). ONE JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; 0.1.5 (the live SET pin), 0.1.6 and the
real SkyyCoins 0.1.5 each in their own class loader; a fake Universe (Unsafe-allocated) holds the online players; the JVM-global
bridge map holds fake SkyyCoins / SkyySkills / SkyyProfiles functions, or the REAL SkyyCoins CoinFn objects in part R) checks:
  A  every class of the three jars loads, verifies (-Xverify:all) and initialises
  B  the contract in bytes, 0.1.5 -> 0.1.6: every class but GCfg, GuildStore, GuildPage, CfgRows, CfgFile is byte-identical (Guild,
     GMember, XpTask, the commands, GHooks ...); CfgFn / SkyyGuildsPlugin / manifest.json = 0.1.5's bytes once "0.1.5" is written back
     (the ready line differs only by the version, the page id is 0.1.5's); CfgFile: only the two row counts 14 -> 15 in <clinit>;
     GCfg: + LEAVE_REFUND, only parse / load / <clinit> changed; GuildStore: exactly seedLine / leaveNote / leaveWarning / leave / kick
     / logParts changed + refundFull / refundInfo / refundText / toGuildNet / payRefund / kickNote / quoteOk / quoteLeave /
     noCoinsLeave / requote new, every other method instruction-identical (disbandNow, payouts, deposit, withdraw, transfer, disband,
     accept ...); GuildPage: only handleDataEvent changed (the kick note, the Leave re-arm)
  C  XpTask (byte-identical) gives the same guild XP on both jars over a random walk
  P  0.1.5's disband split (unchanged code) against the Python reference
  Q  disbands end to end with the refund at its default 35%: /guild disband (with an offline member), the last member's /guild leave
     and the payout refusals give the same purses, texts and files on 0.1.5 and 0.1.6 (disband + last-member leave unchanged)
  R  the REAL SkyyCoins 0.1.5 (CoinStore / CoinFn in their own loader, balance files in scratch, a stand-in profile:fn:key): the
     disband of 0.1.5; a kicked OFFLINE member's refund lands in balances/<uuid>-p2.properties (their ACTIVE profile, profile 1
     untouched); an unreadable balance file = kicked anyway, refund skipped, every balance file byte-identical, the bank keeps it
  S  running totals + the seed: the scratch COPY of the live Skyy_SkyyGuilds data (already seeded by 0.1.5; the live folder is only
     read) started twice on 0.1.6 = no churn (the config gains the 0.1.6 key once, guild files / banklog.log byte-identical, no
     seed); the same copy with net.* / netSeed stripped (what 0.1.4 leaves) seeds the same on 0.1.5 and 0.1.6; 0.1.5 loads a 0.1.6
     file with refunds (rollback safe); 0.1.5's tests of the trimmed log, partial history, new guilds, /guildadmin info
  V  0.1.5's review hardening (payout plan lines, rollback save + WARN) on 0.1.6; the leave confirms with the refund at 0% are
     0.1.5's texts exactly (0 = 0.1.5 behaviour)
  L  the refund: maths (35% of 1,000 = 350, of 999 = 349, zero / negative net = 0, pct 0 / 100, a smaller bank caps it, 1e18, random
     vs the Python reference); the config loader (fresh file, the 0.1.5 file gets the key once, clamps); leave online (Member page +
     /guild leave asking once, Admin, the Leader passing the guild on), kick online + offline; texts; the two logs; refusals: a leave
     with an unreadable purse / SkyyCoins refusing / a blocked guild file / no SkyyCoins is refused with NOTHING changed (file bytes,
     bank, totals, members, purses, logs); a kick in the same cases still kicks, skips the refund (WARN + kick-refund-skipped line),
     the bank keeps it; banklog.log lines read by parseBankLine on both jars, 0.1.6's seed counts the refunds, 0.1.5's skips them and
     still gives the current members' totals (partial); random leave / kick / rejoin / deposit / withdraw fuzz with random pct and
     failures: every player's net adds up to the bank after every step, coins are conserved, every refund = the reference, a positive
     net ends at 0 (the rest in "~guild");
     review fixes (L8): leave + rejoin x 12 pays 35% once (was 99.3%), a rejoined member's old coins are no disband share; a refund
     that changed after the confirm asks again (page + /guild leave), an empty bank says so; no SkyyCoins = refused up front (page
     does not arm; Member / Admin / Leader texts), no refund = leaves without SkyyCoins; the info line before the purse is paid; a
     stale page Kick; 0.1.5 loads and keeps net.~guild
  D  differential page builds 0.1.5 vs 0.1.6 (refund 0%): bindings, b.set lines, visible texts and ids identical for 0.1.5's 42 states;
     0.1.6 states with the refund texts (widest leave / kick confirms, capped, results, refusals, the bank log view with the refund
     lines) through check_markup / check_page / assert_proven
  E  clicks through handleDataEvent on both jars at 0% (two scripted sessions): identical results, boxes, views, purses, guilds,
     bindings, b.set lines; a 35% session on 0.1.6: the armed Kick names the refund, kick + page leave pay it, a refund changed after
     the Leave confirm re-arms the Leave, the page shows it
  F  text fit (SUI.text_width, the client's font tables) of every text the states showed (+ the refund texts)
  G  the page id: 0.1.5's page (26645a3ab908) = GUILD_PAGE_CHECKED = the id in the jar's ready line
  K  the Server Setup row through the config kit (CfgPub.start in a scratch mods folder): config:def:SkyyGuilds lists 0.1.5's 14 rows
     + "Leave refund (% of contribution)" (bank, int 35, 0-100, %, live); set 40 through the kit = live (the field) + the file line;
     101 / -1 refused; a leave then pays 40%
Not testable without the game: how the client draws the page, chat lines to players (say() swallows the fake players' send), a
live SkyyProfiles (stand-in key function). Nothing is deployed and nothing outside the scratch folder is written (default
tools/dev/scratch/guilds016/harness, deleted at the end unless --keep; TEMP / TMP and java.io.tmpdir point into it). Exit code 1 on
any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, random, collections, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.6", "0.1.5"
PKG = "com.skyy.guilds."
SCRIPT = os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION)
CFGROWS_CHANGED = ["<clinit>", "header"]       # the row table + the header (version, row count)
PREFIX = "SkyyG"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "guilds016", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGuilds-%s.jar" % OLD_VERSION)))
COINS_JAR = os.path.abspath(arg("--coins", os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.5.jar")))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                  "Saves", "HUD mod", "mods", "Skyy_SkyyGuilds")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = collections.Counter()


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


# ------------------------------------------------------------------------------------------------ the kit's page, NOW (no JVM)
def kit_page():
    """Run the generated script's page code (its GUILD_* constants and guild_* functions) on the CURRENT kit, without the rest of
    the build: returns (SUI, namespace)."""
    import skyyui as SUI
    SUI.verify(quiet=True)
    tree = ast.parse(open(SCRIPT, encoding="utf8").read())
    body = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name.startswith("guild_"):
            body.append(n)
        elif isinstance(n, ast.Assign):
            names = [x.id for t in n.targets for x in (t.elts if isinstance(t, ast.Tuple) else [t]) if isinstance(x, ast.Name)]
            if names and all(x.startswith("GUILD_") for x in names):
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


def entries(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n, z.read(n)) for n in z.namelist())
    z.close()
    return out


def swap_back(old_b, new_b, old_needle, new_needle):
    """new_b with its one UTF8 constant holding new_needle replaced by old_b's one holding old_needle == old_b ?  (+ the two texts)"""
    ro = [e for e in cp_utf8(old_b) if old_needle in e[2]]
    rn = [e for e in cp_utf8(new_b) if new_needle in e[2]]
    if len(ro) != 1 or len(rn) != 1:
        return False, None, None
    s0, e0, t0 = ro[0]
    s1, e1, t1 = rn[0]
    return new_b[:s1] + old_b[s0:e0] + new_b[e1:] == old_b, t0.decode("utf8"), t1.decode("utf8")


# ------------------------------------------------------------------------------------------------ markup helpers (no JVM)
TEXT_RE = re.compile(r'(?<![A-Za-z])Text: "((?:[^"\\]|\\.)*)"')
ID_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{")
COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")
WHEN_RE = re.compile(r"\d\d-\d\d \d\d:\d\d")
LEFT_RE = re.compile(r"\d+:\d\d left")
NEW_SET_RE = re.compile(r"#SkyyGRowNet\d+\.Text$")            # 0.1.5: the one new b.set line per member row
ROW_SEL_RE = re.compile(r"#SkyyGRow(Name|Rank|Net|Xp|Day|On)(\d+)\.Text$")
BTN_RE = re.compile(r'TextButton #\w+ \{[^{}]*?Text: "([^"]*)"; Style: TextButtonStyle\(Default: \(Background: \([^)]*\), '
                    r'LabelStyle: \(FontSize: (\d+)')


def norm(t):
    return LEFT_RE.sub("<m:ss> left", WHEN_RE.sub("<when>", t or ""))


def js(v):
    """The Java value of a Set command (its data is JSON; set(String, String) sends {"0": value})"""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:
        x = x["0"]
    return x


def is_append(typ):
    return "append" in typ.lower()


def sets_of(cmds):
    return collections.Counter((sel, norm(str(js(data)))) for typ, sel, text, data in cmds if not is_append(typ))


def texts_of(cmds):
    out = collections.Counter()
    for typ, sel, text, data in cmds:
        if is_append(typ):
            for t in TEXT_RE.findall(text or ""):
                if t:
                    out[norm(t)] += 1
        elif sel and sel.endswith(".Text"):
            v = str(js(data))
            if v:
                out[norm(v)] += 1
    return out


def ids_of(cmds):
    return set(i for typ, sel, text, data in cmds if is_append(typ) for i in ID_RE.findall(text or ""))


def first_id(text):
    m = ID_RE.search(text or "")
    return m.group(1) if m else ""


def rows_of(cmds):
    """the member rows of a built guild view, in index order: [{field: text}]"""
    rows = collections.defaultdict(dict)
    for typ, sel, text, data in cmds:
        if is_append(typ) or not sel:
            continue
        m = ROW_SEL_RE.match(sel)
        if m:
            rows[int(m.group(2))][m.group(1)] = str(js(data))
    return [rows[i] for i in sorted(rows)]


def ref_pay(nets, bank, ranks, joined):
    """Python reference of the disband split (Skyy 2026-10-01): [share] in member order"""
    n = len(nets)
    if n == 0:
        return []
    net = [d - w for d, w in nets]
    tot = sum(x for x in net if x > 0)
    best = 0
    for i in range(n):
        if net[i] > net[best] or (net[i] == net[best] and (ranks[i] > ranks[best] or (ranks[i] == ranks[best] and joined[i] < joined[best]))):
            best = i
    a = max(0, bank)
    share = [a // n] * n if tot == 0 else [(a * net[i]) // tot if net[i] > 0 else 0 for i in range(n)]
    share[best] += a - sum(share)
    return share


def num(n):
    return "{:,}".format(n)


def fmt_py(n):
    """GuildStore.fmt in Python (for the expected short contribution texts)"""
    if n < 0:
        return "-" + fmt_py(-n)
    if n < 10000:
        return str(n)
    if n < 1000000:
        t = n // 100
        return "%d.%dk" % (t // 10, t % 10)
    if n < 1000000000:
        h = n // 10000
        return "%d.%02dm" % (h // 100, h % 100)
    g = n // 10000000
    return "%d.%02db" % (g // 100, g % 100)


def net_text(v):
    return num(v) if -10 ** 15 < v < 10 ** 15 else fmt_py(v)


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JLong
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

    L = {"old": loader(OLD), "new": loader(JAR), "coins": loader(COINS_JAR)}
    EN = {"old": entries(OLD), "new": entries(JAR), "coins": entries(COINS_JAR)}
    CLS = dict((k, dict((n[:-6].replace("/", "."), b) for n, b in EN[k].items() if n.endswith(".class"))) for k in EN)

    # ---------------- A. load + verify + init
    for k in ("old", "new", "coins"):
        for n in sorted(CLS[k]):
            try:
                Cls.forName(n, True, L[k])
                COUNT["A " + k] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    OKS[0] += COUNT["A old"] + COUNT["A new"] + COUNT["A coins"]
    print("A. loaded + verified + initialised (-Xverify:all): 0.1.5 %d, 0.1.6 %d, SkyyCoins 0.1.5 %d classes" % (
        COUNT["A old"], COUNT["A new"], COUNT["A coins"]))
    if FAILS:
        return

    # ---------------- B. the contract in bytes, 0.1.5 -> 0.1.6
    old_e, new_e = EN["old"], EN["new"]
    check(sorted(old_e) == sorted(new_e), "B. the same jar entries: %s" % sorted(set(old_e) ^ set(new_e)))
    P = "com/skyy/guilds/"
    CHANGED = set(P + n + ".class" for n in ("GCfg", "GuildStore", "GuildPage", "CfgRows", "CfgFile"))
    VERSIONED = set(P + n + ".class" for n in ("CfgFn", "SkyyGuildsPlugin")) | {"manifest.json"}
    for n in sorted(old_e):
        if n in CHANGED or n not in new_e:
            continue
        if n in VERSIONED:
            if check(new_e[n].replace(b"0.1.6", b"0.1.5") == old_e[n] and old_e[n] != new_e[n],
                     "B. %s = 0.1.5's bytes once the version string is swapped back" % n):
                COUNT["B versioned"] += 1
        elif check(old_e[n] == new_e[n], "B. %s is byte-identical to 0.1.5" % n):
            COUNT["B identical"] += 1
    for n in ("Guild", "GMember", "XpTask", "GADeleteCmd", "GHooks", "GuildTick", "DayTask", "GuildOnlineFn"):
        check(old_e[P + n + ".class"] == new_e[P + n + ".class"], "B. %s is byte-identical to 0.1.5" % n)
    plug = P + "SkyyGuildsPlugin.class"
    lo = [e[2].decode("utf8") for e in cp_utf8(old_e[plug]) if b"] 0.1.5 ready (" in e[2]]
    ln = [e[2].decode("utf8") for e in cp_utf8(new_e[plug]) if b"] 0.1.6 ready (" in e[2]]
    LOG_NEW = ln[0] if len(ln) == 1 else ""
    check(len(lo) == 1 and len(ln) == 1 and LOG_NEW == lo[0].replace("] 0.1.5 ready (", "] 0.1.6 ready (") and "page 26645a3ab908)" in LOG_NEW,
          "B. the ready line differs only by the version; the page id is 0.1.5's (26645a3ab908): %r" % LOG_NEW)
    cf_o, cf_n = old_e[P + "CfgFile.class"], new_e[P + "CfgFile.class"]
    dpos = [i for i in range(min(len(cf_o), len(cf_n))) if cf_o[i] != cf_n[i]]
    check(len(cf_o) == len(cf_n) and len(dpos) == 2 and all(cf_o[i] == 14 and cf_n[i] == 15 for i in dpos),
          "B. CfgFile = 0.1.5's bytes but two constants 14 -> 15 (the row count): %s" % [(i, cf_o[i], cf_n[i]) for i in dpos])
    CP, BAIS, IP = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream"), JClass("javassist.bytecode.InstructionPrinter")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, out = ca.iterator(), []
        while it.hasNext():
            ln_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it, it.next(), cp))).replace("ldc_w ", "ldc ")
            out.append(re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln_))
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try %s" % (cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        if c.getClassInitializer() is not None:
            out["<clinit>()V"] = code_of(c.getClassInitializer())
        return out

    def fields(c):
        return sorted((str(f.getName()), str(f.getSignature())) for f in c.getDeclaredFields())

    def cmp_class(name, changed_want, gone_want, new_want, same_want, new_fields=()):
        co, cn = ct(old_e[P + name + ".class"]), ct(new_e[P + name + ".class"])
        check(sorted(fields(co) + list(new_fields)) == fields(cn), "B. %s fields: 0.1.5's + %s" % (name, list(new_fields)))
        mo, mn = methods(co), methods(cn)
        gone = sorted(k.split("(")[0] for k in mo if k not in mn)
        new = sorted(k.split("(")[0] for k in mn if k not in mo)
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
        same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
        check(gone == sorted(gone_want), "B. %s: gone %s (want %s)" % (name, gone, gone_want))
        check(new == sorted(new_want), "B. %s: new %s (want %s)" % (name, new, new_want))
        check(changed == sorted(changed_want), "B. %s: changed %s (want exactly %s)" % (name, changed, sorted(changed_want)))
        for m in same_want:
            check(m in same, "B. %s.%s is instruction-identical to 0.1.5" % (name, m))
        return changed, same

    cmp_class("CfgFile", ["<clinit>"], [], [], [])
    cmp_class("GCfg", ["<clinit>", "parse", "load"], [], [],
              ["lng", "limProp", "parseSkills", "parseLimits", "onOff", "readProps", "reloadAll", "reloadSkills", "reloadLimits",
               "migrateSkills", "writeAtomic", "missingNew", "sameExceptSkills"], new_fields=[("LEAVE_REFUND", "I")])
    GS_CHANGED = ["seedLine", "leaveNote", "leaveWarning", "leave", "kick", "logParts"]
    GS_NEW = ["refundFull", "refundInfo", "refundText", "toGuildNet", "payRefund", "kickNote", "quoteOk", "quoteLeave", "noCoinsLeave",
              "requote"]
    gs_changed, gs_same = cmp_class("GuildStore", GS_CHANGED, [], GS_NEW,
                                    ["disbandNow", "payouts", "shareOf", "payees", "shareList", "bankNote", "deposit", "withdraw",
                                     "transfer", "disband", "adminDelete", "adminInfo", "snapshot", "cmpRow", "seedNet", "loadAll",
                                     "parseBankLine", "backfillLogs", "addLog", "saveGuild", "removeMember", "successor",
                                     "disbandWarning", "promote", "demote", "invite", "accept", "netAdd", "confirm",
                                     "netValue", "netOf", "coinsAdd", "coinsGet", "coinsTake", "coinsReady", "logText", "propsOf",
                                     "loadGuildFile", "flushDirty", "archive", "create", "setLimit", "nameOfMember"])
    pg_changed, pg_same = cmp_class("GuildPage", ["handleDataEvent"], [], [],
                                    ["<init>", "safe", "jsonStr", "two", "build", "buildNone", "buildGuild", "buildLog", "colorOf",
                                     "infoLabel"])
    rows_changed, rows_same = cmp_class("CfgRows", CFGROWS_CHANGED, [], [], [])
    print("B. %d classes byte-identical to 0.1.5 (Guild, XpTask, GHooks, commands ...), %d = 0.1.5 but the version string (CfgFn, "
          "plugin, manifest); CfgFile: 2 row counts; GCfg + LEAVE_REFUND (parse / load / <clinit>); GuildStore: %d changed %s, %d new "
          "%s, %d instruction-identical; GuildPage changed %s; CfgRows changed %s" % (
              COUNT["B identical"], COUNT["B versioned"], len(gs_changed), gs_changed, len(GS_NEW), GS_NEW, len(gs_same), pg_changed,
              rows_changed))

    # ---------------- common Java objects, the fake Universe, the bridge
    UUID, Paths, Long, Boolean, Props = (JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"),
                                         JClass("java.lang.Boolean"), JClass("java.util.Properties"))
    System = JClass("java.lang.System")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    Holder = JClass("com.hypixel.hytale.component.Holder")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    BAOS, PS = JClass("java.io.ByteArrayOutputStream"), JClass("java.io.PrintStream")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    uni = U.allocateInstance(Universe.class_)
    PLAYERS = CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "players", PLAYERS.values())
    setf(None, Universe, "instance", uni)
    HOLDER = U.allocateInstance(Holder.class_)
    NAMES = {1: "Steve", 2: "Alex", 3: "Bea", 4: "Cid", 5: "Dot", 6: "Eve", 7: "Finn", 8: "Gus", 9: "Hana", 10: "Ivo", 11: "Jade",
             12: "Kai", 13: "Lumberjackmaster", 14: "Abcdefghijklmnop", 15: "m" * 16, 16: "W" * 16}

    def uid(n):
        return UUID(0x6d11d, n)

    def pref(n, online=True):
        p = U.allocateInstance(PR.class_)
        setf(p, PR, "uuid", uid(n))
        setf(p, PR, "username", NAMES.get(n, "P%d" % n))
        if online:
            setf(p, PR, "holder", HOLDER)
        return p

    def set_online(ns):
        PLAYERS.clear()
        for n in ns:
            PLAYERS.put(uid(n), pref(n))

    BR = CHM()
    System.getProperties().put("skyy.bridge", BR)
    PURSE = {}
    FAIL_ADD, FAIL_TAKE = set(), set()     # uuid strings whose coins:fn:add / take answer null (SkyyCoins refused, nothing changed)
    UNREAD = set()                         # 0.1.6: uuid strings whose purse cannot be read (get / add / take answer null; the value is kept)
    REFUND_PCT = [35]                      # 0.1.6: GCfg.LEAVE_REFUND that reset() sets on the 0.1.6 jar (its default)
    HOOK = [None]                          # V: called as HOOK[0](uuid string, amount) at the start of every coins:fn:add

    @JImplements("java.util.function.Function")
    class CoinsGet:
        @JOverride
        def apply(self, u):
            if str(u) in UNREAD:
                return None
            v = PURSE.get(str(u), 0)
            return None if v is None else Long.valueOf(v)

    @JImplements("java.util.function.Function")
    class CoinsAdd:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if HOOK[0] is not None:
                HOOK[0](u, n)
            if PURSE.get(u, 0) is None or u in FAIL_ADD or u in UNREAD:
                return None
            PURSE[u] = PURSE.get(u, 0) + n
            return Long.valueOf(PURSE[u])

    @JImplements("java.util.function.Function")
    class CoinsTake:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            have = PURSE.get(u, 0)
            if have is None or u in FAIL_TAKE or u in UNREAD:
                return None
            if have < n:
                return Boolean.FALSE
            PURSE[u] = have - n
            return Boolean.TRUE

    XP, SLOT, PKEY = {}, {}, {}

    @JImplements("java.util.function.Function")
    class SkillXp:
        @JOverride
        def apply(self, a):
            u, name = str(a[0]), str(a[1]).strip().lower()
            key = SLOT.get(name, "n:" + name)
            v = XP.get(u, {}).get(key)
            return None if v is None else Long.valueOf(v)

    @JImplements("java.util.function.Function")
    class ProfKey:
        @JOverride
        def apply(self, u):
            return PKEY.get(str(u), str(u))

    COINS = (CoinsGet(), CoinsAdd(), CoinsTake())
    SKILLFN, PROFFN = SkillXp(), ProfKey()

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    Cfg0 = jc("new", "GCfg")
    check(int(Cfg0.LEAVE_REFUND) == 35, "L. GCfg.LEAVE_REFUND starts at its default 35 (%s)" % Cfg0.LEAVE_REFUND)
    for nm, sl in zip(list(Cfg0.SK_NAMES), list(Cfg0.SK_SLOTS)):
        SLOT[str(nm)] = int(sl)
    NOW = int(System.currentTimeMillis())
    DAY = 1234

    def reset(k, tag, day_known=True, d=None):
        GS, Cfg, X = jc(k, "GuildStore"), jc(k, "GCfg"), jc(k, "XpTask")
        if d is None:
            d = os.path.join(SCRATCH, "data", k, re.sub(r"[^A-Za-z0-9]+", "-", tag))
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(os.path.join(d, "guilds"))
        GS.DIR = Paths.get(d)
        GS.GDIR = Paths.get(os.path.join(d, "guilds"))
        Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
        for m in (GS.GUILDS, GS.BYNAME, GS.BYPLAYER, GS.INVITES, GS.CONFIRM, X.BASE, X.FRAC):
            m.clear()
        GS.SEASON = 3
        GS.NEXT_ID = 7
        GS.DAY = DAY if day_known else -1
        GS.DAY_READ = int(System.currentTimeMillis()) if day_known else 0
        Cfg.SHARE, Cfg.MAX_DELTA, Cfg.LEVEL_FALLBACK, Cfg.LOG_KEEP, Cfg.MAX_MEMBERS = 10, 10000000, 25, 200, 25
        Cfg.MAX_BANK, Cfg.INVITE_SECONDS, Cfg.ONLINE_MSG, Cfg.BASE, Cfg.STEP = 1000000000000, 300, True, 100, 150
        Cfg.DEF_LIM_ADMIN, Cfg.DEF_LIM_MEMBER = -1, 0
        if k == "new":
            Cfg.LEAVE_REFUND = REFUND_PCT[0]
        p = Props()
        p.setProperty("xpSkills", str(Cfg.DEF_SKILLS))
        Cfg.parseSkills(p)
        BR.clear()
        for key, f in (("coins:fn:get", COINS[0]), ("coins:fn:add", COINS[1]), ("coins:fn:take", COINS[2])):
            BR.put(key, f)
        FAIL_ADD.clear()
        FAIL_TAKE.clear()
        UNREAD.clear()
        HOOK[0] = None
        return GS, Cfg, X

    def logline(i, who, act, amount, bank):
        return "%d|%s|%s|%d|%d" % (NOW - (50 - i) * 3600000, who, act, amount, bank)

    def make_guild(k, gid, name, tag, members, xp=0, bank=0, log=(), lim=(-1, 0), nets=None):
        """members = [(n, rank, contrib, coins taken today)]; nets = {n: (deposited, withdrawn)} (both jars have them since 0.1.5)"""
        GS = jc(k, "GuildStore")
        g = jc(k, "Guild")()
        g.id, g.name, g.tag, g.created, g.xp, g.bank = gid, name, tag, NOW - 86400000, xp, bank
        g.limAdmin, g.limMember = lim
        for j, (n, rank, contrib, took) in enumerate(members):
            m = jc(k, "GMember")()
            m.uuid, m.uid, m.name, m.rank, m.joined, m.contrib = str(uid(n)), uid(n), NAMES.get(n, "P%d" % n), rank, NOW - 1000000 + j, contrib
            if took:
                m.wdDay, m.wdUsed = DAY, took
            g.members.put(m.uuid, m)
            GS.BYPLAYER.put(m.uuid, gid)
        for ln in log:
            g.log.add(ln)
        if nets:
            for n, (dep, wd) in nets.items():
                g.net.put(str(uid(n)), JArray(JLong)([dep, wd]))
        GS.GUILDS.put(gid, g)
        GS.BYNAME.put(name.lower(), gid)
        return g

    def net_of(k, g, n):
        v = g.net.get(str(uid(n)))
        return None if v is None else (int(v[0]), int(v[1]))

    def jprops(path):
        p = Props()
        fin = JClass("java.io.FileInputStream")(path)
        try:
            p.load(fin)
        finally:
            fin.close()
        return dict((str(x), str(p.getProperty(x))) for x in p.stringPropertyNames())

    def capture(fn):
        """run fn() with Java's System.out captured (GuildStore.info / warn print there while LOG is null): (result, text)"""
        buf = BAOS()
        old = System.out
        System.setOut(PS(buf, True, "UTF-8"))
        try:
            r = fn()
        finally:
            System.setOut(old)
        return r, str(buf.toString("UTF-8"))

    # ---------------- C. XpTask is byte-identical: the same guild XP on both jars (random walk)
    def xp_walk(k, steps):
        GS, Cfg, X = reset(k, "xp")
        make_guild(k, "g1", "Xp Guild", "XP", [(1, 2, 0, 0), (2, 0, 0, 0)])
        XP.clear()
        XP[str(uid(1))] = {0: 500, 1: 900, 5: 12345}
        XP[str(uid(2))] = {0: 40, 1: 1}
        PKEY.clear()
        BR.put("skill:fn:xp", SKILLFN)
        gains = []
        for st in steps:
            if st[0] == "xp":
                d = XP.setdefault(str(uid(st[1])), {})
                d[st[2]] = d.get(st[2], 0) + st[3]
            else:
                gains.append(int(X.check(uid(st[1]))))
        return gains

    rnd = random.Random(15)
    walk = []
    for _ in range(80):
        who = rnd.choice((1, 2))
        for _j in range(rnd.randint(0, 3)):
            walk.append(("xp", who, rnd.choice((0, 1, 2, 5, 9, 14, 15)), rnd.choice((1, 3, 7, 13, 29, 101, 997, -5, 40000))))
        walk.append(("check", who))
    wo, wn = xp_walk("old", walk), xp_walk("new", walk)
    check(wo == wn and sum(wn) > 0, "C. XpTask: the same guild XP on both jars over an 80-step walk (%d / %d)" % (sum(wo), sum(wn)))
    print("C. XpTask byte-identical and the same guild XP on both jars (%d checks, %d guild XP)" % (len(wn), sum(wn)))

    # ---------------- P. the disband split (GuildStore.payouts) against the Python reference + its rules
    PAYDIR = os.path.join(SCRATCH, "data", "new", "pay")
    os.makedirs(os.path.join(PAYDIR, "guilds"), exist_ok=True)

    def pay(nets, bank, ranks=None):
        GS, Cfg, X = reset("new", "pay", d=PAYDIR)
        n = len(nets)
        ranks = ranks or [2] + [0] * (n - 1)
        mem = [(i + 1, ranks[i], 0, 0) for i in range(n)]
        g = make_guild("new", "g1", "Pay Guild", "", mem, bank=bank, nets=dict((i + 1, nets[i]) for i in range(n)))
        rows = GS.payouts(g, bank)
        got = [(str(r[0].uuid), int(r[1]), int(r[2])) for r in rows]
        check([u for u, _s, _n in got] == [str(uid(i + 1)) for i in range(n)], "P. payouts rows in member (join) order")
        check([x for _u, _s, x in got] == [d - w for d, w in nets], "P. payouts rows carry each net")
        want = ref_pay(nets, bank, ranks, list(range(n)))
        shares = [s_ for _u, s_, _n in got]
        check(shares == want, "P. payouts %s bank %d: %s, want %s" % (nets, bank, shares, want))
        check(sum(shares) == max(0, bank), "P. the shares sum to the bank exactly (%d / %d)" % (sum(shares), bank))
        check(all(x >= 0 for x in shares), "P. no negative share %s" % shares)
        netv = [d - w for d, w in nets]
        if any(x > 0 for x in netv):
            check(all(sh == 0 for sh, x in zip(shares, netv) if x <= 0), "P. a net <= 0 gets nothing while someone is positive %s" % shares)
            exact = [(bank * x) // sum(y for y in netv if y > 0) if x > 0 else 0 for x in netv]
            check(0 <= bank - sum(exact) < max(1, sum(1 for x in netv if x > 0)), "P. remainder below the number of sharers")
        COUNT["P cases"] += 1
        return shares

    check(pay([(600, 0), (400, 0)], 1000) == [600, 400], "P. 60 / 40 of 1,000")
    check(pay([(600, 0), (400, 0)], 2500) == [1500, 1000], "P. 60 / 40 of a bank that grew to 2,500 (interest / rewards shared the same way)")
    check(pay([(100000, 25000), (2000, 5000)], 72000) == [72000, 0], "P. Skyy's example: +75,000 gets the whole 72,000, -3,000 nothing")
    check(pay([(500, 0), (0, 200), (300, 0)], 900) == [563, 0, 337], "P. one negative member: 562.5 / 0 / 337.5 -> remainder 1 to the biggest")
    check(pay([(0, 0), (0, 100), (50, 100)], 10, [2, 0, 0]) == [4, 3, 3], "P. nobody positive: even 3 / 3 / 3 + 1 to the biggest (net 0)")
    check(pay([(0, 0), (0, 0), (0, 0)], 11, [0, 2, 1]) == [3, 5, 3], "P. even split, net tie: the remainder to the higher rank (Leader)")
    check(pay([(1, 0), (1, 0), (1, 0)], 10, [1, 2, 1]) == [3, 4, 3], "P. 3 equal nets, 10 coins: 3 / 3 / 3 + 1 to the Leader (rank tie-break)")
    check(pay([(5, 0), (5, 0)], 7, [0, 0]) == [4, 3], "P. equal rank + net: the remainder to the earlier join")
    check(pay([(10 ** 15, 1), (3, 0), (7, 0)], 10 ** 15) == ref_pay([(10 ** 15, 1), (3, 0), (7, 0)], 10 ** 15, [2, 0, 0], [0, 1, 2]),
          "P. 1e15 coins x 1e15 net (BigInteger, no overflow)")
    check(pay([(100, 0), (50, 0)], 0) == [0, 0], "P. bank 0 -> nothing")
    check(pay([(0, 0)], 777, [2]) == [777], "P. one member gets everything")
    rr = random.Random(150)
    for i in range(400):
        n = rr.randint(1, 12)
        nets = []
        for _j in range(n):
            kind = rr.random()
            if kind < 0.25:
                nets.append((0, 0))
            elif kind < 0.5:
                d = rr.randint(0, 10 ** rr.randint(1, 9))
                nets.append((d, d + rr.randint(1, 10 ** rr.randint(1, 6))))
            else:
                nets.append((rr.randint(1, 10 ** rr.randint(1, 12)), rr.randint(0, 1000)))
        ranks = [2] + [rr.choice((0, 0, 1)) for _j in range(n - 1)]
        pay(nets, rr.choice((0, 1, 7, rr.randint(0, 10 ** 6), rr.randint(0, 10 ** 12), 10 ** 15)), ranks)
    print("P. disband split: %d cases (11 fixed: 60/40, Skyy's 75,000 / -3,000, one negative, nobody positive, rank / join tie-breaks, "
          "1e15; 400 random) = the Python reference, every sum exact" % COUNT["P cases"])

    # ---------------- Q. disbands end to end (real GuildStore, fake SkyyCoins)
    def coins_total(k=None):
        return sum(v for v in PURSE.values() if v is not None)

    def gfile(GS, gid="g1"):
        return os.path.join(str(GS.GDIR.toString()), gid + ".properties")

    def banklog(GS):
        f = os.path.join(str(GS.DIR.toString()), "banklog.log")
        return open(f, encoding="utf8").read().splitlines() if os.path.exists(f) else []

    def q_setup(k, tag, purses, online, members, lim=(-1, -1), bank=0):
        GS, Cfg, X = reset(k, tag)
        PURSE.clear()
        PURSE.update(dict((str(uid(n)), v) for n, v in purses.items()))
        set_online(online)
        g = make_guild(k, "g1", "Pay Guild", "PAY", members, bank=bank, lim=lim)
        GS.saveGuild(g)
        return GS, g

    def move(GS, n, what, amount):
        r = str((GS.deposit if what == "dep" else GS.withdraw)(uid(n), NAMES[n], str(amount)))
        check(r.startswith("+"), "Q. %s %s %s: %s" % (NAMES[n], what, amount, r))
        return r

    # Q1: 4 members (Steve Leader online, Alex Admin online, Bea Member OFFLINE, Cid Member offline with a negative net) + a reward
    MEM4 = [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0)]
    res_q1 = {}
    for k in ("old", "new"):
        GS, g = q_setup(k, "q1", {1: 5000, 2: 5000, 3: 5000, 4: 5000}, [1, 2], MEM4)
        move(GS, 1, "dep", 600)
        move(GS, 2, "dep", 400)
        move(GS, 3, "dep", 1000)
        move(GS, 4, "dep", 100)
        move(GS, 4, "wd", 300)
        g.bank = g.bank + 1200                 # a reward into the bank (from outside the purses)
        before = coins_total() + int(g.bank)
        warn_txt = str(GS.disbandWarning(uid(1)))
        r, out = capture(lambda: str(GS.disband(uid(1), NAMES[1], True)))
        res_q1[k] = (r, warn_txt, dict(PURSE), coins_total() + 0, before)
        if k == "new":
            check(r == "+Pay Guild is disbanded. The guild bank's 3000 coins went back to 3 members by contribution - your share: 900 coins.",
                  "Q1. result text: %r" % r)
            check(warn_txt == "=Disbanding deletes Pay Guild for all 4 members and pays the bank's 3000 coins back to the members by "
                              "contribution (your share: 900). Click Disband again within 10 s.", "Q1. confirm text: %r" % warn_txt)
            want = {1: 5000 - 600 + 900, 2: 5000 - 400 + 600, 3: 5000 - 1000 + 1500, 4: 5000 - 100 + 300 + 0}
            check(all(PURSE[str(uid(n))] == v for n, v in want.items()), "Q1. purses %s, want %s (Bea offline paid 1500, Cid -200 gets 0)"
                  % (dict((n, PURSE[str(uid(n))]) for n in want), want))
            check(coins_total() == before, "Q1. no coin created or lost (%d / %d)" % (coins_total(), before))
            check(GS.GUILDS.get("g1") is None and GS.BYPLAYER.isEmpty(), "Q1. the guild is gone, nobody is listed")
            check(not os.path.exists(gfile(GS)), "Q1. the live guild file moved away")
            arch = glob.glob(os.path.join(str(GS.GDIR.toString()), "deleted", "g1-*.properties"))
            if check(len(arch) == 1, "Q1. one archived guild file"):
                pp = jprops(arch[0])
                check("disbanded" in pp and pp.get("bank") == "0", "Q1. archived: disbanded, bank 0")
                pays = [v.split("|")[1:4] for kk, v in sorted(pp.items(), key=lambda kv: int(kv[0][4:]) if kv[0].startswith("log.") else 0)
                        if kk.startswith("log.") and "|disband-payout|" in v]
                check(pays == [["Steve", "disband-payout", "900"], ["Alex", "disband-payout", "600"], ["Bea", "disband-payout", "1500"]],
                      "Q1. one disband-payout line per share: %s" % pays)
                check(pp.get("net." + str(uid(3))) == "1000|1500" and pp.get("net." + str(uid(4))) == "100|300",
                      "Q1. the archive keeps the totals (payouts count as withdrawn): %s / %s" % (pp.get("net." + str(uid(3))), pp.get("net." + str(uid(4)))))
            check("paid back by contribution: Steve 900 (net 600), Alex 600 (net 400), Bea 1500 (net 1000), Cid 0 (net -200)" in out,
                  "Q1. the server log line lists every share: %r" % out[-300:])
    check(res_q1["new"][:4] == res_q1["old"][:4], "Q1. with the refund at 35%% the disband is 0.1.5's: the same result, confirm, purses "
          "on both jars: 0.1.5 %s / 0.1.6 %s" % (res_q1["old"][:2], res_q1["new"][:2]))
    # Q2: nobody positive -> even split, remainder to the biggest contributor (the Leader, net 0)
    GS, g = q_setup("new", "q2", {1: 0, 2: 0, 3: 0}, [1, 2, 3], [(1, 2, 0, 0), (2, 0, 0, 0), (3, 0, 0, 0)], bank=1000)
    move(GS, 2, "wd", 100)
    move(GS, 3, "wd", 50)
    r = str(GS.disband(uid(1), NAMES[1], True))
    check([PURSE[str(uid(n))] for n in (1, 2, 3)] == [284, 100 + 283, 50 + 283], "Q2. even split 284 / 283 / 283: %s" % [PURSE[str(uid(n))] for n in (1, 2, 3)])
    check(r == "+Pay Guild is disbanded. The guild bank's 850 coins went back to 3 members in equal parts (nobody had put in more than "
               "they took out) - your share: 284 coins.", "Q2. result text: %r" % r)
    # Q3: /guildadmin delete (the actor is not a member) - the same split
    GS, g = q_setup("new", "q3", {1: 1000, 2: 1000}, [1], [(1, 2, 0, 0), (2, 0, 0, 0)])
    move(GS, 1, "dep", 300)
    move(GS, 2, "dep", 100)
    first = str(GS.adminDelete(uid(99), "Admin", "Pay Guild"))
    check(first == "=This deletes Pay Guild (2 members, its bank's 400 coins are paid back to its members by contribution). Type the "
                   "same command again within 10 s to confirm.", "Q3. admin delete confirm: %r" % first)
    r = str(GS.adminDelete(uid(99), "Admin", "Pay Guild"))
    check(r == "+Pay Guild is disbanded. The guild bank's 400 coins went back to 2 members by contribution.", "Q3. admin delete: %r" % r)
    check([PURSE[str(uid(n))] for n in (1, 2)] == [1000, 1000], "Q3. admin delete paid 300 / 100 back")
    # Q4: the last member leaves (net negative: withdrew more than deposited) - the whole bank, 0.1.4's purse and text
    res_q4 = {}
    for k in ("old", "new"):
        GS, g = q_setup(k, "q4", {1: 0}, [1], [(1, 2, 0, 0)], bank=1000)
        move(GS, 1, "wd", 300)
        w = str(GS.leaveWarning(uid(1)))
        r = str(GS.leave(uid(1), NAMES[1], True))
        res_q4[k] = (w, r, PURSE[str(uid(1))], GS.GUILDS.get("g1") is None)
    check(res_q4["new"] == res_q4["old"] and res_q4["new"][2] == 1000 and res_q4["new"][3],
          "Q4. last member leaves (refund 35%%): the whole bank to their purse, texts = 0.1.5's: %s / %s" % (res_q4["old"], res_q4["new"]))
    # Q4b: the last member with a POSITIVE contribution (a refund would apply to a non-last member): still the whole bank, 0.1.5's texts
    res_q4b = {}
    for k in ("old", "new"):
        GS, g = q_setup(k, "q4b", {1: 5000}, [1], [(1, 2, 0, 0)], bank=0)
        move(GS, 1, "dep", 1000)
        g.bank = g.bank + 500
        GS.saveGuild(g)
        w = str(GS.leaveWarning(uid(1)))
        c1 = str(GS.leave(uid(1), NAMES[1], False))
        r = str(GS.leave(uid(1), NAMES[1], False))
        res_q4b[k] = (w, c1, r, PURSE[str(uid(1))], GS.GUILDS.get("g1") is None, [x for x in banklog(GS) if "refund" in x])
    check(res_q4b["new"] == res_q4b["old"] and res_q4b["new"][3] == 5500 and res_q4b["new"][4] and res_q4b["new"][5] == [],
          "Q4b. the last member (net +1,000, bank 1,500): the whole bank, no refund line, texts = 0.1.5's: %s" % (res_q4b["new"][:3],))
    # Q5: the Leader alone positive in a 3-member guild -> the 0.1.4 texts ("to your purse")
    GS, g = q_setup("new", "q5", {1: 1000, 2: 0, 3: 0}, [1, 2], [(1, 2, 0, 0), (2, 0, 0, 0), (3, 0, 0, 0)])
    move(GS, 1, "dep", 500)
    w = str(GS.disbandWarning(uid(1)))
    r = str(GS.disband(uid(1), NAMES[1], True))
    check(w == "=Disbanding deletes Pay Guild for all 3 members and pays the bank's 500 coins to your purse. Click Disband again within 10 s."
          and r == "+Pay Guild is disbanded. The guild bank's 500 coins went to your purse.", "Q5. one payee = 0.1.4's texts: %r / %r" % (w, r))

    # Q6-Q8: refusals - nothing changed / everything taken back / no coin created or lost
    def q_refuse(tag, fail_add=(), fail_take=(), unreadable=()):
        GS, g = q_setup("new", tag, {1: 5000, 2: 5000, 3: 5000}, [1, 2], [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)])
        move(GS, 1, "dep", 600)
        move(GS, 2, "dep", 400)
        move(GS, 3, "dep", 1000)
        g.bank = g.bank + 1000
        GS.saveGuild(g)
        file_before = open(gfile(GS), "rb").read()
        log_before = [str(x) for x in g.log]
        nets_before = dict((n, net_of("new", g, n)) for n in (1, 2, 3))
        bank_before = int(g.bank)
        total_before = coins_total() + bank_before
        for n in unreadable:
            PURSE[str(uid(n))] = None
        FAIL_ADD.update(str(uid(n)) for n in fail_add)
        FAIL_TAKE.update(str(uid(n)) for n in fail_take)
        purses_before = dict(PURSE)
        r, out = capture(lambda: str(GS.disband(uid(1), NAMES[1], True)))
        return GS, g, r, out, file_before, log_before, nets_before, bank_before, total_before, purses_before

    GS, g, r, out, fb, lb, nb, bb, tb, pb = q_refuse("q6", unreadable=(3,))
    check(r == "-Bea's purse cannot be read right now, so the guild bank cannot be paid out and Pay Guild was NOT disbanded (nothing "
               "changed). Try again.", "Q6. unreadable purse: %r" % r)
    check(open(gfile(GS), "rb").read() == fb and GS.GUILDS.get("g1") is not None and dict(PURSE) == pb,
          "Q6. pre-check refusal: the guild file byte-identical, the guild loaded, every purse unchanged")
    for tag, fail, paid_first in (("q7a", 1, []), ("q7b", 2, [1]), ("q7c", 3, [1, 2])):
        GS, g, r, out, fb, lb, nb, bb, tb, pb = q_refuse(tag, fail_add=(fail,))
        check(r == "-SkyyCoins could not pay %s's share of the guild bank, so Pay Guild was NOT disbanded - every coin paid so far went "
                   "back to the guild bank. Try again." % NAMES[fail], "Q7 %s. payout %s fails: %r" % (tag, NAMES[fail], r))
        check(dict(PURSE) == pb, "Q7 %s. every share paid before (%s) was taken back: purses unchanged" % (tag, [NAMES[n] for n in paid_first]))
        pp = jprops(gfile(GS))
        check("disbanded" not in pp and pp.get("bank") == str(bb) and int(g.bank) == bb, "Q7 %s. the live file is written again: not "
              "disbanded, bank %s (want %d)" % (tag, pp.get("bank"), bb))
        check([str(x) for x in g.log] == lb and dict((n, net_of("new", g, n)) for n in (1, 2, 3)) == nb,
              "Q7 %s. the log and the totals are unchanged" % tag)
        check(GS.GUILDS.get("g1") is not None and str(GS.BYPLAYER.get(str(uid(1)))) == "g1", "Q7 %s. the guild stays loaded" % tag)
        check(coins_total() + int(g.bank) == tb, "Q7 %s. no coin created or lost" % tag)
        COUNT["Q rollback"] += 1
    FAIL_ADD.clear()
    r2 = str(GS.disband(uid(1), NAMES[1], True))
    check(r2.startswith("+Pay Guild is disbanded.") and coins_total() == tb, "Q7. the retry after the failure disbands: %r" % r2)
    # Q8: Bea's payout fails and Steve's share cannot be taken back -> it stays with Steve, logged, counted as withdrawn
    GS, g, r, out, fb, lb, nb, bb, tb, pb = q_refuse("q8", fail_add=(3,), fail_take=(1,))
    sh1 = ref_pay([(600, 0), (400, 0), (1000, 0)], 3000, [2, 1, 0], [0, 1, 2])[0]
    check(r == "-SkyyCoins could not pay Bea's share, so Pay Guild was NOT disbanded. %d coins already paid could not be taken back - see "
               "the bank log. Try again." % sh1, "Q8. text: %r" % r)
    check(int(g.bank) == bb - sh1 and PURSE[str(uid(1))] == pb[str(uid(1))] + sh1 and PURSE[str(uid(2))] == pb[str(uid(2))],
          "Q8. bank %d (want %d), Steve keeps %d, Alex's share taken back" % (int(g.bank), bb - sh1, sh1))
    check(str(g.log.get(g.log.size() - 1)).split("|")[1:4] == ["Steve", "disband-payout", str(sh1)], "Q8. Steve's kept share is a logged disband-payout")
    check(net_of("new", g, 1) == (600, sh1), "Q8. ... and counted as Steve's withdrawal %s" % (net_of("new", g, 1),))
    check(coins_total() + int(g.bank) == tb, "Q8. no coin created or lost (%d / %d)" % (coins_total() + int(g.bank), tb))
    check(jprops(gfile(GS)).get("bank") == str(bb - sh1) and "disbanded" not in jprops(gfile(GS)), "Q8. the live file has the lowered bank")
    print("Q. disbands end to end: 60/40-style split with an offline member (3000 -> 900 / 600 / 1500 / 0), nobody positive 284 / 283 / "
          "283, admin delete, last member (= 0.1.4), one payee (= 0.1.4 texts); refused: unreadable purse (nothing changed), %d "
          "mid-way failures fully rolled back, a share that could not be taken back stays logged; coins conserved every time" % COUNT["Q rollback"])

    # ---------------- R. the REAL SkyyCoins 0.1.5: an offline member is paid into their ACTIVE profile's purse
    CS, CF = JClass("com.skyy.coins.CoinStore", loader=L["coins"]), JClass("com.skyy.coins.CoinFn", loader=L["coins"])

    def real_coins(tag):
        GS, Cfg, X = reset("new", tag)
        bal = os.path.join(SCRATCH, "coins", tag)
        shutil.rmtree(bal, ignore_errors=True)
        os.makedirs(bal)
        CS.DIR = Paths.get(bal)
        CS.BAL.clear()
        CS.LOADED.clear()
        for key in ("get", "add", "take"):
            BR.put("coins:fn:" + key, CF(key))
        PKEY.clear()
        PKEY[str(uid(3))] = str(uid(3)) + "-p2"           # Bea is offline; her active profile is profile 2
        BR.put("profile:fn:key", PROFFN)
        return GS, bal

    def bal_file(bal, key):
        f = os.path.join(bal, key + ".properties")
        return int(jprops(f)["balance"]) if os.path.exists(f) else None

    def write_bal(bal, key, v):
        open(os.path.join(bal, key + ".properties"), "w", encoding="ascii").write("#SkyyCoins\nbalance=%s\n" % v)

    GS, bal = real_coins("r1")
    for key, v in ((str(uid(1)), 1000), (str(uid(2)), 1000), (str(uid(3)), 1000), (str(uid(3)) + "-p2", 50)):
        write_bal(bal, key, v)
    set_online([1, 2])
    g = make_guild("new", "g1", "Real Coins", "", [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    GS.saveGuild(g)
    for n, amt in ((1, 300), (2, 200), (3, 50)):
        r = str(GS.deposit(uid(n), NAMES[n], str(amt)))
        check(r.startswith("+Deposited"), "R. real SkyyCoins deposit %s %d: %r" % (NAMES[n], amt, r))
    check(bal_file(bal, str(uid(3)) + "-p2") == 0 and bal_file(bal, str(uid(3))) == 1000, "R. Bea's deposit came from her active profile 2")
    g.bank = g.bank + 550
    r = str(GS.disband(uid(1), NAMES[1], True))
    got = dict((nm, bal_file(bal, key)) for nm, key in (("Steve", str(uid(1))), ("Alex", str(uid(2))), ("Bea p1", str(uid(3))),
                                                       ("Bea p2", str(uid(3)) + "-p2")))
    check(got == {"Steve": 1000 - 300 + 600, "Alex": 1000 - 200 + 400, "Bea p1": 1000, "Bea p2": 0 + 100},
          "R. real SkyyCoins: offline Bea paid 100 into balances/<uuid>-p2.properties (profile 1 untouched): %s (%r)" % (got, r))
    GS, bal = real_coins("r2")
    for key, v in ((str(uid(1)), 1000), (str(uid(2)), 1000), (str(uid(3)) + "-p2", 1000)):
        write_bal(bal, key, v)
    g = make_guild("new", "g1", "Real Coins", "", [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    for n, amt in ((1, 300), (2, 200), (3, 50)):
        GS.deposit(uid(n), NAMES[n], str(amt))
    GS.saveGuild(g)
    open(os.path.join(bal, str(uid(3)) + "-p2.properties"), "w", encoding="ascii").write("balance=not a number\n")
    CS.BAL.clear()
    CS.LOADED.clear()
    snap = dict((f, open(os.path.join(bal, f), "rb").read()) for f in os.listdir(bal))
    gsnap = open(gfile(GS), "rb").read()
    r = str(GS.disband(uid(1), NAMES[1], True))
    check(r.startswith("-Bea's purse cannot be read right now") and GS.GUILDS.get("g1") is not None
          and dict((f, open(os.path.join(bal, f), "rb").read()) for f in os.listdir(bal)) == snap and open(gfile(GS), "rb").read() == gsnap,
          "R. real SkyyCoins, Bea's balance file unreadable: refused, every balance file and the guild file byte-identical (%r)" % r)
    # R3 (0.1.6): a kicked OFFLINE member's refund lands in their ACTIVE profile's purse (p2) through the real SkyyCoins
    GS, bal = real_coins("r3")
    for key, v in ((str(uid(1)), 1000), (str(uid(3)), 1000), (str(uid(3)) + "-p2", 2000)):
        write_bal(bal, key, v)
    set_online([1, 2])                                   # Bea (3) is offline
    g = make_guild("new", "g1", "Real Coins", "", [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    GS.saveGuild(g)
    check(str(GS.deposit(uid(3), NAMES[3], "1000")).startswith("+Deposited") and bal_file(bal, str(uid(3)) + "-p2") == 1000,
          "R3. Bea's 1,000 deposit came from her active profile 2")
    r, out = capture(lambda: str(GS.kick(uid(1), NAMES[1], "Bea")))
    got = (bal_file(bal, str(uid(3))), bal_file(bal, str(uid(3)) + "-p2"))
    check(r == "+Removed Bea from the guild. Bea got back 350 coins (35% of their contribution of 1,000); the rest stays in the bank."
          and got == (1000, 1350) and int(g.bank) == 650 and g.member(str(uid(3))) is None and net_of("new", g, 3) == (1000, 1000)
          and (int(g.net.get("~guild")[0]), int(g.net.get("~guild")[1])) == (650, 0),
          "R3. real SkyyCoins: offline Bea kicked, 350 into balances/<uuid>-p2.properties (profile 1 untouched): %s %r" % (got, r))
    check(jprops(gfile(GS)).get("bank") == "650" and jprops(gfile(GS)).get("net." + str(uid(3))) == "1000|1000"
          and jprops(gfile(GS)).get("net.~guild") == "650|0",
          "R3. the guild file: bank 650, Bea's totals 1000|1000 (net 0 for a rejoin), the rest 650 in net.~guild")
    # R4: Bea's balance file unreadable -> kicked anyway, the refund skipped (stays in the bank), every balance file byte-identical
    GS, bal = real_coins("r4")
    for key, v in ((str(uid(1)), 1000), (str(uid(3)) + "-p2", 2000)):
        write_bal(bal, key, v)
    set_online([1, 2])
    g = make_guild("new", "g1", "Real Coins", "", [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    GS.deposit(uid(3), NAMES[3], "1000")
    GS.saveGuild(g)
    open(os.path.join(bal, str(uid(3)) + "-p2.properties"), "w", encoding="ascii").write("balance=not a number\n")
    CS.BAL.clear()
    CS.LOADED.clear()
    snap = dict((f, open(os.path.join(bal, f), "rb").read()) for f in os.listdir(bal))
    r, out = capture(lambda: str(GS.kick(uid(1), NAMES[1], "Bea")))
    check(r == "+Removed Bea from the guild. Their refund (350 coins) could not be paid (the purse cannot be read right now), so it stays "
               "in the guild bank." and g.member(str(uid(3))) is None and int(g.bank) == 1000 and net_of("new", g, 3) == (1000, 1000)
          and (int(g.net.get("~guild")[0]), int(g.net.get("~guild")[1])) == (1000, 0)
          and dict((f, open(os.path.join(bal, f), "rb").read()) for f in os.listdir(bal)) == snap,
          "R4. real SkyyCoins, Bea's balance unreadable: kicked, refund skipped, bank 1000, her 1,000 to the guild, balance files "
          "unchanged: %r" % r)
    check("WARN kick refund of 350 coins for Bea (%s) from g1 'Real Coins' skipped: the purse cannot be read right now" % uid(3) in out
          and any(ln.endswith(") player=Bea kick-refund-skipped 350 bank=1000") for ln in banklog(GS))
          and str(g.log.get(g.log.size() - 1)).split("|")[1:] == ["Bea", "kick-refund-skipped", "350", "1000"],
          "R4. a WARN + a kick-refund-skipped line in banklog.log and the guild log: %r" % out[-300:])
    print("R. real SkyyCoins 0.1.5: disband - offline member paid into the active profile (p2) file, profile 1 untouched, an unreadable "
          "balance file refuses with every file unchanged; 0.1.6 kick refund of an OFFLINE member into p2, an unreadable balance file = "
          "kicked, refund skipped, files unchanged")

    # ---------------- S. running totals + the one-time seed
    GS, g = q_setup("new", "s1", {1: 5000, 2: 5000}, [1, 2], [(1, 2, 0, 0), (2, 0, 0, 0)])
    move(GS, 1, "dep", 1000)
    move(GS, 2, "dep", 300)
    move(GS, 2, "wd", 500)
    move(GS, 1, "wd", 200)
    check(net_of("new", g, 1) == (1000, 200) and net_of("new", g, 2) == (300, 500), "S1. deposit / withdraw keep the running totals")
    FAIL_ADD.add(str(uid(2)))
    r = str(GS.withdraw(uid(2), NAMES[2], "100"))
    check(r.startswith("-SkyyCoins could not put the coins in your purse") and net_of("new", g, 2) == (300, 500),
          "S1. a withdraw SkyyCoins refuses takes its total back: %r %s" % (r, net_of("new", g, 2)))
    FAIL_ADD.clear()
    pp = jprops(gfile(GS))
    check(pp.get("net." + str(uid(1))) == "1000|200" and pp.get("net." + str(uid(2))) == "300|500", "S1. the guild file holds net.<uuid>")
    check(re.fullmatch(r"\d+\|new\|0\|0", pp.get("netSeed", "")) is None, "S1. (a test guild made by the harness has no netSeed)")
    ai = [str(x) for x in GS.adminInfo("g1")]
    check(ai[1].endswith(", bank %d coins (contributions not seeded yet)" % int(g.bank)), "V5. /guildadmin info, no netSeed: %r" % ai[1])
    COUNT["V5"] += 1
    # S2: a scratch COPY of the live data (GodSquad, already seeded by 0.1.5 on 2026-10-01) - the live folder is only read
    DATE_LINE = re.compile(rb"^#\w{3} \w{3} \d\d \d\d:\d\d:\d\d \w+ \d{4}\r?$", re.M)    # Properties.store's date comment

    def snapdir(d):
        out = {}
        for root, _dirs, files in os.walk(d):
            for fn in files:
                pth = os.path.join(root, fn)
                out[os.path.relpath(pth, d).replace("\\", "/")] = DATE_LINE.sub(b"#<date>", open(pth, "rb").read())
        return out

    CFG016 = [ast.literal_eval(n.value) for n in ast.parse(open(SCRIPT, encoding="utf8").read()).body
              if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "CFG_LINES_016" for t in n.targets)]
    check(len(CFG016) == 1 and CFG016[0][-1] == "leaveRefundPercent=35", "S2. the build script's CFG_LINES_016: %s" % CFG016)
    BLOCK016 = ("\n".join(CFG016[0] if CFG016 else []) + "\n").encode("utf8")
    live_ok = os.path.isdir(LIVE) and os.path.isfile(os.path.join(LIVE, "guilds", "g1.properties"))
    if check(live_ok, "S2. the live Skyy_SkyyGuilds folder is readable at %s" % LIVE):
        cp = os.path.join(SCRATCH, "live-copy")
        shutil.rmtree(cp, ignore_errors=True)
        shutil.copytree(LIVE, cp)
        before = snapdir(cp)
        livep = jprops(os.path.join(cp, "guilds", "g1.properties"))
        bank_lines = [ln for ln in open(os.path.join(cp, "banklog.log"), encoding="utf8").read().splitlines() if " guild=g1 " in ln]
        want = collections.defaultdict(lambda: [0, 0])
        for ln in bank_lines:
            w = ln.split(" player=")[1].split()
            if w[-3] == "deposit":
                want[w[0].lower()][0] += int(w[-2])
            elif w[-3] in ("withdraw", "disband-payout", "leave-refund", "kick-refund"):
                want[w[0].lower()][1] += int(w[-2])
        names = dict((kk[7:], v.split("|")[3]) for kk, v in livep.items() if kk.startswith("member."))
        wantd = dict((names[u_], tuple(want[names[u_].lower()])) for u_ in names)
        # first 0.1.6 start = what setup() does: GCfg.load(), then GuildStore.loadAll()
        GS, Cfg, X = reset("new", "live", d=cp)
        Cfg.LEAVE_REFUND = 0
        _, out1 = capture(lambda: (Cfg.load(), GS.loadAll()))
        after1 = snapdir(cp)
        cb = before.get("config.properties", b"")
        has016 = b"\nleaveRefundPercent" in b"\n" + cb
        want_cfg = cb if has016 else cb + (b"" if cb.endswith(b"\n") or not cb else b"\n") + BLOCK016
        check(after1.get("config.properties") == want_cfg and int(Cfg.LEAVE_REFUND) == 35,
              "S2. first 0.1.6 start on the live copy: config.properties gains the 0.1.6 block once (%s), leaveRefundPercent 35 running"
              % ("already there" if has016 else "appended"))
        check(out1.count("added the 0.1.6 key leaveRefundPercent") == (0 if has016 else 1), "S2. one INFO line for the appended key")
        check(sorted(after1) == sorted(before) and all(after1[kk] == before[kk] for kk in before if kk != "config.properties"),
              "S2. every other file of the copy byte-identical after the first start (meta / players but their store() date line): %s"
              % [kk for kk in before if kk != "config.properties" and after1.get(kk) != before[kk]])
        g = GS.GUILDS.get("g1")
        got = dict((names[u_], (int(g.net.get(u_)[0]), int(g.net.get(u_)[1])) if g.net.get(u_) is not None else (0, 0)) for u_ in names)
        check("seeded once" not in out1 and str(g.netSeed) == livep.get("netSeed") and got == wantd,
              "S2. already seeded by 0.1.5: no seed, netSeed kept, the totals = the bank log: %s, want %s" % (got, wantd))
        check(sum(a - b for a, b in got.values()) == int(g.bank), "S2. the members' nets add up to the bank (%d)" % int(g.bank))
        # start twice: nothing changes (no churn)
        GS, Cfg, X = reset("new", "live", d=cp)
        _, out2 = capture(lambda: (Cfg.load(), GS.loadAll()))
        after2 = snapdir(cp)
        check(after2 == after1 and "added the 0.1.6 key" not in out2 and "seeded once" not in out2,
              "S2. start twice = no churn (every file byte-identical but the store() date lines, no append, no seed): %s"
              % [kk for kk in after1 if after2.get(kk) != after1[kk]])
        print("S2. live GodSquad copy (0.1.6 start twice): %s, netSeed %s, config %s" % (got, livep.get("netSeed"),
                                                                                       "had the key" if has016 else "+ the 0.1.6 block once"))
        # S2b: the same data with net.* / netSeed stripped (what 0.1.4 leaves behind) seeds the same on 0.1.5 and 0.1.6
        seeded = {}
        for k in ("old", "new"):
            cpk = os.path.join(SCRATCH, "live-strip-" + k)
            shutil.rmtree(cpk, ignore_errors=True)
            shutil.copytree(LIVE, cpk)
            gp = os.path.join(cpk, "guilds", "g1.properties")
            txt = open(gp, "rb").read().decode("latin-1")
            open(gp, "wb").write("".join(l for l in txt.splitlines(True) if not l.startswith(("net.", "netSeed="))).encode("latin-1"))
            GSk, Cfgk, Xk = reset(k, "strip", d=cpk)
            _, o = capture(lambda: GSk.loadAll())
            gk = GSk.GUILDS.get("g1")
            seeded[k] = (dict((names[u_], (int(gk.net.get(u_)[0]), int(gk.net.get(u_)[1])) if gk.net.get(u_) is not None else (0, 0)) for u_ in names),
                         str(gk.netSeed).split("|")[1:], o.count("seeded once from its history"))
        check(seeded["old"] == seeded["new"] and seeded["new"][0] == wantd and seeded["new"][1][0] == "complete" and seeded["new"][2] == 1,
              "S2b. stripped (0.1.4) copy: 0.1.5 and 0.1.6 seed the same, complete: %s / %s" % (seeded["old"], seeded["new"]))
        # later moves keep counting; a restart keeps them; then a 0.1.6 leave refund on the copy
        PURSE.clear()
        wes = [u_ for u_ in names if names[u_] == "WesleyPlayz"]
        sky = [u_ for u_ in names if names[u_] == "SkyLordPlayz"]
        GS, Cfg, X = reset("new", "live", d=cp)
        capture(lambda: GS.loadAll())
        g = GS.GUILDS.get("g1")
        if check(len(wes) == 1 and len(sky) == 1, "S2. the live copy has SkyLordPlayz and WesleyPlayz"):
            UW, US = UUID.fromString(wes[0]), UUID.fromString(sky[0])
            PURSE[wes[0]], PURSE[sky[0]] = 10000, 10000
            check(str(GS.deposit(UW, "WesleyPlayz", "500")).startswith("+"), "S2. Wesley deposits 500 on the copy")
            GS, Cfg, X = reset("new", "live", d=cp)
            _, out3 = capture(lambda: GS.loadAll())
            g = GS.GUILDS.get("g1")
            w0 = got["WesleyPlayz"]
            check((int(g.net.get(wes[0])[0]), int(g.net.get(wes[0])[1])) == (w0[0] + 500, w0[1]) and "seeded once" not in out3,
                  "S2. after a restart Wesley's later deposit is kept, no re-seed")
            bank0 = int(g.bank)
            r = str(GS.leave(UW, "WesleyPlayz", True))
            wnet = w0[0] + 500 - w0[1]
            ref = wnet * 35 // 100
            check(r == "+You left GodSquad. You got back %s coins to your purse (35%% of your contribution of %s); the rest stays in the bank."
                  % (num(ref), num(wnet)) and PURSE[wes[0]] == 10000 - 500 + ref and int(g.bank) == bank0 - ref,
                  "S2. Wesley (Admin) leaves the copy with 35%% of his net back: %r" % r)
            GS, Cfg, X = reset("new", "live", d=cp)
            capture(lambda: GS.loadAll())
            g = GS.GUILDS.get("g1")
            nets_all = [(int(v[0]), int(v[1])) for v in g.net.values()]
            check(g.member(wes[0]) is None and (int(g.net.get(wes[0])[0]), int(g.net.get(wes[0])[1])) == (w0[0] + 500, w0[0] + 500)
                  and (int(g.net.get("~guild")[0]), int(g.net.get("~guild")[1])) == (wnet - ref, 0)
                  and sum(a - b for a, b in nets_all) == int(g.bank), "S2. after a restart: Wesley's net 0 (the refund + the rest to "
                  "~guild), every player's net adds up to the bank (%d)" % int(g.bank))
            # S3 rollback: 0.1.5 loads the 0.1.6 file (a leave-refund line in its log, netSeed present): no re-seed, the same totals
            GSo, Cfgo, Xo = reset("old", "live", d=cp)
            _, outo = capture(lambda: GSo.loadAll())
            go = GSo.GUILDS.get("g1")
            check(go is not None and int(go.bank) == int(g.bank) and go.members.size() == g.members.size() and "seeded once" not in outo
                  and dict((str(kk), (int(go.net.get(kk)[0]), int(go.net.get(kk)[1]))) for kk in go.net.keySet())
                  == dict((str(kk), (int(g.net.get(kk)[0]), int(g.net.get(kk)[1]))) for kk in g.net.keySet())
                  and go.net.get("~guild") is not None, "S3. 0.1.5 loads the 0.1.6 file (rollback safe): same bank, members and totals "
                  "(net.~guild too), no re-seed")
            rl = [str(x) for x in go.log if "|leave-refund|" in str(x)]
            check(len(rl) == 1 and str(GSo.logText(rl[0])).endswith("WesleyPlayz leave-refund %d   (bank %s)" % (ref, num(int(g.bank)))),
                  "S3. 0.1.5 shows the refund line raw in its log view: %r" % (str(GSo.logText(rl[0])) if rl else None))
            check(len(rl) == 1 and str(GS.logText(rl[0])).endswith("WesleyPlayz got back %s coins (left the guild)   (bank %s)" % (num(ref), num(int(g.bank)))),
                  "S3. 0.1.6 names it: %r" % (str(GS.logText(rl[0])) if rl else None))
            GSo.saveGuild(go)
            GS, Cfg, X = reset("new", "live", d=cp)
            capture(lambda: GS.loadAll())
            g = GS.GUILDS.get("g1")
            check(sum(int(v[0]) - int(v[1]) for v in g.net.values()) == int(g.bank) and g.net.get(wes[0]) is not None
                  and g.net.get("~guild") is not None and "net.~guild" in jprops(gfile(GS)),
                  "S3. 0.1.5's save keeps net.* (Wesley's and net.~guild too): 0.1.6 reads the same totals back")
            # S4: a trimmed log + no banklog.log: the running totals (file) still count every move
            Cfg.LOG_KEEP = 3
            for amt in (11, 22, 33, 44):
                GS.deposit(US, "SkyLordPlayz", str(amt))
            os.remove(os.path.join(cp, "banklog.log"))
            sky_before = (int(g.net.get(sky[0])[0]), int(g.net.get(sky[0])[1]))
            GS, Cfg, X = reset("new", "live", d=cp)
            Cfg.LOG_KEEP = 3
            _, out5 = capture(lambda: GS.loadAll())
            g = GS.GUILDS.get("g1")
            check(g.log.size() == 3 and (int(g.net.get(sky[0])[0]), int(g.net.get(sky[0])[1])) == sky_before and "seeded once" not in out5,
                  "S4. a 3-line log and no banklog.log: SkyLordPlayz's totals still count every move %s" % (sky_before,))
            # the GodSquad copy (now SkyLordPlayz alone) disbands: the last member gets the whole bank (0.1.5)
            before_p = PURSE[sky[0]]
            bank_now = int(g.bank)
            r = str(GS.leave(US, "SkyLordPlayz", True))
            check(PURSE[sky[0]] == before_p + bank_now and r == "+GodSquad is disbanded. The guild bank's %d coins went to your purse." % bank_now,
                  "S4. the copy's last member leaves: the whole bank (%d) to their purse, 0.1.5's text: %r" % (bank_now, r))
    # S5: a partial history (bank larger than the moves found) + a move by a player who left
    d = os.path.join(SCRATCH, "data", "new", "s5")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "guilds"))
    open(os.path.join(d, "guilds", "g3.properties"), "w", encoding="utf8").write(
        "id=g3\nname=Partial\ntag=\ncreated=1\nxp=0\nbank=5000\nformat=2\nlimitAdmin=-1\nlimitMember=0\n"
        "member.%s=2|1|0|Steve\nmember.%s=0|2|0|Alex\n" % (uid(1), uid(2))
        + "log.0=%d|Steve|deposit|1000|1000\nlog.1=%d|Ghost|deposit|500|1500\nlog.2=%d|alex|deposit|1000|2500\nlog.3=%d|Steve|limit-member|0|2500\n"
        % (NOW - 4000, NOW - 3000, NOW - 2000, NOW - 1000))
    GS, Cfg, X = reset("new", "s5", d=d)
    _, out = capture(lambda: GS.loadAll())
    g = GS.GUILDS.get("g3")
    check(re.fullmatch(r"\d+\|partial\|3\|1", str(g.netSeed)) is not None and net_of("new", g, 1) == (1000, 0) and net_of("new", g, 2) == (1000, 0)
          and "PARTIAL" in out and "1 move(s) by players no longer in the guild" in out,
          "S5. partial history: netSeed %r, Steve %s, Alex (any case) %s; %r" % (str(g.netSeed), net_of("new", g, 1), net_of("new", g, 2), out[-300:]))
    ai = [str(x) for x in GS.adminInfo("g3")]
    check(re.search(r", bank 5000 coins \(contributions seeded \d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?Z from 3 bank move\(s\) of its history: PARTIAL \(moves were missing; "
                    r"only the moves found count\), 1 move\(s\) by players no longer in the guild \(or renamed since\) credited to nobody\)$",
                    ai[1]) is not None, "V5. /guildadmin info shows the partial seed + the unmatched moves: %r" % ai[1])
    COUNT["V5"] += 1
    # S6: a guild created by 0.1.5 is never seeded
    GS, Cfg, X = reset("new", "s6")
    GS.create(uid(5), NAMES[5], "Fresh Guild")
    gid = str(GS.BYPLAYER.get(str(uid(5))))
    check(re.fullmatch(r"\d+\|new\|0\|0", str(GS.GUILDS.get(gid).netSeed)) is not None, "S6. a new guild starts with netSeed ...|new|0|0")
    ai = [str(x) for x in GS.adminInfo(gid)]
    check(re.search(r", bank 0 coins \(contributions counted from every move since the guild was made \d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?Z\)$", ai[1]) is not None,
          "V5. /guildadmin info, a guild made by 0.1.5: %r" % ai[1])
    COUNT["V5"] += 1
    dd = str(GS.DIR.toString())
    GS, Cfg, X = reset("new", "s6", d=dd)
    _, out = capture(lambda: GS.loadAll())
    check("seeded once" not in out and GS.GUILDS.get(gid) is not None, "S6. ... and is not seeded at the next start")
    print("S. running totals: deposit / withdraw / refused withdraw; the live copy started twice on 0.1.6 (no churn, config + the key "
          "once), a stripped copy seeds the same on both jars, later moves + a refund kept, 0.1.5 reads the 0.1.6 file, a trimmed log + "
          "no banklog.log keep the totals, partial history reported, new guilds unseeded")

    # ---------------- V. the 0.1.5 review hardening (findings 1, 2, 4; 5 is checked in S)
    NOTE_LINE = re.compile(r"^\S+ guild=g1 \(Pay Guild\) DISBAND-PAYOUT-(START|PAID|DONE|CANCELLED)\b")

    def notes(lines):
        return [ln for ln in lines if NOTE_LINE.match(ln)]

    def plan_text(shares):
        return ", ".join("%s %s %d" % (NAMES[n], uid(n), sh) for n, sh in shares)

    # V1 (finding 1): the payout plan is on record BEFORE the first coin moves, each share is marked PAID as it lands, then DONE
    GS, g = q_setup("new", "v1", {1: 5000, 2: 5000, 3: 5000, 4: 5000}, [1, 2], MEM4)
    move(GS, 1, "dep", 600)
    move(GS, 2, "dep", 400)
    move(GS, 3, "dep", 1000)
    move(GS, 4, "dep", 100)
    move(GS, 4, "wd", 300)
    g.bank = g.bank + 1200
    before = coins_total() + int(g.bank)
    SNAP = []
    HOOK[0] = lambda u, n: SNAP.append((u, n, banklog(GS), jprops(gfile(GS))))
    r, out = capture(lambda: str(GS.disband(uid(1), NAMES[1], True)))
    HOOK[0] = None
    plan = plan_text([(1, 900), (2, 600), (3, 1500)])
    start = "DISBAND-PAYOUT-START by Steve: bank 3000 coins to 3 member(s) in this order: %s. The guild file already says disbanded" % plan
    check(r.startswith("+Pay Guild is disbanded.") and coins_total() == before, "V1. the disband works, coins conserved: %r" % r)
    if check(len(SNAP) == 3, "V1. 3 payouts (Steve, Alex, Bea; Cid -200 gets none): %d" % len(SNAP)):
        u0, n0, bl0, gp0 = SNAP[0]
        nt0 = notes(bl0)
        check(len(nt0) == 1 and start in nt0[0], "V1. at the FIRST payout banklog.log already holds the plan (every name, uuid, share): %s" % nt0)
        check("disbanded" in gp0 and gp0.get("bank") == "0", "V1. ... while the guild file says disbanded with bank 0")
        u1, n1, bl1, gp1 = SNAP[1]
        nt1 = notes(bl1)
        check(len(nt1) == 2 and start in nt1[0] and nt1[1].split(") ", 1)[1] == "DISBAND-PAYOUT-PAID 1/3: Steve %s 900 coins." % uid(1),
              "V1. a crash at the 2nd payout (the review's snapshot) leaves the plan + Steve's PAID line, so an admin knows Alex 600 and "
              "Bea 1500 are missing: %s" % nt1)
        check([NOTE_LINE.match(x).group(1) for x in nt1] == ["START", "PAID"] and not any(" disband-payout " in x for x in bl1),
              "V1. ... and no payout move / DONE line yet")
    bl = banklog(GS)
    nt = [x.split(") ", 1)[1] for x in notes(bl)]
    check(len(nt) == 5 and nt[0].startswith(start) and nt[1:] == ["DISBAND-PAYOUT-PAID 1/3: Steve %s 900 coins." % uid(1),
                                                                 "DISBAND-PAYOUT-PAID 2/3: Alex %s 600 coins." % uid(2),
                                                                 "DISBAND-PAYOUT-PAID 3/3: Bea %s 1500 coins." % uid(3),
                                                                 "DISBAND-PAYOUT-DONE: all 3 share(s) paid, 3000 coins; the guild is disbanded."],
          "V1. banklog.log: START, PAID 1/3 .. 3/3, DONE: %s" % nt)
    pays = [x for x in bl if " disband-payout " in x]
    check(len(pays) == 3 and bl.index(pays[0]) > bl.index(notes(bl)[3]) and bl.index(pays[-1]) < bl.index(notes(bl)[4]),
          "V1. the 3 disband-payout moves come after the PAID lines and before DONE")
    parsed = [(ln, GS.parseBankLine(ln, "g1")) for ln in bl]
    check(all(p_ is None for ln, p_ in parsed if NOTE_LINE.match(ln)) and all(p_ is not None for ln, p_ in parsed if not NOTE_LINE.match(ln)),
          "V1. parseBankLine (backfill + seed) skips every DISBAND-PAYOUT note and reads every move (%d notes, %d moves)"
          % (sum(1 for ln, p_ in parsed if NOTE_LINE.match(ln)), sum(1 for ln, p_ in parsed if not NOTE_LINE.match(ln))))
    hm = JClass("java.util.HashMap")()
    sumd = [int(GS.seedLine(hm, str(p_))) for ln, p_ in parsed if p_ is not None]
    check(len(sumd) == 8 and sum(sumd) == 2100 - 300 - 3000, "V1. the seed reads only the 8 moves (4 deposits, 1 withdrawal, 3 payouts = "
          "-1,200: the harness's 1,200 reward is not a logged move), the notes add nothing: %s" % sumd)
    lead = ("disband of g1 'Pay Guild' by Steve: the guild file now says disbanded with bank 0; paying the bank's 3000 coins to 3 member(s) "
            "in this order: %s." % plan)
    check(lead in out and out.index(lead) < out.index("Pay Guild (g1) disbanded by Steve"),
          "V1. the server log names every share before the payouts, ahead of the 'disbanded by' line: %r" % out[:400])
    COUNT["V"] += 1
    # V1b: nothing to pay (bank 0) -> no record at all
    GS, g = q_setup("new", "v1b", {1: 0, 2: 0}, [1, 2], [(1, 2, 0, 0), (2, 0, 0, 0)])
    r, out = capture(lambda: str(GS.disband(uid(1), NAMES[1], True)))
    check(r == "+Pay Guild is disbanded." and notes(banklog(GS)) == [] and "paying the bank" not in out, "V1b. bank 0: no payout record: %r" % r)
    # V2 (findings 1 + 2): Alex's payout fails -> Steve's share taken back, the live file written on the first try, CANCELLED
    GS, g, r, out, fb, lb, nb, bb, tb, pb = q_refuse("v2", fail_add=(2,))
    nt = [x.split(") ", 1)[1] for x in notes(banklog(GS))]
    sh = ref_pay([(600, 0), (400, 0), (1000, 0)], 3000, [2, 1, 0], [0, 1, 2])
    check(len(nt) == 3 and nt[0].startswith("DISBAND-PAYOUT-START by Steve: bank 3000 coins to 3 member(s) in this order: %s."
                                            % plan_text([(1, sh[0]), (2, sh[1]), (3, sh[2])]))
          and nt[1] == "DISBAND-PAYOUT-PAID 1/3: Steve %s %d coins." % (uid(1), sh[0])
          and nt[2] == "DISBAND-PAYOUT-CANCELLED: SkyyCoins could not pay Alex's share, so every share paid before was taken back; the guild "
                       "is NOT disbanded and keeps 3000 coins.", "V2. banklog.log: START, PAID 1/3, CANCELLED: %s" % nt)
    check(out.count("could not save guild g1") == 0 and "DISBAND ROLLBACK NOT ON DISK" not in out and not g.dirty,
          "V2. the rollback save worked on the first try (no WARN, not dirty)")
    check(dict(PURSE) == pb and coins_total() + int(g.bank) == tb, "V2. coins conserved")
    # V2b: Bea fails and Steve's share cannot be taken back -> CANCELLED names the kept coins
    GS, g, r, out, fb, lb, nb, bb, tb, pb = q_refuse("v2b", fail_add=(3,), fail_take=(1,))
    nt = [x.split(") ", 1)[1] for x in notes(banklog(GS))]
    check(len(nt) == 4 and nt[3] == "DISBAND-PAYOUT-CANCELLED: SkyyCoins could not pay Bea's share, so every share paid before was taken back "
                                    "except %d coins (Steve %d (net 600)) that stay with those members, logged above as disband-payout; the "
                                    "guild is NOT disbanded and keeps %d coins." % (sh[0], sh[0], 3000 - sh[0]),
          "V2b. CANCELLED names the share that stayed with Steve: %s" % nt[3:])
    bl = banklog(GS)
    kept_ln = [x for x in bl if " player=Steve disband-payout " in x]
    check(len(kept_ln) == 1 and bl.index(kept_ln[0]) < bl.index(notes(bl)[3]), "V2b. Steve's kept share is a move logged before CANCELLED")
    # V3 (finding 2): the rollback rewrite of the live file fails (a directory blocks guilds/g1.properties.tmp from Alex's payout on)
    BLOCK = [None]
    GSv, g = q_setup("new", "v3", {1: 5000, 2: 5000, 3: 5000}, [1, 2], [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)])

    def block_tmp(u, n):
        if u == str(uid(2)) and BLOCK[0] is None:
            BLOCK[0] = gfile(GSv) + ".tmp"
            os.makedirs(BLOCK[0])

    for n, a_ in ((1, 600), (2, 400), (3, 1000)):
        move(GSv, n, "dep", a_)
    g.bank = g.bank + 1000
    GSv.saveGuild(g)
    tb = coins_total() + int(g.bank)
    FAIL_ADD.add(str(uid(2)))
    HOOK[0] = block_tmp
    r, out = capture(lambda: str(GSv.disband(uid(1), NAMES[1], True)))
    HOOK[0] = None
    pp = jprops(gfile(GSv))
    check(r == "-SkyyCoins could not pay Alex's share of the guild bank, so Pay Guild was NOT disbanded - every coin paid so far went back "
               "to the guild bank. Try again.", "V3. refused as before: %r" % r)
    check(out.count("could not save guild g1") == 3, "V3. the rollback save was tried 3 times (%d)" % out.count("could not save guild g1"))
    loud = ("DISBAND ROLLBACK NOT ON DISK: guild g1 'Pay Guild' holds 3000 bank coins in memory, but guilds/g1.properties still says "
            "DISBANDED with bank 0 after 3 tries. It is retried every 5 s; if the server stops before a save works, edit that file while "
            "the server is stopped: bank=3000 and delete its disbanded line.")
    check(("[SkyyGuilds] WARN " + loud) in out, "V3. a loud WARN names the guild id and its bank: %r" % out[-700:])
    check(bool(g.dirty) and int(g.bank) == 3000 and "disbanded" in pp and pp.get("bank") == "0",
          "V3. memory holds bank 3000 and stays dirty; the disk still says disbanded / bank 0 (what the WARN says)")
    check(coins_total() + int(g.bank) == tb and GSv.GUILDS.get("g1") is not None, "V3. coins conserved in memory, the guild loaded")
    if BLOCK[0]:
        os.rmdir(BLOCK[0])
    GSv.flushDirty()
    pp = jprops(gfile(GSv))
    check("disbanded" not in pp and pp.get("bank") == "3000" and not g.dirty, "V3. once the block is gone flushDirty repairs the file (bank 3000, not disbanded)")
    FAIL_ADD.clear()
    r2 = str(GSv.disband(uid(1), NAMES[1], True))
    check(r2.startswith("+Pay Guild is disbanded.") and coins_total() == tb, "V3. a retry then disbands: %r" % r2)
    COUNT["V"] += 1
    # V4 (finding 4): the leave confirms name the positive contribution left in the bank - 0.1.6 with the refund at 0% = 0.1.5 exactly
    LEAVE_MEM = [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0), (5, 0, 0, 0)]
    plain = {}
    REFUND_PCT[0] = 0
    for k in ("old", "new"):
        GS, g = q_setup(k, "v4", {1: 5000, 2: 5000, 3: 5000, 4: 5000, 5: 5000}, [1, 2, 3], LEAVE_MEM, lim=(-1, 0))
        move(GS, 1, "dep", 600)
        move(GS, 2, "dep", 400)
        move(GS, 3, "dep", 1000)
        plain[k] = (str(GS.leaveWarning(uid(4))), str(GS.leave(uid(4), NAMES[4], False)))
        GS.netAdd(g, str(uid(5)), 0, 100)                  # Dot: net -100
        tail = " stays in the bank for the other members"
        w3, w2, w1, w5 = (str(GS.leaveWarning(uid(n))) for n in (3, 2, 1, 5))
        check(w3 == "=Click Leave again within 10 s to leave Pay Guild. Your guild bank contribution (1,000 coins)" + tail + ".",
              "V4. a Member who cannot withdraw (limit 0): no withdraw hint: %r" % w3)
        check(w2 == "=Click Leave again within 10 s to leave Pay Guild. Your guild bank contribution (400 coins)" + tail
              + " - withdraw first if you want coins back.", "V4. an Admin (no limit): with the hint: %r" % w2)
        check(w1 == "=Leaving makes Alex the new Leader. Your guild bank contribution (600 coins)" + tail
              + " - withdraw first if you want coins back. Click Leave again within 10 s.", "V4. the Leader: %r" % w1)
        check(w5 == "=Click Leave again within 10 s to leave Pay Guild.", "V4. a negative contribution: 0.1.4's text: %r" % w5)
        lead_cmd = str(GS.leave(uid(1), NAMES[1], False))
        check(lead_cmd == "=You are the Leader: leaving makes Alex the new Leader. Your guild bank contribution (600 coins)" + tail
              + " - withdraw first if you want coins back. Type /guild leave again within 10 s to confirm.", "V4. /guild leave, Leader: %r" % lead_cmd)
        GS.CONFIRM.clear()
        fbefore = open(gfile(GS), "rb").read()
        c1 = str(GS.leave(uid(3), NAMES[3], False))
        check(c1 == "=Your guild bank contribution (1,000 coins)" + tail + ". Type /guild leave again within 10 s to leave Pay Guild.",
              "V4. /guild leave, a Member with a positive contribution now asks first: %r" % c1)
        check(g.member(str(uid(3))) is not None and open(gfile(GS), "rb").read() == fbefore, "V4. ... and nothing changed yet")
        c2 = str(GS.leave(uid(3), NAMES[3], False))
        check(c2 == "+You left Pay Guild." and g.member(str(uid(3))) is None and int(g.bank) == 2000 and net_of("new", g, 3) == (1000, 0),
              "V4. repeated within 10 s: Bea leaves, the bank keeps her 1,000, her totals stay in the file for a rejoin: %r" % c2)
        c5 = str(GS.leave(uid(5), NAMES[5], False))
        check(c5 == "+You left Pay Guild." and g.member(str(uid(5))) is None, "V4. /guild leave, a negative contribution: leaves at once (0.1.4): %r" % c5)
        COUNT["V"] += 1
    REFUND_PCT[0] = 35
    check(plain["new"] == plain["old"] and plain["new"] == ("=Click Leave again within 10 s to leave Pay Guild.", "+You left Pay Guild."),
          "V4. no contribution: the page confirm and /guild leave are 0.1.5's (%s / %s)" % (plain["old"], plain["new"]))
    print("V. review hardening: the payout plan in the server log + banklog.log before the first coin (START / PAID n/N / DONE | "
          "CANCELLED, never read as moves, a crash at the 2nd payout leaves the plan + 1 PAID line); the rollback save tried 3 times, "
          "a loud WARN with the id + bank, flushDirty repairs; leave confirms name a positive contribution (Member, Admin, Leader, "
          "/guild leave asks a Member first), zero / negative = 0.1.4 - on BOTH jars (0.1.6 at 0%%); %d /guildadmin info seed lines (S)" % COUNT["V5"])

    # ---------------- L. the leave / kick refund (0.1.6; the 0.1.6 jar, refund 35% unless a check says otherwise)
    def ref_refund(net, pct, bank):
        """Python reference: (refund, before the bank cap) = floor(pct x net / 100) for a positive net, pct clamped 0-100, at most the bank"""
        p = min(max(pct, 0), 100)
        full = net * p // 100 if net > 0 and p > 0 else 0
        return min(full, max(0, bank)), full

    # L1: the maths
    GS, Cfg, X = reset("new", "l1")
    for net, pct, bank, want in ((1000, 35, 10 ** 6, 350), (999, 35, 10 ** 6, 349), (0, 35, 10 ** 6, 0), (-500, 35, 10 ** 6, 0),
                                 (1000, 0, 10 ** 6, 0), (1000, 100, 10 ** 6, 1000), (1000, 35, 200, 200), (1000, 35, 0, 0),
                                 (3, 35, 100, 1), (2, 35, 100, 0), (1000, 30, 10 ** 6, 300), (1000, 40, 10 ** 6, 400),
                                 (10 ** 18, 100, 9 * 10 ** 18, 10 ** 18), (9 * 10 ** 18, 35, 9 * 10 ** 18, 9 * 10 ** 18 * 35 // 100),
                                 (1000, 150, 10 ** 6, 1000), (1000, -5, 10 ** 6, 0)):
        full = int(GS.refundFull(net, pct))
        got = min(full, max(0, bank))
        check(got == want and (got, full) == ref_refund(net, pct, bank),
              "L1. refund of net %d at %d%% with bank %d: %d (want %d)" % (net, pct, bank, got, want))
        COUNT["L1"] += 1
    rl = random.Random(1601)
    for i in range(600):
        dep, wd = rl.randint(0, 10 ** rl.randint(1, 15)), rl.randint(0, 10 ** rl.randint(1, 15))
        pct, bank = rl.choice((0, 30, 35, 40, 100, rl.randint(0, 100))), rl.choice((0, 1, rl.randint(0, 10 ** rl.randint(1, 15))))
        Cfg.LEAVE_REFUND = pct
        g = make_guild("new", "g1", "Maths", "", [(1, 2, 0, 0), (2, 0, 0, 0)], bank=bank, nets={2: (dep, wd)})
        ri = [int(x) for x in GS.refundInfo(g, str(uid(2)))]
        x, full = ref_refund(dep - wd, pct, bank)
        check(ri == [x, dep - wd, full, pct], "L1. refundInfo net %d pct %d bank %d: %s, want %s" % (dep - wd, pct, bank, ri, [x, dep - wd, full, pct]))
        COUNT["L1"] += 1
    Cfg.LEAVE_REFUND = 35
    print("L1. refund maths: %d cases (35%% of 1,000 = 350, of 999 = 349, zero / negative = 0, 0%% / 100%%, capped by the bank, 9e18, "
          "600 random refundInfo) = the Python reference" % COUNT["L1"])

    # L2: the config loader (fresh file, a 0.1.5 file gets the key ONCE, values clamped, hand edit + reload)
    CFGD = os.path.join(SCRATCH, "data", "new", "cfg")
    shutil.rmtree(CFGD, ignore_errors=True)
    os.makedirs(CFGD)

    def cfg_case(name, text):
        f = os.path.join(CFGD, name + ".properties")
        if text is not None:
            open(f, "wb").write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(f)
        Cfg.LEAVE_REFUND = -7
        _, o = capture(lambda: Cfg.load())
        return f, open(f, "rb").read(), int(Cfg.LEAVE_REFUND), o

    f, b1, v, o = cfg_case("fresh", None)
    check(b1.count(b"\nleaveRefundPercent=35\n") == 1 and BLOCK016 in b1 and v == 35 and "added the 0.1.6 key" not in o,
          "L2. a fresh config.properties has the 0.1.6 block once, 35 running")
    _, b2, v, o = cfg_case("fresh", None)
    check(b2 == b1 and v == 35, "L2. a second load of the fresh file changes nothing")
    old015 = b1.decode("latin-1").replace(BLOCK016.decode("latin-1"), "")
    check(old015 != b1.decode("latin-1") and "leaveRefundPercent" not in old015, "L2. (the 0.1.5 default file = the fresh file without the block)")
    _, b3, v, o = cfg_case("old015", old015)
    check(b3 == old015.encode("latin-1") + BLOCK016 and v == 35 and o.count("added the 0.1.6 key leaveRefundPercent") == 1,
          "L2. a 0.1.5 file gets the 0.1.6 block appended once (+ one INFO line), 35 running")
    _, b4, v, o = cfg_case("old015", None)
    check(b4 == b3 and "added the 0.1.6 key" not in o, "L2. its second load appends nothing")
    _, b5, v, o = cfg_case("nonl", "bankLogKeep=200\ndefaultAdminLimit=none\ndefaultMemberLimit=0")
    check(b5 == b"bankLogKeep=200\ndefaultAdminLimit=none\ndefaultMemberLimit=0\n" + BLOCK016 and v == 35,
          "L2. a file without a final newline gets one before the block: %r" % b5[-80:])
    for txt, want in (("leaveRefundPercent=0\n", 0), ("leaveRefundPercent=150\n", 100), ("leaveRefundPercent=-3\n", 0),
                      ("leaveRefundPercent=abc\n", 35), ("leaveRefundPercent = 40\n", 40)):
        _, bb, v, o = cfg_case("v%d" % want, "bankLogKeep=200\ndefaultAdminLimit=none\ndefaultMemberLimit=0\n" + txt)
        check(v == want and bb.endswith(txt.encode("latin-1")) and "added the 0.1.6 key" not in o,
              "L2. %r -> %d running, the file untouched (%d)" % (txt.strip(), want, v))
    open(f, "ab").write(b"leaveRefundPercent=45\n")
    Cfg.FILE = Paths.get(f)
    Cfg.reloadAll()
    check(int(Cfg.LEAVE_REFUND) == 45, "L2. a hand edit + reload (GCfg.reloadAll, the kit's RELOAD) -> 45 running")
    Cfg.LEAVE_REFUND = 35
    print("L2. config loader: fresh file, 0.1.5 file + the key once, no final newline, 5 values clamped, hand edit + reload")

    def nets_all(g):
        return dict((str(kk), (int(g.net.get(kk)[0]), int(g.net.get(kk)[1]))) for kk in g.net.keySet())

    def nets_sum(g):
        return sum(a - b for a, b in nets_all(g).values())

    def last_log(g):
        return str(g.log.get(g.log.size() - 1)).split("|")[1:]

    def gnet(g):
        """the hidden guild total (review finding 1: the rest of a leaver's contribution), (deposited, withdrawn) or (0, 0)"""
        v = g.net.get("~guild")
        return (0, 0) if v is None else (int(v[0]), int(v[1]))

    def after_leave(n0, pct, paid):
        """a leaver's totals after a leave / kick paying `paid`: a positive net with pct > 0 ends at 0 (the rest to the guild), else
        only the refund is added (0% = 0.1.5)"""
        return (n0[0], n0[0]) if pct > 0 and n0[0] - n0[1] > 0 else (n0[0], n0[1] + paid)

    # L3: leave online - a Member through the page, a Member through /guild leave (asks once), an Admin, the Leader passing it on
    LM = [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0)]
    GS, g = q_setup("new", "l3", {1: 5000, 2: 5000, 3: 5000, 4: 5000}, [1, 2, 3, 4], LM, lim=(-1, 0))
    for n, a_ in ((1, 600), (2, 400), (3, 1000), (4, 999)):
        move(GS, n, "dep", a_)
    total = coins_total() + int(g.bank)
    w3 = str(GS.leaveWarning(uid(3)))
    check(w3 == "=Click Leave again within 10 s to leave Pay Guild. You get back 350 coins (35% of your contribution of 1,000); the rest "
               "stays in the bank for the other members.", "L3. the page's Leave confirm names the refund: %r" % w3)
    r3 = str(GS.leave(uid(3), NAMES[3], True))
    check(r3 == "+You left Pay Guild. You got back 350 coins to your purse (35% of your contribution of 1,000); the rest stays in the bank.",
          "L3. Bea leaves through the page: %r" % r3)
    check(PURSE[str(uid(3))] == 5000 - 1000 + 350 and int(g.bank) == 2999 - 350 and net_of("new", g, 3) == (1000, 1000)
          and gnet(g) == (650, 0) and g.member(str(uid(3))) is None and GS.BYPLAYER.get(str(uid(3))) is None, "L3. 350 to Bea's purse, "
          "the bank 2649, her net 1000|1000 (0: a rejoin starts from 0), the other 650 to the guild, she is out: %s %d %s %s"
          % (PURSE[str(uid(3))], int(g.bank), net_of("new", g, 3), gnet(g)))
    check(last_log(g) == ["Bea", "leave-refund", "350", "2649"] and banklog(GS)[-1].endswith(") player=Bea leave-refund 350 bank=2649"),
          "L3. the refund is in the guild log + banklog.log: %s / %r" % (last_log(g), banklog(GS)[-1]))
    pp = jprops(gfile(GS))
    check(pp.get("bank") == "2649" and pp.get("net." + str(uid(3))) == "1000|1000" and pp.get("net.~guild") == "650|0"
          and ("member." + str(uid(3))) not in pp, "L3. the guild file: bank 2649, Bea's totals 1000|1000, net.~guild 650|0, Bea not a member")
    fb = open(gfile(GS), "rb").read()
    c1 = str(GS.leave(uid(4), NAMES[4], False))
    check(c1 == "=You get back 349 coins (35% of your contribution of 999); the rest stays in the bank for the other members. Type /guild "
               "leave again within 10 s to leave Pay Guild." and g.member(str(uid(4))) is not None and open(gfile(GS), "rb").read() == fb,
          "L3. a Member's /guild leave asks once first, nothing changed: %r" % c1)
    c2 = str(GS.leave(uid(4), NAMES[4], False))
    check(c2 == "+You left Pay Guild. You got back 349 coins to your purse (35% of your contribution of 999); the rest stays in the bank."
          and PURSE[str(uid(4))] == 5000 - 999 + 349 and int(g.bank) == 2649 - 349 and net_of("new", g, 4) == (999, 999)
          and gnet(g) == (1300, 0), "L3. repeated: Cid leaves with 349, his other 650 to the guild: %r" % c2)
    w2 = str(GS.leaveWarning(uid(2)))
    check(w2 == "=Click Leave again within 10 s to leave Pay Guild. You get back 140 coins (35% of your contribution of 400); the rest "
               "stays in the bank for the other members.", "L3. an Admin's confirm (no withdraw hint any more): %r" % w2)
    c = str(GS.leave(uid(1), NAMES[1], False))
    wl = str(GS.leaveWarning(uid(1)))
    check(c == "=You are the Leader: leaving makes Alex the new Leader. You get back 210 coins (35% of your contribution of 600); the "
               "rest stays in the bank for the other members. Type /guild leave again within 10 s to confirm."
          and wl == "=Leaving makes Alex the new Leader. You get back 210 coins (35% of your contribution of 600); the rest stays in the "
                    "bank for the other members. Click Leave again within 10 s.", "L3. the Leader's confirms: %r / %r" % (c, wl))
    r = str(GS.leave(uid(1), NAMES[1], False))
    check(r == "+You left Pay Guild. Alex is its new Leader. You got back 210 coins to your purse (35% of your contribution of 600); the "
               "rest stays in the bank." and int(g.member(str(uid(2))).rank) == 2 and PURSE[str(uid(1))] == 5000 - 600 + 210
          and int(g.bank) == 2300 - 210 and net_of("new", g, 1) == (600, 600) and gnet(g) == (1690, 0),
          "L3. the Leader passes the guild on and gets 210 (the other 390 to the guild): %r" % r)
    check(nets_sum(g) == int(g.bank) == 2090 and coins_total() + int(g.bank) == total,
          "L3. every player's net adds up to the bank (%d / %d), coins conserved" % (nets_sum(g), int(g.bank)))
    r = str(GS.leave(uid(2), NAMES[2], True))
    check(r == "+Pay Guild is disbanded. The guild bank's 2090 coins went to your purse." and PURSE[str(uid(2))] == 5000 - 400 + 2090
          and not [x for x in banklog(GS) if " player=Alex leave-refund" in x], "L3. the last member (Alex, net 400) gets the whole bank, "
          "no refund (0.1.5): %r" % r)
    check(coins_total() == total, "L3. coins conserved to the end")
    # L3b: a smaller bank caps the refund; 100%; 0% = 0.1.5's texts
    GS, g = q_setup("new", "l3b", {1: 0, 2: 5000}, [1, 2], [(1, 2, 0, 0), (2, 0, 0, 0)], lim=(-1, -1))
    move(GS, 2, "dep", 1000)
    move(GS, 1, "wd", 800)
    w = str(GS.leaveWarning(uid(2)))
    r = str(GS.leave(uid(2), NAMES[2], True))
    check(w == "=Click Leave again within 10 s to leave Pay Guild. You get back 200 coins - all the guild bank holds (35% of your "
              "contribution of 1,000 would be 350)." and r == "+You left Pay Guild. You got back 200 coins to your purse - all the guild "
              "bank holds (35% of your contribution of 1,000 would be 350).", "L3b. capped by the bank: %r / %r" % (w, r))
    check(int(g.bank) == 0 and net_of("new", g, 2) == (1000, 1000) and gnet(g) == (800, 0) and nets_sum(g) == 0 and PURSE[str(uid(2))] == 4200,
          "L3b. the bank 0, Alex 1000|1000 (the unpaid 800 to the guild), every net adds up to 0")
    GS, g = q_setup("new", "l3c", {1: 0, 2: 5000}, [1, 2], [(1, 2, 0, 0), (2, 0, 0, 0)], lim=(-1, -1))
    move(GS, 2, "dep", 500)
    Cfg = jc("new", "GCfg")
    Cfg.LEAVE_REFUND = 100
    r = str(GS.leave(uid(2), NAMES[2], True))
    check(r == "+You left Pay Guild. You got back 500 coins to your purse (100% of your contribution of 500)." and int(g.bank) == 0,
          "L3c. 100%%: everything back, no 'rest' clause: %r" % r)
    GS, g = q_setup("new", "l3d", {1: 0, 2: 5000}, [1, 2], [(1, 2, 0, 0), (2, 0, 0, 0)], lim=(-1, -1))
    move(GS, 2, "dep", 500)
    Cfg.LEAVE_REFUND = 0
    w = str(GS.leaveWarning(uid(2)))
    r = str(GS.leave(uid(2), NAMES[2], True))
    check(w == "=Click Leave again within 10 s to leave Pay Guild. Your guild bank contribution (500 coins) stays in the bank for the other "
              "members - withdraw first if you want coins back." and r == "+You left Pay Guild." and int(g.bank) == 500
          and PURSE[str(uid(2))] == 4500 and not [x for x in banklog(GS) if "refund" in x], "L3d. 0%%: 0.1.5's texts, nothing paid: %r / %r" % (w, r))
    Cfg.LEAVE_REFUND = 35
    print("L3. leave online: page + /guild leave (asks once) + Admin + the Leader passing it on (350 / 349 / 210), the last member = "
          "0.1.5, capped 200, 100%, 0% = 0.1.5; nets add up to the bank, coins conserved")

    # L4: kick online + offline (fake SkyyCoins; the real one is part R)
    GS, g = q_setup("new", "l4", {1: 5000, 2: 5000, 3: 5000, 4: 5000, 5: 5000}, [1, 2, 3], LM + [(5, 0, 0, 0)], lim=(-1, -1))
    for n, a_ in ((3, 1000), (4, 2000), (2, 100)):
        move(GS, n, "dep", a_)
    total = coins_total() + int(g.bank)
    note = str(GS.kickNote(uid(1), str(uid(3))))
    check(note == " Bea gets back 350 coins (35% of their contribution of 1,000); the rest stays in the bank.", "L4. the kick note: %r" % note)
    check(str(GS.kickNote(uid(1), str(uid(5)))) == "" and str(GS.kickNote(uid(99), str(uid(3)))) == "",
          "L4. no note for a member with nothing put in, nor for a viewer who is not in the guild")
    r, out = capture(lambda: str(GS.kick(uid(1), NAMES[1], "Bea")))
    check(r == "+Removed Bea from the guild. Bea got back 350 coins (35% of their contribution of 1,000); the rest stays in the bank."
          and PURSE[str(uid(3))] == 4000 + 350 and int(g.bank) == 3100 - 350 and net_of("new", g, 3) == (1000, 1000) and gnet(g) == (650, 0)
          and g.member(str(uid(3))) is None, "L4. Steve kicks Bea (online): 350 back, the other 650 to the guild: %r" % r)
    check(last_log(g) == ["Bea", "kick-refund", "350", "2750"] and banklog(GS)[-1].endswith(") player=Bea kick-refund 350 bank=2750")
          and "Steve kicked Bea from g1 (refund 350 coins, bank now 2750)" in out, "L4. logged in both logs + the server log")
    r = str(GS.kick(uid(2), NAMES[2], "Cid"))
    check(r == "+Removed Cid from the guild. Cid got back 700 coins (35% of their contribution of 2,000); the rest stays in the bank."
          and PURSE[str(uid(4))] == 3000 + 700 and int(g.bank) == 2050, "L4. Alex (Admin) kicks OFFLINE Cid: 700 to his purse: %r" % r)
    r = str(GS.kick(uid(1), NAMES[1], "Dot"))
    check(r == "+Removed Dot from the guild." and int(g.bank) == 2050, "L4. Dot put nothing in: 0.1.5's text, no refund: %r" % r)
    check(nets_sum(g) == int(g.bank) and coins_total() + int(g.bank) == total, "L4. nets add up to the bank, coins conserved")
    GS, g = q_setup("new", "l4b", {1: 5000, 3: 5000}, [1, 3], [(1, 2, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    move(GS, 3, "dep", 1000)
    Cfg.LEAVE_REFUND = 0
    check(str(GS.kickNote(uid(1), str(uid(3)))) == "" and str(GS.kick(uid(1), NAMES[1], "Bea")) == "+Removed Bea from the guild."
          and int(g.bank) == 1000, "L4. 0%: no note, 0.1.5's kick")
    Cfg.LEAVE_REFUND = 35
    print("L4. kick: the note, online 350, offline 700, nothing put in = 0.1.5, 0% = 0.1.5; nets add up, coins conserved")

    # L5: a refund that cannot be paid - a LEAVE is refused with nothing changed, a KICK still kicks and skips the refund
    REASON = {"unreadable": "the purse cannot be read right now", "addfail": "SkyyCoins could not put the coins in the purse",
              "blocked": "the guild file could not be written", "nocoins": "SkyyCoins is not loaded"}

    def l5_setup(tag):
        GS, g = q_setup("new", tag, {1: 5000, 2: 5000, 3: 5000}, [1, 2, 3], [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
        move(GS, 3, "dep", 1000)
        move(GS, 1, "dep", 500)
        GS.saveGuild(g)
        return GS, g

    def l5_fail(GS, mode):
        if mode == "unreadable":
            UNREAD.add(str(uid(3)))
        elif mode == "addfail":
            FAIL_ADD.add(str(uid(3)))
        elif mode == "blocked":
            os.makedirs(gfile(GS) + ".tmp")
        else:
            BR.remove("coins:fn:add")

    def l5_clear(GS, mode):
        UNREAD.clear()
        FAIL_ADD.clear()
        if os.path.isdir(gfile(GS) + ".tmp"):
            os.rmdir(gfile(GS) + ".tmp")
        BR.put("coins:fn:add", COINS[1])

    def state(GS, g):
        return (int(g.bank), nets_all(g), sorted(str(m.uuid) for m in g.members.values()), dict(PURSE), [str(x) for x in g.log],
                banklog(GS), str(GS.BYPLAYER.get(str(uid(3)))), jprops(gfile(GS)))

    NOCOINS_TXT = "-SkyyCoins is not running, so your refund (%s coins) cannot be paid and you cannot leave now. %s"
    NOCOINS_ASK = ["Ask the Leader or an Admin to kick you (the refund then stays in the bank) or a server admin to set Leave refund to 0.",
                   "Ask the Leader to kick you (the refund then stays in the bank) or a server admin to set Leave refund to 0.",
                   "Pass the guild on with /guild transfer and ask the new Leader to kick you (the refund then stays in the bank), or ask a "
                   "server admin to set Leave refund to 0."]
    for mode in ("unreadable", "addfail", "blocked", "nocoins"):
        GS, g = l5_setup("l5-leave-" + mode)
        fb, st0 = open(gfile(GS), "rb").read(), state(GS, g)
        total = coins_total() + int(g.bank)
        l5_fail(GS, mode)
        r, out = capture(lambda: str(GS.leave(uid(3), NAMES[3], True)))
        want = (NOCOINS_TXT % ("350", NOCOINS_ASK[0]) if mode == "nocoins" else
                "-Your guild bank refund (350 coins) could not be paid: %s. You are still in Pay Guild - nothing changed. Try again." % REASON[mode])
        check(r == want, "L5 %s. the leave is refused: %r" % (mode, r))
        st1 = state(GS, g)
        check(st1 == st0 and coins_total() + int(g.bank) == total,
              "L5 %s. NOTHING changed: bank, totals, members, purses, both logs, the index, the guild file (parsed)%s"
              % (mode, "" if st1 == st0 else ": %s" % [i for i in range(len(st0)) if st0[i] != st1[i]]))
        if mode in ("unreadable", "nocoins", "blocked"):
            check(open(gfile(GS), "rb").read() == fb, "L5 %s. the guild file is byte-identical (never written)" % mode)
        if mode == "addfail":
            check("WARN leave-refund of 350 for Bea" in out, "L5 addfail. SkyyCoins' refusal is a WARN: %r" % out[-200:])
        l5_clear(GS, mode)
        if mode == "blocked":
            GS.flushDirty()
        r2 = str(GS.leave(uid(3), NAMES[3], True))
        check(r2.startswith("+You left Pay Guild. You got back 350 coins") and int(g.bank) == 1150 and coins_total() + int(g.bank) == total,
              "L5 %s. once it works again the leave pays 350: %r" % (mode, r2))
        COUNT["L5"] += 1
        # the same failure on a KICK: Bea is kicked anyway, the refund stays in the bank
        GS, g = l5_setup("l5-kick-" + mode)
        total = coins_total() + int(g.bank)
        p0, n0 = dict(PURSE), nets_all(g)
        l5_fail(GS, mode)
        r, out = capture(lambda: str(GS.kick(uid(1), NAMES[1], "Bea")))
        check(r == "+Removed Bea from the guild. Their refund (350 coins) could not be paid (%s), so it stays in the guild bank." % REASON[mode],
              "L5 %s. the kick happens anyway: %r" % (mode, r))
        n1 = dict(n0)
        n1[str(uid(3))] = (1000, 1000)
        n1["~guild"] = (1000, 0)
        check(g.member(str(uid(3))) is None and GS.BYPLAYER.get(str(uid(3))) is None and int(g.bank) == 1500 and nets_all(g) == n1
              and dict(PURSE) == p0 and coins_total() + int(g.bank) == total, "L5 %s. Bea is out, the bank keeps 1,500, her whole 1,000 "
              "to the guild, purses unchanged, coins conserved: %s" % (mode, nets_all(g)))
        check(("WARN kick refund of 350 coins for Bea (%s) from g1 'Pay Guild' skipped: %s" % (uid(3), REASON[mode])) in out
              and last_log(g) == ["Bea", "kick-refund-skipped", "350", "1500"]
              and banklog(GS)[-1].endswith(") player=Bea kick-refund-skipped 350 bank=1500"),
              "L5 %s. a WARN + the kick-refund-skipped line in both logs: %r" % (mode, out[-300:]))
        l5_clear(GS, mode)
        GS.flushDirty()
        pp = jprops(gfile(GS))
        check(("member." + str(uid(3))) not in pp and pp.get("bank") == "1500" and pp.get("net." + str(uid(3))) == "1000|1000"
              and pp.get("net.~guild") == "1000|0",
              "L5 %s. the guild file (after flushDirty for the blocked case): Bea out, bank 1500, her totals 1000|1000, net.~guild 1000|0" % mode)
        COUNT["L5"] += 1
    print("L5. %d refusal cases (unreadable purse, SkyyCoins refuses, guild file blocked, no SkyyCoins): leave refused with nothing "
          "changed, then works; kick done, refund skipped + WARN + log line, the bank keeps it; coins conserved" % COUNT["L5"])

    # L6: banklog.log lines - parseBankLine on both jars; 0.1.6's seed counts the refunds, 0.1.5's skips them without breaking the
    # current members' totals
    GS, g = q_setup("new", "l6", {1: 5000, 2: 5000, 3: 5000, 4: 5000}, [1, 2, 3, 4], LM, lim=(-1, -1))
    for n, a_ in ((1, 1000), (2, 600), (3, 400), (4, 300)):
        move(GS, n, "dep", a_)
    move(GS, 1, "wd", 100)
    GS.leave(uid(3), NAMES[3], True)                           # Bea: refund 140
    UNREAD.add(str(uid(2)))
    capture(lambda: GS.kick(uid(1), NAMES[1], "Alex"))         # Alex: refund 210 skipped
    UNREAD.clear()
    GS.kick(uid(1), NAMES[1], "Cid")                           # Cid: refund 105
    bl = banklog(GS)
    kinds = [ln.split(" player=")[1].split()[-3] for ln in bl]
    check(kinds == ["deposit"] * 4 + ["withdraw", "leave-refund", "kick-refund-skipped", "kick-refund"], "L6. the bank log: %s" % kinds)
    for k in ("old", "new"):
        GSk = jc(k, "GuildStore")
        parsed = [GSk.parseBankLine(ln, "g1") for ln in bl]
        check(all(p_ is not None for p_ in parsed) and [str(p_).split("|", 1)[1] for p_ in parsed] == [str(x).split("|", 1)[1] for x in g.log],
              "L6. %s parseBankLine (backfill + seed) reads every line, refunds too, = the guild file log" % k)
        hm = JClass("java.util.HashMap")()
        d = [int(GSk.seedLine(hm, str(p_))) for p_ in parsed]
        want_d = [1000, 600, 400, 300, -100] + ([-140, 0, -105] if k == "new" else [0, 0, 0])
        check(d == want_d, "L6. %s seedLine: %s (want %s: 0.1.6 counts the refunds, the skipped refund is no move%s)"
              % (k, d, want_d, "" if k == "new" else "; 0.1.5 skips all three"))
    check(int(g.bank) == 2300 - 100 - 140 - 105 and nets_sum(g) == int(g.bank), "L6. bank 1955 = every player's net")
    GS.saveGuild(g)
    seeds = {}
    for k in ("old", "new"):
        dk = os.path.join(SCRATCH, "data", k, "l6-strip")
        shutil.rmtree(dk, ignore_errors=True)
        shutil.copytree(str(GS.DIR.toString()), dk)
        gp = os.path.join(dk, "guilds", "g1.properties")
        txt = open(gp, "rb").read().decode("latin-1")
        open(gp, "wb").write("".join(l for l in txt.splitlines(True) if not l.startswith(("net.", "netSeed="))).encode("latin-1"))
        GSk, Cfgk, Xk = reset(k, "l6-strip", d=dk)
        _, o = capture(lambda: GSk.loadAll())
        gk = GSk.GUILDS.get("g1")
        seeds[k] = (nets_all(gk), str(gk.netSeed).split("|")[1:], o)
    check(seeds["old"][0] == seeds["new"][0] == {str(uid(1)): (1000, 100)}, "L6. after a 0.1.4 rollback both seeds give Steve (the one "
          "member left) 1000|100 = his running total: %s / %s" % (seeds["old"][0], seeds["new"][0]))
    check(seeds["new"][1] == ["complete", "7", "5"] and "COMPLETE" in seeds["new"][2],
          "L6. 0.1.6's seed is COMPLETE (7 moves: the refunds explain every coin, the skipped refund is no move; 5 by players who left): %s"
          % seeds["new"][1])
    check(seeds["old"][1] == ["partial", "5", "3"] and "PARTIAL" in seeds["old"][2],
          "L6. 0.1.5's seed skips the 2 refunds: PARTIAL, the current member's totals unchanged: %s" % seeds["old"][1])
    print("L6. banklog.log: deposit / withdraw / leave-refund / kick-refund-skipped / kick-refund read by parseBankLine on both jars; "
          "0.1.6's seed counts the refunds (complete), 0.1.5's skips them (partial) - the current members' totals are the same")

    # L7: fuzz - random leave / kick / rejoin / deposit / withdraw / promote / pct with random failures: after EVERY step every player's
    # net adds up to the bank, the coins in purses + bank never change, every refund = the reference
    rz = random.Random(1606)
    PL = list(range(1, 11))
    for rnd_i in range(40):
        GS, Cfg, X = reset("new", "fuzz")
        PURSE.clear()
        PURSE.update(dict((str(uid(n)), rz.randint(0, 20000)) for n in PL))
        set_online(PL)
        g = make_guild("new", "g1", "Fuzz Guild", "FZ", [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0), (5, 0, 0, 0)], lim=(-1, -1))
        GS.saveGuild(g)
        total = coins_total()
        BUF = BAOS()
        OLD_OUT = System.out
        System.setOut(PS(BUF, True, "UTF-8"))
        Cfg.LEAVE_REFUND = rz.choice((0, 35, 35, 30, 40, 100, rz.randint(0, 100)))
        for step in range(120):
            g = GS.GUILDS.get("g1")
            if g is None:
                break
            mem = [(int(str(m.uuid)[-12:], 16), int(m.rank)) for m in g.members.values()]
            ids = [n for n, _r in mem]
            UNREAD.clear()
            FAIL_ADD.clear()
            if rz.random() < 0.15:
                (UNREAD if rz.random() < 0.5 else FAIL_ADD).add(str(uid(rz.choice(PL))))
            op = rz.random()
            if len(ids) <= 2 and op >= 0.63 and rz.random() < 0.8:
                op = 0.4 + rz.random() * 0.15                    # few members: mostly invite instead of leave / kick
            if op < 0.25:
                n = rz.choice(ids)
                GS.deposit(uid(n), NAMES[n], str(rz.randint(1, 3000)))
            elif op < 0.37:
                n = rz.choice(ids)
                GS.withdraw(uid(n), NAMES[n], str(rz.randint(1, 2000)))
            elif op < 0.55:
                outside = [n for n in PL if n not in ids]
                inviters = [n for n, r_ in mem if r_ >= 1]
                if outside and inviters:
                    t, inv = rz.choice(outside), rz.choice(inviters)
                    GS.invite(uid(inv), NAMES[inv], NAMES[t])
                    GS.accept(uid(t), NAMES[t])
            elif op < 0.6:
                lead = [n for n, r_ in mem if r_ == 2]
                if lead and len(ids) > 1:
                    GS.promote(uid(lead[0]), NAMES[lead[0]], NAMES[rz.choice(ids)])
            elif op < 0.63:
                Cfg.LEAVE_REFUND = rz.choice((0, 35, 50, 100, rz.randint(0, 100)))
            elif op < 0.82:
                n = rz.choice(ids)
                last = len(ids) == 1
                b0, n0, p0, pct = int(g.bank), net_of("new", g, n) or (0, 0), PURSE[str(uid(n))], int(Cfg.LEAVE_REFUND)
                g0 = gnet(g)
                x, _f = ref_refund(n0[0] - n0[1], pct, b0)
                bad = x > 0 and (str(uid(n)) in UNREAD or str(uid(n)) in FAIL_ADD)
                r = str(GS.leave(uid(n), NAMES[n], True))
                if last:
                    gone = GS.GUILDS.get("g1") is None
                    check((gone and PURSE[str(uid(n))] == p0 + b0) or (not gone and r.startswith("-") and int(g.bank) == b0),
                          "L7. the last member's leave disbands with the whole bank (0.1.5), or a failing purse refuses it: %r" % r)
                elif bad:
                    check(r.startswith("-Your guild bank refund (") and int(g.bank) == b0 and (net_of("new", g, n) or (0, 0)) == n0
                          and gnet(g) == g0 and PURSE[str(uid(n))] == p0 and g.member(str(uid(n))) is not None,
                          "L7. a refused leave changed nothing: %r" % r)
                    COUNT["L7 refused"] += 1
                else:
                    n1 = after_leave(n0, pct, x)
                    check(r.startswith("+You left") and g.member(str(uid(n))) is None and PURSE[str(uid(n))] == p0 + x and int(g.bank) == b0 - x
                          and (net_of("new", g, n) or (0, 0)) == n1 and gnet(g)[0] - g0[0] == n1[1] - n0[1] - x and gnet(g)[1] == 0,
                          "L7. leave with refund %d (net %d, pct %d, bank %d): %r %s %s" % (x, n0[0] - n0[1], pct, b0, r, n1, gnet(g)))
                    COUNT["L7 left"] += 1
                    COUNT["L7 refunds"] += 1 if x > 0 else 0
            else:
                kickers = [(n, r_) for n, r_ in mem if r_ >= 1]
                if kickers:
                    kn, kr = rz.choice(kickers)
                    targets = [n for n, r_ in mem if r_ < kr]
                    if targets:
                        t = rz.choice(targets)
                        b0, n0, p0, pct = int(g.bank), net_of("new", g, t) or (0, 0), PURSE[str(uid(t))], int(Cfg.LEAVE_REFUND)
                        g0 = gnet(g)
                        x, _f = ref_refund(n0[0] - n0[1], pct, b0)
                        bad = x > 0 and (str(uid(t)) in UNREAD or str(uid(t)) in FAIL_ADD)
                        r, _o = capture(lambda: str(GS.kick(uid(kn), NAMES[kn], NAMES[t])))
                        paid = 0 if bad else x
                        n1 = after_leave(n0, pct, paid)
                        check(r.startswith("+Removed") and g.member(str(uid(t))) is None and PURSE[str(uid(t))] == p0 + paid
                              and int(g.bank) == b0 - paid and (net_of("new", g, t) or (0, 0)) == n1
                              and gnet(g)[0] - g0[0] == n1[1] - n0[1] - paid,
                              "L7. kick with refund %d%s: %r" % (x, " (skipped)" if bad else "", r))
                        COUNT["L7 kicked"] += 1
                        COUNT["L7 skipped" if bad else "L7 refunds"] += 1 if x > 0 else 0
            g2 = GS.GUILDS.get("g1")
            if g2 is not None:
                check(nets_sum(g2) == int(g2.bank), "L7 round %d step %d: every player's net adds up to the bank (%d / %d)"
                      % (rnd_i, step, nets_sum(g2), int(g2.bank)))
            check(coins_total() + (int(g2.bank) if g2 is not None else 0) == total, "L7 round %d step %d: coins conserved" % (rnd_i, step))
            COUNT["L7 steps"] += 1
        System.setOut(OLD_OUT)
        g = GS.GUILDS.get("g1")
        if g is not None:
            UNREAD.clear()
            FAIL_ADD.clear()
            GS.saveGuild(g)
            gl = GS.loadGuildFile(Paths.get(gfile(GS)))
            nz = lambda d_: dict((kk, v) for kk, v in d_.items() if v != (0, 0))      # propsOf never writes a 0|0 total (0.1.5)
            check(gl is not None and int(gl.bank) == int(g.bank) and nz(nets_all(gl)) == nz(nets_all(g))
                  and sorted(str(m.uuid) for m in gl.members.values()) == sorted(str(m.uuid) for m in g.members.values()),
                  "L7 round %d: the guild file reads back the same bank, totals and members" % rnd_i)
        else:
            COUNT["L7 disbanded"] += 1
    Cfg.LEAVE_REFUND = 35
    print("L7. fuzz: 40 rounds, %d steps (%d leaves, %d refused, %d kicks, %d refunds paid, %d skipped, %d guilds disbanded by the last "
          "member): every player's net = the bank and coins conserved after every step, every refund = the reference" % (
              COUNT["L7 steps"], COUNT["L7 left"], COUNT["L7 refused"], COUNT["L7 kicked"], COUNT["L7 refunds"], COUNT["L7 skipped"],
              COUNT["L7 disbanded"]))

    # L8: the 0.1.6 review fixes (APPROVE WITH NOTES): 1 leave + rejoin loops, 2 a refund that changed after its confirm / an empty bank,
    # 4 no SkyyCoins, 5 the info line before the purse is paid, 6 a stale page Kick
    # (1) Bea (1,000 in) leaves and Alex re-invites her, 12 times: 35% once, then nothing (before the fix: 350, 227, 148 ... = 993)
    GS, g = q_setup("new", "l8-loop", {1: 5000, 2: 5000, 3: 5000}, [1, 2, 3], [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    g.netSeed = "%d|new|0|0" % NOW                 # as every guild file 0.1.5 / 0.1.6 writes (no re-seed when 0.1.5 loads it below)
    move(GS, 3, "dep", 1000)
    total = coins_total() + int(g.bank)
    got = []
    for i in range(12):
        p0 = PURSE[str(uid(3))]
        r = str(GS.leave(uid(3), NAMES[3], True))
        got.append(PURSE[str(uid(3))] - p0)
        check(r.startswith("+You left Pay Guild.") and g.member(str(uid(3))) is None, "L8 loop %d. Bea leaves: %r" % (i, r))
        check(str(GS.invite(uid(2), NAMES[2], NAMES[3])).startswith("+Invited") and str(GS.accept(uid(3), NAMES[3])).startswith("+Welcome"),
              "L8 loop %d. Alex re-invites Bea, she accepts" % i)
        check(nets_sum(g) == int(g.bank) and coins_total() + int(g.bank) == total, "L8 loop %d. nets = the bank, coins conserved" % i)
        COUNT["L8"] += 1
    check(got == [350] + [0] * 11 and int(g.bank) == 650 and net_of("new", g, 3) == (1000, 1000) and gnet(g) == (650, 0),
          "L8. 12 leave + rejoin rounds pay 35%% ONCE (350, then 0 x 11): %s, bank %d, Bea %s, ~guild %s" % (got, int(g.bank), net_of("new", g, 3), gnet(g)))
    move(GS, 1, "dep", 500)
    check(int(GS.shareOf(g, str(uid(3)))) == 0 and int(GS.shareOf(g, str(uid(1)))) == int(g.bank) == 1150,
          "L8. the rejoined Bea's old coins are no disband share (Steve, the one positive net, would get all 1,150)")
    p_ = jprops(gfile(GS))
    dk = os.path.join(SCRATCH, "data", "old", "l8-loop")
    shutil.rmtree(dk, ignore_errors=True)
    shutil.copytree(str(GS.DIR.toString()), dk)
    GSo, _c, _x = reset("old", "l8-loop", d=dk)
    capture(lambda: GSo.loadAll())
    go = GSo.GUILDS.get("g1")
    check(p_.get("net.~guild") == "650|0" and go is not None and go.net.get("~guild") is not None
          and int(go.net.get("~guild")[0]) == 650 and sum(int(v[0]) - int(v[1]) for v in go.net.values()) == int(go.bank) == 1150,
          "L8. 0.1.5 loads net.~guild=650|0 (rollback safe): its nets add up to its bank: %s %s %s" % (
              p_.get("net.~guild"), None if go is None else int(go.bank),
              None if go is None else dict((str(kk), (int(go.net.get(kk)[0]), int(go.net.get(kk)[1]))) for kk in go.net.keySet())))
    # (2) a refund that changed between the confirm and the second click is asked again - the page path (leaveWarning, then leave(.., true))
    GS, g = q_setup("new", "l8-quote", {1: 50000, 2: 5000, 3: 5000}, [1, 2, 3], [(1, 2, 0, 0), (2, 0, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    move(GS, 3, "dep", 1000)
    move(GS, 2, "dep", 1000)
    w = str(GS.leaveWarning(uid(3)))
    check(w.endswith(" You get back 350 coins (35% of your contribution of 1,000); the rest stays in the bank for the other members."),
          "L8 quote. Bea's page confirm shows 350: %r" % w)
    move(GS, 1, "wd", "all")
    fb, st = open(gfile(GS), "rb").read(), (int(g.bank), nets_all(g), dict(PURSE))
    r1 = str(GS.leave(uid(3), NAMES[3], True))
    check(r1 == "=The guild bank changed: You get nothing back - the guild bank is empty (35% of your contribution of 1,000 would be 350). "
                "Click Leave again within 10 s to leave." and g.member(str(uid(3))) is not None and open(gfile(GS), "rb").read() == fb
          and (int(g.bank), nets_all(g), dict(PURSE)) == st, "L8 quote. Steve emptied the bank after the confirm: nothing done, asked again: %r" % r1)
    r2 = str(GS.leave(uid(3), NAMES[3], True))
    check(r2 == "+You left Pay Guild. You got nothing back - the guild bank was empty (35% of your contribution of 1,000 would be 350)."
          and g.member(str(uid(3))) is None and net_of("new", g, 3) == (1000, 1000) and gnet(g) == (1000, 0) and nets_sum(g) == int(g.bank) == 0,
          "L8 quote. clicked again: Bea leaves with nothing, told so, her 1,000 to the guild: %r" % r2)
    # ... and /guild leave (Alex, 1,000 in): asked with 350, the bank drops to 200, asked again with 200 (armed), then leaves with 200
    move(GS, 1, "dep", 5000)
    c1 = str(GS.leave(uid(2), NAMES[2], False))
    move(GS, 1, "wd", 4800)
    c2 = str(GS.leave(uid(2), NAMES[2], False))
    c3 = str(GS.leave(uid(2), NAMES[2], False))
    check(c1.startswith("=You get back 350 coins (35% of your contribution of 1,000)")
          and c2 == "=The guild bank changed: You get back 200 coins - all the guild bank holds (35% of your contribution of 1,000 would be 350). "
                    "Type /guild leave again within 10 s to leave."
          and c3 == "+You left Pay Guild. You got back 200 coins to your purse - all the guild bank holds (35% of your contribution of 1,000 would be 350)."
          and PURSE[str(uid(2))] == 5000 - 1000 + 200 and int(g.bank) == 0 and gnet(g) == (1800, 0) and nets_sum(g) == 0,
          "L8 quote. /guild leave: %r / %r / %r" % (c1, c2, c3))
    COUNT["L8"] += 3
    # the same amount = no new question (L3 pays after leaveWarning); an empty bank on a KICK says so too
    GS, g = q_setup("new", "l8-empty", {1: 5000, 3: 5000}, [1, 3], [(1, 2, 0, 0), (3, 0, 0, 0)], lim=(-1, -1))
    move(GS, 3, "dep", 1000)
    move(GS, 1, "wd", "all")
    note = str(GS.kickNote(uid(1), str(uid(3))))
    r = str(GS.kick(uid(1), NAMES[1], "Bea"))
    check(note == " Bea gets nothing back - the guild bank is empty (35% of their contribution of 1,000 would be 350)."
          and r == "+Removed Bea from the guild. Bea got nothing back - the guild bank was empty (35% of their contribution of 1,000 would be 350)."
          and gnet(g) == (1000, 0) and nets_sum(g) == int(g.bank) == 0, "L8 empty bank. the kick note + result: %r / %r" % (note, r))
    # (4) no SkyyCoins: a leave with a refund is refused UP FRONT (the page's confirm is a "-" refusal, so it does not arm; /guild leave
    # does not ask), nothing changes; a member with no refund still leaves; a kick still kicks (refund skipped)
    GS, g = q_setup("new", "l8-nocoins", {1: 5000, 2: 5000, 3: 5000, 4: 5000}, [1, 2, 3, 4],
                    [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0)], lim=(-1, -1))
    for n, a_ in ((1, 600), (2, 400), (3, 1000)):
        move(GS, n, "dep", a_)
    BR.remove("coins:fn:add")
    fb, st = open(gfile(GS), "rb").read(), (int(g.bank), nets_all(g), dict(PURSE))
    for n, rk, x in ((3, 0, "350"), (2, 1, "140"), (1, 2, "210")):
        want = NOCOINS_TXT % (x, NOCOINS_ASK[rk])
        w, c = str(GS.leaveWarning(uid(n))), str(GS.leave(uid(n), NAMES[n], False))
        c2 = str(GS.leave(uid(n), NAMES[n], False))
        check(w == want and c == want and c2 == want and g.member(str(uid(n))) is not None, "L8 no SkyyCoins. %s (%s): refused up front, "
              "page and /guild leave (twice): %r / %r" % (NAMES[n], ("Member", "Admin", "Leader")[rk], w, c))
        COUNT["L8"] += 1
    check(open(gfile(GS), "rb").read() == fb and (int(g.bank), nets_all(g), dict(PURSE)) == st, "L8 no SkyyCoins. nothing changed")
    r = str(GS.leave(uid(4), NAMES[4], False))
    check(r == "+You left Pay Guild." and g.member(str(uid(4))) is None, "L8 no SkyyCoins. Cid (nothing put in, no refund) still leaves: %r" % r)
    r, _o = capture(lambda: str(GS.kick(uid(1), NAMES[1], "Bea")))
    check(r == "+Removed Bea from the guild. Their refund (350 coins) could not be paid (SkyyCoins is not loaded), so it stays in the guild bank."
          and g.member(str(uid(3))) is None and int(g.bank) == 2000 and nets_sum(g) == 2000, "L8 no SkyyCoins. a kick still kicks: %r" % r)
    BR.put("coins:fn:add", COINS[1])
    # (5) the info line between the guild file write and coins:fn:add (a crash there can be paid by hand), and the rest's line
    GS, g = l5_setup("l8-info")
    FAIL_ADD.add(str(uid(3)))
    r, out = capture(lambda: str(GS.leave(uid(3), NAMES[3], True)))
    FAIL_ADD.clear()
    i1 = out.find("leave-refund of 350 coins for Bea (%s) from g1 'Pay Guild': the guild file is written (bank 1150), paying the purse now" % uid(3))
    i2 = out.find("WARN leave-refund of 350 for Bea")
    check(r.startswith("-Your guild bank refund (350 coins) could not be paid") and 0 <= i1 < i2,
          "L8 info. the paying line comes before SkyyCoins' refusal: %r" % out[-400:])
    r, out = capture(lambda: str(GS.leave(uid(3), NAMES[3], True)))
    check(r.startswith("+You left") and "paying the purse now" in out and "Bea (%s) got 350 coins back from g1; the other 650 coins of their "
          "contribution stay with the guild" % uid(3) in out, "L8 info. paid: the paying line + the rest's line: %r" % out[-400:])
    # (6) a stale page Kick (the row's uuid) of a member who already left
    GS, g = q_setup("new", "l8-stale", {1: 5000, 3: 5000}, [1, 3], [(1, 2, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0)], lim=(-1, -1))
    GS.leave(uid(3), NAMES[3], True)
    r1, r2 = str(GS.kick(uid(1), NAMES[1], str(uid(3)))), str(GS.kick(uid(1), NAMES[1], "Nobody"))
    check(r1 == "-That player is not in your guild any more." and r2 == "-Nobody called Nobody is in your guild.",
          "L8 stale kick: %r / %r" % (r1, r2))
    COUNT["L8"] += 4
    print("L8. review fixes: leave + rejoin x 12 = 350 once (was 993), no disband share for old coins, 0.1.5 keeps net.~guild; a changed "
          "refund asks again (page + /guild leave), an empty bank says so (leave + kick); no SkyyCoins refused up front (Member / Admin / "
          "Leader), no refund leaves, a kick kicks; the paying info line; a stale Kick - %d groups" % COUNT["L8"])

    # ---------------- D. differential page builds 0.1.5 vs 0.1.6 (refund 0% = 0.1.5) + the 0.1.6 refund texts
    ALLOWED = set(SUI.allowed_colors())
    VIEWS = K["GUILD_PAGE"]["views"]
    H = {"none": VIEWS["none"][0].h, "guild": VIEWS["guild"][0].h, "log": VIEWS["log"][0].h}
    INNER = K["GUILD_IN"]
    PW = K["GUILD_PW"]
    SEEN = collections.defaultdict(set)
    RANKCOL = collections.defaultdict(set)
    NETCOL = collections.defaultdict(set)           # "neg" / "pos" -> the contribution cell colours seen
    BUTTONS = {}

    def build(pg):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = [(str(c.type), None if c.selector is None else str(c.selector), None if c.text is None else str(c.text),
                 None if c.data is None else str(c.data)) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), None if e.data is None else str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        return cmds, evs

    def view_of(cmds):
        root = [t for typ, sel, t, d in cmds if is_append(typ) and sel is None]
        m = re.search(r"Height: (\d+)", root[0] if root else "")
        h = int(m.group(1)) if m else 0
        if h == H["none"]:
            return "none"
        return "log" if any(k_[0] == "#SkyyGLogTitle.Text" for k_ in sets_of(cmds)) else "guild"

    def check_new(tag, cmds, evs, my=None):
        """the 0.1.5 page as the client gets it"""
        created, ap, body = set(), SUI.Appends(), []
        first = True
        view = view_of(cmds)
        for typ, sel, text, data in cmds:
            if is_append(typ):
                parent = None if sel is None else sel.lstrip("#")
                check(first == (parent is None), "D. %s: only the first append is the page root" % tag)
                first = False
                check(parent is None or parent in created, "D. %s: append into #%s before it exists" % (tag, parent))
                try:
                    SUI.check_markup(text, prefix=PREFIX, root=(parent is None))
                    COUNT["D markups"] += 1
                except ValueError as e:
                    check(False, "D. %s: check_markup: %s" % (tag, e))
                for c in COL_RE.findall(text):
                    check(SUI.norm_color(c) in ALLOWED, "D. %s: colour %s is not a kit colour" % (tag, c))
                    COUNT["D colours"] += 1
                for bad in ("FlexWeight", "WrapMaxLines", "LetterSpacing", "LayoutMode: Right", "LayoutMode: Center", "LayoutMode: Full",
                            "Width: 0,", "Width: 0)", "Height: 0)", "ItemGrid"):
                    check(bad not in text, "D. %s: %s in %s" % (tag, bad, text[:80]))
                created.update(ID_RE.findall(text))
                ap.append((parent, text))
                if parent == "SkyyGuild":
                    body.append(text)
            else:
                ident, prop = sel.lstrip("#").rsplit(".", 1)
                check(ident in created, "D. %s: b.set #%s.%s before its element exists" % (tag, ident, prop))
                ap.sets.append((ident, prop, str(js(data))))
                if prop == "Text":
                    SEEN[ident].add(str(js(data)))
        try:
            SUI.check_page(ap, PREFIX)
            COUNT["D pages"] += 1
        except ValueError as e:
            check(False, "D. %s: check_page: %s" % (tag, e))
        try:
            SUI.assert_proven(ap, what=tag)
        except Exception as e:
            check(False, "D. %s: assert_proven: %s" % (tag, e))
        for typ, sel, data, lock in evs:
            check(sel.lstrip("#") in created, "D. %s: binding on a missing element %s" % (tag, sel))
        root = ap[0][1]
        check(SUI.outer_size(root) == (K["GUILD_W"], H[view]), "D. %s: page root %s, want %dx%d" % (tag, SUI.outer_size(root), K["GUILD_W"], H[view]))
        used = sum(SUI.outer_size(t)[1] for t in body)
        check(used == H[view] - SUI.TITLE_H - 2 * SUI.CONTENT_PAD, "D. %s: the body children fill %d px exactly (got %d)"
              % (tag, H[view] - SUI.TITLE_H - 2 * SUI.CONTENT_PAD, used))
        for p, t in ap:
            if p == "SkyyGList":
                m = re.match(r"Group #SkyyGRow(\d+) .*?Group #SkyyGRowP\1 \{ Anchor: \(Width: (\d+), Height: (\d+)\)", t)
                if check(m is not None, "D. %s: a member row with its panel" % tag):
                    n, pw = m.group(1), int(m.group(2))
                    if my is not None:
                        check(pw == PW[my], "D. %s: row panel %d px for rank %d (want %d)" % (tag, pw, my, PW[my]))
                    btns = sum(SUI.outer_size(x)[0] for q, x in ap if q == "SkyyGRow" + n)
                    check(pw + btns <= K["GUILD_ROW_W"], "D. %s: row %s is %d px of %d" % (tag, n, pw + btns, K["GUILD_ROW_W"]))
                    COUNT["D rows"] += 1
        for p, t in ap:
            for bm in BTN_RE.finditer(t):
                w = re.search(r"Width: (\d+)", bm.group(0)).group(1)
                pad = re.search(r"Padding: \(Horizontal: (\d+)\)", bm.group(0)).group(1)
                BUTTONS.setdefault((w, pad, bm.group(2)), set()).add(bm.group(1))
                COUNT["D buttons"] += 1
        rank_txt = dict((i, v) for i, pr, v in ap.sets if pr == "Text" and i.startswith("SkyyGRowRank"))
        net_txt = dict((i, v) for i, pr, v in ap.sets if pr == "Text" and i.startswith("SkyyGRowNet"))
        for p, t in ap:
            if p == "SkyyGList":
                for m in re.finditer(r"Label #(SkyyGRowRank\d+) \{[^{}]*?TextColor: (#[0-9A-Fa-f]{6})", t):
                    if check(m.group(1) in rank_txt, "D. %s: #%s has its rank text" % (tag, m.group(1))):
                        RANKCOL[rank_txt[m.group(1)]].add(SUI.norm_color(m.group(2)))
                for m in re.finditer(r"Label #(SkyyGRowNet\d+) \{[^{}]*?TextColor: (#[0-9A-Fa-f]{6})", t):
                    if check(m.group(1) in net_txt, "D. %s: #%s has its contribution text" % (tag, m.group(1))):
                        NETCOL["neg" if net_txt[m.group(1)].startswith("-") else "pos"].add(SUI.norm_color(m.group(2)))
                        COUNT["D net cells"] += 1
        info = [t for p, t in ap if "Label #SkyyGInfo " in t]
        if check(len(info) == 1, "D. %s: one result line" % tag):
            col = re.search(r"TextColor: (#[0-9A-Fa-f]{6})", info[0]).group(1)
            txt = [v for i, pr, v in ap.sets if i == "SkyyGInfo"]
            COUNT["D info " + col] += 1
            return col, txt
        return None, None

    def compare(tag, co, eo, cn, en, my=None, info=""):
        check(eo == en, "D. %s: event bindings identical (%d / %d)" % (tag, len(eo), len(en)))
        COUNT["D bindings"] += len(en)
        ao = [(typ, sel, t) for typ, sel, t, d_ in co if is_append(typ)]
        an = [(typ, sel, t) for typ, sel, t, d_ in cn if is_append(typ)]
        check(ao == an, "D. %s: every append (markup) identical (%d / %d)" % (tag, len(ao), len(an)))
        COUNT["D appends"] += len(an)
        so, sn = sets_of(co), sets_of(cn)
        check(so == sn, "D. %s: b.set lines identical: only 0.1.5 %s, only 0.1.6 %s" % (tag, dict(so - sn), dict(sn - so)))
        COUNT["D sets"] += sum(so.values())
        to, tn = texts_of(co), texts_of(cn)
        check(to == tn, "D. %s: visible texts identical: only 0.1.5 %s, only 0.1.6 %s" % (tag, dict(to - tn), dict(tn - to)))
        COUNT["D texts"] += sum(tn.values())
        io, inn = ids_of(co), ids_of(cn)
        check(io == inn, "D. %s: the same element ids: %s" % (tag, sorted(io ^ inn)))
        COUNT["D ids"] += len(io)
        col, txt = check_new(tag, cn, en, my)
        want = SUI.STATUS.get(info[:1], SUI.COLOR["text"]) if info else SUI.COLOR["text"]
        if col is not None:
            check(col == want, "D. %s: result line colour %s for %r, want %s" % (tag, col, info[:20], want))

    LOG40 = [logline(i, NAMES[1 + i % 4], ("deposit", "withdraw", "limit-admin", "limit-member", "disband-payout")[i % 5],
                     (i + 1) * 137 if i % 5 < 2 else (-1 if i % 5 == 2 else (0 if i % 5 == 3 else 5000)), 100000 + i * 11) for i in range(40)]
    WIDE_XP, WIDE_COINS = 9999990000000, 10 ** 15
    M12 = [(1, 2, 12345, 0), (2, 1, 900, 1500), (3, 1, 0, 0), (4, 0, 77, 200), (5, 0, 5, 0), (6, 0, 0, 0), (7, 0, 1234567, 0),
           (8, 0, 3, 0), (9, 0, 0, 999), (10, 0, 44, 0), (11, 0, 0, 0), (12, 0, 999999999, 0)]
    STATES = [
        ("none plain", 1, [1], None, {}, True),
        ("none invite + error", 1, [1, 2], ("g2", "Abcdefghijklmnopqrstuvwx", "ABCD", [(2, 2, 0, 0), (3, 0, 0, 0)]),
         {"info": "-A guild called Foo already exists. Pick another name.", "keepName": "Foo", "invite": (2, 245500)}, True),
        ("none declined", 1, [1], None, {"info": "=You declined the invite to Somewhere."}, True),
        ("none founded text", 1, [1], None, {"info": "+You founded X! You are its Leader. Invite players with /guild invite <player> - /guild opens the guild page."}, True),
        ("leader of 3", 1, [1, 2], ("g1", "Skyy Guild", "SKY", [(1, 2, 120, 0), (2, 1, 40, 0), (3, 0, 0, 500)]),
         {"xp": 1234, "bank": 5000, "log": LOG40[:2], "lim": (-1, 0)}, True),
        ("leader 12 page 1 armed kick", 1, [1, 2, 4, 5, 7, 9], ("g1", "Skyy Guild", "", M12),
         {"xp": 987654, "bank": 123456789, "log": LOG40[:5], "armed": ("kick", 5), "info": "=Click Sure? within 10 s to remove Dot from the guild."}, True),
        ("leader 12 page 2 armed lead + keeps", 1, [1, 2, 4, 5, 7, 9], ("g1", "Skyy Guild", "", M12),
         {"xp": 50, "bank": 0, "log": LOG40, "pageNo": 1, "armed": ("lead", 10), "keepInvite": "Bob", "keepAmount": "2k", "keepLimit": "5k",
          "info": "=Click Confirm? within 10 s to make Ivo the Leader (you become an Admin)."}, True),
        ("leader armed leave", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0), (2, 0, 0, 0)]),
         {"armed": ("leave",), "info": "=Leaving makes Alex the new Leader. Click Leave again within 10 s."}, True),
        ("leader armed disband", 1, [1], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(1, 2, 0, 0), (2, 0, 0, 0), (3, 1, 0, 0)]),
         {"bank": 1000000000000, "armed": ("disband",), "info": "=Disbanding deletes Abcdefghijklmnopqrstuvwx for all 25 members and pays the bank's 1000000000000 coins to your purse. Click Disband again within 10 s."}, True),
        ("admin view", 3, [1, 2, 3, 5], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0), (2, 1, 0, 0), (3, 1, 50, 1200), (4, 0, 0, 0), (5, 0, 0, 0)]),
         {"lim": (5000, 0), "keepAmount": "1.5m", "info": "-You can take 3,800 more coins today (1,200 / 5,000). The count starts again on the next game day."}, True),
        ("member no withdraw, clamped page", 5, [1, 5], ("g1", "Skyy Guild", "", M12[:9]), {"pageNo": 7, "lim": (-1, 0)}, True),
        ("member limit day unknown", 5, [5], ("g1", "Skyy Guild", "", [(1, 2, 0, 0), (5, 0, 0, 0)]), {"lim": (-1, 2000)}, False),
        ("long names big numbers", 13, [13, 14], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(13, 2, 999999999999, 0), (14, 1, 5, 1000000000)]),
         {"xp": 999999999999, "bank": 1000000000000, "log": [logline(1, NAMES[14], "limit-member", 1000000000000, 1000000000000)],
          "lim": (1000000000000, 1000000000000)}, True),
        ("zero xp empty log", 1, [1], ("g1", "Solo", "", [(1, 2, 0, 0)]), {"xp": 0, "log": []}, True),
        ("log empty", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": []}, True),
        ("log one page", 3, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0), (3, 1, 0, 0)]), {"view": 1, "log": LOG40[:7], "lim": (5000, 0)}, True),
        ("log page 1 of 3", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40}, True),
        ("log page 2 of 3", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40, "logPage": 1}, True),
        ("log last page", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40, "logPage": 2,
                                                                                 "info": "-The guild file could not be written - nothing moved (guild bank: 5). Try again."}, True),
        ("log clamped page", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40, "logPage": 9, "info": "plain"}, False),
        ("admin 12 page 1", 3, [1, 3, 5], ("g1", "Skyy Guild", "SKY", M12), {"lim": (5000, 0), "log": LOG40[:4]}, True),
        ("admin 12 page 2", 3, [1, 3, 5], ("g1", "Skyy Guild", "SKY", M12), {"lim": (5000, 0), "pageNo": 1, "log": LOG40[:4]}, True),
        ("leader exactly 7 members", 1, [1, 2, 3, 4, 5, 6, 7], ("g1", "Skyy Guild", "SKY", M12[:7]), {"xp": 4321, "log": LOG40[:3]}, True),
        ("leader page 2 of 8 members", 1, [1, 8], ("g1", "Skyy Guild", "SKY", M12[:8]), {"pageNo": 1, "log": LOG40[:1]}, True),
        ("member page 2", 5, [5, 12], ("g1", "Skyy Guild", "SKY", M12), {"pageNo": 1, "lim": (-1, 2000)}, True),
        ("log 15 moves", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40[:15]}, True),
        ("log 16 moves page 2", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40[:16], "logPage": 1}, True),
        ("member views the log", 5, [1, 5], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0), (5, 0, 0, 300)]),
         {"view": 1, "log": LOG40[:20], "lim": (-1, 2000)}, True),
        ("widest texts", 15, [15, 16] + list(range(100, 598)),
         ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(15, 2, WIDE_XP, WIDE_COINS), (16, 1, WIDE_XP, WIDE_COINS)]
          + [(n, 0, WIDE_XP, WIDE_COINS) for n in range(100, 598)]),
         {"share": 1000, "xp": WIDE_XP, "bank": WIDE_COINS, "lim": (WIDE_COINS, WIDE_COINS),
          "log": [logline(i, NAMES[15 + i % 2], ("deposit", "withdraw", "limit-admin", "limit-member", "disband-payout")[i % 5],
                          WIDE_COINS, WIDE_COINS) for i in range(5)]}, True),
        ("widest log", 16, [15, 16], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(15, 2, 0, 0), (16, 1, 0, 0)]),
         {"view": 1, "lim": (WIDE_COINS, WIDE_COINS),
          "log": [logline(i, NAMES[15 + i % 2], ("deposit", "withdraw", "limit-admin", "limit-member", "disband-payout")[i % 5],
                          WIDE_COINS, WIDE_COINS) for i in range(10)]}, True),
        ("widest invite", 15, [15, 16], ("g2", "Abcdefghijklmnopqrstuvwx", "ABCD", [(16, 2, 0, 0)] + [(n, 0, 0, 0) for n in range(100, 599)]),
         {"invite": (16, 299000), "keepName": "Abcdefghijklmnopqrstuvwx",
          "info": "-A guild called Abcdefghijklmnopqrstuvwx already exists. Pick another name."}, True),
    ]

    def setup_state(k, st):
        name, me, online, gfix, f, dayk = st
        GS, Cfg, X = reset(k, "page-" + name, day_known=dayk)
        if "share" in f:
            Cfg.SHARE = f["share"]
        set_online(online)
        rank = None
        if gfix is not None:
            gid, gname, tag, mem = gfix
            if f.get("invite") is None or gid == "g1":
                make_guild(k, gid, gname, tag, mem, f.get("xp", 0), f.get("bank", 0), f.get("log", ()), f.get("lim", (-1, 0)), f.get("nets"))
            else:
                make_guild(k, gid, gname, tag, mem)
            for n, r_, _c, _t in mem:
                if n == me:
                    rank = r_
        if f.get("invite"):
            who, ms = f["invite"]
            a = JArray(JObject)(3)
            a[0], a[1], a[2] = JClass("java.lang.String")(gfix[0]), JClass("java.lang.String")(NAMES[who]), Long(int(System.currentTimeMillis()) + ms)
            GS.INVITES.put(str(uid(me)), a)
        pg = jc(k, "GuildPage")(pref(me))
        info = f.get("info", "")
        if callable(info):
            info = info(GS)
        pg.info = info
        pg.view = f.get("view", 0)
        pg.pageNo = f.get("pageNo", 0)
        pg.logPage = f.get("logPage", 0)
        for fld in ("keepName", "keepInvite", "keepAmount", "keepLimit"):
            if fld in f:
                setattr(pg, fld, f[fld])
        armed = f.get("armed")
        if armed:
            pg.confirm = armed[0] if len(armed) == 1 else "%s:%s" % (armed[0], str(uid(armed[1])))
            pg.confirmUntil = int(System.currentTimeMillis()) + 60000
        return pg, rank

    BOUNDARY = {"admin 12 page 1": ("SkyyGList", "#SkyyGPrev", "Page 1 / 2", 7),
                "admin 12 page 2": ("SkyyGList", "#SkyyGPrev", "Page 2 / 2", 5),
                "leader exactly 7 members": ("SkyyGList", "#SkyyGPrev", None, 7),
                "leader page 2 of 8 members": ("SkyyGList", "#SkyyGPrev", "Page 2 / 2", 1),
                "member page 2": ("SkyyGList", "#SkyyGPrev", "Page 2 / 2", 5),
                "log 15 moves": ("SkyyGLList", "#SkyyGLPrev", None, 15),
                "log 16 moves page 2": ("SkyyGLList", "#SkyyGLPrev", "Page 2 / 2", 1),
                "member views the log": ("SkyyGLList", "#SkyyGLPrev", "Page 1 / 2", 15)}
    REFUND_PCT[0] = 0
    for st in STATES:
        res2 = {}
        for k in ("old", "new"):
            pg, rank = setup_state(k, st)
            res2[k] = build(pg)
        (co, eo), (cn, en) = res2["old"], res2["new"]
        compare("D " + st[0], co, eo, cn, en, rank, st[4].get("info", ""))
        COUNT["D states"] += 1
        if st[0] in BOUNDARY:
            lst_id, prev, ptxt, nrows = BOUNDARY[st[0]]
            for k, (cc, ee) in (("0.1.5", res2["old"]), ("0.1.6", res2["new"])):
                has = any(sel == prev for typ, sel, data, lock in ee)
                check(has == (ptxt is not None), "D. %s %s: pager %s (want %s)" % (st[0], k, "shown" if has else "none", ptxt))
                if ptxt is not None:
                    txt = [str(js(d_)) for typ, sel, t, d_ in cc if sel in ("#SkyyGPageTxt.Text", "#SkyyGLPageTxt.Text")]
                    check(txt == [ptxt], "D. %s %s: pager text %s, want %s" % (st[0], k, txt, ptxt))
                rows = sum(1 for typ, sel, t, d_ in cc if is_append(typ) and sel == "#" + lst_id and re.fullmatch(r"SkyyGL?Row\d+", first_id(t)))
                if k == "0.1.6":
                    check(rows == nrows, "D. %s: %d rows in #%s, want %d" % (st[0], rows, lst_id, nrows))
                COUNT["D boundary"] += 1
    print("D. %d states x 2 jars at 0%%: %d bindings, %d appends, %d b.set lines, %d visible texts, %d ids identical; 0.1.6: %d markups "
          "through check_markup in %d check_page, %d colours audited, %d member rows measured" % (
              COUNT["D states"], COUNT["D bindings"], COUNT["D appends"], COUNT["D sets"], COUNT["D texts"], COUNT["D ids"],
              COUNT["D markups"], COUNT["D pages"], COUNT["D colours"], COUNT["D rows"]))

    # 0.1.5's own states (the member list order + numbers, the widest contribution texts, its result texts): both jars at 0%, identical
    ORDER_MEM = [(1, 2, 0, 0), (2, 1, 0, 0), (3, 1, 0, 0), (4, 0, 0, 0), (5, 0, 0, 0), (6, 0, 0, 0), (7, 0, 0, 0)]
    ORDER_NETS = {1: (0, 5000), 2: (0, 0), 3: (100000, 25000), 4: (2000, 5000), 6: (500, 0), 7: (0, 0)}      # 5: no moves
    NEW_STATES = [
        ("order + numbers (Leader view)", 1, [1, 3, 5], ("g1", "Skyy Guild", "SKY", ORDER_MEM), {"bank": 72500, "nets": ORDER_NETS}, True),
        ("order + numbers (Member view)", 4, [1, 3, 4, 5], ("g1", "Skyy Guild", "SKY", ORDER_MEM), {"bank": 72500, "nets": ORDER_NETS, "lim": (-1, -1)}, True),
        ("order page 2 of 9", 1, [1], ("g1", "Skyy Guild", "SKY", ORDER_MEM + [(8, 0, 0, 0), (9, 0, 0, 0)]),
         {"bank": 72500, "nets": dict(list(ORDER_NETS.items()) + [(8, (1, 0)), (9, (0, 1))]), "pageNo": 1}, True),
        ("widest contributions", 15, [15, 16], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(15, 2, WIDE_XP, WIDE_COINS), (16, 1, WIDE_XP, WIDE_COINS),
                                                                                            (100, 0, 0, 0), (101, 0, 0, 0), (102, 0, 0, 0)]),
         {"share": 1000, "xp": WIDE_XP, "bank": WIDE_COINS, "lim": (WIDE_COINS, WIDE_COINS),
          "nets": {15: (999999999999999, 0), 16: (0, 999999999999999), 100: (10 ** 15, 0), 101: (0, 2 ** 62), 102: (2 ** 62, 0)}}, True),
        ("disband split confirm text", 1, [1], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(1, 2, 0, 0), (2, 0, 0, 0), (3, 1, 0, 0)]),
         {"bank": 1000000000000, "armed": ("disband",), "nets": {1: (999999999999, 0), 2: (1, 0), 3: (5, 0)},
          "info": lambda GS: str(GS.disbandWarning(uid(1)))}, True),
        ("disband split result text", 14, [14], None,
         {"info": "+Abcdefghijklmnopqrstuvwx is disbanded. The guild bank's 1000000000000000 coins went back to 500 members in equal "
                  "parts (nobody had put in more than they took out) - your share: 2000000000000 coins."}, True),
        ("payout refused text", 14, [14], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(14, 2, 0, 0)]),
         {"info": "-SkyyCoins could not pay Abcdefghijklmnop's share of the guild bank, so Abcdefghijklmnopqrstuvwx was NOT disbanded - "
                  "every coin paid so far went back to the guild bank. Try again."}, True),
        ("payout kept text", 14, [14], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(14, 2, 0, 0)]),
         {"info": "-SkyyCoins could not pay Abcdefghijklmnop's share, so Abcdefghijklmnopqrstuvwx was NOT disbanded. 999999999999999 coins "
                  "already paid could not be taken back - see the bank log. Try again."}, True),
        ("unreadable purse text", 14, [14], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(14, 2, 0, 0)]),
         {"info": "-Abcdefghijklmnop's purse cannot be read right now, so the guild bank cannot be paid out and Abcdefghijklmnopqrstuvwx was "
                  "NOT disbanded (nothing changed). Try again."}, True),
        # review fix 4: the widest leave confirms with the contribution note (computed by the jar)
        ("leave note text (Leader, widest)", 1, [1], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (14, 0, 0, 0)]),
         {"bank": 999999999999999, "armed": ("leave",), "nets": {1: (999999999999999, 0)}, "info": lambda GS: str(GS.leaveWarning(uid(1)))}, True),
        ("leave note text (Member, widest)", 15, [15], ("g1", "Abcdefghijklmnopqrstuvwx", "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (15, 0, 0, 0)]),
         {"bank": 999999999999999, "armed": ("leave",), "lim": (-1, -1), "nets": {15: (999999999999999, 0)},
          "info": lambda GS: str(GS.leaveWarning(uid(15)))}, True),
    ]
    LEAVE_WIDE = {
        "leave note text (Leader, widest)": "=Leaving makes WWWWWWWWWWWWWWWW the new Leader. Your guild bank contribution (999,999,999,999,999 "
                                            "coins) stays in the bank for the other members - withdraw first if you want coins back. Click "
                                            "Leave again within 10 s.",
        "leave note text (Member, widest)": "=Click Leave again within 10 s to leave Abcdefghijklmnopqrstuvwx. Your guild bank contribution "
                                            "(999,999,999,999,999 coins) stays in the bank for the other members - withdraw first if you "
                                            "want coins back."}
    for st in NEW_STATES:
        pgo, _rk = setup_state("old", st)
        co, eo = build(pgo)
        pg, rank = setup_state("new", st)
        cmds, evs = build(pg)
        info = str(pg.info)
        check(str(pgo.info) == info, "D+. %s: the same result text on both jars at 0%%: %r / %r" % (st[0], str(pgo.info), info))
        compare("D+ " + st[0], co, eo, cmds, evs, rank, info)
        col, txt = check_new("D+ " + st[0], cmds, evs, rank)
        want = SUI.STATUS.get(info[:1], SUI.COLOR["text"]) if info else SUI.COLOR["text"]
        if col is not None:
            check(col == want, "D+. %s: result line colour" % st[0])
        rows = rows_of(cmds)
        if st[0].startswith("order + numbers"):
            names = [r_["Name"].replace("  (you)", "") for r_ in rows]
            nets = [r_["Net"] for r_ in rows]
            check(names == ["Steve", "Bea", "Alex", "Eve", "Dot", "Finn", "Cid"],
                  "D+. %s: order rank, then contribution, then online, then name: %s" % (st[0], names))
            check(nets == ["-5,000", "75,000", "0", "500", "0", "0", "-3,000"], "D+. %s: contribution texts %s" % (st[0], nets))
            COUNT["D+ order"] += 1
        if st[0] == "order page 2 of 9":
            check([r_["Name"] for r_ in rows] == ["Hana", "Cid"] and [r_["Net"] for r_ in rows] == ["-1", "-3,000"],
                  "D+. page 2 shows the most negative members last: %s" % rows)
        if st[0] == "widest contributions":
            wantn = sorted(net_text(d_ - w_) for d_, w_ in st[4]["nets"].values())
            check(sorted(r_["Net"] for r_ in rows) == wantn and "1000000.00b" in wantn and "999,999,999,999,999" in wantn,
                  "D+. widest contribution texts %s, want %s" % (sorted(r_["Net"] for r_ in rows), wantn))
        if st[0] == "disband split confirm text":
            mine = ref_pay([(999999999999, 0), (1, 0), (5, 0)], 1000000000000, [2, 0, 1], [0, 1, 2])[0]
            check(info == "=Disbanding deletes Abcdefghijklmnopqrstuvwx for all 3 members and pays the bank's 1000000000000 coins back to the "
                          "members by contribution (your share: %d). Click Disband again within 10 s." % mine, "D+. confirm text: %r" % info)
        if st[0] in LEAVE_WIDE:
            check(info == LEAVE_WIDE[st[0]], "D+. %s: %r" % (st[0], info))
            check(LEAVE_WIDE[st[0]][1:] in SEEN["SkyyGInfo"], "D+. %s: shown in the result line (F measures it)" % st[0])
        COUNT["D+ states"] += 1
    check(NETCOL.get("neg") == {SUI.norm_color(SUI.COLOR["error"])} and NETCOL.get("pos") == {SUI.norm_color(SUI.COLOR["value"])},
          "D+. contribution colours: negative %s (want error red), else %s (want value)" % (sorted(NETCOL.get("neg", ())), sorted(NETCOL.get("pos", ()))))
    want_rank = {"Leader": SUI.norm_color(SUI.COLOR["gold"]), "Admin": SUI.norm_color(SUI.COLOR[K["GUILD_RANK_ADMIN"]]),
                 "Member": SUI.norm_color(SUI.COLOR["value"])}
    for rk, want in sorted(want_rank.items()):
        check(RANKCOL.get(rk) == {want}, "D. %s rows are coloured %s, want %s" % (rk, sorted(RANKCOL.get(rk, ())), want))
    print("D+. %d new states: the member list order (Steve -5,000 | Bea 75,000, Alex 0 | Eve 500, Dot 0 online, Finn 0, Cid -3,000) "
          "in %d views, %d contribution cells (negative %s, else %s), the new result texts" % (
              COUNT["D+ states"], COUNT["D+ order"], COUNT["D net cells"], sorted(NETCOL.get("neg", ())), sorted(NETCOL.get("pos", ()))))

    REFUND_PCT[0] = 35

    def no_coins(fn):
        BR.remove("coins:fn:add")
        try:
            return fn()
        finally:
            BR.put("coins:fn:add", COINS[1])

    def requoted(GS, n, bank):
        """the page's confirm quotes the refund, the bank changes, the confirmed leave asks again (review finding 2)"""
        GS.leaveWarning(uid(n))
        GS.GUILDS.get("g1").bank = bank
        return str(GS.leave(uid(n), NAMES[n], True))

    W15 = 999999999999999
    WREF = W15 * 35 // 100                        # 349,999,999,999,999
    GNAME = "Abcdefghijklmnopqrstuvwx"
    CAPPED = lambda poss: "%s coins - all the guild bank holds (35%% of %s contribution of %s would be %s)" % (num(WREF - 1), poss, num(W15), num(WREF))
    RLOG = [logline(i, NAMES[15 + i % 2], ("leave-refund", "kick-refund", "kick-refund-skipped")[i % 3], WIDE_COINS, WIDE_COINS)
            for i in range(9)]
    REFUND_STATES = [
        ("refund leave note (Leader, widest)", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (14, 0, 0, 0)]),
         {"bank": W15, "armed": ("leave",), "nets": {1: (W15, 0)}, "info": lambda GS: str(GS.leaveWarning(uid(1)))},
         "=Leaving makes WWWWWWWWWWWWWWWW the new Leader. You get back %s coins (35%% of your contribution of %s); the rest stays in the "
         "bank for the other members. Click Leave again within 10 s." % (num(WREF), num(W15))),
        ("refund leave note capped (Member, widest)", 15, [15], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (15, 0, 0, 0)]),
         {"bank": WREF - 1, "armed": ("leave",), "lim": (-1, -1), "nets": {15: (W15, 0)}, "info": lambda GS: str(GS.leaveWarning(uid(15)))},
         "=Click Leave again within 10 s to leave %s. You get back %s." % (GNAME, CAPPED("your"))),
        ("refund kick confirm (widest)", 1, [1, 16], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (14, 0, 0, 0)]),
         {"bank": WREF - 1, "armed": ("kick", 16), "nets": {16: (W15, 0)},
          "info": lambda GS: "=Click Sure? within 10 s to remove %s from the guild.%s" % (NAMES[16], str(GS.kickNote(uid(1), str(uid(16)))))},
         "=Click Sure? within 10 s to remove WWWWWWWWWWWWWWWW from the guild. WWWWWWWWWWWWWWWW gets back %s." % CAPPED("their")),
        ("refund leave result (Leader, widest)", 14, [14], None,
         {"info": "+You left %s. WWWWWWWWWWWWWWWW is its new Leader. You got back %s." % (GNAME, CAPPED("your").replace(" coins - ", " coins to your purse - ", 1))},
         None),
        ("refund kick result (widest)", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (14, 0, 0, 0)]),
         {"info": "+Removed WWWWWWWWWWWWWWWW from the guild. WWWWWWWWWWWWWWWW got back %s." % CAPPED("their")}, None),
        ("refund kick skipped (widest)", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (14, 0, 0, 0)]),
         {"info": "+Removed WWWWWWWWWWWWWWWW from the guild. Their refund (%s coins) could not be paid (SkyyCoins could not put the coins "
                  "in the purse), so it stays in the guild bank." % num(WREF)}, None),
        ("refund leave refused (widest)", 15, [15], None,
         {"info": "-Your guild bank refund (%s coins) could not be paid: SkyyCoins could not put the coins in the purse. You are still in "
                  "%s - nothing changed. Try again." % (num(WREF), GNAME)}, None),
        ("refund log view (widest)", 16, [15, 16], ("g1", GNAME, "ABCD", [(15, 2, 0, 0), (16, 1, 0, 0)]),
         {"view": 1, "lim": (WIDE_COINS, WIDE_COINS), "log": RLOG}, None),
        ("refund log lines in the guild view", 15, [15, 16], ("g1", GNAME, "ABCD", [(15, 2, 0, 0), (16, 1, 0, 0)]),
         {"bank": WIDE_COINS, "log": RLOG[:3]}, None),
        # review fixes: no SkyyCoins (the Leader's text is the widest), the question after a changed refund, an empty bank
        ("refund no SkyyCoins (Leader, widest)", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (14, 0, 0, 0)]),
         {"bank": W15, "nets": {1: (W15, 0)}, "info": lambda GS: no_coins(lambda: str(GS.leaveWarning(uid(1))))},
         NOCOINS_TXT % (num(WREF), NOCOINS_ASK[2])),
        ("refund changed, asked again (Member, widest)", 15, [15], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (15, 0, 0, 0)]),
         {"bank": W15, "armed": ("leave",), "lim": (-1, -1), "nets": {15: (W15, 0)}, "info": lambda GS: requoted(GS, 15, WREF - 1)},
         "=The guild bank changed: You get back %s. Click Leave again within 10 s to leave." % CAPPED("your")),
        ("refund empty bank leave note (Leader, widest)", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (14, 0, 0, 0)]),
         {"bank": 0, "armed": ("leave",), "nets": {1: (W15, 0)}, "info": lambda GS: str(GS.leaveWarning(uid(1)))},
         "=Leaving makes WWWWWWWWWWWWWWWW the new Leader. You get nothing back - the guild bank is empty (35%% of your contribution of %s "
         "would be %s). Click Leave again within 10 s." % (num(W15), num(WREF))),
        ("refund empty bank kick confirm (widest)", 1, [1, 16], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (16, 1, 0, 0), (14, 0, 0, 0)]),
         {"bank": 0, "armed": ("kick", 16), "nets": {16: (W15, 0)},
          "info": lambda GS: "=Click Sure? within 10 s to remove %s from the guild.%s" % (NAMES[16], str(GS.kickNote(uid(1), str(uid(16)))))},
         "=Click Sure? within 10 s to remove WWWWWWWWWWWWWWWW from the guild. WWWWWWWWWWWWWWWW gets nothing back - the guild bank is empty "
         "(35%% of their contribution of %s would be %s)." % (num(W15), num(WREF))),
        ("refund empty bank leave result (Leader, widest)", 14, [14], None,
         {"info": "+You left %s. WWWWWWWWWWWWWWWW is its new Leader. You got nothing back - the guild bank was empty (35%% of your "
                  "contribution of %s would be %s)." % (GNAME, num(W15), num(WREF))}, None),
        ("refund empty bank kick result (widest)", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (14, 0, 0, 0)]),
         {"info": "+Removed WWWWWWWWWWWWWWWW from the guild. WWWWWWWWWWWWWWWW got nothing back - the guild bank was empty (35%% of their "
                  "contribution of %s would be %s)." % (num(W15), num(WREF))}, None),
        ("stale kick text", 1, [1], ("g1", GNAME, "ABCD", [(1, 2, 0, 0), (14, 0, 0, 0)]),
         {"info": lambda GS: str(GS.kick(uid(1), NAMES[1], str(uid(16))))}, "-That player is not in your guild any more."),
    ]
    for name, me, online, gfix, f, want_info in REFUND_STATES:
        st = (name, me, online, gfix, f, True)
        pg, rank = setup_state("new", st)
        cmds, evs = build(pg)
        info = str(pg.info)
        col, txt = check_new("D16 " + name, cmds, evs, rank)
        want = SUI.STATUS.get(info[:1], SUI.COLOR["text"]) if info else SUI.COLOR["text"]
        if col is not None:
            check(col == want, "D16. %s: result line colour" % name)
        if want_info is not None:
            check(info == want_info, "D16. %s: %r\n  want %r" % (name, info, want_info))
        if info:
            check(info[1:] in SEEN["SkyyGInfo"], "D16. %s: shown in the result line (F measures it)" % name)
        COUNT["D16 states"] += 1
    WHAT16 = ["got back %s coins (left the guild)" % num(WIDE_COINS), "got back %s coins (kicked)" % num(WIDE_COINS),
              "kicked: refund of %s coins not paid" % num(WIDE_COINS)]
    def seen_stem(stem):
        return set(t for ident, ts in SEEN.items() if re.fullmatch(stem + r"\d*", ident) for t in ts)

    check(all(w in seen_stem("SkyyGLWhat") for w in WHAT16), "D16. the log view shows the three refund texts at 1e15: %s"
          % sorted(t for t in seen_stem("SkyyGLWhat") if "refund" in t or "got back" in t))
    check(any("WWWWWWWWWWWWWWWW got back %s coins (kicked)" % num(WIDE_COINS) in t for t in SEEN.get("SkyyGLog0", set()) | SEEN.get("SkyyGLog1", set())
              | SEEN.get("SkyyGLog2", set())), "D16. the guild view's newest log lines name the refunds: %s"
          % sorted(t for k_, v_ in SEEN.items() if k_.startswith("SkyyGLog") for t in v_ if "got back" in t)[:3])
    print("D16. %d refund states (0.1.6, 35%%): widest leave / kick confirms (capped), results, refusals, the log view + the guild view's "
          "newest lines through check_markup / check_page / assert_proven" % COUNT["D16 states"])

    # ---------------- E. clicks through handleDataEvent, identical effects on both jars
    def guild_state(k):
        GS = jc(k, "GuildStore")
        out = []
        for gid in sorted(str(x) for x in GS.GUILDS.keySet()):
            g = GS.GUILDS.get(gid)
            mem = sorted((str(m.name), int(m.rank), int(m.wdUsed) if int(m.wdDay) == DAY else 0) for m in g.members.values())
            logs = [str(x).split("|", 1)[1] for x in g.log]
            out.append((gid, str(g.name), str(g.tag), int(g.bank), int(g.xp), int(g.limAdmin), int(g.limMember), tuple(mem), tuple(logs)))
        inv = sorted((str(kk), str(GS.INVITES.get(kk)[0])) for kk in GS.INVITES.keySet())
        return tuple(out), tuple(inv), tuple(sorted((str(kk), str(GS.BYPLAYER.get(kk))) for kk in GS.BYPLAYER.keySet()))

    def snap_rows(k, who):
        s_ = jc(k, "GuildStore").snapshot(uid(who))
        if s_ is None:
            return None
        return [[str(x) for x in r_] for r_ in s_[5]]

    def order_ok(k, rows):
        key = lambda r_: (-int(r_[2]), -int(r_[6]), 0 if r_[4] == "1" else 1, r_[1].lower())
        return rows == sorted(rows, key=key)

    LEAVE_NOTE_RE = re.compile(r" Your guild bank contribution \(([0-9,]+) coins\) stays in the bank for the other members"
                               r"(?: - withdraw first if you want coins back)?\.")
    E_NOTES = []

    def session(name, setup, steps):
        trace = {}
        for k in ("old", "new"):
            PURSE.clear()
            PURSE.update(setup["purse"])
            reset(k, "click-" + name)
            set_online(setup["online"])
            if setup.get("guild"):
                gid, gname, tag, mem, extra = setup["guild"]
                make_guild(k, gid, gname, tag, mem, **extra)
            pages = {}
            out = []
            for who, a, payload, key in steps:
                if who not in pages:
                    pages[who] = jc(k, "GuildPage")(pref(who))
                    build(pages[who])
                pg = pages[who]
                data = {"a": a}
                if key:
                    data[key] = payload
                pg.handleDataEvent(None, None, json.dumps(data))
                cmds, evs = build(pg)
                COUNT["E clicks"] += 1
                srows = snap_rows(k, who)
                info_txt = str(pg.info)
                if k == "new" and LEAVE_NOTE_RE.search(info_txt):
                    E_NOTES.append((name, NAMES.get(who), a, info_txt))
                snap = (who, a, payload, info_txt, str(pg.keepName), str(pg.keepInvite), str(pg.keepAmount), str(pg.keepLimit),
                        int(pg.view), int(pg.pageNo), int(pg.logPage), str(pg.confirm), tuple(sorted(PURSE.items())), guild_state(k))
                nonrow = collections.Counter()
                for x, c in sets_of(cmds).items():
                    if not ROW_SEL_RE.match(x[0] or ""):
                        nonrow[(x[0], x[1])] += c
                rows = rows_of(cmds)
                if srows is not None and int(pg.view) == 0:
                    check(order_ok(k, srows), "E. %s %s: the snapshot rows follow the documented order" % (name, k))
                    shown = srows[int(pg.pageNo) * 7:int(pg.pageNo) * 7 + 7]
                    check([r_["Name"].replace("  (you)", "") for r_ in rows] == [r_[1] for r_ in shown],
                          "E. %s %s after %s: the page shows the snapshot rows in order" % (name, k, a))
                    if k == "new":
                        check([r_["Net"] for r_ in rows] == [net_text(int(r_[6])) for r_ in shown], "E. %s: contribution cells = deposits - withdrawals" % name)
                    COUNT["E rows"] += len(rows)
                rk = [r_.get("Rank") for r_ in rows]
                out.append((snap, nonrow, evs, rk, sorted(tuple(r_) for r_ in (srows or [])), rows))
                if k == "new":
                    r = jc(k, "GuildStore").rankOf(uid(who))
                    check_new("E %s after %s %r" % (name, a, payload), cmds, evs, int(r) if int(r) >= 0 and int(pg.view) == 0 else None)
            trace[k] = out
        for (so, eo_sets, eo_ev, rko, mo, ro), (sn, en_sets, en_ev, rkn, mn, rn) in zip(trace["old"], trace["new"]):
            check(so == sn, "E. %s: after %s %r: 0.1.5 %s\n  0.1.6 %s" % (name, so[1], so[2], so[3:12], sn[3:12]))
            check(ro == rn, "E. %s: after %s %r: the member rows (every cell) identical" % (name, so[1], so[2]))
            check(eo_sets == en_sets, "E. %s: after %s %r: rebuilt page non-row b.set lines differ %s / %s"
                  % (name, so[1], so[2], dict(eo_sets - en_sets), dict(en_sets - eo_sets)))
            check(eo_ev == en_ev, "E. %s: after %s %r: rebuilt page bindings differ" % (name, so[1], so[2]))
            check(rko == rkn and mo == mn, "E. %s: after %s %r: the same member rows (ranks per row, member data)" % (name, so[1], so[2]))
        COUNT["E done"] += len([s_ for s_, _x, _y, _r, _m, _w in trace["new"] if s_[3].startswith("+")])
        return trace

    A_, G_, I_, L_ = "@GAmount", "@GName", "@GInvite", "@GLimit"
    REFUND_PCT[0] = 0
    session("guild life", {"purse": {str(uid(1)): 50000, str(uid(2)): 700}, "online": [1, 2]}, [
        (1, "refresh", "", None), (1, "create", "", G_), (1, "create", "Ab", G_), (1, "create", "Skyy Guild", G_),
        (1, "amount", "", A_), (1, "amount", "2k", A_), (1, "deposit", "2k", A_), (1, "deposit", "abc", A_),
        (1, "deposit", "999999999", A_), (1, "withdraw", "500", A_), (1, "limit", "", L_), (1, "limit", "5k", L_),
        (1, "limadmin", "5k", L_), (1, "limmember", "none", L_), (1, "limmember", "abc", L_), (1, "limadmin", "5k", L_),
        (1, "invite", "", I_), (1, "invite", "Nobody", I_), (1, "invite", "Alex", I_), (2, "accept", "", None),
        (1, "kick:1", "", None), (1, "refresh", "", None), (1, "kick:1", "", None), (1, "kick:1", "", None),
        (1, "invite", "Alex", I_), (2, "decline", "", None), (1, "invite", "Alex", I_), (2, "accept", "", None),
        (1, "promote:1", "", None), (1, "demote:1", "", None), (1, "promote:1", "", None), (2, "deposit", "700", A_),
        (1, "expand", "", None), (1, "lnext", "", None), (1, "lprev", "", None), (1, "back", "", None), (1, "prev", "", None),
        (1, "next", "", None), (1, "lead:1", "", None), (1, "lead:1", "", None), (1, "disband", "", None),
        (1, "withdraw", "100", A_), (1, "withdraw", "6k", A_), (1, "leave", "", None), (1, "leave", "", None),
        (2, "refresh", "", None), (2, "disband", "", None), (2, "disband", "", None), (2, "bogus:9", "", None), (2, "refresh", "", None)])
    session("12 members", {"purse": {str(uid(5)): 0}, "online": [1, 2, 4, 5, 7, 9],
                           "guild": ("g1", "Skyy Guild", "SKY", M12, {"bank": 10000, "log": LOG40[:9], "lim": (-1, 1000)})}, [
        (1, "next", "", None), (1, "next", "", None), (1, "prev", "", None), (1, "kick:3", "", None), (1, "next", "", None),
        (1, "prev", "", None), (1, "kick:3", "", None), (1, "kick:3", "", None), (1, "limmember", "1k", L_),
        (5, "withdraw", "600", A_), (5, "withdraw", "600", A_), (5, "withdraw", "all", A_), (5, "withdraw", "1", A_),
        (1, "refresh", "", None), (5, "leave", "", None), (5, "leave", "", None), (1, "refresh", "", None)])
    REFUND_PCT[0] = 35
    check(len(E_NOTES) == 1 and E_NOTES[0][:3] == ("guild life", "Steve", "leave"),
          "E. at 0%% 0.1.6 shows 0.1.5's one leave note (Steve arming Leave in 'guild life'), on both jars: %s" % E_NOTES)
    print("E. %d clicks (2 sessions x 2 jars at 0%%), %d successful actions: identical results / boxes / views / purses / guilds / "
          "bindings / b.set lines / member rows; %d rows in the documented order" % (COUNT["E clicks"], COUNT["E done"], COUNT["E rows"]))

    # E16: a 35% session on 0.1.6 only - the armed Kick names the refund, the kick and the page's Leave pay it
    PURSE.clear()
    PURSE.update({str(uid(1)): 50000, str(uid(2)): 5000, str(uid(3)): 5000, str(uid(4)): 5000})
    reset("new", "click-refund")
    set_online([1, 2, 3, 4])
    GSr = jc("new", "GuildStore")
    make_guild("new", "g1", "Skyy Guild", "SKY", [(1, 2, 0, 0), (2, 0, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0)], lim=(-1, -1))
    pages = {}

    def click(who, a, payload="", key=None):
        if who not in pages:
            pages[who] = jc("new", "GuildPage")(pref(who))
            build(pages[who])
        data = {"a": a}
        if key:
            data[key] = payload
        pages[who].handleDataEvent(None, None, json.dumps(data))
        cmds, evs = build(pages[who])
        r_ = GSr.rankOf(uid(who))
        check_new("E16 %s %s" % (NAMES[who], a), cmds, evs, int(r_) if int(r_) >= 0 and int(pages[who].view) == 0 else None)
        COUNT["E16 clicks"] += 1
        return str(pages[who].info)

    total = sum(PURSE.values())
    check(click(2, "deposit", "1000", A_).startswith("+Deposited 1000") and click(3, "deposit", "999", A_).startswith("+Deposited 999"),
          "E16. Alex and Bea deposit through the page")
    click(1, "refresh")
    idx = [str(r_[0]) for r_ in GSr.snapshot(uid(1))[5]].index(str(uid(2)))
    t1 = click(1, "kick:%d" % idx)
    check(t1 == "=Click Sure? within 10 s to remove Alex from the guild. Alex gets back 350 coins (35% of their contribution of 1,000); the "
               "rest stays in the bank.", "E16. the armed Kick names the refund: %r" % t1)
    t2 = click(1, "kick:%d" % idx)
    g = GSr.GUILDS.get("g1")
    check(t2 == "+Removed Alex from the guild. Alex got back 350 coins (35% of their contribution of 1,000); the rest stays in the bank."
          and PURSE[str(uid(2))] == 4350 and int(g.bank) == 1649, "E16. Sure kicks Alex and pays 350: %r" % t2)
    t3 = click(3, "leave")
    check(t3 == "=Click Leave again within 10 s to leave Skyy Guild. You get back 349 coins (35% of your contribution of 999); the rest "
               "stays in the bank for the other members.", "E16. Bea's Leave confirm: %r" % t3)
    t4 = click(3, "leave")
    check(t4 == "+You left Skyy Guild. You got back 349 coins to your purse (35% of your contribution of 999); the rest stays in the bank."
          and PURSE[str(uid(3))] == 4350 and int(g.bank) == 1300 and int(pages[3].view) == 0, "E16. Leave again: Bea is out with 349: %r" % t4)
    # review finding 2: Cid's Leave confirm shows 700, Steve withdraws before Cid clicks again -> asked again with 500, the Leave re-armed
    check(click(4, "deposit", "2000", A_).startswith("+Deposited 2000"), "E16. Cid deposits 2,000")
    t5 = click(4, "leave")
    check(t5 == "=Click Leave again within 10 s to leave Skyy Guild. You get back 700 coins (35% of your contribution of 2,000); the rest "
               "stays in the bank for the other members.", "E16. Cid's Leave confirm: %r" % t5)
    check(click(1, "withdraw", "2800", A_).startswith("+") and int(g.bank) == 500, "E16. Steve withdraws 2,800 (bank 500)")
    t6 = click(4, "leave")
    check(t6 == "=The guild bank changed: You get back 500 coins - all the guild bank holds (35% of your contribution of 2,000 would be "
               "700). Click Leave again within 10 s to leave." and str(pages[4].confirm) == "leave" and g.member(str(uid(4))) is not None
          and int(g.bank) == 500 and PURSE[str(uid(4))] == 3000, "E16. Cid's second click: nothing done, asked again, the Leave re-armed: %r" % t6)
    t7 = click(4, "leave")
    check(t7 == "+You left Skyy Guild. You got back 500 coins to your purse - all the guild bank holds (35% of your contribution of 2,000 "
               "would be 700)." and PURSE[str(uid(4))] == 3500 and int(g.bank) == 0 and g.member(str(uid(4))) is None,
          "E16. the third click: Cid leaves with the 500 he was shown: %r" % t7)
    click(1, "expand")
    check({"got back 350 coins (kicked)", "got back 349 coins (left the guild)"} <= seen_stem("SkyyGLWhat"), "E16. the log view lists both refunds")
    check(sum(PURSE.values()) + int(g.bank) == total and nets_sum(g) == int(g.bank), "E16. coins conserved, nets add up to the bank")
    print("E16. %d clicks at 35%% on 0.1.6: armed Kick with the refund, kick 350, page leave 349, a changed refund re-arms the Leave "
          "(700 -> 500), the log view" % COUNT["E16 clicks"])

    # ---------------- F. text fit
    n_fit = 0
    for (w, pad, size), txts in sorted(BUTTONS.items()):
        for t in txts:
            need = SUI.text_width(t, int(size), True, "Default", True)
            n_fit += 1
            check(need <= int(w) - 2 * int(pad), "F. button %r: %.0f px of label in %d px (%s - 2 x %s)" % (t, need, int(w) - 2 * int(pad), w, pad))
    cols = dict(K["GUILD_COLS"])
    lws = [w for _t, w in K["GUILD_LCOLS"]]
    lim_rest = INNER - K["GUILD_LIM_LBL_W"] - 10 - K["GUILD_LIM_BOX_W"] - 6 - K["GUILD_LIMA_W"] - 6 - K["GUILD_LIMM_W"] - 12
    one = [("SkyyGSub", 16, False, K["GUILD_SUM_IN"]), ("SkyyGBarTxt", 16, True, K["GUILD_SUM_IN"]),
           ("SkyyGXpTxt", 15, False, K["GUILD_XPTXT_W"]), ("SkyyGStats", 16, True, K["GUILD_SUM_IN"] - K["GUILD_XPTXT_W"]),
           ("SkyyGHint", 15, False, INNER), ("SkyyGLogCnt", 15, False, K["GUILD_LOGCNT_W"]), ("SkyyGLimHint", 15, False, lim_rest),
           ("SkyyGLimLbl", 16, True, K["GUILD_LIM_LBL_W"]), ("SkyyGPageTxt", 16, False, 260), ("SkyyGLPageTxt", 16, False, 260),
           ("SkyyGLogSub", 16, False, INNER), ("SkyyGLNote", 15, False, INNER), ("SkyyGRule", 15, False, INNER),
           ("SkyyGLEmpty", 16, False, K["GUILD_ROW_W"]), ("SkyyGRowName", 18, True, cols["Member"]), ("SkyyGRowRank", 16, True, cols["Rank"]),
           ("SkyyGRowNet", 16, False, cols["Contribution"]), ("SkyyGRowXp", 16, False, cols["Guild XP added"]),
           ("SkyyGRowDay", 16, False, cols["Taken today"]), ("SkyyGRowOn", 16, False, cols["Status"]),
           ("SkyyGLWhen", 16, False, lws[0]), ("SkyyGLWho", 18, True, lws[1]), ("SkyyGLWhat", 16, False, lws[2]),
           ("SkyyGLBank", 16, False, lws[3]), ("SkyyGLog", 16, False, INNER - 2 * K["GUILD_LOG_PAD"]),
           ("SkyyGHelp", 16, False, INNER - 2 * SUI.WELL_PAD), ("SkyyGMemAct", 16, True, K["GUILD_ACT_HEAD_W"])]
    worst = {}
    for stem, size, bold, width in one:
        for ident, seen in SEEN.items():
            if not re.fullmatch(stem + r"\d*", ident):
                continue
            for t in seen:
                need = SUI.text_width(t, size, bold, "Default", stem == "SkyyGMemAct")
                worst[stem] = max(worst.get(stem, 0), need / width)
                n_fit += 1
                check(need <= width, "F. #%s one line %r: %.0f px > %d px" % (ident, t, need, width))
    for ident, size, bold, width, h in (("SkyyGLimTxt", 16, True, INNER, K["GUILD_TWO"]), ("SkyyGLogLim", 16, True, INNER, K["GUILD_TWO"]),
                                        ("SkyyGInfo", 16, True, INNER, K["GUILD_TWO"]), ("SkyyGNoneTxt", 16, False, INNER, 26),
                                        ("SkyyGInvTxt", 16, True, INNER - 24 - 180 - 180 - 12, 44)):
        for t in SEEN.get(ident, ()):
            if not t:
                continue
            nl = SUI.text_lines(t, width, size, bold)
            n_fit += 1
            check(nl * SUI.line_height(size) <= h + 0.5, "F. #%s %r: %d lines (%.1f px) in %d px" % (ident, t, nl, nl * SUI.line_height(size), h))
    for ident in ("SkyyGTitle", "SkyyGLogTitle"):
        for t in SEEN.get(ident, ()):
            need = SUI.text_width(t, SUI.TITLE_SIZE, True, "Secondary", True)
            n_fit += 1
            check(need <= K["GUILD_W"] - 2 * SUI.TITLE_LABEL_PAD, "F. window title %r: %.0f px" % (t, need))
    for colset in (K["GUILD_COLS"], K["GUILD_LCOLS"]):
        for t, w in colset:
            need = SUI.text_width(t, 16, True, "Default", True)
            n_fit += 1
            worst["column heads"] = max(worst.get("column heads", 0), need / w)
            check(need <= w, "F. column head %r: %.0f px > %d px" % (t, need, w))

    def seen_all(stem):
        return set(t for ident, ts in SEEN.items() if re.fullmatch(stem + r"\d*", ident) for t in ts)

    for stem, want in (("SkyyGRowName", K["GUILD_NAME_YOU"]), ("SkyyGRowName", K["GUILD_NAME_WIDE"]), ("SkyyGXpTxt", K["GUILD_XPTXT_WIDE"]),
                       ("SkyyGStats", K["GUILD_STATS_WIDE"]),
                       ("SkyyGRowDay", K["GUILD_TAKEN_WIDE"]), ("SkyyGLWho", K["GUILD_NAME_WIDE"]),
                       ("SkyyGLWhat", K["GUILD_WHAT_WIDE"]), ("SkyyGLBank", K["GUILD_BANK_WIDE"]), ("SkyyGRowNet", K["GUILD_NET_WIDE"])):
        check(want in seen_all(stem), "F. the widest %s text %r was shown by a widest state" % (stem, want))
        COUNT["F widest"] += 1
    print("F. text fit: %d labels / texts measured; fullest one-line boxes: %s; %d widest texts shown" % (
        n_fit, ", ".join("%s %.0f%%" % (k_, v * 100) for k_, v in sorted(worst.items(), key=lambda kv: -kv[1])[:6]), COUNT["F widest"]))

    # ---------------- G. the page id
    pid, chk = K["GUILD_PAGE_ID"], K["GUILD_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready line names the page the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW))
    check(pid == chk, "G. the page the kit makes now (%s) is the checked page GUILD_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/guilds_0_1_6_patch.py, regenerate and rebuild" % (pid, chk, pid))
    check(pid == "26645a3ab908", "G. the page is 0.1.5's (26645a3ab908): 0.1.6 changes no markup (%s)" % pid)
    print("G. page id %s, checked %s, kit %s" % (pid, chk, SUI.kit_id()))

    # ---------------- K. the Server Setup row through the config kit (0.1.5 first for its rows, then 0.1.6)
    KIT = {}
    for k in ("old", "new"):
        GS, Cfg, X = reset(k, "kit")
        mods = os.path.join(SCRATCH, "kit-" + k, "mods")
        home = os.path.join(mods, "Skyy_SkyyGuilds")
        shutil.rmtree(os.path.dirname(mods), ignore_errors=True)
        os.makedirs(home)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        capture(lambda: Cfg.load())
        Pub = jc(k, "CfgPub")
        capture(lambda: Pub.start(Paths.get(mods), None))
        hdr = BR.get("config:def:SkyyGuilds")
        fn = BR.get("config:fn:SkyyGuilds")
        if not check(hdr is not None and fn is not None, "K. %s: config:def + config:fn:SkyyGuilds published" % k):
            return
        KIT[k] = ([[str(x) for x in row] for row in hdr[7]], str(hdr[3]))
        if k == "old":
            capture(lambda: Pub.shutdown())
    rows_o, rows_n = KIT["old"][0], KIT["new"][0]
    HELP = "Part of a leaving or kicked member's deposits minus withdrawals paid back from the bank. 0 = none."
    new_row = [r_ for r_ in rows_n if r_[0] == "leaveRefundPercent"]
    check(KIT["new"][1] == "0.1.6" and len(rows_o) == 14 and len(rows_n) == 15 and [r_ for r_ in rows_n if r_[0] != "leaveRefundPercent"] == rows_o,
          "K. config:def lists 0.1.5's 14 rows unchanged + one new row (%d / %d)" % (len(rows_o), len(rows_n)))
    check(len(new_row) == 1 and new_row[0] == ["leaveRefundPercent", "Leave refund (% of contribution)", "bank", "int", "35", "0", "100",
                                                "step=5", "%", "live", HELP] and len(HELP) <= 100,
          "K. the row: %s" % new_row)
    check([r_[0] for r_ in rows_n].index("leaveRefundPercent") == [r_[0] for r_ in rows_n].index("maxBank") + 1,
          "K. it sits in Guild bank right after Largest guild bank")

    def op(*args):
        a = JArray(JObject)(len(args))
        for i_, x in enumerate(args):
            a[i_] = x
        return fn.apply(a)

    def settle():
        Pub.flush()
        time.sleep(0.4)
        Pub.flush()

    cfgf = os.path.join(home, "config.properties")
    check(str(op("get", "leaveRefundPercent")) == "35" and b"\nleaveRefundPercent=35\n" in open(cfgf, "rb").read(),
          "K. get = 35; the kit's file has the line")
    r = op("set", "leaveRefundPercent", "40", None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.LEAVE_REFUND) == 40, "K. set 40 through the kit: live at once (GCfg.LEAVE_REFUND %s): %s"
          % (Cfg.LEAVE_REFUND, [str(x) for x in r]))
    settle()
    txt = open(cfgf, "rb").read()
    check(txt.count(b"leaveRefundPercent=") == 1 and b"\nleaveRefundPercent=40\n" in txt, "K. the file line now says 40 (in place)")
    for bad in ("101", "-1", "abc"):
        r = op("set", "leaveRefundPercent", bad, None, None, "yes", "console")
        check(str(r[0]) != "ok" and int(Cfg.LEAVE_REFUND) == 40, "K. %r refused (%s), 40 stays" % (bad, [str(x) for x in r]))
    r = op("set", "leaveRefundPercent", "35%", None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.LEAVE_REFUND) == 35, "K. '35%%' typed = 35: %s" % [str(x) for x in r])
    op("set", "leaveRefundPercent", "40", None, None, "yes", "console")
    settle()
    PURSE.clear()
    PURSE.update({str(uid(1)): 0, str(uid(2)): 5000})
    g = make_guild("new", "g1", "Kit Guild", "", [(1, 2, 0, 0), (2, 0, 0, 0)], lim=(-1, -1))
    GS.saveGuild(g)
    GS.deposit(uid(2), NAMES[2], "1000")
    r = str(GS.leave(uid(2), NAMES[2], True))
    check(r == "+You left Kit Guild. You got back 400 coins to your purse (40% of your contribution of 1,000); the rest stays in the bank."
          and PURSE[str(uid(2))] == 4400, "K. a leave then pays 40%%: %r" % r)
    capture(lambda: Pub.shutdown())
    print("K. Server Setup: 0.1.5's 14 rows + Leave refund (% of contribution) (bank, int 35, 0-100, step 5, %, live) after Largest "
          "guild bank; set 40 through the kit = live + the file line; 101 / -1 / abc refused; a leave pays 40%")


def main():
    for j in (JAR, OLD, COINS_JAR):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        print("--dir must be inside tools/dev/scratch/ (it is deleted afterwards):", SCRATCH)
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
    print("SkyyGuilds %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAIL", f[:600])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
