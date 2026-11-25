"""Derive SkyyMenu/build_skyymenu_0.3.80.py + SkyyMenu/test_skyymenu_0.3.80.py from the SET pin SkyyMenu 0.3.79 (generated - never re-run
its patch). Run:  python tools/menu_0_3_80_patch.py   then   python SkyyMenu/build_skyymenu_0.3.80.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.80.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Uses the DEPLOYED SkyyVault 0.1.11 (tools/vault_0_1_11_patch.py: vault:fn:view / vault:fn:act, TEST 333);
with an older SkyyVault the view names 0.1.11 (/vault and Storage > Vault work as before).

0.3.80 (2026-11-24, round vaultview) = THE VAULT ITEMS VIEW IN THE NEW SCREEN. Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE
OLD MENU'): "when everything is in the new system id like to disable the old menu compleatly, so instead of adding things like the full tree
button, just build it all into the new system and remove the old "Full tree""; 2026-11-24 "keep building". WHERE (a stopgap): the LOCKED
7-tab plan (docs/answered/ui.md 2026-11-14: "Bank under Market, Vault = an Inventory pocket tab"; it replaced the 12-tab table) puts the Vault
in an Inventory pocket tab, which the new screen does not have yet - until it does, the Vault sits next to the coins (the MARKET tab's Bank view,
0.3.76) as the Market screen's sixth view (MOVE IT to the Inventory pocket tab when that tab is built): sub-tabs Market | Bazaar orders | Merchants | Auction House | Bank | Vault (no back button; the frame + ONE view per packet;
MT_VBW 140 -> 116 so six sub-tabs + the head line fit). The Bank view's '/vault opens it' hint now points at the Vault sub-tab.
THE VAULT VIEW (section V) = SkyyVault 0.1.11's vault:fn:view / vault:fn:act (contract: the header of tools/vault_0_1_11_patch.py):
  PAGES: one row of 6 page buttons (own 'n  used/usable', next 'n  Buy', locked 'n  Locked'; the shown page selected), < > move the row (no
      call, a redraw = a new read), 'a-b of N'. A page button = act 'page <n>' ('+' / '-' = the Menu then views page n; the locked line
      shows instead of the grid).
  THE GRID: the shown page's slots (h field 9, up to 90 = 9 x 10 cells of 52 px - slotsPerPage max 90, asserted), item icons + counts from the s|
      lines drawn as new ItemStack(id, qty, durability, max, null) only (HANDOFF 2: never a metadata stack), the quality index -> the stack's
      quality (InvPage.slot: the rarity tint on the slot + the name in its colour, Style Guide 15; the item's own quality = the client's own
      rarity frame), a tooltip (where it is + the yellow click footer); r| slots = 'Page arrow' (never filled). Click a slot = act
      'take <page>:<slot>:<qty>:<id>' (the whole shown stack).
  YOUR INVENTORY: hotbar / storage / backpack grids from the c| / i| lines (9 / 36 / 36 cells; more = a note, Open shows them). Click a slot =
      act 'put <section>:<slot>:<qty>:<shown page>:<id>' (only while an owned page is shown).
  NEXT PAGE (the b| line): its text, the price / bank level line; Buy only in state 'buy' (one press below buyConfirmCoins; at or above it
      (confirm 1) Buy arms a separate Confirm button for 10 s and sends nothing - Confirm sends 'buy <page>:<price>:1'; a double click on Buy
      only re-arms; any drawing drops the arm). bank / never / max = said, no button.
  CHEST WINDOW: Open = act 'open <shown page>' ('+' = the vanilla chest window replaced the page: no redraw); Refresh = act 'refresh' + a read.
  NEVER A VALUE THE PLAYER DID NOT SEE: every act carries the view's click token + profile key (h fields 3 + 4) and the exact shown slot / id /
      qty / page / price; vault:fn:view is read on every drawing (open, every answer, Refresh, < >) and NEVER on a timer; every answer redraws
      (a new read = a new token; the used token is dropped at once, so a second press of the same drawing is 'The page changed', no call); '+'
      green / '-' red / '=' plain in the caption + the answer line, '=' then the same press again after the redraw; a null answer = 'That could
      not run here - nothing changed.' (nothing read again); 'off|<reason>' = the reason line only (no grid, no buttons); no / older
      SkyyVault = the head names 0.1.11; a button the drawing did not show (no token / locked page / no Buy) = a caption, no call.
New: no class / command / system / picture / lang key / setting / saved data. Move inside the vault, split stacks and the typed amount stay
in the chest window (Open) - the vault:fn:act 'move' op and the take / put <amount> field are not used by this view (a later round if Skyy
wants them). Move to Void (ui.md 2026-10-10) = a later round (two steps: take, then the Pocket's deposit).
ROLLBACK to 0.3.79: safe alone (nothing saved; the Bank view's hint says '/vault opens it' again). SkyyVault 0.1.11 stays (its keys sit unused).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.79.py"), os.path.join(MOD, "build_skyymenu_0.3.80.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.79.py"), os.path.join(MOD, "test_skyymenu_0.3.80.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.79"\n') and P.has("menu:fn:bankview") and not P.has("vault:fn:view"), "not the generated SkyyMenu 0.3.79 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.79: /bank + SkyyBank's Storage > Bank tab''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.80: THE VAULT ITEMS VIEW: the Market screen's sixth view (sub-tab Vault, a stopgap until the Inventory tab's Vault pocket tab exists -
       docs/answered/ui.md 2026-11-14; the Bank view's hint points at it) = SkyyVault 0.1.11 vault:fn:view /
       vault:fn:act: page buttons (own / next / locked, used / usable), the shown page's grid (icons, counts, rarity tint + coloured names), the
       inventory's hotbar / storage / backpack; click a vault slot = take the shown stack, an inventory slot = put it on the shown page; Buy (two
       presses at or above buyConfirmCoins), Open (the chest window), Refresh. Every act carries the view's token + profile key + the shown values;
       the view is read again after every answer, never on a timer (notes: tools/menu_0_3_80_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.80.py.
0.3.79: /bank + SkyyBank's Storage > Bank tab''')
P.rep('VERSION = "0.3.79"\n', 'VERSION = "0.3.80"\n')

# ======================================================================= the sub-tab row gets Vault; the Bank view's hint points at it
P.rep('''MT_VBW = 140                                                # a sub-tab / side / shop tab button (0.3.76: 170 -> 140 for the fifth sub-tab)
MT_SUBS = ["Market", "Bazaar orders", "Merchants", "Auction House", "Bank"]   # 0.3.73: + the Auction House view; 0.3.76: + the Bank view''',
      '''MT_VBW = 116                                                # a sub-tab / side / shop tab button (0.3.76: 170 -> 140; 0.3.80: 140 -> 116 for the sixth)
MT_SUBS = ["Market", "Bazaar orders", "Merchants", "Auction House", "Bank", "Vault"]   # 0.3.73: + Auction House; 0.3.76: + Bank; 0.3.80: + Vault''')
P.rep('''    "kvvault": "Items are kept in your Vault - /vault opens it. This view is your coins.",''',
      '''    "kvvault": "Items are kept in your Vault - the Vault sub-tab above shows them. This view is your coins.",   # 0.3.80: was the /vault command hint''')

VV_CONST = r'''
# ---- 0.3.80 (vaultview): THE VAULT VIEW (section V) - SkyyVault 0.1.11 vault:fn:view / vault:fn:act (contract: tools/vault_0_1_11_patch.py header)
VV_LK = 60                                                  # the off| reason line (only while the vault is shut)
VV_BH = MT_VBH - VV_LK - 6                                  # the two cards under the head + the reason line (718)
VV_LW = 900                                                 # THE VAULT (pages, the grid, next page, chest window)
VV_RW = MT_VI - VV_LW - 10                                  # YOUR INVENTORY (626)
VV_LI, VV_RI = VV_LW - 20, VV_RW - 20
VV_GC, VV_GR, VV_S = 9, 10, 52                              # the vault grid: 9 columns, up to 10 rows, 52 px slots
VV_G = VV_GC * VV_GR                                        # cells shown (slotsPerPage max 90 = config range 9-90)
VV_GW, VV_GH = SUI.glass_grid_size(VV_GC, VV_GR, VV_S)
VV_SW = VV_LI - VV_GW - 12                                  # the side column right of the grid
VV_PN, VV_PBW, VV_PAW = 6, 106, 40                          # page buttons a row, their width, < >
VV_PIW = VV_LI - 2 * VV_PAW - 4 - 8 - VV_PN * (VV_PBW + 4)   # 'a-b of N'
VV_BYW, VV_RFW = 150, 160                                   # Buy, Refresh
VV_BCW = VV_SW - VV_BYW - 8                                 # Confirm
VV_IS = 60                                                  # an inventory slot
VV_IR = [1, 4, 4]                                           # rows: hotbar, storage, backpack (9 columns)
VV_IN = [9 * r_ for r_ in VV_IR]                            # cells a section shows (more = a note; Open shows them)
VV_IM = max(VV_IN)
VV_TXT = {
    "vvcap": "Your vault: click an item to move it between your vault and your inventory. Market on top goes back.",
    "vvold": "This needs SkyyVault 0.1.11 - this server has an older one. /vault works.",
    "vvoff": "The vault is not on this server right now.",
    "vvfail": "Your vault could not be read right now - press Refresh in a moment.",
    "vvnull": "That could not run here - nothing changed.",
    "vvnone": "That button is not on this page - nothing changed",
    "vvbn": "Big prices ask twice: Buy, then Confirm.",
    "vvol": "Drag, split and sort stacks in the game's chest window.",
    "vvx1": "Click an item in your vault to take it. Click one in your inventory to put it on the page shown.",
    "vvover": "Some slots do not fit this view - Open shows them all.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in VV_TXT.values() for c_ in v_), "0.3.80: plain texts"
assert VV_G >= 90, "0.3.80: the grid holds a whole page (slotsPerPage max 90)"
for _k in ("vvold", "vvoff", "vvfail", "vvnull"):
    assert SUI.text_width(VV_TXT[_k], 13) <= MT_VI - 240 - len(MT_SUBS) * (MT_VBW + 6), ("0.3.80: a vault head line fits", _k)
for _k in ("vvcap", "vvnone", "vvnull"):
    assert SUI.text_width(VV_TXT[_k], 14) <= IV_IW - 420, ("0.3.80: a caption fits the hint row", _k)
assert SUI.text_width(VV_TXT["vvx1"], 12) <= VV_LI, "0.3.80: the vault hint fits"
for _k in ("vvbn", "vvol", "vvover"):
    assert SUI.text_width(VV_TXT[_k], 12) <= VV_SW, ("0.3.80: a side line fits", _k)
for _l in ("1000  90/90", "1000  Locked", "1000  Buy"):
    assert SUI.text_width(_l, 14, bold=True) <= VV_PBW - 16, ("0.3.80: a page button fits", _l)
assert SUI.text_width("995-1000 of 1000", 12) <= VV_PIW, "0.3.80: the page row's count fits"
for _l, _w in (("Buy page 1000", VV_BYW), ("Confirm - 999,999,999 coins", VV_BCW), ("Open page 1000 in the chest window", VV_SW), ("Refresh", VV_RFW), ("<", VV_PAW)):
    assert SUI.text_width(_l, 14, bold=True) <= _w - 16, ("0.3.80: a vault button fits", _l)
assert SUI.text_width("Costs 999,999,999 coins - Buy, then Confirm", 12) <= VV_SW and SUI.text_width("Buy page 1000 - 999.9m coins", 13, bold=True) <= VV_SW, \
    "0.3.80: the next-page lines fit"
assert SUI.text_width("Click an item to put it on vault page 1000.", 12) <= VV_RI, "0.3.80: the inventory hint fits"
assert SUI.text_width("VAULT", 16, bold=True) <= 240 and SUI.text_width("Vault", 14, bold=True) <= MT_VBW - 16, "0.3.80: the title + the sub-tab fit"
# the run-time markup: a page button ({S} = only a style MarketTab passes)
VV_PB = "TextButton #SkyyMtab{I} { Anchor: (Width: %d, Height: 34, Right: 4); {S} }" % VV_PBW
_vv_mk = [VV_PB.replace("{I}", "Vp0").replace("{S}", MT_ST_CATSEL), VV_PB.replace("{I}", "Vp1").replace("{S}", MT_ST_CAT)]
for _mk in _vv_mk:
    SUI.check_markup(_mk, prefix=MT, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.80: a run-time markup line Java can hold"
_vv_tok = SUI.proven_tokens(_vv_mk)
assert not [k_ for k_, g_ in _vv_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], "0.3.80: the page button markup is proven"
VV_RUNTIME_MAX = VV_PN                                      # the page buttons
'''
P.rep('''KV_RUNTIME_MAX = 1                                          # the cap bar's fill
''', '''KV_RUNTIME_MAX = 1                                          # the cap bar's fill
''' + VV_CONST)

VV_LAYOUT = r'''    # ======== V: THE VAULT VIEW (0.3.80, vaultview: SkyyVault 0.1.11 vault:fn:view / act). The page buttons are appended at run time; the grids'
    # clicks, Buy / Confirm / Open are bound at run time (they carry the page token, only where the drawing showed them); Refresh + < > are static
    ap = SUI.Appends()
    vv = MT + "Vv"
    ap.append(("#" + win, G_.glass_group(vv, IV_IW, IV_BODY_H, role="panel", layout="Top", pad=10)))
    bv = vhead(ap, vv, "Vv", "VAULT", 5)
    ap.append(("#" + vv, lab(MT + "VvK", "", 15, "text", bold=True, w=MT_VI, h=VV_LK, anchor={"top": 6})))
    vb = MT + "Vvb"
    ap.append(("#" + vv, G_.glass_group(vb, MT_VI, VV_BH, layout="Left", anchor={"top": 6})))
    # ---- THE VAULT
    vl = MT + "VvLc"
    ap.append(("#" + vb, G_.glass_group(vl, VV_LW, VV_BH, role="inset", layout="Top", pad=10)))
    vp = MT + "VvPr"
    ap.append(("#" + vl, G_.glass_group(vp, VV_LI, 34, layout="Left")))
    ap.append(("#" + vp, G_.glass_button(MT + "VvPp", "<", "secondary", w=VV_PAW, h=34, size=14, anchor={"right": 4})))
    ap.append(("#" + vp, G_.glass_group(MT + "VvPs", VV_PN * (VV_PBW + 4), 34, layout="Left")))
    ap.append(("#" + vp, G_.glass_button(MT + "VvPn", ">", "secondary", w=VV_PAW, h=34, size=14, anchor={"right": 8})))
    ap.append(("#" + vp, lab(MT + "VvPi", "", 12, "dim", w=VV_PIW, h=34, halign="End")))
    ap.append(("#" + vl, lab(MT + "VvT", "", 13, "text", w=VV_LI, h=20, anchor={"top": 6})))
    vm = MT + "VvM"
    ap.append(("#" + vl, G_.glass_group(vm, VV_LI, VV_GH, layout="Left", anchor={"top": 6})))
    ap.append(("#" + vm, G_.glass_grid(MT + "VvG", VV_GC, VV_GR, drag=False, slot=VV_S, icon=VV_S - 12)))
    ap.append(("#" + vm, "Group { Anchor: (Width: 12); }"))
    vs = MT + "VvSd"
    ap.append(("#" + vm, G_.glass_group(vs, VV_SW, VV_GH, layout="Top")))
    ap.append(("#" + vs, lab(None, "NEXT PAGE", 15, "accentHi", bold=True, w=VV_SW, h=24)))
    ap.append(("#" + vs, lab(MT + "VvBl", "", 13, "text", bold=True, w=VV_SW, h=20, anchor={"top": 6})))
    ap.append(("#" + vs, lab(MT + "VvBl2", "", 12, "dim", w=VV_SW, h=18, anchor={"top": 2})))
    vbr = MT + "VvBr"
    ap.append(("#" + vs, G_.glass_group(vbr, VV_SW, 40, layout="Left", anchor={"top": 10})))
    ap.append(("#" + vbr, G_.glass_button(MT + "VvBy", "Buy", "primary", w=VV_BYW, h=40, size=14, anchor={"right": 8})))
    ap.append(("#" + vbr, G_.glass_button(MT + "VvBc", "Confirm", "primary", w=VV_BCW, h=40, size=14)))
    ap.append(("#" + vs, lab(MT + "VvBn", "", 12, "dim", w=VV_SW, h=18, anchor={"top": 4})))
    ap.sets.append((MT + "VvBn", "Text", VV_TXT["vvbn"]))
    ap.append(("#" + vs, lab(None, "CHEST WINDOW", 15, "accentHi", bold=True, w=VV_SW, h=24, anchor={"top": 28})))
    ap.append(("#" + vs, lab(MT + "VvOl", "", 12, "dim", w=VV_SW, h=18, anchor={"top": 4})))
    ap.sets.append((MT + "VvOl", "Text", VV_TXT["vvol"]))
    vor = MT + "VvOr"
    ap.append(("#" + vs, G_.glass_group(vor, VV_SW, 40, layout="Left", anchor={"top": 8})))
    ap.append(("#" + vor, G_.glass_button(MT + "VvO", "Open", "secondary", w=VV_SW, h=40, size=14)))
    ap.append(("#" + vs, G_.glass_button(MT + "VvRf", "Refresh", "secondary", w=VV_RFW, h=36, size=14, anchor={"top": 28})))
    ap.append(("#" + vs, lab(MT + "VvOv", "", 12, "dim", w=VV_SW, h=18, anchor={"top": 10})))
    assert 24 + 26 + 20 + 50 + 22 + 52 + 22 + 48 + 64 + 28 <= VV_GH, "0.3.80: the side column fits beside the grid"
    holder(ap, vl, MT + "VvA", VV_LI, 24, 14, ["green", "red", "text"], anchor={"top": 8}, bold=True)
    ap.append(("#" + vl, lab(MT + "VvX1", "", 12, "dim", w=VV_LI, h=18, anchor={"top": 6})))
    ap.sets.append((MT + "VvX1", "Text", VV_TXT["vvx1"]))
    assert 20 + 34 + 6 + 20 + 6 + VV_GH + 8 + 24 + 6 + 18 <= VV_BH, "0.3.80: the vault card fits"
    ap.append(("#" + vb, "Group { Anchor: (Width: 10); }"))
    # ---- YOUR INVENTORY
    vr = MT + "VvRc"
    ap.append(("#" + vb, G_.glass_group(vr, VV_RW, VV_BH, role="inset", layout="Top", pad=10)))
    ap.append(("#" + vr, lab(None, "YOUR INVENTORY", 15, "accentHi", bold=True, w=VV_RI, h=24)))
    ap.append(("#" + vr, lab(MT + "VvRh", "", 12, "dim", w=VV_RI, h=18, anchor={"top": 2})))
    _ih = 0
    for k_, (t_, r_) in enumerate(zip(("HOTBAR", "STORAGE", "BACKPACK"), VV_IR)):
        ap.append(("#" + vr, lab(None, t_, 13, "dim", bold=True, w=VV_RI, h=18, anchor={"top": 6})))
        ap.append(("#" + vr, G_.glass_grid(MT + "VvI%d" % k_, 9, r_, drag=False, slot=VV_IS, icon=VV_IS - 12)))
        _ih += 24 + SUI.glass_grid_size(9, r_, VV_IS)[1]
    assert SUI.glass_grid_size(9, 1, VV_IS)[0] <= VV_RI and 20 + 24 + 20 + _ih <= VV_BH, "0.3.80: the inventory card fits"
    assert VV_LW + 10 + VV_RW == MT_VI and 20 + 34 + 6 + VV_LK + 6 + VV_BH <= IV_BODY_H, "0.3.80: the vault view fits 1080"
    out.append(("V", ap, bv + [("#" + MT + "VvRf", "vvrf"), ("#" + MT + "VvPp", "vvpw:-1"), ("#" + MT + "VvPn", "vvpw:1")]))
    return out
'''
P.rep('''    out.append(("K", ap, bk + [("#" + MT + "KvRf", "kvrf")]))
    return out
''', '''    out.append(("K", ap, bk + [("#" + MT + "KvRf", "kvrf")]))
''' + VV_LAYOUT)
P.rep('''             "KvG0", "KvG1", "KvG2", "KvRf"]''', '''             "KvG0", "KvG1", "KvG2", "KvRf",
             # 0.3.80 (vaultview): the Vault view
             "Vv", "VvH", "VvT0", "VvT1", "VvT2", "VvT3", "VvT4", "VvT5", "VvK", "Vvb", "VvLc", "VvPr", "VvPp", "VvPs", "VvPn", "VvPi", "VvT", "VvM",
             "VvG", "VvSd", "VvBl", "VvBl2", "VvBr", "VvBy", "VvBc", "VvBn", "VvOl", "VvOr", "VvO", "VvRf", "VvOv", "VvA0", "VvA1", "VvA2", "VvX1",
             "VvRc", "VvRh", "VvI0", "VvI1", "VvI2"]''')
P.rep('''+ ["Mk%d" % k_ for k_ in range(MV_KN)] + ["Hm%d" % k_ for k_ in range(len(HMODE))]''',
      '''+ ["Mk%d" % k_ for k_ in range(MV_KN)] + ["Hm%d" % k_ for k_ in range(len(HMODE))] + ["Vp%d" % k_ for k_ in range(VV_PN)]''')
P.rep('''          "K": KV_RUNTIME_MAX}   # 0.3.76: the bank view's cap bar fill
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOMUK")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUK")   # 0.3.76: + K, the Bank view
print("0.3.76 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOMUK")))''',
      '''          "K": KV_RUNTIME_MAX,   # 0.3.76: the bank view's cap bar fill
          "V": VV_RUNTIME_MAX}   # 0.3.80: the vault view's page buttons
MT_SHELL_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] for _s in "HOMUKV")
MT_RUNTIME_MAX = max(_mt_rt.values())
MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUKV")   # 0.3.76: + K, the Bank view; 0.3.80: + V, the Vault view
assert _mt_by["0"] + _mt_by["V"] + _mt_rt["V"] <= 800, "0.3.80: the vault view's packet stays well under the ~1,600 element budget (%d)" % (_mt_by["0"] + _mt_by["V"] + _mt_rt["V"])
print("0.3.80 market sections (elements, + at run time): frame %d, %s" % (_mt_by["0"], ", ".join("%s %d + %d" % (_s, _mt_by[_s], _mt_rt[_s]) for _s in "HOMUKV")))''')

# ======================================================================= the data + the fields
P.rep('''for _k in ("kvcap", "kvold", "kvoff", "kvfail", "kvnull", "kvnone", "kvlvoff"):
    F(mtd, "public static final String %s = %s;" % (_k.upper(), jstr(KV_TXT[_k])))
''', '''for _k in ("kvcap", "kvold", "kvoff", "kvfail", "kvnull", "kvnone", "kvlvoff"):
    F(mtd, "public static final String %s = %s;" % (_k.upper(), jstr(KV_TXT[_k])))
# 0.3.80 (vaultview): the Vault view
for _n, _v in (("VVPN", VV_PN), ("VVG", VV_G), ("VVIM", VV_IM)):
    F(mtd, "public static final int %s = %d;" % (_n, _v))
F(mtd, "public static final int[] VVIN = new int[] { %s };" % ", ".join(str(n_) for n_ in VV_IN))
F(mtd, "public static final String VVPB = %s;" % jstr(VV_PB))
for _k in ("vvcap", "vvold", "vvoff", "vvfail", "vvnull", "vvnone", "vvover"):
    F(mtd, "public static final String %s = %s;" % (_k.upper(), jstr(VV_TXT[_k])))
''')
P.rep('''           "public String kvLast;", "public int kvAk;", "public String kvAns;",
''', '''           "public String kvLast;", "public int kvAk;", "public String kvAns;",
           # 0.3.80 (vaultview): the Vault view - the last read's token + profile key, the page asked / shown / owned / max, the page row's first page,
           # what the drawing showed (vault slots, inventory slots, page buttons, the Buy box), the Confirm arm, the answer line
           "public String vvTok;", "public String vvPk;", "public int vvPage;", "public int vvShown;", "public int vvOwn;", "public int vvMax;", "public int vvPw;",
           "public boolean vvPwFree;", "public boolean vvOk;", "public String[] vvSid;", "public int[] vvSq;", "public boolean[] vvArr;", "public String[] vvIid;",
           "public int[] vvIq;", "public int[] vvPgN;", "public String vvBst;", "public int vvBpg;", "public long vvBpr;", "public boolean vvBconf;",
           "public long vvArm;", "public int vvAk;", "public String vvAns;", "public String vvLast;",
''')
VV_INIT = r'''  this.vvTok = "-";        // 0.3.80 (vaultview)
  this.vvPk = "-";
  this.vvPage = 0;
  this.vvShown = 0;
  this.vvOwn = 0;
  this.vvMax = 0;
  this.vvPw = 0;
  this.vvPwFree = false;
  this.vvOk = false;
  this.vvSid = new String[0];
  this.vvSq = new int[0];
  this.vvArr = new boolean[0];
  this.vvIid = new String[0];
  this.vvIq = new int[0];
  this.vvPgN = new int[0];
  this.vvBst = "";
  this.vvBpg = 0;
  this.vvBpr = -1L;
  this.vvBconf = false;
  this.vvArm = 0L;
  this.vvAk = -1;
  this.vvAns = "";
  this.vvLast = null;
'''
P.rep('''  this.kvAns = "";
  this.builds = 0;''', '''  this.kvAns = "";
''' + VV_INIT + '''  this.builds = 0;''')

# ======================================================================= the Vault view's drawing (before build)
VV_DRAW = r'''# ---- 0.3.80 (vaultview): THE VAULT VIEW. vault:fn:view apply(Object[] { UUID, Integer page }) -> h| (14 fields) + b| / p| / t| / r| / s| / c| / i|
# lines, "off|<reason>", or null (SkyyVault 0.1.11, the header of tools/vault_0_1_11_patch.py). Read on every drawing of this view, never on a timer.
# mode: 0 = the head line only, 1 = the two cards, 2 = the reason line only
M(mtab, r"""
public void vvShow(@UCB@ b, String head, int mode) {
  b.set("#SkyyMtabVvH.Text", head == null ? "" : head);
  b.set("#SkyyMtabVvb.Visible", mode == 1);
  b.set("#SkyyMtabVvK.Visible", mode == 2);
  hold(b, "SkyyMtabVvA", 3, mode == 1 ? this.vvAk : -1, this.vvAns);
}""")
M(mtab, r"""
public void vvReset() {
  this.vvTok = "-";
  this.vvPk = "-";
  this.vvOk = false;
  this.vvSid = new String[0];
  this.vvSq = new int[0];
  this.vvArr = new boolean[0];
  this.vvIid = new String[0];
  this.vvIq = new int[0];
  this.vvPgN = new int[0];
  this.vvBst = "";
  this.vvBpg = 0;
  this.vvBpr = -1L;
  this.vvBconf = false;
  this.vvArm = 0L;
}""")
# a slot the view showed: a NEW ItemStack(id, qty, durability, max, no metadata) at the shown quality -> InvPage.slot (the rarity tint + the coloured
# name when the quality is not the item's own; the copy carries no metadata and no quality override), else (an id the server does not know) the
# name only; the tooltip says where it is + the yellow click footer (Style Guide 15)
M(mtab, r"""
public static @IGS@ vvCell(String id, int qty, int q, String du, String md, String where, String foot) {
  @IGS@ g = null;
  if (id != null && id.length() > 0 && id.length() < 120 && qty > 0 && @PKG@.InvPage.known(id)) {
    double d = 0.0;
    double m = 0.0;
    try { d = Double.parseDouble(du); } catch (Throwable t) { d = 0.0; }
    try { m = Double.parseDouble(md); } catch (Throwable t) { m = 0.0; }
    @IS@ s = new @IS@(id, qty, d, m, (@BSON@) null);
    if (q >= 0) { try { s = s.withQuality(q); } catch (Throwable t) { } }
    g = @PKG@.InvPage.slot(s);
  } else {
    g = new @IGS@();
    g.setActivatable(true);
    if (id != null && id.length() > 0) g.setName(@PKG@.MenuUtil.clip(id, 60) + "  x" + qty);
  }
  String nl = String.valueOf((char) 10);
  g.setDescription(col(@PKG@.MarketTabData.SOFT, where) + nl + nl + col(@PKG@.MarketTabData.FOOT, foot));
  return g;
}""")
M(mtab, r"""
public static @IGS@ vvArrow() {
  @IGS@ g = new @IGS@();
  g.setActivatable(true);
  g.setName("Page arrow");
  g.setDescription(col(@PKG@.MarketTabData.SOFT, "The chest window keeps its page arrow in this slot - nothing goes here."));
  return g;
}""")
M(mtab, r"""
public void fillVv(@UCB@ b, @UEB@ ev) {
  vvReset();
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.InvCraft.fn("vault:fn:view") == null || @PKG@.InvCraft.fn("vault:fn:act") == null) {
    this.vvLast = null;
    vvShow(b, @PKG@.InvCraft.fn("vault:fn:findLL") != null || @PKG@.InvCraft.fn("vault:fn:openBank") != null ? @PKG@.MarketTabData.VVOLD : @PKG@.MarketTabData.VVOFF, 0);
    return;
  }
  Object o = call("vault:fn:view", new Object[] { u, Integer.valueOf(this.vvPage) });
  this.calls = this.calls + 1;
  String s = o instanceof String ? (String) o : null;
  this.vvLast = s;
  if (s == null) { vvShow(b, @PKG@.MarketTabData.VVFAIL, 0); return; }
  if (s.startsWith("off|")) {
    String why = s.substring(4).replace((char) 10, ' ').replace((char) 13, ' ').trim();
    b.set("#SkyyMtabVvK.Text", @PKG@.MenuUtil.clip(why.length() > 0 ? why : "Your vault is closed right now - try again in a moment.", 160));
    vvShow(b, "", 2);
    return;
  }
  String[] ls = s.split("\\n");
  String[] h = ls.length > 0 && ls[0].startsWith("h|") ? sp(ls[0], 14) : new String[0];
  if (h.length < 14 || !"ok".equals(h[1])) {
    String why = @PKG@.MarketTabData.VVFAIL;
    if (ls.length == 1 && ls[0].startsWith("-")) why = @PKG@.MenuUtil.clip(@PKG@.InvPage.bare(ls[0]), 120);
    vvShow(b, why, 0);
    return;
  }
  boolean live = h[2].length() > 0 && !"-".equals(h[2]);
  this.vvTok = live ? h[2] : "-";
  this.vvPk = h[3];
  this.vvOk = live;
  int shown = ni(h[4], 0), own = ni(h[5], 0), max = ni(h[6], 0), cap = ni(h[8], 0);
  if (max < own) max = own;
  this.vvShown = shown;
  this.vvOwn = own;
  this.vvMax = max;
  boolean mine = shown >= 1 && shown <= own;
  boolean act = live && mine;
  int pn = @PKG@.MarketTabData.VVPN;
  if (!this.vvPwFree || this.vvPw < 1 || this.vvPw > max) this.vvPw = shown >= 1 ? ((shown - 1) / pn) * pn + 1 : 1;
  int pw = this.vvPw;
  this.vvPgN = new int[pn];
  vvShow(b, "", 1);
  int n = cap < 0 ? 0 : (cap > @PKG@.MarketTabData.VVG ? @PKG@.MarketTabData.VVG : cap);
  this.vvSid = new String[n];
  this.vvSq = new int[n];
  this.vvArr = new boolean[n];
  int im = @PKG@.MarketTabData.VVIM;
  this.vvIid = new String[3 * im];
  this.vvIq = new int[3 * im];
  int[] icap = new int[] { -1, -1, -1 };
  java.util.ArrayList cells = new java.util.ArrayList();
  for (int i = 0; i < n; i++) cells.add(null);
  java.util.ArrayList il = new java.util.ArrayList();
  String tl = "";
  String[] bl = null;
  int over = 0;
  String bk = String.valueOf((char) 64);
  for (int i = 1; i < ls.length; i++) {
    String l = ls[i];
    if (l.startsWith("t|")) tl = l.substring(2);
    else if (l.startsWith("b|")) bl = sp(l, 8);
    else if (l.startsWith("r|")) { int r = ni(l.substring(2), 0) - 1; if (r >= 0 && r < n) this.vvArr[r] = true; }
    else if (l.startsWith("c|")) { String[] f = sp(l, 3); if (f.length >= 3) { int k = ni(f[1], -1); if (k >= 0 && k < 3) icap[k] = ni(f[2], 0); } }
    else if (l.startsWith("i|")) il.add(sp(l, 9));
    else if (l.startsWith("s|")) {
      String[] f = sp(l, 8);
      if (!mine || f.length < 8) continue;
      int k = ni(f[1], 0) - 1;
      int q = ni(f[3], 0);
      if (k < 0 || q < 1 || f[2].length() == 0) continue;
      if (k >= n) { over = over + 1; continue; }
      this.vvSid[k] = f[2];
      this.vvSq[k] = q;
      cells.set(k, vvCell(f[2], q, ni(f[4], -1), f[5], f[6], "Vault page " + shown + ", slot " + (k + 1) + "  -  " + money((long) q), "Click: take all " + money((long) q) + " into your inventory"));
    }
    else if (l.startsWith("p|")) {
      String[] f = sp(l, 5);
      int q = f.length >= 5 ? ni(f[1], 0) : 0;
      int k = q - pw;
      if (q < 1 || k < 0 || k >= pn || this.vvPgN[k] != 0) continue;
      String tx = f[2].equals("own") ? q + "  " + ni(f[3], 0) + "/" + ni(f[4], 0) : (f[2].equals("next") ? q + "  Buy" : q + "  Locked");
      b.appendInline("#SkyyMtabVvPs", @PKG@.MarketTabData.VVPB.replace("{I}", "Vp" + k).replace("{S}", q == shown ? @PKG@.MarketTabData.ST_CATSEL : @PKG@.MarketTabData.ST_CAT));
      b.set("#SkyyMtabVp" + k + ".Text", tx);
      this.vvPgN[k] = q;
      if (live) ev.addEventBinding(@BT@.Activating, "#SkyyMtabVp" + k, @EVD@.of("a", "vvp:" + q).append("t", this.tok));
    }
  }
  int pe = pw + pn - 1 > max ? max : pw + pn - 1;
  b.set("#SkyyMtabVvPi.Text", max > 0 ? pw + "-" + pe + " of " + max : "");
  b.set("#SkyyMtabVvPp.Visible", pw > 1);
  b.set("#SkyyMtabVvPn.Visible", pw + pn <= max);
  b.set("#SkyyMtabVvT.Text", @PKG@.MenuUtil.clip(tl, 150));
  for (int i = 0; i < n; i++) if (cells.get(i) == null) cells.set(i, this.vvArr[i] ? vvArrow() : @PKG@.InvPage.slot(null));
  b.set("#SkyyMtabVvG.Slots", @PKG@.InvPage.act(cells));
  b.set("#SkyyMtabVvG.Visible", mine);
  if (act) ev.addEventBinding(@BT@.SlotClicking, "#SkyyMtabVvG", @EVD@.of("a", "vvs").append("t", this.tok), false);
  // YOUR INVENTORY: the c| / i| lines (a put needs an owned page on show)
  String[] nm = new String[] { "Hotbar", "Storage", "Backpack" };
  int[] sn = new int[3];
  java.util.ArrayList[] ic = new java.util.ArrayList[3];
  for (int k = 0; k < 3; k++) {
    int c = icap[k];
    int lim = @PKG@.MarketTabData.VVIN[k];
    sn[k] = c < 0 ? 0 : (c > lim ? lim : c);
    if (c > lim) over = over + 1;
    ic[k] = new java.util.ArrayList();
    for (int i = 0; i < sn[k]; i++) ic[k].add(null);
  }
  for (int j = 0; j < il.size(); j++) {
    String[] f = (String[]) il.get(j);
    if (f.length < 9) continue;
    int k = ni(f[1], -1);
    int sl = ni(f[2], 0) - 1;
    int q = ni(f[4], 0);
    if (k < 0 || k > 2 || sl < 0 || q < 1 || f[3].length() == 0) continue;
    if (sl >= sn[k]) { if (sl < icap[k]) over = over + 1; continue; }
    this.vvIid[k * im + sl] = f[3];
    this.vvIq[k * im + sl] = q;
    ic[k].set(sl, vvCell(f[3], q, ni(f[5], -1), f[6], f[7], nm[k] + " slot " + (sl + 1) + "  -  " + money((long) q),
        mine ? "Click: put all " + money((long) q) + " on vault page " + shown : "Show one of your own vault pages to put items in"));
  }
  for (int k = 0; k < 3; k++) {
    for (int i = 0; i < sn[k]; i++) if (ic[k].get(i) == null) ic[k].set(i, @PKG@.InvPage.slot(null));
    b.set("#SkyyMtabVvI" + k + ".Slots", @PKG@.InvPage.act(ic[k]));
    b.set("#SkyyMtabVvI" + k + ".Visible", sn[k] > 0);
    if (act && sn[k] > 0) ev.addEventBinding(@BT@.SlotClicking, "#SkyyMtabVvI" + k, @EVD@.of("a", "vvi:" + k).append("t", this.tok), false);
  }
  b.set("#SkyyMtabVvRh.Text", mine ? "Click an item to put it on vault page " + shown + "." : "Show one of your own vault pages to put items in.");
  b.set("#SkyyMtabVvOv.Text", over > 0 ? @PKG@.MarketTabData.VVOVER : "");
  // NEXT PAGE: the b| line (buy / bank / never / max); Buy only in state buy; a price at or above buyConfirmCoins = Buy, then Confirm
  boolean hb = bl != null && bl.length >= 8;
  this.vvBst = hb ? bl[1] : "";
  this.vvBpg = hb ? ni(bl[2], 0) : 0;
  this.vvBpr = hb ? nl(bl[3], -1L) : -1L;
  this.vvBconf = hb && "1".equals(bl[4]);
  int need = hb ? ni(bl[5], 0) : 0;
  int best = hb ? ni(bl[6], -1) : -1;
  boolean buy = live && "buy".equals(this.vvBst) && this.vvBpg > 0 && this.vvBpr >= 0L;
  String l2 = "";
  if ("buy".equals(this.vvBst)) l2 = this.vvBpr > 0L ? "Costs " + money(this.vvBpr) + " coins" + (this.vvBconf ? " - Buy, then Confirm" : " - one press") : "Free - one press";
  else if ("bank".equals(this.vvBst)) l2 = "Needs Bank Lv " + need + (best >= 0 ? " - yours is Lv " + best : "") + " (the Bank sub-tab)";
  else if ("never".equals(this.vvBst)) l2 = "More pages are not for sale on this server.";
  else if ("max".equals(this.vvBst)) l2 = "You own every vault page.";
  b.set("#SkyyMtabVvBl.Text", hb ? @PKG@.MenuUtil.clip(bl[7], 60) : "");
  b.set("#SkyyMtabVvBl2.Text", @PKG@.MenuUtil.clip(l2, 64));
  b.set("#SkyyMtabVvBr.Visible", buy);
  b.set("#SkyyMtabVvBc.Visible", false);
  if (buy) {
    b.set("#SkyyMtabVvBy.Text", "Buy page " + this.vvBpg);
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabVvBy", @EVD@.of("a", "vvb").append("t", this.tok));
    if (this.vvBconf) ev.addEventBinding(@BT@.Activating, "#SkyyMtabVvBc", @EVD@.of("a", "vvbc").append("t", this.tok));
  }
  // CHEST WINDOW: Open = the vanilla chest window of the shown page (owned pages only)
  b.set("#SkyyMtabVvOr.Visible", act);
  if (act) {
    b.set("#SkyyMtabVvO.Text", "Open page " + shown + " in the chest window");
    ev.addEventBinding(@BT@.Activating, "#SkyyMtabVvO", @EVD@.of("a", "vvo").append("t", this.tok));
  }
}""")
'''
P.rep('''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;''', VV_DRAW + '''M(mtab, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.MarketTabData.LK;''')
P.rep('''  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : (this.view == 3 ? 'U' : (this.view == 4 ? 'K' : 'H')));   // 0.3.73: + U (the Auction House); 0.3.76: + K (the Bank)''',
      '''  char cur = this.view == 1 ? 'O' : (this.view == 2 ? 'M' : (this.view == 3 ? 'U' : (this.view == 4 ? 'K' : (this.view == 5 ? 'V' : 'H'))));   // 0.3.73: + U (the Auction House); 0.3.76: + K (the Bank); 0.3.80: + V (the Vault)''')
P.rep('''    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.KVCAP);
    return;
  }''', '''    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.KVCAP);
    return;
  }
  if (this.view == 5) {   // 0.3.80 (vaultview): the Vault view reads SkyyVault's vault:fn:view only (a new click token per drawing)
    try { fillVv(b, ev); } catch (Throwable t) { vvReset(); @PKG@.MenuUtil.warn("market screen: the vault view failed: " + t); }
    b.set("#SkyyMtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.MarketTabData.VVCAP);
    return;
  }''')

# ======================================================================= the Vault view's acts (after kvAct)
VV_ACT = r'''# ---- 0.3.80 (vaultview): one Vault view act: vault:fn:act apply(Object[] { op, UUID, the view's token, the view's profile key, arg }) -> '+' done,
# '-' refused, '=' changed since the view (the player presses again after the redraw), "" nothing to say, null = not on the player's world thread
# (said, nothing read again). The used token is dropped at once; every answer = the caption + the answer line + a redraw (= vault:fn:view read
# again) - except open '+' (the vanilla chest window replaced this page: no redraw).
M(mtab, r"""
public void vvAct(String op, String arg) {
  this.answered = true;
  if (@PKG@.InvCraft.fn("vault:fn:act") == null || @PKG@.InvCraft.fn("vault:fn:view") == null) {
    say(@PKG@.InvCraft.fn("vault:fn:findLL") != null || @PKG@.InvCraft.fn("vault:fn:openBank") != null ? @PKG@.MarketTabData.VVOLD : @PKG@.MarketTabData.VVOFF);
    return;
  }
  Object o = call("vault:fn:act", new Object[] { op, this.playerRef.getUuid(), this.vvTok, this.vvPk, arg == null ? "" : arg });
  this.calls = this.calls + 1;
  if (o == null) { say(@PKG@.MarketTabData.VVNULL); return; }
  this.vvTok = "-";
  this.vvArm = 0L;
  String r = String.valueOf(o).replace((char) 10, ' ').replace((char) 13, ' ').trim();
  char c = r.length() > 0 ? r.charAt(0) : ' ';
  this.vvAk = c == '+' ? 0 : (c == '-' ? 1 : (r.length() > 0 ? 2 : -1));
  this.vvAns = @PKG@.MenuUtil.clip(@PKG@.InvPage.bare(r), 140);
  this.tcap = this.vvAns;
  if (op.equals("open") && c == '+') {
    if (!still()) { finish("vault window"); return; }
    say(this.vvAns);
    return;
  }
  if (op.equals("page") && (c == '+' || c == '-')) {
    int n = @PKG@.InvPage.toInt(arg, 0);
    if (n > 0) { this.vvPage = n; this.vvPwFree = false; }
  }
  redraw();
}""")
M(mtab, r"""
public boolean vvLive() {
  return this.vvOk && this.vvTok != null && !"-".equals(this.vvTok);
}""")
# a vault slot click = take the whole shown stack (page, slot, quantity, id exactly as drawn)
M(mtab, r"""
public void vvTake(int i) {
  if (!vvLive() || this.vvShown < 1 || this.vvShown > this.vvOwn) { say(@PKG@.MarketTabData.VVNONE); return; }
  if (i < 0 || i >= this.vvSid.length) { say("Nothing there - nothing changed"); return; }
  String id = this.vvSid[i];
  if (id == null) { say(this.vvArr[i] ? "That slot holds the page arrow - nothing to take" : "That vault slot is empty - nothing to take"); return; }
  vvAct("take", this.vvShown + ":" + (i + 1) + ":" + this.vvSq[i] + ":" + id);
}""")
# an inventory slot click = put the whole shown stack onto the shown (owned) page
M(mtab, r"""
public void vvPut(int k, int i) {
  if (!vvLive() || this.vvShown < 1 || this.vvShown > this.vvOwn) { say(@PKG@.MarketTabData.VVNONE); return; }
  int im = @PKG@.MarketTabData.VVIM;
  if (k < 0 || k > 2 || i < 0 || i >= im || k * im + i >= this.vvIid.length) { say("Nothing there - nothing changed"); return; }
  String id = this.vvIid[k * im + i];
  if (id == null) { say("That inventory slot is empty - nothing to put"); return; }
  vvAct("put", k + ":" + (i + 1) + ":" + this.vvIq[k * im + i] + ":" + this.vvShown + ":" + id);
}""")
M(mtab, r"""
public void vvPick(int n) {
  if (!vvLive()) { say(@PKG@.MarketTabData.VVNONE); return; }
  boolean drawn = false;
  for (int k = 0; k < this.vvPgN.length; k++) if (n > 0 && this.vvPgN[k] == n) drawn = true;
  if (!drawn) { say(@PKG@.MarketTabData.VVNONE); return; }
  vvAct("page", String.valueOf(n));
}""")
# Buy (one press) / Buy then Confirm (confirm 1: Buy only arms the separate Confirm button for 10 s, nothing is sent; any drawing drops the arm)
M(mtab, r"""
public void vvBuy(boolean conf) {
  if (!vvLive() || !"buy".equals(this.vvBst) || this.vvBpg < 1 || this.vvBpr < 0L) { this.vvArm = 0L; say(@PKG@.MarketTabData.VVNONE); return; }
  String arg = this.vvBpg + ":" + this.vvBpr;
  if (!this.vvBconf) {
    if (conf) { say(@PKG@.MarketTabData.VVNONE); return; }
    vvAct("buy", arg);
    return;
  }
  long now = System.currentTimeMillis();
  if (!conf) {
    this.vvArm = now + 10000L;
    @UCB@ ub = new @UCB@();
    this.tcap = "Buy page " + this.vvBpg + " for " + money(this.vvBpr) + " coins? Press Confirm within 10 s to pay - nothing was charged yet.";
    ub.set("#SkyyMtabCap.Text", this.tcap);
    ub.set("#SkyyMtabVvBc.Visible", true);
    ub.set("#SkyyMtabVvBc.Text", "Confirm - " + money(this.vvBpr) + " coins");
    this.answered = true;
    this.answers = this.answers + 1;
    this.sendUpdate(ub);
    return;
  }
  if (this.vvArm == 0L) { say("Press Buy first - nothing was charged"); return; }
  if (now > this.vvArm) { this.vvArm = 0L; this.tcap = "That Confirm ran out - press Buy again. Nothing was charged."; redraw(); return; }
  this.vvArm = 0L;
  vvAct("buy", arg + ":1");
}""")
M(mtab, r"""
public void vvOpen() {
  if (!vvLive() || this.vvShown < 1 || this.vvShown > this.vvOwn) { say(@PKG@.MarketTabData.VVNONE); return; }
  vvAct("open", String.valueOf(this.vvShown));
}""")
'''
P.rep('''# ---- 0.3.72 (oldmenu4): the views' actions. Every one answers with ONE packet (a redraw with the answer in the caption, or a caption).
M(mtab, r"""
public static int viewOf(String a) {
  if (a.startsWith("kv")) return 4;                           // 0.3.76: the Bank view''', VV_ACT + '''# ---- 0.3.72 (oldmenu4): the views' actions. Every one answers with ONE packet (a redraw with the answer in the caption, or a caption).
M(mtab, r"""
public static int viewOf(String a) {
  if (a.startsWith("vv")) return 5;                           // 0.3.80: the Vault view
  if (a.startsWith("kv")) return 4;                           // 0.3.76: the Bank view''')
P.rep('''  this.view = v < 0 || v > 4 ? 0 : v;   // 0.3.73: + 3 the Auction House; 0.3.76: + 4 the Bank
  this.kvAk = -1;                        // 0.3.76: a fresh view, no old answer line
  this.kvAns = "";
''', '''  this.view = v < 0 || v > 5 ? 0 : v;   // 0.3.73: + 3 the Auction House; 0.3.76: + 4 the Bank; 0.3.80: + 5 the Vault
  this.kvAk = -1;                        // 0.3.76: a fresh view, no old answer line
  this.kvAns = "";
  this.vvAk = -1;                        // 0.3.80: the Vault view opens on the page /vault opens on (the bridge picks), no old answer / arm
  this.vvAns = "";
  this.vvPage = 0;
  this.vvPwFree = false;
  this.vvArm = 0L;
''')
P.rep('''    if (a.equals("kvamt")) {
      if (!this.kvMove) { say(@PKG@.MarketTabData.KVNONE); return; }
      this.kvTyped = amtClean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "B"));
      kvAct("amount", this.kvTyped);
      return;
    }
''', '''    if (a.equals("kvamt")) {
      if (!this.kvMove) { say(@PKG@.MarketTabData.KVNONE); return; }
      this.kvTyped = amtClean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "B"));
      kvAct("amount", this.kvTyped);
      return;
    }
    // 0.3.80 (vaultview): the Vault view's Refresh (vault:fn:act refresh, then the view is read again) and the page row's < > (no call, a redraw)
    if (a.equals("vvrf")) {
      if (@PKG@.InvCraft.fn("vault:fn:act") == null || @PKG@.InvCraft.fn("vault:fn:view") == null) { this.tcap = ""; redraw(); return; }
      vvAct("refresh", "");
      return;
    }
    if (a.startsWith("vvpw:")) {
      int dw = @PKG@.InvPage.toInt(a.substring(5), 0);
      int st = @PKG@.MarketTabData.VVPN;
      int np = dw < 0 ? this.vvPw - st : this.vvPw + st;
      if (this.vvMax < 1 || np < 1 || np > this.vvMax) { say(np < 1 ? "These are the first pages" : "These are the last pages"); return; }
      this.vvPw = np;
      this.vvPwFree = true;
      this.tcap = "";
      redraw();
      return;
    }
''')
P.rep('''      kvAct(a.equals("kvda") ? "depall" : (a.equals("kvwa") ? "wdall" : (a.equals("kvd") ? "deposit" : (a.equals("kvw") ? "withdraw" : "upgrade"))), typed ? ky : "");
      return;
    }
''', '''      kvAct(a.equals("kvda") ? "depall" : (a.equals("kvwa") ? "wdall" : (a.equals("kvd") ? "deposit" : (a.equals("kvw") ? "withdraw" : "upgrade"))), typed ? ky : "");
      return;
    }
    // 0.3.80 (vaultview): the Vault view's token actions - only what the drawing showed; the view's token + profile key + the shown values ride along
    if (a.equals("vvs")) { vvTake(@PKG@.InvPage.ival(d, "SlotIndex", -1)); return; }
    if (a.startsWith("vvi:")) { vvPut(@PKG@.InvPage.toInt(a.substring(4), -1), @PKG@.InvPage.ival(d, "SlotIndex", -1)); return; }
    if (a.startsWith("vvp:")) { vvPick(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("vvb") || a.equals("vvbc")) { vvBuy(a.equals("vvbc")); return; }
    if (a.equals("vvo")) { vvOpen(); return; }
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.80: no system / command / class"
_i = P.s.index
assert _i("public static void hold(@UCB@ b, String base, int n, int which, String text)") < _i("public void vvShow(@UCB@ b, String head, int mode)") \
    < _i("public static @IGS@ vvCell(") < _i("public void fillVv(@UCB@ b, @UEB@ ev)") \
    < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.pref = ref;\n  this.pst = st;\n  String lk = @PKG@.MarketTabData.LK;") \
    < _i("public void vvAct(String op, String arg)") < _i("public void vvTake(int i)") < _i("public void vvBuy(boolean conf)") \
    < _i("public static int viewOf(String a) {\n  if (a.startsWith(\"vv\")) return 5;") < _i('    if (a.equals("vvrf")) {') < _i('    if (a.equals("vvs")) {'), \
    "0.3.80: the vault view methods before their callers"
assert _i("public void redraw() {\n  this.answered = true;\n  if (!still()) { finish(\"replaced\"); return; }") < _i("public void vvAct(String op, String arg)"), "0.3.80: redraw before vvAct"
assert _i("public static java.util.ArrayList act(java.util.ArrayList l)") < _i("public void fillVv(@UCB@ b, @UEB@ ev)") \
    and _i("public static @IGS@ slot(@IS@ s)") < _i("public static @IGS@ vvCell("), "0.3.80: InvPage.act / slot before the vault view"
assert "/vault opens it" not in P.s[P.s.index("KV_TXT = {"):P.s.index("KV_RUNTIME_MAX = 1")], "0.3.80: the Bank view's hint points at the Vault sub-tab"
P.finish()

# ======================================================================= the HARNESS (every 0.3.79 check runs again on the 0.3.80 jar, plus VAULTVIEW)
HARNESS_STATIC = r'''    # ---- VAULTVIEW (0.3.80; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the Market screen's Vault view
    K.check('call("vault:fn:view", new Object[] { u, Integer.valueOf(this.vvPage) });' in g
            and 'call("vault:fn:act", new Object[] { op, this.playerRef.getUuid(), this.vvTok, this.vvPk, arg == null ? "" : arg });' in g
            and 'this.vvTok = live ? h[2] : "-";' in g and "this.vvPk = h[3];" in g and "ScheduledFuture vv" not in g and g.count('"vault:fn:view"') >= 3,
            "VAULTVIEW STATIC the view reads vault:fn:view {UUID, the page} and acts through vault:fn:act with the read's token (h field 3) + profile key (h field 4); no timer")
    K.check('MT_SUBS = ["Market", "Bazaar orders", "Merchants", "Auction House", "Bank", "Vault"]' in g and "MT_VBW = 116" in g
            and '"kvvault": "Items are kept in your Vault - the Vault sub-tab above shows them.' in g,
            "VAULTVIEW STATIC the sixth sub-tab is Vault (MT_VBW 140 -> 116); the Bank view's hint points at it (no '/vault opens it')")
    K.check(all(("0.3.80: %s" % t_) in g for t_ in ("the grid holds a whole page", "the side column fits beside the grid", "the vault card fits",
                                                      "the inventory card fits", "the vault view fits 1080", "a vault button fits", "a page button fits",
                                                      "a vault head line fits", "a caption fits the hint row", "the page button markup is proven",
                                                      "the vault view's packet stays well under")),
            "VAULTVIEW STATIC the build asserts the Vault view fits 1080 (a whole 90-slot page in one grid), its buttons / lines fit, its element budget")
    K.check('MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUKV")' in g and '"V": VV_RUNTIME_MAX}' in g,
            "VAULTVIEW STATIC the market screen's budget = the frame + its biggest section (+ V, the Vault view)")
    K.check(g.count(' = mk("') == o.count(' = mk("') and g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("),
            "VAULTVIEW STATIC no new class / command / system")
    K.check("a stopgap until the Inventory tab's Vault pocket tab exists" in g and "12-tab" not in g[:g.index("0.3.79:")],
            "VAULTVIEW STATIC (fixer) the build notes say Market > Vault is a stopgap until the Inventory pocket tab (ui.md 2026-11-14), not the old 12-tab plan")
'''

HARNESS_VV = r'''    # ---- VAULTVIEW (0.3.80, round vaultview): THE MARKET TAB'S VAULT VIEW (vault:fn:view / vault:fn:act stand-ins = tools/vault_0_1_11_patch.py's contract)
    def only80(p_):   # the frame + ONE section: the Vault view, no home cards, no other view
        return (p_ is not None and has4(p_, "SkyyMtabVv") and not has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabOv") and not has4(p_, "SkyyMtabMv")
                and not has4(p_, "SkyyMtabHv") and not has4(p_, "SkyyMtabKv") and not sel_ok4(p_))

    def slots80(p_, grid_):   # the grid's ItemGridSlot JSON list in that packet (None = not set)
        v_ = cmap(p_).get("#SkyyMtab%s.Slots" % grid_) if p_ is not None else None
        if v_ is None:
            return None
        j_ = json.loads(v_)
        return j_.get("0") if isinstance(j_, dict) else j_

    def item80(s_):   # (id, qty) of a slot, None = empty
        it_ = s_.get("ItemStack") if isinstance(s_, dict) else None
        if not it_:
            return None
        return (str(it_.get("ItemId", it_.get("Id"))), int(it_.get("Quantity", 1)))
    VOLD = "=That click was for an older copy of your vault - nothing moved. The view is up to date now; click again if you meant it."
    VPROF = "=Your profile changed after this view opened - nothing moved. The view is up to date now."
    VCHG = "=Your vault changed since you looked - nothing moved. The view is up to date now."
    VINV = "=Your inventory changed since you looked - nothing moved. The view is up to date now."
    VT = {"tok": 0, "cur": None, "pk": "prof-A", "epoch": 1, "own": 3, "max": 5, "cap": 36, "inside": False, "off": None, "vnull": False, "anull": False,
          "price": {4: 75000, 5: 250000}, "pricex": 0, "confirm": 100000, "need": 0, "best": 2, "views": [], "acts": [], "last": 1, "opened": [], "full": False,
          "icap": [9, 36, 9], "replace": False}
    VT["vault"] = {(1, 1): ["Rock_Stone", 64, 4, "0.0", "0.0", 0], (1, 5): ["Weapon_Sword_Iron", 1, 3, "120.0", "200.0", 1],
                   (1, 9): ["Wood_Oak_Trunk", 20, 0, "0.0", "0.0", 0], (2, 1): ["Plant_Fruit_Apple", 30, 0, "0.0", "0.0", 0]}
    VT["inv"] = {0: {1: ["Plant_Fruit_Apple", 3, 0, "0.0", "0.0", 0]}, 1: {4: ["Rock_Stone", 10, 0, "0.0", "0.0", 0]}, 2: {}}

    def v_ar(cap_):   # the in-chest arrow slots of arrowLayout=inside (1-based), else none
        if not VT["inside"]:
            return []
        lo_ = ((cap_ - 1) // 9) * 9
        return [lo_ + 1, cap_]

    def v_price(pg_):
        return VT["price"].get(pg_, 50000) + VT["pricex"]

    def f_vview(o):
        a_ = list(o) if o is not None and hasattr(o, "__len__") and not isinstance(o, str) else [o]
        pg_ = int(str(a_[1])) if len(a_) > 1 and a_[1] is not None else 0
        VT["views"].append((str(a_[0]), pg_))
        if VT["vnull"]:
            return None
        if VT["off"]:
            VT["cur"] = None
            return "off|" + VT["off"]
        own_, cap_ = VT["own"], VT["cap"]
        mx_ = max(own_, VT["max"])
        if pg_ < 1 or pg_ > mx_:
            pg_ = VT["last"]
        VT["tok"] += 1
        tok_ = "v%d" % VT["tok"]
        VT["cur"] = (tok_, VT["pk"], pg_, VT["epoch"])
        ar_ = v_ar(cap_)
        per_ = cap_ - len(ar_)
        L = ["h|ok|%s|%s|%d|%d|%d|%d|%d|%d|1|0|0|0" % (tok_, VT["pk"], pg_, own_, mx_, per_, cap_, len(VT["vault"]))]
        nx_ = own_ + 1
        if nx_ > VT["max"]:
            L.append("b|max|0|0|0|0|-1|All pages bought")
        else:
            c_ = v_price(nx_)
            cf_ = 1 if c_ >= VT["confirm"] else 0
            if VT["need"]:
                L.append("b|bank|%d|%d|%d|%d|%d|Page %d needs Bank Lv %d" % (nx_, c_, cf_, VT["need"], VT["best"], nx_, VT["need"]))
            else:
                L.append("b|buy|%d|%d|%d|0|%d|Buy page %d - %dk coins" % (nx_, c_, cf_, VT["best"], nx_, c_ // 1000))
        for q_ in range(1, mx_ + 1):
            st_ = "own" if q_ <= own_ else ("next" if q_ == nx_ else "locked")
            L.append("p|%d|%s|%d|%d" % (q_, st_, len([1 for (p2_, s2_) in VT["vault"] if p2_ == q_]) if q_ <= own_ else 0, per_))
        if pg_ <= own_:
            L.append("t|Page %d of %d - %d of %d slots used - shared by all your profiles" % (pg_, own_, len([1 for (p2_, s2_) in VT["vault"] if p2_ == pg_]), per_))
        else:
            L.append("t|Page %d is locked - it costs %s coins" % (pg_, "{:,}".format(v_price(pg_))))
        for r_ in ar_:
            L.append("r|%d" % r_)
        if pg_ <= own_:
            for (p2_, s2_), v_ in sorted(VT["vault"].items()):
                if p2_ == pg_:
                    L.append("s|%d|%s|%d|%d|%s|%s|%d" % (s2_, v_[0], v_[1], v_[2], v_[3], v_[4], v_[5]))
        for k_ in range(3):
            if VT["icap"][k_] is None:
                continue
            L.append("c|%d|%d" % (k_, VT["icap"][k_]))
            for s2_, v_ in sorted(VT["inv"][k_].items()):
                L.append("i|%d|%d|%s|%d|%d|%s|%s|%d" % (k_, s2_, v_[0], v_[1], v_[2], v_[3], v_[4], v_[5]))
        return "\n".join(L)

    def v_free(pg_):
        ar_ = v_ar(VT["cap"])
        for s_ in range(1, VT["cap"] + 1):
            if s_ not in ar_ and (pg_, s_) not in VT["vault"]:
                return s_
        return 0

    def f_vact(o):
        a = [None if x_ is None else str(x_) for x_ in list(o)]
        VT["acts"].append(a)
        if VT["anull"]:
            return None
        op_, tok_, pk_, arg_ = a[0], a[2], a[3], a[4] or ""
        if op_ not in ("take", "put", "move", "buy", "page", "open", "refresh"):
            return "-Unknown vault action - nothing moved."
        if op_ == "refresh":
            return ""
        rec_ = VT["cur"]
        if rec_ is None or tok_ != rec_[0]:
            return VOLD
        if pk_ != rec_[1] or VT["pk"] != rec_[1] or VT["epoch"] != rec_[3]:
            return VPROF
        own_, shown_ = VT["own"], rec_[2]
        f_ = arg_.split(":")
        if op_ == "take":
            if len(f_) not in (4, 5):
                return "-Bad request - nothing moved."
            pg_, sl_, q_ = int(f_[0]), int(f_[1]), int(f_[2])
            if pg_ > own_:
                return "-Vault page %d is not yours - nothing moved." % pg_
            cur_ = VT["vault"].get((pg_, sl_))
            if not cur_ or cur_[0] != f_[-1] or cur_[1] != q_:
                return VCHG
        elif op_ == "put":
            if len(f_) not in (5, 6):
                return "-Bad request - nothing moved."
            si_, sl_, q_, tp_ = int(f_[0]), int(f_[1]), int(f_[2]), int(f_[3])
            tp_ = shown_ if tp_ == 0 else tp_
            if tp_ < 1 or tp_ > own_:
                return "-Vault page %d is not yours - nothing moved." % tp_
            cur_ = VT["inv"][si_].get(sl_)
            if not cur_ or cur_[0] != f_[-1] or cur_[1] != q_:
                return VINV
        elif op_ == "buy":
            if len(f_) not in (2, 3):
                return "-Bad request - nothing moved."
            pg_, pr_ = int(f_[0]), int(f_[1])
            ok_ = len(f_) == 3 and f_[2] == "1"
            if pg_ <= own_:
                return "=Vault page %d is already yours - nothing was charged. The view is up to date now." % pg_
            if pg_ != own_ + 1:
                return VCHG
            if v_price(pg_) != pr_:
                return "=The price of vault page %d changed to %s coins since you looked - nothing was charged. The view is up to date now." % (pg_, "{:,}".format(v_price(pg_)))
            if v_price(pg_) >= VT["confirm"] and not ok_:
                return "-Buy page %d for %s coins? Confirm it first - nothing was charged." % (pg_, "{:,}".format(v_price(pg_)))
        elif op_ in ("page", "open"):
            if not arg_.isdigit() or int(arg_) < 1:
                return "-Bad request - nothing moved."
        VT["cur"] = None   # the token is used up
        if op_ == "take":
            if VT["full"]:
                return "-Your inventory is full - nothing moved."
            if VT.get("room"):   # room for fewer than the stack: the rest stays in the same slot (vault 0.1.11 take)
                m_ = VT["room"]
                VT["vault"][(pg_, sl_)] = [cur_[0], q_ - m_] + list(cur_[2:])
                return "+Took %d %s from vault page %d - your inventory is full, %d stayed in the vault." % (m_, cur_[0], pg_, q_ - m_)
            v_ = VT["vault"].pop((pg_, sl_))
            fs_ = [s_ for s_ in range(1, VT["icap"][1] + 1) if s_ not in VT["inv"][1]]
            VT["inv"][1][fs_[0]] = v_
            return "+Took %d %s from vault page %d slot %d." % (q_, v_[0], pg_, sl_)
        if op_ == "put":
            ts_ = v_free(tp_)
            if not ts_:
                return "-Vault page %d is full - nothing moved. Pick another page." % tp_
            VT["vault"][(tp_, ts_)] = VT["inv"][si_].pop(sl_)
            return "+Put %d %s into vault page %d slot %d." % (q_, f_[-1], tp_, ts_)
        if op_ == "buy":
            VT["own"] += 1
            return "+Vault page %d is yours - %s coins paid." % (pg_, "{:,}".format(pr_))
        n_ = int(arg_)
        if n_ > own_:
            return "-Page %d is locked - it costs %s coins." % (n_, "{:,}".format(v_price(n_)))
        if op_ == "page":
            VT["last"] = n_
            return "+Showing vault page %d of %d." % (n_, own_)
        VT["opened"].append(n_)
        if VT["replace"]:
            PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
        return "+Vault page %d opened." % n_

    def vv_ev(obj, what, n=1):   # one press; the Vault view's reads + acts during it
        v0_, a0_ = len(VT["views"]), len(VT["acts"])
        p_ = mt_ev(obj, what, n)
        return p_, len(VT["views"]) - v0_, len(VT["acts"]) - a0_
    for k_ in ("vault:fn:view", "vault:fn:act", "vault:fn:findLL", "vault:fn:openBank"):
        BR.remove(k_)
    MS = PK.pm.getCustomPage()
    # ---- FALL: no SkyyVault / an older one (vault:fn:findLL only)
    p_ = mt_ev({"a": "vw:5"}, "VAULTVIEW FALL the Vault sub-tab without SkyyVault")
    cm = cmap(p_)
    K.check(int(MS.view) == 5 and only80(p_) and txt4(cm, "VvH") == str(MTD.VVOFF) and not vis8(cm, "Vvb") and not vis8(cm, "VvK") and cap3(p_) == str(MTD.VVCAP)
            and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabVvT5") and len(bind4(p_, "vw:5")) == 1 and len(bind4(p_, "vw:4")) == 1,
            "VAULTVIEW FALL no SkyyVault = the Vault view says 'not on this server' (ONE section, the Vault sub-tab selected, no old page) %s" % sel_ok4(p_)[:3])
    BR.put("vault:fn:findLL", Fn(lambda o: None))
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW FALL SkyyVault 0.1.10")
    K.check(txt4(cmap(p_), "VvH") == str(MTD.VVOLD) and "0.1.11" in str(MTD.VVOLD) and only80(p_), "VAULTVIEW FALL SkyyVault older than 0.1.11 = the head names 0.1.11 (%s)" % txt4(cmap(p_), "VvH"))
    for x_ in ({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, {"a": "vvi:1", "t": str(MS.tok), "SlotIndex": 4}, {"a": "vvb", "t": str(MS.tok)}, {"a": "vvo", "t": str(MS.tok)}):
        p_ = mt_ev(x_, "VAULTVIEW FALL a forged %s without the bridge" % x_["a"])
        K.check(cap3(p_) == str(MTD.VVNONE) and not VT["acts"], "VAULTVIEW FALL a forged %s the drawing did not show = a caption, no call" % x_["a"])
    BR.put("vault:fn:view", Fn(f_vview))
    BR.put("vault:fn:act", Fn(f_vact))
    # ---- PAGE: Refresh = vault:fn:act refresh, then ONE read {UUID, page 0 = the page /vault opens on}
    p_, nv_, na_ = vv_ev({"a": "vvrf"}, "VAULTVIEW Refresh with SkyyVault 0.1.11")
    cm = cmap(p_)
    K.notes.append("VAULTVIEW the Vault view's packet: %d commands, %d elements appended" % (len(cmds_of(p_)), ecount8(p_)))
    K.check(VT["acts"][-1] == ["refresh", uk3, "-", "-", ""] and nv_ == 1 and VT["views"][-1] == (uk3, 0) and only80(p_) and ecount8(p_) < 800,
            "VAULTVIEW Refresh = vault:fn:act refresh {UUID, the old token '-', ''}, then ONE vault:fn:view read {UUID, 0}; the frame + ONE section, under the element budget (%s, %d reads, %d elements)"
            % (VT["acts"][-1:], nv_, ecount8(p_)))
    tk_ = VT["cur"][0]
    ap_ = appended4(p_, "SkyyMtabVvPs")
    K.check(vis8(cm, "Vvb") and not vis8(cm, "VvK") and txt4(cm, "VvH") == "" and len(ap_) == 5 and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabVp0")
            and str(MTD.ST_CATSEL) not in mk_of(p_, "SkyyMtabVp1") and [txt4(cm, "Vp%d" % k_) for k_ in range(5)] == ["1  3/36", "2  1/36", "3  0/36", "4  Buy", "5  Locked"]
            and all(len(bind4(p_, "vvp:%d" % k_)) == 1 and '"t"' in bind4(p_, "vvp:%d" % k_)[0][2] for k_ in range(1, 6)) and txt4(cm, "VvPi") == "1-5 of 5"
            and not vis8(cm, "VvPp") and not vis8(cm, "VvPn"),
            "VAULTVIEW PAGE the page row: 5 buttons (own 'n  used/usable', next 'n  Buy', locked 'n  Locked'), the shown page selected, each with the page token; no < > (%s)"
            % [txt4(cm, "Vp%d" % k_) for k_ in range(5)])
    g_ = slots80(p_, "VvG")
    K.notes.append("VAULTVIEW grid slot 0 JSON: %s" % (json.dumps(g_[0])[:400] if g_ else g_))
    K.check(g_ is not None and len(g_) == 36 and item80(g_[0]) == ("Rock_Stone", 64) and item80(g_[4]) == ("Weapon_Sword_Iron", 1) and item80(g_[8]) == ("Wood_Oak_Trunk", 20)
            and item80(g_[1]) is None and all(isinstance(s_, dict) and s_.get("IsActivatable") is True for s_ in g_) and vis8(cm, "VvG")
            and txt4(cm, "VvT") == "Page 1 of 3 - 3 of 36 slots used - shared by all your profiles",
            "VAULTVIEW PAGE the grid = the shown page's 36 slots, icons + counts in their slots, empty slots empty, every slot activatable; the t line above it")
    gd_ = json.dumps(g_)
    K.check(tint_("#8b339e") in json.dumps(g_[0]) and '<color is=\\"#8b339e\\">' in json.dumps(g_[0]) and tint_("#55ffff") in json.dumps(g_[4])
            and '"Background"' not in json.dumps(g_[8]) and "etadata" not in gd_ and "QualityOverride" not in gd_ and "qualityIndex" not in gd_
            and "Vault page 1, slot 1" in json.dumps(g_[0]) and "Click: take all 64 into your inventory" in json.dumps(g_[0]),
            "VAULTVIEW PAGE RARITY the quality index = the rarity tint on the slot + the name in its colour (Epic, legendary-stamped sword), the item's own quality = no override; no metadata / quality override; the tooltip says where + the click footer")
    K.check(len(bind4(p_, "vvs")) == 1 and bind4(p_, "vvs")[0][0] == "SlotClicking" and '"t"' in bind4(p_, "vvs")[0][2]
            and all(len(bind4(p_, "vvi:%d" % k_)) == 1 and bind4(p_, "vvi:%d" % k_)[0][0] == "SlotClicking" for k_ in range(3)),
            "VAULTVIEW PAGE a vault slot click (vvs) + each inventory section click (vvi:0..2) carry the page token")
    i0_, i1_, i2_ = slots80(p_, "VvI0"), slots80(p_, "VvI1"), slots80(p_, "VvI2")
    K.check(i0_ is not None and len(i0_) == 9 and len(i1_) == 36 and len(i2_) == 9 and item80(i0_[0]) == ("Plant_Fruit_Apple", 3) and item80(i1_[3]) == ("Rock_Stone", 10)
            and vis8(cm, "VvI2") and txt4(cm, "VvRh") == "Click an item to put it on vault page 1." and txt4(cm, "VvOv") == "",
            "VAULTVIEW PAGE YOUR INVENTORY = the c| / i| lines: hotbar 9, storage 36, backpack 9 cells, the items in their slots")
    K.check(txt4(cm, "VvBl") == "Buy page 4 - 75k coins" and txt4(cm, "VvBl2") == "Costs 75,000 coins - one press" and vis8(cm, "VvBr") and not vis8(cm, "VvBc")
            and txt4(cm, "VvBy") == "Buy page 4" and len(bind4(p_, "vvb")) == 1 and not bind4(p_, "vvbc") and vis8(cm, "VvOr")
            and txt4(cm, "VvO") == "Open page 1 in the chest window" and len(bind4(p_, "vvo")) == 1 and len(bind4(p_, "vvrf")) == 1 and not bind4(p_, "vvrf")[0][2].count('"t"'),
            "VAULTVIEW PAGE NEXT PAGE (the b| text, price, one press below buyConfirmCoins) + Open + Refresh (navigation, no token)")
    K.check(cap3(p_) == str(MTD.VVCAP) and not vis8(cm, "VvA0") and not vis8(cm, "VvA1") and not vis8(cm, "VvA2"), "VAULTVIEW PAGE the caption; no answer line yet")
    # ---- TAKE: a vault slot click = take <page>:<slot>:<qty>:<id> with the view's token + profile key; ONE new read
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW TAKE the Epic stone stack")
    cm = cmap(p_)
    K.check(VT["acts"][-1] == ["take", uk3, tk_, "prof-A", "1:1:64:Rock_Stone"] and na_ == 1 and nv_ == 1 and (1, 1) not in VT["vault"]
            and cap3(p_) == "Took 64 Rock_Stone from vault page 1 slot 1." and vis8(cm, "VvA0") and not vis8(cm, "VvA1") and item80(slots80(p_, "VvG")[0]) is None
            and only80(p_), "VAULTVIEW TAKE = vault:fn:act take {UUID, the view's token, its profile key, '1:1:64:Rock_Stone'}; '+' = the caption + a green answer line; read again (%s)" % VT["acts"][-1:])
    told_ = str(MS.tok)
    p_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 4}, "VAULTVIEW DOUBLE the first click of a double click")
    a0_ = len(VT["acts"])
    v0_ = len(VT["views"])
    p_ = mt_ev({"a": "vvs", "t": told_, "SlotIndex": 4}, "VAULTVIEW DOUBLE the second click (the same drawing)")
    K.check(len(VT["acts"]) == a0_ and VT["acts"][-1][4] == "1:5:1:Weapon_Sword_Iron" and "The page changed" in cap3(p_) and len(VT["views"]) == v0_ + 1
            and (1, 5) not in VT["vault"] and len([x_ for x_ in VT["acts"] if x_[0] == "take" and x_[4] == "1:5:1:Weapon_Sword_Iron"]) == 1,
            "VAULTVIEW DOUBLE a double click on a vault item = ONE take (the second click is from an older drawing: 'The page changed', no call, drawn again)")
    # ---- PUT: an inventory slot click = put <section>:<slot>:<qty>:<shown page>:<id>
    tk_ = VT["cur"][0]
    p_, nv_, na_ = vv_ev({"a": "vvi:0", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW PUT the hotbar apples")
    K.check(VT["acts"][-1] == ["put", uk3, tk_, "prof-A", "0:1:3:1:Plant_Fruit_Apple"] and nv_ == 1 and 1 not in VT["inv"][0] and VT["vault"].get((1, 1), [None])[0] == "Plant_Fruit_Apple"
            and cap3(p_).startswith("Put 3 Plant_Fruit_Apple into vault page 1"), "VAULTVIEW PUT = vault:fn:act put {.., '0:1:3:1:Plant_Fruit_Apple'} (the shown page, explicit); '+'; read again (%s)" % VT["acts"][-1:])
    p_ = mt_ev({"a": "vvi:1", "t": str(MS.tok), "SlotIndex": 20}, "VAULTVIEW PUT an empty inventory slot")
    p2_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 30}, "VAULTVIEW TAKE an empty vault slot")
    p3_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 99}, "VAULTVIEW TAKE a slot outside the grid")
    K.check(cap3(p_) == "That inventory slot is empty - nothing to put" and cap3(p2_) == "That vault slot is empty - nothing to take" and cap3(p3_).startswith("Nothing there")
            and VT["acts"][-1][0] == "put", "VAULTVIEW SAFE an empty / outside slot = a caption, no call")
    # a full page: '-' = red, nothing moved
    keep_ = dict(VT["vault"])
    for s_ in range(1, 37):
        VT["vault"].setdefault((1, s_), ["Rock_Stone", 1, 0, "0.0", "0.0", 0])
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW FULL redraw with page 1 full")
    p_, nv_, na_ = vv_ev({"a": "vvi:1", "t": str(MS.tok), "SlotIndex": 3}, "VAULTVIEW FULL put onto a full page")
    cm = cmap(p_)
    K.check(VT["acts"][-1][0] == "put" and cap3(p_) == "Vault page 1 is full - nothing moved. Pick another page." and vis8(cm, "VvA1") and not vis8(cm, "VvA0")
            and VT["inv"][1].get(4) is not None and nv_ == 1, "VAULTVIEW FULL Put onto a full page = the bridge's '-' line red in the caption + the answer line, nothing moved, read again")
    VT["vault"] = keep_
    VT["full"] = True
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW FULL take into a full inventory")
    K.check(cap3(p_) == "Your inventory is full - nothing moved." and vis8(cmap(p_), "VvA1") and (1, 1) in VT["vault"] and nv_ == 1, "VAULTVIEW FULL take into a full inventory = '-' red, nothing moved")
    VT["full"] = False
    VT["room"] = 20   # (fixer) a partial take: room for 20 of the shown stack - '+' green with the 'stayed' line, read again, the rest drawn
    old11_ = VT["vault"].get((1, 1))
    VT["vault"][(1, 1)] = ["Rock_Stone", 64, 4, "0.0", "0.0", 0]
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW FULL redraw before the partial take")
    q0_ = 64
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW FULL partial take")
    cm = cmap(p_)
    K.check(VT["acts"][-1][4] == "1:1:%d:%s" % (q0_, VT["vault"][(1, 1)][0]) and VT["vault"][(1, 1)][1] == q0_ - 20
            and cap3(p_).endswith("your inventory is full, %d stayed in the vault." % (q0_ - 20)) and vis8(cm, "VvA0") and not vis8(cm, "VvA1")
            and item80(slots80(p_, "VvG")[0]) == (VT["vault"][(1, 1)][0], q0_ - 20) and nv_ == 1 and na_ == 1,
            "VAULTVIEW FULL a partial take (inventory room for 20) = the bridge's '+ ... stayed' line green, ONE read, the slot redrawn with the rest")
    VT["room"] = 0
    if old11_ is None:
        VT["vault"].pop((1, 1), None)
    else:
        VT["vault"][(1, 1)] = old11_
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW FULL redraw after the partial take")
    # ---- STALE: '=' answers (a dead token, the vault / inventory changed, a profile switch) then the same press again after the redraw runs
    VT["tok"] += 10
    VT["cur"] = ("v%d" % VT["tok"],) + tuple(VT["cur"][1:])   # /vault (or another screen) read the view meanwhile: our token is dead
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW STALE take with a dead token")
    cm = cmap(p_)
    K.check(cap3(p_) == VOLD[1:] and vis8(cm, "VvA2") and not vis8(cm, "VvA0") and (1, 1) in VT["vault"] and nv_ == 1 and na_ == 1,
            "VAULTVIEW STALE a dead click token = the bridge's '=' older-copy line (plain), nothing moved, the view read again (a new token)")
    tk_ = VT["cur"][0]
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW STALE the same press again")
    K.check(VT["acts"][-1][2] == tk_ and (1, 1) not in VT["vault"] and cap3(p_).startswith("Took 3 Plant_Fruit_Apple"), "VAULTVIEW STALE the press again carries the new token and runs")
    VT["inv"][1][4][1] = 11   # the stack changed after the view (a pickup)
    p_, nv_, na_ = vv_ev({"a": "vvi:1", "t": str(MS.tok), "SlotIndex": 3}, "VAULTVIEW STALE put of a stack that changed")
    K.check(VT["acts"][-1][4] == "1:4:10:1:Rock_Stone" and cap3(p_) == VINV[1:] and VT["inv"][1].get(4) is not None and nv_ == 1,
            "VAULTVIEW STALE put sends the SHOWN quantity (10); the stack is 11 now = '=Your inventory changed', nothing moved")
    p_, nv_, na_ = vv_ev({"a": "vvi:1", "t": str(MS.tok), "SlotIndex": 3}, "VAULTVIEW STALE put again after the redraw")
    K.check(VT["acts"][-1][4] == "1:4:11:1:Rock_Stone" and 4 not in VT["inv"][1] and cap3(p_).startswith("Put 11 Rock_Stone"), "VAULTVIEW STALE the press again sends the new quantity and runs")
    VT["vault"][(1, 9)][1] = 25   # the vault changed (the chest window) after the view
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 8}, "VAULTVIEW STALE take of a vault stack that changed")
    K.check(VT["acts"][-1][4] == "1:9:20:Wood_Oak_Trunk" and cap3(p_) == VCHG[1:] and VT["vault"][(1, 9)][1] == 25, "VAULTVIEW STALE '=Your vault changed', nothing moved")
    VT["pk"], VT["epoch"] = "prof-B", 2
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 8}, "VAULTVIEW STALE a profile switch")
    K.check(VT["acts"][-1][3] == "prof-A" and cap3(p_) == VPROF[1:] and nv_ == 1, "VAULTVIEW STALE a profile switch = the bridge refuses ('='), read again")
    p_, nv_, na_ = vv_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 8}, "VAULTVIEW STALE after the switch")
    K.check(VT["acts"][-1][3] == "prof-B" and cap3(p_).startswith("Took 25 Wood_Oak_Trunk"), "VAULTVIEW STALE after the redraw the new profile key is sent")
    a0_ = len(VT["acts"])
    v0_ = len(VT["views"])
    p_ = mt_ev({"a": "vvs", "t": "old", "SlotIndex": 4}, "VAULTVIEW SAFE an older drawing")
    K.check(len(VT["acts"]) == a0_ and "The page changed" in cap3(p_) and len(VT["views"]) == v0_ + 1, "VAULTVIEW SAFE a press from an older drawing = 'The page changed', no call, drawn again (ONE read)")
    # a null answer (not on the world thread): said, nothing read again, the token kept
    VT["anull"] = True
    v0_ = len(VT["views"])
    tk_ = str(MS.vvTok)
    p_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW a null answer")
    K.check(cap3(p_) == str(MTD.VVNULL) and len(VT["views"]) == v0_ and str(MS.vvTok) == tk_, "VAULTVIEW a null answer = 'That could not run here - nothing changed.' (nothing read, nothing used)")
    VT["anull"] = False
    # ---- PAGES: a page button = act page <n>, then the view of page n; a locked page = '-' + its locked line instead of the grid
    tk_ = VT["cur"][0]
    p_, nv_, na_ = vv_ev({"a": "vvp:2", "t": str(MS.tok)}, "VAULTVIEW PAGES page 2")
    cm = cmap(p_)
    K.check(VT["acts"][-1] == ["page", uk3, tk_, "prof-B", "2"] and VT["views"][-1] == (uk3, 2) and nv_ == 1 and item80(slots80(p_, "VvG")[0]) == ("Plant_Fruit_Apple", 30)
            and str(MTD.ST_CATSEL) in mk_of(p_, "SkyyMtabVp1") and txt4(cm, "VvO") == "Open page 2 in the chest window" and txt4(cm, "VvRh") == "Click an item to put it on vault page 2."
            and cap3(p_) == "Showing vault page 2 of 3.", "VAULTVIEW PAGES a page button = vault:fn:act page '2', then the view of page 2 (its grid, selected, Open / put name page 2)")
    p_, nv_, na_ = vv_ev({"a": "vvp:5", "t": str(MS.tok)}, "VAULTVIEW PAGES the locked page 5")
    cm = cmap(p_)
    K.check(VT["acts"][-1][0] == "page" and VT["acts"][-1][4] == "5" and VT["views"][-1] == (uk3, 5) and cap3(p_).startswith("Page 5 is locked") and vis8(cm, "VvA1")
            and not vis8(cm, "VvG") and txt4(cm, "VvT") == "Page 5 is locked - it costs 250,000 coins" and not vis8(cm, "VvOr") and not bind4(p_, "vvs") and not bind4(p_, "vvi:1")
            and txt4(cm, "VvRh") == "Show one of your own vault pages to put items in.", "VAULTVIEW PAGES a locked page = '-' red, the view of page 5: the locked line, no grid, no Open, no take / put")
    a0_ = len(VT["acts"])
    for x_ in ({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, {"a": "vvi:1", "t": str(MS.tok), "SlotIndex": 0}, {"a": "vvo", "t": str(MS.tok)}, {"a": "vvp:9", "t": str(MS.tok)}):
        p_ = mt_ev(x_, "VAULTVIEW SAFE forged %s on a locked page" % x_["a"])
        K.check(len(VT["acts"]) == a0_ and cap3(p_) == str(MTD.VVNONE), "VAULTVIEW SAFE a forged %s the drawing did not show = a caption, no call" % x_["a"])
    p_, nv_, na_ = vv_ev({"a": "vvp:1", "t": str(MS.tok)}, "VAULTVIEW PAGES back to page 1")
    # the page row's < >: 12 pages = 6 a row; > shows 7-12 (no call, ONE read), > again = said
    VT["max"] = 12
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW ROW 12 pages")
    cm = cmap(p_)
    K.check(len(appended4(p_, "SkyyMtabVvPs")) == 6 and vis8(cm, "VvPn") and not vis8(cm, "VvPp") and txt4(cm, "VvPi") == "1-6 of 12", "VAULTVIEW ROW 12 pages = 6 buttons + >")
    p_, nv_, na_ = vv_ev({"a": "vvpw:1"}, "VAULTVIEW ROW >")
    cm = cmap(p_)
    K.check(na_ == 0 and nv_ == 1 and [txt4(cm, "Vp%d" % k_) for k_ in range(6)] == ["7  Locked", "8  Locked", "9  Locked", "10  Locked", "11  Locked", "12  Locked"]
            and vis8(cm, "VvPp") and not vis8(cm, "VvPn") and txt4(cm, "VvPi") == "7-12 of 12" and item80(slots80(p_, "VvG")[8]) is None and vis8(cm, "VvG"),
            "VAULTVIEW ROW > = pages 7-12 (no call, ONE read; the shown page stays)")
    v0_ = len(VT["views"])
    p_ = mt_ev({"a": "vvpw:1"}, "VAULTVIEW ROW > at the end")
    K.check(cap3(p_) == "These are the last pages" and len(VT["views"]) == v0_, "VAULTVIEW ROW > at the end = said, nothing read")
    p_ = mt_ev({"a": "vvpw:-1"}, "VAULTVIEW ROW <")
    K.check(txt4(cmap(p_), "VvPi") == "1-6 of 12", "VAULTVIEW ROW < = pages 1-6 (%s / %s)" % (txt4(cmap(p_), "VvPi"), cap3(p_)))
    VT["max"] = 5
    # ---- BUY: below buyConfirmCoins = one press; at or above = Buy arms Confirm (no call), Confirm sends buy <page>:<price>:1
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW BUY redraw")
    tk_ = VT["cur"][0]
    p_, nv_, na_ = vv_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW BUY page 4 (75,000, one press)")
    cm = cmap(p_)
    K.check(VT["acts"][-1] == ["buy", uk3, tk_, "prof-B", "4:75000"] and VT["own"] == 4 and nv_ == 1 and cap3(p_).startswith("Vault page 4 is yours")
            and txt4(cm, "Vp3") == "4  0/36" and txt4(cm, "VvBl2") == "Costs 250,000 coins - Buy, then Confirm" and len(bind4(p_, "vvbc")) == 1 and not vis8(cm, "VvBc"),
            "VAULTVIEW BUY below buyConfirmCoins = ONE press: vault:fn:act buy '4:75000' (the shown page + price); the next page (250,000) asks twice")
    a0_ = len(VT["acts"])
    v0_ = len(VT["views"])
    p_ = mt_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW BUY page 5 first press")
    cm = cmap(p_)
    K.check(len(VT["acts"]) == a0_ and len(VT["views"]) == v0_ and cap3(p_).startswith("Buy page 5 for 250,000 coins? Press Confirm") and vis8(cm, "VvBc")
            and txt4(cm, "VvBc") == "Confirm - 250,000 coins" and int(MS.vvArm) > 0, "VAULTVIEW BUY at or above buyConfirmCoins: Buy = no call, no read; the caption asks, Confirm appears")
    p_ = mt_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW BUY a double click on Buy")
    K.check(len(VT["acts"]) == a0_ and VT["own"] == 4, "VAULTVIEW BUY a double click on Buy only re-arms (no call, nothing charged)")
    tk_ = VT["cur"][0]
    p_, nv_, na_ = vv_ev({"a": "vvbc", "t": str(MS.tok)}, "VAULTVIEW BUY Confirm")
    cm = cmap(p_)
    K.check(VT["acts"][-1] == ["buy", uk3, tk_, "prof-B", "5:250000:1"] and VT["own"] == 5 and nv_ == 1 and txt4(cm, "VvBl") == "All pages bought" and not vis8(cm, "VvBr")
            and not bind4(p_, "vvb") and txt4(cm, "VvBl2") == "You own every vault page.", "VAULTVIEW BUY Confirm = buy '5:250000:1'; then max = said, no Buy")
    a0_ = len(VT["acts"])
    p_ = mt_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW SAFE a forged Buy at max")
    K.check(len(VT["acts"]) == a0_ and cap3(p_) == str(MTD.VVNONE), "VAULTVIEW SAFE a Buy the drawing did not show = a caption, no call")
    VT["own"], VT["max"] = 3, 5
    VT["price"][4] = 150000
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW BUY back to 3 pages, page 4 at 150,000")
    a0_ = len(VT["acts"])
    p_ = mt_ev({"a": "vvbc", "t": str(MS.tok)}, "VAULTVIEW SAFE Confirm without Buy")
    K.check(len(VT["acts"]) == a0_ and "Press Buy first" in cap3(p_), "VAULTVIEW SAFE a Confirm without the Buy press = said, no call")
    p_ = mt_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW BUY arm")
    MS.vvArm = 1
    p_, nv_, na_ = vv_ev({"a": "vvbc", "t": str(MS.tok)}, "VAULTVIEW BUY a Confirm after 10 s")
    K.check(na_ == 0 and nv_ == 1 and cap3(p_).startswith("That Confirm ran out") and VT["own"] == 3 and not vis8(cmap(p_), "VvBc"),
            "VAULTVIEW BUY a Confirm after the 10 s = said, no call, drawn again (the arm dropped)")
    p_ = mt_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW BUY arm again")
    VT["pricex"] = 5
    p_, nv_, na_ = vv_ev({"a": "vvbc", "t": str(MS.tok)}, "VAULTVIEW BUY the price changed since the view")
    K.check(VT["acts"][-1][4] == "4:150000:1" and cap3(p_).startswith("The price of vault page 4 changed to 150,005") and VT["own"] == 3 and nv_ == 1
            and txt4(cmap(p_), "VvBl2") == "Costs 150,005 coins - Buy, then Confirm", "VAULTVIEW BUY a price that changed after the view = the bridge's '=' line, nothing charged; the redraw shows the new price")
    VT["pricex"] = 0
    VT["price"][4] = 75000
    VT["need"] = 3
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW BUY needs a bank level")
    cm = cmap(p_)
    K.check(not vis8(cm, "VvBr") and not bind4(p_, "vvb") and txt4(cm, "VvBl") == "Page 4 needs Bank Lv 3" and txt4(cm, "VvBl2") == "Needs Bank Lv 3 - yours is Lv 2 (the Bank sub-tab)",
            "VAULTVIEW BUY state bank = the bank level line, no Buy")
    a0_ = len(VT["acts"])
    p_ = mt_ev({"a": "vvb", "t": str(MS.tok)}, "VAULTVIEW SAFE a forged Buy in state bank")
    K.check(len(VT["acts"]) == a0_ and cap3(p_) == str(MTD.VVNONE), "VAULTVIEW SAFE a forged Buy in state bank = no call")
    VT["need"] = 0
    # ---- OPEN: act open <shown page>; '+' = the chest window replaced the page: NO redraw (no read)
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW OPEN redraw")
    tk_ = VT["cur"][0]
    v0_ = len(VT["views"])
    p_ = mt_ev({"a": "vvo", "t": str(MS.tok)}, "VAULTVIEW OPEN Open (the page stays in the harness)")
    K.check(VT["acts"][-1] == ["open", uk3, tk_, "prof-B", "1"] and VT["opened"][-1] == 1 and len(VT["views"]) == v0_ and cap3(p_) == "Vault page 1 opened."
            and len(cmds_of(p_)) == 1, "VAULTVIEW OPEN = vault:fn:act open '1'; '+' = no redraw, no read (only the caption while the page is still ours)")
    a0_ = len(VT["acts"])
    p_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW OPEN a click after Open (the token is used)")
    K.check(len(VT["acts"]) == a0_ and cap3(p_) == str(MTD.VVNONE), "VAULTVIEW OPEN a press after Open (the used token) = a caption, no call; Refresh draws again")
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW OPEN Refresh")
    VT["replace"] = True
    f0_ = len(E.sent(PK))
    v0_ = len(VT["views"])
    MS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": "vvo", "t": str(MS.tok)}))
    K.check(bool(MS.closed) and PK.pm.getCustomPage() is None and len(VT["views"]) == v0_ and not pages(PK, f0_),
            "VAULTVIEW OPEN the chest window replacing the page = our page finished, no packet, no read")
    VT["replace"] = False
    MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    p_ = mt_ev({"a": "vw:5"}, "VAULTVIEW back on the Vault view")
    K.check(int(MS.view) == 5 and only80(p_) and VT["views"][-1] == (uk3, 0), "VAULTVIEW the Vault sub-tab opens on page 0 = the page /vault opens on (the bridge picks)")
    # ---- STATES: arrowLayout=inside (the arrow slots), a backpack-less player, more slots than the view holds, off|, a null read, a '-' line
    VT["inside"] = True
    VT["icap"] = [9, 45, None]
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW STATE arrows + no backpack + a bigger storage")
    cm = cmap(p_)
    g_ = slots80(p_, "VvG")
    K.check(len(g_) == 36 and '"Page arrow"' in json.dumps(g_[27]) and '"Page arrow"' in json.dumps(g_[35]) and txt4(cm, "VvT").endswith("of 34 slots used - shared by all your profiles")
            and not vis8(cm, "VvI2") and len(slots80(p_, "VvI1")) == 36 and txt4(cm, "VvOv") == str(MTD.VVOVER),
            "VAULTVIEW STATE arrowLayout=inside: the r| slots = 'Page arrow' cells; no backpack = its grid hidden; a 45-slot storage shows 36 + the 'Open shows them all' note")
    a0_ = len(VT["acts"])
    p_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 35}, "VAULTVIEW SAFE the arrow slot")
    p2_ = mt_ev({"a": "vvi:2", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW SAFE a forged backpack click")
    K.check(len(VT["acts"]) == a0_ and cap3(p_) == "That slot holds the page arrow - nothing to take" and cap3(p2_) == "That inventory slot is empty - nothing to put",
            "VAULTVIEW SAFE the arrow slot / a section not shown = a caption, no call")
    VT["inside"] = False
    VT["icap"] = [9, 36, 9]
    VT["off"] = "Your profile is loading - try /vault again in a moment."
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW STATE off")
    cm = cmap(p_)
    K.check(vis8(cm, "VvK") and not vis8(cm, "Vvb") and txt4(cm, "VvK") == VT["off"] and not bind4(p_, "vvs") and not bind4(p_, "vvb") and not appended4(p_, "SkyyMtabVvPs")
            and only80(p_), "VAULTVIEW STATE off| = the reason line only (no grid, no buttons)")
    a0_ = len(VT["acts"])
    p_ = mt_ev({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, "VAULTVIEW SAFE a forged take while off")
    K.check(len(VT["acts"]) == a0_ and cap3(p_) == str(MTD.VVNONE), "VAULTVIEW SAFE a press while the vault is shut = a caption, no call")
    VT["off"] = None
    VT["vnull"] = True
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW STATE a null read")
    K.check(txt4(cmap(p_), "VvH") == str(MTD.VVFAIL) and not vis8(cmap(p_), "Vvb"), "VAULTVIEW STATE a null read = 'could not be read right now', nothing to press")
    VT["vnull"] = False
    BR.put("vault:fn:view", Fn(lambda o: (VT["views"].append(("dash", 0)), "-Unknown player.")[1]))
    p_ = mt_ev({"a": "vvrf"}, "VAULTVIEW STATE a '-' line")
    K.check(txt4(cmap(p_), "VvH") == "Unknown player." and not vis8(cmap(p_), "Vvb"), "VAULTVIEW STATE a '-' line = said in the head")
    BR.put("vault:fn:view", Fn(f_vview))
    # ---- NAV: the Vault sub-tab on every view head, a Vault press in another view / on the cards = no call, never a timer
    p_ = mt_ev({"a": "vw:4"}, "VAULTVIEW NAV the Bank sub-tab")
    K.check(int(MS.view) == 4 and has4(p_, "SkyyMtabKvT5") and len(bind4(p_, "vw:5")) == 1 and not has4(p_, "SkyyMtabVv")
            and txt4(cmap(p_), "KvX2") == "Items are kept in your Vault - the Vault sub-tab above shows them. This view is your coins.",
            "VAULTVIEW NAV every view head has the Vault sub-tab; the Bank view's hint points at it (no '/vault opens it')")
    a0_ = len(VT["acts"])
    v0_ = len(VT["views"])
    for x_ in ({"a": "vvs", "t": str(MS.tok), "SlotIndex": 0}, {"a": "vvrf"}, {"a": "vvpw:1"}):
        p_ = mt_ev(x_, "VAULTVIEW SAFE %s in the Bank view" % x_["a"])
        K.check(len(VT["acts"]) == a0_ and len(VT["views"]) == v0_ and "not on this page" in cap3(p_), "VAULTVIEW SAFE a Vault press (%s) in another view = a caption, no call, no read" % x_["a"])
    p_ = mt_ev({"a": "tab:3"}, "VAULTVIEW NAV the Market tab")
    K.check(int(MS.view) == 0 and has4(p_, "SkyyMtabBody") and not has4(p_, "SkyyMtabVv") and len(VT["views"]) == v0_, "VAULTVIEW NAV the Market tab = the cards (no vault read)")
    E.pump(PK)
    v0_ = len(VT["views"])
    for _x in range(3):
        E.pump(PK)
    K.check(len(VT["views"]) == v0_, "VAULTVIEW NEVER A TIMER: no vault:fn:view read without a drawing")
    K.notes.append("VAULTVIEW ran: vault reads %d, vault acts %d (%s)" % (len(VT["views"]), len(VT["acts"]), sorted(set(a_[0] for a_ in VT["acts"]))))
    for k_ in ("vault:fn:view", "vault:fn:act", "vault:fn:findLL"):
        BR.remove(k_)
'''

EXPECT_BODY = '''    "MarketTab": ["+f vvAk", "+f vvAns", "+f vvArm", "+f vvArr", "+f vvBconf", "+f vvBpg", "+f vvBpr", "+f vvBst", "+f vvIid", "+f vvIq", "+f vvLast",
                  "+f vvMax", "+f vvOk", "+f vvOwn", "+f vvPage", "+f vvPgN", "+f vvPk", "+f vvPw", "+f vvPwFree", "+f vvShown", "+f vvSid", "+f vvSq",
                  "+f vvTok", "+m fillVv", "+m vvAct", "+m vvArrow", "+m vvBuy", "+m vvCell", "+m vvLive", "+m vvOpen", "+m vvPick", "+m vvPut",
                  "+m vvReset", "+m vvShow", "+m vvTake", "~c ", "~m build", "~m fillHv", "~m fillMv", "~m fillOv", "~m goView", "~m handleDataEvent",
                  "~m viewOf"],
    # fillHv / fillMv / fillOv: MarketTabData.SIDE (a compile-time constant, inlined) holds MT_VBW (140 -> 116 for the sixth sub-tab)
    "MarketTabData": ["+f VVCAP", "+f VVFAIL", "+f VVG", "+f VVIM", "+f VVIN", "+f VVNONE", "+f VVNULL", "+f VVOFF", "+f VVOLD", "+f VVOVER", "+f VVPB",
                      "+f VVPN", "~<clinit>"],
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''


def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.79 (/bank + SkyyBank's Storage > Bank tab = the Bank view while the old menu is off; tools/menu_0_3_79_patch.py,''',
      '''"""Harness for SkyyMenu 0.3.80 (the Market tab's Vault items view on SkyyVault 0.1.11 vault:fn:view / act; tools/menu_0_3_80_patch.py, round
vaultview). GENERATED by tools/menu_0_3_80_patch.py from the 0.3.79 harness (edit the patch, not this file): every 0.3.79 check runs again on the
0.3.80 jar (OLD8 STATIC: the budget is over HOMUKV now), plus
  VAULTVIEW STATIC  the view reads vault:fn:view {UUID, page} and acts through vault:fn:act with the read's token + profile key, no timer; the sixth
                    sub-tab Vault, the Bank hint points at it; the build asserts the view fits 1080 (a 90-slot page in one grid) + its budget
            FALL    no SkyyVault = 'not on this server'; SkyyVault < 0.1.11 = the head names 0.1.11; forged take / put / Buy / Open = no call
            PAGE    Refresh = act refresh + ONE read {UUID, 0}; the page row (own / next / locked, used / usable, selected, page token), the grid
                    (icons, counts, rarity tint + coloured name from the quality index, no metadata, tooltip + click footer, activatable), the
                    inventory sections (c| / i|), NEXT PAGE, Open, Refresh; ONE section; element count
            TAKE    a vault slot click = take '<page>:<slot>:<qty>:<id>' with the view's token + profile key; '+' green; ONE new read; a double
                    click = ONE take; PUT = put '<section>:<slot>:<qty>:<shown page>:<id>'; empty / outside slots = no call
            FULL    put onto a full page / take into a full inventory = '-' red, nothing moved
            STALE   a dead token / a changed inventory / a changed vault / a profile switch = '=' plain, then the same press again runs with the new
                    token / quantity / key; an older drawing = 'The page changed'; a null answer = said, nothing read, the token kept
            PAGES   a page button = act page n + the view of page n; a locked page = '-' + the locked line, no grid / Open / take / put; forged
                    presses there = no call; the row's < > (no call, ONE read; the ends said)
            BUY     below buyConfirmCoins one press (buy '4:75000'); at or above: Buy arms Confirm (no call, no read; a double click only
                    re-arms), Confirm = buy '5:250000:1'; max / bank = no Buy; Confirm without Buy / after 10 s = no call; a changed price = '='
            OPEN    open '<shown page>', '+' = no redraw / no read; the next press = no call; the window replacing the page = finished, no packet
            STATE   arrowLayout=inside arrow cells, no backpack, a bigger storage (the note), off| (the reason line only), a null read, a '-' line
            NAV     the Vault sub-tab on every head, Vault presses in another view = no call, no read without a drawing (never a timer)
The 0.3.79 harness text follows:
Harness for SkyyMenu 0.3.79 (/bank + SkyyBank's Storage > Bank tab = the Bank view while the old menu is off; tools/menu_0_3_79_patch.py,''')
T.rep('VERSION = "0.3.79"\nJAR', 'VERSION = "0.3.80"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.78.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.79.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.78.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.79.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_79_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_80_patch.py")')
T.rep('"scratch", "bankroute", "menu"', '"scratch", "vaultview", "menu"')
T.rep('ADDED = ["MenuBankFn"]   # 0.3.79: menu:fn:bankview / menu:fn:oldmenu\n', 'ADDED = []   # 0.3.80: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.79:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.80: the Market tab's Vault view, the version strings
@@EXPECT@@
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.79"') == 1, "S VERSION")
''', '''    K.check(g.count('VERSION = "0.3.80"') == 1, "S VERSION")
''' + HARNESS_STATIC)
T.rep('''    K.check(g.count(' = mk("') == o.count(' = mk("') + 1 and 'mbk  = mk("MenuBankFn")' in g, "BANKROUTE STATIC one class added (MenuBankFn)")''',
      '''    K.check('mbk  = mk("MenuBankFn")' in g and 'mbk  = mk("MenuBankFn")' in o, "BANKROUTE STATIC (0.3.80: vs 0.3.79) MenuBankFn stays")''')
# OLD8 STATIC checked the budget line over "HOMUK": 0.3.80 adds V (the Vault view)
T.rep('''and 'MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUK")' in g,''',
      '''and 'MT_ELEMENTS = _mt_by["0"] + max(_mt_by[_s] + _mt_rt[_s] for _s in "HOMUKV")' in g,   # 0.3.80: + V''')
T.rep('''    K.notes.append("OLD8 ran: bank reads %d, bank acts %d" % (len(BK["views"]), len(BK["acts"])))
    for k_ in ("bank:fn:view", "bank:fn:act"):
        BR.remove(k_)
''', '''    K.notes.append("OLD8 ran: bank reads %d, bank acts %d" % (len(BK["views"]), len(BK["acts"])))
''' + HARNESS_VV + '''    for k_ in ("bank:fn:view", "bank:fn:act"):
        BR.remove(k_)
''')
T.rep("@@EXPECT@@", EXPECT_BODY)
if T.dst:
    T.finish()
