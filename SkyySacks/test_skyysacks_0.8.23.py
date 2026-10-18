"""Harness for SkyySacks 0.8.23 (the Furnace page shows QUEUE / FUEL / READY TO COLLECT lists, the fuel line red / green;
tools/sacks_0_8_23_patch.py). Build first:
    python tools/sacks_0_8_23_patch.py && python SkyySacks/build_skyysacks_0.8.23.py

    python SkyySacks/test_skyysacks_0.8.23.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.22 -> 0.8.23: exactly the planned members (EXPECT); non-class entries: manifest.json only
  FUR   EXECUTED on the 0.8.15 harness's stand-ins (real SimpleItemContainers, a stand-in Item store, REAL CraftingRecipe objects), the page
        BUILT through the real CraftPage.renderPage and checked with the kit (check_page, sky paths, every b.set / binding names an element,
        assert_menu_page 1600 x 980):
        RULE   ProcBench.fuelEnough at the edges (equal = enough), fuelState (0 no fuel needed / Eternal, 1 enough, 2 short; the Furnace
               Charm's faster burn), queueRows (batch times, done in counted from now, the last = queueMs), fuelRows (the lit remainder row)
        PAGE   the three lists (ids, scroll lists, rows), the fuel header GREEN at equal / RED one ms short (+ "(need ...)"), a late queue
               row red; an empty queue + no fuel + nothing ready (the empty-state lines); 30 queued batches + 30 ready kinds in the scroll
               lists; 250 ready kinds = 200 rows + "+ 50 more"; few rows grow (Skyy rule 7); the text fits its labels (estimate)
        BTN    the old buttons keep their ids + events (pcollect / pcancel / punload / paddf / pfuel:0); the ADD FUEL view keeps 0.8.22's lines
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA    engine-access audit
  TT    RecipeCmp's baked table = tools/tier_tags.py ROWS: build AND test with the COMMITTED table (2026-10-18 another builder's uncommitted
        TT_VERSION 3 sat in the working tree; the build pre-imported `git show b522c21d:tools/tier_tags.py`); FUR checks the baked table = b522c21d's
Not testable without the game (UNVERIFIED): the look in game, the scroll wheel in the three short lists, the real fuel burn times (the item
assets are not loaded here), item icons for queued recipes (the recipe asset map is not loaded here). Exit code 1 on any failure.
"""
import os, sys, re, inspect, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_15", os.path.join(HERE, "test_skyysacks_0.8.15.py"))
T15 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T15)
sys.argv = _argv
HK.run_compare = _orig_compare

VERSION = "0.8.23"
OLD_VERSION = "0.8.22"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks23", "h")))
PKG = "com.skyy.sacks."
EXPECT = {
    "ProcBench": ["+m outId", "+m queueRows", "+m fuelEffMs", "+m fuelRows", "+m fuelEnough", "+m fuelState", "+m fuelNeedMs", "+m knownId", "+m itemName"],
    "CraftPage": ["+f PL_PQ", "+f PL_PFF", "+f PL_PR", "+f L_OKH", "+f L_BADH", "+f L_ROWN", "+f PLHS", "+f PQWS", "+f PFWS", "+f PRWS",
                  "+f PLH", "+f PLLH", "+f PLADD", "+f PLICO", "+f PLMAX", "+f PQW", "+f PFW", "+f PRW",
                  "+m procRow", "+m procEnd", "+m procLists", "~m buildProc", "~<clinit>"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],     # the version text
    "SkyySacksPlugin": ["~m setup"],                         # the ready line
    # the /craft sort table re-baked from the COMMITTED tools/tier_tags.py: rows added after 0.8.22 was built (SkyyGear 0.3.23 G2 forever tools,
    # SkyyArmory 0.1.33 / 0.1.34 metal weapons - rows only, no number moves); checked in FUR (TT_IDS = tier_tags.ROWS)
    "RecipeCmp": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []

# ---- the FUR cases run inside the 0.8.15 fixture: its helpers + the CRAFT set-up (recipes, the test CraftPage, cpage / cbuild), then ours
_src = inspect.getsource(T15.new_cases)
_a = _src.index("    # ============================================================== TAB")
_c = _src.index("    # ============================================================== CRAFT")
_d = _src.index("    pC = player(storage", _c)
_CASES = '''
    # ============================================================== FUR (0.8.23)
    from jpype import JLong
    PB, PJ = J("ProcBench"), J("ProcJob")
    Integer = JClass("java.lang.Integer")
    C_OK, C_BAD = SUI.color("have"), SUI.color("outOfStock")
    # the baked sort table = the tier_tags.py this run sees (build + test with the committed table; see the docstring)
    import subprocess, importlib.util as ILU
    _tth = os.path.join(scratch, "tier_tags_b522c21d.py")
    with open(_tth, "wb") as _fh:
        _fh.write(subprocess.run(["git", "show", "b522c21d:tools/tier_tags.py"], cwd=ROOT, capture_output=True, check=True).stdout)
    _sp2 = ILU.spec_from_file_location("tier_tags_b522c21d", _tth)
    TT_ = ILU.module_from_spec(_sp2)
    _sp2.loader.exec_module(TT_)
    RC = J("RecipeCmp")
    K.eq(sorted(str(x) for x in RC.TT_IDS), sorted(TT_.ROWS), "TT RecipeCmp.TT_IDS = tools/tier_tags.py ROWS as committed at b522c21d (TT_VERSION %s, %d rows)"
         % (TT_.TT_VERSION, len(TT_.ROWS)))
    K.eq([int(x) for x in RC.TT_TIER], [TT_.tier(i) for i in sorted(TT_.ROWS)], "TT RecipeCmp.TT_TIER = that table's tiers")
    # RULE: the pure edges
    K.eq([bool(PB.fuelEnough(JLong(f), JLong(q), JInt(u))) for f, q, u in ((0, 0, 0), (10000, 10000, 2), (10001, 10000, 2), (10002, 10000, 2),
                                                                           (10003, 10000, 2), (0, 1, 1), (5, 0, 0), (10000, 10000, 0))],
         [True, False, False, True, True, False, True, True],
         "RULE fuelEnough (review fix): green needs 1 ms to spare per queued unit - equal with 2 units red, +1 red, +2 green; nothing queued green")
    fuels = ["Ingredient_Stick", "Wood_Oak_Trunk", "Ingredient_Charcoal"]
    _fl = JClass("java.util.ArrayList")()
    for f_ in fuels:
        _fl.add(JString(f_))
    PB.FUELS = _fl
    for f_ in fuels:
        custom_item(f_, 100)
    pb = J("ProcStore").of(JString(k), JString("Furnace"))
    pb.needsFuel = True

    def reset(jobs=(), fuel=(), out=(), fuel_ms=0, progress=0, cfuel=0, eternal=False, ctime=0):
        pb.queue.clear(); pb.fuel.clear(); pb.out.clear()
        for rid, cnt, ums in jobs:
            pb.queue.add(PJ(JString(rid), JInt(cnt), JLong(ums), JString("")))
        for fid, c in fuel:
            pb.fuel.put(JString(fid), Integer.valueOf(c))
        for oid, c in out:
            pb.out.put(JString(oid), Integer.valueOf(c))
        pb.fuelMs = fuel_ms; pb.progress = progress; pb.cFuel = cfuel; pb.cEternal = eternal; pb.cTime = ctime; pb.clock = 0
    reset([("Skyy_Test_R0", 2, 5000)], fuel_ms=10002)
    s1 = int(pb.fuelState())
    reset([("Skyy_Test_R0", 2, 5000)], fuel_ms=10000)
    s2 = int(pb.fuelState())
    reset([("Skyy_Test_R0", 2, 5000)], fuel_ms=12503, cfuel=25)
    s3, f3 = int(pb.fuelState()), int(pb.fuelEffMs())
    reset([("Skyy_Test_R0", 2, 5000)], fuel_ms=12502, cfuel=25)
    s4 = int(pb.fuelState())
    reset([("Skyy_Test_R0", 2, 5000)], fuel_ms=0, eternal=True)
    s5 = int(pb.fuelState())
    reset([], fuel_ms=0)
    s6 = int(pb.fuelState())
    reset([("Skyy_Test_R0", 1, 1000)], fuel_ms=0)
    s7 = int(pb.fuelState())
    pb.needsFuel = False
    s8 = int(pb.fuelState())
    pb.needsFuel = True
    K.eq([s1, s2, s3, f3, s4, s5, s6, s7, s8], [1, 2, 1, 10002, 2, 0, 1, 2, 0],
         "RULE fuelState: 10002 fuel / 10000 queue (2 units) green, 10000 (equal) red, the charm's +25 percent burn (12503 -> 10002) green, 12502 red, Eternal "
         "and no-fuel benches 0, empty queue + no fuel green, a queue with no fuel red")
    reset([("Skyy_Test_R0", 2, 5000), ("Skyy_Test_R1", 3, 1000)], fuel_ms=500, progress=1000)
    qr = [[None if x is None else (str(x) if i < 2 else int(str(x))) for i, x in enumerate(r)] for r in pb.queueRows()]
    K.eq([(r[0], r[1], r[2], r[3], r[4]) for r in qr], [(None, "Skyy Test R0", 2, 9000, 9000), (None, "Skyy Test R1", 3, 3000, 12000)],
         "RULE queueRows: each batch's time (the running unit's progress off), done in from now (the batches ahead included)")
    K.eq(int(pb.queueMs()), 12000, "RULE the last row's done in = queueMs (the whole queue)")
    reset([], fuel=[("Ingredient_Stick", 7)], fuel_ms=4000, cfuel=100)
    fr = [[None if x is None else str(x) for x in r] for r in pb.fuelRows()]
    K.check(len(fr) == 2 and fr[0][0] is None and fr[0][1] == "Burning now" and fr[0][3] == "2000" and fr[1][0] == "Ingredient_Stick" and fr[1][2] == "7",
            "RULE fuelRows: the lit remainder first (4000 ms at +100 percent burn = 2000), then one row per loaded fuel item: %s" % fr)
    reset([("Skyy_Test_R0", 1, 1000)], fuel=[("Ingredient_Stick", 3)])
    pb.fuel.put(JString("Wood_Oak_Trunk"), Integer.valueOf(2))
    K.eq(int(pb.fuelState()) in (1, 2) and pb.fuelCount() == 5, True, "RULE (the fuel map is read, never changed: %d items)" % pb.fuelCount())

    # PAGE
    pF = player(storage=[(BAR, 9), (ORE, 9)] + [(f_, 20 + 10 * n) for n, f_ in enumerate(fuels)])
    setR(rows[:3])
    pp = cpage("P:Furnace")
    lab_re = re.compile(r"Label #([A-Za-z0-9]+) \\{ Anchor: \\(Width: (\\d+), Height: \\d+\\); Text: \\"\\"; Style: \\(FontSize: (\\d+)[^)]*TextColor: ([^;),]+)")

    def labels(c):
        out = {}
        for _ty, s, t, _d in c:
            if t:
                for m in lab_re.finditer(t):
                    out[m.group(1)] = (int(m.group(2)), int(m.group(3)), m.group(4).strip())
        return out

    def fit(c, what):
        lb, bad = labels(c), []
        for ty, s, t, d in c:
            if ty != "Set" or not s or not s.endswith(".Text") or not s.startswith("#SkyyP"):
                continue
            i = s[1:].split(".")[0]
            if i not in lb:
                continue
            txt = str(unq(d))
            w, size, _c = lb[i]
            if len(txt) * 0.56 * size > w:
                bad.append((i, txt, w, size))
        K.check(not bad, "%s: every SkyyP text fits its label (estimate 0.56 x font size per character): %s" % (what, bad[:4]))

    def page(what, **kw):
        reset(**kw)
        c, e, apps, sets, txt = cbuild(pp, pF, what)
        SETS.clear()
        SETS.update(dict((s, str(d)) for s, d in sets))
        return c, e, txt, labels(c), dict((s, d) for s, d in e if s)
    SETS = {}

    # green at equal
    c, e, txt, lb, binds = page("PAGE green", jobs=[("Skyy_Test_R0", 2, 5000)], fuel=[("Ingredient_Stick", 3)], out=[(BAR, 4)], fuel_ms=11000)
    st = int(pb.fuelState())
    ids = ["SkyyPLists", "SkyyPQCol", "SkyyPQHd", "SkyyPQHead", "SkyyPQList", "SkyyPQRow0", "SkyyPFuCol", "SkyyPFuHd", "SkyyPFuHead",
           "SkyyPFuList", "SkyyPFuRow0", "SkyyPFuRow1", "SkyyPRCol", "SkyyPRHd", "SkyyPRHead", "SkyyPRList", "SkyyPRRow0",
           "SkyyPCollect", "SkyyPCancel", "SkyyPUnload", "SkyyPAddF", "SkyyPFuelRow", "SkyyPStat", "SkyyPProg", "SkyyPBar"]
    K.check(all(("#" + i + " ") in txt for i in ids), "PAGE the layout ids exist: %s" % [i for i in ids if ("#" + i + " ") not in txt])
    K.check(all(("Group #%s { Anchor: (Height: 124); LayoutMode: TopScrolling" % i) in txt for i in ("SkyyPQList", "SkyyPFuList", "SkyyPRList")),
            "PAGE the three lists are kit scroll lists (TopScrolling, 124 high)")
    K.check("SkyyPQueue" not in txt and "SkyyPOut " not in txt and "#SkyyPOutRow" not in txt, "PAGE the old one-line queue / ready summaries are gone")
    K.check(st == 1 and lb.get("SkyyPFuHead", (0, 0, ""))[2] == C_OK, "PAGE fuel 11000 ms : queue 10000 ms = GREEN header (state %d, %s)" % (st, lb.get("SkyyPFuHead")))
    sets_ = list(SETS.items())
    gtxt = [d for s, d in sets_ if s == "#SkyyPFuHead.Text"]
    K.check(gtxt and "Fuel 11s : queue 10s" in gtxt[0] and "need" not in gtxt[0], "PAGE the green line = 'Fuel 11s : queue 10s': %s" % gtxt)
    nm_ = dict(SETS)
    K.check(nm_.get("#SkyyPRRow0t0.Text") == str(PB.itemName(JString(BAR))) and nm_.get("#SkyyPFuRow1t0.Text") == str(PB.itemName(JString("Ingredient_Stick")))
            and str(PB.itemName(JString(BAR))) != "", "PAGE ready / fuel rows use ProcBench.itemName (outName's proper name): %s / %s"
            % (nm_.get("#SkyyPRRow0t0.Text"), nm_.get("#SkyyPFuRow1t0.Text")))
    qtx = [d for s, d in sets_ if s.startswith("#SkyyPQRow0t") or s == "#SkyyPQHead.Text"]
    K.check(any("x2" in d for d in qtx) and any("done in 10s" in d for d in qtx) and any("Queue 2 / 256 - done in 10s" in d for d in qtx),
            "PAGE the queue row (x2, done in 10s) + the header's whole queue: %s" % qtx)
    K.check(lb.get("SkyyPQRow0t3", (0, 0, ""))[2] == C_OK, "PAGE a queue row the fuel covers: its done in is green")
    rtx = [d for s, d in sets_ if s.startswith("#SkyyPRRow0t") or s == "#SkyyPRHead.Text"]
    K.check(any("x4" in d for d in rtx) and any("Ready to collect - 4" in d for d in rtx) and ("ItemId: \\"%s\\"" % BAR) in txt,
            "PAGE the ready row (its icon, x4) + the header: %s" % rtx)
    fit(c, "PAGE green")
    # red one ms short
    c, e, txt, lb, binds = page("PAGE red", jobs=[("Skyy_Test_R0", 2, 5000), ("Skyy_Test_R1", 1, 1000)], fuel_ms=9999)
    st = int(pb.fuelState())
    sets_ = list(SETS.items())
    rh = [d for s, d in sets_ if s == "#SkyyPFuHead.Text"]
    K.check(st == 2 and lb.get("SkyyPFuHead", (0, 0, ""))[2] == C_BAD and rh and "Fuel 10s : queue 11s" in rh[0] and "(need 2s)" in rh[0],
            "PAGE fuel 9999 ms : queue 11000 ms = RED header with the shortfall: %s %s" % (rh, lb.get("SkyyPFuHead")))
    K.check(lb.get("SkyyPQRow0t3", (0, 0, ""))[2] == C_BAD and lb.get("SkyyPQRow1t3", (0, 0, ""))[2] == C_BAD,
            "PAGE queue rows past the loaded fuel: done in red")
    fit(c, "PAGE red")
    # exact equality is red now (review fix), the need line says 1s
    c, e, txt, lb, binds = page("PAGE equal", jobs=[("Skyy_Test_R0", 2, 5000)], fuel_ms=10000)
    K.check(lb.get("SkyyPFuHead", (0, 0, ""))[2] == C_BAD and "(need 1s)" in SETS.get("#SkyyPFuHead.Text", ""),
            "PAGE fuel = queue exactly: RED '(need 1s)' (1 ms per unit to spare): %s" % SETS.get("#SkyyPFuHead.Text"))
    # empty everything
    c, e, txt, lb, binds = page("PAGE empty", fuel_ms=0)
    sets_ = dict(SETS)
    K.check("#SkyyPQNone " in txt and "#SkyyPFuNone " in txt and "#SkyyPRNone " in txt and "SkyyPQRow0" not in txt and "SkyyPFuRow0" not in txt
            and "SkyyPRRow0" not in txt, "PAGE empty queue + no fuel + nothing ready: the three empty-state lines, no rows")
    K.check("Queue - empty" in sets_.get("#SkyyPQHead.Text", "") and "Fuel 0s : queue 0s" in sets_.get("#SkyyPFuHead.Text", "")
            and lb.get("SkyyPFuHead", (0, 0, ""))[2] == C_OK and "No fuel loaded" in sets_.get("#SkyyPFuNone.Text", ""),
            "PAGE empty: 'Queue - empty', 'Fuel 0s : queue 0s' green (nothing is short), 'No fuel loaded ...'")
    K.check(all(s in binds for s in ("#SkyyPCollect", "#SkyyPCancel", "#SkyyPUnload", "#SkyyPAddF")), "PAGE empty: the buttons are still bound")
    fit(c, "PAGE empty")
    # no fuel + a queue
    c, e, txt, lb, binds = page("PAGE no fuel", jobs=[("Skyy_Test_R0", 3, 2000)], fuel_ms=0)
    sets_ = dict(SETS)
    K.check(lb.get("SkyyPFuHead", (0, 0, ""))[2] == C_BAD and "(need 6s)" in sets_.get("#SkyyPFuHead.Text", ""), "PAGE a queue with no fuel = red (need 6s): %s" % sets_.get("#SkyyPFuHead.Text"))
    # long lists in the scroll lists
    jobs = [("Skyy_Test_R%d" % (n % 12), 1 + n % 5, 1000) for n in range(30)]
    outs30 = [("Skyy_Test_Out%d" % (n % 12) if n < 12 else "Skyy_Test_Long%d" % n, 1 + n) for n in range(30)]
    c, e, txt, lb, binds = page("PAGE long", jobs=jobs, out=outs30, fuel=[(f_, 5) for f_ in fuels], fuel_ms=1000)
    K.check(all(("#SkyyPQRow%d " % n) in txt for n in range(30)) and all(("#SkyyPRRow%d " % n) in txt for n in range(30))
            and txt.count("Anchor: (Height: 36, Bottom: 3)") == 30 + 30 + 4 and "SkyyPQMore" not in txt and "SkyyPRMore" not in txt,
            "PAGE 30 queued batches + 30 ready kinds: every row in its scroll list at the normal 36 px")
    par = [s for ty, s, t, d in c if t and t.startswith("Group #SkyyPQRow")]
    K.check(par and all(s == "#SkyyPQList" for s in par), "PAGE the queue rows sit inside #SkyyPQList")
    fit(c, "PAGE long")
    K.check('ItemId: "Skyy_Test_Long12"' not in txt and "#SkyyPRRow12 " in txt and ('ItemId: "%s"' % "Skyy_Test_Out0") in txt,
            "PAGE an id the server does not know (an uninstalled mod's) draws its row but no ItemIcon (review fix)")
    many = [("Skyy_Test_Many%d" % n, 1) for n in range(250)]
    c, e, txt, lb, binds = page("PAGE 250 ready", out=many, fuel_ms=0)
    K.check(("#SkyyPRRow199 ") in txt and "#SkyyPRRow200 " not in txt and "#SkyyPRMore " in txt
            and "+ 50 more" in SETS.get("#SkyyPRMore.Text", ""),
            "PAGE 250 ready kinds: 200 rows + '+ 50 more'")
    c, e, txt, lb, binds = page("PAGE few", out=[(BAR, 1)], fuel_ms=0)
    K.check("Group #SkyyPRRow0 { Anchor: (Height: %d, Bottom: 3)" % int(list(CP.PLHS)[2]) in txt and int(list(CP.PLHS)[2]) > 36,
            "PAGE one ready row grows (Skyy rule 7: %s)" % list(CP.PLHS))

    # BTN: the old buttons, ids + events
    c, e, txt, lb, binds = page("BTN", jobs=[("Skyy_Test_R0", 1, 1000)], out=[(BAR, 1)], fuel_ms=1000)
    want = {"#SkyyPCollect": "pcollect", "#SkyyPCancel": "pcancel", "#SkyyPUnload": "punload", "#SkyyPAddF": "paddf", "#SkyyPFuel0": "pfuel:0"}
    K.check(all(s in binds and v in binds[s] for s, v in want.items()), "BTN the old buttons keep their events: %s" % dict((s, binds.get(s, "")[:60]) for s in want))
    K.check(all(re.search(r'TextButton #%s \\{[^}]*Text: \\"%s\\"' % (i, t), txt) for i, t in
                (("SkyyPCollect", "Collect"), ("SkyyPCancel", "Cancel queue"), ("SkyyPUnload", "Unload fuel"), ("SkyyPAddF", "Add fuel"))),
            "BTN the old buttons keep their labels")
    par = dict((re.match(r"TextButton #([A-Za-z0-9]+)", t).group(1), s) for ty, s, t, d in c if t and t.startswith("TextButton #SkyyP"))
    K.check(par.get("SkyyPCollect") == "#SkyyPRHd" and par.get("SkyyPCancel") == "#SkyyPQHd" and par.get("SkyyPUnload") == "#SkyyPFuelRow",
            "BTN Collect by the ready list, Cancel queue by the queue, Unload fuel at the end of the Load fuel row: %s" % par)
    gdr = open(os.path.join(HERE, "build_skyysacks_0.8.23.py"), encoding="utf8").read()
    odr = open(os.path.join(HERE, "build_skyysacks_0.8.22.py"), encoding="utf8").read()
    hp = lambda s_: s_[s_.index("public boolean handleProc("):s_.index('"""', s_.index("public boolean handleProc("))]
    evs = lambda s_: sorted(set(re.findall(r'@EVD@[.]of[(]"a", "([a-z]+)', s_)))
    K.check(evs(gdr) == evs(odr) and hp(gdr) == hp(odr),
            "BTN handleProc is byte-identical to 0.8.22 and the page binds the same event names (%d)" % len(evs(gdr)))
    # the ADD FUEL view keeps 0.8.22's lines
    reset([("Skyy_Test_R0", 1, 1000)], fuel_ms=1000)
    jfield(CP.class_, "fuelPick").setBoolean(pp, True)
    c, e, apps, sets, txt = cbuild(pp, pF, "BTN ADD FUEL")
    binds = dict((s, d) for s, d in e if s)
    K.check("#SkyyPQueue " in txt and "#SkyyPOutRow " in txt and "SkyyPLists" not in txt and "SkyyPFList" in txt
            and all(s in binds for s in ("#SkyyPCollect", "#SkyyPCancel", "#SkyyPUnload", "#SkyyPAddF")),
            "BTN the ADD FUEL view: 0.8.22's queue line + output row (Collect / Cancel / Unload), the fuel list, no 3 lists")
    jfield(CP.class_, "fuelPick").setBoolean(pp, False)
    drain()
'''
_fur_src = _src[:_a] + _src[_c:_d] + "    fresh(base)\n" + _CASES
_fur_src = _fur_src.replace("def new_cases(K, L, scratch):", "def fur_cases(K, L, scratch):", 1)
_ns = dict(T15.__dict__)
exec(compile(_fur_src, __file__ + " (FUR on the 0.8.15 fixture)", "exec"), _ns)


def run_fur(out, jar, scratch, home):
    T15.new_cases = _ns["fur_cases"]
    T15.run_new(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("fur", run_fur), ("live", T15.T0810.run_live10)], __file__, live=(T15.BETA, "Skyy_SkyySacks"))
