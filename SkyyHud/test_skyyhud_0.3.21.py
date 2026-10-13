"""SkyyHud 0.3.21 harness - THE QUEST WIDGET round (tools/hud_0_3_21_patch.py). Built on tools/harness_kit.py: each phase a fresh child JVM
(the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder). Every new code path runs on the real
jar classes (real HudMain.build / fill, the real Widgets model / markup / cut / placement); only the player and quest:fn:hud are stand-ins.

    python SkyyHud/test_skyyhud_0.3.21.py [--jar SkyyHud-0.3.21.jar] [--old SkyyHud-0.3.20.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.20 -> 0.3.21: exactly the listed classes / members differ; non-class entries: the manifest
  X20  the 0.3.20 harness's exec phase (E0-E10 + FIX: the feed, the XP flash, routing, the default spots ...) on THIS jar; the checks that
       list the widget ids / a new player's saved lines are re-checked with Quest appended (eased, then checked exactly here)
  X19  the 0.3.19 exec checks (through the 0.3.20 harness's x19 wrapper) on THIS jar, eased the same way
  Q    quest    Q1 the id (APPENDED), the built-in spot tl 8,42 300 x 149, the label; Q2 no SkyyQuests = hidden + the "Needs SkyyQuests 0.1"
                stand-in, the sample with it; Q3 the model from quest:fn:hud + the EPOCH CACHE (one call per epoch, none per tick); Q4 the
                markup (box, hairline, header, task 1 with the ProgressBar + 8 arrow containers - exactly one visible -, tasks 2-3, no
                underscores, kit colours) and the first fill (cut texts, bar Value, arrow .Visible); Q5 the tick's fill: same shape = only
                .Text / .Value / .Visible sets (direction change included), a done task / a task count / an arrow appearing = the shape
                re-send; Q6 the heights 149 / 124 / 99 / 67 and every size 50-200 % (bodyH = the markup); Q7 long texts cut with "..." to
                their room; Q8 malformed answers = hidden; Q9 questPlace (a player whose widgets cover tl 8,42 gets a free spot; a saved
                Quest line never moves; the server default wins); Q10 the editor / Settings use the same cut texts (bytecode); Q11 the
                quest widget reaches no file / sleep and is only asked from modelL
  ST   live     the 0.3.20 harness's start-twice on a scratch COPY of the live Skyy_SkyyHud (nothing written, every saved line as saved)
                + Q12 every live layout: the Quest widget at the built-in spot or a free one, never touching that player's shown widgets
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): how the widget looks (pixel diamonds / arrows as Groups, the tight rows), .Visible on a Group
container inside a HUD document, the client's real font width vs the tables.
Scratch: tools/dev/scratch/quests01/hud (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION, PREV = "0.3.21", "0.3.20"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "quests01", "hud")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")
QLINE = "Quest=1,tl,8,42,100,1"
EXPECT = {}
ADDED = []


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ease(out, rules, label):
    """rules: [(fail-text fragment, extra condition on the text)] - a matching fail of an older harness becomes an ok + a note"""
    d = json.load(open(out))
    keep, eased = [], []
    for f in d["fails"]:
        if any(fr in f and cond(f) for fr, cond in rules):
            eased.append(f[:100])
        else:
            keep.append(f)
    d["fails"] = keep
    d["ok"] += len(eased)
    d.setdefault("notes", []).append("%s: %d check(s) eased for the appended Quest id (re-checked exactly in Q / here): %s" % (label, len(eased), eased))
    json.dump(d, open(out, "w"), indent=1)


def run_x20(out, jar, scratch, home):
    T20 = load_module(os.path.join(HERE, "test_skyyhud_0.3.20.py"), "hud0320h")
    T20.run_exec(out, jar, os.path.join(scratch, "x20"), home)
    ease(out, [("E0: Feed is APPENDED to Widgets.IDS", lambda f: "'Feed', 'Quest']" in f),
               ("E10: a NEW player's saved file vs 0.3.19's", lambda f: ("+['Abilities=1,br,460,21,100,1', 'Feed=1,bl,8,488,100,1', 'Guild=1,tl,8,324,100,1', 'Party=1,tl,8,200,100,1', '%s', 'Skills=1,tr,8,240,100,1']" % QLINE) in f)],
         "X20")


def run_x19(out, jar, scratch, home):
    T20 = load_module(os.path.join(HERE, "test_skyyhud_0.3.20.py"), "hud0320h")
    T20.run_x19(out, jar, scratch, home)
    ease(out, [("X1: HudThreads: no thread -> inline save", lambda f: "('SkyyHud-Tick', True)" in f and "(writes 1)" in f)], "X19")


def run_live(out, jar, scratch, home):
    T20 = load_module(os.path.join(HERE, "test_skyyhud_0.3.20.py"), "hud0320h")
    T20.run_live(out, jar, scratch, home)


def run_quest(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    UUID, System, CHM, Paths = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    Long, Integer, Double, Boolean = JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.Double"), JClass("java.lang.Boolean")
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
    WL, Wid, LS, HM, Cfg, HT = H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("HudCfg"), H("HudThreads")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, "q")
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
        setf(pr, PRef, "uuid", UUID(0x321, n))
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

    def qgroup(cm):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and "Group #SkyyWQuest " in c[3]]
        return g[0] if len(g) == 1 else None

    @JImplements("java.util.function.Function")
    class QFn(object):
        def __init__(self):
            self.ans = None
            self.calls = 0

        @JOverride
        def apply(self, u):
            self.calls += 1
            return self.ans

    def ans(title, count, *tasks):
        a = [title, count]
        for (nm, pg, fr, wh, dr, dn) in tasks:
            a += [nm, pg, None if fr is None else Double(fr), wh, Integer(dr), Boolean.TRUE if dn else Boolean.FALSE]
        return JArray(JObject)([JObject(x) if x is not None and not isinstance(x, str) else x for x in a])
    T3 = [("Chop 10 logs", "6/10", 0.6, "NE  42 m  -  Island 2", 1, False), ("Craft a crafting accessory", "", None, "", -1, False),
          ("Mine stone and copper", "0/2", 0.0, "", -1, False)]
    # ================================================================================== Q1 ids + the built-in spot
    ids = [str(x) for x in Wid.IDS]
    K.check(ids[-2:] == ["Feed", "Quest"], "Q1 Quest APPENDED to Widgets.IDS: %s" % ids[-3:])
    d = Wid.def_("Quest") if hasattr(Wid, "def_") else Wid.__getattribute__("def")("Quest")
    K.eq((bool(d.en), str(d.anchor), int(d.dx), int(d.dy), int(d.scale), int(d.bw), int(d.bh)), (True, "tl", 8, 42, 100, 300, 149), "Q1 the built-in spot tl 8,42, 300 x 149")
    K.eq(str(Wid.label("Quest")), "Quest Tracker", "Q1 label")
    K.check(bool(Wid.multi("Quest")), "Q1 a multi-line widget")
    # ================================================================================== Q2 no SkyyQuests
    use_dir("q2")
    pr = pref(1)
    u = pr.getUuid()
    l = LS.get(u).get("Quest")
    m = Wid.modelL("Quest", pr, l)
    K.eq(str(m[0]), "Q0", "Q2 no quest:fn:hud = hidden")
    h, cm = hud(pr)
    K.check(qgroup(cm) is None, "Q2 ... and nothing in the HUD document")
    v = Wid.viewModel("Quest", pr, l)
    K.eq((str(v[0]), str(v[2])), ("S", "Needs SkyyQuests 0.1"), "Q2 the editor / Settings stand-in")
    fn = QFn()
    bridge.put("quest:fn:hud", fn)
    v = Wid.viewModel("Quest", pr, l)
    K.eq((str(v[0]), str(v[2]), str(v[5])), ("S", "Getting Started", "Chop 10 logs"), "Q2 with SkyyQuests (nothing to show): the sample")
    # ================================================================================== Q3 model + the epoch cache
    fn.ans = ans("Getting Started", "3 / 24", *T3)
    bridge.put("quest:epoch:" + str(u), Long(1))
    c0 = int(Wid.QCALLS.get())
    m = Wid.modelL("Quest", pr, l)
    for _ in range(5):
        Wid.modelL("Quest", pr, l)
    K.eq(int(Wid.QCALLS.get()) - c0, 1, "Q3 one quest:fn:hud call for 6 reads of one epoch (none per tick)")
    K.eq([None if x is None else str(x) for x in m],
         ["Q3|0ba|0|0", "Getting Started", "Getting Started", "3 / 24", "3", "Chop 10 logs", "6/10", "0.600", "NE  42 m  -  Island 2", "1", "0",
          "Craft a crafting accessory", "", None, "", "-1", "0", "Mine stone and copper", "0/2", None, "", "-1", "0"], "Q3 the model")
    bridge.put("quest:epoch:" + str(u), Long(2))
    Wid.modelL("Quest", pr, l)
    K.eq(int(Wid.QCALLS.get()) - c0, 2, "Q3 a new epoch = one more call")
    # ================================================================================== Q4 markup + first fill
    h, cm = hud(pr)
    g = qgroup(cm)
    K.check(g is not None and "Anchor: (Top: 42, Left: 8, Width: 300, Height: 149)" in g and "Background: #0b1524(0.72)" in g, "Q4 the box: %s" % (None if g is None else g[:160]))
    K.check(g is not None and g.count("#E8A93B(0.45)") == 4 and "#E8A93B(0.35)" in g, "Q4 the gold hairline (4 x 1 px) + the gold line")
    for e in ("H", "C", "N0", "S0", "W0", "N1", "S1", "N2", "S2"):
        K.check(g is not None and ("Label #SkyyWQuest%sTxt " % e) in g, "Q4 label %s" % e)
    K.check(g is not None and "ProgressBar #SkyyWQuestBar0 " in g and "Value: 0.600" in g and '"Common/ProgressBar.png"' in g and '"Common/ProgressBarFill.png"' in g,
            "Q4 the vanilla ProgressBar (the Combat widget's textures)")
    arrows = re.findall(r"Group #SkyyWQuestA(\d) \{ Anchor: \([^)]*\); Visible: (true|false);", g or "")
    K.eq(sorted(arrows), sorted([(str(k), "true" if k == 1 else "false") for k in range(8)]), "Q4 8 arrow containers, A1 (NE) visible")
    ids_ = re.findall(r"#([A-Za-z0-9_]+)", g or "")
    K.check(ids_ and not [i for i in ids_ if "_" in i], "Q4 no underscores in element ids")
    for col in ("#E8A93B", "#878e9c", "#d6e4ee", "#ffffff", "#7caacc", "#96a9be"):
        K.check(g is not None and col in g, "Q4 mockup colour %s" % col)
    st = sets(cm)
    K.eq((st.get("#SkyyWQuestHTxt.Text"), st.get("#SkyyWQuestCTxt.Text"), st.get("#SkyyWQuestN0Txt.Text"), st.get("#SkyyWQuestS0Txt.Text"),
          st.get("#SkyyWQuestW0Txt.Text"), st.get("#SkyyWQuestN2Txt.Text")),
         ("Getting Started", "3 / 24", "Chop 10 logs", "6/10", "NE  42 m  -  Island 2", "Mine stone and copper"), "Q4 the first fill's texts")
    K.check(abs(float(st.get("#SkyyWQuestBar0.Value", -1)) - 0.6) < 1e-6, "Q4 the bar Value: %s" % st.get("#SkyyWQuestBar0.Value"))
    K.eq([st.get("#SkyyWQuestA%d.Visible" % k) for k in range(8)], [k == 1 for k in range(8)], "Q4 the arrow .Visible sets")
    # ================================================================================== Q5 the tick's fill
    def tickfill():
        b = UCB()
        re_ = bool(h.fill(b, False))
        return re_, cmds(b)
    c1 = int(Wid.QCALLS.get())
    re_, cm2 = tickfill()
    K.check(not re_ and not [c for c in cm2 if "SkyyWQuest" in str(c[1])] and int(Wid.QCALLS.get()) == c1, "Q5 an unchanged epoch: no call, no set for the quest widget")
    fn.ans = ans("Getting Started", "3 / 24", ("Chop 10 logs", "7/10", 0.7, "E  38 m  -  Island 2", 2, False), T3[1], T3[2])
    bridge.put("quest:epoch:" + str(u), Long(3))
    re_, cm2 = tickfill()
    s2 = sets(cm2)
    K.check(not re_ and not [c for c in cm2 if c[0] != "Set"], "Q5 progress + direction: Sets only, no re-send")
    K.eq((s2.get("#SkyyWQuestS0Txt.Text"), s2.get("#SkyyWQuestW0Txt.Text"), s2.get("#SkyyWQuestA1.Visible"), s2.get("#SkyyWQuestA2.Visible")),
         ("7/10", "E  38 m  -  Island 2", False, True), "Q5 the changed texts + the arrow swap")
    K.check(abs(float(s2.get("#SkyyWQuestBar0.Value", -1)) - 0.7) < 1e-6 and "#SkyyWQuestN0Txt.Text" not in s2, "Q5 the bar Value; unchanged texts not re-sent")
    for label, a_ in (("a done task", ans("Getting Started", "4 / 24", ("Chop 10 logs", "10/10", 1.0, "Done!  +50 Foraging XP", -1, True), T3[1], T3[2])),
                      ("2 tasks", ans("Getting Started", "4 / 24", T3[1], T3[2])),
                      ("the arrow appears", ans("Getting Started", "4 / 24", ("Craft a crafting accessory", "", None, "N  9 m  -  Bench", 0, False), T3[2]))):
        fn.ans = a_
        bridge.put("quest:epoch:" + str(u), Long(int(bridge.get("quest:epoch:" + str(u))) + 1))
        re_, _ = tickfill()
        K.check(re_, "Q5 %s = the shape re-send" % label)
        h, _ = hud(pr)
    # ================================================================================== Q6 heights
    for n_, hh in ((3, 149), (2, 124), (1, 99)):
        fn.ans = ans("T", "1 / 3", *T3[:n_])
        mm = Wid.questModelOf(fn.ans)
        K.eq(int(Wid.bodyH("Quest", mm, 100)), hh, "Q6 %d task(s) = %d px" % (n_, hh))
    me = Wid.questModelOf(ans("No active quests", ""))
    K.eq((str(me[0]), int(Wid.bodyH("Quest", me, 100)), str(me[8])), ("QE", 67, "Pick one at the quest board in the hub"), "Q6 the empty state")
    lq = LS.get(u).get("Quest")
    for sc in (50, 75, 100, 125, 150, 200):
        for mm in (Wid.questModelOf(ans("T", "1 / 3", *T3)), me):
            lq.scale = sc
            src = str(Wid.multiWidgetSrcW("Quest", lq, mm, int(Wid.multiW("Quest", lq, mm, sc, 6))))
            hh = int(Wid.bodyH("Quest", mm, sc))
            K.check(("Width: %d, Height: %d)" % (300 * sc // 100, hh)) in src, "Q6 size %d%%: the box %d x %d" % (sc, 300 * sc // 100, hh))
    lq.scale = 100
    # ================================================================================== Q7 cut to fit
    long_ = "Craft your very first crafting accessory and put it in the Accessory Bag"
    pm = Wid.questModelOf(ans("A very long quest line name that will not fit at all in the header", "12 / 240", (long_, "1/2", 0.5, "NE  420 m  -  The far away island past the sea", 1, False)))
    pairs = [str(x) for x in Wid.questPairs(pm, 100, True)]
    pd = dict(zip(pairs[0::2], pairs[1::2]))
    K.check(pd["N0"].endswith("...") and pd["H"].endswith("...") and pd["W0"].endswith("...") and pd["C"] == "12 / 240" and pd["S0"] == "1/2", "Q7 cut: %s" % pd)
    room = 300 - 20 - 14 - int(Wid.textW("1/2", 14, True)) - 8
    K.check(int(Wid.textW(pd["N0"], 14, True)) <= room, "Q7 the cut name fits its room (%d <= %d)" % (int(Wid.textW(pd["N0"], 14, True)), room))
    K.eq([str(x) for x in Wid.pairsSc("Combat", Wid.combatSample(), 100, True)], [str(x) for x in Wid.linePairs("Combat", Wid.combatSample())], "Q7 other widgets: pairsSc = linePairs")
    # ================================================================================== Q8 malformed answers
    for bad in (None, "x", JArray(JObject)([JObject("only one")]), JArray(JObject)([JObject(Integer(1)), JObject(Integer(2)), JObject(Integer(3))])):
        mm = Wid.questModelOf(bad)
        K.check(str(mm[0]) in ("Q0", "QE"), "Q8 a malformed answer = hidden / empty: %r -> %s" % (bad, mm[0]))
    mm = Wid.questModelOf(ans("T", "c", ("n", "p", 7.5, "w", 99, False)))
    K.eq((str(mm[7]), str(mm[9])), ("1.000", "-1"), "Q8 a frac above 1 is clamped, a dir outside -1..7 = none")
    # ================================================================================== Q9 questPlace
    d9 = use_dir("q9")
    lyd = os.path.join(d9, "layouts")
    u_cov, u_saved, u_def = UUID(0x321, 91), UUID(0x321, 92), UUID(0x321, 93)
    open(os.path.join(lyd, str(u_cov) + ".properties"), "w").write("Party=1,tl,8,60,100,1\n")
    open(os.path.join(lyd, str(u_saved) + ".properties"), "w").write("Party=1,tl,8,60,100,1\nQuest=1,tl,8,42,100,1\n")
    open(os.path.join(lyd, str(u_def) + ".properties"), "w").write("Coords=1,tl,8,8,100,1\n")
    snap = dict((f, open(os.path.join(lyd, f), "rb").read()) for f in os.listdir(lyd))
    mc, ms, md = LS.get(u_cov), LS.get(u_saved), LS.get(u_def)
    qc = mc.get("Quest")

    def box(m_, id_):
        l_ = m_.get(id_)
        w_ = int(l_.bw) * int(l_.scale) // 100
        h_ = int(Wid.hMax(l_))
        p_ = Wid.screenPosWH(l_, w_, h_)
        return (int(p_[0]), int(p_[1]), w_, h_)

    def touch(a, b, g=0):
        return a[0] < b[0] + b[2] + g and b[0] < a[0] + a[2] + g and a[1] < b[1] + b[3] + g and b[1] < a[1] + a[3] + g
    shown = [k for k in ids if k not in ("Quest", "Seasons") and bool(mc.get(k).en)]
    K.check((int(qc.dx), int(qc.dy)) != (8, 42) and not [k for k in shown if touch(box(mc, "Quest"), box(mc, k))],
            "Q9 a player whose saved Party covers tl 8,42: the Quest widget takes a free spot %s" % (box(mc, "Quest"),))
    K.eq((int(ms.get("Quest").dx), int(ms.get("Quest").dy)), (8, 42), "Q9 a saved Quest line never moves")
    K.eq((int(md.get("Quest").dx), int(md.get("Quest").dy)), (8, 42), "Q9 a free built-in spot is kept")
    K.eq(dict((f, open(os.path.join(lyd, f), "rb").read()) for f in os.listdir(lyd)), snap, "Q9 loading wrote nothing")
    # ================================================================================== Q10 / Q11 bytecode
    gr = PW.calls(jar)
    K.check(PKG + "Widgets.pairsSc" in gr.get("HudMain.fill", ()) and PKG + "Widgets.visPairs" in gr.get("HudMain.fill", ()), "Q10 HudMain.fill uses pairsSc + visPairs")
    K.check(any(PKG + "Widgets.pairsSc" in v for k, v in gr.items() if k.startswith("EditorPage.")), "Q10 the editor preview uses the same cut texts")
    K.eq(PW.callers(gr, "Widgets.questModelU", PKG), ["Widgets.model"], "Q11 quest:fn:hud is asked only from the model (the tick's modelL)")
    r = PW.reach(gr, "Widgets.questModelU", PKG) | PW.reach(gr, "Widgets.questBody", PKG) | PW.reach(gr, "Widgets.questPairs", PKG) | PW.reach(gr, "Widgets.questPlace", PKG)
    bad = sorted(m_ for m_ in r if any(c in PW.IO_TARGETS or c in PW.SLEEP for c in gr.get(m_, ())))
    K.check(not bad, "Q11 the quest widget code reaches no file / sleep: %s" % bad)
    # ================================================================================== Q12 every live layout (a COPY)
    if os.path.isdir(os.path.join(LIVE_DIR, "layouts")):
        dl = os.path.join(work, "live")
        shutil.copytree(os.path.join(LIVE_DIR, "layouts"), os.path.join(dl, "layouts"))
        LS.DIR = Paths.get(os.path.join(dl, "layouts"))
        LS.CACHE.clear()
        badq = []
        n = 0
        for f in sorted(os.listdir(os.path.join(dl, "layouts"))):
            if not f.endswith(".properties") or len(f) < 40:
                continue
            try:
                uu = UUID.fromString(f[:36])
            except Exception:
                continue
            n += 1
            mm_ = LS.get(uu)
            q = mm_.get("Quest")
            if not bool(q.en):
                continue
            sh = [k for k in ids if k not in ("Quest", "Seasons") and bool(mm_.get(k).en)]
            hits = [k for k in sh if touch(box(mm_, "Quest"), box(mm_, k))]
            K.notes.append("Q12 %s...: Quest at %s %d,%d%s" % (f[:8], q.anchor, int(q.dx), int(q.dy), " (touches %s - no free spot)" % hits if hits else ""))
            if hits and (int(q.dx), int(q.dy)) != (8, 42):
                badq.append(f[:8])
        K.check(not badq, "Q12 every live layout (%d): the Quest widget never lands on a moved spot that touches a widget: %s" % (n, badq))
    K.save()


EXPECT.update({
    "Widgets": ["+f QARO", "+f QARR", "+f QCACHE", "+f QCALLS", "+f QEMPTY", "+f QNEED", "+f QROWS", "+m pairsSc", "+m qArrows", "+m qDiamond", "+m qLine",
                "+m qRect", "+m qShape", "+m qStr", "+m questBody", "+m questH", "+m questHave", "+m questModelOf", "+m questModelU", "+m questPairs",
                "+m questPlace", "+m questRows", "+m questSample", "+m visPairs", "~<clinit>", "~m barPairs", "~m bodyH", "~m def", "~m label",
                "~m linePairs", "~m model", "~m multi", "~m multiBody", "~m multiW", "~m sampleU"],
    "LayoutStore": ["~m get"],
    "HudMain": ["~m fill"],
    "SettingsPage": ["~m previewText"],
    "EditorPage": ["~m appendPreviews"],
    # the version string (the config kit's header / export, the ready line) - no behaviour change
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyHudPlugin": ["~m setup"],
})

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("x20", run_x20), ("x19", run_x19), ("quest", run_quest), ("live", run_live)],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
