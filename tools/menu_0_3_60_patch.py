"""Derive SkyyMenu/build_skyymenu_0.3.60.py + SkyyMenu/test_skyymenu_0.3.60.py from the SET pin SkyyMenu 0.3.59 (generated - never re-run
its patch). Run:  python tools/menu_0_3_60_patch.py   then   python SkyyMenu/build_skyymenu_0.3.60.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.60.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.59 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.60 (2026-11-21, round menufix1) = THE MENU FIX ROUND from Skyy's 2026-11-21 test of the new screens (docs/answered/ui.md 2026-11-21 lines).
Skyy's words: "its a bit bugged, and the top bar still needs moved to the top of the screen."; "these skill icons should work as buttons to open
that page from here instead of an open button."; "and it wont detect my multitool"; "editing requip doesnt work in this menu. and when i clicked
storage, there was no back button. and i couldnt really do anything in there."; "crafting doesnt work at all."; "for the charms id like to keep it
more like this, instead of that crating menu style, but keep it small compact and in the inventory."; "i cant select anything" (Void pocket);
"and the numbers cap at 100 even though there is more than that. could you fix that too?"; "game is closed, deploy as ready".
  ROOT CAUSE of "crafting doesnt work", "i cant select anything", "editing requip doesnt work" and "couldnt really do anything" (Storage): every
  click-only grid of the new screens (recipes, pocket items, Requip preset slots + storage, charms, teleports, furnace list, skill icons, pets,
  market rows) was filled with ItemGridSlots whose isActivatable stayed FALSE (the engine default). The client sends a SlotClicking event only
  for an activatable slot - the old SkyWynn Menu grid sets it per tile (MenuPage.put: setActivatable(act != null); its filler false), so its
  clicks always worked; the inventory's own bag / hotbar slots set it too (InvPage.slot). The server code behind every one of those clicks was
  there and harness-tested since 0.3.52 - the client simply never sent the click. (The 18-04 server log of that session has no inventory
  warning at all - consistent: no event ever arrived.) FIX: InvPage.act(list) marks every slot of a click grid activatable; every grid of the
  inventory / skill page / pets / market screens goes through it (the drop zone #SkyyInvDz stays inert).
  1. TOP BAR: the 7-tab bar (coins, Full page, X) leaves the window and sits at the very top of the page (y = 0) on all four new screens
     (Inventory, Skills, Pets, Market) as its own Skyglass strip; the window starts under it (same body size, nothing else moves). The page root
     keeps Width / Height only (HANDOFF 2) - the game centres the page; at 1080p the bar is the page's top edge.
  3. SKILLS CARD: no 'Open' button; every skill tile is the button - the icon (now activatable) AND the "Lv N" text (a transparent tab-style
     TextButton) open that skill's page (skc:<n>).
  4. TOOL CARD: the Mining tool list also takes a multitool (Tool_Hatchet_Pickaxe_Multitool_* - IBC Multitools and SkyyGear's zone-metal /
     lifelong multitools all use that id); Foraging already matched it (Tool_Hatchet_), the Harvester is a Tool_Sickle_ (Farming).
  5. FORTUNE: perk.doubleDropMax 0 = NO cap (SkyySkills 0.4.53+, its default) - the Stats page / skill page showed "(max 0%)" and 0 %; now the
     real total (level perk + trees) and a cap only when an admin set one above 0. The REAL drops were never capped (SkyySkills Perks.fortune:
     DD_MAX 0 = no cap; Mining's tree part uncapped) - display only.
  6. REQUIP: the preset slots (click = pick for Keep slot, drop = save) and the storage strip / full storage grid are activatable now; the
     full storage's 'Show preset' is a clear primary 'Done' (back to the preset).
  7. CRAFTING: the recipe grid is activatable - picking a recipe works, so Craft / x10 / All have a recipe (the craft code is unchanged).
  9. VOID POCKET: the item grid is activatable - a click selects the item (Withdraw / Deposit / Sell / Unpack act on it).
 10. VOID POCKET COUNTS: the icon carries the REAL amount (was capped at the item's stack size, 100); the exact number stays in the tooltip.
 11. IMAGES: the red / white edges = the client UI texture atlas overflowing (client log 2026-11-21 18-03-46: 912 "Texture atlas rejected
     image", incl. SkyyGlass/Clear.png + SkyyGlass/Separator.png). The new screens no longer use either: the full-page drop zone draws with the
     fully clear Tab picture (already used by every tab), the separator strips are gone (the bar is its own strip now); the jar ships ONLY the
     Skyglass pictures its pages name (the unused ones - rarity frames no page draws, Clear, Separator - are left out). The pack-wide fix is
     round atlas1 (SkyyTrees 0.6.9 + tools/ci/ui_budget.py).
  Every bound click still answers with exactly ONE page packet; grid copies stay NEW ItemStacks without metadata behind known(id); no Top /
  Bottom alignment; inline pages only; never setPageWithWindows.
  NOT IN THIS VERSION (left exactly as 0.3.59, reported): 2. the skill tree INLINE on the skill page (needs a SkyyTrees read + learn bridge -
  built on the pinned SkyyTrees 0.6.9 as its own full round - SkyyTrees 0.6.10 tree:fn:map + tree:fn:act, then SkyyMenu draws the map; the
  'Open tree' button stays until then).
  Fix pass (menufix1 critics): the charm rows' probe answer is reused by the first fill (one vc:rows read per open, not two).
  No new command, setting, lang key, system or saved data. ROLLBACK to 0.3.59: safe alone (nothing saved).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.59.py"), os.path.join(MOD, "build_skyymenu_0.3.60.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.59.py"), os.path.join(MOD, "test_skyymenu_0.3.60.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.59"\n') and P.has("tools/menu_0_3_59_patch.py") and P.has("MarketTab")
assert not P.has("public static java.util.ArrayList act("), "not the generated SkyyMenu 0.3.59 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.59: THE MARKET TAB''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.60: MENU FIX ROUND (Skyy's 11-21 test): every click grid of the new screens is ACTIVATABLE (the client never sent their clicks - recipes,
       pocket items, Requip slots + storage, charms, teleports, skill icons ...), the 7-tab bar at the very top of the page (own strip), the
       SKILLS card tiles are the buttons (no Open), multitools count as the Mining tool, Fortune uncapped when doubleDropMax is 0, the Void
       pocket shows the real amounts, Requip storage 'Done' = back, no SkyyGlass Clear / Separator pictures and only the Skyglass pictures the
       pages use (notes: tools/menu_0_3_60_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.60.py.
0.3.59: THE MARKET TAB''')
P.rep('VERSION = "0.3.59"\n', 'VERSION = "0.3.60"\n')

# ---------- (1) THE TOP BAR at the very top of the page (its own strip; the window below it)
P.rep('''IV_BODY_H = IV_WIN_H - 2 * IV_PAD - IV_TOP_H - 14 - 6 - IV_HINT_H   # 844
''', '''IV_BODY_H = IV_WIN_H - 2 * IV_PAD - IV_TOP_H - 14 - 6 - IV_HINT_H   # 844
# 0.3.60 (Skyy 11-21 "the top bar still needs moved to the top of the screen"): the 7-tab bar is its own strip at the page's top edge (y = 0)
# and the window starts under it - the body keeps its size (the separator strip is gone: 48 + 14 out of the window, 4 between bar and window)
IV_BAR_TOP, IV_FRAME_TOP = 0, IV_TOP_H + 4
IV_FRAME_H = IV_WIN_H - IV_TOP_H - 14
assert IV_FRAME_TOP + IV_FRAME_H <= IV_PAGE_H and IV_FRAME_H == 2 * IV_PAD + IV_BODY_H + 6 + IV_HINT_H, "0.3.60: bar + window fit the page"


def iv_bar(G_, parent, ident):
    """0.3.60: the top bar strip at the very top of the page (IV_W wide, the window's inner width inside)"""
    return (parent, G_.glass_group(ident, IV_W, IV_TOP_H, role="panel", layout="Left", pad={"horizontal": IV_PAD},
                                   anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": IV_BAR_TOP}))
''')
# the inventory screen
P.rep('''    used = IV_TOP_H + 14 + IV_BODY_H + 6 + IV_HINT_H
    ivh = used + 2 * IV_PAD
    assert ivh == IV_WIN_H and ivh <= IV_PAGE_H, ivh
    win = IV + "Win"
    ap.append(("#" + IV, G_.glass_group(win, IV_W, ivh, role="frame", layout="Top", pad=IV_PAD,
                                          anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": (IV_PAGE_H - ivh) // 2})))
    # ---- row 1 (the TOP of the screen): the 7 tabs, coins, the X
    top = IV + "Top"
    ap.append(("#" + win, G_.glass_group(top, IV_IW, IV_TOP_H, layout="Left")))
''', '''    used = IV_BODY_H + 6 + IV_HINT_H
    ivh = used + 2 * IV_PAD
    assert ivh == IV_FRAME_H and IV_FRAME_TOP + ivh <= IV_PAGE_H, ivh   # 0.3.60: the window under the top bar
    win = IV + "Win"
    ap.append(("#" + IV, G_.glass_group(win, IV_W, ivh, role="frame", layout="Top", pad=IV_PAD,
                                          anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": IV_FRAME_TOP})))
    # ---- row 1 (0.3.60: the VERY TOP of the page, its own strip): the 7 tabs, coins, the X
    top = IV + "Top"
    ap.append(iv_bar(G_, "#" + IV, top))
''')
P.rep('''    ap.append(("#" + top, G_.glass_button(IV + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    ap.append(("#" + win, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }'
               % (IV, IV_IW, G_.glass_path("Separator"))))
''', '''    ap.append(("#" + top, G_.glass_button(IV + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
''')
# the skill page, the pets screen, the market screen: the same bar
for _pfx, _sel in (("SK", "Skills selected"), ("PT", "Pets selected"), ("MT", "Market selected")):
    P.rep('''    ap.append(("#" + %s, G_.glass_group(win, IV_W, IV_WIN_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": (IV_PAGE_H - IV_WIN_H) // 2})))
''' % _pfx, '''    ap.append(("#" + %s, G_.glass_group(win, IV_W, IV_FRAME_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": IV_FRAME_TOP})))   # 0.3.60: under the top bar
''' % _pfx)
    P.rep('''    top = %s + "Top"
    ap.append(("#" + win, G_.glass_group(top, IV_IW, IV_TOP_H, layout="Left")))
''' % _pfx, '''    top = %s + "Top"
    ap.append(iv_bar(G_, "#" + %s, top))   # 0.3.60: the very top of the page
''' % (_pfx, _pfx))
    P.rep('''    ap.append(("#" + win, 'Group #%%sSep { Anchor: (Width: %%d, Height: 2, Top: 6, Bottom: 6); Background: "%%s"; }' %% (%s, IV_IW, G_.glass_path("Separator"))))
''' % _pfx, '''    # 0.3.60: no separator strip under the %s bar (the bar is its own strip; no SkyyGlass/Separator picture)
''' % _pfx)

# ---------- (11) the drop zone without SkyyGlass/Clear (the fully clear Tab picture every tab already uses)
P.rep('''               % (IV, IV_PAGE_W, IV_PAGE_H, IV_PAGE_W, G_.glass_path("Clear"))))''',
      '''               % (IV, IV_PAGE_W, IV_PAGE_H, IV_PAGE_W, G_.glass_path("Tab"))))   # 0.3.60: no SkyyGlass/Clear (atlas)''')

# ---------- (3) THE SKILLS CARD: no Open button; the tile's "Lv N" is a transparent tab-style button, the icon is activatable (both skc:<n>)
P.rep('''    ap.append(("#" + sh, lab(IV + "SkH", "SKILLS", 15, "accentHi", bold=True, w=riw - 90, h=26)))
    ap.append(("#" + sh, G_.glass_button(IV + "SkBtn", "Open", "secondary", w=90, h=26, size=13)))
''', '''    ap.append(("#" + sh, lab(IV + "SkH", "SKILLS - click a skill", 15, "accentHi", bold=True, w=riw, h=26)))   # 0.3.60: no Open button
''')
P.rep('''            ap.append(("#" + sx_, lab(IV + "Sk%d" % k_, "", 13, "text", bold=True, w=IV_SKBW, h=24)))
''', '''            ap.append(("#" + sx_, G_.glass_button(IV + "Sk%d" % k_, "", "tab", w=IV_SKBW, h=24, size=13)))   # 0.3.60: the tile is the button
''')
P.rep('''        ("#" + IV + "Sum", "sum"), ("#" + IV + "SkBtn", "tab:1"), ("#" + IV + "NowBtn", "nowq"), ("#" + IV + "TpE", "tpe")]   # 0.3.55: + teleport Edit
''', '''        ("#" + IV + "Sum", "sum"), ("#" + IV + "NowBtn", "nowq"), ("#" + IV + "TpE", "tpe")] + [   # 0.3.55: + teleport Edit
        ("#%sSk%d" % (IV, k_), "skc:%d" % k_) for k_ in range(IV_SKN)]   # 0.3.60: a skill tile's Lv button = that skill's page (no Open)
''')

# ---------- (6) the full Requip storage: a clear Back
P.rep('''    ap.append(("#" + qa, G_.glass_button(IV + "QB", "Show preset", "secondary", w=120, h=32, size=13, anchor={"left": 6})))''',
      '''    ap.append(("#" + qa, G_.glass_button(IV + "QB", "Done", "primary", w=120, h=32, size=13, anchor={"left": 6})))   # 0.3.60 (Skyy: "no back button")''')

# ---------- (4) THE TOOL CARD: a multitool is a Mining tool too (Foraging's Tool_Hatchet_ already matched it)
P.rep('''SK_SKILLS = [("Combat", "Weapon_", "Class", True), ("Mining", "Tool_Pickaxe_", "Mining", True), ("Foraging", "Tool_Hatchet_", "Foraging", True),''',
      '''SK_SKILLS = [("Combat", "Weapon_", "Class", True), ("Mining", "Tool_Pickaxe_,Tool_Hatchet_Pickaxe_Multitool_", "Mining", True), ("Foraging", "Tool_Hatchet_", "Foraging", True),''')

# ---------- (5) FORTUNE: perk.doubleDropMax 0 = no cap (SkyySkills 0.4.53+); a cap only above 0
P.rep('''  double max = cfgNum("SkyySkills", "perk.doubleDropMax", 1.0);
  if (max > 1.0) max = 1.0;
  if (max < 0.0) max = 0.0;
  double perk = lvl * rate;
  double tot = perk + tree;
  if (tot > max) tot = max;
  if (tot < 0.0) tot = 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, FORT_N[i] + " level " + (int) lvl, perk * 100.0, "%");
  part(sb, "Skill trees", tree * 100.0, "%");
  if (perk + tree > max) sb.append(" (max ").append(num(max * 100.0)).append("%)");''', '''  double max = cfgNum("SkyySkills", "perk.doubleDropMax", 0.0);   // 0.3.60: 0 = NO cap (SkyySkills 0.4.53+ default; Perks.chanceU)
  boolean capped = max > 0.0;
  double perk = lvl * rate;
  double tot = perk + tree;
  if (capped && tot > max) tot = max;
  if (tot < 0.0) tot = 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, FORT_N[i] + " level " + (int) lvl, perk * 100.0, "%");
  part(sb, "Skill trees", tree * 100.0, "%");
  if (capped && perk + tree > max) sb.append(" (max ").append(num(max * 100.0)).append("%)");''')

# ---------- (7) (9) (6) ... THE ROOT CAUSE: every click grid's slots activatable (the client sends SlotClicking only for those)
P.rep('''public static @IGS@ slot(@IS@ s) {
  @IGS@ g = new @IGS@();
  g.setActivatable(true);''', '''public static @IGS@ slot(@IS@ s) {
  @IGS@ g = new @IGS@();
  g.setActivatable(true);   // (0.3.60: what act() now does for every click grid)''')
P.rep('''# ---- MenuPage helpers (callees first)''', '''# ---- MenuPage helpers (callees first)
# 0.3.60 THE ROOT CAUSE of Skyy's 11-21 "crafting doesnt work at all" / "i cant select anything": the client sends SlotClicking only for an
# ACTIVATABLE ItemGridSlot (MenuPage.put sets it per tile, its fillers false); the new screens' click grids never set it. act() marks every
# slot of a list activatable - every click grid of the inventory / skill page / pets / market screens goes through it.''')
_ACT = '''M(ipg, r"""
public static java.util.ArrayList act(java.util.ArrayList l) {
  for (int i = 0; l != null && i < l.size(); i++) {
    Object o = l.get(i);
    if (o instanceof @IGS@) ((@IGS@) o).setActivatable(true);
  }
  ACTS = ACTS + 1;
  return l;
}""")
'''
P.rep('''# HANDOFF 2: the grid copy carries NO metadata AND no quality override''', '''F(ipg, "public static volatile int ACTS = 0;")   # 0.3.60: lists made activatable (the harness counts them)
''' + _ACT + '''# HANDOFF 2: the grid copy carries NO metadata AND no quality override''')
_WRAP = [
    '  b.set("#SkyyInv" + k + "I.Slots", sl);',
    '  b.set("#SkyyInvVc.Slots", vs);',
    '  b.set("#SkyyInvCo.Slots", os);',
    '  b.set("#SkyyInvCn.Slots", ns);',
    '  b.set("#SkyyInvCg.Slots", sl);',
    '  b.set("#SkyyInvRa.Slots", ra);',
    '  b.set("#SkyyInvRh.Slots", rh);',
    '  b.set("#SkyyInvRs.Slots", rs);',
    '  b.set("#SkyyInvQg.Slots", sl);',
    '  b.set("#SkyyInvPg.Slots", sl);',
    '  b.set("#SkyyInvPsl.Slots", one);',
    '  b.set("#SkyyInvVxG.Slots", sl);',
    '  b.set("#SkyyInvVxS.Slots", one);',
    '  b.set("#SkyyInvTp.Slots", tp);',
    '  b.set("#SkyyInvTxG.Slots", sl);',
    '      b.set("#SkyyInvSkI" + i + ".Slots", sl);',
    '  b.set("#SkyyInvFxG.Slots", gl);',
    '  b.set("#SkyyInvFxO.Slots", og);',
    '  b.set("#SkyyInvFxF.Slots", fg);',
    '    b.set("#SkyySkpCi" + i + ".Slots", sl);',
    '  b.set("#SkyySkpHdI.Slots", sl);',
    '  b.set("#SkyySkpGaI.Slots", ar);',
    '  b.set("#SkyySkpGtI.Slots", tl);',
    '    b.set("#SkyySkpZg" + z + ".Slots", sl);',
    '  b.set("#SkyySkpShI.Slots", sl);',
    '  b.set("#SkyyPtabG.Slots", sl);',
    '  b.set("#SkyyPtabFG.Slots", sl);',
    '  b.set("#SkyyPtabE.Slots", sl);',
]
for _w in _WRAP:
    _m = re.match(r'(\s*b\.set\("[^)]*?\.Slots", )([A-Za-z]+)\);$', _w)
    assert _m, _w
    P.rep(_w + "\n", _m.group(1) + "@PKG@.InvPage.act(" + _m.group(2) + "));\n")
# the one-cell helpers of the pets / market screens: their single slot activatable too
for _w in ('    b.set("#" + q + "I.Slots", one(on ? cell(f[7], 1, f[3] + " - Lv " + f[5], dec(f[10])) : new @IGS@()));',
           '  b.set("#SkyyPtabSI.Slots", one(on ? cell(d[8], 1, d[2] + " - Lv " + d[4], dec(d[14])) : new @IGS@()));',
           '  b.set("#SkyyPtabFR.Slots", one(on && fr != null && fr.length >= 3 && f[3].length() > 0 ? cell(fr[1], 1, f[3], "") : new @IGS@()));',
           '    b.set("#" + r + "I.Slots", one(egg ? cell(f[3], 1, f[4], f[9]) : new @IGS@()));',
           '    b.set("#" + r + "I.Slots", one(cell(f[1], 1, f[2], tip(f[2], rar(f[3]), f[4], by, sl, hv, "Click: select it"))));',
           '  b.set("#SkyyMtabSI.Slots", one(on ? cell(d[1], 1, d[2], tip(d[2], rar(d[3]), d[4], b1, s1, hv, "")) : new @IGS@()));'):
    _i = _w.index(".Slots\", ") + len(".Slots\", ")
    P.rep(_w + "\n", _w[:_i] + "@PKG@.InvPage.act(" + _w[_i:-2] + "));\n")
P.rep('''    b.set("#" + a + "I.Slots", one(cell(id, 1, nm, col(@PKG@.MarketTabData.SOFT, nm)''', '''    b.set("#" + a + "I.Slots", @PKG@.InvPage.act(one(cell(id, 1, nm, col(@PKG@.MarketTabData.SOFT, nm)''')
P.rep('''col(@PKG@.MarketTabData.FOOT, "Open: the Auction House on it"))));''', '''col(@PKG@.MarketTabData.FOOT, "Open: the Auction House on it")))));''')

# ---------- (10) the Void pocket icons carry the REAL amount (was capped at the stack size)
P.rep('''        int ms = @PKG@.InvCraft.maxStack(f[0]);   // the icon number tops out at a full stack (no probe yet for bigger ones); the exact count is in the name + the detail
        if (known(f[0])) g.setItemStack(new @IS@(f[0], (int) (c > (long) ms ? (long) ms : (c < 1L ? 1L : c))));''', '''        // 0.3.60 (Skyy 11-21 "the numbers cap at 100 even though there is more than that"): the REAL amount on the icon (was capped at the
        // stack size); a copy without metadata, the exact number also in the name
        if (known(f[0])) g.setItemStack(new @IS@(f[0], (int) (c > 2000000000L ? 2000000000L : (c < 1L ? 1L : c))));''')

# ---------- (11) ship only the Skyglass pictures the built classes name (the atlas: fewer pictures; no Clear / Separator any more)
P.rep('''files.update(IV_GLASS_FILES)
print("0.3.50 Skyglass textures:", len(IV_GLASS_FILES), "files under Common/UI/Custom/SkyyGlass/ (%d bytes)" % sum(len(v) for v in IV_GLASS_FILES.values()))''',
      '''# 0.3.60 (the client UI atlas overflowed - 11-21 "red / white edges"): only the Skyglass pictures some built class names (scan of every class
# file under OUT for "SkyyGlass/<Name>.png"); Clear + Separator are named by none any more
_used_glass = set()
for _dp, _dn, _fn in os.walk(OUT):
    for _f in _fn:
        if _f.endswith(".class"):
            _used_glass.update(m_.decode("ascii") for m_ in re.findall(rb"SkyyGlass/([A-Za-z0-9]+)\\.png", open(os.path.join(_dp, _f), "rb").read()))
assert {"Window", "Panel", "Slot", "Tab", "TabSelected", "Primary", "Secondary", "Close"} <= _used_glass, ("0.3.60: the class scan found the theme", sorted(_used_glass))
assert not ({"Clear", "Separator"} & _used_glass), ("0.3.60: no page names SkyyGlass/Clear or Separator", sorted(_used_glass))
IV_GLASS_SHIP = dict((k_, v_) for k_, v_ in IV_GLASS_FILES.items() if k_.rsplit("/", 1)[1].replace("@2x.png", "") in _used_glass)
assert len(IV_GLASS_SHIP) == len(_used_glass), ("0.3.60: every named Skyglass picture is shipped", sorted(_used_glass))
files.update(IV_GLASS_SHIP)
print("0.3.60 Skyglass textures:", len(IV_GLASS_SHIP), "of", len(IV_GLASS_FILES), "files under Common/UI/Custom/SkyyGlass/ (%d bytes) - left out: %s"
      % (sum(len(v) for v in IV_GLASS_SHIP.values()), ", ".join(sorted(k_.rsplit("/", 1)[1] for k_ in IV_GLASS_FILES if k_ not in IV_GLASS_SHIP))))''')

# ---------- (8) THE VOID CHARMS PANEL AS ROWS ('w'; Skyy 11-21 "keep it more like this, instead of that crating menu style, but keep it small
# compact and in the inventory"): one compact row per accessory line like the old Void Charms -> CRAFT tab (icon, rarity-coloured name, status +
# cost, Craft / Upgrade), Benches / Combat / Gathering, 5 a page - SkyyAccessories 0.5.38 vc:rows / vc:craft (the Craft tab's own rows and button).
# Without 0.5.38 (vc:rows unknown) the 0.3.59 charm grid panel 'v' stays.
P.rep('''IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), []), "v": (SUI.Appends(), []),   # 0.3.54: + 'v' Charms
''', '''IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), []), "v": (SUI.Appends(), []),   # 0.3.54: + 'v' Charms
             "w": (SUI.Appends(), []),   # 0.3.60: + 'w' the charm ROWS (SkyyAccessories 0.5.38)
''')
P.rep('''_inv_charms()
''', '''_inv_charms()
IV_WRN, IV_WRH, IV_WIS = 5, 40, 36     # 0.3.60: the charm rows - rows a page, row height, icon cell
IV_WF_BTN = "TextButton #SkyyInvWf{I} { Anchor: (Width: 104, Height: 30, Right: 4); {S} }"
IV_TXT["wHelp"] = "Craft or upgrade a charm here - it goes straight into Void Charms. Bag = the full Void Charms page."


def _inv_charm_rows():
    """0.3.60: the charm ROWS panel 'w' (the old Void Charms CRAFT tab, small): header (sub tabs at run time, count, pages, Bag, Done),
    IV_WRN rows (icon, rarity-coloured name, status + cost in green when it can be made now, Craft / Upgrade), the answer line"""
    G_ = SUI
    lab = G_.glass_label
    ph = IV_CRAFT_H[0]
    pw = IV_COL_M - 20
    TP = "#" + IV + "TopP"
    ap, binds = IV_PANELS["w"]
    pan = IV + "WxPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    wa = IV + "WxA"
    ap.append(("#" + pan, G_.glass_group(wa, pw, 32, layout="Left")))
    ap.append(("#" + wa, G_.glass_group(IV + "WfB", 3 * 108, 32, layout="Left")))
    ap.append(("#" + wa, lab(IV + "WxI", "", 12, "gold", w=110, h=30, anchor={"left": 4})))
    sp = pw - 3 * 108 - 4 - 110 - 32 - 50 - 32 - 6 - 60 - 6 - 64
    assert sp >= 0, ("0.3.60: the charm rows header fits", sp)
    ap.append(("#" + wa, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + wa, G_.glass_button(IV + "WxPp", "<", "secondary", w=32, h=30, size=14)))
    ap.append(("#" + wa, lab(IV + "WxPn", "", 12, "text", bold=True, w=50, h=30, halign="Center")))
    ap.append(("#" + wa, G_.glass_button(IV + "WxPx", ">", "secondary", w=32, h=30, size=14)))
    ap.append(("#" + wa, G_.glass_button(IV + "WxB", "Bag", "secondary", w=60, h=30, size=13, anchor={"left": 6})))
    ap.append(("#" + wa, G_.glass_button(IV + "WxD", "Done", "secondary", w=64, h=30, size=13, anchor={"left": 6})))
    bw = 96
    tw = pw - 8 - IV_WIS - 6 - bw - 6
    for i in range(IV_WRN):
        rw = IV + "Wr%d" % i
        ap.append(("#" + pan, G_.glass_group(rw, pw, IV_WRH, role="inset", layout="Left", pad={"horizontal": 4}, anchor={"top": 3})))
        ap.append(("#" + rw, G_.glass_grid(IV + "Wi%d" % i, 1, 1, drag=False, slot=IV_WIS, icon=IV_WIS - 8, anchor={"top": (IV_WRH - IV_WIS) // 2})))
        tx = IV + "Wt%d" % i
        ap.append(("#" + rw, G_.glass_group(tx, tw, IV_WRH, layout="Top", anchor={"left": 6})))
        # the name in its rarity colour: one label per rarity (keep_holder, the 0.3.54 VxN way); v0 = no rarity
        nmv = [SUI.keep_at0(lab(IV + "Wn%dv%d" % (i, k_), "", 13, "title" if k_ == 0 else SUI.RARITY[IV_VRAR[k_ - 1]], bold=True, w=tw, h=20))
               for k_ in range(len(IV_VRAR) + 1)]
        hm_, kids_ = SUI.keep_holder(IV + "Wn%dH" % i, tw, 20, nmv)
        ap.append(("#" + tx, hm_))
        ap.extend(kids_)
        # status + cost: dim when it cannot be made now, green when it can
        stv = [SUI.keep_at0(lab(IV + "Ws%dv%d" % (i, k_), "", 11, "dim" if k_ == 0 else "green", w=tw, h=18)) for k_ in range(2)]
        hs_, kids2_ = SUI.keep_holder(IV + "Ws%dH" % i, tw, 18, stv)
        ap.append(("#" + tx, hs_))
        ap.extend(kids2_)
        ap.append(("#" + rw, G_.glass_button(IV + "Wb%d" % i, "Craft", "primary", w=bw, h=30, size=13, anchor={"left": 6, "top": (IV_WRH - 30) // 2})))
        binds.append(("#" + IV + "Wb%d" % i, "vr:%d" % i))
    used = 20 + 32 + IV_WRN * (IV_WRH + 3) + 4 + 16
    assert used <= ph, ("0.3.60: the charm rows panel fits the craft panel's height", used, ph)
    ap.append(("#" + pan, lab(IV + "WxM", "", 11, "text", w=pw, h=16, anchor={"top": 4})))
    binds.extend([("#" + IV + "WxPp", "vpp"), ("#" + IV + "WxPx", "vpn"), ("#" + IV + "WxB", "vbag"), ("#" + IV + "WxD", "vcd")])
    SUI.check_markup(IV_WF_BTN.replace("{I}", "0").replace("{S}", IV_ST_TABSEL), prefix=IV, kit_paths=True)


_inv_charm_rows()
''')
P.rep('''for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p", "v", "t", "f")]:''',
      '''for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p", "v", "t", "f", "w")]:   # 0.3.60: + w''')
P.rep('''F(idat, "public static final String VC_HELP = %s;" % jstr(IV_TXT["vcHelp"]))
''', '''F(idat, "public static final String VC_HELP = %s;" % jstr(IV_TXT["vcHelp"]))
F(idat, "public static final int WRN = %d;" % IV_WRN)                       # 0.3.60: the charm rows panel
F(idat, "public static final String WF_BTN = %s;" % jstr(IV_WF_BTN))
F(idat, "public static final String W_HELP = %s;" % jstr(IV_TXT["wHelp"]))
''')
P.rep('''           "public String vkey;", "public String[] vshown;",
''', '''           "public String vkey;", "public String[] vshown;",
           # 0.3.60: the charm rows - the sub tab (0 Benches, 1 Combat, 2 Gathering) and "recipe id|name" of every row drawn (null = no button)
           "public int vsub;", "public String[] vrows;",
           "public String vprobe;",   # 0.3.60: charmRowsOk's vc:rows answer, used once by the next fillCharmRows
''')
# the panel choice: 'v' becomes the rows panel 'w' while SkyyAccessories answers vc:rows (0.5.38+); 'v' stays the 0.3.59 grid otherwise
P.rep('''  char pm = this.mode.length() > 0 ? this.mode.charAt(0) : 'c';
''', '''  if ("v".equals(this.mode) && charmRowsOk()) this.mode = "w";   // 0.3.60: the charm ROWS (SkyyAccessories 0.5.38), else the 0.3.59 grid
  char pm = this.mode.length() > 0 ? this.mode.charAt(0) : 'c';
''')
P.rep('''  else if (pm == 'v') { try { fillCharms(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Charms panel failed: " + t); } }
''', '''  else if (pm == 'v') { try { fillCharms(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Charms panel failed: " + t); } }
  else if (pm == 'w') { try { fillCharmRows(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the charm rows failed: " + t); } }
''')
P.rep('''    if (a.equals("vc")) { openCharms(); return; }
''', '''    if (a.equals("vc")) { openCharms(); return; }
    if (a.startsWith("vf:")) { int k = toInt(a.substring(3), 0); this.vsub = k < 0 || k > 2 ? 0 : k; this.vpage = 0; this.vnote = ""; redraw(); return; }   // 0.3.60
    if (a.startsWith("vr:")) { charmRow(toInt(a.substring(3), -1)); return; }   // 0.3.60: a row's Craft / Upgrade
    if (a.equals("vbag")) { openHub("character", "accessories", "Void Charms"); return; }   // 0.3.60: the full Void Charms page
''')
P.rep('''# ---- 0.3.55: THE TELEPORT ROW (the profile's saved keys) + the Teleports panel's list (world thread; reads only)
''', '''# ---- 0.3.60: THE CHARM ROWS ('w'): acc:fn:charms vc:rows (SkyyAccessories 0.5.38) = the Craft tab's rows; vc:craft = its button (before build)
M(ipg, r"""
public boolean charmRowsOk() {
  if (this.vsub < 0 || this.vsub > 2) this.vsub = 0;
  Object o = call("acc:fn:charms", new Object[] { "vc:rows", this.playerRef.getUuid(), "", String.valueOf(this.vsub) });
  boolean ok = o instanceof String && !((String) o).startsWith("-");
  this.vprobe = ok ? (String) o : null;   // the panel's first fill reuses this answer (one vc:rows read per open, not two)
  return ok;
}""")
M(ipg, r"""
public void fillCharmRows(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  if (this.vsub < 0 || this.vsub > 2) this.vsub = 0;
  String[] ls = this.vprobe != null ? this.vprobe.split("\\n") : lines("acc:fn:charms", new Object[] { "vc:rows", u, "", String.valueOf(this.vsub) });
  this.vprobe = null;
  String err = null;
  String[] names = new String[] { "Benches", "Combat", "Gathering" };
  java.util.ArrayList rows = new java.util.ArrayList();
  if (ls == null) err = "Void Charms is not on this server right now";
  else if (!ls[0].startsWith("ok|")) err = ls[0].startsWith("off|") ? ls[0].substring(4) : bare(ls[0]);
  else {
    String[] h = ls[0].split("\\\\|", -1);
    String tk = h.length > 3 ? h[3] : null;
    if (tk != null && this.vkey != null && !tk.equals(this.vkey) && this.vnote.length() == 0) this.vnote = "Your profile changed - these are its Void Charms now";
    this.vkey = tk;
    if (h.length > 4) { String[] nn = h[4].split(",", -1); if (nn.length == 3) names = nn; }
    for (int i = 1; i < ls.length; i++) {
      String[] f = ls[i].split("\\\\|", -1);
      if (f.length >= 12 && f[0].equals("r")) rows.add(f);
      else if (f.length >= 2 && f[0].equals("x") && err == null) err = f[1];
    }
  }
  for (int i = 0; i < 3; i++) {
    b.appendInline("#SkyyInvWfB", @PKG@.InvData.WF_BTN.replace("{I}", String.valueOf(i)).replace("{S}", i == this.vsub ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvWf" + i + ".Text", @PKG@.MenuUtil.clip(names[i], 12));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvWf" + i, @EVD@.of("a", "vf:" + i));
  }
  int per = @PKG@.InvData.WRN;
  int np = rows.size() == 0 ? 1 : (rows.size() + per - 1) / per;
  if (this.vpage >= np) this.vpage = np - 1;
  if (this.vpage < 0) this.vpage = 0;
  this.vrows = new String[per];
  int nr = @PKG@.InvData.VRAR.length;
  for (int k = 0; k < per; k++) {
    int at = this.vpage * per + k;
    if (at >= rows.size()) { b.set("#SkyyInvWr" + k + ".Visible", false); continue; }
    String[] f = (String[]) rows.get(at);
    String id = f[2];
    boolean can = "1".equals(f[7]);
    String st = f[4] + "  -  " + f[6] + (f[10].length() > 0 ? "  -  " + f[10] : "");
    java.util.ArrayList one = new java.util.ArrayList();
    @IGS@ g = new @IGS@();
    if (id.length() > 0 && id.length() < 120 && known(id)) g.setItemStack(new @IS@(id, 1));
    g.setName(f[3]);
    g.setDescription(f[4] + String.valueOf((char) 10) + f[6] + (f[10].length() > 0 ? String.valueOf((char) 10) + f[10] : ""));
    one.add(g);
    b.set("#SkyyInvWi" + k + ".Slots", act(one));
    int rv = 0;
    for (int j = 0; j < nr; j++) if (@PKG@.InvData.VRAR[j].equalsIgnoreCase(f[5])) rv = j + 1;
    for (int j = 0; j <= nr; j++) {
      b.set("#SkyyInvWn" + k + "v" + j + ".Text", @PKG@.MenuUtil.clip(f[3], 60));
      b.set("#SkyyInvWn" + k + "v" + j + ".Visible", j == rv);
    }
    for (int j = 0; j < 2; j++) {
      b.set("#SkyyInvWs" + k + "v" + j + ".Text", @PKG@.MenuUtil.clip(st, 96));
      b.set("#SkyyInvWs" + k + "v" + j + ".Visible", (j == 1) == can);
    }
    boolean btn = !"m".equals(f[8]) && f[9].length() > 0 && f[9].length() < 160;
    b.set("#SkyyInvWb" + k + ".Visible", btn);
    if (btn) b.set("#SkyyInvWb" + k + ".Text", "u".equals(f[8]) ? "Upgrade" : "Craft");
    this.vrows[k] = btn ? f[9] + "|" + f[3] : null;
  }
  b.set("#SkyyInvWxI.Text", rows.size() + (rows.size() == 1 ? " charm" : " charms"));
  b.set("#SkyyInvWxPn.Text", (this.vpage + 1) + " / " + np);
  b.set("#SkyyInvWxM.Text", @PKG@.MenuUtil.clip(this.vnote.length() > 0 ? this.vnote : (err != null ? err : @PKG@.InvData.W_HELP), 110));
  this.vnote = "";
}""")
# ---- 0.3.55: THE TELEPORT ROW (the profile's saved keys) + the Teleports panel's list (world thread; reads only)
''')
P.rep('''M(ipg, r"""
public void charmPick(int si) {''', '''# a row's Craft / Upgrade = vc:craft with the drawn recipe id and the list's profile key (SkyyAccessories re-checks the line's next step,
# the lock, the materials and a free slot - an old row / a double click uses nothing); the same row within 1.5 s = no second call
M(ipg, r"""
public void charmRow(int k) {
  if (this.vrows == null || k < 0 || k >= this.vrows.length || this.vrows[k] == null) { this.vnote = "Nothing to craft on that row"; redraw(); return; }
  if (this.vkey == null || this.vkey.length() == 0) { this.vnote = "Your profile is not settled yet - try again in a moment"; redraw(); return; }
  String[] rv = this.vrows[k].split("\\\\|", 2);
  String key = "vr:" + rv[0];
  if (dup(key)) { this.vnote = this.vlast.length() > 0 ? this.vlast : "Double click ignored - wait a moment to click again"; redraw(); return; }
  moved(key);
  String r = vcAct("vc:craft", rv[0]);
  this.vlast = bare(r);
  this.vnote = this.vlast;
  redraw();
}""")
M(ipg, r"""
public void charmPick(int si) {''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.60: no new system / command"
P.finish()


def cut(t, start, end, keep_end=True):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


# ======================================================================= the HARNESS (derived from the 0.3.59 harness: every 0.3.59 check
# runs again on the 0.3.60 jar, plus MENUFIX1)
T.rep('''"""Harness for SkyyMenu 0.3.59 (the Market tab = one screen; tools/menu_0_3_59_patch.py).
GENERATED by tools/menu_0_3_59_patch.py from the 0.3.58 harness (edit the patch, not this file): every 0.3.58 check runs again on the
0.3.59 jar, plus''', '''"""Harness for SkyyMenu 0.3.60 (the menu fix round of Skyy's 11-21 test; tools/menu_0_3_60_patch.py).
GENERATED by tools/menu_0_3_60_patch.py from the 0.3.59 harness (edit the patch, not this file): every 0.3.59 check runs again on the
0.3.60 jar (INV5's stand-in now answers vc:rows like SkyyAccessories 0.5.37 does - "does not know" - so the 0.3.59 charm grid stays tested as
the fallback), plus
  MENUFIX1 (EXECUTED on the stand-ins; a Python stand-in of SkyyAccessories 0.5.38 vc:rows / vc:craft - the real side runs in
       SkyyAccessories/test_skyyaccessories_0.5.38.py):
       ACT     EVERY grid slot of EVERY page packet the run sent (inventory, skill page, pets, market; all panels) is ACTIVATABLE (the client
               sends SlotClicking only for those - the 11-21 "crafting doesnt work" / "i cant select anything" root cause); the drop zone not
       TOP     the 7-tab bar of all four screens is its own strip on the page root at Top 0, the window under it at Top 52; no separator
               strip; no page names SkyyGlass/Clear or SkyyGlass/Separator; the jar ships only the Skyglass pictures the classes name
       SKILLS  the inventory SKILLS card has no Open button; each tile's Lv text is a tab-style button bound skc:<n>; a click = that page
       TOOL    a multitool (Tool_Hatchet_Pickaxe_Multitool_*) in the bag = the Mining AND the Foraging tool card
       FORT    perk.doubleDropMax 0 / missing = no cap (the real total, no "(max 0%)"); an admin cap above 0 still caps and says so
       COUNT   the Void pocket icon carries the real amount (230 / 1,234 - was the 100 stack cap); a click selects the item
       STORE   the full Requip storage's button reads 'Done' and goes back to the preset
       ROWS    the Charms panel as ROWS (vc:rows): the three sub tabs (the open one selected), 5 rows a page + pages, the name in its rarity
               colour variant, status + cost (green when it can be made), Craft / Upgrade / no button on a max row, an unknown id = name only;
               Craft = ONE vc:craft with the drawn recipe id + the rows' profile key; a double click = no second call; a row without a
               button / out of range = no call; a refusal (materials / full inventory) shown, nothing else; a profile switch seen on a redraw
               says so and the next call carries the new key; Bag = the Void Charms page; Done = the craft panel; without 0.5.38 = the grid
The 0.3.59 harness text follows:
Harness for SkyyMenu 0.3.59 (the Market tab = one screen; tools/menu_0_3_59_patch.py).
GENERATED by tools/menu_0_3_59_patch.py from the 0.3.58 harness (edit the patch, not this file): every 0.3.58 check runs again on the
0.3.59 jar, plus''')
T.rep('VERSION = "0.3.59"\nJAR', 'VERSION = "0.3.60"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.58.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.59.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.58.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.59.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_59_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_60_patch.py")')
T.rep('"scratch", "tab3", "menu"', '"scratch", "menufix1", "menu"')
T.rep('ADDED = ["MarketTabData", "MarketTab"]   # 0.3.59: the market screen\n', 'ADDED = []   # 0.3.60: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.59:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.60: the activatable click grids (InvPage.act everywhere), the charm rows, the top bar markup, Fortune, the multitool
    "InvPage": ["+<clinit>", "+f ACTS", "+f vprobe", "+f vrows", "+f vsub", "+m act", "+m charmRow", "+m charmRowsOk", "+m fillCharmRows", "~m build", "~m fillCharms",
                "~m fillCraft", "~m fillDetail", "~m fillFurn", "~m fillPocket", "~m fillProg", "~m fillRequip", "~m fillSide", "~m fillStore", "~m fillTp",
                "~m fillTpRow", "~m handleDataEvent", "~m petCard"],
    "SkillPage": ["~m build", "~m fillCells", "~m fillGear", "~m fillHead", "~m fillPath", "~m fillShard"],
    "PetsTab": ["~m build", "~m fillEggs", "~m fillFuse", "~m fillGrid", "~m fillHatch", "~m fillSel", "~m fillSlots"],
    "MarketTab": ["~m build", "~m fillAh", "~m fillList", "~m fillSel"],
    "StatsCalc": ["~m fortune"],
    "InvData": ["+f WF_BTN", "+f WRN", "+f W_HELP", "~<clinit>"], "SkillData": ["~<clinit>"], "PetsTabData": ["~<clinit>"], "MarketTabData": ["~<clinit>"],   # the page data
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.59"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.60"') == 1, "S VERSION")''')
# the jar: the Skyglass pictures no class names are left out (0.3.60); every shipped one = the kit's bytes
T.rep('''    glass = SUI.glass_texture_files()
    K.eq(diff, ["manifest.json"], "S non-class jar entries changed = manifest only (the Skyglass textures as 0.3.50)")
    K.check(all(zn.read(k) == v for k, v in glass.items()) and all(k.startswith("Common/UI/Custom/SkyyGlass/") for k in glass),
            "S the jar's Skyglass files = the kit's generated bytes, only under Common/UI/Custom/SkyyGlass/ (%d files, sha256 %s)" % (len(glass), SUI.glass_texture_digest()[:12]))''',
      '''    glass = SUI.glass_texture_files()
    shipped = dict((k, v) for k, v in glass.items() if k in zn.namelist())
    named = set()
    for n_ in zn.namelist():
        if n_.endswith(".class"):
            named.update(m_.decode("ascii") for m_ in re.findall(rb"SkyyGlass/([A-Za-z0-9]+)\\.png", zn.read(n_)))
    K.eq(diff, sorted(["manifest.json"] + [k for k in glass if k not in shipped]), "S non-class jar entries changed = manifest + the Skyglass pictures no page uses (left out)")
    K.check(all(zn.read(k) == v for k, v in shipped.items()) and set(k.rsplit("/", 1)[1].replace("@2x.png", "") for k in shipped) == named
            and "Common/UI/Custom/SkyyGlass/Clear@2x.png" not in shipped and "Common/UI/Custom/SkyyGlass/Separator@2x.png" not in shipped,
            "MENUFIX1 TOP the jar ships exactly the Skyglass pictures its classes name (%d of %d; no Clear / Separator), each = the kit's bytes" % (len(shipped), len(glass)))''')
# INV5's stand-in answers vc:rows / vc:craft as SkyyAccessories 0.5.37 really does (the 0.3.59 grid = the fallback, still tested)
T.rep('''    def f_charms(o):
        op_, tok_, arg_ = str(o[0]), str(o[2]), str(o[3])
        if op_ != "vc:list":''', '''    def f_charms(o):
        op_, tok_, arg_ = str(o[0]), str(o[2]), str(o[3])
        if op_ in ("vc:rows", "vc:craft"):
            return "-Void Charms does not know that - nothing changed"   # 0.3.60: SkyyAccessories 0.5.37's answer
        if op_ != "vc:list":''')
HARNESS_MF = r'''    # ---- MENUFIX1 (0.3.60; Skyy 11-21: "crafting doesnt work at all.", "i cant select anything", "the numbers cap at 100", "these skill icons should
    # work as buttons", "and it wont detect my multitool", "editing requip doesnt work ... there was no back button", the charms as rows)
    MFR = re.compile(r"Top: (\d+)")
    for cls_, pfx_ in (("InvData", "SkyyInv"), ("SkillData", "SkyySkp"), ("PetsTabData", "SkyyPtab"), ("MarketTabData", "SkyyMtab")):
        c_ = JV(cls_)
        lk_, lp_, lb_ = [str(x_) for x_ in c_.LK], [str(x_) for x_ in c_.LP], [str(x_) for x_ in c_.LB]
        tp_ = [i_ for i_ in range(len(lk_)) if lk_[i_] == "A" and lb_[i_].startswith("Group #%sTop " % pfx_)]
        wn_ = [i_ for i_ in range(len(lk_)) if lk_[i_] == "A" and lb_[i_].startswith("Group #%sWin " % pfx_)]
        tt_ = MFR.search(lb_[tp_[0]]) if tp_ else None
        tw_ = MFR.search(lb_[wn_[0]]) if wn_ else None
        K.check(len(tp_) == 1 and len(wn_) == 1 and lp_[tp_[0]] == "#" + pfx_ and tt_ is not None and tt_.group(1) == "0" and tw_ is not None and tw_.group(1) == "52",
                "MENUFIX1 TOP %s: the 7-tab bar is its own strip on the page root at Top 0, the window under it at Top 52" % cls_)
        K.check(not [x_ for x_ in lb_ if "SkyyGlass/Clear.png" in x_ or "SkyyGlass/Separator.png" in x_ or ("#%sSep " % pfx_) in x_],
                "MENUFIX1 TOP %s: no separator strip, no SkyyGlass/Clear or Separator picture" % cls_)
    lk_, lp_, lb_ = [str(x_) for x_ in IDc_.LK], [str(x_) for x_ in IDc_.LP], [str(x_) for x_ in IDc_.LB]
    eb_ = [(lp_[i_], lb_[i_]) for i_ in range(len(lk_)) if lk_[i_] == "E"]
    K.check(not [x_ for x_ in lb_ + lp_ if "SkyyInvSkBtn" in x_] and all(("#SkyyInvSk%d" % k_, "skc:%d" % k_) in eb_ for k_ in range(12))
            and all([x_ for x_ in lb_ if x_.startswith("TextButton #SkyyInvSk%d " % k_)] for k_ in range(12)),
            "MENUFIX1 SKILLS the SKILLS card has no Open button; every tile's Lv text is a button bound to skc:<n>")
    BR.put("skill:fn:prog", Fn(lambda o: PROG))
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    p_ = one(ev(PK, {"a": "skc:2"}), "MENUFIX1 SKILLS a tile click")
    BR.remove("skill:fn:prog")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and str(cur_.skill) == "Foraging", "MENUFIX1 SKILLS the Foraging tile = the Foraging page")
    # TOOL: a multitool in the bag counts as the Mining AND the Foraging tool
    MT_ = "Tool_Hatchet_Pickaxe_Multitool_Iron"
    it_ = Ucls.allocateInstance(ITc.class_)
    E.jf(ITc.class_, "id").set(it_, MT_)
    E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
    E.jf(ITc.class_, "maxStack").setInt(it_, 1)
    amap.put(MT_, it_)
    for k_ in ("requip:fn:presets", "requip:fn:preset"):
        BR.remove(k_)
    put(PK, "hotbar", 5, ISc(MT_, 1))
    for i_, s_ in ((1, "Mining"), (2, "Foraging")):
        f_ = len(E.sent(PK))
        PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, json.dumps({"a": "sk:%d" % i_}))
        ps_ = pages(PK, f_)
        cm = cmap(ps_[0]) if ps_ else {}
        K.check(len(ps_) == 1 and MT_ in cm.get("#SkyySkpGtI.Slots", "") and sval(cm, "#SkyySkpGtL.Text") == "From your inventory",
                "MENUFIX1 TOOL the %s page's tool card = the multitool in the bag (%s)" % (s_, sval(cm, "#SkyySkpGtN.Text")))
    inv(PK, "hotbar").removeItemStackFromSlot(JShort(5))
    PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    # FORT: perk.doubleDropMax 0 / missing = no cap; above 0 = a cap
    SC = JV("StatsCalc")
    HMc = JClass("java.util.HashMap")
    DBLc = JClass("java.lang.Double")
    CFGV = {"perk.doubleDropMax": "0", "perk.mining.doubleDropPerLevel": "0.005"}
    BR.put("config:fn:SkyySkills", Fn(lambda o: CFGV.get(str(o[1]))))
    uk2_ = str(PK.pr.getUuid())
    BR.put("skill:bonus:" + uk2_, JClass("java.util.HashMap")())
    BR.get("skill:bonus:" + uk2_).put("trees", HMc())
    BR.get("skill:bonus:" + uk2_).get("trees").put("dd.mining", DBLc(3.264))
    skm_ = HMc()
    skm_.put("Mining", DBLc(50.0))

    def fort(max_):
        if max_ is None:
            CFGV.pop("perk.doubleDropMax", None)
        else:
            CFGV["perk.doubleDropMax"] = max_
        rows_ = JClass("java.util.ArrayList")()
        SC.fortune(rows_, PK.pr.getUuid(), skm_, True, 0)
        return [str(x_) for x_ in rows_.get(0)]
    r0_, r1_, r2_ = fort("0"), fort(None), fort("1.5")
    K.check(r0_[1] == "351.4%" and "(max" not in r0_[2] and "Mining level 50 +25%" in r0_[2] and "Skill trees +326.4%" in r0_[2],
            "MENUFIX1 FORT perk.doubleDropMax 0 (SkyySkills' default) = no cap: the real 351.4%%, no '(max 0%%)' (%s / %s)" % (r0_[1], r0_[2]))
    K.check(r1_[1] == "351.4%" and "(max" not in r1_[2], "MENUFIX1 FORT the key missing = no cap (%s)" % r1_[1])
    K.check(r2_[1] == "150%" and "(max 150%)" in r2_[2], "MENUFIX1 FORT an admin cap above 0 still caps and says so (%s / %s)" % (r2_[1], r2_[2]))
    BR.remove("config:fn:SkyySkills")
    BR.remove("skill:bonus:" + uk2_)
    # COUNT + pick: the Void pocket icon = the real amount; a click selects
    PKT2 = {"t": "k9"}
    BR.put("sacks:fn:pocketList", Fn(lambda o: "ok|Mining|3|Rare|1464|6720|1|k9\nRock_Stone|230|0|5\nWood_Oak_Trunk|1234|0|-1"))
    BR.put("sacks:fn:pocket", Fn(lambda o: "+ok"))
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    p_ = one(ev(PK, {"a": "pt:1"}), "MENUFIX1 COUNT the Mining pocket")
    gs_ = json.loads(cmap(p_).get("#SkyyInvPg.Slots", "null")) if p_ else None
    gl_ = gs_.get("0") if isinstance(gs_, dict) else gs_
    K.notes.append("MENUFIX1 pocket slot 0 JSON: %s" % (json.dumps(gl_[0])[:300] if gl_ else gl_))

    def qty_of(o_, iid_):
        if isinstance(o_, dict):
            if iid_ in [o_.get(k_) for k_ in ("Id", "ItemId", "id")]:
                for k_ in ("Quantity", "quantity"):
                    if k_ in o_:
                        return o_[k_]
            for v_ in o_.values():
                q_ = qty_of(v_, iid_)
                if q_ is not None:
                    return q_
        if isinstance(o_, list):
            for v_ in o_:
                q_ = qty_of(v_, iid_)
                if q_ is not None:
                    return q_
        return None
    K.check(gl_ is not None and qty_of(gl_[0], "Rock_Stone") == 230 and qty_of(gl_[1], "Wood_Oak_Trunk") == 1234,
            "MENUFIX1 COUNT the pocket icons carry the real amounts 230 / 1234 (not the 100 stack cap) (%s, %s)" % (qty_of(gl_[0], "Rock_Stone") if gl_ else None, qty_of(gl_[1], "Wood_Oak_Trunk") if gl_ else None))
    p_ = one(ev(PK, {"a": "pgs", "SlotIndex": 1}), "MENUFIX1 COUNT pick an item")
    K.check(str(pg.psel) == "Wood_Oak_Trunk" and "1,234" in str(sval(cmap(p_), "#SkyyInvPsC.Text")), "MENUFIX1 COUNT a click selects the item (its Void count %s)" % sval(cmap(p_), "#SkyyInvPsC.Text"))
    BR.remove("sacks:fn:pocketList")
    BR.remove("sacks:fn:pocket")
    one(ev(PK, {"a": "pt:0"}), "MENUFIX1 back to Craft")
    # ROWS: the Charms panel as rows (SkyyAccessories 0.5.38 vc:rows / vc:craft)
    RRAR = ["Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic", "Nope"]
    CRW = {"calls": [], "tok": "ck1", "ans": "+crafted Speed Accessory - it is in your inventory (Void Charms)", "reads": 0}

    def f_rows(o):
        op_, tok_, arg_ = str(o[0]), str(o[2]), str(o[3])
        if op_ == "vc:rows":
            CRW["reads"] += 1
            sub_ = int(arg_) if arg_.isdigit() else 0
            if sub_ == 1:
                ls_ = ["ok|1|7|%s|Benches,Combat,Gathering" % CRW["tok"]]
                for i_ in range(7):
                    can_ = i_ % 2
                    md_ = "m" if i_ == 2 else ("u" if i_ == 3 else "c")
                    ls_.append("r|%d|%s|Speed Charm %d|NORMAL - %s|%s|Speed Gem %d/4|%d|%s|%s||0" % (
                        i_, SPD_ if i_ != 1 else "Gone_Row_Item", i_, "CAN CRAFT" if can_ else "NEEDS MATERIALS", RRAR[i_], i_, can_, md_, "" if md_ == "m" else "Rec_%d" % i_))
                return "\n".join(ls_)
            return "ok|%d|1|%s|Benches,Combat,Gathering\nr|0|%s|Furnace Charm I|NORMAL - MAX|Normal|Fully upgraded|0|m|||0" % (sub_, CRW["tok"], FC1)
        if op_ == "vc:list":
            return "ok|0|18|60|0|%s" % CRW["tok"]
        CRW["calls"].append((op_, tok_, arg_))
        return CRW["ans"]
    BR.put("acc:fn:charms", Fn(f_rows))
    TS_, TN_ = str(JV("InvData").ST_TABSEL), str(JV("InvData").ST_TAB)
    r0_ = CRW["reads"]
    p_ = one(ev(PK, {"a": "vc"}), "MENUFIX1 ROWS All charms")
    K.eq(CRW["reads"] - r0_, 1, "MENUFIX1 ROWS opening the panel reads vc:rows ONCE (the probe's answer is reused by the fill)")
    cm = cmap(p_) if p_ else {}
    vis = lambda c_, k_: sval(c_, "#SkyyInv%s.Visible" % k_) in (True, "true")
    K.check(str(pg.mode) == "w" and "#SkyyInvVxG.Slots" not in cm and "#SkyyInvCg.Slots" not in cm and TS_ in mk_of(p_, "SkyyInvWf0") and TS_ not in mk_of(p_, "SkyyInvWf1")
            and [sval(cm, "#SkyyInvWf%d.Text" % k_) for k_ in range(3)] == ["Benches", "Combat", "Gathering"] and "#SkyyInvIs.Slots" in cm,
            "MENUFIX1 ROWS All charms = the ROWS panel (not the grid, not the craft grid), Benches / Combat / Gathering with Benches selected, the bag stays")
    K.check(vis(cm, "Wn0v1") and not vis(cm, "Wn0v0") and not vis(cm, "Wb0") and sval(cm, "#SkyyInvWr1.Visible") in (False, "false")
            and sval(cm, "#SkyyInvWxI.Text") == "1 charm" and FC1 in cm.get("#SkyyInvWi0.Slots", ""),
            "MENUFIX1 ROWS Benches: one MAX row (name in the Normal colour, no button), rows 2-5 hidden, the count")
    p_ = one(ev(PK, {"a": "vf:1"}), "MENUFIX1 ROWS the Combat tab")
    cm = cmap(p_) if p_ else {}
    K.check(int(pg.vsub) == 1 and TS_ in mk_of(p_, "SkyyInvWf1") and sval(cm, "#SkyyInvWxPn.Text") == "1 / 2" and sval(cm, "#SkyyInvWxI.Text") == "7 charms"
            and vis(cm, "Wn1v2") and vis(cm, "Wn4v5") and not vis(cm, "Wn1v0") and vis(cm, "Ws1v1") and vis(cm, "Ws0v0") and not vis(cm, "Ws0v1")
            and sval(cm, "#SkyyInvWb0.Text") == "Craft" and sval(cm, "#SkyyInvWb3.Text") == "Upgrade" and not vis(cm, "Wb2") and vis(cm, "Wb0")
            and "Gone_Row_Item" not in cm.get("#SkyyInvWi1.Slots", "") and "Speed Charm 1" in cm.get("#SkyyInvWi1.Slots", "")
            and "NORMAL - CAN CRAFT  -  Speed Gem 1/4" in str(sval(cm, "#SkyyInvWs1v1.Text")) and nometa(p_),
            "MENUFIX1 ROWS Combat: 5 rows a page (1 / 2), names in their rarity colours, status + cost green when it can be made, Craft / Upgrade / none on MAX, an unknown id = name only")
    n0_ = len(CRW["calls"])
    p_ = one(ev(PK, {"a": "vr:1"}), "MENUFIX1 ROWS Craft")
    K.check(CRW["calls"][n0_:] == [("vc:craft", "ck1", "Rec_1")] and "crafted Speed Accessory" in str(sval(cmap(p_), "#SkyyInvWxM.Text")),
            "MENUFIX1 ROWS Craft = ONE vc:craft with the drawn recipe id + the rows' profile key, the answer shown (%s)" % CRW["calls"][n0_:])
    one(ev(PK, {"a": "vr:1"}), "MENUFIX1 ROWS the same Craft again")
    K.eq(len(CRW["calls"]), n0_ + 1, "MENUFIX1 ROWS a double click = no second call")
    for a_, why_ in (("vr:2", "a MAX row (no button)"), ("vr:9", "out of range"), ("vr:x", "bad")):
        p_ = one(ev(PK, {"a": a_}), "MENUFIX1 ROWS " + why_)
        K.check(len(CRW["calls"]) == n0_ + 1 and "Nothing to craft" in str(sval(cmap(p_), "#SkyyInvWxM.Text")), "MENUFIX1 ROWS %s: no call, said" % why_)
    CRW["ans"] = "-not enough materials for Speed Charm 3 - nothing was used"
    p_ = one(ev(PK, {"a": "vr:3"}), "MENUFIX1 ROWS Upgrade refused")
    K.check(CRW["calls"][-1] == ("vc:craft", "ck1", "Rec_3") and str(sval(cmap(p_), "#SkyyInvWxM.Text")).startswith("not enough materials"), "MENUFIX1 ROWS a refusal is shown (materials)")
    CRW["ans"] = "-no room for Speed Charm 0 in your inventory or Void Charms - nothing was used"
    p_ = one(ev(PK, {"a": "vr:0"}), "MENUFIX1 ROWS full inventory")
    K.check(str(sval(cmap(p_), "#SkyyInvWxM.Text")).startswith("no room for Speed Charm 0"), "MENUFIX1 ROWS a full inventory is shown, nothing else")
    p_ = one(ev(PK, {"a": "vpn"}), "MENUFIX1 ROWS page 2")
    cm = cmap(p_) if p_ else {}
    K.check(sval(cm, "#SkyyInvWxPn.Text") == "2 / 2" and vis(cm, "Wn1v0") and sval(cm, "#SkyyInvWr2.Visible") in (False, "false"), "MENUFIX1 ROWS page 2: rows 6-7 (an unknown rarity = the plain name), the rest hidden")
    one(ev(PK, {"a": "vpp"}), "MENUFIX1 ROWS page 1")
    CRW["tok"] = "ck2"
    p_ = one(ev(PK, {"a": "vf:1"}), "MENUFIX1 ROWS a redraw after a profile switch")
    K.check("Your profile changed" in str(sval(cmap(p_), "#SkyyInvWxM.Text")), "MENUFIX1 ROWS a profile switch seen on a redraw is said (%s)" % sval(cmap(p_), "#SkyyInvWxM.Text"))
    time.sleep(1.6)
    one(ev(PK, {"a": "vr:1"}), "MENUFIX1 ROWS Craft on the new profile")
    K.eq(CRW["calls"][-1], ("vc:craft", "ck2", "Rec_1"), "MENUFIX1 ROWS the next Craft carries the new profile's key")
    p_ = one(ev(PK, {"a": "vbag"}), "MENUFIX1 ROWS Bag")
    cur_ = PK.pm.getCustomPage()
    K.check(p_ is not None, "MENUFIX1 ROWS Bag = the Void Charms page route, ONE packet (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    if PK.pm.getCustomPage() is not None and PK.pm.getCustomPage() != pg:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    one(ev(PK, {"a": "vc"}), "MENUFIX1 ROWS again")
    p_ = one(ev(PK, {"a": "vcd"}), "MENUFIX1 ROWS Done")
    K.check(str(pg.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_), "MENUFIX1 ROWS Done = the craft panel again")
    BR.remove("acc:fn:charms")
    # STORE: the full Requip storage's 'Done'
    K.check([x_ for x_ in lb_ if x_.startswith("TextButton #SkyyInvQB ") and "Done" in x_] and ("#SkyyInvQB", "rst") in eb_ + [(str(IDc_.LP[i_]), str(IDc_.LB[i_])) for i_ in range(len(lk_)) if lk_[i_] == "E"],
            "MENUFIX1 STORE the full Requip storage's button reads 'Done' (rst = back to the preset)")
    # ACT: every grid slot of every page packet this run sent is activatable (the drop zone excepted)
    bad_, nsl_, ngr_ = [], 0, set()
    for PP_ in (PI, PK):
        for pk_ in E.sent(PP_):
            if str(pk_.getClass().getSimpleName()) != "CustomPage":
                continue
            for c_ in cmds_of(pk_):
                sel_ = str(c_.selector)
                if not sel_.endswith(".Slots") or sel_ == "#SkyyInvDz.Slots" or not sel_.startswith(("#SkyyInv", "#SkyySkp", "#SkyyPtab", "#SkyyMtab")):
                    continue
                try:
                    j_ = json.loads(str(c_.data))
                except Exception:
                    continue
                l_ = j_.get("0") if isinstance(j_, dict) else j_
                for s_ in (l_ or []):
                    nsl_ += 1
                    ngr_.add(re.sub(r"\d+", "#", sel_))
                    if not (isinstance(s_, dict) and s_.get("IsActivatable") is True):
                        bad_.append(sel_)
    K.check(nsl_ > 500 and not bad_ and len(ngr_) >= 25,
            "MENUFIX1 ACT every grid slot of every page packet of this run is ACTIVATABLE (%d slots in %d grids; not: %s)" % (nsl_, len(ngr_), sorted(set(bad_))[:8]))
    K.notes.append("MENUFIX1 grids checked: %s; InvPage.act lists %d" % (sorted(ngr_), int(PG.ACTS)))
    if PK.pm.getCustomPage() is not None:
        PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    E.pump(PK)
'''
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_MF + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
T.rep('''if "--expect-dump" in sys.argv:
    EXPECT = {}
PH = ''', '''if "--expect-dump" in sys.argv:
    EXPECT = {}
_eq60 = HK.Child.eq


def _eq_glass(self, got, want, what):   # 0.3.60: the Skyglass pictures no page names are left out of the jar (the client UI atlas)
    if what == "C: non-class entries changed" and want == ["manifest.json"] and os.path.isfile(JAR):
        _zn = set(zipfile.ZipFile(JAR).namelist())
        want = sorted(["manifest.json"] + [k_ for k_ in SUI.glass_texture_files() if k_ not in _zn])
    return _eq60(self, got, want, what)


HK.Child.eq = _eq_glass
PH = ''')
T.rep('''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12, "PAGE: 61 bindings (0.3.57:''', '''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12 + 12 - 1, "PAGE: 72 bindings (0.3.60: + the 12 skill tiles' Lv buttons, the SKILLS Open button gone; 0.3.57:''')
T.rep('''import os, sys, re, json, subprocess, zipfile, importlib.util, hashlib
''', '''import os, sys, re, json, subprocess, zipfile, importlib.util, hashlib, time
''')
T.rep('''    ST, PG, DATA = JV("InvState"), JV("InvPage"), JV("InvData")
''', '''    ST, PG, DATA = JV("InvState"), JV("InvPage"), JV("InvData")
    IDc_ = DATA   # 0.3.60
''')
if T.dst:
    T.finish()
