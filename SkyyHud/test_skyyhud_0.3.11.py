"""SkyyHud 0.3.11 - bare-JVM harness for the Skills widget (tools/hud_0_3_11_patch.py). SkyyHud had no harness before 0.3.11.

    python SkyyHud/test_skyyhud_0.3.11.py [--jar <SkyyHud-0.3.11.jar>] [--old <SkyyHud-0.3.10.jar>] [--skills <SkyySkills jar>]
                                          [--classes <SkyyClasses jar>] [--live <Skyy_SkyyHud folder>] [--dir <scratch>] [--keep]
                                          [--no-rebuild]

Build the jar first (python SkyyHud/build_skyyhud_0.3.11.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, java.io.tmpdir + TEMP/TMP in the scratch folder; HytaleServer.jar + the HUD jar, + the REAL SkyySkills 0.4.11 and
SkyyClasses 0.1.10 jars for the bridge contract; javassist only for the bytecode step) and check:
  A  every class of the 0.3.11 jar and of the 0.3.10 jar loads and initializes under -Xverify:all
  B  defaults: Widgets.def("Skills") (ON, tl 8,544, 180 x 206, lines = ldef = 3), a new player's HUD draws the widget with exactly
     Overall Level + the class skill (values from the REAL SkyySkills levelsOf / Overall.publish), the default layout line stays in the
     0.3.10 6-field format, editor / Widgets page / Settings page show it; every Skills markup passes skyyui.check_markup
  C  toggles persist PER PLAYER (Settings page clicks -> layout file -> reload), the last line stays on, All on / Default, export /
     import / profile save + load and the server default layout carry the mask, forged clicks on other widgets do nothing, broken
     masks in a file fall back to the default
  D  any combo: all 1023 masks (lines, order, names, values, shape, height, markup, ser/parse and export/import round trips) + random
     click sequences
  E  the class line follows the class (real SkyySkills levelsOf + the 7 real SkyyClasses class skills; a class change / level up /
     profile switch = .Text sets only, no re-send), no class = "Class skill -"
  F  missing / broken bridge: no skyy.bridge, no SkyySkills, nothing published yet, garbage values, unknown mask bits; hidden ->
     shown asks for the re-send
  G  the editor still places / resizes / snaps EVERY widget: all 11 placed; drags, Size +/-, arrows and Snap to on the 10 old widgets
     give byte-identical layouts in 0.3.10 and 0.3.11; the Skills widget drags / sizes / snaps on screen (10 lines at 200%)
  S  0.3.10 vs 0.3.11 output for the old widgets: HUD builds (default, both live layouts, every widget with styles + party + guild),
     the editor (Skills hidden), all 10 old Settings pages, the Widgets page - identical apart from the Skills widget itself
  H  start twice on a scratch COPY of the live Skyy_SkyyHud data (the live folder is only read): HudCfg.load + the config kit start
     + every player's layout + HUD / editor / Settings builds - no file written either time, the old widgets load exactly as saved,
     Skills appears with the defaults; then one toggle writes exactly one new line into that player's file only
  F1 class bytes 0.3.10 vs 0.3.11: only the expected classes / methods differ
  F2 (unless --no-rebuild) 0.3.10 rebuilt in scratch with today's tools: its HUD classes equal the 0.3.10 jar's (reproducible), and its
     config kit classes differ from 0.3.11's only by the version string + KEEP 20 -> 10 (so the kit 1.0 -> 1.1 change is the kit pickup)
Review-fix checks (2026-10-02; each fails on the first 0.3.11 build):
  LOW 1 (B) every one of the 11 Settings pages: the heights of the root's rows + its padding leave at least 20 px spare and the page
        fits 1080 high (the Skills page is 1500 x 940: 894 + 20 of 940; 920 left 6 px)
  LOW 2 (C) "Default" = the lines a new player starts with: a server default code with mask 5 lights Default for 5 and Default sets 5
        (saved as a 13th field - ldef stays the built-in 3); a code without a mask, with only unknown bits, or without a Skills part
        -> Default = 3 (6-field line)
  LOW 3 (D, F) SkyyClasses not installed (no class:list): all 1023 masks lose exactly the Class skill line; the default widget is one
        line; the last line that can show cannot be switched off (also 600 random clicks); only-Class-skill = hidden + "No lines to
        show"; the Settings hint says "Class skill needs SkyyClasses"; Default never picks a mask that shows nothing; SkyyClasses
        appearing changes the shape once (one re-send), then nothing (no flapping)
  INFO  H is SKIPPED (not failed) when the live Skyy_SkyyHud folder does not exist (another machine / a clean checkout); a live
        folder without any layout still fails. The REAL SkyySkills 0.4.11 / SkyyClasses 0.1.10 jars stay required (build them first).
  INFO 4 (E, kept on purpose) the 0.3.9 confirm send is armed by the first build of a HudMain (join / world switch) and, once it
        fired, never again for the same shape (never periodic)
Not testable without the game (UNVERIFIED in the build report): the widget's look on a client, text widths, the live bridge timing.
Nothing is deployed. Default scratch folder: tools/dev/scratch/hud0311/harness (git-ignored), deleted at the end unless --keep.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3.11", "0.3.10"
PKG = "com.skyy.hud."
OLD_IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild"]
LINES = ["Overall Level", "Class skill", "Mining", "Foraging", "Farming", "Alchemy", "Smithing", "Cooking", "Acrobatics", "Exploration"]
ALL = (1 << len(LINES)) - 1


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0311", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
SKILLS_JAR = os.path.abspath(arg("--skills", os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.11.jar")))
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


# ======================================================================================================== child: one JVM, one HUD jar
def run_child(jar, out, mode):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    import skyybuild as B
    extra = [SKILLS_JAR, CLASSES_JAR] if mode == "new" else []
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

    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()

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

    def party_guild():
        bridge.put("party:fn:members", Members())
        bridge.put("party:leader:" + str(uid(1)), str(uid(1)))
        for n, nm, st in ((1, "Steve", "18,20,9,10,0,0,world-a"), (2, "Alex", "20,20,10,10,40,50,world-a"), (3, "Bea", "5,20,1,10,0,0,hub")):
            bridge.put("party:name:" + str(uid(n)), nm)
            bridge.put("party:stats:" + str(uid(n)), st)
        bridge.put("guild:" + str(uid(1)), "Sky Squad")
        bridge.put("guild:info:" + str(uid(1)), "Sky Squad|SKY|3|1240|2000|3|5|Leader")
        bridge.put("guild:fn:online", Online())

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
            lay(pr, "Skills").en = False
        scen("editor live %d" % k, *page(EP(pr, plugin)))
    # S3 every old widget on, styles, party + guild
    use_dir("s3")
    party_guild()
    me = pref(1)
    m = LS.get(me.getUuid())
    pal = ["gold", "aqua", "def", "red", "lime", "def", "blue", "pink", "def", "gray"]
    for i, wid in enumerate(OLD_IDS):
        l = m.get(wid)
        l.en = True
        l.col = pal[i]
        l.glow = (i % 3 == 0)
        l.gcol = "black" if i % 2 else "def"
        l.ital = (i % 4 == 1)
        l.bold = (i % 5 != 2)
        l.scale = 50 + 15 * i
        Wid.clampToScreen(l)
    m.get("Guild").opt = True
    if mode == "new":
        m.get("Skills").en = False
    cm = hud(me)[1]
    scen("hud all styled", [c for c in cm if not (c[0] == "Set" and c[1] and (c[1].startswith("#SkyyWRclock") or c[1].startswith("#SkyyWSession")))])
    # S4 the editor with the default layout (Skills hidden in 0.3.11 - its handle would take a canvas cell)
    use_dir("s4")
    clear_bridge(["party:", "guild:"])
    me = pref(1)
    if mode == "new":
        lay(me, "Skills").en = False
    scen("editor default", *page(EP(me, plugin)))
    # S5 the Settings page of every old widget, S6 the Widgets page
    for wid in OLD_IDS:
        use_dir("s5-" + wid)
        scen("settings " + wid, *page(SP(pref(1), plugin, wid)))
    use_dir("s6")
    scen("widgets page", *page(WP(pref(1), plugin)))

    # ===================================================================================== G (both jars): the editor on the old widgets
    def editor_script(tag):
        """drag / size / arrows / snap every old widget with Skills hidden; returns {id: ser()} after each step group"""
        use_dir("g-" + tag)
        me = pref(7, "Ed")
        m = LS.get(me.getUuid())
        for wid in OLD_IDS:
            m.get(wid).en = True
        if mode == "new":
            m.get("Skills").en = False
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

    if mode != "new":
        json.dump(res, open(out, "w"), indent=1)
        return

    # ========================================================================================== the 0.3.11-only checks (B-H)
    import skyyui as SUI
    Skills = JClass("com.skyy.skills.SkillStore")
    Defs = JClass("com.skyy.skills.SkillDefs")
    Ovl = JClass("com.skyy.skills.Overall")
    SkFn = JClass("com.skyy.skills.SkillFn")
    CDefs = JClass("com.skyy.classes.ClassDefs")
    LBL = [str(x) for x in Defs.LABELS]
    CLASSES = [str(x) for x in Defs.CLASSES]
    C_SLOT = [int(x) for x in Defs.CLASS_SLOT]
    Defs.setTable(Defs.DEFAULT_PER)
    CUM = [int(x) for x in Defs.CUM]

    @JImplements("java.util.function.Function")
    class Allowed(object):
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").TRUE

    def xp_for(level):
        return Long(CUM[level])

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

    # ---- B: defaults
    use_dir("b")
    d0 = wdef("Skills")
    chk(bool(d0.en) and str(d0.anchor) == "tl" and int(d0.dx) == 8 and int(d0.dy) == 544 and int(d0.scale) == 100 and int(d0.bw) == 180
        and int(d0.bh) == 206 and int(d0.lines) == 3 and int(d0.ldef) == 3 and bool(d0.bg) and bool(d0.styleDefault()),
        "B: Widgets.def(Skills) = ON tl 8,544 100%% 180x206 lines 3 (got %s %s %s)" % (d0.ser(), d0.lines, d0.ldef))
    for wid in OLD_IDS:
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
    chk(any(c[3] and "Height: %d)" % (150 + 62 * 11) in c[3] for c in wc[:1]), "B: the Widgets page is 150 + 62 x 11 px high")
    scm, sce = page(SP(me, plugin, "Skills"))
    chk(scm and "Anchor: (Width: 1500, Height: 940)" in (scm[0][3] or ""), "B: the Skills Settings page is 1500 x 940")
    # review fix LOW 1: every Settings page's rows + padding fit its root with at least 20 px to spare, and the page fits 1080 high
    for wid in IDS:
        ph_, pad_, rows_ = page_rows(page(SP(me, plugin, wid))[0])
        spare = ph_ - pad_ - rows_
        chk(20 <= spare and ph_ <= 1080 and (wid != "Skills" or (ph_, rows_) == (940, 894)) and (wid == "Skills" or (ph_, rows_) == (790, 748)),
            "B: Settings page %s: rows %d + padding %d in %d px -> %d px spare (need >= 20; Skills 894 of 940, the others 748 of 790)"
            % (wid, rows_, pad_, ph_, spare))
    chk(len(hint_of(scm)) == 1 and '- Class skill follows your class"' in hint_of(scm)[0] and "needs SkyyClasses" not in hint_of(scm)[0],
        "B: with SkyyClasses the hint ends 'Class skill follows your class': %s" % hint_of(scm))
    lnb = [e for e in sce if e[1] and e[1].startswith("#SkyySetLn")]
    want_b = [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(5)] + [("#SkyySetLnAll", '"lnall"')] +              [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(5, 10)] + [("#SkyySetLnDef", '"lndef"')]
    chk(len(lnb) == len(want_b) and all(e[1] == w[0] and w[1] in (e[2] or "") and e[0] == "Activating" for e, w in zip(lnb, want_b)),
        "B: Lines toggles ln:0-9 + All on + Default: %s" % [(e[0], e[1], e[2]) for e in lnb])
    lit = lit_of(scm)
    chk(lit == ["SkyySetLn0", "SkyySetLn1", "SkyySetLnDef"], "B: lit = Overall Level, Class skill, Default: %s" % lit)
    chk(not any(e[1] in ("#SkyySetOptOn", "#SkyySetOptOff") for e in sce), "B: no Party / Guild option row on the Skills page")
    for c in scm:
        if c[0] == "AppendInline" and c[3] and ("SkyySetLn" in c[3] or "SkyySetRowLn" in (c[1] or "") or "SkyySetRowLn" in c[3]):
            try:
                SUI.check_markup(c[3])
                chk(True, "")
            except ValueError as e:
                chk(False, "B: check_markup(Lines row): %s: %s" % (e, c[3][:100]))
    labels = [js(c[2]) for c in scm if c[0] == "Set" and c[1] == "#SkyySetPvATxt.Text"]
    chk(labels == ["Overall Level " + str(ol)], "B: the Settings preview shows the first line: %s" % labels)

    # ---- C: per-player persistence
    A, Bp = pref(11, "Ann"), pref(12, "Bob")
    use_dir("c")
    for p in (A, Bp):
        skills_world(p.getUuid(), LV, "Archer")
    fa = os.path.join(work, "c", "layouts", str(A.getUuid()) + ".properties")
    fb = os.path.join(work, "c", "layouts", str(Bp.getUuid()) + ".properties")

    def props(f):
        out = {}
        if os.path.isfile(f):
            for ln in open(f, encoding="latin-1"):
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    out[k] = v
        return out

    spA = SP(A, plugin, "Skills")
    spA.handleDataEvent(None, None, '{"a":"ln:2"}')
    chk(int(lay(A, "Skills").lines) == 7 and props(fa).get("Skills") == "1,tl,8,544,100,1,def,1,0,0,def,1,7",
        "C: Ann turns Mining on -> mask 7, her file: %s" % props(fa).get("Skills"))
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
    chk("Skills=1:tl:8:544:100:1:def:1:0:0:def:1:547" in code, "C: export carries mask 547 (%s)" % code[-60:])
    Cc = pref(13, "Cid")
    n = int(LS.importCode(Cc.getUuid(), code))
    chk(n == 11 and int(lay(Cc, "Skills").lines) == 547 and int(lay(Cc, "Skills").ldef) == 3, "C: import into another player keeps 547")
    chk(bool(LS.profileSave(A.getUuid(), "mine")), "C: profile save")
    spA.handleDataEvent(None, None, '{"a":"lndef"}')
    chk(int(LS.profileLoad(A.getUuid(), "mine")) == 11 and int(lay(A, "Skills").lines) == 547, "C: profile load brings 547 back")
    # old codes without a Skills part import as before and leave Skills alone
    n = int(LS.importCode(Cc.getUuid(), "Coords=1:tr:8:8:100:1;Zone=0:tl:8:8:100:1"))
    chk(n == 2 and int(lay(Cc, "Skills").lines) == 547, "C: a 0.3.10 code imports 2 widgets, Skills unchanged")
    n = int(LS.importCode(Cc.getUuid(), "Skills=1:tl:8:544:100:1"))
    chk(n == 1 and int(lay(Cc, "Skills").lines) == 3, "C: a Skills part without a mask = the default lines")
    # the server default layout
    Cfg.DEFAULT_LAYOUT = "Skills=1:tr:8:72:100:1:def:1:0:0:def:1:5"
    chk(Cfg.codeError(Cfg.DEFAULT_LAYOUT) is None, "C: a server default code with a Skills mask is valid")
    Dp = pref(14, "Dot")
    ld = lay(Dp, "Skills")
    chk(str(ld.anchor) == "tr" and int(ld.dy) == 72 and int(ld.lines) == 5 and int(ld.ldef) == 3, "C: a new player gets the server default (tr, mask 5)")
    # review fix LOW 2: "Default" = the lines a new player starts with (= /skyyhud reset): the server default's mask, lit for exactly it
    fdot = os.path.join(work, "c", "layouts", str(Dp.getUuid()) + ".properties")
    spDot = SP(Dp, plugin, "Skills")
    lt = lit_of(page(spDot)[0])
    chk(lt == ["SkyySetLn0", "SkyySetLn2", "SkyySetLnDef"], "C: on the server default (mask 5) Default is lit with Overall Level + Mining: %s" % lt)
    chk(start_lines("Skills") == 5 and start_lines("Party") == -1, "C: startLines = the server default's 5 (Party: -1, no lines)")
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
    # forged line clicks on another widget's page do nothing
    before = str(lay(A, "Party").ser())
    for pl in ('{"a":"ln:2"}', '{"a":"lnall"}', '{"a":"lndef"}'):
        SP(A, plugin, "Party").handleDataEvent(None, None, pl)
    chk(str(lay(A, "Party").ser()) == before and int(lay(A, "Party").lines) == -1, "C: line clicks on the Party page change nothing")
    for pl in ('{"a":"ln:10"}', '{"a":"ln:-1"}', '{"a":"ln:x"}', '{"a":"ln:99999999999"}'):
        spA.handleDataEvent(None, None, pl)
    chk(int(lay(A, "Skills").lines) == 3, "C: out-of-range line clicks change nothing")
    # broken masks in a file
    for bad, want_scale in (("0", 100), ("-4", 100), ("abc", 125), ("", 100), ("2147483648", 100)):
        write_layout("c-bad", uid(30), ["Skills=1,tl,8,544,%d,1,def,1,0,0,def,1,%s" % (want_scale, bad)])
        use_dir("c-bad")
        lb = lay(pref(30), "Skills")
        chk(int(lb.lines) == 3 and int(lb.scale) == want_scale and str(lb.anchor) == "tl", "C: mask %r in a file -> default 3, rest kept" % bad)
    write_layout("c-bad", uid(30), ["Skills=1,tl,8,544,100,1,def,1,0,0,def,1,1031"])
    use_dir("c-bad")
    chk(int(lay(pref(30), "Skills").lines) == 1031 and str(lay(pref(30), "Skills").ser()).endswith(",1031"), "C: an unknown future bit is kept")

    # ---- D: any combo
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
    # review fix LOW 3: the same masks with SkyyClasses NOT installed (no class:list; the stale class:skill:<u> stays on purpose -
    # the install marker decides): exactly the Class skill line is left out, every other line, value and the height follow
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
    # markup of a sample of masks at several sizes through the real widget source
    nb = 0
    for mask in (1, 2, 3, 512, 1023, 341, 682):
        for sc in (50, 70, 100, 130, 200):
            l.lines, l.scale = mask, sc
            src = str(Wid.multiWidgetSrc("Skills", l, Wid.modelL("Skills", me, l)))
            try:
                SUI.check_markup(src)
            except ValueError as e:
                chk(False, "D: check_markup mask %d @%d: %s" % (mask, sc, e))
            n_ = bin(mask).count("1")
            hh = int(Wid.bodyH("Skills", Wid.modelL("Skills", me, l), sc))
            chk("Height: %d)" % hh in src and hh <= int(Wid.hMax(l)), "D: mask %d @%d%%: group height %d <= max box %d" % (mask, sc, hh, int(Wid.hMax(l))))
            nb += 1
    l.lines, l.scale = 3, 100
    # random click sequences on the Settings page
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

    # ---- E: the class line follows the class
    use_dir("e")
    me = pref(1)
    skills_world(me.getUuid(), LV, "Archer")
    h, cm = hud(me)
    b0 = UCB()
    re_ = bool(h.fill(b0, False))
    chk(not re_ and not [c for c in cmds(b0) if "Skills" in str(c[1])], "E: a tick with nothing new sends no Skills text")
    # review INFO 4 (kept on purpose): the 0.3.9 confirm send follows a NEW widget shape only - the first build of a HudMain (a join /
    # world switch makes a new one) arms it once; once it fired, a rebuild with the same shape arms nothing: never periodic
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
    # profile switch: SkyySkills republishes skill:<u> for the new profile
    lv4 = {"Mining": 1, "Combat.Mage": 2}
    skills_world(me.getUuid(), LV, "Archer")
    h, cm = hud(me)
    skills_world(me.getUuid(), lv4, "Mage")
    b3 = UCB()
    re_ = bool(h.fill(b3, False))
    s3 = sets(cmds(b3))
    chk(not re_ and s3.get("#SkyyWSkillsN1Txt.Text") == "Sorcery" and s3.get("#SkyyWSkillsS1Txt.Text") == "2", "E: profile switch -> Sorcery 2: %s" % s3)

    # ---- F: missing / broken bridge
    use_dir("f")
    me = pref(1)
    System.getProperties().remove("skyy.bridge")
    mm = [None if x is None else str(x) for x in Wid.skillsModelU(me.getUuid(), ALL)]
    chk(mm[0] == "K0" and mm[1] is None, "F: no skyy.bridge at all -> hidden")
    h, cm = hud(me)
    chk(not any("SkyyWSkills" in str(c[3]) + str(c[1]) for c in cm) and str(h.shape.get("Skills")) == "K0", "F: ... the HUD draws no Skills widget")
    ec, ee = page(EP(me, plugin))
    stE = sets(ec)
    chk(stE.get("#SkyyEPvSkillsN0Txt.Text") == "Skills not installed" and "#SkyyEPvSkillsN1Txt.Text" not in stE,
        "F: ... the editor shows one line 'Skills not installed'")
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
                ok = ok and mm[7] == "-" and mm[9] == "-" and mm[11] == "-" and mm[13] == "5"   # Mining: the 1st entry decides (abc), Foraging '', Farming -2, Alchemy 4.6 -> 5
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

    # ---- review fix LOW 3: SkyyClasses NOT installed (no class:list - a stale class:skill:<u> stays in the bridge on purpose)
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

    # ---- G: the Skills widget in the editor (all 11 widgets on, 10 lines)
    use_dir("g")
    me = pref(1)
    skills_world(me.getUuid(), LV, "Archer")
    party_guild()
    m = LS.get(me.getUuid())
    for wid in IDS:
        m.get(wid).en = True
    m.get("Skills").lines = ALL
    ep = EP(me, plugin)
    ec, ee = page(ep)
    placed = sorted(set(str(w) for w in ep.cellWidget if w is not None))
    chk(placed == sorted(IDS), "G: all 11 widgets have a canvas handle: %s" % placed)
    chk(all(any(c[3] and ("Group #SkyyEPv%s " % w) in c[3] for c in ec) for w in IDS), "G: all 11 previews drawn")
    ids_all = []
    for c in ec:
        if c[0] == "AppendInline" and c[3]:
            ids_all += re.findall(r"#([A-Za-z0-9_]+)\s*\{", c[3])
    chk(len(ids_all) == len(set(ids_all)) and not [i for i in ids_all if "_" in i], "G: editor ids unique, no underscores (%d)" % len(ids_all))
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

        def start():
            LS.CACHE.clear()
            EP.STEPS.clear()
            LS.DIR = Paths.get(os.path.join(hdir, "layouts"))
            Cfg.FILE = Paths.get(os.path.join(hdir, "config.properties"))
            Cfg.PARSED = None
            r = {"cfg": str(Cfg.load())}
            Pub.start(Paths.get(mods), None)
            for k, us in enumerate(players):
                pr = U.allocateInstance(PRef.class_)
                setf(pr, PRef, "uuid", UUID.fromString(us))
                setf(pr, PRef, "username", "Live%d" % k)
                skills_world(pr.getUuid(), LV, "Archer")
                mp = LS.get(pr.getUuid())
                r[us] = dict((w, str(mp.get(w).ser())) for w in IDS)
                h, cm = hud(pr)
                r[us + " hud"] = sorted(v for k2, v in sets(cm).items() if "Skills" in k2)
                page(EP(pr, plugin))
                page(SP(pr, plugin, "Skills"))
                page(WP(pr, plugin))
            Pub.flush()
            return r
        t0 = tree()
        time.sleep(1.1)
        r1 = start()
        t1 = tree()
        chk(t1 == t0, "H: start 1 on the live copy writes nothing (every byte + modification time; new %s changed %s)"
            % (sorted(k for k in t1 if k not in t0), sorted(k for k in t0 if k in t1 and t0[k] != t1[k])))
        for us in players:
            fl = props(os.path.join(hdir, "layouts", us + ".properties"))
            chk(all(r1[us][w] == fl[w] for w in OLD_IDS if w in fl), "H: %s...: every old widget loads exactly as saved" % us[:8])
            chk(r1[us]["Skills"] == "1,tl,8,544,100,1" and "Skills" not in fl, "H: %s...: Skills = the default, not written" % us[:8])
            chk(r1[us + " hud"] == sorted(["Overall Level", str(ol), "Archery", "18"]), "H: %s...: the HUD shows Overall + Archery: %s" % (us[:8], r1[us + " hud"]))
        time.sleep(1.1)
        r2 = start()
        t2 = tree()
        chk(r2 == r1 and t2 == t1, "H: start 2: same layouts, no file churn")
        if players:
            us = players[0]
            pr = U.allocateInstance(PRef.class_)
            setf(pr, PRef, "uuid", UUID.fromString(us))
            setf(pr, PRef, "username", "Live0")
            before = props(os.path.join(hdir, "layouts", us + ".properties"))
            SP(pr, plugin, "Skills").handleDataEvent(None, None, '{"a":"ln:2"}')
            after = props(os.path.join(hdir, "layouts", us + ".properties"))
            t3 = tree()
            changed = sorted(k for k in t3 if t3[k] != t2.get(k))
            chk(changed == [os.path.join("Skyy_SkyyHud", "layouts", us + ".properties")]
                and dict((k, v) for k, v in after.items() if k != "Skills") == before and after.get("Skills") == "1,tl,8,544,100,1,def,1,0,0,def,1,7",
                "H: one toggle writes only that player's file: the old lines kept, + Skills=...,7 (changed %s)" % changed)
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
SKILLS_RE = re.compile(r"Skills")


def filt(cm, drop_hidden_btn=False):
    """commands without the Skills widget's own (appends / sets naming Skills; the Hidden-row spacer right after its button)"""
    out, skip_next = [], False
    for c in cm:
        if skip_next:
            skip_next = False
            if c[0] == "AppendInline" and c[1] == "#SkyyEOff" and "Width: 4, Height: 22" in (c[3] or ""):
                continue
        if SKILLS_RE.search(str(c[1])) or SKILLS_RE.search(str(c[3])):
            if c[0] == "AppendInline" and "#SkyyEOnSkills" in (c[3] or ""):
                skip_next = True
            if c[0] == "AppendInline" and "#SkyyESelSkills" in (c[3] or ""):
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
    common = ["--dir", SCRATCH, "--skills", SKILLS_JAR, "--classes", CLASSES_JAR, "--live", LIVE]
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        outs[tag] = os.path.join(SCRATCH, "child-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--mode", tag] + common, env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s ran (exit %s)" % (os.path.basename(j), p.returncode))
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
    # B-H (in the 0.3.11 child)
    nb = 0
    for ok, what in new["checks"]:
        if what:
            check(ok, what)
            nb += 1
    print("B-H. %d checks in the 0.3.11 JVM (%d failed); live copy players: %s" % (nb, sum(1 for ok, w in new["checks"] if not ok), new.get("live_players")))
    if os.path.isdir(LIVE):
        check(new.get("live_players", -1) >= 1, "H: the live Skyy_SkyyHud folder was copied and holds at least one layout (%s)" % LIVE)
    else:
        # review INFO: another machine / a clean checkout has no live world - H is skipped (and said so), not failed
        SKIPS.append("H (start twice on a copy of the live data): no live Skyy_SkyyHud folder at %s" % LIVE)
        print("H. SKIPPED - no live Skyy_SkyyHud folder at %s (pass --live <folder> to run it)" % LIVE)
    # S: 0.3.10 vs 0.3.11 for the old widgets
    ns = 0
    for name in sorted(old["scen"]):
        o, n = old["scen"][name], new["scen"].get(name)
        if n is None:
            check(False, "S: scenario %s missing in 0.3.11" % name)
            continue
        oc, nc = o["cmds"], n["cmds"]
        if name == "widgets page":
            oc = [[c[0], c[1], c[2], re.sub(r"Height: \d+\)", "Height: H)", c[3] or "", 1) if i == 0 else c[3]] for i, c in enumerate(oc)]
            nc = [[c[0], c[1], c[2], re.sub(r"Height: \d+\)", "Height: H)", c[3] or "", 1) if i == 0 else c[3]] for i, c in enumerate(nc)]
        fo, fn_ = filt(oc), filt(nc)
        same = fo == fn_
        if not same:
            for i, (a, b) in enumerate(zip(fo, fn_)):
                if a != b:
                    print("   first difference in %s at %d:\n     0.3.10 %s\n     0.3.11 %s" % (name, i, a, b))
                    break
        check(same and len(fo) == len(oc), "S: %s: 0.3.11 = 0.3.10 apart from the Skills widget (%d / %d commands, %d Skills-only)"
              % (name, len(oc), len(nc), len(nc) - len(fn_)))
        ev_o = [e for e in o["evs"]]
        ev_n = [e for e in n["evs"] if "Skills" not in str(e[1]) + str(e[2])]
        check(ev_o == ev_n, "S: %s: event bindings identical apart from Skills (%d / %d)" % (name, len(o["evs"]), len(n["evs"])))
        ns += 1
    print("S. %d scenarios: 0.3.10 output = 0.3.11 output apart from the Skills widget" % ns)
    # G (old widgets, both jars): identical layouts after the same editor clicks
    ge = 0
    for wid in OLD_IDS:
        a, b = old["edit"].get(wid), new["edit"].get(wid)
        check(a == b and a != "no handle", "G: %s: drag / Size / arrows / Snap to give the same layout in both jars: %s / %s" % (wid, a, b))
        ge += 1
    print("G. editor clicks on %d old widgets: identical in 0.3.10 and 0.3.11; Skills after drag/size/snap: %s" % (ge, new.get("edit_new_skills")))
    # F1: class bytes
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F1: same entries in both jars")
    diff = sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    want_diff = sorted(["manifest.json"] + ["com/skyy/hud/%s.class" % c for c in (
        "WLayout", "Widgets", "LayoutStore", "HudMain", "EditorPage", "SettingsPage", "SkyyHudPlugin",
        "CfgFile", "CfgFn", "CfgHist", "CfgRows", "CfgSaveTask")])
    check(diff == want_diff, "F1: exactly these entries differ: %s (got %s)" % (want_diff, diff))
    bc = json.load(open(bco))
    expect = {
        "WLayout": ({"WLayout", "ser", "parse", "<clinit>"}, set(), set()),
        "Widgets": ({"multi", "model", "linePairs", "bodyH", "multiBody", "viewH", "def", "label", "sampleU", "<clinit>"},
                    {"skillVal", "skillsHave", "classesHave", "skillsVis", "skillsModelU", "modelL", "skillsSample", "skillRows",
                     "skillsBody", "viewModel", "startLines"}, {"viewModel"}),
        "LayoutStore": ({"importCode"}, set(), set()),
        "HudMain": ({"fill", "build"}, set(), set()),
        "EditorPage": ({"prepView", "appendPreviews"}, set(), set()),
        "SettingsPage": ({"previewText", "build", "handleDataEvent"}, set(), set()),
        "SkyyHudPlugin": ({"setup"}, set(), set()),
    }
    for cname, (chg, nw, gone) in expect.items():
        r = bc.get("com/skyy/hud/%s.class" % cname, {})
        got_c = set(k.split("(")[0] for k in r.get("changed", []))
        got_n = set(k.split("(")[0] for k in r.get("new", []))
        got_g = set(k.split("(")[0] for k in r.get("gone", []))
        check(got_c == chg and got_n == nw and got_g == gone, "F1: %s: changed %s new %s gone %s (got %s / %s / %s)"
              % (cname, sorted(chg), sorted(nw), sorted(gone), sorted(got_c), sorted(got_n), sorted(got_g)))
    wl = bc.get("com/skyy/hud/WLayout.class", {})
    check(wl.get("fields_new") == sorted(["LINES_ALL I", "LINES_DEF I", "LINE_LABELS [Ljava/lang/String;", "LINE_N I", "ldef I", "lines I"])
          and not wl.get("fields_gone"), "F1: WLayout gains lines, ldef + the line table: %s" % wl.get("fields_new"))
    sp = bc.get("com/skyy/hud/SkyyHudPlugin.class", {})
    check(sp.get("version_only"), "F1: SkyyHudPlugin.setup differs only by the version in the ready line")
    print("F1. class bytes: %d entries identical; differ: %s" % (len(set(zo.namelist()) & set(zn.namelist())) - len(diff),
                                                              ", ".join(x.split("/")[-1] for x in diff)))
    # F2: rebuild 0.3.10 with today's tools to separate the config kit pickup from the 0.3.11 changes
    if "--no-rebuild" not in sys.argv:
        rb = os.path.join(SCRATCH, "rebuild010")
        os.makedirs(rb)
        for f in ("build_skyyhud_0.3.10.py", "icon-256.png", "skyyhud_dot.png"):
            shutil.copy2(os.path.join(HERE, f), os.path.join(rb, f))
        env2 = dict(env)
        env2["PYTHONPATH"] = TOOLS
        env2["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        p = subprocess.run([sys.executable, "build_skyyhud_0.3.10.py"], cwd=rb, env=env2, capture_output=True, text=True)
        rjar = os.path.join(rb, "SkyyHud-0.3.10.jar")
        check(p.returncode == 0 and "assembled" in p.stdout and os.path.isfile(rjar), "F2: 0.3.10 rebuilds in scratch: %s" % (p.stdout[-200:] + p.stderr[-300:]))
        if os.path.isfile(rjar):
            hud_cls = [n for n in zo.namelist() if n.endswith(".class") and not n.split("/")[-1].startswith("Cfg")]
            with zipfile.ZipFile(rjar) as zr:      # closed again at once: Windows cannot delete the scratch folder around an open jar
                same = [n for n in hud_cls if zo.read(n) == zr.read(n)]
            check(len(same) == len(hud_cls), "F2: the rebuilt 0.3.10's HUD classes equal the 0.3.10 jar's (%d / %d; differ %s)"
                  % (len(same), len(hud_cls), sorted(set(hud_cls) - set(same))))
            bc2 = os.path.join(SCRATCH, "bytecode-kit.json")
            p = subprocess.run([sys.executable, me, "--bytecode", rjar, "--new", JAR, "--out", bc2, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
            r2 = json.load(open(bc2)) if os.path.isfile(bc2) else {}
            kit = dict((k, v) for k, v in r2.items() if k.split("/")[-1].startswith("Cfg"))
            bad = []
            keep_sites = [0]
            for k, v in kit.items():
                for mk in v["changed"]:
                    a, b = v["diff"].get(mk, ["", "x"])
                    la, lb = a.replace(OLD_VERSION, "V").splitlines(), b.replace(VERSION, "V").splitlines()
                    # line by line: equal, or the inlined KEEP constant (bipush 20 -> bipush 10) at the same place
                    if len(la) != len(lb) or any(x != y and (x, y) != ("bipush 20", "bipush 10") for x, y in zip(la, lb)):
                        bad.append("%s.%s" % (k.split("/")[-1], mk.split("(")[0]))
                    keep_sites[0] += sum(1 for x, y in zip(la, lb) if (x, y) == ("bipush 20", "bipush 10"))
                if v["new"] or v["gone"] or not v["fields_same"]:
                    bad.append("%s fields/methods" % k)
                for c, (x, y) in v["consts"].items():
                    if (x or "").replace(OLD_VERSION, "V") != (y or "").replace(VERSION, "V") and not (x == "20" and y == "10"):
                        bad.append("%s const %s %s -> %s" % (k, c, x, y))
            check(not bad, "F2: config kit classes rebuilt-0.3.10 vs 0.3.11 differ only by the version + KEEP 20 -> 10: %s (classes %s)"
                  % (bad, sorted(x.split("/")[-1] for x in kit)))
            print("F2. 0.3.10 rebuilt in scratch: HUD classes reproducible (%d / %d); kit classes vs 0.3.11: %s (%d inlined KEEP sites, consts %s)"
                  % (len(same), len(hud_cls), "version + KEEP only" if not bad else bad, keep_sites[0],
                     dict((k.split("/")[-1], v["consts"]) for k, v in kit.items() if v["consts"])))
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
