"""SkyyHud 0.3.25 harness - the dark XP-gain glow and the feed progress cards (tools/hud_0_3_25_patch.py).
Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir
in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.25.py [--jar SkyyHud-0.3.25.jar] [--old SkyyHud-0.3.24.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.24 -> 0.3.25: exactly the listed classes / members differ; non-class entries: the manifest
  X20 / X20F / X19 / Q / M / QK / S24 / L24 / ST   EVERY check of the 0.3.24 harness on THIS jar (M against the SET pin SkyyMenu 0.3.25 -
       the 0.3.20 jar it named is tidied away); X20's E3 / E7 feed checks eased (quest cards now read 'Quest: ...'); X20F = 0.3.24's E5S
       + those E3 / E7 checks re-run exactly with the prefixed texts
  G25  glow     WCAG contrast of the gain colour against its glow (>= 4.5 : 1; the old glow was 1 : 1); Widgets.skillsBody with Glow ON:
                every row's "+N" label X<i> is #39f493 and its 8 glow copies are #0a3a20(0.9), never #39f493(0.45); the names / levels
                keep the widget's own glow; Glow OFF = no glow copies (as before); a temporary row too
  F25  feed     Feed.hasRatio / isProg / label / cardLine / makeView on real FeedCard / FeedState objects: pickup "Cobblestone > Void"
                merged = "x9"; collection "Cobblestone 32 / 50" (count 14) = "Collection: Cobblestone 32 / 50", no count; quest progress
                "Mine 64 stone" (count 9) = "Quest: Mine 64 stone", no count; quest "Done: ..." / "Reward: ..." keep their text (+ xN when
                merged); any kind with "7/10" = no count; the prefix is never doubled; the overflow chat line follows the same rule;
                Widgets.feedFit drops the prefix before cutting a long collection text, keeps it when it fits
  E25  editor   /skyyhud editor's Select / Hidden rows (all shown, all hidden, 10 / rest, 9, two): every button box ends inside the
                page's 1290 px inner width, 9 buttons a row, the rows + page height fit (page <= 1080), every widget's button + its
                sel:<id> / show:<id> event unchanged, 120 x 32 vanilla kit buttons
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): how the dark glow reads on the real HUD over sky / grass; the prefixed cards' look.
Scratch: tools/dev/scratch/hud0325/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION, PREV = "0.3.25", "0.3.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud0325", "h")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")
GREEN, GLOW, GLOW_A = "#39f493", "#0a3a20", "0.9"
EXPECT = {}
ADDED = []


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t24():
    return load_module(os.path.join(HERE, "test_skyyhud_0.3.24.py"), "hud0324h")


def _old(name):
    def f(out, jar, scratch, home):
        getattr(t24(), name)(out, jar, scratch, home)
    return f


E37 = ["E3: CAP: 6 cards in one step", "E3: control characters become spaces", "E7: /skyyhud testfeed"]
FEED_SUBS = [('["Pumpkin", "Double drop!  Oak Log", "Chop logs  7/10", "Wolf  +35 Pet XP"]',
              '["Pumpkin", "Double drop!  Oak Log", "Quest: Chop logs  7/10", "Wolf  +35 Pet XP"]', 2),
             ('c7[1][0] == "Line one two" and len(c7[0][0]) == 48', 'c7[1][0] == "Quest: Line one two" and len(c7[0][0]) == 7 + 48', 1)]


def run_x20(out, jar, scratch, home):
    T = t24()
    T.run_x20(out, jar, scratch, home)
    T.ease(out, E37, "X20", "for 0.3.25's 'Quest: ' prefix on quest progress cards (re-run exactly with the prefixed texts in X20F)")


def run_x20f(out, jar, scratch, home):
    """the 0.3.20 exec phase with the 13-line Skills indexes (0.3.24 E5S) AND the quest cards' 'Quest: ' prefix; only its E3 / E5 / E7
    checks count here (every other check runs unchanged in X20)"""
    import json, types
    T = t24()
    sys.argv += ["--old", T.t23().old_jar(scratch, "0.3.19")]
    path = os.path.join(HERE, "test_skyyhud_0.3.20.py")
    src = open(path, encoding="utf8").read()
    for a, b in T.E5_SUBS:
        assert src.count(a) == 1, a
        src = src.replace(a, b)
    for a, b, n in FEED_SUBS:
        assert src.count(a) == n, a
        src = src.replace(a, b)
    m = types.ModuleType("hud0320f")
    m.__file__ = path
    exec(compile(src, path, "exec"), m.__dict__)
    m.run_exec(out, jar, os.path.join(scratch, "x20f"), home)
    d = json.load(open(out))
    keep = ("E3", "E5", "E7")
    other = [f for f in d["fails"] if not f.startswith(keep)]
    d["fails"] = [f for f in d["fails"] if f.startswith(keep)]
    d.setdefault("notes", []).append("X20F: the 0.3.20 E3 / E5 / E7 checks with the 13-line indexes + 'Quest: ' texts; %d other fails ignored here (X20 "
                                     "checks them): %s" % (len(other), [f[:60] for f in other]))
    json.dump(d, open(out, "w"), indent=1)


MENU_JAR = os.path.join(ROOT, "SkyyMenu", "SkyyMenu-0.3.25.jar")   # the SET pin (the 0.3.22 harness's SkyyMenu 0.3.20 jar is tidied away)


def run_msg(out, jar, scratch, home):
    """the 0.3.22 harness's M phase (what 0.3.23 / 0.3.24 run unchanged) against the SET pin's SkyyMenu jar"""
    m = load_module(os.path.join(HERE, "test_skyyhud_0.3.22.py"), "hud0322m")
    m.MENU_JAR = MENU_JAR
    m.run_msg(out, jar, scratch, home)


def lum(h):
    c = [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _labels(src):
    """Label #<id> { ... TextColor: <c>, ... } -> {id: colour}"""
    import re
    return dict(re.findall(r"Label #(\w+) \{[^}]*?TextColor: ([#\w.()]+)", src))


def run_g25(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    WL, Wid = JClass(PKG + "WLayout"), JClass(PKG + "Widgets")
    String = JClass("java.lang.String")
    cr = contrast(GREEN, GLOW)
    K.check(cr >= 4.5, "G25 WCAG contrast gain %s : glow %s = %.2f : 1 (>= 4.5)" % (GREEN, GLOW, cr))
    K.eq(round(contrast(GREEN, GREEN), 2), 1.0, "G25 (the old glow was the same green: 1 : 1)")
    K.notes.append("G25 contrast %s : %s = %.2f : 1" % (GREEN, GLOW, cr))
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    for glow in (True, False):
        l = WL.parse("1,tr,8,240,100,1,def,1,0,%d,def" % (1 if glow else 0), wdef("Skills"))
        K.eq(bool(l.glow), glow, "G25 the test layout has Glow %s" % glow)
        # 3 rows: Overall, Mining (+14 flashing), a temporary row (Fishing, hidden skill) - tmp count 1 at [SKL_ARR + 13]
        m = [None] * 60
        m[0] = "K3"
        m[2], m[3], m[4], m[5], m[6], m[7] = "Overall Level", "10", "Mining", "12", "Fishing", "7"
        m[28 + 1] = "+14"
        m[28 + 13] = "1"
        src = str(Wid.skillsBody("SkyyWSkills", l, 100, JArray(String)(m), 6, 200))
        lab = _labels(src)
        for i in range(3):
            K.eq(lab.get("SkyyWSkillsX%dTxt" % i), GREEN, "G25 glow %s row %d: the gain label keeps its green" % (glow, i))
            gl = [lab.get("SkyyWSkillsX%dG%d" % (i, k)) for k in range(8)]
            if glow:
                K.eq(gl, ["%s(%s)" % (GLOW, GLOW_A)] * 8, "G25 glow ON row %d: the 8 gain glow copies are the dark green" % i)
            else:
                K.eq(gl, [None] * 8, "G25 glow OFF row %d: no gain glow copies (as before)" % i)
        K.check("%s(0.45)" % GREEN not in src, "G25 glow %s: no green-on-green glow left anywhere in the Skills markup" % glow)
        if glow:
            K.eq(lab.get("SkyyWSkillsN1G0"), str(Wid.glowHex(l)) + "(0.45)", "G25 the skill NAME keeps the widget's own glow")
            K.eq(lab.get("SkyyWSkillsN2G0"), "#b7cedd(0.45)", "G25 a temporary row's name keeps its grey glow")
    K.save()


def run_f25(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Feed, Card, State, Wid = JClass(PKG + "Feed"), JClass(PKG + "FeedCard"), JClass(PKG + "FeedState"), JClass(PKG + "Widgets")
    UUID, Long, Boolean, Object = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Object")
    # ---- the classifier
    for t, want in (("Cobblestone 32 / 50", True), ("Chop logs  7/10", True), ("18/50", True), ("Cobblestone > Void", False),
                    ("Tree felled: 207 logs, 36 leaves", False), ("+120 coins  Bank interest", False), ("a / b", False), ("", False)):
        K.eq(bool(Feed.hasRatio(t)), want, "F25 hasRatio(%r)" % t)
    for kind, t, want in (("collection", "Cobblestone 1,234 (max)", True), ("quest", "Mine 64 stone", True), ("quest", "Done: Mine 64 stone", False),
                          ("quest", "Reward: 100 coins", False), ("pickup", "Cobblestone > Void", False), ("pickup", "Pumpkin", False),
                          ("drop", "Double drop!  Oak Log", False), ("rankup", "Cobblestone II", False), ("heal", "Party 3/4 healed", True)):
        K.eq(bool(Feed.isProg(kind, t)), want, "F25 isProg(%s, %r)" % (kind, t))
    for kind, t, want in (("collection", "Cobblestone 32 / 50", "Collection: Cobblestone 32 / 50"), ("collection", "Collection: Oak 5 / 50", "Collection: Oak 5 / 50"),
                          ("quest", "Mine 64 stone", "Quest: Mine 64 stone"), ("quest", "Quest: Mine 64 stone", "Quest: Mine 64 stone"),
                          ("quest", "Done: Mine 64 stone", "Done: Mine 64 stone"), ("quest", "Reward: 100 coins", "Reward: 100 coins"),
                          ("pickup", "Cobblestone > Void", "Cobblestone > Void"), ("heal", "Party 3/4 healed", "Party 3/4 healed")):
        K.eq(str(Feed.label(kind, t)), want, "F25 label(%s, %r)" % (kind, t))
    # ---- real cards through addCard (the merge; e = the queued push { "f", kind, icon, text, Long n (1 when the sender gave none), Boolean had a count }) -> makeView (what the HUD draws) and cardLine (the chat line)
    Feed.ICONS.put("Rock_Stone_Cobble", Boolean.TRUE)     # an item the server knows (no asset store here): the merge key is kind|icon
    s = State(UUID(0x5ce25, 1))
    now = 1000000

    def push(kind, icon, text, n, hc, at):
        Feed.addCard(s, JArray(Object)(["f", kind, icon, text, Long(n), Boolean(hc)]), at, 3000, 6)
    push("pickup", "Rock_Stone_Cobble", "Cobblestone > Void", 4, True, now)
    push("pickup", "Rock_Stone_Cobble", "Cobblestone > Void", 5, True, now + 200)
    push("collection", "Rock_Stone_Cobble", "Cobblestone 18 / 50", 5, True, now + 300)
    push("collection", "Rock_Stone_Cobble", "Cobblestone 32 / 50", 9, True, now + 500)
    push("quest", None, "Mine 64 stone", 9, True, now + 600)
    push("quest", None, "Done: Chop 10 logs", 1, False, now + 700)
    v = Feed.makeView(s, now + 800, 4000, 3000)
    got = [(str(v.name[j]), str(v.cnt[j])) for j in range(int(v.n))]
    K.eq(got, [("Done: Chop 10 logs", ""), ("Quest: Mine 64 stone", ""), ("Collection: Cobblestone 32 / 50", ""), ("Cobblestone > Void", "x9")],
         "F25 the feed: pickup keeps x9 (4 + 5 merged); the collection card merged to 32 / 50 with NO x14; the quest card NO x9; prefixes")
    cards = list(s.cards)
    lines = [str(Feed.cardLine(c)) for c in cards]
    K.eq(lines, ["Done: Chop 10 logs", "Quest: Mine 64 stone", "Collection: Cobblestone 32 / 50", "Cobblestone > Void  x9"],
         "F25 the overflow chat lines follow the same rule")
    K.eq([int(c.count) for c in cards], [1, 9, 14, 9], "F25 the counts are still added up (merge unchanged; only the display drops xN)")
    s2 = State(UUID(0x5ce25, 2))

    def push2(kind, text, n, hc, at):
        Feed.addCard(s2, JArray(Object)(["f", kind, None, text, Long(n), Boolean(hc)]), at, 3000, 6)
    push2("quest", "Reward: 100 coins", 1, False, now)
    push2("quest", "Reward: 100 coins", 1, False, now + 100)
    push2("heal", "+8 HP  Priest heal", 1, False, now + 200)
    push2("pickup", "Chop logs  7/10", 3, True, now + 300)
    v2 = Feed.makeView(s2, now + 400, 4000, 3000)
    K.eq([(str(v2.name[j]), str(v2.cnt[j])) for j in range(int(v2.n))],
         [("Chop logs  7/10", ""), ("+8 HP  Priest heal", ""), ("Reward: 100 coins", "x2")],
         "F25 a '7/10' text of any kind = no count; a merged Reward card keeps x2; a heal card unchanged")
    # ---- feedFit: the prefix goes before the numbers would be cut
    short = "Collection: Cobblestone 32 / 50"
    K.eq(str(Wid.feedFit(short, "", 100, True)), short, "F25 feedFit keeps a prefixed text that fits at 100 %")
    long_ = "Collection: Enchanted Cobblestone 12,345 / 50,000"
    f = str(Wid.feedFit(long_, "", 100, True))
    K.check(not f.startswith("Collection: ") and f.startswith("Enchanted Cobblestone"), "F25 feedFit drops the prefix of a long collection text first: %r" % f)
    K.check(not str(Wid.feedFit("Cobblestone > Void and some very long pickup text here", "x9", 100, True)).startswith("Collection"),
            "F25 feedFit of a plain text: cut as before")
    K.eq(str(Wid.stripKind("Quest: Mine 64 stone")), "Mine 64 stone", "F25 stripKind Quest")
    K.eq(str(Wid.stripKind("Cobblestone > Void")), "Cobblestone > Void", "F25 stripKind leaves other texts")
    K.save()


def run_e25(out, jar, scratch, home):
    """the editor's Select / Hidden rows: every button box inside the page (1330 wide, 20 px padding = 1290 inside), wrapped rows, the
    page height fits 1080, ids / events unchanged, vanilla kit button style"""
    import re
    T = t24()
    T.JAR_IN_USE[0] = jar
    K = HK.Child(out)
    E = T._env(scratch)
    H = E["H"]
    LS, Wid, EP = H("LayoutStore"), H("Widgets"), H("EditorPage")
    H("DsLink").DS = 1                      # Dynamic Seasons "installed": the editor lists all 17 widgets (the worst case)
    ids = [str(x) for x in Wid.edIds()]
    K.check(len(ids) == len(Wid.IDS) and "Quest" in ids and "Seasons" in ids, "E25 %d editor widget ids (Seasons + Quest included): %s" % (len(ids), ids))
    W = lambda mk: int(re.search(r"Width: (\d+)", mk).group(1)) if re.search(r"Width: (\d+)", mk) else None
    Hh = lambda mk: int(re.search(r"Height: (\d+)", mk).group(1)) if re.search(r"Height: (\d+)", mk) else None
    for n, (case, onset) in enumerate((("all shown", set(ids)), ("all hidden", set()), ("10 shown / rest hidden", set(ids[:10])),
                                       ("9 shown", set(ids[:9])), ("Quest + Feed only", {"Quest", "Feed"}))):
        me = E["pref"](100 + n, "Ed%d" % n)
        u = me.getUuid()
        m = LS.get(u)
        for i in ids:
            l = m.get(i)
            if l is not None:
                l.en = i in onset
        cm, es = E["page"](EP(me, E["plugin"]))
        ap = [(c[1], c[3] or c[2] or "") for c in cm if c[0] == "AppendInline" or (c[0].startswith("Append") and c[1] is not None)]
        root = [c for c in cm if c[1] is None and "#SkyyEditor" in (c[3] or c[2] or "")]
        mk_root = (root[0][3] or root[0][2]) if root else ""
        pw, ph = W(mk_root), Hh(mk_root)
        K.check(pw == 1330 and ph is not None and ph <= 1080, "E25 %s: the page %sx%s fits 1080 high" % (case, pw, ph))
        kids = [Hh(mk) for par, mk in ap if par == "#SkyyEditor"]
        K.check(None not in kids and sum(kids) <= ph - 2 * 10, "E25 %s: the page's rows (%s = %s) fit inside its height %s - 20" % (case, kids, sum(kids or [0]), ph))
        rows = {}
        for par, mk in ap:
            if par and re.match(r"#SkyyE(SelRow|Off)\d+$", par):
                rows.setdefault(par, []).append(mk)
        shown = [i for i in ids if i in onset and m.get(i) is not None]
        hidden = [i for i in ids if i not in onset and m.get(i) is not None]
        nsel = len([r for r in rows if r.startswith("#SkyyESelRow")])
        noff = len([r for r in rows if r.startswith("#SkyyEOff")])
        K.eq((nsel, noff), (max(1, -(-len(shown) // 9)), max(1, -(-len(hidden) // 9))), "E25 %s: Select / Hidden rows (9 buttons a row)" % case)
        for r, mks in sorted(rows.items()):
            x = 0
            for mk in mks:
                w = W(mk)
                K.check(w is not None, "E25 %s %s: every child has a width" % (case, r))
                x += w or 0
                if mk.startswith("TextButton"):
                    bid = re.search(r"#(\w+)", mk).group(1)
                    K.check(x <= 1290, "E25 %s: button %s ends at x %d inside the page (1290 px inside the padding)" % (case, bid, x))
                    K.check(Hh(mk) == 32 and w == 120 and "Common/Buttons/" in mk, "E25 %s: %s is a 120 x 32 vanilla kit button" % (case, bid))
        btn = re.compile(r"TextButton #(SkyyE(?:Sel|On)\w+)")
        got = set(btn.search(mk).group(1) for par, mk in ap if btn.search(mk))
        want = set("SkyyESel" + i for i in shown) | set("SkyyEOn" + i for i in hidden)
        K.check(want <= got, "E25 %s: every widget has its button: missing %s" % (case, sorted(want - got)))
        evs = set((e[1], e[2]) for e in es)
        miss = [i for i in shown if not any(sel == "#SkyyESel" + i and "sel:" + i in (d or "") for sel, d in evs)]
        miss += [i for i in hidden if not any(sel == "#SkyyEOn" + i and "show:" + i in (d or "") for sel, d in evs)]
        K.check(not miss, "E25 %s: the events are unchanged (sel:<id> / show:<id>): missing %s" % (case, miss))
        if case == "all shown":
            K.check("Primary.png" not in "".join(mk for par, mk in ap if "SkyyESel" in mk), "E25 nothing selected: no Primary button")
            K.notes.append("E25 all shown: page %sx%s, rows %s" % (pw, ph, kids))
    K.save()


EXPECT.update({
    "Feed": ["+m hasRatio", "+m isProg", "+m label", "+m questProg", "~m cardLine", "~m makeView"],
    "Widgets": ["+m stripKind", "~m feedFit", "~m skillsBody"],
    "EditorPage": ["~m build"],               # the Select / Hidden rows wrap (vanilla kit buttons 120 x 32)
    # the version string (the kit's header / export, the ready line)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
})

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("x20", run_x20), ("x20f", run_x20f), ("x19", _old("run_x19")), ("quest", _old("run_quest")), ("msg", run_msg),
            ("qk", _old("run_qk")), ("s24", _old("run_s24")), ("l24", _old("run_l24")), ("g25", run_g25), ("e25", run_e25), ("f25", run_f25), ("live", _old("run_live"))],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
