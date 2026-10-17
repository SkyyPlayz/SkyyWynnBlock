"""Derive SkyySacks/build_skyysacks_0.8.15.py from the SET pin 0.8.14 (the GENERATED build_skyysacks_0.8.14.py; edit THIS file, then
regenerate: python tools/sacks_0_8_15_patch.py; never re-run sacks_0_8_14_patch.py on top of it). The chain: ... -> sacks_0_8_14_patch.py ->
0.8.14 (generated, the SET pin) -> this patch -> 0.8.15. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.8.14 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_15_patch.py   then   python SkyySacks/build_skyysacks_0.8.15.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.15.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.15 = MENU PATTERN sweep S2 (research/Menu-Pattern.md 3 + rules 7-8; kit skyyui 1.7 hub_page; tools/HUBS-CONTRACT.md 'Kit 1.7'). Skyy's words
(docs/answered/ui.md 2026-10-16): "Double check every menu and make sure it's fully and completely built out / designed properly in the cohesive
menu system we made. I never want to have to use a back button. The menus at the top should always be there for easy navigation." + "keep this
top bar at this size consistent at the top across every menu." + "i dont mind scrolling, but if there are only a few items try to scale them to
all fit." + popups: every hub page 1600 x 980, row 2 big like Teleport.
  1. THE VOID = Storage > Pocket on the 1600 x 980 kit page (was a 1300 x 690 'SkyyVoid' window with no hub rows, opened over the vanilla
     inventory): row 1 (Home + the 7 hubs) and row 2 (the Storage tabs, Pocket selected) always on top (HubBar.page17), the X closes. The six
     bag categories stay the left column (an in-page selection: each shows its level, space bar and rarity colour - no sub-tab row needed); the
     middle grid is ONE scroll list of 12 columns (was 9 x 4 cells with Prev / Next pages) - every kind of item, empty cells fill the rows that
     show; a count line under it. Deposit all / Craft (top row), Withdraw / Deposit / Pick up all / Deposit <category>, the amount box, the
     Upgrade box (Upgrade -> Pay / Cancel in place) and the stack refill row are unchanged (same events; a cell click 'cell:<n>' now names its
     place in the whole list). SkyySacks now puts its own contract tab hub:tab:storage:pocket ("Pocket", order 10, /sacks, icon
     storage_pocket, VoidHubOpen) so row 2 opens the page directly (SkyyMenu's stand-in steps aside: the owner's tab wins).
     FOR THE PLAYER: /sacks (/pd /bags /pocket) no longer shows the vanilla inventory panel under the Void (the 1600 x 980 page fills the
     screen; HANDOFF 2: no UI on the vanilla inventory screen). Nothing used it: the 9-slot window was an EMPTY container no code read - every
     deposit / withdraw path is a page button (Deposit all, Deposit <category>, Deposit + amount, Withdraw + amount, Pick up all), and the
     side panel shows "on you N" for the picked item. The auto-pickup sweep, the Pocket craft window and bench crafting are untouched.
  2. /craft (Crafting hub, tab recipes "Crafting") on the 1600 x 980 kit page (was 1200 x 960 with the small kit 1.6 row): rows 1 + 2 on top;
     the crafter's category tabs (Crafting / Gear / Farming / Campfire / Furnace / Tannery / Collections) = the page's ONE sub-tab row (kit
     HubBar.subTab, 150 px small buttons, the open one Primary); the old back-to-the-Void button is gone (row 1 Storage leads there); the
     result line + Craftable only + Refresh = the kit footer (48 px buttons). The recipe rows use the wider page (the name column +400 px).
     ADD FUEL (Furnace tab): no pages and no back / cancel buttons any more - ONE in-page view: the picked fuel's amount box + Load on top,
     the fuel list below as a scroll list (few fuels = bigger rows, Skyy rule 7); Pick on another row switches, Add fuel (shown selected while
     open) or the Furnace sub-tab closes it. Same events (pfpick / pfload / paddf); Load is the view's one Primary.
  3. Rule 7 (short lists fill the space) through the SHARED rule: CraftPage.rowSize = HubBar.growSize(n, list, ROWHS, 6) (= skyyui.grow_pick);
     the row heights stay 0.8.14's tuned 92 / 128 / 168 (drawRow's fonts and icons are tuned per size; each is within skyyui.grow_row_sizes'
     caps for the smallest list, asserted); the ADD FUEL rows grow 48 / 69 / 96 (grow_row_sizes). The Void grid keeps its 74 px slots (an
     item grid - Menu-Pattern 3.3 item_grid 74 px slots).
  4. The small Pocket craft window on the vanilla inventory side stays a window (Menu-Pattern 1.2) - unchanged.
Content, coin and item logic unchanged; no command / saved-data / setting change; the only new bridge entry is the contract tab of item 1.
ROLLBACK to 0.8.14: safe (the old pages come back; SkyyMenu's stand-in Pocket tab returns when our tab is gone).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)
import skyyui as SUI

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.14.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.15.py"))
assert P.has('VERSION = "0.8.14"\n') and P.has('CSH = SUI.hub_shell("SkyyCraft"') and not P.has("SUI.hub_page("), "not the live generated SkyySacks 0.8.14"
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.HUB_PAGE_IW == 1552, "kit skyyui 1.7 (hub_page)"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.15 = MENU PATTERN sweep S2"):].rstrip() + "\n"


def between(a, b, inclusive_b=False):
    """the unique text from anchor a up to (not including) the first b after it"""
    assert P.s.count(a) == 1, "anchor count %d: %s" % (P.s.count(a), a[:120])
    i = P.s.index(a)
    j = P.s.index(b, i)
    return P.s[i:j + (len(b) if inclusive_b else 0)]


# ================================================================================================ header, version
P.rep('''ROLLBACK to 0.8.13: safe (the C1 Enchanted stacks already in the Void stay stored and listed by id; 0.8.13 just stops taking new ones).
"""
''', '''ROLLBACK to 0.8.13: safe (the C1 Enchanted stacks already in the Void stay stored and listed by id; 0.8.13 just stops taking new ones).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.14"\n', 'VERSION = "0.8.15"\n')

# ================================================================================================ 1. THE VOID on the kit 1.7 hub page
P.rep('''VP_W, VP_H = 1300, 690                         # the 0.7.11 footprint height (the player inventory window shows with it)
VSH = SUI.page_shell("SkyyV", VP_W, VP_H, title="SkyyVoid", root_id="SkyySacks", body_id="SkyySBody", bar_id="SkyyVBar", title_id="SkyyVTitle")
VIN_W, VIN_H = VSH.inner_w, VSH.inner_h
V_TAB_W, V_MID_W, V_SIDE_W, V_GAP = 220, 682, 340, 12
V_TOP_H, V_MAIN_H, V_INFO_H, V_UP_H = 34, 478, 26, 226
''', '''# 0.8.15 (kit 1.7, research/Menu-Pattern.md 3): Storage > Pocket = the 1600 x 980 hub page - row 1 + row 2 (HubBar.page17), the X; the old
# body id SkyySBody is the content group (every old appendInline keeps working). Content 1552 x 774 (no sub-tab row, no footer).
assert ("storage", "pocket", 10, "SkyySacks", "Pocket", "sacks") in SUI.HUB_TABS
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)   # kit 1.7 (moved up: the Void page uses it)
VSH = SUI.hub_page("SkyyVH", "storage", body_id="SkyyVHB", content_id="SkyySBody")
V_HUB17 = SUI.java_hub_page(VSH, "pocket", cls="@PKG@.HubBar", uuid="u")
VIN_W, VIN_H = VSH.inner_w, VSH.inner_h
assert (VIN_W, VIN_H) == (1552, 774), (VIN_W, VIN_H)
V_TAB_W, V_MID_W, V_SIDE_W, V_GAP = 220, 968, 340, 12
V_TOP_H, V_INFO_H, V_UP_H = 34, 26, 226
V_MAIN_H = VIN_H - V_TOP_H - V_INFO_H - RF_ROW_H - RF_HELP_H
# the middle grid: ONE scroll list (no pages) of V_COLS columns of 74 px cells (78 px rows); empty cells fill the rows that show
V_COLS, V_ROW_H, V_COUNT_H, V_MAXCELLS = 12, 78, 26, 600
V_HEAD_H = 22 + 8 + 4 + 22 + 8 + 4 + 22
V_GRID_H = V_MAIN_H - V_HEAD_H - V_COUNT_H
V_GRID_ROWS = (V_GRID_H - 8) // V_ROW_H
''')
P.rep('''assert 9 * 74 + 8 * 2 == V_MID_W
''', '''assert V_COLS * 74 + (V_COLS - 1) * 2 + 8 + 12 <= V_MID_W, "the grid + the well padding + the scrollbar"
''')
P.rep('''assert 22 + 8 + 4 + 22 + 8 + 4 + 22 + 4 * 78 + 36 <= V_MAIN_H, "middle column"
''', '''assert V_HEAD_H + V_GRID_H + V_COUNT_H <= V_MAIN_H and V_GRID_ROWS >= 4, "middle column (at least the old 4 rows show)"
''')
P.rep('''    "pager": SUI.group("SkyyVPager", "Left", h=36, pad={"top": 4}),
    "prev": SUI.choose("pageNo > 0", SUI.button("SkyyVPrev", "< Prev", "secondary", "small", w=120),
                       SUI.button("SkyyVPrev", "< Prev", "secondary", "small", w=120, disabled=True)),
    "pagel": SUI.label("SkyyVPage", "", "caption", w=V_MID_W - 240, h=32, align="Center"),
    "next": SUI.choose("pageNo < pages - 1", SUI.button("SkyyVNext", "Next >", "secondary", "small", w=120),
                       SUI.button("SkyyVNext", "Next >", "secondary", "small", w=120, disabled=True)),
''', '''    # 0.8.15: the grid scrolls (kit scroll_list on the list well) - no pages; the count line under it
    "grid": SUI.scroll_list("SkyyVGrid", h=V_GRID_H, well=True),
    "count": SUI.label("SkyyVCount", "", "caption", w=V_MID_W, h=V_COUNT_H, align="Center"),
''')
P.rep('''SUI.assert_proven(_vflat + [m for _p, m in VSH.appends], what="SkyyVoid page")
''', '''SUI.assert_proven(_vflat + [m for _p, m in VSH.appends], what="SkyyVoid page")
# 0.8.15: the shell + rows 1 + 2 as one page (kit 1.7 checks; the harness runs assert_menu_page on the REAL built page)
_vpv = SUI.hub_page_preview(VSH, my_tab="pocket")
_vpv.check("Skyy")
SUI.assert_proven(_vpv, what="SkyyVoid hub page")
SUI.check_sky_paths(_vpv, tab_icons=True)
SUI.assert_menu_page(_vpv, VSH)
''')
P.rep('''    src = src.replace("@SHELL@", VSH.java("b")).replace("@TABW@", str(V_TAB_W)).replace("@MIDW@", str(V_MID_W))
''', '''    src = src.replace("@SHELL@", VSH.java("b") + "\\n  " + V_HUB17).replace("@TABW@", str(V_TAB_W)).replace("@MIDW@", str(V_MID_W))
    src = src.replace("@COLS@", str(V_COLS)).replace("@GRIDROWS@", str(V_GRID_ROWS)).replace("@MAXCELLS@", str(V_MAXCELLS))   # 0.8.15
''')
P.rep(r'''  int pages = (entries.size() + 35) / 36;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  this.cells = new String[36];
  String sel = this.sel;
  for (int r = 0; r < 4; r++) {
    b.appendInline("#SkyyVMid", @@row@@);
    for (int c = 0; c < 9; c++) {
      int idx = r * 9 + c;
      int at = this.pageNo * 36 + idx;
      if (at < entries.size()) {
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(at);
        String cid = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = cid;
        b.appendInline("#SkyyVRow" + r, @@cell@@);
        b.set("#SkyyVCell" + idx + "Qty.Text", shortNum(cnt));
        ev.addEventBinding(@BT@.Activating, "#SkyyVCell" + idx, amtEvt("cell:" + idx));
      } else {
        b.appendInline("#SkyyVRow" + r, @@cellempty@@);
      }
      if (c < 8) b.appendInline("#SkyyVRow" + r, @@cellgap@@);
    }
  }
  b.appendInline("#SkyyVMid", @@pager@@);
  b.appendInline("#SkyyVPager", @@prev@@);
  b.appendInline("#SkyyVPager", @@pagel@@);
  b.set("#SkyyVPage.Text", "Page " + (this.pageNo + 1) + " / " + pages + " - " + entries.size() + (entries.size() == 1 ? " kind of item" : " kinds of items"));
  b.appendInline("#SkyyVPager", @@next@@);
  if (this.pageNo > 0) ev.addEventBinding(@BT@.Activating, "#SkyyVPrev", amtEvt("pg:prev"));
  if (this.pageNo < pages - 1) ev.addEventBinding(@BT@.Activating, "#SkyyVNext", amtEvt("pg:next"));
''', r'''  // 0.8.15 (kit 1.7, Skyy "scroll lists instead of pages"): ONE scrolling grid of @COLS@ columns - every kind (up to @MAXCELLS@), no pages;
  // empty cells fill the rows that show (as the old 4 x 9 grid did). A cell's event names its place in the whole list (cell:<n>).
  int shownN = entries.size() < @MAXCELLS@ ? entries.size() : @MAXCELLS@;
  this.cells = new String[shownN];
  String sel = this.sel;
  b.appendInline("#SkyyVMid", @@grid@@);
  int rowsN = (shownN + @COLS@ - 1) / @COLS@;
  if (rowsN < @GRIDROWS@) rowsN = @GRIDROWS@;
  for (int r = 0; r < rowsN; r++) {
    b.appendInline("#SkyyVGrid", @@row@@);
    for (int c = 0; c < @COLS@; c++) {
      int idx = r * @COLS@ + c;
      if (idx < shownN) {
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
        String cid = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = cid;
        b.appendInline("#SkyyVRow" + r, @@cell@@);
        b.set("#SkyyVCell" + idx + "Qty.Text", shortNum(cnt));
        ev.addEventBinding(@BT@.Activating, "#SkyyVCell" + idx, amtEvt("cell:" + idx));
      } else {
        b.appendInline("#SkyyVRow" + r, @@cellempty@@);
      }
      if (c < @COLS@ - 1) b.appendInline("#SkyyVRow" + r, @@cellgap@@);
    }
  }
  b.appendInline("#SkyyVMid", @@count@@);
  b.set("#SkyyVCount.Text", entries.size() + (entries.size() == 1 ? " kind of item" : " kinds of items") + (shownN < entries.size() ? (" - the first " + shownN + " show") : ""));
''')
# the hub rows' clicks first (row 1 'hub:h:<id>', row 2 'hub:<tab>', the X 'hub:close'); a click that left this page on screen gets a no-op update
P.rep(r"""page.addMethod(CtNewMethod.make(jt(r'''
public void onEvent(@REF@ ref, @ST@ st, @PLA@ player0, String data) {
  try {
    if (data == null) return;
""", r"""# 0.8.15 (kit 1.7): a hub click that left this page open on screen is answered with a no-op update (the client's "Loading..." ends)
page.addMethod(CtNewMethod.make(jt(r'''
public void hubAck(@REF@ ref, @ST@ st) {
  try {
    if (ref == null || st == null) return;
    @PLA@ hp = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (hp == null || hp.getPageManager() == null || hp.getPageManager().getCustomPage() != this) return;
    @UCB@ c = new @UCB@();
    c.set("#SkyySInfo.Text", textOf(this.info));
    sendUpdate(c, false);
  } catch (Throwable t) { }
}'''), page))
page.addMethod(CtNewMethod.make(jt(r'''
public void onEvent(@REF@ ref, @ST@ st, @PLA@ player0, String data) {
  try {
    if (data == null) return;
    // 0.8.15 STORAGE HUB (kit 1.7): row 1 (Home + the hubs), row 2 (the Storage tabs) and the X FIRST
    String hr = null;
    try { hr = @PKG@.HubBar.route(this.playerRef, data, "storage", "pocket"); } catch (Throwable th) { hr = null; }
    if ("close".equals(hr)) { close(); return; }
    if (hr != null) {
      if (hr.equals("self")) { rebuild(); return; }
      if (hr.equals("back") || hr.equals("bridge") || hr.equals("command")) { hubAck(ref, st); return; }
      this.info = "-That tab could not open right now - try again.";
      rebuild();
      return;
    }
""")
P.rep('''    for (int i = 0; i < 36; i++) {
      if (a.equals("cell:" + i)) {
        if (this.cells != null && this.cells[i] != null) this.sel = this.cells[i];
        this.info = "";
        rebuild();
        return;
      }
    }
    if (a.equals("pg:prev")) { this.pageNo = this.pageNo - 1; rebuild(); return; }
    if (a.equals("pg:next")) { this.pageNo = this.pageNo + 1; rebuild(); return; }
''', '''    if (a.startsWith("cell:")) {   // 0.8.15: cell:<place in the whole scrolling grid>
      int ci0 = -1;
      try { ci0 = Integer.parseInt(a.substring(5).trim()); } catch (Throwable tc) { ci0 = -1; }
      if (this.cells != null && ci0 >= 0 && ci0 < this.cells.length && this.cells[ci0] != null) this.sel = this.cells[ci0];
      this.info = "";
      rebuild();
      return;
    }
''')
P.rep(between("    // EXPERIMENT 0.3.0: open with an (empty) container window", 'openCustomPageWithWindows returned false"));\n', inclusive_b=True),
      '''    // 0.8.15 (kit 1.7 hub page, 1600 x 980): the Void opens as Storage > Pocket like every hub page - no container window under it any more
    // (that 9-slot window was empty and nothing read it: every deposit / withdraw is a button on the page); it replaces any open page
    player.getPageManager().openCustomPage(ref, store, new {PKG}.SacksPage(pr, (String) null));
''')

# ================================================================================================ 2. /craft on the kit 1.7 hub page
P.rep('''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True)
CP_W, CP_H = 1200, 960
CSH = SUI.hub_shell("SkyyCraft", CP_W, CP_H, "smithing", row=True)
assert CSH.body == "SkyyCraftBody" and CSH.inner_w == 1152 and CSH.inner_h == 822 and CP_H <= SUI.MAX_PAGE_H
''', '''# (0.8.15: HubBar is installed above the Void page now - kit 1.7 page17 / subTab / growSize, used by both pages)
# 0.8.15 (kit 1.7): the 1600 x 980 hub page - row 1, row 2 (Crafting selected), the ONE sub-tab row (the crafter's tabs), the content (the old
# body id SkyyCraftBody: every old appendInline keeps working), the footer (the result line, Craftable only, Refresh)
CSH = SUI.hub_page("SkyyCraft", "smithing", sub=True, footer=True, body_id="SkyyCraftHB", content_id="SkyyCraftBody")
CP_W, CP_H = CSH.w, CSH.h
assert CSH.content == "SkyyCraftBody" and CSH.inner_w == 1552 and CSH.inner_h == 676 and CSH.sub == "SkyyCraftSub" and CSH.foot == "SkyyCraftFoot"
''')
P.rep(between("CP_BODY_H = {  # the tallest body of each view", "assert all(_v <= CSH.inner_h for _v in CP_BODY_H.values()), CP_BODY_H\n"),
      '''CP_BODY_H = {  # 0.8.15: the tallest content of each view (the tabs are the sub-tab row, the foot is the footer) - every one fits CSH.inner_h
    "craft": 40 + 22 + 6 * 98, "camp": 22 + 24 + 6 * 98,           # the search / materials (/ campfire) lines + about 6 rows of 98
    "proc": 22 + 26 + 22 + 18 + 22 + 46 + 42 + 4 * 98,              # the materials line, the Furnace lines (+ fuel) + 4 rows
    "pick": 22 + 26 + 22 + 18 + 22 + 46 + 42 + 40 + 132 + 2 * 100 + 8}   # ADD FUEL: + the title, the picked fuel's box, 2 big fuel rows
''')
P.rep('''assert CSH.inner_h - (CP_FIXED["tabs"] + CP_FIXED["search"] + CP_FIXED["note"] + CP_FIXED["foot"]) >= 6 * (CP_ROW_H + 6), "6 rows with one tab row"
''', '''assert CSH.inner_h - (CP_FIXED["search"] + CP_FIXED["note"]) >= 6 * (CP_ROW_H + 6), "0.8.15: about 6 rows of 98 below the search + note lines"
# 0.8.15: the footer's 48 px buttons + the ADD FUEL scroll list (kit pieces)
_CP_FLIST = SUI.scroll_list("SkyyPFList", h=4321, well=True)
assert _CP_FLIST.count("Height: 4321") == 1 and "TopScrolling" in _CP_FLIST
SUI.check_markup(_CP_FLIST)
_fbs = lambda kind, **kw: SUI.theme_button_style(kind, "normal", theme="sky", **kw)
CP_CONST.update({"F_SEC": _fbs("secondary"), "F_TER": _fbs("tertiary"), "F_TERON": _fbs("tertiary", selected=True),
                 "FLIST_A": _CP_FLIST.split("4321")[0], "FLIST_B": _CP_FLIST.split("4321")[1]})
# Skyy rule 7 through the shared kit rule: the /craft rows keep 0.8.14's tuned 92 / 128 / 168 (drawRow's fonts / icons per size) - each
# within skyyui.grow_row_sizes' caps for the smallest list (the Furnace tab with fuel); the ADD FUEL rows = grow_row_sizes of a 48 px row
_cp_min_list = CSH.inner_h - (22 + 26 + 22 + 18 + 22 + 46 + 42) - 4
_cp_cap = SUI.grow_row_sizes(_cp_min_list, CP_ROW_H, gap=6)
assert 128 <= _cp_cap[1] and 168 <= _cp_cap[2] and 168 <= _cp_min_list // 2, (_cp_min_list, _cp_cap)
CP_FUEL_HS = SUI.grow_row_sizes(CSH.inner_h - (22 + 26 + 22 + 18 + 22 + 46 + 42 + 40 + 132) - 4, 48, gap=4)
assert CP_FUEL_HS == [48, 69, 96], CP_FUEL_HS
''')
P.rep('''CP_HUBBUILD = SUI.java_hub_build(CSH, CP_HUB_TAB, cls="@PKG@.HubBar")
''', '''CP_HUBBUILD = SUI.java_hub_page(CSH, CP_HUB_TAB, cls="@PKG@.HubBar")   # 0.8.15: HubBar.page17 (rows 1 + 2, the X)
# 0.8.15: every look of the page shell + rows 1 + 2 + the widest sub-tab row, checked as one page (kit 1.7; the harness checks the REAL page)
CP_SUBTABS_MAX = ["Crafting", "Gear", "Farming", "Campfire", "Furnace", "Tannery", "Collections"]   # buildTabs' most (ProcStore.BENCHES = 2)
SUI.assert_sub_tabs_fit(CP_SUBTABS_MAX)
_cpv = SUI.hub_page_preview(CSH, my_tab=CP_HUB_TAB)
_cpv.extend(SUI.sub_tabs_preview("SkyyCraft", CP_SUBTABS_MAX, 0))
_cpv.check("Skyy")
SUI.assert_proven(_cpv, what="Crafting hub page")
SUI.check_sky_paths(_cpv, tab_icons=True)
SUI.assert_menu_page(_cpv, CSH)
''')
P.rep('''public static int rowSize(int n, int used) {
  int avail = listH(used) - 8;
  if (n < 1) n = 1;
  if (n * (ROWHS[2] + 6) <= avail) return 2;
  if (n * (ROWHS[1] + 6) <= avail) return 1;
  return 0;
}"""), cpg))
''', '''public static int rowSize(int n, int used) {
  // 0.8.15: the shared kit rule (HubBar.growSize = skyyui.grow_pick): the biggest of ROWHS whose n rows all fit the list, else 0 (it scrolls)
  return @PKG@.HubBar.growSize(n, listH(used) - 8, ROWHS, 6);
}"""), cpg))
cpg.addField(CtField.make("public static final int[] FUELHS = new int[] { %s };" % ", ".join(str(_h) for _h in CP_FUEL_HS), cpg))   # 0.8.15
''')
P.rep('''  int tw = pickI(680, 650, 610);
''', '''  int tw = pickI(1080, 1050, 1010);   // 0.8.15: the 1552 px hub page (680 / 650 / 610 in the old 1152 body)
''')
P.rep(between("# the result line + the pager (+ the page's own toggles): every view ends with it\n", "# D. ADD FUEL (Skyy"),
      '''# 0.8.15 (kit 1.7): a 48 px footer button (the kit's normal sky button art; foot_button's look with a runtime label)
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String fbtn(String id, String text, int w, String st) {
  return "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: 48); Padding: (Horizontal: 10); Text: \\"" + @PKG@.SacksPage.safe(text) + "\\"; " + st + " }";
}"""), cpg))
# the result line + the page's own toggles: every view ends with it. 0.8.15: into the page footer #SkyyCraftFoot (info left, buttons right);
# no pager any more - every list scrolls (pageNo / pages are ignored)
cpg.addMethod(CtNewMethod.make(jt(r"""
public void foot(@UCB@ b, @UEB@ ev, int pageNo, int pages, boolean only, boolean craftOnly, boolean refresh) {
  int iw = 1552 - (craftOnly ? 240 : 0) - (refresh ? 150 : 0);
  b.appendInline("#SkyyCraftFoot", lbl("SkyyCInfo", iw, 48, L_INFO));
  b.set("#SkyyCInfo.Text", this.info == null ? "" : this.info);
  if (craftOnly) {
    b.appendInline("#SkyyCraftFoot", gap(10));
    b.appendInline("#SkyyCraftFoot", fbtn("SkyyCOnly", "Craftable only " + (only ? "ON" : "OFF"), 230, only ? F_TERON : F_TER));
    ev.addEventBinding(@BT@.Activating, "#SkyyCOnly", @EVD@.of("a", "onlyc"));
  }
  if (refresh) {
    b.appendInline("#SkyyCraftFoot", gap(10));
    b.appendInline("#SkyyCraftFoot", fbtn("SkyyPRefresh", "Refresh", 140, F_SEC));
    ev.addEventBinding(@BT@.Activating, "#SkyyPRefresh", @EVD@.of("a", "prefresh"));
  }
}"""), cpg))
''')
P.rep(between("public void fuelPicker(@UCB@ b, @UEB@ ev, @PLA@ p, String k, String bench, @PKG@.ProcBench view) {\n",
              'cpg.addMethod(CtNewMethod.make(jt(r"""\npublic void buildProc('),
      r'''public void fuelPicker(@UCB@ b, @UEB@ ev, @PLA@ p, String k, String bench, @PKG@.ProcBench view) {
  // 0.8.15 (kit 1.7, Skyy "I never want to have to use a back button"): ONE in-page view - the picked fuel's amount box + Load on top, the
  // fuel list below as ONE scroll list (few fuels = bigger rows, Skyy rule 7); Pick on another row switches; Add fuel (shown selected while
  // open) or the bench's sub-tab closes it. No pages, no back / cancel button.
  int room = @PKG@.ProcBench.FUEL_CAP - view.fuelCount();
  if (room < 0) room = 0;
  java.util.ArrayList owned = fuelsOwned(p, k);
  long selHave = 0L;
  for (int i = 0; this.fuelSel != null && i < owned.size(); i++) {
    Object[] e = (Object[]) owned.get(i);
    if (this.fuelSel.equals(e[0])) selHave = ((Long) e[1]).longValue();
  }
  if (this.fuelSel != null && selHave <= 0L) this.fuelSel = null;
  int above = this.usedH + 26 + 22 + 18 + 22 + 46 + 42 + 40;
  b.appendInline("#SkyyCraftBody", "Group #SkyyPFHead { Anchor: (Height: 36, Bottom: 4); LayoutMode: Left; }");
  b.appendInline("#SkyyPFHead", lbl("SkyyPFTitle", 1500, 32, L_HEAD));
  if (this.fuelSel != null) {
    above = above + 132;
    long max = selHave < (long) room ? selHave : (long) room;
    b.set("#SkyyPFTitle.Text", "Add " + pretty(this.fuelSel) + " to the " + bench + " - or pick another fuel below");
    b.appendInline("#SkyyCraftBody", "Group #SkyyPFSel { Anchor: (Height: 128, Bottom: 4); LayoutMode: Left; Padding: (Full: 12); Background: " + BG_PANEL + "; }");
    b.appendInline("#SkyyPFSel", "Group { Anchor: (Width: 96, Height: 96); Padding: (Full: 6); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: 84, Height: 84); ItemId: \"" + @PKG@.SacksPage.safe(this.fuelSel) + "\"; } }");
    b.appendInline("#SkyyPFSel", gap(16));
    b.appendInline("#SkyyPFSel", "Group #SkyyPFCol { Anchor: (Width: 980, Height: 104); LayoutMode: Top; }");
    b.appendInline("#SkyyPFCol", lbl("SkyyPFName", 980, 28, L_NAME));
    b.set("#SkyyPFName.Text", pretty(this.fuelSel));
    b.appendInline("#SkyyPFCol", lbl("SkyyPFHave", 980, 26, L_TEXT));
    b.set("#SkyyPFHave.Text", "You have " + @PKG@.SacksPage.num(selHave) + " (inventory + the Void). Room in the fuel slot: " + @PKG@.SacksPage.num((long) room) + ".");
    b.appendInline("#SkyyPFCol", "Group #SkyyPFAmtRow { Anchor: (Height: 40, Top: 6); LayoutMode: Left; }");
    b.appendInline("#SkyyPFAmtRow", FUEL_MK);
    b.appendInline("#SkyyPFAmtRow", gap(10));
    b.appendInline("#SkyyPFAmtRow", btn("SkyyPFLoad", "Load", 140, 0, max > 0L ? B_PRI : B_PRIDIS));
    b.appendInline("#SkyyPFAmtRow", gap(12));
    b.appendInline("#SkyyPFAmtRow", lbl("SkyyPFMax", 400, 32, L_CAP));
    b.set("#SkyyPFMax.Text", max > 0L ? ("up to " + @PKG@.SacksPage.num(max) + " - empty loads all of them") : "the fuel slot is full");
    if (max > 0L) {
      ev.addEventBinding(@BT@.Activating, "#SkyyPFLoad", @EVD@.of("a", "pfload").append("@FuelAmt", "#SkyyCFuelAmt.Value"));
      ev.addEventBinding(@BT@.Validating, "#SkyyCFuelAmt", @EVD@.of("a", "pfload").append("@FuelAmt", "#SkyyCFuelAmt.Value"), false);
    }
  } else {
    b.set("#SkyyPFTitle.Text", "Pick a fuel - most first (your inventory + the Void). Add fuel closes this list.");
  }
  int lh = BODYH - above - 4;
  if (lh < 120) lh = 120;
  b.appendInline("#SkyyCraftBody", FLIST_A + lh + FLIST_B);
  int n = owned.size() < 100 ? owned.size() : 100;
  int fz = @PKG@.HubBar.growSize(n, lh - 8, FUELHS, 4);
  int rh = FUELHS[fz];
  int fr = fz == 2 ? 84 : (fz == 1 ? 60 : 42);
  String sN = fz == 2 ? L_NAME2 : (fz == 1 ? L_NAMEB : L_NAME);
  String sH = fz == 2 ? L_HAVE2 : (fz == 1 ? L_HAVEB : L_HAVE);
  this.fuelList = new String[n];
  for (int j = 0; j < n; j++) {
    Object[] e = (Object[]) owned.get(j);
    String fid = (String) e[0];
    this.fuelList[j] = fid;
    boolean on = fid.equals(this.fuelSel);
    String rid = "SkyyPFRow" + j;
    b.appendInline("#SkyyPFList", "Group #" + rid + " { Anchor: (Height: " + rh + ", Bottom: 4); LayoutMode: Left; Padding: (Horizontal: 8); Background: " + BG_ROW + "; }");
    b.appendInline("#" + rid, "Group { Anchor: (Width: " + fr + ", Height: " + fr + ", Top: " + ((rh - fr) / 2) + "); Padding: (Full: 3); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: " + (fr - 6) + ", Height: " + (fr - 6) + "); ItemId: \"" + @PKG@.SacksPage.safe(fid) + "\"; } }");
    b.appendInline("#" + rid, gap(12));
    b.appendInline("#" + rid, lbl("SkyyPFN" + j, 900, rh, sN));
    b.set("#SkyyPFN" + j + ".Text", pretty(fid));
    b.appendInline("#" + rid, lbl("SkyyPFC" + j, 300, rh, sH));
    b.set("#SkyyPFC" + j + ".Text", "x " + @PKG@.SacksPage.num(((Long) e[1]).longValue()));
    b.appendInline("#" + rid, btn("SkyyPFPick" + j, on ? "Picked" : "Pick", 120, (rh - 32) / 2, on ? B_TERON : B_SEC));
    if (!on) ev.addEventBinding(@BT@.Activating, "#SkyyPFPick" + j, @EVD@.of("a", "pfpick:" + j));
  }
  if (owned.isEmpty()) {
    b.appendInline("#SkyyPFList", lbl("SkyyPFNone", 1500, 40, L_TEXTC));
    b.set("#SkyyPFNone.Text", "No fuel on you or in the Void - logs, planks, sticks and charcoal burn.");
  } else if (owned.size() > n) {
    b.appendInline("#SkyyPFList", lbl("SkyyPFMore", 1500, 40, L_TEXTC));
    b.set("#SkyyPFMore.Text", "Showing the " + n + " fuels you have most of.");
  }
  foot(b, ev, 0, 0, false, false, false);
}"""), cpg))
''')
P.rep('''  b.appendInline("#SkyyCraftBody", lbl("SkyyPStat", 1152, 26, L_STAT));
''', '''  b.appendInline("#SkyyCraftBody", lbl("SkyyPStat", 1552, 26, L_STAT));   // 0.8.15: the 1552 px page (1152 / 1100 before)
''')
P.rep('''  b.appendInline("#SkyyCraftBody", lbl("SkyyPProg", 1152, 22, L_TEXTC));
''', '''  b.appendInline("#SkyyCraftBody", lbl("SkyyPProg", 1552, 22, L_TEXTC));
''')
P.rep('''  int fw = pct * 1100 / 100;
''', '''  int fw = pct * 1500 / 100;
''')
P.rep('''  b.appendInline("#SkyyPBarRow", "Group #SkyyPBar { Anchor: (Width: 1100, Height: 10); LayoutMode: Left; Background: " + C_TRACK + "; }");
''', '''  b.appendInline("#SkyyPBarRow", "Group #SkyyPBar { Anchor: (Width: 1500, Height: 10); LayoutMode: Left; Background: " + C_TRACK + "; }");
''')
P.rep('''  b.appendInline("#SkyyCraftBody", lbl("SkyyPQueue", 1152, 22, L_CAPC));
''', '''  b.appendInline("#SkyyCraftBody", lbl("SkyyPQueue", 1552, 22, L_CAPC));
''')
# build() -> renderPage(b, ev, p, u) (the whole page from the Player; the harness builds the real page through it) + a short build()
P.rep('''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  if (u != null) @PKG@.ProcTask.PAGEOPEN.put(u, Boolean.TRUE);   // 0.7.18: the 1 s task keeps visiting (the profile notice)
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
@SHELL@
  @HUBBUILD@
  this.key = null;
''', '''public void renderPage(@UCB@ b, @UEB@ ev, @PLA@ p, java.util.UUID u) {
@SHELL@
  @HUBBUILD@
  this.key = null;
''')
P.rep(between('''  // the crafter's own tabs (the vanilla tab rule: the active one Primary, the others Secondary) after''', '''  // 0.7.3 search row (Crafting / Artifacts'''),
      '''  // 0.8.15 (kit 1.7): the crafter's own tabs = the page's ONE sub-tab row (small buttons, the open one Primary); no back button - row 1
  // (Storage) leads to the Void
  for (int i = 0; i < this.tabs.size(); i++) {
    String[] t = (String[]) this.tabs.get(i);
    @PKG@.HubBar.subTab(b, ev, "SkyyCraft", i, t[1], t[0].equals(this.tab) && !searching, "tab:" + i, 150);
  }
''')
P.rep('''  b.appendInline("#SkyyCraftBody", lbl("SkyyCMatNote", 1152, 22, L_CAPC));
''', '''  b.appendInline("#SkyyCraftBody", lbl("SkyyCMatNote", 1552, 22, L_CAPC));
''')
P.rep('''    b.appendInline("#SkyyCraftBody", lbl("SkyyCCampNote", 1152, 24, L_STAT));
''', '''    b.appendInline("#SkyyCraftBody", lbl("SkyyCCampNote", 1552, 24, L_STAT));
''')
P.rep('''  this.usedH = 42 * (tabRow + 1) + (srow ? 40 : 0) + 22 + (campTab ? 24 : 0) + 66;
''', '''  this.usedH = (srow ? 40 : 0) + 22 + (campTab ? 24 : 0);   // 0.8.15: the tab rows / the foot are the sub-tab row / the footer now
''')
P.rep('''  foot(b, ev, 0, 0, only, true, false);
}""".replace("@SHELL@", CP_SHELL).replace("@HUBBUILD@", CP_HUBBUILD)), cpg))
''', '''  foot(b, ev, 0, 0, only, true, false);
}""".replace("@SHELL@", CP_SHELL).replace("@HUBBUILD@", CP_HUBBUILD)), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  if (u != null) @PKG@.ProcTask.PAGEOPEN.put(u, Boolean.TRUE);   // 0.7.18: the 1 s task keeps visiting (the profile notice)
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  renderPage(b, ev, p, u);   // 0.8.15: the page itself (kit 1.7 hub page)
}"""), cpg))
''')

# ================================================================================================ the Storage > Pocket contract tab (VoidHubOpen)
P.rep('''chop = pool.makeClass(PKG + ".CraftHubOpen")
''', '''chop = pool.makeClass(PKG + ".CraftHubOpen")
vho = pool.makeClass(PKG + ".VoidHubOpen")   # 0.8.15: hub:tab:storage:pocket (the Void page, kit 1.7)
''')
P.rep('''}""" % (CP_HUB_TAB, CP_HUB_LABEL, CP_HUB_ORDER, CP_HUB_ICON)), chop))
''', '''}""" % (CP_HUB_TAB, CP_HUB_LABEL, CP_HUB_ORDER, CP_HUB_ICON)), chop))

# ================= 0.8.15 VoidHubOpen: hub:tab:storage:pocket ("Pocket", the contract row of SUI.HUB_TABS) - the Void page for the UUID ======
# The owner's own tab (SkyyMenu's stand-in steps aside: put before us = it skips, put after us = ours replaces it). FALSE = the bar runs /sacks.
vho.addInterface(pool.get("java.util.function.Function"))
vho.addConstructor(CtNewConstructor.make("public VoidHubOpen() { }", vho))
vho.addMethod(CtNewMethod.make(jt(r"""
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
    @PGM@ pm = p.getPageManager();
    if (pm == null) return Boolean.FALSE;
    pm.openCustomPage(r, st, new @PKG@.SacksPage(pr, (String) null));
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.SackPool.warn("the Storage > Pocket tab could not open the Void page: " + t);
    return Boolean.FALSE;
  }
}"""), vho))
vho.addMethod(CtNewMethod.make(jt(r"""
public static int register() {
  Object[] e = @PKG@.HubBar.putIcon("storage", "pocket", "SkyySacks", "Pocket", 10, "sacks", new @PKG@.VoidHubOpen(), null, "storage_pocket");
  return e == null ? 0 : 1;
}"""), vho))
''')
P.rep('''  try {{ hubTab = {PKG}.CraftHubOpen.register(); }} catch (Throwable th) {{ {PKG}.SackPool.warn("the Crafting hub tab could not be registered - /craft still works: " + th); }}
''', '''  try {{ hubTab = {PKG}.CraftHubOpen.register(); }} catch (Throwable th) {{ {PKG}.SackPool.warn("the Crafting hub tab could not be registered - /craft still works: " + th); }}
  int voidTab = 0;   // 0.8.15: the Storage hub's Pocket tab (hub:tab:storage:pocket)
  try {{ voidTab = {PKG}.VoidHubOpen.register(); }} catch (Throwable th) {{ {PKG}.SackPool.warn("the Storage > Pocket tab could not be registered - /sacks still works: " + th); }}
''')
P.rep('''"; Crafting hub tab " + (hubTab == 1 ? "on" : "OFF") + " (/craft''', '''"; Storage > Pocket tab " + (voidTab == 1 ? "on" : "OFF") + "; Crafting hub tab " + (hubTab == 1 ? "on" : "OFF") + " (/craft''')
P.rep('''          hubb, acl, aset, chop):   # 0.8.11: HubBar (kit 1.6), AccLink, AccSettle, CraftHubOpen
''', '''          hubb, acl, aset, chop,   # 0.8.11: HubBar (kit 1.6), AccLink, AccSettle, CraftHubOpen
          vho):   # 0.8.15: VoidHubOpen (HubBar is kit 1.7 now)
''')

# the Pocket tab's icon pair ships in this jar too (the same bytes SkyyMenu ships for its stand-in; whichever jar loads last, the same picture)
P.rep(r"""    files[_jp] = _data
print("0.8.11 kit art: %d Sky Window files + the Crafting tab icon pair" % len(_kit))
""", r"""    files[_jp] = _data
# 0.8.15: + the storage_pocket tab icon pair (the Storage > Pocket tab SkyySacks puts now; art/hub-tab-icons, sha256 = its manifest)
_pv = SUI.hub_tab_icon_paths("storage", "pocket")
for _fn, _jp in (("storage_pocket.png", _pv[2]), ("storage_pocket_on.png", _pv[3])):
    _data = open(os.path.join(HERE, "..", "art", "hub-tab-icons", _fn), "rb").read()
    _me = [f for f in _TAM["files"] if f["path"] == _fn]
    assert len(_me) == 1 and _hl.sha256(_data).hexdigest() == _me[0]["sha256"] and len(_data) == _me[0]["bytes"], "0.8.15: %s = its manifest entry" % _fn
    assert _jp.startswith("Common/UI/Custom/SkyyHubTabs/") and _jp not in files
    files[_jp] = _data
print("0.8.11 kit art: %d Sky Window files + the Crafting and Pocket tab icon pairs" % len(_kit))
""")

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added or removed"
assert "openCustomPageWithWindows" not in P.s and "SkyyCBags" not in P.s and "SkyyPFBack" not in P.s and "hub_shell(" not in P.s
assert '"< Prev"' not in P.s and "SkyyVPager" not in P.s and "SkyyCPrev" not in P.s
P.finish()
