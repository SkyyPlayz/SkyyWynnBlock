"""SkyySkills 0.4.47 - harness for the MENU PATTERN sweep S1 (the Skills tab pages on the kit 1.7 hub_page; tools/skills_0_4_47_patch.py).
Build first: python tools/skills_0_4_47_patch.py && python SkyySkills/build_skyyskills_0.4.47.py

    python SkyySkills/test_skyyskills_0.4.47.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.46 -> 0.4.47: HubBar + the kit 1.6 row / 1.7 page members; SkillsPage (subRow, ROW_HS / TOP_HS, build, clicks),
               StatsPage + OverallPage (build, clicks); the version texts; non-class entries: manifest.json only
  PK  0.4.46's executed asset-pack checks, unchanged (test_skyyskills_0.4.46.run_pack)
  PG  PAGES, EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all) with a
      stand-in of SkyyMenu's merged Stats tab. Every page BUILT through the real builders into a real UICommandBuilder - the list, the
      Top 10 view, a skill's Stats page, the Overall page (and the list without SkyyMenu): page rules (check_page, kit paths, every b.set /
      binding names an element) + SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub row, no back button / < Menu, no pager);
      the sub-tab row = [Your Stats] [Skills] [Overall] (+ [Mining] [Top 10]) with the right one selected and bound to the old actions;
      row 2 as built == the kit's hub_big_tabs_preview, the sub row == sub_tabs_preview; the 12 skill rows at 62 / 82 px in the 670 px
      scrolling list; the Top 10 rows grown (Skyy rule 7); HubBar.growSize == SUI.grow_pick for both size lists.
      CLICKS: YOUR STATS (list, Stats, Overall) -> the Stats tab's open Function (openSub); a row's STATS -> the Stats page; the Stats
      page's Overall / Top 10 sub-tabs -> the Overall page / the Top 10 view; the Top 10 view's <Skill> sub-tab -> the Stats page; Skills
      (sub row), the Skills tab (row 2) and the Character hub (row 1) -> the list (in place on /skills); the X closes; without SkyyMenu
      a stray hub:stats = one chat line
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import hub_tab_kit as HT
import skyyui as SUI

_s46 = importlib.util.spec_from_file_location("test_skyyskills_0_4_46", os.path.join(HERE, "test_skyyskills_0.4.46.py"))
T46 = importlib.util.module_from_spec(_s46)
_s46.loader.exec_module(T46)

VERSION = "0.4.47"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.46.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menuS1", "skills", "h")))
ADDED = []
# HubBar: the kit 1.6 row members (row 1, route / goHub, def4 / defTab / pickTab, putIcon) + the kit 1.7 page members (page17, bigRowFill,
# bigTabsFill, subTab, growSize, hasArt) - install_hub_bar(row=True, sub=True, page=True)
HUBM = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES", "+m bigLab", "+m bigRow", "+m bigRowFill", "+m bigTabLab", "+m bigTabsFill", "+m build2",
        "+m buildRow", "+m def4", "+m defOf", "+m defTab", "+m goHub", "+m growSize", "+m hasArt", "+m hubs", "+m iconOf", "+m okIcon",
        "+m okItem", "+m page17", "+m pickTab", "+m putIcon", "+m route", "+m rowLab", "+m rowStyle", "+m rowWidth", "+m subTab",
        "+m tabBStyle", "+m tabLab", "+m titleOf"]
EXPECT = {"HubBar": HUBM,
          "SkillsPage": ["+<clinit>", "+f ROW_HS", "+f TOP_HS", "+m subRow", "~m build", "~m handleDataEvent"],
          "StatsPage": ["~m build", "~m handleDataEvent"], "OverallPage": ["~m build", "~m handleDataEvent"],
          # version texts (each checked by the compare: only the version constant differs)
          "SkillCfg": ["~m load"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "CfgRows": ["~<clinit>", "~m header"],
          "CfgFn": ["~m opExport"], "SkyySkillsPlugin": ["~m setup"]}
SK_ROW_H, SK_ACRO_H, LIST_AVAIL, LIST_H = 62, 82, 642, 670
TOP_AVAIL = 666 - 8


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


def page_rules(K, cmds, evs, what, prefix_ok="Skyy"):
    """the Menu 0.3.35 harness's page rules: check_page, kit paths (the hub tab art allowed), no Top/Bottom/Left/Right alignment, every
    b.set / binding names an element that exists"""
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, prefix_ok)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    for _p, mk in apps:
        if re.search(r"(Vertical|Horizontal)Alignment\s*:\s*(Top|Bottom|Left|Right)\b", mk):
            K.check(False, "%s: a Top/Bottom/Left/Right alignment: %s" % (what, mk[:80]))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    return apps


def run_pages(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong, JImplements, JOverride, JObject
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, Defs, HO, HB, SP = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("SkillsHubOpen"), J("HubBar"), J("SkillsPage")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a6"), "SkillPattern")
    u = P.pr.getUuid()
    N = int(Defs.N)
    dd = [0] * (2 * N)
    for sl in (0, 1, 2, 4):
        dd[sl] = 4000
    Sto.DATA.put(str(u), JArray(JLong)(dd))
    S, Int = JClass("java.lang.String"), JClass("java.lang.Integer")
    K.eq(str(HO.register()), "character:skills", "REG: the Skills tab is put")

    @JImplements("java.util.function.Function")
    class Stub:
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return self.ans
    sopen, hide = Stub(E.TRUE), Stub(E.FALSE)
    merged = JArray(JObject)([S("SkyyMenu"), S("Stats"), Int.valueOf(10), S("stats"), sopen, hide, S("character_stats"), S("skills")])
    E.bridge.put("hub:tab:character:stats", merged)
    fn = HO()
    cls = lambda pg: None if pg is None else str(pg.getClass().getName())[len(PKG):]

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and cls(pg) == "SkillsPage") else None

    def click(p_, word):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % word)
        E.pump(P)
        return E.pg(P)

    def built(pg, what):
        c, e = HT.build(pg, P)
        apps = page_rules(K, c, e, what)
        sets = [(s, unq(d)) for ty, s, t, d in c if ty == "Set"]
        try:
            info = SUI.assert_menu_page(apps, hub="character", what=what, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back button, no pager)" % what)
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        return c, e, sets

    def subrow(c, e, prefix):
        """[(label, selected, action or None)] of the sub-tab row as built"""
        out_ = []
        bind = dict((s, t) for s, t in e)
        for ty, s, t, d in c:
            if s == "#%sSub" % prefix and (t or "").startswith("TextButton"):
                m = re.match(r"TextButton #(\w+) \{.*?Text: \"([^\"]*)\"", t)
                bid = m.group(1)
                act = None
                if "#" + bid in bind:
                    act = next((w for w in re.findall(r"[a-z][a-z0-9:]*", bind["#" + bid]) if w in ACTS), "?")
                out_.append((m.group(2), SUI.theme_button_style("primary", "small", theme="sky") in t, act))
        return out_
    ACTS = ("hub:stats", "hub:skills", "skstatov", "sttop") + tuple("skstat%d" % i for i in range(N))
    PRIM = SUI.theme_button_style("primary", "small", theme="sky")
    g = SUI.grow_row_sizes
    # ================================================================ growSize (Java) == grow_pick (Python), both size lists
    rhs, ths = [int(x) for x in SP.ROW_HS], [int(x) for x in SP.TOP_HS]
    K.eq((rhs, ths), (g(LIST_AVAIL, SK_ROW_H), g(TOP_AVAIL, 55)), "GROW: SkillsPage.ROW_HS / TOP_HS = the kit's grow_row_sizes")
    K.check(all(int(HB.growSize(n, LIST_AVAIL, SP.ROW_HS, 3)) == SUI.grow_pick(n, LIST_AVAIL, rhs) for n in range(0, 16))
            and all(int(HB.growSize(n, TOP_AVAIL, SP.TOP_HS, 3)) == SUI.grow_pick(n, TOP_AVAIL, ths) for n in range(0, 12)),
            "GROW: HubBar.growSize == SUI.grow_pick for 0-15 skill rows / 0-11 Top 10 rows")
    # ================================================================ the list
    pg = open_page()
    K.check(pg is not None, "LIST: /skills opens (SkillsHubOpen)")
    c, e, sets = built(pg, "LIST /skills")
    sr = subrow(c, e, "SkyySkF")
    K.eq(sr, [("Your Stats", False, "hub:stats"), ("Skills", True, "hub:skills"), ("Overall", False, "skstatov")],
         "LIST: the sub-tab row [Your Stats] [Skills] (selected) [Overall] - bound to hub:stats / hub:skills / skstatov")
    subm = [t for ty, s, t, d in c if s == "#SkyySkFSub"]
    K.check(len(subm) == 6 and subm[-1].startswith("Label #SkyySkHint "), "LIST: the hint caption beside the sub-tabs (%s)" % [x[:24] for x in subm])
    want_sub = [SUI.render(mk) for _p, mk in SUI.sub_tabs_preview("SkyySkF", ["Your Stats", "Skills", "Overall"], 1, 150)]
    K.eq(subm[:5], want_sub, "LIST: the sub row as built == the kit's sub_tabs_preview")
    wt = [(str(x[0]), str(x[1])) for x in HB.shown(HB.tabs("character", u), "skills", 10)]
    want2 = [(p_, SUI.render(mk)) for p_, mk in SUI.hub_big_tabs_preview("SkyySkF", "character", wt, "skills", 1552)]
    got2 = [(s.lstrip("#"), t) for ty, s, t, d in c if t is not None and (s or "").startswith("#SkyySkFBigT")]
    K.check(got2 == want2 and [x[0] for x in wt] == ["skills"], "LIST: row 2 as built == the kit's hub_big_tabs_preview (tabs %s - Stats merged)" % wt)
    bind = dict((s, t) for s, t in e)
    K.check("hub:close" in bind.get("#SkyySkFHubClose", "") and "hub:skills" in bind.get("#SkyySkFBigT0", ""), "LIST: the X + row 2's Skills tab bound")
    ls = [t for ty, s, t, d in c if (t or "").startswith("Group #SkyySkList ")]
    K.check(len(ls) == 1 and "TopScrolling" in ls[0] and "Height: %d" % LIST_H in ls[0], "LIST: the scrolling list %d px (%s)" % (LIST_H, ls[0][:90] if ls else None))
    rows = [int(re.search(r"Height: (\d+)", t).group(1)) for ty, s, t, d in c if s == "#SkyySkList" and (t or "").startswith("Group #SkyySkRow")]
    K.check(len(rows) == 12 and sorted(set(rows)) == [SK_ROW_H, SK_ACRO_H] and rows.count(SK_ACRO_H) == 1,
            "LIST: the 12 skill rows keep 62 px (Acrobatics 82) - more than fit, so the list scrolls (%s)" % rows)
    K.check(not [t for ty, s, t, d in c if t and ("SkyySkSubRow" in t or "SkyySkBack" in t or "SkyySkNav" in t)], "LIST: no old sub row / back button / footer")
    K.check(any("skstat0" in t for s, t in e if s.startswith("#SkyySkStat")), "LIST: a row's STATS still bound (skstat<slot>)")
    del sopen.calls[:]
    del hide.calls[:]
    click(pg, "hub:stats")
    K.check(sopen.calls == [str(u)] and not hide.calls, "CLICK list: YOUR STATS -> the Stats tab's open Function (openSub)")
    # ================================================================ a skill's Stats page
    pg = open_page()
    st = click(pg, "skstat0")
    K.eq(cls(st), "StatsPage", "CLICK list: a row's STATS -> the Stats page")
    c, e, sets = built(st, "STATS Mining")
    K.eq(subrow(c, e, "SkyyStF"), [("Your Stats", False, "hub:stats"), ("Skills", False, "hub:skills"), ("Overall", False, "skstatov"),
                                   ("Mining", True, None), ("Top 10", False, "sttop")],
         "STATS: the sub-tab row [Your Stats] [Skills] [Overall] [Mining] (selected, not bound) [Top 10] (sttop)")
    K.check(not [t for ty, s, t, d in c if t and ("SkyyStBack" in t or "SkyyStNav" in t or "#SkyyStTop " in t)], "STATS: no back button, no footer row, no TOP 10 button")
    K.check(any((t or "").startswith("Group #SkyyStHowRow ") for ty, s, t, d in c) and any(s == "#SkyyStTitle.Text" and "Mining" in d for s, d in sets),
            "STATS: the how-to row + the title line (Mining)")
    del sopen.calls[:]
    click(st, "hub:stats")
    K.check(sopen.calls == [str(u)], "CLICK stats: YOUR STATS -> the Stats tab (openSub)")
    st = click(open_page(), "skstat0")
    ov = click(st, "skstatov")
    K.eq(cls(ov), "OverallPage", "CLICK stats: the Overall sub-tab -> the Overall page")
    st = click(open_page(), "skstat0")
    tp = click(st, "sttop")
    K.check(cls(tp) == "SkillsPage" and int(tp.view) == 0, "CLICK stats: the Top 10 sub-tab -> the Top 10 view of Mining")
    st = click(open_page(), "skstat0")
    sk = click(st, "hub:skills")
    K.check(cls(sk) == "SkillsPage" and int(sk.view) == -1, "CLICK stats: Skills (sub row / row 2 hub:skills) -> the list")
    st = click(open_page(), "skstat0")
    sk = click(st, "hub:h:character")
    K.check(cls(sk) == "SkillsPage" and int(sk.view) == -1, "CLICK stats: row 1's Character hub -> the list")
    # ================================================================ the Overall page
    ov = click(open_page(), "skstatov")
    K.eq(cls(ov), "OverallPage", "CLICK list: OVERALL / the Overall sub-tab -> the Overall page")
    c, e, sets = built(ov, "OVERALL")
    K.eq(subrow(c, e, "SkyyOvPage"), [("Your Stats", False, "hub:stats"), ("Skills", False, "hub:skills"), ("Overall", True, None)],
         "OVERALL: the sub-tab row [Your Stats] [Skills] [Overall] (selected, not bound)")
    K.check(not [t for ty, s, t, d in c if t and ("SkyyOvBack" in t or "SkyyOvNav" in t)], "OVERALL: no back button / footer row")
    del sopen.calls[:]
    click(ov, "hub:stats")
    K.check(sopen.calls == [str(u)], "CLICK overall: YOUR STATS -> the Stats tab (openSub)")
    ov = click(open_page(), "skstatov")
    sk = click(ov, "hub:skills")
    K.check(cls(sk) == "SkillsPage" and int(sk.view) == -1, "CLICK overall: Skills -> the list")
    # ================================================================ the Top 10 view
    pg = open_page()
    pg.view = 0
    c, e, sets = built(pg, "TOP 10 Mining")
    K.eq(subrow(c, e, "SkyySkF"), [("Your Stats", False, "hub:stats"), ("Skills", False, "hub:skills"), ("Overall", False, "skstatov"),
                                   ("Mining", False, "skstat0"), ("Top 10", True, None)],
         "TOP 10: the sub-tab row [...] [Mining] (skstat0) [Top 10] (selected, not bound)")
    K.check(any(s == "#SkyySkFTitle.Text" and d == "Character - Top 10 - Mining" for s, d in sets), "TOP 10: the title bar names the view")
    K.check(not [t for ty, s, t, d in c if t and ("SkyySkBack" in t or "SkyySkNav" in t)] and any((t or "").startswith("Label #SkyySkRank ") for ty, s, t, d in c),
            "TOP 10: the rank line, no back button / footer")
    trs = [int(re.search(r"Height: (\d+)", t).group(1)) for ty, s, t, d in c if s == "#SkyySkTop" and re.match(r"Group #SkyySkTopRow\d+ ", t or "")]
    n_ = len(trs)
    K.check(n_ >= 1 and set(trs) == {ths[SUI.grow_pick(n_, TOP_AVAIL, ths)]} and ths[SUI.grow_pick(n_, TOP_AVAIL, ths)] > 55,
            "TOP 10: %d row(s) grown to %s px (Skyy rule 7: a short list fills its room; sizes %s)" % (n_, sorted(set(trs)), ths))
    st = click(pg, "skstat0")
    K.eq(cls(st), "StatsPage", "CLICK top 10: the Mining sub-tab -> the Stats page")
    pg = open_page()
    pg.view = 0
    cur = click(pg, "hub:skills")
    K.check(E.same(cur, pg) and int(pg.view) == -1, "CLICK top 10: Skills -> the list in place")
    pg.view = 0
    cur = click(pg, "hub:h:character")
    K.check(E.same(cur, pg) and int(pg.view) == -1, "CLICK top 10: row 1's Character hub -> the list in place")
    cur = click(open_page(), "hub:close")
    K.check(cls(cur) != "SkillsPage", "CLICK: the X closes the page (%s)" % cls(cur))
    # ================================================================ NONE (SkyyMenu not loaded)
    E.bridge.remove("hub:tab:character:stats")
    pg = open_page()
    c, e, sets = built(pg, "NONE /skills")
    K.eq(subrow(c, e, "SkyySkF"), [("Skills", True, "hub:skills"), ("Overall", False, "skstatov")], "NONE: no Stats tab -> [Skills] [Overall]")
    n0 = len(E.sent(P))
    cur = click(pg, "hub:stats")
    K.check(E.same(cur, pg) and "Your Stats page could not open" in E.strs_of(P, n0), "NONE: a stray hub:stats = one chat line, the page stays")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("pack", T46.run_pack), ("pages", run_pages)], script=__file__)
