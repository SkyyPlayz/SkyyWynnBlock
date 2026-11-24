"""Derive SkyyMenu/build_skyymenu_0.3.74.py + SkyyMenu/test_skyymenu_0.3.74.py from the SET pin SkyyMenu 0.3.73 (generated - never re-run
its patch). Run:  python tools/menu_0_3_74_patch.py   then   python SkyyMenu/build_skyymenu_0.3.74.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.74.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyQuests 0.4.5 (tools/quests_0_4_5_patch.py: quest:fn:act), SkyyCollections 0.2.37
(tools/collections_0_2_37_patch.py: coll:fn:act), SkyyExploration 0.3.5 (tools/exploration_0_3_5_patch.py: explore:fn:act) and SkyyIslands
0.5.27 (tools/islands_0_5_27_patch.py: island:fn:act); with an older jar that view says which version it needs (the rest of the World tab
works as 0.3.73).

0.3.74 (2026-11-24, round oldmenu6) = OLD MENU FOLLOW-UP: THE WORLD TAB'S QUESTS / COLLECTIONS / EXPLORE / ISLAND VIEWS. Skyy's words
(docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu
compleatly, so instead of adding things like the full tree button, just build it all into the new system and remove the old "Full tree"";
2026-11-24 "keep building". Each part calls the SAME server code as the old page (through the four bridges; no duplicated rule, no new number):
  THE WORLD SCREEN = THE FRAME + ONE SECTION PER PACKET (as the Market / Social screens): 0 = the frame (top bar, hint row), H = the home
      cards, Q = Quests, C = Collections, E = Explore, I = Island. Every view: one sub-tab row World | Quests | Collections | Explore | Island
      (research/Menu-Pattern.md: the open one selected, no back button - World on it = the cards), Refresh, a head line.
  QUESTS (world:quests gone): the Quests card's Quest log, the inventory's Right now quest row + its quest button = the QUESTS VIEW
      (quest:fn:act): the quest lines in the page's order (tracked / open / locked with how to start it / all done; x / y + a bar; 11 a page),
      the picked line (status, Track this line / Stop tracking with the SHOWN state, the daily reset), Open | Done (the page's tabs: open,
      ready, next in line, then skipped / done), 6 tasks a page: tier tag + name, the state word in its colour, progress + bar, where,
      reward, hint, Claim (ready) / Skip / Unskip (the SHOWN state); Claim all (n) and Hide / Show tutorial.
  COLLECTIONS (character:collections gone): the codex card's Collections (Combat picked) and the skill page's Collections (that skill's
      category) = the COLLECTIONS VIEW (coll:fn:act): the totals line + the 4 category cards (Open); a category = its collection cards (15 a
      page: tier + progress, the Next line, a bar, View); a collection = the detail: category / curve / from, the progress bar, the coin
      unlock offer (Buy sends the SHOWN tier + price; the first press = the bridge's '=Click Buy again ...', the same press again pays) or
      why not, every tier (DONE / BOUGHT / NEXT / LOCKED / NEW in their colours, the threshold, the rewards), the recipes in the page's order
      (tier, then name) with Craft (the crafting page opens in place of this screen); drawing a collection with NEW tiers = 'seen' once.
  EXPLORE (world:explore gone): the Explore card's button = the EXPLORE VIEW (explore:fn:act): the level line; Overview | Zones | Titles |
      Checklist (the page's tabs): the 8 cards, the owed / quiet / note lines; the region groups left / right with found / XP; every title
      (in use / earned / locked colours, what earns it, Use, No title); the islands (here first) with Show = that island's checklist rows +
      the reward line.
  ISLAND (world:island gone): the island card's Island settings = the ISLAND VIEW (island:fn:act): the role line; Overview | Members |
      Permissions | Visitors | Island (the page's 5 tabs): OVERVIEW (no island = Create my island; the owner box; Go to island; a live co-op
      invite with Accept / Decline; Disband co-op 2 presses, Reset island 3 presses with the page's words, Leave island 2 presses; the closed
      note), MEMBERS (typed name: Invite to co-op / Trust, Enter = the bridge's note; co-op rows with Promote / Demote / Kick (2 presses,
      'Sure?') at owner rank; invited; trusted rows with Untrust), PERMISSIONS (the grid: a cell = perm NNx|<shown>; Reset to defaults 2
      presses; read-only rows for players who cannot edit), VISITORS (mode, limit - / +, visit ping with the SHOWN state; players on the island
      with Expel / Trust / Ban (2 presses); bans with Unban), ISLAND (PvP / Mob spawning toggles with the SHOWN state). Create / Go to island
      (and a confirmed Leave / Reset) close the screen as the bridge does. The menu sends island:fn:act refresh when the island view opens,
      on every island tab change, when the view is left and when the screen closes (the bridge keeps its arm per player - fix isl1fix).
  NEVER A VALUE THE PLAYER DID NOT SEE: every toggle sends the drawn state (track / skip / notify / pvp / spawning / a grid cell), Buy the drawn
      tier + price, a title its drawn index + id, every row button the drawn row's key / uuid and only where that drawing showed the button (a
      forged one = a caption, no call). '=' answers (a question / a stale state) show in the caption; the same press again confirms (the bridges
      keep the arm, the next drawing shows the armed word). A null answer (not on the world thread) = "That could not run here - nothing
      changed."; a view's click on another view / the home cards = a caption, no call.
  SAFETY: every bridge act carries the page token (an older drawing = "The page changed", nothing runs) and the read's own token + profile key
      (the bridges answer "=Your profile changed ..." / "=The quest list changed ..." / "=The collections changed ..." / "=Your exploration
      file changed ..." / "=Your island changed ..."); the bridges' 350 ms guard "=One moment." shows as the caption.
  CONTRACT NOTE (explore:fn:act): the t| line carries no title id; the bridge's id = the title's name, lower case, spaces removed (ExpDefs.T_ID
      = TITLES[i][0] = that for every title today); a renamed title = the bridge's "=The titles changed" - nothing changes.
New: no class / command / system / picture / lang key / setting / saved data. OLD_LEFT: world:quests, world:explore, world:island,
character:collections out (11 -> 7).
ROLLBACK to 0.3.73: safe alone (nothing saved; the Quest log / Explore page / Island settings / Collections links come back). Each bridge mod
rolls back alone (Menu then names the version that view needs).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.73.py"), os.path.join(MOD, "build_skyymenu_0.3.74.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.73.py"), os.path.join(MOD, "test_skyymenu_0.3.74.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.73"\n') and P.has("OLD_LEFT = sorted(set([") and P.has('MT + "HvBr"') and not P.has('WT + "Qv"'), "not the generated SkyyMenu 0.3.73 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.73: OLD MENU FOLLOW-UP - THE GUILD + AUCTION HOUSE VIEWS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.74: OLD MENU FOLLOW-UP - THE WORLD TAB'S VIEWS: Quest log / the inventory's quest row = the Quests view (lines, tasks, Open / Done, Track,
       Skip / Unskip, Claim, Claim all, Hide / Show tutorial - SkyyQuests 0.4.5 quest:fn:act); Collections (World + skill page) = the
       Collections view (categories, cards, a collection's tiers + recipes + Craft + the coin Buy - SkyyCollections 0.2.37 coll:fn:act);
       the Explore card = the Explore view (overview, zones, titles + Use, checklists - SkyyExploration 0.3.5 explore:fn:act); Island
       settings = the Island view (the island menu's 5 tabs - SkyyIslands 0.5.27 island:fn:act); OLD_LEFT lost 4 rows (notes:
       tools/menu_0_3_74_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.74.py.
0.3.73: OLD MENU FOLLOW-UP - THE GUILD + AUCTION HOUSE VIEWS''')
P.rep('VERSION = "0.3.73"\n', 'VERSION = "0.3.74"\n')

# ======================================================================= the HOME cards: the buttons open the views
P.rep('''    "qnote": "Dailies, weeklies, story and side quests: Quest log.",
    "ihint": "Members, visitors, PvP and the name: Island settings.",''', '''    "qnote": "Every quest line, its tasks and rewards: Quest log.",   # 0.3.74: the quests view
    "ihint": "Members, visitors, permissions, PvP: Island settings.",''')
P.rep('''    ap.append(("#" + ex, G_.glass_button(WT + "Ego", "Explore page", "secondary", w=180, h=34, size=14, anchor={"top": 10})))''',
      '''    ap.append(("#" + ex, G_.glass_button(WT + "Ego", "Explore", "secondary", w=180, h=34, size=14, anchor={"top": 10})))   # 0.3.74: the explore view''')
P.rep('''    "c3": "Combat collections - each tier pays a reward.",''', '''    "c3": "Combat collections - open Collections for each tier.",''')

# ======================================================================= the VIEWS (Q quests, C collections, E explore, I island) + the section letters
WV_PY = r'''

# ---- 0.3.74 (oldmenu6): THE WORLD SCREEN'S VIEWS - each one fills the body's place (the frame, the top bar and the hint row stay). The page
# data carries a section letter per line: 0 = always, H = the home cards, Q = quests, C = collections, E = explore, I = island; build()
# appends the frame + the current one only. Sub-tabs (research/Menu-Pattern.md: one row, the open one selected, no back button).
WV_VI = IV_IW - 20                                          # a view's inner width (1536)
WV_SBW, WV_RFW = 150, 120                                   # a sub-tab, Refresh
WV_SUBS = ["World", "Quests", "Collections", "Explore", "Island"]
WV_HCW = WV_VI - 200 - len(WV_SUBS) * (WV_SBW + 6) - WV_RFW - 6   # the head's count line (430)
WV_BH = IV_BODY_H - 20 - 34 - 24 - 6                        # a view's body under its head + head line (760)
WV_KBW = 160                                                # a view's own tab row (run time)
# QUESTS
QL_W, QL_N, QL_RH = 500, 11, 54                             # the quest lines column, 11 a page
QL_IW = QL_W - 16
QL_TW = QL_IW - 12 - 90 - 6
QR_W = WV_VI - QL_W - 10                                    # the picked line (1026)
QR_IW = QR_W - 16
QT_N, QT_RH, QT_BW = 6, 78, 120                             # 6 tasks a page
QT_TW = QR_IW - 16 - 2 * (QT_BW + 6) - 8                    # a task row's text column
QT_BARW = 300
QT_SW = 170                                                 # the state word
QT_STATES = [("Open", "text"), ("Ready to claim", "xp"), ("Done", "green"), ("Skipped", "dim"), ("Next in line", "accentHi")]
# COLLECTIONS
CK_N, CK_H = 4, 96                                          # the category cards
CK_W = (WV_VI - (CK_N - 1) * 10) // CK_N                    # 376
CK_TW = CK_W - 16 - 110 - 6
CB_H = WV_BH - 20 - 6 - CK_H - 8                            # under the cards (630)
CC_C, CC_R, CC_H = 3, 5, 100                                # collection cards: 3 x 5 a page
CC_N = CC_C * CC_R
CC_W = (WV_VI - (CC_C - 1) * 10) // CC_C                    # 505
CC_TW = CC_W - 16 - 100 - 8
CD_LW = 900
CD_LI = CD_LW - 20
CD_RW = WV_VI - CD_LW - 10                                  # recipes (626)
CD_RI = CD_RW - 20
CT_N = 12                                                   # tier rows
CT_STATES = [("DONE", "green"), ("BOUGHT", "xp"), ("NEXT", "action"), ("LOCKED", "dim"), ("NEW", "accentHi")]
CT_RW = CD_LI - 12 - 90 - 100 - 130 - 8                     # a tier's rewards
CR_N, CR_RH = 11, 44                                        # recipes a page
CR_TW = CD_RI - 12 - 110 - 8
CY_TW = CD_LI - 16 - 200 - 8                                # the buy box's text
# EXPLORE
EB_H = WV_BH - 24 - 4 - 40 - 6                              # under the level line + the tab row (686)
EO_W = (WV_VI - 30) // 4                                    # an overview card (376)
EZ_W = (WV_VI - 10) // 2                                    # a zones / titles column (763)
EZ_N = 18                                                   # zone lines per column a page
EZ_VW = 150
ET_N = 12                                                   # titles per column a page
ET_TW = EZ_W - 16 - 110 - 8
EC_LW, EC_IN = 560, 10                                      # checklist: the islands (10 a page)
EC_LI = EC_LW - 16
EC_ITW = EC_LI - 12 - 100 - 6
EC_RW = WV_VI - EC_LW - 10                                  # the picked island (966)
EC_RI = EC_RW - 16
EC_RN = 15                                                  # rows per column a page (2 columns)
EC_CW = (EC_RI - 10) // 2
EV_SUB = ["Overview", "Zones", "Titles", "Checklist"]
# ISLAND
IB_H = WV_BH - 24 - 40 - 6 - 30                             # under the role line + the tab row + the note line (660)
IM_LW = 960
IM_LI = IM_LW - 16
IM_RW = WV_VI - IM_LW - 10                                  # 566
IM_RI = IM_RW - 16
IM_N, IM_RH = 10, 44                                        # co-op members a page
IM_TW = IM_LI - 16 - 2 * (120 + 6) - 8
IT_N = 12                                                   # trusted a page
IP_N, IP_CW = 14, 130                                       # the permission grid (SkyyIslands has 14 flags)
IP_WW = WV_VI - 16 - 4 * (IP_CW + 8) - (110 + 8)            # the grid's 'What' column
IV_N, IV_BWW = 10, 110                                      # visitors a page, a visitor button
IV_TW = IM_LI - 16 - 3 * (IV_BWW + 6) - 8
IX_N = 10                                                   # bans a page
IX_TW = IM_RI - 12 - 110 - 6
IS_SUB = ["Overview", "Members", "Permissions", "Visitors", "Island"]
IS_MODE = ["Public (anyone)", "Friends (members + trusted)", "Closed (members only)"]
IM_MBW = 300
IV_READ = "200|200|200|200"                                 # island:fn:act state: members | trusted | visitors | bans to send
assert QT_TW >= 700 and QL_TW >= 360 and CC_TW >= 360 and CT_RW >= 500 and CR_TW >= 450 and ET_TW >= 600 and EC_ITW >= 400, (QT_TW, QL_TW, CC_TW, CT_RW, CR_TW, ET_TW, EC_ITW)
assert IM_TW >= 600 and IP_WW >= 800 and IV_TW >= 500 and IX_TW >= 400 and WV_HCW >= 400, (IM_TW, IP_WW, IV_TW, IX_TW, WV_HCW)
for _l in WV_SUBS:
    assert SUI.text_width(_l, 14, bold=True) <= WV_SBW - 16, ("0.3.74: a sub-tab fits", _l)
for _l in EV_SUB + IS_SUB + ["Open (999)", "Done (999)"]:
    assert SUI.text_width(_l, 14, bold=True) <= WV_KBW - 16, ("0.3.74: a view tab fits", _l)
for _l, _w, _z in (("Track this line", 220, 13), ("Stop tracking", 220, 13), ("Claim all (999)", 200, 13), ("Hide tutorial", 200, 13), ("Show tutorial", 200, 13),
                   ("Claim", QT_BW, 13), ("Skip", QT_BW, 13), ("Unskip", QT_BW, 13), ("Open", 90, 13), ("Showing", 90, 13), ("View", 100, 13), ("Craft", 110, 13),
                   ("Buy", 200, 14), ("Use", 110, 13), ("No title", 200, 13), ("Show", 100, 13), ("Create my island", 260, 14), ("Go to island", 260, 14),
                   ("Click again to DISBAND", 260, 13), ("Disband co-op (99)", 260, 13), ("Really? Last click", 260, 13), ("Delete everything?", 260, 13),
                   ("Reset island", 260, 13), ("Click again to leave", 260, 13), ("Leave island", 260, 13), ("Invite to co-op", 200, 13), ("Trust - build only", 200, 13),
                   ("Promote", 120, 13), ("Demote", 120, 13), ("Kick", 120, 13), ("Sure?", 120, 13), ("Untrust", 110, 13), ("Unban", 110, 13), ("Expel", IV_BWW, 13),
                   ("Trust", IV_BWW, 13), ("Ban", IV_BWW, 13), ("Click again to reset", 260, 13), ("Reset to defaults", 260, 13), ("YES", IP_CW, 13), ("NO", IP_CW, 13),
                   ("Accept", 140, 13), ("Decline", 140, 13), ("ON", 120, 13), ("OFF", 120, 13), ("On", 110, 13), ("Off", 110, 13), ("Refresh", WV_RFW, 13)):
    assert SUI.text_width(_l, _z, bold=True) <= _w - 12, ("0.3.74: a view button fits", _l)
for _l in IS_MODE:
    assert SUI.text_width(_l, 13, bold=True) <= IM_MBW - 12, ("0.3.74: a visit mode fits", _l)
WV_TXT = {
    "qvold": "The quest log here needs SkyyQuests 0.4.5 - this server has an older one. /quests works.",
    "qvoff": "Quests are not on this server right now.",
    "qvfail": "Your quests could not be read right now - try again in a moment.",
    "qvcap": "Pick a quest line on the left. Track puts it on your HUD. World on top goes back.",
    "cvold": "Collections here need SkyyCollections 0.2.37 - this server has an older one. /collections works.",
    "cvoff": "Collections are not on this server right now.",
    "cvfail": "Your collections could not be read right now - try again in a moment.",
    "cvcap": "Pick a category, then a collection. Tiers pay when you reach them. World on top goes back.",
    "evold": "Exploring here needs SkyyExploration 0.3.5 - this server has an older one. /explore works.",
    "evoff": "Exploring is not on this server right now.",
    "evfail": "Your exploring could not be read right now - try again in a moment.",
    "evcap": "Exploring pays as you go - nothing waits to be claimed. World on top goes back.",
    "ivold": "Island settings here need SkyyIslands 0.5.27 - this server has an older one. /island menu works.",
    "ivoff": "Islands are not on this server right now.",
    "ivfail": "Your island could not be read right now - try again in a moment.",
    "ivcap": "Buttons that delete or remove ask first: press the same button again. World on top goes back.",
    "none": "That button is not on this page - nothing changed",
    "nullans": "That could not run here - nothing changed.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in WV_TXT.values() for c_ in v_), "0.3.74: plain texts"
for _k in ("qvold", "qvoff", "qvfail", "cvold", "cvoff", "cvfail", "evold", "evoff", "evfail", "ivold", "ivoff", "ivfail"):
    assert SUI.text_width(WV_TXT[_k], 13) <= WV_VI, ("0.3.74: a head line fits", _k)
for _k in ("qvcap", "cvcap", "evcap", "ivcap"):
    assert SUI.text_width(WV_TXT[_k], 14) <= IV_IW - 420, ("0.3.74: a caption fits the hint row", _k)
# the run-time markup: a view's own tab buttons (the market screen's tab styles), the mode buttons; the bars use WT_FILL
WV_TAB = "TextButton #SkyyWtab{I} { Anchor: (Width: %d, Height: 34, Right: 6); {S} }" % WV_KBW
WV_MODE = "TextButton #SkyyWtab{I} { Anchor: (Width: %d, Height: 36, Right: 8); {S} }" % IM_MBW
WV_ST0, WV_ST1 = SUI.glass_button_style("tab", 14), SUI.glass_button_style("tabSelected", 14)
WV_MS0, WV_MS1 = SUI.glass_button_style("tab", 13), SUI.glass_button_style("tabSelected", 13)
_wv_mk = [WV_TAB.replace("{I}", "Qk0").replace("{S}", WV_ST1), WV_TAB.replace("{I}", "Ek1").replace("{S}", WV_ST0),
          WV_MODE.replace("{I}", "Im0").replace("{S}", WV_MS1), WV_MODE.replace("{I}", "Im1").replace("{S}", WV_MS0)]
for _mk in _wv_mk:
    SUI.check_markup(_mk, prefix=WT, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.74: a run-time markup line Java can hold"
_wv_tok = SUI.proven_tokens(_wv_mk)
assert not [k_ for k_, g_ in _wv_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], "0.3.74: the view markups are proven"
WV_RUNTIME = {"Q": 2 + QL_N + QT_N, "C": CC_N + 1, "E": len(EV_SUB) + EC_IN + 1, "I": len(IS_SUB) + len(IS_MODE)}   # tabs + bar fills / mode buttons
WV_RUNTIME_IDS = ["Qk0", "Qk1"] + ["Ek%d" % k_ for k_ in range(len(EV_SUB))] + ["Ik%d" % k_ for k_ in range(len(IS_SUB))] + ["Im%d" % k_ for k_ in range(len(IS_MODE))]


def _wt_views():
    G_ = SUI
    lab = G_.glass_label
    win = WT + "Win"
    out = []

    def vhead(ap, parent, v, title, on):
        hd = WT + v + "h"
        ap.append(("#" + parent, G_.glass_group(hd, WV_VI, 34, layout="Left")))
        ap.append(("#" + hd, lab(None, title, 16, "accentHi", bold=True, w=200, h=34)))
        for k_, t_ in enumerate(WV_SUBS):
            ap.append(("#" + hd, G_.glass_button("%s%sVt%d" % (WT, v, k_), t_, "tabSelected" if k_ == on else "tab", w=WV_SBW, h=34, size=14, anchor={"right": 6})))
        ap.append(("#" + hd, lab(WT + v + "C", "", 13, "xp", bold=True, w=WV_HCW, h=34, halign="End", anchor={"right": 6})))
        ap.append(("#" + hd, G_.glass_button(WT + v + "Rf", "Refresh", "secondary", w=WV_RFW, h=34, size=13)))
        ap.append(("#" + parent, lab(WT + v + "H", "", 13, "text", w=WV_VI, h=20, anchor={"top": 4})))
        return [("#%s%sVt%d" % (WT, v, k_), "vw:%d" % k_) for k_ in range(len(WV_SUBS))] + [("#" + WT + v + "Rf", "vrf")]

    def holder(ap, parent, ident, w, h, size, cols, anchor=None, bold=False, halign=None):
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, c_, bold=bold, w=w, h=h, halign=halign)) for k_, c_ in enumerate(cols)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)

    def pagerow(ap, parent, ident, w, anchor=None):
        pg = WT + ident
        ap.append(("#" + parent, G_.glass_group(pg, w, 30, layout="Left", anchor=anchor or {"top": 6})))
        ap.append(("#" + pg, G_.glass_button(pg + "p", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
        ap.append(("#" + pg, lab(pg + "g", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
        ap.append(("#" + pg, G_.glass_button(pg + "n", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))

    def bar(ap, parent, ident, w, top=4):
        ap.append(("#" + parent, 'Group #%s { Anchor: (Width: %d, Height: 8, Top: %d); LayoutMode: Left; Background: %s; }' % (ident, w, top, IV_TRACK)))
    # ======== Q: THE QUESTS VIEW (the old Quest log: the lines, the picked line's tasks, Track / Skip / Claim / Claim all / tutorial)
    ap = SUI.Appends()
    qv = WT + "Qv"
    ap.append(("#" + win, G_.glass_group(qv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bq = vhead(ap, qv, "Qv", "QUESTS", 1)
    qb = WT + "Qvb"
    ap.append(("#" + qv, G_.glass_group(qb, WV_VI, WV_BH, layout="Left", anchor={"top": 6})))
    ql = WT + "QvL"
    ap.append(("#" + qb, G_.glass_group(ql, QL_W, WV_BH, role="inset", layout="Top", pad=8)))
    ap.append(("#" + ql, lab(None, "QUEST LINES", 12, "dim", bold=True, w=QL_IW, h=18)))
    for k_ in range(QL_N):
        r = "%sQvL%d" % (WT, k_)
        ap.append(("#" + ql, G_.glass_group(r, QL_IW, QL_RH, role="panel", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", QL_TW, QL_RH, layout="Top", anchor={"right": 6})))
        ap.append(("#" + r + "X", lab(r + "N", "", 14, "row", bold=True, w=QL_TW, h=22, anchor={"top": 4})))
        ap.append(("#" + r + "X", lab(r + "S", "", 11, "dim", w=QL_TW, h=16)))
        bar(ap, r + "X", r + "B", QL_TW, 2)
        ap.append(("#" + r, G_.glass_button(r + "P", "Open", "secondary", w=90, h=30, size=13, anchor={"top": 12})))
    pagerow(ap, ql, "QvLp", QL_IW)
    assert 18 + QL_N * (QL_RH + 4) + 36 + 16 <= WV_BH and 4 + 22 + 16 + 10 <= QL_RH, "0.3.74: the quest lines fit"
    ap.append(("#" + qb, "Group { Anchor: (Width: 10); }"))
    qr = WT + "QvR"
    ap.append(("#" + qb, G_.glass_group(qr, QR_W, WV_BH, role="inset", layout="Top", pad=8)))
    rh = WT + "QvRh"
    ap.append(("#" + qr, G_.glass_group(rh, QR_IW, 50, layout="Left")))
    rx = WT + "QvRx"
    ap.append(("#" + rh, G_.glass_group(rx, QR_IW - 228, 50, layout="Top", anchor={"right": 8})))
    ap.append(("#" + rx, lab(WT + "QvN", "", 18, "title", bold=True, w=QR_IW - 228, h=28)))
    ap.append(("#" + rx, lab(WT + "QvS", "", 13, "text", w=QR_IW - 228, h=20)))
    ap.append(("#" + rh, G_.glass_button(WT + "QvTr", "Track this line", "primary", w=220, h=36, size=13, anchor={"top": 7})))
    ap.append(("#" + qr, lab(WT + "QvW", "", 12, "action", w=QR_IW, h=18, anchor={"top": 2})))
    sr = WT + "QvSr"
    ap.append(("#" + qr, G_.glass_group(sr, QR_IW, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + sr, G_.glass_group(WT + "QvK", 2 * (WV_KBW + 6), 34, layout="Left")))
    ap.append(("#" + sr, lab(WT + "QvKn", "", 12, "dim", w=QR_IW - 2 * (WV_KBW + 6), h=34, halign="End")))
    for k_ in range(QT_N):
        r = "%sQvT%d" % (WT, k_)
        ap.append(("#" + qr, G_.glass_group(r, QR_IW, QT_RH, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"top": 4})))
        x_ = r + "X"
        ap.append(("#" + r, G_.glass_group(x_, QT_TW, QT_RH, layout="Top", anchor={"right": 8})))
        y_ = r + "Y"
        ap.append(("#" + x_, G_.glass_group(y_, QT_TW, 22, layout="Left", anchor={"top": 3})))
        ap.append(("#" + y_, lab(r + "N", "", 15, "row", bold=True, w=QT_TW - QT_SW, h=22)))
        holder(ap, y_, r + "S", QT_SW, 22, 13, [c_ for _t, c_ in QT_STATES], bold=True, halign="End")
        g_ = r + "G"
        ap.append(("#" + x_, G_.glass_group(g_, QT_TW, 18, layout="Left")))
        ap.append(("#" + g_, lab(r + "P", "", 12, "xp", bold=True, w=110, h=18)))
        bar(ap, g_, r + "B", QT_BARW, 5)
        ap.append(("#" + g_, lab(r + "W", "", 12, "text", w=QT_TW - 110 - QT_BARW - 12, h=18, anchor={"left": 12})))
        ap.append(("#" + x_, lab(r + "R", "", 12, "text", w=QT_TW, h=16)))
        ap.append(("#" + x_, lab(r + "H", "", 11, "dim", w=QT_TW, h=16)))
        ap.append(("#" + r, G_.glass_button(r + "C", "Claim", "primary", w=QT_BW, h=32, size=13, anchor={"top": 23, "right": 6})))
        ap.append(("#" + r, G_.glass_button(r + "K", "Skip", "secondary", w=QT_BW, h=32, size=13, anchor={"top": 23})))
    assert 3 + 22 + 18 + 16 + 16 <= QT_RH, "0.3.74: a task row fits"
    pagerow(ap, qr, "QvTp", QR_IW)
    qf = WT + "QvF"
    ap.append(("#" + qr, G_.glass_group(qf, QR_IW, 36, layout="Left", anchor={"top": 6})))
    ap.append(("#" + qf, lab(WT + "QvFn", "", 12, "dim", w=QR_IW - 412, h=36)))
    ap.append(("#" + qf, G_.glass_button(WT + "QvCa", "Claim all", "primary", w=200, h=36, size=13, anchor={"right": 6})))
    ap.append(("#" + qf, G_.glass_button(WT + "QvHd", "Hide tutorial", "secondary", w=200, h=36, size=13)))
    assert 50 + 20 + 40 + QT_N * (QT_RH + 4) + 36 + 42 + 16 <= WV_BH, "0.3.74: the quests panel fits"
    out.append(("Q", ap, bq + [("#" + WT + "QvLpp", "qlpg:-1"), ("#" + WT + "QvLpn", "qlpg:1"), ("#" + WT + "QvTpp", "qtpg:-1"), ("#" + WT + "QvTpn", "qtpg:1")]))
    # ======== C: THE COLLECTIONS VIEW (the old /collections page: overview + 4 category cards, a category's cards, a collection's detail)
    ap = SUI.Appends()
    cv = WT + "Cv"
    ap.append(("#" + win, G_.glass_group(cv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bc = vhead(ap, cv, "Cv", "COLLECTIONS", 2)
    ap.append(("#" + cv, lab(WT + "CvT", "", 13, "text", w=WV_VI, h=20, anchor={"top": 6})))
    ck = WT + "CvK"
    ap.append(("#" + cv, G_.glass_group(ck, WV_VI, CK_H, layout="Left", anchor={"top": 6})))
    for k_ in range(CK_N):
        c_ = "%sCvK%d" % (WT, k_)
        ap.append(("#" + ck, G_.glass_group(c_, CK_W, CK_H, role="inset", layout="Left", pad=8, anchor={"right": 10} if k_ < CK_N - 1 else None)))
        ap.append(("#" + c_, G_.glass_group(c_ + "X", CK_TW, CK_H - 16, layout="Top", anchor={"right": 6})))
        ap.append(("#" + c_ + "X", lab(c_ + "N", "", 15, "accentHi", bold=True, w=CK_TW, h=24)))
        ap.append(("#" + c_ + "X", lab(c_ + "F", "", 12, "text", w=CK_TW, h=18)))
        ap.append(("#" + c_ + "X", lab(c_ + "D", "", 12, "dim", w=CK_TW, h=18)))
        ap.append(("#" + c_, G_.glass_button(c_ + "B", "Open", "secondary", w=110, h=30, size=13, anchor={"top": 25})))
    assert 24 + 18 + 18 <= CK_H - 16 and CK_N * CK_W + (CK_N - 1) * 10 <= WV_VI, "0.3.74: the category cards fit"
    cb = WT + "CvB"
    ap.append(("#" + cv, G_.glass_group(cb, WV_VI, CB_H, layout="Top", anchor={"top": 8})))
    cg = WT + "CvG"
    ap.append(("#" + cb, G_.glass_group(cg, WV_VI, CB_H, layout="Top")))
    ap.append(("#" + cg, lab(WT + "CvGh", "", 14, "accentHi", bold=True, w=WV_VI, h=22)))
    for r_ in range(CC_R):
        rw = "%sCvGr%d" % (WT, r_)
        ap.append(("#" + cg, G_.glass_group(rw, WV_VI, CC_H, layout="Left", anchor={"top": 6})))
        for c_ in range(CC_C):
            k_ = r_ * CC_C + c_
            cc = "%sCvC%d" % (WT, k_)
            ap.append(("#" + rw, G_.glass_group(cc, CC_W, CC_H, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"right": 10} if c_ < CC_C - 1 else None)))
            ap.append(("#" + cc, G_.glass_group(cc + "X", CC_TW, CC_H, layout="Top", anchor={"right": 8})))
            ap.append(("#" + cc + "X", lab(cc + "N", "", 15, "row", bold=True, w=CC_TW, h=22, anchor={"top": 8})))
            ap.append(("#" + cc + "X", lab(cc + "P", "", 13, "xp", bold=True, w=CC_TW, h=18)))
            bar(ap, cc + "X", cc + "B", CC_TW)
            ap.append(("#" + cc + "X", lab(cc + "S", "", 12, "text", w=CC_TW, h=18, anchor={"top": 4})))
            ap.append(("#" + cc, G_.glass_button(cc + "V", "View", "secondary", w=100, h=32, size=13, anchor={"top": 34})))
    assert 8 + 22 + 18 + 12 + 22 <= CC_H and CC_C * CC_W + (CC_C - 1) * 10 <= WV_VI, "0.3.74: a collection card fits"
    pagerow(ap, cg, "CvGp", WV_VI)
    ap.append(("#" + cg, lab(WT + "CvGn", "", 12, "dim", w=WV_VI, h=18, anchor={"top": 4})))
    assert 22 + CC_R * (CC_H + 6) + 36 + 22 <= CB_H, "0.3.74: the collection cards fit"
    cd = WT + "CvD"
    ap.append(("#" + cb, G_.glass_group(cd, WV_VI, CB_H, layout="Left")))
    dl = WT + "CvDl"
    ap.append(("#" + cd, G_.glass_group(dl, CD_LW, CB_H, role="inset", layout="Top", pad=10)))
    ap.append(("#" + dl, lab(WT + "CvDN", "", 20, "title", bold=True, w=CD_LI, h=28)))
    ap.append(("#" + dl, lab(WT + "CvDM", "", 12, "dim", w=CD_LI, h=18)))
    ap.append(("#" + dl, lab(WT + "CvDG", "", 13, "xp", bold=True, w=CD_LI, h=20, anchor={"top": 6})))
    bar(ap, dl, WT + "CvDB", CD_LI)
    dy = WT + "CvDy"
    ap.append(("#" + dl, G_.glass_group(dy, CD_LI, 76, role="panel", layout="Left", pad=8, anchor={"top": 10})))
    ap.append(("#" + dy, G_.glass_group(dy + "X", CY_TW, 60, layout="Top", anchor={"right": 8})))
    ap.append(("#" + dy + "X", lab(WT + "CvDy1", "", 14, "xp", bold=True, w=CY_TW, h=24)))
    ap.append(("#" + dy + "X", lab(WT + "CvDy2", "", 12, "text", w=CY_TW, h=18)))
    ap.append(("#" + dy + "X", lab(WT + "CvDy3", "", 12, "action", w=CY_TW, h=18)))
    ap.append(("#" + dy, G_.glass_button(WT + "CvDyB", "Buy", "primary", w=200, h=40, size=14, anchor={"top": 10})))
    ap.append(("#" + dl, lab(None, "TIERS", 12, "dim", bold=True, w=CD_LI, h=18, anchor={"top": 10})))
    for k_ in range(CT_N):
        r = "%sCvDt%d" % (WT, k_)
        ap.append(("#" + dl, G_.glass_group(r, CD_LI, 28, layout="Left", pad={"horizontal": 6}, anchor={"top": 2})))
        ap.append(("#" + r, lab(r + "N", "", 13, "row", bold=True, w=90, h=28)))
        holder(ap, r, r + "S", 100, 28, 12, [c_ for _t, c_ in CT_STATES], bold=True)
        ap.append(("#" + r, lab(r + "A", "", 12, "xp", w=130, h=28)))
        ap.append(("#" + r, lab(r + "R", "", 12, "text", w=CT_RW, h=28, anchor={"left": 8})))
    ap.append(("#" + dl, lab(WT + "CvDtn", "", 12, "dim", w=CD_LI, h=18, anchor={"top": 4})))
    assert 28 + 18 + 26 + 12 + 86 + 28 + CT_N * 30 + 22 + 20 <= CB_H, "0.3.74: the collection detail fits"
    ap.append(("#" + cd, "Group { Anchor: (Width: 10); }"))
    dr = WT + "CvDr"
    ap.append(("#" + cd, G_.glass_group(dr, CD_RW, CB_H, role="inset", layout="Top", pad=10)))
    ap.append(("#" + dr, lab(WT + "CvDrh", "", 14, "accentHi", bold=True, w=CD_RI, h=22)))
    for k_ in range(CR_N):
        r = "%sCvR%d" % (WT, k_)
        ap.append(("#" + dr, G_.glass_group(r, CD_RI, CR_RH, role="panel", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", CR_TW, CR_RH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + r + "X", lab(r + "N", "", 14, "row", bold=True, w=CR_TW, h=22, anchor={"top": 3})))
        ap.append(("#" + r + "X", lab(r + "S", "", 11, "dim", w=CR_TW, h=16)))
        ap.append(("#" + r, G_.glass_button(r + "C", "Craft", "primary", w=110, h=30, size=13, anchor={"top": 7})))
    pagerow(ap, dr, "CvRp", CD_RI)
    ap.append(("#" + dr, lab(WT + "CvRn", "", 12, "dim", w=CD_RI, h=18, anchor={"top": 4})))
    assert 22 + CR_N * (CR_RH + 4) + 36 + 22 + 20 <= CB_H, "0.3.74: the recipes fit"
    assert 20 + 34 + 24 + 6 + 20 + 6 + CK_H + 8 + CB_H <= IV_BODY_H, "0.3.74: the collections view fits"
    out.append(("C", ap, bc + [("#" + WT + "CvGpp", "cpg:-1"), ("#" + WT + "CvGpn", "cpg:1"), ("#" + WT + "CvRpp", "crpg:-1"), ("#" + WT + "CvRpn", "crpg:1")]))
    # ======== E: THE EXPLORE VIEW (the old /explore page: Overview | Zones | Titles | Checklist)
    ap = SUI.Appends()
    ev_ = WT + "Ev"
    ap.append(("#" + win, G_.glass_group(ev_, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    be = vhead(ap, ev_, "Ev", "EXPLORE", 3)
    ap.append(("#" + ev_, lab(WT + "EvL", "", 15, "xp", bold=True, w=WV_VI, h=24, anchor={"top": 4})))
    es = WT + "EvSr"
    ap.append(("#" + ev_, G_.glass_group(es, WV_VI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + es, G_.glass_group(WT + "EvK", len(EV_SUB) * (WV_KBW + 6), 34, layout="Left")))
    ap.append(("#" + es, lab(WT + "EvKn", "", 12, "dim", w=WV_VI - len(EV_SUB) * (WV_KBW + 6), h=34, halign="End")))
    eb = WT + "EvB"
    ap.append(("#" + ev_, G_.glass_group(eb, WV_VI, EB_H, layout="Top", anchor={"top": 6})))
    eo = WT + "EvO"
    ap.append(("#" + eb, G_.glass_group(eo, WV_VI, EB_H, layout="Top")))
    for r_ in range(2):
        rw = "%sEvOr%d" % (WT, r_)
        ap.append(("#" + eo, G_.glass_group(rw, WV_VI, 104, layout="Left", anchor={"top": 6 if r_ else 0})))
        for c_ in range(4):
            k_ = r_ * 4 + c_
            o_ = "%sEvO%d" % (WT, k_)
            ap.append(("#" + rw, G_.glass_group(o_, EO_W, 104, role="inset", layout="Top", pad=8, anchor={"right": 10} if c_ < 3 else None)))
            ap.append(("#" + o_, lab(o_ + "H", "", 12, "dim", bold=True, w=EO_W - 16, h=18)))
            ap.append(("#" + o_, lab(o_ + "V", "", 18, "title", bold=True, w=EO_W - 16, h=28)))
            ap.append(("#" + o_, lab(o_ + "S", "", 12, "text", w=EO_W - 16, h=18)))
            ap.append(("#" + o_, lab(o_ + "T", "", 12, "text", w=EO_W - 16, h=18)))
    ap.append(("#" + eo, lab(WT + "EvOq", "", 13, "action", bold=True, w=WV_VI, h=20, anchor={"top": 12})))
    ap.append(("#" + eo, lab(WT + "EvOu", "", 12, "dim", w=WV_VI, h=20)))
    ap.append(("#" + eo, lab(WT + "EvOv", "", 12, "dim", w=WV_VI, h=20, anchor={"top": 6})))
    assert 18 + 28 + 18 + 18 <= 104 - 16 and 2 * 104 + 6 + 32 + 20 + 26 <= EB_H, "0.3.74: the overview fits"
    ez = WT + "EvZ"
    ap.append(("#" + eb, G_.glass_group(ez, WV_VI, EB_H, layout="Top")))
    zc = WT + "EvZs"
    ap.append(("#" + ez, G_.glass_group(zc, WV_VI, EB_H - 36, layout="Left")))
    for c_ in range(2):
        col_ = "%sEvZc%d" % (WT, c_)
        ap.append(("#" + zc, G_.glass_group(col_, EZ_W, EB_H - 36, role="inset", layout="Top", pad=8, anchor={"right": 10} if c_ == 0 else None)))
        for k_ in range(EZ_N):
            z_ = "%sEvZ%d" % (WT, c_ * EZ_N + k_)
            ap.append(("#" + col_, G_.glass_group(z_, EZ_W - 16, 30, layout="Left", anchor={"top": 2})))
            holder(ap, z_, z_ + "N", EZ_W - 16 - EZ_VW, 30, 13, ["accentHi", "text"], bold=True)
            ap.append(("#" + z_, lab(z_ + "V", "", 12, "xp", bold=True, w=EZ_VW, h=30, halign="End")))
    assert EZ_N * 32 + 16 <= EB_H - 36, "0.3.74: the zones fit"
    pagerow(ap, ez, "EvZp", WV_VI)
    et = WT + "EvT"
    ap.append(("#" + eb, G_.glass_group(et, WV_VI, EB_H, layout="Top")))
    tt = WT + "EvTt"
    ap.append(("#" + et, G_.glass_group(tt, WV_VI, 34, layout="Left")))
    ap.append(("#" + tt, lab(WT + "EvTs", "", 13, "text", w=WV_VI - 206, h=34, anchor={"right": 6})))
    ap.append(("#" + tt, G_.glass_button(WT + "EvTn", "No title", "secondary", w=200, h=34, size=13)))
    tc = WT + "EvTcs"
    ap.append(("#" + et, G_.glass_group(tc, WV_VI, ET_N * 50, layout="Left", anchor={"top": 6})))
    for c_ in range(2):
        col_ = "%sEvTc%d" % (WT, c_)
        ap.append(("#" + tc, G_.glass_group(col_, EZ_W, ET_N * 50, layout="Top", anchor={"right": 10} if c_ == 0 else None)))
        for k_ in range(ET_N):
            t_ = "%sEvT%d" % (WT, c_ * ET_N + k_)
            ap.append(("#" + col_, G_.glass_group(t_, EZ_W, 46, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"top": 4})))
            ap.append(("#" + t_, G_.glass_group(t_ + "X", ET_TW, 46, layout="Top", anchor={"right": 8})))
            holder(ap, t_ + "X", t_ + "N", ET_TW, 22, 14, ["green", "xp", "dim"], anchor={"top": 3}, bold=True)
            ap.append(("#" + t_ + "X", lab(t_ + "R", "", 11, "dim", w=ET_TW, h=16)))
            ap.append(("#" + t_, G_.glass_button(t_ + "U", "Use", "primary", w=110, h=30, size=13, anchor={"top": 8})))
    pagerow(ap, et, "EvTp", WV_VI)
    assert 34 + 6 + ET_N * 50 + 36 <= EB_H, "0.3.74: the titles fit"
    ec = WT + "EvCk"
    ap.append(("#" + eb, G_.glass_group(ec, WV_VI, EB_H, layout="Left")))
    cl = WT + "EvCl"
    ap.append(("#" + ec, G_.glass_group(cl, EC_LW, EB_H, role="inset", layout="Top", pad=8)))
    ap.append(("#" + cl, lab(None, "ISLAND CHECKLISTS", 12, "dim", bold=True, w=EC_LI, h=18)))
    for k_ in range(EC_IN):
        r = "%sEvCi%d" % (WT, k_)
        ap.append(("#" + cl, G_.glass_group(r, EC_LI, 56, role="panel", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", EC_ITW, 56, layout="Top", anchor={"right": 6})))
        ap.append(("#" + r + "X", lab(r + "N", "", 14, "row", bold=True, w=EC_ITW, h=22, anchor={"top": 4})))
        ap.append(("#" + r + "X", lab(r + "S", "", 12, "text", w=EC_ITW, h=16)))
        bar(ap, r + "X", r + "B", EC_ITW, 2)
        ap.append(("#" + r, G_.glass_button(r + "Go", "Show", "secondary", w=100, h=30, size=13, anchor={"top": 13})))
    pagerow(ap, cl, "EvCip", EC_LI)
    assert 18 + EC_IN * 60 + 36 + 16 <= EB_H, "0.3.74: the islands fit"
    ap.append(("#" + ec, "Group { Anchor: (Width: 10); }"))
    cr = WT + "EvCr"
    ap.append(("#" + ec, G_.glass_group(cr, EC_RW, EB_H, role="inset", layout="Top", pad=8)))
    ap.append(("#" + cr, lab(WT + "EvCrN", "", 16, "title", bold=True, w=EC_RI, h=24)))
    ap.append(("#" + cr, lab(WT + "EvCrS", "", 12, "text", w=EC_RI, h=18)))
    bar(ap, cr, WT + "EvCrB", EC_RI)
    cs = WT + "EvCrw"
    ap.append(("#" + cr, G_.glass_group(cs, EC_RI, EC_RN * 30, layout="Left", anchor={"top": 8})))
    for c_ in range(2):
        col_ = "%sEvCc%d" % (WT, c_)
        ap.append(("#" + cs, G_.glass_group(col_, EC_CW, EC_RN * 30, layout="Top", anchor={"right": 10} if c_ == 0 else None)))
        for k_ in range(EC_RN):
            e_ = "%sEvCe%d" % (WT, c_ * EC_RN + k_)
            ap.append(("#" + col_, G_.glass_group(e_, EC_CW, 28, layout="Left", anchor={"top": 2})))
            holder(ap, e_, e_ + "N", EC_CW - 100, 28, 13, ["green", "text"])
            ap.append(("#" + e_, lab(e_ + "V", "", 12, "xp", bold=True, w=100, h=28, halign="End")))
    ap.append(("#" + cr, lab(WT + "EvCrf", "", 13, "xp", bold=True, w=EC_RI, h=20, anchor={"top": 8})))
    pagerow(ap, cr, "EvCrp", EC_RI)
    assert 24 + 18 + 12 + 8 + EC_RN * 30 + 28 + 36 + 16 <= EB_H, "0.3.74: a checklist fits"
    assert 20 + 34 + 24 + 4 + 24 + 6 + 34 + 6 + EB_H <= IV_BODY_H, "0.3.74: the explore view fits"
    out.append(("E", ap, be + [("#" + WT + "EvZpp", "ezpg:-1"), ("#" + WT + "EvZpn", "ezpg:1"), ("#" + WT + "EvTpp", "etpg:-1"), ("#" + WT + "EvTpn", "etpg:1"),
                               ("#" + WT + "EvCipp", "eipg:-1"), ("#" + WT + "EvCipn", "eipg:1"), ("#" + WT + "EvCrpp", "ecpg:-1"), ("#" + WT + "EvCrpn", "ecpg:1")]))
    # ======== I: THE ISLAND VIEW (the old island menu: Overview | Members | Permissions | Visitors | Island)
    ap = SUI.Appends()
    iv = WT + "Iv"
    ap.append(("#" + win, G_.glass_group(iv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bi = vhead(ap, iv, "Iv", "ISLAND", 4)
    ap.append(("#" + iv, lab(WT + "IvR", "", 13, "accentHi", bold=True, w=WV_VI, h=20, anchor={"top": 4})))
    isr = WT + "IvSr"
    ap.append(("#" + iv, G_.glass_group(isr, WV_VI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + isr, G_.glass_group(WT + "IvK", len(IS_SUB) * (WV_KBW + 6), 34, layout="Left")))
    ap.append(("#" + isr, lab(WT + "IvKn", "", 12, "dim", w=WV_VI - len(IS_SUB) * (WV_KBW + 6), h=34, halign="End")))
    ib = WT + "IvB"
    ap.append(("#" + iv, G_.glass_group(ib, WV_VI, IB_H + 30, layout="Top", anchor={"top": 6})))
    ap.append(("#" + ib, lab(WT + "IvE", "", 13, "dim", w=WV_VI, h=24, anchor={"bottom": 6})))
    # OVERVIEW
    io = WT + "IvO"
    ap.append(("#" + ib, G_.glass_group(io, WV_VI, IB_H, layout="Top")))
    ob = WT + "IvOb"
    ap.append(("#" + io, G_.glass_group(ob, WV_VI, 120, role="inset", layout="Top", pad=10)))
    ap.append(("#" + ob, lab(WT + "IvO1", "", 16, "title", bold=True, w=WV_VI - 20, h=26)))
    ap.append(("#" + ob, lab(WT + "IvO2", "", 13, "text", w=WV_VI - 20, h=20)))
    ap.append(("#" + ob, lab(WT + "IvO3", "", 13, "text", w=WV_VI - 20, h=20)))
    ap.append(("#" + ob, lab(WT + "IvO4", "", 12, "dim", w=WV_VI - 20, h=20)))
    ap.append(("#" + io, lab(WT + "IvOz", "", 13, "red", bold=True, w=WV_VI, h=20, anchor={"top": 6})))
    og = WT + "IvOg"
    ap.append(("#" + io, G_.glass_group(og, WV_VI, 40, layout="Left", anchor={"top": 10})))
    ap.append(("#" + og, G_.glass_button(WT + "IvGo", "Go to island", "primary", w=260, h=40, size=14, anchor={"right": 12})))
    ap.append(("#" + og, lab(WT + "IvGoh", "", 12, "dim", w=WV_VI - 272, h=40)))
    oi = WT + "IvOi"
    ap.append(("#" + io, G_.glass_group(oi, 1000, 104, role="panel", layout="Top", pad=10, anchor={"top": 12})))
    ap.append(("#" + oi, lab(WT + "IvOiq", "", 14, "action", bold=True, w=980, h=24)))
    ap.append(("#" + oi, lab(WT + "IvOis", "", 12, "text", w=980, h=18)))
    oy = WT + "IvOib"
    ap.append(("#" + oi, G_.glass_group(oy, 980, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + oy, G_.glass_button(WT + "IvOy", "Accept", "primary", w=140, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + oy, G_.glass_button(WT + "IvOn", "Decline", "secondary", w=140, h=34, size=13)))
    oo = WT + "IvOo"
    ap.append(("#" + io, G_.glass_group(oo, WV_VI, 40, layout="Left", anchor={"top": 14})))
    ap.append(("#" + oo, G_.glass_button(WT + "IvDb", "Disband co-op", "secondary", w=260, h=40, size=13, anchor={"right": 12})))
    ap.append(("#" + oo, G_.glass_button(WT + "IvRs", "Reset island", "secondary", w=260, h=40, size=13, anchor={"right": 12})))
    ap.append(("#" + oo, lab(WT + "IvRsn", "", 12, "dim", w=WV_VI - 2 * 272, h=40)))
    ap.append(("#" + io, lab(WT + "IvOon", "", 12, "dim", w=WV_VI, h=18, anchor={"top": 4})))
    ol = WT + "IvOl"
    ap.append(("#" + io, G_.glass_group(ol, WV_VI, 40, layout="Left", anchor={"top": 10})))
    ap.append(("#" + ol, G_.glass_button(WT + "IvLv", "Leave island", "secondary", w=260, h=40, size=13, anchor={"right": 12})))
    ap.append(("#" + ol, lab(WT + "IvLvn", "", 12, "dim", w=WV_VI - 272, h=40)))
    assert 120 + 26 + 50 + 116 + 54 + 22 + 50 <= IB_H and 24 + 18 + 6 + 34 <= 104 - 20, "0.3.74: the island overview fits"
    # MEMBERS (co-op + trusted)
    im = WT + "IvM"
    ap.append(("#" + ib, G_.glass_group(im, WV_VI, IB_H, layout="Left")))
    ml = WT + "IvMl"
    ap.append(("#" + im, G_.glass_group(ml, IM_LW, IB_H, role="inset", layout="Top", pad=8)))
    mi = WT + "IvMi"
    ap.append(("#" + ml, G_.glass_group(mi, IM_LI, 34, layout="Left")))
    ap.append(("#" + mi, G_.text_field(WT + "IvMfBox", WT + "IvMf", w=280, h=32, placeholder="Player name", max_length=32, size=13, anchor={"right": 6})))
    ap.append(("#" + mi, G_.glass_button(WT + "IvMinv", "Invite to co-op", "primary", w=200, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + mi, G_.glass_button(WT + "IvMtr", "Trust - build only", "secondary", w=200, h=34, size=13)))
    ap.append(("#" + ml, lab(WT + "IvMih", "", 12, "dim", w=IM_LI, h=18, anchor={"top": 4})))
    ap.append(("#" + ml, lab(WT + "IvMh", "", 13, "accentHi", bold=True, w=IM_LI, h=22, anchor={"top": 6})))
    for k_ in range(IM_N):
        r = "%sIvM%d" % (WT, k_)
        ap.append(("#" + ml, G_.glass_group(r, IM_LI, IM_RH, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"top": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", IM_TW, IM_RH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + r + "X", lab(r + "N", "", 14, "row", bold=True, w=IM_TW, h=22, anchor={"top": 2})))
        ap.append(("#" + r + "X", lab(r + "S", "", 11, "dim", w=IM_TW, h=16)))
        ap.append(("#" + r, G_.glass_button(r + "P", "Promote", "secondary", w=120, h=30, size=13, anchor={"top": 7, "right": 6})))
        ap.append(("#" + r, G_.glass_button(r + "K", "Kick", "secondary", w=120, h=30, size=13, anchor={"top": 7})))
    pagerow(ap, ml, "IvMp", IM_LI, {"top": 4})
    ap.append(("#" + ml, lab(WT + "IvMn", "", 12, "action", w=IM_LI, h=18, anchor={"top": 4})))
    assert 34 + 22 + 28 + IM_N * (IM_RH + 4) + 34 + 22 + 16 <= IB_H, "0.3.74: the co-op list fits"
    ap.append(("#" + im, "Group { Anchor: (Width: 10); }"))
    mt = WT + "IvMt"
    ap.append(("#" + im, G_.glass_group(mt, IM_RW, IB_H, role="inset", layout="Top", pad=8)))
    ap.append(("#" + mt, lab(WT + "IvTh", "", 13, "accentHi", bold=True, w=IM_RI, h=22)))
    for k_ in range(IT_N):
        r = "%sIvT%d" % (WT, k_)
        ap.append(("#" + mt, G_.glass_group(r, IM_RI, 40, role="panel", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + r, lab(r + "N", "", 13, "row", bold=True, w=IX_TW, h=40, anchor={"right": 6})))
        ap.append(("#" + r, G_.glass_button(r + "U", "Untrust", "secondary", w=110, h=30, size=13, anchor={"top": 5})))
    pagerow(ap, mt, "IvTp", IM_RI, {"top": 4})
    ap.append(("#" + mt, lab(WT + "IvTn", "", 12, "dim", w=IM_RI, h=18, anchor={"top": 4})))
    ap.append(("#" + mt, lab(WT + "IvTo", "", 12, "dim", w=IM_RI, h=18)))
    assert 22 + IT_N * 44 + 34 + 40 + 16 <= IB_H, "0.3.74: the trusted list fits"
    # PERMISSIONS (the grid)
    ip = WT + "IvP"
    ap.append(("#" + ib, G_.glass_group(ip, WV_VI, IB_H, layout="Top")))
    pt = WT + "IvPt"
    ap.append(("#" + ip, G_.glass_group(pt, WV_VI, 36, layout="Left")))
    ap.append(("#" + pt, lab(WT + "IvPtx", "", 12, "text", w=WV_VI - 266, h=36, anchor={"right": 6})))
    ap.append(("#" + pt, G_.glass_button(WT + "IvPdef", "Reset to defaults", "secondary", w=260, h=36, size=13)))
    ap.append(("#" + ip, lab(WT + "IvPs", "", 12, "dim", w=WV_VI, h=18, anchor={"top": 2})))
    ph = WT + "IvPh"
    ap.append(("#" + ip, G_.glass_group(ph, WV_VI, 22, layout="Left", pad={"horizontal": 8}, anchor={"top": 4})))
    ap.append(("#" + ph, lab(None, "WHAT", 12, "dim", bold=True, w=IP_WW, h=22)))
    for t_ in ("VISITOR", "TRUSTED", "MEMBER", "ADMIN"):
        ap.append(("#" + ph, lab(None, t_, 12, "dim", bold=True, w=IP_CW, h=22, halign="Center", anchor={"left": 8})))
    ap.append(("#" + ph, lab(None, "OWNER", 12, "dim", bold=True, w=110, h=22, halign="Center", anchor={"left": 8})))
    for k_ in range(IP_N):
        r = "%sIvP%d" % (WT, k_)
        ap.append(("#" + ip, G_.glass_group(r, WV_VI, 38, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"top": 2})))
        ap.append(("#" + r, G_.glass_group(r + "X", IP_WW, 38, layout="Top")))
        ap.append(("#" + r + "X", lab(r + "N", "", 13, "row", bold=True, w=IP_WW, h=20, anchor={"top": 2})))
        ap.append(("#" + r + "X", lab(r + "S", "", 11, "dim", w=IP_WW, h=14)))
        cells = SUI.keep_at0(G_.glass_group(r + "Cb", 4 * (IP_CW + 8), 38, layout="Left"))
        ro = SUI.keep_at0(lab(r + "Ro", "", 12, "text", w=4 * (IP_CW + 8), h=38, halign="Center"))
        hm_, kids_ = SUI.keep_holder(r + "Ch", 4 * (IP_CW + 8), 38, [cells, ro])
        ap.append(("#" + r, hm_))
        ap.extend(kids_)
        for c_ in range(4):
            ap.append(("#" + r + "Cb", G_.glass_button("%sc%d" % (r, c_), "NO", "secondary", w=IP_CW, h=30, size=13, anchor={"left": 8, "top": 4})))
        ap.append(("#" + r, lab(None, "always", 12, "green", bold=True, w=110, h=38, halign="Center", anchor={"left": 8})))
    assert IP_WW + 4 * (IP_CW + 8) + 118 + 16 <= WV_VI and 36 + 20 + 26 + IP_N * 40 <= IB_H, "0.3.74: the permission grid fits"
    # VISITORS (mode, limit, ping; players on the island; bans)
    ivv = WT + "IvV"
    ap.append(("#" + ib, G_.glass_group(ivv, WV_VI, IB_H, layout="Top")))
    vm = WT + "IvVm"
    ap.append(("#" + ivv, G_.glass_group(vm, WV_VI, 36, layout="Left")))
    ap.append(("#" + vm, lab(None, "Who may visit", 13, "text", bold=True, w=170, h=36)))
    ap.append(("#" + vm, G_.glass_group(WT + "IvVmb", len(IS_MODE) * (IM_MBW + 8), 36, layout="Left")))
    ap.append(("#" + vm, lab(WT + "IvVmx", "", 13, "xp", bold=True, w=WV_VI - 170 - len(IS_MODE) * (IM_MBW + 8), h=36)))
    vl = WT + "IvVl"
    ap.append(("#" + ivv, G_.glass_group(vl, WV_VI, 36, layout="Left", anchor={"top": 6})))
    ap.append(("#" + vl, lab(None, "Visitor limit", 13, "text", bold=True, w=170, h=36)))
    ap.append(("#" + vl, G_.glass_button(WT + "IvVlm", "-", "secondary", w=44, h=36, size=15)))
    ap.append(("#" + vl, lab(WT + "IvVlv", "", 14, "xp", bold=True, w=80, h=36, halign="Center")))
    ap.append(("#" + vl, G_.glass_button(WT + "IvVlp", "", "secondary", w=44, h=36, size=15, anchor={"right": 30})))
    ap.append(("#" + vl, lab(None, "Visit ping", 13, "text", bold=True, w=120, h=36)))
    ap.append(("#" + vl, G_.glass_button(WT + "IvVn", "Off", "secondary", w=110, h=36, size=13)))
    ap.append(("#" + ivv, lab(WT + "IvVh", "", 12, "dim", w=WV_VI, h=18, anchor={"top": 4})))
    vb = WT + "IvVb"
    vbh = IB_H - 36 - 42 - 22 - 8
    ap.append(("#" + ivv, G_.glass_group(vb, WV_VI, vbh, layout="Left", anchor={"top": 8})))
    vv = WT + "IvVv"
    ap.append(("#" + vb, G_.glass_group(vv, IM_LW, vbh, role="inset", layout="Top", pad=8)))
    ap.append(("#" + vv, lab(WT + "IvVvh", "", 13, "accentHi", bold=True, w=IM_LI, h=22)))
    for k_ in range(IV_N):
        r = "%sIvV%d" % (WT, k_)
        ap.append(("#" + vv, G_.glass_group(r, IM_LI, 44, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"top": 4})))
        ap.append(("#" + r, lab(r + "N", "", 14, "row", bold=True, w=IV_TW, h=44, anchor={"right": 8})))
        for b_, t_ in (("E", "Expel"), ("T", "Trust"), ("B", "Ban")):
            ap.append(("#" + r, G_.glass_button(r + b_, t_, "secondary", w=IV_BWW, h=30, size=13, anchor={"top": 7, "right": 6})))
    pagerow(ap, vv, "IvVp", IM_LI, {"top": 4})
    assert 22 + IV_N * 48 + 34 + 16 <= vbh, "0.3.74: the visitors list fits"
    ap.append(("#" + vb, "Group { Anchor: (Width: 10); }"))
    vx = WT + "IvVx"
    ap.append(("#" + vb, G_.glass_group(vx, IM_RW, vbh, role="inset", layout="Top", pad=8)))
    ap.append(("#" + vx, lab(WT + "IvXh", "", 13, "accentHi", bold=True, w=IM_RI, h=22)))
    for k_ in range(IX_N):
        r = "%sIvX%d" % (WT, k_)
        ap.append(("#" + vx, G_.glass_group(r, IM_RI, 44, role="panel", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + r, lab(r + "N", "", 13, "row", bold=True, w=IX_TW, h=44, anchor={"right": 6})))
        ap.append(("#" + r, G_.glass_button(r + "U", "Unban", "secondary", w=110, h=30, size=13, anchor={"top": 7})))
    pagerow(ap, vx, "IvXp", IM_RI, {"top": 4})
    assert 22 + IX_N * 48 + 34 + 16 <= vbh, "0.3.74: the ban list fits"
    # ISLAND (the rules: PvP + Mob spawning)
    ii = WT + "IvI"
    ap.append(("#" + ib, G_.glass_group(ii, WV_VI, IB_H, layout="Top")))
    for t_, h_ in (("PvP - players can hurt each other", "IvIp"), ("Mob spawning", "IvIs")):
        r = WT + h_
        ap.append(("#" + ii, G_.glass_group(r, WV_VI, 40, role="inset", layout="Left", pad={"horizontal": 10}, anchor={"top": 10})))
        ap.append(("#" + r, lab(None, t_, 14, "row", bold=True, w=420, h=40)))
        ap.append(("#" + r, G_.glass_button(r + "b", "OFF", "secondary", w=120, h=34, size=13, anchor={"top": 3, "right": 12})))
        ap.append(("#" + r, lab(r + "h", "", 12, "dim", w=WV_VI - 20 - 420 - 132, h=40)))
    ap.append(("#" + ii, lab(WT + "IvIx", "", 12, "text", w=WV_VI, h=22, anchor={"top": 20})))
    ap.append(("#" + ii, lab(WT + "IvIn", "", 12, "dim", w=WV_VI, h=18)))
    ap.sets.append((WT + "IvIx", "Text", "Coming in a later version: island biome (grass colour, sky, weather, wildlife), a weather lock and a visitor landing point."))
    assert 20 + 34 + 24 + 6 + 34 + 6 + IB_H + 30 <= IV_BODY_H, "0.3.74: the island view fits"
    out.append(("I", ap, bi + [("#" + WT + "IvMpp", "impg:-1"), ("#" + WT + "IvMpn", "impg:1"), ("#" + WT + "IvTpp", "itpg:-1"), ("#" + WT + "IvTpn", "itpg:1"),
                               ("#" + WT + "IvVpp", "ivpg:-1"), ("#" + WT + "IvVpn", "ivpg:1"), ("#" + WT + "IvXpp", "ixpg:-1"), ("#" + WT + "IvXpn", "ixpg:1")]))
    return out
'''
WV_JAVA = r'''# ---- 0.3.74 (oldmenu6): THE WORLD SCREEN'S VIEWS. Shared helpers: a bridge act as the player with a read's token + profile key (null =
# the bridge is not there; a null answer = not on the world thread), clean texts, an answer without its mark, the version note, bars, tabs
M(wtab, r"""
public String wact(String key, String op, String tok, String pk, String arg) {
  if (@PKG@.InvCraft.fn(key) == null) return null;
  this.calls = this.calls + 1;
  Object r = call(key, new Object[] { op, this.playerRef.getUuid(), tok, pk, arg });
  return r instanceof String ? (String) r : "-" + @PKG@.WorldTabData.NULLANS;
}""")
M(wtab, r"""
public static String tx(String s, int n) { return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(s == null ? "" : s.trim()), n); }""")
M(wtab, r"""
public static boolean allowed(String al, String k) { return al != null && k != null && al.indexOf("|" + k + "|") >= 0; }""")
M(wtab, r"""
public static String ansT(String r) {
  String m = @PKG@.InvPage.bare(r);
  return m.length() == 0 ? "" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(m), 118);
}""")
M(wtab, r"""
public static String oldT(String hubKey, String oldText, String offText) {
  Object o = null;
  try { o = @PKG@.HubBar.get(hubKey); } catch (Throwable t) { o = null; }
  return o instanceof Object[] ? oldText : offText;
}""")
M(wtab, r"""
public static String roman(int n) {
  if (n <= 0 || n > 39) return String.valueOf(n);
  String[] t = new String[] { "", "X", "XX", "XXX" };
  String[] o = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX" };
  return t[n / 10] + o[n % 10];
}""")
M(wtab, r"""
public static String durS(String s) {
  long v = @PKG@.InvPage.toLong(s, -1L);
  if (v < 0L) return "?";
  if (v < 60L) return v + "s";
  long m = v / 60L;
  if (m < 60L) return m + "m";
  return (m / 60L) + "h " + (m % 60L) + "m";
}""")
M(wtab, r"""
public static void vtabs(@UCB@ b, @UEB@ ev, String box, String pre, String[] nm, int sel, String act) {
  for (int i = 0; i < nm.length; i++) {
    b.appendInline("#SkyyWtab" + box, @PKG@.WorldTabData.TAB.replace("{I}", pre + i).replace("{S}", i == sel ? @PKG@.WorldTabData.ST1 : @PKG@.WorldTabData.ST0));
    b.set("#SkyyWtab" + pre + i + ".Text", nm[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyWtab" + pre + i, @EVD@.of("a", act + i));
  }
}""")
M(wtab, r"""
public static void fillBar(@UCB@ b, String id, long into, long need, int w) {
  int x = @PKG@.InvPage.barW(into, need, w);
  if (x > 0) b.appendInline("#SkyyWtab" + id, @PKG@.WorldTabData.FILL.replace("{W}", String.valueOf(x)));
}""")
M(wtab, r"""
public static int pagesOf(int n, int per) {
  int p = (n + per - 1) / per;
  return p < 1 ? 1 : p;
}""")
M(wtab, r"""
public static int clampPage(int p, int pages) {
  if (p >= pages) p = pages - 1;
  return p < 0 ? 0 : p;
}""")
M(wtab, r"""
public static String[] cut(String l, int n) { return l.split("\\|", n); }""")
# ======== Q: THE QUESTS VIEW - quest:fn:act state: h| l| w| t| x| (contract: tools/quests_0_4_5_patch.py)
M(wtab, r"""
public void qvHide(@UCB@ b, String head) {
  b.set("#SkyyWtabQvH.Text", head);
  b.set("#SkyyWtabQvb.Visible", false);
  b.set("#SkyyWtabQvC.Text", "");
  this.qOk = false;
}""")
M(wtab, r"""
public void fillQv(@UCB@ b, @UEB@ ev) {
  this.qOk = false;
  this.qAllow = "|";
  this.qLn = new String[0];
  this.qTk = new String[0];
  this.qSkS = new String[0];
  this.qBtn = new int[0];
  String s = wact("quest:fn:act", "state", null, null, null);
  this.qLast = s;
  if (s == null) { qvHide(b, oldT("hub:tab:world:quests", @PKG@.WorldTabData.QVOLD, @PKG@.WorldTabData.QVOFF)); return; }
  String[] ls = s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? ls[0].split("\\|", -1) : new String[0];
  if (h.length < 9) { qvHide(b, @PKG@.WorldTabData.QVFAIL); return; }
  this.qTok = h[1];
  this.qPk = h[2];
  if (!"1".equals(h[3])) { qvHide(b, "Your quests are still loading - try again in a moment."); return; }
  this.qOk = true;
  b.set("#SkyyWtabQvb.Visible", true);
  b.set("#SkyyWtabQvH.Text", "");
  java.util.ArrayList lines = new java.util.ArrayList();
  java.util.ArrayList tasks = new java.util.ArrayList();
  java.util.ArrayList hows = new java.util.ArrayList();
  java.util.ArrayList hints = new java.util.ArrayList();
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("l|")) { String[] f = cut(l, 7); if (f.length >= 7) lines.add(f); }
    else if (l.startsWith("w|")) { String[] f = cut(l, 3); if (f.length >= 3) hows.add(f); }
    else if (l.startsWith("t|")) { String[] f = cut(l, 11); if (f.length >= 11) tasks.add(f); }
    else if (l.startsWith("x|")) { String[] f = cut(l, 4); if (f.length >= 4) hints.add(f); }
  }
  String track = h[4];
  int claims = @PKG@.InvPage.toInt(h[6], 0);
  String[] sel = null;
  for (int j = 0; j < lines.size(); j++) { String[] f = (String[]) lines.get(j); if (f[1].equals(this.qLine)) sel = f; }
  if (sel == null && lines.size() > 0) { sel = (String[]) lines.get(0); this.qLine = sel[1]; this.qSub = 0; this.qPage = 0; }
  if (sel == null) this.qLine = "";
  b.set("#SkyyWtabQvC.Text", lines.size() + (lines.size() == 1 ? " quest line" : " quest lines") + (claims > 0 ? "   -   " + claims + " rewards waiting" : ""));
  // THE LINES (the page's order: tracked, open, locked, all done), 11 a page
  int n = @PKG@.WorldTabData.QLN;
  this.qLPages = pagesOf(lines.size(), n);
  this.qLPage = clampPage(this.qLPage, this.qLPages);
  this.qLn = new String[n];
  for (int k = 0; k < n; k++) {
    String r = "SkyyWtabQvL" + k;
    int ix = this.qLPage * n + k;
    this.qLn[k] = "";
    if (ix >= lines.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) lines.get(ix);
    int rk = @PKG@.InvPage.toInt(f[2], 1);
    long dn = @PKG@.InvPage.toLong(f[3], 0L);
    long ct = @PKG@.InvPage.toLong(f[4], 0L);
    this.qLn[k] = f[1];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[6], 34) + (f[1].equals(track) ? "  (tracked)" : ""));
    b.set("#" + r + "S.Text", (rk == 0 ? "On your HUD" : (rk == 1 ? "Open" : (rk == 2 ? "Locked - not started" : "All done"))) + "   -   " + dn + " / " + ct + " done"
        + ("1".equals(f[5]) ? "   -   daily" : ""));
    if (ct > 0L) fillBar(b, "QvL" + k + "B", dn, ct, @PKG@.WorldTabData.QLBARW);
    b.set("#" + r + "P.Text", f[1].equals(this.qLine) ? "Showing" : "Open");
    ev.addEventBinding(@BT@.Activating, "#" + r + "P", @EVD@.of("a", "ql:" + k));
  }
  b.set("#SkyyWtabQvLpg.Text", "Page " + (this.qLPage + 1) + " / " + this.qLPages);
  b.set("#SkyyWtabQvLp.Visible", this.qLPages > 1);
  if (sel == null) {
    b.set("#SkyyWtabQvN.Text", "No quest lines yet");
    b.set("#SkyyWtabQvS.Text", "New lines come as you play.");
    b.set("#SkyyWtabQvTr.Visible", false);
    b.set("#SkyyWtabQvW.Text", "");
    b.set("#SkyyWtabQvSr.Visible", false);
    for (int i = 0; i < @PKG@.WorldTabData.QTN; i++) b.set("#SkyyWtabQvT" + i + ".Visible", false);
    b.set("#SkyyWtabQvTp.Visible", false);
  } else {
    int rk = @PKG@.InvPage.toInt(sel[2], 1);
    boolean pinned = sel[1].equals(track);
    b.set("#SkyyWtabQvN.Text", tx(sel[6], 60));
    b.set("#SkyyWtabQvS.Text", (rk == 0 ? "On your HUD" : (rk == 1 ? "Open" : (rk == 2 ? "Locked" : "All done"))) + "   -   " + sel[3] + " / " + sel[4] + " done"
        + ("1".equals(sel[5]) ? "   -   Daily jobs: new ones in " + durS(h[7]) : ""));
    b.set("#SkyyWtabQvTr.Visible", rk != 2);
    if (rk != 2) {
      b.set("#SkyyWtabQvTr.Text", pinned ? "Stop tracking" : "Track this line");
      this.qTrArg = sel[1] + "|" + (pinned ? "1" : "0");
      this.qAllow = this.qAllow + "track|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabQvTr", @EVD@.of("a", "qtr").append("t", this.tok));
    }
    String how = "";
    for (int j = 0; j < hows.size(); j++) { String[] f = (String[]) hows.get(j); if (f[1].equals(sel[1])) how = f[2]; }
    b.set("#SkyyWtabQvW.Text", rk == 2 ? "How to start: " + tx(how, 110) : "");
    java.util.ArrayList open = new java.util.ArrayList();
    java.util.ArrayList done = new java.util.ArrayList();
    for (int pass = 0; pass < 2; pass++) {
      for (int j = 0; j < tasks.size(); j++) {
        String[] f = (String[]) tasks.get(j);
        if (!f[1].equals(sel[1])) continue;
        int st = @PKG@.InvPage.toInt(f[3], 0);
        if (pass == 0 && (st == 0 || st == 1 || st == 4)) open.add(f);
        if (pass == 1 && st == 3) open.add(f);
        if (pass == 0 && st == 2) done.add(f);
      }
    }
    b.set("#SkyyWtabQvSr.Visible", rk != 2);
    if (this.qSub < 0 || this.qSub > 1) this.qSub = 0;
    vtabs(b, ev, "QvK", "Qk", new String[] { "Open (" + open.size() + ")", "Done (" + done.size() + ")" }, this.qSub, "qk:");
    b.set("#SkyyWtabQvKn.Text", this.qSub == 0 ? "Open, ready to claim and next in line - skipped ones at the end" : "Finished tasks");
    java.util.ArrayList rows = this.qSub == 0 ? open : done;
    int m = @PKG@.WorldTabData.QTN;
    this.qPages = pagesOf(rows.size(), m);
    this.qPage = clampPage(this.qPage, this.qPages);
    this.qTk = new String[m];
    this.qSkS = new String[m];
    this.qBtn = new int[m];
    for (int i = 0; i < m; i++) {
      String r = "SkyyWtabQvT" + i;
      int ix = this.qPage * m + i;
      this.qTk[i] = "";
      this.qSkS[i] = "";
      this.qBtn[i] = 0;
      if (rk == 2 || ix >= rows.size()) { b.set("#" + r + ".Visible", false); continue; }
      String[] f = (String[]) rows.get(ix);
      int st = @PKG@.InvPage.toInt(f[3], 0);
      if (st < 0 || st > 4) st = 0;
      int fill = @PKG@.InvPage.toInt(f[7], -1);
      String hint = "";
      for (int j = 0; j < hints.size(); j++) { String[] x = (String[]) hints.get(j); if (x[1].equals(f[1]) && x[2].equals(f[2])) hint = x[3]; }
      b.set("#" + r + ".Visible", true);
      b.set("#" + r + "N.Text", (f[5].length() > 0 ? tx(f[5], 8) + "  " : "") + tx(f[10], 60) + ("1".equals(f[4]) ? "  (optional)" : ""));
      hold(b, r + "S", 5, st, @PKG@.WorldTabData.QSTATE[st]);
      b.set("#" + r + "P.Text", f[6].length() > 0 ? tx(f[6], 14) : (st == 2 ? "done" : "not started"));
      if (fill >= 0) fillBar(b, "QvT" + i + "B", (long) fill, 1000L, @PKG@.WorldTabData.QBARW);
      b.set("#" + r + "W.Text", f[8].length() > 0 ? "Where: " + tx(f[8], 40) : "");
      b.set("#" + r + "R.Text", f[9].length() > 0 ? "Reward: " + tx(f[9], 110) : "No reward");
      b.set("#" + r + "H.Text", tx(hint, 118));
      this.qTk[i] = f[1] + "." + f[2];
      int bt = 0;
      if (st == 1) bt = bt | 1;
      if (st == 0 || st == 4 || st == 3) bt = bt | 2;
      this.qSkS[i] = st == 3 ? "1" : "0";
      this.qBtn[i] = bt;
      b.set("#" + r + "C.Visible", (bt & 1) != 0);
      if ((bt & 1) != 0) ev.addEventBinding(@BT@.Activating, "#" + r + "C", @EVD@.of("a", "qcl:" + i).append("t", this.tok));
      b.set("#" + r + "K.Visible", (bt & 2) != 0);
      if ((bt & 2) != 0) {
        b.set("#" + r + "K.Text", st == 3 ? "Unskip" : "Skip");
        ev.addEventBinding(@BT@.Activating, "#" + r + "K", @EVD@.of("a", "qsk:" + i).append("t", this.tok));
      }
    }
    b.set("#SkyyWtabQvTpg.Text", "Page " + (this.qPage + 1) + " / " + this.qPages);
    b.set("#SkyyWtabQvTp.Visible", rk != 2 && this.qPages > 1);
  }
  b.set("#SkyyWtabQvFn.Text", "Every task counts the moment you do it, in any order.");
  b.set("#SkyyWtabQvCa.Visible", claims > 0);
  if (claims > 0) {
    b.set("#SkyyWtabQvCa.Text", "Claim all (" + claims + ")");
    this.qAllow = this.qAllow + "claim|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabQvCa", @EVD@.of("a", "qca").append("t", this.tok));
  }
  boolean hid = "1".equals(h[5]);
  b.set("#SkyyWtabQvHd.Text", hid ? "Show tutorial" : "Hide tutorial");
  this.qHideOp = hid ? "show" : "hide";
  this.qAllow = this.qAllow + "hide|";
  ev.addEventBinding(@BT@.Activating, "#SkyyWtabQvHd", @EVD@.of("a", "qhd").append("t", this.tok));
}""")
# ======== C: THE COLLECTIONS VIEW - coll:fn:act state / detail (contract: tools/collections_0_2_37_patch.py)
M(wtab, r"""
public void cvHide(@UCB@ b, String head) {
  b.set("#SkyyWtabCvH.Text", head);
  b.set("#SkyyWtabCvT.Visible", false);
  b.set("#SkyyWtabCvK.Visible", false);
  b.set("#SkyyWtabCvB.Visible", false);
  b.set("#SkyyWtabCvC.Text", "");
  this.cOk = false;
}""")
M(wtab, r"""
public void fillCvD(@UCB@ b, @UEB@ ev) {
  String s = wact("coll:fn:act", "detail", null, null, this.cId);
  this.cLast = s;
  String[] ls = s == null ? new String[0] : s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? ls[0].split("\\|", 12) : new String[0];
  if (h.length < 12) {
    b.set("#SkyyWtabCvDN.Text", "That collection could not be read");
    b.set("#SkyyWtabCvDM.Text", s == null ? "" : ansT(s));
    b.set("#SkyyWtabCvDG.Text", "");
    b.set("#SkyyWtabCvDy.Visible", false);
    for (int i = 0; i < @PKG@.WorldTabData.CTN; i++) b.set("#SkyyWtabCvDt" + i + ".Visible", false);
    b.set("#SkyyWtabCvDtn.Text", "Pick another collection, or a category above.");
    b.set("#SkyyWtabCvDrh.Text", "RECIPES");
    for (int i = 0; i < @PKG@.WorldTabData.CRN; i++) b.set("#SkyyWtabCvR" + i + ".Visible", false);
    b.set("#SkyyWtabCvRp.Visible", false);
    b.set("#SkyyWtabCvRn.Text", "");
    return;
  }
  this.cTok = h[1];
  this.cPk = h[2];
  String[] m = null;
  String[] bo = null;
  String g = "";
  String y = null;
  java.util.ArrayList rs = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("m|")) m = cut(l, 4);
    else if (l.startsWith("g|")) g = l.substring(2);
    else if (l.startsWith("r|")) { String[] f = cut(l, 5); if (f.length >= 5) rs.add(f); }
    else if (l.startsWith("q|")) { String[] f = cut(l, 7); if (f.length >= 7) qs.add(f); }
    else if (l.startsWith("b|")) bo = cut(l, 4);
    else if (l.startsWith("y|")) y = l.substring(2);
  }
  long sum = @PKG@.InvPage.toLong(h[5], 0L);
  long next = @PKG@.InvPage.toLong(h[9], 0L);
  b.set("#SkyyWtabCvDN.Text", tx(h[11], 50));
  b.set("#SkyyWtabCvDM.Text", m != null && m.length >= 4 ? tx(m[1] + " collection   -   curve " + m[2] + (m[3].length() > 0 ? "   -   From: " + m[3] : ""), 118) : "");
  b.set("#SkyyWtabCvDG.Text", tx(g, 100));
  fillBar(b, "CvDB", sum, next, @PKG@.WorldTabData.CDBARW);
  boolean buyOn = "1".equals(h[10]);
  this.cBuy = "";
  b.set("#SkyyWtabCvDy.Visible", buyOn && (bo != null || y != null));
  b.set("#SkyyWtabCvDyB.Visible", false);
  if (buyOn && bo != null && bo.length >= 4) {
    int nt = @PKG@.InvPage.toInt(bo[1], 0);
    long pr = @PKG@.InvPage.toLong(bo[2], -1L);
    b.set("#SkyyWtabCvDy1.Text", "Buy tier " + roman(nt) + " for " + @PKG@.MenuUtil.fmt(pr) + " coins");
    b.set("#SkyyWtabCvDy2.Text", "Unlocks: " + tx(bo[3], 100));
    b.set("#SkyyWtabCvDy3.Text", "Press Buy, then Buy again within 10 s to pay. The tier's rewards come when you reach it.");
    if (nt > 0 && pr >= 0L) {
      b.set("#SkyyWtabCvDyB.Visible", true);
      this.cBuy = h[3] + "|" + nt + "|" + pr;
      this.cAllow = this.cAllow + "buy|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabCvDyB", @EVD@.of("a", "cbuy").append("t", this.tok));
    }
  } else if (buyOn && y != null) {
    b.set("#SkyyWtabCvDy1.Text", "Coin unlock");
    b.set("#SkyyWtabCvDy2.Text", tx(y, 110));
    b.set("#SkyyWtabCvDy3.Text", "");
  }
  boolean anyNew = false;
  int nt2 = @PKG@.WorldTabData.CTN;
  int st0 = 0;   // fix: a ladder longer than the rows = a window that keeps the NEXT tier (else the first LOCKED one) in view, 2 rows of what is done above it
  if (rs.size() > nt2) {
    int fi = -1;
    for (int i = 0; i < rs.size() && fi < 0; i++) { if ("NEXT".equals(((String[]) rs.get(i))[2])) fi = i; }
    for (int i = 0; i < rs.size() && fi < 0; i++) { if ("LOCKED".equals(((String[]) rs.get(i))[2])) fi = i; }
    if (fi < 0) fi = rs.size() - 1;
    st0 = fi - 2;
    if (st0 > rs.size() - nt2) st0 = rs.size() - nt2;
    if (st0 < 0) st0 = 0;
  }
  for (int i = 0; i < nt2; i++) {
    String r = "SkyyWtabCvDt" + i;
    if (st0 + i >= rs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) rs.get(st0 + i);
    String w = f[2];
    int si = w.equals("DONE") ? 0 : (w.equals("BOUGHT") ? 1 : (w.equals("NEXT") ? 2 : (w.equals("NEW") ? 4 : 3)));
    if (si == 4) anyNew = true;
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", "Tier " + roman(@PKG@.InvPage.toInt(f[1], 0)));
    hold(b, r + "S", 5, si, @PKG@.WorldTabData.CSTATE[si]);
    b.set("#" + r + "A.Text", @PKG@.MenuUtil.fmt(@PKG@.InvPage.toLong(f[3], 0L)));
    b.set("#" + r + "R.Text", tx(f[4], 96));
  }
  int up0 = st0;
  int dn0 = rs.size() - st0 - nt2;
  if (dn0 < 0) dn0 = 0;
  b.set("#SkyyWtabCvDtn.Text", up0 > 0 && dn0 > 0 ? "+" + up0 + " tiers done above, +" + dn0 + " more past these" : (up0 > 0 ? "+" + up0 + " tiers done above these" : (dn0 > 0 ? "+" + dn0 + " more tiers past these" : "")));
  int n = @PKG@.WorldTabData.CRN;
  this.cRPages = pagesOf(qs.size(), n);
  this.cRPage = clampPage(this.cRPage, this.cRPages);
  this.cRec = new String[n];
  b.set("#SkyyWtabCvDrh.Text", "RECIPES  (" + qs.size() + ")");
  for (int i = 0; i < n; i++) {
    String r = "SkyyWtabCvR" + i;
    int ix = this.cRPage * n + i;
    this.cRec[i] = "";
    if (ix >= qs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) qs.get(ix);
    boolean known = "1".equals(f[2]);
    boolean craft = "1".equals(f[5]);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", (f[4].length() > 0 ? tx(f[4], 8) + "  " : "") + tx(f[6], 44));
    b.set("#" + r + "S.Text", "T" + f[3] + "   -   " + (known ? (craft ? "Unlocked - Craft opens it" : "Unlocked") : "Locked - a higher tier unlocks it"));
    b.set("#" + r + "C.Visible", craft);
    if (craft) {
      this.cRec[i] = f[1];
      ev.addEventBinding(@BT@.Activating, "#" + r + "C", @EVD@.of("a", "ccr:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyWtabCvRpg.Text", "Page " + (this.cRPage + 1) + " / " + this.cRPages);
  b.set("#SkyyWtabCvRp.Visible", this.cRPages > 1);
  b.set("#SkyyWtabCvRn.Text", qs.size() == 0 ? "No recipes come from this collection." : "By tier, then name.");
  if (anyNew) {   // what drawing the page does once: its NEW markers cleared (CollNew.seen)
    String r = wact("coll:fn:act", "seen", h[1], h[2], h[3]);
    this.cSeen = this.cSeen + 1;
    if (r != null && r.startsWith("-")) @PKG@.MenuUtil.warn("world screen: coll:fn:act seen " + h[3] + ": " + r);
  }
}""")
M(wtab, r"""
public void fillCv(@UCB@ b, @UEB@ ev) {
  this.cOk = false;
  this.cAllow = "|";
  this.cIds = new String[0];
  this.cRec = new String[0];
  this.cKc = new int[0];
  this.cBuy = "";
  String s = wact("coll:fn:act", "state", null, null, null);
  this.cLast = s;
  if (s == null) { cvHide(b, oldT("hub:tab:character:collections", @PKG@.WorldTabData.CVOLD, @PKG@.WorldTabData.CVOFF)); return; }
  String[] ls = s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? ls[0].split("\\|", -1) : new String[0];
  if (h.length < 10) { cvHide(b, @PKG@.WorldTabData.CVFAIL); return; }
  this.cTok = h[1];
  this.cPk = h[2];
  if (!"1".equals(h[3])) { cvHide(b, "Collections are not loaded right now - try again in a moment."); return; }
  this.cOk = true;
  b.set("#SkyyWtabCvT.Visible", true);
  b.set("#SkyyWtabCvK.Visible", true);
  b.set("#SkyyWtabCvB.Visible", true);
  b.set("#SkyyWtabCvH.Text", "");
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList cs = new java.util.ArrayList();
  java.util.HashMap ps = new java.util.HashMap();
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) { String[] f = cut(l, 9); if (f.length >= 9) ks.add(f); }
    else if (l.startsWith("c|")) { String[] f = cut(l, 8); if (f.length >= 8) cs.add(f); }
    else if (l.startsWith("p|")) { String[] f = cut(l, 4); if (f.length >= 4) ps.put(f[1], f); }
  }
  b.set("#SkyyWtabCvT.Text", "Tiers reached " + @PKG@.MenuUtil.fmt(@PKG@.InvPage.toLong(h[4], 0L)) + " / " + @PKG@.MenuUtil.fmt(@PKG@.InvPage.toLong(h[5], 0L))
      + "      Maxed " + tx(h[6], 8) + "      Found " + tx(h[7], 8) + "      Recipes unlocked " + tx(h[8], 8));
  b.set("#SkyyWtabCvC.Text", cs.size() + " collections");
  if (this.cWant != null && this.cWant.length() > 0) {   // the codex card (Combat) / a skill page (that skill's category)
    for (int j = 0; j < ks.size(); j++) {
      String[] f = (String[]) ks.get(j);
      if (f[8].trim().equalsIgnoreCase(this.cWant)) { this.cCat = @PKG@.InvPage.toInt(f[1], -1); this.cId = ""; this.cPage = 0; }
    }
    this.cWant = "";
  }
  int nk = @PKG@.WorldTabData.CKN;
  this.cKc = new int[nk];
  String catName = "";
  for (int k = 0; k < nk; k++) {
    String r = "SkyyWtabCvK" + k;
    this.cKc[k] = -1;
    if (k >= ks.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) ks.get(k);
    int cat = @PKG@.InvPage.toInt(f[1], -1);
    this.cKc[k] = cat;
    if (cat == this.cCat) catName = f[8];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[8], 24));
    b.set("#" + r + "F.Text", "Found " + f[2] + " / " + f[3]);
    b.set("#" + r + "D.Text", "Tiers " + f[4] + " / " + f[5] + "   -   maxed " + f[6]);
    b.set("#" + r + "B.Text", cat == this.cCat ? "Showing" : "Open");
    ev.addEventBinding(@BT@.Activating, "#" + r + "B", @EVD@.of("a", "cc:" + k));
  }
  boolean det = this.cId != null && this.cId.length() > 0;
  b.set("#SkyyWtabCvD.Visible", det);
  b.set("#SkyyWtabCvG.Visible", !det);
  if (det) { fillCvD(b, ev); return; }
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int j = 0; j < cs.size(); j++) { String[] f = (String[]) cs.get(j); if (@PKG@.InvPage.toInt(f[2], -9) == this.cCat) rows.add(f); }
  int n = @PKG@.WorldTabData.CCN;
  this.cPages = pagesOf(rows.size(), n);
  this.cPage = clampPage(this.cPage, this.cPages);
  this.cIds = new String[n];
  b.set("#SkyyWtabCvGh.Text", this.cCat < 0 || catName.length() == 0 ? "Pick a category above to see its collections." : tx(catName, 30).toUpperCase() + "  -  " + rows.size() + " collections");
  for (int i = 0; i < n; i++) {
    String r = "SkyyWtabCvC" + i;
    int ix = this.cPage * n + i;
    this.cIds[i] = "";
    if (catName.length() == 0 || ix >= rows.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) rows.get(ix);
    long sum = @PKG@.InvPage.toLong(f[3], 0L);
    long next = @PKG@.InvPage.toLong(f[6], 0L);
    String[] p = (String[]) ps.get(f[1]);
    boolean found = sum > 0L;
    this.cIds[i] = f[1];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[7], 34));
    b.set("#" + r + "P.Text", found ? (p != null ? tx(p[2], 44) : "Tier " + roman(@PKG@.InvPage.toInt(f[4], 0))) : "Not found yet");
    if (found) fillBar(b, "CvC" + i + "B", sum, next, @PKG@.WorldTabData.CCBARW);
    b.set("#" + r + "S.Text", found ? (p != null ? tx(p[3], 54) : "") : "Pick one up to start this collection");
    ev.addEventBinding(@BT@.Activating, "#" + r + "V", @EVD@.of("a", "cv:" + i));
  }
  b.set("#SkyyWtabCvGpg.Text", "Page " + (this.cPage + 1) + " / " + this.cPages);
  b.set("#SkyyWtabCvGp.Visible", catName.length() > 0 && this.cPages > 1);
  b.set("#SkyyWtabCvGn.Text", catName.length() == 0 ? "" : "Found ones first, then the ones you have not found yet. Tier rewards pay when you reach them.");
}""")
# ======== E: THE EXPLORE VIEW - explore:fn:act state / checklist (contract: tools/exploration_0_3_5_patch.py)
M(wtab, r"""
public void evHide(@UCB@ b, String head) {
  b.set("#SkyyWtabEvH.Text", head);
  b.set("#SkyyWtabEvL.Text", "");
  b.set("#SkyyWtabEvSr.Visible", false);
  b.set("#SkyyWtabEvB.Visible", false);
  b.set("#SkyyWtabEvC.Text", "");
  this.eOk = false;
}""")
# the title id the bridge checks (ExpDefs.T_ID): the title's name, lower case, no spaces (tools/exploration_0_3_5_patch.py; see 0.3.74 notes)
M(wtab, r"""
public static String titleId(String n) {
  if (n == null) return "";
  StringBuilder sb = new StringBuilder();
  String s = n.trim().toLowerCase();
  for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); if (c != ' ' && c != '|') sb.append(c); }
  return sb.toString();
}""")
M(wtab, r"""
public void evZones(@UCB@ b, java.util.ArrayList gs, java.util.ArrayList zs) {
  java.util.ArrayList[] col = new java.util.ArrayList[] { new java.util.ArrayList(), new java.util.ArrayList() };
  for (int side = 0; side < 2; side++) {
    for (int j = 0; j < gs.size(); j++) {
      String[] g = (String[]) gs.get(j);
      if (@PKG@.InvPage.toInt(g[2], 0) != side) continue;
      col[side].add(new String[] { "0", tx(g[6], 40), g[4] + " / " + g[5] + " found" });
      for (int i = 0; i < zs.size(); i++) {
        String[] z = (String[]) zs.get(i);
        if (!z[1].equals(g[1])) continue;
        boolean got = "1".equals(z[3]);
        col[side].add(new String[] { "1", "    " + tx(z[5], 40), got ? "found" : @PKG@.MenuUtil.fmt(@PKG@.InvPage.toLong(z[4], 0L)) + " XP" });
      }
    }
  }
  int n = @PKG@.WorldTabData.EZN;
  int p0 = pagesOf(col[0].size(), n);
  int p1 = pagesOf(col[1].size(), n);
  this.eZPages = p0 > p1 ? p0 : p1;
  this.eZPage = clampPage(this.eZPage, this.eZPages);
  for (int c = 0; c < 2; c++) {
    for (int k = 0; k < n; k++) {
      String r = "SkyyWtabEvZ" + (c * n + k);
      int ix = this.eZPage * n + k;
      if (ix >= col[c].size()) { b.set("#" + r + ".Visible", false); continue; }
      String[] e = (String[]) col[c].get(ix);
      b.set("#" + r + ".Visible", true);
      hold(b, r + "N", 2, "0".equals(e[0]) ? 0 : 1, e[1]);
      b.set("#" + r + "V.Text", e[2]);
    }
  }
  b.set("#SkyyWtabEvZpg.Text", "Page " + (this.eZPage + 1) + " / " + this.eZPages);
  b.set("#SkyyWtabEvZp.Visible", this.eZPages > 1);
}""")
M(wtab, r"""
public void evTitles(@UCB@ b, @UEB@ ev, java.util.ArrayList ts, java.util.HashMap rt, String[] h) {
  int sel = @PKG@.InvPage.toInt(h[5], -1);
  String wear = "";
  for (int j = 0; j < ts.size(); j++) { String[] f = (String[]) ts.get(j); if ("1".equals(f[3])) wear = f[5]; }
  b.set("#SkyyWtabEvTs.Text", "Wearing: " + (sel >= 0 && wear.length() > 0 ? tx(wear, 30) : "no title") + "   -   " + h[6] + " of " + h[7] + " titles earned");
  b.set("#SkyyWtabEvTn.Visible", sel >= 0);
  if (sel >= 0) {
    this.eAllow = this.eAllow + "none|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabEvTn", @EVD@.of("a", "etn").append("t", this.tok));
  }
  int n = 2 * @PKG@.WorldTabData.ETN;
  this.eTPages = pagesOf(ts.size(), n);
  this.eTPage = clampPage(this.eTPage, this.eTPages);
  this.eTi = new String[n];
  for (int j = 0; j < n; j++) {
    String r = "SkyyWtabEvT" + j;
    int ix = this.eTPage * n + j;
    this.eTi[j] = "";
    if (ix >= ts.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) ts.get(ix);
    boolean earned = "1".equals(f[2]);
    boolean use = "1".equals(f[3]);
    b.set("#" + r + ".Visible", true);
    hold(b, r + "N", 3, use ? 0 : (earned ? 1 : 2), tx(f[5], 30) + (use ? "   (wearing)" : (earned ? "" : "   (locked)")));
    Object w = rt.get(f[1]);
    b.set("#" + r + "R.Text", w instanceof String ? tx((String) w, 70) : "");
    boolean u = earned && !use;
    b.set("#" + r + "U.Visible", u);
    if (u) {
      this.eTi[j] = f[1] + "|" + titleId(f[5]);
      ev.addEventBinding(@BT@.Activating, "#" + r + "U", @EVD@.of("a", "et:" + j).append("t", this.tok));
    }
  }
  b.set("#SkyyWtabEvTpg.Text", "Page " + (this.eTPage + 1) + " / " + this.eTPages);
  b.set("#SkyyWtabEvTp.Visible", this.eTPages > 1);
}""")
M(wtab, r"""
public void evCheck(@UCB@ b, @UEB@ ev, java.util.ArrayList is, String on) {
  int n = @PKG@.WorldTabData.ECIN;
  this.eIs = new String[n];
  if (!"1".equals(on)) {
    b.set("#SkyyWtabEvCl.Visible", false);
    b.set("#SkyyWtabEvCrN.Text", "Island checklists");
    b.set("#SkyyWtabEvCrS.Text", "Island checklists are turned off on this server.");
    b.set("#SkyyWtabEvCrw.Visible", false);
    b.set("#SkyyWtabEvCrf.Text", "");
    b.set("#SkyyWtabEvCrp.Visible", false);
    return;
  }
  b.set("#SkyyWtabEvCl.Visible", true);
  boolean keep = false;
  for (int j = 0; j < is.size(); j++) { String[] f = (String[]) is.get(j); if (f[1].equals(this.eWf)) keep = true; }
  if (!keep) {
    this.eWf = "";
    for (int j = 0; j < is.size() && this.eWf.length() == 0; j++) { String[] f = (String[]) is.get(j); if ("1".equals(f[2])) this.eWf = f[1]; }
    if (this.eWf.length() == 0 && is.size() > 0) this.eWf = ((String[]) is.get(0))[1];
    this.eCPage = 0;
  }
  this.eIPages = pagesOf(is.size(), n);
  this.eIPage = clampPage(this.eIPage, this.eIPages);
  for (int k = 0; k < n; k++) {
    String r = "SkyyWtabEvCi" + k;
    int ix = this.eIPage * n + k;
    this.eIs[k] = "";
    if (ix >= is.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) is.get(ix);
    int pct = @PKG@.InvPage.toInt(f[7], 0);
    this.eIs[k] = f[1];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[8], 34) + ("1".equals(f[2]) ? "  (you are here)" : ""));
    b.set("#" + r + "S.Text", f[3] + " / " + f[4] + " done   -   secrets " + f[5] + " / " + f[6] + "   -   " + pct + String.valueOf((char) 37));
    fillBar(b, "EvCi" + k + "B", (long) pct, 100L, @PKG@.WorldTabData.ECIBARW);
    b.set("#" + r + "Go.Text", f[1].equals(this.eWf) ? "Showing" : "Show");
    ev.addEventBinding(@BT@.Activating, "#" + r + "Go", @EVD@.of("a", "ei:" + k));
  }
  b.set("#SkyyWtabEvCipg.Text", "Page " + (this.eIPage + 1) + " / " + this.eIPages);
  b.set("#SkyyWtabEvCip.Visible", this.eIPages > 1);
  if (this.eWf.length() == 0) {
    b.set("#SkyyWtabEvCrN.Text", "No island checklists yet");
    b.set("#SkyyWtabEvCrS.Text", "Islands with a checklist show here.");
    b.set("#SkyyWtabEvCrw.Visible", false);
    b.set("#SkyyWtabEvCrf.Text", "");
    b.set("#SkyyWtabEvCrp.Visible", false);
    return;
  }
  String s = wact("explore:fn:act", "checklist", null, null, this.eWf);
  String[] ls = s == null ? new String[0] : s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? ls[0].split("\\|", 12) : new String[0];
  if (h.length < 12) {
    b.set("#SkyyWtabEvCrN.Text", "");
    b.set("#SkyyWtabEvCrS.Text", s == null ? "" : ansT(s));
    b.set("#SkyyWtabEvCrw.Visible", false);
    b.set("#SkyyWtabEvCrf.Text", "");
    b.set("#SkyyWtabEvCrp.Visible", false);
    return;
  }
  java.util.ArrayList es = new java.util.ArrayList();
  String rw = "";
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("e|")) { String[] f = cut(l, 4); if (f.length >= 4) es.add(f); }
    else if (l.startsWith("f|")) rw = l.substring(2);
  }
  int pct = @PKG@.InvPage.toInt(h[9], 0);
  b.set("#SkyyWtabEvCrN.Text", tx(h[11], 40) + ("1".equals(h[4]) ? "  (you are here)" : ""));
  b.set("#SkyyWtabEvCrS.Text", h[5] + " / " + h[6] + " done   -   secrets " + h[7] + " / " + h[8] + "   -   " + pct + String.valueOf((char) 37));
  fillBar(b, "EvCrB", (long) pct, 100L, @PKG@.WorldTabData.ECRBARW);
  b.set("#SkyyWtabEvCrw.Visible", true);
  int m = 2 * @PKG@.WorldTabData.ECRN;
  this.eCPages = pagesOf(es.size(), m);
  this.eCPage = clampPage(this.eCPage, this.eCPages);
  for (int j = 0; j < m; j++) {
    String r = "SkyyWtabEvCe" + j;
    int ix = this.eCPage * m + j;
    if (ix >= es.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) es.get(ix);
    boolean dn = "1".equals(f[1]);
    b.set("#" + r + ".Visible", true);
    hold(b, r + "N", 2, dn ? 0 : 1, (dn ? "Done  " : "") + tx(f[3], 50));
    b.set("#" + r + "V.Text", tx(f[2], 14));
  }
  b.set("#SkyyWtabEvCrf.Text", tx(rw, 110));
  b.set("#SkyyWtabEvCrpg.Text", "Page " + (this.eCPage + 1) + " / " + this.eCPages);
  b.set("#SkyyWtabEvCrp.Visible", this.eCPages > 1);
}""")
M(wtab, r"""
public void fillEv(@UCB@ b, @UEB@ ev) {
  this.eOk = false;
  this.eAllow = "|";
  this.eTi = new String[0];
  this.eIs = new String[0];
  String s = wact("explore:fn:act", "state", null, null, null);
  this.eLast = s;
  if (s == null) { evHide(b, oldT("hub:tab:world:explore", @PKG@.WorldTabData.EVOLD, @PKG@.WorldTabData.EVOFF)); return; }
  String[] ls = s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? ls[0].split("\\|", 11) : new String[0];
  if (h.length < 11) { evHide(b, @PKG@.WorldTabData.EVFAIL); return; }
  this.eTok = h[1];
  this.ePk = h[2];
  this.eOk = true;
  b.set("#SkyyWtabEvSr.Visible", true);
  b.set("#SkyyWtabEvB.Visible", true);
  String v = "";
  String q = "";
  String u = "";
  Object[] os = new Object[8];
  java.util.ArrayList gs = new java.util.ArrayList();
  java.util.ArrayList zs = new java.util.ArrayList();
  java.util.ArrayList ts = new java.util.ArrayList();
  java.util.ArrayList is = new java.util.ArrayList();
  java.util.HashMap rt = new java.util.HashMap();
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("v|")) v = l.substring(2);
    else if (l.startsWith("q|")) q = l.substring(2);
    else if (l.startsWith("u|")) u = l.substring(2);
    else if (l.startsWith("o|")) { String[] f = cut(l, 5); int k = f.length >= 5 ? @PKG@.InvPage.toInt(f[1], -1) : -1; if (k >= 0 && k < 8) os[k] = f; }
    else if (l.startsWith("g|")) { String[] f = cut(l, 7); if (f.length >= 7) gs.add(f); }
    else if (l.startsWith("z|")) { String[] f = cut(l, 6); if (f.length >= 6) zs.add(f); }
    else if (l.startsWith("t|")) { String[] f = cut(l, 6); if (f.length >= 6) ts.add(f); }
    else if (l.startsWith("r|")) { String[] f = cut(l, 3); if (f.length >= 3) rt.put(f[1], f[2]); }
    else if (l.startsWith("i|")) { String[] f = cut(l, 9); if (f.length >= 9) is.add(f); }
  }
  b.set("#SkyyWtabEvH.Text", "1".equals(h[3]) ? tx(v, 118) : "");
  b.set("#SkyyWtabEvL.Text", tx(h[10], 100));
  b.set("#SkyyWtabEvC.Text", "Titles " + h[6] + " / " + h[7]);
  if (this.eSub < 0 || this.eSub > 3) this.eSub = 0;
  vtabs(b, ev, "EvK", "Ek", @PKG@.WorldTabData.ESUB, this.eSub, "ek:");
  b.set("#SkyyWtabEvKn.Text", h[9].length() > 0 ? "You are in " + tx(h[9], 40) : "");
  b.set("#SkyyWtabEvO.Visible", this.eSub == 0);
  b.set("#SkyyWtabEvZ.Visible", this.eSub == 1);
  b.set("#SkyyWtabEvT.Visible", this.eSub == 2);
  b.set("#SkyyWtabEvCk.Visible", this.eSub == 3);
  if (this.eSub == 0) {
    for (int k = 0; k < 8; k++) {
      String r = "SkyyWtabEvO" + k;
      if (os[k] == null) { b.set("#" + r + ".Visible", false); continue; }
      String[] o = (String[]) os[k];
      String[] w = @PKG@.MarketTab.wrap2(@PKG@.MenuUtil.safe(o[4]), 58);
      b.set("#" + r + ".Visible", true);
      b.set("#" + r + "H.Text", tx(o[2], 40).toUpperCase());
      b.set("#" + r + "V.Text", tx(o[3], 34));
      b.set("#" + r + "S.Text", w[0]);
      b.set("#" + r + "T.Text", w[1]);
    }
    b.set("#SkyyWtabEvOq.Text", tx(q, 118));
    b.set("#SkyyWtabEvOu.Text", tx(u, 118));
    b.set("#SkyyWtabEvOv.Text", "1".equals(h[3]) ? "" : tx(v, 118));
  } else if (this.eSub == 1) evZones(b, gs, zs);
  else if (this.eSub == 2) evTitles(b, ev, ts, rt, h);
  else evCheck(b, ev, is, h[8]);
}""")
# ======== I: THE ISLAND VIEW - island:fn:act state "200|200|200|200" (contract: tools/islands_0_5_27_patch.py)
M(wtab, r"""
public static String roleN(int r) {
  if (r == 9) return "Server admin";
  if (r < 0) return "Banned";
  if (r == 0) return "Visitor";
  if (r == 1) return "Trusted";
  if (r == 2) return "Member";
  if (r == 3) return "Admin";
  return "Owner";
}""")
M(wtab, r"""
public static String dateOf(String ms) {
  try { return new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date(Long.parseLong(ms.trim()))); } catch (Throwable t) { return ""; }
}""")
M(wtab, r"""
public static String two(int i) { return i < 10 ? "0" + i : String.valueOf(i % 100); }""")
M(wtab, r"""
public void ivHide(@UCB@ b, String head) {
  b.set("#SkyyWtabIvH.Text", head);
  b.set("#SkyyWtabIvR.Text", "");
  b.set("#SkyyWtabIvSr.Visible", false);
  b.set("#SkyyWtabIvB.Visible", false);
  b.set("#SkyyWtabIvC.Text", "");
  this.iOk = false;
}""")
M(wtab, r"""
public void ivPanels(@UCB@ b, int show) {
  String[] p = new String[] { "IvO", "IvM", "IvP", "IvV", "IvI" };
  for (int i = 0; i < p.length; i++) b.set("#SkyyWtab" + p[i] + ".Visible", i == show);
}""")
M(wtab, r"""
public void ivOverview(@UCB@ b, @UEB@ ev, String[] h, String name, String zc, String rb, String[] inv) {
  boolean has = "1".equals(h[1]);
  int rank = @PKG@.InvPage.toInt(h[4], 0);
  boolean own = "1".equals(h[5]);
  String arm = h[25];
  b.set("#SkyyWtabIvOz.Text", zc == null ? "" : tx(zc, 118));
  b.set("#SkyyWtabIvOb.Visible", true);
  b.set("#SkyyWtabIvOg.Visible", false);
  if (!has && own) {
    b.set("#SkyyWtabIvO1.Text", "You have no island yet");
    b.set("#SkyyWtabIvO2.Text", "Your private sky island is where you farm, build and later keep minions.");
    b.set("#SkyyWtabIvO3.Text", "It is created the first time you go there.");
    b.set("#SkyyWtabIvO4.Text", "");
    b.set("#SkyyWtabIvOg.Visible", true);
    b.set("#SkyyWtabIvGo.Text", "Create my island");
    b.set("#SkyyWtabIvGoh.Text", "Creates your island and takes you there (this screen closes).");
    this.iAllow = this.iAllow + "create|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvGo", @EVD@.of("a", "iv:create").append("t", this.tok));
  } else if (!has) {
    b.set("#SkyyWtabIvO1.Text", "Island not available");
    b.set("#SkyyWtabIvO2.Text", "The island you are a co-op member of is not available right now - ask its owner.");
    b.set("#SkyyWtabIvO3.Text", "");
    b.set("#SkyyWtabIvO4.Text", "");
  } else {
    int mode = @PKG@.InvPage.toInt(h[13], 0);
    b.set("#SkyyWtabIvO1.Text", "Owner: " + tx(name, 40) + (own ? "   (that is you)" : "   - you are a co-op " + roleN(rank) + " here"));
    b.set("#SkyyWtabIvO2.Text", "Co-op: " + h[7] + " / " + h[8] + " players      Trusted: " + h[9] + "      Banned: " + h[11]);
    b.set("#SkyyWtabIvO3.Text", "Visits: " + @PKG@.WorldTabData.IMODE[mode < 0 || mode > 2 ? 0 : mode] + " (limit " + h[14] + ")      Visitors now: " + h[19]
        + "      PvP: " + ("1".equals(h[17]) ? "ON" : "off") + "      Mob spawning: " + ("1".equals(h[18]) ? "on" : "off"));
    b.set("#SkyyWtabIvO4.Text", "World: " + tx(h[27], 60) + ("1".equals(h[20]) ? "  (loaded)" : "  (not loaded - it loads when someone goes there)"));
    if (rank >= 2) {
      b.set("#SkyyWtabIvOg.Visible", true);
      b.set("#SkyyWtabIvGo.Text", "Go to island");
      b.set("#SkyyWtabIvGoh.Text", "Same as /island. Closes this screen and takes you there.");
      this.iAllow = this.iAllow + "go|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvGo", @EVD@.of("a", "iv:go").append("t", this.tok));
    }
  }
  b.set("#SkyyWtabIvOi.Visible", inv != null);
  if (inv != null) {
    boolean ok = "1".equals(inv[2]);
    b.set("#SkyyWtabIvOiq.Text", tx(inv[4], 30) + " invited you to join " + tx(inv[5], 30) + "'s island - " + inv[1] + " s left");
    b.set("#SkyyWtabIvOis.Text", ok ? "Joining uses your current profile." : "You can't accept: " + tx(inv[3], 100));
    b.set("#SkyyWtabIvOy.Visible", ok);
    if (ok) {
      this.iAllow = this.iAllow + "acc|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvOy", @EVD@.of("a", "iv:acc").append("t", this.tok));
    }
    this.iAllow = this.iAllow + "dec|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvOn", @EVD@.of("a", "iv:dec").append("t", this.tok));
  }
  boolean owner = rank == 4 && has;
  b.set("#SkyyWtabIvOo.Visible", owner);
  b.set("#SkyyWtabIvOon.Text", owner ? "Reset rebuilds your island from scratch with a fresh starter kit. Members, trusted players, bans and settings stay. Once every " + h[23] + " h." : "");
  if (owner) {
    int nm = @PKG@.InvPage.toInt(h[7], 1) - 1;
    b.set("#SkyyWtabIvDb.Visible", nm > 0);
    if (nm > 0) {
      b.set("#SkyyWtabIvDb.Text", "disb".equals(arm) ? "Click again to DISBAND" : "Disband co-op (" + nm + ")");
      this.iAllow = this.iAllow + "disb|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvDb", @EVD@.of("a", "iv:disb").append("t", this.tok));
    }
    boolean canReset = rb != null && rb.length() == 0;
    b.set("#SkyyWtabIvRs.Visible", canReset);
    b.set("#SkyyWtabIvRsn.Text", canReset ? "" : "Reset island: " + (rb == null ? "only while you are online" : ansT(rb)));
    if (canReset) {
      b.set("#SkyyWtabIvRs.Text", "reset2".equals(arm) ? "Really? Last click" : ("reset1".equals(arm) ? "Delete everything?" : "Reset island"));
      this.iAllow = this.iAllow + "reset|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvRs", @EVD@.of("a", "iv:reset").append("t", this.tok));
    }
  }
  boolean mem = has && (rank == 2 || rank == 3);
  b.set("#SkyyWtabIvOl.Visible", mem);
  if (mem) {
    b.set("#SkyyWtabIvLv.Text", "leave".equals(arm) ? "Click again to leave" : "Leave island");
    b.set("#SkyyWtabIvLvn.Text", "Your own island stays saved and comes back when you leave.");
    this.iAllow = this.iAllow + "leave|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvLv", @EVD@.of("a", "iv:leave").append("t", this.tok));
  }
}""")
M(wtab, r"""
public void ivMembers(@UCB@ b, @UEB@ ev, String[] h, java.util.ArrayList ms, java.util.ArrayList ts, String[] cn, String pend, String[] dl) {
  int rank = @PKG@.InvPage.toInt(h[4], 0);
  boolean canInv = "1".equals(h[21]);
  String arm = h[25];
  String at = String.valueOf((char) 64) + "IN";
  b.set("#SkyyWtabIvMi.Visible", rank >= 3);
  b.set("#SkyyWtabIvMih.Text", rank >= 3 ? (canInv ? "Invite to co-op = they join " + (rank == 4 ? "your" : "the") + " island (their /island comes here).   " : "")
      + "Trust = build rights only, their /island stays their own.   Enter only explains the buttons." : "Only the owner and island admins invite or trust players.");
  if (rank >= 3) {
    b.set("#SkyyWtabIvMf.Value", this.iKeepN);
    b.set("#SkyyWtabIvMinv.Visible", canInv);
    if (canInv) {
      this.iAllow = this.iAllow + "inv|";
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvMinv", @EVD@.of("a", "iv:inv").append("t", this.tok).append(at, "#SkyyWtabIvMf.Value"));
    }
    this.iAllow = this.iAllow + "trust|name|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvMtr", @EVD@.of("a", "iv:trust").append("t", this.tok).append(at, "#SkyyWtabIvMf.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyWtabIvMf", @EVD@.of("a", "iv:name").append("t", this.tok).append(at, "#SkyyWtabIvMf.Value"), false);
  }
  int total = cn != null && cn.length >= 9 ? @PKG@.InvPage.toInt(cn[2], ms.size()) : ms.size();
  b.set("#SkyyWtabIvMh.Text", "CO-OP MEMBERS  (" + total + " / " + h[8] + ")");
  int n = @PKG@.WorldTabData.IMN;
  this.iMPages = pagesOf(ms.size(), n);
  this.iMPage = clampPage(this.iMPage, this.iMPages);
  this.iMk = new String[n];
  this.iMb = new int[n];
  for (int i = 0; i < n; i++) {
    String r = "SkyyWtabIvM" + i;
    int ix = this.iMPage * n + i;
    this.iMk[i] = "";
    this.iMb[i] = 0;
    if (ix >= ms.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) ms.get(ix);
    int rr = @PKG@.InvPage.toInt(f[2], 2);
    boolean me = "1".equals(f[6]);
    boolean on = "1".equals(f[3]);
    boolean other = "1".equals(f[4]);
    String since = dateOf(f[5]);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[7], 32) + (me ? "  (you)" : ""));
    b.set("#" + r + "S.Text", roleN(rr) + "   -   " + (on ? "online" : (other ? "online on another profile" : "offline")) + "   -   "
        + (rr == 4 ? "leader" : (since.length() > 0 ? "since " + since : "member")));
    int bt = 0;
    if (rank == 4 && rr != 4 && !me) bt = (rr == 2 ? 1 : 2) | 4;
    this.iMk[i] = f[1];
    this.iMb[i] = bt;
    b.set("#" + r + "P.Visible", (bt & 3) != 0);
    b.set("#" + r + "K.Visible", (bt & 4) != 0);
    if ((bt & 3) != 0) {
      b.set("#" + r + "P.Text", (bt & 1) != 0 ? "Promote" : "Demote");
      ev.addEventBinding(@BT@.Activating, "#" + r + "P", @EVD@.of("a", ((bt & 1) != 0 ? "im:pro:" : "im:dem:") + i).append("t", this.tok));
    }
    if ((bt & 4) != 0) {
      b.set("#" + r + "K.Text", arm.equals("kk:" + f[1]) ? "Sure?" : "Kick");
      ev.addEventBinding(@BT@.Activating, "#" + r + "K", @EVD@.of("a", "im:kick:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyWtabIvMpg.Text", "Page " + (this.iMPage + 1) + " / " + this.iMPages);
  b.set("#SkyyWtabIvMp.Visible", this.iMPages > 1);
  b.set("#SkyyWtabIvMn.Text", (pend != null && pend.length() > 0 ? "Invited: " + tx(pend, 90) + "   " : "") + (total > ms.size() ? "... and " + (total - ms.size()) + " more - /island info lists everyone." : ""));
  int tt = cn != null && cn.length >= 9 ? @PKG@.InvPage.toInt(cn[4], ts.size()) : ts.size();
  b.set("#SkyyWtabIvTh.Text", "TRUSTED - build only  (" + tt + " / " + h[10] + ")");
  int m = @PKG@.WorldTabData.ITN;
  this.iTPages = pagesOf(ts.size(), m);
  this.iTPage = clampPage(this.iTPage, this.iTPages);
  this.iTk = new String[m];
  for (int i = 0; i < m; i++) {
    String r = "SkyyWtabIvT" + i;
    int ix = this.iTPage * m + i;
    this.iTk[i] = "";
    if (ix >= ts.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) ts.get(ix);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[4], 26) + (f[3].length() > 0 ? "  (" + tx(f[3], 16) + ")" : "") + ("1".equals(f[2]) ? "  (you)" : ""));
    b.set("#" + r + "U.Visible", rank >= 3);
    if (rank >= 3) {
      this.iTk[i] = f[1];
      ev.addEventBinding(@BT@.Activating, "#" + r + "U", @EVD@.of("a", "it:un:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyWtabIvTpg.Text", "Page " + (this.iTPage + 1) + " / " + this.iTPages);
  b.set("#SkyyWtabIvTp.Visible", this.iTPages > 1);
  String th = "";
  if (ts.size() == 0 && dl != null && dl.length >= 3) {   // the page's 'Nobody yet' line, made from the island's grid (d|)
    String nt = dl[2];
    th = "Nobody yet. Trusted players may place and break blocks, use crafting benches and pick up items" + (nt.length() > 0 ? " - not " + nt : "") + ".";
    if (th.length() > 160) th = "Nobody yet. Trusted players may place and break blocks, use crafting benches and pick up items (the Permissions tab lists the rest).";
    if (!"1".equals(dl[1])) th = "Nobody yet. The Permissions tab shows what Trusted players may do on this island.";
  }
  String[] w = @PKG@.MarketTab.wrap2(@PKG@.MenuUtil.safe(th), 84);
  b.set("#SkyyWtabIvTn.Text", w[0]);
  b.set("#SkyyWtabIvTo.Text", w[1] + (tt > ts.size() ? (w[1].length() > 0 ? "  " : "") + "+" + (tt - ts.size()) + " more" : ""));
}""")
M(wtab, r"""
public void ivPerms(@UCB@ b, @UEB@ ev, String[] h, java.util.ArrayList fs) {
  int rank = @PKG@.InvPage.toInt(h[4], 0);
  boolean ed = rank >= 3;
  String arm = h[25];
  b.set("#SkyyWtabIvPtx.Text", ed ? "Click a cell to allow or deny. Allowing a role also allows every role to its right; denying it also denies every role to its left."
      : "Only the owner and island admins can change these.");
  b.set("#SkyyWtabIvPdef.Visible", ed);
  if (ed) {
    b.set("#SkyyWtabIvPdef.Text", "pdef".equals(arm) ? "Click again to reset" : "Reset to defaults");
    this.iAllow = this.iAllow + "pdef|perm|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvPdef", @EVD@.of("a", "iv:pdef").append("t", this.tok));
  }
  b.set("#SkyyWtabIvPs.Text", "1".equals(h[22]) ? "Server rule: a player who has a role here on ANOTHER of their profiles only gets doors, seats and mobs while on the wrong profile."
      : "Server rule: a player who has a role here on ANOTHER of their profiles can't drop items while on the wrong profile.");
  int n = @PKG@.WorldTabData.IPN;
  this.iPf = new int[n];
  this.iPm = new int[n];
  String[] cols = new String[] { "Visitor", "Trusted", "Member", "Admin" };
  for (int i = 0; i < n; i++) {
    String r = "SkyyWtabIvP" + i;
    this.iPf[i] = -1;
    this.iPm[i] = 9;
    if (i >= fs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) fs.get(i);
    int ix = @PKG@.InvPage.toInt(f[1], -1);
    int mn = @PKG@.InvPage.toInt(f[3], 4);
    this.iPf[i] = ix;
    this.iPm[i] = mn;
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[4], 40));
    b.set("#" + r + "S.Text", tx(f[5], 70));
    b.set("#" + r + "Cb.Visible", ed);
    b.set("#" + r + "Ro.Visible", !ed);
    StringBuilder ro = new StringBuilder();
    for (int c = 0; c < 4; c++) {
      boolean yes = c >= mn;
      if (c > 0) ro.append("      ");
      ro.append(cols[c]).append(yes ? ": YES" : ": no");
      if (ed) {
        b.set("#" + r + "c" + c + ".Text", yes ? "YES" : "NO");
        ev.addEventBinding(@BT@.Activating, "#" + r + "c" + c, @EVD@.of("a", "ip:" + i + ":" + c).append("t", this.tok));
      }
    }
    b.set("#" + r + "Ro.Text", ro.toString());
  }
}""")
M(wtab, r"""
public void ivVisitors(@UCB@ b, @UEB@ ev, String[] h, java.util.ArrayList vs, java.util.ArrayList bs, String[] cn) {
  int rank = @PKG@.InvPage.toInt(h[4], 0);
  boolean ed = rank >= 3;
  int mode = @PKG@.InvPage.toInt(h[13], 0);
  if (mode < 0 || mode > 2) mode = 0;
  b.set("#SkyyWtabIvVmx.Text", ed ? "" : @PKG@.WorldTabData.IMODE[mode]);
  if (ed) {
    for (int i = 0; i < 3; i++) {
      b.appendInline("#SkyyWtabIvVmb", @PKG@.WorldTabData.MODE.replace("{I}", "Im" + i).replace("{S}", i == mode ? @PKG@.WorldTabData.MS1 : @PKG@.WorldTabData.MS0));
      b.set("#SkyyWtabIm" + i + ".Text", @PKG@.WorldTabData.IMODE[i]);
      ev.addEventBinding(@BT@.Activating, "#SkyyWtabIm" + i, @EVD@.of("a", "iv:mode" + i).append("t", this.tok));
    }
    this.iAllow = this.iAllow + "mode0|mode1|mode2|limm|limp|notify|";
  }
  b.set("#SkyyWtabIvVlv.Text", h[14]);
  b.set("#SkyyWtabIvVlm.Visible", ed);
  b.set("#SkyyWtabIvVlp.Visible", ed);
  b.set("#SkyyWtabIvVn.Visible", ed);
  boolean ping = "1".equals(h[16]);
  this.iShowN = ping ? "1" : "0";
  if (ed) {
    b.set("#SkyyWtabIvVlp.Text", "+");
    b.set("#SkyyWtabIvVn.Text", ping ? "On" : "Off");
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvVlm", @EVD@.of("a", "iv:limm").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvVlp", @EVD@.of("a", "iv:limp").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvVn", @EVD@.of("a", "iv:notify").append("t", this.tok));
  }
  b.set("#SkyyWtabIvVh.Text", "Visit ping: " + (ping ? "On" : "Off") + "  -  a chat line to the owner and members when someone visits.   The limit is " + h[14] + " (most " + h[15] + ").");
  int vt = cn != null && cn.length >= 9 ? @PKG@.InvPage.toInt(cn[6], vs.size()) : vs.size();
  b.set("#SkyyWtabIvVvh.Text", "ON THE ISLAND NOW  (" + vt + ")" + ("1".equals(h[20]) ? "" : "  - the island is not loaded"));
  String arm = h[25];
  int n = @PKG@.WorldTabData.IVN;
  this.iVPages = pagesOf(vs.size(), n);
  this.iVPage = clampPage(this.iVPage, this.iVPages);
  this.iVu = new String[n];
  this.iVb = new int[n];
  for (int i = 0; i < n; i++) {
    String r = "SkyyWtabIvV" + i;
    int ix = this.iVPage * n + i;
    this.iVu[i] = "";
    this.iVb[i] = 0;
    if (ix >= vs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) vs.get(ix);
    int tr = @PKG@.InvPage.toInt(f[2], 0);
    boolean me = "1".equals(f[3]);
    boolean adm = tr == 9;
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[4], 28) + (me ? " (you)" : "") + "   -   " + roleN(tr));
    int bt = 0;
    if (!me && !adm && tr <= 1 && rank >= 2) bt = bt | 1;
    if (!me && !adm && tr == 0 && rank >= 3) bt = bt | 2;
    if (!me && !adm && tr <= 1 && rank >= 3) bt = bt | 4;
    this.iVu[i] = f[1];
    this.iVb[i] = bt;
    b.set("#" + r + "E.Visible", (bt & 1) != 0);
    b.set("#" + r + "T.Visible", (bt & 2) != 0);
    b.set("#" + r + "B.Visible", (bt & 4) != 0);
    if ((bt & 1) != 0) ev.addEventBinding(@BT@.Activating, "#" + r + "E", @EVD@.of("a", "ivv:ex:" + i).append("t", this.tok));
    if ((bt & 2) != 0) ev.addEventBinding(@BT@.Activating, "#" + r + "T", @EVD@.of("a", "ivv:tr:" + i).append("t", this.tok));
    if ((bt & 4) != 0) {
      b.set("#" + r + "B.Text", arm.equals("vb:" + f[1]) ? "Sure?" : "Ban");
      ev.addEventBinding(@BT@.Activating, "#" + r + "B", @EVD@.of("a", "ivv:ban:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyWtabIvVpg.Text", "Page " + (this.iVPage + 1) + " / " + this.iVPages);
  b.set("#SkyyWtabIvVp.Visible", this.iVPages > 1);
  int bt2 = cn != null && cn.length >= 9 ? @PKG@.InvPage.toInt(cn[8], bs.size()) : bs.size();
  b.set("#SkyyWtabIvXh.Text", "BANNED  (" + bt2 + " / " + h[12] + ")" + (bt2 > bs.size() ? "  +" + (bt2 - bs.size()) + " more" : ""));
  int m = @PKG@.WorldTabData.IXN;
  this.iXPages = pagesOf(bs.size(), m);
  this.iXPage = clampPage(this.iXPage, this.iXPages);
  this.iBk = new String[m];
  for (int i = 0; i < m; i++) {
    String r = "SkyyWtabIvX" + i;
    int ix = this.iXPage * m + i;
    this.iBk[i] = "";
    if (ix >= bs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) bs.get(ix);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", tx(f[2], 30));
    b.set("#" + r + "U.Visible", rank >= 3);
    if (rank >= 3) {
      this.iBk[i] = f[1];
      ev.addEventBinding(@BT@.Activating, "#" + r + "U", @EVD@.of("a", "ib:un:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyWtabIvXpg.Text", "Page " + (this.iXPage + 1) + " / " + this.iXPages);
  b.set("#SkyyWtabIvXp.Visible", this.iXPages > 1);
}""")
M(wtab, r"""
public void ivRules(@UCB@ b, @UEB@ ev, String[] h) {
  int rank = @PKG@.InvPage.toInt(h[4], 0);
  boolean ed = rank >= 3;
  boolean pvp = "1".equals(h[17]);
  boolean spw = "1".equals(h[18]);
  this.iShowP = pvp ? "1" : "0";
  this.iShowS = spw ? "1" : "0";
  b.set("#SkyyWtabIvIpb.Visible", ed);
  b.set("#SkyyWtabIvIsb.Visible", ed);
  b.set("#SkyyWtabIvIph.Text", (ed ? "" : "Now " + (pvp ? "ON" : "OFF") + ".   ") + "Turning PvP on sends visitors to the hub. Members and trusted players stay.");
  b.set("#SkyyWtabIvIsh.Text", (ed ? "" : "Now " + (spw ? "ON" : "OFF") + ".   ") + "Needs a biome with wildlife - Void Sky (today's islands) has none, so nothing spawns yet.");
  b.set("#SkyyWtabIvIn.Text", ed ? "" : "Only the owner and island admins can change these.");
  if (ed) {
    b.set("#SkyyWtabIvIpb.Text", pvp ? "ON" : "OFF");
    b.set("#SkyyWtabIvIsb.Text", spw ? "ON" : "OFF");
    this.iAllow = this.iAllow + "pvp|spawn|";
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvIpb", @EVD@.of("a", "iv:pvp").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyWtabIvIsb", @EVD@.of("a", "iv:spawn").append("t", this.tok));
  }
}""")
M(wtab, r"""
public void fillIv(@UCB@ b, @UEB@ ev) {
  this.iOk = false;
  this.iAllow = "|";
  this.iMk = new String[0];
  this.iMb = new int[0];
  this.iTk = new String[0];
  this.iVu = new String[0];
  this.iVb = new int[0];
  this.iBk = new String[0];
  this.iPf = new int[0];
  this.iPm = new int[0];
  if (!this.iSeen) iRefresh();   // fix isl1fix: the island view opens = the bridge's arm dropped
  this.iSeen = true;
  String s = wact("island:fn:act", "state", null, null, @PKG@.WorldTabData.IVREAD);
  this.iLast = s;
  if (s == null) { ivHide(b, oldT("hub:tab:world:island", @PKG@.WorldTabData.IVOLD, @PKG@.WorldTabData.IVOFF)); return; }
  String[] ls = s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? ls[0].split("\\|", -1) : new String[0];
  if (h.length < 28) { ivHide(b, @PKG@.WorldTabData.IVFAIL); return; }
  this.iTok = h[2];
  this.iPk = h[3];
  this.iOk = true;
  b.set("#SkyyWtabIvSr.Visible", true);
  b.set("#SkyyWtabIvB.Visible", true);
  b.set("#SkyyWtabIvH.Text", "");
  String name = "";
  String zc = null;
  String rb = null;
  String pend = null;
  String[] cn = null;
  String[] dl = null;
  String[] inv = null;
  java.util.ArrayList ms = new java.util.ArrayList();
  java.util.ArrayList ts = new java.util.ArrayList();
  java.util.ArrayList fs = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  java.util.ArrayList bs = new java.util.ArrayList();
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("n|")) name = l.substring(2);
    else if (l.startsWith("z|")) zc = l.substring(2);
    else if (l.startsWith("r|")) rb = l.substring(2);
    else if (l.startsWith("c|")) cn = l.split("\\|", -1);
    else if (l.startsWith("m|")) { String[] f = cut(l, 8); if (f.length >= 8) ms.add(f); }
    else if (l.startsWith("p|")) pend = l.substring(2);
    else if (l.startsWith("t|")) { String[] f = cut(l, 5); if (f.length >= 5) ts.add(f); }
    else if (l.startsWith("d|")) dl = cut(l, 3);
    else if (l.startsWith("f|")) { String[] f = cut(l, 6); if (f.length >= 6) fs.add(f); }
    else if (l.startsWith("v|")) { String[] f = cut(l, 5); if (f.length >= 5) vs.add(f); }
    else if (l.startsWith("b|")) { String[] f = cut(l, 3); if (f.length >= 3) bs.add(f); }
    else if (l.startsWith("i|")) { String[] f = cut(l, 6); if (f.length >= 6) inv = f; }
  }
  boolean has = "1".equals(h[1]);
  int rank = @PKG@.InvPage.toInt(h[4], 0);
  int mode = @PKG@.InvPage.toInt(h[13], 0);
  b.set("#SkyyWtabIvR.Text", tx((has ? name + "'s Island" : "Your Island") + "      Your role: " + roleN(rank)
      + (has ? "      Co-op " + h[7] + " / " + h[8] + "      Visits: " + (mode == 1 ? "friends" : (mode == 2 ? "closed" : "public")) : ""), 118));
  b.set("#SkyyWtabIvC.Text", has ? "Visitors now " + h[19] : "");
  if (this.iSub < 0 || this.iSub > 4) this.iSub = 0;
  vtabs(b, ev, "IvK", "Ik", @PKG@.WorldTabData.ISUB, this.iSub, "ik:");
  b.set("#SkyyWtabIvKn.Text", h[24].length() > 0 && rank >= 3 ? "A co-op invite lasts " + h[24] + " s" : "");
  if ("1".equals(h[6])) {   // the page shows only this line
    b.set("#SkyyWtabIvE.Visible", true);
    b.set("#SkyyWtabIvE.Text", "Your island file can't be read right now - click Refresh in a moment. Nothing was changed.");
    ivPanels(b, -1);
    return;
  }
  if (this.iSub > 0 && !has) {
    b.set("#SkyyWtabIvE.Visible", true);
    b.set("#SkyyWtabIvE.Text", this.iSub == 1 ? "Create your island first (Overview tab), then invite co-op members or trust builders here." : "Create your island first (Overview tab).");
    ivPanels(b, -1);
    return;
  }
  b.set("#SkyyWtabIvE.Visible", false);
  ivPanels(b, this.iSub);
  if (this.iSub == 0) ivOverview(b, ev, h, name, zc, rb, inv);
  else if (this.iSub == 1) ivMembers(b, ev, h, ms, ts, cn, rank >= 3 ? pend : null, dl);
  else if (this.iSub == 2) ivPerms(b, ev, h, fs);
  else if (this.iSub == 3) ivVisitors(b, ev, h, vs, bs, cn);
  else ivRules(b, ev, h);
}""")
'''

WV_ACT = r'''# ---- 0.3.74 (oldmenu6): the views' actions - every one answers with ONE packet (a redraw with the bridge's line in the caption, a caption,
# or the close a trip does). Navigation (views, tabs, picks, pages) needs no token; a bridge act needs the token (checked in handleDataEvent)
M(wtab, r"""
public static int viewOf(String a) {
  if (a.startsWith("ql:") || a.startsWith("qk:") || a.startsWith("qlpg:") || a.startsWith("qtpg:") || a.equals("qtr") || a.equals("qca") || a.equals("qhd")
      || a.startsWith("qcl:") || a.startsWith("qsk:")) return 1;
  if (a.startsWith("cc:") || a.startsWith("cv:") || a.startsWith("cpg:") || a.startsWith("crpg:") || a.equals("cbuy") || a.startsWith("ccr:")) return 2;
  if (a.startsWith("ek:") || a.startsWith("ezpg:") || a.startsWith("etpg:") || a.startsWith("eipg:") || a.startsWith("ecpg:") || a.startsWith("ei:")
      || a.startsWith("et:") || a.equals("etn")) return 3;
  if (a.startsWith("ik:") || a.startsWith("impg:") || a.startsWith("itpg:") || a.startsWith("ivpg:") || a.startsWith("ixpg:") || a.startsWith("iv:")
      || a.startsWith("im:") || a.startsWith("it:") || a.startsWith("ivv:") || a.startsWith("ib:") || a.startsWith("ip:")) return 4;
  if (a.startsWith("flt:") || a.startsWith("pg:") || a.startsWith("go:") || a.equals("home") || a.equals("isl") || a.equals("exp") || a.equals("qlog") || a.equals("coll")) return 0;
  return -1;
}""")
M(wtab, r"""
public void goView(int v) {
  this.answered = true;
  int was = this.view;
  this.view = v < 0 || v > 4 ? 0 : v;
  if (was == 4 && this.view != 4 && this.iSeen) { iRefresh(); this.iSeen = false; }   // the island bridge keeps its arm per player: dropped when the view is left (fillIv: when it opens)
  if (was != this.view) {
    this.qLPage = 0;
    this.qPage = 0;
    this.cPage = 0;
    this.cRPage = 0;
    this.eZPage = 0;
    this.eTPage = 0;
    this.eIPage = 0;
    this.eCPage = 0;
    this.iMPage = 0;
    this.iTPage = 0;
    this.iVPage = 0;
    this.iXPage = 0;
  }
  this.tcap = "";
  redraw();
}""")
M(wtab, r"""
public void vRefresh() {
  this.answered = true;
  if (this.view == 4) iRefresh();
  else if (this.view == 1 && this.qOk) wact("quest:fn:act", "refresh", this.qTok, this.qPk, null);
  else if (this.view == 2 && this.cOk) wact("coll:fn:act", "refresh", this.cTok, this.cPk, null);
  else if (this.view == 3 && this.eOk) wact("explore:fn:act", "refresh", this.eTok, this.ePk, null);
  this.tcap = "";
  redraw();
}""")
# a page step: the new page, or -1 (said: the first / last page)
M(wtab, r"""
public int step(int cur, int max, String a, int cut) {
  int dp = @PKG@.InvPage.toInt(a.substring(cut), 0);
  int np = cur + (dp < 0 ? -1 : 1);
  if (np < 0 || np >= max) { say(np < 0 ? "This is the first page" : "This is the last page"); return -1; }
  return np;
}""")
M(wtab, r"""
public static int pick(String a, int cut, int n) {
  int k = @PKG@.InvPage.toInt(a.substring(cut), -1);
  return k < 0 || k >= n ? -1 : k;
}""")
# the navigation inside a view (no bridge act): tabs, picks, pages
M(wtab, r"""
public boolean navView(String a) {
  int p = -2;
  if (a.startsWith("ql:")) {
    int k = pick(a, 3, this.qLn == null ? 0 : this.qLn.length);
    if (k < 0 || this.qLn[k].length() == 0) { say("Nothing there"); return true; }
    if (!this.qLn[k].equals(this.qLine)) { this.qLine = this.qLn[k]; this.qSub = 0; this.qPage = 0; }
    this.tcap = "";
    redraw();
    return true;
  }
  if (a.startsWith("qk:")) { int k = pick(a, 3, 2); this.qSub = k < 0 ? 0 : k; this.qPage = 0; this.tcap = ""; redraw(); return true; }
  if (a.startsWith("cc:")) {
    int k = pick(a, 3, this.cKc == null ? 0 : this.cKc.length);
    if (k < 0 || this.cKc[k] < 0) { say("Nothing there"); return true; }
    this.cCat = this.cKc[k];
    this.cId = "";
    this.cPage = 0;
    this.tcap = "";
    redraw();
    return true;
  }
  if (a.startsWith("cv:")) {
    int k = pick(a, 3, this.cIds == null ? 0 : this.cIds.length);
    if (k < 0 || this.cIds[k].length() == 0) { say("Nothing there"); return true; }
    this.cId = this.cIds[k];
    this.cRPage = 0;
    this.tcap = "";
    redraw();
    return true;
  }
  if (a.startsWith("ek:")) { int k = pick(a, 3, 4); this.eSub = k < 0 ? 0 : k; this.tcap = ""; redraw(); return true; }
  if (a.startsWith("ei:")) {
    int k = pick(a, 3, this.eIs == null ? 0 : this.eIs.length);
    if (k < 0 || this.eIs[k].length() == 0) { say("Nothing there"); return true; }
    if (!this.eIs[k].equals(this.eWf)) { this.eWf = this.eIs[k]; this.eCPage = 0; }
    this.tcap = "";
    redraw();
    return true;
  }
  if (a.startsWith("ik:")) { int k = pick(a, 3, 5); this.iSub = k < 0 ? 0 : k; iRefresh(); this.tcap = ""; redraw(); return true; }   // fix isl1fix: every island tab change
  if (a.startsWith("qlpg:")) { p = step(this.qLPage, this.qLPages, a, 5); if (p >= 0) this.qLPage = p; }
  else if (a.startsWith("qtpg:")) { p = step(this.qPage, this.qPages, a, 5); if (p >= 0) this.qPage = p; }
  else if (a.startsWith("cpg:")) { p = step(this.cPage, this.cPages, a, 4); if (p >= 0) this.cPage = p; }
  else if (a.startsWith("crpg:")) { p = step(this.cRPage, this.cRPages, a, 5); if (p >= 0) this.cRPage = p; }
  else if (a.startsWith("ezpg:")) { p = step(this.eZPage, this.eZPages, a, 5); if (p >= 0) this.eZPage = p; }
  else if (a.startsWith("etpg:")) { p = step(this.eTPage, this.eTPages, a, 5); if (p >= 0) this.eTPage = p; }
  else if (a.startsWith("eipg:")) { p = step(this.eIPage, this.eIPages, a, 5); if (p >= 0) this.eIPage = p; }
  else if (a.startsWith("ecpg:")) { p = step(this.eCPage, this.eCPages, a, 5); if (p >= 0) this.eCPage = p; }
  else if (a.startsWith("impg:")) { p = step(this.iMPage, this.iMPages, a, 5); if (p >= 0) this.iMPage = p; }
  else if (a.startsWith("itpg:")) { p = step(this.iTPage, this.iTPages, a, 5); if (p >= 0) this.iTPage = p; }
  else if (a.startsWith("ivpg:")) { p = step(this.iVPage, this.iVPages, a, 5); if (p >= 0) this.iVPage = p; }
  else if (a.startsWith("ixpg:")) { p = step(this.iXPage, this.iXPages, a, 5); if (p >= 0) this.iXPage = p; }
  else return false;
  if (p >= 0) { this.tcap = ""; redraw(); }
  return true;
}""")
M(wtab, r"""
public void qDo(String op, String arg) {
  this.answered = true;
  if (!this.qOk) { say("Your quests are not ready - nothing changed."); return; }
  String r = wact("quest:fn:act", op, this.qTok, this.qPk, arg);
  if (r == null) { this.tcap = oldT("hub:tab:world:quests", @PKG@.WorldTabData.QVOLD, @PKG@.WorldTabData.QVOFF); redraw(); return; }
  this.tcap = ansT(r);
  redraw();
}""")
M(wtab, r"""
public void cDo(String op, String arg) {
  this.answered = true;
  if (!this.cOk) { say("Your collections are not ready - nothing changed."); return; }
  String r = wact("coll:fn:act", op, this.cTok, this.cPk, arg);
  if (r == null) { this.tcap = oldT("hub:tab:character:collections", @PKG@.WorldTabData.CVOLD, @PKG@.WorldTabData.CVOFF); redraw(); return; }
  if (op.equals("craft") && !still()) { finish("craft"); return; }   // the crafting page opened in place of this screen
  String m = r.trim();
  this.tcap = m.equals("+") ? "Opening the crafting page." : ansT(m);
  redraw();
}""")
M(wtab, r"""
public void eDo(String op, String arg) {
  this.answered = true;
  if (!this.eOk) { say("Your exploring is not ready - nothing changed."); return; }
  String r = wact("explore:fn:act", op, this.eTok, this.ePk, arg);
  if (r == null) { this.tcap = oldT("hub:tab:world:explore", @PKG@.WorldTabData.EVOLD, @PKG@.WorldTabData.EVOFF); redraw(); return; }
  this.tcap = ansT(r);
  redraw();
}""")
# an island act; Create / Go to island (answer "") and a confirmed Leave / Reset ("+") are trips: the bridge closes the screen (the page's
# closePage) - if it is still open here it is closed too (never a redraw over a trip)
M(wtab, r"""
public void iDo(String op, String arg) {
  this.answered = true;
  if (!this.iOk) { say("Your island is not ready - nothing changed."); return; }
  String r = wact("island:fn:act", op, this.iTok, this.iPk, arg);
  if (r == null) { this.tcap = oldT("hub:tab:world:island", @PKG@.WorldTabData.IVOLD, @PKG@.WorldTabData.IVOFF); redraw(); return; }
  String m = r.trim();
  boolean trip = ((op.equals("create") || op.equals("go")) && m.length() == 0) || ((op.equals("leave") || op.equals("reset")) && m.startsWith("+"));
  if (trip) {
    this.iSeen = false;
    GOES = GOES + 1;
    if (still()) shut(); else finish("island trip");
    return;
  }
  if (m.startsWith("+") && (op.equals("invite") || op.equals("trust"))) this.iKeepN = "";
  this.tcap = ansT(m);
  redraw();
}""")
# a typed player name: no control characters, quotes, backslashes or '|' (the bridge cleans it again: IslandStore.cleanName)
M(wtab, r"""
public static String nameClean(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 32; i++) {
    char c = s.charAt(i);
    if (c < 32 || c == 127 || c == 34 || c == 92 || c == '|') continue;
    sb.append(c);
  }
  return sb.toString().trim();
}""")
# the token-checked acts of the views (each button only where the drawing showed it; else a caption, no call)
M(wtab, r"""
public boolean actView(String a, String d) {
  String none = @PKG@.WorldTabData.NONE;
  if (a.equals("qtr")) { if (!allowed(this.qAllow, "track")) say(none); else qDo("track", this.qTrArg); return true; }
  if (a.equals("qca")) { if (!allowed(this.qAllow, "claim")) say(none); else qDo("claim", null); return true; }
  if (a.equals("qhd")) { if (!allowed(this.qAllow, "hide")) say(none); else qDo(this.qHideOp, null); return true; }
  if (a.startsWith("qcl:") || a.startsWith("qsk:")) {
    boolean cl = a.startsWith("qcl:");
    int k = pick(a, 4, this.qBtn == null ? 0 : this.qBtn.length);
    if (k < 0 || (this.qBtn[k] & (cl ? 1 : 2)) == 0) { say(none); return true; }
    if (cl) qDo("claim1", this.qTk[k]); else qDo("skip", this.qTk[k] + "|" + this.qSkS[k]);
    return true;
  }
  if (a.equals("cbuy")) { if (!allowed(this.cAllow, "buy") || this.cBuy.length() == 0) say(none); else cDo("buy", this.cBuy); return true; }
  if (a.startsWith("ccr:")) {
    int k = pick(a, 4, this.cRec == null ? 0 : this.cRec.length);
    if (k < 0 || this.cRec[k].length() == 0) { say(none); return true; }
    cDo("craft", this.cRec[k]);
    return true;
  }
  if (a.startsWith("et:")) {
    int k = pick(a, 3, this.eTi == null ? 0 : this.eTi.length);
    if (k < 0 || this.eTi[k].length() == 0) { say(none); return true; }
    eDo("title", this.eTi[k]);
    return true;
  }
  if (a.equals("etn")) { if (!allowed(this.eAllow, "none")) say(none); else eDo("title", "none"); return true; }
  if (a.startsWith("iv:")) {
    String k = a.substring(3);
    if (!allowed(this.iAllow, k)) { say(none); return true; }
    if (k.equals("inv") || k.equals("trust") || k.equals("name")) {
      String nm = nameClean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "IN"));
      this.iKeepN = nm;
      if (nm.length() == 0 && !k.equals("name")) { say("Type a player's name in the box first."); return true; }
      iDo(k.equals("inv") ? "invite" : k, nm);
      return true;
    }
    if (k.equals("create") || k.equals("go") || k.equals("leave") || k.equals("reset")) { iDo(k, null); return true; }
    if (k.equals("acc")) { iDo("accept", null); return true; }
    if (k.equals("dec")) { iDo("decline", null); return true; }
    if (k.equals("disb")) { iDo("disband", null); return true; }
    if (k.equals("pdef")) { iDo("permreset", null); return true; }
    if (k.equals("limm") || k.equals("limp")) { iDo("limit", k.equals("limm") ? "-1" : "1"); return true; }
    if (k.equals("notify")) { iDo("notify", this.iShowN); return true; }
    if (k.equals("pvp")) { iDo("pvp", this.iShowP); return true; }
    if (k.equals("spawn")) { iDo("spawning", this.iShowS); return true; }
    if (k.startsWith("mode")) { iDo("mode", k.substring(4)); return true; }
    say(none);
    return true;
  }
  if (a.startsWith("im:")) {
    int bit = a.startsWith("im:pro:") ? 1 : (a.startsWith("im:dem:") ? 2 : (a.startsWith("im:kick:") ? 4 : 0));
    int k = bit == 0 ? -1 : pick(a, bit == 4 ? 8 : 7, this.iMb == null ? 0 : this.iMb.length);
    if (k < 0 || (this.iMb[k] & bit) == 0) { say(none); return true; }
    iDo(bit == 1 ? "promote" : (bit == 2 ? "demote" : "kick"), this.iMk[k]);
    return true;
  }
  if (a.startsWith("it:un:")) {
    int k = pick(a, 6, this.iTk == null ? 0 : this.iTk.length);
    if (k < 0 || this.iTk[k].length() == 0) { say(none); return true; }
    iDo("untrust", this.iTk[k]);
    return true;
  }
  if (a.startsWith("ivv:")) {
    int bit = a.startsWith("ivv:ex:") ? 1 : (a.startsWith("ivv:tr:") ? 2 : (a.startsWith("ivv:ban:") ? 4 : 0));
    int k = bit == 0 ? -1 : pick(a, bit == 4 ? 8 : 7, this.iVb == null ? 0 : this.iVb.length);
    if (k < 0 || (this.iVb[k] & bit) == 0) { say(none); return true; }
    iDo(bit == 1 ? "expel" : (bit == 2 ? "vtrust" : "ban"), this.iVu[k]);
    return true;
  }
  if (a.startsWith("ib:un:")) {
    int k = pick(a, 6, this.iBk == null ? 0 : this.iBk.length);
    if (k < 0 || this.iBk[k].length() == 0) { say(none); return true; }
    iDo("unban", this.iBk[k]);
    return true;
  }
  if (a.startsWith("ip:")) {
    String[] f = a.split(":");
    int r = f.length == 3 ? pick("x" + f[1], 1, this.iPf == null ? 0 : this.iPf.length) : -1;
    int c = f.length == 3 ? pick("x" + f[2], 1, 4) : -1;
    if (r < 0 || c < 0 || this.iPf[r] < 0 || !allowed(this.iAllow, "perm")) { say(none); return true; }
    iDo("perm", two(this.iPf[r]) + String.valueOf("vtma".charAt(c)) + "|" + (c >= this.iPm[r] ? "1" : "0"));
    return true;
  }
  return false;
}""")
'''
P.rep('''WT_AP, WT_BINDS = _wt_page()
SUI.check_page(WT_AP, WT)
for _p, _mk in WT_AP:
    SUI.check_markup(_mk, prefix=WT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.62: the world screen never scrolls"
_wt_ids = set(i_ for _p, mk_ in WT_AP for i_ in SUI._static_ids(mk_))''', WV_PY.lstrip("\n") + '''

WT_AP0, WT_BINDS = _wt_page()
WT_VIEWS = _wt_views()
# 0.3.74: the home cards = the body group and everything inside it (section H); the views go in before the hint row (the window's next child)
_wt_home = set([WT + "Body"])
WT_SEC = []
for _p, _mk in WT_AP0:
    _ids = set(SUI._static_ids(_mk))
    _pid = None if _p is None else SUI.render(_p).lstrip("#")
    if (WT + "Body") in _ids or _pid in _wt_home:
        _wt_home |= _ids
        WT_SEC.append("H")
    else:
        WT_SEC.append("0")
_hi = [k_ for k_, (_p, _mk) in enumerate(WT_AP0) if (WT + "Hints") in SUI._static_ids(_mk)]
assert len(_hi) == 1 and WT_SEC[:_hi[0]].count("H") > 50 and "H" not in WT_SEC[_hi[0]:], "0.3.74: the home cards come right before the hint row"
WT_AP = SUI.Appends(list(WT_AP0[:_hi[0]]))
WT_SECA = WT_SEC[:_hi[0]]
for _v, _vap, _vb in WT_VIEWS:
    WT_AP.extend(_vap)
    WT_SECA += [_v] * len(_vap)
WT_AP.extend(SUI.Appends(list(WT_AP0[_hi[0]:])))
WT_SECA += WT_SEC[_hi[0]:]
WT_AP.sets = list(WT_AP0.sets)
for _v, _vap, _vb in WT_VIEWS:
    WT_AP.sets.extend(_vap.sets)
assert len(WT_SECA) == len(WT_AP)
SUI.check_page(WT_AP, WT)
for _p, _mk in WT_AP:
    SUI.check_markup(_mk, prefix=WT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.62: the world screen never scrolls"
_wt_ids = set(i_ for _p, mk_ in WT_AP for i_ in SUI._static_ids(mk_))
_wt_vsec = {}
for _v, _vap, _vb in WT_VIEWS:
    for _p, _mk in _vap:
        for _i in SUI._static_ids(_mk):
            _wt_vsec[_i] = _v
_wt_sec_of = lambda i_: "H" if i_ in _wt_home else _wt_vsec.get(i_, "0")
for _v, _vap, _vb in WT_VIEWS:
    for _s, _a in _vb:
        assert _s[1:] in _wt_ids and _wt_sec_of(_s[1:]) == _v, ("0.3.74: a view binding names its own element", _s)''')
P.rep('''          + ["E%d%s" % (k_, x_) for k_ in range(WT_EN) for x_ in ("r", "N", "B", "P")])
for _g in WT_DYN:''', '''          + ["E%d%s" % (k_, x_) for k_ in range(WT_EN) for x_ in ("r", "N", "B", "P")]
          # 0.3.74 (oldmenu6): the views
          + ["%s%s" % (v_, x_) for v_ in ("Qv", "Cv", "Ev", "Iv") for x_ in ("H", "C", "Rf", "Vt0", "Vt1", "Vt2", "Vt3", "Vt4")]
          + ["QvL%d%s" % (k_, x_) for k_ in range(QL_N) for x_ in ("", "N", "S", "B", "P")] + ["QvT%d%s" % (k_, x_) for k_ in range(QT_N) for x_ in ("", "N", "S0", "S4", "P", "B", "W", "R", "H", "C", "K")]
          + ["QvN", "QvS", "QvTr", "QvW", "QvSr", "QvK", "QvKn", "QvLp", "QvLpg", "QvTp", "QvTpg", "QvFn", "QvCa", "QvHd", "Qvb"]
          + ["CvK%d%s" % (k_, x_) for k_ in range(CK_N) for x_ in ("", "N", "F", "D", "B")] + ["CvC%d%s" % (k_, x_) for k_ in range(CC_N) for x_ in ("", "N", "P", "B", "S", "V")]
          + ["CvDt%d%s" % (k_, x_) for k_ in range(CT_N) for x_ in ("", "N", "S0", "S4", "A", "R")] + ["CvR%d%s" % (k_, x_) for k_ in range(CR_N) for x_ in ("", "N", "S", "C")]
          + ["CvT", "CvK", "CvB", "CvG", "CvGh", "CvGp", "CvGpg", "CvGn", "CvD", "CvDN", "CvDM", "CvDG", "CvDB", "CvDy", "CvDy1", "CvDy2", "CvDy3", "CvDyB",
             "CvDtn", "CvDrh", "CvRp", "CvRpg", "CvRn"]
          + ["EvO%d%s" % (k_, x_) for k_ in range(8) for x_ in ("", "H", "V", "S", "T")] + ["EvZ%d%s" % (k_, x_) for k_ in range(2 * EZ_N) for x_ in ("", "N0", "N1", "V")]
          + ["EvT%d%s" % (k_, x_) for k_ in range(2 * ET_N) for x_ in ("", "N0", "N1", "N2", "R", "U")] + ["EvCi%d%s" % (k_, x_) for k_ in range(EC_IN) for x_ in ("", "N", "S", "B", "Go")]
          + ["EvCe%d%s" % (k_, x_) for k_ in range(2 * EC_RN) for x_ in ("", "N0", "N1", "V")]
          + ["EvL", "EvSr", "EvK", "EvKn", "EvB", "EvO", "EvOq", "EvOu", "EvOv", "EvZ", "EvZp", "EvZpg", "EvT", "EvTs", "EvTn", "EvTp", "EvTpg", "EvC", "EvCk", "EvCl",
             "EvCip", "EvCipg", "EvCrN", "EvCrS", "EvCrB", "EvCrw", "EvCrf", "EvCrp", "EvCrpg"]
          + ["IvM%d%s" % (k_, x_) for k_ in range(IM_N) for x_ in ("", "N", "S", "P", "K")] + ["IvT%d%s" % (k_, x_) for k_ in range(IT_N) for x_ in ("", "N", "U")]
          + ["IvP%d%s" % (k_, x_) for k_ in range(IP_N) for x_ in ("", "N", "S", "Cb", "Ro", "c0", "c1", "c2", "c3")] + ["IvV%d%s" % (k_, x_) for k_ in range(IV_N) for x_ in ("", "N", "E", "T", "B")]
          + ["IvX%d%s" % (k_, x_) for k_ in range(IX_N) for x_ in ("", "N", "U")]
          + ["IvR", "IvSr", "IvK", "IvKn", "IvB", "IvE", "IvO", "IvO1", "IvO2", "IvO3", "IvO4", "IvOb", "IvOz", "IvOg", "IvGo", "IvGoh", "IvOi", "IvOiq", "IvOis",
             "IvOy", "IvOn", "IvOo", "IvDb", "IvRs", "IvRsn", "IvOon", "IvOl", "IvLv", "IvLvn", "IvM", "IvMi", "IvMf", "IvMinv", "IvMtr", "IvMih", "IvMh", "IvMp",
             "IvMpg", "IvMn", "IvTh", "IvTp", "IvTpg", "IvTn", "IvTo", "IvP", "IvPtx", "IvPdef", "IvPs", "IvV", "IvVmb", "IvVmx", "IvVlm", "IvVlv", "IvVlp", "IvVn",
             "IvVh", "IvVvh", "IvVp", "IvVpg", "IvXh", "IvXp", "IvXpg", "IvI", "IvIpb", "IvIph", "IvIsb", "IvIsh", "IvIx", "IvIn"])
for _g in WT_DYN:''')
P.rep('''WT_RUNTIME_IDS = ["Fc%d" % k_ for k_ in range(len(WT_FILT))]''', '''WT_RUNTIME_IDS = ["Fc%d" % k_ for k_ in range(len(WT_FILT))] + WV_RUNTIME_IDS   # 0.3.74: + the views' tabs / mode buttons''')
P.rep(r'''WT_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in WT_AP)
WT_RUNTIME_MAX = len(WT_FILT) + WT_QN + WT_EN                 # the filter chips + a fill per quest step + a fill per explore row
WT_ELEMENTS = WT_SHELL_ELEMENTS + WT_RUNTIME_MAX''', r'''_wt_cnt = lambda mk_: len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_))))
# 0.3.74: one packet = the frame + ONE section (the home cards or a view) - the budget is the frame + the biggest section
_wt_by = {}
for (_p, _mk), _s in zip(WT_AP, WT_SECA):
    _wt_by[_s] = _wt_by.get(_s, 0) + _wt_cnt(_mk)
_wt_rt = {"H": len(WT_FILT) + WT_QN + WT_EN}                 # the filter chips + a fill per quest step + a fill per explore row
_wt_rt.update(WV_RUNTIME)                                    # a view's tabs + its bar fills / mode buttons
WT_SHELL_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] for _s in "HQCEI")
WT_RUNTIME_MAX = max(_wt_rt.values())
WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEI")
print("0.3.74 world sections (elements, + at run time): frame %d, %s" % (_wt_by["0"], ", ".join("%s %d + %d" % (_s, _wt_by[_s], _wt_rt[_s]) for _s in "HQCEI")))''')
P.rep('''WT_LK, WT_LP, WT_LB = [], [], []
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
assert WT_LK[0] == "A" and WT_LP[0] == "", "0.3.62: the page data starts with the root"''', '''WT_LK, WT_LP, WT_LB, WT_LS = [], [], [], []
for (_p, _mk), _s in zip(WT_AP, WT_SECA):
    WT_LK.append("A")
    WT_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    WT_LB.append(SUI.render(_mk))
    WT_LS.append(_s)
for _i, _pr, _v in WT_AP.sets:
    WT_LK.append("S")
    WT_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    WT_LB.append(_v)
    WT_LS.append(_wt_sec_of(SUI.render(_i).lstrip("#")))
for _s, _a in WT_BINDS + [b_ for _v, _vap, _vb in WT_VIEWS for b_ in _vb]:
    WT_LK.append("E")
    WT_LP.append(_s)
    WT_LB.append(_a)
    WT_LS.append(_wt_sec_of(_s.lstrip("#")))
assert WT_LK[0] == "A" and WT_LP[0] == "" and WT_LS[0] == "0", "0.3.62: the page data starts with the root"
assert all(_wt_sec_of(s_.lstrip("#")) in ("0", "H") for s_, _a in WT_BINDS), "0.3.74: the home bindings are frame / home elements"''')

# ---- the WorldTabData: the sections + the views' numbers, texts and run-time markup; the WorldTab fields
P.rep('''F(wtd, "public static final String[] FILT = %s;" % jarr(WT_FILT))''', '''F(wtd, "public static final String[] FILT = %s;" % jarr(WT_FILT))
# 0.3.74 (oldmenu6): the section letter of each page data line (0 frame / H home / Q quests / C collections / E explore / I island) + the views
F(wtd, "public static final String LS = %s;" % jstr("".join(WT_LS)))
for _n, _v in (("QSTATE", [t_ for t_, _c in QT_STATES]), ("CSTATE", [t_ for t_, _c in CT_STATES]), ("ESUB", EV_SUB), ("ISUB", IS_SUB), ("IMODE", IS_MODE)):
    F(wtd, "public static final String[] %s = %s;" % (_n, jarr(_v)))
for _n, _v in (("QLN", QL_N), ("QTN", QT_N), ("QLBARW", QL_TW), ("QBARW", QT_BARW), ("CKN", CK_N), ("CCN", CC_N), ("CTN", CT_N), ("CRN", CR_N), ("CCBARW", CC_TW),
               ("CDBARW", CD_LI), ("EZN", EZ_N), ("ETN", ET_N), ("ECIN", EC_IN), ("ECRN", EC_RN), ("ECIBARW", EC_ITW), ("ECRBARW", EC_RI), ("IMN", IM_N), ("ITN", IT_N),
               ("IPN", IP_N), ("IVN", IV_N), ("IXN", IX_N)):
    F(wtd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("TAB", WV_TAB), ("MODE", WV_MODE), ("ST0", WV_ST0), ("ST1", WV_ST1), ("MS0", WV_MS0), ("MS1", WV_MS1), ("IVREAD", IV_READ)):
    F(wtd, "public static final String %s = %s;" % (_n, jstr(_v)))
for _k in sorted(WV_TXT):
    F(wtd, "public static final String %s = %s;" % (_k.upper(), jstr(WV_TXT[_k])))''')
P.rep('''           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;"):
    F(wtab, _f)''', '''           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;",
           # 0.3.74 (oldmenu6): the view (0 home, 1 quests, 2 collections, 3 explore, 4 island) and each view's read + what its drawing showed
           "public int view;", "public int calls;", "public int irefs;", "public int cSeen;",
           "public String qTok;", "public String qPk;", "public boolean qOk;", "public String qLine;", "public int qSub;", "public int qPage;", "public int qPages;",
           "public int qLPage;", "public int qLPages;", "public String[] qLn;", "public String[] qTk;", "public String[] qSkS;", "public int[] qBtn;",
           "public String qTrArg;", "public String qHideOp;", "public String qAllow;", "public String qLast;",
           "public String cTok;", "public String cPk;", "public boolean cOk;", "public int cCat;", "public String cId;", "public String cWant;", "public int cPage;",
           "public int cPages;", "public int cRPage;", "public int cRPages;", "public String[] cIds;", "public String[] cRec;", "public int[] cKc;", "public String cBuy;",
           "public String cAllow;", "public String cLast;",
           "public String eTok;", "public String ePk;", "public boolean eOk;", "public int eSub;", "public int eZPage;", "public int eZPages;", "public int eTPage;",
           "public int eTPages;", "public int eIPage;", "public int eIPages;", "public int eCPage;", "public int eCPages;", "public String[] eTi;", "public String[] eIs;",
           "public String eWf;", "public String eAllow;", "public String eLast;",
           "public String iTok;", "public String iPk;", "public boolean iOk;", "public boolean iSeen;", "public int iSub;", "public int iMPage;", "public int iMPages;",
           "public int iTPage;", "public int iTPages;", "public int iVPage;", "public int iVPages;", "public int iXPage;", "public int iXPages;", "public String[] iMk;",
           "public String[] iTk;", "public String[] iVu;", "public String[] iBk;", "public int[] iMb;", "public int[] iVb;", "public int[] iPf;", "public int[] iPm;",
           "public String iAllow;", "public String iLast;", "public String iKeepN;", "public String iShowN;", "public String iShowP;", "public String iShowS;"):
    F(wtab, _f)''')
P.rep('''  this.keys = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
# 0.3.63: THE SOCIAL SCREEN DATA (SocialTabData) + the SocialTab fields''', '''  this.keys = new String[0];
  this.builds = 0;
  this.answers = 0;
  this.view = 0;           // 0.3.74 (oldmenu6)
  this.calls = 0;
  this.irefs = 0;
  this.cSeen = 0;
  this.qOk = false;
  this.qLine = "";
  this.qSub = 0;
  this.qPage = 0;
  this.qPages = 1;
  this.qLPage = 0;
  this.qLPages = 1;
  this.qLn = new String[0];
  this.qTk = new String[0];
  this.qSkS = new String[0];
  this.qBtn = new int[0];
  this.qTrArg = "";
  this.qHideOp = "hide";
  this.qAllow = "|";
  this.cOk = false;
  this.cCat = -1;
  this.cId = "";
  this.cWant = "";
  this.cPage = 0;
  this.cPages = 1;
  this.cRPage = 0;
  this.cRPages = 1;
  this.cIds = new String[0];
  this.cRec = new String[0];
  this.cKc = new int[0];
  this.cBuy = "";
  this.cAllow = "|";
  this.eOk = false;
  this.eSub = 0;
  this.eZPage = 0;
  this.eZPages = 1;
  this.eTPage = 0;
  this.eTPages = 1;
  this.eIPage = 0;
  this.eIPages = 1;
  this.eCPage = 0;
  this.eCPages = 1;
  this.eTi = new String[0];
  this.eIs = new String[0];
  this.eWf = "";
  this.eAllow = "|";
  this.iOk = false;
  this.iSeen = false;
  this.iSub = 0;
  this.iMPage = 0;
  this.iMPages = 1;
  this.iTPage = 0;
  this.iTPages = 1;
  this.iVPage = 0;
  this.iVPages = 1;
  this.iXPage = 0;
  this.iXPages = 1;
  this.iMk = new String[0];
  this.iTk = new String[0];
  this.iVu = new String[0];
  this.iBk = new String[0];
  this.iMb = new int[0];
  this.iVb = new int[0];
  this.iPf = new int[0];
  this.iPm = new int[0];
  this.iAllow = "|";
  this.iKeepN = "";
  this.iShowN = "";
  this.iShowP = "";
  this.iShowS = "";
}""")
# 0.3.63: THE SOCIAL SCREEN DATA (SocialTabData) + the SocialTab fields''')

# ---- WorldTab.openAt: the world screen on a view (the inventory's quest row, the skill page's Collections)
P.rep('''  catch (Throwable t) { @PKG@.MenuUtil.warn("world screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")''', '''  catch (Throwable t) { @PKG@.MenuUtil.warn("world screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")
# 0.3.74 (oldmenu6): the world screen opened on a view (1 quests, 2 collections with an optional category name, 3 explore, 4 island); null = it could not open
M(wtab, r"""
public static @PKG@.WorldTab openAt(@REF@ ref, @ST@ st, @PR@ pr, String via, int view, String want) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  @PKG@.WorldTab pg = new @PKG@.WorldTab(pr, via);
  pg.pref = ref;
  pg.pst = st;
  pg.view = view < 0 || view > 4 ? 0 : view;
  pg.cWant = want == null ? "" : want;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("world screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")''')

# ---- iRefresh before finish (finish sends it when a screen that showed the island view closes - fix isl1fix)
P.rep('''M(wtab, r"""
public void finish(String why) { this.closed = true; }""")''', '''M(wtab, r"""
public void iRefresh() {
  if (@PKG@.InvCraft.fn("island:fn:act") == null) return;
  call("island:fn:act", new Object[] { "refresh", this.playerRef.getUuid(), null, null, null });
  this.irefs = this.irefs + 1;
}""")
M(wtab, r"""
public void finish(String why) {
  boolean was = this.closed;
  this.closed = true;
  if (!was && this.iSeen) {   // 0.3.74: the island view was shown - the bridge's armed press is dropped with the screen (fix isl1fix)
    this.iSeen = false;
    try { iRefresh(); } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: island refresh failed: " + t); }
  }
}""")''')

# ---- the fills before build; build = the frame + the current section; a view instead of the home cards
P.rep('''M(wtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.WorldTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.WorldTabData.LP[i];''', WV_JAVA + '''M(wtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.WorldTabData.LK;
  String ls = @PKG@.WorldTabData.LS;   // 0.3.74 (oldmenu6): the frame + the current section only
  char cur = this.view == 1 ? 'Q' : (this.view == 2 ? 'C' : (this.view == 3 ? 'E' : (this.view == 4 ? 'I' : 'H')));
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    char sc = ls.charAt(i);
    if (sc != '0' && sc != cur) continue;
    String x = @PKG@.WorldTabData.LP[i];''')
P.rep('''  b.set("#SkyyWtabCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  try { fillTravel(b, ev, places()); }''', '''  b.set("#SkyyWtabCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  if (this.view != 0) {   // 0.3.74 (oldmenu6): a view instead of the home cards
    String vc = "";
    if (this.view == 1) {
      vc = @PKG@.WorldTabData.QVCAP;
      try { fillQv(b, ev); } catch (Throwable t) { this.qOk = false; this.qBtn = new int[0]; this.qAllow = "|"; @PKG@.MenuUtil.warn("world screen: the quests view failed: " + t); }
    } else if (this.view == 2) {
      vc = @PKG@.WorldTabData.CVCAP;
      try { fillCv(b, ev); } catch (Throwable t) { this.cOk = false; this.cIds = new String[0]; this.cRec = new String[0]; this.cAllow = "|"; @PKG@.MenuUtil.warn("world screen: the collections view failed: " + t); }
    } else if (this.view == 3) {
      vc = @PKG@.WorldTabData.EVCAP;
      try { fillEv(b, ev); } catch (Throwable t) { this.eOk = false; this.eTi = new String[0]; this.eAllow = "|"; @PKG@.MenuUtil.warn("world screen: the explore view failed: " + t); }
    } else {
      vc = @PKG@.WorldTabData.IVCAP;
      try { fillIv(b, ev); } catch (Throwable t) { this.iOk = false; this.iMb = new int[0]; this.iVb = new int[0]; this.iAllow = "|"; @PKG@.MenuUtil.warn("world screen: the island view failed: " + t); }
    }
    b.set("#SkyyWtabCap.Text", this.tcap.length() > 0 ? this.tcap : vc);
    return;
  }
  try { fillTravel(b, ev, places()); }''')

# ---- the actions: the home buttons open the views; navigation before the token; the bridge acts after the token + profile checks
P.rep('''M(wtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', WV_ACT + '''M(wtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''    if (a.equals("isl")) { hub("world", "island", "Island settings"); return; }
    if (a.equals("exp")) { hub("world", "explore", "the Explore page"); return; }
    if (a.equals("qlog")) { hub("world", "quests", "the Quest log"); return; }
    if (a.equals("coll")) { hub("character", "collections", "Collections"); return; }''',
      '''    // 0.3.74 (oldmenu6): the Quest log / Collections / Explore / Island settings are views of this screen (no old page); a click meant for
    // another view or the home cards = a caption, no call
    int vo = viewOf(a);
    if (vo >= 0 && vo != this.view) { say(@PKG@.WorldTabData.NONE); return; }
    if (a.startsWith("vw:")) { goView(@PKG@.InvPage.toInt(a.substring(3), 0)); return; }
    if (a.equals("vrf")) { vRefresh(); return; }
    if (a.equals("isl")) { goView(4); return; }
    if (a.equals("exp")) { goView(3); return; }
    if (a.equals("qlog")) { goView(1); return; }
    if (a.equals("coll")) { this.cWant = "Combat"; this.cId = ""; goView(2); return; }   // the codex card: the Combat collections
    if (navView(a)) return;''')
P.rep('''    if (a.startsWith("go:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || this.keys == null || k >= this.keys.length || this.keys[k] == null) { say("Nothing there"); return; }
      travel(this.keys[k]);''', '''    if (actView(a, d)) return;   // 0.3.74: the views' bridge acts (each only where the drawing showed it)
    if (a.startsWith("go:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || this.keys == null || k >= this.keys.length || this.keys[k] == null) { say("Nothing there"); return; }
      travel(this.keys[k]);''')

# ======================================================================= the SKILL PAGE's Collections + the INVENTORY's quest row = the views
P.rep('''# 0.3.63: the Social tab = the social screen (false = it could not open: today's route below)
M(skpg, r"""
public boolean socialTab() {''', '''# 0.3.74 (oldmenu6): the world screen on a view (Collections = that skill's category); false = it could not open
M(skpg, r"""
public boolean worldAt(int v, String want) {
  @PKG@.WorldTab pg = null;
  try { pg = @PKG@.WorldTab.openAt(this.pref, this.pst, this.playerRef, "skill page", v, want); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the world screen failed: " + t); }
  if (pg == null) return false;
  this.answered = true;
  if (!still()) finish("world");
  return true;
}""")
# 0.3.63: the Social tab = the social screen (false = it could not open: today's route below)
M(skpg, r"""
public boolean socialTab() {''')
P.rep('''    if (a.equals("col")) { hub("character", "collections", "Collections"); return; }''',
      '''    if (a.equals("col")) { if (!worldAt(2, this.skill)) say("Collections could not open here - try the World tab"); return; }   // 0.3.74: the collections view''')
P.rep('''M(ipg, r"""
public void nowGo(int i) {''', '''# 0.3.74 (oldmenu6): the world screen on a view (the Right now quest row / the quest button = the quests view)
M(ipg, r"""
public void worldView(int v) {
  @PKG@.WorldTab wt = null;
  try { wt = @PKG@.WorldTab.openAt(this.pref, this.pst, this.playerRef, "inventory", v, ""); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("inventory: the world screen failed: " + t); }
  if (wt == null) { say("The World screen could not open here"); return; }
  this.answered = true;
  if (!still()) finish("world");
}""")
M(ipg, r"""
public void nowGo(int i) {''')
P.rep('''  int c = t.indexOf(':');
  String hub = c < 0 ? t : t.substring(0, c);
  String tab = c < 0 ? "" : t.substring(c + 1);
  if (hub.equals("tree")) {   // 0.3.69 (oldmenu1)''', '''  if (t.equals("world:quests")) { worldView(1); return; }   // 0.3.74 (oldmenu6): the quests view
  int c = t.indexOf(':');
  String hub = c < 0 ? t : t.substring(0, c);
  String tab = c < 0 ? "" : t.substring(c + 1);
  if (hub.equals("tree")) {   // 0.3.69 (oldmenu1)''')
P.rep('''    if (a.equals("nowq")) { openHub("world", "quests", "Quests"); return; }''', '''    if (a.equals("nowq")) { worldView(1); return; }   // 0.3.74 (oldmenu6): the quests view''')

# ======================================================================= the ratchet: OLD_LEFT shrinks by the four rows this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"),
    ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.74 (oldmenu6): world:quests (Quest log / the Right now quest row = the quests view - SkyyQuests 0.4.5 quest:fn:act), character:collections
# (World + skill page Collections = the collections view - SkyyCollections 0.2.37 coll:fn:act), world:explore (the explore view - SkyyExploration 0.3.5
# explore:fn:act), world:island (Island settings = the island view - SkyyIslands 0.5.27 island:fn:act) are gone.
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"),
    ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.74: no system / command / class"
_i = P.s.index
assert _i("public void iRefresh() {") < _i("public void finish(String why) {\n  boolean was = this.closed;") < _i("public String wact(String key") \
    < _i("public void fillQv(") < _i("public void fillCvD(") < _i("public void fillCv(") < _i("public void evZones(") < _i("public void fillEv(") \
    < _i("public void ivOverview(") < _i("public void fillIv(") < _i("  char cur = this.view == 1 ? 'Q' :") < _i('public static int viewOf(String a) {\n  if (a.startsWith("ql:")') \
    < _i("public void goView(int v) {\n  this.answered = true;\n  int was = this.view;") < _i("public boolean navView(String a)") < _i("public void iDo(String op") \
    < _i("public boolean actView(String a, String d)") < _i("    if (navView(a)) return;") < _i("    if (actView(a, d)) return;"), "0.3.74: the world view methods before their callers"
assert _i("public static @PKG@.WorldTab openAt(") < _i("public boolean worldAt(int v, String want)") < _i('if (!worldAt(2, this.skill))') \
    and _i("public static @PKG@.WorldTab openAt(") < _i("public void worldView(int v)") < _i('if (t.equals("world:quests")) { worldView(1); return; }') < _i('if (a.equals("nowq")) { worldView(1); return; }'), \
    "0.3.74: openAt before its callers"
assert _i("public static String[] wrap2(String s, int n)") < _i("public void fillEv("), "0.3.74: MarketTab.wrap2 before the explore view"
for _old in ('hub("world", "island"', 'hub("world", "explore"', 'hub("world", "quests"', 'hub("character", "collections"', 'openHub("world", "quests"'):
    assert _old not in P.s[P.s.index("# ================= 0.3.50 THE INVENTORY SCREEN"):P.s.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")], "0.3.74: no old link left: " + _old
P.finish()

HARNESS_OLD6_STATIC = r'''    # ---- OLD6 (0.3.74; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the ratchet shrank by exactly the four rows this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("world", "quests"), ("world", "explore"), ("world", "island"), ("character", "collections")]) and not (left2_ - lefto_)
            and len(left2_) == len(lefto_) - 4,
            "OLD6 RATCHET OLD_LEFT lost world:quests + world:explore + world:island + character:collections, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('hub("world", "quests"' not in g and 'hub("world", "explore"' not in g and 'hub("world", "island"' not in g and 'hub("character", "collections"' not in g
            and 'openHub("world", "quests"' not in g and '"the Explore page"' not in g and '"Explore page"' not in g and 'if (a.equals("nowq")) { worldView(1); return; }' in g
            and 'if (t.equals("world:quests")) { worldView(1); return; }' in g and 'if (!worldAt(2, this.skill))' in g,
            "OLD6 STATIC no Quest log / Explore / Island settings / Collections old-page link left; the inventory's quest row + the skill page's Collections open the views")
    K.check('wact("quest:fn:act", op, this.qTok, this.qPk, arg)' in g and 'wact("coll:fn:act", op, this.cTok, this.cPk, arg)' in g
            and 'wact("explore:fn:act", op, this.eTok, this.ePk, arg)' in g and 'wact("island:fn:act", op, this.iTok, this.iPk, arg)' in g
            and 'call(key, new Object[] { op, this.playerRef.getUuid(), tok, pk, arg })' in g and 'qDo("skip", this.qTk[k] + "|" + this.qSkS[k])' in g
            and 'cDo("buy", this.cBuy)' in g and 'this.cBuy = h[3] + "|" + nt + "|" + pr;' in g and 'iDo("notify", this.iShowN)' in g
            and '+ "|" + (c >= this.iPm[r] ? "1" : "0"));' in g,
            "OLD6 STATIC the views call the four bridges with the read's token + profile key; toggles / Buy / grid cells send the drawn state / tier + price")
    K.check(all(("0.3.74: %s" % t_) in g for t_ in ("the quests panel fits", "the quest lines fit", "a task row fits", "the collections view fits", "the collection detail fits",
                                                      "the recipes fit", "the explore view fits", "the zones fit", "the titles fit", "a checklist fits", "the island view fits",
                                                      "the island overview fits", "the co-op list fits", "the permission grid fits", "the visitors list fits", "the ban list fits",
                                                      "the view markups are proven", "a view binding names its own element", "the home cards come right before the hint row")),
            "OLD6 STATIC the build asserts every new view fits 1080, its run-time markup is proven, its bindings name its own section")
    mw6_ = re.search(r"WT_ELEMENTS <= (\d+)", g)
    K.check(mw6_ is not None and int(mw6_.group(1)) <= 800 and 'WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEI")' in g,
            "OLD6 STATIC the world screen's budget = the frame + its biggest section (one packet), still <= 800")
'''

HARNESS_OLD6 = r'''    # ---- OLD6 (0.3.74, round oldmenu6): THE WORLD TAB'S QUESTS / COLLECTIONS / EXPLORE / ISLAND VIEWS (stand-ins = the four bridge contracts:
    # tools/quests_0_4_5_patch.py, tools/collections_0_2_37_patch.py, tools/exploration_0_3_5_patch.py, tools/islands_0_5_27_patch.py)
    def sel_ok6(pk_):
        ids_ = set()
        for c_ in cmds_of(pk_):
            t_ = str(c_.text) if c_.text is not None else ""
            ids_ |= set(re.findall(r"#([A-Za-z0-9]+) *\{", t_))
        bad_ = []
        for c_ in cmds_of(pk_):
            s_ = str(c_.selector) if c_.selector is not None else ""
            t_ = str(c_.text) if c_.text is not None else ""
            if s_ and s_.lstrip("#").split(".")[0] not in ids_:
                bad_.append(("append into " if t_ else "set ") + s_)
        for b_ in binds_of(pk_):
            if b_[1].lstrip("#") not in ids_:
                bad_.append("bind " + b_[1])
        return bad_
    has6 = lambda pk_, ident: any(re.search(r"#%s *\{" % ident, str(c_.text or "")) for c_ in cmds_of(pk_))
    txt6 = lambda c_, k_: str(sval(c_, "#SkyyWtab%s.Text" % k_))
    bind6 = lambda p_, act_: [b_ for b_ in binds_of(p_) if ('"a":"%s"' % act_) in b_[2].replace(" ", "")]
    app6 = lambda p_, parent: [str(c_.text or "") for c_ in cmds_of(p_) if str(c_.selector) == "#SkyyWtab" + parent and c_.text is not None]
    NONE6 = str(WTD.NONE)
    uk6 = uk4
    SECT6 = {1: "SkyyWtabQv", 2: "SkyyWtabCv", 3: "SkyyWtabEv", 4: "SkyyWtabIv"}

    def only6(p_, v_):   # the frame + ONE section: that view and no other, no home cards
        return (p_ is not None and has6(p_, SECT6[v_]) and not has6(p_, "SkyyWtabBody")
                and not [k_ for k_, s_ in SECT6.items() if k_ != v_ and has6(p_, s_)] and not sel_ok6(p_))
    for k_ in ("quest:fn:act", "coll:fn:act", "explore:fn:act", "island:fn:act", "hub:tab:world:quests", "hub:tab:character:collections", "hub:tab:world:explore", "hub:tab:world:island"):
        BR.remove(k_)
    WS, p_ = w_open("OLD6 open")
    K.check(has6(p_, "SkyyWtabBody") and not [s_ for s_ in SECT6.values() if has6(p_, s_)] and not sel_ok6(p_)
            and 'Text: "Explore"' in mk_of(p_, "SkyyWtabEgo") and 'Text: "Quest log"' in mk_of(p_, "SkyyWtabQlog"),
            "OLD6 OPEN the home packet = the frame + the cards only (no view); every set / binding names a drawn element %s" % sel_ok6(p_)[:3])
    # ---- the views without their bridge (an older mod / not installed): said, nothing pressable, no old page
    for a_, v_, key_, hub_, old_, off_ in (("qlog", 1, "quest:fn:act", "hub:tab:world:quests", "QVOLD", "QVOFF"), ("coll", 2, "coll:fn:act", "hub:tab:character:collections", "CVOLD", "CVOFF"),
                                          ("exp", 3, "explore:fn:act", "hub:tab:world:explore", "EVOLD", "EVOFF"), ("isl", 4, "island:fn:act", "hub:tab:world:island", "IVOLD", "IVOFF")):
        p_ = w_ev({"a": a_}, "OLD6 FALL %s without %s" % (a_, key_))
        hd_ = "#SkyyWtab%sH.Text" % SECT6[v_][8:]
        K.check(int(WS.view) == v_ and only6(p_, v_) and str(sval(cmap(p_), hd_)) == str(getattr(WTD, off_)) and PK.pm.getCustomPage() == WS,
                "OLD6 FALL %s with no %s = the view (ONE section) says it is not on this server; no old page opened %s" % (a_, key_, sel_ok6(p_)[:3]))
        BR.put(hub_, OBJ(["SkyyX", "Tab", JClass("java.lang.Integer")(1), "x", None, None]))
        p_ = w_ev({"a": "vrf"}, "OLD6 FALL refresh with the old hub tab")
        K.check(str(sval(cmap(p_), hd_)) == str(getattr(WTD, old_)), "OLD6 FALL %s: an older mod (its hub tab, no %s) = the view names the version it needs" % (a_, key_))
        BR.remove(hub_)
        p_ = w_ev({"a": "vw:0"}, "OLD6 back to World")
        K.check(int(WS.view) == 0 and has6(p_, "SkyyWtabBody"), "OLD6 the World sub-tab = the cards (no back button)")

    # ======== QUESTS (quest:fn:act stand-in)
    QD = {"tok": "q1", "pk": "prof-A", "ready": "1", "track": "tutorial", "hide": "0", "reads": [], "acts": [], "null": False, "moment": False, "bad": False}
    QL6 = [["tutorial", 0, "Getting Started", "0", ""], ["farmer", 1, "The Farmer's Field", "0", ""], ["daily", 1, "Daily Jobs", "1", ""],
           ["marlow", 2, "Marlow's Lesson", "0", "Talk to Marlow at the hub dock"], ["done1", 3, "First Steps", "0", ""]] + \
          [["f%02d" % i_, 1, "Line %02d" % i_, "0", ""] for i_ in range(8)]
    QT6 = {"tutorial": [["t1", 1, "0", "", "1/1", 1000, "Hub", "25 coins", "Talk to the Farmer", ""],
                        ["t2", 0, "0", "", "4/10", 400, "Emerald Wilds", "2 Oak Sapling", "Chop 10 logs", "Any tree counts"],
                        ["t3", 4, "1", "", "", -1, "", "", "Craft a pickaxe", ""],
                        ["t4", 3, "0", "", "", -1, "", "10 coins", "Catch a fish", ""]]
                       + [["t%d" % i_, 0, "0", "", "0/5", 0, "", "5 coins", "Task %d" % i_, ""] for i_ in range(5, 9)]
                       + [["t%d" % i_, 2, "0", "", "1/1", 1000, "", "1 coin", "Done task %d" % i_, ""] for i_ in range(9, 13)],
           "farmer": [["f1", 0, "0", "", "", -1, "", "", "Plant wheat", ""]],
           "daily": [["d1", 0, "0", "Easy", "2/5", 400, "Farm", "50 coins", "Harvest 5 wheat", ""], ["d2", 1, "0", "Hard", "5/5", 1000, "", "200 coins", "Mine 50 ore", ""]],
           "done1": [["x1", 2, "0", "", "1/1", 1000, "", "", "Walk", ""]]}

    def q_row(k_):
        l_, t_ = k_.split(".", 1)
        h_ = [x_ for x_ in QT6.get(l_, []) if x_[0] == t_]
        return h_[0] if h_ else None

    def q_state():
        if QD["bad"]:
            return "garbage"
        claims_ = sum(1 for l_ in QT6.values() for t_ in l_ if t_[1] == 1)
        L = ["h|%s|%s|%s|%s|%s|%d|3725|%d" % (QD["tok"], QD["pk"], QD["ready"], QD["track"], QD["hide"], claims_, len(QL6))]
        if QD["ready"] != "1":
            return L[0]
        for l_ in QL6:
            ts_ = QT6.get(l_[0], [])
            dn_ = sum(1 for t_ in ts_ if t_[1] == 2)
            L.append("l|%s|%d|%d|%d|%s|%s" % (l_[0], l_[1], dn_, max(1, len(ts_)), l_[3], l_[2]))
            if l_[1] == 2:
                L.append("w|%s|%s" % (l_[0], l_[4]))
                continue
            for t_ in ts_:
                L.append("t|%s|%s|%d|%s|%s|%s|%d|%s|%s|%s" % (l_[0], t_[0], t_[1], t_[2], t_[3], t_[4], t_[5], t_[6], t_[7], t_[8]))
                if t_[9]:
                    L.append("x|%s|%s|%s" % (l_[0], t_[0], t_[9]))
        return "\n".join(L)

    def f_qact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        if a_[0] == "state":
            QD["reads"].append(a_)
            return q_state()
        QD["acts"].append(a_)
        if QD["null"]:
            return None
        op, tok, pk, arg = a_[0], a_[2], a_[3], a_[4]
        if op == "refresh":
            return ""
        if pk != QD["pk"]:
            return "=Your profile changed - here are this profile's quests. Nothing changed."
        if tok != QD["tok"]:
            return "=The quest list changed - look again. Nothing changed."
        if QD["moment"]:
            QD["moment"] = False
            return "=One moment."
        if op == "track":
            k_, f_ = arg.rsplit("|", 1)
            on_ = k_ == QD["track"]
            if on_ != (f_ == "1"):
                return "=That changed since you looked - look again. Nothing changed."
            QD["track"] = "" if on_ else k_
            return ("+Stopped tracking %s." if on_ else "+Tracking %s on your HUD.") % k_
        if op == "skip":
            k_, f_ = arg.rsplit("|", 1)
            r_ = q_row(k_)
            if r_ is None:
                return "-No task '%s' (see /quests)." % k_
            sk_ = r_[1] == 3
            if sk_ != (f_ == "1"):
                return "=That changed since you looked - look again. Nothing changed."
            r_[1] = 0 if sk_ else 3
            return ("+Unskipped %s." if sk_ else "+Skipped %s.") % r_[8]
        if op == "claim1":
            r_ = q_row(arg)
            if r_ is None or r_[1] != 1:
                return "-Nothing to claim for that task."
            r_[1] = 2
            return "+Claimed %s: %s." % (r_[8], r_[7])
        if op == "claim":
            n_ = 0
            for l_ in QT6.values():
                for t_ in l_:
                    if t_[1] == 1:
                        t_[1] = 2
                        n_ += 1
            return ("+Claimed %d rewards." % n_) if n_ else "-Nothing to claim."
        if op in ("hide", "show"):
            QD["hide"] = "1" if op == "hide" else "0"
            return "+Tutorial tasks %s." % ("hidden from your quest widget" if op == "hide" else "shown on your quest widget again")
        return "-Unknown quest action."
    BR.put("quest:fn:act", Fn(f_qact))
    nq_ = lambda: len(QD["acts"])
    p_ = w_ev({"a": "qlog"}, "OLD6 Q the Quest log button")
    cm = cmap(p_)
    K.check(int(WS.view) == 1 and only6(p_, 1) and QD["reads"][-1] == ["state", uk6, None, None, None] and txt6(cm, "QvC") == "13 quest lines   -   2 rewards waiting"
            and str(WTD.ST1) in mk_of(p_, "SkyyWtabQvVt1") and txt6(cm, "Cap") == str(WTD.QVCAP),
            "OLD6 Q Quest log = the QUESTS VIEW (ONE section; the state read; the head count; the Quests sub-tab selected) %s" % sel_ok6(p_)[:3])
    K.check(txt6(cm, "QvL0N") == "Getting Started  (tracked)" and txt6(cm, "QvL0S") == "On your HUD   -   4 / 12 done" and txt6(cm, "QvL0P") == "Showing"
            and txt6(cm, "QvL3S") == "Locked - not started   -   0 / 1 done" and txt6(cm, "QvL2S") == "Open   -   0 / 2 done   -   daily"
            and txt6(cm, "QvL4S") == "All done   -   1 / 1 done" and vis4(cm, "QvL10") and txt6(cm, "QvLpg") == "Page 1 / 2" and vis4(cm, "QvLp")
            and ("Width: %d," % (4 * int(WTD.QLBARW) // 12)) in " ".join(app6(p_, "QvL0B")) and len(bind6(p_, "ql:3")) == 1,
            "OLD6 Q LINES in the page's order: tracked / open / daily / locked / all done, x / y done + a bar, 11 a page (2 pages)")
    K.check(txt6(cm, "QvN") == "Getting Started" and txt6(cm, "QvS") == "On your HUD   -   4 / 12 done" and txt6(cm, "QvTr") == "Stop tracking" and len(bind6(p_, "qtr")) == 1
            and '"t"' in bind6(p_, "qtr")[0][2] and txt6(cm, "Qk0") == "Open (8)" and txt6(cm, "Qk1") == "Done (4)" and str(WTD.ST1) in mk_of(p_, "SkyyWtabQk0"),
            "OLD6 Q the picked line: status, Stop tracking (the drawn state: tracked), Open (8) | Done (4) with Open selected")
    K.check(vis4(cm, "QvT0S1") and not vis4(cm, "QvT0S0") and txt6(cm, "QvT0S1") == "Ready to claim" and vis4(cm, "QvT0C") and not vis4(cm, "QvT0K")
            and txt6(cm, "QvT1N") == "Chop 10 logs" and txt6(cm, "QvT1P") == "4/10" and ("Width: %d," % (400 * int(WTD.QBARW) // 1000)) in " ".join(app6(p_, "QvT1B"))
            and txt6(cm, "QvT1W") == "Where: Emerald Wilds" and txt6(cm, "QvT1R") == "Reward: 2 Oak Sapling" and txt6(cm, "QvT1H") == "Any tree counts"
            and txt6(cm, "QvT1K") == "Skip" and vis4(cm, "QvT1K") and not vis4(cm, "QvT1C") and txt6(cm, "QvT2N") == "Craft a pickaxe  (optional)" and vis4(cm, "QvT2S4")
            and txt6(cm, "QvT2R") == "No reward" and txt6(cm, "QvTpg") == "Page 1 / 2" and txt6(cm, "QvCa") == "Claim all (2)" and txt6(cm, "QvHd") == "Hide tutorial",
            "OLD6 Q TASKS: the state word in its colour, progress + bar, where, reward, hint, Claim (ready) / Skip, 6 a page; Claim all (2); Hide tutorial")
    n0_ = nq_()
    p_ = w_ev({"a": "qcl:1", "t": str(WS.tok)}, "OLD6 Q SAFE a forged Claim on an open task")
    p2_ = w_ev({"a": "qcl:0", "t": "old"}, "OLD6 Q SAFE Claim with an old token")
    K.check(nq_() == n0_ and cap4(p_) == NONE6 and "The page changed" in cap4(p2_), "OLD6 Q SAFE a button not drawn / an older drawing = a caption, no call")
    p_ = w_ev({"a": "qcl:0", "t": str(WS.tok)}, "OLD6 Q Claim")
    K.check(QD["acts"][-1] == ["claim1", uk6, "q1", "prof-A", "tutorial.t1"] and cap4(p_) == "Claimed Talk to the Farmer: 25 coins." and txt6(cmap(p_), "QvT0N") == "Chop 10 logs"
            and txt6(cmap(p_), "QvCa") == "Claim all (1)", "OLD6 Q Claim = quest:fn:act claim1 <line.task> with the read's token + profile key; the redraw")
    p_ = w_ev({"a": "qsk:0", "t": str(WS.tok)}, "OLD6 Q Skip")
    K.check(QD["acts"][-1] == ["skip", uk6, "q1", "prof-A", "tutorial.t2|0"] and cap4(p_) == "Skipped Chop 10 logs.", "OLD6 Q Skip = skip <line.task>|0 (the drawn state)")
    cm = cmap(p_)
    ks_ = [k_ for k_ in range(int(WTD.QTN)) if txt6(cm, "QvT%dN" % k_) == "Chop 10 logs"]
    K.check(ks_ == [5] and txt6(cm, "QvT5K") == "Unskip" and vis4(cm, "QvT5S3") and txt6(cm, "QvT4N") == "Task 8",
            "OLD6 Q a skipped task goes to the end of Open, greyed, Unskip")
    p_ = w_ev({"a": "qtpg:1"}, "OLD6 Q tasks page 2")
    cm = cmap(p_)
    K.check(txt6(cm, "QvTpg") == "Page 2 / 2" and txt6(cm, "QvT0N") == "Catch a fish" and txt6(cm, "QvT0K") == "Unskip" and not vis4(cm, "QvT1"),
            "OLD6 Q > = page 2")
    p_ = w_ev({"a": "qtpg:-1"}, "OLD6 Q tasks page 1")
    QT6["tutorial"][1][1] = 0   # another click (the widget) unskipped it meanwhile
    p_ = w_ev({"a": "qsk:%d" % (ks_[0] if ks_ else 0), "t": str(WS.tok)}, "OLD6 Q a stale Unskip")
    K.check(QD["acts"][-1][4] == "tutorial.t2|1" and cap4(p_) == "That changed since you looked - look again. Nothing changed." and QT6["tutorial"][1][1] == 0,
            "OLD6 Q SAFE a stale toggle sends the drawn state; the bridge's '=' answer in the caption, never flipped the wrong way")
    p_ = w_ev({"a": "qk:1"}, "OLD6 Q the Done tab")
    cm = cmap(p_)
    K.check(int(WS.qSub) == 1 and txt6(cm, "Qk1") == "Done (5)" and vis4(cm, "QvT0S2") and not vis4(cm, "QvT0C") and not vis4(cm, "QvT0K") and str(WTD.ST1) in mk_of(p_, "SkyyWtabQk1"),
            "OLD6 Q Done = the finished tasks, green, no buttons")
    n0_ = nq_()
    p_ = w_ev({"a": "qsk:0", "t": str(WS.tok)}, "OLD6 Q SAFE a forged Skip on a done task")
    K.check(nq_() == n0_ and cap4(p_) == NONE6, "OLD6 Q SAFE Skip on a done row = a caption, no call")
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q Stop tracking")
    K.check(QD["acts"][-1] == ["track", uk6, "q1", "prof-A", "tutorial|1"] and txt6(cmap(p_), "QvTr") == "Track this line" and QD["track"] == "",
            "OLD6 Q Track = track <line>|1 (the drawn state); the button now says Track this line")
    QD["track"] = "tutorial"   # the widget tracked it again meanwhile
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q a stale Track")
    K.check(QD["acts"][-1][4] == "tutorial|0" and "That changed since you looked" in cap4(p_) and QD["track"] == "tutorial", "OLD6 Q SAFE a stale Track = the bridge's '=' line, nothing flipped")
    QD["track"] = "farmer"
    p_ = w_ev({"a": "qca", "t": str(WS.tok)}, "OLD6 Q Claim all")
    K.check(QD["acts"][-1][:4] == ["claim", uk6, "q1", "prof-A"] and cap4(p_) == "Claimed 1 rewards." and not vis4(cmap(p_), "QvCa"), "OLD6 Q Claim all = claim; then it is gone")
    n0_ = nq_()
    p_ = w_ev({"a": "qca", "t": str(WS.tok)}, "OLD6 Q SAFE Claim all with nothing drawn")
    K.check(nq_() == n0_ and cap4(p_) == NONE6, "OLD6 Q SAFE Claim all not drawn = a caption, no call")
    p_ = w_ev({"a": "qhd", "t": str(WS.tok)}, "OLD6 Q Hide tutorial")
    p2_ = w_ev({"a": "qhd", "t": str(WS.tok)}, "OLD6 Q Show tutorial")
    K.check([a_[0] for a_ in QD["acts"][-2:]] == ["hide", "show"] and txt6(cmap(p_), "QvHd") == "Show tutorial" and txt6(cmap(p2_), "QvHd") == "Hide tutorial",
            "OLD6 Q Hide / Show tutorial = hide / show by the drawn state")
    p_ = w_ev({"a": "qlpg:1"}, "OLD6 Q lines page 2")
    K.check(txt6(cmap(p_), "QvLpg") == "Page 2 / 2" and txt6(cmap(p_), "QvL0N") == "Line 06", "OLD6 Q lines > = page 2")
    p_ = w_ev({"a": "qlpg:1"}, "OLD6 Q past the last page")
    K.check(cap4(p_) == "This is the last page", "OLD6 Q past the last page = a caption")
    p_ = w_ev({"a": "qlpg:-1"}, "OLD6 Q lines page 1")
    p_ = w_ev({"a": "ql:3"}, "OLD6 Q the locked line")
    cm = cmap(p_)
    K.check(str(WS.qLine) == "marlow" and txt6(cm, "QvW") == "How to start: Talk to Marlow at the hub dock" and not vis4(cm, "QvTr") and not vis4(cm, "QvSr")
            and not vis4(cm, "QvT0") and txt6(cm, "QvL3P") == "Showing", "OLD6 Q a locked line = how to start it, no Track, no tasks")
    n0_ = nq_()
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q SAFE a forged Track on a locked line")
    K.check(nq_() == n0_ and cap4(p_) == NONE6, "OLD6 Q SAFE Track not drawn = a caption, no call")
    p_ = w_ev({"a": "ql:2"}, "OLD6 Q the daily line")
    cm = cmap(p_)
    K.check(txt6(cm, "QvS") == "Open   -   1 / 2 done   -   Daily jobs: new ones in 1h 2m" and txt6(cm, "QvT0N") == "Easy  Harvest 5 wheat",
            "OLD6 Q the daily line: new jobs in (the read's seconds), the tier tag first")
    QD["moment"] = True
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q '=One moment.'")
    K.check(cap4(p_) == "One moment." and QD["track"] == "farmer" and QD["acts"][-1][0] == "track", "OLD6 Q the bridge's 350 ms guard = the caption, nothing changed")
    QD["pk"] = "prof-B"
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q a profile switch")
    K.check(QD["acts"][-1][3] == "prof-A" and "profile changed" in cap4(p_) and str(WS.qPk) == "prof-B", "OLD6 Q SAFE a profile switch = the bridge refuses; the redraw reads the new key")
    QD["tok"] = "q2"
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q a reload")
    K.check(QD["acts"][-1][2] == "q1" and "quest list changed" in cap4(p_) and str(WS.qTok) == "q2", "OLD6 Q SAFE /questadmin reload between read and click = refused, the new token next")
    QD["null"] = True
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q a null answer")
    K.check(cap4(p_) == str(WTD.NULLANS), "OLD6 Q a null answer (not on the world thread) = said, nothing done")
    QD["null"] = False
    p_ = w_ev({"a": "qtr", "t": str(WS.tok)}, "OLD6 Q Track again")
    K.check(QD["acts"][-1] == ["track", uk6, "q2", "prof-B", "daily|0"] and cap4(p_) == "Tracking daily on your HUD.", "OLD6 Q Track this line = track <line>|0")
    QD["ready"] = "0"
    p_ = w_ev({"a": "vrf"}, "OLD6 Q still loading")
    K.check(QD["acts"][-1][0] == "refresh" and txt6(cmap(p_), "QvH") == "Your quests are still loading - try again in a moment." and not vis4(cmap(p_), "Qvb"),
            "OLD6 Q Refresh = quest:fn:act refresh; quests not loaded = said, nothing to press")
    QD["ready"] = "1"
    QD["bad"] = True
    p_ = w_ev({"a": "vrf"}, "OLD6 Q a bad read")
    K.check(txt6(cmap(p_), "QvH") == str(WTD.QVFAIL), "OLD6 Q an unreadable state = said")
    QD["bad"] = False
    p_ = w_ev({"a": "vw:0"}, "OLD6 Q back to World")
    n0_ = nq_()
    p_ = w_ev({"a": "qca", "t": str(WS.tok)}, "OLD6 Q SAFE a quest act on the cards")
    p2_ = w_ev({"a": "ql:0"}, "OLD6 Q SAFE a quest pick on the cards")
    K.check(nq_() == n0_ and cap4(p_) == NONE6 and cap4(p2_) == NONE6, "OLD6 Q SAFE a forged quest action on the home cards = a caption, no call")
    p_ = w_ev({"a": "vw:1"}, "OLD6 Q the Quests sub-tab")
    n0_ = nq_()
    p_ = w_ev({"a": "go:0", "t": str(WS.tok)}, "OLD6 Q SAFE a travel Go inside the quests view")
    K.check(cap4(p_) == NONE6 and not bool(WS.closed) and nq_() == n0_, "OLD6 Q SAFE a home button inside a view = a caption, nothing travels")
    # the inventory's quest button / Right now quest row = the quests view
    pgI6 = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI6.handleDataEvent(PK.ref, PK.st, '{"a":"nowq"}')
    WS = PK.pm.getCustomPage()
    K.check(len(pages(PK, f0_)) == 1 and WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab" and int(WS.view) == 1 and bool(pgI6.closed),
            "OLD6 Q the inventory's quest button = the world screen on the quests view (ONE packet), no old page")
    pgI6 = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    pgI6.nowT = _JA(JS)(["world:quests"])
    f0_ = len(E.sent(PK))
    pgI6.nowGo(0)
    WS = PK.pm.getCustomPage()
    K.check(WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab" and int(WS.view) == 1, "OLD6 Q the Right now quest row's Go = the quests view")
    K.notes.append("OLD6 Q ran: quest:fn:act reads %d, acts %d" % (len(QD["reads"]), len(QD["acts"])))

    # ======== COLLECTIONS (coll:fn:act stand-in)
    CD = {"tok": "c1", "pk": "prof-A", "reads": [], "acts": [], "seen": [], "null": False, "moment": False, "arm": None, "price": 12000, "tier": 5, "why": None, "craftpage": False}
    CK6 = [(0, "Farming"), (1, "Mining"), (2, "Foraging"), (3, "Combat")]
    CC6 = [("c_rotten", 3, 1234, 3, 9, 2500, "Rotten Flesh"), ("c_bone", 3, 50, 1, 9, 100, "Bone")] + [("c_m%02d" % i_, 3, 10 + i_, 1, 9, 100, "Mob drop %02d" % i_) for i_ in range(14)] \
        + [("c_spider", 3, 0, 0, 9, 50, "Spider Eye"), ("c_cobble", 1, 640, 2, 9, 1000, "Cobblestone")]
    CT6 = ["DONE", "DONE", "NEW", "BOUGHT", "NEXT", "LOCKED", "LOCKED", "LOCKED", "LOCKED"]
    CR6 = [("r1", 1, 1, "NEW", 1, "Rotten Pie"), ("r2", 1, 2, "", 0, "Zombie Charm")] + [("r%d" % i_, 0, i_, "", 0, "Recipe %02d" % i_) for i_ in range(3, 13)]

    def c_state():
        L = ["h|%s|%s|1|34|120|3|20|15|1" % (CD["tok"], CD["pk"])]
        for k_, n_ in CK6:
            cs_ = [c_ for c_ in CC6 if c_[1] == k_]
            L.append("k|%d|%d|%d|%d|%d|0|#c9d2dd|%s" % (k_, len([c_ for c_ in cs_ if c_[2] > 0]), len(cs_), sum(c_[3] for c_ in cs_), 9 * len(cs_), n_))
        for k_, n_ in CK6:
            for c_ in [x_ for x_ in CC6 if x_[1] == k_ and x_[2] > 0] + [x_ for x_ in CC6 if x_[1] == k_ and x_[2] == 0]:
                L.append("c|%s|%d|%d|%d|%d|%d|%s" % c_)
                if c_[2] > 0:
                    L.append("p|%s|Tier %d    %d / %d|Next: tier %d" % (c_[0], c_[3], c_[2], c_[5], c_[3] + 1))
        return "\n".join(L)

    def c_detail(id_):
        hit_ = [c_ for c_ in CC6 if c_[0] == id_]
        if not hit_:
            return "-No collection '%s'." % id_
        c_ = hit_[0]
        L = ["h|%s|%s|%s|%d|%d|%d|4|9|%d|1|%s" % (CD["tok"], CD["pk"], c_[0], c_[1], c_[2], c_[3], c_[5], c_[6]), "m|Combat|Normal|Zombies, husks", "g|1,234 / 2,500 to tier IV"]
        for t_, st_ in enumerate(CD.get("ct") or CT6):
            L.append("r|%d|%s|%d|+%d coins|x" % (t_ + 1, st_, 100 * (t_ + 1) ** 2, 50 * (t_ + 1)))
        for r_ in CR6:
            L.append("q|%s|%d|%d|%s|%d|%s" % r_)
        L.append(("y|" + CD["why"]) if CD["why"] else "b|%d|%d|Rotten Flesh tier %d rewards" % (CD["tier"], CD["price"], CD["tier"]))
        return "\n".join(L)

    def f_cact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        if a_[0] in ("state", "detail"):
            CD["reads"].append(a_)
            return c_state() if a_[0] == "state" else c_detail(a_[4])
        if a_[0] == "seen":
            CD["seen"].append(a_)
            return ""
        CD["acts"].append(a_)
        if CD["null"]:
            return None
        op, tok, pk, arg = a_[0], a_[2], a_[3], a_[4]
        if op == "refresh":
            return ""
        if pk != CD["pk"]:
            return "=Your profile changed - here are this profile's collections. Nothing changed."
        if tok != CD["tok"]:
            return "=The collections changed - look again. Nothing changed."
        if CD["moment"]:
            CD["moment"] = False
            return "=One moment."
        if op == "buy":
            f_ = arg.split("|")
            if CD["why"]:
                return "-" + CD["why"]
            if int(f_[1]) != CD["tier"] or int(f_[2]) != CD["price"]:
                return "=The offer changed - look again. Nothing changed."
            if CD["arm"] != arg:
                CD["arm"] = arg
                return "=Click Buy again within 10 s to buy tier %d of Rotten Flesh for %s coins." % (CD["tier"], "{:,}".format(CD["price"]))
            CD["arm"] = None
            CD["tier"], CD["price"] = CD["tier"] + 1, CD["price"] * 2
            return "+Bought tier %d of Rotten Flesh." % (CD["tier"] - 1)
        if op == "craft":
            if CD["craftpage"]:
                ST.openPage(PK.ref, PK.st, PK.pr, "test")   # the crafting page opens in place of this screen
            return "+" if arg == "r1" else "-That recipe is not unlocked yet."
        return "-Unknown collections action."
    BR.put("coll:fn:act", Fn(f_cact))
    nc_ = lambda: len(CD["acts"])
    WS, p_ = w_open("OLD6 C reopen")
    p_ = w_ev({"a": "coll"}, "OLD6 C the codex card's Collections")
    cm = cmap(p_)
    K.check(int(WS.view) == 2 and only6(p_, 2) and CD["reads"][-1] == ["state", uk6, None, None, None] and int(WS.cCat) == 3 and txt6(cm, "CvK3B") == "Showing"
            and txt6(cm, "CvK0B") == "Open" and txt6(cm, "CvT") == "Tiers reached 34 / 120      Maxed 3      Found 20      Recipes unlocked 15"
            and txt6(cm, "CvK3N") == "Combat" and txt6(cm, "CvK3F") == "Found 16 / 17" and txt6(cm, "CvGh") == "COMBAT  -  17 collections" and len(bind6(p_, "cc:1")) == 1,
            "OLD6 C the codex card = the COLLECTIONS VIEW on Combat: the totals line, the 4 category cards (Open / Showing) %s" % sel_ok6(p_)[:3])
    K.check(txt6(cm, "CvC0N") == "Rotten Flesh" and txt6(cm, "CvC0P") == "Tier 3    1234 / 2500" and txt6(cm, "CvC0S") == "Next: tier 4"
            and ("Width: %d," % (1234 * int(WTD.CCBARW) // 2500)) in " ".join(app6(p_, "CvC0B")) and vis4(cm, "CvC14") and txt6(cm, "CvGpg") == "Page 1 / 2"
            and len(bind6(p_, "cv:0")) == 1, "OLD6 C a category's cards: name, tier + progress, the Next line, a bar, View; 15 a page")
    p_ = w_ev({"a": "cpg:1"}, "OLD6 C cards page 2")
    cm = cmap(p_)
    K.check(txt6(cm, "CvC1N") == "Spider Eye" and txt6(cm, "CvC1P") == "Not found yet" and not app6(p_, "CvC1B") and not vis4(cm, "CvC2"), "OLD6 C page 2: the one not found yet last, no bar")
    p_ = w_ev({"a": "cc:1"}, "OLD6 C the Mining card")
    K.check(int(WS.cCat) == 1 and txt6(cmap(p_), "CvC0N") == "Cobblestone" and not vis4(cmap(p_), "CvC1"), "OLD6 C a category card = its collections")
    p_ = w_ev({"a": "cc:3"}, "OLD6 C back to Combat")
    p_ = w_ev({"a": "cv:0"}, "OLD6 C View Rotten Flesh")
    cm = cmap(p_)
    K.check(CD["reads"][-1] == ["detail", uk6, None, None, "c_rotten"] and vis4(cm, "CvD") and not vis4(cm, "CvG") and txt6(cm, "CvDN") == "Rotten Flesh"
            and txt6(cm, "CvDM") == "Combat collection   -   curve Normal   -   From: Zombies, husks" and txt6(cm, "CvDG") == "1,234 / 2,500 to tier IV"
            and ("Width: %d," % (1234 * int(WTD.CDBARW) // 2500)) in " ".join(app6(p_, "CvDB")) and only6(p_, 2),
            "OLD6 C View = the detail read (id), the meta + progress line + bar %s" % sel_ok6(p_)[:3])
    K.check(vis4(cm, "CvDt0S0") and txt6(cm, "CvDt0N") == "Tier I" and vis4(cm, "CvDt2S4") and txt6(cm, "CvDt2S4") == "NEW" and vis4(cm, "CvDt3S1") and vis4(cm, "CvDt4S2")
            and vis4(cm, "CvDt8S3") and txt6(cm, "CvDt1A") == "400" and txt6(cm, "CvDt0R") == "+50 coins|x" and not vis4(cm, "CvDt9"),
            "OLD6 C TIERS: DONE / NEW / BOUGHT / NEXT / LOCKED in their colours, the threshold, the rewards")
    K.check(CD["seen"] and CD["seen"][-1] == ["seen", uk6, "c1", "prof-A", "c_rotten"] and int(WS.cSeen) == 1,
            "OLD6 C a drawn collection with NEW tiers = coll:fn:act seen <id> once (what drawing the page does)")
    K.check(txt6(cm, "CvDy1") == "Buy tier V for 12,000 coins" and txt6(cm, "CvDy2") == "Unlocks: Rotten Flesh tier 5 rewards" and vis4(cm, "CvDyB") and len(bind6(p_, "cbuy")) == 1
            and txt6(cm, "CvR0N") == "NEW  Rotten Pie" and vis4(cm, "CvR0C") and not vis4(cm, "CvR1C") and txt6(cm, "CvR2S").startswith("T3   -   Locked")
            and txt6(cm, "CvDrh") == "RECIPES  (12)" and txt6(cm, "CvRpg") == "Page 1 / 2",
            "OLD6 C the coin Buy offer (tier + price), the recipes (tier, NEW first, Craft only where it can), 11 a page")
    p_ = w_ev({"a": "cbuy", "t": str(WS.tok)}, "OLD6 C Buy (first press)")
    K.check(CD["acts"][-1] == ["buy", uk6, "c1", "prof-A", "c_rotten|5|12000"] and cap4(p_) == "Click Buy again within 10 s to buy tier 5 of Rotten Flesh for 12,000 coins."
            and int(CD["tier"]) == 5, "OLD6 C Buy = buy <id>|<the drawn tier>|<the drawn price>; the first press = the bridge's question")
    old6_ = str(WS.tok)
    p_ = w_ev({"a": "cbuy", "t": str(WS.tok)}, "OLD6 C Buy (the same press again)")
    K.check(cap4(p_) == "Bought tier 5 of Rotten Flesh." and txt6(cmap(p_), "CvDy1") == "Buy tier VI for 24,000 coins", "OLD6 C the same press again = paid; the next offer drawn")
    n0_ = nc_()
    p_ = w_ev({"a": "cbuy", "t": old6_}, "OLD6 C SAFE Buy on the older drawing")
    K.check(nc_() == n0_ and "The page changed" in cap4(p_), "OLD6 C SAFE a double click (the older drawing) = no second buy")
    CD["price"] = 25000
    p_ = w_ev({"a": "cbuy", "t": str(WS.tok)}, "OLD6 C a changed offer")
    K.check(CD["acts"][-1][4] == "c_rotten|6|24000" and cap4(p_) == "The offer changed - look again. Nothing changed." and int(CD["tier"]) == 6,
            "OLD6 C SAFE the price changed between read and click = the bridge refuses (never a price the player did not see)")
    CD["why"] = "Coin unlocks need the collection found first"
    p_ = w_ev({"a": "vrf"}, "OLD6 C no offer")
    cm = cmap(p_)
    K.check(CD["acts"][-1][0] == "refresh" and txt6(cm, "CvDy1") == "Coin unlock" and txt6(cm, "CvDy2") == "Coin unlocks need the collection found first" and not vis4(cm, "CvDyB"),
            "OLD6 C Refresh = coll:fn:act refresh; no offer = the why-not line, no Buy")
    n0_ = nc_()
    p_ = w_ev({"a": "cbuy", "t": str(WS.tok)}, "OLD6 C SAFE a forged Buy")
    K.check(nc_() == n0_ and cap4(p_) == NONE6, "OLD6 C SAFE Buy not drawn = a caption, no call")
    CD["why"] = None
    p_ = w_ev({"a": "ccr:0", "t": str(WS.tok)}, "OLD6 C Craft")
    K.check(CD["acts"][-1] == ["craft", uk6, "c1", "prof-A", "r1"] and cap4(p_) == "Opening the crafting page." and not bool(WS.closed), "OLD6 C Craft = craft <recipe id>; '+' said")
    n0_ = nc_()
    p_ = w_ev({"a": "ccr:1", "t": str(WS.tok)}, "OLD6 C SAFE Craft where it cannot")
    K.check(nc_() == n0_ and cap4(p_) == NONE6, "OLD6 C SAFE Craft not drawn = a caption, no call")
    p_ = w_ev({"a": "crpg:1"}, "OLD6 C recipes page 2")
    K.check(txt6(cmap(p_), "CvR0N") == "Recipe 12" and txt6(cmap(p_), "CvRpg") == "Page 2 / 2", "OLD6 C recipes > = page 2")
    p_ = w_ev({"a": "crpg:-1"}, "OLD6 C recipes page 1")
    CD["ct"] = ["DONE"] * 9 + ["NEW"] + ["NEXT"] + ["LOCKED"] * 14
    s0_ = len(CD["seen"])
    p_ = w_ev({"a": "vrf"}, "OLD6 C a 25-tier ladder")
    cm = cmap(p_)
    K.check(txt6(cm, "CvDt0N") == "Tier IX" and txt6(cm, "CvDt2N") == "Tier XI" and vis4(cm, "CvDt2S2") and txt6(cm, "CvDt11N") == "Tier XX" and vis4(cm, "CvDt11")
            and txt6(cm, "CvDtn") == "+8 tiers done above, +5 more past these",
            "OLD6 C FIX a ladder longer than the 12 rows = a window with the NEXT tier in view (2 done rows above it) + how many are above / past")
    K.check(vis4(cm, "CvDt1S4") and len(CD["seen"]) == s0_ + 1, "OLD6 C FIX2 a NEW tier drawn in the window = coll:fn:act seen")
    CD["ct"] = ["DONE", "NEW"] + ["DONE"] * 12 + ["NEXT"]
    s0_ = len(CD["seen"])
    p_ = w_ev({"a": "vrf"}, "OLD6 C a 15-tier ladder, NEXT last")
    cm = cmap(p_)
    K.check(txt6(cm, "CvDt0N") == "Tier IV" and txt6(cm, "CvDt11N") == "Tier XV" and vis4(cm, "CvDt11S2") and txt6(cm, "CvDtn") == "+3 tiers done above these",
            "OLD6 C FIX the window stops at the ladder's end")
    K.check(len(CD["seen"]) == s0_, "OLD6 C FIX2 a NEW tier outside the window (not drawn) = no seen call, its NEW marker stays")
    CD["ct"] = None
    p_ = w_ev({"a": "vrf"}, "OLD6 C back to 9 tiers")
    K.check(txt6(cmap(p_), "CvDt0N") == "Tier I" and txt6(cmap(p_), "CvDtn") == "" and not vis4(cmap(p_), "CvDt9"), "OLD6 C FIX a short ladder = from tier I, no note")
    CD["moment"] = True
    p_ = w_ev({"a": "ccr:0", "t": str(WS.tok)}, "OLD6 C '=One moment.'")
    K.check(cap4(p_) == "One moment.", "OLD6 C the bridge's guard = the caption")
    CD["null"] = True
    p_ = w_ev({"a": "ccr:0", "t": str(WS.tok)}, "OLD6 C a null answer")
    K.check(cap4(p_) == str(WTD.NULLANS), "OLD6 C a null answer = said, nothing done")
    CD["null"] = False
    CD["pk"] = "prof-B"
    p_ = w_ev({"a": "ccr:0", "t": str(WS.tok)}, "OLD6 C a profile switch")
    K.check(CD["acts"][-1][3] == "prof-A" and "profile changed" in cap4(p_), "OLD6 C SAFE a profile switch = the bridge refuses")
    CD["tok"] = "c2"
    p_ = w_ev({"a": "ccr:0", "t": str(WS.tok)}, "OLD6 C a reload")
    K.check(CD["acts"][-1][2] == "c1" and "collections changed" in cap4(p_), "OLD6 C SAFE /collections reload = refused, the new token next")
    CD["craftpage"] = True
    w_ev({"a": "ccr:0", "t": str(WS.tok)}, "OLD6 C Craft opens the crafting page", n=None)
    cur_ = PK.pm.getCustomPage()
    K.check(CD["acts"][-1][:3] == ["craft", uk6, "c2"] and bool(WS.closed) and cur_ is not None and str(cur_.getClass().getSimpleName()) != "WorldTab",
            "OLD6 C Craft that opened the crafting page = this screen forgotten (no packet over it)")
    CD["craftpage"] = False
    # the skill page's Collections = that skill's category
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    E.pump(PK)
    SP6 = JV("SkillPage").open(PK.ref, PK.st, PK.pr, "Mining", "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    SP6.handleDataEvent(PK.ref, PK.st, '{"a":"col"}')
    WS = PK.pm.getCustomPage()
    K.check(len(pages(PK, f0_)) == 1 and WS is not None and str(WS.getClass().getSimpleName()) == "WorldTab" and int(WS.view) == 2 and int(WS.cCat) == 1 and bool(SP6.closed),
            "OLD6 C the Mining skill page's Collections = the world screen on the collections view, Mining picked (ONE packet), no old page")
    K.notes.append("OLD6 C ran: coll:fn:act reads %d, acts %d, seen %d" % (len(CD["reads"]), len(CD["acts"]), len(CD["seen"])))

    # ======== EXPLORE (explore:fn:act stand-in)
    TN6 = ["Wanderer", "Pathfinder", "Trailblazer", "Wayfarer", "Explorer", "Voyager", "Cartographer", "Pioneer", "Worldwalker", "Echo Seeker", "Wilds Walker",
           "Sand Strider", "Frost Ranger", "Ash Walker", "Deep Diver", "World Seer", "Treasure Hunter", "Relic Seeker", "Hoarder", "Roamer", "Far Strider",
           "Discoverer", "Secret Keeper"]
    ED = {"tok": "e1", "pk": "prof-A", "sel": 1, "bad": "0", "check": "1", "reads": [], "acts": [], "null": False, "moment": False}
    EI6 = [("isle_b", 0, 3, 10, 1, 2, 30, "Brook Isle"), ("isle_a", 1, 5, 10, 0, 1, 50, "Ash Isle")] + [("isle_%d" % i_, 0, 0, 5, 0, 0, 0, "Isle %02d" % i_) for i_ in range(10)]

    def e_state():
        L = ["h|%s|%s|%s|12|%d|4|23|%s|skywynn_z1|Exploration 12 - 3,400 XP" % (ED["tok"], ED["pk"], ED["bad"], ED["sel"], ED["check"]),
             "v|Exploring pays as you go." if ED["bad"] == "0" else "v|Your exploring file could not be read - nothing is lost."]
        for i_ in range(8):
            L.append("o|%d|Card %d|Value %d|%s" % (i_, i_, i_, ("Sub line %d " % i_) * (8 if i_ == 0 else 1)))
        L += ["q|1,200 Exploration XP waiting for SkyySkills 0.4.1", "u|Chunk XP messages are hidden (/explore quiet)",
              "g|0|0|#4fd88a|1|2|Emerald Wilds", "g|1|0|#e8c25a|0|1|Howling Sands", "g|2|1|#8fcbff|1|1|Whisperfrost",
              "z|0|Zone1_Spawn|1|100|Spawn Meadow", "z|0|Zone1_Tier1|0|250|Oak Hollow", "z|1|Zone2_Tier1|0|400|Dune Sea", "z|2|Zone3_Tier1|1|500|Frost Gate"]
        for i_, n_ in enumerate(TN6):
            L.append("t|%d|%d|%d|%s|%s" % (i_, 1 if i_ < 4 else 0, 1 if i_ == ED["sel"] else 0, "#4fd88a" if i_ < 4 else "", n_))
            L.append("r|%d|Exploration %d" % (i_, 5 * (i_ + 1)))
        if ED["check"] == "1":
            for e_ in EI6:
                L.append("i|%s|%d|%d|%d|%d|%d|%d|%s" % e_)
        return "\n".join(L)

    def e_check(wf_):
        hit_ = [e_ for e_ in EI6 if e_[0] == wf_]
        if not hit_:
            return "-No checklist for that island."
        e_ = hit_[0]
        L = ["h|%s|%s|%s|%d|%d|%d|%d|%d|%d|35|%s" % (ED["tok"], ED["pk"], e_[0], e_[1], e_[2], e_[3], e_[4], e_[5], e_[6], e_[7])]
        for i_ in range(35):
            L.append("e|%d|%s|%s" % (1 if i_ < 3 else 0, "+120 XP" if i_ % 2 else "3/5", "??? Secret spot" if i_ == 5 else "Row %02d of %s" % (i_, e_[7])))
        L.append("f|Reward at 100%: +500 Exploration XP, +2,000 coins")
        return "\n".join(L)

    def f_eact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        if a_[0] in ("state", "checklist"):
            ED["reads"].append(a_)
            return e_state() if a_[0] == "state" else e_check(a_[4])
        ED["acts"].append(a_)
        if ED["null"]:
            return None
        op, tok, pk, arg = a_[0], a_[2], a_[3], a_[4]
        if op == "refresh":
            return ""
        if pk != ED["pk"]:
            return "=Your profile changed - here is this profile's exploring. Nothing changed."
        if tok != ED["tok"]:
            return "=Your exploration file changed - look again. Nothing changed."
        if ED["moment"]:
            ED["moment"] = False
            return "=One moment."
        if op == "title":
            if arg == "none":
                ED["sel"] = -1
                return "+Title removed"
            i_, id_ = arg.split("|")
            i_ = int(i_)
            if id_ != TN6[i_].lower().replace(" ", ""):
                return "=The titles changed - look again. Nothing changed."
            if i_ >= 4:
                return "-%s is locked - reach Exploration %d." % (TN6[i_], 5 * (i_ + 1))
            ED["sel"] = i_
            return "+Your title is now %s." % TN6[i_]
        return "-Unknown exploration action."
    BR.put("explore:fn:act", Fn(f_eact))
    ne_ = lambda: len(ED["acts"])
    WS, p_ = w_open("OLD6 E reopen")
    p_ = w_ev({"a": "exp"}, "OLD6 E the Explore card's button")
    cm = cmap(p_)
    K.check(int(WS.view) == 3 and only6(p_, 3) and ED["reads"][-1] == ["state", uk6, None, None, None] and txt6(cm, "EvL") == "Exploration 12 - 3,400 XP"
            and txt6(cm, "EvC") == "Titles 4 / 23" and txt6(cm, "Ek0") == "Overview" and str(WTD.ST1) in mk_of(p_, "SkyyWtabEk0") and txt6(cm, "EvKn") == "You are in skywynn_z1",
            "OLD6 E Explore = the EXPLORE VIEW (ONE section): the level line, Overview | Zones | Titles | Checklist %s" % sel_ok6(p_)[:3])
    K.check(txt6(cm, "EvO0H") == "CARD 0" and txt6(cm, "EvO0V") == "Value 0" and txt6(cm, "EvO0S").startswith("Sub line 0") and txt6(cm, "EvO0T") != "" and txt6(cm, "EvO7V") == "Value 7"
            and txt6(cm, "EvOq") == "1,200 Exploration XP waiting for SkyySkills 0.4.1" and txt6(cm, "EvOu") == "Chunk XP messages are hidden (/explore quiet)"
            and txt6(cm, "EvOv") == "Exploring pays as you go." and vis4(cm, "EvO") and not vis4(cm, "EvZ"),
            "OLD6 E OVERVIEW: the 8 cards (a long line on two), the owed / quiet / note lines")
    p_ = w_ev({"a": "ek:1"}, "OLD6 E Zones")
    cm = cmap(p_)
    K.check(vis4(cm, "EvZ") and vis4(cm, "EvZ0N0") and txt6(cm, "EvZ0N0") == "Emerald Wilds" and txt6(cm, "EvZ0V") == "1 / 2 found" and vis4(cm, "EvZ1N1")
            and txt6(cm, "EvZ1V") == "found" and txt6(cm, "EvZ2V") == "250 XP" and txt6(cm, "EvZ3N0") == "Howling Sands" and txt6(cm, "EvZ%dN0" % int(WTD.EZN)) == "Whisperfrost"
            and not vis4(cm, "EvZp"), "OLD6 E ZONES: the groups left / right, each region found or its XP")
    p_ = w_ev({"a": "ek:2"}, "OLD6 E Titles")
    cm = cmap(p_)
    K.check(vis4(cm, "EvT") and vis4(cm, "EvT1N0") and txt6(cm, "EvT1N0") == "Pathfinder   (wearing)" and vis4(cm, "EvT0N1") and vis4(cm, "EvT0U") and not vis4(cm, "EvT1U")
            and vis4(cm, "EvT5N2") and not vis4(cm, "EvT5U") and txt6(cm, "EvT5R") == "Exploration 30" and vis4(cm, "EvTn") and txt6(cm, "EvTs").startswith("Wearing: Pathfinder")
            and vis4(cm, "EvT22") and not vis4(cm, "EvT23"), "OLD6 E TITLES: wearing green, earned gold + Use, locked dim, what earns it, No title")
    p_ = w_ev({"a": "et:3", "t": str(WS.tok)}, "OLD6 E Use Wayfarer")
    K.check(ED["acts"][-1] == ["title", uk6, "e1", "prof-A", "3|wayfarer"] and cap4(p_) == "Your title is now Wayfarer." and vis4(cmap(p_), "EvT3N0"),
            "OLD6 E Use = title <drawn index>|<its id> with the read's token + profile key")
    n0_ = ne_()
    p_ = w_ev({"a": "et:5", "t": str(WS.tok)}, "OLD6 E SAFE Use on a locked title")
    K.check(ne_() == n0_ and cap4(p_) == NONE6, "OLD6 E SAFE Use not drawn = a caption, no call")
    p_ = w_ev({"a": "etn", "t": str(WS.tok)}, "OLD6 E No title")
    K.check(ED["acts"][-1][4] == "none" and cap4(p_) == "Title removed" and not vis4(cmap(p_), "EvTn"), "OLD6 E No title = title none; then hidden")
    n0_ = ne_()
    p_ = w_ev({"a": "etn", "t": str(WS.tok)}, "OLD6 E SAFE No title when none is worn")
    K.check(ne_() == n0_ and cap4(p_) == NONE6, "OLD6 E SAFE No title not drawn = a caption, no call")
    p_ = w_ev({"a": "ek:3"}, "OLD6 E Checklist")
    cm = cmap(p_)
    K.check(str(WS.eWf) == "isle_a" and ED["reads"][-1] == ["checklist", uk6, None, None, "isle_a"] and txt6(cm, "EvCi1N") == "Ash Isle  (you are here)" and txt6(cm, "EvCi1Go") == "Showing"
            and txt6(cm, "EvCrN") == "Ash Isle  (you are here)" and txt6(cm, "EvCrS") == "5 / 10 done   -   secrets 0 / 1   -   50%" and vis4(cm, "EvCe0N0")
            and txt6(cm, "EvCe0N0") == "Done  Row 00 of Ash Isle" and vis4(cm, "EvCe3N1") and txt6(cm, "EvCe5N1") == "??? Secret spot" and txt6(cm, "EvCe1V") == "+120 XP"
            and txt6(cm, "EvCrf") == "Reward at 100%: +500 Exploration XP, +2,000 coins" and txt6(cm, "EvCrpg") == "Page 1 / 2" and txt6(cm, "EvCipg") == "Page 1 / 2"
            and ("Width: %d," % (50 * int(WTD.ECRBARW) // 100)) in " ".join(app6(p_, "EvCrB")),
            "OLD6 E CHECKLIST: the island you are on picked, its rows (done green), the secret hidden, the reward line, pages %s" % sel_ok6(p_)[:3])
    p_ = w_ev({"a": "ei:0"}, "OLD6 E Show another island")
    K.check(ED["reads"][-1][4] == "isle_b" and txt6(cmap(p_), "EvCrN") == "Brook Isle", "OLD6 E Show = that island's checklist")
    p_ = w_ev({"a": "ecpg:1"}, "OLD6 E checklist page 2")
    p2_ = w_ev({"a": "eipg:1"}, "OLD6 E islands page 2")
    K.check(txt6(cmap(p_), "EvCe0N1") == "Row 30 of Brook Isle" and txt6(cmap(p2_), "EvCi0N") == "Isle 08", "OLD6 E the checklist / island pages")
    ED["check"] = "0"
    p_ = w_ev({"a": "vrf"}, "OLD6 E checklists off")
    K.check(ED["acts"][-1][0] == "refresh" and txt6(cmap(p_), "EvCrS") == "Island checklists are turned off on this server." and not vis4(cmap(p_), "EvCl"),
            "OLD6 E Refresh = explore:fn:act refresh; checklists off = said")
    ED["check"] = "1"
    ED["bad"] = "1"
    p_ = w_ev({"a": "ek:0"}, "OLD6 E a bad file")
    K.check(txt6(cmap(p_), "EvH") == "Your exploring file could not be read - nothing is lost.", "OLD6 E an unreadable exploration file = the page's note on top")
    ED["bad"] = "0"
    p_ = w_ev({"a": "ek:2"}, "OLD6 E Titles again")
    ED["moment"] = True
    p_ = w_ev({"a": "et:0", "t": str(WS.tok)}, "OLD6 E '=One moment.'")
    K.check(cap4(p_) == "One moment.", "OLD6 E the bridge's guard = the caption")
    ED["pk"] = "prof-B"
    p_ = w_ev({"a": "et:0", "t": str(WS.tok)}, "OLD6 E a profile switch")
    K.check("profile changed" in cap4(p_), "OLD6 E SAFE a profile switch = refused")
    ED["tok"] = "e2"
    p_ = w_ev({"a": "et:0", "t": str(WS.tok)}, "OLD6 E another file")
    K.check("exploration file changed" in cap4(p_), "OLD6 E SAFE the file changed = refused")
    ED["null"] = True
    p_ = w_ev({"a": "et:0", "t": str(WS.tok)}, "OLD6 E a null answer")
    K.check(cap4(p_) == str(WTD.NULLANS), "OLD6 E a null answer = said")
    ED["null"] = False
    TN6[0] = "Wanderess"
    p_ = w_ev({"a": "et:0", "t": str(WS.tok)}, "OLD6 E a renamed title")
    K.check(ED["acts"][-1][4] == "0|wanderer" and "titles changed" in cap4(p_), "OLD6 E SAFE a title renamed between read and click = the bridge's '=The titles changed'")
    TN6[0] = "Wanderer"
    K.notes.append("OLD6 E ran: explore:fn:act reads %d, acts %d" % (len(ED["reads"]), len(ED["acts"])))

    # ======== ISLAND (island:fn:act stand-in)
    ub6 = "00000000-0000-0000-0000-0000000000b1"
    ID = {"tok": "isle-A", "pk": "prof-A", "has": 1, "rank": 4, "own": 1, "bad": 0, "arm": "", "mode": 0, "limit": 5, "notify": 1, "pvp": 0, "spawn": 1,
          "reads": [], "acts": [], "refresh": 0, "null": False, "moment": False, "inv": None, "close": False, "reset": "",
          "members": [("prof-A", 4, 1, 0, "", 1, "SkyyCraftA")] + [("k%02d" % i_, 3 if i_ == 0 else 2, 1 if i_ == 1 else 0, 1 if i_ == 2 else 0, "1700000000000", 0, "Member %02d" % i_) for i_ in range(11)],
          "trusted": [("t%02d" % i_, 0, "Alt" if i_ == 0 else "", "Trusted %02d" % i_) for i_ in range(13)],
          "visitors": [(uk6, 4, 1, "SkyyCraftA"), (ub6, 0, 0, "Bravo"), ("00000000-0000-0000-0000-0000000000b2", 9, 0, "Admin")] + [("00000000-0000-0000-0000-0000000000c%d" % i_, 1, 0, "Friend %d" % i_) for i_ in range(9)],
          "bans": [("bn%02d" % i_, "Banned %02d" % i_) for i_ in range(11)],
          "perm": [1, 1, 2, 0, 1, 2, 2, 0, 2, 2, 0, 1, 1, 1]}
    MEM6 = list(ID["members"])
    FL6 = ["Place blocks", "Break blocks", "Chests and barrels", "Doors and gates", "Crafting benches", "Furnaces", "Beds", "Chairs and benches", "Crops and plants",
           "Farm animals", "Hostile mobs", "Pick up items", "Drop items", "Other blocks"]

    def i_state(arg):
        L = ["h|%d|%s|%s|%d|%d|%d|%d|4|%d|20|%d|25|%d|%d|10|%d|%d|%d|3|1|1|0|24|60|%s|%d|skyy-island-abc"
             % (ID["has"], ID["tok"], ID["pk"], ID["rank"], ID["own"], ID["bad"], len(ID["members"]), len(ID["trusted"]), len(ID["bans"]), ID["mode"], ID["limit"],
                ID["notify"], ID["pvp"], ID["spawn"], ID["arm"], 10 if ID["arm"] else 0), "n|SkyyCraftA"]
        if ID["rank"] == 4 and ID["has"]:
            L.append("r|" + ID["reset"])
        L.append("c|%d|%d|%d|%d|%d|%d|%d|%d" % (len(ID["members"]), len(ID["members"]), len(ID["trusted"]), len(ID["trusted"]), len(ID["visitors"]), len(ID["visitors"]),
                                                 len(ID["bans"]), len(ID["bans"])))
        if ID["has"]:
            for m_ in ID["members"]:
                L.append("m|%s|%d|%d|%d|%s|%d|%s" % m_)
            if ID["rank"] >= 3:
                L.append("p|Charlie (55 s)")
            for t_ in ID["trusted"]:
                L.append("t|%s|%d|%s|%s" % t_)
            L.append("d|1|containers, beds")
            for i_, n_ in enumerate(FL6):
                L.append("f|%d|flag%d|%d|%s|Hint %d" % (i_, i_, ID["perm"][i_], n_, i_))
            for v_ in ID["visitors"]:
                L.append("v|%s|%d|%d|%s" % v_)
            for b_ in ID["bans"]:
                L.append("b|%s|%s" % b_)
        if ID["inv"]:
            L.append("i|42|%s|%s|Delta|Delta" % ID["inv"])
        return "\n".join(L)

    def f_iact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        if a_[0] == "state":
            ID["reads"].append(a_)
            return i_state(a_[4])
        if a_[0] == "refresh":
            ID["refresh"] += 1
            ID["arm"] = ""
            return ""
        ID["acts"].append(a_)
        if ID["null"]:
            return None
        op, tok, pk, arg = a_[0], a_[2], a_[3], a_[4]
        if pk != ID["pk"]:
            ID["arm"] = ""
            return "=Your profile changed - here is this profile's island. Nothing changed."
        if tok != ID["tok"]:
            ID["arm"] = ""
            return "=Your island changed - look again. Nothing changed."
        if ID["moment"]:
            ID["moment"] = False
            return "=One moment."
        was = ID["arm"]
        ID["arm"] = ""
        if op in ("create", "go"):
            if ID["close"]:
                PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
            ID["has"] = 1
            return ""
        if op == "accept":
            return "+You joined Delta's island."
        if op == "decline":
            ID["inv"] = None
            return "+Invite declined."
        if op == "leave":
            if was == "leave":
                return "+You left the co-op. Your own island is your home again."
            ID["arm"] = "leave"
            return "=Click again within 10 s to leave. Your own island becomes your home again."
        if op == "disband":
            if was == "disb":
                ID["members"] = ID["members"][:1]
                return "+The co-op was disbanded."
            ID["arm"] = "disb"
            return "=Click again within 10 s to remove every co-op member (trusted players, bans and settings stay)."
        if op == "reset":
            if was == "reset2":
                return "+Your island was reset."
            ID["arm"] = "reset2" if was == "reset1" else "reset1"
            return "=Reset warning %d: everything you built is deleted." % (2 if was == "reset1" else 1)
        if op == "name":
            return "=Click Invite to co-op or Trust (build only) for %s. Enter alone does nothing." % arg if arg else "=Type a player's name, then click Invite to co-op or Trust."
        if op in ("invite", "trust"):
            return ("+Invited %s to your co-op." % arg if op == "invite" else "+%s may build here now." % arg) if arg == "Charlie" else "-Nobody called %s is online right now." % arg
        if op in ("promote", "demote"):
            return "+%s is now %s." % (arg, "an Admin" if op == "promote" else "a Member")
        if op == "kick":
            if was == "kk:" + arg:
                ID["members"] = [m_ for m_ in ID["members"] if m_[0] != arg]
                return "+Removed %s from the co-op." % arg
            ID["arm"] = "kk:" + arg
            return "=Click Sure? within 10 s to remove %s from the co-op." % arg
        if op in ("untrust", "unban"):
            return "+%s %s." % ("Untrusted" if op == "untrust" else "Unbanned", arg)
        if op == "mode":
            ID["mode"] = int(arg)
            return "+Visits: mode %s." % arg
        if op == "limit":
            ID["limit"] += int(arg)
            return "+Visitor limit %d." % ID["limit"]
        if op in ("notify", "pvp", "spawning"):
            k_ = {"notify": "notify", "pvp": "pvp", "spawning": "spawn"}[op]
            if str(ID[k_]) != arg:
                return "=That changed since you looked - look again. Nothing changed."
            ID[k_] = 1 - ID[k_]
            return "+%s %s." % (op, "on" if ID[k_] else "off")
        if op == "perm":
            code_, sh_ = arg.split("|")
            fl_, r_ = int(code_[:2]), "vtma".index(code_[2])
            if (r_ >= ID["perm"][fl_]) != (sh_ == "1"):
                return "=That changed since you looked - look again. Nothing changed."
            ID["perm"][fl_] = r_ + 1 if r_ >= ID["perm"][fl_] else r_
            return "+%s: %s." % (FL6[fl_], "changed")
        if op == "permreset":
            if was == "pdef":
                return "+Every permission is back to the server defaults."
            ID["arm"] = "pdef"
            return "=Click again within 10 s to put every permission back to the server defaults."
        if op in ("expel", "vtrust"):
            return "+%s %s." % ("Expelled" if op == "expel" else "Trusted", arg[-2:])
        if op == "ban":
            if was == "vb:" + arg:
                return "+Banned %s." % arg[-2:]
            ID["arm"] = "vb:" + arg
            return "=Click Sure? within 10 s to ban Bravo from the island."
        return "-Unknown island action."
    BR.put("island:fn:act", Fn(f_iact))
    ni_ = lambda: len(ID["acts"])
    WS, p_ = w_open("OLD6 I reopen")
    r0_ = ID["refresh"]
    p_ = w_ev({"a": "isl"}, "OLD6 I Island settings")
    cm = cmap(p_)
    K.check(int(WS.view) == 4 and only6(p_, 4) and ID["refresh"] == r0_ + 1 and ID["reads"][-1] == ["state", uk6, None, None, "200|200|200|200"]
            and txt6(cm, "IvR") == "SkyyCraftA's Island      Your role: Owner      Co-op 12 / 4      Visits: public" and txt6(cm, "Ik4") == "Island" and str(WTD.ST1) in mk_of(p_, "SkyyWtabIk0"),
            "OLD6 I Island settings = the ISLAND VIEW (ONE section): refresh first (fix isl1fix), the state read, the role line, the 5 tabs %s" % sel_ok6(p_)[:3])
    K.check(txt6(cm, "IvO1") == "Owner: SkyyCraftA   (that is you)" and txt6(cm, "IvO2") == "Co-op: 12 / 4 players      Trusted: 13      Banned: 11"
            and txt6(cm, "IvO3").startswith("Visits: Public (anyone) (limit 5)      Visitors now: 3") and txt6(cm, "IvGo") == "Go to island" and len(bind6(p_, "iv:go")) == 1
            and txt6(cm, "IvDb") == "Disband co-op (11)" and txt6(cm, "IvRs") == "Reset island" and not vis4(cm, "IvOl") and not vis4(cm, "IvOi") and "Once every 24 h." in txt6(cm, "IvOon"),
            "OLD6 I OVERVIEW (owner): the owner box, Go to island, Disband co-op (n), Reset island, no Leave, no invite")
    p_ = w_ev({"a": "iv:disb", "t": str(WS.tok)}, "OLD6 I Disband (first press)")
    K.check(ID["acts"][-1] == ["disband", uk6, "isle-A", "prof-A", None] and txt6(cmap(p_), "IvDb") == "Click again to DISBAND" and cap4(p_).startswith("Click again within 10 s"),
            "OLD6 I Disband = disband with the read's token + key; the first press = the page's question, the button armed")
    p_ = w_ev({"a": "iv:disb", "t": str(WS.tok)}, "OLD6 I Disband (the same press again)")
    K.check(cap4(p_) == "The co-op was disbanded." and not vis4(cmap(p_), "IvDb"), "OLD6 I the same press again = disbanded; no Disband left")
    for i_ in (1, 2, 3):
        p_ = w_ev({"a": "iv:reset", "t": str(WS.tok)}, "OLD6 I Reset press %d" % i_, n=1 if i_ < 3 else None)
        if i_ == 1:
            K.check(txt6(cmap(p_), "IvRs") == "Delete everything?" and "warning 1" in cap4(p_), "OLD6 I Reset press 1 = warning 1, the button armed")
        if i_ == 2:
            K.check(txt6(cmap(p_), "IvRs") == "Really? Last click" and "warning 2" in cap4(p_), "OLD6 I Reset press 2 = warning 2, the last-click word")
    K.check(ID["acts"][-1][0] == "reset" and bool(WS.closed) and PK.pm.getCustomPage() is None and int(ID["refresh"]) == r0_ + 1,
            "OLD6 I the third Reset press ('+') = the trip: the screen closed as the bridge does (no refresh over it)")
    WS, p_ = w_open("OLD6 I reopen 2")
    p_ = w_ev({"a": "isl"}, "OLD6 I Island settings again")
    ID["close"] = True
    w_ev({"a": "iv:go", "t": str(WS.tok)}, "OLD6 I Go to island", n=None)
    K.check(ID["acts"][-1][0] == "go" and bool(WS.closed) and PK.pm.getCustomPage() is None, "OLD6 I Go to island = go; the bridge closed the screen (it stays closed, no packet over it)")
    ID["close"] = False
    WS, p_ = w_open("OLD6 I reopen 3")
    p_ = w_ev({"a": "isl"}, "OLD6 I Island settings 3")
    w_ev({"a": "iv:go", "t": str(WS.tok)}, "OLD6 I Go to island (the bridge left it open)", n=None)
    K.check(bool(WS.closed) and PK.pm.getCustomPage() is None, "OLD6 I Go to island the bridge did not close = closed here (never a redraw over a trip)")
    ID["members"] = list(MEM6)
    WS, p_ = w_open("OLD6 I reopen 4")
    p_ = w_ev({"a": "isl"}, "OLD6 I Island settings 4")
    r1_ = ID["refresh"]
    p_ = w_ev({"a": "ik:1"}, "OLD6 I Members")
    cm = cmap(p_)
    K.check(ID["refresh"] == r1_ + 1 and int(WS.iSub) == 1 and vis4(cm, "IvM") and not vis4(cm, "IvO") and txt6(cm, "IvMh") == "CO-OP MEMBERS  (12 / 4)"
            and txt6(cm, "IvM0N") == "SkyyCraftA  (you)" and not vis4(cm, "IvM0P") and not vis4(cm, "IvM0K") and txt6(cm, "IvM1P") == "Demote" and txt6(cm, "IvM2P") == "Promote"
            and txt6(cm, "IvM2K") == "Kick" and "online on another profile" in txt6(cm, "IvM3S") and "since 2023-11-14" in txt6(cm, "IvM2S") and txt6(cm, "IvMpg") == "Page 1 / 2"
            and txt6(cm, "IvMn") == "Invited: Charlie (55 s)   " and vis4(cm, "IvMinv") and len([b_ for b_ in binds_of(p_) if "iv:name" in b_[2] and "SkyyWtabIvMf.Value" in b_[2]]) == 1,
            "OLD6 I MEMBERS: a tab change = refresh; the owner row (you) without buttons, Promote / Demote / Kick by role, since, another profile, pages, invited, the name box %s" % sel_ok6(p_)[:3])
    K.check(txt6(cm, "IvTh") == "TRUSTED - build only  (13 / 20)" and txt6(cm, "IvT0N") == "Trusted 00  (Alt)" and vis4(cm, "IvT0U") and txt6(cm, "IvTpg") == "Page 1 / 2",
            "OLD6 I TRUSTED: name (profile), Untrust, pages")
    p_ = w_ev({"a": "im:pro:2", "t": str(WS.tok)}, "OLD6 I Promote")
    K.check(ID["acts"][-1] == ["promote", uk6, "isle-A", "prof-A", "k01"] and cap4(p_) == "k01 is now an Admin.", "OLD6 I Promote = promote <the drawn key>")
    n0_ = ni_()
    p_ = w_ev({"a": "im:pro:0", "t": str(WS.tok)}, "OLD6 I SAFE Promote on your own row")
    p2_ = w_ev({"a": "im:dem:2", "t": str(WS.tok)}, "OLD6 I SAFE Demote on a Member row")
    K.check(ni_() == n0_ and cap4(p_) == NONE6 and cap4(p2_) == NONE6, "OLD6 I SAFE a button the drawing did not show on that row = a caption, no call")
    p_ = w_ev({"a": "im:kick:2", "t": str(WS.tok)}, "OLD6 I Kick (first press)")
    K.check(ID["acts"][-1][:5] == ["kick", uk6, "isle-A", "prof-A", "k01"] and txt6(cmap(p_), "IvM2K") == "Sure?", "OLD6 I Kick = kick <key>: the first press arms, the button says Sure?")
    p_ = w_ev({"a": "im:kick:2", "t": str(WS.tok)}, "OLD6 I Kick (again)")
    K.check(cap4(p_) == "Removed k01 from the co-op." and txt6(cmap(p_), "IvM2N") != "Member 01", "OLD6 I the same press again = removed")
    p_ = w_ev({"a": "iv:inv", "t": str(WS.tok), "@IN": "Char|lie\""}, "OLD6 I Invite")
    K.check(ID["acts"][-1] == ["invite", uk6, "isle-A", "prof-A", "Charlie"] and cap4(p_) == "Invited Charlie to your co-op." and (sval(cmap(p_), "#SkyyWtabIvMf.Value") or "") == "",
            "OLD6 I Invite to co-op = invite <the typed name, cleaned>; the box empties after it worked")
    p_ = w_ev({"a": "iv:trust", "t": str(WS.tok), "@IN": "Nobody"}, "OLD6 I Trust an unknown name")
    K.check(ID["acts"][-1][0] == "trust" and cap4(p_) == "Nobody called Nobody is online right now." and str(sval(cmap(p_), "#SkyyWtabIvMf.Value")) == "Nobody",
            "OLD6 I Trust = trust <typed>; a refusal keeps the typed name")
    p_ = w_ev({"a": "iv:name", "t": str(WS.tok), "@IN": "Dee"}, "OLD6 I Enter in the name box")
    K.check(ID["acts"][-1][0] == "name" and "Enter alone does nothing" in cap4(p_), "OLD6 I Enter = name <typed>: the bridge's note, nothing changes")
    n0_ = ni_()
    p_ = w_ev({"a": "iv:inv", "t": str(WS.tok), "@IN": "  "}, "OLD6 I Invite with no name")
    K.check(ni_() == n0_ and cap4(p_) == "Type a player's name in the box first.", "OLD6 I an empty name = a caption, no call")
    p_ = w_ev({"a": "it:un:0", "t": str(WS.tok)}, "OLD6 I Untrust")
    K.check(ID["acts"][-1][0] == "untrust" and ID["acts"][-1][4] == "t00", "OLD6 I Untrust = untrust <the drawn key>")
    p_ = w_ev({"a": "impg:1"}, "OLD6 I members page 2")
    p2_ = w_ev({"a": "itpg:1"}, "OLD6 I trusted page 2")
    K.check(txt6(cmap(p_), "IvMpg") == "Page 2 / 2" and txt6(cmap(p2_), "IvT0N") == "Trusted 12", "OLD6 I members / trusted pages")
    p_ = w_ev({"a": "ik:2"}, "OLD6 I Permissions")
    cm = cmap(p_)
    K.check(vis4(cm, "IvP") and txt6(cm, "IvP0N") == "Place blocks" and txt6(cm, "IvP0S") == "Hint 0" and txt6(cm, "IvP0c0") == "NO" and txt6(cm, "IvP0c1") == "YES"
            and txt6(cm, "IvP3c0") == "YES" and vis4(cm, "IvP0Cb") and not vis4(cm, "IvP0Ro") and vis4(cm, "IvP13") and txt6(cm, "IvPdef") == "Reset to defaults",
            "OLD6 I PERMISSIONS: the grid (YES from the row's role up), Reset to defaults")
    p_ = w_ev({"a": "ip:0:1", "t": str(WS.tok)}, "OLD6 I a grid cell")
    K.check(ID["acts"][-1] == ["perm", uk6, "isle-A", "prof-A", "00t|1"] and txt6(cmap(p_), "IvP0c1") == "NO", "OLD6 I a cell = perm <NN><role>|<the drawn YES/NO>")
    ID["perm"][2] = 0
    p_ = w_ev({"a": "ip:2:1", "t": str(WS.tok)}, "OLD6 I a stale cell")
    K.check(ID["acts"][-1][4] == "02t|0" and "That changed since you looked" in cap4(p_), "OLD6 I SAFE a stale cell = the drawn state sent, the bridge's '=' answer")
    p_ = w_ev({"a": "iv:pdef", "t": str(WS.tok)}, "OLD6 I Reset to defaults (first)")
    K.check(txt6(cmap(p_), "IvPdef") == "Click again to reset", "OLD6 I Reset to defaults arms (two presses)")
    p_ = w_ev({"a": "iv:pdef", "t": str(WS.tok)}, "OLD6 I Reset to defaults (again)")
    K.check(ID["acts"][-1][0] == "permreset" and cap4(p_) == "Every permission is back to the server defaults.", "OLD6 I the same press again = permreset")
    p_ = w_ev({"a": "ik:3"}, "OLD6 I Visitors")
    cm = cmap(p_)
    K.check(vis4(cm, "IvV") and txt6(cm, "Im0") == "Public (anyone)" and str(WTD.MS1) in mk_of(p_, "SkyyWtabIm0") and txt6(cm, "IvVlv") == "5" and txt6(cm, "IvVn") == "On"
            and txt6(cm, "IvVvh") == "ON THE ISLAND NOW  (12)" and txt6(cm, "IvV0N") == "SkyyCraftA (you)   -   Owner" and not vis4(cm, "IvV0E") and vis4(cm, "IvV1E") and vis4(cm, "IvV1T")
            and txt6(cm, "IvV1B") == "Ban" and not vis4(cm, "IvV2E") and vis4(cm, "IvV3E") and not vis4(cm, "IvV3T") and txt6(cm, "IvXh") == "BANNED  (11 / 25)" and vis4(cm, "IvX0U")
            and txt6(cm, "IvVpg") == "Page 1 / 2" and txt6(cm, "IvXpg") == "Page 1 / 2", "OLD6 I VISITORS: modes, limit, ping, the players (no buttons on you / an admin; Trust only for visitors), bans")
    p_ = w_ev({"a": "iv:mode2", "t": str(WS.tok)}, "OLD6 I mode Closed")
    p2_ = w_ev({"a": "iv:limp", "t": str(WS.tok)}, "OLD6 I limit +")
    p3_ = w_ev({"a": "iv:limm", "t": str(WS.tok)}, "OLD6 I limit -")
    K.check([(a_[0], a_[4]) for a_ in ID["acts"][-3:]] == [("mode", "2"), ("limit", "1"), ("limit", "-1")] and str(WTD.MS1) in mk_of(p_, "SkyyWtabIm2")
            and txt6(cmap(p2_), "IvVlv") == "6", "OLD6 I mode <n> / limit 1 / limit -1")
    p_ = w_ev({"a": "iv:notify", "t": str(WS.tok)}, "OLD6 I ping")
    K.check(ID["acts"][-1][:5] == ["notify", uk6, "isle-A", "prof-A", "1"] and txt6(cmap(p_), "IvVn") == "Off", "OLD6 I Visit ping = notify <the drawn 1/0>")
    p_ = w_ev({"a": "ivv:ex:1", "t": str(WS.tok)}, "OLD6 I Expel")
    p2_ = w_ev({"a": "ivv:tr:1", "t": str(WS.tok)}, "OLD6 I Trust a visitor")
    K.check([(a_[0], a_[4]) for a_ in ID["acts"][-2:]] == [("expel", ub6), ("vtrust", ub6)], "OLD6 I Expel / Trust = expel / vtrust <the drawn uuid>")
    p_ = w_ev({"a": "ivv:ban:1", "t": str(WS.tok)}, "OLD6 I Ban (first)")
    K.check(txt6(cmap(p_), "IvV1B") == "Sure?" and "ban Bravo" in cap4(p_), "OLD6 I Ban arms, the button says Sure?")
    p_ = w_ev({"a": "ivv:ban:1", "t": str(WS.tok)}, "OLD6 I Ban (again)")
    K.check(ID["acts"][-1][:5] == ["ban", uk6, "isle-A", "prof-A", ub6] and cap4(p_) == "Banned b1.", "OLD6 I the same press again = banned")
    n0_ = ni_()
    p_ = w_ev({"a": "ivv:tr:3", "t": str(WS.tok)}, "OLD6 I SAFE Trust on a trusted visitor")
    p2_ = w_ev({"a": "ivv:ex:0", "t": str(WS.tok)}, "OLD6 I SAFE Expel yourself")
    K.check(ni_() == n0_ and cap4(p_) == NONE6 and cap4(p2_) == NONE6, "OLD6 I SAFE visitor buttons not drawn = a caption, no call")
    p_ = w_ev({"a": "ib:un:0", "t": str(WS.tok)}, "OLD6 I Unban")
    K.check(ID["acts"][-1][0] == "unban" and ID["acts"][-1][4] == "bn00", "OLD6 I Unban = unban <the drawn key>")
    p_ = w_ev({"a": "ivpg:1"}, "OLD6 I visitors page 2")
    p2_ = w_ev({"a": "ixpg:1"}, "OLD6 I bans page 2")
    K.check(txt6(cmap(p_), "IvVpg") == "Page 2 / 2" and txt6(cmap(p2_), "IvX0N") == "Banned 10", "OLD6 I visitors / bans pages")
    p_ = w_ev({"a": "ik:4"}, "OLD6 I Island rules")
    cm = cmap(p_)
    K.check(vis4(cm, "IvI") and txt6(cm, "IvIpb") == "OFF" and txt6(cm, "IvIsb") == "ON" and "visitors to the hub" in txt6(cm, "IvIph"), "OLD6 I ISLAND: PvP / Mob spawning toggles")
    p_ = w_ev({"a": "iv:pvp", "t": str(WS.tok)}, "OLD6 I PvP")
    p2_ = w_ev({"a": "iv:spawn", "t": str(WS.tok)}, "OLD6 I spawning")
    K.check([(a_[0], a_[4]) for a_ in ID["acts"][-2:]] == [("pvp", "0"), ("spawning", "1")] and txt6(cmap(p2_), "IvIpb") == "ON" and txt6(cmap(p2_), "IvIsb") == "OFF",
            "OLD6 I PvP / Mob spawning = pvp / spawning <the drawn 1/0>")
    ID["pvp"] = 0
    p_ = w_ev({"a": "iv:pvp", "t": str(WS.tok)}, "OLD6 I a stale PvP")
    K.check(ID["acts"][-1][4] == "1" and "That changed since you looked" in cap4(p_) and ID["pvp"] == 0, "OLD6 I SAFE a stale toggle = the drawn state, the bridge's '='")
    ID["moment"] = True
    p_ = w_ev({"a": "iv:spawn", "t": str(WS.tok)}, "OLD6 I '=One moment.'")
    K.check(cap4(p_) == "One moment.", "OLD6 I the bridge's guard = the caption")
    ID["null"] = True
    p_ = w_ev({"a": "iv:spawn", "t": str(WS.tok)}, "OLD6 I a null answer")
    K.check(cap4(p_) == str(WTD.NULLANS), "OLD6 I a null answer (not on the world thread) = said, nothing done")
    ID["null"] = False
    ID["pk"] = "prof-B"
    p_ = w_ev({"a": "iv:spawn", "t": str(WS.tok)}, "OLD6 I a profile switch")
    K.check(ID["acts"][-1][3] == "prof-A" and "profile changed" in cap4(p_), "OLD6 I SAFE a profile switch = refused")
    ID["tok"] = "isle-B"
    p_ = w_ev({"a": "iv:spawn", "t": str(WS.tok)}, "OLD6 I another island")
    K.check(ID["acts"][-1][2] == "isle-A" and "island changed" in cap4(p_) and str(WS.iTok) == "isle-B", "OLD6 I SAFE the island changed = refused, the new token next")
    # a co-op Member: Leave (two presses = the trip), no owner actions, read-only grid
    ID.update({"rank": 2, "own": 0})
    p_ = w_ev({"a": "ik:0"}, "OLD6 I as a Member")
    cm = cmap(p_)
    K.check(txt6(cm, "IvO1") == "Owner: SkyyCraftA   - you are a co-op Member here" and not vis4(cm, "IvOo") and txt6(cm, "IvLv") == "Leave island", "OLD6 I a Member: Leave island, no owner actions")
    p_ = w_ev({"a": "ik:2"}, "OLD6 I a Member's grid")
    cm = cmap(p_)
    K.check(not vis4(cm, "IvP0Cb") and vis4(cm, "IvP0Ro") and txt6(cm, "IvP0Ro").startswith("Visitor: no      Trusted: no") and txt6(cm, "IvP0Ro").endswith("Admin: YES") and not vis4(cm, "IvPdef"), "OLD6 I a Member's grid is read-only")
    n0_ = ni_()
    p_ = w_ev({"a": "ip:0:0", "t": str(WS.tok)}, "OLD6 I SAFE a Member's forged cell")
    p2_ = w_ev({"a": "ik:1"}, "OLD6 I a Member's members")
    K.check(ni_() == n0_ and cap4(p_) == NONE6 and not vis4(cmap(p2_), "IvMi") and not vis4(cmap(p2_), "IvM1P") and not vis4(cmap(p2_), "IvT0U"),
            "OLD6 I SAFE a Member: no grid cell, no invite box, no row buttons")
    p_ = w_ev({"a": "ik:0"}, "OLD6 I Overview again")
    p_ = w_ev({"a": "iv:leave", "t": str(WS.tok)}, "OLD6 I Leave (first)")
    K.check(txt6(cmap(p_), "IvLv") == "Click again to leave", "OLD6 I Leave arms")
    w_ev({"a": "iv:leave", "t": str(WS.tok)}, "OLD6 I Leave (again)", n=None)
    K.check(ID["acts"][-1][0] == "leave" and bool(WS.closed) and PK.pm.getCustomPage() is None, "OLD6 I the same press again ('+') = the trip: the screen closed")
    # no island yet: Create my island; a live invite: Accept / Decline; a bad file
    ID.update({"rank": 4, "own": 1, "has": 0, "pk": "prof-A", "tok": "isle-A", "inv": ("1", "")})
    WS, p_ = w_open("OLD6 I reopen 5")
    p_ = w_ev({"a": "isl"}, "OLD6 I no island")
    cm = cmap(p_)
    K.check(txt6(cm, "IvO1") == "You have no island yet" and txt6(cm, "IvGo") == "Create my island" and len(bind6(p_, "iv:create")) == 1 and not bind6(p_, "iv:go")
            and txt6(cm, "IvOiq") == "Delta invited you to join Delta's island - 42 s left" and vis4(cm, "IvOy"),
            "OLD6 I no island = Create my island; the live co-op invite with Accept / Decline")
    p_ = w_ev({"a": "ik:1"}, "OLD6 I members without an island")
    K.check(vis4(cmap(p_), "IvE") and "Create your island first" in txt6(cmap(p_), "IvE") and not vis4(cmap(p_), "IvM"), "OLD6 I a tab that needs the island = said")
    p_ = w_ev({"a": "ik:0"}, "OLD6 I back to Overview")
    p_ = w_ev({"a": "iv:dec", "t": str(WS.tok)}, "OLD6 I Decline")
    K.check(ID["acts"][-1][0] == "decline" and cap4(p_) == "Invite declined." and not vis4(cmap(p_), "IvOi"), "OLD6 I Decline = decline")
    n0_ = ni_()
    p_ = w_ev({"a": "iv:acc", "t": str(WS.tok)}, "OLD6 I SAFE Accept with no invite")
    K.check(ni_() == n0_ and cap4(p_) == NONE6, "OLD6 I SAFE Accept not drawn = a caption, no call")
    ID["inv"] = ("0", "you already have co-op members")
    p_ = w_ev({"a": "vrf"}, "OLD6 I an invite you cannot accept")
    K.check(not vis4(cmap(p_), "IvOy") and "can't accept: you already have co-op members" in txt6(cmap(p_), "IvOis"), "OLD6 I an invite you cannot accept = why, no Accept")
    ID["inv"] = ("1", "")
    p_ = w_ev({"a": "vrf"}, "OLD6 I a new invite")
    p_ = w_ev({"a": "iv:acc", "t": str(WS.tok)}, "OLD6 I Accept")
    K.check(ID["acts"][-1][0] == "accept" and cap4(p_) == "You joined Delta's island.", "OLD6 I Accept = accept")
    ID["inv"] = None
    ID.update({"own": 0})
    p_ = w_ev({"a": "vrf"}, "OLD6 I a co-op island that is not there")
    K.check(txt6(cmap(p_), "IvO2").startswith("The island you are a co-op member of is not available") and not vis4(cmap(p_), "IvOg"), "OLD6 I has 0 + own 0 = not available, nothing to press")
    ID.update({"own": 1})
    p_ = w_ev({"a": "vrf"}, "OLD6 I Create")
    w_ev({"a": "iv:create", "t": str(WS.tok)}, "OLD6 I Create my island", n=None)
    K.check(ID["acts"][-1][0] == "create" and bool(WS.closed) and PK.pm.getCustomPage() is None, "OLD6 I Create my island = create; the screen closed")
    ID.update({"bad": 1})
    WS, p_ = w_open("OLD6 I reopen 6")
    p_ = w_ev({"a": "isl"}, "OLD6 I a bad island file")
    K.check(vis4(cmap(p_), "IvE") and "can't be read right now" in txt6(cmap(p_), "IvE") and not vis4(cmap(p_), "IvO"), "OLD6 I an unreadable island file = the page's line only")
    ID.update({"bad": 0})
    r2_ = ID["refresh"]
    p_ = w_ev({"a": "vw:3"}, "OLD6 I leave the island view")
    K.check(ID["refresh"] == r2_ + 1 and int(WS.view) == 3, "OLD6 I leaving the island view = refresh (the bridge's arm dropped)")
    p_ = w_ev({"a": "vw:4"}, "OLD6 I the island view again")
    r3_ = ID["refresh"]
    WS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(ID["refresh"] == r3_ + 1 and r3_ == r2_ + 2 and bool(WS.closed), "OLD6 I opening the view = refresh; closing the screen = refresh (fix isl1fix)")
    K.notes.append("OLD6 I ran: island:fn:act reads %d, acts %d, refresh %d" % (len(ID["reads"]), len(ID["acts"]), ID["refresh"]))
    for k_ in ("quest:fn:act", "coll:fn:act", "explore:fn:act", "island:fn:act"):
        BR.remove(k_)
    E.pump(PK)
'''
EXPECT_BODY = '''    "WorldTab": ["+f cAllow", "+f cBuy", "+f cCat", "+f cId", "+f cIds", "+f cKc", "+f cLast", "+f cOk", "+f cPage", "+f cPages", "+f cPk", "+f cRPage",
                "+f cRPages", "+f cRec", "+f cSeen", "+f cTok", "+f cWant", "+f calls", "+f eAllow", "+f eCPage", "+f eCPages", "+f eIPage", "+f eIPages",
                "+f eIs", "+f eLast", "+f eOk", "+f ePk", "+f eSub", "+f eTPage", "+f eTPages", "+f eTi", "+f eTok", "+f eWf", "+f eZPage", "+f eZPages",
                "+f iAllow", "+f iBk", "+f iKeepN", "+f iLast", "+f iMPage", "+f iMPages", "+f iMb", "+f iMk", "+f iOk", "+f iPf", "+f iPk", "+f iPm",
                "+f iSeen", "+f iShowN", "+f iShowP", "+f iShowS", "+f iSub", "+f iTPage", "+f iTPages", "+f iTk", "+f iTok", "+f iVPage", "+f iVPages",
                "+f iVb", "+f iVu", "+f iXPage", "+f iXPages", "+f irefs", "+f qAllow", "+f qBtn", "+f qHideOp", "+f qLPage", "+f qLPages", "+f qLast",
                "+f qLine", "+f qLn", "+f qOk", "+f qPage", "+f qPages", "+f qPk", "+f qSkS", "+f qSub", "+f qTk", "+f qTok", "+f qTrArg", "+f view",
                "+m actView", "+m allowed", "+m ansT", "+m cDo", "+m clampPage", "+m cut", "+m cvHide", "+m dateOf", "+m durS", "+m eDo", "+m evCheck",
                "+m evHide", "+m evTitles", "+m evZones", "+m fillBar", "+m fillCv", "+m fillCvD", "+m fillEv", "+m fillIv", "+m fillQv", "+m goView",
                "+m iDo", "+m iRefresh", "+m ivHide", "+m ivMembers", "+m ivOverview", "+m ivPanels", "+m ivPerms", "+m ivRules", "+m ivVisitors",
                "+m nameClean", "+m navView", "+m oldT", "+m openAt", "+m pagesOf", "+m pick", "+m qDo", "+m qvHide", "+m roleN", "+m roman", "+m step",
                "+m titleId", "+m two", "+m tx", "+m vRefresh", "+m viewOf", "+m vtabs", "+m wact", "~c ", "~m build", "~m finish", "~m handleDataEvent"],
    "WorldTabData": ["+f CCBARW", "+f CCN", "+f CDBARW", "+f CKN", "+f CRN", "+f CSTATE", "+f CTN", "+f CVCAP", "+f CVFAIL", "+f CVOFF", "+f CVOLD", "+f ECIBARW",
                    "+f ECIN", "+f ECRBARW", "+f ECRN", "+f ESUB", "+f ETN", "+f EVCAP", "+f EVFAIL", "+f EVOFF", "+f EVOLD", "+f EZN", "+f IMN", "+f IMODE",
                    "+f IPN", "+f ISUB", "+f ITN", "+f IVCAP", "+f IVFAIL", "+f IVN", "+f IVOFF", "+f IVOLD", "+f IVREAD", "+f IXN", "+f LS", "+f MODE",
                    "+f MS0", "+f MS1", "+f NONE", "+f NULLANS", "+f QBARW", "+f QLBARW", "+f QLN", "+f QSTATE", "+f QTN", "+f QVCAP", "+f QVFAIL", "+f QVOFF",
                    "+f QVOLD", "+f ST0", "+f ST1", "+f TAB", "~<clinit>"],
    "InvPage": ["+m worldView", "~m handleDataEvent", "~m nowGo"],
    "SkillPage": ["+m worldAt", "~m handleDataEvent"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
# ======================================================================= the HARNESS (every 0.3.73 check runs again on the 0.3.74 jar, plus OLD6)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.73 (old menu follow-up - the Guild + Auction House views; tools/menu_0_3_73_patch.py, round oldmenu5).''',
      '''"""Harness for SkyyMenu 0.3.74 (old menu follow-up - the World tab's Quests / Collections / Explore / Island views; tools/menu_0_3_74_patch.py,
round oldmenu6). GENERATED by tools/menu_0_3_74_patch.py from the 0.3.73 harness (edit the patch, not this file): every 0.3.73 check runs again
on the 0.3.74 jar (TAB4: Island settings / Explore / Quest log / Collections open the views - still ONE packet; OLD2..OLD5's ratchets = 'stays
gone'), plus
  OLD6 STATIC   the ratchet: OLD_LEFT lost world:quests + world:explore + world:island + character:collections; no old-page link left; the views
                call the four bridges with the read's token + profile key and the drawn states; the build asserts the views fit, their run-time
                markup is proven, each binding names its own section; the budget = the frame + the biggest section
       FALL     each view with its bridge missing (not on this server) / an older mod (its hub tab) = said, ONE section, no old page
       Q        (quest:fn:act stand-in) the lines in order + pages, the picked line, Open / Done, task rows (state colours, bar, where, reward,
                hint), Claim (claim1), Skip / Unskip (the drawn state; a stale one = the bridge's '='), Track (the drawn state), Claim all, Hide /
                Show tutorial, a locked line (how to start, no Track), the daily line, forged / old-drawing clicks refused, '=One moment.',
                profile switch, reload, null answer, not loaded, bad read, forged on the cards / home buttons in a view; the inventory's quest
                button + Right now row = the quests view
       C        (coll:fn:act stand-in) the codex card = Combat, the 4 category cards, cards + pages, detail (tiers DONE / NEW / BOUGHT / NEXT /
                LOCKED, seen once, the Buy offer), Buy two presses (the drawn tier + price, a double click once, a changed offer refused), no offer
                = why, Craft (+ said / the crafting page replaces the screen), forged Buy / Craft, pages, '=', profile, reload, null; the skill
                page's Collections = that skill's category
       E        (explore:fn:act stand-in) overview cards + lines, zones by side, titles (wearing / earned / locked, Use = index|id, No title),
                checklists (the island you are on, Show, rows, the secret, reward, pages), checklists off, a bad file, '=', profile, file, null,
                a renamed title
       I        (island:fn:act stand-in) refresh on open / tab change / leaving the view / close; the role line; OVERVIEW (Disband 2 presses,
                Reset 3 presses = the trip closes the screen, Go to island closed by the bridge or here), MEMBERS (rows by role, Promote, forged
                buttons, Kick 2 presses, Invite / Trust typed + cleaned, Enter note, empty name, Untrust, pages), PERMISSIONS (cells with the
                drawn YES/NO, a stale cell, Reset to defaults 2 presses), VISITORS (mode, limit, ping, Expel / Trust / Ban 2 presses, forged,
                Unban, pages), ISLAND (PvP / spawning, a stale toggle), '=', null, profile, island changed, a Member (Leave 2 presses = trip,
                read-only grid, no buttons), no island (Create = trip), invite Accept / Decline / cannot accept, not available, a bad file
       every new packet: every b.set / append / binding names an element drawn in that packet (the frame + ONE section)
The 0.3.73 harness text follows:
Harness for SkyyMenu 0.3.73 (old menu follow-up - the Guild + Auction House views; tools/menu_0_3_73_patch.py, round oldmenu5).''')
T.rep('VERSION = "0.3.73"\nJAR', 'VERSION = "0.3.74"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.72.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.73.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.72.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.73.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_73_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_74_patch.py")')
T.rep('"scratch", "oldmenu5", "menu"', '"scratch", "oldmenu6", "menu"')
T.rep('ADDED = []   # 0.3.73: no new class\n', 'ADDED = []   # 0.3.74: no new class\n')
EXPECT_74 = '''EXPECT = {   # 0.3.74: the World tab's Quests / Collections / Explore / Island views, the skill page's + the inventory's openers, the version strings
@@EXPECT@@
}
'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.73:', 'if "--expect-dump" in sys.argv:'), EXPECT_74.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.73"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.74"') == 1, "S VERSION")
''' + HARNESS_OLD6_STATIC.rstrip("\n"))
# OLD5's ratchet compared 0.3.73 with 0.3.72: against 0.3.73 it is OLD6's (above) - its two rows stay gone
T.rep('''    K.check(lefto_ - left2_ == set([("social", "guild"), ("market", "auctions")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 2,
            "OLD5 RATCHET OLD_LEFT lost social:guild + market:auctions, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(not (left2_ & set([("social", "guild"), ("market", "auctions")])), "OLD5 RATCHET (0.3.74: vs 0.3.73) social:guild + market:auctions stay gone")''')
T.rep('''    K.check(not (left2_ & set([("market", "bazaar"), ("market", "merchants")])), "OLD4 RATCHET (0.3.73: vs 0.3.72) market:bazaar + market:merchants stay gone")''',
      '''    K.check(not (left2_ & set([("market", "bazaar"), ("market", "merchants")])), "OLD4 RATCHET (0.3.74: vs 0.3.73) market:bazaar + market:merchants stay gone")''')
T.rep('''            "OLD3 RATCHET (0.3.73: vs 0.3.72) social:players + character:stats + character:profiles + social:party stay gone")''',
      '''            "OLD3 RATCHET (0.3.74: vs 0.3.73) social:players + character:stats + character:profiles + social:party stay gone")''')
T.rep('''    K.check(("market", "auctions") in ops_o_ and ("settings", "mods") not in left2_ and ("character", "pets") not in left2_,
            "OLD2 RATCHET (0.3.73: vs 0.3.72) settings:mods + character:pets stay gone; 0.3.72's opener links were tracked (0.3.73: gone, OLD5)")''',
      '''    K.check(not ops_o_ and ("settings", "mods") not in left2_ and ("character", "pets") not in left2_,
            "OLD2 RATCHET (0.3.74: vs 0.3.73) settings:mods + character:pets stay gone; no opener link left since 0.3.73 (OLD5)")''')
# TAB4: the home buttons open the views now (still ONE packet each); then OLD6
T.rep('''    # links to the old pages (each ONE packet)
    for a_, what in (("full", "Full page"), ("isl", "Island settings"), ("exp", "Explore page"), ("qlog", "Quest log"), ("coll", "Collections")):''',
      '''    # links (each ONE packet): Full page = the old Teleport page (OLD_LEFT world:teleport); 0.3.74: the rest open this screen's views
    for a_, what in (("full", "Full page"), ("isl", "Island settings (0.3.74: the island view)"), ("exp", "Explore (0.3.74: the explore view)"),
                     ("qlog", "Quest log (0.3.74: the quests view)"), ("coll", "Collections (0.3.74: the collections view)")):''')
T.rep('''    # TABS
    WS, p_ = w_open("TAB4 reopen for tabs")''', HARNESS_OLD6.rstrip("\n") + '''
    # TABS
    WS, p_ = w_open("TAB4 reopen for tabs")''')
if T.dst:
    T.finish()
