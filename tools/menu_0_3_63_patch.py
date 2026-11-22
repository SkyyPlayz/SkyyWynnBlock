"""Derive SkyyMenu/build_skyymenu_0.3.63.py + SkyyMenu/test_skyymenu_0.3.63.py from the SET pin SkyyMenu 0.3.62 (generated - never re-run
its patch). Run:  python tools/menu_0_3_63_patch.py   then   python SkyyMenu/build_skyymenu_0.3.63.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.63.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run).

0.3.63 (2026-11-22, round tab5) = TAB SCREENS ROUND 5: THE SOCIAL TAB - ONE SCREEN (Players online + You + Profiles + Party + Guild).
Skyy's words: 11-14 popup on research/ui-theme-art/tab-plan.png (12 tabs -> 7) "Yes, both"; 11-21 "build and deploy everything on your list",
"pc is back on if you wana keep building". Approved art: research/ui-theme-art/social-page.png + README 'Tab pages' (Social = PLAYERS ONLINE +
YOU + PROFILES + PARTY + GUILD) and the nothing-lost table (Character > Stats -> Social (your profile card); Character > Profiles -> Social;
Social > Players, Party, Guild -> Social). No new picture (tools/ci/ui_budget.py unchanged: this jar ships no new picture; no class emblems).
SURVEY: vanilla has no social / profile screen; no pack mod draws one. The screen reads ONLY bridges that already exist (no other mod changes):
  SkyyProfiles 0.1.18 profile:list:<uuid> ("1:Main:Archer,2:Iron:Warrior"), profile:<uuid> (the active id), profile:busy:<uuid>,
  profile:fn:key; SkyyParty 0.1.10 party:fn:members, party:name:<uuid>, party:stats:<uuid>; SkyyGuilds 0.1.13 guild:info:<uuid>,
  guild:fn:online; the Stats page's own reads (StatsCalc: class, profile name, Overall, skills, the Main tab rows, the Profile tab rows); the
  engine's online players.
  1. THE SOCIAL TAB of the inventory's top bar (and the skill page's / pets screen's / market screen's / world screen's Social tab) opens the
     new SOCIAL SCREEN (SocialTab: an inline Skyglass page, kit tools/skyyui.py, the inventory's frame + the same 7-tab top bar with Social
     selected; coins in the bar):
     LEFT   PLAYERS ONLINE (everyone online but you, A-Z, 10 a page: name, class + Overall, where they are, "in your party"; Pick) and the
            PICKED player with the 7 actions of the old Players page (Ask to TP, Bring here, Visit island, Party invite, Guild invite,
            Island invite, Let build) - each runs the SAME command line as the old page (MenuData.PA_CMD with the name, PA_CLOSE), after the
            same checks (the command exists, the server's version has the subcommand, the player's permission for it) - plus Trade (fix
            round: Skyy's LOCKED 2026-10-10 social ask "invite to party, add friend, ... message and trade") = SkyyEssentials' own
            /trade <name> (a request only, the page stays) through the same checks
     MIDDLE YOU (your name, class, profile, Overall + class skill, 10 skills, the Stats page's first 8 Main rows with gear on, purse / bank /
            charms / recipes; Stats page = the old Character > Stats page) | PROFILES (your profiles, ACTIVE marked; Switch -> a Confirm row ->
            the page closes and /profiles switch <number> runs as you - SkyyProfiles' own command with every refusal it has (combat, dead,
            busy, rebirth); Profiles page = the old page for New / Rename / Delete / Restore)
     RIGHT  PARTY (members, leader, health bar + where from party:stats; Leave party = /party leave; Party page = the old page for Accept /
            Kick / Promote / Disband / invite by name; after Leave the caption says the card updates on the next click - the command
            runs after our redraw) | GUILD (name, tag, level, rank, members, XP bar, who is online; Guild page)
     This page holds a page token: a Pick / action / Switch / Confirm / Leave from an older drawing = "The page changed" (nothing runs); the
     profile key of the drawing is checked too (a profile switch = "Your profile changed", drawn again, nothing runs); a command that does
     not close the page draws it again (a new token), so a double click never runs it twice.
  2. FALLBACK: the screen always opens; each card says so when its mod is not on the server ("... not on this server right now"); an action
     whose command is missing / too old / not allowed = the old page's caption. 'Full page' (top bar) = today's Social > Players page.
  NOT BUILT (next rounds, nothing half-wired): search + All / Friends / Nearby filters (no friends system exists), class emblems (art),
  another player's full profile card in the YOU spot (README question 5 - needs their live stats; the picked line shows class / Overall /
  where), Message + Add friend (Skyy's LOCKED 10-10 ask: /msg needs a typed text box, a Hytale friend needs an engine read / call - a
  design question for Skyy), party loot / XP share (no such setting in SkyyParty), the guild
  MOTD + guild quest (no SkyyGuilds read), Guild chat (a typed message - the Guild page / /gc), island co-op members (World > Island settings).
  New classes SocialTabData + SocialTab; no command, no setting, no lang key, no system, no saved data, no picture.
  ROLLBACK to 0.3.62: safe alone (nothing saved; the Social tab opens the old Social hub again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.62.py"), os.path.join(MOD, "build_skyymenu_0.3.63.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.62.py"), os.path.join(MOD, "test_skyymenu_0.3.63.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.62"\n') and P.has("tools/menu_0_3_62_patch.py") and P.has("WorldTab")
assert not P.has("SocialTab"), "not the generated SkyyMenu 0.3.62 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.62: THE WORLD TAB = ONE SCREEN''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.63: THE SOCIAL TAB = ONE SCREEN (SocialTab: PLAYERS ONLINE - A-Z, Pick, the old Players page's 7 actions as the same command lines + Trade;
       YOU - name, class, profile, Overall, skills, the Stats page's Main rows, purse / bank; PROFILES - Switch + Confirm = /profiles switch;
       PARTY - members with health + Leave party; GUILD - level, rank, XP, who is online. 'Full page' = the old Social > Players page)
       (notes: tools/menu_0_3_63_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.63.py.
0.3.62: THE WORLD TAB = ONE SCREEN''')
P.rep('VERSION = "0.3.62"\n', 'VERSION = "0.3.63"\n')

# ---------- (1) the SOCIAL SCREEN markup (one page data list drawn by SocialTab.build)
SC_PAGE = r'''
# ================= 0.3.63 THE SOCIAL TAB: ONE SCREEN (tools/menu_0_3_63_patch.py; approved art research/ui-theme-art/social-page.png; popup 11-14
# "Yes, both" on the 7 tabs) =================
# The inventory's frame and top bar (Social selected); LEFT: Players online + the picked player's actions; MIDDLE: You | Profiles;
# RIGHT: Party | Guild.
SC = "SkyyStab"
SC_L, SC_M = 520, 560
SC_R = IV_IW - SC_L - SC_M - 2 * IV_GAP                     # 456
SC_LI, SC_MI, SC_RI = SC_L - 20, SC_M - 20, SC_R - 20
SC_YH = 510
SC_FH = IV_BODY_H - SC_YH - 8                               # 326
SC_PH = 410
SC_GH = IV_BODY_H - SC_PH - 8                               # 426
SC_PN, SC_RH = 10, 48                                       # the players list: 10 a page (nothing scrolls)
SC_PKW = 80
SC_RXW = SC_LI - 16 - SC_PKW - 8                            # a player row's text column
SC_AW = 118                                                 # an action button
SC_PA = ["Ask to TP", "Bring here", "Visit island", "Party invite", "Guild invite", "Island invite", "Let build", "Trade"]
SC_XCMD = ["trade %P"]                                      # fix: SkyyEssentials' /trade <player> (a request; the page stays open)
assert len(SC_PA) == len(PA) + len(SC_XCMD), "0.3.63: the old page's 7 actions + Trade"
assert [a_[5] for a_ in PA] == ["tpa %P", "tpahere %P", "island visit %P", "party invite %P", "guild invite %P", "island invite %P",
                                "island trust %P"], "0.3.63: the 7 actions = the old Players page's PLAYER_ACTIONS, in order"
SC_KN, SC_VN = 10, 8                                        # skills shown (2 x 5), stats shown (2 x 4)
SC_CW = (SC_MI - 20) // 2                                   # a skill / stat cell (260)
SC_FN = 4                                                   # profiles shown
SC_MN = 5                                                   # party members shown
SC_GN = 8                                                   # guild members online shown
SC_BARW = SC_RI - 16                                        # a member's health bar
SC_GBW = SC_RI                                              # the guild XP bar
SC_TXT = {
    "cap0": "Pick a player for their actions. Tabs on top.",
    "anote": "Same commands as the old Players page, plus /trade.",
    "left": "/party leave  - see your chat. The party card updates on your next click.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in SC_TXT.values() for c_ in v_), "0.3.63: plain texts"
assert SUI.text_width(SC_TXT["anote"], 12) <= SC_LI, "0.3.63: the actions note fits"
for _l in SC_PA:
    assert SUI.text_width(_l, 13, bold=True) <= SC_AW - 12, ("0.3.63: an action label fits", _l)
assert 4 * SC_AW + 3 * 4 <= SC_LI, "0.3.63: four actions fit a row"
# the run-time markup: a member's health fill, the guild XP fill
SC_FILLH = "Group { Anchor: (Width: {W}, Height: 6); Background: %s; }" % SUI.glass_col("health")
SC_FILLX = "Group { Anchor: (Width: {W}, Height: 8); Background: %s; }" % SUI.glass_col("xp")
for _mk in (SC_FILLH.replace("{W}", "40"), SC_FILLX.replace("{W}", "40")):
    SUI.check_markup(_mk, prefix=SC, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.63: a run-time markup line Java can hold"


def _sc_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label

    def holder(parent, ident, w, h, size, cols, anchor=None, bold=False):
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, c_, bold=bold, w=w, h=h)) for k_, c_ in enumerate(cols)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)

    def head(parent, ident, title, w, right_w):
        hd = SC + ident
        ap.append(("#" + parent, G_.glass_group(hd, w, 24, layout="Left")))
        ap.append(("#" + hd, lab(None, title, 15, "accentHi", bold=True, w=w - right_w, h=24)))
        return hd
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (SC, IV_PAGE_W, IV_PAGE_H)))
    win = SC + "Win"
    ap.append(("#" + SC, G_.glass_group(win, IV_W, IV_FRAME_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": IV_FRAME_TOP})))   # under the top bar (0.3.60)
    # ---- the top bar: the same 7 tabs (Social selected), Full page, coins, the X
    top = SC + "Top"
    ap.append(iv_bar(G_, "#" + SC, top))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (SC, i), lb, "tabSelected" if i == 5 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(SC + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(SC + "Coins", "", 14, "xp", bold=True, w=cw_, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(SC + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    body = SC + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Left")))
    # ======== LEFT: PLAYERS ONLINE (the old Social > Players page) + the picked player's actions
    pl = SC + "Pl"
    ap.append(("#" + body, G_.glass_group(pl, SC_L, IV_BODY_H, role="panel", layout="Top", pad=10)))
    ph = head(pl, "Ph", "PLAYERS ONLINE", SC_LI, 160)
    ap.append(("#" + ph, lab(SC + "Pc", "", 12, "green", bold=True, w=160, h=24, halign="End")))
    ls = SC + "Ls"
    ap.append(("#" + pl, G_.glass_group(ls, SC_LI, SC_PN * (SC_RH + 6), layout="Top", anchor={"top": 8})))
    for k_ in range(SC_PN):
        rw = "%sR%d" % (SC, k_)
        ap.append(("#" + ls, G_.glass_group(rw, SC_LI, SC_RH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 6})))
        rx = rw + "X"
        ap.append(("#" + rw, G_.glass_group(rx, SC_RXW, SC_RH, layout="Top", anchor={"right": 8})))
        holder(rx, rw + "N", SC_RXW, 24, 15, ["row", "accentHi"], anchor={"top": 3}, bold=True)
        ap.append(("#" + rx, lab(rw + "S", "", 11, "dim", w=SC_RXW, h=18)))
        ap.append(("#" + rw, G_.glass_button(rw + "P", "Pick", "secondary", w=SC_PKW, h=30, size=13, anchor={"top": 9})))
    assert 16 + SC_RXW + 8 + SC_PKW <= SC_LI, "0.3.63: a player row fits"
    pr_ = SC + "Pr"
    ap.append(("#" + pl, G_.glass_group(pr_, SC_LI, 28, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pr_, G_.glass_button(SC + "Pp", "<", "secondary", w=36, h=26, size=14, anchor={"right": 4})))
    ap.append(("#" + pr_, lab(SC + "Pg", "", 12, "text", bold=True, w=110, h=26, halign="Center")))
    ap.append(("#" + pr_, G_.glass_button(SC + "Pn", ">", "secondary", w=36, h=26, size=14, anchor={"left": 4})))
    ap.append(("#" + pl, lab(SC + "St", "", 17, "title", bold=True, w=SC_LI, h=26, anchor={"top": 10})))
    ap.append(("#" + pl, lab(SC + "Ss", "", 13, "text", w=SC_LI, h=20)))
    for r_, ks_ in ((1, range(0, 4)), (2, range(4, len(SC_PA)))):
        ar = "%sAr%d" % (SC, r_)
        ap.append(("#" + pl, G_.glass_group(ar, SC_LI, 34, layout="Left", anchor={"top": 8 if r_ == 1 else 6})))
        for k_ in ks_:
            ap.append(("#" + ar, G_.glass_button("%sA%d" % (SC, k_), SC_PA[k_], "primary" if k_ == 3 else "secondary", w=SC_AW, h=34, size=13,
                                                 anchor={"right": 4})))
    ap.append(("#" + pl, lab(SC + "An", "", 12, "dim", w=SC_LI, h=18, anchor={"top": 6})))
    ap.sets.append((SC + "An", "Text", SC_TXT["anote"]))
    assert 20 + 24 + 8 + SC_PN * (SC_RH + 6) + 6 + 28 + 10 + 26 + 20 + 8 + 34 + 6 + 34 + 6 + 18 <= IV_BODY_H, "0.3.63: the players panel fits"
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== MIDDLE: YOU (the Stats page's reads) | PROFILES (SkyyProfiles)
    md = SC + "Md"
    ap.append(("#" + body, G_.glass_group(md, SC_M, IV_BODY_H, layout="Top")))
    yu = SC + "Yu"
    ap.append(("#" + md, G_.glass_group(yu, SC_M, SC_YH, role="panel", layout="Top", pad=10)))
    ap.append(("#" + yu, lab(None, "YOU", 15, "accentHi", bold=True, w=SC_MI, h=24)))
    ap.append(("#" + yu, lab(SC + "Yn", "", 20, "title", bold=True, w=SC_MI, h=30, anchor={"top": 6})))
    ap.append(("#" + yu, lab(SC + "Y2", "", 14, "accentHi", bold=True, w=SC_MI, h=22)))
    ap.append(("#" + yu, lab(SC + "Y3", "", 13, "xp", bold=True, w=SC_MI, h=22)))

    def cells(title, letter, n, rows_):
        ap.append(("#" + yu, lab(None, title, 12, "dim", bold=True, w=SC_MI, h=18, anchor={"top": 8})))
        gr = SC + letter + "g"
        ap.append(("#" + yu, G_.glass_group(gr, SC_MI, rows_ * 24, layout="Left")))
        for c_ in range(2):
            col_ = "%s%sc%d" % (SC, letter, c_)
            ap.append(("#" + gr, G_.glass_group(col_, SC_CW, rows_ * 24, layout="Top", anchor={"right": 20} if c_ == 0 else None)))
            for r_ in range(rows_):
                k_ = c_ * rows_ + r_
                ce = "%s%s%d" % (SC, letter, k_)
                ap.append(("#" + col_, G_.glass_group(ce, SC_CW, 24, layout="Left")))
                ap.append(("#" + ce, lab(ce + "N", "", 14, "text", w=SC_CW - 64, h=24, anchor={"right": 4})))
                ap.append(("#" + ce, lab(ce + "L", "", 14, "xp", bold=True, w=60, h=24, halign="End")))
        assert n == 2 * rows_
    cells("SKILLS", "K", SC_KN, SC_KN // 2)
    cells("STATS - GEAR ON", "V", SC_VN, SC_VN // 2)
    ap.append(("#" + yu, lab(None, "PROGRESS", 12, "dim", bold=True, w=SC_MI, h=18, anchor={"top": 8})))
    ap.append(("#" + yu, lab(SC + "P1", "", 13, "text", w=SC_MI, h=20)))
    ap.append(("#" + yu, lab(SC + "P2", "", 13, "text", w=SC_MI, h=20)))
    ap.append(("#" + yu, G_.glass_button(SC + "Ystats", "Stats page", "secondary", w=160, h=34, size=14, anchor={"top": 10})))
    assert 20 + 24 + 36 + 22 + 22 + 26 + SC_KN // 2 * 24 + 26 + SC_VN // 2 * 24 + 26 + 40 + 44 <= SC_YH, "0.3.63: the you card fits"
    assert 2 * SC_CW + 20 <= SC_MI, "0.3.63: two cell columns fit"
    fp = SC + "Pf"
    ap.append(("#" + md, G_.glass_group(fp, SC_M, SC_FH, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    fh = head(fp, "Fh", "PROFILES", SC_MI, 200)
    ap.append(("#" + fh, lab(SC + "Fc", "", 12, "xp", bold=True, w=200, h=24, halign="End")))
    ap.append(("#" + fp, "Group { Anchor: (Height: 8); }"))
    for k_ in range(SC_FN):
        fr = "%sF%d" % (SC, k_)
        ap.append(("#" + fp, G_.glass_group(fr, SC_MI, 38, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 4})))
        ap.append(("#" + fr, lab(fr + "N", "", 14, "row", bold=True, w=SC_MI - 16 - 100 - 100 - 8, h=38, anchor={"right": 8})))
        ap.append(("#" + fr, lab(fr + "A", "ACTIVE", 12, "green", bold=True, w=100, h=38, halign="Center")))
        ap.append(("#" + fr, G_.glass_button(fr + "W", "Switch", "primary", w=100, h=28, size=13, anchor={"top": 5})))
    fq = SC + "Fq"
    ap.append(("#" + fp, G_.glass_group(fq, SC_MI, 30, layout="Left", anchor={"top": 4})))
    ap.append(("#" + fq, lab(SC + "FqT", "", 13, "action", bold=True, w=SC_MI - 100 - 90 - 12, h=30, anchor={"right": 8})))
    ap.append(("#" + fq, G_.glass_button(SC + "Fyes", "Confirm", "primary", w=100, h=28, size=13, anchor={"right": 4})))
    ap.append(("#" + fq, G_.glass_button(SC + "Fno", "Cancel", "secondary", w=90, h=28, size=13)))
    fb = SC + "Fb"
    ap.append(("#" + fp, G_.glass_group(fb, SC_MI, 34, layout="Left", anchor={"top": 8})))
    ap.append(("#" + fb, lab(SC + "Fnote", "", 12, "dim", w=SC_MI - 170, h=34, anchor={"right": 10})))
    ap.append(("#" + fb, G_.glass_button(SC + "Fpage", "Profiles page", "secondary", w=160, h=34, size=14)))
    assert 20 + 24 + 8 + SC_FN * 42 + 34 + 42 <= SC_FH, "0.3.63: the profiles card fits"
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== RIGHT: PARTY (SkyyParty) | GUILD (SkyyGuilds)
    rt = SC + "Rt"
    ap.append(("#" + body, G_.glass_group(rt, SC_R, IV_BODY_H, layout="Top")))
    pa = SC + "Pa"
    ap.append(("#" + rt, G_.glass_group(pa, SC_R, SC_PH, role="panel", layout="Top", pad=10)))
    ah = head(pa, "Ah", "PARTY", SC_RI, 200)
    ap.append(("#" + ah, lab(SC + "Ac", "", 12, "xp", bold=True, w=200, h=24, halign="End")))
    ap.append(("#" + pa, "Group { Anchor: (Height: 8); }"))
    for k_ in range(SC_MN):
        mr = "%sM%d" % (SC, k_)
        ap.append(("#" + pa, G_.glass_group(mr, SC_RI, 50, role="inset", layout="Top", pad={"horizontal": 8}, anchor={"bottom": 4})))
        ml = mr + "L"
        ap.append(("#" + mr, G_.glass_group(ml, SC_RI - 16, 22, layout="Left", anchor={"top": 2})))
        ap.append(("#" + ml, lab(mr + "N", "", 14, "row", bold=True, w=SC_RI - 16 - 110, h=22)))
        ap.append(("#" + ml, lab(mr + "T", "", 12, "xp", bold=True, w=110, h=22, halign="End")))
        ap.append(("#" + mr, lab(mr + "S", "", 11, "dim", w=SC_RI - 16, h=16)))
        ap.append(("#" + mr, 'Group #%sB { Anchor: (Width: %d, Height: 6, Top: 2); LayoutMode: Left; Background: %s; }' % (mr, SC_BARW, IV_TRACK)))
    ap.append(("#" + pa, lab(SC + "Am", "", 12, "dim", w=SC_RI, h=20, anchor={"top": 6})))
    ab = SC + "Ab"
    ap.append(("#" + pa, G_.glass_group(ab, SC_RI, 34, layout="Left", anchor={"top": 8})))
    ap.append(("#" + ab, G_.glass_button(SC + "Aleave", "Leave party", "secondary", w=160, h=34, size=14, anchor={"right": 10})))
    ap.append(("#" + ab, G_.glass_button(SC + "Apage", "Party page", "secondary", w=160, h=34, size=14)))
    assert 20 + 24 + 8 + SC_MN * 54 + 26 + 42 <= SC_PH and 2 + 22 + 16 + 8 <= 50, "0.3.63: the party card fits"
    gu = SC + "Gu"
    ap.append(("#" + rt, G_.glass_group(gu, SC_R, SC_GH, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    gh = head(gu, "Gh", "GUILD", SC_RI, 200)
    ap.append(("#" + gh, lab(SC + "Gl", "", 13, "xp", bold=True, w=200, h=24, halign="End")))
    ap.append(("#" + gu, lab(SC + "Gn", "", 18, "title", bold=True, w=SC_RI, h=28, anchor={"top": 6})))
    ap.append(("#" + gu, lab(SC + "Gr", "", 13, "text", w=SC_RI, h=20)))
    ap.append(("#" + gu, 'Group #%sGb { Anchor: (Width: %d, Height: 8, Top: 6); LayoutMode: Left; Background: %s; }' % (SC, SC_GBW, IV_TRACK)))
    ap.append(("#" + gu, lab(SC + "Gx", "", 11, "dim", w=SC_RI, h=16, anchor={"top": 4})))
    ap.append(("#" + gu, lab(None, "ONLINE NOW", 12, "dim", bold=True, w=SC_RI, h=18, anchor={"top": 8})))
    for k_ in range(SC_GN):
        ap.append(("#" + gu, lab("%sO%d" % (SC, k_), "", 13, "row", w=SC_RI, h=20)))
    ap.append(("#" + gu, G_.glass_button(SC + "Gpage", "Guild page", "secondary", w=160, h=34, size=14, anchor={"top": 10})))
    assert 20 + 24 + 34 + 20 + 14 + 20 + 26 + SC_GN * 20 + 44 <= SC_GH, "0.3.63: the guild card fits"
    assert (IV_PAGE_H <= SUI.MAX_PAGE_H and IV_PAGE_W <= SUI.MAX_PAGE_W and SC_YH + 8 + SC_FH == IV_BODY_H and SC_PH + 8 + SC_GH == IV_BODY_H
            and SC_L + SC_M + SC_R + 2 * IV_GAP == IV_IW), "0.3.63: the social screen fits one 1080p screen"
    # ---- the caption + key hints
    hn = SC + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(SC + "Kh%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate((("LMB", "Pick / act"), ("Tab / Esc", "Close")))]
    hw = sum(w_ for _m, w_ in parts)
    ap.append(("#" + hn, lab(SC + "Cap", "", 14, "dim", w=IV_IW - hw - 20, h=IV_HINT_H)))
    assert SUI.text_width(SC_TXT["left"], 14) <= IV_IW - hw - 20, "0.3.63: the Leave party caption fits the caption line"
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    binds = [("#%sT%d" % (SC, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + SC + "Close", "close"), ("#" + SC + "Full", "full"),
                                                                                  ("#" + SC + "Pp", "pg:-1"), ("#" + SC + "Pn", "pg:1"),
                                                                                  ("#" + SC + "Ystats", "stats"), ("#" + SC + "Fpage", "prof"),
                                                                                  ("#" + SC + "Fno", "swno"), ("#" + SC + "Apage", "party"),
                                                                                  ("#" + SC + "Gpage", "guild")]
    return ap, binds


SC_AP, SC_BINDS = _sc_page()
SUI.check_page(SC_AP, SC)
for _p, _mk in SC_AP:
    SUI.check_markup(_mk, prefix=SC, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.63: the social screen never scrolls"
_sc_ids = set(i_ for _p, mk_ in SC_AP for i_ in SUI._static_ids(mk_))
for _s, _a in SC_BINDS:
    assert _s[1:] in _sc_ids, ("0.3.63: binding target", _s)
SC_DYN = (["Coins", "Close", "Full", "Cap", "Pc", "Pp", "Pg", "Pn", "St", "Ss", "An", "Yn", "Y2", "Y3", "P1", "P2", "Ystats", "Fc", "Fq", "FqT",
           "Fyes", "Fno", "Fnote", "Fpage", "Ac", "Am", "Aleave", "Apage", "Gl", "Gn", "Gr", "Gb", "Gx", "Gpage"]
          + ["R%d%s" % (k_, x_) for k_ in range(SC_PN) for x_ in ("", "N0", "N1", "S", "P")]
          + ["A%d" % k_ for k_ in range(len(SC_PA))]
          + ["K%d%s" % (k_, x_) for k_ in range(SC_KN) for x_ in ("", "N", "L")]
          + ["V%d%s" % (k_, x_) for k_ in range(SC_VN) for x_ in ("", "N", "L")]
          + ["F%d%s" % (k_, x_) for k_ in range(SC_FN) for x_ in ("", "N", "A", "W")]
          + ["M%d%s" % (k_, x_) for k_ in range(SC_MN) for x_ in ("", "N", "T", "S", "B")]
          + ["O%d" % k_ for k_ in range(SC_GN)])
for _g in SC_DYN:
    assert SC + _g in _sc_ids, "0.3.63: the social screen has #" + SC + _g
_sc_tok = SUI.proven_tokens(list(SC_AP))
SC_UNPROVEN = sorted(k_ for k_, g_ in _sc_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_)))
assert set(SC_UNPROVEN) <= set(["SlotBackground"]), "0.3.63: only SlotBackground (proven on the inventory page, TEST 282): %s" % SC_UNPROVEN
assert not [k_ for k_ in _sc_tok if k_ in ("MouseEntered", "MouseExited", "TooltipText")], "0.3.63: no hover events / tooltips of ours"
SUI.assert_glass_paths(SC_AP)
_sc_glass = set(re.findall(r"SkyyGlass/([A-Za-z0-9]+)\.png", " ".join(SUI.render(mk_) for _p, mk_ in SC_AP)))
assert _sc_glass <= _mt_glass, ("0.3.63: the social screen names only Skyglass pictures the market screen already ships (no new picture)", sorted(_sc_glass - _mt_glass))
SC_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in SC_AP)
SC_RUNTIME_MAX = SC_MN + 1                                     # a health fill per member + the guild XP fill
SC_ELEMENTS = SC_SHELL_ELEMENTS + SC_RUNTIME_MAX
assert SC_ELEMENTS <= 800, "0.3.63: the social screen stays well under the ~1,600 element budget (%d static + %d at run time)" % (SC_SHELL_ELEMENTS, SC_RUNTIME_MAX)
SC_LK, SC_LP, SC_LB = [], [], []
for _p, _mk in SC_AP:
    SC_LK.append("A")
    SC_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    SC_LB.append(SUI.render(_mk))
for _i, _pr, _v in SC_AP.sets:
    SC_LK.append("S")
    SC_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    SC_LB.append(_v)
for _s, _a in SC_BINDS:
    SC_LK.append("E")
    SC_LP.append(_s)
    SC_LB.append(_a)
assert SC_LK[0] == "A" and SC_LP[0] == "", "0.3.63: the page data starts with the root"
for _x in SC_LP + SC_LB:
    assert "@" not in _x and "\n" not in _x and len(_x.encode("utf-8")) < 60000, "0.3.63: a page line Java can hold"
print("0.3.63 social screen: %d elements (shell %d + at most %d at run time; budget ~1,600), %d appends, %d b.set, %d bindings; unproven: %s"
      % (SC_ELEMENTS, SC_SHELL_ELEMENTS, SC_RUNTIME_MAX, len(SC_AP), len(SC_AP.sets), len(SC_BINDS), ", ".join(SC_UNPROVEN)))

'''
P.rep('''PKG = T["PKG"]
# 0.2: every class goes through mk()''', SC_PAGE.lstrip("\n") + '''PKG = T["PKG"]
# 0.2: every class goes through mk()''')

# ---------- the two new classes
P.rep('''wtab = mk("WorldTab", T["PAGE"])    # 0.3.62: THE WORLD TAB = ONE SCREEN
''', '''wtab = mk("WorldTab", T["PAGE"])    # 0.3.62: THE WORLD TAB = ONE SCREEN
scd  = mk("SocialTabData")   # 0.3.63: the social screen's data (LK / LP / LB, the run-time markup)
stab = mk("SocialTab", T["PAGE"])   # 0.3.63: THE SOCIAL TAB = ONE SCREEN
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, mtd, mtab, wtd, wtab, pl)''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, mtd, mtab, wtd, wtab, scd, stab, pl)''')

# ---------- SocialTabData constants + SocialTab fields / constructor (after the WorldTab constructor)
SC_DATA = r'''# 0.3.63: THE SOCIAL SCREEN DATA (SocialTabData) + the SocialTab fields
F(scd, "public static final String LK = %s;" % jstr("".join(SC_LK)))
F(scd, "public static final String[] LP = %s;" % jarr(SC_LP))
F(scd, "public static final String[] LB = %s;" % jarr(SC_LB))
for _n, _v in (("PN", SC_PN), ("KN", SC_KN), ("VN", SC_VN), ("FN", SC_FN), ("MN", SC_MN), ("GN", SC_GN), ("BARW", SC_BARW), ("GBW", SC_GBW),
               ("AN", len(SC_PA))):
    F(scd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("FILLH", SC_FILLH), ("FILLX", SC_FILLX), ("CAP0", SC_TXT["cap0"]), ("LEFTCAP", SC_TXT["left"])):
    F(scd, "public static final String %s = %s;" % (_n, jstr(_v)))
F(scd, "public static final String[] XCMD = %s;" % jarr(SC_XCMD))   # fix: the actions after the old page's 7 (Trade)
for _f in ("public static volatile int OPENS = 0;", "public static volatile int STALE = 0;", "public static volatile int ACTS = 0;",
           "public volatile boolean closed;", "public boolean answered;", "public String via;", "public String tcap;", "public long seq;", "public long base;",
           "public String tok;", "public String pkey;", "public int page;", "public int pages;", "public String[] keys;", "public java.util.UUID selU;",
           "public String ask;", "public String askName;", "public String[] fids;", "public String[] fnames;",
           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;"):
    F(stab, _f)
C(stab, r"""
public SocialTab(@PR@ pr, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.via = via;
  this.closed = false;
  this.answered = false;
  this.tcap = "";
  this.seq = 0L;
  this.base = System.nanoTime() & 0xffffffL;
  this.tok = "";
  this.pkey = null;
  this.page = 0;
  this.pages = 1;
  this.keys = new String[0];
  this.selU = null;
  this.ask = null;
  this.askName = "";
  this.fids = new String[0];
  this.fnames = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
'''
P.rep('''  this.keys = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
''', '''  this.keys = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
''' + SC_DATA)

# ---------- SocialTab.open BEFORE the world screen's open (every caller below can reach it)
SC_OPEN = r'''# ---- 0.3.63: the SOCIAL SCREEN opens (the inventory's / skill page's / pets / market / world screen's Social tab); null = it could not open =
# the caller opens today's Social hub instead. Needs no bridge key: each card says when its mod is missing.
M(stab, r"""
public static @PKG@.SocialTab open(@REF@ ref, @ST@ st, @PR@ pr, String via) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  @PKG@.SocialTab pg = new @PKG@.SocialTab(pr, via);
  pg.pref = ref;
  pg.pst = st;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("social screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")
'''
P.rep('''# ---- 0.3.62: the WORLD SCREEN opens (the inventory's / skill page's / pets screen's / market screen's World tab); null = it could not open =
''', SC_OPEN + '''# ---- 0.3.62: the WORLD SCREEN opens (the inventory's / skill page's / pets screen's / market screen's World tab); null = it could not open =
''')
# the skill page's Social tab = this screen (else today's route, as before)
P.rep('''M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }''', '''# 0.3.63: the Social tab = the social screen (false = it could not open: today's route below)
M(skpg, r"""
public boolean socialTab() {
  @PKG@.SocialTab pg = null;
  try { pg = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "skill page"); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the social screen failed: " + t); }
  if (pg == null) return false;
  this.answered = true;
  if (!still()) finish("social");
  return true;
}""")
M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }''')
P.rep('''  if (i == 4 && worldTab()) return;   // 0.3.62
''', '''  if (i == 4 && worldTab()) return;   // 0.3.62
  if (i == 5 && socialTab()) return;   // 0.3.63
''')
# the pets screen's / market screen's Social tab = this screen
for _who in ("pets screen", "market screen"):
    P.rep('''    try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "%s"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("%s: the world screen failed: " + t); }
    if (wt != null) { if (!still()) finish("world"); return; }
  }
''' % (_who, _who), '''    try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "%s"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("%s: the world screen failed: " + t); }
    if (wt != null) { if (!still()) finish("world"); return; }
  }
  if (i == 5) {   // 0.3.63: the social screen (else today's route below)
    @PKG@.SocialTab so = null;
    try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "%s"); } catch (Throwable t) { so = null; @PKG@.MenuUtil.warn("%s: the social screen failed: " + t); }
    if (so != null) { if (!still()) finish("social"); return; }
  }
''' % (_who, _who, _who, _who))
# the world screen's Social tab = this screen
P.rep('''  if (i == 4) { say("You are on World"); return; }
''', '''  if (i == 4) { say("You are on World"); return; }
  if (i == 5) {   // 0.3.63: the social screen (else today's route below)
    @PKG@.SocialTab so = null;
    try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "world screen"); } catch (Throwable t) { so = null; @PKG@.MenuUtil.warn("world screen: the social screen failed: " + t); }
    if (so != null) { if (!still()) finish("social"); return; }
  }
''')

SC_JAVA = r'''# ================= 0.3.63 SocialTab: THE SOCIAL TAB = ONE SCREEN (approved social-page.png) =================
# Reads only existing bridges (profile:list / profile:<uuid> / profile:busy, party:fn:members / party:name / party:stats, guild:info /
# guild:fn:online) + the Stats page's own reads (StatsCalc) + the engine's players. Every action = the old page's command line (the Players
# page's PA_CMD / PA_CLOSE, /party leave, /profiles switch <n>) after the old page's checks. Every bound click answers with ONE page packet.
M(stab, r"""
public Object call(String key, Object arg) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null) return null;
  try { return f.apply(arg); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: " + key + " failed: " + t); return null; }
}""")
M(stab, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyyStabCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(stab, r"""
public void finish(String why) { this.closed = true; }""")
M(stab, r"""
public void shut() { finish("closed"); this.close(); }""")
M(stab, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(stab, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.answers = this.answers + 1;
  this.rebuild();
}""")
M(stab, r"""
public static void hold(@UCB@ b, String base, int n, int which, String text) {
  for (int k = 0; k < n; k++) {
    b.set("#" + base + k + ".Text", text == null ? "" : text);
    b.set("#" + base + k + ".Visible", k == which);
  }
}""")
M(stab, r"""
public static boolean hasCmd(String c) { return @PKG@.MenuUtil.cmd(c) != null; }""")
M(stab, r"""
public static String text(Object o) {
  if (!(o instanceof String)) return null;
  String t = ((String) o).trim();
  return t.length() == 0 ? null : t;
}""")
M(stab, r"""
public static boolean has(String[] a, String s) {
  for (int i = 0; a != null && s != null && i < a.length; i++) if (s.equals(a[i])) return true;
  return false;
}""")
# where a player stands: the world's name (an island world = "on an island"), "" when unknown
M(stab, r"""
public static String where(@PR@ p) {
  String n = "";
  try {
    java.util.UUID wu = p == null ? null : p.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w != null && w.getName() != null) n = String.valueOf(w.getName());
  } catch (Throwable t) { n = ""; }
  if (n.length() == 0) return "";
  if (n.startsWith("skyy-island-")) return "on an island";
  return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(n), 28);
}""")
# class + Overall of any online player (the Stats page's reads: profile:class / class, skill:fn:overall / skill:overall)
M(stab, r"""
public static String who(java.util.UUID u) {
  if (u == null) return "";
  StringBuilder sb = new StringBuilder();
  String c = null;
  try { c = @PKG@.StatsCalc.className(u); } catch (Throwable t) { c = null; }
  if (c != null) sb.append(@PKG@.MenuUtil.clip(c, 20));
  int ov = -1;
  try { ov = @PKG@.StatsCalc.overall(u); } catch (Throwable t) { ov = -1; }
  if (ov >= 0) { if (sb.length() > 0) sb.append("  "); sb.append("Overall Lv ").append(ov); }
  return sb.toString();
}""")
M(stab, r"""
public static String join(String a, String b) {
  if (a == null || a.length() == 0) return b == null ? "" : b;
  if (b == null || b.length() == 0) return a;
  return a + "  -  " + b;
}""")
M(stab, r"""
public @PR@ sel() {
  if (this.selU == null) return null;
  try {
    @PR@ p = @UNI@.get().getPlayer(this.selU);
    return p != null && p.isValid() ? p : null;
  } catch (Throwable t) { return null; }
}""")
M(stab, r"""
public String[] members() {
  Object r = call("party:fn:members", this.playerRef.getUuid());
  if (r instanceof String[]) return (String[]) r;
  return new String[0];
}""")
# everyone online but you, A-Z: "lowercase name \t uuid \t name"
M(stab, r"""
public java.util.ArrayList players() {
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.UUID me = this.playerRef.getUuid();
  Object all = null;
  try { all = @UNI@.get().getPlayers(); } catch (Throwable t) { all = null; }
  if (!(all instanceof java.util.Collection)) return rows;
  Object[] a = ((java.util.Collection) all).toArray();
  for (int i = 0; i < a.length && i < 2000; i++) {
    if (!(a[i] instanceof @PR@)) continue;
    @PR@ p = (@PR@) a[i];
    if (!p.isValid() || me.equals(p.getUuid())) continue;
    String n = p.getUsername();
    if (n == null || n.length() == 0) continue;
    rows.add(n.toLowerCase() + "\t" + p.getUuid().toString() + "\t" + n);
  }
  java.util.Collections.sort(rows);
  return rows;
}""")
# PLAYERS ONLINE: 10 a page; Pick carries the page token
M(stab, r"""
public void fillPlayers(@UCB@ b, @UEB@ ev, String[] mem) {
  java.util.ArrayList rows = players();
  b.set("#SkyyStabPc.Text", (rows.size() + 1) + " online");
  int n = @PKG@.SocialTabData.PN;
  this.pages = (rows.size() + n - 1) / n;
  if (this.pages < 1) this.pages = 1;
  if (this.page >= this.pages) this.page = this.pages - 1;
  if (this.page < 0) this.page = 0;
  int from = this.page * n;
  this.keys = new String[n];
  b.set("#SkyyStabPg.Text", "Page " + (this.page + 1) + " / " + this.pages);
  for (int k = 0; k < n; k++) {
    String r = "SkyyStabR" + k;
    int j = from + k;
    if (j >= rows.size()) {
      boolean none = rows.isEmpty() && k == 0;
      b.set("#" + r + ".Visible", none);
      this.keys[k] = null;
      if (none) {
        hold(b, r + "N", 2, 0, "Nobody else is online");
        b.set("#" + r + "S.Text", "You are the only player online right now.");
        b.set("#" + r + "P.Visible", false);
      }
      continue;
    }
    String[] f = ((String) rows.get(j)).split("\t");
    if (f.length < 3) { b.set("#" + r + ".Visible", false); this.keys[k] = null; continue; }
    java.util.UUID u = null;
    try { u = java.util.UUID.fromString(f[1]); } catch (Throwable t) { u = null; }
    @PR@ p = null;
    try { p = u == null ? null : @UNI@.get().getPlayer(u); } catch (Throwable t) { p = null; }
    boolean picked = this.selU != null && this.selU.toString().equals(f[1]);
    this.keys[k] = f[1];
    b.set("#" + r + ".Visible", true);
    hold(b, r + "N", 2, picked ? 1 : 0, @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[2]), 24) + (picked ? "   - picked" : ""));
    String s = join(join(who(u), where(p)), has(mem, f[1]) ? "in your party" : "");
    b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip(s, 64));
    b.set("#" + r + "P.Visible", true);
    ev.addEventBinding(@BT@.Activating, "#" + r + "P", @EVD@.of("a", "pick:" + k).append("t", this.tok));
  }
}""")
# the PICKED player + the old Players page's 7 actions + Trade (hidden until a player is picked)
M(stab, r"""
public void fillPicked(@UCB@ b, @UEB@ ev) {
  @PR@ t = sel();
  boolean on = t != null;
  if (!on && this.selU != null) { this.selU = null; b.set("#SkyyStabSt.Text", "That player went offline"); }
  else if (!on) b.set("#SkyyStabSt.Text", "Pick a player above");
  else b.set("#SkyyStabSt.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(t.getUsername()), 32));
  b.set("#SkyyStabSs.Text", on ? @PKG@.MenuUtil.clip(join(who(t.getUuid()), where(t)), 70) : "Their actions show here: teleport, party, guild, island.");
  b.set("#SkyyStabAr1.Visible", on);
  b.set("#SkyyStabAr2.Visible", on);
  if (!on) return;
  for (int i = 0; i < @PKG@.SocialTabData.AN; i++)
    ev.addEventBinding(@BT@.Activating, "#SkyyStabA" + i, @EVD@.of("a", "pa:" + i).append("t", this.tok));
}""")
# YOU: the Stats page's reads (StatsCalc) - name, class, profile, Overall + the class skill, skills, the Main tab's first rows, progress
M(stab, r"""
public void fillYou(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  b.set("#SkyyStabYn.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(this.playerRef.getUsername()), 32));
  String c = @PKG@.StatsCalc.className(u);
  String pn = @PKG@.StatsCalc.profileName(u);
  b.set("#SkyyStabY2.Text", @PKG@.MenuUtil.clip((c == null ? "No class yet" : c) + (pn == null ? "" : "  -  profile " + pn), 60));
  int ov = @PKG@.StatsCalc.overall(u);
  String cs = @PKG@.StatsCalc.classSkill(u);
  java.util.ArrayList ps = @PKG@.StatsCalc.pairs(@PKG@.MenuUtil.bridge().get("skill:" + u.toString()));
  String csl = "";
  java.util.ArrayList sk = new java.util.ArrayList();
  for (int i = 0; i < ps.size(); i++) {
    String[] p = (String[]) ps.get(i);
    if (@PKG@.StatsCalc.isClassSkill(p[0])) { if (cs != null && cs.equals(p[0])) csl = "    " + p[0] + " Lv " + p[1]; continue; }
    sk.add(p);
  }
  b.set("#SkyyStabY3.Text", (ov >= 0 ? "Overall Lv " + ov : "Overall Lv -") + csl);
  for (int k = 0; k < @PKG@.SocialTabData.KN; k++) {
    String e = "SkyyStabK" + k;
    if (k < sk.size()) {
      String[] p = (String[]) sk.get(k);
      b.set("#" + e + ".Visible", true);
      b.set("#" + e + "N.Text", @PKG@.MenuUtil.clip(p[0], 22));
      b.set("#" + e + "L.Text", p[1]);
    } else if (k == 0) {
      b.set("#" + e + ".Visible", true);
      b.set("#" + e + "N.Text", "No skill data yet");
      b.set("#" + e + "L.Text", "");
    } else b.set("#" + e + ".Visible", false);
  }
  Object[] vit = @PKG@.StatsCalc.vitals(this.pst, this.pref);
  java.util.ArrayList rs = @PKG@.StatsCalc.rows(u, 0, vit);
  for (int k = 0; k < @PKG@.SocialTabData.VN; k++) {
    String e = "SkyyStabV" + k;
    if (k < rs.size() && rs.get(k) instanceof String[] && ((String[]) rs.get(k)).length >= 2) {
      String[] r = (String[]) rs.get(k);
      b.set("#" + e + ".Visible", true);
      b.set("#" + e + "N.Text", @PKG@.MenuUtil.clip(r[0], 22));
      b.set("#" + e + "L.Text", @PKG@.MenuUtil.clip(r[1], 9));
    } else b.set("#" + e + ".Visible", false);
  }
  java.util.ArrayList pr = @PKG@.StatsCalc.rows(u, 4, null);
  String p1 = "";
  String p2 = "";
  if (pr.size() >= 6) {
    String[] a = (String[]) pr.get(2);
    String[] bk = (String[]) pr.get(3);
    String[] ch = (String[]) pr.get(4);
    String[] rc = (String[]) pr.get(5);
    p1 = a[0] + " " + a[1] + "      " + bk[0] + " " + bk[1];
    p2 = ch[0] + " " + ch[1] + "      " + rc[0] + " " + rc[1];
  }
  b.set("#SkyyStabP1.Text", @PKG@.MenuUtil.clip(p1, 70));
  b.set("#SkyyStabP2.Text", @PKG@.MenuUtil.clip(p2, 70));
}""")
# PROFILES: profile:list:<uuid> = "1:Main:Archer,2:Iron:Warrior" (live profiles), profile:<uuid> = the active id -> { id, name, class, "1" active }
M(stab, r"""
public static java.util.ArrayList profs(java.util.UUID u) {
  java.util.ArrayList act = new java.util.ArrayList();
  java.util.ArrayList rest = new java.util.ArrayList();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  String l = text(br.get("profile:list:" + u.toString()));
  String a = text(br.get("profile:" + u.toString()));
  if (l == null) return act;
  String[] es = l.split(",");
  for (int i = 0; i < es.length && i < 64; i++) {
    String s = es[i].trim();
    int c = s.indexOf(':');
    if (c <= 0) continue;
    int z = s.lastIndexOf(':');
    String id = s.substring(0, c).trim();
    boolean digits = id.length() > 0 && id.length() < 4;
    for (int k = 0; k < id.length(); k++) { char ch = id.charAt(k); if (ch < '0' || ch > '9') digits = false; }
    if (!digits) continue;
    String nm = z > c ? s.substring(c + 1, z).trim() : s.substring(c + 1).trim();
    String cl = z > c ? s.substring(z + 1).trim() : "";
    boolean on = a != null && a.equals(id);
    String[] r = new String[] { id, @PKG@.MenuUtil.safe(nm), @PKG@.MenuUtil.safe(cl), on ? "1" : "0" };
    if (on) act.add(r); else rest.add(r);
  }
  act.addAll(rest);
  return act;
}""")
M(stab, r"""
public void fillProfiles(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  boolean on = @PKG@.InvCraft.fn("profile:fn:key") != null || hasCmd("profiles");
  java.util.ArrayList ls = on ? profs(u) : new java.util.ArrayList();
  int n = ls.size();
  b.set("#SkyyStabFc.Text", !on || n == 0 ? "" : (n == 1 ? "1 profile" : n + " profiles"));
  this.fids = new String[@PKG@.SocialTabData.FN];
  this.fnames = new String[@PKG@.SocialTabData.FN];
  for (int k = 0; k < @PKG@.SocialTabData.FN; k++) {
    String r = "SkyyStabF" + k;
    if (k >= n) {
      boolean none = n == 0 && k == 0;
      b.set("#" + r + ".Visible", none);
      if (none) {
        b.set("#" + r + "N.Text", !on ? "Profiles are not on this server right now" : "No profile yet - the Profiles page makes one");
        b.set("#" + r + "A.Visible", false);
        b.set("#" + r + "W.Visible", false);
      }
      continue;
    }
    String[] f = (String[]) ls.get(k);
    boolean act = "1".equals(f[3]);
    this.fids[k] = f[0];
    this.fnames[k] = f[1];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(f[1] + (f[2].length() > 0 ? "  -  " + f[2] : ""), 40));
    b.set("#" + r + "A.Visible", act);
    b.set("#" + r + "W.Visible", !act);
    if (!act) ev.addEventBinding(@BT@.Activating, "#" + r + "W", @EVD@.of("a", "sw:" + k).append("t", this.tok));
  }
  boolean q = this.ask != null;
  b.set("#SkyyStabFq.Visible", q);
  if (q) {
    b.set("#SkyyStabFqT.Text", @PKG@.MenuUtil.clip("Switch to " + this.askName + "? You then go to its island.", 60));
    ev.addEventBinding(@BT@.Activating, "#SkyyStabFyes", @EVD@.of("a", "swok").append("t", this.tok));
  }
  int more = n - @PKG@.SocialTabData.FN;
  b.set("#SkyyStabFnote.Text", !on ? "" : (more > 0 ? "+" + more + " more on the Profiles page" : "New, rename, delete: the Profiles page"));
}""")
# PARTY: party:fn:members (leader first), party:name:<uuid>, party:stats:<uuid> = "hp,maxHp,stamina,maxStamina,mana,maxMana,worldName"
M(stab, r"""
public void fillParty(@UCB@ b, @UEB@ ev, String[] mem) {
  boolean on = @PKG@.InvCraft.fn("party:fn:members") != null || hasCmd("party");
  String me = this.playerRef.getUuid().toString();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  int n = mem == null ? 0 : mem.length;
  b.set("#SkyyStabAc.Text", n > 0 ? n + " members" : "");
  for (int k = 0; k < @PKG@.SocialTabData.MN; k++) {
    String r = "SkyyStabM" + k;
    if (k >= n || mem[k] == null) { b.set("#" + r + ".Visible", false); continue; }
    String u = mem[k];
    String nm = text(br.get("party:name:" + u));
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(nm == null ? "A player" : nm), 24) + (u.equals(me) ? " (you)" : ""));
    b.set("#" + r + "T.Text", k == 0 ? "Leader" : "");
    String st = text(br.get("party:stats:" + u));
    String[] f = st == null ? new String[0] : st.split(",", -1);
    if (f.length >= 7) {
      long hp = @PKG@.InvPage.toLong(f[0], 0L);
      long mx = @PKG@.InvPage.toLong(f[1], 0L);
      String wn = f[6].trim();
      b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip("Health " + hp + " / " + mx + (wn.length() > 0 ? "  -  " + @PKG@.MenuUtil.safe(wn) : ""), 60));
      int w = mx > 0L ? @PKG@.InvPage.barW(hp, mx, @PKG@.SocialTabData.BARW) : 0;
      if (w > 0) b.appendInline("#" + r + "B", @PKG@.SocialTabData.FILLH.replace("{W}", String.valueOf(w)));
    } else b.set("#" + r + "S.Text", "Offline, or no stats yet");
  }
  int more = n - @PKG@.SocialTabData.MN;
  b.set("#SkyyStabAm.Text", !on ? "Parties are not on this server right now"
      : (n == 0 ? "No party yet - pick a player and press Party invite." : (more > 0 ? "+" + more + " more on the Party page" : "")));
  b.set("#SkyyStabAleave.Visible", on && n > 0);
  b.set("#SkyyStabApage.Visible", on);
  if (on && n > 0) ev.addEventBinding(@BT@.Activating, "#SkyyStabAleave", @EVD@.of("a", "leave").append("t", this.tok));
}""")
# GUILD: guild:info:<uuid> = "name|tag|level|xp|xpForNext|onlineCount|memberCount|rank", guild:fn:online apply(UUID) -> String[] names
M(stab, r"""
public void fillGuild(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  boolean on = @PKG@.InvCraft.fn("guild:fn:online") != null || hasCmd("guild");
  String in = text(@PKG@.MenuUtil.bridge().get("guild:info:" + u.toString()));
  String[] f = in == null ? new String[0] : in.split("\\|", -1);
  boolean has = on && f.length >= 8 && f[0].trim().length() > 0;
  b.set("#SkyyStabGl.Text", has ? "Guild Lv " + @PKG@.MenuUtil.clip(f[2].trim(), 6) : "");
  if (!on) b.set("#SkyyStabGn.Text", "Guilds are not on this server right now");
  else if (!has) b.set("#SkyyStabGn.Text", "You are not in a guild");
  else b.set("#SkyyStabGn.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[0].trim()) + (f[1].trim().length() > 0 ? "  [" + @PKG@.MenuUtil.safe(f[1].trim()) + "]" : ""), 40));
  b.set("#SkyyStabGr.Text", !on ? "" : (!has ? "The Guild page makes one or shows your invites."
      : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[7].trim()) + "  -  " + f[6].trim() + " members, " + f[5].trim() + " online", 60)));
  long xp = has ? @PKG@.InvPage.toLong(f[3], 0L) : 0L;
  long need = has ? @PKG@.InvPage.toLong(f[4], 0L) : 0L;
  b.set("#SkyyStabGb.Visible", has);
  b.set("#SkyyStabGx.Text", has ? "Guild XP " + @PKG@.MenuUtil.fmt(xp) + " / " + @PKG@.MenuUtil.fmt(need) : "");
  if (has && need > 0L) {
    int w = @PKG@.InvPage.barW(xp, need, @PKG@.SocialTabData.GBW);
    if (w > 0) b.appendInline("#SkyyStabGb", @PKG@.SocialTabData.FILLX.replace("{W}", String.valueOf(w)));
  }
  String[] ol = new String[0];
  if (has) {
    Object o = call("guild:fn:online", u);
    if (o instanceof String[]) ol = (String[]) o;
  }
  int g = @PKG@.SocialTabData.GN;
  for (int k = 0; k < g; k++) {
    String r = "#SkyyStabO" + k;
    if (k >= ol.length || ol[k] == null) { b.set(r + ".Visible", false); continue; }
    b.set(r + ".Visible", true);
    b.set(r + ".Text", k == g - 1 && ol.length > g ? "+" + (ol.length - g + 1) + " more on the Guild page" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(ol[k]), 32));
  }
  b.set("#SkyyStabGpage.Visible", on);
}""")
M(stab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.SocialTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.SocialTabData.LP[i];
    String y = @PKG@.SocialTabData.LB[i];
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
  b.set("#SkyyStabCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  String[] mem = new String[0];
  try { mem = members(); } catch (Throwable t) { mem = new String[0]; }
  try { fillPlayers(b, ev, mem); } catch (Throwable t) { this.keys = new String[0]; @PKG@.MenuUtil.warn("social screen: the players list failed: " + t); }
  try { fillPicked(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: the picked player failed: " + t); }
  try { fillYou(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: the you card failed: " + t); }
  try { fillProfiles(b, ev); } catch (Throwable t) { this.fids = new String[0]; @PKG@.MenuUtil.warn("social screen: the profiles card failed: " + t); }
  try { fillParty(b, ev, mem); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: the party card failed: " + t); }
  try { fillGuild(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: the guild card failed: " + t); }
  b.set("#SkyyStabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.SocialTabData.CAP0);
}""")
# ---- the actions (each answers with ONE packet: a redraw, a caption, a page that replaces this one, or the close)
M(stab, r"""
public void hub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    if (tab != null && tab.length() > 0) r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("social screen: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
M(stab, r"""
public void tabGo(int i) {
  this.answered = true;
  if (i == 0) {
    @PKG@.InvPage pg = null;
    try { pg = @PKG@.InvState.openAt(this.pref, this.pst, this.playerRef, "social screen", "c", -1); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("social screen: the inventory failed: " + t); }
    if (pg == null) { if (still()) say("The inventory could not open here"); return; }
    if (!still()) finish("inventory");
    return;
  }
  if (i == 1) {
    @PKG@.SkillPage sp = null;
    try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, @PKG@.SkillPage.lastOf(this.playerRef.getUuid()), "social screen"); } catch (Throwable t) { sp = null; @PKG@.MenuUtil.warn("social screen: the skill page failed: " + t); }
    if (sp == null) { hub(@PKG@.InvData.TAB_HUB[1], @PKG@.InvData.TAB_TAB[1], @PKG@.InvData.TAB_NAME[1]); return; }
    if (!still()) finish("skills");
    return;
  }
  if (i == 2) {
    @PKG@.PetsTab pt = null;
    try { pt = @PKG@.PetsTab.open(this.pref, this.pst, this.playerRef, "social screen"); } catch (Throwable t) { pt = null; @PKG@.MenuUtil.warn("social screen: the pets screen failed: " + t); }
    if (pt == null) { hub(@PKG@.InvData.TAB_HUB[2], @PKG@.InvData.TAB_TAB[2], @PKG@.InvData.TAB_NAME[2]); return; }
    if (!still()) finish("pets");
    return;
  }
  if (i == 3) {
    @PKG@.MarketTab mt = null;
    try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "social screen"); } catch (Throwable t) { mt = null; @PKG@.MenuUtil.warn("social screen: the market screen failed: " + t); }
    if (mt == null) { hub(@PKG@.InvData.TAB_HUB[3], @PKG@.InvData.TAB_TAB[3], @PKG@.InvData.TAB_NAME[3]); return; }
    if (!still()) finish("market");
    return;
  }
  if (i == 4) {
    @PKG@.WorldTab wt = null;
    try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "social screen"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("social screen: the world screen failed: " + t); }
    if (wt == null) { hub(@PKG@.InvData.TAB_HUB[4], @PKG@.InvData.TAB_TAB[4], @PKG@.InvData.TAB_NAME[4]); return; }
    if (!still()) finish("world");
    return;
  }
  if (i == 5) { say("You are on Social"); return; }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }
  hub(@PKG@.InvData.TAB_HUB[i], @PKG@.InvData.TAB_TAB[i], @PKG@.InvData.TAB_NAME[i]);
}""")
# a command line as the player - the old Players page's MenuPage.runCmd checks in its order: the command exists, the server's version has the
# subcommand (needOf), the player's permission; close = the page closes first (a teleport / a profile switch), else the caption + a redraw
M(stab, r"""
public void runLine(String line, boolean close) {
  this.answered = true;
  String name = @PKG@.MenuUtil.firstWord(line);
  @ACM@ c = @PKG@.MenuUtil.cmd(name);
  if (c == null) { this.tcap = "/" + name + " is not on this server - that mod is not installed."; redraw(); return; }
  String need = @PKG@.MenuUtil.needOf(line);
  if (need != null) { this.tcap = "/" + line + " needs " + need + " - this server has an older version."; redraw(); return; }
  boolean ok = false;
  boolean checked = true;
  try { ok = c.hasPermission(this.playerRef); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("permission check for /" + name + " failed: " + t); ok = false; checked = false; }
  if (!checked) { this.tcap = "Could not check your permission for /" + name + ". Ask an admin."; redraw(); return; }
  if (!ok) {
    String node = null;
    try { node = c.getPermission(); } catch (Throwable t) { node = null; }
    this.tcap = "You do not have permission for /" + name + (node == null ? "" : " (" + @PKG@.MenuUtil.safe(node) + ")") + ". Ask an admin.";
    redraw();
    return;
  }
  ACTS = ACTS + 1;
  if (close) {
    shut();
    try { @CMGR@.get().handleCommand(this.playerRef, line); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: /" + line + " failed: " + t); }
    return;
  }
  try { @CMGR@.get().handleCommand(this.playerRef, line); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: /" + line + " failed: " + t); this.tcap = "/" + name + " could not be run."; redraw(); return; }
  this.tcap = "party leave".equals(line) ? @PKG@.SocialTabData.LEFTCAP : "/" + line + "  - see your chat";
  redraw();
}""")
# one of the old Players page's actions on the picked player (MenuPage.playerAction: the same line, the same close flag); after them
# SocialTabData.XCMD (Trade = SkyyEssentials' /trade <name>, a request - the page stays) through the same runLine checks
M(stab, r"""
public void act(int i) {
  this.answered = true;
  int na = @PKG@.MenuData.PA_CMD.length;
  if (i < 0 || i >= na + @PKG@.SocialTabData.XCMD.length) { say("No such action"); return; }
  @PR@ t = sel();
  if (t == null) { this.selU = null; this.tcap = "That player went offline."; redraw(); return; }
  String n = @PKG@.MenuUtil.cleanName(t.getUsername());
  if (n.length() == 0) { this.tcap = "That player's name cannot be used in a command."; redraw(); return; }
  if (i < na) runLine(@PKG@.MenuData.PA_CMD[i].replace("%P", n), @PKG@.MenuData.PA_CLOSE[i]);
  else runLine(@PKG@.SocialTabData.XCMD[i - na].replace("%P", n), false);
}""")
M(stab, r"""
public void pick(int k) {
  this.answered = true;
  if (k < 0 || this.keys == null || k >= this.keys.length || this.keys[k] == null) { say("Nobody there"); return; }
  java.util.UUID u = null;
  try { u = java.util.UUID.fromString(this.keys[k]); } catch (Throwable t) { u = null; }
  if (u == null) { say("Nobody there"); return; }
  this.selU = u;
  this.tcap = "";
  redraw();
}""")
# Switch: the confirm row first (SkyyProfiles' own page asks too); Confirm = the page closes, /profiles switch <number> as the player
M(stab, r"""
public int findProf(String id) {
  java.util.ArrayList ls = profs(this.playerRef.getUuid());
  for (int i = 0; i < ls.size(); i++) {
    String[] f = (String[]) ls.get(i);
    if (f[0].equals(id)) return "1".equals(f[3]) ? 1 : 0;
  }
  return -1;
}""")
M(stab, r"""
public void swAsk(int k) {
  this.answered = true;
  if (k < 0 || this.fids == null || k >= this.fids.length || this.fids[k] == null) { say("No profile there"); return; }
  int f = findProf(this.fids[k]);
  if (f < 0) { this.ask = null; this.tcap = "That profile is gone - here is your list."; redraw(); return; }
  if (f == 1) { this.ask = null; this.tcap = "You are already on that profile."; redraw(); return; }
  this.ask = this.fids[k];
  this.askName = this.fnames[k] == null ? this.fids[k] : this.fnames[k];
  this.tcap = "";
  redraw();
}""")
M(stab, r"""
public void swGo() {
  this.answered = true;
  String id = this.ask;
  if (id == null) { say("Press Switch on a profile first"); return; }
  this.ask = null;
  int f = findProf(id);
  if (f < 0) { this.tcap = "That profile is gone - here is your list."; redraw(); return; }
  if (f == 1) { this.tcap = "You are already on that profile."; redraw(); return; }
  if (Boolean.TRUE.equals(@PKG@.MenuUtil.bridge().get("profile:busy:" + this.playerRef.getUuid().toString()))) {
    this.tcap = "A profile switch is already running - try again in a moment.";
    redraw();
    return;
  }
  runLine("profiles switch " + id, true);
}""")
M(stab, r"""
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
    if (a.equals("full")) { hub("social", "players", "the Players page"); return; }
    if (a.equals("stats")) { hub("character", "stats", "the Stats page"); return; }
    if (a.equals("prof")) { hub("character", "profiles", "the Profiles page"); return; }
    if (a.equals("party")) { hub("social", "party", "the Party page"); return; }
    if (a.equals("guild")) { hub("social", "guild", "the Guild page"); return; }
    if (a.equals("swno")) { this.ask = null; this.tcap = "Nothing changed."; redraw(); return; }
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
      this.ask = null;
      this.tcap = "Your profile changed - here it is again. Nothing happened.";
      redraw();
      return;
    }
    if (a.startsWith("pick:")) { pick(@PKG@.InvPage.toInt(a.substring(5), -1)); return; }
    if (a.startsWith("pa:")) { act(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.startsWith("sw:")) { swAsk(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.equals("swok")) { swGo(); return; }
    if (a.equals("leave")) { runLine("party leave", false); return; }
    say("Pick a player");
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("social screen event '" + a + "' failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.MenuUtil.warn("social screen: the empty answer failed: " + t2); }
    }
  }
}""")
M(stab, r"""
public void onDismiss(@REF@ ref, @ST@ st) { finish("dismissed"); }""")
'''
P.rep('''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''', SC_JAVA + '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''')
# Tab while the social screen is open = it closes
P.rep('''  if (sp0 instanceof @PKG@.WorldTab && !((@PKG@.WorldTab) sp0).closed) { ((@PKG@.WorldTab) sp0).shut(); return; }   // 0.3.62
''', '''  if (sp0 instanceof @PKG@.WorldTab && !((@PKG@.WorldTab) sp0).closed) { ((@PKG@.WorldTab) sp0).shut(); return; }   // 0.3.62
  if (sp0 instanceof @PKG@.SocialTab && !((@PKG@.SocialTab) sp0).closed) { ((@PKG@.SocialTab) sp0).shut(); return; }   // 0.3.63
''')
# ---------- the inventory: the Social tab opens the social screen
P.rep('''M(ipg, r"""
public void goTab(int i) {''', '''# 0.3.63: the Social tab = the social screen (false = it could not open: today's Social route below)
M(ipg, r"""
public boolean openSocial() {
  @PKG@.SocialTab so = null;
  try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "inventory"); } catch (Throwable t) { so = null; @PKG@.MenuUtil.warn("inventory: the social screen failed: " + t); }
  if (so == null) return false;
  this.answered = true;
  if (!still()) finish("social");
  return true;
}""")
M(ipg, r"""
public void goTab(int i) {''')
P.rep('''  if (i == 4 && openWorld()) return;   // 0.3.62: the world screen (else today's World route below)
''', '''  if (i == 4 && openWorld()) return;   // 0.3.62: the world screen (else today's World route below)
  if (i == 5 && openSocial()) return;   // 0.3.63: the social screen (else today's Social route below)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.63: no new system / command"
_i = P.s.index
assert _i("public SocialTab(@PR@ pr, String via)") < _i("public static @PKG@.SocialTab open(") < _i("public static @PKG@.WorldTab open(")
assert _i("public static @PKG@.SocialTab open(") < _i("public boolean socialTab()") < _i('try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "pets screen")')
assert _i('try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "world screen")') > _i("public static @PKG@.SocialTab open(")
assert _i("public void shut() { finish(\"closed\"); this.close(); }\"\"\")\nM(stab") < _i("if (sp0 instanceof @PKG@.SocialTab")
assert _i("public boolean openSocial()") < _i("public void goTab(int i)") and _i('F(scd, "public static final String LK') < _i("public static @PKG@.SocialTab open(")
assert _i("public static @PKG@.WorldTab open(") < _i('try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "social screen")')
assert _i("public static String[] homes(String key, java.util.UUID u)") < _i("public void fillYou(@UCB@ b)"), "0.3.63: the social screen's methods come after WorldTab's"
P.finish()


# ======================================================================= the HARNESS (derived from the 0.3.62 harness: every 0.3.62 check
# runs again on the 0.3.63 jar, plus TAB5 on Python stand-ins of the social bridges + the harness' own command manager)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.62 (the World tab = one screen; tools/menu_0_3_62_patch.py, round tab4).
GENERATED by tools/menu_0_3_62_patch.py from the 0.3.61 harness (edit the patch, not this file): every 0.3.61 check runs again on the
0.3.62 jar''', '''"""Harness for SkyyMenu 0.3.63 (the Social tab = one screen; tools/menu_0_3_63_patch.py, round tab5).
GENERATED by tools/menu_0_3_63_patch.py from the 0.3.62 harness (edit the patch, not this file): every 0.3.62 check runs again on the
0.3.63 jar (the world screen's Social tab now opens the social screen - still ONE packet), plus
  TAB5 (EXECUTED on Python stand-ins of SkyyProfiles profile:list / profile:<uuid> / profile:busy / profile:fn:key, SkyyParty party:fn:members /
       party:name / party:stats, SkyyGuilds guild:info / guild:fn:online, SkyySkills skill:<uuid> / skill:overall, the class keys - and the
       harness' own command manager (/tpa /party /guild /island /profiles, one command that refuses the permission) + online players):
       OPEN    the inventory's / skill page's / pets screen's / market screen's / world screen's Social tab = the SOCIAL SCREEN (ONE packet)
       FALL    no keys + no commands: every card says "not on this server"; nobody else online = said; a missing / refused command = the
               old page's caption, no command
       PAGE    players A-Z (class + Overall, where, in your party), you (class, profile, Overall, skills, stats, progress), profiles (ACTIVE
               first, Switch on the others), party (leader, health + bar, where), guild (name, tag, level, rank, XP bar, online)
       ACT     Pick + each of the 7 actions = the old Players page's command line (the close flag kept); Trade = /trade <name> (fix round);
               Leave party = /party leave (its caption: the card updates on the next click);
               Switch -> Confirm = the page closes + /profiles switch <n>; Cancel; a busy profile = said; links = the old pages (ONE packet)
       SAFE    a stale page token / a double click = nothing runs twice; a profile switch between draw and click = said, nothing runs;
               the picked player gone offline = said
       TABS    every tab from the screen; the Tab key and X close it
The 0.3.62 harness text follows:
Harness for SkyyMenu 0.3.62 (the World tab = one screen; tools/menu_0_3_62_patch.py, round tab4).
GENERATED by tools/menu_0_3_62_patch.py from the 0.3.61 harness (edit the patch, not this file): every 0.3.61 check runs again on the
0.3.62 jar''')
T.rep('VERSION = "0.3.62"\nJAR', 'VERSION = "0.3.63"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.61.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.62.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.61.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.62.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_62_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_63_patch.py")')
T.rep('"scratch", "tab4", "menu"', '"scratch", "tab5", "menu"')
T.rep('ADDED = ["WorldTabData", "WorldTab"]   # 0.3.62: the world screen\n', 'ADDED = ["SocialTabData", "SocialTab"]   # 0.3.63: the social screen\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.62:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.63: the Social tab opens the social screen (inventory + skill page + pets / market / world screen); Tab closes it
    "InvPage": ["+m openSocial", "~m goTab"],
    "InvState": ["~m tab"],
    "SkillPage": ["+m socialTab", "~m tabGo"],
    "PetsTab": ["~m tabGo"],
    "MarketTab": ["~m tabGo"],
    "WorldTab": ["~m tabGo"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.62"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.63"') == 1, "S VERSION")
    # 0.3.63: the social screen fits one 1080p screen, never scrolls, element budget, no new picture
    K.check("0.3.63: the social screen fits one 1080p screen" in g and "0.3.63: the social screen never scrolls" in g
            and "0.3.63: the social screen names only Skyglass pictures the market screen already ships" in g,
            "TAB5 STATIC the build asserts the social screen fits 1080 (every column sums to the body), has no scrolling list and no new picture")
    mw5_ = re.search(r"SC_ELEMENTS <= (\\d+)", g)
    K.check(mw5_ is not None and int(mw5_.group(1)) <= 800, "TAB5 STATIC the social screen's element budget assert is <= 800 (the ~1,600 client budget)")''')
T.rep('''("MarketTabData", "SkyyMtab"), ("WorldTabData", "SkyyWtab")):''',
      '''("MarketTabData", "SkyyMtab"), ("WorldTabData", "SkyyWtab"), ("SocialTabData", "SkyyStab")):''')
# the world screen's Social tab is now the social screen (still ONE packet - the 0.3.62 check stays, its words say so)
T.rep('''    K.check(len(pages(PK, f0_)) == 1, "TAB4 TABS Social = today's route, ONE packet")''',
      '''    K.check(len(pages(PK, f0_)) == 1 and PK.pm.getCustomPage() is not None and str(PK.pm.getCustomPage().getClass().getSimpleName()) == "SocialTab",
            "TAB4 TABS Social = (0.3.63) the social screen, ONE packet")''')

HARNESS_TAB5 = r'''    # ---- TAB5 (0.3.63; popup 11-14 "Yes, both" on the 7 tabs; Skyy 11-21 "build and deploy everything on your list"): THE SOCIAL SCREEN
    SCB, SCD = JV("SocialTab"), JV("SocialTabData")
    uk5 = str(PK.pr.getUuid())
    WK5 = ("profile:list:" + uk5, "profile:" + uk5, "profile:busy:" + uk5, "profile:fn:key", "profile:class:" + uk5, "profile:pname:" + uk5,
           "party:fn:members", "guild:info:" + uk5, "guild:fn:online", "skill:" + uk5, "skill:overall:" + uk5, "class:skill:" + uk5,
           "skill:fn:overall", "class:fn:get", "coins:fn:get", "class:" + uk5)
    for k_ in WK5:
        BR.remove(k_)
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    E.pump(PK)
    CMD5 = {}
    for cn_ in ("tpa", "tpahere", "island", "party", "guild", "profiles", "trade"):
        CMD5[cn_] = E.CM.cmds.remove(cn_)
    CMDOK = CMD5["island"] if CMD5["island"] is not None else Ucls.allocateInstance(JClass("skyymenu19.Cmd").class_)
    PL5 = [E.UniH.PL.get(i_) for i_ in range(int(E.UniH.PL.size()))]
    EP5 = [E.PLAYERS.get(i_) for i_ in range(int(E.PLAYERS.size()))]   # the engine's own list (Universe.getPlayers reads it)
    for L_ in (E.UniH.PL, E.PLAYERS):
        L_.clear()
        L_.add(PK.pr)

    def lines5():
        return [str(E.CM.lines.get(i_)) for i_ in range(int(E.CM.lines.size()))]

    def s_ev(obj, what, n=1, page=None):
        pg_ = page if page is not None else PK.pm.getCustomPage()
        f_ = len(E.sent(PK))
        pg_.handleDataEvent(PK.ref, PK.st, json.dumps(obj))
        ps_ = pages(PK, f_)
        if n is not None:
            K.eq(len(ps_), n, what + ": exactly %d page packet" % n)
        return ps_[0] if ps_ else None

    def s_open(what):
        if PK.pm.getCustomPage() is not None:
            PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
        E.pump(PK)
        f_ = len(E.sent(PK))
        ss_ = SCB.open(PK.ref, PK.st, PK.pr, "test")
        E.pump(PK)
        ps_ = pages(PK, f_)
        K.check(ss_ is not None and len(ps_) == 1, what + ": SocialTab.open = ONE page packet")
        return ss_, (ps_[0] if ps_ else None)
    vis5 = lambda c_, k_: sval(c_, "#SkyyStab%s.Visible" % k_) in (True, "true")
    txt5 = lambda c_, k_: str(sval(c_, "#SkyyStab%s.Text" % k_))
    cap5 = lambda p_: str(sval(cmap(p_), "#SkyyStabCap.Text"))
    who5 = lambda c_: [txt5(c_, "R%dN%d" % (k_, 1 if vis5(c_, "R%dN1" % k_) else 0)) for k_ in range(int(SCD.PN)) if vis5(c_, "R%d" % k_)]
    # OPEN from the inventory with no social mod at all (no keys, no commands, nobody else online)
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:5"}')
    pk_ = pages(PK, f0_)
    SS = PK.pm.getCustomPage()
    K.check(len(pk_) == 1 and SS is not None and str(SS.getClass().getSimpleName()) == "SocialTab" and bool(pgI_.closed) and ST.PAGES.get(PK.pr.getUuid()) is None,
            "TAB5 OPEN the inventory's Social tab = the SOCIAL SCREEN (ONE page packet), the inventory page forgotten")
    cm = cmap(pk_[0]) if pk_ else {}
    K.notes.append("TAB5 the screen's first packet: %d commands, %d bindings" % (len(cmds_of(pk_[0])) if pk_ else 0, len(binds_of(pk_[0])) if pk_ else 0))
    K.check(who5(cm) == ["Nobody else is online"] and not vis5(cm, "R0P") and txt5(cm, "Pc") == "1 online" and not vis5(cm, "R1")
            and not vis5(cm, "Ar1") and not vis5(cm, "Ar2") and txt5(cm, "St") == "Pick a player above",
            "TAB5 FALL nobody else online: one row says so (no Pick), 1 online, no actions (%s)" % who5(cm))
    K.check(txt5(cm, "F0N") == "Profiles are not on this server right now" and not vis5(cm, "F0W") and not vis5(cm, "F1") and not vis5(cm, "Fq")
            and txt5(cm, "Am") == "Parties are not on this server right now" and not vis5(cm, "Aleave") and not vis5(cm, "Apage") and not vis5(cm, "M0")
            and txt5(cm, "Gn") == "Guilds are not on this server right now" and not vis5(cm, "Gpage") and not vis5(cm, "O0") and not vis5(cm, "Gb"),
            "TAB5 FALL no social mod: profiles / party / guild cards say 'not on this server', their buttons hidden")
    K.check(txt5(cm, "Yn") == "SkyyCraftA" and txt5(cm, "Y2") == "No class yet" and txt5(cm, "K0N") == "No skill data yet" and not vis5(cm, "K1")
            and txt5(cm, "V0N") == "Health" and "Purse" in txt5(cm, "P1") and txt5(cm, "Cap") == str(SCD.CAP0),
            "TAB5 FALL you card without the skill mods: your name, no class, no skill data, the Stats page's Health row, the purse line, the caption")
    p_ = s_ev({"a": "pick:0", "t": str(SS.tok)}, "TAB5 FALL Pick on the empty row")
    K.check("Nobody there" in cap5(p_) or "Pick" in cap5(p_), "TAB5 FALL Pick on 'nobody' = a caption (%s)" % cap5(p_))
    # the social mods + players arrive
    PB5 = E.player(uid=UUIDc(0x63, 0x01), name="Bravo", world=E.W2, world_u=E.W2U)
    PA5 = E.player(uid=UUIDc(0x63, 0x02), name="alpha")
    PC5 = E.player(uid=UUIDc(0x63, 0x03), name="Charlie")
    for P_ in (PB5, PA5, PC5):
        E.UniH.PL.add(P_.pr)
        E.PLAYERS.add(P_.pr)
        byU.put(P_.pr.getUuid(), P_.pr)
    ub5, ua5 = str(PB5.pr.getUuid()), str(PA5.pr.getUuid())
    for cn_ in ("tpa", "island", "party", "profiles"):
        E.CM.cmds.put(cn_, CMDOK)
    CP5_ = JClass("javassist.ClassPool").getDefault()
    np_ = CP5_.makeClass("skyymenu63.NoPerm", CP5_.get("skyymenu19.Cmd"))
    np_.addMethod(JClass("javassist.CtNewMethod").make("public boolean hasPermission(" + PH + "server.core.command.system.CommandSender s) { return false; }", np_))
    np_.writeFile(hcls)
    E.CM.cmds.put("guild", Ucls.allocateInstance(JClass("skyymenu63.NoPerm").class_))
    BR.put("profile:list:" + uk5, "1:Main:Archer,2:Iron:Warrior,x:Bad:None")
    BR.put("profile:" + uk5, "1")
    BR.put("profile:class:" + uk5, "Archer")
    BR.put("profile:pname:" + uk5, "Main")
    BR.put("class:skill:" + uk5, "Archery")
    BR.put("skill:" + uk5, "Mining:31,Archery:12,Farming:24")
    BR.put("skill:overall:" + uk5, JClass("java.lang.Integer")(23))
    BR.put("profile:class:" + ua5, "Mage")
    BR.put("skill:overall:" + ua5, JClass("java.lang.Integer")(19))
    f_mem5 = Fn(lambda o: _JA(JS)([uk5, ub5]) if str(o) in (uk5, ub5) else _JA(JS)([]))
    BR.put("party:fn:members", f_mem5)
    BR.put("party:name:" + uk5, "SkyyCraftA")
    BR.put("party:name:" + ub5, "Bravo")
    BR.put("party:stats:" + uk5, "150,200,10,10,30,30,harness_home")
    BR.put("party:stats:" + ub5, "40,100,10,10,30,30,")
    BR.put("guild:info:" + uk5, "Wardens|SW|6|1200|5000|2|24|Leader")
    BR.put("guild:fn:online", Fn(lambda o: _JA(JS)(["SkyyCraftA", "Bravo"])))
    p_ = s_ev({"a": "pg:1"}, "TAB5 a redraw with every key")
    p_ = s_ev({"a": "swno"}, "TAB5 a redraw with every key (Cancel with nothing asked)")
    cm = cmap(p_)
    K.check(who5(cm) == ["alpha", "Bravo", "Charlie"] and txt5(cm, "Pc") == "4 online" and txt5(cm, "Pg") == "Page 1 / 1" and all(vis5(cm, "R%dP" % k_) for k_ in range(3))
            and "Mage  Overall Lv 19" in txt5(cm, "R0S") and "harness_other" in txt5(cm, "R1S") and "in your party" in txt5(cm, "R1S")
            and "in your party" not in txt5(cm, "R2S"), "TAB5 PAGE players A-Z (case ignored), class + Overall, where, in your party; 4 online (%s / %s)" % (who5(cm), txt5(cm, "R1S")))
    K.check(txt5(cm, "Y2") == "Archer  -  profile Main" and txt5(cm, "Y3") == "Overall Lv 23    Archery Lv 12"
            and [txt5(cm, "K0N"), txt5(cm, "K0L"), txt5(cm, "K1N"), txt5(cm, "K1L")] == ["Mining", "31", "Farming", "24"] and not vis5(cm, "K2"),
            "TAB5 PAGE you: class + profile, Overall + the class skill, the other skills with levels (the class skill not twice)")
    K.check([txt5(cm, "V%dN" % k_) for k_ in range(3)] == ["Health", "Mana", "Stamina"] and "Bank" in txt5(cm, "P1") and "Void Charms" in txt5(cm, "P2"),
            "TAB5 PAGE you: the Stats page's Main rows (Health, Mana, Stamina ...) and progress (purse, bank, charms, recipes)")
    K.check(txt5(cm, "Fc") == "2 profiles" and txt5(cm, "F0N") == "Main  -  Archer" and vis5(cm, "F0A") and not vis5(cm, "F0W")
            and txt5(cm, "F1N") == "Iron  -  Warrior" and vis5(cm, "F1W") and not vis5(cm, "F1A") and not vis5(cm, "F2") and not vis5(cm, "Fq"),
            "TAB5 PAGE profiles: the active one first + ACTIVE, Switch on the other; a bad id left out")
    K.check(txt5(cm, "Ac") == "2 members" and txt5(cm, "M0N") == "SkyyCraftA (you)" and txt5(cm, "M0T") == "Leader" and txt5(cm, "M1T") == ""
            and txt5(cm, "M0S") == "Health 150 / 200  -  harness_home" and txt5(cm, "M1S") == "Health 40 / 100" and not vis5(cm, "M2")
            and ("Width: %d," % (150 * int(SCD.BARW) // 200)) in cm.get("#SkyyStabM0B", "") and vis5(cm, "Aleave") and vis5(cm, "Apage"),
            "TAB5 PAGE party: members (you marked), the leader, health + where, the health bar; Leave party + Party page")
    K.check(txt5(cm, "Gn") == "Wardens  [SW]" and txt5(cm, "Gl") == "Guild Lv 6" and txt5(cm, "Gr") == "Leader  -  24 members, 2 online"
            and txt5(cm, "Gx") == "Guild XP 1,200 / 5,000" and ("Width: %d," % (1200 * int(SCD.GBW) // 5000)) in cm.get("#SkyyStabGb", "")
            and [txt5(cm, "O0"), txt5(cm, "O1")] == ["SkyyCraftA", "Bravo"] and not vis5(cm, "O2") and vis5(cm, "Gpage"),
            "TAB5 PAGE guild: name + tag, level, rank + members + online, the XP bar, who is online")
    K.check(not any("Scrolling" in str(c_.text or "") for c_ in cmds_of(p_)), "TAB5 FIT the screen's packet carries no scrolling list")
    # SAFE: a forged token, a profile switch between draw and click
    l0_ = len(lines5())
    p_ = s_ev({"a": "pick:1", "t": "forged"}, "TAB5 SAFE forged token")
    K.check("The page changed" in cap5(p_) and int(SCB.STALE) >= 1 and SS.selU is None, "TAB5 SAFE a wrong page token = said + drawn again, nothing picked")
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p9"))
    p_ = s_ev({"a": "pick:1", "t": str(SS.tok)}, "TAB5 SAFE profile switch")
    K.check("Your profile changed" in cap5(p_) and SS.selU is None, "TAB5 SAFE a profile switch between draw and click = said, nothing happens")
    BR.remove("profile:fn:key")
    p_ = s_ev({"a": "pg:-1"}, "TAB5 the first page (a caption only)")
    K.check("first page" in cap5(p_), "TAB5 ACT < on the first page = a caption")
    p_ = s_ev({"a": "swno"}, "TAB5 redraw on the first profile")
    # ACT: Pick Bravo, then the actions
    p_ = s_ev({"a": "pick:1", "t": str(SS.tok)}, "TAB5 ACT Pick Bravo")
    cm = cmap(p_)
    K.check(str(SS.selU) == ub5 and txt5(cm, "St") == "Bravo" and "harness_other" in txt5(cm, "Ss") and vis5(cm, "Ar1") and vis5(cm, "Ar2")
            and vis5(cm, "R1N1") and "picked" in txt5(cm, "R1N1") and not vis5(cm, "R0N1"),
            "TAB5 ACT Pick = the picked line (name, where) + the 7 actions + Trade, the row marked")
    K.check(sorted(set(b_[2] for b_ in binds_of(p_) if '"pa:' in b_[2] or "pa:" in b_[2])) != [] and len([b_ for b_ in binds_of(p_) if "pa:" in b_[2]]) == 8
            and int(SCD.AN) == 8 and [str(x_) for x_ in SCD.XCMD] == ["trade %P"],
            "TAB5 ACT the 7 action buttons + Trade are bound (each with the page token)")
    old_ = str(SS.tok)
    p_ = s_ev({"a": "pa:3", "t": old_}, "TAB5 ACT Party invite")
    K.check(lines5()[l0_:] == ["party invite Bravo"] and not bool(SS.closed) and "/party invite Bravo  - see your chat" in cap5(p_) and int(SCB.ACTS) >= 1,
            "TAB5 ACT Party invite = /party invite Bravo as the player (the old page's line), the page stays with the caption (%s)" % lines5()[l0_:])
    p_ = s_ev({"a": "pa:3", "t": old_}, "TAB5 SAFE double click")
    K.check(lines5()[l0_:] == ["party invite Bravo"] and "The page changed" in cap5(p_), "TAB5 SAFE a double click on an action = ONE command")
    p_ = s_ev({"a": "pa:1", "t": str(SS.tok)}, "TAB5 FALL a missing command")
    K.check(lines5()[l0_:] == ["party invite Bravo"] and "/tpahere is not on this server" in cap5(p_), "TAB5 FALL Bring here without /tpahere = the old page's caption, no command (%s)" % cap5(p_))
    p_ = s_ev({"a": "pa:4", "t": str(SS.tok)}, "TAB5 FALL a refused permission")
    K.check(lines5()[l0_:] == ["party invite Bravo"] and "You do not have permission for /guild" in cap5(p_), "TAB5 ACT Guild invite without the permission = said, no command (%s)" % cap5(p_))
    p_ = s_ev({"a": "pa:0", "t": str(SS.tok)}, "TAB5 ACT Ask to TP")
    K.check(lines5()[l0_:] == ["party invite Bravo", "tpa Bravo"], "TAB5 ACT Ask to TP = /tpa Bravo")
    # fix (critic 1): Trade = SkyyEssentials' /trade <name> after the same checks; the page stays (a request)
    p_ = s_ev({"a": "pa:7", "t": str(SS.tok)}, "TAB5 FALL Trade without /trade")
    K.check(lines5()[l0_:] == ["party invite Bravo", "tpa Bravo"] and "/trade is not on this server" in cap5(p_) and not bool(SS.closed),
            "TAB5 FIX1 Trade without SkyyEssentials = the 'not on this server' caption, no command (%s)" % cap5(p_))
    E.CM.cmds.put("trade", CMDOK)
    old_ = str(SS.tok)
    p_ = s_ev({"a": "pa:7", "t": old_}, "TAB5 ACT Trade")
    K.check(lines5()[l0_:] == ["party invite Bravo", "tpa Bravo", "trade Bravo"] and not bool(SS.closed) and "/trade Bravo  - see your chat" in cap5(p_),
            "TAB5 FIX1 Trade = /trade Bravo as the player, the page stays with the caption (%s)" % lines5()[l0_:])
    p_ = s_ev({"a": "pa:7", "t": old_}, "TAB5 SAFE double click on Trade")
    K.check(lines5()[l0_:].count("trade Bravo") == 1 and "The page changed" in cap5(p_), "TAB5 FIX1 a double click on Trade = ONE request")
    E.CM.cmds.put("trade", Ucls.allocateInstance(JClass("skyymenu63.NoPerm").class_))
    p_ = s_ev({"a": "pa:7", "t": str(SS.tok)}, "TAB5 FALL Trade refused")
    K.check(lines5()[l0_:].count("trade Bravo") == 1 and "You do not have permission for /trade" in cap5(p_), "TAB5 FIX1 Trade without the permission = said, no command")
    E.CM.cmds.put("trade", CMDOK)
    p_ = s_ev({"a": "pa:9", "t": str(SS.tok)}, "TAB5 SAFE junk action")
    K.check("No such action" in cap5(p_), "TAB5 SAFE an unknown action = a caption")
    p_ = s_ev({"a": "leave", "t": str(SS.tok)}, "TAB5 ACT Leave party")
    K.check(lines5()[l0_:] == ["party invite Bravo", "tpa Bravo", "trade Bravo", "party leave"] and not bool(SS.closed), "TAB5 ACT Leave party = /party leave, the page stays")
    K.check(cap5(p_) == str(SCD.LEFTCAP) and "updates on your next click" in cap5(p_), "TAB5 FIX4 Leave party caption says the card updates on the next click (%s)" % cap5(p_))
    # the picked player goes offline
    byU.remove(PB5.pr.getUuid())
    p_ = s_ev({"a": "pa:3", "t": str(SS.tok)}, "TAB5 SAFE picked player offline")
    K.check(lines5()[l0_:] == ["party invite Bravo", "tpa Bravo", "trade Bravo", "party leave"] and "went offline" in cap5(p_) and SS.selU is None,
            "TAB5 SAFE the picked player gone offline = said, the pick cleared, no command")
    byU.put(PB5.pr.getUuid(), PB5.pr)
    # Visit island (close = true): the page closes first, the line once
    p_ = s_ev({"a": "pick:1", "t": str(SS.tok)}, "TAB5 ACT Pick Bravo again")
    old_ = str(SS.tok)
    s_ev({"a": "pa:2", "t": old_}, "TAB5 ACT Visit island", n=None)
    K.check(bool(SS.closed) and lines5()[-1] == "island visit Bravo", "TAB5 ACT Visit island = the page closed + /island visit Bravo (the old page's close flag)")
    s_ev({"a": "pa:2", "t": old_}, "TAB5 SAFE double click on a closing action", n=0, page=SS)
    K.check(lines5().count("island visit Bravo") == 1, "TAB5 SAFE a double click on Visit island = ONE command")
    # PROFILES: Switch -> Confirm / Cancel
    SS, p_ = s_open("TAB5 reopen")
    p_ = s_ev({"a": "sw:1", "t": str(SS.tok)}, "TAB5 ACT Switch")
    cm = cmap(p_)
    K.check(vis5(cm, "Fq") and "Switch to Iron?" in txt5(cm, "FqT") and str(SS.ask) == "2" and len([b_ for b_ in binds_of(p_) if "swok" in b_[2]]) == 1,
            "TAB5 ACT Switch = the confirm row (Switch to Iron? Confirm / Cancel), nothing run yet")
    p_ = s_ev({"a": "swno"}, "TAB5 ACT Cancel")
    K.check(not vis5(cmap(p_), "Fq") and SS.ask is None and "profiles switch 2" not in lines5(), "TAB5 ACT Cancel = the row gone, nothing run")
    p_ = s_ev({"a": "swok", "t": str(SS.tok)}, "TAB5 SAFE Confirm with nothing asked")
    K.check("Press Switch on a profile first" in cap5(p_) and "profiles switch 2" not in lines5(), "TAB5 SAFE Confirm with nothing asked = a caption")
    p_ = s_ev({"a": "sw:0", "t": str(SS.tok)}, "TAB5 SAFE Switch on the active")
    K.check("No profile there" in cap5(p_) or "already on that profile" in cap5(p_), "TAB5 SAFE the active profile has no Switch (%s)" % cap5(p_))
    p_ = s_ev({"a": "sw:1", "t": str(SS.tok)}, "TAB5 ACT Switch again")
    BR.put("profile:busy:" + uk5, TRUE)
    p_ = s_ev({"a": "swok", "t": str(SS.tok)}, "TAB5 SAFE a busy profile")
    K.check("already running" in cap5(p_) and "profiles switch 2" not in lines5() and not bool(SS.closed), "TAB5 SAFE profile:busy = said, no switch")
    BR.remove("profile:busy:" + uk5)
    p_ = s_ev({"a": "sw:1", "t": str(SS.tok)}, "TAB5 ACT Switch once more")
    old_ = str(SS.tok)
    s_ev({"a": "swok", "t": old_}, "TAB5 ACT Confirm", n=None)
    K.check(bool(SS.closed) and lines5()[-1] == "profiles switch 2", "TAB5 ACT Confirm = the page closed + /profiles switch 2 (SkyyProfiles' own command, its refusals)")
    s_ev({"a": "swok", "t": old_}, "TAB5 SAFE double Confirm", n=0, page=SS)
    K.check(lines5().count("profiles switch 2") == 1, "TAB5 SAFE a double Confirm = ONE switch")
    # links to the old pages (each ONE packet)
    for a_, what in (("full", "Full page"), ("stats", "Stats page"), ("prof", "Profiles page"), ("party", "Party page"), ("guild", "Guild page")):
        SS, p_ = s_open("TAB5 reopen for " + what)
        f0_ = len(E.sent(PK))
        SS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": a_}))
        cur_ = PK.pm.getCustomPage()
        K.check(len(pages(PK, f0_)) == 1, "TAB5 LINK %s = the old page's route, ONE packet (%s)" % (what, None if cur_ is None else cur_.getClass().getSimpleName()))
    # a throwing party bridge: the rest still draws
    BR.put("party:fn:members", Fn(lambda o: 1 // 0))
    SS, p_ = s_open("TAB5 reopen with a throwing party bridge")
    K.check(txt5(cmap(p_), "Gn") == "Wardens  [SW]" and txt5(cmap(p_), "Am") == "No party yet - pick a player and press Party invite.",
            "TAB5 FALL a throwing party:fn:members = no party shown, the rest still draws")
    BR.put("party:fn:members", f_mem5)
    # TABS
    SS, p_ = s_open("TAB5 reopen for tabs")
    p_ = s_ev({"a": "tab:5"}, "TAB5 TABS Social")
    K.eq(cap5(p_), "You are on Social", "TAB5 TABS Social = a caption")
    p_ = s_ev({"a": "tab:4"}, "TAB5 TABS World")
    WS5 = PK.pm.getCustomPage()
    K.check(WS5 is not None and str(WS5.getClass().getSimpleName()) == "WorldTab" and bool(SS.closed), "TAB5 TABS World = the world screen")
    p_ = s_ev({"a": "tab:5"}, "TAB5 OPEN the world screen's Social tab")
    SS = PK.pm.getCustomPage()
    K.check(SS is not None and str(SS.getClass().getSimpleName()) == "SocialTab" and bool(WS5.closed), "TAB5 OPEN the world screen's Social tab = the social screen")
    p_ = s_ev({"a": "tab:1"}, "TAB5 TABS Skills")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and bool(SS.closed), "TAB5 TABS Skills = the skill page")
    p_ = s_ev({"a": "tab:5"}, "TAB5 OPEN the skill page's Social tab")
    SS = PK.pm.getCustomPage()
    K.check(SS is not None and str(SS.getClass().getSimpleName()) == "SocialTab", "TAB5 OPEN the skill page's Social tab = the social screen")
    p_ = s_ev({"a": "tab:0"}, "TAB5 TABS Inventory")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "c", "TAB5 TABS Inventory = the inventory screen")
    BR.put("pets:fn:tab", Fn(f_tab))
    BR.put("pets:fn:tabact", Fn(f_act))
    p_ = one(ev(PK, {"a": "pet"}), "TAB5 the pets screen")
    PS5 = PK.pm.getCustomPage()
    p_ = s_ev({"a": "tab:5"}, "TAB5 OPEN the pets screen's Social tab")
    SS = PK.pm.getCustomPage()
    K.check(str(PS5.getClass().getSimpleName()) == "PetsTab" and SS is not None and str(SS.getClass().getSimpleName()) == "SocialTab" and bool(PS5.closed),
            "TAB5 OPEN the pets screen's Social tab = the social screen")
    p_ = s_ev({"a": "tab:2"}, "TAB5 TABS Pets")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "PetsTab", "TAB5 TABS Pets = the pets screen")
    for k_ in ("pets:fn:tab", "pets:fn:tabact"):
        BR.remove(k_)
    BR.put("bazaar:fn:tab", Fn(f_btab))
    BR.put("bazaar:fn:tabact", Fn(f_bact))
    SS, p_ = s_open("TAB5 reopen for Market")
    p_ = s_ev({"a": "tab:3"}, "TAB5 TABS Market")
    MS5 = PK.pm.getCustomPage()
    K.check(MS5 is not None and str(MS5.getClass().getSimpleName()) == "MarketTab" and bool(SS.closed), "TAB5 TABS Market = the market screen")
    p_ = s_ev({"a": "tab:5"}, "TAB5 OPEN the market screen's Social tab")
    SS = PK.pm.getCustomPage()
    K.check(SS is not None and str(SS.getClass().getSimpleName()) == "SocialTab" and bool(MS5.closed), "TAB5 OPEN the market screen's Social tab = the social screen")
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact"):
        BR.remove(k_)
    p_ = s_ev({"a": "tab:6"}, "TAB5 TABS Settings")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(SS.closed), "TAB5 TABS Settings = our Settings page")
    SS, p_ = s_open("TAB5 reopen for the Tab key")
    ST.tab(PK.ref, PK.st, PK.pr, PK.pl, "test")
    K.check(PK.pm.getCustomPage() is None and bool(SS.closed), "TAB5 TABS the Tab key closes the social screen")
    SS, p_ = s_open("TAB5 reopen for X")
    SS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(PK.pm.getCustomPage() is None and bool(SS.closed), "TAB5 TABS X closes the screen")
    K.notes.append("TAB5 counters: opens %d, stale %d, commands run %d, lines %s" % (int(SCB.OPENS), int(SCB.STALE), int(SCB.ACTS), lines5()[l0_:]))
    for k_ in WK5 + ("profile:class:" + ua5, "skill:overall:" + ua5, "party:name:" + uk5, "party:name:" + ub5, "party:stats:" + uk5, "party:stats:" + ub5):
        BR.remove(k_)
    for P_ in (PB5, PA5, PC5):
        byU.remove(P_.pr.getUuid())
    E.UniH.PL.clear()
    for p0_ in PL5:
        E.UniH.PL.add(p0_)
    E.PLAYERS.clear()
    for p0_ in EP5:
        E.PLAYERS.add(p0_)
    for cn_ in ("tpa", "tpahere", "island", "party", "guild", "profiles", "trade"):
        E.CM.cmds.remove(cn_)
        if CMD5[cn_] is not None:
            E.CM.cmds.put(cn_, CMD5[cn_])
    E.pump(PK)
'''
T.rep('''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
''', HARNESS_TAB5 + '''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
''')
if T.dst:
    T.finish()
