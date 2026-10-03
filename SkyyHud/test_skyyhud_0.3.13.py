"""SkyyHud 0.3.13 - bare-JVM harness for the CONTENT-SIZED BOXES and the Combat widget's two colours (tools/hud_0_3_13_patch.py).

    python SkyyHud/test_skyyhud_0.3.13.py [--jar <SkyyHud-0.3.13.jar>] [--old <SkyyHud-0.3.12.jar>] [--live <Skyy_SkyyHud folder>]
                                          [--dir <scratch>] [--keep] [--no-rebuild]

Build the jar first (python SkyyHud/build_skyyhud_0.3.13.py). Child processes start fresh JVMs (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, java.io.tmpdir + TEMP/TMP in the scratch folder; HytaleServer.jar + the HUD jar; the bridge values the Party / Guild /
Skills / Combat widgets read are plain fakes with the agreed contracts; javassist for the fake asset store, the bytecode and the audit
steps). Every check EXECUTES the jar's own code:
  A   every class of the 0.3.13 jar and of the 0.3.12 jar loads and initializes under -Xverify:all
  T   the font table inside the jar (Widgets.ADVB / ADVM) = the vanilla kit's (tools/skyyui.py text_width per glyph, both weights);
      CAPK = line height / 2 - ascender + cap height re-read from the client's font files; P(size) for every size; textW = the kit's
      width rounded up, for real texts
  P   EVERY widget at EVERY size the HUD can have (50-200 % in tens + 75 / 125) built by the real HudMain.build: box width = the text
      (kit) + 2P, the height as before (Combat in combat 37 x size), never above the clamp box, on screen; the visible gaps (box edge
      to the letters: left, right, top over the caps, bottom under the last baseline / under the bar): left within 1 px of the top,
      right 1.5 px (widths round UP so a text never clips), bottom 2.1 px (Guild's small 0.3.12 name rows, unchanged, sit up to 2 px
      lower at 130-180 %). The task's sizes 50 / 100 / 200 % are reported widget by widget (before / after)
  C   corners: the Game Clock (and the Real Clock, which shows a real HH:MM in a bare JVM) at 50 / 100 / 170 / 200 % into all four
      corners - Snap to + the editor arrows down to x = y = 0, and a drag from the opposite corner + Step 25 arrows: anchor = the corner,
      the HUD anchor (Top|Bottom: 0, Left|Right: 0), the text P px from both screen edges, the editor preview in the canvas corner;
      the same clicks in 0.3.12 leave the text 74 px (100 %) from the edge
  K   the two Combat colours end to end: the Settings page rows (In combat: 13 swatches, Default shows red; Out of combat: 13 swatches,
      Default shows grey; the picked one ringed), col: / ocol: clicks -> the saved file line (14th field only with an out-of-combat
      colour), a reload from the file, the HUD in combat and out of combat (Show) in the picked colours, glow Same / Black, Default =
      0.3.12's grey text + grey glow byte for byte, the editor sample, the two preview rows, Reset style, export / import, profiles,
      the server default layout, forged ocol on another widget ignored
  L   a 0.3.12 layout FILE, EXPORT CODE and PROFILE written by the 0.3.12 jar load in 0.3.13 with identical lines (anchor / x / y /
      size / styles / lines / opt) and the HUD builds; how far each widget's text moves (reported); 0.3.12 reads a 0.3.13 line with
      an out-of-combat colour (rollback): every field but the 14th
  W   the width follows the text on one HudMain: more room -> re-send asked at once; less room -> only after 15 s (no flapping);
      the same width -> only .Text sets; Skills 9 -> 10 grows; Party HP swings never resize; the clock never re-sends
  E   the editor: previews / outline / handles use the drawn box; Size / arrows / Snap to give byte-identical layouts to 0.3.12; a
      drag drops the drawn box where it was dropped; the HUD margins land where the editor draws it (every anchor, 50 / 100 / 200 %)
  S   0.3.12 vs 0.3.13 on the same layouts (HUD builds, editors, every non-Combat Settings page, the Widgets page): the same texts,
      element ids, event bindings and markup once the Anchor numbers are normalised - only the box geometry changed
  X   Combat regression: in combat a tick sends exactly the countdown text + the bar Value, a re-hit jumps back, leaving re-sends
  H   start twice on a scratch COPY of the live Skyy_SkyyHud (the live folder is only read): nothing written, every layout loads
      exactly as saved; the live layouts' boxes old -> new (reported)
  Z   engine-access audit: every class / field / method / constructor reference of the 0.3.13 jar looked up with MethodHandles.Lookup
      in its own class (a protected engine member only from a subclass) - 0 refused; control: a class calling the protected
      CustomUIHud.onRemove from outside is refused AND throws IllegalAccessError when run
  F1  class bytes 0.3.12 vs 0.3.13: only the expected classes / methods differ
  F2  (unless --no-rebuild) 0.3.12 rebuilt in scratch with today's tools: its HUD classes equal the 0.3.12 jar's (so every difference is
      the patch's), its kit classes differ from 0.3.13's only by the version string
Not testable without the game (UNVERIFIED in the build report): the client's own text rendering width (the kit's table is the
client's atlas; kerning none), how the boxes look, a width re-send on a real client.
Nothing is deployed. Default scratch folder: tools/dev/scratch/hud0313/harness (git-ignored), deleted at the end unless --keep.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, math, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3.13", "0.3.12"
PKG = "com.skyy.hud."
IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild", "Skills", "Combat"]
ONE = IDS[:8]
MULTI = IDS[8:]
LINES = ["Overall Level", "Class skill", "Mining", "Foraging", "Farming", "Alchemy", "Smithing", "Cooking", "Acrobatics", "Exploration"]
ALL = (1 << len(LINES)) - 1
RED, GREY, GREYG = "#ff6b6b", "#8b949e", "#5a626b(0.35)"
SIZES = [50, 60, 70, 75, 80, 90, 100, 110, 120, 125, 130, 140, 150, 160, 170, 180, 190, 200]
MAXBOX = {"Party": (340, 116), "Guild": (260, 94), "Skills": (180, 206), "Combat": (180, 37)}


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0313", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
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
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:
        x = x["0"]
    return x


# ---------------- font metrics (read-only, the client's files; the kit for the advances)
def font_numbers():
    import skyyui as SUI
    fj = json.load(open(os.path.join(SUI.FONT_DIR, "NunitoSans-ExtraBold.json"), encoding="utf-8"))["metrics"]
    d = open(os.path.join(SUI.FONT_DIR, "NunitoSans-ExtraBold.ttf"), "rb").read()
    tabs = {}
    for i in range(struct.unpack(">H", d[4:6])[0]):
        tag, _c, off, ln = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i])
        tabs[tag.decode("latin-1")] = off
    upem = struct.unpack(">H", d[tabs["head"] + 18:tabs["head"] + 20])[0]
    cap = struct.unpack(">h", d[tabs["OS/2"] + 88:tabs["OS/2"] + 90])[0] / float(upem)
    return float(fj["lineHeight"]), abs(float(fj["ascender"])), cap


def pad_expected(sc, minfs=6, multi=False):
    lh, asc, cap = font_numbers()
    k = lh / 2 - asc + cap
    fs = max(minfs, 12 * sc // 100)
    top = (3 * sc // 100 + (20 * sc // 100) / 2.0) if multi else (26 * sc // 100) / 2.0
    return max(1, int(math.floor(top - k * fs + 0.5)))


ANC_RE = re.compile(r"Anchor: \((Top|Bottom): (-?\d+), (Left|Right): (-?\d+), Width: (\d+), Height: (\d+)\)")
RECT_RE = re.compile(r"Anchor: \(Left: (-?\d+), Top: (-?\d+), Width: (\d+), Height: (\d+)\)")


def group_rect(markup):
    """(x, y, w, h) on the 1920 x 1080 screen of a HUD widget Group's anchor"""
    m = ANC_RE.search(markup or "")
    if not m:
        return None
    w, h = int(m.group(5)), int(m.group(6))
    x = int(m.group(4)) if m.group(3) == "Left" else 1920 - w - int(m.group(4))
    y = int(m.group(2)) if m.group(1) == "Top" else 1080 - h - int(m.group(2))
    return (x, y, w, h)


def labels_of(markup, base):
    """the real text labels (no glow copies) inside a widget markup: suffix -> (x, y, w, h | None for Full, fs, bold, align)"""
    out = {}
    for m in re.finditer(r"Label #%s([A-Za-z0-9]*?)Txt \{ Anchor: \(([^)]*)\); Text: \\?\"\\?\"; Style: \(FontSize: (\d+), RenderBold: (true|false)"
                         r"[^)]*?HorizontalAlignment: (\w+)" % re.escape(base), markup or ""):
        a = m.group(2)
        r = RECT_RE.search("Anchor: (" + a + ")")
        out[m.group(1)] = ((int(r.group(1)), int(r.group(2)), int(r.group(3)), int(r.group(4))) if r else None, int(m.group(3)),
                           m.group(4) == "true", m.group(5))
    return out


# ======================================================================================================== child: one JVM, one HUD jar
def run_child(jar, out, mode):
    from jpype import JClass, JImplements, JOverride, JArray
    import skyybuild as B
    _jvm_start([jar], [B.JAVASSIST])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    res = {"jar": jar, "mode": mode, "classes": len(names), "loaded": 0, "load_fails": [], "checks": [], "scen": {}, "edit": {}, "report": {}}
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
    Transform = JClass("com.hypixel.hytale.math.vector.Transform")
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

    # a bare JVM has no Item asset store (the editor's canvas handles are new ItemStack(...)): an empty one (the 0.3.12 harness pattern)
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
    JIDS = [str(x) for x in Wid.IDS]
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    plugin = U.allocateInstance(Plugin.class_)
    setf(plugin, Plugin, "huds", CHM())
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(SCRATCH, "child-" + mode)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    NEW = mode == "new"

    def uid(n):
        return UUID(0x5ce0, n)

    def pref(n, name="Steve", pos=None):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", uid(n))
        setf(pr, PRef, "username", name)
        if pos is not None:
            setf(pr, PRef, "transform", Transform(float(pos[0]), float(pos[1]), float(pos[2])))
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

    def hud(pr, join_ago_ms=None):
        h = HM(pr)
        if join_ago_ms is not None:
            h.joinMs = int(System.currentTimeMillis()) - join_ago_ms
        b = UCB()
        mBuild.invoke(h, b)
        return h, cmds(b)

    def build_again(h):
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

    def grp(cm, base):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and ("Group #%s " % base) in c[3]]
        return g[0] if len(g) == 1 else None

    def props(f):
        o = {}
        if os.path.isfile(f):
            for ln in open(f, encoding="latin-1"):
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    o[k] = v
        return o

    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()

    # ---------------- bridge fakes
    @JImplements("java.util.function.Function")
    class CombatFake(object):
        def __init__(self):
            self.left = {}
            self.window = Long(6000)
            self.calls = 0

        @JOverride
        def apply(self, x):
            if x is not None and str(x).strip().lower() == "window":
                return self.window
            self.calls += 1
            return Long(int(self.left.get(str(x), 0)))

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

    def skills_plain(u, archery=18):
        bridge.put("skill:fn:level", AnyFn())
        bridge.put("skill:" + str(u), "Mining:12,Foraging:3,Farming:1,Alchemy:2,Smithing:5,Cooking:4,Acrobatics:7,Exploration:6,Archery:%d" % archery)
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
        o = []
        d = os.path.join(LIVE, "layouts")
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".properties"):
                    o.append((f[:-11], open(os.path.join(d, f), encoding="latin-1").read()))
        return o

    def everything(me, scale=None):
        """every widget ON, styled a little, party + guild + skills + combat data (combat in combat)"""
        m = LS.get(me.getUuid())
        for w in JIDS:
            m.get(w).en = True
            if scale is not None:
                m.get(w).scale = scale
                Wid.clampToScreen(m.get(w))
        if "Skills" in JIDS:
            m.get("Skills").lines = ALL
        return m

    # ===================================================================================== S: scenarios built by both jars
    def scen(name, cm, ev=None):
        res["scen"][name] = {"cmds": cm, "evs": ev or []}

    cfn = CombatFake()
    bridge.put("skill:fn:combat", cfn)
    use_dir("s1")
    me = pref(1, pos=(123.4, 64.2, -456.7))
    scen("hud default", hud(me)[1])
    for k, (us, text) in enumerate(live_layouts()):
        d = use_dir("s2-%d" % k)
        os.makedirs(os.path.join(d, "layouts"), exist_ok=True)
        open(os.path.join(d, "layouts", us + ".properties"), "w", encoding="latin-1").write(text)
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID.fromString(us))
        setf(pr, PRef, "username", "Live%d" % k)
        setf(pr, PRef, "transform", Transform(-1500.2, 112.0, 2048.9))
        scen("hud live %d" % k, hud(pr)[1])
        scen("editor live %d" % k, *page(EP(pr, plugin)))
    use_dir("s3")
    party_guild()
    me = pref(1, pos=(-12.5, 99.9, 3456.1))
    skills_plain(me.getUuid())
    cfn.left[str(me.getUuid())] = 3500
    m = everything(me)
    pal = ["gold", "aqua", "def", "red", "lime", "def", "blue", "pink", "def", "gray", "purple", "orange"]
    for i, w in enumerate(JIDS):
        l = m.get(w)
        l.col = pal[i]
        l.glow = (i % 3 == 0)
        l.gcol = "black" if i % 2 else "def"
        l.ital = (i % 4 == 1)
        l.bold = (i % 5 != 2)
        l.scale = 50 + 13 * i
        Wid.clampToScreen(l)
    cm = hud(me)[1]
    scen("hud all styled", cm)
    m.get("Rclock").en = False
    scen("editor all styled", *page(EP(me, plugin)))
    use_dir("s4")
    clear_bridge(["party:", "guild:", "skill:fn:level", "skill:overall", "class:"])
    me = pref(1)
    scen("editor default", *page(EP(me, plugin)))
    for w in JIDS:
        if w == "Combat":
            continue
        use_dir("s5-" + w)
        scen("settings " + w, *page(SP(pref(1), plugin, w)))
    use_dir("s6")
    scen("widgets page", *page(WP(pref(1), plugin)))

    # ===================================================================================== G (both jars): editor clicks without drags
    def editor_script(tag):
        """Size / arrows / Step / Snap to on every widget (no drag): the layouts after each group (the clamps use the max box)"""
        use_dir("g-" + tag)
        me = pref(7, "Ed")
        m = LS.get(me.getUuid())
        for w in JIDS:
            m.get(w).en = True
        steps = {}
        ep = EP(me, plugin)
        page(ep)
        for w in JIDS:
            ep.handleDataEvent(None, None, '{"a":"sel:%s"}' % w)
            for act in ("Sp", "Sp", "Sp", "Lt", "Up", "Step", "Rt", "Dn", "Dn", "Sm"):
                ep.handleDataEvent(None, None, '{"a":"act:%s"}' % act)
            a = str(m.get(w).ser())
            sp = SP(me, plugin, w)
            snaps = []
            for an in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br"):
                sp.handleDataEvent(None, None, '{"a":"an:%s"}' % an)
                snaps.append(str(m.get(w).ser()))
            for sz in (50, 125, 200):
                sp.handleDataEvent(None, None, '{"a":"sz:%d"}' % sz)
                snaps.append(str(m.get(w).ser()))
            ep.handleDataEvent(None, None, '{"a":"sel:%s"}' % w)
            for i in range(60):
                ep.handleDataEvent(None, None, '{"a":"act:Rt"}')
            snaps.append(str(m.get(w).ser()))
            steps[w] = [a, snaps]
        return steps
    res["edit"] = editor_script(mode)

    # ===================================================================================== the 0.3.12 jar's own jobs
    if not NEW:
        # L: a 0.3.12 layout FILE, EXPORT CODE and PROFILE written by this jar (read by the 0.3.13 child)
        ld = use_dir("l012")
        me = pref(30, "Old", pos=(77.0, 101.0, -9.0))
        m = LS.get(me.getUuid())
        spec = {"Coords": ("tl", 0, 5, 170, False, "aqua", True, "blue"), "Zone": ("tr", 0, 0, 170, False, "blue", False, "def"),
                "Gclock": ("bl", 0, 5, 170, False, "def", False, "def"), "Rclock": ("br", 0, 439, 160, True, "def", False, "def"),
                "Day": ("tr", 0, 120, 150, False, "lime", False, "def"), "Session": ("br", 0, 0, 160, False, "red", False, "def"),
                "Online": ("t", 40, 45, 150, True, "lime", True, "black"), "Coins": ("br", 8, 633, 200, False, "gold", False, "def"),
                "Party": ("br", 418, 0, 160, False, "gold", False, "def"), "Guild": ("tl", 8, 274, 170, True, "gold", False, "def"),
                "Skills": ("r", 8, 65, 150, False, "purple", True, "black"), "Combat": ("bl", 183, 8, 180, False, "aqua", True, "black")}
        for w, (an, dx, dy, sc, bg, col, gl, gc) in spec.items():
            l = m.get(w)
            l.en = w != "Rclock"
            l.anchor, l.dx, l.dy, l.scale, l.bg, l.col, l.glow, l.gcol = an, dx, dy, sc, bg, col, gl, gc
        m.get("Skills").lines = 1023
        m.get("Combat").opt = False
        m.get("Guild").opt = False
        for w in JIDS:
            Wid.clampToScreen(m.get(w))
        LS.save(me.getUuid())
        code = str(LS.export(me.getUuid()))
        LS.profileSave(me.getUuid(), "skyy")
        pfile = os.path.join(ld, "profiles", str(me.getUuid()), "skyy.txt")
        res["l012"] = {"file": open(os.path.join(ld, "layouts", str(me.getUuid()) + ".properties"), encoding="latin-1").read(),
                       "code": code, "profile": open(pfile, encoding="utf-8").read() if os.path.isfile(pfile) else None,
                       "ser": dict((w, str(m.get(w).ser())) for w in JIDS)}
        chk(res["l012"]["profile"] is not None, "L(0.3.12): the profile file was written")
        # O: 0.3.12 reads 0.3.13 lines (rollback): the out-of-combat colour (14th field) is ignored, every other field kept
        lines = ["Combat=1,t,0,130,100,1,gold,1,0,1,def,0,-,aqua", "Coins=1,br,8,8,100,1,def,1,0,0,def,1,-,lime",
                 "Skills=1,r,8,65,150,0,purple,1,0,1,black,1,1023,aqua", "Coords=1,tr,8,8,100,1"]
        write_layout("o", uid(60), lines)
        use_dir("o")
        mo = LS.get(uid(60))
        res["old_reads_new"] = dict((w, str(mo.get(w).ser())) for w in ("Combat", "Coins", "Skills", "Coords"))
        json.dump(res, open(out, "w"), indent=1)
        return

    # ========================================================================================== the 0.3.13-only checks
    import skyyui as SUI
    LH, ASC, CAP = font_numbers()
    K_ = LH / 2 - ASC + CAP

    def kw(t, fs, bold):
        return SUI.text_width(t, fs, bold)

    # ---- T: the font table and the padding
    advb = [int(x) for x in Wid.ADVB]
    advm = [int(x) for x in Wid.ADVM]
    kb = [int(round(SUI.text_width(chr(c), 1000, True))) for c in range(32, 256)]
    km = [int(round(SUI.text_width(chr(c), 1000, False))) for c in range(32, 256)]
    chk(advb == kb and advm == km, "T: the jar's font tables (U+0020-U+00FF, 224 x 2) = the kit's text_width per glyph (%d / %d differ)"
        % (sum(1 for a, b in zip(advb, kb) if a != b), sum(1 for a, b in zip(advm, km) if a != b)))
    chk(int(Wid.ADVBX) == int(round(SUI.text_width("M", 1000, True))) and int(Wid.ADVMX) == int(round(SUI.text_width("M", 1000, False))),
        "T: any other character counts as wide as M (the kit's rule): %d / %d" % (int(Wid.ADVBX), int(Wid.ADVMX)))
    chk(abs(float(Wid.CAPK) - K_) < 1e-9 and abs(K_ - 0.376) < 1e-9, "T: CAPK %s = LH/2 - ascender + cap from the client's files (%.6f)" % (Wid.CAPK, K_))
    ptab, pmul = {}, {}
    for sc in SIZES:
        ptab[sc] = int(Wid.padSc(sc, 6))
        pmul[sc] = int(Wid.padMl(sc, 6))
        chk(ptab[sc] == pad_expected(sc) and pmul[sc] == pad_expected(sc, multi=True),
            "T: P(%d%%) = %d one-line / %d multi-line (expected %d / %d)" % (sc, ptab[sc], pmul[sc], pad_expected(sc), pad_expected(sc, multi=True)))
    res["report"]["P"] = ptab
    res["report"]["Pmulti"] = pmul
    samples = ["12:30", "--:--", "X 123  Y 64  Z -456", "Drifting Plains", "Whisperfrost Frontiers", "Your Island", "Day 42",
               "12m 34s", "1h 5m", "3 online", "Coins: 1,234,567", "In combat 6s", "Out of combat", "Overall Level", "Party (3)",
               "Jos\u00e9 \u00c5ngstr\u00f6m", "\u4e2d\u6587 name"]
    bad = []
    for t in samples:
        for fs in (6, 12, 20, 24):
            for bold in (True, False):
                want = math.ceil(kw(t, fs, bold) - 1e-9)
                got = int(Wid.textW(t, fs, bold))
                if got != want:
                    bad.append((t, fs, bold, got, want))
    chk(not bad, "T: textW = the kit's text_width rounded up for %d real texts x 4 sizes x 2 weights (bad %s)" % (len(samples), bad[:3]))
    chk(int(Wid.textWn("HP 9/100", 11, True)) == int(Wid.textW("HP 100/100", 11, True)) and
        int(Wid.textWn("HP 83/100  ST 1/10  MP 5/20", 11, True)) == int(Wid.textW("HP 100/100  ST 10/10  MP 20/20", 11, True)) and
        int(Wid.textWn("HP 120/100", 11, True)) == int(Wid.textW("HP 120/100", 11, True)),
        "T: Party stats count every current value with its max's digits ('HP 9/100' = 'HP 100/100'; above the max as it is)")

    # ---- the visible gaps of a built widget
    def gaps(id_, mk, sets_, base):
        """(W, H, left, right, top, bottom) - the box and the gaps from its edges to the letters (kit widths, client line box)"""
        r = group_rect(mk) if base.startswith("SkyyW") else None
        if base.startswith("SkyyW"):
            W, Hh = r[2], r[3]
        else:
            mr = RECT_RE.search(mk)
            W, Hh = int(mr.group(3)), int(mr.group(4))
        labs = labels_of(mk, base)
        lefts, rights, tops, bots = [], [], [], []
        for suf, (rect, fs, bold, al) in labs.items():
            t = sets_.get("#%s%sTxt.Text" % (base, suf))
            if t is None or t == "":
                continue
            x, y, w, h = rect if rect is not None else (0, 0, W, Hh)
            tw = kw(t, fs, bold)
            ix = x if al == "Start" else (x + w - tw if al == "End" else x + (w - tw) / 2.0)
            lt = y + (h - LH * fs) / 2.0
            lefts.append(ix)
            rights.append(W - (ix + tw))
            tops.append(lt + (ASC - CAP) * fs)
            bots.append(Hh - (lt + ASC * fs))
        for suf, (rect, fs, bold, al) in labs.items():
            if rect is not None:
                d = max(1, (fs * 3 + 12) // 24)
                far = (rect[0] + rect[2]) if al == "Start" else rect[0]
                if (al == "Start" and far != W - d) or (al == "End" and far != d) or rect[0] < 0 or rect[0] + rect[2] > W:
                    lefts.append(-999.0)          # a label without its slack (or outside the box) fails the gap check loudly
        bar = re.search(r"ProgressBar #%sBar \{ Anchor: \(Left: (-?\d+), Top: (-?\d+), Width: (\d+), Height: (\d+)\)" % base, mk)
        bot = min(bots) if bots else None
        if bar:
            bot = Hh - (int(bar.group(2)) + int(bar.group(4)))
        return W, Hh, (min(lefts) if lefts else None), (min(rights) if rights else None), (min(tops) if tops else None), bot

    # ---- P: every widget at every size, through the real HUD build
    use_dir("p")
    party_guild()
    pme = pref(1, "Steve", pos=(123.4, 64.2, -456.7))
    skills_plain(pme.getUuid())
    bridge.put("coins:" + str(pme.getUuid()), Long(1234567))
    pbad, pn, rep, worst = [], 0, {}, [0.0, 0.0, 0.0]
    for sc in SIZES:
        m = everything(pme, sc)
        m.get("Combat").opt = False
        for state in ("in", "out"):
            cfn.left[str(pme.getUuid())] = 4200 if state == "in" else 0
            LS.CACHE.put(pme.getUuid(), m)
            h, cm = hud(pme, join_ago_ms=754000)
            st = sets(cm)
            for w in JIDS:
                if state == "out" and w != "Combat":
                    continue
                mk = grp(cm, "SkyyW" + w)
                if mk is None:
                    pbad.append("%s %d%%: not drawn" % (w, sc))
                    continue
                W, Hh, L, R, T, Bt = gaps(w, mk, st, "SkyyW" + w)
                l = m.get(w)
                mx = int(l.bw) * sc // 100
                p = ptab[sc]
                pn += 1
                if w in ONE:
                    t = st.get("#SkyyW%sTxt.Text" % w)
                    want_w = min(mx, math.ceil(kw(t, max(6, 12 * sc // 100), True) - 1e-9) + 2 * p)
                    want_h = 26 * sc // 100
                else:
                    want_w = int(Wid.multiW(w, l, h.models.get(w), sc, 6))
                    want_h = int(Wid.bodyH(w, h.models.get(w), sc))
                    if w == "Combat" and state == "in":
                        chk(want_h == 3 * sc // 100 + 20 * sc // 100 + max(1, 6 * sc // 100) + 8 * sc // 100 and want_h <= 37 * sc // 100,
                            "P: Combat in combat at %d%% is %d high (<= the 37 x size clamp box)" % (sc, want_h))
                rx = group_rect(mk)
                if W != want_w or Hh != want_h or W > mx or not (0 <= rx[0] <= 1920 - W and 0 <= rx[1] <= 1080 - Hh):
                    pbad.append("%s %d%% %s: box %dx%d want %dx%d max %d at %s" % (w, sc, state, W, Hh, want_w, want_h, mx, rx[:2]))
                    continue
                if W < mx and None not in (L, R, T, Bt):
                    worst[0] = max(worst[0], abs(L - T))
                    worst[1] = max(worst[1], abs(R - T))
                    worst[2] = max(worst[2], abs(Bt - T))
                    if abs(L - T) > 1.0 or abs(R - T) > 1.5 or abs(Bt - T) > 2.1:
                        pbad.append("%s %d%% %s: gaps L %.2f R %.2f T %.2f B %.2f" % (w, sc, state, L, R, T, Bt))
                if sc in (50, 100, 200):
                    rep["%s %d%%%s" % (w, sc, " out" if state == "out" and w == "Combat" else "")] = [W, Hh, round(L, 1), round(R, 1),
                                                                                                    round(T, 1), round(Bt, 1)]
    chk(not pbad and pn >= 12 * len(SIZES), "P: %d widget boxes (12 widgets x %d sizes + Combat out of combat): width = text + 2P, height as "
        "before, inside the clamp box and the screen; the gap left of the text within 1 px of the gap over it, right 1.5 px (a width is "
        "rounded UP so text never clips), under the last line 2.1 px (Guild's small 0.3.12 name rows at 130-180%%): %s" % (pn, len(SIZES), pbad[:6]))
    res["report"]["boxes"] = rep
    res["report"]["worst_gap_diff"] = [round(x, 2) for x in worst]
    # the realistic in-game texts the bare JVM cannot produce (no world / universe): the same Java methods the HUD build calls
    real = {"Gclock": ["12:30", "00:00", "23:59"], "Day": ["Day 1", "Day 42", "Day 1234"], "Zone": ["Drifting Plains", "Whisperfrost Frontiers", "Hub", "Your Island"],
            "Online": ["1 online", "12 online"], "Coords": ["X 0  Y 100  Z 0", "X -12345  Y 123  Z -12345"], "Session": ["0m 5s", "59m 59s", "12h 3m"]}
    rbad, rn = [], 0
    for w, texts in real.items():
        l = wdef(w)
        for sc in SIZES:
            l.scale = sc
            for t in texts:
                for bold in (True, False):
                    l.bold = bold
                    W = int(Wid.lineW(l, t, sc, 6))
                    want = min(180 * sc // 100, math.ceil(kw(t, max(6, 12 * sc // 100), bold) - 1e-9) + 2 * ptab[sc])
                    mk = str(Wid.widgetSrcW(w, l, W))
                    rr = group_rect(mk)
                    side = (W - kw(t, max(6, 12 * sc // 100), bold)) / 2.0
                    top = (26 * sc // 100) / 2.0 - K_ * max(6, 12 * sc // 100)
                    rn += 1
                    if W != want or rr is None or rr[2] != W or rr[3] != 26 * sc // 100 or (W < 180 * sc // 100 and abs(side - top) > 1.0):
                        rbad.append((w, sc, t, bold, W, want, rr))
        l.bold = True
    chk(not rbad, "P: %d in-game texts (clock, day, zone names, online, coordinates, session) x every size x bold / plain: box = text + 2P, "
        "the side gap within 1 px of the top gap (%s)" % (rn, rbad[:3]))
    res["report"]["clock"] = dict((sc, int(Wid.lineW(wdef("Gclock"), "12:30", sc, 6))) for sc in (50, 100, 170, 200))
    typical = [("Coords", "X 123  Y 64  Z -456"), ("Zone", "Drifting Plains"), ("Gclock", "12:30"), ("Rclock", "12:30"), ("Day", "Day 42"),
               ("Session", "12m 34s"), ("Online", "3 online"), ("Coins", "Coins: 48,213")]
    res["report"]["typical"] = dict(("%s '%s'" % (w, t), [int(Wid.lineW(wdef(w), t, sc, 6)) for sc in (50, 100, 200)]) for w, t in typical)

    # ---- C: corners (the Game Clock; the Real Clock shows a real HH:MM here)
    cbad, cn = [], 0
    for w in ("Gclock", "Rclock"):
        for sc in (50, 100, 170, 200):
            for corner in ("tl", "tr", "bl", "br"):
                use_dir("c-%s-%d-%s" % (w, sc, corner))
                me = pref(50, "Cora")
                m = LS.get(me.getUuid())
                l = m.get(w)
                l.en = True
                sp = SP(me, plugin, w)
                sp.handleDataEvent(None, None, '{"a":"sz:%d"}' % sc)
                sp.handleDataEvent(None, None, '{"a":"an:%s"}' % corner)
                ep = EP(me, plugin)
                page(ep)
                ep.handleDataEvent(None, None, '{"a":"sel:%s"}' % w)
                for i in range(4):
                    ep.handleDataEvent(None, None, '{"a":"act:%s"}' % ("Lt" if corner[1] == "l" else "Rt"))
                    ep.handleDataEvent(None, None, '{"a":"act:%s"}' % ("Up" if corner[0] == "t" else "Dn"))
                h, cm = hud(me)
                mk = grp(cm, "SkyyW" + w)
                t = sets(cm).get("#SkyyW%sTxt.Text" % w)
                ma = ANC_RE.search(mk or "")
                fs = max(6, 12 * sc // 100)
                W = int(ma.group(5)) if ma else -1
                Hh = int(ma.group(6)) if ma else -1
                edge_x = (W - kw(t, fs, True)) / 2.0                       # the box sits on the screen edge: box gap = screen gap
                edge_y = (Hh / 2.0 - K_ * fs) if corner[0] == "t" else (Hh / 2.0 - (ASC - LH / 2) * fs)   # over the caps / under the baseline
                ec, ee = page(EP(me, plugin))
                pv = RECT_RE.search(grp(ec, "SkyyEPv" + w) or "")
                cn += 1
                okp = pv is not None and ((int(pv.group(1)) == 0) if corner[1] == "l" else (1278 <= int(pv.group(1)) + int(pv.group(3)) <= 1280)) \
                    and ((int(pv.group(2)) == 0) if corner[0] == "t" else (718 <= int(pv.group(2)) + int(pv.group(4)) <= 720))
                want_anchor = "(%s: 0, %s: 0, Width: %d, Height: %d)" % ("Top" if corner[0] == "t" else "Bottom", "Left" if corner[1] == "l" else "Right", W, Hh)
                if not (str(l.anchor) == corner and int(l.dx) == 0 and int(l.dy) == 0 and ma and ma.group(0) == "Anchor: " + want_anchor
                        and abs(edge_x - ptab[sc]) <= 0.5 and abs(edge_y - ptab[sc]) <= 1.5 and okp and W == int(Wid.lineW(l, t, sc, 6))):
                    cbad.append((w, sc, corner, str(l.ser()), ma.group(0) if ma else None, round(edge_x, 2), round(edge_y, 2), pv.group(0) if pv else None))
                # a drag from the opposite corner into this corner's cell: the drawn box lands in the corner's anchor within one
                # cell (exactly 0 when the move overshoots), then Step 25 arrows take it to x = y = 0
                opp = {"tl": "br", "tr": "bl", "bl": "tr", "br": "tl"}[corner]
                sp.handleDataEvent(None, None, '{"a":"an:%s"}' % opp)
                ep = EP(me, plugin)
                page(ep)
                cells = [i for i, x in enumerate(list(ep.cellWidget)) if x is not None and str(x) == w]
                target = {"tl": 0, "tr": 31, "bl": 544, "br": 575}[corner]
                if len(cells) == 1:
                    ep.handleDataEvent(None, None, '{"a":"drop","SourceSlotId":%d,"SlotIndex":%d}' % (cells[0], target))
                after_drag = (str(l.anchor), int(l.dx), int(l.dy))
                ep.handleDataEvent(None, None, '{"a":"act:Step"}')
                ep.handleDataEvent(None, None, '{"a":"act:Step"}')
                for i in range(10):
                    ep.handleDataEvent(None, None, '{"a":"act:%s"}' % ("Lt" if corner[1] == "l" else "Rt"))
                    ep.handleDataEvent(None, None, '{"a":"act:%s"}' % ("Up" if corner[0] == "t" else "Dn"))
                if not (len(cells) == 1 and after_drag[0] == corner and str(l.anchor) == corner and int(l.dx) == 0 and int(l.dy) == 0):
                    cbad.append((w, sc, corner, "drag", after_drag, str(l.ser()), cells))
    chk(not cbad and cn == 32, "C: the Game Clock and the Real Clock reach all 4 corners at 50 / 100 / 170 / 200%% (Snap to + arrows, and a drag "
        "past the corner): anchor = corner, x = y = 0, HUD anchor (Top|Bottom: 0, Left|Right: 0), text P px from both screen edges, "
        "the editor preview in the canvas corner (%d cases): %s" % (cn, cbad[:3]))

    # ---- K: the two Combat colours end to end
    use_dir("k")
    bridge.clear()
    bridge.put("skill:fn:combat", cfn)
    me = pref(70, "Kai")
    u = str(me.getUuid())
    fk = os.path.join(work, "k", "layouts", u + ".properties")
    l = lay(me, "Combat")
    chk(str(l.ocol) == "def" and str(l.ser()) == "1,t,0,130,100,1", "K: a new player's Combat = Default / Default, the 6-field line (%s)" % l.ser())
    scm, sce = page(SP(me, plugin, "Combat"))
    tc = [c[3] for c in scm if c[0] == "AppendInline" and c[3] and "TextButton #SkyySetTc" in c[3]]
    oc = [c[3] for c in scm if c[0] == "AppendInline" and c[3] and "TextButton #SkyySetOc" in c[3]]
    rowlab = [c[3] for c in scm if c[0] == "AppendInline" and c[1] in ("#SkyySetRowCol", "#SkyySetRowOc") and c[3] and "Width: 200, Height: 44" in c[3]]
    chk(len(tc) == 13 and len(oc) == 13, "K: the Combat Settings page has 13 In combat + 13 Out of combat swatches (%d / %d)" % (len(tc), len(oc)))
    chk(any('Text: \\"In combat\\"' in x or 'Text: "In combat"' in x for x in rowlab) and any('Out of combat' in x for x in rowlab),
        "K: the rows are labelled In combat / Out of combat: %s" % [re.search(r'Text: \\?"([^"\\]*)', x).group(1) for x in rowlab])
    d_tc = [x for x in tc if "#SkyySetTcDef " in x]
    d_oc = [x for x in oc if "#SkyySetOcDef " in x]
    chk(d_tc and "Background: %s" % RED in d_tc[0] and d_oc and "Background: %s" % GREY in d_oc[0],
        "K: the Default swatches show what Default means: red in combat, grey out of combat")
    ring = [c[3] for c in scm if c[0] == "AppendInline" and c[1] in ("#SkyySetRowCol", "#SkyySetRowOc") and c[3] and c[3].startswith("Group { Anchor: (Width: 84, Height: 44); Background: #ffffff;")]
    chk(len(ring) == 2 and "#SkyySetTcDef " in ring[0] and "#SkyySetOcDef " in ring[1], "K: Default / Default ringed on a new layout")
    ocev = sorted(e[2] for e in sce if e[1] and e[1].startswith("#SkyySetOc"))
    chk(len(ocev) == 13 and all('"ocol:' in x for x in ocev), "K: 13 ocol:<key> bindings (%s ...)" % ocev[:2])
    rows = [c for c in scm if c[0] == "AppendInline" and c[1] == "#SkyySet"]
    tot = 0
    for c in rows:
        mm = re.match(r"\s*(?:Group|Label|TextButton)(?:\s+#[A-Za-z0-9]+)?\s*\{\s*Anchor: \(([^)]*)\)", c[3])
        hv = re.search(r"Height: (\d+)", mm.group(1)) if mm else None
        tot += int(hv.group(1)) if hv else 100000
    root = [c[3] for c in scm if c[0] == "AppendInline" and c[1] is None and c[3].startswith("Group #SkyySet {")]
    chk(root and "Height: 924" in root[0] and tot == 882 and tot + 20 <= 924, "K: the Combat page is 1500 x 924 with %d px of rows + 20 padding" % tot)
    pvs = sets(scm)
    chk(pvs.get("#SkyySetPvATxt.Text") == "In combat 4s" and pvs.get("#SkyySetPvCTxt.Text") == "Out of combat"
        and pvs.get("#SkyySetPvBTxt.Text") == "In combat 4s" and pvs.get("#SkyySetPvDTxt.Text") == "Out of combat",
        "K: the two preview rows show In combat 4s / Out of combat (dark + bright)")
    # click the colours
    sp = SP(me, plugin, "Combat")
    sp.handleDataEvent(None, None, '{"a":"col:gold"}')
    sp.handleDataEvent(None, None, '{"a":"ocol:aqua"}')
    fl = props(fk)
    chk(fl.get("Combat") == "1,t,0,130,100,1,gold,1,0,0,def,1,-,aqua", "K: the file line carries both colours: %s" % fl.get("Combat"))
    LS.CACHE.clear()
    l = lay(me, "Combat")
    chk(str(l.col) == "gold" and str(l.ocol) == "aqua" and str(l.ser()) == "1,t,0,130,100,1,gold,1,0,0,def,1,-,aqua",
        "K: reloaded from the file: in combat gold, out of combat aqua")
    cfn.left[u] = 3000
    h, cm = hud(me)
    mk = grp(cm, "SkyyWCombat")
    chk(mk is not None and "TextColor: #ffaa00" in mk and "#55ffff" not in mk and "ProgressBar" in mk, "K: in combat the HUD draws gold (the in-combat colour)")
    l.opt = False
    cfn.left[u] = 0
    h, cm = hud(me)
    mk = grp(cm, "SkyyWCombat")
    chk(mk is not None and "TextColor: #55ffff" in mk and "#ffaa00" not in mk and "ProgressBar" not in mk and str(h.shape.get("Combat")) == "CO",
        "K: out of combat (Show) the HUD draws aqua (the out-of-combat colour)")
    l.glow = True
    h, cm = hud(me)
    mk = grp(cm, "SkyyWCombat") or ""
    chk("TextColor: #55ffff(0.45)" in mk, "K: glow Same follows the out-of-combat colour")
    l.gcol = "black"
    h, cm = hud(me)
    mk = grp(cm, "SkyyWCombat") or ""
    chk("TextColor: #000000(0.45)" in mk and "TextColor: #55ffff" in mk, "K: glow Black out of combat")
    l.ocol = "def"
    h, cm = hud(me)
    mk = grp(cm, "SkyyWCombat") or ""
    chk("TextColor: %s" % GREY in mk and "TextColor: %s" % GREYG in mk and "#000000(0.45)" not in mk,
        "K: Default out of combat = 0.3.12's grey text + quiet grey glow (the glow colour ignored, as 0.3.12)")
    l.ocol = "aqua"
    l.glow = False
    l.gcol = "def"
    l.opt = True
    ep = EP(me, plugin)
    ec, ee = page(ep)
    pv = grp(ec, "SkyyEPvCombat") or ""
    chk("TextColor: #ffaa00" in pv and "ProgressBar #SkyyEPvCombatBar" in pv, "K: the editor sample (hidden widget) uses the in-combat colour")
    l.opt = False
    ec, ee = page(EP(me, plugin))
    pv = grp(ec, "SkyyEPvCombat") or ""
    chk("TextColor: #55ffff" in pv and sets(ec).get("#SkyyEPvCombatN0Txt.Text") == "Out of combat", "K: the editor shows the real out-of-combat line in aqua")
    scm, sce = page(SP(me, plugin, "Combat"))
    pa, pc = grp(scm, "SkyySetPvA") or "", grp(scm, "SkyySetPvC") or ""
    chk("TextColor: #ffaa00" in pa and "TextColor: #55ffff" in pc, "K: the Settings previews: In combat gold, Out of combat aqua")
    ring = [c[3] for c in scm if c[0] == "AppendInline" and c[1] in ("#SkyySetRowCol", "#SkyySetRowOc") and c[3] and c[3].startswith("Group { Anchor: (Width: 84, Height: 44); Background: #ffffff;")]
    chk(len(ring) == 2 and "#SkyySetTcGold " in ring[0] and "#SkyySetOcAqua " in ring[1], "K: gold and aqua are the ringed swatches")
    hint = sets(scm)
    chk(hint.get("#SkyySetPvHintA.Text") == "in combat - on dark and on bright scenery" and hint.get("#SkyySetPvHintB.Text", "").startswith("out of combat"),
        "K: the preview hints: %s / %s" % (hint.get("#SkyySetPvHintA.Text"), hint.get("#SkyySetPvHintB.Text")))
    # export / import / profile / server default
    code = str(LS.export(me.getUuid()))
    chk("Combat=1:t:0:130:100:1:gold:1:0:0:def:0:-:aqua" in code, "K: the export code carries the out-of-combat colour: %s" % code[-48:])
    other = pref(71, "Ola")
    n = int(LS.importCode(other.getUuid(), code))
    lo = lay(other, "Combat")
    chk(n == 12 and str(lo.col) == "gold" and str(lo.ocol) == "aqua" and int(lo.bh) == 37 and int(lo.bw) == 180,
        "K: import on another player: both colours, the 180 x 37 clamp box (%d parts)" % n)
    chk(bool(LS.profileSave(me.getUuid(), "cols")), "K: profile save")
    l.ocol = "def"
    l.col = "def"
    chk(int(LS.profileLoad(me.getUuid(), "cols")) == 12 and str(lay(me, "Combat").ocol) == "aqua" and str(lay(me, "Combat").col) == "gold",
        "K: profile load brings both colours back")
    Cfg.DEFAULT_LAYOUT = "Combat=1:t:0:130:100:1:def:1:0:0:def:1:-:lime"
    Cfg.PARSED = None
    nw = pref(72, "Nia")
    ln_ = lay(nw, "Combat")
    chk(str(ln_.ocol) == "lime" and str(ln_.col) == "def", "K: a server default layout with an out-of-combat colour reaches a new player")
    chk(Cfg.checkLayout("hud.defaultLayout", "Combat=1:t:0:130:100:1:def:1:0:0:def:1:-:lime") is None, "K: the admin check accepts such a code")
    Cfg.DEFAULT_LAYOUT = ""
    Cfg.PARSED = None
    # Reset style, forged payloads
    sp = SP(me, plugin, "Combat")
    sp.handleDataEvent(None, None, '{"a":"rstyle"}')
    lr = lay(me, "Combat")
    chk(str(lr.col) == "def" and str(lr.ocol) == "def", "K: Reset style puts both colours back to Default")
    sp.handleDataEvent(None, None, '{"a":"ocol:black"}')
    sp.handleDataEvent(None, None, '{"a":"ocol:nope"}')
    chk(str(lay(me, "Combat").ocol) == "def", "K: ocol:black (glow-only) and ocol:nope are refused")
    before = props(fk)
    SP(me, plugin, "Coins").handleDataEvent(None, None, '{"a":"ocol:aqua"}')
    chk(str(lay(me, "Coins").ocol) == "def" and props(fk) == before, "K: a forged ocol on another widget's page changes and saves nothing")
    sp.handleDataEvent(None, None, '{"a":"ocol:pink"}')
    chk(props(fk).get("Combat", "").endswith(",-,pink") and str(lay(me, "Combat").ocol) == "pink", "K: ocol:pink saved: %s" % props(fk).get("Combat"))

    # ---- L: the 0.3.12 jar's file / code / profile in 0.3.13
    l012 = json.load(open(os.path.join(SCRATCH, "child-old.json"))).get("l012") if os.path.isfile(os.path.join(SCRATCH, "child-old.json")) else None
    if l012:
        lu = str(uid(30))
        d = use_dir("l")
        os.makedirs(os.path.join(d, "layouts"), exist_ok=True)
        open(os.path.join(d, "layouts", lu + ".properties"), "w", encoding="latin-1").write(l012["file"])
        pdir = os.path.join(d, "profiles", lu)
        os.makedirs(pdir, exist_ok=True)
        open(os.path.join(pdir, "skyy.txt"), "w", encoding="utf-8").write(l012["profile"])
        me = pref(30, "Old", pos=(77.0, 101.0, -9.0))
        mf = LS.get(me.getUuid())
        got = dict((w, str(mf.get(w).ser())) for w in JIDS)
        chk(got == l012["ser"], "L: the 0.3.12 FILE loads with identical lines for all 12 widgets: %s" % [w for w in JIDS if got[w] != l012["ser"][w]])
        h, cm = hud(me)
        chk(all(grp(cm, "SkyyW" + w) is not None for w in ONE if w != "Rclock"), "L: the HUD builds every enabled one-line widget")
        other = pref(31, "Imp")
        n = int(LS.importCode(other.getUuid(), l012["code"]))
        mi = LS.get(other.getUuid())
        got2 = dict((w, str(mi.get(w).ser())) for w in JIDS)
        chk(n == 12 and got2 == l012["ser"], "L: the 0.3.12 EXPORT CODE imports with identical lines (%d parts; differ %s)" % (n, [w for w in JIDS if got2[w] != l012["ser"][w]]))
        LS.reset(me.getUuid())
        n = int(LS.profileLoad(me.getUuid(), "skyy"))
        got3 = dict((w, str(LS.get(me.getUuid()).get(w).ser())) for w in JIDS)
        chk(n == 12 and got3 == l012["ser"], "L: the 0.3.12 PROFILE loads with identical lines")
        LS.save(me.getUuid())
        chk(props(os.path.join(d, "layouts", lu + ".properties")) == dict((w, l012["ser"][w]) for w in JIDS),
            "L: saving it again writes the 0.3.12 lines byte for byte (no 14th field, nothing re-clamped)")
        res["report"]["l012_code"] = l012["code"]
    else:
        chk(False, "L: the 0.3.12 child's files are missing")

    # ---- W: the width follows the text (grow now, shrink after 15 s)
    use_dir("w")
    bridge.clear()
    me = pref(80, "Wes", pos=(5.0, 64.0, 5.0))
    m = LS.get(me.getUuid())
    for w in JIDS:
        m.get(w).en = w in ("Coins", "Coords", "Rclock")
    bridge.put("coins:" + str(me.getUuid()), Long(5))
    h, cm = hud(me)
    w0 = int(h.wb.get("Coins"))
    chk(w0 == int(Wid.lineW(m.get("Coins"), "Coins: 5", 100, 6)) and int(h.wb.get("Rclock")) == int(Wid.lineW(m.get("Rclock"), "12:30", 100, 6)),
        "W: the HUD remembers the widths it sent (Coins %d, Rclock = an HH:MM box)" % w0)
    b0 = UCB()
    chk(not bool(h.fill(b0, False)) and not [c for c in cmds(b0) if "Coins" in str(c[1])], "W: nothing changed -> no re-send, no Coins command")
    bridge.put("coins:" + str(me.getUuid()), Long(5000000))
    b1 = UCB()
    chk(bool(h.fill(b1, False)) and sets(cmds(b1)).get("#SkyyWCoinsTxt.Text") == "Coins: 5,000,000", "W: a longer text asks for the re-send at once (and sets the text)")
    cm2 = build_again(h)
    w1 = int(h.wb.get("Coins"))
    chk(w1 == int(Wid.lineW(m.get("Coins"), "Coins: 5,000,000", 100, 6)) and w1 > w0 and ("Width: %d" % w1) in (grp(cm2, "SkyyWCoins") or ""),
        "W: the re-send draws the wider box (%d -> %d)" % (w0, w1))
    bridge.put("coins:" + str(me.getUuid()), Long(7))
    b2 = UCB()
    chk(not bool(h.fill(b2, False)) and h.narrow.get("Coins") is not None, "W: a shorter text does NOT re-send at once (the timer starts)")
    h.narrow.put("Coins", Long(int(System.currentTimeMillis()) - 14000))
    chk(not bool(h.fill(UCB(), False)), "W: 14 s later still no re-send")
    h.narrow.put("Coins", Long(int(System.currentTimeMillis()) - 15500))
    chk(bool(h.fill(UCB(), False)), "W: after 15 s the shrink re-send is asked")
    build_again(h)
    chk(int(h.wb.get("Coins")) == int(Wid.lineW(m.get("Coins"), "Coins: 7", 100, 6)) and h.narrow.get("Coins") is None, "W: the re-send shrinks the box")
    bridge.put("coins:" + str(me.getUuid()), Long(9))
    b3 = UCB()
    chk(not bool(h.fill(b3, False)) and sets(cmds(b3)).get("#SkyyWCoinsTxt.Text") == "Coins: 9" and h.narrow.get("Coins") is None,
        "W: the same width -> just the text (Coins: 9, tabular digits)")
    # coordinates: a sign / a digit
    setf(me, PRef, "transform", Transform(-5.0, 64.0, 5.0))
    chk(bool(h.fill(UCB(), False)), "W: X 5 -> X -5 needs a minus: re-send")
    build_again(h)
    setf(me, PRef, "transform", Transform(-6.0, 63.0, 4.0))
    chk(not bool(h.fill(UCB(), False)), "W: X -6  Y 63  Z 4 fits the same box: no re-send")
    # the clock never re-sends (tabular digits), 60 ticks
    flips = 0
    for i in range(60):
        if bool(h.fill(UCB(), False)):
            flips += 1
    chk(flips == 0, "W: 60 ticks with nothing moving: 0 re-sends (%d)" % flips)
    # multi-line: Skills 9 -> 10, Party HP swings
    use_dir("w2")
    bridge.clear()
    party_guild()
    me = pref(1, "Steve")
    skills_plain(me.getUuid(), archery=9)
    m = LS.get(me.getUuid())
    for w in JIDS:
        m.get(w).en = w in ("Skills", "Party")
    h, cm = hud(me)
    sw0 = int(h.wb.get("Skills"))
    bridge.put("skill:overall:" + str(me.getUuid()), Integer(9))
    h.fill(UCB(), False)
    h.narrow.clear()
    build_again(h)
    sw0 = int(h.wb.get("Skills"))
    bridge.put("skill:overall:" + str(me.getUuid()), Integer(10))
    b4 = UCB()
    chk(bool(h.fill(b4, False)) and sets(cmds(b4)).get("#SkyyWSkillsS0Txt.Text") == "10", "W: Skills Overall Level 9 -> 10 (the widest line) grows the box (re-send asked)")
    build_again(h)
    chk(int(h.wb.get("Skills")) > sw0, "W: ... and the re-send is wider (%d -> %d)" % (sw0, int(h.wb.get("Skills"))))
    pw0 = int(h.wb.get("Party"))
    swing = 0
    for hp in (20, 9, 1, 15, 20, 3):
        bridge.put("party:stats:" + str(uid(1)), "%d,20,9,10,0,0,world-a" % hp)
        if bool(h.fill(UCB(), False)):
            swing += 1
    chk(swing == 0 and int(h.wb.get("Party")) == pw0, "W: Party HP 20 -> 9 -> 1 -> 15 -> 20 -> 3 never resizes the box (%d re-sends)" % swing)

    # ---- E: the editor uses the drawn box; the HUD lands where the editor draws it
    ebad, en_ = [], 0
    use_dir("e")
    bridge.clear()
    bridge.put("skill:fn:combat", cfn)
    party_guild()
    me = pref(1, "Steve", pos=(10.0, 70.0, 10.0))
    skills_plain(me.getUuid())
    cfn.left[str(me.getUuid())] = 2500
    for sc in (50, 100, 200):
        for an in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br"):
            m = everything(me, sc)
            for w in JIDS:
                Wid.snapTo(m.get(w), an)
            h, cm = hud(me)
            ep = EP(me, plugin)
            ec, ee = page(ep)
            for w in JIDS:
                l = m.get(w)
                mk = grp(cm, "SkyyW" + w)
                r = group_rect(mk)
                ws, hs = int(ep.widthOf(w, l)), int(ep.heightOf(w, l))
                pos = list(Wid.screenPosWH(l, ws, hs))
                pv = RECT_RE.search(grp(ec, "SkyyEPv" + w) or "")
                en_ += 1
                if r is None or [r[0], r[1]] != pos or r[2] != ws or r[3] != hs or pv is None:
                    ebad.append((w, sc, an, r, pos, ws, hs))
                    continue
                left, top, cw, ch = (int(pv.group(i)) for i in (1, 2, 3, 4))
                if w in ONE:
                    okx = cw == ws * 2 // 3 and abs(left - min(pos[0] * 2 // 3, 1280 - cw)) <= 0
                else:
                    if an in ("tr", "r", "br"):
                        wl = (pos[0] + ws) * 2 // 3 - cw
                    elif an in ("t", "c", "b"):
                        wl = (2 * pos[0] + ws) // 3 - cw // 2
                    else:
                        wl = pos[0] * 2 // 3
                    okx = cw == int(Wid.multiW(w, l, ep.pm.get(w), sc * 2 // 3, 5)) and left == max(0, min(wl, 1280 - cw))
                cell = int(Wid.cellOfWH(l, ws, hs))
                centred = w not in ONE or left in (0, 1280 - cw) or abs((left + cw / 2.0) * 1.5 - (pos[0] + ws / 2.0)) <= 2
                if not okx or not centred or cell != min(31, max(0, (pos[0] + ws // 2) // 60)) + 32 * min(17, max(0, (pos[1] + hs // 2) // 60)):
                    ebad.append((w, sc, an, "preview", left, cw, pos, ws))
    chk(not ebad and en_ == 12 * 27, "E: %d HUD boxes (12 widgets x 9 anchors x 50/100/200%%): the HUD anchor lands on the editor's screen position of the "
        "drawn box, the 2/3 preview sits on it (multi-line by the anchored edge), the handle cell under its centre: %s" % (en_, ebad[:3]))
    # a drag drops the DRAWN box where it was dropped (nearest corner by the drawn centre, clamped)
    use_dir("e2")
    dbad = []
    me = pref(1, "Steve", pos=(10.0, 70.0, 10.0))
    m = LS.get(me.getUuid())
    for w in JIDS:
        m.get(w).en = True
    for w in JIDS:
        ep = EP(me, plugin)
        page(ep)
        l = m.get(w)
        cells = [i for i, x in enumerate(list(ep.cellWidget)) if x is not None and str(x) == w]
        if len(cells) != 1:
            dbad.append((w, "no handle"))
            continue
        ws, hs = int(ep.widthOf(w, l)), int(ep.heightOf(w, l))
        p0 = list(Wid.screenPosWH(l, ws, hs))
        frm = cells[0]
        to = (frm % 32 + (4 if frm % 32 < 27 else -4)) + 32 * (frm // 32 + (3 if frm // 32 < 14 else -3))
        ep.handleDataEvent(None, None, '{"a":"drop","SourceSlotId":%d,"SlotIndex":%d}' % (frm, to))
        dx_, dy_ = (to % 32 - frm % 32) * 60, (to // 32 - frm // 32) * 60
        want = [min(max(p0[0] + dx_, 0), 1920 - ws), min(max(p0[1] + dy_, 0), 1080 - hs)]
        got = list(Wid.screenPosWH(l, ws, hs))
        corner = ("t" if want[1] + hs // 2 < 540 else "b") + ("l" if want[0] + ws // 2 < 960 else "r")
        if got != want or str(l.anchor) != corner:
            dbad.append((w, p0, want, got, str(l.anchor), corner))
    chk(not dbad, "E: a drag moves every widget's drawn box by the dragged cells (clamped), nearest corner by the drawn centre: %s" % dbad[:3])

    # ---- X: Combat regression (the light per-tick update)
    use_dir("x")
    bridge.clear()
    bridge.put("skill:fn:combat", cfn)
    me = pref(90, "Xi")
    u = str(me.getUuid())
    cfn.left[u] = 5400
    m = LS.get(me.getUuid())
    for w in JIDS:
        m.get(w).en = w == "Combat"
    h, cm = hud(me)
    chk(str(h.shape.get("Combat")) == "CI" and vsets(cm, "#SkyyWCombatBar.Value") and sets(cm).get("#SkyyWCombatS0Txt.Text") == "6s",
        "X: in combat the HUD draws In combat / 6s and sets the bar")
    seq = []
    for left in (4400, 3400, 2400, 1400, 400):
        cfn.left[u] = left
        b = UCB()
        re_ = bool(h.fill(b, False))
        cc = [c for c in cmds(b) if c[1] and "Combat" in c[1]]
        seq.append((re_, len(cc), sets(cmds(b)).get("#SkyyWCombatS0Txt.Text")))
    chk(seq == [(False, 2, "5s"), (False, 2, "4s"), (False, 2, "3s"), (False, 2, "2s"), (False, 2, "1s")],
        "X: each tick = the countdown text + the bar Value, never a re-send (the width does not move): %s" % seq)
    cfn.left[u] = 0
    chk(bool(h.fill(UCB(), False)), "X: leaving combat asks for the shape re-send")

    # ---- H: start twice on a scratch COPY of the live data
    if os.path.isdir(LIVE):
        import time
        mods = os.path.join(work, "live")
        shutil.copytree(LIVE, os.path.join(mods, "Skyy_SkyyHud"))
        hdir = os.path.join(mods, "Skyy_SkyyHud")
        Pub = JClass(PKG + "CfgPub")

        def tree():
            o = {}
            for dp, dn, fn in os.walk(mods):
                for f in fn:
                    p = os.path.join(dp, f)
                    o[os.path.relpath(p, mods)] = (open(p, "rb").read(), os.path.getmtime(p))
                for dn_ in dn:
                    o[os.path.relpath(os.path.join(dp, dn_), mods) + os.sep] = None
            return o

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
            bridge.put("skill:fn:combat", cfn)
            for k, us in enumerate(players):
                pr = U.allocateInstance(PRef.class_)
                setf(pr, PRef, "uuid", UUID.fromString(us))
                setf(pr, PRef, "username", "Live%d" % k)
                setf(pr, PRef, "transform", Transform(-1500.2, 112.0, 2048.9))
                skills_plain(pr.getUuid())
                bridge.put("coins:" + us, Long(48213))
                cfn.left[us] = 4200 if in_combat else 0
                mp = LS.get(pr.getUuid())
                r[us] = dict((w, str(mp.get(w).ser())) for w in JIDS)
                h, cm = hud(pr, join_ago_ms=754000)
                r[us + " boxes"] = dict((w, group_rect(grp(cm, "SkyyW" + w))) for w in JIDS if grp(cm, "SkyyW" + w))
                page(EP(pr, plugin))
                page(SP(pr, plugin, "Combat"))
                page(SP(pr, plugin, "Gclock"))
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
            chk(all(r1[us][w] == fl[w] for w in JIDS if w in fl), "H: %s...: every saved widget loads exactly as saved" % us[:8])
        time.sleep(1.1)
        r2 = start(False)
        t2 = tree()
        chk(r2 == r1 and t2 == t1, "H: start 2: same layouts and boxes, no file churn")
        time.sleep(1.1)
        r3 = start(True)
        t3 = tree()
        chk(t3 == t2, "H: start 3 with everybody in combat writes nothing either")
        res["live_players"] = len(players)
        res["report"]["live_new"] = dict((us, r1[us + " boxes"]) for us in players)
        res["report"]["live_new_combat"] = dict((us, r3[us + " boxes"].get("Combat")) for us in players)
    else:
        res["live_players"] = -1
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the old jar's live boxes (report)
def run_oldlive(jar, out):
    """the live layouts' boxes in 0.3.12 (only for the before / after report)"""
    from jpype import JClass
    import skyybuild as B
    _jvm_start([jar])
    UUID, Paths, Long = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Transform = JClass("com.hypixel.hytale.math.vector.Transform")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    LS, HM, Cfg = JClass(PKG + "LayoutStore"), JClass(PKG + "HudMain"), JClass(PKG + "HudCfg")
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    work = os.path.join(SCRATCH, "child-oldlive")
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(LIVE, os.path.join(work, "Skyy_SkyyHud"))
    LS.DIR = Paths.get(os.path.join(work, "Skyy_SkyyHud", "layouts"))
    Cfg.FILE = Paths.get(os.path.join(work, "cfg.properties"))
    Cfg.load()
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn0(object):
        @JOverride
        def apply(self, x):
            return Long(6000) if x is not None and str(x) == "window" else Long(0)
    bridge.put("skill:fn:combat", Fn0())
    bridge.put("skill:fn:level", Fn0())
    bridge.put("class:list", "Archer,Warrior,Mage")
    res = {}
    for f in sorted(os.listdir(os.path.join(work, "Skyy_SkyyHud", "layouts"))):
        if not f.endswith(".properties"):
            continue
        us = f[:-11]
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID.fromString(us))
        setf(pr, PRef, "username", "Live")
        setf(pr, PRef, "transform", Transform(-1500.2, 112.0, 2048.9))
        bridge.put("coins:" + us, Long(48213))
        bridge.put("skill:" + us, "Mining:12,Foraging:3,Farming:1,Alchemy:2,Smithing:5,Cooking:4,Acrobatics:7,Exploration:6,Archery:18")
        bridge.put("skill:overall:" + us, JClass("java.lang.Integer")(7))
        bridge.put("class:skill:" + us, "Archery")
        h = HM(pr)
        b = UCB()
        mBuild.invoke(h, b)
        cm = [str(c.text) for c in b.getCommands() if c.text is not None]
        res[us] = {}
        for w in IDS:
            g = [t for t in cm if ("Group #SkyyW%s " % w) in t]
            if g:
                res[us][w] = group_rect(g[0])
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
                  and all((x or "").replace(old_version, "V") == (y or "").replace(new_version, "V") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: engine-access audit (section Z)
def run_audit(jar, out):
    import skyybuild as B
    from jpype import JClass, JArray
    hcls = os.path.join(SCRATCH, "audit-classes")
    shutil.rmtree(hcls, ignore_errors=True)
    os.makedirs(hcls)
    _jvm_start([jar], [B.JAVASSIST])
    CPc = JClass("javassist.ClassPool")
    CtNewMethod = JClass("javassist.CtNewMethod")
    Cls = JClass("java.lang.Class")
    ldr = JClass("java.lang.ClassLoader").getSystemClassLoader()
    # helpers compiled by javassist: a privateLookupIn (the JVM's own access rules for a lookup class) and the control BadCaller
    hp = CPc(True)
    hp.appendClassPath(B.SERVER_JAR)
    hp.appendClassPath(jar)
    li = hp.makeClass("skyyhudharness.LookupIn")
    li.addMethod(CtNewMethod.make("public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {"
                                  " return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup()); }", li))
    li.writeFile(hcls)
    bc = hp.makeClass("skyyhudharness.BadCaller")
    bc.addMethod(CtNewMethod.make("public static void poke(com.skyy.hud.HudMain h) { h.onRemove(); }", bc))
    bc.writeFile(hcls)
    URL, File, URLCL = JClass("java.net.URL"), JClass("java.io.File"), JClass("java.net.URLClassLoader")
    ua = JArray(URL)(1)
    ua[0] = File(hcls).toURI().toURL()
    hl = URLCL(ua, ldr)
    LIN = JClass("skyyhudharness.LookupIn", loader=hl)
    MTc = JClass("java.lang.invoke.MethodType")
    CPool = JClass("javassist.bytecode.ConstPool")
    JMod_ = JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}
    cs = {"n": 0}

    def audit(cn, ld, pool):
        def jvm_class(name):
            return Cls.forName(name.replace("/", "."), False, ld)
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
                C_ = None
                name = desc = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", ld).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, ld)
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
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb9, 0xb8) and C_ is not None:
                        try:
                            m_ = C_.getMethod(name, MTc.fromMethodDescriptorString(desc, ld).parameterArray())
                            if JMod_.isPublic(int(m_.getModifiers())) and JMod_.isPublic(int(m_.getDeclaringClass().getModifiers())):
                                cs["n"] += 1
                                continue
                        except Exception:
                            pass
                    refused.append("%s: %s" % (where, ex_))
        return refused, n

    xp = CPc(False)
    xp.appendSystemPath()
    xp.appendClassPath(B.SERVER_JAR)
    xp.appendClassPath(jar)
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    refused, total = [], 0
    for cn in sorted(names):
        r_, n_ = audit(cn, ldr, xp)
        refused += r_
        total += n_
    xb = CPc(False)
    xb.appendSystemPath()
    xb.appendClassPath(B.SERVER_JAR)
    xb.appendClassPath(jar)
    xb.appendClassPath(hcls)
    br_, bn_ = audit("skyyhudharness.BadCaller", hl, xb)
    ran = None
    try:
        JClass("skyyhudharness.BadCaller", loader=hl).poke(None)
        ran = "ran"
    except Exception as e:
        ran = "%s %s" % (e.__class__.__name__, str(e)[:160])
    json.dump({"classes": len(names), "refs": total, "refused": refused, "caller_sensitive": cs["n"], "control_refused": br_,
               "control_run": ran}, open(out, "w"), indent=1)


# ============================================================================================ parent
CLOCK_RE = re.compile(r'^\{"0": "(\d\d:\d\d|\d+m \d+s|\d+h \d+m)"\}$')


def norm(cm, editor=False):
    """geometry-free form of a command list: every number inside an Anchor (...) becomes N; the wall-clock texts a token; editors
    without the cell-dependent parts (the handle slots, the displaced-handle markers)"""
    out = []
    for c in cm:
        t, sel, data, text = c
        if editor and ((sel or "").startswith("#SkyyEMk") or "#SkyyEMk" in (text or "") or sel == "#SkyyECanvas.Slots"):
            continue
        if text:
            text = re.sub(r"Anchor: \([^)]*\)", lambda m: re.sub(r"-?\d+", "N", m.group(0)), text)
        if t == "Set" and data and CLOCK_RE.match(data):
            data = '{"0": "CLOCK"}'
        out.append([t, sel, data, text])
    return out


def main():
    if "--run" in sys.argv:
        run_child(arg("--run"), arg("--out"), arg("--mode"))
        return
    if "--oldlive" in sys.argv:
        run_oldlive(arg("--oldlive"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"), arg("--ov"), arg("--nv"))
        return
    if "--audit" in sys.argv:
        run_audit(arg("--audit"), arg("--out"))
        return
    for j in (JAR, OLD_JAR):
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
    common = ["--dir", SCRATCH, "--live", LIVE]
    outs = {}
    for tag, j in (("old", OLD_JAR), ("new", JAR)):      # old first: it writes the 0.3.12 file / code / profile the new child loads
        outs[tag] = os.path.join(SCRATCH, "child-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--run", j, "--out", outs[tag], "--mode", tag] + common, env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "child JVM for %s (%s) ran (exit %s)" % (os.path.basename(j), tag, p.returncode))
    olo = os.path.join(SCRATCH, "oldlive.json")
    if os.path.isdir(LIVE):
        subprocess.run([sys.executable, me, "--oldlive", OLD_JAR, "--out", olo] + common, env=env)
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
    auo = os.path.join(SCRATCH, "audit.json")
    p = subprocess.run([sys.executable, me, "--audit", JAR, "--out", auo] + common, env=env)
    check(p.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran")
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
    nb = 0
    for ok, what in new["checks"] + old["checks"]:
        check(ok, what)
        nb += 1
    print("T-X, H. %d checks in the child JVMs (%d failed); live copy players: %s" % (nb, sum(1 for ok, w in new["checks"] + old["checks"] if not ok),
                                                                                    new.get("live_players")))
    if not os.path.isdir(LIVE):
        SKIPS.append("H (start twice on a copy of the live data): no live Skyy_SkyyHud folder at %s" % LIVE)
    else:
        check(new.get("live_players", -1) >= 1, "H: the live Skyy_SkyyHud folder was copied and holds at least one layout (%s)" % LIVE)
    # S: 0.3.12 vs 0.3.13 output, geometry normalised
    ns = 0
    for name in sorted(old["scen"]):
        o, n = old["scen"][name], new["scen"].get(name)
        if n is None:
            check(False, "S: scenario %s missing in 0.3.13" % name)
            continue
        ed = name.startswith("editor")
        fo, fn_ = norm(o["cmds"], ed), norm(n["cmds"], ed)
        same = fo == fn_
        if not same:
            for i, (a, b) in enumerate(zip(fo, fn_)):
                if a != b:
                    print("   first difference in %s at %d:\n     0.3.12 %s\n     0.3.13 %s" % (name, i, str(a)[:400], str(b)[:400]))
                    break
        check(same, "S: %s: 0.3.13 = 0.3.12 apart from the box geometry (%d / %d commands)" % (name, len(o["cmds"]), len(n["cmds"])))
        check(o["evs"] == n["evs"], "S: %s: event bindings identical (%d / %d)" % (name, len(o["evs"]), len(n["evs"])))
        ns += 1
    check(ns >= 16, "S: every scenario compared (%d)" % ns)
    print("S. %d scenarios: 0.3.12 output = 0.3.13 output once the Anchor numbers are normalised" % ns)
    # G: Size / arrows / Snap to give the same layouts (the clamps keep the maximum box)
    ge = 0
    for w in IDS:
        a, b = old["edit"].get(w), new["edit"].get(w)
        check(a == b and a is not None, "G: %s: Size / arrows / Step / Snap to / sizes give the same layout in both jars: %s / %s" % (w, a, b))
        ge += 1
    print("G. editor clicks without drags on %d widgets: identical layouts in 0.3.12 and 0.3.13" % ge)
    # O: 0.3.12 reads 0.3.13 lines
    orn = old.get("old_reads_new") or {}
    check(orn == {"Combat": "1,t,0,130,100,1,gold,1,0,1,def,0", "Coins": "1,br,8,8,100,1", "Skills": "1,r,8,65,150,0,purple,1,0,1,black,1,1023",
                  "Coords": "1,tr,8,8,100,1"},
          "O: 0.3.12 reads 0.3.13 lines (rollback): every field but the out-of-combat colour kept: %s" % orn)
    # Z
    au = json.load(open(auo))
    check(not au["refused"] and au["refs"] > 1000, "Z: all %d references in the %d classes of the 0.3.13 jar pass MethodHandles.Lookup in their "
          "own class (the JVM's access rules): refused %s" % (au["refs"], au["classes"], au["refused"][:4]))
    check(len(au["control_refused"]) == 1 and "onRemove" in au["control_refused"][0], "Z: control: a class calling the protected "
          "CustomUIHud.onRemove from outside is refused by the audit: %s" % au["control_refused"])
    check("IllegalAccessError" in (au["control_run"] or ""), "Z: control: running it throws IllegalAccessError (%s)" % au["control_run"])
    print("Z. engine-access audit: %d references in %d classes, 0 refused (%d caller-sensitive JDK calls checked as public members); "
          "control refused + %s" % (au["refs"], au["classes"], au["caller_sensitive"], (au["control_run"] or "")[:40]))
    # F1: class bytes
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "F1: same entries in both jars")
    diff = sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    want_diff = sorted(["manifest.json"] + ["com/skyy/hud/%s.class" % c for c in (
        "WLayout", "Widgets", "HudMain", "EditorPage", "SettingsPage", "SkyyHudPlugin", "CfgFn", "CfgRows")])
    check(diff == want_diff, "F1: exactly these entries differ: %s (got %s)" % (want_diff, diff))
    bc = json.load(open(bco))
    expect = {
        "WLayout": ({"WLayout", "ser", "parse"}, set(), set()),
        "Widgets": ({"def", "bodyH", "partyBody", "guildBody", "skillsBody", "combatColor", "combatGlow", "combatBody", "multiBody",
                     "anchorSrcH", "screenPosH", "setTopLeftH", "cornerAtH", "cellOfH", "moveByCellsH", "<clinit>"},
                    {"advOf", "advMilli", "pxOf", "textW", "textWn", "fsOf", "padOf", "padSc", "padMl", "capW", "lineW", "innerW", "multiW",
                     "anchorSrcWH", "lineS", "lineE", "multiWidgetSrcW", "widgetSrcW", "screenPosWH", "setTopLeftWH", "cornerAtWH", "cellOfWH",
                     "moveByCellsWH", "viewW"}, {"multiWidgetSrc", "widgetSrc"}),
        "HudMain": ({"HudMain", "fill", "build"}, {"widthMoved"}, set()),
        "EditorPage": ({"prepView", "widgetAtCell", "appendPreviews", "build", "handleDataEvent"}, {"widthOf"}, set()),
        "SettingsPage": ({"swatch", "build", "handleDataEvent"}, {"swatchHex", "<clinit>"}, set()),
        "SkyyHudPlugin": ({"setup"}, set(), set()),
    }
    for cname, (chg, nw, gone) in expect.items():
        r = bc.get("com/skyy/hud/%s.class" % cname, {})
        got_c = set(k.split("(")[0] for k in r.get("changed", []))
        got_n = set(k.split("(")[0] for k in r.get("new", []))
        got_g = set(k.split("(")[0] for k in r.get("gone", []))
        # a changed signature shows as gone + new of the same name (the bodies / multiBody gained the box width)
        both = got_n & got_g
        got_c, got_n, got_g = got_c | both, got_n - both, got_g - both
        check(got_c == chg and got_n == nw and got_g == gone, "F1: %s: changed %s new %s gone %s (got %s / %s / %s)"
              % (cname, sorted(chg), sorted(nw), sorted(gone), sorted(got_c), sorted(got_n), sorted(got_g)))
    wd = bc.get("com/skyy/hud/Widgets.class", {})
    check(wd.get("fields_new") == sorted(["ADVB [I", "ADVBX I", "ADVM [I", "ADVMX I", "CAPK D", "SHRINK J"]) and not wd.get("fields_gone"),
          "F1: Widgets gains the font table, CAPK, SHRINK: %s" % wd.get("fields_new"))
    check(bc.get("com/skyy/hud/WLayout.class", {}).get("fields_new") == ["ocol Ljava/lang/String;"], "F1: WLayout gains ocol")
    check(sorted(bc.get("com/skyy/hud/HudMain.class", {}).get("fields_new", [])) == sorted(["narrow Ljava/util/concurrent/ConcurrentHashMap;",
          "texts Ljava/util/concurrent/ConcurrentHashMap;", "wb Ljava/util/concurrent/ConcurrentHashMap;"]), "F1: HudMain gains texts, wb, narrow")
    check(sorted(bc.get("com/skyy/hud/EditorPage.class", {}).get("fields_new", [])) == sorted(["pt Ljava/util/HashMap;", "ww Ljava/util/HashMap;"]),
          "F1: EditorPage gains ww, pt")
    check(sorted(bc.get("com/skyy/hud/SettingsPage.class", {}).get("fields_new", [])) == sorted(["CSW [Ljava/lang/String;", "OSW [Ljava/lang/String;"]),
          "F1: SettingsPage gains CSW, OSW")
    check(bc.get("com/skyy/hud/SkyyHudPlugin.class", {}).get("version_only"), "F1: SkyyHudPlugin.setup differs only by the version in the ready line")
    for cname in ("CfgFn", "CfgRows"):
        r = bc.get("com/skyy/hud/%s.class" % cname, {})
        check(r.get("version_only") and not r.get("new") and not r.get("gone"), "F1: %s differs only by the version string" % cname)
    print("F1. class bytes: %d entries identical; differ: %s" % (len(set(zo.namelist()) & set(zn.namelist())) - len(diff),
                                                              ", ".join(x.split("/")[-1] for x in diff)))
    # F2: rebuild 0.3.12 with today's tools
    if "--no-rebuild" not in sys.argv:
        rb = os.path.join(SCRATCH, "rebuild012")
        os.makedirs(rb)
        for f in ("build_skyyhud_0.3.12.py", "icon-256.png", "skyyhud_dot.png"):
            shutil.copy2(os.path.join(HERE, f), os.path.join(rb, f))
        env2 = dict(env)
        env2["PYTHONPATH"] = TOOLS
        env2["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        p = subprocess.run([sys.executable, "build_skyyhud_0.3.12.py"], cwd=rb, env=env2, capture_output=True, text=True)
        rjar = os.path.join(rb, "SkyyHud-0.3.12.jar")
        check(p.returncode == 0 and "assembled" in p.stdout and os.path.isfile(rjar), "F2: 0.3.12 rebuilds in scratch: %s" % (p.stdout[-200:] + p.stderr[-300:]))
        if os.path.isfile(rjar):
            hud_cls = [n for n in zo.namelist() if n.endswith(".class") and not n.split("/")[-1].startswith("Cfg")]
            with zipfile.ZipFile(rjar) as zr:
                same = [n for n in hud_cls if zo.read(n) == zr.read(n)]
            check(len(same) == len(hud_cls), "F2: the rebuilt 0.3.12's HUD classes equal the 0.3.12 jar's (%d / %d; differ %s)"
                  % (len(same), len(hud_cls), sorted(set(hud_cls) - set(same))))
            bc2 = os.path.join(SCRATCH, "bytecode-kit.json")
            subprocess.run([sys.executable, me, "--bytecode", rjar, "--new", JAR, "--out", bc2, "--ov", OLD_VERSION, "--nv", VERSION] + common, env=env)
            r2 = json.load(open(bc2)) if os.path.isfile(bc2) else {}
            kit = dict((k, v) for k, v in r2.items() if k.split("/")[-1].startswith("Cfg"))
            bad = [k.split("/")[-1] for k, v in kit.items() if not v["version_only"] or v["new"] or v["gone"] or not v["fields_same"]]
            check(not bad, "F2: config kit classes rebuilt-0.3.12 vs 0.3.13 differ only by the version string: %s" % bad)
            print("F2. 0.3.12 rebuilt in scratch: HUD classes reproducible (%d / %d); kit vs 0.3.13: %s" % (len(same), len(hud_cls), "version only" if not bad else bad))
    # the report: boxes before / after
    rep = new.get("report", {})
    print("P(size): %s" % rep.get("P"))
    print("Game Clock '12:30' box width at 50/100/170/200%%: %s (0.3.12: 90 / 180 / 306 / 360)" % rep.get("clock"))
    print("one-line widgets with in-game texts, width at 50 / 100 / 200% (0.3.12: 90 / 180 / 360; heights 13 / 26 / 52 unchanged):")
    for k, v in sorted(rep.get("typical", {}).items()):
        print("  %-32s %s" % (k, v))
    print("worst gap differences (left / right / bottom vs the gap over the text): %s px" % rep.get("worst_gap_diff"))
    boxes = rep.get("boxes", {})
    for sc in (50, 100, 200):
        print("  %d%%: " % sc + "; ".join("%s %dx%d" % (k.split(" ")[0] + (" out" if k.endswith("out") else ""), v[0], v[1])
                                         for k, v in sorted(boxes.items()) if (" %d%%" % sc) in k))
    if os.path.isfile(olo):
        oldlive = json.load(open(olo))
        for us, ob in oldlive.items():
            nbx = rep.get("live_new", {}).get(us, {})
            print("  live %s...: " % us[:8] + "; ".join("%s %s->%s" % (w, "%dx%d" % tuple(ob[w][2:]) if ob.get(w) else "-",
                                                                      "%dx%d" % tuple(nbx[w][2:]) if nbx.get(w) else "-") for w in IDS if ob.get(w) or nbx.get(w)))
    json.dump(rep, open(os.path.join(SCRATCH, "report.json"), "w"), indent=1)
    if KEEP:
        print("report:", os.path.join(SCRATCH, "report.json"))
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
