"""Derive SkyyMenu/build_skyymenu_0.3.71.py + SkyyMenu/test_skyymenu_0.3.71.py from the SET pin SkyyMenu 0.3.70 (generated - never re-run
its patch). Run:  python tools/menu_0_3_71_patch.py   then   python SkyyMenu/build_skyymenu_0.3.71.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.71.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyProfiles 0.1.19 (tools/profiles_0_1_19_patch.py: profile:fn:act) for Manage profiles and
SkyyParty 0.1.11 (tools/party_0_1_11_patch.py: party:fn:act) for Manage party; with the older jars those two views say which version they
need (the rest of the Social tab works as 0.3.70).

0.3.71 (2026-11-24, round oldmenu3) = OLD MENU FOLLOW-UP F6: THE SOCIAL TAB = THE OLD PLAYERS / STATS / PROFILES / PARTY PAGES. Skyy's words
(docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu
compleatly, so instead of adding things like the full tree button, just build it all into the new system and remove the old "Full tree"";
2026-11-23 "looks better. go head and build everything on your list." + the queued OPEN-QUESTIONS line 'Social tab Message / Add friend'
[yes, Message first; Add friend after checking the game's friends list]. Each part calls the SAME server code as the old page (no duplicated
rule, no new number):
  F6a PLAYERS (social:players gone): the top bar's Full page button is gone. What the old Players page had beyond the 7 actions + Trade:
      its two bottom tiles - ACCEPT TP (= /tpaccept, the page closes first: the old tile's cmdc) and DENY TP (= /tpdeny, the page stays) -
      are a row under the actions, through the same runLine checks (the command exists, the permission). MESSAGE (the queued question,
      default yes): a typed box + Message on the picked player = /msg <name> <text> (SkyyEssentials' own /msg; the same runLine checks;
      the text is cleaned: no quotes / backslashes / control characters, 120 at most). ADD FRIEND is NOT built: no friends system exists
      (vanilla's only "friend" command is the single-player PlayFriendCommand; no SkyWynn / pack mod keeps friends) - Message only.
      The players list shows 8 a page (was 10) to make room.
  F6b STATS (character:stats gone): "All stats" on the You card = the STATS VIEW of this screen: the old Stats page's rows -
      StatsCalc.allRows (Main, Combat, Gathering with the by-source table, Elements, Reactions, the Sources legend) - 20 a page (< >),
      StatsCalc.header + SUB, Refresh = read again. The rows are drawn at run time (row group + labels in the Style Guide 15 colours:
      stat names soft white, totals gold, sources dim, by-source cells green / red / dim / white = StatsCalc.cellCol / rxCol).
  F6c PROFILES (character:profiles gone): "Manage" on the Profiles card = the PROFILES VIEW: every profile the old list draws
      (profile:fn:act list = ProfilePage.shownIds - active / live / deleted with its undo line) with SWITCH (the confirm row, then /profiles
      switch <n> - as the Profiles card), RENAME (a typed name, Save / Enter = profile:fn:act rename = ProfStore.renameProfile), DELETE (only
      where the old page shows it; the confirm row = profile:fn:act delask, Confirm = delete = ProfDel.delete) and RESTORE (= ProfDel.restore);
      NEW PROFILE: the class cards (profile:fn:act roster - Pick, Selected, Coming later), the suggested name + Other name (newname =
      ProfNames.pick), Create profile = cancreate (the old page's checks, nothing made) then create (= createFirst / createAndSwitch: the
      class kit + the switch; the screen closes first when the switch follows, its answer then comes in chat).
  F6d PARTY (social:party gone): "Manage party" on the Party card = the PARTY VIEW: the members (Health / Stamina / Mana / where, the health
      bar, Leader), Promote / Kick (leader, other members) and TPA (another online member, SkyyEssentials), the invite box (typed name +
      Invite / Enter), the pending invite (Accept / Decline + its seconds), Accept TPA, Leave party, Disband party (TWO presses like the
      page: the first arms it for 10 s, any other click clears it) - every one = party:fn:act (SkyyParty 0.1.11 = PartyStore / PartyPage).
  STILL OLD (OLD_LEFT keeps social:guild, follow-up round): the GUILD page (create / invites / members + ranks with promote / demote / kick /
      leader transfer / the guild bank with typed amounts and daily limits / the log) is a whole system - SkyyGuilds needs its own
      guild:fn:act op set (one round of its own); the Guild card's Guild page button stays. Never half-wired.
  SAFETY: every new action carries the page token (an older drawing = "The page changed", nothing runs) and the profile key (a profile
      switch between drawing and click = nothing runs); every action redraws (a new token), so a double click never runs twice; SkyyProfiles /
      SkyyParty re-check under their own locks (a stale Delete = "already deleted", a stale Accept = "already in a party").
  ONE SCREEN, FOUR VIEWS: the page data carries a section letter per line (0 = the frame, H = the home cards, S / P / A = a view); build()
      appends the frame + the current view only (the element budget = the frame + the biggest view; nothing hidden is sent).
New: no class / command / system / picture / lang key / setting / saved data. OLD_LEFT: social:players, character:stats, character:profiles,
social:party out (19 -> 15).
ROLLBACK to 0.3.70: safe alone (nothing saved; the old links come back). SkyyProfiles 0.1.19 / SkyyParty 0.1.11 each roll back alone (Menu
then names the version Manage / Manage party needs).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.70.py"), os.path.join(MOD, "build_skyymenu_0.3.71.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.70.py"), os.path.join(MOD, "test_skyymenu_0.3.71.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.70"\n') and P.has("OLD_LEFT = sorted(set([") and P.has("fillModRows") and not P.has("SkyyStabSvL"), "not the generated SkyyMenu 0.3.70 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.70: OLD MENU FOLLOW-UPS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.71: OLD MENU FOLLOW-UP F6 - THE SOCIAL TAB: no Full page; Accept TP / Deny TP + Message (/msg) on the players panel; All stats (the old Stats
       page's rows), Manage (profiles: switch / rename / delete / restore / new - SkyyProfiles 0.1.19 profile:fn:act) and Manage party (invite /
       accept / decline / promote / kick / TPA / leave / disband - SkyyParty 0.1.11 party:fn:act) are views of the Social screen; OLD_LEFT lost
       4 rows, the Guild page stays (notes: tools/menu_0_3_71_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.71.py.
0.3.70: OLD MENU FOLLOW-UPS''')
P.rep('VERSION = "0.3.70"\n', 'VERSION = "0.3.71"\n')

# ======================================================================= F6a: the players panel (8 a page, Message, Accept / Deny TP), no Full page
P.rep('''SC_PN, SC_RH = 10, 48                                       # the players list: 10 a page (nothing scrolls)''',
      '''SC_PN, SC_RH = 8, 48                                        # the players list: 8 a page (nothing scrolls; 0.3.71: was 10 - room for Message + TP)''')
P.rep('''SC_TXT = {
    "cap0": "Pick a player for their actions. Tabs on top.",''', '''SC_MGW = 110                                                # 0.3.71: the Message button
SC_MSGMAX = 120                                             # 0.3.71: a typed message's length (the box and SocialTab.cleanMsg)
SC_TXT = {
    "cap0": "Pick a player for their actions. Tabs on top.",''')
P.rep('''    "left": "/party leave  - see your chat. The party card updates on your next click.",
}''', '''    "left": "/party leave  - see your chat. The party card updates on your next click.",
    # 0.3.71 (F6): the views' fixed lines
    "pvold": "Manage needs SkyyProfiles 0.1.19 - this server has an older one. /profiles works.",
    "pvoff": "Profiles are not on this server right now.",
    "avold": "Manage party needs SkyyParty 0.1.11 - this server has an older one. /party works.",
    "avoff": "Parties are not on this server right now.",
    "disq": "Click Disband again within 10 s to disband the party - everyone leaves it.",
    "msgnone": "Type a message in the box first, then press Message.",
    "chat": "Party chat: /pc <message>",
    "vcap": "The Social tab on top shows your cards again.",
}''')
P.rep('''    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(SC + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))''',
      '''    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % (sp + 128)))   # 0.3.71: no Full page (the old Players page is in this screen)''')
P.rep('''    ap.append(("#" + pl, lab(SC + "An", "", 12, "dim", w=SC_LI, h=18, anchor={"top": 6})))
    ap.sets.append((SC + "An", "Text", SC_TXT["anote"]))
    assert 20 + 24 + 8 + SC_PN * (SC_RH + 6) + 6 + 28 + 10 + 26 + 20 + 8 + 34 + 6 + 34 + 6 + 18 <= IV_BODY_H, "0.3.63: the players panel fits"''',
      '''    # 0.3.71 (F6a): Message on the picked player (a typed box + Message = /msg <name> <text>) and the old page's Accept / Deny TP tiles
    mr = SC + "Mr"
    ap.append(("#" + pl, G_.glass_group(mr, SC_LI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + mr, G_.text_field(SC + "MqBox", SC + "Mq", w=SC_LI - SC_MGW - 4, h=32, placeholder="Type a message", max_length=SC_MSGMAX, size=13,
                                       anchor={"right": 4})))
    ap.append(("#" + mr, G_.glass_button(SC + "Mgo", "Message", "primary", w=SC_MGW, h=34, size=13)))
    tr = SC + "Tr"
    ap.append(("#" + pl, G_.glass_group(tr, SC_LI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + tr, lab(SC + "Trl", "Teleport requests to you", 13, "dim", bold=True, w=SC_LI - 2 * (SC_AW + 4), h=34)))
    ap.append(("#" + tr, G_.glass_button(SC + "Tpa", "Accept TP", "primary", w=SC_AW, h=34, size=13, anchor={"right": 4})))
    ap.append(("#" + tr, G_.glass_button(SC + "Tpd", "Deny TP", "secondary", w=SC_AW, h=34, size=13)))
    ap.append(("#" + pl, lab(SC + "An", "", 12, "dim", w=SC_LI, h=18, anchor={"top": 6})))
    ap.sets.append((SC + "An", "Text", SC_TXT["anote"]))
    assert SUI.text_width("Teleport requests to you", 13, bold=True) <= SC_LI - 2 * (SC_AW + 4), "0.3.71: the TP row label fits"
    assert 20 + 24 + 8 + SC_PN * (SC_RH + 6) + 6 + 28 + 10 + 26 + 20 + 8 + 34 + 6 + 34 + 6 + 34 + 6 + 34 + 6 + 18 <= IV_BODY_H, "0.3.63: the players panel fits"''')
# the You / Profiles / Party cards' buttons = this screen's views (the ids stay)
P.rep('''    ap.append(("#" + yu, G_.glass_button(SC + "Ystats", "Stats page", "secondary", w=160, h=34, size=14, anchor={"top": 10})))''',
      '''    ap.append(("#" + yu, G_.glass_button(SC + "Ystats", "All stats", "secondary", w=160, h=34, size=14, anchor={"top": 10})))   # 0.3.71: the stats view''')
P.rep('''    ap.append(("#" + fb, G_.glass_button(SC + "Fpage", "Profiles page", "secondary", w=160, h=34, size=14)))''',
      '''    ap.append(("#" + fb, G_.glass_button(SC + "Fpage", "Manage", "secondary", w=160, h=34, size=14)))   # 0.3.71: the profiles view''')
P.rep('''    ap.append(("#" + ab, G_.glass_button(SC + "Apage", "Party page", "secondary", w=160, h=34, size=14)))''',
      '''    ap.append(("#" + ab, G_.glass_button(SC + "Apage", "Manage party", "secondary", w=160, h=34, size=14)))   # 0.3.71: the party view''')
P.rep('''    binds = [("#%sT%d" % (SC, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + SC + "Close", "close"), ("#" + SC + "Full", "full"),''',
      '''    binds = [("#%sT%d" % (SC, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + SC + "Close", "close"),''')

# ======================================================================= the VIEWS (S stats, P profiles, A party) + the section letters
SC_VIEWS_PY = r'''

# ---- 0.3.71 (F6): THE SOCIAL SCREEN'S VIEWS - each one fills the body's place (the frame, the top bar and the hint row stay). The page
# data carries a section letter per line: 0 = always, H = the home cards, S = stats, P = profiles, A = party; build() appends the frame +
# the current one only.
SC_VI = IV_IW - 20                                          # a view's inner width (1536)
SC_VBW = 160                                                # a view head's buttons
SV_N, SV_RH = 20, 30                                        # STATS: 20 rows a page, 30 high
SV_NW, SV_VW, SV_CW, SV_TW = 340, 170, 130, 170             # a row's name, its value, a by-source cell, the table's total
SV_SW = SC_VI - 16 - SV_NW - SV_VW - 12                     # a plain row's source line
SV_HW = SC_VI - 16 - SV_NW - 4                              # a head row's note
assert SV_NW + 6 * SV_CW + SV_TW + 16 <= SC_VI and SV_SW > 300, "0.3.71: a by-source row fits the view"
PV_N, PV_RH = 10, 50                                        # PROFILES: 10 profile rows (the old list's LIST_MAX scrolls; more = the head line)
PV_LW = 900
PV_RW = SC_VI - PV_LW - 10                                  # NEW PROFILE (626)
PV_BW = 100
PV_TW = PV_LW - 16 - 90 - 4 * (PV_BW + 4) - 8               # a profile row's text column
PC_N, PC_RH = 10, 46                                        # the class cards (the old page draws up to MAX_CARDS = 12; 10 here, the rest named)
PC_TW = PV_RW - 16 - 16 - 104 - 8
AV_N, AV_RH = 10, 58                                        # PARTY: 10 members (SkyyParty's maxSize goes to 10)
AV_LW = 1060                                                # fix: + Message / Trade per member (LOCKED 2026-10-10 party menu)
AV_RW = SC_VI - AV_LW - 10                                  # 466
AV_BW = 96
AV_TW = AV_LW - 16 - 5 * (AV_BW + 4) - 8
AV_BARW = AV_TW - 20
assert PV_TW >= 300 and PC_TW >= 300 and AV_TW >= 500 and AV_RW - 16 >= 160 + 6 + 200, (PV_TW, PC_TW, AV_TW, AV_RW)
for _l in ("Switch", "Rename", "Delete", "Restore", "Pick", "Promote", "Kick", "TPA", "Message", "Trade", "Save", "Cancel", "Confirm", "Invite", "Accept", "Decline"):
    assert SUI.text_width(_l, 13, bold=True) <= min(PV_BW, AV_BW) - 12, ("0.3.71: a view button fits", _l)
for _l in ("Refresh", "Other name", "Accept TPA", "Leave party"):
    assert SUI.text_width(_l, 14, bold=True) <= SC_VBW - 12, ("0.3.71: a view head button fits", _l)
# the stats view's run-time markup (a row group + its labels; {I} = the id, {C} = the colour - only a #rrggbb from SocialTab.hexOf)
_SV_IDQ, _SV_COLQ = "SkyyStabZzq", "#abcdef"


def _sv_tpl(mk):
    assert mk.count(_SV_IDQ) == 1, mk
    return mk.replace(_SV_IDQ, "{I}").replace(_SV_COLQ, "{C}")


SV_T = {
    "row": _sv_tpl(SUI.glass_group(_SV_IDQ, SC_VI, SV_RH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 2})),
    "name": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 15, _SV_COLQ, w=SV_NW, h=SV_RH)),
    "val": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 15, _SV_COLQ, bold=True, w=SV_VW, h=SV_RH, halign="End")),
    "src": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 13, _SV_COLQ, w=SV_SW, h=SV_RH, anchor={"left": 12})),
    "cell": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 14, _SV_COLQ, bold=True, w=SV_CW, h=SV_RH, halign="Center")),
    "tot": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 15, _SV_COLQ, bold=True, w=SV_TW, h=SV_RH, halign="End")),
    "head": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 16, _SV_COLQ, bold=True, w=SV_NW, h=SV_RH)),
    "note": _sv_tpl(SUI.glass_label(_SV_IDQ, "", 12, _SV_COLQ, w=SV_HW, h=SV_RH, anchor={"left": 4})),
}
for _k, _t in SV_T.items():
    _s = _t.replace("{I}", "SkyyStabSvR0" if _k == "row" else "SkyyStabSvR0N").replace("{C}", ST_ABS)
    SUI.check_markup(_s, prefix=SC, kit_paths=True)
    assert "@" not in _t and "\n" not in _t and _t.count("{I}") == 1 and (_k == "row" or _t.count("{C}") == 1), ("0.3.71: a stats markup line Java can hold", _k)
AV_FILL = "Group { Anchor: (Width: {W}, Height: 6); Background: %s; }" % SUI.glass_col("health")
SUI.check_markup(AV_FILL.replace("{W}", "40"), prefix=SC, kit_paths=True)
_sv_mk = [SV_T[_k].replace("{I}", "SkyyStabSvR0" if _k == "row" else "SkyyStabSvR0N").replace("{C}", ST_ABS) for _k in SV_T] + [AV_FILL.replace("{W}", "40")]
_sv_tok = SUI.proven_tokens(_sv_mk)
assert not [k_ for k_, g_ in _sv_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], "0.3.71: the view markups are proven"
SV_RUNTIME_MAX = SV_N * (1 + 1 + 6 + 1)                     # a by-source row: the row + the name + 6 cells + the total
AV_RUNTIME_MAX = AV_N                                       # a health fill per member


def _sc_views():
    G_ = SUI
    lab = G_.glass_label
    win = SC + "Win"
    out = []

    def vhead(ap, parent, v, title, extra=()):
        hd = SC + v + "h"
        ap.append(("#" + parent, G_.glass_group(hd, SC_VI, 34, layout="Left")))
        ap.append(("#" + hd, lab(None, title, 16, "accentHi", bold=True, w=240, h=34)))
        rest = SC_VI - 240 - len(extra) * (SC_VBW + 6)   # no back button (menu pattern): the Social tab on top = the cards
        ap.append(("#" + hd, lab(SC + v + "H", "", 13, "text", w=rest, h=34)))
        for ident, text, kind in extra:
            ap.append(("#" + hd, G_.glass_button(ident, text, kind, w=SC_VBW, h=34, size=14, anchor={"left": 6})))
    # ======== S: THE STATS VIEW (the old Stats page's rows, 20 a page)
    ap = SUI.Appends()
    sv = SC + "Sv"
    ap.append(("#" + win, G_.glass_group(sv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    vhead(ap, sv, "Sv", "YOUR STATS", [(SC + "SvRf", "Refresh", "secondary")])
    ap.append(("#" + sv, lab(SC + "SvS", "", 12, "dim", w=SC_VI, h=20, anchor={"top": 4})))
    ap.append(("#" + sv, G_.glass_group(SC + "SvL", SC_VI, SV_N * (SV_RH + 2), layout="Top", anchor={"top": 6})))
    pr = SC + "SvP"
    ap.append(("#" + sv, G_.glass_group(pr, SC_VI, 30, layout="Left", anchor={"top": 8})))
    ap.append(("#" + pr, G_.glass_button(SC + "SvPp", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
    ap.append(("#" + pr, lab(SC + "SvPg", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
    ap.append(("#" + pr, G_.glass_button(SC + "SvPn", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))
    assert 20 + 34 + 24 + 6 + SV_N * (SV_RH + 2) + 8 + 30 <= IV_BODY_H, "0.3.71: the stats view fits"
    out.append(("S", ap, [("#" + SC + "SvRf", "svrf"), ("#" + SC + "SvPp", "svpg:-1"), ("#" + SC + "SvPn", "svpg:1")]))
    # ======== P: THE PROFILES VIEW (the old Profiles page: the list + Create profile)
    ap = SUI.Appends()
    pv = SC + "Pv"
    ap.append(("#" + win, G_.glass_group(pv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    vhead(ap, pv, "Pv", "YOUR PROFILES")
    bh = IV_BODY_H - 20 - 34 - 6
    pb = SC + "Pvb"
    ap.append(("#" + pv, G_.glass_group(pb, SC_VI, bh, layout="Left", anchor={"top": 6})))
    pl = SC + "PvL"
    ap.append(("#" + pb, G_.glass_group(pl, PV_LW, bh, layout="Top")))
    for k_ in range(PV_N):
        r = "%sPvR%d" % (SC, k_)
        ap.append(("#" + pl, G_.glass_group(r, PV_LW, PV_RH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", PV_TW, PV_RH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + r + "X", lab(r + "N", "", 15, "row", bold=True, w=PV_TW, h=26, anchor={"top": 3})))
        ap.append(("#" + r + "X", lab(r + "S", "", 11, "dim", w=PV_TW, h=18)))
        hm, kids = SUI.keep_holder(r + "T", 90, PV_RH, [SUI.keep_at0(lab(r + "A", "ACTIVE", 12, "green", bold=True, w=90, h=PV_RH, halign="Center")),
                                                        SUI.keep_at0(lab(r + "D", "DELETED", 12, ST_BAD, bold=True, w=90, h=PV_RH, halign="Center"))])
        ap.append(("#" + r, hm))
        ap.extend(kids)
        for b_, t_, kd_ in (("W", "Switch", "primary"), ("E", "Rename", "secondary"), ("Q", "Delete", "secondary"), ("R", "Restore", "primary")):
            ap.append(("#" + r, G_.glass_button(r + b_, t_, kd_, w=PV_BW, h=30, size=13, anchor={"left": 4, "top": 10})))
    q = SC + "Pvq"
    ap.append(("#" + pl, G_.glass_group(q, PV_LW, 36, layout="Left", anchor={"top": 4})))
    ap.append(("#" + q, lab(SC + "Pvqt", "", 13, "action", bold=True, w=PV_LW - 2 * (PV_BW + 4) - 8, h=36, anchor={"right": 8})))
    ap.append(("#" + q, G_.glass_button(SC + "Pvyes", "Confirm", "primary", w=PV_BW, h=30, size=13, anchor={"right": 4})))
    ap.append(("#" + q, G_.glass_button(SC + "Pvno", "Cancel", "secondary", w=PV_BW, h=30, size=13)))
    rn = SC + "Pvn"
    ap.append(("#" + pl, G_.glass_group(rn, PV_LW, 36, layout="Left", anchor={"top": 4})))
    ap.append(("#" + rn, lab(SC + "Pvnt", "", 13, "text", w=320, h=36, anchor={"right": 8})))
    ap.append(("#" + rn, G_.text_field(SC + "PvnfBox", SC + "Pvnf", w=PV_LW - 320 - 8 - 2 * (PV_BW + 4), h=32, placeholder="New name", max_length=24, size=13,
                                       anchor={"right": 4})))
    ap.append(("#" + rn, G_.glass_button(SC + "Pvnok", "Save", "primary", w=PV_BW, h=30, size=13, anchor={"right": 4})))
    ap.append(("#" + rn, G_.glass_button(SC + "Pvnno", "Cancel", "secondary", w=PV_BW, h=30, size=13)))
    assert PV_N * (PV_RH + 4) + 40 + 40 <= bh, "0.3.71: the profile list fits"
    ap.append(("#" + pb, "Group { Anchor: (Width: 10); }"))
    pc = SC + "PvC"
    ap.append(("#" + pb, G_.glass_group(pc, PV_RW, bh, role="inset", layout="Top", pad=8)))
    ap.append(("#" + pc, lab(None, "NEW PROFILE", 15, "accentHi", bold=True, w=PV_RW - 16, h=24)))
    ap.append(("#" + pc, lab(SC + "PvCs", "", 12, "dim", w=PV_RW - 16, h=20)))
    for k_ in range(PC_N):
        c = "%sPvK%d" % (SC, k_)
        ap.append(("#" + pc, G_.glass_group(c, PV_RW - 16, PC_RH, role="panel", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 4})))
        ap.append(("#" + c, G_.glass_group(c + "X", PC_TW, PC_RH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + c + "X", lab(c + "N", "", 15, "accentHi", bold=True, w=PC_TW, h=24, anchor={"top": 2})))
        ap.append(("#" + c + "X", lab(c + "S", "", 11, "dim", w=PC_TW, h=18)))
        hm, kids = SUI.keep_holder(c + "H", 104, PC_RH, [SUI.keep_at0(G_.glass_button(c + "P", "Pick", "secondary", w=100, h=30, size=13, anchor={"top": 8})),
                                                         SUI.keep_at0(lab(c + "L", "Selected", 13, "green", bold=True, w=100, h=PC_RH, halign="Center")),
                                                         SUI.keep_at0(lab(c + "Z", "Coming later", 12, "dim", bold=True, w=100, h=PC_RH, halign="Center"))])
        ap.append(("#" + c, hm))
        ap.extend(kids)
    nm = SC + "PvM"
    ap.append(("#" + pc, G_.glass_group(nm, PV_RW - 16, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + nm, lab(None, "Name", 13, "dim", bold=True, w=70, h=34)))
    ap.append(("#" + nm, lab(SC + "PvMn", "", 15, "title", bold=True, w=PV_RW - 16 - 70 - SC_VBW - 6, h=34)))
    ap.append(("#" + nm, G_.glass_button(SC + "PvMr", "Other name", "secondary", w=SC_VBW, h=32, size=13, anchor={"left": 6})))
    gr = SC + "PvG"
    ap.append(("#" + pc, G_.glass_group(gr, PV_RW - 16, 36, layout="Left", anchor={"top": 6})))
    ap.append(("#" + gr, G_.glass_button(SC + "PvGo", "Create profile", "primary", w=180, h=34, size=14, anchor={"right": 8})))
    ap.append(("#" + gr, lab(SC + "PvGn", "", 12, "dim", w=PV_RW - 16 - 188, h=36)))
    assert 16 + 24 + 20 + PC_N * (PC_RH + 4) + 40 + 42 <= bh, "0.3.71: the new profile card fits"
    out.append(("P", ap, [("#" + SC + "Pvno", "pvno"), ("#" + SC + "Pvnno", "pvrnno")]))
    # ======== A: THE PARTY VIEW (the old party page)
    ap = SUI.Appends()
    av = SC + "Av"
    ap.append(("#" + win, G_.glass_group(av, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    vhead(ap, av, "Av", "PARTY")
    ab = SC + "Avb"
    ap.append(("#" + av, G_.glass_group(ab, SC_VI, bh, layout="Left", anchor={"top": 6})))
    al = SC + "AvL"
    ap.append(("#" + ab, G_.glass_group(al, AV_LW, bh, layout="Top")))
    for k_ in range(AV_N):
        r = "%sAvR%d" % (SC, k_)
        ap.append(("#" + al, G_.glass_group(r, AV_LW, AV_RH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", AV_TW, AV_RH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + r + "X", G_.glass_group(r + "Y", AV_TW, 22, layout="Left", anchor={"top": 4})))
        ap.append(("#" + r + "Y", lab(r + "N", "", 15, "row", bold=True, w=AV_TW - 120, h=22)))
        ap.append(("#" + r + "Y", lab(r + "T", "", 12, "xp", bold=True, w=120, h=22, halign="End")))
        ap.append(("#" + r + "X", lab(r + "S", "", 12, "text", w=AV_TW, h=18)))
        ap.append(("#" + r + "X", 'Group #%sB { Anchor: (Width: %d, Height: 6, Top: 2); LayoutMode: Left; Background: %s; }' % (r, AV_BARW, IV_TRACK)))
        for b_, t_ in (("P", "Promote"), ("K", "Kick"), ("G", "TPA"), ("M", "Message"), ("R", "Trade")):
            ap.append(("#" + r, G_.glass_button(r + b_, t_, "secondary", w=AV_BW, h=30, size=13, anchor={"left": 4, "top": 14})))
    assert AV_N * (AV_RH + 4) <= bh and 4 + 22 + 18 + 2 + 6 <= AV_RH, "0.3.71: the member list fits"
    ap.append(("#" + ab, "Group { Anchor: (Width: 10); }"))
    ac = SC + "AvC"
    ap.append(("#" + ab, G_.glass_group(ac, AV_RW, bh, role="inset", layout="Top", pad=8)))
    ap.append(("#" + ac, lab(None, "INVITE A PLAYER", 12, "dim", bold=True, w=AV_RW - 16, h=20)))
    ai = SC + "AvI"
    ap.append(("#" + ac, G_.glass_group(ai, AV_RW - 16, 34, layout="Left", anchor={"top": 4})))
    ap.append(("#" + ai, G_.text_field(SC + "AvFBox", SC + "AvF", w=AV_RW - 16 - AV_BW - 4, h=32, placeholder="Player name", max_length=32, size=13,
                                       anchor={"right": 4})))
    ap.append(("#" + ai, G_.glass_button(SC + "AvGo", "Invite", "primary", w=AV_BW, h=34, size=13)))
    ap.append(("#" + ac, lab(SC + "AvIh", "", 12, "dim", w=AV_RW - 16, h=20, anchor={"top": 2})))
    ap_ = SC + "AvP"
    ap.append(("#" + ac, G_.glass_group(ap_, AV_RW - 16, 74, layout="Top", anchor={"top": 12})))
    ap.append(("#" + ap_, lab(SC + "AvPt", "", 13, "action", bold=True, w=AV_RW - 16, h=30)))
    apb = SC + "AvPb"
    ap.append(("#" + ap_, G_.glass_group(apb, AV_RW - 16, 34, layout="Left", anchor={"top": 4})))
    ap.append(("#" + apb, G_.glass_button(SC + "AvPy", "Accept", "primary", w=AV_BW, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + apb, G_.glass_button(SC + "AvPn", "Decline", "secondary", w=AV_BW, h=34, size=13)))
    at = SC + "AvT"
    ap.append(("#" + ac, G_.glass_group(at, AV_RW - 16, 74, layout="Top", anchor={"top": 12})))
    ap.append(("#" + at, lab(SC + "AvTt", "", 13, "action", bold=True, w=AV_RW - 16, h=30)))
    ap.append(("#" + at, G_.glass_button(SC + "AvTy", "Accept TPA", "primary", w=SC_VBW, h=34, size=13, anchor={"top": 4})))
    aa = SC + "AvA"
    ap.append(("#" + ac, G_.glass_group(aa, AV_RW - 16, 34, layout="Left", anchor={"top": 16})))
    ap.append(("#" + aa, G_.glass_button(SC + "AvLv", "Leave party", "secondary", w=SC_VBW, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + aa, G_.glass_button(SC + "AvDb", "Disband party", "secondary", w=200, h=34, size=13)))
    ap.append(("#" + ac, lab(SC + "AvCh", "", 12, "dim", w=AV_RW - 16, h=20, anchor={"top": 10})))
    assert 16 + 20 + 38 + 22 + 86 + 86 + 50 + 30 <= bh, "0.3.71: the party card fits"
    assert SUI.text_width("Click again to disband", 13, bold=True) <= 200 - 12, "0.3.71: the armed Disband label fits"
    out.append(("A", ap, []))
    return out
'''
P.rep('''SC_AP, SC_BINDS = _sc_page()
SUI.check_page(SC_AP, SC)
for _p, _mk in SC_AP:
    SUI.check_markup(_mk, prefix=SC, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.63: the social screen never scrolls"
_sc_ids = set(i_ for _p, mk_ in SC_AP for i_ in SUI._static_ids(mk_))''', SC_VIEWS_PY.lstrip("\n") + '''

SC_AP0, SC_BINDS = _sc_page()
SC_VIEWS = _sc_views()
# 0.3.71: the home cards = the body group and everything inside it (section H); the views go in before the hint row (the window's next child)
_sc_home = set([SC + "Body"])
SC_SEC = []
for _p, _mk in SC_AP0:
    _ids = set(SUI._static_ids(_mk))
    _pid = None if _p is None else SUI.render(_p).lstrip("#")
    if (SC + "Body") in _ids or _pid in _sc_home:
        _sc_home |= _ids
        SC_SEC.append("H")
    else:
        SC_SEC.append("0")
_hi = [k_ for k_, (_p, _mk) in enumerate(SC_AP0) if (SC + "Hints") in SUI._static_ids(_mk)]
assert len(_hi) == 1 and SC_SEC[:_hi[0]].count("H") > 100 and "H" not in SC_SEC[_hi[0]:], "0.3.71: the home cards come right before the hint row"
SC_AP = SUI.Appends(list(SC_AP0[:_hi[0]]))
SC_SECA = SC_SEC[:_hi[0]]
for _v, _vap, _vb in SC_VIEWS:
    SC_AP.extend(_vap)
    SC_SECA += [_v] * len(_vap)
SC_AP.extend(SUI.Appends(list(SC_AP0[_hi[0]:])))
SC_SECA += SC_SEC[_hi[0]:]
SC_AP.sets = list(SC_AP0.sets)
for _v, _vap, _vb in SC_VIEWS:
    SC_AP.sets.extend(_vap.sets)
assert len(SC_SECA) == len(SC_AP)
SUI.check_page(SC_AP, SC)
for _p, _mk in SC_AP:
    SUI.check_markup(_mk, prefix=SC, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.63: the social screen never scrolls"
_sc_ids = set(i_ for _p, mk_ in SC_AP for i_ in SUI._static_ids(mk_))
_sc_vsec = {}
for _v, _vap, _vb in SC_VIEWS:
    for _p, _mk in _vap:
        for _i in SUI._static_ids(_mk):
            _sc_vsec[_i] = _v
_sc_sec_of = lambda i_: "H" if i_ in _sc_home else _sc_vsec.get(i_, "0")''')
P.rep('''SC_DYN = (["Coins", "Close", "Full", "Cap", "Pc", "Pp", "Pg", "Pn", "St", "Ss", "An", "Yn", "Y2", "Y3", "P1", "P2", "Ystats", "Fc", "Fq", "FqT",''',
      '''SC_DYN = (["Coins", "Close", "Cap", "Pc", "Pp", "Pg", "Pn", "St", "Ss", "An", "Yn", "Y2", "Y3", "P1", "P2", "Ystats", "Fc", "Fq", "FqT",
           "Mr", "Mq", "Mgo", "Tr", "Tpa", "Tpd",   # 0.3.71 (F6a); no Full page
           "SvH", "SvRf", "SvS", "SvL", "SvPp", "SvPg", "SvPn", "PvH", "Pvq", "Pvqt", "Pvyes", "Pvno", "Pvn", "Pvnt", "Pvnf",
           "Pvnok", "Pvnno", "PvCs", "PvMn", "PvMr", "PvGo", "PvGn", "AvH", "AvF", "AvGo", "AvIh", "AvP", "AvPt", "AvPy", "AvPn", "AvT",
           "AvTt", "AvTy", "AvA", "AvLv", "AvDb", "AvCh"]
          + ["PvR%d%s" % (k_, x_) for k_ in range(PV_N) for x_ in ("", "N", "S", "A", "D", "W", "E", "Q", "R")]
          + ["PvK%d%s" % (k_, x_) for k_ in range(PC_N) for x_ in ("", "N", "S", "P", "L", "Z")]
          + ["AvR%d%s" % (k_, x_) for k_ in range(AV_N) for x_ in ("", "N", "T", "S", "B", "P", "K", "G", "M", "R")]
          + [''')
P.rep('''_sc_tok = SUI.proven_tokens(list(SC_AP))''', '''_sc_tok = SUI.proven_tokens(list(SC_AP))
assert "SkyyStabFull" not in _sc_ids, "0.3.71: the social screen has no Full page (no old Players page link)"''')
P.rep('''SC_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9]+)?\\s*\\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in SC_AP)
SC_RUNTIME_MAX = SC_MN + 1                                     # a health fill per member + the guild XP fill
SC_ELEMENTS = SC_SHELL_ELEMENTS + SC_RUNTIME_MAX''', '''_sc_cnt = lambda mk_: len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9]+)?\\s*\\{", SUI._strip_quoted(SUI.render(mk_))))
# 0.3.71: one packet = the frame + ONE section (the home cards or a view) - the budget is the frame + the biggest section
_sc_by = {}
for (_p, _mk), _s in zip(SC_AP, SC_SECA):
    _sc_by[_s] = _sc_by.get(_s, 0) + _sc_cnt(_mk)
_sc_rt = {"H": SC_MN + 1, "S": SV_RUNTIME_MAX, "P": 0, "A": AV_RUNTIME_MAX}   # run time: the home fills / the stats rows / the member fills
SC_SHELL_ELEMENTS = _sc_by["0"] + max(_sc_by[_s] for _s in "HSPA")
SC_RUNTIME_MAX = max(_sc_rt.values())
SC_ELEMENTS = _sc_by["0"] + max(_sc_by[_s] + _sc_rt[_s] for _s in "HSPA")
print("0.3.71 social sections (elements, + at run time): frame %d, %s" % (_sc_by["0"], ", ".join("%s %d + %d" % (_s, _sc_by[_s], _sc_rt[_s]) for _s in "HSPA")))''')
P.rep('''SC_LK, SC_LP, SC_LB = [], [], []
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
assert SC_LK[0] == "A" and SC_LP[0] == "", "0.3.63: the page data starts with the root"''', '''SC_LK, SC_LP, SC_LB, SC_LS = [], [], [], []
for (_p, _mk), _s in zip(SC_AP, SC_SECA):
    SC_LK.append("A")
    SC_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    SC_LB.append(SUI.render(_mk))
    SC_LS.append(_s)
for _i, _pr, _v in SC_AP.sets:
    SC_LK.append("S")
    SC_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    SC_LB.append(_v)
    SC_LS.append(_sc_sec_of(SUI.render(_i).lstrip("#")))
for _s, _a in SC_BINDS + [b_ for _v, _vap, _vb in SC_VIEWS for b_ in _vb]:
    SC_LK.append("E")
    SC_LP.append(_s)
    SC_LB.append(_a)
    SC_LS.append(_sc_sec_of(_s.lstrip("#")))
for _v, _vap, _vb in SC_VIEWS:
    assert all(_sc_sec_of(s_.lstrip("#")) == _v for s_, _a in _vb), "0.3.71: a view's bindings name its own elements"
assert SC_LK[0] == "A" and SC_LP[0] == "" and SC_LS[0] == "0", "0.3.63: the page data starts with the root"
assert all(_sc_sec_of(s_.lstrip("#")) in ("0", "H") for s_, _a in SC_BINDS), "0.3.71: the home bindings are frame / home elements"''')

# ---- the SocialTabData: the sections + the views' numbers, texts and run-time markup
P.rep('''F(scd, "public static final String[] XCMD = %s;" % jarr(SC_XCMD))   # fix: the actions after the old page's 7 (Trade)''',
      '''F(scd, "public static final String[] XCMD = %s;" % jarr(SC_XCMD))   # fix: the actions after the old page's 7 (Trade)
# 0.3.71 (F6): the section letter of each page data line (0 frame / H home / S stats / P profiles / A party) + the views
F(scd, "public static final String LS = %s;" % jstr("".join(SC_LS)))
for _n, _v in (("SVN", SV_N), ("PVN", PV_N), ("PCN", PC_N), ("AVN", AV_N), ("AVBARW", AV_BARW), ("MSGMAX", SC_MSGMAX)):
    F(scd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("SROW", SV_T["row"]), ("SNAME", SV_T["name"]), ("SVAL", SV_T["val"]), ("SSRC", SV_T["src"]), ("SCELL", SV_T["cell"]),
               ("STOT", SV_T["tot"]), ("SHEAD", SV_T["head"]), ("SNOTE", SV_T["note"]), ("AVFILL", AV_FILL),
               ("C_ABS", ST_ABS), ("C_GOLD", ST_GOLD), ("C_DIM", ST_DIM), ("C_ACC", SUI.glass_col("accentHi")),
               ("PVOLD", SC_TXT["pvold"]), ("PVOFF", SC_TXT["pvoff"]), ("AVOLD", SC_TXT["avold"]), ("AVOFF", SC_TXT["avoff"]),
               ("DISQ", SC_TXT["disq"]), ("MSGNONE", SC_TXT["msgnone"]), ("CHAT", SC_TXT["chat"]), ("VCAP", SC_TXT["vcap"])):
    F(scd, "public static final String %s = %s;" % (_n, jstr(_v)))''')
P.rep('''           "public String ask;", "public String askName;", "public String[] fids;", "public String[] fnames;",''',
      '''           "public String ask;", "public String askName;", "public String[] fids;", "public String[] fnames;",
           # 0.3.71 (F6): the view (0 home, 1 stats, 2 profiles, 3 party) and each view's state
           "public int view;", "public int svPage;", "public int svPages;", "public String[] pvIds;", "public String[] pvSt;", "public String[] pvNames;",
           "public String[] pcNames;", "public String[] pcOn;", "public String pcls;", "public String pname;", "public String pAsk;", "public String pAskId;",
           "public String pAskText;", "public String pRen;", "public String pRenText;", "public boolean pvFirst;", "public String[] avIds;",
           "public String avTpa;", "public boolean avLead;", "public long disArm;", "public String msgKeep;", "public String invKeep;",''')
P.rep('''  this.fnames = new String[0];
  this.builds = 0;''', '''  this.fnames = new String[0];
  this.view = 0;           // 0.3.71 (F6)
  this.svPage = 0;
  this.svPages = 1;
  this.pvIds = new String[0];
  this.pvSt = new String[0];
  this.pvNames = new String[0];
  this.pcNames = new String[0];
  this.pcOn = new String[0];
  this.pcls = null;
  this.pname = "";
  this.pAsk = null;
  this.pAskId = null;
  this.pAskText = "";
  this.pRen = null;
  this.pRenText = "";
  this.pvFirst = false;
  this.avIds = new String[0];
  this.avTpa = null;
  this.avLead = false;
  this.disArm = 0L;
  this.msgKeep = "";
  this.invKeep = "";
  this.builds = 0;''')

# ---- the home cards' texts (the views replace the old pages)
P.rep('''        b.set("#" + r + "N.Text", !on ? "Profiles are not on this server right now" : "No profile yet - the Profiles page makes one");''',
      '''        b.set("#" + r + "N.Text", !on ? "Profiles are not on this server right now" : "No profile yet - Manage makes one");   // 0.3.71''')
P.rep('''  b.set("#SkyyStabFnote.Text", !on ? "" : (more > 0 ? "+" + more + " more on the Profiles page" : "New, rename, delete: the Profiles page"));''',
      '''  b.set("#SkyyStabFnote.Text", !on ? "" : (more > 0 ? "+" + more + " more - Manage shows them" : "New, rename, delete, restore: Manage"));   // 0.3.71''')
P.rep('''      : (n == 0 ? "No party yet - pick a player and press Party invite." : (more > 0 ? "+" + more + " more on the Party page" : "")));''',
      '''      : (n == 0 ? "No party yet - pick a player and press Party invite." : (more > 0 ? "+" + more + " more - Manage party shows them" : "")));   // 0.3.71''')
# the picked player: + Message (bound with the token, the kept text back in the box); the TP row is always there
P.rep('''  b.set("#SkyyStabAr1.Visible", on);
  b.set("#SkyyStabAr2.Visible", on);
  if (!on) return;
  for (int i = 0; i < @PKG@.SocialTabData.AN; i++)
    ev.addEventBinding(@BT@.Activating, "#SkyyStabA" + i, @EVD@.of("a", "pa:" + i).append("t", this.tok));''',
      '''  b.set("#SkyyStabAr1.Visible", on);
  b.set("#SkyyStabAr2.Visible", on);
  b.set("#SkyyStabMr.Visible", on);   // 0.3.71 (F6a): Message
  ev.addEventBinding(@BT@.Activating, "#SkyyStabTpa", @EVD@.of("a", "tpacc").append("t", this.tok));   // 0.3.71 (F6a): the old page's two tiles
  ev.addEventBinding(@BT@.Activating, "#SkyyStabTpd", @EVD@.of("a", "tpdeny").append("t", this.tok));
  if (!on) return;
  for (int i = 0; i < @PKG@.SocialTabData.AN; i++)
    ev.addEventBinding(@BT@.Activating, "#SkyyStabA" + i, @EVD@.of("a", "pa:" + i).append("t", this.tok));
  String mk = String.valueOf((char) 64) + "M";
  ev.addEventBinding(@BT@.Activating, "#SkyyStabMgo", @EVD@.of("a", "msg").append("t", this.tok).append(mk, "#SkyyStabMq.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyStabMq", @EVD@.of("a", "msg").append("t", this.tok).append(mk, "#SkyyStabMq.Value"), false);
  if (this.msgKeep != null && this.msgKeep.length() > 0) b.set("#SkyyStabMq.Value", this.msgKeep);''')

# ---- the views' fill methods + build (before build: methods before their callers)
FILL_JAVA = r'''# ---- 0.3.71 (F6): THE VIEWS. Helpers: a "+" / "-" / "=" answer without its mark; a colour that is a #rrggbb (else the stat white)
M(stab, r"""
public static String msgOf(Object r) {
  if (!(r instanceof String)) return "That did not work - try again.";
  String s = ((String) r).trim();
  if (s.length() > 0 && (s.charAt(0) == '+' || s.charAt(0) == '-' || s.charAt(0) == '=')) s = s.substring(1);
  return s.length() == 0 ? "Done." : @PKG@.MenuUtil.clip(s, 200);
}""")
M(stab, r"""
public static String hexOf(String c) {
  if (c == null || c.length() != 7 || c.charAt(0) != '#') return @PKG@.SocialTabData.C_ABS;
  for (int i = 1; i < 7; i++) {
    char x = c.charAt(i);
    if (!((x >= '0' && x <= '9') || (x >= 'a' && x <= 'f') || (x >= 'A' && x <= 'F'))) return @PKG@.SocialTabData.C_ABS;
  }
  return c;
}""")
# one run-time label: appended into the row with its colour, its text set after (never inline: no escaping)
M(stab, r"""
public static void slab(@UCB@ b, String row, String tpl, String id, String col, String text) {
  b.appendInline("#" + row, tpl.replace("{I}", id).replace("{C}", hexOf(col)));
  b.set("#" + id + ".Text", text == null ? "" : @PKG@.MenuUtil.clip(text, 160));
}""")
M(stab, r"""
public static String[] split(String s, String sep) {
  if (s == null) return new String[0];
  return s.split(sep, -1);
}""")
# THE STATS VIEW: StatsCalc.allRows = the old Stats page's rows (heads, the column head, by-source rows, plain rows), 20 a page
M(stab, r"""
public void fillStats(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  Object[] vit = null;
  try { vit = @PKG@.StatsCalc.vitals(this.pst, this.pref); } catch (Throwable t) { vit = null; }
  java.util.ArrayList rows = @PKG@.StatsCalc.allRows(u, vit);
  b.set("#SkyyStabSvH.Text", @PKG@.StatsCalc.header(u, this.playerRef.getUsername()));
  b.set("#SkyyStabSvS.Text", @PKG@.StatsCalc.SUB);
  int n = @PKG@.SocialTabData.SVN;
  this.svPages = (rows.size() + n - 1) / n;
  if (this.svPages < 1) this.svPages = 1;
  if (this.svPage >= this.svPages) this.svPage = this.svPages - 1;
  if (this.svPage < 0) this.svPage = 0;
  b.set("#SkyyStabSvPg.Text", "Page " + (this.svPage + 1) + " / " + this.svPages);
  int from = this.svPage * n;
  for (int k = 0; k < n; k++) {
    int j = from + k;
    if (j >= rows.size()) break;
    String[] r = (String[]) rows.get(j);
    String rid = "SkyyStabSvR" + k;
    b.appendInline("#SkyyStabSvL", @PKG@.SocialTabData.SROW.replace("{I}", rid));
    if (r[0] == null && r[1] == null) {
      boolean own = r.length >= 11;
      slab(b, rid, @PKG@.SocialTabData.SNAME, rid + "N", @PKG@.SocialTabData.C_DIM, own ? r[9] : @PKG@.StatsCalc.COL_STAT);
      for (int ck = 0; ck < 6; ck++) slab(b, rid, @PKG@.SocialTabData.SCELL, rid + "C" + ck, @PKG@.SocialTabData.C_DIM, own ? r[3 + ck] : @PKG@.StatsCalc.COLS[ck]);
      slab(b, rid, @PKG@.SocialTabData.STOT, rid + "V", @PKG@.SocialTabData.C_DIM, own ? r[10] : @PKG@.StatsCalc.COL_TOTAL);
      continue;
    }
    if (r[0] == null) {
      slab(b, rid, @PKG@.SocialTabData.SHEAD, rid + "N", @PKG@.SocialTabData.C_ACC, r[1]);
      slab(b, rid, @PKG@.SocialTabData.SNOTE, rid + "S", @PKG@.SocialTabData.C_DIM, r.length > 2 ? r[2] : "");
      continue;
    }
    if (r.length >= 9) {
      slab(b, rid, @PKG@.SocialTabData.SNAME, rid + "N", @PKG@.SocialTabData.C_ABS, r[0]);
      for (int ck = 0; ck < 6; ck++) {
        String cc = r.length >= 10 ? @PKG@.StatsCalc.rxCol(r, ck) : @PKG@.StatsCalc.cellCol(r[3 + ck], ck);
        slab(b, rid, @PKG@.SocialTabData.SCELL, rid + "C" + ck, cc, r[3 + ck]);
      }
      slab(b, rid, @PKG@.SocialTabData.STOT, rid + "V", @PKG@.SocialTabData.C_GOLD, r[1]);
      continue;
    }
    slab(b, rid, @PKG@.SocialTabData.SNAME, rid + "N", @PKG@.SocialTabData.C_ABS, r[0]);
    slab(b, rid, @PKG@.SocialTabData.SVAL, rid + "V", @PKG@.SocialTabData.C_GOLD, r.length > 1 ? r[1] : "");
    slab(b, rid, @PKG@.SocialTabData.SSRC, rid + "S", @PKG@.SocialTabData.C_DIM, r.length > 2 ? r[2] : "");
  }
}""")
# profile:fn:act (SkyyProfiles 0.1.19) as the player; null = not there (an older SkyyProfiles)
M(stab, r"""
public String pact(String op, String a1, String a2) {
  if (@PKG@.InvCraft.fn("profile:fn:act") == null) return null;
  Object r = call("profile:fn:act", new Object[] { op, this.playerRef.getUuid(), a1, a2 });
  return r instanceof String ? (String) r : "-That did not work - try again.";
}""")
M(stab, r"""
public String aact(String op, String arg) {
  if (@PKG@.InvCraft.fn("party:fn:act") == null) return null;
  Object r = call("party:fn:act", new Object[] { op, this.playerRef.getUuid(), arg });
  return r instanceof String ? (String) r : "That did not work - try again.";
}""")
# THE PROFILES VIEW: the old list's rows (profile:fn:act list) + Create profile (roster, the suggested name)
M(stab, r"""
public void pvHide(@UCB@ b, String head) {
  b.set("#SkyyStabPvH.Text", head);
  for (int k = 0; k < @PKG@.SocialTabData.PVN; k++) b.set("#SkyyStabPvR" + k + ".Visible", false);
  for (int k = 0; k < @PKG@.SocialTabData.PCN; k++) b.set("#SkyyStabPvK" + k + ".Visible", false);
  b.set("#SkyyStabPvq.Visible", false);
  b.set("#SkyyStabPvn.Visible", false);
  b.set("#SkyyStabPvM.Visible", false);
  b.set("#SkyyStabPvG.Visible", false);
  b.set("#SkyyStabPvCs.Text", "");
  this.pvIds = new String[0];
  this.pcNames = new String[0];
}""")
M(stab, r"""
public void fillPv(@UCB@ b, @UEB@ ev) {
  String ls = pact("list", null, null);
  if (ls == null) { pvHide(b, hasCmd("profiles") ? @PKG@.SocialTabData.PVOLD : @PKG@.SocialTabData.PVOFF); return; }
  if (ls.startsWith("-")) { pvHide(b, msgOf(ls)); return; }
  String[] lines = split(ls, String.valueOf((char) 10));
  String[] h = lines.length > 0 ? split(lines[0], "\\|") : new String[0];
  if (h.length < 9 || !h[0].equals("h")) { pvHide(b, "Your profiles could not be read right now - try again in a moment."); return; }
  int n = @PKG@.InvPage.toInt(h[1], 0);
  int max = @PKG@.InvPage.toInt(h[2], 0);
  boolean adm = "1".equals(h[3]);
  int nd = @PKG@.InvPage.toInt(h[4], 0);
  boolean room = "1".equals(h[6]);
  this.pvFirst = "1".equals(h[7]);
  String used = n + " of " + max + " profile slots used (" + h[5] + ").";
  if (n > max) used = n + " profiles - this server now allows " + max + ". You keep them all but cannot create more.";
  if (adm) used = n + " profiles - admins have no profile limit.";
  if (nd > 0) used = used + " A deleted profile does not use a slot.";
  int rows = lines.length - 1;
  if (rows > @PKG@.SocialTabData.PVN) used = used + " " + (rows - @PKG@.SocialTabData.PVN) + " more - /profiles list shows them.";
  b.set("#SkyyStabPvH.Text", @PKG@.MenuUtil.clip(used, 150));
  int pn = @PKG@.SocialTabData.PVN;
  this.pvIds = new String[pn];
  this.pvSt = new String[pn];
  this.pvNames = new String[pn];
  for (int k = 0; k < pn; k++) {
    String r = "SkyyStabPvR" + k;
    String[] f = k + 1 < lines.length ? split(lines[k + 1], "\\|") : new String[0];
    if (f.length < 7 || !f[0].equals("p")) {
      b.set("#" + r + ".Visible", k == 0 && rows <= 0);
      if (k == 0 && rows <= 0) {
        b.set("#" + r + "N.Text", "No profile yet - pick a class on the right");
        b.set("#" + r + "S.Text", "");
        b.set("#" + r + "A.Visible", false);
        b.set("#" + r + "D.Visible", false);
        b.set("#" + r + "W.Visible", false);
        b.set("#" + r + "E.Visible", false);
        b.set("#" + r + "Q.Visible", false);
        b.set("#" + r + "R.Visible", false);
      }
      continue;
    }
    String st = f[4];
    boolean act = st.equals("active");
    boolean live = act || st.equals("live");
    boolean del = st.equals("del");
    this.pvIds[k] = f[1];
    this.pvSt[k] = st;
    this.pvNames[k] = f[2];
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(f[2] + (f[3].length() > 0 ? "  -  " + f[3] : ""), 40));
    b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip(f[5], 70));
    b.set("#" + r + "A.Visible", act);
    b.set("#" + r + "D.Visible", !live);
    b.set("#" + r + "W.Visible", live && !act);
    b.set("#" + r + "E.Visible", live);
    b.set("#" + r + "Q.Visible", "1".equals(f[6]));
    b.set("#" + r + "R.Visible", del);
    if (live && !act) ev.addEventBinding(@BT@.Activating, "#" + r + "W", @EVD@.of("a", "pv:sw:" + k).append("t", this.tok));
    if (live) ev.addEventBinding(@BT@.Activating, "#" + r + "E", @EVD@.of("a", "pv:ren:" + k).append("t", this.tok));
    if ("1".equals(f[6])) ev.addEventBinding(@BT@.Activating, "#" + r + "Q", @EVD@.of("a", "pv:del:" + k).append("t", this.tok));
    if (del) ev.addEventBinding(@BT@.Activating, "#" + r + "R", @EVD@.of("a", "pv:res:" + k).append("t", this.tok));
  }
  boolean q = this.pAsk != null;
  b.set("#SkyyStabPvq.Visible", q);
  if (q) {
    b.set("#SkyyStabPvqt.Text", @PKG@.MenuUtil.clip(this.pAskText, 120));
    ev.addEventBinding(@BT@.Activating, "#SkyyStabPvyes", @EVD@.of("a", "pvyes").append("t", this.tok));
  }
  boolean rn = this.pRen != null && !q;
  b.set("#SkyyStabPvn.Visible", rn);
  if (rn) {
    String nm = this.pRen;
    for (int k = 0; k < this.pvIds.length; k++) if (this.pRen.equals(this.pvIds[k]) && this.pvNames[k] != null) nm = this.pvNames[k];
    b.set("#SkyyStabPvnt.Text", @PKG@.MenuUtil.clip("New name for " + nm + " - 2 to 16 letters", 48));
    b.set("#SkyyStabPvnf.Value", this.pRenText == null ? "" : this.pRenText);
    String nk = String.valueOf((char) 64) + "N";
    ev.addEventBinding(@BT@.Activating, "#SkyyStabPvnok", @EVD@.of("a", "pvrenok").append("t", this.tok).append(nk, "#SkyyStabPvnf.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyStabPvnf", @EVD@.of("a", "pvrenok").append("t", this.tok).append(nk, "#SkyyStabPvnf.Value"), false);
  }
  // NEW PROFILE: the class cards
  String ro = pact("roster", null, null);
  String[] cl = ro == null ? new String[0] : split(ro, String.valueOf((char) 10));
  int cn = @PKG@.SocialTabData.PCN;
  this.pcNames = new String[cn];
  this.pcOn = new String[cn];
  int shown = 0;
  for (int k = 0; k < cn; k++) {
    String c = "SkyyStabPvK" + k;
    String[] f = k < cl.length ? split(cl[k], "\\|") : new String[0];
    if (f.length < 8 || !f[0].equals("c")) { b.set("#" + c + ".Visible", false); continue; }
    shown++;
    boolean on = "1".equals(f[4]);
    boolean sel = on && this.pcls != null && this.pcls.equalsIgnoreCase(f[1]);
    this.pcNames[k] = f[1];
    this.pcOn[k] = on ? "1" : "0";
    b.set("#" + c + ".Visible", true);
    b.set("#" + c + "N.Text", @PKG@.MenuUtil.clip(f[1] + (f[3].length() > 0 ? "  -  " + f[3] : ""), 40));
    b.set("#" + c + "S.Text", @PKG@.MenuUtil.clip("Combat skill " + f[2] + " - " + f[5], 64));
    b.set("#" + c + "P.Visible", on && !sel);
    b.set("#" + c + "L.Visible", sel);
    b.set("#" + c + "Z.Visible", !on);
    if (on && !sel) ev.addEventBinding(@BT@.Activating, "#" + c + "P", @EVD@.of("a", "pc:" + k).append("t", this.tok));
  }
  String slots = this.pvFirst ? "Your first profile - everything you already have stays on it."
    : (room ? "This is profile " + (n + 1) + " of " + max + " - " + h[5] + "." : "All " + max + " profile slots are used - you cannot create another profile.");
  if (adm && !this.pvFirst) slots = "This is profile " + (n + 1) + " - admins have no profile limit.";
  if (cl.length > cn) slots = slots + " " + (cl.length - cn) + " more classes: /profiles create.";
  b.set("#SkyyStabPvCs.Text", @PKG@.MenuUtil.clip(slots, 110));
  boolean can = (room || adm || this.pvFirst) && shown > 0;
  b.set("#SkyyStabPvM.Visible", can);
  b.set("#SkyyStabPvG.Visible", can);
  if (!can) return;
  if (this.pname == null || this.pname.length() == 0) {
    String nn = pact("newname", null, null);
    this.pname = nn == null || nn.startsWith("-") ? "" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(nn), 24);
  }
  b.set("#SkyyStabPvMn.Text", this.pname);
  ev.addEventBinding(@BT@.Activating, "#SkyyStabPvMr", @EVD@.of("a", "pcname").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyStabPvGo", @EVD@.of("a", "pcgo").append("t", this.tok));
  b.set("#SkyyStabPvGn.Text", this.pcls == null ? "Pick a class first. It is locked to that profile forever."
    : @PKG@.MenuUtil.clip("Create " + this.pname + " as " + this.pcls + (this.pvFirst ? "." : " - you switch to it at once."), 70));
}""")
# THE PARTY VIEW: party:fn:act state + party:fn:members / party:name / party:stats (the page's own reads)
M(stab, r"""
public void avHide(@UCB@ b, String head) {
  b.set("#SkyyStabAvH.Text", head);
  for (int k = 0; k < @PKG@.SocialTabData.AVN; k++) b.set("#SkyyStabAvR" + k + ".Visible", false);
  b.set("#SkyyStabAvI.Visible", false);
  b.set("#SkyyStabAvIh.Text", "");
  b.set("#SkyyStabAvP.Visible", false);
  b.set("#SkyyStabAvT.Visible", false);
  b.set("#SkyyStabAvA.Visible", false);
  b.set("#SkyyStabAvCh.Text", "");
  this.avIds = new String[0];
  this.avTpa = null;
}""")
M(stab, r"""
public void fillAv(@UCB@ b, @UEB@ ev) {
  String s = aact("state", null);
  if (s == null) { avHide(b, hasCmd("party") ? @PKG@.SocialTabData.AVOLD : @PKG@.SocialTabData.AVOFF); return; }
  String[] f = split(s, "\\|");
  if (f.length < 12 || !f[0].equals("s")) { avHide(b, "Your party could not be read right now - try again in a moment."); return; }
  boolean in = "1".equals(f[1]);
  boolean lead = "1".equals(f[2]);
  this.avLead = lead;
  boolean ess = "1".equals(f[8]);
  String me = this.playerRef.getUuid().toString();
  b.set("#SkyyStabAvH.Text", in ? "Party " + f[3] + " / " + f[4] + " players." + (lead ? "  You lead it." : "") : "You are not in a party. Invite a player on the right, or accept an invite.");
  String[] mem = new String[0];
  try { mem = members(); } catch (Throwable t) { mem = new String[0]; }
  java.util.Map br = @PKG@.MenuUtil.bridge();
  int an = @PKG@.SocialTabData.AVN;
  this.avIds = new String[an];
  for (int k = 0; k < an; k++) {
    String r = "SkyyStabAvR" + k;
    if (k >= mem.length || mem[k] == null) { b.set("#" + r + ".Visible", false); continue; }
    String u = mem[k];
    boolean self = u.equals(me);
    this.avIds[k] = u;
    @PR@ p = null;
    try { p = @UNI@.get().getPlayer(java.util.UUID.fromString(u)); } catch (Throwable t) { p = null; }
    boolean on = p != null && p.isValid();
    String nm = text(br.get("party:name:" + u));
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(nm == null ? "A player" : nm), 24) + (self ? "  (you)" : ""));
    b.set("#" + r + "T.Text", k == 0 ? "Leader" : "");
    String st = text(br.get("party:stats:" + u));
    String[] v = st == null ? new String[0] : st.split(",", -1);
    if (v.length >= 7) {
      long hp = @PKG@.InvPage.toLong(v[0], 0L);
      long mx = @PKG@.InvPage.toLong(v[1], 0L);
      long mn = @PKG@.InvPage.toLong(v[5], 0L);
      String wh = on ? where(p) : "";
      b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip("Health " + hp + " / " + mx + "    Stamina " + v[2].trim() + " / " + v[3].trim() + "    "
        + (mn > 0L ? "Mana " + v[4].trim() + " / " + v[5].trim() : "Mana none") + (wh.length() > 0 ? "    " + wh : "") + (on ? "" : "    offline"), 100));
      int w = mx > 0L ? @PKG@.InvPage.barW(hp, mx, @PKG@.SocialTabData.AVBARW) : 0;
      if (w > 0) b.appendInline("#" + r + "B", @PKG@.SocialTabData.AVFILL.replace("{W}", String.valueOf(w)));
    } else b.set("#" + r + "S.Text", on ? "Health ..." : "Offline");
    b.set("#" + r + "P.Visible", lead && !self);
    b.set("#" + r + "K.Visible", lead && !self);
    b.set("#" + r + "G.Visible", ess && !self && on);
    b.set("#" + r + "M.Visible", !self && on);   // fix: Message / Trade per member (LOCKED 2026-10-10: "buttons for adding friend, message, trade")
    b.set("#" + r + "R.Visible", !self && on);
    if (!self && on) {
      ev.addEventBinding(@BT@.Activating, "#" + r + "M", @EVD@.of("a", "av:msg:" + k).append("t", this.tok));
      ev.addEventBinding(@BT@.Activating, "#" + r + "R", @EVD@.of("a", "av:trd:" + k).append("t", this.tok));
    }
    if (lead && !self) {
      ev.addEventBinding(@BT@.Activating, "#" + r + "P", @EVD@.of("a", "av:pro:" + k).append("t", this.tok));
      ev.addEventBinding(@BT@.Activating, "#" + r + "K", @EVD@.of("a", "av:kick:" + k).append("t", this.tok));
    }
    if (ess && !self && on) ev.addEventBinding(@BT@.Activating, "#" + r + "G", @EVD@.of("a", "av:tpa:" + k).append("t", this.tok));
  }
  // the invite box (Enter or Invite), the pending invite, Accept TPA, Leave / Disband
  b.set("#SkyyStabAvI.Visible", true);
  b.set("#SkyyStabAvIh.Text", "They must be online - the invite lasts " + f[5] + " s.");
  String pk = String.valueOf((char) 64) + "P";
  ev.addEventBinding(@BT@.Activating, "#SkyyStabAvGo", @EVD@.of("a", "av:inv").append("t", this.tok).append(pk, "#SkyyStabAvF.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyStabAvF", @EVD@.of("a", "av:inv").append("t", this.tok).append(pk, "#SkyyStabAvF.Value"), false);
  if (this.invKeep != null && this.invKeep.length() > 0) b.set("#SkyyStabAvF.Value", this.invKeep);
  boolean pend = !in && f[6].length() > 0;
  b.set("#SkyyStabAvP.Visible", pend);
  if (pend) {
    b.set("#SkyyStabAvPt.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[6]) + " invited you to their party  (" + f[7] + " s left)", 60));
    ev.addEventBinding(@BT@.Activating, "#SkyyStabAvPy", @EVD@.of("a", "av:acc").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyStabAvPn", @EVD@.of("a", "av:dec").append("t", this.tok));
  }
  this.avTpa = f[9].length() > 0 ? f[9] : null;
  b.set("#SkyyStabAvT.Visible", this.avTpa != null);
  if (this.avTpa != null) {
    b.set("#SkyyStabAvTt.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[10]) + ("1".equals(f[11]) ? " wants you to teleport to them" : " wants to teleport to you"), 60));
    ev.addEventBinding(@BT@.Activating, "#SkyyStabAvTy", @EVD@.of("a", "av:tpacc").append("t", this.tok));
  }
  b.set("#SkyyStabAvA.Visible", in);
  b.set("#SkyyStabAvLv.Visible", in);
  b.set("#SkyyStabAvDb.Visible", lead);
  if (in) ev.addEventBinding(@BT@.Activating, "#SkyyStabAvLv", @EVD@.of("a", "av:leave").append("t", this.tok));
  if (lead) {
    b.set("#SkyyStabAvDb.Text", this.disArm > System.currentTimeMillis() ? "Click again to disband" : "Disband party");
    ev.addEventBinding(@BT@.Activating, "#SkyyStabAvDb", @EVD@.of("a", "av:dis").append("t", this.tok));
  }
  b.set("#SkyyStabAvCh.Text", @PKG@.SocialTabData.CHAT);
}""")
'''
P.rep('''M(stab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.SocialTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.SocialTabData.LP[i];
    String y = @PKG@.SocialTabData.LB[i];''', FILL_JAVA + '''M(stab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.SocialTabData.LK;
  String ls = @PKG@.SocialTabData.LS;   // 0.3.71 (F6): the frame + the current section only
  char cur = this.view == 1 ? 'S' : (this.view == 2 ? 'P' : (this.view == 3 ? 'A' : 'H'));
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    char sc = ls.charAt(i);
    if (sc != '0' && sc != cur) continue;
    String x = @PKG@.SocialTabData.LP[i];
    String y = @PKG@.SocialTabData.LB[i];''')
P.rep('''  String[] mem = new String[0];
  try { mem = members(); } catch (Throwable t) { mem = new String[0]; }
  try { fillPlayers(b, ev, mem); } catch (Throwable t) { this.keys = new String[0]; @PKG@.MenuUtil.warn("social screen: the players list failed: " + t); }''',
      '''  if (this.view == 1) {   // 0.3.71 (F6): a view instead of the home cards
    try { fillStats(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: the stats view failed: " + t); }
  } else if (this.view == 2) {
    try { fillPv(b, ev); } catch (Throwable t) { this.pvIds = new String[0]; this.pcNames = new String[0]; @PKG@.MenuUtil.warn("social screen: the profiles view failed: " + t); }
  } else if (this.view == 3) {
    try { fillAv(b, ev); } catch (Throwable t) { this.avIds = new String[0]; @PKG@.MenuUtil.warn("social screen: the party view failed: " + t); }
  }
  if (this.view != 0) { b.set("#SkyyStabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.SocialTabData.VCAP); return; }
  String[] mem = new String[0];
  try { mem = members(); } catch (Throwable t) { mem = new String[0]; }
  try { fillPlayers(b, ev, mem); } catch (Throwable t) { this.keys = new String[0]; @PKG@.MenuUtil.warn("social screen: the players list failed: " + t); }''')
# the Social tab while a view is open = back to the cards
P.rep('''  if (i == 5) { say("You are on Social"); return; }''',
      '''  if (i == 5) {
    if (this.view != 0) { this.view = 0; this.tcap = ""; redraw(); return; }   // 0.3.71 (F6): a view open = back to the cards
    say("You are on Social");
    return;
  }''')

# ---- the views' actions (after swGo: runLine / redraw / say exist)
ACT_JAVA = r'''# ---- 0.3.71 (F6): the views' actions. Every one answers with ONE packet (a redraw with the answer in the caption, or the close).
M(stab, r"""
public void goView(int v) {
  this.answered = true;
  this.view = v;
  this.svPage = 0;
  this.pAsk = null;
  this.pRen = null;
  this.disArm = 0L;
  this.tcap = "";
  redraw();
}""")
# Message = /msg <name> <text> (SkyyEssentials' own command) through runLine's checks; the text: no quotes / backslashes / control chars
M(stab, r"""
public static String cleanMsg(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < @PKG@.SocialTabData.MSGMAX; i++) {
    char c = s.charAt(i);
    if (c < 32 || c == 127 || c == '"' || c == '\\') continue;
    sb.append(c);
  }
  return sb.toString().trim();
}""")
M(stab, r"""
public void msgSend(String typed) {
  this.answered = true;
  @PR@ t = sel();
  if (t == null) { this.selU = null; this.tcap = "That player went offline."; redraw(); return; }
  String txt = cleanMsg(typed);
  if (txt.length() == 0) { this.msgKeep = ""; this.tcap = @PKG@.SocialTabData.MSGNONE; redraw(); return; }
  String n = @PKG@.MenuUtil.cleanName(t.getUsername());
  if (n.length() == 0) { this.tcap = "That player's name cannot be used in a command."; redraw(); return; }
  this.msgKeep = txt;                        // kept when runLine refuses (its redraw puts it back in the box); runLine clears it when /msg runs
  runLine("msg " + n + " " + txt, false);
}""")
M(stab, r"""
public int pvRow(String a, int cut) {
  int k = @PKG@.InvPage.toInt(a.substring(cut), -1);
  if (k < 0 || this.pvIds == null || k >= this.pvIds.length || this.pvIds[k] == null) return -1;
  return k;
}""")
M(stab, r"""
public void pvSay(String r) {
  this.answered = true;
  this.tcap = r == null ? @PKG@.SocialTabData.PVOLD : msgOf(r);
  redraw();
}""")
M(stab, r"""
public void pvSw(int k) {
  this.answered = true;
  if (k < 0) { say("No profile there"); return; }
  if (!"live".equals(this.pvSt[k])) { this.tcap = "active".equals(this.pvSt[k]) ? "You are already on that profile." : "That profile cannot be switched to."; redraw(); return; }
  this.pRen = null;
  this.pAsk = "sw";
  this.pAskId = this.pvIds[k];
  this.pAskText = "Switch to " + this.pvNames[k] + "? Your inventory is saved and you go to the island of that profile.";
  this.tcap = "";
  redraw();
}""")
M(stab, r"""
public void pvDel(int k) {
  this.answered = true;
  if (k < 0) { say("No profile there"); return; }
  String r = pact("delask", this.pvIds[k], null);
  if (r != null && r.startsWith("=")) {
    this.pRen = null;
    this.pAsk = "del";
    this.pAskId = this.pvIds[k];
    this.pAskText = msgOf(r);
    this.tcap = "";
    redraw();
    return;
  }
  this.pAsk = null;
  pvSay(r);
}""")
M(stab, r"""
public void pvYes() {
  this.answered = true;
  String ask = this.pAsk;
  String id = this.pAskId;
  this.pAsk = null;
  if (ask == null || id == null) { say("Press Switch or Delete on a profile first"); return; }
  if (ask.equals("sw")) {
    if (Boolean.TRUE.equals(@PKG@.MenuUtil.bridge().get("profile:busy:" + this.playerRef.getUuid().toString()))) {
      this.tcap = "A profile switch is already running - try again in a moment.";
      redraw();
      return;
    }
    runLine("profiles switch " + id, true);
    return;
  }
  pvSay(pact("delete", id, null));
}""")
M(stab, r"""
public void pvRes(int k) {
  this.answered = true;
  if (k < 0) { say("No profile there"); return; }
  this.pAsk = null;
  this.pRen = null;
  pvSay(pact("restore", this.pvIds[k], null));
}""")
M(stab, r"""
public void pvRen(int k) {
  this.answered = true;
  if (k < 0) { say("No profile there"); return; }
  this.pAsk = null;
  this.pRen = this.pvIds[k];
  this.pRenText = this.pvNames[k] == null ? "" : this.pvNames[k];
  this.tcap = "";
  redraw();
}""")
M(stab, r"""
public void pvRenOk(String typed) {
  this.answered = true;
  String id = this.pRen;
  if (id == null) { say("Press Rename on a profile first"); return; }
  String t = typed == null ? "" : typed;
  if (t.length() > 40) t = t.substring(0, 40);
  String r = pact("rename", id, t);
  if (r != null && r.startsWith("+")) { this.pRen = null; this.pRenText = ""; }
  else this.pRenText = t;
  pvSay(r);
}""")
M(stab, r"""
public void pcPick(String a) {
  this.answered = true;
  int k = @PKG@.InvPage.toInt(a.substring(3), -1);
  if (k < 0 || this.pcNames == null || k >= this.pcNames.length || this.pcNames[k] == null) { say("No class there"); return; }
  if (!"1".equals(this.pcOn[k])) { this.tcap = this.pcNames[k] + " is coming later."; redraw(); return; }
  this.pcls = this.pcNames[k];
  this.tcap = "";
  redraw();
}""")
M(stab, r"""
public void pcName() {
  this.answered = true;
  String r = pact("newname", this.pname, null);
  if (r == null) { pvSay(null); return; }
  if (!r.startsWith("-")) this.pname = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(r), 24);
  this.tcap = "";
  redraw();
}""")
# Create profile: the old page's checks first (nothing made); the first profile = made here; another = the screen closes, then create +
# switch (createAndSwitch) - its refusal (rare after the checks) is said in chat, like /profiles switch
M(stab, r"""
public void pcGo() {
  this.answered = true;
  if (this.pcls == null) { this.tcap = "Pick a class first."; redraw(); return; }
  String ok = pact("cancreate", this.pcls, null);
  if (ok == null || !ok.startsWith("+")) { pvSay(ok); return; }
  String cls = this.pcls;
  String nm = this.pname == null ? "" : this.pname;
  this.pcls = null;
  if (this.pvFirst) {
    String r = pact("create", cls, nm);
    if (r != null && r.startsWith("+")) { this.pname = ""; this.tcap = "Profile created - you are " + cls + " for good on it."; redraw(); return; }
    this.pcls = cls;
    pvSay(r);
    return;
  }
  ACTS = ACTS + 1;
  shut();
  String r2 = pact("create", cls, nm);
  if (r2 != null && r2.startsWith("-")) {
    try { this.playerRef.sendMessage(@MSG@.raw("[Profiles] " + msgOf(r2))); } catch (Throwable t) { }
  }
}""")
M(stab, r"""
public void avSay(String r) {
  this.answered = true;
  this.tcap = r == null ? @PKG@.SocialTabData.AVOLD : @PKG@.MenuUtil.clip(r, 200);
  redraw();
}""")
M(stab, r"""
public void avRow(String op, String a, int cut) {
  this.answered = true;
  int k = @PKG@.InvPage.toInt(a.substring(cut), -1);
  if (k < 0 || this.avIds == null || k >= this.avIds.length || this.avIds[k] == null) { say("Nobody there"); return; }
  avSay(aact(op, this.avIds[k]));
}""")
# fix (LOCKED 2026-10-10 party menu): Message = that member becomes the picked player on the cards (the Message box: msgSend, /msg);
# Trade = the Social tab's Trade line (SocialTabData.XCMD = SkyyEssentials' /trade <name>) through runLine's checks
M(stab, r"""
public @PR@ avOn(String a, int cut) {
  int k = @PKG@.InvPage.toInt(a.substring(cut), -1);
  if (k < 0 || this.avIds == null || k >= this.avIds.length || this.avIds[k] == null) return null;
  if (this.avIds[k].equals(this.playerRef.getUuid().toString())) return null;
  try {
    @PR@ p = @UNI@.get().getPlayer(java.util.UUID.fromString(this.avIds[k]));
    return p != null && p.isValid() ? p : null;
  } catch (Throwable t) { return null; }
}""")
M(stab, r"""
public void avMsg(String a) {
  this.answered = true;
  @PR@ t = avOn(a, 7);
  if (t == null) { avSay("That player is not online."); return; }
  this.view = 0;
  this.disArm = 0L;
  this.selU = t.getUuid();
  this.msgKeep = "";
  this.tcap = @PKG@.MenuUtil.clip("Type your message to " + @PKG@.MenuUtil.safe(t.getUsername()) + " in the box, then press Message.", 200);
  redraw();
}""")
M(stab, r"""
public void avTrade(String a) {
  this.answered = true;
  @PR@ t = avOn(a, 7);
  if (t == null) { avSay("That player is not online."); return; }
  String n = @PKG@.MenuUtil.cleanName(t.getUsername());
  if (n.length() == 0) { avSay("That player's name cannot be used in a command."); return; }
  this.disArm = 0L;
  runLine(@PKG@.SocialTabData.XCMD[0].replace("%P", n), false);
}""")
M(stab, r"""
public void avInvite(String typed) {
  this.answered = true;
  String nm = @PKG@.MenuUtil.cleanName(typed);
  String r = aact("invite", nm);
  this.invKeep = r != null && r.startsWith("Invited ") ? "" : nm;
  avSay(r);
}""")
# Disband: two presses within 10 s like the page (a member's press = SkyyParty's refusal at once); any other click clears it
M(stab, r"""
public void avDisband(boolean armed) {
  this.answered = true;
  if (armed || !this.avLead) { this.disArm = 0L; avSay(aact("disband", null)); return; }
  this.disArm = System.currentTimeMillis() + 10000L;
  this.tcap = @PKG@.SocialTabData.DISQ;
  redraw();
}""")
'''
P.rep('''  runLine("profiles switch " + id, true);
}""")''', '''  runLine("profiles switch " + id, true);
}""")
''' + ACT_JAVA.rstrip("\n"))
P.rep('''    if (a.equals("full")) { hub("social", "players", "the Players page"); return; }
    if (a.equals("stats")) { hub("character", "stats", "the Stats page"); return; }
    if (a.equals("prof")) { hub("character", "profiles", "the Profiles page"); return; }
    if (a.equals("party")) { hub("social", "party", "the Party page"); return; }
    if (a.equals("guild")) { hub("social", "guild", "the Guild page"); return; }''',
      '''    // 0.3.71 (F6): the Stats / Profiles / Party pages are views of this screen (no Full page); the Guild page stays (OLD_LEFT)
    boolean armed = this.disArm > System.currentTimeMillis();
    if (!a.equals("av:dis")) this.disArm = 0L;
    if (a.equals("stats")) { goView(1); return; }
    if (a.equals("prof")) { goView(2); return; }
    if (a.equals("party")) { goView(3); return; }
    if (a.equals("svrf")) { this.tcap = ""; redraw(); return; }
    if (a.startsWith("svpg:")) {
      int ds = @PKG@.InvPage.toInt(a.substring(5), 0);
      int ns = this.svPage + (ds < 0 ? -1 : 1);
      if (ns < 0 || ns >= this.svPages) { say(ns < 0 ? "This is the first page" : "This is the last page"); return; }
      this.svPage = ns;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("pvno")) { this.pAsk = null; this.tcap = "Nothing changed."; redraw(); return; }
    if (a.equals("pvrnno")) { this.pRen = null; this.pRenText = ""; this.tcap = "Nothing changed."; redraw(); return; }
    if (a.equals("guild")) { hub("social", "guild", "the Guild page"); return; }''')
P.rep('''    if (a.startsWith("pick:")) { pick(@PKG@.InvPage.toInt(a.substring(5), -1)); return; }
    if (a.startsWith("pa:")) { act(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }''',
      '''    if (a.startsWith("pick:")) { pick(@PKG@.InvPage.toInt(a.substring(5), -1)); return; }
    if (a.startsWith("pa:")) { act(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    // 0.3.71 (F6): every view action below carries the token (checked above) - a double click / an older drawing never runs twice
    if (a.equals("msg")) { msgSend(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "M")); return; }
    if (a.equals("tpacc")) { runLine("tpaccept", true); return; }
    if (a.equals("tpdeny")) { runLine("tpdeny", false); return; }
    if (a.startsWith("pv:sw:")) { pvSw(pvRow(a, 6)); return; }
    if (a.startsWith("pv:del:")) { pvDel(pvRow(a, 7)); return; }
    if (a.startsWith("pv:res:")) { pvRes(pvRow(a, 7)); return; }
    if (a.startsWith("pv:ren:")) { pvRen(pvRow(a, 7)); return; }
    if (a.equals("pvyes")) { pvYes(); return; }
    if (a.equals("pvrenok")) { pvRenOk(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "N")); return; }
    if (a.startsWith("pc:")) { pcPick(a); return; }
    if (a.equals("pcname")) { pcName(); return; }
    if (a.equals("pcgo")) { pcGo(); return; }
    if (a.equals("av:inv")) { avInvite(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "P")); return; }
    if (a.equals("av:acc")) { avSay(aact("accept", null)); return; }
    if (a.equals("av:dec")) { avSay(aact("decline", null)); return; }
    if (a.equals("av:leave")) { avSay(aact("leave", null)); return; }
    if (a.equals("av:dis")) { avDisband(armed); return; }
    if (a.startsWith("av:pro:")) { avRow("promote", a, 7); return; }
    if (a.startsWith("av:kick:")) { avRow("kick", a, 8); return; }
    if (a.startsWith("av:tpa:")) { avRow("tpa", a, 7); return; }
    if (a.startsWith("av:msg:")) { avMsg(a); return; }
    if (a.startsWith("av:trd:")) { avTrade(a); return; }
    if (a.equals("av:tpacc")) {
      if (this.avTpa == null) { avSay("That request is gone - here is the page again."); return; }
      avSay(aact("tpaccept", this.avTpa));
      return;
    }''')

# runLine: a command that runs clears the kept message (only a refused /msg keeps its text in the box)
P.rep('''  ACTS = ACTS + 1;
  if (close) {
    shut();
    try { @CMGR@.get().handleCommand(this.playerRef, line); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: /" + line''', '''  ACTS = ACTS + 1;
  this.msgKeep = "";   // 0.3.71 (F6a)
  if (close) {
    shut();
    try { @CMGR@.get().handleCommand(this.playerRef, line); } catch (Throwable t) { @PKG@.MenuUtil.warn("social screen: /" + line''')
# ======================================================================= the ratchet: OLD_LEFT shrinks by the four rows this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"), ("character", "stats"),
    ("character", "profiles"), ("market", "auctions"), ("market", "bazaar"), ("market", "merchants"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"), ("social", "players"), ("social", "party"), ("social", "guild"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.71 (oldmenu3, F6): social:players (no Full page: Accept / Deny TP + Message in the screen), character:stats (the stats view),
# character:profiles (the profiles view - SkyyProfiles 0.1.19 profile:fn:act) and social:party (the party view - SkyyParty 0.1.11 party:fn:act)
# are gone. social:guild stays: the guild page (members + ranks, the guild bank, the log) needs SkyyGuilds ops of its own (a follow-up round).
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"),
    ("market", "auctions"), ("market", "bazaar"), ("market", "merchants"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"), ("social", "guild"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.71: no system / command / class"
_i = P.s.index
assert _i("public static String msgOf(Object r)") < _i("public void fillStats(@UCB@ b)") < _i("public void fillPv(@UCB@ b, @UEB@ ev)") \
    < _i("public void fillAv(@UCB@ b, @UEB@ ev)") < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.pref = ref;\n  this.pst = st;\n  String lk = @PKG@.SocialTabData.LK;") \
    < _i("public void runLine(String line, boolean close)") < _i("public void goView(int v)") < _i("public void avDisband(boolean armed)") \
    < _i("if (a.equals(\"av:dis\")) { avDisband(armed); return; }"), "0.3.71: methods before their callers"
assert 'hub("social", "players"' not in P.s and 'hub("character", "stats"' not in P.s and 'hub("character", "profiles"' not in P.s \
    and 'hub("social", "party"' not in P.s, "0.3.71: no old Players / Stats / Profiles / Party page link left in the new screens"
P.finish()


# ======================================================================= the HARNESS (every 0.3.70 check runs again on the 0.3.71 jar, plus OLD3)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


EXPECT_71 = '''EXPECT = {   # 0.3.71: the Social tab's views (stats / profiles / party), Message + Accept / Deny TP, no Full page, the version strings
@@EXPECT@@
}
'''
HARNESS_OLD3_STATIC = r'''    # ---- OLD3 (0.3.71; Skyy 11-22 "build it all into the new system"): the ratchet shrank by exactly the four rows this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("social", "players"), ("character", "stats"), ("character", "profiles"), ("social", "party")])
            and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 4 and ("social", "guild") in left2_,
            "OLD3 RATCHET OLD_LEFT lost social:players + character:stats + character:profiles + social:party, nothing added, the Guild page kept (%d -> %d; still: %s)"
            % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('G_.glass_button(SC + "Full"' not in g and '("#" + SC + "Full", "full")' not in g and 'hub("social", "players"' not in g
            and 'hub("character", "stats"' not in g and 'hub("character", "profiles"' not in g and 'hub("social", "party"' not in g
            and "0.3.71: the social screen has no Full page (no old Players page link)" in g and '"< Social"' not in g,
            "OLD3 STATIC no Full page, no Players / Stats / Profiles / Party page link, no back button on the views (the Social tab returns)")
    K.check('pact("delete", id, null)' in g and 'pact("rename", id, t)' in g and 'pact("cancreate", this.pcls, null)' in g and 'aact("disband", null)' in g
            and 'runLine("tpaccept", true)' in g and 'runLine("tpdeny", false)' in g and 'runLine("msg " + n + " " + txt, false)' in g
            and "StatsCalc.allRows(u, vit)" in g, "OLD3 STATIC the views call the old pages' code: profile:fn:act / party:fn:act ops, /tpaccept /tpdeny /msg, StatsCalc.allRows")
    K.check("0.3.71: the view markups are proven" in g and "0.3.71: the stats view fits" in g and "0.3.71: the profile list fits" in g
            and "0.3.71: the party card fits" in g and "0.3.71: the home cards come right before the hint row" in g,
            "OLD3 STATIC the build asserts every view fits 1080, its run-time markup is proven, the sections are in order")
'''
HARNESS_OLD3 = r'''    # ---- OLD3 (0.3.71, round oldmenu3): THE SOCIAL TAB = THE OLD PLAYERS / STATS / PROFILES / PARTY PAGES (the guild page stays)
    def sel_ok5(pk_):
        ids_ = set()
        for c_ in cmds_of(pk_):
            t_ = str(c_.text) if c_.text is not None else ""
            ids_ |= set(re.findall(r"#([A-Za-z0-9]+) *\{", t_))
        bad_ = []
        for c_ in cmds_of(pk_):
            s_ = str(c_.selector) if c_.selector is not None else ""
            t_ = str(c_.text) if c_.text is not None else ""
            if not s_:
                continue
            if s_.lstrip("#").split(".")[0] not in ids_:
                bad_.append(("append into " if t_ else "set ") + s_)
        for b_ in binds_of(pk_):
            if b_[1].lstrip("#") not in ids_:
                bad_.append("bind " + b_[1])
        return bad_

    def has5(pk_, ident):
        return any(re.search(r"#%s *\{" % ident, str(c_.text or "")) for c_ in cmds_of(pk_))
    for cn_ in ("msg", "tpaccept", "tpdeny", "trade"):
        CMD5[cn_] = E.CM.cmds.remove(cn_)
    SS, p_ = s_open("OLD3 open")
    K.check(has5(p_, "SkyyStabBody") and not has5(p_, "SkyyStabFull") and not has5(p_, "SkyyStabSv") and not has5(p_, "SkyyStabPv")
            and not has5(p_, "SkyyStabAv") and not sel_ok5(p_), "OLD3 OPEN the home packet = the frame + the cards only (no Full page, no view); every set / binding names a drawn element %s" % sel_ok5(p_)[:3])
    # F6a: Message + Accept / Deny TP
    p_ = s_ev({"a": "pick:1", "t": str(SS.tok)}, "OLD3 F6a pick Bravo")
    cm = cmap(p_)
    K.check(vis5(cm, "Mr") and len([b_ for b_ in binds_of(p_) if '"msg"' in b_[2] and "SkyyStabMq.Value" in b_[2]]) == 2
            and len([b_ for b_ in binds_of(p_) if '"tpacc"' in b_[2]]) == 1 and len([b_ for b_ in binds_of(p_) if '"tpdeny"' in b_[2]]) == 1 and not sel_ok5(p_),
            "OLD3 F6a the picked player: the Message box (button + Enter carry the typed text); Accept TP / Deny TP bound with the token")
    l1_ = len(lines5())
    p_ = s_ev({"a": "msg", "t": str(SS.tok), "@M": "hi"}, "OLD3 F6a Message without /msg")
    K.check(lines5()[l1_:] == [] and "/msg is not on this server" in cap5(p_) and str(sval(cmap(p_), "#SkyyStabMq.Value")) == "hi",
            "OLD3 F6a Message without SkyyEssentials = the 'not on this server' caption, no command, the typed text kept (%s)" % cap5(p_))
    E.CM.cmds.put("msg", CMDOK)
    old_ = str(SS.tok)
    p_ = s_ev({"a": "msg", "t": old_, "@M": 'hi "there" \\ ok'}, "OLD3 F6a Message")
    K.check(lines5()[l1_:] == ["msg Bravo hi there  ok"] and not bool(SS.closed) and "/msg Bravo" in cap5(p_) and sval(cmap(p_), "#SkyyStabMq.Value") is None,
            "OLD3 F6a Message = /msg Bravo <text> (quotes / backslashes dropped), the page stays, the box empty again (%s)" % lines5()[l1_:])
    p_ = s_ev({"a": "msg", "t": old_, "@M": "again"}, "OLD3 SAFE double Message")
    K.check(lines5()[l1_:] == ["msg Bravo hi there  ok"] and "The page changed" in cap5(p_), "OLD3 SAFE a double click on Message = ONE /msg")
    p_ = s_ev({"a": "msg", "t": str(SS.tok), "@M": "   "}, "OLD3 SAFE an empty message")
    K.check(lines5()[l1_:] == ["msg Bravo hi there  ok"] and cap5(p_) == str(SCD.MSGNONE), "OLD3 SAFE an empty message = a caption, no command")
    E.CM.cmds.put("tpdeny", CMDOK)
    p_ = s_ev({"a": "tpdeny", "t": str(SS.tok)}, "OLD3 F6a Deny TP")
    K.check(lines5()[-1] == "tpdeny" and not bool(SS.closed), "OLD3 F6a Deny TP = /tpdeny, the page stays (the old tile's cmd)")
    p_ = s_ev({"a": "tpacc", "t": str(SS.tok)}, "OLD3 F6a Accept TP without /tpaccept")
    K.check("/tpaccept is not on this server" in cap5(p_) and not bool(SS.closed), "OLD3 F6a Accept TP without the command = the caption, nothing runs")
    E.CM.cmds.put("tpaccept", CMDOK)
    old_ = str(SS.tok)
    s_ev({"a": "tpacc", "t": old_}, "OLD3 F6a Accept TP", n=None)
    K.check(bool(SS.closed) and lines5()[-1] == "tpaccept", "OLD3 F6a Accept TP = the page closed + /tpaccept (the old tile's cmdc: accepting a /tpahere teleports you)")
    s_ev({"a": "tpacc", "t": old_}, "OLD3 SAFE double Accept TP", n=0, page=SS)
    K.check(lines5().count("tpaccept") == 1, "OLD3 SAFE a double click on Accept TP = ONE /tpaccept")
    # F6b: All stats = the old Stats page's rows (StatsCalc.allRows), 20 a page
    SS, p_ = s_open("OLD3 reopen for stats")
    p_ = s_ev({"a": "stats"}, "OLD3 F6b All stats")
    SCL = JV("StatsCalc")
    rows_ = list(SCL.allRows(PK.pr.getUuid(), SCL.vitals(PK.st, PK.ref)))

    def rname(r_):
        r_ = list(r_)
        if r_[0] is None and r_[1] is None:
            return str(r_[9]) if len(r_) >= 11 else str(SCL.COL_STAT)
        return str(r_[1]) if r_[0] is None else str(r_[0])
    K.check(int(SS.view) == 1 and has5(p_, "SkyyStabSv") and not has5(p_, "SkyyStabBody") and not sel_ok5(p_)
            and str(sval(cmap(p_), "#SkyyStabSvPg.Text")) == "Page 1 / %d" % ((len(rows_) + 19) // 20) and cap5(p_) == str(SCD.VCAP),
            "OLD3 F6b All stats = the stats view (no cards sent), page 1 of %d, the view caption %s" % ((len(rows_) + 19) // 20, sel_ok5(p_)[:3]))
    got_ = []
    for pg_ in range((len(rows_) + 19) // 20):
        if pg_ > 0:
            p_ = s_ev({"a": "svpg:1"}, "OLD3 F6b stats page %d" % (pg_ + 1))
        cm = cmap(p_)
        got_ += [str(sval(cm, "#SkyyStabSvR%dN.Text" % k_)) for k_ in range(20) if ("#SkyyStabSvR%dN.Text" % k_) in cm]
    K.check(got_ == [rname(r_) for r_ in rows_] and len(got_) > 20, "OLD3 F6b every row of the old Stats page is drawn, in order, over the pages (%d rows)" % len(got_))
    tb_ = [k_ for k_, r_ in enumerate(rows_) if r_[0] is not None and len(list(r_)) >= 9]
    if tb_:
        k0_ = tb_[0]
        SS.svPage = k0_ // 20
        p_ = s_ev({"a": "svrf"}, "OLD3 F6b Refresh on a by-source row's page")
        cm = cmap(p_)
        rr_ = list(rows_[k0_])
        K.check([str(sval(cm, "#SkyyStabSvR%dC%d.Text" % (k0_ % 20, ck_))) for ck_ in range(6)] == [str(x_) for x_ in rr_[3:9]]
                and str(sval(cm, "#SkyyStabSvR%dV.Text" % (k0_ % 20))) == str(rr_[1]) and any(str(SCL.cellCol(rr_[3], 0)) in str(c_.text or "") for c_ in cmds_of(p_)),
                "OLD3 F6b a by-source row: its 6 cells + total, the cell colours = StatsCalc.cellCol (Style Guide 15)")
    p_ = s_ev({"a": "svpg:1"}, "OLD3 F6b past the last page") if int(SS.svPage) == int(SS.svPages) - 1 else None
    p_ = s_ev({"a": "tab:5"}, "OLD3 F6b the Social tab")
    K.check(int(SS.view) == 0 and has5(p_, "SkyyStabBody") and not has5(p_, "SkyyStabSv") and not bool(SS.closed), "OLD3 the Social tab in a view = the cards again (no back button)")
    # F6c: Manage (profiles) - an older SkyyProfiles, then the profile:fn:act stand-in
    BR.remove("profile:fn:act")
    p_ = s_ev({"a": "prof"}, "OLD3 F6c Manage without profile:fn:act")
    K.check(int(SS.view) == 2 and txt5(cmap(p_), "PvH") == str(SCD.PVOLD) and not vis5(cmap(p_), "PvR0") and not sel_ok5(p_),
            "OLD3 F6c FALL SkyyProfiles 0.1.18 (no profile:fn:act) = the view says which version it needs, no rows")
    PF = {"acts": []}

    def f_pact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        PF["acts"].append(a_)
        op_ = a_[0]
        if op_ == "list":
            return ("h|3|6|0|1|one per class|1|0|6 hours\np|1|Main|Archer|active|Created 2026-11-01 - playing now|0\n"
                    "p|2|Iron|Warrior|live|Created 2026-11-02 - last played 1 h ago|1\np|3|Old|Mage|del|Deleted - restore it within 5 h. Then it is gone.|0")
        if op_ == "roster":
            return "c|Archer|Archery|Ranged|1|Bows|Shoots|#ffffff\nc|Spellblade|Battlemagic|Hybrid|0|Swords|Later|#ffffff"
        if op_ == "newname":
            return "Peach"
        if op_ == "delask":
            return "=Delete profile Iron? Its island, coins, skills, bags and items will be gone." if a_[2] == "2" else "-You are playing Main right now."
        if op_ == "delete":
            return "+Iron is deleted. Restore it within 6 hours - after that it is gone."
        if op_ == "restore":
            return "+Old is back - exactly as it was."
        if op_ == "rename":
            return "+Profile 2 is now called Copper." if a_[3] == "Copper" else "-A profile name needs 2 to 16 characters."
        if op_ == "cancreate":
            return "+ok" if a_[2] == "Archer" else "-Select a class first."
        if op_ == "create":
            return "+switched"
        return "-Unknown profile action."
    BR.put("profile:fn:act", Fn(f_pact))
    p_ = s_ev({"a": "svrf"}, "OLD3 F6c Manage")
    cm = cmap(p_)
    K.check(txt5(cm, "PvR0N") == "Main  -  Archer" and vis5(cm, "PvR0A") and not vis5(cm, "PvR0W") and not vis5(cm, "PvR0Q") and vis5(cm, "PvR0E")
            and vis5(cm, "PvR1W") and vis5(cm, "PvR1Q") and vis5(cm, "PvR1E") and not vis5(cm, "PvR1R")
            and vis5(cm, "PvR2D") and vis5(cm, "PvR2R") and not vis5(cm, "PvR2W") and not vis5(cm, "PvR2E") and not vis5(cm, "PvR3")
            and "3 of 6 profile slots used" in txt5(cm, "PvH") and "does not use a slot" in txt5(cm, "PvH") and not sel_ok5(p_),
            "OLD3 F6c the list = the old page's rows: ACTIVE (Rename), a live one (Switch / Rename / Delete), a deleted one (Restore); the slots line %s" % sel_ok5(p_)[:3])
    K.check(txt5(cm, "PvK0N").startswith("Archer") and vis5(cm, "PvK0P") and vis5(cm, "PvK1Z") and not vis5(cm, "PvK1P") and not vis5(cm, "PvK2")
            and txt5(cm, "PvMn") == "Peach" and vis5(cm, "PvG"), "OLD3 F6c NEW PROFILE: the class cards (Pick / Coming later), the suggested name, Create profile")
    n0_ = len(PF["acts"])
    p_ = s_ev({"a": "pv:del:1", "t": str(SS.tok)}, "OLD3 F6c Delete Iron")
    K.check(vis5(cmap(p_), "Pvq") and txt5(cmap(p_), "Pvqt").startswith("Delete profile Iron?") and [a_[0] for a_ in PF["acts"][n0_:]].count("delete") == 0,
            "OLD3 F6c Delete = SkyyProfiles' question in the confirm row, nothing deleted yet")
    p_ = s_ev({"a": "pvno"}, "OLD3 F6c Cancel")
    K.check(not vis5(cmap(p_), "Pvq") and [a_[0] for a_ in PF["acts"][n0_:]].count("delete") == 0, "OLD3 F6c Cancel = nothing deleted")
    p_ = s_ev({"a": "pv:del:1", "t": str(SS.tok)}, "OLD3 F6c Delete again")
    old_ = str(SS.tok)
    p_ = s_ev({"a": "pvyes", "t": old_}, "OLD3 F6c Confirm")
    K.check([a_ for a_ in PF["acts"][n0_:] if a_[0] == "delete"] == [["delete", uk5, "2", None]] and "Iron is deleted" in cap5(p_),
            "OLD3 F6c Confirm = profile:fn:act delete 2 (ProfDel.delete), its answer in the caption (%s)" % cap5(p_))
    p_ = s_ev({"a": "pvyes", "t": old_}, "OLD3 SAFE double Confirm")
    K.check([a_[0] for a_ in PF["acts"][n0_:]].count("delete") == 1 and "The page changed" in cap5(p_), "OLD3 SAFE a double click on Confirm = ONE delete")
    p_ = s_ev({"a": "pv:del:0", "t": str(SS.tok)}, "OLD3 SAFE a forged Delete on the active profile")
    K.check([a_[0] for a_ in PF["acts"][n0_:]].count("delete") == 1 and "You are playing Main" in cap5(p_) and not vis5(cmap(p_), "Pvq"),
            "OLD3 SAFE a forged Delete on the active profile = SkyyProfiles' refusal, no question, no delete")
    p_ = s_ev({"a": "pv:res:2", "t": str(SS.tok)}, "OLD3 F6c Restore")
    K.check([a_[:3] for a_ in PF["acts"] if a_[0] == "restore"] == [["restore", uk5, "3"]] and "Old is back" in cap5(p_), "OLD3 F6c Restore = profile:fn:act restore 3 (ProfDel.restore)")
    p_ = s_ev({"a": "pv:ren:1", "t": str(SS.tok)}, "OLD3 F6c Rename Iron")
    cm = cmap(p_)
    K.check(vis5(cm, "Pvn") and str(sval(cm, "#SkyyStabPvnf.Value")) == "Iron" and len([b_ for b_ in binds_of(p_) if '"pvrenok"' in b_[2] and "SkyyStabPvnf.Value" in b_[2]]) == 2,
            "OLD3 F6c Rename = the name row (the old name in the box; Save / Enter carry it)")
    p_ = s_ev({"a": "pvrenok", "t": str(SS.tok), "@N": "x"}, "OLD3 F6c a refused name")
    K.check("needs 2 to 16" in cap5(p_) and vis5(cmap(p_), "Pvn") and str(sval(cmap(p_), "#SkyyStabPvnf.Value")) == "x", "OLD3 F6c a refused name = SkyyProfiles' line, the row stays with the typed name")
    p_ = s_ev({"a": "pvrenok", "t": str(SS.tok), "@N": "Copper"}, "OLD3 F6c Save")
    K.check(["rename", uk5, "2", "Copper"] in PF["acts"] and "Copper" in cap5(p_) and not vis5(cmap(p_), "Pvn"), "OLD3 F6c Save = profile:fn:act rename 2 Copper (renameProfile), the row closes")
    p_ = s_ev({"a": "pc:1", "t": str(SS.tok)}, "OLD3 F6c Pick a later class")
    K.check("coming later" in cap5(p_) and SS.pcls is None, "OLD3 F6c a class that is not released = 'coming later', not picked")
    p_ = s_ev({"a": "pcgo", "t": str(SS.tok)}, "OLD3 F6c Create with no class")
    K.check("Pick a class first" in cap5(p_) and not [a_ for a_ in PF["acts"] if a_[0] in ("cancreate", "create")], "OLD3 F6c Create with no class = a caption, nothing asked")
    p_ = s_ev({"a": "pc:0", "t": str(SS.tok)}, "OLD3 F6c Pick Archer")
    K.check(str(SS.pcls) == "Archer" and vis5(cmap(p_), "PvK0L") and not vis5(cmap(p_), "PvK0P"), "OLD3 F6c Pick = Selected")
    p_ = s_ev({"a": "pcname", "t": str(SS.tok)}, "OLD3 F6c Other name")
    K.check(["newname", uk5, "Peach", None] in PF["acts"], "OLD3 F6c Other name = profile:fn:act newname (ProfNames.pick, the shown name avoided)")
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p9"))
    nk_ = len(PF["acts"])
    p_ = s_ev({"a": "pcgo", "t": str(SS.tok)}, "OLD3 SAFE a profile switch before Create")
    K.check("Your profile changed" in cap5(p_) and len([a_ for a_ in PF["acts"][nk_:] if a_[0] != "list" and a_[0] != "roster"]) == 0,
            "OLD3 SAFE a profile switch between drawing and Create = nothing asked, nothing made")
    BR.remove("profile:fn:key")
    p_ = s_ev({"a": "svrf"}, "OLD3 F6c redraw")
    old_ = str(SS.tok)
    s_ev({"a": "pcgo", "t": old_}, "OLD3 F6c Create profile", n=None)
    K.check(bool(SS.closed) and [a_[0] for a_ in PF["acts"][-2:]] == ["cancreate", "create"] and PF["acts"][-1][2:] == ["Archer", "Peach"],
            "OLD3 F6c Create = cancreate (the old page's checks) then the screen closes + create Archer Peach (createAndSwitch)")
    s_ev({"a": "pcgo", "t": old_}, "OLD3 SAFE double Create", n=0, page=SS)
    K.check([a_[0] for a_ in PF["acts"]].count("create") == 1, "OLD3 SAFE a double click on Create = ONE profile")
    SS, p_ = s_open("OLD3 reopen for the switch")
    p_ = s_ev({"a": "prof"}, "OLD3 F6c Manage again")
    p_ = s_ev({"a": "pv:sw:1", "t": str(SS.tok)}, "OLD3 F6c Switch Iron")
    K.check(vis5(cmap(p_), "Pvq") and "Switch to Iron?" in txt5(cmap(p_), "Pvqt"), "OLD3 F6c Switch = the confirm row")
    old_ = str(SS.tok)
    s_ev({"a": "pvyes", "t": old_}, "OLD3 F6c Confirm the switch", n=None)
    K.check(bool(SS.closed) and lines5()[-1] == "profiles switch 2", "OLD3 F6c Confirm = the page closed + /profiles switch 2 (as the Profiles card)")
    BR.remove("profile:fn:act")
    # F6d: Manage party - an older SkyyParty, then the party:fn:act stand-in
    SS, p_ = s_open("OLD3 reopen for the party")
    BR.remove("party:fn:act")
    p_ = s_ev({"a": "party"}, "OLD3 F6d Manage party without party:fn:act")
    K.check(int(SS.view) == 3 and txt5(cmap(p_), "AvH") == str(SCD.AVOLD) and not vis5(cmap(p_), "AvR0") and not sel_ok5(p_),
            "OLD3 F6d FALL SkyyParty 0.1.10 (no party:fn:act) = the view says which version it needs")
    PA = {"acts": [], "in": "1", "lead": "1", "inv": "", "tpa": ""}

    def f_aact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        if a_[0] == "state":
            return "s|%s|%s|2|5|60|%s|%s|1|%s|%s|0" % (PA["in"], PA["lead"], PA["inv"], "42" if PA["inv"] else "0", PA["tpa"], "Bravo" if PA["tpa"] else "")
        PA["acts"].append(a_)
        if a_[0] == "invite":
            return "Invited %s to your party. They have 60 s to type /party accept." % a_[2] if a_[2] == "Bravo" else "Nobody called %s is online right now." % a_[2]
        if a_[0] == "disband" and PA["lead"] != "1":
            return "Only the party leader can disband the party. Use /party leave to leave it."
        return "OK %s" % a_[0]
    BR.put("party:fn:act", Fn(f_aact))
    p_ = s_ev({"a": "svrf"}, "OLD3 F6d Manage party")
    cm = cmap(p_)
    K.check(txt5(cm, "AvH").startswith("Party 2 / 5 players.") and txt5(cm, "AvR0N") == "SkyyCraftA  (you)" and txt5(cm, "AvR0T") == "Leader"
            and not vis5(cm, "AvR0P") and not vis5(cm, "AvR0K") and vis5(cm, "AvR1P") and vis5(cm, "AvR1K") and vis5(cm, "AvR1G") and not vis5(cm, "AvR2")
            and "Health 150 / 200" in txt5(cm, "AvR0S") and "Stamina 10 / 10" in txt5(cm, "AvR0S") and ("Width: %d," % (150 * int(SCD.AVBARW) // 200)) in cm.get("#SkyyStabAvR0B", "")
            and vis5(cm, "AvLv") and vis5(cm, "AvDb") and not vis5(cm, "AvP") and not vis5(cm, "AvT") and not sel_ok5(p_),
            "OLD3 F6d the party view = the page's members (you, Leader, Health / Stamina / Mana + bar), Promote / Kick / TPA on the other member, Leave / Disband %s" % sel_ok5(p_)[:3])
    p_ = s_ev({"a": "av:pro:1", "t": str(SS.tok)}, "OLD3 F6d Promote")
    K.check(PA["acts"][-1] == ["promote", uk5, ub5] and cap5(p_) == "OK promote", "OLD3 F6d Promote = party:fn:act promote <Bravo> (PartyStore.promote), its line in the caption")
    old_ = str(SS.tok)
    p_ = s_ev({"a": "av:kick:1", "t": old_}, "OLD3 F6d Kick")
    p_ = s_ev({"a": "av:kick:1", "t": old_}, "OLD3 SAFE double Kick")
    K.check([a_[0] for a_ in PA["acts"]].count("kick") == 1 and "The page changed" in cap5(p_), "OLD3 SAFE a double click on Kick = ONE kick")
    p_ = s_ev({"a": "av:tpa:1", "t": str(SS.tok)}, "OLD3 F6d TPA")
    K.check(PA["acts"][-1] == ["tpa", uk5, ub5], "OLD3 F6d TPA = party:fn:act tpa <Bravo> (PartyPage.tpaCall)")
    # fix (LOCKED 2026-10-10 party menu: "buttons for adding friend, message, trade"): Message + Trade per other online member
    cm = cmap(p_)
    K.check(vis5(cm, "AvR1M") and vis5(cm, "AvR1R") and not vis5(cm, "AvR0M") and not vis5(cm, "AvR0R")
            and len([b_ for b_ in binds_of(p_) if '"av:msg:1"' in b_[2]]) == 1 and len([b_ for b_ in binds_of(p_) if '"av:trd:1"' in b_[2]]) == 1
            and not [b_ for b_ in binds_of(p_) if '"av:msg:0"' in b_[2] or '"av:trd:0"' in b_[2]] and not sel_ok5(p_),
            "FIX party view: Message + Trade on the other member (bound with the token), not on yourself")
    E.CM.cmds.put("trade", CMDOK)
    l2_ = len(lines5())
    old_ = str(SS.tok)
    p_ = s_ev({"a": "av:trd:1", "t": old_}, "FIX party Trade")
    K.check(lines5()[l2_:] == ["trade Bravo"] and not bool(SS.closed) and "/trade Bravo" in cap5(p_), "FIX party Trade = /trade Bravo (the Social tab's Trade line), the page stays")
    p_ = s_ev({"a": "av:trd:1", "t": old_}, "FIX party double Trade")
    K.check(lines5()[l2_:] == ["trade Bravo"] and "The page changed" in cap5(p_), "FIX party a double click on Trade = ONE request")
    p_ = s_ev({"a": "av:trd:0", "t": str(SS.tok)}, "FIX party Trade yourself (forged)")
    K.check(lines5()[l2_:] == ["trade Bravo"] and "not online" in cap5(p_), "FIX party a forged Trade on your own row = a caption, no command")
    p_ = s_ev({"a": "av:msg:1", "t": str(SS.tok)}, "FIX party Message")
    cm = cmap(p_)
    K.check(int(SS.view) == 0 and str(SS.selU) == str(ub5) and vis5(cm, "Mr") and "Type your message to Bravo" in cap5(p_)
            and len([b_ for b_ in binds_of(p_) if '"msg"' in b_[2] and "SkyyStabMq.Value" in b_[2]]) == 2 and not sel_ok5(p_),
            "FIX party Message = the cards with Bravo picked and the Message box ready (msgSend = /msg)")
    E.CM.cmds.put("msg", CMDOK)
    p_ = s_ev({"a": "msg", "t": str(SS.tok), "@M": "party hi"}, "FIX party Message sent")
    K.check(lines5()[-1] == "msg Bravo party hi", "FIX party Message then the box = /msg Bravo <text> (%s)" % lines5()[-1:])
    p_ = s_ev({"a": "party"}, "FIX back to Manage party")
    K.check(int(SS.view) == 3, "FIX back on the party view")
    p_ = s_ev({"a": "av:kick:7", "t": str(SS.tok)}, "OLD3 SAFE a hidden row")
    K.check("Nobody there" in cap5(p_) and [a_[0] for a_ in PA["acts"]].count("kick") == 1, "OLD3 SAFE a forged click on a hidden member row = a caption")
    p_ = s_ev({"a": "av:dis", "t": str(SS.tok)}, "OLD3 F6d Disband (first press)")
    K.check("disband" not in [a_[0] for a_ in PA["acts"]] and cap5(p_) == str(SCD.DISQ) and txt5(cmap(p_), "AvDb") == "Click again to disband",
            "OLD3 F6d Disband's first press only arms it (the page's two clicks)")
    p_ = s_ev({"a": "av:pro:1", "t": str(SS.tok)}, "OLD3 F6d another click")
    p_ = s_ev({"a": "av:dis", "t": str(SS.tok)}, "OLD3 F6d Disband after another click")
    K.check("disband" not in [a_[0] for a_ in PA["acts"]] and txt5(cmap(p_), "AvDb") == "Click again to disband", "OLD3 F6d any other click clears the armed Disband (the next press arms again)")
    SS.disArm = 1
    p_ = s_ev({"a": "av:dis", "t": str(SS.tok)}, "OLD3 F6d Disband after 10 s")
    K.check("disband" not in [a_[0] for a_ in PA["acts"]], "OLD3 F6d after 10 s the second press only re-arms")
    p_ = s_ev({"a": "av:dis", "t": str(SS.tok)}, "OLD3 F6d Disband (second press)")
    K.check([a_[0] for a_ in PA["acts"]].count("disband") == 1 and cap5(p_) == "OK disband", "OLD3 F6d the second press within 10 s = party:fn:act disband")
    p_ = s_ev({"a": "av:leave", "t": str(SS.tok)}, "OLD3 F6d Leave")
    K.check(PA["acts"][-1][:2] == ["leave", uk5], "OLD3 F6d Leave party = party:fn:act leave")
    p_ = s_ev({"a": "av:inv", "t": str(SS.tok), "@P": "Bra vo!"}, "OLD3 F6d Invite")
    K.check(PA["acts"][-1] == ["invite", uk5, "Bravo"] and cap5(p_).startswith("Invited Bravo") and sval(cmap(p_), "#SkyyStabAvF.Value") is None,
            "OLD3 F6d Invite = party:fn:act invite <the cleaned typed name>, the box empty after it worked")
    p_ = s_ev({"a": "av:inv", "t": str(SS.tok), "@P": "Nobody"}, "OLD3 F6d Invite an unknown name")
    K.check(cap5(p_).startswith("Nobody called Nobody") and str(sval(cmap(p_), "#SkyyStabAvF.Value")) == "Nobody", "OLD3 F6d an unknown name = SkyyParty's line, the typed name kept")
    PA["in"], PA["lead"], PA["inv"], PA["tpa"] = "0", "0", "Bravo", ub5
    p_ = s_ev({"a": "svrf"}, "OLD3 F6d a pending invite + a TPA request")
    cm = cmap(p_)
    K.check(vis5(cm, "AvP") and txt5(cm, "AvPt") == "Bravo invited you to their party  (42 s left)" and vis5(cm, "AvT") and "Bravo wants to teleport to you" == txt5(cm, "AvTt")
            and not vis5(cm, "AvA") and not sel_ok5(p_), "OLD3 F6d not in a party: the pending invite (Accept / Decline + its seconds) and Accept TPA show")
    p_ = s_ev({"a": "av:acc", "t": str(SS.tok)}, "OLD3 F6d Accept")
    p_ = s_ev({"a": "av:dec", "t": str(SS.tok)}, "OLD3 F6d Decline")
    p_ = s_ev({"a": "av:tpacc", "t": str(SS.tok)}, "OLD3 F6d Accept TPA")
    K.check([a_[:3] for a_ in PA["acts"][-3:]] == [["accept", uk5, None], ["decline", uk5, None], ["tpaccept", uk5, ub5]],
            "OLD3 F6d Accept / Decline / Accept TPA = party:fn:act accept / decline / tpaccept <Bravo>")
    PA["in"], PA["lead"], PA["inv"], PA["tpa"] = "1", "0", "", ""
    p_ = s_ev({"a": "svrf"}, "OLD3 F6d a member")
    K.check(not vis5(cmap(p_), "AvDb") and not vis5(cmap(p_), "AvR1K"), "OLD3 F6d a member sees no Disband / Kick")
    p_ = s_ev({"a": "av:dis", "t": str(SS.tok)}, "OLD3 SAFE a member's forged Disband")
    K.check(cap5(p_).startswith("Only the party leader"), "OLD3 SAFE a member's forged Disband = SkyyParty's refusal at once (the page's rule)")
    p_ = s_ev({"a": "tab:5"}, "OLD3 back to the cards")
    K.check(int(SS.view) == 0 and has5(p_, "SkyyStabBody"), "OLD3 the Social tab = the cards")
    K.notes.append("OLD3 ran: profile:fn:act calls %d, party:fn:act calls %d, last command lines %s" % (len(PF["acts"]), len(PA["acts"]), lines5()[-6:]))
    BR.remove("party:fn:act")
    for cn_ in ("msg", "tpaccept", "tpdeny", "trade"):
        E.CM.cmds.remove(cn_)
        if CMD5.get(cn_) is not None:
            E.CM.cmds.put(cn_, CMD5[cn_])
'''
T.rep('''"""Harness for SkyyMenu 0.3.70 (old menu follow-ups F1 + F2 + F3; tools/menu_0_3_70_patch.py, round oldmenu2).''',
      '''"""Harness for SkyyMenu 0.3.71 (old menu follow-up F6 - the Social tab; tools/menu_0_3_71_patch.py, round oldmenu3).
GENERATED by tools/menu_0_3_71_patch.py from the 0.3.70 harness (edit the patch, not this file): every 0.3.70 check runs again on the
0.3.71 jar (TAB5: the Full / Stats / Profiles / Party links now stay on the screen; OLD2's ratchet = OLD3's), plus
  OLD3 STATIC   the ratchet: OLD_LEFT lost social:players, character:stats, character:profiles, social:party (Guild kept); no Full page, no
                back button; the views call profile:fn:act / party:fn:act / StatsCalc.allRows / /tpaccept /tpdeny /msg; the build asserts
       F6a      Message (/msg <name> <text>, cleaned; missing command, double click, empty text), Deny TP (/tpdeny), Accept TP (page closes
                + /tpaccept, once)
       F6b      All stats = every StatsCalc.allRows row over the pages (names, a by-source row's cells + total + cellCol colours); Refresh;
                the Social tab = the cards
       F6c      (profile:fn:act stand-in) Manage: the old list's rows + buttons, the class cards, Delete (question, Cancel, Confirm once,
                a forged Delete on the active one refused), Restore, Rename (refused name kept, Save), Pick (later class refused), Other
                name, Create (no class; profile switch = nothing; cancreate + close + create, once), Switch (confirm, /profiles switch)
       F6d      (party:fn:act stand-in) Manage party: members + buttons, Promote, Kick once, TPA, a hidden row, Disband (arm, cleared by
                another click, re-arm after 10 s, second press), Leave, Invite (cleaned name; unknown kept), the pending invite + Accept /
                Decline + Accept TPA, a member's view + forged Disband
       every Social packet: every b.set / append / binding names an element drawn in that packet (the frame + ONE section)
The 0.3.70 harness text follows:
Harness for SkyyMenu 0.3.70 (old menu follow-ups F1 + F2 + F3; tools/menu_0_3_70_patch.py, round oldmenu2).''')
T.rep('VERSION = "0.3.70"\nJAR', 'VERSION = "0.3.71"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.69.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.70.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.69.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.70.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_70_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_71_patch.py")')
T.rep('"scratch", "oldmenu2", "menu"', '"scratch", "oldmenu3", "menu"')
T.rep('ADDED = []   # 0.3.70: no new class\n', 'ADDED = []   # 0.3.71: no new class\n')
EXPECT_BODY = '''    "SocialTab": ["+f avIds", "+f avLead", "+f avTpa", "+f disArm", "+f invKeep", "+f msgKeep", "+f pAsk", "+f pAskId", "+f pAskText", "+f pRen",
                  "+f pRenText", "+f pcNames", "+f pcOn", "+f pcls", "+f pname", "+f pvFirst", "+f pvIds", "+f pvNames", "+f pvSt", "+f svPage", "+f svPages",
                  "+f view", "+m aact", "+m avDisband", "+m avHide", "+m avInvite", "+m avMsg", "+m avOn", "+m avRow", "+m avTrade", "+m avSay", "+m cleanMsg", "+m fillAv", "+m fillPv",
                  "+m fillStats", "+m goView", "+m hexOf", "+m msgOf", "+m msgSend", "+m pact", "+m pcGo", "+m pcName", "+m pcPick", "+m pvDel", "+m pvHide",
                  "+m pvRen", "+m pvRenOk", "+m pvRes", "+m pvRow", "+m pvSay", "+m pvSw", "+m pvYes", "+m slab", "+m split", "~c ", "~m build",
                  "~m fillParty", "~m fillPicked", "~m fillPlayers", "~m fillProfiles", "~m handleDataEvent", "~m runLine", "~m tabGo"],
                  # F6 (fillPlayers: the page size PN 10 -> 8 is an inlined constant)
    "SocialTabData": ["+f AVBARW", "+f AVFILL", "+f AVN", "+f AVOFF", "+f AVOLD", "+f CHAT", "+f C_ABS", "+f C_ACC", "+f C_DIM", "+f C_GOLD", "+f DISQ",
                      "+f LS", "+f MSGMAX", "+f MSGNONE", "+f PCN", "+f PVN", "+f PVOFF", "+f PVOLD", "+f SCELL", "+f SHEAD", "+f SNAME", "+f SNOTE",
                      "+f SROW", "+f SSRC", "+f STOT", "+f SVAL", "+f SVN", "+f VCAP", "~<clinit>"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.70:', 'if "--expect-dump" in sys.argv:'), EXPECT_71.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.70"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.71"') == 1, "S VERSION")
''' + HARNESS_OLD3_STATIC.rstrip("\n"))
# OLD2's ratchet compared 0.3.70 with 0.3.69: against 0.3.70 it is OLD3's (above)
T.rep('''    K.check(lefto_ - left2_ == set([("settings", "mods"), ("character", "pets")]) and left2_ - lefto_ == set([("market", "auctions")])
            and ("market", "auctions") in ops_o_ and len(left2_) == len(lefto_) - 1,
            "OLD2 RATCHET OLD_LEFT lost settings:mods + character:pets; the one row added = market:auctions, an opener link 0.3.69 already had, now tracked (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(("market", "auctions") in left2_ and ("market", "auctions") in ops_o_ and ("settings", "mods") not in left2_ and ("character", "pets") not in left2_,
            "OLD2 RATCHET (0.3.71: vs 0.3.70) settings:mods + character:pets stay gone, market:auctions still tracked")''')
# TAB5: the Full / Stats / Profiles / Party links are this screen now (one packet, the screen stays); the Guild page link stays
T.rep('''    for a_, what in (("full", "Full page"), ("stats", "Stats page"), ("prof", "Profiles page"), ("party", "Party page"), ("guild", "Guild page")):
        SS, p_ = s_open("TAB5 reopen for " + what)
        f0_ = len(E.sent(PK))
        SS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": a_}))
        cur_ = PK.pm.getCustomPage()
        K.check(len(pages(PK, f0_)) == 1, "TAB5 LINK %s = the old page's route, ONE packet (%s)" % (what, None if cur_ is None else cur_.getClass().getSimpleName()))''',
      '''    for a_, what, want_ in (("full", "a forged Full page (0.3.71: gone)", "SocialTab"), ("stats", "All stats (0.3.71: the stats view)", "SocialTab"),
                            ("prof", "Manage (0.3.71: the profiles view)", "SocialTab"), ("party", "Manage party (0.3.71: the party view)", "SocialTab"),
                            ("guild", "Guild page", None)):
        SS, p_ = s_open("TAB5 reopen for " + what)
        f0_ = len(E.sent(PK))
        SS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": a_}))
        cur_ = PK.pm.getCustomPage()
        K.check(len(pages(PK, f0_)) == 1 and (want_ is None or (cur_ is not None and str(cur_.getClass().getSimpleName()) == want_)),
                "TAB5 LINK %s, ONE packet (%s)" % (what, None if cur_ is None else cur_.getClass().getSimpleName()))''')
T.rep('''    BR.put("party:fn:members", f_mem5)
    # TABS''', '''    BR.put("party:fn:members", f_mem5)
''' + HARNESS_OLD3.rstrip("\n") + '''
    # TABS''')
if T.dst:
    T.finish()