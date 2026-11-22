"""Derive SkyyMenu/build_skyymenu_0.3.59.py + SkyyMenu/test_skyymenu_0.3.59.py from the SET pin SkyyMenu 0.3.58 (generated - never re-run
its patch). Run:  python tools/menu_0_3_59_patch.py   then   python SkyyMenu/build_skyymenu_0.3.59.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.59.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.58 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.59 (2026-11-21, round tab3) = TAB SCREENS ROUND 3: THE MARKET TAB - ONE SCREEN (Bazaar + Auction House + Merchants + the Bank).
Skyy's words: 11-21 "game is closed, deploy as ready. i might be able to test later. build and deploy everything on your list"; 11-14 on the Market
card ("Bazaar, Auction House, Merchants, and the Bank, so the new bank mini-game lives here"): "perfect."; popup "Do the 7 tabs and the Pets screen
look right?": "Yes, both" (Bank under Market) (docs/answered/ui.md 2026-11-14). Approved art: research/ui-theme-art/market-page.png; README 'Tab
pages' question 1 default = ONE SCREEN AS DRAWN (Auctions | Merchants | Bank always visible). SURVEY: vanilla has no market screen; no pack mod
draws one - this page reads our own market mods' bridges only (SkyyBazaar 0.2.6 bazaar:fn:tab / tabact - NEW, the only new keys; SkyyBank 0.1.17
bank:fn:panel / move - unchanged; SkyyAuctions 0.1.17 ah:fn:find / view / open - unchanged; SkyyMerchants: its hub tab).
  1. THE MARKET TAB of the inventory's top bar (and the skill page's / pets screen's Market tab) opens the new MARKET SCREEN (MarketTab: an inline
     Skyglass page, kit tools/skyyui.py, the inventory's frame + the same 7-tab top bar with Market selected; coins + bank in the bar):
     TOP    BAZAAR rail (search field + Find / Clear, the Bazaar tabs) | THE TAB'S ITEMS (7 a page, SORTED BY TIER then name, icon in its
            rarity frame + the Style Guide 15 tooltip, name, tier tag, BUY NOW / SELL NOW each, you have; View; < >) | THE SELECTED ITEM
            (icon, name in its rarity colour, tier tag + you have, best order / offer, BUY NOW / SELL NOW with the price each, AMOUNT 1 /
            a stack / All, the two totals (green = it can go, red = why not), Buy order / Sell offer -> the Bazaar page on that item,
            YOUR ORDERS (4 rows) + Claim all).
     BOTTOM AUCTION HOUSE (claims waiting, the search's auctions with Open, Browse all / New listing / Your listings) | MERCHANTS (Open
            Merchants = their Market tab) | BANK (Lv badge, balance, purse, a fill bar against the level's capacity, interest, next payout,
            your share, AMOUNT 1k / 10k / 100k / 1M / All, Deposit / Withdraw, the level line + Upgrade (two presses), Bank page).
     Every number, price, tax, limit and rule = the owning mod's: buys / sells / claims through bazaar:fn:tabact (SkyyBazaar's Trader.buyN /
     sellN / BzClaim.claimAll: the shown total is the cap / floor, 'Confirm buys from' two presses, profile key, world thread, 350 ms guard);
     deposits / withdrawals / the upgrade through bank:fn:move (BankCmd.move / BankStore.upgrade: lock, profile key + epoch from the panel).
     This page holds a page token too: a click from an older drawing = "The page changed" (no bridge call) - a double click never moves twice.
  2. FALLBACK: without bazaar:fn:tab / tabact (an older SkyyBazaar) the Market tab opens today's Market page (as 0.3.58). Without bank:fn:panel
     the bank panel says so; without SkyyAuctions the AH card says so. 'Full page' = today's Market > Bazaar page; World / Social / Settings
     keep today's routes.
  3. Rarity colours (rarity frames round the icons - fix tab3, the selected name in its rarity colour, tooltip titles), tier sort (SkyyBazaar sorts),
     Style Guide 15 tooltips (name in rarity colour, tier tag, prices gold, you have, the yellow click footer) on every item cell.
  Every bound click answers with exactly ONE page packet; every grid copy is a NEW ItemStack(id, qty) without metadata behind known(id); no Top /
  Bottom alignment; inline page only; never setPageWithWindows.
  NOT BUILT (next rounds, nothing half-wired): placing buy orders / sell offers ON this screen (the buttons open the Bazaar page on the item), a
  typed amount, cancelling an order here (the Bazaar page), the 24 h price change column (SkyyBazaar keeps no price history), Auction House
  'ending soon' without a search + Bid / Buy in place (needs an AH read key), merchant cards with where / when (needs a SkyyMerchants read key),
  the bank's vault pages row (SkyyVault), Shift-click = buy / sell 64.
  New classes MarketTabData + MarketTab; no command, no setting, no lang key, no system, no saved data.
  ROLLBACK to 0.3.58: safe alone (nothing saved; the Market tab opens the old Market page again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.58.py"), os.path.join(MOD, "build_skyymenu_0.3.59.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.58.py"), os.path.join(MOD, "test_skyymenu_0.3.59.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.58"\n') and P.has("tools/menu_0_3_58_patch.py") and P.has("PetsTab")
assert not P.has("MarketTab"), "not the generated SkyyMenu 0.3.58 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.58: THE PETS TAB''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.59: THE MARKET TAB = ONE SCREEN (MarketTab: the Bazaar rail + search, the tab's items sorted by tier, the selected item with BUY NOW / SELL NOW
       + amount chips + your orders / Claim all, the Auction House card, Merchants, the BANK panel with Deposit / Withdraw / Upgrade - SkyyBazaar
       0.2.6 bazaar:fn:tab / tabact + SkyyBank bank:fn:panel / move; 'Full page' = the old Market page) (notes: tools/menu_0_3_59_patch.py).
       CHECKED: see SkyyMenu/test_skyymenu_0.3.59.py.
0.3.58: THE PETS TAB''')
P.rep('VERSION = "0.3.58"\n', 'VERSION = "0.3.59"\n')

# ---------- (1) the MARKET SCREEN markup (one page data list drawn by MarketTab.build)
MT_PAGE = r'''
# ================= 0.3.59 THE MARKET TAB: ONE SCREEN (tools/menu_0_3_59_patch.py; approved art research/ui-theme-art/market-page.png; Skyy 11-14 on
# the Market card "Bazaar, Auction House, Merchants, and the Bank, so the new bank mini-game lives here": "perfect.") =================
# The inventory's frame and top bar (Market selected); TOP: Bazaar rail | the tab's items | the selected item + your orders;
# BOTTOM: Auction House | Merchants | Bank.
MT = "SkyyMtab"
MT_TOP_H = 480
MT_BOT_H = IV_BODY_H - MT_TOP_H - 8                         # 356
MT_L, MT_M = 300, 640
MT_R = IV_IW - MT_L - MT_M - 2 * IV_GAP                     # 596
MT_A, MT_C = 500, 400
MT_B = IV_IW - MT_A - MT_C - 2 * IV_GAP                     # 636
MT_LI, MT_MI, MT_RI, MT_AI, MT_CI, MT_BI = MT_L - 20, MT_M - 20, MT_R - 20, MT_A - 20, MT_C - 20, MT_B - 20
MT_CATN = 9                                                 # the Bazaar tabs in the rail (SkyyBazaar has 6 today)
MT_RN = 7                                                   # item rows a page (nothing scrolls)
MT_NW, MT_PW, MT_HW, MT_VW = 220, 92, 84, 52                # a row: name, a price, you have, View
MT_ON = 4                                                   # your orders shown
MT_AN = 4                                                   # auction rows
MT_SW = MT_RI - 64 - 10                                     # the selected item's text column
MT_BBW = (MT_RI - 8) // 2                                   # a big button
MT_BAR = MT_BI                                              # the bank fill bar
MT_AMT = ["1", "Stack", "All"]
MT_BAMT = ["1k", "10k", "100k", "1m", "all"]
MT_BAMTL = ["1k", "10k", "100k", "1M", "All"]
MT_CHW, MT_BCW = 120, 70
MT_TXT = {
    "foot": "Prices move with every trade.",
    "lfoot": "Click an item (or View) to see it on the right.",
    "merch1": "Merchants sell weapons, mounts, pet eggs and augments.",
    "merch2": "The travelling merchant moves between the zones;",
    "merch3": "each visit restocks. Their shop opens from here.",
    "ahnone": "Search above to see the auctions for it too.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in MT_TXT.values() for c_ in v_), "0.3.59: plain texts"
for _k in ("merch1", "merch2", "merch3"):
    assert SUI.text_width(MT_TXT[_k], 13) <= MT_CI, ("0.3.59: a merchants line fits", _k)
assert SUI.text_width(MT_TXT["lfoot"], 12) <= MT_MI and SUI.text_width(MT_TXT["ahnone"], 12) <= MT_AI, "0.3.59: the foot lines fit"
for _l in MT_AMT[:2] + ["All 100,000"]:
    assert SUI.text_width(_l, 12, bold=True) <= MT_CHW - 12, ("0.3.59: an amount chip fits", _l)
for _l in MT_BAMTL:
    assert SUI.text_width(_l, 12, bold=True) <= MT_BCW - 12, ("0.3.59: a bank chip fits", _l)
# the run-time markup: the tab buttons of the rail, the amount chips, the bank bar fill
MT_ST_CAT, MT_ST_CATSEL = SUI.glass_button_style("tab", 14), SUI.glass_button_style("tabSelected", 14)
MT_ST_CH, MT_ST_CHSEL = SUI.glass_button_style("tab", 12), SUI.glass_button_style("tabSelected", 12)
MT_CAT = "TextButton #SkyyMtab{I} { Anchor: (Width: %d, Height: 32, Bottom: 4); {S} }" % MT_LI
MT_CHIP = "TextButton #SkyyMtab{I} { Anchor: (Width: {W}, Height: 28, Right: 4); {S} }"
MT_FILL = "Group { Anchor: (Width: {W}, Height: 8); Background: %s; }" % SUI.glass_col("xp")
for _mk in (MT_CAT.replace("{I}", "Kt0").replace("{S}", MT_ST_CATSEL), MT_CHIP.replace("{I}", "Am0").replace("{W}", "120").replace("{S}", MT_ST_CH),
            MT_FILL.replace("{W}", "40")):
    SUI.check_markup(_mk, prefix=MT, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.59: a run-time markup line Java can hold"
MT_RCOL = list(PT_RCOL)                                     # 0 = none; 1-6 Common..Mythic (= the pets screen's)
assert SUI.text_width("Sell now: 100,000 for 99,999,999,999 coins  (after the 10.25% tax on order fills)", 13, bold=True) <= MT_RI - 8,     "0.3.59: the sell total + its tax note fit"
MT_FRAMES = ["QualityCommon", "QualityUncommon", "QualityRare", "QualityEpic", "QualityLegendary", "RarityMythic"]   # fix tab3: rarity 1-6 frames
assert all(f_ in SUI.GLASS_RARITY for f_ in MT_FRAMES) and len(MT_FRAMES) == len(MT_RCOL) - 1, "0.3.59: a Skyglass frame per rarity 1-6"
MT_TAGCOL, MT_GOLD, MT_FOOT, MT_SOFT, MT_DIMC = SUI.glass_col("xp"), SUI.glass_col("xp"), SUI.glass_col("action"), SUI.glass_col("row"), SUI.glass_col("dim")
MT_GAIN = [SUI.COLOR["success"], SUI.COLOR["error"]]       # SkyyBank 0.1.17 bank:fn:panel [7] = one of these (else the text colour)


def _mt_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label

    def holder(parent, ident, w, h, size, cols, anchor=None, bold=False):
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, c_, bold=bold, w=w, h=h)) for k_, c_ in enumerate(cols)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)

    def framed(parent, grid, size, anchor):
        # fix tab3: the RARITY FRAME on the icon (PROJECT-RULES 'rarity colour on the icon / frame'): a holder without LayoutMode, the 6
        # rarity frames (Skyglass Quality / Rarity patches, MT_FRAMES) BEHIND a 1 x 1 grid inset 3 px - the frame shows as a ring round the
        # slot and never covers the slot (hover tooltip + click stay the grid's). MarketTab.frame shows one (rarity 1-6) or none.
        vs = [SUI.keep_at0('Group #%sF%d { Anchor: (Width: %d, Height: %d); Background: %s; }' % (grid, k_ + 1, size, size, SUI.glass_patch(fr_)))
              for k_, fr_ in enumerate(MT_FRAMES)]
        hm, kids = SUI.keep_holder(grid + "Q", size, size, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)
        ap.append(("#" + grid + "Q", SUI.keep_at0(G_.glass_grid(grid, 1, 1, drag=False, slot=size - 6, icon=size - 14)).replace(
            "Left: 0, Top: 0", "Left: 3, Top: 3")))
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (MT, IV_PAGE_W, IV_PAGE_H)))
    win = MT + "Win"
    ap.append(("#" + MT, G_.glass_group(win, IV_W, IV_WIN_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": (IV_PAGE_H - IV_WIN_H) // 2})))
    # ---- row 1: the same 7 tabs (Market selected), Full page, coins + bank, the X
    top = MT + "Top"
    ap.append(("#" + win, G_.glass_group(top, IV_IW, IV_TOP_H, layout="Left")))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (MT, i), lb, "tabSelected" if i == 3 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    cw_ = IV_COIN_W + 96
    assert SUI.text_width("Coins 999,999,999    Bank 999,999,999", 14, bold=True) <= cw_ - 8, "0.3.59: coins + bank fit the top bar"
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(MT + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(MT + "Coins", "", 14, "xp", bold=True, w=cw_, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(MT + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    ap.append(("#" + win, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }' % (MT, IV_IW, G_.glass_path("Separator"))))
    body = MT + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Top")))
    up_ = MT + "Up"
    ap.append(("#" + body, G_.glass_group(up_, IV_IW, MT_TOP_H, layout="Left")))
    # ======== TOP LEFT: the BAZAAR rail
    rl = MT + "Rl"
    ap.append(("#" + up_, G_.glass_group(rl, MT_L, MT_TOP_H, role="panel", layout="Top", pad=10)))
    ap.append(("#" + rl, lab(None, "BAZAAR", 15, "accentHi", bold=True, w=MT_LI, h=24)))
    srow = MT + "Srow"
    ap.append(("#" + rl, G_.glass_group(srow, MT_LI, 32, layout="Left", anchor={"top": 6})))
    ap.append(("#" + srow, G_.text_field(MT + "QBox", MT + "Q", w=MT_LI - 128, h=32, placeholder="Search all items", max_length=40, size=13)))
    ap.append(("#" + srow, G_.glass_button(MT + "Find", "Find", "secondary", w=60, h=32, size=13, anchor={"left": 4})))
    ap.append(("#" + srow, G_.glass_button(MT + "Fx", "Clear", "secondary", w=60, h=32, size=13, anchor={"left": 4})))
    ap.append(("#" + rl, G_.glass_group(MT + "Cats", MT_LI, MT_CATN * 36, layout="Top", anchor={"top": 8})))
    ap.append(("#" + rl, lab(MT + "Rf", "", 12, "dim", w=MT_LI, h=18, anchor={"top": 6})))
    ap.sets.append((MT + "Rf", "Text", MT_TXT["foot"]))
    assert 20 + 24 + 6 + 32 + 8 + MT_CATN * 36 + 6 + 18 <= MT_TOP_H and MT_LI - 128 + 128 <= MT_LI, "0.3.59: the Bazaar rail fits"
    ap.append(("#" + up_, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== TOP MIDDLE: the tab's items
    ls = MT + "Ls"
    ap.append(("#" + up_, G_.glass_group(ls, MT_M, MT_TOP_H, role="panel", layout="Top", pad=10)))
    lh = MT + "Lh"
    ap.append(("#" + ls, G_.glass_group(lh, MT_MI, 24, layout="Left")))
    ap.append(("#" + lh, lab(MT + "Lt", "", 15, "accentHi", bold=True, w=MT_MI - 200, h=24)))
    ap.append(("#" + lh, lab(None, "sorted by tier", 12, "dim", w=200, h=24, halign="End")))
    ch = MT + "Lc"
    ap.append(("#" + ls, G_.glass_group(ch, MT_MI, 20, layout="Left", anchor={"top": 6})))
    ap.append(("#" + ch, lab(None, "ITEM", 11, "dim", bold=True, w=6 + 44 + 8 + MT_NW, h=20)))
    for t_, w_ in (("BUY NOW", MT_PW), ("SELL NOW", MT_PW), ("YOU HAVE", MT_HW)):
        ap.append(("#" + ch, lab(None, t_, 11, "dim", bold=True, w=w_, h=20, halign="End")))
    for k_ in range(MT_RN):
        r_ = "%sR%d" % (MT, k_)
        ap.append(("#" + ls, G_.glass_group(r_, MT_MI, 46, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        framed(r_, r_ + "I", 46, {"top": 0})
        nx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(nx, MT_NW, 46, layout="Top", anchor={"left": 8})))
        ap.append(("#" + nx, lab(r_ + "N", "", 14, "row", bold=True, w=MT_NW, h=24, anchor={"top": 2})))
        ap.append(("#" + nx, lab(r_ + "T", "", 11, "xp", bold=True, w=MT_NW, h=16)))
        ap.append(("#" + r_, lab(r_ + "B", "", 14, "xp", bold=True, w=MT_PW, h=46, halign="End")))
        ap.append(("#" + r_, lab(r_ + "S", "", 14, "xp", bold=True, w=MT_PW, h=46, halign="End")))
        ap.append(("#" + r_, lab(r_ + "H", "", 13, "text", w=MT_HW, h=46, halign="End")))
        ap.append(("#" + r_, G_.glass_button(r_ + "Go", "View", "secondary", w=MT_VW, h=28, size=12, anchor={"left": 4, "top": 9})))
    assert 12 + 46 + 8 + MT_NW + 2 * MT_PW + MT_HW + 4 + MT_VW <= MT_MI, "0.3.59: an item row fits"
    pr_ = MT + "Pr"
    ap.append(("#" + ls, G_.glass_group(pr_, MT_MI, 28, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pr_, G_.glass_button(MT + "Pp", "<", "secondary", w=36, h=26, size=14, anchor={"right": 4})))
    ap.append(("#" + pr_, lab(MT + "Pg", "", 12, "text", bold=True, w=110, h=26, halign="Center")))
    ap.append(("#" + pr_, G_.glass_button(MT + "Pn", ">", "secondary", w=36, h=26, size=14, anchor={"left": 4, "right": 8})))
    ap.append(("#" + pr_, lab(MT + "Ln", "", 12, "dim", w=MT_MI - 36 - 4 - 110 - 36 - 12, h=26, halign="End")))
    ap.append(("#" + ls, lab(MT + "Lf", "", 12, "action", bold=True, w=MT_MI, h=18, anchor={"top": 4})))
    ap.sets.append((MT + "Lf", "Text", MT_TXT["lfoot"]))
    assert 20 + 24 + 6 + 20 + MT_RN * 50 + 6 + 28 + 4 + 18 <= MT_TOP_H, "0.3.59: the items panel fits"
    ap.append(("#" + up_, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== TOP RIGHT: the selected item + your orders
    se = MT + "Se"
    ap.append(("#" + up_, G_.glass_group(se, MT_R, MT_TOP_H, role="panel", layout="Top", pad=10)))
    sh = MT + "Sh"
    ap.append(("#" + se, G_.glass_group(sh, MT_RI, 64, layout="Left")))
    framed(sh, MT + "SI", 64, None)
    sx = MT + "Sx"
    ap.append(("#" + sh, G_.glass_group(sx, MT_SW, 64, layout="Top", anchor={"left": 10})))
    holder(sx, MT + "SN", MT_SW, 26, 20, ["dim"] + MT_RCOL[1:], bold=True)
    ap.append(("#" + sx, lab(MT + "St", "", 13, "xp", bold=True, w=MT_SW, h=18)))
    ap.append(("#" + sx, lab(MT + "Sb", "", 11, "dim", w=MT_SW, h=18)))
    bb = MT + "Bbn"
    ap.append(("#" + se, G_.glass_group(bb, MT_RI, 44, layout="Left", anchor={"top": 8})))
    ap.append(("#" + bb, G_.glass_button(MT + "Buy", "BUY NOW", "primary", w=MT_BBW, h=44, size=15, anchor={"right": 8})))
    ap.append(("#" + bb, G_.glass_button(MT + "Sell", "SELL NOW", "primary", w=MT_BBW, h=44, size=15)))
    ob = MT + "Ob"
    ap.append(("#" + se, G_.glass_group(ob, MT_RI, 32, layout="Left", anchor={"top": 6})))
    ap.append(("#" + ob, G_.glass_button(MT + "Ord", "Buy order - on the Bazaar page", "secondary", w=MT_BBW, h=32, size=12, anchor={"right": 8})))
    ap.append(("#" + ob, G_.glass_button(MT + "Off", "Sell offer - on the Bazaar page", "secondary", w=MT_BBW, h=32, size=12)))
    for t_ in ("Buy order - on the Bazaar page", "Sell offer - on the Bazaar page"):
        assert SUI.text_width(t_, 12, bold=True) <= MT_BBW - 16, ("0.3.59: a button text fits", t_)
    amr = MT + "Amr"
    ap.append(("#" + se, G_.glass_group(amr, MT_RI, 28, layout="Left", anchor={"top": 8})))
    ap.append(("#" + amr, lab(None, "Amount", 13, "dim", bold=True, w=76, h=28)))
    ap.append(("#" + amr, G_.glass_group(MT + "Am", MT_RI - 76, 28, layout="Left")))
    holder(se, MT + "Tb", MT_RI, 20, 13, ["green", "red"], anchor={"top": 6}, bold=True)
    holder(se, MT + "Ts", MT_RI, 20, 13, ["green", "red"], bold=True)
    orh = MT + "Orh"
    ap.append(("#" + se, G_.glass_group(orh, MT_RI, 28, layout="Left", anchor={"top": 10})))
    ap.append(("#" + orh, lab(MT + "Oh", "", 12, "dim", bold=True, w=150, h=28)))
    ap.append(("#" + orh, lab(MT + "Cl", "", 12, "green", bold=True, w=MT_RI - 150 - 120, h=28, halign="End", anchor={"right": 8})))
    ap.append(("#" + orh, G_.glass_button(MT + "Claim", "Claim all", "primary", w=112, h=28, size=12)))
    for k_ in range(MT_ON):
        ap.append(("#" + se, lab("%sO%d" % (MT, k_), "", 12, "text", w=MT_RI, h=20, anchor={"top": 2})))
    assert 20 + 64 + 8 + 44 + 6 + 32 + 8 + 28 + 6 + 20 + 20 + 10 + 28 + MT_ON * 22 <= MT_TOP_H and 3 * (MT_CHW + 4) <= MT_RI - 76, "0.3.59: the item panel fits"
    # ======== BOTTOM
    dn = MT + "Dn"
    ap.append(("#" + body, G_.glass_group(dn, IV_IW, MT_BOT_H, layout="Left", anchor={"top": 8})))
    # ---- AUCTION HOUSE
    ah = MT + "Ah"
    ap.append(("#" + dn, G_.glass_group(ah, MT_A, MT_BOT_H, role="panel", layout="Top", pad=10)))
    ahh = MT + "Ahh"
    ap.append(("#" + ah, G_.glass_group(ahh, MT_AI, 24, layout="Left")))
    ap.append(("#" + ahh, lab(None, "AUCTION HOUSE", 15, "accentHi", bold=True, w=200, h=24)))
    ap.append(("#" + ahh, lab(MT + "Ac", "", 12, "green", bold=True, w=MT_AI - 200, h=24, halign="End")))
    ap.append(("#" + ah, lab(MT + "As", "", 12, "dim", w=MT_AI, h=18, anchor={"top": 4})))
    for k_ in range(MT_AN):
        a_ = "%sA%d" % (MT, k_)
        ap.append(("#" + ah, G_.glass_group(a_, MT_AI, 44, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + a_, G_.glass_grid(a_ + "I", 1, 1, drag=False, slot=40, icon=32, anchor={"top": 2})))
        ax = a_ + "X"
        ap.append(("#" + a_, G_.glass_group(ax, MT_AI - 12 - 40 - 8 - 80, 44, layout="Top", anchor={"left": 8})))
        ap.append(("#" + ax, lab(a_ + "N", "", 13, "row", bold=True, w=MT_AI - 140, h=22, anchor={"top": 2})))
        ap.append(("#" + ax, lab(a_ + "S", "", 11, "xp", bold=True, w=MT_AI - 140, h=16)))
        ap.append(("#" + a_, G_.glass_button(a_ + "Go", "Open", "primary", w=72, h=28, size=12, anchor={"top": 8})))
    abr = MT + "Abr"
    ap.append(("#" + ah, G_.glass_group(abr, MT_AI, 32, layout="Left", anchor={"top": 10})))
    for k_, t_ in enumerate(("Browse all", "New listing", "Your listings")):
        ap.append(("#" + abr, G_.glass_button("%sAb%d" % (MT, k_), t_, "primary" if k_ == 1 else "secondary", w=152, h=32, size=13, anchor={"right": 8})))
    assert 20 + 24 + 4 + 18 + MT_AN * 48 + 10 + 32 <= MT_BOT_H and 3 * 160 <= MT_AI, "0.3.59: the Auction House card fits"
    ap.append(("#" + dn, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ---- MERCHANTS
    mc = MT + "Mc"
    ap.append(("#" + dn, G_.glass_group(mc, MT_C, MT_BOT_H, role="panel", layout="Top", pad=10)))
    ap.append(("#" + mc, lab(None, "MERCHANTS", 15, "accentHi", bold=True, w=MT_CI, h=24)))
    for k_ in range(3):
        ap.append(("#" + mc, lab(MT + "M%d" % k_, "", 13, "text", w=MT_CI, h=20, anchor={"top": 6 if k_ == 0 else 2})))
        ap.sets.append((MT + "M%d" % k_, "Text", MT_TXT["merch%d" % (k_ + 1)]))
    ap.append(("#" + mc, G_.glass_button(MT + "Mgo", "Open Merchants", "primary", w=200, h=36, size=14, anchor={"top": 14})))
    ap.append(("#" + mc, lab(MT + "Mn", "", 12, "dim", w=MT_CI, h=18, anchor={"top": 6})))
    assert 20 + 24 + 6 + 60 + 4 + 14 + 36 + 6 + 18 <= MT_BOT_H, "0.3.59: the merchants card fits"
    ap.append(("#" + dn, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ---- BANK
    bk = MT + "Bk"
    ap.append(("#" + dn, G_.glass_group(bk, MT_B, MT_BOT_H, role="panel", layout="Top", pad=10)))
    bkh = MT + "Bkh"
    ap.append(("#" + bk, G_.glass_group(bkh, MT_BI, 24, layout="Left")))
    ap.append(("#" + bkh, lab(None, "BANK", 15, "accentHi", bold=True, w=120, h=24)))
    ap.append(("#" + bkh, lab(MT + "Bl", "", 13, "xp", bold=True, w=MT_BI - 120 - 112, h=24, halign="End", anchor={"right": 8})))
    ap.append(("#" + bkh, G_.glass_button(MT + "Bpg", "Bank page", "secondary", w=104, h=24, size=12)))
    ap.append(("#" + bk, lab(MT + "Bv", "", 26, "xp", bold=True, w=MT_BI, h=34, anchor={"top": 4})))
    ap.append(("#" + bk, lab(MT + "Bs", "", 12, "dim", w=MT_BI, h=18)))
    ap.append(("#" + bk, 'Group #%sBb { Anchor: (Width: %d, Height: 8, Top: 4); LayoutMode: Left; Background: %s; }' % (MT, MT_BAR, IV_TRACK)))
    ap.append(("#" + bk, lab(MT + "Bi", "", 11, "text", w=MT_BI, h=18, anchor={"top": 6})))
    ap.append(("#" + bk, lab(MT + "Bn", "", 11, "dim", w=MT_BI, h=18)))
    holder(bk, MT + "Bg", MT_BI, 18, 12, ["green", "red", "text"], bold=True)
    bar_ = MT + "Bar"
    ap.append(("#" + bk, G_.glass_group(bar_, MT_BI, 28, layout="Left", anchor={"top": 6})))
    ap.append(("#" + bar_, lab(None, "Amount", 13, "dim", bold=True, w=76, h=28)))
    ap.append(("#" + bar_, G_.glass_group(MT + "Ba", MT_BI - 76, 28, layout="Left")))
    bbt = MT + "Bbt"
    ap.append(("#" + bk, G_.glass_group(bbt, MT_BI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + bbt, G_.glass_button(MT + "Dep", "Deposit", "primary", w=150, h=34, size=14, anchor={"right": 8})))
    ap.append(("#" + bbt, G_.glass_button(MT + "Wd", "Withdraw", "secondary", w=150, h=34, size=14)))
    ap.append(("#" + bbt, "Group { Anchor: (Width: %d); }" % (MT_BI - 150 - 8 - 150 - 160)))
    ap.append(("#" + bbt, G_.glass_button(MT + "Upg", "Upgrade", "secondary", w=160, h=34, size=14)))
    ap.append(("#" + bk, lab(MT + "L1", "", 11, "text", w=MT_BI, h=16, anchor={"top": 6})))
    ap.append(("#" + bk, lab(MT + "L2", "", 11, "dim", w=MT_BI, h=16)))
    assert 20 + 24 + 4 + 34 + 18 + 4 + 8 + 6 + 18 + 18 + 18 + 6 + 28 + 6 + 34 + 6 + 16 + 16 <= MT_BOT_H and 5 * (MT_BCW + 4) <= MT_BI - 76, "0.3.59: the bank panel fits"
    assert (IV_PAGE_H <= SUI.MAX_PAGE_H and IV_PAGE_W <= SUI.MAX_PAGE_W and MT_TOP_H + 8 + MT_BOT_H == IV_BODY_H
            and MT_L + MT_M + MT_R + 2 * IV_GAP == IV_IW and MT_A + MT_C + MT_B + 2 * IV_GAP == IV_IW), "0.3.59: the market screen fits one 1080p screen"
    # ---- row 3: the caption + key hints
    hn = MT + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(MT + "K%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate((("LMB", "Select"), ("Enter", "Search"), ("Tab / Esc", "Close")))]
    hw = sum(w_ for _m, w_ in parts)
    ap.append(("#" + hn, lab(MT + "Cap", "", 14, "dim", w=IV_IW - hw - 20, h=IV_HINT_H)))
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    binds = [("#%sT%d" % (MT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + MT + "Close", "close"), ("#" + MT + "Full", "full"),
                                                                                  ("#" + MT + "Pp", "pg:-1"), ("#" + MT + "Pn", "pg:1"), ("#" + MT + "Fx", "fclear"),
                                                                                  ("#" + MT + "Ord", "order"), ("#" + MT + "Off", "offer"),
                                                                                  ("#" + MT + "Ab0", "ah:browse"), ("#" + MT + "Ab1", "ah:create"),
                                                                                  ("#" + MT + "Ab2", "ah:manage"), ("#" + MT + "Mgo", "mer"), ("#" + MT + "Bpg", "bank")]
    return ap, binds


MT_AP, MT_BINDS = _mt_page()
SUI.check_page(MT_AP, MT)
for _p, _mk in MT_AP:
    SUI.check_markup(_mk, prefix=MT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.59: the market screen never scrolls"
_mt_ids = set(i_ for _p, mk_ in MT_AP for i_ in SUI._static_ids(mk_))
for _s, _a in MT_BINDS:
    assert _s[1:] in _mt_ids, ("0.3.59: binding target", _s)
MT_DYN = (["Coins", "Close", "Full", "Cap", "Q", "Find", "Fx", "Cats", "Rf", "Lt", "Pp", "Pg", "Pn", "Ln", "Lf", "SI", "St", "Sb", "Buy", "Sell", "Ord", "Off",
           "Am", "Oh", "Cl", "Claim", "Ac", "As", "Mgo", "Mn", "Bl", "Bpg", "Bv", "Bs", "Bb", "Bi", "Bn", "Ba", "Dep", "Wd", "Upg", "L1", "L2"]
          + ["SN%d" % k_ for k_ in range(7)] + ["Tb0", "Tb1", "Ts0", "Ts1", "Bg0", "Bg1", "Bg2"] + ["O%d" % k_ for k_ in range(MT_ON)]
          + ["R%d%s" % (k_, x_) for k_ in range(MT_RN) for x_ in ("", "I", "N", "T", "B", "S", "H", "Go", "IQ")]
          + ["%sF%d" % (g_, f_ + 1) for g_ in ["SI"] + ["R%dI" % k_ for k_ in range(MT_RN)] for f_ in range(len(MT_FRAMES))] + ["SIQ"]
          + ["A%d%s" % (k_, x_) for k_ in range(MT_AN) for x_ in ("", "I", "N", "S", "Go")] + ["Ab0", "Ab1", "Ab2"])
for _g in MT_DYN:
    assert MT + _g in _mt_ids, "0.3.59: the market screen has #" + MT + _g
MT_RUNTIME_IDS = ["Kt%d" % k_ for k_ in range(MT_CATN)] + ["Am%d" % k_ for k_ in range(len(MT_AMT))] + ["Bc%d" % k_ for k_ in range(len(MT_BAMT))]
assert not [x_ for x_ in MT_RUNTIME_IDS if MT + x_ in _mt_ids], "0.3.59: a run-time id is also a static id (the rail tabs once clashed with the key hints)"
_mt_tok = SUI.proven_tokens(list(MT_AP))
MT_UNPROVEN = sorted(k_ for k_, g_ in _mt_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_)))
assert set(MT_UNPROVEN) <= set(["SlotBackground"]), "0.3.59: only SlotBackground (proven on the inventory page, TEST 282): %s" % MT_UNPROVEN
assert not [k_ for k_ in _mt_tok if k_ in ("MouseEntered", "MouseExited", "TooltipText")], "0.3.59: no hover events / tooltips of ours"
SUI.assert_glass_paths(MT_AP)
MT_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in MT_AP)
MT_RUNTIME_MAX = MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1      # the rail's tabs + the amount chips + the bank chips + the bank fill
MT_ELEMENTS = MT_SHELL_ELEMENTS + MT_RUNTIME_MAX
assert MT_ELEMENTS <= 800, "0.3.59: the market screen stays well under the ~1,600 element budget (%d static + %d at run time)" % (MT_SHELL_ELEMENTS, MT_RUNTIME_MAX)
MT_LK, MT_LP, MT_LB = [], [], []
for _p, _mk in MT_AP:
    MT_LK.append("A")
    MT_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    MT_LB.append(SUI.render(_mk))
for _i, _pr, _v in MT_AP.sets:
    MT_LK.append("S")
    MT_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    MT_LB.append(_v)
for _s, _a in MT_BINDS:
    MT_LK.append("E")
    MT_LP.append(_s)
    MT_LB.append(_a)
assert MT_LK[0] == "A" and MT_LP[0] == "", "0.3.59: the page data starts with the root"
for _x in MT_LP + MT_LB:
    assert "@" not in _x and "\n" not in _x and len(_x.encode("utf-8")) < 60000, "0.3.59: a page line Java can hold"
print("0.3.59 market screen: %d elements (shell %d + at most %d at run time; budget ~1,600), %d appends, %d b.set, %d bindings; unproven: %s"
      % (MT_ELEMENTS, MT_SHELL_ELEMENTS, MT_RUNTIME_MAX, len(MT_AP), len(MT_AP.sets), len(MT_BINDS), ", ".join(MT_UNPROVEN)))

'''
P.rep('''PKG = T["PKG"]
# 0.2: every class goes through mk()''', MT_PAGE.lstrip("\n") + '''PKG = T["PKG"]
# 0.2: every class goes through mk()''')

# ---------- the two new classes
P.rep('''ptab = mk("PetsTab", T["PAGE"])     # 0.3.58: THE PETS TAB = ONE SCREEN
''', '''ptab = mk("PetsTab", T["PAGE"])     # 0.3.58: THE PETS TAB = ONE SCREEN
mtd  = mk("MarketTabData")  # 0.3.59: the market screen's data (LK / LP / LB, the run-time markup)
mtab = mk("MarketTab", T["PAGE"])   # 0.3.59: THE MARKET TAB = ONE SCREEN
''')
P.rep('''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, pl)''',
      '''         idat, ist, ipg, itk, irf, icl, ich, ihk, ihf, iwr, ifl, ibye, irdy, imod, icr, sdat, skpg, ptd, ptab, mtd, mtab, pl)''')

# ---------- MarketTabData constants + MarketTab fields / constructor (after the PetsTab constructor)
MT_DATA = r'''# 0.3.59: THE MARKET SCREEN DATA (MarketTabData) + the MarketTab fields
F(mtd, "public static final String LK = %s;" % jstr("".join(MT_LK)))
F(mtd, "public static final String[] LP = %s;" % jarr(MT_LP))
F(mtd, "public static final String[] LB = %s;" % jarr(MT_LB))
F(mtd, "public static final String[] AMT = %s;" % jarr(MT_AMT))
F(mtd, "public static final String[] BAMT = %s;" % jarr(MT_BAMT))
F(mtd, "public static final String[] BAMTL = %s;" % jarr(MT_BAMTL))
F(mtd, "public static final String[] RCOL = %s;" % jarr(MT_RCOL))
for _n, _v in (("CATN", MT_CATN), ("RN", MT_RN), ("ON", MT_ON), ("AN", MT_AN), ("BAR", MT_BAR), ("CHW", MT_CHW), ("BCW", MT_BCW)):
    F(mtd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("CAT", MT_CAT), ("CHIP", MT_CHIP), ("ST_CAT", MT_ST_CAT), ("ST_CATSEL", MT_ST_CATSEL), ("ST_CH", MT_ST_CH), ("ST_CHSEL", MT_ST_CHSEL),
               ("FILL", MT_FILL), ("TAGCOL", MT_TAGCOL), ("GOLD", MT_GOLD), ("FOOT", MT_FOOT), ("SOFT", MT_SOFT), ("DIMC", MT_DIMC),
               ("GOK", MT_GAIN[0]), ("GBAD", MT_GAIN[1]), ("AHNONE", MT_TXT["ahnone"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))
for _f in ("public static volatile int OPENS = 0;", "public static volatile int STALE = 0;",
           "public volatile boolean closed;", "public boolean answered;", "public String via;", "public String tcap;", "public long seq;", "public long base;",
           "public String tok;", "public boolean ok;", "public String last;", "public String ptok;", "public String cat;", "public String query;",
           "public String sel;", "public String selName;", "public int page;", "public int pages;", "public int amt;", "public String[] rowIds;",
           "public String[] cats;", "public long buyQ;", "public long buyCost;", "public boolean buyOk;", "public String buyWhy;", "public long sellQ;",
           "public long sellPay;", "public boolean sellOk;", "public String sellWhy;", "public int claims;", "public String[] ahQ;",
           "public int bamt;", "public boolean bok;", "public String bkey;", "public Object bepoch;", "public int blv;", "public boolean bcan;",
           "public long upUntil;", "public String bup;", "public long taxBp;",
           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;", "public int calls;"):
    F(mtab, _f)
C(mtab, r"""
public MarketTab(@PR@ pr, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.via = via;
  this.closed = false;
  this.answered = false;
  this.tcap = "";
  this.seq = 0L;
  this.base = System.nanoTime() & 0xffffffL;
  this.tok = "";
  this.ok = false;
  this.last = null;
  this.ptok = "";
  this.cat = "";
  this.query = "";
  this.sel = "";
  this.selName = "";
  this.page = 0;
  this.pages = 1;
  this.amt = 0;
  this.rowIds = new String[0];
  this.cats = new String[0];
  this.buyQ = 0L;
  this.buyCost = 0L;
  this.buyOk = false;
  this.buyWhy = "";
  this.sellQ = 0L;
  this.sellPay = 0L;
  this.taxBp = -1L;
  this.sellOk = false;
  this.sellWhy = "";
  this.claims = 0;
  this.ahQ = new String[0];
  this.bamt = 0;
  this.bok = false;
  this.bkey = null;
  this.bepoch = null;
  this.blv = -1;
  this.bcan = false;
  this.upUntil = 0L;
  this.bup = "";
  this.builds = 0;
  this.answers = 0;
  this.calls = 0;
}""")
'''
P.rep('''  this.calls = 0;
}""")
for _iface, _cls in ((T["SPH"], ihk)''', '''  this.calls = 0;
}""")
''' + MT_DATA + '''for _iface, _cls in ((T["SPH"], ihk)''')

# ---------- MarketTab.open BEFORE the pets screen's open (every caller below can reach it)
MT_OPEN = r'''# ---- 0.3.59: the MARKET SCREEN opens (the inventory's / skill page's / pets screen's Market tab); null = SkyyBazaar has no bazaar:fn:tab /
# tabact (an older SkyyBazaar) or it could not open = the caller opens today's Market page instead
M(mtab, r"""
public static @PKG@.MarketTab open(@REF@ ref, @ST@ st, @PR@ pr, String via) {
  if (@PKG@.InvCraft.fn("bazaar:fn:tab") == null || @PKG@.InvCraft.fn("bazaar:fn:tabact") == null) return null;
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  @PKG@.MarketTab pg = new @PKG@.MarketTab(pr, via);
  pg.pref = ref;
  pg.pst = st;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("market screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")
'''
P.rep('''# ---- 0.3.58: the PETS SCREEN opens (the inventory's / skill page's Pets tab, the pet + mount cards); null = SkyyPets has no pets:fn:tab /
''', MT_OPEN + '''# ---- 0.3.58: the PETS SCREEN opens (the inventory's / skill page's Pets tab, the pet + mount cards); null = SkyyPets has no pets:fn:tab /
''')
# the skill page's Market tab = this screen (else today's route, as before)
P.rep('''M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
  if (i == 2 && petsTab()) return;   // 0.3.58
''', '''# 0.3.59: the Market tab = the market screen (false = it could not open: today's route below)
M(skpg, r"""
public boolean marketTab() {
  @PKG@.MarketTab pg = null;
  try { pg = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "skill page"); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the market screen failed: " + t); }
  if (pg == null) return false;
  this.answered = true;
  if (!still()) finish("market");
  return true;
}""")
M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }
  if (i == 1) { say("You are on Skills - pick a skill on the right"); return; }
  if (i == 2 && petsTab()) return;   // 0.3.58
  if (i == 3 && marketTab()) return;   // 0.3.59
''')
# the pets screen's Market tab = this screen
P.rep('''  if (i == 2) { say("You are on Pets"); return; }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }''', '''  if (i == 2) { say("You are on Pets"); return; }
  if (i == 3) {   // 0.3.59: the market screen (else today's route below)
    @PKG@.MarketTab mt = null;
    try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "pets screen"); } catch (Throwable t) { mt = null; @PKG@.MenuUtil.warn("pets screen: the market screen failed: " + t); }
    if (mt != null) { if (!still()) finish("market"); return; }
  }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }''')

MT_JAVA = r'''# ================= 0.3.59 MarketTab: THE MARKET TAB = ONE SCREEN (approved market-page.png) =================
# Reads: bazaar:fn:tab (SkyyBazaar 0.2.6), bank:fn:panel (SkyyBank 0.1.17), ah:fn:find / ah:fn:view (SkyyAuctions). Every coin / item move through
# bazaar:fn:tabact (the profile key from the read) or bank:fn:move (the panel's key + epoch). Every bound click answers with ONE page packet.
M(mtab, r"""
public static String[] sp(String s, int n) { return s.split("\\|", n); }""")
M(mtab, r"""
public static int ni(String s, int d) { return @PKG@.InvPage.toInt(s, d); }""")
M(mtab, r"""
public static long nl(String s, long d) { return @PKG@.InvPage.toLong(s, d); }""")
M(mtab, r"""
public static String money(long v) { return v < 0L ? "-" : @PKG@.MenuUtil.fmt(v); }""")
M(mtab, r"""
public static String col(String hex, String t) { return "<color is=" + String.valueOf((char) 34) + hex + String.valueOf((char) 34) + ">" + t + "</color>"; }""")
M(mtab, r"""
public static String clean(String q) {
  if (q == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < q.length() && sb.length() < 40; i++) {
    char c = q.charAt(i);
    if (c == '|' || c < 32 || c > 126) continue;
    sb.append(c);
  }
  return sb.toString().trim();
}""")
M(mtab, r"""
public Object call(String key, Object arg) {
  java.util.function.Function f = @PKG@.InvCraft.fn(key);
  if (f == null) return null;
  try { return f.apply(arg); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: " + key + " failed: " + t); return null; }
}""")
M(mtab, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyyMtabCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(mtab, r"""
public void finish(String why) { this.closed = true; }""")
M(mtab, r"""
public void shut() { finish("closed"); this.close(); }""")
M(mtab, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(mtab, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.answers = this.answers + 1;
  this.rebuild();
}""")
# a grid cell: a NEW ItemStack(id, qty) without metadata, only for ids the server knows (else the name + tooltip alone)
M(mtab, r"""
public static @IGS@ cell(String id, int qty, String name, String desc) {
  @IGS@ g = new @IGS@();
  if (id != null && id.length() > 0 && id.length() < 120 && @PKG@.InvPage.known(id)) g.setItemStack(new @IS@(id, qty < 1 ? 1 : (qty > 999 ? 999 : qty)));
  if (name != null && name.length() > 0) g.setName(name);
  if (desc != null && desc.length() > 0) g.setDescription(desc);
  return g;
}""")
M(mtab, r"""
public static void hold(@UCB@ b, String base, int n, int which, String text) {
  for (int k = 0; k < n; k++) {
    b.set("#" + base + k + ".Text", text == null ? "" : text);
    b.set("#" + base + k + ".Visible", k == which);
  }
}""")
# fix tab3: the rarity frame round an icon (#<base>F1..F6 behind the grid; 0 / out of range = none)
M(mtab, r"""
public static void frame(@UCB@ b, String base, int r) {
  for (int k = 1; k <= 6; k++) b.set("#" + base + "F" + k + ".Visible", k == r);
}""")
M(mtab, r"""
public static java.util.ArrayList one(@IGS@ g) { java.util.ArrayList l = new java.util.ArrayList(); l.add(g); return l; }""")
M(mtab, r"""
public static int rar(String s) { int r = ni(s, 0); return r < 0 || r > 6 ? 0 : r; }""")
# the Style Guide 15 item tooltip: the name in its rarity colour, the tier tag, the prices gold, you have, the yellow click footer
M(mtab, r"""
public static String tip(String name, int r, String tag, long buy, long sell, long have, String foot) {
  String nl = String.valueOf((char) 10);
  StringBuilder sb = new StringBuilder();
  sb.append(col(r > 0 ? @PKG@.MarketTabData.RCOL[r] : @PKG@.MarketTabData.SOFT, name));
  if (tag != null && tag.length() > 0) sb.append(nl).append(col(@PKG@.MarketTabData.TAGCOL, tag));
  sb.append(nl).append(nl);
  sb.append(col(@PKG@.MarketTabData.SOFT, "Buy now  ")).append(col(@PKG@.MarketTabData.GOLD, buy > 0L ? money(buy) + " each" : "no price"));
  sb.append(nl).append(col(@PKG@.MarketTabData.SOFT, "Sell now  ")).append(col(@PKG@.MarketTabData.GOLD, sell > 0L ? money(sell) + " each" : "no price"));
  if (have >= 0L) sb.append(nl).append(col(@PKG@.MarketTabData.SOFT, "You have  ")).append(col(@PKG@.MarketTabData.GOLD, money(have)));
  if (foot != null && foot.length() > 0) sb.append(nl).append(nl).append(col(@PKG@.MarketTabData.FOOT, foot));
  return sb.toString();
}""")
# the rail: the Bazaar tabs (appended at run time; the open one in the selected tab look; a search = none selected)
M(mtab, r"""
public void fillRail(@UCB@ b, @UEB@ ev, java.util.ArrayList ks) {
  int n = ks.size() < @PKG@.MarketTabData.CATN ? ks.size() : @PKG@.MarketTabData.CATN;
  this.cats = new String[n];
  boolean searching = this.query.length() > 0;
  for (int i = 0; i < n; i++) {
    String[] f = (String[]) ks.get(i);
    String c = f.length > 1 ? f[1] : "";
    this.cats[i] = c;
    boolean on = !searching && c.equals(this.cat);
    b.appendInline("#SkyyMtabCats", @PKG@.MarketTabData.CAT.replace("{I}", "Kt" + i).replace("{S}", on ? @PKG@.MarketTabData.ST_CATSEL : @PKG@.MarketTabData.ST_CAT));
    b.set("#SkyyMtabKt" + i + ".Text", @PKG@.MenuUtil.clip(c, 22));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabKt" + i, @EVD@.of("a", "cat:" + i));
  }
  if (this.query.length() > 0) b.set("#SkyyMtabQ.Value", this.query);
  String qk = String.valueOf((char) 64) + "Q";
  ev.addEventBinding(@BT@.Validating, "#SkyyMtabQ", @EVD@.of("a", "find").append(qk, "#SkyyMtabQ.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabFind", @EVD@.of("a", "find").append(qk, "#SkyyMtabQ.Value"));
}""")
# the tab's items (r|id|name|rar|tag|buy|sell|have), MT_RN rows; hd = the read's header
M(mtab, r"""
public void fillList(@UCB@ b, @UEB@ ev, java.util.ArrayList rs, String[] hd) {
  int n = @PKG@.MarketTabData.RN;
  int m = rs.size() < n ? rs.size() : n;
  this.rowIds = new String[m];
  this.page = ni(hd[3], 0);
  this.pages = ni(hd[4], 1);
  if (this.pages < 1) this.pages = 1;
  boolean searching = "1".equals(hd[6]);
  if (!searching && hd[2].length() > 0) this.cat = hd[2];
  b.set("#SkyyMtabLt.Text", searching ? "SEARCH  " + @PKG@.MenuUtil.clip(this.query, 24).toUpperCase() : this.cat.toUpperCase());
  b.set("#SkyyMtabPg.Text", "Page " + (this.page + 1) + " / " + this.pages);
  b.set("#SkyyMtabLn.Text", ni(hd[5], 0) == 0 ? (searching ? "Nothing matches - try another word" : "Nothing in this tab") : hd[5] + " items");
  for (int i = 0; i < n; i++) {
    String r = "SkyyMtabR" + i;
    if (i >= m) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) rs.get(i);
    this.rowIds[i] = f[1];
    long by = nl(f[5], -1L), sl = nl(f[6], -1L), hv = nl(f[7], 0L);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", one(cell(f[1], 1, f[2], tip(f[2], rar(f[3]), f[4], by, sl, hv, "Click: select it"))));
    frame(b, r + "I", rar(f[3]));
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip((f[1].equals(this.sel) ? "> " : "") + f[2], 26));
    b.set("#" + r + "T.Text", f[4]);
    b.set("#" + r + "B.Text", by > 0L ? money(by) : "-");
    b.set("#" + r + "S.Text", sl > 0L ? money(sl) : "-");
    b.set("#" + r + "H.Text", money(hv));
    ev.addEventBinding(@BT@.SlotClicking, "#" + r + "I", @EVD@.of("a", "rs:" + i).append("t", this.tok), false);
    ev.addEventBinding(@BT@.Activating, "#" + r + "Go", @EVD@.of("a", "rs:" + i).append("t", this.tok));
  }
}""")
# fix tab3: the sell total says it is AFTER the Bazaar's seller tax on order fills (SkyyBazaar's orders.taxPct; BzFill.quote takes it off)
M(mtab, r"""
public String taxNote() {
  long t = this.taxBp;
  if (t <= 0L || t > 1000L) return "";
  String s = String.valueOf(t / 100L);
  long f = t % 100L;
  if (f > 0L) {
    s = s + "." + (f < 10L ? "0" : "") + f;
    if (s.endsWith("0")) s = s.substring(0, s.length() - 1);
  }
  return "  (after the " + s + String.valueOf((char) 37) + " tax on order fills)";
}""")
# the selected item (d|id|name|rar|tag|buy|sell|have|void|stack|bid|ask|afford|room|chip) + its priced chip (q|bq|bc|bw|sq|sv|sw)
M(mtab, r"""
public void fillSel(@UCB@ b, @UEB@ ev, String[] d, String[] q) {
  boolean on = d != null && d.length >= 15;
  this.sel = on ? d[1] : "";
  this.selName = on ? d[2] : "";
  long b1 = on ? nl(d[5], -1L) : -1L, s1 = on ? nl(d[6], -1L) : -1L, hv = on ? nl(d[7], 0L) : 0L, vd = on ? nl(d[8], 0L) : 0L;
  b.set("#SkyyMtabSI.Slots", one(on ? cell(d[1], 1, d[2], tip(d[2], rar(d[3]), d[4], b1, s1, hv, "")) : new @IGS@()));
  hold(b, "SkyyMtabSN", 7, on ? rar(d[3]) : 0, on ? d[2] : "Pick an item");
  frame(b, "SkyyMtabSI", on ? rar(d[3]) : 0);
  b.set("#SkyyMtabSt.Text", !on ? "" : (d[4].length() > 0 ? d[4] + "    " : "") + "You have " + money(hv) + (vd > 0L ? "  (" + money(vd) + " in the Void)" : ""));
  long bid = on ? nl(d[10], 0L) : 0L, ask = on ? nl(d[11], 0L) : 0L;
  b.set("#SkyyMtabSb.Text", !on ? "" : (bid > 0L ? "Best buy order " + money(bid) : "No buy orders yet") + "   -   " + (ask > 0L ? "lowest sell offer " + money(ask) : "no sell offers yet"));
  b.set("#SkyyMtabBuy.Text", on && b1 > 0L ? "BUY NOW  -  " + money(b1) + " each" : "BUY NOW");
  b.set("#SkyyMtabSell.Text", on && s1 > 0L ? "SELL NOW  -  " + money(s1) + " each" : "SELL NOW");
  int stk = on ? ni(d[9], 64) : 64;
  long aff = on ? nl(d[12], -1L) : -1L;
  for (int i = 0; i < 3; i++) {
    boolean sel = i == this.amt;
    String lb = i == 0 ? "1" : (i == 1 ? String.valueOf(stk) : "All");
    b.appendInline("#SkyyMtabAm", @PKG@.MarketTabData.CHIP.replace("{I}", "Am" + i).replace("{W}", String.valueOf(@PKG@.MarketTabData.CHW))
        .replace("{S}", sel ? @PKG@.MarketTabData.ST_CHSEL : @PKG@.MarketTabData.ST_CH));
    b.set("#SkyyMtabAm" + i + ".Text", lb);
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabAm" + i, @EVD@.of("a", "amt:" + i));
  }
  boolean qon = on && q != null && q.length >= 7;
  this.buyQ = qon ? nl(q[1], 0L) : 0L;
  this.buyCost = qon ? nl(q[2], 0L) : 0L;
  this.buyWhy = qon ? q[3] : "Pick an item first";
  this.buyOk = qon && this.buyWhy.length() == 0 && this.buyQ > 0L && this.buyCost > 0L;
  this.sellQ = qon ? nl(q[4], 0L) : 0L;
  this.sellPay = qon ? nl(q[5], 0L) : 0L;
  this.sellWhy = qon ? q[6] : "Pick an item first";
  this.sellOk = qon && this.sellWhy.length() == 0 && this.sellQ > 0L && this.sellPay > 0L;
  hold(b, "SkyyMtabTb", 2, this.buyOk ? 0 : 1, !on ? "" : (this.buyOk ? "Buy now: " + money(this.buyQ) + " for " + money(this.buyCost) + " coins" : "Buy now: " + this.buyWhy));
  hold(b, "SkyyMtabTs", 2, this.sellOk ? 0 : 1, !on ? "" : (this.sellOk ? "Sell now: " + money(this.sellQ) + " for " + money(this.sellPay) + " coins" + taxNote() : "Sell now: " + this.sellWhy));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabBuy", @EVD@.of("a", "buy").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabSell", @EVD@.of("a", "sell").append("t", this.tok));
}""")
# YOUR ORDERS (o|side|item|name|qty|filled|price) + Claim all (m|coins|items|rows)
M(mtab, r"""
public void fillOrders(@UCB@ b, @UEB@ ev, java.util.ArrayList os, String[] m, String[] hd) {
  int no = ni(hd[9], 0);
  b.set("#SkyyMtabOh.Text", "YOUR ORDERS  " + no);
  long cw = m != null && m.length >= 4 ? nl(m[1], 0L) : 0L, iw = m != null && m.length >= 4 ? nl(m[2], 0L) : 0L;
  this.claims = m != null && m.length >= 4 ? ni(m[3], 0) : 0;
  b.set("#SkyyMtabCl.Text", this.claims <= 0 ? "" : "Ready: " + (cw > 0L ? money(cw) + " coins" : "") + (cw > 0L && iw > 0L ? " + " : "") + (iw > 0L ? money(iw) + " items" : ""));
  b.set("#SkyyMtabClaim.Visible", this.claims > 0);
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabClaim", @EVD@.of("a", "claim").append("t", this.tok));
  for (int i = 0; i < @PKG@.MarketTabData.ON; i++) {
    String t = "";
    if (i < os.size()) {
      String[] f = (String[]) os.get(i);
      if (f.length >= 7) t = ("0".equals(f[1]) ? "Buy order  " : "Sell offer  ") + money(nl(f[4], 0L)) + " " + @PKG@.MenuUtil.clip(f[3], 24) + " at " + money(nl(f[6], 0L)) + " each   -   " + money(nl(f[5], 0L)) + " / " + money(nl(f[4], 0L)) + " filled";
    } else if (i == 0 && no == 0) t = "No open orders - place them on the Bazaar page (Buy order / Sell offer).";
    else if (i == os.size() && no > os.size()) t = (no - os.size()) + " more on the Bazaar page";
    b.set("#SkyyMtabO" + i + ".Text", t);
  }
}""")
# the AUCTION HOUSE card: claims waiting (ah:fn:view apply(UUID) -> Long), the search's auctions (ah:fn:find), the three views
M(mtab, r"""
public void fillAh(@UCB@ b, @UEB@ ev) {
  boolean on = @PKG@.InvCraft.fn("ah:fn:view") != null || @PKG@.InvCraft.fn("ah:fn:open") != null;
  java.util.UUID u = this.playerRef.getUuid();
  Object c = null;
  if (on) c = call("ah:fn:view", u);
  long cl = c instanceof Number ? ((Number) c).longValue() : 0L;
  b.set("#SkyyMtabAc.Text", !on ? "" : (cl > 0L ? cl + " to claim - Your listings" : ""));
  java.util.ArrayList rows = new java.util.ArrayList();
  if (on && this.query.length() > 0) {
    Object r = call("ah:fn:find", this.query);
    if (r instanceof java.util.List) {
      java.util.List l = (java.util.List) r;
      for (int i = 0; i < l.size() && rows.size() < @PKG@.MarketTabData.AN; i++) {
        Object o = l.get(i);
        if (!(o instanceof Object[])) continue;
        Object[] e = (Object[]) o;
        if (e.length < 7 || !(e[0] instanceof String) || !(e[1] instanceof String) || !(e[2] instanceof Number) || !(e[3] instanceof Number) || !(e[6] instanceof String)) continue;
        rows.add(e);
      }
    }
  }
  b.set("#SkyyMtabAs.Text", !on ? "The Auction House is not on this server right now." : (this.query.length() == 0 ? @PKG@.MarketTabData.AHNONE
      : (rows.size() == 0 ? "No auctions for " + @PKG@.MenuUtil.clip(this.query, 24) + " right now." : "Auctions for " + @PKG@.MenuUtil.clip(this.query, 24) + ":")));
  this.ahQ = new String[rows.size()];
  for (int i = 0; i < @PKG@.MarketTabData.AN; i++) {
    String a = "SkyyMtabA" + i;
    if (i >= rows.size()) { b.set("#" + a + ".Visible", false); continue; }
    Object[] e = (Object[]) rows.get(i);
    String id = (String) e[0], nm = (String) e[1];
    this.ahQ[i] = nm;
    int n = ((Number) e[2]).intValue();
    long low = ((Number) e[3]).longValue();
    b.set("#" + a + ".Visible", true);
    b.set("#" + a + "I.Slots", one(cell(id, 1, nm, col(@PKG@.MarketTabData.SOFT, nm) + String.valueOf((char) 10) + String.valueOf((char) 10)
        + col(@PKG@.MarketTabData.GOLD, n + " listed, from " + money(low) + " each") + String.valueOf((char) 10) + String.valueOf((char) 10) + col(@PKG@.MarketTabData.FOOT, "Open: the Auction House on it"))));
    b.set("#" + a + "N.Text", @PKG@.MenuUtil.clip(nm, 34));
    b.set("#" + a + "S.Text", n + " listed  -  from " + money(low) + " each  -  ends " + @PKG@.MenuUtil.clip((String) e[6], 12));
    ev.addEventBinding(@BT@.Activating, "#" + a + "Go", @EVD@.of("a", "ahr:" + i).append("t", this.tok));
  }
  b.set("#SkyyMtabMn.Text", @PKG@.HubBar.get("hub:tab:market:merchants") instanceof Object[] ? "" : "Merchants are not on this server right now.");
}""")
# the BANK panel: bank:fn:panel apply(UUID) -> Object[13] (SkyyBank 0.1.17: ok, profile, purse, bank, rate, next, gain, its colour, key, epoch,
# the level line, Integer level, Boolean another level can be bought); "locked" = the lock text in [1]
M(mtab, r"""
public static long capOf(String line) {
  if (line == null) return -1L;
  int i = line.indexOf("holds up to ");
  if (i < 0) return -1L;
  int j = line.indexOf(" coins", i);
  if (j < 0) return -1L;
  return nl(line.substring(i + 12, j).replace(",", "").trim(), -1L);
}""")
M(mtab, r"""
public String fillBank(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  Object o = null;
  if (@PKG@.InvCraft.fn("bank:fn:panel") != null) o = call("bank:fn:panel", u);
  Object[] r = null;
  if (o instanceof Object[]) r = (Object[]) o;
  this.bok = r != null && r.length >= 10 && "ok".equals(r[0]);
  this.bkey = null;
  this.bepoch = null;
  if (this.bok && r[8] instanceof String) this.bkey = (String) r[8];
  if (this.bok) this.bepoch = r[9];
  this.blv = this.bok && r.length >= 13 && r[11] instanceof Number ? ((Number) r[11]).intValue() : -1;
  this.bcan = this.bok && r.length >= 13 && Boolean.TRUE.equals(r[12]) && this.blv > 0;
  for (int i = 0; i < 5; i++) {
    boolean sel = i == this.bamt;
    b.appendInline("#SkyyMtabBa", @PKG@.MarketTabData.CHIP.replace("{I}", "Bc" + i).replace("{W}", String.valueOf(@PKG@.MarketTabData.BCW))
        .replace("{S}", sel ? @PKG@.MarketTabData.ST_CHSEL : @PKG@.MarketTabData.ST_CH));
    b.set("#SkyyMtabBc" + i + ".Text", @PKG@.MarketTabData.BAMTL[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabBc" + i, @EVD@.of("a", "bamt:" + i));
  }
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabDep", @EVD@.of("a", "dep").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabWd", @EVD@.of("a", "wd").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabUpg", @EVD@.of("a", "up").append("t", this.tok));
  b.set("#SkyyMtabDep.Visible", this.bok);
  b.set("#SkyyMtabWd.Visible", this.bok);
  b.set("#SkyyMtabUpg.Visible", this.bcan);
  if (!this.bok) {
    String why = @PKG@.InvCraft.fn("bank:fn:panel") == null ? "The bank is not on this server right now." : "Your bank could not be read right now - try again in a moment.";
    if (r != null && "locked".equals(r[0]) && r.length > 1 && r[1] instanceof String) why = (String) r[1];
    b.set("#SkyyMtabBv.Text", "");
    b.set("#SkyyMtabBs.Text", @PKG@.MenuUtil.clip(why, 110));
    b.set("#SkyyMtabBl.Text", "");
    hold(b, "SkyyMtabBg", 3, 2, "");
    this.bup = "";
    return "";
  }
  String lvl = r.length >= 11 && r[10] instanceof String ? (String) r[10] : "";
  int li = lvl.indexOf("Bank Lv ");
  if (li > 0) lvl = lvl.substring(li);
  b.set("#SkyyMtabBl.Text", this.blv > 0 ? "Bank Lv " + this.blv : "");
  b.set("#SkyyMtabBv.Text", String.valueOf(r[3]));
  long cap = capOf(lvl);
  long bal = nl(String.valueOf(r[3]).replace(",", ""), -1L);
  b.set("#SkyyMtabBs.Text", "in the bank" + (cap > 0L ? "  -  holds up to " + money(cap) : "") + "     Purse  " + String.valueOf(r[2]));
  int w = cap > 0L && bal >= 0L ? @PKG@.InvPage.barW(bal, cap, @PKG@.MarketTabData.BAR) : 0;
  if (w > 0) b.appendInline("#SkyyMtabBb", @PKG@.MarketTabData.FILL.replace("{W}", String.valueOf(w)));
  b.set("#SkyyMtabBi.Text", @PKG@.MenuUtil.clip(String.valueOf(r[4]), 110));
  b.set("#SkyyMtabBn.Text", @PKG@.MenuUtil.clip(String.valueOf(r[5]), 110));
  String gc = String.valueOf(r[7]);
  hold(b, "SkyyMtabBg", 3, gc.equalsIgnoreCase(@PKG@.MarketTabData.GOK) ? 0 : (gc.equalsIgnoreCase(@PKG@.MarketTabData.GBAD) ? 1 : 2), @PKG@.MenuUtil.clip(String.valueOf(r[6]), 110));
  int dot = lvl.indexOf(". Upgrade");
  String l1 = dot > 0 ? lvl.substring(0, dot + 1) : lvl;
  String l2 = dot > 0 ? lvl.substring(dot + 2) : "";
  this.bup = l2;
  b.set("#SkyyMtabL1.Text", @PKG@.MenuUtil.clip(l1, 110));
  b.set("#SkyyMtabL2.Text", @PKG@.MenuUtil.clip(l2, 110));
  b.set("#SkyyMtabUpg.Text", this.upUntil > System.currentTimeMillis() ? "Press again" : "Upgrade");
  return String.valueOf(r[3]);
}""")
M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.MarketTabData.LP[i];
    String y = @PKG@.MarketTabData.LB[i];
    if (k == 'A') b.appendInline(x.length() == 0 ? (String) null : x, y);
    else if (k == 'S') b.set(x, y);
    else if (k == 'E') ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
  }
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  this.builds = this.builds + 1;
  java.util.UUID u = this.playerRef.getUuid();
  String bank = "";
  try { bank = fillBank(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the bank failed: " + t); }
  long c = -1L;
  try { c = @PKG@.MenuUtil.purse(u); } catch (Throwable t) { c = -1L; }
  b.set("#SkyyMtabCoins.Text", (c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c)) + (bank.length() > 0 ? "    Bank " + bank : ""));
  try { fillAh(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the auction card failed: " + t); }
  Object o = call("bazaar:fn:tab", new Object[] { u, this.cat, this.query, this.sel, Integer.valueOf(this.page), Integer.valueOf(@PKG@.MarketTabData.RN), Integer.valueOf(this.amt) });
  this.calls = this.calls + 1;
  String s = o instanceof String ? (String) o : null;
  this.last = s;
  this.ok = s != null && s.startsWith("ok|");
  String[] ls = this.ok ? s.split("\n") : new String[0];
  String[] hd = this.ok ? sp(ls[0], 13) : new String[0];
  if (hd.length < 12) this.ok = false;
  if (!this.ok) {
    this.ptok = "";
    this.rowIds = new String[0];
    this.cats = new String[0];
    this.buyOk = false;
    this.sellOk = false;
    this.claims = 0;
    for (int i = 0; i < @PKG@.MarketTabData.RN; i++) b.set("#SkyyMtabR" + i + ".Visible", false);
    b.set("#SkyyMtabLt.Text", "BAZAAR");
    b.set("#SkyyMtabLn.Text", "The Bazaar could not be read right now - try again in a moment, or open the Full page.");
    hold(b, "SkyyMtabSN", 7, 0, "The Bazaar is not ready");
    frame(b, "SkyyMtabSI", 0);
    if (this.tcap.length() == 0) this.tcap = "The Bazaar is not ready yet";
    b.set("#SkyyMtabCap.Text", this.tcap);
    return;
  }
  this.ptok = hd[1];
  this.taxBp = hd.length >= 13 ? nl(hd[12], -1L) : -1L;   // fix tab3: SkyyBazaar's seller tax on order fills (1/100 pct; older = none)
  java.util.ArrayList ks = new java.util.ArrayList(), rs = new java.util.ArrayList(), os = new java.util.ArrayList();
  String[] d = null, q = null, m = null;
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) ks.add(sp(l, 2));
    else if (l.startsWith("r|")) rs.add(sp(l, 8));
    else if (l.startsWith("d|")) d = sp(l, 15);
    else if (l.startsWith("q|")) q = sp(l, 7);
    else if (l.startsWith("o|")) os.add(sp(l, 7));
    else if (l.startsWith("m|")) m = sp(l, 4);
  }
  if (d != null && d.length >= 15) this.sel = d[1];      // the row mark below knows the selection of THIS read
  if (this.tcap.length() > 0) b.set("#SkyyMtabCap.Text", this.tcap);
  else if ("0".equals(hd[7])) b.set("#SkyyMtabCap.Text", "Trading is off - the coin bank (SkyyCoins) is not loaded");
  else if ("1".equals(hd[11])) b.set("#SkyyMtabCap.Text", "The Bazaar order book is paused - an admin has been told; buy / sell now still work");
  try { fillRail(b, ev, ks); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the rail failed: " + t); }
  try { fillList(b, ev, rs, hd); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the items failed: " + t); }
  try { fillSel(b, ev, d, q); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the selected item failed: " + t); }
  try { fillOrders(b, ev, os, m, hd); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: your orders failed: " + t); }
}""")
# ---- the actions (each answers with ONE packet: a redraw, a caption, a page that replaces this one, or the close)
M(mtab, r"""
public void hub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    if (tab != null && tab.length() > 0) r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("market screen: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
# a Function that opens another mod's page (TRUE = it opened); our page replaced = no packet of ours
M(mtab, r"""
public void opener(String key, Object arg, String hb, String tb, String label) {
  this.answered = true;
  Object r = null;
  if (@PKG@.InvCraft.fn(key) != null) r = call(key, arg);
  if (Boolean.TRUE.equals(r)) {
    if (!still()) { finish(key); return; }
    say("Opening " + label);
    return;
  }
  hub(hb, tb, label);
}""")
M(mtab, r"""
public void tabGo(int i) {
  this.answered = true;
  if (i == 0) {
    @PKG@.InvPage pg = null;
    try { pg = @PKG@.InvState.openAt(this.pref, this.pst, this.playerRef, "market screen", "c", -1); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("market screen: the inventory failed: " + t); }
    if (pg == null) { if (still()) say("The inventory could not open here"); return; }
    if (!still()) finish("inventory");
    return;
  }
  if (i == 1) {
    @PKG@.SkillPage sp = null;
    try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, @PKG@.SkillPage.lastOf(this.playerRef.getUuid()), "market screen"); } catch (Throwable t) { sp = null; @PKG@.MenuUtil.warn("market screen: the skill page failed: " + t); }
    if (sp == null) { hub(@PKG@.InvData.TAB_HUB[1], @PKG@.InvData.TAB_TAB[1], @PKG@.InvData.TAB_NAME[1]); return; }
    if (!still()) finish("skills");
    return;
  }
  if (i == 2) {
    @PKG@.PetsTab pt = null;
    try { pt = @PKG@.PetsTab.open(this.pref, this.pst, this.playerRef, "market screen"); } catch (Throwable t) { pt = null; @PKG@.MenuUtil.warn("market screen: the pets screen failed: " + t); }
    if (pt == null) { hub(@PKG@.InvData.TAB_HUB[2], @PKG@.InvData.TAB_TAB[2], @PKG@.InvData.TAB_NAME[2]); return; }
    if (!still()) finish("pets");
    return;
  }
  if (i == 3) { say("You are on Market"); return; }
  if (i < 0 || i >= @PKG@.InvData.TAB_NAME.length) { say("No such tab"); return; }
  hub(@PKG@.InvData.TAB_HUB[i], @PKG@.InvData.TAB_TAB[i], @PKG@.InvData.TAB_NAME[i]);
}""")
# one Bazaar action through bazaar:fn:tabact with the profile key of the last read
M(mtab, r"""
public void act(String op, String arg) {
  this.answered = true;
  Object o = call("bazaar:fn:tabact", new Object[] { this.playerRef.getUuid(), this.ptok, op, arg == null ? "" : arg });
  if (o == null) { say(@PKG@.InvCraft.fn("bazaar:fn:tabact") == null ? "The Bazaar is not on this server right now - nothing changed" : "That could not run here - nothing changed"); return; }
  this.tcap = @PKG@.InvPage.bare(String.valueOf(o));
  redraw();
}""")
# one bank move through bank:fn:move with the panel's profile key + epoch
M(mtab, r"""
public void bankMove(String op, String amount) {
  this.answered = true;
  if (!this.bok) { say("The bank is not ready - nothing was moved"); return; }
  Object o = call("bank:fn:move", new Object[] { this.playerRef.getUuid(), op, amount == null ? "" : amount, this.bkey, this.bepoch });
  if (o == null) { say(@PKG@.InvCraft.fn("bank:fn:move") == null ? "The bank is not on this server right now - nothing was moved" : "That could not run here - nothing was moved"); return; }
  this.tcap = @PKG@.InvPage.bare(String.valueOf(o));
  redraw();
}""")
M(mtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {
  String a = @PKG@.InvPage.val(d, "a");
  if (a == null) a = "";
  this.answered = false;
  try {
    if (this.closed) { this.answered = true; return; }
    this.pref = ref;
    this.pst = st;
    if (!a.equals("up")) this.upUntil = 0L;
    if (a.equals("close")) { this.answered = true; shut(); return; }
    if (a.startsWith("tab:")) { tabGo(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("full")) { hub("market", "bazaar", "the Bazaar page"); return; }
    if (a.equals("mer")) { hub("market", "merchants", "Merchants"); return; }
    if (a.equals("bank")) { hub("storage", "bank", "the Bank page"); return; }
    if (a.startsWith("ah:")) {
      String v = a.substring(3);
      if (!(v.equals("browse") || v.equals("create") || v.equals("manage"))) { say("Pick an Auction House button"); return; }
      opener("ah:fn:view", new Object[] { this.playerRef.getUuid(), v }, "market", "auctions", "the Auction House");
      return;
    }
    if (a.equals("order") || a.equals("offer")) {
      if (this.selName.length() == 0) { say("Pick an item first"); return; }
      opener("bazaar:fn:open", new Object[] { this.playerRef.getUuid(), this.selName }, "market", "bazaar", "the Bazaar page");
      return;
    }
    if (a.startsWith("cat:")) {
      int k = @PKG@.InvPage.toInt(a.substring(4), -1);
      if (k < 0 || k >= this.cats.length) { say("No such Bazaar tab"); return; }
      this.cat = this.cats[k];
      this.query = "";
      this.page = 0;
      this.sel = "";
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("find")) {
      this.query = clean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "Q"));
      this.page = 0;
      this.sel = "";
      this.tcap = this.query.length() == 0 ? "Type a word to search, then Find" : "";
      redraw();
      return;
    }
    if (a.equals("fclear")) { this.query = ""; this.page = 0; this.sel = ""; this.tcap = ""; redraw(); return; }
    if (a.startsWith("pg:")) {
      int dp = @PKG@.InvPage.toInt(a.substring(3), 0);
      int np = this.page + (dp < 0 ? -1 : 1);
      if (np < 0 || np >= this.pages) { say(np < 0 ? "This is the first page" : "This is the last page"); return; }
      this.page = np;
      this.sel = "";
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("amt:")) { int k = @PKG@.InvPage.toInt(a.substring(4), 0); this.amt = k < 0 || k > 2 ? 0 : k; this.tcap = ""; redraw(); return; }
    if (a.startsWith("bamt:")) { int k = @PKG@.InvPage.toInt(a.substring(5), 0); this.bamt = k < 0 || k > 4 ? 0 : k; this.tcap = ""; redraw(); return; }
    String t = @PKG@.InvPage.val(d, "t");
    if (t == null || !t.equals(this.tok)) {
      STALE = STALE + 1;
      this.tcap = "The page changed - here it is again. Nothing changed.";
      redraw();
      return;
    }
    if (a.startsWith("rs:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || k >= this.rowIds.length) { say("Nothing there"); return; }
      this.sel = this.rowIds[k];
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("ahr:")) {
      int k = @PKG@.InvPage.toInt(a.substring(4), -1);
      if (k < 0 || k >= this.ahQ.length) { say("Nothing there"); return; }
      opener("ah:fn:open", new Object[] { this.playerRef.getUuid(), this.ahQ[k] }, "market", "auctions", "the Auction House");
      return;
    }
    if (a.equals("dep") || a.equals("wd")) {
      String am = @PKG@.MarketTabData.BAMT[this.bamt];
      boolean all = am.equals("all");
      bankMove(a.equals("dep") ? (all ? "depall" : "deposit") : (all ? "wdall" : "withdraw"), all ? "" : am);
      return;
    }
    if (a.equals("up")) {
      if (!this.bok || !this.bcan) { this.upUntil = 0L; say(this.bok ? "Your bank is at its top level" : "The bank is not ready - nothing was charged"); return; }
      long now = System.currentTimeMillis();
      if (now > this.upUntil) {
        this.upUntil = now + 10000L;
        this.tcap = (this.bup.length() > 0 ? @PKG@.MenuUtil.clip(this.bup, 90) + " - " : "") + "press Upgrade again within 10 s to pay";
        redraw();
        return;
      }
      this.upUntil = 0L;
      bankMove("upgrade", String.valueOf(this.blv));
      return;
    }
    if (!this.ok) { this.tcap = "The Bazaar is not ready yet - nothing changed"; redraw(); return; }
    if (a.equals("buy")) {
      if (this.sel.length() == 0) { say("Pick an item first"); return; }
      if (!this.buyOk) { say("Buy now: " + this.buyWhy); return; }
      act("buy", this.sel + "|" + this.buyQ + "|" + this.buyCost);
      return;
    }
    if (a.equals("sell")) {
      if (this.sel.length() == 0) { say("Pick an item first"); return; }
      if (!this.sellOk) { say("Sell now: " + this.sellWhy); return; }
      act("sell", this.sel + "|" + this.sellQ + "|" + this.sellPay);
      return;
    }
    if (a.equals("claim")) {
      if (this.claims <= 0) { say("Nothing to claim"); return; }
      act("claim", "");
      return;
    }
    say("Pick an item");
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("market screen event '" + a + "' failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.MenuUtil.warn("market screen: the empty answer failed: " + t2); }
    }
  }
}""")
M(mtab, r"""
public void onDismiss(@REF@ ref, @ST@ st) { finish("dismissed"); }""")
'''
P.rep('''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''', MT_JAVA + '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''')
# Tab while the market screen is open = it closes
P.rep('''  if (sp0 instanceof @PKG@.PetsTab && !((@PKG@.PetsTab) sp0).closed) { ((@PKG@.PetsTab) sp0).shut(); return; }   // 0.3.58
''', '''  if (sp0 instanceof @PKG@.PetsTab && !((@PKG@.PetsTab) sp0).closed) { ((@PKG@.PetsTab) sp0).shut(); return; }   // 0.3.58
  if (sp0 instanceof @PKG@.MarketTab && !((@PKG@.MarketTab) sp0).closed) { ((@PKG@.MarketTab) sp0).shut(); return; }   // 0.3.59
''')
# ---------- the inventory: the Market tab opens the market screen
P.rep('''M(ipg, r"""
public void goTab(int i) {''', '''# 0.3.59: the Market tab = the market screen (false = it could not open / no bazaar:fn:tab: today's Market route below)
M(ipg, r"""
public boolean openMarket() {
  @PKG@.MarketTab mt = null;
  try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "inventory"); } catch (Throwable t) { mt = null; @PKG@.MenuUtil.warn("inventory: the market screen failed: " + t); }
  if (mt == null) return false;
  this.answered = true;
  if (!still()) finish("market");
  return true;
}""")
M(ipg, r"""
public void goTab(int i) {''')
P.rep('''  if (i == 2 && openPets()) return;   // 0.3.58: the pets screen (else today's Pets page below)
''', '''  if (i == 2 && openPets()) return;   // 0.3.58: the pets screen (else today's Pets page below)
  if (i == 3 && openMarket()) return;   // 0.3.59: the market screen (else today's Market route below)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.59: no new system / command"
_i = P.s.index
assert _i("public static @PKG@.MarketTab open(") < _i("public static @PKG@.PetsTab open(") < _i("public boolean marketTab()")
assert _i("public MarketTab(@PR@ pr, String via)") < _i("public static @PKG@.MarketTab open(")
assert _i("public static @PKG@.MarketTab open(") < _i("try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, \"pets screen\")")
assert _i("public void shut() { finish(\"closed\"); this.close(); }\"\"\")\nM(mtab") < _i("if (sp0 instanceof @PKG@.MarketTab")
assert _i("public boolean openMarket()") < _i("public void goTab(int i)") and _i('F(mtd, "public static final String LK') < _i("public static @PKG@.MarketTab open(")
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.58 harness: every 0.3.58 check
# runs again on the 0.3.59 jar; + the TAB3 section)
T.rep('''"""Harness for SkyyMenu 0.3.58 (the Pets tab = one screen; tools/menu_0_3_58_patch.py).
''', '''"""Harness for SkyyMenu 0.3.59 (the Market tab = one screen; tools/menu_0_3_59_patch.py).
GENERATED by tools/menu_0_3_59_patch.py from the 0.3.58 harness (edit the patch, not this file): every 0.3.58 check runs again on the
0.3.59 jar, plus
  TAB3 (EXECUTED on Python stand-ins of SkyyBazaar 0.2.6 bazaar:fn:tab / tabact, SkyyBank 0.1.17 bank:fn:panel / move, SkyyAuctions ah:fn:view /
       find / open, bazaar:fn:open - a little market with a profile key, a purse, a bank, item counts; the real SkyyBazaar side runs in
       SkyyBazaar/test_skyybazaar_0.2.6.py):
       FALL    without bazaar:fn:tab / tabact the Market tab (inventory + skill page + pets screen) keeps today's route, never the screen
       OPEN    the inventory's / skill page's / pets screen's Market tab = the MARKET SCREEN (ONE page packet, the old page forgotten)
       PAGE    every part drawn: the rail tabs (the open one selected), the 7 item rows (tooltip with the rarity colour, tier tag, prices; no
               metadata, known ids only), the selected item (rarity variant, prices on the buttons, the chips, green / red totals), your
               orders + Claim all, the AH card (claims, a search's auctions), the bank (balance, purse, bar, interest, gain colour, chips,
               level lines, Upgrade only when another level can be bought); no scrolling
       ACT     tabs / search / clear / pages / chips (no bridge action), View / icon select, BUY NOW / SELL NOW (the read's profile key, the
               shown amount + total), Claim all, Deposit / Withdraw (each chip, All = depall / wdall, the panel's key + epoch), Upgrade (two
               presses), Buy order / Sell offer (bazaar:fn:open), AH Browse / New / Your listings / Open - each ONE page packet
       SAFE    a stale page token / a double click = no bridge call; a refusal (not enough coins / full inventory / profile changed) = the
               answer shown, nothing else; buy / sell refused up front when the read said why (no call); the read failing = the page still
               draws (bank + AH + Full page work), no Bazaar action without a call
       TABS    Inventory / Skills / Pets / World / Settings / Full page / Merchants / Bank page from the screen; the Tab key and X close it
The 0.3.58 harness text follows:
Harness for SkyyMenu 0.3.58 (the Pets tab = one screen; tools/menu_0_3_58_patch.py).
''')
T.rep('VERSION = "0.3.58"\nJAR', 'VERSION = "0.3.59"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.57.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.58.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.57.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.58.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_58_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_59_patch.py")')
T.rep('"scratch", "tab2", "menu"', '"scratch", "tab3", "menu"')
T.rep('ADDED = ["PetsTabData", "PetsTab"]   # 0.3.58: the pets screen\n', 'ADDED = ["MarketTabData", "MarketTab"]   # 0.3.59: the market screen\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.58:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.59: the Market tab opens the market screen (inventory + skill page + pets screen); Tab closes it
    "InvPage": ["+m openMarket", "~m goTab"],
    "InvState": ["~m tab"],
    "SkillPage": ["+m marketTab", "~m tabGo"],
    "PetsTab": ["~m tabGo"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.58"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.59"') == 1, "S VERSION")
    # 0.3.59: the market screen fits one 1080p screen, never scrolls, element budget
    K.check("0.3.59: the market screen fits one 1080p screen" in g and "0.3.59: the market screen never scrolls" in g,
            "TAB3 STATIC the build asserts the market screen fits 1080 (both rows sum to the body) and has no scrolling list")
    mp3_ = re.search(r"MT_ELEMENTS <= (\\d+)", g)
    K.check(mp3_ is not None and int(mp3_.group(1)) <= 800, "TAB3 STATIC the market screen's element budget assert is <= 800 (the ~1,600 client budget)")''')

HARNESS_TAB3 = r"""    # ---- TAB3 (0.3.59; Skyy 11-14 on the Market card "Bazaar, Auction House, Merchants, and the Bank, so the new bank mini-game lives here": "perfect."):
    # THE MARKET SCREEN
    MTB, MTD = JV("MarketTab"), JV("MarketTabData")
    uk3 = str(PK.pr.getUuid())
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:panel", "bank:fn:move", "ah:fn:view", "ah:fn:find", "ah:fn:open", "bazaar:fn:open", "pets:fn:tab", "pets:fn:tabact"):
        BR.remove(k_)
    CATS3 = ["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]
    PROD = [("Rock_Stone", "Stone", "Mining", 1, "T1 Stone", 6, 5), ("Wood_Oak_Trunk", "Oak Log", "Foraging", 1, "T1 Oak", 9, 8),
            ("Plant_Fruit_Apple", "Apple", "Farming", 2, "", 12, 10), ("Weapon_Sword_Iron", "Iron Sword", "Combat", 3, "T3 Iron", 400, 300)] + \
           [("Skyy_Fake_%d" % i_, "Ore %02d" % i_, "Mining", 2 + i_ % 5, "T%d Ore" % (2 + i_ % 5), 10 + i_, 8 + i_) for i_ in range(12)]
    MW = {"tok": "prof-A", "purse": 50000, "have": {"Rock_Stone": 30}, "reads": [], "acts": [], "conf": None, "full": False, "claims": 2,
          "bank": 120000, "bmoves": [], "bkey": "prof-A", "lv": 2, "can": True, "ahv": [], "aho": [], "bzo": [], "readNull": False, "tax": 125}

    def f_btab(o):
        a = list(o)
        MW["reads"].append([str(x) for x in a])
        if MW["readNull"]:
            return None
        cat, q, sel, page, per, amt = str(a[1]), str(a[2]), str(a[3]), int(a[4]), int(a[5]), int(a[6])
        if not q and cat not in CATS3:
            cat = CATS3[0]
        rows = [p for p in PROD if (q.lower() in p[1].lower() if q else p[2] == cat)]
        rows.sort(key=lambda p: (p[3], p[1].lower()))
        pages = max(1, (len(rows) + per - 1) // per)
        page = max(0, min(page, pages - 1))
        pg = rows[page * per:(page + 1) * per]
        if not [p for p in PROD if p[0] == sel]:
            sel = pg[0][0] if pg else ""
        L = ["ok|%s|%s|%d|%d|%d|%d|1|%d|1|%d|0" % (MW["tok"], "" if q else cat, page, pages, len(rows), 1 if q else 0, MW["purse"], MW["claims"])
             + ("" if MW["tax"] is None else "|%d" % MW["tax"])]
        L += ["k|" + c for c in CATS3]
        for p in pg:
            L.append("r|%s|%s|%d|%s|%d|%d|%d" % (p[0], p[1], p[3], p[4], p[5], p[6], MW["have"].get(p[0], 0)))
        if sel:
            p = [x for x in PROD if x[0] == sel][0]
            hv = MW["have"].get(sel, 0)
            L.append("d|%s|%s|%d|%s|%d|%d|%d|4|64|%d|%d|%d|36|%d" % (p[0], p[1], p[3], p[4], p[5], p[6], hv, p[6] + 1, p[5] - 1, MW["purse"] // p[5], amt))
            bq = 1 if amt == 0 else (64 if amt == 1 else MW["purse"] // p[5])
            bw = "Your inventory is full" if MW["full"] else ("Not enough coins" if bq * p[5] > MW["purse"] else "")
            sq = 1 if amt == 0 else (64 if amt == 1 else hv)
            sw = "You have none to sell" if hv <= 0 else ("You have %d - pick All" % hv if sq > hv else "")
            L.append("q|%d|%d|%s|%d|%d|%s" % (bq, bq * p[5] if not bw else 0, bw, sq, sq * p[6] if not sw else 0, sw))
        L += ["o|0|Rock_Stone|Stone|640|412|5", "o|1|Wood_Oak_Trunk|Oak Log|128|128|9"]
        L.append("m|377600|12|%d" % MW["claims"])
        return "\n".join(L)

    def f_bact(o):
        a = [str(x) for x in list(o)]
        MW["acts"].append(a)
        u_, tok, op, arg = a[0], a[1], a[2], a[3]
        if tok != MW["tok"]:
            return "=Your profile changed - here is this profile's Bazaar. Nothing changed."
        if op == "claim":
            MW["claims"] = 0
            MW["purse"] += 377600
            return "+Claimed 377600 coins and 12 items."
        iid_, q_, shown = arg.split("|")
        q_, shown = int(q_), int(shown)
        if op == "buy":
            if MW["full"]:
                return "-Your inventory is full - nothing bought."
            if shown > MW["purse"]:
                return "-You cannot afford that."
            MW["purse"] -= shown
            MW["have"][iid_] = MW["have"].get(iid_, 0) + q_
            return "+Bought %d for %d coins." % (q_, shown)
        if op == "sell":
            if MW["have"].get(iid_, 0) < q_:
                return "-You only hold %d." % MW["have"].get(iid_, 0)
            MW["have"][iid_] -= q_
            MW["purse"] += shown
            return "+Sold %d for %d coins." % (q_, shown)
        return "-Unknown Bazaar action."

    def f_bpanel(o):
        r = OBJ([None] * 13)
        r[0], r[1], r[2], r[3] = "ok", "Main profile", "{:,}".format(MW["purse"]), "{:,}".format(MW["bank"])
        r[4], r[5], r[6], r[7] = "Interest every day at Bank Lv 2: 1.1% up to 100,000", "Next payout in 3h 12m", "+1,320 at the next payout", "#39f493"
        r[8], r[9] = MW["bkey"], JClass("java.lang.Long").valueOf(7)
        r[10] = "Main profile - Bank Lv %d of 10: holds up to 250,000 coins, 1.1%% interest. Upgrade to Lv %d: holds 500,000, 1.2%%, costs 75,000 coins from the bank." % (MW["lv"], MW["lv"] + 1)
        r[11] = JClass("java.lang.Integer").valueOf(MW["lv"])
        r[12] = TRUE if MW["can"] else JClass("java.lang.Boolean").FALSE
        return r

    def f_bmove(o):
        a = [x for x in list(o)]
        MW["bmoves"].append([str(x) if x is not None else None for x in a])
        if str(a[3]) != MW["bkey"]:
            return "=Your profile changed after this page opened, so nothing was moved."
        op, am = str(a[1]), str(a[2])
        n = {"1k": 1000, "10k": 10000, "100k": 100000, "1m": 1000000}.get(am, 0)
        if op == "depall":
            n = MW["purse"]
        if op == "wdall":
            n = MW["bank"]
        if op in ("deposit", "depall"):
            if n > MW["purse"]:
                return "-You only have %d coins in your purse - nothing was moved." % MW["purse"]
            MW["purse"] -= n
            MW["bank"] += n
            return "+Deposited %d coins." % n
        if op in ("withdraw", "wdall"):
            if n > MW["bank"]:
                return "-The bank holds %d - nothing was moved." % MW["bank"]
            MW["bank"] -= n
            MW["purse"] += n
            return "+Withdrew %d coins." % n
        if op == "upgrade":
            if am != str(MW["lv"]):
                return "=The level changed - nothing was charged."
            MW["bank"] -= 75000
            MW["lv"] += 1
            return "+Bank Lv %d!" % MW["lv"]
        return "=That button is not part of this page any more."

    def f_ahview(o):
        if str(o.getClass().getName()) == "java.util.UUID":
            return JClass("java.lang.Long").valueOf(3)
        MW["ahv"].append([str(x) for x in list(o)])
        return JClass("java.lang.Boolean").FALSE

    def f_ahfind(o):
        l_ = JClass("java.util.ArrayList")()
        if "stone" in str(o).lower():
            l_.add(OBJ(["Rock_Stone", "Fine Stone", JClass("java.lang.Integer").valueOf(3), JClass("java.lang.Long").valueOf(1200), JClass("java.lang.Long").valueOf(1200),
                        JClass("java.lang.Long").valueOf(1), "2m 10s", JClass("java.lang.Integer").valueOf(-1), "#ffffff"]))
            l_.add("junk row")
        return l_

    def f_ahopen(o):
        MW["aho"].append([str(x) for x in list(o)])
        return JClass("java.lang.Boolean").FALSE

    def f_bzopen(o):
        MW["bzo"].append([str(x) for x in list(o)])
        return JClass("java.lang.Boolean").FALSE

    def mt_ev(obj, what, n=1):
        f_ = len(E.sent(PK))
        PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, json.dumps(obj))
        ps_ = pages(PK, f_)
        K.eq(len(ps_), n, what + ": exactly %d page packet" % n)
        return ps_[0] if ps_ else None
    vis3 = lambda c_, k_: sval(c_, "#SkyyMtab%s.Visible" % k_) in (True, "true")
    cap3 = lambda p_: str(sval(cmap(p_), "#SkyyMtabCap.Text"))
    # FALL: no keys = today's route (never the screen)
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:3"}')
    cur_ = PK.pm.getCustomPage()
    K.check(len(pages(PK, f0_)) == 1 and (cur_ is None or str(cur_.getClass().getSimpleName()) != "MarketTab"), "TAB3 FALL no bazaar:fn:tab: the Market tab keeps today's route (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    K.check(MTB.open(PK.ref, PK.st, PK.pr, "test") is None, "TAB3 FALL MarketTab.open = null without the keys")
    if cur_ is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    BR.put("bazaar:fn:tab", Fn(f_btab))
    K.check(MTB.open(PK.ref, PK.st, PK.pr, "test") is None, "TAB3 FALL only one of the two keys = null (both are needed)")
    BR.put("bazaar:fn:tabact", Fn(f_bact))
    # OPEN from the inventory (no bank / AH keys yet: their cards say so)
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:3"}')
    pk_ = pages(PK, f0_)
    MS = PK.pm.getCustomPage()
    K.check(len(pk_) == 1 and MS is not None and str(MS.getClass().getSimpleName()) == "MarketTab" and bool(pgI_.closed) and ST.PAGES.get(PK.pr.getUuid()) is None,
            "TAB3 OPEN the inventory's Market tab = the MARKET SCREEN (ONE page packet), the inventory page forgotten")
    cm = cmap(pk_[0]) if pk_ else {}
    K.notes.append("TAB3 the screen's first packet: %d commands" % len(cmds_of(pk_[0])) if pk_ else "TAB3 no packet")
    K.check("not on this server" in str(sval(cm, "#SkyyMtabBs.Text")) and not vis3(cm, "Dep") and "not on this server" in str(sval(cm, "#SkyyMtabAs.Text")),
            "TAB3 FALL no bank / AH keys: their cards say so, no Deposit button")
    BR.put("bank:fn:panel", Fn(f_bpanel))
    BR.put("bank:fn:move", Fn(f_bmove))
    BR.put("ah:fn:view", Fn(f_ahview))
    BR.put("ah:fn:find", Fn(f_ahfind))
    BR.put("ah:fn:open", Fn(f_ahopen))
    BR.put("bazaar:fn:open", Fn(f_bzopen))
    p_ = mt_ev({"a": "amt:0"}, "TAB3 a redraw with every key")
    cm = cmap(p_)
    K.check(MW["reads"] and MW["reads"][-1][0] == uk3 and MW["reads"][-1][4:7] == ["0", str(int(MTD.RN)), "0"], "TAB3 OPEN the read: your UUID, page 0, 7 rows, chip 0 (%s)" % (MW["reads"][-1:],))
    # PAGE: the rail, the rows, the selected item, orders, AH, bank
    K.check(sval(cm, "#SkyyMtabKt0.Text") == "Mining" and sval(cm, "#SkyyMtabKt5.Text") == "Smithing" and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabKt0")
            and str(MTD.ST_CAT) in mk_of(p_, "SkyyMtabKt1"), "TAB3 PAGE the rail: the six Bazaar tabs, Mining selected (%s / %s / %s)" % (sval(cm, "#SkyyMtabKt0.Text"), sval(cm, "#SkyyMtabKt5.Text"), mk_of(p_, "SkyyMtabKt0")[:300]))
    K.check(sval(cm, "#SkyyMtabLt.Text") == "MINING" and sval(cm, "#SkyyMtabPg.Text") == "Page 1 / 2" and sval(cm, "#SkyyMtabLn.Text") == "13 items",
            "TAB3 PAGE the list header: the tab, page 1 / 2, 13 items")
    r0 = cm.get("#SkyyMtabR0I.Slots", "")
    K.notes.append("TAB3 row 0 cell: %s" % r0[:600])
    K.check(vis3(cm, "R0") and vis3(cm, "R6") and "Rock_Stone" in r0 and "#c9d2dd" in r0 and "T1 Stone" in r0 and "Click: select it" in r0 and "Buy now" in r0 and nometa(p_),
            "TAB3 PAGE a row's cell: the item, the Style Guide 15 tooltip (rarity-coloured name, tier tag, prices, footer), no metadata")
    K.check("Skyy_Fake_0" not in cm.get("#SkyyMtabR1I.Slots", "") and "Ore 00" in cm.get("#SkyyMtabR1I.Slots", ""), "TAB3 PAGE an id the server does not know = name + tooltip only (no ItemStack)")
    K.check(sval(cm, "#SkyyMtabR0N.Text") == "> Stone" and sval(cm, "#SkyyMtabR0T.Text") == "T1 Stone" and sval(cm, "#SkyyMtabR0B.Text") == "6" and sval(cm, "#SkyyMtabR0H.Text") == "30",
            "TAB3 PAGE a row: the selected mark, name, tier tag, buy, you have")
    K.check(vis3(cm, "SN1") and sval(cm, "#SkyyMtabSN1.Text") == "Stone" and sval(cm, "#SkyyMtabBuy.Text") == "BUY NOW  -  6 each" and sval(cm, "#SkyyMtabSell.Text") == "SELL NOW  -  5 each"
            and str(sval(cm, "#SkyyMtabSt.Text")).startswith("T1 Stone    You have 30  (4 in the Void)") and "Best buy order 6" in str(sval(cm, "#SkyyMtabSb.Text")),
            "TAB3 PAGE the selected item: the default = the first row, Common colour, prices on the buttons, tier + you have + the Void, best order / offer")
    K.check(sval(cm, "#SkyyMtabAm1.Text") == "64" and str(MTD.ST_CHSEL) in mk_of(p_, "SkyyMtabAm0") and vis3(cm, "Tb0") and sval(cm, "#SkyyMtabTb0.Text") == "Buy now: 1 for 6 coins"
            and sval(cm, "#SkyyMtabTs0.Text") == "Sell now: 1 for 5 coins  (after the 1.25% tax on order fills)",
            "TAB3 PAGE the chips (1 chosen, the stack 64) and the green totals; (fix tab3) the sell total says it is after the 1.25%% order-fill tax (%s)" % sval(cm, "#SkyyMtabTs0.Text"))
    # fix tab3: the RARITY FRAME round every Bazaar icon (rows + the selected item): exactly the item's rarity frame shows
    def frames3(cm_, g_):
        return [k_ for k_ in range(1, 7) if vis3(cm_, "%sF%d" % (g_, k_))]
    K.check(frames3(cm, "R0I") == [1] and frames3(cm, "R1I") == [2] and frames3(cm, "R4I") == [3] and frames3(cm, "SI") == [1],
            "TAB3 PAGE (fix tab3) the rarity frame on the icons: Stone Common, Ore 00 Uncommon, Ore 01 Rare, the selected Stone Common (%s %s %s %s)"
            % (frames3(cm, "R0I"), frames3(cm, "R1I"), frames3(cm, "R4I"), frames3(cm, "SI")))
    lb3 = [str(x_) for x_ in MTD.LB]
    gi3 = [i_ for i_, x_ in enumerate(lb3) if x_.startswith("ItemGrid #SkyyMtabR0I ")]
    fi3 = [i_ for i_, x_ in enumerate(lb3) if x_.startswith("Group #SkyyMtabR0IF")]
    K.check(len(gi3) == 1 and len(fi3) == 6 and max(fi3) < gi3[0] and "Left: 3, Top: 3" in lb3[gi3[0]] and "SkyyGlass/RarityMythic.png" in lb3[fi3[5]],
            "TAB3 STATIC (fix tab3) the six frames sit BEHIND the grid (drawn first) and the grid is inset 3 px - the frame never covers the slot's hover / click")
    MW["tax"] = None
    cmx = cmap(mt_ev({"a": "amt:0"}, "TAB3 an older SkyyBazaar read without the tax field"))
    MW["tax"] = 0
    cm0 = cmap(mt_ev({"a": "amt:0"}, "TAB3 a 0 pct order tax"))
    MW["tax"] = 125
    K.check(sval(cmx, "#SkyyMtabTs0.Text") == "Sell now: 1 for 5 coins" and sval(cm0, "#SkyyMtabTs0.Text") == "Sell now: 1 for 5 coins",
            "TAB3 PAGE (fix tab3) no tax field (an older read) / a 0 pct tax = no tax note")
    K.check(sval(cm, "#SkyyMtabOh.Text") == "YOUR ORDERS  1" and str(sval(cm, "#SkyyMtabO0.Text")).startswith("Buy order  640 Stone at 5 each") and "412 / 640 filled" in str(sval(cm, "#SkyyMtabO0.Text"))
            and vis3(cm, "Claim") and sval(cm, "#SkyyMtabCl.Text") == "Ready: 377,600 coins + 12 items", "TAB3 PAGE your orders + Claim all with what is waiting")
    K.check(sval(cm, "#SkyyMtabAc.Text") == "3 to claim - Your listings" and str(sval(cm, "#SkyyMtabAs.Text")).startswith("Search above") and not vis3(cm, "A0"),
            "TAB3 PAGE the AH card: claims waiting, the search hint, no rows without a search")
    K.check(sval(cm, "#SkyyMtabBv.Text") == "120,000" and sval(cm, "#SkyyMtabBl.Text") == "Bank Lv 2" and "holds up to 250,000" in str(sval(cm, "#SkyyMtabBs.Text"))
            and ("Width: %d," % (120000 * int(MTD.BAR) // 250000)) in cm.get("#SkyyMtabBb", "") and vis3(cm, "Bg0") and sval(cm, "#SkyyMtabL1.Text").startswith("Bank Lv 2 of 10")
            and str(sval(cm, "#SkyyMtabL2.Text")).startswith("Upgrade to Lv 3") and vis3(cm, "Upg") and vis3(cm, "Dep") and sval(cm, "#SkyyMtabBc3.Text") == "1M",
            "TAB3 PAGE the bank: balance, Lv badge, capacity + the fill bar, the green gain, level lines, Upgrade, Deposit, the chips")
    K.check("Bank 120,000" in str(sval(cm, "#SkyyMtabCoins.Text")), "TAB3 PAGE coins + bank in the top bar")
    K.check(not any("Scrolling" in str(c_.text or "") for c_ in cmds_of(p_)), "TAB3 FIT the screen's packet carries no scrolling list")
    # ACT: navigation (no bridge action)
    n0 = len(MW["acts"])
    p_ = mt_ev({"a": "cat:1"}, "TAB3 ACT the Foraging tab")
    K.check(MW["reads"][-1][1] == "Foraging" and sval(cmap(p_), "#SkyyMtabLt.Text") == "FORAGING" and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabKt1"), "TAB3 ACT a rail tab = that tab (read asks Foraging)")
    p_ = mt_ev({"a": "find", "@Q": "  ore|x  "}, "TAB3 ACT search")
    K.check(MW["reads"][-1][2] == "orex" and sval(cmap(p_), "#SkyyMtabLt.Text") == "SEARCH  OREX", "TAB3 ACT Find = the cleaned search ('|' + spaces gone) (%s)" % MW["reads"][-1][2])
    p_ = mt_ev({"a": "find", "@Q": "stone"}, "TAB3 ACT search stone")
    cm = cmap(p_)
    K.check(vis3(cm, "A0") and not vis3(cm, "A1") and sval(cm, "#SkyyMtabA0N.Text") == "Fine Stone" and "3 listed" in str(sval(cm, "#SkyyMtabA0S.Text")) and sval(cm, "#SkyyMtabQ.Value") == "stone",
            "TAB3 PAGE the AH card shows the search's auctions (a junk row skipped), the field keeps the word")
    p_ = mt_ev({"a": "fclear"}, "TAB3 ACT clear")
    K.check(MW["reads"][-1][2] == "" and MW["reads"][-1][1] == "Foraging", "TAB3 ACT Clear = back to the tab")
    p_ = mt_ev({"a": "cat:0"}, "TAB3 back to Mining")
    p_ = mt_ev({"a": "pg:1"}, "TAB3 ACT next page")
    K.check(MW["reads"][-1][4] == "1" and sval(cmap(p_), "#SkyyMtabPg.Text") == "Page 2 / 2", "TAB3 ACT > = page 2")
    p_ = mt_ev({"a": "pg:1"}, "TAB3 ACT past the last page")
    K.check("last page" in cap3(p_), "TAB3 ACT past the last page = a caption")
    p_ = mt_ev({"a": "pg:-1"}, "TAB3 ACT back")
    K.check(len(MW["acts"]) == n0, "TAB3 SAFE navigation never calls tabact")
    # select
    MS = PK.pm.getCustomPage()
    p_ = mt_ev({"a": "rs:3", "t": str(MS.tok)}, "TAB3 ACT View row 3")
    K.check(str(MS.sel) == str(MS.rowIds[3]) and MW["reads"][-1][3] == str(MS.sel), "TAB3 ACT View selects that row (the read asks for it)")
    p_ = mt_ev({"a": "rs:0", "t": str(MS.tok)}, "TAB3 ACT icon row 0")
    K.check(str(MS.sel) == "Rock_Stone", "TAB3 ACT the icon click selects too")
    # BUY / SELL
    p0 = MW["purse"]
    old = str(MS.tok)
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "TAB3 ACT BUY NOW")
    K.check(MW["acts"][-1] == [uk3, "prof-A", "buy", "Rock_Stone|1|6"] and MW["purse"] == p0 - 6 and "Bought 1" in cap3(p_),
            "TAB3 ACT BUY NOW = tabact buy <id>|<amount>|<the shown total> with the read's profile key, the answer as the caption (%s)" % MW["acts"][-1:])
    p2 = mt_ev({"a": "buy", "t": old}, "TAB3 SAFE double click")
    n1 = len(MW["acts"])
    K.check("The page changed" in cap3(p2) and int(MTB.STALE) >= 1, "TAB3 SAFE a double click (the second from the older drawing) = a caption, no call")
    p_ = mt_ev({"a": "buy", "t": "forged"}, "TAB3 SAFE forged token")
    K.check(len(MW["acts"]) == n1, "TAB3 SAFE a wrong page token never reaches the Bazaar")
    p_ = mt_ev({"a": "amt:2"}, "TAB3 ACT chip All")
    p_ = mt_ev({"a": "sell", "t": str(MS.tok)}, "TAB3 ACT SELL NOW all")
    K.check(MW["acts"][-1][2:] == ["sell", "Rock_Stone|31|155"] and MW["have"]["Rock_Stone"] == 0, "TAB3 ACT SELL NOW All = tabact sell <id>|<all you have>|<the shown pay> (%s)" % MW["acts"][-1:])
    n1 = len(MW["acts"])
    p_ = mt_ev({"a": "sell", "t": str(MS.tok)}, "TAB3 SAFE sell with none")
    K.check(len(MW["acts"]) == n1 and "You have none to sell" in cap3(p_), "TAB3 SAFE SELL NOW with nothing to sell = the read's reason, no call")
    MW["full"] = True
    p_ = mt_ev({"a": "amt:0"}, "TAB3 full")
    K.check(vis3(cmap(p_), "Tb1") and "Your inventory is full" in str(sval(cmap(p_), "#SkyyMtabTb1.Text")), "TAB3 SAFE a full inventory: the buy total turns red with why")
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "TAB3 SAFE buy when full")
    K.check(len(MW["acts"]) == n1 and "full" in cap3(p_), "TAB3 SAFE BUY NOW refused up front when the read said why (no call)")
    MW["full"] = False
    MW["purse"] = 3
    p_ = mt_ev({"a": "amt:1"}, "TAB3 poor")
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "TAB3 SAFE not enough coins")
    K.check(len(MW["acts"]) == n1 and "Not enough coins" in cap3(p_), "TAB3 SAFE not enough coins = said, no call")
    MW["purse"] = 50000
    MW["tok"] = "prof-B"
    p_ = mt_ev({"a": "amt:0"}, "TAB3 redraw before switch")
    MW["tok"] = "prof-C"
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "TAB3 SAFE profile switch")
    K.check(MW["acts"][-1][1] == "prof-B" and "profile changed" in cap3(p_) and MW["have"].get("Rock_Stone", 0) == 0, "TAB3 SAFE a profile switch between read and click = the Bazaar refuses, nothing moved")
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "TAB3 SAFE after the redraw")
    K.check(MW["acts"][-1][1] == "prof-C" and MW["have"].get("Rock_Stone", 0) == 1, "TAB3 SAFE after the redraw the new profile key is used")
    MW["tok"] = "prof-A"
    p_ = mt_ev({"a": "amt:0"}, "TAB3 redraw")
    p_ = mt_ev({"a": "claim", "t": str(MS.tok)}, "TAB3 ACT Claim all")
    K.check(MW["acts"][-1][2] == "claim" and MW["claims"] == 0 and "Claimed" in cap3(p_) and not vis3(cmap(p_), "Claim"), "TAB3 ACT Claim all = tabact claim; the button goes when nothing waits")
    n1 = len(MW["acts"])
    p_ = mt_ev({"a": "claim", "t": str(MS.tok)}, "TAB3 SAFE claim nothing")
    K.check(len(MW["acts"]) == n1 and "Nothing to claim" in cap3(p_), "TAB3 SAFE Claim with nothing waiting = a caption, no call")
    # orders / offers + AH (functions that would open another page; FALSE here = the hub route)
    p_ = mt_ev({"a": "order"}, "TAB3 ACT Buy order")
    K.check(MW["bzo"] and MW["bzo"][-1][1] == "Stone", "TAB3 ACT Buy order = bazaar:fn:open on the selected item's name (%s)" % MW["bzo"][-1:])
    p_ = mt_ev({"a": "ah:create"}, "TAB3 ACT New listing")
    K.check(MW["ahv"] and MW["ahv"][-1][1] == "create", "TAB3 ACT New listing = ah:fn:view create")
    p_ = mt_ev({"a": "find", "@Q": "stone"}, "TAB3 search for AH")
    p_ = mt_ev({"a": "ahr:0", "t": str(MS.tok)}, "TAB3 ACT AH Open")
    K.check(MW["aho"] and MW["aho"][-1][1] == "Fine Stone", "TAB3 ACT an auction row's Open = ah:fn:open on its name")
    p_ = mt_ev({"a": "ah:steal"}, "TAB3 SAFE junk AH view")
    K.check(MW["ahv"][-1][1] == "create", "TAB3 SAFE an unknown AH view never reaches ah:fn:view")
    p_ = mt_ev({"a": "fclear"}, "TAB3 clear")
    # BANK
    b0, pu0 = MW["bank"], MW["purse"]
    p_ = mt_ev({"a": "bamt:1"}, "TAB3 ACT bank chip 10k")
    K.check(str(MTD.ST_CHSEL) in mk_of(p_, "SkyyMtabBc1"), "TAB3 ACT a bank chip shows chosen")
    p_ = mt_ev({"a": "dep", "t": str(MS.tok)}, "TAB3 ACT Deposit 10k")
    K.check(MW["bmoves"][-1][:4] == [uk3, "deposit", "10k", "prof-A"] and MW["bmoves"][-1][4] == "7" and MW["bank"] == b0 + 10000 and MW["purse"] == pu0 - 10000 and "Deposited" in cap3(p_),
            "TAB3 ACT Deposit = bank:fn:move deposit 10k with the panel's key + epoch (%s)" % MW["bmoves"][-1:])
    nb = len(MW["bmoves"])
    old = str(MS.tok)
    p_ = mt_ev({"a": "wd", "t": str(MS.tok)}, "TAB3 ACT Withdraw 10k")
    p2 = mt_ev({"a": "wd", "t": old}, "TAB3 SAFE bank double click")
    K.check(len(MW["bmoves"]) == nb + 1 and MW["bmoves"][-1][1] == "withdraw" and MW["bank"] == b0 and "The page changed" in cap3(p2),
            "TAB3 SAFE a bank double click moves once")
    p_ = mt_ev({"a": "bamt:4"}, "TAB3 ACT bank chip All")
    p_ = mt_ev({"a": "dep", "t": str(MS.tok)}, "TAB3 ACT Deposit all")
    K.check(MW["bmoves"][-1][1] == "depall" and MW["purse"] == 0, "TAB3 ACT Deposit All = depall")
    p_ = mt_ev({"a": "wd", "t": str(MS.tok)}, "TAB3 ACT Withdraw all")
    K.check(MW["bmoves"][-1][1] == "wdall" and MW["bank"] == 0, "TAB3 ACT Withdraw All = wdall")
    MW["bank"], MW["purse"] = 120000, 50000
    p_ = mt_ev({"a": "bamt:3"}, "TAB3 1M")
    p_ = mt_ev({"a": "dep", "t": str(MS.tok)}, "TAB3 SAFE deposit more than the purse")
    K.check("nothing was moved" in cap3(p_) and MW["bank"] == 120000, "TAB3 SAFE a refused deposit = SkyyBank's answer, nothing moved")
    nb = len(MW["bmoves"])
    p_ = mt_ev({"a": "up", "t": str(MS.tok)}, "TAB3 ACT Upgrade first press")
    K.check(len(MW["bmoves"]) == nb and "press Upgrade again" in cap3(p_) and sval(cmap(p_), "#SkyyMtabUpg.Text") == "Press again", "TAB3 ACT Upgrade asks first (no move)")
    p_ = mt_ev({"a": "up", "t": str(MS.tok)}, "TAB3 ACT Upgrade second press")
    K.check(MW["bmoves"][-1][1:3] == ["upgrade", "2"] and MW["lv"] == 3 and "Bank Lv 3" in cap3(p_), "TAB3 ACT the second press = bank:fn:move upgrade <the level shown>")
    p_ = mt_ev({"a": "up", "t": str(MS.tok)}, "TAB3 Upgrade again asks")
    p_ = mt_ev({"a": "bamt:0"}, "TAB3 another click cancels the ask")
    nb = len(MW["bmoves"])
    p_ = mt_ev({"a": "up", "t": str(MS.tok)}, "TAB3 Upgrade asks once more")
    K.check(len(MW["bmoves"]) == nb, "TAB3 SAFE any other click between the two presses cancels the upgrade ask")
    MW["can"] = False
    p_ = mt_ev({"a": "bamt:0"}, "TAB3 top level")
    K.check(not vis3(cmap(p_), "Upg"), "TAB3 PAGE Upgrade hidden when no level can be bought")
    MW["can"] = True
    MW["bkey"] = "prof-Z"
    p_ = mt_ev({"a": "dep", "t": str(MS.tok)}, "TAB3 SAFE bank profile switch")
    K.check("profile changed" in cap3(p_), "TAB3 SAFE a bank move with the old profile key = SkyyBank refuses")
    MW["bkey"] = "prof-A"
    # the read failing: the page still draws, no Bazaar action
    MW["readNull"] = True
    p_ = mt_ev({"a": "amt:0"}, "TAB3 FALL the read fails")
    cm = cmap(p_)
    n1 = len(MW["acts"])
    K.check("could not be read" in str(sval(cm, "#SkyyMtabLn.Text")) and not vis3(cm, "R0") and sval(cm, "#SkyyMtabBv.Text") == "{:,}".format(MW["bank"]),
            "TAB3 FALL the Bazaar read = null: the page still draws (rows hidden), the bank still works")
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "TAB3 FALL buy while the read fails")
    K.check(len(MW["acts"]) == n1 and "not ready" in cap3(p_), "TAB3 FALL no Bazaar action while it cannot be read (no call)")
    p_ = mt_ev({"a": "dep", "t": str(MS.tok)}, "TAB3 FALL bank still works")
    K.check(MW["bmoves"][-1][1] == "deposit", "TAB3 FALL a deposit still works while the Bazaar read fails")
    MW["readNull"] = False
    # TABS
    p_ = mt_ev({"a": "tab:3"}, "TAB3 TABS Market")
    K.eq(cap3(p_), "You are on Market", "TAB3 TABS Market = a caption")
    p_ = mt_ev({"a": "tab:2"}, "TAB3 TABS Pets (no pets keys)")
    K.check("Pets is not on this server" in cap3(p_) or "Opening" in cap3(p_) or PK.pm.getCustomPage() != MS, "TAB3 TABS Pets without SkyyPets' keys = today's route")
    if PK.pm.getCustomPage() != MS:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
        MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
        E.pump(PK)
    p_ = mt_ev({"a": "tab:1"}, "TAB3 TABS Skills")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and bool(MS.closed), "TAB3 TABS Skills = the skill page")
    p_ = mt_ev({"a": "tab:3"}, "TAB3 OPEN the skill page's Market tab")
    MS = PK.pm.getCustomPage()
    K.check(MS is not None and str(MS.getClass().getSimpleName()) == "MarketTab", "TAB3 OPEN the skill page's Market tab = the market screen")
    p_ = mt_ev({"a": "tab:0"}, "TAB3 TABS Inventory")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "c", "TAB3 TABS Inventory = the inventory screen")
    BR.put("pets:fn:tab", Fn(f_tab))
    BR.put("pets:fn:tabact", Fn(f_act))
    p_ = one(ev(PK, {"a": "pet"}), "TAB3 the pets screen")
    PS3 = PK.pm.getCustomPage()
    p_ = mt_ev({"a": "tab:3"}, "TAB3 OPEN the pets screen's Market tab")
    MS = PK.pm.getCustomPage()
    K.check(str(PS3.getClass().getSimpleName()) == "PetsTab" and MS is not None and str(MS.getClass().getSimpleName()) == "MarketTab" and bool(PS3.closed),
            "TAB3 OPEN the pets screen's Market tab = the market screen")
    p_ = mt_ev({"a": "tab:2"}, "TAB3 TABS Pets")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "PetsTab", "TAB3 TABS Pets = the pets screen")
    for k_ in ("pets:fn:tab", "pets:fn:tabact"):
        BR.remove(k_)
    p_ = mt_ev({"a": "tab:3"}, "TAB3 back to Market")
    MS = PK.pm.getCustomPage()
    p_ = mt_ev({"a": "tab:6"}, "TAB3 TABS Settings")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(MS.closed), "TAB3 TABS Settings = our Settings page")
    for a_, what in (("full", "Full page"), ("mer", "Merchants"), ("bank", "the Bank page"), ("tab:4", "World")):
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
        MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
        E.pump(PK)
        f0_ = len(E.sent(PK))
        MS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": a_}))
        cur_ = PK.pm.getCustomPage()
        K.check(len(pages(PK, f0_)) == 1, "TAB3 TABS %s = today's route, ONE packet (%s)" % (what, None if cur_ is None else cur_.getClass().getSimpleName()))
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    ST.tab(PK.ref, PK.st, PK.pr, PK.pl, "test")
    K.check(PK.pm.getCustomPage() is None and bool(MS.closed), "TAB3 TABS the Tab key closes the market screen")
    MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    MS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(PK.pm.getCustomPage() is None and bool(MS.closed), "TAB3 TABS X closes the screen")
    K.notes.append("TAB3 counters: opens %d, stale %d, reads %d, acts %d, bank moves %d" % (int(MTB.OPENS), int(MTB.STALE), len(MW["reads"]), len(MW["acts"]), len(MW["bmoves"])))
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:panel", "bank:fn:move", "ah:fn:view", "ah:fn:find", "ah:fn:open", "bazaar:fn:open"):
        BR.remove(k_)
    E.pump(PK)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_TAB3 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
if T.dst:
    T.finish()
