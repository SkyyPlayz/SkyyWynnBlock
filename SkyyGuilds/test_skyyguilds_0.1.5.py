"""SkyyGuilds 0.1.5 - bare-JVM harness: disband pays the guild bank back by contribution + the member list shows each member's
contribution (Skyy, OPEN-QUESTIONS.md LOCKED 2026-10-01). Derived from test_skyyguilds_0.1.4.py; copy it to the next version.

    python SkyyGuilds/test_skyyguilds_0.1.5.py [--jar <SkyyGuilds-0.1.5.jar>] [--old <SkyyGuilds-0.1.4.jar>] [--coins <SkyyCoins jar>]
                                               [--live <Skyy_SkyyGuilds folder>] [--dir <scratch>] [--keep]

Build first (python tools/guilds_0_1_5_patch.py, then python SkyyGuilds/build_skyyguilds_0.1.5.py). ONE JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; 0.1.4 (the live SET pin), 0.1.5 and the
real SkyyCoins 0.1.5 each in their own class loader; a fake Universe (Unsafe-allocated) holds the online players; the JVM-global
bridge map holds fake SkyyCoins / SkyySkills / SkyyProfiles functions, or the REAL SkyyCoins CoinFn objects in part R) checks:
  A  every class of the three jars loads, verifies (-Xverify:all) and initialises
  B  the contract in bytes, 0.1.4 -> 0.1.5: every class but Guild, GuildStore, GuildPage, SkyyGuildsPlugin, GADeleteCmd is
     byte-identical (XpTask, DayTask, GuildTick, the commands, GHooks, GMember ...); GCfg / CfgFn / CfgRows / manifest.json = 0.1.4's
     bytes once "0.1.5" is written back; SkyyGuildsPlugin = 0.1.4's bytes once its ready-log constant is swapped back (only the
     version and the page id differ); GADeleteCmd = 0.1.4's bytes once its description constant is swapped back; Guild: + the fields
     net / netSeed, only <init> changed; GuildStore: exactly the listed methods changed / new (javassist, constant-pool indices
     resolved), every other method instruction-identical; GuildPage: only the three view builders changed (the 1400 px width + the
     Contribution cell), infoLabel / build / handleDataEvent / colorOf ... instruction-identical
  C  XpTask (byte-identical) gives the same guild XP on both jars over a random walk
  P  the disband split GuildStore.payouts against a Python reference and by its rules: 60 / 40, Skyy's examples (+100,000 - 25,000 =
     75,000 and +2,000 - 5,000 = -3,000), one negative member, nobody positive = even split, the remainder to the biggest contributor
     (ties: rank, then join order), 1e15 coins (BigInteger), bank 0, 400 random guilds: the shares sum to the bank exactly, never
     negative, nothing for a net <= 0 while someone is positive, the remainder < the number of sharers
  Q  disbands end to end through the real GuildStore (deposit / withdraw build the nets, fake SkyyCoins): /guild disband with an
     offline member paid, nobody positive, /guildadmin delete, the last member's /guild leave (same purse + text as 0.1.4); the
     confirm and result texts; the archived file (disbanded, bank 0, one disband-payout line per share, net.* kept); REFUSED and
     nothing changed when a payee's purse is unreadable (pre-check); a payout failing on the first / second / last payee = every
     share paid so far taken back, the live file written again (not disbanded, same bank, same log), the guild still loaded, then
     a retry works; a share that cannot be taken back stays with its member as a logged disband-payout (bank lowered by it, their
     withdrawn total raised): the coins in purses + bank never change (no coin created or lost); 0.1.4 paid the Leader everything
  R  the REAL SkyyCoins 0.1.5 (CoinStore / CoinFn in their own loader, balance files in scratch, a stand-in profile:fn:key): an
     OFFLINE member whose active profile is p2 is paid into balances/<uuid>-p2.properties (profile 1's file untouched), online members
     into theirs; an unreadable balance file refuses the disband with every file byte-identical
  S  running totals: deposit / withdraw add, a withdraw SkyyCoins refuses takes its total back; the SEED from a scratch COPY of the
     live Skyy_SkyyGuilds data (GodSquad; the live folder is only read): the totals match the bank log, netSeed complete, the file
     gains net.* + netSeed; start twice = seeded once (no second seed line, netSeed unchanged); later moves keep counting; totals
     survive a trimmed log and a missing banklog.log; 0.1.4 loads a 0.1.5 file (rollback safe) and 0.1.5 seeds again after 0.1.4
     dropped the keys; a partial history says partial + the unmatched moves; a guild created by 0.1.5 is never seeded;
     /guildadmin info's bank line shows the seed status (not seeded / complete / partial + unmatched moves / new) - review fix 5
  V  the 0.1.5 review hardening: (1) the payout plan (every payee's name, uuid, share) is in the server log and in banklog.log
     (DISBAND-PAYOUT-START) BEFORE the first coins:fn:add, each share gets a PAID n/N line as it lands, then DONE (or CANCELLED on a
     rollback, naming a share that stayed); a snapshot at the 2nd payout (a crash there) holds the plan + exactly one PAID line;
     parseBankLine (backfill + seed) never reads a note as a move; bank 0 = no record; (2) the rollback rewrite of the live file is
     tried 3 times when a directory blocks the .tmp file, then a loud WARN names the guild id + bank, memory keeps the bank (dirty),
     flushDirty repairs the file once unblocked, a retry disbands; (4) every leave confirm of a member who is not the last names a
     positive contribution (Member without / Admin + Leader with the withdraw hint, the Leader's /guild leave), a Member's /guild leave
     with a positive contribution asks once first (nothing changed), then leaves (the bank keeps it, the totals stay); a zero /
     negative contribution = 0.1.4's texts and an immediate /guild leave
  D  differential page builds 0.1.4 vs 0.1.5 (the 0.1.4 harness states: not in a guild, Leader / Admin / Member views, pagers, armed
     buttons, log view, widest texts): identical bindings, b.set lines (+ only #SkyyGRowNet<i>), visible texts (+ only the
     Contribution head and the contribution cells), every 0.1.4 id kept; the 0.1.5 markup through check_markup / check_page /
     assert_proven, kit colours only, root 1400 x H and the body filled exactly, member rows within the list well; NEW states: the
     member list order (rank, then contribution highest first, then online, then name) and the numbers (75,000 / -3,000 ...) with
     negative cells in the kit's error red and the rest in the row value colour, the widest contribution texts, the new result texts,
     the widest leave confirms with the contribution note (review fix 4)
  E  clicks through handleDataEvent on both jars (two scripted sessions): identical result lines, keep boxes, views, armed actions,
     purses, guilds, invites, bindings and non-row b.set lines; the member rows of each jar match that jar's own documented order;
     the one intended difference, 0.1.5's leave note (Steve arming Leave with a positive contribution), is checked and stripped first
  F  text fit (SUI.text_width, the client's font tables): buttons, one-line boxes (+ the contribution cells), wrapped result lines
     (+ the new disband texts), titles, column heads
  G  the page id: GUILD_PAGE_ID of the kit's page now == GUILD_PAGE_CHECKED == the id in the jar's ready line
Not testable without the game: how the client draws the page, a live SkyyProfiles (stand-in key function), rebuild() on a live
page. Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/guilds015/harness, deleted
at the end unless --keep; TEMP / TMP and java.io.tmpdir point into it). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, random, collections, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.5", "0.1.4"
PKG = "com.skyy.guilds."
SCRIPT = os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION)
PREFIX = "SkyyG"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "guilds015", "harness")))
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
    print("A. loaded + verified + initialised (-Xverify:all): 0.1.4 %d, 0.1.5 %d, SkyyCoins 0.1.5 %d classes" % (
        COUNT["A old"], COUNT["A new"], COUNT["A coins"]))
    if FAILS:
        return

    # ---------------- B. the contract in bytes
    old_e, new_e = EN["old"], EN["new"]
    check(sorted(old_e) == sorted(new_e), "B. the same jar entries: %s" % sorted(set(old_e) ^ set(new_e)))
    P = "com/skyy/guilds/"
    CHANGED = set(P + n + ".class" for n in ("Guild", "GuildStore", "GuildPage", "SkyyGuildsPlugin", "GADeleteCmd"))
    VERSIONED = set(P + n + ".class" for n in ("GCfg", "CfgFn", "CfgRows")) | {"manifest.json"}
    for n in sorted(old_e):
        if n in CHANGED or n not in new_e:
            continue
        if n in VERSIONED:
            if check(new_e[n].replace(b"0.1.5", b"0.1.4") == old_e[n] and old_e[n] != new_e[n],
                     "B. %s = 0.1.4's bytes once the version string is swapped back" % n):
                COUNT["B versioned"] += 1
        elif check(old_e[n] == new_e[n], "B. %s is byte-identical to 0.1.4" % n):
            COUNT["B identical"] += 1
    check(old_e[P + "XpTask.class"] == new_e[P + "XpTask.class"], "B. XpTask is byte-identical (the 0.1.4 fix B unchanged)")
    plug = P + "SkyyGuildsPlugin.class"
    ok, t0, LOG_NEW = swap_back(old_e[plug], new_e[plug], b"] 0.1.4 ready (", b"] 0.1.5 ready (")
    check(ok, "B. SkyyGuildsPlugin = 0.1.4's bytes once the ready-log constant is swapped back")
    LOG_NEW = LOG_NEW or ""
    if t0:
        po = re.search(r"page ([0-9a-f]{12})\)", t0).group(1)
        pn = re.search(r"page ([0-9a-f]{12})\)", LOG_NEW)
        check(pn is not None and LOG_NEW == t0.replace("] 0.1.4 ready (", "] 0.1.5 ready (").replace("page %s)" % po, "page %s)" % pn.group(1)),
              "B. the ready line differs only by the version and the page id: %r" % LOG_NEW)
    ok, d0, d1 = swap_back(old_e[P + "GADeleteCmd.class"], new_e[P + "GADeleteCmd.class"], b"Admin: delete a guild", b"Admin: delete a guild")
    check(ok and d1 == "Admin: delete a guild (repeat to confirm; bank paid back to its members by contribution)",
          "B. GADeleteCmd = 0.1.4's bytes once its description is swapped back (%r -> %r)" % (d0, d1))
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
            ln = re.sub(r"#\d+ = ", "", str(IP.instructionString(it, it.next(), cp))).replace("ldc_w ", "ldc ")
            out.append(re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln))
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
        check(sorted(fields(co) + list(new_fields)) == fields(cn), "B. %s fields: 0.1.4's + %s" % (name, list(new_fields)))
        mo, mn = methods(co), methods(cn)
        gone = sorted(k.split("(")[0] for k in mo if k not in mn)
        new = sorted(k.split("(")[0] for k in mn if k not in mo)
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
        same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
        check(gone == sorted(gone_want), "B. %s: gone %s (want %s)" % (name, gone, gone_want))
        check(new == sorted(new_want), "B. %s: new %s (want %s)" % (name, new, new_want))
        check(changed == sorted(changed_want), "B. %s: changed %s (want exactly %s)" % (name, changed, sorted(changed_want)))
        for m in same_want:
            check(m in same, "B. %s.%s is instruction-identical to 0.1.4" % (name, m))
        return changed, same

    cmp_class("Guild", ["<init>"], [], [], ["seasonXp", "addSeason", "member", "leader"],
              new_fields=[("net", "Ljava/util/HashMap;"), ("netSeed", "Ljava/lang/String;")])
    GS_CHANGED = ["propsOf", "loadGuildFile", "loadAll", "create", "disbandWarning", "leave", "disband", "adminDelete", "adminHelp",
                  "adminInfo", "deposit", "withdraw", "cmpRow", "snapshot",
                  "leaveWarning"]                                       # review fix 4: the leave note
    GS_NEW = ["netOf", "netAdd", "netValue", "netText", "seedLine", "readBankLines", "seedNet", "payouts", "shareOf", "payees",
              "shareList", "disbandNow",
              "bankNote", "leaveNote", "seedText"]                      # review fixes 1, 4, 5
    gs_changed, gs_same = cmp_class("GuildStore", GS_CHANGED, ["disbandNow"], GS_NEW,
                                    ["addLog", "archive", "saveGuild", "parseBankLine", "backfillLogs", "invite", "accept", "kick",
                                     "promote", "demote", "transfer", "setLimit", "flushDirty", "removeMember", "successor", "addXp",
                                     "touch", "infoLines", "bankLines", "coinsAdd", "coinsTake", "coinsGet", "parseAmount", "logParts"])
    pg_changed, pg_same = cmp_class("GuildPage", ["buildNone", "buildGuild", "buildLog"], [], [],
                                    ["<init>", "safe", "jsonStr", "two", "build", "handleDataEvent", "colorOf", "infoLabel"])
    print("B. %d classes byte-identical to 0.1.4 (XpTask included), %d = 0.1.4 but the version string, SkyyGuildsPlugin / "
          "GADeleteCmd = 0.1.4 but one constant; Guild + net / netSeed; GuildStore: %d changed, %d new, %d instruction-identical; "
          "GuildPage changed %s (same: %s)" % (COUNT["B identical"], COUNT["B versioned"], len(gs_changed), len(GS_NEW), len(gs_same),
                                              pg_changed, ", ".join(pg_same)))

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
    HOOK = [None]                          # V: called as HOOK[0](uuid string, amount) at the start of every coins:fn:add

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
            if HOOK[0] is not None:
                HOOK[0](u, n)
            if PURSE.get(u, 0) is None or u in FAIL_ADD:
                return None
            PURSE[u] = PURSE.get(u, 0) + n
            return Long.valueOf(PURSE[u])

    @JImplements("java.util.function.Function")
    class CoinsTake:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            have = PURSE.get(u, 0)
            if have is None or u in FAIL_TAKE:
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
        p = Props()
        p.setProperty("xpSkills", str(Cfg.DEF_SKILLS))
        Cfg.parseSkills(p)
        BR.clear()
        for key, f in (("coins:fn:get", COINS[0]), ("coins:fn:add", COINS[1]), ("coins:fn:take", COINS[2])):
            BR.put(key, f)
        FAIL_ADD.clear()
        FAIL_TAKE.clear()
        HOOK[0] = None
        return GS, Cfg, X

    def logline(i, who, act, amount, bank):
        return "%d|%s|%s|%d|%d" % (NOW - (50 - i) * 3600000, who, act, amount, bank)

    def make_guild(k, gid, name, tag, members, xp=0, bank=0, log=(), lim=(-1, 0), nets=None):
        """members = [(n, rank, contrib, coins taken today)]; nets = {n: (deposited, withdrawn)} (0.1.5 only)"""
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
        if nets and k == "new":
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
        else:
            check(PURSE[str(uid(1))] == 5000 - 600 + 3000 and r.endswith("went to your purse."), "Q1. 0.1.4 paid the Leader everything: %r" % r)
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
          "Q4. last member leaves: the whole bank to their purse, texts = 0.1.4's: %s / %s" % (res_q4["old"], res_q4["new"]))
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
    print("R. real SkyyCoins 0.1.5: offline member paid into the active profile (p2) file, profile 1 untouched; an unreadable balance "
          "file refuses with every file unchanged")

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
    # S2: a scratch COPY of the live data (GodSquad) - the live folder is only read
    live_ok = os.path.isdir(LIVE) and os.path.isfile(os.path.join(LIVE, "guilds", "g1.properties"))
    if check(live_ok, "S2. the live Skyy_SkyyGuilds folder is readable at %s" % LIVE):
        cp = os.path.join(SCRATCH, "live-copy")
        shutil.rmtree(cp, ignore_errors=True)
        shutil.copytree(LIVE, cp)
        livep = jprops(os.path.join(cp, "guilds", "g1.properties"))
        bank_lines = [ln for ln in open(os.path.join(cp, "banklog.log"), encoding="utf8").read().splitlines() if " guild=g1 " in ln]
        want = collections.defaultdict(lambda: [0, 0])
        for ln in bank_lines:
            w = ln.split(" player=")[1].split()
            if w[-3] == "deposit":
                want[w[0].lower()][0] += int(w[-2])
            elif w[-3] in ("withdraw", "disband-payout"):
                want[w[0].lower()][1] += int(w[-2])
        names = dict((kk[7:], v.split("|")[3]) for kk, v in livep.items() if kk.startswith("member."))
        GS, Cfg, X = reset("new", "live", d=cp)
        _, out1 = capture(lambda: GS.loadAll())
        g = GS.GUILDS.get("g1")
        got = dict((names[u_], (int(g.net.get(u_)[0]), int(g.net.get(u_)[1])) if g.net.get(u_) is not None else (0, 0)) for u_ in names)
        wantd = dict((names[u_], tuple(want[names[u_].lower()])) for u_ in names)
        check(got == wantd, "S2. GodSquad seeded from the bank log: %s, want %s" % (got, wantd))
        check(sum(a - b for a, b in got.values()) == int(g.bank), "S2. the members' nets add up to the bank (%d)" % int(g.bank))
        seed1 = str(g.netSeed)
        check(re.fullmatch(r"\d+\|complete\|%d\|0" % len(bank_lines), seed1) is not None, "S2. netSeed says complete: %r" % seed1)
        check(out1.count("seeded once from its history") == 1 and "COMPLETE" in out1, "S2. one seed info line: %r" % out1[-400:])
        ai = [str(x) for x in GS.adminInfo("GodSquad")]
        check(re.search(r", bank %d coins \(contributions seeded \d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?Z from %d bank move\(s\) of its history: COMPLETE \(the history added up "
                        r"to the bank\)\)$" % (int(g.bank), len(bank_lines)), ai[1]) is not None,
              "V5. /guildadmin info shows the complete seed of the live copy: %r" % ai[1])
        COUNT["V5"] += 1
        print("S2. live GodSquad copy: %s; info: %s" % (got, [ln for ln in out1.splitlines() if "seeded once" in ln][0][:240] if "seeded once" in out1 else "?"))
        pp = jprops(os.path.join(cp, "guilds", "g1.properties"))
        check(pp.get("netSeed") == seed1 and all(pp.get("net." + u_) == "%d|%d" % got[names[u_]] for u_ in names if got[names[u_]] != (0, 0)),
              "S2. the copy's guild file gained net.* + netSeed")
        check(all(pp.get(kk) == v for kk, v in livep.items() if not kk.startswith("net")), "S2. every other key of the live file kept its value")
        # start twice: seeded once
        GS, Cfg, X = reset("new", "live", d=cp)
        _, out2 = capture(lambda: GS.loadAll())
        g = GS.GUILDS.get("g1")
        got2 = dict((names[u_], (int(g.net.get(u_)[0]), int(g.net.get(u_)[1])) if g.net.get(u_) is not None else (0, 0)) for u_ in names)
        check(str(g.netSeed) == seed1 and got2 == got and "seeded once" not in out2, "S2. start twice = seeded once (netSeed %r, %s)" % (str(g.netSeed), got2))
        # later moves keep counting; a restart keeps them
        PURSE.clear()
        wes = [u_ for u_ in names if names[u_] == "WesleyPlayz"]
        sky = [u_ for u_ in names if names[u_] == "SkyLordPlayz"]
        if check(len(wes) == 1 and len(sky) == 1, "S2. the live copy has SkyLordPlayz and WesleyPlayz"):
            UW, US = UUID.fromString(wes[0]), UUID.fromString(sky[0])
            PURSE[wes[0]], PURSE[sky[0]] = 10000, 10000
            check(str(GS.deposit(UW, "WesleyPlayz", "500")).startswith("+"), "S2. Wesley deposits 500 on the copy")
            GS, Cfg, X = reset("new", "live", d=cp)
            _, out3 = capture(lambda: GS.loadAll())
            g = GS.GUILDS.get("g1")
            check((int(g.net.get(wes[0])[0]), int(g.net.get(wes[0])[1])) == (got["WesleyPlayz"][0] + 500, got["WesleyPlayz"][1])
                  and "seeded once" not in out3, "S2. after a restart Wesley's later deposit is kept, no re-seed")
            # rollback: 0.1.4 loads the 0.1.5 file, saves it (drops net.* / netSeed), then 0.1.5 seeds again from the history
            GSo, Cfgo, Xo = reset("old", "live", d=cp)
            capture(lambda: GSo.loadAll())
            go = GSo.GUILDS.get("g1")
            check(go is not None and int(go.bank) == int(g.bank) and go.members.size() == g.members.size(), "S3. 0.1.4 loads the 0.1.5 file (rollback safe)")
            GSo.saveGuild(go)
            check(not any(kk.startswith("net") for kk in jprops(os.path.join(cp, "guilds", "g1.properties"))), "S3. 0.1.4's save drops net.* / netSeed")
            GS, Cfg, X = reset("new", "live", d=cp)
            _, out4 = capture(lambda: GS.loadAll())
            g = GS.GUILDS.get("g1")
            check("seeded once" in out4 and "COMPLETE" in out4 and (int(g.net.get(wes[0])[0]), int(g.net.get(wes[0])[1])) == (got["WesleyPlayz"][0] + 500, got["WesleyPlayz"][1]),
                  "S3. 0.1.5 seeds again after 0.1.4 dropped the keys - complete, Wesley's later deposit included (banklog.log has it)")
            # a trimmed log + no banklog.log: the running totals (file) still count every move
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
            # the GodSquad copy disbands by contribution
            nets_now = [(int(g.net.get(u_)[0]), int(g.net.get(u_)[1])) for u_ in [str(m.uuid) for m in g.members.values()]]
            ranks_now = [int(m.rank) for m in g.members.values()]
            want_sh = ref_pay(nets_now, int(g.bank), ranks_now, [int(m.joined) for m in g.members.values()])
            before = dict(PURSE)
            r = str(GS.disband(US, "SkyLordPlayz", True))
            paidv = [PURSE[str(m)] - before[str(m)] for m in [str(x.uuid) for x in g.members.values()]]
            check(paidv == want_sh and sum(paidv) == sum(want_sh), "S4. the GodSquad copy disbands by contribution: %s (%r)" % (paidv, r))
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
    print("S. running totals: deposit / withdraw / refused withdraw; the live copy seeded once (complete), start twice = once, later "
          "moves kept, 0.1.4 interop, a trimmed log + no banklog.log keep the totals, partial history reported, new guilds unseeded")

    # ---------------- V. the 0.1.5 review hardening (findings 1, 2, 4; 5 is checked in S)
    NOTE_LINE = re.compile(r"^\S+ guild=g1 \(Pay Guild\) DISBAND-PAYOUT-(START|PAID|DONE|CANCELLED)\b")

    def banklog(GS):
        f = os.path.join(str(GS.DIR.toString()), "banklog.log")
        return open(f, encoding="utf8").read().splitlines() if os.path.exists(f) else []

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
    # V4 (finding 4): the leave confirms name the positive contribution left in the bank
    LEAVE_MEM = [(1, 2, 0, 0), (2, 1, 0, 0), (3, 0, 0, 0), (4, 0, 0, 0), (5, 0, 0, 0)]
    plain = {}
    for k in ("old", "new"):
        GS, g = q_setup(k, "v4", {1: 5000, 2: 5000, 3: 5000, 4: 5000, 5: 5000}, [1, 2, 3], LEAVE_MEM, lim=(-1, 0))
        move(GS, 1, "dep", 600)
        move(GS, 2, "dep", 400)
        move(GS, 3, "dep", 1000)
        plain[k] = (str(GS.leaveWarning(uid(4))), str(GS.leave(uid(4), NAMES[4], False)))
        if k == "old":
            continue
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
    check(plain["new"] == plain["old"] and plain["new"] == ("=Click Leave again within 10 s to leave Pay Guild.", "+You left Pay Guild."),
          "V4. no contribution: the page confirm and /guild leave are 0.1.4's (%s / %s)" % (plain["old"], plain["new"]))
    print("V. review hardening: the payout plan in the server log + banklog.log before the first coin (START / PAID n/N / DONE | "
          "CANCELLED, never read as moves, a crash at the 2nd payout leaves the plan + 1 PAID line); the rollback save tried 3 times, "
          "a loud WARN with the id + bank, flushDirty repairs; leave confirms name a positive contribution (Member, Admin, Leader, "
          "/guild leave asks a Member first), zero / negative = 0.1.4; %d /guildadmin info seed lines (S)" % COUNT["V5"])

    # ---------------- D. differential page builds 0.1.4 vs 0.1.5 + the new member list
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
        so, sn = sets_of(co), sets_of(cn)
        extra, missing = sn - so, so - sn
        check(not missing and all(NEW_SET_RE.match(x[0]) for x in extra),
              "D. %s: b.set lines identical but #SkyyGRowNet<i>: missing %s, extra %s" % (tag, dict(missing), dict(extra)))
        nrows = sum(1 for x in sn if NEW_SET_RE.match(x[0]))
        check(sum(extra.values()) == nrows, "D. %s: one contribution cell per member row" % tag)
        COUNT["D sets"] += sum(so.values())
        to, tn = texts_of(co), texts_of(cn)
        allowed = collections.Counter(str(x[1]) for x in sn.elements() if NEW_SET_RE.match(x[0]) and str(x[1]))
        if view_of(cn) == "guild":
            allowed["Contribution"] += 1
        check(not (to - tn) and (tn - to) == allowed,
              "D. %s: visible texts identical but the Contribution head + cells: only 0.1.4 %s, only 0.1.5 %s (allowed %s)"
              % (tag, dict(to - tn), dict(tn - to), dict(allowed)))
        COUNT["D texts"] += sum(tn.values())
        io, inn = ids_of(co), ids_of(cn)
        check(io <= inn, "D. %s: 0.1.4 ids missing: %s" % (tag, sorted(io - inn)))
        check(all(re.fullmatch(r"SkyyGRowNet\d+", x) for x in inn - io), "D. %s: new ids only #SkyyGRowNet<i>: %s" % (tag, sorted(inn - io)))
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
            for k, (cc, ee) in (("0.1.4", res2["old"]), ("0.1.5", res2["new"])):
                has = any(sel == prev for typ, sel, data, lock in ee)
                check(has == (ptxt is not None), "D. %s %s: pager %s (want %s)" % (st[0], k, "shown" if has else "none", ptxt))
                if ptxt is not None:
                    txt = [str(js(d_)) for typ, sel, t, d_ in cc if sel in ("#SkyyGPageTxt.Text", "#SkyyGLPageTxt.Text")]
                    check(txt == [ptxt], "D. %s %s: pager text %s, want %s" % (st[0], k, txt, ptxt))
                rows = sum(1 for typ, sel, t, d_ in cc if is_append(typ) and sel == "#" + lst_id and re.fullmatch(r"SkyyGL?Row\d+", first_id(t)))
                if k == "0.1.5":
                    check(rows == nrows, "D. %s: %d rows in #%s, want %d" % (st[0], rows, lst_id, nrows))
                COUNT["D boundary"] += 1
    print("D. %d states x 2 jars: %d bindings identical, %d b.set lines identical (+ #SkyyGRowNet per row), %d visible texts, %d 0.1.4 "
          "ids kept; 0.1.5: %d markups through check_markup in %d check_page, %d colours audited, %d member rows measured" % (
              COUNT["D states"], COUNT["D bindings"], COUNT["D sets"], COUNT["D texts"], COUNT["D ids"], COUNT["D markups"],
              COUNT["D pages"], COUNT["D colours"], COUNT["D rows"]))

    # NEW (0.1.5 only): the member list order + numbers, the widest contribution texts, the new result texts
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
        pg, rank = setup_state("new", st)
        cmds, evs = build(pg)
        info = str(pg.info)
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
        if k == "old":
            key = lambda r_: (-int(r_[2]), 0 if r_[4] == "1" else 1, r_[1].lower())
        else:
            key = lambda r_: (-int(r_[2]), -int(r_[6]), 0 if r_[4] == "1" else 1, r_[1].lower())
        return rows == sorted(rows, key=key)

    # review fix 4: 0.1.5's leave confirms may end with this note (a positive contribution); everything else must match 0.1.4
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
                if k == "new":
                    mm = LEAVE_NOTE_RE.search(info_txt)
                    if mm:
                        mine = [r_ for r_ in (srows or []) if r_[0] == str(uid(who))]
                        check(len(mine) == 1 and int(mine[0][6]) > 0 and mm.group(1) == num(int(mine[0][6])) and a == "leave",
                              "E. %s: the leave note names the leaver's own contribution: %r (%s)" % (name, info_txt, mine))
                        E_NOTES.append((name, NAMES.get(who), a, info_txt))
                    info_txt = LEAVE_NOTE_RE.sub("", info_txt)
                snap = (who, a, payload, info_txt, str(pg.keepName), str(pg.keepInvite), str(pg.keepAmount), str(pg.keepLimit),
                        int(pg.view), int(pg.pageNo), int(pg.logPage), str(pg.confirm), tuple(sorted(PURSE.items())), guild_state(k))
                nonrow = collections.Counter()
                for x, c in sets_of(cmds).items():
                    if not ROW_SEL_RE.match(x[0] or ""):
                        nonrow[(x[0], LEAVE_NOTE_RE.sub("", x[1]) if k == "new" else x[1])] += c
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
                out.append((snap, nonrow, evs, rk, sorted(tuple(r_[:6]) for r_ in (srows or []))))
                if k == "new":
                    r = jc(k, "GuildStore").rankOf(uid(who))
                    check_new("E %s after %s %r" % (name, a, payload), cmds, evs, int(r) if int(r) >= 0 and int(pg.view) == 0 else None)
            trace[k] = out
        for (so, eo_sets, eo_ev, rko, mo), (sn, en_sets, en_ev, rkn, mn) in zip(trace["old"], trace["new"]):
            check(so == sn, "E. %s: after %s %r: 0.1.4 %s\n  0.1.5 %s" % (name, so[1], so[2], so[3:12], sn[3:12]))
            check(eo_sets == en_sets, "E. %s: after %s %r: rebuilt page non-row b.set lines differ %s / %s"
                  % (name, so[1], so[2], dict(eo_sets - en_sets), dict(en_sets - eo_sets)))
            check(eo_ev == en_ev, "E. %s: after %s %r: rebuilt page bindings differ" % (name, so[1], so[2]))
            check(rko == rkn and mo == mn, "E. %s: after %s %r: the same member rows (ranks per row, member data)" % (name, so[1], so[2]))
        COUNT["E done"] += len([s_ for s_, _x, _y, _r, _m in trace["new"] if s_[3].startswith("+")])
        return trace

    A_, G_, I_, L_ = "@GAmount", "@GName", "@GInvite", "@GLimit"
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
    check(len(E_NOTES) == 1 and E_NOTES[0][:3] == ("guild life", "Steve", "leave")
          and E_NOTES[0][3].endswith(" - withdraw first if you want coins back."),
          "E. exactly one leave note: Steve (an Admin by then, net > 0, Admin limit 5k) arming Leave in 'guild life': %s" % E_NOTES)
    print("E. %d clicks (2 sessions x 2 jars), %d successful actions, identical results / boxes / views / purses / guilds / bindings / "
          "non-row b.set lines (0.1.5's leave note stripped: %d, %r); %d member rows in each jar's own documented order"
          % (COUNT["E clicks"], COUNT["E done"], len(E_NOTES), E_NOTES[0][3] if E_NOTES else "", COUNT["E rows"]))

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
                      "PAGE_CHECKED = %r in tools/guilds_0_1_5_patch.py, regenerate and rebuild" % (pid, chk, pid))
    print("G. page id %s, checked %s, kit %s" % (pid, chk, SUI.kit_id()))


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
