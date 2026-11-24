"""Derive SkyyMenu/build_skyymenu_0.3.76.py + SkyyMenu/test_skyymenu_0.3.76.py from the SET pin SkyyMenu 0.3.75 (generated - never re-run
its patch). Run:  python tools/menu_0_3_76_patch.py   then   python SkyyMenu/build_skyymenu_0.3.76.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.76.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyBank 0.1.18 (tools/bank_0_1_18_patch.py: bank:fn:view / bank:fn:act, deployed TEST 329) for the
Bank view; with an older SkyyBank the view says which version it needs (the Market tab's bank card works as 0.3.75 through bank:fn:panel / move).

0.3.76 (2026-11-24, round oldmenu8) = OLD MENU FOLLOW-UP: THE BANK VIEW (the old Storage > Bank link, OLD_LEFT storage:bank). Skyy's words
(docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu
compleatly, so instead of adding things like the full tree button, just build it all into the new system and remove the old "Full tree"";
2026-11-24 "keep building". WHERE: the new screen has no Storage tab yet (the 7 approved tabs; the 12-tab plan of 2026-11-12 moves the bank to
a Storage tab later) - the bank lives on the MARKET tab (Skyy 11-14 "Bazaar, Auction House, Merchants, and the Bank"), so the Bank view is the
Market screen's fifth view (sub-tabs Market | Bazaar orders | Merchants | Auction House | Bank, no back button; the frame + ONE view per packet).
The bank card's 'Vault' button (hub storage:bank = the old Vault page through SkyyBank's hub tab) is now 'Bank' and opens the view.
THE BANK VIEW (section K) = SkyyBank 0.1.18's bank page through bank:fn:view / bank:fn:act (the SAME page code: BankCmd.move, BankStore.upgrade):
  YOUR COINS: the line above purse / bank (profile + level), Purse + Bank (the page's own numbers, gold), the cap bar, 'Holds up to N coins - room
      for M more' (or no limit), Deposit all / Withdraw all, Amount (typed: 500, 2k, 1.5m or all) + Deposit / Withdraw (Enter in the box = the
      page's amount note, nothing moves), the answer line (+ green, - red, = plain), a Vault hint (/vault: items are not in this view).
  BANK LEVEL: the level line (split at '. Upgrade'), 'top level', Upgrade to Lv N+1 - <next cost> coins (ONE press, as the page: the bridge
      guards the level and the price the view showed); bank levels off = said, no Upgrade.
  INTEREST: the rate line, the next payout line, the gain line (pay green / bad red / info plain), Refresh.
  LOCKED: the lock text only (no numbers, no buttons). Not on this server / SkyyBank older than 0.1.18 / unreadable / a '-' line = the head says so.
  NEVER A VALUE THE PLAYER DID NOT SEE: every act carries the view's click token + profile key (h fields 3 + 4); bank:fn:view is read on every
      drawing (open, every answer, Refresh) and NEVER on a timer; every answer redraws (a new read = a new token); '=' / '-' / '+' answers go to
      the caption and the answer line; a null answer = 'That could not run here - nothing changed.' (nothing read again). A coin button the drawing
      did not show (no token / no Upgrade) = 'That button is not on this page - nothing changed', no call; the page token on every coin button
      (an older drawing = 'The page changed', nothing runs).
New: no class / command / system / picture / lang key / setting / saved data. MT_VBW 170 -> 140 (five sub-tabs + the head line fit).
OLD_LEFT: storage:bank out (6 -> 5) = no new-screen link to it is left. WHAT STILL REACHES SkyyBank's OLD page (fix round, a decision): SkyyBank's
  OWN Storage > Bank hub tab (hub:tab:storage:bank is SkyyBank's BankHubOpen - SkyyMenu's MenuHub.page only serves its own 6 tabs, so the 0.3.75
  teleport-style route cannot be done here) and /bank = a later SkyyBank round; the old Home's TILE_TAB / MIG / REDIR 'bank' shortcuts are old-menu
  data, reached only while the old menu is ON (OFF: home() and /storage open the new screen), so they stay as they are (the old menu stays one piece).
ROLLBACK to 0.3.75: safe alone (nothing saved; the card's Vault button comes back). SkyyBank 0.1.18 rolls back alone (this view then names 0.1.18).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.75.py"), os.path.join(MOD, "build_skyymenu_0.3.76.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.75.py"), os.path.join(MOD, "test_skyymenu_0.3.76.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.75"\n') and P.has("OLD_LEFT = sorted(set([") and P.has('WT + "Gv"') and not P.has('MT + "Kv"'), "not the generated SkyyMenu 0.3.75 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.75: OLD MENU FOLLOW-UP - THE WORLD TAB'S TRAVEL VIEW''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.76: OLD MENU FOLLOW-UP - THE BANK VIEW (the old Storage > Bank link): the Market screen's fifth view (sub-tab Bank; the bank card's Bank
       button) = SkyyBank 0.1.18 bank:fn:view / bank:fn:act: purse + bank, the cap bar + room, Deposit all / Withdraw all, a typed amount +
       Deposit / Withdraw (Enter = the amount note), the level line + Upgrade (the next cost on it), interest + next payout + gain, Refresh; the
       lock text only while locked. Every act carries the view's token + profile key; the view is read again after every answer, never on a
       timer. OLD_LEFT lost storage:bank (notes: tools/menu_0_3_76_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.76.py.
0.3.75: OLD MENU FOLLOW-UP - THE WORLD TAB'S TRAVEL VIEW''')
P.rep('VERSION = "0.3.75"\n', 'VERSION = "0.3.76"\n')

# ======================================================================= the bank card: Vault (storage:bank) -> Bank (the view)
P.rep('''    ap.append(("#" + bkh, G_.glass_button(MT + "Bpg", "Vault", "secondary", w=104, h=24, size=12)))   # 0.3.70: HubBar storage:bank = the Vault (items)''',
      '''    ap.append(("#" + bkh, G_.glass_button(MT + "Bpg", "Bank", "secondary", w=104, h=24, size=12)))   # 0.3.76: the Bank view (was storage:bank = the Vault page)''')

# ======================================================================= the sub-tab row gets Bank; THE BANK VIEW (section K)
P.rep('''MT_VBW = 170                                                # a sub-tab / side / shop tab button
MT_SUBS = ["Market", "Bazaar orders", "Merchants", "Auction House"]   # 0.3.73: + the Auction House view''',
      '''MT_VBW = 140                                                # a sub-tab / side / shop tab button (0.3.76: 170 -> 140 for the fifth sub-tab)
MT_SUBS = ["Market", "Bazaar orders", "Merchants", "Auction House", "Bank"]   # 0.3.73: + the Auction House view; 0.3.76: + the Bank view''')
P.rep('''HV_RUNTIME_MAX = len(HMODE) + max(HV_RN, HV_CN + 1, HV_MN, 1)   # the mode buttons + a rarity square per row (+ the picked stack)
''', '''HV_RUNTIME_MAX = len(HMODE) + max(HV_RN, HV_CN + 1, HV_MN, 1)   # the mode buttons + a rarity square per row (+ the picked stack)

# ---- 0.3.76 (oldmenu8): THE BANK VIEW (section K) - SkyyBank 0.1.18 bank:fn:view / bank:fn:act (contract: tools/bank_0_1_18_patch.py header)
KV_LK = 60                                                  # the lock text line (only while the bank is locked)
KV_BH = MT_VBH - KV_LK - 6                                  # the two cards under the head + the lock line (718)
KV_LW = 760                                                 # YOUR COINS
KV_RW = MT_VI - KV_LW - 10                                  # BANK LEVEL + INTEREST (766)
KV_LI, KV_RI = KV_LW - 20, KV_RW - 20
KV_NW, KV_AW, KV_BW, KV_QW, KV_UW = 160, 220, 160, 240, 400  # the Purse / Bank word, Deposit all, Deposit, the typed box, Upgrade
KV_TXT = {
    "kvcap": "Your coins: deposit, withdraw and upgrade your bank here. Market on top goes back.",
    "kvold": "This needs SkyyBank 0.1.18 - this server has an older one. /bank works.",
    "kvoff": "The bank is not on this server right now.",
    "kvfail": "Your bank could not be read right now - press Refresh in a moment.",
    "kvnull": "That could not run here - nothing changed.",
    "kvnone": "That button is not on this page - nothing changed",
    "kvhint": "Type 500, 2k, 1.5m or all. Enter shows what it would move - only the buttons move coins.",
    "kvvault": "Items are kept in your Vault - /vault opens it. This view is your coins.",
    "kvlvoff": "Bank levels are off on this server - there is no level to buy.",
    "kvup": "Paid from your bank - one press, the price shown.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\\\' for v_ in KV_TXT.values() for c_ in v_), "0.3.76: plain texts"
for _k in ("kvold", "kvoff", "kvfail", "kvnull"):
    assert SUI.text_width(KV_TXT[_k], 13) <= MT_VI - 240 - len(MT_SUBS) * (MT_VBW + 6), ("0.3.76: a bank head line fits", _k)
for _k in ("kvcap", "kvnone", "kvnull"):
    assert SUI.text_width(KV_TXT[_k], 14) <= IV_IW - 420, ("0.3.76: a caption fits the hint row", _k)
for _k in ("kvhint", "kvvault"):
    assert SUI.text_width(KV_TXT[_k], 12) <= KV_LI, ("0.3.76: a coins card line fits", _k)
assert SUI.text_width(KV_TXT["kvlvoff"], 13) <= KV_RI and SUI.text_width(KV_TXT["kvup"], 12) <= KV_RI - KV_UW - 8, "0.3.76: a level card line fits"
for _l, _w in (("Deposit all", KV_AW), ("Withdraw all", KV_AW), ("Deposit", KV_BW), ("Withdraw", KV_BW), ("Refresh", KV_BW),
               ("Upgrade to Lv 99  -  999,999,999,999 coins", KV_UW)):
    assert SUI.text_width(_l, 14, bold=True) <= _w - 16, ("0.3.76: a bank button fits", _l)
assert SUI.text_width("Bank", 12, bold=True) <= 104 - 12, "0.3.76: the bank card's Bank button fits"
assert SUI.text_width("999,999,999,999 coins", 26, bold=True) <= KV_LI - KV_NW, "0.3.76: a coin number fits"
assert 90 + KV_QW + 8 + KV_BW + 8 + KV_BW <= KV_LI and 2 * KV_AW + 8 <= KV_LI, "0.3.76: the move rows fit"
KV_RUNTIME_MAX = 1                                          # the cap bar's fill
''')
P.rep('''                               ("#" + MT + "HvJpn", "hvjpg:1"), ("#" + MT + "HvCdp", "hvd:-1"), ("#" + MT + "HvCdn", "hvd:1"), ("#" + MT + "HvKpp", "hvkpg:-1"),
                               ("#" + MT + "HvKpn", "hvkpg:1")]))
    return out
''', '''                               ("#" + MT + "HvJpn", "hvjpg:1"), ("#" + MT + "HvCdp", "hvd:-1"), ("#" + MT + "HvCdn", "hvd:1"), ("#" + MT + "HvKpp", "hvkpg:-1"),
                               ("#" + MT + "HvKpn", "hvkpg:1")]))
    # ======== K: THE BANK VIEW (0.3.76, oldmenu8: the old Storage > Bank link = SkyyBank 0.1.18's bank page through bank:fn:view / act). The coin
    # buttons + the typed box's Enter are bound at run time (they carry the page token / only where the drawing showed them); Refresh is static
    ap = SUI.Appends()
    kv = MT + "Kv"
    ap.append(("#" + win, G_.glass_group(kv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bk = vhead(ap, kv, "Kv", "BANK", 4)
    ap.append(("#" + kv, lab(MT + "KvK", "", 15, "text", bold=True, w=MT_VI, h=KV_LK, anchor={"top": 6})))
    kb = MT + "Kvb"
    ap.append(("#" + kv, G_.glass_group(kb, MT_VI, KV_BH, layout="Left", anchor={"top": 6})))
    # ---- YOUR COINS
    kl = MT + "KvLc"
    ap.append(("#" + kb, G_.glass_group(kl, KV_LW, KV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + kl, lab(None, "YOUR COINS", 15, "accentHi", bold=True, w=KV_LI, h=24)))
    ap.append(("#" + kl, lab(MT + "KvS", "", 13, "text", w=KV_LI, h=20, anchor={"top": 4})))
    for r_, w_, t_, top_ in (("KvPr", "Purse", "KvP", 12), ("KvBr", "Bank", "KvB", 4)):
        ap.append(("#" + kl, G_.glass_group(MT + r_, KV_LI, 44, layout="Left", anchor={"top": top_})))
        ap.append(("#" + MT + r_, lab(None, w_, 16, "dim", bold=True, w=KV_NW, h=44)))
        ap.append(("#" + MT + r_, lab(MT + t_, "", 26, "xp", bold=True, w=KV_LI - KV_NW, h=44)))
    ap.append(("#" + kl, 'Group #%sKvBb { Anchor: (Width: %d, Height: 8, Top: 8); LayoutMode: Left; Background: %s; }' % (MT, KV_LI, IV_TRACK)))
    ap.append(("#" + kl, lab(MT + "KvC", "", 12, "dim", w=KV_LI, h=18, anchor={"top": 6})))
    ka = MT + "KvAl"
    ap.append(("#" + kl, G_.glass_group(ka, KV_LI, 40, layout="Left", anchor={"top": 18})))
    ap.append(("#" + ka, G_.glass_button(MT + "KvDa", "Deposit all", "primary", w=KV_AW, h=40, size=14, anchor={"right": 8})))
    ap.append(("#" + ka, G_.glass_button(MT + "KvWa", "Withdraw all", "secondary", w=KV_AW, h=40, size=14)))
    kr = MT + "KvAr"
    ap.append(("#" + kl, G_.glass_group(kr, KV_LI, 36, layout="Left", anchor={"top": 18})))
    ap.append(("#" + kr, lab(None, "Amount", 13, "dim", bold=True, w=90, h=36)))
    ap.append(("#" + kr, G_.text_field(MT + "KvQBox", MT + "KvQ", w=KV_QW, h=34, placeholder="like 2k or all", max_length=16, size=14, anchor={"right": 8})))
    ap.append(("#" + kr, G_.glass_button(MT + "KvD", "Deposit", "primary", w=KV_BW, h=36, size=14, anchor={"right": 8})))
    ap.append(("#" + kr, G_.glass_button(MT + "KvW", "Withdraw", "secondary", w=KV_BW, h=36, size=14)))
    ap.append(("#" + kl, lab(MT + "KvX1", "", 12, "dim", w=KV_LI, h=18, anchor={"top": 6})))
    ap.sets.append((MT + "KvX1", "Text", KV_TXT["kvhint"]))
    holder(ap, kl, MT + "KvA", KV_LI, 24, 14, ["green", "red", "text"], anchor={"top": 16}, bold=True)
    ap.append(("#" + kl, lab(MT + "KvX2", "", 12, "dim", w=KV_LI, h=18, anchor={"top": 16})))
    ap.sets.append((MT + "KvX2", "Text", KV_TXT["kvvault"]))
    assert 20 + 24 + 24 + 56 + 48 + 16 + 24 + 58 + 54 + 24 + 40 + 34 <= KV_BH, "0.3.76: the coins card fits"
    ap.append(("#" + kb, "Group { Anchor: (Width: 10); }"))
    # ---- BANK LEVEL + INTEREST
    kq = MT + "KvRc"
    ap.append(("#" + kb, G_.glass_group(kq, KV_RW, KV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + kq, lab(None, "BANK LEVEL", 15, "accentHi", bold=True, w=KV_RI, h=24)))
    ap.append(("#" + kq, lab(MT + "KvL1", "", 13, "text", w=KV_RI, h=20, anchor={"top": 6})))
    ap.append(("#" + kq, lab(MT + "KvL2", "", 12, "dim", w=KV_RI, h=18)))
    ap.append(("#" + kq, lab(MT + "KvLo", "", 12, "dim", w=KV_RI, h=18, anchor={"top": 4})))
    ku = MT + "KvUr"
    ap.append(("#" + kq, G_.glass_group(ku, KV_RI, 40, layout="Left", anchor={"top": 12})))
    ap.append(("#" + ku, G_.glass_button(MT + "KvU", "Upgrade", "primary", w=KV_UW, h=40, size=14, anchor={"right": 8})))
    ap.append(("#" + ku, lab(MT + "KvUn", "", 12, "dim", w=KV_RI - KV_UW - 8, h=40)))
    ap.sets.append((MT + "KvUn", "Text", KV_TXT["kvup"]))
    ap.append(("#" + kq, lab(None, "INTEREST", 15, "accentHi", bold=True, w=KV_RI, h=24, anchor={"top": 24})))
    ap.append(("#" + kq, lab(MT + "KvR", "", 13, "text", w=KV_RI, h=20, anchor={"top": 6})))
    ap.append(("#" + kq, lab(MT + "KvN", "", 13, "text", w=KV_RI, h=20, anchor={"top": 2})))
    holder(ap, kq, MT + "KvG", KV_RI, 24, 14, ["green", "red", "text"], anchor={"top": 6}, bold=True)
    ap.append(("#" + kq, G_.glass_button(MT + "KvRf", "Refresh", "secondary", w=KV_BW, h=36, size=14, anchor={"top": 24})))
    assert 20 + 24 + 26 + 18 + 22 + 52 + 48 + 26 + 22 + 30 + 60 <= KV_BH, "0.3.76: the level card fits"
    assert KV_LW + 10 + KV_RW == MT_VI and 20 + 34 + 6 + KV_LK + 6 + KV_BH <= IV_BODY_H, "0.3.76: the bank view fits 1080"
    out.append(("K", ap, bk + [("#" + MT + "KvRf", "kvrf")]))
    return out
''')
P.rep('''             "HvCdv", "HvCdn", "HvCz", "HvCgo", "HvCn", "HvMg", "HvMs", "HvMca", "HvMo", "HvKp", "HvKpp", "HvKpg", "HvKpn", "HvKn"]''',
      '''             "HvCdv", "HvCdn", "HvCz", "HvCgo", "HvCn", "HvMg", "HvMs", "HvMca", "HvMo", "HvKp", "HvKpp", "HvKpg", "HvKpn", "HvKn",
             # 0.3.76 (oldmenu8): the Bank view
             "Kv", "KvH", "KvT0", "KvT1", "KvT2", "KvT3", "KvT4", "KvK", "Kvb", "KvLc", "KvS", "KvP", "KvB", "KvBb", "KvC", "KvAl", "KvDa", "KvWa", "KvAr",
             "KvQ", "KvQBox", "KvD", "KvW", "KvX1", "KvA0", "KvA1", "KvA2", "KvX2", "KvRc", "KvL1", "KvL2", "KvLo", "KvUr", "KvU", "KvUn", "KvR", "KvN",
             "KvG0", "KvG1", "KvG2", "KvRf"]''')
P.rep('''_mt_rt = {"H": MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1, "O": OV_RUNTIME_MAX, "M": MV_RUNTIME_MAX, "U": HV_RUNTIME_MAX}   # + 0.3.73: the AH modes + squares
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOMU")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMU")
print("0.3.73 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOMU")))''',
      '''_mt_rt = {"H": MT_CATN + len(MT_AMT) + len(MT_BAMT) + 1, "O": OV_RUNTIME_MAX, "M": MV_RUNTIME_MAX, "U": HV_RUNTIME_MAX,   # + 0.3.73: the AH modes + squares
          "K": KV_RUNTIME_MAX}   # 0.3.76: the bank view's cap bar fill
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOMUK")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUK")   # 0.3.76: + K, the Bank view
print("0.3.76 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOMUK")))''')

# ======================================================================= the data + the fields
P.rep('''for _n, _v in (("HVOLD", HV_TXT["hvold"]), ("HVOFF", HV_TXT["hvoff"]), ("HVFAIL", HV_TXT["hvfail"]), ("HVCAP", HV_TXT["hvcap"]), ("HVCHK", HV_TXT["hvchk"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))
''', '''for _n, _v in (("HVOLD", HV_TXT["hvold"]), ("HVOFF", HV_TXT["hvoff"]), ("HVFAIL", HV_TXT["hvfail"]), ("HVCAP", HV_TXT["hvcap"]), ("HVCHK", HV_TXT["hvchk"])):
    F(mtd, "public static final String %s = %s;" % (_n, jstr(_v)))
# 0.3.76 (oldmenu8): the Bank view
F(mtd, "public static final int KVBAR = %d;" % KV_LI)
for _k in ("kvcap", "kvold", "kvoff", "kvfail", "kvnull", "kvnone", "kvlvoff"):
    F(mtd, "public static final String %s = %s;" % (_k.upper(), jstr(KV_TXT[_k])))
''')
P.rep('''           "public String[] hvMKind;", "public boolean[] hvMBtn;",
''', '''           "public String[] hvMKind;", "public boolean[] hvMBtn;",
           # 0.3.76 (oldmenu8): the Bank view - the last read's token + profile key, what its drawing showed, the typed amount, the answer line
           "public String kvTok;", "public String kvPk;", "public String kvState;", "public boolean kvMove;", "public boolean kvUp;", "public String kvTyped;",
           "public String kvLast;", "public int kvAk;", "public String kvAns;",
''')
P.rep('''  this.hvMBtn = new boolean[0];
  this.builds = 0;''', '''  this.hvMBtn = new boolean[0];
  this.kvTok = "-";        // 0.3.76 (oldmenu8)
  this.kvPk = "-";
  this.kvState = "";
  this.kvMove = false;
  this.kvUp = false;
  this.kvTyped = "";
  this.kvLast = null;
  this.kvAk = -1;
  this.kvAns = "";
  this.builds = 0;''')

# ======================================================================= the Bank view's drawing (before build)
P.rep('''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;''', '''# ---- 0.3.76 (oldmenu8): THE BANK VIEW. bank:fn:view apply(UUID) -> h| (18 fields) + k| / f| / s| / l| / r| / n| / g| lines, or ONE '-' line
# (SkyyBank 0.1.18, the header of tools/bank_0_1_18_patch.py). Read on every drawing of this view (open, every answer, Refresh), never on a timer.
# mode: 0 = the head line only, 1 = the two cards, 2 = the lock text only
M(mtab, r"""
public void kvShow(@UCB@ b, String head, int mode) {
  b.set("#SkyyMtabKvH.Text", head == null ? "" : head);
  b.set("#SkyyMtabKvb.Visible", mode == 1);
  b.set("#SkyyMtabKvK.Visible", mode == 2);
  hold(b, "SkyyMtabKvA", 3, mode == 1 ? this.kvAk : -1, this.kvAns);
}""")
M(mtab, r"""
public void fillKv(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  this.kvTok = "-";
  this.kvPk = "-";
  this.kvState = "";
  this.kvMove = false;
  this.kvUp = false;
  boolean has = @PKG@.InvCraft.fn("bank:fn:view") != null && @PKG@.InvCraft.fn("bank:fn:act") != null;
  if (!has) {
    this.kvLast = null;
    kvShow(b, @PKG@.InvCraft.fn("bank:fn:panel") != null || @PKG@.InvCraft.fn("bank:fn:move") != null ? @PKG@.MarketTabData.KVOLD : @PKG@.MarketTabData.KVOFF, 0);
    return;
  }
  Object o = call("bank:fn:view", u);
  this.calls = this.calls + 1;
  String s = o instanceof String ? (String) o : null;
  this.kvLast = s;
  String[] ls = s == null ? new String[0] : s.split("\\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? sp(ls[0], 18) : new String[0];
  if (h.length < 18) {
    String why = @PKG@.MarketTabData.KVFAIL;
    if (ls.length == 1 && ls[0].startsWith("-")) why = @PKG@.MenuUtil.clip(@PKG@.InvPage.bare(ls[0]), 120);
    kvShow(b, why, 0);
    return;
  }
  String lk = "", f1 = "", f2 = "", sl = "", ll = "", rl = "", nx = "", gk = "", gt = "";
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("k|")) lk = l.substring(2);
    else if (l.startsWith("f|")) { String[] f = sp(l, 3); if (f.length >= 3) { f1 = f[1]; f2 = f[2]; } }
    else if (l.startsWith("s|")) sl = l.substring(2);
    else if (l.startsWith("l|")) ll = l.substring(2);
    else if (l.startsWith("r|")) rl = l.substring(2);
    else if (l.startsWith("n|")) nx = l.substring(2);
    else if (l.startsWith("g|")) { String[] g = sp(l, 3); if (g.length >= 3) { gk = g[1]; gt = g[2]; } }
  }
  if ("locked".equals(h[1])) {
    this.kvState = "locked";
    b.set("#SkyyMtabKvK.Text", @PKG@.MenuUtil.clip(lk.length() > 0 ? lk : "Your bank is still locked.", 150));
    kvShow(b, "", 2);
    return;
  }
  if (!"ok".equals(h[1])) { kvShow(b, @PKG@.MarketTabData.KVFAIL, 0); return; }
  this.kvState = "ok";
  this.kvTok = h[2];
  this.kvPk = h[3];
  boolean move = h[2].length() > 0 && !"-".equals(h[2]);
  this.kvMove = move;
  long purse = nl(h[6], -1L), bank = nl(h[7], -1L), cost = nl(h[12], -1L), cap = nl(h[13], -1L), room = nl(h[14], -1L);
  boolean lvOn = "1".equals(h[8]);
  int lv = ni(h[9], 0), mx = ni(h[10], 0);
  kvShow(b, "", 1);
  b.set("#SkyyMtabKvS.Text", @PKG@.MenuUtil.clip(sl, 110));
  b.set("#SkyyMtabKvP.Text", @PKG@.MenuUtil.clip(f1, 40) + (purse >= 0L ? " coins" : ""));
  b.set("#SkyyMtabKvB.Text", @PKG@.MenuUtil.clip(f2, 40) + (bank >= 0L ? " coins" : ""));
  int w = cap > 0L && bank >= 0L ? @PKG@.InvPage.barW(bank, cap, @PKG@.MarketTabData.KVBAR) : 0;
  if (w > 0) b.appendInline("#SkyyMtabKvBb", @PKG@.MarketTabData.FILL.replace("{W}", String.valueOf(w)));
  b.set("#SkyyMtabKvC.Text", cap >= 0L ? "Holds up to " + money(cap) + " coins" + (room >= 0L ? "  -  room for " + money(room) + " more" : "") : "No limit on what your bank holds");
  b.set("#SkyyMtabKvDa.Visible", move);
  b.set("#SkyyMtabKvWa.Visible", move);
  b.set("#SkyyMtabKvD.Visible", move);
  b.set("#SkyyMtabKvW.Visible", move);
  b.set("#SkyyMtabKvQBox.Visible", move);
  b.set("#SkyyMtabKvQ.Value", this.kvTyped == null ? "" : this.kvTyped);
  String bk = String.valueOf((char) 64) + "B";
  if (move) {
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabKvDa", @EVD@.of("a", "kvda").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabKvWa", @EVD@.of("a", "kvwa").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabKvD", @EVD@.of("a", "kvd").append("t", this.tok).append(bk, "#SkyyMtabKvQ.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabKvW", @EVD@.of("a", "kvw").append("t", this.tok).append(bk, "#SkyyMtabKvQ.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyMtabKvQ", @EVD@.of("a", "kvamt").append(bk, "#SkyyMtabKvQ.Value"), false);
  }
  if (lvOn) {
    int li = ll.indexOf("Bank Lv ");
    String lt = li > 0 ? ll.substring(li) : ll;
    int dot = lt.indexOf(". Upgrade");
    b.set("#SkyyMtabKvL1.Text", @PKG@.MenuUtil.clip(dot > 0 ? lt.substring(0, dot + 1) : lt, 110));
    b.set("#SkyyMtabKvL2.Text", @PKG@.MenuUtil.clip(dot > 0 ? lt.substring(dot + 2) : "", 110));
    b.set("#SkyyMtabKvLo.Text", mx > 0 && lv >= mx ? "Your bank is at its top level (Lv " + lv + ")." : "");
  } else {
    b.set("#SkyyMtabKvL1.Text", @PKG@.MarketTabData.KVLVOFF);
    b.set("#SkyyMtabKvL2.Text", "");
    b.set("#SkyyMtabKvLo.Text", "");
  }
  boolean up = lvOn && move && "1".equals(h[11]) && cost >= 0L && lv > 0;
  this.kvUp = up;
  b.set("#SkyyMtabKvUr.Visible", up);
  if (up) {
    b.set("#SkyyMtabKvU.Text", "Upgrade to Lv " + (lv + 1) + "  -  " + money(cost) + " coins");
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabKvU", @EVD@.of("a", "kvu").append("t", this.tok));
  }
  b.set("#SkyyMtabKvR.Text", @PKG@.MenuUtil.clip(rl, 110));
  b.set("#SkyyMtabKvN.Text", @PKG@.MenuUtil.clip(nx, 110));
  hold(b, "SkyyMtabKvG", 3, gk.equals("pay") ? 0 : (gk.equals("bad") ? 1 : 2), @PKG@.MenuUtil.clip(gt, 110));
}""")
M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;''')
P.rep('''  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : (this.view == 3 ? 'U' : 'H'));   // 0.3.73: + U (the Auction House)''',
      '''  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : (this.view == 3 ? 'U' : (this.view == 4 ? 'K' : 'H')));   // 0.3.73: + U (the Auction House); 0.3.76: + K (the Bank)''')
P.rep('''    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.HVCAP);
    return;
  }''', '''    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.HVCAP);
    return;
  }
  if (this.view == 4) {   // 0.3.76 (oldmenu8): the Bank view reads SkyyBank's bank:fn:view only (a new click token per drawing)
    try { fillKv(b, ev); } catch (Throwable t) { this.kvState = ""; this.kvMove = false; this.kvUp = false; @PKG@.MenuUtil.warn("market screen: the bank view failed: " + t); }
    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.KVCAP);
    return;
  }''')

# ======================================================================= the Bank view's acts (after bankMove)
P.rep('''# ---- 0.3.72 (oldmenu4): the views' actions. Every one answers with ONE packet (a redraw with the answer in the caption, or a caption).
M(mtab, r"""
public static int viewOf(String a) {
  if (a.startsWith("ov") || a.startsWith("oc:")) return 1;''', '''# ---- 0.3.76 (oldmenu8): one Bank view act: bank:fn:act apply(Object[] { op, UUID, the view's token, the view's profile key, arg }) -> the page's
# answer line ('+' done, '-' refused, '=' a note, "" nothing to say). Every answer = the caption + the answer line + a redraw (= bank:fn:view read
# again: the used token is dead). A null answer = said, nothing read again (nothing ran).
M(mtab, r"""
public void kvAct(String op, String arg) {
  this.answered = true;
  if (@PKG@.InvCraft.fn("bank:fn:act") == null || @PKG@.InvCraft.fn("bank:fn:view") == null) {
    say(@PKG@.InvCraft.fn("bank:fn:panel") != null || @PKG@.InvCraft.fn("bank:fn:move") != null ? @PKG@.MarketTabData.KVOLD : @PKG@.MarketTabData.KVOFF);
    return;
  }
  Object o = call("bank:fn:act", new Object[] { op, this.playerRef.getUuid(), this.kvTok, this.kvPk, arg == null ? "" : arg });
  this.calls = this.calls + 1;
  if (o == null) { say(@PKG@.MarketTabData.KVNULL); return; }
  String r = String.valueOf(o).replace((char) 10, ' ').replace((char) 13, ' ').trim();
  char c = r.length() > 0 ? r.charAt(0) : ' ';
  this.kvAk = c == '+' ? 0 : (c == '-' ? 1 : (r.length() > 0 ? 2 : -1));
  this.kvAns = @PKG@.MenuUtil.clip(@PKG@.InvPage.bare(r), 140);
  if (c == '+' && (op.equals("deposit") || op.equals("withdraw"))) this.kvTyped = "";   // moved: the box empties (a second press cannot repeat it)
  this.tcap = this.kvAns;
  redraw();
}""")
# ---- 0.3.72 (oldmenu4): the views' actions. Every one answers with ONE packet (a redraw with the answer in the caption, or a caption).
M(mtab, r"""
public static int viewOf(String a) {
  if (a.startsWith("kv")) return 4;                           // 0.3.76: the Bank view
  if (a.startsWith("ov") || a.startsWith("oc:")) return 1;''')
P.rep('''  if (a.equals("claim")) return 4;                            // the Bazaar's Claim all: the cards or the orders view''',
      '''  if (a.equals("claim")) return 9;                            // the Bazaar's Claim all: the cards or the orders view (0.3.76: 4 -> 9, 4 = the Bank view)''')
P.rep('''    if (need >= 0 && !(need == this.view || (need == 4 && this.view <= 1))) { say("That button is not on this page - nothing changed"); return; }''',
      '''    if (need >= 0 && !(need == this.view || (need == 9 && this.view <= 1))) { say("That button is not on this page - nothing changed"); return; }   // 0.3.76: Claim all = 9''')
P.rep('''  this.view = v < 0 || v > 3 ? 0 : v;   // 0.3.73: + 3 the Auction House
''', '''  this.view = v < 0 || v > 4 ? 0 : v;   // 0.3.73: + 3 the Auction House; 0.3.76: + 4 the Bank
  this.kvAk = -1;                        // 0.3.76: a fresh view, no old answer line
  this.kvAns = "";
''')
P.rep('''    if (a.equals("bank")) { hub("storage", "bank", "the Vault"); return; }   // 0.3.70: the bank itself is all on this card; this = the Vault
''', '''    if (a.equals("bank")) { goView(4); return; }   // 0.3.76 (oldmenu8): the card's Bank button = the Bank view (was storage:bank = the old Vault page)
    // 0.3.76: the Bank view's Refresh (bank:fn:act refresh, then the view is read again) and the typed box's Enter (the page's amount note)
    if (a.equals("kvrf")) {
      if (@PKG@.InvCraft.fn("bank:fn:act") == null || @PKG@.InvCraft.fn("bank:fn:view") == null) { this.tcap = ""; redraw(); return; }
      kvAct("refresh", "");
      return;
    }
    if (a.equals("kvamt")) {
      if (!this.kvMove) { say(@PKG@.MarketTabData.KVNONE); return; }
      this.kvTyped = amtClean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "B"));
      kvAct("amount", this.kvTyped);
      return;
    }
''')
P.rep('''    if (a.startsWith("mb:")) { mBuy(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
''', '''    if (a.startsWith("mb:")) { mBuy(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    // 0.3.76 (oldmenu8): the Bank view's coin buttons - only where the drawing showed them; the view's token + profile key ride along
    if (a.equals("kvda") || a.equals("kvwa") || a.equals("kvd") || a.equals("kvw") || a.equals("kvu")) {
      if (!this.kvMove || (a.equals("kvu") && !this.kvUp)) { say(@PKG@.MarketTabData.KVNONE); return; }
      String ky = amtClean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "B"));
      boolean typed = a.equals("kvd") || a.equals("kvw");
      if (typed) this.kvTyped = ky;
      kvAct(a.equals("kvda") ? "depall" : (a.equals("kvwa") ? "wdall" : (a.equals("kvd") ? "deposit" : (a.equals("kvw") ? "withdraw" : "upgrade"))), typed ? ky : "");
      return;
    }
''')

# ======================================================================= the ratchet: OLD_LEFT shrinks by the row this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"),
    ("storage", "bank"), ("storage", "pocket"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.76 (oldmenu8): storage:bank (the Market bank card's Vault button = the old Vault page through SkyyBank's hub tab) is gone from the NEW screens:
# the button is 'Bank' and opens the Market screen's Bank view (SkyyBank 0.1.18 bank:fn:view / bank:fn:act). Still outside SkyyMenu: SkyyBank's own
# Storage > Bank hub tab (its BankHubOpen) and /bank open SkyyBank's page - a SkyyBank round; the old Home's 'bank' shortcuts only while the old menu is on.
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"),
    ("storage", "pocket"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.76: no system / command / class"
_i = P.s.index
assert _i("public static void hold(@UCB@ b, String base, int n, int which, String text)") < _i("public void kvShow(@UCB@ b, String head, int mode)") \
    < _i("public void fillKv(@UCB@ b, @UEB@ ev)") < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.pref = ref;\n  this.pst = st;\n  String lk = @PKG@.MarketTabData.LK;") \
    < _i("public void kvAct(String op, String arg)") < _i("public static int viewOf(String a) {\n  if (a.startsWith(\"kv\")) return 4;") \
    < _i('    if (a.equals("kvrf")) {'), "0.3.76: the bank view methods before their callers"
assert _i("public void redraw() {\n  this.answered = true;\n  if (!still()) { finish(\"replaced\"); return; }") < _i("public void kvAct(String op, String arg)"), "0.3.76: redraw before kvAct"
assert _i("public static String amtClean(String s)") < _i('    if (a.equals("kvamt")) {'), "0.3.76: amtClean before its caller"
for _old in ('hub("storage", "bank"', 'openHub("storage", "bank"', '"Vault", "secondary", w=104'):
    assert _old not in P.s[P.s.index("# ================= 0.3.50 THE INVENTORY SCREEN"):P.s.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")], "0.3.76: no old link left: " + _old
P.finish()

# ======================================================================= the HARNESS (every 0.3.75 check runs again on the 0.3.76 jar, plus OLD8)
HARNESS_OLD8_STATIC = r'''    # ---- OLD8 (0.3.76; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the ratchet shrank by exactly the row this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("storage", "bank")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 1,
            "OLD8 RATCHET OLD_LEFT lost storage:bank, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('hub("storage", "bank"' not in g and 'G_.glass_button(MT + "Bpg", "Vault"' not in g and 'G_.glass_button(MT + "Bpg", "Bank"' in g
            and 'if (a.equals("bank")) { goView(4); return; }' in g and '"the Vault")' not in g,
            "OLD8 STATIC no storage:bank link on the Market screen; the bank card's button is 'Bank' and opens the Bank view")
    K.check('Object o = call("bank:fn:view", u);' in g and 'call("bank:fn:act", new Object[] { op, this.playerRef.getUuid(), this.kvTok, this.kvPk, arg == null ? "" : arg })' in g
            and 'this.kvTok = h[2];' in g and 'this.kvPk = h[3];' in g and g.count('"bank:fn:view"') >= 3 and "ScheduledFuture kv" not in g,
            "OLD8 STATIC the Bank view reads bank:fn:view and acts through bank:fn:act with the read's token (h field 3) + profile key (h field 4); no timer")
    K.check(all(("0.3.76: %s" % t_) in g for t_ in ("the coins card fits", "the level card fits", "the bank view fits 1080", "a bank button fits",
                                                      "a bank head line fits", "a caption fits the hint row", "the move rows fit", "a coin number fits")),
            "OLD8 STATIC the build asserts the Bank view fits 1080, its buttons and lines fit")
    mw8_ = re.search(r"MT_ELEMENTS <= (\d+)", g)
    K.check(mw8_ is not None and int(mw8_.group(1)) <= 800 and 'MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUK")' in g,
            "OLD8 STATIC the market screen's budget = the frame + its biggest section (+ K, the Bank view), still <= 800")
'''

HARNESS_OLD8 = r'''    # ---- OLD8 (0.3.76, round oldmenu8): THE MARKET TAB'S BANK VIEW (bank:fn:view / bank:fn:act stand-ins = tools/bank_0_1_18_patch.py's contract)
    def only8(p_):   # the frame + ONE section: the Bank view, no home cards, no other view
        return (p_ is not None and has4(p_, "SkyyMtabKv") and not has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabOv") and not has4(p_, "SkyyMtabMv")
                and not has4(p_, "SkyyMtabHv") and not sel_ok4(p_))

    def ecount8(p_):   # the elements a packet appends (Group / Label / TextButton ... { ), the budget is ~1,600
        return sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", re.sub(r'"(?:[^"\\]|\\.)*"', '""', str(c_.text or ""))))
                   for c_ in cmds_of(p_))
    vis8 = lambda c_, k_: vis3(c_, k_)
    BK = {"tok": 0, "cur": None, "pk": "prof-A", "epoch": 1, "locked": False, "lvOn": True, "lv": 2, "max": 10, "coins": True, "readable": True,
          "purse": 50000, "bank": 120000, "cap": 250000, "intOn": True, "gain": 1320, "views": [], "acts": [], "vnull": False, "anull": False,
          "dash": None, "costx": 0}

    def bk_cost(lv_):
        return 75000 * lv_ // 2 + BK["costx"]

    def f_kview(o):
        BK["views"].append(str(o))
        if BK["vnull"]:
            return None
        if BK["dash"]:
            return BK["dash"]
        if BK["locked"]:
            BK["cur"] = None
            return "h|locked|-|-|0|0|-1|-1|0|0|0|0|-1|-1|-1|0|0|-1\nk|Your bank is still locked - finish the Bank quest to open it."
        BK["tok"] += 1
        tok_ = ("t%d" % BK["tok"]) if BK["pk"] else "-"
        purse_ = BK["purse"] if BK["coins"] else -1
        bank_ = BK["bank"] if BK["readable"] else -1
        on_ = BK["lvOn"]
        lv_ = BK["lv"] if on_ else 0
        mx_ = BK["max"] if on_ else 0
        can_ = on_ and 0 < lv_ < mx_
        cost_ = bk_cost(lv_) if can_ else -1
        cap_ = BK["cap"] if on_ else -1
        room_ = (cap_ - bank_) if (cap_ >= 0 and bank_ >= 0) else -1
        BK["cur"] = (tok_, BK["pk"], BK["epoch"], lv_, purse_, bank_, cost_) if tok_ != "-" else None
        L = ["h|ok|%s|%s|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (tok_, BK["pk"] or "-", 1 if BK["readable"] else 0, 1 if BK["coins"] else 0, purse_, bank_,
                                                                    1 if on_ else 0, lv_, mx_, 1 if can_ else 0, cost_, cap_, room_, 1 if BK["intOn"] else 0,
                                                                    BK["gain"], 11520000 if BK["intOn"] else -1)]
        L.append("f|%s|%s" % ("{:,}".format(purse_) if purse_ >= 0 else ("unreadable" if BK["coins"] else "no SkyyCoins"), "{:,}".format(bank_) if bank_ >= 0 else "unreadable"))
        L.append(("s|Main profile - Bank Lv %d" % lv_) if on_ else "s|Profile: Main profile")
        if on_:
            L.append("l|Bank Lv %d of %d: holds up to %s coins, 1.1%% interest. Upgrade to Lv %d: holds 500,000, 1.2%%, costs %s coins from the bank."
                     % (lv_, mx_, "{:,}".format(cap_), lv_ + 1, "{:,}".format(cost_)) if can_ else "l|Bank Lv %d of %d: holds up to %s coins, 1.1%% interest." % (lv_, mx_, "{:,}".format(cap_)))
        L.append("r|Interest every day at your level: 1.1% up to 100,000 | then 0.5%")
        L.append("n|" + ("Next payout in 3h 12m" if BK["intOn"] else "Interest is off on this server"))
        kind_ = "bad" if not BK["readable"] else ("pay" if BK["intOn"] else "info")
        L.append("g|%s|%s" % (kind_, "+1,320 coins at the next payout" if kind_ == "pay" else ("Your bank file could not be read" if kind_ == "bad" else "No interest right now")))
        return "\n".join(L)

    def bk_amt(t_, have_):
        t_ = t_.lower()
        if t_ == "all":
            return have_
        m_ = {"k": 1000, "m": 1000000}.get(t_[-1:], 1)
        try:
            return int(float(t_[:-1] if m_ > 1 else t_) * m_)
        except Exception:
            return -1

    def f_kact(o):
        a = [None if x_ is None else str(x_) for x_ in list(o)]
        BK["acts"].append(a)
        if BK["anull"]:
            return None
        op_, tok_, pk_, arg_ = a[0], a[2], a[3], a[4]
        if op_ in ("state", "view"):
            return f_kview(a[1])
        if op_ == "refresh":
            return ""
        t_ = (arg_ or "").strip()[:16]
        if op_ == "amount":
            return "=Type an amount (500, 2k, 1.5m or all), then click Deposit or Withdraw." if not t_ else "=Click Deposit or Withdraw to move %s coins. Enter alone never moves coins." % t_
        all_ = op_ in ("depall", "wdall")
        dep_ = op_ in ("depall", "deposit")
        upg_ = op_ == "upgrade"
        if not upg_ and not all_ and op_ not in ("deposit", "withdraw"):
            return "-Unknown bank action."
        if BK["locked"]:
            return "-Your bank is locked - nothing was moved."
        w_ = "charged" if upg_ else "moved"
        rec_ = BK["cur"]
        if rec_ is None or tok_ != rec_[0]:
            return "=That click was for an older copy of this page, so nothing was %s. The page is up to date now - click again if you meant it." % w_
        if pk_ != rec_[1] or BK["pk"] != rec_[1] or BK["epoch"] != rec_[2]:
            return "=Your profile changed after this page opened, so nothing was %s. The page now shows your current profile - click again." % w_
        if not all_ and not upg_ and not t_:
            return "=Type an amount in the box first (500, 2k, 1.5m or all), then click " + ("Deposit." if dep_ else "Withdraw.")
        if op_ == "depall" and BK["purse"] != rec_[4]:
            return "=Your purse changed since you looked (%s coins now) - look again. Nothing was moved." % "{:,}".format(BK["purse"])
        if op_ == "wdall" and BK["bank"] != rec_[5]:
            return "=Your bank changed since you looked (%s coins now) - look again. Nothing was moved." % "{:,}".format(BK["bank"])
        if upg_ and BK["lvOn"] and 0 < rec_[3] < BK["max"] and bk_cost(rec_[3]) != rec_[6]:
            return "=The upgrade price changed since you looked (Bank Lv %d now costs %s coins) - look again. Nothing was charged." % (rec_[3] + 1, "{:,}".format(bk_cost(rec_[3])))
        BK["cur"] = None   # the token is used up
        if upg_:
            if BK["bank"] < rec_[6]:
                return "-Your bank holds %s coins - Bank Lv %d costs %s. Nothing was charged." % ("{:,}".format(BK["bank"]), rec_[3] + 1, "{:,}".format(rec_[6]))
            BK["bank"] -= rec_[6]
            BK["lv"] += 1
            BK["cap"] = 500000
            return "+Your bank is now Lv %d - it holds up to 500,000 coins." % BK["lv"]
        if dep_:
            n_ = BK["purse"] if all_ else bk_amt(t_, BK["purse"])
            if n_ <= 0:
                return "-That is not an amount - nothing was moved."
            if n_ > BK["purse"]:
                return "-You only have %s coins in your purse - nothing was moved." % "{:,}".format(BK["purse"])
            n_ = min(n_, BK["cap"] - BK["bank"])
            if n_ <= 0:
                return "-Your bank is full - nothing was moved."
            BK["purse"] -= n_
            BK["bank"] += n_
            return "+Deposited %s coins." % "{:,}".format(n_)
        n_ = BK["bank"] if all_ else bk_amt(t_, BK["bank"])
        if n_ <= 0 or n_ > BK["bank"]:
            return "-Your bank holds %s coins - nothing was moved." % "{:,}".format(BK["bank"])
        BK["bank"] -= n_
        BK["purse"] += n_
        return "+Withdrew %s coins." % "{:,}".format(n_)

    def kv_ev(obj, what, n=1):   # one press; the Bank view's reads during it
        v0_ = len(BK["views"])
        p_ = mt_ev(obj, what, n)
        return p_, len(BK["views"]) - v0_
    for k_ in ("bank:fn:view", "bank:fn:act"):
        BR.remove(k_)
    p_ = mt_ev({"a": "fclear"}, "OLD8 the cards")
    K.check('Text: "Bank"' in mk_of(p_, "SkyyMtabBpg") and len(bind4(p_, "bank")) == 1, "OLD8 HOME the bank card's button reads Bank (was Vault = storage:bank)")
    # ---- FALL: SkyyBank older than 0.1.18 (bank:fn:panel only) / no SkyyBank
    p_ = mt_ev({"a": "bank"}, "OLD8 FALL Bank with SkyyBank 0.1.17")
    cm = cmap(p_)
    K.check(int(MS.view) == 4 and only8(p_) and txt4(cm, "KvH") == str(MTD.KVOLD) and not vis8(cm, "Kvb") and not vis8(cm, "KvK") and cap3(p_) == str(MTD.KVCAP)
            and str(PK.pm.getCustomPage().getClass().getSimpleName()) == "MarketTab" and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabKvT4") and len(bind4(p_, "vw:4")) == 1,
            "OLD8 FALL the card's Bank with SkyyBank 0.1.17 = the Bank view naming 0.1.18 (ONE section, Bank sub-tab selected, no old page) %s" % sel_ok4(p_)[:3])
    pan8_, mov8_ = BR.remove("bank:fn:panel"), BR.remove("bank:fn:move")
    p_ = mt_ev({"a": "kvrf"}, "OLD8 FALL no SkyyBank")
    K.check(txt4(cmap(p_), "KvH") == str(MTD.KVOFF) and only8(p_), "OLD8 FALL no SkyyBank at all = 'not on this server' (%s)" % txt4(cmap(p_), "KvH"))
    p_ = mt_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 FALL a forged Deposit all without the bridge")
    K.check(cap3(p_) == str(MTD.KVNONE) and not BK["acts"], "OLD8 FALL a coin button the drawing did not show = a caption, no call")
    BR.put("bank:fn:panel", pan8_)
    BR.put("bank:fn:move", mov8_)
    BR.put("bank:fn:view", Fn(f_kview))
    BR.put("bank:fn:act", Fn(f_kact))
    # ---- PAGE: Refresh = bank:fn:act refresh, then ONE read
    p_, nv_ = kv_ev({"a": "kvrf"}, "OLD8 Refresh with SkyyBank 0.1.18")
    cm = cmap(p_)
    K.notes.append("OLD8 the Bank view's packet: %d commands, %d elements appended" % (len(cmds_of(p_)), ecount8(p_)))
    K.check(BK["acts"][-1] == ["refresh", uk3, "-", "-", ""] and nv_ == 1 and only8(p_) and ecount8(p_) < 800,
            "OLD8 Refresh = bank:fn:act refresh {your UUID, the old token '-', ''}, then ONE bank:fn:view read; the frame + ONE section, under the element budget (%s, %d reads, %d elements)"
            % (BK["acts"][-1:], nv_, ecount8(p_)))
    K.check(vis8(cm, "Kvb") and not vis8(cm, "KvK") and txt4(cm, "KvH") == "" and txt4(cm, "KvS") == "Main profile - Bank Lv 2" and txt4(cm, "KvP") == "50,000 coins"
            and txt4(cm, "KvB") == "120,000 coins" and txt4(cm, "KvC") == "Holds up to 250,000 coins  -  room for 130,000 more"
            and any("Width: %d" % (120000 * int(MTD.KVBAR) // 250000) in t_ for t_ in appended4(p_, "SkyyMtabKvBb")),
            "OLD8 PAGE YOUR COINS: the line above, Purse + Bank (the view's numbers + coins), the cap line, the cap bar filled 120k / 250k")
    K.check("#e8c25a" in mk_of(p_, "SkyyMtabKvP").lower() and "#e8c25a" in mk_of(p_, "SkyyMtabKvB").lower(),
            "OLD8 PAGE the coin numbers are gold (Style Guide 15)")
    K.check(txt4(cm, "KvL1") == "Bank Lv 2 of 10: holds up to 250,000 coins, 1.1% interest." and txt4(cm, "KvL2").startswith("Upgrade to Lv 3: holds 500,000")
            and txt4(cm, "KvLo") == "" and vis8(cm, "KvUr") and txt4(cm, "KvU") == "Upgrade to Lv 3  -  75,000 coins",
            "OLD8 PAGE BANK LEVEL: the level line in two, Upgrade with the next level + its cost (%s)" % txt4(cm, "KvU"))
    K.check(txt4(cm, "KvR") == "Interest every day at your level: 1.1% up to 100,000 | then 0.5%" and txt4(cm, "KvN") == "Next payout in 3h 12m"
            and vis8(cm, "KvG0") and not vis8(cm, "KvG1") and txt4(cm, "KvG0") == "+1,320 coins at the next payout",
            "OLD8 PAGE INTEREST: the rate line (its '|' kept: the last field is the rest of the line), the next payout, the gain line green")
    K.check(all(vis8(cm, k_) for k_ in ("KvDa", "KvWa", "KvD", "KvW", "KvQBox")) and all(len(bind4(p_, a_)) == 1 and '"t"' in bind4(p_, a_)[0][2] for a_ in ("kvda", "kvwa", "kvd", "kvw", "kvu"))
            and "@B" in bind4(p_, "kvd")[0][2] and "@B" in bind4(p_, "kvw")[0][2] and len(bind4(p_, "kvamt")) == 1 and len(bind4(p_, "kvrf")) == 1 and not bind4(p_, "kvrf")[0][2].count('"t"'),
            "OLD8 PAGE the coin buttons carry the page token (Deposit / Withdraw the typed box too); Enter in the box; Refresh is navigation")
    K.check(cap3(p_) == str(MTD.KVCAP) and not vis8(cm, "KvA0") and not vis8(cm, "KvA1") and not vis8(cm, "KvA2"), "OLD8 PAGE the caption; no answer line yet")
    # ---- ACT: every button = the exact bridge call with the view's token + profile key; every answer = ONE new read
    tk_ = BK["cur"][0]
    p_, nv_ = kv_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 ACT Deposit all")
    cm = cmap(p_)
    K.check(BK["acts"][-1] == ["depall", uk3, tk_, "prof-A", ""] and BK["purse"] == 0 and BK["bank"] == 170000 and nv_ == 1 and cap3(p_) == "Deposited 50,000 coins."
            and vis8(cm, "KvA0") and txt4(cm, "KvA0") == "Deposited 50,000 coins." and txt4(cm, "KvP") == "0 coins" and only8(p_),
            "OLD8 ACT Deposit all = bank:fn:act depall {UUID, the view's token, its profile key, ''}; '+' = the caption + a green answer line; read again (%s)" % BK["acts"][-1:])
    tk_ = BK["cur"][0]
    p_, nv_ = kv_ev({"a": "kvwa", "t": str(MS.tok)}, "OLD8 ACT Withdraw all")
    K.check(BK["acts"][-1] == ["wdall", uk3, tk_, "prof-A", ""] and BK["bank"] == 0 and BK["purse"] == 170000 and nv_ == 1, "OLD8 ACT Withdraw all = wdall (%s)" % BK["acts"][-1:])
    tk_ = BK["cur"][0]
    p_, nv_ = kv_ev({"a": "kvd", "t": str(MS.tok), "@B": " 2K"}, "OLD8 ACT Deposit typed 2k")
    K.check(BK["acts"][-1] == ["deposit", uk3, tk_, "prof-A", "2k"] and BK["bank"] == 2000 and nv_ == 1 and str(val4(cmap(p_), "KvQ")) == "" and str(MS.kvTyped) == "",
            "OLD8 ACT Deposit = deposit <the typed amount, cleaned>; done = the box empties (a second press cannot repeat it) (%s)" % BK["acts"][-1:])
    tk_ = BK["cur"][0]
    p_, nv_ = kv_ev({"a": "kvw", "t": str(MS.tok), "@B": "1k"}, "OLD8 ACT Withdraw typed 1k")
    K.check(BK["acts"][-1] == ["withdraw", uk3, tk_, "prof-A", "1k"] and BK["bank"] == 1000 and nv_ == 1, "OLD8 ACT Withdraw = withdraw <the typed amount>")
    p_, nv_ = kv_ev({"a": "kvd", "t": str(MS.tok), "@B": ""}, "OLD8 ACT Deposit with an empty box")
    cm = cmap(p_)
    K.check(BK["acts"][-1][0] == "deposit" and BK["acts"][-1][4] == "" and cap3(p_).startswith("Type an amount in the box first") and vis8(cm, "KvA2") and not vis8(cm, "KvA0")
            and BK["bank"] == 1000 and nv_ == 1, "OLD8 ACT an empty box = the bridge's '=' note in the caption + a plain answer line, nothing moved, read again")
    p_, nv_ = kv_ev({"a": "kvamt", "@B": "1.5m"}, "OLD8 ACT Enter in the box")
    cm = cmap(p_)
    K.check(BK["acts"][-1][0] == "amount" and BK["acts"][-1][4] == "1.5m" and "Enter alone never moves coins" in cap3(p_) and str(val4(cm, "KvQ")) == "1.5m" and nv_ == 1
            and BK["bank"] == 1000, "OLD8 ACT Enter in the box = amount <typed> (the page's note in the caption), the typed amount kept in the box, nothing moved")
    p_, nv_ = kv_ev({"a": "kvd", "t": str(MS.tok), "@B": "900k"}, "OLD8 ACT a refused deposit")
    cm = cmap(p_)
    K.check(BK["acts"][-1][0] == "deposit" and cap3(p_).startswith("You only have") and vis8(cm, "KvA1") and not vis8(cm, "KvA0") and str(val4(cm, "KvQ")) == "900k"
            and BK["bank"] == 1000 and nv_ == 1, "OLD8 ACT a '-' answer = a refusal: the caption + a red answer line, the typed amount stays, nothing moved")
    # Upgrade: ONE press (the page's), the level + price the view showed guard it
    BK["bank"] = 200000
    p_ = mt_ev({"a": "kvrf"}, "OLD8 UPG redraw with 200k banked")
    tk_ = BK["cur"][0]
    p_, nv_ = kv_ev({"a": "kvu", "t": str(MS.tok)}, "OLD8 UPG Upgrade")
    cm = cmap(p_)
    K.check(BK["acts"][-1] == ["upgrade", uk3, tk_, "prof-A", ""] and BK["lv"] == 3 and BK["bank"] == 125000 and nv_ == 1 and txt4(cm, "KvU") == "Upgrade to Lv 4  -  112,500 coins"
            and cap3(p_).startswith("Your bank is now Lv 3"), "OLD8 UPG Upgrade = bank:fn:act upgrade with the view's token (ONE press); the next drawing shows the next price (%s)" % txt4(cm, "KvU"))
    BK["costx"] = 5
    p_, nv_ = kv_ev({"a": "kvu", "t": str(MS.tok)}, "OLD8 UPG the price changed since the view")
    K.check(cap3(p_).startswith("The upgrade price changed since you looked") and BK["lv"] == 3 and BK["bank"] == 125000 and nv_ == 1
            and txt4(cmap(p_), "KvU") == "Upgrade to Lv 4  -  112,505 coins", "OLD8 UPG a price that changed after the view = the bridge's '=' line, nothing charged; the redraw shows the new price")
    BK["costx"] = 0
    BK["lv"] = 10
    p_ = mt_ev({"a": "kvrf"}, "OLD8 UPG the top level")
    cm = cmap(p_)
    K.check(not vis8(cm, "KvUr") and not bind4(p_, "kvu") and txt4(cm, "KvLo") == "Your bank is at its top level (Lv 10).", "OLD8 UPG the top level = no Upgrade, said")
    n8_ = len(BK["acts"])
    p_ = mt_ev({"a": "kvu", "t": str(MS.tok)}, "OLD8 SAFE a forged Upgrade at the top level")
    K.check(len(BK["acts"]) == n8_ and cap3(p_) == str(MTD.KVNONE), "OLD8 SAFE an Upgrade the drawing did not show = a caption, no call")
    BK["lv"] = 3
    # ---- STALE: a token that is not the bridge's last (another bank page drew meanwhile) / an older drawing of this screen
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STALE redraw")
    BK["tok"] += 10
    BK["cur"] = ("t%d" % BK["tok"],) + tuple(BK["cur"][1:])   # the /bank page (or another screen) read the view meanwhile: our token is dead
    b8_ = (BK["purse"], BK["bank"])
    p_, nv_ = kv_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 STALE Deposit all with a dead token")
    K.check(cap3(p_).startswith("That click was for an older copy of this page, so nothing was moved") and (BK["purse"], BK["bank"]) == b8_ and nv_ == 1,
            "OLD8 STALE a dead click token = the bridge's '=' older-copy line, nothing moved, the view read again (a new token)")
    tk_ = BK["cur"][0]
    p_, nv_ = kv_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 STALE the same press again")
    K.check(BK["acts"][-1][2] == tk_ and BK["purse"] == 0 and nv_ == 1, "OLD8 STALE the press again carries the new token and runs")
    BK["purse"] = 1000
    n8_ = len(BK["acts"])
    v8_ = len(BK["views"])
    p_ = mt_ev({"a": "kvwa", "t": "old"}, "OLD8 SAFE an older drawing")
    K.check(len(BK["acts"]) == n8_ and "The page changed" in cap3(p_) and len(BK["views"]) == v8_ + 1, "OLD8 SAFE a press from an older drawing = 'The page changed', no call, drawn again (ONE read)")
    # the purse changed after the view (Deposit all moves only what the player saw)
    BK["purse"] = 4321
    p_, nv_ = kv_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 SAFE the purse changed since the view")
    K.check(cap3(p_).startswith("Your purse changed since you looked (4,321 coins now)") and BK["purse"] == 4321 and nv_ == 1, "OLD8 SAFE Deposit all of a purse that changed = '=', nothing moved")
    # a profile switch between the view and the press
    BK["pk"], BK["epoch"] = "prof-B", 2
    p_, nv_ = kv_ev({"a": "kvwa", "t": str(MS.tok)}, "OLD8 SAFE a profile switch")
    K.check(BK["acts"][-1][3] == "prof-A" and cap3(p_).startswith("Your profile changed after this page opened") and nv_ == 1, "OLD8 SAFE a profile switch = the bridge refuses ('='), read again")
    p_, nv_ = kv_ev({"a": "kvwa", "t": str(MS.tok)}, "OLD8 SAFE after the switch")
    K.check(BK["acts"][-1][3] == "prof-B" and cap3(p_).startswith("Withdrew"), "OLD8 SAFE after the redraw the new profile key is sent")
    BK["pk"], BK["epoch"] = "prof-A", 1
    # a null answer (not on the world thread): said, nothing read again
    BK["anull"] = True
    v8_ = len(BK["views"])
    p_ = mt_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 a null answer")
    K.check(cap3(p_) == str(MTD.KVNULL) and len(BK["views"]) == v8_, "OLD8 a null answer = 'That could not run here - nothing changed.' (nothing read)")
    BK["anull"] = False
    # ---- STATES: no profile key (token '-'), levels off, no SkyyCoins, unreadable, locked, a '-' line, a null read
    BK["pk"] = ""
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE no profile key")
    cm = cmap(p_)
    K.check(not bool(MS.kvMove) and not vis8(cm, "KvDa") and not vis8(cm, "KvD") and not bind4(p_, "kvda") and not bind4(p_, "kvamt") and not vis8(cm, "KvUr"),
            "OLD8 STATE no click token ('-') = no coin buttons, no Enter")
    n8_ = len(BK["acts"])
    p_ = mt_ev({"a": "kvw", "t": str(MS.tok), "@B": "5"}, "OLD8 SAFE a forged Withdraw without a token")
    p2_ = mt_ev({"a": "kvamt", "@B": "5"}, "OLD8 SAFE a forged Enter without a token")
    K.check(len(BK["acts"]) == n8_ and cap3(p_) == str(MTD.KVNONE) and cap3(p2_) == str(MTD.KVNONE), "OLD8 SAFE coin presses without a drawn token = a caption, no call")
    BK["pk"] = "prof-A"
    BK["lvOn"] = False
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE bank levels off")
    cm = cmap(p_)
    K.check(txt4(cm, "KvL1") == str(MTD.KVLVOFF) and txt4(cm, "KvL2") == "" and not vis8(cm, "KvUr") and txt4(cm, "KvC") == "No limit on what your bank holds"
            and txt4(cm, "KvS") == "Profile: Main profile" and vis8(cm, "KvDa"), "OLD8 STATE levels off = said, no Upgrade, no cap (the coin buttons stay)")
    BK["lvOn"] = True
    BK["coins"] = False
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE no SkyyCoins")
    K.check(txt4(cmap(p_), "KvP") == "no SkyyCoins" and txt4(cmap(p_), "KvB").endswith(" coins"), "OLD8 STATE no SkyyCoins = the purse says so (the view's text, no 'coins')")
    BK["coins"] = True
    BK["readable"] = False
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE unreadable")
    cm = cmap(p_)
    K.check(txt4(cm, "KvB") == "unreadable" and vis8(cm, "KvG1") and not vis8(cm, "KvG0") and txt4(cm, "KvG1") == "Your bank file could not be read"
            and not appended4(p_, "SkyyMtabKvBb") and txt4(cm, "KvC") == "Holds up to 500,000 coins", "OLD8 STATE an unreadable bank = 'unreadable', the gain line red, no bar, no room")
    BK["readable"] = True
    BK["locked"] = True
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE locked")
    cm = cmap(p_)
    K.check(vis8(cm, "KvK") and not vis8(cm, "Kvb") and txt4(cm, "KvK") == "Your bank is still locked - finish the Bank quest to open it." and not bind4(p_, "kvda")
            and not bind4(p_, "kvu") and txt4(cm, "KvH") == "" and only8(p_), "OLD8 STATE locked = the lock text only (no numbers, no buttons)")
    n8_ = len(BK["acts"])
    p_ = mt_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 SAFE Deposit all while locked")
    K.check(len(BK["acts"]) == n8_ and cap3(p_) == str(MTD.KVNONE), "OLD8 SAFE a coin press while locked = a caption, no call")
    BK["locked"] = False
    BK["dash"] = "-Unknown player."
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE a '-' line")
    K.check(txt4(cmap(p_), "KvH") == "Unknown player." and not vis8(cmap(p_), "Kvb") and not bind4(p_, "kvda"), "OLD8 STATE a '-' line = said in the head, nothing to press")
    BK["dash"] = None
    BK["vnull"] = True
    p_ = mt_ev({"a": "kvrf"}, "OLD8 STATE a null read")
    K.check(txt4(cmap(p_), "KvH") == str(MTD.KVFAIL) and not vis8(cmap(p_), "Kvb"), "OLD8 STATE a null read = 'could not be read right now'")
    BK["vnull"] = False
    # ---- NAVIGATION: the Bank sub-tab on every view head, the Market tab = the cards, card buttons only on the cards, never a timer
    p_ = mt_ev({"a": "vw:2"}, "OLD8 NAV the Merchants sub-tab")
    K.check(int(MS.view) == 2 and has4(p_, "SkyyMtabMvT4") and not has4(p_, "SkyyMtabKv"), "OLD8 NAV every view head has the Bank sub-tab")
    n8_ = len(BK["acts"])
    p_ = mt_ev({"a": "kvda", "t": str(MS.tok)}, "OLD8 SAFE a Bank button in another view")
    K.check(len(BK["acts"]) == n8_ and "not on this page" in cap3(p_), "OLD8 SAFE a Bank view press in another view = a caption, no call")
    v8_ = len(BK["views"])
    p_ = mt_ev({"a": "vw:4"}, "OLD8 NAV the Bank sub-tab")
    K.check(int(MS.view) == 4 and only8(p_) and len(BK["views"]) == v8_ + 1 and not vis8(cmap(p_), "KvA0"), "OLD8 NAV the Bank sub-tab = the Bank view (ONE read, no old answer line)")
    p_ = mt_ev({"a": "bank"}, "OLD8 SAFE the card's Bank button inside a view")
    K.check("not on this page" in cap3(p_), "OLD8 SAFE the card's Bank button only on the cards")
    p_ = mt_ev({"a": "tab:3"}, "OLD8 NAV the Market tab in the Bank view")
    K.check(int(MS.view) == 0 and has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabKv"), "OLD8 NAV the Market tab = the cards (no back button)")
    v8_ = len(BK["views"])
    p_ = mt_ev({"a": "kvrf"}, "OLD8 SAFE Refresh on the cards")
    K.check("not on this page" in cap3(p_) and len(BK["views"]) == v8_, "OLD8 SAFE a Bank view press on the cards = a caption, the bank view not read")
    E.pump(PK)
    v8_ = len(BK["views"])
    for _x in range(3):
        E.pump(PK)
    K.check(len(BK["views"]) == v8_, "OLD8 NEVER A TIMER: no bank:fn:view read without a drawing")
    K.notes.append("OLD8 ran: bank reads %d, bank acts %d" % (len(BK["views"]), len(BK["acts"])))
    for k_ in ("bank:fn:view", "bank:fn:act"):
        BR.remove(k_)
'''

EXPECT_BODY = '''    "MarketTab": ["+f kvAk", "+f kvAns", "+f kvLast", "+f kvMove", "+f kvPk", "+f kvState", "+f kvTok", "+f kvTyped", "+f kvUp", "+m fillKv", "+m kvAct",
                  "+m kvShow", "~c ", "~m build", "~m fillHv", "~m fillMv", "~m fillOv", "~m goView", "~m handleDataEvent", "~m viewOf"],
    # fillHv / fillMv / fillOv: MarketTabData.SIDE (a compile-time constant, inlined) holds MT_VBW (170 -> 140 for the fifth sub-tab)
    "MarketTabData": ["+f KVBAR", "+f KVCAP", "+f KVFAIL", "+f KVLVOFF", "+f KVNONE", "+f KVNULL", "+f KVOFF", "+f KVOLD", "~<clinit>"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''


def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.75 (old menu follow-up - the World tab's Travel view = the old World > Teleport page; tools/menu_0_3_75_patch.py,''',
      '''"""Harness for SkyyMenu 0.3.76 (old menu follow-up - the Market tab's Bank view = the old Storage > Bank link; tools/menu_0_3_76_patch.py,
round oldmenu8). GENERATED by tools/menu_0_3_76_patch.py from the 0.3.75 harness (edit the patch, not this file): every 0.3.75 check runs again
on the 0.3.76 jar (TAB3: the card's Bank button = the Bank view, still ONE packet; OLD7's ratchet = 'stays gone'; OLD2: storage:bank gone), plus
  OLD8 STATIC   the ratchet: OLD_LEFT lost storage:bank; no storage:bank / Vault link on the Market screen; the view reads bank:fn:view and
                acts through bank:fn:act with the read's token + profile key, no timer; the build asserts the view fits; the budget (+ K)
       HOME     the bank card's button reads Bank
       FALL     SkyyBank 0.1.17 (bank:fn:panel only) = the view names 0.1.18; no SkyyBank = not on this server; a forged coin press = no call
       PAGE     Refresh = act refresh + ONE read; purse / bank gold, cap line + bar, the line above, level line + Upgrade (next level + cost),
                rate (its '|' kept) / next payout / gain (green); the coin buttons carry the page token; Enter; ONE section; element count
       ACT      Deposit all / Withdraw all / Deposit + Withdraw (typed, cleaned) / Enter (amount) / Upgrade = the exact bridge call with the
                view's token + profile key; '+' green, '-' red (refusal), '=' plain, each in the caption; every answer = ONE new read; the box
                empties after a move, stays after a refusal / note
       UPG      ONE press; a price changed since the view = '='; the top level = no Upgrade, a forged one = no call
       STALE    a dead click token = the older-copy '=' then the press again runs with the new token; an older drawing = 'The page changed';
                a changed purse; a profile switch (the new key after the redraw); a null answer = said, nothing read
       STATE    no token, levels off, no SkyyCoins, unreadable (red gain, no bar), locked (the lock text only, a forged press = no call), a '-'
                line, a null read
       NAV      the Bank sub-tab on every view head, a Bank press in another view / on the cards = no call, the Market tab = the cards, no
                read without a drawing (never a timer)
       every new packet: every b.set / append / binding names an element drawn in that packet (the frame + ONE section)
The 0.3.75 harness text follows:
Harness for SkyyMenu 0.3.75 (old menu follow-up - the World tab's Travel view = the old World > Teleport page; tools/menu_0_3_75_patch.py,''')
T.rep('VERSION = "0.3.75"\nJAR', 'VERSION = "0.3.76"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.74.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.75.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.74.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.75.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_75_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_76_patch.py")')
T.rep('"scratch", "oldmenu7", "menu"', '"scratch", "oldmenu8", "menu"')
T.rep('ADDED = ["WorldSpawn"]   # 0.3.75: the Travel view\'s Spawn (the spawn point -> the player\'s world thread)\n', 'ADDED = []   # 0.3.76: no new class\n')
EXPECT_76 = '''EXPECT = {   # 0.3.76: the Market tab's Bank view, the version strings
@@EXPECT@@
}
'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.75:', 'if "--expect-dump" in sys.argv:'), EXPECT_76.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.75"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.76"') == 1, "S VERSION")
''' + HARNESS_OLD8_STATIC.rstrip("\n"))
# OLD7's ratchet compared 0.3.75 with 0.3.74: against 0.3.75 it is OLD8's (above) - its row stays gone
T.rep('''    K.check(lefto_ - left2_ == set([("world", "teleport")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 1,
            "OLD7 RATCHET OLD_LEFT lost world:teleport, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(("world", "teleport") not in left2_, "OLD7 RATCHET (0.3.76: vs 0.3.75) world:teleport stays gone")''')
# OLD2 (0.3.70) kept storage:bank on the Vault button: 0.3.76 takes it out (the Bank view)
T.rep('''    K.check('hub("storage", "bank", "the Vault")' in g and 'G_.glass_button(MT + "Bpg", "Vault"' in g and 'act("start", this.starts[si]);' in g''',
      '''    K.check('hub("storage", "bank"' not in g and 'G_.glass_button(MT + "Bpg", "Bank"' in g and 'act("start", this.starts[si]);' in g   # 0.3.76: storage:bank gone''')
T.rep('''            "OLD2 STATIC the Vault button keeps storage:bank; starters / egg fusing go through pets:fn:tabact; Set up + the Server Setup card share setupOf")''',
      '''            "OLD2 STATIC (0.3.76) the bank card's button = the Bank view (storage:bank gone); starters / egg fusing go through pets:fn:tabact; Set up + the Server Setup card share setupOf")''')
T.rep('''    K.check("Vault" in str(sval(cmap(p_), "#SkyyMtabBpg.Text")) or 'G_.glass_button(MT + "Bpg", "Vault"' in open(GEN, encoding="utf8").read(), "OLD2 F3 the old Bank page button reads Vault")''',
      '''    K.check('G_.glass_button(MT + "Bpg", "Bank"' in open(GEN, encoding="utf8").read(), "OLD2 F3 (0.3.76) the bank card's button reads Bank (the Bank view)")''')
T.rep('''    for a_, what in (("full", "a forged Full page (0.3.72: gone)"), ("mer", "See merchants (0.3.72: the merchants view)"), ("bank", "the Bank page"), ("tab:4", "World")):''',
      '''    for a_, what in (("full", "a forged Full page (0.3.72: gone)"), ("mer", "See merchants (0.3.72: the merchants view)"), ("bank", "Bank (0.3.76: the Bank view)"), ("tab:4", "World")):''')
T.rep('''    for k_ in ("ah:fn:tab", "ah:fn:tabact"):
        BR.remove(k_)
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:panel", "bank:fn:move", "ah:fn:view", "ah:fn:find", "ah:fn:open", "bazaar:fn:open"):''',
      '''    for k_ in ("ah:fn:tab", "ah:fn:tabact"):
        BR.remove(k_)
''' + HARNESS_OLD8.rstrip("\n") + '''
    for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:panel", "bank:fn:move", "ah:fn:view", "ah:fn:find", "ah:fn:open", "bazaar:fn:open"):''')
HARNESS_OLD8_HUB = r'''    # OLD8 FIX (0.3.76): storage:bank is SkyyBank's hub tab (its BankHubOpen), never SkyyMenu's: MenuHub.page / openFor do not serve "bank"
    # with the old menu ON or OFF (so no MenuHub.page route like OLD7's teleport can exist here); with it OFF /storage + home() = the new screen
    for on_ in (True, False):
        CFG.OLD_MENU = on_
        o_clear()
        f0_ = len(E.sent(PO))
        pg8_ = MH.page(PO.pr, "bank")
        ok8_ = bool(MH.openFor(PO.pr.getUuid(), "bank"))
        K.check(pg8_ is None and not ok8_ and "bank" not in [str(x_) for x_ in JV("MenuData").HT_TAB] and not pages(PO, f0_),
                "OLD8 HUBTAB old menu %s: SkyyMenu does not serve the storage:bank hub tab (SkyyBank's own) - nothing opened" % ("ON" if on_ else "OFF"))
        E.pump(PO)
    CFG.OLD_MENU = False
    o_clear()
    f0_ = len(E.sent(PO))
    ok8_ = bool(MH.home(PO.ref, PO.st, PO.pr))
    K.check(ok8_ and o_cur() != "MenuPage", "OLD8 HUBTAB old menu OFF: home() = the new screen, never the old Home (its 'bank' shortcut tile is old-menu only) (%s)" % o_cur())
    E.pump(PO)
    CFG.OLD_MENU = False   # as the OLD7 loop left it
    o_clear()
'''
T.rep('''    o_clear()
    # FIX (Skyy "remove the old "Full tree""): the Right now 'unspent tree points' row''', HARNESS_OLD8_HUB + '''    # FIX (Skyy "remove the old "Full tree""): the Right now 'unspent tree points' row''')
if T.dst:
    T.finish()
