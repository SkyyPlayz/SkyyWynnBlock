"""SkyyHud 0.3.18 - harness for the ABILITIES widget (tools/hud_0_3_18_patch.py; research/cloud/Ability-Engine-Plan.md round R2).

    python SkyyHud/test_skyyhud_0.3.18.py [--jar <SkyyHud-0.3.18.jar>] [--old <SkyyHud-0.3.17.jar>] [--old2 <SkyyHud-0.3.15.jar>]
                                          [--live <Skyy_SkyyHud folder>] [--dir <scratch>] [--keep]

Build the jar first (python SkyyHud/build_skyyhud_0.3.18.py). Every JVM is a fresh child (the game's own JRE, -Xverify:all, -XX:-UsePerfData,
java.io.tmpdir + TEMP/TMP in the scratch folder). The bridge Function class:fn:abil is a plain fake with the SkyyClasses 0.1.17 contract
(tools/classes_0_1_17_patch.py); the REAL SkyyClasses 0.1.17 AbilFn + world-thread sample feeding this widget is executed by
SkyyClasses/test_skyyclasses_0.1.17.py section H (the same Widgets.abilModelU on the real bridge).
  A  every class of the 0.3.18 jar loads + initializes under -Xverify:all
  W  THE WIDGET through the REAL HudMain.build / fill / the 1 s tick path, per ability state: READY (cost, widget colour, icon), COOLDOWN
     (countdown + the vanilla ProgressBar Value, a shape re-send when it starts / ends, then only text + Value sets each tick),
     UNAFFORDABLE (grey + the cost you lack), LOCKED (grey "Lv 10"), CROUCH (the rows swap to the two alts - a shape re-send), creative
     "Free", PASSIVE / SOON / an empty slot; SkyyClasses 0.1.16's 16-field answer ("Ready" / "Locked", no icons); NO class:fn:abil or a
     classless player = no widget on the HUD; the editor + Settings stand-in ("Needs SkyyClasses 0.1.17" / the Mage sample); the Settings
     page's Icons Show / Hide row (FIX ROUND: Hide = opt true = the DEFAULT; Show = optoff -> the saved layout line); hide / show, size 50-200 %, Snap to, export /
     import code, profile save / load like every widget; old 0.3.17 layout files / codes load unchanged (the new id appended); the
     Combat widget's bar is set exactly as in 0.3.17 (Widgets.barPairs)
  J  the jar files: 0.3.17's entries + exactly the 10 Mage / Priest icons at Common/UI/Custom/SkyyHud/Abil/<Id>.png, byte-identical to
     art/ability-icons; 64 x 64 PNGs; no .ui file
  F  class compare 0.3.17 -> 0.3.18: only Widgets, HudMain, SettingsPage (+ the kit's version text) differ; no class added or removed
  R  REGRESSION: the whole 0.3.16 harness re-run on the 0.3.18 jar (minimap repro, placement, kit rows, START TWICE ON A SCRATCH COPY OF THE
     LIVE DATA - nothing written -, the engine-access audit); its own class-compare line (written for 0.3.15 -> 0.3.16) is the only check
     allowed to differ, and only by HudMain / SettingsPage (section F checks the classes)
  V  THE ENGINE ASSET VALIDATORS (the 0.3.17 V child: real asset stores, the vanilla pack, then the jar as its own pack): no failed store,
     not one SEVERE / WARNING line for the jar, the 11 common assets registered (dot.png + 10 icons), P0 no one-entry Parallel; the
     negative control (a one-entry Parallel MUST be refused)
Not testable without the game (UNVERIFIED): a PACK picture in a HUD Group Background (the vanilla textures resolve the same way; the
Settings row "Icons Hide" is the fallback), how the rows look, the crouch swap feel (1 s tick + the 1.5 s re-send limit).
Default scratch folder: tools/dev/scratch/abil02/hud (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION, OLD2_VERSION = "0.3.18", "0.3.17", "0.3.15"
PKG = "com.skyy.hud."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
ICON_SRC = os.path.join(ROOT, "art", "ability-icons", "Common", "Icons", "Abilities")
ICONS = [("Mage", "Meteor"), ("Mage", "ManaBarrier"), ("Mage", "FrostNova"), ("Mage", "Starfall"), ("Mage", "ArcaneBeam"),
         ("Priest", "SacredHeal"), ("Priest", "ShieldBubble"), ("Priest", "GuardianSpirit"), ("Priest", "Sanctuary"), ("Priest", "MartyrsGrace")]
GREY, RED = "#8b949e", "#ff6b6b"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "abil02", "hud"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % OLD_VERSION)))
OLD2_JAR = os.path.abspath(arg("--old2", os.path.join(HERE, "SkyyHud-%s.jar" % OLD2_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyHud")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def js(v):
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


# ======================================================================================================== child: A + W
def run_w(out):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST], convertStrings=True)
    res = {"checks": [], "notes": []}

    def chk(cond, what):
        res["checks"].append([bool(cond), what])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    fails = []
    for n in names:
        try:
            Cls.forName(n, True, loader)
        except Exception as e:
            fails.append("%s: %s" % (n, str(e)[:200]))
    chk(not fails, "A. all %d classes of the %s jar load + initialize under -Xverify:all: %s" % (len(names), VERSION, fails[:3]))
    UUID, System, CHM = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths, Long, Integer, Double, Boolean, String = (JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Integer"),
                                                     JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.String"))
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    # a bare JVM has no Item asset store (the editor's canvas handles): an empty one (the 0.3.12 / 0.3.13 harness pattern)
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
    WL, Wid, LS, HM, EP, SP, Cfg, Plugin = (H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("EditorPage"), H("SettingsPage"),
                                           H("HudCfg"), H("SkyyHudPlugin"))
    JIDS = [str(x) for x in Wid.IDS]
    plugin = U.allocateInstance(Plugin.class_)
    setf(plugin, Plugin, "huds", CHM())
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(SCRATCH, "child-w")
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
        return [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data)] for e in ev.getEvents()]

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

    def page(p):
        b, ev = UCB(), UEB()
        p.build(None, b, ev, None)
        return cmds(b), evs(ev)

    def sets(cm):
        return dict((c[1], js(c[2])) for c in cm if c[0] == "Set" and c[1] and c[1].endswith(".Text"))

    def vsets(cm, sel):
        return [jv(c[2]) for c in cm if c[0] == "Set" and c[1] == sel]

    def grp(cm, base):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and ("Group #%s " % base) in c[3]]
        return g[0] if len(g) == 1 else None
    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()

    # ---------------- the class:fn:abil fake (the SkyyClasses 0.1.17 contract, tools/classes_0_1_17_patch.py)
    @JImplements("java.util.function.Function")
    class AbilFake(object):
        def __init__(self):
            self.p = {}
            self.calls = 0

        def set(self, u, **kw):
            d = {"names": ["Meteor", "Mana Barrier", "Frost Nova", "Starfall"], "ids": ["Meteor", "ManaBarrier", "FrostNova", "Starfall"],
                 "left": [0, 0, 0, 0], "total": [0, 0, 0, 0], "state": ["ready", "ready", "locked", "locked"], "mana": [23.0, 16.0, 19.0, 28.0],
                 "stam": [2.0, 1.0, 1.0, 2.0], "afford": [True, True, None, None], "crouch": False, "cls": "Mage", "now": [145.0, 14.5],
                 "free": False, "unlock": [1, 10, 20, 30], "old16": False, "none": False}
            d.update(kw)
            self.p[str(u)] = d

        @JOverride
        def apply(self, x):
            self.calls += 1
            d = self.p.get(str(x))
            if d is None or d["none"]:
                return None
            a = [None] * (16 if d["old16"] else 44)
            for i in range(4):
                a[i * 4] = String(d["names"][i])
                a[i * 4 + 1] = Long(d["left"][i])
                a[i * 4 + 2] = Long(d["total"][i])
                a[i * 4 + 3] = String(d["state"][i])
                if not d["old16"]:
                    a[16 + i] = String(d["ids"][i])
                    a[20 + i] = Double(d["mana"][i])
                    a[24 + i] = Double(d["stam"][i])
                    a[28 + i] = None if d["afford"][i] is None else Boolean(d["afford"][i])
                    a[38 + i] = Long(d["unlock"][i])
            if not d["old16"]:
                a[32] = Boolean(d["crouch"])
                a[33] = String(d["cls"])
                a[34] = Double(d["now"][0])
                a[35] = Double(d["now"][1])
                a[36] = Boolean(d["free"])
                a[37] = String("abil2")
                a[42] = Long(100)
            return JArray(JObject)(a)

    afn = AbilFake()
    me = pref(1, "Mia")
    u = me.getUuid()
    use_dir("w1")
    # ---- W0: no SkyyClasses -> no widget on the HUD; the editor / Settings stand-in
    h, cm = hud(me)
    l = LS.get(u).get("Abilities")
    chk(JIDS[-1] == "Abilities" and JIDS[:-1] == ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild",
                                                  "Skills", "Combat", "Minimap", "Seasons"],
        "W0: Abilities is APPENDED to Widgets.IDS (old layout files / export codes keep their meaning)")
    chk(l is not None and bool(l.en) and str(l.anchor) == "tl" and int(l.dx) == 8 and int(l.dy) == 760 and int(l.bw) == 220 and int(l.bh) == 59
        and int(l.scale) == 100 and bool(l.opt), "W0: a new player's Abilities = ON, tl 8,760, box 220 x 59 at 100 %%, opt true (= Icons Hide, FIX ROUND): %s" % (l.ser() if l else None))
    chk(grp(cm, "SkyyWAbilities") is None and str(h.shape.get("Abilities")) == "A0", "W0: no class:fn:abil (SkyyClasses missing) -> nothing on the HUD (shape A0)")
    sm = [None if x is None else str(x) for x in Wid.abilSample(True)]
    chk(sm[2] == "Needs SkyyClasses 0.1.17" and sm[1] == "Needs SkyyClasses 0.1.17", "W0: the editor / Settings stand-in says 'Needs SkyyClasses 0.1.17'")
    ecm, eev = page(EP(me, plugin))
    pv = grp(ecm, "SkyyEPvAbilities") or ""
    chk("SkyyEPvAbilitiesN0" in pv and sets(ecm).get("#SkyyEPvAbilitiesN0Txt.Text") == "Needs SkyyClasses 0.1.17", "W0: the editor previews the hidden widget with that line")
    bridge.put("class:fn:abil", afn)
    # ---- FIX W1: the DEFAULT is Icons Hide (a pack picture in a HUD is UNVERIFIED - AGENT-BRIEF: trial features stay off until Skyy saw them)
    afn.set(u)
    h0, cm0 = hud(me)
    mk0 = grp(cm0, "SkyyWAbilities") or ""
    chk(str(h0.shape.get("Abilities")) == "Ap0|-n|-n" and "SkyyHud/Abil/" not in mk0 and "SkyyWAbilitiesI0" not in mk0 and "SkyyWAbilitiesN0" in mk0
        and Wid.sampleU("Abilities", "Mia", True)[6] is None and bool(LS.get(u).get("Abilities").opt),
        "FIX W1: a new player's Abilities widget shows NAMES ONLY by default (no pack picture), the editor sample too: %s" % h0.shape.get("Abilities"))
    smp_on = [None if x is None else str(x) for x in Wid.sampleU("Abilities", "Mia", False)]
    chk(smp_on[6] == "SkyyHud/Abil/Meteor.png" and smp_on[11] == "SkyyHud/Abil/ManaBarrier.png", "FIX W1: the editor / Settings sample with Icons Show (opt false) has the pictures: %s" % smp_on[6:12])
    LS.get(u).get("Abilities").opt = False   # Icons Show for the rest of W1-W7 (the picture checks)
    # ---- W1: READY
    h, cm = hud(me)
    mk = grp(cm, "SkyyWAbilities") or ""
    st = sets(cm)
    chk(str(h.shape.get("Abilities")) == "Ap1|-nSkyyHud/Abil/Meteor.png|-nSkyyHud/Abil/ManaBarrier.png", "W1: READY shape: %s" % h.shape.get("Abilities"))
    chk(re.search(r"Group #SkyyWAbilities \{ Anchor: \(Top: 760, Left: 8, Width: \d+, Height: 59\);", mk) is not None
        and 'Group #SkyyWAbilitiesI0 { Anchor: (Left: ' in mk and 'Background: "SkyyHud/Abil/Meteor.png"; }' in mk
        and 'Background: "SkyyHud/Abil/ManaBarrier.png"; }' in mk and "ProgressBar" not in mk and GREY not in mk,
        "W1: the widget box at tl 8,760, 59 high, the two icons (the shipped pictures), no bar, nothing grey: %s" % mk[:200])
    chk(st.get("#SkyyWAbilitiesN0Txt.Text") == "Meteor" and st.get("#SkyyWAbilitiesS0Txt.Text") == "23 Mana + 2 Stam"
        and st.get("#SkyyWAbilitiesN1Txt.Text") == "Mana Barrier" and st.get("#SkyyWAbilitiesS1Txt.Text") == "16 Mana + 1 Stam",
        "W1 (FIX2: both costs): the first fill sets 'Meteor  23 Mana + 2 Stam' / 'Mana Barrier  16 Mana + 1 Stam': %s" % dict((k, v) for k, v in st.items() if "Abilities" in k))
    w_ready = int(re.search(r"Group #SkyyWAbilities \{ Anchor: \(Top: 760, Left: 8, Width: (\d+)", mk).group(1)) if mk else 0
    chk(0 < w_ready <= 220, "W1: the box is as wide as its widest row + the icon column (%d px, at most 220)" % w_ready)
    # ---- W2: COOLDOWN starts -> a shape re-send; then each tick only the countdown + the bar Value
    afn.set(u, left=[14000, 0, 0, 0], total=[14000, 0, 0, 0], state=["cooldown", "ready", "locked", "locked"])
    b = UCB()
    re1 = bool(h.fill(b, False))
    chk(re1, "W2: a cast (cooldown starts) changes the shape -> the HUD asks for the re-send")
    cm = cmds(UCB())
    b = UCB()
    mBuild.invoke(h, b)
    cm = cmds(b)
    mk = grp(cm, "SkyyWAbilities") or ""
    chk("ProgressBar #SkyyWAbilitiesBar0" in mk and "ProgressBar #SkyyWAbilitiesBar1" not in mk and "Common/ProgressBar.png" in mk
        and "EffectTexturePath" not in mk and vsets(cm, "#SkyyWAbilitiesBar0.Value") == [1.0] and sets(cm).get("#SkyyWAbilitiesS0Txt.Text") == "14s",
        "W2: re-built: the vanilla ProgressBar under Meteor (Value 1.0), '14s': %s" % vsets(cm, "#SkyyWAbilitiesBar0.Value"))
    seq = []
    for left in (13000, 12000, 11500, 2000, 400):
        afn.set(u, left=[left, 0, 0, 0], total=[14000, 0, 0, 0], state=["cooldown", "ready", "locked", "locked"])
        b = UCB()
        re_ = bool(h.fill(b, False))
        cc = [c for c in cmds(b) if c[1] and "Abilities" in c[1]]
        seq.append((re_, len(cc), sets(cmds(b)).get("#SkyyWAbilitiesS0Txt.Text"), (vsets(cmds(b), "#SkyyWAbilitiesBar0.Value") or [None])[0]))
    chk([x[0] for x in seq] == [False] * 5 and [x[2] for x in seq] == ["13s", "12s", None, "2s", "1s"]
        and all(x[3] is not None for x in seq) and [x[1] for x in seq] == [2, 2, 1, 2, 2],
        "W2: each tick = the countdown text (only when the second changes) + the bar Value, never a re-send: %s" % seq)
    afn.set(u)
    chk(bool(h.fill(UCB(), False)), "W2: the cooldown ends -> the shape changes back (re-send), the cost shows again")
    # ---- W3: UNAFFORDABLE (grey + the cost you lack); W4 LOCKED; W5 CROUCH; W6 creative / passive / soon / empty
    def built(**kw):
        afn.set(u, **kw)
        b_ = UCB()
        mBuild.invoke(h, b_)
        c_ = cmds(b_)
        return str(h.shape.get("Abilities")), grp(c_, "SkyyWAbilities") or "", sets(c_)
    sh, mk, st = built(afford=[False, True, None, None], now=[20.0, 14.5])
    n0 = re.search(r'Label #SkyyWAbilitiesN0Txt \{[^}]*TextColor: (#[0-9a-f]{6})', mk)
    n1 = re.search(r'Label #SkyyWAbilitiesN1Txt \{[^}]*TextColor: (#[0-9a-f]{6})', mk)
    chk(sh.startswith("Ap1|-g") and n0 is not None and n0.group(1) == GREY and n1 is not None and n1.group(1) != GREY
        and st.get("#SkyyWAbilitiesS0Txt.Text") == "23 Mana + 2 Stam", "W3: UNAFFORDABLE (20 Mana): Meteor GREY with '23 Mana + 2 Stam', Mana Barrier in the widget colour: %s" % sh)
    sh, mk, st = built(afford=[True, False, None, None], now=[145.0, 0.5])
    chk(st.get("#SkyyWAbilitiesS1Txt.Text") == "16 Mana + 1 Stam" and "|-gSkyyHud/Abil/ManaBarrier.png" in sh, "W3 (FIX2): short of Stamina only -> grey with the whole cost '16 Mana + 1 Stam'")
    sh, mk, st = built(afford=[True, False, None, None], now=[18.0, 14.5])
    chk(st.get("#SkyyWAbilitiesS1Txt.Text") == "16 Mana + 1 Stam" and "|-gSkyyHud/Abil/ManaBarrier.png" in sh,
        "FIX W3: not affordable with enough of both costs (Mana Barrier's Mana kept: 18 < 16 + 4) -> grey with the whole cost: %s" % st.get("#SkyyWAbilitiesS1Txt.Text"))
    sh, mk, st = built(state=["ready", "locked", "locked", "locked"], afford=[True, None, None, None])
    chk(st.get("#SkyyWAbilitiesS1Txt.Text") == "Lv 10" and "|-gSkyyHud/Abil/ManaBarrier.png" in sh, "W4: LOCKED -> 'Mana Barrier  Lv 10' grey")
    sh, mk, st = built(crouch=True)
    chk(sh == "Aa1|-gSkyyHud/Abil/FrostNova.png|-gSkyyHud/Abil/Starfall.png" and st.get("#SkyyWAbilitiesN0Txt.Text") == "Frost Nova"
        and st.get("#SkyyWAbilitiesS0Txt.Text") == "Lv 20" and st.get("#SkyyWAbilitiesN1Txt.Text") == "Starfall" and st.get("#SkyyWAbilitiesS1Txt.Text") == "Lv 30",
        "W5: CROUCHING -> the rows swap to the two alts (Frost Nova Lv 20, Starfall Lv 30, grey): %s" % sh)
    afn.set(u, crouch=True, state=["ready", "ready", "ready", "ready"], afford=[True, True, True, True])
    re_c = bool(h.fill(UCB(), False))
    afn.set(u, crouch=False)
    re_s = bool(h.fill(UCB(), False))
    chk(re_c and re_s, "W5: crouch on / off between ticks -> a shape re-send each way")
    sh, mk, st = built(free=True)
    chk(st.get("#SkyyWAbilitiesS0Txt.Text") == "Free" and st.get("#SkyyWAbilitiesS1Txt.Text") == "Free", "W6: creative + free -> 'Free'")
    sh, mk, st = built(names=["Sacred Heal", "Shield Bubble", "Guardian Spirit", ""], ids=["SacredHeal", "ShieldBubble", "GuardianSpirit", ""],
                       state=["ready", "soon", "passive", "empty"], mana=[18.0, 20.0, 0.0, 0.0], stam=[2.0, 2.0, 0.0, 0.0], afford=[True, None, None, None], cls="Priest")
    chk(st.get("#SkyyWAbilitiesS0Txt.Text") == "18 Mana + 2 Stam" and st.get("#SkyyWAbilitiesS1Txt.Text") == "Soon" and "|-gSkyyHud/Abil/ShieldBubble.png" in sh
        and 'Background: "SkyyHud/Abil/SacredHeal.png"' in mk, "W6: a Priest: Sacred Heal with its icon, a SOON row grey")
    sh, mk, st = built(names=["Sacred Heal", "Shield Bubble", "Guardian Spirit", ""], ids=["SacredHeal", "ShieldBubble", "GuardianSpirit", ""],
                       state=["ready", "ready", "passive", "empty"], crouch=True, cls="Priest")
    chk(st.get("#SkyyWAbilitiesN0Txt.Text") == "Guardian Spirit" and st.get("#SkyyWAbilitiesS0Txt.Text") == "Passive"
        and st.get("#SkyyWAbilitiesN1Txt.Text") == "-" and st.get("#SkyyWAbilitiesS1Txt.Text") == "" and sh.startswith("Aa1|-nSkyyHud/Abil/GuardianSpirit.png|-g"),
        "W6: crouching Priest: 'Guardian Spirit  Passive' (not grey), an empty alt slot '-' grey without an icon: %s" % sh)
    # ---- W7: SkyyClasses 0.1.16 (16 fields), no class, the bridge gone again
    sh, mk, st = built(old16=True, state=["ready", "locked", "locked", "locked"])
    chk(sh == "Ap0|-n|-g" and st.get("#SkyyWAbilitiesS0Txt.Text") == "Ready" and st.get("#SkyyWAbilitiesS1Txt.Text") == "Locked" and "Background:" not in mk.split("TextColor")[0][200:],
        "W7: SkyyClasses 0.1.16's 16-field answer -> 'Meteor Ready', 'Mana Barrier Locked', no icons: %s" % sh)
    sh, mk, st = built(none=True)
    chk(sh == "A0" and mk == "", "W7: a player without a class with abilities (null) -> no widget")
    built()
    bridge.remove("class:fn:abil")
    chk(bool(h.fill(UCB(), False)), "W7: SkyyClasses gone -> the widget hides (shape re-send)")
    bridge.put("class:fn:abil", afn)
    # ---- W8: Settings page (Icons Show / Hide) -> the saved line; editor; Combat unchanged
    sp = SP(me, plugin, "Abilities")
    scm, sce = page(sp)
    lab = [c[3] for c in scm if c[0] == "AppendInline" and c[3] and "Icons" in c[3]]
    on_ev = [e for e in sce if e[1] == "#SkyySetOptOn" and "opton" in (e[2] or "")]
    off_ev = [e for e in sce if e[1] == "#SkyySetOptOff" and "optoff" in (e[2] or "")]
    chk(lab and on_ev and off_ev and any('Text: "Show"' in c[3] for c in scm if c[0] == "AppendInline" and c[3] and "SkyySetOptOff" in c[3])
        and any('Text: "Hide"' in c[3] for c in scm if c[0] == "AppendInline" and c[3] and "SkyySetOptOn" in c[3]),
        "W8: the Abilities Settings page has the 'Icons  Show / Hide' row (FIX ROUND: Show = optoff, Hide = opton = the default)")
    sp.handleDataEvent(None, None, '{"a":"opton"}')
    LS.CACHE.clear()
    l2 = LS.get(u).get("Abilities")
    fl = dict(x.split("=", 1) for x in open(os.path.join(work, "w1", "layouts", str(u) + ".properties"), encoding="latin-1").read().splitlines() if "=" in x and not x.startswith("#"))
    chk(bool(l2.opt) and fl.get("Abilities", "").split(",")[:5] == ["1", "tl", "8", "760", "100"], "W8: Hide -> saved (the layout line): %s" % fl.get("Abilities"))
    sh, mk, st = built()
    chk(sh == "Ap0|-n|-n" and "Background:" not in re.sub(r"Group #SkyyWAbilities \{ Anchor: [^;]*; (Background: #0b1524\(0\.72\); )?", "", mk),
        "W8: Icons Hide -> names only on the HUD: %s" % sh)
    sp.handleDataEvent(None, None, '{"a":"optoff"}')
    LS.CACHE.clear()
    chk(not bool(LS.get(u).get("Abilities").opt), "W8: Show -> the icons back on (opt false)")
    ecm, eev = page(EP(me, plugin))
    pv = grp(ecm, "SkyyEPvAbilities") or ""
    chk("SkyyEPvAbilitiesI0" in pv and sets(ecm).get("#SkyyEPvAbilitiesN0Txt.Text") == "Meteor", "W8: the editor previews the real rows (icons included) at 2/3 size")
    # sizes, export / import, snap
    l = LS.get(u).get("Abilities")
    hs = []
    for sc in (50, 75, 100, 150, 200):
        l.scale = sc
        Wid.clampToScreen(l)
        b = UCB()
        mBuild.invoke(h, b)
        g = grp(cmds(b), "SkyyWAbilities") or ""
        m_ = re.search(r"Width: (\d+), Height: (\d+)\);", g)
        hs.append((sc, int(m_.group(2)) if m_ else None, int(m_.group(1)) if m_ else None))
    l.scale = 100
    chk([x[1] for x in hs] == [29, 43, 59, 88, 118] and all(x[2] and x[2] <= 220 * x[0] // 100 for x in hs),
        "W8: sizes 50-200 %%: the height = 3 + 2 x (20 + 4) + 2 + 6 at each size (each part floored), the width within the clamp box: %s" % hs)
    # export / import code + a profile round trip carry the Abilities line like every widget
    l.anchor, l.dx, l.dy, l.opt = "br", 40, 300, False
    LS.save(u)
    code = str(LS.export(u))
    me2 = pref(2, "Noa")
    u2 = me2.getUuid()
    rc_ = int(LS.importCode(u2, code))
    l_in = LS.get(u2).get("Abilities")
    ok_prof = bool(LS.profileSave(u, "abil"))
    LS.get(u).get("Abilities").dy = 5
    rp_ = int(LS.profileLoad(u, "abil"))
    chk("Abilities=" in code and rc_ > 0 and str(l_in.anchor) == "br" and int(l_in.dx) == 40 and int(l_in.dy) == 300 and not bool(l_in.opt)
        and ok_prof and rp_ > 0 and int(LS.get(u).get("Abilities").dy) == 300,
        "W8: export code -> import on another player, profile save -> load: the Abilities line (spot + Icons Show) travels like every widget: %s %s %s" % (code[-40:], rc_, rp_))
    l = LS.get(u).get("Abilities")
    l.anchor, l.dx, l.dy, l.opt = "tl", 8, 760, True
    LS.save(u)
    # the Combat widget's bar still goes through the same path (Widgets.barPairs "Bar" = barOf)
    cm_ = JArray(String)(["CI", "In combat 4s", "In combat", "4s", "0.667", "r"])
    chk([str(x) for x in Wid.barPairs("Combat", cm_)] == ["Bar", "0.667"] and str(Wid.barOf("Combat", cm_)) == "0.667"
        and len(list(Wid.barPairs("Party", cm_))) == 0, "W9: Widgets.barPairs keeps the Combat bar exactly as barOf (selector #SkyyWCombatBar)")
    # an old 0.3.17 layout file (no Abilities line) loads unchanged, Abilities at its default
    use_dir("w2")
    d2 = os.path.join(work, "w2", "layouts")
    os.makedirs(d2, exist_ok=True)
    lines = ["Combat=1,t,0,130,100,1,gold,1,0,1,def,0,-,aqua", "Coins=1,br,8,8,100,1,def,1,0,0,def,1,-,lime", "Skills=1,tl,8,544,100,1,def,1,0,0,def,1,1023"]
    open(os.path.join(d2, str(u) + ".properties"), "w", encoding="latin-1").write("#SkyyHud layout\n" + "\n".join(lines) + "\n")
    m = LS.get(u)
    chk(str(m.get("Combat").ser()) == lines[0].split("=", 1)[1] and str(m.get("Coins").ser()) == lines[1].split("=", 1)[1]
        and bool(m.get("Abilities").en) and int(m.get("Abilities").dy) == 760, "W10: a 0.3.17 layout file loads unchanged; Abilities at its default")
    res["afn_calls"] = afn.calls
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


# ======================================================================================================== J (plain Python)
def run_j():
    zj, zo = zipfile.ZipFile(JAR), zipfile.ZipFile(OLD_JAR)
    nn = sorted(n for n in zj.namelist() if not n.endswith(".class"))
    no = sorted(n for n in zo.namelist() if not n.endswith(".class"))
    icons = sorted("Common/UI/Custom/SkyyHud/Abil/%s.png" % i for c, i in ICONS)
    check(nn == sorted(no + icons), "J. the jar = 0.3.17's entries + the 10 Mage / Priest icons: %s" % sorted(set(nn) ^ set(no)))
    for c, i in ICONS:
        b = zj.read("Common/UI/Custom/SkyyHud/Abil/%s.png" % i)
        src = open(os.path.join(ICON_SRC, c, i + ".png"), "rb").read()
        check(b == src and b[:8] == b"\x89PNG\r\n\x1a\n" and int.from_bytes(b[16:20], "big") == 64 and int.from_bytes(b[20:24], "big") == 64,
              "J. %s.png = art/ability-icons/.../%s/%s.png, a 64 x 64 PNG" % (i, c, i))
    for n in ("Common/UI/Custom/SkyyHud/dot.png", "icon-256.png"):
        check(zj.read(n) == zo.read(n), "J. %s identical to 0.3.17" % n)
    mn, mo = json.loads(zj.read("manifest.json")), json.loads(zo.read("manifest.json"))
    diff = sorted(k for k in set(mn) | set(mo) if mn.get(k) != mo.get(k))
    check(diff == ["Description", "Name", "Version"] and mn["IncludesAssetPack"] is True and "Abilities" in mn["Description"],
          "J. manifest.json: only Name / Version / Description differ; IncludesAssetPack true: %s" % diff)
    check(not any(n.lower().endswith(".ui") for n in zj.namelist()), "J. no .ui file in the jar")


# ======================================================================================================== parent
def main():
    if "--child-w" in sys.argv:
        run_w(arg("--out"))
        return
    if "--child-v" in sys.argv:
        m = load_module(os.path.join(HERE, "test_skyyhud_0.3.17.py"), "hud0317h")
        m.JAR, m.SCRATCH, m.VERSION = JAR, SCRATCH, VERSION
        try:
            m.run_v()
        except Exception as e:
            import traceback
            traceback.print_exc()
            m.FAILS.append("crash: %s" % e)
        # 0.3.17's V counts its ONE common asset (dot.png); this jar has 11 (dot.png + the 10 icons) - the only allowed difference
        want = "V: the jar's common assets registered: 11 (dot.png; the icon is a root file, not an asset)"
        rest = [f for f in m.FAILS if f != want]
        print("V child: %d ok, %d fail (the asset count line %s)" % (m.OKS[0], len(rest), "= 11" if want in m.FAILS else "NOT 11"))
        for f in rest:
            print("FAIL", f)
        sys.exit(1 if rest or want not in m.FAILS else 0)
    if "--bytecode" in sys.argv:
        m = load_module(os.path.join(HERE, "test_skyyhud_0.3.13.py"), "hud0313h")
        m.SCRATCH = SCRATCH
        m.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"), arg("--ov"), arg("--nv"))
        return
    for j in (JAR, OLD_JAR, OLD2_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not (SCRATCH + os.sep).startswith(SCRATCH_ROOT + os.sep) or SCRATCH == SCRATCH_ROOT:
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"), PYTHONDONTWRITEBYTECODE="1")
    env.pop("JAVA_TOOL_OPTIONS", None)
    me = os.path.abspath(__file__)
    run_j()
    # A + W
    out = os.path.join(SCRATCH, "w.json")
    p = subprocess.run([sys.executable, me, "--child-w", "--out", out, "--dir", SCRATCH, "--jar", JAR], env=env)
    check(p.returncode == 0 and os.path.isfile(out), "W: the child JVM ran")
    if os.path.isfile(out):
        R = json.load(open(out))
        for ok, what in R["checks"]:
            check(ok, what)
        for n in R.get("notes", []):
            print("note:", n)
        print("A/W: %d checks in the child; class:fn:abil asked %d times" % (len(R["checks"]), R.get("afn_calls", 0)))
    # F: class compare 0.3.17 -> 0.3.18
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--ov", OLD_VERSION, "--nv", VERSION, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "F. bytecode child ran")
    if os.path.isfile(bco):
        bc = json.load(open(bco))
        diff = sorted(n.split("/")[-1][:-6] for n, r in bc.items() if not r["version_only"] or r["new"] or r["gone"] or r["fields_new"] or r["fields_gone"])
        check(diff == ["HudMain", "SettingsPage", "Widgets"], "F. only Widgets, HudMain and SettingsPage differ beyond the version text: %s" % diff)
        w = [r for n, r in bc.items() if n.endswith("/Widgets.class")][0]
        hm = [r for n, r in bc.items() if n.endswith("/HudMain.class")][0]
        sp = [r for n, r in bc.items() if n.endswith("/SettingsPage.class")][0]
        check(sorted(x.split("(")[0] for x in w["new"]) == ["abilAt", "abilBody", "abilCost", "abilData", "abilHave", "abilIcon", "abilModelU", "abilNum", "abilNumOr",
                                                            "abilRow", "abilSample", "abilSecs", "abilShape", "barPairs"]
              and sorted(x.split("(")[0] for x in w["changed"]) == ["<clinit>", "bodyH", "def", "innerW", "label", "linePairs", "model", "multi", "multiBody", "sampleU"]
              and w["fields_new"] == ["ADIR Ljava/lang/String;", "AICONS [Ljava/lang/String;", "ANEED Ljava/lang/String;"] and not w["gone"],
              "F. Widgets: 14 new methods (the Abilities model / markup + barPairs; FIX2 abilCost), 10 changed (the Abilities branches + IDS / def / label tables), 3 new fields: %s / %s / %s"
              % (w["new"], w["changed"], w["fields_new"]))
        check([x.split("(")[0] for x in hm["changed"]] == ["fill"] and not hm["new"] and [x.split("(")[0] for x in sp["changed"]] == ["build", "previewText"] and not sp["new"],
              "F. HudMain: only fill (the bars loop); SettingsPage: build (the Icons row) + previewText: %s / %s" % (hm["changed"], sp["changed"]))
        zn = set(n for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class"))
        zo = set(n for n in zipfile.ZipFile(OLD_JAR).namelist() if n.endswith(".class"))
        check(zn == zo, "F. no class added or removed: %s %s" % (sorted(zn - zo), sorted(zo - zn)))
    # R: the 0.3.16 harness on the 0.3.18 jar
    print("---- R: the 0.3.16 harness re-run on the %s jar" % VERSION)
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyhud_0.3.16.py"), "--jar", JAR, "--old", OLD2_JAR, "--live", LIVE,
                        "--dir", os.path.join(SCRATCH, "h16")], env=env, capture_output=True, text=True, encoding="utf8", errors="replace")
    failed = [ln.strip()[len("FAILED:"):].strip() for ln in p.stdout.splitlines() if ln.strip().startswith("FAILED:")]
    skipped = [ln for ln in p.stdout.splitlines() if "SKIPPED" in ln]
    allowed = [f for f in failed if f.startswith("F. class bytes 0.3.15 -> 0.3.16 differ only in the expected classes:")
               and sorted(re.findall(r"'(\w+)'", f.split(":", 1)[1])) == ["HudMain", "SettingsPage"]]
    tail = [ln for ln in p.stdout.splitlines() if ln.startswith(("A-L.", "F.", "Z.", "  SKIPPED", "SkyyHud 0.3.16 harness")) or "checks passed" in ln]
    for ln in tail:
        print("  " + ln[:300])
    check(len(failed) == len(allowed) == 1 and not skipped,
          "R. the whole 0.3.16 harness passes on the %s jar (live-copy start twice + the engine-access audit included); its only failing line is its own "
          "0.3.15 -> 0.3.16 class list, which now also names HudMain / SettingsPage (section F checks them): %s" % (VERSION, [f[:200] for f in failed if f not in allowed] or failed[:1]))
    # V: the engine asset validators
    print("---- V: the engine asset validators")
    rc = subprocess.call([sys.executable, me, "--child-v", "--dir", SCRATCH, "--jar", JAR], env=env, cwd=ROOT)
    check(rc == 0, "V. the engine asset validator child passed (exit %d)" % rc)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f[:600])
    print("SkyyHud %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
