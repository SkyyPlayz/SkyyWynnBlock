"""Derive SkyyMenu/build_skyymenu_0.3.73.py + SkyyMenu/test_skyymenu_0.3.73.py from the SET pin SkyyMenu 0.3.72 (generated - never re-run
its patch). Run:  python tools/menu_0_3_73_patch.py   then   python SkyyMenu/build_skyymenu_0.3.73.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.73.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyGuilds 0.1.14 (tools/guilds_0_1_14_patch.py: guild:fn:act) for the Guild view and SkyyAuctions
0.1.18 (tools/auctions_0_1_18_patch.py: ah:fn:tab / ah:fn:tabact) for the Auction House view; with the older jars those two views say which
version they need (the rest of the Social / Market tabs works as 0.3.72).

0.3.73 (2026-11-24, round oldmenu5) = OLD MENU FOLLOW-UP: THE SOCIAL TAB'S GUILD VIEW + THE MARKET TAB'S AUCTION HOUSE VIEW. Skyy's words
(docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu
compleatly, so instead of adding things like the full tree button, just build it all into the new system and remove the old "Full tree"";
2026-11-24 "keep building". Each part calls the SAME server code as the old page (through the bridges; no duplicated rule, no new number):
  GUILD (social:guild gone): the Guild card's 'Guild page' button = 'Manage guild' = the GUILD VIEW of the Social screen (Menu-Pattern: no back
      button, the Social tab on top = the cards). guild:fn:act state (500 members / 300 log lines) draws it:
      NOT IN A GUILD - the live invite (who, guild + tag, level, members, seconds left) with Accept / Decline, CREATE A GUILD (typed name +
        Create guild / Enter);
      IN A GUILD - the card: name + tag, level, season XP, your rank, the XP bar + numbers, the XP share; Leave guild (everyone) / Disband guild
        (Leader) - the page's two presses ('Click again to leave' / 'Click again to DISBAND' while armed); the sub-tabs Members | Bank | Log:
        MEMBERS - 9 a page (< >): name (you), rank, online, guild XP added, bank contribution, taken today; the page's buttons by rank:
          Promote / Demote (Leader, one press), Kick (a lower rank; 'Sure' while armed), Make leader (Leader; 'Confirm' while armed);
          Invite to party (every rank, on an online member who is not you = /party invite <name>, the Players page's line - LOCKED
          2026-10-10 docs/answered/ui.md "guild member list has Invite to party"; Add friend waits on OPEN-QUESTIONS: the game has no friends list);
          INVITE (Leader / Admin: typed name + Invite / Enter; else the page's 'Only the Leader and Admins can invite players.')
        BANK - the guild bank, your purse, the daily limits + your usage + the game day, Amount (typed) + Deposit / Withdraw (Withdraw only
          when your rank may), Enter in the box = the page's amount note (amounthint); the Leader's limit box + Set Admin limit / Set Member
          limit, Enter = the limit note (limithint)
        LOG - 15 a page (< >), newest first: when, who, what, the bank after.
      Every answer word for word in the caption ('+' done, '-' refused, '=' a question: the same press again within 10 s confirms - the bridge
      keeps the arm and the next drawing shows the armed button word).
  AUCTION HOUSE (market:auctions gone): the AH card's Browse all / New listing / Your listings and each auction row's Open = the AUCTION HOUSE
      VIEW of the Market screen (sub-tabs Market | Bazaar orders | Merchants | Auction House). Buy It Now only (no bids - Skyy 2026-09-24).
      Modes (run-time buttons): Browse | Create BIN | Manage, the status (purse, listings used / max, claims), the page's banner line, Not now
      (drops an armed confirm = op no), Refresh.
        BROWSE - Category / Sort / Rarity (< value >, the AH's own lists), Search + Level min / max (only while the level filter is on; the
          AH's bad-level warning), Reset (the AH's empty line names it), the AH's summary; 9 rows a page (< >) in the AH's order (default Tier then name): the rarity
          square behind the icon + the name in the rarity colour in the tooltip, T<tier>, qty, each, ends, seller (yours / your other
          profile), off the market, for sale in N s; the price; View; Show more (+100 rows, up to 1000).
        ITEM - the icon + square, name, tier + qty + ends, SkyyGear's name line, the AH's 9 fact lines, the description; BUY NOW (the b| price
          drawn; at the confirm amount the first press = the AH's '=Confirm the purchase ...', the button says CONFIRM BUY, the same press
          again buys), your own listing = Cancel listing (two presses: 'YES, CANCEL IT'), or the AH's why-not note / the grace seconds.
        CREATE BIN - your stacks (the AH's c| cells, sorted by tier then name, 10 a page, off-market ones without Pick), Pick, the picked
          stack (lowest BIN hint), Price (typed) + Check fee / Enter, Duration (< value >), the AH's 3 fee lines + the fee / tax / you get
          line; CREATE BIN (the AH previews: '=Check the fee above, then click Create BIN again.') then LIST IT (w| = the next press lists).
        MANAGE - the AH's summary + Claim all ('Yes, claim all' while armed), the other-profiles line, 9 rows a page: square + icon, name,
          the AH's state line, price, the AH's button word (Claim coins / Claim item / Cancel - 'Yes, cancel' while armed).
  NEVER A VALUE THE PLAYER DID NOT SEE: Buy sends the listing id + the price DRAWN in the packet pressed; Create sends the stack (section / slot
      / sig), the price and the duration of the read DRAWN - a price typed after that drawing is only checked (a redraw with its fees, nothing
      sent: 'Here is the fee for the price you typed ...'); Cancel / Claim send the drawn row's listing id; a guild row's button sends the
      drawn member's uuid and only where the drawing showed that button (a forged Promote on a Demote row = a caption, no call).
  SAFETY: every trading / guild click carries the page token (an older drawing = "The page changed", nothing runs) and the bridges' own
      profile key + token from the read (SkyyGuilds / SkyyAuctions answer "=Your profile changed ..." / "=Your guild changed ..." / "=The
      Auction House changed ..."); the bridges' 350 ms guard "=One moment." shows as the caption; a null answer (not on the world thread) =
      "That could not run here - nothing changed"; a click meant for another view / mode = a caption, no call.
  ONE PACKET = THE FRAME + ONE SECTION: Social G (guild), Market U (auction house) join the section letters (0 / H / S P A G and 0 / H / O M U).
New: no class / command / system / picture / lang key / setting / saved data. OLD_LEFT: social:guild + market:auctions out (13 -> 11).
ROLLBACK to 0.3.72: safe alone (nothing saved; the Guild page / Auction House links come back). SkyyGuilds 0.1.14 / SkyyAuctions 0.1.18 each roll
back alone (Menu then names the version each view needs).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.72.py"), os.path.join(MOD, "build_skyymenu_0.3.73.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.72.py"), os.path.join(MOD, "test_skyymenu_0.3.73.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.72"\n') and P.has("OLD_LEFT = sorted(set([") and P.has('MT + "OvL"') and not P.has('MT + "HvBr"'), "not the generated SkyyMenu 0.3.72 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.72: OLD MENU FOLLOW-UP - THE MARKET TAB''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.73: OLD MENU FOLLOW-UP - THE GUILD + AUCTION HOUSE VIEWS: Manage guild = the Social screen's Guild view (create / invite Accept / Decline;
       members + Promote / Demote / Kick / Make leader by rank, two presses where the page asks; invite; the bank with typed amounts, limits
       and the Leader's limit box; the log; Leave / Disband - SkyyGuilds 0.1.14 guild:fn:act); Browse all / New listing / Your listings /
       an auction's Open = the Market screen's Auction House view (Browse with filters + search + level, the item with Buy now, Create BIN
       with the fee check then list, Manage with Claim / Cancel / Claim all - SkyyAuctions 0.1.18 ah:fn:tab / tabact; Buy It Now only);
       OLD_LEFT lost 2 rows (notes: tools/menu_0_3_73_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.73.py.
0.3.72: OLD MENU FOLLOW-UP - THE MARKET TAB''')
P.rep('VERSION = "0.3.72"\n', 'VERSION = "0.3.73"\n')

# ======================================================================= SOCIAL: the Guild card's button = the guild view
P.rep('''    ap.append(("#" + gu, G_.glass_button(SC + "Gpage", "Guild page", "secondary", w=160, h=34, size=14, anchor={"top": 10})))''',
      '''    ap.append(("#" + gu, G_.glass_button(SC + "Gpage", "Manage guild", "secondary", w=160, h=34, size=14, anchor={"top": 10})))   # 0.3.73: the guild view''')

GV_PY = r'''
# ---- 0.3.73 (oldmenu5): THE GUILD VIEW (section G) - the old guild page through SkyyGuilds 0.1.14 guild:fn:act (contract tools/guilds_0_1_14_patch.py)
GV_BH = IV_BODY_H - 20 - 34 - 6                             # under the view head (784)
GV_TH, GV_LDW = 100, 220                                    # the guild card, its Leave / Disband column
GV_TXW = SC_VI - 16 - 8 - GV_LDW                            # the card's text column (1292)
GV_BARW = 700                                               # the guild XP bar
GV_PH = GV_BH - GV_TH - 8 - 34 - 8                          # a sub-tab's panel (634)
GV_MN, GV_RH = 9, 48                                        # MEMBERS: 9 a page
GV_PBW, GV_KBW, GV_LBW = 120, 100, 140                      # Promote / Demote, Kick, Make leader
GV_QBW = 160                                                # Invite to party (fix: LOCKED 2026-10-10)
GV_RTW = SC_VI - 16 - 8 - (GV_QBW + 4) - (GV_PBW + 4) - (GV_KBW + 4) - (GV_LBW + 4)   # a member row's text column (976)
GV_LN, GV_LH = 15, 30                                       # LOG: 15 a page
GV_LWW, GV_LPW, GV_LBW2 = 180, 260, 220                     # when, who, the bank after
GV_LTW = SC_VI - 16 - GV_LWW - GV_LPW - GV_LBW2             # what (860)
GV_OW = 900                                                 # NOT IN A GUILD: the invite card
GV_SUB = ["Members", "Bank", "Log"]
GV_READ = "500|300"                                         # guild:fn:act state: members | log lines to send (0-1000)
GV_TXT = {
    "gvold": "Manage guild needs SkyyGuilds 0.1.14 - this server has an older one. /guild works.",
    "gvoff": "Guilds are not on this server right now.",
    "gvfail": "Your guild could not be read right now - try again in a moment.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in GV_TXT.values() for c_ in v_), "0.3.73: plain texts"
for _k in GV_TXT:
    assert SUI.text_width(GV_TXT[_k], 13) <= SC_VI - 240 - (SC_VBW + 6), ("0.3.73: a guild head line fits", _k)
assert GV_RTW >= 900 and GV_LTW >= 600 and GV_TXW >= 1000, (GV_RTW, GV_LTW, GV_TXW)
for _l, _w in (("Invite to party", GV_QBW), ("Promote", GV_PBW),("Demote", GV_PBW), ("Kick", GV_KBW), ("Sure", GV_KBW), ("Make leader", GV_LBW), ("Confirm", GV_LBW)):
    assert SUI.text_width(_l, 13, bold=True) <= _w - 12, ("0.3.73: a member button fits", _l)
for _l in ("Click again to leave", "Click again to DISBAND", "Leave guild", "Disband guild"):
    assert SUI.text_width(_l, 13, bold=True) <= GV_LDW - 12, ("0.3.73: Leave / Disband fits", _l)
for _l in GV_SUB:
    assert SUI.text_width(_l, 14, bold=True) <= SC_VBW - 16, ("0.3.73: a guild sub-tab fits", _l)
for _l in ("Set Admin limit", "Set Member limit"):
    assert SUI.text_width(_l, 13, bold=True) <= 200 - 12, ("0.3.73: a limit button fits", _l)
# the run-time markup: the sub-tab buttons (the market screen's tab styles) - the XP fill is SC_FILLX
GV_TAB = "TextButton #SkyyStab{I} { Anchor: (Width: %d, Height: 34, Right: 6); {S} }" % SC_VBW
_gv_mk = [GV_TAB.replace("{I}", "Gs0").replace("{S}", MT_ST_CATSEL), GV_TAB.replace("{I}", "Gs1").replace("{S}", MT_ST_CAT)]
for _mk in _gv_mk:
    SUI.check_markup(_mk, prefix=SC, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.73: a run-time markup line Java can hold"
_gv_tok = SUI.proven_tokens(_gv_mk)
assert not [k_ for k_, g_ in _gv_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], "0.3.73: the view markups are proven"
GV_RUNTIME_MAX = len(GV_SUB) + 1                            # the sub-tabs + the XP fill
'''
P.rep('''AV_RUNTIME_MAX = AV_N                                       # a health fill per member
''', '''AV_RUNTIME_MAX = AV_N                                       # a health fill per member
''' + GV_PY)

GV_VIEW_PY = r'''    out.append(("A", ap, []))
    # ======== G: THE GUILD VIEW (0.3.73, oldmenu5: the old guild page - SkyyGuilds 0.1.14 guild:fn:act)
    ap = SUI.Appends()
    gv = SC + "Gv"
    ap.append(("#" + win, G_.glass_group(gv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    vhead(ap, gv, "Gv", "GUILD", [(SC + "GvRf", "Refresh", "secondary")])
    gi = SC + "GvI"                                          # in a guild
    ap.append(("#" + gv, G_.glass_group(gi, SC_VI, GV_BH, layout="Top", anchor={"top": 6})))
    tp = SC + "GvTop"
    ap.append(("#" + gi, G_.glass_group(tp, SC_VI, GV_TH, role="inset", layout="Left", pad=8)))
    tx = SC + "GvTx"
    ap.append(("#" + tp, G_.glass_group(tx, GV_TXW, GV_TH - 16, layout="Top", anchor={"right": 8})))
    ap.append(("#" + tx, lab(SC + "GvN", "", 20, "title", bold=True, w=GV_TXW, h=28)))
    ap.append(("#" + tx, lab(SC + "GvL", "", 13, "accentHi", bold=True, w=GV_TXW, h=20)))
    ap.append(("#" + tx, 'Group #%sGvB { Anchor: (Width: %d, Height: 8, Top: 4); LayoutMode: Left; Background: %s; }' % (SC, GV_BARW, IV_TRACK)))
    ap.append(("#" + tx, lab(SC + "GvX", "", 12, "dim", w=GV_TXW, h=18, anchor={"top": 4})))
    ld = SC + "GvLd"
    ap.append(("#" + tp, G_.glass_group(ld, GV_LDW, GV_TH - 16, layout="Top")))
    ap.append(("#" + ld, G_.glass_button(SC + "GvLv", "Leave guild", "secondary", w=GV_LDW, h=34, size=13)))
    ap.append(("#" + ld, G_.glass_button(SC + "GvDb", "Disband guild", "secondary", w=GV_LDW, h=34, size=13, anchor={"top": 8})))
    assert 28 + 20 + 12 + 22 <= GV_TH - 16 and 34 + 8 + 34 <= GV_TH - 16, "0.3.73: the guild card fits"
    sr = SC + "GvS"
    ap.append(("#" + gi, G_.glass_group(sr, SC_VI, 34, layout="Left", anchor={"top": 8})))
    ap.append(("#" + sr, G_.glass_group(SC + "GvSt", len(GV_SUB) * (SC_VBW + 6), 34, layout="Left")))
    ap.append(("#" + sr, lab(SC + "GvSh", "", 13, "xp", bold=True, w=SC_VI - len(GV_SUB) * (SC_VBW + 6), h=34, halign="End")))
    # MEMBERS
    gm = SC + "GvM"
    ap.append(("#" + gi, G_.glass_group(gm, SC_VI, GV_PH, layout="Top", anchor={"top": 8})))
    for k_ in range(GV_MN):
        r = "%sGvR%d" % (SC, k_)
        ap.append(("#" + gm, G_.glass_group(r, SC_VI, GV_RH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"bottom": 4})))
        ap.append(("#" + r, G_.glass_group(r + "X", GV_RTW, GV_RH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + r + "X", G_.glass_group(r + "Y", GV_RTW, 22, layout="Left", anchor={"top": 4})))
        ap.append(("#" + r + "Y", lab(r + "N", "", 15, "row", bold=True, w=GV_RTW - 120, h=22)))
        ap.append(("#" + r + "Y", lab(r + "T", "", 12, "xp", bold=True, w=120, h=22, halign="End")))
        ap.append(("#" + r + "X", lab(r + "S", "", 12, "text", w=GV_RTW, h=18)))
        for b_, t_, w_ in (("Q", "Invite to party", GV_QBW), ("P", "Promote", GV_PBW),("K", "Kick", GV_KBW), ("L", "Make leader", GV_LBW)):
            ap.append(("#" + r, G_.glass_button(r + b_, t_, "secondary", w=w_, h=30, size=13, anchor={"left": 4, "top": 9})))
    assert 4 + 22 + 18 <= GV_RH and 9 + 30 <= GV_RH, "0.3.73: a member row fits"
    pg = SC + "GvMp"
    ap.append(("#" + gm, G_.glass_group(pg, SC_VI, 30, layout="Left", anchor={"top": 2})))
    ap.append(("#" + pg, G_.glass_button(SC + "GvMpp", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
    ap.append(("#" + pg, lab(SC + "GvMg", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
    ap.append(("#" + pg, G_.glass_button(SC + "GvMpn", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))
    iw = SC + "GvIw"
    ap.append(("#" + gm, G_.glass_group(iw, SC_VI, 58, layout="Top", anchor={"top": 10})))
    iv = SC + "GvIv"
    ap.append(("#" + iw, G_.glass_group(iv, SC_VI, 34, layout="Left")))
    ap.append(("#" + iv, lab(None, "INVITE A PLAYER", 13, "dim", bold=True, w=180, h=34)))
    ap.append(("#" + iv, G_.text_field(SC + "GvIfBox", SC + "GvIf", w=320, h=32, placeholder="Player name", max_length=32, size=13, anchor={"right": 6})))
    ap.append(("#" + iv, G_.glass_button(SC + "GvIgo", "Invite", "primary", w=120, h=34, size=13)))
    ap.append(("#" + iw, lab(SC + "GvIh", "", 12, "dim", w=SC_VI, h=20, anchor={"top": 4})))
    ap.append(("#" + gm, lab(SC + "GvMn", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 6})))
    assert GV_MN * (GV_RH + 4) + 32 + 68 + 24 <= GV_PH, "0.3.73: the members tab fits"
    # BANK
    gk = SC + "GvK"
    ap.append(("#" + gi, G_.glass_group(gk, SC_VI, GV_PH, layout="Top", anchor={"top": 8})))
    ap.append(("#" + gk, lab(SC + "GvKv", "", 26, "xp", bold=True, w=SC_VI, h=36)))
    ap.append(("#" + gk, lab(SC + "GvKp", "", 13, "text", w=SC_VI, h=20)))
    ap.append(("#" + gk, lab(SC + "GvKu", "", 13, "text", w=SC_VI, h=20, anchor={"top": 4})))
    ka = SC + "GvKa"
    ap.append(("#" + gk, G_.glass_group(ka, SC_VI, 34, layout="Left", anchor={"top": 14})))
    ap.append(("#" + ka, lab(None, "Amount", 13, "dim", bold=True, w=110, h=34)))
    ap.append(("#" + ka, G_.text_field(SC + "GvKfBox", SC + "GvKf", w=260, h=32, placeholder="Coins", max_length=16, size=13, anchor={"right": 6})))
    ap.append(("#" + ka, G_.glass_button(SC + "GvKd", "Deposit", "primary", w=150, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + ka, G_.glass_button(SC + "GvKw", "Withdraw", "secondary", w=150, h=34, size=13)))
    ap.append(("#" + gk, lab(SC + "GvKh", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 4})))
    kl = SC + "GvKl"
    ap.append(("#" + gk, G_.glass_group(kl, SC_VI, 80, layout="Top", anchor={"top": 18})))
    ap.append(("#" + kl, lab(None, "DAILY WITHDRAW LIMITS", 12, "dim", bold=True, w=SC_VI, h=18)))
    kr = SC + "GvKr"
    ap.append(("#" + kl, G_.glass_group(kr, SC_VI, 34, layout="Left", anchor={"top": 4})))
    ap.append(("#" + kr, G_.text_field(SC + "GvKlfBox", SC + "GvKlf", w=220, h=32, placeholder="Daily limit", max_length=16, size=13, anchor={"right": 6})))
    ap.append(("#" + kr, G_.glass_button(SC + "GvKla", "Set Admin limit", "secondary", w=200, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + kr, G_.glass_button(SC + "GvKlm", "Set Member limit", "secondary", w=200, h=34, size=13)))
    ap.append(("#" + kl, lab(SC + "GvKlh", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 4})))
    ap.sets.append((SC + "GvKlh", "Text", "0 = no withdrawing, none = no limit. Enter in the box only explains it."))
    ap.append(("#" + gk, lab(SC + "GvKn", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 6})))
    ap.sets.append((SC + "GvKn", "Text", "Only the Leader sets the daily withdraw limits."))
    ap.append(("#" + gk, lab(SC + "GvKs", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 6})))
    assert 36 + 20 + 24 + 48 + 22 + 98 + 24 + 24 <= GV_PH, "0.3.73: the bank tab fits"
    # LOG
    gg = SC + "GvG"
    ap.append(("#" + gi, G_.glass_group(gg, SC_VI, GV_PH, layout="Top", anchor={"top": 8})))
    lh = SC + "GvGh"
    ap.append(("#" + gg, G_.glass_group(lh, SC_VI, 20, layout="Left", pad={"horizontal": 8})))
    for t_, w_, h_ in (("WHEN", GV_LWW, None), ("PLAYER", GV_LPW, None), ("WHAT", GV_LTW, None), ("BANK AFTER", GV_LBW2, "End")):
        ap.append(("#" + lh, lab(None, t_, 12, "dim", bold=True, w=w_, h=20, halign=h_)))
    for k_ in range(GV_LN):
        r = "%sGvE%d" % (SC, k_)
        ap.append(("#" + gg, G_.glass_group(r, SC_VI, GV_LH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"top": 2})))
        ap.append(("#" + r, lab(r + "W", "", 12, "dim", w=GV_LWW, h=GV_LH)))
        ap.append(("#" + r, lab(r + "P", "", 13, "row", bold=True, w=GV_LPW, h=GV_LH)))
        ap.append(("#" + r, lab(r + "T", "", 13, "text", w=GV_LTW, h=GV_LH)))
        ap.append(("#" + r, lab(r + "B", "", 13, "xp", bold=True, w=GV_LBW2, h=GV_LH, halign="End")))
    lp = SC + "GvGp"
    ap.append(("#" + gg, G_.glass_group(lp, SC_VI, 30, layout="Left", anchor={"top": 6})))
    ap.append(("#" + lp, G_.glass_button(SC + "GvGpp", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
    ap.append(("#" + lp, lab(SC + "GvGg", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
    ap.append(("#" + lp, G_.glass_button(SC + "GvGpn", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))
    ap.append(("#" + gg, lab(SC + "GvGn", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 4})))
    assert 20 + GV_LN * (GV_LH + 2) + 36 + 22 <= GV_PH, "0.3.73: the log tab fits"
    assert GV_TH + 8 + 34 + 8 + GV_PH <= GV_BH and 20 + 34 + 6 + GV_BH <= IV_BODY_H, "0.3.73: the guild view fits"
    # NOT IN A GUILD
    go = SC + "GvO"
    ap.append(("#" + gv, G_.glass_group(go, SC_VI, GV_BH, layout="Top", anchor={"top": 6})))
    ap.append(("#" + go, lab(SC + "GvOt", "You are not in a guild", 17, "title", bold=True, w=SC_VI, h=26)))
    oi = SC + "GvOi"
    ap.append(("#" + go, G_.glass_group(oi, GV_OW, 104, role="inset", layout="Top", pad=10, anchor={"top": 12})))
    ap.append(("#" + oi, lab(SC + "GvOq", "", 14, "action", bold=True, w=GV_OW - 20, h=24)))
    ap.append(("#" + oi, lab(SC + "GvOs", "", 12, "text", w=GV_OW - 20, h=18)))
    ob = SC + "GvOb"
    ap.append(("#" + oi, G_.glass_group(ob, GV_OW - 20, 34, layout="Left", anchor={"top": 8})))
    ap.append(("#" + ob, G_.glass_button(SC + "GvOy", "Accept", "primary", w=140, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + ob, G_.glass_button(SC + "GvOn", "Decline", "secondary", w=140, h=34, size=13)))
    ap.append(("#" + go, lab(None, "CREATE A GUILD", 15, "accentHi", bold=True, w=SC_VI, h=24, anchor={"top": 20})))
    orw = SC + "GvOr"
    ap.append(("#" + go, G_.glass_group(orw, SC_VI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + orw, G_.text_field(SC + "GvOfBox", SC + "GvOf", w=360, h=32, placeholder="Guild name", max_length=32, size=13, anchor={"right": 6})))
    ap.append(("#" + orw, G_.glass_button(SC + "GvOgo", "Create guild", "primary", w=180, h=34, size=13)))
    ap.append(("#" + go, lab(SC + "GvOh", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 4})))
    ap.append(("#" + go, lab(SC + "GvOx", "", 12, "dim", w=SC_VI, h=18, anchor={"top": 16})))
    ap.sets.append((SC + "GvOx", "Text", "Guild chat: /gc <message>. Your guild's members, bank and log show here once you are in one."))
    assert 26 + 116 + 44 + 40 + 22 + 34 <= GV_BH and 24 + 18 + 42 <= 104 - 20, "0.3.73: the not-in-a-guild card fits"
    out.append(("G", ap, [("#" + SC + "GvRf", "gvrf"), ("#" + SC + "GvMpp", "gpg:-1"), ("#" + SC + "GvMpn", "gpg:1"),
                          ("#" + SC + "GvGpp", "glpg:-1"), ("#" + SC + "GvGpn", "glpg:1")]))
    return out
'''
P.rep('''    out.append(("A", ap, []))
    return out
''', GV_VIEW_PY)
P.rep('''_sc_rt = {"H": SC_MN + 1, "S": SV_RUNTIME_MAX, "P": 0, "A": AV_RUNTIME_MAX}   # run time: the home fills / the stats rows / the member fills
SC_SHELL_ELEMENTS = _sc_by["0"] + max(_sc_by[_s] for _s in "HSPA")
SC_RUNTIME_MAX = max(_sc_rt.values())
SC_ELEMENTS = _sc_by["0"] + max(_sc_by[_s] + _sc_rt[_s] for _s in "HSPA")
print("0.3.71 social sections (elements, + at run time): frame %d, %s" % (_sc_by["0"], ", ".join("%s %d + %d" % (_s, _sc_by[_s], _sc_rt[_s]) for _s in "HSPA")))''',
      '''_sc_rt = {"H": SC_MN + 1, "S": SV_RUNTIME_MAX, "P": 0, "A": AV_RUNTIME_MAX, "G": GV_RUNTIME_MAX}   # run time: the home fills / the stats rows / the member fills / the guild tabs + XP fill
SC_SHELL_ELEMENTS = _sc_by["0"] + max(_sc_by[_s] for _s in "HSPAG")
SC_RUNTIME_MAX = max(_sc_rt.values())
SC_ELEMENTS = _sc_by["0"] + max(_sc_by[_s] + _sc_rt[_s] for _s in "HSPAG")
print("0.3.73 social sections (elements, + at run time): frame %d, %s" % (_sc_by["0"], ", ".join("%s %d + %d" % (_s, _sc_by[_s], _sc_rt[_s]) for _s in "HSPAG")))
assert not [x_ for x_ in ["Gs%d" % k_ for k_ in range(len(GV_SUB))] if SC + x_ in _sc_ids], "0.3.73: a guild run-time id is also a static id"''')
P.rep('''           "AvTt", "AvTy", "AvA", "AvLv", "AvDb", "AvCh"]''',
      '''           "AvTt", "AvTy", "AvA", "AvLv", "AvDb", "AvCh",
           # 0.3.73 (oldmenu5): the guild view
           "Gv", "GvH", "GvRf", "GvI", "GvN", "GvL", "GvB", "GvX", "GvLv", "GvDb", "GvSt", "GvSh", "GvM", "GvMp", "GvMpp", "GvMg", "GvMpn", "GvIv",
           "GvIf", "GvIgo", "GvIh", "GvMn", "GvK", "GvKv", "GvKp", "GvKu", "GvKf", "GvKd", "GvKw", "GvKh", "GvKl", "GvKlf", "GvKla", "GvKlm",
           "GvKlh", "GvKn", "GvKs", "GvG", "GvGp", "GvGpp", "GvGg", "GvGpn", "GvGn", "GvO", "GvOi", "GvOq", "GvOs", "GvOy", "GvOn", "GvOf",
           "GvOgo", "GvOh", "GvOx"]
          + ["GvR%d%s" % (k_, x_) for k_ in range(GV_MN) for x_ in ("", "N", "T", "S", "Q", "P", "K", "L")]
          + ["GvE%d%s" % (k_, x_) for k_ in range(GV_LN) for x_ in ("", "W", "P", "T", "B")]''')

# ---- the SocialTabData + the SocialTab fields
P.rep('''               ("DISQ", SC_TXT["disq"]), ("MSGNONE", SC_TXT["msgnone"]), ("CHAT", SC_TXT["chat"]), ("VCAP", SC_TXT["vcap"])):
    F(scd, "public static final String %s = %s;" % (_n, jstr(_v)))''',
      '''               ("DISQ", SC_TXT["disq"]), ("MSGNONE", SC_TXT["msgnone"]), ("CHAT", SC_TXT["chat"]), ("VCAP", SC_TXT["vcap"])):
    F(scd, "public static final String %s = %s;" % (_n, jstr(_v)))
# 0.3.73 (oldmenu5): the guild view
for _n, _v in (("GVMN", GV_MN), ("GVLN", GV_LN), ("GVBARW", GV_BARW)):
    F(scd, "public static final int %s = %d;" % (_n, _v))
F(scd, "public static final String[] GSUB = %s;" % jarr(GV_SUB))
for _n, _v in (("GTAB", GV_TAB), ("GST0", MT_ST_CAT), ("GST1", MT_ST_CATSEL), ("GVREAD", GV_READ), ("GVOLD", GV_TXT["gvold"]), ("GVOFF", GV_TXT["gvoff"]),
               ("GVFAIL", GV_TXT["gvfail"])):
    F(scd, "public static final String %s = %s;" % (_n, jstr(_v)))''')
P.rep('''           "public String avTpa;", "public boolean avLead;", "public long disArm;", "public String msgKeep;", "public String invKeep;",''',
      '''           "public String avTpa;", "public boolean avLead;", "public long disArm;", "public String msgKeep;", "public String invKeep;",
           # 0.3.73 (oldmenu5): the guild view (4) - the read's token + profile key, the drawn rows + their buttons, the typed boxes
           "public String gTok;", "public String gPk;", "public boolean gOk;", "public boolean gIn;", "public boolean gInv;", "public int gMy;",
           "public String gArm;", "public int gSub;", "public int gPage;", "public int gPages;", "public int gLPage;", "public int gLPages;",
           "public String[] gIds;", "public int[] gBtn;", "public String gAllow;", "public String gLast;", "public String gKeepN;", "public String gKeepI;",
           "public String gKeepA;", "public String gKeepL;", "public String[] gNm;",''')
P.rep('''  this.msgKeep = "";
  this.invKeep = "";
  this.builds = 0;
  this.answers = 0;
}""")
# 0.3.64: THE SETTINGS SCREEN DATA''', '''  this.msgKeep = "";
  this.invKeep = "";
  this.gTok = null;        // 0.3.73 (oldmenu5)
  this.gPk = null;
  this.gOk = false;
  this.gIn = false;
  this.gInv = false;
  this.gMy = -1;
  this.gArm = "";
  this.gSub = 0;
  this.gPage = 0;
  this.gPages = 1;
  this.gLPage = 0;
  this.gLPages = 1;
  this.gIds = new String[0];
  this.gBtn = new int[0];
  this.gNm = new String[0];
  this.gAllow = "|";
  this.gLast = null;
  this.gKeepN = "";
  this.gKeepI = "";
  this.gKeepA = "";
  this.gKeepL = "";
  this.builds = 0;
  this.answers = 0;
}""")
# 0.3.64: THE SETTINGS SCREEN DATA''')

# ---- the Guild card's texts name the guild view (no old page)
P.rep('''  b.set("#SkyyStabGr.Text", !on ? "" : (!has ? "The Guild page makes one or shows your invites."''',
      '''  b.set("#SkyyStabGr.Text", !on ? "" : (!has ? "Manage guild makes one or shows your invites."   // 0.3.73''')
P.rep('''"+" + (ol.length - g + 1) + " more on the Guild page"''', '''"+" + (ol.length - g + 1) + " more - Manage guild shows them"''')

GV_JAVA = r'''# ---- 0.3.73 (oldmenu5): THE GUILD VIEW. guild:fn:act (SkyyGuilds 0.1.14) as the player with the read's token + profile key; null = not there
M(stab, r"""
public String gact(String op, String arg) {
  if (@PKG@.InvCraft.fn("guild:fn:act") == null) return null;
  Object r = call("guild:fn:act", new Object[] { op, this.playerRef.getUuid(), this.gTok, this.gPk, arg });
  return r instanceof String ? (String) r : "-That could not run here - nothing changed.";
}""")
# a typed name: no control characters, quotes, backslashes or '|' (the bridge cuts at 200; GuildStore checks the name)
M(stab, r"""
public static String gtext(String s, int max) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < max; i++) {
    char c = s.charAt(i);
    if (c < 32 || c == 127 || c == 34 || c == 92 || c == '|') continue;
    sb.append(c);
  }
  return sb.toString().trim();
}""")
# a typed amount / limit = what the guild page's box takes (500, 2k, 1.5m, all, none): letters, digits, . and , only, 16 at most
M(stab, r"""
public static String gamt(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 16; i++) {
    char c = s.charAt(i);
    if ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '.' || c == ',') sb.append(c);
  }
  return sb.toString().toLowerCase();
}""")
M(stab, r"""
public static String gfmt(String s) { return @PKG@.MenuUtil.fmt(@PKG@.InvPage.toLong(s, 0L)); }""")
M(stab, r"""
public static String limT(String s) {
  long v = @PKG@.InvPage.toLong(s, -1L);
  if (v < 0L) return "no limit";
  if (v == 0L) return "no withdrawing";
  return @PKG@.MenuUtil.fmt(v) + " a day";
}""")
M(stab, r"""
public static String netT(String s) {
  long v = @PKG@.InvPage.toLong(s, 0L);
  if (v > 0L) return "+" + @PKG@.MenuUtil.fmt(v);
  if (v < 0L) return "-" + @PKG@.MenuUtil.fmt(-v);
  return "0";
}""")
M(stab, r"""
public static String rankN(int r) { return r >= 2 ? "Leader" : (r == 1 ? "Admin" : "Member"); }""")
M(stab, r"""
public void gvHide(@UCB@ b, String head) {
  b.set("#SkyyStabGvH.Text", head);
  b.set("#SkyyStabGvI.Visible", false);
  b.set("#SkyyStabGvO.Visible", false);
  this.gOk = false;
  this.gIn = false;
  this.gInv = false;
  this.gIds = new String[0];
  this.gBtn = new int[0];
  this.gAllow = "|";
}""")
# MEMBERS: m|uuid|rank|guildXpAdded|online|takenToday|bankContribution|<name> in the page's order; the page's buttons by rank (GuildPage.buildGuild)
M(stab, r"""
public void gvMembers(@UCB@ b, @UEB@ ev, java.util.ArrayList ms, int my, String[] h, String[] cn) {
  String me = this.playerRef.getUuid().toString();
  int n = @PKG@.SocialTabData.GVMN;
  this.gPages = (ms.size() + n - 1) / n;
  if (this.gPages < 1) this.gPages = 1;
  if (this.gPage >= this.gPages) this.gPage = this.gPages - 1;
  if (this.gPage < 0) this.gPage = 0;
  this.gIds = new String[n];
  this.gBtn = new int[n];
  this.gNm = new String[n];
  for (int i = 0; i < n; i++) {
    String r = "SkyyStabGvR" + i;
    int ix = this.gPage * n + i;
    this.gIds[i] = "";
    this.gBtn[i] = 0;
    this.gNm[i] = "";
    if (ix >= ms.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) ms.get(ix);
    String u = f[1];
    int rr = @PKG@.InvPage.toInt(f[2], 0);
    boolean on = "1".equals(f[4]);
    boolean self = u.equals(me);
    long took = @PKG@.InvPage.toLong(f[5], 0L);
    this.gIds[i] = u;
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[7]), 28) + (self ? "  (you)" : ""));
    b.set("#" + r + "T.Text", rankN(rr));
    b.set("#" + r + "S.Text", (on ? "online" : "offline") + "   -   " + gfmt(f[3]) + " guild XP added   -   bank contribution " + netT(f[6])
        + "   -   taken today " + (took > 0L ? @PKG@.MenuUtil.fmt(took) + " coins" : "-"));
    int bt = 0;
    if (my == 2 && !self) bt = bt | (rr == 0 ? 1 : 2);
    if (!self && rr < my && my >= 1) bt = bt | 4;
    if (my == 2 && !self) bt = bt | 8;
    // fix (LOCKED 2026-10-10 "Invite to party"): an online member who is not you, every rank = /party invite <the drawn name>
    String pn = @PKG@.MenuUtil.cleanName(f[7]);
    if (!self && on && pn.length() > 0) { bt = bt | 16; this.gNm[i] = pn; }
    this.gBtn[i] = bt;
    b.set("#" + r + "Q.Visible", (bt & 16) != 0);
    if ((bt & 16) != 0) ev.addEventBinding(@BT@.Activating, "#" + r + "Q", @EVD@.of("a", "gm:pty:" + i).append("t", this.tok));
    b.set("#" + r + "P.Visible", (bt & 3) != 0);
    b.set("#" + r + "K.Visible", (bt & 4) != 0);
    b.set("#" + r + "L.Visible", (bt & 8) != 0);
    if ((bt & 3) != 0) {
      b.set("#" + r + "P.Text", (bt & 1) != 0 ? "Promote" : "Demote");
      ev.addEventBinding(@BT@.Activating, "#" + r + "P", @EVD@.of("a", ((bt & 1) != 0 ? "gm:pro:" : "gm:dem:") + i).append("t", this.tok));
    }
    if ((bt & 4) != 0) {
      b.set("#" + r + "K.Text", this.gArm.equals("kick:" + u) ? "Sure" : "Kick");
      ev.addEventBinding(@BT@.Activating, "#" + r + "K", @EVD@.of("a", "gm:kick:" + i).append("t", this.tok));
    }
    if ((bt & 8) != 0) {
      b.set("#" + r + "L.Text", this.gArm.equals("transfer:" + u) ? "Confirm" : "Make leader");
      ev.addEventBinding(@BT@.Activating, "#" + r + "L", @EVD@.of("a", "gm:lead:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyStabGvMg.Text", "Page " + (this.gPage + 1) + " / " + this.gPages);
  b.set("#SkyyStabGvMp.Visible", this.gPages > 1);
  int tot = cn != null && cn.length >= 5 ? @PKG@.InvPage.toInt(cn[2], ms.size()) : ms.size();
  b.set("#SkyyStabGvMn.Text", (tot > ms.size() ? (tot - ms.size()) + " more members are not shown here.   " : "")
      + "Kick and Make leader ask first: press the same button again within 10 s.");
  b.set("#SkyyStabGvIv.Visible", my >= 1);
  if (my >= 1) {
    String tk = String.valueOf((char) 64) + "GI";
    b.set("#SkyyStabGvIf.Value", this.gKeepI);
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGvIgo", @EVD@.of("a", "gv:inv").append("t", this.tok).append(tk, "#SkyyStabGvIf.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyStabGvIf", @EVD@.of("a", "gv:inv").append("t", this.tok).append(tk, "#SkyyStabGvIf.Value"), false);
    this.gAllow = this.gAllow + "inv|";
  }
  b.set("#SkyyStabGvIh.Text", my >= 1 ? "Invite: an online player's name - the invite lasts " + h[20] + " s." : "Only the Leader and Admins can invite players.");
}""")
# BANK: the page's bank view (GuildPage.buildBank) - the bank, your purse, the limits + your usage, Deposit / Withdraw, the Leader's limits
M(stab, r"""
public void gvBank(@UCB@ b, @UEB@ ev, int my, String[] h) {
  String tk = String.valueOf((char) 64);
  b.set("#SkyyStabGvKv.Text", "Guild bank  " + gfmt(h[11]) + " coins");
  long c = -1L;
  try { c = @PKG@.MenuUtil.purse(this.playerRef.getUuid()); } catch (Throwable t) { c = -1L; }
  b.set("#SkyyStabGvKp.Text", c < 0L ? "" : "Your purse  " + @PKG@.MenuUtil.fmt(c) + " coins");
  boolean wd = "1".equals(h[19]);
  b.set("#SkyyStabGvKu.Text", @PKG@.MenuUtil.clip("Withdraw limits per game day:  Admins " + limT(h[16]) + "  -  Members " + limT(h[17]) + "      You: "
      + (my >= 2 ? "no limit (Leader)" : @PKG@.MenuUtil.safe(h[24])) + (h[25].length() > 0 ? "   (" + @PKG@.MenuUtil.safe(h[25]) + ")" : ""), 160));
  b.set("#SkyyStabGvKf.Value", this.gKeepA);
  ev.addEventBinding(@BT@.Activating, "#SkyyStabGvKd", @EVD@.of("a", "gv:dep").append("t", this.tok).append(tk + "GA", "#SkyyStabGvKf.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyStabGvKf", @EVD@.of("a", "gv:amt").append("t", this.tok).append(tk + "GA", "#SkyyStabGvKf.Value"), false);
  this.gAllow = this.gAllow + "dep|amt|";
  b.set("#SkyyStabGvKw.Visible", wd);
  if (wd) {
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGvKw", @EVD@.of("a", "gv:wd").append("t", this.tok).append(tk + "GA", "#SkyyStabGvKf.Value"));
    this.gAllow = this.gAllow + "wd|";
  }
  b.set("#SkyyStabGvKh.Text", "Amounts: 500, 2k, 1.5m or all - coins come from and go to your purse." + (wd ? "" : "  Your rank can't withdraw right now (daily limit 0)."));
  b.set("#SkyyStabGvKl.Visible", my == 2);
  b.set("#SkyyStabGvKn.Visible", my != 2);
  if (my == 2) {
    b.set("#SkyyStabGvKlf.Value", this.gKeepL);
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGvKla", @EVD@.of("a", "gv:lima").append("t", this.tok).append(tk + "GL", "#SkyyStabGvKlf.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGvKlm", @EVD@.of("a", "gv:limm").append("t", this.tok).append(tk + "GL", "#SkyyStabGvKlf.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyStabGvKlf", @EVD@.of("a", "gv:limh").append("t", this.tok).append(tk + "GL", "#SkyyStabGvKlf.Value"), false);
    this.gAllow = this.gAllow + "lima|limm|limh|";
  }
  b.set("#SkyyStabGvKs.Text", "Members add " + h[15] + "% of the skill XP they earn to the guild's XP.");
}""")
# LOG: l|when|bankAfter|who|<what>, newest first (the page's log text), 15 a page
M(stab, r"""
public void gvLog(@UCB@ b, java.util.ArrayList lg, String[] cn) {
  int n = @PKG@.SocialTabData.GVLN;
  this.gLPages = (lg.size() + n - 1) / n;
  if (this.gLPages < 1) this.gLPages = 1;
  if (this.gLPage >= this.gLPages) this.gLPage = this.gLPages - 1;
  if (this.gLPage < 0) this.gLPage = 0;
  for (int i = 0; i < n; i++) {
    String r = "SkyyStabGvE" + i;
    int ix = this.gLPage * n + i;
    if (ix >= lg.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) lg.get(ix);
    long ba = @PKG@.InvPage.toLong(f[2], -1L);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "W.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[1]), 26));
    b.set("#" + r + "P.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[3]), 26));
    b.set("#" + r + "T.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(f[4]), 100));
    b.set("#" + r + "B.Text", ba >= 0L ? @PKG@.MenuUtil.fmt(ba) + " coins" : "");
  }
  b.set("#SkyyStabGvGg.Text", "Page " + (this.gLPage + 1) + " / " + this.gLPages);
  b.set("#SkyyStabGvGp.Visible", this.gLPages > 1);
  int tot = cn != null && cn.length >= 5 ? @PKG@.InvPage.toInt(cn[4], lg.size()) : lg.size();
  b.set("#SkyyStabGvGn.Text", lg.size() == 0 ? "No deposits or withdrawals yet." : "Newest first   -   " + lg.size() + (tot > lg.size() ? " newest of " + tot : "") + " bank moves kept");
}""")
# THE GUILD VIEW: guild:fn:act state "500|300" -> h| (26 fields), n| the name, c| counts, m| members, l| log, i| a live invite
M(stab, r"""
public void fillGv(@UCB@ b, @UEB@ ev) {
  this.gOk = false;
  this.gIds = new String[0];
  this.gBtn = new int[0];
  this.gAllow = "|";
  String s = gact("state", @PKG@.SocialTabData.GVREAD);
  this.gLast = s;
  if (s == null) { gvHide(b, hasCmd("guild") ? @PKG@.SocialTabData.GVOLD : @PKG@.SocialTabData.GVOFF); return; }
  String[] ls = split(s, "\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? split(ls[0], "\\|") : new String[0];
  if (h.length < 26) { gvHide(b, @PKG@.SocialTabData.GVFAIL); return; }
  this.gTok = h[2];
  this.gPk = h[3];
  this.gOk = true;
  this.gIn = "1".equals(h[1]);
  this.gMy = @PKG@.InvPage.toInt(h[4], -1);
  this.gArm = h[21];
  java.util.ArrayList ms = new java.util.ArrayList();
  java.util.ArrayList lg = new java.util.ArrayList();
  String name = "";
  String[] iv = null;
  String[] cn = null;
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("n|")) name = l.substring(2);
    else if (l.startsWith("m|")) { String[] f = l.split("\\|", 8); if (f.length >= 8) ms.add(f); }
    else if (l.startsWith("l|")) { String[] f = l.split("\\|", 5); if (f.length >= 5) lg.add(f); }
    else if (l.startsWith("i|")) { String[] f = l.split("\\|", 7); if (f.length >= 7) iv = f; }
    else if (l.startsWith("c|")) cn = l.split("\\|", -1);
  }
  String tk = String.valueOf((char) 64) + "GN";
  if (!this.gIn) {
    b.set("#SkyyStabGvI.Visible", false);
    b.set("#SkyyStabGvO.Visible", true);
    b.set("#SkyyStabGvH.Text", "Make a guild, or accept an invite.");
    this.gInv = iv != null;
    b.set("#SkyyStabGvOi.Visible", this.gInv);
    if (this.gInv) {
      b.set("#SkyyStabGvOq.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(iv[5]) + " invited you to " + @PKG@.MenuUtil.safe(iv[6]) + (iv[4].length() > 0 ? "  [" + @PKG@.MenuUtil.safe(iv[4]) + "]" : ""), 80));
      b.set("#SkyyStabGvOs.Text", "Guild Lv " + iv[2] + "  -  " + iv[3] + " members  -  " + iv[1] + " s left to answer");
      ev.addEventBinding(@BT@.Activating, "#SkyyStabGvOy", @EVD@.of("a", "gv:acc").append("t", this.tok));
      ev.addEventBinding(@BT@.Activating, "#SkyyStabGvOn", @EVD@.of("a", "gv:dec").append("t", this.tok));
      this.gAllow = this.gAllow + "acc|dec|";
    }
    b.set("#SkyyStabGvOf.Value", this.gKeepN);
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGvOgo", @EVD@.of("a", "gv:create").append("t", this.tok).append(tk, "#SkyyStabGvOf.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyStabGvOf", @EVD@.of("a", "gv:create").append("t", this.tok).append(tk, "#SkyyStabGvOf.Value"), false);
    this.gAllow = this.gAllow + "create|";
    b.set("#SkyyStabGvOh.Text", "Type a name, then Create guild (or Enter). An invite lasts " + h[20] + " s; a guild holds up to " + h[14] + " members.");
    return;
  }
  b.set("#SkyyStabGvO.Visible", false);
  b.set("#SkyyStabGvI.Visible", true);
  int my = this.gMy;
  String tag = h[23];
  b.set("#SkyyStabGvH.Text", "");
  b.set("#SkyyStabGvN.Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(name) + (tag.length() > 0 ? "  [" + @PKG@.MenuUtil.safe(tag) + "]" : ""), 60));
  b.set("#SkyyStabGvL.Text", "Guild Lv " + h[5] + "   -   Season " + h[10] + ": " + gfmt(h[9]) + " guild XP   -   You are " + (my >= 2 ? "the Leader" : (my == 1 ? "an Admin" : "a Member")));
  long xi = @PKG@.InvPage.toLong(h[6], 0L);
  long xn = @PKG@.InvPage.toLong(h[7], 0L);
  if (xn > 0L) {
    int w = @PKG@.InvPage.barW(xi, xn, @PKG@.SocialTabData.GVBARW);
    if (w > 0) b.appendInline("#SkyyStabGvB", @PKG@.SocialTabData.FILLX.replace("{W}", String.valueOf(w)));
  }
  b.set("#SkyyStabGvX.Text", (xn > 0L ? "Guild XP " + @PKG@.MenuUtil.fmt(xi) + " / " + @PKG@.MenuUtil.fmt(xn) + " to the next level" : "Guild XP " + gfmt(h[8]))
      + "   -   members add " + h[15] + "% of the skill XP they earn");
  b.set("#SkyyStabGvSh.Text", "Members " + h[13] + " / " + h[14] + "   -   " + h[12] + " online   -   Guild bank " + gfmt(h[11]) + " coins");
  boolean aL = "leave".equals(this.gArm);
  boolean aD = "disband".equals(this.gArm);
  b.set("#SkyyStabGvLv.Text", aL ? "Click again to leave" : "Leave guild");
  ev.addEventBinding(@BT@.Activating, "#SkyyStabGvLv", @EVD@.of("a", "gv:leave").append("t", this.tok));
  this.gAllow = this.gAllow + "leave|";
  b.set("#SkyyStabGvDb.Visible", my == 2);
  if (my == 2) {
    b.set("#SkyyStabGvDb.Text", aD ? "Click again to DISBAND" : "Disband guild");
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGvDb", @EVD@.of("a", "gv:dis").append("t", this.tok));
    this.gAllow = this.gAllow + "dis|";
  }
  if (this.gSub < 0 || this.gSub > 2) this.gSub = 0;
  for (int i = 0; i < 3; i++) {
    b.appendInline("#SkyyStabGvSt", @PKG@.SocialTabData.GTAB.replace("{I}", "Gs" + i).replace("{S}", i == this.gSub ? @PKG@.SocialTabData.GST1 : @PKG@.SocialTabData.GST0));
    b.set("#SkyyStabGs" + i + ".Text", @PKG@.SocialTabData.GSUB[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyStabGs" + i, @EVD@.of("a", "gs:" + i));
  }
  b.set("#SkyyStabGvM.Visible", this.gSub == 0);
  b.set("#SkyyStabGvK.Visible", this.gSub == 1);
  b.set("#SkyyStabGvG.Visible", this.gSub == 2);
  if (this.gSub == 0) gvMembers(b, ev, ms, my, h, cn);
  else if (this.gSub == 1) gvBank(b, ev, my, h);
  else gvLog(b, lg, cn);
}""")
'''
P.rep('''M(stab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''', GV_JAVA + '''M(stab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''')
P.rep('''  char cur = this.view == 1 ? 'S' : (this.view == 2 ? 'P' : (this.view == 3 ? 'A' : 'H'));''',
      '''  char cur = this.view == 1 ? 'S' : (this.view == 2 ? 'P' : (this.view == 3 ? 'A' : (this.view == 4 ? 'G' : 'H')));   // 0.3.73: + G (guild)''')
P.rep('''    try { fillAv(b, ev); } catch (Throwable t) { this.avIds = new String[0]; @PKG@.MenuUtil.warn("social screen: the party view failed: " + t); }
  }''', '''    try { fillAv(b, ev); } catch (Throwable t) { this.avIds = new String[0]; @PKG@.MenuUtil.warn("social screen: the party view failed: " + t); }
  } else if (this.view == 4) {   // 0.3.73 (oldmenu5): the guild view
    try { fillGv(b, ev); } catch (Throwable t) { this.gOk = false; this.gIds = new String[0]; this.gBtn = new int[0]; this.gAllow = "|"; @PKG@.MenuUtil.warn("social screen: the guild view failed: " + t); }
  }''')
P.rep('''  this.view = v;
  this.svPage = 0;''', '''  this.view = v;
  this.svPage = 0;
  this.gPage = 0;          // 0.3.73
  this.gLPage = 0;''')

GV_ACT = r'''# ---- 0.3.73 (oldmenu5): the guild view's actions - each answers with ONE packet (the redraw with the bridge's line in the caption)
M(stab, r"""
public boolean gHas(String k) { return this.gAllow != null && this.gAllow.indexOf("|" + k + "|") >= 0; }""")
M(stab, r"""
public void gvDo(String op, String arg) {
  this.answered = true;
  if (!this.gOk) { say("Your guild is not ready - nothing changed."); return; }
  String r = gact(op, arg);
  if (r == null) { this.tcap = hasCmd("guild") ? @PKG@.SocialTabData.GVOLD : @PKG@.SocialTabData.GVOFF; redraw(); return; }
  String m = r.trim();
  if (m.startsWith("+")) {
    if (op.equals("create")) this.gKeepN = "";
    if (op.equals("invite")) this.gKeepI = "";
    if (op.equals("deposit") || op.equals("withdraw")) this.gKeepA = "";
    if (op.equals("limitadmin") || op.equals("limitmember")) this.gKeepL = "";
    if (op.equals("create") || op.equals("accept") || op.equals("leave") || op.equals("disband")) { this.gSub = 0; this.gPage = 0; this.gLPage = 0; }
  }
  this.tcap = m.length() == 0 ? "" : msgOf(m);
  redraw();
}""")
# a member row's button: only the drawn member, only a button the drawing showed on that row (1 Promote, 2 Demote, 4 Kick, 8 Make leader)
M(stab, r"""
public void gvRow(String op, String a, int cut, int bit) {
  this.answered = true;
  int k = @PKG@.InvPage.toInt(a.substring(cut), -1);
  if (k < 0 || this.gIds == null || this.gBtn == null || k >= this.gIds.length || k >= this.gBtn.length || this.gIds[k] == null || this.gIds[k].length() == 0) { say("Nobody there"); return; }
  if ((this.gBtn[k] & bit) == 0) { say("That button is not on this page - nothing changed"); return; }
  gvDo(op, this.gIds[k]);
}""")
# fix (LOCKED 2026-10-10): Invite to party on a drawn online member = the Players page's /party invite line through runLine (its checks + caption)
M(stab, r"""
public void gvParty(String a) {
  this.answered = true;
  int k = @PKG@.InvPage.toInt(a.substring(7), -1);
  if (k < 0 || this.gBtn == null || this.gNm == null || k >= this.gBtn.length || k >= this.gNm.length) { say("Nobody there"); return; }
  if ((this.gBtn[k] & 16) == 0 || this.gNm[k] == null || this.gNm[k].length() == 0) { say("That button is not on this page - nothing changed"); return; }
  runLine("party invite " + this.gNm[k], false);
}""")
'''
P.rep('''M(stab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', GV_ACT + '''M(stab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''    // 0.3.71 (F6): the Stats / Profiles / Party pages are views of this screen (no Full page); the Guild page stays (OLD_LEFT)''',
      '''    // 0.3.71 (F6): the Stats / Profiles / Party pages are views of this screen (no Full page); 0.3.73: the Guild page too (the guild view)
    boolean gvw = a.startsWith("gv:") || a.startsWith("gm:") || a.startsWith("gs:") || a.startsWith("gpg:") || a.startsWith("glpg:") || a.equals("gvrf");
    if (gvw && this.view != 4) { say("That button is not on this page - nothing changed"); return; }''')
P.rep('''    if (a.equals("guild")) { hub("social", "guild", "the Guild page"); return; }''',
      '''    if (a.equals("guild")) { goView(4); return; }   // 0.3.73 (oldmenu5): the guild view (SkyyGuilds 0.1.14 guild:fn:act)
    if (a.startsWith("gs:")) { int k = @PKG@.InvPage.toInt(a.substring(3), 0); this.gSub = k < 0 || k > 2 ? 0 : k; this.tcap = ""; redraw(); return; }
    if (a.equals("gvrf")) { if (this.gOk) gact("refresh", null); this.tcap = ""; redraw(); return; }   // the page's Refresh (drops an armed confirm)
    if (a.startsWith("gpg:") || a.startsWith("glpg:")) {
      boolean lgp = a.startsWith("glpg:");
      int dg = @PKG@.InvPage.toInt(a.substring(lgp ? 5 : 4), 0);
      int cur = lgp ? this.gLPage : this.gPage;
      int max = lgp ? this.gLPages : this.gPages;
      int ng = cur + (dg < 0 ? -1 : 1);
      if (ng < 0 || ng >= max) { say(ng < 0 ? "This is the first page" : "This is the last page"); return; }
      if (lgp) this.gLPage = ng; else this.gPage = ng;
      this.tcap = "";
      redraw();
      return;
    }''')
P.rep('''    if (a.startsWith("sw:")) { swAsk(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }''',
      '''    // 0.3.73 (oldmenu5): the guild view's actions (token + profile checked above; each button only where the drawing showed it)
    if (a.startsWith("gv:")) {
      String gk = a.substring(3);
      String at = String.valueOf((char) 64);
      if (!gHas(gk)) { say("That button is not on this page - nothing changed"); return; }
      if (gk.equals("create")) {
        String nm = gtext(@PKG@.InvPage.val(d, at + "GN"), 32);
        this.gKeepN = nm;
        if (nm.length() == 0) { say("Type a guild name first, then Create guild."); return; }
        gvDo("create", nm);
        return;
      }
      if (gk.equals("acc")) { gvDo("accept", null); return; }
      if (gk.equals("dec")) { gvDo("decline", null); return; }
      if (gk.equals("inv")) {
        String nm = @PKG@.MenuUtil.cleanName(@PKG@.InvPage.val(d, at + "GI"));
        this.gKeepI = nm;
        if (nm.length() == 0) { say("Type an online player's name first, then Invite."); return; }
        gvDo("invite", nm);
        return;
      }
      if (gk.equals("dep") || gk.equals("wd") || gk.equals("amt")) {
        String am = gamt(@PKG@.InvPage.val(d, at + "GA"));
        this.gKeepA = am;
        gvDo(gk.equals("dep") ? "deposit" : (gk.equals("wd") ? "withdraw" : "amounthint"), am);
        return;
      }
      if (gk.equals("lima") || gk.equals("limm") || gk.equals("limh")) {
        String am = gamt(@PKG@.InvPage.val(d, at + "GL"));
        this.gKeepL = am;
        gvDo(gk.equals("lima") ? "limitadmin" : (gk.equals("limm") ? "limitmember" : "limithint"), am);
        return;
      }
      if (gk.equals("leave")) { gvDo("leave", null); return; }
      if (gk.equals("dis")) { gvDo("disband", null); return; }
      say("That button is not on this page - nothing changed");
      return;
    }
    if (a.startsWith("gm:pro:")) { gvRow("promote", a, 7, 1); return; }
    if (a.startsWith("gm:dem:")) { gvRow("demote", a, 7, 2); return; }
    if (a.startsWith("gm:kick:")) { gvRow("kick", a, 8, 4); return; }
    if (a.startsWith("gm:lead:")) { gvRow("transfer", a, 8, 8); return; }
    if (a.startsWith("gm:pty:")) { gvParty(a); return; }
    if (a.startsWith("sw:")) { swAsk(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }''')

# ======================================================================= MARKET: the Auction House view (section U)
P.rep('''MT_SUBS = ["Market", "Bazaar orders", "Merchants"]''', '''MT_SUBS = ["Market", "Bazaar orders", "Merchants", "Auction House"]   # 0.3.73: + the Auction House view''')
HV_PY = r'''
# ---- 0.3.73 (oldmenu5): THE AUCTION HOUSE VIEW (section U) - SkyyAuctions 0.1.18 ah:fn:tab / ah:fn:tabact (contract tools/auctions_0_1_18_patch.py)
HMODE = ["Browse", "Create BIN", "Manage"]                  # the mode buttons (run time; Browse also marks the item mode)
HV_BH = MT_VBH - 34 - 6 - 24                                # under the mode row + the banner (720)
HV_SQ = MV_SQ                                               # the rarity square behind an icon (52)
HV_RN, HV_RH = 9, 58                                        # BROWSE: rows a page
HV_PW, HV_VW = 220, 110                                     # a row's price, View
HV_RTW = MT_VI - 12 - HV_SQ - 8 - HV_PW - 8 - HV_VW         # a browse row's text column
HV_FLW, HV_FVW = 90, 190                                    # a filter's label, its value
HV_ILW = 900                                                # ITEM: the facts card
HV_IRW = MT_VI - HV_ILW - 10                                # the buy card (626)
HV_DN = 8                                                   # description lines shown
HV_CLW = 760                                                # CREATE: your stacks
HV_CRW = MT_VI - HV_CLW - 10                                # the new listing (766)
HV_CN, HV_CH = 10, 56                                       # stacks a page
HV_CTW = HV_CLW - 20 - 12 - HV_SQ - 8 - 8 - 100             # a stack row's text column
HV_MN, HV_MH = 9, 58                                        # MANAGE: rows a page
HV_MBW = 150
HV_MTW = MT_VI - 12 - HV_SQ - 8 - HV_PW - 8 - HV_MBW        # a manage row's text column
HV_TXT = {
    "hvold": "This needs SkyyAuctions 0.1.18 - this server has an older one. /ah works.",
    "hvoff": "The Auction House is not on this server right now.",
    "hvfail": "The Auction House could not be read right now - try again in a moment.",
    "hvcap": "Buy It Now only. Browse, View an item, Buy now - or list your own with Create BIN.",
    "hvchk": "Here is the fee for the price you typed - check it, then press again.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in HV_TXT.values() for c_ in v_), "0.3.73: plain texts"
for _k in ("hvold", "hvoff", "hvfail"):
    assert SUI.text_width(HV_TXT[_k], 13) <= MT_VI - 240 - len(MT_SUBS) * (MT_VBW + 6), ("0.3.73: an auction head line fits", _k)
for _k in ("hvcap", "hvchk"):
    assert SUI.text_width(HV_TXT[_k], 14) <= IV_IW - 420, ("0.3.73: a caption fits the hint row", _k)
assert HV_RTW >= 600 and HV_CTW >= 300 and HV_MTW >= 600, (HV_RTW, HV_CTW, HV_MTW)
for _l in HMODE:
    assert SUI.text_width(_l, 14, bold=True) <= MT_VBW - 16, ("0.3.73: a mode button fits", _l)
for _l in ("BUY NOW", "CONFIRM BUY", "YES, CANCEL IT", "Cancel listing", "CREATE BIN", "LIST IT"):
    assert SUI.text_width(_l, 15, bold=True) <= 320 - 16, ("0.3.73: a big button fits", _l)
for _l in ("Claim coins", "Claim item", "Yes, cancel", "Cancel"):
    assert SUI.text_width(_l, 13, bold=True) <= HV_MBW - 12, ("0.3.73: a manage button fits", _l)
assert SUI.text_width("999,999,999,999 coins", 15, bold=True) <= HV_PW, "0.3.73: a price fits"
HV_RUNTIME_MAX = len(HMODE) + max(HV_RN, HV_CN + 1, HV_MN, 1)   # the mode buttons + a rarity square per row (+ the picked stack)
'''
P.rep('''MV_RUNTIME_MAX = MV_KN + MV_SN                              # the shop tabs + a rarity square per stock row
''', '''MV_RUNTIME_MAX = MV_KN + MV_SN                              # the shop tabs + a rarity square per stock row
''' + HV_PY)
HV_VIEW_PY = r'''    out.append(("M", ap, bm + [("#" + MT + "MvRf", "mrf"), ("#" + MT + "MvPp", "mpg:-1"), ("#" + MT + "MvPn", "mpg:1")]))
    # ======== U: THE AUCTION HOUSE (0.3.73, oldmenu5: the old Auction House pages - SkyyAuctions 0.1.18 ah:fn:tab / tabact; Buy It Now only)
    ap = SUI.Appends()

    def sqrow(ap, parent, r_, w, h, role):   # a row with the rarity square behind the item icon (the merchants' stock row pattern)
        ap.append(("#" + parent, G_.glass_group(r_, w, h, role=role, layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        q_ = r_ + "Q"
        hm, kids = SUI.keep_holder(q_, HV_SQ, HV_SQ, [SUI.keep_at0("Group #%sBg { Anchor: (Width: %d, Height: %d); }" % (r_, HV_SQ, HV_SQ))], anchor={"top": (h - HV_SQ) // 2})
        ap.append(("#" + r_, hm))
        ap.extend(kids)
        ap.append(("#" + q_, SUI.keep_at0(G_.glass_grid(r_ + "I", 1, 1, drag=False, slot=HV_SQ - 6, icon=HV_SQ - 14)).replace("Left: 0, Top: 0", "Left: 3, Top: 3")))

    def sqicon(ap, parent, r_, anchor):      # an icon with its square (the item / the picked stack)
        q_ = r_ + "Q"
        hm, kids = SUI.keep_holder(q_, HV_SQ, HV_SQ, [SUI.keep_at0("Group #%sBg { Anchor: (Width: %d, Height: %d); }" % (r_, HV_SQ, HV_SQ))], anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)
        ap.append(("#" + q_, SUI.keep_at0(G_.glass_grid(r_ + "I", 1, 1, drag=False, slot=HV_SQ - 6, icon=HV_SQ - 14)).replace("Left: 0, Top: 0", "Left: 3, Top: 3")))

    def pgrow(ap, parent, pid, extra=None):   # < Page n / m > (the merchants' stock pages)
        ap.append(("#" + parent, G_.glass_group(pid, MT_VI if extra is None else extra, 30, layout="Left", anchor={"top": 6})))
        ap.append(("#" + pid, G_.glass_button(pid + "p", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
        ap.append(("#" + pid, lab(pid + "g", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
        ap.append(("#" + pid, G_.glass_button(pid + "n", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))
    hv = MT + "Hv"
    ap.append(("#" + win, G_.glass_group(hv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bu = vhead(ap, hv, "Hv", "AUCTION HOUSE", 3)
    hk = MT + "Hvk"
    ap.append(("#" + hv, G_.glass_group(hk, MT_VI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + hk, G_.glass_group(MT + "HvMd", len(HMODE) * (MT_VBW + 6), 34, layout="Left")))
    ap.append(("#" + hk, lab(MT + "HvW", "", 13, "text", w=MT_VI - len(HMODE) * (MT_VBW + 6) - 2 * (112 + 8), h=34, halign="End", anchor={"right": 8})))
    ap.append(("#" + hk, G_.glass_button(MT + "HvNn", "Not now", "secondary", w=112, h=34, size=13, anchor={"right": 8})))
    ap.append(("#" + hk, G_.glass_button(MT + "HvRf", "Refresh", "secondary", w=112, h=34, size=13)))
    ap.append(("#" + hv, lab(MT + "HvBn", "", 13, "red", bold=True, w=MT_VI, h=20, anchor={"top": 4})))
    hb = MT + "Hvb"
    ap.append(("#" + hv, G_.glass_group(hb, MT_VI, HV_BH, layout="Top")))
    assert 20 + 34 + 6 + 34 + 24 + HV_BH <= IV_BODY_H, "0.3.73: the auction view fits"
    # ---- BROWSE
    br = MT + "HvBr"
    ap.append(("#" + hb, G_.glass_group(br, MT_VI, HV_BH, layout="Top")))
    f1 = MT + "HvF1"
    ap.append(("#" + br, G_.glass_group(f1, MT_VI, 34, layout="Left")))
    for x_, t_ in (("c", "Category"), ("s", "Sort"), ("r", "Rarity")):
        ap.append(("#" + f1, lab(None, t_, 13, "dim", bold=True, w=HV_FLW, h=34)))
        ap.append(("#" + f1, G_.glass_button(MT + "HvF%sp" % x_, "<", "secondary", w=36, h=30, size=14, anchor={"top": 2})))
        ap.append(("#" + f1, lab(MT + "HvF%sv" % x_, "", 14, "title", bold=True, w=HV_FVW, h=34, halign="Center")))
        ap.append(("#" + f1, G_.glass_button(MT + "HvF%sn" % x_, ">", "secondary", w=36, h=30, size=14, anchor={"top": 2, "right": 24})))
    assert 3 * (HV_FLW + 36 + HV_FVW + 36 + 24) <= MT_VI and SUI.text_width("Accessories", 14, bold=True) <= HV_FVW and SUI.text_width("Tier then name", 14, bold=True) <= HV_FVW, \
        "0.3.73: the filter row fits"
    f2 = MT + "HvF2"
    ap.append(("#" + br, G_.glass_group(f2, MT_VI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + f2, G_.text_field(MT + "HvQBox", MT + "HvQ", w=320, h=32, placeholder="Search items", max_length=40, size=13, anchor={"right": 6})))
    ap.append(("#" + f2, G_.glass_button(MT + "HvGo", "Search", "primary", w=120, h=34, size=13, anchor={"right": 12})))
    lv = MT + "HvLv"
    ap.append(("#" + f2, G_.glass_group(lv, 290, 34, layout="Left", anchor={"right": 12})))
    ap.append(("#" + lv, lab(None, "Level", 13, "dim", bold=True, w=64, h=34)))
    ap.append(("#" + lv, G_.text_field(MT + "HvLaBox", MT + "HvLa", w=96, h=32, placeholder="min", max_length=6, size=13, anchor={"right": 6})))
    ap.append(("#" + lv, lab(None, "to", 13, "dim", w=24, h=34)))
    ap.append(("#" + lv, G_.text_field(MT + "HvLbBox", MT + "HvLb", w=96, h=32, placeholder="max", max_length=6, size=13)))
    # fix (oldmenu5 critic): "Reset" = the word the AH's own empty line names ("... click Reset to see every listing")
    ap.append(("#" + f2, G_.glass_button(MT + "HvClr", "Reset", "secondary", w=112, h=34, size=13, anchor={"right": 12})))
    ap.append(("#" + f2, lab(MT + "HvFs", "", 12, "dim", w=MT_VI - 326 - 132 - 302 - 124, h=34)))
    ap.append(("#" + br, lab(MT + "HvX", "", 12, "red", w=MT_VI, h=18, anchor={"top": 4})))
    for k_ in range(HV_RN):
        r_ = "%sHvR%d" % (MT, k_)
        sqrow(ap, br, r_, MT_VI, HV_RH, "inset")
        rx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(rx, HV_RTW, HV_RH, layout="Top", anchor={"left": 8})))
        ap.append(("#" + rx, lab(r_ + "N", "", 14, "row", bold=True, w=HV_RTW, h=24, anchor={"top": 7})))
        ap.append(("#" + rx, lab(r_ + "S", "", 11, "xp", bold=True, w=HV_RTW, h=18)))
        ap.append(("#" + r_, lab(r_ + "P", "", 15, "xp", bold=True, w=HV_PW, h=HV_RH, halign="End", anchor={"right": 8})))
        ap.append(("#" + r_, G_.glass_button(r_ + "V", "View", "primary", w=HV_VW, h=32, size=13, anchor={"top": (HV_RH - 32) // 2})))
    pgrow(ap, br, MT + "HvP")
    ap.append(("#" + MT + "HvP", G_.glass_button(MT + "HvMore", "Show more", "secondary", w=150, h=28, size=13, anchor={"left": 20})))
    ap.append(("#" + br, lab(MT + "HvE", "", 12, "dim", w=MT_VI, h=18, anchor={"top": 4})))
    assert 34 + 40 + 22 + HV_RN * (HV_RH + 4) + 36 + 22 <= HV_BH, "0.3.73: the browse rows fit"
    # ---- ITEM
    it = MT + "HvIt"
    ap.append(("#" + hb, G_.glass_group(it, MT_VI, HV_BH, layout="Left")))
    il = MT + "HvIl"
    ap.append(("#" + it, G_.glass_group(il, HV_ILW, HV_BH, role="inset", layout="Top", pad=10)))
    ih = MT + "HvIh"
    ap.append(("#" + il, G_.glass_group(ih, HV_ILW - 20, 64, layout="Left")))
    sqicon(ap, ih, MT + "HvIq", {"top": 6})
    ix = MT + "HvIx"
    ap.append(("#" + ih, G_.glass_group(ix, HV_ILW - 20 - HV_SQ - 10, 64, layout="Top", anchor={"left": 10})))
    ap.append(("#" + ix, lab(MT + "HvIn", "", 20, "title", bold=True, w=HV_ILW - 20 - HV_SQ - 10, h=28)))
    ap.append(("#" + ix, lab(MT + "HvIs", "", 13, "xp", bold=True, w=HV_ILW - 20 - HV_SQ - 10, h=18)))
    ap.append(("#" + ix, lab(MT + "HvIg", "", 12, "accentHi", w=HV_ILW - 20 - HV_SQ - 10, h=18)))
    ap.append(("#" + il, lab(None, "FACTS", 12, "dim", bold=True, w=HV_ILW - 20, h=18, anchor={"top": 12})))
    for k_ in range(9):
        ap.append(("#" + il, lab(MT + "HvIf%d" % k_, "", 13, "text", w=HV_ILW - 20, h=22)))
    ap.append(("#" + il, lab(None, "ABOUT", 12, "dim", bold=True, w=HV_ILW - 20, h=18, anchor={"top": 12})))
    for k_ in range(HV_DN):
        ap.append(("#" + il, lab(MT + "HvId%d" % k_, "", 12, "dim", w=HV_ILW - 20, h=18)))
    assert 20 + 64 + 30 + 9 * 22 + 30 + HV_DN * 18 <= HV_BH, "0.3.73: the item facts fit"
    ap.append(("#" + it, "Group { Anchor: (Width: 10); }"))
    ir = MT + "HvIr"
    ap.append(("#" + it, G_.glass_group(ir, HV_IRW, HV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + ir, lab(None, "BUY IT NOW", 12, "dim", bold=True, w=HV_IRW - 20, h=18)))
    ap.append(("#" + ir, lab(MT + "HvIp", "", 26, "xp", bold=True, w=HV_IRW - 20, h=36, anchor={"top": 4})))
    ap.append(("#" + ir, lab(MT + "HvIe", "", 12, "dim", w=HV_IRW - 20, h=18)))
    ap.append(("#" + ir, G_.glass_button(MT + "HvIb", "BUY NOW", "primary", w=320, h=44, size=15, anchor={"top": 16})))
    ap.append(("#" + ir, lab(MT + "HvIc", "", 12, "action", w=HV_IRW - 20, h=18, anchor={"top": 6})))
    ap.append(("#" + ir, lab(MT + "HvIo", "", 13, "red", bold=True, w=HV_IRW - 20, h=20, anchor={"top": 10})))
    ap.append(("#" + ir, lab(MT + "HvIo2", "", 13, "red", bold=True, w=HV_IRW - 20, h=20)))
    ap.append(("#" + ir, lab(MT + "HvIk", "", 12, "dim", w=HV_IRW - 20, h=18, anchor={"top": 20})))
    ap.sets.append((MT + "HvIk", "Text", "Browse (above) goes back to the listings."))
    # ---- CREATE BIN
    cr = MT + "HvCr"
    ap.append(("#" + hb, G_.glass_group(cr, MT_VI, HV_BH, layout="Left")))
    cl = MT + "HvCl"
    ap.append(("#" + cr, G_.glass_group(cl, HV_CLW, HV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + cl, lab(None, "YOUR ITEMS  -  pick a stack to list", 12, "dim", bold=True, w=HV_CLW - 20, h=18)))
    for k_ in range(HV_CN):
        r_ = "%sHvJ%d" % (MT, k_)
        sqrow(ap, cl, r_, HV_CLW - 20, HV_CH, "panel")
        rx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(rx, HV_CTW, HV_CH, layout="Top", anchor={"left": 8, "right": 8})))
        ap.append(("#" + rx, lab(r_ + "N", "", 13, "row", bold=True, w=HV_CTW, h=22, anchor={"top": 7})))
        ap.append(("#" + rx, lab(r_ + "S", "", 11, "xp", bold=True, w=HV_CTW, h=18)))
        ap.append(("#" + r_, G_.glass_button(r_ + "K", "Pick", "secondary", w=100, h=30, size=13, anchor={"top": (HV_CH - 30) // 2})))
    pgrow(ap, cl, MT + "HvJp", HV_CLW - 20)
    ap.append(("#" + cl, lab(MT + "HvJn", "", 12, "dim", w=HV_CLW - 20, h=18, anchor={"top": 4})))
    assert 18 + HV_CN * (HV_CH + 4) + 36 + 22 <= HV_BH - 20, "0.3.73: the stacks fit"
    ap.append(("#" + cr, "Group { Anchor: (Width: 10); }"))
    cx = MT + "HvCx"
    ap.append(("#" + cr, G_.glass_group(cx, HV_CRW, HV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + cx, lab(None, "NEW BUY IT NOW LISTING", 15, "accentHi", bold=True, w=HV_CRW - 20, h=24)))
    cp = MT + "HvCp"
    ap.append(("#" + cx, G_.glass_group(cp, HV_CRW - 20, 64, layout="Left", anchor={"top": 10})))
    sqicon(ap, cp, MT + "HvCpq", {"top": 6})
    cpx = MT + "HvCpx"
    ap.append(("#" + cp, G_.glass_group(cpx, HV_CRW - 20 - HV_SQ - 10, 64, layout="Top", anchor={"left": 10})))
    ap.append(("#" + cpx, lab(MT + "HvCpn", "", 16, "title", bold=True, w=HV_CRW - 20 - HV_SQ - 10, h=26)))
    ap.append(("#" + cpx, lab(MT + "HvCps", "", 12, "xp", w=HV_CRW - 20 - HV_SQ - 10, h=18)))
    ap.append(("#" + cpx, lab(MT + "HvCpl", "", 12, "dim", w=HV_CRW - 20 - HV_SQ - 10, h=18)))
    ap.append(("#" + cx, lab(MT + "HvCpw", "", 13, "red", bold=True, w=HV_CRW - 20, h=20, anchor={"top": 4})))
    cq = MT + "HvCq"
    ap.append(("#" + cx, G_.glass_group(cq, HV_CRW - 20, 34, layout="Left", anchor={"top": 12})))
    ap.append(("#" + cq, lab(None, "Price", 13, "dim", bold=True, w=110, h=34)))
    ap.append(("#" + cq, G_.text_field(MT + "HvCvBox", MT + "HvCv", w=260, h=32, placeholder="Coins", max_length=16, size=14, anchor={"right": 6})))
    ap.append(("#" + cq, G_.glass_button(MT + "HvCck", "Check fee", "secondary", w=150, h=34, size=13)))
    ap.append(("#" + cx, lab(MT + "HvCvw", "", 12, "red", w=HV_CRW - 20, h=18, anchor={"top": 2})))
    cd = MT + "HvCd"
    ap.append(("#" + cx, G_.glass_group(cd, HV_CRW - 20, 34, layout="Left", anchor={"top": 10})))
    ap.append(("#" + cd, lab(None, "Duration", 13, "dim", bold=True, w=110, h=34)))
    ap.append(("#" + cd, G_.glass_button(MT + "HvCdp", "<", "secondary", w=36, h=30, size=14, anchor={"top": 2})))
    ap.append(("#" + cd, lab(MT + "HvCdv", "", 14, "title", bold=True, w=120, h=34, halign="Center")))
    ap.append(("#" + cd, G_.glass_button(MT + "HvCdn", ">", "secondary", w=36, h=30, size=14, anchor={"top": 2})))
    for k_ in range(3):
        ap.append(("#" + cx, lab(MT + "HvCf%d" % k_, "", 12, "text", w=HV_CRW - 20, h=18, anchor={"top": 12} if k_ == 0 else None)))
    ap.append(("#" + cx, lab(MT + "HvCz", "", 14, "green", bold=True, w=HV_CRW - 20, h=22, anchor={"top": 6})))
    cg = MT + "HvCg"
    ap.append(("#" + cx, G_.glass_group(cg, HV_CRW - 20, 44, layout="Left", anchor={"top": 14})))
    ap.append(("#" + cg, G_.glass_button(MT + "HvCgo", "CREATE BIN", "primary", w=320, h=44, size=15)))
    ap.append(("#" + cx, lab(MT + "HvCn", "", 12, "dim", w=HV_CRW - 20, h=18, anchor={"top": 8})))
    assert 24 + 74 + 24 + 46 + 20 + 44 + 66 + 28 + 58 + 26 <= HV_BH - 20, "0.3.73: the new listing card fits"
    # ---- MANAGE
    mg = MT + "HvMg"
    ap.append(("#" + hb, G_.glass_group(mg, MT_VI, HV_BH, layout="Top")))
    mh = MT + "HvMh"
    ap.append(("#" + mg, G_.glass_group(mh, MT_VI, 34, layout="Left")))
    ap.append(("#" + mh, lab(MT + "HvMs", "", 13, "text", bold=True, w=MT_VI - 208, h=34, anchor={"right": 8})))
    ap.append(("#" + mh, G_.glass_button(MT + "HvMca", "Claim all", "primary", w=200, h=34, size=13)))
    ap.append(("#" + mg, lab(MT + "HvMo", "", 12, "dim", w=MT_VI, h=18, anchor={"top": 4})))
    for k_ in range(HV_MN):
        r_ = "%sHvK%d" % (MT, k_)
        sqrow(ap, mg, r_, MT_VI, HV_MH, "inset")
        rx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(rx, HV_MTW, HV_MH, layout="Top", anchor={"left": 8})))
        ap.append(("#" + rx, lab(r_ + "N", "", 14, "row", bold=True, w=HV_MTW, h=24, anchor={"top": 7})))
        ap.append(("#" + rx, lab(r_ + "S", "", 11, "text", w=HV_MTW, h=18)))
        ap.append(("#" + r_, lab(r_ + "P", "", 15, "xp", bold=True, w=HV_PW, h=HV_MH, halign="End", anchor={"right": 8})))
        ap.append(("#" + r_, G_.glass_button(r_ + "B", "Claim coins", "primary", w=HV_MBW, h=32, size=13, anchor={"top": (HV_MH - 32) // 2})))
    pgrow(ap, mg, MT + "HvKp")
    ap.append(("#" + mg, lab(MT + "HvKn", "", 12, "dim", w=MT_VI, h=18, anchor={"top": 4})))
    assert 34 + 22 + HV_MN * (HV_MH + 4) + 36 + 22 <= HV_BH, "0.3.73: the manage rows fit"
    out.append(("U", ap, bu + [("#" + MT + "HvRf", "hvrf"), ("#" + MT + "HvFcp", "hvc:-1"), ("#" + MT + "HvFcn", "hvc:1"), ("#" + MT + "HvFsp", "hvs:-1"),
                               ("#" + MT + "HvFsn", "hvs:1"), ("#" + MT + "HvFrp", "hvr:-1"), ("#" + MT + "HvFrn", "hvr:1"), ("#" + MT + "HvClr", "hvclr"),
                               ("#" + MT + "HvPp", "hvpg:-1"), ("#" + MT + "HvPn", "hvpg:1"), ("#" + MT + "HvMore", "hvmore"), ("#" + MT + "HvJpp", "hvjpg:-1"),
                               ("#" + MT + "HvJpn", "hvjpg:1"), ("#" + MT + "HvCdp", "hvd:-1"), ("#" + MT + "HvCdn", "hvd:1"), ("#" + MT + "HvKpp", "hvkpg:-1"),
                               ("#" + MT + "HvKpn", "hvkpg:1")]))
    return out
'''
P.rep('''    out.append(("M", ap, bm + [("#" + MT + "MvRf", "mrf"), ("#" + MT + "MvPp", "mpg:-1"), ("#" + MT + "MvPn", "mpg:1")]))
    return out
''', HV_VIEW_PY)
P.rep('''_mt_rt = {"H": MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1, "O": OV_RUNTIME_MAX, "M": MV_RUNTIME_MAX}   # the rail / chips / bank fill; the sides; tabs + squares
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOM")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOM")
print("0.3.72 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOM")))''',
      '''_mt_rt = {"H": MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1, "O": OV_RUNTIME_MAX, "M": MV_RUNTIME_MAX, "U": HV_RUNTIME_MAX}   # + 0.3.73: the AH modes + squares
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOMU")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMU")
print("0.3.73 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOMU")))''')
P.rep('''             "MvH", "MvT0", "MvT1", "MvT2", "MvK", "MvW", "MvRf", "MvZx", "MvSh", "MvSs", "MvP", "MvPp", "MvPg", "MvPn", "MvSn"]''',
      '''             "MvH", "MvT0", "MvT1", "MvT2", "MvK", "MvW", "MvRf", "MvZx", "MvSh", "MvSs", "MvP", "MvPp", "MvPg", "MvPn", "MvSn",
             # 0.3.73 (oldmenu5): the Auction House view
             "Hv", "HvH", "HvT0", "HvT1", "HvT2", "HvT3", "HvMd", "HvW", "HvNn", "HvRf", "HvBn", "HvBr", "HvFcp", "HvFcv", "HvFcn", "HvFsp", "HvFsv",
             "HvFsn", "HvFrp", "HvFrv", "HvFrn", "HvQ", "HvGo", "HvLv", "HvLa", "HvLb", "HvClr", "HvFs", "HvX", "HvP", "HvPp", "HvPg", "HvPn",
             "HvMore", "HvE", "HvIt", "HvIqBg", "HvIqI", "HvIn", "HvIs", "HvIg", "HvIp", "HvIe", "HvIb", "HvIc", "HvIo", "HvIo2", "HvCr", "HvJp",
             "HvJpp", "HvJpg", "HvJpn", "HvJn", "HvCp", "HvCpqBg", "HvCpqI", "HvCpn", "HvCps", "HvCpl", "HvCpw", "HvCv", "HvCck", "HvCvw", "HvCdp",
             "HvCdv", "HvCdn", "HvCz", "HvCgo", "HvCn", "HvMg", "HvMs", "HvMca", "HvMo", "HvKp", "HvKpp", "HvKpg", "HvKpn", "HvKn"]
          + ["HvIf%d" % k_ for k_ in range(9)] + ["HvId%d" % k_ for k_ in range(HV_DN)] + ["HvCf%d" % k_ for k_ in range(3)]
          + ["HvR%d%s" % (k_, x_) for k_ in range(HV_RN) for x_ in ("", "Q", "Bg", "I", "N", "S", "P", "V")]
          + ["HvJ%d%s" % (k_, x_) for k_ in range(HV_CN) for x_ in ("", "Q", "Bg", "I", "N", "S", "K")]
          + ["HvK%d%s" % (k_, x_) for k_ in range(HV_MN) for x_ in ("", "Q", "Bg", "I", "N", "S", "P", "B")]''')
P.rep('''    + ["Sd0", "Sd1"] + ["Mk%d" % k_ for k_ in range(MV_KN)]   # 0.3.72: the side / shop tab buttons''',
      '''    + ["Sd0", "Sd1"] + ["Mk%d" % k_ for k_ in range(MV_KN)] + ["Hm%d" % k_ for k_ in range(len(HMODE))]   # 0.3.72: the side / shop tab buttons; 0.3.73: + the AH modes''')
P.rep('''_mt_tok = SUI.proven_tokens(list(MT_AP))''', '''_mt_tok = SUI.proven_tokens(list(MT_AP))
assert not [x_ for x_ in ("Ab0", "Ab1", "Ab2") if ("#" + MT + x_) not in [b_[0] for b_ in MT_BINDS]], "0.3.73: the AH card's buttons stay (they open the Auction House view)"''')

# ---- the MarketTabData + the MarketTab fields
P.rep('''               ("MVOFF", MT_VTXT["mvoff"]), ("MVFAR", MT_VTXT["mvfar"]), ("MVFAIL", MT_VTXT["mvfail"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))''',
      '''               ("MVOFF", MT_VTXT["mvoff"]), ("MVFAR", MT_VTXT["mvfar"]), ("MVFAIL", MT_VTXT["mvfail"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))
# 0.3.73 (oldmenu5): the Auction House view
for _n, _v in (("HVRN", HV_RN), ("HVCN", HV_CN), ("HVMN", HV_MN), ("HVDN", HV_DN)):
    F(mtd, "public static final int %s = %d;" % (_n, _v))
F(mtd, "public static final String[] HMODE = %s;" % jarr(HMODE))
for _n, _v in (("HVOLD", HV_TXT["hvold"]), ("HVOFF", HV_TXT["hvoff"]), ("HVFAIL", HV_TXT["hvfail"]), ("HVCAP", HV_TXT["hvcap"]), ("HVCHK", HV_TXT["hvchk"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))''')
P.rep('''           "public String[] msNpc;", "public String[] msId;", "public String[] msPrice;", "public int[] msLeft;", "public int mpage;", "public int mpages;",''',
      '''           "public String[] msNpc;", "public String[] msId;", "public String[] msPrice;", "public int[] msLeft;", "public int mpage;", "public int mpages;",
           # 0.3.73 (oldmenu5): the Auction House view (3) - its mode (0 browse, 1 item, 2 create, 3 manage), the read's arguments, the read's
           # profile key + token, and what the last drawing showed (the rows' ids, the stacks, the buy line, the manage rows)
           "public int hvMode;", "public int hvCat;", "public int hvSort;", "public int hvRar;", "public String hvQ;", "public String hvLa;", "public String hvLb;",
           "public int hvMax;", "public int hvPage;", "public int hvPages;", "public int hvCPage;", "public int hvCPages;", "public int hvMPage;", "public int hvMPages;",
           "public String hvId;", "public int hvSec;", "public int hvSlot;", "public String hvSig;", "public String hvPrice;", "public String hvPriceSeen;",
           "public String hvPriceWhy;", "public boolean hvPriceOk;", "public boolean hvPick;", "public boolean hvReady;", "public int hvDur;", "public int hvDurN;",
           "public int hvCatN;", "public int hvSortN;", "public int hvRarN;", "public String hvPk;", "public String hvTok;", "public boolean hvOk;",
           "public String hvLast;", "public boolean hvArmed;", "public boolean hvClaimAll;", "public String[] hvRows;", "public int[] hvCs;", "public int[] hvCl;",
           "public String[] hvCg;", "public boolean[] hvCo;", "public int hvBuyK;", "public String hvBuyId;", "public long hvBuyP;", "public String[] hvMIds;",
           "public String[] hvMKind;", "public boolean[] hvMBtn;",''')
P.rep('''  this.mpage = 0;
  this.mpages = 1;
  this.builds = 0;
  this.answers = 0;
  this.calls = 0;
}""")
# 0.3.62: THE WORLD SCREEN DATA''', '''  this.mpage = 0;
  this.mpages = 1;
  this.hvMode = 0;         // 0.3.73 (oldmenu5)
  this.hvCat = 0;
  this.hvSort = 0;
  this.hvRar = 0;
  this.hvQ = "";
  this.hvLa = "";
  this.hvLb = "";
  this.hvMax = 100;
  this.hvPage = 0;
  this.hvPages = 1;
  this.hvCPage = 0;
  this.hvCPages = 1;
  this.hvMPage = 0;
  this.hvMPages = 1;
  this.hvId = "";
  this.hvSec = -1;
  this.hvSlot = -1;
  this.hvSig = "";
  this.hvPrice = "";
  this.hvPriceSeen = "";
  this.hvPriceWhy = "";
  this.hvPriceOk = false;
  this.hvPick = false;
  this.hvReady = false;
  this.hvDur = -1;
  this.hvDurN = 0;
  this.hvCatN = 0;
  this.hvSortN = 0;
  this.hvRarN = 0;
  this.hvPk = "";
  this.hvTok = "";
  this.hvOk = false;
  this.hvLast = null;
  this.hvArmed = false;
  this.hvClaimAll = false;
  this.hvRows = new String[0];
  this.hvCs = new int[0];
  this.hvCl = new int[0];
  this.hvCg = new String[0];
  this.hvCo = new boolean[0];
  this.hvBuyK = 0;
  this.hvBuyId = "";
  this.hvBuyP = -1L;
  this.hvMIds = new String[0];
  this.hvMKind = new String[0];
  this.hvMBtn = new boolean[0];
  this.builds = 0;
  this.answers = 0;
  this.calls = 0;
}""")
# 0.3.62: THE WORLD SCREEN DATA''')
P.rep('''col(@PKG@.MarketTabData.FOOT, "Open: the Auction House on it")''', '''col(@PKG@.MarketTabData.FOOT, "Open: these auctions in the Auction House view")''')

HV_JAVA = r'''# ---- 0.3.73 (oldmenu5): THE AUCTION HOUSE VIEW. ah:fn:tab (SkyyAuctions 0.1.18 AhTabFn mode 0) reads; the drawing keeps what it showed
M(mtab, r"""
public static String ahSq(String c) {
  String h = hexOf(c);
  if (h == null || h.equalsIgnoreCase(@PKG@.MarketTabData.NONEC)) return null;
  return h + "(0.4)";
}""")
M(mtab, r"""
public static String tierT(int t) { return t > 0 && t < 99 ? "T" + t : ""; }""")
# a listing's Style Guide 15 tooltip: the name in its rarity colour, the tier tag, the AH's sub line, price / each gold, ends, the yellow footer
M(mtab, r"""
public static String htip(String name, String hex, int tier, long qty, long price, long each, String ends, String sub, String foot) {
  String lf = String.valueOf((char) 10);
  StringBuilder sb = new StringBuilder();
  sb.append(col(hex != null ? hex : @PKG@.MarketTabData.SOFT, name));
  if (tier > 0 && tier < 99) sb.append(lf).append(col(@PKG@.MarketTabData.TAGCOL, "T" + tier));
  if (sub != null && sub.length() > 0) sb.append(lf).append(col(@PKG@.MarketTabData.DIMC, @PKG@.MenuUtil.clip(sub, 80)));
  sb.append(lf).append(lf);
  sb.append(col(@PKG@.MarketTabData.SOFT, "Amount  ")).append(col(@PKG@.MarketTabData.GOLD, "x" + qty));
  if (price >= 0L) sb.append(lf).append(col(@PKG@.MarketTabData.SOFT, "Price  ")).append(col(@PKG@.MarketTabData.GOLD, money(price) + " coins"));
  if (qty > 1L && each >= 0L) sb.append(lf).append(col(@PKG@.MarketTabData.SOFT, "Each  ")).append(col(@PKG@.MarketTabData.GOLD, money(each) + " coins"));
  if (ends != null && ends.length() > 0) sb.append(lf).append(col(@PKG@.MarketTabData.SOFT, "Ends in  ")).append(col(@PKG@.MarketTabData.GOLD, ends));
  if (foot != null && foot.length() > 0) sb.append(lf).append(lf).append(col(@PKG@.MarketTabData.FOOT, foot));
  return sb.toString();
}""")
M(mtab, r"""
public static void hvSquare(@UCB@ b, String row, String c) {
  String sq = ahSq(c);
  if (sq != null) b.appendInline("#" + row + "Bg", @PKG@.MarketTabData.SQ.replace("{C}", sq));
}""")
# the name of index i in k| / s| / t| / u| lines (i|name)
M(mtab, r"""
public static String nameAt(java.util.ArrayList l, int i) {
  String k = String.valueOf(i);
  for (int j = 0; j < l.size(); j++) {
    String[] f = (String[]) l.get(j);
    if (f.length >= 3 && f[1].equals(k)) return @PKG@.MenuUtil.clip(f[2], 22);
  }
  return "-";
}""")
# the stacks to list: sorted by tier, then name (Skyy 2026-10-16 "sort everything by tier")
M(mtab, r"""
public static boolean cellAfter(String[] a, String[] b) {
  int ta = ni(a[6], 99);
  int tb = ni(b[6], 99);
  if (ta != tb) return ta > tb;
  return a[9].toLowerCase().compareTo(b[9].toLowerCase()) > 0;
}""")
M(mtab, r"""
public static void sortCells(java.util.ArrayList cs) {
  for (int i = 1; i < cs.size(); i++) {
    String[] x = (String[]) cs.get(i);
    int j = i - 1;
    while (j >= 0 && cellAfter((String[]) cs.get(j), x)) { cs.set(j + 1, cs.get(j)); j = j - 1; }
    cs.set(j + 1, x);
  }
}""")
M(mtab, r"""
public String hvRead(java.util.UUID u) {
  String vw = this.hvMode == 1 ? "item" : (this.hvMode == 2 ? "create" : (this.hvMode == 3 ? "manage" : "browse"));
  Object o = call("ah:fn:tab", new Object[] { u, vw, Integer.valueOf(this.hvCat), Integer.valueOf(this.hvSort), Integer.valueOf(this.hvRar), this.hvQ, this.hvLa,
      this.hvLb, Integer.valueOf(this.hvMode == 3 ? 1000 : this.hvMax), this.hvId, Integer.valueOf(this.hvMode == 2 ? this.hvSec : -1), Integer.valueOf(this.hvSlot),
      this.hvSig, this.hvPrice, Integer.valueOf(this.hvDur) });
  this.calls = this.calls + 1;
  return o instanceof String ? (String) o : null;
}""")
# BROWSE: k| s| t| (the AH's category / sort / rarity lists), f| (the read's own filters + summary), x| e| r| (15 fields, the AH's order)
M(mtab, r"""
public void hvBrowse(@UCB@ b, @UEB@ ev, String[] ls) {
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList ss = new java.util.ArrayList();
  java.util.ArrayList ts = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  String[] f = null;
  String x = "";
  String e = "";
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) ks.add(sp(l, 3));
    else if (l.startsWith("s|")) ss.add(sp(l, 3));
    else if (l.startsWith("t|")) ts.add(sp(l, 3));
    else if (l.startsWith("f|")) f = sp(l, 10);
    else if (l.startsWith("x|")) x = l.substring(2);
    else if (l.startsWith("e|")) e = l.substring(2);
    else if (l.startsWith("r|")) { String[] r = sp(l, 16); if (r.length >= 16) rs.add(r); }
  }
  this.hvCatN = ks.size();
  this.hvSortN = ss.size();
  this.hvRarN = ts.size();
  boolean fo = f != null && f.length >= 10;
  if (fo) { this.hvCat = ni(f[1], 0); this.hvSort = ni(f[2], 0); this.hvRar = ni(f[3], 0); }
  b.set("#SkyyMtabHvFcv.Text", nameAt(ks, this.hvCat));
  b.set("#SkyyMtabHvFsv.Text", nameAt(ss, this.hvSort));
  b.set("#SkyyMtabHvFrv.Text", nameAt(ts, this.hvRar));
  String tk = String.valueOf((char) 64);
  b.set("#SkyyMtabHvQ.Value", this.hvQ);
  b.set("#SkyyMtabHvLa.Value", this.hvLa);
  b.set("#SkyyMtabHvLb.Value", this.hvLb);
  boolean lv = fo && "1".equals(f[6]);
  b.set("#SkyyMtabHvLv.Visible", lv);
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabHvGo", @EVD@.of("a", "hvq").append(tk + "H1", "#SkyyMtabHvQ.Value").append(tk + "H2", "#SkyyMtabHvLa.Value").append(tk + "H3", "#SkyyMtabHvLb.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyMtabHvQ", @EVD@.of("a", "hvq").append(tk + "H1", "#SkyyMtabHvQ.Value").append(tk + "H2", "#SkyyMtabHvLa.Value").append(tk + "H3", "#SkyyMtabHvLb.Value"), false);
  if (lv) {
    ev.addEventBinding(@BT@.Validating, "#SkyyMtabHvLa", @EVD@.of("a", "hvq").append(tk + "H1", "#SkyyMtabHvQ.Value").append(tk + "H2", "#SkyyMtabHvLa.Value").append(tk + "H3", "#SkyyMtabHvLb.Value"), false);
    ev.addEventBinding(@BT@.Validating, "#SkyyMtabHvLb", @EVD@.of("a", "hvq").append(tk + "H1", "#SkyyMtabHvQ.Value").append(tk + "H2", "#SkyyMtabHvLa.Value").append(tk + "H3", "#SkyyMtabHvLb.Value"), false);
  }
  b.set("#SkyyMtabHvFs.Text", fo ? @PKG@.MenuUtil.clip(f[9], 90) : "");
  b.set("#SkyyMtabHvX.Text", @PKG@.MenuUtil.clip(x, 120));
  int n = @PKG@.MarketTabData.HVRN;
  this.hvPages = (rs.size() + n - 1) / n;
  if (this.hvPages < 1) this.hvPages = 1;
  if (this.hvPage >= this.hvPages) this.hvPage = this.hvPages - 1;
  if (this.hvPage < 0) this.hvPage = 0;
  this.hvRows = new String[n];
  for (int i = 0; i < n; i++) {
    String r = "SkyyMtabHvR" + i;
    int ix = this.hvPage * n + i;
    this.hvRows[i] = "";
    if (ix >= rs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] w = (String[]) rs.get(ix);
    long qty = nl(w[3], 1L);
    long pr = nl(w[6], -1L);
    long ea = nl(w[7], -1L);
    int tr = ni(w[4], 99);
    int st = ni(w[10], 0);
    boolean off = "1".equals(w[11]);
    long gs = nl(w[12], 0L);
    this.hvRows[i] = w[1];
    hvSquare(b, r, w[5]);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", @PKG@.InvPage.act(one(cell(w[2], (int) qty, w[15], htip(w[15], hexOf(w[5]), tr, qty, pr, ea, w[9], w[14], "View: the item and Buy now")))));
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(w[15], 44));
    String t = tierT(tr);
    b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip((t.length() > 0 ? t + "   -   " : "") + "x" + qty + "   -   " + money(ea) + " each   -   ends in " + @PKG@.MenuUtil.clip(w[9], 14) + "   -   "
        + (st == 1 ? "yours" : (st == 2 ? "your other profile" : "by " + @PKG@.MenuUtil.clip(w[13], 20))) + (off ? "   -   off the market" : "") + (gs > 0L ? "   -   for sale in " + gs + " s" : ""), 150));
    b.set("#" + r + "P.Text", pr >= 0L ? money(pr) + " coins" : "-");
    ev.addEventBinding(@BT@.Activating, "#" + r + "V", @EVD@.of("a", "hvv:" + i).append("t", this.tok));
  }
  boolean more = fo && ni(f[7], 0) > ni(f[8], 0) && this.hvMax < 1000;
  b.set("#SkyyMtabHvPg.Text", "Page " + (this.hvPage + 1) + " / " + this.hvPages);
  b.set("#SkyyMtabHvP.Visible", this.hvPages > 1 || more);
  b.set("#SkyyMtabHvMore.Visible", more);
  b.set("#SkyyMtabHvE.Text", rs.size() == 0 ? @PKG@.MenuUtil.clip(e, 110)
      : rs.size() + " shown" + (fo && ni(f[7], 0) > rs.size() ? " of " + ni(f[7], 0) + " - Show more reads the next 100" : "") + "   -   rarity colour behind each icon, tier first");
}""")
# ITEM: d| (or d|id|gone), G| SkyyGear's name line, n| the description, g| the 9 fact lines, b| own / note / grace / buy
M(mtab, r"""
public void hvItem(@UCB@ b, @UEB@ ev, String[] ls) {
  String[] d = null;
  String[] bl = null;
  String bnote = "";
  String g = "";
  java.util.ArrayList ns = new java.util.ArrayList();
  String[] fx = new String[9];
  for (int i = 0; i < 9; i++) fx[i] = "";
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("d|")) d = sp(l, 13);
    else if (l.startsWith("G|")) g = l.substring(2);
    else if (l.startsWith("n|")) ns.add(l.substring(2));
    else if (l.startsWith("g|")) { String[] q = sp(l, 3); int k = q.length >= 3 ? ni(q[1], -1) : -1; if (k >= 0 && k < 9) fx[k] = q[2]; }
    else if (l.startsWith("b|note|")) { bl = new String[] { "b", "note" }; bnote = l.substring(7); }
    else if (l.startsWith("b|")) bl = sp(l, 5);
  }
  boolean live = d != null && d.length >= 13;
  this.hvBuyK = 0;
  this.hvBuyId = "";
  this.hvBuyP = -1L;
  if (!live) {
    b.set("#SkyyMtabHvIn.Text", "That listing is gone");
    b.set("#SkyyMtabHvIs.Text", "");
    b.set("#SkyyMtabHvIp.Text", "");
    b.set("#SkyyMtabHvIe.Text", "");
  } else {
    long qty = nl(d[4], 1L);
    long pr = nl(d[7], -1L);
    long ea = nl(d[8], -1L);
    long ends = nl(d[9], -1L);
    int tr = ni(d[5], 99);
    boolean sale = "1".equals(d[2]);
    hvSquare(b, "SkyyMtabHvIq", d[6]);
    b.set("#SkyyMtabHvIqI.Slots", @PKG@.InvPage.act(one(cell(d[3], (int) qty, d[12], htip(d[12], hexOf(d[6]), tr, qty, pr, ea, sale ? dur(ends) : "", g, "")))));
    b.set("#SkyyMtabHvIn.Text", @PKG@.MenuUtil.clip(d[12], 40));
    String t = tierT(tr);
    b.set("#SkyyMtabHvIs.Text", (t.length() > 0 ? t + "   -   " : "") + "x" + qty + (sale ? "   -   ends in " + dur(ends) : "   -   not for sale any more"));
    b.set("#SkyyMtabHvIp.Text", pr >= 0L ? money(pr) + " coins" : "");
    b.set("#SkyyMtabHvIe.Text", qty > 1L && ea >= 0L ? money(ea) + " coins each" : "");
  }
  b.set("#SkyyMtabHvIg.Text", @PKG@.MenuUtil.clip(g, 90));
  for (int i = 0; i < 9; i++) b.set("#SkyyMtabHvIf" + i + ".Text", @PKG@.MenuUtil.clip(fx[i], 110));
  for (int i = 0; i < @PKG@.MarketTabData.HVDN; i++) b.set("#SkyyMtabHvId" + i + ".Text", i < ns.size() ? @PKG@.MenuUtil.clip((String) ns.get(i), 110) : "");
  String note = "";
  String btn = "";
  String cf = "";
  if (bl != null && bl.length >= 2) {
    if (bl[1].equals("buy") && bl.length >= 5 && live) {
      this.hvBuyK = 1;
      this.hvBuyId = d[1];
      this.hvBuyP = nl(bl[2], -1L);
      boolean arm = "1".equals(bl[4]);
      this.hvArmed = this.hvArmed || arm;
      btn = arm ? "CONFIRM BUY" : "BUY NOW";
      cf = arm ? "Press CONFIRM BUY to buy it for " + money(this.hvBuyP) + " coins." : ("1".equals(bl[3]) ? "Over the confirm amount: the first press asks, the same press again buys." : "");
    } else if (bl[1].equals("own") && bl.length >= 5 && live) {
      this.hvBuyK = 2;
      this.hvBuyId = d[1];
      boolean arm = "1".equals(bl[4]);
      this.hvArmed = this.hvArmed || arm;
      btn = arm ? "YES, CANCEL IT" : "Cancel listing";
      cf = "Your listing - its fee of " + money(nl(bl[2], 0L)) + " coins is " + ("1".equals(bl[3]) ? "refunded" : "not refunded") + " if you cancel.";
    } else if (bl[1].equals("grace") && bl.length >= 3) note = "Just listed - it can be bought in " + ni(bl[2], 0) + " s.";
    else if (bl[1].equals("note")) note = bnote;
  }
  b.set("#SkyyMtabHvIb.Visible", this.hvBuyK > 0);
  b.set("#SkyyMtabHvIb.Text", btn);
  if (this.hvBuyK > 0) ev.addEventBinding(@BT@.Activating, "#SkyyMtabHvIb", @EVD@.of("a", "hvbuy").append("t", this.tok));
  b.set("#SkyyMtabHvIc.Text", cf);
  String[] nw = wrap2(note, 70);
  b.set("#SkyyMtabHvIo.Text", nw[0]);
  b.set("#SkyyMtabHvIo2.Text", nw[1]);
}""")
# CREATE BIN: u| durations, c0| (cells, default, min, max, the duration used), c| stacks, p| the pick, v| the price, l| x3 fee lines, z| numbers, w| ready
M(mtab, r"""
public void hvCreate(@UCB@ b, @UEB@ ev, String[] ls) {
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList cs = new java.util.ArrayList();
  String[] c0 = null;
  String[] p = null;
  String[] v = null;
  String[] z = null;
  String[] fl = new String[] { "", "", "" };
  int nf = 0;
  boolean w = false;
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("u|")) us.add(sp(l, 3));
    else if (l.startsWith("c0|")) c0 = sp(l, 6);
    else if (l.startsWith("c|")) { String[] c = sp(l, 10); if (c.length >= 10) cs.add(c); }
    else if (l.startsWith("p|1|")) p = sp(l, 6);
    else if (l.startsWith("p|")) p = sp(l, 3);
    else if (l.startsWith("v|")) v = sp(l, 3);
    else if (l.startsWith("l|")) { if (nf < 3) { fl[nf] = l.substring(2); nf = nf + 1; } }
    else if (l.startsWith("z|")) z = sp(l, 6);
    else if (l.startsWith("w|")) w = l.equals("w|1");
  }
  this.hvDurN = us.size();
  if (c0 != null && c0.length >= 6) this.hvDur = ni(c0[5], 0);   // c0|cells|default|min|max|the duration used
  b.set("#SkyyMtabHvCdv.Text", nameAt(us, this.hvDur));
  sortCells(cs);
  int n = @PKG@.MarketTabData.HVCN;
  this.hvCPages = (cs.size() + n - 1) / n;
  if (this.hvCPages < 1) this.hvCPages = 1;
  if (this.hvCPage >= this.hvCPages) this.hvCPage = this.hvCPages - 1;
  if (this.hvCPage < 0) this.hvCPage = 0;
  this.hvCs = new int[n];
  this.hvCl = new int[n];
  this.hvCg = new String[n];
  this.hvCo = new boolean[n];
  String pickCol = "";
  String pickName = "";
  for (int j = 0; j < cs.size(); j++) {
    String[] c = (String[]) cs.get(j);
    if (ni(c[1], -1) == this.hvSec && ni(c[2], -1) == this.hvSlot && c[3].equals(this.hvSig)) { pickCol = c[7]; pickName = c[9]; }
  }
  for (int i = 0; i < n; i++) {
    String r = "SkyyMtabHvJ" + i;
    int ix = this.hvCPage * n + i;
    this.hvCs[i] = -1;
    this.hvCl[i] = -1;
    this.hvCg[i] = "";
    this.hvCo[i] = false;
    if (ix >= cs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] c = (String[]) cs.get(ix);
    int sec = ni(c[1], -1);
    int slot = ni(c[2], -1);
    long qty = nl(c[5], 1L);
    int tr = ni(c[6], 99);
    boolean off = "1".equals(c[8]);
    this.hvCs[i] = sec;
    this.hvCl[i] = slot;
    this.hvCg[i] = c[3];
    this.hvCo[i] = !off;
    boolean picked = sec == this.hvSec && slot == this.hvSlot && c[3].equals(this.hvSig);
    hvSquare(b, r, c[7]);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", @PKG@.InvPage.act(one(cell(c[4], (int) qty, c[9], htip(c[9], hexOf(c[7]), tr, qty, -1L, -1L, "", "",
        off ? "This item cannot be listed on the Auction House" : "Pick: list this stack")))));
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(c[9], 34));
    String t = tierT(tr);
    b.set("#" + r + "S.Text", (t.length() > 0 ? t + "   -   " : "") + "x" + qty + (off ? "   -   cannot be listed" : ""));
    b.set("#" + r + "K.Visible", !off);
    b.set("#" + r + "K.Text", picked ? "Picked" : "Pick");
    if (!off) ev.addEventBinding(@BT@.Activating, "#" + r + "K", @EVD@.of("a", "hvp:" + i).append("t", this.tok));
  }
  b.set("#SkyyMtabHvJpg.Text", "Page " + (this.hvCPage + 1) + " / " + this.hvCPages);
  b.set("#SkyyMtabHvJp.Visible", this.hvCPages > 1);
  b.set("#SkyyMtabHvJn.Text", cs.size() == 0 ? "Nothing in your inventory to list." : cs.size() + " stacks - sorted by tier, then name.");
  boolean pk = p != null && p.length >= 6 && "1".equals(p[1]);
  this.hvPick = pk;
  b.set("#SkyyMtabHvCp.Visible", pk);
  if (pk) {
    long pq = nl(p[3], 1L);
    hvSquare(b, "SkyyMtabHvCpq", pickCol);
    b.set("#SkyyMtabHvCpqI.Slots", @PKG@.InvPage.act(one(cell(p[2], (int) pq, pickName.length() > 0 ? pickName : p[2], htip(pickName.length() > 0 ? pickName : p[2], hexOf(pickCol), 99, pq, -1L, -1L, "", p[5], "")))));
    b.set("#SkyyMtabHvCpn.Text", @PKG@.MenuUtil.clip(pickName.length() > 0 ? pickName : p[2], 40));
    b.set("#SkyyMtabHvCps.Text", @PKG@.MenuUtil.clip(p[5], 80));
    b.set("#SkyyMtabHvCpl.Text", @PKG@.MenuUtil.clip(p[4], 90));
  }
  b.set("#SkyyMtabHvCpw.Text", p != null && p.length >= 3 && "0".equals(p[1]) ? @PKG@.MenuUtil.clip(p[2], 90) : (this.hvSec < 0 ? "Pick a stack on the left." : ""));
  String tk = String.valueOf((char) 64) + "H4";
  b.set("#SkyyMtabHvCv.Value", this.hvPrice);
  this.hvPriceSeen = this.hvPrice;
  long vp = v != null && v.length >= 3 ? nl(v[1], -1L) : -1L;
  this.hvPriceOk = vp > 0L;
  this.hvPriceWhy = v != null && v.length >= 3 ? v[2] : "";
  b.set("#SkyyMtabHvCvw.Text", @PKG@.MenuUtil.clip(this.hvPriceWhy, 90));
  for (int i = 0; i < 3; i++) b.set("#SkyyMtabHvCf" + i + ".Text", @PKG@.MenuUtil.clip(fl[i], 100));
  b.set("#SkyyMtabHvCz.Text", z != null && z.length >= 6 ? "Fee now " + money(nl(z[3], 0L)) + " coins   -   if it sells: tax " + money(nl(z[4], 0L)) + ", you get " + money(nl(z[5], 0L)) : "");
  this.hvReady = w && pk && this.hvPriceOk;
  b.set("#SkyyMtabHvCgo.Text", this.hvReady ? "LIST IT" : "CREATE BIN");
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabHvCgo", @EVD@.of("a", "hvgo").append("t", this.tok).append(tk, "#SkyyMtabHvCv.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabHvCck", @EVD@.of("a", "hvchk").append(tk, "#SkyyMtabHvCv.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyMtabHvCv", @EVD@.of("a", "hvchk").append(tk, "#SkyyMtabHvCv.Value"), false);
  b.set("#SkyyMtabHvCn.Text", this.hvReady ? "The fee is checked - LIST IT lists it now. Buy It Now only, no bids."
      : "The first press checks the fee, the second lists it. Buy It Now only, no bids.");
}""")
# MANAGE: g| (used, max, claims, coins, items, claim-all armed, the summary), m| rows (the AH's order + button word), o| other profiles
M(mtab, r"""
public void hvManage(@UCB@ b, @UEB@ ev, String[] ls) {
  String[] g = null;
  String o = "";
  java.util.ArrayList ms = new java.util.ArrayList();
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("g|")) g = sp(l, 8);
    else if (l.startsWith("m|")) { String[] m = sp(l, 12); if (m.length >= 12) ms.add(m); }
    else if (l.startsWith("o|")) o = l.substring(2);
  }
  boolean go = g != null && g.length >= 8;
  long owed = go ? nl(g[3], 0L) + nl(g[5], 0L) : 0L;
  boolean armAll = go && "1".equals(g[6]);
  this.hvArmed = this.hvArmed || armAll;
  this.hvClaimAll = go && (ni(g[3], 0) > 0 || nl(g[4], 0L) > 0L || nl(g[5], 0L) > 0L);
  b.set("#SkyyMtabHvMs.Text", go ? @PKG@.MenuUtil.clip(g[7], 110) : "");
  b.set("#SkyyMtabHvMca.Visible", this.hvClaimAll);
  b.set("#SkyyMtabHvMca.Text", armAll ? "Yes, claim all" : "Claim all");
  if (this.hvClaimAll) ev.addEventBinding(@BT@.Activating, "#SkyyMtabHvMca", @EVD@.of("a", "hvca").append("t", this.tok));
  b.set("#SkyyMtabHvMo.Text", @PKG@.MenuUtil.clip(o, 120));
  int n = @PKG@.MarketTabData.HVMN;
  this.hvMPages = (ms.size() + n - 1) / n;
  if (this.hvMPages < 1) this.hvMPages = 1;
  if (this.hvMPage >= this.hvMPages) this.hvMPage = this.hvMPages - 1;
  if (this.hvMPage < 0) this.hvMPage = 0;
  this.hvMIds = new String[n];
  this.hvMKind = new String[n];
  this.hvMBtn = new boolean[n];
  for (int i = 0; i < n; i++) {
    String r = "SkyyMtabHvK" + i;
    int ix = this.hvMPage * n + i;
    this.hvMIds[i] = "";
    this.hvMKind[i] = "";
    this.hvMBtn[i] = false;
    if (ix >= ms.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] m = (String[]) ms.get(ix);
    long qty = nl(m[4], 1L);
    long pr = nl(m[7], -1L);
    int tr = ni(m[5], 99);
    boolean arm = "1".equals(m[8]);
    boolean bt = m[9].length() > 0 && !m[2].equals("ro");
    this.hvMIds[i] = m[1];
    this.hvMKind[i] = m[2];
    this.hvMBtn[i] = bt;
    this.hvArmed = this.hvArmed || arm;
    hvSquare(b, r, m[6]);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", @PKG@.InvPage.act(one(cell(m[3], (int) qty, m[11], htip(m[11], hexOf(m[6]), tr, qty, pr, -1L, "", m[10], "")))));
    String t = tierT(tr);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(m[11], 40) + (t.length() > 0 ? "    " + t : ""));
    b.set("#" + r + "S.Text", @PKG@.MenuUtil.clip(m[10], 110));
    b.set("#" + r + "P.Text", pr >= 0L ? money(pr) + " coins" : "");
    b.set("#" + r + "B.Visible", bt);
    if (bt) {
      b.set("#" + r + "B.Text", arm ? "Yes, cancel" : @PKG@.MenuUtil.clip(m[9], 16));
      ev.addEventBinding(@BT@.Activating, "#" + r + "B", @EVD@.of("a", "hvm:" + i).append("t", this.tok));
    }
  }
  b.set("#SkyyMtabHvKpg.Text", "Page " + (this.hvMPage + 1) + " / " + this.hvMPages);
  b.set("#SkyyMtabHvKp.Visible", this.hvMPages > 1);
  b.set("#SkyyMtabHvKn.Text", ms.size() == 0 ? "Nothing listed or waiting - Create BIN lists a stack." : (owed > 0L ? "Claim all collects everything that waits." : ""));
}""")
M(mtab, r"""
public void hvFail(@UCB@ b, String head) {
  b.set("#SkyyMtabHvH.Text", head);
  b.set("#SkyyMtabHvBr.Visible", false);
  b.set("#SkyyMtabHvIt.Visible", false);
  b.set("#SkyyMtabHvCr.Visible", false);
  b.set("#SkyyMtabHvMg.Visible", false);
  b.set("#SkyyMtabHvW.Text", "");
  b.set("#SkyyMtabHvBn.Text", "");
  b.set("#SkyyMtabHvNn.Visible", false);
  this.hvOk = false;
  this.hvArmed = false;
}""")
M(mtab, r"""
public void fillHv(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  this.hvArmed = false;
  this.hvClaimAll = false;
  this.hvBuyK = 0;
  this.hvRows = new String[0];
  this.hvCs = new int[0];
  this.hvCl = new int[0];
  this.hvCg = new String[0];
  this.hvCo = new boolean[0];
  this.hvMIds = new String[0];
  this.hvMKind = new String[0];
  this.hvMBtn = new boolean[0];
  int sel = this.hvMode == 2 ? 1 : (this.hvMode == 3 ? 2 : 0);
  for (int i = 0; i < 3; i++) {
    b.appendInline("#SkyyMtabHvMd", @PKG@.MarketTabData.SIDE.replace("{I}", "Hm" + i).replace("{S}", i == sel ? @PKG@.MarketTabData.ST_CATSEL : @PKG@.MarketTabData.ST_CAT));
    b.set("#SkyyMtabHm" + i + ".Text", @PKG@.MarketTabData.HMODE[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabHm" + i, @EVD@.of("a", "hm:" + i));
  }
  boolean has = @PKG@.InvCraft.fn("ah:fn:tab") != null && @PKG@.InvCraft.fn("ah:fn:tabact") != null;
  if (!has) {
    hvFail(b, @PKG@.InvCraft.fn("ah:fn:view") != null || @PKG@.InvCraft.fn("ah:fn:open") != null ? @PKG@.MarketTabData.HVOLD : @PKG@.MarketTabData.HVOFF);
    return;
  }
  String s = hvRead(u);
  this.hvLast = s;
  String[] ls = s == null ? new String[0] : s.split("\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? sp(ls[0], 15) : new String[0];
  if (h.length < 15) { hvFail(b, @PKG@.MarketTabData.HVFAIL); return; }
  this.hvOk = true;
  this.hvPk = h[1];
  this.hvTok = h[2];
  long purse = nl(h[4], -1L);
  int claims = ni(h[5], 0);
  b.set("#SkyyMtabHvH.Text", "");
  b.set("#SkyyMtabHvW.Text", (purse >= 0L ? "Purse " + money(purse) : (purse == -2L ? "No coin bank" : "Purse ?")) + "     Listings " + ni(h[8], 0) + " / " + ni(h[9], 0)
      + (claims > 0 ? "     " + claims + " to claim (Manage)" : ""));
  String bn = "";
  for (int i = 1; i < ls.length; i++) { if (ls[i].startsWith("B|")) bn = ls[i].substring(2); }
  b.set("#SkyyMtabHvBn.Text", @PKG@.MenuUtil.clip(bn, 130));
  b.set("#SkyyMtabHvBr.Visible", this.hvMode == 0);
  b.set("#SkyyMtabHvIt.Visible", this.hvMode == 1);
  b.set("#SkyyMtabHvCr.Visible", this.hvMode == 2);
  b.set("#SkyyMtabHvMg.Visible", this.hvMode == 3);
  if (this.hvMode == 1) hvItem(b, ev, ls);
  else if (this.hvMode == 2) hvCreate(b, ev, ls);
  else if (this.hvMode == 3) hvManage(b, ev, ls);
  else hvBrowse(b, ev, ls);
  b.set("#SkyyMtabHvNn.Visible", this.hvArmed);
  if (this.hvArmed) ev.addEventBinding(@BT@.Activating, "#SkyyMtabHvNn", @EVD@.of("a", "hvno").append("t", this.tok));
}""")
'''
P.rep('''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;''', HV_JAVA + '''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;''')
P.rep('''  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : 'H');''',
      '''  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : (this.view == 3 ? 'U' : 'H'));   // 0.3.73: + U (the Auction House)''')
P.rep('''    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.MVCAP);
    return;
  }''', '''    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.MVCAP);
    return;
  }
  if (this.view == 3) {   // 0.3.73 (oldmenu5): the Auction House view reads SkyyAuctions only
    try { fillHv(b, ev); } catch (Throwable t) { this.hvOk = false; this.hvRows = new String[0]; this.hvMIds = new String[0]; this.hvBuyK = 0; @PKG@.MenuUtil.warn("market screen: the auction view failed: " + t); }
    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.HVCAP);
    return;
  }''')
P.rep('''public static int viewOf(String a) {
  if (a.startsWith("ov") || a.startsWith("oc:")) return 1;
  if (a.startsWith("mk:") || a.startsWith("mz:") || a.startsWith("mb:") || a.startsWith("mpg:") || a.equals("mrf")) return 2;
  if (a.equals("claim")) return 3;''', '''public static int viewOf(String a) {
  if (a.startsWith("ov") || a.startsWith("oc:")) return 1;
  if (a.startsWith("mk:") || a.startsWith("mz:") || a.startsWith("mb:") || a.startsWith("mpg:") || a.equals("mrf")) return 2;
  if (a.startsWith("hv") || a.startsWith("hm:")) return 3;   // 0.3.73: the Auction House view
  if (a.equals("claim")) return 4;                            // the Bazaar's Claim all: the cards or the orders view''')
P.rep('''  this.view = v < 0 || v > 2 ? 0 : v;''', '''  this.view = v < 0 || v > 3 ? 0 : v;   // 0.3.73: + 3 the Auction House''')
P.rep('''    if (need >= 0 && !(need == this.view || (need == 3 && this.view <= 1))) { say("That button is not on this page - nothing changed"); return; }''',
      '''    if (need >= 0 && !(need == this.view || (need == 4 && this.view <= 1))) { say("That button is not on this page - nothing changed"); return; }
    int hm = hvModeOf(a);   // 0.3.73: an Auction House button meant for another mode (a forged event) = a caption, no call
    if (hm >= 0 && hm != this.hvMode) { say("That button is not on this page - nothing changed"); return; }''')

HV_ACT = r'''# ---- 0.3.73 (oldmenu5): the Auction House view's actions. ah:fn:tabact (AhTabFn mode 1) with the read's profile key + token; ONE packet each
M(mtab, r"""
public static int hvModeOf(String a) {
  if (a.startsWith("hvv:")) return 0;
  if (a.equals("hvbuy")) return 1;
  if (a.startsWith("hvp:") || a.equals("hvgo") || a.startsWith("hvd:") || a.equals("hvchk") || a.startsWith("hvjpg:")) return 2;
  if (a.startsWith("hvm:") || a.equals("hvca") || a.startsWith("hvkpg:")) return 3;
  return -1;
}""")
# a typed search / level: no control characters, quotes, backslashes or '|'
M(mtab, r"""
public static String hvText(String s, int max) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < max; i++) {
    char c = s.charAt(i);
    if (c < 32 || c == 127 || c == 34 || c == 92 || c == '|') continue;
    sb.append(c);
  }
  return sb.toString().trim();
}""")
M(mtab, r"""
public static int cyc(int cur, int d, int n) {
  if (n <= 0) return cur;
  int x = (cur + (d < 0 ? -1 : 1)) % n;
  if (x < 0) x = x + n;
  return x;
}""")
M(mtab, r"""
public void hvAct(String op, String arg) {
  this.answered = true;
  if (!this.hvOk) { say("The Auction House is not ready - nothing changed"); return; }
  Object o = call("ah:fn:tabact", new Object[] { this.playerRef.getUuid(), this.hvPk, this.hvTok, op, arg == null ? "" : arg });
  if (o == null) { say(@PKG@.InvCraft.fn("ah:fn:tabact") == null ? "The Auction House is not on this server right now - nothing changed" : "That could not run here - nothing changed"); return; }
  String r = String.valueOf(o).trim();
  if (r.startsWith("+") && op.equals("create")) { this.hvSec = -1; this.hvSlot = -1; this.hvSig = ""; this.hvPrice = ""; }   // listed: a second press cannot repeat it
  this.tcap = @PKG@.InvPage.bare(r);
  redraw();
}""")
# View: the drawn row's listing id -> the item mode (a read)
M(mtab, r"""
public void hvOpen(int k) {
  this.answered = true;
  if (k < 0 || k >= this.hvRows.length || this.hvRows[k] == null || this.hvRows[k].length() == 0) { say("Nothing there"); return; }
  this.hvId = this.hvRows[k];
  this.hvMode = 1;
  this.tcap = "";
  redraw();
}""")
# BUY NOW / Cancel listing: the listing id + the price DRAWN (b|buy); the AH asks at its confirm amount, the same press again buys
M(mtab, r"""
public void hvBuy() {
  this.answered = true;
  if (this.hvBuyK == 1 && this.hvBuyId.length() > 0 && this.hvBuyP >= 0L) { hvAct("buy", this.hvBuyId + "|" + this.hvBuyP); return; }
  if (this.hvBuyK == 2 && this.hvBuyId.length() > 0) { hvAct("cancel", this.hvBuyId); return; }
  say("Nothing to buy there");
}""")
# Pick: the drawn stack (section, slot, sig) - read again with it, nothing sent to tabact
M(mtab, r"""
public void hvPickAt(int k) {
  this.answered = true;
  if (k < 0 || k >= this.hvCs.length || this.hvCg[k] == null || this.hvCg[k].length() == 0) { say("Nothing there"); return; }
  if (!this.hvCo[k]) { say("That item cannot be listed on the Auction House"); return; }
  this.hvSec = this.hvCs[k];
  this.hvSlot = this.hvCl[k];
  this.hvSig = this.hvCg[k];
  this.tcap = "";
  redraw();
}""")
# CREATE BIN / LIST IT: the stack, price and duration of the read DRAWN; a price typed after that drawing = checked first (nothing sent)
M(mtab, r"""
public void hvGo(String typed) {
  this.answered = true;
  if (!this.hvOk) { say("The Auction House is not ready - nothing changed"); return; }
  String tp = amtClean(typed);
  if (!tp.equals(this.hvPriceSeen)) { this.hvPrice = tp; this.tcap = @PKG@.MarketTabData.HVCHK; redraw(); return; }
  if (this.hvSec < 0 || !this.hvPick) { say("Pick a stack on the left first"); return; }
  if (!this.hvPriceOk) { say(this.hvPriceWhy.length() > 0 ? this.hvPriceWhy : "Type a price first"); return; }
  hvAct("create", this.hvSec + "|" + this.hvSlot + "|" + this.hvSig + "|" + this.hvPriceSeen + "|" + this.hvDur);
}""")
# a Manage row's button: Cancel (an active listing, two presses) or Claim (coins / sold item / bought item)
M(mtab, r"""
public void hvMRow(int k) {
  this.answered = true;
  if (k < 0 || k >= this.hvMIds.length || this.hvMIds[k] == null || this.hvMIds[k].length() == 0 || !this.hvMBtn[k]) { say("Nothing there"); return; }
  String kd = this.hvMKind[k];
  if (kd.equals("active")) { hvAct("cancel", this.hvMIds[k]); return; }
  if (kd.equals("coins") || kd.equals("sitem") || kd.equals("bitem")) { hvAct("claim", this.hvMIds[k]); return; }
  say("Nothing to do there");
}""")
'''
P.rep('''M(mtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', HV_ACT + '''M(mtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''    if (a.equals("mer")) { goView(2); return; }''', '''    if (a.equals("mer")) { goView(2); return; }
    // 0.3.73 (oldmenu5): the Auction House view's non-trading buttons (modes, filters, search, pages, duration, the price check)
    String hk = String.valueOf((char) 64);
    if (a.startsWith("hm:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), 0);
      this.hvMode = k == 1 ? 2 : (k == 2 ? 3 : 0);
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("hvc:") || a.startsWith("hvs:") || a.startsWith("hvr:")) {
      int dd = @PKG@.InvPage.toInt(a.substring(4), 0);
      if (a.startsWith("hvc:")) this.hvCat = cyc(this.hvCat, dd, this.hvCatN);
      else if (a.startsWith("hvs:")) this.hvSort = cyc(this.hvSort, dd, this.hvSortN);
      else this.hvRar = cyc(this.hvRar, dd, this.hvRarN);
      this.hvPage = 0;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("hvq")) {
      this.hvQ = hvText(@PKG@.InvPage.val(d, hk + "H1"), 40);
      this.hvLa = hvText(@PKG@.InvPage.val(d, hk + "H2"), 8);
      this.hvLb = hvText(@PKG@.InvPage.val(d, hk + "H3"), 8);
      this.hvPage = 0;
      this.hvMax = 100;
      this.hvMode = 0;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("hvclr")) { this.hvCat = 0; this.hvSort = 0; this.hvRar = 0; this.hvQ = ""; this.hvLa = ""; this.hvLb = ""; this.hvPage = 0; this.hvMax = 100; this.tcap = ""; redraw(); return; }
    if (a.equals("hvrf")) { this.tcap = ""; redraw(); return; }
    if (a.equals("hvmore")) { this.hvMax = this.hvMax + 100 > 1000 ? 1000 : this.hvMax + 100; this.tcap = ""; redraw(); return; }
    if (a.startsWith("hvpg:") || a.startsWith("hvjpg:") || a.startsWith("hvkpg:")) {
      int kind = a.startsWith("hvpg:") ? 0 : (a.startsWith("hvjpg:") ? 1 : 2);
      int dh = @PKG@.InvPage.toInt(a.substring(kind == 0 ? 5 : 6), 0);
      int cur = kind == 0 ? this.hvPage : (kind == 1 ? this.hvCPage : this.hvMPage);
      int max = kind == 0 ? this.hvPages : (kind == 1 ? this.hvCPages : this.hvMPages);
      int nh = cur + (dh < 0 ? -1 : 1);
      if (nh < 0 || nh >= max) { say(nh < 0 ? "This is the first page" : "This is the last page"); return; }
      if (kind == 0) this.hvPage = nh; else if (kind == 1) this.hvCPage = nh; else this.hvMPage = nh;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("hvd:")) { this.hvDur = cyc(this.hvDur < 0 ? 0 : this.hvDur, @PKG@.InvPage.toInt(a.substring(4), 0), this.hvDurN); this.tcap = ""; redraw(); return; }
    if (a.equals("hvchk")) { this.hvPrice = amtClean(@PKG@.InvPage.val(d, hk + "H4")); this.tcap = ""; redraw(); return; }''')
P.rep('''    if (a.startsWith("mb:")) { mBuy(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }''',
      '''    if (a.startsWith("mb:")) { mBuy(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    // 0.3.73 (oldmenu5): the Auction House view's token actions (View, Buy now / Cancel listing, Pick, Create BIN / List it, Manage, Claim all, Not now)
    if (a.startsWith("hvv:")) { hvOpen(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("hvbuy")) { hvBuy(); return; }
    if (a.startsWith("hvp:")) { hvPickAt(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("hvgo")) { hvGo(@PKG@.InvPage.val(d, hk + "H4")); return; }
    if (a.startsWith("hvm:")) { hvMRow(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("hvca")) { if (!this.hvClaimAll) { say("Nothing to claim"); return; } hvAct("claimall", ""); return; }
    if (a.equals("hvno")) { if (!this.hvArmed) { say("Nothing is waiting for a second press"); return; } hvAct("no", ""); return; }''')
# the home card: Browse all / New listing / Your listings + an auction row's Open = the Auction House view (no old page)
P.rep('''    if (a.startsWith("ah:")) {
      String v = a.substring(3);
      if (!(v.equals("browse") || v.equals("create") || v.equals("manage"))) { say("Pick an Auction House button"); return; }
      opener("ah:fn:view", new Object[] { this.playerRef.getUuid(), v }, "market", "auctions", "the Auction House");
      return;
    }''', '''    if (a.startsWith("ah:")) {   // 0.3.73 (oldmenu5): Browse all / New listing / Your listings = the Auction House view (no old page)
      String v = a.substring(3);
      if (!(v.equals("browse") || v.equals("create") || v.equals("manage"))) { say("Pick an Auction House button"); return; }
      this.hvMode = v.equals("create") ? 2 : (v.equals("manage") ? 3 : 0);
      goView(3);
      return;
    }''')
P.rep('''    if (a.startsWith("ahr:")) {
      int k = @PKG@.InvPage.toInt(a.substring(4), -1);
      if (k < 0 || k >= this.ahQ.length) { say("Nothing there"); return; }
      opener("ah:fn:open", new Object[] { this.playerRef.getUuid(), this.ahQ[k] }, "market", "auctions", "the Auction House");
      return;
    }''', '''    if (a.startsWith("ahr:")) {   // 0.3.73: an auction row's Open = the Auction House view searching for that item (its drawn name)
      int k = @PKG@.InvPage.toInt(a.substring(4), -1);
      if (k < 0 || k >= this.ahQ.length) { say("Nothing there"); return; }
      this.hvQ = hvText(this.ahQ[k], 40);
      this.hvCat = 0;
      this.hvRar = 0;
      this.hvLa = "";
      this.hvLb = "";
      this.hvPage = 0;
      this.hvMax = 100;
      this.hvMode = 0;
      goView(3);
      return;
    }''')

# ======================================================================= the ratchet: OLD_LEFT shrinks by the two rows this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"),
    ("market", "auctions"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"), ("social", "guild"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.73 (oldmenu5): social:guild (Manage guild = the guild view - SkyyGuilds 0.1.14 guild:fn:act) and market:auctions (the AH card's buttons + Open =
# the Auction House view - SkyyAuctions 0.1.18 ah:fn:tab / tabact; no opener(...) link left) are gone.
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"),
    ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.73: no system / command / class"
_i = P.s.index
assert _i("public String gact(String op, String arg)") < _i("public void gvMembers(") < _i("public void gvBank(") < _i("public void gvLog(") \
    < _i("public void fillGv(@UCB@ b, @UEB@ ev)") < _i('''  char cur = this.view == 1 ? 'S' : ''') < _i("public void gvDo(String op, String arg)") \
    < _i("public void gvRow(String op, String a, int cut, int bit)") < _i('if (a.startsWith("gm:lead:")) { gvRow('), "0.3.73: the guild methods before their callers"
assert _i("public static String ahSq(String c)") < _i("public static void sortCells(") < _i("public String hvRead(java.util.UUID u)") < _i("public void hvBrowse(") \
    < _i("public void hvManage(") < _i("public void fillHv(@UCB@ b, @UEB@ ev)") < _i("  if (this.view == 3) {   // 0.3.73 (oldmenu5): the Auction House view") \
    < _i("public static String amtClean(String s)") < _i("public static int hvModeOf(String a)") < _i("public void hvAct(String op, String arg)") \
    < _i("public void hvGo(String typed)") < _i("int hm = hvModeOf(a);") < _i('if (a.equals("hvgo")) { hvGo('), "0.3.73: the auction methods before their callers"
assert _i("public static String hexOf(String s)") < _i("public static String ahSq(String c)") and _i("public static String[] wrap2(String s, int n)") < _i("public void hvItem("), \
    "0.3.73: the 0.3.72 helpers before the auction view"
assert 'hub("social", "guild"' not in P.s and 'opener("ah:fn:' not in P.s and '"the Guild page"' not in P.s and "more on the Guild page" not in P.s, \
    "0.3.73: no old Guild / Auction House page link left in the new screens"
P.finish()


# ======================================================================= the HARNESS (every 0.3.72 check runs again on the 0.3.73 jar, plus OLD5)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


EXPECT_73 = '''EXPECT = {   # 0.3.73: the Social tab's guild view + the Market tab's Auction House view, the version strings
@@EXPECT@@
}
'''
HARNESS_OLD5_STATIC = r'''    # ---- OLD5 (0.3.73; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the ratchet shrank by exactly the two rows this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("social", "guild"), ("market", "auctions")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 2,
            "OLD5 RATCHET OLD_LEFT lost social:guild + market:auctions, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('hub("social", "guild"' not in g and 'opener("ah:fn:' not in g and '"Guild page"' not in g and "more on the Guild page" not in g
            and "The Guild page makes one" not in g and 'G_.glass_button(SC + "Gpage", "Manage guild"' in g
            and "0.3.73: the guild view fits" in g,
            "OLD5 STATIC no Guild page / Auction House page link or text pointing at one (Manage guild + the AH card = the views)")
    K.check('call("guild:fn:act", new Object[] { op, this.playerRef.getUuid(), this.gTok, this.gPk, arg })' in g
            and 'call("ah:fn:tabact", new Object[] { this.playerRef.getUuid(), this.hvPk, this.hvTok, op, arg == null ? "" : arg })' in g
            and 'call("ah:fn:tab", new Object[] { u, vw, Integer.valueOf(this.hvCat),' in g
            and 'hvAct("buy", this.hvBuyId + "|" + this.hvBuyP);' in g and 'hvAct("create", this.hvSec + "|" + this.hvSlot + "|" + this.hvSig + "|" + this.hvPriceSeen + "|" + this.hvDur);' in g,
            "OLD5 STATIC the views call the bridges: guild:fn:act (the read's token + profile key), ah:fn:tab, ah:fn:tabact buy (the drawn price) / create (the drawn read)")
    K.check("0.3.73: the guild view fits" in g and "0.3.73: the members tab fits" in g and "0.3.73: the bank tab fits" in g and "0.3.73: the log tab fits" in g
            and "0.3.73: the auction view fits" in g and "0.3.73: the browse rows fit" in g and "0.3.73: the stacks fit" in g and "0.3.73: the manage rows fit" in g
            and "0.3.73: the view markups are proven" in g and "0.3.73: a guild run-time id is also a static id" in g,
            "OLD5 STATIC the build asserts every new view fits 1080, its run-time markup is proven, its run-time ids are not static ids")
'''
HARNESS_OLD5_AH = r'''    # ---- OLD5 AH (0.3.73, round oldmenu5): THE MARKET TAB'S AUCTION HOUSE VIEW (ah:fn:tab / tabact stand-ins = tools/auctions_0_1_18_patch.py's contract)
    p_ = mt_ev({"a": "ah:browse"}, "OLD5 AH Browse all without SkyyAuctions 0.1.18")
    cm = cmap(p_)
    K.check(int(MS.view) == 3 and int(MS.hvMode) == 0 and has4(p_, "SkyyMtabHv") and not has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabOv") and not has4(p_, "SkyyMtabMv")
            and txt4(cm, "HvH") == str(MTD.HVOLD) and not vis3(cm, "HvBr") and not vis3(cm, "HvMg") and not sel_ok4(p_) and cap3(p_) == str(MTD.HVCAP),
            "OLD5 AH FALL Browse all with SkyyAuctions 0.1.17 (no ah:fn:tab) = the view names 0.1.18; no old page opened %s" % sel_ok4(p_)[:3])
    SORTS = ["Tier then name", "Price low-high", "Price high-low", "Ending soonest", "Newest listed"]
    CATS = ["All", "Weapons", "Armor", "Tools", "Accessories", "Materials", "Consumables", "Other"]
    RARS = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
    AHR = [("L1", "Weapon_Sword_Iron", 1, 3, "#2770b7", 400, 400, 3600000, "1h 0m", 0, 0, 0, "Bravo", "Iron sword, Lv 12", "Iron Sword"),
           ("L2", "Rock_Stone", 64, 1, "#c9d2dd", 120000, 1875, 600000, "10m", 0, 0, 0, "Bravo", "", "Fine Stone"),
           ("L3", "Wood_Oak_Trunk", 16, 1, "#c9d2dd", 800, 50, 7200000, "2h 0m", 1, 0, 0, "SkyyCraftA", "", "Oak Log"),
           ("L4", "Plant_Fruit_Apple", 5, 99, "red); Background: (TexturePath: x", 50, 10, 60000, "1m", 2, 1, 30, "SkyyCraftA", "", "Apple")] + \
          [("F%d" % i_, "Weapon_Fake_%d" % i_, 1, 6, "#bb8a2c", 150000 + i_, 150000 + i_, 9000000, "2h 30m", 0, 0, 0, "Charlie", "", "Blade %02d" % i_) for i_ in range(8)]
    AH = {"pk": "prof-A", "tok": 0, "reads": [], "acts": [], "null": False, "anull": False, "moment": False, "arm": None, "prev": None, "purse": 500000,
          "gone": set(), "bought": [], "cancelled": [], "claimed": [], "listed": [], "owed": 60000, "banner": "",
          "cells": [(0, 3, "s~A", "Weapon_Sword_Iron", 1, 3, "#2770b7", 0, "Iron Sword"), (0, 5, "s~B", "Rock_Stone", 30, 1, "#c9d2dd", 0, "Stone"),
                    (1, 0, "s~C", "Skyy_Bound", 1, 99, "#bb8a2c", 1, "Bound Charm"), (0, 1, "s~D", "Wood_Oak_Trunk", 16, 1, "#c9d2dd", 0, "Oak Log")],
          "manage": [("M1", "coins", "Weapon_Sword_Iron", 1, 3, "#2770b7", 60000, "Claim coins", "Sold to Bravo - 58,800 coins (tax 1,200)", "Iron Sword"),
                     ("M2", "active", "Wood_Oak_Trunk", 16, 1, "#c9d2dd", 800, "Cancel", "For sale - ends in 2h", "Oak Log"),
                     ("M3", "ro", "Rock_Stone", 1, 1, "#c9d2dd", 5, "", "Expired - already claimed", "Stone"),
                     ("M4", "bitem", "Plant_Fruit_Apple", 5, 99, "#c9d2dd", 50, "Claim item", "Bought from Bravo - waiting for inventory room", "Apple")]}

    def f_ahtab(o):
        a = [None if x_ is None else str(x_) for x_ in list(o)]
        AH["reads"].append(a)
        if AH["null"]:
            return None
        AH["tok"] += 1
        vw = a[1]
        claims = [m_ for m_ in AH["manage"] if m_[1] in ("coins", "sitem", "bitem")]
        used = len([m_ for m_ in AH["manage"] if m_[1] == "active"]) + 1
        L = ["h|%s|%d|%s|%d|%d|%d|%d|%d|20|10|100000|50000|1|Main" % (AH["pk"], AH["tok"], vw, AH["purse"], len(claims), AH["owed"], 1, used), "B|" + AH["banner"]]
        if vw == "browse":
            cat, so, ra = int(a[2]), int(a[3]), int(a[4])
            cat = cat if 0 <= cat < len(CATS) else 0
            so = so if 0 <= so < len(SORTS) else 0
            ra = ra if 0 <= ra <= len(RARS) else 0
            q = (a[5] or "").lower()[:40]
            L += ["k|%d|%s" % (i_, n_) for i_, n_ in enumerate(CATS)] + ["s|%d|%s" % (i_, n_) for i_, n_ in enumerate(SORTS)]
            L += ["t|0|Any"] + ["t|%d|%s" % (i_ + 1, n_) for i_, n_ in enumerate(RARS)]
            rows = [r_ for r_ in AHR if r_[0] not in AH["gone"] and (cat == 0 or (cat == 1 and r_[1].startswith("Weapon"))) and (ra == 0 or r_[3] == ra) and q in r_[14].lower()]
            mx = int(a[8])
            L.append("f|%d|%d|%d|%s|%s|1|%d|%d|%s - %s" % (cat, so, ra, a[6] or "", a[7] or "", len(rows), min(mx, len(rows)), CATS[cat], SORTS[so]))
            if (a[6] or "") and not (a[6] or "").isdigit():
                L.append("x|Level min must be a whole number - it is ignored.")
            if not rows:
                L.append("e|No listings match - try fewer filters.")
            for r_ in rows[:mx]:
                L.append("r|" + "|".join(str(x_) for x_ in r_))
        elif vw == "item":
            lid = a[9]
            hit = [x_ for x_ in AHR if x_[0] == lid and lid not in AH["gone"]]
            if not hit:
                L += ["d|%s|gone" % lid, "b|note|That listing is gone - sold, cancelled or ended."]
            else:
                r_ = hit[0]
                L.append("d|%s|1|%s|%d|%d|%s|%d|%d|%d|%d|%d|%s" % (r_[0], r_[1], r_[2], r_[3], r_[4], r_[5], r_[6], r_[7], r_[11], 1 if r_[9] == 1 else 0, r_[14]))
                L += ["n|A plain item.", "n|It does one thing well."] + ["g|%d|Fact %d of %s" % (i_, i_, r_[14]) for i_ in range(9)]
                if r_[9] == 1:
                    L.append("b|own|25|1|%d" % (1 if AH["arm"] == ("cancel", r_[0]) else 0))
                elif r_[9] == 2:
                    L.append("b|note|That is your other profile's listing - it cannot buy it.")
                elif r_[11] > 0:
                    L.append("b|grace|%d" % r_[11])
                else:
                    L.append("b|buy|%d|%d|%d" % (r_[5], 1 if r_[5] >= 100000 else 0, 1 if AH["arm"] == ("buy", "%s|%d" % (r_[0], r_[5])) else 0))
        elif vw == "create":
            durs = ["1h", "6h", "12h", "24h", "48h"]
            dd = int(a[14])
            dd = dd if 0 <= dd < len(durs) else 3
            L += ["u|%d|%s" % (i_, d_) for i_, d_ in enumerate(durs)] + ["c0|%d|3|10|1000000000|%d" % (len(AH["cells"]), dd)]
            for c_ in AH["cells"]:
                L.append("c|" + "|".join(str(x_) for x_ in c_))
            sec, slot, sig = int(a[10]), int(a[11]), a[12] or ""
            if sec >= 0:
                hit = [c_ for c_ in AH["cells"] if c_[0] == sec and c_[1] == slot and c_[2] == sig]
                if not hit:
                    L.append("p|0|That slot changed - pick again.")
                elif hit[0][7] == 1:
                    L.append("p|0|That item cannot be sold here.")
                else:
                    L.append("p|1|%s|%d|Lowest BIN now: 900 coins|x%d - Common" % (hit[0][3], hit[0][4], hit[0][4]))
            pt = (a[13] or "").strip()[:16]
            v_ = int(pt) if pt.isdigit() else -1
            why = "" if pt.isdigit() and v_ >= 10 else ("Type a price." if not pt else ("The price must be at least 10 coins." if pt.isdigit() else "That is not a price."))
            vp = v_ if not why else -1
            L.append("v|%d|%s" % (vp, why))
            L += ["l|Listing fee: 1%% of the price", "l|Duration fee for %s: 10 coins" % durs[dd], "l|Tax if it sells: 2%"]
            if vp > 0:
                L.append("z|%d|10|%d|%d|%d" % (vp // 100, vp // 100 + 10, vp // 50, vp - vp // 50))
            L.append("w|%d" % (1 if vp > 0 and AH["prev"] == (sec, slot, sig, vp, dd) else 0))
        else:
            L.append("g|%d|20|%d|%d|0|%d|%d of 20 listings used. %s coins to claim." % (used, len(claims), AH["owed"], 1 if AH["arm"] == ("claimall",) else 0, used, "{:,}".format(AH["owed"])))
            for m_ in AH["manage"]:
                L.append("m|%s|%s|%s|%d|%d|%s|%d|%d|%s|%s|%s" % (m_[0], m_[1], m_[2], m_[3], m_[4], m_[5], m_[6], 1 if AH["arm"] == ("cancel", m_[0]) else 0, m_[7], m_[8], m_[9]))
            L.append("o|Your other profiles have nothing waiting.")
        return "\n".join(L)

    def f_ahact(o):
        a = [None if x_ is None else str(x_) for x_ in list(o)]
        AH["acts"].append(a)
        if AH["anull"]:
            return None
        if a[1] != AH["pk"]:
            AH["arm"] = None
            return "=Your profile changed - here is this profile's Auction House. Nothing changed."
        if a[2] != str(AH["tok"]):
            return "=The Auction House changed - look again. Nothing changed."
        if AH["moment"]:
            AH["moment"] = False
            return "=One moment."
        op, arg = a[3], a[4] or ""
        was = AH["arm"]
        AH["arm"] = None
        if op == "buy":
            g_ = arg.split("|")
            hit = [x_ for x_ in AHR if x_[0] == g_[0] and g_[0] not in AH["gone"]]
            if not hit:
                return "-That listing is gone."
            if str(hit[0][5]) != g_[1]:
                return "-The price is not the one you saw - look again."
            if hit[0][5] >= 100000 and was != ("buy", arg):
                AH["arm"] = ("buy", arg)
                return "=Confirm the purchase within 10 s."
            AH["purse"] -= hit[0][5]
            AH["gone"].add(g_[0])
            AH["bought"].append(g_[0])
            return "+You bought %s for %d coins." % (hit[0][14], hit[0][5])
        if op == "cancel":
            ids = [m_[0] for m_ in AH["manage"] if m_[1] == "active"] + [x_[0] for x_ in AHR if x_[9] == 1 and x_[0] not in AH["gone"]]
            if arg not in ids:
                return "-That listing is not yours or is gone."
            if was != ("cancel", arg):
                AH["arm"] = ("cancel", arg)
                return "=Cancel it? The fee is refunded - click Yes, cancel within 10 s."
            AH["cancelled"].append(arg)
            AH["gone"].add(arg)
            AH["manage"] = [m_ for m_ in AH["manage"] if m_[0] != arg]
            return "+Cancelled - the items are back in your inventory."
        if op == "claim":
            hit = [m_ for m_ in AH["manage"] if m_[0] == arg and m_[1] in ("coins", "sitem", "bitem")]
            if not hit:
                return "-Nothing to claim there."
            AH["manage"].remove(hit[0])
            AH["claimed"].append(arg)
            return "+Claimed %s." % hit[0][9]
        if op == "claimall":
            if AH["owed"] >= 50000 and was != ("claimall",):
                AH["arm"] = ("claimall",)
                return "=Claim everything (%s coins)? Click Yes, claim all within 10 s." % "{:,}".format(AH["owed"])
            AH["owed"] = 0
            AH["manage"] = [m_ for m_ in AH["manage"] if m_[1] not in ("coins", "sitem", "bitem")]
            AH["claimed"].append("all")
            return "+Claimed everything."
        if op == "create":
            g_ = arg.split("|")
            if len(g_) != 5:
                return "-Unknown Auction House action."
            key = (int(g_[0]), int(g_[1]), g_[2], int(g_[3]) if g_[3].isdigit() else -1, int(g_[4]))
            if AH["prev"] != key:
                AH["prev"] = key
                return "=Check the fee above, then click Create BIN again."
            AH["prev"] = None
            AH["listed"].append(key)
            AH["cells"] = [c_ for c_ in AH["cells"] if not (c_[0] == key[0] and c_[1] == key[1])]
            return "+Listed for %d coins." % key[3]
        if op == "no":
            return "=Nothing done."
        return "-Unknown Auction House action."
    BR.put("ah:fn:tab", Fn(f_ahtab))
    BR.put("ah:fn:tabact", Fn(f_ahact))
    # ======== BROWSE
    p_ = mt_ev({"a": "hvrf"}, "OLD5 AH Browse with SkyyAuctions 0.1.18")
    cm = cmap(p_)
    K.check(AH["reads"][-1][:9] == [uk3, "browse", "0", "0", "0", "", "", "", "100"] and txt4(cm, "HvH") == "" and vis3(cm, "HvBr") and not vis3(cm, "HvIt")
            and not vis3(cm, "HvCr") and not vis3(cm, "HvMg") and [txt4(cm, k_) for k_ in ("HvFcv", "HvFsv", "HvFrv")] == ["All", "Tier then name", "Any"]
            and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabHm0") and str(MTD.ST_CAT) in mk_of(p_, "SkyyMtabHm1") and txt4(cm, "Hm1") == "Create BIN"
            and "Purse 500,000" in txt4(cm, "HvW") and "Listings 2 / 20" in txt4(cm, "HvW") and not vis3(cm, "HvNn") and not sel_ok4(p_),
            "OLD5 AH BROWSE the read: browse, the AH's own filters (category / sort / rarity names), 100 rows; Browse selected; purse + listings %s" % sel_ok4(p_)[:3])
    K.check([txt4(cm, "HvR%dN" % k_) for k_ in range(4)] == ["Iron Sword", "Fine Stone", "Oak Log", "Apple"] and txt4(cm, "HvR0P") == "400 coins"
            and txt4(cm, "HvR0S").startswith("T3   -   x1   -   400 each   -   ends in 1h 0m   -   by Bravo") and "yours" in txt4(cm, "HvR2S")
            and "your other profile" in txt4(cm, "HvR3S") and "off the market" in txt4(cm, "HvR3S") and "for sale in 30 s" in txt4(cm, "HvR3S")
            and not txt4(cm, "HvR3S").startswith("T") and vis3(cm, "HvR8") and txt4(cm, "HvPg") == "Page 1 / 2" and vis3(cm, "HvP") and not vis3(cm, "HvMore")
            and len(bind4(p_, "hvv:0")) == 1 and '"t"' in bind4(p_, "hvv:0")[0][2].replace(" ", ""),
            "OLD5 AH BROWSE rows in the AH's order: name, T + qty + each + ends + seller (yours / your other profile), off the market, grace, price, View (with the token)")
    sq0_, sq3_ = appended4(p_, "SkyyMtabHvR0Bg"), appended4(p_, "SkyyMtabHvR3Bg")
    K.check(len(sq0_) == 1 and "Background: #2770b7(0.4);" in sq0_[0] and sq3_ == [] and "#2770b7" in cm.get("#SkyyMtabHvR0I.Slots", "") and "T3" in cm.get("#SkyyMtabHvR0I.Slots", "")
            and "TexturePath: x" not in str([str(c_.text or "") for c_ in cmds_of(p_)]),
            "OLD5 AH BROWSE rarity: the square behind the icon + the name colour in the tooltip (Iron Sword #2770b7); a bad colour never reaches the markup")
    p_ = mt_ev({"a": "hvpg:1"}, "OLD5 AH next page")
    K.check([txt4(cmap(p_), "HvR%dN" % k_) for k_ in range(3)] == ["Blade 05", "Blade 06", "Blade 07"] and not vis3(cmap(p_), "HvR3"), "OLD5 AH > = page 2")
    p_ = mt_ev({"a": "hvpg:1"}, "OLD5 AH past the last page")
    K.check("last page" in cap3(p_), "OLD5 AH past the last page = a caption")
    p_ = mt_ev({"a": "hvc:1"}, "OLD5 AH Category >")
    cm = cmap(p_)
    K.check(AH["reads"][-1][2] == "1" and txt4(cm, "HvFcv") == "Weapons" and txt4(cm, "HvR0N") == "Iron Sword" and int(MS.hvPage) == 0, "OLD5 AH Category > = the next category read (page 1)")
    p_ = mt_ev({"a": "hvc:-1"}, "OLD5 AH Category <")
    p_ = mt_ev({"a": "hvc:-1"}, "OLD5 AH Category < wraps")
    cm = cmap(p_)
    K.check(AH["reads"][-1][2] == "7" and txt4(cm, "HvFcv") == "Other" and not vis3(cm, "HvR0") and txt4(cm, "HvE") == "No listings match - try fewer filters.",
            "OLD5 AH Category < wraps to the last; no match = the AH's empty text")
    p_ = mt_ev({"a": "hvs:1"}, "OLD5 AH Sort >")
    p_ = mt_ev({"a": "hvr:1"}, "OLD5 AH Rarity >")
    K.check(AH["reads"][-1][3:5] == ["1", "1"] and txt4(cmap(p_), "HvFsv") == "Price low-high" and txt4(cmap(p_), "HvFrv") == "Common", "OLD5 AH Sort / Rarity > = the AH's next sort / rarity")
    p_ = mt_ev({"a": "hvq", "@H1": "Bla\"de", "@H2": "5x", "@H3": "60"}, "OLD5 AH Search + levels")
    cm = cmap(p_)
    K.check(AH["reads"][-1][5:8] == ["Blade", "5x", "60"] and txt4(cm, "HvX") == "Level min must be a whole number - it is ignored." and vis3(cm, "HvLv")
            and str(val4(cm, "HvQ")) == "Blade" and str(val4(cm, "HvLb")) == "60" and len([b_ for b_ in bind4(p_, "hvq") if "SkyyMtabHvLa.Value" in b_[2]]) == 4,
            "OLD5 AH Search: the typed word (quotes dropped) + level boxes read, the AH's bad-level warning, the boxes keep it, Enter in any box searches")
    p_ = mt_ev({"a": "hvclr"}, "OLD5 AH Clear")
    K.check('Text: "Reset"' in mk_of(p_, "SkyyMtabHvClr") and "Clear" not in mk_of(p_, "SkyyMtabHvClr"),
            "OLD5 AH FIX the filter reset button says Reset (the AH's empty line: 'click Reset to see every listing')")
    K.check(AH["reads"][-1][2:9] == ["0", "0", "0", "", "", "", "100"] and vis3(cmap(p_), "HvMore") is False, "OLD5 AH Clear = every filter back")
    p_ = mt_ev({"a": "hvmore"}, "OLD5 AH Show more")
    K.check(AH["reads"][-1][8] == "200", "OLD5 AH Show more = 100 more rows read")
    # ======== ITEM + BUY
    p_ = mt_ev({"a": "hvv:0", "t": str(MS.tok)}, "OLD5 AH View Iron Sword")
    cm = cmap(p_)
    K.check(int(MS.hvMode) == 1 and AH["reads"][-1][1] == "item" and AH["reads"][-1][9] == "L1" and vis3(cm, "HvIt") and not vis3(cm, "HvBr")
            and txt4(cm, "HvIn") == "Iron Sword" and txt4(cm, "HvIs").startswith("T3   -   x1   -   ends in") and txt4(cm, "HvIf0") == "Fact 0 of Iron Sword"
            and txt4(cm, "HvIf8") == "Fact 8 of Iron Sword" and txt4(cm, "HvId0") == "A plain item." and txt4(cm, "HvIp") == "400 coins" and vis3(cm, "HvIb")
            and txt4(cm, "HvIb") == "BUY NOW" and txt4(cm, "HvIc") == "" and len(appended4(p_, "SkyyMtabHvIqBg")) == 1 and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabHm0")
            and not sel_ok4(p_), "OLD5 AH ITEM View = the item read: name, T + qty + ends, the 9 facts, the description, the price, BUY NOW, the square %s" % sel_ok4(p_)[:3])
    n0_ = len(AH["acts"])
    old_ = str(MS.tok)
    pu_ = AH["purse"]
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH Buy now")
    K.check(AH["acts"][-1] == [uk3, "prof-A", str(AH["tok"] - 1), "buy", "L1|400"] and AH["bought"] == ["L1"] and AH["purse"] == pu_ - 400
            and cap3(p_) == "You bought Iron Sword for 400 coins." and txt4(cmap(p_), "HvIn") == "That listing is gone" and not vis3(cmap(p_), "HvIb"),
            "OLD5 AH Buy now = tabact buy <id>|<the drawn price> with the read's profile key + token; the AH's answer; the item is gone (%s)" % AH["acts"][-1:])
    p_ = mt_ev({"a": "hvbuy", "t": old_}, "OLD5 AH SAFE double Buy")
    K.check(len(AH["acts"]) == n0_ + 1 and "The page changed" in cap3(p_), "OLD5 AH SAFE a double click on Buy now = ONE call")
    p_ = mt_ev({"a": "hm:0"}, "OLD5 AH back to Browse")
    K.check(int(MS.hvMode) == 0 and txt4(cmap(p_), "HvR0N") == "Fine Stone", "OLD5 AH Browse = the rows again (the bought one gone)")
    p_ = mt_ev({"a": "hvv:0", "t": str(MS.tok)}, "OLD5 AH View Fine Stone (over the confirm amount)")
    cm = cmap(p_)
    K.check(txt4(cm, "HvIb") == "BUY NOW" and "first press asks" in txt4(cm, "HvIc") and txt4(cm, "HvIe") == "1,875 coins each", "OLD5 AH an item over the confirm amount says so")
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH Buy (first press)")
    cm = cmap(p_)
    K.check(AH["acts"][-1][3:] == ["buy", "L2|120000"] and "L2" not in AH["bought"] and cap3(p_) == "Confirm the purchase within 10 s." and txt4(cm, "HvIb") == "CONFIRM BUY"
            and vis3(cm, "HvNn") and len(bind4(p_, "hvno")) == 1, "OLD5 AH the first press = the AH's '=' question word for word; CONFIRM BUY + Not now drawn")
    old_ = str(MS.tok)
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH Buy (the same press again)")
    p2_ = mt_ev({"a": "hvbuy", "t": old_}, "OLD5 AH SAFE a third click on the old drawing")
    K.check("L2" in AH["bought"] and len(AH["acts"]) == n0_ + 1 and cap3(p_) == "You bought Fine Stone for 120000 coins." and "The page changed" in cap3(p2_),
            "OLD5 AH the same press again = bought once; an older drawing's press = no call")
    p_ = mt_ev({"a": "hm:0"}, "OLD5 AH Browse again")
    rown_ = [txt4(cmap(p_), "HvR%dN" % k_) for k_ in range(9)]
    p_ = mt_ev({"a": "hvv:%d" % rown_.index("Blade 00"), "t": str(MS.tok)}, "OLD5 AH View Blade 00")
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH arm Blade 00")
    p_ = mt_ev({"a": "hvno", "t": str(MS.tok)}, "OLD5 AH Not now")
    K.check(AH["acts"][-1][3] == "no" and cap3(p_) == "Nothing done." and not vis3(cmap(p_), "HvNn") and txt4(cmap(p_), "HvIb") == "BUY NOW" and "F0" not in AH["bought"],
            "OLD5 AH Not now = tabact no (the armed buy dropped; the AH's answer)")
    p_ = mt_ev({"a": "hvno", "t": str(MS.tok)}, "OLD5 AH SAFE Not now with nothing armed")
    K.check(AH["acts"][-1][3] == "no" and len([a_ for a_ in AH["acts"] if a_[3] == "no"]) == 1 and "second press" in cap3(p_), "OLD5 AH SAFE Not now with nothing armed = a caption, no call")
    p_ = mt_ev({"a": "hm:0"}, "OLD5 AH Browse for the own listing")
    rown_ = [txt4(cmap(p_), "HvR%dN" % k_) for k_ in range(9)]
    p_ = mt_ev({"a": "hvv:%d" % rown_.index("Oak Log"), "t": str(MS.tok)}, "OLD5 AH View my listing")
    cm = cmap(p_)
    K.check(txt4(cm, "HvIb") == "Cancel listing" and "fee of 25 coins is refunded" in txt4(cm, "HvIc"), "OLD5 AH my own listing = Cancel listing + the fee note")
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH Cancel listing (first press)")
    K.check(AH["acts"][-1][3:] == ["cancel", "L3"] and txt4(cmap(p_), "HvIb") == "YES, CANCEL IT" and cap3(p_).startswith("Cancel it?"), "OLD5 AH Cancel listing asks first (the AH's question)")
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH Cancel listing (second press)")
    K.check(AH["cancelled"] == ["L3"] and cap3(p_).startswith("Cancelled"), "OLD5 AH the same press again = cancelled once")
    p_ = mt_ev({"a": "hm:0"}, "OLD5 AH Browse for the other profile's listing")
    rown_ = [txt4(cmap(p_), "HvR%dN" % k_) for k_ in range(9)]
    p_ = mt_ev({"a": "hvv:%d" % rown_.index("Apple"), "t": str(MS.tok)}, "OLD5 AH View the other profile's listing")
    cm = cmap(p_)
    n0_ = len(AH["acts"])
    K.check(not vis3(cm, "HvIb") and txt4(cm, "HvIo").startswith("That is your other profile's listing") and appended4(p_, "SkyyMtabHvIqBg") == [],
            "OLD5 AH a listing you cannot buy = the AH's why-not note, no button; a bad rarity colour = no square")
    p_ = mt_ev({"a": "hvbuy", "t": str(MS.tok)}, "OLD5 AH SAFE a forged Buy")
    K.check(len(AH["acts"]) == n0_ and cap3(p_) == "Nothing to buy there", "OLD5 AH SAFE a forged Buy where no button was drawn = a caption, no call")
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 AH SAFE a Manage button in the item mode")
    p2_ = mt_ev({"a": "hvp:0", "t": str(MS.tok)}, "OLD5 AH SAFE a Pick in the item mode")
    K.check(len(AH["acts"]) == n0_ and "not on this page" in cap3(p_) and "not on this page" in cap3(p2_), "OLD5 AH SAFE another mode's button (forged) = a caption, no call")
    # ======== CREATE BIN
    p_ = mt_ev({"a": "hm:1"}, "OLD5 AH Create BIN")
    cm = cmap(p_)
    K.check(int(MS.hvMode) == 2 and AH["reads"][-1][1] == "create" and AH["reads"][-1][10:15] == ["-1", "-1", "", "", "-1"] and vis3(cm, "HvCr")
            and [txt4(cm, "HvJ%dN" % k_) for k_ in range(4)] == ["Oak Log", "Stone", "Iron Sword", "Bound Charm"] and not vis3(cm, "HvJ3K") and vis3(cm, "HvJ0K")
            and txt4(cm, "HvJ3S").endswith("cannot be listed") and txt4(cm, "HvCdv") == "24h" and not vis3(cm, "HvCp") and txt4(cm, "HvCpw") == "Pick a stack on the left."
            and txt4(cm, "HvCgo") == "CREATE BIN" and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabHm1") and not sel_ok4(p_),
            "OLD5 AH CREATE your stacks sorted by tier then name (off-market = no Pick), the AH's default duration, nothing picked %s" % sel_ok4(p_)[:3])
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvgo", "t": str(MS.tok), "@H4": ""}, "OLD5 AH SAFE Create without a pick")
    p2_ = mt_ev({"a": "hvp:3", "t": str(MS.tok)}, "OLD5 AH SAFE a forged Pick on an off-market stack")
    K.check(len(AH["acts"]) == n0_ and "Pick a stack" in cap3(p_) and "cannot be listed" in cap3(p2_) and int(MS.hvSec) == -1, "OLD5 AH SAFE no pick / an off-market pick = a caption, no call")
    p_ = mt_ev({"a": "hvp:2", "t": str(MS.tok)}, "OLD5 AH Pick Iron Sword")
    cm = cmap(p_)
    K.check(AH["reads"][-1][10:13] == ["0", "3", "s~A"] and vis3(cm, "HvCp") and txt4(cm, "HvCpn") == "Iron Sword" and txt4(cm, "HvCpl") == "Lowest BIN now: 900 coins"
            and txt4(cm, "HvJ2K") == "Picked" and len(appended4(p_, "SkyyMtabHvCpqBg")) == 1 and len(AH["acts"]) == n0_,
            "OLD5 AH Pick = read again with the drawn stack (section, slot, sig as drawn); the picked stack + the lowest BIN hint; nothing sent")
    p_ = mt_ev({"a": "hvgo", "t": str(MS.tok), "@H4": "500"}, "OLD5 AH SAFE a typed price never seen")
    cm = cmap(p_)
    K.check(len(AH["acts"]) == n0_ and cap3(p_) == str(MTD.HVCHK) and AH["reads"][-1][13] == "500" and txt4(cm, "HvCz") == "Fee now 15 coins   -   if it sells: tax 10, you get 490"
            and txt4(cm, "HvCf1") == "Duration fee for 24h: 10 coins" and str(val4(cm, "HvCv")) == "500",
            "OLD5 AH SAFE NEVER A PRICE NOT SEEN: a typed price = read + its fees drawn, nothing sent")
    p_ = mt_ev({"a": "hvgo", "t": str(MS.tok), "@H4": "500"}, "OLD5 AH Create BIN (the fee check)")
    cm = cmap(p_)
    K.check(AH["acts"][-1][3:] == ["create", "0|3|s~A|500|3"] and cap3(p_) == "Check the fee above, then click Create BIN again." and txt4(cm, "HvCgo") == "LIST IT" and not AH["listed"],
            "OLD5 AH Create BIN = tabact create <the drawn section|slot|sig|price|duration>; the AH previews ('=' word for word); w| = LIST IT")
    old_ = str(MS.tok)
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvgo", "t": str(MS.tok), "@H4": "500"}, "OLD5 AH LIST IT")
    p2_ = mt_ev({"a": "hvgo", "t": old_, "@H4": "500"}, "OLD5 AH SAFE double LIST IT")
    cm = cmap(p_)
    K.check(AH["listed"] == [(0, 3, "s~A", 500, 3)] and len(AH["acts"]) == n0_ + 1 and cap3(p_) == "Listed for 500 coins." and int(MS.hvSec) == -1 and str(MS.hvPrice) == ""
            and "The page changed" in cap3(p2_), "OLD5 AH LIST IT = listed once; the pick + price emptied (a second press cannot repeat it); a double click = one call")
    p_ = mt_ev({"a": "hvd:1"}, "OLD5 AH Duration >")
    K.check(AH["reads"][-1][14] == "4" and txt4(cmap(p_), "HvCdv") == "48h", "OLD5 AH Duration > = the next duration read")
    p_ = mt_ev({"a": "hvd:1"}, "OLD5 AH Duration > wraps")
    K.check(AH["reads"][-1][14] == "0" and txt4(cmap(p_), "HvCdv") == "1h", "OLD5 AH Duration wraps")
    p_ = mt_ev({"a": "hvp:1", "t": str(MS.tok)}, "OLD5 AH Pick Stone")
    p_ = mt_ev({"a": "hvchk", "@H4": "5"}, "OLD5 AH Check fee 5")
    n0_ = len(AH["acts"])
    p2_ = mt_ev({"a": "hvgo", "t": str(MS.tok), "@H4": "5"}, "OLD5 AH SAFE Create with a refused price")
    K.check(txt4(cmap(p_), "HvCvw") == "The price must be at least 10 coins." and len(AH["acts"]) == n0_ and "at least 10 coins" in cap3(p2_),
            "OLD5 AH SAFE the AH's price refusal (v|) shows; Create with it = a caption, no call")
    # ======== MANAGE
    p_ = mt_ev({"a": "hm:2"}, "OLD5 AH Manage")
    cm = cmap(p_)
    K.check(int(MS.hvMode) == 3 and AH["reads"][-1][1] == "manage" and AH["reads"][-1][8] == "1000" and vis3(cm, "HvMg")
            and [txt4(cm, "HvK%dB" % k_) for k_ in (0, 1, 3)] == ["Claim coins", "Cancel", "Claim item"] and not vis3(cm, "HvK2B")
            and txt4(cm, "HvK0S") == "Sold to Bravo - 58,800 coins (tax 1,200)" and vis3(cm, "HvMca") and txt4(cm, "HvMca") == "Claim all"
            and txt4(cm, "HvMo") == "Your other profiles have nothing waiting." and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabHm2") and not sel_ok4(p_),
            "OLD5 AH MANAGE rows in the AH's order with its button words (none on a read-only row), the state line, Claim all, the other-profiles line %s" % sel_ok4(p_)[:3])
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 AH Claim coins")
    K.check(AH["acts"][-1][3:] == ["claim", "M1"] and AH["claimed"] == ["M1"] and cap3(p_) == "Claimed Iron Sword.", "OLD5 AH Claim coins = tabact claim <that row's id>")
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 AH Cancel (first press)")
    K.check(AH["acts"][-1][3:] == ["cancel", "M2"] and txt4(cmap(p_), "HvK0B") == "Yes, cancel" and vis3(cmap(p_), "HvNn"), "OLD5 AH Cancel asks first: 'Yes, cancel' + Not now")
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 AH Cancel (second press)")
    K.check(AH["cancelled"][-1] == "M2" and cap3(p_).startswith("Cancelled"), "OLD5 AH the same press again = cancelled")
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 AH SAFE a forged press on the read-only row")
    p2_ = mt_ev({"a": "hvm:8", "t": str(MS.tok)}, "OLD5 AH SAFE a forged press on no row")
    K.check(len(AH["acts"]) == n0_ and cap3(p_) == "Nothing there" and cap3(p2_) == "Nothing there", "OLD5 AH SAFE a row without a button / no row = a caption, no call")
    p_ = mt_ev({"a": "hvca", "t": str(MS.tok)}, "OLD5 AH Claim all (first press)")
    K.check(AH["acts"][-1][3] == "claimall" and txt4(cmap(p_), "HvMca") == "Yes, claim all" and cap3(p_).startswith("Claim everything (60,000 coins)?"),
            "OLD5 AH Claim all over the confirm amount asks first (the AH's question word for word)")
    p_ = mt_ev({"a": "hvca", "t": str(MS.tok)}, "OLD5 AH Claim all (second press)")
    K.check(AH["claimed"][-1] == "all" and not vis3(cmap(p_), "HvMca") and cap3(p_) == "Claimed everything.", "OLD5 AH the same press again = claimed; nothing waits = no Claim all")
    p_ = mt_ev({"a": "hvca", "t": str(MS.tok)}, "OLD5 AH SAFE Claim all with nothing waiting")
    K.check(AH["claimed"].count("all") == 1 and cap3(p_) == "Nothing to claim", "OLD5 AH SAFE a forged Claim all with nothing waiting = a caption, no call")
    # ======== SAFE: profile switch, '=One moment.', null answers, the banner, a forged home button, the tabs
    AH["owed"] = 60000
    AH["manage"].append(("M5", "coins", "Rock_Stone", 1, 1, "#c9d2dd", 60000, "Claim coins", "Sold", "Stone"))
    p_ = mt_ev({"a": "hvrf"}, "OLD5 AH redraw")
    AH["pk"] = "prof-B"
    p_ = mt_ev({"a": "hvca", "t": str(MS.tok)}, "OLD5 AH SAFE a profile switch")
    K.check(AH["acts"][-1][1] == "prof-A" and "profile changed" in cap3(p_) and AH["claimed"].count("all") == 1, "OLD5 AH SAFE a profile switch between read and click = the AH refuses, nothing moves")
    p_ = mt_ev({"a": "hvca", "t": str(MS.tok)}, "OLD5 AH after the redraw")
    K.check(AH["acts"][-1][1] == "prof-B", "OLD5 AH after the redraw the new profile key is sent")
    AH["pk"] = "prof-A"
    p_ = mt_ev({"a": "hvrf"}, "OLD5 AH redraw 2")
    AH["moment"] = True
    p_ = mt_ev({"a": "hvm:1", "t": str(MS.tok)}, "OLD5 AH '=One moment.'")
    K.check(cap3(p_) == "One moment." and "M5" not in AH["claimed"], "OLD5 AH the AH's 350 ms guard '=One moment.' = the caption, nothing moved")
    AH["anull"] = True
    p_ = mt_ev({"a": "hvm:1", "t": str(MS.tok)}, "OLD5 AH a null answer")
    K.check(cap3(p_) == "That could not run here - nothing changed" and "M5" not in AH["claimed"], "OLD5 AH a null answer (not on the world thread) = said, nothing done")
    AH["anull"] = False
    AH["banner"] = "Trading is paused by an admin."
    AH["null"] = True
    p_ = mt_ev({"a": "hvrf"}, "OLD5 AH FALL the read fails")
    cm = cmap(p_)
    K.check(txt4(cm, "HvH") == str(MTD.HVFAIL) and not vis3(cm, "HvMg") and not sel_ok4(p_), "OLD5 AH FALL the read = null: said, nothing drawn to press")
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 AH FALL a press while it cannot be read")
    K.check(len(AH["acts"]) == n0_ and cap3(p_) == "Nothing there", "OLD5 AH FALL no call while it cannot be read")
    AH["null"] = False
    p_ = mt_ev({"a": "hvrf"}, "OLD5 AH the banner")
    K.check(txt4(cmap(p_), "HvBn") == "Trading is paused by an admin.", "OLD5 AH the AH's banner line shows")
    AH["banner"] = ""
    n1_ = len(MW["acts"])
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "OLD5 SAFE a home button in the Auction House view")
    K.check(len(MW["acts"]) == n1_ and "not on this page" in cap3(p_), "OLD5 SAFE a forged home action (BUY NOW) in the AH view = a caption, no call")
    p_ = mt_ev({"a": "vw:1"}, "OLD5 the Bazaar orders sub-tab from the AH view")
    K.check(int(MS.view) == 1 and has4(p_, "SkyyMtabOv") and not has4(p_, "SkyyMtabHv") and has4(p_, "SkyyMtabOvT3"), "OLD5 the sub-tabs (+ Auction House on every view head)")
    p_ = mt_ev({"a": "vw:3"}, "OLD5 the Auction House sub-tab")
    K.check(int(MS.view) == 3 and int(MS.hvMode) == 3 and has4(p_, "SkyyMtabHv"), "OLD5 the Auction House sub-tab = the AH view (its last mode)")
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvca", "t": str(MS.tok)}, "OLD5 AH Claim all again")
    p_ = mt_ev({"a": "tab:3"}, "OLD5 the Market tab in the AH view")
    K.check(int(MS.view) == 0 and has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabHv"), "OLD5 the Market tab in the AH view = the cards (no back button)")
    n0_ = len(AH["acts"])
    p_ = mt_ev({"a": "hvm:0", "t": str(MS.tok)}, "OLD5 SAFE an AH button on the cards")
    K.check(len(AH["acts"]) == n0_ and "not on this page" in cap3(p_), "OLD5 SAFE a forged AH action on the cards = a caption, no call")
    p_ = mt_ev({"a": "find", "@Q": "stone"}, "OLD5 search on the cards")
    p_ = mt_ev({"a": "ahr:0", "t": str(MS.tok)}, "OLD5 an auction row's Open")
    K.check(int(MS.view) == 3 and int(MS.hvMode) == 0 and AH["reads"][-1][1] == "browse" and AH["reads"][-1][5] == "Fine Stone" and str(val4(cmap(p_), "HvQ")) == "Fine Stone",
            "OLD5 an auction row's Open on the cards = the AH view searching its drawn name")
    p_ = mt_ev({"a": "ah:manage"}, "OLD5 SAFE a card button in the AH view")
    K.check("not on this page" in cap3(p_), "OLD5 SAFE the card's buttons only on the cards")
    p_ = mt_ev({"a": "tab:3"}, "OLD5 back to the cards")
    p_ = mt_ev({"a": "ah:manage"}, "OLD5 Your listings")
    K.check(int(MS.view) == 3 and int(MS.hvMode) == 3 and AH["reads"][-1][1] == "manage", "OLD5 Your listings on the card = the AH view on Manage")
    p_ = mt_ev({"a": "tab:3"}, "OLD5 the cards")
    p_ = mt_ev({"a": "fclear"}, "OLD5 clear")
    K.notes.append("OLD5 AH ran: reads %d, acts %d (bought %s, cancelled %s, claimed %s, listed %s)" % (len(AH["reads"]), len(AH["acts"]), AH["bought"], AH["cancelled"], AH["claimed"], AH["listed"]))
    for k_ in ("ah:fn:tab", "ah:fn:tabact"):
        BR.remove(k_)
'''
HARNESS_OLD5_GUILD = r'''    # ---- OLD5 G (0.3.73, round oldmenu5): THE SOCIAL TAB'S GUILD VIEW (a guild:fn:act stand-in = tools/guilds_0_1_14_patch.py's contract)
    SS, p_ = s_open("OLD5 reopen for the guild")
    K.check('Text: "Manage guild"' in mk_of(p_, "SkyyStabGpage"), "OLD5 G the Guild card's button = Manage guild")
    BR.remove("guild:fn:act")
    p_ = s_ev({"a": "guild"}, "OLD5 G Manage guild without guild:fn:act")
    cm = cmap(p_)
    K.check(int(SS.view) == 4 and has5(p_, "SkyyStabGv") and not has5(p_, "SkyyStabBody") and not has5(p_, "SkyyStabAv") and txt5(cm, "GvH") == str(SCD.GVOLD)
            and not vis5(cm, "GvI") and not vis5(cm, "GvO") and not sel_ok5(p_), "OLD5 G FALL SkyyGuilds 0.1.13 (no guild:fn:act) = the view names 0.1.14; no old page %s" % sel_ok5(p_)[:3])
    ux5 = "00000000-0000-0000-0000-0000000000%02d"
    MEM0 = [[uk5, 2, 1200, 1, 0, 5000, "SkyyCraftA"], [ub5, 1, 800, 1, 2000, -300, "Bravo"], [ua5, 0, 300, 0, 0, 0, "alpha"]] + \
           [[ux5 % i_, 0, 10 * i_, 0, 0, 0, "Member %02d" % i_] for i_ in range(9)]
    GD = {"in": False, "my": -1, "tok": "-", "pk": "prof-G", "arm": "", "acts": [], "reads": [], "inv": ("Bravo", "Wardens", "SW", 6, 24, 42), "moment": False,
          "null": False, "bad": False, "members": [], "log": [("2026-11-%02d 10:00" % (1 + i_ % 28), 100000 + i_, "Bravo", "deposited %d coins" % (i_ + 1)) for i_ in range(20)],
          "bank": 120000, "limA": 5000, "limM": 0, "name": "", "tag": "SW"}

    def g_state():
        if GD["bad"]:
            return "garbage"
        if not GD["in"]:
            L = ["h|0|-|%s|-1|0|0|0|0|0|3|0|0|0|50|10|0|0|0|0|60|%s|%d|||" % (GD["pk"], GD["arm"], 10 if GD["arm"] else 0)]
            if GD["inv"]:
                iv_ = GD["inv"]
                L.append("i|%d|%d|%d|%s|%s|%s" % (iv_[5], iv_[3], iv_[4], iv_[2], iv_[0], iv_[1]))
            return "\n".join(L)
        my = GD["my"]
        ml = -1 if my >= 2 else (GD["limA"] if my == 1 else GD["limM"])
        on_ = len([m_ for m_ in GD["members"] if m_[3] == 1])
        L = ["h|1|%s|%s|%d|6|1200|5000|31200|12000|3|%d|%d|%d|50|10|%d|%d|%d|%d|60|%s|%d|%s|used 2,000 of 5,000 today|game day 12"
             % (GD["tok"], GD["pk"], my, GD["bank"], on_, len(GD["members"]), GD["limA"], GD["limM"], ml, 1 if ml != 0 else 0, GD["arm"], 10 if GD["arm"] else 0, GD["tag"]),
             "n|%s" % GD["name"], "c|%d|%d|%d|%d" % (len(GD["members"]), len(GD["members"]), min(len(GD["log"]), 300), len(GD["log"]))]
        for m_ in GD["members"]:
            L.append("m|%s|%d|%d|%d|%d|%d|%s" % tuple(m_))
        for l_ in reversed(GD["log"]):
            L.append("l|%s|%d|%s|%s" % l_)
        return "\n".join(L)

    def mem_(u_):
        h_ = [m_ for m_ in GD["members"] if m_[0] == u_]
        return h_[0] if h_ else None

    def f_gact(o):
        a_ = [None if x_ is None else str(x_) for x_ in list(o)]
        if a_[0] == "state":
            GD["reads"].append(a_)
            return g_state()
        GD["acts"].append(a_)
        if GD["null"]:
            return None
        op, tok, pk, arg = a_[0], a_[2], a_[3], a_[4]
        if op == "refresh":
            GD["arm"] = ""
            return ""
        if pk != GD["pk"]:
            GD["arm"] = ""
            return "=Your profile changed - here is this profile's guild. Nothing changed."
        if tok != GD["tok"]:
            GD["arm"] = ""
            return "=Your guild changed - look again. Nothing changed."
        if GD["moment"]:
            GD["moment"] = False
            return "=One moment."
        was = GD["arm"]
        GD["arm"] = ""
        if op == "create":
            if len(arg or "") < 3:
                return "-A guild name needs 3 to 24 letters."
            GD.update({"in": True, "my": 2, "tok": "g-1", "name": arg, "inv": None})
            GD["members"] = [list(m_) for m_ in MEM0]
            return "+Created the guild %s." % arg
        if op == "accept":
            GD.update({"in": True, "my": 0, "tok": "g-1", "name": "Wardens", "inv": None})
            GD["members"] = [list(m_) for m_ in MEM0]
            return "+You joined Wardens."
        if op == "decline":
            GD["inv"] = None
            return "+Invite declined."
        if op == "invite":
            return ("+Invited %s - they have 60 s to type /guild accept." % arg) if arg == "Charlie" else ("-Nobody called %s is online." % arg)
        if op in ("deposit", "withdraw"):
            return "+%s %s coins." % ("Deposited" if op == "deposit" else "Withdrew", arg) if arg else "-Type an amount first."
        if op == "amounthint":
            return "=Click Deposit or Withdraw to move %s coins. Enter alone never moves coins." % arg if arg else "=Type an amount (500, 2k, 1.5m or all), then click Deposit or Withdraw."
        if op in ("limitadmin", "limitmember"):
            return "+%s daily limit is now %s." % ("Admin" if op == "limitadmin" else "Member", arg)
        if op == "limithint":
            return "=Type a daily limit (5k, 0 = no withdrawing, none = no limit), then click Set Admin limit or Set Member limit."
        if op in ("promote", "demote"):
            m_ = mem_(arg)
            if m_ is None:
                return "-That player is not in your guild any more."
            m_[1] = 1 if op == "promote" else 0
            return "+%s is now %s." % (m_[6], "an Admin" if op == "promote" else "a Member")
        if op == "kick":
            m_ = mem_(arg)
            if m_ is None:
                return "-That player is not in your guild any more."
            if was == "kick:" + arg:
                GD["members"].remove(m_)
                return "+Removed %s from the guild." % m_[6]
            GD["arm"] = "kick:" + arg
            return "=Click Sure? within 10 s to remove %s from the guild." % m_[6]
        if op == "transfer":
            m_ = mem_(arg)
            if was == "transfer:" + arg:
                m_[1] = 2
                mem_(uk5)[1] = 1
                GD["my"] = 1
                return "+%s is the Leader now. You are an Admin." % m_[6]
            GD["arm"] = "transfer:" + arg
            return "=Click Confirm? within 10 s to make %s the Leader (you become an Admin)." % m_[6]
        if op == "leave":
            if was == "leave":
                GD.update({"in": False, "my": -1, "tok": "-"})
                return "+You left the guild. 1,750 coins of your contribution came back."
            GD["arm"] = "leave"
            return "=Leave %s? 1,750 coins of your contribution come back. Click Leave guild again within 10 s." % GD["name"]
        if op == "disband":
            if GD["my"] != 2:
                return "-Only the Leader can disband the guild."
            if was == "disband":
                GD.update({"in": False, "my": -1, "tok": "-"})
                return "+The guild was disbanded - the bank went back to its members."
            GD["arm"] = "disband"
            return "=Disband %s? Everyone leaves it. Click Disband guild again within 10 s." % GD["name"]
        return "-Unknown guild action."
    BR.put("guild:fn:act", Fn(f_gact))
    nact_ = lambda: len(GD["acts"])
    p_ = s_ev({"a": "gvrf"}, "OLD5 G not in a guild, an invite waiting")
    cm = cmap(p_)
    K.check(GD["reads"][-1] == ["state", uk5, None, None, "500|300"] and vis5(cm, "GvO") and not vis5(cm, "GvI") and vis5(cm, "GvOi")
            and txt5(cm, "GvOq") == "Bravo invited you to Wardens  [SW]" and txt5(cm, "GvOs") == "Guild Lv 6  -  24 members  -  42 s left to answer"
            and "An invite lasts 60 s" in txt5(cm, "GvOh") and len([b_ for b_ in binds_of(p_) if '"gv:create"' in b_[2] and "SkyyStabGvOf.Value" in b_[2]]) == 2 and not sel_ok5(p_),
            "OLD5 G NOT IN A GUILD: the state read (500 members / 300 log lines), the live invite + Accept / Decline, Create guild + Enter %s" % sel_ok5(p_)[:3])
    n0_ = nact_()
    p_ = s_ev({"a": "gv:inv", "t": str(SS.tok), "@GI": "Charlie"}, "OLD5 G SAFE a forged Invite when none is drawn")
    p2_ = s_ev({"a": "gv:create", "t": str(SS.tok), "@GN": "  "}, "OLD5 G SAFE Create with no name")
    K.check(nact_() == n0_ and "not on this page" in cap5(p_) and "Type a guild name first" in cap5(p2_), "OLD5 G SAFE a button not drawn / an empty name = a caption, no call")
    p_ = s_ev({"a": "gv:create", "t": str(SS.tok), "@GN": "Iron \"Pact|"}, "OLD5 G Create guild")
    cm = cmap(p_)
    K.check(GD["acts"][-1] == ["create", uk5, "-", "prof-G", "Iron Pact"] and cap5(p_) == "Created the guild Iron Pact." and vis5(cm, "GvI") and not vis5(cm, "GvO")
            and txt5(cm, "GvN") == "Iron Pact  [SW]" and txt5(cm, "GvL") == "Guild Lv 6   -   Season 3: 12,000 guild XP   -   You are the Leader"
            and "Members 12 / 50   -   2 online   -   Guild bank 120,000 coins" == txt5(cm, "GvSh") and ("Width: %d," % (1200 * int(SCD.GVBARW) // 5000)) in cm.get("#SkyyStabGvB", "")
            and txt5(cm, "GvLv") == "Leave guild" and vis5(cm, "GvDb") and str(SCD.GST1) in mk_of(p_, "SkyyStabGs0") and str(SCD.GST0) in mk_of(p_, "SkyyStabGs1")
            and txt5(cm, "Gs2") == "Log" and not sel_ok5(p_),
            "OLD5 G Create guild = guild:fn:act create <the cleaned typed name> with the read's token '-' + profile key; the guild card, XP bar, Members selected %s" % sel_ok5(p_)[:3])
    K.check(txt5(cm, "GvR0N") == "SkyyCraftA  (you)" and txt5(cm, "GvR0T") == "Leader" and not vis5(cm, "GvR0P") and not vis5(cm, "GvR0K") and not vis5(cm, "GvR0L")
            and txt5(cm, "GvR1T") == "Admin" and txt5(cm, "GvR1P") == "Demote" and vis5(cm, "GvR1K") and txt5(cm, "GvR1L") == "Make leader"
            and txt5(cm, "GvR2P") == "Promote" and txt5(cm, "GvR2K") == "Kick" and "offline" in txt5(cm, "GvR2S") and "bank contribution -300" in txt5(cm, "GvR1S")
            and "taken today 2,000 coins" in txt5(cm, "GvR1S") and vis5(cm, "GvR8") and txt5(cm, "GvMg") == "Page 1 / 2" and vis5(cm, "GvMp") and vis5(cm, "GvIv")
            and txt5(cm, "GvIh") == "Invite: an online player's name - the invite lasts 60 s." and len(bind5(p_, "gm:pro:2")) == 1 and '"t"' in bind5(p_, "gm:pro:2")[0][2].replace(" ", ""),
            "OLD5 G MEMBERS: name (you), rank, online, XP added, bank contribution, taken today; the page's buttons by rank (Leader: Promote / Demote, Kick, Make leader; none on you)")
    # fix (LOCKED 2026-10-10 "guild member list has Invite to party"): online + not you = Invite to party = /party invite <the drawn name>
    K.check(vis5(cm, "GvR1Q") and 'Text: "Invite to party"' in mk_of(p_, "SkyyStabGvR1Q") and not vis5(cm, "GvR0Q") and not vis5(cm, "GvR2Q") and len(bind5(p_, "gm:pty:1")) == 1
            and not bind5(p_, "gm:pty:2") and not bind5(p_, "gm:pty:0"), "OLD5 G FIX Invite to party only on an online member who is not you")
    n0_, l0_ = nact_(), len(lines5())
    p_ = s_ev({"a": "gm:pty:1", "t": str(SS.tok)}, "OLD5 G FIX Invite to party")
    K.check(lines5()[l0_:] == ["party invite Bravo"] and "/party invite Bravo  - see your chat" in cap5(p_) and nact_() == n0_ and not bool(SS.closed) and int(SS.view) == 4,
            "OLD5 G FIX Invite to party = /party invite Bravo as the player (the Players page's line), no guild call, the guild view stays (%s)" % lines5()[l0_:])
    p_ = s_ev({"a": "gm:pty:2", "t": str(SS.tok)}, "OLD5 G FIX SAFE a forged Invite to party on an offline row")
    p2_ = s_ev({"a": "gm:pty:0", "t": str(SS.tok)}, "OLD5 G FIX SAFE a forged Invite to party on your own row")
    K.check(lines5()[l0_:] == ["party invite Bravo"] and "not on this page" in cap5(p_) and "not on this page" in cap5(p2_),
            "OLD5 G FIX SAFE Invite to party where the drawing did not show it = a caption, no command")
    p_ = s_ev({"a": "gpg:1"}, "OLD5 G members page 2")
    K.check(txt5(cmap(p_), "GvR0N") == "Member 06" and not vis5(cmap(p_), "GvR3"), "OLD5 G > = page 2")
    p_ = s_ev({"a": "gpg:-1"}, "OLD5 G members page 1")
    p_ = s_ev({"a": "gm:pro:2", "t": str(SS.tok)}, "OLD5 G Promote alpha")
    K.check(GD["acts"][-1] == ["promote", uk5, "g-1", "prof-G", ua5] and cap5(p_) == "alpha is now an Admin." and txt5(cmap(p_), "GvR2P") == "Demote",
            "OLD5 G Promote = guild:fn:act promote <that row's uuid> (one press, as the page); the row now offers Demote")
    n0_ = nact_()
    p_ = s_ev({"a": "gm:pro:2", "t": str(SS.tok)}, "OLD5 G SAFE a forged Promote on a Demote row")
    p2_ = s_ev({"a": "gm:kick:0", "t": str(SS.tok)}, "OLD5 G SAFE a forged Kick on your own row")
    p3_ = s_ev({"a": "gm:kick:8", "t": str(SS.tok)}, "OLD5 G a Kick on a drawn member")
    K.check(nact_() == n0_ + 1 and "not on this page" in cap5(p_) and "not on this page" in cap5(p2_) and GD["acts"][-1][:1] == ["kick"],
            "OLD5 G SAFE a button the drawing did not show on that row = a caption, no call")
    p_ = s_ev({"a": "gm:dem:2", "t": str(SS.tok)}, "OLD5 G Demote alpha")
    K.check(GD["acts"][-1][0] == "demote" and txt5(cmap(p_), "GvR2P") == "Promote", "OLD5 G Demote = guild:fn:act demote")
    old_ = str(SS.tok)
    p_ = s_ev({"a": "gm:kick:2", "t": str(SS.tok)}, "OLD5 G Kick (first press)")
    cm = cmap(p_)
    K.check(GD["acts"][-1] == ["kick", uk5, "g-1", "prof-G", ua5] and cap5(p_) == "Click Sure? within 10 s to remove alpha from the guild." and txt5(cm, "GvR2K") == "Sure"
            and mem_(ua5) is not None, "OLD5 G Kick's first press = the page's question word for word, the button says Sure (the bridge's arm)")
    n0_ = nact_()
    p_ = s_ev({"a": "gm:kick:2", "t": old_}, "OLD5 G SAFE Kick on the older drawing")
    K.check(nact_() == n0_ and "The page changed" in cap5(p_), "OLD5 G SAFE a double click (the older drawing) = no second call")
    p_ = s_ev({"a": "gm:kick:2", "t": str(SS.tok)}, "OLD5 G Kick (the same press again)")
    K.check(mem_(ua5) is None and cap5(p_) == "Removed alpha from the guild." and txt5(cmap(p_), "GvR2N") != "alpha", "OLD5 G the same press again = removed once")
    p_ = s_ev({"a": "gm:lead:1", "t": str(SS.tok)}, "OLD5 G Make leader (first press)")
    K.check(GD["acts"][-1][0] == "transfer" and GD["acts"][-1][4] == ub5 and txt5(cmap(p_), "GvR1L") == "Confirm" and "the Leader (you become an Admin)" in cap5(p_),
            "OLD5 G Make leader = guild:fn:act transfer <uuid>: the first press asks, the button says Confirm")
    p_ = s_ev({"a": "gm:lead:1", "t": str(SS.tok)}, "OLD5 G Make leader (second press)")
    cm = cmap(p_)
    K.check(int(GD["my"]) == 1 and "You are an Admin" in cap5(p_) and txt5(cm, "GvR1T") == "Leader" and not vis5(cm, "GvR1P") and not vis5(cm, "GvR1K")
            and not vis5(cm, "GvR1L") and vis5(cm, "GvR2K") and not vis5(cm, "GvR2P") and not vis5(cm, "GvDb") and "an Admin" in txt5(cm, "GvL"),
            "OLD5 G now an Admin: no Promote / Make leader / Disband; Kick only on Members; nothing on the Leader")
    p_ = s_ev({"a": "gv:inv", "t": str(SS.tok), "@GI": "Char lie!"}, "OLD5 G Invite")
    K.check(GD["acts"][-1] == ["invite", uk5, "g-1", "prof-G", "Charlie"] and cap5(p_).startswith("Invited Charlie") and (sval(cmap(p_), "#SkyyStabGvIf.Value") or "") == "",
            "OLD5 G Invite = guild:fn:act invite <the cleaned typed name>; the box empties after it worked")
    p_ = s_ev({"a": "gv:inv", "t": str(SS.tok), "@GI": "Nobody"}, "OLD5 G Invite an unknown name")
    K.check(cap5(p_) == "Nobody called Nobody is online." and str(sval(cmap(p_), "#SkyyStabGvIf.Value")) == "Nobody", "OLD5 G an unknown name = the guild's line, the typed name kept")
    # BANK
    p_ = s_ev({"a": "gs:1"}, "OLD5 G the Bank tab")
    cm = cmap(p_)
    K.check(int(SS.gSub) == 1 and vis5(cm, "GvK") and not vis5(cm, "GvM") and not vis5(cm, "GvG") and txt5(cm, "GvKv") == "Guild bank  120,000 coins"
            and txt5(cm, "GvKu") == "Withdraw limits per game day:  Admins 5,000 a day  -  Members no withdrawing      You: used 2,000 of 5,000 today   (game day 12)"
            and vis5(cm, "GvKw") and not vis5(cm, "GvKl") and vis5(cm, "GvKn") and str(SCD.GST1) in mk_of(p_, "SkyyStabGs1") and "can't withdraw" not in txt5(cm, "GvKh")
            and not sel_ok5(p_), "OLD5 G BANK: the bank, the limits + your usage + the day, Deposit / Withdraw (Admin), no limit box (not the Leader) %s" % sel_ok5(p_)[:3])
    p_ = s_ev({"a": "gv:dep", "t": str(SS.tok), "@GA": "5K"}, "OLD5 G Deposit 5k")
    K.check(GD["acts"][-1] == ["deposit", uk5, "g-1", "prof-G", "5k"] and cap5(p_) == "Deposited 5k coins." and (sval(cmap(p_), "#SkyyStabGvKf.Value") or "") == "",
            "OLD5 G Deposit = guild:fn:act deposit <the typed amount>; the box empties")
    p_ = s_ev({"a": "gv:amt", "t": str(SS.tok), "@GA": "2k"}, "OLD5 G Enter in the amount box")
    K.check(GD["acts"][-1][0] == "amounthint" and cap5(p_) == "Click Deposit or Withdraw to move 2k coins. Enter alone never moves coins."
            and str(sval(cmap(p_), "#SkyyStabGvKf.Value")) == "2k", "OLD5 G Enter = the page's amount note (amounthint), nothing moves, the box kept")
    p_ = s_ev({"a": "gv:wd", "t": str(SS.tok), "@GA": "1,000"}, "OLD5 G Withdraw")
    K.check(GD["acts"][-1] == ["withdraw", uk5, "g-1", "prof-G", "1,000"] and cap5(p_) == "Withdrew 1,000 coins.", "OLD5 G Withdraw = guild:fn:act withdraw <the typed amount>")
    n0_ = nact_()
    p_ = s_ev({"a": "gv:lima", "t": str(SS.tok), "@GL": "none"}, "OLD5 G SAFE an Admin's forged Set Admin limit")
    K.check(nact_() == n0_ and "not on this page" in cap5(p_), "OLD5 G SAFE the limit buttons only for the Leader (a forged one = a caption)")
    GD["my"] = 2
    mem_(uk5)[1] = 2
    p_ = s_ev({"a": "gvrf"}, "OLD5 G Refresh as the Leader")
    cm = cmap(p_)
    K.check(GD["acts"][-1][0] == "refresh" and vis5(cm, "GvKl") and not vis5(cm, "GvKn") and "no limit (Leader)" in txt5(cm, "GvKu"), "OLD5 G Refresh = guild:fn:act refresh; the Leader sees the limit box")
    p_ = s_ev({"a": "gv:lima", "t": str(SS.tok), "@GL": "None"}, "OLD5 G Set Admin limit")
    p2_ = s_ev({"a": "gv:limm", "t": str(SS.tok), "@GL": "2k"}, "OLD5 G Set Member limit")
    p3_ = s_ev({"a": "gv:limh", "t": str(SS.tok), "@GL": ""}, "OLD5 G Enter in the limit box")
    K.check([a_[0] + " " + str(a_[4]) for a_ in GD["acts"][-3:]] == ["limitadmin none", "limitmember 2k", "limithint "] and cap5(p_) == "Admin daily limit is now none."
            and cap5(p3_).startswith("Type a daily limit"), "OLD5 G Set Admin / Member limit = limitadmin / limitmember <typed>; Enter = limithint")
    GD["my"] = 0
    mem_(uk5)[1] = 0
    p_ = s_ev({"a": "gvrf"}, "OLD5 G a Member with no withdrawing")
    cm = cmap(p_)
    K.check(not vis5(cm, "GvKw") and "can't withdraw right now" in txt5(cm, "GvKh"), "OLD5 G a Member with the daily limit 0 = no Withdraw (the page's note)")
    n0_ = nact_()
    p_ = s_ev({"a": "gv:wd", "t": str(SS.tok), "@GA": "5"}, "OLD5 G SAFE a forged Withdraw")
    K.check(nact_() == n0_ and "not on this page" in cap5(p_), "OLD5 G SAFE a forged Withdraw = a caption, no call")
    # LOG
    p_ = s_ev({"a": "gs:2"}, "OLD5 G the Log tab")
    cm = cmap(p_)
    K.check(vis5(cm, "GvG") and not vis5(cm, "GvK") and txt5(cm, "GvE0T") == "deposited 20 coins" and txt5(cm, "GvE0P") == "Bravo" and txt5(cm, "GvE0B") == "100,019 coins"
            and txt5(cm, "GvE14T") == "deposited 6 coins" and txt5(cm, "GvGg") == "Page 1 / 2" and "20 bank moves kept" in txt5(cm, "GvGn") and not sel_ok5(p_),
            "OLD5 G LOG: newest first, when / who / what / the bank after, 15 a page %s" % sel_ok5(p_)[:3])
    p_ = s_ev({"a": "glpg:1"}, "OLD5 G log page 2")
    K.check(txt5(cmap(p_), "GvE0T") == "deposited 5 coins" and not vis5(cmap(p_), "GvE5"), "OLD5 G log > = page 2")
    p_ = s_ev({"a": "gs:0"}, "OLD5 G back to Members")
    # SAFE: '=One moment.', a profile switch, a null answer, a bad read
    GD["moment"] = True
    p_ = s_ev({"a": "gv:leave", "t": str(SS.tok)}, "OLD5 G '=One moment.'")
    K.check(cap5(p_) == "One moment." and GD["in"] and txt5(cmap(p_), "GvLv") == "Leave guild", "OLD5 G the bridge's 350 ms guard = the caption, nothing changed")
    GD["pk"] = "prof-H"
    p_ = s_ev({"a": "gv:leave", "t": str(SS.tok)}, "OLD5 G SAFE a profile switch")
    K.check(GD["acts"][-1][3] == "prof-G" and "profile changed" in cap5(p_) and GD["in"], "OLD5 G SAFE a profile switch between read and click = the guild refuses, nothing changed")
    p_ = s_ev({"a": "gv:leave", "t": str(SS.tok)}, "OLD5 G Leave (first press)")
    K.check(GD["acts"][-1][:4] == ["leave", uk5, "g-1", "prof-H"] and txt5(cmap(p_), "GvLv") == "Click again to leave" and cap5(p_).startswith("Leave Iron Pact?"),
            "OLD5 G after the redraw the new profile key; Leave's first press = the page's question, the button says Click again to leave")
    GD["null"] = True
    p_ = s_ev({"a": "gv:leave", "t": str(SS.tok)}, "OLD5 G a null answer")
    K.check(cap5(p_) == "That could not run here - nothing changed." and GD["in"], "OLD5 G a null answer (not on the world thread) = said, nothing done")
    GD["null"] = False
    GD["arm"] = "leave"
    p_ = s_ev({"a": "gv:leave", "t": str(SS.tok)}, "OLD5 G Leave (the same press again)")
    cm = cmap(p_)
    K.check(not GD["in"] and cap5(p_).startswith("You left the guild.") and vis5(cm, "GvO") and not vis5(cm, "GvI") and not vis5(cm, "GvOi") and not sel_ok5(p_),
            "OLD5 G the same press again = left; the view shows Create guild again")
    p_ = s_ev({"a": "gv:acc", "t": str(SS.tok)}, "OLD5 G SAFE a forged Accept with no invite")
    K.check(GD["acts"][-1][0] == "leave" and "not on this page" in cap5(p_), "OLD5 G SAFE Accept with no invite drawn = a caption, no call")
    GD["inv"] = ("Bravo", "Wardens", "SW", 6, 24, 42)
    p_ = s_ev({"a": "gvrf"}, "OLD5 G a new invite")
    p_ = s_ev({"a": "gv:dec", "t": str(SS.tok)}, "OLD5 G Decline")
    K.check(GD["acts"][-1][:4] == ["decline", uk5, "-", "prof-H"] and cap5(p_) == "Invite declined." and not vis5(cmap(p_), "GvOi"), "OLD5 G Decline = guild:fn:act decline")
    GD["inv"] = ("Bravo", "Wardens", "SW", 6, 24, 42)
    p_ = s_ev({"a": "gvrf"}, "OLD5 G another invite")
    p_ = s_ev({"a": "gv:acc", "t": str(SS.tok)}, "OLD5 G Accept")
    cm = cmap(p_)
    K.check(GD["acts"][-1][:4] == ["accept", uk5, "-", "prof-H"] and GD["in"] and vis5(cm, "GvI") and "a Member" in txt5(cm, "GvL") and not vis5(cm, "GvIv")
            and txt5(cm, "GvIh") == "Only the Leader and Admins can invite players." and not vis5(cm, "GvR1K"), "OLD5 G Accept = joined as a Member: no invite box, no buttons")
    GD["my"] = 2
    p_ = s_ev({"a": "gvrf"}, "OLD5 G the Leader again")
    p_ = s_ev({"a": "gv:dis", "t": str(SS.tok)}, "OLD5 G Disband (first press)")
    K.check(GD["acts"][-1][0] == "disband" and txt5(cmap(p_), "GvDb") == "Click again to DISBAND" and GD["in"], "OLD5 G Disband's first press arms it (the page's words)")
    p_ = s_ev({"a": "gs:2"}, "OLD5 G another tab while armed")
    p_ = s_ev({"a": "gv:dis", "t": str(SS.tok)}, "OLD5 G Disband (second press)")
    K.check(not GD["in"] and cap5(p_).startswith("The guild was disbanded") and int(SS.gSub) == 0, "OLD5 G the same press again = disbanded; the view back on Members")
    GD["bad"] = True
    p_ = s_ev({"a": "gvrf"}, "OLD5 G FALL a bad read")
    K.check(txt5(cmap(p_), "GvH") == str(SCD.GVFAIL) and not vis5(cmap(p_), "GvO") and not vis5(cmap(p_), "GvI"), "OLD5 G FALL an unreadable state = said, nothing to press")
    n0_ = nact_()
    p_ = s_ev({"a": "gv:create", "t": str(SS.tok), "@GN": "Again"}, "OLD5 G FALL Create while unreadable")
    K.check(nact_() == n0_ and "not on this page" in cap5(p_), "OLD5 G FALL no call while it cannot be read")
    GD["bad"] = False
    p_ = s_ev({"a": "tab:5"}, "OLD5 G the Social tab")
    K.check(int(SS.view) == 0 and has5(p_, "SkyyStabBody") and not has5(p_, "SkyyStabGv"), "OLD5 G the Social tab = the cards (no back button)")
    n0_ = nact_()
    p_ = s_ev({"a": "gv:dep", "t": str(SS.tok), "@GA": "5"}, "OLD5 G SAFE a guild button on the cards")
    p2_ = s_ev({"a": "gs:1"}, "OLD5 G SAFE a guild tab on the cards")
    K.check(nact_() == n0_ and "not on this page" in cap5(p_) and "not on this page" in cap5(p2_), "OLD5 G SAFE a forged guild action on the cards = a caption, no call")
    K.notes.append("OLD5 G ran: guild:fn:act reads %d, acts %d" % (len(GD["reads"]), len(GD["acts"])))
    BR.remove("guild:fn:act")
'''
T.rep('''"""Harness for SkyyMenu 0.3.72 (old menu follow-up - the Market tab; tools/menu_0_3_72_patch.py, round oldmenu4).''',
      '''"""Harness for SkyyMenu 0.3.73 (old menu follow-up - the Guild + Auction House views; tools/menu_0_3_73_patch.py, round oldmenu5).
GENERATED by tools/menu_0_3_73_patch.py from the 0.3.72 harness (edit the patch, not this file): every 0.3.72 check runs again on the
0.3.73 jar (TAB3: New listing / an auction's Open = the Auction House view, not ah:fn:view / ah:fn:open; TAB5: Manage guild = the guild view;
OLD2 / OLD3 / OLD4's ratchets = 'stays gone'), plus
  OLD5 STATIC   the ratchet: OLD_LEFT lost social:guild + market:auctions; no Guild page / opener link or text; the views call guild:fn:act
                and ah:fn:tab / tabact (the drawn price / the drawn read); the build asserts the views fit and their run-time markup is proven
       G        (guild:fn:act stand-in) Manage guild: an older SkyyGuilds named; not in a guild (the state read, the invite, Create + Enter, a
                forged / empty one refused), Create (the cleaned name, token '-'), the card + XP bar, MEMBERS (rank buttons as the page, 2
                pages, Promote / Demote, forged buttons refused, Kick + Make leader two presses with the armed words, a double click once,
                the Admin view), Invite (cleaned, emptied / kept), BANK (limits + usage, Deposit / Enter note / Withdraw, the Leader's limit
                box + its Enter note, a Member with limit 0, forged ones refused), LOG (newest first, 2 pages), '=One moment.', profile
                switch, null answer, Leave two presses, Accept / Decline, Disband two presses, a bad read, the Social tab, forged on the cards
       AH       (ah:fn:tab / tabact stand-ins) Browse all on an older SkyyAuctions named; BROWSE (filters by the AH's lists, wrap, search +
                levels + the warning, Clear, Show more, rows: square / tooltip colour / tier / seller / off market / grace, a bad colour never
                in markup, 2 pages), ITEM (facts, Buy now with the drawn price, a double click once, the confirm press + CONFIRM BUY, Not now,
                own listing Cancel two presses, a why-not note, forged buttons), CREATE BIN (stacks by tier then name, off-market no Pick,
                Pick = read with the drawn stack, a typed price only checked, preview then LIST IT once, Duration wraps, a refused price),
                MANAGE (button words, Claim, Cancel two presses, read-only / no row refused, Claim all two presses, nothing left), profile
                switch, '=One moment.', a null answer, a null read, the banner, a forged home action, the sub-tabs, the Market tab, Open +
                Your listings on the cards
       every new packet: every b.set / append / binding names an element drawn in that packet (the frame + ONE section)
The 0.3.72 harness text follows:
Harness for SkyyMenu 0.3.72 (old menu follow-up - the Market tab; tools/menu_0_3_72_patch.py, round oldmenu4).''')
T.rep('VERSION = "0.3.72"\nJAR', 'VERSION = "0.3.73"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.71.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.72.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.71.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.72.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_72_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_73_patch.py")')
T.rep('"scratch", "oldmenu4", "menu"', '"scratch", "oldmenu5", "menu"')
T.rep('ADDED = []   # 0.3.72: no new class\n', 'ADDED = []   # 0.3.73: no new class\n')
EXPECT_BODY = '''    "MarketTab": ["+f hvArmed", "+f hvBuyId", "+f hvBuyK", "+f hvBuyP", "+f hvCPage", "+f hvCPages", "+f hvCat", "+f hvCatN", "+f hvCg", "+f hvCl",
                  "+f hvClaimAll", "+f hvCo", "+f hvCs", "+f hvDur", "+f hvDurN", "+f hvId", "+f hvLa", "+f hvLast", "+f hvLb", "+f hvMBtn", "+f hvMIds",
                  "+f hvMKind", "+f hvMPage", "+f hvMPages", "+f hvMax", "+f hvMode", "+f hvOk", "+f hvPage", "+f hvPages", "+f hvPick", "+f hvPk",
                  "+f hvPrice", "+f hvPriceOk", "+f hvPriceSeen", "+f hvPriceWhy", "+f hvQ", "+f hvRar", "+f hvRarN", "+f hvReady", "+f hvRows", "+f hvSec",
                  "+f hvSig", "+f hvSlot", "+f hvSort", "+f hvSortN", "+f hvTok", "+m ahSq", "+m cellAfter", "+m cyc", "+m fillHv", "+m htip", "+m hvAct",
                  "+m hvBrowse", "+m hvBuy", "+m hvCreate", "+m hvFail", "+m hvGo", "+m hvItem", "+m hvMRow", "+m hvManage", "+m hvModeOf", "+m hvOpen",
                  "+m hvPickAt", "+m hvRead", "+m hvSquare", "+m hvText", "+m nameAt", "+m sortCells", "+m tierT", "~c ", "~m build", "~m fillAh",
                  "~m goView", "~m handleDataEvent", "~m viewOf"],
    "MarketTabData": ["+f HMODE", "+f HVCAP", "+f HVCHK", "+f HVCN", "+f HVDN", "+f HVFAIL", "+f HVMN", "+f HVOFF", "+f HVOLD", "+f HVRN", "~<clinit>"],
    "SocialTab": ["+f gAllow", "+f gArm", "+f gBtn", "+f gIds", "+f gIn", "+f gInv", "+f gKeepA", "+f gKeepI", "+f gKeepL", "+f gKeepN", "+f gLPage",
                  "+f gLPages", "+f gLast", "+f gMy", "+f gNm", "+f gOk", "+f gPage", "+f gPages", "+f gPk", "+f gSub", "+f gTok", "+m fillGv", "+m gHas", "+m gact",
                  "+m gamt", "+m gfmt", "+m gtext", "+m gvBank", "+m gvDo", "+m gvHide", "+m gvLog", "+m gvMembers", "+m gvParty", "+m gvRow", "+m limT", "+m netT",
                  "+m rankN", "~c ", "~m build", "~m fillGuild", "~m goView", "~m handleDataEvent"],
    "SocialTabData": ["+f GST0", "+f GST1", "+f GSUB", "+f GTAB", "+f GVBARW", "+f GVFAIL", "+f GVLN", "+f GVMN", "+f GVOFF", "+f GVOLD", "+f GVREAD", "~<clinit>"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.72:', 'if "--expect-dump" in sys.argv:'), EXPECT_73.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.72"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.73"') == 1, "S VERSION")
''' + HARNESS_OLD5_STATIC.rstrip("\n"))
# OLD4's ratchet compared 0.3.72 with 0.3.71: against 0.3.72 it is OLD5's (above) - its two rows stay gone
T.rep('''    K.check(lefto_ - left2_ == set([("market", "bazaar"), ("market", "merchants")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 2
            and ("market", "auctions") in left2_,
            "OLD4 RATCHET OLD_LEFT lost market:bazaar + market:merchants, nothing added, the Auction House kept (%d -> %d; still: %s)"
            % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(not (left2_ & set([("market", "bazaar"), ("market", "merchants")])), "OLD4 RATCHET (0.3.73: vs 0.3.72) market:bazaar + market:merchants stay gone")''')
T.rep('''    K.check(not (left2_ & set([("social", "players"), ("character", "stats"), ("character", "profiles"), ("social", "party")])) and ("social", "guild") in left2_,
            "OLD3 RATCHET (0.3.72: vs 0.3.71) social:players + character:stats + character:profiles + social:party stay gone, the Guild page kept")''',
      '''    K.check(not (left2_ & set([("social", "players"), ("character", "stats"), ("character", "profiles"), ("social", "party")])),
            "OLD3 RATCHET (0.3.73: vs 0.3.72) social:players + character:stats + character:profiles + social:party stay gone")''')
T.rep('''    K.check(("market", "auctions") in left2_ and ("market", "auctions") in ops_o_ and ("settings", "mods") not in left2_ and ("character", "pets") not in left2_,
            "OLD2 RATCHET (0.3.71: vs 0.3.70) settings:mods + character:pets stay gone, market:auctions still tracked")''',
      '''    K.check(("market", "auctions") in ops_o_ and ("settings", "mods") not in left2_ and ("character", "pets") not in left2_,
            "OLD2 RATCHET (0.3.73: vs 0.3.72) settings:mods + character:pets stay gone; 0.3.72's opener links were tracked (0.3.73: gone, OLD5)")''')
# TAB3: New listing / an auction's Open are the Auction House view now (never ah:fn:view / ah:fn:open)
T.rep('''    p_ = mt_ev({"a": "ah:create"}, "TAB3 ACT New listing")
    K.check(MW["ahv"] and MW["ahv"][-1][1] == "create", "TAB3 ACT New listing = ah:fn:view create")
    p_ = mt_ev({"a": "find", "@Q": "stone"}, "TAB3 search for AH")
    p_ = mt_ev({"a": "ahr:0", "t": str(MS.tok)}, "TAB3 ACT AH Open")
    K.check(MW["aho"] and MW["aho"][-1][1] == "Fine Stone", "TAB3 ACT an auction row's Open = ah:fn:open on its name")
    p_ = mt_ev({"a": "ah:steal"}, "TAB3 SAFE junk AH view")
    K.check(MW["ahv"][-1][1] == "create", "TAB3 SAFE an unknown AH view never reaches ah:fn:view")''',
      '''    p_ = mt_ev({"a": "ah:create"}, "TAB3 ACT New listing")
    K.check(not MW["ahv"] and int(MS.view) == 3 and int(MS.hvMode) == 2,
            "TAB3 ACT New listing (0.3.73) = the Auction House view on Create BIN - ah:fn:view (the old page) is never called (%s)" % MW["ahv"][-1:])
    p_ = mt_ev({"a": "vw:0"}, "TAB3 back to the cards (AH)")
    p_ = mt_ev({"a": "find", "@Q": "stone"}, "TAB3 search for AH")
    p_ = mt_ev({"a": "ahr:0", "t": str(MS.tok)}, "TAB3 ACT AH Open")
    K.check(not MW["aho"] and int(MS.view) == 3 and int(MS.hvMode) == 0 and str(MS.hvQ) == "Fine Stone",
            "TAB3 ACT an auction row's Open (0.3.73) = the Auction House view searching its drawn name - ah:fn:open is never called (%s)" % MW["aho"][-1:])
    p_ = mt_ev({"a": "vw:0"}, "TAB3 back to the cards (AH 2)")
    p_ = mt_ev({"a": "ah:steal"}, "TAB3 SAFE junk AH view")
    K.check(not MW["ahv"] and int(MS.view) == 0 and "Pick an Auction House button" in cap3(p_), "TAB3 SAFE an unknown AH view = a caption, nothing opened")''')
T.rep('''                            ("guild", "Guild page", None)):''', '''                            ("guild", "Manage guild (0.3.73: the guild view)", "SocialTab")):''')
T.rep('''    MW["have"]["Rock_Stone"] = 0
    MW["purse"] = 50000
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:panel", "bank:fn:move", "ah:fn:view", "ah:fn:find", "ah:fn:open", "bazaar:fn:open"):''',
      '''    MW["have"]["Rock_Stone"] = 0
    MW["purse"] = 50000
''' + HARNESS_OLD5_AH.rstrip("\n") + '''
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:panel", "bank:fn:move", "ah:fn:view", "ah:fn:find", "ah:fn:open", "bazaar:fn:open"):''')
T.rep('''    for cn_ in ("msg", "tpaccept", "tpdeny", "trade"):
        E.CM.cmds.remove(cn_)
        if CMD5.get(cn_) is not None:
            E.CM.cmds.put(cn_, CMD5[cn_])
    # TABS''', '''    for cn_ in ("msg", "tpaccept", "tpdeny", "trade"):
        E.CM.cmds.remove(cn_)
        if CMD5.get(cn_) is not None:
            E.CM.cmds.put(cn_, CMD5[cn_])
    bind5 = lambda p_, act_: [b_ for b_ in binds_of(p_) if ('"a":"%s"' % act_) in b_[2].replace(" ", "")]
''' + HARNESS_OLD5_GUILD.rstrip("\n") + '''
    # TABS''')
if T.dst:
    T.finish()
