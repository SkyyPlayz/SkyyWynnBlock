"""Harness for SkyyHud 0.3.29 (the STACKS widget: class:fn:stacks rows -> a movable / stylable HUD widget; tools/hud_0_3_29_patch.py).
Build first:  python tools/hud_0_3_29_patch.py && python SkyyHud/build_skyyhud_0.3.29.py

    python SkyyHud/test_skyyhud_0.3.29.py [--jar SkyyHud-0.3.29.jar] [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.28 -> 0.3.29: exactly the listed classes / members differ; non-class entries: the manifest
  R28  the 0.3.28 phase (Background OFF by default, Quest ON, saved values kept, reset, admin default, import) re-run on THIS jar
  S    stacks   EXECUTED on the real jar classes (Widgets / LayoutStore / HudMain.build / fill / fillStacks / stacksTick, SkyyHudPlugin.stacksAll);
                only the player and class:fn:stacks are stand-ins:
                S1 the id APPENDED, built-in spot br 460,86 (6 px above the Abilities box), 220 x 118, Background OFF, label, multi
                S2 no key / null / empty / not an array / a throwing Function (no stack seen yet) = hidden, nothing in the HUD document;
                   the editor stand-in; a stack seen = shape "T|<class>", then no rows = the same shape with blank slots
                S3 the model: rows parsed (pips / bar / no strip, colours checked, empty / repeated name skipped, at most 4, clamp, countdown);
                   a row KEEPS its slot (Rolling / Unstoppable / back); a full table reuses a slot whose name is not shown
                S4 the markup: the FIXED 220 x 118 box, 4 slots x (2 labels + 10 dim + 10 bright pips + a ProgressBar in a Group), bottom-
                   anchored = slot 0 at the bottom, slot colours, no Background, no underscores; the first fill
                S5 fillStacks: values, a max / colour change, rows coming / going, pips <-> bar = Sets only; only a CLASS change re-sends.
                   S5x the critic's case: a Spellblade crossing Rolling -> Unstoppable -> back x3 through stacksStep = ZERO page re-sends; a
                   new colour = ONE deferred re-send after 10 s quiet, at most once a minute
                S6 the 1 s fill never calls class:fn:stacks (the 250 ms step does)
                S7 the height (118) and width (220) never change with rows / countdowns; every size 50-200 % (bodyH = the markup)
                S8 a picked colour overrides the row colours (Default = the row colour)
                S9 widget OFF: stacksTick reads nothing; SkyyHudPlugin.stacksAll steps every HUD (one call each)
                S10 /skyyhud reset saves the Stacks line (Background 0); an old file without it gets the built-in spot
                S11 bytecode: FeedTick.run -> stacksAll -> stacksTick -> stacksStep -> fillStacks; class:fn:stacks asked only from the model;
                    the Stacks code reaches no file / sleep
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the look (pip strip, colours over terrain), .Visible on Groups in a HUD document (the Quest
arrows use it), the real class:fn:stacks rows of SkyyClasses 0.1.32.
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION, PREV = "0.3.29", "0.3.28"
PKG = "com.skyy.hud."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0329", "h")))
ADDED = []
EXPECT = {
    "Widgets": ["+f STKCALLS", "+f STKNEED", "+f STKT", "+m stkBody", "+m stkHave", "+m stkHex", "+m stkIn", "+m stkModelOf", "+m stkModelT",
                "+m stkModelU", "+m stkN", "+m stkNewT", "+m stkNum", "+m stkSample", "+m stkSig", "+m stkSplit", "~<clinit>", "~m barPairs",
                "~m bodyH", "~m def0", "~m label", "~m linePairs", "~m model", "~m multi", "~m multiBody", "~m multiW", "~m sampleU", "~m visPairs"],
    "HudMain": ["+f stkAt", "+f stkLast", "+f stkRc", "+m fillStacks", "+m stacksStep", "+m stacksTick", "+m stkRecolor", "~m fill"],
    "SkyyHudPlugin": ["+m stacksAll", "~m setup"],
    "FeedTick": ["~m run"],
    "SettingsPage": ["~m previewText"],
    # the version string (the kit's header / export)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
}


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_r28(out, jar, scratch, home):
    load_module(os.path.join(HERE, "test_skyyhud_0.3.28.py"), "hud0328h").run_r28(out, jar, scratch, home)


def run_stacks(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    UUID, System, CHM, Paths = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                f.set(obj, val)
                return
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)
    H = lambda n: JClass(PKG + n)
    WL, Wid, LS, HM, Cfg, HT, Plugin = H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("HudCfg"), H("HudThreads"), H("SkyyHudPlugin")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, "s")
    os.makedirs(os.path.join(work, "cfg"), exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(work, "cfg", "config.properties"))
    Cfg.load()
    HT.EXEC = None
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)

    def use_dir(name):
        d = os.path.join(work, name)
        os.makedirs(os.path.join(d, "layouts"), exist_ok=True)
        LS.DIR = Paths.get(os.path.join(d, "layouts"))
        LS.CACHE.clear()
        return d

    def pref(n, name="Mia"):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID(0x329, n))
        setf(pr, PRef, "username", name)
        return pr

    def cmds(b):
        return [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]

    def sets(cm):
        out_ = {}
        for c in cm:
            if c[0] == "Set" and c[1]:
                v = c[2]
                try:
                    x = json.loads(v)
                    if isinstance(x, dict) and list(x) == ["0"]:
                        x = x["0"]
                    v = x
                except Exception:
                    pass
                out_[c[1]] = v
        return out_

    def hud(pr):
        h = HM(pr)
        b = UCB()
        mBuild.invoke(h, b)
        return h, cmds(b)

    def sgroup(cm):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and "Group #SkyyWStacks " in c[3]]
        return g[0] if len(g) == 1 else None

    @JImplements("java.util.function.Function")
    class SFn(object):
        def __init__(self):
            self.ans = None
            self.calls = 0
            self.args = []
            self.boom = False

        @JOverride
        def apply(self, a):
            self.calls += 1
            self.args.append(a)
            if self.boom:
                raise RuntimeError("boom")
            if self.ans is None:
                return None
            return JArray(JString)(self.ans)

    def mlist(m):
        return [None if x is None else str(x) for x in m]

    calls = lambda: int(Wid.STKCALLS.get())
    # ================================================================================== S1 id + spot
    ids = [str(x) for x in Wid.IDS]
    K.check(ids[-2:] == ["Quest", "Stacks"], "S1 Stacks APPENDED to Widgets.IDS: %s" % ids[-3:])
    d = Wid.def_("Stacks") if hasattr(Wid, "def_") else Wid.__getattribute__("def")("Stacks")
    K.eq((bool(d.en), str(d.anchor), int(d.dx), int(d.dy), int(d.scale), int(d.bw), int(d.bh), bool(d.bg)), (True, "br", 460, 86, 100, 220, 118, False),
         "S1 the built-in spot br 460,86, 220 x 118, ON, Background OFF")
    da = Wid.def_("Abilities") if hasattr(Wid, "def_") else Wid.__getattribute__("def")("Abilities")
    K.eq((1080 - int(d.dy)) + 6, 1080 - int(da.dy) - int(da.bh), "S1 the Stacks box ends 6 px above the Abilities box (built-in spots)")
    K.eq(str(Wid.label("Stacks")), "Stacks", "S1 label")
    K.check(bool(Wid.multi("Stacks")) and not bool(Wid.bgDef("Stacks")), "S1 a multi-line widget, Background OFF by default")
    # ================================================================================== S2 hidden cases
    use_dir("s2")
    pr = pref(1)
    u = pr.getUuid()
    l = LS.get(u).get("Stacks")
    K.eq(str(Wid.modelL("Stacks", pr, l)[0]), "T0", "S2 no class:fn:stacks = hidden")
    h, cm = hud(pr)
    K.check(sgroup(cm) is None and str(h.shape.get("Stacks")) == "T0", "S2 ... nothing in the HUD document (shape T0 tracked)")
    v = Wid.viewModel("Stacks", pr, l)
    K.eq((str(v[0]), str(v[2]), str(v[1])), ("S", "Needs SkyyClasses 0.1.32", "Needs SkyyClasses 0.1.32"), "S2 the editor / Settings stand-in")
    fn = SFn()
    bridge.put("class:fn:stacks", fn)
    v = Wid.viewModel("Stacks", pr, l)
    K.eq((str(v[0]), str(v[2]), str(v[3]), str(v[9]), str(v[10])), ("S", "Momentum", "3/5  4s", "Combo", "2/3"), "S2 with the key (nothing to show): the sample")
    for label, setup in (("null", lambda: setattr(fn, "ans", None)), ("empty", lambda: setattr(fn, "ans", [])),
                         ("only nameless rows", lambda: setattr(fn, "ans", ["|1|2|0|#ffffff", "  |3|3"])),
                         ("a throwing Function", lambda: setattr(fn, "boom", True))):
        setup()
        m = Wid.modelL("Stacks", pr, l)
        K.check(str(m[0]) == "T0" and m[1] is None, "S2 %s (no stack seen yet) = hidden" % label)
        fn.boom = False
    bridge.put("class:fn:stacks", "not a function")
    K.eq(str(Wid.modelL("Stacks", pr, l)[0]), "T0", "S2 a key that is not a Function = hidden")
    K.eq(str(Wid.stkModelOf(JString("a|1|2"))[0]), "T0", "S2 an answer that is not an array = hidden")
    bridge.put("class:fn:stacks", fn)
    bridge.put("class:" + str(u), "Spellblade")
    fn.args = []
    fn.ans = ["Momentum|3|5|0|#7fc8ff"]
    m = Wid.modelL("Stacks", pr, l)
    a0 = fn.args[-1] if fn.args else None
    K.check(a0 is not None and len(a0) == 1 and str(a0[0]) == str(u), "S2 called with new Object[] { UUID }: %s" % (None if a0 is None else [str(x) for x in a0]))
    K.eq(str(m[0]), "T|Spellblade", "S2 a stack seen: shape T|<class>")
    fn.ans = []
    m = mlist(Wid.modelL("Stacks", pr, l))
    K.check(m[0] == "T|Spellblade" and m[1] == "Stacks" and m[2] == "" and m[30] == "0" and m[5] == "#7fc8ff", "S2 ... then no rows: the same shape, blank slots (colour kept)")
    # ================================================================================== S3 the model + the fixed slots
    m = mlist(Wid.stkModelOf(JArray(JString)(["Momentum|3|5|4.2|#7FC8FF", "Frenzy|12|20|0|zzz", " Combo |7|3", "|1|2|0|#fff000", "Charge|2.9|0|0|#123456", "Fifth|1|1"])))
    K.eq((m[0], m[1], m[30]), ("T|", "Momentum 3/5  5s", "4"), "S3 shape, headline, 4 rows (the 5th named row dropped)")
    K.eq(m[2:9], ["Momentum", "3/5  5s", "0.000", "#7fc8ff", "5", "3", "0"], "S3 slot 0: 5 pips (3 lit), 4.2 s left = 5s, colour lower-cased")
    K.eq(m[9:16], ["Frenzy", "12/20", "0.600", None, "0", "0", "1"], "S3 slot 1: max 20 > 10 = the bar 0.600, no pips, a bad colour = the widget's")
    K.eq(m[16:23], ["Combo", "3/3", "0.000", None, "3", "3", "0"], "S3 slot 2: name trimmed, current clamped to max, no secs field")
    K.eq(m[23:30], ["Charge", "2", "0.000", "#123456", "0", "0", "0"], "S3 slot 3: max 0 = no strip, 2.9 floored; a nameless row skipped")
    m = mlist(Wid.stkModelOf(JArray(JString)(["A|-3|-2|-1|#abc", "B|x|y|z", "C|1|5|100000", "A|9|9"])))
    K.eq((m[3], m[10], m[5], m[30]), ("0", "0", None, "3"), "S3 negatives / junk = 0 (no countdown), a 3-digit colour = none, a repeated name skipped")
    K.check(m[17].startswith("1/5  ") and m[17].endswith("m"), "S3 a long countdown shows minutes: %s" % m[17])
    tb = Wid.stkNewT("Spellblade")
    slots = []
    for rows in (["Momentum|2|5", "Rolling|1|1"], ["Momentum|5|5", "Unstoppable|1|1|4"], ["Momentum|1|5"], ["Momentum|3|5", "Rolling|1|1"],
                 ["Unstoppable|1|1", "Momentum|5|5"]):
        mm = mlist(Wid.stkModelT(JArray(JString)(rows), tb))
        slots.append((mm[0], [mm[2 + 7 * k] for k in range(4)]))
    K.eq(slots, [("T|Spellblade", ["Momentum", "Rolling", "", ""]), ("T|Spellblade", ["Momentum", "", "Unstoppable", ""]),
                 ("T|Spellblade", ["Momentum", "", "", ""]), ("T|Spellblade", ["Momentum", "Rolling", "", ""]),
                 ("T|Spellblade", ["Momentum", "", "Unstoppable", ""])], "S3 a row keeps its slot (any order); the shape never changes")
    for rows in (["A|1|2", "B|1|2"], ["C|1|2", "D|1|2"], ["E|1|2"]):
        mm = mlist(Wid.stkModelT(JArray(JString)(rows), tb))
    K.eq([mm[2 + 7 * k] for k in range(4)].count("E"), 1, "S3 a full table: a new name takes a slot whose name is not shown now")
    # ================================================================================== S4 markup + first fill
    use_dir("s4")
    pr = pref(4)
    u = pr.getUuid()
    bridge.put("class:" + str(u), "Berserker")
    fn.ans = ["Momentum|3|5|4|#7fc8ff", "Frenzy|12|20|0|", "Combo|1|3|0|#f0c060"]
    h, cm = hud(pr)
    g = sgroup(cm)
    K.check(g is not None, "S4 the widget is in the HUD document")
    g = g or ""
    K.check(re.search(r"Anchor: \((?=[^)]*Bottom: 86)(?=[^)]*Right: 460)(?=[^)]*Width: 220)(?=[^)]*Height: 118)[^)]*\)", g) is not None, "S4 the FIXED box br 460,86, 220 x 118: %s" % g[:120])
    K.check(not g.split("Label")[0].count("Background: #0b1524"), "S4 no widget Background (0.3.28 rule)")
    pips = re.findall(r"Group #SkyyWStacks([DP])(\d)n(\d) \{ Anchor: \([^)]*\); Background: (#[0-9a-f]{6})\((0\.25|0\.95)\); Visible: (true|false); \}", g)
    K.eq(len(pips), 80, "S4 4 slots x 10 dim + 10 bright pips always in the markup")
    lit = sorted((k, j) for (dp, k, j, c, a, vv) in pips if dp == "P" and vv == "true")
    dim = sorted((k, j) for (dp, k, j, c, a, vv) in pips if dp == "D" and vv == "true")
    K.eq(lit, sorted([("0", str(j)) for j in range(3)] + [("2", "0")]), "S4 bright pips: Momentum 3, Combo 1")
    K.eq(dim, sorted([("0", str(j)) for j in range(5)] + [("2", str(j)) for j in range(3)]), "S4 dim pips: Momentum 5, Combo 3")
    K.check(all(c == "#7fc8ff" for (dp, k, j, c, a, vv) in pips if k == "0") and all(c == "#f0c060" for (dp, k, j, c, a, vv) in pips if k == "2"), "S4 pips in the slot colours")
    bw = re.findall(r"Group #SkyyWStacksBW(\d) \{ Anchor: \([^)]*\); Visible: (true|false); ProgressBar #SkyyWStacksBar\1 ", g)
    K.eq(sorted(bw), [("0", "false"), ("1", "true"), ("2", "false"), ("3", "false")], "S4 each slot's ProgressBar in a Group; only Frenzy's shown")
    K.check("Value: 0.600" in g and '"Common/ProgressBar.png"' in g and '"Common/ProgressBarFill.png"' in g, "S4 the vanilla ProgressBar textures + value")
    for e in ("N0", "S0", "N1", "S1", "N2", "S2", "N3", "S3"):
        K.check(("Label #SkyyWStacks%sTxt " % e) in g, "S4 label %s" % e)
    tops = dict((k, int(t_)) for k, t_ in re.findall(r"Label #SkyyWStacksN(\d)Txt \{ Anchor: \(Left: -?\d+, Top: (\d+)", g))
    K.check(len(tops) == 4 and tops["0"] > tops["1"] > tops["2"] > tops["3"], "S4 bottom-anchored: slot 0 at the bottom (%s)" % tops)
    K.check(re.search(r"Label #SkyyWStacksN0Txt [^}]*TextColor: #7fc8ff", g) and re.search(r"Label #SkyyWStacksN2Txt [^}]*TextColor: #f0c060", g),
            "S4 slot texts in the row colour")
    defc = str(Wid.hexOf("def"))
    K.check(re.search(r"Label #SkyyWStacksN1Txt [^}]*TextColor: " + re.escape(defc), g) is not None, "S4 a row without colour = the widget colour %s" % defc)
    ids_ = re.findall(r"#([A-Za-z0-9_]+)", g)
    K.check(ids_ and not [i for i in ids_ if "_" in i], "S4 no underscores in element ids")
    st = sets(cm)
    K.eq([st.get("#SkyyWStacks%sTxt.Text" % e) for e in ("N0", "S0", "N1", "S1", "N2", "S2", "N3", "S3")],
         ["Momentum", "3/5  4s", "Frenzy", "12/20", "Combo", "1/3", "", ""], "S4 the first fill's texts (slot 3 blank)")
    K.check(abs(float(st.get("#SkyyWStacksBar1.Value", -1)) - 0.6) < 1e-6, "S4 the bar Value")
    K.eq([st.get("#SkyyWStacksP0n%d.Visible" % j) for j in range(5)], [True, True, True, False, False], "S4 the pip .Visible sets")
    # ================================================================================== S5 fillStacks + THE CROSSING (zero page re-sends)
    def step():
        b = UCB()
        c0 = calls()
        r_ = bool(h.fillStacks(b, System.currentTimeMillis()))
        return r_, cmds(b), calls() - c0
    re_, cm2, nc = step()
    K.check(not re_ and cm2 == [] and nc == 1, "S5 unchanged: nothing sent, one class:fn:stacks call (%s, %d calls)" % (cm2[:2], nc))
    fn.ans = ["Momentum|4|5|3|#7fc8ff", "Frenzy|15|20|0|", "Combo|1|3|0|#f0c060"]
    re_, cm2, nc = step()
    s2 = sets(cm2)
    K.check(not re_ and not [c for c in cm2 if c[0] != "Set"], "S5 current / countdown / bar: Sets only, no re-send")
    K.eq(sorted(s2), sorted(["#SkyyWStacksS0Txt.Text", "#SkyyWStacksP0n3.Visible", "#SkyyWStacksS1Txt.Text", "#SkyyWStacksBar1.Value"]), "S5 only what changed is sent")
    K.check(s2.get("#SkyyWStacksS0Txt.Text") == "4/5  3s" and s2.get("#SkyyWStacksP0n3.Visible") is True and abs(float(s2.get("#SkyyWStacksBar1.Value")) - 0.75) < 1e-6,
            "S5 the values: %s" % s2)
    for label, a_ in (("a max change", ["Momentum|0|6|0|#7fc8ff", "Frenzy|15|20|0|", "Combo|1|3|0|#f0c060"]),
                      ("a colour change", ["Momentum|0|5|0|#ff0000", "Frenzy|15|20|0|", "Combo|1|3|0|#f0c060"]),
                      ("a new row", ["Momentum|0|5|0|#7fc8ff", "Frenzy|15|20|0|", "Combo|1|3|0|#f0c060", "Echo|1|2"]),
                      ("a row gone", ["Momentum|0|5|0|#7fc8ff", "Combo|1|3|0|#f0c060"]),
                      ("every row gone", []),
                      ("max 5 -> 20 (pips -> bar)", ["Momentum|7|20|0|#7fc8ff"])):
        fn.ans = a_
        re_, cm2, nc = step()
        K.check(not re_ and not [c for c in cm2 if c[0] != "Set"], "S5 %s = Sets only, no page re-send" % label)
    s2 = sets(cm2)
    K.check(s2.get("#SkyyWStacksBW0.Visible") is True and s2.get("#SkyyWStacksD0n0.Visible") is not True, "S5 pips -> bar: the bar Group shown, no pip lit (they went dark at the empty step)")
    bridge.put("class:" + str(u), "Monk")
    fn.ans = ["Combo|1|3|0|#ffd060"]
    re_, cm2, nc = step()
    K.check(re_ and not cm2, "S5 a CLASS change = the shape re-send (nothing half-sent)")
    # the critic's case: a Spellblade crossing Rolling -> Unstoppable -> back, 250 ms steps, through stacksStep (the timer's entry)
    use_dir("s5x")
    pr = pref(6, "Sy")
    u = pr.getUuid()
    bridge.put("class:" + str(u), "Spellblade")
    fn.ans = ["Momentum|2|5|0|#7fc8ff", "Rolling|1|1|0|#9fe0ff"]
    h, cm = hud(pr)
    K.check(sgroup(cm) is not None, "S5x the Spellblade HUD is built")
    t0 = 1000000000000
    seq = [["Momentum|3|5|0|#7fc8ff", "Rolling|1|1|0|#9fe0ff"], ["Momentum|5|5|6|#7fc8ff", "Unstoppable|1|1|6|#ff9a3c"],
           ["Momentum|5|5|5|#7fc8ff", "Unstoppable|1|1|5|#ff9a3c"], ["Momentum|1|5|0|#7fc8ff"], ["Momentum|3|5|0|#7fc8ff", "Rolling|1|1|0|#9fe0ff"],
           ["Momentum|5|5|6|#7fc8ff", "Unstoppable|1|1|6|#ff9a3c"], ["Momentum|2|5|0|#7fc8ff", "Rolling|1|1|0|#9fe0ff"], []] * 3
    res = []
    c0 = calls()
    for i, a_ in enumerate(seq):
        fn.ans = a_
        h.stacksStep(t0 + 250 * i)
        res.append(int(h.lastRe) != 0 or int(h.stkRc) != 0)
    K.eq(calls() - c0, len(seq), "S5x one class:fn:stacks call per 250 ms step")
    K.check(not any(res) and int(h.lastRe) == 0 and int(h.stkRc) == 0, "S5x Rolling -> Unstoppable -> back x3 (%d steps): ZERO page re-sends (lastRe %d)" % (len(seq), int(h.lastRe)))
    tq = t0 + 250 * len(seq)
    fn.ans = ["Momentum|2|5|0|#7fc8ff", "Rolling|1|1|0|#9fe0ff"]
    h.stacksStep(tq)
    h.stacksStep(tq + 5000)
    K.check(int(h.stkRc) == 0, "S5x Unstoppable's new colour: no re-send while the widget is quiet for < 10 s")
    h.stacksStep(tq + 10500)
    K.eq(int(h.stkRc), tq + 10500, "S5x ... ONE deferred colour re-send after 10 s quiet")
    h.stacksStep(tq + 30000)
    K.eq(int(h.stkRc), tq + 10500, "S5x ... at most once a minute")
    # ================================================================================== S6 the 1 s fill leaves it to the 250 ms step
    c0 = calls()
    b = UCB()
    h.fill(b, False)
    K.check(calls() == c0 and not [c for c in cmds(b) if c[1] and "SkyyWStacks" in c[1]], "S6 HudMain.fill (1 s tick) makes no class:fn:stacks call and no Stacks set")
    # ================================================================================== S7 heights + widths (fixed)
    for rows in ([], ["R0|1|3"], ["R0|1|3", "R1|1|3", "R2|1|3", "R3|1|3"]):
        mm = Wid.stkModelOf(JArray(JString)(rows))
        K.eq(int(Wid.bodyH("Stacks", mm, 100)), 118, "S7 %d row(s): always 118 px" % len(rows))
    ls = LS.get(u).get("Stacks")
    mm = Wid.stkModelOf(JArray(JString)(["Momentum|3|5|4|#7fc8ff", "Frenzy|12|20|0|", "Combo|1|3|0|"]))
    for sc in (50, 75, 100, 125, 150, 200):
        ls.scale = sc
        w_ = int(Wid.multiW("Stacks", ls, mm, sc, 6))
        src = str(Wid.multiWidgetSrcW("Stacks", ls, mm, w_))
        K.check(w_ == 220 * sc // 100 and ("Width: %d, Height: %d)" % (w_, int(Wid.bodyH("Stacks", mm, sc)))) in src, "S7 size %d%%: the box %d x %d" % (sc, w_, int(Wid.bodyH("Stacks", mm, sc))))
    ls.scale = 100
    ws = set()
    for rows in (["Momentum|3|5|12|#7fc8ff"], ["Momentum|3|5|9|#7fc8ff"], [], ["A very long stack name here|999999|999999|75"]):
        ws.add(int(Wid.multiW("Stacks", ls, Wid.stkModelOf(JArray(JString)(rows)), 100, 6)))
    K.eq(len(ws), 1, "S7 rows / countdowns never change the box width (%s)" % sorted(ws))
    # ================================================================================== S8 a picked colour overrides
    keys = [str(k) for k in WL.PAL_KEYS]
    pick = keys[3]
    ls.col = pick
    src = str(Wid.multiWidgetSrcW("Stacks", ls, mm, 200))
    ph = str(Wid.hexOf(pick))
    K.check("#7fc8ff" not in src and re.search(r"Label #SkyyWStacksN0Txt [^}]*TextColor: " + re.escape(ph), src) is not None, "S8 Color %s overrides the row colours (%s)" % (pick, ph))
    ls.col = "def"
    # ================================================================================== S9 OFF / the plugin loop
    ls.en = False
    h, cm = hud(pr)
    c0 = calls()
    h.stacksTick(System.currentTimeMillis())
    K.check(h.shape.get("Stacks") is None and calls() == c0 and sgroup(cm) is None, "S9 widget OFF: no markup, stacksTick reads nothing")
    ls.en = True
    h, cm = hud(pr)
    h2, _ = hud(pref(5, "Bo"))
    pl = U.allocateInstance(Plugin.class_)
    hm = CHM()
    hm.put(u, h)
    hm.put(UUID(0x329, 5), h2)
    setf(pl, Plugin, "huds", hm)
    c0 = calls()
    pl.stacksAll()
    K.eq(calls() - c0, 2, "S9 SkyyHudPlugin.stacksAll: one class:fn:stacks call per HUD with the widget ON")
    # ================================================================================== S10 reset + old files
    d10 = use_dir("s10")
    ly = os.path.join(d10, "layouts")
    uo = UUID(0x329, 10)
    open(os.path.join(ly, str(uo) + ".properties"), "w").write("Coords=1,tl,8,8,100,1\nAbilities=1,br,460,21,100,0\n")
    so = LS.get(uo).get("Stacks")
    K.eq((bool(so.en), str(so.anchor), int(so.dx), int(so.dy), bool(so.bg)), (True, "br", 460, 86, False), "S10 an old file (no Stacks line): the built-in spot")
    LS.reset(uo)
    lines = open(os.path.join(ly, str(uo) + ".properties"), encoding="latin-1").read().splitlines()
    sl = [x for x in lines if x.startswith("Stacks=")]
    K.check(len(sl) == 1 and sl[0].startswith("Stacks=1,br,460,86,100,0"), "S10 /skyyhud reset saves the Stacks line: %s" % sl)
    # ================================================================================== S11 bytecode
    gr = PW.calls(jar)
    K.check(PKG + "SkyyHudPlugin.stacksAll" in gr.get("FeedTick.run", ()), "S11 FeedTick.run -> SkyyHudPlugin.stacksAll")
    K.check(PKG + "HudMain.stacksTick" in gr.get("SkyyHudPlugin.stacksAll", ()), "S11 stacksAll -> HudMain.stacksTick")
    K.check(PKG + "HudMain.stacksStep" in gr.get("HudMain.stacksTick", ()) and PKG + "HudMain.fillStacks" in gr.get("HudMain.stacksStep", ()), "S11 stacksTick -> stacksStep -> fillStacks")
    K.eq(PW.callers(gr, "Widgets.stkModelU", PKG), ["Widgets.model"], "S11 class:fn:stacks is asked only from the model")
    r = PW.reach(gr, "Widgets.stkModelU", PKG) | PW.reach(gr, "Widgets.stkBody", PKG) | PW.reach(gr, "HudMain.fillStacks", PKG) | PW.reach(gr, "Widgets.stkSample", PKG)
    # LayoutStore.get = the per-player layout CACHE (a file read only on a cache miss - the HUD build fills it); the 1 s fill reads it the same way
    K.check(PKG + "LayoutStore.get" in gr.get("HudMain.fill", ()), "S11 HudMain.fill reads the layout through LayoutStore.get too (the cache)")
    bad = sorted(m_ for m_ in r if m_ != "LayoutStore.get" and any(c in PW.IO_TARGETS or c in PW.SLEEP for c in gr.get(m_, ())))
    K.check(not bad, "S11 the Stacks code reaches no file / sleep (besides the cached LayoutStore.get): %s" % bad)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyHud", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("r28", run_r28), ("stacks", run_stacks)], script=__file__)
