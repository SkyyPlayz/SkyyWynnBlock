"""Derive SkyyGear/build_skyygear_0.3.16.py from the LIVE 0.3.15 (build_skyygear_0.3.15.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_15_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_16_patch.py      then      python SkyyGear/build_skyygear_0.3.16.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.16.py

0.3.16 (2026-10-16) = MENU PATTERN sweep S3 (Crafting hub), the SkyyGear part - LAYOUT ONLY. Gear 0.3.16 was earmarked for the T1 tool-upgrade
round; that work is NOT in this round and moves to SkyyGear 0.3.17. Spec research/Menu-Pattern.md (section 3, the S3 row of section 4, merge M3 with
Skyy's answer 6, rules 7 + 8); recipe tools/HUBS-CONTRACT.md "Kit 1.7" -> "How to move a page". Skyy's words (docs/answered/ui.md 2026-10-16):
"Double check every menu and make sure it's fully and completely built out / designed properly in the cohesive menu system we made. I never
want to have to use a back button. The menus at the top should always be there for easy navigation." + "keep this top bar at this size consistent
at the top across every menu." + "i dont mind scrolling, but if there are only a few items try to scale them to all fit." + popups: every hub page
Home size (1600 x 980), row 2 big like Teleport (56 px), Crafting = Crafting / Smithing / Anvil (Reforge + Identify inside) / Upgrade, keep only the
old commands that still fit.
1. EVERY GEAR PAGE = SUI.hub_page (kit 1.7, 1600 x 980; 0.3.15: 1100 x 940 / 976 with the kit 1.6 big row + strip): title bar ("Crafting"),
   row 1 (Home + the 7 hubs at Home's size) and row 2 (the Crafting tabs at Teleport's size: Crafting | Smithing | Anvil | Upgrade, the page's
   own tab lit) from the kit's HubBar.page17, the X; the old body #SkyyGBody is the content group (1066 wide = the old inner width, centred).
   Pages: Smithing (set cards AND every set / piece page), Anvil (Reforge + Identify views), Upgrade (= the lifelong tools page), the old Upgrade
   list (lifelong tools off), and the part.anvil-off legacy pages (old Reforge page + its Upgrade mode, Multitool page, the 0.2.11 Identify page).
   GearHub.page / foot / anvilSub / list hold the kit-built markup; the 0.3.15 kit 1.6 strip (GearHub.bars) is gone.
2. ONE SUB-TAB ROW, only on the Anvil: Reforge | Identify (kit small buttons, the active one Primary; mode:0 / mode:5 = the Anvil's own in-place
   switch) with the purse / Appraisal Tool line on its right (Menu-Pattern 3.1 row 3: "Right side may hold ... the purse line").
3. NO BACK BUTTONS (rule 8): the footer's BACK / CLOSE button is gone from every page (rows 1 + 2 and the X lead away; the 'back' click still works
   for a stale page); the set page's BACK button is gone - a set is an in-page selection: the category buttons on the left (the open set's category
   stays lit) and row 2's Smithing tab lead back to the cards. The footer (kit 10 + 48) = the result line #SkyyGInfo + REFRESH.
4. SCROLL, NOT PAGES (Menu-Pattern 3.3 + rule 7): the Smithing cards (6 a page) and a set's piece rows (6 a page) and the old Upgrade list (8 a
   page) are ONE scroll list each (their Prev / Next went; the prev / next / rprev / rnext / pg: clicks still answer); a short list uses bigger
   rows (HubBar.growSize over SUI.grow_row_sizes: piece rows 74 / 107 / 148, Upgrade rows 70 / 101 / 140, Anvil rows 46 / 66 / 92 with a 32 ->
   64 px icon), content centred in the taller row. The Anvil list always scrolls (ui.frames off no longer pages it: the kit page is the sky
   theme either way). The cards grid keeps its 266 x 300 cards (3 a row, 10 px apart for the scroll bar) - already big tiles, two rows visible.
5. part.anvil-off pages: the Reforge-page mode row keeps only the page's own modes (Reforge / Upgrade / Multitool); Smithing / Tools / Identify /
   Upgrade are row 2's tabs. Their hub clicks route through HubBar.route like the other pages (0.3.15 routed only the four default pages).
6. Two animation-data lines that name the MovementCondition branch "Back" are marked menu-pattern-ok (no button text).
Commands: none added, none removed; /smithing /reforge /identify /upgrade /toolpoints open their tab / view exactly as in 0.3.15.
Content, items, coins, crafting, reforge, identify, upgrade, reset points, tool fetch and every click: UNCHANGED.
SAVED DATA: none. ROLLBACK 0.3.16 -> 0.3.15: safe (pages only); the 0.3.15 STOP rule (Gear 0.3.15+ with Menu 0.3.34+) still holds - 0.3.16 needs
no new STOP rule (kit 1.7 HubBar lives in this jar; row 2's art: its own tab icons, + SkyyMenu 0.3.35's hub:art when loaded).
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.15.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.16.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.15"' in s and "GENERATED by tools/gear_0_3_15_patch.py" in s, "not the generated 0.3.15 script"
assert "SUI.hub_page(" not in s and "GearHub.page(" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def cut(start, end, new):
    """Replace the text from `start` (inclusive) up to `end` (exclusive) - both unique - with `new`."""
    assert s.count(start) == 1 and s.count(end) == 1, (s.count(start), s.count(end), start[:80], end[:80])
    i, j = s.index(start), s.index(end)
    assert i < j, (start[:60], end[:60])
    rep(s[i:j], new)


def rep_in(start, end, pairs):
    """Inside the region start .. end (both unique, start first) replace each (old, new, count) - counted inside the region only."""
    assert s.count(start) == 1 and s.count(end) == 1, (s.count(start), s.count(end), start[:80], end[:80])
    i, j = s.index(start), s.index(end)
    assert i < j
    reg = s[i:j]
    new = reg
    for o, n_, c in pairs:
        assert new.count(o) == c, "region anchor count %d (want %d): %s" % (new.count(o), c, o[:140])
        new = new.replace(o, n_)
    rep(reg, new)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.15":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.15" % _set.get("SkyyGear"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI
assert SUI.KIT_PAGE_VERSION == "1.7", "0.3.16 needs kit skyyui 1.7 (hub_page)"

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.16 (2026-10-16)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.15 - build script (javassist via jpype). GENERATED by tools/gear_0_3_15_patch.py from the LIVE 0.3.14 (itself GENERATED by
tools/gear_0_3_14_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.15.py -> SkyyGear/SkyyGear-0.3.15.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.15.py
''', '''"""SkyyGear 0.3.16 - build script (javassist via jpype). GENERATED by tools/gear_0_3_16_patch.py from the LIVE 0.3.15 (itself GENERATED by
tools/gear_0_3_15_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.16.py -> SkyyGear/SkyyGear-0.3.16.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.16.py

''' + NOTE + '''
--- 0.3.15 notes ---
''')
rep('VERSION = "0.3.15"\n', 'VERSION = "0.3.16"\n')

# ================================================================================================================ 6. lint: animation data, not buttons
rep('''            return [(k, "i") for k in ("Forward", "Back", "Left", "Right", "ForwardLeft", "ForwardRight", "BackLeft", "BackRight", "Failed")]
''', '''            return [(k, "i") for k in ("Forward", "Back", "Left", "Right", "ForwardLeft", "ForwardRight", "BackLeft", "BackRight", "Failed")]  # menu-pattern-ok (MovementCondition branch names, no button)
''')
rep('''            return self.seq([rt], self.mx([self.steps(d.get(k), depth + 1) for k in ("Forward", "Back", "Left", "Right", "ForwardLeft",
''', '''            return self.seq([rt], self.mx([self.steps(d.get(k), depth + 1) for k in ("Forward", "Back", "Left", "Right", "ForwardLeft",  # menu-pattern-ok (branch names)
''')

# ================================================================================================================ 1. the kit 1.7 HubBar + GearHub's page pieces
rep('''ghbar = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True, big=True)
''', '''assert SUI.KIT_PAGE_VERSION == "1.7", "0.3.16: kit skyyui 1.7 (hub_page)"
ghbar = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True, big=True, page=True)   # 0.3.16: + kit 1.7 (page17, subTab, growSize)
''')

G316_EARLY = r'''# ####################################################################################################################################
# 0.3.16 MENU PATTERN (kit 1.7, tools/gear_0_3_16_patch.py items 1-4): every Gear page = SUI.hub_page 1600 x 980 - title bar, row 1 (Home + the
# 7 hubs), row 2 (the Crafting tabs, the page's own lit), the content group = the old body #SkyyGBody (every old append keeps working; 1066 wide,
# centred), the footer #SkyyGHpFoot (result line + Refresh). The Anvil alone has the ONE sub-tab row (Reforge | Identify + the purse line).
# GearHub.page / foot / anvilSub / list / grow* = the kit-built markup the pages call.
# ####################################################################################################################################
G316_PFX = "SkyyGHp"
G316_KW = dict(body_id="SkyyGHpB", content_id="SkyyGBody", content_w=G315_BODY_W, content_layout="Top")
G316_SH = SUI.hub_page(G316_PFX, "smithing", footer=True, **G316_KW)
G316_SHS = SUI.hub_page(G316_PFX, "smithing", sub=True, footer=True, **G316_KW)
assert (G316_SH.w, G316_SH.h, G316_SH.content_h, G316_SHS.content_h, G316_SH.content_w) == (1600, 980, 716, 676, 1066), (G316_SH.content_h, G316_SHS.content_h)
assert (G316_SH.content, G316_SH.foot, G316_SHS.sub) == ("SkyyGBody", "SkyyGHpFoot", "SkyyGHpSub") and not G316_SH.sets and not G316_SHS.sets
G316_ROW = SUI.java_hub_page(G316_SH, cls="@PKG@.HubBar", uuid="u", tab_expr="tabOf(sel)")
assert G316_ROW == SUI.java_hub_page(G316_SHS, cls="@PKG@.HubBar", uuid="u", tab_expr="tabOf(sel)") == '@PKG@.HubBar.page17(b, ev, "SkyyGHp", "smithing", tabOf(sel), 1552, u, 2);', G316_ROW
G316_IW = SUI.HUB_PAGE_IW
G316_BTN = 170                                   # the footer's REFRESH (the old bar's button width)
G316_INFO_W = G316_IW - G316_BTN - SUI.FOOT_GAP  # the result line left of it
G316_FOOT = SUI.Appends([
    (G316_SH.foot, SUI.label("SkyyGInfo", "", "default", w=G316_INFO_W, h=SUI.FOOT_BTN_H, size=16, bold=True,
                             col=SUI.J("@PKG@.GearUi.infoColor(info)", SUI.COLOR["success"]), wrap=True, padding={"horizontal": 8})),
    (G316_SH.foot, SUI.spacer(w=SUI.FOOT_GAP, h=SUI.FOOT_BTN_H)),
    (G316_SH.foot, SUI.foot_button("SkyyGBtnRefresh", "Refresh", G316_BTN))])
G316_SUBS = ("Reforge", "Identify")
SUI.assert_sub_tabs_fit(list(G316_SUBS))
G316_LINE_W = G316_IW - len(G316_SUBS) * SUI.SUB_TAB_W - SUI.SUB_TAB_GAP - 10     # the purse / Appraisal Tool line right of the sub-tabs
G316_SUBX = SUI.Appends([(G316_SHS.sub, SUI.spacer(w=10, h=SUI.SUB_TAB_H)),
                         (G316_SHS.sub, SUI.label("SkyyGFoot", "", "default", w=G316_LINE_W, h=SUI.SUB_TAB_H, size=15, col="text", wrap=True, max_lines=2))])
# the scroll lists (Menu-Pattern 3.3): the kit's scroll_list, its id and height filled in at runtime
_l316 = SUI.scroll_list("SkyyGXList", h=999)
assert _l316.count("SkyyGXList") == 1 and _l316.count("Height: 999") == 1 and _l316.index("SkyyGXList") < _l316.index("Height: 999")
_a316, _r316 = _l316.split("SkyyGXList")
_b316, _c316 = _r316.split("Height: 999")
G316_LIST = "%s + id + %s + h + %s" % (SUI.java_lit(_a316), SUI.java_lit(_b316 + "Height: "), SUI.java_lit(_c316))
# rule 7 (Skyy "if there are only a few items try to scale them to all fit"): the row tiers of each list (normal, 1.45x, 2x)
G316_PIECE_H = 534          # a set's piece rows: the right column 630 - the reason line 40 - Craft every missing piece 56
G316_UP_H = 646             # the old Upgrade list: 686 - 6 - the head 34
G316_GROW_PIECE = SUI.grow_row_sizes(G316_PIECE_H, 74, gap=0)
G316_GROW_UP = SUI.grow_row_sizes(G316_UP_H, 70, gap=6)
G316_GROW_ANVIL = SUI.grow_row_sizes(522, 46, gap=0)          # the Anvil list's smaller height (with Identify all + the tick row)
assert (G316_GROW_PIECE, G316_GROW_UP, G316_GROW_ANVIL) == ([74, 107, 148], [70, 101, 140], [46, 66, 92]), (G316_GROW_PIECE, G316_GROW_UP, G316_GROW_ANVIL)
assert SUI.grow_pick(3, G316_PIECE_H, G316_GROW_PIECE, 0) == 2 and SUI.grow_pick(8, G316_PIECE_H, G316_GROW_PIECE, 0) == 0
# build-time check of both shells (kit 1.7 recipe step 6): the shell + rows 1 / 2 (the Crafting strip as Gear's tabs label it) + stand-in
# content of each page's real height + the footer; the harness runs assert_menu_page on every REAL rendered page
G316_TABS = [("recipes", "Crafting"), ("gear", "Smithing"), ("reforge", "Anvil"), ("upgrade", "Upgrade")]
for _sh316, _what, _kids in ((G316_SH, "Smithing / Upgrade / legacy pages", [("Group #SkyyGMain { Anchor: (Height: 686); LayoutMode: Left; }"),
                                                                          ("Group #SkyyGFootS { Anchor: (Height: 30); }")]),
                             (G316_SHS, "the Anvil (Reforge | Identify)", [("Group #SkyyGMain { Anchor: (Height: 662); LayoutMode: Left; }")])):
    _pv = SUI.hub_page_preview(_sh316, tabs=G316_TABS, my_tab="gear" if _sh316 is G316_SH else "reforge")
    if _sh316.sub:
        _pv.extend(SUI.sub_tabs_preview(G316_PFX, list(G316_SUBS), 0))
        _pv.extend(G316_SUBX)
    for _k in _kids:
        _pv.append((_sh316.content, _k))
    _pv.extend(G316_FOOT)
    SUI.check_page(_pv, "SkyyG")
    SUI.assert_proven(_sh316.appends, what="0.3.16 Gear hub page")
    SUI.check_sky_paths(_sh316.appends, tab_icons=True)
    SUI.assert_menu_page(_pv, _sh316, what="0.3.16 " + _what)
G316_JSH = G316_SH.java("b").replace(chr(10), chr(10) + "    ")
G316_JSHS = G316_SHS.java("b").replace(chr(10), chr(10) + "    ")
M(ghub, r"""
public static void page(@UCB@ b, @UEB@ ev, java.util.UUID u, int sel, boolean sub) {
  N[0] = N[0] + 1L;
  if (sub) {
    @@SHS@@
  } else {
    @@SH@@
  }
  @@ROW@@
}""".replace("@@SHS@@", G316_JSHS).replace("@@SH@@", G316_JSH).replace("@@ROW@@", G316_ROW))
# the footer: the result line (+ done white, - refused gold, = neutral: GearUi.infoColor) and REFRESH; no Back / Close (rule 8: rows 1 + 2, the X)
M(ghub, r"""
public static void foot(@UCB@ b, @UEB@ ev, String info) {
  @@FOOT@@
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(info));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
}""".replace("@@FOOT@@", G316_FOOT.java("b").replace(chr(10), chr(10) + "  ")))
# the Anvil's ONE sub-tab row: Reforge | Identify (a = mode:0 / mode:5 - the Anvil page's own in-place switch) + the purse line #SkyyGFoot (b.set
# by the page)
M(ghub, r"""
public static void anvilSub(@UCB@ b, @UEB@ ev, boolean idm, boolean it) {
  @PKG@.HubBar.subTab(b, ev, "SkyyGHp", 0, "Reforge", !idm, "mode:0", @@SW@@);
  if (it) @PKG@.HubBar.subTab(b, ev, "SkyyGHp", 1, "Identify", idm, "mode:5", @@SW@@);
  @@SUBX@@
}""".replace("@@SW@@", str(SUI.SUB_TAB_W)).replace("@@SUBX@@", G316_SUBX.java("b").replace(chr(10), chr(10) + "  ")))
# a scroll list (kit scroll_list) #<id>, h px high, into parent
M(ghub, r"""
public static void list(@UCB@ b, String parent, String id, int h) {
  b.appendInline(parent, @@LIST@@);
}""".replace("@@LIST@@", G316_LIST))
# rule 7: the row height of a list of n rows in avail px (the kit's HubBar.growSize over three tiers)
M(ghub, r"""
public static int growOf(int n, int avail, int h0, int h1, int h2, int gap) {
  int[] hs = new int[] { h0, h1, h2 };
  return hs[@PKG@.HubBar.growSize(n, avail, hs, gap)];
}""")
M(ghub, "public static int growPiece(int n) { return growOf(n, %d, %d, %d, %d, 0); }" % ((G316_PIECE_H,) + tuple(G316_GROW_PIECE)))
M(ghub, "public static int growUp(int n) { return growOf(n, %d, %d, %d, %d, 6); }" % ((G316_UP_H,) + tuple(G316_GROW_UP)))
# the Anvil rows (44 + the 2 px line): n rows + 4 rows of room for the Requip block under them
M(ghub, "public static int growAnvil(int n, int avail) { return growOf(n + 4, avail, %d, %d, %d, 0) - 2; }" % tuple(G316_GROW_ANVIL))
'''
cut('''M(ghub, r"""
public static int bars(@UCB@ b, @UEB@ ev, java.util.UUID u, int sel) {''', '''# a click on the bars (world thread): null = not a hub click; "self" = redraw this page; "close" = close it; anything else = handled elsewhere
''', G316_EARLY)

# ================================================================================================================ 5. the legacy mode row: only the page's own modes
rep('''  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0) + (lt ? 1 : 0) + (it ? 1 : 0) + (ut ? 1 : 0);
''', '''  int n = 1 + (up ? 1 : 0) + (mt ? 1 : 0);          // 0.3.16: Smithing / Tools / Identify / Upgrade are row 2's tabs (kit 1.7) - only the page's own modes here
''')
rep('''    if (m == 5 && !it) continue;
    if (m == 3 && !cr) continue;
''', '''    if (m == 3 || m == 4 || m == 5 || m == 6) continue;          // 0.3.16: row 2 has them
''')

# ================================================================================================================ 1. the pages: the kit page shell where the frame was
_UU = "this.playerRef.getUuid()"
rep('''  this.rows = @PKG@.GearForge.rows(inv);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
''', '''  this.rows = @PKG@.GearForge.rows(inv);
  @PKG@.GearHub.page(b, ev, %s, 0, false);          // 0.3.16: the kit 1.7 page (part.anvil off: the old Reforge page)
''' % _UU)
rep('''  this.rows = @PKG@.GearMerge.rows(inv);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
''', '''  this.rows = @PKG@.GearMerge.rows(inv);
  @PKG@.GearHub.page(b, ev, %s, 2, false);          // 0.3.16: the kit 1.7 page (the Multitool page)
''' % _UU)
rep('''  this.rows = @PKG@.GearUp.rows(inv);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
''', '''  this.rows = @PKG@.GearUp.rows(inv);
  @PKG@.GearHub.page(b, ev, %s, 1, false);          // 0.3.16: the kit 1.7 page (the old Reforge page's Upgrade mode)
''' % _UU)
rep('''  @PKG@.GearUi.frame(b, "Identify", 1100, 880);
''', '''  @PKG@.GearHub.page(b, ev, %s, 5, false);          // 0.3.16: the kit 1.7 page (the 0.2.11 Identify page)
''' % _UU)
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 940);          // 0.3.15: + the big hub row and the Crafting hub's strip
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), 3);
  @PKG@.GearUi.ap(b, "#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 662); LayoutMode: Left; Padding: (Top: 6); }");
''', '''  @PKG@.GearHub.page(b, ev, this.playerRef.getUuid(), 3, false);          // 0.3.16: the kit 1.7 page (Smithing lit); content 716 = main 686 + the line 30
  @PKG@.GearUi.ap(b, "#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 686); LayoutMode: Left; Padding: (Top: 6); }");
''')
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 976);          // 0.3.15: + the big hub row, the Crafting hub's strip (Anvil lit), Reforge | Identify
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), this.anIdM ? 5 : 0);
  @PKG@.GearHub.anvilSub(b, ev, this.anIdM, @PKG@.GearAnvil.idTab());
''', '''  @PKG@.GearHub.page(b, ev, this.playerRef.getUuid(), this.anIdM ? 5 : 0, true);          // 0.3.16: the kit 1.7 page (Anvil lit) + the ONE sub-tab row
  @PKG@.GearHub.anvilSub(b, ev, this.anIdM, @PKG@.GearAnvil.idTab());          // Reforge | Identify + the purse line #SkyyGFoot
''')
rep('''  @PKG@.GearUi.ap(b, "#SkyyGBody", "Label #SkyyGFoot { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  @PKG@.GearUi.st(b, "#SkyyGFoot.Text", (have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)") + "   -   Upgrade materials: inventory, then your bags   -   " + @PKG@.GearAnvil.toolLineT(anTier(u)));
''', '''  @PKG@.GearUi.st(b, "#SkyyGFoot.Text", (have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)") + "   -   Upgrade materials: inventory, then your bags   -   " + @PKG@.GearAnvil.toolLineT(anTier(u)));          // 0.3.16: on the sub-tab row
''')
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 940);          // 0.3.15: + the big hub row and the Crafting hub's strip (Upgrade lit)
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), 4);
''', '''  @PKG@.GearHub.page(b, ev, this.playerRef.getUuid(), 4, false);          // 0.3.16: the kit 1.7 page (Upgrade lit = the lifelong tools page)
''')

# ---- the old Upgrade list (UpgPage): one scroll list, bigger rows when few, the kit footer
cut('''  int per = 8;          // 0.3.12: 8 rows a page (Skyy 2026-10-16; was 6)
''', '''# the Tier up click: GearUp.upgrade = the Anvil's tier-up (same check, cost, skill gate, inventory + bags, restore on failure, log, sound)
''', r'''  this.pageNo = 0;          // 0.3.16: one scroll list (no pages; the pg: clicks still answer)
  @PKG@.GearHub.page(b, ev, this.playerRef.getUuid(), 6, false);          // 0.3.16: the kit 1.7 page (Upgrade lit); content 716 = main 686 + the line 30
  b.appendInline("#SkyyGBody", "Group #SkyyGUMain { Anchor: (Height: 686); LayoutMode: Top; Padding: (Top: 6); }");
  b.appendInline("#SkyyGUMain", "Label #SkyyGUHead { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  int items = 0;
  int away = 0;          // fix round 2: the lifelong rows count too (the pole on you = on you; a lifelong tool not on you = not on you)
  for (int i = 0; i < this.rows.size(); i++) {
    Object[] e0 = (Object[]) this.rows.get(i);
    if (e0[0] instanceof Integer) items++;
    else if (e0[0] == null) { if ("here".equals(e0[2])) items++; else away++; }
  }
  b.set("#SkyyGUHead.Text", (items == 0 && nrq == 0 && away == 0 ? "Nothing you carry can tier up right now" : "Everything you own that can tier up (" + items + " on you" + (away > 0 ? ", " + away + " not on you" : "") + (nrq > 0 ? ", " + nrq + " in Requip" : "") + ")"));
  @PKG@.GearHub.list(b, "#SkyyGUMain", "SkyyGUList", @@UPH@@);          // 0.3.16: the kit scroll list (was 8 rows a page)
  if (inv == null) {
    b.appendInline("#SkyyGUList", "Label { Anchor: (Height: 40); Text: \"Your inventory cannot be read right now - click Refresh.\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  } else {
    for (int i = 0; i < this.rows.size(); i++) row(b, ev, u, inv, pk, P, i, (Object[]) this.rows.get(i));
    if (this.rows.isEmpty()) b.appendInline("#SkyyGUList", "Label { Anchor: (Height: 60); Text: \"Tools, gathering armor and gear with a next tier show up here while you carry them or keep them in Requip. Your lifelong tools tier up here too.\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, Wrap: true); }");
  }
  b.appendInline("#SkyyGBody", "Label #SkyyGFoot { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGFoot.Text", "Costs count your inventory and your Magic Bags. Tiering up keeps rarity and rolls. Reforge on the Anvil, Upgrade Points on Tools.");
  @PKG@.GearHub.foot(b, ev, this.info);          // 0.3.16 kit footer (UpgPage): the result line + Refresh (no Prev / Next / Back)
}""")
'''.replace("@@UPH@@", "646"))
assert "646" == str(646)
rep('''  b.appendInline("#SkyyGUList", "Group " + rid + " { Anchor: (Height: 70); LayoutMode: Left; Padding: (Full: 6); Background: #000000(0.25); " + @PKG@.GearUi.cell(58, id)''',
    '''  int rh9 = @PKG@.GearHub.growUp(this.rows == null ? 1 : this.rows.size());          // 0.3.16 (rule 7): few rows = taller rows, content centred
  b.appendInline("#SkyyGUList", "Group " + rid + " { Anchor: (Height: " + rh9 + "); LayoutMode: Left; Padding: (Horizontal: 6, Top: " + (6 + (rh9 - 70) / 2) + "); Background: #000000(0.25); " + @PKG@.GearUi.cell(58, id)''')

# ---- the footers: the old bar (info + Refresh + Back / Close) -> GearHub.foot on every other page
_BAR = '"Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");'
_BACK = '"#SkyyGBtnBack", @EVD@.of("a", "back"));'
_MENU = '  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;\n'
assert s.count(_BAR) == s.count(_BACK) == 7, (s.count(_BAR), s.count(_BACK))
_spans = []
_k = 0
while True:
    _e = s.find(_BACK, _k)
    if _e < 0:
        break
    _e2 = s.index("\n", _e) + 1
    _b = s.rfind(_BAR, 0, _e)
    _st = s.rfind("\n", 0, _b) + 1
    if s[:_st].endswith(_MENU):
        _st -= len(_MENU)
    _m = s.rfind(chr(10) + 'M(', 0, _st) + 1
    _who = s[_m + 2:s.index(",", _m)] + "." + s[s.index("public ", _m):s.index("(", s.index("public ", _m))].split()[-1]
    _spans.append((s[_st:_e2], _who))
    _k = _e2
assert len(_spans) == 7 and all(_t.startswith(_MENU) for _t, _w in _spans), [w for _t, w in _spans]
_same = {}
for _t, _w in _spans:
    assert "#SkyyGBtnRefresh" in _t and '"refresh"' in _t and "#SkyyGInfo" in _t and "Prev" not in _t, _w
    _same.setdefault(_t, []).append(_w)
for _t, _ws in _same.items():          # byte-identical bars (the part.anvil-off pages) are replaced together
    rep(_t, "  @PKG@.GearHub.foot(b, ev, this.info);          // 0.3.16 kit footer (%s): the result line + Refresh (no Back / Close: rows 1 + 2, the X)\n" % " / ".join(_ws), len(_ws))
G316_FOOTED = sorted(w for _t, w in _spans)
assert G316_FOOTED == ["ipg.build", "lpg.build", "mpg.build", "rpg.anBuild", "rpg.build", "rpg.upBuild", "spg.build"], G316_FOOTED

# ================================================================================================================ 3 + 4. the Smithing page: cards + set page
cut('''M(spg, r"""
public void cardsArea(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv) {''', '''# one piece / tier row (height 74): icon | name + band + materials (2 lines of 2) | Craft
''', r'''M(spg, r"""
public void cardsArea(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv) {
  @PKG@.GearUi.ap(b, "#SkyyGMain", "Group #SkyyGCards { Anchor: (Width: 830); LayoutMode: Top; }");
  this.pageNo = 0;          // 0.3.16: ONE scroll list of every card (was 6 a page; the prev / next clicks still answer)
  int n = this.cards.size();
  if (n == 0) {
    @PKG@.GearUi.ap(b, "#SkyyGCards", "Label #SkyyGNone1 { Anchor: (Height: 60); Text: \"\"; Style: (FontSize: 17, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    @PKG@.GearUi.st(b, "#SkyyGNone1.Text", "Nothing in " + @PKG@.GearSmith.CAT_NAME[this.cat] + " can be crafted on this server yet.");
    return;
  }
  @PKG@.GearHub.list(b, "#SkyyGCards", "SkyyGCardList", 680);          // 0.3.16: main 686 - 6
  int rows = (n + 2) / 3;
  for (int r = 0; r < rows; r++) {
    String rid = "#SkyyGCardRow" + r;
    if (r > 0) @PKG@.GearUi.ap(b, "#SkyyGCardList", "Group { Anchor: (Height: 12); }");
    @PKG@.GearUi.ap(b, "#SkyyGCardList", "Group " + rid + " { Anchor: (Height: 300); LayoutMode: Left; }");
    for (int k = 0; k < 3; k++) {
      int i = r * 3 + k;
      if (i >= n) break;
      if (k > 0) @PKG@.GearUi.ap(b, rid, @PKG@.GearUi.gap(10));          // 0.3.16: 10 apart (was 16): the scroll bar's room
      card(b, ev, rid, i, (Object[]) this.cards.get(i), u, inv);
    }
  }
}""")
''')
# piece / tier rows: taller when few (rule 7), 6 px narrower for the scroll bar
rep('''  String gid = "#SkyyGPc" + i;
''', '''  String gid = "#SkyyGPc" + i;
  int rh9 = @PKG@.GearHub.growPiece(this.grp == null ? 1 : ((String[]) this.grp[1]).length);          // 0.3.16 (rule 7): few rows = taller rows
''', 2)
rep('''"Group " + gid + " { Anchor: (Height: 74); LayoutMode: Left; Padding: (Top: 4); }"''',
    '''"Group " + gid + " { Anchor: (Height: " + rh9 + "); LayoutMode: Left; Padding: (Top: " + (4 + (rh9 - 74) / 2) + "); }"''', 2)
rep('''"Group " + gid + "T { Anchor: (Width: 330); LayoutMode: Top; }"''', '''"Group " + gid + "T { Anchor: (Width: 324); LayoutMode: Top; }"''', 2)
rep('''"Label " + lid + "L" + k + " { Anchor: (Width: 165);''', '''"Label " + lid + "L" + k + " { Anchor: (Width: 162);''')
# the set page: no Back (rule 8: the category buttons + row 2's Smithing tab), every piece row in one scroll list
rep('''  @PKG@.GearUi.ap(b, "#SkyyGPHead", "TextButton #SkyyGBtnPBack { Anchor: (Width: 120, Height: 40); Text: \\"Back\\"; " + @PKG@.GearUi.btn(1) + " }");
  @PKG@.GearUi.ap(b, "#SkyyGPHead", "Label #SkyyGPTitle { Anchor: (Width: 700, Height: 40); Padding: (Horizontal: 14);''',
    '''  @PKG@.GearUi.ap(b, "#SkyyGPHead", "Label #SkyyGPTitle { Anchor: (Width: 830, Height: 40); Padding: (Horizontal: 14);''')
rep('''  @PKG@.GearUi.on(b, ev, @BT@.Activating, "#SkyyGBtnPBack", @EVD@.of("a", "pback"));
''', '''  // 0.3.16: no Back button (rule 8) - the category buttons on the left (this set's lit) and row 2's Smithing tab lead back; 'pback' still answers
''')
rep('''"Group #SkyyGPBody { Anchor: (Height: 600); LayoutMode: Left; Padding: (Top: 6); }"''', '''"Group #SkyyGPBody { Anchor: (Height: 636); LayoutMode: Left; Padding: (Top: 6); }"''')
rep('''  @PKG@.GearUi.ap(b, "#SkyyGPRight", "Group #SkyyGRows { Anchor: (Height: 444); LayoutMode: Top; }");
''', '''  @PKG@.GearHub.list(b, "#SkyyGPRight", "SkyyGRows", %d);          // 0.3.16: one scroll list (was 6 rows a page)
''' % 534)
rep('''  int per = 6;
  int pages = (outs.length + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.rowPage >= pages) this.rowPage = pages - 1;
  if (this.rowPage < 0) this.rowPage = 0;
  int start = this.rowPage * per;
  for (int i = start; i < outs.length && i < start + per; i++) {
''', '''  this.rowPage = 0;          // 0.3.16: every row in the scroll list (the rprev / rnext clicks still answer)
  for (int i = 0; i < outs.length; i++) {
''')
cut('''  if (pages > 1) {
    @PKG@.GearUi.ap(b, "#SkyyGPRight", "Group #SkyyGRPager { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
''', '''# find the open group again by its key (filters / recipes may have changed): null = gone
''', '''  // 0.3.16: no Tiers x-y pager (one scroll list)
}""")
''')

# ================================================================================================================ 4. the Anvil list: always scrolls, bigger rows when few
_AL0 = 'public void anList(@UCB@ b, @UEB@ ev, @INV@ inv, java.util.UUID u, java.util.ArrayList un) {'
_AL1 = 'M(rpg, r"""\npublic void anBuild(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {'
rep_in(_AL0, _AL1, [
    ('''  boolean t = @PKG@.GearUi.tex();
''', '''  boolean t = true;          // 0.3.16: the kit 1.7 page is the sky theme either way - the list always scrolls (ui.frames off paged it)
''', 1),
    ('''  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
''', '''  int rh9 = @PKG@.GearHub.growAnvil(this.rows.size(), lh);          // 0.3.16 (rule 7): few rows = taller rows (44 / 64 / 90) and a bigger icon
  int ic9 = rh9 - 12 > 64 ? 64 : rh9 - 12;
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
''', 1),
    ('''"Group #SkyyGRowW" + i + " { Anchor: (Height: 44); LayoutMode: Left; TextButton #SkyyGTick" + i + " { Anchor: (Width: 52, Height: 44);''',
     '''"Group #SkyyGRowW" + i + " { Anchor: (Height: " + rh9 + "); LayoutMode: Left; TextButton #SkyyGTick" + i + " { Anchor: (Width: 52, Height: " + rh9 + ");''', 1),
    ('''Button " + rid + " { Anchor: (Width: 412, Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32);''',
     '''Button " + rid + " { Anchor: (Width: 412, Height: " + rh9 + "); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: " + ic9 + ", Height: " + ic9 + ");''', 1),
    ('''Label #SkyyGRowName" + i + " { Anchor: (Width: 210);''', '''Label #SkyyGRowName" + i + " { Anchor: (Width: " + (210 - (ic9 - 32)) + ");''', 1),
    ('''"Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32);''',
     '''"Button " + rid + " { Anchor: (Height: " + rh9 + "); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: " + ic9 + ", Height: " + ic9 + ");''', 1),
    ('''Label #SkyyGRowName" + i + " { Anchor: (Width: 262);''', '''Label #SkyyGRowName" + i + " { Anchor: (Width: " + (262 - (ic9 - 32)) + ");''', 1),
])

# ================================================================================================================ 3 + 5. clicks (late: before the always-answer wrapper)
G316_LATE = r'''# ####################################################################################################################################
# 0.3.16 (tools/gear_0_3_16_patch.py items 3 + 5): row 2's Smithing tab on an open set = back to the cards (no Back button); the part.anvil-off
# pages (old Reforge page + its Upgrade mode, Multitool, the 0.2.11 Identify page) route their row 1 / row 2 / X clicks like the others.
# ####################################################################################################################################
spg.getDeclaredMethod("handleDataEvent").insertBefore(J(r"""{
  if ($3 != null && this.view == 1 && @PKG@.Gear.jsonStr($3, "a").equals("hub:gear")) { this.view = 0; this.gkey = null; this.info = ""; rebuild(); return; }
}"""))
rpg.getDeclaredMethod("handleDataEvent").insertBefore(J(r"""{
  if (!@PKG@.GearCfg.ANVIL_ON && $3 != null) {
    String hr8 = null;
    try { hr8 = @PKG@.GearHub.route(this.playerRef, $3, this.mode == 1 ? 1 : 0); } catch (Throwable th8) { hr8 = null; }
    if (hr8 != null) { if (hr8.equals("close")) close(); else if (hr8.equals("self")) rebuild(); return; }
  }
}"""))
for _pg, _sel in ((mpg, "2"), (ipg, "5")):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J(_HUBCLICK.replace("@SEL@", _sel)))
pl.getDeclaredMethod("start").insertAfter(J("""{ @PKG@.Gear.info("[SkyyGear] 0.3.16: the kit 1.7 pages (1600 x 980, rows 1 + 2, no back buttons, scroll lists)"); }"""))
print("0.3.16 menu pattern: GearHub.page / foot / anvilSub / list on %d page builds; hub clicks on the legacy pages too" % 8)
'''
before('''from jpype import JClass as _JC10
''', G316_LATE)

# ================================================================================================================ checks on the result
assert s.count("@PKG@.GearHub.page(") == 8 and s.count("@PKG@.GearHub.foot(b, ev, this.info);") == 8, (s.count("@PKG@.GearHub.page("), s.count("@PKG@.GearHub.foot("))
assert s.count("@PKG@.GearUi.frame(b,") == 0 and s.count("GearHub.bars(") == 0 and "#SkyyGBtnBack" not in s and "#SkyyGBtnPBack" not in s
assert "#SkyyGBtnPrev" in s          # only the part.anvil-off legacy list pagers (frames off) - checked below
_i = s.index
assert _i("ghub = mk(\"GearHub\")") < _i("public static void page(@UCB@ b") < _i("public static int tabs(@UCB@ b, @UEB@ ev, String parent, int sel, int w, String title)")
assert _i("public static void page(@UCB@ b") < _i('M(spg, r"""\npublic void build(') and _i("_HUBCLICK = ") < _i("for _pg, _sel in ((mpg, \"2\"), (ipg, \"5\")):")
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.15 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.15 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
