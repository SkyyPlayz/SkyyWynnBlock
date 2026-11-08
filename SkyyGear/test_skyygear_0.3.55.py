"""Harness for SkyyGear 0.3.55 (round furnall: the Furnace button - tools/gear_0_3_55_patch.py header; partner SkyySacks 0.8.35 = sacks:fn:openFurnace).
Build first (the build needs Quirk's private art; in a worktree: SKYWYNN_PRIVATE_ART=<path to SkyWynn-PRIVATE-art>):
    python tools/gear_0_3_55_patch.py && python SkyyGear/build_skyygear_0.3.55.py
    python SkyyGear/test_skyygear_0.3.55.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.54 jar is the compare base):
  S  static   the patch re-runs to identical bytes, no new class / command / system
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.54 -> 0.3.55 (EXPECT below)
  E  engine   every new path EXECUTED with a real UICommandBuilder / UIEventBuilder and a stand-in bridge function: footF without the bridge = the old footer; with it = the
              Button, the vanilla icon, the event, a footer that adds up to the 1552 px page; route: "hub:furnace" with the bridge saying yes ("opened", no second update) / no ("info:" +
              the footer text, never chat) / throwing; not a hub click = null; the Button has Refresh's art + sounds; the real click hooks (skyHde) of the pages that draw the button put
              the refusal on this.info. GearHub.tabOf: the four pages with the button are Smithing or Upgrade.
  D  live     0.3.54's start twice on a scratch COPY of Skyy's live data: no new migration, the second start changes nothing
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the button; the page swap itself (SkyySacks' CraftHubOpen.apply needs a real player).
Scratch: tools/dev/scratch/furnall/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.55"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "furnall", "gear")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.54.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_55_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.54.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
T54 = {"__file__": os.path.join(HERE, "test_skyygear_0.3.54.py"), "__name__": "t54"}
_s = open(T54["__file__"], encoding="utf8").read()
exec(compile(_s[:_s.index("HK.run_compare = run_compare54")], T54["__file__"], "exec"), T54)
T54["SCRATCH"] = SCRATCH
EXPECT = None if "--expect-dump" in sys.argv else {
    "GearHub": ["+m footF", "+m furnace", "~m route"], "ReforgePage": ["~m upBuild", "~m skyHde"], "LifePage": ["~m build", "~m skyHde"], "SmithPage": ["~m build", "~m skyHde"],
    "UpgPage": ["~m build", "~m skyHde"], "MultiPage": ["~m skyHde"], "IdentifyPage": ["~m skyHde"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "GearCfg": ["~m defaultsText"], "SkyyGearPlugin": ["~m setup"],          # the last row: the version in texts only
}
LIVE_DIR = T54["LIVE_DIR"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.55 - build script') and g.count('VERSION = "0.3.55"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')), (0, 0, 0), "S no new class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.save()


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JString, JProxy, JObject
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    GH = JClass(PKG + "GearHub")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Mod = JClass("java.lang.reflect.Modifier")

    def texts(b_):
        o_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if Mod.isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        o_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(o_)

    def evs(e_):
        o_ = []
        for c_ in e_.getEvents():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if Mod.isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        o_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(o_)

    b0, e0 = UCBc(), UEBc()
    GH.footF(b0, e0, JString("hello"))
    t0 = texts(b0)
    K.check("SkyyGBtnFurnace" not in t0 and "SkyyGInfo" in t0 and "SkyyGBtnRefresh" in t0, "E without the bridge the footer is the old one (result line + Refresh)")
    CALLS, ANSWER = [], [True]

    class Fn(object):
        pass
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class OpenFn(object):
        @JOverride
        def apply(self, x):
            CALLS.append(str(x))
            a = ANSWER[0]
            if a == "boom":
                raise JClass("java.lang.RuntimeException")("boom")
            return JClass("java.lang.Boolean").valueOf(bool(a))

        @JOverride
        def compose(self, f):
            return None

        @JOverride
        def andThen(self, f):
            return None
    bridge.put("sacks:fn:openFurnace", OpenFn())
    b1, e1 = UCBc(), UEBc()
    GH.footF(b1, e1, JString("hello"))
    t1, ev1 = texts(b1), evs(e1)
    K.check("Button #SkyyGBtnFurnace" in t1 and 'ItemId: "Bench_Furnace"' in t1 and "Furnace" in t1 and "SkyyGBtnRefresh" in t1, "E the footer has the Furnace Button with the vanilla icon, Refresh stays")
    K.check("hub:furnace" in ev1 and "SkyyGBtnFurnace" in ev1 and "refresh" in ev1, "E the button sends hub:furnace, Refresh still refresh")
    m = re.findall(r"Label #SkyyGInfo \{ Anchor: \(Width: (\d+)", t1)
    K.check(m and int(m[0]) + 10 + 170 + 10 + 170 == 1552, "E the footer adds up to the 1552 px page: %s + 10 + 170 + 10 + 170" % m)
    K.eq(t1.index("Label #SkyyGInfo") < t1.index("Button #SkyyGBtnFurnace") < t1.index("TextButton #SkyyGBtnRefresh"), True, "E the order: result line, Furnace, Refresh")
    fb = t1[t1.index("Button #SkyyGBtnFurnace"):]
    fb = fb[:fb.index("SkyyGBtnFurnace", 40)] if "SkyyGBtnFurnace" in fb[40:] else fb
    K.check("#000000(0.05)" not in fb and "ButtonStyle(" in fb and "TextButtonStyle(" not in fb, "E fix 1: the Furnace Button has a ButtonStyle, not the plain row background")
    for st_ in ("Default", "Hovered", "Pressed"):
        ra_ = re.search(r"TextButton #SkyyGBtnRefresh.*?%s: \(Background: (\(TexturePath: .+?\)), LabelStyle" % st_, t1, re.S)
        fa_ = re.search(r"Button #SkyyGBtnFurnace.*?%s: \(Background: (\(TexturePath: .+?\))\)" % st_, t1, re.S)
        K.check(ra_ is not None and fa_ is not None and ra_.group(1) == fa_.group(1), "E fix 1: %s art = Refresh's: %s" % (st_, fa_.group(1) if fa_ else None))
    K.check("Sounds: (Activate: (SoundPath: " in fb, "E fix 1: the Furnace Button has the kit's click and hover sounds")
    K.check("FontSize: 17" in t1[t1.index('Text: "Furnace"'):t1.index('Text: "Furnace"') + 200] and "RenderUppercase: true" in t1[t1.index('Text: "Furnace"'):t1.index('Text: "Furnace"') + 200], "E fix 1: the label is the kit button label")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = us.allocateInstance(PRc.class_)
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000355")
    for f_ in PRc.class_.getDeclaredFields():
        if f_.getType() == JClass("java.util.UUID").class_ and not Mod.isStatic(f_.getModifiers()):
            f_.setAccessible(True)
            f_.set(pr, U)
    K.check(GH.route(pr, JString('{"a":"refresh"}'), 3) is None, "E route: not a hub click = null")
    ANSWER[0] = True
    n0 = int(GH.N[2])
    K.eq(str(GH.route(pr, JString('{"a":"hub:furnace"}'), 3)), "opened", "E route: the bridge opened the page = handled, no second update")
    K.check(CALLS[-1:] == [str(U)] and int(GH.N[2]) == n0 + 1, "E the bridge got the UUID: %s" % CALLS[-1:])
    ANSWER[0] = False
    n3 = int(GH.N[3])
    EQUIP = "info:-Equip a Furnace accessory in your Void Charms to use the Furnace."
    K.eq(str(GH.route(pr, JString('{"a":"hub:furnace"}'), 6)), EQUIP, "E fix 2: refused = the footer text, no chat, no [Smithing] prefix")
    K.eq(int(GH.N[3]), n3 + 1, "E refusal counted")
    ANSWER[0] = "boom"
    BROKE = "info:-The Furnace could not open."
    K.eq(str(GH.route(pr, JString('{"a":"hub:furnace"}'), 4)), BROKE, "E route: a throwing bridge is caught, the footer says so")
    bridge.remove("sacks:fn:openFurnace")
    K.eq(str(GH.route(pr, JString('{"a":"hub:furnace"}'), 1)), BROKE, "E route: a bridge gone since the page was drawn = the footer says so")
    # fix 2: the real hooks of every page that draws the button (rebuild() on a stand-in player may throw AFTER this.info is set: that is the stand-in, not the hook)
    bridge.put("sacks:fn:openFurnace", OpenFn())
    Cfg = JClass(PKG + "GearCfg")
    CUP = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage")

    def click(page_name, anvil, answer):
        Cfg.ANVIL_ON = anvil
        ANSWER[0] = answer
        k_ = JClass(PKG + page_name).class_
        pg_ = us.allocateInstance(k_)
        rf_ = CUP.class_.getDeclaredField("playerRef")
        rf_.setAccessible(True)
        rf_.set(pg_, pr)
        m_ = [x_ for x_ in k_.getDeclaredMethods() if str(x_.getName()) == "handleDataEvent"][0]
        m_.setAccessible(True)
        try:
            m_.invoke(pg_, None, None, JString('{"a":"hub:furnace"}'))
        except Exception as ex_:
            pass
        return None if pg_.info is None else str(pg_.info)
    for pn_, an_ in (("SmithPage", True), ("LifePage", True), ("UpgPage", True), ("ReforgePage", True), ("ReforgePage", False)):
        K.eq(click(pn_, an_, False), EQUIP[5:], "E fix 2: %s (anvil %s) refused: the text is on this.info for the footer" % (pn_, an_))
        K.eq(click(pn_, an_, True), None, "E fix 2: %s (anvil %s) opened: nothing on this.info, no second update path" % (pn_, an_))
    Cfg.ANVIL_ON = True
    GU = JClass(PKG + "GearUi")
    K.eq((str(GU.infoText(JString(EQUIP[5:]))), str(GU.infoColor(JString(EQUIP[5:])))), (EQUIP[6:], str(JClass(PKG + "GearDefs").C_GOLD)), "E fix 2: the footer shows it without the minus and in the refused gold")
    bridge.remove("sacks:fn:openFurnace")
    K.eq([str(GH.tabOf(i)) for i in (3, 6, 4, 1, 0)], ["gear", "upgrade", "upgrade", "upgrade", "reforge"], "E tabOf: the four pages with the button are the Smithing and Upgrade tabs")
    K.save()


HK.run_compare = T54["run_compare54"]
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
       [("static", run_static), ("engine", run_engine), ("live", T54["run_live"])], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
