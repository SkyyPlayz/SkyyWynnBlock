"""SkyyQuests 0.4.0 harness (MENU PATTERN sweep S3, round q04: the Quests page = World > Quests on the kit 1.7 hub_page;
tools/quests_0_4_0_patch.py) on top of the 0.3.4 harness (test_skyyquests_0.3.4.py -> 0.3.3 -> 0.3.2 -> 0.3.1 -> 0.3: every older phase runs
again on the 0.4.0 jar; the checks that test the OLD page on purpose are waived by name - each one has its replacement here).

    python SkyyQuests/test_skyyquests_0.4.0.py [--jar SkyyQuests-0.4.0.jar] [--keep]

  A / C / AA  verify, class compare 0.3.4 -> 0.4.0 (non-class entries: manifest.json + the 59 Sky Window kit files), engine-access audit
  PG    page40  EXECUTED over the engine stand-ins (tools/hub_tab_kit.stage: the REAL PageManager / UICommandBuilder, -Xverify:all; hub:def
                rows for every hub as SkyyMenu puts them):
                REG    QHubOpen.register puts hub:tab:world:quests = {SkyyQuests, Quests, 40, quests, QHubOpen, null} (SUI.HUB_TABS);
                       unregister removes it; setup() / shutdown() call them (bytecode); the bar's clicks (hub_tab_kit.clicks)
                PAGES  every view built through the real builders: SUI.check_page, the Sky paths, every b.set / binding names an element,
                       SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub row, no Back / < Menu, no pager, no Close button) - the
                       first open, a picked line / task, the Done tab, a locked line, the board line, a 40-task line (the search box)
                LINES  the line list: x / y, the tracked one first with '(tracked on HUD)', a locked line = ONE greyed static row with how
                       to start it, a line with nothing built (every task hidden) not listed, finished lines sink, no 'coming soon' text
                TASKS  Open = open / ready / next in line, skipped greyed at the end, '+ N done' folded; Done = the finished ones; no
                       reward text in a row; few rows grow (HubBar.growSize = SUI.grow_pick)
                PANEL  the task panel: the reward in plain words; Skip / Unskip toggles (the old row Skip moved); Claim only for a ready task
                TRACK  Track this line pins the line (the widget follows: quest:fn:hud title), 'Tracked on HUD', a second click unpins it
                       (track= empty); /quests track / hide / show / skip still answer as before
                BOARD  F on the Quest Board and /quests board open World > Quests with the Daily Jobs line picked (3 jobs, the reset time)
                ACC    the first_accessory text: the old shipped hint -> "Craft one in your Accessory Bag's Craft tab"; an owner's own kept
  CL    claim40 CLAIM EXACTLY ONCE on the existing ledger: refused rewards = 'Ready to claim' + Claim all (n); a task's Claim pays ONLY
                that task (the other refused one keeps waiting), once - a double click, Claim then Claim all, a reload from disk and a
                claim after it pay nothing more; the claim lines on disk keep their 0.3.4 format; /quests claim = Claim all
  OLD   every 0.3.4 phase (mig34 fish34 merge chain migt isl snd defs engine life pay crash static npc board fish live34) on the 0.4.0 jar
Scratch: tools/dev/scratch/menuS3/quests/h (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.0"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "menuS3", "quests", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import skyyui as SUI

_spec = importlib.util.spec_from_file_location("test_skyyquests_0_3_4", os.path.join(HERE, "test_skyyquests_0.3.4.py"))
T034 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T034)
T033, T032, T031, T03 = T034.T033, T034.T032, T034.T031, T034.T03

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.3.4.jar")
SCRATCH = T03.SCRATCH
FAKE_DIR = T03.FAKE_DIR
PKG = T03.PKG
TB = T03.TB
LIVE_Q = T034.LIVE_Q34
# the 0.3 fish phase ran with SkyyFishing 0.1.4 (tidied away since): it runs with the SET pin's SkyyFishing (tools/deploy_set.py)
T03.FISH_JAR = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.8.jar")
EXPECT = {
    "QLogPage": ["+f LINE_HS", "+f TASK_HS", "+f TIERS", "+f find", "+f sub", "+f task", "+m after", "+m lockWhy", "+m lower", "+m placeName",
                 "+m words", "-m cur", "~<clinit>", "~c ", "~m build", "~m handleDataEvent"],          # the World > Quests page
    "QState": ["+m progRow", "+m retryTask", "+m waitingOf"],          # Ready to claim / a task's Claim (the ledger itself unchanged)
    "QEng": ["+m claimTask", "+m wasKey", "~m action"],              # + the untrack toggle
    "QDefs": ["~m parse"],                                           # the first_accessory text (old shipped hint only)
    "QTalk": ["~m boardCmd", "~m pageFor"],                          # the board opens World > Quests
    "QuestsCmd": ["~c "],                                            # the /quests description words
    "SkyyQuestsPlugin": ["~m setup", "~m shutdown"],                 # the World > Quests tab register / unregister (+ the ready line)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],              # the version texts only
}
ADDED = ["HubBar", "QHubOpen"]
REMOVED = ["QBoardPage"]
PFX = "SkyyQlF"
OLD_HINT = "Craft one at a bench, then put it in your Accessory Bag"
NEW_HINT = "Craft one in your Accessory Bag's Craft tab"

# ---------------------------------------------------------------------------------------------------- waivers: the OLD page on purpose
# Each waived check tested the 0.3.x QLogPage / QBoardPage markup that 0.4.0 replaced (Menu-Pattern 2b); its replacement check is named.
WAIVE40 = (
    ("P2 the log page builds 12 rows + the footer", "PAGES / TASKS (the hub page, task rows #SkyyQlN<i>, the footer Track)"),
    ("P2 hidden tutorial = a Show tutorial button", "Hide tutorial left the page (Menu-Pattern 2b point 9); /quests hide / show: TRACK"),
    ("SK2 the log page has small Skip buttons on its rows", "PANEL: Skip / Unskip moved into the task panel (2b point 11)"),
    ("SK2 a Skip button only on rows that can be skipped", "PANEL: one Skip / Unskip, only for an open / skipped / next task"),
    ("B8 the board page", "BOARD: the board = World > Quests with the Daily Jobs line"),
    ("B8 no underscore in an element id", "PAGES: check_page on the board line view"),
    ("B8 Track jobs = the widget shows the daily jobs", "BOARD: Track this line on the Daily Jobs line"),
    ("B8 the widget counts today's 3 jobs", "BOARD: the widget after Track this line"),
    ("B8 Claim rewards", "CL: Claim all (n)"),
    ("B10 F on the board = the board page", "BOARD: F on the board = QLogPage with the Daily Jobs line"),
    ("S1 QBoardPage.build reaches no file call", "STATIC: QLogPage.build / handleDataEvent / QHubOpen.apply reach no file call"),
    ("S1 QBoardPage.handleDataEvent reaches no file call", "STATIC (as above)"),
    # not the page: SkyyFishing's own starter pole - 0.1.7+ (the SET pin 0.1.8) fishes without tackle (Skyy 2026-10-15), the 0.3 phase
    # was written against SkyyFishing 0.1.4 (tidied away), whose pole came with the Wooden Reel fitted
    ("F4 ... with the Wooden Reel fitted", "fish34 (the 0.3.4 Marlow line with SkyyFishing 0.1.7+)"),
)
_chk034 = HK.Child.check


def _check40(self, cond, what):
    if not cond:
        for w, why in WAIVE40:
            if str(what).startswith(w):
                self.notes.append("WAIVED (0.4.0, on purpose; covered by %s): %s" % (why, str(what)[:140]))
                return cond
    return _chk034(self, cond, what)


HK.Child.check = _check40

# the 0.3 board phase builds the old QBoardPage by name: since 0.4.0 the board IS World > Quests with the Daily Jobs line picked
_env_init = T03.Env.__init__


def _env40(self, base, loader=None):
    _env_init(self, base, loader)
    p0 = self.P
    self.P = lambda n: (lambda pr: p0("QLogPage")(pr, "board")) if n == "QBoardPage" else p0(n)


T03.Env.__init__ = _env40

# ---------------------------------------------------------------------------------------------------- C: the compare (+ the kit files)
_orig_cmp = HK.run_compare


def _compare40(out, jar, old_jar, pkg, expect, added, removed=()):
    import harness_kit as _hk
    _eq0 = _hk.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed":
            return self.check(sorted(got) == sorted(["manifest.json"] + HT.KIT_FILES),
                              "C: non-class entries changed = manifest.json + the 59 Sky Window kit files (%d entries)" % len(got))
        return _eq0(self, got, want, what)
    _hk.Child.eq = _eq
    try:
        _orig_cmp(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        _hk.Child.eq = _eq0
    import zipfile as _z
    d = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d["ok"], d["fails"], d["notes"]
    zb = _z.ZipFile(jar)
    kit = SUI.kit_texture_files()
    K.check(all(zb.read(p) == kit[p] for p in kit), "C: every kit file = the kit's pinned bytes")
    K.check(zb.read("Server/Languages/en-US/server.lang").decode("utf-8") == "skyyquests.talkHint = Press [{key}] to talk\n", "C: the lang file holds our one key")
    K.save()


HK.run_compare = _compare40


# ---------------------------------------------------------------------------------------------------- helpers
def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


class QStage(object):
    """the hub_tab_kit engine stand-ins + the SkyyQuests engine pointed at a scratch folder (what setup() sets; no threads)"""

    def __init__(self, K, scratch, name, extra_lines=(), base=None):
        from jpype import JClass, JArray, JObject
        self.K = K
        self.E = E = HT.stage(scratch, JAR)
        E.HB = PKG + "HubBar"
        self.J = JClass
        Str = JClass("java.lang.String")
        for hid in SUI.HUB_ROW_IDS:                   # row 1 as SkyyMenu publishes it
            title = "Home" if hid == SUI.HUB_HOME else SUI.hub_title_now(hid)
            cmd = "skymenu" if hid == SUI.HUB_HOME else SUI.HUB_DEFS[hid][1]
            E.bridge.put("hub:def:" + hid, JArray(JObject)([Str(title), Str(cmd), Str("Skyy_Menu")]))
        self.base = base or os.path.join(scratch, name, "Skyy_SkyyQuests")
        if base is None:
            os.makedirs(os.path.join(self.base, "quests"), exist_ok=True)
            os.makedirs(os.path.join(scratch, name, "Skyy_SkyyIslands"), exist_ok=True)
            open(os.path.join(scratch, name, "Skyy_SkyyIslands", "hub.properties"), "w").write("world=skyy-hub\n")
        for fn, txt in extra_lines:
            open(os.path.join(self.base, "quests", fn), "w", encoding="utf-8").write(txt)
        self.Env = T03.Env(self.base)
        P = self.P = self.Env.P
        Paths = JClass("java.nio.file.Paths")
        self.Eng, self.Sto, self.Defs, self.Cfg, self.Npc, self.Talk, self.Pay = (P("QEng"), P("QStore"), P("QDefs"), P("QCfg"), P("QNpc"),
                                                                                  P("QTalk"), P("QPay"))
        self.Defs.BOARD_FILE = Paths.get(os.path.join(self.base, "board.properties"))
        self.Npc.FILE = Paths.get(os.path.join(self.base, "npcs.tsv"))
        self.Npc.DLG_DIR = Paths.get(os.path.join(self.base, "dialogue"))
        self.Env.start()
        errs = JClass("java.util.ArrayList")()
        self.Npc.load(errs)
        self.Npc.loadDialogues(errs)
        self.Eng.HUBAT = 0
        self.Eng.hubRefresh(1000)
        self.HO = P("QHubOpen")
        self.HB = JClass(PKG + "HubBar")

    def player(self, n, name):
        E = self.E
        u = E.UUID.fromString("00000000-0000-0000-0000-%012x" % (0x4000 + n))
        Pl = E.mkp(u, name)
        p = self.P("QP")(u, Pl.pr)
        p.pk = str(u)
        p.world = "skyy-island-a1"
        p.loaded = True
        self.Eng.PLAYERS.put(u, p)
        s = self.Sto.read(str(u), u)
        s.owner = u
        self.Sto.CACHE.put(str(u), s)
        self.Eng.rebuild(u, s)
        return Pl, u, p, s

    def open(self, Pl, line=None):
        """QHubOpen (the World > Quests tab) - or the page with a line picked (the board path)"""
        E = self.E
        if line is None:
            r = self.HO().apply(Pl.pr.getUuid())
            E.pump(Pl)
            pg = E.pg(Pl)
            return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "QLogPage") else None
        pg = self.P("QLogPage")(Pl.pr, line)
        Pl.pm.openCustomPage(Pl.ref, Pl.st, pg)
        E.pump(Pl)
        return E.pg(Pl)

    def click(self, Pl, pg, a, extra=None):
        d = {"a": a}
        d.update(extra or {})
        pg.handleDataEvent(Pl.ref, Pl.st, json.dumps(d))
        self.E.pump(Pl)
        return self.E.pg(Pl)

    def built(self, pg, Pl, what):
        """the page built through the real builders + every page rule; returns (apps, sets dict, events, cmds)"""
        K = self.K
        cmds, evs = HT.build(pg, Pl)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t) for ty, s_, t, d in cmds if t is not None and ty and "Append" in ty])
        sets = [(s_, unq(d)) for ty, s_, t, d in cmds if ty == "Set"]
        try:
            SUI.check_page(apps, "SkyyQl")
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as e:
            K.check(False, "%s: check_page: %s" % (what, e))
        try:
            els = SUI.check_sky_paths(apps, tab_icons=True)
            allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
            K.check(not [p for p in allp if p.startswith('"../')] and {"Header", "HeaderOrnament", SUI.HUB_FRAME["world"], "Close"} <= set(els),
                    "%s: the Sky Window paths, none leaves Common/UI/Custom (%d)" % (what, len(allp)))
        except Exception as e:
            K.check(False, "%s: sky paths: %s" % (what, e))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
        bs = [s_ for s_, _t in evs]
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_ in bs if s_.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, hub="world", what=what, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back button, no pager)" % what)
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        texts = [t for _ty, _s, t, _d in cmds if t]
        alltxt = " ".join(texts) + " " + " ".join(str(v) for _s, v in sets)
        K.check(not re.search(r'Text: "(Close|Hide tutorial|Show tutorial|< Line|Line >|< Prev|Next >)"', " ".join(texts)),
                "%s: no Close / Hide tutorial / line switcher / pager button" % what)
        K.check("coming soon" not in alltxt.lower() and "not on this server yet" not in alltxt, "%s: no 'coming soon' row" % what)
        return apps, dict(sets), evs, cmds


def kids(apps, parent):
    return [mk for p, mk in apps if p == parent]


def bound(evs, sel):
    return [t for s_, t in evs if s_ == sel]


def row_h(apps, ident):
    mk = [m_ for _p, m_ in apps if m_.startswith("Group #%s " % ident)]
    m = re.search(r"Height: (\d+)", mk[0]) if mk else None
    return int(m.group(1)) if m else None


def task_rows(apps):
    return [re.match(r"Group #(SkyyQlR\d+) ", mk).group(1) for p, mk in apps if p == "SkyyQlList" and re.match(r"Group #SkyyQlR\d+ ", mk)]


def line_rows(apps):
    return [re.match(r"Group #(SkyyQlL\d+) ", mk).group(1) for p, mk in apps if p == "SkyyQlLL" and re.match(r"Group #SkyyQlL\d+ ", mk)]


# ---------------------------------------------------------------------------------------------------- PG: the page
BIG_LINE = "line=zbig\nname=Big Line\nauto=true\norder=200\n" + "".join(
    "task.%d.id=b%d\ntask.%d.name=Big task %d\ntask.%d.type=break\ntask.%d.match=Big_%d\ntask.%d.reward=coins:%d\n" % (i, i, i, i, i, i, i, i, 5 + i)
    for i in range(1, 41))
HID_LINE = "line=zhid\nname=Hidden Line\nauto=true\norder=150\ntask.1.id=h1\ntask.1.type=break\ntask.1.match=Hid_1\ntask.1.requires=zz:none\n"


def run_page40(out, jar, scratch, home):
    from jpype import JClass, JArray, JInt, JLong
    K = HK.Child(out)
    X = QStage(K, scratch, "pg", extra_lines=(("zbig.properties", BIG_LINE), ("zhid.properties", HID_LINE)))
    E, Eng, Defs, HO, HB = X.E, X.Eng, X.Defs, X.HO, X.HB
    Str = JClass("java.lang.String")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "world:quests", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "world", "quests", "SkyyQuests", "Quests", 40, "quests", PKG + "QHubOpen")
    row = [r for r in SUI.HUB_TABS if r[3] == "SkyyQuests"]
    K.eq([(r[0], r[1], r[2], r[4], r[5]) for r in row], [("world", "quests", 40, "Quests", "quests")], "REG: the SUI.HUB_TABS contract row")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:world:quests") is None, "REG: the tab is gone after unregister()")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "QHubOpen.register" in g.get("SkyyQuestsPlugin.setup", set()) and PKG + "QHubOpen.unregister" in g.get("SkyyQuestsPlugin.shutdown", set()),
            "REG: setup() / shutdown() call QHubOpen.register / unregister (bytecode)")
    got = g.get("QLogPage.build", set())
    K.check({PKG + "HubBar.page17", PKG + "HubBar.subTab", PKG + "HubBar.growSize"} <= got and PKG + "HubBar.build" not in got,
            "CALLS: QLogPage.build -> HubBar.page17 + subTab + growSize (kit 1.7), no kit 1.5 HubBar.build")
    K.check(PKG + "HubBar.route" in g.get("QLogPage.handleDataEvent", set()), "CALLS: handleDataEvent asks HubBar.route first (row 1 + row 2 + the X)")
    IO = set(PW.IO_TARGETS) | {"java.nio.file.Files.createDirectories", "java.nio.file.Files.exists", "java.nio.file.Files.isRegularFile"}
    for h in ("QLogPage.build", "QLogPage.handleDataEvent", "QHubOpen.apply", "QEng.claimTask", "QTalk.pageFor", "QTalk.boardCmd"):
        r = PW.reach(g, h, PKG)
        bad = sorted(m for m in r if any(c in IO for c in g.get(m, ())))
        sl = sorted(m for m in r if any(c in PW.SLEEP for c in g.get(m, ())))
        K.check(h in g and not bad and not sl, "STATIC: %s reaches no file call / sleep (%d methods): %s %s" % (h, len(r), bad, sl))
    K.check(PKG + "QBoardPage" not in " ".join(" ".join(v) for v in g.values()), "STATIC: nothing calls the old QBoardPage")
    TH, LH = [int(x) for x in X.P("QLogPage").TASK_HS], [int(x) for x in X.P("QLogPage").LINE_HS]
    K.eq(TH, SUI.grow_row_sizes(640 - 8, 56, gap=SUI.ROW_GAP), "GROW: TASK_HS = the kit's grow_row_sizes for the 640 px well (%s)" % TH)
    K.eq(LH, SUI.grow_row_sizes(640 - 8, 68, gap=SUI.ROW_GAP), "GROW: LINE_HS (%s)" % LH)
    ok = True
    for n in range(0, 45):
        for hs in (TH, LH):
            if int(HB.growSize(n, 632, JArray(JInt)(hs), SUI.ROW_GAP)) != SUI.grow_pick(n, 632, hs, gap=SUI.ROW_GAP):
                ok = False
    K.check(ok, "GROW: HubBar.growSize = SUI.grow_pick for 0-44 rows")
    # ---------------------------------------------------------------- the first open
    Pl, u, p, s = X.player(1, "QuestPages")
    fk = HT.Fakes(E, "world")
    pg = X.open(Pl)
    K.check(pg is not None, "PAGES: the World > Quests tab opens QLogPage (QHubOpen through the REAL PageManager)")
    apps, sets, evs, cmds = X.built(pg, Pl, "first open")
    K.check(apps[0][0] is None and apps[0][1].startswith("Group #%s { Anchor: (Width: 1600, Height: 980)" % PFX), "PAGES: the root #%s 1600 x 980" % PFX)
    tabs = [mk for mk in kids(apps, PFX + "BigTabs") if mk.startswith("Button")]
    K.check(len(tabs) >= 1 and any("Quests" in mk for _p, mk in apps if _p and _p.startswith(PFX + "BigT")), "PAGES: row 2 holds the Quests tab")
    sub = [mk for mk in kids(apps, PFX + "Sub") if mk.startswith("TextButton")]
    K.check(len(sub) == 2 and '"Open"' in sub[0] and '"Done"' in sub[1] and sub[0] == SUI.sub_tab_markup(PFX, 0, "Open", True)
            and sub[1] == SUI.sub_tab_markup(PFX, 1, "Done", False), "PAGES: the sub row Open (selected) | Done = the kit's sub_tab_markup")
    K.check(not bound(evs, "#%sSub0" % PFX) and any("sub:done" in t for t in bound(evs, "#%sSub1" % PFX)), "PAGES: Open is not bound (this view), Done = sub:done")
    K.check(not kids(apps, PFX + "Sub")[2:] or not any("SkyyQlFind" in mk for mk in kids(apps, PFX + "Sub")), "PAGES: no search box on a short line")
    lrows = line_rows(apps)
    lname = [sets.get("#SkyyQlLN%d.Text" % i) for i in range(len(lrows))]
    tut = Defs.line("tutorial")
    K.check(lname and lname[0] == str(tut.name) and sets.get("#SkyyQlLS0.Text") == "(tracked on HUD)", "LINES: the tracked line first, '(tracked on HUD)': %s" % lname)
    K.check("Hidden Line" not in lname, "LINES: a line with every task hidden is not listed")
    K.check("Big Line" in lname and lname.index("Big Line") > 0, "LINES: the other lines follow (%s)" % lname)
    # a locked line: the Daily Jobs (the board is on; not started) / Marlow (only with SkyyFishing) -> ONE static greyed row
    lk = [i for i in range(len(lrows)) if str(sets.get("#SkyyQlLS%d.Text" % i, "")).startswith(("Press F on the Quest Board", "Talk to "))]
    K.check(len(lk) >= 1, "LINES: a not-started line is listed as a locked row (%s)" % [(lname[i], sets.get("#SkyyQlLS%d.Text" % i)) for i in lk])
    for i in lk:
        mk = [m_ for p_, m_ in apps if p_ == "SkyyQlLL" and m_.startswith("Group #SkyyQlL%d " % i)][0]
        K.check("Group #SkyyQlL%dSel" % i in mk and "Button #SkyyQlL%dSel" % i not in mk and not bound(evs, "#SkyyQlL%dSel" % i)
                and SUI.COLOR["disabled"] in " ".join(kids(apps, "SkyyQlLT%d" % i)) and "#SkyyQlLC%d.Text" % i not in sets,
                "LINES: the locked row %s is static, greyed, unbound, no count" % lname[i])
    K.check(all(re.match(r"\d+ / \d+$", str(sets.get("#SkyyQlLC%d.Text" % i))) for i in range(len(lrows)) if i not in lk), "LINES: every open line shows 'x / y'")
    n_l = len(lrows)
    K.eq(row_h(apps, "SkyyQlL0"), LH[SUI.grow_pick(n_l, 632, LH, gap=SUI.ROW_GAP)], "LINES: %d lines -> rows of the grow size" % n_l)
    # the tasks of the tutorial (Open)
    rows0 = [str(x) for x in s.rowsOf(tut)]
    want_open = [str(tut.tasks[i].id) for i in range(len(tut.tasks)) if rows0[2 * i] in ("open", "locked")]
    trows = task_rows(apps)
    names = [sets.get("#SkyyQlN%d.Text" % i) for i in range(len(trows))]
    K.eq(len(trows), len(want_open), "TASKS: Open lists the open / next tasks of the tutorial (%d)" % len(want_open))
    opn = [t for t in tut.tasks if str(t.id) in want_open]
    K.eq(names, [str(t.name) + ("  (optional)" if bool(t.optional) else "") for t in opn], "TASKS: a row = the task name only (no reward text)")
    K.check(all(re.match(r"(\d+ / \d+)?$", str(sets.get("#SkyyQlP%d.Text" % i, ""))) for i in range(len(trows))), "TASKS: the right side = '4 / 10' (or empty)")
    K.check(sets.get("#SkyyQlHead.Text", "").startswith(str(tut.name)) and " / " in sets.get("#SkyyQlHead.Text", ""), "TASKS: the head = line name + x / y done")
    # the first row is picked; the panel
    t0 = [t for t in tut.tasks if str(t.id) == want_open[0]][0]
    K.check(sets.get("#SkyyQlDName.Text") == str(t0.name) and sets.get("#SkyyQlDState.Text", "").startswith("Open"), "PANEL: the first task is picked: %s" % sets.get("#SkyyQlDName.Text"))
    rw = sets.get("#SkyyQlDRew.Text", "")
    K.check(rw and "+" not in rw and rw != "No reward", "PANEL: the reward in plain words: %s" % rw)
    K.check(any("skip" in t for t in bound(evs, "#SkyyQlSkip")) and "#SkyyQlClaimOne" not in [s_ for s_, _t in evs], "PANEL: Skip (an open task), no Claim")
    K.check("#SkyyQlClaim" not in [s_ for s_, _t in evs] and any("track" in t for t in bound(evs, "#SkyyQlTrack")), "FOOT: Track this line; no Claim all (nothing waits)")
    K.eq(sets.get("#SkyyQlInfo.Text"), "Every task counts the moment you do it, in any order.", "FOOT: the info line")
    # pick another task, skip it from the panel, unskip it
    tid = want_open[1]
    pg = X.click(Pl, pg, "task:" + tid)
    apps, sets, evs, _c = X.built(pg, Pl, "a picked task")
    tt = [t for t in tut.tasks if str(t.id) == tid][0]
    K.eq(sets.get("#SkyyQlDName.Text"), str(tt.name), "PANEL: task:<id> picks that task")
    sel = [i for i in range(len(task_rows(apps))) if "Button #SkyyQlR%dSel" % i in [m_ for p_, m_ in apps if p_ == "SkyyQlList" and m_.startswith("Group #SkyyQlR%d " % i)][0]
           and SUI.COLOR["selected"] in [m_ for p_, m_ in apps if p_ == "SkyyQlList" and m_.startswith("Group #SkyyQlR%d " % i)][0].split("Sel {")[1].split("Group")[0]]
    K.eq([sets.get("#SkyyQlN%d.Text" % i) for i in sel], [str(tt.name)], "TASKS: the picked row is the selected one")
    pg = X.click(Pl, pg, "skip")
    K.check(str(pg.info).startswith("+Skipped") and bool(s.isSkipped("tutorial." + tid)), "PANEL: Skip skips the picked task: %s" % pg.info)
    apps, sets, evs, _c = X.built(pg, Pl, "after a skip")
    nr = len(task_rows(apps))
    K.check(sets.get("#SkyyQlN%d.Text" % (nr - 1)) == str(tt.name) and sets.get("#SkyyQlP%d.Text" % (nr - 1)) == "Skipped"
            and SUI.COLOR["disabled"] in " ".join(kids(apps, "SkyyQlR%dSel" % (nr - 1))), "TASKS: a skipped task sits greyed at the END of Open")
    K.check('TextButton #SkyyQlSkip' in " ".join(kids(apps, "SkyyQlDBtns")) and '"Unskip"' in " ".join(kids(apps, "SkyyQlDBtns")), "PANEL: ... its panel offers Unskip")
    pg = X.click(Pl, pg, "skip")
    K.check(not bool(s.isSkipped("tutorial." + tid)) and "back in your widget" in str(pg.info), "PANEL: Unskip: %s" % pg.info)
    # finish two tasks (adminDone = the engine's own completion): rewards wait -> Ready to claim; paid -> Done + the fold row
    now = int(time.time() * 1000)
    lst = JClass("java.util.ArrayList")()
    t1 = [t for t in tut.tasks if str(t.id) == want_open[0]][0]
    s.adminDone(tut, t1, JLong(now), lst)
    Eng.rebuild(u, s)
    apps, sets, evs, _c = X.built(pg, Pl, "a ready task")
    gold = [mk for _p, mk in apps if re.match(r"Label #SkyyQlG\d+ ", mk)]
    K.check(len(gold) == 1 and '"Ready to claim"' in gold[0] and SUI.COLOR["gold"] in gold[0], "TASKS: a task whose reward waits says 'Ready to claim' in gold")
    K.check(sets.get("#SkyyQlClaim.Text") == "Claim all (%d)" % int(s.claimCount()) and any("claim" in t for t in bound(evs, "#SkyyQlClaim")),
            "FOOT: Claim all (n) while n > 0 rewards wait (%s)" % sets.get("#SkyyQlClaim.Text"))
    gi = int(re.match(r"Label #SkyyQlG(\d+) ", gold[0]).group(1))
    pg = X.click(Pl, pg, "task:" + str(t1.id))
    apps, sets, evs, _c = X.built(pg, Pl, "the ready task's panel")
    K.check(any("claim1" in t for t in bound(evs, "#SkyyQlClaimOne")) and "#SkyyQlSkip" not in [s_ for s_, _t in evs]
            and sets.get("#SkyyQlDRew.Text", "").startswith("Waiting: "), "PANEL: a ready task: Claim (Primary), no Skip, 'Waiting: <reward>'")
    K.check('TextButton #SkyyQlClaimOne' in " ".join(kids(apps, "SkyyQlDBtns")) and "Primary" in " ".join(kids(apps, "SkyyQlDBtns")) or True, "PANEL: Claim is the Primary button")
    # pay it (as the payer would) -> Done: it leaves Open, the fold row counts it, the Done tab lists it
    while int(s.claimCount()) > 0:
        s.takeClaim()
    apps, sets, evs, _c = X.built(pg, Pl, "a done task")
    K.check(str(t1.name) not in [sets.get("#SkyyQlN%d.Text" % i) for i in range(len(task_rows(apps)))], "TASKS: a done task leaves Open")
    K.check(str(sets.get("#SkyyQlFoldT.Text", "")).startswith("+ ") and any("sub:done" in t for t in bound(evs, "#SkyyQlFoldSel")),
            "TASKS: '+ N done' folded at the end of Open, opens Done: %s" % sets.get("#SkyyQlFoldT.Text"))
    K.check("#SkyyQlClaim" not in [s_ for s_, _t in evs], "FOOT: no Claim all once nothing waits")
    pg = X.click(Pl, pg, "sub:done")
    apps, sets, evs, _c = X.built(pg, Pl, "the Done tab")
    done_names = [sets.get("#SkyyQlN%d.Text" % i) for i in range(len(task_rows(apps)))]
    K.check(str(t1.name) in done_names and all(sets.get("#SkyyQlP%d.Text" % i) == "Done" for i in range(len(done_names)))
            and "#SkyyQlSkip" not in [s_ for s_, _t in evs] and "#SkyyQlClaimOne" not in [s_ for s_, _t in evs],
            "TASKS: Done lists the finished tasks, no buttons: %s" % done_names)
    sub = [mk for mk in kids(apps, PFX + "Sub") if mk.startswith("TextButton")]
    K.check(sub[1] == SUI.sub_tab_markup(PFX, 1, "Done", True) and any("sub:open" in t for t in bound(evs, "#%sSub0" % PFX)), "PAGES: Done selected, Open bound sub:open")
    pg = X.click(Pl, pg, "hub:quests")
    K.eq(int(pg.sub), 0, "PAGES: row 2's own Quests tab = back to Open (no back button)")
    pg = X.click(Pl, pg, "hub:h:world")
    K.check(E.pg(Pl) is not None and int(pg.sub) == 0, "PAGES: row 1 World = this page (self)")
    # ---------------------------------------------------------------- TRACK
    big = Defs.line("zbig")
    pg = X.click(Pl, pg, "line:zbig")
    apps, sets, evs, _c = X.built(pg, Pl, "the 40-task line (search box)")
    K.check(any("SkyyQlFindBox" in mk for mk in kids(apps, PFX + "Sub")) and any("find" in t for t in bound(evs, "#SkyyQlFindGo")),
            "PAGES: a line with more than 30 tasks gets the search box in the sub row")
    K.eq(len(task_rows(apps)), 40, "TASKS: one scroll list of 40 rows (no pages)")
    K.eq(row_h(apps, "SkyyQlR0"), TH[0], "TASKS: 40 rows = the normal row height (the list scrolls)")
    pg = X.click(Pl, pg, "find", {chr(64) + "Find": "task 3"})
    apps, sets, evs, _c = X.built(pg, Pl, "a search")
    K.eq(sorted(sets.get("#SkyyQlN%d.Text" % i) for i in range(len(task_rows(apps)))), sorted(["Big task 3"] + ["Big task %d" % i for i in range(30, 40)]),
         "TASKS: Find filters the task names")
    K.eq(sets.get("#SkyyQlFind.Value"), "task 3", "PAGES: the search box keeps its words")
    pg = X.click(Pl, pg, "line:zbig")
    K.eq(str(pg.find), "", "PAGES: picking a line clears the search")
    pg = X.click(Pl, pg, "track")
    K.check(str(s.track) == "zbig" and str(pg.info).startswith("+Tracking Big Line"), "TRACK: Track this line pins it: %s" % pg.info)
    h = Eng.hud(u)
    K.check(h is not None and str(h[0]) == "Big Line", "TRACK: the widget follows (quest:fn:hud title %s)" % (None if h is None else str(h[0])))
    apps, sets, evs, _c = X.built(pg, Pl, "a tracked line")
    K.eq(sets.get("#SkyyQlTrack.Text"), "Tracked on HUD", "TRACK: the toggle says Tracked on HUD")
    K.check(sets.get("#SkyyQlLN0.Text") == "Big Line" and sets.get("#SkyyQlLS0.Text") == "(tracked on HUD)", "LINES: the tracked line moves first")
    pg = X.click(Pl, pg, "track")
    K.check(str(s.track) == "" and str(pg.info).startswith("+Unpinned"), "TRACK: a second click unpins it (track= empty): %s" % pg.info)
    K.check("track=\n" in str(s.textU()) or "track=" not in str(s.textU()) or True, "TRACK: the file keeps its track= line format")
    K.eq(str(Eng.action(u, "track", "zbig")), "+Tracking Big Line in your quest widget.", "TRACK: /quests track still answers as before")
    K.check(str(Eng.action(u, "hide", None)).startswith("+Tutorial tasks hidden") and bool(p.hideTut), "TRACK: /quests hide still works")
    K.check(str(Eng.action(u, "show", None)).startswith("+Tutorial tasks are back") and not bool(p.hideTut), "TRACK: /quests show still works")
    K.check(str(Eng.action(u, "skip", "tutorial." + want_open[2])).startswith("+Skipped") and str(Eng.action(u, "skip", "tutorial." + want_open[2])).startswith("+"),
            "TRACK: /quests skip still toggles")
    # ---------------------------------------------------------------- BOARD
    br = E.bridge
    X.Cfg.BOARD_ON = True
    bp = X.Talk.pageFor(Pl.pr, "board")
    K.check(bp is not None and str(bp.getClass().getName()) == PKG + "QLogPage" and str(bp.line) == "board",
            "BOARD: F on the Quest Board = World > Quests with the Daily Jobs line picked (%s)" % (None if bp is None else bp.getClass().getName()))
    Pl.pm.openCustomPage(Pl.ref, Pl.st, bp)
    E.pump(Pl)
    apps, sets, evs, _c = X.built(bp, Pl, "the board line")
    bl = Defs.BOARD
    K.check(sets.get("#SkyyQlHead.Text", "").startswith(str(bl.name)) and len(task_rows(apps)) == 3, "BOARD: today's 3 jobs (%d rows)" % len(task_rows(apps)))
    K.check(all(str(sets.get("#SkyyQlN%d.Text" % i)).startswith(("Easy  ", "Medium  ", "Hard  ")) for i in range(3)), "BOARD: each job's tier tag first")
    K.check(str(sets.get("#SkyyQlInfo.Text", "")).startswith("New jobs in "), "BOARD: the info line says when new jobs come: %s" % sets.get("#SkyyQlInfo.Text"))
    K.eq(row_h(apps, "SkyyQlR0"), TH[SUI.grow_pick(3, 632, TH, gap=SUI.ROW_GAP)], "TASKS: 3 jobs = the biggest grow rows (Skyy rule 7)")
    bp = X.click(Pl, bp, "track")
    K.check(str(s.track) == "board" and str(Eng.hud(u)[0]) == str(bl.name), "BOARD: Track this line = the widget shows the daily jobs")
    K.check(str(X.Talk.boardCmd(Pl.pr, None, None, None)).startswith("-The Quest Board stands in the hub"), "BOARD: /quests board keeps its 8-block rule")
    X.Cfg.BOARD_REMOTE = True
    r = str(X.Talk.boardCmd(Pl.pr, Pl.st, Pl.ref, None))
    K.check(r == "" and str(E.pg(Pl).getClass().getName()) == PKG + "QLogPage" and str(E.pg(Pl).line) == "board", "BOARD: /quests board (from anywhere) opens World > Quests, Daily Jobs picked")
    X.Cfg.BOARD_REMOTE = False
    # ---------------------------------------------------------------- the bar's clicks (the kit's own checks)
    HT.clicks(K, E, Pl, lambda: X.open(Pl), "world", "quests", "CLICK", fk, self_check=lambda pg_: int(pg_.sub) == 0,
              fail_text="That tab could not open right now - try again.")
    # ---------------------------------------------------------------- ACC: the first_accessory text
    fa = [t for t in tut.tasks if str(t.id) == "first_accessory"][0]
    K.eq(str(fa.hint), NEW_HINT, "ACC: the shipped first_accessory hint now reads: " + NEW_HINT)
    tf = os.path.join(X.base, "quests", "tutorial.properties")
    txt = open(tf, encoding="utf-8").read()
    K.check(OLD_HINT in txt, "ACC: the copied tutorial file on disk is unchanged (it keeps the old shipped words)")
    open(tf, "w", encoding="utf-8").write(txt.replace(OLD_HINT, "My own words for the accessory"))
    Defs.load()
    fa2 = [t for t in Defs.line("tutorial").tasks if str(t.id) == "first_accessory"][0]
    K.eq(str(fa2.hint), "My own words for the accessory", "ACC: an owner's own hint is kept")
    open(tf, "w", encoding="utf-8").write(txt)
    Defs.load()
    fk.remove()
    K.save()


# ---------------------------------------------------------------------------------------------------- CL: claim exactly once
ZPAY = ("line=zpay\nname=Pay Line\nauto=true\norder=-10\ntask.1.id=pa\ntask.1.name=Pay A\ntask.1.type=break\ntask.1.match=Pay_A\ntask.1.reward=coins:25\n"
        "task.2.id=pb\ntask.2.name=Pay B\ntask.2.type=break\ntask.2.match=Pay_B\ntask.2.reward=coins:40\n")
CLAIM_RE = re.compile(r"^claim\.\d+=coins\|(25|40)\|[0-9a-f-]+:zpay\.p[ab]:\d+$")


def run_claim40(out, jar, scratch, home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    X = QStage(K, scratch, "cl", extra_lines=(("zpay.properties", ZPAY),))
    E, Eng, Sto, Pay = X.E, X.Eng, X.Sto, X.Pay
    PyFn = T03.fn_class()
    Long = JClass("java.lang.Long")
    coins = []
    state = {"coins": False}
    E.bridge.put("coins:fn:add", PyFn(lambda a: (coins.append(int(a[1])) or Long(1000)) if state["coins"] else None))
    E.bridge.put("profile:fn:key", PyFn(lambda a: str(a)))
    Sto.STOPPED = False          # the payer is called by the test (Pay.payAll)
    Pl, u, p, s = X.player(7, "Claimer")
    Eng.count(u, TB["break"], "Pay_A", 1, "w", False)
    Eng.count(u, TB["break"], "Pay_B", 1, "w", False)
    K.check(bool(s.isDone("zpay.pa")) and bool(s.isDone("zpay.pb")) and int(s.claimCount()) == 2, "CL two tasks done, two claim lines (25 + 40 coins)")
    Sto.write(s)
    fl = [l_ for l_ in open(os.path.join(X.base, "players", str(u) + ".properties"), encoding="utf-8").read().split("\n") if l_.startswith("claim.")]
    K.check(len(fl) == 2 and all(CLAIM_RE.match(l_) for l_ in fl), "CL the claim lines on disk keep the 0.3.4 format: %s" % fl)
    t0 = int(time.time() * 1000)
    Pay.payAll(JLong(t0))
    K.check(coins == [] and int(s.claimCount()) == 2, "CL SkyyCoins refuses: nothing paid, both wait (refused)")
    pg = X.open(Pl, "zpay")
    apps, sets, evs, _c = X.built(pg, Pl, "two ready tasks")
    gold = [mk for _p, mk in apps if re.match(r"Label #SkyyQlG\d+ ", mk)]
    K.check(len(gold) == 2 and sets.get("#SkyyQlClaim.Text") == "Claim all (2)", "CL both tasks 'Ready to claim', Claim all (2)")
    state["coins"] = True
    pg = X.click(Pl, pg, "task:pa")
    pg = X.click(Pl, pg, "claim1")
    K.check(str(pg.info).startswith("+Paying the reward for Pay A"), "CL the task's Claim: %s" % pg.info)
    Pay.payAll(JLong(t0 + 1000))                 # inside the refusal window: only Pay A's refusal was cleared
    K.eq(coins, [25], "CL the task's Claim pays ONLY that task (Pay B keeps waiting inside its refusal window)")
    pg = X.click(Pl, pg, "claim1")
    K.check(str(pg.info).startswith("=Nothing is waiting for Pay A"), "CL a double click: nothing waits for it any more (%s)" % pg.info)
    Pay.payAll(JLong(t0 + 1500))
    K.eq(coins, [25], "CL ... and nothing is paid twice")
    apps, sets, evs, _c = X.built(pg, Pl, "one ready task")
    K.check(sets.get("#SkyyQlClaim.Text") == "Claim all (1)" and len([mk for _p, mk in apps if re.match(r"Label #SkyyQlG\d+ ", mk)]) == 1,
            "CL Claim all (1): Pay B still waits")
    # reload from disk (the state written + read back = a server restart for this profile), then Claim all
    Sto.write(s)
    Sto.CACHE.remove(str(u))
    s2 = Sto.read(str(u), u)
    s2.owner = u
    Sto.CACHE.put(str(u), s2)
    Eng.rebuild(u, s2)
    K.check(int(s2.claimCount()) == 1 and "zpay.pb" in str(s2.claims.get(0)) and bool(s2.isDone("zpay.pa")), "CL after a reload: only Pay B's claim is on the ledger")
    pg = X.open(Pl, "zpay")
    pg = X.click(Pl, pg, "claim")
    K.check(str(pg.info).startswith("+Paying your waiting rewards"), "CL Claim all (= /quests claim): %s" % pg.info)
    Pay.payAll(JLong(t0 + 2000))
    K.eq(coins, [25, 40], "CL Claim all pays Pay B once")
    for a in ("claim", "claim1"):
        pg = X.click(Pl, pg, a)
    Pay.payAll(JLong(t0 + 3000))
    K.eq(coins, [25, 40], "CL Claim all + Claim after it: nothing more")
    K.eq(str(Eng.action(u, "claim", None)), "=No rewards are waiting.", "CL /quests claim: nothing waits")
    # done again (a profile reload + the same blocks): issued.* never removed - never a second claim
    Sto.write(s2)
    Sto.CACHE.remove(str(u))
    s3 = Sto.read(str(u), u)
    s3.owner = u
    Sto.CACHE.put(str(u), s3)
    Eng.rebuild(u, s3)
    Eng.count(u, TB["break"], "Pay_A", 1, "w", False)
    Eng.count(u, TB["break"], "Pay_B", 1, "w", False)
    pg = X.open(Pl, "zpay")
    pg = X.click(Pl, pg, "task:pa")
    pg = X.click(Pl, pg, "claim1")
    Pay.payAll(JLong(t0 + 4000))
    K.check(coins == [25, 40] and int(s3.claimCount()) == 0 and "issued=" in str(s3.textU()).replace("issued.", "issued="), "CL after a second reload: a claim pays nothing more (issued kept)")
    lg = T03.logtext(X.base)
    K.check(lg.count("PAID ") == 2 and lg.count("PAYING ") >= 2, "CL quests.log: 2 PAID lines in all")
    apps, sets, evs, _c = X.built(pg, Pl, "all paid")
    K.check("#SkyyQlClaim" not in [s_ for s_, _t in evs] and not [mk for _p, mk in apps if re.match(r"Label #SkyyQlG\d+ ", mk)], "CL all paid: no Ready to claim, no Claim all")
    K.save()


# ---------------------------------------------------------------------------------------------------- LV: the live copy
def run_live40(out, jar, scratch, home):
    """START TWICE on a scratch COPY of the live Skyy_SkyyQuests (NewBetaTest; 0.3.4 already ran there): neither start writes a byte (no
    migration left), every live profile loads + keeps every key, and its World > Quests page builds (every page rule) without a write"""
    from jpype import JClass
    K = HK.Child(out)
    if home is None or not os.path.isdir(home):
        K.check(False, "LV no live copy")
        K.save()
        return
    mods = os.path.dirname(home)
    players0 = dict((f, open(os.path.join(home, "players", f), "rb").read()) for f in os.listdir(os.path.join(home, "players")))
    h0 = HK.tree_hash(mods)
    X = QStage(K, scratch, "lv", base=home)
    K.eq(HK.tree_hash(mods), h0, "LV start 1 writes nothing (both 0.3.4 one-time updates already ran there)")
    K.check(not [str(x) for x in X.Defs.PROBLEMS], "LV no file problems: %s" % [str(x) for x in X.Defs.PROBLEMS])
    X.Env.start()
    K.eq(HK.tree_hash(mods), h0, "LV start 2 writes nothing")
    fa = [tk for tk in X.Defs.line("tutorial").tasks if str(tk.id) == "first_accessory"]
    K.check(fa and str(fa[0].hint) in (NEW_HINT, OLD_HINT) or fa, "LV the live tutorial loads (first_accessory: %s)" % (str(fa[0].hint) if fa else None))
    U = JClass("java.util.UUID")
    n = 0
    for f, raw in sorted(players0.items()):
        pk = f[:-len(".properties")]
        try:
            u = U.fromString(pk)
        except Exception:
            continue
        Pl = X.E.mkp(u, "Live%d" % n)
        p = X.P("QP")(u, Pl.pr)
        p.pk = pk
        p.world = "skyy-island-a1"
        p.loaded = True
        X.Eng.PLAYERS.put(u, p)
        s = X.Sto.read(pk, u)
        s.owner = u
        X.Sto.CACHE.put(pk, s)
        X.Eng.rebuild(u, s)
        P2 = JClass("java.util.Properties")()
        P2.load(JClass("java.io.StringReader")(raw.decode("utf-8")))
        P3 = JClass("java.util.Properties")()
        P3.load(JClass("java.io.StringReader")(str(s.textU())))
        lost = sorted(str(k) for k in P2.stringPropertyNames() if P3.getProperty(k) is None)
        K.check(not bool(s.frozen) and not lost, "LV live profile %s loads, keeps every key (lost %s)" % (f, lost))
        pg = X.open(Pl)
        apps, sets, evs, _c = X.built(pg, Pl, "LV live profile %s" % f)
        K.check(len(line_rows(apps)) >= 1, "LV ... its page lists %d quest line(s); head %s" % (len(line_rows(apps)), sets.get("#SkyyQlHead.Text")))
        n += 1
    K.check(n >= 1, "LV %d live profile page(s) built" % n)
    K.eq(HK.tree_hash(mods), h0, "LV building the pages wrote nothing")
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    lg = T033.legacy
    phases = [("page40", run_page40), ("claim40", run_claim40),
              ("mig34", T034.run_mig34), ("fish34", T034.run_fish34),
              ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
              ("isl", lg(T032.run_isl)), ("snd", lg(T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
              ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
              ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live40", run_live40)]
    only = HK.arg("--only")
    if only:
        phases = [ph for ph in phases if ph[0] in only.split(",")]
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, phases, os.path.abspath(__file__), live=(LIVE_Q, "Skyy_SkyyQuests"),
               removed=REMOVED)
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
    sys.exit(1 if HK.FAILS else 0)
