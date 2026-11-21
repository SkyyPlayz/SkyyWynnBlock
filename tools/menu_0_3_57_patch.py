"""Derive SkyyMenu/build_skyymenu_0.3.57.py + SkyyMenu/test_skyymenu_0.3.57.py from the SET pin SkyyMenu 0.3.56 (generated - never re-run
its patch). Run:  python tools/menu_0_3_57_patch.py   then   python SkyyMenu/build_skyymenu_0.3.57.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.57.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.56 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.57 (2026-11-21, round tab1) = TAB SCREENS ROUND 1: THE SKILLS TAB - ONE PAGE PER SKILL (Mining first, the same template for every skill).
Skyy's words: 11-21 "game is closed, deploy as ready. i might be able to test later. build and deploy everything on your list"; 11-14 on
skill-page-mining.png "perfect!"; 11-14 "clicking any button in the top bar of the inventory takes me to the old system, we are going to need a
full ui redesign ..."; on the Skills card "class is combat."; on skill-page-mining.png "show the alloys too." (docs/answered/ui.md 2026-11-14 +
world.md "SKILL PAGE ALLOYS"). Approved art: research/ui-theme-art/skill-page-mining.png + skill-page-mining-locked.png + tab-plan.png (README
defaults). SURVEY: vanilla has no skill page (the vanilla inventory has none); no pack mod draws one - this page reads OUR mods' bridges only.
  1. THE SKILLS TAB of the inventory's top bar (and a click on a skill icon in the inventory's Skills panel) opens the new SKILL PAGE
     (SkillPage: an inline Skyglass page, kit tools/skyyui.py, the inventory's frame + the same 7-tab top bar with Skills selected) instead
     of the old Character > Skills list. One page per skill, the approved layout:
     LEFT   YOUR STATS - the Stats page's own rows (StatsCalc, read only): the skill's rows first (Mining Fortune / Wisdom ...; Combat = the
            Combat tab rows), then the general rows; a line saying whether the skill's Requip preset is worn now.
     MIDDLE HEADER (icon, name, LEVEL box, the XP bar into / needed, NEXT UNLOCK = the next path tier or the shard at Lv 10);
            GEAR (the TOOL card: the preset's tool for this skill - or the one in your hotbar - with its tier tag + Upgrade; the ARMOUR 4
            slots of the skill's Requip preset - or what you wear - with on-you / missing marks; Requip = the inventory's Requip panel on
            THIS preset; Charms = the inventory's Charms panel);
            COLLECTIONS - PATH BY ZONE (Mining: the full 16-metal ladder of tools/tier_tags.py LADDER by zone WITH the 5 alloys - Bronze,
            Dusk, Azurvane, Cinder, Lumen - marked "alloy", their parents = the zone's two metals; Onyxium = LATER; Foraging = the 15 log
            tiers, Farming = the 15 crop tiers, 3 a zone): each tier = icon (known(id) guard, a NEW ItemStack(id, 1)) + name + "Lv N" + the
            collection count (coll:fn:count / coll:fn:tier, read only); a zone above your level is drawn LOCKED (red zone title, greyed icons,
            "locked") like skill-page-mining-locked.png; click a tier = the SELECTED line; the NEXT TIER line. Skills without a path say so;
            SKILL TREE: tree:<uuid> points (free / spent of total) for this skill's tree (Combat = the Class tree) + the PERKS NOW lines
            (the Stats page's own breakdown notes of this skill's rows) + Open tree (/tree <name>); on the COMBAT page the ABILITIES
            line (Skyy 11-14: "the COMBAT skill page holds your class (abilities, class tree, combat gear)"): the 4 ability slots' names +
            state from SkyyClasses class:fn:abil (read only - the HUD's own reader), or what is missing.
     FIT    one 1080p screen, nothing scrolls (Skyy "no zooming or scrolling"): the build asserts the root = the kit's MAX_PAGE_H / W,
            every column adds up to the body exactly, no Scrolling layout anywhere; the harness checks no page packet carries one.
     RIGHT  SKILLS grid (12 cells: Combat = your class skill - Skyy "class is combat." -, Mining, Foraging, Farming, Fishing, Smithing,
            Alchemy, Cooking, Acrobatics, Exploration, Ranching, Orchard; icon + Lv + XP bar, the shown one highlighted; click = its page);
            the SHARD card (Combat / Mining / Foraging / Farming): locked below the skill's Lv 10 (Skyy "lets lock it to lvl 10") with the
            level progress, open from Lv 10 - its button takes you to your island (today's shard entry is the portal there; the clicker game
            itself is round forage1). No shard bridge exists yet, so the card shows no stored counts (UNVERIFIED / next round).
  2. The other top-bar tabs keep opening today's pages (Pets, Market, World, Social, Settings) - no dead buttons; on the skill page the
     Inventory tab opens the inventory screen again.
  3. The Mods list no longer mentions a coin death penalty (no death penalty since SkyyCoins 0.1.12): the SkyyCoins note + description +
     the /deathpenalty line and the SkyyBank "never lost when you die" sentence; the description says "By default you keep your coins when
     you die." (the Coins Death rows can still be turned back on by an owner - fix after the tab1 critic).
  Every bound click answers with exactly ONE page packet (a redraw, a caption, a page that replaces this one, or the close); every grid copy is
  a NEW ItemStack(id, 1) without metadata behind known(id); no Top / Bottom alignment; inline page only; never setPageWithWindows.
  NOT BUILT (next rounds, nothing half-wired): the shard card's stored items / spirits (needs a read-only shard bridge in SkyyShards - round
  forage1 owns that mod); "stats WITH the set on" when the preset is not worn (needs a what-if stats bridge in SkyyGear - the page says
  whether the preset is worn instead); the collection's progress bar to the next tier (coll:fn:count / tier give no threshold); the charm
  row + its Upgrade on the page (the Charms button opens the inventory's Charms panel); the scaled-up tree drawing (Open tree opens it);
  the shard clicker itself (the shard button runs /island - a stand-in until round forage1's clicker; the Lv 10 lock is on this card only);
  real shard art (the card shows the skill's icon); the Combat abilities' details / cooldown bars (the line shows names + state only).
  ASSUMED (Skyy may correct): the path levels = the tools/tier_tags.py ladder bands (3 tiers a zone at the zone's base level +0 / +8 / +15).
  New classes SkillData + SkillPage; no command, no setting, no lang key, no system, no saved data.
  ROLLBACK to 0.3.56: safe alone (nothing saved; the Skills tab opens the old Character > Skills list again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.56.py"), os.path.join(MOD, "build_skyymenu_0.3.57.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.56.py"), os.path.join(MOD, "test_skyymenu_0.3.57.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.56"\n') and P.has("tools/menu_0_3_56_patch.py") and P.has("fillFurn")
assert not P.has("SkillPage"), "not the generated SkyyMenu 0.3.56 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.56: THE FURNACE / TANNING PANEL''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.57: THE SKILLS TAB = ONE PAGE PER SKILL (SkillPage: stats, header + XP, tool + armour + Requip, the path by zone with alloys and locked
       zones, tree points + perks, the 12-skill grid, the shard card) + the Mods list without the old coin death penalty
       (notes: tools/menu_0_3_57_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.57.py.
0.3.56: THE FURNACE / TANNING PANEL''')
P.rep('VERSION = "0.3.56"\n', 'VERSION = "0.3.57"\n')

# ---------- (3) the Mods list: no coin death penalty since SkyyCoins 0.1.12
P.rep('''"desc": "A SkyBlock-style bank next to your coin purse: deposit coins to earn interest and withdraw them any time. Bank coins are never lost when you die.",''',
      '''"desc": "A SkyBlock-style bank next to your coin purse: deposit coins to earn interest and withdraw them any time.",''')
P.rep('''     "config": "Skyy_SkyyCoins/config.properties", "reload": "", "note": "Change the death penalty in chat with /deathpenalty - saved at once.",
     "desc": "The server's coins. Check your balance and pay other players. When you die you lose a set share of the coins in your purse (bank coins are safe).",
     "commands": ["/balance (or /bal, /coins, /purse) - your coins", "/pay <player> <amount> - send coins to a player",
                  "/coinsgive <amount> - (admin) give yourself coins", "/deathpenalty 5% or 5%-10% - (admin) coins lost on death"]},''',
      '''     "config": "Skyy_SkyyCoins/config.properties", "reload": "", "note": "",
     "desc": "The server's coins. Check your balance and pay other players. By default you keep your coins when you die.",
     "commands": ["/balance (or /bal, /coins, /purse) - your coins", "/pay <player> <amount> - send coins to a player",
                  "/coinsgive <amount> - (admin) give yourself coins"]},''')

# ---------- (1) the SKILL PAGE markup (built like the inventory page: one page data list drawn by SkillPage.build)
SK_PAGE = r'''
# ================= 0.3.57 THE SKILLS TAB: ONE PAGE PER SKILL (tools/menu_0_3_57_patch.py; approved art research/ui-theme-art/skill-page-mining.png
# + skill-page-mining-locked.png; Skyy 11-14 "perfect!", "show the alloys too.", "class is combat.") =================
# The inventory's frame and top bar (Skills selected); LEFT your stats | MIDDLE header + XP, tool + armour, the path by zone, the tree |
# RIGHT the 12-skill grid + the shard card. Static markup = SkillData.LK / LP / LB (like InvData), the rest b.set / run-time appends.
import tier_tags as _TT57
SK = "SkyySkp"
SK_L, SK_R = 356, 372
SK_M = IV_IW - SK_L - SK_R - 2 * IV_GAP                    # 808
SK_HD_H, SK_GR_H, SK_PA_H = 104, 132, 266
SK_TR_H = IV_BODY_H - SK_HD_H - SK_GR_H - SK_PA_H - 3 * 8
SK_STN, SK_TRN, SK_GN, SK_ZN, SK_ZK = 27, 8, 12, 6, 3
SK_MI = SK_M - 20                                          # the middle panels' inner width
SK_ZW = (SK_MI - (SK_ZN - 1) * 6) // SK_ZN                 # a zone box
SK_ZS, SK_ZI = 40, 32
SK_ZTW = SK_ZW - 8 - SK_ZS - 2                             # a zone box's text column
SK_ZB_H = 8 + 18 + 16 + 4 + SK_ZK * SK_ZS + (SK_ZK - 1) * SUI.GRID_SPACING
SK_RI = SK_R - 20                                          # the right panels' inner width
SK_CW = (SK_RI - 6) // 2                                   # a skill cell
SK_CBW = SK_CW - 12 - 44 - 6                               # its text column
SK_SHBW = SK_RI - 20
SK_HDBW = SK_MI - 72 - 12 - 300 - 8 - 84 - 12              # the header's XP bar
# the 12 skills in grid order: (label, tool id prefixes, tree name (Combat = the class tree), has a shard card)
SK_SKILLS = [("Combat", "Weapon_", "Class", True), ("Mining", "Tool_Pickaxe_", "Mining", True), ("Foraging", "Tool_Hatchet_", "Foraging", True),
             ("Farming", "Tool_Sickle_,Tool_Hoe_,Tool_WaterCan_", "Farming", True), ("Fishing", "SkyyFishing_Rod_", "Fishing", False),
             ("Smithing", "Tool_Hammer_", "Smithing", False), ("Alchemy", "", "Alchemy", False), ("Cooking", "", "Cooking", False),
             ("Acrobatics", "", "Acrobatics", False), ("Exploration", "", "Exploration", False), ("Ranching", "Tool_Shears_", "Ranching", False),
             ("Orchard", "", "Orchard", False)]
assert len(SK_SKILLS) == SK_GN and SK_SKILLS[0][0] == "Combat" and SK_SKILLS[1][0] == "Mining", "0.3.57: Combat (= your class) first, Mining next"
SK_SHARD_LV = 10                                           # Skyy 11-14: "lets lock it to lvl 10"
SK_TXT = {
    "sub": "Gear, collections, tree and shard in one page",
    "foot": "Your stats now. The Stats page shows every source.",
    "nopath": "No zone path for this skill yet. Its collections are on the Collections page.",
    "alloy": "ALLOY = smelted from the zone's two metals; only base metals have collections.",
}


def _sk_path():
    """(skill, item id, name, level, zone 1-5 / 6 = later, collection id or "", alloy, tier tag, parents) - the approved path by zone
    (tools/tier_tags.py: LADDER + METAL_BANDS for Mining, LOGS for Foraging, CROP_LADDER for Farming; 3 tiers a zone)"""
    out = []
    alloys = ("Bronze", "Dusk", "Azurvane", "Cinder", "Lumen")
    for i_, m_ in enumerate(_TT57.LADDER):
        t_ = i_ + 1
        z_ = (i_ // 3) + 1 if t_ <= 15 else 6
        bid = "Ingredient_Bar_%s" % m_ if ("Ingredient_Bar_%s" % m_) in _TT57.ROWS else "Ingredient_Bar_%s_SkyWynn" % m_
        assert bid in _TT57.ROWS, bid
        al = m_ in alloys
        par = " + ".join(_TT57.LADDER[(z_ - 1) * 3 + k_] for k_ in range(3) if _TT57.LADDER[(z_ - 1) * 3 + k_] != m_) if al else ""
        out.append(("Mining", bid, m_, _TT57.METAL_BANDS[m_][0], z_, "" if al else m_, al, _TT57.tag_for(bid), par))
    for t_ in range(1, 16):
        w_ = _TT57.LOGS[t_][0]
        lid = "Wood_%s_Trunk" % w_
        out.append(("Foraging", lid, w_.replace("_", " "), _TT57.METAL_BANDS[_TT57.LADDER[t_ - 1]][0], (t_ - 1) // 3 + 1, w_.replace("_", "") + "Log", False,
                    _TT57.tag_for(lid), ""))
    for t_ in range(1, 16):
        c_ = _TT57.CROP_LADDER[t_ - 1]
        cid = "Plant_Crop_%s_Item" % c_ if c_ != "Mushroom" else "Plant_Crop_Mushroom_Cap_Brown"
        out.append(("Farming", cid, c_, _TT57.METAL_BANDS[_TT57.LADDER[t_ - 1]][0], (t_ - 1) // 3 + 1, c_, False, _TT57.tag_for(cid), ""))
    return out
SK_PATH = _sk_path()
assert [r_[2] for r_ in SK_PATH if r_[0] == "Mining" and r_[6]] == ["Bronze", "Dusk", "Azurvane", "Cinder", "Lumen"], "0.3.57: the 5 alloys on the Mining path"
assert [(r_[2], r_[3], r_[4]) for r_ in SK_PATH if r_[0] == "Mining"][:3] == [("Copper", 1, 1), ("Iron", 8, 1), ("Bronze", 15, 1)] and SK_PATH[15][2:5] == ("Onyxium", 100, 6)
assert [r_[8] for r_ in SK_PATH if r_[2] == "Bronze"] == ["Copper + Iron"] and [r_[8] for r_ in SK_PATH if r_[2] == "Lumen"] == ["Mithril + Titanium"]
for _s in ("Mining", "Foraging", "Farming"):
    for _z in range(1, 7):
        assert len([r_ for r_ in SK_PATH if r_[0] == _s and r_[4] == _z]) <= SK_ZK, ("0.3.57: a zone box holds 3 tiers", _s, _z)
    _lv = [r_[3] for r_ in SK_PATH if r_[0] == _s]
    assert _lv == sorted(_lv), ("0.3.57: a path climbs by level", _s)
for _r in SK_PATH:
    assert all(32 <= ord(c_) < 127 and c_ not in '"\\|' for c_ in "".join(str(x_) for x_ in _r)), _r
    assert SUI.text_width(_r[2], 12, bold=True) <= SK_ZTW, ("0.3.57: a path name fits its zone box", _r[2], SK_ZTW)
print("0.3.57 skill pages: %d path tiers (Mining %d with %d alloys, Foraging %d, Farming %d)" % (len(SK_PATH), len([1 for r_ in SK_PATH if r_[0] == "Mining"]),
      len([1 for r_ in SK_PATH if r_[6]]), len([1 for r_ in SK_PATH if r_[0] == "Foraging"]), len([1 for r_ in SK_PATH if r_[0] == "Farming"])))
# the run-time markup: a skill cell (appended into #SkyySkpGr<row>, the shown one in the selected tab look), the XP bar fills
SK_ST_CB, SK_ST_CBSEL = SUI.glass_button_style("tab", 13), SUI.glass_button_style("tabSelected", 13)
_cell = SUI.glass_group(SK + "C7777", SK_CW, 58, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"right": 8888, "bottom": 6},
                        inner=SUI.glass_grid(SK + "Ci7777", 1, 1, drag=False, slot=44, icon=36, anchor={"top": 7}) + " " +
                        SUI.glass_group(SK + "Cx7777", SK_CBW, 58, layout="Top", anchor={"left": 6},
                                        inner=SUI.glass_button(SK + "Cb7777", "", "tab", w=SK_CBW, h=26, size=13, anchor={"top": 4}) + " " +
                                        SUI.glass_label(SK + "Cl7777", "", 12, "xp", bold=True, w=SK_CBW, h=18) + " " +
                                        'Group #%sCt7777 { Anchor: (Width: %d, Height: 6); LayoutMode: Left; Background: %s; }' % (SK, SK_CBW - 6, IV_TRACK)))
SUI.check_markup(_cell.replace("8888", "6"), prefix=SK, kit_paths=True)
assert _cell.count(SUI.glass_bg("inset")) == 1 and _cell.count(SK_ST_CB) == 1, "0.3.57: the cell's background + button style are swappable"
SK_CELL = _cell.replace("7777", "{I}").replace("8888", "{R}").replace(SUI.glass_bg("inset"), "{BG}").replace(SK_ST_CB, "{S}")
SK_BG_CELL, SK_BG_SEL = SUI.glass_bg("inset"), SUI.glass_bg("tabSelected")
SK_FILL10 = "Group { Anchor: (Width: {W}, Height: 10); Background: %s; }" % SUI.glass_col("xp")
SK_FILL8 = "Group { Anchor: (Width: {W}, Height: 8); Background: %s; }" % SUI.glass_col("green")
for _mk in (SK_CELL.replace("{I}", "0").replace("{R}", "6").replace("{BG}", SK_BG_SEL).replace("{S}", SK_ST_CBSEL), SK_FILL10.replace("{W}", "40"),
            SK_FILL8.replace("{W}", "40"), IV_FILL.replace("{W}", "40")):
    SUI.check_markup(_mk, prefix=SK, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.57: a run-time markup line Java can hold"
for _l, _p, _t, _s in SK_SKILLS:
    assert SUI.text_width(_l, 13, bold=True) <= SK_CBW - 10, ("0.3.57: a skill name fits its cell button", _l)
for _k, _v in SK_TXT.items():
    assert all(32 <= ord(c_) < 127 for c_ in _v) and '"' not in _v and "\\" not in _v, "0.3.57: plain text: " + _k


def _sk_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (SK, IV_PAGE_W, IV_PAGE_H)))
    win = SK + "Win"
    ap.append(("#" + SK, G_.glass_group(win, IV_W, IV_WIN_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": (IV_PAGE_H - IV_WIN_H) // 2})))
    # ---- row 1: the same 7 tabs as the inventory (Skills selected), coins, the X
    top = SK + "Top"
    ap.append(("#" + win, G_.glass_group(top, IV_IW, IV_TOP_H, layout="Left")))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (SK, i), lb, "tabSelected" if i == 1 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - IV_COIN_W - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, lab(SK + "Coins", "", 15, "xp", bold=True, w=IV_COIN_W, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(SK + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    ap.append(("#" + win, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }' % (SK, IV_IW, G_.glass_path("Separator"))))
    body = SK + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Left")))
    # ======== LEFT: YOUR STATS
    st = SK + "St"
    ap.append(("#" + body, G_.glass_group(st, SK_L, IV_BODY_H, role="panel", layout="Top", pad=12)))
    liw = SK_L - 24
    ap.append(("#" + st, lab(SK + "StH", "YOUR STATS", 16, "accentHi", bold=True, w=liw, h=26)))
    ap.append(("#" + st, lab(SK + "StW", "", 13, "dim", w=liw, h=20)))
    for k_ in range(SK_STN):
        rw = SK + "Sr%d" % k_
        ap.append(("#" + st, G_.glass_group(rw, liw, 24, layout="Left", anchor={"top": 6} if k_ == 0 else None)))
        ap.append(("#" + rw, lab(SK + "Sn%d" % k_, "", 14, "row", w=214, h=24)))
        ap.append(("#" + rw, lab(SK + "Sv%d" % k_, "", 14, "title", bold=True, w=liw - 214, h=24, halign="End")))
    ap.append(("#" + st, lab(SK + "StF", "", 12, "dim", w=liw, h=36, anchor={"top": 8})))
    ap.sets.append((SK + "StF", "Text", SK_TXT["foot"]))
    assert 26 + 20 + 6 + SK_STN * 24 + 8 + 36 <= IV_BODY_H - 24, "0.3.57: the stats column fits"
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== MIDDLE
    md = SK + "Mid"
    ap.append(("#" + body, G_.glass_group(md, SK_M, IV_BODY_H, layout="Top")))
    # A) the HEADER: icon, name, LEVEL box, XP bar, NEXT UNLOCK
    hd = SK + "Hd"
    ap.append(("#" + md, G_.glass_group(hd, SK_M, SK_HD_H, role="panel", layout="Left", pad=10)))
    ap.append(("#" + hd, G_.glass_grid(SK + "HdI", 1, 1, drag=False, slot=72, icon=60, anchor={"top": 6})))
    hn = SK + "HdN"
    ap.append(("#" + hd, G_.glass_group(hn, 300, 84, layout="Top", anchor={"left": 12})))
    ap.append(("#" + hn, lab(SK + "HdT", "", 26, "title", bold=True, w=300, h=40)))
    ap.append(("#" + hn, lab(SK + "HdS", "", 13, "dim", w=300, h=22)))
    ap.sets.append((SK + "HdS", "Text", SK_TXT["sub"]))
    ap.append(("#" + hn, lab(SK + "HdC", "", 13, "gold", bold=True, w=300, h=20)))
    hl = SK + "HdL"
    ap.append(("#" + hd, G_.glass_group(hl, 84, 84, role="inset", layout="Top", anchor={"left": 8})))
    ap.append(("#" + hl, lab(None, "LEVEL", 11, "dim", bold=True, w=84, h=24, halign="Center", anchor={"top": 4})))
    ap.append(("#" + hl, lab(SK + "HdLv", "", 30, "xp", bold=True, w=84, h=50, halign="Center")))
    hx = SK + "HdX"
    ap.append(("#" + hd, G_.glass_group(hx, SK_HDBW, 84, layout="Top", anchor={"left": 12})))
    hxr = SK + "HdXr"
    ap.append(("#" + hx, G_.glass_group(hxr, SK_HDBW, 22, layout="Left")))
    ap.append(("#" + hxr, lab(SK + "HdXa", "", 13, "text", bold=True, w=SK_HDBW // 2, h=22)))
    ap.append(("#" + hxr, lab(SK + "HdXn", "", 13, "xp", w=SK_HDBW - SK_HDBW // 2, h=22, halign="End")))
    ap.append(("#" + hx, 'Group #%sHdB { Anchor: (Width: %d, Height: 10, Top: 4); LayoutMode: Left; Background: %s; }' % (SK, SK_HDBW, IV_TRACK)))
    ap.append(("#" + hx, lab(SK + "HdU", "NEXT UNLOCK", 12, "action", bold=True, w=SK_HDBW, h=18, anchor={"top": 8})))
    ap.append(("#" + hx, lab(SK + "HdU1", "", 12, "text", w=SK_HDBW, h=18)))
    assert SK_HDBW >= 260 and 72 + 12 + 300 + 8 + 84 + 12 + SK_HDBW <= SK_MI, ("0.3.57: the header fits", SK_HDBW)
    # B) GEAR: the tool card, the armour of the skill's preset, Requip + Charms
    gr = SK + "Gr"
    ap.append(("#" + md, G_.glass_group(gr, SK_M, SK_GR_H, role="panel", layout="Left", pad=10, anchor={"top": 8})))
    gt = SK + "Gt"
    ap.append(("#" + gr, G_.glass_group(gt, 250, 112, layout="Top")))
    ap.append(("#" + gt, lab(None, "TOOL", 12, "dim", bold=True, w=250, h=18)))
    gtr = SK + "Gtr"
    ap.append(("#" + gt, G_.glass_group(gtr, 250, 64, layout="Left")))
    ap.append(("#" + gtr, G_.glass_grid(SK + "GtI", 1, 1, drag=False, slot=64, icon=52)))
    gtx = SK + "Gtx"
    ap.append(("#" + gtr, G_.glass_group(gtx, 178, 64, layout="Top", anchor={"left": 8})))
    ap.append(("#" + gtx, lab(SK + "GtN", "", 14, "title", bold=True, w=178, h=22)))
    ap.append(("#" + gtx, lab(SK + "GtT", "", 12, "accentHi", bold=True, w=178, h=20)))
    ap.append(("#" + gtx, lab(SK + "GtL", "", 12, "dim", w=178, h=20)))
    ap.append(("#" + gt, G_.glass_button(SK + "GtU", "Upgrade", "secondary", w=110, h=26, size=12, anchor={"top": 4})))
    aw_, _ah = SUI.glass_grid_size(4, 1, 64)
    ga = SK + "Ga"
    ap.append(("#" + gr, G_.glass_group(ga, aw_, 112, layout="Top", anchor={"left": 12})))
    gah = SK + "Gah"
    ap.append(("#" + ga, G_.glass_group(gah, aw_, 18, layout="Left")))
    ap.append(("#" + gah, lab(None, "ARMOR", 12, "dim", bold=True, w=60, h=18)))
    ap.append(("#" + gah, lab(SK + "GaS", "", 12, "green", bold=True, w=aw_ - 60, h=18)))
    ap.append(("#" + ga, G_.glass_grid(SK + "GaI", 4, 1, drag=False, slot=64, icon=52, anchor={"top": 4})))
    ap.append(("#" + ga, lab(SK + "GaL", "", 12, "text", w=aw_, h=22, anchor={"top": 4})))
    gbw = SK_MI - 250 - 12 - aw_ - 12
    assert gbw >= 200, ("0.3.57: the Requip column fits", gbw)
    gb = SK + "Gb"
    ap.append(("#" + gr, G_.glass_group(gb, gbw, 112, layout="Top", anchor={"left": 12})))
    ap.append(("#" + gb, G_.glass_button(SK + "GbR", "Requip", "primary", w=gbw, h=36, size=15)))
    ap.append(("#" + gb, lab(SK + "GbP", "", 12, "dim", w=gbw, h=20, halign="Center")))
    ap.append(("#" + gb, G_.glass_button(SK + "GbV", "Charms", "secondary", w=gbw, h=30, size=13, anchor={"top": 6})))
    # C) COLLECTIONS - THE PATH BY ZONE (the zone boxes, or the no-path note - kit 1.9 keep_holder: one shows)
    pa = SK + "Pa"
    ap.append(("#" + md, G_.glass_group(pa, SK_M, SK_PA_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    par = SK + "Par"
    ap.append(("#" + pa, G_.glass_group(par, SK_MI, 24, layout="Left")))
    ap.append(("#" + par, lab(SK + "PaT", "", 15, "accentHi", bold=True, w=330, h=24)))
    ap.append(("#" + par, lab(SK + "PaI", "", 12, "dim", w=SK_MI - 330 - 130, h=24)))
    ap.append(("#" + par, G_.glass_button(SK + "PaC", "Collections", "secondary", w=130, h=24, size=12)))
    zones = SUI.keep_at0(G_.glass_group(SK + "Zr", SK_MI, SK_ZB_H, layout="Left"))
    note = SUI.keep_at0(lab(SK + "Np", "", 14, "dim", w=SK_MI, h=40))
    hm_, kids_ = SUI.keep_holder(SK + "PaH", SK_MI, SK_ZB_H, [zones, note], anchor={"top": 6})
    ap.append(("#" + pa, hm_))
    ap.extend(kids_)
    ap.sets.append((SK + "Np", "Text", SK_TXT["nopath"]))
    for z_ in range(SK_ZN):
        zb = SK + "Z%d" % z_
        ap.append(("#" + SK + "Zr", G_.glass_group(zb, SK_ZW, SK_ZB_H, role="inset", layout="Top", pad=4, anchor={"right": 6} if z_ < SK_ZN - 1 else None)))
        tv = [SUI.keep_at0(lab(SK + "Zt%d" % z_, "", 12, "title", bold=True, w=SK_ZW - 8, h=18)),
              SUI.keep_at0(lab(SK + "Zk%d" % z_, "", 12, "red", bold=True, w=SK_ZW - 8, h=18))]
        zh_, zk_ = SUI.keep_holder(SK + "Zh%d" % z_, SK_ZW - 8, 18, tv)
        ap.append(("#" + zb, zh_))
        ap.extend(zk_)
        ap.append(("#" + zb, lab(SK + "Zl%d" % z_, "", 11, "dim", w=SK_ZW - 8, h=16)))
        zc = SK + "Zc%d" % z_
        ap.append(("#" + zb, G_.glass_group(zc, SK_ZW - 8, SK_ZK * SK_ZS + (SK_ZK - 1) * SUI.GRID_SPACING, layout="Left", anchor={"top": 4})))
        ap.append(("#" + zc, G_.glass_grid(SK + "Zg%d" % z_, 1, SK_ZK, drag=False, slot=SK_ZS, icon=SK_ZI)))
        zx = SK + "Zx%d" % z_
        ap.append(("#" + zc, G_.glass_group(zx, SK_ZTW, SK_ZK * SK_ZS + (SK_ZK - 1) * SUI.GRID_SPACING, layout="Top", anchor={"left": 2})))
        for k_ in range(SK_ZK):
            ze = SK + "Ze%d%d" % (z_, k_)
            ap.append(("#" + zx, G_.glass_group(ze, SK_ZTW, SK_ZS, layout="Top", anchor={"bottom": SUI.GRID_SPACING} if k_ < SK_ZK - 1 else None)))
            # the name: plain, or in the action colour when it is the SELECTED tier (keep_holder: one shows)
            nv = [SUI.keep_at0(lab(SK + "Zn%d%d" % (z_, k_), "", 12, "title", bold=True, w=SK_ZTW, h=20)),
                  SUI.keep_at0(lab(SK + "Zs%d%d" % (z_, k_), "", 12, "action", bold=True, w=SK_ZTW, h=20))]
            nh_, nk_ = SUI.keep_holder(SK + "Zm%d%d" % (z_, k_), SK_ZTW, 20, nv)
            ap.append(("#" + ze, nh_))
            ap.extend(nk_)
            ap.append(("#" + ze, lab(SK + "Zv%d%d" % (z_, k_), "", 11, "dim", w=SK_ZTW, h=18)))
    assert SUI.text_width("Lv 100  locked", 11) <= SK_ZTW and SUI.text_width("Lv 100  999k", 11) <= SK_ZTW and SUI.text_width("Lv 100  9999", 11) <= SK_ZTW, "0.3.57: a tier's level line fits"
    assert SK_ZN * SK_ZW + (SK_ZN - 1) * 6 <= SK_MI and SK_ZTW >= 70, ("0.3.57: the zone boxes fit", SK_ZW, SK_ZTW)
    ap.append(("#" + pa, lab(SK + "PaS", "", 12, "text", w=SK_MI, h=20, anchor={"top": 6})))
    ap.append(("#" + pa, lab(SK + "PaN", "", 12, "text", w=SK_MI, h=20)))
    assert 20 + 24 + 6 + SK_ZB_H + 6 + 20 + 20 <= SK_PA_H, ("0.3.57: the path panel fits", SK_ZB_H)
    # D) SKILL TREE: points + PERKS NOW + Open tree
    tr = SK + "Tr"
    ap.append(("#" + md, G_.glass_group(tr, SK_M, SK_TR_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    trr = SK + "Trr"
    ap.append(("#" + tr, G_.glass_group(trr, SK_MI, 30, layout="Left")))
    ap.append(("#" + trr, lab(None, "SKILL TREE", 15, "accentHi", bold=True, w=160, h=30)))
    ap.append(("#" + trr, lab(SK + "TrP", "", 13, "xp", bold=True, w=SK_MI - 160 - 170, h=30)))
    ap.append(("#" + trr, G_.glass_button(SK + "TrO", "Open tree", "primary", w=170, h=30, size=14)))
    # the Combat page's ABILITIES line (Skyy 11-14: "the COMBAT skill page holds your class (abilities, class tree, combat gear)"; read only,
    # SkyyClasses class:fn:abil - the 4 slots' names + state; empty on every other skill)
    ap.append(("#" + tr, lab(SK + "TrA", "", 13, "gold", bold=True, w=SK_MI, h=22, anchor={"top": 6})))
    ap.append(("#" + tr, lab(None, "PERKS NOW", 12, "dim", bold=True, w=SK_MI, h=20, anchor={"top": 8})))
    for k_ in range(SK_TRN):
        ap.append(("#" + tr, lab(SK + "Tl%d" % k_, "", 13, "text", w=SK_MI, h=26)))
    assert 20 + 30 + 28 + 28 + SK_TRN * 26 <= SK_TR_H, ("0.3.57: the tree panel fits (+ the ABILITIES line)", SK_TR_H)
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== RIGHT: the SKILLS grid (cells appended at run time into the 6 rows) + the SHARD card
    rt = SK + "Rt"
    ap.append(("#" + body, G_.glass_group(rt, SK_R, IV_BODY_H, layout="Top")))
    sk_h = 20 + 24 + 6 + (SK_GN // 2) * 64
    skp = SK + "Sk"
    ap.append(("#" + rt, G_.glass_group(skp, SK_R, sk_h, role="panel", layout="Top", pad=10, anchor={"bottom": 10})))
    ap.append(("#" + skp, lab(None, "SKILLS", 15, "accentHi", bold=True, w=SK_RI, h=24)))
    for r_ in range(SK_GN // 2):
        ap.append(("#" + skp, G_.glass_group(SK + "Gr%d" % r_, SK_RI, 64, layout="Left", anchor={"top": 6} if r_ == 0 else None)))
    sh_h = IV_BODY_H - sk_h - 10
    sh = SK + "Sh"
    ap.append(("#" + rt, G_.glass_group(sh, SK_R, sh_h, role="panel", layout="Top", pad=10)))
    ap.append(("#" + sh, lab(SK + "ShT", "", 15, "accentHi", bold=True, w=SK_RI, h=24)))
    shp = SK + "ShP"
    ap.append(("#" + sh, G_.glass_group(shp, SK_RI, 150, layout="Left", anchor={"top": 6})))
    ap.append(("#" + shp, "Group { Anchor: (Width: %d); }" % ((SK_RI - 150) // 2)))
    ap.append(("#" + shp, G_.glass_grid(SK + "ShI", 1, 1, drag=False, slot=150, icon=120)))
    sv = [SUI.keep_at0(lab(SK + "ShS" + s_, "", 16, c_, bold=True, w=SK_RI, h=24)) for s_, c_ in (("", "title"), ("R", "red"), ("G", "green"))]
    shm, shk = SUI.keep_holder(SK + "ShSH", SK_RI, 24, sv, anchor={"top": 6})
    ap.append(("#" + sh, shm))
    ap.extend(shk)
    ap.append(("#" + sh, lab(SK + "ShU", "", 14, "xp", bold=True, w=SK_RI, h=20)))
    ap.append(("#" + sh, 'Group #%sShB { Anchor: (Width: %d, Height: 8, Top: 6); LayoutMode: Left; Background: %s; }' % (SK, SK_SHBW, IV_TRACK)))
    ap.append(("#" + sh, lab(SK + "Sh1", "", 12, "text", w=SK_RI, h=20, anchor={"top": 6})))
    ap.append(("#" + sh, lab(SK + "Sh2", "", 12, "dim", w=SK_RI, h=20)))
    ap.append(("#" + sh, G_.glass_button(SK + "ShGo", "", "primary", w=SK_RI, h=36, size=14, anchor={"top": 8})))
    assert 20 + 24 + 156 + 30 + 20 + 14 + 46 + 44 <= sh_h, ("0.3.57: the shard card fits", sh_h)
    # one 1080p screen, nothing scrolls (Skyy: "all fit so there is no zooming or scrolling"): the page root is the kit's ceiling
    # (MAX_PAGE_H = 980 + decorations fits 1080), and every column adds up to the body height exactly
    assert (IV_PAGE_H <= SUI.MAX_PAGE_H and IV_PAGE_W <= SUI.MAX_PAGE_W and SK_TR_H > 0
            and SK_HD_H + SK_GR_H + SK_PA_H + SK_TR_H + 3 * 8 == IV_BODY_H and sk_h + 10 + sh_h == IV_BODY_H
            and SK_L + SK_M + SK_R + 2 * IV_GAP == IV_IW), "0.3.57: the skill page fits one 1080p screen"
    # ---- row 3: the caption + key hints
    hn = SK + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(SK + "K%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate((("LMB", "Open or select"), ("Tab / Esc", "Close")))]
    hw = sum(w_ for _m, w_ in parts)
    ap.append(("#" + hn, lab(SK + "Cap", "", 14, "dim", w=IV_IW - hw - 20, h=IV_HINT_H)))
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    binds = [("#%sT%d" % (SK, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [
        ("#" + SK + "Close", "close"), ("#" + SK + "GtU", "up"), ("#" + SK + "GbR", "rq"), ("#" + SK + "GbV", "vc"), ("#" + SK + "PaC", "col"),
        ("#" + SK + "TrO", "tr"), ("#" + SK + "ShGo", "sh")]
    return ap, binds


SK_AP, SK_BINDS = _sk_page()
SUI.check_page(SK_AP, SK)
for _p, _mk in SK_AP:
    SUI.check_markup(_mk, prefix=SK, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.57: the skill page never scrolls"
_sk_ids = set(i_ for _p, mk_ in SK_AP for i_ in SUI._static_ids(mk_))
for _s, _a in SK_BINDS:
    assert _s[1:] in _sk_ids, ("0.3.57: binding target", _s)
for _g in (["Coins", "Close", "Cap", "StW", "StF", "HdI", "HdT", "HdS", "HdC", "HdLv", "HdXa", "HdXn", "HdB", "HdU1", "GtI", "GtN", "GtT", "GtL", "GtU",
            "GaS", "GaI", "GaL", "GbR", "GbP", "GbV", "PaT", "PaI", "PaC", "PaH", "Zr", "Np", "PaS", "PaN", "TrP", "TrO", "TrA", "ShT", "ShI", "ShS", "ShSR", "ShSG",
            "ShU", "ShB", "Sh1", "Sh2", "ShGo"] + ["Sn%d" % k_ for k_ in range(SK_STN)] + ["Sv%d" % k_ for k_ in range(SK_STN)]
           + ["Tl%d" % k_ for k_ in range(SK_TRN)] + ["Gr%d" % k_ for k_ in range(SK_GN // 2)]
           + [x_ % z_ for z_ in range(SK_ZN) for x_ in ("Zt%d", "Zk%d", "Zl%d", "Zg%d")]
           + ["Z%s%d%d" % (c_, z_, k_) for c_ in ("n", "s", "v") for z_ in range(SK_ZN) for k_ in range(SK_ZK)]):
    assert SK + _g in _sk_ids, "0.3.57: the skill page has #" + SK + _g
_sk_tok = SUI.proven_tokens(list(SK_AP))
SK_UNPROVEN = sorted(k_ for k_, g_ in _sk_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_)))
assert set(SK_UNPROVEN) <= set(["SlotBackground"]), "0.3.57: only SlotBackground (proven on the inventory page, TEST 282): %s" % SK_UNPROVEN
assert not [k_ for k_ in _sk_tok if k_ in ("MouseEntered", "MouseExited", "TooltipText")], "0.3.57: no hover events / tooltips of ours"
SUI.assert_glass_paths(SK_AP)
SK_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in SK_AP)
_cell_el = len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9{}]+)?\s*\{", SUI._strip_quoted(SK_CELL.replace("{I}", "0"))))
SK_RUNTIME_MAX = SK_GN * (_cell_el + 1) + 2      # the 12 cells + their XP fills + the header / shard bar fills
SK_ELEMENTS = SK_SHELL_ELEMENTS + SK_RUNTIME_MAX
assert SK_ELEMENTS <= 800, "0.3.57: the skill page stays well under the ~1,600 element budget (%d static + %d at run time)" % (SK_SHELL_ELEMENTS, SK_RUNTIME_MAX)
SK_LK, SK_LP, SK_LB = [], [], []
for _p, _mk in SK_AP:
    SK_LK.append("A")
    SK_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    SK_LB.append(SUI.render(_mk))
for _i, _pr, _v in SK_AP.sets:
    SK_LK.append("S")
    SK_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    SK_LB.append(_v)
for _s, _a in SK_BINDS:
    SK_LK.append("E")
    SK_LP.append(_s)
    SK_LB.append(_a)
assert SK_LK[0] == "A" and SK_LP[0] == "", "0.3.57: the page data starts with the root"
for _x in SK_LP + SK_LB:
    assert "@" not in _x and "\n" not in _x and len(_x.encode("utf-8")) < 60000, "0.3.57: a page line Java can hold"
print("0.3.57 skill page: %d elements (shell %d + at most %d at run time; budget ~1,600), %d appends, %d b.set, %d bindings; unproven: %s"
      % (SK_ELEMENTS, SK_SHELL_ELEMENTS, SK_RUNTIME_MAX, len(SK_AP), len(SK_AP.sets), len(SK_BINDS), ", ".join(SK_UNPROVEN)))

'''
P.rep('''PKG = T["PKG"]
# 0.2: every class goes through mk()''', SK_PAGE.lstrip("\n") + '''PKG = T["PKG"]
# 0.2: every class goes through mk()''')

# ---------- the two new classes
P.rep('''icr  = mk("InvCraft")       # 0.3.52: our own crafting (the list, the stock, the craft as CraftingManager.craftItem does it) + side-panel reads
''', '''icr  = mk("InvCraft")       # 0.3.52: our own crafting (the list, the stock, the craft as CraftingManager.craftItem does it) + side-panel reads
sdat = mk("SkillData")      # 0.3.57: the skill page's data (LK / LP / LB, the 12 skills, the path by zone, the run-time markup)
skpg = mk("SkillPage", T["PAGE"])   # 0.3.57: ONE PAGE PER SKILL (the inventory's Skills tab)
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, pl)''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, pl)''')

# ---------- SkillData constants + SkillPage fields / constructor (before any method that reads them)
SK_DATA = r'''
# 0.3.57: THE SKILL PAGE DATA (SkillData) + the SkillPage fields
F(sdat, "public static final String LK = %s;" % jstr("".join(SK_LK)))
F(sdat, "public static final String[] LP = %s;" % jarr(SK_LP))
F(sdat, "public static final String[] LB = %s;" % jarr(SK_LB))
F(sdat, "public static final String[] ORDER = %s;" % jarr([s_[0] for s_ in SK_SKILLS]))
F(sdat, "public static final String[] TOOLP = %s;" % jarr([s_[1] for s_ in SK_SKILLS]))
F(sdat, "public static final String[] TREE = %s;" % jarr([s_[2] for s_ in SK_SKILLS]))
F(sdat, "public static final boolean[] SHARD = new boolean[] { %s };" % ", ".join("true" if s_[3] else "false" for s_ in SK_SKILLS))
F(sdat, "public static final String DEF = %s;" % jstr("Mining"))
for _n, _v in (("STN", SK_STN), ("TRN", SK_TRN), ("GN", SK_GN), ("ZN", SK_ZN), ("ZK", SK_ZK), ("CBW", SK_CBW - 6), ("HDBW", SK_HDBW), ("SHBW", SK_SHBW),
               ("SHARD_LV", SK_SHARD_LV)):
    F(sdat, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("CELL", SK_CELL), ("BG_CELL", SK_BG_CELL), ("BG_SEL", SK_BG_SEL), ("ST_CB", SK_ST_CB), ("ST_CBSEL", SK_ST_CBSEL), ("FILL6", IV_FILL),
               ("FILL10", SK_FILL10), ("FILL8", SK_FILL8), ("ALLOY", SK_TXT["alloy"])):
    F(sdat, "public static final String %s = %s;" % (_n, jstr(_v)))
F(sdat, "public static final String[] LADDER = %s;" % jarr(list(_TT57.LADDER)))
F(sdat, "public static final String[] P_SKILL = %s;" % jarr([r_[0] for r_ in SK_PATH]))
F(sdat, "public static final String[] P_ID = %s;" % jarr([r_[1] for r_ in SK_PATH]))
F(sdat, "public static final String[] P_NAME = %s;" % jarr([r_[2] for r_ in SK_PATH]))
F(sdat, "public static final int[] P_LV = %s;" % jints([r_[3] for r_ in SK_PATH]))
F(sdat, "public static final int[] P_ZONE = %s;" % jints([r_[4] for r_ in SK_PATH]))
F(sdat, "public static final String[] P_COLL = %s;" % jarr([r_[5] for r_ in SK_PATH]))
F(sdat, "public static final boolean[] P_ALLOY = new boolean[] { %s };" % ", ".join("true" if r_[6] else "false" for r_ in SK_PATH))
F(sdat, "public static final String[] P_TAG = %s;" % jarr([r_[7] for r_ in SK_PATH]))
F(sdat, "public static final String[] P_PAR = %s;" % jarr([r_[8] for r_ in SK_PATH]))
for _f in ("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> the last skill shown
           "public static volatile int OPENS = 0;",
           "public volatile boolean closed;", "public boolean answered;", "public String skill;", "public String via;", "public String tcap;",
           "public int sel;", "public int[] zmap;", "public int presetN;", "public String[] pl;", "public java.util.ArrayList srows;",
           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;"):
    F(skpg, _f)
C(skpg, r"""
public SkillPage(@PR@ pr, String skill, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.skill = skill;
  this.via = via;
  this.closed = false;
  this.answered = false;
  this.tcap = "";
  this.sel = -1;
  this.zmap = new int[18];
  this.presetN = -1;
  this.pl = null;
  this.srows = new java.util.ArrayList();
  this.builds = 0;
  this.answers = 0;
}""")
'''
P.rep('''print("0.3.52 crafting: %d tier rows baked from tools/tier_tags.py (TT_VERSION %s), %d metal words" % (len(_tt), _TT.TT_VERSION, len(_TT.TOOL_METALS)))
''', '''print("0.3.52 crafting: %d tier rows baked from tools/tier_tags.py (TT_VERSION %s), %d metal words" % (len(_tt), _TT.TT_VERSION, len(_TT.TOOL_METALS)))
''' + SK_DATA.lstrip("\n"))

# ---------- InvState.openAt + THE SKILL PAGE methods (after InvState.openPage, before the Tab task that closes a skill page)
SK_JAVA = r'''# ---- 0.3.57: the inventory opened on a panel (the skill page's Requip / Charms / Inventory buttons): the mode is set BEFORE the open,
# so the one page packet already shows that panel ("r" = the Requip panel on preset rsel, "v" = the Charms panel, "c" = crafting)
M(ist, r"""
public static @PKG@.InvPage openAt(@REF@ ref, @ST@ st, @PR@ pr, String via, String mode, int rsel) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) return null;
  @PKG@.InvPage pg = new @PKG@.InvPage(pr, via);
  if ("r".equals(mode)) { pg.mode = "r"; pg.rsel = rsel; pg.rslot = -1; pg.rlTop = -1; }
  else if ("v".equals(mode)) { pg.mode = "v"; pg.vpage = 0; }
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("inventory page could not open for " + pr.getUsername() + ": " + t); pg.finish("open failed"); return null; }
  OPENS = OPENS + 1;
  return pg;
}""")

# ================= 0.3.57 SkillPage: ONE PAGE PER SKILL (the inventory's Skills tab; approved skill-page-mining.png) =================
# Read only: skill:fn:prog (SkyySkills 0.4.71), skill:<uuid>, the Stats page rows (StatsCalc), requip:fn:presets / preset (SkyyWardrobe
# 0.2.14), coll:fn:count / tier (SkyyCollections), tree:<uuid> (SkyyTrees), purse. Every bound click answers with ONE page packet.
M(skpg, r"""
public static int idx(String s) {
  if (s == null) return -1;
  for (int i = 0; i < @PKG@.SkillData.ORDER.length; i++) { if (@PKG@.SkillData.ORDER[i].equals(s)) return i; }
  return -1;
}""")
M(skpg, r"""
public static String lastOf(java.util.UUID u) {
  Object o = u == null ? null : LAST.get(u);
  return (o instanceof String && idx((String) o) >= 0) ? (String) o : @PKG@.SkillData.DEF;
}""")
M(skpg, r"""
public static void forget(java.util.UUID u) { if (u != null) LAST.remove(u); }""")
M(skpg, r"""
public static String roman(long n) {
  if (n <= 0L) return "0";
  String[] r = new String[] { "M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I" };
  int[] v = new int[] { 1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1 };
  long x = n > 3999L ? 3999L : n;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length; i++) { while (x >= (long) v[i]) { sb.append(r[i]); x = x - (long) v[i]; } }
  return sb.toString();
}""")
M(skpg, r"""
public Object call(String key, Object arg) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null) return null;
  try { return f.apply(arg); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: " + key + " failed: " + t); return null; }
}""")
M(skpg, r"""
public String[] lines(String key, Object arg) {
  Object o = call(key, arg);
  if (!(o instanceof String)) return null;
  return ((String) o).split("\n");
}""")
M(skpg, r"""
public boolean progOn() { return this.pl != null && this.pl.length > 0 && this.pl[0].startsWith("ok|"); }""")
# the class skill's label: skill:fn:prog's first line, else the Stats page's class:skill:<uuid>
M(skpg, r"""
public String classLabel() {
  if (progOn()) { String c = this.pl[0].substring(3); return c.length() > 0 ? c : null; }
  try { return @PKG@.StatsCalc.classSkill(this.playerRef.getUuid()); } catch (Throwable t) { return null; }
}""")
M(skpg, r"""
public String[] fields(String sk) {
  String lb = "Combat".equals(sk) ? classLabel() : sk;
  if (lb == null || !progOn()) return null;
  for (int i = 1; i < this.pl.length; i++) {
    String[] f = this.pl[i].split("\\|", -1);
    if (f.length >= 6 && f[0].equals(lb)) return f;
  }
  return null;
}""")
M(skpg, r"""
public long level(String sk) {
  String[] f = fields(sk);
  if (f != null) return @PKG@.InvPage.toLong(f[1], -1L);
  String lb = "Combat".equals(sk) ? classLabel() : sk;
  if (lb == null) return -1L;
  return (long) @PKG@.InvPage.skillLevel(this.playerRef.getUuid(), lb);
}""")
M(skpg, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyySkpCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(skpg, r"""
public void finish(String why) { this.closed = true; }""")
M(skpg, r"""
public void shut() { finish("closed"); this.close(); }""")
M(skpg, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(skpg, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.answers = this.answers + 1;
  this.rebuild();
}""")
# ---- the fills (world thread, bridge reads only)
M(skpg, r"""
public static @IGS@ icon(String id, String name, String desc, boolean grey) {
  @IGS@ g = new @IGS@();
  if (id != null && id.length() > 0 && id.length() < 120 && @PKG@.InvPage.known(id)) g.setItemStack(new @IS@(id, 1));
  if (name != null && name.length() > 0) g.setName(name);
  if (desc != null && desc.length() > 0) g.setDescription(desc);
  if (grey) g.setItemUncraftable(true);
  return g;
}""")
M(skpg, r"""
public void fillCells(@UCB@ b, @UEB@ ev) {
  int n = @PKG@.SkillData.GN;
  for (int i = 0; i < n; i++) {
    String sk = @PKG@.SkillData.ORDER[i];
    boolean on = sk.equals(this.skill);
    String mk = @PKG@.SkillData.CELL.replace("{I}", String.valueOf(i)).replace("{R}", String.valueOf(i % 2 == 0 ? 6 : 0))
        .replace("{BG}", on ? @PKG@.SkillData.BG_SEL : @PKG@.SkillData.BG_CELL).replace("{S}", on ? @PKG@.SkillData.ST_CBSEL : @PKG@.SkillData.ST_CB);
    b.appendInline("#SkyySkpGr" + (i / 2), mk);
    String[] f = fields(sk);
    long lv = level(sk);
    String cl = "Combat".equals(sk) ? classLabel() : null;
    String lt = lv >= 0L ? "Lv " + lv : ("Combat".equals(sk) && cl == null ? "pick a class" : "Lv -");
    String desc = "";
    int w = 0;
    String iconId = null;
    if (f != null) {
      long into = @PKG@.InvPage.toLong(f[2], 0L);
      long need = @PKG@.InvPage.toLong(f[3], 0L);
      iconId = f[4];
      desc = (cl != null ? "Your class skill: " + cl + "\n" : "") + (need > 0L ? "XP " + @PKG@.MenuUtil.fmt(into) + " / " + @PKG@.MenuUtil.fmt(need) + " to Lv " + (lv + 1) : "MAX LEVEL")
          + "\nClick: open the " + sk + " page";
      w = @PKG@.InvPage.barW(into, need, @PKG@.SkillData.CBW);
    } else desc = "Click: open the " + sk + " page";
    java.util.ArrayList sl = new java.util.ArrayList();
    sl.add(icon(iconId, sk + (lv >= 0L ? " - Lv " + lv : ""), desc, false));
    b.set("#SkyySkpCi" + i + ".Slots", sl);
    b.set("#SkyySkpCb" + i + ".Text", sk);
    b.set("#SkyySkpCl" + i + ".Text", lt);
    if (w > 0) b.appendInline("#SkyySkpCt" + i, @PKG@.SkillData.FILL6.replace("{W}", String.valueOf(w)));
    ev.addEventBinding(@BT@.Activating, "#SkyySkpCb" + i, @EVD@.of("a", "sk:" + i));
    ev.addEventBinding(@BT@.SlotClicking, "#SkyySkpCi" + i, @EVD@.of("a", "sk:" + i), false);
  }
}""")
# the path entries of this skill (indexes into SkillData.P_*), in order
M(skpg, r"""
public java.util.ArrayList pathOf(String sk) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.SkillData.P_SKILL.length; i++) { if (@PKG@.SkillData.P_SKILL[i].equals(sk)) out.add(Integer.valueOf(i)); }
  return out;
}""")
M(skpg, r"""
public String nextUnlock(String sk, long lv) {
  if (lv < 0L) return "Level this skill to open its path";
  java.util.ArrayList ps = pathOf(sk);
  int best = -1;
  for (int k = 0; k < ps.size(); k++) {
    int e = ((Integer) ps.get(k)).intValue();
    if ((long) @PKG@.SkillData.P_LV[e] > lv) { best = e; break; }
  }
  int si = idx(sk);
  boolean shard = si >= 0 && @PKG@.SkillData.SHARD[si] && lv < (long) @PKG@.SkillData.SHARD_LV;
  if (shard && (best < 0 || @PKG@.SkillData.P_LV[best] >= @PKG@.SkillData.SHARD_LV)) return "Lv " + @PKG@.SkillData.SHARD_LV + ": your " + sk + " Shard";
  if (best < 0) return ps.size() > 0 ? "Every tier of the path is open" : "Lv " + (lv + 1) + ": more " + sk + " perks and tree points";
  String nm = @PKG@.SkillData.P_NAME[best];
  return "Lv " + @PKG@.SkillData.P_LV[best] + ": " + nm + (@PKG@.SkillData.P_ALLOY[best] ? " alloy" : " + the " + nm + " collection");
}""")
M(skpg, r"""
public void fillHead(@UCB@ b) {
  String sk = this.skill;
  String[] f = fields(sk);
  long lv = level(sk);
  b.set("#SkyySkpHdT.Text", sk.toUpperCase());
  String cl = null;
  if ("Combat".equals(sk)) {
    String cn = null;
    try { cn = @PKG@.StatsCalc.className(this.playerRef.getUuid()); } catch (Throwable t) { cn = null; }
    cl = classLabel();
    b.set("#SkyySkpHdC.Text", cn == null ? "No class yet - pick one to level Combat" : "Class: " + cn + (cl != null ? " - " + cl : ""));
  } else b.set("#SkyySkpHdC.Text", "");
  b.set("#SkyySkpHdLv.Text", lv >= 0L ? String.valueOf(lv) : "-");
  java.util.ArrayList sl = new java.util.ArrayList();
  sl.add(icon(f == null ? null : f[4], sk + (lv >= 0L ? " - Lv " + lv : ""), cl != null ? "Your class skill: " + cl : "", false));
  b.set("#SkyySkpHdI.Slots", sl);
  if (f != null) {
    long into = @PKG@.InvPage.toLong(f[2], 0L);
    long need = @PKG@.InvPage.toLong(f[3], 0L);
    b.set("#SkyySkpHdXa.Text", need > 0L ? "Lv " + lv + "  ->  " + (lv + 1) : "Lv " + lv);
    b.set("#SkyySkpHdXn.Text", need > 0L ? @PKG@.MenuUtil.fmt(into) + " / " + @PKG@.MenuUtil.fmt(need) + " XP" : "MAX LEVEL");
    int w = @PKG@.InvPage.barW(into, need, @PKG@.SkillData.HDBW);
    if (w > 0) b.appendInline("#SkyySkpHdB", @PKG@.SkillData.FILL10.replace("{W}", String.valueOf(w)));
  } else {
    b.set("#SkyySkpHdXa.Text", lv >= 0L ? "Lv " + lv : "");
    b.set("#SkyySkpHdXn.Text", "Combat".equals(sk) && classLabel() == null ? "no class yet" : "XP shows with SkyySkills 0.4.71");
  }
  b.set("#SkyySkpHdU1.Text", nextUnlock(sk, lv));
}""")
M(skpg, r"""
public static boolean toolOf(String id, String pre) {
  if (id == null || id.length() == 0 || pre == null || pre.length() == 0) return false;
  String[] ps = pre.split(",");
  for (int i = 0; i < ps.length; i++) { if (ps[i].length() > 0 && id.startsWith(ps[i])) return true; }
  return false;
}""")
M(skpg, r"""
public static String tierText(String id) {
  int t = 0;
  try { t = @PKG@.InvCraft.tier(id); } catch (Throwable e) { t = 0; }
  if (t <= 0 || t > @PKG@.SkillData.LADDER.length) return "";
  return "T" + t + " " + @PKG@.SkillData.LADDER[t - 1];
}""")
# GEAR: the skill's Requip preset (requip:fn:presets / preset) - its tool + armour + marks; without one: what you wear + the hotbar's tool
M(skpg, r"""
public void fillGear(@UCB@ b, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  String sk = this.skill;
  int si = idx(sk);
  String pre = si >= 0 ? @PKG@.SkillData.TOOLP[si] : "";
  this.presetN = -1;
  boolean worn = false;
  String[] ls = lines("requip:fn:presets", u);
  if (ls != null && ls.length > 0 && ls[0].startsWith("ok|")) {
    String[] h = ls[0].split("\\|", -1);
    int wn = h.length > 1 ? @PKG@.InvPage.toInt(h[1], -1) : -1;
    for (int i = 1; i < ls.length && this.presetN < 0; i++) {
      String[] f = ls[i].split("\\|", -1);
      if (f.length >= 2 && f[1].trim().equalsIgnoreCase(sk)) { this.presetN = @PKG@.InvPage.toInt(f[0], -1); worn = this.presetN >= 0 && this.presetN == wn; }
    }
  }
  String[] ids = new String[13];
  String[] marks = new String[13];
  String[] tit = new String[13];
  boolean got = false;
  if (this.presetN >= 0) {
    String[] d = lines("requip:fn:preset", new Object[] { u, Integer.valueOf(this.presetN) });
    if (d != null && d.length > 0 && d[0].startsWith("ok|")) {
      got = true;
      for (int i = 1; i < d.length; i++) {
        String[] f = d[i].split("\\|", -1);
        if (f.length < 4) continue;
        int k = @PKG@.InvPage.toInt(f[0], -1);
        if (k < 0 || k > 12) continue;
        marks[k] = f[1];
        ids[k] = f[2];
        tit[k] = f[3];
      }
    }
  }
  java.util.ArrayList ar = new java.util.ArrayList();
  int on = 0;
  int miss = 0;
  String tool = null;
  String from = "";
  if (got) {
    for (int k = 0; k < 4; k++) {
      ar.add(@PKG@.InvPage.rqSlot(ids[k], tit[k], marks[k]));
      if ("on".equals(marks[k])) on = on + 1;
      if ("missing".equals(marks[k]) || "gone".equals(marks[k])) miss = miss + 1;
    }
    for (int k = 4; k < 13 && tool == null; k++) { if (toolOf(ids[k], pre)) { tool = ids[k]; from = "From your " + sk + " preset"; } }
    b.set("#SkyySkpGaS.Text", sk + " set  " + on + " / 4 on you");
    b.set("#SkyySkpGaL.Text", miss > 0 ? miss + " missing - Requip shows where" : (worn ? "Worn now" : "Requip puts it on"));
    b.set("#SkyySkpGbP.Text", sk + " preset" + (worn ? " - worn" : ""));
    b.set("#SkyySkpStW.Text", worn ? "With your " + sk + " set on" : "Your stats now - your " + sk + " set is not on");
  } else {
    @IC@ a = null;
    try {
      @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (p != null && p.getInventory() != null) a = p.getInventory().getSectionById(@INVC@.ARMOR_SECTION_ID);
    } catch (Throwable t) { a = null; }
    for (int k = 0; k < 4; k++) {
      @IS@ s = (a != null && k < a.getCapacity()) ? a.getItemStack((short) k) : null;
      ar.add(@PKG@.InvPage.slot(s));
      if (s != null && !s.isEmpty()) on = on + 1;
    }
    b.set("#SkyySkpGaS.Text", "Worn now  " + on + " / 4");
    b.set("#SkyySkpGaL.Text", ls == null ? "Requip presets are not on this server" : "No " + sk + " preset yet");
    b.set("#SkyySkpGbP.Text", ls == null ? "" : "Make a " + sk + " preset in Requip");
    b.set("#SkyySkpStW.Text", "Your stats now");
  }
  b.set("#SkyySkpGaI.Slots", ar);
  if (tool == null && pre.length() > 0) {
    try {
      @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      @IC@ c = p == null ? null : @PKG@.InvCraft.bagHotbarFirst(p);
      for (int i = 0; c != null && i < c.getCapacity() && tool == null; i++) {
        @IS@ s = c.getItemStack((short) i);
        if (s != null && !s.isEmpty() && toolOf(s.getItemId(), pre)) { tool = s.getItemId(); from = "From your inventory"; }
      }
    } catch (Throwable t) { tool = null; }
  }
  java.util.ArrayList tl = new java.util.ArrayList();
  if (tool != null) {
    String tt = tierText(tool);
    tl.add(icon(tool, @PKG@.InvCraft.name(tool), (tt.length() > 0 ? tt + "\n" : "") + from, false));
    b.set("#SkyySkpGtN.Text", @PKG@.MenuUtil.clip(@PKG@.InvCraft.name(tool), 22));
    b.set("#SkyySkpGtT.Text", tt);
    b.set("#SkyySkpGtL.Text", from);
  } else {
    tl.add(new @IGS@());
    b.set("#SkyySkpGtN.Text", pre.length() > 0 ? "No tool found" : "No tool for this skill");
    b.set("#SkyySkpGtT.Text", "");
    b.set("#SkyySkpGtL.Text", pre.length() > 0 ? "Put one in the preset or your bag" : "");
  }
  b.set("#SkyySkpGtI.Slots", tl);
}""")
M(skpg, r"""
public void fillStats(@UCB@ b, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  String sk = this.skill;
  Object[] vit = null;
  try { vit = @PKG@.StatsCalc.vitals(st, ref); } catch (Throwable t) { vit = null; }
  java.util.ArrayList own = new java.util.ArrayList();
  if ("Combat".equals(sk)) own = @PKG@.StatsCalc.rows(u, 1, vit);
  else {
    java.util.ArrayList g = @PKG@.StatsCalc.rows(u, 2, vit);
    for (int i = 0; i < g.size(); i++) {
      Object o = g.get(i);
      if (o instanceof String[] && ((String[]) o).length >= 2 && ((String[]) o)[0].startsWith(sk + " ")) own.add(o);
    }
  }
  this.srows = own;
  java.util.ArrayList out = new java.util.ArrayList();
  if (own.size() > 0) { out.add(new String[] { sk.toUpperCase(), "" }); for (int i = 0; i < own.size(); i++) out.add(own.get(i)); }
  java.util.ArrayList mn = @PKG@.StatsCalc.rows(u, 0, vit);
  out.add(new String[] { "GENERAL", "" });
  for (int i = 0; i < mn.size(); i++) out.add(mn.get(i));
  int n = @PKG@.SkillData.STN;
  for (int i = 0; i < n; i++) {
    String nm = "";
    String v = "";
    if (i < out.size() && out.get(i) instanceof String[]) {
      String[] r = (String[]) out.get(i);
      nm = @PKG@.MenuUtil.clip(r.length > 0 && r[0] != null ? r[0] : "", 28);
      v = @PKG@.MenuUtil.clip(r.length > 1 && r[1] != null ? r[1] : "", 14);
    }
    b.set("#SkyySkpSn" + i + ".Text", nm);
    b.set("#SkyySkpSv" + i + ".Text", v);
  }
}""")
# THE PATH BY ZONE: 6 boxes (Zone 1-5 + LATER), 3 tiers each; a zone above your level = LOCKED (red title, greyed icons, "locked")
M(skpg, r"""
public void fillPath(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  String sk = this.skill;
  long lv = level(sk);
  java.util.ArrayList ps = pathOf(sk);
  for (int i = 0; i < this.zmap.length; i++) this.zmap[i] = -1;
  String kind = "Mining".equals(sk) ? "METAL PATH" : ("Foraging".equals(sk) ? "WOOD PATH" : ("Farming".equals(sk) ? "CROP PATH" : "PATH"));
  b.set("#SkyySkpPaT.Text", "COLLECTIONS - " + kind);
  if (ps.size() == 0) {
    b.set("#SkyySkpZr.Visible", false);
    b.set("#SkyySkpNp.Visible", true);
    b.set("#SkyySkpPaI.Text", "");
    b.set("#SkyySkpPaS.Text", "");
    b.set("#SkyySkpPaN.Text", "");
    return;
  }
  b.set("#SkyySkpZr.Visible", true);
  b.set("#SkyySkpNp.Visible", false);
  b.set("#SkyySkpPaI.Text", "Tiers open with your " + sk + " LEVEL - recipes and rewards with the COLLECTION");
  boolean selOk = false;
  for (int k0 = 0; k0 < ps.size(); k0++) { if (((Integer) ps.get(k0)).intValue() == this.sel) selOk = true; }
  if (!selOk) {
    this.sel = ((Integer) ps.get(0)).intValue();
    for (int k1 = 0; k1 < ps.size(); k1++) { int e0 = ((Integer) ps.get(k1)).intValue(); if ((long) @PKG@.SkillData.P_LV[e0] <= lv) this.sel = e0; }
  }
  boolean collOn = @PKG@.InvCraft.fn("coll:fn:count") != null;
  long[] cnt = new long[@PKG@.SkillData.P_ID.length];
  long[] tier = new long[@PKG@.SkillData.P_ID.length];
  for (int z = 0; z < @PKG@.SkillData.ZN; z++) {
    int zmin = -1;
    int k = 0;
    java.util.ArrayList sl = new java.util.ArrayList();
    for (int j = 0; j < ps.size(); j++) {
      int e = ((Integer) ps.get(j)).intValue();
      if (@PKG@.SkillData.P_ZONE[e] != z + 1 || k >= @PKG@.SkillData.ZK) continue;
      if (zmin < 0 || @PKG@.SkillData.P_LV[e] < zmin) zmin = @PKG@.SkillData.P_LV[e];
      String nm = @PKG@.SkillData.P_NAME[e];
      boolean al = @PKG@.SkillData.P_ALLOY[e];
      boolean lk = lv < (long) @PKG@.SkillData.P_LV[e];
      long c = -1L;
      long t = -1L;
      String cid = @PKG@.SkillData.P_COLL[e];
      if (collOn && cid.length() > 0) {
        Object o1 = call("coll:fn:count", new Object[] { u, cid });
        Object o2 = call("coll:fn:tier", new Object[] { u, cid });
        c = o1 instanceof Number ? ((Number) o1).longValue() : -1L;
        t = o2 instanceof Number ? ((Number) o2).longValue() : -1L;
      }
      cnt[e] = c;
      tier[e] = t;
      String id = @PKG@.SkillData.P_ID[e];
      String desc = @PKG@.SkillData.P_TAG[e] + "\nOpens at " + sk + " Lv " + @PKG@.SkillData.P_LV[e] + (lk ? " (you " + (lv < 0L ? "-" : String.valueOf(lv)) + ")" : "")
          + (al ? "\nAlloy of " + @PKG@.SkillData.P_PAR[e] + " - no collection" : (c >= 0L ? "\n" + nm + " collection " + roman(t) + " - " + @PKG@.MenuUtil.fmt(c) + " collected" : ""))
          + "\nClick: select";
      sl.add(icon(id, @PKG@.InvCraft.name(id), desc, lk));
      b.set("#SkyySkpZn" + z + k + ".Text", nm);
      b.set("#SkyySkpZs" + z + k + ".Text", nm);
      b.set("#SkyySkpZn" + z + k + ".Visible", e != this.sel);
      b.set("#SkyySkpZs" + z + k + ".Visible", e == this.sel);
      String sfx = lk ? "locked" : (al ? "alloy" : (c >= 0L ? @PKG@.InvCraft.shortN(c) : ""));
      String l2 = "Lv " + @PKG@.SkillData.P_LV[e] + (sfx.length() > 0 ? "  " + sfx : "");
      b.set("#SkyySkpZv" + z + k + ".Text", l2);
      this.zmap[z * @PKG@.SkillData.ZK + k] = e;
      k = k + 1;
    }
    for (int j2 = k; j2 < @PKG@.SkillData.ZK; j2++) {
      sl.add(new @IGS@());
      b.set("#SkyySkpZn" + z + j2 + ".Text", "");
      b.set("#SkyySkpZs" + z + j2 + ".Visible", false);
      b.set("#SkyySkpZv" + z + j2 + ".Text", "");
    }
    b.set("#SkyySkpZg" + z + ".Slots", sl);
    boolean zl = zmin >= 0 && lv < (long) zmin;
    String zt = z + 1 < @PKG@.SkillData.ZN ? "ZONE " + (z + 1) : "LATER";
    b.set("#SkyySkpZt" + z + ".Text", zt);
    b.set("#SkyySkpZk" + z + ".Text", zt + "  LOCKED");
    b.set("#SkyySkpZt" + z + ".Visible", !zl);
    b.set("#SkyySkpZk" + z + ".Visible", zl);
    b.set("#SkyySkpZl" + z + ".Text", zmin >= 0 ? sk + " " + zmin + "+" : "");
    ev.addEventBinding(@BT@.SlotClicking, "#SkyySkpZg" + z, @EVD@.of("a", "pz:" + z), false);
  }
  int es = this.sel;
  String snm = @PKG@.SkillData.P_NAME[es];
  String what;
  if (@PKG@.SkillData.P_ALLOY[es]) what = "alloy of " + @PKG@.SkillData.P_PAR[es] + " - smelt it in the Furnace";
  else if (cnt[es] >= 0L) what = @PKG@.MenuUtil.fmt(cnt[es]) + " collected - collection " + roman(tier[es]);
  else what = collOn ? "no collection data yet" : "collections are not on this server";
  b.set("#SkyySkpPaS.Text", "SELECTED  " + snm + "  (" + @PKG@.SkillData.P_TAG[es] + ")  " + what + (lv < (long) @PKG@.SkillData.P_LV[es] ? "  - opens at Lv " + @PKG@.SkillData.P_LV[es] : ""));
  int nx = -1;
  for (int j3 = 0; j3 < ps.size() && nx < 0; j3++) { int x = ((Integer) ps.get(j3)).intValue(); if ((long) @PKG@.SkillData.P_LV[x] > lv) nx = x; }
  String nt = nx < 0 ? "NEXT TIER  every tier is open" : "NEXT TIER  " + @PKG@.SkillData.P_NAME[nx] + (@PKG@.SkillData.P_ALLOY[nx] ? " alloy" : "") + " at " + sk + " " + @PKG@.SkillData.P_LV[nx] + "  (you " + (lv < 0L ? "-" : String.valueOf(lv)) + ")";
  b.set("#SkyySkpPaN.Text", "Mining".equals(sk) ? nt + "     " + @PKG@.SkillData.ALLOY : nt);
}""")
# the Combat page's ABILITIES line: SkyyClasses class:fn:abil apply(UUID) -> Object[] (>= 16: slot k = [4k] name, [4k+3] state "ready" /
# "cooldown" / "locked" / "passive" / "soon" / "empty"; the HUD's own reader) - read only; null = no class with abilities
M(skpg, r"""
public String abilLine(java.util.UUID u) {
  if (@PKG@.InvCraft.fn("class:fn:abil") == null) return "ABILITIES  Classes are not on this server";
  Object o = call("class:fn:abil", u);
  if (!(o instanceof Object[]) || ((Object[]) o).length < 16) return "ABILITIES  your class's abilities show here once you have a class with abilities";
  Object[] a = (Object[]) o;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < 4; i++) {
    Object nm = a[i * 4];
    if (!(nm instanceof String) || ((String) nm).length() == 0) continue;
    Object st = a[i * 4 + 3];
    if (sb.length() > 0) sb.append("    ");
    sb.append(@PKG@.MenuUtil.safe((String) nm));
    if (st instanceof String && ((String) st).length() > 0 && !"empty".equals(st)) sb.append(" (").append(@PKG@.MenuUtil.safe((String) st)).append(")");
  }
  if (sb.length() == 0) return "ABILITIES  no ability in your slots yet - Open tree to pick them";
  return @PKG@.MenuUtil.clip("ABILITIES  " + sb.toString(), 110);
}""")
# tree:<uuid> = "<Tree>:<spent>/<points>,..." (SkyyTrees, the Right now panel's reader) - this skill's tree; PERKS NOW = the Stats rows' notes
M(skpg, r"""
public void fillTree(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  int si = idx(this.skill);
  String tn = si >= 0 ? @PKG@.SkillData.TREE[si] : this.skill;
  Object o = null;
  try { o = @PKG@.MenuUtil.bridge().get("tree:" + u.toString()); } catch (Throwable t) { o = null; }
  String pts = "No " + this.skill + " tree on this server";
  if (o instanceof String) {
    String[] es = ((String) o).split(",");
    for (int i = 0; i < es.length; i++) {
      String e = es[i].trim();
      int c = e.indexOf(':');
      int sl = c < 0 ? -1 : e.indexOf('/', c + 1);
      if (c <= 0 || sl < 0 || !e.substring(0, c).trim().equalsIgnoreCase(tn)) continue;
      int sp = @PKG@.InvPage.toInt(e.substring(c + 1, sl), 0);
      int tot = @PKG@.InvPage.toInt(e.substring(sl + 1), 0);
      int fr = tot - sp;
      pts = "Points  " + (fr > 0 ? fr : 0) + " free   " + sp + " spent of " + tot;
    }
  } else pts = "Trees are not on this server";
  b.set("#SkyySkpTrP.Text", pts);
  b.set("#SkyySkpTrA.Text", "Combat".equals(this.skill) ? abilLine(u) : "");
  int n = @PKG@.SkillData.TRN;
  int k = 0;
  java.util.ArrayList rs = this.srows;
  for (int i = 0; rs != null && i < rs.size() && k < n; i++) {
    Object x = rs.get(i);
    if (!(x instanceof String[])) continue;
    String[] r = (String[]) x;
    if (r.length != 3 || r[2] == null || r[2].length() == 0) continue;
    b.set("#SkyySkpTl" + k + ".Text", @PKG@.MenuUtil.clip(r[0] + "  " + r[1] + "  -  " + r[2], 110));
    k = k + 1;
  }
  if (k == 0 && k < n) { b.set("#SkyySkpTl0.Text", "Open tree to spend your points - its perks show here once they count"); k = 1; }
  for (int i = k; i < n; i++) b.set("#SkyySkpTl" + i + ".Text", "");
}""")
M(skpg, r"""
public void fillShard(@UCB@ b) {
  String sk = this.skill;
  int si = idx(sk);
  boolean has = si >= 0 && @PKG@.SkillData.SHARD[si];
  long lv = level(sk);
  int need = @PKG@.SkillData.SHARD_LV;
  String[] f = fields(sk);
  java.util.ArrayList sl = new java.util.ArrayList();
  sl.add(icon(f == null ? null : f[4], sk + " Shard", has ? (lv >= (long) need ? "Open - its portal is on your island" : "Unlocks at " + sk + " Lv " + need) : "No shard for this skill yet", has && lv < (long) need));
  b.set("#SkyySkpShI.Slots", sl);
  b.set("#SkyySkpShT.Text", sk.toUpperCase() + " SHARD");
  int st = 0;
  if (!has) {
    b.set("#SkyySkpShS.Text", "No " + sk + " shard yet");
    b.set("#SkyySkpShU.Text", "");
    b.set("#SkyySkpSh1.Text", "Shards: Combat, Mining, Foraging and Farming");
    b.set("#SkyySkpSh2.Text", "");
    b.set("#SkyySkpShGo.Text", "No shard yet");
  } else if (lv < (long) need) {
    st = 1;
    b.set("#SkyySkpShSR.Text", sk + " Shard - locked");
    b.set("#SkyySkpShU.Text", "Unlocks at " + sk + " Lv " + need);
    int w = @PKG@.InvPage.barW(lv < 0L ? 0L : lv, (long) need, @PKG@.SkillData.SHBW);
    if (w > 0) b.appendInline("#SkyySkpShB", @PKG@.SkillData.FILL8.replace("{W}", String.valueOf(w)));
    b.set("#SkyySkpSh1.Text", "You: " + sk + " Lv " + (lv < 0L ? "-" : String.valueOf(lv)) + "   " + (lv < 0L ? 0L : lv) + " / " + need);
    b.set("#SkyySkpSh2.Text", "Then its portal on your island opens it");
    b.set("#SkyySkpShGo.Text", "Locked - " + sk + " Lv " + need);
  } else {
    st = 2;
    b.set("#SkyySkpShSG.Text", sk + " Shard - open");
    b.set("#SkyySkpShU.Text", "Open it from its portal on your island");
    b.appendInline("#SkyySkpShB", @PKG@.SkillData.FILL8.replace("{W}", String.valueOf(@PKG@.SkillData.SHBW)));
    b.set("#SkyySkpSh1.Text", "Right-click the portal to open the shard");
    b.set("#SkyySkpSh2.Text", "Collect, upgrades and totems are there");
    b.set("#SkyySkpShGo.Text", "Go to my island");
  }
  b.set("#SkyySkpShS.Visible", st == 0);
  b.set("#SkyySkpShSR.Visible", st == 1);
  b.set("#SkyySkpShSG.Visible", st == 2);
}""")
M(skpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.SkillData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.SkillData.LP[i];
    String y = @PKG@.SkillData.LB[i];
    if (k == 'A') b.appendInline(x.length() == 0 ? (String) null : x, y);
    else if (k == 'S') b.set(x, y);
    else if (k == 'E') ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
  }
  if (idx(this.skill) < 0) this.skill = @PKG@.SkillData.DEF;
  java.util.UUID u = this.playerRef.getUuid();
  this.pl = lines("skill:fn:prog", u);
  long c = -1L;
  try { c = @PKG@.MenuUtil.purse(u); } catch (Throwable t) { c = -1L; }
  b.set("#SkyySkpCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  if (this.tcap.length() > 0) b.set("#SkyySkpCap.Text", this.tcap);
  try { fillCells(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the skill grid failed: " + t); }
  try { fillHead(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the header failed: " + t); }
  try { fillStats(b, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the stats failed: " + t); }
  try { fillGear(b, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the gear failed: " + t); }
  try { fillPath(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the path failed: " + t); }
  try { fillTree(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the tree failed: " + t); }
  try { fillShard(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the shard card failed: " + t); }
  this.builds = this.builds + 1;
}""")
# ---- the actions (each answers with ONE packet: a redraw, a caption, a page that replaces this one, or the close)
M(skpg, r"""
public void hub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    if (tab != null && tab.length() > 0) r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("skill page: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
M(skpg, r"""
public void toInv(String mode, int rsel) {
  this.answered = true;
  @PKG@.InvPage pg = null;
  try { pg = @PKG@.InvState.openAt(this.pref, this.pst, this.playerRef, "skill page", mode, rsel); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the inventory failed: " + t); }
  if (pg == null) { if (still()) say("The inventory could not open here"); return; }
  if (!still()) finish("inventory");
}""")
M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }
  hub(@PKG@.InvData.TAB_HUB[i], @PKG@.InvData.TAB_TAB[i], @PKG@.InvData.TAB_NAME[i]);
}""")
M(skpg, r"""
public void openTree() {
  int si = idx(this.skill);
  String tn = si >= 0 ? @PKG@.SkillData.TREE[si] : this.skill;
  Object o = null;
  try { o = @PKG@.MenuUtil.bridge().get("tree:" + this.playerRef.getUuid().toString()); } catch (Throwable t) { o = null; }
  boolean has = false;
  if (o instanceof String) {
    String[] es = ((String) o).split(",");
    for (int i = 0; i < es.length; i++) { int c = es[i].indexOf(':'); if (c > 0 && es[i].substring(0, c).trim().equalsIgnoreCase(tn)) has = true; }
  }
  if (!has || @PKG@.MenuUtil.cmd("tree") == null) { hub("character", "trees", "Trees"); return; }
  this.answered = true;
  try { @CMGR@.get().handleCommand(this.playerRef, "tree " + tn.toLowerCase()); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: /tree " + tn + " failed: " + t); }
  if (!still()) { finish("tree"); return; }
  say("Opening the " + tn + " tree");
}""")
M(skpg, r"""
public void shard() {
  String sk = this.skill;
  int si = idx(sk);
  if (si < 0 || !@PKG@.SkillData.SHARD[si]) { say("There is no " + sk + " shard yet"); return; }
  long lv = level(sk);
  if (lv < (long) @PKG@.SkillData.SHARD_LV) { say("Your " + sk + " Shard unlocks at " + sk + " Lv " + @PKG@.SkillData.SHARD_LV + " (you " + (lv < 0L ? "-" : String.valueOf(lv)) + ")"); return; }
  if (@PKG@.MenuUtil.cmd("island") == null) { say("Islands are not on this server - the shard portal lives on your island"); return; }
  this.answered = true;
  shut();
  try { @CMGR@.get().handleCommand(this.playerRef, "island"); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: /island failed: " + t); }
}""")
M(skpg, r"""
public void pickZone(int z, int si) {
  int at = z * @PKG@.SkillData.ZK + si;
  if (z < 0 || z >= @PKG@.SkillData.ZN || si < 0 || si >= @PKG@.SkillData.ZK || this.zmap[at] < 0) { say("Nothing there"); return; }
  this.sel = this.zmap[at];
  this.tcap = "";
  redraw();
}""")
M(skpg, r"""
public void pickSkill(int i) {
  if (i < 0 || i >= @PKG@.SkillData.ORDER.length) { say("No such skill"); return; }
  this.skill = @PKG@.SkillData.ORDER[i];
  this.sel = -1;
  this.tcap = "";
  LAST.put(this.playerRef.getUuid(), this.skill);
  redraw();
}""")
M(skpg, r"""
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
    if (a.startsWith("sk:")) { pickSkill(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.startsWith("pz:")) { pickZone(@PKG@.InvPage.toInt(a.substring(3), -1), @PKG@.InvPage.ival(d, "SlotIndex", -1)); return; }
    if (a.equals("rq")) {
      if (@PKG@.InvCraft.fn("requip:fn:preset") == null || @PKG@.InvCraft.fn("requip:fn:presets") == null) { say("Requip presets are not on this server right now"); return; }
      toInv("r", this.presetN);
      return;
    }
    if (a.equals("vc")) {
      if (@PKG@.InvCraft.fn("acc:fn:charms") == null) { hub("character", "accessories", "Void Charms"); return; }
      toInv("v", -1);
      return;
    }
    if (a.equals("up")) { hub("smithing", "upgrade", "Upgrade"); return; }
    if (a.equals("col")) { hub("character", "collections", "Collections"); return; }
    if (a.equals("tr")) { openTree(); return; }
    if (a.equals("sh")) { shard(); return; }
    say("Pick a skill on the right");
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("skill page event '" + a + "' failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.MenuUtil.warn("skill page: the empty answer failed: " + t2); }
    }
  }
}""")
M(skpg, r"""
public void onDismiss(@REF@ ref, @ST@ st) { finish("dismissed"); }""")
M(skpg, r"""
public static @PKG@.SkillPage open(@REF@ ref, @ST@ st, @PR@ pr, String sk, String via) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  String s = idx(sk) >= 0 ? sk : @PKG@.SkillData.DEF;
  @PKG@.SkillPage pg = new @PKG@.SkillPage(pr, s, via);
  pg.pref = ref;
  pg.pst = st;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("skill page could not open for " + pr.getUsername() + ": " + t); pg.finish("open failed"); return null; }
  LAST.put(pr.getUuid(), s);
  OPENS = OPENS + 1;
  return pg;
}""")
'''
P.rep('''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''', SK_JAVA + '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''')
# Tab while the skill page is open = it closes (the hint row: "Tab / Esc Close")
P.rep('''public static void tab(@REF@ ref, @ST@ st, @PR@ pr, @PLA@ p, String via) {
  java.util.UUID u = pr.getUuid();
''', '''public static void tab(@REF@ ref, @ST@ st, @PR@ pr, @PLA@ p, String via) {
  java.util.UUID u = pr.getUuid();
  Object sp0 = p.getPageManager().getCustomPage();
  if (sp0 instanceof @PKG@.SkillPage && !((@PKG@.SkillPage) sp0).closed) { ((@PKG@.SkillPage) sp0).shut(); return; }   // 0.3.57
''')

# ---------- the inventory: the Skills tab + a skill icon click open the skill page
P.rep('''           "public boolean fneeds;", "public long froom;", "public long flim;"):''',
      '''           "public boolean fneeds;", "public long froom;", "public long flim;",
           # 0.3.57: the skill drawn in each Skills panel cell (a click opens its page)
           "public String[] skn;"):''')
P.rep('''  String cls = on ? pl[0].substring(3) : "";
  int n = @PKG@.InvData.SKN;
  if (on) {''', '''  String cls = on ? pl[0].substring(3) : "";
  int n = @PKG@.InvData.SKN;
  this.skn = new String[n];   // 0.3.57: the skill of each cell (the class skill = "Combat")
  if (on) {''')
P.rep('''          String nm = @PKG@.MenuUtil.safe(f[0]);
          if (known(f[4])) g.setItemStack(new @IS@(f[4], 1));''', '''          String nm = @PKG@.MenuUtil.safe(f[0]);
          this.skn[i] = (i == 0 && cls.length() > 0 && cls.equals(f[0])) ? "Combat" : f[0];
          if (known(f[4])) g.setItemStack(new @IS@(f[4], 1));''')
P.rep('''  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvMntI", @EVD@.of("a", "pet"), false);
  listen();''', '''  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvMntI", @EVD@.of("a", "pet"), false);
  for (int i = 0; i < @PKG@.InvData.SKN; i++) ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvSkI" + i, @EVD@.of("a", "skc:" + i), false);   // 0.3.57
  listen();''')
P.rep('''M(ipg, r"""
public void goTab(int i) {
  this.answered = true;
  if (i <= 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("You are on the Inventory tab"); return; }
''', '''# 0.3.57: the Skills tab / a skill icon = the skill page (ONE page per skill); false = it could not open (the old Skills list then)
M(ipg, r"""
public boolean openSkills(String sk) {
  @PKG@.SkillPage sp = null;
  try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, sk, "inventory"); } catch (Throwable t) { sp = null; @PKG@.MenuUtil.warn("inventory: the skill page failed: " + t); }
  if (sp == null) return false;
  this.answered = true;
  if (!still()) finish("skills");
  return true;
}""")
M(ipg, r"""
public void goTab(int i) {
  this.answered = true;
  if (i <= 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("You are on the Inventory tab"); return; }
  if (i == 1 && openSkills(@PKG@.SkillPage.lastOf(this.playerRef.getUuid()))) return;   // 0.3.57: the skill page (else the old list below)
''')
P.rep('''# ---- 0.3.53: Requip + pocket + Summon actions (each answers with ONE packet: redraw or say)
''', '''M(ipg, r"""
public void skillCell(int i) {
  String sk = (this.skn != null && i >= 0 && i < this.skn.length) ? this.skn[i] : null;
  if (sk == null || @PKG@.SkillPage.idx(sk) < 0) sk = @PKG@.SkillPage.lastOf(this.playerRef.getUuid());
  if (!openSkills(sk)) goTab(1);
}""")
# ---- 0.3.53: Requip + pocket + Summon actions (each answers with ONE packet: redraw or say)
''')
P.rep('''    if (a.equals("pet")) { goTab(2); return; }
''', '''    if (a.equals("pet")) { goTab(2); return; }
    if (a.startsWith("skc:")) { skillCell(toInt(a.substring(4), -1)); return; }   // 0.3.57: a skill icon = its page
''')
P.rep('''    @PKG@.InvState.CREATIVE.remove(u);
    @PKG@.InvPage pg = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(u);
    if (pg != null) pg.finish("disconnect");''', '''    @PKG@.InvState.CREATIVE.remove(u);
    @PKG@.SkillPage.forget(u);   // 0.3.57: the last skill shown goes with the player
    @PKG@.InvPage pg = (@PKG@.InvPage) @PKG@.InvState.PAGES.get(u);
    if (pg != null) pg.finish("disconnect");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.57: no new system / command"
_i = P.s.index
assert _i("public static @PKG@.InvPage openPage(") < _i("public static @PKG@.InvPage openAt(") < _i("public void toInv(") < _i("public static void tab(@REF@ ref")
assert _i("public static boolean known(String id)") < _i("public static @IGS@ icon(String id") and _i("public static @IGS@ rqSlot(") < _i("public void fillGear(")
assert _i("public static @PKG@.SkillPage open(") < _i("public boolean openSkills(") < _i("public void goTab(int i)") < _i("public void skillCell(") < _i("public void handleDataEvent(@REF@ ref, @ST@ st, String d) {\n  String a = val(")
assert _i("public static void forget(java.util.UUID u) { if (u != null) LAST.remove(u); }") < _i("@PKG@.SkillPage.forget(u);")
assert _i('F(sdat, "public static final String LK') < _i("public static int idx(String s)") and _i("public SkillPage(@PR@ pr") < _i("public static int idx(String s)")
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.56 harness: every 0.3.56 check
# runs again on the 0.3.57 jar, the TABS Skills check now expects the skill page; + the TAB1 section)
T.rep('''"""Harness for SkyyMenu 0.3.56 (the Furnace / Tanning panel, skill icons + XP bars, the class XP bar; tools/menu_0_3_56_patch.py).
''', '''"""Harness for SkyyMenu 0.3.57 (the Skills tab = one page per skill; the Mods list without the coin death penalty; tools/menu_0_3_57_patch.py).
GENERATED by tools/menu_0_3_57_patch.py from the 0.3.56 harness (edit the patch, not this file): every 0.3.56 check runs again on the
0.3.57 jar (TABS Skills now expects the skill page instead of /skills), plus
  TAB1 (EXECUTED on the stand-ins; Python stand-ins of SkyySkills 0.4.71 skill:fn:prog, SkyyWardrobe 0.2.14 requip:fn:presets / preset,
       SkyyCollections coll:fn:count / tier, SkyyTrees tree:<uuid>):
       OPEN    the inventory's Skills tab = the SKILL PAGE (one page packet, the inventory page forgotten), default Mining, then the last
               skill shown; a skill icon in the inventory's Skills panel = that skill's page (the class cell = Combat)
       FALL    without any new bridge every part draws and says what is missing (levels from skill:<uuid>, no XP bar, no Requip / trees /
               collections)
       PATH    Mining = Copper / Iron / Bronze ... by zone with the 5 alloys ("alloy", parents), LATER = Onyxium; a zone above your level =
               the red LOCKED title, greyed icons, "locked" (skill-page-mining-locked.png); known ids only, no metadata; the selected tier
               (default = the highest open one) in the action colour + the SELECTED line; click a tier = selected (one packet); the
               NEXT TIER line + the alloy note; Foraging / Farming paths; skills without a path = the note
       PAGE    with the bridges: XP bar + numbers, NEXT UNLOCK, the class skill in the Combat cell, the shown cell highlighted, the tool card
               (T2 Iron), the preset's armour + marks, the tree points, the shard card locked (Lv 6 / 10, bar) and open (Lv 100)
       ALL     all 12 skill pages build (one packet each, every part drawn)
       ACT     Requip = the inventory on the Requip panel of THIS preset; Inventory tab = the inventory; Market (no mod) = a caption, the page
               stays; Settings = our Settings page; Open tree = /tree <name> (or the Trees tab without /tree); the shard button: locked =
               a caption, open = /island; X closes; the Tab key closes the skill page; every answer ONE page packet
       ABIL    the Combat page's ABILITIES line from class:fn:abil (names + state, empty slots skipped); missing / null / all empty /
               a throw = a line saying so, the page still draws; no line on other skills
       FIT     no skill page packet carries a scrolling list; the build's 1080p fit + no-scroll asserts are there
       STATIC  the Mods list has no coin death penalty text; the skill page's element budget assert <= 800
The 0.3.56 harness text follows:
Harness for SkyyMenu 0.3.56 (the Furnace / Tanning panel, skill icons + XP bars, the class XP bar; tools/menu_0_3_56_patch.py).
''')
T.rep('VERSION = "0.3.56"\nJAR', 'VERSION = "0.3.57"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.55.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.56.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.55.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.56.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_56_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_57_patch.py")')
T.rep('"scratch", "inv7", "menu"', '"scratch", "tab1", "menu"')
T.rep('ADDED = []\n', 'ADDED = ["SkillData", "SkillPage"]   # 0.3.57: the skill page\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.56:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.57: the Skills tab opens the skill page; a skill icon too; Tab closes the skill page; the Mods list text
    "InvPage": ["+f skn", "+m openSkills", "+m skillCell", "~m build", "~m fillProg", "~m goTab", "~m handleDataEvent"],
    "InvState": ["+m openAt", "~m tab"],
    "InvBye": ["~m accept"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.56"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.57"') == 1, "S VERSION")
    # 0.3.57: the Mods list without the coin death penalty (none since SkyyCoins 0.1.12); the skill page's element budget
    K.check("/deathpenalty 5%" not in g and "When you die you lose" not in g and "Bank coins are never lost when you die" not in g
            and "Change the death penalty in chat" not in g and "By default you keep your coins when you die." in g,
            "TAB1 STATIC the Mods list has no coin death penalty text ('By default' - the Coins Death rows can still be turned back on)")
    # 0.3.57 fix: the page fits one 1080p screen with no scrolling (Skyy: "all fit so there is no zooming or scrolling")
    K.check("0.3.57: the skill page fits one 1080p screen" in g and "0.3.57: the skill page never scrolls" in g,
            "TAB1 STATIC the build asserts the page fits 1080 (MAX_PAGE_H, both columns sum to the body) and has no scrolling list")
    ms_ = re.search(r"SK_ELEMENTS <= (\\d+)", g)
    K.check(ms_ is not None and int(ms_.group(1)) <= 800, "TAB1 STATIC the skill page's element budget assert is <= 800 (the ~1,600 client budget)")''')
T.rep('''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2, "PAGE: 49 bindings (0.3.55:''', '''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12, "PAGE: 61 bindings (0.3.57: + the 12 skill icons' clicks = their skill pages; 0.3.55:''')
T.rep('''    K.check([str(E.CM.lines.get(i_)) for i_ in range(l0, int(E.CM.lines.size()))] == ["skills"] and [cap_of(x_) for x_ in pages(PI, f0)] == ["Opening Skills"]
            and cur == pg, "TABS Skills: the hub tab's command (/skills as the player - SkyySkills opens its page over ours), ONE caption packet")
    pg.onDismiss(PI.ref, PI.st)                         # what the engine does when the Skills page replaces ours
''', '''    K.check([str(E.CM.lines.get(i_)) for i_ in range(l0, int(E.CM.lines.size()))] == [] and len(pages(PI, f0)) == 1
            and cur is not None and str(cur.getClass().getSimpleName()) == "SkillPage", "TABS Skills (0.3.57): the SKILL PAGE opens (no /skills command), ONE page packet")
''')
assert 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.55.jar")' not in T.s, "0.3.57 harness: an old line is still there"


HARNESS_TAB1 = r"""    # ---- TAB1 (0.3.57; Skyy 11-21 "build and deploy everything on your list"): the Skills tab = ONE PAGE PER SKILL
    SKP, SKD = JV("SkillPage"), JV("SkillData")
    INTc = JClass("java.lang.Integer")
    uk_ = str(PK.pr.getUuid())
    for k_ in ("skill:fn:prog", "requip:fn:presets", "requip:fn:preset", "requip:fn:act", "coll:fn:count", "coll:fn:tier", "acc:fn:charms", "wardrobe:fn:list", "class:fn:abil"):
        BR.remove(k_)
    BR.remove("tree:" + uk_)
    SCROLLS = []   # pages whose packet carries a scrolling list (must stay empty: one 1080p screen, no scrolling)
    BR.put("skill:" + uk_, "Mining:12,Farming:5")
    SKP.LAST.clear()
    E.CM.cmds.remove("tree")
    visS = lambda c_, k_: sval(c_, "#SkyySkp%s.Visible" % k_) in (True, "true")
    ORD = [str(x_) for x_ in list(SKD.ORDER)]
    K.eq(ORD, ["Combat", "Mining", "Foraging", "Farming", "Fishing", "Smithing", "Alchemy", "Cooking", "Acrobatics", "Exploration", "Ranching", "Orchard"],
         "TAB1 the 12 skills, Combat (= your class, Skyy 'class is combat.') first")

    def parts_ok(cm_):
        return all(k_ in cm_ for k_ in ("#SkyySkpCb11.Text", "#SkyySkpHdT.Text", "#SkyySkpHdU1.Text", "#SkyySkpSn0.Text", "#SkyySkpGtN.Text", "#SkyySkpGaI.Slots",
                                        "#SkyySkpPaT.Text", "#SkyySkpTrP.Text", "#SkyySkpTl0.Text", "#SkyySkpShGo.Text", "#SkyySkpShSG.Visible"))

    def sk_ev(obj, what):
        f_ = len(E.sent(PK))
        cur_ = PK.pm.getCustomPage()
        cur_.handleDataEvent(PK.ref, PK.st, json.dumps(obj))
        ps_ = pages(PK, f_)
        K.eq(len(ps_), 1, what + ": exactly ONE page packet")
        return ps_[0] if ps_ else None
    # OPEN + FALL: no new bridge at all
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:1"}')
    pk_ = pages(PK, f0_)
    SP = PK.pm.getCustomPage()
    K.check(len(pk_) == 1 and SP is not None and str(SP.getClass().getSimpleName()) == "SkillPage" and bool(pgI_.closed) and ST.PAGES.get(PK.pr.getUuid()) is None,
            "TAB1 OPEN the Skills tab = the SKILL PAGE (ONE page packet), the inventory page forgotten")
    cm = cmap(pk_[0]) if pk_ else {}
    K.check(parts_ok(cm) and sval(cm, "#SkyySkpHdT.Text") == "MINING" and str(SP.skill) == "Mining" and nometa(pk_[0]),
            "TAB1 OPEN the default page = Mining (Skyy: Mining first), every part drawn, no grid metadata")
    K.check(sval(cm, "#SkyySkpHdLv.Text") == "12" and "0.4.71" in (sval(cm, "#SkyySkpHdXn.Text") or "") and "#SkyySkpHdB" not in cm
            and sval(cm, "#SkyySkpCl1.Text") == "Lv 12" and sval(cm, "#SkyySkpCl0.Text") == "pick a class" and sval(cm, "#SkyySkpCb0.Text") == "Combat",
            "TAB1 FALL no skill:fn:prog: the levels from skill:<uuid>, no XP bar, the Combat cell says pick a class (%s)" % sval(cm, "#SkyySkpHdXn.Text"))
    K.check(sval(cm, "#SkyySkpGaL.Text") == "Requip presets are not on this server" and sval(cm, "#SkyySkpTrP.Text") == "Trees are not on this server"
            and "collections are not on this server" in (sval(cm, "#SkyySkpPaS.Text") or "") and sval(cm, "#SkyySkpStW.Text") == "Your stats now"
            and str(sval(cm, "#SkyySkpSn0.Text")) in ("MINING", "GENERAL"),
            "TAB1 FALL Requip / trees / collections missing = said on the page; the stats rows drawn (%s)" % sval(cm, "#SkyySkpSn0.Text"))
    K.eq([sval(cm, "#SkyySkpZn0%d.Text" % k_) for k_ in range(3)] + [sval(cm, "#SkyySkpZn1%d.Text" % k_) for k_ in range(3)] + [sval(cm, "#SkyySkpZn50.Text")],
         ["Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Onyxium"], "TAB1 PATH Mining = the metal ladder by zone with the alloys, Onyxium LATER")
    K.eq([sval(cm, "#SkyySkpZv0%d.Text" % k_) for k_ in range(3)] + [sval(cm, "#SkyySkpZv12.Text")], ["Lv 1", "Lv 8", "Lv 15  locked", "Lv 35  locked"],
         "TAB1 PATH the level lines (Mining 12: Bronze + zone 2 locked)")
    K.check(sval(cm, "#SkyySkpZt0.Text") == "ZONE 1" and visS(cm, "Zt0") and not visS(cm, "Zk0") and visS(cm, "Zk1") and not visS(cm, "Zt1")
            and sval(cm, "#SkyySkpZk1.Text") == "ZONE 2  LOCKED" and sval(cm, "#SkyySkpZk5.Text") == "LATER  LOCKED" and sval(cm, "#SkyySkpZl1.Text") == "Mining 20+",
            "TAB1 PATH LOCK zone 1 open; zone 2 (Mining 20+) and LATER above Mining 12 = the red LOCKED title (skill-page-mining-locked.png)")
    g0_, g1_ = cm.get("#SkyySkpZg0.Slots", ""), cm.get("#SkyySkpZg1.Slots", "")
    K.notes.append("TAB1 zone grid 1 (locked): %s" % g1_[:400])
    K.check("Ingredient_Bar_Iron" in g0_ and "Ingredient_Bar_Copper" not in g0_ and "T2 Iron" in g0_ and "Opens at Mining Lv 8" in g0_,
            "TAB1 PATH icons only for ids the server knows (Copper Ingot = name only here), the hover = tier tag + level")
    K.check(g1_.count('"IsItemUncraftable": true') == 3 and g0_.count('"IsItemUncraftable": true') == 1,
            "TAB1 PATH the locked tiers' icons are greyed (uncraftable): all 3 of zone 2, only Bronze in zone 1")
    K.check(visS(cm, "Zs01") and not visS(cm, "Zn01") and str(sval(cm, "#SkyySkpPaS.Text")).startswith("SELECTED  Iron  (T2 Iron)"),
            "TAB1 PATH the default pick = the highest open tier (Iron), in the action colour")
    K.check(str(sval(cm, "#SkyySkpPaN.Text")).startswith("NEXT TIER  Bronze alloy at Mining 15  (you 12)") and "ALLOY = smelted" in str(sval(cm, "#SkyySkpPaN.Text"))
            and sval(cm, "#SkyySkpHdU1.Text") == "Lv 15: Bronze alloy", "TAB1 PATH the NEXT TIER line + the alloy note, NEXT UNLOCK")
    K.check(visS(cm, "ShSG") and not visS(cm, "ShSR") and sval(cm, "#SkyySkpShGo.Text") == "Go to my island" and ("Width: %d," % int(SKD.SHBW)) in cm.get("#SkyySkpShB", ""),
            "TAB1 the shard card at Mining 12 = open (green), full bar, Go to my island")
    # PAGE: with the bridges (Mining Lv 6 = the locked picture)
    PROG = "ok|Swordsmanship\nSwordsmanship|23|1240|2000|Weapon_Sword_Iron|#e0b060\nMining|6|410|900|Tool_Pickaxe_Iron|#aaaaaa\nForaging|5|0|100|Wood_Oak_Trunk|#55aa55\nFarming|100|0|0|Rock_Stone|#ffffff"
    BR.put("skill:fn:prog", Fn(lambda o: PROG))
    BR.put("profile:class:" + uk_, "Knight")
    BR.put("requip:fn:presets", Fn(lambda o: "ok|0|2|18\n0|Combat|3|0|1|1\n1|Mining|2|1|1|1"))

    def f_pre(o):
        n_ = int(o[1])
        if n_ == 1:
            return "\n".join(["ok|1|Mining|0|0", "0|on|Armor_Iron_Head|Head", "1|missing|Armor_Iron_Chest|Chest", "2|keep||Hands", "3|stored|Armor_Iron_Legs|Legs",
                              "4|on|Tool_Pickaxe_Iron|Hotbar 1"] + ["%d|keep||Hotbar %d" % (k_, k_ - 3) for k_ in range(5, 13)] + ["pet|keep||", "mount|keep||"])
        return "\n".join(["ok|0|Combat|1|0", "0|on|Armor_Iron_Head|Head", "4|on|Weapon_Sword_Iron|Hotbar 1"])
    BR.put("requip:fn:preset", Fn(f_pre))
    BR.put("requip:fn:act", Fn(lambda o: "+done"))
    BR.put("coll:fn:count", Fn(lambda o: LONGc(365) if str(o[1]) == "Iron" else LONGc(82)))
    BR.put("coll:fn:tier", Fn(lambda o: INTc.valueOf(2)))
    BR.put("tree:" + uk_, "Mining:5/6,Class:2/23,Foraging:0/5")
    p_ = sk_ev({"a": "sk:1"}, "TAB1 PAGE Mining with the bridges")
    cm = cmap(p_) if p_ else {}
    hb_ = int(SKD.HDBW)
    K.check(sval(cm, "#SkyySkpHdXa.Text") == "Lv 6  ->  7" and sval(cm, "#SkyySkpHdXn.Text") == "410 / 900 XP" and ("Width: %d," % (410 * hb_ // 900)) in cm.get("#SkyySkpHdB", "")
            and sval(cm, "#SkyySkpHdLv.Text") == "6", "TAB1 PAGE the header: level box, Lv 6 -> 7, 410 / 900 XP, the XP bar fill")
    K.eq(sval(cm, "#SkyySkpHdU1.Text"), "Lv 8: Iron + the Iron collection", "TAB1 PAGE NEXT UNLOCK = the next tier")
    K.eq([sval(cm, "#SkyySkpZv0%d.Text" % k_) for k_ in range(3)], ["Lv 1  82", "Lv 8  locked", "Lv 15  locked"], "TAB1 PATH the collection count on an open tier, locked above Mining 6")
    K.check(str(sval(cm, "#SkyySkpPaS.Text")).startswith("SELECTED  Copper  (T1 Copper)  82 collected - collection II"), "TAB1 PATH the SELECTED line (count + tier) (%s)" % sval(cm, "#SkyySkpPaS.Text"))
    K.check("Tool_Pickaxe_Iron" in cm.get("#SkyySkpGtI.Slots", "") and sval(cm, "#SkyySkpGtT.Text") == "T2 Iron" and sval(cm, "#SkyySkpGtL.Text") == "From your Mining preset"
            and "Armor_Iron_Head" in cm.get("#SkyySkpGaI.Slots", "") and sval(cm, "#SkyySkpGaS.Text") == "Mining set  1 / 4 on you"
            and sval(cm, "#SkyySkpGaL.Text") == "1 missing - Requip shows where" and sval(cm, "#SkyySkpStW.Text") == "Your stats now - your Mining set is not on" and nometa(p_),
            "TAB1 PAGE the tool card (preset pickaxe, T2 Iron) + the preset's armour with its marks, the stats line says the set is not worn")
    K.eq(sval(cm, "#SkyySkpTrP.Text"), "Points  1 free   5 spent of 6", "TAB1 PAGE the Mining tree points (tree:<uuid>)")
    K.eq(sval(cm, "#SkyySkpTrA.Text"), "", "TAB1 PAGE no ABILITIES line on a non-Combat page")
    cb_ = int(SKD.CBW)
    K.check(sval(cm, "#SkyySkpCl0.Text") == "Lv 23" and "Weapon_Sword_Iron" in cm.get("#SkyySkpCi0.Slots", "") and "Your class skill: Swordsmanship" in cm.get("#SkyySkpCi0.Slots", "")
            and str(SKD.ST_CBSEL) in mk_of(p_, "SkyySkpCb1") and str(SKD.ST_CB) in mk_of(p_, "SkyySkpCb0")
            and ("Width: %d," % (410 * cb_ // 900)) in cm.get("#SkyySkpCt1", "") and "Tool_Pickaxe_Iron" in cm.get("#SkyySkpCi1.Slots", ""),
            "TAB1 PAGE the grid: Combat = the class skill (Lv 23), the shown Mining cell highlighted, its XP bar")
    K.check(visS(cm, "ShSR") and not visS(cm, "ShSG") and sval(cm, "#SkyySkpShSR.Text") == "Mining Shard - locked" and sval(cm, "#SkyySkpShU.Text") == "Unlocks at Mining Lv 10"
            and ("Width: %d," % (6 * int(SKD.SHBW) // 10)) in cm.get("#SkyySkpShB", "") and sval(cm, "#SkyySkpShGo.Text") == "Locked - Mining Lv 10",
            "TAB1 PAGE the shard card LOCKED below Mining 10 (Skyy 'lets lock it to lvl 10'), the level progress bar")
    l0_ = int(E.CM.lines.size())
    p_ = sk_ev({"a": "sh"}, "TAB1 ACT the locked shard button")
    K.check("unlocks at Mining Lv 10 (you 6)" in (sval(cmap(p_), "#SkyySkpCap.Text") or "") and int(E.CM.lines.size()) == l0_, "TAB1 ACT a locked shard = a caption, no command")
    # PATH clicks
    p_ = sk_ev({"a": "pz:0", "SlotIndex": 1}, "TAB1 PATH click Iron")
    K.check(str(sval(cmap(p_), "#SkyySkpPaS.Text")).startswith("SELECTED  Iron  (T2 Iron)  365 collected - collection II  - opens at Lv 8") and visS(cmap(p_), "Zs01"),
            "TAB1 PATH a click = that tier selected (one packet) (%s)" % sval(cmap(p_), "#SkyySkpPaS.Text"))
    p_ = sk_ev({"a": "pz:3", "SlotIndex": 2}, "TAB1 PATH click Cinder")
    K.check(str(sval(cmap(p_), "#SkyySkpPaS.Text")).startswith("SELECTED  Cinder  (T12 Cinder)  alloy of Adamantite + Slag"), "TAB1 PATH an alloy: its parents (%s)" % sval(cmap(p_), "#SkyySkpPaS.Text"))
    p_ = sk_ev({"a": "pz:5", "SlotIndex": 2}, "TAB1 PATH click an empty cell")
    K.eq(sval(cmap(p_), "#SkyySkpCap.Text"), "Nothing there", "TAB1 PATH an empty cell = a caption")
    # ALL: every skill's page builds
    for i_, s_ in enumerate(ORD):
        p_ = sk_ev({"a": "sk:%d" % i_}, "TAB1 ALL the %s page" % s_)
        cm = cmap(p_) if p_ else {}
        K.check(parts_ok(cm) and sval(cm, "#SkyySkpHdT.Text") == s_.upper() and str(SP.skill) == s_ and nometa(p_), "TAB1 ALL the %s page builds, every part drawn" % s_)
        if s_ == "Foraging":
            K.check(sval(cm, "#SkyySkpPaT.Text") == "COLLECTIONS - WOOD PATH" and sval(cm, "#SkyySkpZn00.Text") == "Oak" and visS(cm, "Zr"), "TAB1 PATH Foraging = the wood path (Oak first)")
        if s_ == "Farming":
            K.check(sval(cm, "#SkyySkpPaT.Text") == "COLLECTIONS - CROP PATH" and sval(cm, "#SkyySkpZn00.Text") == "Wheat" and sval(cm, "#SkyySkpZn42.Text") == "Mushroom"
                    and visS(cm, "ShSG") and sval(cm, "#SkyySkpHdXn.Text") == "MAX LEVEL", "TAB1 PATH Farming = the crop path; Lv 100 = MAX LEVEL, the shard open")
        if s_ == "Fishing":
            K.check(visS(cm, "Np") and not visS(cm, "Zr") and sval(cm, "#SkyySkpShS.Text") == "No Fishing shard yet", "TAB1 PATH no path for Fishing = the note; no shard card")
        if s_ == "Combat":
            K.check(sval(cm, "#SkyySkpHdC.Text") == "Class: Knight - Swordsmanship" and sval(cm, "#SkyySkpHdLv.Text") == "23" and sval(cm, "#SkyySkpTrP.Text") == "Points  21 free   2 spent of 23"
                    and visS(cm, "ShSG") and visS(cm, "Np"), "TAB1 ALL Combat = your class (Skyy 'class is combat.'): class line, class level, the Class tree's points (%s)" % sval(cm, "#SkyySkpHdC.Text"))
            K.eq(sval(cm, "#SkyySkpTrA.Text"), "ABILITIES  Classes are not on this server", "TAB1 FALL the Combat ABILITIES line without class:fn:abil")
        if p_ is not None and any("Scrolling" in str(c_.text or "") for c_ in cmds_of(p_)):
            SCROLLS.append(s_)
        K.notes.append("TAB1 %s: %d commands in the page packet" % (s_, len(cmds_of(p_)) if p_ else -1))
    K.eq(SCROLLS, [], "TAB1 FIT no skill page packet carries a scrolling list (one 1080p screen, Skyy 'no zooming or scrolling')")
    # the Combat page's ABILITIES (Skyy 11-14: "the COMBAT skill page holds your class (abilities, class tree, combat gear)") - class:fn:abil read only
    OBJA = lambda xs: _JA(JClass("java.lang.Object"))(xs)
    JSTR = JClass("java.lang.String")
    AB = [JSTR("Shield Bash"), LONGc(0), LONGc(8000), JSTR("ready"), JSTR("Charge"), LONGc(3000), LONGc(9000), JSTR("cooldown"),
          JSTR(""), LONGc(0), LONGc(0), JSTR("empty"), JSTR("Bulwark"), LONGc(0), LONGc(0), JSTR("locked")] + [None] * 32
    ABQ = []
    BR.put("class:fn:abil", Fn(lambda o: (ABQ.append(str(o)), OBJA(AB))[1]))
    p_ = sk_ev({"a": "sk:0"}, "TAB1 Combat with class:fn:abil")
    K.check(sval(cmap(p_), "#SkyySkpTrA.Text") == "ABILITIES  Shield Bash (ready)    Charge (cooldown)    Bulwark (locked)" and ABQ == [uk_],
            "TAB1 PAGE Combat = the ABILITIES line (the 4 slots' names + state, the empty slot skipped; asked with your UUID) (%s)" % sval(cmap(p_), "#SkyySkpTrA.Text"))
    BR.put("class:fn:abil", Fn(lambda o: None))
    p_ = sk_ev({"a": "sk:0"}, "TAB1 Combat, a class without abilities")
    K.eq(sval(cmap(p_), "#SkyySkpTrA.Text"), "ABILITIES  your class's abilities show here once you have a class with abilities", "TAB1 FALL class:fn:abil = null: the ABILITIES line says so")
    BR.put("class:fn:abil", Fn(lambda o: OBJA([JSTR("")] * 16)))
    p_ = sk_ev({"a": "sk:0"}, "TAB1 Combat, no ability slotted")
    K.eq(sval(cmap(p_), "#SkyySkpTrA.Text"), "ABILITIES  no ability in your slots yet - Open tree to pick them", "TAB1 FALL every slot empty: the ABILITIES line says so")
    BR.put("class:fn:abil", Fn(lambda o: 1 / 0))
    p_ = sk_ev({"a": "sk:0"}, "TAB1 Combat, class:fn:abil throws")
    K.check(p_ is not None and parts_ok(cmap(p_)) and "ABILITIES  your class" in str(sval(cmap(p_), "#SkyySkpTrA.Text")), "TAB1 FALL class:fn:abil throws: the page still draws")
    BR.remove("class:fn:abil")
    sk_ev({"a": "sk:11"}, "TAB1 back to Orchard")
    # ACT: the buttons
    p_ = sk_ev({"a": "tab:3"}, "TAB1 ACT Market (no market mod)")
    K.check("Market is not on this server right now" in (sval(cmap(p_), "#SkyySkpCap.Text") or "") and PK.pm.getCustomPage() == SP, "TAB1 ACT Market = a caption, the page stays")
    p_ = sk_ev({"a": "tr"}, "TAB1 ACT Open tree without /tree")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ == SP or (cur_ is not None and bool(SP.closed)), "TAB1 ACT Open tree without /tree = the Character hub's Trees route (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    if cur_ != SP:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
        SP = SKP.open(PK.ref, PK.st, PK.pr, "Mining", "test")
        E.pump(PK)
    E.CM.cmds.put("tree", E.CM.cmds.get("island"))
    sk_ev({"a": "sk:1"}, "TAB1 back to Mining")
    l0_ = int(E.CM.lines.size())
    p_ = sk_ev({"a": "tr"}, "TAB1 ACT Open tree")
    K.check([str(E.CM.lines.get(i_)) for i_ in range(l0_, int(E.CM.lines.size()))] == ["tree mining"] and sval(cmap(p_), "#SkyySkpCap.Text") == "Opening the Mining tree",
            "TAB1 ACT Open tree = /tree mining as the player")
    E.CM.cmds.remove("tree")
    p_ = sk_ev({"a": "rq"}, "TAB1 ACT Requip")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "r" and int(cur_.rsel) == 1 and bool(SP.closed)
            and "#SkyyInvRa.Slots" in cmap(p_) and "#SkyyInvCg.Slots" not in cmap(p_), "TAB1 ACT Requip = the inventory on the Requip panel of the Mining preset (one page packet)")
    # the inventory's skill icons: cell 0 = the class = Combat, cell 1 = Mining
    p_ = one(ev(PK, {"a": "skc:0"}), "TAB1 OPEN the class icon in the inventory")
    SP = PK.pm.getCustomPage()
    K.check(SP is not None and str(SP.getClass().getSimpleName()) == "SkillPage" and str(SP.skill) == "Combat", "TAB1 OPEN the inventory's class skill icon = the Combat page")
    p_ = sk_ev({"a": "tab:0"}, "TAB1 ACT the Inventory tab")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_), "TAB1 ACT the Inventory tab = the inventory screen")
    p_ = one(ev(PK, {"a": "skc:1"}), "TAB1 OPEN the Mining icon in the inventory")
    SP = PK.pm.getCustomPage()
    K.check(SP is not None and str(SP.skill) == "Mining", "TAB1 OPEN the inventory's Mining icon = the Mining page")
    p_ = sk_ev({"a": "sk:3"}, "TAB1 Farming (Lv 100)")
    l0_ = int(E.CM.lines.size())
    SP.handleDataEvent(PK.ref, PK.st, '{"a":"sh"}')
    K.check(PK.pm.getCustomPage() is None and bool(SP.closed) and [str(E.CM.lines.get(i_)) for i_ in range(l0_, int(E.CM.lines.size()))] == ["island"],
            "TAB1 ACT the open shard's button = the page closes, /island (today's shard entry: the portal on your island)")
    K.eq(str(SKP.lastOf(PK.pr.getUuid())), "Farming", "TAB1 the last skill shown is remembered (the Skills tab opens it again)")
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:1"}')
    SP = PK.pm.getCustomPage()
    K.check(SP is not None and str(SP.skill) == "Farming", "TAB1 OPEN the Skills tab = the last skill shown")
    p_ = sk_ev({"a": "tab:6"}, "TAB1 ACT Settings")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(SP.closed), "TAB1 ACT Settings = our Settings page")
    PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    SP = SKP.open(PK.ref, PK.st, PK.pr, "Mining", "test")
    E.pump(PK)
    ST.tab(PK.ref, PK.st, PK.pr, PK.pl, "test")
    K.check(PK.pm.getCustomPage() is None and bool(SP.closed), "TAB1 ACT the Tab key closes the skill page")
    SP = SKP.open(PK.ref, PK.st, PK.pr, "Nope", "test")
    E.pump(PK)
    K.check(SP is not None and str(SP.skill) == "Mining", "TAB1 an unknown skill name = the Mining page")
    SP.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(PK.pm.getCustomPage() is None and bool(SP.closed), "TAB1 ACT X closes the page")
    SKP.forget(PK.pr.getUuid())
    K.eq(str(SKP.lastOf(PK.pr.getUuid())), "Mining", "TAB1 forget (disconnect) = back to the default")
    for k_ in ("skill:fn:prog", "requip:fn:presets", "requip:fn:preset", "requip:fn:act", "coll:fn:count", "coll:fn:tier", "profile:class:" + uk_, "tree:" + uk_):
        BR.remove(k_)
    E.pump(PK)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_TAB1 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
if T.dst:
    T.finish()
