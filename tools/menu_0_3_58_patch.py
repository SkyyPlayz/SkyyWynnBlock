"""Derive SkyyMenu/build_skyymenu_0.3.58.py + SkyyMenu/test_skyymenu_0.3.58.py from the SET pin SkyyMenu 0.3.57 (generated - never re-run
its patch). Run:  python tools/menu_0_3_58_patch.py   then   python SkyyMenu/build_skyymenu_0.3.58.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.58.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.57 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.58 (2026-11-21, round tab2) = TAB SCREENS ROUND 2: THE PETS TAB - ONE SCREEN (pets, slots, eggs, hatchery, egg crafting + upgrade, fusing).
Skyy's words: 11-21 "game is closed, deploy as ready. i might be able to test later. build and deploy everything on your list"; 11-14 "clicking any
button in the top bar of the inventory takes me to the old system, we are going to need a full ui redesign ... like in pets. 1 tab with your pets
your eggs the hatchery,, ecc crafting, pet fusing. i want it all on 1 screen."; on pets-page.png "i like this!" (docs/answered/ui.md + pets.md
2026-11-14; pet tooltip approved 2026-10-24). Approved art: research/ui-theme-art/pets-page.png (README defaults). SURVEY: vanilla has no pet screen;
no pack mod draws one - this page reads SkyyPets' own bridges only (vanilla first: the egg / pet items, portraits and frames are SkyyPets' own).
  1. THE PETS TAB of the inventory's top bar (and the inventory's pet / mount cards, and the skill page's Pets tab) opens the new PETS SCREEN
     (PetsTab: an inline Skyglass page, kit tools/skyyui.py, the inventory's frame + the same 7-tab top bar with Pets selected):
     LEFT   EQUIPPED (the PET slot card + the MOUNT slot card: portrait, name in its rarity colour, level, what the slot does; Take out;
            Summon = pets:fn:ride on the mount card) + YOUR PETS (count / max, role chips All / Bonus / Fighter / Mount, the area chips from
            SkyyPets, a 7 x 6 grid of rarity-framed portraits with the APPROVED sectioned pet tooltip, pages of 42 - < > - so nothing scrolls).
     MIDDLE SELECTED PET (portrait, rarity-coloured name, tags, Lv + XP bar, BUFFS NOW, WHERE IT WORKS, PROGRESS, AT LV max; Pet slot /
            Mount slot (Take out when it is in that slot) / Rebirth) + PET FUSING (the group: it + up to 3 of the same kind and rarity, the
            result, have / need, why not; Fuse = SkyyPets' two-press rule).
     RIGHT  HATCHERY (6 rows: the egg, time left + bar, Ready!, Hatch / Take out / Place; locked rows = Beastmastery; more slots = the Full
            page) + EGGS (your eggs grid, Place = the selected egg into a free Hatchery slot; CRAFT = the Common eggs with the cost line
            "Name have/need + ..." (green = enough, red = short; fix round tab2fix); UPGRADE THE SELECTED EGG = its Uncommon upgrade per SkyyPets 0.4.27). Every number, cost, timer and rule = SkyyPets'.
     Reads + actions through SkyyPets 0.4.28 pets:fn:tab / pets:fn:tabact (profile token, the world thread, the 350 ms same-op guard, items moved
     only inside SkyyPets' own doors). This page holds a page token too: a click from an older drawing = "The page changed" (no bridge call).
  2. FALLBACK: without pets:fn:tab / tabact (an older SkyyPets) the Pets tab opens today's Pets page; on the screen 'Full page' opens it any time
     (more than 6 Hatchery slots, egg fusing, the starter choice). The other tabs not built yet keep opening today's pages.
  3. Pet tooltips: SkyyPets' approved sectioned tooltip (docs/answered/pets.md 2026-10-24) on every portrait, with this screen's click footer;
     rarity colours on the frames (the portrait items) and on every name (slot cards, selected pet; keep_holder variants).
  Every bound click answers with exactly ONE page packet (a redraw, a caption, a page that replaces this one, or the close); every grid copy is
  a NEW ItemStack(id, qty) without metadata behind known(id); no Top / Bottom alignment; inline page only; never setPageWithWindows.
  NOT BUILT (next rounds, nothing half-wired): Shift-click = pet slot / right-click = mount slot (the client's click data with modifiers is not
  proven - the buttons do it); drag an egg onto the Hatchery (Place does it); search + sort (the SkyyPets order = rarest first); egg FUSING
  (Full page); more than 6 Hatchery rows (Full page); /pets opening this screen (SkyyPets' command); live timers (no periodic updates - a click
  refreshes them).
  New classes PetsTabData + PetsTab; no command, no setting, no lang key, no system, no saved data.
  ROLLBACK to 0.3.57: safe alone (nothing saved; the Pets tab opens the old Pets page again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.57.py"), os.path.join(MOD, "build_skyymenu_0.3.58.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.57.py"), os.path.join(MOD, "test_skyymenu_0.3.58.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.57"\n') and P.has("tools/menu_0_3_57_patch.py") and P.has("SkillPage")
assert not P.has("PetsTab"), "not the generated SkyyMenu 0.3.57 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.57: THE SKILLS TAB''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.58: THE PETS TAB = ONE SCREEN (PetsTab: equipped pet + mount slots with Summon, your pets grid with the approved tooltips + filters + pages,
       the selected pet, pet fusing, the Hatchery, eggs: craft Common + upgrade the selected egg - SkyyPets 0.4.28 pets:fn:tab / tabact;
       'Full page' = the old Pets page) (notes: tools/menu_0_3_58_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.58.py.
0.3.57: THE SKILLS TAB''')
P.rep('VERSION = "0.3.57"\n', 'VERSION = "0.3.58"\n')

# ---------- (1) the PETS SCREEN markup (built like the skill page: one page data list drawn by PetsTab.build)
PT_PAGE = r'''
# ================= 0.3.58 THE PETS TAB: ONE SCREEN (tools/menu_0_3_58_patch.py; approved art research/ui-theme-art/pets-page.png; Skyy 11-14
# "1 tab with your pets your eggs the hatchery,, ecc crafting, pet fusing. i want it all on 1 screen." + on pets-page.png "i like this!") =================
# The inventory's frame and top bar (Pets selected); LEFT equipped + your pets | MIDDLE the selected pet + fusing | RIGHT the Hatchery + eggs.
PT = "SkyyPtab"
PT_L, PT_M = 560, 470
PT_R = IV_IW - PT_L - PT_M - 2 * IV_GAP                    # 506
PT_LI, PT_MI, PT_RI = PT_L - 20, PT_M - 20, PT_R - 20
PT_EQ_H, PT_SE_H, PT_HA_H = 166, 560, 400
PT_PE_H, PT_FU_H, PT_EG_H = IV_BODY_H - PT_EQ_H - 8, IV_BODY_H - PT_SE_H - 8, IV_BODY_H - PT_HA_H - 8
PT_CW = (PT_LI - 10) // 2                                  # a slot card
PT_CTW = PT_CW - 16 - 56 - 8                               # its text column
PT_GC, PT_GR = 7, 6                                        # the pets grid (pages of 42, nothing scrolls)
PT_PER = PT_GC * PT_GR
PT_SXW = 250                                               # the selected pet's XP bar
PT_HRN, PT_HTW = 6, PT_RI - 12 - 44 - 8 - 96 - 8           # Hatchery rows + their text column
PT_EGC, PT_EGR = 9, 2                                      # the eggs grid
PT_CRN = 5                                                 # the Common egg crafts
PT_CRN_W, PT_CRB_W = 84, 64                                # a craft row's name (the category: the header says Common) + its Craft button
PT_CRW = PT_RI - PT_CRN_W - 6 - PT_CRB_W - 6                # a craft row's cost line
PT_UPW = PT_RI - 12 - 96 - 6                               # the upgrade box's cost line
# fix (critic 3 / 1): SkyyPets 0.4.28 sends the cost as "Name have/need + ..." and asserts its longest line fits 244 / 372 px at size 11 - keep these
# widths at least that wide (green = can craft, red = short); the character clip below is only a safety net
import skyyeggs as _EGG58
assert all(SUI.text_width(c_, 12, bold=True) <= PT_CRN_W for c_ in _EGG58.CATEGORIES), "0.3.58: a craft row's category name fits"
assert PT_CRW >= 320 and PT_UPW >= 372, ("0.3.58: the cost labels SkyyPets 0.4.28 measures against", PT_CRW, PT_UPW)
PT_RCOL = ["#7f93a6", "#c9d2dd", "#3e9049", "#2770b7", "#8b339e", "#bb8a2c", "#cc66cc"]   # 0 = no pet; 1-6 Common..Mythic (research/ui-theme-art/README)
PT_ROLES = ["All", "Bonus", "Fighter", "Mount"]
PT_AREAS = ["All", "Combat", "Farming", "Mining", "Foraging", "Fishing", "Explore", "Cooking"]   # the SkyyPets 0.4.27 AREA_SKILLS labels (Exploration = Explore)
PT_CHW, PT_ACW = 80, 63
PT_TXT = {
    "foot": "Click a pet to select it. Pet slot, Mount slot and Rebirth are on the right.",
    "fuseRule": "Keeps the highest level. Mythic cannot be fused - eggs only.",
    "hfoot": "Hatch = 2 rolls: which pet, then its rarity. Time by egg rarity.",
    "eggsNote": "craft Common, upgrade the rest",
    "craftH": "CRAFT  (Common eggs only)",
}
assert PT_TXT and all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in PT_TXT.values() for c_ in v_), "0.3.58: plain texts"
for _l in PT_ROLES:
    assert SUI.text_width(_l, 12, bold=True) <= PT_CHW - 12, ("0.3.58: a role chip fits", _l)
for _l in PT_AREAS + ["Exploration"[:8]]:
    assert SUI.text_width(_l, 11, bold=True) <= PT_ACW - 8, ("0.3.58: an area chip fits", _l)
# the run-time markup: the chips (appended into #SkyyPtabRr / #SkyyPtabAr, the chosen one in the selected tab look) + the bar fills
PT_ST_CH, PT_ST_CHSEL = SUI.glass_button_style("tab", 12), SUI.glass_button_style("tabSelected", 12)
PT_ST_ACH, PT_ST_ACHSEL = SUI.glass_button_style("tab", 11), SUI.glass_button_style("tabSelected", 11)
PT_CHIP = "TextButton #SkyyPtab{I} { Anchor: (Width: {W}, Height: 26, Right: 4); {S} }"
PT_FILL8 = "Group { Anchor: (Width: {W}, Height: 8); Background: %s; }" % SUI.glass_col("xp")
PT_FILL6 = "Group { Anchor: (Width: {W}, Height: 6); Background: %s; }" % SUI.glass_col("accent")
PT_FILL6G = "Group { Anchor: (Width: {W}, Height: 6); Background: %s; }" % SUI.glass_col("green")
for _mk in (PT_CHIP.replace("{I}", "Ro0").replace("{W}", "80").replace("{S}", PT_ST_CHSEL), PT_CHIP.replace("{I}", "Ao0").replace("{W}", "63").replace("{S}", PT_ST_ACH),
            PT_FILL8.replace("{W}", "40"), PT_FILL6.replace("{W}", "40"), PT_FILL6G.replace("{W}", "40")):
    SUI.check_markup(_mk, prefix=PT, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.58: a run-time markup line Java can hold"


def _pt_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label

    def rar_holder(parent, ident, w, h, size, anchor=None, dim_col="dim"):
        """the name in its rarity colour: 7 variants (0 = no pet) in a keep_holder"""
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, dim_col if k_ == 0 else PT_RCOL[k_], bold=True, w=w, h=h)) for k_ in range(7)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)

    def two_holder(parent, ident, w, h, size, cols, anchor=None, bold=False):
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, c_, bold=bold, w=w, h=h)) for k_, c_ in enumerate(cols)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (PT, IV_PAGE_W, IV_PAGE_H)))
    win = PT + "Win"
    ap.append(("#" + PT, G_.glass_group(win, IV_W, IV_WIN_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": (IV_PAGE_H - IV_WIN_H) // 2})))
    # ---- row 1: the same 7 tabs (Pets selected), Full page, coins, the X
    top = PT + "Top"
    ap.append(("#" + win, G_.glass_group(top, IV_IW, IV_TOP_H, layout="Left")))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (PT, i), lb, "tabSelected" if i == 2 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - IV_COIN_W - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(PT + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(PT + "Coins", "", 15, "xp", bold=True, w=IV_COIN_W, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(PT + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    ap.append(("#" + win, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }' % (PT, IV_IW, G_.glass_path("Separator"))))
    body = PT + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Left")))
    # ======== LEFT: EQUIPPED + YOUR PETS
    lf = PT + "Lf"
    ap.append(("#" + body, G_.glass_group(lf, PT_L, IV_BODY_H, layout="Top")))
    eq = PT + "Eq"
    ap.append(("#" + lf, G_.glass_group(eq, PT_L, PT_EQ_H, role="panel", layout="Top", pad=10)))
    ap.append(("#" + eq, lab(None, "EQUIPPED", 15, "accentHi", bold=True, w=PT_LI, h=22)))
    eqr = PT + "Eqr"
    ap.append(("#" + eq, G_.glass_group(eqr, PT_LI, 116, layout="Left", anchor={"top": 6})))
    for s_, title in ((1, "PET SLOT - follows you"), (2, "MOUNT SLOT - ride")):
        cd = "%sQ%d" % (PT, s_)
        ap.append(("#" + eqr, G_.glass_group(cd, PT_CW, 116, role="inset", layout="Top", pad=8, anchor={"right": 10} if s_ == 1 else None)))
        ap.append(("#" + cd, lab(None, title, 11, "dim", bold=True, w=PT_CW - 16, h=16)))
        cr = cd + "R"
        ap.append(("#" + cd, G_.glass_group(cr, PT_CW - 16, 56, layout="Left")))
        ap.append(("#" + cr, G_.glass_grid(cd + "I", 1, 1, drag=False, slot=56, icon=46)))
        cx = cd + "X"
        ap.append(("#" + cr, G_.glass_group(cx, PT_CTW, 56, layout="Top", anchor={"left": 8})))
        rar_holder(cx, cd + "N", PT_CTW, 20, 14)
        ap.append(("#" + cx, lab(cd + "L", "", 12, "xp", bold=True, w=PT_CTW, h=18)))
        ap.append(("#" + cx, lab(cd + "S", "", 11, "dim", w=PT_CTW, h=18)))
        cb = cd + "B"
        ap.append(("#" + cd, G_.glass_group(cb, PT_CW - 16, 24, layout="Left", anchor={"top": 4})))
        if s_ == 2:
            ap.append(("#" + cb, G_.glass_button(cd + "Go", "Summon", "primary", w=96, h=24, size=12, anchor={"right": 6})))
        ap.append(("#" + cb, G_.glass_button(cd + "Out", "Take out", "secondary", w=96, h=24, size=12)))
    assert 16 + 56 + 4 + 24 <= 116 - 16 and 2 * PT_CW + 10 <= PT_LI and 20 + 22 + 6 + 116 <= PT_EQ_H, "0.3.58: the slot cards fit"
    pe = PT + "Pe"
    ap.append(("#" + lf, G_.glass_group(pe, PT_L, PT_PE_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    peh = PT + "Peh"
    ap.append(("#" + pe, G_.glass_group(peh, PT_LI, 24, layout="Left")))
    ap.append(("#" + peh, lab(None, "YOUR PETS", 15, "accentHi", bold=True, w=200, h=24)))
    ap.append(("#" + peh, lab(PT + "Pn", "", 14, "xp", bold=True, w=PT_LI - 200, h=24, halign="End")))
    rr = PT + "Rrow"
    ap.append(("#" + pe, G_.glass_group(rr, PT_LI, 28, layout="Left", anchor={"top": 6})))
    ap.append(("#" + rr, G_.glass_group(PT + "Rr", PT_LI - 190, 28, layout="Left")))
    ap.append(("#" + rr, G_.glass_button(PT + "Pp", "<", "secondary", w=36, h=26, size=14, anchor={"right": 4})))
    ap.append(("#" + rr, lab(PT + "Pg", "", 12, "text", bold=True, w=106, h=26, halign="Center")))
    ap.append(("#" + rr, G_.glass_button(PT + "Pnx", ">", "secondary", w=36, h=26, size=14, anchor={"left": 4})))
    assert len(PT_ROLES) * (PT_CHW + 4) <= PT_LI - 190 and len(PT_AREAS) * (PT_ACW + 4) <= PT_LI, "0.3.58: the chip rows fit"
    ap.append(("#" + pe, G_.glass_group(PT + "Ar", PT_LI, 28, layout="Left", anchor={"top": 4})))
    gw_, gh_ = SUI.glass_grid_size(PT_GC, PT_GR, 74)
    pgr = PT + "Gw"
    ap.append(("#" + pe, G_.glass_group(pgr, PT_LI, gh_, layout="Left", anchor={"top": 8})))
    ap.append(("#" + pgr, "Group { Anchor: (Width: %d); }" % ((PT_LI - gw_) // 2)))
    ap.append(("#" + pgr, G_.glass_grid(PT + "G", PT_GC, PT_GR, drag=False, slot=74, icon=64)))
    ap.append(("#" + pe, lab(PT + "Pf", "", 12, "action", bold=True, w=PT_LI, h=20, anchor={"top": 8})))
    ap.sets.append((PT + "Pf", "Text", PT_TXT["foot"]))
    ap.append(("#" + pe, lab(PT + "Pe2", "", 12, "dim", w=PT_LI, h=20)))
    assert 20 + 24 + 6 + 28 + 4 + 28 + 8 + gh_ + 8 + 20 + 20 <= PT_PE_H and gw_ <= PT_LI, ("0.3.58: the pets panel fits", gw_, gh_)
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== MIDDLE: SELECTED PET + PET FUSING
    md = PT + "Md"
    ap.append(("#" + body, G_.glass_group(md, PT_M, IV_BODY_H, layout="Top")))
    se = PT + "Se"
    ap.append(("#" + md, G_.glass_group(se, PT_M, PT_SE_H, role="panel", layout="Top", pad=10)))
    sh = PT + "Sh"
    ap.append(("#" + se, G_.glass_group(sh, PT_MI, 96, layout="Left")))
    ap.append(("#" + sh, G_.glass_grid(PT + "SI", 1, 1, drag=False, slot=88, icon=76, anchor={"top": 4})))
    sx = PT + "Scol"
    sxw = PT_MI - 88 - 12
    ap.append(("#" + sh, G_.glass_group(sx, sxw, 96, layout="Top", anchor={"left": 12})))
    rar_holder(sx, PT + "SN", sxw, 30, 20)
    ap.append(("#" + sx, lab(PT + "Stg", "", 12, "accentHi", bold=True, w=sxw, h=20)))
    slr = PT + "Slr"
    ap.append(("#" + sx, G_.glass_group(slr, sxw, 22, layout="Left")))
    ap.append(("#" + slr, lab(PT + "SL", "", 14, "xp", bold=True, w=sxw - PT_SXW, h=22)))
    ap.append(("#" + slr, 'Group #%sSB { Anchor: (Width: %d, Height: 8, Top: 7); LayoutMode: Left; Background: %s; }' % (PT, PT_SXW, IV_TRACK)))
    ap.append(("#" + sx, lab(PT + "SX", "", 11, "dim", w=sxw, h=18, halign="End")))
    ap.append(("#" + se, lab(None, "BUFFS NOW", 12, "dim", bold=True, w=PT_MI, h=20, anchor={"top": 8})))
    for k_ in range(6):
        ap.append(("#" + se, lab(PT + "Sb%d" % k_, "", 13, "green", bold=True, w=PT_MI, h=20)))
    ap.append(("#" + se, lab(None, "WHERE IT WORKS", 12, "dim", bold=True, w=PT_MI, h=20, anchor={"top": 6})))
    for k_ in range(3):
        two_holder(se, PT + "Sw%d" % k_, PT_MI, 20, 13, ("green", "red"))
    ap.append(("#" + se, lab(None, "PROGRESS", 12, "dim", bold=True, w=PT_MI, h=20, anchor={"top": 6})))
    for k_ in range(2):
        ap.append(("#" + se, lab(PT + "Sg%d" % k_, "", 13, "text", w=PT_MI, h=20)))
    ap.append(("#" + se, lab(PT + "Sa", "", 12, "dim", bold=True, w=PT_MI, h=20, anchor={"top": 6})))
    ap.append(("#" + se, lab(PT + "Sat", "", 13, "green", bold=True, w=PT_MI, h=20)))
    sbt = PT + "Sbt"
    ap.append(("#" + se, G_.glass_group(sbt, PT_MI, 34, layout="Left", anchor={"top": 10})))
    ap.append(("#" + sbt, G_.glass_button(PT + "S1", "Pet slot", "primary", w=140, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + sbt, G_.glass_button(PT + "S2", "Mount slot", "secondary", w=140, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + sbt, G_.glass_button(PT + "S3", "Rebirth", "secondary", w=PT_MI - 292, h=34, size=13)))
    assert 20 + 96 + 8 + 20 + 120 + 6 + 20 + 60 + 6 + 20 + 40 + 6 + 20 + 20 + 10 + 34 <= PT_SE_H and 30 + 20 + 22 + 18 <= 96, "0.3.58: the selected pet card fits"
    fu = PT + "Fu"
    ap.append(("#" + md, G_.glass_group(fu, PT_M, PT_FU_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    fuh = PT + "Fuh"
    ap.append(("#" + fu, G_.glass_group(fuh, PT_MI, 24, layout="Left")))
    ap.append(("#" + fuh, lab(None, "PET FUSING", 15, "accentHi", bold=True, w=200, h=24)))
    ap.append(("#" + fuh, lab(PT + "Fh", "", 12, "dim", w=PT_MI - 200, h=24, halign="End")))
    fr = PT + "Frow"
    ap.append(("#" + fu, G_.glass_group(fr, PT_MI, 84, layout="Left", anchor={"top": 8})))
    fgw_, _fgh = SUI.glass_grid_size(4, 1, 64)
    ap.append(("#" + fr, G_.glass_grid(PT + "FG", 4, 1, drag=False, slot=64, icon=52)))
    ap.append(("#" + fr, lab(None, ">", 22, "action", bold=True, w=36, h=64, halign="Center")))
    frr = PT + "Fres"
    ap.append(("#" + fr, G_.glass_group(frr, 140, 84, layout="Top")))
    ap.append(("#" + frr, G_.glass_grid(PT + "FR", 1, 1, drag=False, slot=64, icon=52, anchor={"left": 38})))
    ap.append(("#" + frr, lab(PT + "Fn", "", 12, "title", bold=True, w=140, h=18, halign="Center", anchor={"top": 2})))
    assert fgw_ + 36 + 140 <= PT_MI, "0.3.58: the fusing row fits"
    ap.append(("#" + fu, lab(PT + "F1", "", 14, "title", bold=True, w=PT_MI, h=20, anchor={"top": 6})))
    ap.append(("#" + fu, lab(PT + "F2", "", 12, "dim", w=PT_MI, h=18)))
    ap.sets.append((PT + "F2", "Text", PT_TXT["fuseRule"]))
    two_holder(fu, PT + "F3", PT_MI, 18, 12, ("green", "red"), bold=True)
    fb = PT + "Fb"
    ap.append(("#" + fu, G_.glass_group(fb, PT_MI, 32, layout="Left", anchor={"top": 8})))
    ap.append(("#" + fb, "Group { Anchor: (Width: %d); }" % (PT_MI - 140)))
    ap.append(("#" + fb, G_.glass_button(PT + "Fz", "Fuse", "primary", w=140, h=32, size=14)))
    assert 20 + 24 + 8 + 84 + 6 + 20 + 18 + 18 + 8 + 32 <= PT_FU_H, ("0.3.58: the fusing panel fits", PT_FU_H)
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== RIGHT: HATCHERY + EGGS
    rt = PT + "Rt"
    ap.append(("#" + body, G_.glass_group(rt, PT_R, IV_BODY_H, layout="Top")))
    ha = PT + "Ha"
    ap.append(("#" + rt, G_.glass_group(ha, PT_R, PT_HA_H, role="panel", layout="Top", pad=10)))
    hah = PT + "Hah"
    ap.append(("#" + ha, G_.glass_group(hah, PT_RI, 24, layout="Left")))
    ap.append(("#" + hah, lab(None, "HATCHERY", 15, "accentHi", bold=True, w=200, h=24)))
    ap.append(("#" + hah, lab(PT + "Hc", "", 14, "xp", bold=True, w=PT_RI - 200, h=24, halign="End")))
    for k_ in range(PT_HRN):
        hr = "%sH%d" % (PT, k_)
        ap.append(("#" + ha, G_.glass_group(hr, PT_RI, 48, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + hr, G_.glass_grid(hr + "I", 1, 1, drag=False, slot=44, icon=36, anchor={"top": 2})))
        hx = hr + "X"
        ap.append(("#" + hr, G_.glass_group(hx, PT_HTW, 48, layout="Top", anchor={"left": 8})))
        rar_holder(hx, hr + "N", PT_HTW, 20, 13, anchor={"top": 2})
        two_holder(hx, hr + "S", PT_HTW, 16, 12, ("dim", "green", "red"), bold=True)
        ap.append(("#" + hx, 'Group #%sB { Anchor: (Width: %d, Height: 6, Top: 2); LayoutMode: Left; Background: %s; }' % (hr, PT_HTW, IV_TRACK)))
        ap.append(("#" + hr, G_.glass_button(hr + "Go", "", "secondary", w=96, h=30, size=12, anchor={"left": 8, "top": 9})))
    ap.append(("#" + ha, lab(PT + "Hf", "", 11, "dim", w=PT_RI, h=18, anchor={"top": 4})))
    assert 20 + 24 + PT_HRN * 52 + 22 <= PT_HA_H and 2 + 20 + 16 + 2 + 6 <= 48 and PT_HTW >= 260, ("0.3.58: the Hatchery fits", PT_HTW)
    eg = PT + "Eg"
    ap.append(("#" + rt, G_.glass_group(eg, PT_R, PT_EG_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    egh = PT + "Egh"
    ap.append(("#" + eg, G_.glass_group(egh, PT_RI, 24, layout="Left")))
    ap.append(("#" + egh, lab(None, "EGGS", 15, "accentHi", bold=True, w=120, h=24)))
    ap.append(("#" + egh, lab(PT + "En", "", 12, "dim", w=PT_RI - 120, h=24, halign="End")))
    ap.sets.append((PT + "En", "Text", PT_TXT["eggsNote"]))
    ehr = PT + "Ehr"
    ap.append(("#" + eg, G_.glass_group(ehr, PT_RI, 28, layout="Left", anchor={"top": 4})))
    ap.append(("#" + ehr, lab(PT + "Eh", "", 12, "dim", bold=True, w=PT_RI - 110, h=28)))
    ap.append(("#" + ehr, G_.glass_button(PT + "Ep", "Place", "secondary", w=110, h=28, size=12)))
    egw_, egh_ = SUI.glass_grid_size(PT_EGC, PT_EGR, 52)
    ap.append(("#" + eg, G_.glass_grid(PT + "E", PT_EGC, PT_EGR, drag=False, slot=52, icon=44, anchor={"top": 4})))
    ap.append(("#" + eg, lab(PT + "Ch", "", 12, "dim", bold=True, w=PT_RI, h=18, anchor={"top": 6})))
    ap.sets.append((PT + "Ch", "Text", PT_TXT["craftH"]))
    for k_ in range(PT_CRN):
        cr = "%sC%d" % (PT, k_)
        ap.append(("#" + eg, G_.glass_group(cr, PT_RI, 26, layout="Left", anchor={"bottom": 2})))
        ap.append(("#" + cr, lab(cr + "N", "", 12, "title", bold=True, w=PT_CRN_W, h=26)))
        two_holder(cr, cr + "C", PT_CRW, 26, 11, ("green", "red"), anchor={"left": 6})
        ap.append(("#" + cr, G_.glass_button(cr + "Go", "Craft", "secondary", w=PT_CRB_W, h=24, size=12, anchor={"left": 6, "top": 1})))
    ap.append(("#" + eg, lab(None, "UPGRADE THE SELECTED EGG", 12, "dim", bold=True, w=PT_RI, h=18, anchor={"top": 6})))
    ub = PT + "Ub"
    ap.append(("#" + eg, G_.glass_group(ub, PT_RI, 58, role="inset", layout="Top", pad=6, anchor={"top": 4})))
    ap.append(("#" + ub, lab(PT + "U1", "", 13, "title", bold=True, w=PT_RI - 12, h=20)))
    ubr = PT + "Ubr"
    ap.append(("#" + ub, G_.glass_group(ubr, PT_RI - 12, 24, layout="Left")))
    two_holder(ubr, PT + "Uc", PT_UPW, 24, 11, ("green", "red"))
    ap.append(("#" + ubr, G_.glass_button(PT + "Up", "Upgrade", "primary", w=96, h=24, size=12, anchor={"left": 6})))
    assert egw_ <= PT_RI and 20 + 24 + 4 + 28 + 4 + egh_ + 6 + 18 + PT_CRN * 28 + 6 + 18 + 4 + 58 <= PT_EG_H, ("0.3.58: the eggs panel fits", egw_, egh_, PT_EG_H)
    # one 1080p screen, nothing scrolls (Skyy: "no zooming or scrolling"): the root is the kit's ceiling, every column adds up to the body
    assert (IV_PAGE_H <= SUI.MAX_PAGE_H and IV_PAGE_W <= SUI.MAX_PAGE_W and PT_EQ_H + 8 + PT_PE_H == IV_BODY_H and PT_SE_H + 8 + PT_FU_H == IV_BODY_H
            and PT_HA_H + 8 + PT_EG_H == IV_BODY_H and PT_L + PT_M + PT_R + 2 * IV_GAP == IV_IW), "0.3.58: the pets screen fits one 1080p screen"
    # ---- row 3: the caption + key hints
    hn = PT + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(PT + "K%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate((("LMB", "Select"), ("Tab / Esc", "Close")))]
    hw = sum(w_ for _m, w_ in parts)
    ap.append(("#" + hn, lab(PT + "Cap", "", 14, "dim", w=IV_IW - hw - 20, h=IV_HINT_H)))
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    binds = [("#%sT%d" % (PT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + PT + "Close", "close"), ("#" + PT + "Full", "full"),
                                                                                  ("#" + PT + "Pp", "pg:-1"), ("#" + PT + "Pnx", "pg:1")]
    return ap, binds


PT_AP, PT_BINDS = _pt_page()
SUI.check_page(PT_AP, PT)
for _p, _mk in PT_AP:
    SUI.check_markup(_mk, prefix=PT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.58: the pets screen never scrolls"
_pt_ids = set(i_ for _p, mk_ in PT_AP for i_ in SUI._static_ids(mk_))
for _s, _a in PT_BINDS:
    assert _s[1:] in _pt_ids, ("0.3.58: binding target", _s)
PT_DYN = (["Coins", "Close", "Full", "Cap", "Pn", "Rr", "Ar", "Pp", "Pg", "Pnx", "G", "Pf", "Pe2", "SI", "Stg", "SL", "SB", "SX", "Sa", "Sat", "S1", "S2", "S3",
           "Fh", "FG", "FR", "Fn", "F1", "F2", "F30", "F31", "Fz", "Hc", "Hf", "En", "Eh", "Ep", "E", "Ch", "U1", "Uc0", "Uc1", "Up"]
          + ["Q%d%s" % (s_, x_) for s_ in (1, 2) for x_ in ("I", "L", "S", "Out")] + ["Q2Go"]
          + ["Q%dN%d" % (s_, k_) for s_ in (1, 2) for k_ in range(7)] + ["SN%d" % k_ for k_ in range(7)] + ["Sb%d" % k_ for k_ in range(6)]
          + ["Sw%d%d" % (i_, v_) for i_ in range(3) for v_ in range(2)] + ["Sg0", "Sg1"]
          + ["H%d%s" % (k_, x_) for k_ in range(PT_HRN) for x_ in ("", "I", "B", "Go", "S0", "S1", "S2")] + ["H%dN%d" % (k_, v_) for k_ in range(PT_HRN) for v_ in range(7)]
          + ["C%d%s" % (k_, x_) for k_ in range(PT_CRN) for x_ in ("", "N", "C0", "C1", "Go")])
for _g in PT_DYN:
    assert PT + _g in _pt_ids, "0.3.58: the pets screen has #" + PT + _g
_pt_tok = SUI.proven_tokens(list(PT_AP))
PT_UNPROVEN = sorted(k_ for k_, g_ in _pt_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_)))
assert set(PT_UNPROVEN) <= set(["SlotBackground"]), "0.3.58: only SlotBackground (proven on the inventory page, TEST 282): %s" % PT_UNPROVEN
assert not [k_ for k_ in _pt_tok if k_ in ("MouseEntered", "MouseExited", "TooltipText")], "0.3.58: no hover events / tooltips of ours"
SUI.assert_glass_paths(PT_AP)
PT_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in PT_AP)
PT_RUNTIME_MAX = len(PT_ROLES) + len(PT_AREAS) + 1 + PT_HRN      # the chips + the XP fill + the Hatchery bar fills
PT_ELEMENTS = PT_SHELL_ELEMENTS + PT_RUNTIME_MAX
assert PT_ELEMENTS <= 800, "0.3.58: the pets screen stays well under the ~1,600 element budget (%d static + %d at run time)" % (PT_SHELL_ELEMENTS, PT_RUNTIME_MAX)
PT_LK, PT_LP, PT_LB = [], [], []
for _p, _mk in PT_AP:
    PT_LK.append("A")
    PT_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    PT_LB.append(SUI.render(_mk))
for _i, _pr, _v in PT_AP.sets:
    PT_LK.append("S")
    PT_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    PT_LB.append(_v)
for _s, _a in PT_BINDS:
    PT_LK.append("E")
    PT_LP.append(_s)
    PT_LB.append(_a)
assert PT_LK[0] == "A" and PT_LP[0] == "", "0.3.58: the page data starts with the root"
for _x in PT_LP + PT_LB:
    assert "@" not in _x and "\n" not in _x and len(_x.encode("utf-8")) < 60000, "0.3.58: a page line Java can hold"
print("0.3.58 pets screen: %d elements (shell %d + at most %d at run time; budget ~1,600), %d appends, %d b.set, %d bindings; unproven: %s"
      % (PT_ELEMENTS, PT_SHELL_ELEMENTS, PT_RUNTIME_MAX, len(PT_AP), len(PT_AP.sets), len(PT_BINDS), ", ".join(PT_UNPROVEN)))

'''
P.rep('''PKG = T["PKG"]
# 0.2: every class goes through mk()''', PT_PAGE.lstrip("\n") + '''PKG = T["PKG"]
# 0.2: every class goes through mk()''')

# ---------- the two new classes
P.rep('''skpg = mk("SkillPage", T["PAGE"])   # 0.3.57: ONE PAGE PER SKILL (the inventory's Skills tab)
''', '''skpg = mk("SkillPage", T["PAGE"])   # 0.3.57: ONE PAGE PER SKILL (the inventory's Skills tab)
ptd  = mk("PetsTabData")    # 0.3.58: the pets screen's data (LK / LP / LB, the run-time markup)
ptab = mk("PetsTab", T["PAGE"])     # 0.3.58: THE PETS TAB = ONE SCREEN
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, pl)''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, pl)''')

# ---------- PetsTabData constants + PetsTab fields / constructor (after the SkillPage constructor)
PT_DATA = r'''# 0.3.58: THE PETS SCREEN DATA (PetsTabData) + the PetsTab fields
F(ptd, "public static final String LK = %s;" % jstr("".join(PT_LK)))
F(ptd, "public static final String[] LP = %s;" % jarr(PT_LP))
F(ptd, "public static final String[] LB = %s;" % jarr(PT_LB))
F(ptd, "public static final String[] ROLES = %s;" % jarr(PT_ROLES))
F(ptd, "public static final String[] AREAS = %s;" % jarr(PT_AREAS))
for _n, _v in (("PER", PT_PER), ("HRN", PT_HRN), ("EGN", PT_EGC * PT_EGR), ("CRN", PT_CRN), ("SXW", PT_SXW), ("HBW", PT_HTW), ("CHW", PT_CHW), ("ACW", PT_ACW), ("CRW", PT_CRW), ("UPW", PT_UPW)):
    F(ptd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("CHIP", PT_CHIP), ("ST_CH", PT_ST_CH), ("ST_CHSEL", PT_ST_CHSEL), ("ST_ACH", PT_ST_ACH), ("ST_ACHSEL", PT_ST_ACHSEL), ("FILL8", PT_FILL8),
               ("FILL6", PT_FILL6), ("FILL6G", PT_FILL6G), ("HFOOT", PT_TXT["hfoot"])):
    F(ptd, "public static final String %s = %s;" % (_n, jstr(_v)))
for _f in ("public static volatile int OPENS = 0;", "public static volatile int STALE = 0;",
           "public volatile boolean closed;", "public boolean answered;", "public String via;", "public String tcap;", "public long seq;", "public long base;",
           "public String tok;", "public String ptok;", "public String sel;", "public int selSlot;", "public String esel;", "public int role;", "public int area;",
           "public int page;", "public int pages;", "public String[] pageIds;", "public String[] eggIds;", "public String[] crIds;", "public String upId;",
           "public String[] hRows;", "public String[] slotIds;", "public boolean ok;", "public String last;",
           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;", "public int calls;", "public boolean fresh;"):
    F(ptab, _f)
C(ptab, r"""
public PetsTab(@PR@ pr, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.via = via;
  this.closed = false;
  this.fresh = true;
  this.answered = false;
  this.tcap = "";
  this.seq = 0L;
  this.base = System.nanoTime() & 0xffffffL;
  this.tok = "";
  this.ptok = "";
  this.sel = "";
  this.selSlot = 0;
  this.esel = "";
  this.role = 0;
  this.area = 0;
  this.page = 0;
  this.pages = 1;
  this.pageIds = new String[0];
  this.eggIds = new String[0];
  this.crIds = new String[0];
  this.upId = "";
  this.hRows = new String[0];
  this.slotIds = new String[] { "", "" };
  this.ok = false;
  this.last = null;
  this.builds = 0;
  this.answers = 0;
  this.calls = 0;
}""")
'''
P.rep('''  this.srows = new java.util.ArrayList();
  this.builds = 0;
  this.answers = 0;
}""")
''', '''  this.srows = new java.util.ArrayList();
  this.builds = 0;
  this.answers = 0;
}""")
''' + PT_DATA)

# ---------- PetsTab.open BEFORE the skill page (its Pets tab opens this screen); the rest of PetsTab after the skill page
PT_OPEN = r'''# ---- 0.3.58: the PETS SCREEN opens (the inventory's / skill page's Pets tab, the pet + mount cards); null = SkyyPets has no pets:fn:tab /
# tabact (an older SkyyPets) or it could not open = the caller opens today's Pets page instead
M(ptab, r"""
public static @PKG@.PetsTab open(@REF@ ref, @ST@ st, @PR@ pr, String via) {
  if (@PKG@.InvCraft.fn("pets:fn:tab") == null || @PKG@.InvCraft.fn("pets:fn:tabact") == null) return null;
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  @PKG@.PetsTab pg = new @PKG@.PetsTab(pr, via);
  pg.pref = ref;
  pg.pst = st;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")
'''
P.rep('''# ---- 0.3.57: the inventory opened on a panel (the skill page's Requip / Charms / Inventory buttons): the mode is set BEFORE the open,
''', PT_OPEN + '''# ---- 0.3.57: the inventory opened on a panel (the skill page's Requip / Charms / Inventory buttons): the mode is set BEFORE the open,
''')
# the skill page's Pets tab = this screen (else today's page, as before)
P.rep('''M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
''', '''# 0.3.58: the Pets tab = the pets screen (false = it could not open: today's Pets page below)
M(skpg, r"""
public boolean petsTab() {
  @PKG@.PetsTab pg = null;
  try { pg = @PKG@.PetsTab.open(this.pref, this.pst, this.playerRef, "skill page"); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the pets screen failed: " + t); }
  if (pg == null) return false;
  this.answered = true;
  if (!still()) finish("pets");
  return true;
}""")
M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
  if (i == 2 && petsTab()) return;   // 0.3.58
''')

PT_JAVA = r'''# ================= 0.3.58 PetsTab: THE PETS TAB = ONE SCREEN (approved pets-page.png) =================
# Read only: pets:fn:tab (SkyyPets 0.4.28) - every action through pets:fn:tabact (the profile token from the read; SkyyPets checks it, the world
# thread, the same-op guard, and moves items only inside its own doors). Every bound click answers with ONE page packet.
M(ptab, r"""
public static String[] sp(String s, int n) { return s.split("\\|", n); }""")
M(ptab, r"""
public static String dec(String s) { return s == null ? "" : s.replace(String.valueOf((char) 31), "\n"); }""")
M(ptab, r"""
public static int ni(String s, int d) { return @PKG@.InvPage.toInt(s, d); }""")
M(ptab, r"""
public static String dur(long ms) {
  long s = ms <= 0L ? 0L : (ms + 999L) / 1000L;
  if (s >= 3600L) { long m = (s % 3600L) / 60L; return (s / 3600L) + "h " + (m < 10L ? "0" : "") + m + "m"; }
  if (s >= 60L) return (s / 60L) + "m " + (s % 60L) + "s";
  return s + "s";
}""")
M(ptab, r"""
public Object call(String key, Object arg) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null) return null;
  try { return f.apply(arg); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: " + key + " failed: " + t); return null; }
}""")
M(ptab, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyyPtabCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(ptab, r"""
public void finish(String why) { this.closed = true; }""")
M(ptab, r"""
public void shut() { finish("closed"); this.close(); }""")
M(ptab, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(ptab, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.answers = this.answers + 1;
  this.rebuild();
}""")
# a grid cell: a NEW ItemStack(id, qty) without metadata, only for ids the server knows (else the name + tooltip alone)
M(ptab, r"""
public static @IGS@ cell(String id, int qty, String name, String desc) {
  @IGS@ g = new @IGS@();
  if (id != null && id.length() > 0 && id.length() < 120 && @PKG@.InvPage.known(id)) g.setItemStack(new @IS@(id, qty < 1 ? 1 : (qty > 999 ? 999 : qty)));
  if (name != null && name.length() > 0) g.setName(name);
  if (desc != null && desc.length() > 0) g.setDescription(desc);
  return g;
}""")
# one variant of a keep_holder shows (n variants #<base>0..n-1, all with the text)
M(ptab, r"""
public static void hold(@UCB@ b, String base, int n, int which, String text) {
  for (int k = 0; k < n; k++) {
    b.set("#" + base + k + ".Text", text == null ? "" : text);
    b.set("#" + base + k + ".Visible", k == which);
  }
}""")
M(ptab, r"""
public static int rar(String s) { int r = ni(s, 0); return r < 0 || r > 6 ? 0 : r; }""")
M(ptab, r"""
public static java.util.ArrayList one(@IGS@ g) { java.util.ArrayList l = new java.util.ArrayList(); l.add(g); return l; }""")
# the two slot cards (s|slot|id|name|rar|lv|cap|icon|ride|fight|tip)
M(ptab, r"""
public void fillSlots(@UCB@ b, java.util.ArrayList sl, String[] hd) {
  boolean open2 = hd.length > 4 && "1".equals(hd[4]);
  for (int s = 1; s <= 2; s++) {
    String[] f = null;
    for (int i = 0; i < sl.size(); i++) { String[] x = (String[]) sl.get(i); if (x.length >= 11 && ni(x[1], 0) == s) f = x; }
    String id = f == null ? "" : f[2];
    this.slotIds[s - 1] = id;
    String q = "SkyyPtabQ" + s;
    boolean on = id.length() > 0;
    b.set("#" + q + "I.Slots", one(on ? cell(f[7], 1, f[3] + " - Lv " + f[5], dec(f[10])) : new @IGS@()));
    hold(b, q + "N", 7, on ? rar(f[4]) : 0, on ? f[3] : (s == 1 ? "Pet slot - empty" : (open2 ? "Mount slot - empty" : "Mount slot - locked")));
    b.set("#" + q + "L.Text", on ? "Lv " + f[5] + " / " + f[6] : "");
    String sub;
    if (s == 1) sub = !on ? "Select a pet, then Pet slot" : ("1".equals(f[9]) ? "Fights + full buffs" : "Follows you, full buffs");
    else if (!open2) sub = @PKG@.MenuUtil.clip(hd.length > 5 && hd[5].length() > 0 ? hd[5] : "Locked", 40);
    else sub = !on ? "Mounts and Fighters go here" : ("1".equals(f[8]) ? "Summon = ride" : "Buffs only - no riding");
    b.set("#" + q + "S.Text", sub);
    b.set("#" + q + "Out.Visible", on);
    if (s == 2) b.set("#" + q + "Go.Visible", on && "1".equals(f[8]));
  }
}""")
# the chips (role + area, appended at run time; the chosen one in the selected tab look)
M(ptab, r"""
public void fillChips(@UCB@ b, @UEB@ ev, java.util.ArrayList ar) {
  for (int i = 0; i < @PKG@.PetsTabData.ROLES.length; i++) {
    boolean on = i == this.role;
    b.appendInline("#SkyyPtabRr", @PKG@.PetsTabData.CHIP.replace("{I}", "Ro" + i).replace("{W}", String.valueOf(@PKG@.PetsTabData.CHW))
        .replace("{S}", on ? @PKG@.PetsTabData.ST_CHSEL : @PKG@.PetsTabData.ST_CH));
    b.set("#SkyyPtabRo" + i + ".Text", @PKG@.PetsTabData.ROLES[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyPtabRo" + i, @EVD@.of("a", "ro:" + i));
  }
  int n = ar.size() < @PKG@.PetsTabData.AREAS.length ? ar.size() : @PKG@.PetsTabData.AREAS.length;
  if (n == 0) n = 1;
  for (int i = 0; i < n; i++) {
    String lb = @PKG@.PetsTabData.AREAS[i];
    if (i < ar.size()) { String[] f = (String[]) ar.get(i); if (f.length >= 3 && f[2].length() > 0) lb = f[2]; }
    if (lb.equals("Exploration")) lb = "Explore";
    if (lb.length() > 8) lb = lb.substring(0, 8);
    boolean on = i == this.area;
    b.appendInline("#SkyyPtabAr", @PKG@.PetsTabData.CHIP.replace("{I}", "Ao" + i).replace("{W}", String.valueOf(@PKG@.PetsTabData.ACW))
        .replace("{S}", on ? @PKG@.PetsTabData.ST_ACHSEL : @PKG@.PetsTabData.ST_ACH));
    b.set("#SkyyPtabAo" + i + ".Text", lb);
    ev.addEventBinding(@BT@.Activating, "#SkyyPtabAo" + i, @EVD@.of("a", "ar:" + i));
  }
}""")
# the pets grid (p|id|rar|name|lv|icon|slot|tip) - pages of PER, nothing scrolls
M(ptab, r"""
public void fillGrid(@UCB@ b, @UEB@ ev, java.util.ArrayList ps, String[] hd) {
  int per = @PKG@.PetsTabData.PER;
  int n = ps.size() < per ? ps.size() : per;
  this.pageIds = new String[n];
  java.util.ArrayList sl = new java.util.ArrayList();
  for (int i = 0; i < per; i++) {
    if (i < n) {
      String[] f = (String[]) ps.get(i);
      this.pageIds[i] = f[1];
      String nm = f[3] + " - Lv " + f[4] + (f[1].equals(this.sel) ? "  (selected)" : "");
      sl.add(cell(f[5], 1, nm, dec(f[7])));
    } else sl.add(new @IGS@());
  }
  b.set("#SkyyPtabG.Slots", sl);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyPtabG", @EVD@.of("a", "g").append("t", this.tok), false);
  int cnt = ni(hd[2], 0), mx = ni(hd[3], 0), shown = ni(hd[6], 0);
  this.page = ni(hd[7], 0);
  this.pages = ni(hd[8], 1);
  if (this.pages < 1) this.pages = 1;
  b.set("#SkyyPtabPn.Text", cnt + " / " + mx + (shown != cnt ? "   (" + shown + " shown)" : ""));
  b.set("#SkyyPtabPg.Text", "Page " + (this.page + 1) + " / " + this.pages);
  String note = "";
  if ("1".equals(hd.length > 13 ? hd[13] : "0")) note = "Your pet file could not be read - an admin has been told. Nothing changes until it is fixed.";
  else if (cnt == 0 && "1".equals(hd.length > 14 ? hd[14] : "0")) note = "No pet yet - choose your first pet on the Full page.";
  else if (cnt == 0) note = "No pets yet - craft an egg (right), then hatch it in the Hatchery.";
  else if (shown == 0) note = "No pets match this filter - pick All.";
  b.set("#SkyyPtabPe2.Text", note);
}""")
# the selected pet (d|id|name|rar|lv|cap|xp|need|icon|tags|slot|rebReady|rb|rm|tip + b / w / g / t lines)
M(ptab, r"""
public void fillSel(@UCB@ b, String[] d, java.util.ArrayList bl, java.util.ArrayList wl, java.util.ArrayList gl, String[] tl) {
  boolean on = d != null && d.length >= 15;
  this.sel = on ? d[1] : "";
  this.selSlot = on ? ni(d[10], 0) : 0;
  b.set("#SkyyPtabSI.Slots", one(on ? cell(d[8], 1, d[2] + " - Lv " + d[4], dec(d[14])) : new @IGS@()));
  hold(b, "SkyyPtabSN", 7, on ? rar(d[3]) : 0, on ? d[2] : "No pet selected");
  b.set("#SkyyPtabStg.Text", on ? d[9] : "Pick a pet on the left");
  long xp = on ? @PKG@.InvPage.toLong(d[6], 0L) : 0L;
  long need = on ? @PKG@.InvPage.toLong(d[7], 0L) : 0L;
  b.set("#SkyyPtabSL.Text", on ? "Lv " + d[4] + " / " + d[5] : "");
  b.set("#SkyyPtabSX.Text", !on ? "" : (need > 0L ? @PKG@.MenuUtil.fmt(xp) + " / " + @PKG@.MenuUtil.fmt(need) + " pet XP" : "MAX LEVEL"));
  int w = !on ? 0 : (need > 0L ? @PKG@.InvPage.barW(xp, need, @PKG@.PetsTabData.SXW) : @PKG@.PetsTabData.SXW);
  if (w > 0) b.appendInline("#SkyyPtabSB", @PKG@.PetsTabData.FILL8.replace("{W}", String.valueOf(w)));
  for (int i = 0; i < 6; i++) {
    String t = "";
    if (i < bl.size()) { String[] f = (String[]) bl.get(i); t = f.length > 1 ? f[1] : ""; }
    if (i == 0 && on && bl.size() == 0) t = "Nothing yet";
    b.set("#SkyyPtabSb" + i + ".Text", t);
  }
  for (int i = 0; i < 3; i++) {
    String[] f = null;
    if (i < wl.size()) f = (String[]) wl.get(i);
    hold(b, "SkyyPtabSw" + i, 2, f != null && f.length > 2 && "1".equals(f[1]) ? 0 : 1, f != null && f.length > 2 ? f[2] : "");
  }
  for (int i = 0; i < 2; i++) { String[] f = null; if (i < gl.size()) f = (String[]) gl.get(i); b.set("#SkyyPtabSg" + i + ".Text", f != null && f.length > 1 ? f[1] : ""); }
  b.set("#SkyyPtabSa.Text", tl != null && tl.length > 2 ? tl[1] : "");
  b.set("#SkyyPtabSat.Text", tl != null && tl.length > 2 ? tl[2] : "");
  b.set("#SkyyPtabS1.Text", this.selSlot == 1 ? "Take out" : "Pet slot");
  b.set("#SkyyPtabS2.Text", this.selSlot == 2 ? "Take out" : "Mount slot");
  b.set("#SkyyPtabS3.Text", on && "1".equals(d[11]) ? "Rebirth" : (on ? "Rebirth (Lv " + d[5] + ")" : "Rebirth"));
}""")
# PET FUSING (f|have|need|next|ok|why|group + fo|id|icon|lv x <= 4 + fr|icon|rar)
M(ptab, r"""
public void fillFuse(@UCB@ b, String[] f, java.util.ArrayList fo, String[] fr) {
  boolean on = f != null && f.length >= 7;
  java.util.ArrayList sl = new java.util.ArrayList();
  for (int i = 0; i < 4; i++) {
    String[] x = null;
    if (i < fo.size()) x = (String[]) fo.get(i);
    sl.add(x != null && x.length >= 4 ? cell(x[2], 1, "Lv " + x[3], "") : new @IGS@());
  }
  b.set("#SkyyPtabFG.Slots", sl);
  b.set("#SkyyPtabFR.Slots", one(on && fr != null && fr.length >= 3 && f[3].length() > 0 ? cell(fr[1], 1, f[3], "") : new @IGS@()));
  b.set("#SkyyPtabFn.Text", on ? f[3] : "");
  b.set("#SkyyPtabFh.Text", on ? f[2] + " same pets -> next rarity" : "");
  b.set("#SkyyPtabF1.Text", on ? f[1] + " / " + f[2] + " " + f[6] : "Pick a pet to see its fusing group");
  hold(b, "SkyyPtabF3", 2, on && "1".equals(f[4]) ? 0 : 1, !on ? "" : ("1".equals(f[4]) ? "Ready - press Fuse twice to fuse " + f[2] + " into 1" : @PKG@.MenuUtil.clip(f[5], 70)));
}""")
# the HATCHERY (h|n|state|egg|name|rar|left|total|hid|sub), 6 rows
M(ptab, r"""
public void fillHatch(@UCB@ b, @UEB@ ev, java.util.ArrayList hl, String[] hd) {
  int slots = ni(hd[9], 0), shown = ni(hd[10], 0), used = ni(hd[11], 0), cut = ni(hd[12], 0);
  int n = @PKG@.PetsTabData.HRN;
  this.hRows = new String[n];
  b.set("#SkyyPtabHc.Text", used + " / " + slots + " slots" + (cut > 0 ? "   -" + cut + "% time" : ""));
  for (int i = 0; i < n; i++) {
    String r = "SkyyPtabH" + i;
    String[] f = null;
    for (int j = 0; j < hl.size(); j++) { String[] x = (String[]) hl.get(j); if (x.length >= 10 && ni(x[1], -1) == i + 1) f = x; }
    String st = f == null ? (i + 1 > slots ? "lock" : "none") : f[2];
    if ("empty".equals(st)) st = "none";
    this.hRows[i] = st + "|" + (i + 1) + "|" + (f == null ? "" : f[8]);
    boolean egg = f != null && ("wait".equals(st) || "ready".equals(st));
    b.set("#" + r + "I.Slots", one(egg ? cell(f[3], 1, f[4], f[9]) : new @IGS@()));
    String nm = egg ? f[4] : ("lock".equals(st) ? "Locked slot" : ("bad".equals(st) ? "Unreadable slot" : "Empty slot"));
    hold(b, r + "N", 7, egg ? rar(f[5]) : 0, nm);
    String sub;
    int sv = 0;
    String btn = "";
    if ("ready".equals(st)) { sub = "Ready!"; sv = 1; btn = "Hatch"; }
    else if ("wait".equals(st)) { sub = dur(@PKG@.InvPage.toLong(f[6], 0L)) + " left"; btn = "Take out"; }
    else if ("bad".equals(st)) { sub = "This line could not be read - an admin can clear it"; sv = 2; }
    else if ("lock".equals(st)) sub = "Beastmastery tree: +1 slot";
    else { sub = "Empty - select an egg, then Place"; btn = "Place"; }
    hold(b, r + "S", 3, sv, sub);
    if (egg) {
      long tot = @PKG@.InvPage.toLong(f[7], 0L), left = @PKG@.InvPage.toLong(f[6], 0L);
      int w = "ready".equals(st) ? @PKG@.PetsTabData.HBW : @PKG@.InvPage.barW(tot - left, tot, @PKG@.PetsTabData.HBW);
      if (w > 0) b.appendInline("#" + r + "B", ("ready".equals(st) ? @PKG@.PetsTabData.FILL6G : @PKG@.PetsTabData.FILL6).replace("{W}", String.valueOf(w)));
    }
    b.set("#" + r + "Go.Text", btn);
    b.set("#" + r + "Go.Visible", btn.length() > 0);
    if (btn.length() > 0) ev.addEventBinding(@BT@.Activating, "#" + r + "Go", @EVD@.of("a", "hr:" + i).append("t", this.tok));
  }
  b.set("#SkyyPtabHf.Text", shown > n ? (shown - n) + " more slots on the Full page" : @PKG@.PetsTabData.HFOOT);
}""")
# EGGS (e|id|name|rar|count|tip) + CRAFT (c|i|id|name|rar|can|up|cost|from) + UPGRADE THE SELECTED EGG
M(ptab, r"""
public void fillEggs(@UCB@ b, @UEB@ ev, java.util.ArrayList el, java.util.ArrayList cl) {
  int cap = @PKG@.PetsTabData.EGN;
  int n = el.size() < cap ? el.size() : cap;
  this.eggIds = new String[n];
  boolean have = false;
  for (int i = 0; i < el.size(); i++) { String[] x = (String[]) el.get(i); if (x[1].equals(this.esel)) have = true; }
  if (!have) {
    this.esel = "";
    for (int i = 0; i < el.size() && this.esel.length() == 0; i++) {
      String[] x = (String[]) el.get(i);
      for (int j = 0; j < cl.size(); j++) { String[] c = (String[]) cl.get(j); if ("1".equals(c[6]) && c[8].equals(x[1])) this.esel = x[1]; }
    }
    if (this.esel.length() == 0 && el.size() > 0) this.esel = ((String[]) el.get(0))[1];
  }
  java.util.ArrayList sl = new java.util.ArrayList();
  String selName = "";
  for (int i = 0; i < cap; i++) {
    if (i < n) {
      String[] x = (String[]) el.get(i);
      this.eggIds[i] = x[1];
      boolean me = x[1].equals(this.esel);
      sl.add(cell(x[1], ni(x[4], 1), x[2] + " x" + x[4] + (me ? "  (selected)" : ""), dec(x[5])));
    } else sl.add(new @IGS@());
  }
  for (int i = 0; i < el.size(); i++) { String[] x = (String[]) el.get(i); if (x[1].equals(this.esel)) selName = x[2]; }
  b.set("#SkyyPtabE.Slots", sl);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyPtabE", @EVD@.of("a", "e").append("t", this.tok), false);
  b.set("#SkyyPtabEh.Text", el.size() == 0 ? "YOUR EGGS - none yet" : "YOUR EGGS  " + el.size() + " kinds" + (el.size() > cap ? " - the first " + cap + " here" : "")
      + (selName.length() > 0 ? "  -  " + @PKG@.MenuUtil.clip(selName, 24) : ""));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabEp", @EVD@.of("a", "place").append("t", this.tok));
  int k = 0;
  int crn = @PKG@.PetsTabData.CRN;
  this.crIds = new String[crn];
  this.upId = "";
  String upTxt = "";
  String upCost = "";
  boolean upCan = false;
  for (int j = 0; j < cl.size(); j++) {
    String[] c = (String[]) cl.get(j);
    if (c.length < 9) continue;
    if ("1".equals(c[6])) {
      if (c[8].length() > 0 && c[8].equals(this.esel)) { this.upId = c[2]; upTxt = selName + "  ->  " + c[3]; upCost = c[7]; upCan = "1".equals(c[5]); }
      continue;
    }
    if (k >= crn) continue;
    String r = "SkyyPtabC" + k;
    this.crIds[k] = c[2];
    b.set("#" + r + ".Visible", true);
    String cn = c[3];                                  // "Common Mining Egg" -> "Mining" (the header says CRAFT Common eggs; fix round tab2fix: room for the cost)
    if (cn.startsWith("Common ")) cn = cn.substring(7);
    if (cn.endsWith(" Egg")) cn = cn.substring(0, cn.length() - 4);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(cn, 14));
    hold(b, r + "C", 2, "1".equals(c[5]) ? 0 : 1, @PKG@.MenuUtil.clip(c[7], 90));
    ev.addEventBinding(@BT@.Activating, "#" + r + "Go", @EVD@.of("a", "cr:" + k).append("t", this.tok));
    k = k + 1;
  }
  for (int j = k; j < crn; j++) { this.crIds[j] = ""; b.set("#SkyyPtabC" + j + ".Visible", false); }
  if (this.upId.length() == 0) {
    upTxt = this.esel.length() == 0 ? "Select an egg above to upgrade it" : (selName.length() > 0 ? selName : "This egg") + " has no upgrade (only Common -> Uncommon for now)";
    upCost = "";
  }
  b.set("#SkyyPtabU1.Text", @PKG@.MenuUtil.clip(upTxt, 60));
  hold(b, "SkyyPtabUc", 2, upCan || upCost.length() == 0 ? 0 : 1, @PKG@.MenuUtil.clip(upCost, 90));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabUp", @EVD@.of("a", "up").append("t", this.tok));
}""")
M(ptab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.PetsTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.PetsTabData.LP[i];
    String y = @PKG@.PetsTabData.LB[i];
    if (k == 'A') b.appendInline(x.length() == 0 ? (String) null : x, y);
    else if (k == 'S') b.set(x, y);
    else if (k == 'E') ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
  }
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  this.builds = this.builds + 1;
  java.util.UUID u = this.playerRef.getUuid();
  long c = -1L;
  try { c = @PKG@.MenuUtil.purse(u); } catch (Throwable t) { c = -1L; }
  b.set("#SkyyPtabCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabQ1Out", @EVD@.of("a", "out:1").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabQ2Out", @EVD@.of("a", "out:2").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabQ2Go", @EVD@.of("a", "ride").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabS1", @EVD@.of("a", "s1").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabS2", @EVD@.of("a", "s2").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabS3", @EVD@.of("a", "reb").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabFz", @EVD@.of("a", "fuse").append("t", this.tok));
  Object o = call("pets:fn:tab", new Object[] { u, this.sel, Integer.valueOf(this.role), Integer.valueOf(this.area), Integer.valueOf(this.page),
                                                Integer.valueOf(@PKG@.PetsTabData.PER), this.esel, Integer.valueOf(this.fresh ? 1 : 0) });
  this.fresh = false;                                 // fix (critic tab2-crit-safety 1): the first read of a newly opened screen clears an old two-press ask
  this.calls = this.calls + 1;
  String s = o instanceof String ? (String) o : null;
  this.last = s;
  this.ok = s != null && s.startsWith("ok|");
  if (!this.ok) {
    this.ptok = "";
    this.pageIds = new String[0];
    this.eggIds = new String[0];
    this.crIds = new String[0];
    this.hRows = new String[0];
    this.upId = "";
    b.set("#SkyyPtabPe2.Text", "Your pets could not be read right now - try again in a moment, or open the Full page.");
    if (this.tcap.length() == 0) this.tcap = "Your pets are not ready yet";
    b.set("#SkyyPtabCap.Text", this.tcap);
    return;
  }
  String[] ls = s.split("\n");
  String[] hd = sp(ls[0], 16);
  if (hd.length < 15) { this.ok = false; b.set("#SkyyPtabCap.Text", "Your pets could not be read right now"); return; }
  this.ptok = hd[1];
  java.util.ArrayList ar = new java.util.ArrayList(), sl = new java.util.ArrayList(), ps = new java.util.ArrayList(), bl = new java.util.ArrayList();
  java.util.ArrayList wl = new java.util.ArrayList(), gl = new java.util.ArrayList(), fo = new java.util.ArrayList(), el = new java.util.ArrayList();
  java.util.ArrayList cl = new java.util.ArrayList(), hl = new java.util.ArrayList();
  String[] d = null, tl = null, fu = null, fr = null;
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("a|")) ar.add(sp(l, 3));
    else if (l.startsWith("s|")) sl.add(sp(l, 11));
    else if (l.startsWith("p|")) ps.add(sp(l, 8));
    else if (l.startsWith("d|")) d = sp(l, 15);
    else if (l.startsWith("b|")) bl.add(sp(l, 2));
    else if (l.startsWith("w|")) wl.add(sp(l, 3));
    else if (l.startsWith("g|")) gl.add(sp(l, 2));
    else if (l.startsWith("t|")) tl = sp(l, 3);
    else if (l.startsWith("fo|")) fo.add(sp(l, 4));
    else if (l.startsWith("fr|")) fr = sp(l, 3);
    else if (l.startsWith("f|")) fu = sp(l, 7);
    else if (l.startsWith("e|")) el.add(sp(l, 6));
    else if (l.startsWith("c|")) cl.add(sp(l, 9));
    else if (l.startsWith("h|")) hl.add(sp(l, 10));
  }
  if (this.tcap.length() > 0) b.set("#SkyyPtabCap.Text", this.tcap);
  try { fillSlots(b, sl, hd); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the slot cards failed: " + t); }
  try { fillChips(b, ev, ar); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the filters failed: " + t); }
  try { fillSel(b, d, bl, wl, gl, tl); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the selected pet failed: " + t); }
  try { fillGrid(b, ev, ps, hd); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the pets grid failed: " + t); }
  try { fillFuse(b, fu, fo, fr); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: fusing failed: " + t); }
  try { fillHatch(b, ev, hl, hd); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the Hatchery failed: " + t); }
  try { fillEggs(b, ev, el, cl); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the eggs failed: " + t); }
}""")
# ---- the actions (each answers with ONE packet: a redraw, a caption, a page that replaces this one, or the close)
M(ptab, r"""
public void hub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    if (tab != null && tab.length() > 0) r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("pets screen: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
M(ptab, r"""
public void tabGo(int i) {
  this.answered = true;
  if (i == 0) {
    @PKG@.InvPage pg = null;
    try { pg = @PKG@.InvState.openAt(this.pref, this.pst, this.playerRef, "pets screen", "c", -1); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("pets screen: the inventory failed: " + t); }
    if (pg == null) { if (still()) say("The inventory could not open here"); return; }
    if (!still()) finish("inventory");
    return;
  }
  if (i == 1) {
    @PKG@.SkillPage sp = null;
    try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, @PKG@.SkillPage.lastOf(this.playerRef.getUuid()), "pets screen"); } catch (Throwable t) { sp = null; @PKG@.MenuUtil.warn("pets screen: the skill page failed: " + t); }
    if (sp == null) { hub(@PKG@.InvData.TAB_HUB[1], @PKG@.InvData.TAB_TAB[1], @PKG@.InvData.TAB_NAME[1]); return; }
    if (!still()) finish("skills");
    return;
  }
  if (i == 2) { say("You are on Pets"); return; }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }
  hub(@PKG@.InvData.TAB_HUB[i], @PKG@.InvData.TAB_TAB[i], @PKG@.InvData.TAB_NAME[i]);
}""")
# one action through pets:fn:tabact with the profile token of the last read; "^" = a Pets page opened over this one (the hatch reel)
M(ptab, r"""
public void act(String op, String arg) {
  this.answered = true;
  Object o = call("pets:fn:tabact", new Object[] { this.playerRef.getUuid(), this.ptok, op, arg == null ? "" : arg });
  if (o == null) { say(@PKG@.InvCraft.fn("pets:fn:tabact") == null ? "Pets is not on this server right now - nothing changed" : "That could not run here - nothing changed"); return; }
  String m = String.valueOf(o);
  if (m.startsWith("^")) {
    if (!still()) { finish("pets page"); return; }
    say(m.substring(1));
    return;
  }
  this.tcap = @PKG@.InvPage.bare(m);
  redraw();
}""")
M(ptab, r"""
public void hatchRow(int i) {
  if (i < 0 || i >= this.hRows.length || this.hRows[i] == null) { say("Nothing there"); return; }
  String[] f = this.hRows[i].split("\\|", -1);
  String st = f[0];
  if ("none".equals(st)) {
    if (this.esel.length() == 0) { say("Select an egg in Your eggs first"); return; }
    act("place", this.esel);
    return;
  }
  if ("wait".equals(st)) { act("take", f[1] + "|" + f[2]); return; }
  if ("ready".equals(st)) { act("hatch", f[1] + "|" + f[2]); return; }
  say("Nothing to do in that slot");
}""")
M(ptab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {
  String a = @PKG@.InvPage.val(d, "a");
  if (a == null) a = "";
  this.answered = false;
  try {
    if (this.closed) { this.answered = true; return; }
    this.pref = ref;
    this.pst = st;
    if (a.equals("close")) { this.answered = true; shut(); return; }
    if (a.startsWith("tab:")) { tabGo(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("full")) { hub("character", "pets", "the Pets page"); return; }
    if (a.startsWith("pg:")) {
      int dp = @PKG@.InvPage.toInt(a.substring(3), 0);
      int np = this.page + (dp < 0 ? -1 : 1);
      if (np < 0 || np >= this.pages) { say(np < 0 ? "This is the first page" : "This is the last page"); return; }
      this.page = np;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("ro:")) { int r = @PKG@.InvPage.toInt(a.substring(3), 0); this.role = r < 0 || r > 3 ? 0 : r; this.page = 0; this.tcap = ""; redraw(); return; }
    if (a.startsWith("ar:")) { int r = @PKG@.InvPage.toInt(a.substring(3), 0); this.area = r < 0 || r > 7 ? 0 : r; this.page = 0; this.tcap = ""; redraw(); return; }
    String t = @PKG@.InvPage.val(d, "t");
    if (t == null || !t.equals(this.tok) || !this.ok) {
      STALE = STALE + 1;
      this.tcap = this.ok ? "The page changed - here it is again. Nothing changed." : "Your pets are not ready yet - nothing changed";
      redraw();
      return;
    }
    if (a.equals("g")) {
      int si = @PKG@.InvPage.ival(d, "SlotIndex", -1);
      if (si < 0 || si >= this.pageIds.length) { say("Nothing there"); return; }
      this.sel = this.pageIds[si];
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("e")) {
      int si = @PKG@.InvPage.ival(d, "SlotIndex", -1);
      if (si < 0 || si >= this.eggIds.length) { say("Nothing there"); return; }
      this.esel = this.eggIds[si];
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("s1") || a.equals("s2")) {
      int n = a.equals("s1") ? 1 : 2;
      if (this.sel.length() == 0) { say("Pick a pet on the left first"); return; }
      if (this.selSlot == n) act("out", String.valueOf(n)); else act("slot", this.sel + "|" + n);
      return;
    }
    if (a.equals("out:1") || a.equals("out:2")) { act("out", a.substring(4)); return; }
    if (a.equals("ride")) { act("ride", ""); return; }
    if (a.equals("reb") || a.equals("fuse")) {
      if (this.sel.length() == 0) { say("Pick a pet on the left first"); return; }
      act(a, this.sel);
      return;
    }
    if (a.startsWith("hr:")) { hatchRow(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.equals("place")) {
      if (this.esel.length() == 0) { say("Select an egg in Your eggs first"); return; }
      act("place", this.esel);
      return;
    }
    if (a.startsWith("cr:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || k >= this.crIds.length || this.crIds[k] == null || this.crIds[k].length() == 0) { say("Nothing to craft there"); return; }
      act("craft", this.crIds[k]);
      return;
    }
    if (a.equals("up")) {
      if (this.upId.length() == 0) { say(this.esel.length() == 0 ? "Select an egg in Your eggs first" : "That egg has no upgrade yet"); return; }
      act("craft", this.upId);
      return;
    }
    say("Pick a pet or an egg");
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("pets screen event '" + a + "' failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.MenuUtil.warn("pets screen: the empty answer failed: " + t2); }
    }
  }
}""")
M(ptab, r"""
public void onDismiss(@REF@ ref, @ST@ st) { finish("dismissed"); }""")
'''
P.rep('''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''', PT_JAVA + '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''')
# Tab while the pets screen is open = it closes
P.rep('''  if (sp0 instanceof @PKG@.SkillPage && !((@PKG@.SkillPage) sp0).closed) { ((@PKG@.SkillPage) sp0).shut(); return; }   // 0.3.57
''', '''  if (sp0 instanceof @PKG@.SkillPage && !((@PKG@.SkillPage) sp0).closed) { ((@PKG@.SkillPage) sp0).shut(); return; }   // 0.3.57
  if (sp0 instanceof @PKG@.PetsTab && !((@PKG@.PetsTab) sp0).closed) { ((@PKG@.PetsTab) sp0).shut(); return; }   // 0.3.58
''')
# ---------- the inventory: the Pets tab + the pet / mount cards open the pets screen
P.rep('''M(ipg, r"""
public void goTab(int i) {
  this.answered = true;
  if (i <= 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("You are on the Inventory tab"); return; }
  if (i == 1 && openSkills(@PKG@.SkillPage.lastOf(this.playerRef.getUuid()))) return;   // 0.3.57: the skill page (else the old list below)
''', '''# 0.3.58: the Pets tab = the pets screen (false = it could not open / no pets:fn:tab: today's Pets page below)
M(ipg, r"""
public boolean openPets() {
  @PKG@.PetsTab pt = null;
  try { pt = @PKG@.PetsTab.open(this.pref, this.pst, this.playerRef, "inventory"); } catch (Throwable t) { pt = null; @PKG@.MenuUtil.warn("inventory: the pets screen failed: " + t); }
  if (pt == null) return false;
  this.answered = true;
  if (!still()) finish("pets");
  return true;
}""")
M(ipg, r"""
public void goTab(int i) {
  this.answered = true;
  if (i <= 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("You are on the Inventory tab"); return; }
  if (i == 1 && openSkills(@PKG@.SkillPage.lastOf(this.playerRef.getUuid()))) return;   // 0.3.57: the skill page (else the old list below)
  if (i == 2 && openPets()) return;   // 0.3.58: the pets screen (else today's Pets page below)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.58: no new system / command"
_i = P.s.index
assert _i("public static @PKG@.PetsTab open(") < _i("public boolean petsTab()") < _i("public void tabGo(int i) {\n  if (i == 0) { toInv(")
assert _i("public static @PKG@.SkillPage open(") < _i("public void tabGo(int i) {\n  this.answered = true;\n  if (i == 0) {\n    @PKG@.InvPage pg")
assert _i("public void shut() { finish(\"closed\"); this.close(); }\"\"\")\nM(ptab") < _i("if (sp0 instanceof @PKG@.PetsTab")
assert _i("public boolean openPets()") < _i("public void goTab(int i)") and _i('F(ptd, "public static final String LK') < _i("public static @PKG@.PetsTab open(")
assert _i("public PetsTab(@PR@ pr, String via)") < _i("public static @PKG@.PetsTab open(")
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.57 harness: every 0.3.57 check
# runs again on the 0.3.58 jar; + the TAB2 section)
T.rep('''"""Harness for SkyyMenu 0.3.57 (the Skills tab = one page per skill; the Mods list without the coin death penalty; tools/menu_0_3_57_patch.py).
''', '''"""Harness for SkyyMenu 0.3.58 (the Pets tab = one screen; tools/menu_0_3_58_patch.py).
GENERATED by tools/menu_0_3_58_patch.py from the 0.3.57 harness (edit the patch, not this file): every 0.3.57 check runs again on the
0.3.58 jar, plus
  TAB2 (EXECUTED on Python stand-ins of SkyyPets 0.4.28 pets:fn:tab / pets:fn:tabact - a little pet world with a profile token, item counts,
       a two-press fuse, a Hatchery and egg crafts; the real SkyyPets side runs in SkyyPets/test_skyypets_0.4.28.py):
       FALL    without the two keys the Pets tab (inventory + skill page + the pet card) opens today's route, never the screen
       OPEN    the inventory's Pets tab / the pet card / the skill page's Pets tab = the PETS SCREEN (ONE page packet, the old page forgotten)
       PAGE    every part drawn: slot cards (rarity variant, Summon only for a rideable mount), the chips, the 42-cell grid with the tooltips
               (newlines decoded, no metadata, known ids only), the selected pet (rarity variant, buffs, where, progress, at max, buttons),
               fusing, 6 Hatchery rows (wait / ready / empty / locked, bars), eggs grid, 5 Common crafts, the upgrade box; no scrolling
       ACT     select a pet / an egg, Pet slot / Mount slot / Take out (the selected pet's slot decides), Summon, Rebirth, Fuse (twice),
               Hatch (the reveal / a page that replaces ours = no packet of ours), Take out, Place, Craft, Upgrade - each ONE page packet, the
               bridge called with the READ's profile token and the right op / arg
       SAFE    a click from an older drawing (stale page token, a double click) = no bridge call, ONE packet; a profile switch between read
               and click = SkyyPets' refusal shown, nothing moved; a full inventory = SkyyPets' "no room" shown; the read failing = the page
               still draws (Full page works), actions refused without a call; filters + pages; empty grid cells = a caption
       TABS    Inventory / Skills / Market / Settings / Full page from the screen; the Tab key and X close it
The 0.3.57 harness text follows:
Harness for SkyyMenu 0.3.57 (the Skills tab = one page per skill; the Mods list without the coin death penalty; tools/menu_0_3_57_patch.py).
''')
T.rep('VERSION = "0.3.57"\nJAR', 'VERSION = "0.3.58"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.56.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.57.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.56.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.57.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_57_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_58_patch.py")')
T.rep('"scratch", "tab1", "menu"', '"scratch", "tab2", "menu"')
T.rep('ADDED = ["SkillData", "SkillPage"]   # 0.3.57: the skill page\n', 'ADDED = ["PetsTabData", "PetsTab"]   # 0.3.58: the pets screen\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.57:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.58: the Pets tab opens the pets screen (inventory + skill page); Tab closes it
    "InvPage": ["+m openPets", "~m goTab"],
    "InvState": ["~m tab"],
    "SkillPage": ["+m petsTab", "~m tabGo"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.57"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.58"') == 1, "S VERSION")
    # 0.3.58: the pets screen fits one 1080p screen, never scrolls, element budget
    K.check("0.3.58: the pets screen fits one 1080p screen" in g and "0.3.58: the pets screen never scrolls" in g,
            "TAB2 STATIC the build asserts the pets screen fits 1080 (every column sums to the body) and has no scrolling list")
    mp_ = re.search(r"PT_ELEMENTS <= (\\d+)", g)
    K.check(mp_ is not None and int(mp_.group(1)) <= 800, "TAB2 STATIC the pets screen's element budget assert is <= 800 (the ~1,600 client budget)")''')
# the 0.3.57 STATIC checks compared 0.3.57 with 0.3.56 (the Mods list text) - still true of 0.3.58's script
assert 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.56.jar")' not in T.s, "0.3.58 harness: an old line is still there"

HARNESS_TAB2 = r"""    # ---- TAB2 (0.3.58; Skyy 11-14 "1 tab with your pets your eggs the hatchery,, ecc crafting, pet fusing. i want it all on 1 screen."): THE PETS SCREEN
    PTB, PTD = JV("PetsTab"), JV("PetsTabData")
    uk2 = str(PK.pr.getUuid())
    for k_ in ("pets:fn:tab", "pets:fn:tabact", "requip:fn:presets", "requip:fn:preset", "skill:fn:prog"):
        BR.remove(k_)
    NL = chr(31)
    PW = {"tok": "prof-A", "slot1": "w1", "slot2": "d1", "reads": [], "acts": [], "conf": None, "inv": {"Egg_C": 2, "Egg_U": 0}, "full": False, "opener": None}
    PETS = [("w1", 5, "Wolf", 37, "Skyy_PetIcon_Wolf_Legendary", "Fighter"), ("d1", 4, "Plain Dragon", 24, "Skyy_PetIcon_Dragon_Epic", "Mount")] + \
           [("r%d" % i_, 3, "Rabbit", i_ + 1, "Rock_Stone", "Bonus") for i_ in range(50)]

    def slotOf(pid):
        return 1 if PW["slot1"] == pid else (2 if PW["slot2"] == pid else 0)

    def f_tab(o):
        a = list(o)
        PW["reads"].append([str(x) if x is not None else None for x in a])
        if PW.get("readNull"):
            return None
        sel, role, area, page, per, esel = str(a[1]), int(a[2]), int(a[3]), int(a[4]), int(a[5]), str(a[6])
        shown = [p for p in PETS if role == 0 or (role == 1 and p[5] == "Bonus") or (role == 2 and p[5] == "Fighter") or (role == 3 and p[5] == "Mount")]
        if area == 2:
            shown = [p for p in shown if p[2] == "Rabbit"]
        pages = max(1, (len(shown) + per - 1) // per)
        page = max(0, min(page, pages - 1))
        L = ["ok|%s|%d|120|1||%d|%d|%d|6|6|3|10|0|0" % (PW["tok"], len(PETS), len(shown), page, pages)]
        for i_, lb in enumerate(["All", "Combat", "Farming", "Mining", "Foraging", "Fishing", "Exploration", "Cooking"]):
            L.append("a|%d|%s" % (i_, lb))
        for s_ in (1, 2):
            pid = PW["slot%d" % s_]
            p = [x for x in PETS if x[0] == pid]
            if p:
                p = p[0]
                L.append("s|%d|%s|%s|%d|%d|50|%s|%d|%d|SLOT TIP%sline 2" % (s_, p[0], p[2], p[1], p[3], p[4], 1 if p[5] == "Mount" else 0, 1 if p[5] == "Fighter" else 0, NL))
            else:
                L.append("s|%d|||0|0|0||0|0|" % s_)
        for p in shown[page * per:(page + 1) * per]:
            L.append("p|%s|%d|%s|%d|%s|%d|TYPE%s%s tooltip | with a bar%sClick: select it" % (p[0], p[1], p[2], p[3], p[4], slotOf(p[0]), NL, p[2], NL))
        sid = sel if sel and [x for x in PETS if x[0] == sel] else (PW["slot1"] or shown[0][0])
        p = [x for x in PETS if x[0] == sid][0]
        L.append("d|%s|%s|%d|%d|50|41200|66000|%s|FIGHTER   COMBAT PET|%d|%d|0|3|SEL TIP" % (p[0], p[2], p[1], p[3], p[4], slotOf(p[0]), 1 if p[3] >= 50 else 0))
        L += ["b|+24 Damage", "b|+6% Crit Chance", "w|1|Pet slot: follows you and FIGHTS, full buffs", "w|0|Mount slot: not a mount (no riding)", "w|1|Now in your pet slot",
              "g|Rebirths 0 / 3 - next at Lv 50", "g|Next rarity: 3 / 4 Rare Wolf pets", "t|AT LV 50|+32 Damage    +8% Crit Chance"]
        L += ["f|3|4|Mythic Wolf|0|You need 4 Legendary Wolf pets to fuse (you have 3).|Legendary Wolf", "fo|%s|%s|%d" % (p[0], p[4], p[3]), "fo|r1|Rock_Stone|6", "fr|Skyy_PetIcon_Wolf_Mythic|6"]
        if PW["inv"]["Egg_C"] > 0:
            L.append("e|Egg_C|Common Mining Egg|1|%d|EGG TIP%sHATCHES" % (PW["inv"]["Egg_C"], NL))
        if PW["inv"]["Egg_U"] > 0:
            L.append("e|Egg_U|Uncommon Mining Egg|2|%d|EGG TIP U" % PW["inv"]["Egg_U"])
        for i_, nm in enumerate(["Mining", "Farming", "Combat", "Foraging", "Fishing"]):
            L.append("c|%d|Egg_C%s|Common %s Egg|1|%d|0|Egg 1/1 + Copper Ore %s/64|" % (i_, "" if i_ == 0 else str(i_), nm, 1 if i_ == 0 else 0, "64" if i_ == 0 else "42"))
        L.append("c|5|Egg_U|Uncommon Mining Egg|2|1|1|1 Common Mining Egg + 2 Enchanted Iron|Egg_C")
        L += ["h|1|ready|Egg_R|Rare Combat Egg|3|0|3600000|hidA|READY", "h|2|wait|Egg_U|Uncommon Farming Egg|2|4320000|7200000|hidB|Hatching", "h|3|empty|||0|0|0||Empty"]
        return "\n".join(L)

    def f_act(o):
        a = [str(x) for x in list(o)]
        PW["acts"].append(a)
        u_, tok, op, arg = a[0], a[1], a[2], a[3]
        if tok != PW["tok"]:
            PW["conf"] = None
            return "=Your profile changed - here are its pets. Nothing changed."
        if op == "slot":
            pid, n = arg.split("|")
            PW["slot" + n] = pid
            return "+%s is now in your slot %s." % (pid, n)
        if op == "out":
            PW["slot" + arg] = ""
            return "+left your slot %s." % arg
        if op == "ride":
            return "+Summoning your Plain Dragon - hop on!"
        if op in ("fuse", "reb", "take"):
            if PW["conf"] == op + arg:
                PW["conf"] = None
                return "+%s done" % op
            PW["conf"] = op + arg
            return "=Press %s again." % op
        PW["conf"] = None
        if op == "craft":
            if PW["full"]:
                return "-No room in your inventory - everything is back where it was."
            if arg == "Egg_U":
                if PW["inv"]["Egg_C"] < 1:
                    return "-You need 1 more Common Mining Egg."
                PW["inv"]["Egg_C"] -= 1
                PW["inv"]["Egg_U"] += 1
                return "+Upgraded: 1 Common Mining Egg -> 1 Uncommon Mining Egg."
            PW["inv"]["Egg_C"] += 1
            return "+Crafted a Common Mining Egg."
        if op == "place":
            return "+The %s is in Hatchery slot 3." % arg
        if op == "hatch":
            if PW["opener"]:
                PW["opener"]()
                return "^Hatched"
            return "+You hatched a Rare Wolf!"
        return "-Unknown pet action."

    def pt_ev(obj, what, n=1):
        f_ = len(E.sent(PK))
        PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, json.dumps(obj))
        ps_ = pages(PK, f_)
        K.eq(len(ps_), n, what + ": exactly %d page packet" % n)
        return ps_[0] if ps_ else None
    vis2 = lambda c_, k_: sval(c_, "#SkyyPtab%s.Visible" % k_) in (True, "true")
    # FALL: no keys = today's route (never the screen)
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:2"}')
    cur_ = PK.pm.getCustomPage()
    K.check(len(pages(PK, f0_)) == 1 and (cur_ is None or str(cur_.getClass().getSimpleName()) != "PetsTab"), "TAB2 FALL no pets:fn:tab: the Pets tab keeps today's route (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    K.check(PTB.open(PK.ref, PK.st, PK.pr, "test") is None, "TAB2 FALL PetsTab.open = null without the keys")
    if cur_ is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    BR.put("pets:fn:tab", Fn(f_tab))
    K.check(PTB.open(PK.ref, PK.st, PK.pr, "test") is None, "TAB2 FALL only one of the two keys = null (both are needed)")
    BR.put("pets:fn:tabact", Fn(f_act))
    # OPEN from the inventory
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:2"}')
    pk_ = pages(PK, f0_)
    PS = PK.pm.getCustomPage()
    K.check(len(pk_) == 1 and PS is not None and str(PS.getClass().getSimpleName()) == "PetsTab" and bool(pgI_.closed) and ST.PAGES.get(PK.pr.getUuid()) is None,
            "TAB2 OPEN the inventory's Pets tab = the PETS SCREEN (ONE page packet), the inventory page forgotten")
    cm = cmap(pk_[0]) if pk_ else {}
    K.notes.append("TAB2 the screen's first packet: %d commands" % len(cmds_of(pk_[0])) if pk_ else "TAB2 no packet")
    K.check(PW["reads"] and PW["reads"][-1][0] == uk2 and PW["reads"][-1][2:6] == ["0", "0", "0", str(int(PTD.PER))], "TAB2 OPEN the read: your UUID, role 0, area 0, page 0, 42 a page (%s)" % (PW["reads"][-1:],))
    K.check(len(PW["reads"][-1]) == 8 and PW["reads"][-1][7] == "1" and not bool(PS.fresh),
            "TAB2 FIX the screen's FIRST read sends 1 (SkyyPets then clears an old two-press ask - critic tab2-crit-safety 1)")
    # FIX (critic 3 / 1): the cost labels are green (enough) / red (short) and their widths are the ones SkyyPets 0.4.28 measures its lines against
    def col_of(id_):
        t_ = mk_of(pk_[0], id_)
        i_ = t_.find("#" + id_ + " ")
        return t_[i_:t_.find("}", i_)] if i_ >= 0 else ""
    K.check("TextColor: #4fd88a" in col_of("SkyyPtabC0C0") and "TextColor: #ff6b6b" in col_of("SkyyPtabC0C1") and "TextColor: #4fd88a" in col_of("SkyyPtabUc0")
            and int(PTD.CRW) >= 320 and int(PTD.UPW) >= 372, "TAB2 FIX the craft + upgrade cost lines: green when enough, red when short, wide enough for SkyyPets' measured lines")
    # PAGE: every part
    K.check(vis2(cm, "Q1N5") and not vis2(cm, "Q1N0") and sval(cm, "#SkyyPtabQ1N5.Text") == "Wolf" and sval(cm, "#SkyyPtabQ1L.Text") == "Lv 37 / 50"
            and sval(cm, "#SkyyPtabQ1S.Text") == "Fights + full buffs" and vis2(cm, "Q1Out"), "TAB2 PAGE the pet slot card: Legendary colour, level, what it does, Take out")
    K.check(vis2(cm, "Q2N4") and sval(cm, "#SkyyPtabQ2S.Text") == "Summon = ride" and vis2(cm, "Q2Go") and vis2(cm, "Q2Out"), "TAB2 PAGE the mount slot card: Epic colour, Summon (a rideable mount)")
    g_ = cm.get("#SkyyPtabG.Slots", "")
    K.notes.append("TAB2 the grid's first cells: %s" % g_[:700])
    K.check(g_.count("Lv ") >= 42, "TAB2 PAGE the grid: 42 cells drawn (page 1 of 2): %s" % g_[:200])
    K.check("TYPE\\nWolf tooltip | with a bar\\nClick: select it" in g_ and "Rock_Stone" in g_ and "Skyy_PetIcon_Dragon_Epic" not in g_ and "Plain Dragon - Lv 24" in g_ and nometa(pk_[0]),
            "TAB2 PAGE the approved tooltip passes through (newlines decoded, a '|' inside kept), icons only for known ids (an unknown portrait = name + tooltip only), no metadata")
    K.check(sval(cm, "#SkyyPtabPn.Text") == "52 / 120" and sval(cm, "#SkyyPtabPg.Text") == "Page 1 / 2", "TAB2 PAGE the count and the page (52 pets, 2 pages)")
    K.check(str(PTD.ST_CHSEL) in mk_of(pk_[0], "SkyyPtabRo0") and str(PTD.ST_CH) in mk_of(pk_[0], "SkyyPtabRo1") and sval(cm, "#SkyyPtabAo6.Text") == "Explore"
            and sval(cm, "#SkyyPtabRo3.Text") == "Mount", "TAB2 PAGE the chips: All chosen, Mount, the area labels from SkyyPets (Exploration = Explore)")
    K.check(vis2(cm, "SN5") and sval(cm, "#SkyyPtabSN5.Text") == "Wolf" and sval(cm, "#SkyyPtabSL.Text") == "Lv 37 / 50" and sval(cm, "#SkyyPtabSX.Text") == "41,200 / 66,000 pet XP"
            and ("Width: %d," % (41200 * int(PTD.SXW) // 66000)) in cm.get("#SkyyPtabSB", "") and sval(cm, "#SkyyPtabSb1.Text") == "+6% Crit Chance"
            and vis2(cm, "Sw00") and vis2(cm, "Sw11") and sval(cm, "#SkyyPtabSg1.Text") == "Next rarity: 3 / 4 Rare Wolf pets" and sval(cm, "#SkyyPtabSa.Text") == "AT LV 50"
            and sval(cm, "#SkyyPtabS1.Text") == "Take out" and sval(cm, "#SkyyPtabS2.Text") == "Mount slot" and sval(cm, "#SkyyPtabS3.Text") == "Rebirth (Lv 50)",
            "TAB2 PAGE the selected pet (default = the pet slot one): name colour, XP bar, buffs, where (green / red), progress, at Lv 50, the buttons")
    K.check(sval(cm, "#SkyyPtabF1.Text") == "3 / 4 Legendary Wolf" and vis2(cm, "F31") and "Mythic Wolf" in str(sval(cm, "#SkyyPtabFn.Text")) and "Rock_Stone" in cm.get("#SkyyPtabFG.Slots", ""),
            "TAB2 PAGE fusing: have / need, why not (red), the result, the group icons")
    K.check(vis2(cm, "H0S1") and sval(cm, "#SkyyPtabH0S1.Text") == "Ready!" and sval(cm, "#SkyyPtabH0Go.Text") == "Hatch" and sval(cm, "#SkyyPtabH1S0.Text") == "1h 12m left"
            and sval(cm, "#SkyyPtabH1Go.Text") == "Take out" and ("Width: %d," % (2880000 * int(PTD.HBW) // 7200000)) in cm.get("#SkyyPtabH1B", "")
            and sval(cm, "#SkyyPtabH2Go.Text") == "Place" and sval(cm, "#SkyyPtabH3S0.Text") == "Empty - select an egg, then Place" and vis2(cm, "H3Go")
            and sval(cm, "#SkyyPtabHc.Text") == "3 / 6 slots   -10% time", "TAB2 PAGE the Hatchery rows: Ready! + Hatch, time left + bar + Take out, empty + Place")
    K.check("EGG TIP\\nHATCHES" in cm.get("#SkyyPtabE.Slots", "") and str(sval(cm, "#SkyyPtabEh.Text")).startswith("YOUR EGGS  1 kinds")
            and sval(cm, "#SkyyPtabC0N.Text") == "Mining" and sval(cm, "#SkyyPtabC1N.Text") == "Farming" and vis2(cm, "C0C0") and vis2(cm, "C1C1") and sval(cm, "#SkyyPtabC1C1.Text") == "Egg 1/1 + Copper Ore 42/64"
            and sval(cm, "#SkyyPtabC0C0.Text") == "Egg 1/1 + Copper Ore 64/64"
            and sval(cm, "#SkyyPtabU1.Text") == "Common Mining Egg  ->  Uncommon Mining Egg" and vis2(cm, "Uc0"), "TAB2 PAGE eggs: the grid + tooltip, 5 Common crafts (red when short), the upgrade of the selected Common egg")
    K.check(not any("Scrolling" in str(c_.text or "") for c_ in cmds_of(pk_[0])), "TAB2 FIT the screen's packet carries no scrolling list")
    # ACT
    p_ = pt_ev({"a": "g", "SlotIndex": 3, "t": str(PS.tok)}, "TAB2 ACT select a pet")
    K.check(str(PS.sel) == str(PS.pageIds[3]) and PW["reads"][-1][1] == str(PS.sel) and not PW["acts"], "TAB2 ACT a grid click selects (the read asks for it), no action call")
    n0 = len(PW["acts"])
    p_ = pt_ev({"a": "s1", "t": str(PS.tok)}, "TAB2 ACT Pet slot")
    K.check(PW["acts"][-1] == [uk2, "prof-A", "slot", str(PS.sel) + "|1"] and "is now in your slot 1" in str(sval(cmap(p_), "#SkyyPtabCap.Text")),
            "TAB2 ACT Pet slot = tabact slot <id>|1 with the read's profile token, the answer as the caption (%s)" % PW["acts"][-1:])
    p_ = pt_ev({"a": "s1", "t": str(PS.tok)}, "TAB2 ACT the selected pet is in the pet slot = Take out")
    K.check(PW["acts"][-1][2:] == ["out", "1"], "TAB2 ACT Pet slot on a pet already there = out 1 (never a second slot op)")
    p_ = pt_ev({"a": "ride", "t": str(PS.tok)}, "TAB2 ACT Summon")
    K.check(PW["acts"][-1][2] == "ride" and "hop on" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 ACT Summon = tabact ride")
    p_ = pt_ev({"a": "fuse", "t": str(PS.tok)}, "TAB2 ACT Fuse (first press)")
    p_ = pt_ev({"a": "fuse", "t": str(PS.tok)}, "TAB2 ACT Fuse (second press)")
    K.check([x[2] for x in PW["acts"][-2:]] == ["fuse", "fuse"] and "fuse done" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 ACT Fuse twice = SkyyPets' two-press rule decides")
    K.check(all(len(x) == 8 and x[7] == "0" for x in PW["reads"][1:]) and len(PW["reads"]) >= 4, "TAB2 FIX every later read (redraws after clicks) sends 0 - a pending ask survives its own redraw")
    # SAFE: a stale page token / a double click
    old = str(PS.tok)
    n0 = len(PW["acts"])
    p_ = pt_ev({"a": "reb", "t": old}, "TAB2 ACT Rebirth")
    p2 = pt_ev({"a": "reb", "t": old}, "TAB2 SAFE the double click's second event (older drawing)")
    K.check(len(PW["acts"]) == n0 + 1 and "The page changed" in str(sval(cmap(p2), "#SkyyPtabCap.Text")) and int(PTB.STALE) >= 1,
            "TAB2 SAFE a double click = ONE bridge call; the second (stale page token) = a caption, no call")
    p_ = pt_ev({"a": "craft", "t": "nope"}, "TAB2 SAFE a forged token")
    K.check(len(PW["acts"]) == n0 + 1, "TAB2 SAFE a wrong page token never reaches SkyyPets")
    # Hatchery + eggs
    p_ = pt_ev({"a": "hr:1", "t": str(PS.tok)}, "TAB2 ACT Take out a hatching egg")
    K.check(PW["acts"][-1][2:] == ["take", "2|hidB"], "TAB2 ACT Take out = tabact take <slot>|<hid> (SkyyPets asks twice)")
    p_ = pt_ev({"a": "hr:2", "t": str(PS.tok)}, "TAB2 ACT Place from an empty row")
    K.check(PW["acts"][-1][2:] == ["place", "Egg_C"], "TAB2 ACT an empty row's Place = the selected egg (default: the Common egg with an upgrade)")
    p_ = pt_ev({"a": "hr:0", "t": str(PS.tok)}, "TAB2 ACT Hatch (reveal)")
    K.check(PW["acts"][-1][2:] == ["hatch", "1|hidA"] and "hatched a Rare Wolf" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 ACT Hatch = tabact hatch <slot>|<hid>, the reveal as caption")
    PW["opener"] = lambda: JV("SkillPage").open(PK.ref, PK.st, PK.pr, "Mining", "pets reel stand-in")
    p_ = pt_ev({"a": "hr:0", "t": str(PS.tok)}, "TAB2 ACT Hatch (a page replaces ours)")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and bool(PS.closed), "TAB2 ACT Hatch '^' with our page replaced = that page's ONE packet, ours forgotten")
    PW["opener"] = None
    PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    PS = PTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    p_ = pt_ev({"a": "cr:0", "t": str(PS.tok)}, "TAB2 ACT Craft a Common egg")
    K.check(PW["acts"][-1][2:] == ["craft", "Egg_C"] and PW["inv"]["Egg_C"] == 3, "TAB2 ACT Craft = tabact craft <egg id> of that row")
    p_ = pt_ev({"a": "up", "t": str(PS.tok)}, "TAB2 ACT Upgrade the selected egg")
    K.check(PW["acts"][-1][2:] == ["craft", "Egg_U"] and PW["inv"]["Egg_U"] == 1 and PW["inv"]["Egg_C"] == 2 and "Upgraded" in str(sval(cmap(p_), "#SkyyPtabCap.Text")),
            "TAB2 ACT Upgrade = tabact craft <the Uncommon id> (SkyyPets takes the Common egg)")
    p_ = pt_ev({"a": "e", "SlotIndex": 1, "t": str(PS.tok)}, "TAB2 ACT select the Uncommon egg")
    K.check(str(PS.esel) == "Egg_U" and "no upgrade" in str(sval(cmap(p_), "#SkyyPtabU1.Text")), "TAB2 ACT an egg click selects it; an Uncommon egg has no upgrade yet (said)")
    n0 = len(PW["acts"])
    p_ = pt_ev({"a": "up", "t": str(PS.tok)}, "TAB2 ACT Upgrade with no upgrade")
    K.check(len(PW["acts"]) == n0 and "no upgrade" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 ACT Upgrade with nothing to upgrade = a caption, no call")
    PW["full"] = True
    p_ = pt_ev({"a": "cr:0", "t": str(PS.tok)}, "TAB2 SAFE a full inventory")
    K.check("No room" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 SAFE a full inventory = SkyyPets' answer shown (everything back - its harness proves the items)")
    PW["full"] = False
    # a profile switch between the read and the click
    PW["tok"] = "prof-B"
    n0 = len(PW["acts"])
    p_ = pt_ev({"a": "cr:0", "t": str(PS.tok)}, "TAB2 SAFE a profile switch before the click")
    K.check(PW["acts"][-1][1] == "prof-A" and "profile changed" in str(sval(cmap(p_), "#SkyyPtabCap.Text")) and PW["inv"]["Egg_C"] == 2,
            "TAB2 SAFE the click carries the OLD profile token = SkyyPets refuses, nothing moved")
    p_ = pt_ev({"a": "cr:0", "t": str(PS.tok)}, "TAB2 SAFE the redrawn page uses the new token")
    K.check(PW["acts"][-1][1] == "prof-B" and PW["inv"]["Egg_C"] == 3, "TAB2 SAFE after the redraw the new profile's token is used")
    # filters + pages + empty cells
    p_ = pt_ev({"a": "pg:1"}, "TAB2 next page")
    K.check(sval(cmap(p_), "#SkyyPtabPg.Text") == "Page 2 / 2" and PW["reads"][-1][4] == "1", "TAB2 PAGE > = page 2 (the read asks for page 1)")
    p_ = pt_ev({"a": "pg:1"}, "TAB2 past the last page")
    K.check("last page" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 PAGE past the last page = a caption")
    p_ = pt_ev({"a": "g", "SlotIndex": 40, "t": str(PS.tok)}, "TAB2 an empty grid cell")
    K.eq(sval(cmap(p_), "#SkyyPtabCap.Text"), "Nothing there", "TAB2 an empty grid cell = a caption")
    p_ = pt_ev({"a": "ro:3"}, "TAB2 the Mount chip")
    K.check(PW["reads"][-1][2] == "3" and PW["reads"][-1][4] == "0" and str(PTD.ST_CHSEL) in mk_of(p_, "SkyyPtabRo3") and sval(cmap(p_), "#SkyyPtabPn.Text") == "52 / 120   (1 shown)",
            "TAB2 PAGE a role chip filters (the read asks role 3, page 0), the chip shows chosen")
    p_ = pt_ev({"a": "ro:0"}, "TAB2 All again")
    # the read failing: the page still draws, actions are refused without a call
    PW["readNull"] = True
    p_ = pt_ev({"a": "ar:2"}, "TAB2 FALL the read fails")
    n0 = len(PW["acts"])
    K.check("could not be read" in str(sval(cmap(p_), "#SkyyPtabPe2.Text")), "TAB2 FALL the read = null: the page still draws and says so")
    p_ = pt_ev({"a": "cr:0", "t": str(PS.tok)}, "TAB2 FALL an action while the read fails")
    K.check(len(PW["acts"]) == n0 and "not ready" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "TAB2 FALL no action while the pets cannot be read (no call)")
    PW["readNull"] = False
    p_ = pt_ev({"a": "ar:0"}, "TAB2 the read works again")
    # TABS
    p_ = pt_ev({"a": "tab:3"}, "TAB2 TABS Market (no market mod)")
    K.check("Market is not on this server right now" in str(sval(cmap(p_), "#SkyyPtabCap.Text")) and PK.pm.getCustomPage() == PS, "TAB2 TABS Market = a caption, the screen stays")
    p_ = pt_ev({"a": "tab:2"}, "TAB2 TABS Pets")
    K.eq(sval(cmap(p_), "#SkyyPtabCap.Text"), "You are on Pets", "TAB2 TABS Pets = a caption")
    p_ = pt_ev({"a": "tab:1"}, "TAB2 TABS Skills")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and bool(PS.closed), "TAB2 TABS Skills = the skill page")
    p_ = pt_ev({"a": "tab:2"}, "TAB2 OPEN the skill page's Pets tab")
    PS = PK.pm.getCustomPage()
    K.check(PS is not None and str(PS.getClass().getSimpleName()) == "PetsTab", "TAB2 OPEN the skill page's Pets tab = the pets screen")
    p_ = pt_ev({"a": "tab:0"}, "TAB2 TABS Inventory")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "c", "TAB2 TABS Inventory = the inventory screen")
    p_ = one(ev(PK, {"a": "pet"}), "TAB2 OPEN the inventory's pet card")
    PS = PK.pm.getCustomPage()
    K.check(PS is not None and str(PS.getClass().getSimpleName()) == "PetsTab", "TAB2 OPEN the inventory's pet / mount card = the pets screen")
    p_ = pt_ev({"a": "tab:6"}, "TAB2 TABS Settings")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(PS.closed), "TAB2 TABS Settings = our Settings page")
    PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    PS = PTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    PS.handleDataEvent(PK.ref, PK.st, '{"a":"full"}')
    cur_ = PK.pm.getCustomPage()
    K.check(len(pages(PK, f0_)) == 1, "TAB2 TABS Full page = today's Pets page route, ONE packet (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    PS = PTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    ST.tab(PK.ref, PK.st, PK.pr, PK.pl, "test")
    K.check(PK.pm.getCustomPage() is None and bool(PS.closed), "TAB2 TABS the Tab key closes the pets screen")
    PS = PTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    PS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(PK.pm.getCustomPage() is None and bool(PS.closed), "TAB2 TABS X closes the screen")
    K.notes.append("TAB2 counters: opens %d, stale %d, reads %d, acts %d" % (int(PTB.OPENS), int(PTB.STALE), len(PW["reads"]), len(PW["acts"])))
    for k_ in ("pets:fn:tab", "pets:fn:tabact"):
        BR.remove(k_)
    E.pump(PK)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_TAB2 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
if T.dst:
    T.finish()
