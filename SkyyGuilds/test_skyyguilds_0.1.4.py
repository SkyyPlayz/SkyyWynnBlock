"""SkyyGuilds 0.1.4 - bare-JVM harness for the look-only restyle of GuildPage on the shared UI kit tools/skyyui.py + the xpSkills fix.
The first SkyyGuilds harness in the repo; copy it to the next version and keep it passing.

    python SkyyGuilds/test_skyyguilds_0.1.4.py [--jar <SkyyGuilds-0.1.4.jar>] [--old <SkyyGuilds-0.1.3.jar>] [--dir <scratch>] [--keep]

Build first (python tools/guilds_0_1_4_patch.py, then python SkyyGuilds/build_skyyguilds_0.1.4.py). ONE JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar on the classpath; EACH SkyyGuilds jar in its own class loader,
so 0.1.3 - the live SET pin - and 0.1.4 run side by side; a fake Universe (Unsafe-allocated) holds the online players, the JVM-global
bridge map holds fake SkyyCoins / SkyySkills / SkyyProfiles functions) checks:
  A  every class of both jars loads, verifies and initialises
  B  the contract in bytes: every class but GuildPage, XpTask, SkyyGuildsPlugin, GCfg, CfgFn, CfgRows is byte-identical to 0.1.3;
     GCfg / CfgFn / CfgRows / manifest.json = 0.1.3's bytes once "0.1.4" is written back as "0.1.3" (the embedded version string);
     SkyyGuildsPlugin = 0.1.3's bytes once its ready-log constant is swapped back (the new one names the kit and the page id);
     GuildPage (javassist, constant-pool indices resolved, ldc / ldc_w + branch offsets normalised): the same fields, only infoLabel / buildNone / buildGuild / buildLog
     changed, style gone, colorOf new (only the kit's colour method - its textOf is not compiled, review 2026-09-29), <init> / safe /
     jsonStr / two / build / handleDataEvent instruction-identical;
     XpTask: the same fields, only check changed, totals / skillKey / stepSkills new
  C  FIX B (xpSkills changed while the server runs), both jars through the real XpTask.check + GCfg.reloadSkills / parseSkills with a
     fake skill:fn:xp: the 0.1.3 bug reproduced (an added skill's saved XP credited at once - 500,000 guild XP, and 1,000,000 at the
     xpMaxPerCheck cap; a removed skill swallowing the other skills' gains; a re-added skill crediting everything it earned while
     off the list; an unknown future skill name the same) and fixed in 0.1.4 (0 credited, only later gains count), and 0.1.4 ==
     0.1.3 where nothing changes (an unchanged list over a 60-step random walk with fractions and decreases, an alias rename on the
     same SkyySkills slot, a profile switch, two members, the level fallback without skill:fn:xp)
  D  differential page builds, 0.1.3 vs 0.1.4, with the engine's own UICommandBuilder / UIEventBuilder, in the not-in-a-guild view
     (no invite / an invite / results), the guild view (Leader / Admin / Member, 1 and 2+ member pages and a clamped page number, armed
     kick / make leader / leave / disband, withdraw allowed or not, day unknown, long names and big numbers, empty log, 0 XP) and the
     log view (empty, 1 page, 3 pages, the last page, a clamped page) + the pager boundaries (review 2026-09-29: an Admin with a
     member pager on both pages, a Leader with exactly 7 members = no pager, a Leader on page 2 of 8 members, a Member on page 2,
     15 log moves = no pager, 16 moves on page 2, a Member viewing the log) + the widest texts (review 2: 16-letter names of W / m,
     500 members online, xpSharePercent 1000, a 13-digit guild XP, 1e15 coins; guild view, log view, invite): identical event bindings (type, selector, EventData, lock flag,
     order); identical b.set lines (+ the one disclosed new b.set #SkyyGLimLbl = "Set a daily limit:", text that was inline in
     0.1.3); identical visible texts (inline + b.set) but the two disclosed armed labels ("Sure?" -> "Sure", "Confirm?" ->
     "Confirm"); every 0.1.3 element id still created; the 0.1.4 markup as the client gets it: SUI.check_markup on every append (the
     first = the page root), SUI.check_page, every b.set AFTER its element's append (command order), every binding on an existing
     element, only kit colours, SUI.assert_proven (no FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Center, Right, Full,
     nothing UNVERIFIED), the root size and the body filled exactly (the outer heights read back out of the markup), every member
     row within the list well and its panel the width the viewer's rank gives; the result line coloured by its mark (kit colours);
     the rank text colours Leader gold / Admin info blue / Member value, one colour per rank, three different colours
  E  clicks through the real handleDataEvent on both jars (its rebuild() fails harmlessly outside a server and is caught by the page)
     in two scripted sessions (a solo leader's whole guild life with a second player: create, amounts, deposit / withdraw, limits,
     invite / decline / accept, kick / promote / demote / make leader with their second click, the log pages, leave, disband with the
     payout; a 12-member guild: member pages, a kick, a Member's limited withdrawals): after every click identical result line, keep
     boxes, view / page numbers, armed action, purses, guilds (bank, xp, limits, members + ranks + day counts, log), invites, and the
     rebuilt page's b.set lines + bindings (and the rebuilt 0.1.4 page passes every D markup check)
  F  text fit with the client's font tables (SUI.text_width; read-only): every button label fits its button minus 2 x its padding,
     every seen one-line text fits its box, every wrapped text fits its lines, the window titles fit the title bar, the column
     heads fit their columns, and the widest states really showed the widest texts the build's guild_fits() asserts (review 2)
  G  the page id: GUILD_PAGE_ID of the kit's page NOW == GUILD_PAGE_CHECKED in the generated script == the id in the jar's ready line
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the page, the textures / sounds, the real
PageManager, rebuild() on a live page, a real SkyySkills. Nothing is deployed and nothing outside the scratch folder is written
(default tools/dev/scratch/test-guilds-014, deleted at the end unless --keep; TEMP / TMP and java.io.tmpdir point into it).
Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, struct, zipfile, random, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.4", "0.1.3"
PKG = "com.skyy.guilds."
SCRIPT = os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION)
PREFIX = "SkyyG"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "test-guilds-014")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGuilds-%s.jar" % OLD_VERSION)))
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


# ------------------------------------------------------------------------------------------------ markup helpers (no JVM)
TEXT_RE = re.compile(r'(?<![A-Za-z])Text: "((?:[^"\\]|\\.)*)"')
ID_RE = re.compile(r"#([A-Za-z0-9_]+)\s*\{")
COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")
WHEN_RE = re.compile(r"\d\d-\d\d \d\d:\d\d")
LEFT_RE = re.compile(r"\d+:\d\d left")
DISCLOSED = {"Sure?": "Sure", "Confirm?": "Confirm"}          # the armed labels (kit rule: button text is proven text only)
NEW_SETS = {"#SkyyGLimLbl.Text": "Set a daily limit:"}        # 0.1.3 inline text, b.set in 0.1.4 (it has a ':')
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


def texts_of(cmds, old=False):
    out = collections.Counter()
    for typ, sel, text, data in cmds:
        if is_append(typ):
            for t in TEXT_RE.findall(text or ""):
                if t:
                    out[norm(DISCLOSED.get(t, t) if old else t)] += 1
        elif sel and sel.endswith(".Text"):
            v = str(js(data))
            if v:
                out[norm(v)] += 1
    return out


def ids_of(cmds):
    return set(i for typ, sel, text, data in cmds if is_append(typ) for i in ID_RE.findall(text or ""))


def first_id(text):
    """the id of the first element of an append's markup ("" when it has none)"""
    m = ID_RE.search(text or "")
    return m.group(1) if m else ""


# ------------------------------------------------------------------------------------------------ the JVM part
def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
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
    EN = {"old": entries(OLD), "new": entries(JAR)}
    CLS = dict((k, dict((n[:-6].replace("/", "."), b) for n, b in EN[k].items() if n.endswith(".class"))) for k in EN)

    # ---------------- A. load + verify + init, both jars
    for k in ("old", "new"):
        for n in sorted(CLS[k]):
            try:
                Cls.forName(n, True, L[k])
                COUNT["A " + k] += 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    OKS[0] += COUNT["A old"] + COUNT["A new"]
    print("A. loaded + verified + initialised (-Xverify:all): 0.1.3 %d, 0.1.4 %d classes" % (COUNT["A old"], COUNT["A new"]))
    if FAILS:
        return

    # ---------------- B. the contract in bytes
    old_e, new_e = EN["old"], EN["new"]
    check(sorted(old_e) == sorted(new_e), "B. the same jar entries: %s" % sorted(set(old_e) ^ set(new_e)))
    P = "com/skyy/guilds/"
    LOOKFIX = set(P + n + ".class" for n in ("GuildPage", "XpTask", "SkyyGuildsPlugin"))
    VERSIONED = set(P + n + ".class" for n in ("GCfg", "CfgFn", "CfgRows")) | {"manifest.json"}
    for n in sorted(old_e):
        if n in LOOKFIX or n not in new_e:
            continue
        if n in VERSIONED:
            if check(new_e[n].replace(b"0.1.4", b"0.1.3") == old_e[n] and old_e[n] != new_e[n],
                     "B. %s = 0.1.3's bytes once the version string is swapped back" % n):
                COUNT["B versioned"] += 1
        elif check(old_e[n] == new_e[n], "B. %s is byte-identical to 0.1.3" % n):
            COUNT["B identical"] += 1
    plug = P + "SkyyGuildsPlugin.class"
    ro = [e for e in cp_utf8(old_e[plug]) if b"] 0.1.3 ready" in e[2]]
    rn = [e for e in cp_utf8(new_e[plug]) if b"] 0.1.4 ready" in e[2]]
    LOG_NEW = ""
    if check(len(ro) == 1 and len(rn) == 1, "B. one ready-log constant in each SkyyGuildsPlugin"):
        s0, e0, t0 = ro[0]
        s1, e1, t1 = rn[0]
        check(new_e[plug][:s1] + old_e[plug][s0:e0] + new_e[plug][e1:] == old_e[plug],
              "B. SkyyGuildsPlugin = 0.1.3's bytes once the ready-log constant is swapped back")
        LOG_NEW = t1.decode("utf8")
        check(t1.decode("utf8") == t0.decode("utf8").replace("] 0.1.3 ready - ", "] 0.1.4 ready (%s) - " % re.search(r"\((skyyui [^)]*)\)", LOG_NEW).group(1))
              if re.search(r"\((skyyui [^)]*)\)", LOG_NEW) else False, "B. the ready line only gains (kit, page): %r" % LOG_NEW)
        check(re.search(r"\] 0\.1\.4 ready \(skyyui [0-9.]+ [0-9a-f]{12}, page [0-9a-f]{12}\) - ", LOG_NEW) is not None,
              "B. the ready line names the kit and the page id: %r" % LOG_NEW)
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
            # constant-pool indices resolved; ldc / ldc_w and branch offsets normalised (a constant pool that grew or shrank - here:
            # style() gone, the kit's markup strings new - moves a string between ldc and ldc_w, and every later offset by a byte)
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

    def cmp_class(name, changed_ok, gone_want, new_want, same_want):
        co, cn = ct(old_e[P + name + ".class"]), ct(new_e[P + name + ".class"])
        check(fields(co) == fields(cn), "B. %s fields unchanged" % name)
        mo, mn = methods(co), methods(cn)
        gone = sorted(k.split("(")[0] for k in mo if k not in mn)
        new = sorted(k.split("(")[0] for k in mn if k not in mo)
        changed = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] != mn[k])
        same = sorted(k.split("(")[0] for k in mo if k in mn and mo[k] == mn[k])
        check(gone == sorted(gone_want), "B. %s: gone %s (want %s)" % (name, gone, gone_want))
        check(new == sorted(new_want), "B. %s: new %s (want %s)" % (name, new, new_want))
        check(set(changed) <= set(changed_ok), "B. %s: changed %s (allowed %s)" % (name, changed, changed_ok))
        for m in same_want:
            check(m in same, "B. %s.%s is instruction-identical to 0.1.3" % (name, m))
        return changed, same

    pg_changed, pg_same = cmp_class("GuildPage", ("infoLabel", "buildNone", "buildGuild", "buildLog"), ["style"], ["colorOf"],
                                    ["<init>", "safe", "jsonStr", "two", "build", "handleDataEvent"])
    xp_changed, xp_same = cmp_class("XpTask", ("check",), [], ["totals", "skillKey", "stepSkills"],
                                    ["<init>", "total", "levels", "step", "share", "run", "<clinit>"])
    check(xp_changed == ["check"], "B. XpTask: exactly check() changed: %s" % xp_changed)
    print("B. %d classes byte-identical, %d = 0.1.3 but the version string, SkyyGuildsPlugin = 0.1.3 but its ready constant; GuildPage "
          "changed %s (same: %s); XpTask changed %s, new totals / skillKey / stepSkills" % (
              COUNT["B identical"], COUNT["B versioned"], pg_changed, ", ".join(pg_same), xp_changed))

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
             12: "Kai", 13: "Lumberjackmaster", 14: "Abcdefghijklmnop",
             # review 2 (finding 5): the widest 16-letter names (W = the widest letter; m = the widest after W, for "(you)")
             15: "m" * 16, 16: "W" * 16}

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

    XP = {}            # uuid str -> {slot or "n:<name>": skill XP}
    SLOT = {}          # lower-case name -> SkyySkills slot (GCfg.SK_NAMES / SK_SLOTS)
    PKEY = {}

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
    check(list(jc("old", "GCfg").SK_NAMES) == list(Cfg0.SK_NAMES), "C. both jars read the same SkyySkills name table")
    NOW = int(System.currentTimeMillis())
    DAY = 1234

    def reset(k, tag, day_known=True):
        GS, Cfg, X = jc(k, "GuildStore"), jc(k, "GCfg"), jc(k, "XpTask")
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
        return GS, Cfg, X

    def logline(i, who, act, amount, bank):
        return "%d|%s|%s|%d|%d" % (NOW - (50 - i) * 3600000, who, act, amount, bank)

    def make_guild(k, gid, name, tag, members, xp=0, bank=0, log=(), lim=(-1, 0)):
        """members = [(n, rank, contrib, coins taken today)]"""
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
        GS.GUILDS.put(gid, g)
        GS.BYNAME.put(name.lower(), gid)
        return g

    # ---------------- C. FIX B: xpSkills changed while the server runs
    def xp_env(k, skills, xp, members=((1, 2, 0, 0),), fallback=False):
        GS, Cfg, X = reset(k, "xp")
        make_guild(k, "g1", "Xp Guild", "XP", list(members))
        XP.clear()
        for u, d in xp.items():
            XP[str(uid(u))] = dict(d)
        PKEY.clear()
        if not fallback:
            BR.put("skill:fn:xp", SKILLFN)
        set_list(k, skills, via_file=True)
        return GS, Cfg, X

    def set_list(k, skills, via_file=False):
        Cfg = jc(k, "GCfg")
        if via_file:           # the config kit's own reload routine for the xpSkills row (Server Setup / /guildadmin set / a hand edit)
            open(str(Cfg.FILE.toString()), "w", encoding="utf8").write("# test\nxpSkills=%s\n" % skills)
            Cfg.reloadSkills()
        else:
            p = Props()
            p.setProperty("xpSkills", skills)
            Cfg.parseSkills(p)

    def xp_check(k, n=1):
        return int(jc(k, "XpTask").check(uid(n)))

    def guild_xp(k, gid="g1"):
        return int(jc(k, "GuildStore").GUILDS.get(gid).xp)

    def scenario(name, steps, want):
        """steps: a list of ("xp", n, slot, +d) / ("set", list, via_file) / ("check", n) / ("prof", n, key) / ("levels", n, text)
        run on both jars; want = {"old": [gains of each check], "new": [...]} (None = the two jars must agree)"""
        got = {}
        for k in ("old", "new"):
            env = steps[0]
            xp_env(k, env[1], env[2], env[3] if len(env) > 3 else ((1, 2, 0, 0),), env[4] if len(env) > 4 else False)
            gains = []
            for st in steps[1:]:
                if st[0] == "xp":
                    d = XP.setdefault(str(uid(st[1])), {})
                    d[st[2]] = d.get(st[2], 0) + st[3]
                elif st[0] == "set":
                    set_list(k, st[1], st[2])
                elif st[0] == "check":
                    before = guild_xp(k)
                    r = xp_check(k, st[1])
                    check(r == guild_xp(k) - before, "C. %s %s: check() returns what it added" % (name, k))
                    gains.append(r)
                elif st[0] == "prof":
                    PKEY[str(uid(st[1]))] = st[2]
                    BR.put("profile:fn:key", PROFFN)
                elif st[0] == "levels":
                    BR.put("skill:" + str(uid(st[1])), st[2])
            got[k] = gains
        if want is None:
            check(got["old"] == got["new"], "C. %s: 0.1.4 == 0.1.3 %s / %s" % (name, got["old"], got["new"]))
        else:
            check(got["old"] == want["old"], "C. %s: 0.1.3 (the bug) %s, want %s" % (name, got["old"], want["old"]))
            check(got["new"] == want["new"], "C. %s: 0.1.4 (fixed) %s, want %s" % (name, got["new"], want["new"]))
        COUNT["C scenarios"] += 1
        return got

    MIN, FOR, ARC = 0, 1, 5
    res = {}
    res["added"] = scenario("added skill", [
        ("env", "Mining", {1: {MIN: 1000, FOR: 5000000}}),
        ("check", 1), ("xp", 1, MIN, 500), ("check", 1),
        ("set", "Mining,Foraging", True), ("check", 1),                   # the admin adds Foraging while the server runs
        ("xp", 1, MIN, 100), ("xp", 1, FOR, 300), ("check", 1)],
        {"old": [0, 50, 500000, 40], "new": [0, 50, 0, 40]})
    res["cap"] = scenario("added skill, 50m saved XP (the xpMaxPerCheck cap)", [
        ("env", "Mining", {1: {MIN: 0, FOR: 50000000}}),
        ("check", 1), ("set", "Mining,Foraging", True), ("check", 1), ("xp", 1, FOR, 1234), ("check", 1)],
        {"old": [0, 1000000, 123], "new": [0, 0, 123]})
    res["removed"] = scenario("removed + re-added skill", [
        ("env", "Mining,Foraging", {1: {MIN: 1000, FOR: 2000}}),
        ("check", 1),
        ("xp", 1, MIN, 1000), ("xp", 1, FOR, 200), ("set", "Mining", True), ("check", 1),     # removed: Mining's gain must count
        ("xp", 1, FOR, 500), ("xp", 1, MIN, 10), ("check", 1),                               # Foraging off the list: not counted
        ("set", "Mining,Foraging", False), ("check", 1),                                     # added again: no retroactive credit
        ("xp", 1, FOR, 100), ("check", 1)],
        {"old": [0, 0, 1, 270, 10], "new": [0, 100, 1, 0, 10]})
    res["unknown"] = scenario("added future skill name (SkyySkills answers it, not in the table)", [
        ("env", "Mining", {1: {MIN: 10, "n:fishing": 7000}}),
        ("check", 1), ("set", "Mining,Fishing", False), ("check", 1), ("xp", 1, "n:fishing", 50), ("check", 1)],
        {"old": [0, 700, 5], "new": [0, 0, 5]})
    res["alias"] = scenario("alias rename on the same SkyySkills slot (Archery -> Archer)", [
        ("env", "Archery", {1: {ARC: 1000}}),
        ("check", 1), ("xp", 1, ARC, 100), ("set", "Archer", False), ("check", 1), ("xp", 1, ARC, 7), ("check", 1)], None)
    check(res["alias"]["new"] == [0, 10, 0], "C. alias rename: the slot keeps its baseline in 0.1.4 %s" % res["alias"]["new"])
    rnd = random.Random(14)
    walk = [("env", "Mining,Foraging,Farming,Archery,Sorcery,Fury,Divinity",
             {1: {0: 500, 1: 900, 2: 0, 5: 12345, 9: 7, 14: 0, 15: 3}, 2: {0: 40, 1: 1, 2: 2}}, ((1, 2, 0, 0), (2, 0, 0, 0)))]
    for _ in range(60):
        who = rnd.choice((1, 2))
        for _j in range(rnd.randint(0, 3)):
            walk.append(("xp", who, rnd.choice((0, 1, 2, 5, 9, 14, 15)), rnd.choice((1, 3, 7, 13, 29, 101, 997, -5, 40000))))
        walk.append(("check", who))
    res["walk"] = scenario("unchanged list, 60-step random walk (fractions, decreases, two members)", walk, None)
    check(sum(res["walk"]["new"]) > 0, "C. the random walk credited guild XP (%d)" % sum(res["walk"]["new"]))
    res["profile"] = scenario("profile switch (a new baseline key)", [
        ("env", "Mining", {1: {MIN: 100}}), ("prof", 1, "p1"),
        ("check", 1), ("xp", 1, MIN, 100), ("check", 1), ("prof", 1, "p2"), ("xp", 1, MIN, 5000), ("check", 1), ("xp", 1, MIN, 30),
        ("check", 1)], None)
    check(res["profile"]["new"] == [0, 10, 0, 3], "C. profile switch: 0 at the new profile's first check %s" % res["profile"]["new"])
    res["fallback"] = scenario("level fallback (no skill:fn:xp) + a list change", [
        ("env", "Mining", {}, ((1, 2, 0, 0),), True), ("levels", 1, "Mining:5,Foraging:3"),
        ("check", 1), ("levels", 1, "Mining:6,Foraging:4"), ("check", 1), ("set", "Mining,Foraging,Farming", True),
        ("levels", 1, "Mining:6,Foraging:5,Farming:1"), ("check", 1)], None)
    check(res["fallback"]["new"] == [0, 50, 50], "C. level fallback unchanged %s" % res["fallback"]["new"])
    print("C. fix B: %d scenarios on both jars; 0.1.3 credited an added skill %s / %s guild XP (cap) at once, 0.1.4 %s / %s; removed + "
          "re-added 0.1.3 %s vs 0.1.4 %s; unchanged lists identical (random walk %d checks, %d guild XP)" % (
              COUNT["C scenarios"], res["added"]["old"][2], res["cap"]["old"][1], res["added"]["new"][2], res["cap"]["new"][1],
              res["removed"]["old"], res["removed"]["new"], len(res["walk"]["new"]), sum(res["walk"]["new"])))

    # ---------------- D. differential page builds
    ALLOWED = set(SUI.allowed_colors())
    VIEWS = K["GUILD_PAGE"]["views"]
    H = {"none": VIEWS["none"][0].h, "guild": VIEWS["guild"][0].h, "log": VIEWS["log"][0].h}
    INNER = K["GUILD_IN"]
    PW = K["GUILD_PW"]
    IDS013 = K["GUILD_IDS_013"]
    SEEN = collections.defaultdict(set)          # label id -> texts seen (F)
    RANKCOL = collections.defaultdict(set)       # rank name -> the text colours its row label had
    BUTTONS = {}                                 # button markup text -> (text seen)

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
        sets = sets_of(cmds)
        if h == H["none"]:
            return "none"
        return "log" if any(k[0] == "#SkyyGLogTitle.Text" for k in sets) else "guild"

    def check_new(tag, cmds, evs, my=None):
        """the 0.1.4 page as the client gets it (D5)"""
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
                for m in re.finditer(r'Label #(\w+) \{[^{}]*\}', text):
                    COUNT["D labels"] += 1
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
        # member rows: the panel is the width the viewer's rank gives, panel + buttons within the list well
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
        # the rank text colour of every member row (review 2026-09-29: Admin info blue, not accentHover - too close to Member's value)
        rank_txt = dict((i, v) for i, pr, v in ap.sets if pr == "Text" and i.startswith("SkyyGRowRank"))
        for p, t in ap:
            if p == "SkyyGList":
                for m in re.finditer(r"Label #(SkyyGRowRank\d+) \{[^{}]*?TextColor: (#[0-9A-Fa-f]{6})", t):
                    if check(m.group(1) in rank_txt, "D. %s: #%s has its rank text" % (tag, m.group(1))):
                        RANKCOL[rank_txt[m.group(1)]].add(SUI.norm_color(m.group(2)))
                        COUNT["D rank colours"] += 1
        info = [t for p, t in ap if "Label #SkyyGInfo " in t]
        if check(len(info) == 1, "D. %s: one result line" % tag):
            col = re.search(r"TextColor: (#[0-9A-Fa-f]{6})", info[0]).group(1)
            txt = [v for i, pr, v in ap.sets if i == "SkyyGInfo"]
            COUNT["D info " + col] += 1
            return col, txt
        return None, None

    def compare(tag, co, eo, cn, en, my=None, info=""):
        check(eo == en, "D. %s: event bindings identical (%d / %d)%s" % (tag, len(eo), len(en), "" if eo == en else "\n  0.1.3 %s\n  0.1.4 %s" % (eo, en)))
        COUNT["D bindings"] += len(en)
        so, sn = sets_of(co), sets_of(cn)
        extra = sn - so
        missing = so - sn
        check(not missing and all(k in NEW_SETS.items() for k in extra),
              "D. %s: b.set lines identical but the disclosed new one: missing %s, extra %s" % (tag, dict(missing), dict(extra)))
        COUNT["D sets"] += sum(so.values())
        to, tn = texts_of(co, old=True), texts_of(cn)
        check(to == tn, "D. %s: visible texts identical (the 2 armed labels disclosed): only 0.1.3 %s, only 0.1.4 %s" % (tag, dict(to - tn), dict(tn - to)))
        COUNT["D texts"] += sum(tn.values())
        io, inn = ids_of(co), ids_of(cn)
        check(io <= inn, "D. %s: 0.1.3 ids missing: %s" % (tag, sorted(io - inn)))
        COUNT["D ids"] += len(io)
        col, txt = check_new(tag, cn, en, my)
        want = SUI.STATUS.get(info[:1], SUI.COLOR["text"]) if info else SUI.COLOR["text"]
        if col is not None:
            check(col == want, "D. %s: result line colour %s for %r, want %s" % (tag, col, info[:20], want))

    LOG40 = [logline(i, NAMES[1 + i % 4], ("deposit", "withdraw", "limit-admin", "limit-member", "disband-payout")[i % 5],
                     (i + 1) * 137 if i % 5 < 2 else (-1 if i % 5 == 2 else (0 if i % 5 == 3 else 5000)), 100000 + i * 11) for i in range(40)]
    WIDE_XP, WIDE_COINS = 9999990000000, 10 ** 15     # review 2: GuildStore.fmt -> "9999.99b"; maxBank's highest value (1e15)
    M12 = [(1, 2, 12345, 0), (2, 1, 900, 1500), (3, 1, 0, 0), (4, 0, 77, 200), (5, 0, 5, 0), (6, 0, 0, 0), (7, 0, 1234567, 0),
           (8, 0, 3, 0), (9, 0, 0, 999), (10, 0, 44, 0), (11, 0, 0, 0), (12, 0, 999999999, 0)]
    # (name, viewer, online, guild fixture or None, page fields, day known)
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
        # the pager boundaries (review 2026-09-29; per = 7 members / 15 log moves are fixed in the Java)
        ("admin 12 page 1", 3, [1, 3, 5], ("g1", "Skyy Guild", "SKY", M12), {"lim": (5000, 0), "log": LOG40[:4]}, True),
        ("admin 12 page 2", 3, [1, 3, 5], ("g1", "Skyy Guild", "SKY", M12), {"lim": (5000, 0), "pageNo": 1, "log": LOG40[:4]}, True),
        ("leader exactly 7 members", 1, [1, 2, 3, 4, 5, 6, 7], ("g1", "Skyy Guild", "SKY", M12[:7]), {"xp": 4321, "log": LOG40[:3]}, True),
        ("leader page 2 of 8 members", 1, [1, 8], ("g1", "Skyy Guild", "SKY", M12[:8]), {"pageNo": 1, "log": LOG40[:1]}, True),
        ("member page 2", 5, [5, 12], ("g1", "Skyy Guild", "SKY", M12), {"pageNo": 1, "lim": (-1, 2000)}, True),
        ("log 15 moves", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40[:15]}, True),
        ("log 16 moves page 2", 1, [1], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0)]), {"view": 1, "log": LOG40[:16], "logPage": 1}, True),
        ("member views the log", 5, [1, 5], ("g1", "Skyy Guild", "SKY", [(1, 2, 0, 0), (5, 0, 0, 300)]),
         {"view": 1, "log": LOG40[:20], "lim": (-1, 2000)}, True),
        # review 2 (finding 5): the widest texts at the config maxima, made by the real Java - you = 16 x m (the Leader, "  (you)"),
        # an Admin named 16 x W, 500 members all online, xpSharePercent 1000, a 13-digit guild XP and contributions, 1e15 coins in
        # the bank, taken today and both limits; the log view with 16 x W / 16 x m players and 1e15 amounts; an invite from 16 x W
        # to a 24-letter guild of 500 members
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
        if "share" in f:               # review 2: xpSharePercent at its maximum (the XP caption at its widest)
            Cfg.SHARE = f["share"]
        set_online(online)
        rank = None
        if gfix is not None:
            gid, gname, tag, mem = gfix
            if f.get("invite") is None or gid == "g1":
                make_guild(k, gid, gname, tag, mem, f.get("xp", 0), f.get("bank", 0), f.get("log", ()), f.get("lim", (-1, 0)))
            else:
                make_guild(k, gid, gname, tag, mem)
            for n, r, _c, _t in mem:
                if n == me:
                    rank = r
        if f.get("invite"):
            who, ms = f["invite"]
            a = JArray(JObject)(3)
            a[0], a[1], a[2] = JClass("java.lang.String")(gfix[0]), JClass("java.lang.String")(NAMES[who]), Long(int(System.currentTimeMillis()) + ms)
            GS.INVITES.put(str(uid(me)), a)
        pg = jc(k, "GuildPage")(pref(me))
        pg.info = f.get("info", "")
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

    # the pager boundaries: state -> (list parent, prev button, page text or None = no pager, rows shown)
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
            for k, (cc, ee) in (("0.1.3", res2["old"]), ("0.1.4", res2["new"])):
                has = any(sel == prev for typ, sel, data, lock in ee)
                check(has == (ptxt is not None), "D. %s %s: pager %s (want %s)" % (st[0], k, "shown" if has else "none", ptxt))
                if ptxt is not None:
                    txt = [str(js(d)) for typ, sel, t, d in cc if sel in ("#SkyyGPageTxt.Text", "#SkyyGLPageTxt.Text")]
                    check(txt == [ptxt], "D. %s %s: pager text %s, want %s" % (st[0], k, txt, ptxt))
                rows = sum(1 for typ, sel, t, d in cc if is_append(typ) and sel == "#" + lst_id
                           and re.fullmatch(r"SkyyGL?Row\d+", first_id(t)))
                if k == "0.1.4":
                    check(rows == nrows, "D. %s: %d rows in #%s, want %d" % (st[0], rows, lst_id, nrows))
                COUNT["D boundary"] += 1
        if st[4].get("armed") and st[4]["armed"][0] in ("kick", "lead"):
            want = "Sure" if st[4]["armed"][0] == "kick" else "Confirm"
            check(any('Text: "%s"' % want in (t or "") for typ, sel, t, d in cn), "D. %s: the armed button says %s" % (st[0], want))
            check(any('Text: "%s?"' % want in (t or "") for typ, sel, t, d in co), "D. %s: 0.1.3's armed button said %s?" % (st[0], want))
    print("D. %d states x 2 jars: %d bindings identical, %d b.set lines identical (+ the disclosed #SkyyGLimLbl), %d visible texts "
          "identical (2 disclosed armed labels), %d 0.1.3 ids all kept; 0.1.4: %d markups through check_markup in %d check_page, %d "
          "colours audited, %d member rows measured, result line colours %s" % (
              COUNT["D states"], COUNT["D bindings"], COUNT["D sets"], COUNT["D texts"], COUNT["D ids"], COUNT["D markups"],
              COUNT["D pages"], COUNT["D colours"], COUNT["D rows"],
              dict((k[7:], v) for k, v in COUNT.items() if k.startswith("D info "))))
    want_rank = {"Leader": SUI.norm_color(SUI.COLOR["gold"]), "Admin": SUI.norm_color(SUI.COLOR[K["GUILD_RANK_ADMIN"]]),
                 "Member": SUI.norm_color(SUI.COLOR["value"])}
    check(K["GUILD_RANK_ADMIN"] == "info", "D. the Admin rank colour is the kit's info blue (%s)" % K["GUILD_RANK_ADMIN"])
    check(sorted(RANKCOL) == sorted(want_rank), "D. rank texts seen: %s" % sorted(RANKCOL))
    for rk, want in sorted(want_rank.items()):
        check(RANKCOL.get(rk) == {want}, "D. %s rows are coloured %s, want %s" % (rk, sorted(RANKCOL.get(rk, ())), want))
    check(len(set(want_rank.values())) == 3, "D. the three rank colours differ: %s" % want_rank)
    print("D. pager boundaries: %d checks on 8 states; rank colours %s over %d member rows" % (
        COUNT["D boundary"], ", ".join("%s %s" % (k, sorted(RANKCOL.get(k, ()))) for k in ("Leader", "Admin", "Member")),
        COUNT["D rank colours"]))

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
                snap = (who, a, payload, str(pg.info), str(pg.keepName), str(pg.keepInvite), str(pg.keepAmount), str(pg.keepLimit),
                        int(pg.view), int(pg.pageNo), int(pg.logPage), str(pg.confirm), tuple(sorted(PURSE.items())), guild_state(k))
                out.append((snap, sets_of(cmds), evs))
                if k == "new":
                    r = jc(k, "GuildStore").rankOf(uid(who))
                    check_new("E %s after %s %r" % (name, a, payload), cmds, evs, int(r) if int(r) >= 0 and int(pg.view) == 0 else None)
            trace[k] = out
        for (so, eo_sets, eo_ev), (sn, en_sets, en_ev) in zip(trace["old"], trace["new"]):
            check(so == sn, "E. %s: after %s %r: 0.1.3 %s\n  0.1.4 %s" % (name, so[1], so[2], so[3:12], sn[3:12]))
            extra, missing = en_sets - eo_sets, eo_sets - en_sets
            check(not missing and all(x in NEW_SETS.items() for x in extra), "E. %s: after %s %r: rebuilt page b.set lines differ %s / %s"
                  % (name, so[1], so[2], dict(missing), dict(extra)))
            check(eo_ev == en_ev, "E. %s: after %s %r: rebuilt page bindings differ" % (name, so[1], so[2]))
        moves = [s for s, _x, _y in trace["new"] if s[3].startswith("+")]
        COUNT["E done"] += len(moves)
        return trace

    A_, G_, I_, M_, L_ = "@GAmount", "@GName", "@GInvite", None, "@GLimit"
    t1 = session("guild life", {"purse": {str(uid(1)): 50000, str(uid(2)): 700}, "online": [1, 2]}, [
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
    t2 = session("12 members", {"purse": {str(uid(5)): 0}, "online": [1, 2, 4, 5, 7, 9],
                                "guild": ("g1", "Skyy Guild", "SKY", M12, {"bank": 10000, "log": LOG40[:9], "lim": (-1, 1000)})}, [
        (1, "next", "", None), (1, "next", "", None), (1, "prev", "", None), (1, "kick:3", "", None), (1, "next", "", None),
        (1, "prev", "", None), (1, "kick:3", "", None), (1, "kick:3", "", None), (1, "limmember", "1k", L_),
        (5, "withdraw", "600", A_), (5, "withdraw", "600", A_), (5, "withdraw", "all", A_), (5, "withdraw", "1", A_),
        (5, "leave", "", None), (5, "leave", "", None), (1, "refresh", "", None)])
    print("E. %d clicks (2 sessions x 2 jars), %d successful actions, identical result / keep boxes / views / armed action / purses / "
          "guilds / invites / rebuilt pages after every click" % (COUNT["E clicks"], COUNT["E done"] // 1))

    # ---------------- F. text fit (the client's font tables, read-only; SUI.text_width)
    n_fit = 0
    for (w, pad, size), txts in sorted(BUTTONS.items()):
        for t in txts:
            need = SUI.text_width(t, int(size), True, "Default", True)
            n_fit += 1
            check(need <= int(w) - 2 * int(pad), "F. button %r: %.0f px of label in %d px (%s - 2 x %s)" % (t, need, int(w) - 2 * int(pad), w, pad))
    lh16 = SUI.line_height(16)
    # one-line labels: (id stem, size, bold, width)
    ws = [w for _t, w in K["GUILD_COLS"]]
    lws = [w for _t, w in K["GUILD_LCOLS"]]
    one = [("SkyyGSub", 16, False, K["GUILD_SUM_IN"]), ("SkyyGBarTxt", 16, True, K["GUILD_SUM_IN"]),
           ("SkyyGXpTxt", 15, False, K["GUILD_XPTXT_W"]), ("SkyyGStats", 16, True, K["GUILD_SUM_IN"] - K["GUILD_XPTXT_W"]),
           ("SkyyGHint", 15, False, INNER), ("SkyyGLogCnt", 15, False, K["GUILD_LOGCNT_W"]), ("SkyyGLimHint", 15, False, 367),
           ("SkyyGLimLbl", 16, True, K["GUILD_LIM_LBL_W"]), ("SkyyGPageTxt", 16, False, 260), ("SkyyGLPageTxt", 16, False, 260),
           ("SkyyGLogSub", 16, False, INNER), ("SkyyGLNote", 15, False, INNER), ("SkyyGRule", 15, False, INNER),
           ("SkyyGLEmpty", 16, False, K["GUILD_ROW_W"]), ("SkyyGRowName", 18, True, ws[0]), ("SkyyGRowRank", 16, True, ws[1]),
           ("SkyyGRowXp", 16, False, ws[2]), ("SkyyGRowDay", 16, False, ws[3]), ("SkyyGRowOn", 16, False, ws[4]),
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
    # review 2 (finding 5): the column heads (static, no id: not in SEEN) fit their columns, and the "widest" states really showed
    # the widest texts the build's guild_fits() asserts (so the one-line checks above measured them as the Java makes them)
    for cols in (K["GUILD_COLS"], K["GUILD_LCOLS"]):
        for t, w in cols:
            need = SUI.text_width(t, 16, True, "Default", True)
            n_fit += 1
            worst["column heads"] = max(worst.get("column heads", 0), need / w)
            check(need <= w, "F. column head %r: %.0f px > %d px" % (t, need, w))
    def seen_all(stem):
        return set(t for ident, ts in SEEN.items() if re.fullmatch(stem + r"\d*", ident) for t in ts)

    for stem, want in (("SkyyGRowName", K["GUILD_NAME_YOU"]), ("SkyyGRowName", K["GUILD_NAME_WIDE"]), ("SkyyGXpTxt", K["GUILD_XPTXT_WIDE"]),
                       ("SkyyGStats", K["GUILD_STATS_WIDE"]), ("SkyyGRowDay", K["GUILD_TAKEN_WIDE"]), ("SkyyGLWho", K["GUILD_NAME_WIDE"]),
                       ("SkyyGLWhat", K["GUILD_WHAT_WIDE"]), ("SkyyGLBank", K["GUILD_BANK_WIDE"])):
        check(want in seen_all(stem), "F. the widest %s text %r was shown by a widest state (seen: %d texts)" % (stem, want, len(seen_all(stem))))
        COUNT["F widest"] += 1
    COUNT["F"] = n_fit
    print("F. text fit: %d button labels / texts measured (Nunito Sans / Lexend tables, line height %.2f px at 16); fullest one-line boxes: %s; "
          "%d widest texts shown by the widest states" % (
              n_fit, lh16, ", ".join("%s %.0f%%" % (k, v * 100) for k, v in sorted(worst.items(), key=lambda kv: -kv[1])[:6]), COUNT["F widest"]))

    # ---------------- G. the page id
    pid, chk = K["GUILD_PAGE_ID"], K["GUILD_PAGE_CHECKED"]
    check("page %s)" % pid in LOG_NEW, "G. the jar's ready line names the page the kit makes now (%s): %r - rebuild the jar" % (pid, LOG_NEW))
    check(pid == chk, "G. the page the kit makes now (%s) is the checked page GUILD_PAGE_CHECKED (%s): if everything else passed, set "
                      "PAGE_CHECKED = %r in tools/guilds_0_1_4_patch.py, regenerate and rebuild" % (pid, chk, pid))
    print("G. page id %s, checked %s, kit %s%s" % (pid, chk, SUI.kit_id(), "" if SUI.kit_id() in LOG_NEW else " (the jar was built on another kit file)"))


def main():
    for j in (JAR, OLD):
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
