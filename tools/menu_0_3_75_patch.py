"""Derive SkyyMenu/build_skyymenu_0.3.75.py + SkyyMenu/test_skyymenu_0.3.75.py from the SET pin SkyyMenu 0.3.74 (generated - never re-run
its patch). Run:  python tools/menu_0_3_75_patch.py   then   python SkyyMenu/build_skyymenu_0.3.75.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.75.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs no other mod change: the Travel view reads the same bridges / engine calls as the old Teleport
page (island:fn:homes, essentials:fn:homes / warps, island:fn:gohome, essentials:fn:gohome, /island, /hub, the engine warps + spawn point)
and SkyyMenu's own saved Teleport order (MenuLayout part 1).

0.3.75 (2026-11-24, round oldmenu7) = OLD MENU FOLLOW-UP: THE WORLD TAB'S TRAVEL VIEW (the old World > Teleport page). Skyy's words
(docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu
compleatly, so instead of adding things like the full tree button, just build it all into the new system and remove the old "Full tree"";
2026-11-24 "keep building". The World screen's TRAVEL list (0.3.62) already had Your island / island homes / homes / Hub / every warp (icons,
locked ones greyed, filters, pages, Go). What only the old page could do, now the TRAVEL VIEW (section T; the sub-tab row World | Quests |
Collections | Explore | Island | Travel, no back button; the home Travel card's 'Travel' button opens it):
  YOUR TRAVEL ORDER: the player's own 5 x 5 Teleport grid (MenuLayout part 1, the SAME saved file the old page edits - one order, two
      screens), My Island | Hub | Spawn by default, then the places nobody pinned (island homes, homes, warps A-Z) in the free slots of rows 4
      + 5 with < > pages (the old page's auto tiles), each a card: icon, name, where, Go (a locked warp / a missing command: greyed, no Go).
  SPAWN: the main world's spawn point - the old page's engine path (ISpawnProvider.getSpawnPointAsync, never waited for on the world thread:
      WorldSpawn hops to the player's world thread -> WorldTab.spawnResolved -> the Teleport component + the /tp back history line).
  ARRANGE (the old page's Arrange): Pick up a card, then Move here / Swap here on its new slot (an auto card is pinned where it is first),
      Put back cancels, Remove takes it off, an empty slot's + Add lists every place not in the order (25 a page) and Add puts it there; Reset
      (two presses), admins Set default / Clear default (two presses, the admin node re-checked on the press); Done. Saved at once per account
      (MenuLayout.put / saveDefault / clearDefault - the old page's calls). An unreadable layout file is never changed (the old EDIT_WAIT).
  NEVER A VALUE THE PLAYER DID NOT SEE: every card button acts on the drawn card (its key and the action its drawing showed); every save first
      checks the saved order is still the drawn one ("Your Travel order changed - here it is again. Nothing moved."); Reset / Set default /
      Clear default arm on the first press (the caption asks, the button says "Click again ...") and run on the same press again; any other
      press drops the arm. A forged button = "That button is not on this page - nothing changed", no call. Page token on every press
      (an older drawing = "The page changed", nothing runs); the profile check as the rest of the screen.
  THE OLD LINKS: the top bar's 'Full page' (the old Teleport page) is gone; the World > Teleport hub tab (other mods' tab strips, MenuHubOpen
      "teleport") opens this Travel view while the old menu is OFF (Server Setup menu.oldMenu; ON = the old page as before - the old menu
      stays one piece). SkyyMenu has no /teleport alias (vanilla /teleport is the engine's own tp command, untouched); /travel = the World
      screen as before.
New: class WorldSpawn (the spawn point's hop to the world thread); no command / system / picture / lang key / setting / saved data format.
OLD_LEFT: world:teleport out (7 -> 6).
ROLLBACK to 0.3.74: safe alone (the Teleport order is the same file, nothing new saved; the 'Full page' link comes back).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.74.py"), os.path.join(MOD, "build_skyymenu_0.3.75.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.74.py"), os.path.join(MOD, "test_skyymenu_0.3.75.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.74"\n') and P.has("OLD_LEFT = sorted(set([") and P.has('WT + "Qv"') and not P.has('WT + "Gv"'), "not the generated SkyyMenu 0.3.74 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.74: OLD MENU FOLLOW-UP - THE WORLD TAB'S VIEWS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.75: OLD MENU FOLLOW-UP - THE WORLD TAB'S TRAVEL VIEW (the old World > Teleport page): your Travel order (the saved Teleport grid, the same
       file), Spawn (the engine's async spawn point - WorldSpawn), the auto places with pages, Arrange (Pick up / Move here / Swap here / Put back
       / Remove / + Add / Reset / admins Set default + Clear default, two presses where the old page asked); the top bar's Full page is gone; the
       World > Teleport hub tab = the Travel view while the old menu is off; OLD_LEFT lost world:teleport (notes: tools/menu_0_3_75_patch.py).
       CHECKED: SkyyMenu/test_skyymenu_0.3.75.py.
0.3.74: OLD MENU FOLLOW-UP - THE WORLD TAB'S VIEWS''')
P.rep('VERSION = "0.3.74"\n', 'VERSION = "0.3.75"\n')

# ======================================================================= the HOME cards: no Full page; the Travel card's button opens the view
P.rep('''    "tfoot": "Spawn and your teleport row: Full page.",''', '''    "tfoot": "Spawn, your own order and Arrange:",   # 0.3.75: the Travel view''')
P.rep('''    # ---- the top bar: the same 7 tabs (World selected), Full page, coins, the X
    top = WT + "Top"
    ap.append(iv_bar(G_, "#" + WT, top))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (WT, i), lb, "tabSelected" if i == 4 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(WT + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))''',
      '''    # ---- the top bar: the same 7 tabs (World selected), coins, the X (0.3.75: no Full page - the Travel view is the old Teleport page)
    top = WT + "Top"
    ap.append(iv_bar(G_, "#" + WT, top))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (WT, i), lb, "tabSelected" if i == 4 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % (sp + 128)))   # 0.3.75: + the Full page button's 120 + 8 px''')
P.rep('''    ap.append(("#" + pr_, lab(WT + "Tf", "", 12, "dim", w=WT_LI - 36 - 4 - 110 - 36 - 12, h=26, halign="End")))
    ap.sets.append((WT + "Tf", "Text", WT_TXT["tfoot"]))''', '''    ap.append(("#" + pr_, lab(WT + "Tf", "", 12, "dim", w=WT_LI - 36 - 4 - 110 - 36 - 12 - 158, h=26, halign="End")))
    ap.sets.append((WT + "Tf", "Text", WT_TXT["tfoot"]))
    ap.append(("#" + pr_, G_.glass_button(WT + "Tgo", "Travel", "secondary", w=150, h=26, size=13, anchor={"left": 8})))   # 0.3.75: the Travel view''')
P.rep('''    binds = [("#%sT%d" % (WT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + WT + "Close", "close"), ("#" + WT + "Full", "full"),''',
      '''    binds = [("#%sT%d" % (WT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + WT + "Close", "close"), ("#" + WT + "Tgo", "trv"),''')
P.rep('''WT_DYN = (["Coins", "Close", "Full", "Cap", "Fl", "Lt", "Pp", "Pg", "Pn", "Tf", "Qc",''', '''WT_DYN = (["Coins", "Close", "Tgo", "Cap", "Fl", "Lt", "Pp", "Pg", "Pn", "Tf", "Qc",''')
P.rep('''          + ["%s%s" % (v_, x_) for v_ in ("Qv", "Cv", "Ev", "Iv") for x_ in ("H", "C", "Rf", "Vt0", "Vt1", "Vt2", "Vt3", "Vt4")]''',
      '''          + ["%s%s" % (v_, x_) for v_ in ("Qv", "Cv", "Ev", "Iv", "Gv") for x_ in ("H", "C", "Rf", "Vt0", "Vt1", "Vt2", "Vt3", "Vt4", "Vt5")]
          # 0.3.75 (oldmenu7): the Travel view
          + ["GvT%d%s" % (k_, x_) for k_ in range(GV_N) for x_ in ("", "I", "X", "N", "S", "W", "B")] + ["Gvb", "GvF", "GvP", "GvPp", "GvPg", "GvPn"]
          + ["Gv" + i_ for i_, _t, _s, _w in GV_FOOT]''')

# ======================================================================= the sub-tab row gets Travel; the TRAVEL VIEW (section T)
P.rep('''WV_SBW, WV_RFW = 150, 120                                   # a sub-tab, Refresh
WV_SUBS = ["World", "Quests", "Collections", "Explore", "Island"]''', '''WV_SBW, WV_RFW = 128, 120                                   # a sub-tab, Refresh (0.3.75: 150 -> 128 for the sixth sub-tab)
WV_SUBS = ["World", "Quests", "Collections", "Explore", "Island", "Travel"]   # 0.3.75: + Travel (the old World > Teleport page)''')
P.rep('''    "nullans": "That could not run here - nothing changed.",
}''', '''    "nullans": "That could not run here - nothing changed.",
    # 0.3.75 (oldmenu7): the Travel view
    "gvcap": "Go travels there. Arrange moves your places: Pick up, then Move here. World on top goes back.",
    "gvhead": "Your Travel order - Go takes you there. Arrange moves, adds and removes places (saved for you, the same order as before).",
    "gvedit": "ARRANGE: Pick up a place, then Move here or Swap here on the slot it goes to. An empty slot: + Add. Done when finished.",
    "gvadd": "Pick what goes in the empty slot - Add puts it there. Cancel goes back.",
    "gvnone": "Nothing left to add - every place is in your Travel order already. Cancel goes back.",
    "gvnowarp": "No warps have been set on this server yet - an admin adds them on /warpadmin (Add warp here).",
    "gvload": "The warp list is still loading - press Refresh in a moment.",
    "gvstale": "Your Travel order changed - here it is again. Nothing moved.",
}''')
P.rep('''for _k in ("qvcap", "cvcap", "evcap", "ivcap"):
    assert SUI.text_width(WV_TXT[_k], 14) <= IV_IW - 420, ("0.3.74: a caption fits the hint row", _k)''',
      '''for _k in ("qvcap", "cvcap", "evcap", "ivcap", "gvcap"):
    assert SUI.text_width(WV_TXT[_k], 14) <= IV_IW - 420, ("0.3.74: a caption fits the hint row", _k)
for _k in ("gvhead", "gvedit", "gvadd", "gvnone", "gvnowarp", "gvload", "gvstale"):
    assert SUI.text_width(WV_TXT[_k], 13) <= WV_VI, ("0.3.75: a travel head line fits", _k)
# 0.3.75 (oldmenu7): THE TRAVEL VIEW - the old Teleport page's 5 x 5 grid as cards (icon, name, where, one button), the foot row
GV_C, GV_R = 5, 5
GV_N = GV_C * GV_R
assert GV_N == HG_N and GV_C == HG_COLS, "0.3.75: the Travel view's cards are the saved Teleport grid's 25 slots"
GV_W = (WV_VI - (GV_C - 1) * 10) // GV_C                    # a card (299)
GV_H = 130
GV_BW = 130
GV_TW = GV_W - 16 - 44 - 8                                  # a card's text column (231)
GV_FOOT = [("Ar", "Arrange", "primary", 150), ("Rm", "Remove", "secondary", 140), ("Rs", "Reset", "secondary", 190),
           ("Sd", "Set default", "secondary", 210), ("Cd", "Clear default", "secondary", 210), ("Dn", "Done", "primary", 140),
           ("Cn", "Cancel", "secondary", 140)]
for _l, _w in (("Go", GV_BW), ("Pick up", GV_BW), ("Put back", GV_BW), ("Move here", GV_BW), ("Swap here", GV_BW), ("+ Add", GV_BW), ("Add", GV_BW),
               ("Arrange", 150), ("Remove", 140), ("Reset", 190), ("Click again to reset", 190), ("Set default", 210), ("Click again to set", 210),
               ("Clear default", 210), ("Click again to clear", 210), ("Done", 140), ("Cancel", 140), ("Travel", 150)):
    assert SUI.text_width(_l, 13, bold=True) <= _w - 12, ("0.3.75: a travel button fits", _l)
assert GV_BW <= GV_TW and SUI.text_width("[Moving] Island home Farmhous", 14, bold=True) <= GV_TW \\
    and SUI.text_width("Locked - you have not unlocked this warp yet", 11) <= GV_TW, "0.3.75: a card's text column (names cut at 30, lines at 44)"''')
P.rep('''WV_RUNTIME = {"Q": 2 + QL_N + QT_N, "C": CC_N + 1, "E": len(EV_SUB) + EC_IN + 1, "I": len(IS_SUB) + len(IS_MODE)}   # tabs + bar fills / mode buttons''',
      '''WV_RUNTIME = {"Q": 2 + QL_N + QT_N, "C": CC_N + 1, "E": len(EV_SUB) + EC_IN + 1, "I": len(IS_SUB) + len(IS_MODE),   # tabs + bar fills / mode buttons
              "T": 0}   # 0.3.75: the Travel view appends nothing at run time (texts, visibility and bindings only)''')
P.rep('''    out.append(("I", ap, bi + [("#" + WT + "IvMpp", "impg:-1"), ("#" + WT + "IvMpn", "impg:1"), ("#" + WT + "IvTpp", "itpg:-1"), ("#" + WT + "IvTpn", "itpg:1"),
                               ("#" + WT + "IvVpp", "ivpg:-1"), ("#" + WT + "IvVpn", "ivpg:1"), ("#" + WT + "IvXpp", "ixpg:-1"), ("#" + WT + "IvXpn", "ixpg:1")]))
    return out''', '''    out.append(("I", ap, bi + [("#" + WT + "IvMpp", "impg:-1"), ("#" + WT + "IvMpn", "impg:1"), ("#" + WT + "IvTpp", "itpg:-1"), ("#" + WT + "IvTpn", "itpg:1"),
                               ("#" + WT + "IvVpp", "ivpg:-1"), ("#" + WT + "IvVpn", "ivpg:1"), ("#" + WT + "IvXpp", "ixpg:-1"), ("#" + WT + "IvXpn", "ixpg:1")]))
    # ======== T: THE TRAVEL VIEW (0.3.75, oldmenu7: the old World > Teleport page - your Travel order, Spawn, Arrange). The card buttons and
    # the foot buttons are bound at run time (they carry the page token); the pager is navigation (no token)
    ap = SUI.Appends()
    gv = WT + "Gv"
    ap.append(("#" + win, G_.glass_group(gv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bt = vhead(ap, gv, "Gv", "TRAVEL", 5)
    gb = WT + "Gvb"
    ap.append(("#" + gv, G_.glass_group(gb, WV_VI, GV_R * (GV_H + 6) - 6, layout="Top", anchor={"top": 6})))
    for r_ in range(GV_R):
        rw = "%sGvr%d" % (WT, r_)
        ap.append(("#" + gb, G_.glass_group(rw, WV_VI, GV_H, layout="Left", anchor={"top": 6} if r_ > 0 else None)))
        for c_ in range(GV_C):
            t_ = "%sGvT%d" % (WT, r_ * GV_C + c_)
            ap.append(("#" + rw, G_.glass_group(t_, GV_W, GV_H, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"right": 10} if c_ < GV_C - 1 else None)))
            ap.append(("#" + t_, G_.glass_grid(t_ + "I", 1, 1, drag=False, slot=44, icon=34, anchor={"top": (GV_H - 44) // 2})))
            x_ = t_ + "X"
            ap.append(("#" + t_, G_.glass_group(x_, GV_TW, GV_H, layout="Top", anchor={"left": 8})))
            ap.append(("#" + x_, lab(t_ + "N", "", 14, "row", bold=True, w=GV_TW, h=22, anchor={"top": 10})))
            ap.append(("#" + x_, lab(t_ + "S", "", 11, "dim", w=GV_TW, h=16)))
            ap.append(("#" + x_, lab(t_ + "W", "", 11, "text", w=GV_TW, h=16)))
            ap.append(("#" + x_, G_.glass_button(t_ + "B", "Go", "primary", w=GV_BW, h=30, size=13, anchor={"top": 8})))
    assert 10 + 22 + 16 + 16 + 8 + 30 <= GV_H and 16 + 44 + 8 + GV_TW <= GV_W and GV_C * GV_W + (GV_C - 1) * 10 <= WV_VI, "0.3.75: a travel card fits"
    gf = WT + "GvF"
    ap.append(("#" + gv, G_.glass_group(gf, WV_VI, 40, layout="Left", anchor={"top": 8})))
    pagerow(ap, gf, "GvP", 200, {"top": 6})
    for i_, t_, s_, w_ in GV_FOOT:
        ap.append(("#" + gf, G_.glass_button(WT + "Gv" + i_, t_, s_, w=w_, h=36, size=13, anchor={"left": 8, "top": 2})))
    assert 200 + sum(w_ + 8 for _i, _t, _s, w_ in GV_FOOT) <= WV_VI, "0.3.75: the travel foot row fits"
    assert 6 + GV_R * (GV_H + 6) - 6 + 8 + 40 <= WV_BH, "0.3.75: the travel view fits"
    out.append(("T", ap, bt + [("#" + WT + "GvPp", "gpg:-1"), ("#" + WT + "GvPn", "gpg:1")]))
    return out''')
P.rep('''WT_SHELL_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] for _s in "HQCEI")
WT_RUNTIME_MAX = max(_wt_rt.values())
WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEI")
print("0.3.74 world sections (elements, + at run time): frame %d, %s" % (_wt_by["0"], ", ".join("%s %d + %d" % (_s, _wt_by[_s], _wt_rt[_s]) for _s in "HQCEI")))''',
      '''WT_SHELL_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] for _s in "HQCEIT")
WT_RUNTIME_MAX = max(_wt_rt.values())
WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEIT")   # 0.3.75: + T, the Travel view
print("0.3.75 world sections (elements, + at run time): frame %d, %s" % (_wt_by["0"], ", ".join("%s %d + %d" % (_s, _wt_by[_s], _wt_rt[_s]) for _s in "HQCEIT")))''')

# ======================================================================= the data + the fields
P.rep('''for _k in sorted(WV_TXT):
    F(wtd, "public static final String %s = %s;" % (_k.upper(), jstr(WV_TXT[_k])))
''', '''for _k in sorted(WV_TXT):
    F(wtd, "public static final String %s = %s;" % (_k.upper(), jstr(WV_TXT[_k])))
F(wtd, "public static final int GN = %d;" % GV_N)   # 0.3.75: the Travel view's cards (= MenuData.HG_N)
''')
P.rep('''           "public String iAllow;", "public String iLast;", "public String iKeepN;", "public String iShowN;", "public String iShowP;", "public String iShowS;"):
    F(wtab, _f)''', '''           "public String iAllow;", "public String iLast;", "public String iKeepN;", "public String iShowN;", "public String iShowP;", "public String iShowS;",
           # 0.3.75 (oldmenu7): the Travel view - what its drawing showed (the grid, each card's key / go key / action), the modes, the armed press
           "public String[] gKey;", "public String[] gGoK;", "public int[] gAct;", "public String[] gDrawn;", "public String gAllow;", "public boolean gEdit;",
           "public int gSel;", "public int gAddAt;", "public int gPage;", "public int gPages;", "public int gAPage;", "public String gArm;", "public boolean gAdmin;",
           "public volatile boolean spawnWait;"):
    F(wtab, _f)''')
P.rep('''  this.view = 0;           // 0.3.74 (oldmenu6)
''', '''  this.view = 0;           // 0.3.74 (oldmenu6)
  this.gKey = new String[0];   // 0.3.75 (oldmenu7): the Travel view
  this.gGoK = new String[0];
  this.gAct = new int[0];
  this.gDrawn = null;
  this.gAllow = "|";
  this.gEdit = false;
  this.gSel = -1;
  this.gAddAt = -1;
  this.gPage = 0;
  this.gPages = 1;
  this.gAPage = 0;
  this.gArm = null;
  this.gAdmin = false;
  this.spawnWait = false;
''')
P.rep('''wtab = mk("WorldTab", T["PAGE"])    # 0.3.62: THE WORLD TAB = ONE SCREEN
''', '''wtab = mk("WorldTab", T["PAGE"])    # 0.3.62: THE WORLD TAB = ONE SCREEN
wsp  = mk("WorldSpawn")      # 0.3.75: the Travel view's Spawn - the async spawn point -> the player's world thread -> WorldTab.spawnResolved
''')
P.rep('''ptd, ptab, mtd, mtab, wtd, wtab, scd, stab, sgd, sgt, pl)''', '''ptd, ptab, mtd, mtab, wtd, wtab, wsp, scd, stab, sgd, sgt, pl)''')
P.rep('''  pg.view = view < 0 || view > 4 ? 0 : view;''', '''  pg.view = view < 0 || view > 5 ? 0 : view;   // 0.3.75: 5 = the Travel view''')
P.rep('''# 0.3.74 (oldmenu6): the world screen opened on a view (1 quests, 2 collections with an optional category name, 3 explore, 4 island); null = it could not open''',
      '''# 0.3.74 (oldmenu6): the world screen opened on a view (1 quests, 2 collections with an optional category name, 3 explore, 4 island; 0.3.75: 5 travel); null = it could not open''')

# ======================================================================= the Travel view's drawing (before build)
GV_FILL = r'''# ======== T: THE TRAVEL VIEW (0.3.75, oldmenu7) - the old World > Teleport page: the saved Teleport grid (MenuLayout part 1), the auto places
# in the free slots of rows 4 + 5 (MenuPage.addAuto - island homes, homes, then warps A-Z), Arrange and + Add. The same reads as the old page.
M(wtab, r"""
public static String gName(String k) {
  if (k == null) return "That place";
  if (k.equals("tp:island")) return "Your island";
  if (k.equals("tp:hub")) return "Hub";
  if (k.equals("tp:spawn")) return "Spawn";
  if (k.startsWith("ihome:")) return "Island home " + @PKG@.MenuUtil.safe(k.substring(6));
  if (k.startsWith("zhome:")) return "Home " + @PKG@.MenuUtil.safe(k.substring(6));
  if (k.startsWith("warp:")) return @PKG@.MenuUtil.safe(k.substring(5));
  return "That place";
}""")
# a key as a card: { icon, name, where, line 2, "1" usable / "0", ok | dim | gone, the go key } - MenuPage.look's rules for the Teleport grid's keys
M(wtab, r"""
public String[] gLook(String k, String[] ihs, String[] zhs, java.util.HashMap th, @TPP@ tp) {
  if (k == null) return null;
  if (k.startsWith("tp:")) {
    int i = @PKG@.MenuPage.tpEntry(k);
    if (i < 0) return new String[] { @PKG@.MenuData.ICON_EMPTY, k, "Not on this server", "", "0", "gone", k };
    String ic = @PKG@.MenuData.E_ICON[i];
    if (k.equals("tp:spawn")) return new String[] { ic, "Spawn", "The main world's spawn point", "", "1", "ok", k };
    boolean isl = k.equals("tp:island");
    boolean on = hasCmd(isl ? "island" : "hub");
    if (isl) return new String[] { ic, on ? "Your island" : "Your island (not on this server)", on ? "Teleport to your island" : "Islands are not on this server right now",
                                   on ? "Command: /island" : "", on ? "1" : "0", on ? "ok" : "dim", k };
    return new String[] { ic, on ? "Hub" : "Hub (not on this server)", on ? "Go back to the hub" : "The hub is not on this server right now",
                          on ? "Command: /hub" : "", on ? "1" : "0", on ? "ok" : "dim", k };
  }
  if (k.startsWith("ihome:") || k.startsWith("zhome:")) {
    boolean isl = k.startsWith("ihome:");
    String n = k.substring(6);
    String nm = @PKG@.MenuPage.nameIn(isl ? ihs : zhs, n);
    String ic = isl ? @PKG@.MenuData.ICON_IHOME : @PKG@.MenuData.ICON_ZHOME;
    if (nm == null) return new String[] { ic, (isl ? "Island home " : "Home ") + @PKG@.MenuUtil.safe(n), "Not there any more", "", "0", "gone", k };
    if (isl) return new String[] { ic, "Island home " + @PKG@.MenuUtil.safe(nm), "On your island", "Command: /island " + @PKG@.MenuUtil.safe(nm), "1", "ok", "ihome:" + nm };
    return new String[] { ic, "Home " + @PKG@.MenuUtil.safe(nm), "Your home", "Command: /home " + @PKG@.MenuUtil.safe(nm), "1", "ok", "zhome:" + nm };
  }
  if (k.startsWith("warp:")) {
    String n = k.substring(5);
    if (tp == null || !tp.isWarpsLoaded()) return new String[] { @PKG@.MenuData.ICON_WARP, @PKG@.MenuUtil.safe(n), "The warp list is still loading", "", "0", "dim", k };
    @WRP@ w = null;
    try { w = (@WRP@) tp.getWarps().get(n); } catch (Throwable t) { w = null; }
    if (w == null) return new String[] { @PKG@.MenuData.ICON_WARP_LOCKED, @PKG@.MenuUtil.safe(n), "This warp was removed", "", "0", "gone", k };
    String id = @PKG@.MenuUtil.safe(w.getId());
    boolean open = @PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId());
    String pos = "";
    try {
      @V3D@ p = w.getTransform().getPosition();
      pos = "X " + (long) Math.floor(p.x) + "   Y " + (long) Math.floor(p.y) + "   Z " + (long) Math.floor(p.z);
    } catch (Throwable t) { pos = ""; }
    if (!open) return new String[] { @PKG@.MenuData.ICON_WARP_LOCKED, id + " (locked)", "Locked - you have not unlocked this warp yet", "", "0", "dim", k };
    return new String[] { @PKG@.MenuPage.themeIcon(th, n), id, "Warp - World: " + @PKG@.MenuUtil.safe(w.getWorld()), pos, "1", "ok", k };
  }
  return new String[] { @PKG@.MenuData.ICON_EMPTY, @PKG@.MenuUtil.safe(k), "Not on this server", "", "0", "gone", k };
}""")
M(wtab, r"""
public void gHide(@UCB@ b, int k) {
  b.set("#SkyyWtabGvT" + k + ".Visible", false);
  this.gKey[k] = null;
  this.gGoK[k] = null;
  this.gAct[k] = 0;
}""")
# a card: act 0 none, 1 Go, 2 Pick up (a pinned place), 3 Pick up (an auto place: pinned first), 4 + Add (an empty slot), 5 Put back, 6 Move here /
# Swap here, 7 Add (the + Add list). The button and the icon (Go only) carry the page token; the key / go key are what this card showed.
M(wtab, r"""
public void gDraw(@UCB@ b, @UEB@ ev, int k, String[] l, String name, String btn, int act, String key) {
  String c = "SkyyWtabGvT" + k;
  boolean ok = "1".equals(l[4]);
  b.set("#" + c + ".Visible", true);
  b.set("#" + c + "I.Slots", @PKG@.InvPage.act(one(cell(l[0], name, l[2], ok))));
  b.set("#" + c + "N.Text", @PKG@.MenuUtil.clip(name, 30));
  b.set("#" + c + "S.Text", @PKG@.MenuUtil.clip(l[2], 44));
  b.set("#" + c + "W.Text", @PKG@.MenuUtil.clip(l[3], 44));
  b.set("#" + c + "B.Visible", act != 0);
  if (act != 0) {
    b.set("#" + c + "B.Text", btn);
    ev.addEventBinding(@BT@.Activating, "#" + c + "B", @EVD@.of("a", "gk:" + k).append("t", this.tok));
  }
  if (act == 1) ev.addEventBinding(@BT@.SlotClicking, "#" + c + "I", @EVD@.of("a", "gk:" + k).append("t", this.tok), false);
  this.gKey[k] = key;
  this.gGoK[k] = l.length > 6 ? l[6] : key;
  this.gAct[k] = act;
}""")
M(wtab, r"""
public void fillGv(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  int n = @PKG@.WorldTabData.GN;
  this.gKey = new String[n];
  this.gGoK = new String[n];
  this.gAct = new int[n];
  this.gAllow = "|";
  this.gDrawn = null;
  String[] ihs = homes("island:fn:homes", u);
  String[] zhs = homes("essentials:fn:homes", u);
  java.util.HashMap th = null;
  try { th = @PKG@.MenuPage.warpThemes(); } catch (Throwable t) { th = null; }
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
  boolean bad = @PKG@.MenuLayout.unreadable(u);
  this.gAdmin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  String[] g = @PKG@.MenuLayout.grid(u, 1);
  this.gDrawn = @PKG@.MenuLayout.copy(g);
  if (bad) { this.gEdit = false; this.gSel = -1; this.gAddAt = -1; }
  if (this.gSel >= 0 && (this.gSel >= g.length || g[this.gSel] == null)) this.gSel = -1;
  if (this.gAddAt >= 0 && (this.gAddAt >= g.length || g[this.gAddAt] != null)) this.gAddAt = -1;
  boolean add = this.gEdit && this.gAddAt >= 0;
  String head = "";
  String cnt = "";
  int pg = 0;
  if (add) {
    java.util.ArrayList c = new java.util.ArrayList();
    for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) c.add(@PKG@.MenuData.TPK_KEY[i]);
    for (int i = 0; ihs != null && i < ihs.length; i++) c.add("ihome:" + ihs[i]);
    for (int i = 0; zhs != null && i < zhs.length; i++) c.add("zhome:" + zhs[i]);
    if (tp != null && tp.isWarpsLoaded()) {
      java.util.ArrayList ws = new java.util.ArrayList();
      try {
        java.util.Iterator it = tp.getWarps().keySet().iterator();
        while (it.hasNext()) { String w = String.valueOf(it.next()); if (@PKG@.MenuLayout.okWarp(w)) ws.add(w); }
      } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the warp list failed: " + t); }
      java.util.Collections.sort(ws);
      for (int i = 0; i < ws.size(); i++) c.add("warp:" + (String) ws.get(i));
    }
    java.util.ArrayList left = new java.util.ArrayList();
    for (int i = 0; i < c.size(); i++) {
      String k = (String) c.get(i);
      if (@PKG@.MenuLayout.hasSame(g, k) || !@PKG@.MenuLayout.okKey(k, true)) continue;
      String[] l = gLook(k, ihs, zhs, th, tp);
      if (l != null && !"gone".equals(l[5])) left.add(k);
    }
    this.gPages = pagesOf(left.size(), n);
    this.gAPage = clampPage(this.gAPage, this.gPages);
    pg = this.gAPage;
    for (int k = 0; k < n; k++) {
      int j = this.gAPage * n + k;
      if (j >= left.size()) { gHide(b, k); continue; }
      String key = (String) left.get(j);
      String[] l = gLook(key, ihs, zhs, th, tp);
      gDraw(b, ev, k, l, l[1], "Add", 7, key);
    }
    head = left.isEmpty() ? @PKG@.WorldTabData.GVNONE : @PKG@.WorldTabData.GVADD;
    cnt = left.size() == 1 ? "1 to add" : left.size() + " to add";
    this.gAllow = "|cn|";
  } else {
    java.util.ArrayList auto = new java.util.ArrayList();
    @PKG@.MenuPage.addAuto(auto, g, "ihome:", ihs);
    @PKG@.MenuPage.addAuto(auto, g, "zhome:", zhs);
    boolean placed = false;
    for (int s = 0; s < g.length; s++) { if (g[s] != null && g[s].startsWith("warp:")) placed = true; }
    int nw = 0;
    if (tp != null && tp.isWarpsLoaded()) {
      java.util.ArrayList ws = new java.util.ArrayList();
      try {
        java.util.Iterator it = tp.getWarps().keySet().iterator();
        while (it.hasNext()) { String w = String.valueOf(it.next()); if (!@PKG@.MenuLayout.has(g, "warp:" + w)) ws.add(w); }
      } catch (Throwable t) { @PKG@.MenuUtil.warn("world screen: the warp list failed: " + t); }
      java.util.Collections.sort(ws);
      nw = ws.size();
      for (int i = 0; i < ws.size(); i++) auto.add("warp:" + (String) ws.get(i));
    }
    java.util.ArrayList free = new java.util.ArrayList();
    for (int i = 0; i < @PKG@.MenuData.TP_AUTO.length; i++) {
      int s = @PKG@.MenuData.TP_AUTO[i];
      if (s >= 0 && s < g.length && s < n && g[s] == null) free.add(Integer.valueOf(s));
    }
    int per = free.size();
    this.gPages = per == 0 ? 1 : pagesOf(auto.size(), per);
    this.gPage = clampPage(this.gPage, this.gPages);
    pg = this.gPage;
    String[] at = new String[n];
    for (int i = 0; i < per; i++) {
      int j = this.gPage * per + i;
      if (j >= auto.size()) break;
      at[((Integer) free.get(i)).intValue()] = (String) auto.get(j);
    }
    int places = auto.size();
    String moving = null;
    for (int s = 0; s < n; s++) {
      String key = s < g.length ? g[s] : null;
      boolean pin = key != null;
      if (!pin) key = at[s];
      if (key == null) {
        if (!this.gEdit) { gHide(b, s); continue; }
        boolean mv = this.gSel >= 0;
        String[] e = new String[] { @PKG@.MenuData.ICON_EMPTY, "Empty slot", mv ? "Move here puts it in this slot" : "+ Add puts a place here", "", "0", "ok", null };
        gDraw(b, ev, s, e, "Empty slot", mv ? "Move here" : "+ Add", mv ? 6 : 4, null);
        continue;
      }
      String[] l = gLook(key, ihs, zhs, th, tp);
      if (l == null) { gHide(b, s); continue; }
      boolean gone = "gone".equals(l[5]);
      if (gone && (!this.gEdit || !pin)) { gHide(b, s); continue; }
      if (pin && !gone) places = places + 1;
      String nm = gone ? l[1] + " (not on this server)" : l[1];
      if (!this.gEdit) { gDraw(b, ev, s, l, nm, "Go", "1".equals(l[4]) ? 1 : 0, key); continue; }
      if (this.gSel < 0) { gDraw(b, ev, s, l, nm, "Pick up", pin ? 2 : 3, key); continue; }
      if (s == this.gSel) { moving = nm; gDraw(b, ev, s, l, "[Moving] " + nm, "Put back", 5, key); continue; }
      gDraw(b, ev, s, l, nm, pin ? "Swap here" : "Move here", 6, key);
    }
    cnt = places == 1 ? "1 place" : places + " places";
    if (bad) head = @PKG@.MenuData.EDIT_WAIT;
    else if (!this.gEdit) head = nw == 0 && !placed ? (tp == null || tp.isWarpsLoaded() ? @PKG@.WorldTabData.GVNOWARP : @PKG@.WorldTabData.GVLOAD) : @PKG@.WorldTabData.GVHEAD;
    else if (moving != null) head = "Moving " + @PKG@.MenuUtil.clip(moving, 40) + " - press Move here or Swap here where it goes, Put back to cancel, or Remove.";
    else head = @PKG@.WorldTabData.GVEDIT;
    if (!this.gEdit) this.gAllow = "|ar|";
    else this.gAllow = "|rs|dn|" + (this.gSel >= 0 ? "rm|" : "") + (this.gAdmin ? "sd|cd|" : "");
  }
  b.set("#SkyyWtabGvH.Text", head);
  b.set("#SkyyWtabGvC.Text", cnt);
  b.set("#SkyyWtabGvP.Visible", this.gPages > 1);
  b.set("#SkyyWtabGvPg.Text", "Page " + (pg + 1) + " / " + this.gPages);
  String[] fb = new String[] { "Ar", "Rm", "Rs", "Sd", "Cd", "Dn", "Cn" };
  String[] fa = new String[] { "ar", "rm", "rs", "sd", "cd", "dn", "cn" };
  for (int i = 0; i < fb.length; i++) {
    boolean on = allowed(this.gAllow, fa[i]);
    b.set("#SkyyWtabGv" + fb[i] + ".Visible", on);
    if (on) ev.addEventBinding(@BT@.Activating, "#SkyyWtabGv" + fb[i], @EVD@.of("a", "g" + fa[i]).append("t", this.tok));
  }
  b.set("#SkyyWtabGvRs.Text", "grs".equals(this.gArm) ? "Click again to reset" : "Reset");
  b.set("#SkyyWtabGvSd.Text", "gsd".equals(this.gArm) ? "Click again to set" : "Set default");
  b.set("#SkyyWtabGvCd.Text", "gcd".equals(this.gArm) ? "Click again to clear" : "Clear default");
}""")
'''
P.rep('''M(wtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.WorldTabData.LK;''', GV_FILL + '''M(wtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.WorldTabData.LK;''')
P.rep('''  char cur = this.view == 1 ? 'Q' : (this.view == 2 ? 'C' : (this.view == 3 ? 'E' : (this.view == 4 ? 'I' : 'H')));''',
      '''  char cur = this.view == 1 ? 'Q' : (this.view == 2 ? 'C' : (this.view == 3 ? 'E' : (this.view == 4 ? 'I' : (this.view == 5 ? 'T' : 'H'))));   // 0.3.75: T = travel''')
P.rep('''    } else {
      vc = @PKG@.WorldTabData.IVCAP;''', '''    } else if (this.view == 5) {   // 0.3.75 (oldmenu7): the Travel view
      vc = @PKG@.WorldTabData.GVCAP;
      try { fillGv(b, ev); } catch (Throwable t) { this.gKey = new String[0]; this.gGoK = new String[0]; this.gAct = new int[0]; this.gAllow = "|"; @PKG@.MenuUtil.warn("world screen: the travel view failed: " + t); }
    } else {
      vc = @PKG@.WorldTabData.IVCAP;''')

# ======================================================================= the Travel view's trips (after travel()): Go, Spawn (WorldSpawn), the go keys
GV_GO = r'''# ---- 0.3.75 (oldmenu7): the Travel view's trips. Spawn = the old Teleport page's engine path (MenuPage.doSpawn / spawnResolved / moveTo):
# the spawn point is a future (never waited for on the world thread); WorldSpawn takes its answer to the world the player pressed in.
F(wsp, "public @PKG@.WorldTab page;")
F(wsp, "public @PR@ pr;")
F(wsp, "public @WLD@ target;")
F(wsp, "public @WLD@ home;")
F(wsp, "public volatile Object result;")
F(wsp, "public volatile Throwable error;")
wsp.addInterface(pool.get("java.lang.Runnable"))
wsp.addInterface(pool.get("java.util.function.BiConsumer"))
C(wsp, r"""
public WorldSpawn(@PKG@.WorldTab page, @PR@ pr, @WLD@ target, @WLD@ home) { this.page = page; this.pr = pr; this.target = target; this.home = home; }""")
# any thread (the future's): keep the answer, hop to the world the player pressed in
M(wsp, r"""
public void accept(Object r, Object e) {
  this.result = r;
  this.error = e instanceof Throwable ? (Throwable) e : null;
  try { this.home.execute(this); }
  catch (Throwable t) { if (this.page != null) this.page.spawnWait = false; @PKG@.MenuUtil.warn("world screen: could not finish the Spawn teleport: " + t); }
}""")
# the Teleport component + the /tp back history line (MenuPage.moveTo's calls)
M(wtab, r"""
public void moveTo(@REF@ ref, @ST@ st, @TP@ t, String label) {
  @WLD@ here = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); here = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }
  @TC@ mtc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
  st.addComponent(ref, @TP@.getComponentType(), t);
  try {
    if (here != null && mtc != null && mtc.getPosition() != null) {
      @V3D@ p = mtc.getPosition();
      @R3F@ r = mhr != null ? mhr.getRotation() : null;
      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());
      if (h != null) h.append(here, new @V3D@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@(), "Menu: " + label);
    }
  } catch (Throwable t2) { }
}""")
# the player's world thread (WorldSpawn.run): the screen still open = the caption or the trip (the screen closes first, as warpGo); closed
# meanwhile = the trip + the chat line (no page touched); no spawn point / an error = the caption (open) or a chat line
M(wtab, r"""
public void spawnResolved(@REF@ ref, @ST@ st, @WLD@ target, Object result, Throwable error) {
  this.spawnWait = false;
  boolean open = !this.closed && still();
  if (error != null) @PKG@.MenuUtil.warn("world screen: the spawn point of the main world could not be found for " + @PKG@.PageGuard.who(this.playerRef) + ": " + error);
  if (error != null || !(result instanceof @TRF@)) {
    String why = error != null ? "The spawn point could not be found - try again." : "The main world has no spawn point.";
    if (open) say(why);
    else this.playerRef.sendMessage(@MSG@.raw("[Menu] " + why));
    return;
  }
  @TP@ t = @TP@.createForPlayer(target, (@TRF@) result);
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { if (open) say("You are already teleporting"); return; }
  if (open) shut();
  GOES = GOES + 1;
  moveTo(ref, st, t, "Spawn");
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to Spawn..."));
}""")
M(wsp, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) { if (this.page != null) this.page.spawnWait = false; return; }
    java.util.UUID wu = this.pr.getWorldUuid();
    if (wu == null || @UNI@.get().getWorld(wu) != this.home) { if (this.page != null) this.page.spawnWait = false; return; }
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) { if (this.page != null) this.page.spawnWait = false; return; }
    @ST@ st = r.getStore();
    if (st == null) { if (this.page != null) this.page.spawnWait = false; return; }
    this.page.spawnResolved(r, st, this.target, this.result, this.error);
  } catch (Throwable t) { if (this.page != null) this.page.spawnWait = false; @PKG@.MenuUtil.warn("world screen: the Spawn teleport failed: " + t); }
}""")
# Spawn pressed: the caption first (ONE packet for the press), then the future; a second press while it runs = a caption, no second trip
M(wtab, r"""
public void spawnGo() {
  this.answered = true;
  if (this.spawnWait) { say("On the way to Spawn - one moment"); return; }
  @WLD@ target = null;
  try { target = @UNI@.get().getDefaultWorld(); } catch (Throwable t) { target = null; }
  if (target == null) { say("The main world is not loaded"); return; }
  @WLD@ home = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); home = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { home = null; }
  if (home == null) { say("The main world has no spawn point"); return; }
  java.util.concurrent.CompletableFuture f = null;
  try { f = target.getWorldConfig().getSpawnProvider().getSpawnPointAsync(target, this.playerRef.getUuid()); }
  catch (Throwable t) { f = null; @PKG@.MenuUtil.warn("world screen: the spawn point could not be asked for: " + t); }
  if (f == null) { say("The main world has no spawn point"); return; }
  this.spawnWait = true;
  say("Finding the spawn point...");
  f.whenComplete(new @PKG@.WorldSpawn(this, this.playerRef, target, home));
}""")
# a card's Go: the drawn go key -> the SAME trip the home Travel list makes (cmdGo / islandHome / homeGo / warpGo) or Spawn
M(wtab, r"""
public void gGo(String k) {
  this.answered = true;
  if (k == null) { say("Nothing there"); return; }
  if (k.equals("tp:island")) { cmdGo("island"); return; }
  if (k.equals("tp:hub")) { cmdGo("hub"); return; }
  if (k.equals("tp:spawn")) { spawnGo(); return; }
  if (k.startsWith("ihome:")) { islandHome(k.substring(6)); return; }
  if (k.startsWith("zhome:")) { homeGo(k.substring(6)); return; }
  if (k.startsWith("warp:")) { warpGo(k.substring(5)); return; }
  say("Nothing there");
}""")
'''
P.rep('''# ---- 0.3.74 (oldmenu6): the views' actions - every one answers with ONE packet (a redraw with the bridge's line in the caption, a caption,
# or the close a trip does). Navigation (views, tabs, picks, pages) needs no token; a bridge act needs the token (checked in handleDataEvent)''',
      GV_GO + '''# ---- 0.3.74 (oldmenu6): the views' actions - every one answers with ONE packet (a redraw with the bridge's line in the caption, a caption,
# or the close a trip does). Navigation (views, tabs, picks, pages) needs no token; a bridge act needs the token (checked in handleDataEvent)''')
P.rep('''      || a.startsWith("im:") || a.startsWith("it:") || a.startsWith("ivv:") || a.startsWith("ib:") || a.startsWith("ip:")) return 4;
  if (a.startsWith("flt:") || a.startsWith("pg:") || a.startsWith("go:") || a.equals("home") || a.equals("isl") || a.equals("exp") || a.equals("qlog") || a.equals("coll")) return 0;''',
      '''      || a.startsWith("im:") || a.startsWith("it:") || a.startsWith("ivv:") || a.startsWith("ib:") || a.startsWith("ip:")) return 4;
  if (a.startsWith("gk:") || a.startsWith("gpg:") || a.equals("gar") || a.equals("gdn") || a.equals("gcn") || a.equals("grm") || a.equals("grs")
      || a.equals("gsd") || a.equals("gcd")) return 5;   // 0.3.75: the Travel view
  if (a.startsWith("flt:") || a.startsWith("pg:") || a.startsWith("go:") || a.equals("home") || a.equals("isl") || a.equals("exp") || a.equals("qlog") || a.equals("coll")
      || a.equals("trv")) return 0;''')
P.rep('''  int was = this.view;
  this.view = v < 0 || v > 4 ? 0 : v;
  if (was == 4 && this.view != 4 && this.iSeen) { iRefresh(); this.iSeen = false; }''', '''  int was = this.view;
  this.view = v < 0 || v > 5 ? 0 : v;   // 0.3.75: 5 = the Travel view
  if (was == 4 && this.view != 4 && this.iSeen) { iRefresh(); this.iSeen = false; }
  this.gArm = null;   // 0.3.75: a view change drops an armed Reset / Set default / Clear default
  if (was == 5 && this.view != 5) { this.gEdit = false; this.gSel = -1; this.gAddAt = -1; }   // leaving Travel leaves Arrange (saved at every press)''')
P.rep('''    this.iVPage = 0;
    this.iXPage = 0;
  }
  this.tcap = "";
  redraw();
}""")''', '''    this.iVPage = 0;
    this.iXPage = 0;
    this.gPage = 0;
    this.gAPage = 0;
  }
  this.tcap = "";
  redraw();
}""")''')
P.rep('''public void vRefresh() {
  this.answered = true;
  if (this.view == 4) iRefresh();''', '''public void vRefresh() {
  this.answered = true;
  this.gArm = null;   // 0.3.75: Refresh drops an armed press
  if (this.view == 4) iRefresh();''')

# ======================================================================= the Travel view's presses (after actView: pick / step are defined)
GV_ACT = r'''# ---- 0.3.75 (oldmenu7): the Travel view's presses - ONE packet each. The pager is navigation (no token); every other press carries the token
# and acts only on what the drawing showed (gKey / gGoK / gAct / gAllow / gDrawn). Saves: MenuLayout.put / saveDefault / clearDefault (the
# old page's calls, the same file); an unreadable layout file is never changed.
M(wtab, r"""
public boolean navGv(String a) {
  if (!a.startsWith("gpg:")) return false;
  boolean add = this.gEdit && this.gAddAt >= 0;
  int p = step(add ? this.gAPage : this.gPage, this.gPages, a, 4);
  if (p >= 0) {   // a new page drops an armed press (the redraw shows the plain button again); the first / last page = a caption only
    if (add) this.gAPage = p; else this.gPage = p;
    this.gArm = null;
    this.tcap = "";
    redraw();
  }
  return true;
}""")
M(wtab, r"""
public void gNone(String armed) {
  this.gArm = armed;
  say(@PKG@.WorldTabData.NONE);
}""")
# the saved order is not the drawn one any more (another screen / the old page / an admin changed it): say so, draw it again, nothing moves
M(wtab, r"""
public boolean gStale() {
  String[] live = @PKG@.MenuLayout.grid(this.playerRef.getUuid(), 1);
  if (this.gDrawn != null && java.util.Arrays.equals(live, this.gDrawn)) return false;
  this.gSel = -1;
  this.gAddAt = -1;
  this.tcap = @PKG@.WorldTabData.GVSTALE;
  redraw();
  return true;
}""")
M(wtab, r"""
public boolean gSave(String[] g) {
  if (@PKG@.MenuLayout.put(this.playerRef.getUuid(), this.playerRef.getUsername(), 1, g) == 1) return true;
  this.gSel = -1;
  this.tcap = "That did not work - try again. Nothing moved.";
  redraw();
  return false;
}""")
M(wtab, r"""
public boolean actGv(String a) {
  boolean gk = a.startsWith("gk:");
  if (!gk && !a.equals("gar") && !a.equals("gdn") && !a.equals("gcn") && !a.equals("grm") && !a.equals("grs") && !a.equals("gsd") && !a.equals("gcd")) return false;
  this.answered = true;
  String armed = this.gArm;
  this.gArm = null;
  java.util.UUID u = this.playerRef.getUuid();
  if (a.equals("gar")) {
    if (!allowed(this.gAllow, "ar")) { gNone(armed); return true; }
    if (@PKG@.MenuLayout.unreadable(u)) { this.tcap = @PKG@.MenuData.EDIT_WAIT; redraw(); return true; }
    @PKG@.MenuLayout.SPILL.remove(u.toString());
    this.gEdit = true;
    this.gSel = -1;
    this.gAddAt = -1;
    this.gAPage = 0;
    this.tcap = "Arrange is on - nothing moves until you press Move here or Swap here.";
    redraw();
    return true;
  }
  if (a.equals("gdn")) {
    if (!allowed(this.gAllow, "dn")) { gNone(armed); return true; }
    this.gEdit = false;
    this.gSel = -1;
    this.gAddAt = -1;
    @PKG@.MenuLayout.MIGRATED.remove(u.toString());
    this.tcap = "Saved - press Go to travel.";
    redraw();
    return true;
  }
  if (a.equals("gcn")) {
    if (!allowed(this.gAllow, "cn")) { gNone(armed); return true; }
    this.gAddAt = -1;
    this.tcap = "Nothing was added.";
    redraw();
    return true;
  }
  if (gk) {
    int k = pick(a, 3, this.gAct == null ? 0 : this.gAct.length);
    int act = k < 0 ? 0 : this.gAct[k];
    if (act == 0 || ((act == 1 || act == 2 || act == 3 || act == 7) && this.gKey[k] == null)) { gNone(armed); return true; }
    if (act == 1) { gGo(this.gGoK[k]); return true; }
    if (act == 5) { this.gSel = -1; this.tcap = "Put back - nothing moved."; redraw(); return true; }
    if (@PKG@.MenuLayout.unreadable(u)) { this.gSel = -1; this.gAddAt = -1; this.tcap = @PKG@.MenuData.EDIT_WAIT; redraw(); return true; }
    if (gStale()) return true;
    if (act == 4) { this.gAddAt = k; this.gAPage = 0; this.tcap = ""; redraw(); return true; }
    String key = this.gKey[k];
    String[] g = @PKG@.MenuLayout.grid(u, 1);
    if (act == 2) {
      this.gSel = k;
      this.tcap = "Picked up " + gName(key) + " - press Move here or Swap here where it goes.";
      redraw();
      return true;
    }
    if (act == 3) {
      if (!@PKG@.MenuLayout.okKey(key, true)) { this.tcap = gName(key) + " can't be arranged (its name has characters a layout can't save) - it stays in the free slots."; redraw(); return true; }
      if (k >= g.length || g[k] != null || @PKG@.MenuLayout.has(g, key)) { this.tcap = @PKG@.WorldTabData.GVSTALE; redraw(); return true; }
      g[k] = key;
      if (!gSave(g)) return true;
      this.gSel = k;
      this.tcap = "Picked up " + gName(key) + " - press Move here or Swap here where it goes.";
      redraw();
      return true;
    }
    if (act == 6) {
      int from = this.gSel;
      this.gSel = -1;
      if (from < 0 || from >= g.length || k >= g.length || g[from] == null || from == k) { this.tcap = "That move did not work - nothing moved."; redraw(); return true; }
      String x = g[from];
      String y = g[k];
      g[k] = x;
      g[from] = y;
      if (!gSave(g)) return true;
      this.tcap = y != null ? gName(x) + " and " + gName(y) + " swapped places." : gName(x) + " moved.";
      redraw();
      return true;
    }
    if (act == 7) {
      int at = this.gAddAt;
      this.gAddAt = -1;
      if (at < 0 || at >= g.length || g[at] != null) { this.tcap = "That slot is not free any more - nothing was added."; redraw(); return true; }
      if (@PKG@.MenuLayout.hasSame(g, key)) { this.tcap = gName(key) + " is in your Travel order already."; redraw(); return true; }
      g[at] = key;
      if (!gSave(g)) return true;
      this.tcap = gName(key) + " added.";
      redraw();
      return true;
    }
    gNone(armed);
    return true;
  }
  // the foot: Remove, Reset, Set default, Clear default (the last three arm first: the same press again runs it)
  String al = a.equals("grm") ? "rm" : (a.equals("grs") ? "rs" : (a.equals("gsd") ? "sd" : "cd"));
  if (!allowed(this.gAllow, al)) { gNone(armed); return true; }
  if ((al.equals("sd") || al.equals("cd")) && !@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.tcap = "Only admins can change the server default Travel order."; redraw(); return true; }
  if (@PKG@.MenuLayout.unreadable(u)) { this.gSel = -1; this.tcap = @PKG@.MenuData.EDIT_WAIT; redraw(); return true; }
  if (al.equals("rm")) {
    if (gStale()) return true;
    String[] g = @PKG@.MenuLayout.grid(u, 1);
    int s = this.gSel;
    this.gSel = -1;
    if (s < 0 || s >= g.length || g[s] == null) { this.tcap = "Pick a place up first, then press Remove."; redraw(); return true; }
    String gone = g[s];
    g[s] = null;
    if (!gSave(g)) return true;
    this.tcap = gName(gone) + " removed - it waits in + Add (press + Add on an empty slot).";
    redraw();
    return true;
  }
  if (!a.equals(armed)) {
    this.gArm = a;
    this.tcap = al.equals("rs") ? "Press Reset again: your Travel order goes back to the default."
              : (al.equals("sd") ? "Press Set default again: YOUR Travel order becomes the server default (for players without their own)."
              : "Press Clear default again: the standard Travel order becomes the server default again.");
    redraw();
    return true;
  }
  this.gSel = -1;
  if (al.equals("rs")) {
    this.tcap = @PKG@.MenuLayout.put(u, this.playerRef.getUsername(), 1, (String[]) null) == 1 ? "Back to the default Travel order." : "That did not work - try again.";
  } else if (al.equals("sd")) {
    if (gStale()) return true;   // fixer: save only the order the admin saw (another screen changed it between the two presses = said, nothing saved)
    this.tcap = @PKG@.MenuLayout.saveDefault(1, @PKG@.MenuLayout.grid(u, 1)) == 1 ? "Saved - every player without their own Travel order now gets yours." : "That did not work - try again.";
  } else {
    @PKG@.MenuLayout.clearDefault(1);
    this.tcap = "The standard Travel order is the server default again.";
  }
  redraw();
  return true;
}""")
'''
P.rep('''  return false;
}""")
M(wtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', '''  return false;
}""")
''' + GV_ACT + '''M(wtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''    if (a.equals("full")) { hub("world", "teleport", "the Teleport page"); return; }
    // 0.3.74 (oldmenu6): the Quest log / Collections / Explore / Island settings are views of this screen (no old page); a click meant for
    // another view or the home cards = a caption, no call''', '''    // 0.3.75 (oldmenu7): no Full page - the old Teleport page is the Travel view (a forged 'full' falls through: the stale-token redraw)
    // 0.3.74 (oldmenu6): the Quest log / Collections / Explore / Island settings are views of this screen (no old page); a click meant for
    // another view or the home cards = a caption, no call''')
P.rep('''    if (a.equals("isl")) { goView(4); return; }
    if (a.equals("exp")) { goView(3); return; }''', '''    if (a.equals("isl")) { goView(4); return; }
    if (a.equals("trv")) { goView(5); return; }   // 0.3.75: the Travel card's button = the Travel view
    if (a.equals("exp")) { goView(3); return; }''')
P.rep('''    if (navView(a)) return;
    if (a.startsWith("flt:")) {''', '''    if (navView(a)) return;
    if (navGv(a)) return;   // 0.3.75: the Travel view's pager
    if (a.startsWith("flt:")) {''')
P.rep('''    if (actView(a, d)) return;   // 0.3.74: the views' bridge acts (each only where the drawing showed it)''',
      '''    if (actView(a, d)) return;   // 0.3.74: the views' bridge acts (each only where the drawing showed it)
    if (actGv(a)) return;   // 0.3.75: the Travel view's presses (each only where the drawing showed it)''')
P.rep('''# every place the old World > Teleport page offers (Spawn + Arrange: Full page): { key, icon, name, hover text, "1" usable / "0", kind }''',
      '''# every place the old World > Teleport page offers (0.3.75: Spawn + Arrange = the Travel view): { key, icon, name, hover text, "1" usable / "0", kind }''')

# ======================================================================= the hub tab World > Teleport with the old menu OFF = the Travel view
P.rep('''_old_body(mhub, "itemPage", r"""{
  if (@PKG@.MenuCfg.OLD_MENU || $1 == null) return null;
  return new @PKG@.InvPage($1, "menu item");
}""")''', '''_old_body(mhub, "itemPage", r"""{
  if (@PKG@.MenuCfg.OLD_MENU || $1 == null) return null;
  return new @PKG@.InvPage($1, "menu item");
}""")
# 0.3.75 (oldmenu7): MenuHub.page - the World > Teleport hub tab (other mods' tab strips: MenuHubOpen "teleport") with the old menu OFF = the World
# screen's Travel view, never the old Teleport page; ON = the old page as before (the old menu stays one piece). Set here: WorldTab is made after
# MenuHub.page (inserted in front of its body; every other tab exactly as 0.3.74).
_pg75 = [m_ for m_ in mhub.getDeclaredMethods() if str(m_.getName()) == "page"]
assert len(_pg75) == 1, "0.3.75: MenuHub.page"
_pg75[0].insertBefore(jv(r"""{
  if ($1 != null && $2 != null && $2.equals("teleport") && !@PKG@.MenuCfg.OLD_MENU) {
    @PKG@.WorldTab w = new @PKG@.WorldTab($1, "World > Teleport");
    w.view = 5;
    return w;
  }
}"""))''')
assert P.has('''public static @PAGE@ page(@PR@ pr, String tab) {
  if (pr == null || tab == null) return null;
  if (tab.equals("stats")) return new @PKG@.StatsPage(pr, 0);
  if (tab.equals("teleport")) return new @PKG@.MenuPage(pr, "tp");''') and P.has('_old_body(mhub, "itemPage"'), "0.3.75: MenuHub.page as 0.3.74 (the Travel route goes in front of it, nothing else changes)"

# ======================================================================= the ratchet: OLD_LEFT shrinks by the row this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"),
    ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.75 (oldmenu7): world:teleport (the World screen's Full page = the Travel view: your Travel order, Spawn, Arrange; the World > Teleport hub tab
# opens it while the old menu is off) is gone.
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"),
    ("storage", "bank"), ("storage", "pocket"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0 + 1, "0.3.75: no system / command; one class (WorldSpawn)"
_i = P.s.index
assert _i("public static int pagesOf(int n, int per)") < _i("public String[] gLook(") < _i("public void gDraw(") < _i("public void fillGv(") \
    < _i("  char cur = this.view == 1 ? 'Q' :") < _i("public void cmdGo(String c)") < _i("public void warpGo(String n)") < _i('public WorldSpawn(@PKG@.WorldTab page') \
    < _i("public void moveTo(@REF@ ref, @ST@ st, @TP@ t, String label) {\n  @WLD@ here = null;\n  try { java.util.UUID wu = this.playerRef.getWorldUuid(); here = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }\n  @TC@ mtc = (@TC@) st.getComponent(ref, @TC@.getComponentType());\n  @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());\n  st.addComponent(ref, @TP@.getComponentType(), t);\n  try {\n    if (here != null && mtc != null && mtc.getPosition() != null) {\n      @V3D@ p = mtc.getPosition();\n      @R3F@ r = mhr != null ? mhr.getRotation() : null;\n      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());\n      if (h != null) h.append(here, new @V3D@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@(), \"Menu: \" + label);\n    }\n  } catch (Throwable t2) { }\n}\"\"\")\n# the player's world thread") \
    < _i("public void spawnResolved(@REF@ ref, @ST@ st, @WLD@ target, Object result, Throwable error) {\n  this.spawnWait = false;") \
    < _i("    this.page.spawnResolved(r, st, this.target, this.result, this.error);\n  } catch (Throwable t) { if (this.page != null)") < _i("public void spawnGo() {") < _i("public void gGo(String k) {") \
    < _i("public static int pick(String a, int cut, int n)") < _i("public boolean actView(String a, String d)") < _i("public boolean navGv(String a)") \
    < _i("public boolean actGv(String a)") < _i("    if (navGv(a)) return;") < _i("    if (actGv(a)) return;"), "0.3.75: the travel view methods before their callers"
assert _i("public WorldTab(@PR@ pr, String via) {") < _i('_pg75[0].insertBefore(jv(r"""{'), "0.3.75: the hub tab's route goes in after the WorldTab constructor"
for _old in ('hub("world", "teleport"', 'openHub("world", "teleport"', '"the Teleport page"', 'WT + "Full"'):
    assert _old not in P.s[P.s.index("# ================= 0.3.50 THE INVENTORY SCREEN"):P.s.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")], "0.3.75: no old link left: " + _old
assert 'WT + "Full"' not in P.s, "0.3.75: the World screen has no Full page"
P.finish()

HARNESS_OLD7_STATIC = r'''    # ---- OLD7 (0.3.75; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the ratchet shrank by exactly the row this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("world", "teleport")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 1,
            "OLD7 RATCHET OLD_LEFT lost world:teleport, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('hub("world", "teleport"' not in g and 'G_.glass_button(WT + "Full"' not in g and '("#" + WT + "Full", "full")' not in g and '"the Teleport page"' not in g
            and "Spawn and your teleport row: Full page." not in g and 'G_.glass_button(WT + "Tgo", "Travel"' in g and 'if (a.equals("trv")) { goView(5); return; }' in g,
            "OLD7 STATIC no Full page / Teleport page link or text on the World screen; the Travel card's Travel button opens the Travel view")
    K.check('if ($1 != null && $2 != null && $2.equals("teleport") && !@PKG@.MenuCfg.OLD_MENU) {' in g and "    w.view = 5;" in g and 'if (tab.equals("teleport")) return new @PKG@.MenuPage(pr, "tp");' in g
            and '_pg75[0].insertBefore(jv(r' in g,
            "OLD7 STATIC the World > Teleport hub tab = the Travel view while the old menu is off (the old page while it is on)")
    K.check('@PKG@.MenuLayout.put(this.playerRef.getUuid(), this.playerRef.getUsername(), 1, g) == 1' in g and "java.util.Arrays.equals(live, this.gDrawn)" in g
            and "if (act == 1) { gGo(this.gGoK[k]); return true; }" in g and 'getSpawnPointAsync(target, this.playerRef.getUuid());' in g
            and "f.whenComplete(new @PKG@.WorldSpawn(this, this.playerRef, target, home));" in g,
            "OLD7 STATIC a save only over the drawn order (MenuLayout part 1, the old page's file); Go = the drawn go key; Spawn = the engine's async spawn point")
    K.check(all(("0.3.75: %s" % t_) in g for t_ in ("a travel card fits", "the travel foot row fits", "the travel view fits", "a travel button fits", "a travel head line fits",
                                                      "a card's text column", "the Travel view's cards are the saved Teleport grid's 25 slots")),
            "OLD7 STATIC the build asserts the Travel view fits 1080, its buttons and lines fit, its 25 cards = the saved grid")
    mw7_ = re.search(r"WT_ELEMENTS <= (\d+)", g)
    K.check(mw7_ is not None and int(mw7_.group(1)) <= 800 and 'WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEIT")' in g,
            "OLD7 STATIC the world screen's budget = the frame + its biggest section (+ T, the Travel view), still <= 800")
'''

HARNESS_OLD7 = r'''    # ---- OLD7 (0.3.75, round oldmenu7): THE TRAVEL VIEW (the old World > Teleport page: your Travel order, Spawn, Arrange; stand-ins = the
    # Islands / Essentials contracts the old page used: island:fn:homes / gohome, essentials:fn:homes / gohome; the engine warps; MenuLayout part 1)
    SECT6[5] = "SkyyWtabGv"

    def only7(p_):   # the frame + ONE section: the Travel view, no home cards, no other view
        return (p_ is not None and has6(p_, "SkyyWtabGv") and not has6(p_, "SkyyWtabBody")
                and not [s_ for k_, s_ in SECT6.items() if k_ != 5 and has6(p_, s_)] and not sel_ok6(p_))
    nm7 = lambda c_, k_: txt6(c_, "GvT%dN" % k_)
    uu7 = PK.pr.getUuid()
    UNO7 = UUIDc(0x75, 0x75)   # a player with no Travel order of their own = the server default (or the built-in one)

    def g7(u_=None):
        return [None if x_ is None else str(x_) for x_ in list(ML.grid(uu7 if u_ is None else u_, 1))]

    def t_open(what):
        ws_, p_ = w_open(what)
        p_ = w_ev({"a": "trv"}, what + " - the Travel button")
        return ws_, p_

    def card7(c_, name_):
        ks_ = [k_ for k_ in range(25) if vis4(c_, "GvT%d" % k_) and nm7(c_, k_) == name_]
        return ks_[0] if ks_ else -1
    BR.put("island:fn:homes", Fn(lambda o: _JA(JS)(["Farm"])))
    ZH7 = ["base"]
    BR.put("essentials:fn:homes", Fn(lambda o: _JA(JS)(list(ZH7))))
    BR.put("island:fn:gohome", Fn(f_ih))
    BR.put("essentials:fn:gohome", Fn(f_zh))
    WW["zans"] = "ok"
    for k_ in ("essentials:fn:warps", "profile:fn:key"):
        BR.remove(k_)
    WN7 = sorted(str(k_) for k_ in WARPS.keySet())
    DEF7 = g7(UNO7)
    G0 = [None] * 25
    G0[11], G0[12], G0[13] = "tp:island", "tp:hub", "tp:spawn"
    K.check(int(ML.put(uu7, "SkyyCraftA", 1, _JA(JS)(G0))) == 1 and g7() == G0, "OLD7 setup: this player's Travel order = My Island | Hub | Spawn (%s)" % g7())
    WS, p_ = w_open("OLD7 open")
    K.check(not has6(p_, "SkyyWtabFull") and 'Text: "Travel"' in mk_of(p_, "SkyyWtabTgo") and len(bind6(p_, "trv")) == 1 and not bind6(p_, "full")
            and txt6(cmap(p_), "Tf") == "Spawn, your own order and Arrange:",
            "OLD7 HOME no Full page in the top bar; the Travel card's 'Travel' button (and its line)")
    p_ = w_ev({"a": "full"}, "OLD7 SAFE a forged Full page")
    K.check(str(PK.pm.getCustomPage().getClass().getSimpleName()) == "WorldTab" and not bool(WS.closed) and "The page changed" in cap4(p_),
            "OLD7 SAFE a forged Full page = the screen redrawn (ONE packet), no old page")
    p_ = w_ev({"a": "trv"}, "OLD7 the Travel button")
    cm = cmap(p_)
    exp7 = ["Island home Farm", "Home base"] + WN7
    K.notes.append("OLD7 the Travel view's first packet: %d commands, cards %s" % (len(cmds_of(p_)), [(k_, nm7(cm, k_)) for k_ in range(25) if vis4(cm, "GvT%d" % k_)]))
    K.check(int(WS.view) == 5 and only7(p_) and txt6(cm, "Cap") == str(WTD.GVCAP) and str(WTD.ST1) in mk_of(p_, "SkyyWtabGvVt5") and len(bind6(p_, "vw:5")) == 1,
            "OLD7 OPEN Travel = the TRAVEL VIEW (ONE section; the Travel sub-tab selected; its caption) %s" % sel_ok6(p_)[:3])
    K.check(nm7(cm, 11) == "Your island" and nm7(cm, 12) == "Hub" and nm7(cm, 13) == "Spawn" and txt6(cm, "GvT13S") == "The main world's spawn point"
            and [nm7(cm, 15 + i_) for i_ in range(min(10, len(exp7)))] == exp7[:10] and not vis4(cm, "GvT0") and not vis4(cm, "GvT14")
            and txt6(cm, "GvT11B") == "Go" and vis4(cm, "GvT13B") and txt6(cm, "GvT16W") == "Command: /home base" and txt6(cm, "GvT17S").startswith("Warp - World: ")
            and txt6(cm, "GvC") == "%d places" % (3 + len(exp7)) and txt6(cm, "GvH") == str(WTD.GVHEAD),
            "OLD7 PAGE your order: My Island | Hub | Spawn where they are pinned, then the auto places (island home, home, warps A-Z) in rows 4 + 5; empty slots hidden")
    K.check(vis4(cm, "GvAr") and not vis4(cm, "GvRm") and not vis4(cm, "GvRs") and not vis4(cm, "GvDn") and not vis4(cm, "GvCn") and not vis4(cm, "GvSd")
            and len(bind6(p_, "gk:11")) == 2 and '"t"' in bind6(p_, "gk:11")[0][2] and len(bind6(p_, "gar")) == 1 and '"t"' in bind6(p_, "gar")[0][2]
            and not bind6(p_, "grs") and len(bind6(p_, "gpg:1")) == 1 and "Slots" in " ".join(k_ for k_ in cm if k_.startswith("#SkyyWtabGvT11I")),
            "OLD7 PAGE Go (button + icon) and Arrange carry the page token; only Arrange in the foot; the pager is navigation")
    K.check(not any("Scrolling" in str(c_.text or "") for c_ in cmds_of(p_)) and nometa(p_), "OLD7 FIT no scrolling list; no item metadata in a card's icon")
    # ---- GO: the old page's trips, the same calls as the home Travel list
    l0_ = len(lines4())
    old_ = str(WS.tok)
    w_ev({"a": "gk:11", "t": old_}, "OLD7 GO Your island", n=None)
    K.check(bool(WS.closed) and lines4()[l0_:] == ["island"], "OLD7 GO Your island = /island as the player, the screen closed (%s)" % lines4()[l0_:])
    w_ev({"a": "gk:11", "t": old_}, "OLD7 SAFE double click", n=0, page=WS)
    K.check(lines4()[l0_:] == ["island"], "OLD7 SAFE a double click on Go = ONE /island")
    WS, p_ = t_open("OLD7 reopen")
    w_ev({"a": "gk:12", "t": str(WS.tok)}, "OLD7 GO Hub", n=None)
    K.check(bool(WS.closed) and lines4()[l0_:] == ["island", "hub"], "OLD7 GO Hub = /hub")
    WS, p_ = t_open("OLD7 reopen")
    ih0_ = len(WW["ih"])
    w_ev({"a": "gk:15", "t": str(WS.tok)}, "OLD7 GO island home", n=None)
    K.check(bool(WS.closed) and WW["ih"][ih0_:] == [[uk4, "Farm"]], "OLD7 GO an island home = island:fn:gohome {your UUID, Farm}, the screen closed first")
    WS, p_ = t_open("OLD7 reopen")
    zh0_ = len(WW["zh"])
    w_ev({"a": "gk:16", "t": str(WS.tok)}, "OLD7 GO home", n=None)
    K.check(bool(WS.closed) and WW["zh"][zh0_:] == [[uk4, "base"]], "OLD7 GO a home = essentials:fn:gohome {your UUID, base}; 'ok' = the screen closes")
    WS, p_ = t_open("OLD7 reopen")
    p_ = w_ev({"a": "gk:17", "t": str(WS.tok)}, "OLD7 GO a warp whose world is not loaded")
    K.check(not bool(WS.closed) and "is not loaded" in cap4(p_), "OLD7 GO a warp = InvPage.warpGo's calls (its world not loaded here = a caption) (%s)" % cap4(p_))
    # SPAWN: the main world not loaded / no spawn provider / a second press while one runs
    UniH7 = JClass("skyymenu19.Uni")
    def7_ = UniH7.DEF
    UniH7.DEF = None
    p_ = w_ev({"a": "gk:13", "t": str(WS.tok)}, "OLD7 SPAWN no main world")
    K.check(cap4(p_) == "The main world is not loaded" and not bool(WS.closed) and not bool(WS.spawnWait), "OLD7 SPAWN no main world = a caption")
    UniH7.DEF = E.W1
    p_ = w_ev({"a": "gk:13", "t": str(WS.tok)}, "OLD7 SPAWN no spawn provider")
    K.check(cap4(p_) == "The main world has no spawn point" and not bool(WS.spawnWait), "OLD7 SPAWN a main world without a spawn provider = a caption, nothing waits (%s)" % cap4(p_))
    UniH7.DEF = def7_
    WS.spawnWait = True
    p_ = w_ev({"a": "gk:13", "t": str(WS.tok)}, "OLD7 SPAWN pressed again while it runs")
    K.check(cap4(p_) == "On the way to Spawn - one moment", "OLD7 SAFE a second Spawn press while the first runs = a caption, no second trip")
    # the spawn point's answer: WorldSpawn hops to the world the player pressed in (queued there), then spawnResolved on that thread
    WSPc = JV("WorldSpawn")
    try:
        home7_ = JClass(PH + "server.core.universe.Universe").get().getWorld(PK.pr.getWorldUuid())
    except Exception:
        home7_ = None
    if home7_ is not None:
        ws7_ = WSPc(WS, PK.pr, E.W1, home7_)
        ws7_.accept(None, JClass("java.lang.RuntimeException")("harness: no spawn point"))
        K.check(ws7_.error is not None and E.queued(home7_)[-1:] == ["WorldSpawn"], "OLD7 SPAWN the future's answer is queued on the player's world (never run on the future's thread)")
        f7_ = len(E.sent(PK))
        E.run_world(home7_)
        p7_ = pages(PK, f7_)
        K.check(len(p7_) == 1 and "could not be found" in cap4(p7_[0]) and not bool(WS.spawnWait) and not bool(WS.closed),
                "OLD7 SPAWN an error = the caption on the open screen (ONE packet), nothing waits")
        WS.spawnWait = True
        ws8_ = WSPc(WS, PK.pr, E.W1, E.W2 if home7_ != E.W2 else E.W1)
        ws8_.run()
        K.check(not bool(WS.spawnWait), "OLD7 SPAWN the player changed world meanwhile = nothing to do, nothing waits")
    else:
        K.notes.append("OLD7 SPAWN the harness Universe has no world for the player's world UUID - WorldSpawn.run checked through spawnResolved only")
        WS.spawnWait = True
        WSPc(WS, PK.pr, E.W1, E.W2).run()
        K.check(not bool(WS.spawnWait), "OLD7 SPAWN another world = nothing to do, nothing waits")
    f7_ = len(E.sent(PK))
    WS.spawnResolved(PK.ref, PK.st, E.W1, None, None)
    p7_ = pages(PK, f7_)
    K.check(len(p7_) == 1 and cap4(p7_[0]) == "The main world has no spawn point." and not bool(WS.closed), "OLD7 SPAWN no spawn point = the caption")
    if w4_ is not None:
        TRF7 = JClass("com.hypixel.hytale.math.vector.Transform")
        WS7 = WTB.openAt(PW4.ref, st4_, PW4.pr, "test", 5, "")
        E.pump(PW4)
        st4_.row(PW4.ref).remove(TPc_.getComponentType())
        WS7.spawnResolved(PW4.ref, st4_, E.W1, TRF7(), None)
        tp7_ = st4_.getComponent(PW4.ref, TPc_.getComponentType())
        K.check(bool(WS7.closed) and tp7_ is not None, "OLD7 SPAWN a spawn point = the engine Teleport component on the player (MenuPage.moveTo's calls), the screen closed first")
        WS8 = WTB.openAt(PW4.ref, st4_, PW4.pr, "test", 5, "")
        E.pump(PW4)
        f8_ = len(E.sent(PW4))
        WS8.spawnResolved(PW4.ref, st4_, E.W1, TRF7(), None)
        p8_ = pages(PW4, f8_)
        K.check(len(p8_) == 1 and "already teleporting" in cap4(p8_[0]) and not bool(WS8.closed), "OLD7 SAFE a spawn point while a teleport is pending = a caption, no second trip")
        WS8.handleDataEvent(PW4.ref, st4_, '{"a":"close"}')
        st4_.row(PW4.ref).remove(TPc_.getComponentType())
        f8_ = len(E.sent(PW4))
        WS8.spawnResolved(PW4.ref, st4_, E.W1, TRF7(), None)
        K.check(st4_.getComponent(PW4.ref, TPc_.getComponentType()) is not None and not pages(PW4, f8_),
                "OLD7 SPAWN the screen closed meanwhile = the trip + the chat line, no page touched")
        st4_.row(PW4.ref).remove(TPc_.getComponentType())
    else:
        K.notes.append("OLD7 SPAWN no loaded-world player (TAB4 could not make one) - the trip itself unchecked")
    # ---- the old page's other states: a missing command, a warp list still loading, no warps at all, places that are gone
    WS, p_ = t_open("OLD7 reopen")
    cmdh7_ = E.CM.cmds.remove("hub")
    p_ = w_ev({"a": "vrf"}, "OLD7 no /hub")
    cm = cmap(p_)
    K.check(nm7(cm, 12) == "Hub (not on this server)" and not vis4(cm, "GvT12B") and not bind6(p_, "gk:12"), "OLD7 FALL no /hub = the card greyed, no Go")
    l1_ = len(lines4())
    p_ = w_ev({"a": "gk:12", "t": str(WS.tok)}, "OLD7 SAFE a forged Go on the greyed hub")
    K.check(cap4(p_) == str(WTD.NONE) and len(lines4()) == l1_, "OLD7 SAFE a Go that was not drawn = a caption, no command")
    E.CM.cmds.put("hub", cmdh7_)
    G2 = list(G0)
    G2[0], G2[1], G2[2] = "warp:" + WN7[0], "zhome:gone1", "ihome:gone2"
    ML.put(uu7, "SkyyCraftA", 1, _JA(JS)(G2))
    p_ = w_ev({"a": "vrf"}, "OLD7 a pinned warp + two gone places")
    cm = cmap(p_)
    K.check(nm7(cm, 0) == WN7[0] and not vis4(cm, "GvT1") and not vis4(cm, "GvT2") and nm7(cm, 15) == "Island home Farm",
            "OLD7 PAGE a pinned warp on its slot; a home / island home that is gone = hidden (the old page's rule)")
    TPB7 = []
    for f_ in TPPc.class_.getDeclaredFields():
        f_.setAccessible(True)
        if not ModC_.isStatic(f_.getModifiers()) and str(f_.getType().getName()) == "boolean":
            TPB7.append((f_, bool(f_.getBoolean(tpi_))))
            f_.setBoolean(tpi_, False)
        elif not ModC_.isStatic(f_.getModifiers()) and str(f_.getType().getName()) == "java.util.concurrent.atomic.AtomicBoolean":
            TPB7.append((f_, None))
            f_.get(tpi_).set(False)
    p_ = w_ev({"a": "vrf"}, "OLD7 the warp list still loading")
    cm = cmap(p_)
    K.check(not bool(TPPc.get().isWarpsLoaded()) and nm7(cm, 0) == WN7[0] and txt6(cm, "GvT0S") == "The warp list is still loading" and not vis4(cm, "GvT0B")
            and txt6(cm, "GvH") == str(WTD.GVHEAD), "OLD7 FALL a pinned warp while the warp list loads = greyed, no Go")
    ML.put(uu7, "SkyyCraftA", 1, _JA(JS)(G0))
    p_ = w_ev({"a": "vrf"}, "OLD7 loading, nothing pinned")
    K.check(txt6(cmap(p_), "GvH") == str(WTD.GVLOAD), "OLD7 FALL the warp list loading = the head line says so (the old page's tile)")
    for f_, v_ in TPB7:
        if v_ is None:
            f_.get(tpi_).set(True)
        else:
            f_.setBoolean(tpi_, v_)
    WB7 = JClass("java.util.HashMap")(WARPS)
    WARPS.clear()
    p_ = w_ev({"a": "vrf"}, "OLD7 no warps")
    K.check(txt6(cmap(p_), "GvH") == str(WTD.GVNOWARP) and txt6(cmap(p_), "GvC") == "5 places", "OLD7 FALL no warps at all = the /warpadmin line (%s)" % txt6(cmap(p_), "GvC"))
    WARPS.putAll(WB7)
    # ---- ARRANGE (the old page's Arrange; saved per account at once, MenuLayout part 1)
    p_ = w_ev({"a": "gar", "t": str(WS.tok)}, "OLD7 ARR Arrange")
    cm = cmap(p_)
    K.check(bool(WS.gEdit) and txt6(cm, "GvT11B") == "Pick up" and txt6(cm, "GvT15B") == "Pick up" and nm7(cm, 0) == "Empty slot" and txt6(cm, "GvT0B") == "+ Add"
            and vis4(cm, "GvRs") and txt6(cm, "GvRs") == "Reset" and vis4(cm, "GvDn") and not vis4(cm, "GvAr") and not vis4(cm, "GvRm") and not vis4(cm, "GvSd")
            and not vis4(cm, "GvCd") and txt6(cm, "GvH") == str(WTD.GVEDIT) and cap4(p_).startswith("Arrange is on") and g7() == G0,
            "OLD7 ARR Arrange: every card = Pick up, an empty slot = + Add; Reset + Done (no admin buttons for a player); nothing saved yet")
    p_ = w_ev({"a": "gsd", "t": str(WS.tok)}, "OLD7 SAFE a forged Set default")
    K.check(cap4(p_) == str(WTD.NONE) and g7(UNO7) == DEF7, "OLD7 SAFE Set default not drawn (a player) = a caption, the server default unchanged")
    WS.gAllow = "|rs|dn|sd|cd|"
    p_ = w_ev({"a": "gsd", "t": str(WS.tok)}, "OLD7 SAFE Set default by a player whose drawing showed it")
    K.check(cap4(p_) == "Only admins can change the server default Travel order." and g7(UNO7) == DEF7, "OLD7 SAFE the admin node is re-checked on the press")
    p_ = w_ev({"a": "grm", "t": str(WS.tok)}, "OLD7 SAFE Remove with nothing picked up")
    K.check(cap4(p_) == str(WTD.NONE), "OLD7 SAFE Remove is drawn only after Pick up")
    p_ = w_ev({"a": "gk:11", "t": str(WS.tok)}, "OLD7 ARR Pick up Your island")
    cm = cmap(p_)
    K.check(int(WS.gSel) == 11 and nm7(cm, 11) == "[Moving] Your island" and txt6(cm, "GvT11B") == "Put back" and txt6(cm, "GvT12B") == "Swap here"
            and txt6(cm, "GvT0B") == "Move here" and txt6(cm, "GvT15B") == "Move here" and vis4(cm, "GvRm") and txt6(cm, "GvH").startswith("Moving Your island")
            and g7() == G0, "OLD7 ARR Pick up: Put back / Swap here (a pin) / Move here (an empty or auto slot); Remove shows; nothing saved")
    p_ = w_ev({"a": "gk:11", "t": str(WS.tok)}, "OLD7 ARR Put back")
    K.check(int(WS.gSel) == -1 and cap4(p_) == "Put back - nothing moved." and g7() == G0, "OLD7 ARR Put back = nothing moved")
    w_ev({"a": "gk:11", "t": str(WS.tok)}, "OLD7 ARR Pick up again")
    p_ = w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 ARR Move here (an empty slot)")
    G3 = list(G0)
    G3[0], G3[11] = "tp:island", None
    K.check(g7() == G3 and cap4(p_) == "Your island moved." and nm7(cmap(p_), 0) == "Your island", "OLD7 ARR Move here = moved + saved at once (%s)" % g7())
    w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 ARR Pick up Your island")
    p_ = w_ev({"a": "gk:12", "t": str(WS.tok)}, "OLD7 ARR Swap here (Hub)")
    G3[0], G3[12] = "tp:hub", "tp:island"
    K.check(g7() == G3 and cap4(p_) == "Your island and Hub swapped places.", "OLD7 ARR Swap here = swapped + saved")
    p_ = w_ev({"a": "gk:15", "t": str(WS.tok)}, "OLD7 ARR Pick up an auto place")
    G3[15] = "ihome:Farm"
    K.check(g7() == G3 and int(WS.gSel) == 15 and cap4(p_).startswith("Picked up Island home Farm"), "OLD7 ARR an auto place: pinned where it is, then picked up (the old page's rule)")
    p_ = w_ev({"a": "gk:1", "t": str(WS.tok)}, "OLD7 ARR Move the island home")
    G3[1], G3[15] = "ihome:Farm", None
    K.check(g7() == G3 and nm7(cmap(p_), 15) == "Home base", "OLD7 ARR moved; the auto places move up into the free slots (%s)" % nm7(cmap(p_), 15))
    # SAFE: the saved order changed behind the drawing (another screen / the old page) = said, drawn again, nothing moved
    G4 = list(G3)
    G4[2], G4[1] = "ihome:Farm", None
    ML.put(uu7, "SkyyCraftA", 1, _JA(JS)(G4))
    p_ = w_ev({"a": "gk:1", "t": str(WS.tok)}, "OLD7 SAFE a pick on a changed order")
    K.check(cap4(p_) == str(WTD.GVSTALE) and g7() == G4 and int(WS.gSel) == -1 and nm7(cmap(p_), 2) == "Island home Farm", "OLD7 SAFE the order changed behind the drawing = said, drawn again, nothing moved")
    p_ = w_ev({"a": "gk:1", "t": "old"}, "OLD7 SAFE an older drawing")
    K.check("The page changed" in cap4(p_) and g7() == G4, "OLD7 SAFE a press from an older drawing = 'The page changed', nothing runs")
    # + Add: the places not in the order, Cancel, Add
    p_ = w_ev({"a": "gk:3", "t": str(WS.tok)}, "OLD7 ADD an empty slot's + Add")
    cm = cmap(p_)
    cand7 = ["Home base"] + WN7
    K.check(int(WS.gAddAt) == 3 and [nm7(cm, k_) for k_ in range(len(cand7))] == cand7 and txt6(cm, "GvT0B") == "Add" and vis4(cm, "GvCn") and not vis4(cm, "GvRs")
            and txt6(cm, "GvH") == str(WTD.GVADD) and txt6(cm, "GvC") == "%d to add" % len(cand7) and g7() == G4,
            "OLD7 ADD + Add = every place not in the order (homes, then warps A-Z; My Island / Hub / Spawn and the pinned island home left out); Cancel")
    p_ = w_ev({"a": "gcn", "t": str(WS.tok)}, "OLD7 ADD Cancel")
    K.check(int(WS.gAddAt) == -1 and cap4(p_) == "Nothing was added." and g7() == G4, "OLD7 ADD Cancel = nothing added")
    w_ev({"a": "gk:3", "t": str(WS.tok)}, "OLD7 ADD + Add again")
    p_ = w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 ADD Add Home base")
    G4[3] = "zhome:base"
    K.check(g7() == G4 and cap4(p_) == "Home base added." and int(WS.gAddAt) == -1, "OLD7 ADD Add = put in the slot + saved")
    w_ev({"a": "gk:4", "t": str(WS.tok)}, "OLD7 ADD + Add on slot 4")
    WS.gAddAt = 3   # the slot filled meanwhile (the drawing's slot is not free any more)
    p_ = w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 ADD the slot is not free any more")
    K.check(cap4(p_) == "That slot is not free any more - nothing was added." and g7() == G4, "OLD7 ADD a slot that is not free any more = nothing added")
    w_ev({"a": "gk:4", "t": str(WS.tok)}, "OLD7 ADD + Add on slot 4 again")
    WS.gKey[0] = "tp:hub"   # a place already in the order (the drawing's list cannot hold one - the bridge-side guard)
    p_ = w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 ADD a place already in the order")
    K.check(cap4(p_) == "Hub is in your Travel order already." and g7() == G4, "OLD7 ADD a place already in the order = not added twice")
    # Remove
    w_ev({"a": "gk:3", "t": str(WS.tok)}, "OLD7 REM Pick up Home base")
    p_ = w_ev({"a": "grm", "t": str(WS.tok)}, "OLD7 REM Remove")
    G4[3] = None
    K.check(g7() == G4 and cap4(p_).startswith("Home base removed") and int(WS.gSel) == -1, "OLD7 REM Remove = off the order + saved (a home comes back as an auto place)")
    # a move that cannot run (the picked slot is the target)
    w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 ARR Pick up Hub")
    WS.gSel = 5
    p_ = w_ev({"a": "gk:5", "t": str(WS.tok)}, "OLD7 ARR a move onto itself")
    K.check(cap4(p_) == "That move did not work - nothing moved." and g7() == G4, "OLD7 ARR a move that cannot run = said, nothing moved")
    # Reset: two presses; anything in between drops the arm
    p_ = w_ev({"a": "grs", "t": str(WS.tok)}, "OLD7 RESET first press")
    K.check(cap4(p_).startswith("Press Reset again") and txt6(cmap(p_), "GvRs") == "Click again to reset" and g7() == G4, "OLD7 RESET the first press asks (the button says Click again)")
    p_ = w_ev({"a": "vrf"}, "OLD7 RESET Refresh in between")
    K.check(txt6(cmap(p_), "GvRs") == "Reset" and WS.gArm is None, "OLD7 RESET Refresh drops the arm")
    p_ = w_ev({"a": "grs", "t": str(WS.tok)}, "OLD7 RESET first press again")
    K.check(g7() == G4 and cap4(p_).startswith("Press Reset again"), "OLD7 RESET the press after Refresh asks again")
    p_ = w_ev({"a": "grs", "t": str(WS.tok)}, "OLD7 RESET second press")
    K.check(g7() == DEF7 and cap4(p_) == "Back to the default Travel order.", "OLD7 RESET the same press again = back to the default order (%s)" % g7())
    # an auto place whose name a layout cannot save stays in the free slots
    mkwarp("bad name!")
    p_ = w_ev({"a": "vrf"}, "OLD7 a warp with a bad name")
    kb_ = card7(cmap(p_), "bad name!")
    p_ = w_ev({"a": "gk:%d" % kb_, "t": str(WS.tok)}, "OLD7 ARR Pick up the bad name")
    K.check(kb_ >= 15 and "can't be arranged" in cap4(p_) and g7() == DEF7, "OLD7 ARR an auto place a layout cannot save = said, it stays in the free slots (%d)" % kb_)
    WARPS.remove("bad name!")
    p_ = w_ev({"a": "gdn", "t": str(WS.tok)}, "OLD7 ARR Done")
    K.check(not bool(WS.gEdit) and cap4(p_) == "Saved - press Go to travel." and vis4(cmap(p_), "GvAr") and txt6(cmap(p_), "GvT11B" if nm7(cmap(p_), 11) else "GvT12B") == "Go",
            "OLD7 ARR Done = Go again")
    # pages: more auto places than the 10 free slots (the old page's < >); + Add 25 a page
    ZH7[:] = ["h%02d" % i_ for i_ in range(20)]
    ML.put(uu7, "SkyyCraftA", 1, _JA(JS)(G0))
    p_ = w_ev({"a": "vrf"}, "OLD7 PG 20 homes")
    cm = cmap(p_)
    na7 = 1 + 20 + len(WN7)
    K.check(vis4(cm, "GvP") and txt6(cm, "GvPg") == "Page 1 / %d" % ((na7 + 9) // 10) and nm7(cm, 15) == "Island home Farm" and nm7(cm, 16) == "Home h00",
            "OLD7 PG the auto places over the free slots, with < > (%s)" % txt6(cm, "GvPg"))
    p_ = w_ev({"a": "gpg:-1"}, "OLD7 PG before the first page")
    K.check(cap4(p_) == "This is the first page", "OLD7 PG before the first page = a caption")
    p_ = w_ev({"a": "gpg:1"}, "OLD7 PG page 2")
    K.check(txt6(cmap(p_), "GvPg").startswith("Page 2 /") and nm7(cmap(p_), 15) == "Home h09", "OLD7 PG > = the next 10 (%s)" % nm7(cmap(p_), 15))
    w_ev({"a": "gar", "t": str(WS.tok)}, "OLD7 PG Arrange")
    p_ = w_ev({"a": "gk:0", "t": str(WS.tok)}, "OLD7 PG + Add")
    cm = cmap(p_)
    K.check(txt6(cm, "GvPg") == "Page 1 / 2" and nm7(cm, 0) == "Island home Farm" and nm7(cm, 1) == "Home h00" and vis4(cm, "GvT24") and vis4(cm, "GvP"),
            "OLD7 PG + Add = 25 a page (%s)" % txt6(cm, "GvPg"))
    p_ = w_ev({"a": "gpg:1"}, "OLD7 PG + Add page 2")
    K.check(txt6(cmap(p_), "GvPg") == "Page 2 / 2" and int(WS.gAPage) == 1 and int(WS.gPage) >= 0, "OLD7 PG + Add > = its next page")
    w_ev({"a": "gcn", "t": str(WS.tok)}, "OLD7 PG Cancel")
    w_ev({"a": "gdn", "t": str(WS.tok)}, "OLD7 PG Done")
    ZH7[:] = ["base"]
    # an unreadable layout file is never changed (the old EDIT_WAIT)
    rec7_ = ML.OWN.get(str(uu7))
    ML.OWN.remove(str(uu7))
    ML.ERRAT.put(str(uu7), JClass("java.lang.Long")(JClass("java.lang.System").currentTimeMillis()))
    p_ = w_ev({"a": "vrf"}, "OLD7 an unreadable layout file")
    K.check(bool(ML.unreadable(uu7)) and txt6(cmap(p_), "GvH") == str(JV("MenuData").EDIT_WAIT), "OLD7 FALL an unreadable layout file = the old EDIT_WAIT line")
    p_ = w_ev({"a": "gar", "t": str(WS.tok)}, "OLD7 FALL Arrange on an unreadable file")
    K.check(not bool(WS.gEdit) and cap4(p_) == str(JV("MenuData").EDIT_WAIT), "OLD7 FALL Arrange refused while the file cannot be read")
    WS.gEdit = True
    WS.gAct[11] = 2
    WS.gKey[11] = "tp:island"
    p_ = w_ev({"a": "gk:11", "t": str(WS.tok)}, "OLD7 FALL a pick while the file cannot be read")
    K.check(cap4(p_) == str(JV("MenuData").EDIT_WAIT) and not bool(WS.gEdit), "OLD7 FALL a press that would save while the file cannot be read = refused, Arrange left")
    WS.gEdit = True
    WS.gAllow = "|rs|dn|"
    p_ = w_ev({"a": "grs", "t": str(WS.tok)}, "OLD7 FALL Reset while the file cannot be read")
    K.check(cap4(p_) == str(JV("MenuData").EDIT_WAIT), "OLD7 FALL Reset refused while the file cannot be read")
    ML.ERRAT.remove(str(uu7))
    if rec7_ is not None:
        ML.OWN.put(str(uu7), rec7_)
    WS.gEdit = False
    # leaving the view leaves Arrange
    WS, p_ = t_open("OLD7 reopen for the view change")
    w_ev({"a": "gar", "t": str(WS.tok)}, "OLD7 Arrange")
    w_ev({"a": "grs", "t": str(WS.tok)}, "OLD7 arm Reset")
    p_ = w_ev({"a": "vw:0"}, "OLD7 the World sub-tab")
    K.check(int(WS.view) == 0 and not bool(WS.gEdit) and WS.gArm is None and has6(p_, "SkyyWtabBody"), "OLD7 leaving the Travel view leaves Arrange, drops the arm (World = the cards)")
    p_ = w_ev({"a": "gk:11", "t": str(WS.tok)}, "OLD7 SAFE a travel press on the cards")
    K.check(cap4(p_) == str(WTD.NONE), "OLD7 SAFE a Travel view press while the cards show = a caption, no call")
    p_ = w_ev({"a": "vw:5"}, "OLD7 the Travel sub-tab")
    K.check(int(WS.view) == 5 and only7(p_), "OLD7 the Travel sub-tab = the Travel view")
    p_ = w_ev({"a": "trv"}, "OLD7 SAFE the home button inside the view")
    K.check(cap4(p_) == str(WTD.NONE), "OLD7 SAFE a home card's button inside a view = a caption")
    # ADMIN: Set default / Clear default (two presses, the admin node re-checked)
    PO7 = E.player(uid=E.OP, name="SkyyTravelOp")
    byU.put(PO7.pr.getUuid(), PO7.pr)
    K.check(bool(JV("MenuUtil").isAdmin(PO7.pr)), "OLD7 ADMIN the harness op is an admin")

    def o7_ev(pg_, obj):
        E.pump(PO7)
        f_ = len(E.sent(PO7))
        pg_.handleDataEvent(PO7.ref, PO7.st, json.dumps(obj))
        return (pages(PO7, f_) or [None])[0]
    GA = [None] * 25
    GA[0], GA[1] = "tp:spawn", "tp:island"
    ML.put(PO7.pr.getUuid(), "SkyyTravelOp", 1, _JA(JS)(GA))
    WA = WTB.openAt(PO7.ref, PO7.st, PO7.pr, "test", 5, "")
    E.pump(PO7)
    p_ = o7_ev(WA, {"a": "gar", "t": str(WA.tok)})
    cm = cmap(p_)
    K.check(vis4(cm, "GvSd") and vis4(cm, "GvCd") and txt6(cm, "GvSd") == "Set default", "OLD7 ADMIN Arrange shows Set default + Clear default to an admin")
    # fixer: the admin's order changes between the two Set default presses = the stale caption, the server default untouched
    p_ = o7_ev(WA, {"a": "gsd", "t": str(WA.tok)})
    GA2 = list(GA); GA2[2] = "tp:hub"
    ML.put(PO7.pr.getUuid(), "SkyyTravelOp", 1, _JA(JS)(GA2))
    p_ = o7_ev(WA, {"a": "gsd", "t": str(WA.tok)})
    K.check(cap4(p_) == str(WTD.GVSTALE) and g7(UNO7) == DEF7 and txt6(cmap(p_), "GvSd") == "Set default",
            "OLD7 FIX Set default refuses an order that changed between its two presses (nothing saved: %s)" % g7(UNO7))
    ML.put(PO7.pr.getUuid(), "SkyyTravelOp", 1, _JA(JS)(GA))
    p_ = o7_ev(WA, {"a": "gar", "t": str(WA.tok)}) if not vis4(cmap(p_), "GvSd") else p_
    p_ = o7_ev(WA, {"a": "gsd", "t": str(WA.tok)})
    K.check(cap4(p_).startswith("Press Set default again") and txt6(cmap(p_), "GvSd") == "Click again to set" and g7(UNO7) == DEF7, "OLD7 ADMIN Set default asks first")
    p_ = o7_ev(WA, {"a": "gsd", "t": str(WA.tok)})
    K.check(g7(UNO7) == GA and cap4(p_).startswith("Saved - every player without their own"), "OLD7 ADMIN Set default again = the admin's order is the server default (%s)" % g7(UNO7))
    p_ = o7_ev(WA, {"a": "gcd", "t": str(WA.tok)})
    K.check(cap4(p_).startswith("Press Clear default again") and txt6(cmap(p_), "GvCd") == "Click again to clear" and g7(UNO7) == GA, "OLD7 ADMIN Clear default asks first")
    p_ = o7_ev(WA, {"a": "gcd", "t": str(WA.tok)})
    K.check(g7(UNO7) == G0 and cap4(p_) == "The standard Travel order is the server default again.", "OLD7 ADMIN Clear default again = the built-in order (%s)" % g7(UNO7))
    if DEF7 != G0:
        ML.saveDefault(1, _JA(JS)(DEF7))
    ML.put(PO7.pr.getUuid(), "SkyyTravelOp", 1, None)
    WA.handleDataEvent(PO7.ref, PO7.st, '{"a":"close"}')
    byU.remove(PO7.pr.getUuid())
    ML.put(uu7, "SkyyCraftA", 1, None)
    WS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    E.pump(PK)
'''

HARNESS_OLD7_HUB = r'''    # OLD7 (0.3.75): the World > Teleport hub tab (other mods' tab strips: MenuHubOpen "teleport") = the old page while the old menu is ON,
    # the World screen's Travel view while it is OFF (never the old page)
    for on_, what_ in ((True, "ON"), (False, "OFF")):
        CFG.OLD_MENU = on_
        o_clear()
        f0_ = len(E.sent(PO))
        ok_ = bool(MH.openFor(PO.pr.getUuid(), "teleport"))
        cur_ = PO.pm.getCustomPage()
        ps_ = pages(PO, f0_)
        if on_:
            K.check(ok_ and o_cur() == "MenuPage" and len(ps_) == 1, "OLD7 HUBTAB old menu ON: World > Teleport = the old Teleport page as before (%s)" % o_cur())
        else:
            K.check(ok_ and o_cur() == "WorldTab" and int(cur_.view) == 5 and len(ps_) == 1 and has6(ps_[0], "SkyyWtabGv") and not has6(ps_[0], "SkyyWtabBody"),
                    "OLD7 HUBTAB old menu OFF: World > Teleport = the World screen's Travel view, ONE packet (%s)" % o_cur())
        E.pump(PO)
    o_clear()
'''

EXPECT_BODY = '''    "WorldTab": ["+f gAPage", "+f gAct", "+f gAddAt", "+f gAdmin", "+f gAllow", "+f gArm", "+f gDrawn", "+f gEdit", "+f gGoK", "+f gKey", "+f gPage",
                "+f gPages", "+f gSel", "+f spawnWait", "+m actGv", "+m fillGv", "+m gDraw", "+m gGo", "+m gHide", "+m gLook", "+m gName", "+m gNone",
                "+m gSave", "+m gStale", "+m moveTo", "+m navGv", "+m spawnGo", "+m spawnResolved", "~c ", "~m build", "~m goView", "~m handleDataEvent",
                "~m openAt", "~m vRefresh", "~m viewOf"],
    "WorldTabData": ["+f GN", "+f GVADD", "+f GVCAP", "+f GVEDIT", "+f GVHEAD", "+f GVLOAD", "+f GVNONE", "+f GVNOWARP", "+f GVSTALE", "~<clinit>"],
    "MenuHub": ["~m page"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
# ======================================================================= the HARNESS (every 0.3.74 check runs again on the 0.3.75 jar, plus OLD7)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.74 (old menu follow-up - the World tab's Quests / Collections / Explore / Island views; tools/menu_0_3_74_patch.py,''',
      '''"""Harness for SkyyMenu 0.3.75 (old menu follow-up - the World tab's Travel view = the old World > Teleport page; tools/menu_0_3_75_patch.py,
round oldmenu7). GENERATED by tools/menu_0_3_75_patch.py from the 0.3.74 harness (edit the patch, not this file): every 0.3.74 check runs again
on the 0.3.75 jar (TAB4: a forged Full page stays on the screen; OLD6's ratchet = 'stays gone'), plus
  OLD7 STATIC   the ratchet: OLD_LEFT lost world:teleport; no Full page / Teleport page link or text on the World screen; the hub tab route; a save
                only over the drawn order (MenuLayout part 1); Go = the drawn go key; Spawn = the engine's async spawn point; the build asserts
                the Travel view fits; the budget = the frame + the biggest section (+ T)
       HOME     no Full page; the Travel card's Travel button; a forged Full page = redrawn, no old page
       PAGE     your order (My Island | Hub | Spawn pinned, the auto places in rows 4 + 5: island homes, homes, warps A-Z), counts, the token on
                Go / Arrange, no scrolling, no metadata
       GO       /island, /hub (double click once), island:fn:gohome, essentials:fn:gohome, a warp (InvPage.warpGo), SPAWN (no main world, no
                provider, a second press, WorldSpawn queued on the player's world, an error, another world, no point, the Teleport component, a
                pending teleport, the screen closed meanwhile)
       FALL     no /hub (greyed, a forged Go refused), a pinned warp + gone places, the warp list loading, no warps, an unreadable layout file
       ARR      Arrange, Pick up / Put back / Move here / Swap here, an auto place pinned, a changed order refused, an older drawing, + Add / Cancel
                / Add, a slot not free / a place already there, Remove, a move onto itself, Reset (two presses, Refresh drops the arm), a bad
                name, Done, pages (auto + Add), leaving the view; ADMIN Set default / Clear default (two presses; a player's forged press refused,
                the node re-checked)
       HUBTAB   World > Teleport = the old page (old menu ON) / the Travel view (OFF)
       every new packet: every b.set / append / binding names an element drawn in that packet (the frame + ONE section)
The 0.3.74 harness text follows:
Harness for SkyyMenu 0.3.74 (old menu follow-up - the World tab's Quests / Collections / Explore / Island views; tools/menu_0_3_74_patch.py,''')
T.rep('VERSION = "0.3.74"\nJAR', 'VERSION = "0.3.75"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.73.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.74.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.73.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.74.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_74_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_75_patch.py")')
T.rep('"scratch", "oldmenu6", "menu"', '"scratch", "oldmenu7", "menu"')
T.rep('ADDED = []   # 0.3.74: no new class\n', 'ADDED = ["WorldSpawn"]   # 0.3.75: the Travel view\'s Spawn (the spawn point -> the player\'s world thread)\n')
EXPECT_75 = '''EXPECT = {   # 0.3.75: the World tab's Travel view, the hub tab route (MenuHub.page), the version strings
@@EXPECT@@
}
'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.74:', 'if "--expect-dump" in sys.argv:'), EXPECT_75.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.74"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.75"') == 1, "S VERSION")
''' + HARNESS_OLD7_STATIC.rstrip("\n"))
# OLD6's ratchet compared 0.3.74 with 0.3.73: against 0.3.74 it is OLD7's (above) - its four rows stay gone; its budget line now names T too
T.rep('''    K.check(lefto_ - left2_ == set([("world", "quests"), ("world", "explore"), ("world", "island"), ("character", "collections")]) and not (left2_ - lefto_)
            and len(left2_) == len(lefto_) - 4,
            "OLD6 RATCHET OLD_LEFT lost world:quests + world:explore + world:island + character:collections, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(not (left2_ & set([("world", "quests"), ("world", "explore"), ("world", "island"), ("character", "collections")])),
            "OLD6 RATCHET (0.3.75: vs 0.3.74) world:quests + world:explore + world:island + character:collections stay gone")''')
T.rep('''    K.check(mw6_ is not None and int(mw6_.group(1)) <= 800 and 'WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEI")' in g,''',
      '''    K.check(mw6_ is not None and int(mw6_.group(1)) <= 800 and 'WT_ELEMENTS = _wt_by["0"] + max(_wt_by[_s] + _wt_rt[_s] for _s in "HQCEIT")' in g,   # 0.3.75: + T''')
# TAB4: the Full page is gone (a forged one stays on the screen); Travel opens the Travel view (each still ONE packet); then OLD7
T.rep('''    # links (each ONE packet): Full page = the old Teleport page (OLD_LEFT world:teleport); 0.3.74: the rest open this screen's views
    for a_, what in (("full", "Full page"), ("isl", "Island settings (0.3.74: the island view)"), ("exp", "Explore (0.3.74: the explore view)"),''',
      '''    # links (each ONE packet): 0.3.75: no Full page (a forged one = redrawn); 0.3.74: the rest open this screen's views; 0.3.75: Travel = the travel view
    for a_, what in (("full", "a forged Full page (0.3.75: gone)"), ("trv", "Travel (0.3.75: the travel view)"), ("isl", "Island settings (0.3.74: the island view)"), ("exp", "Explore (0.3.74: the explore view)"),''')
T.rep('''    # TABS
    WS, p_ = w_open("TAB4 reopen for tabs")''', HARNESS_OLD7.rstrip("\n") + '''
    # TABS
    WS, p_ = w_open("TAB4 reopen for tabs")''')
T.rep('''    # FIX (Skyy "remove the old "Full tree""): the Right now 'unspent tree points' row = that skill's page (its inline tree), Class = Combat''',
      HARNESS_OLD7_HUB + '''    # FIX (Skyy "remove the old "Full tree""): the Right now 'unspent tree points' row = that skill's page (its inline tree), Class = Combat''')
if T.dst:
    T.finish()
