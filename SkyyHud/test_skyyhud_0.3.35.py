"""SkyyHud 0.3.35 harness - UI round R1 part A: the Keys widget (ALT - Menu beside the hotbar) + the Quest Tracker fold + hud:fn:questFold
(research/UI-Queue-Spec.md items 1 + 2; tools/hud_0_3_35_patch.py). Built on tools/harness_kit.py: each phase a fresh child JVM (the game's
JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.35.py [--jar SkyyHud-0.3.35.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.34 -> 0.3.35: exactly the listed classes / members differ (+ the new class QuestFoldFn)
  K35  EXECUTED on the real jar classes:
       KEYS   the id APPENDED, label, built-in spot b 330,14 (64 x 56, Background OFF), a multi widget; the flag menu:walkkey:<uuid>: none /
              "0" / "x" = hidden (Y0, nothing in the HUD document), "1" / TRUE = shown (Y1); HudMain.build draws #SkyyWKeys with the vanilla
              cap (Common/InputBinding.png, Border 6), the ALT + Menu labels, fill sets "ALT" / "Menu"; a flag change = a shape change (the
              1 s fill asks for a re-send), the same flag = no set at all; the editor / Settings sample while hidden; every scale fits the box
       PLACE  keysPlace: a new player (built-in Abilities br 460,21 in the way) -> the first free spot (b -330,14); a player whose widgets
              leave b 330 free keeps it; a saved Keys line never moves; nothing free -> the built-in spot
       FOLD   questFold on real quest:fn:hud models: open = the very same model; folded = "QF", the header + count, the hint row ("Crouch x2
              to open" with menu:crouch:<uuid> = "fold", else "/quests widget fold to open"), the cached model untouched; questBody of a
              folded tracker: gold header, the hint row, no task / bar / arrow labels; questH = the empty-state height; the HUD build of a
              folded layout draws it, unfolding = another shape (one re-send)
       FN     hud:fn:questFold (QuestFoldFn) on a scratch layouts folder: bad args / unknown op / SkyyHud stopping = FALSE; toggle + fold
              without SkyyQuests = FALSE; toggle open -> folded -> open (saved: a fresh read of the file agrees; field 11 "0"); hide -> OFF,
              toggle on a hidden one = FALSE + stays hidden (fix 2); fold; show = ON + OPEN; "state"; a String uuid; a player with a HUD gets the re-send
              (the HUD's Quest shape follows)
       SET    Settings > HUD > Quest Tracker: the Tracker Open / Folded row (bound opton / optoff), the clicks save opt; the WLayout line:
              an old line = OPEN, a folded one writes field 11 "0" and round-trips
  LIVE twice on a scratch COPY of the live Skyy_SkyyHud (NewBetaTest): nothing written either time, every saved line loads as saved, every
       Quest tracker OPEN, the Keys spot of each player printed
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the key cap's look on the HUD (a texture Background on a HUD Group - vanilla's ToolsLegends HUD
uses the same), where the vanilla hotbar ends at the player's UI scale, the fold re-send look.
Scratch: tools/dev/scratch/uir1a/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK
import skyybuild as B

VERSION, PREV = "0.3.35", "0.3.34"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "uir1a", "h")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyHud")


def run_k35(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    UUID, System, CHM, Paths = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    Integer, Double, Boolean, String = JClass("java.lang.Integer"), JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.String")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
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
    WL, Wid, LS, HM, Cfg, HT, Plugin, Feed, QF = (H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("HudCfg"), H("HudThreads"),
                                                   H("SkyyHudPlugin"), H("Feed"), H("QuestFoldFn"))
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, "k")
    os.makedirs(os.path.join(work, "cfg"), exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(work, "cfg", "config.properties"))
    Cfg.load()
    HT.EXEC = None
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    mFill = HM.class_.getDeclaredMethod("fill", UCB.class_, JClass("boolean"))
    mFill.setAccessible(True)

    def use_dir(name):
        d = os.path.join(work, name)
        os.makedirs(os.path.join(d, "layouts"), exist_ok=True)
        LS.DIR = Paths.get(os.path.join(d, "layouts"))
        LS.CACHE.clear()
        return d

    def pref(n, name="Mia"):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID(0x335, n))
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

    def fill(h):
        b = UCB()
        re_ = bool(mFill.invoke(h, b, False))
        return re_, cmds(b)

    def group(cm, wid):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and ("Group #SkyyW%s " % wid) in c[3]]
        return g[0] if len(g) == 1 else None
    mlist = lambda m: [None if x is None else str(x) for x in m]

    # ================================================================================== KEYS
    ids = [str(x) for x in Wid.IDS]
    K.check(ids[-2:] == ["Stacks", "Keys"], "KEYS: Keys APPENDED to Widgets.IDS: %s" % ids[-3:])
    d = wdef("Keys")
    K.eq((bool(d.en), str(d.anchor), int(d.dx), int(d.dy), int(d.scale), int(d.bw), int(d.bh), bool(d.bg)), (True, "b", 330, 14, 100, 64, 56, False),
         "KEYS: built-in spot b 330,14, 64 x 56, ON, Background OFF")
    K.eq(str(Wid.label("Keys")), "Key hints", "KEYS: label")
    K.check(bool(Wid.multi("Keys")) and not bool(Wid.bgDef("Keys")), "KEYS: a multi widget, Background OFF by default")
    use_dir("keys")
    pr = pref(1)
    u = pr.getUuid()
    l = LS.get(u).get("Keys")
    for v, want in ((None, "Y0"), ("0", "Y0"), ("x", "Y0"), ("1", "Y1"), (Boolean.TRUE, "Y1"), (Boolean.FALSE, "Y0")):
        if v is None:
            bridge.remove("menu:walkkey:" + str(u))
        else:
            bridge.put("menu:walkkey:" + str(u), v)
        m = Wid.modelL("Keys", pr, l)
        K.eq((str(m[0]), m[1] is not None), (want, want == "Y1"), "KEYS: flag %r -> %s" % (v if v is None else str(v), want))
    bridge.remove("menu:walkkey:" + str(u))
    h, cm = hud(pr)
    K.check(group(cm, "Keys") is None and str(h.shape.get("Keys")) == "Y0", "KEYS: no flag - nothing in the HUD document (shape Y0 tracked)")
    re_, fc = fill(h)
    K.check(not re_ and not [c for c in fc if c[1] and "SkyyWKeys" in c[1]], "KEYS: the 1 s fill with the same (no) flag: no re-send, no set")
    bridge.put("menu:walkkey:" + str(u), "1")
    re_, fc = fill(h)
    K.check(re_, "KEYS: the flag turns 1 -> the 1 s fill asks for the re-send (shape Y0 -> Y1)")
    h, cm = hud(pr)
    g = group(cm, "Keys")
    K.check(g is not None and 'Background: (TexturePath: "Common/InputBinding.png", Border: 6)' in g,
            "KEYS: shown - #SkyyWKeys with the vanilla key cap (Common/InputBinding.png, Border 6)")
    K.check(g is not None and "#SkyyWKeysCap " in g and "#SkyyWKeysKTxt " in g and "#SkyyWKeysTTxt " in g and "_" not in "".join(
        x.split()[0] for x in g.split("#")[1:]), "KEYS: the ids #SkyyWKeysCap / KTxt / TTxt (no underscores)")
    K.check(g is not None and "#ccd8e8" in g and "#96a9be" in g and "Anchor: (Bottom: 14, " in g and "Width: 64, Height: 56" in g,
            "KEYS: cap text #ccd8e8, caption #96a9be, the box 64 x 56 at the bottom: %s" % (g or "")[:160])
    st = sets(cm)
    K.eq((st.get("#SkyyWKeysKTxt.Text"), st.get("#SkyyWKeysTTxt.Text")), ("ALT", "Menu"), "KEYS: the first fill sets ALT / Menu")
    re_, fc = fill(h)
    K.check(not re_ and not [c for c in fc if c[1] and "SkyyWKeys" in c[1]], "KEYS: a quiet second: nothing sent (never updated periodically)")
    bridge.put("menu:walkkey:" + str(u), "0")
    re_, _fc = fill(h)
    K.check(re_, "KEYS: the flag turns 0 -> re-send (hidden again)")
    v = Wid.viewModel("Keys", pr, l)
    K.eq((str(v[0]), str(v[1]), str(v[2]), str(v[3])), ("S", "ALT - Menu", "ALT", "Menu"), "KEYS: the editor / Settings stand-in while hidden")
    for sc in (50, 75, 100, 125, 150, 200):
        ls = WL.parse("1,b,330,14,%d,0" % sc, wdef("Keys"))
        src = str(Wid.multiWidgetSrcW("Keys", ls, Wid.keysModelOf(True), int(Wid.multiW("Keys", ls, Wid.keysModelOf(True), sc, 6))))
        w_, h_ = int(Wid.multiW("Keys", ls, Wid.keysModelOf(True), sc, 6)), int(Wid.bodyH("Keys", Wid.keysModelOf(True), sc))
        K.check(w_ == 64 * sc // 100 and h_ == 56 * sc // 100 and src.count("{") == src.count("}"), "KEYS: scale %d -> %d x %d, balanced markup" % (sc, w_, h_))
    ls = WL.parse("1,b,330,14,100,0,def,1,0,1,gold", wdef("Keys"))
    src = str(Wid.multiWidgetSrcW("Keys", ls, Wid.keysModelOf(True), 64))
    K.check(src.count("#SkyyWKeysKG") == 8 and src.count("#SkyyWKeysTG") == 8, "KEYS: glow on = 8 glow copies per text (setText's G0-G7)")

    # ================================================================================== PLACE
    use_dir("place")
    pn = pref(2)
    mp = LS.get(pn.getUuid())
    kp = mp.get("Keys")
    K.eq((str(kp.anchor), int(kp.dx), int(kp.dy)), ("b", -330, 14), "PLACE: a new player (built-in Abilities br 460,21 in the way) -> b -330,14")
    K.check(kp is not wdef("Keys"), "PLACE: ... on a COPY (the shared default untouched: dx %d)" % int(wdef("Keys").dx))
    lay = os.path.join(work, "place", "layouts")
    pf = pref(3)
    open(os.path.join(lay, str(pf.getUuid()) + ".properties"), "w").write("Abilities=1,br,10,231,110,0\n")
    LS.CACHE.clear()
    kf = LS.get(pf.getUuid()).get("Keys")
    K.eq((str(kf.anchor), int(kf.dx), int(kf.dy)), ("b", 330, 14), "PLACE: Abilities moved away (no Keys line) -> the built-in b 330,14 stays")
    ps = pref(4)
    open(os.path.join(lay, str(ps.getUuid()) + ".properties"), "w").write("Keys=1,b,330,14,100,0\n")
    LS.CACHE.clear()
    ks = LS.get(ps.getUuid()).get("Keys")
    K.eq((str(ks.anchor), int(ks.dx), int(ks.dy)), ("b", 330, 14), "PLACE: a saved Keys line is never moved (even with Abilities in the way)")
    pb = pref(5)
    big = "".join("%s=1,b,%d,%d,200,0\n" % (w_, dx_, dy_) for w_, dx_, dy_ in (("Coords", 0, 8), ("Zone", 0, 120), ("Gclock", -500, 8), ("Day", 500, 8)))
    open(os.path.join(lay, str(pb.getUuid()) + ".properties"), "w").write(big)
    LS.CACHE.clear()
    kb = LS.get(pb.getUuid()).get("Keys")
    K.check(str(kb.anchor) == "b" and int(kb.dy) in (14, 80), "PLACE: widgets all over the bottom -> a free try or the built-in spot (%s %d,%d)" % (kb.anchor, kb.dx, kb.dy))

    # ================================================================================== FOLD
    def qtask(name, prog="", frac=None, where="", d_=-1, done=False):
        return [String(name), String(prog), None if frac is None else Double(frac), String(where), Integer(d_), Boolean(done)]

    def qmodel(title, count, tasks):
        a = [String(title), String(count)]
        for t in tasks:
            a.extend(t)
        return JArray(JObject)(a)
    full = qmodel("Getting Started", "3 / 24", [qtask("Chop 10 logs", "6/10", 0.6, "NE  42 m", 1), qtask("Craft a workbench"), qtask("Mine stone", "0/2")])
    m0 = Wid.questModelOf(full)
    K.check(Wid.questFold(m0, True, u) is m0 or Wid.questFold(m0, True, u).equals(m0), "FOLD: open -> the very same model")
    bridge.remove("menu:crouch:" + str(u))
    f = Wid.questFold(m0, False, u)
    K.eq((str(f[0]), str(f[1]), str(f[2]), str(f[3]), str(f[4]), str(f[8]), str(f[9])),
         ("QF", "Getting Started", "Getting Started", "3 / 24", "E", "/quests widget fold to open", "-1"), "FOLD: folded = QF, header + count + the command hint")
    K.check(str(m0[0]).startswith("Q3") and str(m0[5]) == "Chop 10 logs", "FOLD: the cached model is untouched (%s)" % m0[0])
    bridge.put("menu:crouch:" + str(u), "fold")
    K.eq(str(Wid.questFold(m0, False, u)[8]), "Crouch x2 to open", "FOLD: menu:crouch = fold -> the crouch hint")
    bridge.put("menu:crouch:" + str(u), "menu")
    K.eq(str(Wid.questFold(m0, False, u)[8]), "/quests widget fold to open", "FOLD: menu:crouch = menu -> the command hint")
    hid = Wid.questModelOf(None)
    K.check(Wid.questFold(hid, False, u) is hid or str(Wid.questFold(hid, False, u)[0]) == "Q0", "FOLD: a hidden model stays hidden")
    K.check(Wid.questFold(None, False, u) is None, "FOLD: null is safe")
    lq = WL.parse("1,tl,8,42,100,1,def,1,0,0,def,0", wdef("Quest"))
    K.check(not bool(lq.opt) and not bool(Wid.optOf("Quest", lq)), "FOLD: field 11 '0' = opt false = folded")
    body = str(Wid.questBody("SkyyWQuest", lq, 100, f, 6, 300))
    K.check("#E8A93B" in body and "#SkyyWQuestHTxt " in body and "#SkyyWQuestW0Txt " in body and "#SkyyWQuestN0Txt" not in body
            and "Bar0" not in body and "#SkyyWQuestA0 " not in body, "FOLD: questBody folded = gold header + hint row, no task / bar / arrow")
    e0 = Wid.questModelOf(qmodel("No quest", "", []))
    K.eq(int(Wid.questH(f, 100)), int(Wid.questH(e0, 100)), "FOLD: questH folded = the empty-state height (%d)" % int(Wid.questH(f, 100)))
    K.check(int(Wid.questH(f, 100)) < int(Wid.questH(m0, 100)), "FOLD: ... smaller than the open tracker (%d < %d)" % (int(Wid.questH(f, 100)), int(Wid.questH(m0, 100))))
    eb = str(Wid.questBody("SkyyWQuest", lq, 100, e0, 6, 300))
    K.check("#96a9be" in eb, "FOLD: the real empty state keeps its grey header")
    pairs = [str(x) for x in Wid.pairsSc("Quest", f, 100, True)]
    K.check(pairs[:4] == ["H", "Getting Started", "C", "3 / 24"] and "W0" in pairs, "FOLD: the texts of a folded tracker: %s" % pairs[:8])
    # ---- fix pass 3: the Open-state footer hint while the choice is Fold
    bridge.remove("menu:crouch:" + str(u))
    K.check(Wid.questFold(m0, True, u).equals(m0) and len(Wid.questFold(m0, True, u)) == 23, "FIX3: open, no crouch flag -> no hint (the very same model)")
    bridge.put("menu:crouch:" + str(u), "menu")
    K.check(len(Wid.questFold(m0, True, u)) == 23, "FIX3: open, choice Open the menu -> no hint")
    bridge.put("menu:crouch:" + str(u), "fold")
    oh = Wid.questFold(m0, True, u)
    K.check(len(oh) == 24 and str(oh[23]) == "Crouch x2: fold - /quests widget hide" and str(oh[0]) == str(m0[0]) + "h"
            and [str(x) if x is not None else None for x in list(oh)[1:23]] == [str(x) if x is not None else None for x in list(m0)[1:23]],
            "FIX3: open + choice Fold -> a copy with the footer hint, shape + h (%s)" % oh[0])
    K.check(len(m0) == 23 and not str(m0[0]).endswith("h"), "FIX3: ... the cached model untouched")
    K.check(Wid.questFold(e0, True, u) is e0 or len(Wid.questFold(e0, True, u)) == 23, "FIX3: the empty state gets no hint")
    K.eq(int(Wid.questH(oh, 100)), int(Wid.questH(m0, 100)) + 8 + 15, "FIX3: questH + the gap and one 15 px row")
    for _sc in (50, 75, 100, 150, 200):
        K.check(int(Wid.questH(oh, _sc)) > int(Wid.questH(m0, _sc)), "FIX3: questH grows at scale %d" % _sc)
    ob = str(Wid.questBody("SkyyWQuest", lq, 100, oh, 6, 300))
    K.check("#SkyyWQuestF0Txt " in ob and "#7f93a6" in ob and "#SkyyWQuestN0Txt " in ob and ob.count("{") == ob.count("}"),
            "FIX3: questBody draws the footer row #SkyyWQuestF0 in caption #7f93a6 under the tasks")
    K.check("#SkyyWQuestF0Txt" not in str(Wid.questBody("SkyyWQuest", lq, 100, m0, 6, 300)), "FIX3: ... and none without the hint")
    op_ = [str(x) for x in Wid.pairsSc("Quest", oh, 100, True)]
    K.check("F0" in op_ and op_[op_.index("F0") + 1] == "Crouch x2: fold - /quests widget hide" and "F0L1" not in op_, "FIX3: the hint text pair F0 (one row)")
    op50 = [str(x) for x in Wid.pairsSc("Quest", oh, 50, True)]
    K.check("F0" in op50 and "F0L1" not in op50, "FIX3: at 50 %% still one row (cut to fit): %r" % op50[op50.index("F0") + 1])
    K.check(str(Wid.shapeOf("Quest", oh, lq)) != str(Wid.shapeOf("Quest", m0, lq)), "FIX3: the hint changes the shape (one re-send when it comes / goes)")
    bridge.remove("menu:crouch:" + str(u))

    @JImplements("java.util.function.Function")
    class QHud(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, a):
            return self.ans
    # the HUD build of a folded layout, then unfolded
    use_dir("fold")
    pq = pref(6)
    uq = pq.getUuid()
    bridge.put("quest:fn:hud", QHud(full))
    bridge.put("quest:epoch:" + str(uq), JClass("java.lang.Long")(1))
    LS.get(uq).get("Quest").opt = False
    h, cm = hud(pq)
    gq = group(cm, "Quest")
    K.check(gq is not None and str(h.shape.get("Quest")).startswith("QF"), "FOLD: HudMain.build of a folded layout: shape %s" % h.shape.get("Quest"))
    K.check(gq is not None and "#SkyyWQuestN0Txt" not in gq and "#SkyyWQuestW0Txt " in gq, "FOLD: ... the folded markup (no task rows)")
    st = sets(cm)
    K.eq((st.get("#SkyyWQuestHTxt.Text"), st.get("#SkyyWQuestCTxt.Text")), ("Getting Started", "3 / 24"), "FOLD: ... header + count set")
    # fix pass 5 (rejected): the folded hint follows the choice through the 1 s fill - a .Text set, no re-send
    bridge.put("menu:crouch:" + str(uq), "fold")
    re_, fc5 = fill(h)
    K.check(not re_ and sets(fc5).get("#SkyyWQuestW0Txt.Text") == "Crouch x2 to open", "FIX5: choice -> Fold while folded: the 1 s fill sets the crouch hint (%s)" % sets(fc5).get("#SkyyWQuestW0Txt.Text"))
    bridge.put("menu:crouch:" + str(uq), "off")
    re_, fc5 = fill(h)
    K.check(not re_ and sets(fc5).get("#SkyyWQuestW0Txt.Text") == "/quests widget fold to open", "FIX5: choice -> Nothing: back to the command hint")
    LS.get(uq).get("Quest").opt = True
    re_, _fc = fill(h)
    K.check(re_, "FOLD: unfolding = another shape (the 1 s fill asks for ONE re-send)")
    # fix pass 3 on the real HUD: an open tracker + the choice Fold draws the footer; the choice changing = one re-send
    bridge.put("menu:crouch:" + str(uq), "fold")
    h3, cm3 = hud(pq)
    g3 = group(cm3, "Quest")
    K.check(g3 is not None and "#SkyyWQuestF0Txt " in g3 and sets(cm3).get("#SkyyWQuestF0Txt.Text") == "Crouch x2: fold - /quests widget hide",
            "FIX3: HudMain.build of an open tracker (choice Fold) draws + sets the footer hint")
    re_, _fc = fill(h3)
    K.check(not re_, "FIX3: a quiet second: no re-send")
    bridge.put("menu:crouch:" + str(uq), "menu")
    re_, _fc = fill(h3)
    K.check(re_, "FIX3: the choice -> Open the menu: the hint goes = ONE re-send")
    bridge.remove("menu:crouch:" + str(uq))

    # ================================================================================== FN
    use_dir("fn")
    lay = os.path.join(work, "fn", "layouts")
    plugin = U.allocateInstance(Plugin.class_)
    setf(plugin, Plugin, "huds", CHM())
    fn = QF()
    pz = pref(7)
    uz = pz.getUuid()
    bridge.remove("quest:fn:hud")
    A = lambda *a: JArray(JObject)(list(a))
    Feed.PLUGIN = None
    K.eq(bool(fn.apply(A(uz, String("open")))), False, "FN: SkyyHud stopping (Feed.PLUGIN null) -> FALSE")
    Feed.PLUGIN = plugin
    for arg, what in ((None, "null"), (String("x"), "not an array"), (A(uz), "one element"), (A(uz, Integer(3)), "op not a String"),
                      (A(String("not-a-uuid"), String("open")), "bad uuid"), (A(uz, String("explode")), "unknown op")):
        K.eq(bool(fn.apply(arg)), False, "FN: %s -> FALSE" % what)
    K.eq((bool(fn.apply(A(uz, String("toggle")))), bool(fn.apply(A(uz, String("fold"))))), (False, False),
         "FN: toggle / fold without SkyyQuests (quest:fn:hud) -> FALSE (SkyyMenu falls back)")
    bridge.put("quest:fn:hud", QHud(full))

    def state():
        return str(fn.apply(A(uz, String("state"))))

    def fresh():
        LS.CACHE.clear()
        return LS.get(uz).get("Quest")
    # fix pass 1: SkyyQuests on but no quest showing -> toggle / fold = FALSE (SkyyMenu opens the Menu), nothing changed or saved
    bridge.put("quest:fn:hud", QHud(None))
    K.eq((bool(fn.apply(A(uz, String("toggle")))), bool(fn.apply(A(uz, String("fold"))))), (False, False),
         "FIX1: toggle / fold with no quest on the tracker -> FALSE (the double tap opens the Menu)")
    K.check(state() == "open" and not os.path.exists(os.path.join(lay, str(uz) + ".properties")), "FIX1: ... nothing changed, nothing saved")
    fn.apply(A(uz, String("hide")))
    K.eq((bool(fn.apply(A(uz, String("toggle")))), state()), (False, "hidden"), "FIX1: a hidden tracker with no quest stays hidden on a double tap")
    K.eq(bool(fn.apply(A(uz, String("show")))), True, "FIX1: show / hide still work without a quest")
    bridge.put("quest:fn:hud", QHud(full))
    K.eq(state(), "open", "FN: a new player's tracker is open")
    K.eq(bool(fn.apply(A(uz, String("toggle")))), True, "FN: toggle -> TRUE")
    K.eq(state(), "folded", "FN: ... folded")
    fl = open(os.path.join(lay, str(uz) + ".properties"), encoding="latin-1").read()
    K.check("Quest=1,tl,8,42,100,1,def,1,0,0,def,0" in fl, "FN: ... saved: the Quest line carries field 11 '0' (%s)" % [x for x in fl.split("\n") if x.startswith("Quest=")])
    K.check(not bool(fresh().opt), "FN: ... a fresh read of the file = folded")
    fn.apply(A(uz, String("toggle")))
    K.eq((state(), bool(fresh().opt)), ("open", True), "FN: toggle again -> open (saved)")
    fn.apply(A(uz, String("hide")))
    K.eq((state(), bool(fresh().en)), ("hidden", False), "FN: hide -> the widget OFF (saved)")
    K.eq((bool(fn.apply(A(uz, String("toggle")))), state(), bool(fresh().en)), (False, "hidden", False),
         "FIX2b: toggle on a hidden tracker (quest showing) -> FALSE, stays hidden, nothing saved (the double tap opens the Menu)")
    fn.apply(A(uz, String("fold")))
    K.eq(state(), "folded", "FN: fold")
    fn.apply(A(uz, String("fold")))
    K.eq(state(), "folded", "FN: fold twice stays folded")
    fn.apply(A(uz, String("hide")))
    fn.apply(A(uz, String("show")))
    K.eq((state(), bool(fresh().en), bool(fresh().opt)), ("open", True, True), "FN: show = ON + OPEN (saved)")
    fn.apply(A(uz, String(" FOLD ")))
    K.eq(state(), "folded", "FN: ops ignore case and spaces")
    fn.apply(A(String(str(uz)), String("open")))
    K.eq(state(), "open", "FN: a String uuid works")
    # a player with a HUD gets the re-send: the HUD's Quest shape follows the fold
    hz = HM(pz)
    plugin.huds.put(uz, hz)
    bridge.put("quest:epoch:" + str(uz), JClass("java.lang.Long")(2))
    fn.apply(A(uz, String("fold")))
    K.check(str(hz.shape.get("Quest")).startswith("QF"), "FN: fold re-sends the player's HUD (HudMain.rebuild): Quest shape %s" % hz.shape.get("Quest"))
    fn.apply(A(uz, String("open")))
    K.check(str(hz.shape.get("Quest")).startswith("Q3"), "FN: open re-sends it: Quest shape %s" % hz.shape.get("Quest"))
    fn.apply(A(uz, String("hide")))
    K.check(hz.shape.get("Quest") is None, "FN: hide re-sends it without the tracker")
    K.check(int(QF.CALLS.get()) > 20, "FN: the call counter counts (%d)" % int(QF.CALLS.get()))

    # ================================================================================== SET
    SP = H("SettingsPage")
    me = pref(8, "Bo")
    um = me.getUuid()
    LS.CACHE.clear()
    LS.get(um)
    sp = SP(me, plugin, "Quest")
    b, ev = UCB(), UEB()
    sp.build(None, b, ev, None)
    cm = cmds(b)
    evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data)] for e in ev.getEvents()]
    txt = " ".join(c[3] or "" for c in cm)
    K.check('Text: "Tracker"' in txt and 'Text: "Open"' in txt and 'Text: "Folded"' in txt and "Folded shows the quest name and count only" in txt,
            "SET: the Quest Tracker settings show the Tracker Open / Folded row")
    bnd = dict((e[1], e[2]) for e in evs)
    K.check("opton" in str(bnd.get("#SkyySetOptOn")) and "optoff" in str(bnd.get("#SkyySetOptOff")), "SET: ... both bound (opton / optoff)")
    SP(me, plugin, "Quest").handleDataEvent(None, None, '{"a":"optoff"}')
    LS.CACHE.clear()
    K.check(not bool(LS.get(um).get("Quest").opt), "SET: Folded click -> saved folded (a fresh read)")
    SP(me, plugin, "Quest").handleDataEvent(None, None, '{"a":"opton"}')
    LS.CACHE.clear()
    lq2 = LS.get(um).get("Quest")
    K.check(bool(lq2.opt) and not bool(lq2.optH), "SET: Open click -> saved open, optH untouched")
    old = WL.parse("1,tl,8,42,100,1", wdef("Quest"))
    K.check(bool(old.opt) and str(old.ser()) == "1,tl,8,42,100,1", "SET: an old Quest line = OPEN and writes back unchanged")
    old.opt = False
    K.eq(str(old.ser()), "1,tl,8,42,100,1,def,1,0,0,def,0", "SET: folded writes field 11 '0'")
    K.check(not bool(WL.parse(str(old.ser()), wdef("Quest")).opt), "SET: ... and round-trips")
    sp2 = SP(me, plugin, "Keys")
    b2, ev2 = UCB(), UEB()
    sp2.build(None, b2, ev2, None)
    K.check(len(cmds(b2)) > 10 and str(sp2.previewText()) == "ALT - Menu", "SET: the Key hints settings page builds; preview %r" % str(sp2.previewText()))
    Feed.PLUGIN = None
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    LS, Cfg, Pub, Wid = P("LayoutStore"), P("HudCfg"), P("CfgPub"), P("Widgets")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    lyd = os.path.join(home, "layouts")
    players = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []
    res = []
    for _n in range(2):
        b0 = HK.tree_hash(mods)
        LS.CACHE.clear()
        LS.DIR = Paths.get(lyd)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Wid.HUBFILE = Paths.get(os.path.join(mods, "Skyy_SkyyIslands", "hub.properties"))
        Cfg.load()
        Pub.start(Paths.get(mods), None)
        r_ = {}
        for us in players:
            mp = LS.get(UUID.fromString(us))
            r_[us] = dict((str(w_), str(mp.get(w_).ser())) for w_ in Wid.IDS)
        Pub.flush()
        a0 = HK.tree_hash(mods)
        res.append((r_, sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))))
    K.check(res[0][1] == [] and res[1][1] == [] and res[0][0] == res[1][0],
            "LIVE: two starts on a COPY of the live Skyy_SkyyHud (%d layouts): nothing written, the same layouts: %s" % (len(players), [r[1] for r in res]))
    bad, folded = [], []
    for us in players:
        fl = {}
        for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                k_, v_ = ln.strip().split("=", 1)
                fl[k_] = v_
        r_ = res[0][0][us]
        if not all(r_[w_] == fl[w_] for w_ in r_ if w_ in fl):
            bad.append(us[:8])
        mp = LS.get(UUID.fromString(us))
        if not bool(mp.get("Quest").opt):
            folded.append(us[:8])
        kk = mp.get("Keys")
        K.notes.append("LIVE: player %s...: Keys at %s %d,%d (saved Keys line: %s)" % (us[:8], kk.anchor, kk.dx, kk.dy, "Keys" in fl))
    K.check(not bad, "LIVE: every saved line of every live layout loads exactly as saved (%d players): %s" % (len(players), bad))
    K.check(not folded, "LIVE: every live Quest tracker loads OPEN (no old line reads as folded): %s" % folded)
    K.check(len(players) >= 1, "LIVE: the copy has layouts (%d)" % len(players))
    K.save()


EXPECT = {
    "Widgets": ["+m keysBody", "+m keysModelOf", "+m keysModelU", "+m keysOn", "+m keysPlace", "+m keysSample", "+m questCrouch", "+m questFold", "+m questFoldHint",
                "~<clinit>", "~m bodyH", "~m def0", "~m label", "~m linePairs", "~m model", "~m multi", "~m multiBody", "~m multiW",
                "~m questBody", "~m questH", "~m questPairs", "~m sampleU"],     # questH / questPairs: the fix-pass Open-state hint row     # <clinit> / def0 / label: the Keys id, spot and label tables
    "LayoutStore": ["~m get"],                     # the Keys first spot (keysPlace) for a file without a Keys line
    "SettingsPage": ["~m build", "~m previewText"],  # the Quest Tracker's Open / Folded row; the Keys preview text
    "SkyyHudPlugin": ["~m setup"],                 # hud:fn:questFold published
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],   # the config kit's version text
}
if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, ["QuestFoldFn"], [("k35", run_k35), ("live", run_live)], os.path.abspath(__file__),
           live=(LIVE_DIR, "Skyy_SkyyHud"))
