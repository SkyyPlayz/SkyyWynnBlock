"""Derive SkyyMenu/build_skyymenu_0.3.62.py + SkyyMenu/test_skyymenu_0.3.62.py from the SET pin SkyyMenu 0.3.61 (generated - never re-run
its patch). Run:  python tools/menu_0_3_62_patch.py   then   python SkyyMenu/build_skyymenu_0.3.62.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.62.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.61 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.62 (2026-11-22, round tab4) = TAB SCREENS ROUND 4: THE WORLD TAB - ONE SCREEN (Travel + Quests + Your island + Explore + Bestiary / drops).
Skyy's words: 11-14 popup on research/ui-theme-art/tab-plan.png (12 tabs -> 7) "Yes, both"; 11-21 "build and deploy everything on your list",
"pc is back on if you wana keep building". Approved art: research/ui-theme-art/world-page.png (v2: a hub town per zone island) + README 'Tab pages'
(World = MAP + YOUR ISLAND + EXPLORE + QUESTS) and the nothing-lost table (World > Teleport / Island / Explore, Quests = quest log + tracked quest,
the bestiary / drops codex). README question 3 default: the hand-drawn world map = a LATER ART ROUND - this screen draws NO big picture (the map
area is the TRAVEL list; tools/ci/ui_budget.py unchanged: this jar ships no new picture).
SURVEY: vanilla has no world / travel screen; no pack mod draws one. The screen reads ONLY bridges that already exist (no other mod changes):
  SkyyIslands 0.5.26 island:<uuid> (the home island's world), island:role:fn, island:fn:homes, island:fn:gohome; SkyyEssentials 0.1.16
  essentials:fn:homes / essentials:fn:gohome / essentials:fn:warps (warp icons); SkyyExploration 0.3.4 explore:<uuid> (the summary),
  explore:fn:title, explore:fn:pct; SkyyQuests 0.4.4 quest:fn:hud; SkyyCollections 0.2.36 coll:fn:catTotal (Combat); the engine's warps.
  1. THE WORLD TAB of the inventory's top bar (and the skill page's / pets screen's / market screen's World tab) opens the new WORLD SCREEN
     (WorldTab: an inline Skyglass page, kit tools/skyyui.py, the inventory's frame + the same 7-tab top bar with World selected; coins in the bar):
     TOP    TRAVEL (the old World > Teleport page's places: Your island, Hub, your island homes, your homes, every warp - locked ones greyed;
            filter chips All / Islands / Homes / Warps; 10 a page in two columns, icon + name + where + Go; nothing scrolls) | QUESTS (the
            tracked quest: its title, progress, up to 5 steps with progress, where and a bar - done steps green; Quest log = the old Quests page)
     BOTTOM YOUR ISLAND (have one / role / island homes; Go home; Island settings = the old Island page for members, visitors, PvP, the name) |
            EXPLORE (Exploration level, zones found, chests, spots, secrets, your title, the discovery % of every loaded world with
            exploration spots - your world first, 4 rows; Explore page = the old page) | BESTIARY + DROPS (mob drops collected =
            the Combat collections total; Collections = the old Collections page)
     Every teleport goes through the SAME code path as the old Teleport page / the inventory's teleport row: Your island / Hub = the /island
     / /hub command as the player (InvPage.teleport); an island home = island:fn:gohome (the page closes first, as MenuPage.goHome); a home =
     essentials:fn:gohome ("ok" = the page closes, else the reason shown); a warp = the engine Teleport component with the teleport
     history line (InvPage.warpGo, the same calls: unlocked check, world loaded, already teleporting). No cost, cooldown or rule of ours - the
     owning command / bridge keeps its own.
     This page holds a page token: a Go / Go home from an older drawing = "The page changed" (no teleport); the profile key of the drawing is
     checked too (a profile switch = "Your profile changed", the list drawn again, nothing happens); a teleport closes the page, so a double
     click never teleports twice.
  2. FALLBACK: the screen always opens (SkyyMenu's own teleports); each card says so when its mod is not on the server ("... not on this server
     right now") and its button routes like today. 'Full page' (top bar) = today's World > Teleport page (Spawn + Arrange live there).
  NOT BUILT (next rounds, nothing half-wired): the hand-drawn world map with zone islands / pins (art round - question 3), Set as home, the
  island toggles (visitors / chests / PvP), Members, Rename ON this screen (Island settings opens the page that has them), dailies / weeklies /
  achievements rows and Claim (the Quest log page; needs a SkyyQuests read key), tracking another quest, mob icons + drop chances in the codex
  (needs a SkyyMobs / SkyyCollections read key), Spawn on this screen (Full page).
  New classes WorldTabData + WorldTab; no command, no setting, no lang key, no system, no saved data, no picture.
  ROLLBACK to 0.3.61: safe alone (nothing saved; the World tab opens the old World > Teleport page again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.61.py"), os.path.join(MOD, "build_skyymenu_0.3.62.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.61.py"), os.path.join(MOD, "test_skyymenu_0.3.62.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.61"\n') and P.has("tools/menu_0_3_61_patch.py") and P.has("tree:fn:map")
assert not P.has("WorldTab"), "not the generated SkyyMenu 0.3.61 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.61: THE SKILL TREE INLINE''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.62: THE WORLD TAB = ONE SCREEN (WorldTab: TRAVEL - your island, the hub, island homes, homes, every warp with filters + pages and Go; QUESTS -
       the tracked quest with its steps + Quest log; YOUR ISLAND - Go home + Island settings; EXPLORE - level, zones, title, discovery per
       world; BESTIARY + DROPS - the Combat collections total. Every teleport = the old Teleport page's own path; 'Full page' = the old World >
       Teleport page) (notes: tools/menu_0_3_62_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.62.py.
0.3.61: THE SKILL TREE INLINE''')
P.rep('VERSION = "0.3.61"\n', 'VERSION = "0.3.62"\n')

# ---------- (1) the WORLD SCREEN markup (one page data list drawn by WorldTab.build)
WT_PAGE = r'''
# ================= 0.3.62 THE WORLD TAB: ONE SCREEN (tools/menu_0_3_62_patch.py; approved art research/ui-theme-art/world-page.png; popup 11-14
# "Yes, both" on the 7 tabs) =================
# The inventory's frame and top bar (World selected); TOP: Travel (the map area - the map art is a later round) | Quests;
# BOTTOM: Your island | Explore | Bestiary + drops.
WT = "SkyyWtab"
WT_TOP_H = 470
WT_BOT_H = IV_BODY_H - WT_TOP_H - 8                         # 366
WT_L = 980
WT_Q = IV_IW - WT_L - IV_GAP                                # 566
WT_I, WT_E = 420, 620
WT_C = IV_IW - WT_I - WT_E - 2 * IV_GAP                     # 496
WT_LI, WT_QI, WT_II, WT_EI, WT_CI = WT_L - 20, WT_Q - 20, WT_I - 20, WT_E - 20, WT_C - 20
WT_TC, WT_TR = 2, 5                                         # the travel list: 2 columns x 5 rows a page (nothing scrolls)
WT_TN = WT_TC * WT_TR
WT_RW = (WT_LI - 10) // WT_TC                               # a travel card (475)
WT_RH = 52
WT_GOW = 72
WT_RXW = WT_RW - 12 - 44 - 8 - 6 - WT_GOW                   # a card's text column
WT_QN = 5                                                   # the tracked quest's steps shown
WT_EN = 4                                                   # the worlds in EXPLORE
WT_ENW, WT_EBW, WT_EPW = 250, WT_EI - 250 - 8 - 70, 70      # an explore row: the world, its bar, the pct
WT_BARQ = WT_QI                                             # a quest step's bar
WT_FILT = ["All", "Islands", "Homes", "Warps"]
WT_CHW = 96
WT_TXT = {
    "cap0": "Pick a place and press Go to travel there.",
    "tfoot": "Spawn and your teleport row: Full page.",
    "qnote": "Dailies, weeklies, story and side quests: Quest log.",
    "ihint": "Members, visitors, PvP and the name: Island settings.",
    "c2": "Every mob drop you pick up counts in your",
    "c3": "Combat collections - each tier pays a reward.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in WT_TXT.values() for c_ in v_), "0.3.62: plain texts"
assert SUI.text_width(WT_TXT["tfoot"], 12) <= WT_LI - 300 and SUI.text_width(WT_TXT["qnote"], 12) <= WT_QI - 160 - 10, "0.3.62: the foot lines fit"
assert SUI.text_width(WT_TXT["ihint"], 12) <= WT_II and max(SUI.text_width(WT_TXT[k_], 13) for k_ in ("c2", "c3")) <= WT_CI, "0.3.62: the card lines fit"
for _l in WT_FILT:
    assert SUI.text_width(_l, 12, bold=True) <= WT_CHW - 12, ("0.3.62: a filter chip fits", _l)
assert SUI.text_width("Zones found 27 / 27    Chests 9,999    Spots 999    Secrets 999", 13) <= WT_EI, "0.3.62: the explore line fits"
# the run-time markup: the filter chips, a bar fill
WT_ST_CH, WT_ST_CHSEL = SUI.glass_button_style("tab", 12), SUI.glass_button_style("tabSelected", 12)
WT_CHIP = "TextButton #SkyyWtab{I} { Anchor: (Width: {W}, Height: 26, Right: 4); {S} }"
WT_FILL = "Group { Anchor: (Width: {W}, Height: 8); Background: %s; }" % SUI.glass_col("xp")
for _mk in (WT_CHIP.replace("{I}", "Fc0").replace("{W}", "96").replace("{S}", WT_ST_CHSEL), WT_FILL.replace("{W}", "40")):
    SUI.check_markup(_mk, prefix=WT, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.62: a run-time markup line Java can hold"
WT_ICON = {"island": "Skyy_Menu_Icon_MyIsland", "hub": "Skyy_Menu_Icon_Hub", "ihome": ICON_IHOME, "home": ICON_ZHOME}
assert all(i_ in ICON_ITEMS for i_ in WT_ICON.values()), "0.3.62: the travel icons are items this jar ships"


def _wt_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label

    def holder(parent, ident, w, h, size, cols, anchor=None, bold=False):
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, c_, bold=bold, w=w, h=h)) for k_, c_ in enumerate(cols)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)

    def head(parent, ident, title, w, right_w):
        hd = WT + ident
        ap.append(("#" + parent, G_.glass_group(hd, w, 24, layout="Left")))
        ap.append(("#" + hd, lab(None, title, 15, "accentHi", bold=True, w=w - right_w, h=24)))
        return hd
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (WT, IV_PAGE_W, IV_PAGE_H)))
    win = WT + "Win"
    ap.append(("#" + WT, G_.glass_group(win, IV_W, IV_FRAME_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": IV_FRAME_TOP})))   # under the top bar (0.3.60)
    # ---- the top bar: the same 7 tabs (World selected), Full page, coins, the X
    top = WT + "Top"
    ap.append(iv_bar(G_, "#" + WT, top))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (WT, i), lb, "tabSelected" if i == 4 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(WT + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(WT + "Coins", "", 14, "xp", bold=True, w=cw_, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(WT + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    body = WT + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Top")))
    up_ = WT + "Up"
    ap.append(("#" + body, G_.glass_group(up_, IV_IW, WT_TOP_H, layout="Left")))
    # ======== TOP LEFT: TRAVEL (the old World > Teleport page's places)
    tv = WT + "Tv"
    ap.append(("#" + up_, G_.glass_group(tv, WT_L, WT_TOP_H, role="panel", layout="Top", pad=10)))
    th = head(tv, "Th", "TRAVEL", WT_LI, 4 * (WT_CHW + 4) + 150)
    ap.append(("#" + th, G_.glass_group(WT + "Fl", 4 * (WT_CHW + 4), 26, layout="Left")))
    ap.append(("#" + th, lab(WT + "Lt", "", 12, "dim", w=150, h=24, halign="End")))
    ls = WT + "Ls"
    ap.append(("#" + tv, G_.glass_group(ls, WT_LI, WT_TR * (WT_RH + 6), layout="Left", anchor={"top": 8})))
    for c_ in range(WT_TC):
        col_ = "%sCol%d" % (WT, c_)
        ap.append(("#" + ls, G_.glass_group(col_, WT_RW, WT_TR * (WT_RH + 6), layout="Top", anchor={"right": 10} if c_ == 0 else None)))
        for r_ in range(WT_TR):
            k_ = c_ * WT_TR + r_
            rw = "%sR%d" % (WT, k_)
            ap.append(("#" + col_, G_.glass_group(rw, WT_RW, WT_RH, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"bottom": 6})))
            ap.append(("#" + rw, G_.glass_grid(rw + "I", 1, 1, drag=False, slot=44, icon=34, anchor={"top": 4})))
            rx = rw + "X"
            ap.append(("#" + rw, G_.glass_group(rx, WT_RXW, WT_RH, layout="Top", anchor={"left": 8, "right": 6})))
            ap.append(("#" + rx, lab(rw + "N", "", 14, "row", bold=True, w=WT_RXW, h=24, anchor={"top": 4})))
            ap.append(("#" + rx, lab(rw + "S", "", 11, "dim", w=WT_RXW, h=18)))
            ap.append(("#" + rw, G_.glass_button(rw + "Go", "Go", "primary", w=WT_GOW, h=30, size=13, anchor={"top": 11})))
    assert 12 + 44 + 8 + WT_RXW + 6 + WT_GOW <= WT_RW and WT_TC * WT_RW + 10 <= WT_LI, "0.3.62: a travel card fits"
    pr_ = WT + "Pr"
    ap.append(("#" + tv, G_.glass_group(pr_, WT_LI, 28, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pr_, G_.glass_button(WT + "Pp", "<", "secondary", w=36, h=26, size=14, anchor={"right": 4})))
    ap.append(("#" + pr_, lab(WT + "Pg", "", 12, "text", bold=True, w=110, h=26, halign="Center")))
    ap.append(("#" + pr_, G_.glass_button(WT + "Pn", ">", "secondary", w=36, h=26, size=14, anchor={"left": 4, "right": 8})))
    ap.append(("#" + pr_, lab(WT + "Tf", "", 12, "dim", w=WT_LI - 36 - 4 - 110 - 36 - 12, h=26, halign="End")))
    ap.sets.append((WT + "Tf", "Text", WT_TXT["tfoot"]))
    assert 20 + 24 + 8 + WT_TR * (WT_RH + 6) + 6 + 28 <= WT_TOP_H, "0.3.62: the travel panel fits"
    ap.append(("#" + up_, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== TOP RIGHT: QUESTS (the tracked quest - SkyyQuests quest:fn:hud)
    qs = WT + "Qs"
    ap.append(("#" + up_, G_.glass_group(qs, WT_Q, WT_TOP_H, role="panel", layout="Top", pad=10)))
    qh = head(qs, "Qh", "QUESTS", WT_QI, 200)
    ap.append(("#" + qh, lab(WT + "Qc", "", 12, "xp", bold=True, w=200, h=24, halign="End")))
    ap.append(("#" + qs, lab(None, "TRACKED", 12, "dim", bold=True, w=WT_QI, h=18, anchor={"top": 8})))
    ap.append(("#" + qs, lab(WT + "Qt", "", 17, "title", bold=True, w=WT_QI, h=28)))
    for k_ in range(WT_QN):
        q_ = "%sQ%d" % (WT, k_)
        ap.append(("#" + qs, G_.glass_group(q_, WT_QI, 50, layout="Top", anchor={"top": 4})))
        holder(q_, q_ + "N", WT_QI, 20, 13, ["text", "green"], bold=True)
        ap.append(("#" + q_, lab(q_ + "W", "", 11, "dim", w=WT_QI, h=16)))
        ap.append(("#" + q_, 'Group #%sB { Anchor: (Width: %d, Height: 8, Top: 2); LayoutMode: Left; Background: %s; }' % (q_, WT_BARQ, IV_TRACK)))
    qb = WT + "Qb"
    ap.append(("#" + qs, G_.glass_group(qb, WT_QI, 34, layout="Left", anchor={"top": 10})))
    ap.append(("#" + qb, G_.glass_button(WT + "Qlog", "Quest log", "primary", w=160, h=34, size=14, anchor={"right": 10})))
    ap.append(("#" + qb, lab(WT + "Qn", "", 12, "dim", w=WT_QI - 170, h=34)))
    ap.sets.append((WT + "Qn", "Text", WT_TXT["qnote"]))
    assert 20 + 24 + 8 + 18 + 28 + WT_QN * 54 + 10 + 34 <= WT_TOP_H, "0.3.62: the quests panel fits"
    # ======== BOTTOM
    dn = WT + "Dn"
    ap.append(("#" + body, G_.glass_group(dn, IV_IW, WT_BOT_H, layout="Left", anchor={"top": 8})))
    # ---- YOUR ISLAND (SkyyIslands: island:<uuid>, island:role:fn, island:fn:homes; Go home = /island)
    il = WT + "Il"
    ap.append(("#" + dn, G_.glass_group(il, WT_I, WT_BOT_H, role="panel", layout="Top", pad=10)))
    ap.append(("#" + il, lab(None, "YOUR ISLAND", 15, "accentHi", bold=True, w=WT_II, h=24)))
    ap.append(("#" + il, lab(WT + "I1", "", 17, "title", bold=True, w=WT_II, h=28, anchor={"top": 8})))
    ap.append(("#" + il, lab(WT + "I2", "", 13, "text", w=WT_II, h=22, anchor={"top": 4})))
    ap.append(("#" + il, lab(WT + "I3", "", 13, "text", w=WT_II, h=22)))
    ap.append(("#" + il, lab(WT + "I4", "", 12, "dim", w=WT_II, h=20, anchor={"top": 10})))
    ap.sets.append((WT + "I4", "Text", WT_TXT["ihint"]))
    ib = WT + "Ib"
    ap.append(("#" + il, G_.glass_group(ib, WT_II, 36, layout="Left", anchor={"top": 14})))
    ap.append(("#" + ib, G_.glass_button(WT + "Ihome", "Go home", "primary", w=150, h=36, size=14, anchor={"right": 10})))
    ap.append(("#" + ib, G_.glass_button(WT + "Iset", "Island settings", "secondary", w=180, h=36, size=14)))
    assert 20 + 24 + 8 + 28 + 4 + 22 + 22 + 10 + 20 + 14 + 36 <= WT_BOT_H and 150 + 10 + 180 <= WT_II, "0.3.62: the island card fits"
    ap.append(("#" + dn, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ---- EXPLORE (SkyyExploration: explore:<uuid>, explore:fn:title, explore:fn:pct)
    ex = WT + "Ex"
    ap.append(("#" + dn, G_.glass_group(ex, WT_E, WT_BOT_H, role="panel", layout="Top", pad=10)))
    eh = head(ex, "Eh", "EXPLORE", WT_EI, 260)
    ap.append(("#" + eh, lab(WT + "El", "", 13, "xp", bold=True, w=260, h=24, halign="End")))
    ap.append(("#" + ex, lab(WT + "E1", "", 13, "text", w=WT_EI, h=20, anchor={"top": 6})))
    ap.append(("#" + ex, lab(WT + "E2", "", 13, "gold", bold=True, w=WT_EI, h=20)))
    ap.append(("#" + ex, lab(None, "DISCOVERED", 12, "dim", bold=True, w=WT_EI, h=18, anchor={"top": 8})))
    for k_ in range(WT_EN):
        e_ = "%sE%dr" % (WT, k_)
        ap.append(("#" + ex, G_.glass_group(e_, WT_EI, 26, layout="Left", anchor={"top": 4})))
        ap.append(("#" + e_, lab("%sE%dN" % (WT, k_), "", 13, "text", w=WT_ENW, h=26, anchor={"right": 8})))
        ap.append(("#" + e_, 'Group #%sE%dB { Anchor: (Width: %d, Height: 8, Top: 9); LayoutMode: Left; Background: %s; }' % (WT, k_, WT_EBW, IV_TRACK)))
        ap.append(("#" + e_, lab("%sE%dP" % (WT, k_), "", 13, "xp", bold=True, w=WT_EPW, h=26, halign="End")))
    ap.append(("#" + ex, lab(WT + "Em", "", 12, "dim", w=WT_EI, h=18, anchor={"top": 4})))
    ap.append(("#" + ex, G_.glass_button(WT + "Ego", "Explore page", "secondary", w=180, h=34, size=14, anchor={"top": 10})))
    assert 20 + 24 + 6 + 20 + 20 + 8 + 18 + WT_EN * 30 + 4 + 18 + 10 + 34 <= WT_BOT_H and WT_ENW + 8 + WT_EBW + WT_EPW <= WT_EI, "0.3.62: the explore card fits"
    ap.append(("#" + dn, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ---- BESTIARY + DROPS (SkyyCollections coll:fn:catTotal Combat; the codex lives in the Collections page)
    cx = WT + "Cx"
    ap.append(("#" + dn, G_.glass_group(cx, WT_C, WT_BOT_H, role="panel", layout="Top", pad=10)))
    ap.append(("#" + cx, lab(None, "BESTIARY AND DROPS", 15, "accentHi", bold=True, w=WT_CI, h=24)))
    ap.append(("#" + cx, lab(WT + "C1", "", 17, "xp", bold=True, w=WT_CI, h=28, anchor={"top": 8})))
    for k_ in ("c2", "c3"):
        ap.append(("#" + cx, lab(WT + k_.upper(), "", 13, "text", w=WT_CI, h=20, anchor={"top": 6 if k_ == "c2" else 0})))
        ap.sets.append((WT + k_.upper(), "Text", WT_TXT[k_]))
    ap.append(("#" + cx, G_.glass_button(WT + "Cgo", "Collections", "secondary", w=180, h=34, size=14, anchor={"top": 14})))
    assert 20 + 24 + 8 + 28 + 6 + 40 + 14 + 34 <= WT_BOT_H, "0.3.62: the codex card fits"
    assert (IV_PAGE_H <= SUI.MAX_PAGE_H and IV_PAGE_W <= SUI.MAX_PAGE_W and WT_TOP_H + 8 + WT_BOT_H == IV_BODY_H
            and WT_L + WT_Q + IV_GAP == IV_IW and WT_I + WT_E + WT_C + 2 * IV_GAP == IV_IW), "0.3.62: the world screen fits one 1080p screen"
    # ---- the caption + key hints
    hn = WT + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(WT + "K%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate((("LMB", "Go / select"), ("Tab / Esc", "Close")))]
    hw = sum(w_ for _m, w_ in parts)
    ap.append(("#" + hn, lab(WT + "Cap", "", 14, "dim", w=IV_IW - hw - 20, h=IV_HINT_H)))
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    binds = [("#%sT%d" % (WT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + WT + "Close", "close"), ("#" + WT + "Full", "full"),
                                                                                  ("#" + WT + "Pp", "pg:-1"), ("#" + WT + "Pn", "pg:1"),
                                                                                  ("#" + WT + "Qlog", "qlog"), ("#" + WT + "Iset", "isl"),
                                                                                  ("#" + WT + "Ego", "exp"), ("#" + WT + "Cgo", "coll")]
    return ap, binds


WT_AP, WT_BINDS = _wt_page()
SUI.check_page(WT_AP, WT)
for _p, _mk in WT_AP:
    SUI.check_markup(_mk, prefix=WT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.62: the world screen never scrolls"
_wt_ids = set(i_ for _p, mk_ in WT_AP for i_ in SUI._static_ids(mk_))
for _s, _a in WT_BINDS:
    assert _s[1:] in _wt_ids, ("0.3.62: binding target", _s)
WT_DYN = (["Coins", "Close", "Full", "Cap", "Fl", "Lt", "Pp", "Pg", "Pn", "Tf", "Qc", "Qt", "Qlog", "Qn", "I1", "I2", "I3", "I4", "Ihome", "Iset",
           "El", "E1", "E2", "Em", "Ego", "C1", "C2", "C3", "Cgo"]
          + ["R%d%s" % (k_, x_) for k_ in range(WT_TN) for x_ in ("", "I", "N", "S", "Go")]
          + ["Q%d%s" % (k_, x_) for k_ in range(WT_QN) for x_ in ("", "N0", "N1", "W", "B")]
          + ["E%d%s" % (k_, x_) for k_ in range(WT_EN) for x_ in ("r", "N", "B", "P")])
for _g in WT_DYN:
    assert WT + _g in _wt_ids, "0.3.62: the world screen has #" + WT + _g
WT_RUNTIME_IDS = ["Fc%d" % k_ for k_ in range(len(WT_FILT))]
assert not [x_ for x_ in WT_RUNTIME_IDS if WT + x_ in _wt_ids], "0.3.62: a run-time id is also a static id"
_wt_tok = SUI.proven_tokens(list(WT_AP))
WT_UNPROVEN = sorted(k_ for k_, g_ in _wt_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_)))
assert set(WT_UNPROVEN) <= set(["SlotBackground"]), "0.3.62: only SlotBackground (proven on the inventory page, TEST 282): %s" % WT_UNPROVEN
assert not [k_ for k_ in _wt_tok if k_ in ("MouseEntered", "MouseExited", "TooltipText")], "0.3.62: no hover events / tooltips of ours"
SUI.assert_glass_paths(WT_AP)
_wt_glass = set(re.findall(r"SkyyGlass/([A-Za-z0-9]+)\.png", " ".join(SUI.render(mk_) for _p, mk_ in WT_AP)))
_mt_glass = set(re.findall(r"SkyyGlass/([A-Za-z0-9]+)\.png", " ".join(SUI.render(mk_) for _p, mk_ in MT_AP)))
assert _wt_glass <= _mt_glass, ("0.3.62: the world screen names only Skyglass pictures the market screen already ships (no new picture)", sorted(_wt_glass - _mt_glass))
WT_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in WT_AP)
WT_RUNTIME_MAX = len(WT_FILT) + WT_QN + WT_EN                 # the filter chips + a fill per quest step + a fill per explore row
WT_ELEMENTS = WT_SHELL_ELEMENTS + WT_RUNTIME_MAX
assert WT_ELEMENTS <= 800, "0.3.62: the world screen stays well under the ~1,600 element budget (%d static + %d at run time)" % (WT_SHELL_ELEMENTS, WT_RUNTIME_MAX)
WT_LK, WT_LP, WT_LB = [], [], []
for _p, _mk in WT_AP:
    WT_LK.append("A")
    WT_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    WT_LB.append(SUI.render(_mk))
for _i, _pr, _v in WT_AP.sets:
    WT_LK.append("S")
    WT_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    WT_LB.append(_v)
for _s, _a in WT_BINDS:
    WT_LK.append("E")
    WT_LP.append(_s)
    WT_LB.append(_a)
assert WT_LK[0] == "A" and WT_LP[0] == "", "0.3.62: the page data starts with the root"
for _x in WT_LP + WT_LB:
    assert "@" not in _x and "\n" not in _x and len(_x.encode("utf-8")) < 60000, "0.3.62: a page line Java can hold"
print("0.3.62 world screen: %d elements (shell %d + at most %d at run time; budget ~1,600), %d appends, %d b.set, %d bindings; unproven: %s"
      % (WT_ELEMENTS, WT_SHELL_ELEMENTS, WT_RUNTIME_MAX, len(WT_AP), len(WT_AP.sets), len(WT_BINDS), ", ".join(WT_UNPROVEN)))

'''
P.rep('''PKG = T["PKG"]
# 0.2: every class goes through mk()''', WT_PAGE.lstrip("\n") + '''PKG = T["PKG"]
# 0.2: every class goes through mk()''')

# ---------- the two new classes
P.rep('''mtab = mk("MarketTab", T["PAGE"])   # 0.3.59: THE MARKET TAB = ONE SCREEN
''', '''mtab = mk("MarketTab", T["PAGE"])   # 0.3.59: THE MARKET TAB = ONE SCREEN
wtd  = mk("WorldTabData")   # 0.3.62: the world screen's data (LK / LP / LB, the run-time markup)
wtab = mk("WorldTab", T["PAGE"])    # 0.3.62: THE WORLD TAB = ONE SCREEN
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, mtd, mtab, pl)''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, mtd, mtab, wtd, wtab, pl)''')

# ---------- WorldTabData constants + WorldTab fields / constructor (after the MarketTab constructor)
WT_DATA = r'''# 0.3.62: THE WORLD SCREEN DATA (WorldTabData) + the WorldTab fields
F(wtd, "public static final String LK = %s;" % jstr("".join(WT_LK)))
F(wtd, "public static final String[] LP = %s;" % jarr(WT_LP))
F(wtd, "public static final String[] LB = %s;" % jarr(WT_LB))
F(wtd, "public static final String[] FILT = %s;" % jarr(WT_FILT))
for _n, _v in (("TN", WT_TN), ("QN", WT_QN), ("EN", WT_EN), ("BARQ", WT_BARQ), ("BARE", WT_EBW), ("CHW", WT_CHW)):
    F(wtd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("CHIP", WT_CHIP), ("ST_CH", WT_ST_CH), ("ST_CHSEL", WT_ST_CHSEL), ("FILL", WT_FILL), ("CAP0", WT_TXT["cap0"]),
               ("IC_ISLAND", WT_ICON["island"]), ("IC_HUB", WT_ICON["hub"]), ("IC_IHOME", WT_ICON["ihome"]), ("IC_HOME", WT_ICON["home"])):
    F(wtd, "public static final String %s = %s;" % (_n, jstr(_v)))
for _f in ("public static volatile int OPENS = 0;", "public static volatile int STALE = 0;", "public static volatile int GOES = 0;",
           "public volatile boolean closed;", "public boolean answered;", "public String via;", "public String tcap;", "public long seq;", "public long base;",
           "public String tok;", "public String pkey;", "public int filt;", "public int page;", "public int pages;", "public String[] keys;",
           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;"):
    F(wtab, _f)
C(wtab, r"""
public WorldTab(@PR@ pr, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.via = via;
  this.closed = false;
  this.answered = false;
  this.tcap = "";
  this.seq = 0L;
  this.base = System.nanoTime() & 0xffffffL;
  this.tok = "";
  this.pkey = null;
  this.filt = 0;
  this.page = 0;
  this.pages = 1;
  this.keys = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
'''
P.rep('''  this.calls = 0;
}""")
for _iface, _cls in ((T["SPH"], ihk)''', '''  this.calls = 0;
}""")
''' + WT_DATA + '''for _iface, _cls in ((T["SPH"], ihk)''')

# ---------- WorldTab.open BEFORE the market screen's open (every caller below can reach it)
WT_OPEN = r'''# ---- 0.3.62: the WORLD SCREEN opens (the inventory's / skill page's / pets screen's / market screen's World tab); null = it could not open =
# the caller opens today's World page instead. Needs no bridge key: the travel list is SkyyMenu's own; each card says when its mod is missing.
M(wtab, r"""
public static @PKG@.WorldTab open(@REF@ ref, @ST@ st, @PR@ pr, String via) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  @PKG@.WorldTab pg = new @PKG@.WorldTab(pr, via);
  pg.pref = ref;
  pg.pst = st;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("world screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")
'''
P.rep('''# ---- 0.3.59: the MARKET SCREEN opens (the inventory's / skill page's / pets screen's Market tab); null = SkyyBazaar has no bazaar:fn:tab /
''', WT_OPEN + '''# ---- 0.3.59: the MARKET SCREEN opens (the inventory's / skill page's / pets screen's Market tab); null = SkyyBazaar has no bazaar:fn:tab /
''')
# the skill page's World tab = this screen (else today's route, as before)
P.rep('''M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
  if (i == 2 && petsTab()) return;   // 0.3.58
  if (i == 3 && marketTab()) return;   // 0.3.59
''', '''# 0.3.62: the World tab = the world screen (false = it could not open: today's route below)
M(skpg, r"""
public boolean worldTab() {
  @PKG@.WorldTab pg = null;
  try { pg = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "skill page"); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the world screen failed: " + t); }
  if (pg == null) return false;
  this.answered = true;
  if (!still()) finish("world");
  return true;
}""")
M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
  if (i == 2 && petsTab()) return;   // 0.3.58
  if (i == 3 && marketTab()) return;   // 0.3.59
  if (i == 4 && worldTab()) return;   // 0.3.62
''')
# the pets screen's World tab = this screen
P.rep('''    if (mt != null) { if (!still()) finish("market"); return; }
  }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }''', '''    if (mt != null) { if (!still()) finish("market"); return; }
  }
  if (i == 4) {   // 0.3.62: the world screen (else today's route below)
    @PKG@.WorldTab wt = null;
    try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "pets screen"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("pets screen: the world screen failed: " + t); }
    if (wt != null) { if (!still()) finish("world"); return; }
  }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }''')
# the market screen's World tab = this screen
P.rep('''  if (i == 3) { say("You are on Market"); return; }
''', '''  if (i == 3) { say("You are on Market"); return; }
  if (i == 4) {   // 0.3.62: the world screen (else today's route below)
    @PKG@.WorldTab wt = null;
    try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "market screen"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("market screen: the world screen failed: " + t); }
    if (wt != null) { if (!still()) finish("world"); return; }
  }
''')

WT_JAVA = r'''# ================= 0.3.62 WorldTab: THE WORLD TAB = ONE SCREEN (approved world-page.png v2; the map art is a later round) =================
# Reads only existing bridges (island:<uuid>, island:role:fn, island:fn:homes, essentials:fn:homes / warps, explore:<uuid>, explore:fn:title,
# explore:fn:pct, quest:fn:hud, coll:fn:catTotal) + the engine's warps. Every teleport = the old Teleport page's own path (the /island + /hub
# commands, island:fn:gohome, essentials:fn:gohome, the engine Teleport component for a warp). Every bound click answers with ONE page packet.
M(wtab, r"""
public Object call(String key, Object arg) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null) return null;
  try { return f.apply(arg); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: " + key + " failed: " + t); return null; }
}""")
M(wtab, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyyWtabCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(wtab, r"""
public void finish(String why) { this.closed = true; }""")
M(wtab, r"""
public void shut() { finish("closed"); this.close(); }""")
M(wtab, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(wtab, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.answers = this.answers + 1;
  this.rebuild();
}""")
M(wtab, r"""
public static void hold(@UCB@ b, String base, int n, int which, String text) {
  for (int k = 0; k < n; k++) {
    b.set("#" + base + k + ".Text", text == null ? "" : text);
    b.set("#" + base + k + ".Visible", k == which);
  }
}""")
M(wtab, r"""
public static java.util.ArrayList one(@IGS@ g) { java.util.ArrayList l = new java.util.ArrayList(); l.add(g); return l; }""")
# a travel icon: a NEW ItemStack(id, 1) without metadata, only for ids the server knows (our own icon items); greyed when it cannot be used
M(wtab, r"""
public static @IGS@ cell(String id, String name, String desc, boolean ok) {
  @IGS@ g = new @IGS@();
  if (id != null && id.length() > 0 && id.length() < 120 && @PKG@.InvPage.known(id)) g.setItemStack(new @IS@(id, 1));
  if (name != null && name.length() > 0) g.setName(name);
  if (desc != null && desc.length() > 0) g.setDescription(desc);
  if (!ok) g.setItemUncraftable(true);
  return g;
}""")
# a command the player runs (/island, /hub): the CommandManager's own lookup (the old Teleport page's "not installed" test)
M(wtab, r"""
public static boolean hasCmd(String c) { return @PKG@.MenuUtil.cmd(c) != null; }""")
# a bridge's home list exactly as the old Teleport page reads it (MenuPage.homesOf): null = no bridge; names that break the key rule left out
M(wtab, r"""
public static String[] homes(String key, java.util.UUID u) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(u);
    if (r instanceof String[]) {
      String[] a = (String[]) r;
      java.util.ArrayList ok = new java.util.ArrayList();
      for (int i = 0; i < a.length; i++) { if (a[i] != null && @PKG@.MenuLayout.okWarp(a[i]) && !ok.contains(a[i])) ok.add(a[i]); }
      return (String[]) ok.toArray(new String[0]);
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: " + key + " failed: " + t); }
  return new String[0];
}""")
# every place the old World > Teleport page offers (Spawn + Arrange: Full page): { key, icon, name, hover text, "1" usable / "0", kind }
# kind i = your island + island homes, h = homes, w = the hub + warps (the zone hub towns are warps)
M(wtab, r"""
public java.util.ArrayList places() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList out = new java.util.ArrayList();
  boolean isl = hasCmd("island");
  out.add(new String[] { "tp:island", @PKG@.WorldTabData.IC_ISLAND, isl ? "Your island" : "Your island (not on this server)",
                         isl ? "Teleport to your island" : "Islands are not on this server right now", isl ? "1" : "0", "i" });
  String[] ih = homes("island:fn:homes", u);
  for (int i = 0; ih != null && i < ih.length; i++)
    out.add(new String[] { "ih:" + ih[i], @PKG@.WorldTabData.IC_IHOME, ih[i], "Island home " + ih[i] + " - on your island", "1", "i" });
  String[] zh = homes("essentials:fn:homes", u);
  for (int i = 0; zh != null && i < zh.length; i++)
    out.add(new String[] { "zh:" + zh[i], @PKG@.WorldTabData.IC_HOME, zh[i], "Your home " + zh[i], "1", "h" });
  boolean hb = hasCmd("hub");
  out.add(new String[] { "tp:hub", @PKG@.WorldTabData.IC_HUB, hb ? "Hub" : "Hub (not on this server)", hb ? "Go back to the hub" : "The hub is not on this server right now",
                         hb ? "1" : "0", "w" });
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
  if (tp == null || !tp.isWarpsLoaded()) {
    out.add(new String[] { "", @PKG@.MenuData.ICON_WARP, "Warps", "The warp list is still loading", "0", "w" });
    return out;
  }
  java.util.HashMap th = null;
  try { th = @PKG@.MenuPage.warpThemes(); } catch (Throwable t) { th = null; }
  java.util.ArrayList open = new java.util.ArrayList();
  java.util.ArrayList lock = new java.util.ArrayList();
  try {
    java.util.Iterator it = tp.getWarps().keySet().iterator();
    while (it.hasNext()) {
      String n = String.valueOf(it.next());
      if (!@PKG@.MenuLayout.okWarp(n)) continue;
      @WRP@ w = (@WRP@) tp.getWarps().get(n);
      if (w == null) continue;
      if (@PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId())) open.add(n); else lock.add(n);
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the warp list failed: " + t); }
  java.util.Collections.sort(open);
  java.util.Collections.sort(lock);
  for (int i = 0; i < open.size() + lock.size(); i++) {
    boolean ok = i < open.size();
    String n = (String) (ok ? open.get(i) : lock.get(i - open.size()));
    @WRP@ w = null;
    try { w = (@WRP@) tp.getWarps().get(n); } catch (Throwable t) { w = null; }
    if (w == null) continue;
    String id = @PKG@.MenuUtil.safe(w.getId());
    out.add(new String[] { "warp:" + n, ok ? @PKG@.MenuPage.themeIcon(th, n) : @PKG@.MenuData.ICON_WARP_LOCKED, ok ? id : id + " (locked)",
                           ok ? "Warp " + id + " - World: " + @PKG@.MenuUtil.safe(w.getWorld()) : "You have not unlocked the warp " + id + " yet", ok ? "1" : "0", "w" });
  }
  return out;
}""")
# TRAVEL: the filter chips (run time), 10 cards a page (2 columns), the pager; Go + the icon carry the page token
M(wtab, r"""
public void fillTravel(@UCB@ b, @UEB@ ev, java.util.ArrayList all) {
  String want = this.filt == 1 ? "i" : (this.filt == 2 ? "h" : (this.filt == 3 ? "w" : ""));
  java.util.ArrayList rs = new java.util.ArrayList();
  for (int i = 0; i < all.size(); i++) {
    String[] r = (String[]) all.get(i);
    if (want.length() == 0 || want.equals(r[5])) rs.add(r);
  }
  for (int k = 0; k < @PKG@.WorldTabData.FILT.length; k++) {
    b.appendInline("#SkyyWtabFl", @PKG@.WorldTabData.CHIP.replace("{I}", "Fc" + k).replace("{W}", String.valueOf(@PKG@.WorldTabData.CHW))
        .replace("{S}", k == this.filt ? @PKG@.WorldTabData.ST_CHSEL : @PKG@.WorldTabData.ST_CH));
    b.set("#SkyyWtabFc" + k + ".Text", @PKG@.WorldTabData.FILT[k]);
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabFc" + k, @EVD@.of("a", "flt:" + k));
  }
  int n = @PKG@.WorldTabData.TN;
  this.pages = (rs.size() + n - 1) / n;
  if (this.pages < 1) this.pages = 1;
  if (this.page >= this.pages) this.page = this.pages - 1;
  if (this.page < 0) this.page = 0;
  int from = this.page * n;
  this.keys = new String[n];
  b.set("#SkyyWtabLt.Text", rs.size() == 1 ? "1 place" : rs.size() + " places");
  b.set("#SkyyWtabPg.Text", "Page " + (this.page + 1) + " / " + this.pages);
  for (int k = 0; k < n; k++) {
    String r = "SkyyWtabR" + k;
    int j = from + k;
    if (j >= rs.size()) { b.set("#" + r + ".Visible", false); this.keys[k] = null; continue; }
    String[] f = (String[]) rs.get(j);
    boolean ok = "1".equals(f[4]) && f[0].length() > 0;
    this.keys[k] = f[0];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", @PKG@.InvPage.act(one(cell(f[1], f[2], f[3], ok))));
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(f[2], 40));
    b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip(f[3], 52));
    b.set("#" + r + "Go.Visible", ok);
    ev.addEventBinding(@BT@.SlotClicking, "#" + r + "I", @EVD@.of("a", "go:" + k).append("t", this.tok), false);
    ev.addEventBinding(@BT@.Activating, "#" + r + "Go", @EVD@.of("a", "go:" + k).append("t", this.tok));
  }
}""")
# QUESTS: SkyyQuests quest:fn:hud apply(UUID) -> Object[] { title, "3 / 24", then per shown step: name, progress, Double frac or null, where,
# Integer dir, Boolean done }; null = nothing to show; no key = not on this server
M(wtab, r"""
public void fillQuests(@UCB@ b) {
  boolean on = @PKG@.InvCraft.fn("quest:fn:hud") != null;
  Object r = null;
  if (on) r = call("quest:fn:hud", this.playerRef.getUuid());
  Object[] a = null;
  if (r instanceof Object[]) a = (Object[]) r;
  String tt = a != null && a.length >= 1 && a[0] instanceof String ? ((String) a[0]).trim() : "";
  String cn = a != null && a.length >= 2 && a[1] instanceof String ? ((String) a[1]).trim() : "";
  b.set("#SkyyWtabQc.Text", cn.length() > 0 ? "Steps " + @PKG@.MenuUtil.clip(cn, 16) : "");
  b.set("#SkyyWtabQt.Text", !on ? "Quests are not on this server right now" : (a == null || tt.length() == 0 ? "No quest to show right now" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(tt), 44)));
  int n = 0;
  for (int i = 2; a != null && i + 5 < a.length && n < @PKG@.WorldTabData.QN; i += 6) {
    String nm = a[i] instanceof String ? @PKG@.MenuUtil.safe(((String) a[i]).trim()) : "";
    if (nm.length() == 0) continue;
    String pg = a[i + 1] instanceof String ? ((String) a[i + 1]).trim() : "";
    String wh = a[i + 3] instanceof String ? @PKG@.MenuUtil.safe(((String) a[i + 3]).trim()) : "";
    boolean done = Boolean.TRUE.equals(a[i + 5]);
    double fr = a[i + 2] instanceof Number ? ((Number) a[i + 2]).doubleValue() : -1.0;
    String q = "SkyyWtabQ" + n;
    b.set("#" + q + ".Visible", true);
    hold(b, q + "N", 2, done ? 1 : 0, @PKG@.MenuUtil.clip((done ? "Done - " : "") + nm + (pg.length() > 0 ? "   " + pg : ""), 60));
    b.set("#" + q + "W.Text", @PKG@.MenuUtil.clip(wh, 70));
    int w = done ? @PKG@.WorldTabData.BARQ : (fr <= 0.0 || fr != fr ? 0 : (fr >= 1.0 ? @PKG@.WorldTabData.BARQ : (int) (fr * (double) @PKG@.WorldTabData.BARQ)));
    if (w > 0) b.appendInline("#" + q + "B", @PKG@.WorldTabData.FILL.replace("{W}", String.valueOf(w)));
    n++;
  }
  for (int k = n; k < @PKG@.WorldTabData.QN; k++) b.set("#SkyyWtabQ" + k + ".Visible", false);
}""")
# YOUR ISLAND: island:<uuid> = the home island's world (SkyyIslands), island:role:fn {UUID, world} -> the role word, island:fn:homes
M(wtab, r"""
public void fillIsland(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  boolean cmd = hasCmd("island");
  Object w = null;
  try { w = @PKG@.MenuUtil.bridge().get("island:" + u); } catch (Throwable t) { w = null; }
  boolean has = w instanceof String && ((String) w).length() > 0;
  boolean on = cmd || has || @PKG@.InvCraft.fn("island:fn:homes") != null;
  String role = null;
  if (has && @PKG@.InvCraft.fn("island:role:fn") != null) {
    Object o = call("island:role:fn", new Object[] { u, (String) w });
    if (o instanceof String) role = (String) o;
  }
  String[] ih = homes("island:fn:homes", u);
  b.set("#SkyyWtabI1.Text", !on ? "Islands are not on this server right now" : (has ? "Your island" : "No island yet"));
  String r2 = "";
  if (has && role != null) r2 = role.equals("owner") ? "You own this island" : "Your role there: " + @PKG@.MenuUtil.clip(role, 20);
  else if (on && !has && cmd) r2 = "Go home takes you to your island.";
  b.set("#SkyyWtabI2.Text", r2);
  b.set("#SkyyWtabI3.Text", ih == null ? "" : (ih.length == 1 ? "1 island home" : ih.length + " island homes") + (ih.length > 0 ? " - in Travel (Islands)" : ""));
  b.set("#SkyyWtabIhome.Visible", cmd);
  ev.addEventBinding(@BT@.Activating, "#SkyyWtabIhome", @EVD@.of("a", "home").append("t", this.tok));
}""")
# EXPLORE: explore:<uuid> = "level:12,zones:7/27,chests:12,chunks:1204,title:wayfarer,spots:3,secrets:1,island:2/5" (the ACTIVE profile),
# explore:fn:title apply(UUID) -> the title's name or null, explore:fn:pct apply(Object[] {UUID, world}) -> "73|11|15|Fens Island" or null
M(wtab, r"""
public static String part(String s, String k) {
  if (s == null) return "";
  String[] a = s.split(",");
  for (int i = 0; i < a.length; i++) {
    int c = a[i].indexOf(':');
    if (c > 0 && a[i].substring(0, c).trim().equals(k)) return a[i].substring(c + 1).trim();
  }
  return "";
}""")
M(wtab, r"""
public java.util.ArrayList worlds() {
  java.util.ArrayList ns = new java.util.ArrayList();
  try {
    java.util.UUID wu = this.playerRef.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w != null && w.getName() != null) ns.add(String.valueOf(w.getName()));
  } catch (Throwable t) { }
  try {
    java.util.Map ws = @UNI@.get().getWorlds();
    Object[] vs = ws == null ? new Object[0] : ws.values().toArray();
    java.util.ArrayList rest = new java.util.ArrayList();
    for (int i = 0; i < vs.length && i < 64; i++) {
      if (!(vs[i] instanceof @WLD@)) continue;
      String n = String.valueOf(((@WLD@) vs[i]).getName());
      if (!ns.contains(n) && !rest.contains(n)) rest.add(n);
    }
    java.util.Collections.sort(rest);
    ns.addAll(rest);
  } catch (Throwable t) { }
  return ns;
}""")
M(wtab, r"""
public void fillExplore(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  Object so = null;
  try { so = @PKG@.MenuUtil.bridge().get("explore:" + u); } catch (Throwable t) { so = null; }
  String s = so instanceof String ? (String) so : null;
  boolean on = s != null || @PKG@.InvCraft.fn("explore:fn:pct") != null;
  String lv = part(s, "level");
  b.set("#SkyyWtabEl.Text", lv.length() > 0 ? "Exploration Lv " + @PKG@.MenuUtil.clip(lv, 6) : "");
  if (!on) b.set("#SkyyWtabE1.Text", "Exploring is not on this server right now");
  else if (s == null) b.set("#SkyyWtabE1.Text", "Walk around - new places count here.");
  else {
    String z = part(s, "zones").replace("/", " / ");
    b.set("#SkyyWtabE1.Text", @PKG@.MenuUtil.clip("Zones found " + z + "    Chests " + part(s, "chests") + "    Spots " + part(s, "spots") + "    Secrets " + part(s, "secrets"), 80));
  }
  Object t = null;
  if (@PKG@.InvCraft.fn("explore:fn:title") != null) t = call("explore:fn:title", u);
  b.set("#SkyyWtabE2.Text", !on ? "" : (t instanceof String && ((String) t).length() > 0 ? "Title: " + @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe((String) t), 40) : "No title worn yet"));
  int n = 0;
  if (@PKG@.InvCraft.fn("explore:fn:pct") != null) {
    java.util.ArrayList ws = worlds();
    for (int i = 0; i < ws.size() && n < @PKG@.WorldTabData.EN; i++) {
      Object r = call("explore:fn:pct", new Object[] { u, (String) ws.get(i) });
      if (!(r instanceof String)) continue;
      String[] f = ((String) r).split("\\|", -1);
      if (f.length < 4) continue;
      int pc = @PKG@.InvPage.toInt(f[0].trim(), -1);
      if (pc < 0) continue;
      if (pc > 100) pc = 100;
      String e = "SkyyWtabE" + n;
      b.set("#" + e + "r.Visible", true);
      b.set("#" + e + "N.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[3].length() > 0 ? f[3] : (String) ws.get(i)), 30));
      b.set("#" + e + "P.Text", pc + String.valueOf((char) 37));
      int w = @PKG@.InvPage.barW((long) pc, 100L, @PKG@.WorldTabData.BARE);
      if (w > 0) b.appendInline("#" + e + "B", @PKG@.WorldTabData.FILL.replace("{W}", String.valueOf(w)));
      n++;
    }
  }
  for (int k = n; k < @PKG@.WorldTabData.EN; k++) b.set("#SkyyWtabE" + k + "r.Visible", false);
  b.set("#SkyyWtabEm.Text", !on ? "" : (n == 0 ? "No world with exploration spots is loaded right now." : "Your world first, then every loaded world with spots."));
}""")
# BESTIARY + DROPS: SkyyCollections coll:fn:catTotal apply(Object[] {UUID, "Combat"}) -> Long (every mob drop collected), null = unknown
M(wtab, r"""
public void fillCodex(@UCB@ b) {
  boolean on = @PKG@.InvCraft.fn("coll:fn:catTotal") != null;
  Object o = null;
  if (on) o = call("coll:fn:catTotal", new Object[] { this.playerRef.getUuid(), "Combat" });
  b.set("#SkyyWtabC1.Text", !on ? "Collections are not on this server right now" : (o instanceof Number ? "Mob drops collected: " + @PKG@.MenuUtil.fmt(((Number) o).longValue()) : "Mob drops collected: -"));
}""")
M(wtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.WorldTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.WorldTabData.LP[i];
    String y = @PKG@.WorldTabData.LB[i];
    if (k == 'A') b.appendInline(x.length() == 0 ? (String) null : x, y);
    else if (k == 'S') b.set(x, y);
    else if (k == 'E') ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
  }
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  this.builds = this.builds + 1;
  java.util.UUID u = this.playerRef.getUuid();
  this.pkey = @PKG@.Given.key(u);
  long c = -1L;
  try { c = @PKG@.MenuUtil.purse(u); } catch (Throwable t) { c = -1L; }
  b.set("#SkyyWtabCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  try { fillTravel(b, ev, places()); } catch (Throwable t) { this.keys = new String[0]; @PKG@.MenuUtil.warn("world screen: the travel list failed: " + t); }
  try { fillQuests(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the quests card failed: " + t); }
  try { fillIsland(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the island card failed: " + t); }
  try { fillExplore(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the explore card failed: " + t); }
  try { fillCodex(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the codex card failed: " + t); }
  b.set("#SkyyWtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.WorldTabData.CAP0);
}""")
# ---- the actions (each answers with ONE packet: a redraw, a caption, a page that replaces this one, or the close)
M(wtab, r"""
public void hub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    if (tab != null && tab.length() > 0) r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("world screen: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
M(wtab, r"""
public void tabGo(int i) {
  this.answered = true;
  if (i == 0) {
    @PKG@.InvPage pg = null;
    try { pg = @PKG@.InvState.openAt(this.pref, this.pst, this.playerRef, "world screen", "c", -1); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("world screen: the inventory failed: " + t); }
    if (pg == null) { if (still()) say("The inventory could not open here"); return; }
    if (!still()) finish("inventory");
    return;
  }
  if (i == 1) {
    @PKG@.SkillPage sp = null;
    try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, @PKG@.SkillPage.lastOf(this.playerRef.getUuid()), "world screen"); } catch (Throwable t) { sp = null; @PKG@.MenuUtil.warn("world screen: the skill page failed: " + t); }
    if (sp == null) { hub(@PKG@.InvData.TAB_HUB[1], @PKG@.InvData.TAB_TAB[1], @PKG@.InvData.TAB_NAME[1]); return; }
    if (!still()) finish("skills");
    return;
  }
  if (i == 2) {
    @PKG@.PetsTab pt = null;
    try { pt = @PKG@.PetsTab.open(this.pref, this.pst, this.playerRef, "world screen"); } catch (Throwable t) { pt = null; @PKG@.MenuUtil.warn("world screen: the pets screen failed: " + t); }
    if (pt == null) { hub(@PKG@.InvData.TAB_HUB[2], @PKG@.InvData.TAB_TAB[2], @PKG@.InvData.TAB_NAME[2]); return; }
    if (!still()) finish("pets");
    return;
  }
  if (i == 3) {
    @PKG@.MarketTab mt = null;
    try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "world screen"); } catch (Throwable t) { mt = null; @PKG@.MenuUtil.warn("world screen: the market screen failed: " + t); }
    if (mt == null) { hub(@PKG@.InvData.TAB_HUB[3], @PKG@.InvData.TAB_TAB[3], @PKG@.InvData.TAB_NAME[3]); return; }
    if (!still()) finish("market");
    return;
  }
  if (i == 4) { say("You are on World"); return; }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }
  hub(@PKG@.InvData.TAB_HUB[i], @PKG@.InvData.TAB_TAB[i], @PKG@.InvData.TAB_NAME[i]);
}""")
# Your island / Hub = the command as the player, the page closed first (InvPage.teleport: shut + handleCommand)
M(wtab, r"""
public void cmdGo(String c) {
  this.answered = true;
  if (!hasCmd(c)) { say(c.equals("hub") ? "The hub is not on this server right now" : "Islands are not on this server right now"); return; }
  shut();
  GOES = GOES + 1;
  try { @CMGR@.get().handleCommand(this.playerRef, c); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: /" + c + " failed: " + t); }
}""")
# an island home = island:fn:gohome; the page closes first (the /island teleport may change worlds - MenuPage.goHome's order)
M(wtab, r"""
public void islandHome(String n) {
  this.answered = true;
  java.util.function.Function f = @PKG@.InvCraft.fn("island:fn:gohome");
  if (f == null) { say("Island homes are not on this server right now"); return; }
  shut();
  GOES = GOES + 1;
  try { f.apply(new Object[] { this.playerRef.getUuid(), n }); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: island:fn:gohome failed: " + t); }
}""")
# a home = essentials:fn:gohome: "ok" = queued on the player's world thread -> the page closes; else the reason (MenuPage.goHome)
M(wtab, r"""
public void homeGo(String n) {
  this.answered = true;
  java.util.function.Function f = @PKG@.InvCraft.fn("essentials:fn:gohome");
  if (f == null) { say("Homes are not on this server right now"); return; }
  Object r = null;
  try { r = f.apply(new Object[] { this.playerRef.getUuid(), n }); } catch (Throwable t) { r = null; @PKG@.MenuUtil.warn("world screen: essentials:fn:gohome failed: " + t); }
  String s = r == null ? "" : String.valueOf(r);
  if (s.equals("ok")) { GOES = GOES + 1; shut(); return; }
  this.tcap = s.length() == 0 ? "That did not work - try again." : "Could not go home: " + @PKG@.MenuUtil.clip(s, 90);
  redraw();
}""")
# a warp: the same engine calls as the inventory's teleport row (InvPage.warpGo) and the old Teleport page (MenuPage.doWarp)
M(wtab, r"""
public void warpGo(String n) {
  this.answered = true;
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
  if (tp == null || !tp.isWarpsLoaded()) { say("Warps are still loading - try again in a moment"); return; }
  @WRP@ w = (@WRP@) tp.getWarps().get(n);
  if (w == null) { say("That warp was removed"); return; }
  String id = @PKG@.MenuUtil.safe(w.getId());
  if (!@PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId())) { say("You have not unlocked the warp " + id + " yet"); return; }
  @WLD@ target = null;
  try { target = @UNI@.get().getWorld(w.getWorld()); } catch (Throwable t) { target = null; }
  @TP@ t = null;
  try { t = w.toTeleport(); } catch (Throwable t2) { t = null; }
  if (target == null || t == null) { say("The world of warp " + id + " is not loaded"); return; }
  @REF@ ref = this.pref;
  @ST@ st = this.pst;
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { say("You are already teleporting"); return; }
  @WLD@ here = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); here = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }
  @TC@ mtc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
  shut();
  GOES = GOES + 1;
  st.addComponent(ref, @TP@.getComponentType(), t);
  try {
    if (here != null && mtc != null && mtc.getPosition() != null) {
      @V3D@ p = mtc.getPosition();
      @R3F@ r = mhr != null ? mhr.getRotation() : null;
      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());
      if (h != null) h.append(here, new @V3D@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@(), "Menu: warp " + id);
    }
  } catch (Throwable t3) { }
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to warp " + id + "..."));
}""")
M(wtab, r"""
public void travel(String k) {
  this.answered = true;
  if (k == null) { say("Nothing there"); return; }
  if (k.length() == 0) { say("Warps are still loading - try again in a moment"); return; }
  if (k.equals("tp:island")) { cmdGo("island"); return; }
  if (k.equals("tp:hub")) { cmdGo("hub"); return; }
  if (k.startsWith("ih:")) { islandHome(k.substring(3)); return; }
  if (k.startsWith("zh:")) { homeGo(k.substring(3)); return; }
  if (k.startsWith("warp:")) { warpGo(k.substring(5)); return; }
  say("Nothing there");
}""")
M(wtab, r"""
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
    if (a.equals("full")) { hub("world", "teleport", "the Teleport page"); return; }
    if (a.equals("isl")) { hub("world", "island", "Island settings"); return; }
    if (a.equals("exp")) { hub("world", "explore", "the Explore page"); return; }
    if (a.equals("qlog")) { hub("world", "quests", "the Quest log"); return; }
    if (a.equals("coll")) { hub("character", "collections", "Collections"); return; }
    if (a.startsWith("flt:")) {
      int k = @PKG@.InvPage.toInt(a.substring(4), -1);
      if (k < 0 || k >= @PKG@.WorldTabData.FILT.length) { say("No such filter"); return; }
      this.filt = k;
      this.page = 0;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("pg:")) {
      int dp = @PKG@.InvPage.toInt(a.substring(3), 0);
      int np = this.page + (dp < 0 ? -1 : 1);
      if (np < 0 || np >= this.pages) { say(np < 0 ? "This is the first page" : "This is the last page"); return; }
      this.page = np;
      this.tcap = "";
      redraw();
      return;
    }
    String t = @PKG@.InvPage.val(d, "t");
    if (t == null || !t.equals(this.tok)) {
      STALE = STALE + 1;
      this.tcap = "The page changed - here it is again. Nothing happened.";
      redraw();
      return;
    }
    String pk = @PKG@.Given.key(this.playerRef.getUuid());
    if (pk == null ? this.pkey != null : !pk.equals(this.pkey)) {
      this.page = 0;
      this.tcap = "Your profile changed - here is its list. Nothing happened.";
      redraw();
      return;
    }
    if (a.startsWith("go:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || this.keys == null || k >= this.keys.length || this.keys[k] == null) { say("Nothing there"); return; }
      travel(this.keys[k]);
      return;
    }
    if (a.equals("home")) { cmdGo("island"); return; }
    say("Pick a place");
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("world screen event '" + a + "' failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.MenuUtil.warn("world screen: the empty answer failed: " + t2); }
    }
  }
}""")
M(wtab, r"""
public void onDismiss(@REF@ ref, @ST@ st) { finish("dismissed"); }""")
'''
P.rep('''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''', WT_JAVA + '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''')
# Tab while the world screen is open = it closes
P.rep('''  if (sp0 instanceof @PKG@.MarketTab && !((@PKG@.MarketTab) sp0).closed) { ((@PKG@.MarketTab) sp0).shut(); return; }   // 0.3.59
''', '''  if (sp0 instanceof @PKG@.MarketTab && !((@PKG@.MarketTab) sp0).closed) { ((@PKG@.MarketTab) sp0).shut(); return; }   // 0.3.59
  if (sp0 instanceof @PKG@.WorldTab && !((@PKG@.WorldTab) sp0).closed) { ((@PKG@.WorldTab) sp0).shut(); return; }   // 0.3.62
''')
# ---------- the inventory: the World tab opens the world screen
P.rep('''M(ipg, r"""
public void goTab(int i) {''', '''# 0.3.62: the World tab = the world screen (false = it could not open: today's World route below)
M(ipg, r"""
public boolean openWorld() {
  @PKG@.WorldTab wt = null;
  try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "inventory"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("inventory: the world screen failed: " + t); }
  if (wt == null) return false;
  this.answered = true;
  if (!still()) finish("world");
  return true;
}""")
M(ipg, r"""
public void goTab(int i) {''')
P.rep('''  if (i == 3 && openMarket()) return;   // 0.3.59: the market screen (else today's Market route below)
''', '''  if (i == 3 && openMarket()) return;   // 0.3.59: the market screen (else today's Market route below)
  if (i == 4 && openWorld()) return;   // 0.3.62: the world screen (else today's World route below)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.62: no new system / command"
_i = P.s.index
assert _i("public WorldTab(@PR@ pr, String via)") < _i("public static @PKG@.WorldTab open(") < _i("public static @PKG@.MarketTab open(")
assert _i("public static @PKG@.WorldTab open(") < _i("public boolean worldTab()") < _i("try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, \"pets screen\")")
assert _i("try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, \"market screen\")") > _i("public static @PKG@.WorldTab open(")
assert _i("public void shut() { finish(\"closed\"); this.close(); }\"\"\")\nM(wtab") < _i("if (sp0 instanceof @PKG@.WorldTab")
assert _i("public boolean openWorld()") < _i("public void goTab(int i)") and _i('F(wtd, "public static final String LK') < _i("public static @PKG@.WorldTab open(")
assert _i("public static @PKG@.MarketTab open(") < _i('try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "world screen")')
P.finish()


# ======================================================================= the HARNESS (derived from the 0.3.61 harness: every 0.3.61 check
# runs again on the 0.3.62 jar, plus TAB4 on Python stand-ins of the world bridges + the harness' own warps / commands)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.61 (the skill tree inline on every skill page; tools/menu_0_3_61_patch.py, round treemap1).
GENERATED by tools/menu_0_3_61_patch.py from the 0.3.60 harness (edit the patch, not this file): every 0.3.60 check runs again on the
0.3.61 jar''', '''"""Harness for SkyyMenu 0.3.62 (the World tab = one screen; tools/menu_0_3_62_patch.py, round tab4).
GENERATED by tools/menu_0_3_62_patch.py from the 0.3.61 harness (edit the patch, not this file): every 0.3.61 check runs again on the
0.3.62 jar (the market screen's World tab now opens the world screen - still ONE packet), plus
  TAB4 (EXECUTED on Python stand-ins of SkyyIslands island:<uuid> / island:role:fn / island:fn:homes / island:fn:gohome, SkyyEssentials
       essentials:fn:homes / gohome, SkyyExploration explore:<uuid> / explore:fn:title / explore:fn:pct, SkyyQuests quest:fn:hud, SkyyCollections
       coll:fn:catTotal - and the harness' own command manager (/island, /hub) + the engine's warps + Teleport component):
       OPEN    the inventory's / skill page's / pets screen's / market screen's World tab = the WORLD SCREEN (ONE page packet, the old page forgotten)
       FALL    no world mod keys + no /island /hub: every card says "not on this server", the rows greyed without Go; a throwing bridge = the card
               still draws
       PAGE    travel (your island, island homes, homes, hub, warps A-Z, 10 a page, filters, pager, no metadata), the tracked quest (done steps
               green, the bars), your island (role, island homes), explore (level, zones, title, your world's %% + bar), the codex total
       ACT     Go on your island / hub = the /island /hub command (page closed first), an island home = island:fn:gohome (closed first), a home
               = essentials:fn:gohome ("ok" closes, a refusal = the reason, the page stays), a warp = the engine Teleport component + history
               (a warp whose world is not loaded = a caption), Go home on the island card = /island; links = the old pages (ONE packet)
       SAFE    a stale page token / a double click = no teleport; a profile switch between draw and click = said, nothing happens
       TABS    every tab from the screen; the Tab key and X close it
The 0.3.61 harness text follows:
Harness for SkyyMenu 0.3.61 (the skill tree inline on every skill page; tools/menu_0_3_61_patch.py, round treemap1).
GENERATED by tools/menu_0_3_61_patch.py from the 0.3.60 harness (edit the patch, not this file): every 0.3.60 check runs again on the
0.3.61 jar''')
T.rep('VERSION = "0.3.61"\nJAR', 'VERSION = "0.3.62"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.60.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.61.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.60.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.61.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_61_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_62_patch.py")')
T.rep('"scratch", "treemap1", "menu"', '"scratch", "tab4", "menu"')
T.rep('ADDED = []   # 0.3.61: no new class\n', 'ADDED = ["WorldTabData", "WorldTab"]   # 0.3.62: the world screen\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.61:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.62: the World tab opens the world screen (inventory + skill page + pets screen + market screen); Tab closes it
    "InvPage": ["+m openWorld", "~m goTab"],
    "InvState": ["~m tab"],
    "SkillPage": ["+m worldTab", "~m tabGo"],
    "PetsTab": ["~m tabGo"],
    "MarketTab": ["~m tabGo"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.61"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.62"') == 1, "S VERSION")
    # 0.3.62: the world screen fits one 1080p screen, never scrolls, element budget, no new picture
    K.check("0.3.62: the world screen fits one 1080p screen" in g and "0.3.62: the world screen never scrolls" in g
            and "0.3.62: the world screen names only Skyglass pictures the market screen already ships" in g,
            "TAB4 STATIC the build asserts the world screen fits 1080 (both rows sum to the body), has no scrolling list and no new picture")
    mw4_ = re.search(r"WT_ELEMENTS <= (\\d+)", g)
    K.check(mw4_ is not None and int(mw4_.group(1)) <= 800, "TAB4 STATIC the world screen's element budget assert is <= 800 (the ~1,600 client budget)")''')
T.rep('''    for cls_, pfx_ in (("InvData", "SkyyInv"), ("SkillData", "SkyySkp"), ("PetsTabData", "SkyyPtab"), ("MarketTabData", "SkyyMtab")):''',
      '''    for cls_, pfx_ in (("InvData", "SkyyInv"), ("SkillData", "SkyySkp"), ("PetsTabData", "SkyyPtab"), ("MarketTabData", "SkyyMtab"), ("WorldTabData", "SkyyWtab")):''')

T.rep('''not sel_.startswith(("#SkyyInv", "#SkyySkp", "#SkyyPtab", "#SkyyMtab")):''',
      '''not sel_.startswith(("#SkyyInv", "#SkyySkp", "#SkyyPtab", "#SkyyMtab", "#SkyyWtab")):''')   # 0.3.62: + the world screen's travel icons

HARNESS_TAB4 = r'''    # ---- TAB4 (0.3.62; popup 11-14 "Yes, both" on the 7 tabs; Skyy 11-21 "build and deploy everything on your list"): THE WORLD SCREEN
    WTB, WTD = JV("WorldTab"), JV("WorldTabData")
    uk4 = str(PK.pr.getUuid())
    WK4 = ("island:fn:homes", "island:fn:gohome", "island:role:fn", "essentials:fn:homes", "essentials:fn:gohome", "essentials:fn:warps",
           "explore:fn:pct", "explore:fn:title", "quest:fn:hud", "coll:fn:catTotal", "island:" + uk4, "explore:" + uk4, "profile:fn:key")
    for k_ in WK4:
        BR.remove(k_)
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    E.pump(PK)
    CMD4 = {}
    for cn_ in ("island", "hub"):
        CMD4[cn_] = E.CM.cmds.remove(cn_)
    WW = {"ih": [], "zh": [], "zans": "ok", "pct": [], "role": [], "first": None, "qthrow": False}
    wn4 = None
    try:
        wn4 = str(JClass(PH + "server.core.universe.Universe").get().getWorld(PK.pr.getWorldUuid()).getName())
    except Exception:
        wn4 = None

    def lines4():
        return [str(E.CM.lines.get(i_)) for i_ in range(int(E.CM.lines.size()))]

    def w_ev(obj, what, n=1, page=None):
        pg_ = page if page is not None else PK.pm.getCustomPage()
        f_ = len(E.sent(PK))
        pg_.handleDataEvent(PK.ref, PK.st, json.dumps(obj))
        ps_ = pages(PK, f_)
        if n is not None:
            K.eq(len(ps_), n, what + ": exactly %d page packet" % n)
        return ps_[0] if ps_ else None

    def w_open(what):
        if PK.pm.getCustomPage() is not None:
            PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
        E.pump(PK)
        f_ = len(E.sent(PK))
        ws_ = WTB.open(PK.ref, PK.st, PK.pr, "test")
        E.pump(PK)
        ps_ = pages(PK, f_)
        K.check(ws_ is not None and len(ps_) == 1, what + ": WorldTab.open = ONE page packet")
        return ws_, (ps_[0] if ps_ else None)
    vis4 = lambda c_, k_: sval(c_, "#SkyyWtab%s.Visible" % k_) in (True, "true")
    cap4 = lambda p_: str(sval(cmap(p_), "#SkyyWtabCap.Text"))
    names4 = lambda c_: [str(sval(c_, "#SkyyWtabR%dN.Text" % k_)) for k_ in range(int(WTD.TN)) if vis4(c_, "R%d" % k_)]
    # OPEN from the inventory with no world mod at all (no keys, no /island /hub)
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:4"}')
    pk_ = pages(PK, f0_)
    WS = PK.pm.getCustomPage()
    K.check(len(pk_) == 1 and WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab" and bool(pgI_.closed) and ST.PAGES.get(PK.pr.getUuid()) is None,
            "TAB4 OPEN the inventory's World tab = the WORLD SCREEN (ONE page packet), the inventory page forgotten")
    cm = cmap(pk_[0]) if pk_ else {}
    K.notes.append("TAB4 the screen's first packet: %d commands, travel %s" % (len(cmds_of(pk_[0])) if pk_ else 0, names4(cm)))
    K.check(names4(cm)[:2] == ["Your island (not on this server)", "Hub (not on this server)"] and not vis4(cm, "R0Go") and not vis4(cm, "R1Go")
            and names4(cm)[2:] == ["mines", "w1", "w2", "w3", "w4", "w5", "w6"] and vis4(cm, "R2Go") and sval(cm, "#SkyyWtabLt.Text") == "9 places"
            and nometa(pk_[0]), "TAB4 FALL no /island /hub: both rows greyed without Go; the engine's warps A-Z with Go; 9 places; no metadata (%s)" % names4(cm))
    K.check(sval(cm, "#SkyyWtabQt.Text") == "Quests are not on this server right now" and sval(cm, "#SkyyWtabI1.Text") == "Islands are not on this server right now"
            and sval(cm, "#SkyyWtabE1.Text") == "Exploring is not on this server right now" and sval(cm, "#SkyyWtabC1.Text") == "Collections are not on this server right now"
            and not vis4(cm, "Q0") and not vis4(cm, "E0r") and not vis4(cm, "Ihome"),
            "TAB4 FALL no world mod keys: every card says 'not on this server', no quest steps / explore rows / Go home")
    K.check(sval(cm, "#SkyyWtabCap.Text") == str(WTD.CAP0) and str(WTD.ST_CHSEL) in mk_of(pk_[0], "SkyyWtabFc0") and sval(cm, "#SkyyWtabFc3.Text") == "Warps",
            "TAB4 PAGE the caption + the four filter chips (All selected)")
    l0_ = len(lines4())
    p_ = w_ev({"a": "go:0", "t": str(WS.tok)}, "TAB4 FALL Go on the greyed island row")
    K.check(len(lines4()) == l0_ and not bool(WS.closed) and "not on this server" in cap4(p_), "TAB4 FALL the greyed island row = a caption, no command (%s)" % cap4(p_))
    # the world mods arrive
    for cn_ in ("island", "hub"):
        if CMD4[cn_] is not None:
            E.CM.cmds.put(cn_, CMD4[cn_])
    BR.put("island:" + uk4, "isle-" + uk4[:8])

    def f_role(o):
        WW["role"].append([str(x) for x in list(o)])
        return "owner"
    BR.put("island:role:fn", Fn(f_role))
    BR.put("island:fn:homes", Fn(lambda o: _JA(JS)(["Farm", "bad name!", "Farm"])))
    BR.put("essentials:fn:homes", Fn(lambda o: _JA(JS)(["base"])))

    def f_ih(o):
        WW["ih"].append([str(x) for x in list(o)])
        return "+Going to your home 'Farm'."
    BR.put("island:fn:gohome", Fn(f_ih))

    def f_zh(o):
        WW["zh"].append([str(x) for x in list(o)])
        return WW["zans"]
    BR.put("essentials:fn:gohome", Fn(f_zh))
    BR.put("explore:" + uk4, "level:12,zones:7/27,chests:12,chunks:1204,title:wayfarer,spots:3,secrets:1,island:2/5")
    BR.put("explore:fn:title", Fn(lambda o: "Wayfarer"))

    def f_pct(o):
        a_ = [str(x) for x in list(o)]
        WW["pct"].append(a_)
        if WW["first"] is None:
            WW["first"] = a_[1]
        return "73|11|15|Fens Island" if a_[1] == WW["first"] else None
    BR.put("explore:fn:pct", Fn(f_pct))

    def f_qhud(o):
        if WW["qthrow"]:
            raise RuntimeError("quest stand-in throws")
        D_ = JClass("java.lang.Double")
        return OBJ(["Into the Howling Sands", "3 / 24", "Reach the Oasis camp", "", None, "Oasis camp", JClass("java.lang.Integer")(-1), TRUE,
                    "Defeat 10 sand mobs", "6/10", D_(0.6), "Dunes - 340 m", JClass("java.lang.Integer")(2), FALSE])
    BR.put("quest:fn:hud", Fn(f_qhud))
    BR.put("coll:fn:catTotal", Fn(lambda o: JClass("java.lang.Long")(1234) if str(list(o)[1]) == "Combat" else None))
    p_ = w_ev({"a": "flt:0"}, "TAB4 a redraw with every key")
    cm = cmap(p_)
    K.check(names4(cm) == ["Your island", "Farm", "base", "Hub", "mines", "w1", "w2", "w3", "w4", "w5"] and sval(cm, "#SkyyWtabLt.Text") == "11 places"
            and sval(cm, "#SkyyWtabPg.Text") == "Page 1 / 2" and all(vis4(cm, "R%dGo" % k_) for k_ in range(10)),
            "TAB4 PAGE travel: your island, the island home (a bad name + a duplicate left out), the home, the hub, the warps A-Z; 10 a page (%s)" % names4(cm))
    K.check("Island home Farm" in str(sval(cm, "#SkyyWtabR1S.Text")) and "Skyy_Menu_Icon_MyIsland" in cm.get("#SkyyWtabR0I.Slots", "") or "Your island" in cm.get("#SkyyWtabR0I.Slots", ""),
            "TAB4 PAGE a travel card: its icon cell (our icon item when the server knows it, else name + text) and where it goes")
    K.check(sval(cm, "#SkyyWtabQt.Text") == "Into the Howling Sands" and sval(cm, "#SkyyWtabQc.Text") == "Steps 3 / 24" and vis4(cm, "Q0N1") and not vis4(cm, "Q0N0")
            and sval(cm, "#SkyyWtabQ0N1.Text") == "Done - Reach the Oasis camp" and vis4(cm, "Q1N0") and sval(cm, "#SkyyWtabQ1N0.Text") == "Defeat 10 sand mobs   6/10"
            and sval(cm, "#SkyyWtabQ1W.Text") == "Dunes - 340 m" and not vis4(cm, "Q2")
            and ("Width: %d," % int(WTD.BARQ)) in cm.get("#SkyyWtabQ0B", "") and ("Width: %d," % int(0.6 * int(WTD.BARQ))) in cm.get("#SkyyWtabQ1B", ""),
            "TAB4 PAGE quests: the tracked title + steps count, a done step green and full, a step with its progress, where and a 60%% bar, no empty rows")
    K.check(sval(cm, "#SkyyWtabI1.Text") == "Your island" and sval(cm, "#SkyyWtabI2.Text") == "You own this island" and sval(cm, "#SkyyWtabI3.Text") == "1 island home - in Travel (Islands)"
            and vis4(cm, "Ihome") and WW["role"] and WW["role"][-1] == [uk4, "isle-" + uk4[:8]],
            "TAB4 PAGE your island: have one, the role from island:role:fn (your UUID + the island's world), island homes, Go home")
    K.check(sval(cm, "#SkyyWtabEl.Text") == "Exploration Lv 12" and sval(cm, "#SkyyWtabE1.Text") == "Zones found 7 / 27    Chests 12    Spots 3    Secrets 1"
            and sval(cm, "#SkyyWtabE2.Text") == "Title: Wayfarer" and sval(cm, "#SkyyWtabE0N.Text") == "Fens Island" and sval(cm, "#SkyyWtabE0P.Text") == "73%"
            and not vis4(cm, "E1r") and ("Width: %d," % (73 * int(WTD.BARE) // 100)) in cm.get("#SkyyWtabE0B", ""),
            "TAB4 PAGE explore: level, zones / chests / spots / secrets, the title, the world with spots + its 73%% bar")
    K.check(wn4 is None or (WW["pct"] and WW["pct"][0] == [uk4, wn4]), "TAB4 PAGE explore asks YOUR world first (%s / %s)" % (WW["pct"][:1], wn4))
    K.check(sval(cm, "#SkyyWtabC1.Text") == "Mob drops collected: 1,234", "TAB4 PAGE the codex: the Combat collections total")
    K.check("Coins" in str(sval(cm, "#SkyyWtabCoins.Text")) or sval(cm, "#SkyyWtabCoins.Text") == "", "TAB4 PAGE coins in the top bar")
    K.check(not any("Scrolling" in str(c_.text or "") for c_ in cmds_of(p_)), "TAB4 FIT the screen's packet carries no scrolling list")
    # filters + pages (no teleport)
    l0_ = len(lines4())
    p_ = w_ev({"a": "flt:1"}, "TAB4 filter Islands")
    K.check(names4(cmap(p_)) == ["Your island", "Farm"] and str(WTD.ST_CHSEL) in mk_of(p_, "SkyyWtabFc1"), "TAB4 ACT the Islands filter = your island + island homes")
    p_ = w_ev({"a": "flt:2"}, "TAB4 filter Homes")
    K.eq(names4(cmap(p_)), ["base"], "TAB4 ACT the Homes filter")
    p_ = w_ev({"a": "flt:3"}, "TAB4 filter Warps")
    K.eq(names4(cmap(p_)), ["Hub", "mines", "w1", "w2", "w3", "w4", "w5", "w6"], "TAB4 ACT the Warps filter = the hub + the warps")
    p_ = w_ev({"a": "flt:9"}, "TAB4 junk filter")
    K.check("No such filter" in cap4(p_), "TAB4 SAFE an unknown filter = a caption")
    p_ = w_ev({"a": "flt:0"}, "TAB4 All")
    p_ = w_ev({"a": "pg:1"}, "TAB4 next page")
    K.check(names4(cmap(p_)) == ["w6"] and sval(cmap(p_), "#SkyyWtabPg.Text") == "Page 2 / 2", "TAB4 ACT > = page 2")
    p_ = w_ev({"a": "pg:1"}, "TAB4 past the last page")
    K.check("last page" in cap4(p_), "TAB4 ACT past the last page = a caption")
    p_ = w_ev({"a": "pg:-1"}, "TAB4 back")
    K.check(len(lines4()) == l0_ and not WW["ih"] and not WW["zh"], "TAB4 SAFE filters / pages never teleport")
    # SAFE: a stale token, a profile switch
    p_ = w_ev({"a": "go:0", "t": "forged"}, "TAB4 SAFE forged token")
    K.check(len(lines4()) == l0_ and "The page changed" in cap4(p_) and int(WTB.STALE) >= 1 and not bool(WS.closed), "TAB4 SAFE a wrong page token = said + drawn again, no teleport")
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p9"))
    p_ = w_ev({"a": "go:0", "t": str(WS.tok)}, "TAB4 SAFE profile switch")
    K.check(len(lines4()) == l0_ and "Your profile changed" in cap4(p_) and not bool(WS.closed), "TAB4 SAFE a profile switch between draw and click = said, nothing happens")
    BR.remove("profile:fn:key")
    p_ = w_ev({"a": "flt:0"}, "TAB4 redraw on the first profile")
    # ACT: Go on your island = /island (the page closed first); the double click never runs it twice
    old_ = str(WS.tok)
    w_ev({"a": "go:0", "t": old_}, "TAB4 ACT Go on your island", n=None)
    K.check(bool(WS.closed) and lines4()[l0_:] == ["island"] and int(WTB.GOES) >= 1, "TAB4 ACT Go on your island = the /island command as the player, the page closed (%s)" % lines4()[l0_:])
    w_ev({"a": "go:0", "t": old_}, "TAB4 SAFE double click", n=0, page=WS)
    K.check(lines4()[l0_:] == ["island"], "TAB4 SAFE a double click on Go = ONE /island")
    # an island home = island:fn:gohome (closed first)
    WS, p_ = w_open("TAB4 reopen")
    w_ev({"a": "go:1", "t": str(WS.tok)}, "TAB4 ACT island home", n=None)
    K.check(bool(WS.closed) and WW["ih"] == [[uk4, "Farm"]], "TAB4 ACT an island home = island:fn:gohome {your UUID, Farm}, the page closed first (%s)" % WW["ih"])
    # a home = essentials:fn:gohome: ok closes; a refusal stays with the reason; the old drawing after it = stale
    WS, p_ = w_open("TAB4 reopen")
    w_ev({"a": "go:2", "t": str(WS.tok)}, "TAB4 ACT home ok", n=None)
    K.check(bool(WS.closed) and WW["zh"] == [[uk4, "base"]], "TAB4 ACT a home = essentials:fn:gohome {your UUID, base}; 'ok' = the page closes")
    WS, p_ = w_open("TAB4 reopen")
    WW["zans"] = "You must wait 30 s between homes."
    old_ = str(WS.tok)
    p_ = w_ev({"a": "go:2", "t": old_}, "TAB4 ACT home refused")
    K.check(not bool(WS.closed) and "Could not go home: You must wait 30 s between homes." in cap4(p_) and len(WW["zh"]) == 2,
            "TAB4 ACT a refused home = SkyyEssentials' reason, the page stays (its cooldown is its own)")
    p_ = w_ev({"a": "go:2", "t": old_}, "TAB4 SAFE double click on a refused home")
    K.check(len(WW["zh"]) == 2 and "The page changed" in cap4(p_), "TAB4 SAFE the second click of a double click = stale, no second call")
    WW["zans"] = "ok"
    # the hub = /hub; a warp whose world is not loaded = a caption; a warp in a loaded world = the engine Teleport component
    l1_ = len(lines4())
    p_ = w_ev({"a": "flt:3"}, "TAB4 Warps")
    p_ = w_ev({"a": "go:1", "t": str(WS.tok)}, "TAB4 ACT a warp in a world that is not loaded")
    K.check(not bool(WS.closed) and "is not loaded" in cap4(p_), "TAB4 ACT a warp whose world is not loaded = a caption, the page stays (%s)" % cap4(p_))
    w_ev({"a": "go:0", "t": str(WS.tok)}, "TAB4 ACT the hub", n=None)
    K.check(bool(WS.closed) and lines4()[l1_:] == ["hub"], "TAB4 ACT Go on the hub = the /hub command, the page closed")
    TRc_ = [c_ for c_ in WARPc.class_.getDeclaredConstructors() if len(c_.getParameterTypes()) == 5]
    w4_ = None
    if TRc_:
        try:
            tr_ = JClass(str(TRc_[0].getParameterTypes()[0].getName()))()
            w4_ = WARPc(tr_, "harbor", E.W1, "Skyy", JClass("java.time.Instant").now())
        except Exception as x_:
            K.notes.append("TAB4 a loaded-world warp could not be made: %s" % x_)
    if w4_ is not None:
        WARPS.put("harbor", w4_)
        UNI4_ = JClass(PH + "server.core.universe.Universe")
        UW4_ = E.jf(UNI4_.class_, "worlds").get(UNI4_.get())
        UW4_.put("harness_home", E.W1)   # the harness Universe's by-name map (getWorld(String)) - a loaded world for this warp
        # a player whose store takes addComponent off the world thread (the harness store's row; the engine Store asserts its thread)
        CP4_ = JClass("javassist.ClassPool").getDefault()
        ts_ = CP4_.makeClass("skyymenu62.TpStore", CP4_.get(PH + "component.SkyyMenu19Store"))
        ts_.addConstructor(JClass("javassist.CtNewConstructor").make("public TpStore() { super(); }", ts_))
        ts_.addMethod(JClass("javassist.CtNewMethod").make("public void addComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t, "
                                                           + PH + "component.Component c) { row(r).put(t, c); }", ts_))
        ts_.writeFile(hcls)
        PW4 = E.player(uid=UUIDc(0x62, 0x62), name="SkyyWarpW")
        STO4_ = JClass(PH + "component.Store")
        st4_ = Ucls.allocateInstance(JClass("skyymenu62.TpStore").class_)
        st4_.row(PW4.ref).putAll(PW4.st.row(PW4.ref))
        E.jf(PW4.ref.getClass(), "store").set(PW4.ref, st4_)
        E.jf(STO4_.class_, "externalData").set(st4_, E.jf(STO4_.class_, "externalData").get(PW4.st))
        PW4.st = st4_
        byU.put(PW4.pr.getUuid(), PW4.pr)
        TPc_ = JClass(PH + "server.core.modules.entity.teleport.Teleport")

        def w4_ev(pg_, obj):
            E.pump(PW4)
            f_ = len(E.sent(PW4))
            pg_.handleDataEvent(PW4.ref, st4_, json.dumps(obj))
            ps_ = pages(PW4, f_)
            return ps_[0] if ps_ else None
        WS4 = WTB.open(PW4.ref, st4_, PW4.pr, "test")
        E.pump(PW4)
        p_ = w4_ev(WS4, {"a": "flt:3"})
        K.check(p_ is not None and names4(cmap(p_))[1] == "harbor", "TAB4 PAGE a new warp is listed A-Z (%s)" % (names4(cmap(p_)) if p_ is not None else None))
        K.check(st4_.getComponent(PW4.ref, TPc_.getComponentType()) is None, "TAB4 ACT (setup) not teleporting yet")
        p_ = w4_ev(WS4, {"a": "go:1", "t": str(WS4.tok)})
        tp4_ = st4_.getComponent(PW4.ref, TPc_.getComponentType())
        IDH4 = JClass("java.lang.System").identityHashCode
        same4 = lambda: tp4_ is not None and IDH4(st4_.getComponent(PW4.ref, TPc_.getComponentType())) == IDH4(tp4_)
        K.check(bool(WS4.closed) and tp4_ is not None and int(WTB.GOES) >= 1,
                "TAB4 ACT Go on a warp in a loaded world = the engine Teleport component on the player (InvPage.warpGo's calls), the page closed (%s)"
                % (cap4(p_) if p_ is not None else "no page packet"))
        p_ = w4_ev(WS4, {"a": "go:1", "t": str(WS4.tok)})
        K.check(p_ is None and same4(), "TAB4 SAFE a double click on a warp = ONE teleport (the page is closed)")
        WS4 = WTB.open(PW4.ref, st4_, PW4.pr, "test")
        E.pump(PW4)
        p_ = w4_ev(WS4, {"a": "flt:3"})
        p_ = w4_ev(WS4, {"a": "go:1", "t": str(WS4.tok)})
        K.check(p_ is not None and not bool(WS4.closed) and "already teleporting" in cap4(p_) and same4(),
                "TAB4 SAFE a warp while a teleport is pending = a caption, no second teleport (%s)" % (cap4(p_) if p_ is not None else "no packet"))
        WS4.handleDataEvent(PW4.ref, st4_, '{"a":"close"}')
        st4_.row(PW4.ref).remove(TPc_.getComponentType())
        WARPS.remove("harbor")
        UW4_.remove("harness_home")
        byU.remove(PW4.pr.getUuid())
    # Go home on the island card = /island
    WS, p_ = w_open("TAB4 reopen")
    l2_ = len(lines4())
    w_ev({"a": "home", "t": str(WS.tok)}, "TAB4 ACT Go home", n=None)
    K.check(bool(WS.closed) and lines4()[l2_:] == ["island"], "TAB4 ACT the island card's Go home = /island, the page closed")
    # a bridge gone / throwing: said, the page still draws
    WS, p_ = w_open("TAB4 reopen")
    BR.remove("island:fn:gohome")
    p_ = w_ev({"a": "go:1", "t": str(WS.tok)}, "TAB4 FALL island home without the bridge")
    K.check(not bool(WS.closed) and "Island homes are not on this server" in cap4(p_), "TAB4 FALL an island home without island:fn:gohome = a caption")
    BR.put("island:fn:gohome", Fn(f_ih))
    WW["qthrow"] = True
    p_ = w_ev({"a": "flt:0"}, "TAB4 FALL a throwing quest bridge")
    K.check(sval(cmap(p_), "#SkyyWtabQt.Text") == "No quest to show right now" and sval(cmap(p_), "#SkyyWtabC1.Text") == "Mob drops collected: 1,234",
            "TAB4 FALL a throwing quest:fn:hud = 'No quest to show', the rest of the page still draws")
    WW["qthrow"] = False
    # links to the old pages (each ONE packet)
    for a_, what in (("full", "Full page"), ("isl", "Island settings"), ("exp", "Explore page"), ("qlog", "Quest log"), ("coll", "Collections")):
        WS, p_ = w_open("TAB4 reopen for " + what)
        f0_ = len(E.sent(PK))
        WS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": a_}))
        cur_ = PK.pm.getCustomPage()
        K.check(len(pages(PK, f0_)) == 1, "TAB4 LINK %s = the old page's route, ONE packet (%s)" % (what, None if cur_ is None else cur_.getClass().getSimpleName()))
    # TABS
    WS, p_ = w_open("TAB4 reopen for tabs")
    p_ = w_ev({"a": "tab:4"}, "TAB4 TABS World")
    K.eq(cap4(p_), "You are on World", "TAB4 TABS World = a caption")
    p_ = w_ev({"a": "tab:1"}, "TAB4 TABS Skills")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and bool(WS.closed), "TAB4 TABS Skills = the skill page")
    p_ = w_ev({"a": "tab:4"}, "TAB4 OPEN the skill page's World tab")
    WS = PK.pm.getCustomPage()
    K.check(WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab", "TAB4 OPEN the skill page's World tab = the world screen")
    p_ = w_ev({"a": "tab:0"}, "TAB4 TABS Inventory")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "c", "TAB4 TABS Inventory = the inventory screen")
    BR.put("pets:fn:tab", Fn(f_tab))
    BR.put("pets:fn:tabact", Fn(f_act))
    p_ = one(ev(PK, {"a": "pet"}), "TAB4 the pets screen")
    PS4 = PK.pm.getCustomPage()
    p_ = w_ev({"a": "tab:4"}, "TAB4 OPEN the pets screen's World tab")
    WS = PK.pm.getCustomPage()
    K.check(str(PS4.getClass().getSimpleName()) == "PetsTab" and WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab" and bool(PS4.closed),
            "TAB4 OPEN the pets screen's World tab = the world screen")
    p_ = w_ev({"a": "tab:2"}, "TAB4 TABS Pets")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "PetsTab", "TAB4 TABS Pets = the pets screen")
    for k_ in ("pets:fn:tab", "pets:fn:tabact"):
        BR.remove(k_)
    BR.put("bazaar:fn:tab", Fn(f_btab))
    BR.put("bazaar:fn:tabact", Fn(f_bact))
    WS, p_ = w_open("TAB4 reopen for Market")
    p_ = w_ev({"a": "tab:3"}, "TAB4 TABS Market")
    MS4 = PK.pm.getCustomPage()
    K.check(MS4 is not None and str(MS4.getClass().getSimpleName()) == "MarketTab" and bool(WS.closed), "TAB4 TABS Market = the market screen")
    p_ = w_ev({"a": "tab:4"}, "TAB4 OPEN the market screen's World tab")
    WS = PK.pm.getCustomPage()
    K.check(WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab" and bool(MS4.closed), "TAB4 OPEN the market screen's World tab = the world screen")
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact"):
        BR.remove(k_)
    p_ = w_ev({"a": "tab:6"}, "TAB4 TABS Settings")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(WS.closed), "TAB4 TABS Settings = our Settings page")
    WS, p_ = w_open("TAB4 reopen for Social")
    f0_ = len(E.sent(PK))
    WS.handleDataEvent(PK.ref, PK.st, '{"a":"tab:5"}')
    K.check(len(pages(PK, f0_)) == 1, "TAB4 TABS Social = today's route, ONE packet")
    WS, p_ = w_open("TAB4 reopen for the Tab key")
    ST.tab(PK.ref, PK.st, PK.pr, PK.pl, "test")
    K.check(PK.pm.getCustomPage() is None and bool(WS.closed), "TAB4 TABS the Tab key closes the world screen")
    WS, p_ = w_open("TAB4 reopen for X")
    WS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(PK.pm.getCustomPage() is None and bool(WS.closed), "TAB4 TABS X closes the screen")
    K.notes.append("TAB4 counters: opens %d, stale %d, teleports %d, commands %s, island homes %d, homes %d, pct asks %d"
                   % (int(WTB.OPENS), int(WTB.STALE), int(WTB.GOES), lines4()[l0_:], len(WW["ih"]), len(WW["zh"]), len(WW["pct"])))
    for k_ in WK4:
        BR.remove(k_)
    E.pump(PK)
'''
T.rep('''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
''', HARNESS_TAB4 + '''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
''')
if T.dst:
    T.finish()
