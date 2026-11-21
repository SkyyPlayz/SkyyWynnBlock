"""Derive SkyyMenu/build_skyymenu_0.3.56.py + SkyyMenu/test_skyymenu_0.3.56.py from the SET pin SkyyMenu 0.3.55 (generated - never re-run
its patch). Run:  python tools/menu_0_3_56_patch.py   then   python SkyyMenu/build_skyymenu_0.3.56.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.56.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.55 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.56 (2026-11-21, round inv7) = THE FURNACE / TANNING PANEL INSIDE THE INVENTORY + SKILL ICONS WITH XP BARS + THE CLASS XP BAR + A STATS LINE
+ the Furnace / Tannery in Right now.
Skyy's words: "Start it now" (11-21, 'Start the next inventory round (Furnace, skill XP bars, Requip leftovers)?'); 11-14 "furnace and tanning
will have a custom look and work more like they do in our pack than they do in vanilla"; on the approved furnace mockup (v4 -> v5) "i donty see
how you add the fuel. and move the search to the top of the metal row, above coper."; popup 'Where should editing Requip presets (and the
Charms page) happen instead?' -> "Inside the inventory (Recommended)"; popup 'Are the world page and the Requip / Charms panels right?' ->
"Yes, all three". Approved art: research/ui-theme-art/inventory-mockup-furnace.png (v5), inventory-mockup.png (v5).
  1. FURNACE / TANNING PANEL 'f' (like the Charms panel: the crafting area swaps): the Furnace and Tanning bench tabs open it when SkyySacks
     0.8.40's sacks:fn:furnList is on the server (else the pack's own pages as 0.3.55). Row 1 = the same bench tabs (Crafting goes back) +
     Refresh + Full page (the pack's own Furnace / Tannery page, kept as the fallback for anything this panel does not show). Row 2 = the
     bench status (tier, speed, charm, fuel). LEFT = the search box ABOVE the list (Skyy: "move the search to the top of the metal row,
     above coper"), 5 rows a page (icon + name + tier tag + how many you can make), ingots first by tier on the Furnace (SkyySacks' own
     order), the list's info line. MIDDLE = the picked recipe (icon, name, tier, time each, the inputs have / need), the FUEL slot (Skyy: "i
     donty see how you add the fuel"): drag fuel from your bag onto it = that many loaded, or click it = the fuel you own (bag + Void, most
     first) in the list - pick one, then 64 / All / Done; then Queue 1 / x10 / All N (N = what you can make, up to the free queue room).
     RIGHT = QUEUE (used / cap, the first 3 batches with their times, Cancel = every unfinished unit's inputs to the output slot), READY
     (the first 3), Collect all + Unload, the fuel note (enough for the whole queue / short). Every action = ONE sacks:fn:furn call with the
     list's PROFILE TOKEN (SkyySacks refuses another profile's token: nothing moves) and ONE page packet; a repeated click within 1.5 s is
     ignored (never two queues / two collects from one double click). Items move only inside SkyySacks (its counted removal, refunds,
     only-what-fits Collect) - this page moves nothing itself.
  2. SKILLS as icons with XP bars: each of the 12 cells = the skill's icon (SkyySkills' own icon item, known(id) guard) + "Lv N" + an XP bar
     (into / needed for the next level), the hover names the skill + its XP; through SkyySkills 0.4.71's read-only skill:fn:prog (without it:
     the 0.3.55 text cells). The class skill comes first. The left column gains the CLASS XP bar (the class skill's XP into its level) and
     a STATS line (Strength, Crit Chance, Crit Damage, Speed - the Stats page's own rows, read only).
  3. RIGHT NOW: "Furnace: N ready" / "Tannery: N in the queue" rows (sacks:fn:furnList "sum", reads only); Go opens the panel.
  NOT BUILT (next round, nothing half-wired): dailies / to-do rows (no bridge publishes dailies yet); the Requip leftovers (storage strip
     scroll, Salvage - needs a SkyyWardrobe journaled salvage op on requip:fn:act -, charm / ability slots); keys 1-5 for the presets while
     the inventory is open (NEEDS A CLIENT PROBE - SkyyUiProbe is retired; SetActiveSlot goes to the engine, not the page's event data);
     Merge 3 + Upgrade bag (open question, Skyy's costs).
  No command, no setting, no lang key, no system, no new class, no saved data. Client-crash rules kept: never setPageWithWindows; every grid
  copy a NEW ItemStack(id, 1) without metadata behind known(id); no Top / Bottom alignment; inline page only.
  ROLLBACK to 0.3.55: safe alone (nothing saved; the bench tabs open the pack's pages again). Goes with SkyySacks 0.8.40 + SkyySkills 0.4.71
  (both optional: without them the old pages / text cells).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.55.py"), os.path.join(MOD, "build_skyymenu_0.3.56.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.55.py"), os.path.join(MOD, "test_skyymenu_0.3.56.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.55"\n') and P.has("tools/menu_0_3_55_patch.py") and P.has("fillTpRow")
assert not P.has("fillFurn"), "not the generated SkyyMenu 0.3.55 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(" = mk(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.56: THE FURNACE / TANNING PANEL inside the inventory (search above the list, fuel slot, queue, Collect all - SkyySacks 0.8.40 bridges) +
       SKILL ICONS WITH XP BARS, the class XP bar + a stats line (SkyySkills 0.4.71 skill:fn:prog) + Furnace / Tannery rows in Right now
       (notes: tools/menu_0_3_56_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.56.py.
''')
P.rep('VERSION = "0.3.55"\n', 'VERSION = "0.3.56"\n')

# ---------- (1) the skill cells: icon + Lv + XP bar
P.rep('''            ap.append(("#" + rw, G_.glass_group(cl_, cw3, 36, role="inset", layout="Left", pad={"horizontal": 6}, anchor={"right": 6} if c_ < 2 else None)))
            ap.append(("#" + cl_, lab(IV + "Sk%d" % k_, "", 13, "text", bold=True, w=cw3 - 12, h=36, halign="Center")))''',
      '''            # 0.3.56: the skill's icon (a 1 x 1 grid) + "Lv N" + the XP bar track (its fill is appended at run time)
            ap.append(("#" + rw, G_.glass_group(cl_, cw3, 36, role="inset", layout="Left", pad={"horizontal": 4}, anchor={"right": 6} if c_ < 2 else None)))
            ap.append(("#" + cl_, G_.glass_grid(IV + "SkI%d" % k_, 1, 1, drag=False, slot=32, icon=26, anchor={"top": 2})))
            sx_ = IV + "SkX%d" % k_
            ap.append(("#" + cl_, G_.glass_group(sx_, IV_SKBW, 36, layout="Top", anchor={"left": 4})))
            ap.append(("#" + sx_, lab(IV + "Sk%d" % k_, "", 13, "text", bold=True, w=IV_SKBW, h=24)))
            ap.append(("#" + sx_, 'Group #%sSb%d { Anchor: (Width: %d, Height: 6); LayoutMode: Left; Background: %s; }' % (IV, k_, IV_SKBW, IV_TRACK)))
            assert 4 + 32 + 4 + IV_SKBW + 4 <= cw3, ("0.3.56: a skill cell fits", cw3)''')
P.rep('''IV_SKN, IV_NOWN, IV_TPN, IV_VCN = 12, 8, 8, 6
''', '''IV_SKN, IV_NOWN, IV_TPN, IV_VCN = 12, 8, 8, 6
# 0.3.56: the XP bars (the skill cells' bar width, the track colour, the run-time fill: digits for {W} only)
IV_SKBW = 84
IV_TRACK = SUI.glass_col("inset")
IV_FILL = "Group { Anchor: (Width: {W}, Height: 6); Background: %s; }" % SUI.glass_col("xp")
''')
# ---------- (2) the left column: the class XP bar + the stats line under the vitals
P.rep('''    left_used = 34 + 8 + 26 + 22 + 18 + 6 + gear_h + 8 + 26 + 4 + 56 + 10 + 64 + 34 + 10 + 76 + 24   # 0.3.53: + the Summon row''',
      '''    # 0.3.56: the CLASS XP bar (label + numbers, the track; the fill at run time) + the stats line
    cx_ = IV + "CxpRow"
    ap.append(("#" + ch, G_.glass_group(cx_, ciw, 18, layout="Left", anchor={"top": 6})))
    ap.append(("#" + cx_, lab(IV + "CxpT", "", 12, "dim", bold=True, w=ciw // 2, h=18)))
    ap.append(("#" + cx_, lab(IV + "CxpN", "", 12, "xp", w=ciw - ciw // 2, h=18, halign="End")))
    ap.append(("#" + ch, 'Group #%sCxpB { Anchor: (Width: %d, Height: 6, Top: 2); LayoutMode: Left; Background: %s; }' % (IV, ciw, IV_TRACK)))
    ap.append(("#" + ch, lab(IV + "Stl", "", 12, "text", w=ciw, h=18, anchor={"top": 4})))
    IV_CXBW[0] = ciw
    left_used = 34 + 8 + 26 + 22 + 18 + 6 + gear_h + 8 + 26 + 4 + 56 + 10 + 64 + 34 + 10 + 76 + 24   # 0.3.53: + the Summon row
    left_used += 6 + 18 + 2 + 6 + 4 + 18   # 0.3.56: + the class XP bar + the stats line''')
P.rep('''IV_BW_ALL = [0]
IV_AP, IV_BINDS, IV_H = _inv_page()''', '''IV_BW_ALL = [0]
IV_CXBW = [0]   # 0.3.56: the class XP bar's width (the left column's inner width)
IV_AP, IV_BINDS, IV_H = _inv_page()''')

# ---------- (3) the Furnace / Tanning panel 'f' (built after the Teleports panel)
P.rep('''             "t": (SUI.Appends(), [])}   # 0.3.55: + 't' Teleports
''', '''             "t": (SUI.Appends(), []),   # 0.3.55: + 't' Teleports
             "f": (SUI.Appends(), [])}   # 0.3.56: + 'f' Furnace / Tanning
''')
P.rep('''_inv_tp()
SUI.check_page(IV_AP, IV)
''', '''_inv_tp()
# 0.3.56: THE FURNACE / TANNING PANEL 'f' (approved inventory-mockup-furnace.png v5): bench tabs + Refresh + Full page, the status line, then
# LEFT the search ABOVE the list (5 rows a page) | MIDDLE the picked recipe, the FUEL slot, Queue 1 / x10 / All | RIGHT queue, ready, Collect all
IV_FXR, IV_FXS, IV_FQN, IV_FON = 5, 30, 3, 3
IV_FX_LW = 250
IV_TXT.update({
    "fxHelp": "Pick a recipe on the left, then 1, x10 or All.",
    "fxFuel": "Drag fuel onto the slot, or click it to pick fuel.",
    "fxPick": "Fuel you own - most first. Pick one, then 64 or All.",
})


def _inv_furn():
    G_ = SUI
    lab = G_.glass_label
    ph = IV_CRAFT_H[0]
    pw = IV_COL_M - 20
    TP = "#" + IV + "TopP"
    ap, binds = IV_PANELS["f"]
    pan = IV + "FxPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    ra = IV + "FxA"
    ap.append(("#" + pan, G_.glass_group(ra, pw, 36, layout="Left")))
    fbw = pw - 90 - 6 - 110 - 8
    ap.append(("#" + ra, G_.glass_group(IV + "FxB", fbw, 36, layout="Left", anchor={"right": 8})))
    ap.append(("#" + ra, G_.glass_button(IV + "FxRf", "Refresh", "secondary", w=90, h=34, size=13)))
    ap.append(("#" + ra, G_.glass_button(IV + "FxFp", "Full page", "secondary", w=110, h=34, size=13, anchor={"left": 6})))
    IV_FX_BW[0] = fbw
    ap.append(("#" + pan, lab(IV + "FxS", "", 12, "gold", w=pw, h=18, anchor={"top": 4})))
    bh = ph - 20 - 36 - 4 - 18 - 4
    bd = IV + "FxBody"
    ap.append(("#" + pan, G_.glass_group(bd, pw, bh, layout="Left", anchor={"top": 4})))
    lw = IV_FX_LW
    cw = (pw - lw - 16) // 2
    # LEFT: the search row ABOVE the list (Skyy "move the search to the top of the metal row, above coper") + the pages, the list, the info
    L = IV + "FxL"
    ap.append(("#" + bd, G_.glass_group(L, lw, bh, layout="Top")))
    sr = IV + "FxSr"
    ap.append(("#" + L, G_.glass_group(sr, lw, 30, layout="Left")))
    ap.append(("#" + sr, G_.text_field(IV + "FqBox", IV + "Fq", w=112, h=30, placeholder="Search", max_length=24, size=13)))
    ap.append(("#" + sr, G_.glass_button(IV + "FqGo", "Go", "secondary", w=40, h=30, size=13, anchor={"left": 4})))
    ap.append(("#" + sr, G_.glass_button(IV + "FpP", "<", "secondary", w=26, h=30, size=13, anchor={"left": 4})))
    ap.append(("#" + sr, lab(IV + "FpN", "", 12, "text", bold=True, w=36, h=30, halign="Center")))
    ap.append(("#" + sr, G_.glass_button(IV + "FpX", ">", "secondary", w=26, h=30, size=13)))
    assert 112 + 4 + 40 + 4 + 26 + 36 + 26 <= lw, "0.3.56: the Furnace search row fits"
    gw, gh = SUI.glass_grid_size(1, IV_FXR, IV_FXS)
    lr = IV + "FxLr"
    ap.append(("#" + L, G_.glass_group(lr, lw, gh, layout="Left", anchor={"top": 4})))
    ap.append(("#" + lr, G_.glass_grid(IV + "FxG", 1, IV_FXR, drag=False, slot=IV_FXS, icon=IV_FXS - 6)))
    bc = IV + "FxBc"
    ap.append(("#" + lr, G_.glass_group(bc, lw - gw - 4, gh, layout="Top", anchor={"left": 4})))
    for i_ in range(IV_FXR):
        ap.append(("#" + bc, G_.glass_button(IV + "Fr%d" % i_, "", "secondary", w=lw - gw - 4, h=IV_FXS, size=12,
                                             anchor={"bottom": SUI.GRID_SPACING} if i_ < IV_FXR - 1 else None)))
        binds.append(("#" + IV + "Fr%d" % i_, "fr:%d" % i_))
    ap.append(("#" + L, lab(IV + "FxLi", "", 12, "dim", w=lw, h=20, anchor={"top": 4})))
    assert 30 + 4 + gh + 4 + 20 <= bh, ("0.3.56: the Furnace list fits", gh, bh)
    # fix inv7 critic #2: the row text is measured at run time (fxRow) against the button's inner width, from the client's own glyph advances
    IV_FX_TXW[0] = (lw - gw - 4 - 12) * 100
    IV_FXW[:] = [int(round(SUI.text_width(chr(c_), 12, bold=True) * 100)) for c_ in range(32, 127)]
    assert sum(IV_FXW[ord(c_) - 32] for c_ in "Copper Ingot  T1  1,792") <= IV_FX_TXW[0], "0.3.56: a short row fits whole"
    # MIDDLE: the picked recipe, its inputs, the FUEL slot, Queue 1 / x10 / All, the answer line
    ap.append(("#" + bd, "Group { Anchor: (Width: 8); }"))
    M_ = IV + "FxM"
    ap.append(("#" + bd, G_.glass_group(M_, cw, bh, role="inset", layout="Top", pad=8)))
    mw = cw - 16
    orow = IV + "FxOr"
    ap.append(("#" + M_, G_.glass_group(orow, mw, 40, layout="Left")))
    ap.append(("#" + orow, G_.glass_grid(IV + "FxO", 1, 1, drag=False, slot=40, icon=34)))
    ot = IV + "FxOt"
    ap.append(("#" + orow, G_.glass_group(ot, mw - 44, 40, layout="Top", anchor={"left": 4})))
    ap.append(("#" + ot, lab(IV + "FxON", "", 14, "title", bold=True, w=mw - 44, h=22)))
    ap.append(("#" + ot, lab(IV + "FxOS", "", 11, "dim", w=mw - 44, h=18)))
    ap.append(("#" + M_, lab(IV + "FxI0", "", 11, "text", w=mw, h=16, anchor={"top": 4})))
    ap.append(("#" + M_, lab(IV + "FxI1", "", 11, "text", w=mw, h=16)))
    fh = IV + "FxFh"
    ap.append(("#" + M_, G_.glass_group(fh, mw, 16, layout="Left", anchor={"top": 4})))
    ap.append(("#" + fh, lab(IV + "FxFt", "FUEL", 11, "dim", bold=True, w=50, h=16)))
    # fix inv7 critic #1 (docs/answered/ui.md 2026-10-18: the fuel turns red when it will not finish the whole queue, green when it will):
    # one label per colour in a fixed holder (kit 1.9 keep_holder, the 0.3.55 VxN way), fillFurn shows the one that fits (.Visible only)
    fnv = [SUI.keep_at0(lab(IV + "FxFn" + s_, "", 11, c_, w=mw - 50, h=16, halign="End")) for s_, c_ in (("", "text"), ("R", "red"), ("G", "green"))]
    hm_, kids_ = SUI.keep_holder(IV + "FxFnH", mw - 50, 16, fnv)
    ap.append(("#" + fh, hm_))
    ap.extend(kids_)
    frw = IV + "FxFr"
    ap.append(("#" + M_, G_.glass_group(frw, mw, 40, layout="Left", anchor={"top": 2})))
    ap.append(("#" + frw, G_.glass_grid(IV + "FxF", 1, 1, drag=False, slot=40, icon=34)))
    ft = IV + "FxFx"
    ap.append(("#" + frw, G_.glass_group(ft, mw - 44, 40, layout="Top", anchor={"left": 4})))
    ap.append(("#" + ft, lab(IV + "FxF0", "", 12, "title", bold=True, w=mw - 44, h=20)))
    ap.append(("#" + ft, lab(IV + "FxF1", "", 11, "dim", w=mw - 44, h=18)))
    brw = IV + "FxBr"
    ap.append(("#" + M_, G_.glass_group(brw, mw, 28, layout="Left", anchor={"top": 6})))
    bw3 = (mw - 8) // 3
    for i_, (t_, k_) in enumerate((("1", "primary"), ("x10", "secondary"), ("All", "secondary"))):
        ap.append(("#" + brw, G_.glass_button(IV + "Fb%d" % i_, t_, k_, w=bw3, h=28, size=13, anchor={"left": 4} if i_ else None)))
        binds.append(("#" + IV + "Fb%d" % i_, "fb:%d" % i_))
    for _t in ("All 1000", "Done", "64"):
        assert SUI.text_width(_t, 13, bold=True) <= bw3 - 8, ("0.3.56: a Furnace button text fits", _t, bw3)
    ap.append(("#" + M_, lab(IV + "FxMsg", "", 11, "text", w=mw, h=20, anchor={"top": 4})))
    assert 40 + 4 + 16 + 16 + 4 + 16 + 2 + 40 + 6 + 28 + 4 + 20 <= bh - 16, ("0.3.56: the Furnace middle column fits", bh)
    # RIGHT: QUEUE (Cancel), READY, Collect all + Unload, the fuel note
    ap.append(("#" + bd, "Group { Anchor: (Width: 8); }"))
    R_ = IV + "FxRt"
    ap.append(("#" + bd, G_.glass_group(R_, cw, bh, role="inset", layout="Top", pad=8)))
    qh = IV + "FxQh"
    ap.append(("#" + R_, G_.glass_group(qh, mw, 22, layout="Left")))
    ap.append(("#" + qh, lab(IV + "FxQt", "QUEUE", 12, "accentHi", bold=True, w=mw - 70, h=22)))
    ap.append(("#" + qh, G_.glass_button(IV + "FxCq", "Cancel", "secondary", w=70, h=22, size=11)))
    for i_ in range(IV_FQN):
        ap.append(("#" + R_, lab(IV + "Fu%d" % i_, "", 11, "text", w=mw, h=16)))
    ap.append(("#" + R_, lab(IV + "FxRh", "READY", 12, "accentHi", bold=True, w=mw, h=18, anchor={"top": 4})))
    for i_ in range(IV_FON):
        ap.append(("#" + R_, lab(IV + "Fo%d" % i_, "", 11, "green", w=mw, h=16)))
    cr_ = IV + "FxCr"
    ap.append(("#" + R_, G_.glass_group(cr_, mw, 28, layout="Left", anchor={"top": 6})))
    ap.append(("#" + cr_, G_.glass_button(IV + "FxCo", "Collect all", "primary", w=mw - 6 - 76, h=28, size=13)))
    ap.append(("#" + cr_, G_.glass_button(IV + "FxUl", "Unload", "secondary", w=76, h=28, size=12, anchor={"left": 6})))
    ntv = [SUI.keep_at0(lab(IV + "FxNt" + s_, "", 11, c_, w=mw, h=20)) for s_, c_ in (("", "dim"), ("R", "red"), ("G", "green"))]
    hm_, kids_ = SUI.keep_holder(IV + "FxNtH", mw, 20, ntv, anchor={"top": 4})
    ap.append(("#" + R_, hm_))
    ap.extend(kids_)
    assert 22 + IV_FQN * 16 + 4 + 18 + IV_FON * 16 + 6 + 28 + 4 + 20 <= bh - 16, ("0.3.56: the Furnace right column fits", bh)
    binds.extend([("#" + IV + "FxRf", "fxr"), ("#" + IV + "FxFp", "fxp"), ("#" + IV + "FpP", "fpp"), ("#" + IV + "FpX", "fpn"),
                  ("#" + IV + "FxCq", "fxc"), ("#" + IV + "FxCo", "fxo"), ("#" + IV + "FxUl", "fxu")])


IV_FX_BW = [0]
IV_FX_TXW = [0]
IV_FXW = []
_inv_furn()
SUI.check_page(IV_AP, IV)
''')
P.rep('''for _c in ("c", "r", "q", "p", "v", "t")]:''', '''for _c in ("c", "r", "q", "p", "v", "t", "f")]:''')
P.rep('''for _g in ("TpE", "TxPan", "TxT", "TxPn", "TxH", "TxG", "TxM", "TxD", "PUp", "PCm", "Pr"):
    assert IV + _g in _iv_ids, "0.3.55: the page has #" + IV + _g
''', '''for _g in ("TpE", "TxPan", "TxT", "TxPn", "TxH", "TxG", "TxM", "TxD", "PUp", "PCm", "Pr"):
    assert IV + _g in _iv_ids, "0.3.55: the page has #" + IV + _g
for _g in (("FxPan", "FxB", "FxRf", "FxFp", "FxS", "Fq", "FqGo", "FpP", "FpN", "FpX", "FxG", "FxLi", "FxO", "FxON", "FxOS", "FxI0", "FxI1", "FxFn", "FxF",
            "FxF0", "FxF1", "FxMsg", "FxQt", "FxCq", "FxCo", "FxUl", "FxNt", "FxFnH", "FxFnR", "FxFnG", "FxNtH", "FxNtR", "FxNtG", "CxpT", "CxpN", "CxpB", "Stl")
           + tuple("Fr%d" % k_ for k_ in range(IV_FXR)) + tuple("Fb%d" % k_ for k_ in range(3)) + tuple("Fu%d" % k_ for k_ in range(IV_FQN))
           + tuple("Fo%d" % k_ for k_ in range(IV_FON)) + tuple("SkI%d" % k_ for k_ in range(IV_SKN)) + tuple("Sb%d" % k_ for k_ in range(IV_SKN))):
    assert IV + _g in _iv_ids, "0.3.56: the page has #" + IV + _g
for _mk in (IV_FILL.replace("{W}", "40"),):
    SUI.check_markup(_mk, prefix=IV, kit_paths=True)
    assert "@" not in _mk and "\\n" not in _mk, "0.3.56: a runtime markup line Java can hold"
''')
P.rep('''IV_RUNTIME_MAX = max(IV_BMAX, 2 * (1 + len(IV_PCATS)), IV_RLMAX) + IV_PMAX + 1 + len(IV_PCATS) + 1 + 4 * IV_NOWN   # bench tabs or list rows + presets + pocket tabs + Right now''',
      '''IV_RUNTIME_MAX = max(IV_BMAX, 2 * (1 + len(IV_PCATS)), IV_RLMAX) + IV_PMAX + 1 + len(IV_PCATS) + 1 + 4 * IV_NOWN   # bench tabs or list rows + presets + pocket tabs + Right now
IV_RUNTIME_MAX += IV_SKN + 1   # 0.3.56: the skill XP bar fills + the class XP bar fill''')
# InvData: the 0.3.56 constants
P.rep('''for _n, _k in (("TP_NOTE", "tpNote"), ("TP_EDIT", "tpEdit"), ("TX_HELP", "txHelp")):
    F(idat, "public static final String %s = %s;" % (_n, jstr(IV_TXT[_k])))
''', '''for _n, _k in (("TP_NOTE", "tpNote"), ("TP_EDIT", "tpEdit"), ("TX_HELP", "txHelp")):
    F(idat, "public static final String %s = %s;" % (_n, jstr(IV_TXT[_k])))
# 0.3.56: the Furnace / Tanning panel (bench tab row width, list rows, queue / ready lines, texts) + the XP bars
for _n, _v in (("FX_BW", IV_FX_BW[0]), ("FXR", IV_FXR), ("FQN", IV_FQN), ("FON", IV_FON), ("SKBW", IV_SKBW), ("CXBW", IV_CXBW[0])):
    F(idat, "public static final int %s = %d;" % (_n, _v))
for _n, _k in (("FX_HELP", "fxHelp"), ("FX_FUEL", "fxFuel"), ("FX_PICK", "fxPick")):
    F(idat, "public static final String %s = %s;" % (_n, jstr(IV_TXT[_k])))
F(idat, "public static final String XP_FILL = %s;" % jstr(IV_FILL))
F(idat, "public static final int FX_TXW = %d;" % IV_FX_TXW[0])   # fix inv7 critic #2: the list row's inner width (1/100 px)
F(idat, "public static final int[] FXW = new int[] { %s };" % ", ".join(str(v_) for v_ in IV_FXW))   # the glyph advances of ' '..'~' (size 12 bold, 1/100 px)
assert IV_FX_TXW[0] > 15000 and len(IV_FXW) == 95 and min(IV_FXW) > 0, "0.3.56: the row widths were measured"
assert IV_FX_BW[0] > 200 and IV_CXBW[0] > 200, "0.3.56: the widths were measured"
''')

# ---------- InvPage state
P.rep('''           "public String[] tkeys;", "public String tkey;", "public int tslot;", "public String[] tcand;", "public int tpage;", "public String tnote;"):''',
      '''           "public String[] tkeys;", "public String tkey;", "public int tslot;", "public String[] tcand;", "public int tpage;", "public String tnote;",
           # 0.3.56: the Furnace / Tanning panel - the bench, the picked recipe id, the search, the list page, the ids drawn (recipes or fuels),
           # the fuel picker on + the picked fuel, the list's profile token, the answer line + the last answer, the bench burns fuel, the free
           # queue room + what the picked recipe can make (the All button)
           "public String fbench;", "public String fsel;", "public String fquery;", "public int fpage;", "public String[] fshown;",
           "public boolean fpick;", "public String ffuel;", "public String fkey;", "public String fnote;", "public String flast;",
           "public boolean fneeds;", "public long froom;", "public long flim;"):''')
P.rep('''  this.tpage = 0;
  this.tnote = "";
}""")

# ---- InvState: helpers''', '''  this.tpage = 0;
  this.tnote = "";
  this.fbench = "Furnace";
  this.fsel = null;
  this.fquery = "";
  this.fpage = 0;
  this.fshown = new String[0];
  this.fpick = false;
  this.ffuel = null;
  this.fkey = null;
  this.fnote = "";
  this.flast = "";
  this.fneeds = false;
  this.froom = 0L;
  this.flim = 0L;
}""")

# ---- InvState: helpers''')

# ---------- fillSide: the skill cells move to fillProg (icons + XP bars; the text cells stay its fallback)
P.rep('''  java.util.ArrayList ps = new java.util.ArrayList();
  try { ps = @PKG@.StatsCalc.pairs(@PKG@.MenuUtil.bridge().get("skill:" + u.toString())); } catch (Throwable t) { ps = new java.util.ArrayList(); }
  for (int i = 0; i < @PKG@.InvData.SKN; i++) {
    String tx = "";
    if (i < ps.size()) { String[] e = (String[]) ps.get(i); tx = @PKG@.MenuUtil.safe(e[0]) + "  " + @PKG@.MenuUtil.safe(e[1]); }
    else if (i == 0) tx = "No skills yet";
    b.set("#SkyyInvSk" + i + ".Text", tx);
  }
''', '''  // 0.3.56: the skill cells = fillProg (icons + XP bars through skill:fn:prog; the 0.3.55 text cells are its fallback)
''')

# ---------- fillNow: the Furnace / Tannery rows (sacks:fn:furnList "sum", reads only)
P.rep('''  for (int i = 0; i < tr.size() && rows.size() < @PKG@.InvData.NOWN; i++) rows.add(tr.get(i));
  String[] tg = new String[rows.size()];''', '''  for (int i = 0; i < tr.size() && rows.size() < @PKG@.InvData.NOWN; i++) rows.add(tr.get(i));
  try {   // 0.3.56: the Furnace / Tannery (SkyySacks 0.8.40 sacks:fn:furnList "sum": reads only)
    java.util.function.Function ff = @PKG@.InvCraft.fn("sacks:fn:furnList");
    Object fo = ff == null ? null : ff.apply(new Object[] { u, "sum" });
    String[] fl = fo instanceof String ? ((String) fo).split("\\n") : new String[0];
    for (int i = 0; i < fl.length && rows.size() < @PKG@.InvData.NOWN; i++) {
      String[] f = fl[i].split("\\\\|", -1);
      if (f.length < 5 || !f[0].equals("sum")) continue;
      String lbl = "Tannery".equals(f[1]) ? "Tannery" : "Furnace";
      long rd = 0L;
      long qn = 0L;
      try { rd = Long.parseLong(f[2].trim()); qn = Long.parseLong(f[3].trim()); } catch (Throwable t2) { continue; }
      String tx = rd > 0L ? (lbl + ": " + @PKG@.MenuUtil.fmt(rd) + " ready" + (f[4].length() > 0 ? " - " + f[4] : "")) : (lbl + ": " + @PKG@.MenuUtil.fmt(qn) + " in the queue");
      rows.add(new String[] { tx, "furn:" + f[1] });
    }
  } catch (Throwable t) { }
  String[] tg = new String[rows.size()];''')

# ---------- fillProg + fillFurn (before build: its caller)
PROG = r'''# ---- 0.3.56: the skill cells (icons + XP bars), the class XP bar, the stats line (bridge reads only; world thread)
# fix inv7 critic #2: a Furnace list row measured with the client's glyph advances (InvData.FXW, 1/100 px) - too long = the tier tag goes
# (it stays on the hover), still too long = the name is cut with ".."; the count / "locked" always shows
M(ipg, r"""
public static int fxPx(String s) {
  int[] t = @PKG@.InvData.FXW;
  int mx = 0;
  for (int i = 0; i < t.length; i++) { if (t[i] > mx) mx = t[i]; }
  int w = 0;
  for (int i = 0; i < s.length(); i++) { int c = s.charAt(i); w = w + ((c >= 32 && c - 32 < t.length) ? t[c - 32] : mx); }
  return w;
}""")
M(ipg, r"""
public static String fxRow(String pre, String nm, String tag, String cnt) {
  int max = @PKG@.InvData.FX_TXW;
  String s = pre + nm + (tag.length() > 0 ? "  " + tag : "") + "  " + cnt;
  if (fxPx(s) <= max) return s;
  s = pre + nm + "  " + cnt;
  if (fxPx(s) <= max) return s;
  String n = nm;
  while (n.length() > 1 && fxPx(pre + n + "..  " + cnt) > max) n = n.substring(0, n.length() - 1);
  return pre + n.trim() + "..  " + cnt;
}""")
M(ipg, r"""
public static String statLine(java.util.UUID u, @ST@ st, @REF@ ref) {
  java.util.ArrayList rows = new java.util.ArrayList();
  try { @PKG@.StatsCalc.mainTab(rows, u, @PKG@.StatsCalc.vitals(st, ref)); } catch (Throwable t) { return ""; }
  String[] want = new String[] { "Strength", "Crit Chance", "Crit Damage", "Speed" };
  String[] show = new String[] { "Strength", "Crit", "Crit Dmg", "Speed" };
  StringBuilder sb = new StringBuilder();
  for (int w = 0; w < want.length; w++) {
    for (int i = 0; i < rows.size(); i++) {
      Object o = rows.get(i);
      if (!(o instanceof String[])) continue;
      String[] r = (String[]) o;
      if (r.length < 2 || !want[w].equals(r[0]) || r[1] == null || r[1].length() == 0 || r[1].equals("-")) continue;
      if (sb.length() > 0) sb.append("   ");
      sb.append(show[w]).append(' ').append(r[1]);
      break;
    }
  }
  return sb.toString();
}""")
M(ipg, r"""
public static int barW(long into, long need, int w) {
  if (need <= 0L) return w;
  if (into <= 0L) return 0;
  long x = into * (long) w / need;
  if (x > (long) w) x = (long) w;
  return (int) x;
}""")
M(ipg, r"""
public void fillProg(@UCB@ b, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  String[] pl = lines("skill:fn:prog", u);
  boolean on = pl != null && pl.length > 0 && pl[0].startsWith("ok|");
  String cls = on ? pl[0].substring(3) : "";
  int n = @PKG@.InvData.SKN;
  if (on) {
    for (int i = 0; i < n; i++) {
      java.util.ArrayList sl = new java.util.ArrayList();
      @IGS@ g = new @IGS@();
      String tx = "";
      int w = 0;
      if (i + 1 < pl.length) {
        String[] f = pl[i + 1].split("\\|", -1);
        if (f.length >= 6) {
          long lv = toLong(f[1], 0L);
          long into = toLong(f[2], 0L);
          long need = toLong(f[3], 0L);
          String nm = @PKG@.MenuUtil.safe(f[0]);
          if (known(f[4])) g.setItemStack(new @IS@(f[4], 1));
          g.setName(nm + " - Lv " + lv + (i == 0 && cls.length() > 0 && cls.equals(f[0]) ? " (your class)" : ""));
          g.setDescription(need > 0L ? ("XP " + @PKG@.MenuUtil.fmt(into) + " / " + @PKG@.MenuUtil.fmt(need) + " to Lv " + (lv + 1)) : "MAX LEVEL");
          tx = "Lv " + lv;
          w = barW(into, need, @PKG@.InvData.SKBW);
          if (i == 0 && cls.length() > 0 && cls.equals(f[0])) {
            b.set("#SkyyInvCxpT.Text", "CLASS XP - " + nm);
            b.set("#SkyyInvCxpN.Text", need > 0L ? (@PKG@.MenuUtil.fmt(into) + " / " + @PKG@.MenuUtil.fmt(need)) : "MAX LEVEL");
            int cw = barW(into, need, @PKG@.InvData.CXBW);
            if (cw > 0) b.appendInline("#SkyyInvCxpB", @PKG@.InvData.XP_FILL.replace("{W}", String.valueOf(cw)));
          }
        }
      }
      sl.add(g);
      b.set("#SkyyInvSkI" + i + ".Slots", sl);
      b.set("#SkyyInvSk" + i + ".Text", tx);
      if (w > 0) b.appendInline("#SkyyInvSb" + i, @PKG@.InvData.XP_FILL.replace("{W}", String.valueOf(w)));
    }
    if (cls.length() == 0) { b.set("#SkyyInvCxpT.Text", "CLASS XP"); b.set("#SkyyInvCxpN.Text", "no class yet"); }
  } else {   // the 0.3.55 text cells (no SkyySkills 0.4.71)
    java.util.ArrayList ps = new java.util.ArrayList();
    try { ps = @PKG@.StatsCalc.pairs(@PKG@.MenuUtil.bridge().get("skill:" + u.toString())); } catch (Throwable t) { ps = new java.util.ArrayList(); }
    for (int i = 0; i < n; i++) {
      String tx = "";
      if (i < ps.size()) { String[] e = (String[]) ps.get(i); tx = @PKG@.MenuUtil.safe(e[0]) + "  " + @PKG@.MenuUtil.safe(e[1]); }
      else if (i == 0) tx = "No skills yet";
      b.set("#SkyyInvSk" + i + ".Text", tx);
    }
    b.set("#SkyyInvCxpT.Text", "CLASS XP");
    b.set("#SkyyInvCxpN.Text", "");
  }
  String sline = "";
  try { sline = statLine(u, st, ref); } catch (Throwable t) { sline = ""; }
  b.set("#SkyyInvStl.Text", sline);
}""")
# ---- 0.3.56: THE FURNACE / TANNING PANEL fill (sacks:fn:furnList: the list's profile token is kept for the actions)
M(ipg, r"""
public void fillFurn(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList bs = this.cbenches;
  if (bs == null || bs.size() == 0) { bs = new java.util.ArrayList(); bs.add("Crafting"); bs.add(this.fbench); this.cbenches = bs; }
  int bw = (@PKG@.InvData.FX_BW - 4 * bs.size()) / bs.size();
  if (bw > 120) bw = 120;
  for (int i = 0; i < bs.size(); i++) {
    String bk = (String) bs.get(i);
    b.appendInline("#SkyyInvFxB", @PKG@.InvData.BENCH_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(bw)).replace("{S}", bk.equals(this.fbench) ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvBt" + i + ".Text", @PKG@.InvCraft.benchLabel(bk));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvBt" + i, @EVD@.of("a", "cb:" + i));
  }
  String lbl = @PKG@.InvCraft.benchLabel(this.fbench);
  String[] ls = lines("sacks:fn:furnList", new Object[] { u, this.fbench, this.fsel == null ? "" : this.fsel, this.fquery });
  String err = null;
  String[] h = null;
  if (ls == null) err = (@PKG@.InvCraft.fn("sacks:fn:furnList") == null ? "The " + lbl + " is not on this server right now - Full page opens the old one" : "The " + lbl + " did not answer - try Refresh");
  else if (!ls[0].startsWith("ok|")) err = ls[0].startsWith("off|") ? ls[0].substring(4) : "The " + lbl + " did not answer - try Refresh";
  else h = ls[0].split("\\|", -1);
  if (h != null && h.length < 16) { h = null; err = "The " + lbl + " answered in a way this menu does not know - use Full page"; }
  java.util.ArrayList qs = new java.util.ArrayList();
  java.util.ArrayList os = new java.util.ArrayList();
  java.util.ArrayList fs = new java.util.ArrayList();
  java.util.ArrayList hs = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  java.util.ArrayList is = new java.util.ArrayList();
  if (h != null) {
    String tk = h[15];
    if (this.fkey != null && !tk.equals(this.fkey) && (this.fsel != null || this.ffuel != null || this.fpick)) {
      this.fsel = null; this.ffuel = null; this.fpick = false;
      this.fnote = "Your profile changed - this is its " + lbl + " now; pick again";
    }
    this.fkey = tk;
    for (int i = 1; i < ls.length; i++) {
      String[] f = ls[i].split("\\|", -1);
      if (f.length < 3) continue;
      if (f[0].equals("q") && f.length >= 6) qs.add(f);
      else if (f[0].equals("o") && f.length >= 4) os.add(f);
      else if (f[0].equals("f") && f.length >= 5) fs.add(f);
      else if (f[0].equals("h") && f.length >= 4) hs.add(f);
      else if (f[0].equals("r") && f.length >= 9) rs.add(f);
      else if (f[0].equals("i") && f.length >= 5) is.add(f);
    }
  } else this.fkey = null;
  this.fneeds = h != null && "1".equals(h[8]);
  if (!this.fneeds) { this.fpick = false; this.ffuel = null; }
  long cap = h == null ? 0L : toLong(h[7], 0L);
  long queued = h == null ? 0L : toLong(h[6], 0L);
  this.froom = cap - queued < 0L ? 0L : cap - queued;
  b.set("#SkyyInvFxS.Text", err != null ? err : @PKG@.MenuUtil.safe(h[3]));
  // LEFT: the recipes (or, picking fuel, the fuel you own), 5 a page
  java.util.ArrayList list = this.fpick ? hs : rs;
  int per = @PKG@.InvData.FXR;
  int np = list.size() == 0 ? 1 : (list.size() + per - 1) / per;
  if (this.fpage >= np) this.fpage = np - 1;
  if (this.fpage < 0) this.fpage = 0;
  java.util.ArrayList gl = new java.util.ArrayList();
  this.fshown = new String[per];
  String[] selR = null;
  for (int i = 0; i < rs.size(); i++) { String[] f = (String[]) rs.get(i); if (f[1].equals(this.fsel)) selR = f; }
  if (selR == null && !this.fpick) this.fsel = null;
  for (int k = 0; k < per; k++) {
    @IGS@ g = new @IGS@();
    String tx = "";
    int at = this.fpage * per + k;
    if (at < list.size()) {
      String[] f = (String[]) list.get(at);
      if (this.fpick) {
        String fid = f[1];
        if (known(fid)) g.setItemStack(new @IS@(fid, 1));
        g.setName(@PKG@.MenuUtil.safe(f[2]));
        g.setDescription("You have " + @PKG@.MenuUtil.fmt(toLong(f[3], 0L)) + " (bag + Void)");
        tx = fxRow(fid.equals(this.ffuel) ? "> " : "", @PKG@.MenuUtil.safe(f[2]), "", "x" + @PKG@.MenuUtil.fmt(toLong(f[3], 0L)));
        this.fshown[k] = fid;
      } else {
        String oid = f[2];
        long lim = toLong(f[4], 0L);
        String tt = f[5];
        String tag = tt.indexOf(' ') > 0 ? tt.substring(0, tt.indexOf(' ')) : tt;
        if (known(oid)) { g.setItemStack(new @IS@(oid, 1)); g.setItemUncraftable(lim <= 0L); }
        g.setName(@PKG@.MenuUtil.safe(f[6]));
        g.setDescription((tt.length() > 0 ? tt + " - " : "") + f[8] + " each" + (f[7].length() > 0 ? " - " + f[7] : ""));
        tx = fxRow(f[1].equals(this.fsel) ? "> " : "", @PKG@.MenuUtil.safe(f[6]), tag, f[7].length() > 0 ? "locked" : @PKG@.MenuUtil.fmt(lim));
        this.fshown[k] = f[1];
      }
    }
    gl.add(g);
    b.set("#SkyyInvFr" + k + ".Text", tx);
  }
  b.set("#SkyyInvFxG.Slots", gl);
  b.set("#SkyyInvFpN.Text", (this.fpage + 1) + " / " + np);
  if (this.fquery.length() > 0) b.set("#SkyyInvFq.Value", this.fquery);
  String li = this.fpick ? @PKG@.InvData.FX_PICK : (h == null ? "" : (rs.size() + (rs.size() == 1 ? " recipe" : " recipes")
      + ("Furnace".equals(this.fbench) ? " - ingots first, by tier" : " - by tier") + (this.fquery.length() > 0 ? " - search: " + this.fquery : "")));
  if (!this.fpick && h != null && toInt(h[2], 0) <= 0) li = "No " + lbl + " accessory equipped - finish or collect what is there";
  b.set("#SkyyInvFxLi.Text", li);
  // MIDDLE: the picked recipe (or the picked fuel), the FUEL slot, the three buttons
  java.util.ArrayList og = new java.util.ArrayList();
  @IGS@ o1 = new @IGS@();
  String on = "Pick a recipe";
  String osb = "";
  String i0 = "";
  String i1 = "";
  this.flim = 0L;
  String b0 = "1";
  String b1 = "x10";
  String b2 = "All";
  if (this.fpick) {
    on = "Load fuel";
    osb = "Pick a fuel on the left";
    b0 = "64"; b1 = "All"; b2 = "Done";
    for (int i = 0; i < hs.size(); i++) {
      String[] f = (String[]) hs.get(i);
      if (!f[1].equals(this.ffuel)) continue;
      if (known(f[1])) o1.setItemStack(new @IS@(f[1], 1));
      on = @PKG@.MenuUtil.safe(f[2]);
      osb = "You have " + @PKG@.MenuUtil.fmt(toLong(f[3], 0L)) + " - the slot takes " + (h == null ? "0" : @PKG@.MenuUtil.fmt(toLong(h[10], 0L) - toLong(h[9], 0L))) + " more";
    }
  } else if (selR != null) {
    String oid = selR[2];
    if (known(oid)) o1.setItemStack(new @IS@(oid, 1));
    long oq = toLong(selR[3], 1L);
    on = @PKG@.MenuUtil.safe(selR[6]) + (oq > 1L ? " x" + oq : "");
    osb = (selR[5].length() > 0 ? selR[5] + "  -  " : "") + selR[8] + " each" + (selR[7].length() > 0 ? "  -  " + selR[7] : "");
    long lim = toLong(selR[4], 0L);
    this.flim = lim < this.froom ? lim : this.froom;
    b2 = "All " + (this.flim > 99999L ? "99999+" : String.valueOf(this.flim));
    StringBuilder s1 = new StringBuilder();
    for (int i = 0; i < is.size(); i++) {
      String[] f = (String[]) is.get(i);
      String ln = @PKG@.MenuUtil.safe(f[2]) + "  " + @PKG@.MenuUtil.fmt(toLong(f[3], 0L)) + " / " + f[4];
      if (i == 0) i0 = ln;
      else { if (s1.length() > 0) s1.append("   "); s1.append(ln); }
    }
    i1 = s1.toString();
  }
  og.add(o1);
  b.set("#SkyyInvFxO.Slots", og);
  b.set("#SkyyInvFxON.Text", on);
  b.set("#SkyyInvFxOS.Text", osb);
  b.set("#SkyyInvFxI0.Text", i0);
  b.set("#SkyyInvFxI1.Text", i1);
  b.set("#SkyyInvFb0.Text", b0);
  b.set("#SkyyInvFb1.Text", b1);
  b.set("#SkyyInvFb2.Text", b2);
  java.util.ArrayList fg = new java.util.ArrayList();
  @IGS@ f1 = new @IGS@();
  String f0t = "";
  String f1t = "";
  String fn = "";
  if (h == null) { }
  else if (!this.fneeds) { f0t = "This bench needs no fuel"; }
  else {
    String[] first = null;
    long items = 0L;
    for (int i = 0; i < fs.size(); i++) { String[] f = (String[]) fs.get(i); if (f[1].length() > 0) { if (first == null) first = f; items = items + toLong(f[3], 0L); } }
    if (first != null) {
      if (known(first[1])) f1.setItemStack(new @IS@(first[1], 1));
      f1.setName(@PKG@.MenuUtil.safe(first[2]) + " x" + @PKG@.MenuUtil.fmt(toLong(first[3], 0L)));
      f1.setDescription("Fuel loaded - " + @PKG@.MenuUtil.fmt(toLong(h[9], 0L)) + " / " + @PKG@.MenuUtil.fmt(toLong(h[10], 0L)) + " items");
      f0t = @PKG@.MenuUtil.safe(first[2]) + " x" + @PKG@.MenuUtil.fmt(toLong(first[3], 0L)) + (fs.size() > 1 ? " +" + (fs.size() - 1) : "");
    } else {
      f1.setName("Fuel slot");
      f1.setDescription(@PKG@.InvData.FX_FUEL);
      f0t = "No fuel loaded";
    }
    f1t = this.fpick ? "Click again to close the fuel list" : @PKG@.InvData.FX_FUEL;
    fn = "2".equals(h[11]) ? "needs " + h[13] + " - has " + h[12] : ("1".equals(h[11]) ? "lasts " + h[12] : "");
  }
  fg.add(f1);
  b.set("#SkyyInvFxF.Slots", fg);
  b.set("#SkyyInvFxF0.Text", f0t);
  b.set("#SkyyInvFxF1.Text", f1t);
  b.set("#SkyyInvFxFn.Text", fn);
  // fix inv7 critic #1: red = the loaded fuel will not finish the whole queue, green = it will (docs/answered/ui.md 2026-10-18)
  int fc = (h != null && this.fneeds) ? ("2".equals(h[11]) ? 1 : ("1".equals(h[11]) ? 2 : 0)) : 0;
  b.set("#SkyyInvFxFnR.Text", fn);
  b.set("#SkyyInvFxFnG.Text", fn);
  b.set("#SkyyInvFxFn.Visible", fc == 0);
  b.set("#SkyyInvFxFnR.Visible", fc == 1);
  b.set("#SkyyInvFxFnG.Visible", fc == 2);
  b.set("#SkyyInvFxMsg.Text", this.fnote.length() > 0 ? this.fnote : (h == null ? "" : (this.fpick ? "" : (selR == null ? @PKG@.InvData.FX_HELP : (this.flim > 0L ? "You can queue " + @PKG@.MenuUtil.fmt(this.flim) : (selR[7].length() > 0 ? "Locked - " + selR[7] : (this.froom <= 0L ? "The queue is full" : "Not enough materials yet")))))));
  this.fnote = "";
  // RIGHT: the queue, ready to collect, the fuel note
  b.set("#SkyyInvFxQt.Text", h == null ? "QUEUE" : "QUEUE  " + @PKG@.MenuUtil.fmt(queued) + " / " + @PKG@.MenuUtil.fmt(cap));
  for (int i = 0; i < @PKG@.InvData.FQN; i++) {
    String t = "";
    if (i < qs.size()) { String[] f = (String[]) qs.get(i); t = @PKG@.MenuUtil.safe(f[2]) + " x" + f[3] + "  -  done in " + f[5]; }
    else if (i == 0 && h != null && qs.size() == 0) t = "Empty - queue something on the left";
    if (i == @PKG@.InvData.FQN - 1 && qs.size() > @PKG@.InvData.FQN) t = "+ " + (qs.size() - @PKG@.InvData.FQN + 1) + " more batches";
    b.set("#SkyyInvFu" + i + ".Text", t);
  }
  long ready = h == null ? 0L : toLong(h[14], 0L);
  b.set("#SkyyInvFxRh.Text", ready > 0L ? "READY  " + @PKG@.MenuUtil.fmt(ready) : "READY");
  for (int i = 0; i < @PKG@.InvData.FON; i++) {
    String t = "";
    if (i < os.size()) { String[] f = (String[]) os.get(i); t = @PKG@.MenuUtil.safe(f[2]) + " x" + @PKG@.MenuUtil.fmt(toLong(f[3], 0L)); }
    else if (i == 0 && h != null && os.size() == 0) t = "Nothing ready yet";
    if (i == @PKG@.InvData.FON - 1 && os.size() > @PKG@.InvData.FON) t = "+ " + (os.size() - @PKG@.InvData.FON + 1) + " more";
    b.set("#SkyyInvFo" + i + ".Text", t);
  }
  String nt = "";
  int nc = 0;
  if (h != null) {
    String run = h[4];
    if (run.indexOf("OUT OF FUEL") >= 0) { nt = "Out of fuel - load fuel to continue"; nc = 1; }
    else if (run.indexOf("OUTPUT FULL") >= 0) nt = "Output full - collect to continue";
    else if ("2".equals(h[11])) { nt = "Not enough fuel for the whole queue"; nc = 1; }
    else if ("1".equals(h[11])) { nt = "Fuel lasts the whole queue"; nc = 2; }
    else if (queued > 0L) nt = @PKG@.MenuUtil.safe(run);
  }
  b.set("#SkyyInvFxNt.Text", nt);
  b.set("#SkyyInvFxNtR.Text", nt);
  b.set("#SkyyInvFxNtG.Text", nt);
  b.set("#SkyyInvFxNt.Visible", nc == 0);
  b.set("#SkyyInvFxNtR.Visible", nc == 1);
  b.set("#SkyyInvFxNtG.Visible", nc == 2);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvFxG", @EVD@.of("a", "fxg"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvFxF", @EVD@.of("a", "fxf"), false);
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvFxF", @EVD@.of("a", "fxd"), false);
  String fk0 = String.valueOf((char) 64) + "F";
  ev.addEventBinding(@BT@.Validating, "#SkyyInvFq", @EVD@.of("a", "fq").append(fk0, "#SkyyInvFq.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyInvFqGo", @EVD@.of("a", "fq").append(fk0, "#SkyyInvFq.Value"));
}""")
'''
P.rep('''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;''', PROG + '''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;''')
P.rep('''  try { fillTpRow(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the teleport row failed: " + t); }   // 0.3.55: the saved row
''', '''  try { fillTpRow(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the teleport row failed: " + t); }   // 0.3.55: the saved row
  try { fillProg(b, ref, st); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the skill XP bars failed: " + t); }   // 0.3.56
''')
P.rep('''  else if (pm == 't') { try { fillTp(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Teleports panel failed: " + t); } }
''', '''  else if (pm == 't') { try { fillTp(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Teleports panel failed: " + t); } }
  else if (pm == 'f') { try { fillFurn(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Furnace panel failed: " + t); } }
''')

# ---------- the Furnace / Tanning actions (after redraw / openFn / tanning, before bench(): its caller)
ACTS = r'''# ---- 0.3.56: the Furnace / Tanning panel actions (each answers with ONE packet; SkyySacks moves the items, this page nothing)
M(ipg, r"""
public void openFurn(String bk) {
  String b = "Tannery".equals(bk) ? "Tannery" : "Furnace";
  if (!b.equals(this.fbench)) { this.fsel = null; this.fpage = 0; this.fquery = ""; this.fpick = false; this.ffuel = null; }
  this.fbench = b;
  this.mode = "f";
  this.fnote = "";
  redraw();
}""")
M(ipg, r"""
public void furnFull() {
  if ("Tannery".equals(this.fbench)) { tanning(); return; }
  openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace");
}""")
M(ipg, r"""
public void furnDo(String op, String arg, String amt) {
  String lbl = @PKG@.InvCraft.benchLabel(this.fbench);
  if (this.fkey == null || this.fkey.length() == 0) { this.fnote = "Your profile is not settled yet - try again in a moment"; redraw(); return; }
  String key = "fx:" + this.fbench + ":" + op + ":" + (arg == null ? "" : arg) + ":" + (amt == null ? "" : amt);
  if (dup(key)) { this.fnote = "Double click ignored - wait a moment to click again. Last: " + this.flast; redraw(); return; }   // fix inv7 critic #3: said, not silent
  moved(key);
  Object o = call("sacks:fn:furn", new Object[] { this.playerRef.getUuid(), this.fbench, op, arg == null ? "" : arg, amt == null ? "" : amt, this.fkey });
  String r = o == null ? (@PKG@.InvCraft.fn("sacks:fn:furn") == null ? "The " + lbl + " is not on this server right now - nothing was done" : "The " + lbl + " could not do that here - nothing was done") : bare(String.valueOf(o));
  this.flast = r;
  this.fnote = r;
  if (o != null && String.valueOf(o).startsWith("-Your profile changed")) { this.fsel = null; this.ffuel = null; this.fpick = false; }
  if (o != null && String.valueOf(o).startsWith("+") && "fuel".equals(op)) { this.fpick = false; this.ffuel = null; this.fpage = 0; }
  redraw();
}""")
M(ipg, r"""
public void furnPick(int i) {
  if (this.fshown == null || i < 0 || i >= this.fshown.length || this.fshown[i] == null) { this.fnote = "That row is empty"; redraw(); return; }
  if (this.fpick) this.ffuel = this.fshown[i].equals(this.ffuel) ? null : this.fshown[i];
  else this.fsel = this.fshown[i];
  redraw();
}""")
M(ipg, r"""
public void furnBtn(int i) {
  if (this.fpick) {
    if (i == 2) { this.fpick = false; this.ffuel = null; this.fpage = 0; redraw(); return; }
    if (this.ffuel == null) { this.fnote = "Pick a fuel on the left first"; redraw(); return; }
    furnDo("fuel", this.ffuel, i == 0 ? "64" : "");
    return;
  }
  if (this.fsel == null) { this.fnote = "Pick a recipe on the left first"; redraw(); return; }
  if (i == 2 && this.flim <= 0L) { this.fnote = this.froom <= 0L ? "The queue is full" : "Not enough materials yet"; redraw(); return; }
  furnDo("queue", this.fsel, i == 0 ? "1" : (i == 1 ? "10" : "all"));
}""")
M(ipg, r"""
public void furnFuelSlot() {
  if (!this.fneeds) { this.fnote = "This bench needs no fuel"; redraw(); return; }
  this.fpick = !this.fpick;
  this.ffuel = null;
  this.fpage = 0;
  redraw();
}""")
# fuel dragged from the bag / hotbar onto the fuel slot = that many of that fuel loaded (SkyySacks takes it - inventory first, then the Void)
M(ipg, r"""
public void furnDrop(String d) {
  String id = val(d, "ItemStackId");
  if (id == null) id = this.di;
  int q = ival(d, "ItemStackQuantity", -1);
  clearDrag();
  if (!this.fneeds) { this.fnote = "This bench needs no fuel"; redraw(); return; }
  if (id == null || id.length() == 0 || id.length() >= 120) { this.fnote = "Drag fuel from your bag onto the fuel slot"; redraw(); return; }
  furnDo("fuel", id, q > 0 ? String.valueOf(q) : "");
}""")
'''
P.rep('''M(ipg, r"""
public void bench(int i) {''', ACTS + '''M(ipg, r"""
public void bench(int i) {''')
P.rep('''  if (bk.equals("Furnace")) { openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace"); return; }
  if (bk.equals("Tannery")) { tanning(); return; }
  this.cbench = bk;''', '''  if ((bk.equals("Furnace") || bk.equals("Tannery")) && @PKG@.InvCraft.fn("sacks:fn:furnList") != null) { openFurn(bk); return; }   // 0.3.56: the panel
  if (bk.equals("Furnace")) { openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace"); return; }
  if (bk.equals("Tannery")) { tanning(); return; }
  this.mode = "c";   // 0.3.56: the Crafting / a bench tab from the Furnace panel = the craft panel again
  this.cbench = bk;''')
P.rep('''  String t = this.nowT[i];
  int c = t.indexOf(':');''', '''  String t = this.nowT[i];
  if (t.startsWith("furn:")) {   // 0.3.56: the Furnace / Tannery row
    if (@PKG@.InvCraft.fn("sacks:fn:furnList") != null) { openFurn(t.substring(5)); return; }
    if ("furn:Tannery".equals(t)) { tanning(); return; }
    openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace");
    return;
  }
  int c = t.indexOf(':');''')
P.rep('''    if (a.equals("pet")) { goTab(2); return; }''', '''    // 0.3.56: the Furnace / Tanning panel
    if (a.equals("fxg")) { furnPick(ival(d, "SlotIndex", -1)); return; }
    if (a.startsWith("fr:")) { furnPick(toInt(a.substring(3), -1)); return; }
    if (a.startsWith("fb:")) { furnBtn(toInt(a.substring(3), -1)); return; }
    if (a.equals("fq")) { this.fquery = @PKG@.InvCraft.clean(val(d, String.valueOf((char) 64) + "F")); this.fpage = 0; redraw(); return; }
    if (a.equals("fpp")) { this.fpage = this.fpage - 1; redraw(); return; }
    if (a.equals("fpn")) { this.fpage = this.fpage + 1; redraw(); return; }
    if (a.equals("fxr")) { this.fnote = ""; redraw(); return; }
    if (a.equals("fxp")) { furnFull(); return; }
    if (a.equals("fxf")) { furnFuelSlot(); return; }
    if (a.equals("fxd")) { furnDrop(d); return; }
    if (a.equals("fxc")) { furnDo("cancel", "", ""); return; }
    if (a.equals("fxo")) { furnDo("collect", "", ""); return; }
    if (a.equals("fxu")) { furnDo("unload", "", ""); return; }
    if (a.equals("pet")) { goTab(2); return; }''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(" = mk(") == MK0, "0.3.56: no system / command / class added"
_i = P.s.index
assert _i("public String[] lines(String key, Object arg)") < _i("public void fillProg(") < _i("public void fillFurn(") < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.pref = ref;")
assert _i("public static boolean known(String id)") < _i("public void fillProg(")
assert _i("public void redraw()") < _i("public void openFurn(") and _i("public void tanning()") < _i("public void furnFull(") < _i("public void bench(int i)") < _i("public void nowGo(int i)")
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.55 harness: every 0.3.55 check
# runs again on the 0.3.56 jar; + the INV7 section)
T.rep('''"""Harness for SkyyMenu 0.3.55 (editable armour / off-hand, teleport row editing, pocket Upgrades + Auto-compact; tools/menu_0_3_55_patch.py).
''', '''"""Harness for SkyyMenu 0.3.56 (the Furnace / Tanning panel, skill icons + XP bars, the class XP bar; tools/menu_0_3_56_patch.py).
GENERATED by tools/menu_0_3_56_patch.py from the 0.3.55 harness (edit the patch, not this file): every 0.3.55 check runs again on the
0.3.56 jar, plus
  INV7 (EXECUTED on the stand-ins with Python stand-ins of SkyySacks 0.8.40 sacks:fn:furnList / sacks:fn:furn and SkyySkills 0.4.71
       skill:fn:prog):
       FURN    the Furnace tab = the panel INSTEAD of the craft panel (no craft grid drawn), its bench tabs (Furnace selected), the status
               line, the list (5 a page, icon + name + tier tag + can make, an unknown output id = name only), pages, the info line, the
               queue / ready / fuel lines + the fuel note; search (the typed words reach the bridge); pick a recipe = its detail (inputs
               have / need, All N = min(can make, free queue room)); 1 / x10 / All = ONE furn call each with the recipe, the amount and
               the list's PROFILE TOKEN; a double click within 1.5 s = no second call; All on a locked / empty recipe = no call; the fuel
               slot click = the fuel list (64 / All / Done), pick + 64 = ONE fuel call, the list closes on "+"; a fuel DRAG onto the slot
               = ONE fuel call with that id + quantity; Collect all / Cancel / Unload = one call each, a double Collect = one call; a
               profile token change seen on a redraw clears the pick and says so, the next call carries the new token; a "-Your
               profile changed" answer clears the pick; an off answer = the reason shown, actions refused WITHOUT a call; Full page =
               the pack's own Furnace page; the Tanning tab (no fuel: the slot says so, no list); Crafting = the craft panel again;
               without the bridge the Furnace tab opens the pack's page (0.3.55); every answer ONE page packet, every grid metadata-free
       NOW     the Furnace / Tannery rows in Right now ("sum"), Go = the panel
       PROG    the skill cells: icon (known id only) + "Lv N" + the XP bar fill (width = into / need), MAX LEVEL = a full bar, the class
               first ("your class"), the CLASS XP bar + numbers; without skill:fn:prog the 0.3.55 text cells; the stats line drawn
The 0.3.55 harness text follows:
Harness for SkyyMenu 0.3.55 (editable armour / off-hand, teleport row editing, pocket Upgrades + Auto-compact; tools/menu_0_3_55_patch.py).
''')
T.rep('VERSION = "0.3.55"\nJAR', 'VERSION = "0.3.56"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.54.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.55.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.54.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.55.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_55_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_56_patch.py")')
T.rep('"scratch", "inv6", "menu"', '"scratch", "inv7", "menu"')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.55:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.56: the Furnace / Tanning panel, the skill XP bars + the class XP bar + the stats line, Right now rows
    "InvPage": ["+f fbench", "+f ffuel", "+f fkey", "+f flast", "+f flim", "+f fneeds", "+f fnote", "+f fpage", "+f fpick", "+f fquery", "+f froom",
                "+f fsel", "+f fshown",
                "+m barW", "+m fillFurn", "+m fillProg", "+m furnBtn", "+m furnDo", "+m furnDrop", "+m furnFuelSlot", "+m furnFull", "+m furnPick",
                "+m fxPx", "+m fxRow", "+m openFurn", "+m statLine",
                "~c ", "~m bench", "~m build", "~m fillNow", "~m fillSide", "~m handleDataEvent", "~m nowGo"],
    "InvData": ["~<clinit>", "+f CXBW", "+f FON", "+f FQN", "+f FXR", "+f FXW", "+f FX_BW", "+f FX_FUEL", "+f FX_HELP", "+f FX_PICK", "+f FX_TXW", "+f SKBW", "+f XP_FILL"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.55"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.56"') == 1, "S VERSION")''')
assert 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.54.jar")' not in T.s, "0.3.56 harness: an old line is still there"

HARNESS_INV7 = r"""    # ---- INV7 (0.3.56; "Start it now" 11-21): the Furnace / Tanning panel, skill icons + XP bars, the class XP bar, Right now rows
    FX = {"calls": [], "lists": [], "tok": "ftok1", "off": None, "ans": {}, "fs": "2"}
    FREC = [("Skyy_R_Cu", "Ingredient_Bar_Iron", 1, 1792, "T1 Copper", "Copper Ingot", "", "2s"),
            ("Skyy_R_Fe", "Ingredient_Bar_Iron", 1, 1262, "T2 Iron", "Iron Ingot", "", "2s"),
            ("Skyy_R_Br", "Skyy_No_Such_Bar", 1, 0, "T3 Bronze", "Bronze Ingot", "Furnace Charm T2 unlocks this", "3s"),
            ("Skyy_R_Th", "Ingredient_Bar_Iron", 1, 86, "T4 Thorium", "Thorium Ingot", "", "4s"),
            ("Skyy_R_Ch", "Wood_Oak_Trunk", 1, 640, "", "Charcoal", "", "1s"),
            ("Skyy_R_Gl", "Rock_Stone", 1, 0, "", "Glass", "", "1s"),
            ("Skyy_R_Ba", "Rock_Stone", 2, 12, "", "Basalt", "", "1s")]

    def f_flist(o):
        a_ = [str(x_) if x_ is not None else None for x_ in list(o)]
        FX["lists"].append(tuple(a_[1:]))
        if a_[1] == "sum":
            return "sum|Furnace|64|128|Iron Ingot\nsum|Tannery|0|12|"
        if FX["off"]:
            return "off|" + FX["off"]
        b_ = a_[1]
        fu_ = "1" if b_ == "Furnace" else "0"
        ls_ = ["ok|%s|3|%s III - Furnace Charm T3|Smelting Iron Ingot - 12s left|40|312|1000|%s|640|1000|%s|16m 10s|20m|64|%s" % (b_, b_, fu_, FX["fs"], FX["tok"]),
               "q|Ingredient_Bar_Iron|Iron Ingot|64|44s|44s", "q|Ingredient_Bar_Iron|Copper Ingot|128|4m|4m 44s", "o|Ingredient_Bar_Iron|Iron Ingot|64",
               "f|Wood_Oak_Trunk|Oak Log|640|16m 10s"]
        if fu_ == "1":
            ls_ += ["h|Wood_Oak_Trunk|Oak Log|1000", "h|Rock_Stone|Stone Fuel|5"]
        q_ = (a_[3] or "").lower()
        for r_ in FREC:
            if q_ and q_ not in r_[5].lower():
                continue
            ls_.append("r|%s|%s|%d|%d|%s|%s|%s|%s" % r_)
        if a_[2]:
            ls_.append("i|Ore_Iron|Iron Ore|1262|1")
        return "\n".join(ls_)

    def f_fact(o):
        a_ = tuple(str(x_) if x_ is not None else None for x_ in list(o))
        FX["calls"].append(a_[1:])
        return FX["ans"].get(a_[2], "+queued 1 x Iron Ingot in the Furnace")
    nf_ = lambda: len(FX["calls"])
    pgF = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    one(ev(PK, {"a": "cb:0"}), "INV7 the craft panel first")
    bks_ = [str(x_) for x_ in list(pgF.cbenches)]
    fi_, ti_ = bks_.index("Furnace"), bks_.index("Tannery")
    o0_ = len(OPENED)
    p_ = one(ev(PK, {"a": "cb:%d" % fi_}), "INV7 FURN the Furnace tab without SkyySacks 0.8.40")
    K.check(len(OPENED) == o0_ + 1 and str(pgF.mode) == "c", "INV7 FURN without sacks:fn:furnList the Furnace tab opens the pack's own page (0.3.55)")
    BR.put("sacks:fn:furnList", Fn(f_flist))
    BR.put("sacks:fn:furn", Fn(f_fact))
    p_ = one(ev(PK, {"a": "cb:%d" % fi_}), "INV7 FURN the Furnace tab")
    cm = cmap(p_) if p_ else {}
    bl = binds_of(p_) if p_ else []
    K.check(str(pgF.mode) == "f" and "#SkyyInvCg.Slots" not in cm and "#SkyyInvFxG.Slots" in cm and FX["lists"][-1] == ("Furnace", "", ""),
            "INV7 FURN the Furnace tab = the panel INSTEAD of the craft panel, ONE furnList call (bench, no pick, no search)")
    K.check(sval(cm, "#SkyyInvBt%d.Text" % fi_) == "Furnace" and TSEL_ in mk_of(p_, "SkyyInvBt%d" % fi_) and sval(cm, "#SkyyInvBt0.Text") == "Crafting",
            "INV7 FURN the bench tabs on the panel, Furnace selected")
    K.eq(sval(cm, "#SkyyInvFxS.Text"), "Furnace III - Furnace Charm T3", "INV7 FURN the status line")
    K.eq([sval(cm, "#SkyyInvFr%d.Text" % k_) for k_ in range(5)], ["Copper Ingot  T1  1,792", "Iron Ingot  T2  1,262", "Bronze Ingot  T3  locked",
                                                                   "Thorium Ingot  T4  86", "Charcoal  640"], "INV7 FURN the list rows (SkyySacks' order: ingots first)")
    gs_ = cm.get("#SkyyInvFxG.Slots", "")
    K.check("Ingredient_Bar_Iron" in gs_ and "Skyy_No_Such_Bar" not in gs_ and "Bronze Ingot" in gs_ and nometa(p_),
            "INV7 FURN the list grid: icons for ids the server knows, an unknown output = name only, no metadata")
    K.check(sval(cm, "#SkyyInvFpN.Text") == "1 / 2" and sval(cm, "#SkyyInvFxLi.Text") == "7 recipes - ingots first, by tier", "INV7 FURN 7 recipes = 2 pages, the info line")
    K.check(sval(cm, "#SkyyInvFxQt.Text") == "QUEUE  312 / 1,000" and sval(cm, "#SkyyInvFu0.Text") == "Iron Ingot x64  -  done in 44s"
            and sval(cm, "#SkyyInvFxRh.Text") == "READY  64" and sval(cm, "#SkyyInvFo0.Text") == "Iron Ingot x64" and sval(cm, "#SkyyInvFo1.Text") == "",
            "INV7 FURN the queue + ready lines")
    K.check(sval(cm, "#SkyyInvFxF0.Text") == "Oak Log x640" and sval(cm, "#SkyyInvFxFn.Text") == "needs 20m - has 16m 10s"
            and sval(cm, "#SkyyInvFxNt.Text") == "Not enough fuel for the whole queue" and "Wood_Oak_Trunk" in cm.get("#SkyyInvFxF.Slots", ""),
            "INV7 FURN the FUEL slot (the loaded fuel, its count), the need / has line, the fuel note")
    vis_ = lambda c_, k_: sval(c_, "#SkyyInv%s.Visible" % k_) in (True, "true")
    K.check(vis_(cm, "FxFnR") and not vis_(cm, "FxFn") and not vis_(cm, "FxFnG") and sval(cm, "#SkyyInvFxFnR.Text") == "needs 20m - has 16m 10s"
            and vis_(cm, "FxNtR") and not vis_(cm, "FxNt") and not vis_(cm, "FxNtG") and sval(cm, "#SkyyInvFxNtR.Text") == "Not enough fuel for the whole queue",
            "FIX1 short fuel = the RED fuel line + the RED note shown, the others hidden (ui.md 2026-10-18)")
    TXW_ = int(DATA.FX_TXW)
    px_ = lambda t_: int(pgF.fxPx(t_))
    r1_ = str(pgF.fxRow("> ", "Enchanted Copper Ingot Alloy", "T2", "locked"))
    r2_ = str(pgF.fxRow("", "Enchanted Super Compressed Thorium Alloy Ingot", "T4", "1,234"))
    r3_ = str(pgF.fxRow("", "Copper Ingot", "T1", "1,792"))
    K.check(px_(r1_) <= TXW_ and "T2" not in r1_ and r1_.startswith("> Enchanted") and r1_.endswith("locked")
            and px_(r2_) <= TXW_ and ".." in r2_ and r2_.endswith("1,234") and "T4" not in r2_ and r3_ == "Copper Ingot  T1  1,792",
            "FIX2 a long row drops its tier tag, a longer one is cut with '..', the count always shows, a short row stays whole (%r %r)" % (r1_, r2_))
    K.check(all(px_(sval(cm, "#SkyyInvFr%d.Text" % k_) or "") <= TXW_ for k_ in range(5)), "FIX2 every drawn list row fits the button")
    K.check(("SlotClicking", "#SkyyInvFxG") in [(b_[0], b_[1]) for b_ in bl] and ("Dropped", "#SkyyInvFxF") in [(b_[0], b_[1]) for b_ in bl]
            and ("Validating", "#SkyyInvFq") in [(b_[0], b_[1]) for b_ in bl] and "#SkyyInvFb2" in [b_[1] for b_ in bl] and "#SkyyInvFxCo" in [b_[1] for b_ in bl]
            and "#SkyyInvCg" not in [b_[1] for b_ in bl], "INV7 FURN the panel's bindings (list, fuel drop, search, buttons), none for the craft grid")
    p_ = one(ev(PK, {"a": "fpn"}), "INV7 FURN page 2")
    K.check(sval(cmap(p_), "#SkyyInvFr0.Text") == "Glass  0" and sval(cmap(p_), "#SkyyInvFr2.Text") == "" and sval(cmap(p_), "#SkyyInvFpN.Text") == "2 / 2", "INV7 FURN page 2")
    p_ = one(ev(PK, {"a": "fq", "@F": "iron"}), "INV7 FURN search")
    K.check(FX["lists"][-1] == ("Furnace", "", "iron") and int(pgF.fpage) == 0 and "search: iron" in (sval(cmap(p_), "#SkyyInvFxLi.Text") or ""),
            "INV7 FURN search: the typed words reach SkyySacks, page 1 (%s)" % sval(cmap(p_), "#SkyyInvFxLi.Text"))
    one(ev(PK, {"a": "fq", "@F": ""}), "INV7 FURN clear the search")
    p_ = one(ev(PK, {"a": "fr:1"}), "INV7 FURN pick Iron Ingot")
    cm = cmap(p_) if p_ else {}
    K.check(str(pgF.fsel) == "Skyy_R_Fe" and FX["lists"][-1] == ("Furnace", "Skyy_R_Fe", "") and sval(cm, "#SkyyInvFxON.Text") == "Iron Ingot"
            and sval(cm, "#SkyyInvFxOS.Text") == "T2 Iron  -  2s each" and sval(cm, "#SkyyInvFxI0.Text") == "Iron Ore  1,262 / 1"
            and sval(cm, "#SkyyInvFb2.Text") == "All 688" and str(sval(cm, "#SkyyInvFr1.Text")).startswith("> "),
            "INV7 FURN pick = the detail (tier, time, inputs have / need), All = min(1,262 can make, 688 free room), the row marked")
    n0_ = nf_()
    p_ = one(ev(PK, {"a": "fb:0"}), "INV7 FURN Queue 1")
    K.check(FX["calls"][n0_:] == [("Furnace", "queue", "Skyy_R_Fe", "1", "ftok1")] and sval(cmap(p_), "#SkyyInvFxMsg.Text") == "queued 1 x Iron Ingot in the Furnace",
            "INV7 FURN 1 = ONE furn queue call (recipe, 1, the list's token), the answer shown")
    p_ = one(ev(PK, {"a": "fb:0"}), "INV7 FURN the same click again")
    K.eq(nf_(), n0_ + 1, "INV7 FURN a double click within 1.5 s = no second queue")
    K.check(str(sval(cmap(p_), "#SkyyInvFxMsg.Text")).startswith("Double click ignored") and "queued 1 x Iron Ingot" in str(sval(cmap(p_), "#SkyyInvFxMsg.Text")),
            "FIX3 the ignored second click is SAID, not silent (%s)" % sval(cmap(p_), "#SkyyInvFxMsg.Text"))
    pgF.lastMoveAt = 0
    one(ev(PK, {"a": "fb:1"}), "INV7 FURN x10")
    pgF.lastMoveAt = 0
    one(ev(PK, {"a": "fb:2"}), "INV7 FURN All")
    K.eq(FX["calls"][n0_ + 1:], [("Furnace", "queue", "Skyy_R_Fe", "10", "ftok1"), ("Furnace", "queue", "Skyy_R_Fe", "all", "ftok1")], "INV7 FURN x10 = 10, All = all")
    one(ev(PK, {"a": "fr:2"}), "INV7 FURN pick the locked Bronze")
    pgF.lastMoveAt = 0
    n0_ = nf_()
    p_ = one(ev(PK, {"a": "fb:2"}), "INV7 FURN All on a locked recipe")
    K.check(nf_() == n0_ and "Not enough materials" in (sval(cmap(p_), "#SkyyInvFxMsg.Text") or ""), "INV7 FURN All with nothing to make = NO call, a hint (%s)" % sval(cmap(p_), "#SkyyInvFxMsg.Text"))
    # the FUEL slot
    p_ = one(ev(PK, {"a": "fxf"}), "INV7 FURN the fuel slot")
    cm = cmap(p_) if p_ else {}
    K.check(bool(pgF.fpick) and sval(cm, "#SkyyInvFr0.Text") == "Oak Log  x1,000" and [sval(cm, "#SkyyInvFb%d.Text" % k_) for k_ in range(3)] == ["64", "All", "Done"]
            and str(sval(cm, "#SkyyInvFxLi.Text")).startswith("Fuel you own"), "INV7 FURN the fuel slot click = the fuel you own in the list, 64 / All / Done")
    n0_ = nf_()
    p_ = one(ev(PK, {"a": "fb:0"}), "INV7 FURN 64 with no fuel picked")
    K.check(nf_() == n0_ and "Pick a fuel" in (sval(cmap(p_), "#SkyyInvFxMsg.Text") or ""), "INV7 FURN 64 with no fuel picked = no call")
    one(ev(PK, {"a": "fr:0"}), "INV7 FURN pick Oak Log")
    FX["ans"]["fuel"] = "+loaded 64 Oak Log into the Furnace"
    pgF.lastMoveAt = 0
    p_ = one(ev(PK, {"a": "fb:0"}), "INV7 FURN load 64")
    K.check(FX["calls"][n0_:] == [("Furnace", "fuel", "Wood_Oak_Trunk", "64", "ftok1")] and not bool(pgF.fpick)
            and sval(cmap(p_), "#SkyyInvFxMsg.Text") == "loaded 64 Oak Log into the Furnace", "INV7 FURN 64 = ONE fuel call (id, 64, token); the list closes on '+'")
    one(ev(PK, {"a": "fxf"}), "INV7 FURN the fuel list again")
    p_ = one(ev(PK, {"a": "fb:2"}), "INV7 FURN Done")
    K.check(not bool(pgF.fpick) and nf_() == n0_ + 1 and sval(cmap(p_), "#SkyyInvFb0.Text") == "1", "INV7 FURN Done closes the fuel list, no call")
    pgF.lastMoveAt = 0
    one(ev(PK, {"a": "fxd", "ItemStackId": "Wood_Oak_Trunk", "ItemStackQuantity": 25}), "INV7 FURN drag fuel onto the slot")
    K.eq(FX["calls"][-1], ("Furnace", "fuel", "Wood_Oak_Trunk", "25", "ftok1"), "INV7 FURN a fuel DRAG onto the slot = ONE fuel call with that id + quantity")
    # Collect all / Cancel / Unload
    FX["ans"]["collect"] = "+Collected 64 items"
    n0_ = nf_()
    p_ = one(ev(PK, {"a": "fxo"}), "INV7 FURN Collect all")
    one(ev(PK, {"a": "fxo"}), "INV7 FURN Collect all again")
    K.check(FX["calls"][n0_:] == [("Furnace", "collect", "", "", "ftok1")] and sval(cmap(p_), "#SkyyInvFxMsg.Text") == "Collected 64 items",
            "INV7 FURN Collect all = ONE collect call; a double click = still one")
    pgF.lastMoveAt = 0
    one(ev(PK, {"a": "fxc"}), "INV7 FURN Cancel")
    pgF.lastMoveAt = 0
    one(ev(PK, {"a": "fxu"}), "INV7 FURN Unload")
    K.eq([c_[1] for c_ in FX["calls"][n0_ + 1:]], ["cancel", "unload"], "INV7 FURN Cancel / Unload = one call each")
    FX["fs"] = "1"
    p_ = one(ev(PK, {"a": "fxr"}), "FIX1 Refresh with enough fuel")
    cm = cmap(p_) if p_ else {}
    K.check(vis_(cm, "FxFnG") and not vis_(cm, "FxFnR") and vis_(cm, "FxNtG") and not vis_(cm, "FxNtR") and not vis_(cm, "FxNt")
            and sval(cm, "#SkyyInvFxNtG.Text") == "Fuel lasts the whole queue", "FIX1 enough fuel = the GREEN fuel line + note")
    FX["fs"] = "0"
    p_ = one(ev(PK, {"a": "fxr"}), "FIX1 Refresh with no fuel state")
    cm = cmap(p_) if p_ else {}
    K.check(vis_(cm, "FxFn") and vis_(cm, "FxNt") and not vis_(cm, "FxFnR") and not vis_(cm, "FxNtG"), "FIX1 no fuel state = the plain lines")
    FX["fs"] = "2"
    # the profile token
    one(ev(PK, {"a": "fr:1"}), "INV7 FURN pick again")
    FX["tok"] = "ftok2"
    p_ = one(ev(PK, {"a": "fxr"}), "INV7 FURN Refresh after a profile switch")
    K.check(pgF.fsel is None and "Your profile changed" in (sval(cmap(p_), "#SkyyInvFxMsg.Text") or "") and str(pgF.fkey) == "ftok2",
            "INV7 FURN a new profile token on a redraw: the pick cleared + said so")
    one(ev(PK, {"a": "fr:1"}), "INV7 FURN pick on the new profile")
    pgF.lastMoveAt = 0
    one(ev(PK, {"a": "fb:0"}), "INV7 FURN queue on the new profile")
    K.eq(FX["calls"][-1], ("Furnace", "queue", "Skyy_R_Fe", "1", "ftok2"), "INV7 FURN the next call carries the NEW token")
    FX["ans"]["queue"] = "-Your profile changed - the Furnace now shows it; nothing was done"
    pgF.lastMoveAt = 0
    p_ = one(ev(PK, {"a": "fb:1"}), "INV7 FURN a '-Your profile changed' answer")
    K.check(pgF.fsel is None and "Your profile changed" in (sval(cmap(p_), "#SkyyInvFxMsg.Text") or ""), "INV7 FURN a '-Your profile changed' answer clears the pick")
    del FX["ans"]["queue"]
    FX["off"] = "Equip a Furnace accessory in your Void Charms to use the Furnace"
    p_ = one(ev(PK, {"a": "fxr"}), "INV7 FURN an off answer")
    K.check(sval(cmap(p_), "#SkyyInvFxS.Text") == FX["off"] and pgF.fkey is None, "INV7 FURN an off answer: the reason shown, no token kept")
    n0_ = nf_()
    pgF.lastMoveAt = 0
    p_ = one(ev(PK, {"a": "fxo"}), "INV7 FURN Collect with no token")
    K.check(nf_() == n0_ and "not settled" in (sval(cmap(p_), "#SkyyInvFxMsg.Text") or ""), "INV7 FURN no profile token = actions refused WITHOUT a call")
    FX["off"] = None
    o0_ = len(OPENED)
    p_ = one(ev(PK, {"a": "fxp"}), "INV7 FURN Full page")
    K.check(len(OPENED) == o0_ + 1 and "Opening the Furnace" in cap_of(p_), "INV7 FURN Full page = the pack's own Furnace page (sacks:fn:openFurnace)")
    p_ = one(ev(PK, {"a": "cb:%d" % ti_}), "INV7 FURN the Tanning tab")
    cm = cmap(p_) if p_ else {}
    K.check(str(pgF.fbench) == "Tannery" and FX["lists"][-1][0] == "Tannery" and sval(cm, "#SkyyInvFxF0.Text") == "This bench needs no fuel"
            and sval(cm, "#SkyyInvBt%d.Text" % ti_) == "Tanning" and TSEL_ in mk_of(p_, "SkyyInvBt%d" % ti_), "INV7 FURN the Tanning tab: the same panel for the Tannery, no fuel")
    p_ = one(ev(PK, {"a": "fxf"}), "INV7 FURN the Tannery fuel slot")
    K.check(not bool(pgF.fpick) and "needs no fuel" in (sval(cmap(p_), "#SkyyInvFxMsg.Text") or ""), "INV7 FURN the Tannery's fuel slot = a hint, no list")
    p_ = one(ev(PK, {"a": "cb:0"}), "INV7 FURN Crafting")
    K.check(str(pgF.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_) and "#SkyyInvFxG.Slots" not in cmap(p_), "INV7 FURN the Crafting tab = the craft panel again")
    # Right now
    cm = cmap(p_) if p_ else {}
    nt_ = [str(x_) for x_ in list(pgF.nowT)]
    K.check("furn:Furnace" in nt_ and "furn:Tannery" in nt_ and sval(cm, "#SkyyInvNrT%d.Text" % nt_.index("furn:Furnace")) == "Furnace: 64 ready - Iron Ingot"
            and sval(cm, "#SkyyInvNrT%d.Text" % nt_.index("furn:Tannery")) == "Tannery: 12 in the queue", "INV7 NOW the Furnace / Tannery rows (sum) (%s)" % nt_)
    p_ = one(ev(PK, {"a": "now:%d" % nt_.index("furn:Furnace")}), "INV7 NOW Go on the Furnace row")
    K.check(str(pgF.mode) == "f" and str(pgF.fbench) == "Furnace", "INV7 NOW Go = the Furnace panel")
    one(ev(PK, {"a": "cb:0"}), "INV7 back to Crafting")
    # PROG: the skill cells + the class XP bar
    BR.put("skill:fn:prog", Fn(lambda o: "ok|Swordsmanship\nSwordsmanship|23|1240|2000|Weapon_Sword_Iron|#e0b060\nMining|31|500|1000|Tool_No_Such_Pick|#aaaaaa\nFarming|100|0|0|Rock_Stone|#ffffff"))
    p_ = one(ev(PK, {"a": "cb:0"}), "INV7 PROG a redraw with skill:fn:prog")
    cm = cmap(p_) if p_ else {}
    K.eq([sval(cm, "#SkyyInvSk%d.Text" % k_) for k_ in range(4)], ["Lv 23", "Lv 31", "Lv 100", ""], "INV7 PROG the cells say Lv N (class first)")
    K.check("Weapon_Sword_Iron" in cm.get("#SkyyInvSkI0.Slots", "") and "Swordsmanship - Lv 23 (your class)" in cm.get("#SkyyInvSkI0.Slots", "")
            and "XP 1,240 / 2,000 to Lv 24" in cm.get("#SkyyInvSkI0.Slots", "") and "Tool_No_Such_Pick" not in cm.get("#SkyyInvSkI1.Slots", "")
            and "Mining - Lv 31" in cm.get("#SkyyInvSkI1.Slots", "") and "MAX LEVEL" in cm.get("#SkyyInvSkI2.Slots", "") and nometa(p_),
            "INV7 PROG the icons (known ids only), the hover names the skill + its XP, MAX LEVEL")
    K.check("Width: 52," in cm.get("#SkyyInvSb0", ""), "INV7 PROG the XP bar: 1,240 / 2,000 of 84 px = 52 (%s)" % cm.get("#SkyyInvSb0"))
    K.check("Width: 42," in cm.get("#SkyyInvSb1", "") and "Width: 84," in cm.get("#SkyyInvSb2", "") and "#SkyyInvSb3" not in cm,
            "INV7 PROG half a level = half the bar, MAX LEVEL = a full bar, an empty cell = no fill")
    cx_ = int(DATA.CXBW)
    K.check(sval(cm, "#SkyyInvCxpT.Text") == "CLASS XP - Swordsmanship" and sval(cm, "#SkyyInvCxpN.Text") == "1,240 / 2,000"
            and ("Width: %d," % (1240 * cx_ // 2000)) in cm.get("#SkyyInvCxpB", ""), "INV7 PROG the CLASS XP bar + numbers (%s)" % cm.get("#SkyyInvCxpB"))
    K.check("#SkyyInvStl.Text" in cm, "INV7 PROG the stats line is drawn (%s)" % sval(cm, "#SkyyInvStl.Text"))
    BR.put("skill:fn:prog", Fn(lambda o: None))
    p_ = one(ev(PK, {"a": "cb:0"}), "INV7 PROG skill:fn:prog answers nothing")
    K.check(sval(cmap(p_), "#SkyyInvSk0.Text") == "Mining  12" and "#SkyyInvSb0" not in cmap(p_), "INV7 PROG no answer = the 0.3.55 text cells, no bar")
    for k_ in ("sacks:fn:furnList", "sacks:fn:furn", "skill:fn:prog"):
        BR.remove(k_)
    pgF.shut()
    E.pump(PK)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_INV7 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
if T.dst:
    T.finish()
