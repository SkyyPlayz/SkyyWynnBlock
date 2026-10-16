"""Derive SkyyGear/build_skyygear_0.3.15.py from the LIVE 0.3.14 (build_skyygear_0.3.14.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_14_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_15_patch.py      then      python SkyyGear/build_skyygear_0.3.15.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.15.py

0.3.15 (2026-10-16, round "smithhub" / gear0315; the T1 tool-upgrade round that had 0.3.15 reserved becomes 0.3.16). Skyy's words
(docs/answered/ui.md 2026-10-16, screenshots of the Crafting hub): "one problem with the menu. crafting shows smithing reforge, upgrade, and
identify. but in smithing it doesnt." + the standing "replace, dont add extra" / "make sure we dont have any duplicates"; the Home row: "its a
little small in the crafting one though. keep this top bar at this size consistent at the top across every menu."; the Tools page: "i dont see
1 for tools. BUT tools can be rolled into upgrade. just below reset points add an upgrade button. and thats 1 less menu. (we can move upgrading
armor to the smithing tab.)"; the set page: "just change to the anvil to upgrade".
1. THE CRAFTING HUB BARS ON EVERY SMITHING PAGE: the Smithing (set cards), Anvil (Reforge + its Identify view) and Upgrade (lifelong tools)
   pages draw (a) the BIG hub row (Home / Character / Storage / Market / Crafting / World / Social / Settings, Crafting lit) at the SkyWynn Menu
   Home size - the new kit helper (tools/skyyui.py "THE BIG HUB ROW": install_hub_bar(..., big=True) + java_hub_big_row; HubBar.bigRow), and
   (b) the Crafting hub's tab strip (the kit HubBar.build2, the same strip the /craft page draws). Skyy's popup 2026-10-16 "Crafting / Smithing
   / Anvil (Reforge + Identify inside) / Upgrade (your tools)" -> "Yes, those 4": the strip is Crafting | Smithing | Anvil | Upgrade with the
   page's own tab lit; the Anvil page has a Reforge | Identify sub-row under the strip (its in-place switch). The old inner SMITHING / ANVIL /
   IDENTIFY / TOOLS / UPGRADE row is gone from these pages (the legacy part.anvil-off Reforge / Multitool / Identify pages keep it - not
   reachable with the defaults). Clicks: HubBar.route first (a row hub, a tab, Home). Pages 1100 x 880 -> 1100 x 940 (the Anvil 976):
   assert_big_hub_page: +56 row +52 strip -48 old row (+36 the Anvil's sub-row); content unchanged.
2. SKYYGEAR OWNS ITS CRAFTING-HUB TABS (HUBS-CONTRACT: hub:tab:smithing:gear "Smithing" 10 /smithing, reforge "Anvil" 30 /reforge, upgrade
   "Upgrade" 40 /upgrade, and identify "Identify" 60 /identify as a MERGED tab inside the Anvil (kit HUB_MERGED + HubHide: still published,
   so /identify and saved shortcuts open the Anvil's Identify view; never drawn in a strip). Tab icons smithing_<tab> = the bytes SkyyMenu
   already ships; SkyyMenu's stand-ins step aside by themselves. Open = the command's own page code run as that player (GearHubOpen); shown
   while the page exists (Smithing: part.smithing; Upgrade: lifelong tools, or part.upgrade's old Upgrade list).
3. TOOLS + UPGRADE = ONE TAB (Skyy "tools can be rolled into upgrade ... thats 1 less menu"): the Upgrade tab IS the lifelong tools page (Upgrade
   Points, Reset points, the tier-up, Make multitool). Its old "Tier up" button sits right below Reset points and is renamed UPGRADE - it is
   what the old Upgrade tab did for a lifelong tool (GearUp.upgrade: the Anvil's own tier-up, same costs / skill gate / journal), so no second
   button doing the same thing. /upgrade opens it while lifelong tools are on (part.lifelong; off = the 0.3.14 pages); /toolpoints too.
4. ARMOR UPGRADES ON THE SMITHING TAB (Skyy "just change to the anvil to upgrade"): on a set page each tier-up piece's TO THE ANVIL button is an
   UPGRADE button: it takes the player's previous-tier piece that passes every check - one in the inventory first; else one in Requip whose
   own document passes GearUp.check and whose cost the player has (checked BEFORE anything moves; critic fix 1-2) is taken out with
   wardrobe:fn:fetch, the Anvil's Take out - and runs GearUp.upgrade (the Anvil's tier-up: check, cost from inventory + bags, skill gate, counts before / after, log,
   sound) - same refusals. The page's "Open the Anvil" button goes (the hub's Reforge tab is the one way there). Gear upgrades (weapons) stay
   on the Anvil.
Commands: none added, none removed; /smithing /reforge /identify /upgrade /toolpoints still open their pages (/upgrade = the Upgrade tab).
SAVED DATA: none. ROLLBACK 0.3.15 -> 0.3.14: safe (pages and tabs only); SkyyMenu's stand-in tabs come back by themselves.
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.14.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.15.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.14"' in s and "GENERATED by tools/gear_0_3_14_patch.py" in s, "not the generated 0.3.14 script"
assert "GearHub" not in s and "HubBar" not in s and "\"tup:" not in s
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


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.14":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.14" % _set.get("SkyyGear"))

# the four tabs SkyyGear owns in the Crafting hub (id "smithing"): (tab, label, order, command) - the contract's orders / commands
G315_TABS = [("gear", "Smithing", 10, "smithing"), ("reforge", "Anvil", 30, "reforge"), ("upgrade", "Upgrade", 40, "upgrade"),
             ("identify", "Identify", 60, "identify")]          # Identify = a MERGED tab (kit HUB_MERGED): a view inside the Anvil tab
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI
for _t, _l, _o, _c in G315_TABS:
    _r = [r for r in SUI.HUB_TABS if (r[0], r[1]) == ("smithing", _t)]
    assert len(_r) == 1 and _r[0][2] == _o and _r[0][3] == "SkyyGear" and _r[0][5] == _c and SUI.hub_tab_label("smithing", _t) == _l, (_t, _r)
assert SUI.hub_merged_host("smithing", "identify") == "reforge" and [r[0] for r in SUI.hub_shown_tabs("smithing") if r[0] != "multitool"] == ["gear", "recipes", "reforge", "upgrade"]

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.14 - build script (javassist via jpype). GENERATED by tools/gear_0_3_14_patch.py from the LIVE 0.3.13 (itself GENERATED by
tools/gear_0_3_13_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.14.py -> SkyyGear/SkyyGear-0.3.14.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.14.py
''', '''"""SkyyGear 0.3.15 - build script (javassist via jpype). GENERATED by tools/gear_0_3_15_patch.py from the LIVE 0.3.14 (itself GENERATED by
tools/gear_0_3_14_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.15.py -> SkyyGear/SkyyGear-0.3.15.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.15.py

0.3.15 = THE CRAFTING HUB BARS ON EVERY SMITHING PAGE (notes: tools/gear_0_3_15_patch.py): the Smithing / Reforge (Anvil) / Upgrade / Identify
pages draw the big hub row (the SkyWynn Menu Home size, kit HubBar.bigRow) + the Crafting hub's tab strip (Crafting | Smithing | Reforge |
Upgrade | Identify) instead of their old inner row; SkyyGear owns those four hub tabs; the Tools page IS the Upgrade tab (its tier-up button is
UPGRADE now; /upgrade opens it); a set page's TO THE ANVIL buttons are UPGRADE buttons (the Anvil's tier-up, right there).

--- 0.3.14 notes ---
''')
rep('VERSION = "0.3.14"\n', 'VERSION = "0.3.15"\n')

# ================================================================================================================ 1. the hub bars (early: before GearUi.tabs' callers)
G315_EARLY = r'''# ####################################################################################################################################
# 0.3.15 THE CRAFTING HUB BARS (tools/gear_0_3_15_patch.py item 1): the kit's HubBar (kit 1.6 row + the big row) in THIS jar; GearHub draws the
# big hub row + the Crafting hub's tab strip where the old inner tab row was (Smithing / Anvil / Identify / Upgrade pages) and routes their
# clicks. Placed here: the pages that call it are built below.
# ####################################################################################################################################
import skyyui as SUI
SUI.verify(quiet=True)
G315_W, G315_H, G315_BODY_W = 1100, 940, 1066
assert SUI.assert_big_hub_page(1100, 880, old_title_h=48, hub="smithing", pad=17) == (G315_W, G315_H), "0.3.15: the Smithing pages + the big row + the strip fit 1080p"
assert SUI.assert_big_row_fits(G315_BODY_W) >= SUI.BIG_ROW_ICON_MIN and SUI.assert_hub_fits("smithing", G315_BODY_W) >= 110
G315_STRIP = SUI.hub_bar_markup("SkyyGBody", "SkyyG")[0][1]
assert G315_STRIP == "Group #SkyyGHubTabs { Anchor: (Height: 44, Bottom: 8); LayoutMode: Left; }", G315_STRIP
G315_BIG = SUI.java_hub_big_row("SkyyGBody", "SkyyG", "smithing", G315_BODY_W, cls="@PKG@.HubBar")
assert G315_BIG == '@PKG@.HubBar.bigRow(b, ev, "#SkyyGBody", "SkyyG", "smithing", 1066);', G315_BIG
ghbar = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True, big=True)
ghhide = SUI.install_hub_hide(pool, PKG + ".HubHide", CtField, CtNewMethod, CtNewConstructor)
ghub = mk("GearHub")
G315_CLASSES = [ghbar, ghhide, ghub]
G315_AH = 976          # the Anvil page: + the Reforge | Identify sub-row (36) under the strip
assert SUI.assert_big_hub_page(1100, 880 + 36, old_title_h=48, hub="smithing", pad=17) == (1100, G315_AH)
F(ghub, "public static final java.util.concurrent.ConcurrentHashMap PRS = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> the clicking page's PlayerRef
F(ghub, "public static final long[] N = new long[4];")          # 0 bars drawn, 1 hub clicks, 2 opened another page, 3 could not open
# the page's own tab: 3 Smithing (set cards) = gear, 4 the lifelong tools page / 6 the old Upgrade list / 1 = upgrade, else the Anvil (Reforge
# and its Identify view: Identify is a merged tab inside the Anvil tab - Skyy 2026-10-16 "Anvil (Reforge + Identify inside)")
M(ghub, r"""
public static String tabOf(int sel) {
  if (sel == 3) return "gear";
  if (sel == 4 || sel == 6 || sel == 1) return "upgrade";
  return "reforge";
}""")
M(ghub, r"""
public static int bars(@UCB@ b, @UEB@ ev, java.util.UUID u, int sel) {
  N[0] = N[0] + 1L;
  @@BIG@@
  b.appendInline("#SkyyGBody", "@@STRIP@@");
  return @PKG@.HubBar.build2(b, ev, "SkyyG", "smithing", tabOf(sel), @@W@@, u, 0, 0);
}""".replace("@@BIG@@", G315_BIG).replace("@@STRIP@@", G315_STRIP).replace("@@W@@", str(G315_BODY_W)))
# the Anvil tab's two views under the strip: Reforge | Identify (a = mode:0 / mode:5 - the Anvil page's own in-place switch)
M(ghub, r"""
public static void anvilSub(@UCB@ b, @UEB@ ev, boolean idm, boolean it) {
  b.appendInline("#SkyyGBody", "Group #SkyyGASub { Anchor: (Height: 36); LayoutMode: Left; Padding: (Bottom: 4); }");
  b.appendInline("#SkyyGASub", "TextButton #SkyyGASubR { Anchor: (Width: 180, Height: 32); Text: \"Reforge\"; " + @PKG@.GearUi.btn(idm ? 1 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGASubR", @EVD@.of("a", "mode:0"));
  if (!it) return;
  b.appendInline("#SkyyGASub", "Group { Anchor: (Width: 6); }");
  b.appendInline("#SkyyGASub", "TextButton #SkyyGASubI { Anchor: (Width: 180, Height: 32); Text: \"Identify\"; " + @PKG@.GearUi.btn(idm ? 0 : 1) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGASubI", @EVD@.of("a", "mode:5"));
}""")
# a click on the bars (world thread): null = not a hub click; "self" = redraw this page; "close" = close it; anything else = handled elsewhere
M(ghub, r"""
public static String route(@PR@ pr, String data, int sel) {
  if (pr == null || data == null) return null;
  String a = @PKG@.Gear.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return null;
  N[1] = N[1] + 1L;
  String r = null;
  java.util.UUID u = null;
  try {
    u = pr.getUuid();
    if (u != null) PRS.put(u, pr);
    r = @PKG@.HubBar.route(pr, data, "smithing", tabOf(sel));
  } catch (Throwable t) { r = "failed"; @PKG@.Gear.warnOnce("hubroute", "a Crafting hub click failed: " + t); }
  try { if (u != null) PRS.remove(u); } catch (Throwable t2) { }
  if (r == null) return "self";
  if (r.equals("failed") || r.equals("missing") || r.equals("hidden") || r.equals("nocmd")) {
    N[3] = N[3] + 1L;
    try { pr.sendMessage(@MSG@.raw("[Smithing] That page could not open (" + r + ").").color(@PKG@.GearDefs.C_GOLD)); } catch (Throwable t3) { }
    return "self";
  }
  if (!r.equals("self") && !r.equals("close")) N[2] = N[2] + 1L;
  return r;
}""")
'''
_G315_SZ = "G315_W, G315_H, G315_BODY_W = 1100, 940, 1066" + chr(10)
assert G315_EARLY.count(_G315_SZ) == 1
G315_EARLY = G315_EARLY.replace(_G315_SZ, _G315_SZ + "G315_TABS = %r          # (tab, label, order, command): the Crafting-hub tabs SkyyGear owns" % (G315_TABS,) + chr(10))
before('''# 0.2.22 the tab row: 0 Reforge, 1 Upgrade (part.upgrade on), 2 Multitool (multiTab); EventData a = "mode:<n>"; returns how many tabs show
''', G315_EARLY)

# ---- the four pages: the bars where the old inner row was; the page 60 px taller (the body grows with it, the content is unchanged)
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 3, 1066, "Smithing");''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 940);          // 0.3.15: + the big hub row and the Crafting hub's strip
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), 3);''')
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", this.anIdM ? 5 : 0, 1066, this.anIdM ? "Identify" : "Anvil");''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 976);          // 0.3.15: + the big hub row, the Crafting hub's strip (Anvil lit), Reforge | Identify
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), this.anIdM ? 5 : 0);
  @PKG@.GearHub.anvilSub(b, ev, this.anIdM, @PKG@.GearAnvil.idTab());''')
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 4, 1066, "Tools");''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 940);          // 0.3.15: + the big hub row and the Crafting hub's strip (Upgrade lit)
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), 4);''')
rep('''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 6, 1066, "Upgrade");''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 940);          // 0.3.15: + the big hub row and the Crafting hub's strip
  @PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), 6);''')

# ================================================================================================================ 3. the Tools page = the Upgrade tab
rep('''TextButton #SkyyGPUp { Anchor: (Width: 160, Height: 44); Text: \\"Tier up\\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");''',
    '''TextButton #SkyyGPUp { Anchor: (Width: 160, Height: 44); Text: \\"Upgrade\\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");          // 0.3.15: the Upgrade tab's button (was Tier up)''')
rep('''Tier them up with the Tier up button here or on the Anvil''', '''Tier them up with the Upgrade button here or on the Anvil''')
rep('''"   -   Tier up: the button on the right (or the Anvil)   -   ''', '''"   -   Upgrade (tier up): the button on the right (or the Anvil)   -   ''')
rep('''  super("toolpoints", "Your lifelong tools and their Upgrade Points (the Tools tab of /smithing)");''',
    '''  super("toolpoints", "Your lifelong tools and their Upgrade Points (the Upgrade tab of the Crafting hub)");''')
rep('''  super("upgrade", "Open the Reforge page on its Upgrade tab: turn an item into its next tier and keep its rarity and lines");''',
    '''  super("upgrade", "Open the Upgrade tab: your lifelong tools - Upgrade Points and tier-ups (armor: Smithing, other gear: the Anvil)");''')

# ================================================================================================================ 4. the set page: Upgrade buttons
rep('''  @PKG@.GearUi.st(b, gid + "U.Text", p == null ? "Not crafted here." : "Tier up a " + @PKG@.Gear.itemName(p) + " on the Anvil");''',
    '''  @PKG@.GearUi.st(b, gid + "U.Text", p == null ? "Not crafted here." : "Upgrade your " + @PKG@.Gear.itemName(p) + " - it keeps its rarity");          // 0.3.15''')
rep('''  @PKG@.GearUi.ap(b, gid + "B", "TextButton " + gid + "Go { Anchor: (Height: 40); Text: \\"To the Anvil\\"; " + @PKG@.GearUi.btn(1) + " }");
  @PKG@.GearUi.on(b, ev, @BT@.Activating, gid + "Go", @EVD@.of("a", "mode:0"));''',
    '''  boolean upOk = p != null && @PKG@.GearCfg.UP_ON;          // 0.3.15 (Skyy "just change to the anvil to upgrade"): the Anvil's tier-up, here
  @PKG@.GearUi.ap(b, gid + "B", "TextButton " + gid + "Go { Anchor: (Height: 40); Text: \\"Upgrade\\"; " + @PKG@.GearUi.btn(upOk ? 0 : 3) + " }");
  @PKG@.GearUi.on(b, ev, @BT@.Activating, gid + "Go", @EVD@.of("a", "tup:" + i + ":" + this.token));''')
rep('''"Higher tiers are not crafted: tier up the set below on the Anvil - it keeps its rarity, the new tier levels with your skill."''',
    '''"Higher tiers are not crafted: Upgrade each piece below - it keeps its rarity, the new tier levels with your skill."''')
rep('''  if (@PKG@.GearSmith.tierUp(g)) {          // 0.3.9: a tier-up set - the way to the Anvil instead of Craft every missing piece
    @PKG@.GearUi.ap(b, "#SkyyGPRight", "Group #SkyyGPAll { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
    @PKG@.GearUi.ap(b, "#SkyyGPAll", "TextButton #SkyyGBtnAnv { Anchor: (Width: 330, Height: 44); Text: \\"Open the Anvil\\"; " + @PKG@.GearUi.btn(0) + " }");
    @PKG@.GearUi.on(b, ev, @BT@.Activating, "#SkyyGBtnAnv", @EVD@.of("a", "mode:0"));
  } else if (c == 0 || c == 1) {''', '''  if (@PKG@.GearSmith.tierUp(g)) {          // 0.3.15: each piece has its own Upgrade button; the Anvil = the hub's Reforge tab (no second way)
  } else if (c == 0 || c == 1) {''')

# ================================================================================================================ 2. the tabs, the clicks, /upgrade (late: before the always-answer wrapper)
G315_LATE = r'''# ####################################################################################################################################
# 0.3.15 (tools/gear_0_3_15_patch.py items 1-4): GearHubOpen (the four Crafting-hub tabs SkyyGear owns: open = the command's own page code for
# that player; the set page's Upgrade = GearUp.upgrade) + GearHubVis (shown while the page exists); the hub clicks on the four pages (before
# the always-answer wrapper copies their handlers); /upgrade = the Upgrade tab (the lifelong tools page); setup / start / shutdown.
# ####################################################################################################################################
ghop = mk("GearHubOpen")
ghvis = mk("GearHubVis")
G315_CLASSES += [ghop, ghvis]
ghop.addInterface(pool.get("java.util.function.Function"))
F(ghop, "public int k;")
F(ghop, "public static volatile int REG;")
F(ghop, "public static final long[] N = new long[6];")          # 0 tab opens, 1 refused (no player / page), 2 set-page upgrades, 3 refused, 4 Requip take-outs, 5 errors
C(ghop, "public GearHubOpen(int k) { this.k = k; }")
F(ghop, "public static final String[] TAB = %s;" % jarr([t for t, _l, _o, _c in G315_TABS]))
F(ghop, "public static final String[] LABEL = %s;" % jarr([l for _t, l, _o, _c in G315_TABS]))
F(ghop, "public static final String[] CMD = %s;" % jarr([c for _t, _l, _o, c in G315_TABS]))
F(ghop, "public static final int[] ORDER = new int[] { %s };" % ", ".join(str(o) for _t, _l, o, _c in G315_TABS))
# shown while the page exists: 0 Smithing (part.smithing), 1 Reforge (always: the Anvil / Reforge page), 2 Upgrade (the lifelong tools page,
# or part.upgrade's own Upgrade list / the old Reforge-page Upgrade mode), 3 Identify (identify.command)
M(ghop, r"""
public static boolean shows(int k) {
  if (k == 0) return @PKG@.GearCfg.SMITH_ON;
  if (k == 1) return true;
  if (k == 2) return @PKG@.GearCfg.LL_ON || (@PKG@.GearCfg.UP_ON && (@PKG@.GearCfg.UPG_TAB || !@PKG@.GearCfg.ANVIL_ON));
  if (k == 3) return @PKG@.GearCfg.IDENTIFY_CMD;
  return false;
}""")
# the tab's page for that player (world thread): exactly what its command runs (same package: the commands' execute is reachable)
M(ghop, r"""
public static boolean open(@PR@ pr, int k) {
  if (pr == null) return false;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return false;
  @ST@ s = r.getStore();
  if (s == null) return false;
  if (k == 0) new @PKG@.SmithCmd().execute((@CTX@) null, s, r, pr, (@WLD@) null);
  else if (k == 1) new @PKG@.ReforgeCmd().execute((@CTX@) null, s, r, pr, (@WLD@) null);
  else if (k == 2) new @PKG@.UpCmd().execute((@CTX@) null, s, r, pr, (@WLD@) null);
  else if (k == 3) new @PKG@.IdentifyCmd().execute((@CTX@) null, s, r, pr, (@WLD@) null);
  else return false;
  return true;
}""")
M(ghop, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) o;
    Object c = @PKG@.GearHub.PRS.get(u);
    @PR@ pr = c instanceof @PR@ ? (@PR@) c : null;
    if (pr == null) { try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t1) { pr = null; } }
    if (open(pr, this.k)) { N[0] = N[0] + 1L; return Boolean.TRUE; }
    N[1] = N[1] + 1L;
  } catch (Throwable t) { N[5] = N[5] + 1L; @PKG@.Gear.warnOnce("hubopen" + this.k, "the Crafting hub tab " + this.k + " could not open: " + t); }
  return Boolean.FALSE;
}""")
# why the piece x of the player cannot tier up NOW (GearUp.check: tier, identified, special, skill gate, the recipe; then the cost from the
# inventory + bags = GearUp.shortOfU) - null = it can. Nothing is moved.
M(ghop, r"""
public static String why(@INV@ inv, java.util.UUID u, @IS@ x) {
  Object[] c = @PKG@.GearUp.check(x, u);
  if (c == null) return "The item moved - click Refresh.";
  if (c[0] != null) return (String) c[0];
  return @PKG@.GearUp.shortOfU(inv, u, (Object[]) c[2]);
}""")
# the player's piece of item id `id` in the inventory that can tier up NOW: int[] { section, slot }, or null (then W[0] = why the first one
# cannot; null = there is none). A failing piece is never returned.
M(ghop, r"""
public static int[] find(@INV@ inv, java.util.UUID u, String id, String[] W) {
  if (inv == null || id == null) return null;
  java.util.ArrayList rs = @PKG@.GearUp.rows(inv);
  for (int i = 0; i < rs.size(); i++) {
    int[] a = (int[]) rs.get(i);
    @IS@ x = @PKG@.GearStamp.at(inv, a[0], a[1]);
    if (x == null || x.isEmpty() || !id.equals(x.getItemId())) continue;
    String w = why(inv, u, x);
    if (w == null) return a;
    if (W != null && W[0] == null) W[0] = w;
  }
  return null;
}""")
# the set page's UPGRADE (Skyy 2026-10-16 "just change to the anvil to upgrade"): the piece `out` from its previous tier, with the Anvil's own
# tier-up (GearUp.upgrade: check, cost from inventory + bags, skill gate, counts before / after, log, sound). Which previous-tier piece: one
# in the inventory that passes every check; else one in Requip that passes them (its own document checked, the cost counted FIRST) is taken
# out (wardrobe:fn:fetch = the Anvil's Take out) and tiered up. Refused = nothing moves. "+..." done, "-..." refused, "=..." taken out only.
M(ghop, r"""
public static String upPiece(@INV@ inv, java.util.UUID u, @PR@ pr, String out) {
  boolean took = false;
  String p = null;
  try {
    if (!@PKG@.GearCfg.UP_ON) { N[3] = N[3] + 1L; return "-Tiering up is switched off on this server."; }
    if (inv == null) { N[3] = N[3] + 1L; return "-Your inventory cannot be read right now - nothing changed."; }
    p = @PKG@.GearSmith.prevOf(out);
    if (p == null) { N[3] = N[3] + 1L; return "-" + @PKG@.Gear.itemName(out) + " is not made from another piece."; }
    String nx = @PKG@.GearUp.next(p);
    if (nx == null || !nx.equals(out)) { N[3] = N[3] + 1L; return "-" + @PKG@.Gear.itemName(p) + " does not tier up into " + @PKG@.Gear.itemName(out) + "."; }
    String[] W = new String[1];
    int[] at = find(inv, u, p, W);
    if (at == null) {
      java.util.ArrayList rq = null;
      try { rq = @PKG@.ReforgePage.rqRows(u, 1); } catch (Throwable t1) { rq = null; }
      Object[] hit = null;
      boolean any = false;
      for (int i = 0; rq != null && i < rq.size() && hit == null; i++) {
        Object[] e = (Object[]) rq.get(i);
        if (!p.equals(e[1])) continue;
        any = true;
        @IS@ v = new @IS@(p, 1);          // a look-alike of the stored piece (its own document): checked, never given
        if (e[2] instanceof @BD@) v = v.withMetadata(@PKG@.GearDefs.DOC_KEY, (@BV@) e[2]);
        String w = why(inv, u, v);
        if (w == null) hit = e;
        else if (W[0] == null) W[0] = w;
      }
      if (hit == null) {
        N[3] = N[3] + 1L;
        if (W[0] != null) return "-" + W[0] + (any ? " (nothing was taken out of Requip)" : "");
        return "-You have no " + @PKG@.Gear.itemName(p) + " on you or in Requip - make that one first.";
      }
      java.util.function.Function f = @PKG@.Gear.fn("wardrobe:fn:fetch");
      if (f == null) { N[3] = N[3] + 1L; return "-Your " + @PKG@.Gear.itemName(p) + " is in Requip, which is not loaded right now."; }
      Object res = null;
      try { res = f.apply(new Object[] { u, (String) hit[0] }); } catch (Throwable t2) { res = "Requip did not answer (" + t2 + ")"; }
      if (!"ok".equals(res)) { N[3] = N[3] + 1L; return "-" + (res == null ? "Requip did not answer." : String.valueOf(res)); }
      N[4] = N[4] + 1L;
      took = true;
      String[] W2 = new String[1];
      at = find(inv, u, p, W2);
      if (at == null) return "=Your " + @PKG@.Gear.itemName(p) + " was taken out of Requip and is in your inventory now" + (W2[0] != null ? " - " + W2[0] : " - click Upgrade again.");
    }
    @IS@ x = @PKG@.GearStamp.at(inv, at[0], at[1]);
    if (x == null || x.isEmpty()) { N[3] = N[3] + 1L; return "-The item moved - click Refresh."; }
    Object[] r = @PKG@.GearUp.upgrade(inv, at[0], at[1], x.getItemId(), @PKG@.GearForge.fp(x), u, pr == null ? "?" : pr.getUsername());
    if (((Integer) r[0]).intValue() == 1) {
      @BD@ d = (@BD@) r[3];
      String to = ((@IS@) r[2]).getItemId();
      N[2] = N[2] + 1L;
      return "+" + @PKG@.Gear.itemName(p) + " -> " + @PKG@.Gear.itemName(to) + " (" + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + ", Lv " + @PKG@.GearLevel.level(to, d) + ")!";
    }
    N[3] = N[3] + 1L;
    return "-" + (String) r[1] + (took ? " (it was taken out of Requip: it is in your inventory now)" : "");
  } catch (Throwable t) {
    N[5] = N[5] + 1L;
    @PKG@.Gear.warn("set page Upgrade failed: " + t);
    if (took) return "-Something went wrong - your " + @PKG@.Gear.itemName(p) + " was taken out of Requip and is in your inventory now; nothing else changed. Click Refresh.";
    return "-Something went wrong - nothing was changed. Click Refresh.";
  }
}""")
ghvis.addInterface(pool.get("java.util.function.Function"))
F(ghvis, "public int k;")
C(ghvis, "public GearHubVis(int k) { this.k = k; }")
M(ghvis, "public Object apply(Object o) { try { return @PKG@.GearHubOpen.shows(this.k) ? Boolean.TRUE : Boolean.FALSE; } catch (Throwable t) { return Boolean.FALSE; } }")
# start(): hub:tab:smithing:<tab> = { "SkyyGear", label, order, command, open, visible, "smithing_<tab>" } (HubBar.putIcon); shutdown: removeAll
M(ghop, r"""
public static int register() {
  int n = 0;
  for (int i = 0; i < TAB.length; i++) {
    Object[] e = null;
    if (TAB[i].equals("identify")) e = @PKG@.HubBar.putSub("smithing", TAB[i], "SkyyGear", LABEL[i], ORDER[i], CMD[i], new @PKG@.GearHubOpen(i), new @PKG@.HubHide("smithing", "reforge"), "smithing_" + TAB[i], "reforge");
    else e = @PKG@.HubBar.putIcon("smithing", TAB[i], "SkyyGear", LABEL[i], ORDER[i], CMD[i], new @PKG@.GearHubOpen(i), new @PKG@.GearHubVis(i), "smithing_" + TAB[i]);
    if (e != null) n = n + 1;
  }
  REG = n;
  return n;
}""")
M(ghop, r"""
public static String statusText() {
  return "Crafting hub: " + REG + " of " + TAB.length + " tabs put (Smithing / Anvil / Upgrade in the strip, Identify inside the Anvil; big hub row on every Smithing page; bars drawn " + @PKG@.GearHub.N[0] + ", hub clicks " + @PKG@.GearHub.N[1] + ", tab opens " + N[0] + ", set-page upgrades " + N[2] + ")";
}""")
# ---- the set page's Upgrade click (tup:<row>:<token>) - the craft guard first (token, pace, profile)
M(spg, r"""
public boolean tupClick(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.Gear.jsonStr(data, "a");
  if (!a.startsWith("tup:")) return false;
  java.util.UUID u = this.playerRef.getUuid();
  String[] ps = a.split(":");
  if (this.view != 1 || this.grp == null || ps.length < 3) { this.info = "-Open a set first."; rebuild(); return true; }
  String[] outs = (String[]) this.grp[1];
  int pi = -1;
  try { pi = Integer.parseInt(ps[1]); } catch (Throwable t1) { pi = -1; }
  if (pi < 0 || pi >= outs.length) { rebuild(); return true; }
  if (!ps[2].equals(String.valueOf(this.token))) { rebuild(); return true; }          // a repeat of a used click: nothing done, the last answer stays
  if (!guard(u, ps[2])) { rebuild(); return true; }
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t2) { p = null; }
  this.info = @PKG@.GearHubOpen.upPiece(p == null ? null : p.getInventory(), u, this.playerRef, outs[pi]);
  rebuild();
  return true;
}""")
_HUBCLICK = "{ String hr9 = null; try { hr9 = @PKG@.GearHub.route(this.playerRef, $3, @SEL@); } catch (Throwable th9) { hr9 = null; } if (hr9 != null) { if (hr9.equals(\"close\")) close(); else if (hr9.equals(\"self\")) rebuild(); return; } }"
spg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (tupClick($1, $2, $3)) return; }"))
for _pg, _sel in ((spg, "3"), (lpg, "4"), (upg, "6")):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J(_HUBCLICK.replace("@SEL@", _sel)))
# the Anvil page: Reforge <-> Identify switch in place (the old row's way), every other hub click through the bars
rpg.getDeclaredMethod("handleDataEvent").insertBefore(J(r"""{
  if (@PKG@.GearCfg.ANVIL_ON && $3 != null) {
    String ha9 = @PKG@.Gear.jsonStr($3, "a");
    if (ha9.equals("hub:identify") && !this.anIdM && @PKG@.GearAnvil.idTab()) { try { anEvent($1, $2, "{\"a\":\"mode:5\"}"); } catch (Throwable ta9) { @PKG@.Gear.warn("anvil: the Identify tab failed: " + ta9); } return; }
    if (ha9.equals("hub:reforge") && this.anIdM) { try { anEvent($1, $2, "{\"a\":\"mode:0\"}"); } catch (Throwable tb9) { @PKG@.Gear.warn("anvil: the Reforge tab failed: " + tb9); } return; }
    String hr9 = null;
    try { hr9 = @PKG@.GearHub.route(this.playerRef, $3, this.anIdM ? 5 : 0); } catch (Throwable th9) { hr9 = null; }
    if (hr9 != null) { if (hr9.equals("close")) close(); else if (hr9.equals("self")) rebuild(); return; }
  }
}"""))
# /upgrade = the Upgrade tab (the lifelong tools page) while lifelong tools are on (Skyy "tools can be rolled into upgrade"); off = 0.3.14
upc.getDeclaredMethod("execute").insertBefore(J("{ if (@PKG@.GearCfg.LL_ON) { new @PKG@.ToolPtsCmd().execute($1, $2, $3, $4, $5); return; } }"))
pl.getDeclaredMethod("start").insertAfter(J("""{
  try {
    @PKG@.GearHubOpen.register();
    @PKG@.Gear.info("[SkyyGear] 0.3.15: " + @PKG@.GearHubOpen.statusText());
  } catch (Throwable th5) { @PKG@.Gear.warn("0.3.15 Crafting hub tabs failed: " + th5); }
}"""))
pl.getDeclaredMethod("shutdown").insertBefore(J("{ try { @PKG@.HubBar.removeAll(); } catch (Throwable thr5) { } }"))
print("0.3.15 Crafting hub bars: HubBar (kit row + big row) / GearHub / GearHubOpen / GearHubVis; tabs %s; pages 1100 x 940; hooks on Smithing / Anvil / Tools / Upgrade clicks, /upgrade, start / shutdown"
      % ", ".join("%s %d" % (l, o) for _t, l, o, _c in G315_TABS))
'''
G315_LATE = G315_LATE.replace('@@NONE@@', '')
before('''from jpype import JClass as _JC10
''', G315_LATE)

# ================================================================================================================ the class list, the jar files
rep('''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES + G313_CLASSES + G314_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES + G313_CLASSES + G314_CLASSES + G315_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')
after('''EXTRA.update(BAG_ITEMS)          # 0.2.11: the 7 mystery bag items (new ids; the old 'no item file' build check is narrowed to them)
''', '''# 0.3.15: the Sky Window kit art (all 59, byte-identical in every hub jar - HUBS-CONTRACT 2.7) + the four Crafting-hub tab icon pairs at the
# kit 1.6 hook path (the same bytes SkyyMenu 0.3.30+ ships: whichever jar loads last, the picture is the same)
import hashlib as _hl315
_kit315 = SUI.kit_texture_files()
assert len(_kit315) == len(SUI.SKY_FILES) == 59 and all(p.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p for p in _kit315) and not set(_kit315) & set(EXTRA)
EXTRA.update(_kit315)
_TAM315 = json.load(open(os.path.join(HERE, "..", "art", "hub-tab-icons", "manifest.json"), encoding="utf8"))
G315_ICONS = []
for _t in [t for t, _l, _o, _c in G315_TABS]:
    _pp = SUI.hub_tab_icon_paths("smithing", _t)
    for _fn, _jp in (("smithing_%s.png" % _t, _pp[2]), ("smithing_%s_on.png" % _t, _pp[3])):
        _data = open(os.path.join(HERE, "..", "art", "hub-tab-icons", _fn), "rb").read()
        _me = [f for f in _TAM315["files"] if f["path"] == _fn]
        assert len(_me) == 1 and _hl315.sha256(_data).hexdigest() == _me[0]["sha256"] and len(_data) == _me[0]["bytes"], "0.3.15: %s = its manifest entry" % _fn
        assert _jp.startswith("Common/UI/Custom/SkyyHubTabs/") and _jp not in EXTRA
        EXTRA[_jp] = _data
        G315_ICONS.append(_jp)
print("0.3.15 kit art: %d Sky Window files + %d Crafting-hub tab icons" % (len(_kit315), len(G315_ICONS)))
''')
after('''B.assemble(jar, man, OUT, extra_files=EXTRA)
''', '''assert SUI.check_jar_kit(jar, need=("Primary", "Tertiary")) == 59, "0.3.15: the kit art in the jar"
with zipfile.ZipFile(jar) as _jz315:
    assert all(_jz315.read(_p) == EXTRA[_p] for _p in G315_ICONS), "0.3.15: the tab icons in the jar"
''')

# ================================================================================================================ checks on the result
assert s.index("ghub = mk(\"GearHub\")") < s.index("public static int tabs(@UCB@ b, @UEB@ ev, String parent, int sel, int w, String title)")
assert s.index("ghub = mk(\"GearHub\")") < s.index("@PKG@.GearHub.bars(b, ev, this.playerRef.getUuid(), 3);")
assert s.index('ghop = mk("GearHubOpen")') > s.index('M(gup, r"""\npublic static Object[] upgrade(') and s.index('ghop = mk("GearHubOpen")') < s.index("ANSWER_PAGES = [")
assert s.index('ghop = mk("GearHubOpen")') > s.index('C(tpc, r"""') and s.index('ghop = mk("GearHubOpen")') > s.index('M(upc, r"""')
assert s.count("@PKG@.GearHub.bars(") == 4 + 0 and s.count("GearUi.tabs(b, ev, \"#SkyyGBody\"") == 0, "every #SkyyGBody page draws the bars"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.14 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.14 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
