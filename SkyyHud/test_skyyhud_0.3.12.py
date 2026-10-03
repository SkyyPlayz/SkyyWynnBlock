"""SkyyHud 0.3.12 - bare-JVM harness for the Combat Indicator widget (tools/hud_0_3_12_patch.py). Copied forward from the 0.3.11
harness: its Skills widget checks run on as regression checks (counts moved to 12 widgets), the 0.3.10 -> 0.3.11 comparisons became
0.3.11 -> 0.3.12 ones, and the Combat checks (X, R) are new.

    python SkyyHud/test_skyyhud_0.3.12.py [--jar <SkyyHud-0.3.12.jar>] [--old <SkyyHud-0.3.11.jar>] [--skills <SkyySkills 0.4.11 jar>]
                                          [--skills13 <SkyySkills 0.4.13 jar>] [--classes <SkyyClasses jar>]
                                          [--live <Skyy_SkyyHud folder>] [--dir <scratch>] [--keep] [--no-rebuild]

Build the jar first (python SkyyHud/build_skyyhud_0.3.12.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, java.io.tmpdir + TEMP/TMP in the scratch folder; HytaleServer.jar + the HUD jar + the REAL SkyySkills 0.4.11 and
SkyyClasses 0.1.10 jars for the Skills bridge contract; javassist only for the bytecode step) and check:
  A  every class of the 0.3.12 jar and of the 0.3.11 jar loads and initializes under -Xverify:all
  K-G (0.3.11's Skills checks, regression): Skills defaults, per-player lines, all 1023 masks, the class line, missing bridge,
     no SkyyClasses, the editor - with 12 widgets now (Widgets page 150 + 62 x 12, imports of 12 parts, 12 canvas handles)
  X  the Combat widget against a FAKE skill:fn:combat with the agreed contract (apply(UUID) -> Long ms left, 0 = out of combat;
     apply("window") -> Long ms, as SkyySkills 0.4.13 answers):
       X0 defaults (ON, t 0,130, 180 x 34, the 6-field line, the export part, label / short label)
       X1 missing key (SkyySkills missing / older than 0.4.13): hidden on the HUD with either out-of-combat setting, the editor still
          places it and shows "Needs SkyySkills 0.4.13" (fits the box), so does the Settings preview
       X2 out of combat, Hide (default): no markup, a tick sends nothing; the editor shows the in-combat sample (bar 0.667)
       X3 out of combat, Show: the Settings click saves the 12th field ",0"; a grey #8b949e "Out of combat" line, 26 px, no bar
       X4 in combat: the group at Top 130 / Right 870 / 180 x 34, red #ff6b6b labels, "In combat" / "6s", the vanilla ProgressBar
          with the kit's textures and the inline Value, the first fill's float Value set; check_markup; assert_proven needs exactly
          progress-element (Skyy's probe page 6) and nothing else
       X5 counting down on one HudMain: 5s 4s 3s 2s 1s - each tick exactly 2 Set commands (countdown text + bar Value), no re-send;
          an unchanged tick sends nothing; a re-hit jumps back to 6s / 0.983; 0 asks for the shape re-send (CI -> CO / C0)
       X6 colours: picked colour replaces red, glow Same follows the drawn colour, glow Black, grey ignores the palette; with glow a
          tick is 9 + 1 commands
       X7 the Combat Settings page: 1500 x 790, rows 748, the Out of combat row (Hide / Show lit, opton / optoff, 1322 px wide, the
          hint), the preview in the real colour, the 6 <-> 12 field round trip, forged line clicks ignored
       X8 the editor on Combat: drag / Size / arrows / every Snap to - the HUD margins land where the editor draws it (34 and 26 px
          boxes), on screen at 50-200 %
       X9 every size 50-200 %: drawn height <= the 34 px x size box, the bar inside it, check_markup on every shape
       X10 a misbehaving Function: Integer / Double / String / null / negative / huge / throwing answers; window answers null / 10 s /
           out of range / throwing / a String -> never an exception, sensible values
       X11 light: a hidden widget asks the Function once per tick, a shown one once + the window, a widget switched OFF never
       X12 the shape cycle: enter -> re-send asked + confirm armed; same shape -> none; leave into Hide -> re-send, no confirm
       X13 export / import / profiles / the server default carry the Combat part; a 0.3.11 code leaves Combat alone
  R  (when the SkyySkills 0.4.13 jar exists; SKIPPED otherwise) a third JVM with the REAL SkyySkills 0.4.13 CombatFn: its answers are
     java.lang.Long, its state (ManaRegen.CMB / WINDOW) drives the widget exactly like the fake (6s / 0.9, window 8000 -> 0.5,
     WINDOW 0 -> the 6000 fallback, no entry -> out of combat)
  S  0.3.11 vs 0.3.12 output for the 11 old widgets (Skills included, also SHOWN with data): HUD builds, editors (Combat hidden), all
     11 old Settings pages, the Widgets page - identical apart from the Combat widget itself (the Real Clock / Session texts compared
     as a token: the two JVMs run seconds apart and may cross a minute)
  G  the editor still places / resizes / snaps EVERY widget: drags, Size +/-, arrows and Snap to on the 11 old widgets give
     byte-identical layouts in 0.3.11 and 0.3.12
  O  0.3.11 reading a 0.3.12 layout file (rollback): every old widget loads exactly, the Combat line is ignored
  H  start twice on a scratch COPY of the live Skyy_SkyyHud data (the live folder is only read): HudCfg.load + the config kit start +
     every player's layout + HUD / editor / Settings / Widgets builds, out of combat AND in combat - no file written either time, the
     old widgets load exactly as saved, Combat appears with the defaults; then one Combat click writes exactly one line into that
     player's file only
  F1 class bytes 0.3.11 vs 0.3.12: only the expected classes / methods differ (Widgets, HudMain, SettingsPage, the version strings)
  F2 (unless --no-rebuild) 0.3.11 rebuilt in scratch with today's tools: its HUD classes equal the 0.3.11 jar's (reproducible), and its
     config kit classes differ from 0.3.12's only by the version string
Not testable without the game (UNVERIFIED in the build report): the ProgressBar inside the inline HUD document on a real client, the
widget's look, the live combat timing.
Nothing is deployed. Default scratch folder: tools/dev/scratch/hud0312/harness (git-ignored), deleted at the end unless --keep.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3.12", "0.3.11"
PKG = "com.skyy.hud."
OLD_IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild", "Skills"]
LINES = ["Overall Level", "Class skill", "Mining", "Foraging", "Farming", "Alchemy", "Smithing", "Cooking", "Acrobatics", "Exploration"]
ALL = (1 << len(LINES)) - 1
RED, GREY, NEED = "#ff6b6b", "#8b949e", "Needs SkyySkills 0.4.13"
TRACK, FILL = "Common/ProgressBar.png", "Common/ProgressBarFill.png"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0312", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
SKILLS_JAR = os.path.abspath(arg("--skills", os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.11.jar")))
SKILLS13_JAR = os.path.abspath(arg("--skills13", os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.13.jar")))
CLASSES_JAR = os.path.abspath(arg("--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.10.jar")))
LIVE = os.path.abspath(arg("--live", os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData",
                                                  "Saves", "HUD mod", "mods", "Skyy_SkyyHud")))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]
SKIPS = []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


def js(v):
    """The Java string a Set command carries (its data is JSON); non-strings come back as their JSON text."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:
        x = x["0"]
    return x if isinstance(x, str) else v


def jv(v):
    """The JSON value a Set command carries (numbers stay numbers)."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:
        x = x["0"]
    return x


# ======================================================================================================== child: one JVM, one HUD jar
def run_child(jar, out, mode):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    import skyybuild as B
    extra = [SKILLS13_JAR, CLASSES_JAR] if mode == "real" else [SKILLS_JAR, CLASSES_JAR]
    _jvm_start([jar] + extra, [B.JAVASSIST])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    res = {"jar": jar, "mode": mode, "classes": len(names), "loaded": 0, "load_fails": [], "checks": [], "scen": {}, "edit": {}}
    for n in names:
        try:
            Cls.forName(n, True, loader)
            res["loaded"] += 1
        except Exception as e:
            res["load_fails"].append("%s: %s" % (n, e))
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return

    def chk(cond, what):
        res["checks"].append([bool(cond), what])

    UUID, System, CHM = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths, Integer, Long, String = JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.String")
    Double = JClass("java.lang.Double")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    # a bare JVM has no Item asset store (the editor's canvas handles are new ItemStack(...)): an empty one, Item.UNKNOWN for every
    # id - the SkyySacks / SkyyGear harness pattern (javassist subclass of AssetStore + Item.ASSET_STORE)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = U.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)

    H = lambda n: JClass(PKG + n)
    WL, Wid, LS, HM, EP, SP, WP, Cfg, Plugin = (H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("EditorPage"),
                                               H("SettingsPage"), H("WidgetsPage"), H("HudCfg"), H("SkyyHudPlugin"))
    IDS = [str(x) for x in Wid.IDS]
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")     # jpype renames a Java member named like a Python keyword
    plugin = U.allocateInstance(Plugin.class_)
    setf(plugin, Plugin, "huds", CHM())
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(SCRATCH, "child-" + mode)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)

    def uid(n):
        return UUID(0x5ce0, n)

    def pref(n, name="Steve"):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", uid(n))
        setf(pr, PRef, "username", name)
        return pr

    def cmds(b):
        return [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]

    def evs(ev):
        return [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                 bool(e.locksInterface)] for e in ev.getEvents()]

    def use_dir(name):
        d = os.path.join(work, name)
        os.makedirs(d, exist_ok=True)
        LS.DIR = Paths.get(os.path.join(d, "layouts"))
        LS.CACHE.clear()
        EP.STEPS.clear()
        return d

    def hud(pr):
        h = HM(pr)
        b = UCB()
        mBuild.invoke(h, b)
        return h, cmds(b)

    def build_again(h):
        """build() again on the SAME HudMain (what show() sends after a re-send request)"""
        b = UCB()
        mBuild.invoke(h, b)
        return cmds(b)

    def page(p):
        b, ev = UCB(), UEB()
        p.build(None, b, ev, None)
        return cmds(b), evs(ev)

    def lay(pr, wid):
        return LS.get(pr.getUuid()).get(wid)

    def sets(cm):
        return dict((c[1], js(c[2])) for c in cm if c[0] == "Set" and c[1] and c[1].endswith(".Text"))

    def vsets(cm, sel):
        return [jv(c[2]) for c in cm if c[0] == "Set" and c[1] == sel]

    def props(f):
        out = {}
        if os.path.isfile(f):
            for ln in open(f, encoding="latin-1"):
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    out[k] = v
        return out

    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()

    # ---------------- the fake skill:fn:combat (the agreed contract; SkyySkills 0.4.13's CombatFn answers the same way)
    @JImplements("java.util.function.Function")
    class CombatFake(object):
        def __init__(self):
            self.left = {}
            self.window = Long(6000)
            self.mode = "ok"
            self.calls = 0
            self.wcalls = 0

        @JOverride
        def apply(self, x):
            if x is not None and str(x).strip().lower() == "window":
                self.wcalls += 1
                if self.mode == "throw-window":
                    raise ValueError("window boom")
                return self.window
            self.calls += 1
            if self.mode == "throw":
                raise ValueError("boom")
            v = self.left.get(str(x), 0)
            if isinstance(v, int) and not isinstance(v, bool):
                return Long(v)
            return v

    # ---------------- the REAL SkyySkills 0.4.13 CombatFn (optional third JVM)
    if mode == "real":
        MR, CF = JClass("com.skyy.skills.ManaRegen"), JClass("com.skyy.skills.CombatFn")
        JLong = JClass("long")
        fn = CF()
        bridge.put("skill:fn:combat", fn)
        u = uid(90)
        me = pref(90, "Real")
        r0 = fn.apply(u)
        chk(r0 is not None and str(r0.getClass().getName()) == "java.lang.Long" and int(r0) == 0,
            "R: the real CombatFn answers apply(UUID) with a java.lang.Long, 0 for a player never hit (%s)" % r0)
        MR.WINDOW = 6000
        rw = fn.apply("window")
        chk(rw is not None and str(rw.getClass().getName()) == "java.lang.Long" and int(rw) == 6000, "R: apply(\"window\") -> Long 6000 (%s)" % rw)
        MR.CMB.put(u, JArray(JLong)([5400, int(System.currentTimeMillis())]))
        mm = [None if x is None else str(x) for x in Wid.combatModelU(u, True)]
        chk(mm[0] == "CI" and mm[2] == "In combat" and mm[3] == "6s" and abs(float(mm[4]) - 0.9) <= 0.02 and mm[5] == "r",
            "R: a real combat entry (5.4 s left) -> In combat / 6s / bar ~0.9: %s" % mm)
        h, cm = hud(me)
        grp = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and "Group #SkyyWCombat " in c[3]]
        bv = vsets(cm, "#SkyyWCombatBar.Value")
        chk(len(grp) == 1 and "ProgressBar #SkyyWCombatBar " in grp[0] and len(bv) == 1 and abs(float(bv[0]) - 0.9) <= 0.02
            and str(h.shape.get("Combat")) == "CI", "R: the HUD built with the real Function draws the widget and sets the bar (%s)" % bv)
        MR.WINDOW = 8000
        MR.CMB.put(u, JArray(JLong)([4000, int(System.currentTimeMillis())]))
        mm = [None if x is None else str(x) for x in Wid.combatModelU(u, True)]
        chk(mm[0] == "CI" and mm[3] == "4s" and abs(float(mm[4]) - 0.5) <= 0.02, "R: WINDOW 8000, 4 s left -> 4s / bar ~0.5: %s" % mm)
        MR.WINDOW = 0
        mm = [None if x is None else str(x) for x in Wid.combatModelU(u, True)]
        chk(mm[0] == "CI" and abs(float(mm[4]) - 0.667) <= 0.02, "R: WINDOW 0 (nobody in combat yet) -> the HUD's 6000 fallback: %s" % mm)
        MR.CMB.remove(u)
        mh = [None if x is None else str(x) for x in Wid.combatModelU(u, True)]
        ms = [None if x is None else str(x) for x in Wid.combatModelU(u, False)]
        chk(mh[0] == "C0" and mh[1] is None and ms[0] == "CO" and ms[2] == "Out of combat",
            "R: no entry = out of combat -> hidden / the grey line (%s / %s)" % (mh[0], ms[0]))
        bridge.remove("skill:fn:combat")
        chk(str(Wid.combatModelU(u, False)[0]) == "C0", "R: SkyySkills' shutdown removes the key -> hidden")
        json.dump(res, open(out, "w"), indent=1)
        return

    # ---------------- party / guild bridge data (the old multi-line widgets, for the S scenarios)
    @JImplements("java.util.function.Function")
    class Members(object):
        @JOverride
        def apply(self, u):
            if str(u) in (str(uid(1)), str(uid(2)), str(uid(3))):
                return JArray(String)([str(uid(1)), str(uid(2)), str(uid(3))])
            return JArray(String)([])

    @JImplements("java.util.function.Function")
    class Online(object):
        @JOverride
        def apply(self, u):
            return JArray(String)(["Steve", "Alex", "Bea"])

    @JImplements("java.util.function.Function")
    class AnyFn(object):
        @JOverride
        def apply(self, u):
            return Integer(0)

    def party_guild():
        bridge.put("party:fn:members", Members())
        bridge.put("party:leader:" + str(uid(1)), str(uid(1)))
        for n, nm, st in ((1, "Steve", "18,20,9,10,0,0,world-a"), (2, "Alex", "20,20,10,10,40,50,world-a"), (3, "Bea", "5,20,1,10,0,0,hub")):
            bridge.put("party:name:" + str(uid(n)), nm)
            bridge.put("party:stats:" + str(uid(n)), st)
        bridge.put("guild:" + str(uid(1)), "Sky Squad")
        bridge.put("guild:info:" + str(uid(1)), "Sky Squad|SKY|3|1240|2000|3|5|Leader")
        bridge.put("guild:fn:online", Online())

    def skills_plain(u):
        """the Skills bridge keys as plain values (both jars render the same Skills widget from them)"""
        bridge.put("skill:fn:level", AnyFn())
        bridge.put("skill:" + str(u), "Mining:12,Foraging:3,Farming:1,Alchemy:2,Smithing:5,Cooking:4,Acrobatics:7,Exploration:6,Archery:18")
        bridge.put("skill:overall:" + str(u), Integer(7))
        bridge.put("class:list", "Archer,Warrior,Mage")
        bridge.put("class:skill:" + str(u), "Archery")

    def clear_bridge(prefixes):
        for k in list(bridge.keySet()):
            if any(str(k).startswith(p) for p in prefixes):
                bridge.remove(k)

    def write_layout(dirname, u, lines):
        d = os.path.join(work, dirname, "layouts")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, str(u) + ".properties"), "w", encoding="latin-1").write("#SkyyHud layout\n" + "\n".join(lines) + "\n")

    def live_layouts():
        out = []
        d = os.path.join(LIVE, "layouts")
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".properties"):
                    out.append((f[:-11], open(os.path.join(d, f), encoding="latin-1").read()))
        return out

    # ===================================================================================== S: scenarios built by both jars
    def scen(name, cm, ev=None):
        res["scen"][name] = {"cmds": cm, "evs": ev or []}

    # S1 default layout, a new player
    use_dir("s1")
    me = pref(1)
    scen("hud default", hud(me)[1])
    # S2 the live layouts (read from the live folder, written into scratch)
    for k, (us, text) in enumerate(live_layouts()):
        d = use_dir("s2-%d" % k)
        os.makedirs(os.path.join(d, "layouts"), exist_ok=True)
        open(os.path.join(d, "layouts", us + ".properties"), "w", encoding="latin-1").write(text)
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID.fromString(us))
        setf(pr, PRef, "username", "Live%d" % k)
        scen("hud live %d" % k, hud(pr)[1])
        if mode == "new":
            lay(pr, "Combat").en = False
        scen("editor live %d" % k, *page(EP(pr, plugin)))
    # S3 every old widget on, styles, party + guild
    use_dir("s3")
    party_guild()
    me = pref(1)
    m = LS.get(me.getUuid())
    pal = ["gold", "aqua", "def", "red", "lime", "def", "blue", "pink", "def", "gray", "purple"]
    for i, wid in enumerate(OLD_IDS):
        l = m.get(wid)
        l.en = True
        l.col = pal[i]
        l.glow = (i % 3 == 0)
        l.gcol = "black" if i % 2 else "def"
        l.ital = (i % 4 == 1)
        l.bold = (i % 5 != 2)
        l.scale = 50 + 13 * i
        Wid.clampToScreen(l)
    m.get("Guild").opt = True
    cm = hud(me)[1]
    scen("hud all styled", [c for c in cm if not (c[0] == "Set" and c[1] and (c[1].startswith("#SkyyWRclock") or c[1].startswith("#SkyyWSession")))])
    # S3b the same with the Skills widget SHOWN (all 10 lines, plain bridge values): 0.3.11 and 0.3.12 draw the same Skills widget
    skills_plain(me.getUuid())
    m.get("Skills").lines = ALL
    cm = hud(me)[1]
    scen("hud all styled + skills shown", [c for c in cm if not (c[0] == "Set" and c[1] and (c[1].startswith("#SkyyWRclock") or c[1].startswith("#SkyyWSession")))])
    m.get("Rclock").en = False          # both editors keep a Hidden row entry (0.3.11 would print "none" where 0.3.12 lists Combat)
    if mode == "new":
        m.get("Combat").en = False
    scen("editor all styled + skills shown", *page(EP(me, plugin)))
    clear_bridge(["skill:", "class:"])
    # S4 the editor with the default layout (Combat hidden in 0.3.12 - its handle would take a canvas cell)
    use_dir("s4")
    clear_bridge(["party:", "guild:"])
    me = pref(1)
    if mode == "new":
        lay(me, "Combat").en = False
    scen("editor default", *page(EP(me, plugin)))
    # S5 the Settings page of every old widget, S6 the Widgets page
    for wid in OLD_IDS:
        use_dir("s5-" + wid)
        scen("settings " + wid, *page(SP(pref(1), plugin, wid)))
    use_dir("s6")
    scen("widgets page", *page(WP(pref(1), plugin)))

    # ===================================================================================== G (both jars): the editor on the old widgets
    def editor_script(tag):
        """drag / size / arrows / snap every old widget with Combat hidden; returns {id: ser()} after each step group"""
        use_dir("g-" + tag)
        me = pref(7, "Ed")
        m = LS.get(me.getUuid())
        for wid in OLD_IDS:
            m.get(wid).en = True
        if mode == "new":
            m.get("Combat").en = False
        steps = {}
        ep = EP(me, plugin)
        page(ep)
        for wid in OLD_IDS:
            cells = [i for i, w in enumerate(list(ep.cellWidget)) if w is not None and str(w) == wid]
            if len(cells) != 1:
                steps[wid] = "no handle"
                continue
            frm = cells[0]
            to = min(575, frm + 3 + 2 * 32) if frm % 32 < 28 and frm // 32 < 16 else max(0, frm - 3 - 2 * 32)
            ep.handleDataEvent(None, None, '{"a":"drop","SourceSlotId":%d,"SlotIndex":%d}' % (frm, to))
            page(ep)
            a = str(m.get(wid).ser())
            ep.handleDataEvent(None, None, '{"a":"sel:%s"}' % wid)
            for act in ("Sp", "Sp", "Sp", "Lt", "Up", "Step", "Rt", "Dn", "Dn", "Sm"):
                ep.handleDataEvent(None, None, '{"a":"act:%s"}' % act)
            page(ep)
            b_ = str(m.get(wid).ser())
            sp = SP(me, plugin, wid)
            snaps = []
            for an in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br"):
                sp.handleDataEvent(None, None, '{"a":"an:%s"}' % an)
                snaps.append(str(m.get(wid).ser()))
            sp.handleDataEvent(None, None, '{"a":"sz:200"}')
            sp.handleDataEvent(None, None, '{"a":"an:br"}')
            steps[wid] = [a, b_, snaps, str(m.get(wid).ser())]
        return steps
    res["edit"] = editor_script(mode)

    # ===================================================================================== O (old jar): 0.3.11 reads a 0.3.12 file
    if mode != "new":
        lines = ["Coords=1,tr,8,8,100,1", "Skills=1,r,8,65,150,0,purple,1,0,1,black,1,1023", "Combat=1,t,0,130,100,1,def,1,0,0,def,0",
                 "Zone=0,tl,8,40,100,1,gold,1,0,0,def"]
        write_layout("o", uid(60), lines)
        use_dir("o")
        mo = LS.get(uid(60))
        res["old_reads_new"] = {"ids": sorted(str(k) for k in mo.keySet()),
                                "ser": dict((w, str(mo.get(w).ser())) for w in ("Coords", "Skills", "Zone"))}
        json.dump(res, open(out, "w"), indent=1)
        return

    # ========================================================================================== the 0.3.12-only checks
    import skyyui as SUI
    Skills = JClass("com.skyy.skills.SkillStore")
    Defs = JClass("com.skyy.skills.SkillDefs")
    Ovl = JClass("com.skyy.skills.Overall")
    SkFn = JClass("com.skyy.skills.SkillFn")
    CDefs = JClass("com.skyy.classes.ClassDefs")
    LBL = [str(x) for x in Defs.LABELS]
    CLASSES = [str(x) for x in Defs.CLASSES]
    Defs.setTable(Defs.DEFAULT_PER)
    CUM = [int(x) for x in Defs.CUM]

    @JImplements("java.util.function.Function")
    class Allowed(object):
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").TRUE

    SLOT = dict((str(n), i) for i, n in enumerate(Defs.NAMES))

    def skills_world(u, levels, cls, classes=True):
        """the REAL SkyySkills publish of one player: skill:<u> = SkillStore.levelsOf, skill:overall:<u> = Overall.publish(level of
        Overall.sums) + SkyyClasses' class:list (its setup() key = SkyyClasses installed; classes=False removes it) and class:<u> /
        class:skill:<u>; returns the expected Overall Level"""
        bridge.put("skill:fn:level", SkFn())
        bridge.put("class:fn:allowed", Allowed())
        if classes:
            bridge.put("class:list", str(CDefs.listText()))
        else:
            bridge.remove("class:list")
        if cls is None:
            bridge.remove("class:" + str(u))
            bridge.remove("class:skill:" + str(u))
        else:
            bridge.put("class:" + str(u), cls)
            bridge.put("class:skill:" + str(u), str(CDefs.SKILLS[[str(x) for x in CDefs.NAMES].index(cls)]))
        d = JArray(JClass("long"))(2 * int(Defs.N))
        for name, lv in levels.items():
            d[SLOT[name]] = CUM[lv]
        bridge.put("skill:" + str(u), str(Skills.levelsOf(u, d)))
        sc = Ovl.sums(u, d)
        ol = int(Ovl.level(sc))
        Ovl.publish(u, ol)
        return ol

    LV = {"Mining": 14, "Foraging": 9, "Farming": 3, "Acrobatics": 7, "Alchemy": 2, "Smithing": 5, "Cooking": 11, "Exploration": 6,
          "Combat.Archer": 18, "Combat.Berserker": 3}
    CLS_LIST = str(CDefs.listText())

    def lit_of(cm):
        """the lit (green) Lines buttons of a Skills Settings page build"""
        btn = dict((re.search(r"#(SkyySetLn\w+)", c[3]).group(1), c[3]) for c in cm
                   if c[0] == "AppendInline" and c[3] and "TextButton #SkyySetLn" in c[3])
        return sorted(k for k, v in btn.items() if "Background: #7fe07f" in v)

    def btn_of(cm, bid):
        """the markup of TextButton #bid in a page build (None when it is not there)"""
        got = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and ("TextButton #%s " % bid) in c[3]]
        return got[0] if len(got) == 1 else None

    def page_rows(cm):
        """(root height, vertical padding, sum of the heights of the root's direct children) of a Settings page build: the root
        #SkyySet is LayoutMode: Top, so its rows stack - each row is an AppendInline into #SkyySet with its Height in its Anchor"""
        root = [c for c in cm if c[0] == "AppendInline" and c[1] is None and c[3] and c[3].startswith("Group #SkyySet {")]
        mh = re.search(r"Anchor: \(Width: \d+, Height: (\d+)\)", root[0][3]) if root else None
        pd = re.search(r"Padding: \(Horizontal: \d+, Vertical: (\d+)\)", root[0][3]) if root else None
        tot = 0
        for c in cm:
            if c[0] == "AppendInline" and c[1] == "#SkyySet" and c[3]:
                ma = re.match(r"\s*(?:Group|Label|TextButton)(?:\s+#[A-Za-z0-9]+)?\s*\{\s*Anchor: \(([^)]*)\)", c[3])
                hv = re.search(r"Height: (\d+)", ma.group(1)) if ma else None
                tot += int(hv.group(1)) if hv else 100000
        return (int(mh.group(1)) if mh else -1, 2 * int(pd.group(1)) if pd else 100000, tot)

    def start_lines(wid):
        """Widgets.startLines (review fix LOW 2); None when the jar has no such method (a check fails instead of the run crashing)"""
        try:
            return int(Wid.startLines(wid))
        except Exception:
            return None

    def hint_of(cm):
        return [c[3] for c in cm if c[0] == "AppendInline" and c[1] == "#SkyySetRowLnH" and c[3] and "Click a line" in c[3]]

    # ---- K: the bridge contract with the real mods
    chk(all(x in LBL for x in LINES[2:]), "K: every HUD skill line is a SkyySkills label: %s / %s" % (LINES[2:], LBL))
    chk(all(str(s) in LBL for s in CDefs.SKILLS), "K: every SkyyClasses class skill is a SkyySkills label: %s" % [str(s) for s in CDefs.SKILLS])
    chk(IDS == OLD_IDS + ["Combat"], "K: Combat is APPENDED to Widgets.IDS (old codes / files keep their meaning): %s" % IDS)

    # ---- B: Skills defaults (regression)
    use_dir("b")
    d0 = wdef("Skills")
    chk(bool(d0.en) and str(d0.anchor) == "tl" and int(d0.dx) == 8 and int(d0.dy) == 544 and int(d0.scale) == 100 and int(d0.bw) == 180
        and int(d0.bh) == 206 and int(d0.lines) == 3 and int(d0.ldef) == 3 and bool(d0.bg) and bool(d0.styleDefault()),
        "B: Widgets.def(Skills) = ON tl 8,544 100%% 180x206 lines 3 (got %s %s %s)" % (d0.ser(), d0.lines, d0.ldef))
    for wid in OLD_IDS[:-1] + ["Combat"]:
        dd = wdef(wid)
        chk(int(dd.lines) == -1 and int(dd.ldef) == -1, "B: %s has no lines (ldef -1)" % wid)
    me = pref(1)
    ol = skills_world(me.getUuid(), LV, "Archer")
    chk(ol == (14 + 9 + 3 + 7 + 2 + 5 + 11 + 6 + 18) // 9, "B: real Overall.sums = the 8 skills + the class skill (got %d)" % ol)
    l = lay(me, "Skills")
    chk(str(l.ser()) == "1,tl,8,544,100,1" and int(l.lines) == 3, "B: a new player's Skills layout = the default, 6-field line (%s)" % l.ser())
    chk("Skills=1:tl:8:544:100:1" in str(LS.export(me.getUuid())), "B: export carries the default Skills part")
    h, cm = hud(me)
    sk = [c for c in cm if c[0] == "AppendInline" and c[3] and "#SkyyWSkills " in c[3]]
    chk(len(sk) == 1 and "Anchor: (Top: 544, Left: 8, Width: 180, Height: 46)" in sk[0][3] and "Background: #0b1524(0.72)" in sk[0][3],
        "B: the HUD draws one Skills group at tl 8,544, 180 x 46 (2 lines): %s" % (sk[0][3][:140] if sk else None))
    if sk:
        for x in ("#SkyyWSkillsN0Txt", "#SkyyWSkillsS0Txt", "#SkyyWSkillsN1Txt", "#SkyyWSkillsS1Txt"):
            chk(x in sk[0][3], "B: label %s exists" % x)
        chk("#SkyyWSkillsN2Txt" not in sk[0][3] and "G0 " not in sk[0][3], "B: no third line, no glow copies by default")
        try:
            SUI.check_markup(sk[0][3])
            chk(True, "")
        except ValueError as e:
            chk(False, "B: check_markup(Skills group): %s" % e)
    chk(not any("SkyyWCombat" in str(c[3]) + str(c[1]) for c in cm), "B: no skill:fn:combat in this bridge -> no Combat markup")
    st = sets(cm)
    chk(st.get("#SkyyWSkillsN0Txt.Text") == "Overall Level" and st.get("#SkyyWSkillsS0Txt.Text") == str(ol)
        and st.get("#SkyyWSkillsN1Txt.Text") == "Archery" and st.get("#SkyyWSkillsS1Txt.Text") == "18",
        "B: lines Overall Level %d / Archery 18: %s" % (ol, dict((k, v) for k, v in st.items() if "Skills" in k)))
    chk(str(h.shape.get("Skills")) == "K2", "B: shape K2")
    ec, ee = page(EP(me, plugin))
    chk(any(c[3] and "Group #SkyyEPvSkills " in c[3] for c in ec if c[0] == "AppendInline")
        and any(e[1] == "#SkyyESelSkills" for e in ee), "B: the editor previews the widget and lists it in the Select row")
    wc, we = page(WP(me, plugin))
    chk(any(c[3] and "#SkyyWRowSkills " in c[3] for c in wc if c[0] == "AppendInline") and sum(1 for e in we if "Skills" in str(e[2])) == 3,
        "B: the Widgets page has a Skills row (ON / OFF / Settings)")
    chk(any(c[3] and "#SkyyWRowCombat " in c[3] for c in wc if c[0] == "AppendInline") and sum(1 for e in we if "Combat" in str(e[2])) == 3,
        "B: the Widgets page has a Combat row (ON / OFF / Settings)")
    chk(any(c[3] and "Height: %d)" % (150 + 62 * 12) in c[3] for c in wc[:1]) and 150 + 62 * 12 <= 1080, "B: the Widgets page is 150 + 62 x 12 px high")
    scm, sce = page(SP(me, plugin, "Skills"))
    chk(scm and "Anchor: (Width: 1500, Height: 940)" in (scm[0][3] or ""), "B: the Skills Settings page is 1500 x 940")
    # review fix LOW 1 (0.3.11): every Settings page's rows + padding fit its root with at least 20 px to spare, and the page fits 1080
    for wid in IDS:
        ph_, pad_, rows_ = page_rows(page(SP(me, plugin, wid))[0])
        spare = ph_ - pad_ - rows_
        chk(20 <= spare and ph_ <= 1080 and (wid != "Skills" or (ph_, rows_) == (940, 894)) and (wid == "Skills" or (ph_, rows_) == (790, 748)),
            "B: Settings page %s: rows %d + padding %d in %d px -> %d px spare (need >= 20; Skills 894 of 940, the others 748 of 790)"
            % (wid, rows_, pad_, ph_, spare))
    chk(len(hint_of(scm)) == 1 and '- Class skill follows your class"' in hint_of(scm)[0] and "needs SkyyClasses" not in hint_of(scm)[0],
        "B: with SkyyClasses the hint ends 'Class skill follows your class': %s" % hint_of(scm))
    lnb = [e for e in sce if e[1] and e[1].startswith("#SkyySetLn")]
    want_b = [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(5)] + [("#SkyySetLnAll", '"lnall"')] + \
             [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(5, 10)] + [("#SkyySetLnDef", '"lndef"')]
    chk(len(lnb) == len(want_b) and all(e[1] == w[0] and w[1] in (e[2] or "") and e[0] == "Activating" for e, w in zip(lnb, want_b)),
        "B: Lines toggles ln:0-9 + All on + Default: %s" % [(e[0], e[1], e[2]) for e in lnb])
    lit = lit_of(scm)
    chk(lit == ["SkyySetLn0", "SkyySetLn1", "SkyySetLnDef"], "B: lit = Overall Level, Class skill, Default: %s" % lit)
    chk(not any(e[1] in ("#SkyySetOptOn", "#SkyySetOptOff") for e in sce), "B: no option row on the Skills page")
    for c in scm:
        if c[0] == "AppendInline" and c[3] and ("SkyySetLn" in c[3] or "SkyySetRowLn" in (c[1] or "") or "SkyySetRowLn" in c[3]):
            try:
                SUI.check_markup(c[3])
                chk(True, "")
            except ValueError as e:
                chk(False, "B: check_markup(Lines row): %s: %s" % (e, c[3][:100]))
    labels = [js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"]
    chk(labels == ["Overall Level " + str(ol)], "B: the Settings preview shows the first line: %s" % labels)

    # ---- C: Skills per-player persistence (regression; 12 widgets in a code now)
    A, Bp = pref(11, "Ann"), pref(12, "Bob")
    use_dir("c")
    for p in (A, Bp):
        skills_world(p.getUuid(), LV, "Archer")
    fa = os.path.join(work, "c", "layouts", str(A.getUuid()) + ".properties")
    fb = os.path.join(work, "c", "layouts", str(Bp.getUuid()) + ".properties")
    spA = SP(A, plugin, "Skills")
    spA.handleDataEvent(None, None, '{"a":"ln:2"}')
    chk(int(lay(A, "Skills").lines) == 7 and props(fa).get("Skills") == "1,tl,8,544,100,1,def,1,0,0,def,1,7",
        "C: Ann turns Mining on -> mask 7, her file: %s" % props(fa).get("Skills"))
    chk(props(fa).get("Combat") == "1,t,0,130,100,1", "C: ... and her file holds the default Combat line: %s" % props(fa).get("Combat"))
    chk(not os.path.isfile(fb) and int(lay(Bp, "Skills").lines) == 3, "C: Bob untouched (no file, mask 3)")
    LS.CACHE.clear()
    chk(int(lay(A, "Skills").lines) == 7 and int(lay(Bp, "Skills").lines) == 3, "C: after a reload Ann 7, Bob 3")
    st = sets(hud(A)[1])
    chk([st.get("#SkyyWSkillsN%dTxt.Text" % k) for k in range(4)] == ["Overall Level", "Archery", "Mining", None]
        and st.get("#SkyyWSkillsS2Txt.Text") == "14", "C: Ann's HUD: Overall / Archery / Mining 14")
    for k, want in ((0, 6), (1, 4), (2, 4)):
        spA.handleDataEvent(None, None, '{"a":"ln:%d"}' % k)
        chk(int(lay(A, "Skills").lines) == want, "C: ln:%d -> %d (got %d)" % (k, want, int(lay(A, "Skills").lines)))
    chk(props(fa).get("Skills", "").endswith(",1,4"), "C: the last line stayed on and is saved (%s)" % props(fa).get("Skills"))
    spA.handleDataEvent(None, None, '{"a":"lnall"}')
    chk(int(lay(A, "Skills").lines) == ALL and props(fa).get("Skills", "").endswith(",1,%d" % ALL), "C: All on -> %d" % ALL)
    cmA, _ = page(spA)
    chk(sum(1 for c in cmA if c[0] == "AppendInline" and c[3] and "TextButton #SkyySetLn" in c[3] and "Background: #7fe07f" in c[3]) == 11,
        "C: All on lights all 10 lines + All on")
    spA.handleDataEvent(None, None, '{"a":"lndef"}')
    chk(int(lay(A, "Skills").lines) == 3 and props(fa).get("Skills") == "1,tl,8,544,100,1", "C: Default -> back to the 6-field line")
    spA.handleDataEvent(None, None, '{"a":"ln:5"}')
    spA.handleDataEvent(None, None, '{"a":"ln:9"}')
    code = str(LS.export(A.getUuid()))
    chk("Skills=1:tl:8:544:100:1:def:1:0:0:def:1:547" in code, "C: export carries mask 547 (%s)" % code[-90:])
    Cc = pref(13, "Cid")
    n = int(LS.importCode(Cc.getUuid(), code))
    chk(n == 12 and int(lay(Cc, "Skills").lines) == 547 and int(lay(Cc, "Skills").ldef) == 3, "C: import into another player keeps 547 (12 parts, got %d)" % n)
    chk(bool(LS.profileSave(A.getUuid(), "mine")), "C: profile save")
    spA.handleDataEvent(None, None, '{"a":"lndef"}')
    chk(int(LS.profileLoad(A.getUuid(), "mine")) == 12 and int(lay(A, "Skills").lines) == 547, "C: profile load brings 547 back")
    n = int(LS.importCode(Cc.getUuid(), "Coords=1:tr:8:8:100:1;Zone=0:tl:8:8:100:1"))
    chk(n == 2 and int(lay(Cc, "Skills").lines) == 547, "C: a 0.3.10 code imports 2 widgets, Skills unchanged")
    n = int(LS.importCode(Cc.getUuid(), "Skills=1:tl:8:544:100:1"))
    chk(n == 1 and int(lay(Cc, "Skills").lines) == 3, "C: a Skills part without a mask = the default lines")
    Cfg.DEFAULT_LAYOUT = "Skills=1:tr:8:72:100:1:def:1:0:0:def:1:5"
    chk(Cfg.codeError(Cfg.DEFAULT_LAYOUT) is None, "C: a server default code with a Skills mask is valid")
    Dp = pref(14, "Dot")
    ld = lay(Dp, "Skills")
    chk(str(ld.anchor) == "tr" and int(ld.dy) == 72 and int(ld.lines) == 5 and int(ld.ldef) == 3, "C: a new player gets the server default (tr, mask 5)")
    fdot = os.path.join(work, "c", "layouts", str(Dp.getUuid()) + ".properties")
    spDot = SP(Dp, plugin, "Skills")
    lt = lit_of(page(spDot)[0])
    chk(lt == ["SkyySetLn0", "SkyySetLn2", "SkyySetLnDef"], "C: on the server default (mask 5) Default is lit with Overall Level + Mining: %s" % lt)
    chk(start_lines("Skills") == 5 and start_lines("Party") == -1 and start_lines("Combat") == -1, "C: startLines = the server default's 5 (Party / Combat: -1)")
    spDot.handleDataEvent(None, None, '{"a":"ln:3"}')
    lt = lit_of(page(spDot)[0])
    chk(int(lay(Dp, "Skills").lines) == 13 and "SkyySetLnDef" not in lt, "C: Foraging on -> 13, Default not lit: %s" % lt)
    spDot.handleDataEvent(None, None, '{"a":"lndef"}')
    chk(int(lay(Dp, "Skills").lines) == 5 and props(fdot).get("Skills") == "1,tr,8,72,100,1,def,1,0,0,def,1,5"
        and "SkyySetLnDef" in lit_of(page(spDot)[0]),
        "C: Default -> the server default's 5, lit, saved as a 13th field (ldef stays the built-in 3): %s" % props(fdot).get("Skills"))
    Cfg.DEFAULT_LAYOUT = "Skills=1:tr:8:72:100:1"
    spDot.handleDataEvent(None, None, '{"a":"lndef"}')
    lt = lit_of(page(spDot)[0])
    chk(int(lay(Dp, "Skills").lines) == 3 and props(fdot).get("Skills") == "1,tr,8,72,100,1" and lt == ["SkyySetLn0", "SkyySetLn1", "SkyySetLnDef"],
        "C: a server default Skills part without a mask -> Default = the built-in 3, the 6-field line, lit %s" % lt)
    for code in ("Skills=1:tr:8:72:100:1:def:1:0:0:def:1:1024", "Coords=1:tl:8:8:100:1", ""):
        Cfg.DEFAULT_LAYOUT = code
        spDot.handleDataEvent(None, None, '{"a":"ln:4"}')
        spDot.handleDataEvent(None, None, '{"a":"lndef"}')
        chk(int(lay(Dp, "Skills").lines) == 3 and start_lines("Skills") == 3, "C: server default %r -> Default = the built-in 3" % code)
    Cfg.DEFAULT_LAYOUT = "Skills=1:tr:8:72:100:1:def:1:0:0:def:1:5"
    LS.reset(A.getUuid())
    chk(int(lay(A, "Skills").lines) == 5 and str(lay(A, "Skills").anchor) == "tr", "C: /skyyhud reset -> the server default incl. its mask")
    Cfg.DEFAULT_LAYOUT = ""
    LS.reset(A.getUuid())
    chk(int(lay(A, "Skills").lines) == 3 and props(fa).get("Skills") == "1,tl,8,544,100,1", "C: reset with no server default -> built-in")
    chk(Cfg.codeError("Skills=1:tl:8") is not None, "C: a broken Skills part is refused as a server default")
    before = str(lay(A, "Party").ser())
    for pl in ('{"a":"ln:2"}', '{"a":"lnall"}', '{"a":"lndef"}'):
        SP(A, plugin, "Party").handleDataEvent(None, None, pl)
    chk(str(lay(A, "Party").ser()) == before and int(lay(A, "Party").lines) == -1, "C: line clicks on the Party page change nothing")
    for pl in ('{"a":"ln:10"}', '{"a":"ln:-1"}', '{"a":"ln:x"}', '{"a":"ln:99999999999"}'):
        spA.handleDataEvent(None, None, pl)
    chk(int(lay(A, "Skills").lines) == 3, "C: out-of-range line clicks change nothing")
    for bad, want_scale in (("0", 100), ("-4", 100), ("abc", 125), ("", 100), ("2147483648", 100)):
        write_layout("c-bad", uid(30), ["Skills=1,tl,8,544,%d,1,def,1,0,0,def,1,%s" % (want_scale, bad)])
        use_dir("c-bad")
        lb = lay(pref(30), "Skills")
        chk(int(lb.lines) == 3 and int(lb.scale) == want_scale and str(lb.anchor) == "tl", "C: mask %r in a file -> default 3, rest kept" % bad)
    write_layout("c-bad", uid(30), ["Skills=1,tl,8,544,100,1,def,1,0,0,def,1,1031"])
    use_dir("c-bad")
    chk(int(lay(pref(30), "Skills").lines) == 1031 and str(lay(pref(30), "Skills").ser()).endswith(",1031"), "C: an unknown future bit is kept")

    # ---- D: Skills - any combo (regression)
    use_dir("d")
    me = pref(1)
    skills_world(me.getUuid(), LV, "Archer")
    vals = {"Overall Level": str(ol), "Class skill": "18", "Mining": "14", "Foraging": "9", "Farming": "3", "Alchemy": "2", "Smithing": "5",
            "Cooking": "11", "Acrobatics": "7", "Exploration": "6"}
    bad = []
    l = lay(me, "Skills")
    for mask in range(1, ALL + 1):
        mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), mask)]
        want = [k for k in range(len(LINES)) if mask & (1 << k)]
        names = [("Archery" if k == 1 else LINES[k]) for k in want]
        got_n = [mm[2 + 2 * i] for i in range(len(LINES)) if mm[2 + 2 * i] is not None]
        got_v = [mm[3 + 2 * i] for i in range(len(want))]
        exp_v = [vals[LINES[k]] for k in want]
        pairs = [str(x) for x in Wid.linePairs("Skills", Wid.skillsModelU(me.getUuid(), mask))]
        ok = (got_n == names and got_v == exp_v and mm[0] == "K%d" % len(want) and mm[1] == names[0] + " " + exp_v[0]
              and pairs == sum([["N%d" % i, names[i], "S%d" % i, exp_v[i]] for i in range(len(want))], [])
              and int(Wid.bodyH("Skills", Wid.skillsModelU(me.getUuid(), mask), 100)) == 6 + 20 * len(want))
        l.lines = mask
        s_ = str(l.ser())
        back = WL.parse(s_, wdef("Skills"))
        ok = ok and int(back.lines) == mask and (s_ == "1,tl,8,544,100,1") == (mask == 3)
        body = str(Wid.skillsBody("SkyyWSkills", l, 100, Wid.skillsModelU(me.getUuid(), mask), 6))
        ok = ok and body.count("Label #SkyyWSkillsN") == len(want) and body.count("Label #SkyyWSkillsS") == len(want)
        if not ok:
            bad.append(mask)
    chk(not bad, "D: all %d masks: lines, order, names, values, shape, pairs, height, ser/parse, markup (bad: %s)" % (ALL, bad[:10]))
    bridge.remove("class:list")
    bad = []
    for mask in range(1, ALL + 1):
        mk = Wid.skillsModelU(me.getUuid(), mask)
        mm = [None if x is None else str(x) for x in mk]
        want = [k for k in range(len(LINES)) if mask & (1 << k) and k != 1]
        names = [LINES[k] for k in want]
        exp_v = [vals[LINES[k]] for k in want]
        got_n = [mm[2 + 2 * i] for i in range(len(LINES)) if mm[2 + 2 * i] is not None]
        got_v = [mm[3 + 2 * i] for i in range(len(want))]
        ok = (got_n == names and got_v == exp_v and mm[0] == "K%d" % len(want)
              and (mm[1] == names[0] + " " + exp_v[0] if want else mm[1] is None)
              and int(Wid.bodyH("Skills", mk, 100)) == 6 + 20 * len(want))
        if not ok:
            bad.append(mask)
    chk(not bad, "D: all %d masks without SkyyClasses: only the Class skill line is left out (bad: %s)" % (ALL, bad[:10]))
    bridge.put("class:list", CLS_LIST)
    for mask in (1, 2, 3, 512, 1023, 341, 682):
        for sc in (50, 70, 100, 130, 200):
            l.lines, l.scale = mask, sc
            src = str(Wid.multiWidgetSrc("Skills", l, Wid.modelL("Skills", me, l)))
            try:
                SUI.check_markup(src)
            except ValueError as e:
                chk(False, "D: check_markup mask %d @%d: %s" % (mask, sc, e))
            hh = int(Wid.bodyH("Skills", Wid.modelL("Skills", me, l), sc))
            chk("Height: %d)" % hh in src and hh <= int(Wid.hMax(l)), "D: mask %d @%d%%: group height %d <= max box %d" % (mask, sc, hh, int(Wid.hMax(l))))
    l.lines, l.scale = 3, 100
    rnd = random.Random(311)
    spD = SP(me, plugin, "Skills")
    seen = set()
    fd = os.path.join(work, "d", "layouts", str(me.getUuid()) + ".properties")
    okseq = True
    for step in range(1500):
        r_ = rnd.random()
        pl = '{"a":"lnall"}' if r_ < 0.03 else ('{"a":"lndef"}' if r_ < 0.06 else '{"a":"ln:%d"}' % rnd.randrange(10))
        prev = int(lay(me, "Skills").lines)
        spD.handleDataEvent(None, None, pl)
        cur = int(lay(me, "Skills").lines)
        k = re.search(r"ln:(\d+)", pl)
        exp = ALL if "lnall" in pl else (3 if "lndef" in pl else (prev ^ (1 << int(k.group(1)))))
        if exp == 0:
            exp = prev
        saved = props(fd).get("Skills", "")
        if cur != exp or cur == 0 or (cur != 3 and not saved.endswith(",%d" % cur)) or (cur == 3 and saved != "1,tl,8,544,100,1"):
            okseq = False
        seen.add(cur)
    chk(okseq and len(seen) > 300, "D: 1500 random clicks: every state as expected and saved, never 0 (%d masks reached)" % len(seen))

    # ---- E: Skills - the class line follows the class (regression)
    use_dir("e")
    me = pref(1)
    skills_world(me.getUuid(), LV, "Archer")
    h, cm = hud(me)
    b0 = UCB()
    re_ = bool(h.fill(b0, False))
    chk(not re_ and not [c for c in cmds(b0) if "Skills" in str(c[1])], "E: a tick with nothing new sends no Skills text")
    chk(int(h.confirmAt) > 0, "E: the first build arms the one confirm send (join / world switch)")
    h.confirmAt = 1
    h.tick()
    c1 = int(h.confirmAt)
    build_again(h)
    chk(c1 == 0 and int(h.confirmAt) == 0, "E: after it fired, a rebuild with the same shape arms no further confirm send (never periodic): %d / %d"
        % (c1, int(h.confirmAt)))
    skills_world(me.getUuid(), LV, "Berserker")
    b1 = UCB()
    re_ = bool(h.fill(b1, False))
    s1 = sets(cmds(b1))
    chk(not re_ and s1.get("#SkyyWSkillsN1Txt.Text") == "Fury" and s1.get("#SkyyWSkillsS1Txt.Text") == "3",
        "E: class change Archer -> Berserker: .Text sets Fury / 3, no re-send: %s" % s1)
    lv2 = dict(LV)
    lv2["Combat.Berserker"] = 4
    lv2["Mining"] = 15
    ol2 = skills_world(me.getUuid(), lv2, "Berserker")
    b2 = UCB()
    h.fill(b2, False)
    s2 = sets(cmds(b2))
    chk(s2.get("#SkyyWSkillsS1Txt.Text") == "4" and "#SkyyWSkillsN1Txt.Text" not in s2 and s2.get("#SkyyWSkillsS0Txt.Text", str(ol2)) == str(ol2),
        "E: a level up sends only the changed values: %s" % s2)
    for ci, cname in enumerate(CLASSES):
        lv3 = dict(LV)
        lv3["Combat." + cname] = 20 + ci
        skills_world(me.getUuid(), lv3, cname)
        mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), 3)]
        skn = str(CDefs.SKILLS[[str(x) for x in CDefs.NAMES].index(cname)])
        chk(mm[4] == skn and mm[5] == str(20 + ci), "E: %s -> class line %s %d (got %s %s)" % (cname, skn, 20 + ci, mm[4], mm[5]))
    skills_world(me.getUuid(), LV, None)
    mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), 3)]
    chk(mm[4] == "Class skill" and mm[5] == "-" and mm[0] == "K2", "E: no class -> 'Class skill -' (still 2 lines)")
    lv4 = {"Mining": 1, "Combat.Mage": 2}
    skills_world(me.getUuid(), LV, "Archer")
    h, cm = hud(me)
    skills_world(me.getUuid(), lv4, "Mage")
    b3 = UCB()
    re_ = bool(h.fill(b3, False))
    s3 = sets(cmds(b3))
    chk(not re_ and s3.get("#SkyyWSkillsN1Txt.Text") == "Sorcery" and s3.get("#SkyyWSkillsS1Txt.Text") == "2", "E: profile switch -> Sorcery 2: %s" % s3)

    # ---- F: Skills - missing / broken bridge (regression)
    use_dir("f")
    me = pref(1)
    System.getProperties().remove("skyy.bridge")
    mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), ALL)]
    chk(mm[0] == "K0" and mm[1] is None, "F: no skyy.bridge at all -> hidden")
    chk(str(Wid.combatModelU(me.getUuid(), False)[0]) == "C0" and int(Wid.combatLeft(None, me.getUuid())) == -1,
        "F: no skyy.bridge at all -> Combat hidden too (combatLeft -1)")
    h, cm = hud(me)
    chk(not any("SkyyWSkills" in str(c[3]) + str(c[1]) for c in cm) and str(h.shape.get("Skills")) == "K0", "F: ... the HUD draws no Skills widget")
    ec, ee = page(EP(me, plugin))
    stE = sets(ec)
    chk(stE.get("#SkyyEPvSkillsN0Txt.Text") == "Skills not installed" and "#SkyyEPvSkillsN1Txt.Text" not in stE,
        "F: ... the editor shows one line 'Skills not installed'")
    chk(stE.get("#SkyyEPvCombatN0Txt.Text") == NEED, "F: ... and the Combat stand-in '%s'" % NEED)
    scm, _ = page(SP(me, plugin, "Skills"))
    chk([js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"] == ["Skills not installed"], "F: ... and so does the Settings preview")
    System.getProperties().put("skyy.bridge", bridge)
    bridge.clear()
    chk(str(Wid.skillsModelU(me.getUuid(), 3)[0]) == "K0", "F: a bridge without SkyySkills (no skill:fn:level) -> hidden")
    bridge.put("skill:fn:level", SkFn())
    mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), ALL)]
    chk(mm[0] == "K9" and all(mm[3 + 2 * i] == "-" for i in range(9)) and mm[2] == "Overall Level" and mm[4] == "Mining"
        and "Class skill" not in mm and mm[20] is None,
        "F: SkyySkills without SkyyClasses, nothing published yet -> 9 lines of '-', no Class skill line: %s" % mm[:6])
    chk(str(Wid.combatModelU(me.getUuid(), False)[0]) == "C0", "F: SkyySkills 0.4.12 or older (skill:fn:level, no skill:fn:combat) -> Combat hidden")
    bridge.put("class:list", CLS_LIST)
    mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), ALL)]
    chk(mm[0] == "K10" and all(mm[3 + 2 * i] == "-" for i in range(10)) and mm[4] == "Class skill",
        "F: + SkyyClasses (class:list), no class yet, nothing published -> 10 lines of '-' incl. 'Class skill -'")
    for junk in (Integer(5), "Mining", "Mining:abc,:3,Foraging:,Farming:-2,Alchemy:4.6, mining : 8 ", "x" * 5000, ""):
        bridge.put("skill:" + str(me.getUuid()), junk)
        bridge.put("skill:overall:" + str(me.getUuid()), "x")
        try:
            mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), ALL)]
            ok = mm[0] == "K10" and mm[3] == "-"
            if isinstance(junk, str) and junk.startswith("Mining:abc"):
                ok = ok and mm[7] == "-" and mm[9] == "-" and mm[11] == "-" and mm[13] == "5"
            chk(ok, "F: garbage skill:<u> %r -> no error: %s" % (str(junk)[:30], mm[:14]))
        except Exception as e:
            chk(False, "F: garbage skill:<u> %r threw %s" % (str(junk)[:30], e))
    bridge.clear()
    use_dir("f2")
    me = pref(2)
    h, cm = hud(me)
    chk(str(h.shape.get("Skills")) == "K0", "F: hidden at the first build")
    skills_world(me.getUuid(), LV, "Archer")
    b4 = UCB()
    chk(bool(h.fill(b4, False)), "F: SkyySkills data arrives -> fill asks for the re-send (shape K0 -> K2)")
    h2, cm2 = hud(me)
    chk(any("#SkyyWSkills " in str(c[3]) for c in cm2), "F: the re-sent HUD has the widget")
    lay(me, "Skills").lines = 1024
    mm = [None if x is None else str(x) for x in Wid.modelL("Skills", me, lay(me, "Skills"))]
    stE = sets(page(EP(me, plugin))[0])
    chk(mm[0] == "K0" and stE.get("#SkyyEPvSkillsN0Txt.Text") == "No lines to show", "F: a mask with only unknown bits -> hidden, editor 'No lines to show'")
    lay(me, "Skills").lines = 3
    # ---- F3: SkyyClasses NOT installed (no class:list - a stale class:skill:<u> stays in the bridge on purpose)
    bridge.clear()
    use_dir("f3")
    me = pref(3, "Nox")
    ln_ = lambda: int(lay(me, "Skills").lines)
    skills_world(me.getUuid(), LV, "Archer", classes=False)
    h, cm = hud(me)
    st = sets(cm)
    sk = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and "#SkyyWSkills " in c[3]]
    chk(str(h.shape.get("Skills")) == "K1" and st.get("#SkyyWSkillsN0Txt.Text") == "Overall Level" and "#SkyyWSkillsN1Txt.Text" not in st
        and len(sk) == 1 and "Width: 180, Height: 26)" in sk[0] and "Archery" not in st.values(),
        "F: no SkyyClasses -> the default widget is one line, Overall Level (26 px): %s" % dict((k, v) for k, v in st.items() if "Skills" in k))
    spN = SP(me, plugin, "Skills")
    scN, _ = page(spN)
    lt = lit_of(scN)
    chk(len(hint_of(scN)) == 1 and '- Class skill needs SkyyClasses"' in hint_of(scN)[0] and lt == ["SkyySetLn0", "SkyySetLn1", "SkyySetLnDef"],
        "F: no SkyyClasses -> the hint ends 'Class skill needs SkyyClasses', lit %s" % lt)
    spN.handleDataEvent(None, None, '{"a":"ln:0"}')
    chk(ln_() == 3, "F: no SkyyClasses: Overall Level (the only line that can show) cannot be switched off (mask stays 3, got %d)" % ln_())
    spN.handleDataEvent(None, None, '{"a":"ln:1"}')
    chk(ln_() == 1, "F: ... Class skill can be switched off -> 1 (got %d)" % ln_())
    spN.handleDataEvent(None, None, '{"a":"ln:0"}')
    chk(ln_() == 1, "F: ... and the last line still stays on (got %d)" % ln_())
    lay(me, "Skills").lines = 2
    mm = [None if x is None else str(x) for x in Wid.modelL("Skills", me, lay(me, "Skills"))]
    stE = sets(page(EP(me, plugin))[0])
    pvN = [js(c[2]) for c in page(spN)[0] if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"]
    chk(mm[0] == "K0" and stE.get("#SkyyEPvSkillsN0Txt.Text") == "No lines to show" and pvN == ["No lines to show"],
        "F: only Class skill without SkyyClasses -> hidden; the editor and the Settings preview say 'No lines to show' (%s / %s)"
        % (stE.get("#SkyyEPvSkillsN0Txt.Text"), pvN))
    spN.handleDataEvent(None, None, '{"a":"ln:1"}')
    chk(ln_() == 2, "F: ... switching Class skill off as well is refused (got %d)" % ln_())
    spN.handleDataEvent(None, None, '{"a":"lndef"}')
    chk(ln_() == 3, "F: ... Default -> 3 (got %d)" % ln_())
    Cfg.DEFAULT_LAYOUT = "Skills=1:tl:8:544:100:1:def:1:0:0:def:1:2"
    chk(start_lines("Skills") == 3, "F: a server default of only Class skill shows nothing without SkyyClasses -> Default = the built-in 3")
    bridge.put("class:list", CLS_LIST)
    chk(start_lines("Skills") == 2, "F: ... with SkyyClasses the same server default -> Default = 2")
    bridge.remove("class:list")
    Cfg.DEFAULT_LAYOUT = ""
    rnd2 = random.Random(3110)
    okn, seen2 = True, set()
    for step in range(600):
        r_ = rnd2.random()
        pl = '{"a":"lnall"}' if r_ < 0.03 else ('{"a":"lndef"}' if r_ < 0.06 else '{"a":"ln:%d"}' % rnd2.randrange(10))
        spN.handleDataEvent(None, None, pl)
        cur = ln_()
        seen2.add(cur)
        if cur & (ALL - 2) == 0 or not bool(Wid.shown(Wid.modelL("Skills", me, lay(me, "Skills")))):
            okn = False
    chk(okn and len(seen2) > 150, "F: 600 random clicks without SkyyClasses: a line that can show always stays on, the widget never hides (%d masks)" % len(seen2))
    lay(me, "Skills").lines = 3
    h, cm = hud(me)
    chk(str(h.shape.get("Skills")) == "K1", "F: (rebuilt without SkyyClasses: K1)")
    bridge.put("class:list", CLS_LIST)
    b5 = UCB()
    chk(bool(h.fill(b5, False)), "F: SkyyClasses appears -> the shape K1 -> K2 asks for one re-send")
    cm5 = build_again(h)
    st5 = sets(cm5)
    b6 = UCB()
    r6 = bool(h.fill(b6, False))
    chk(str(h.shape.get("Skills")) == "K2" and st5.get("#SkyyWSkillsN1Txt.Text") == "Archery" and not r6
        and not [c for c in cmds(b6) if "Skills" in str(c[1])],
        "F: ... the re-sent HUD has Overall + Archery, and the next tick sends nothing (no flapping)")

    # ---- G: every widget in the editor (all 12 on, Skills 10 lines, Combat in combat)
    use_dir("g")
    me = pref(1)
    skills_world(me.getUuid(), LV, "Archer")
    party_guild()
    cfg_ = CombatFake()
    bridge.put("skill:fn:combat", cfg_)
    cfg_.left[str(me.getUuid())] = 3500
    m = LS.get(me.getUuid())
    for wid in IDS:
        m.get(wid).en = True
    m.get("Skills").lines = ALL
    ep = EP(me, plugin)
    ec, ee = page(ep)
    placed = sorted(set(str(w) for w in ep.cellWidget if w is not None))
    chk(placed == sorted(IDS) and len(IDS) == 12, "G: all 12 widgets have a canvas handle: %s" % placed)
    chk(all(any(c[3] and ("Group #SkyyEPv%s " % w) in c[3] for c in ec) for w in IDS), "G: all 12 previews drawn")
    chk(any(c[3] and "ProgressBar #SkyyEPvCombatBar " in c[3] for c in ec), "G: the editor preview of Combat (in combat) has its bar")
    ids_all = []
    for c in ec:
        if c[0] == "AppendInline" and c[3]:
            ids_all += re.findall(r"#([A-Za-z0-9_]+)\s*\{", c[3])
    chk(len(ids_all) == len(set(ids_all)) and not [i for i in ids_all if "_" in i], "G: editor ids unique, no underscores (%d)" % len(ids_all))
    sel_row = [e[1] for e in ee if e[1] and e[1].startswith("#SkyyESel")]
    chk(len(sel_row) == 12 and "#SkyyESelCombat" in sel_row, "G: the Select row lists all 12 widgets: %s" % sel_row)
    l = m.get("Skills")
    for sc in (200, 50, 100):
        l.scale = sc
        Wid.clampToScreen(l)
        p = Wid.screenPos(l)
        chk(0 <= p[0] <= 1920 - 180 * sc // 100 and 0 <= p[1] <= 1080 - int(Wid.hMax(l)), "G: Skills %d%% (10 lines, max box %d) on screen" % (sc, int(Wid.hMax(l))))
    cells = [i for i, w in enumerate(list(ep.cellWidget)) if w is not None and str(w) == "Skills"]
    hs = int(ep.heightOf("Skills", l))
    p0 = list(Wid.screenPosH(l, hs))
    ep.handleDataEvent(None, None, '{"a":"drop","SourceSlotId":%d,"SlotIndex":%d}' % (cells[0], cells[0] + 5 + 32))
    p1 = list(Wid.screenPosH(l, hs))
    chk(p1 == [min(p0[0] + 300, 1740), min(p0[1] + 60, 1080 - hs)] and str(l.anchor) in ("tl", "tr", "bl", "br"),
        "G: drag Skills 5 right 1 down: %s -> %s (%s)" % (p0, p1, l.anchor))
    ep.handleDataEvent(None, None, '{"a":"sel:Skills"}')
    for act in ("Sp", "Sp", "Sm", "Lt", "Up"):
        ep.handleDataEvent(None, None, '{"a":"act:%s"}' % act)
    chk(int(l.scale) == 110, "G: Size + + - on Skills -> 110%%")
    spS = SP(me, plugin, "Skills")
    for an in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br"):
        spS.handleDataEvent(None, None, '{"a":"an:%s"}' % an)
        mmx = Wid.modelL("Skills", me, l)
        hh = int(Wid.bodyH("Skills", mmx, int(l.scale)))
        src = str(Wid.multiWidgetSrc("Skills", l, mmx))
        mt = re.search(r"Anchor: \((Top|Bottom): (-?\d+), (Left|Right): (-?\d+), Width: (\d+), Height: (\d+)\)", src)
        pos = list(Wid.screenPosH(l, hh))
        w_ = int(mt.group(5)) if mt else -1
        x = int(mt.group(4)) if mt and mt.group(3) == "Left" else (1920 - w_ - int(mt.group(4)) if mt else -1)
        y = int(mt.group(2)) if mt and mt.group(1) == "Top" else (1080 - hh - int(mt.group(2)) if mt else -1)
        chk(str(l.anchor) == an and [x, y] == pos and 0 <= x <= 1920 - w_ and 0 <= y <= 1080 - hh,
            "G: Snap to %s: the HUD margins land where the editor draws it (%s vs %s)" % (an, [x, y], pos))
    res["edit_new_skills"] = str(l.ser())
    bridge.remove("skill:fn:combat")

    # ======================================================================== X: the Combat Indicator widget (0.3.12)
    SUI.verify()
    chk(SUI.COLOR["error"] == RED and str(Wid.CRED) == RED, "X: the in-combat red is the kit's vanilla error red (%s / %s)" % (SUI.COLOR["error"], Wid.CRED))
    chk(SUI.TEX["progress"] == TRACK and SUI.TEX["progressFill"] == FILL, "X: the bar textures are the kit's (verified in Assets.zip by SUI.verify())")
    chk(str(Wid.GREY) == GREY and int(Wid.CWIN) == 6000 and str(Wid.CNEED) == NEED, "X: grey %s, window 6000 ms, stand-in %r" % (Wid.GREY, str(Wid.CNEED)))
    cfn = CombatFake()

    def combat_on():
        bridge.put("skill:fn:combat", cfn)

    def grp_of(cm, base="SkyyWCombat"):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and ("Group #%s " % base) in c[3]]
        return g[0] if len(g) == 1 else None

    def combat_cmds(cm):
        return [c for c in cm if c[1] and "Combat" in c[1]]

    # ---- X0 defaults
    use_dir("x0")
    bridge.clear()
    dc = wdef("Combat")
    chk(bool(dc.en) and str(dc.anchor) == "t" and int(dc.dx) == 0 and int(dc.dy) == 130 and int(dc.scale) == 100 and int(dc.bw) == 180
        and int(dc.bh) == 34 and int(dc.lines) == -1 and int(dc.ldef) == -1 and bool(dc.opt) and bool(dc.bg) and bool(dc.styleDefault()),
        "X0: Widgets.def(Combat) = ON t 0,130 100%% 180x34, hide out of combat, no lines (got %s opt %s)" % (dc.ser(), dc.opt))
    me = pref(40, "Cora")
    chk(str(lay(me, "Combat").ser()) == "1,t,0,130,100,1", "X0: a new player's Combat layout = the 6-field line (%s)" % lay(me, "Combat").ser())
    code = str(LS.export(me.getUuid()))
    chk(code.endswith(";Combat=1:t:0:130:100:1"), "X0: the export code ends with the Combat part: %s" % code[-40:])
    chk(str(Wid.label("Combat")) == "Combat Indicator" and str(Wid.shortLabel("Combat")) == "Combat" and bool(Wid.multi("Combat")),
        "X0: label 'Combat Indicator', short 'Combat', a multi-line (shape-driven) widget")
    chk(int(Wid.hMax(dc)) == 34 and list(Wid.screenPos(dc)) == [870, 130], "X0: the default box sits at 870,130 (top centre), 34 high")

    # ---- X1 missing key (SkyySkills missing or older than 0.4.13)
    use_dir("x1")
    bridge.clear()
    me = pref(41, "Mo")
    chk(all(str(Wid.combatModelU(me.getUuid(), hd)[0]) == "C0" and Wid.combatModelU(me.getUuid(), hd)[1] is None for hd in (True, False)),
        "X1: no skill:fn:combat -> hidden with Hide and with Show")
    chk(not bool(Wid.combatHave(bridge)) and int(Wid.combatLeft(bridge, me.getUuid())) == -1, "X1: combatHave false, combatLeft -1")
    for hd in (True, False):
        lay(me, "Combat").opt = hd
        h, cm = hud(me)
        chk(grp_of(cm) is None and not combat_cmds(cm) and str(h.shape.get("Combat")) == "C0", "X1: the HUD draws no Combat widget (opt %s)" % hd)
    lay(me, "Combat").opt = True
    ep = EP(me, plugin)
    ec, ee = page(ep)
    st = sets(ec)
    pv = grp_of(ec, "SkyyEPvCombat")
    chk(st.get("#SkyyEPvCombatN0Txt.Text") == NEED and st.get("#SkyyEPvCombatS0Txt.Text") == "" and pv is not None
        and "ProgressBar" not in pv and "TextColor: #eaf6ff" in pv,
        "X1: the editor shows the stand-in line '%s' in the widget's own colour, no bar" % NEED)
    chk("Combat" in [str(w) for w in ep.cellWidget if w is not None], "X1: the editor still places it (a canvas handle)")
    scm, sce = page(SP(me, plugin, "Combat"))
    chk([js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"] == [NEED], "X1: the Settings preview shows the stand-in too")
    tw = SUI.text_width(NEED, 12, True)
    chk(tw <= 180 - 2 * 6 - 2 * 2, "X1: the stand-in fits the 100%% text box (%.0f px of %d)" % (tw, 180 - 2 * 6 - 2 * 2))
    for t_ in ("In combat", "Out of combat", "99s"):
        chk(SUI.text_width(t_, 12, True) <= (180 - 12 - 40 - 4 if t_ != "99s" else 40 - 4), "X1: %r fits its column at 100%%" % t_)

    # ---- X2 out of combat, Hide (the default)
    use_dir("x2")
    bridge.clear()
    combat_on()
    cfn.left.clear()
    me = pref(42, "Ivy")
    u = str(me.getUuid())
    fx = os.path.join(work, "x2", "layouts", u + ".properties")
    h, cm = hud(me)
    chk(grp_of(cm) is None and str(h.shape.get("Combat")) == "C0" and not combat_cmds(cm), "X2: out of combat + Hide -> no Combat markup, shape C0")
    b0 = UCB()
    r0 = bool(h.fill(b0, False))
    chk(not r0 and not combat_cmds(cmds(b0)), "X2: a tick out of combat sends nothing for Combat")
    ec, _ = page(EP(me, plugin))
    st = sets(ec)
    pv = grp_of(ec, "SkyyEPvCombat")
    chk(st.get("#SkyyEPvCombatN0Txt.Text") == "In combat" and st.get("#SkyyEPvCombatS0Txt.Text") == "4s" and pv is not None
        and "ProgressBar #SkyyEPvCombatBar " in pv and "Value: 0.667;" in pv and ("TextColor: %s" % RED) in pv,
        "X2: the editor shows the in-combat sample (red, 4s, bar 0.667) so it can be placed")
    scm, _ = page(SP(me, plugin, "Combat"))
    chk([js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"] == ["In combat 4s"], "X2: the Settings preview: the sample")

    # ---- X3 out of combat, Show
    sp = SP(me, plugin, "Combat")
    sp.handleDataEvent(None, None, '{"a":"optoff"}')
    chk(not bool(lay(me, "Combat").opt) and props(fx).get("Combat") == "1,t,0,130,100,1,def,1,0,0,def,0",
        "X3: Show -> opt false, saved as the 12th field: %s" % props(fx).get("Combat"))
    h, cm = hud(me)
    g = grp_of(cm)
    st = sets(cm)
    chk(g is not None and "Anchor: (Top: 130, Right: 870, Width: 180, Height: 26)" in g and "ProgressBar" not in g
        and g.count("TextColor: %s" % GREY) == 2 and RED not in g and str(h.shape.get("Combat")) == "CO",
        "X3: out of combat + Show -> one grey line, 180 x 26 at the top centre, no bar: %s" % (g[:150] if g else None))
    chk(st.get("#SkyyWCombatN0Txt.Text") == "Out of combat" and st.get("#SkyyWCombatS0Txt.Text") == "" and not vsets(cm, "#SkyyWCombatBar.Value"),
        "X3: texts 'Out of combat' / '', no bar Value set")
    try:
        SUI.check_markup(g)
        chk(True, "")
    except Exception as e:
        chk(False, "X3: check_markup(grey line): %s" % e)
    b1 = UCB()
    chk(not bool(h.fill(b1, False)) and not combat_cmds(cmds(b1)), "X3: a tick on the grey line sends nothing")

    # ---- X4 in combat
    cfn.left[u] = 5400
    b2 = UCB()
    chk(bool(h.fill(b2, False)) and not combat_cmds(cmds(b2)), "X4: getting hit -> the tick asks for the shape re-send (CO -> CI), no text sets yet")
    cm = build_again(h)
    g = grp_of(cm)
    bar = ('ProgressBar #SkyyWCombatBar { Anchor: (Left: 6, Top: 23, Width: 168, Height: 6); Background: "%s"; BarTexturePath: "%s"; '
           'Value: 0.900; }' % (TRACK, FILL))
    chk(g is not None and "Anchor: (Top: 130, Right: 870, Width: 180, Height: 34)" in g and bar in g and str(h.shape.get("Combat")) == "CI",
        "X4: in combat -> 180 x 34 at the top centre with the vanilla ProgressBar (Value 0.900 inline): %s" % (g[:400] if g else None))
    chk(g is not None and g.count("TextColor: %s" % RED) == 2 and GREY not in g and "EffectTexturePath" not in g,
        "X4: both labels red #ff6b6b, no grey, no Effect glow on the bar")
    st = sets(cm)
    bv = vsets(cm, "#SkyyWCombatBar.Value")
    chk(st.get("#SkyyWCombatN0Txt.Text") == "In combat" and st.get("#SkyyWCombatS0Txt.Text") == "6s" and len(bv) == 1
        and isinstance(bv[0], (int, float)) and abs(bv[0] - 0.9) < 1e-6,
        "X4: 'In combat' / '6s' and the bar Value set as a float 0.9 in the same packet: %s / %s" % (dict((k, v) for k, v in st.items() if "Combat" in k), bv))
    if g:
        try:
            SUI.check_markup(g)
            chk(True, "")
        except Exception as e:
            chk(False, "X4: check_markup(in combat): %s" % e)
        try:
            SUI.assert_proven(g, allow=("progress-element",), what="Combat widget")
            chk(True, "")
        except Exception as e:
            chk(False, "X4: assert_proven with the progress-element probe (Skyy's probe page 6): %s" % e)
        need = None
        try:
            SUI.assert_proven(g, what="Combat widget")
        except Exception as e:
            need = str(e)
        chk(need is not None and "element ProgressBar" in need and "BarTexturePath" in need and "Value" in need and "3 unproven" in need,
            "X4: without it exactly ProgressBar / BarTexturePath / Value are flagged (nothing else unproven): %s" % need)
    mm = [None if x is None else str(x) for x in Wid.combatModelU(me.getUuid(), True)]
    chk(mm == ["CI", "In combat 6s", "In combat", "6s", "0.900", "r"], "X4: the model: %s" % mm)

    # ---- X5 counting down on one HudMain (the light per-tick update)
    seq = [(4400, "5s", 0.733), (3400, "4s", 0.567), (2400, "3s", 0.4), (1400, "2s", 0.233), (400, "1s", 0.067)]
    okc, log = True, []
    for left, txt, val in seq:
        cfn.left[u] = left
        b_ = UCB()
        r_ = bool(h.fill(b_, False))
        cc = combat_cmds(cmds(b_))
        s_ = sets(cc)
        v_ = vsets(cc, "#SkyyWCombatBar.Value")
        ok_ = (not r_ and len(cc) == 2 and s_.get("#SkyyWCombatS0Txt.Text") == txt and len(v_) == 1 and abs(v_[0] - val) < 0.0006)
        okc = okc and ok_
        log.append((left, r_, len(cc), s_.get("#SkyyWCombatS0Txt.Text"), v_))
    chk(okc, "X5: 5s 4s 3s 2s 1s - each tick exactly 2 Set commands (countdown text + bar Value), no re-send: %s" % log)
    b_ = UCB()
    r_ = bool(h.fill(b_, False))
    chk(not r_ and not combat_cmds(cmds(b_)), "X5: a tick with the same ms left sends nothing")
    cfn.left[u] = 900
    b_ = UCB()
    cc = combat_cmds(cmds(b_)) if not h.fill(b_, False) else ["re-send"]
    chk(len(cc) == 1 and vsets(cc, "#SkyyWCombatBar.Value") and abs(vsets(cc, "#SkyyWCombatBar.Value")[0] - 0.15) < 0.0006,
        "X5: the same second, less ms -> only the bar Value (1 command): %s" % cc)
    cfn.left[u] = 5900
    b_ = UCB()
    r_ = bool(h.fill(b_, False))
    cc = combat_cmds(cmds(b_))
    chk(not r_ and sets(cc).get("#SkyyWCombatS0Txt.Text") == "6s" and abs(vsets(cc, "#SkyyWCombatBar.Value")[0] - 0.983) < 0.0006,
        "X5: a re-hit jumps back to 6s / 0.983 without a re-send")
    cfn.left[u] = 0
    b_ = UCB()
    r_ = bool(h.fill(b_, False))
    chk(r_ and not combat_cmds(cmds(b_)), "X5: out of combat -> the tick asks for the shape re-send (CI -> CO)")
    cm = build_again(h)
    chk(str(h.shape.get("Combat")) == "CO" and grp_of(cm) is not None and "ProgressBar" not in grp_of(cm), "X5: ... the re-sent HUD: the grey line")
    sp.handleDataEvent(None, None, '{"a":"opton"}')
    chk(bool(lay(me, "Combat").opt) and props(fx).get("Combat") == "1,t,0,130,100,1", "X5: Hide again -> the 6-field line: %s" % props(fx).get("Combat"))
    b_ = UCB()
    r_ = bool(h.fill(b_, False))
    cm = build_again(h)
    chk(r_ and grp_of(cm) is None and str(h.shape.get("Combat")) == "C0", "X5: ... and the widget is gone out of combat (CO -> C0 re-send)")

    # ---- X6 colours and glow
    use_dir("x6")
    me = pref(43, "Pip")
    u = str(me.getUuid())
    cfn.left[u] = 3000
    l = lay(me, "Combat")
    l.col, l.glow, l.gcol = "gold", True, "def"
    h, cm = hud(me)
    g = grp_of(cm) or ""
    chk(g.count("TextColor: #ffaa00,") == 2 and g.count("TextColor: #ffaa00(0.45)") == 16 and RED not in g,
        "X6: a picked colour (gold) replaces red; glow Same follows it (16 copies)")
    l.col = "def"
    g = grp_of(hud(me)[1]) or ""
    chk(g.count("TextColor: %s;" % RED) + g.count("TextColor: %s," % RED) == 2 and g.count("TextColor: %s(0.45)" % RED) == 16,
        "X6: Default = red, glow Same = red copies")
    l.gcol = "black"
    h, cm = hud(me)
    g = grp_of(cm) or ""
    chk(g.count("TextColor: #000000(0.45)") == 16, "X6: glow Black -> black copies")
    cfn.left[u] = 2000
    b_ = UCB()
    h.fill(b_, False)
    cc = combat_cmds(cmds(b_))
    chk(len(cc) == 10 and sets(cc).get("#SkyyWCombatS0Txt.Text") == "2s" and sets(cc).get("#SkyyWCombatS0G7.Text") == "2s",
        "X6: with glow a tick sets the countdown on the label + 8 copies + the bar (10 commands): %d" % len(cc))
    l.opt = False
    l.col = "gold"
    cfn.left[u] = 0
    g = grp_of(hud(me)[1]) or ""
    chk(g.count("TextColor: %s" % GREY) == 2 and g.count("TextColor: #5a626b(0.35)") == 16 and "#ffaa00" not in g,
        "X6: out of combat the grey line ignores the palette (grey + grey glow)")
    l.col, l.glow, l.gcol, l.opt = "def", False, "def", True
    l.ital = True
    cfn.left[u] = 3000
    g = grp_of(hud(me)[1]) or ""
    chk(g.count("RenderItalics: true") == 2 and g.count("RenderBold: true") == 2, "X6: italic / bold reach both labels")
    l.ital = False

    # ---- X7 the Combat Settings page
    use_dir("x7")
    me = pref(44, "Rue")
    u = str(me.getUuid())
    fx = os.path.join(work, "x7", "layouts", u + ".properties")
    cfn.left[u] = 0
    sp = SP(me, plugin, "Combat")
    scm, sce = page(sp)
    ph_, pad_, rows_ = page_rows(scm)
    chk((ph_, rows_) == (790, 748) and ph_ - pad_ - rows_ >= 20, "X7: the page is 1500 x 790, rows 748 + padding (%d / %d / %d)" % (ph_, pad_, rows_))
    chk(any(c[3] and 'Text: "Combat Indicator settings"' in c[3] for c in scm if c[0] == "AppendInline"), "X7: title 'Combat Indicator settings'")
    on_b, off_b = btn_of(scm, "SkyySetOptOn"), btn_of(scm, "SkyySetOptOff")
    chk(on_b is not None and off_b is not None and 'Text: "Hide"' in on_b and 'Text: "Show"' in off_b
        and "Background: #7fe07f" in on_b and "Background: #7fe07f" not in off_b, "X7: Out of combat: Hide lit (the default), Show not")
    lab = [c[3] for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySetRow2" and c[3] and 'Text: "Out of combat"' in c[3]]
    hint = [c[3] for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySetRow2" and c[3] and "Show adds a grey line out of combat" in c[3]]
    chk(len(lab) == 1 and len(hint) == 1, "X7: the row label and its hint")
    ob = [(e[0], e[1], e[2]) for e in sce if e[1] in ("#SkyySetOptOn", "#SkyySetOptOff")]
    chk(len(ob) == 2 and ob[0][0] == "Activating" and '"opton"' in ob[0][2] and '"optoff"' in ob[1][2], "X7: bound to opton / optoff: %s" % ob)
    widths = [int(re.search(r"Width: (\d+)", c[3]).group(1)) for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySetRow2" and c[3]]
    chk(sum(widths) == 1322 and sum(widths) <= 1500 - 32, "X7: the Background row is %d px of the 1468 inner width" % sum(widths))
    for c in scm:
        if c[0] == "AppendInline" and c[1] == "#SkyySetRow2" and c[3]:
            try:
                SUI.check_markup(c[3])
                chk(True, "")
            except Exception as e:
                chk(False, "X7: check_markup(option row): %s: %s" % (e, c[3][:80]))
    pvl = [c[3] for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySetPvAWrap" and c[3]]
    chk(pvl and ("TextColor: %s" % RED) in pvl[0], "X7: the preview (Hide, out of combat = the sample) is drawn red")
    sp.handleDataEvent(None, None, '{"a":"optoff"}')
    scm, _ = page(sp)
    pvl = [c[3] for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySetPvAWrap" and c[3]]
    chk(props(fx).get("Combat") == "1,t,0,130,100,1,def,1,0,0,def,0" and "Background: #7fe07f" in (btn_of(scm, "SkyySetOptOff") or "")
        and pvl and ("TextColor: %s" % GREY) in pvl[0]
        and [js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"] == ["Out of combat"],
        "X7: Show -> saved, Show lit, the preview 'Out of combat' in grey")
    cfn.left[u] = 2500
    scm, _ = page(sp)
    pvl = [c[3] for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySetPvAWrap" and c[3]]
    chk(pvl and ("TextColor: %s" % RED) in pvl[0] and [js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"] == ["In combat 3s"],
        "X7: in combat the preview reads 'In combat 3s' in red")
    sp.handleDataEvent(None, None, '{"a":"opton"}')
    chk(props(fx).get("Combat") == "1,t,0,130,100,1", "X7: Hide -> back to the 6-field line")
    for pl in ('{"a":"ln:2"}', '{"a":"lnall"}', '{"a":"lndef"}'):
        sp.handleDataEvent(None, None, pl)
    chk(str(lay(me, "Combat").ser()) == "1,t,0,130,100,1" and int(lay(me, "Combat").lines) == -1, "X7: forged line clicks change nothing")
    sp.handleDataEvent(None, None, '{"a":"col:red"}')
    sp.handleDataEvent(None, None, '{"a":"rstyle"}')
    chk(str(lay(me, "Combat").ser()) == "1,t,0,130,100,1", "X7: Reset style keeps the Out of combat setting")

    # ---- X8 the editor on Combat: drag, size, arrows, every Snap to (HUD margins == where the editor draws it)
    use_dir("x8")
    me = pref(45, "Sol")
    u = str(me.getUuid())
    cfn.left[u] = 4000
    l = lay(me, "Combat")
    ep = EP(me, plugin)
    page(ep)
    cells = [i for i, w in enumerate(list(ep.cellWidget)) if w is not None and str(w) == "Combat"]
    chk(len(cells) == 1, "X8: one canvas handle for Combat")
    hs = int(ep.heightOf("Combat", l))
    p0 = list(Wid.screenPosH(l, hs))
    if cells:
        ep.handleDataEvent(None, None, '{"a":"drop","SourceSlotId":%d,"SlotIndex":%d}' % (cells[0], cells[0] + 3 + 2 * 32))
    p1 = list(Wid.screenPosH(l, hs))
    chk(hs == 34 and p1 == [p0[0] + 180, p0[1] + 120] and str(l.anchor) in ("tl", "tr", "bl", "br"), "X8: drag 3 right 2 down: %s -> %s (%s)" % (p0, p1, l.anchor))
    ep.handleDataEvent(None, None, '{"a":"sel:Combat"}')
    for act in ("Sp", "Sp", "Sp", "Sm", "Rt", "Dn"):
        ep.handleDataEvent(None, None, '{"a":"act:%s"}' % act)
    chk(int(l.scale) == 120, "X8: Size + + + - -> 120%%")
    for out_mode, left in (("in", 4000), ("out", 0)):
        cfn.left[u] = left
        l.opt = out_mode == "in"
        okp = True
        for an in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br"):
            SP(me, plugin, "Combat").handleDataEvent(None, None, '{"a":"an:%s"}' % an)
            mmx = Wid.modelL("Combat", me, l)
            hh = int(Wid.bodyH("Combat", mmx, int(l.scale)))
            src = str(Wid.multiWidgetSrc("Combat", l, mmx))
            mt = re.search(r"Anchor: \((Top|Bottom): (-?\d+), (Left|Right): (-?\d+), Width: (\d+), Height: (\d+)\)", src)
            pos = list(Wid.screenPosH(l, hh))
            w_ = int(mt.group(5)) if mt else -1
            x = int(mt.group(4)) if mt and mt.group(3) == "Left" else (1920 - w_ - int(mt.group(4)) if mt else -1)
            y = int(mt.group(2)) if mt and mt.group(1) == "Top" else (1080 - hh - int(mt.group(2)) if mt else -1)
            if not (str(l.anchor) == an and [x, y] == pos and 0 <= x <= 1920 - w_ and 0 <= y <= 1080 - hh and int(mt.group(6)) == hh):
                okp = False
        chk(okp, "X8: every Snap to (%s combat, %d px box): the HUD margins land where the editor draws it" % (out_mode, hh))
    l.opt = True
    for sc in (200, 50, 100):
        l.scale = sc
        Wid.clampToScreen(l)
        p = Wid.screenPos(l)
        chk(0 <= p[0] <= 1920 - 180 * sc // 100 and 0 <= p[1] <= 1080 - int(Wid.hMax(l)), "X8: Combat %d%% on screen (box %d)" % (sc, int(Wid.hMax(l))))

    # ---- X9 every size: drawn height within the box, the bar inside, valid markup for every shape
    use_dir("x9")
    me = pref(46, "Tam")
    u = str(me.getUuid())
    l = lay(me, "Combat")
    okz, info = True, []
    for sc in range(50, 201, 5):
        l.scale = sc
        for kind in ("CI", "CO", "S"):
            if kind == "CI":
                cfn.left[u] = 5000
                combat_on()
                mmx = Wid.combatModelU(me.getUuid(), True)
            elif kind == "CO":
                cfn.left[u] = 0
                mmx = Wid.combatModelU(me.getUuid(), False)
            else:
                bridge.remove("skill:fn:combat")
                mmx = Wid.combatSample()
            hh = int(Wid.bodyH("Combat", mmx, sc))
            src = str(Wid.multiWidgetSrc("Combat", l, mmx))
            exp_h = (3 * sc // 100) + (20 * sc // 100) + (max(1, 6 * sc // 100) + 5 * sc // 100 if kind == "CI" else 3 * sc // 100)
            ok_ = hh == exp_h and hh <= int(Wid.hMax(l)) and ("Height: %d)" % hh) in src
            mb = re.search(r"ProgressBar #SkyyWCombatBar \{ Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+), Height: (\d+)\)", src)
            if kind == "CI":
                ok_ = ok_ and mb is not None and int(mb.group(2)) + int(mb.group(4)) <= hh and int(mb.group(1)) + int(mb.group(3)) <= 180 * sc // 100
            else:
                ok_ = ok_ and mb is None
            try:
                SUI.check_markup(src)
            except Exception as e:
                ok_ = False
                info.append("%s@%d: %s" % (kind, sc, e))
            if not ok_:
                okz = False
                info.append((kind, sc, hh, exp_h))
    combat_on()
    chk(okz, "X9: sizes 50-200 %%: height = the floored parts, <= the box, the bar inside it, check_markup on every shape: %s" % info[:6])

    # ---- X10 a misbehaving Function
    use_dir("x10")
    me = pref(47, "Una")
    u = str(me.getUuid())
    Lmax = Long(9223372036854775807)
    cases = [(Integer(3000), ("CI", "3s", "0.500")), (Double(2500.7), ("CI", "3s", "0.417")), ("abc", ("C0",)), (None, ("C0",)),
             (Long(-5), ("C0",)), (Lmax, ("CI", "99s", "1.000")), (Long(1), ("CI", "1s", "0.000")), (Long(6000), ("CI", "6s", "1.000")),
             (Long(99999), ("CI", "99s", "1.000")), (Long(100001), ("CI", "99s", "1.000")), (Double(float("nan")), ("C0",))]
    okm, info = True, []
    for val, want in cases:
        cfn.left[u] = val
        try:
            mm = [None if x is None else str(x) for x in Wid.combatModelU(me.getUuid(), True)]
            ok_ = mm[0] == want[0] and (len(want) == 1 or (mm[3] == want[1] and mm[4] == want[2]))
        except Exception as e:
            ok_, mm = False, str(e)
        if not ok_:
            okm = False
            info.append((str(val), mm))
    chk(okm, "X10: Integer / Double / String / null / negative / huge / NaN answers -> sensible, never an exception: %s" % info)
    cfn.left[u] = 3000
    cfn.mode = "throw"
    lay(me, "Combat").opt = False       # Show: "out of combat" is then visible as the grey line (Hide would just hide it)
    try:
        mm = [None if x is None else str(x) for x in Wid.combatModelU(me.getUuid(), False)]
        h, cm = hud(me)
        chk(mm[0] == "CO" and str(h.shape.get("Combat")) == "CO" and int(Wid.combatLeft(bridge, me.getUuid())) == 0,
            "X10: a throwing Function counts as out of combat (no exception): %s / %s" % (mm[0], h.shape.get("Combat")))
    except Exception as e:
        chk(False, "X10: a throwing Function escaped: %s" % e)
    lay(me, "Combat").opt = True
    cfn.mode = "ok"
    okw, info = True, []
    for wv, mode_, want in ((None, "ok", "0.500"), (Long(10000), "ok", "0.300"), (Long(500), "ok", "0.500"), (Long(700000), "ok", "0.500"),
                            ("6000", "ok", "0.500"), (Long(6000), "throw-window", "0.500"), (Integer(4000), "ok", "0.750")):
        cfn.window, cfn.mode = wv, mode_
        try:
            mm = [None if x is None else str(x) for x in Wid.combatModelU(me.getUuid(), True)]
            ok_ = mm[0] == "CI" and mm[4] == want
        except Exception as e:
            ok_, mm = False, str(e)
        if not ok_:
            okw = False
            info.append((str(wv), mode_, mm))
    cfn.window, cfn.mode = Long(6000), "ok"
    chk(okw, "X10: window answers null / 10 s / out of range / a String / throwing / Integer -> the right bar or the 6000 fallback: %s" % info)

    # ---- X11 light: how often the Function is asked
    use_dir("x11")
    me = pref(48, "Val")
    u = str(me.getUuid())
    cfn.left[u] = 0
    h, cm = hud(me)
    c0, w0 = cfn.calls, cfn.wcalls
    h.fill(UCB(), False)
    chk(cfn.calls - c0 == 1 and cfn.wcalls == w0, "X11: a hidden widget: one call per tick, no window call (%d / %d)" % (cfn.calls - c0, cfn.wcalls - w0))
    cfn.left[u] = 3000
    h.fill(UCB(), False)
    build_again(h)
    c0, w0 = cfn.calls, cfn.wcalls
    b_ = UCB()
    h.fill(b_, False)
    chk(cfn.calls - c0 == 1 and cfn.wcalls - w0 == 1, "X11: in combat: one call + one window call per tick (%d / %d)" % (cfn.calls - c0, cfn.wcalls - w0))
    lay(me, "Combat").en = False
    h, cm = hud(me)
    c0, w0 = cfn.calls, cfn.wcalls
    for i in range(5):
        h.fill(UCB(), False)
    chk(cfn.calls == c0 and cfn.wcalls == w0 and grp_of(cm) is None, "X11: a widget switched OFF never asks (5 ticks: %d calls)" % (cfn.calls - c0))
    lay(me, "Combat").en = True

    # ---- X12 the shape cycle and the confirm send
    use_dir("x12")
    me = pref(49, "Wes")
    u = str(me.getUuid())
    cfn.left[u] = 0
    h, cm = hud(me)
    chk(int(h.confirmAt) == 0, "X12: a HUD with every multi-line widget hidden arms no confirm send")
    cfn.left[u] = 5000
    r1 = bool(h.fill(UCB(), False))
    build_again(h)
    chk(r1 and int(h.confirmAt) > 0 and str(h.shape.get("Combat")) == "CI", "X12: entering combat -> one re-send asked, the confirm send armed")
    h.confirmAt = 0
    build_again(h)
    chk(int(h.confirmAt) == 0, "X12: a rebuild with the same shape arms nothing (never periodic)")
    cfn.left[u] = 3000
    chk(not bool(h.fill(UCB(), False)), "X12: counting down never asks for a re-send")
    cfn.left[u] = 0
    r2 = bool(h.fill(UCB(), False))
    build_again(h)
    chk(r2 and int(h.confirmAt) == 0 and str(h.shape.get("Combat")) == "C0", "X12: leaving combat into Hide -> one re-send, no confirm send")

    # ---- X13 export / import / profiles / the server default with a Combat part
    use_dir("x13")
    me, oth = pref(50, "Xan"), pref(51, "Yul")
    n = int(LS.importCode(me.getUuid(), "Combat=0:t:0:130:100:1"))
    chk(n == 1 and not bool(lay(me, "Combat").en), "X13: a code switching Combat OFF imports")
    n = int(LS.importCode(me.getUuid(), "Combat=1:br:8:8:150:1:red:1:1:1:black:0"))
    lc = lay(me, "Combat")
    chk(n == 1 and str(lc.anchor) == "br" and int(lc.scale) == 150 and str(lc.col) == "red" and bool(lc.ital) and bool(lc.glow)
        and str(lc.gcol) == "black" and not bool(lc.opt) and int(lc.bw) == 180 and int(lc.bh) == 34, "X13: a full 12-field Combat part imports")
    code = str(LS.export(me.getUuid()))
    n = int(LS.importCode(oth.getUuid(), code))
    chk(n == 12 and str(lay(oth, "Combat").ser()) == str(lc.ser()) == "1,br,8,8,150,1,red,1,1,1,black,0", "X13: export -> import keeps it (12 parts)")
    chk(bool(LS.profileSave(me.getUuid(), "fight")), "X13: profile save")
    LS.reset(me.getUuid())
    chk(str(lay(me, "Combat").ser()) == "1,t,0,130,100,1", "X13: /skyyhud reset -> the built-in Combat")
    chk(int(LS.profileLoad(me.getUuid(), "fight")) == 12 and str(lay(me, "Combat").ser()) == "1,br,8,8,150,1,red,1,1,1,black,0", "X13: profile load brings it back")
    n = int(LS.importCode(me.getUuid(), "Coords=1:tr:8:8:100:1;Skills=1:tl:8:544:100:1"))
    chk(n == 2 and str(lay(me, "Combat").ser()) == "1,br,8,8,150,1,red,1,1,1,black,0", "X13: a 0.3.11 code (no Combat part) leaves Combat alone")
    chk(Cfg.codeError("Combat=1:t:0:130:100:1") is None and Cfg.codeError("Combat=1:t") is not None, "X13: the server default check knows Combat")
    Cfg.DEFAULT_LAYOUT = "Combat=1:tl:8:8:100:1:def:1:0:0:def:0"
    nw = pref(52, "Zed")
    chk(str(lay(nw, "Combat").anchor) == "tl" and not bool(lay(nw, "Combat").opt), "X13: a server default Combat part reaches a new player")
    Cfg.DEFAULT_LAYOUT = ""

    # ---- H: start twice on a scratch COPY of the live data
    if os.path.isdir(LIVE):
        import time
        mods = os.path.join(work, "live")
        shutil.copytree(LIVE, os.path.join(mods, "Skyy_SkyyHud"))
        hdir = os.path.join(mods, "Skyy_SkyyHud")
        Pub = JClass(PKG + "CfgPub")

        def tree():
            out = {}
            for dp, dn, fn in os.walk(mods):
                for f in fn:
                    p = os.path.join(dp, f)
                    out[os.path.relpath(p, mods)] = (open(p, "rb").read(), os.path.getmtime(p))
                for dn_ in dn:
                    out[os.path.relpath(os.path.join(dp, dn_), mods) + os.sep] = None
            return out

        lyd = os.path.join(hdir, "layouts")
        players = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []

        def start(in_combat):
            LS.CACHE.clear()
            EP.STEPS.clear()
            LS.DIR = Paths.get(os.path.join(hdir, "layouts"))
            Cfg.FILE = Paths.get(os.path.join(hdir, "config.properties"))
            Cfg.PARSED = None
            r = {"cfg": str(Cfg.load())}
            Pub.start(Paths.get(mods), None)
            bridge.clear()
            combat_on()
            for k, us in enumerate(players):
                pr = U.allocateInstance(PRef.class_)
                setf(pr, PRef, "uuid", UUID.fromString(us))
                setf(pr, PRef, "username", "Live%d" % k)
                skills_world(pr.getUuid(), LV, "Archer")
                cfn.left[us] = 4200 if in_combat else 0
                mp = LS.get(pr.getUuid())
                r[us] = dict((w, str(mp.get(w).ser())) for w in IDS)
                h, cm = hud(pr)
                r[us + " hud"] = sorted(v for k2, v in sets(cm).items() if "Skills" in k2)
                r[us + " combat"] = [str(h.shape.get("Combat")), sorted(v for k2, v in sets(cm).items() if "Combat" in k2), vsets(cm, "#SkyyWCombatBar.Value")]
                page(EP(pr, plugin))
                page(SP(pr, plugin, "Skills"))
                page(SP(pr, plugin, "Combat"))
                page(WP(pr, plugin))
            Pub.flush()
            return r
        t0 = tree()
        time.sleep(1.1)
        r1 = start(False)
        t1 = tree()
        chk(t1 == t0, "H: start 1 on the live copy writes nothing (every byte + modification time; new %s changed %s)"
            % (sorted(k for k in t1 if k not in t0), sorted(k for k in t0 if k in t1 and t0[k] != t1[k])))
        for us in players:
            fl = props(os.path.join(hdir, "layouts", us + ".properties"))
            chk(all(r1[us][w] == fl[w] for w in OLD_IDS if w in fl), "H: %s...: every old widget loads exactly as saved" % us[:8])
            chk(r1[us]["Combat"] == "1,t,0,130,100,1" and "Combat" not in fl, "H: %s...: Combat = the default, not written" % us[:8])
            chk(r1[us + " combat"] == ["C0", [], []], "H: %s...: out of combat the widget is hidden (%s)" % (us[:8], r1[us + " combat"]))
        time.sleep(1.1)
        r2 = start(False)
        t2 = tree()
        chk(r2 == r1 and t2 == t1, "H: start 2: same layouts, no file churn")
        time.sleep(1.1)
        r3 = start(True)
        t3 = tree()
        chk(t3 == t2, "H: start 3 with everybody in combat writes nothing either")
        for us in players:
            got = r3[us + " combat"]
            chk(got[0] == "CI" and got[1] == ["5s", "In combat"] and len(got[2]) == 1 and abs(float(got[2][0]) - 0.7) < 1e-6,
                "H: %s...: in combat the widget shows In combat / 5s / bar 0.7: %s" % (us[:8], got))
        if players:
            us = players[0]
            pr = U.allocateInstance(PRef.class_)
            setf(pr, PRef, "uuid", UUID.fromString(us))
            setf(pr, PRef, "username", "Live0")
            before = props(os.path.join(hdir, "layouts", us + ".properties"))
            SP(pr, plugin, "Combat").handleDataEvent(None, None, '{"a":"optoff"}')
            after = props(os.path.join(hdir, "layouts", us + ".properties"))
            t4 = tree()
            changed = sorted(k for k in t4 if t4[k] != t3.get(k))
            # the save writes every widget the player has: the old lines exactly, + Skills (when the file had none) + Combat
            extra = dict((k, v) for k, v in after.items() if k not in before)
            chk(changed == [os.path.join("Skyy_SkyyHud", "layouts", us + ".properties")]
                and dict((k, v) for k, v in after.items() if k in before) == before
                and after.get("Combat") == "1,t,0,130,100,1,def,1,0,0,def,0" and set(extra) <= {"Skills", "Combat"},
                "H: one Combat click writes only that player's file: the old lines kept, + Combat=...,0 (changed %s, new keys %s)" % (changed, sorted(extra)))
        res["live_players"] = len(players)
    else:
        res["live_players"] = -1
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
def run_bytecode(old, new, out, old_version, new_version):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([], [B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            key = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[key] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[key] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        consts = {}
        for f in list(cc.getDeclaredFields()):
            ca = f.getFieldInfo().getConstantValue()
            if ca:
                consts[str(f.getName())] = str(cc.getClassFile().getConstPool().getLdcValue(ca))
        return ms, fields, consts

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo, co = listing(ClassPool(False), a)
        mn, fn, cn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        consts = dict((k, [co.get(k), cn.get(k)]) for k in set(co) | set(cn) if co.get(k) != cn.get(k))
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "fields_new": sorted(set(fn) - set(fo)), "fields_gone": sorted(set(fo) - set(fn)), "consts": consts,
                  "version_only": all(mo[k].replace(old_version, "V") == mn[k].replace(new_version, "V") for k in changed)
                  and all((x or "").replace(old_version, "V") == (y or "").replace(new_version, "V") for x, y in consts.values()),
                  "diff": dict((k, [mo[k], mn[k]]) for k in changed)}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
COMBAT_RE = re.compile(r"Combat")
CLOCK_RE = re.compile(r'^\{"0": "(\d\d:\d\d|\d+m \d+s|\d+h \d+m)"\}$')


def norm(cm):
    """the wall-clock texts (Real Clock HH:MM, Session time) as a token: the two child JVMs run seconds apart and may cross a minute"""
    return [[c[0], c[1], '{"0": "CLOCK"}' if c[0] == "Set" and c[2] and CLOCK_RE.match(c[2]) else c[2], c[3]] for c in cm]


def filt(cm):
    """commands without the Combat widget's own (appends / sets naming Combat; the Hidden / Select row spacer right after its button)"""
    out, skip_next = [], False
    for c in cm:
        if skip_next:
            skip_next = False
            if c[0] == "AppendInline" and c[1] in ("#SkyyEOff", "#SkyyESelRow") and ("Width: 4, Height: 22" in (c[3] or "")):
                continue
        if COMBAT_RE.search(str(c[1])) or COMBAT_RE.search(str(c[3])):
            if c[0] == "AppendInline" and ("#SkyyEOnCombat" in (c[3] or "") or "#SkyyESelCombat" in (c[3] or "")):
                skip_next = True
            continue
        out.append(c)
    return out


def main():
    if "--run" in sys.argv:
        run_child(arg("--run"), arg("--out"), arg("--mode"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"), arg("--ov"), arg("--nv"))
        return
    for j in (JAR, OLD_JAR, SKILLS_JAR, CLASSES_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not SCRATCH.replace("\\", "/").lower().startswith(os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower()):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    common = ["--dir", SCRATCH, "--skills", SKILLS_JAR, "--skills13", SKILLS13_JAR, "--classes", CLASSES_JAR, "--live", LIVE]
    outs = {}
    tags = [("new", JAR), ("old", OLD_JAR)] + ([("real", JAR)] if os.path.isfile(SKILLS13_JAR) else [])
    for tag, j in tags:
        outs[tag] = os.path.join(SCRATCH, "child-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--mode", tag] + common, env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s (%s) ran (exit %s)" % (os.path.basename(j), tag, p.returncode))
    if not os.path.isfile(SKILLS13_JAR):
        SKIPS.append("R (the real SkyySkills 0.4.13 CombatFn): no jar at %s" % SKILLS13_JAR)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    if FAILS:
        return finish()
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    if new["load_fails"] or old["load_fails"]:
        return finish()
    # K-G, X, H (in the 0.3.12 child)
    nb = 0
    for ok, what in new["checks"]:
        if what:
            check(ok, what)
            nb += 1
    print("K-X, H. %d checks in the 0.3.12 JVM (%d failed); live copy players: %s" % (nb, sum(1 for ok, w in new["checks"] if not ok), new.get("live_players")))
    if "real" in outs:
        real = json.load(open(outs["real"]))
        check(not real["load_fails"], "R: the 0.3.12 jar loads next to SkyySkills 0.4.13 %s" % real["load_fails"])
        nr = 0
        for ok, what in real["checks"]:
            if what:
                check(ok, what)
                nr += 1
        check(nr >= 8, "R: the real-CombatFn checks ran (%d)" % nr)
        print("R. %d checks against the REAL SkyySkills 0.4.13 CombatFn (%d failed)" % (nr, sum(1 for ok, w in real["checks"] if not ok)))
    else:
        print("R. SKIPPED - no SkyySkills 0.4.13 jar at %s" % SKILLS13_JAR)
    if os.path.isdir(LIVE):
        check(new.get("live_players", -1) >= 1, "H: the live Skyy_SkyyHud folder was copied and holds at least one layout (%s)" % LIVE)
    else:
        SKIPS.append("H (start twice on a copy of the live data): no live Skyy_SkyyHud folder at %s" % LIVE)
        print("H. SKIPPED - no live Skyy_SkyyHud folder at %s (pass --live <folder> to run it)" % LIVE)
    # S: 0.3.11 vs 0.3.12 for the old widgets
    ns = 0
    for name in sorted(old["scen"]):
        o, n = old["scen"][name], new["scen"].get(name)
        if n is None:
            check(False, "S: scenario %s missing in 0.3.12" % name)
            continue
        oc, nc = o["cmds"], n["cmds"]
        if name == "widgets page":
            oc = [[c[0], c[1], c[2], re.sub(r"Height: \d+\)", "Height: H)", c[3] or "", 1) if i == 0 else c[3]] for i, c in enumerate(oc)]
            nc = [[c[0], c[1], c[2], re.sub(r"Height: \d+\)", "Height: H)", c[3] or "", 1) if i == 0 else c[3]] for i, c in enumerate(nc)]
        fo, fn_ = filt(norm(oc)), filt(norm(nc))
        same = fo == fn_
        if not same:
            for i, (a, b) in enumerate(zip(fo, fn_)):
                if a != b:
                    print("   first difference in %s at %d:\n     0.3.11 %s\n     0.3.12 %s" % (name, i, a, b))
                    break
        check(same and len(fo) == len(oc), "S: %s: 0.3.12 = 0.3.11 apart from the Combat widget (%d / %d commands, %d Combat-only)"
              % (name, len(oc), len(nc), len(nc) - len(fn_)))
        ev_o = [e for e in o["evs"]]
        ev_n = [e for e in n["evs"] if "Combat" not in str(e[1]) + str(e[2])]
        check(ev_o == ev_n, "S: %s: event bindings identical apart from Combat (%d / %d)" % (name, len(o["evs"]), len(n["evs"])))
        ns += 1
    check(ns >= 17, "S: every scenario compared (%d; 21 with the two live layouts)" % ns)
    print("S. %d scenarios: 0.3.11 output = 0.3.12 output apart from the Combat widget" % ns)
    # G (old widgets, both jars): identical layouts after the same editor clicks
    ge = 0
    for wid in OLD_IDS:
        a, b = old["edit"].get(wid), new["edit"].get(wid)
        check(a == b and a != "no handle", "G: %s: drag / Size / arrows / Snap to give the same layout in both jars: %s / %s" % (wid, a, b))
        ge += 1
    print("G. editor clicks on %d old widgets: identical in 0.3.11 and 0.3.12; Skills after drag/size/snap: %s" % (ge, new.get("edit_new_skills")))
    # O: 0.3.11 reads a 0.3.12 layout file (rollback)
    orn = old.get("old_reads_new") or {}
    check(orn.get("ids") == sorted(OLD_IDS) and orn.get("ser") == {"Coords": "1,tr,8,8,100,1", "Skills": "1,r,8,65,150,0,purple,1,0,1,black,1,1023",
                                                                   "Zone": "0,tl,8,40,100,1,gold,1,0,0,def"},
          "O: 0.3.11 reads a 0.3.12 file: every old widget exactly, the Combat line ignored: %s" % orn)
    # F1: class bytes
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F1: same entries in both jars")
    diff = sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    want_diff = sorted(["manifest.json"] + ["com/skyy/hud/%s.class" % c for c in (
        "Widgets", "HudMain", "SettingsPage", "SkyyHudPlugin", "CfgFn", "CfgRows")])
    check(diff == want_diff, "F1: exactly these entries differ: %s (got %s)" % (want_diff, diff))
    bc = json.load(open(bco))
    expect = {
        "Widgets": ({"multi", "model", "sampleU", "linePairs", "bodyH", "multiBody", "def", "label", "<clinit>"},
                    {"combatHave", "combatLeft", "combatSecs", "combatWin", "combatBar", "combatModelU", "combatSample", "textSrcC",
                     "combatColor", "combatGlow", "combatBody", "barOf"}, set()),
        "HudMain": ({"fill"}, set(), set()),
        "SettingsPage": ({"previewText", "build"}, set(), set()),
        "SkyyHudPlugin": ({"setup"}, set(), set()),
    }
    for cname, (chg, nw, gone) in expect.items():
        r = bc.get("com/skyy/hud/%s.class" % cname, {})
        got_c = set(k.split("(")[0] for k in r.get("changed", []))
        got_n = set(k.split("(")[0] for k in r.get("new", []))
        got_g = set(k.split("(")[0] for k in r.get("gone", []))
        check(got_c == chg and got_n == nw and got_g == gone, "F1: %s: changed %s new %s gone %s (got %s / %s / %s)"
              % (cname, sorted(chg), sorted(nw), sorted(gone), sorted(got_c), sorted(got_n), sorted(got_g)))
    wd = bc.get("com/skyy/hud/Widgets.class", {})
    check(wd.get("fields_new") == sorted(["CNEED Ljava/lang/String;", "CRED Ljava/lang/String;", "CWIN J"]) and not wd.get("fields_gone"),
          "F1: Widgets gains CRED, CWIN, CNEED: %s" % wd.get("fields_new"))
    for cname in ("HudMain", "SettingsPage", "SkyyHudPlugin"):
        r = bc.get("com/skyy/hud/%s.class" % cname, {})
        check(r.get("fields_same"), "F1: %s keeps its fields" % cname)
    sp = bc.get("com/skyy/hud/SkyyHudPlugin.class", {})
    check(sp.get("version_only"), "F1: SkyyHudPlugin.setup differs only by the version in the ready line")
    for cname in ("CfgFn", "CfgRows"):
        r = bc.get("com/skyy/hud/%s.class" % cname, {})
        check(r.get("version_only") and not r.get("new") and not r.get("gone"), "F1: %s differs only by the version string" % cname)
    print("F1. class bytes: %d entries identical; differ: %s" % (len(set(zo.namelist()) & set(zn.namelist())) - len(diff),
                                                              ", ".join(x.split("/")[-1] for x in diff)))
    # F2: rebuild 0.3.11 with today's tools to separate a kit pickup from the 0.3.12 changes
    if "--no-rebuild" not in sys.argv:
        rb = os.path.join(SCRATCH, "rebuild011")
        os.makedirs(rb)
        for f in ("build_skyyhud_0.3.11.py", "icon-256.png", "skyyhud_dot.png"):
            shutil.copy2(os.path.join(HERE, f), os.path.join(rb, f))
        env2 = dict(env)
        env2["PYTHONPATH"] = TOOLS
        env2["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        p = subprocess.run([sys.executable, "build_skyyhud_0.3.11.py"], cwd=rb, env=env2, capture_output=True, text=True)
        rjar = os.path.join(rb, "SkyyHud-0.3.11.jar")
        check(p.returncode == 0 and "assembled" in p.stdout and os.path.isfile(rjar), "F2: 0.3.11 rebuilds in scratch: %s" % (p.stdout[-200:] + p.stderr[-300:]))
        if os.path.isfile(rjar):
            hud_cls = [n for n in zo.namelist() if n.endswith(".class") and not n.split("/")[-1].startswith("Cfg")]
            with zipfile.ZipFile(rjar) as zr:      # closed again at once: Windows cannot delete the scratch folder around an open jar
                same = [n for n in hud_cls if zo.read(n) == zr.read(n)]
                kit_same = [n for n in zo.namelist() if n.split("/")[-1].startswith("Cfg") and zo.read(n) == zr.read(n)]
            check(len(same) == len(hud_cls), "F2: the rebuilt 0.3.11's HUD classes equal the 0.3.11 jar's (%d / %d; differ %s)"
                  % (len(same), len(hud_cls), sorted(set(hud_cls) - set(same))))
            bc2 = os.path.join(SCRATCH, "bytecode-kit.json")
            p = subprocess.run([sys.executable, me, "--bytecode", rjar, "--new", JAR, "--out", bc2, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
            r2 = json.load(open(bc2)) if os.path.isfile(bc2) else {}
            kit = dict((k, v) for k, v in r2.items() if k.split("/")[-1].startswith("Cfg"))
            bad = []
            for k, v in kit.items():
                if not v["version_only"] or v["new"] or v["gone"] or not v["fields_same"]:
                    bad.append(k.split("/")[-1])
            check(not bad, "F2: config kit classes rebuilt-0.3.11 vs 0.3.12 differ only by the version string: %s (classes %s)"
                  % (bad, sorted(x.split("/")[-1] for x in kit)))
            print("F2. 0.3.11 rebuilt in scratch: HUD classes reproducible (%d / %d), kit classes identical to the 0.3.11 jar's: %d; "
                  "kit vs 0.3.12: %s" % (len(same), len(hud_cls), len(kit_same), "version only" if not bad else bad))
    return finish()


def finish():
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed%s" % (OKS[0], len(FAILS), (", %d part(s) skipped" % len(SKIPS)) if SKIPS else ""))
    for f in FAILS:
        print("  FAILED:", f)
    for s_ in SKIPS:
        print("  SKIPPED:", s_)
    print("SkyyHud %s harness:" % VERSION, ("PASS" + (" (with skips)" if SKIPS else "")) if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
