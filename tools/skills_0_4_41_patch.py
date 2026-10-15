"""Derive SkyySkills/build_skyyskills_0.4.41.py from the GENERATED SkyySkills 0.4.40 (build_skyyskills_0.4.40.py = the tools/deploy_set.py SET
pin; 0.4.40 came from 0.4.39 by tools/skills_0_4_40_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.40 (nothing else changed); 0.4.40 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_41_patch.py   then   python SkyySkills/build_skyyskills_0.4.41.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.41.py

0.4.41 (2026-10-15) = HUBS H3a, the SkyySkills part (research/Hubs-Spec.md 1.2 / 2 / 7 + the build table row H3a; the kit skyyui 1.5 hub
contract tools/HUBS-CONTRACT.md; SkyyMenu 0.3.28 = H2 is live). Skyy 2026-10-10 (docs/answered/ui.md): "picked ALL: /market hub, /storage
hub, /character hub, Accessory Bag v2, + could we tidy and simplify them any more from here?", "I like 2 the best" + "can we design it all
with the new theme"; 2026-10-15 "And when are we condensing menus together?".
  1. The kit's HubBar class in this jar (SUI.install_hub_bar, the sky tabs). setup() puts the Character hub's Skills tab
     (hub:tab:character:skills = {"SkyySkills", "Skills", 20, "skills", SkillsHubOpen, null} - the SUI.HUB_TABS row: always visible)
     through SkillsHubOpen.register(); shutdown() removes it (SkillsHubOpen.unregister -> HubBar.removeAll: only keys that still hold
     this jar's array).
  2. SkillsHubOpen (java.util.function.Function): apply(UUID) opens /skills for that player on the world thread (a hub click is the
     caller), the /skills command's own open; anything wrong = FALSE (the bar then runs /skills as the player).
  3. /skills and its sub-pages (a skill's Stats page, the Overall page; the Top 10 view is /skills itself) draw in the kit's hub_shell (Sky
     Window: the Character Frame mood, the Header title bar with the crest and the hub title, "< Menu" in the title bar, the close X, the
     shared tab strip filled by HubBar.build; the Skills tab selected on all three):
     - Stats (960 x 848 -> 974 x 914) and Overall (960 x 689 -> 974 x 755): the body is 0.4.40's exactly. Their window titles (the skill
       name / "Overall Level") become the hub title - the body already shows "<Skill> - level n of m" / "Level n of m" in its first line.
     - /skills: 0.4.40's 960 x 973 + the strip + the sky padding would be 1039 high, past 1080p (MAX_PAGE_H 980). It becomes 974 x 980:
       the 12 skill rows sit in a SCROLLING list well (the kit's scroll_list, TopScrolling + the vanilla scrollbar) 749 px high instead
       of the fixed 808 px well (11 rows and most of the 12th show; it scrolls 59 px); each row is 12 px narrower (the 6 px scrollbar + its
       6 px spacing: the row panel 714 / 810, the XP bar 638 / 734). The Overall row, the hint line, the Top 10 view (its fixed list 722
       px, still 10 rows + the rank line) and every text are 0.4.40's; the Top 10 view's title "Top 10 - <Skill>" moves into the hub
       title bar after the hub name ("Character - Top 10 - Mining"; its column heads and rank line stay).
  4. Clicks: handleDataEvent asks HubBar.handle FIRST - the X closes, "< Menu" opens the SkyWynn Menu (/skymenu), the Skills tab = the
     skill list (from the Top 10 view, a Stats page or the Overall page), another tab opens through its open Function or its command, a
     tab that could not open = one chat line (these pages have no status line).
  5. The jar ships the kit's 59 Sky Window files (SUI.kit_texture_files: Common/UI/Custom/SkyyKit/, sha256-pinned, never a ../ path).
  No gameplay change, no saved data, no new command. ROLLBACK to 0.4.40: safe (the tab key is memory only; the old pages come back).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.40.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.41.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.4.40"' in s and s.startswith('"""SkyySkills 0.4.40 - build script') and "HubBar" not in s, "not the generated 0.4.40 script"
REG0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.41 (2026-10-15)"):].rstrip() + "\n"
FAIL_CHAT = "[Skills] That tab could not open right now - try again."

# ================================================================================================ docstring + version
rep('''"""SkyySkills 0.4.40 - build script (derived from the generated 0.4.39 by tools/skills_0_4_40_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.41 - build script (derived from the generated 0.4.40 by tools/skills_0_4_41_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.40 was derived from the generated 0.4.39 by tools/skills_0_4_40_patch.py;
''')
rep('VERSION = "0.4.40"', 'VERSION = "0.4.41"')

# ================================================================================================ the kit's HubBar + SkillsHubOpen classes
rep('''pcfg = pool.makeClass(PKG + ".PerkCfg")
scls = pool.makeClass(PKG + ".SkillClass")
''', '''pcfg = pool.makeClass(PKG + ".PerkCfg")
scls = pool.makeClass(PKG + ".SkillClass")
# 0.4.41 HUBS H3a: the kit's HubBar (kit skyyui 1.5, the sky tabs) in OUR package (cross-jar classes are not allowed: every hub mod has its
# own copy of the same code) + SkillsHubOpen (the Skills tab's open Function; its methods after SkillsCmd). The tab = the SUI.HUB_TABS row
# owned by SkyySkills (tab id, order, label, command)
assert SUI.KIT_VERSION == "1.5" and SUI.HUB_THEME == "sky", "0.4.41: kit skyyui 1.5, hub pages in the sky theme"
HUB_ROW = [r for r in SUI.HUB_TABS if r[3] == "SkyySkills"]
assert [(r[0], r[1], r[2], r[4], r[5]) for r in HUB_ROW] == [("character", "skills", 20, "Skills", "skills")], "0.4.41: the contract's Skills tab"
HUB, HUB_TAB, HUB_ORDER, _HUB_MOD, HUB_LABEL, HUB_CMD = HUB_ROW[0]
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod)
hopen = pool.makeClass(PKG + ".SkillsHubOpen")
''')

# ================================================================================================ sizes: the list scrolls in the hub window
rep('''SK_LIST_IN = SK_IN_W - 2 * SUI.WELL_LIST_PAD                           # 918: a row inside a list well
''', '''SK_LIST_IN = SK_IN_W - 2 * SUI.WELL_LIST_PAD - (SUI.SCROLL_SIZE + SUI.SCROLL_SPACING)   # 906: a row inside the SCROLLING list well
#   (0.4.41 hubs: the 6 px scrollbar + its 6 px spacing come off every row; 0.4.40's fixed well: 918)
''')
rep('''SK_TOP_SPEC = SUI.column_spec([("Rank", 100), ("Player", 444), ("Level", 150), ("XP", 200)], avail=SK_LIST_IN, pad_left=12)''',
    '''SK_TOP_SPEC = SUI.column_spec([("Rank", 100), ("Player", 444), ("Level", 150), ("XP", 200)], avail=SK_IN_W - 2 * SUI.WELL_LIST_PAD, pad_left=12)   # 0.4.41: the Top 10 well stays fixed (918)''')
rep('''assert SK_TEXT_W == {True: 658, False: 754}, SK_TEXT_W
assert SK_TOP_LIST_H >= SUI.list_well_h(10, SK_TOP_ROW_H), "the Top 10 well holds its 10 rows"
''', '''assert SK_TEXT_W == {True: 646, False: 742}, SK_TEXT_W      # 0.4.41: 12 px narrower (the scrolling list; 0.4.40: 658 / 754)
assert SK_TOP_LIST_H >= SUI.list_well_h(10, SK_TOP_ROW_H), "the Top 10 well holds its 10 rows"
# 0.4.41 HUBS: the three pages in the Character hub window (the sky padding 24 + the 52 px tab strip). Stats and Overall keep their bodies;
# /skills is capped at MAX_PAGE_H (0.4.40's 973 + 66 = 1039 > 1080p): the skill list scrolls the 59 px, the Top 10 well gives them up
HUB_PAD = SUI.THEME_PAD[SUI.HUB_THEME]
SK_HUB_W = SK_W + 2 * (HUB_PAD - SUI.CONTENT_PAD)                                       # 974
SK_HUB_H = SUI.MAX_PAGE_H                                                                # 980
SK_HUB_BODY = SK_HUB_H - SUI.TITLE_H - 2 * HUB_PAD - SUI.HUB_BAR_H                       # 842 (0.4.40: SK_BODY_H 901)
SK_HUB_LIST_H = SK_HUB_BODY - (SK_OV_H + SK_OV_M) - (SK_HINT_M + SK_HINT_H)               # 749 (0.4.40: the fixed SK_LIST_H 808)
SK_TOP_LIST_H = SK_HUB_BODY - SK_TOP_HEAD_H - (SK_RANK_M + SK_RANK_H) - SK_FOOT_H          # 722 (0.4.40: 781)
STATS_HUB_W, STATS_HUB_H = SK_HUB_W, STATS_H + SUI.HUB_BAR_H + 2 * (HUB_PAD - SUI.CONTENT_PAD)   # 974 x 914
OV_HUB_W, OV_HUB_H = SK_HUB_W, OV_H + SUI.HUB_BAR_H + 2 * (HUB_PAD - SUI.CONTENT_PAD)            # 974 x 755
assert (SK_HUB_W, SK_HUB_BODY, SK_HUB_LIST_H, SK_TOP_LIST_H, STATS_HUB_H, OV_HUB_H) == (974, 842, 749, 722, 914, 755), "0.4.41 hub sizes"
assert SK_H + SUI.HUB_BAR_H + 2 * (HUB_PAD - SUI.CONTENT_PAD) > SUI.MAX_PAGE_H, "0.4.41: /skills would not fit 1080p without the scroll"
assert SK_HUB_LIST_H >= 2 * SUI.WELL_LIST_PAD + SK_ACRO_H + 10 * (SK_ROW_H + SUI.ROW_GAP), "0.4.41: at least 11 skill rows show at once"
assert SK_TOP_LIST_H >= SUI.list_well_h(10, SK_TOP_ROW_H), "0.4.41: the Top 10 well still holds its 10 rows"
for _hw, _hh in ((SK_HUB_W, SK_HUB_H), (STATS_HUB_W, STATS_HUB_H), (OV_HUB_W, OV_HUB_H)):
    assert SUI.assert_hub_page(_hw, _hh - SUI.HUB_BAR_H, old_title_h=0, hub=HUB, pad=HUB_PAD) == (_hw, _hh)
assert SUI.assert_hub_fits(HUB, SK_IN_W) >= 110, "0.4.41: the 8 Character tabs fit the 926 px strip"
''')
rep('''    return SUI.page_shell("SkyySkF", SK_W, SK_H, title, kind="plain", body_id="SkyySkills")''',
    '''    return SUI.hub_shell("SkyySkF", SK_HUB_W, SK_HUB_H, HUB, body_id="SkyySkills")   # 0.4.41: the Character hub shell (title = the hub)''')
rep('''    ap.add(body, SUI.list_well("SkyySkList", w=SK_IN_W, h=SK_LIST_H))''',
    '''    ap.add(body, SUI.scroll_list("SkyySkList", w=SK_IN_W, h=SK_HUB_LIST_H, well=True))   # 0.4.41: scrolls (0.4.40: the fixed 808 px well)''')
rep('''    return SUI.page_shell("SkyyStF", STATS_W, STATS_H, name, kind="plain", body_id="SkyySkStats")''',
    '''    return SUI.hub_shell("SkyyStF", STATS_HUB_W, STATS_HUB_H, HUB, body_id="SkyySkStats")   # 0.4.41: the Character hub shell (the name is in the body's first line)''')
rep('''    return SUI.page_shell("SkyyOvF", OV_W, OV_H, "Overall Level", kind="plain", root_id="SkyyOvPage", bar_id="SkyyOvHead",
                          title_id="SkyyOvHeadTxt", body_id="SkyyOvBody")''',
    '''    return SUI.hub_shell("SkyyOvPage", OV_HUB_W, OV_HUB_H, HUB, body_id="SkyyOvBody")   # 0.4.41: the Character hub shell (root #SkyyOvPage kept)''')
# every state's body: the strip (52) is its first child now, the content below it fills the room under the strip as before
rep('''    left = SUI.fit([SUI.used_height(whole, body)], inner_h, body)''',
    '''    left = SUI.fit([SUI.used_height(whole, body)], inner_h + SUI.HUB_BAR_H, body)   # 0.4.41: + the hub tab strip (inner_h = the room under it)''')
rep('''print("skills pages: /skills %d x %d, Stats %d x %d, Overall %d x %d on %s - %d sample states checked (check_page, assert_proven, heights)"
      % (SK_W, SK_H, STATS_W, STATS_H, OV_W, OV_H, KIT_ID, len(_sk_checked)))''',
    '''print("skills pages (Character hub shell): /skills %d x %d (the list scrolls), Stats %d x %d, Overall %d x %d on %s - %d sample states checked (check_page, assert_proven, heights)"
      % (SK_HUB_W, SK_HUB_H, STATS_HUB_W, STATS_HUB_H, OV_HUB_W, OV_HUB_H, KIT_ID, len(_sk_checked)))''')

# ================================================================================================ the shells' checks + the HubBar.build lines
rep('''SK_SH = sk_shell()
SK_SHELL_JAVA = _sk_shell_java(SK_SH, "SkyySk", "  ")
''', '''SK_SH = sk_shell()
SK_SHELL_JAVA = _sk_shell_java(SK_SH, "SkyySk", "  ")


def _sk_hub(sh, idp):
    """0.4.41: a Skills tab page's hub shell: the Sky Window parts, the bar with every contract tab of the hub (H3 complete) and with Menu's
    Stats + ours only (valid markup, ours selected, every label fits) -> the HubBar.build line for its build()"""
    assert (sh.inner_w, sh.tabs_w, sh.parts) == (SK_IN_W, SK_IN_W, SUI.HUB_PART_MENU | SUI.HUB_PART_CLOSE)
    els = SUI.check_sky_paths(sh.appends)
    assert {"Header", "HeaderOrnament", SUI.HUB_FRAME[HUB], "Close", "Tertiary"} <= set(els), "0.4.41: the Sky Window shell: %s" % els
    for rows in (SUI.hub_tabs(HUB), [r for r in SUI.hub_tabs(HUB) if r[2] in ("SkyyMenu", "SkyySkills")]):
        bar = SUI.hub_bar_preview(sh.prefix, [(t, l, o) for t, o, _m, l, _c in rows], HUB_TAB, sh.tabs_w)
        SUI.check_page(SUI.Appends(list(sh.appends) + list(bar)), idp)
        SUI.check_sky_paths(bar)
        btn = [mk for _p, mk in bar if mk.startswith("TextButton")]
        assert len(btn) == len(rows) and sum(1 for mk in btn if "Tab_Selected" in mk) == 1, sh.prefix
        assert ('Text: "%s"' % HUB_LABEL) in [mk for mk in btn if "Tab_Selected" in mk][0], sh.prefix
        for r in rows:
            assert SUI.text_width(r[3], 12, bold=True) <= SUI.hub_tab_width(sh.tabs_w, len(rows)) - 2 * SUI.HUB_TAB_PAD, "0.4.41: tab %s fits" % r[3]
    return "  " + SUI.java_hub_build(sh, HUB_TAB, cls=PKG + ".HubBar", uuid="u")


SK_HUB_JAVA = _sk_hub(SK_SH, "SkyySk")
assert SK_HUB_JAVA == '  com.skyy.skills.HubBar.build(b, ev, "SkyySkF", "character", "skills", 926, u, 3);', SK_HUB_JAVA
''')
rep('''ST_SH = st_shell(SUI.J("name", "Mining"))
ST_SHELL_JAVA = _sk_shell_java(ST_SH, "SkyyS", "  ")
''', '''ST_SH = st_shell(SUI.J("name", "Mining"))
ST_SHELL_JAVA = _sk_shell_java(ST_SH, "SkyyS", "  ")
ST_HUB_JAVA = _sk_hub(ST_SH, "SkyyS")      # 0.4.41
''')
rep('''OV_SH = ov_shell()
OV_SHELL_JAVA = _sk_shell_java(OV_SH, "SkyyOv", "  ")
''', '''OV_SH = ov_shell()
OV_SHELL_JAVA = _sk_shell_java(OV_SH, "SkyyOv", "  ")
OV_HUB_JAVA = _sk_hub(OV_SH, "SkyyOv")     # 0.4.41
''')
rep('''  // 0.4.7: the plain vanilla window (title SKILLS / TOP 10 - <SKILL>), body = 0.4.6's root #SkyySkills - kit markup
{SK_SHELL_JAVA}
''', '''  // 0.4.7: the plain vanilla window (title SKILLS / TOP 10 - <SKILL>), body = 0.4.6's root #SkyySkills - kit markup
  // 0.4.41: the Character hub shell + its tab strip (HubBar.build: the visible Character tabs, Skills selected)
{SK_SHELL_JAVA}
{SK_HUB_JAVA}
''')
rep('''{ST_SHELL_JAVA}
{ST_TOP_JAVA}
''', '''{ST_SHELL_JAVA}
{ST_HUB_JAVA}
{ST_TOP_JAVA}
''')
rep('''{OV_SHELL_JAVA}
{OV_TOP_JAVA}
''', '''{OV_SHELL_JAVA}
{OV_HUB_JAVA}
{OV_TOP_JAVA}
''')
# the Top 10 view: its old window title "Top 10 - <Skill>" goes into the hub title bar after the hub name (the view does not name the skill
# anywhere else; the title label is the shell's #SkyySkFTitle - a b.set on a Label's Text, the proven way)
rep('''  int s = this.view;
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);''', '''  int s = this.view;
  b.set("#SkyySkFTitle.Text", "Character - Top 10 - " + {PKG}.SkillDefs.LABELS[s]);   // 0.4.41: the view's title (was the window title)
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);''')
for _a, _b in (("for _piece in (SK_SHELL_JAVA, SK_OVERVIEW_JAVA,", "for _piece in (SK_SHELL_JAVA, SK_HUB_JAVA, SK_OVERVIEW_JAVA,"),
               ("for _piece in (ST_SHELL_JAVA, ST_TOP_JAVA,", "for _piece in (ST_SHELL_JAVA, ST_HUB_JAVA, ST_TOP_JAVA,"),
               ("for _piece in (OV_SHELL_JAVA, OV_TOP_JAVA,", "for _piece in (OV_SHELL_JAVA, OV_HUB_JAVA, OV_TOP_JAVA,")):
    rep(_a, _b)

# ================================================================================================ the clicks: the hub bar first (3 pages)
_HUB_HANDLE = '''    String hr = {PKG}.HubBar.handle(this.playerRef, data, "character", "skills");   // 0.4.41 hubs: the bar first (null = not a hub click)
    if (hr != null) {{
      if (hr.equals("close")) {{ close(); return; }}
      if (hr.equals("self")) {{ %s }}
      else if (!hr.equals("bridge") && !hr.equals("command") && !hr.equals("back")) this.playerRef.sendMessage({MSG}.raw("%s"));
      return;
    }}
'''
_TO_LIST = '''{PLA} ph = ({PLA}) st.getComponent(ref, {PLA}.getComponentType()); if (ph != null) ph.getPageManager().openCustomPage(ref, st, new {PKG}.SkillsPage(this.playerRef)); return;'''
rep('''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("stback\\\\"") >= 0) {{''', '''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
''' + _HUB_HANDLE % (_TO_LIST, FAIL_CHAT) + '''    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("stback\\\\"") >= 0) {{''')
rep('''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    if (data.indexOf("ovback\\\\"") >= 0) {{''', '''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
''' + _HUB_HANDLE % (_TO_LIST, FAIL_CHAT) + '''    if (data.indexOf("ovback\\\\"") >= 0) {{''')
rep('''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    if (data.indexOf("skstatov\\\\"") >= 0) {{''', '''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
''' + _HUB_HANDLE % ("this.view = -1; rebuild(); return;", FAIL_CHAT) + '''    if (data.indexOf("skstatov\\\\"") >= 0) {{''')

# ================================================================================================ SkillsHubOpen (after SkillsCmd)
rep('''    {PKG}.SkillCfg.warn("/skills failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not open the page: " + {PKG}.SkillStore.levelsString(pr.getUuid())));
  }}
}}""", cmd))
''', '''    {PKG}.SkillCfg.warn("/skills failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not open the page: " + {PKG}.SkillStore.levelsString(pr.getUuid())));
  }}
}}""", cmd))
# ---- 0.4.41 SkillsHubOpen: the Skills tab's open Function (HUBS-CONTRACT 1): apply(UUID) on the player's world thread (a hub click is the
# caller) opens /skills (the command's own open); anything wrong = FALSE -> the bar runs /skills as the player. register() / unregister():
# setup() puts the tab (always visible; /skills is the fallback) -> "character:skills" or "off"; shutdown() takes it off again.
_HO_TOK = {"@PKG@": PKG, "@PR@": PR, "@REF@": REF, "@ST@": ST, "@PLA@": PLA, "@UNI@": UNI}


def _ho(src):
    for _k, _v in _HO_TOK.items():
        src = src.replace(_k, _v)
    assert "@" not in src, src
    return src


hopen.addInterface(pool.get("java.util.function.Function"))
hopen.addField(CtField.make("public static volatile long OPENED = 0L;", hopen))
hopen.addConstructor(CtNewConstructor.make("public SkillsHubOpen() { super(); }", hopen))
hopen.addMethod(CtNewMethod.make(_ho("""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    if (st == null) return Boolean.FALSE;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return Boolean.FALSE;
    p.getPageManager().openCustomPage(r, st, new @PKG@.SkillsPage(pr));
    OPENED = OPENED + 1L;
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("the Skills hub tab could not open: " + t);
    return Boolean.FALSE;
  }
}"""), hopen))
hopen.addMethod(CtNewMethod.make(_ho("""
public static String register() {
  try {
    if (@PKG@.HubBar.put("%s", "%s", "SkyySkills", "%s", %d, "%s", new @PKG@.SkillsHubOpen(), null) != null) return "%s:%s";
  } catch (Throwable t) { @PKG@.SkillCfg.warn("the Skills hub tab could not be registered: " + t); }
  return "off";
}""" % (HUB, HUB_TAB, HUB_LABEL, HUB_ORDER, HUB_CMD, HUB, HUB_TAB)), hopen))
hopen.addMethod(CtNewMethod.make(_ho("""
public static int unregister() {
  try { return @PKG@.HubBar.removeAll(); } catch (Throwable t) { return 0; }
}"""), hopen))
''')

# ================================================================================================ setup / shutdown / write / jar
rep('''  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SkillTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
''', '''  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SkillTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  String hubTab = {PKG}.SkillsHubOpen.register();     // 0.4.41 hubs: the Character hub's Skills tab
''')
rep('''(fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)));''',
    '''(fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)) + "; hub tab " + hubTab);''')
rep('''  try {{ {PKG}.MoveSync.releaseFall({PKG}.Acro.MOD); }} catch (Throwable t) {{ }}
  super.shutdown();''', '''  try {{ {PKG}.MoveSync.releaseFall({PKG}.Acro.MOD); }} catch (Throwable t) {{ }}
  {PKG}.SkillsHubOpen.unregister();     // 0.4.41: the Skills tab off the bridge (only while it still holds ours; never throws)
  super.shutdown();''')
rep('''          rbcm, snd39, rbs39):   # 0.4.39: + SkSnd, RbStat;''', '''          rbcm, snd39, rbs39,
          hubb, hopen):   # 0.4.41: + HubBar, SkillsHubOpen; 0.4.39: + SkSnd, RbStat;''')
rep('''B.assemble(jar, m, OUT, ASSET_FILES)''', '''# 0.4.41: the Sky Window kit art - all 59 files, byte-identical in every hub jar (sha256-pinned by the kit; HUBS-CONTRACT 2.7), under
# Common/UI/Custom/SkyyKit/ only (a texture outside Common/UI/Custom disconnects the client - probe k1b, 2026-10-15)
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p for p in _kit), "0.4.41: the kit art"
assert not set(_kit) & set(ASSET_FILES), "0.4.41: a kit file clashes with a file of this jar"
B.assemble(jar, m, OUT, dict(ASSET_FILES, **_kit))
assert SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", "Frame_Character", "Tertiary")) == 59, "0.4.41: the jar's kit art"''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
_i = s.index
assert _i("hubb = SUI.install_hub_bar(") < _i("SK_SH = sk_shell()") < _i("hopen.addInterface(") < _i("{PKG}.SkillsHubOpen.register();")
assert s.count("{PKG}.HubBar.handle(") == 3 and s.count("@PKG@.HubBar.put(") == 1 and s.count("@PKG@.HubBar.removeAll()") == 1
assert s.count("{PKG}.SkillsHubOpen.register()") == 1 and s.count("{PKG}.SkillsHubOpen.unregister()") == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.4.40 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.4.40 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
