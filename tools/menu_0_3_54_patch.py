"""Derive SkyyMenu/build_skyymenu_0.3.54.py + SkyyMenu/test_skyymenu_0.3.54.py from the SET pin SkyyMenu 0.3.53 (generated - never re-run
its patch). Run:  python tools/menu_0_3_54_patch.py   then   python SkyyMenu/build_skyymenu_0.3.54.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.54.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.53 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.54 (2026-11-20, round inv5) = THE CHARMS PANEL INSIDE THE INVENTORY (approved art research/ui-theme-art/inventory-mockup-charms.png).
Skyy's words: "Start it now" (11-20, 'Start the next inventory round (Charms panel and the rest) now?'); popup 'Where should editing Requip
presets (and the Charms page) happen instead?' -> "Inside the inventory (Recommended)"; TEST 284 "i dont see the pets the requip, the
charms, the pockets, the teleports."; popup 'Are the world page and the Requip / Charms panels right?' -> "Yes, all three".
  1. 'All charms' (and a click on the charm row) swaps the crafting area for the CHARMS PANEL (panel code 'v'; the bag, hotbar and character
     column stay) - NO jump to the old Void Charms page while SkyyAccessories 0.5.37's acc:fn:charms is there (without it: the Void Charms page
     as 0.3.53). The panel: VOID CHARMS used / slots + Accessory Power; the charm bag grid (9 x 3 per page, server-drawn copies without
     metadata, the rarity frame = the item's own quality, a charm that does not count greyed + "not counting" (a better one of its line,
     a second copy, the Omni, a line switched off), slots past the server's limit drawn as "Locked slot", an id the server does not know =
     a name-only slot), pages, Done; ALL CHARMS TOGETHER (SkyyAccessories' bonus rows: the best of each line); the PICKED charm: icon,
     name (in its rarity colour: fix of critic inv5 #2), what it gives, its Accessory Power, TIER UP -> the next rarity with its costs in
     the "(need N more)" style (the charm itself
     first) or MAX / NOT COUNTING, Tier up + Take out, the result line. DRAG a charm from the bag onto the grid = put it in (SkyyAccessories'
     own Equip). Every action carries the profile key of the list it was drawn from (SkyyAccessories refuses another profile's); a profile
     change seen on a redraw clears the pick; a double click within 1.5 s sends nothing; the page never moves an item itself.
  NOT BUILT (next round, nothing half-wired): Merge 3 + Upgrade bag (SkyyAccessories has no merge rule / per-player bag upgrade - Skyy's
     costs needed), editable armour / off-hand + the Z bar (engine: InventoryComponent$Armor sets ArmorSlotAddFilter, so the engine would
     enforce the equip rules - the harness's read-only checks must be rewritten with it), teleport row editing (new per-profile saved data),
     keys 1-5 for the presets (needs a client probe: does a custom page get the hotbar keys?), Requip storage scroll / Salvage / charm + ability
     slots (SkyyWardrobe data), the pocket Upgrades link + Auto-compact and the themed Furnace / Tanning (no SkyySacks bridge keys yet), skill
     icons + XP bars + dailies in Right now.
  No saved data, no command, no setting, no lang key, no system; no new class. Client-crash rules kept: never setPageWithWindows; every grid
  copy a NEW ItemStack(id, 1) without metadata behind the known(id) guard; no Top / Bottom alignment; inline page only; runtime markup = none
  new (the panel is static markup + b.set texts).
  ROLLBACK to 0.3.53: safe (no data). Goes with SkyyAccessories 0.5.37 (optional: without it 'All charms' opens the Void Charms page).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.53.py"), os.path.join(MOD, "build_skyymenu_0.3.54.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.53.py"), os.path.join(MOD, "test_skyymenu_0.3.54.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.53"\n') and P.has("tools/menu_0_3_53_patch.py") and P.has("fillRequip")
assert not P.has("fillCharms"), "not the generated SkyyMenu 0.3.53 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(" = mk(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.54: THE CHARMS PANEL INSIDE THE INVENTORY ('All charms' swaps the crafting area: the charm bag grid with not-counting / locked slots,
       ALL CHARMS TOGETHER, the picked charm with Tier up (costs in the '(need N more)' style) + Take out, drag a charm in - through
       SkyyAccessories 0.5.37 acc:fn:charms) (notes: tools/menu_0_3_54_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.54.py.
''')
P.rep('VERSION = "0.3.53"\n', 'VERSION = "0.3.54"\n')
P.rep('''IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), [])}
''', '''IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), []), "v": (SUI.Appends(), [])}   # 0.3.54: + 'v' Charms
''')

# ---------- the Charms panel 'v' (built after the other panels: the holder's height is known)
P.rep('''

_inv_panels()
''', '''

_inv_panels()
# 0.3.54: THE CHARMS PANEL 'v' (research/ui-theme-art/inventory-mockup-charms.png): the bag grid 9 x 3 per page, 8 total cells, 4 cost lines
IV_VC, IV_VR, IV_VS, IV_VTN, IV_VUN, IV_VML = 9, 3, 44, 8, 4, 46
IV_VRAR = ["Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic"]   # SkyyAccessories AccDefs.DISPLAY[1..6] (the picked charm's name colour)
IV_TXT["vcHelp"] = "Click a charm to see it. Drag a charm from your bag onto the grid to put it in."


def _inv_charms():
    G_ = SUI
    lab = G_.glass_label
    ph = IV_CRAFT_H[0]
    pw = IV_COL_M - 20
    TP = "#" + IV + "TopP"
    ap, binds = IV_PANELS["v"]
    pan = IV + "VxPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    va = IV + "VxA"
    ap.append(("#" + pan, G_.glass_group(va, pw, 34, layout="Left")))
    ap.append(("#" + va, lab(IV + "VxT", "VOID CHARMS", 16, "accentHi", bold=True, w=260, h=34)))
    ap.append(("#" + va, lab(IV + "VxI", "", 13, "gold", w=230, h=34)))
    sp = pw - 260 - 230 - 32 - 50 - 32 - 6 - 80
    assert sp >= 0, ("0.3.54: the Charms header fits", sp)
    ap.append(("#" + va, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + va, G_.glass_button(IV + "VxPp", "<", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + va, lab(IV + "VxPn", "", 13, "text", bold=True, w=50, h=32, halign="Center")))
    ap.append(("#" + va, G_.glass_button(IV + "VxPx", ">", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + va, G_.glass_button(IV + "VxD", "Done", "secondary", w=80, h=32, size=13, anchor={"left": 6})))
    bh = ph - 20 - 34 - 6
    vb = IV + "VxB"
    ap.append(("#" + pan, G_.glass_group(vb, pw, bh, layout="Left", anchor={"top": 6})))
    gw, gh = SUI.glass_grid_size(IV_VC, IV_VR, IV_VS)
    vl = IV + "VxL"
    ap.append(("#" + vb, G_.glass_group(vl, gw, bh, layout="Top")))
    ap.append(("#" + vl, G_.glass_grid(IV + "VxG", IV_VC, IV_VR, drag=False, slot=IV_VS, icon=IV_VS - 8)))
    ap.append(("#" + vl, lab(IV + "VxH", "", 11, "dim", w=gw, h=18, anchor={"top": 4})))
    ap.append(("#" + vl, lab(None, "ALL CHARMS TOGETHER", 12, "dim", bold=True, w=gw, h=16, anchor={"top": 2})))
    tw = (gw - 6) // 2
    rows = IV_VTN // 2
    th = (bh - gh - 4 - 18 - 2 - 16) // rows
    assert th >= 14, ("0.3.54: the totals rows fit", th, bh, gh)
    for r_ in range(rows):
        rw = IV + "VxR%d" % r_
        ap.append(("#" + vl, G_.glass_group(rw, gw, th, layout="Left")))
        for c_ in range(2):
            ap.append(("#" + rw, lab(IV + "Vt%d" % (2 * r_ + c_), "", 11, "green", w=tw, h=th, anchor={"right": 6} if c_ == 0 else None)))
    ap.append(("#" + vb, "Group { Anchor: (Width: 12); }"))
    dw = pw - gw - 12
    vd = IV + "VxRt"
    ap.append(("#" + vb, G_.glass_group(vd, dw, bh, role="inset", layout="Top", pad=8)))
    dw2 = dw - 16
    sr = IV + "VxSr"
    ap.append(("#" + vd, G_.glass_group(sr, dw2, 44, layout="Left")))
    ap.append(("#" + sr, G_.glass_grid(IV + "VxS", 1, 1, drag=False, slot=44, icon=36)))
    stx = IV + "VxSt"
    ap.append(("#" + sr, G_.glass_group(stx, dw2 - 44 - 8, 44, layout="Top", anchor={"left": 8})))
    # fix (critic inv5 #2, PROJECT-RULES 'rarity colours ... popup title'): the picked charm's NAME in its rarity colour - one label per
    # rarity in a fixed holder (kit 1.9 keep_holder, the SkyyTrees way), fillCharms shows the one of the charm's rarity (VxN = no rarity)
    nmv = [SUI.keep_at0(lab(IV + "VxN" + ("" if k_ == 0 else str(k_)), "", 14, "title" if k_ == 0 else SUI.RARITY[IV_VRAR[k_ - 1]], bold=True,
                            w=dw2 - 52, h=22)) for k_ in range(len(IV_VRAR) + 1)]
    hm_, kids_ = SUI.keep_holder(IV + "VxNH", dw2 - 52, 22, nmv)
    ap.append(("#" + stx, hm_))
    ap.extend(kids_)
    ap.append(("#" + stx, lab(IV + "VxE", "", 11, "green", w=dw2 - 52, h=22)))
    ap.append(("#" + vd, lab(IV + "VxAp", "", 11, "gold", w=dw2, h=16, anchor={"top": 4})))
    ap.append(("#" + vd, lab(IV + "VxU", "", 12, "accentHi", bold=True, w=dw2, h=16, anchor={"top": 4})))
    for k_ in range(IV_VUN):
        ap.append(("#" + vd, lab(IV + "Vu%d" % k_, "", 11, "text", w=dw2, h=16)))
    bt = IV + "VxBt"
    ap.append(("#" + vd, G_.glass_group(bt, dw2, 32, layout="Left", anchor={"top": 6})))
    bw = (dw2 - 6) // 2
    ap.append(("#" + bt, G_.glass_button(IV + "VxTu", "Tier up", "primary", w=bw, h=32, size=13)))
    ap.append(("#" + bt, G_.glass_button(IV + "VxTo", "Take out", "secondary", w=bw, h=32, size=13, anchor={"left": 6})))
    rh = bh - 16 - 44 - 20 - 20 - IV_VUN * 16 - 38 - 4
    assert rh >= 32, ("0.3.54: the two result lines fit", rh)
    ap.append(("#" + vd, lab(IV + "VxM0", "", 11, "text", w=dw2, h=16, anchor={"top": 4})))
    ap.append(("#" + vd, lab(IV + "VxM1", "", 11, "text", w=dw2, h=16)))
    assert SUI.text_width("M" * 4 + "a" * (IV_VML - 4), 11) <= dw2 + 60, ("0.3.54: a result line of %d characters about fits" % IV_VML, dw2)
    binds.extend([("#" + IV + "VxPp", "vpp"), ("#" + IV + "VxPx", "vpn"), ("#" + IV + "VxD", "vcd"), ("#" + IV + "VxTu", "vtu"), ("#" + IV + "VxTo", "vto")])


_inv_charms()
''')
# the checks + the page data: the 'v' lines go with the others
P.rep('''    assert IV + _g in _iv_ids, "0.3.53: the page has #" + IV + _g
''', '''    assert IV + _g in _iv_ids, "0.3.53: the page has #" + IV + _g
for _g in ("VxPan", "VxT", "VxI", "VxPn", "VxG", "VxH", "VxS", "VxNH", "VxN") + tuple("VxN%d" % k_ for k_ in range(1, len(IV_VRAR) + 1)) + ("VxE", "VxAp", "VxU", "VxTu", "VxTo", "VxM0", "VxM1", "VxD") + tuple("Vt%d" % k_ for k_ in range(IV_VTN)) + tuple("Vu%d" % k_ for k_ in range(IV_VUN)):
    assert IV + _g in _iv_ids, "0.3.54: the page has #" + IV + _g
''')
P.rep('''for _c in ("c", "r", "q", "p")]:''', '''for _c in ("c", "r", "q", "p", "v")]:''')
P.rep('''F(idat, "public static final String[] PCATS = %s;" % jarr(IV_PCATS))
''', '''F(idat, "public static final String[] PCATS = %s;" % jarr(IV_PCATS))
for _n, _v in (("VN", IV_VC * IV_VR), ("VTN", IV_VTN), ("VUN", IV_VUN), ("VML", IV_VML)):   # 0.3.54: the Charms panel
    F(idat, "public static final int %s = %d;" % (_n, _v))
F(idat, "public static final String VC_HELP = %s;" % jstr(IV_TXT["vcHelp"]))
F(idat, "public static final String[] VRAR = %s;" % jarr(IV_VRAR))   # fix inv5 #2: the rarity names, in the order of the #VxN1.. labels
''')

# ---------- InvPage: the Charms panel state
P.rep('''           "public int rlTop;", "public int rlPer;", "public int rnew;", "public String pkey;"):''',
      '''           "public int rlTop;", "public int rlPer;", "public int rnew;", "public String pkey;",
           # 0.3.54: the Charms panel - the picked charm ("slot|id"), its mode + next-step recipe id as drawn, the page, the answer line, the last
           # answer (a double click shows it again), the profile key of the list, the "slot|id" of every grid cell drawn
           "public String vsel;", "public String vmode;", "public String vrid;", "public int vpage;", "public String vnote;", "public String vlast;",
           "public String vkey;", "public String[] vshown;"):''')
P.rep('''  this.pkey = null;
}""")''', '''  this.pkey = null;
  this.vsel = null;
  this.vmode = "";
  this.vrid = "";
  this.vpage = 0;
  this.vnote = "";
  this.vlast = "";
  this.vkey = null;
  this.vshown = new String[0];
}""")''')

FILLS = r'''# ---- 0.3.54: THE CHARMS PANEL ('v'): acc:fn:charms vc:list (SkyyAccessories 0.5.37) - grid, totals, the picked charm (world thread, reads only)
M(ipg, r"""
public static String half(String t, int n, int part) {
  if (t == null) return "";
  if (t.length() <= n) return part == 0 ? t : "";
  int c = t.lastIndexOf(' ', n);
  if (c < n / 2) c = n;
  if (part == 0) return t.substring(0, c).trim();
  String r = t.substring(c).trim();
  return r.length() > n ? r.substring(0, n - 3) + "..." : r;
}""")
M(ipg, r"""
public static String notCounting(int a) {
  if (a == -1) return "a better one of its line counts";
  if (a == -2) return "your Omni Accessory covers it";
  if (a == -3) return "its line is switched off on this server";
  if (a == -4) return "retired";
  if (a == -5) return "a second copy - only one counts";
  return "it does not count";
}""")
M(ipg, r"""
public void fillCharms(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  String[] ls = lines("acc:fn:charms", new Object[] { "vc:list", u, "", this.vsel == null ? "" : this.vsel });
  String title = "VOID CHARMS";
  String info = "";
  String err = null;
  int cap = 0;
  int len = 0;
  int top = -1;
  java.util.HashMap at = new java.util.HashMap();
  java.util.ArrayList tot = new java.util.ArrayList();
  java.util.ArrayList costs = new java.util.ArrayList();
  String[] sh = null;
  if (ls == null) err = "Void Charms is not on this server right now";
  else if (!ls[0].startsWith("ok|")) err = ls[0].startsWith("off|") ? ls[0].substring(4) : "Void Charms did not answer";
  else {
    String[] h = ls[0].split("\\|", -1);
    String tk = h.length > 5 ? h[5] : null;
    boolean changed = tk != null && this.vkey != null && !tk.equals(this.vkey);
    if (changed && this.vsel != null) { this.vsel = null; this.vnote = "Your profile changed - these are its Void Charms; pick a charm again"; }
    this.vkey = tk;
    if (h.length > 4) { title = "VOID CHARMS  " + h[1] + " / " + h[2]; info = "Accessory Power " + h[4]; cap = toInt(h[2], 0); len = toInt(h[3], 0); }
    for (int i = 1; i < ls.length; i++) {
      String[] f = ls[i].split("\\|", -1);
      if (f.length < 3) continue;
      if (f[0].equals("c") && f.length >= 7) { int si = toInt(f[1], -1); if (si >= 0 && si < 1000) { at.put(Integer.valueOf(si), f); if (si > top) top = si; } }
      else if (f[0].equals("t")) tot.add(f);
      else if (f[0].equals("s") && f.length >= 10 && !changed) sh = f;
      else if (f[0].equals("n") && !changed) costs.add(f);
    }
  }
  if (sh == null || this.vsel == null || !this.vsel.equals(sh[1] + "|" + sh[2])) { this.vsel = null; sh = null; costs.clear(); }
  int n = cap > top + 1 ? cap : top + 1;
  if (n < 1) n = 1;
  int per = @PKG@.InvData.VN;
  int np = (n + per - 1) / per;
  if (this.vpage >= np) this.vpage = np - 1;
  if (this.vpage < 0) this.vpage = 0;
  java.util.ArrayList sl = new java.util.ArrayList();
  this.vshown = new String[per];
  for (int k = 0; k < per; k++) {
    int si = this.vpage * per + k;
    @IGS@ g = new @IGS@();
    String[] f = (String[]) at.get(Integer.valueOf(si));
    if (f != null) {
      String id = f[2];
      int a = toInt(f[3], 0);
      String key = si + "|" + id;
      if (id.length() > 0 && id.length() < 120) {
        if (known(id)) g.setItemStack(new @IS@(id, 1));
        g.setName(f[4] + (a < 0 ? "  - not counting" : "") + (key.equals(this.vsel) ? "  (picked)" : ""));
        g.setDescription(f[5] + (f[6].length() > 0 ? " - " + f[6] : "") + (a < 0 ? " - " + notCounting(a) : ""));
        if (a < 0) g.setItemUncraftable(true);
      }
      this.vshown[k] = key;
    } else if (si >= cap && si < len) {
      g.setName("Locked slot");
      g.setDescription("This server opens " + cap + " charm slots");
    }
    sl.add(g);
  }
  java.util.ArrayList one = new java.util.ArrayList();
  @IGS@ pg = new @IGS@();
  String nm = "Pick a charm";
  String fx = "";
  String tag = "";
  String up = "";
  int rv = 0;
  this.vmode = sh == null ? "" : sh[3];
  this.vrid = sh == null ? "" : sh[4];
  if (sh != null) {
    String[] f = (String[]) at.get(Integer.valueOf(toInt(sh[1], -1)));
    if (sh[2].length() < 120 && known(sh[2])) pg.setItemStack(new @IS@(sh[2], 1));
    nm = f != null ? f[4] : @PKG@.InvCraft.name(sh[2]);
    if (f != null) for (int k = 0; k < @PKG@.InvData.VRAR.length; k++) if (@PKG@.InvData.VRAR[k].equals(f[5])) rv = k + 1;
    fx = sh[7];
    tag = sh[6];
    if ("u".equals(sh[3])) up = "TIER UP  ->  " + sh[9] + "  (" + sh[8] + ")";
    else if ("m".equals(sh[3])) up = "MAX - nothing to tier up";
    else if ("x".equals(sh[3])) up = "NOT COUNTING";
    else up = "NO TIER UP";
  }
  one.add(pg);
  b.set("#SkyyInvVxG.Slots", sl);
  b.set("#SkyyInvVxS.Slots", one);
  b.set("#SkyyInvVxT.Text", title);
  b.set("#SkyyInvVxI.Text", info);
  b.set("#SkyyInvVxPn.Text", (this.vpage + 1) + " / " + np);
  b.set("#SkyyInvVxH.Text", err == null ? "Best of each line counts - greyed = not counting" : "");
  b.set("#SkyyInvVxN.Text", nm);
  b.set("#SkyyInvVxN.Visible", rv == 0);
  for (int k = 0; k < @PKG@.InvData.VRAR.length; k++) { b.set("#SkyyInvVxN" + (k + 1) + ".Text", nm); b.set("#SkyyInvVxN" + (k + 1) + ".Visible", rv == k + 1); }
  b.set("#SkyyInvVxE.Text", fx);
  b.set("#SkyyInvVxAp.Text", tag);
  b.set("#SkyyInvVxU.Text", up);
  int vu = @PKG@.InvData.VUN;
  for (int k = 0; k < vu; k++) {
    String t = "";
    if (k < costs.size()) {
      String[] f = (String[]) costs.get(k);
      t = (k == vu - 1 && costs.size() > vu) ? "+ " + (costs.size() - vu + 1) + " more costs" : ("1".equals(f[1]) ? "ok   " : "x    ") + f[2];
    }
    b.set("#SkyyInvVu" + k + ".Text", t);
  }
  int vt = @PKG@.InvData.VTN;
  for (int k = 0; k < vt; k++) {
    String t = "";
    if (k < tot.size()) {
      String[] f = (String[]) tot.get(k);
      t = (k == vt - 1 && tot.size() > vt) ? "+ " + (tot.size() - vt + 1) + " more lines" : f[1] + ": " + f[2];
    } else if (k == 0 && tot.isEmpty() && err == null) t = "Nothing yet - put charms in";
    b.set("#SkyyInvVt" + k + ".Text", t);
  }
  String msg = this.vnote.length() > 0 ? this.vnote : (err != null ? err : (sh != null ? sh[5] : @PKG@.InvData.VC_HELP));
  int ml = @PKG@.InvData.VML;
  b.set("#SkyyInvVxM0.Text", half(msg, ml, 0));
  b.set("#SkyyInvVxM1.Text", half(msg, ml, 1));
  this.vnote = "";
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvVxG", @EVD@.of("a", "vg"), false);
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvVxG", @EVD@.of("a", "vd"), false);
}""")
'''
P.rep('''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''', FILLS + '''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''')
P.rep('''  else if (pm == 'p') { try { fillPocket(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the pocket panel failed: " + t); } }
''', '''  else if (pm == 'p') { try { fillPocket(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the pocket panel failed: " + t); } }
  else if (pm == 'v') { try { fillCharms(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Charms panel failed: " + t); } }
''')

ACTIONS = r'''# ---- 0.3.54: the Charms panel actions (each answers with ONE packet: redraw or say; the page moves nothing itself)
M(ipg, r"""
public void openCharms() {
  if (@PKG@.InvCraft.fn("acc:fn:charms") == null) { openHub("character", "accessories", "Void Charms"); return; }
  this.mode = "v";
  this.vpage = 0;
  redraw();
}""")
M(ipg, r"""
public String vcAct(String op, String arg) {
  Object o = call("acc:fn:charms", new Object[] { op, this.playerRef.getUuid(), this.vkey == null ? "" : this.vkey, arg == null ? "" : arg });
  if (o == null) return @PKG@.InvCraft.fn("acc:fn:charms") == null ? "-Void Charms is not on this server right now - nothing changed" : "-Void Charms could not do that here - nothing changed";
  return String.valueOf(o);
}""")
M(ipg, r"""
public void vcDone(String r) {
  this.vlast = bare(r);
  this.vnote = this.vlast;
  if (r.startsWith("-Your profile changed")) this.vsel = null;
  redraw();
}""")
M(ipg, r"""
public void charmPick(int si) {
  if (this.vshown == null || si < 0 || si >= this.vshown.length || this.vshown[si] == null) { this.vnote = "That slot has no charm"; redraw(); return; }
  this.vsel = this.vshown[si].equals(this.vsel) ? null : this.vshown[si];
  redraw();
}""")
M(ipg, r"""
public void charmTier() {
  if (this.vsel == null) { this.vnote = "Pick a charm first"; redraw(); return; }
  if (!"u".equals(this.vmode) || this.vrid == null || this.vrid.length() == 0) { this.vnote = "This charm cannot tier up - nothing was used"; redraw(); return; }
  String key = "vt:" + this.vsel + ">" + this.vrid;
  if (dup(key)) { this.vnote = this.vlast; redraw(); return; }
  moved(key);
  vcDone(vcAct("vc:tier", this.vsel + "|" + this.vrid));
}""")
M(ipg, r"""
public void charmTake() {
  if (this.vsel == null) { this.vnote = "Pick a charm first"; redraw(); return; }
  String key = "vo:" + this.vsel;
  if (dup(key)) { this.vnote = this.vlast; redraw(); return; }
  moved(key);
  String r = vcAct("vc:take", this.vsel);
  if (r.startsWith("+")) this.vsel = null;
  vcDone(r);
}""")
# a charm dragged from the bag / hotbar onto the grid = SkyyAccessories' own Equip (it takes the charm out of the inventory itself)
M(ipg, r"""
public void charmDrop(String d) {
  String expect = val(d, "ItemStackId");
  if (expect == null) expect = this.di;
  int csec = ival(d, "SourceInventorySectionId", 999);
  int cslot = ival(d, "SourceSlotId", -1);
  if ((csec == 999 || cslot < 0) && this.dg != null) { csec = sectionOf(this.dg); cslot = this.ds; }
  clearDrag();
  if (expect == null || expect.length() == 0 || expect.length() >= 120) { this.vnote = "Drag a charm from your bag onto the grid"; redraw(); return; }
  String key = "vd:" + csec + ":" + cslot + ":" + expect;
  if (dup(key)) { this.vnote = this.vlast; redraw(); return; }
  moved(key);
  vcDone(vcAct("vc:put", expect));
}""")
'''
P.rep('''M(ipg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', ACTIONS + '''M(ipg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''    if (a.equals("vc")) { openHub("character", "accessories", "Void Charms"); return; }
''', '''    // 0.3.54: the Charms panel inside the inventory (the old Void Charms page only without SkyyAccessories 0.5.37)
    if (a.equals("vc")) { openCharms(); return; }
    if (a.equals("vg")) { charmPick(ival(d, "SlotIndex", -1)); return; }
    if (a.equals("vd")) { charmDrop(d); return; }
    if (a.equals("vtu")) { charmTier(); return; }
    if (a.equals("vto")) { charmTake(); return; }
    if (a.equals("vpp")) { this.vpage = this.vpage - 1; redraw(); return; }
    if (a.equals("vpn")) { this.vpage = this.vpage + 1; redraw(); return; }
    if (a.equals("vcd")) { this.mode = "c"; redraw(); return; }
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(" = mk(") == MK0, "0.3.54: no system / command / class added"
_i = P.s.index
assert _i("public static boolean known(") < _i("public void fillCharms(") < _i("  else if (pm == 'v')"), "0.3.54: the fill before build"
assert _i("public void redraw()") < _i("public void openCharms()") and _i("public String vcAct(") < _i("public void vcDone(") < _i("public void charmTier()") < _i('    if (a.equals("vtu"))'), "0.3.54: methods before callers"
assert P.s.count("if (known(") == 5 + 1 and P.s.count("&& known(sh[2])) pg.setItemStack(") == 1,"0.3.54: the two new grid ItemStacks (charm grid, picked charm) are guarded by known()"
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.53 harness: every 0.3.53 check
# runs again on the 0.3.54 jar; + the INV5 section)
T.rep('''"""Harness for SkyyMenu 0.3.53 (Requip inside the inventory + pocket tabs + mount Summon + the Tanning tab; tools/menu_0_3_53_patch.py).
''', '''"""Harness for SkyyMenu 0.3.54 (the Charms panel inside the inventory; tools/menu_0_3_54_patch.py).
GENERATED by tools/menu_0_3_54_patch.py from the 0.3.53 harness (edit the patch, not this file): every 0.3.53 check runs again on the
0.3.54 jar, plus
  INV5 (EXECUTED on the stand-ins with a Python stand-in of SkyyAccessories 0.5.37 acc:fn:charms): WITHOUT it 'All charms' opens the Void
       Charms page (a caption, the craft panel stays); WITH it 'All charms' = the Charms panel INSTEAD of the craft panel (no craft grid /
       binding drawn): the title (used / slots), Accessory Power, the bag grid (a not-counting copy greyed + named, slots past the limit
       "Locked slot", an unknown id = a name-only slot, every copy without metadata), the totals, the help line; pick a charm = its detail
       (TIER UP -> the next rarity, the costs "ok" / "x ... (need N more)", the status); Tier up = ONE vc:tier call with the slot, id, the
       recipe id drawn and the list's profile key; a double click within 1.5 s = no second call (the last answer again); Tier up on a
       not-counting / max charm = no call; Take out = vc:take (the pick cleared on "+"); nothing picked = no call; a DRAG of a charm from
       the bag onto the grid = ONE vc:put with the item id (the page moves nothing itself; the drag cleared; a repeat ignored); a profile
       change seen on a redraw clears the pick and says so, the next action carries the new key; a "-Your profile changed" answer clears
       the pick; pages (a charm in slot 40 = page 2); a long answer split over the two result lines; the charm-row click = the panel too;
       a bridge that answers nothing = the panel says so; Done = the craft panel again; every answer ONE page packet; the picked charm's
       name in its rarity colour (one label per rarity shown, the title-colour one when nothing is picked) - fix of critic inv5 #2.
The 0.3.53 harness text follows:
Harness for SkyyMenu 0.3.53 (Requip inside the inventory + pocket tabs + mount Summon + the Tanning tab; tools/menu_0_3_53_patch.py).
''')
T.rep('VERSION = "0.3.53"\nJAR', 'VERSION = "0.3.54"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.52.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.53.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.52.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.53.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_53_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_54_patch.py")')
T.rep('"scratch", "inv4", "menu"', '"scratch", "inv5", "menu"')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.53:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.54: the Charms panel page data (InvData), its state + fill + actions (InvPage); the rest = the version text
    "InvPage": ["+f vkey", "+f vlast", "+f vmode", "+f vnote", "+f vpage", "+f vrid", "+f vsel", "+f vshown",
                "+m charmDrop", "+m charmPick", "+m charmTake", "+m charmTier", "+m fillCharms", "+m half", "+m notCounting", "+m openCharms",
                "+m vcAct", "+m vcDone", "~c ", "~m build", "~m handleDataEvent"],
    "InvData": ["~<clinit>", "+f VC_HELP", "+f VML", "+f VN", "+f VRAR", "+f VTN", "+f VUN"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text in the setup lines (as every version)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.53"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.54"') == 1, "S VERSION")''')
HARNESS_INV5 = r"""    # ---- INV5 (0.3.54; "Start it now" 11-20, popup "Inside the inventory (Recommended)"): the Charms panel (SkyyAccessories 0.5.37 acc:fn:charms)
    FC1, SPD_, LAN_ = "Skyy_Charm_Furnace_T1", "Skyy_Talisman_Speed_Common", "Skyy_Talisman_Lantern_Common"
    for iid_ in (FC1, SPD_, LAN_):
        it_ = Ucls.allocateInstance(ITc.class_)
        E.jf(ITc.class_, "id").set(it_, iid_)
        E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
        E.jf(ITc.class_, "maxStack").setInt(it_, 1)
        amap.put(iid_, it_)
    RID2 = "Skyy_Charm_Furnace_T2_Recipe_SkyyCharm"
    CH = {"calls": [], "tok": "pk1", "ans": "+upgraded to Furnace Charm II in your Void Charms - your Furnace Charm I was used for it",
          "bag": {0: (FC1, 0, "Furnace Charm I", "Normal", "2x speed"), 3: (FC1, -5, "Furnace Charm I", "Normal", "2x speed"),
                  5: (SPD_, 4, "Speed Accessory", "Normal", "+2% Speed"), 7: ("Gone_Charm_Item", 0, "Gone Charm", "Rare", "")}}

    def f_charms(o):
        op_, tok_, arg_ = str(o[0]), str(o[2]), str(o[3])
        if op_ != "vc:list":
            CH["calls"].append((op_, tok_, arg_))
            return CH["ans"]
        ls_ = ["ok|%d|18|60|35|%s" % (len(CH["bag"]), CH["tok"])]
        for si_, (id_, ap_, nm_, rr_, fx_) in sorted(CH["bag"].items()):
            ls_.append("c|%d|%s|%d|%s|%s|%s" % (si_, id_, ap_, nm_, rr_, fx_))
        ls_ += ["t|Furnace Charm|2x speed, queue 100", "t|Speed|+2% Speed"]
        for si_, e_ in CH["bag"].items():
            if arg_ != "%d|%s" % (si_, e_[0]):
                continue
            if si_ == 0:
                ls_ += ["s|0|%s|u|%s|NORMAL - NEEDS MATERIALS|no Accessory Power|2x speed|Furnace Charm II|Unique" % (FC1, RID2),
                        "n|1|this Furnace Charm I", "n|1|64 Thorium Bar", "n|0|64 Lead Bar  (need 9 more)"]
            elif si_ == 3:
                ls_.append("s|3|%s|x||Not counting - your Furnace Charm I is better.|a second copy|2x speed||" % FC1)
            else:
                ls_.append("s|%d|%s|m||Fully upgraded - the top of its line|+4 Accessory Power|%s||" % (si_, e_[0], e_[4]))
        return "\n".join(ls_)
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    p_ = one(ev(PK, {"a": "vc"}), "INV5 All charms without SkyyAccessories 0.5.37")
    K.check(str(pg.mode) == "c" and "Void Charms" in cap_of(p_), "INV5 no acc:fn:charms: the Void Charms page as 0.3.53 (a caption), the craft panel stays (%s)" % cap_of(p_))
    BR.put("acc:fn:charms", Fn(f_charms))
    p_ = one(ev(PK, {"a": "vc"}), "INV5 All charms")
    cm, bl = (cmap(p_), binds_of(p_)) if p_ else ({}, [])
    gs_ = cm.get("#SkyyInvVxG.Slots", "")
    K.check(str(pg.mode) == "v" and "#SkyyInvCg.Slots" not in cm and "#SkyyInvRa.Slots" not in cm and not [b_ for b_ in bl if b_[1] in ("#SkyyInvCg", "#SkyyInvCq", "#SkyyInvCx1")]
            and "#SkyyInvIs.Slots" in cm, "INV5 ALL CHARMS = the Charms panel INSTEAD of the craft panel (no craft grid / binding), the bag stays")
    K.check(sval(cm, "#SkyyInvVxT.Text") == "VOID CHARMS  4 / 18" and sval(cm, "#SkyyInvVxI.Text") == "Accessory Power 35" and sval(cm, "#SkyyInvVxPn.Text") == "1 / 1",
            "INV5 the title (used / slots), Accessory Power, the page (%s, %s)" % (sval(cm, "#SkyyInvVxT.Text"), sval(cm, "#SkyyInvVxI.Text")))
    K.check(FC1 in gs_ and SPD_ in gs_ and "Furnace Charm I  - not counting" in gs_ and "a second copy - only one counts" in gs_ and "Locked slot" in gs_
            and "Gone_Charm_Item" not in gs_ and "Gone Charm" in gs_ and nometa(p_),
            "INV5 the grid: the charms, the second copy greyed 'not counting', slots past 18 'Locked slot', an unknown id name-only, no metadata")
    K.check(sval(cm, "#SkyyInvVt0.Text") == "Furnace Charm: 2x speed, queue 100" and sval(cm, "#SkyyInvVt1.Text") == "Speed: +2% Speed" and sval(cm, "#SkyyInvVt2.Text") == ""
            and sval(cm, "#SkyyInvVxN.Text") == "Pick a charm" and sval(cm, "#SkyyInvVxM0.Text") == "Click a charm to see it. Drag a charm from"
            and sval(cm, "#SkyyInvVxM1.Text") == "your bag onto the grid to put it in.",
            "INV5 ALL CHARMS TOGETHER + the help split over the two result lines (%s / %s)" % (sval(cm, "#SkyyInvVxM0.Text"), sval(cm, "#SkyyInvVxM1.Text")))
    K.check(all(x_ in [(b_[0], b_[1]) for b_ in bl] for x_ in (("SlotClicking", "#SkyyInvVxG"), ("Dropped", "#SkyyInvVxG"), ("Activating", "#SkyyInvVxTu"),
                                                               ("Activating", "#SkyyInvVxTo"), ("Activating", "#SkyyInvVxD"))),
            "INV5 the grid click + drop, Tier up, Take out, Done are bound")
    p_ = one(ev(PK, {"a": "vg", "SlotIndex": 0}), "INV5 pick Furnace Charm I")
    cm = cmap(p_) if p_ else {}
    K.check(str(pg.vsel) == "0|" + FC1 and sval(cm, "#SkyyInvVxN.Text") == "Furnace Charm I" and sval(cm, "#SkyyInvVxU.Text") == "TIER UP  ->  Unique  (Furnace Charm II)"
            and FC1 in cm.get("#SkyyInvVxS.Slots", "") and "(picked)" in cm.get("#SkyyInvVxG.Slots", ""),
            "INV5 PICK: the detail - name, TIER UP -> the next rarity (%s)" % sval(cm, "#SkyyInvVxU.Text"))
    K.check(sval(cm, "#SkyyInvVxN1.Visible") in (True, "true") and all(sval(cm, "#SkyyInvVxN%s.Visible" % k_) in (False, "false") for k_ in ("", 2, 3, 4, 5, 6))
            and all(sval(cm, "#SkyyInvVxN%d.Text" % k_) == "Furnace Charm I" for k_ in range(1, 7)),
            "INV5 FIX #2: the picked charm's name shows in its rarity colour (Normal = #VxN1 only; the others hidden, every variant the same text)")
    K.check([sval(cm, "#SkyyInvVu%d.Text" % k_) for k_ in range(4)] == ["ok   this Furnace Charm I", "ok   64 Thorium Bar", "x    64 Lead Bar  (need 9 more)", ""]
            and sval(cm, "#SkyyInvVxM0.Text") == "NORMAL - NEEDS MATERIALS", "INV5 PICK: the costs (charm first, '(need N more)') + the status (%s)" % [sval(cm, "#SkyyInvVu%d.Text" % k_) for k_ in range(4)])
    p_ = one(ev(PK, {"a": "vtu"}), "INV5 Tier up")
    K.check(CH["calls"][-1] == ("vc:tier", "pk1", "0|%s|%s" % (FC1, RID2)) and sval(cmap(p_), "#SkyyInvVxM0.Text").startswith("upgraded to Furnace Charm II"),
            "INV5 TIER UP = ONE vc:tier call (slot, id, the recipe id drawn, the list's profile key), its answer shown (%s)" % sval(cmap(p_), "#SkyyInvVxM0.Text"))
    n0_ = len(CH["calls"])
    p_ = one(ev(PK, {"a": "vtu"}), "INV5 Tier up again (double click)")
    K.check(len(CH["calls"]) == n0_ and sval(cmap(p_), "#SkyyInvVxM0.Text").startswith("upgraded to"), "INV5 a double click within 1.5 s = no second call, the last answer again")
    one(ev(PK, {"a": "vg", "SlotIndex": 3}), "INV5 pick the second copy")
    p_ = one(ev(PK, {"a": "vtu"}), "INV5 Tier up on a not-counting copy")
    K.check(len(CH["calls"]) == n0_ and "cannot tier up" in sval(cmap(p_), "#SkyyInvVxM0.Text") and sval(cmap(p_), "#SkyyInvVxU.Text") == "NOT COUNTING",
            "INV5 Tier up on a not-counting copy: no call, said so")
    one(ev(PK, {"a": "vg", "SlotIndex": 5}), "INV5 pick Speed")
    p_ = one(ev(PK, {"a": "vtu"}), "INV5 Tier up on a max charm")
    K.check(len(CH["calls"]) == n0_ and sval(cmap(p_), "#SkyyInvVxU.Text") == "MAX - nothing to tier up", "INV5 Tier up on a top-of-line charm: no call")
    CH["ans"] = "+Took out Speed Accessory - it is in your inventory now, Strawberry"
    p_ = one(ev(PK, {"a": "vto"}), "INV5 Take out")
    t0_, t1_ = sval(cmap(p_), "#SkyyInvVxM0.Text") or "", sval(cmap(p_), "#SkyyInvVxM1.Text") or ""
    K.check(CH["calls"][-1] == ("vc:take", "pk1", "5|" + SPD_) and pg.vsel is None and (t0_ + " " + t1_).split() == CH["ans"][1:].split() and t1_,
            "INV5 TAKE OUT = vc:take (slot|id), the pick cleared, the long answer over two lines (%s / %s)" % (t0_, t1_))
    n0_ = len(CH["calls"])
    p_ = one(ev(PK, {"a": "vto"}), "INV5 Take out with nothing picked")
    K.check(len(CH["calls"]) == n0_ and "Pick a charm first" in sval(cmap(p_), "#SkyyInvVxM0.Text"), "INV5 Take out / Tier up with nothing picked: no call")
    put(PK, "storage", 8, ISc(LAN_, 1))
    c0_ = E.count(PK, LAN_)
    CH["ans"] = "+Put Lantern Accessory into Void Charms"
    one(ev(PK, {"a": "sc", "g": "s", "SlotIndex": 8}), "INV5 drag start in the bag")
    p_ = one(ev(PK, {"a": "vd", "SlotIndex": 2, "SourceInventorySectionId": -2, "SourceSlotId": 8, "ItemStackId": LAN_}), "INV5 DROP a charm on the grid")
    K.check(CH["calls"][-1] == ("vc:put", "pk1", LAN_) and pg.dg is None and E.count(PK, LAN_) == c0_ and sval(cmap(p_), "#SkyyInvVxM0.Text") == "Put Lantern Accessory into Void Charms",
            "INV5 DRAG a charm from the bag onto the grid = ONE vc:put with its id; the page moves nothing itself; the drag cleared")
    n0_ = len(CH["calls"])
    one(ev(PK, {"a": "vd", "SlotIndex": 2, "SourceInventorySectionId": -2, "SourceSlotId": 8, "ItemStackId": LAN_}), "INV5 the same drop again")
    K.eq(len(CH["calls"]), n0_, "INV5 the same drop within 1.5 s = no second call")
    pg.lastMoveAt = 0
    one(ev(PK, {"a": "vg", "SlotIndex": 0}), "INV5 pick again")
    CH["tok"] = "pk2"
    p_ = one(ev(PK, {"a": "vpn"}), "INV5 a redraw after a profile switch")
    K.check(pg.vsel is None and str(pg.vkey) == "pk2" and "Your profile changed" in sval(cmap(p_), "#SkyyInvVxM0.Text"),
            "INV5 a profile switch seen on a redraw clears the pick and says so (%s)" % sval(cmap(p_), "#SkyyInvVxM0.Text"))
    one(ev(PK, {"a": "vtu"}), "INV5 Tier up after the switch")
    K.eq(len(CH["calls"]), n0_, "INV5 Tier up after a profile switch with the old pick: no call")
    one(ev(PK, {"a": "vg", "SlotIndex": 0}), "INV5 pick on the new profile")
    CH["ans"] = "-Your profile changed - pick the charm again (nothing changed)"
    p_ = one(ev(PK, {"a": "vtu"}), "INV5 Tier up on the new profile")
    K.check(CH["calls"][-1][1] == "pk2" and pg.vsel is None and sval(cmap(p_), "#SkyyInvVxM0.Text").startswith("Your profile changed"),
            "INV5 the action carries the new key; a '-Your profile changed' answer clears the pick")
    CH["bag"][40] = (SPD_, 2, "Speed Accessory", "Normal", "+2% Speed")
    p_ = one(ev(PK, {"a": "vpn"}), "INV5 page 2")
    K.check(sval(cmap(p_), "#SkyyInvVxPn.Text") == "2 / 2" and SPD_ in cmap(p_).get("#SkyyInvVxG.Slots", ""), "INV5 a charm in slot 40 = page 2 of 2")
    one(ev(PK, {"a": "vg", "SlotIndex": 13}), "INV5 pick on page 2")
    K.eq(str(pg.vsel), "40|" + SPD_, "INV5 a pick on page 2 = slot 40")
    p_ = one(ev(PK, {"a": "vpp"}), "INV5 page 1")
    K.eq(sval(cmap(p_), "#SkyyInvVxPn.Text"), "1 / 2", "INV5 back to page 1")
    p_ = one(ev(PK, {"a": "vg", "SlotIndex": 7}), "INV5 pick the Rare charm")
    cm = cmap(p_) if p_ else {}
    K.check(str(pg.vsel) == "7|Gone_Charm_Item" and sval(cm, "#SkyyInvVxN3.Visible") in (True, "true") and sval(cm, "#SkyyInvVxN3.Text") == "Gone Charm"
            and all(sval(cm, "#SkyyInvVxN%s.Visible" % k_) in (False, "false") for k_ in ("", 1, 2, 4, 5, 6)),
            "INV5 FIX #2: a Rare charm's name = the Rare-coloured label only")
    p_ = one(ev(PK, {"a": "vg", "SlotIndex": 7}), "INV5 unpick")
    cm = cmap(p_) if p_ else {}
    K.check(pg.vsel is None and sval(cm, "#SkyyInvVxN.Visible") in (True, "true") and sval(cm, "#SkyyInvVxN.Text") == "Pick a charm"
            and all(sval(cm, "#SkyyInvVxN%d.Visible" % k_) in (False, "false") for k_ in range(1, 7)),
            "INV5 FIX #2: nothing picked = the plain title-colour label ('Pick a charm')")
    p_ = one(ev(PK, {"a": "vcd"}), "INV5 Done")
    K.check(str(pg.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_) and "#SkyyInvVxG.Slots" not in cmap(p_), "INV5 Done = the craft panel again")
    p_ = one(ev(PK, {"a": "vc", "SlotIndex": 0}), "INV5 the charm row click")
    K.check(str(pg.mode) == "v" and "#SkyyInvVxG.Slots" in cmap(p_), "INV5 a click on the charm row = the Charms panel too")
    BR.put("acc:fn:charms", Fn(lambda o: None))
    p_ = one(ev(PK, {"a": "vpn"}), "INV5 a bridge that answers nothing")
    K.check(sval(cmap(p_), "#SkyyInvVxM0.Text") == "Void Charms is not on this server right now" and "Locked slot" not in cmap(p_).get("#SkyyInvVxG.Slots", ""),
            "INV5 no answer: the panel says so, an empty grid")
    BR.remove("acc:fn:charms")
    pg.shut()
    E.pump(PK)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_INV5 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
assert 'VERSION = "0.3.53"' not in T.s and 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.52.jar")' not in T.s, "0.3.54 harness: an old line is still there"
if T.dst:
    T.finish()
