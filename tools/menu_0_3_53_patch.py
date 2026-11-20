"""Derive SkyyMenu/build_skyymenu_0.3.53.py + SkyyMenu/test_skyymenu_0.3.53.py from the SET pin SkyyMenu 0.3.52 (generated - never re-run
its patch). Run:  python tools/menu_0_3_53_patch.py   then   python SkyyMenu/build_skyymenu_0.3.53.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.53.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.52 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.53 (2026-11-17, round inv4) = REQUIP INSIDE THE INVENTORY + POCKET TABS + the mount Summon button (approved art research/ui-theme-art/
inventory-mockup-requip.png, inventory-mockup-mining.png, README defaults). Skyy's words: "Start it now" (11-17); popup 'Where should
editing Requip presets (and the Charms page) happen instead?' -> "Inside the inventory (Recommended)"; TEST 284 "i dont see the pets the
requip, the charms, the pockets, the teleports."; popup 'Are the world page and the Requip / Charms panels right?' -> "Yes, all three";
"start with combat, mining, farming, foraging and fishing" (the presets); pets.md 11-14 "i want to summon it with a button".
  1. REQUIP PRESETS in the character header (where 0.3.52 had "REQUIP  Open Requip"): one button per preset - Combat / Mining / Farming /
     Foraging / Fishing (SkyyWardrobe 0.2.14 names its unnamed loadouts 1-5 so; an own name wins), the preset you wear highlighted; ONE
     click = Equip that loadout (requip:fn:act equip = Requip's own write-ahead Equip). "Edit" opens the Requip panel.
  2. THE REQUIP PANEL swaps the crafting area (the bag, hotbar and character column stay): the preset list (+ the custom ones), the
     selected preset's 4 armour pieces + pet + mount and its 9 hotbar slots, each marked on you / stored / missing / keep / empty / pocket
     (requip:fn:preset), Equip / Save what I wear / Rename / Keep slot / Done, a smart hint line (what is missing, what waits in storage, the
     picked slot), the Requip storage strip (wardrobe:fn:list; Take out) and its title = the full storage grid (12 x 4, paged).
     DRAG an item from the bag / hotbar / armour onto a preset slot = it is SAVED AT ONCE (README default): requip:fn:act drop = Requip's own
     deposit (the item goes into Requip storage) + the pick of that entry - every check BEFORE anything moves (SkyyWardrobe 0.2.14).
     The page never moves an item for Requip itself; the Requip button no longer opens the old Requip page (Skyy: no separate Requip page).
  3. POCKET TABS above the bag: Craft | Mining | Foraging | Farming | Fishing | Combat | Smithing (SkyySacks 0.8.38's categories). A pocket
     tab swaps the crafting area for that pocket's grid (sacks:fn:pocketList: one slot per item with its whole Void count in the name and
     the detail - the icon number tops out at a full stack until a probe proves bigger numbers safe on the client - no metadata), Lv / rarity / used / space, a search box, an "Enchanted only" chip, paging, the picked item with its Void count and Bazaar
     price, an amount box and Withdraw / Deposit / Sell / Unpack = sacks:fn:pocket = the Void page's OWN click branches (item + coin
     safety stays SkyySacks'). Without SkyySacks 0.8.38 the row is Craft | Void (the Void page) as 0.3.52.
  4. MOUNT SUMMON: a Summon button under the mount card = pets:fn:ride (SkyyPets 0.4.26) = F on your own summon-slot mount (today's ride).
  5. TANNING tab: sacks:fn:openTannery (SkyySacks 0.8.38) opens the pack's own Tannery page; without it, the Crafting page as 0.3.52.
  Layout: one holder (#SkyyInvTopP) for the swappable panel; the page data carries a panel code per line (LC: '-' shell, 'c' craft,
  'r' Requip, 'q' Requip storage, 'p' pocket) and build() draws the shell + the panel of the current mode only (fewer elements than
  0.3.52's always-on craft panel when a panel is swapped). Every click answers with ONE page packet (redraw / say), as 0.3.52.
  FIX PASS (critics, round inv4): (a) the preset list pages - a "More (1 / 2)" row when the presets do not fit, so every loadout (up to
     Requip's max) can be picked, edited and equipped; (b) "+ New preset" (the approved Requip art) = the first unused custom loadout (6+,
     nothing picked) - pick it, then Save what I wear / Rename; (c) a pocket action carries the profile token of the list it was picked
     from (SkyySacks 0.8.38 refuses another profile's, the Void page's own "your profile changed" check) and a profile change seen on a
     redraw clears the pick; (d) an item id the server does not know (a pack mod removed) is drawn as a name-only slot, never as an
     ItemStack (pocket grid + pick, Requip slots, storage, pet / mount icons).
  NEXT ROUND (not built here, nothing half-wired): the pocket panel's Upgrades link + Auto-compact (README pocket design), a scrolling
     Requip storage strip (today: 7 slots windowed to the pick, the full grid on its title), Salvage + charm / ability slots in the Requip
     panel (approved art), keys 1-5 for the presets, the Charms panel ('All charms' still opens the Void Charms page until it exists - its
  Tier up / Merge 3 / Upgrade bag need new SkyyAccessories mechanics), editable armour / off-hand + the Z bar, teleport row editing, the
  themed Furnace / Tanning inside the panel (fuel slot, queue, Collect all), charms + abilities per preset (needs a Requip data field).
  No saved data, no command, no setting, no lang key, no system; no new class. Client-crash rules kept: never setPageWithWindows; every grid
  copy a NEW ItemStack without metadata; no Top / Bottom alignment; inline page only; runtime markup = kit styles + digits only.
  ROLLBACK to 0.3.52: safe (no data). Goes with SkyyWardrobe 0.2.14 / SkyyPets 0.4.26 / SkyySacks 0.8.38 (each optional: a missing bridge =
  that part says it is not on this server, nothing breaks).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.52.py"), os.path.join(MOD, "build_skyymenu_0.3.53.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.52.py"), os.path.join(MOD, "test_skyymenu_0.3.53.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.52"\n') and P.has("tools/menu_0_3_52_patch.py") and P.has("InvCraft")
assert not P.has("fillRequip"), "not the generated SkyyMenu 0.3.52 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(" = mk(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.53: REQUIP INSIDE THE INVENTORY (one-click presets Combat / Mining / Farming / Foraging / Fishing in the header; Edit = the Requip panel in
       the crafting area: slots with on you / stored / missing marks, Equip / Save what I wear / Rename / Keep slot, drag a bag item onto a
       slot = saved at once, the storage strip + full grid) + POCKET TABS (each pocket's grid, Withdraw / Deposit / Sell / Unpack through
       SkyySacks' own branches) + the mount card's Summon + the Tanning tab (notes: tools/menu_0_3_53_patch.py).
       CHECKED: see SkyyMenu/test_skyymenu_0.3.53.py.
''')
P.rep('VERSION = "0.3.52"\n', 'VERSION = "0.3.53"\n')

# ---------- THE PAGE: the shell changes (inside _inv_page)
# (1) the header presets row
P.rep('''    rq = IV + "RqRow"
    ap.append(("#" + ch, G_.glass_group(rq, ciw, 34, layout="Left")))
    ap.append(("#" + rq, lab(IV + "RqH", "REQUIP", 15, "accentHi", bold=True, w=110, h=34)))
    ap.append(("#" + rq, G_.glass_button(IV + "RqBtn", "Open Requip", "secondary", w=160, h=32, size=14)))
''', '''    # 0.3.53: THE REQUIP PRESETS (drawn at run time into #SkyyInvRqP: one button per preset, the worn one selected) + Edit = the Requip panel
    rq = IV + "RqRow"
    ap.append(("#" + ch, G_.glass_group(rq, ciw, 34, layout="Left")))
    ap.append(("#" + rq, G_.glass_group(IV + "RqP", IV_PRESET_W, 34, layout="Left")))
    ap.append(("#" + rq, G_.glass_button(IV + "RqE", "Edit", "secondary", w=ciw - IV_PRESET_W - 6, h=32, size=13, anchor={"left": 6})))
''')
# (2) the Summon row under the pet + mount cards
P.rep('''    # vitals 2 x 2
    vit = IV + "Vit"
''', '''    # 0.3.53: the mount card's Summon button (pets:fn:ride = F on your own summon-slot mount)
    smr = IV + "SmRow"
    ap.append(("#" + ch, G_.glass_group(smr, ciw, 30, layout="Left", anchor={"top": 4})))
    ap.append(("#" + smr, "Group { Anchor: (Width: %d); }" % (cw + 10)))
    ap.append(("#" + smr, G_.glass_button(IV + "Sum", "Summon", "secondary", w=cw, h=28, size=13)))
    # vitals 2 x 2
    vit = IV + "Vit"
''')
P.rep('''    left_used = 34 + 8 + 26 + 22 + 18 + 6 + gear_h + 8 + 26 + 4 + 56 + 10 + 64 + 10 + 76 + 24''',
      '''    left_used = 34 + 8 + 26 + 22 + 18 + 6 + gear_h + 8 + 26 + 4 + 56 + 10 + 64 + 34 + 10 + 76 + 24   # 0.3.53: + the Summon row''')
# (3) the swappable holder: the craft panel goes into its own list (panel code 'c') inside #SkyyInvTopP
P.rep('''    ap.append(("#" + md, G_.glass_group(cf, IV_COL_M, craft_h, role="panel", layout="Top", pad=10)))
''', '''    # 0.3.53: ONE holder for the swappable panel (craft 'c', Requip 'r', Requip storage 'q', a pocket 'p'); the craft panel is its own list
    ap.append(("#" + md, G_.glass_group(IV + "TopP", IV_COL_M, craft_h, layout="Top")))
    IV_CRAFT_H[0] = craft_h
    ap_shell = ap
    ap = IV_PANELS["c"][0]
    ap.append(("#" + IV + "TopP", G_.glass_group(cf, IV_COL_M, craft_h, role="panel", layout="Top", pad=10)))
''')
# (4) the pocket row = run-time tabs (Craft + the six pockets, or Craft | Void without SkyySacks 0.8.38)
P.rep('''    # the pocket row (Craft | Void)
    pk = IV + "Pk"
    ap.append(("#" + md, G_.glass_group(pk, IV_COL_M, 40, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pk, G_.glass_button(IV + "PkC", "Craft", "tabSelected", w=120, h=38, size=15, anchor={"right": 2})))
    ap.append(("#" + pk, G_.glass_button(IV + "PkV", "Void", "tab", w=120, h=38, size=15)))
    ap.append(("#" + pk, lab(IV + "PkNote", "", 13, "dim", w=IV_COL_M - 242 - 12, h=38, anchor={"left": 12})))
    ap.sets.append((IV + "PkNote", "Text", IV_TXT["pkNote"]))
''', '''    ap = ap_shell
    # 0.3.53: the pocket row = run-time tabs into #SkyyInvPk (Craft | Mining | Foraging | Farming | Fishing | Combat | Smithing)
    pk = IV + "Pk"
    ap.append(("#" + md, G_.glass_group(pk, IV_COL_M, 40, layout="Left", anchor={"top": 6})))
''')
# (5) the bindings: the craft panel's go with its list; Requip / Void / Open Requip are gone; Edit + Summon added
P.rep('''    binds = [("#%sT%d" % (IV, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [
        ("#" + IV + "Close", "close"), ("#" + IV + "Sort", "sort"), ("#" + IV + "RqBtn", "rq"), ("#" + IV + "VcAll", "vc"),
        ("#" + IV + "CfOnly", "conly"), ("#" + IV + "CqX", "cqx"), ("#" + IV + "CpPrev", "cpp"), ("#" + IV + "CpNext", "cpn"),
        ("#" + IV + "Cx1", "cx:1"), ("#" + IV + "Cx10", "cx:10"), ("#" + IV + "CxA", "cx:0"), ("#" + IV + "PkC", "pkc"),
        ("#" + IV + "PkV", "pkv"), ("#" + IV + "SkBtn", "tab:1"), ("#" + IV + "NowBtn", "nowq")]
''', '''    binds = [("#%sT%d" % (IV, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [
        ("#" + IV + "Close", "close"), ("#" + IV + "Sort", "sort"), ("#" + IV + "RqE", "rqe"), ("#" + IV + "VcAll", "vc"),
        ("#" + IV + "Sum", "sum"), ("#" + IV + "SkBtn", "tab:1"), ("#" + IV + "NowBtn", "nowq")]
    IV_PANELS["c"][1].extend([
        ("#" + IV + "CfOnly", "conly"), ("#" + IV + "CqX", "cqx"), ("#" + IV + "CpPrev", "cpp"), ("#" + IV + "CpNext", "cpn"),
        ("#" + IV + "Cx1", "cx:1"), ("#" + IV + "Cx10", "cx:10"), ("#" + IV + "CxA", "cx:0")])
''')

# ---------- the constants the shell + panels need (before _inv_page)
P.rep('''def _inv_page():
    ap = SUI.Appends()
''', '''# 0.3.53: the presets row (the run-time preset buttons fit IV_PRESET_W; Edit takes the rest), the panels' lists, the run-time templates
IV_PRESET_W, IV_PMAX = 300, 5
IV_CRAFT_H = [0]
IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), [])}
IV_PCATS = ["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]   # SkyySacks' Void categories, its tab order (PD_CATS)
IV_RS, IV_RSN, IV_QC, IV_QR, IV_PGC, IV_PGR, IV_RLMAX = 44, 7, 12, 4, 9, 4, 7
IV_ST_P, IV_ST_PSEL = SUI.glass_button_style("tab", 12), SUI.glass_button_style("tabSelected", 12)
IV_PRESET_BTN = "TextButton #SkyyInvRp{I} { Anchor: (Width: {W}, Height: 32, Right: 2, Top: 1); {S} }"
IV_PRESET_NONE = "Label #SkyyInvRpE { Anchor: (Width: %d, Height: 32); Style: %s; }" % (IV_PRESET_W, SUI.glass_text_style(12, "dim"))
IV_PK_BTN = "TextButton #SkyyInvPt{I} { Anchor: (Width: {W}, Height: 38, Right: 2); {S} }"
IV_RL_BTN = "TextButton #SkyyInvRl{I} { Anchor: (Width: 150, Height: 26, Bottom: 4); {S} }"
IV_ST_RL, IV_ST_RLSEL = SUI.glass_button_style("secondary", 12), SUI.glass_button_style("tabSelected", 12)
for _mk in (IV_PRESET_BTN.replace("{I}", "0").replace("{W}", "58").replace("{S}", IV_ST_P), IV_PRESET_NONE,
            IV_PK_BTN.replace("{I}", "0").replace("{W}", "100").replace("{S}", IV_ST_TAB), IV_RL_BTN.replace("{I}", "0").replace("{S}", IV_ST_RL)):
    SUI.check_markup(_mk, prefix=IV, kit_paths=True)
    assert "@" not in _mk and "\\n" not in _mk, "0.3.53: a runtime markup line Java can hold"
for _l in ("Combat", "Mining", "Farming", "Foraging", "Fishing"):
    assert SUI.text_width(_l, 12, bold=True) <= (IV_PRESET_W - 2 * IV_PMAX) // IV_PMAX - 6, "0.3.53: a preset name fits its button: " + _l
for _l in ["Craft"] + IV_PCATS:
    assert SUI.text_width(_l, 14, bold=True) <= (IV_COL_M - 2 * 7) // 7 - 10, "0.3.53: a pocket tab label fits: " + _l
IV_TXT.update({
    "rqHelp": "Drag gear from your bag onto a slot to save it into this preset.",
    "pkHelp": "Pick an item, type an amount (empty = one stack, or all), then Withdraw, Deposit, Sell or Unpack.",
    "qHelp": "Click an item, then Take out.",
})


def _inv_page():
    ap = SUI.Appends()
''')

# ---------- the three new panels (built after _inv_page: the holder's height is known then)
P.rep('''IV_BW_ALL = [0]
IV_AP, IV_BINDS, IV_H = _inv_page()
''', '''IV_BW_ALL = [0]
IV_AP, IV_BINDS, IV_H = _inv_page()


def _inv_panels():
    """0.3.53: the Requip panel 'r', the full Requip storage 'q' and a pocket 'p' - each fills #SkyyInvTopP (IV_COL_M x the craft height)."""
    G_ = SUI
    lab = G_.glass_label
    ph = IV_CRAFT_H[0]
    pw = IV_COL_M - 20
    TP = "#" + IV + "TopP"
    # ======== 'r' REQUIP - editing one preset (research/ui-theme-art/inventory-mockup-requip.png)
    ap, binds = IV_PANELS["r"]
    pan = IV + "RqPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    ra = IV + "RqA"
    ap.append(("#" + pan, G_.glass_group(ra, pw, 34, layout="Left")))
    tw = 280
    ap.append(("#" + ra, lab(IV + "RqT", "", 16, "accentHi", bold=True, w=tw, h=34)))
    sp = pw - tw - 110 - 6 - 170 - 6 - 80
    assert sp >= 0, ("0.3.53: the Requip header fits", sp)
    ap.append(("#" + ra, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + ra, G_.glass_button(IV + "RqEq", "Equip", "primary", w=110, h=32, size=14)))
    ap.append(("#" + ra, G_.glass_button(IV + "RqSv", "Save what I wear", "secondary", w=170, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + ra, G_.glass_button(IV + "RqDn", "Done", "secondary", w=80, h=32, size=13, anchor={"left": 6})))
    bh = ph - 20 - 34 - 6
    rb = IV + "RqB"
    ap.append(("#" + pan, G_.glass_group(rb, pw, bh, layout="Left", anchor={"top": 6})))
    ap.append(("#" + rb, G_.glass_group(IV + "RqL", 150, bh, layout="Top")))
    ap.append(("#" + rb, "Group { Anchor: (Width: 10); }"))
    rw = pw - 150 - 10
    rr = IV + "RqR"
    ap.append(("#" + rb, G_.glass_group(rr, rw, bh, layout="Top")))
    ap.append(("#" + rr, lab(None, "Armour - pet - mount", 12, "dim", bold=True, w=rw, h=16)))
    gaw, _gah = SUI.glass_grid_size(6, 1, IV_RS)
    ghw, _ghh = SUI.glass_grid_size(9, 1, IV_RS)
    r1 = IV + "RqAr"
    ap.append(("#" + rr, G_.glass_group(r1, rw, IV_RS, layout="Left")))
    ap.append(("#" + r1, G_.glass_grid(IV + "Ra", 6, 1, drag=False, slot=IV_RS, icon=IV_RS - 8)))
    ap.append(("#" + r1, "Group { Anchor: (Width: 12); }"))
    ap.append(("#" + r1, G_.text_field(IV + "RnBox", IV + "Rn", w=150, h=32, placeholder="New name", max_length=24, size=13, anchor={"top": 6})))
    ap.append(("#" + r1, G_.glass_button(IV + "RnGo", "Rename", "secondary", w=90, h=32, size=13, anchor={"left": 6, "top": 6})))
    assert gaw + 12 + 150 + 6 + 90 <= rw, ("0.3.53: the armour row fits", gaw, rw)
    m1 = IV + "RmA"
    ap.append(("#" + rr, G_.glass_group(m1, rw, 16, layout="Left")))
    for k_ in range(6):
        ap.append(("#" + m1, lab(IV + "Ma%d" % k_, "", 11, "text", w=IV_RS, h=16, halign="Center", anchor={"right": SUI.GRID_SPACING} if k_ < 5 else None)))
    ap.append(("#" + rr, lab(None, "Hotbar", 12, "dim", bold=True, w=rw, h=16, anchor={"top": 4})))
    r2 = IV + "RqHr"
    ap.append(("#" + rr, G_.glass_group(r2, rw, IV_RS, layout="Left")))
    ap.append(("#" + r2, G_.glass_grid(IV + "Rh", 9, 1, drag=False, slot=IV_RS, icon=IV_RS - 8)))
    ap.append(("#" + r2, "Group { Anchor: (Width: 8); }"))
    ap.append(("#" + r2, G_.glass_button(IV + "RqK", "Keep slot", "secondary", w=110, h=32, size=13, anchor={"top": 6})))
    assert ghw + 8 + 110 <= rw, ("0.3.53: the hotbar row fits", ghw, rw)
    m2 = IV + "RmH"
    ap.append(("#" + rr, G_.glass_group(m2, rw, 16, layout="Left")))
    for k_ in range(9):
        ap.append(("#" + m2, lab(IV + "Mh%d" % k_, "", 11, "text", w=IV_RS, h=16, halign="Center", anchor={"right": SUI.GRID_SPACING} if k_ < 8 else None)))
    ap.append(("#" + rr, lab(IV + "RqI", "", 12, "text", w=rw, h=18, anchor={"top": 4})))
    r3 = IV + "RsRow"
    ap.append(("#" + rr, G_.glass_group(r3, rw, 40, layout="Left", anchor={"top": 4})))
    ap.append(("#" + r3, G_.glass_button(IV + "RsT", "Storage", "secondary", w=130, h=32, size=13, anchor={"top": 4})))
    gsw, _gsh = SUI.glass_grid_size(IV_RSN, 1, 40)
    ap.append(("#" + r3, G_.glass_grid(IV + "Rs", IV_RSN, 1, drag=False, slot=40, icon=32, anchor={"left": 6})))
    ap.append(("#" + r3, G_.glass_button(IV + "RsO", "Take out", "secondary", w=96, h=32, size=13, anchor={"left": 6, "top": 4})))
    assert 130 + 6 + gsw + 6 + 96 <= rw, ("0.3.53: the storage strip fits", gsw, rw)
    used = 16 + IV_RS + 16 + 4 + 16 + IV_RS + 16 + 4 + 18 + 4 + 40
    assert used <= bh and IV_RLMAX * 30 <= bh, ("0.3.53: the Requip body fits", used, bh)
    binds.extend([("#" + IV + "RqEq", "rqeq"), ("#" + IV + "RqSv", "rqsv"), ("#" + IV + "RqDn", "rqd"), ("#" + IV + "RqK", "rqk"),
                  ("#" + IV + "RsT", "rst"), ("#" + IV + "RsO", "rso")])
    # ======== 'q' the FULL Requip storage (the strip's title; README default "storage one row, full grid on its title")
    ap, binds = IV_PANELS["q"]
    pan = IV + "QPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    qa = IV + "QA"
    ap.append(("#" + pan, G_.glass_group(qa, pw, 34, layout="Left")))
    ap.append(("#" + qa, lab(IV + "QT", "", 16, "accentHi", bold=True, w=300, h=34)))
    sp = pw - 300 - 32 - 50 - 32 - 6 - 96 - 6 - 120
    assert sp >= 0, ("0.3.53: the storage header fits", sp)
    ap.append(("#" + qa, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + qa, G_.glass_button(IV + "QpP", "<", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + qa, lab(IV + "Qn", "", 13, "text", bold=True, w=50, h=32, halign="Center")))
    ap.append(("#" + qa, G_.glass_button(IV + "QpN", ">", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + qa, G_.glass_button(IV + "QO", "Take out", "secondary", w=96, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + qa, G_.glass_button(IV + "QB", "Show preset", "secondary", w=120, h=32, size=13, anchor={"left": 6})))
    qgw, qgh = SUI.glass_grid_size(IV_QC, IV_QR, IV_RS)
    assert qgw <= pw and 34 + 6 + qgh + 6 + 20 <= ph - 20, ("0.3.53: the storage grid fits", qgw, qgh)
    ap.append(("#" + pan, G_.glass_grid(IV + "Qg", IV_QC, IV_QR, drag=False, slot=IV_RS, icon=IV_RS - 8, anchor={"top": 6, "left": (pw - qgw) // 2})))
    ap.append(("#" + pan, lab(IV + "Qi", "", 12, "text", w=pw, h=20, anchor={"top": 6})))
    binds.extend([("#" + IV + "QpP", "qpp"), ("#" + IV + "QpN", "qpn"), ("#" + IV + "QO", "rso"), ("#" + IV + "QB", "rst")])
    # ======== 'p' ONE POCKET (research/ui-theme-art/inventory-mockup-mining.png)
    ap, binds = IV_PANELS["p"]
    pan = IV + "PPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    pa = IV + "PA"
    ap.append(("#" + pan, G_.glass_group(pa, pw, 34, layout="Left")))
    ap.append(("#" + pa, lab(IV + "PkT", "", 16, "accentHi", bold=True, w=220, h=34)))
    ap.append(("#" + pa, lab(IV + "PkL", "", 13, "dim", w=250, h=34)))
    ap.append(("#" + pa, G_.text_field(IV + "PqBox", IV + "Pq", w=140, h=30, placeholder="Search", max_length=24, size=13, anchor={"top": 2})))
    ap.append(("#" + pa, G_.glass_button(IV + "PqGo", "Search", "secondary", w=78, h=30, size=13, anchor={"left": 4, "top": 2})))
    assert 220 + 250 + 140 + 4 + 78 <= pw, "0.3.53: the pocket header fits"
    bh = ph - 20 - 34 - 6
    pb = IV + "PB"
    ap.append(("#" + pan, G_.glass_group(pb, pw, bh, layout="Left", anchor={"top": 6})))
    pgw, pgh = SUI.glass_grid_size(IV_PGC, IV_PGR, 46)
    pl_ = IV + "PL"
    ap.append(("#" + pb, G_.glass_group(pl_, pgw, bh, layout="Top")))
    ap.append(("#" + pl_, G_.glass_grid(IV + "Pg", IV_PGC, IV_PGR, drag=False, slot=46, icon=38)))
    pp = IV + "PP"
    ap.append(("#" + pl_, G_.glass_group(pp, pgw, 30, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pp, G_.glass_button(IV + "PpP", "<", "secondary", w=32, h=30, size=14)))
    ap.append(("#" + pp, lab(IV + "PpN", "", 13, "text", bold=True, w=56, h=30, halign="Center")))
    ap.append(("#" + pp, G_.glass_button(IV + "PpX", ">", "secondary", w=32, h=30, size=14)))
    ap.append(("#" + pp, G_.glass_button(IV + "Pf", "Enchanted only", "secondary", w=180, h=30, size=13, anchor={"left": 10})))
    ap.append(("#" + pp, G_.glass_button(IV + "PqX", "Clear", "secondary", w=70, h=30, size=13, anchor={"left": 6})))
    assert 32 + 56 + 32 + 10 + 180 + 6 + 70 <= pgw and pgh + 6 + 30 <= bh, ("0.3.53: the pocket grid + pager fit", pgw, pgh, bh)
    ap.append(("#" + pb, "Group { Anchor: (Width: 12); }"))
    dw = pw - pgw - 12
    pd = IV + "PD"
    ap.append(("#" + pb, G_.glass_group(pd, dw, bh, role="inset", layout="Top", pad=8)))
    dw2 = dw - 16
    ps = IV + "PsRow"
    ap.append(("#" + pd, G_.glass_group(ps, dw2, 56, layout="Left")))
    ap.append(("#" + ps, G_.glass_grid(IV + "Psl", 1, 1, drag=False, slot=56, icon=46)))
    pt = IV + "PsTx"
    ap.append(("#" + ps, G_.glass_group(pt, dw2 - 56 - 8, 56, layout="Top", anchor={"left": 8})))
    ap.append(("#" + pt, lab(IV + "PsN", "", 14, "title", bold=True, w=dw2 - 64, h=24)))
    ap.append(("#" + pt, lab(IV + "PsC", "", 12, "dim", w=dw2 - 64, h=30)))
    ap.append(("#" + pd, G_.text_field(IV + "PaBox", IV + "Pa", w=dw2, h=30, placeholder="Amount or all", max_length=12, size=13, anchor={"top": 6})))
    bw2 = (dw2 - 6) // 2
    for r_, ((i1, t1, k1), (i2, t2, k2)) in enumerate(((("Pw", "Withdraw", "primary"), ("Pd", "Deposit", "secondary")), (("Pl", "Sell", "secondary"), ("Pu", "Unpack", "secondary")))):
        row = IV + "PbR%d" % r_
        ap.append(("#" + pd, G_.glass_group(row, dw2, 32, layout="Left", anchor={"top": 6})))
        ap.append(("#" + row, G_.glass_button(IV + i1, t1, k1, w=bw2, h=32, size=13)))
        ap.append(("#" + row, G_.glass_button(IV + i2, t2, k2, w=bw2, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + pd, lab(IV + "Pr", "", 12, "text", w=dw2, h=bh - 16 - 56 - 36 - 76 - 8, anchor={"top": 6})))
    assert bh - 16 - 56 - 36 - 76 - 8 >= 36, ("0.3.53: the pocket result line has room", bh)
    binds.extend([("#" + IV + "PpP", "ppp"), ("#" + IV + "PpX", "ppn"), ("#" + IV + "Pf", "pf"), ("#" + IV + "PqX", "pqx")])


_inv_panels()
''')

# ---------- the checks + the page data: the shell ('-') then each panel's lines with its code
P.rep('''SUI.check_page(IV_AP, IV)
for _p, _mk in IV_AP:
    SUI.check_markup(_mk, prefix=IV, root=(_p is None), kit_paths=True)
SUI.assert_page_size(IV_PAGE_W, IV_PAGE_H)
_iv_tok = SUI.proven_tokens(IV_AP)
''', '''SUI.check_page(IV_AP, IV)
for _p, _mk in IV_AP:
    SUI.check_markup(_mk, prefix=IV, root=(_p is None), kit_paths=True)
SUI.assert_page_size(IV_PAGE_W, IV_PAGE_H)
_iv_shell_ids = set(i_ for _p, mk_ in IV_AP for i_ in SUI._static_ids(mk_))
for _c, (_pa, _pb) in IV_PANELS.items():   # 0.3.53: each panel on top of the shell (the holder #SkyyInvTopP is the shell's)
    SUI.check_page(_pa, IV, known_parents=["#" + x_ for x_ in _iv_shell_ids])
    for _p, _mk in _pa:
        SUI.check_markup(_mk, prefix=IV, kit_paths=True)
    _pids = set(i_ for _p, mk_ in _pa for i_ in SUI._static_ids(mk_))
    assert not (_pids & _iv_shell_ids), ("0.3.53: a panel id also in the shell", _c, _pids & _iv_shell_ids)
    for _s, _a in _pb:
        assert _s[1:] in _pids, ("0.3.53: a panel binding target", _c, _s)
_iv_tok = SUI.proven_tokens(list(IV_AP) + [x_ for _c in IV_PANELS for x_ in IV_PANELS[_c][0]])
''')
P.rep('''_iv_ids = set(i_ for _p, mk_ in IV_AP for i_ in SUI._static_ids(mk_))
for _s, _a in IV_BINDS:
    assert _s[1:] in _iv_ids, ("0.3.50: binding target", _s)
''', '''_iv_ids = set(i_ for _p, mk_ in list(IV_AP) + [x_ for _c in IV_PANELS for x_ in IV_PANELS[_c][0]] for i_ in SUI._static_ids(mk_))
for _s, _a in IV_BINDS:
    assert _s[1:] in _iv_shell_ids, ("0.3.50: binding target", _s)
''')
P.rep('''           "MntI", "MntN", "MntL", "NowL", "Tp") + tuple("Nq%d" % k_ for k_ in range(IV_NMAX)) + tuple("Sk%d" % k_ for k_ in range(IV_SKN)):   # skills, now, teleports
    assert IV + _g in _iv_ids, "0.3.50: the page has #" + IV + _g
IV_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9]+)?\\s*\\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in IV_AP)
assert IV_ELEMENTS <= 700, "0.3.52: the inventory page stays well under the ~1,600 element budget (%d + at most %d at run time)" % (IV_ELEMENTS, IV_BMAX + 4 * IV_NOWN)
IV_LK, IV_LP, IV_LB = [], [], []
for _p, _mk in IV_AP:
    IV_LK.append("A")
    IV_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    IV_LB.append(SUI.render(_mk))
for _i, _pr, _v in IV_AP.sets:
    IV_LK.append("S")
    IV_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    IV_LB.append(_v)
for _s, _a in IV_BINDS:
    IV_LK.append("E")
    IV_LP.append(_s)
    IV_LB.append(_a)
''', '''           "MntI", "MntN", "MntL", "NowL", "Tp") + tuple("Nq%d" % k_ for k_ in range(IV_NMAX)) + tuple("Sk%d" % k_ for k_ in range(IV_SKN)):   # skills, now, teleports
    assert IV + _g in _iv_ids, "0.3.50: the page has #" + IV + _g
for _g in ("RqP", "RqE", "Sum", "TopP", "Pk", "RqT", "RqL", "Ra", "Rh", "Rn", "RqI", "Rs", "RsT", "QT", "Qg", "Qn", "Qi", "PkT", "PkL", "Pq", "Pg",
           "PpN", "Pf", "Psl", "PsN", "PsC", "Pa", "Pr", "Pw", "Pd", "Pl", "Pu", "RnGo", "PqGo") + tuple("Ma%d" % k_ for k_ in range(6)) + tuple("Mh%d" % k_ for k_ in range(9)):
    assert IV + _g in _iv_ids, "0.3.53: the page has #" + IV + _g


def _elems(aps):
    return sum(len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9]+)?\\s*\\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in aps)
IV_SHELL_ELEMENTS = _elems(IV_AP)
IV_PANEL_ELEMENTS = dict((_c, _elems(IV_PANELS[_c][0])) for _c in IV_PANELS)
IV_RUNTIME_MAX = max(IV_BMAX, 2 * (1 + len(IV_PCATS)), IV_RLMAX) + IV_PMAX + 1 + len(IV_PCATS) + 1 + 4 * IV_NOWN   # bench tabs or list rows + presets + pocket tabs + Right now
IV_ELEMENTS = IV_SHELL_ELEMENTS + max(IV_PANEL_ELEMENTS.values())
assert IV_ELEMENTS <= 700, "0.3.53: the inventory page stays well under the ~1,600 element budget (%d static (shell %d + the biggest panel %s) + at most %d at run time)" % (IV_ELEMENTS, IV_SHELL_ELEMENTS, IV_PANEL_ELEMENTS, IV_RUNTIME_MAX)
IV_LK, IV_LP, IV_LB, IV_LC = [], [], [], []
for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p")]:
    for _p, _mk in _aps:
        IV_LK.append("A")
        IV_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
        IV_LB.append(SUI.render(_mk))
        IV_LC.append(_code)
    for _i, _pr, _v in _aps.sets:
        IV_LK.append("S")
        IV_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
        IV_LB.append(_v)
        IV_LC.append(_code)
    for _s, _a in _bnd:
        IV_LK.append("E")
        IV_LP.append(_s)
        IV_LB.append(_a)
        IV_LC.append(_code)
assert len(IV_LC) == len(IV_LK) and IV_LC[0] == "-" and IV_LK[0] == "A" and IV_LP[0] == "", "0.3.53: the page data starts with the root, one code per line"
''')
P.rep('''print("0.3.50 inventory page: %d elements (budget ~1,600), %d appends, %d b.set, %d bindings (+ grid events in Java), %d bytes markup, "''',
      '''print("0.3.53 inventory page: shell %d elements + panel %s (budget ~1,600; at most %d more at run time)" % (IV_SHELL_ELEMENTS, IV_PANEL_ELEMENTS, IV_RUNTIME_MAX))
print("0.3.50 inventory page: %d elements (budget ~1,600), %d appends, %d b.set, %d bindings (+ grid events in Java), %d bytes markup, "''')

# ---------- InvData: the panel codes + the run-time templates
P.rep('''F(idat, "public static final String[] LB = %s;" % jarr(IV_LB))
''', '''F(idat, "public static final String[] LB = %s;" % jarr(IV_LB))
F(idat, "public static final String LC = %s;" % jstr("".join(IV_LC)))   # 0.3.53: '-' shell, 'c' craft, 'r' Requip, 'q' Requip storage, 'p' pocket
for _n, _v in (("PMAX", IV_PMAX), ("PRESET_W", IV_PRESET_W), ("PK_W", IV_COL_M), ("RSN", IV_RSN), ("QN", IV_QC * IV_QR), ("PGN", IV_PGC * IV_PGR),
               ("RLMAX", IV_RLMAX)):
    F(idat, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("PRESET_BTN", IV_PRESET_BTN), ("PRESET_NONE", IV_PRESET_NONE), ("ST_P", IV_ST_P), ("ST_PSEL", IV_ST_PSEL), ("PK_BTN", IV_PK_BTN),
               ("RL_BTN", IV_RL_BTN), ("ST_RL", IV_ST_RL), ("ST_RLSEL", IV_ST_RLSEL), ("RQ_HELP", IV_TXT["rqHelp"]), ("PK_HELP", IV_TXT["pkHelp"]),
               ("Q_HELP", IV_TXT["qHelp"])):
    F(idat, "public static final String %s = %s;" % (_n, jstr(_v)))
F(idat, "public static final String[] PCATS = %s;" % jarr(IV_PCATS))
''')

# ---------- InvPage: the state of the swappable panel
P.rep('''           "public String[] cshown;", "public String cnote;", "public java.util.ArrayList cbenches;", "public String[] nowT;", "public int crafts;"):
    F(ipg, _f)''', '''           "public String[] cshown;", "public String cnote;", "public java.util.ArrayList cbenches;", "public String[] nowT;", "public int crafts;",
           # 0.3.53: the panel shown ("c" craft, "r" Requip, "q" Requip storage, "p" a pocket); Requip: the presets read this draw, the worn
           # one, the drawn preset buttons / list rows, the edited preset, the picked slot (0-12 gear, 13 pet, 14 mount), the slot data, the
           # storage entries drawn + the picked one, the full grid page, the last answer; pocket: the category, search, Enchanted only, page,
           # the ids drawn, the picked id, the last answer + amount, the pocket tabs on
           "public String mode;", "public String[] rlines;", "public int rworn;", "public int[] presetN;", "public int[] rlN;", "public int rsel;",
           "public int rslot;", "public String[] rmarks;", "public String[] rids;", "public String[] rtit;", "public String[] rsShown;",
           "public String rsSel;", "public int qpage;", "public String rnote;", "public String pcat;", "public String pquery;", "public boolean penc;",
           "public int ppage;", "public String[] pshown;", "public String psel;", "public String pnote;", "public String pamt;", "public boolean pkOn;",
           # fix pass: the preset list window (first row, rows per window, the "+ New preset" target) + the pocket list's profile token
           "public int rlTop;", "public int rlPer;", "public int rnew;", "public String pkey;"):
    F(ipg, _f)''')
P.rep('''  this.nowT = new String[0];
  this.crafts = 0;
}""")''', '''  this.nowT = new String[0];
  this.crafts = 0;
  this.mode = "c";
  this.rlines = null;
  this.rworn = -1;
  this.presetN = new int[0];
  this.rlN = new int[0];
  this.rsel = -1;
  this.rslot = -1;
  this.rmarks = new String[15];
  this.rids = new String[15];
  this.rtit = new String[15];
  this.rsShown = new String[0];
  this.rsSel = null;
  this.qpage = 0;
  this.rnote = "";
  this.pcat = "Mining";
  this.pquery = "";
  this.penc = false;
  this.ppage = 0;
  this.pshown = new String[0];
  this.psel = null;
  this.pnote = "";
  this.pamt = "";
  this.pkOn = false;
  this.rlTop = -1;
  this.rlPer = 1;
  this.rnew = -1;
  this.pkey = null;
}""")''')

# ---------- InvPage part 1: the new fills (before build)
FILLS = r'''# ---- 0.3.53: the presets row, the pocket tabs, the Requip panel, the full Requip storage, a pocket (bridge reads only, world thread)
M(ipg, r"""
public static String bare(String r) {
  if (r == null) return "";
  String t = r.trim();
  if (t.length() > 0 && (t.charAt(0) == '+' || t.charAt(0) == '-' || t.charAt(0) == '=')) return t.substring(1).trim();
  return t;
}""")
M(ipg, r"""
public static int toInt(String s, int d) {
  if (s == null) return d;
  try { return Integer.parseInt(s.trim()); } catch (Throwable t) { return d; }
}""")
M(ipg, r"""
public static long toLong(String s, long d) {
  if (s == null) return d;
  try { return Long.parseLong(s.trim()); } catch (Throwable t) { return d; }
}""")
M(ipg, r"""
public Object call(String key, Object arg) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null) return null;
  try { return f.apply(arg); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: " + key + " failed: " + t); return null; }
}""")
M(ipg, r"""
public String[] lines(String key, Object arg) {
  Object o = call(key, arg);
  if (!(o instanceof String)) return null;
  return ((String) o).split("\n");
}""")
M(ipg, r"""
public static String markWord(String m) {
  if (m == null) return "";
  if (m.equals("on")) return "on you";
  if (m.equals("stored")) return "stored";
  if (m.equals("missing")) return "missing";
  if (m.equals("pocket")) return "pocket";
  if (m.equals("empty")) return "empty";
  if (m.equals("none")) return "none";
  if (m.equals("gone")) return "gone";
  if (m.equals("set")) return "set";
  return "keep";
}""")
# fix pass: an id the server does not know (a pack mod taken out) is never put into a grid slot as an ItemStack - name only
M(ipg, r"""
public static boolean known(String id) {
  return id != null && id.length() > 0 && id.length() < 120 && @PKG@.InvCraft.item(id) != null;
}""")
# HANDOFF 2: a NEW ItemStack(id, 1) - never metadata; a missing piece is drawn uncraftable (greyed)
M(ipg, r"""
public static @IGS@ rqSlot(String id, String title, String m) {
  @IGS@ g = new @IGS@();
  if (id != null && id.length() > 0 && id.length() < 120) {
    if (known(id)) g.setItemStack(new @IS@(id, 1));
    g.setName(@PKG@.InvCraft.name(id));
    g.setDescription((title == null ? "" : title + " - ") + markWord(m));
    if ("missing".equals(m) || "gone".equals(m)) g.setItemUncraftable(true);
  }
  return g;
}""")
# THE PRESETS ROW (requip:fn:presets): the first PMAX presets, the worn one selected; one click = Equip
M(ipg, r"""
public void fillPresets(@UCB@ b, @UEB@ ev) {
  String[] ls = lines("requip:fn:presets", this.playerRef.getUuid());
  this.rlines = ls;
  this.rworn = -1;
  java.util.ArrayList ns = new java.util.ArrayList();
  if (ls != null && ls.length > 0 && ls[0].startsWith("ok|")) {
    String[] h = ls[0].split("\\|", -1);
    this.rworn = h.length > 1 ? toInt(h[1], -1) : -1;
    for (int i = 1; i < ls.length; i++) { String[] f = ls[i].split("\\|", -1); if (f.length >= 6) ns.add(f); }
  }
  int shown = ns.size() < @PKG@.InvData.PMAX ? ns.size() : @PKG@.InvData.PMAX;
  this.presetN = new int[shown];
  if (shown == 0) {
    b.appendInline("#SkyyInvRqP", @PKG@.InvData.PRESET_NONE);
    String why = ls == null ? "Requip presets are not on this server" : (ls.length > 0 && ls[0].startsWith("off|") ? ls[0].substring(4) : "No presets yet");
    b.set("#SkyyInvRpE.Text", why);
    return;
  }
  int w = (@PKG@.InvData.PRESET_W - 2 * shown) / shown;
  for (int i = 0; i < shown; i++) {
    String[] f = (String[]) ns.get(i);
    int n = toInt(f[0], -1);
    this.presetN[i] = n;
    b.appendInline("#SkyyInvRqP", @PKG@.InvData.PRESET_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(w)).replace("{S}", n == this.rworn ? @PKG@.InvData.ST_PSEL : @PKG@.InvData.ST_P));
    b.set("#SkyyInvRp" + i + ".Text", f[1]);
    ev.addEventBinding(@BT@.Activating, "#SkyyInvRp" + i, @EVD@.of("a", "rp:" + i));
  }
}""")
# THE POCKET TABS: Craft + SkyySacks 0.8.38's six pockets, or Craft | Void without its pocket bridge
M(ipg, r"""
public void fillPockets(@UCB@ b, @UEB@ ev) {
  boolean pk = @PKG@.InvCraft.fn("sacks:fn:pocketList") != null && @PKG@.InvCraft.fn("sacks:fn:pocket") != null;
  this.pkOn = pk;
  int n = pk ? 1 + @PKG@.InvData.PCATS.length : 2;
  int w = (@PKG@.InvData.PK_W - 2 * n) / n;
  if (w > 150) w = 150;
  for (int i = 0; i < n; i++) {
    String lb = i == 0 ? "Craft" : (pk ? @PKG@.InvData.PCATS[i - 1] : "Void");
    boolean sel = i == 0 ? this.mode.equals("c") : (pk && this.mode.equals("p") && @PKG@.InvData.PCATS[i - 1].equals(this.pcat));
    b.appendInline("#SkyyInvPk", @PKG@.InvData.PK_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(w)).replace("{S}", sel ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvPt" + i + ".Text", lb);
    ev.addEventBinding(@BT@.Activating, "#SkyyInvPt" + i, @EVD@.of("a", "pt:" + i));
  }
}""")
# the Requip storage entries (wardrobe:fn:list, IN gear only): { eid, item id }
M(ipg, r"""
public java.util.ArrayList storeList() {
  java.util.ArrayList out = new java.util.ArrayList();
  Object o = call("wardrobe:fn:list", new Object[] { this.playerRef.getUuid(), "all" });
  if (!(o instanceof Object[])) return out;
  Object[] a = (Object[]) o;
  for (int i = 0; i < a.length; i++) {
    if (!(a[i] instanceof Object[])) continue;
    Object[] e = (Object[]) a[i];
    if (e.length < 2 || !(e[0] instanceof String) || !(e[1] instanceof String)) continue;
    out.add(new String[] { (String) e[0], (String) e[1] });
  }
  return out;
}""")
M(ipg, r"""
public static @IGS@ storeSlot(String[] e, String picked) {
  @IGS@ g = new @IGS@();
  if (e == null || e[1].length() == 0 || e[1].length() >= 120) return g;
  if (known(e[1])) g.setItemStack(new @IS@(e[1], 1));
  g.setName(@PKG@.InvCraft.name(e[1]) + (e[0].equals(picked) ? "  (picked)" : ""));
  return g;
}""")
M(ipg, r"""
public @IGS@ petSlot(int k) {
  @IGS@ g = new @IGS@();
  String m = this.rmarks[k];
  String ic = this.rids[k];
  if (("set".equals(m) || "gone".equals(m)) && ic != null && ic.length() > 0 && ic.length() < 120) {
    if (known(ic)) g.setItemStack(new @IS@(ic, 1));
    g.setName(this.rtit[k] == null || this.rtit[k].length() == 0 ? (k == 13 ? "Pet" : "Mount") : this.rtit[k]);
    if ("gone".equals(m)) g.setItemUncraftable(true);
  }
  return g;
}""")
# THE REQUIP PANEL ('r'): the preset list, the picked preset's slots + marks, the hint, the storage strip
M(ipg, r"""
public void fillRequip(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  String[] ls = this.rlines;
  java.util.ArrayList rows = new java.util.ArrayList();
  if (ls != null && ls.length > 0 && ls[0].startsWith("ok|")) for (int i = 1; i < ls.length; i++) { String[] f = ls[i].split("\\|", -1); if (f.length >= 6) rows.add(f); }
  boolean found = false;
  int at = -1;
  for (int i = 0; i < rows.size(); i++) if (toInt(((String[]) rows.get(i))[0], -1) == this.rsel) { found = true; at = i; }
  if (!found) {
    this.rsel = this.rworn >= 0 ? this.rworn : (rows.size() > 0 ? toInt(((String[]) rows.get(0))[0], 0) : 0);
    for (int i = 0; i < rows.size(); i++) if (toInt(((String[]) rows.get(i))[0], -1) == this.rsel) at = i;
  }
  // fix pass: the list pages (a "More" row when the presets do not fit) + "+ New preset" = the first unused custom loadout (6+, nothing picked)
  this.rnew = -1;
  for (int i = 0; i < rows.size(); i++) { String[] f = (String[]) rows.get(i); int n = toInt(f[0], -1); if (this.rnew < 0 && n >= 5 && toInt(f[2], 1) == 0 && n != this.rworn) this.rnew = n; }
  int cap = @PKG@.InvData.RLMAX - 1;
  boolean more = rows.size() > cap;
  int per = more ? cap - 1 : cap;
  this.rlPer = per;
  if (this.rlTop < 0 || this.rlTop >= rows.size()) this.rlTop = at >= 0 ? (at / per) * per : 0;
  int nl = rows.size() - this.rlTop < per ? rows.size() - this.rlTop : per;
  if (nl < 0) nl = 0;
  int tot = nl + (more ? 1 : 0) + 1;
  this.rlN = new int[tot];
  for (int i = 0; i < tot; i++) {
    String tx;
    int n;
    if (i < nl) {
      String[] f = (String[]) rows.get(this.rlTop + i);
      n = toInt(f[0], -1);
      int miss = toInt(f[3], 0);
      tx = f[1] + (n == this.rworn ? "  - worn" : (miss > 0 ? "  - " + miss + " miss" : ""));
    } else if (more && i == nl) {
      n = -2;
      tx = "More  (" + (this.rlTop / per + 1) + " / " + ((rows.size() + per - 1) / per) + ")";
    } else {
      n = -3;
      tx = "+ New preset";
    }
    this.rlN[i] = n;
    b.appendInline("#SkyyInvRqL", @PKG@.InvData.RL_BTN.replace("{I}", String.valueOf(i)).replace("{S}", n >= 0 && n == this.rsel ? @PKG@.InvData.ST_RLSEL : @PKG@.InvData.ST_RL));
    b.set("#SkyyInvRl" + i + ".Text", tx);
    ev.addEventBinding(@BT@.Activating, "#SkyyInvRl" + i, @EVD@.of("a", "rl:" + i));
  }
  String[] d = lines("requip:fn:preset", new Object[] { u, Integer.valueOf(this.rsel) });
  this.rmarks = new String[15];
  this.rids = new String[15];
  this.rtit = new String[15];
  String title = "REQUIP";
  String hint = "";
  int miss = 0;
  int sto = 0;
  String firstMiss = null;
  if (d == null) hint = ls == null ? "Requip is not on this server right now" : (ls.length > 0 && ls[0].startsWith("off|") ? ls[0].substring(4) : "Requip did not answer");
  else if (!d[0].startsWith("ok|")) hint = d[0].startsWith("off|") ? d[0].substring(4) : "Requip did not answer";
  else {
    String[] h = d[0].split("\\|", -1);
    title = "REQUIP - " + (h.length > 2 ? h[2].toUpperCase() : "") + (h.length > 3 && "1".equals(h[3]) ? "  (WORN)" : "");
    for (int i = 1; i < d.length; i++) {
      String[] f = d[i].split("\\|", -1);
      if (f.length < 4) continue;
      int k = f[0].equals("pet") ? 13 : (f[0].equals("mount") ? 14 : toInt(f[0], -1));
      if (k < 0 || k > 14) continue;
      this.rmarks[k] = f[1];
      this.rids[k] = f[2];
      this.rtit[k] = k == 13 ? (f[3].length() > 0 ? f[3] : "Pet") : (k == 14 ? (f[3].length() > 0 ? f[3] : "Mount") : f[3]);
      if (k < 13 && "missing".equals(f[1])) { miss = miss + 1; if (firstMiss == null) firstMiss = f[3] + (f[2].length() > 0 ? " (" + @PKG@.InvCraft.name(f[2]) + ")" : ""); }
      if (k < 13 && "stored".equals(f[1])) sto = sto + 1;
    }
  }
  java.util.ArrayList ra = new java.util.ArrayList();
  java.util.ArrayList rh = new java.util.ArrayList();
  for (int k = 0; k < 4; k++) ra.add(rqSlot(this.rids[k], this.rtit[k], this.rmarks[k]));
  ra.add(petSlot(13));
  ra.add(petSlot(14));
  for (int k = 4; k < 13; k++) rh.add(rqSlot(this.rids[k], this.rtit[k], this.rmarks[k]));
  b.set("#SkyyInvRa.Slots", ra);
  b.set("#SkyyInvRh.Slots", rh);
  for (int k = 0; k < 6; k++) {
    int s = k < 4 ? k : 9 + k;
    String w = this.rmarks[s] == null ? "" : (k < 4 ? markWord(this.rmarks[s]) : (k == 4 ? "pet " : "mount ") + markWord(this.rmarks[s]));
    b.set("#SkyyInvMa" + k + ".Text", (s == this.rslot && w.length() > 0 ? "> " : "") + w);
  }
  for (int k = 0; k < 9; k++) {
    String w = this.rmarks[4 + k] == null ? "" : markWord(this.rmarks[4 + k]);
    b.set("#SkyyInvMh" + k + ".Text", (4 + k == this.rslot && w.length() > 0 ? "> " : "") + w);
  }
  if (this.rnote.length() > 0) hint = this.rnote;
  else if (hint.length() == 0) {
    if (this.rslot >= 0 && this.rslot < 15 && this.rmarks[this.rslot] != null) {
      String id = this.rids[this.rslot];
      hint = this.rtit[this.rslot] + ": " + (this.rslot < 13 && id != null && id.length() > 0 ? @PKG@.InvCraft.name(id) + " - " : "") + markWord(this.rmarks[this.rslot])
          + (this.rslot < 13 ? " - drag an item here to change it, Keep slot = what you wear" : " - set pets on the Pets tab");
    }
    else if (miss > 0) hint = miss + " missing - " + firstMiss + " is not with you or in Requip storage";
    else if (sto > 0) hint = sto + (sto == 1 ? " piece waits" : " pieces wait") + " in Requip storage - Equip brings them to you";
    else hint = @PKG@.InvData.RQ_HELP;
  }
  this.rnote = "";
  b.set("#SkyyInvRqT.Text", title);
  b.set("#SkyyInvRqI.Text", hint);
  java.util.ArrayList ents = storeList();
  int ns = @PKG@.InvData.RSN;
  int pi = -1;
  for (int i = 0; i < ents.size(); i++) if (((String[]) ents.get(i))[0].equals(this.rsSel)) pi = i;
  if (pi < 0) this.rsSel = null;
  int st0 = pi >= ns ? pi - ns + 1 : 0;
  java.util.ArrayList rs = new java.util.ArrayList();
  this.rsShown = new String[ns];
  for (int i = 0; i < ns; i++) {
    String[] e = null;
    if (st0 + i < ents.size()) e = (String[]) ents.get(st0 + i);
    rs.add(storeSlot(e, this.rsSel));
    this.rsShown[i] = e == null ? null : e[0];
  }
  b.set("#SkyyInvRs.Slots", rs);
  b.set("#SkyyInvRsT.Text", "Storage " + ents.size());
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvRa", @EVD@.of("a", "rs:a"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvRh", @EVD@.of("a", "rs:h"), false);
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvRa", @EVD@.of("a", "rd:a"), false);
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvRh", @EVD@.of("a", "rd:h"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvRs", @EVD@.of("a", "rss"), false);
  String rk = String.valueOf((char) 64) + "R";
  ev.addEventBinding(@BT@.Validating, "#SkyyInvRn", @EVD@.of("a", "rn").append(rk, "#SkyyInvRn.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyInvRnGo", @EVD@.of("a", "rn").append(rk, "#SkyyInvRn.Value"));
}""")
# THE FULL REQUIP STORAGE ('q'): 12 x 4 per page; click = pick, Take out
M(ipg, r"""
public void fillStore(@UCB@ b, @UEB@ ev) {
  java.util.ArrayList ents = storeList();
  int per = @PKG@.InvData.QN;
  int np = ents.size() == 0 ? 1 : (ents.size() + per - 1) / per;
  if (this.qpage >= np) this.qpage = np - 1;
  if (this.qpage < 0) this.qpage = 0;
  boolean has = false;
  for (int i = 0; i < ents.size(); i++) if (((String[]) ents.get(i))[0].equals(this.rsSel)) has = true;
  if (!has) this.rsSel = null;
  java.util.ArrayList sl = new java.util.ArrayList();
  this.rsShown = new String[per];
  String pickedName = null;
  for (int k = 0; k < per; k++) {
    int at = this.qpage * per + k;
    String[] e = null;
    if (at < ents.size()) e = (String[]) ents.get(at);
    sl.add(storeSlot(e, this.rsSel));
    this.rsShown[k] = e == null ? null : e[0];
  }
  for (int i = 0; i < ents.size(); i++) { String[] e = (String[]) ents.get(i); if (e[0].equals(this.rsSel)) pickedName = @PKG@.InvCraft.name(e[1]); }
  b.set("#SkyyInvQg.Slots", sl);
  b.set("#SkyyInvQT.Text", "REQUIP STORAGE - " + ents.size() + (ents.size() == 1 ? " item" : " items"));
  b.set("#SkyyInvQn.Text", (this.qpage + 1) + " / " + np);
  b.set("#SkyyInvQi.Text", this.rnote.length() > 0 ? this.rnote : (pickedName != null ? "Picked: " + pickedName + " - Take out puts it in your bag" : @PKG@.InvData.Q_HELP));
  this.rnote = "";
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvQg", @EVD@.of("a", "rss"), false);
}""")
# ONE POCKET ('p'): sacks:fn:pocketList - the real counts on the icons, search, Enchanted only, pages, the picked item; the actions are bound
# here because they carry the amount box
M(ipg, r"""
public void fillPocket(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  String[] ls = lines("sacks:fn:pocketList", new Object[] { u, this.pcat });
  String info = "";
  java.util.ArrayList rows = new java.util.ArrayList();
  String[] pick = null;
  if (ls == null) info = "The pockets are not on this server right now";
  else if (!ls[0].startsWith("ok|")) info = ls[0].startsWith("off|") ? ls[0].substring(4) : "The Void did not answer";
  else {
    String[] h = ls[0].split("\\|", -1);
    String tk = h.length >= 8 ? h[7] : null;
    if (tk != null && this.pkey != null && !tk.equals(this.pkey) && this.psel != null) { this.psel = null; this.pnote = "Your profile changed - this pocket now shows it; pick the item again"; }
    this.pkey = tk;
    if (h.length >= 6) info = "Lv " + h[2] + "  -  " + h[3] + "  -  " + @PKG@.MenuUtil.fmt(toLong(h[4], 0L)) + " / " + @PKG@.MenuUtil.fmt(toLong(h[5], 0L));
    String q = this.pquery.toLowerCase();
    for (int i = 1; i < ls.length; i++) {
      String[] f = ls[i].split("\\|", -1);
      if (f.length < 4 || f[0].length() == 0) continue;
      if (f[0].equals(this.psel)) pick = f;
      if (this.penc && !"1".equals(f[2])) continue;
      if (q.length() > 0 && @PKG@.InvCraft.name(f[0]).toLowerCase().indexOf(q) < 0 && f[0].toLowerCase().indexOf(q) < 0) continue;
      rows.add(f);
    }
  }
  if (pick == null) this.psel = null;
  int per = @PKG@.InvData.PGN;
  int np = rows.size() == 0 ? 1 : (rows.size() + per - 1) / per;
  if (this.ppage >= np) this.ppage = np - 1;
  if (this.ppage < 0) this.ppage = 0;
  java.util.ArrayList sl = new java.util.ArrayList();
  this.pshown = new String[per];
  for (int k = 0; k < per; k++) {
    @IGS@ g = new @IGS@();
    int at = this.ppage * per + k;
    if (at < rows.size()) {
      String[] f = (String[]) rows.get(at);
      long c = toLong(f[1], 0L);
      if (f[0].length() < 120) {
        int ms = @PKG@.InvCraft.maxStack(f[0]);   // the icon number tops out at a full stack (no probe yet for bigger ones); the exact count is in the name + the detail
        if (known(f[0])) g.setItemStack(new @IS@(f[0], (int) (c > (long) ms ? (long) ms : (c < 1L ? 1L : c))));
        g.setName(@PKG@.InvCraft.name(f[0]) + "  -  " + @PKG@.MenuUtil.fmt(c) + " in the Void");
      }
      this.pshown[k] = f[0];
    }
    sl.add(g);
  }
  java.util.ArrayList one = new java.util.ArrayList();
  @IGS@ pg = new @IGS@();
  String pn = "Pick an item";
  String pc = "";
  if (pick != null && pick[0].length() < 120) {
    if (known(pick[0])) pg.setItemStack(new @IS@(pick[0], 1));
    pn = @PKG@.InvCraft.name(pick[0]);
    long pr = toLong(pick[3], -1L);
    pc = "In the Void: " + @PKG@.MenuUtil.fmt(toLong(pick[1], 0L)) + (pr > 0L ? "  -  the Bazaar pays about " + @PKG@.MenuUtil.fmt(pr) + " each" : "") + ("1".equals(pick[2]) ? "  -  can unpack" : "");
  }
  one.add(pg);
  b.set("#SkyyInvPg.Slots", sl);
  b.set("#SkyyInvPsl.Slots", one);
  b.set("#SkyyInvPkT.Text", this.pcat.toUpperCase() + " POCKET");
  b.set("#SkyyInvPkL.Text", info);
  b.set("#SkyyInvPpN.Text", (this.ppage + 1) + " / " + np);
  b.set("#SkyyInvPf.Text", this.penc ? "Enchanted only - On" : "Enchanted only - Off");
  b.set("#SkyyInvPsN.Text", pn);
  b.set("#SkyyInvPsC.Text", pc);
  b.set("#SkyyInvPr.Text", this.pnote.length() > 0 ? this.pnote : @PKG@.InvData.PK_HELP);
  if (this.pquery.length() > 0) b.set("#SkyyInvPq.Value", this.pquery);
  if (this.pamt.length() > 0) b.set("#SkyyInvPa.Value", this.pamt);
  this.pnote = "";
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvPg", @EVD@.of("a", "pgs"), false);
  String sk = String.valueOf((char) 64) + "S";
  String ak = String.valueOf((char) 64) + "A";
  ev.addEventBinding(@BT@.Validating, "#SkyyInvPq", @EVD@.of("a", "pq").append(sk, "#SkyyInvPq.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyInvPqGo", @EVD@.of("a", "pq").append(sk, "#SkyyInvPq.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyInvPw", @EVD@.of("a", "po:wd").append(ak, "#SkyyInvPa.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyInvPd", @EVD@.of("a", "po:dep").append(ak, "#SkyyInvPa.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyInvPl", @EVD@.of("a", "po:sell").append(ak, "#SkyyInvPa.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyInvPu", @EVD@.of("a", "po:unpack").append(ak, "#SkyyInvPa.Value"));
}""")
'''
P.rep('''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''', FILLS + '''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''')
# build(): the shell + the current panel only; the panel's own fill + bindings
P.rep('''  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.InvData.LP[i];''', '''  char pm = this.mode.length() > 0 ? this.mode.charAt(0) : 'c';
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    char pc = @PKG@.InvData.LC.charAt(i);
    if (pc != '-' && pc != pm) continue;
    String x = @PKG@.InvData.LP[i];''')
P.rep('''  try { fillCraft(b, ev, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the craft panel failed: " + t); }
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvCg", @EVD@.of("a", "cr"), false);
''', '''  try { fillPresets(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the presets row failed: " + t); }
  try { fillPockets(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the pocket tabs failed: " + t); }
  if (pm == 'r') { try { fillRequip(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Requip panel failed: " + t); } }
  else if (pm == 'q') { try { fillStore(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Requip storage failed: " + t); } }
  else if (pm == 'p') { try { fillPocket(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the pocket panel failed: " + t); } }
  else {
    try { fillCraft(b, ev, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the craft panel failed: " + t); }
    ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvCg", @EVD@.of("a", "cr"), false);
    String qk0 = String.valueOf((char) 64) + "Q";
    ev.addEventBinding(@BT@.Validating, "#SkyyInvCq", @EVD@.of("a", "cq").append(qk0, "#SkyyInvCq.Value"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyInvCqGo", @EVD@.of("a", "cq").append(qk0, "#SkyyInvCq.Value"));
  }
''')
P.rep('''  String qk = String.valueOf((char) 64) + "Q";
  ev.addEventBinding(@BT@.Validating, "#SkyyInvCq", @EVD@.of("a", "cq").append(qk, "#SkyyInvCq.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyInvCqGo", @EVD@.of("a", "cq").append(qk, "#SkyyInvCq.Value"));
  listen();''', '''  listen();''')

# ---------- InvPage part 2: the Tanning tab through SkyySacks 0.8.38's own door
P.rep('''  if (bk.equals("Tannery")) { openHub("smithing", "recipes", "the Crafting page - pick its Tannery tab"); return; }''',
      '''  if (bk.equals("Tannery")) { tanning(); return; }''')
ACTIONS = r'''# 0.3.53: the Tanning tab = sacks:fn:openTannery (SkyySacks 0.8.38: the pack's own Tannery page); FALSE / missing = the Crafting page as 0.3.52
M(ipg, r"""
public void tanning() {
  this.answered = true;
  java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");
  Object o = null;
  try { if (f != null) o = f.apply(this.playerRef.getUuid()); } catch (Throwable t) { o = null; @PKG@.MenuUtil.warn("inventory: opening the Tannery failed: " + t); }
  if (Boolean.TRUE.equals(o)) {
    if (!still()) { finish("bridge Tannery"); return; }
    say("Opening the Tannery");
    return;
  }
  openHub("smithing", "recipes", "the Crafting page - pick its Tannery tab");
}""")
'''
P.rep('''M(ipg, r"""
public void bench(int i) {''', ACTIONS + '''M(ipg, r"""
public void bench(int i) {''')
ACTIONS2 = r'''# ---- 0.3.53: Requip + pocket + Summon actions (each answers with ONE packet: redraw or say)
M(ipg, r"""
public String rqAct(String op, int n, String arg) {
  Object o = call("requip:fn:act", new Object[] { this.playerRef.getUuid(), op, Integer.valueOf(n), arg == null ? "" : arg });
  if (o == null) return @PKG@.InvCraft.fn("requip:fn:act") == null ? "Requip presets are not on this server right now" : "Requip could not do that here - nothing changed";
  return bare(String.valueOf(o));
}""")
M(ipg, r"""
public void presetEquip(int i) {
  if (this.presetN == null || i < 0 || i >= this.presetN.length) { say("No such preset"); return; }
  int n = this.presetN[i];
  String r = rqAct("equip", n, "");
  this.rsel = n;
  if (this.mode.equals("r")) this.rnote = r;
  this.tcap = r;
  redraw();
}""")
M(ipg, r"""
public void editRequip() {
  if (@PKG@.InvCraft.fn("requip:fn:preset") == null || @PKG@.InvCraft.fn("requip:fn:presets") == null) { say("Requip presets are not on this server right now"); return; }
  this.mode = "r";
  if (this.rsel < 0) this.rsel = this.rworn;
  this.rslot = -1;
  this.rlTop = -1;
  redraw();
}""")
M(ipg, r"""
public void rqList(int i) {
  if (this.rlN == null || i < 0 || i >= this.rlN.length) { say("No such preset"); return; }
  int n = this.rlN[i];
  if (n == -2) { this.rlTop = this.rlTop + this.rlPer; if (this.rlTop >= (this.rlines == null ? 0 : this.rlines.length - 1)) this.rlTop = 0; redraw(); return; }
  if (n == -3) {
    if (this.rnew < 0) { this.rnote = "Every preset is in use - pick one and Save what I wear to replace it"; redraw(); return; }
    this.rsel = this.rnew;
    this.rslot = -1;
    this.rlTop = -1;
    this.rnote = "New preset: wear what you want in it, then Save what I wear - and Rename it";
    redraw();
    return;
  }
  this.rsel = n;
  this.rslot = -1;
  redraw();
}""")
M(ipg, r"""
public void rqDo(String op, String arg) {
  this.rnote = rqAct(op, this.rsel, arg);
  redraw();
}""")
M(ipg, r"""
public void rqSlotPick(String g, int si) {
  int k = -1;
  if ("a".equals(g) && si >= 0 && si < 6) k = si < 4 ? si : 9 + si;
  if ("h".equals(g) && si >= 0 && si < 9) k = 4 + si;
  if (k < 0) { say("That slot is not part of the preset"); return; }
  this.rslot = this.rslot == k ? -1 : k;
  redraw();
}""")
M(ipg, r"""
public void rqKeep() {
  if (this.rslot < 0 || this.rslot > 12) { this.rnote = "Pick an armour or hotbar slot of the preset first"; redraw(); return; }
  rqDo("keep", String.valueOf(this.rslot));
}""")
# a bag / hotbar / armour item dropped on a preset slot = saved at once (SkyyWardrobe 0.2.14 checks first, then its own deposit + pick)
M(ipg, r"""
public void rqDrop(String d, String g) {
  int si = ival(d, "SlotIndex", -1);
  int csec = ival(d, "SourceInventorySectionId", 999);
  int cslot = ival(d, "SourceSlotId", -1);
  String expect = val(d, "ItemStackId");
  int sec = csec;
  int slot = cslot;
  if ((sec == 999 || slot < 0) && this.dg != null) { sec = sectionOf(this.dg); slot = this.ds; }
  if (expect == null) expect = this.di;
  clearDrag();
  if ("a".equals(g) && (si == 4 || si == 5)) { this.rnote = "Pets and mounts are set on the Pets tab - then Save what I wear"; redraw(); return; }
  int k = "a".equals(g) ? si : 4 + si;
  if (k < 0 || k > 12) { this.rnote = "Drop it on an armour or hotbar slot of the preset"; redraw(); return; }
  String word = sec == @INVC@.STORAGE_SECTION_ID ? "storage" : (sec == @INVC@.HOTBAR_SECTION_ID ? "hotbar" : (sec == @INVC@.ARMOR_SECTION_ID ? "armor" : null));
  if (word == null || slot < 0) { this.rnote = "Drag the item from your bag, hotbar or armour"; redraw(); return; }
  String key = "rd:" + word + ":" + slot + ">" + this.rsel + ":" + k;
  if (dup(key)) { this.rnote = "Done"; redraw(); return; }
  moved(key);
  this.rslot = k;
  rqDo("drop", k + "|" + word + ":" + slot + ":" + (expect == null ? "" : expect));
}""")
M(ipg, r"""
public void rqPickStore(int si) {
  if (this.rsShown == null || si < 0 || si >= this.rsShown.length || this.rsShown[si] == null) { say("That slot is empty"); return; }
  this.rsSel = this.rsShown[si].equals(this.rsSel) ? null : this.rsShown[si];
  redraw();
}""")
M(ipg, r"""
public void rqTake() {
  if (this.rsSel == null) { this.rnote = "Pick an item in Requip storage first"; redraw(); return; }
  this.rnote = rqAct("take", -1, this.rsSel);
  this.rsSel = null;
  redraw();
}""")
M(ipg, r"""
public void pocketTab(int i) {
  if (i == 0) { this.mode = "c"; redraw(); return; }
  if (!this.pkOn) { openHub("storage", "pocket", "the Void"); return; }
  if (i < 1 || i > @PKG@.InvData.PCATS.length) { say("No such pocket"); return; }
  String c = @PKG@.InvData.PCATS[i - 1];
  if (!c.equals(this.pcat) || !this.mode.equals("p")) { this.psel = null; this.ppage = 0; this.pquery = ""; this.penc = false; }
  this.pcat = c;
  this.mode = "p";
  redraw();
}""")
M(ipg, r"""
public void pocketPick(int si) {
  if (this.pshown == null || si < 0 || si >= this.pshown.length || this.pshown[si] == null) { say("That slot is empty"); return; }
  this.psel = this.pshown[si];
  redraw();
}""")
M(ipg, r"""
public void pocketAct(String op, String amt) {
  String a = amt == null ? "" : amt.trim();
  if (a.length() > 12) a = a.substring(0, 12);
  this.pamt = a;
  if (this.psel == null) { this.pnote = "Pick an item in the grid first"; redraw(); return; }
  Object o = call("sacks:fn:pocket", this.pkey == null ? new Object[] { this.playerRef.getUuid(), op, this.psel, a } : new Object[] { this.playerRef.getUuid(), op, this.psel, a, this.pkey });
  this.pnote = o == null ? "The pockets are not on this server right now - nothing moved" : bare(String.valueOf(o));
  if (o != null && String.valueOf(o).startsWith("-Your profile changed")) this.psel = null;
  redraw();
}""")
M(ipg, r"""
public void summon() {
  this.answered = true;
  Object o = call("pets:fn:ride", this.playerRef.getUuid());
  say(o == null ? (@PKG@.InvCraft.fn("pets:fn:ride") == null ? "The mount button is not on this server right now" : "Your mount could not come right now") : bare(String.valueOf(o)));
}""")
'''
P.rep('''M(ipg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', ACTIONS2 + '''M(ipg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
# the events: Requip / pocket / Summon (the old Open Requip + Void buttons are gone; "rq" / "pkv" still answer for an old client page)
P.rep('''    if (a.equals("pkc")) { say("You are on Craft"); return; }
    if (a.equals("pkv")) { openHub("storage", "pocket", "the Void"); return; }
    if (a.equals("rq")) { openFn("requip:fn:open", "wardrobe:fn:open", "Requip"); return; }
''', '''    if (a.equals("pkc")) { say("You are on Craft"); return; }
    if (a.equals("pkv")) { openHub("storage", "pocket", "the Void"); return; }
    // 0.3.53: Requip inside the inventory (no jump to the old Requip page), the pockets, the mount
    if (a.equals("rq") || a.equals("rqe")) { editRequip(); return; }
    if (a.startsWith("rp:")) { presetEquip(toInt(a.substring(3), -1)); return; }
    if (a.startsWith("rl:")) { rqList(toInt(a.substring(3), -1)); return; }
    if (a.equals("rqeq")) { rqDo("equip", ""); return; }
    if (a.equals("rqsv")) { rqDo("worn", ""); return; }
    if (a.equals("rn")) { String nm = val(d, String.valueOf((char) 64) + "R"); nm = nm == null ? "" : nm.trim(); if (nm.length() > 24) nm = nm.substring(0, 24); rqDo("rename", nm); return; }
    if (a.equals("rqk")) { rqKeep(); return; }
    if (a.equals("rqd")) { this.mode = "c"; this.rslot = -1; redraw(); return; }
    if (a.startsWith("rs:")) { rqSlotPick(a.substring(3), ival(d, "SlotIndex", -1)); return; }
    if (a.startsWith("rd:")) { rqDrop(d, a.substring(3)); return; }
    if (a.equals("rss")) { rqPickStore(ival(d, "SlotIndex", -1)); return; }
    if (a.equals("rso")) { rqTake(); return; }
    if (a.equals("rst")) { this.mode = this.mode.equals("q") ? "r" : "q"; this.qpage = 0; redraw(); return; }
    if (a.equals("qpp")) { this.qpage = this.qpage - 1; redraw(); return; }
    if (a.equals("qpn")) { this.qpage = this.qpage + 1; redraw(); return; }
    if (a.startsWith("pt:")) { pocketTab(toInt(a.substring(3), -1)); return; }
    if (a.equals("pgs")) { pocketPick(ival(d, "SlotIndex", -1)); return; }
    if (a.equals("pq")) { this.pquery = @PKG@.InvCraft.clean(val(d, String.valueOf((char) 64) + "S")); this.ppage = 0; redraw(); return; }
    if (a.equals("pqx")) { this.pquery = ""; this.ppage = 0; redraw(); return; }
    if (a.equals("pf")) { this.penc = !this.penc; this.ppage = 0; redraw(); return; }
    if (a.equals("ppp")) { this.ppage = this.ppage - 1; redraw(); return; }
    if (a.equals("ppn")) { this.ppage = this.ppage + 1; redraw(); return; }
    if (a.startsWith("po:")) { pocketAct(a.substring(3), val(d, String.valueOf((char) 64) + "A")); return; }
    if (a.equals("sum")) { summon(); return; }
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(" = mk(") == MK0, "0.3.53: no system / command / class added"
_i = P.s.index
assert _i("public void fillPresets(") < _i("public void fillRequip(") < _i("public void fillPocket(") < _i("  try { fillPresets(b, ev); }"), "0.3.53: the fills before build"
assert P.s.count("if (known(") == 5, "fix pass: the five new grid ItemStacks (Requip slot, storage, pet / mount, pocket grid, pocket pick) are guarded by known()"
assert _i("public static boolean known(") < _i("public static @IGS@ rqSlot(") and _i("public void tanning()") < _i("public void bench(int i)") and _i("public String rqAct(") < _i('    if (a.equals("rq") || a.equals("rqe"))'), "0.3.53: methods before callers"
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.52 harness: every 0.3.52 check
# runs again on the 0.3.53 jar; the page now draws the craft panel only in mode "c" and has 40 bindings at first; + the INV4 section)
T.rep('''"""Harness for SkyyMenu 0.3.52 (OUR OWN CRAFTING inside the inventory + the v5 layout; tools/menu_0_3_52_patch.py).
''', '''"""Harness for SkyyMenu 0.3.53 (Requip inside the inventory + pocket tabs + mount Summon + the Tanning tab; tools/menu_0_3_53_patch.py).
GENERATED by tools/menu_0_3_53_patch.py from the 0.3.52 harness (edit the patch, not this file): every 0.3.52 check runs again on the
0.3.53 jar (the first page = the craft panel, mode "c"; 40 bindings: the Requip / Void buttons are gone, Edit + Summon + 2 pocket tabs are
new), plus
  INV4 (EXECUTED on the stand-ins with Python stand-ins of SkyyWardrobe 0.2.14 requip:fn:presets / preset / act + wardrobe:fn:list,
       SkyySacks 0.8.38 sacks:fn:pocketList / pocket / openTannery and SkyyPets 0.4.26 pets:fn:ride): WITHOUT them the presets row says
       so, Edit / Summon answer with a caption, the pocket row is Craft | Void; WITH them: the five presets in the header (the worn one
       selected), one click = Equip (the act call, the caption, the selection moves); Edit = the Requip panel INSTEAD of the craft panel
       (no craft grid or binding drawn), the title, the marks (on you / missing / keep / stored / pet / mount), the hint, the list (worn /
       miss notes), the storage strip; pick a preset, Equip, Save what I wear, Rename (the typed name), pick a slot + Keep slot (a pet slot
       refused, no call); a DRAG from the bag onto a preset slot = ONE drop call with the slot, section, source slot and item id (the page
       moves nothing itself), the drag cleared, a repeat within 1.5 s ignored, a drop on the pet slot refused, from the hotbar; the strip
       pick + Take out (nothing picked = no call); the full storage grid (title) + back; Done = the craft panel again; the POCKET tabs
       (Craft + six), a pocket's grid (the real counts, the level line), pick, Withdraw / Sell / Deposit / Unpack with the typed amount,
       Enchanted only, search, an action with nothing picked = no call; Summon = pets:fn:ride; the Tanning tab = sacks:fn:openTannery;
       every answer ONE page packet; every grid copy without metadata.
The 0.3.52 harness text follows:
Harness for SkyyMenu 0.3.52 (OUR OWN CRAFTING inside the inventory + the v5 layout; tools/menu_0_3_52_patch.py).
''')
T.rep('VERSION = "0.3.52"\nJAR', 'VERSION = "0.3.53"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.51.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.52.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.51.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.52.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_52_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_53_patch.py")')
T.rep('"scratch", "inv3", "menu"', '"scratch", "inv4", "menu"')
T.rep(cut(T.s, 'ADDED = ["InvCraft"]', 'if "--expect-dump" in sys.argv:'), '''ADDED = []
EXPECT = {   # 0.3.53: the page data + run-time templates (InvData), the panel state + fills + actions (InvPage); the rest = the version text
    "InvPage": ["+f mode", "+f pamt", "+f pcat", "+f penc", "+f pkOn", "+f pkey", "+f pnote", "+f ppage", "+f pquery", "+f presetN", "+f psel", "+f pshown",
                "+f qpage", "+f rids", "+f rlN", "+f rlPer", "+f rlTop", "+f rlines", "+f rmarks", "+f rnew", "+f rnote", "+f rsSel", "+f rsShown", "+f rsel", "+f rslot", "+f rtit",
                "+f rworn", "+m bare", "+m call", "+m editRequip", "+m fillPocket", "+m fillPockets", "+m fillPresets", "+m fillRequip",
                "+m fillStore", "+m known", "+m lines", "+m markWord", "+m petSlot", "+m pocketAct", "+m pocketPick", "+m pocketTab", "+m presetEquip",
                "+m rqAct", "+m rqDo", "+m rqDrop", "+m rqKeep", "+m rqList", "+m rqPickStore", "+m rqSlotPick", "+m rqSlot", "+m rqTake",
                "+m storeList", "+m storeSlot", "+m summon", "+m tanning", "+m toInt", "+m toLong", "~c ", "~m bench", "~m build", "~m handleDataEvent"],
    "InvData": ["~<clinit>", "+f LC", "+f PCATS", "+f PGN", "+f PK_BTN", "+f PK_HELP", "+f PK_W", "+f PMAX", "+f PRESET_BTN", "+f PRESET_NONE",
                "+f PRESET_W", "+f QN", "+f Q_HELP", "+f RLMAX", "+f RL_BTN", "+f RQ_HELP", "+f RSN", "+f ST_P", "+f ST_PSEL", "+f ST_RL", "+f ST_RLSEL"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text in the setup lines (as every version)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.52"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.53"') == 1, "S VERSION")''')
T.rep('''    K.eq(len(bl), 7 + 15 + 2 * 4 + 1 + 5 + 2 + 1, "PAGE: 39 bindings (7 tabs + 15 buttons, 2 grids x 4 slot events, the drop zone, 5 click grids, "
                                                    "the search field + button, 1 bench tab)")''',
      '''    K.eq(len(bl), 7 + 7 + 7 + 2 * 4 + 1 + 5 + 2 + 1 + 2, "PAGE: 40 bindings (7 tabs + 7 shell buttons (0.3.53: Edit + Summon, no Open Requip / Craft / Void) + "
                                                            "7 craft buttons, 2 grids x 4 slot events, the drop zone, 5 click grids, the search field + button, "
                                                            "1 bench tab, 2 pocket tabs Craft | Void; no presets without SkyyWardrobe 0.2.14)")''')
HARNESS_INV4 = r"""    # ---- INV4 (0.3.53; popup 11-14 "Inside the inventory (Recommended)", "Start it now"): Requip presets + panel, pocket tabs, Summon, Tanning
    for iid_, ms_ in (("Armor_Iron_Chest", 1), ("Armor_Iron_Legs", 1), ("Ore_Copper", 100), ("Skyy_Ench_Iron", 100)):
        it_ = Ucls.allocateInstance(ITc.class_)
        E.jf(ITc.class_, "id").set(it_, iid_)
        E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
        E.jf(ITc.class_, "maxStack").setInt(it_, ms_)
        amap.put(iid_, it_)
    RQ = {"worn": 1, "names": ["Combat", "Mining", "Farming", "Foraging", "Fishing", "Loadout 6"], "calls": []}

    def f_presets(o):
        return "\n".join(["ok|%d|%d|18" % (RQ["worn"], len(RQ["names"]))] + ["%d|%s|%d|%d|1|1" % (i_, n_, 3 if i_ < 5 else 0, 1 if i_ == 1 else 0) for i_, n_ in enumerate(RQ["names"])])

    def f_preset(o):
        n_ = int(o[1])
        if n_ < 0 or n_ >= len(RQ["names"]):
            return "off|There is no preset %d (6 open)" % (n_ + 1)
        mk_ = {0: ("on", "Armor_Iron_Head"), 1: ("missing", "Armor_Iron_Chest"), 3: ("stored", "Armor_Iron_Legs"), 4: ("on", "Weapon_Sword_Iron")}
        nm_ = ["Head", "Chest", "Hands", "Legs"] + ["Hotbar %d" % (i_ + 1) for i_ in range(9)]
        ls_ = ["ok|%d|%s|%d|0" % (n_, RQ["names"][n_], 1 if n_ == RQ["worn"] else 0)]
        ls_ += ["%d|%s|%s|%s" % (k_, mk_.get(k_, ("keep", ""))[0], mk_.get(k_, ("keep", ""))[1], nm_[k_]) for k_ in range(13)]
        return "\n".join(ls_ + ["pet|set|Skyy_PetIcon_Wolf_Legendary|Legendary Wolf Lv 42", "mount|keep||", "abil|keep||"])

    def f_act(o):
        op_, n_ = str(o[1]), int(o[2])
        RQ["calls"].append((op_, n_, None if o[3] is None else str(o[3])))
        if op_ == "equip":
            RQ["worn"] = n_
            return "+Equipped %s (2 moves)." % RQ["names"][n_]
        if op_ == "drop":
            return "+%s: Chest takes Armor_Iron_Chest. It waits in Requip storage until you Equip." % RQ["names"][n_]
        return "+%s: %s done." % (RQ["names"][n_] if 0 <= n_ < 6 else "Requip", op_)
    STORE = [("e1", "Armor_Iron_Legs"), ("e2", "Weapon_Sword_Iron")]
    POCK, RIDE, TAN, PTOK, PKT = [], [], [], [], {"t": "k1"}

    def f_plist(o):
        if str(o[1]) == "Mining":
            return "ok|Mining|3|Rare|240|6720|1|%s\nOre_Copper|128|0|5\nRock_Stone|64|0|-1\nSkyy_Ench_Iron|2|1|900\nGone_Mod_Item|7|0|-1" % PKT["t"]
        return "ok|%s|0|Common|0|640|1|%s" % (str(o[1]), PKT["t"])

    def f_pact(o):
        PTOK.append(str(o[4]) if len(o) > 4 else None)
        POCK.append((str(o[1]), str(o[2]), str(o[3])))
        return "+Took 64 Copper Ore"
    NEW = {"requip:fn:presets": f_presets, "requip:fn:preset": f_preset, "requip:fn:act": f_act,
           "wardrobe:fn:list": lambda o: OBJ([OBJ([e_, i_, None]) for e_, i_ in STORE]), "sacks:fn:pocketList": f_plist, "sacks:fn:pocket": f_pact,
           "pets:fn:ride": lambda o: (RIDE.append(str(o)), "+Mounting your Horse")[1], "sacks:fn:openTannery": lambda o: (TAN.append(str(o)), TRUE)[1]}

    def mk_of(p_, ident):
        for c_ in cmds_of(p_):
            t_ = str(c_.text or "")
            if ("#" + ident + " ") in t_:
                return t_
        return ""

    def nometa(p_):
        return all("etadata" not in v_ for k_, v_ in cmap(p_).items() if k_.endswith(".Slots"))
    PSEL_, TSEL_ = str(JV("InvData").ST_PSEL), str(JV("InvData").ST_TABSEL)   # the selected styles (the plain tab style names TabSelected for Pressed too)
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    p_ = one(ev(PK, {"a": "cb:0"}), "INV4 a page without the new bridges")
    cm = cmap(p_) if p_ else {}
    K.check(sval(cm, "#SkyyInvRpE.Text") == "Requip presets are not on this server" and sval(cm, "#SkyyInvPt0.Text") == "Craft" and sval(cm, "#SkyyInvPt1.Text") == "Void"
            and "#SkyyInvPt2.Text" not in cm and ("Activating", "#SkyyInvPt1") in [(b_[0], b_[1]) for b_ in binds_of(p_)],
            "INV4 no SkyyWardrobe 0.2.14 / SkyySacks 0.8.38: the presets row says so; the pocket row = Craft | Void (%s)" % sval(cm, "#SkyyInvRpE.Text"))
    p_ = one(ev(PK, {"a": "rqe"}), "INV4 Edit without the presets bridge")
    K.check("not on this server" in cap_of(p_) and str(pg.mode) == "c", "INV4 Edit without Requip: a caption, the craft panel stays (%s)" % cap_of(p_))
    p_ = one(ev(PK, {"a": "sum"}), "INV4 Summon without SkyyPets 0.4.26")
    K.check("not on this server" in cap_of(p_), "INV4 Summon without pets:fn:ride: a caption (%s)" % cap_of(p_))
    for k_, f_ in NEW.items():
        BR.put(k_, Fn(f_))
    p_ = one(ev(PK, {"a": "cb:0"}), "INV4 redraw with the bridges")
    cm = cmap(p_) if p_ else {}
    K.check([sval(cm, "#SkyyInvRp%d.Text" % i_) for i_ in range(5)] == RQ["names"][:5] and "#SkyyInvRp5.Text" not in cm
            and all(("Activating", "#SkyyInvRp%d" % i_) in [(b_[0], b_[1]) for b_ in binds_of(p_)] for i_ in range(5)),
            "INV4 PRESETS: Combat / Mining / Farming / Foraging / Fishing in the header, each bound (%s)" % [sval(cm, "#SkyyInvRp%d.Text" % i_) for i_ in range(5)])
    K.check(PSEL_ in mk_of(p_, "SkyyInvRp1") and PSEL_ not in mk_of(p_, "SkyyInvRp0"), "INV4 PRESETS: the worn one (Mining) is drawn selected")
    K.check([sval(cm, "#SkyyInvPt%d.Text" % i_) for i_ in range(7)] == ["Craft", "Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]
            and TSEL_ in mk_of(p_, "SkyyInvPt0") and TSEL_ not in mk_of(p_, "SkyyInvPt1"), "INV4 POCKET TABS: Craft + the six pockets, Craft selected")
    p_ = one(ev(PK, {"a": "rp:2"}), "INV4 one click on Farming")
    K.check(RQ["calls"][-1] == ("equip", 2, "") and "Equipped Farming" in cap_of(p_) and PSEL_ in mk_of(p_, "SkyyInvRp2") and PSEL_ not in mk_of(p_, "SkyyInvRp1"),
            "INV4 ONE CLICK = Equip that preset (requip:fn:act equip 2), the caption, the selection moves (%s)" % cap_of(p_))
    p_ = one(ev(PK, {"a": "rqe"}), "INV4 Edit")
    cm, bl = (cmap(p_), binds_of(p_)) if p_ else ({}, [])
    K.check(str(pg.mode) == "r" and "#SkyyInvCg.Slots" not in cm and not [b_ for b_ in bl if b_[1] in ("#SkyyInvCg", "#SkyyInvCq", "#SkyyInvCx1")]
            and sval(cm, "#SkyyInvRqT.Text") == "REQUIP - FARMING  (WORN)" and "#SkyyInvIs.Slots" in cm,
            "INV4 EDIT: the Requip panel INSTEAD of the craft panel (no craft grid / binding drawn), the bag stays, editing the worn preset (%s)" % sval(cm, "#SkyyInvRqT.Text"))
    K.eq([sval(cm, "#SkyyInvMa%d.Text" % k_) for k_ in range(6)] + [sval(cm, "#SkyyInvMh0.Text"), sval(cm, "#SkyyInvMh1.Text")],
         ["on you", "missing", "keep", "stored", "pet set", "mount keep", "on you", "keep"], "INV4 EDIT: the marks under every slot")
    K.check("Armor_Iron_Head" in cm.get("#SkyyInvRa.Slots", "") and "Skyy_PetIcon_Wolf_Legendary" in cm.get("#SkyyInvRa.Slots", "") and "Weapon_Sword_Iron" in cm.get("#SkyyInvRh.Slots", "")
            and nometa(p_), "INV4 EDIT: the preset's armour + pet + hotbar items, every copy without metadata")
    K.check((sval(cm, "#SkyyInvRqI.Text") or "").startswith("1 missing - Chest") and sval(cm, "#SkyyInvRsT.Text") == "Storage 2" and "Armor_Iron_Legs" in cm.get("#SkyyInvRs.Slots", ""),
            "INV4 EDIT: the hint names what is missing; the storage strip + its count (%s)" % sval(cm, "#SkyyInvRqI.Text"))
    K.check([sval(cm, "#SkyyInvRl%d.Text" % i_) for i_ in range(6)] == ["Combat", "Mining  - 1 miss", "Farming  - worn", "Foraging", "Fishing", "Loadout 6"],
            "INV4 EDIT: the preset list with the worn / missing notes (%s)" % [sval(cm, "#SkyyInvRl%d.Text" % i_) for i_ in range(6)])
    K.check(all(x_ in [(b_[0], b_[1]) for b_ in bl] for x_ in (("Dropped", "#SkyyInvRa"), ("Dropped", "#SkyyInvRh"), ("SlotClicking", "#SkyyInvRa"),
                                                               ("SlotClicking", "#SkyyInvRs"), ("Validating", "#SkyyInvRn"), ("Activating", "#SkyyInvRqEq"))),
            "INV4 EDIT: drop + click bindings on the preset slots, the strip, the name field, Equip")
    # FIX PASS: "+ New preset" + the list pages (every loadout reachable)
    K.check(sval(cm, "#SkyyInvRl6.Text") == "+ New preset" and "#SkyyInvRl7.Text" not in cm, "INV4 FIX the list ends with + New preset (%s)" % sval(cm, "#SkyyInvRl6.Text"))
    p_ = one(ev(PK, {"a": "rl:6"}), "INV4 FIX + New preset")
    K.check(int(pg.rsel) == 5 and sval(cmap(p_), "#SkyyInvRqT.Text") == "REQUIP - LOADOUT 6" and "Save what I wear" in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""),
            "INV4 FIX + New preset picks the first unused custom loadout (6) and says what to do (%s)" % sval(cmap(p_), "#SkyyInvRqI.Text"))
    RQ["names"] = ["Combat", "Mining", "Farming", "Foraging", "Fishing"] + ["Loadout %d" % (i_ + 6) for i_ in range(5)]
    p_ = one(ev(PK, {"a": "rl:0"}), "INV4 FIX ten presets")
    cm = cmap(p_) if p_ else {}
    K.check([sval(cm, "#SkyyInvRl%d.Text" % i_) for i_ in range(7)] == ["Combat", "Mining  - 1 miss", "Farming  - worn", "Foraging", "Fishing", "More  (1 / 2)", "+ New preset"]
            and "#SkyyInvRl7.Text" not in cm, "INV4 FIX ten presets: 5 rows + More (1 / 2) + New preset (%s)" % [sval(cm, "#SkyyInvRl%d.Text" % i_) for i_ in range(7)])
    p_ = one(ev(PK, {"a": "rl:5"}), "INV4 FIX More")
    cm = cmap(p_) if p_ else {}
    K.check([sval(cm, "#SkyyInvRl%d.Text" % i_) for i_ in range(7)] == ["Loadout %d" % (i_ + 6) for i_ in range(5)] + ["More  (2 / 2)", "+ New preset"],
            "INV4 FIX More shows the next page (%s)" % [sval(cm, "#SkyyInvRl%d.Text" % i_) for i_ in range(7)])
    p_ = one(ev(PK, {"a": "rl:4"}), "INV4 FIX pick Loadout 10")
    K.check(int(pg.rsel) == 9 and sval(cmap(p_), "#SkyyInvRqT.Text") == "REQUIP - LOADOUT 10" and sval(cmap(p_), "#SkyyInvRl4.Text") == "Loadout 10",
            "INV4 FIX loadout 10 is reachable, edited, the page stays (%s)" % sval(cmap(p_), "#SkyyInvRqT.Text"))
    one(ev(PK, {"a": "rqeq"}), "INV4 FIX Equip loadout 10")
    K.eq(RQ["calls"][-1], ("equip", 9, ""), "INV4 FIX Equip on loadout 10 -> requip:fn:act equip 9")
    p_ = one(ev(PK, {"a": "rl:5"}), "INV4 FIX More wraps")
    K.eq(sval(cmap(p_), "#SkyyInvRl0.Text"), "Combat", "INV4 FIX More on the last page goes back to the first")
    RQ["names"] = ["Combat", "Mining", "Farming", "Foraging", "Fishing", "Loadout 6"]
    RQ["worn"] = 2
    p_ = one(ev(PK, {"a": "rl:1"}), "INV4 pick Mining in the list")
    K.check(sval(cmap(p_), "#SkyyInvRqT.Text") == "REQUIP - MINING" and int(pg.rsel) == 1, "INV4 the list picks the preset to edit")
    for a_, want_ in (({"a": "rqeq"}, ("equip", 1, "")), ({"a": "rqsv"}, ("worn", 1, "")), ({"a": "rn", "@R": "Deep caves"}, ("rename", 1, "Deep caves"))):
        p_ = one(ev(PK, a_), "INV4 " + a_["a"])
        K.check(RQ["calls"][-1] == want_ and "Mining" in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""), "INV4 %s -> requip:fn:act %s (%s)" % (a_["a"], want_, sval(cmap(p_), "#SkyyInvRqI.Text")))
    p_ = one(ev(PK, {"a": "rs:h", "SlotIndex": 2}), "INV4 pick Hotbar 3")
    K.check(int(pg.rslot) == 6 and (sval(cmap(p_), "#SkyyInvMh2.Text") or "").startswith("> ") and (sval(cmap(p_), "#SkyyInvRqI.Text") or "").startswith("Hotbar 3"),
            "INV4 a slot click picks it (marked >, the hint names it)")
    p_ = one(ev(PK, {"a": "rqk"}), "INV4 Keep slot")
    K.eq(RQ["calls"][-1], ("keep", 1, "6"), "INV4 Keep slot -> requip:fn:act keep 6")
    n0_ = len(RQ["calls"])
    one(ev(PK, {"a": "rs:a", "SlotIndex": 4}), "INV4 pick the pet slot")
    p_ = one(ev(PK, {"a": "rqk"}), "INV4 Keep on the pet slot")
    K.check(len(RQ["calls"]) == n0_ and "Pick an armour or hotbar slot" in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""), "INV4 Keep on the pet slot: refused, no call")
    put(PK, "storage", 5, ISc("Armor_Iron_Chest", 1))
    c0_ = E.count(PK, "Armor_Iron_Chest")
    one(ev(PK, {"a": "sc", "g": "s", "SlotIndex": 5}), "INV4 drag start in the bag")
    p_ = one(ev(PK, {"a": "rd:a", "SlotIndex": 1, "SourceInventorySectionId": -2, "SourceSlotId": 5, "ItemStackId": "Armor_Iron_Chest"}), "INV4 DROP on the Chest slot")
    K.check(RQ["calls"][-1] == ("drop", 1, "1|storage:5:Armor_Iron_Chest") and pg.dg is None and E.count(PK, "Armor_Iron_Chest") == c0_
            and "waits in Requip storage" in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""),
            "INV4 DRAG from the bag onto a preset slot = ONE drop call (slot 1, storage slot 5, the item id); the page moves nothing itself; the drag is cleared")
    n0_ = len(RQ["calls"])
    one(ev(PK, {"a": "rd:a", "SlotIndex": 1, "SourceInventorySectionId": -2, "SourceSlotId": 5, "ItemStackId": "Armor_Iron_Chest"}), "INV4 the same drop again")
    K.eq(len(RQ["calls"]), n0_, "INV4 the same drop within 1.5 s = no second call")
    p_ = one(ev(PK, {"a": "rd:a", "SlotIndex": 4, "SourceInventorySectionId": -2, "SourceSlotId": 6, "ItemStackId": "Rock_Stone"}), "INV4 drop on the pet slot")
    K.check(len(RQ["calls"]) == n0_ and "Pets tab" in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""), "INV4 a drop on the pet slot: refused, no call")
    one(ev(PK, {"a": "rd:h", "SlotIndex": 3, "SourceInventorySectionId": -1, "SourceSlotId": 0, "ItemStackId": "Plant_Fruit_Apple"}), "INV4 drop from the hotbar")
    K.eq(RQ["calls"][-1], ("drop", 1, "7|hotbar:0:Plant_Fruit_Apple"), "INV4 a hotbar item onto Hotbar 4 = drop 7|hotbar:0")
    p_ = one(ev(PK, {"a": "rso"}), "INV4 Take out with nothing picked")
    K.check(RQ["calls"][-1][0] != "take" and "Pick an item in Requip storage" in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""), "INV4 Take out with nothing picked: no call")
    one(ev(PK, {"a": "rss", "SlotIndex": 0}), "INV4 pick a stored item")
    K.eq(str(pg.rsSel), "e1", "INV4 the strip click picks the entry")
    one(ev(PK, {"a": "rso"}), "INV4 Take out")
    K.check(RQ["calls"][-1] == ("take", -1, "e1") and pg.rsSel is None, "INV4 Take out -> requip:fn:act take e1")
    p_ = one(ev(PK, {"a": "rst"}), "INV4 the full storage")
    cm = cmap(p_) if p_ else {}
    K.check(str(pg.mode) == "q" and sval(cm, "#SkyyInvQT.Text") == "REQUIP STORAGE - 2 items" and "Weapon_Sword_Iron" in cm.get("#SkyyInvQg.Slots", "") and "#SkyyInvRa.Slots" not in cm
            and nometa(p_), "INV4 the strip's title = the full storage grid (12 x 4) instead of the preset")
    one(ev(PK, {"a": "rss", "SlotIndex": 1}), "INV4 pick in the full grid")
    one(ev(PK, {"a": "rso"}), "INV4 Take out from the full grid")
    K.eq(RQ["calls"][-1], ("take", -1, "e2"), "INV4 Take out from the full grid")
    one(ev(PK, {"a": "rst"}), "INV4 back to the preset")
    K.eq(str(pg.mode), "r", "INV4 Show preset = the preset view again")
    p_ = one(ev(PK, {"a": "rqd"}), "INV4 Done")
    K.check(str(pg.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_) and "#SkyyInvRa.Slots" not in cmap(p_), "INV4 Done = the craft panel again")
    p_ = one(ev(PK, {"a": "pt:1"}), "INV4 the Mining pocket")
    cm = cmap(p_) if p_ else {}
    K.check(str(pg.mode) == "p" and sval(cm, "#SkyyInvPkT.Text") == "MINING POCKET" and sval(cm, "#SkyyInvPkL.Text") == "Lv 3  -  Rare  -  240 / 6,720"
            and "Ore_Copper" in cm.get("#SkyyInvPg.Slots", "") and "128" in cm.get("#SkyyInvPg.Slots", "") and "#SkyyInvCg.Slots" not in cm
            and TSEL_ in mk_of(p_, "SkyyInvPt1") and TSEL_ not in mk_of(p_, "SkyyInvPt0") and nometa(p_),
            "INV4 POCKET: the Mining grid with the real counts (the exact 128 in the name; the icon number a full stack at most), the level line, its tab selected (%s)" % sval(cm, "#SkyyInvPkL.Text"))
    K.check("Gone_Mod_Item" not in cm.get("#SkyyInvPg.Slots", "") and "Gone Mod Item  -  7 in the Void" in cm.get("#SkyyInvPg.Slots", "") and str(pg.pkey) == "k1",
            "INV4 FIX an id the server does not know = a name-only slot, never an ItemStack; the list's profile token kept")
    p_ = one(ev(PK, {"a": "pgs", "SlotIndex": 3}), "INV4 FIX pick the unknown item")
    K.check(str(pg.psel) == "Gone_Mod_Item" and "Gone_Mod_Item" not in cmap(p_).get("#SkyyInvPsl.Slots", "") and sval(cmap(p_), "#SkyyInvPsN.Text") == "Gone Mod Item",
            "INV4 FIX the picked unknown item: its name, no ItemStack in the pick slot")
    pg.psel = None
    p_ = one(ev(PK, {"a": "po:wd", "@A": "64"}), "INV4 Withdraw with nothing picked")
    K.check(POCK == [] and "Pick an item" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""), "INV4 an action with nothing picked: no call")
    p_ = one(ev(PK, {"a": "pgs", "SlotIndex": 0}), "INV4 pick Copper Ore")
    K.check(str(pg.psel) == "Ore_Copper" and "128" in (sval(cmap(p_), "#SkyyInvPsC.Text") or "") and "5 each" in (sval(cmap(p_), "#SkyyInvPsC.Text") or ""),
            "INV4 the picked item: its Void count + the Bazaar price (%s)" % sval(cmap(p_), "#SkyyInvPsC.Text"))
    for op_, amt_ in (("wd", "64"), ("sell", "10"), ("dep", ""), ("unpack", "all")):
        p_ = one(ev(PK, {"a": "po:" + op_, "@A": amt_}), "INV4 " + op_)
        K.check(POCK[-1] == (op_, "Ore_Copper", amt_) and PTOK[-1] == "k1" and sval(cmap(p_), "#SkyyInvPr.Text") == "Took 64 Copper Ore",
                "INV4 %s -> sacks:fn:pocket (%s, Ore_Copper, '%s'), its answer shown" % (op_, op_, amt_))
    PKT["t"] = "k2"
    p_ = one(ev(PK, {"a": "ppn"}), "INV4 FIX a redraw after a profile switch")
    K.check(pg.psel is None and str(pg.pkey) == "k2" and "Your profile changed" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""),
            "INV4 FIX a profile switch seen on a redraw clears the pick and says so (%s)" % sval(cmap(p_), "#SkyyInvPr.Text"))
    n0_ = len(POCK)
    one(ev(PK, {"a": "po:sell", "@A": ""}), "INV4 FIX Sell after the switch")
    K.eq(len(POCK), n0_, "INV4 FIX Sell after a profile switch with the old pick: no call (nothing sold)")
    one(ev(PK, {"a": "pgs", "SlotIndex": 0}), "INV4 FIX pick again")
    one(ev(PK, {"a": "po:wd", "@A": "1"}), "INV4 FIX Withdraw on the new profile")
    K.check(PTOK[-1] == "k2" and POCK[-1] == ("wd", "Ore_Copper", "1"), "INV4 FIX the action carries the new profile's token")
    p_ = one(ev(PK, {"a": "pf"}), "INV4 Enchanted only")
    K.check("Skyy_Ench_Iron" in cmap(p_).get("#SkyyInvPg.Slots", "") and "Ore_Copper" not in cmap(p_).get("#SkyyInvPg.Slots", "") and sval(cmap(p_), "#SkyyInvPf.Text") == "Enchanted only - On",
            "INV4 Enchanted only shows only Enchanted items")
    one(ev(PK, {"a": "pf"}), "INV4 Enchanted only off")
    p_ = one(ev(PK, {"a": "pq", "@S": "rock"}), "INV4 pocket search")
    K.check("Rock_Stone" in cmap(p_).get("#SkyyInvPg.Slots", "") and "Ore_Copper" not in cmap(p_).get("#SkyyInvPg.Slots", ""), "INV4 the pocket search filters the grid")
    p_ = one(ev(PK, {"a": "pt:0"}), "INV4 back to Craft")
    K.check(str(pg.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_), "INV4 the Craft tab = the craft panel again")
    p_ = one(ev(PK, {"a": "sum"}), "INV4 Summon")
    K.check(RIDE == [str(PK.pr.getUuid())] and cap_of(p_) == "Mounting your Horse", "INV4 SUMMON = pets:fn:ride with your UUID, its answer as the caption (%s)" % cap_of(p_))
    bk_ = [str(x_) for x_ in pg.cbenches]
    if "Tannery" in bk_:
        p_ = one(ev(PK, {"a": "cb:%d" % bk_.index("Tannery")}), "INV4 Tanning tab")
        K.check(TAN == [str(PK.pr.getUuid())] and cap_of(p_) == "Opening the Tannery", "INV4 the Tanning tab = sacks:fn:openTannery (%s)" % cap_of(p_))
    else:
        K.check(False, "INV4 the Tanning tab is drawn in the Void mode (benches %s)" % bk_)
    for k_ in NEW:
        BR.remove(k_)
    pg.shut()
    E.pump(PK)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_INV4 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
assert 'VERSION = "0.3.52"' not in T.s and 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.51.jar")' not in T.s, "0.3.53 harness: an old line is still there"
if T.dst:
    T.finish()
