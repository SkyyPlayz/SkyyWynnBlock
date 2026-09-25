"""Bare-JVM check for SkyyClasses 0.1.5 (kept next to the build so the build report's JVM claim can be re-run).

    python SkyyClasses/test_skyyclasses_0.1.5.py [--jar <SkyyClasses-0.1.5.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python tools/classes_0_1_5_patch.py, then python SkyyClasses/build_skyyclasses_0.1.5.py). A child process starts a
fresh JVM (the game's own JRE, -Xverify:all, HytaleServer.jar + the jar + tools/javassist.jar on the classpath) and checks:
  A  every class loads and verifies
  B  defaults are identical to 0.1.4 (the 0.1.4 build script's DEF_* values and default file lines vs the 0.1.5 fields and file text)
  C  a missing file is written with the defaults; a hand-made 0.1.4 file is read with the old clamps; no file line turns switching on
  D  the 0.1.4 default file is taken over by the config kit unchanged (header, rows, flags, epoch, no rewrite at start)
  E  get / set per row through config:fn:SkyyClasses (danger asks both ways, int bounds, read-only row, unknown key, denied)
  F  line-preserving writes, the change log, history copies
  G  hand edit + the kit's reload op (logged via=file, ClassCfg.load clamps); ClassCfg.loadInert never touches a bound field
  H  player Settings: notifyOn / regSetting, and the ClassRules.tell / popup gates sit before their throttles
  I  setup() order (config load -> ... -> Settings switches -> CfgPub.start last), shutdown flushes the kit
  J  permissions with the engine's own AbstractCommand code: /classadmin puts skyyclasses.admin into no group
  K  garbage ops never throw
Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyclasses-test (git-ignored), deleted at the end unless --keep; TEMP/TMP
and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1.5"
PKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyclasses-test")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def old_defaults():
    """The 0.1.4 build script's DEF_* values and default file lines (the script is only read, never run)."""
    src = open(os.path.join(HERE, "build_skyyclasses_0.1.4.py"), encoding="utf8").read()
    ns = {}
    for m in re.finditer(r"^(DEF_[A-Z_]+) = (.+)$", src, re.M):
        ns[m.group(1)] = eval(m.group(2), {}, {})
    m = re.search(r"^CFG_LINES = (\[.*?^\])", src, re.M | re.S)
    lines = eval(m.group(1), {}, dict(ns))
    return ns, lines


def props_of(text):
    out = {}
    for l in text.replace("\r\n", "\n").split("\n"):
        s = l.strip()
        if not s or s[0] in "#!" or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


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
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    Cfg, Rows, Pub, Hooks, Rules = (JClass(PKG + "ClassCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "CfgPub"), JClass(PKG + "ClassHooks"),
                                    JClass(PKG + "ClassRules"))
    UUID, Paths, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer")

    # ---------------- B. defaults identical to 0.1.4 (fields read before any load)
    ns, lines14 = old_defaults()
    check(int(Cfg.SWITCH_COST) == ns["DEF_SWITCH_COST"] and int(Cfg.COOLDOWN_MIN) == ns["DEF_COOLDOWN_MIN"]
          and bool(Cfg.REQUIRE_CLASS) == ns["DEF_REQUIRE_CLASS"] and bool(Cfg.UNASSIGNED_BLOCKED) == ns["DEF_UNASSIGNED_BLOCKED"]
          and bool(Cfg.PROMPT_EVERY_LOGIN) == ns["DEF_PROMPT_EVERY_LOGIN"] and int(Cfg.OPEN_DELAY_MS) == ns["DEF_OPEN_DELAY_MS"],
          "field defaults = 0.1.4 DEF_* %s" % (ns,))
    check(not bool(Cfg.ALLOW_SWITCH), "ALLOW_SWITCH is false (design lock)")
    text14 = "".join(l + "\n" for l in lines14)
    text15 = "".join(str(l) + "\n" for l in Cfg.DEFAULT_LINES)
    check(props_of(text15) == props_of(text14), "default file keys + values = 0.1.4 %s vs %s" % (props_of(text15), props_of(text14)))
    check(list(props_of(text15)) == list(props_of(text14)), "default file key order = 0.1.4")
    check([str(x) for x in Rows.defLines(0)] == [str(x) for x in Cfg.DEFAULT_LINES], "kit DEFAULTS text = ClassCfg.DEFAULT_LINES")
    print("B. defaults = 0.1.4")

    work = os.path.join(SCRATCH, "work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)

    # ---------------- C. missing file / a hand-made 0.1.4 file (ClassCfg.load, no kit yet)
    fresh = os.path.join(work, "fresh", "Skyy_SkyyClasses", "config.properties")
    Cfg.FILE = Paths.get(fresh)
    r = str(Cfg.load())
    check(os.path.isfile(fresh) and open(fresh, encoding="utf8").read() == text15, "missing file written with DEFAULT_LINES")
    check(r == str(Cfg.summary()) and r == "switchCost=5000 cooldownMinutes=60 requireClass=false unassignedBlocked=true "
          "promptEveryLogin=true openDelayMillis=2000", "load() text = summary() = the defaults: %s" % r)
    custom = os.path.join(work, "custom", "Skyy_SkyyClasses", "config.properties")
    os.makedirs(os.path.dirname(custom))
    open(custom, "w", newline="\n").write("switchCost=-5\ncooldownMinutes=abc\nrequireClass=yes\nunassignedBlocked=off\npromptEveryLogin=0\n"
                                          "openDelayMillis=100\nallowSwitch=true\nclassSwitching=true\n")
    Cfg.FILE = Paths.get(custom)
    Cfg.load()
    check(int(Cfg.SWITCH_COST) == 0 and int(Cfg.COOLDOWN_MIN) == 60 and bool(Cfg.REQUIRE_CLASS) and not bool(Cfg.UNASSIGNED_BLOCKED)
          and not bool(Cfg.PROMPT_EVERY_LOGIN) and int(Cfg.OPEN_DELAY_MS) == 250, "0.1.4 clamps and words: %s" % Cfg.summary())
    check(not bool(Cfg.ALLOW_SWITCH) and str(Hooks.customGet("classSwitching")) == "false", "allowSwitch / classSwitching lines never turn switching on")
    r = Hooks.customSet("classSwitching", "true")
    check(str(r[0]) == "bad" and r[1] is None and "design lock" in str(r[2]), "ClassHooks.customSet always refuses")
    check(Hooks.customGet("other") is None, "ClassHooks.customGet(other key) = null")
    print("C. load paths done")

    # ---------------- D. the 0.1.4 default file under the kit
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyClasses")
    os.makedirs(home)
    cfgp = os.path.join(home, "config.properties")
    open(cfgp, "w", newline="\n").write(text14)          # exactly what 0.1.4 wrote when the file was missing
    Cfg.FILE = Paths.get(cfgp)
    Cfg.load()
    check(str(Cfg.summary()) == "switchCost=5000 cooldownMinutes=60 requireClass=false unassignedBlocked=true promptEveryLogin=true "
          "openDelayMillis=2000", "0.1.4 file read back to the defaults")
    Pub.start(Paths.get(mods), None)
    bridge = Cfg.bridge()
    fn = bridge.get("config:fn:SkyyClasses")
    hdr = bridge.get("config:def:SkyyClasses")
    check(fn is not None and hdr is not None, "config:fn + config:def published")
    check(str(bridge.get("config:epoch:SkyyClasses")) == "0", "epoch starts at 0")
    check(len(hdr) == 10 and str(hdr[0]) == "1" and str(hdr[1]) == "SkyyClasses" and str(hdr[2]) == "Classes" and str(hdr[3]) == VERSION
          and str(hdr[4]) == "skyyclasses.admin", "header 0-4 %s" % ([str(hdr[i]) for i in range(5)],))
    check([str(x) for x in hdr[5]] == ["lock", "picker"] and [str(x) for x in hdr[6]] == ["Weapon lock", "Class picker"], "categories")
    check(str(hdr[8]) == "Skyy_SkyyClasses/config.properties" and 0 < len(str(hdr[9])) <= 100, "files + note")
    rows = [[str(x) for x in row] for row in hdr[7]]
    want = [("requireClass", "lock", "bool", "false", "", "", "", "", "live,danger"),
            ("unassignedBlocked", "lock", "bool", "true", "", "", "", "", "live"),
            ("promptEveryLogin", "picker", "bool", "true", "", "", "", "", "live"),
            ("openDelayMillis", "picker", "int", "2000", "250", "60000", "step=250", "ms", "live,adv"),
            ("classSwitching", "picker", "bool", "false", "", "", "", "", "ro")]
    check(len(rows) == 5 and all(len(x) == 11 for x in rows), "5 rows of 11")
    for got, w in zip(rows, want):
        check((got[0], got[2], got[3], got[4], got[5], got[6], got[7], got[8], got[9]) == w, "row %s = %s (got %s)" % (w[0], w, got))
    check(not any(x[0] in ("switchCost", "cooldownMinutes") for x in rows), "switchCost / cooldownMinutes are not rows")
    for x in rows:
        if x[0] != "classSwitching":
            check(props_of(text14).get(x[0]) == x[4], "row %s default = the 0.1.4 file value" % x[0])
    Pub.flush()
    time.sleep(0.3)
    Pub.flush()
    check(open(cfgp, "rb").read().decode("latin-1") == text14, "the kit does not rewrite the 0.1.4 file at start")
    print("D. kit header done")

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
        time.sleep(0.4)
        Pub.flush()

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    # ---------------- E. get / set
    check((get("requireClass"), get("unassignedBlocked"), get("promptEveryLogin"), get("openDelayMillis"), get("classSwitching"))
          == ("false", "true", "true", "2000", "false"), "initial gets")
    check(get("switchCost") is None and get("nope") is None, "non-row keys are unknown to get")
    r = cset("requireClass", "true", confirm="")
    check(r[0] == "confirm" and not bool(Cfg.REQUIRE_CLASS), "requireClass ON asks first, nothing changed: %s" % (r,))
    r = cset("requireClass", "true")
    check(r[0] == "ok" and r[1] == "true" and bool(Cfg.REQUIRE_CLASS), "requireClass ON with yes: %s" % (r,))
    r = cset("requireClass", "false", confirm="")
    check(r[0] == "confirm" and bool(Cfg.REQUIRE_CLASS), "requireClass OFF asks too (danger, both ways): %s" % (r,))
    r = cset("requireClass", "off")
    check(r[0] == "ok" and r[1] == "false" and not bool(Cfg.REQUIRE_CLASS), "requireClass OFF with yes (typed 'off'): %s" % (r,))
    r = cset("unassignedBlocked", "false", confirm="")
    check(r[0] == "ok" and not bool(Cfg.UNASSIGNED_BLOCKED), "unassignedBlocked asks nothing: %s" % (r,))
    r = cset("promptEveryLogin", "false", confirm="")
    check(r[0] == "ok" and not bool(Cfg.PROMPT_EVERY_LOGIN), "promptEveryLogin: %s" % (r,))
    check(cset("openDelayMillis", "100")[0] == "bad" and cset("openDelayMillis", "60250")[0] == "bad" and int(Cfg.OPEN_DELAY_MS) == 2000,
          "openDelayMillis outside 250-60000 refused (typed values are never clamped)")
    check(cset("openDelayMillis", "abc")[0] == "bad", "openDelayMillis not a number refused")
    r = cset("openDelayMillis", "3000", confirm="")
    check(r[0] == "ok" and r[1] == "3000" and int(Cfg.OPEN_DELAY_MS) == 3000, "openDelayMillis live: %s" % (r,))
    r = cset("openDelayMillis", "3000")
    check(r[0] == "ok" and "already" in r[2], "same value = already: %s" % (r,))
    r = cset("classSwitching", "true")
    check(r[0] == "bad" and not bool(Cfg.ALLOW_SWITCH) and get("classSwitching") == "false", "read-only row refused: %s" % (r,))
    check(cset("switchCost", "1")[0] == "unknown", "switchCost cannot be set through the kit")
    A = UUID.fromString("00000000-0000-0000-0000-0000000000aa")
    check(R(op("set", "unassignedBlocked", "true", A, "Someone", "yes", "menu"))[0] == "denied" and not bool(Cfg.UNASSIGNED_BLOCKED),
          "a player without skyyclasses.admin is denied")
    check(R(op("set", "unassignedBlocked", "true", None, "Ghost", "yes", "command"))[0] == "denied", "null who via command is denied")
    check(int(str(bridge.get("config:epoch:SkyyClasses"))) == 5, "epoch counts the 5 applied changes (%s)" % bridge.get("config:epoch:SkyyClasses"))
    print("E. get/set done")

    # ---------------- F. files
    settle()
    t = open(cfgp, "rb").read().decode("latin-1")
    exp = (text14.replace("unassignedBlocked=true", "unassignedBlocked=false").replace("promptEveryLogin=true", "promptEveryLogin=false")
           .replace("openDelayMillis=2000", "openDelayMillis=3000"))
    check(t == exp, "only the changed lines changed (comments, order kept, no appended header):\n%s" % t)
    lg = logs()
    check(any(l.split("\t")[1:] == ["console", "-", "console", "requireClass", "true", "false", "ok"] for l in lg)
          and any(l.split("\t")[1:] == ["console", "-", "console", "openDelayMillis", "2000", "3000", "ok"] for l in lg),
          "changes logged (console) %s" % lg[:6])
    check(os.path.isfile(os.path.join(home, "config-changes.log")), "config-changes.log written")
    v = op("versions")
    check(v is not None and len(v) >= 1 and os.path.isdir(os.path.join(home, "config-history")), "history copy made")
    print("F. files done")

    # ---------------- G. hand edits: loadInert, the kit's reload op
    open(cfgp, "w", newline="\n").write(t.replace("switchCost=5000", "switchCost=777").replace("cooldownMinutes=60", "cooldownMinutes=-3")
                                        .replace("requireClass=false", "requireClass=true").replace("openDelayMillis=3000", "openDelayMillis=100"))
    Cfg.loadInert()
    check(int(Cfg.SWITCH_COST) == 777 and int(Cfg.COOLDOWN_MIN) == 0, "loadInert re-reads switchCost / cooldownMinutes with the clamps")
    check(not bool(Cfg.REQUIRE_CLASS) and int(Cfg.OPEN_DELAY_MS) == 3000, "loadInert never touches a bound field")
    r = R(op("reload", None, None, "console"))
    check(r is not None and r[0] == "ok" and r[1] == "2" and "2 values changed by hand" in r[2], "reload op counts the 2 row edits: %s" % (r,))
    settle()
    check(bool(Cfg.REQUIRE_CLASS) and int(Cfg.OPEN_DELAY_MS) == 250, "ClassCfg.load applied them with its clamp: %s" % Cfg.summary())
    lg = logs()
    check(any(l.split("\t")[3:7] == ["file", "requireClass", "false", "true"] for l in lg)
          and any(l.split("\t")[3:7] == ["file", "openDelayMillis", "3000", "100"] for l in lg), "hand edits logged via=file %s" % lg[:6])
    check(get("openDelayMillis") == "250" and get("requireClass") == "true", "get shows the running values")
    r = R(op("reload", None, None, "console"))
    check(r[0] == "ok" and r[1] == "0", "a second reload finds nothing: %s" % (r,))
    t2 = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "w", newline="\n").write(t2 + "classSwitching=true\nallowSwitch=true\n")
    r = R(op("reload", None, None, "console"))
    settle()
    check(r[0] == "ok" and r[1] == "0" and not bool(Cfg.ALLOW_SWITCH) and get("classSwitching") == "false",
          "typed classSwitching / allowSwitch lines change nothing: %s" % (r,))
    r = cset("requireClass", "false")
    check(r[0] == "ok" and not bool(Cfg.REQUIRE_CLASS), "back to OFF")
    settle()
    s = [str(x) for x in op("status")]
    check(s[0] == "ok", "status ok %s" % s)
    print("G. hand edits done")

    # ---------------- H. player Settings
    U = UUID.fromString("00000000-0000-0000-0000-0000000000bb")
    check(bool(Cfg.notifyOn(U, "classes.blockedChat")) and bool(Cfg.notifyOn(None, "classes.blockedChat")), "no SkyyMenu = ON (0.1.4)")

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
    Cfg.regSetting("classes.blockedChat", "Blocked weapon - chat line", "combat", True, "help")
    d = bridge.get("settings:def:classes.blockedChat")
    want_d = ["SkyyClasses", "classes.blockedChat", "Blocked weapon - chat line", "combat", "true", "help"]
    got_d = None if d is None else [str(x).lower() if i == 4 else str(x) for i, x in enumerate(d)]
    got_r = [[str(x).lower() if i == 4 else str(x) for i, x in enumerate(g)] for g in fr.got]
    check(got_d == want_d and got_r == [want_d], "regSetting writes settings:def and calls settings:fn:register: %s %s" % (got_d, got_r))
    check(d is not None and JClass("java.lang.Boolean").TRUE.equals(d[4]), "the default travels as java.lang.Boolean")
    check(bool(Cfg.notifyOn(U, "classes.blockedChat")), "switch ON")
    fg.off.add("classes.blockedChat")
    check(not bool(Cfg.notifyOn(U, "classes.blockedChat")) and bool(Cfg.notifyOn(U, "classes.blockedPopup")), "chat OFF, popup still ON")
    fg.mode = "null"
    check(bool(Cfg.notifyOn(U, "classes.blockedChat")), "no answer = ON")
    fg.mode = "throw"
    check(bool(Cfg.notifyOn(U, "classes.blockedChat")), "a throwing Settings function = ON")
    fg.mode = "bool"
    Rules.WARNED.remove(U)
    Rules.POPPED.remove(U)
    try:
        Rules.tell(None, U, "x")                            # chat OFF: returns before the throttle and before pr is touched
    except Exception as ex:
        print("tell with chat OFF threw", ex)
    check(not Rules.WARNED.containsKey(U), "tell gate sits before the 3 s throttle (hidden line does not use it up)")
    fg.off.add("classes.blockedPopup")
    Rules.popup(None, U, "Weapon_Sword_Iron", "x")
    check(not Rules.POPPED.containsKey(U), "popup gate sits before the 1.5 s throttle")
    fg.off.clear()
    try:
        Rules.tell(None, U, "x")                            # ON: throttle entry made, then the null pr throws
    except Exception:
        pass
    check(Rules.WARNED.containsKey(U), "chat ON still reaches the throttle / send")
    Rules.popup(None, U, "Weapon_Sword_Iron", "x")          # popup catches its own errors
    check(Rules.POPPED.containsKey(U), "popup ON still reaches the throttle / send")
    bridge.remove("settings:fn:get")
    bridge.remove("settings:fn:register")
    bridge.remove("settings:def:classes.blockedChat")
    print("H. settings done")

    # ---------------- I. bytecode order in setup() / shutdown()
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendSystemPath()

    def code(cls, meth):
        cc = pool.get(PKG + cls)
        mm = cc.getDeclaredConstructors()[0] if meth == "<init>" else cc.getDeclaredMethod(meth)
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    su = code("SkyyClassesPlugin", "setup")

    def idx(pat, lines=su):
        return [i for i, l in enumerate(lines) if pat in l]

    ld, st, rg = idx("ClassCfg.load("), idx("CfgPub.start("), idx("ClassCfg.regSetting(")
    reg = idx("registerCommand(") + idx("registerGlobal(") + idx("registerSystem(") + idx("scheduleAtFixedRate(")
    check(len(ld) == 1 and len(st) == 1 and len(rg) == 2, "setup: one load, one CfgPub.start, two regSetting")
    check(ld and st and rg and ld[0] < min(rg) and max(rg) < st[0] and max(reg) < st[0],
          "setup order: ClassCfg.load -> registrations -> regSetting x2 -> CfgPub.start")
    txt = "\n".join(su)
    for s in ('"classes.blockedChat"', '"classes.blockedPopup"', '"Blocked weapon - chat line"', '"Blocked weapon - popup"', '"combat"'):
        check(s in txt, "setup registers %s" % s)
    after = [l for l in su[st[0] + 1:] if "invoke" in l]
    check(not any(("register" in l) or ("CfgPub" in l) or ("regSetting" in l) for l in after), "nothing is registered after CfgPub.start")
    sd = code("SkyyClassesPlugin", "shutdown")
    ps, ss = idx("CfgPub.shutdown(", sd), idx("JavaPlugin.shutdown(", sd)
    check(len(ps) == 1 and len(ss) == 1 and ps[0] < ss[0], "shutdown flushes the kit before super.shutdown()")
    rl = code("AdminReloadCmd", "execute")
    a, b, c = idx("hasPermission(", rl), idx("CfgFn.apply(", rl), idx("CfgPub.flush(", rl)
    e = idx("ClassCfg.loadInert(", rl)
    check(a and b and c and e and a[0] < b[0] < c[0] < e[0] and not idx("ClassCfg.load(", rl),
          "/classadmin reload: permission -> kit reload op -> flush -> loadInert, never ClassCfg.load directly")
    check(not idx("ClassCfg.load(", code("ClassAdminCmd", "execute")), "bare /classadmin does not re-read the file")
    print("I. bytecode order done")

    # ---------------- J. permissions: the engine's own AbstractCommand code
    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyClasses"

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Sender(object):
        def __init__(self, nodes):
            self.nodes = nodes

        def _has(self, q):
            n = str(q) if isinstance(q, str) else str(q.getId())
            return "*" in self.nodes or n in self.nodes

        @JOverride
        def hasPermission(self, *a):
            return self._has(a[0])

        @JOverride
        def getUsername(self):
            return "tester"

        @JOverride
        def getUuid(self):
            return U

        @JOverride
        def sendMessage(self, m):
            pass

    # a top-level command without requirePermission needs a PluginBase or CommandManager owner for its auto node; the engine's
    # CommandManager is allocated without running its constructor (only its type is read: the node becomes the command name)
    try:
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        own = uf.get(None).allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    except Exception as ex:
        print("no CommandManager owner (%s) - using a plain CommandOwner" % ex)
        own = Owner()
    adm, pc = JClass(PKG + "ClassAdminCmd")(), JClass(PKG + "ClassCmd")()
    subs = list(adm.getSubCommands().values())
    for c_ in [adm, pc] + subs + list(pc.getSubCommands().values()):
        c_.setOwner(own)
    check(str(adm.getPermission()) == "skyyclasses.admin" and adm.getPermissionGroups() is None, "/classadmin: requirePermission, no groups")
    check(len(subs) == 4 and all(s_.getPermissionGroups() is None and s_.getPermission() is not None for s_ in subs),
          "set / reset / info / reload: auto nodes, no groups (as 0.1.4)")
    m = adm.getPermissionGroupsRecursive()
    check(m.size() == 0, "/classadmin and its sub-commands put their nodes into NO permission group: %s" % m)
    mp = pc.getPermissionGroupsRecursive()
    allnodes = [str(x) for k in mp.keySet() for x in mp.get(k)]
    check(list(str(k) for k in mp.keySet()) == ["hytale:Adventurer"] and not any("admin" in n for n in allnodes),
          "/class gives hytale:Adventurer only player nodes: %s" % mp)
    everyone = Sender(set(allnodes))
    check(bool(pc.hasPermission(everyone)) and not bool(adm.hasPermission(everyone)), "an Adventurer may run /class, not /classadmin")
    check(all(bool(x.hasPermission(Sender({"*"}))) for x in [adm] + subs), "an op ('*') may run /classadmin and every sub-command")
    ctl = JClass(PKG + "ClassAdminCmd")()                  # control: the same command WITH groups would leak (the check can fail)
    SA = JArray(JClass("java.lang.String"))
    spg = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand").class_.getDeclaredMethod("setPermissionGroups", SA.class_)
    spg.setAccessible(True)                                # protected: called by reflection
    va = JArray(JObject)(1)
    va[0] = SA(["hytale:Adventurer"])
    spg.invoke(ctl, va)
    ctl.setOwner(own)
    cm_ = ctl.getPermissionGroupsRecursive()
    check(cm_.size() == 1 and "skyyclasses.admin" in [str(x) for x in cm_.get("hytale:Adventurer")], "control: a group list on /classadmin would leak its node")
    print("J. permissions done (sub-command nodes: %s; hytale:Adventurer gets: %s)"
          % (", ".join(sorted(str(s_.getPermission()) for s_ in subs)), ", ".join(sorted(allnodes))))

    # ---------------- K. garbage never throws
    thrown = 0
    for g in [None, [], ["nope"], ["set"], ["get"], ["get", 7], ["set", "requireClass", 5, None, None, "yes", "console"],
              ["set", "requireClass", "true", "notauuid", "n", "yes", "menu"], ["reload"], ["reload", "x", "n"], ["log", "abc"], ["status", 1]]:
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
    check(not bool(Cfg.REQUIRE_CLASS), "garbage changed nothing")
    Pub.shutdown()
    print("K. garbage done")


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyClasses/build_skyyclasses_%s.py)" % (JAR, VERSION))
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--dir", SCRATCH], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyClasses %s bare-JVM check:" % VERSION, "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
