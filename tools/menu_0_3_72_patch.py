"""Derive SkyyMenu/build_skyymenu_0.3.72.py + SkyyMenu/test_skyymenu_0.3.72.py from the SET pin SkyyMenu 0.3.71 (generated - never re-run
its patch). Run:  python tools/menu_0_3_72_patch.py   then   python SkyyMenu/build_skyymenu_0.3.72.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.72.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyBazaar 0.2.8 (tools/bazaar_0_2_8_patch.py: bazaar:fn:tab 8+ arguments + tabact bid / ask /
cancel) for Bazaar orders and SkyyMerchants 0.1.10 (tools/merchants_0_1_10_patch.py: merchants:fn:tab / tabact buy) for Merchants; with the
older jars those two views say which version they need (the rest of the Market tab works as 0.3.71).

0.3.72 (2026-11-24, round oldmenu4) = OLD MENU FOLLOW-UP: THE MARKET TAB = THE OLD BAZAAR ORDERS + MERCHANTS PAGES. Skyy's words (docs/answered/
ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu compleatly, so instead of
adding things like the full tree button, just build it all into the new system and remove the old "Full tree""; 2026-11-23 "looks better. go
head and build everything on your list." Each part calls the SAME server code as the old page (through the bridges; no duplicated rule, no new
number):
  BAZAAR ORDERS (market:bazaar gone): the top bar's Full page button is gone; Buy order / Sell offer on the selected item open the BAZAAR ORDERS
      VIEW of this screen (sub-tabs Market | Bazaar orders | Merchants - research/Menu-Pattern.md: one sub-tab row, no back button):
      the item (rarity frame + name colour, tier, you have, best order / offer), BUY ORDER | SELL OFFER, the prices a new order may use now
      (n| band), Amount (typed) + All (n| all), Price each (typed) + Best price + Beat by 1 (n| chips + their notes), the TOTAL / why-not line
      (w| = BzPage.whyStep: green total or the red reason) and the 'Confirm buys from' note, PLACE (bazaar:fn:tabact bid / ask
      id|qty|price|total) + Check total; MY ORDERS (o| with order ids: side, item, qty, filled, price) with Cancel per order (tabact cancel
      <order id>) + Claim all.
      NEVER A TOTAL THE PLAYER DID NOT SEE: Place sends the amount / price / total of the w| line DRAWN in the packet the player pressed; the
      button carries the typed boxes - typed values that differ from the drawn ones are only checked (a redraw with the new total, nothing
      sent). The page's own confirm (bid over 'Confirm buys from'): SkyyBazaar answers '=Place a buy order holding N coins ...? Press Buy order
      again within 10 s.' (the caption), the same press again places it. A '+' answer empties the boxes (a deliberate second press cannot
      repeat it).
  MERCHANTS (market:merchants gone): the Merchants card's Open Merchants is gone; See merchants = the MERCHANTS VIEW: the shop's 4 tabs
      (Weapons / Mounts / Pet eggs / Augments - k| lines), every merchant zone of your world (z|: name + level band, out / moves in, near +
      blocks, the rumour), Shop here (another merchant you stand at), the STOCK of the merchant you stand at (s|: sorted by tier then name by
      SkyyMerchants, the rarity square behind the icon + the name colour in the tooltip, T<tier>, left, price, Buy - 9 a page, < >), Refresh.
      FINDING STAYS A HUNT (docs/answered/economy.md LOCKED 2026-10-09): no coordinates are ever drawn (SkyyMerchants sends them only when you
      stand at the merchant; the view shows only the blocks away), stock + Buy only at the merchant. Buy = merchants:fn:tabact buy
      zone|npc|tab|item|price shown; the first press answers '=Buy X for N coins? Press Buy again within 10 s.', the same press again buys -
      every answer word for word in the caption.
  SAFETY: every placing / cancelling / buying click carries the page token (an older drawing = "The page changed", nothing runs) and the
      profile key of the read (a profile switch = SkyyBazaar's / SkyyMerchants' "=Your profile changed", nothing moves); every action redraws
      (a new token), so a double click never runs twice; the bridges re-check everything under their own rules (350 ms same-op guard
      "=One moment.", busy profile, stopping server). A click meant for another view (a forged event) = a caption, no call.
  ONE SCREEN, THREE SECTIONS: the page data carries a section letter per line (0 = the frame, H = the home cards, O = Bazaar orders,
      M = Merchants); build() appends the frame + the current section only (the element budget = the frame + the biggest section).
  The Bazaar read always sends the 0.2.8 opt-in arguments (max order lines, side, amount, price); its o| lines are split in 8 (an older
      SkyyBazaar's 7-field lines still read the same).
  STILL OLD (OLD_LEFT keeps market:auctions - its own round). NOT YET IN THE NEW SCREEN: the old Bazaar page's 'Sell <tab>' + 'Sell all
      tabs' bulk sells (SkyyBazaar's own sellinv / sellalltabs actions - the bridge tabact has no such op yet): /bazaar only until the next
      Bazaar op round (tabact sellinv | sellalltabs + a two-press confirm on the Market cards). MY ORDERS rows carry no rarity frame (the o|
      line has no rarity field; the rarity table lives in SkyyBazaar BzMarket.rar) - the same Bazaar round adds it.
New: no class / command / system / picture / lang key / setting / saved data. OLD_LEFT: market:bazaar, market:merchants out (15 -> 13).
ROLLBACK to 0.3.71: safe alone (nothing saved; the Full page + Open Merchants links come back). SkyyBazaar 0.2.8 / SkyyMerchants 0.1.10 each
roll back alone (Menu then names the version each view needs).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.71.py"), os.path.join(MOD, "build_skyymenu_0.3.72.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.71.py"), os.path.join(MOD, "test_skyymenu_0.3.72.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.71"\n') and P.has("OLD_LEFT = sorted(set([") and P.has("SkyyStabSvL") and not P.has("SkyyMtabOvL"), "not the generated SkyyMenu 0.3.71 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.71: OLD MENU FOLLOW-UP F6''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.72: OLD MENU FOLLOW-UP - THE MARKET TAB: no Full page; Buy order / Sell offer = the Bazaar orders view (typed amount + price, Best price /
       Beat by 1 / All, the total + why-not before pressing, the page's two-press confirm, MY ORDERS with Cancel - SkyyBazaar 0.2.8 tabact bid /
       ask / cancel); See merchants = the Merchants view (4 shop tabs, every zone + rumour + moves-in, stock / Buy only at the merchant -
       SkyyMerchants 0.1.10 merchants:fn:tab / tabact buy); OLD_LEFT lost 2 rows, the Auction House stays (notes: tools/menu_0_3_72_patch.py).
       CHECKED: SkyyMenu/test_skyymenu_0.3.72.py.
0.3.71: OLD MENU FOLLOW-UP F6''')
P.rep('VERSION = "0.3.71"\n', 'VERSION = "0.3.72"\n')

# ======================================================================= the HOME cards: no Full page, Buy order / Sell offer, See merchants
P.rep('''    "merch3": "each visit restocks. Their shop opens from here.",''', '''    "merch3": "each visit restocks - follow the rumours.",   # 0.3.72''')
P.rep('''    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(MT + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(MT + "Coins",''', '''    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % (sp + 128)))   # 0.3.72: no Full page (the old Bazaar page is in this screen)
    ap.append(("#" + top, lab(MT + "Coins",''')
P.rep('''    ap.append(("#" + ob, G_.glass_button(MT + "Ord", "Buy order - on the Bazaar page", "secondary", w=MT_BBW, h=32, size=12, anchor={"right": 8})))
    ap.append(("#" + ob, G_.glass_button(MT + "Off", "Sell offer - on the Bazaar page", "secondary", w=MT_BBW, h=32, size=12)))
    for t_ in ("Buy order - on the Bazaar page", "Sell offer - on the Bazaar page"):''',
      '''    ap.append(("#" + ob, G_.glass_button(MT + "Ord", "Buy order", "secondary", w=MT_BBW, h=32, size=13, anchor={"right": 8})))   # 0.3.72: the orders view
    ap.append(("#" + ob, G_.glass_button(MT + "Off", "Sell offer", "secondary", w=MT_BBW, h=32, size=13)))
    for t_ in ("Buy order", "Sell offer"):''')
P.rep('''    ap.append(("#" + mc, G_.glass_button(MT + "Mgo", "Open Merchants", "primary", w=200, h=36, size=14, anchor={"top": 14})))''',
      '''    ap.append(("#" + mc, G_.glass_button(MT + "Mgo", "See merchants", "primary", w=200, h=36, size=14, anchor={"top": 14})))   # 0.3.72: the merchants view''')
P.rep('''    binds = [("#%sT%d" % (MT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + MT + "Close", "close"), ("#" + MT + "Full", "full"),''',
      '''    binds = [("#%sT%d" % (MT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + MT + "Close", "close"),''')

# ======================================================================= the VIEWS (O Bazaar orders, M Merchants) + the section letters
MT_VIEWS_PY = r'''

# ---- 0.3.72 (oldmenu4): THE MARKET SCREEN'S VIEWS - each one fills the body's place (the frame, the top bar and the hint row stay). The page
# data carries a section letter per line: 0 = always, H = the home cards, O = Bazaar orders, M = Merchants; build() appends the frame + the
# current one only. Sub-tabs (research/Menu-Pattern.md: one row, the open one selected, no back button): Market | Bazaar orders | Merchants.
MT_VI = IV_IW - 20                                          # a view's inner width (1536)
MT_VBW = 170                                                # a sub-tab / side / shop tab button
MT_SUBS = ["Market", "Bazaar orders", "Merchants"]
MT_VBH = IV_BODY_H - 20 - 34 - 6                            # a view's body under its head (784)
OV_LW = 760                                                 # BAZAAR ORDERS: the form card
OV_RW = MT_VI - OV_LW - 10                                  # MY ORDERS (766)
OV_LI = OV_LW - 20
OV_ON, OV_RH = 12, 46                                       # my orders shown (the read asks for this many with ids)
OV_FW, OV_LBW, OV_CW, OV_GOW = 220, 110, 196, 360           # a typed box, a row label, a chip button, Place
OV_RTW = OV_RW - 12 - 40 - 8 - 8 - 110                      # an order row's text column
MV_KN = 4                                                   # MERCHANTS: the shop's tabs (MerchShop.CAT_NAME)
MV_KNAME = ["Weapons", "Mounts", "Pet eggs", "Augments"]    # until the read names them (k| lines)
MV_LW = 640
MV_RW = MT_VI - MV_LW - 10                                  # the stock card (886)
MV_RI = MV_RW - 20
MV_BH = MT_VBH - 34 - 6                                     # under the shop tabs (744)
MV_ZN, MV_ZH = 6, 96                                        # zone rows (SkyyMerchants has 5 zones a world)
MV_ZTW = MV_LW - 16 - 120 - 8
MV_SN, MV_SH, MV_SQ = 9, 56, 52                             # stock rows a page, their height, the icon + rarity square
MV_PW, MV_BW = 170, 110
MV_STW = MV_RI - 12 - MV_SQ - 8 - MV_PW - 8 - MV_BW         # a stock row's text column
assert OV_RTW >= 400 and MV_ZTW >= 400 and MV_STW >= 400, (OV_RTW, MV_ZTW, MV_STW)
assert MT_VI - 240 - len(MT_SUBS) * (MT_VBW + 6) >= 400, "0.3.72: a view head fits its sub-tabs"
for _l in MT_SUBS + ["Buy order", "Sell offer"] + MV_KNAME:
    assert SUI.text_width(_l, 14, bold=True) <= MT_VBW - 16, ("0.3.72: a sub-tab / side / shop tab fits", _l)
for _l in ("All  999,999,999", "Best price  999,999,999", "Beat by 1  999,999,999", "Check total"):
    assert SUI.text_width(_l, 13, bold=True) <= OV_CW - 12, ("0.3.72: a chip button fits", _l)
for _l in ("PLACE BUY ORDER", "PLACE SELL OFFER"):
    assert SUI.text_width(_l, 15, bold=True) <= OV_GOW - 16, ("0.3.72: Place fits", _l)
assert SUI.text_width("999,999,999,999 coins", 15, bold=True) <= MV_PW, "0.3.72: a merchant price fits"
MT_VTXT = {
    "ovcap": "Type an amount and a price, check the total, then Place. Market on top goes back.",
    "ovchk": "Here is the total for what you typed - check it, then press Place again.",
    "ovold": "Buy orders and sell offers here need SkyyBazaar 0.2.8 - this server has an older one.",
    "ovpick": "Pick an item on the Market page first (Market above), then press Buy order or Sell offer.",
    "ovhelp1": "A buy order holds its coins now and fills when someone sells; a sell offer takes the items now.",
    "ovhelp2": "Filled orders wait here - Claim all collects them. Cancel gives back what has not filled.",
    "mvcap": "Merchants roam each zone - the rumours say roughly where. Buy needs you at the merchant.",
    "mvold": "Merchants here need SkyyMerchants 0.1.10 - this server has an older one. /merchants works.",
    "mvoff": "Merchants are not on this server right now.",
    "mvfar": "Stand next to a merchant to see its stock and buy. Finding them is the hunt - follow the rumours.",
    "mvfail": "The merchants could not be read right now - try again in a moment.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in MT_VTXT.values() for c_ in v_), "0.3.72: plain texts"
for _k in ("ovold", "ovpick", "ovhelp1", "ovhelp2"):
    assert SUI.text_width(MT_VTXT[_k], 12) <= OV_LI, ("0.3.72: an orders line fits", _k)
for _k in ("mvold", "mvoff", "mvfail"):
    assert SUI.text_width(MT_VTXT[_k], 13) <= MT_VI - 240 - len(MT_SUBS) * (MT_VBW + 6), ("0.3.72: a merchants head line fits", _k)
assert SUI.text_width(MT_VTXT["mvfar"], 12) <= MV_RI, "0.3.72: the not-near line fits"
for _k in ("ovcap", "ovchk", "mvcap"):
    assert SUI.text_width(MT_VTXT[_k], 14) <= IV_IW - 420, ("0.3.72: a caption fits the hint row", _k)
# the run-time markup: the side / shop tab buttons and the merchant's rarity square ({C} = only a colour MarketTab.sqOf passed)
MT_SIDE = "TextButton #SkyyMtab{I} { Anchor: (Width: %d, Height: 34, Right: 6); {S} }" % MT_VBW
MT_SQ = "Group { Anchor: (Width: %d, Height: %d, Left: 0, Top: 0); Background: {C}; }" % (MV_SQ, MV_SQ)
_mv_mk = [MT_SIDE.replace("{I}", "Sd0").replace("{S}", MT_ST_CATSEL), MT_SIDE.replace("{I}", "Mk0").replace("{S}", MT_ST_CAT), MT_SQ.replace("{C}", "#2770b7(0.4)")]
for _mk in _mv_mk:
    SUI.check_markup(_mk, prefix=MT, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.72: a run-time markup line Java can hold"
_mv_tok = SUI.proven_tokens(_mv_mk)
assert not [k_ for k_, g_ in _mv_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], "0.3.72: the view markups are proven"
OV_RUNTIME_MAX = 2                                          # the two side buttons
MV_RUNTIME_MAX = MV_KN + MV_SN                              # the shop tabs + a rarity square per stock row


def _mt_views():
    G_ = SUI
    lab = G_.glass_label
    win = MT + "Win"
    out = []

    def vhead(ap, parent, v, title, on):
        hd = MT + v + "h"
        ap.append(("#" + parent, G_.glass_group(hd, MT_VI, 34, layout="Left")))
        ap.append(("#" + hd, lab(None, title, 16, "accentHi", bold=True, w=240, h=34)))
        for k_, t_ in enumerate(MT_SUBS):
            ap.append(("#" + hd, G_.glass_button("%s%sT%d" % (MT, v, k_), t_, "tabSelected" if k_ == on else "tab", w=MT_VBW, h=34, size=14, anchor={"right": 6})))
        ap.append(("#" + hd, lab(MT + v + "H", "", 13, "text", w=MT_VI - 240 - len(MT_SUBS) * (MT_VBW + 6), h=34, halign="End")))
        return [("#%s%sT%d" % (MT, v, k_), "vw:%d" % k_) for k_ in range(len(MT_SUBS))]

    def holder(ap, parent, ident, w, h, size, cols, anchor=None, bold=False):
        vs = [SUI.keep_at0(lab("%s%d" % (ident, k_), "", size, c_, bold=bold, w=w, h=h)) for k_, c_ in enumerate(cols)]
        hm, kids = SUI.keep_holder(ident + "H", w, h, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)

    def framed(ap, parent, grid, size, anchor):   # the home screen's rarity frame (MT_FRAMES behind a 1 x 1 grid inset 3 px)
        vs = [SUI.keep_at0('Group #%sF%d { Anchor: (Width: %d, Height: %d); Background: %s; }' % (grid, k_ + 1, size, size, SUI.glass_patch(fr_)))
              for k_, fr_ in enumerate(MT_FRAMES)]
        hm, kids = SUI.keep_holder(grid + "Q", size, size, vs, anchor=anchor)
        ap.append(("#" + parent, hm))
        ap.extend(kids)
        ap.append(("#" + grid + "Q", SUI.keep_at0(G_.glass_grid(grid, 1, 1, drag=False, slot=size - 6, icon=size - 14)).replace(
            "Left: 0, Top: 0", "Left: 3, Top: 3")))
    # ======== O: BAZAAR ORDERS (the old Bazaar page's BUY ORDER / SELL OFFER steps + MY ORDERS)
    ap = SUI.Appends()
    ov = MT + "Ov"
    ap.append(("#" + win, G_.glass_group(ov, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bo = vhead(ap, ov, "Ov", "BAZAAR ORDERS", 1)
    ob = MT + "Ovb"
    ap.append(("#" + ov, G_.glass_group(ob, MT_VI, MT_VBH, layout="Left", anchor={"top": 6})))
    ol = MT + "OvL"
    ap.append(("#" + ob, G_.glass_group(ol, OV_LW, MT_VBH, role="inset", layout="Top", pad=10)))
    oh = MT + "Ovit"
    ap.append(("#" + ol, G_.glass_group(oh, OV_LI, 64, layout="Left")))
    framed(ap, oh, MT + "OvI", 64, None)
    ox = MT + "Ovx"
    ap.append(("#" + oh, G_.glass_group(ox, OV_LI - 74, 64, layout="Top", anchor={"left": 10})))
    holder(ap, ox, MT + "OvN", OV_LI - 74, 26, 20, ["dim"] + MT_RCOL[1:], bold=True)
    ap.append(("#" + ox, lab(MT + "OvT", "", 13, "xp", bold=True, w=OV_LI - 74, h=18)))
    ap.append(("#" + ox, lab(MT + "OvB", "", 11, "dim", w=OV_LI - 74, h=18)))
    sr = MT + "Ovs"
    ap.append(("#" + ol, G_.glass_group(sr, OV_LI, 34, layout="Left", anchor={"top": 10})))
    ap.append(("#" + sr, lab(None, "Place a", 13, "dim", bold=True, w=OV_LBW, h=34)))
    ap.append(("#" + sr, G_.glass_group(MT + "OvSd", 2 * (MT_VBW + 6), 34, layout="Left")))
    ap.append(("#" + ol, lab(MT + "OvBd", "", 12, "text", w=OV_LI, h=20, anchor={"top": 6})))
    fm = MT + "OvF"                                           # the form (hidden when nothing can be placed)
    fm_h = 10 + 34 + 2 + 18 + 10 + 34 + 2 + 18 + 18 + 12 + 24 + 2 + 18 + 12 + 44
    ap.append(("#" + ol, G_.glass_group(fm, OV_LI, fm_h, layout="Top")))
    ar = MT + "Ova"
    ap.append(("#" + fm, G_.glass_group(ar, OV_LI, 34, layout="Left", anchor={"top": 10})))
    ap.append(("#" + ar, lab(None, "Amount", 13, "dim", bold=True, w=OV_LBW, h=34)))
    ap.append(("#" + ar, G_.text_field(MT + "OvABox", MT + "OvA", w=OV_FW, h=32, placeholder="How many", max_length=15, size=14, anchor={"right": 6})))
    ap.append(("#" + ar, G_.glass_button(MT + "OvAll", "All", "secondary", w=OV_CW, h=34, size=13)))
    ap.append(("#" + fm, lab(MT + "OvAn", "", 12, "dim", w=OV_LI, h=18, anchor={"top": 2})))
    pr = MT + "Ovp"
    ap.append(("#" + fm, G_.glass_group(pr, OV_LI, 34, layout="Left", anchor={"top": 10})))
    ap.append(("#" + pr, lab(None, "Price each", 13, "dim", bold=True, w=OV_LBW, h=34)))
    ap.append(("#" + pr, G_.text_field(MT + "OvPBox", MT + "OvP", w=OV_FW, h=32, placeholder="Coins each", max_length=15, size=14, anchor={"right": 6})))
    ap.append(("#" + pr, G_.glass_button(MT + "OvBest", "Best price", "secondary", w=OV_CW, h=34, size=13, anchor={"right": 6})))
    ap.append(("#" + pr, G_.glass_button(MT + "OvBeat", "Beat by 1", "secondary", w=OV_CW, h=34, size=13)))
    assert OV_LBW + OV_FW + 6 + 2 * (OV_CW + 6) <= OV_LI, "0.3.72: the price row fits"
    ap.append(("#" + fm, lab(MT + "OvNa", "", 12, "dim", w=OV_LI, h=18, anchor={"top": 2})))
    ap.append(("#" + fm, lab(MT + "OvNb", "", 12, "dim", w=OV_LI, h=18)))
    holder(ap, fm, MT + "OvW", OV_LI, 24, 15, ["green", "red"], anchor={"top": 12}, bold=True)
    ap.append(("#" + fm, lab(MT + "OvCf", "", 12, "action", w=OV_LI, h=18, anchor={"top": 2})))
    gr = MT + "Ovg"
    ap.append(("#" + fm, G_.glass_group(gr, OV_LI, 44, layout="Left", anchor={"top": 12})))
    ap.append(("#" + gr, G_.glass_button(MT + "OvGo", "PLACE BUY ORDER", "primary", w=OV_GOW, h=44, size=15, anchor={"right": 8})))
    ap.append(("#" + gr, G_.glass_button(MT + "OvChk", "Check total", "secondary", w=OV_CW, h=44, size=14)))
    ap.append(("#" + ol, lab(MT + "OvX1", "", 12, "dim", w=OV_LI, h=18, anchor={"top": 14})))
    ap.append(("#" + ol, lab(MT + "OvX2", "", 12, "dim", w=OV_LI, h=18)))
    ap.sets.append((MT + "OvX1", "Text", MT_VTXT["ovhelp1"]))
    ap.sets.append((MT + "OvX2", "Text", MT_VTXT["ovhelp2"]))
    assert 20 + 64 + 10 + 34 + 6 + 20 + fm_h + 14 + 18 + 18 <= MT_VBH, "0.3.72: the orders form fits"
    ap.append(("#" + ob, "Group { Anchor: (Width: 10); }"))
    orr = MT + "OvO"
    ap.append(("#" + ob, G_.glass_group(orr, OV_RW, MT_VBH, layout="Top")))
    orh = MT + "OvOr"
    ap.append(("#" + orr, G_.glass_group(orh, OV_RW, 30, layout="Left")))
    ap.append(("#" + orh, lab(MT + "OvOh", "", 14, "accentHi", bold=True, w=220, h=30)))
    ap.append(("#" + orh, lab(MT + "OvCl", "", 12, "green", bold=True, w=OV_RW - 220 - 130, h=30, halign="End", anchor={"right": 8})))
    ap.append(("#" + orh, G_.glass_button(MT + "OvClaim", "Claim all", "primary", w=122, h=30, size=12)))
    for k_ in range(OV_ON):
        r_ = "%sOvR%d" % (MT, k_)
        ap.append(("#" + orr, G_.glass_group(r_, OV_RW, OV_RH, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        ap.append(("#" + r_, G_.glass_grid(r_ + "I", 1, 1, drag=False, slot=40, icon=32, anchor={"top": 3})))
        rx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(rx, OV_RTW, OV_RH, layout="Top", anchor={"left": 8})))
        ap.append(("#" + rx, lab(r_ + "N", "", 13, "row", bold=True, w=OV_RTW, h=22, anchor={"top": 3})))
        ap.append(("#" + rx, lab(r_ + "S", "", 11, "xp", bold=True, w=OV_RTW, h=18)))
        ap.append(("#" + r_, G_.glass_button(r_ + "C", "Cancel", "secondary", w=110, h=30, size=13, anchor={"left": 8, "top": 8})))
    ap.append(("#" + orr, lab(MT + "OvMore", "", 12, "dim", w=OV_RW, h=18, anchor={"top": 6})))
    assert 30 + OV_ON * (OV_RH + 4) + 24 <= MT_VBH and 3 + 22 + 18 <= OV_RH, "0.3.72: my orders fit"
    out.append(("O", ap, bo))
    # ======== M: MERCHANTS (the old Merchants shop window: 4 tabs, every zone + rumour, the stock of the merchant you stand at)
    ap = SUI.Appends()
    mv = MT + "Mv"
    ap.append(("#" + win, G_.glass_group(mv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bm = vhead(ap, mv, "Mv", "MERCHANTS", 2)
    mk = MT + "Mvk"
    ap.append(("#" + mv, G_.glass_group(mk, MT_VI, 34, layout="Left", anchor={"top": 6})))
    ap.append(("#" + mk, G_.glass_group(MT + "MvK", MV_KN * (MT_VBW + 6), 34, layout="Left")))
    ap.append(("#" + mk, lab(MT + "MvW", "", 13, "text", w=MT_VI - MV_KN * (MT_VBW + 6) - 112 - 8, h=34, halign="End", anchor={"right": 8})))
    ap.append(("#" + mk, G_.glass_button(MT + "MvRf", "Refresh", "secondary", w=112, h=34, size=13)))
    mb = MT + "Mvb"
    ap.append(("#" + mv, G_.glass_group(mb, MT_VI, MV_BH, layout="Left", anchor={"top": 6})))
    zl = MT + "MvZ"
    ap.append(("#" + mb, G_.glass_group(zl, MV_LW, MV_BH, layout="Top")))
    ap.append(("#" + zl, lab(None, "ZONES  -  where the merchants roam", 12, "dim", bold=True, w=MV_LW, h=20)))
    for k_ in range(MV_ZN):
        r_ = "%sMvZ%d" % (MT, k_)
        ap.append(("#" + zl, G_.glass_group(r_, MV_LW, MV_ZH, role="inset", layout="Left", pad={"horizontal": 8}, anchor={"top": 6})))
        rx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(rx, MV_ZTW, MV_ZH, layout="Top", anchor={"right": 8})))
        ap.append(("#" + rx, lab(r_ + "N", "", 15, "accentHi", bold=True, w=MV_ZTW, h=24, anchor={"top": 4})))
        ap.append(("#" + rx, lab(r_ + "S", "", 13, "text", bold=True, w=MV_ZTW, h=20)))
        ap.append(("#" + rx, lab(r_ + "R", "", 12, "xp", w=MV_ZTW, h=18)))
        ap.append(("#" + rx, lab(r_ + "Q", "", 12, "xp", w=MV_ZTW, h=18)))
        ap.append(("#" + r_, G_.glass_button(r_ + "G", "Shop here", "secondary", w=120, h=30, size=13, anchor={"top": 33})))
    ap.append(("#" + zl, lab(MT + "MvZx", "", 12, "dim", w=MV_LW, h=18, anchor={"top": 6})))
    assert 20 + MV_ZN * (MV_ZH + 6) + 24 <= MV_BH and 4 + 24 + 20 + 18 + 18 <= MV_ZH, "0.3.72: the zones fit"
    ap.append(("#" + mb, "Group { Anchor: (Width: 10); }"))
    sr = MT + "MvS"
    ap.append(("#" + mb, G_.glass_group(sr, MV_RW, MV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + sr, lab(MT + "MvSh", "", 15, "accentHi", bold=True, w=MV_RI, h=24)))
    ap.append(("#" + sr, lab(MT + "MvSs", "", 12, "dim", w=MV_RI, h=18)))
    for k_ in range(MV_SN):
        r_ = "%sMvR%d" % (MT, k_)
        ap.append(("#" + sr, G_.glass_group(r_, MV_RI, MV_SH, role="panel", layout="Left", pad={"horizontal": 6}, anchor={"top": 4})))
        q_ = r_ + "Q"
        hm, kids = SUI.keep_holder(q_, MV_SQ, MV_SQ, [SUI.keep_at0("Group #%sBg { Anchor: (Width: %d, Height: %d); }" % (r_, MV_SQ, MV_SQ))], anchor={"top": 2})
        ap.append(("#" + r_, hm))
        ap.extend(kids)
        ap.append(("#" + q_, SUI.keep_at0(G_.glass_grid(r_ + "I", 1, 1, drag=False, slot=MV_SQ - 6, icon=MV_SQ - 14)).replace("Left: 0, Top: 0", "Left: 3, Top: 3")))
        rx = r_ + "X"
        ap.append(("#" + r_, G_.glass_group(rx, MV_STW, MV_SH, layout="Top", anchor={"left": 8})))
        ap.append(("#" + rx, lab(r_ + "N", "", 14, "row", bold=True, w=MV_STW, h=24, anchor={"top": 5})))
        ap.append(("#" + rx, lab(r_ + "T", "", 11, "xp", bold=True, w=MV_STW, h=18)))
        ap.append(("#" + r_, lab(r_ + "P", "", 15, "xp", bold=True, w=MV_PW, h=MV_SH, halign="End", anchor={"right": 8})))
        ap.append(("#" + r_, G_.glass_button(r_ + "B", "Buy", "primary", w=MV_BW, h=32, size=13, anchor={"top": 12})))
    pg = MT + "MvP"
    ap.append(("#" + sr, G_.glass_group(pg, MV_RI, 30, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pg, G_.glass_button(MT + "MvPp", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
    ap.append(("#" + pg, lab(MT + "MvPg", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
    ap.append(("#" + pg, G_.glass_button(MT + "MvPn", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))
    ap.append(("#" + sr, lab(MT + "MvSn", "", 12, "dim", w=MV_RI, h=18, anchor={"top": 4})))
    assert 20 + 24 + 18 + MV_SN * (MV_SH + 4) + 36 + 22 <= MV_BH, "0.3.72: the stock fits"
    out.append(("M", ap, bm + [("#" + MT + "MvRf", "mrf"), ("#" + MT + "MvPp", "mpg:-1"), ("#" + MT + "MvPn", "mpg:1")]))
    return out
'''
P.rep('''MT_AP, MT_BINDS = _mt_page()
SUI.check_page(MT_AP, MT)
for _p, _mk in MT_AP:
    SUI.check_markup(_mk, prefix=MT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.59: the market screen never scrolls"
_mt_ids = set(i_ for _p, mk_ in MT_AP for i_ in SUI._static_ids(mk_))''', MT_VIEWS_PY.lstrip("\n") + '''

MT_AP0, MT_BINDS = _mt_page()
MT_VIEWS = _mt_views()
# 0.3.72: the home cards = the body group and everything inside it (section H); the views go in before the hint row (the window's next child)
_mt_home = set([MT + "Body"])
MT_SEC = []
for _p, _mk in MT_AP0:
    _ids = set(SUI._static_ids(_mk))
    _pid = None if _p is None else SUI.render(_p).lstrip("#")
    if (MT + "Body") in _ids or _pid in _mt_home:
        _mt_home |= _ids
        MT_SEC.append("H")
    else:
        MT_SEC.append("0")
_hi = [k_ for k_, (_p, _mk) in enumerate(MT_AP0) if (MT + "Hints") in SUI._static_ids(_mk)]
assert len(_hi) == 1 and MT_SEC[:_hi[0]].count("H") > 100 and "H" not in MT_SEC[_hi[0]:], "0.3.72: the home cards come right before the hint row"
MT_AP = SUI.Appends(list(MT_AP0[:_hi[0]]))
MT_SECA = MT_SEC[:_hi[0]]
for _v, _vap, _vb in MT_VIEWS:
    MT_AP.extend(_vap)
    MT_SECA += [_v] * len(_vap)
MT_AP.extend(SUI.Appends(list(MT_AP0[_hi[0]:])))
MT_SECA += MT_SEC[_hi[0]:]
MT_AP.sets = list(MT_AP0.sets)
for _v, _vap, _vb in MT_VIEWS:
    MT_AP.sets.extend(_vap.sets)
assert len(MT_SECA) == len(MT_AP)
SUI.check_page(MT_AP, MT)
for _p, _mk in MT_AP:
    SUI.check_markup(_mk, prefix=MT, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.59: the market screen never scrolls"
_mt_ids = set(i_ for _p, mk_ in MT_AP for i_ in SUI._static_ids(mk_))
_mt_vsec = {}
for _v, _vap, _vb in MT_VIEWS:
    for _p, _mk in _vap:
        for _i in SUI._static_ids(_mk):
            _mt_vsec[_i] = _v
_mt_sec_of = lambda i_: "H" if i_ in _mt_home else _mt_vsec.get(i_, "0")''')
P.rep('''MT_DYN = (["Coins", "Close", "Full", "Cap", "Q", "Find",''', '''MT_DYN = (["Coins", "Close", "Cap", "Q", "Find",''')
P.rep('''          + ["A%d%s" % (k_, x_) for k_ in range(MT_AN) for x_ in ("", "I", "N", "S", "Go")] + ["Ab0", "Ab1", "Ab2"])''',
      '''          + ["A%d%s" % (k_, x_) for k_ in range(MT_AN) for x_ in ("", "I", "N", "S", "Go")] + ["Ab0", "Ab1", "Ab2"]
          # 0.3.72: the views (no Full page)
          + ["OvH", "OvT0", "OvT1", "OvT2", "OvI", "OvIQ", "OvT", "OvB", "OvSd", "OvBd", "OvF", "OvA", "OvABox", "OvAll", "OvAn", "OvP", "OvPBox", "OvBest",
             "OvBeat", "OvNa", "OvNb", "OvW0", "OvW1", "OvCf", "OvGo", "OvChk", "OvX1", "OvX2", "OvOh", "OvCl", "OvClaim", "OvMore",
             "MvH", "MvT0", "MvT1", "MvT2", "MvK", "MvW", "MvRf", "MvZx", "MvSh", "MvSs", "MvP", "MvPp", "MvPg", "MvPn", "MvSn"]
          + ["OvN%d" % k_ for k_ in range(7)] + ["OvIF%d" % (f_ + 1) for f_ in range(len(MT_FRAMES))]
          + ["OvR%d%s" % (k_, x_) for k_ in range(OV_ON) for x_ in ("", "I", "N", "S", "C")]
          + ["MvZ%d%s" % (k_, x_) for k_ in range(MV_ZN) for x_ in ("", "N", "S", "R", "Q", "G")]
          + ["MvR%d%s" % (k_, x_) for k_ in range(MV_SN) for x_ in ("", "Q", "Bg", "I", "N", "T", "P", "B")])''')
P.rep('''MT_RUNTIME_IDS = ["Kt%d" % k_ for k_ in range(MT_CATN)] + ["Am%d" % k_ for k_ in range(len(MT_AMT))] + ["Bc%d" % k_ for k_ in range(len(MT_BAMT))]''',
      '''MT_RUNTIME_IDS = ["Kt%d" % k_ for k_ in range(MT_CATN)] + ["Am%d" % k_ for k_ in range(len(MT_AMT))] + ["Bc%d" % k_ for k_ in range(len(MT_BAMT))] \\
    + ["Sd0", "Sd1"] + ["Mk%d" % k_ for k_ in range(MV_KN)]   # 0.3.72: the side / shop tab buttons''')
P.rep('''_mt_tok = SUI.proven_tokens(list(MT_AP))''', '''_mt_tok = SUI.proven_tokens(list(MT_AP))
assert "SkyyMtabFull" not in _mt_ids, "0.3.72: the market screen has no Full page (no old Bazaar page link)"''')
P.rep('''MT_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9]+)?\\s*\\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in MT_AP)
MT_RUNTIME_MAX = MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1      # the rail's tabs + the amount chips + the bank chips + the bank fill
MT_ELEMENTS = MT_SHELL_ELEMENTS + MT_RUNTIME_MAX''', '''_mt_cnt = lambda mk_: len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9]+)?\\s*\\{", SUI._strip_quoted(SUI.render(mk_))))
# 0.3.72: one packet = the frame + ONE section (the home cards or a view) - the budget is the frame + the biggest section
_mt_by = {}
for (_p, _mk), _s in zip(MT_AP, MT_SECA):
    _mt_by[_s] = _mt_by.get(_s, 0) + _mt_cnt(_mk)
_mt_rt = {"H": MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1, "O": OV_RUNTIME_MAX, "M": MV_RUNTIME_MAX}   # the rail / chips / bank fill; the sides; tabs + squares
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOM")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOM")
print("0.3.72 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOM")))''')
P.rep('''MT_LK, MT_LP, MT_LB = [], [], []
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
assert MT_LK[0] == "A" and MT_LP[0] == "", "0.3.59: the page data starts with the root"''', '''MT_LK, MT_LP, MT_LB, MT_LS = [], [], [], []
for (_p, _mk), _s in zip(MT_AP, MT_SECA):
    MT_LK.append("A")
    MT_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    MT_LB.append(SUI.render(_mk))
    MT_LS.append(_s)
for _i, _pr, _v in MT_AP.sets:
    MT_LK.append("S")
    MT_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    MT_LB.append(_v)
    MT_LS.append(_mt_sec_of(SUI.render(_i).lstrip("#")))
for _s, _a in MT_BINDS + [b_ for _v, _vap, _vb in MT_VIEWS for b_ in _vb]:
    MT_LK.append("E")
    MT_LP.append(_s)
    MT_LB.append(_a)
    MT_LS.append(_mt_sec_of(_s.lstrip("#")))
for _v, _vap, _vb in MT_VIEWS:
    assert all(_mt_sec_of(s_.lstrip("#")) == _v for s_, _a in _vb), "0.3.72: a view's bindings name its own elements"
assert MT_LK[0] == "A" and MT_LP[0] == "" and MT_LS[0] == "0", "0.3.59: the page data starts with the root"
assert all(_mt_sec_of(s_.lstrip("#")) in ("0", "H") for s_, _a in MT_BINDS), "0.3.72: the home bindings are frame / home elements"''')

# ---- the MarketTabData: the sections + the views' numbers, texts and run-time markup
P.rep('''F(mtd, "public static final String[] RCOL = %s;" % jarr(MT_RCOL))''', '''F(mtd, "public static final String[] RCOL = %s;" % jarr(MT_RCOL))
# 0.3.72 (oldmenu4): the section letter of each page data line (0 frame / H home / O Bazaar orders / M Merchants) + the views
F(mtd, "public static final String LS = %s;" % jstr("".join(MT_LS)))
F(mtd, "public static final String[] KNAME = %s;" % jarr(MV_KNAME))
for _n, _v in (("OVN", OV_ON), ("MVKN", MV_KN), ("MVZN", MV_ZN), ("MVSN", MV_SN)):
    F(mtd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("SIDE", MT_SIDE), ("SQ", MT_SQ), ("NONEC", SUI.COLOR["disabled"]), ("OVCAP", MT_VTXT["ovcap"]), ("OVCHK", MT_VTXT["ovchk"]),
               ("OVOLD", MT_VTXT["ovold"]), ("OVPICK", MT_VTXT["ovpick"]), ("MVCAP", MT_VTXT["mvcap"]), ("MVOLD", MT_VTXT["mvold"]),
               ("MVOFF", MT_VTXT["mvoff"]), ("MVFAR", MT_VTXT["mvfar"]), ("MVFAIL", MT_VTXT["mvfail"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))''')
P.rep('''           "public long upUntil;", "public String bup;", "public long taxBp;", "public String btyped;",''',
      '''           "public long upUntil;", "public String bup;", "public long taxBp;", "public String btyped;",
           # 0.3.72 (oldmenu4): the view (0 home, 1 Bazaar orders, 2 Merchants) and each view's state
           "public int view;", "public int oside;", "public String oAmt;", "public String oPrice;", "public boolean wSeen;", "public boolean wOk;",
           "public long wQ;", "public long wP;", "public long wT;", "public String wWhy;", "public boolean ovOk;", "public long[] nBest;",
           "public long[] nBeat;", "public long[] nAll;", "public String[] ovIds;", "public int mtab;", "public String mzone;", "public boolean mok;",
           "public String mptok;", "public String mlast;", "public String[] mzKeys;", "public boolean[] mzNear;", "public String[] msZone;",
           "public String[] msNpc;", "public String[] msId;", "public String[] msPrice;", "public int[] msLeft;", "public int mpage;", "public int mpages;",''')
P.rep('''  this.upUntil = 0L;
  this.bup = "";
  this.builds = 0;
  this.answers = 0;
  this.calls = 0;
}""")
# 0.3.62: THE WORLD SCREEN DATA''', '''  this.upUntil = 0L;
  this.bup = "";
  this.view = 0;           // 0.3.72 (oldmenu4)
  this.oside = 0;
  this.oAmt = "";
  this.oPrice = "";
  this.wSeen = false;
  this.wOk = false;
  this.wQ = -1L;
  this.wP = -1L;
  this.wT = -1L;
  this.wWhy = "";
  this.ovOk = false;
  this.nBest = new long[2];
  this.nBeat = new long[2];
  this.nAll = new long[2];
  this.ovIds = new String[0];
  this.mtab = 0;
  this.mzone = "";
  this.mok = false;
  this.mptok = "";
  this.mlast = null;
  this.mzKeys = new String[0];
  this.mzNear = new boolean[0];
  this.msZone = new String[0];
  this.msNpc = new String[0];
  this.msId = new String[0];
  this.msPrice = new String[0];
  this.msLeft = new int[0];
  this.mpage = 0;
  this.mpages = 1;
  this.builds = 0;
  this.answers = 0;
  this.calls = 0;
}""")
# 0.3.62: THE WORLD SCREEN DATA''')

# ---- the home's YOUR ORDERS: an 8-field o| line (the order id) reads the same; the texts name the orders view
P.rep('''    } else if (i == 0 && no == 0) t = "No open orders - place them on the Bazaar page (Buy order / Sell offer).";
    else if (i == os.size() && no > os.size()) t = (no - os.size()) + " more on the Bazaar page";''',
      '''    } else if (i == 0 && no == 0) t = "No open orders - Buy order / Sell offer above places one.";   // 0.3.72
    else if (i == os.size() && no > os.size()) t = (no - os.size()) + " more - Buy order shows them all";''')

# ---- the views' fill methods (before build: methods before their callers)
FILL_JAVA = r'''# ---- 0.3.72 (oldmenu4): THE VIEWS. Helpers: a typed whole number (-1 = not one); the merchant's rarity square / its colour; a duration
M(mtab, r"""
public static long pnum(String s) {
  if (s == null) return -1L;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c >= '0' && c <= '9') { sb.append(c); continue; }
    if (c == ',' || c == ' ' || c == '_') continue;
    return -1L;
  }
  if (sb.length() == 0 || sb.length() > 15) return -1L;
  try { return Long.parseLong(sb.toString()); } catch (Throwable t) { return -1L; }
}""")
M(mtab, r"""
public static String hexOf(String s) {
  if (s == null || s.length() < 7 || s.charAt(0) != '#') return null;
  for (int i = 1; i < 7; i++) {
    char c = s.charAt(i);
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))) return null;
  }
  return s.substring(0, 7);
}""")
# the rarity square SkyyMerchants sends (MerchPage.rbg: #rrggbb(0.4)); anything else (or the 'no rarity' grey) = no square - never into markup
M(mtab, r"""
public static String sqOf(String s) {
  String h = hexOf(s);
  if (h == null || h.equalsIgnoreCase(@PKG@.MarketTabData.NONEC)) return null;
  if (s.length() == 7) return s;
  if (s.length() > 14 || s.length() < 10 || s.charAt(7) != '(' || s.charAt(s.length() - 1) != ')') return null;
  for (int i = 8; i < s.length() - 1; i++) {
    char c = s.charAt(i);
    if (!((c >= '0' && c <= '9') || c == '.')) return null;
  }
  return s;
}""")
M(mtab, r"""
public static String dur(long ms) {
  if (ms < 0L) return "?";
  long s = ms / 1000L;
  if (s < 60L) return s + "s";
  long m = s / 60L;
  if (m < 60L) return m + "m " + (s % 60L) + "s";
  return (m / 60L) + "h " + (m % 60L) + "m";
}""")
M(mtab, r"""
public static String[] wrap2(String s, int n) {
  if (s == null) s = "";
  if (s.length() <= n) return new String[] { s, "" };
  int c = s.lastIndexOf(' ', n);
  if (c < n / 2) c = n;
  return new String[] { s.substring(0, c).trim(), @PKG@.MenuUtil.clip(s.substring(c).trim(), n) };
}""")
# a stock row's Style Guide 15 tooltip: the name in its rarity colour, the tier tag, the price gold, left, the yellow footer
M(mtab, r"""
public static String mtip(String name, String hex, int tier, long price, int left) {
  String lf = String.valueOf((char) 10);
  StringBuilder sb = new StringBuilder();
  sb.append(col(hex != null ? hex : @PKG@.MarketTabData.SOFT, name));
  if (tier > 0 && tier < 99) sb.append(lf).append(col(@PKG@.MarketTabData.TAGCOL, "T" + tier));
  sb.append(lf).append(lf);
  sb.append(col(@PKG@.MarketTabData.SOFT, "Price  ")).append(col(@PKG@.MarketTabData.GOLD, price >= 0L ? money(price) + " coins" : "-"));
  sb.append(lf).append(col(@PKG@.MarketTabData.SOFT, "Left this visit  ")).append(col(@PKG@.MarketTabData.GOLD, left > 0 ? String.valueOf(left) : "sold out"));
  sb.append(lf).append(lf).append(col(@PKG@.MarketTabData.FOOT, left > 0 ? "Buy: press twice to buy" : "Sold out - it restocks when the merchant moves"));
  return sb.toString();
}""")
# the bank balance for the top bar while a view is open (the bank card itself is only on the home cards)
M(mtab, r"""
public String bankBal() {
  Object o = null;
  if (@PKG@.InvCraft.fn("bank:fn:panel") != null) o = call("bank:fn:panel", this.playerRef.getUuid());
  if (!(o instanceof Object[])) return "";
  Object[] r = (Object[]) o;
  return r.length >= 10 && "ok".equals(r[0]) ? String.valueOf(r[3]) : "";
}""")
# ---- BAZAAR ORDERS: d| the item, n| (side 0 / 1) the band + chips + All, w| the typed amount + price checked, o| (8 fields) my orders, m| claims
M(mtab, r"""
public void fillOv(@UCB@ b, @UEB@ ev, String[] d, String[] n0, String[] n1, String[] w, java.util.ArrayList os, String[] m, String[] hd) {
  boolean on = d != null && d.length >= 15;
  int sd = this.oside == 1 ? 1 : 0;
  String[] n = sd == 0 ? n0 : n1;
  this.ovOk = (n0 != null && n0.length >= 9) || (n1 != null && n1.length >= 9);
  String ak = String.valueOf((char) 64) + "A";
  String pk = String.valueOf((char) 64) + "P";
  String h = "";
  if ("0".equals(hd[7])) h = "Trading is off - the coin bank (SkyyCoins) is not loaded";
  else if ("1".equals(hd[11])) h = "The order book is paused - an admin has been told";
  b.set("#SkyyMtabOvH.Text", h);
  for (int i = 0; i < 2; i++) {
    b.appendInline("#SkyyMtabOvSd", @PKG@.MarketTabData.SIDE.replace("{I}", "Sd" + i).replace("{S}", i == sd ? @PKG@.MarketTabData.ST_CATSEL : @PKG@.MarketTabData.ST_CAT));
    b.set("#SkyyMtabSd" + i + ".Text", i == 0 ? "Buy order" : "Sell offer");
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabSd" + i, @EVD@.of("a", "ovs:" + i).append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"));
  }
  long b1 = on ? nl(d[5], -1L) : -1L, s1 = on ? nl(d[6], -1L) : -1L, hv = on ? nl(d[7], 0L) : 0L, vd = on ? nl(d[8], 0L) : 0L;
  b.set("#SkyyMtabOvI.Slots", @PKG@.InvPage.act(one(on ? cell(d[1], 1, d[2], tip(d[2], rar(d[3]), d[4], b1, s1, hv, "")) : new @IGS@())));
  hold(b, "SkyyMtabOvN", 7, on ? rar(d[3]) : 0, on ? d[2] : "No item picked");
  frame(b, "SkyyMtabOvI", on ? rar(d[3]) : 0);
  b.set("#SkyyMtabOvT.Text", !on ? "" : (d[4].length() > 0 ? d[4] + "    " : "") + "You have " + money(hv) + (vd > 0L ? "  (" + money(vd) + " in the Void)" : ""));
  long bid = on ? nl(d[10], 0L) : 0L, ask = on ? nl(d[11], 0L) : 0L;
  b.set("#SkyyMtabOvB.Text", !on ? "" : (bid > 0L ? "Best buy order " + money(bid) : "No buy orders yet") + "   -   " + (ask > 0L ? "lowest sell offer " + money(ask) : "no sell offers yet"));
  boolean form = on && n != null && n.length >= 9;
  this.wSeen = false;
  this.wOk = false;
  this.wQ = -1L;
  this.wP = -1L;
  this.wT = -1L;
  this.wWhy = "";
  if (!on) b.set("#SkyyMtabOvBd.Text", @PKG@.MarketTabData.OVPICK);
  else if (!form) b.set("#SkyyMtabOvBd.Text", @PKG@.MarketTabData.OVOLD);
  else {
    long lo = nl(n[2], -1L), hi = nl(n[3], -1L), best = nl(n[4], -1L), beat = nl(n[6], -1L), all = nl(n[8], -1L);
    this.nBest[sd] = best;
    this.nBeat[sd] = beat;
    this.nAll[sd] = all;
    String what = sd == 0 ? "buy order" : "sell offer";
    b.set("#SkyyMtabOvBd.Text", hi < lo || hi <= 0L ? "No room for a new " + what + " right now - the prices are too close." : "Prices a " + what + " can use now: " + money(lo) + " - " + money(hi) + " coins each");
    b.set("#SkyyMtabOvAll.Text", all > 0L ? "All  " + money(all) : "All");
    b.set("#SkyyMtabOvAn.Text", (sd == 0 ? "All = what you can afford at the best price" : "All = everything you have (inventory + the Void)") + (all > 0L ? ": " + money(all) : ": none"));
    b.set("#SkyyMtabOvBest.Text", best > 0L ? "Best price  " + money(best) : "Best price");
    b.set("#SkyyMtabOvBeat.Text", beat > 0L ? "Beat by 1  " + money(beat) : "Beat by 1");
    b.set("#SkyyMtabOvNa.Text", @PKG@.MenuUtil.clip(n[5], 110));
    b.set("#SkyyMtabOvNb.Text", @PKG@.MenuUtil.clip(n[7], 110));
    b.set("#SkyyMtabOvA.Value", this.oAmt);     // fix: always (an emptied box after a placed order shows empty, even on a partial redraw)
    b.set("#SkyyMtabOvP.Value", this.oPrice);
    boolean conf = false;
    if (w != null && w.length >= 7 && ni(w[1], -1) == sd) {
      this.wSeen = true;
      this.wQ = nl(w[2], -1L);
      this.wP = nl(w[3], -1L);
      this.wT = nl(w[4], -1L);
      this.wWhy = w[5];
      this.wOk = this.wWhy.length() == 0 && this.wQ > 0L && this.wP > 0L && this.wT > 0L;
      conf = "1".equals(w[6]);
    }
    String tl = this.wOk ? (sd == 0 ? "Buy order: " : "Sell offer: ") + money(this.wQ) + " x " + money(this.wP) + " = " + money(this.wT) + " coins"
        + (sd == 0 ? "  - held from your purse now" : "  - the items leave now, coins come as it fills" + taxNote())
        : (this.wSeen && this.wWhy.length() > 0 ? this.wWhy : "Type an amount and a price, then Check total");
    hold(b, "SkyyMtabOvW", 2, this.wOk ? 0 : 1, @PKG@.MenuUtil.clip(tl, 120));
    b.set("#SkyyMtabOvCf.Text", this.wOk && conf ? "Over your 'Confirm buys from' amount: the first press asks, press Place again within 10 s." : "");
    b.set("#SkyyMtabOvGo.Text", sd == 0 ? "PLACE BUY ORDER" : "PLACE SELL OFFER");
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabOvGo", @EVD@.of("a", "ovgo").append("t", this.tok).append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabOvChk", @EVD@.of("a", "ovchk").append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyMtabOvA", @EVD@.of("a", "ovchk").append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"), false);
    ev.addEventBinding(@BT@.Validating, "#SkyyMtabOvP", @EVD@.of("a", "ovchk").append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabOvAll", @EVD@.of("a", "ovall").append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabOvBest", @EVD@.of("a", "ovbest").append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabOvBeat", @EVD@.of("a", "ovbeat").append(ak, "#SkyyMtabOvA.Value").append(pk, "#SkyyMtabOvP.Value"));
  }
  b.set("#SkyyMtabOvF.Visible", form);
  // MY ORDERS (the read's open orders with their ids) + Claim all
  int no = ni(hd[9], 0);
  b.set("#SkyyMtabOvOh.Text", "MY ORDERS  " + no);
  long cw = m != null && m.length >= 4 ? nl(m[1], 0L) : 0L, iw = m != null && m.length >= 4 ? nl(m[2], 0L) : 0L;
  this.claims = m != null && m.length >= 4 ? ni(m[3], 0) : 0;
  b.set("#SkyyMtabOvCl.Text", this.claims <= 0 ? "" : "Ready: " + (cw > 0L ? money(cw) + " coins" : "") + (cw > 0L && iw > 0L ? " + " : "") + (iw > 0L ? money(iw) + " items" : ""));
  b.set("#SkyyMtabOvClaim.Visible", this.claims > 0);
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabOvClaim", @EVD@.of("a", "claim").append("t", this.tok));
  String lf = String.valueOf((char) 10);
  int nr = @PKG@.MarketTabData.OVN;
  this.ovIds = new String[nr];
  boolean ids = false;
  for (int i = 0; i < nr; i++) {
    String r = "SkyyMtabOvR" + i;
    this.ovIds[i] = "";
    String[] f = null;
    if (i < os.size()) f = (String[]) os.get(i);
    if (f == null || f.length < 7) { b.set("#" + r + ".Visible", false); continue; }
    boolean buy = "0".equals(f[1]);
    long q = nl(f[4], 0L), fl = nl(f[5], 0L), pe = nl(f[6], 0L);
    this.ovIds[i] = f.length >= 8 ? f[7] : "";
    if (this.ovIds[i].length() > 0) ids = true;
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", @PKG@.InvPage.act(one(cell(f[2], 1, f[3], col(@PKG@.MarketTabData.SOFT, f[3]) + lf + lf
        + col(@PKG@.MarketTabData.GOLD, (buy ? "Buy order  " : "Sell offer  ") + money(q) + " at " + money(pe) + " each") + lf
        + col(@PKG@.MarketTabData.SOFT, money(fl) + " / " + money(q) + " filled")))));
    b.set("#" + r + "N.Text", (buy ? "Buy order  -  " : "Sell offer  -  ") + @PKG@.MenuUtil.clip(f[3], 30));
    b.set("#" + r + "S.Text", money(q) + " at " + money(pe) + " each   -   " + money(fl) + " / " + money(q) + " filled");
    b.set("#" + r + "C.Visible", this.ovIds[i].length() > 0);
    ev.addEventBinding(@BT@.Activating, "#" + r + "C", @EVD@.of("a", "oc:" + i).append("t", this.tok));
  }
  b.set("#SkyyMtabOvMore.Text", no == 0 ? "No open orders yet." : (os.size() > 0 && !ids ? "Cancel here needs SkyyBazaar 0.2.8." : (no > os.size() ? (no - os.size()) + " more orders" : "")));
}""")
M(mtab, r"""
public void ovFail(@UCB@ b) {
  this.ovOk = false;
  this.wSeen = false;
  this.wOk = false;
  this.ovIds = new String[0];
  hold(b, "SkyyMtabOvN", 7, 0, "The Bazaar is not ready");
  frame(b, "SkyyMtabOvI", 0);
  b.set("#SkyyMtabOvBd.Text", "The Bazaar could not be read right now - try again in a moment.");
  b.set("#SkyyMtabOvF.Visible", false);
  b.set("#SkyyMtabOvOh.Text", "MY ORDERS");
  b.set("#SkyyMtabOvClaim.Visible", false);
  for (int i = 0; i < @PKG@.MarketTabData.OVN; i++) b.set("#SkyyMtabOvR" + i + ".Visible", false);
}""")
# ---- MERCHANTS: merchants:fn:tab apply(Object[] { UUID, Integer shop tab }) -> ok| header, k| tabs, z| zones, s| stock (only at the merchant), x|
M(mtab, r"""
public void fillMv(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  boolean has = @PKG@.InvCraft.fn("merchants:fn:tab") != null && @PKG@.InvCraft.fn("merchants:fn:tabact") != null;
  Object o = has ? call("merchants:fn:tab", new Object[] { u, Integer.valueOf(this.mtab) }) : null;
  this.calls = this.calls + (has ? 1 : 0);
  String s = o instanceof String ? (String) o : null;
  this.mlast = s;
  this.mok = s != null && s.startsWith("ok|");
  String[] ls = this.mok ? s.split("\n") : new String[0];
  String[] hd = this.mok ? sp(ls[0], 8) : new String[0];
  if (hd.length < 8) this.mok = false;
  this.mptok = this.mok ? hd[1] : "";
  java.util.ArrayList ks = new java.util.ArrayList(), zs = new java.util.ArrayList(), ss = new java.util.ArrayList();
  String x = "";
  for (int i = 1; this.mok && i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) ks.add(sp(l, 3));
    else if (l.startsWith("z|")) { String[] f = sp(l, 13); if (f.length >= 13) zs.add(f); }
    else if (l.startsWith("s|")) { String[] f = sp(l, 9); if (f.length >= 9) ss.add(f); }
    else if (l.startsWith("x|")) x = l.substring(2);
  }
  int nk = @PKG@.MarketTabData.MVKN;
  String[] kn = new String[nk];
  for (int i = 0; i < nk; i++) {
    kn[i] = @PKG@.MarketTabData.KNAME[i];
    for (int j = 0; j < ks.size(); j++) {
      String[] f = (String[]) ks.get(j);
      if (f.length >= 3 && String.valueOf(i).equals(f[1]) && f[2].length() > 0) kn[i] = f[2];
    }
    b.appendInline("#SkyyMtabMvK", @PKG@.MarketTabData.SIDE.replace("{I}", "Mk" + i).replace("{S}", i == this.mtab ? @PKG@.MarketTabData.ST_CATSEL : @PKG@.MarketTabData.ST_CAT));
    b.set("#SkyyMtabMk" + i + ".Text", @PKG@.MenuUtil.clip(kn[i], 18));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabMk" + i, @EVD@.of("a", "mk:" + i));
  }
  String head = "";
  if (!has) head = @PKG@.HubBar.get("hub:tab:market:merchants") instanceof Object[] ? @PKG@.MarketTabData.MVOLD : @PKG@.MarketTabData.MVOFF;
  else if (!this.mok) head = @PKG@.MarketTabData.MVFAIL;
  else if ("0".equals(hd[2])) head = "The merchants are away (switched off on this server).";
  b.set("#SkyyMtabMvH.Text", head);
  long purse = this.mok ? nl(hd[4], -1L) : -1L;
  b.set("#SkyyMtabMvW.Text", !this.mok ? "" : "Purse " + money(purse) + "     Buy within " + @PKG@.MenuUtil.clip(hd[7], 6) + " blocks of the merchant");
  // the stock shown = the merchant picked with Shop here (still near) or the first one you stand at
  boolean keep = false;
  for (int j = 0; j < zs.size(); j++) {
    String[] f = (String[]) zs.get(j);
    if ("1".equals(f[11]) && f[1].equals(this.mzone)) keep = true;
  }
  if (!keep) {
    this.mzone = "";
    for (int j = 0; j < zs.size() && this.mzone.length() == 0; j++) {
      String[] f = (String[]) zs.get(j);
      if ("1".equals(f[11])) this.mzone = f[1];
    }
  }
  String zname = "";
  String npc = "";
  int nz = @PKG@.MarketTabData.MVZN;
  this.mzKeys = new String[nz];
  this.mzNear = new boolean[nz];
  for (int k = 0; k < nz; k++) {
    String r = "SkyyMtabMvZ" + k;
    this.mzKeys[k] = "";
    this.mzNear[k] = false;
    if (k >= zs.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) zs.get(k);
    boolean out = "1".equals(f[4]), near = "1".equals(f[11]);
    this.mzKeys[k] = f[1];
    this.mzNear[k] = near;
    if (f[1].equals(this.mzone)) { zname = f[2]; npc = f[5]; }
    long ms = nl(f[9], -1L), dist = nl(f[10], -1L);
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(f[2], 40) + (f[3].length() > 0 ? "    Lv " + @PKG@.MenuUtil.clip(f[3], 12) : ""));
    b.set("#" + r + "S.Text", near ? "You are at this merchant" + (dist >= 0L ? " - " + dist + " blocks away" : "") + "  -  moves in " + dur(ms)
        : (out ? "Out in this zone  -  moves in " + dur(ms) : "No merchant in this zone right now"));
    String[] rw = wrap2(!out ? "" : (f[12].length() > 0 ? "Rumour: " + f[12] : "No rumour yet - look around the zone."), 70);
    b.set("#" + r + "R.Text", rw[0]);
    b.set("#" + r + "Q.Text", rw[1]);
    b.set("#" + r + "G.Visible", near && !f[1].equals(this.mzone));
    ev.addEventBinding(@BT@.Activating, "#" + r + "G", @EVD@.of("a", "mz:" + k).append("t", this.tok));
  }
  b.set("#SkyyMtabMvZx.Text", x.length() > 0 ? @PKG@.MenuUtil.clip(x, 90) : (zs.size() > nz ? "+" + (zs.size() - nz) + " more zones" : (this.mok && zs.size() == 0 ? "No merchant zones in this world." : "")));
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int j = 0; j < ss.size(); j++) {
    String[] f = (String[]) ss.get(j);
    if (this.mzone.length() > 0 && f[1].equals(this.mzone) && String.valueOf(this.mtab).equals(f[2])) rows.add(f);
  }
  int n = @PKG@.MarketTabData.MVSN;
  this.mpages = (rows.size() + n - 1) / n;
  if (this.mpages < 1) this.mpages = 1;
  if (this.mpage >= this.mpages) this.mpage = this.mpages - 1;
  if (this.mpage < 0) this.mpage = 0;
  String tn = this.mtab >= 0 && this.mtab < nk ? kn[this.mtab] : "";
  b.set("#SkyyMtabMvSh.Text", this.mzone.length() == 0 ? "STOCK" : "STOCK  -  " + @PKG@.MenuUtil.clip(zname, 30).toUpperCase() + "  -  " + tn.toUpperCase());
  b.set("#SkyyMtabMvSs.Text", this.mzone.length() == 0 ? (this.mok ? @PKG@.MarketTabData.MVFAR : "")
      : (rows.size() == 0 ? "Nothing in this tab this visit - try another tab." : "Sorted by tier, then name. Prices hold for this visit."));
  this.msZone = new String[n];
  this.msNpc = new String[n];
  this.msId = new String[n];
  this.msPrice = new String[n];
  this.msLeft = new int[n];
  for (int i = 0; i < n; i++) {
    String r = "SkyyMtabMvR" + i;
    int ix = this.mpage * n + i;
    this.msZone[i] = "";
    this.msNpc[i] = "";
    this.msId[i] = "";
    this.msPrice[i] = "";
    this.msLeft[i] = 0;
    if (ix >= rows.size()) { b.set("#" + r + ".Visible", false); continue; }
    String[] f = (String[]) rows.get(ix);
    int tr = ni(f[6], 99);
    long pr = nl(f[7], -1L);
    int left = ni(f[8], 0);
    this.msZone[i] = f[1];
    this.msNpc[i] = npc;
    this.msId[i] = f[3];
    this.msPrice[i] = f[7];
    this.msLeft[i] = left;
    String sq = sqOf(f[5]);
    String hx = null;
    if (sq != null) { hx = hexOf(sq); b.appendInline("#" + r + "Bg", @PKG@.MarketTabData.SQ.replace("{C}", sq)); }
    b.set("#" + r + ".Visible", true);
    b.set("#" + r + "I.Slots", @PKG@.InvPage.act(one(cell(f[3], 1, f[4], mtip(f[4], hx, tr, pr, left)))));
    b.set("#" + r + "N.Text", @PKG@.MenuUtil.clip(f[4], 40));
    b.set("#" + r + "T.Text", (tr > 0 && tr < 99 ? "T" + tr + "    " : "") + (left > 0 ? left + " left" : "Sold out"));
    b.set("#" + r + "P.Text", pr >= 0L ? money(pr) + " coins" : "-");
    b.set("#" + r + "B.Visible", left > 0 && pr >= 0L);
    ev.addEventBinding(@BT@.Activating, "#" + r + "B", @EVD@.of("a", "mb:" + i).append("t", this.tok));
  }
  b.set("#SkyyMtabMvPg.Text", "Page " + (this.mpage + 1) + " / " + this.mpages);
  b.set("#SkyyMtabMvP.Visible", this.mpages > 1);
  b.set("#SkyyMtabMvSn.Text", this.mok ? "Merchants move and restock on their own - finding them stays the hunt." : "");
}""")
'''
P.rep('''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.MarketTabData.LP[i];
    String y = @PKG@.MarketTabData.LB[i];''', FILL_JAVA + '''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;
  String ls = @PKG@.MarketTabData.LS;   // 0.3.72 (oldmenu4): the frame + the current section only
  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : 'H');
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    char sc = ls.charAt(i);
    if (sc != '0' && sc != cur) continue;
    String x = @PKG@.MarketTabData.LP[i];
    String y = @PKG@.MarketTabData.LB[i];''')
P.rep('''  String bank = "";
  try { bank = fillBank(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the bank failed: " + t); }''',
      '''  String bank = "";
  if (this.view == 0) { try { bank = fillBank(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the bank failed: " + t); } }
  else { try { bank = bankBal(); } catch (Throwable t) { bank = ""; } }   // 0.3.72: a view shows the balance only''')
P.rep('''  try { fillAh(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the auction card failed: " + t); }
  Object o = call("bazaar:fn:tab", new Object[] { u, this.cat, this.query, this.sel, Integer.valueOf(this.page), Integer.valueOf(@PKG@.MarketTabData.RN), Integer.valueOf(this.amt) });''',
      '''  if (this.view == 2) {   // 0.3.72 (oldmenu4): the merchants view reads SkyyMerchants only
    try { fillMv(b, ev); } catch (Throwable t) { this.mok = false; this.msId = new String[0]; @PKG@.MenuUtil.warn("market screen: the merchants view failed: " + t); }
    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.MVCAP);
    return;
  }
  if (this.view == 0) { try { fillAh(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("market screen: the auction card failed: " + t); } }
  // 0.3.72: SkyyBazaar 0.2.8's opt-in arguments (max order lines with ids, the order side, the typed amount + price); 0.2.7 ignores them
  boolean ovw = this.view == 1;
  Object o = call("bazaar:fn:tab", new Object[] { u, this.cat, this.query, this.sel, Integer.valueOf(this.page), Integer.valueOf(@PKG@.MarketTabData.RN), Integer.valueOf(this.amt),
      Integer.valueOf(@PKG@.MarketTabData.OVN), Integer.valueOf(ovw ? this.oside : -1), Long.valueOf(ovw ? pnum(this.oAmt) : -1L), Long.valueOf(ovw ? pnum(this.oPrice) : -1L) });''')
P.rep('''    this.claims = 0;
    for (int i = 0; i < @PKG@.MarketTabData.RN; i++) b.set("#SkyyMtabR" + i + ".Visible", false);
    b.set("#SkyyMtabLt.Text", "BAZAAR");
    b.set("#SkyyMtabLn.Text", "The Bazaar could not be read right now - try again in a moment, or open the Full page.");''',
      '''    this.claims = 0;
    if (this.view == 1) {   // 0.3.72: the orders view says so, nothing can be placed
      ovFail(b);
      b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : "The Bazaar is not ready yet");
      return;
    }
    for (int i = 0; i < @PKG@.MarketTabData.RN; i++) b.set("#SkyyMtabR" + i + ".Visible", false);
    b.set("#SkyyMtabLt.Text", "BAZAAR");
    b.set("#SkyyMtabLn.Text", "The Bazaar could not be read right now - try again in a moment.");''')
P.rep('''  String[] d = null, q = null, m = null;
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) ks.add(sp(l, 2));
    else if (l.startsWith("r|")) rs.add(sp(l, 8));
    else if (l.startsWith("d|")) d = sp(l, 15);
    else if (l.startsWith("q|")) q = sp(l, 7);
    else if (l.startsWith("o|")) os.add(sp(l, 7));
    else if (l.startsWith("m|")) m = sp(l, 4);
  }
  if (d != null && d.length >= 15) this.sel = d[1];      // the row mark below knows the selection of THIS read''',
      '''  String[] d = null, q = null, m = null, n0 = null, n1 = null, w = null;
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) ks.add(sp(l, 2));
    else if (l.startsWith("r|")) rs.add(sp(l, 8));
    else if (l.startsWith("d|")) d = sp(l, 15);
    else if (l.startsWith("q|")) q = sp(l, 7);
    else if (l.startsWith("o|")) os.add(sp(l, 8));     // 0.3.72: + the order id (SkyyBazaar 0.2.8, 8 arguments); 7 fields read the same
    else if (l.startsWith("m|")) m = sp(l, 4);
    else if (l.startsWith("n|")) { String[] f = sp(l, 9); if (f.length >= 9) { if ("1".equals(f[1])) n1 = f; else if ("0".equals(f[1])) n0 = f; } }
    else if (l.startsWith("w|")) w = sp(l, 7);
  }
  if (d != null && d.length >= 15) this.sel = d[1];      // the row mark below knows the selection of THIS read
  if (this.view == 1) {   // 0.3.72 (oldmenu4): the Bazaar orders view
    try { fillOv(b, ev, d, n0, n1, w, os, m, hd); } catch (Throwable t) { this.ovOk = false; this.wSeen = false; this.wOk = false; @PKG@.MenuUtil.warn("market screen: the orders view failed: " + t); }
    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.OVCAP);
    return;
  }''')
# the Market tab while a view is open = back to the cards
P.rep('''  if (i == 3) { say("You are on Market"); return; }''',
      '''  if (i == 3) {
    if (this.view != 0) { this.view = 0; this.tcap = ""; redraw(); return; }   // 0.3.72: a view open = back to the cards
    say("You are on Market");
    return;
  }''')

# ---- the views' actions (after bankMove: act / redraw / say / amtClean exist)
ACT_JAVA = r'''# ---- 0.3.72 (oldmenu4): the views' actions. Every one answers with ONE packet (a redraw with the answer in the caption, or a caption).
M(mtab, r"""
public static int viewOf(String a) {
  if (a.startsWith("ov") || a.startsWith("oc:")) return 1;
  if (a.startsWith("mk:") || a.startsWith("mz:") || a.startsWith("mb:") || a.startsWith("mpg:") || a.equals("mrf")) return 2;
  if (a.equals("claim")) return 3;
  if (a.startsWith("cat:") || a.equals("find") || a.equals("fclear") || a.startsWith("pg:") || a.startsWith("amt:") || a.startsWith("bamt:") || a.startsWith("rs:")
      || a.startsWith("ahr:") || a.startsWith("ah:") || a.equals("buy") || a.equals("sell") || a.equals("dep") || a.equals("wd") || a.equals("up") || a.equals("bank")) return 0;
  return -1;
}""")
M(mtab, r"""
public void goView(int v) {
  this.answered = true;
  this.view = v < 0 || v > 2 ? 0 : v;
  this.mpage = 0;
  this.wSeen = false;
  this.tcap = "";
  redraw();
}""")
M(mtab, r"""
public void keep(String ta, String tp) {
  this.oAmt = amtClean(ta);
  this.oPrice = amtClean(tp);
}""")
# Best price / Beat by 1 / All: the read's own values (n| = BzPage.price0 / all0) into the typed boxes, then the total is checked by the redraw
M(mtab, r"""
public void ovChip(int k, String ta, String tp) {
  this.answered = true;
  keep(ta, tp);
  int sd = this.oside == 1 ? 1 : 0;
  long v = k == 0 ? this.nAll[sd] : (k == 1 ? this.nBest[sd] : this.nBeat[sd]);
  if (!this.ovOk || v <= 0L) {
    say(k == 0 ? (sd == 0 ? "You cannot afford any at the best price right now" : "You have none of it to sell") : "There is no price to copy yet - type one");
    return;
  }
  if (k == 0) this.oAmt = String.valueOf(v);
  else this.oPrice = String.valueOf(v);
  this.tcap = "";
  redraw();
}""")
# PLACE: only the amount / price / total of the w| line DRAWN in this packet; typed values that differ = checked first (a redraw, nothing sent)
M(mtab, r"""
public void ovGo(String ta, String tp) {
  this.answered = true;
  if (this.sel.length() == 0) { say("Pick an item on the Market page first"); return; }
  if (!this.ovOk) { say(@PKG@.MarketTabData.OVOLD); return; }
  long q = pnum(ta), p = pnum(tp);
  keep(ta, tp);
  if (!this.wSeen || q != this.wQ || p != this.wP) { this.tcap = @PKG@.MarketTabData.OVCHK; redraw(); return; }
  String what = this.oside == 1 ? "Sell offer" : "Buy order";
  if (!this.wOk) { say(what + ": " + (this.wWhy.length() > 0 ? this.wWhy : "type an amount and a price")); return; }
  Object o = call("bazaar:fn:tabact", new Object[] { this.playerRef.getUuid(), this.ptok, this.oside == 1 ? "ask" : "bid", this.sel + "|" + this.wQ + "|" + this.wP + "|" + this.wT });
  if (o == null) { say(@PKG@.InvCraft.fn("bazaar:fn:tabact") == null ? "The Bazaar is not on this server right now - nothing changed" : "That could not run here - nothing changed"); return; }
  String r = String.valueOf(o).trim();
  if (r.startsWith("+")) { this.oAmt = ""; this.oPrice = ""; }   // placed: the boxes empty (a second press cannot repeat it)
  this.tcap = @PKG@.InvPage.bare(r);
  redraw();
}""")
M(mtab, r"""
public void ovCancel(int k) {
  this.answered = true;
  if (k < 0 || k >= this.ovIds.length || this.ovIds[k] == null || this.ovIds[k].length() == 0) { say("Nothing to cancel there"); return; }
  act("cancel", this.ovIds[k]);
}""")
M(mtab, r"""
public void mPick(int k) {
  this.answered = true;
  if (k < 0 || k >= this.mzKeys.length || !this.mzNear[k]) { say("You are not at that merchant - walk to it first"); return; }
  this.mzone = this.mzKeys[k];
  this.mpage = 0;
  this.tcap = "";
  redraw();
}""")
# BUY: merchants:fn:tabact buy zone|npc|tab|item|price shown (the read's profile key); SkyyMerchants asks first, the same press again buys
M(mtab, r"""
public void mBuy(int k) {
  this.answered = true;
  if (!this.mok) { say("The merchants are not ready - nothing was bought"); return; }
  if (k < 0 || k >= this.msId.length || this.msId[k] == null || this.msId[k].length() == 0) { say("Nothing there"); return; }
  if (this.msLeft[k] <= 0) { say("Sold out - the merchant restocks when it moves."); return; }
  Object o = call("merchants:fn:tabact", new Object[] { this.playerRef.getUuid(), this.mptok, "buy",
      this.msZone[k] + "|" + this.msNpc[k] + "|" + this.mtab + "|" + this.msId[k] + "|" + this.msPrice[k] });
  if (o == null) { say(@PKG@.InvCraft.fn("merchants:fn:tabact") == null ? "Merchants are not on this server right now - nothing was bought" : "That could not run here - nothing was bought"); return; }
  this.tcap = @PKG@.InvPage.bare(String.valueOf(o));
  redraw();
}""")
'''
P.rep('''M(mtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', ACT_JAVA + '''M(mtab, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''    if (a.startsWith("tab:")) { tabGo(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("full")) { hub("market", "bazaar", "the Bazaar page"); return; }
    if (a.equals("mer")) { hub("market", "merchants", "Merchants"); return; }''',
      '''    if (a.startsWith("tab:")) { tabGo(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    // 0.3.72 (oldmenu4): the old Bazaar page (Full page / Buy order / Sell offer) and the Merchants page are views of this screen
    int need = viewOf(a);
    if (need >= 0 && !(need == this.view || (need == 3 && this.view <= 1))) { say("That button is not on this page - nothing changed"); return; }
    if (a.startsWith("vw:")) {
      int v = @PKG@.InvPage.toInt(a.substring(3), 0);
      if (v == this.view) { this.tcap = ""; redraw(); return; }
      goView(v);
      return;
    }
    if (a.equals("mer")) { goView(2); return; }
    String ak = String.valueOf((char) 64) + "A", pk = String.valueOf((char) 64) + "P";
    if (a.startsWith("ovs:")) { keep(@PKG@.InvPage.val(d, ak), @PKG@.InvPage.val(d, pk)); this.oside = @PKG@.InvPage.toInt(a.substring(4), 0) == 1 ? 1 : 0; this.tcap = ""; redraw(); return; }
    if (a.equals("ovchk")) { keep(@PKG@.InvPage.val(d, ak), @PKG@.InvPage.val(d, pk)); this.tcap = ""; redraw(); return; }
    if (a.equals("ovall")) { ovChip(0, @PKG@.InvPage.val(d, ak), @PKG@.InvPage.val(d, pk)); return; }
    if (a.equals("ovbest")) { ovChip(1, @PKG@.InvPage.val(d, ak), @PKG@.InvPage.val(d, pk)); return; }
    if (a.equals("ovbeat")) { ovChip(2, @PKG@.InvPage.val(d, ak), @PKG@.InvPage.val(d, pk)); return; }
    if (a.startsWith("mk:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), 0);
      this.mtab = k < 0 || k >= @PKG@.MarketTabData.MVKN ? 0 : k;
      this.mpage = 0;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.equals("mrf")) { this.tcap = ""; redraw(); return; }
    if (a.startsWith("mpg:")) {
      int dm = @PKG@.InvPage.toInt(a.substring(4), 0);
      int nm = this.mpage + (dm < 0 ? -1 : 1);
      if (nm < 0 || nm >= this.mpages) { say(nm < 0 ? "This is the first page" : "This is the last page"); return; }
      this.mpage = nm;
      this.tcap = "";
      redraw();
      return;
    }''')
P.rep('''    if (a.equals("order") || a.equals("offer")) {
      if (this.selName.length() == 0) { say("Pick an item first"); return; }
      opener("bazaar:fn:open", new Object[] { this.playerRef.getUuid(), this.selName }, "market", "bazaar", "the Bazaar page");
      return;
    }''', '''    if (a.equals("order") || a.equals("offer")) {   // 0.3.72: the Bazaar orders view on that side (fresh boxes)
      if (this.selName.length() == 0) { say("Pick an item first"); return; }
      this.oside = a.equals("offer") ? 1 : 0;
      this.oAmt = "";
      this.oPrice = "";
      goView(1);
      return;
    }''')
P.rep('''    if (a.startsWith("rs:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || k >= this.rowIds.length) { say("Nothing there"); return; }''', '''    // 0.3.72 (oldmenu4): the views' token actions
    if (a.equals("ovgo")) { ovGo(@PKG@.InvPage.val(d, ak), @PKG@.InvPage.val(d, pk)); return; }
    if (a.startsWith("oc:")) { ovCancel(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.startsWith("mz:")) { mPick(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.startsWith("mb:")) { mBuy(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.startsWith("rs:")) {
      int k = @PKG@.InvPage.toInt(a.substring(3), -1);
      if (k < 0 || k >= this.rowIds.length) { say("Nothing there"); return; }''')

# ======================================================================= the ratchet: OLD_LEFT shrinks by the two rows this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"),
    ("market", "auctions"), ("market", "bazaar"), ("market", "merchants"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),''',
      '''# 0.3.72 (oldmenu4): market:bazaar (no Full page; Buy order / Sell offer = the Bazaar orders view - SkyyBazaar 0.2.8 tabact bid / ask / cancel) and
# market:merchants (See merchants = the Merchants view - SkyyMerchants 0.1.10 merchants:fn:tab / tabact buy) are gone. market:auctions stays (own round).
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"),
    ("market", "auctions"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.72: no system / command / class"
_i = P.s.index
assert _i("public static long pnum(String s)") < _i("public static String sqOf(String s)") < _i("public void fillOv(@UCB@ b, @UEB@ ev, String[] d,") \
    < _i("public void fillMv(@UCB@ b, @UEB@ ev)") < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.pref = ref;\n  this.pst = st;\n  String lk = @PKG@.MarketTabData.LK;"), \
    "0.3.72: the view helpers before build"
assert _i("public void fillMv(@UCB@ b, @UEB@ ev)") < _i("String ls = @PKG@.MarketTabData.LS;") < _i("public void bankMove(String op, String amount)") \
    < _i("public static int viewOf(String a)") < _i("public void ovGo(String ta, String tp)") < _i("public void mBuy(int k)") \
    < _i('if (a.startsWith("mb:")) { mBuy('), "0.3.72: methods before their callers"
assert _i("public static String amtClean(String s)") < _i("public void keep(String ta, String tp)"), "0.3.72: amtClean before keep"
assert 'hub("market", "bazaar"' not in P.s and 'hub("market", "merchants"' not in P.s and '"market", "bazaar", "the Bazaar page"' not in P.s \
    and "Open Merchants" not in P.s, "0.3.72: no old Bazaar / Merchants page link left in the new screens"
P.finish()


# ======================================================================= the HARNESS (every 0.3.71 check runs again on the 0.3.72 jar, plus OLD4)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


EXPECT_72 = '''EXPECT = {   # 0.3.72: the Market tab's views (Bazaar orders / Merchants), no Full page, the version strings
@@EXPECT@@
}
'''
HARNESS_OLD4_STATIC = r'''    # ---- OLD4 (0.3.72; Skyy 11-22 "build it all into the new system"): the ratchet shrank by exactly the two rows this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("market", "bazaar"), ("market", "merchants")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 2
            and ("market", "auctions") in left2_,
            "OLD4 RATCHET OLD_LEFT lost market:bazaar + market:merchants, nothing added, the Auction House kept (%d -> %d; still: %s)"
            % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('G_.glass_button(MT + "Full"' not in g and '("#" + MT + "Full", "full")' not in g and 'hub("market", "bazaar"' not in g
            and 'hub("market", "merchants"' not in g and '"market", "bazaar", "the Bazaar page"' not in g and "Open Merchants" not in g
            and "on the Bazaar page" not in g and "or open the Full page." not in g
            and "0.3.72: the market screen has no Full page (no old Bazaar page link)" in g,
            "OLD4 STATIC no Full page, no Bazaar / Merchants page link or text pointing at one (Buy order / Sell offer / See merchants = the views)")
    K.check('call("bazaar:fn:tabact", new Object[] { this.playerRef.getUuid(), this.ptok, this.oside == 1 ? "ask" : "bid", this.sel + "|" + this.wQ + "|" + this.wP + "|" + this.wT })' in g
            and 'act("cancel", this.ovIds[k]);' in g and 'call("merchants:fn:tab", new Object[] { u, Integer.valueOf(this.mtab) })' in g
            and 'call("merchants:fn:tabact", new Object[] { this.playerRef.getUuid(), this.mptok, "buy",' in g,
            "OLD4 STATIC the views call the bridges: bazaar:fn:tabact bid / ask (the drawn total) / cancel <order id>, merchants:fn:tab / tabact buy")
    K.check("0.3.72: the orders form fits" in g and "0.3.72: my orders fit" in g and "0.3.72: the zones fit" in g and "0.3.72: the stock fits" in g
            and "0.3.72: the view markups are proven" in g and "0.3.72: the home cards come right before the hint row" in g,
            "OLD4 STATIC the build asserts every view fits 1080, its run-time markup is proven, the sections are in order")
'''
HARNESS_OLD4 = r'''    # ---- OLD4 (0.3.72, round oldmenu4): THE MARKET TAB = THE OLD BAZAAR ORDERS + MERCHANTS PAGES (the Auction House stays)
    def sel_ok4(pk_):
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

    def has4(pk_, ident):
        return any(re.search(r"#%s *\{" % ident, str(c_.text or "")) for c_ in cmds_of(pk_))

    def appended4(pk_, parent):
        return [str(c_.text or "") for c_ in cmds_of(pk_) if str(c_.selector) == "#" + parent and c_.text is not None]
    txt4 = lambda cm_, k_: str(sval(cm_, "#SkyyMtab%s.Text" % k_))
    val4 = lambda cm_, k_: sval(cm_, "#SkyyMtab%s.Value" % k_)
    bind4 = lambda p_, act_: [b_ for b_ in binds_of(p_) if ('"a":"%s"' % act_) in b_[2].replace(" ", "")]
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    for k_ in ("merchants:fn:tab", "merchants:fn:tabact"):
        BR.remove(k_)
    MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    MW["tok"], MW["purse"], MW["readNull"], MW["full"], MW["claims"] = "prof-A", 50000, False, False, 0
    MW["have"]["Rock_Stone"] = 200
    p_ = mt_ev({"a": "cat:0"}, "OLD4 open")
    cm = cmap(p_)
    K.check(has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabFull") and not has4(p_, "SkyyMtabOv") and not has4(p_, "SkyyMtabMv") and not sel_ok4(p_),
            "OLD4 OPEN the home packet = the frame + the cards only (no Full page, no view); every set / binding names a drawn element %s" % sel_ok4(p_)[:3])
    K.check('Text: "Buy order"' in mk_of(p_, "SkyyMtabOrd") and 'Text: "Sell offer"' in mk_of(p_, "SkyyMtabOff") and 'Text: "See merchants"' in mk_of(p_, "SkyyMtabMgo")
            and len(MW["reads"][-1]) == 11 and MW["reads"][-1][7:11] == [str(int(MTD.OVN)), "-1", "-1", "-1"],
            "OLD4 HOME Buy order / Sell offer / See merchants; the read sends SkyyBazaar 0.2.8's opt-in arguments (12 order lines, no side) (%s)" % MW["reads"][-1][7:])
    # ======== MERCHANTS
    p_ = mt_ev({"a": "mer"}, "OLD4 MER See merchants without SkyyMerchants 0.1.10")
    cm = cmap(p_)
    K.check(int(MS.view) == 2 and has4(p_, "SkyyMtabMv") and not has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabOv") and not sel_ok4(p_)
            and txt4(cm, "MvH") in (str(MTD.MVOLD), str(MTD.MVOFF)) and not vis3(cm, "MvZ0") and not vis3(cm, "MvR0")
            and [txt4(cm, "Mk%d" % k_) for k_ in range(4)] == ["Weapons", "Mounts", "Pet eggs", "Augments"] and cap3(p_) == str(MTD.MVCAP),
            "OLD4 MER FALL no merchants:fn:tab = the view says which version it needs; the 4 shop tabs; no zones, no stock (%s)" % txt4(cm, "MvH"))
    MCH = {"tok": "prof-A", "near": ["zone2"], "on": 1, "null": False, "reads": [], "acts": [], "arm": None, "bought": []}
    STK = {0: [("Weapon_Sword_Iron", "Iron Sword", "#2770b7(0.4)", 3, 400, 2), ("Weapon_Sword_Copper", "Copper Sword", "#797b7c(0.15)", 2, 150, 1),
               ("Weapon_Axe_Bad", "Bad Axe", "red); Background: (TexturePath: x", 4, 900, 1), ("Weapon_Bow_Old", "Old Bow", "#bb8a2c(0.4)", 5, 1200, 0)]
              + [("Weapon_Fake_%d" % i_, "Blade %02d" % i_, "#2770b7", 6, 2000 + i_, 3) for i_ in range(8)],
           1: [("Skyy_Mount_Horse", "Horse", "#3e9049(0.4)", 99, 5000, 1)], 2: [], 3: [("Skyy_Aug_Brute_1", "Brute Augment I", "#c9d2dd(0.4)", 1, 300, 4)]}
    ZON = [("zone1", "Zone 1 - Emerald Grove", "1-20", 1, 250000, "Seen near the old well, past the big oak where the river bends twice and the road forks north to the hills"),
           ("zone2", "Zone 2 - Howling Sands", "20-40", 1, 61000, "Camped by the dunes"), ("zone3", "Zone 3 - Borea", "40-60", 0, -1, ""),
           ("zone4", "Zone 4 - Cliffs", "60-80", 1, 5000, "By the cliffs")]

    def f_mtab(o):
        a = list(o)
        tab = int(a[1])
        MCH["reads"].append([str(a[0]), tab])
        if MCH["null"]:
            return None
        L = ["ok|%s|%d|1|%d|%d|default|6" % (MCH["tok"], MCH["on"], MW["purse"], tab)]
        L += ["k|%d|%s" % (i_, n_) for i_, n_ in enumerate(["Weapons", "Mounts", "Pet eggs", "Augments"])]
        for k_, nm_, band_, out_, ms_, rum_ in ZON:
            near_ = k_ in MCH["near"] and out_ == 1
            L.append("z|%s|%s|%s|%d|%s|%d|%d|%d|%d|%d|%d|%s" % (k_, nm_, band_, out_, ("npc-" + k_) if near_ else "", 1234 if near_ else 0, 64 if near_ else 0,
                                                               -567 if near_ else 0, ms_, 3 if near_ else -1, 1 if near_ else 0, rum_ if out_ else ""))
            if near_:
                for r_ in sorted(STK.get(tab, []), key=lambda x_: (x_[3], x_[1].lower())):
                    L.append("s|%s|%d|%s|%s|%s|%d|%d|%d" % (k_, tab, r_[0], r_[1], r_[2], r_[3], r_[4], r_[5]))
        return "\n".join(L)

    def f_mact(o):
        a = [str(x_) for x_ in list(o)]
        MCH["acts"].append(a)
        if a[1] != MCH["tok"]:
            MCH["arm"] = None
            return "=Your profile changed - here are this profile's merchants. Nothing changed."
        f = a[3].split("|")
        if a[2] != "buy" or len(f) != 5:
            return "-Unknown merchant action."
        if MCH["arm"] != a[3]:
            MCH["arm"] = a[3]
            return "=Buy %s for %s coins? Press Buy again within 10 s." % (f[3], f[4])
        MCH["arm"] = None
        MCH["bought"].append(f[3])
        MW["purse"] -= int(f[4])
        return "+You bought %s for %s coins." % (f[3], f[4])
    BR.put("merchants:fn:tab", Fn(f_mtab))
    BR.put("merchants:fn:tabact", Fn(f_mact))
    p_ = mt_ev({"a": "mrf"}, "OLD4 MER Refresh with SkyyMerchants")
    cm = cmap(p_)
    zt_ = " ".join(txt4(cm, "MvZ%d%s" % (k_, x_)) for k_ in range(4) for x_ in ("N", "S", "R", "Q"))
    K.check(MCH["reads"][-1] == [uk3, 0] and txt4(cm, "MvH") == "" and txt4(cm, "MvZ0N") == "Zone 1 - Emerald Grove    Lv 1-20"
            and txt4(cm, "MvZ0S") == "Out in this zone  -  moves in 4m 10s" and txt4(cm, "MvZ0R").startswith("Rumour: Seen near the old well") and txt4(cm, "MvZ0Q") != ""
            and txt4(cm, "MvZ1S") == "You are at this merchant - 3 blocks away  -  moves in 1m 1s" and txt4(cm, "MvZ2S") == "No merchant in this zone right now"
            and txt4(cm, "MvZ2R") == "" and vis3(cm, "MvZ3") and not vis3(cm, "MvZ4") and not vis3(cm, "MvZ0G") and not vis3(cm, "MvZ1G")
            and "1234" not in zt_ and "-567" not in zt_ and "Purse 50,000" in txt4(cm, "MvW") and not sel_ok4(p_),
            "OLD4 MER the zones: name + band, out / moves in, the rumour (wrapped), near + blocks away; NO coordinates drawn (finding stays a hunt) %s" % sel_ok4(p_)[:3])
    K.check(txt4(cm, "MvSh") == "STOCK  -  ZONE 2 - HOWLING SANDS  -  WEAPONS" and [txt4(cm, "MvR%dN" % k_) for k_ in range(4)] == ["Copper Sword", "Iron Sword", "Bad Axe", "Old Bow"]
            and txt4(cm, "MvR1T") == "T3    2 left" and txt4(cm, "MvR1P") == "400 coins" and vis3(cm, "MvR1B") and not vis3(cm, "MvR3B") and txt4(cm, "MvR3T") == "T5    Sold out"
            and vis3(cm, "MvR8") and txt4(cm, "MvPg") == "Page 1 / 2" and vis3(cm, "MvP"),
            "OLD4 MER the stock of the merchant you stand at, in SkyyMerchants' tier order: T + left, price, Buy (none when sold out), 9 a page")
    sq1_, sq0_, sq2_ = appended4(p_, "SkyyMtabMvR1Bg"), appended4(p_, "SkyyMtabMvR0Bg"), appended4(p_, "SkyyMtabMvR2Bg")
    K.check(len(sq1_) == 1 and "Background: #2770b7(0.4);" in sq1_[0] and sq0_ == [] and sq2_ == [] and "#2770b7" in cm.get("#SkyyMtabMvR1I.Slots", "")
            and "T3" in cm.get("#SkyyMtabMvR1I.Slots", "") and "press twice" in cm.get("#SkyyMtabMvR1I.Slots", "") and "TexturePath: x" not in str([str(c_.text or "") for c_ in cmds_of(p_)]),
            "OLD4 MER rarity: the square behind the icon + the name colour in the tooltip (Iron Sword #2770b7); the 'no rarity' grey and a bad colour never reach the markup")
    p_ = mt_ev({"a": "mpg:1"}, "OLD4 MER next page")
    cm = cmap(p_)
    K.check([txt4(cm, "MvR%dN" % k_) for k_ in range(3)] == ["Blade 05", "Blade 06", "Blade 07"] and not vis3(cm, "MvR3") and txt4(cm, "MvPg") == "Page 2 / 2", "OLD4 MER > = page 2")
    p_ = mt_ev({"a": "mpg:1"}, "OLD4 MER past the last page")
    K.check("last page" in cap3(p_), "OLD4 MER past the last page = a caption")
    p_ = mt_ev({"a": "mpg:-1"}, "OLD4 MER back")
    n0_ = len(MCH["acts"])
    old_ = str(MS.tok)
    p_ = mt_ev({"a": "mb:1", "t": str(MS.tok)}, "OLD4 MER Buy (first press)")
    K.check(MCH["acts"][-1] == [uk3, "prof-A", "buy", "zone2|npc-zone2|0|Weapon_Sword_Iron|400"] and MCH["bought"] == []
            and cap3(p_) == "Buy Weapon_Sword_Iron for 400 coins? Press Buy again within 10 s.",
            "OLD4 MER Buy = merchants:fn:tabact buy zone|npc|tab|item|price shown with the read's profile key; the first press = SkyyMerchants' question word for word (%s)" % MCH["acts"][-1:])
    p_ = mt_ev({"a": "mb:1", "t": old_}, "OLD4 MER SAFE an older drawing's Buy")
    K.check(len(MCH["acts"]) == n0_ + 1 and "The page changed" in cap3(p_), "OLD4 MER SAFE a double click (the older drawing) = no second call")
    pu_ = MW["purse"]
    p_ = mt_ev({"a": "mb:1", "t": str(MS.tok)}, "OLD4 MER Buy (second press)")
    K.check(MCH["bought"] == ["Weapon_Sword_Iron"] and MW["purse"] == pu_ - 400 and cap3(p_) == "You bought Weapon_Sword_Iron for 400 coins.",
            "OLD4 MER the same press again = bought once, SkyyMerchants' answer word for word")
    n0_ = len(MCH["acts"])
    p_ = mt_ev({"a": "mb:3", "t": str(MS.tok)}, "OLD4 MER SAFE a forged Buy on a sold-out row")
    p2_ = mt_ev({"a": "mb:20", "t": str(MS.tok)}, "OLD4 MER SAFE a forged Buy on no row")
    K.check(len(MCH["acts"]) == n0_ and "Sold out" in cap3(p_) and cap3(p2_) == "Nothing there", "OLD4 MER SAFE sold out / no row = a caption, no call")
    MCH["tok"] = "prof-B"
    p_ = mt_ev({"a": "mb:0", "t": str(MS.tok)}, "OLD4 MER SAFE a profile switch")
    K.check(MCH["acts"][-1][1] == "prof-A" and "profile changed" in cap3(p_) and MCH["bought"] == ["Weapon_Sword_Iron"], "OLD4 MER SAFE a profile switch between read and click = SkyyMerchants refuses, nothing bought")
    p_ = mt_ev({"a": "mb:0", "t": str(MS.tok)}, "OLD4 MER after the redraw")
    K.check(MCH["acts"][-1][1] == "prof-B", "OLD4 MER after the redraw the new profile key is sent")
    MCH["tok"] = "prof-A"
    p_ = mt_ev({"a": "mk:3"}, "OLD4 MER the Augments tab")
    cm = cmap(p_)
    K.check(MCH["reads"][-1][1] == 3 and txt4(cm, "MvR0N") == "Brute Augment I" and txt4(cm, "MvSh").endswith("AUGMENTS") and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabMk3")
            and not vis3(cm, "MvP"), "OLD4 MER a shop tab = that tab read (Augments selected), one page = no pager")
    p_ = mt_ev({"a": "mk:2"}, "OLD4 MER an empty tab")
    K.check("Nothing in this tab" in txt4(cmap(p_), "MvSs") and not vis3(cmap(p_), "MvR0"), "OLD4 MER an empty tab says so")
    p_ = mt_ev({"a": "mk:0"}, "OLD4 MER Weapons")
    MCH["near"] = ["zone2", "zone4"]
    p_ = mt_ev({"a": "mrf"}, "OLD4 MER two merchants near")
    cm = cmap(p_)
    K.check(str(MS.mzone) == "zone2" and vis3(cm, "MvZ3G") and not vis3(cm, "MvZ1G"), "OLD4 MER two merchants near: the shown one stays, Shop here on the other")
    p_ = mt_ev({"a": "mz:3", "t": str(MS.tok)}, "OLD4 MER Shop here")
    K.check(str(MS.mzone) == "zone4" and txt4(cmap(p_), "MvSh").startswith("STOCK  -  ZONE 4"), "OLD4 MER Shop here = that merchant's stock")
    p_ = mt_ev({"a": "mz:0", "t": str(MS.tok)}, "OLD4 MER SAFE Shop here on a far merchant")
    K.check(str(MS.mzone) == "zone4" and "not at that merchant" in cap3(p_), "OLD4 MER SAFE a forged Shop here on a merchant you are not at = a caption")
    MCH["near"] = []
    n0_ = len(MCH["acts"])
    p_ = mt_ev({"a": "mrf"}, "OLD4 MER far from every merchant")
    cm = cmap(p_)
    K.check(txt4(cm, "MvSs") == str(MTD.MVFAR) and not vis3(cm, "MvR0") and txt4(cm, "MvSh") == "STOCK" and str(MS.mzone) == "", "OLD4 MER far away: no stock, no Buy - the hunt line")
    p_ = mt_ev({"a": "mb:0", "t": str(MS.tok)}, "OLD4 MER SAFE a forged Buy far away")
    K.check(len(MCH["acts"]) == n0_ and cap3(p_) == "Nothing there", "OLD4 MER SAFE a forged Buy while far away = no call")
    MCH["near"] = ["zone2"]
    MCH["on"] = 0
    p_ = mt_ev({"a": "mrf"}, "OLD4 MER switched off")
    K.check("away" in txt4(cmap(p_), "MvH"), "OLD4 MER merchants switched off = said in the head")
    MCH["on"] = 1
    MCH["null"] = True
    p_ = mt_ev({"a": "mrf"}, "OLD4 MER the read fails")
    K.check(txt4(cmap(p_), "MvH") == str(MTD.MVFAIL) and not vis3(cmap(p_), "MvZ0"), "OLD4 MER FALL the read = null: said, no zones")
    p_ = mt_ev({"a": "mb:0", "t": str(MS.tok)}, "OLD4 MER FALL Buy while it cannot be read")
    K.check("not ready" in cap3(p_), "OLD4 MER FALL no buy while it cannot be read")
    MCH["null"] = False
    n1_ = len(MW["acts"])
    p_ = mt_ev({"a": "buy", "t": str(MS.tok)}, "OLD4 SAFE a home button in the merchants view")
    K.check(len(MW["acts"]) == n1_ and "not on this page" in cap3(p_), "OLD4 SAFE a forged home action (BUY NOW) in a view = a caption, no call")
    p_ = mt_ev({"a": "tab:3"}, "OLD4 the Market tab in a view")
    K.check(int(MS.view) == 0 and has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabMv"), "OLD4 the Market tab in a view = the cards again (no back button)")
    p_ = mt_ev({"a": "mer"}, "OLD4 MER again")
    p_ = mt_ev({"a": "vw:0"}, "OLD4 the Market sub-tab")
    K.check(int(MS.view) == 0 and has4(p_, "SkyyMtabBody"), "OLD4 the Market sub-tab = the cards")
    # ======== BAZAAR ORDERS
    OB = {"orders": [["ord-1", 0, "Rock_Stone", "Stone", 640, 412, 5], ["ord-2", 1, "Wood_Oak_Trunk", "Oak Log", 128, 0, 9]],
          "arm": None, "conf": 1000, "old": False, "moment": False, "acts": [], "next": 3}
    BAND = {0: (4, 7, 6, "Best = the highest buy order + 1", 7, "Beat best by 1 = 7"), 1: (5, 9, 5, "Best = the lowest sell offer", 4, "Beat best by 1 = 4")}

    def f_btab8(o):
        a = list(o)
        base = f_btab(o)
        if base is None or OB["old"] or len(a) < 8:
            return base
        omax, side, q, p = int(a[7]), int(a[8]), int(a[9]), int(a[10])
        L = [l_ for l_ in base.split("\n") if not l_.startswith("o|")]
        h_ = L[0].split("|")
        h_[9] = str(len(OB["orders"]))
        L[0] = "|".join(h_)
        dl_ = [l_ for l_ in L if l_.startswith("d|")]
        if dl_:
            iid = dl_[0].split("|")[1]
            for sd in (0, 1):
                lo, hi, best, bn, beat, btn = BAND[sd]
                al = MW["purse"] // best if sd == 0 else MW["have"].get(iid, 0)
                L.append("n|%d|%d|%d|%d|%s|%d|%s|%d" % (sd, lo, hi, best, bn, beat, btn, al))
            if side in (0, 1):
                lo, hi = BAND[side][0], BAND[side][1]
                tot = q * p if q > 0 and p > 0 else -1
                hv_ = MW["have"].get(iid, 0)
                why = ("Type how many" if q < 1 else ("Type a price" if p < 1 else ("The price must be %d - %d" % (lo, hi) if p < lo or p > hi else
                       ("You need %d coins - you have %d" % (tot, MW["purse"]) if side == 0 and tot > MW["purse"] else ("You only have %d" % hv_ if side == 1 and q > hv_ else "")))))
                L.append("w|%d|%d|%d|%d|%s|%d" % (side, q, p, tot, why, 1 if side == 0 and tot >= OB["conf"] else 0))
        for od in OB["orders"][:omax]:
            L.append("o|%d|%s|%s|%d|%d|%d|%s" % (od[1], od[2], od[3], od[4], od[5], od[6], od[0]))
        return "\n".join(L)

    def f_bact8(o):
        a = [str(x_) for x_ in list(o)]
        if a[2] not in ("bid", "ask", "cancel"):
            return f_bact(o)
        OB["acts"].append(a)
        if a[1] != MW["tok"]:
            OB["arm"] = None
            return "=Your profile changed - here is this profile's Bazaar. Nothing changed."
        if OB["moment"]:
            OB["moment"] = False
            return "=One moment."
        if a[2] == "cancel":
            hit = [x_ for x_ in OB["orders"] if x_[0] == a[3]]
            if not hit:
                return "-That order is not open any more."
            OB["orders"].remove(hit[0])
            return "+Cancelled your order - what had not filled comes back."
        g_ = a[3].split("|")
        if len(g_) != 4:
            return "-Unknown Bazaar action."
        iid, q, p, tot = g_[0], int(g_[1]), int(g_[2]), int(g_[3])
        if q * p != tot:
            OB["arm"] = None
            return "=The total changed - look again. Nothing changed."
        if a[2] == "bid":
            if tot >= OB["conf"] and OB["arm"] != a[3]:
                OB["arm"] = a[3]
                return "=Place a buy order holding %s coins for %d Stone? Press Buy order again within 10 s." % ("{:,}".format(tot), q)
            OB["arm"] = None
            MW["purse"] -= tot
        else:
            OB["arm"] = None
            MW["have"][iid] = MW["have"].get(iid, 0) - q
        OB["orders"].append(["ord-%d" % OB["next"], 0 if a[2] == "bid" else 1, iid, "Stone" if iid == "Rock_Stone" else iid, q, 0, p])
        OB["next"] += 1
        return "+%s placed: %d at %d each." % ("Buy order" if a[2] == "bid" else "Sell offer", q, p)
    BR.put("bazaar:fn:tab", Fn(f_btab8))
    BR.put("bazaar:fn:tabact", Fn(f_bact8))
    p_ = mt_ev({"a": "rs:0", "t": str(MS.tok)}, "OLD4 ORD pick Stone")
    K.check(str(MS.sel) == "Rock_Stone", "OLD4 ORD Stone picked on the Market page")
    p_ = mt_ev({"a": "order"}, "OLD4 ORD Buy order")
    cm = cmap(p_)
    K.check(int(MS.view) == 1 and int(MS.oside) == 0 and has4(p_, "SkyyMtabOv") and not has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabMv") and not sel_ok4(p_)
            and MW["reads"][-1][7:11] == [str(int(MTD.OVN)), "0", "-1", "-1"] and cap3(p_) == str(MTD.OVCAP),
            "OLD4 ORD Buy order = the Bazaar orders view on the buy side (no cards sent); the read asks side 0, nothing typed %s" % sel_ok4(p_)[:3])
    K.check(txt4(cm, "OvBd") == "Prices a buy order can use now: 4 - 7 coins each" and txt4(cm, "OvBest") == "Best price  6" and txt4(cm, "OvBeat") == "Beat by 1  7"
            and txt4(cm, "OvAll") == "All  " + "{:,}".format(MW["purse"] // 6) and txt4(cm, "OvNa") == "Best = the highest buy order + 1" and vis3(cm, "OvF") and vis3(cm, "OvW1")
            and txt4(cm, "OvW1") == "Type how many" and txt4(cm, "OvGo") == "PLACE BUY ORDER" and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabSd0")
            and str(MTD.ST_CAT) in mk_of(p_, "SkyyMtabSd1") and txt4(cm, "OvT").startswith("T1 Stone    You have 200"),
            "OLD4 ORD the n| band, Best price / Beat by 1 / All chips + notes, the w| reason (red), the item, Buy order selected (%s)"
            % [txt4(cm, k_) for k_ in ("OvBd", "OvBest", "OvBeat", "OvAll", "OvNa", "OvW1", "OvGo", "OvT")])
    K.check(txt4(cm, "OvOh") == "MY ORDERS  2" and txt4(cm, "OvR0N") == "Buy order  -  Stone" and "412 / 640 filled" in txt4(cm, "OvR0S") and vis3(cm, "OvR0C")
            and txt4(cm, "OvR1N") == "Sell offer  -  Oak Log" and not vis3(cm, "OvR2") and len(bind4(p_, "oc:0")) == 1 and '"t"' in bind4(p_, "oc:0")[0][2].replace(" ", ""),
            "OLD4 ORD MY ORDERS: the read's orders with Cancel (bound with the token)")
    K.check(len([b_ for b_ in bind4(p_, "ovgo") if "SkyyMtabOvA.Value" in b_[2] and "SkyyMtabOvP.Value" in b_[2]]) == 1
            and len([b_ for b_ in binds_of(p_) if b_[0] == "Validating" and b_[1] in ("#SkyyMtabOvA", "#SkyyMtabOvP")]) == 2,
            "OLD4 ORD Place carries the token + both typed boxes; Enter in a box checks the total")
    p_ = mt_ev({"a": "ovbest", "@A": "10", "@P": ""}, "OLD4 ORD Best price")
    cm = cmap(p_)
    K.check(MW["reads"][-1][9:11] == ["10", "6"] and str(val4(cm, "OvA")) == "10" and str(val4(cm, "OvP")) == "6" and vis3(cm, "OvW0")
            and txt4(cm, "OvW0") == "Buy order: 10 x 6 = 60 coins  - held from your purse now" and txt4(cm, "OvCf") == "",
            "OLD4 ORD Best price = the n| best into the price box (the typed amount kept); the green total from the w| line (%s)" % txt4(cm, "OvW0"))
    n0_ = len(OB["acts"])
    old_ = str(MS.tok)
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "10", "@P": "6"}, "OLD4 ORD Place")
    cm = cmap(p_)
    K.check(OB["acts"][-1] == [uk3, "prof-A", "bid", "Rock_Stone|10|6|60"] and cap3(p_) == "Buy order placed: 10 at 6 each." and val4(cm, "OvA") == "" and val4(cm, "OvP") == ""
            and txt4(cm, "OvOh") == "MY ORDERS  3",
            "OLD4 ORD Place = tabact bid id|qty|price|the drawn total with the read's profile key; SkyyBazaar's answer; the boxes empty (%s)" % OB["acts"][-1:])
    p_ = mt_ev({"a": "ovgo", "t": old_, "@A": "10", "@P": "6"}, "OLD4 ORD SAFE double Place")
    K.check(len(OB["acts"]) == n0_ + 1 and "The page changed" in cap3(p_), "OLD4 ORD SAFE a double click on Place = ONE order")
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "10", "@P": "6"}, "OLD4 ORD SAFE Place after the boxes emptied")
    K.check(len(OB["acts"]) == n0_ + 1 and cap3(p_) == str(MTD.OVCHK), "OLD4 ORD SAFE pressing again with the old numbers typed back = checked first, nothing sent")
    p_ = mt_ev({"a": "ovchk", "@A": "500", "@P": "6"}, "OLD4 ORD Check total 500 x 6")
    cm = cmap(p_)
    K.check(txt4(cm, "OvW0").startswith("Buy order: 500 x 6 = 3,000 coins") and "Confirm buys from" in txt4(cm, "OvCf"), "OLD4 ORD Check total: 3,000 coins + the 'Confirm buys from' note")
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "500", "@P": "6"}, "OLD4 ORD Place over Confirm buys from (first press)")
    cm = cmap(p_)
    K.check(OB["acts"][-1][3] == "Rock_Stone|500|6|3000" and cap3(p_) == "Place a buy order holding 3,000 coins for 500 Stone? Press Buy order again within 10 s."
            and txt4(cm, "OvOh") == "MY ORDERS  3" and str(val4(cm, "OvA")) == "500", "OLD4 ORD the page's confirm: the first press = SkyyBazaar's '=' question as the caption, nothing placed, the boxes kept")
    pu_ = MW["purse"]
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "500", "@P": "6"}, "OLD4 ORD Place again")
    K.check(txt4(cmap(p_), "OvOh") == "MY ORDERS  4" and MW["purse"] == pu_ - 3000, "OLD4 ORD the same press again = placed once")
    p_ = mt_ev({"a": "ovchk", "@A": "20", "@P": "6"}, "OLD4 ORD check 20")
    n0_ = len(OB["acts"])
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "21", "@P": "6"}, "OLD4 ORD SAFE typed after the check")
    K.check(len(OB["acts"]) == n0_ and cap3(p_) == str(MTD.OVCHK) and MW["reads"][-1][9] == "21" and txt4(cmap(p_), "OvW0").startswith("Buy order: 21 x 6 = 126"),
            "OLD4 ORD SAFE NEVER A TOTAL NOT SEEN: an amount typed after the check = the new total drawn, nothing sent")
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "21", "@P": "6"}, "OLD4 ORD Place the seen total")
    K.check(OB["acts"][-1][2:] == ["bid", "Rock_Stone|21|6|126"], "OLD4 ORD then Place sends the total that was drawn")
    p_ = mt_ev({"a": "ovchk", "@A": "5", "@P": "99"}, "OLD4 ORD a price out of the band")
    n0_ = len(OB["acts"])
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "5", "@P": "99"}, "OLD4 ORD SAFE Place out of the band")
    K.check(len(OB["acts"]) == n0_ and "The price must be 4 - 7" in cap3(p_),
            "OLD4 ORD SAFE the w| reason (BzPage.whyStep) refuses up front: a caption, no call")
    p_ = mt_ev({"a": "ovchk", "@A": "5k", "@P": "6"}, "OLD4 ORD letters typed")
    K.check(MW["reads"][-1][9] == "-1" and str(val4(cmap(p_), "OvA")) == "5k", "OLD4 ORD '5k' is not a whole number: the read gets -1, the box keeps what was typed")
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "5k", "@P": "6"}, "OLD4 ORD SAFE Place with letters")
    K.check(len(OB["acts"]) == n0_ and "Type how many" in cap3(p_), "OLD4 ORD SAFE letters = SkyyBazaar's reason, no call")
    p_ = mt_ev({"a": "ovchk", "@A": "3", "@P": "6"}, "OLD4 ORD check 3")
    OB["moment"] = True
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "3", "@P": "6"}, "OLD4 ORD '=One moment.'")
    K.check(cap3(p_) == "One moment." and txt4(cmap(p_), "OvOh") == "MY ORDERS  5", "OLD4 ORD SkyyBazaar's 350 ms guard '=One moment.' = the caption, nothing placed")
    p_ = mt_ev({"a": "ovs:1", "@A": "", "@P": "6"}, "OLD4 ORD Sell offer side")
    cm = cmap(p_)
    K.check(int(MS.oside) == 1 and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabSd1") and txt4(cm, "OvGo") == "PLACE SELL OFFER" and MW["reads"][-1][8] == "1"
            and txt4(cm, "OvAll") == "All  200" and txt4(cm, "OvBd") == "Prices a sell offer can use now: 5 - 9 coins each", "OLD4 ORD Sell offer: its band, All = what you have")
    p_ = mt_ev({"a": "ovall", "@A": "", "@P": "6"}, "OLD4 ORD All")
    cm = cmap(p_)
    K.check(str(val4(cm, "OvA")) == "200" and txt4(cm, "OvW0").startswith("Sell offer: 200 x 6 = 1,200 coins"), "OLD4 ORD All = the n| all into the amount box")
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "200", "@P": "6"}, "OLD4 ORD Place a sell offer")
    K.check(OB["acts"][-1][2:] == ["ask", "Rock_Stone|200|6|1200"] and MW["have"]["Rock_Stone"] == 0 and cap3(p_).startswith("Sell offer placed"),
            "OLD4 ORD Place a sell offer = tabact ask (no confirm: the page has none for offers)")
    n0_ = len(OB["acts"])
    old_ = str(MS.tok)
    p_ = mt_ev({"a": "oc:0", "t": str(MS.tok)}, "OLD4 ORD Cancel")
    K.check(OB["acts"][-1][2:] == ["cancel", "ord-1"] and "ord-1" not in [x_[0] for x_ in OB["orders"]] and cap3(p_).startswith("Cancelled"),
            "OLD4 ORD Cancel = tabact cancel <that row's order id>")
    p_ = mt_ev({"a": "oc:0", "t": old_}, "OLD4 ORD SAFE double Cancel")
    K.check(len(OB["acts"]) == n0_ + 1 and "The page changed" in cap3(p_), "OLD4 ORD SAFE a double click on Cancel = ONE cancel")
    p_ = mt_ev({"a": "oc:11", "t": str(MS.tok)}, "OLD4 ORD SAFE Cancel on an empty row")
    K.check(len(OB["acts"]) == n0_ + 1 and cap3(p_) == "Nothing to cancel there", "OLD4 ORD SAFE Cancel on an empty row = a caption, no call")
    MW["claims"] = 2
    p_ = mt_ev({"a": "ovchk", "@A": "", "@P": ""}, "OLD4 ORD claims waiting")
    K.check(vis3(cmap(p_), "OvClaim") and "Ready: 377,600 coins + 12 items" == txt4(cmap(p_), "OvCl"), "OLD4 ORD Claim all shows in the view when something waits")
    p_ = mt_ev({"a": "claim", "t": str(MS.tok)}, "OLD4 ORD Claim all")
    K.check(MW["acts"][-1][2] == "claim" and MW["claims"] == 0, "OLD4 ORD Claim all = tabact claim (the home card's door)")
    MW["have"]["Rock_Stone"] = 50
    p_ = mt_ev({"a": "ovs:0", "@A": "", "@P": ""}, "OLD4 ORD back to the buy side")
    p_ = mt_ev({"a": "ovchk", "@A": "3", "@P": "6"}, "OLD4 ORD check before a switch")
    MW["tok"] = "prof-B"
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "3", "@P": "6"}, "OLD4 ORD SAFE a profile switch")
    K.check(OB["acts"][-1][1] == "prof-A" and "profile changed" in cap3(p_), "OLD4 ORD SAFE a profile switch between read and click = SkyyBazaar refuses, nothing placed")
    MW["tok"] = "prof-A"
    p_ = mt_ev({"a": "ovchk", "@A": "", "@P": ""}, "OLD4 ORD redraw")
    n1_ = len(MW["acts"])
    p_ = mt_ev({"a": "sell", "t": str(MS.tok)}, "OLD4 SAFE a home button in the orders view")
    K.check(len(MW["acts"]) == n1_ and "not on this page" in cap3(p_), "OLD4 SAFE a forged home action (SELL NOW) in the orders view = a caption, no call")
    MW["readNull"] = True
    p_ = mt_ev({"a": "ovchk", "@A": "", "@P": ""}, "OLD4 ORD FALL the read fails")
    cm = cmap(p_)
    K.check("could not be read" in txt4(cm, "OvBd") and not vis3(cm, "OvF") and not vis3(cm, "OvR0") and not sel_ok4(p_), "OLD4 ORD FALL the read = null: said, no form, no rows")
    n0_ = len(OB["acts"])
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "3", "@P": "6"}, "OLD4 ORD FALL Place while it cannot be read")
    K.check(len(OB["acts"]) == n0_, "OLD4 ORD FALL no order while it cannot be read")
    MW["readNull"] = False
    OB["old"] = True
    p_ = mt_ev({"a": "ovchk", "@A": "", "@P": ""}, "OLD4 ORD an older SkyyBazaar")
    cm = cmap(p_)
    K.check(txt4(cm, "OvBd") == str(MTD.OVOLD) and not vis3(cm, "OvF") and vis3(cm, "OvR0") and not vis3(cm, "OvR0C") and txt4(cm, "OvMore") == "Cancel here needs SkyyBazaar 0.2.8.",
            "OLD4 ORD FALL SkyyBazaar 0.2.7 (no n| / ids) = the view names 0.2.8, the orders listed without Cancel")
    p_ = mt_ev({"a": "ovgo", "t": str(MS.tok), "@A": "3", "@P": "6"}, "OLD4 ORD FALL forged Place on 0.2.7")
    p2_ = mt_ev({"a": "oc:0", "t": str(MS.tok)}, "OLD4 ORD FALL forged Cancel on 0.2.7")
    K.check(len(OB["acts"]) == n0_ and cap3(p_) == str(MTD.OVOLD) and cap3(p2_) == "Nothing to cancel there", "OLD4 ORD FALL forged Place / Cancel on 0.2.7 = captions, no call")
    OB["old"] = False
    p_ = mt_ev({"a": "vw:0"}, "OLD4 ORD back to the cards")
    cm = cmap(p_)
    K.check(int(MS.view) == 0 and has4(p_, "SkyyMtabBody") and str(sval(cm, "#SkyyMtabO0.Text")).startswith("Sell offer  128 Oak Log at 9 each") and not sel_ok4(p_),
            "OLD4 HOME the cards' YOUR ORDERS read the 8-field o| lines (the id never shows as the price)")
    p_ = mt_ev({"a": "find", "@Q": "zzz"}, "OLD4 ORD search for nothing")
    p_ = mt_ev({"a": "order"}, "OLD4 ORD Buy order with no item")
    K.check(int(MS.view) == 0 and "Pick an item first" in cap3(p_), "OLD4 ORD Buy order with no item picked = a caption (the cards stay)")
    p_ = mt_ev({"a": "vw:1"}, "OLD4 ORD the Bazaar orders sub-tab with no item")
    cm = cmap(p_)
    K.check(int(MS.view) == 1 and txt4(cm, "OvBd") == str(MTD.OVPICK) and not vis3(cm, "OvF"), "OLD4 ORD the sub-tab with no item = pick one first, no form")
    p_ = mt_ev({"a": "vw:2"}, "OLD4 the Merchants sub-tab")
    K.check(int(MS.view) == 2 and has4(p_, "SkyyMtabMv"), "OLD4 the Merchants sub-tab = the merchants view")
    p_ = mt_ev({"a": "tab:3"}, "OLD4 the Market tab")
    p_ = mt_ev({"a": "fclear"}, "OLD4 clear")
    K.notes.append("OLD4 ran: bazaar order calls %d, merchant reads %d, merchant calls %d" % (len(OB["acts"]), len(MCH["reads"]), len(MCH["acts"])))
    for k_ in ("merchants:fn:tab", "merchants:fn:tabact"):
        BR.remove(k_)
    BR.put("bazaar:fn:tab", Fn(f_btab))
    BR.put("bazaar:fn:tabact", Fn(f_bact))
    MW["have"]["Rock_Stone"] = 0
    MW["purse"] = 50000
'''
T.rep('''"""Harness for SkyyMenu 0.3.71 (old menu follow-up F6 - the Social tab; tools/menu_0_3_71_patch.py, round oldmenu3).''',
      '''"""Harness for SkyyMenu 0.3.72 (old menu follow-up - the Market tab; tools/menu_0_3_72_patch.py, round oldmenu4).
GENERATED by tools/menu_0_3_72_patch.py from the 0.3.71 harness (edit the patch, not this file): every 0.3.71 check runs again on the
0.3.72 jar (TAB3: Buy order = the orders view, not bazaar:fn:open; OLD3's ratchet = 'stays gone'), plus
  OLD4 STATIC   the ratchet: OLD_LEFT lost market:bazaar + market:merchants (Auction House kept); no Full page / Open Merchants / old-page
                text; the views call bazaar:fn:tabact bid / ask / cancel + merchants:fn:tab / tabact; the build asserts the views fit
       MER      (merchants:fn:tab / tabact stand-ins) See merchants: an older SkyyMerchants named; the 4 shop tabs, every zone (band, out /
                moves in, rumour wrapped, near + blocks - never a coordinate), the stock of the merchant you stand at in tier order (T,
                left, price, sold out = no Buy, 9 a page, < >), the rarity square + tooltip colour (grey / bad colours never in markup),
                Buy (first press = the question word for word, double click once, second press buys, sold out / no row / far away = no
                call, profile switch refused then the new key), shop tabs, an empty tab, Shop here (two near; a far one refused), off,
                read null; a forged home action in a view refused; the Market tab / sub-tab = the cards
       ORD      (bazaar:fn:tab 8+ arguments / tabact bid / ask / cancel stand-ins) Buy order = the orders view (the read asks the side, typed
                amount + price): n| band + chips + notes, w| reason / total; Best price, Place (the drawn total, boxes emptied, double click
                once, re-press with the old numbers = only checked), the confirm (first press '=' question, second places), typed after
                the check = checked not sent, out of band refused, letters, '=One moment.', Sell offer + All + Place (ask), Cancel <order
                id> (double click once, empty row), Claim all, profile switch, a forged home action, read null, an older SkyyBazaar (no
                form, no Cancel), the cards' YOUR ORDERS on 8-field lines, no item = pick first
       every Market packet: every b.set / append / binding names an element drawn in that packet (the frame + ONE section)
The 0.3.71 harness text follows:
Harness for SkyyMenu 0.3.71 (old menu follow-up F6 - the Social tab; tools/menu_0_3_71_patch.py, round oldmenu3).''')
T.rep('VERSION = "0.3.71"\nJAR', 'VERSION = "0.3.72"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.70.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.71.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.70.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.71.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_71_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_72_patch.py")')
T.rep('"scratch", "oldmenu3", "menu"', '"scratch", "oldmenu4", "menu"')
T.rep('ADDED = []   # 0.3.71: no new class\n', 'ADDED = []   # 0.3.72: no new class\n')
EXPECT_BODY = '''    "MarketTab": ["+f mlast", "+f mok", "+f mpage", "+f mpages", "+f mptok", "+f msId", "+f msLeft", "+f msNpc", "+f msPrice", "+f msZone", "+f mtab",
                  "+f mzKeys", "+f mzNear", "+f mzone", "+f nAll", "+f nBeat", "+f nBest", "+f oAmt", "+f oPrice", "+f oside", "+f ovIds", "+f ovOk",
                  "+f view", "+f wOk", "+f wP", "+f wQ", "+f wSeen", "+f wT", "+f wWhy", "+m bankBal", "+m dur", "+m fillMv", "+m fillOv", "+m goView",
                  "+m hexOf", "+m keep", "+m mBuy", "+m mPick", "+m mtip", "+m ovCancel", "+m ovChip", "+m ovFail", "+m ovGo", "+m pnum", "+m sqOf",
                  "+m viewOf", "+m wrap2", "~c ", "~m build", "~m fillOrders", "~m handleDataEvent", "~m tabGo"],
    "MarketTabData": ["+f KNAME", "+f LS", "+f MVCAP", "+f MVFAIL", "+f MVFAR", "+f MVKN", "+f MVOFF", "+f MVOLD", "+f MVSN", "+f MVZN", "+f NONEC",
                      "+f OVCAP", "+f OVCHK", "+f OVN", "+f OVOLD", "+f OVPICK", "+f SIDE", "+f SQ", "~<clinit>"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.71:', 'if "--expect-dump" in sys.argv:'), EXPECT_72.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.71"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.72"') == 1, "S VERSION")
''' + HARNESS_OLD4_STATIC.rstrip("\n"))
# OLD3's ratchet compared 0.3.71 with 0.3.70: against 0.3.71 it is OLD4's (above) - its four rows stay gone
T.rep('''    K.check(lefto_ - left2_ == set([("social", "players"), ("character", "stats"), ("character", "profiles"), ("social", "party")])
            and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 4 and ("social", "guild") in left2_,
            "OLD3 RATCHET OLD_LEFT lost social:players + character:stats + character:profiles + social:party, nothing added, the Guild page kept (%d -> %d; still: %s)"
            % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(not (left2_ & set([("social", "players"), ("character", "stats"), ("character", "profiles"), ("social", "party")])) and ("social", "guild") in left2_,
            "OLD3 RATCHET (0.3.72: vs 0.3.71) social:players + character:stats + character:profiles + social:party stay gone, the Guild page kept")''')
# TAB3: Buy order is the orders view now (never bazaar:fn:open); back to the cards for the rest of TAB3
T.rep('''    p_ = mt_ev({"a": "order"}, "TAB3 ACT Buy order")
    K.check(MW["bzo"] and MW["bzo"][-1][1] == "Stone", "TAB3 ACT Buy order = bazaar:fn:open on the selected item's name (%s)" % MW["bzo"][-1:])''',
      '''    p_ = mt_ev({"a": "order"}, "TAB3 ACT Buy order")
    K.check(not MW["bzo"] and int(MS.view) == 1 and int(MS.oside) == 0,
            "TAB3 ACT Buy order (0.3.72) = the Bazaar orders view on the buy side - bazaar:fn:open (the old page) is never called (%s)" % MW["bzo"][-1:])
    p_ = mt_ev({"a": "vw:0"}, "TAB3 back to the cards")''')
T.rep('''    for a_, what in (("full", "Full page"), ("mer", "Merchants"), ("bank", "the Bank page"), ("tab:4", "World")):''',
      '''    for a_, what in (("full", "a forged Full page (0.3.72: gone)"), ("mer", "See merchants (0.3.72: the merchants view)"), ("bank", "the Bank page"), ("tab:4", "World")):''')
T.rep('''    K.notes.append("TAB3 counters: opens %d, stale %d, reads %d, acts %d, bank moves %d" % (int(MTB.OPENS), int(MTB.STALE), len(MW["reads"]), len(MW["acts"]), len(MW["bmoves"])))''',
      '''    K.notes.append("TAB3 counters: opens %d, stale %d, reads %d, acts %d, bank moves %d" % (int(MTB.OPENS), int(MTB.STALE), len(MW["reads"]), len(MW["acts"]), len(MW["bmoves"])))
''' + HARNESS_OLD4.rstrip("\n"))
if T.dst:
    T.finish()
