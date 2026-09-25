"""Bare-JVM check for SkyyEssentials 0.1.3 (kept next to the build so the build report's JVM claim can be re-run).

    python SkyyEssentials/test_skyyessentials_0.1.3.py [--jar <SkyyEssentials-0.1.3.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyEssentials/build_skyyessentials_0.1.3.py). A child process starts a fresh JVM (the game's own JRE,
-Xverify:all, HytaleServer.jar + the jar + tools/javassist.jar on the classpath) and checks:
  A  every class loads and verifies
  B  defaults are identical to 0.1.2 (the 0.1.2 build script's ROWS defaults + the 0.1.2 EXPIRE_MS / COOLDOWN_MS constants)
  C  a missing file gets exactly the default text; a 0.1.2 CRLF file with a hand comment keeps every byte and gets the 4 new keys
     appended (CRLF); the 0.1.2 clamps still apply
  D  the config kit header (21 rows, flags, bindings' start values) and no rewrite of the file at start
  E  get / set per row through config:fn:SkyyEssentials from the console (unit scale, ranges, parts ask on OFF, part.trade ->
     tradeEnabled, tradeOpenMode through the custom: binding, replyShortcut RESTART, tradeAfterSwitchSeconds asks only when lowered,
     denied without the node)
  F  line-preserving writes (CRLF + comments kept, the row key part.trade never written), the change log, history copies
  G  hand edit + the kit's reload op (logged via=file, TCfg.reloadKit applied it with the clamps, replyShortcut untouched)
  H  player Settings: notifyOn / regSetting against fake settings:fn:get / register; the tpa.updates gates sit only on the
     denied / expired / went-offline / cancelled lines (bytecode); the request book uses the live EXPIRE_MS / COOLDOWN_MS
  I  setup() order (TCfg.load -> registrations -> regSetting -> CfgPub.start last), shutdown flushes the kit
  J  permissions with the engine's own AbstractCommand code: player commands give hytale:Adventurer only player nodes; /fly,
     /tradeadmin and /warpadmin put their nodes into no group
  K  world spawn: console / no-node actions refused, a scheduled change that does not happen writes a "failed" line (via menu, never a
     second "done" line), the page's call logs via=command, a missing world is refused
  L  the warps page (main view with a test subclass whose guard() is true, confirm view, no-permission view) and both settings pages
     (plain + confirm) rendered into a real UICommandBuilder: root anchor only Width/Height, height <= 1000, unique ids, no
     underscores, every append / set / event target exists, balanced markup
  M  garbage ops never throw
NOT runnable in a bare JVM (no TeleportPlugin / worlds / permissions): warp rows with real warps, Go / Move / Rename / Remove / Add,
the world spawn change itself, EssPerm with real nodes - they are in the in-game steps (TEST-CHECKLIST).
Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyessentials-test (git-ignored), deleted at the end unless --keep;
TEMP/TMP and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1.3"
PKG = "com.skyy.essentials."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyessentials-test")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def rows_of(script):
    """The ROWS table of a build script (a list of literal tuples; the script is only read, never run)."""
    src = open(os.path.join(HERE, script), encoding="utf8").read()
    m = re.search(r"^ROWS = (\[.*?^\])", src, re.M | re.S)
    return ast.literal_eval(m.group(1))


def file_012(rows12):
    """What 0.1.2's TCfg.fileText() wrote with every default (FILE_ORDER = [13] + 0..12)."""
    out = ["# SkyyEssentials config - change it in game with /tradeadmin config (it writes this file at once),",
           "# or edit it here and run /tradeadmin reload. replyShortcut needs a server restart; everything else applies at once."]
    for k, i in enumerate([13] + list(range(13))):
        if k == 1:
            out += ["#", "# ---- /trade (SkyyEssentials 0.1.2) ----"]
        out.append("# " + rows12[i][8])
        out.append("%s=%s" % (rows12[i][0], rows12[i][6]))
    return "\n".join(out) + "\n"


def props_of(text):
    out = {}
    for l in text.replace("\r\n", "\n").split("\n"):
        s = l.strip()
        if not s or s[0] in "#!" or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


# ------------------------------------------------------------------------------------------------ page markup checks (section L)
EL_RE = re.compile(r"\b([A-Z][A-Za-z]+) #([A-Za-z0-9_]+)\s*\{")


def balanced(s):
    q, br, pa = False, 0, 0
    for i, c in enumerate(s):
        if c == '"' and (i == 0 or s[i - 1] != "\\"):
            q = not q
        elif not q:
            br += (c == "{") - (c == "}")
            pa += (c == "(") - (c == ")")
            if br < 0 or pa < 0:
                return False
    return br == 0 and pa == 0 and not q


def page_problems(name, cmds, evs):
    """cmds = [(type, selector, data, text)], evs = [(selector, data)]. Returns a list of problems (empty = fine)."""
    bad = []
    ids = []
    if not cmds:
        return [name + ": nothing rendered"]
    t0, s0, d0, x0 = cmds[0]
    m = re.match(r"^Group #([A-Za-z0-9]+) \{ Anchor: \(([^)]*)\);", x0 or "")
    if s0 is not None or not m:
        bad.append("%s: the first command is not a root Group append (%s %s)" % (name, s0, (x0 or "")[:80]))
    else:
        parts = dict(p.split(":", 1) for p in [q.strip() for q in m.group(2).split(",")] if ":" in p)
        keys = sorted(k.strip() for k in parts)
        if keys != ["Height", "Width"]:
            bad.append("%s: root anchor is not only Width/Height: %s" % (name, m.group(2)))
        else:
            h, w = int(parts["Height"]), int(parts["Width"])
            if h > 1000 or w > 1900:
                bad.append("%s: root %d x %d does not fit 1920 x 1080" % (name, w, h))
    for typ, sel, data, text in cmds:
        if text:
            if not balanced(text):
                bad.append("%s: unbalanced markup: %s" % (name, text[:120]))
            for el, i in EL_RE.findall(text):
                if "_" in i:
                    bad.append("%s: underscore in element id #%s" % (name, i))
                if i in ids:
                    bad.append("%s: element id #%s used twice" % (name, i))
                ids.append(i)
        if sel is not None and sel != "":
            tid = sel.lstrip("#").split(".")[0].split(" ")[0]
            known = ids if not text else ids[:len(ids) - len(EL_RE.findall(text))]
            if tid not in known:
                bad.append("%s: %s targets #%s before / without it existing" % (name, typ, tid))
    for sel, data in evs:
        tid = (sel or "").lstrip("#")
        if tid not in ids:
            bad.append("%s: event on #%s which does not exist" % (name, tid))
        try:
            for v in (json.loads(data) if data else {}).values():
                if isinstance(v, str) and v.startswith("#"):
                    if v.lstrip("#").split(".")[0] not in ids:
                        bad.append("%s: event data reads %s which does not exist" % (name, v))
        except ValueError:
            bad.append("%s: event data is not JSON: %s" % (name, data))
    return bad


# ============================================================================================================== child: the checks
def run(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import zipfile
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST], convertStrings=True)

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    check(len(names) == 62, "62 classes in the jar (got %d)" % len(names))
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    ES, TC, Rows, Pub, Warp = (JClass(PKG + "EssStore"), JClass(PKG + "TCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "CfgPub"),
                               JClass(PKG + "EssWarp"))
    UUID, Paths, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    rows12, rows13 = rows_of("build_skyyessentials_0.1.2.py"), rows_of("build_skyyessentials_0.1.3.py")

    # ---------------- B. defaults identical to 0.1.2 (fields read before any load)
    check(int(ES.EXPIRE_MS) == 60000 and int(ES.COOLDOWN_MS) == 10000 and bool(ES.PART_TPA) and bool(ES.PART_MSG),
          "EXPIRE_MS / COOLDOWN_MS = the 0.1.2 constants, parts on")
    keys13 = [str(k) for k in TC.KEYS]
    for r in rows12:
        i = keys13.index(r[0]) if r[0] in keys13 else -1
        check(i >= 0 and str(TC.get(i)) == r[6] and str(TC.DEFAULTS[i]) == r[6], "default %s = 0.1.2 %s (got %s)"
              % (r[0], r[6], TC.get(i) if i >= 0 else "missing"))
    check(bool(TC.ENABLED) and bool(TC.PAGE_MODE) and bool(TC.REPLY_FILE), "tradeEnabled / page mode / replyShortcut default on")
    print("B. defaults = 0.1.2")

    work = os.path.join(SCRATCH, "work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)

    # ---------------- C. missing file / a 0.1.2 CRLF file with a hand comment (TCfg.load, no kit yet)
    fresh = os.path.join(work, "fresh", "Skyy_SkyyEssentials", "config.properties")
    ES.CFG = Paths.get(fresh)
    r = str(TC.load())
    dt = str(TC.DEFAULT_TEXT)
    check(os.path.isfile(fresh) and open(fresh, "rb").read().decode("latin-1") == dt, "missing file written with DEFAULT_TEXT")
    check("new config.properties written" in r, "load() says the file was written: %s" % r)
    want = dict((x[0], x[6]) for x in rows13)
    check(props_of(dt) == want, "default file keys + values = the rows: %s" % props_of(dt))
    check([str(x) for x in Rows.defLines(0)] == dt.split("\n")[:-1] or "\n".join(str(x) for x in Rows.defLines(0)) + "\n" == dt,
          "kit DEFAULTS text = TCfg.DEFAULT_TEXT")
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    os.makedirs(home)
    cfgp = os.path.join(home, "config.properties")
    t12 = file_012(rows12).replace("tradeDistance=9", "tradeDistance=12").replace("tradeOpenMode=page", "tradeOpenMode=chest")
    t12 = t12.replace("# ---- /trade (SkyyEssentials 0.1.2) ----\n", "# ---- /trade (SkyyEssentials 0.1.2) ----\n# my note: keep trades close\n")
    orig = t12.replace("\n", "\r\n").encode("latin-1")
    open(cfgp, "wb").write(orig)
    ES.CFG = Paths.get(cfgp)
    TC.load()
    now = open(cfgp, "rb").read()
    check(now.startswith(orig), "every byte of the 0.1.2 file kept")
    add = now[len(orig):].decode("latin-1")
    exp = "#\r\n# ---- added by SkyyEssentials %s (keys this file did not have yet, with their defaults) ----\r\n" % VERSION
    by = dict((x[0], x) for x in rows13)
    for k in ("part.tpa", "part.msg", "tpa.expireSeconds", "tpa.cooldownSeconds"):
        exp += "# %s\r\n%s=%s\r\n" % (by[k][8], k, by[k][6])
    check(add == exp, "the 4 new keys appended with their comments, CRLF:\n%r\n%r" % (add, exp))
    check(int(TC.DIST) == 12 and not bool(TC.PAGE_MODE), "the 0.1.2 values read (tradeDistance 12, chest)")
    # 0.1.2 clamps (a scratch copy; the kit fixture above stays as it is)
    clampf = os.path.join(work, "clamp", "Skyy_SkyyEssentials", "config.properties")
    os.makedirs(os.path.dirname(clampf))
    open(clampf, "w", newline="\n").write(t12.replace("tradeDistance=12", "tradeDistance=5000").replace("tradeSlotsPerSide=16", "tradeSlotsPerSide=2")
                                          .replace("tradeCoinsAllowed=true", "tradeCoinsAllowed=maybe"))
    ES.CFG = Paths.get(clampf)
    TC.load()
    check(int(TC.DIST) == 1000 and int(TC.SLOTS) == 4 and bool(TC.COINS), "0.1.2 clamps (5000 -> 1000, 2 -> 4) and a bad word keeps the value")
    ES.CFG = Paths.get(cfgp)
    TC.load()
    check(open(cfgp, "rb").read() == now, "a second load appends nothing")
    check(int(TC.DIST) == 12 and int(TC.SLOTS) == 16 and not bool(TC.PAGE_MODE), "the kit fixture values are back")
    print("C. load paths done")

    # ---------------- D. the kit header
    Pub.start(Paths.get(mods), None)
    bridge = TC.bridge()
    fn = bridge.get("config:fn:SkyyEssentials")
    hdr = bridge.get("config:def:SkyyEssentials")
    check(fn is not None and hdr is not None, "config:fn + config:def published")
    check(str(bridge.get("config:epoch:SkyyEssentials")) == "0", "epoch starts at 0")
    check(len(hdr) == 10 and str(hdr[0]) == "1" and str(hdr[1]) == "SkyyEssentials" and str(hdr[2]) == "Essentials"
          and str(hdr[3]) == VERSION and str(hdr[4]) == "skyyessentials.admin", "header 0-4 %s" % ([str(hdr[i]) for i in range(5)],))
    check([str(x) for x in hdr[5]] == ["parts", "tpa", "msg", "warps", "trade"], "categories %s" % [str(x) for x in hdr[5]])
    check(str(hdr[8]) == "Skyy_SkyyEssentials/config.properties" or "config.properties" in str(hdr[8]), "files %s" % hdr[8])
    rows = [[str(x) for x in row] for row in hdr[7]]
    check(len(rows) == 21 and all(len(x) == 11 for x in rows), "21 rows of 11 (got %d)" % len(rows))
    flags = dict((x[0], x[9]) for x in rows)
    for k, f in (("part.tpa", "live,part,danger"), ("part.msg", "live,part,danger"), ("part.trade", "live,part,danger"),
                 ("tpa.expireSeconds", "live"), ("tpa.cooldownSeconds", "live"), ("replyShortcut", "restart"), ("spawn.set", "danger"),
                 ("spawn.reset", "danger"), ("tradeSlotsPerSide", "new"), ("tradeAfterSwitchSeconds", "live,adv,danger"),
                 ("tradeSaveDelayMillis", "live,adv"), ("tradeOpenMode", "live")):
        check(flags.get(k) == f, "row %s flags %s (got %s)" % (k, f, flags.get(k)))
    types = dict((x[0], x[3]) for x in rows)
    check(types.get("warps.editor") == "link" and types.get("spawn.set") == "action" and types.get("tradeOpenMode") == "choice",
          "link / action / choice rows")

    def op(*args):
        a = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            a[i] = x
        return fn.apply(a)

    def R(r):
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    def get(k):
        v = op("get", k)
        return None if v is None else str(v)

    def cset(k, v, confirm="yes"):   # the server console (no permission provider in a bare JVM)
        return R(op("set", k, v, None, None, confirm, "console"))

    def settle():
        Pub.flush()
        time.sleep(0.5)
        Pub.flush()

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    start = {"part.tpa": "true", "part.msg": "true", "part.trade": "true", "tpa.expireSeconds": "60", "tpa.cooldownSeconds": "10",
             "replyShortcut": "true", "tradeDistance": "12", "tradeOpenMode": "chest", "tradeSlotsPerSide": "16",
             "tradeAfterSwitchSeconds": "30", "tradeSaveDelayMillis": "1000", "tradeMaxCoins": "0"}
    for k, v in start.items():
        check(get(k) == v, "start value %s = %s (got %s)" % (k, v, get(k)))
    settle()
    check(open(cfgp, "rb").read() == now, "the kit does not rewrite the file at start")
    check(not [l for l in logs() if "\tclamped" in l or "\tinvalid" in l], "no clamp / invalid lines at start")
    print("D. kit header done")

    # ---------------- E. get / set
    r = cset("tpa.expireSeconds", "90", confirm="")
    check(r[0] == "ok" and int(ES.EXPIRE_MS) == 90000, "tpa.expireSeconds 90 -> EXPIRE_MS 90000 (unit scale): %s" % (r,))
    check(cset("tpa.expireSeconds", "5")[0] == "bad" and cset("tpa.expireSeconds", "601")[0] == "bad" and int(ES.EXPIRE_MS) == 90000,
          "tpa.expireSeconds outside 10-600 refused")
    r = cset("tpa.cooldownSeconds", "0", confirm="")
    check(r[0] == "ok" and int(ES.COOLDOWN_MS) == 0, "tpa.cooldownSeconds 0: %s" % (r,))
    r = cset("part.tpa", "false", confirm="")
    check(r[0] == "confirm" and bool(ES.PART_TPA), "part.tpa OFF asks first: %s" % (r,))
    r = cset("part.tpa", "false")
    check(r[0] == "ok" and not bool(ES.PART_TPA), "part.tpa OFF with yes: %s" % (r,))
    r = cset("part.tpa", "true", confirm="")
    check(r[0] == "ok" and bool(ES.PART_TPA), "part.tpa ON does not ask: %s" % (r,))
    r = cset("part.trade", "false")
    check(r[0] == "ok" and not bool(TC.ENABLED), "part.trade -> TCfg.ENABLED: %s" % (r,))
    r = cset("tradeOpenMode", "page", confirm="")
    check(r[0] == "ok" and bool(TC.PAGE_MODE) and get("tradeOpenMode") == "page", "tradeOpenMode through the custom: binding: %s" % (r,))
    check(cset("tradeOpenMode", "window")[0] == "bad", "tradeOpenMode refuses an unknown choice")
    r = cset("replyShortcut", "false", confirm="")
    check(r[0] == "restart" and bool(TC.REPLY_FILE), "replyShortcut: status restart, the field waits for the restart: %s" % (r,))
    r = cset("tradeAfterSwitchSeconds", "20", confirm="")
    check(r[0] == "confirm" and int(TC.AFTER_S) == 30, "tradeAfterSwitchSeconds lowered asks: %s" % (r,))
    r = cset("tradeAfterSwitchSeconds", "20")
    check(r[0] == "ok" and int(TC.AFTER_S) == 20, "tradeAfterSwitchSeconds lowered with yes: %s" % (r,))
    r = cset("tradeAfterSwitchSeconds", "40", confirm="")
    check(r[0] == "ok" and int(TC.AFTER_S) == 40, "tradeAfterSwitchSeconds raised does not ask: %s" % (r,))
    r = cset("tradeMaxCoins", "2k", confirm="")
    check(r[0] == "ok" and int(TC.MAX_COINS) == 2000, "tradeMaxCoins 2k: %s" % (r,))
    check(cset("tradeEnabled", "true")[0] == "unknown", "the file key tradeEnabled is not a row key (part.trade is)")
    A = UUID.fromString("00000000-0000-0000-0000-0000000000aa")
    check(R(op("set", "tradeDistance", "5", A, "Someone", "yes", "menu"))[0] == "denied" and int(TC.DIST) == 12,
          "a player without skyyessentials.admin is denied")
    check(R(op("set", "tradeDistance", "5", None, "Ghost", "yes", "command"))[0] == "denied", "null who via command is denied")
    print("E. get/set done")

    # ---------------- F. files
    settle()
    t = open(cfgp, "rb").read().decode("latin-1")
    exp = now.decode("latin-1")
    for a_, b_ in (("tpa.expireSeconds=60", "tpa.expireSeconds=90"), ("tpa.cooldownSeconds=10", "tpa.cooldownSeconds=0"),
                   ("tradeEnabled=true", "tradeEnabled=false"), ("tradeOpenMode=chest", "tradeOpenMode=page"),
                   ("replyShortcut=true", "replyShortcut=false"), ("tradeAfterSwitchSeconds=30", "tradeAfterSwitchSeconds=40"),
                   ("tradeMaxCoins=0", "tradeMaxCoins=2000")):
        exp = exp.replace(a_ + "\r\n", b_ + "\r\n")
    check(t == exp, "only the changed lines changed (CRLF, hand comment and order kept):\n%s" % t)
    check("part.trade=" not in t and "# my note: keep trades close\r\n" in t, "the row key part.trade is never written; the hand comment stays")
    lg = logs()

    def has(via, key, old, new, status):
        return any(l.split("\t")[3:8] == [via, key, old, new, status] for l in lg)

    check(has("console", "tpa.expireSeconds", "60", "90", "ok") and has("console", "part.trade", "true", "false", "ok")
          and has("console", "replyShortcut", "true", "false", "restart") and has("console", "tradeOpenMode", "chest", "page", "ok"),
          "changes logged (console) %s" % lg[:8])
    check(os.path.isfile(os.path.join(home, "config-changes.log")), "config-changes.log written")
    v = op("versions")
    check(v is not None and len(v) >= 1 and os.path.isdir(os.path.join(home, "config-history")), "history copy made")
    print("F. files done")

    # ---------------- G. hand edits: the kit's reload op -> TCfg.reloadKit
    open(cfgp, "wb").write(t.replace("tradeDistance=12", "tradeDistance=15").replace("tpa.cooldownSeconds=0", "tpa.cooldownSeconds=400")
                           .encode("latin-1"))
    r = R(op("reload", None, None, "console"))
    check(r is not None and r[0] == "ok", "reload op: %s" % (r,))
    settle()
    time.sleep(0.3)
    check(int(TC.DIST) == 15 and int(ES.COOLDOWN_MS) == 300000, "TCfg.reloadKit applied them with the 0.1.2 clamp (400 -> 300): %s %s"
          % (TC.DIST, ES.COOLDOWN_MS))
    check(bool(TC.REPLY_FILE), "reloadKit never applies replyShortcut (the file says false, the running value waits for a restart)")
    lg = logs()
    check(any(l.split("\t")[3:7] == ["file", "tradeDistance", "12", "15"] for l in lg), "hand edit logged via=file %s" % lg[:6])
    r = R(op("reload", None, None, "console"))
    check(r[0] == "ok" and r[1] == "0", "a second reload finds nothing: %s" % (r,))
    TC.reloadKit()
    check(int(TC.DIST) == 15, "a direct reloadKit keeps the values")
    code_ = op("export", "all")
    check(code_ is not None and str(code_).startswith("SKYY1.SkyyEssentials."), "export code: %s" % (str(code_)[:40],))
    r = R(op("import", code_, None, None, "preview"))
    check(r is not None and r[0] == "ok" and "nothing to change" in r[2].lower(), "export -> import preview: nothing to change: %s" % (r,))
    s = [str(x) for x in op("status")]
    check(s[0] == "restart" and "1 change" in s[1], "status: the replyShortcut change from E waits for a restart %s" % s)
    print("G. hand edits done")

    # ---------------- H. player Settings + the request book
    U = UUID.fromString("00000000-0000-0000-0000-0000000000bb")
    check(bool(ES.notifyOn(U, "tpa.updates")) and bool(ES.notifyOn(None, "tpa.updates")), "no SkyyMenu = ON (0.1.2)")

    @JImplements("java.util.function.Function")
    class FakeGet(object):
        def __init__(self):
            self.off, self.mode = set(), "bool"

        @JOverride
        def apply(self, o):
            if self.mode == "throw":
                raise RuntimeError("boom")
            if self.mode == "null":
                return None
            return JClass("java.lang.Boolean").valueOf(str(o[1]) not in self.off)

    @JImplements("java.util.function.Function")
    class FakeReg(object):
        def __init__(self):
            self.got = []

        @JOverride
        def apply(self, o):
            self.got.append([str(x) for x in o])
            return None

    fg, fr = FakeGet(), FakeReg()
    bridge.put("settings:fn:get", fg)
    bridge.put("settings:fn:register", fr)
    ES.regSetting("tpa.updates", "Teleport request updates", "general", True, "help")
    d = bridge.get("settings:def:tpa.updates")
    want_d = ["SkyyEssentials", "tpa.updates", "Teleport request updates", "general", "true", "help"]
    got_d = None if d is None else [str(x).lower() if i == 4 else str(x) for i, x in enumerate(d)]
    got_r = [[str(x).lower() if i == 4 else str(x) for i, x in enumerate(g)] for g in fr.got]
    check(got_d == want_d and got_r == [want_d], "regSetting writes settings:def and calls settings:fn:register: %s %s" % (got_d, got_r))
    check(d is not None and JClass("java.lang.Boolean").TRUE.equals(d[4]), "the default travels as java.lang.Boolean")
    fg.off.add("tpa.updates")
    check(not bool(ES.notifyOn(U, "tpa.updates")), "switch OFF")
    fg.mode = "null"
    check(bool(ES.notifyOn(U, "tpa.updates")), "no answer = ON")
    fg.mode = "throw"
    check(bool(ES.notifyOn(U, "tpa.updates")), "a throwing Settings function = ON")
    for k in ("settings:fn:get", "settings:fn:register", "settings:def:tpa.updates"):
        bridge.remove(k)
    # the request book reads the live values (EXPIRE_MS 90 s from E; cooldown set to 10 s here)
    ES.COOLDOWN_MS = 10000
    X, Y, Z = (UUID.fromString("00000000-0000-0000-0000-00000000010%d" % i) for i in (1, 2, 3))
    t0 = int(time.time() * 1000)
    check(ES.tryAdd(X, Y, False, "X", "Y") is None, "tryAdd accepts a first request")
    rq = ES.REQ.get(ES.key(X, Y))
    check(rq is not None and 89000 <= int(rq.expires) - t0 <= 91500, "the request expires after the live EXPIRE_MS (90 s): %s" % (
        None if rq is None else int(rq.expires) - t0))
    e = ES.tryAdd(X, Z, False, "X", "Z")
    check(e is not None and "Please wait" in str(e), "the live COOLDOWN_MS (10 s) applies: %s" % e)
    ES.COOLDOWN_MS = 0
    check(ES.tryAdd(X, Z, False, "X", "Z") is None, "COOLDOWN_MS 0 = no cooldown")
    ES.REQ.clear()
    ES.LAST_SENT.clear()
    print("H. settings + request book done")

    # ---------------- I. bytecode: setup() / shutdown() order, the tpa.updates gates
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth, sig=None):
        cc = pool.get(PKG + cls)
        mm = cc.getDeclaredMethod(meth) if sig is None else [m_ for m_ in cc.getDeclaredMethods()
                                                             if str(m_.getName()) == meth and sig in str(m_.getSignature())][0]
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    def idx(pat, lines):
        return [i for i, l in enumerate(lines) if pat in l]

    su = code("SkyyEssentialsPlugin", "setup")
    ld, st, rg = idx("TCfg.load(", su), idx("CfgPub.start(", su), idx("EssStore.regSetting(", su)
    reg = idx("registerCommand(", su) + idx("registerGlobal(", su) + idx("scheduleAtFixedRate(", su)
    check(len(ld) == 1 and len(st) == 1 and len(rg) == 1, "setup: one TCfg.load, one CfgPub.start, one regSetting")
    check(ld and st and rg and reg and ld[0] < min(reg) and rg[0] < st[0] and max(reg) < st[0],
          "setup order: TCfg.load -> registrations -> regSetting -> CfgPub.start")
    check('"tpa.updates"' in "\n".join(su) and '"Teleport request updates"' in "\n".join(su), "setup registers tpa.updates")
    after = [l for l in su[st[0] + 1:] if "invoke" in l]
    check(not any(("register" in l) or ("regSetting" in l) for l in after), "nothing is registered after CfgPub.start")
    sd = code("SkyyEssentialsPlugin", "shutdown")
    ps_, ss_ = idx("CfgPub.shutdown(", sd), idx("invokespecial", sd)
    check(len(ps_) == 1 and ss_ and ps_[0] < ss_[-1], "shutdown flushes the kit before super.shutdown()")
    pr_ = code("EssStore", "prune")
    check(len(idx("EssStore.notifyOn(", pr_)) == 4, "prune: 4 gated lines (went offline x2, expired x2)")
    check(len(idx("EssStore.notifyOn(", code("EssStore", "deny"))) == 1, "deny: the 'denied your request' line is gated")
    check(not idx("notifyOn(", code("EssStore", "accept")) and not idx("notifyOn(", code("EssStore", "request", "Ljava/lang/Object;Z")),
          "accept / request lines are never gated")
    check(len(idx("EssStore.notifyOn(", code("TpaCancelCmd", "execute"))) == 1, "/tpacancel: the notice to the target is gated")
    rn = code("SpawnTask", "run")
    check(idx("EssWarp.spawnSet(", rn) and not idx("auditVia(", rn) and not idx("EssWarp.audit(", rn),
          "SpawnTask never writes a second done line itself")
    sp = code("EssWarp", "spawnSet")
    check(idx("isAlive(", sp) and idx("auditVia(", sp) and idx("TCfg.info(", sp), "spawnSet: dead-world refusal, auditVia only with a via")
    print("I. bytecode order done")

    # ---------------- J. permissions: the engine's own AbstractCommand code
    try:
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        own = uf.get(None).allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    except Exception as ex:
        print("no CommandManager owner (%s)" % ex)
        own = None

    def tree(c_):
        out = [c_]
        for s_ in list(c_.getSubCommands().values()):
            out += tree(s_)
        return out

    player_roots = ["TpaCmd", "TpaHereCmd", "TpAcceptCmd", "TpDenyCmd", "TpaCancelCmd", "MsgCmd", "ReplyCmd", "RCmd", "TradeCmd"]
    admin_roots = {"FlyCmd": "skyyessentials.fly", "TradeAdminCmd": "skyyessentials.tradeadmin", "WarpAdminCmd": "skyyessentials.admin"}
    adv = []
    if own is not None:
        for n in player_roots + list(admin_roots):
            c_ = JClass(PKG + n)()
            for x in tree(c_):
                x.setOwner(own)
            mp = c_.getPermissionGroupsRecursive()
            nodes = [str(y) for k in mp.keySet() for y in mp.get(k)]
            if n in admin_roots:
                check(str(c_.getPermission()) == admin_roots[n] and mp.size() == 0,
                      "/%s: requirePermission %s, its nodes in NO group: %s" % (n, admin_roots[n], mp))
            else:
                check([str(k) for k in mp.keySet()] == ["hytale:Adventurer"] and nodes, "%s: hytale:Adventurer only: %s" % (n, mp))
                adv += nodes
        check(not [x for x in adv if x in admin_roots.values() or "admin" in x], "hytale:Adventurer gets no admin node: %s" % adv)
        ctl = JClass(PKG + "WarpAdminCmd")()                # control: the same command WITH groups would leak (the check can fail)
        SA = JArray(JClass("java.lang.String"))
        spg = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand").class_.getDeclaredMethod("setPermissionGroups", SA.class_)
        spg.setAccessible(True)
        va = JArray(JObject)(1)
        va[0] = SA(["hytale:Adventurer"])
        spg.invoke(ctl, va)
        ctl.setOwner(own)
        cm_ = ctl.getPermissionGroupsRecursive()
        check(cm_.size() == 1 and "skyyessentials.admin" in [str(x) for x in cm_.get("hytale:Adventurer")],
              "control: a group list on /warpadmin would leak its node")
    else:
        check(False, "J skipped: no CommandManager owner")
    print("J. permissions done (hytale:Adventurer gets: %s)" % ", ".join(sorted(set(adv))))

    # ---------------- K. world spawn: refusals and the log lines
    n0 = len(logs())
    r = R(op("action", "spawn.set", None, None, "", "console"))
    check(r[0] == "confirm", "spawn.set from the console asks first (danger): %s" % (r,))
    r = R(op("action", "spawn.set", None, None, "yes", "console"))
    check(r[0] == "bad" and "player in game" in r[2], "spawn.set from the console is refused (it changes the admin's own world): %s" % (r,))
    r = R(op("action", "spawn.reset", A, "Someone", "yes", "menu"))
    check(r[0] == "denied", "spawn.reset without skyyessentials.admin is denied: %s" % (r,))
    settle()
    check(len(logs()) == n0, "refused actions write no log line")
    res = str(Warp.spawnSet(None, None, None, None, False, "command"))
    check(res.startswith("-") and "not in a world" in res, "spawnSet without a world is refused: %s" % res)
    S1 = UUID.fromString("00000000-0000-0000-0000-0000000000cc")
    JClass(PKG + "SpawnTask")(S1, "Tester", False, None).run()      # bare JVM: no Universe -> the change cannot happen
    JClass(PKG + "SpawnTask")(S1, "Tester", True, None).run()
    settle()
    lg = logs()
    fl = [l.split("\t") for l in lg if l.split("\t")[2:3] == [str(S1)]]
    check(len(fl) == 2 and all(f[1] == "Tester" and f[3] == "menu" and f[5] == "(action)" and f[6].startswith("not done - ")
                               and f[7] == "failed" for f in fl) and sorted(f[4] for f in fl) == ["spawn.reset", "spawn.set"],
          "a scheduled spawn change that did not happen writes one 'failed' line each (via menu), never 'done': %s" % fl)
    Warp.auditVia(S1, "Tester", "command", "spawn.set", "default", "1 2 3")
    Warp.failed(S1, "Tester", "spawn.set", "why")
    settle()
    lg = logs()
    check(lg[0].split("\t")[1:] == ["Tester", str(S1), "menu", "spawn.set", "(action)", "not done - why", "failed"]
          and lg[1].split("\t")[1:] == ["Tester", str(S1), "command", "spawn.set", "default", "1 2 3", "done"],
          "auditVia / failed line format: %s" % lg[:2])
    print("K. world spawn done")

    # ---------------- L. page markup
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def render(page):
        b, ev = UCB(), UEB()
        page.build(None, b, ev, None)
        cmds = [(str(c_.type), None if c_.selector is None else str(c_.selector), None if c_.data is None else str(c_.data),
                 None if c_.text is None else str(c_.text)) for c_ in b.getCommands()]
        evs = [(None if e_.selector is None else str(e_.selector), None if e_.data is None else str(e_.data)) for e_ in ev.getEvents()]
        return cmds, evs

    cc = pool.makeClass(PKG + "TestWarpPage", pool.get(PKG + "WarpPage"))
    CNC, CNM = JClass("javassist.CtNewConstructor"), JClass("javassist.CtNewMethod")
    cc.addConstructor(CNC.make("public TestWarpPage() { super((com.hypixel.hytale.server.core.universe.PlayerRef) null); }", cc))
    cc.addMethod(CNM.make("public boolean guard() { return true; }", cc))
    cc.toClass(JClass(PKG + "WarpPage").class_)
    TWP = JClass(PKG + "TestWarpPage")
    views = []
    wp = TWP()
    views.append(("warps main", render(wp)))
    wp.info = "+Warp fens2 added where you stand (world 1 2 3)."
    views.append(("warps main + result", render(wp)))
    wp.cKind = "spset"
    views.append(("warps confirm spawn", render(wp)))
    wp.cKind, wp.cId = "rm", "fens2"
    views.append(("warps confirm remove", render(wp)))
    views.append(("warps no permission", render(JClass(PKG + "WarpPage")(None))))
    for w_ in (0, 1):
        pg = JClass(PKG + "TCfgPage")(None, w_)
        views.append(("settings %d" % w_, render(pg)))
        pg.pendKey, pg.pendVal, pg.pendQ = "part.trade", "false", "Turn Trading off?"
        pg.keep[2] = "draft"                               # row 2 = a number row on both pages
        views.append(("settings %d confirm + draft" % w_, render(pg)))
    for name, (cmds, evs) in views:
        p = page_problems(name, cmds, evs)
        check(not p, "%s: %s" % (name, p))
        check(len(cmds) > 5, "%s rendered %d commands" % (name, len(cmds)))
    main = views[0][1][0]
    ids = [i for _, _, _, x in main if x for _, i in EL_RE.findall(x)]
    for i in ("SkyyWpSpSet", "SkyyWpSpReset", "SkyyWpAdd", "SkyyWpName", "SkyyWpSettings", "SkyyWpRefresh", "SkyyWpClose"):
        check(i in ids, "warps page has #%s" % i)
    conf = views[2][1]
    check(any(x and "Wrap: true" in x for _, _, _, x in conf[0]) and [e for e in conf[1] if e[0] == "#SkyyWpYes"],
          "confirm view: wrapped question + Confirm button")
    set_texts = [d for _, s_, d, _ in views[6][1][0] if s_ == "#SkyyTcV2.Value"]
    check(set_texts and "draft" in set_texts[0], "settings page keeps a refused draft in its box: %s" % set_texts)
    print("L. page markup done (%d views)" % len(views))

    # ---------------- M. garbage never throws
    thrown = 0
    for g in [None, [], ["nope"], ["set"], ["get"], ["get", 7], ["set", "part.tpa", 5, None, None, "yes", "console"],
              ["set", "part.tpa", "false", "notauuid", "n", "yes", "menu"], ["action"], ["action", "spawn.set", "x", None, "yes", "menu"],
              ["action", "nope", None, None, "yes", "console"], ["reload"], ["reload", "x", "n"], ["log", "abc"], ["status", 1],
              ["set", "tradeOpenMode", None, None, None, "yes", "console"]]:
        try:
            if g is None:
                fn.apply(None)
            else:
                a = JArray(JObject)(len(g))
                for i, x in enumerate(g):
                    a[i] = x
                fn.apply(a)
        except Exception as ex:
            thrown += 1
            print("threw", g, ex)
    check(thrown == 0, "garbage ops never throw")
    check(bool(ES.PART_TPA), "garbage changed nothing")
    Pub.shutdown()
    print("M. garbage done")


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--dir", SCRATCH], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
