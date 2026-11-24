"""Derive SkyyMenu/build_skyymenu_0.3.78.py + SkyyMenu/test_skyymenu_0.3.78.py from the SET pin SkyyMenu 0.3.77 (generated - never re-run
its patch). Run:  python tools/menu_0_3_78_patch.py   then   python SkyyMenu/build_skyymenu_0.3.78.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.78.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyySacks 0.8.43 (tools/sacks_0_8_43_patch.py: sacks:fn:upView / upAct) for the pocket Upgrades
view; with 0.8.42 the view says it needs 0.8.43 (everything else works as 0.3.77).

0.3.78 (2026-11-24, round oldmenu10) = THE LAST TWO OLD-PAGE DOORS. Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'):
"when everything is in the new system id like to disable the old menu compleatly, so instead of adding things like the full tree button, just
build it all into the new system and remove the old "Full tree""; 2026-11-24 "keep building". OLD_LEFT held storage:pocket (the pocket panel's
Upgrades = sacks:fn:openPocket, SkyySacks' own /pd Void page on that pocket), smithing:recipes (the Furnace / Tanning panel's Full page =
sacks:fn:openTannery, SkyySacks' Crafting > Tannery page) and settings:setup (Server Setup, kept on purpose). Both doors are gone:
  storage:pocket  Upgrades = a fifth inventory panel 'u' (THE POCKET UPGRADES VIEW) on the same pocket: a sub-tab row Items | Upgrade | Compact |
      Link | More (Items = back to the pocket grid; no back button), the pocket's name in its rarity colour, and an OVERVIEW column (rarity,
      Auto-compact, Shard Link, Stack refill). Upgrade = the /pd rarity Upgrade box (next rarity + its multiplier, space now -> after, every cost
      cell have / need green / red; Upgrade -> Pay / Cancel, as the page); Compact = the Auto-compact box (price, Buy -> Pay / Cancel; bought:
      Pause / Turn on); Link = the Shard Link box (price + the item lines, Buy -> Pay / Cancel; bought: Pause / Turn on); More = the page's Pick up
      all / Deposit <pocket> / Deposit every bag + the Stack refill row (Hotbar only / Full inventory / Off). Every draw = ONE sacks:fn:upView
      read (a new click token); every press = ONE sacks:fn:upAct {op, UUID, token, profile key, arg} where arg is the value the drawing showed
      (the rarity, the price, the box state, the refill word) - never a value the player did not see; Buy / Upgrade only arm the Pay (no call).
      '=' (something changed since the drawing) = the answer line + the redraw, and the same press again runs at once (the guard re-armed);
      '+' / '-' = the answer line; null = 'The Void could not do that here - nothing was done'; a press within 1.5 s = no second call; a button
      the drawing did not show = 'Nothing to do there', no call. Without SkyySacks 0.8.43 (no sacks:fn:upView / upAct) = a line naming it; no
      old page. sacks:fn:openPocket is no longer called (cmpState keeps it only as the 0.8.39 version probe).
  smithing:recipes  the Furnace / Tanning panel has no Full page (Refresh widened into the bench row): SkyySacks' Tannery page did nothing the
      panel cannot (sacks:fn:furn = CraftPage.handleProc's every branch - tools/sacks_0_8_43_patch.py SURVEY). The Tanning tab / the Right now
      Tannery row without sacks:fn:furnList (SkyySacks older than 0.8.40) = a caption naming SkyySacks 0.8.40 (was sacks:fn:openTannery = the
      old page). oldmenu10fix: the Furnace fallback (only without furnList) = a caption naming SkyySacks 0.8.40 too (no sacks:fn:openFurnace call).
New: no class / command / system / picture / lang key / setting / saved data. Fields on InvPage (usub, utok, ukey, uconf, ua, unote, ulast).
OLD_LEFT: 3 -> 1 (settings:setup = Server Setup for admins, on purpose).
ROLLBACK to 0.3.77: safe alone (nothing saved; the two old doors come back). SkyySacks 0.8.43 rolls back alone (the Upgrades view then names
0.8.43). The two may deploy apart; together = the full view.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.77.py"), os.path.join(MOD, "build_skyymenu_0.3.78.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.77.py"), os.path.join(MOD, "test_skyymenu_0.3.78.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.77"\n') and P.has("OLD_LEFT = sorted(set([") and P.has('"vc:power"') and not P.has("sacks:fn:upView"), "not the generated SkyyMenu 0.3.77 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.77: THE LAST OLD-MENU ROWS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.78: THE LAST TWO OLD-PAGE DOORS: the pocket panel's Upgrades = the in-screen POCKET UPGRADES VIEW (sub-tabs Items | Upgrade | Compact | Link |
       More; SkyySacks 0.8.43 sacks:fn:upView / upAct: the rarity upgrade, Auto-compact, Shard Link, Pick up all / Deposit, Stack refill - token
       + profile key + the shown value on every press, two presses where the /pd page asked); the Furnace / Tanning panel has no Full page;
       the Tanning fallback without SkyySacks 0.8.40 = a caption. OLD_LEFT 3 -> 1 (Server Setup stays; notes: tools/menu_0_3_78_patch.py).
       CHECKED: SkyyMenu/test_skyymenu_0.3.78.py.
0.3.77: THE LAST OLD-MENU ROWS''')
P.rep('VERSION = "0.3.77"\n', 'VERSION = "0.3.78"\n')

# ======================================================================= the panels: + 'u' THE POCKET UPGRADES VIEW
P.rep('''             "k": (SUI.Appends(), [])}   # 0.3.67: + 'k' the Requip slot picker''',
      '''             "k": (SUI.Appends(), []),   # 0.3.67: + 'k' the Requip slot picker
             "u": (SUI.Appends(), [])}   # 0.3.78: + 'u' the pocket Upgrades view (SkyySacks 0.8.43)''')
# the Furnace / Tanning panel: no Full page (the bench row takes its 116 px)
P.rep('''    fbw = pw - 90 - 6 - 110 - 8
    ap.append(("#" + ra, G_.glass_group(IV + "FxB", fbw, 36, layout="Left", anchor={"right": 8})))
    ap.append(("#" + ra, G_.glass_button(IV + "FxRf", "Refresh", "secondary", w=90, h=34, size=13)))
    ap.append(("#" + ra, G_.glass_button(IV + "FxFp", "Full page", "secondary", w=110, h=34, size=13, anchor={"left": 6})))''',
      '''    fbw = pw - 90 - 6 - 110 - 8   # 0.3.78 (oldmenu10): no Full page - the bench row keeps its width (IV_BMAX), the 116 px stay empty
    ap.append(("#" + ra, G_.glass_group(IV + "FxB", fbw, 36, layout="Left", anchor={"right": 8})))
    ap.append(("#" + ra, G_.glass_button(IV + "FxRf", "Refresh", "secondary", w=90, h=34, size=13)))
    ap.append(("#" + ra, "Group { Anchor: (Width: 116); }"))''')
P.rep('''    binds.extend([("#" + IV + "FxRf", "fxr"), ("#" + IV + "FxFp", "fxp"), ("#" + IV + "FpP", "fpp"), ("#" + IV + "FpX", "fpn"),''',
      '''    binds.extend([("#" + IV + "FxRf", "fxr"), ("#" + IV + "FpP", "fpp"), ("#" + IV + "FpX", "fpn"),''')
P.rep('''for _g in (("FxPan", "FxB", "FxRf", "FxFp", "FxS",''', '''for _g in (("FxPan", "FxB", "FxRf", "FxS",''')

UPG_PY = r'''

# 0.3.78 (oldmenu10): THE POCKET UPGRADES VIEW 'u' (the /pd Void page's side panel on one pocket - SkyySacks 0.8.43 sacks:fn:upView / upAct):
# a header (the pocket in its rarity colour, level + rarity, the sub-tab row), the BOX (title in a state colour, two text lines, six cost lines
# have / need green / red, two button rows of three) and the OVERVIEW column (rarity, Auto-compact, Shard Link, Stack refill), the answer line
IV_UF_NAMES = ["Items", "Upgrade", "Compact", "Link", "More"]
IV_UF_W, IV_UT_N, IV_UC_N, IV_UB_N, IV_UO_N = 68, 9, 6, 6, 4
IV_UF_BTN = "TextButton #SkyyInvUf{I} { Anchor: (Width: %d, Height: 30, Right: 2); {S} }" % IV_UF_W
IV_U_COLS = ["title", SUI.RARITY["Normal"], SUI.RARITY["Unique"], SUI.RARITY["Rare"], SUI.RARITY["Legendary"], SUI.RARITY["Mythic"], "gold", "green", "dim"]
IV_TXT["uHelp"] = "Upgrades for this pocket - the same as the /pd page. Pay buttons show the price first."
for _n in IV_UF_NAMES:
    assert SUI.text_width(_n, 12, bold=True) <= IV_UF_W - 10, ("0.3.78: an Upgrades sub-tab fits", _n)


def _inv_upg():
    G_ = SUI
    lab = G_.glass_label
    ph = IV_CRAFT_H[0]
    pw = IV_COL_M - 20
    TP = "#" + IV + "TopP"
    ap, binds = IV_PANELS["u"]
    pan = IV + "UxPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    ua = IV + "UxA"
    ap.append(("#" + pan, G_.glass_group(ua, pw, 34, layout="Left")))
    tw, iw = 200, 150
    tv = [SUI.keep_at0(lab(IV + "UkTv%d" % k_, "", 16, IV_U_COLS[k_], bold=True, w=tw, h=34)) for k_ in range(6)]
    hm_, kids_ = SUI.keep_holder(IV + "UkTH", tw, 34, tv)
    ap.append(("#" + ua, hm_))
    ap.extend(kids_)
    ap.append(("#" + ua, lab(IV + "UkL", "", 12, "dim", w=iw, h=34)))
    tabs_w = len(IV_UF_NAMES) * (IV_UF_W + 2)
    assert tw + iw + tabs_w <= pw, ("0.3.78: the Upgrades header fits", tw + iw + tabs_w, pw)
    ap.append(("#" + ua, G_.glass_group(IV + "UfB", tabs_w, 34, layout="Left")))
    for _t in ("FORAGING POCKET", "SMITHING POCKET"):
        assert SUI.text_width(_t, 16, bold=True) <= tw, ("0.3.78: the pocket title fits", _t)
    assert SUI.text_width("Lv 120  -  Legendary", 12) <= iw, "0.3.78: the level line fits"
    bh = ph - 20 - 34 - 4 - 20 - 4
    bd = IV + "UxBody"
    ap.append(("#" + pan, G_.glass_group(bd, pw, bh, layout="Left", anchor={"top": 4})))
    lw = 470
    L = IV + "UxL"
    ap.append(("#" + bd, G_.glass_group(L, lw, bh, role="inset", layout="Top", pad=8)))
    iw2 = lw - 16
    tv = [SUI.keep_at0(lab(IV + "UTv%d" % k_, "", 15, IV_U_COLS[k_], bold=True, w=iw2, h=22)) for k_ in range(IV_UT_N)]
    hm_, kids_ = SUI.keep_holder(IV + "UTH", iw2, 22, tv)
    ap.append(("#" + L, hm_))
    ap.extend(kids_)
    ap.append(("#" + L, lab(IV + "Ux0", "", 11, "text", w=iw2, h=16, anchor={"top": 4})))
    ap.append(("#" + L, lab(IV + "Ux1", "", 11, "text", w=iw2, h=16)))
    cw = (iw2 - 8) // 2
    for r_ in range(IV_UC_N // 2):
        row = IV + "UcR%d" % r_
        ap.append(("#" + L, G_.glass_group(row, iw2, 16, layout="Left", anchor={"top": 4 if r_ == 0 else 0})))
        for j_ in range(2):
            i_ = r_ * 2 + j_
            cv = [SUI.keep_at0(lab(IV + "Uc%dv%d" % (i_, k_), "", 11, c_, w=cw, h=16)) for k_, c_ in enumerate(("dim", "green", "red"))]
            hm_, kids_ = SUI.keep_holder(IV + "Uc%dH" % i_, cw, 16, cv, anchor={"left": 8} if j_ else None)
            ap.append(("#" + row, hm_))
            ap.extend(kids_)
    bw = (iw2 - 12) // 3
    for r_, nm_ in enumerate(("UbR", "UbS")):
        row = IV + nm_
        ap.append(("#" + L, G_.glass_group(row, iw2, 30, layout="Left", anchor={"top": 6 if r_ == 0 else 4})))
        for j_ in range(3):
            i_ = r_ * 3 + j_
            ap.append(("#" + row, G_.glass_button(IV + "Ub%d" % i_, "", "primary" if i_ == 0 else "secondary", w=bw, h=30, size=12, anchor={"left": 6} if j_ else None)))
            binds.append(("#" + IV + "Ub%d" % i_, "ub:%d" % i_))
    used = 16 + 22 + 4 + 16 + 16 + 4 + 3 * 16 + 6 + 30 + 4 + 30
    assert used <= bh, ("0.3.78: the Upgrades box fits", used, bh)
    for _t in ("Full inventory - on", "Deposit Smithing", "Deposit every bag", "Take all out", "Upgrade", "Turn on", "Cancel", "Pay"):
        assert SUI.text_width(_t, 12, bold=True) <= bw - 10, ("0.3.78: an Upgrades button text fits", _t, bw)
    ap.append(("#" + bd, "Group { Anchor: (Width: 8); }"))
    rw = pw - lw - 8
    R_ = IV + "UxR"
    ap.append(("#" + bd, G_.glass_group(R_, rw, bh, role="inset", layout="Top", pad=8)))
    rw2 = rw - 16
    ap.append(("#" + R_, lab(IV + "UxRh", "OVERVIEW", 12, "accentHi", bold=True, w=rw2, h=18)))
    for i_ in range(IV_UO_N):
        ap.append(("#" + R_, lab(IV + "Uk%d" % i_, "", 11, "dim", w=rw2, h=14, anchor={"top": 4})))
        ov = [SUI.keep_at0(lab(IV + "Uo%dv%d" % (i_, k_), "", 12, IV_U_COLS[k_], bold=True, w=rw2, h=18)) for k_ in range(IV_UT_N)]
        hm_, kids_ = SUI.keep_holder(IV + "Uo%dH" % i_, rw2, 18, ov)
        ap.append(("#" + R_, hm_))
        ap.extend(kids_)
    assert 16 + 18 + IV_UO_N * (4 + 14 + 18) <= bh, ("0.3.78: the overview fits", bh)
    for _t in ("Buy - 12,345,678 coins", "Needs Legendary", "Full inventory", "Legendary (x3)"):
        assert SUI.text_width(_t, 12, bold=True) <= rw2, ("0.3.78: an overview value fits", _t, rw2)
    ap.append(("#" + pan, lab(IV + "UxM", "", 12, "text", w=pw, h=20, anchor={"top": 4})))
    assert SUI.text_width(IV_TXT["uHelp"], 12) <= pw, "0.3.78: the help line fits"
    SUI.check_markup(IV_UF_BTN.replace("{I}", "0").replace("{S}", IV_ST_TABSEL), prefix=IV, kit_paths=True)


_inv_upg()
'''
P.rep('''IV_FX_BW = [0]
IV_FX_TXW = [0]
IV_FXW = []
_inv_furn()
''', '''IV_FX_BW = [0]
IV_FX_TXW = [0]
IV_FXW = []
_inv_furn()''' + UPG_PY)
P.rep('''for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p", "v", "t", "f", "w", "k")]:   # 0.3.60: + w; 0.3.67: + k''',
      '''for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p", "v", "t", "f", "w", "k", "u")]:   # 0.3.60: + w; 0.3.67: + k; 0.3.78: + u''')
P.rep('''F(idat, "public static final String W_HELP = %s;" % jstr(IV_TXT["wHelp"]))
''', '''F(idat, "public static final String W_HELP = %s;" % jstr(IV_TXT["wHelp"]))
F(idat, "public static final String UF_BTN = %s;" % jstr(IV_UF_BTN))          # 0.3.78: the pocket Upgrades view's sub-tabs
F(idat, "public static final String[] UF_NAMES = %s;" % jarr(IV_UF_NAMES))
F(idat, "public static final String U_HELP = %s;" % jstr(IV_TXT["uHelp"]))
''')

# ======================================================================= the Java: THE POCKET UPGRADES VIEW (fill before build; press before the handler)
P.rep('''M(ipg, r"""
public static String notCounting(int a) {''',
      r'''# ---- 0.3.78 (oldmenu10): THE POCKET UPGRADES VIEW ('u') = SkyySacks 0.8.43 sacks:fn:upView (one read per drawing = a new click token) on the
# open pocket; usub 1 Upgrade / 2 Compact / 3 Link / 4 More; ua[i] = what button i sends ("op|arg" with the value THIS drawing showed, "#conf<n>"
# arms a Pay, "#cancel"), null = no button; uconf = the Pay that is armed (1 upgrade, 2 compact, 3 link); the 1.5 s guard is per action (op)
F(ipg, "public int usub;")
F(ipg, "public String utok;")
F(ipg, "public String ukey;")
F(ipg, "public int uconf;")
F(ipg, "public String[] ua;")
F(ipg, "public String unote = \"\";")
F(ipg, "public String ulast = \"\";")
M(ipg, r"""
public static void uset(@UCB@ b, String id, int n, String t, int c) {
  for (int j = 0; j < n; j++) {
    b.set("#" + id + "v" + j + ".Text", t == null ? "" : t);
    b.set("#" + id + "v" + j + ".Visible", j == c);
  }
}""")
M(ipg, r"""
public void ubtn(@UCB@ b, int i, String text, String send) {
  b.set("#SkyyInvUb" + i + ".Visible", send != null);
  b.set("#SkyyInvUb" + i + ".Text", text == null ? "" : @PKG@.MenuUtil.clip(text, 24));
  this.ua[i] = send;
}""")
M(ipg, r"""
public static int rcol(String rank) {
  int r = toInt(rank, 0);
  return r < 0 || r > 4 ? 0 : r + 1;
}""")
M(ipg, r"""
public static String hv(String[] f) {
  return @PKG@.MenuUtil.clip(f[1], 26) + "  " + @PKG@.MenuUtil.fmt(toLong(f[2], 0L)) + " / " + @PKG@.MenuUtil.fmt(toLong(f[3], 0L));
}""")
M(ipg, r"""
public void fillUp(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  if (this.usub < 1 || this.usub > 4) this.usub = 1;
  for (int i = 0; i < @PKG@.InvData.UF_NAMES.length; i++) {
    b.appendInline("#SkyyInvUfB", @PKG@.InvData.UF_BTN.replace("{I}", String.valueOf(i)).replace("{S}", i == this.usub ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvUf" + i + ".Text", @PKG@.InvData.UF_NAMES[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyInvUf" + i, @EVD@.of("a", "uv:" + i));
  }
  this.ua = new String[6];
  for (int i = 0; i < 6; i++) ubtn(b, i, "", (String) null);
  for (int i = 0; i < 6; i++) uset(b, "SkyyInvUc" + i, 3, "", 0);
  String err = null;
  String[] ls = null;
  if (@PKG@.InvCraft.fn("sacks:fn:upView") == null || @PKG@.InvCraft.fn("sacks:fn:upAct") == null) err = "Pocket upgrades here need SkyySacks 0.8.43 - it is not on this server right now";
  else {
    ls = lines("sacks:fn:upView", new Object[] { u, this.pcat });
    if (ls == null) err = "The Void could not answer here - try again in a moment";
    else if (!ls[0].startsWith("h|ok|")) err = ls[0].startsWith("off|") ? ls[0].substring(4) : "The Void answered in a way this menu does not know";
  }
  String[] h = null;
  String[] uu = null;
  String[] kk = null;
  String[] ll = null;
  String[] rr = null;
  java.util.ArrayList cc = new java.util.ArrayList();
  java.util.ArrayList li = new java.util.ArrayList();
  if (err == null) {
    for (int i = 0; i < ls.length; i++) {
      String[] f = ls[i].split("\\|", -1);
      if (f[0].equals("h") && f.length >= 12) h = f;
      else if (f[0].equals("u") && f.length >= 10) uu = f;
      else if (f[0].equals("c") && f.length >= 5) cc.add(new String[] { f[1], f[2], f[3], f[4] });
      else if (f[0].equals("k") && f.length >= 6) kk = f;
      else if (f[0].equals("l") && f.length >= 6) ll = f;
      else if (f[0].equals("li") && f.length >= 5) li.add(new String[] { f[1], f[2], f[3], f[4] });
      else if (f[0].equals("r") && f.length >= 4) rr = f;
    }
    if (h == null || uu == null || kk == null || ll == null || rr == null) err = "The Void answered in a way this menu does not know";
  }
  String cat = this.pcat == null ? "" : this.pcat;
  b.set("#SkyyInvUk0.Text", "RARITY");
  b.set("#SkyyInvUk1.Text", "AUTO-COMPACT");
  b.set("#SkyyInvUk2.Text", "SHARD LINK");
  b.set("#SkyyInvUk3.Text", "STACK REFILL");
  if (err != null) {
    this.utok = null;
    this.uconf = 0;
    uset(b, "SkyyInvUkT", 6, cat.toUpperCase() + " POCKET", 0);
    b.set("#SkyyInvUkL.Text", "");
    uset(b, "SkyyInvUT", 9, "Pocket upgrades", 8);
    b.set("#SkyyInvUx0.Text", @PKG@.MenuUtil.clip(err, 90));
    b.set("#SkyyInvUx1.Text", "");
    for (int i = 0; i < 4; i++) uset(b, "SkyyInvUo" + i, 9, "-", 8);
    b.set("#SkyyInvUxM.Text", @PKG@.MenuUtil.clip(this.unote.length() > 0 ? this.unote : err, 110));
    this.unote = "";
    return;
  }
  this.utok = h[2];
  if (this.ukey != null && !h[3].equals(this.ukey)) { this.uconf = 0; if (this.unote.length() == 0) this.unote = "Your profile changed - this is its pocket now"; }
  this.ukey = h[3];
  int rk = rcol(h[6]);
  uset(b, "SkyyInvUkT", 6, cat.toUpperCase() + " POCKET", rk);
  b.set("#SkyyInvUkL.Text", "Lv " + h[5] + "  -  " + h[7]);
  // the OVERVIEW: the rarity (its colour), Auto-compact, Shard Link, Stack refill
  uset(b, "SkyyInvUo0", 9, h[7] + ("1".equals(h[8]) ? " - every pocket" : ""), rk);
  String ks = kk[1];
  uset(b, "SkyyInvUo1", 9, ks.equals("on") ? "On" : (ks.equals("paused") ? "Paused" : (ks.equals("buy") ? "Buy - " + @PKG@.MenuUtil.fmt(toLong(kk[2], 0L)) + " coins" : "None here")),
       ks.equals("on") ? 7 : (ks.equals("buy") ? 6 : 8));
  String lsv = ll[1];
  uset(b, "SkyyInvUo2", 9, lsv.equals("on") ? "On" : (lsv.equals("paused") ? "Paused" : (lsv.equals("buy") ? "Buy - " + @PKG@.MenuUtil.fmt(toLong(ll[2], 0L)) + " coins" : (lsv.equals("need") ? "Needs Legendary" : "None here"))),
       lsv.equals("on") ? 7 : (lsv.equals("buy") ? 6 : 8));
  int rm = toInt(rr[1], 0);
  String[] rw = new String[] { "hotbar", "full", "off" };
  String[] rl = new String[] { "Hotbar only", "Full inventory", "Off" };
  if (rm < 0 || rm > 2) rm = 0;
  uset(b, "SkyyInvUo3", 9, "1".equals(rr[2]) ? rl[rm] : rl[rm] + " (server: off)", "1".equals(rr[2]) ? 0 : 8);
  String t1 = "";
  int tc = 0;
  String x0 = "";
  String x1 = "";
  if (this.usub == 1) {   // THE RARITY UPGRADE (the page's Upgrade box)
    boolean up = uu[1].equals("up");
    boolean ready = up && "1".equals(uu[8]);
    if (!ready && this.uconf == 1) this.uconf = 0;
    if (up || uu[1].equals("bad")) {
      t1 = this.uconf == 1 ? "Pay these items for " + uu[5] + "?" : "Upgrade to " + uu[5] + " (x" + uu[6] + ")";
      tc = rcol(uu[4]);
      x0 = up ? "Space " + @PKG@.MenuUtil.fmt(toLong(h[10], 0L)) + " -> " + @PKG@.MenuUtil.fmt(toLong(uu[7], 0L)) : "";
      x1 = ready ? uu[9] : (up ? "Get the items below (Void + bag count), then Upgrade" : uu[9]);
    } else {
      t1 = uu[1].equals("omni") ? "Omni" : uu[3] + " - the top rarity";
      tc = uu[1].equals("omni") ? 5 : 4;
      x0 = uu[9];
    }
    for (int i = 0; i < cc.size() && i < 6; i++) {
      String[] f = (String[]) cc.get(i);
      uset(b, "SkyyInvUc" + i, 3, hv(f), toLong(f[2], 0L) >= toLong(f[3], 0L) ? 1 : 2);
    }
    if (ready && this.uconf == 1) { ubtn(b, 0, "Pay", "up|" + uu[2]); ubtn(b, 1, "Cancel", "#cancel"); }
    else if (ready) ubtn(b, 0, "Upgrade", "#conf1");
  } else if (this.usub == 2) {   // AUTO-COMPACT (the page's box)
    boolean buy = ks.equals("buy") && "1".equals(kk[3]);
    if (!buy && this.uconf == 2) this.uconf = 0;
    long kp = toLong(kk[2], 0L);
    if (ks.equals("buy")) { t1 = this.uconf == 2 ? "Pay " + @PKG@.MenuUtil.fmt(kp) + " coins for Auto-compact?" : "Auto-compact - " + (kp > 0L ? @PKG@.MenuUtil.fmt(kp) + " coins" : "free"); tc = 6; }
    else if (ks.equals("on")) { t1 = "Auto-compact: On"; tc = 7; }
    else if (ks.equals("paused")) { t1 = "Auto-compact: Paused"; tc = 8; }
    else { t1 = "Auto-compact"; tc = 8; }
    x0 = half(kk[5], 80, 0);
    x1 = half(kk[5], 80, 1);
    if (ks.equals("buy") && kp > 0L) {
      long hc = toLong(h[11], -1L);
      uset(b, "SkyyInvUc0", 3, "Coins  " + (hc < 0L ? "?" : @PKG@.MenuUtil.fmt(hc)) + " / " + @PKG@.MenuUtil.fmt(kp), hc < 0L || hc >= kp ? 1 : 2);
    }
    if (buy && this.uconf == 2) { ubtn(b, 0, "Pay", "cmpbuy|" + kk[2]); ubtn(b, 1, "Cancel", "#cancel"); }
    else if (buy) ubtn(b, 0, "Buy", "#conf2");
    else if ((ks.equals("on") || ks.equals("paused")) && "1".equals(kk[4])) ubtn(b, 0, ks.equals("on") ? "Pause" : "Turn on", "cmptog|" + ks);
  } else if (this.usub == 3) {   // SHARD LINK (the page's box)
    boolean buy = lsv.equals("buy") && "1".equals(ll[3]);
    if (!buy && this.uconf == 3) this.uconf = 0;
    long lp = toLong(ll[2], 0L);
    if (lsv.equals("buy")) { t1 = this.uconf == 3 ? "Pay " + @PKG@.MenuUtil.fmt(lp) + " coins + the items?" : "Shard Link - " + (lp > 0L ? @PKG@.MenuUtil.fmt(lp) + " coins" : "items only"); tc = 6; }
    else if (lsv.equals("on")) { t1 = "Shard Link: On"; tc = 7; }
    else if (lsv.equals("paused")) { t1 = "Shard Link: Paused"; tc = 8; }
    else { t1 = "Shard Link"; tc = 8; }
    x0 = half(ll[5], 80, 0);
    x1 = half(ll[5], 80, 1);
    int n = 0;
    if (lsv.equals("buy") && lp > 0L) {
      long hc = toLong(h[11], -1L);
      uset(b, "SkyyInvUc0", 3, "Coins  " + (hc < 0L ? "?" : @PKG@.MenuUtil.fmt(hc)) + " / " + @PKG@.MenuUtil.fmt(lp), hc < 0L || hc >= lp ? 1 : 2);
      n = 1;
    }
    for (int i = 0; i < li.size() && n < 6; i++) {
      String[] f = (String[]) li.get(i);
      uset(b, "SkyyInvUc" + n, 3, hv(f), toLong(f[2], 0L) >= toLong(f[3], 0L) ? 1 : 2);
      n = n + 1;
    }
    if (buy && this.uconf == 3) { ubtn(b, 0, "Pay", "lnkbuy|" + ll[2]); ubtn(b, 1, "Cancel", "#cancel"); }
    else if (buy) ubtn(b, 0, "Buy", "#conf3");
    else if (lsv.equals("on") || lsv.equals("paused")) ubtn(b, 0, lsv.equals("on") ? "Pause" : "Turn on", "lnktog|" + lsv);
  } else {   // MORE: the page's Pick up all / Deposit <pocket> / Deposit every bag + the Stack refill row
    this.uconf = 0;
    t1 = "Move items + stack refill";
    tc = 0;
    x0 = "Take every " + cat + " item out, put what you carry in, or pick how stacks refill.";
    x1 = "Stack refill: " + rl[rm] + ("1".equals(rr[2]) ? "" : " (turned off on this server for now)");
    uset(b, "SkyyInvUc0", 3, half(rr[3], 40, 0), 0);
    uset(b, "SkyyInvUc1", 3, half(rr[3], 40, 1), 0);
    ubtn(b, 0, "Take all out", "takeall|");
    ubtn(b, 1, "Deposit " + cat, "depcat|");
    ubtn(b, 2, "Deposit every bag", "depevery|");
    for (int i = 0; i < 3; i++) ubtn(b, 3 + i, rl[i] + (i == rm ? " - on" : ""), i == rm ? (String) null : "refill|" + rw[i]);
    for (int i = 0; i < 3; i++) b.set("#SkyyInvUb" + (3 + i) + ".Visible", true);   // the chosen one shows (with '- on'), it just sends nothing
  }
  uset(b, "SkyyInvUT", 9, t1, tc);
  b.set("#SkyyInvUx0.Text", @PKG@.MenuUtil.clip(x0, 90));
  b.set("#SkyyInvUx1.Text", @PKG@.MenuUtil.clip(x1, 90));
  b.set("#SkyyInvUxM.Text", @PKG@.MenuUtil.clip(this.unote.length() > 0 ? this.unote : @PKG@.InvData.U_HELP, 110));
  this.unote = "";
}""")
M(ipg, r"""
public static String notCounting(int a) {''')
P.rep('''  else if (pm == 'k') { try { fillPick(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Requip slot picker failed: " + t); } }   // 0.3.67''',
      '''  else if (pm == 'k') { try { fillPick(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Requip slot picker failed: " + t); } }   // 0.3.67
  else if (pm == 'u') { try { fillUp(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the pocket Upgrades view failed: " + t); } }   // 0.3.78''')
# the pocket tab stays selected on the Upgrades view
P.rep('''    boolean sel = i == 0 ? this.mode.equals("c") : (pk && this.mode.equals("p") && @PKG@.InvData.PCATS[i - 1].equals(this.pcat));''',
      '''    boolean sel = i == 0 ? this.mode.equals("c") : (pk && (this.mode.equals("p") || this.mode.equals("u")) && @PKG@.InvData.PCATS[i - 1].equals(this.pcat));   // 0.3.78: + the Upgrades view''')
P.rep('''  if (!c.equals(this.pcat) || !this.mode.equals("p")) { this.psel = null; this.ppage = 0; this.pquery = ""; this.penc = false; }
  this.pcat = c;
  this.mode = "p";''', '''  if (!c.equals(this.pcat) || !this.mode.equals("p")) { this.psel = null; this.ppage = 0; this.pquery = ""; this.penc = false; }
  boolean upv = this.mode.equals("u");   // 0.3.78: another pocket while the Upgrades view is open = that pocket's Upgrades view
  if (!c.equals(this.pcat)) this.uconf = 0;
  this.pcat = c;
  this.mode = upv ? "u" : "p";''')
# Upgrades = the view (no SkyySacks page); the press
P.rep('''public void pocketUp() {
  this.answered = true;
  if (this.pcat == null || this.pcat.length() == 0) { say("Pick a pocket first"); return; }
  java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");
  if (f == null) { say("Pocket upgrades need SkyySacks 0.8.39 - they are not on this server right now"); return; }   // 0.3.77: no old Void page
  Object o = null;
  try { o = f.apply(new Object[] { this.playerRef.getUuid(), this.pcat }); } catch (Throwable t) { o = null; @PKG@.MenuUtil.warn("inventory: opening the " + this.pcat + " pocket's upgrades failed: " + t); }
  if (!still()) { finish("pocket upgrades"); return; }
  say(Boolean.TRUE.equals(o) ? "Opening the " + this.pcat + " pocket" : "The pocket upgrades are not on this server right now");
}""")''', '''public void pocketUp() {
  if (this.pcat == null || this.pcat.length() == 0) { say("Pick a pocket first"); return; }
  // 0.3.78 (oldmenu10): the in-screen Upgrades view (SkyySacks 0.8.43) - no SkyySacks Void page any more
  if (@PKG@.InvCraft.fn("sacks:fn:upView") == null || @PKG@.InvCraft.fn("sacks:fn:upAct") == null) { say("Pocket upgrades here need SkyySacks 0.8.43 - they are not on this server right now"); return; }
  this.mode = "u";
  this.usub = 1;
  this.uconf = 0;
  this.unote = "";
  redraw();
}""")
# 0.3.78: a sub-tab of the Upgrades view (0 = Items = the pocket grid again)
M(ipg, r"""
public void upTab(int i) {
  if (i == 0) { this.mode = "p"; this.uconf = 0; redraw(); return; }
  if (i < 1 || i > 4) { redraw(); return; }
  if (i != this.usub) this.uconf = 0;
  this.usub = i;
  this.unote = "";
  redraw();
}""")
# 0.3.78: a button of the Upgrades view = what THIS drawing put on it (ua[i]); Buy / Upgrade arm the Pay (no call); a press = ONE
# sacks:fn:upAct {op, UUID, the view's token, its profile key, the shown value}; '=' re-arms the 1.5 s guard (the same press again runs);
# oldmenu10fix: '=' on a Pay (up / cmpbuy / lnkbuy) also disarms it - Upgrade / Buy again shows the new cost before any Pay
M(ipg, r"""
public void upPress(int i) {
  if (this.ua == null || i < 0 || i >= this.ua.length || this.ua[i] == null) { this.unote = "Nothing to do there"; redraw(); return; }
  String x = this.ua[i];
  if (x.startsWith("#conf")) { this.uconf = toInt(x.substring(5), 0); this.unote = "Check the cost, then Pay - or Cancel"; redraw(); return; }
  if (x.equals("#cancel")) { this.uconf = 0; this.unote = ""; redraw(); return; }
  if (@PKG@.InvCraft.fn("sacks:fn:upAct") == null) { this.unote = "Pocket upgrades here need SkyySacks 0.8.43 - nothing was done"; redraw(); return; }
  if (this.utok == null || this.ukey == null || this.ukey.length() == 0) { this.unote = "Your profile is not settled yet - try again in a moment"; redraw(); return; }
  int bar = x.indexOf('|');
  if (bar <= 0) { this.unote = "Nothing to do there"; redraw(); return; }
  String key = "ua:" + x.substring(0, bar);   // per action, not per value: a double click on Pause never also presses the redrawn Turn on
  if (dup(key)) { this.unote = this.ulast.length() > 0 ? this.ulast : "Double click ignored - wait a moment to click again"; redraw(); return; }
  moved(key);
  Object o = call("sacks:fn:upAct", new Object[] { x.substring(0, bar), this.playerRef.getUuid(), this.utok, this.ukey, x.substring(bar + 1) });
  String r = o == null ? "-The Void could not do that here - nothing was done" : String.valueOf(o);
  String op = x.substring(0, bar);
  if (r.startsWith("=")) {   // nothing was done: the redraw shows what changed, the same press again runs at once
    this.lastMove = null;
    // a Pay never stays armed on a changed cost: Upgrade / Buy again shows the new one first (never send a value the player did not see)
    if (op.equals("up") || op.equals("cmpbuy") || op.equals("lnkbuy")) this.uconf = 0;
  }
  else this.uconf = 0;
  this.ulast = bare(r);
  this.unote = this.ulast;
  redraw();
}""")''')
P.rep('''    if (a.equals("pup")) { pocketUp(); return; }''', '''    if (a.equals("pup")) { pocketUp(); return; }
    if (a.startsWith("uv:")) { upTab(toInt(a.substring(3), -1)); return; }   // 0.3.78: the pocket Upgrades view
    if (a.startsWith("ub:")) { upPress(toInt(a.substring(3), -1)); return; }''')

# ======================================================================= the Tannery door: no Full page, the fallback = a caption
P.rep('''public void tanning() {
  this.answered = true;
  java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");
  Object o = null;
  try { if (f != null) o = f.apply(this.playerRef.getUuid()); } catch (Throwable t) { o = null; @PKG@.MenuUtil.warn("inventory: opening the Tannery failed: " + t); }
  if (Boolean.TRUE.equals(o)) {
    if (!still()) { finish("bridge Tannery"); return; }
    say("Opening the Tannery");
    return;
  }
  say(f == null ? "The Tannery needs SkyySacks 0.8.38 - it is not on this server right now" : "The Tannery could not open right now - try again");   // 0.3.77: no old Crafting page
}""")''', '''public void tanning() {
  // 0.3.78 (oldmenu10): the Tanning panel needs SkyySacks 0.8.40 (sacks:fn:furnList); no SkyySacks Tannery page any more (sacks:fn:openTannery)
  say("The Tanning panel needs SkyySacks 0.8.40 - it is not on this server right now");
}""")''')
# oldmenu10fix: the Furnace fallback (no sacks:fn:furnList = SkyySacks before 0.8.40) = a caption too; no sacks:fn:openFurnace call
# left (Skyy 11-22 "disable the old menu compleatly"). openFn stays as a helper with no caller.
FURN_CAP = 'say("The Furnace panel needs SkyySacks 0.8.40 - it is not on this server right now");'
P.rep('''  if (bk.equals("Furnace")) { openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace"); return; }''',
      '''  if (bk.equals("Furnace")) { ''' + FURN_CAP + ''' return; }   // oldmenu10fix: no SkyySacks Furnace page''')
P.rep('''    if ("furn:Tannery".equals(t)) { tanning(); return; }
    openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace");
    return;''', '''    if ("furn:Tannery".equals(t)) { tanning(); return; }
    ''' + FURN_CAP + '''   // oldmenu10fix: no SkyySacks Furnace page
    return;''')
P.rep('''M(ipg, r"""
public void furnFull() {
  if ("Tannery".equals(this.fbench)) { tanning(); return; }
  openFn("sacks:fn:openFurnace", "sacks:fn:openFurnace", "the Furnace");
}""")
''', '''# 0.3.78 (oldmenu10): the Furnace / Tanning panel's Full page (furnFull) is gone - the panel does all those pages did
''')
P.rep('''    if (a.equals("fxp")) { furnFull(); return; }
''', '''    // 0.3.78 (oldmenu10): no Full page on the Furnace / Tanning panel (a forged one = the default caption)
''')
P.rep('''  if (ls == null) err = (@PKG@.InvCraft.fn("sacks:fn:furnList") == null ? "The " + lbl + " is not on this server right now - Full page opens the old one" : "The " + lbl + " did not answer - try Refresh");''',
      '''  if (ls == null) err = (@PKG@.InvCraft.fn("sacks:fn:furnList") == null ? "The " + lbl + " panel needs SkyySacks 0.8.40 - it is not on this server right now" : "The " + lbl + " did not answer - try Refresh");''')
P.rep('''  if (h != null && h.length < 16) { h = null; err = "The " + lbl + " answered in a way this menu does not know - use Full page"; }''',
      '''  if (h != null && h.length < 16) { h = null; err = "The " + lbl + " answered in a way this menu does not know - try Refresh"; }''')

# ======================================================================= the ratchet: OLD_LEFT = Server Setup only
P.rep('''OLD_LEFT = sorted(set([
    ("storage", "pocket"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.78 (oldmenu10): storage:pocket (Upgrades = the in-screen pocket Upgrades view - SkyySacks 0.8.43 sacks:fn:upView / upAct; no
# sacks:fn:openPocket call left) and smithing:recipes (the Furnace / Tanning panel has no Full page; the Tanning fallback = a caption, no
# sacks:fn:openTannery call left) are gone. Left: Server Setup (admins), on purpose.
OLD_LEFT = sorted(set([
    ("settings", "setup")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.78: no system / command / class"
_i = P.s.index
BUILD_INV = 'public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {' + chr(10) + '  this.pref = ref;' + chr(10) + '  this.pst = st;' + chr(10) + '  String lk = @PKG@.InvData.LK;'
assert _i('F(ipg, "public String[] ua;")') < _i("public void fillUp(@UCB@ b, @UEB@ ev)") < _i(BUILD_INV) \
    < _i("public void upPress(int i)") < _i("public void handleDataEvent(@REF@ ref, @ST@ st, String d) {\n  String a = val(d, \"a\");\n  if (a == null) a = \"\";\n  this.answered = false;"), \
    "0.3.78: fields + fillUp before build, upPress before the handler"
assert _i("public static String half(String t, int n, int part)") < _i("public void fillUp(@UCB@ b, @UEB@ ev)"), "0.3.78: half before fillUp"
_new = P.s[P.s.index("# ================= 0.3.50 THE INVENTORY SCREEN"):P.s.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")]
for _old in ('InvCraft.fn("sacks:fn:openPocket");', 'InvCraft.fn("sacks:fn:openTannery")', '"sacks:fn:openTannery"', "Full page opens the old one", "use Full page",
             '"Full page", "secondary"', "furnFull()", 'a.equals("fxp")', '"sacks:fn:openFurnace"'):
    assert _old not in _new, "0.3.78: no old door left: " + _old
P.finish()

# ======================================================================= the HARNESS (every 0.3.77 check runs again on the 0.3.78 jar, plus OLD10)
HARNESS_OLD10_STATIC = r'''    # ---- OLD10 (0.3.78; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the last two SkyySacks doors are gone
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("storage", "pocket"), ("smithing", "recipes")]) and left2_ == set([("settings", "setup")]),
            "OLD10 RATCHET OLD_LEFT lost storage:pocket + smithing:recipes; left = Server Setup only (on purpose) (%d -> %d: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
    nw10_ = g[g.index("# ================= 0.3.50 THE INVENTORY SCREEN"):g.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")]
    K.check('InvCraft.fn("sacks:fn:openPocket");' not in nw10_ and '"sacks:fn:openTannery"' not in nw10_ and 'G_.glass_button(IV + "FxFp"' not in nw10_
            and 'a.equals("fxp")' not in nw10_ and "furnFull()" not in nw10_ and "Full page opens the old one" not in nw10_ and '"sacks:fn:openFurnace"' not in nw10_,
            "OLD10 STATIC no sacks:fn:openPocket / openTannery / openFurnace call, no Full page on the Furnace / Tanning panel (markup, binding, handler, text)")
    K.check('Object o = call("sacks:fn:upAct", new Object[] { x.substring(0, bar), this.playerRef.getUuid(), this.utok, this.ukey, x.substring(bar + 1) });' in g
            and 'ls = lines("sacks:fn:upView", new Object[] { u, this.pcat });' in g and "this.utok = h[2];" in g and "this.ukey = h[3];" in g
            and 'if (r.startsWith("=")) {   // nothing was done' in g and 'if (op.equals("up") || op.equals("cmpbuy") || op.equals("lnkbuy")) this.uconf = 0;' in g
            and "ScheduledFuture up" not in g,
            "OLD10 STATIC the Upgrades view reads sacks:fn:upView per drawing and acts through sacks:fn:upAct with the drawing's token + profile key + shown value; '=' re-arms; no timer")
    K.check(all(("0.3.78: %s" % t_) in g for t_ in ("an Upgrades sub-tab fits", "the Upgrades header fits", "the pocket title fits", "the Upgrades box fits",
                                                    "an Upgrades button text fits", "the overview fits", "an overview value fits", "the help line fits")),
            "OLD10 STATIC the build asserts every part of the Upgrades view fits")
'''

HARNESS_UPG = r'''    # ---- OLD10 (0.3.78): Upgrades = the in-screen POCKET UPGRADES VIEW (SkyySacks 0.8.43 sacks:fn:upView / upAct; stand-ins = the
    # tools/sacks_0_8_43_patch.py contract); sacks:fn:openPocket (still on the bridge here) is never called
    UPV = {"n": 0, "tok": None, "key": "pk6", "rar": 0, "ready": 1, "kst": "buy", "kp": 73500, "lst": "need", "lp": 370000, "rf": 0,
           "reads": [], "acts": [], "ans": None, "null": False, "off": None}
    RN_ = ["Normal", "Unique", "Rare", "Legendary", "Omni"]

    def f_upv(o):
        UPV["reads"].append((str(o[0]), str(o[1])))
        if UPV["off"]:
            return UPV["off"]
        UPV["n"] += 1
        UPV["tok"] = "ut%d" % UPV["n"]
        r_ = UPV["rar"]
        L_ = ["h|ok|%s|%s|%s|12|%d|%s|0|240|6720|1000000" % (UPV["tok"], UPV["key"], str(o[1]), r_, RN_[r_])]
        if r_ < 3:
            L_.append("u|up|%d|%s|%d|%s|%s|13440|%d|Pay the items below to upgrade" % (r_, RN_[r_], r_ + 1, RN_[r_ + 1], ["1.0", "1.5", "2.0", "3.0"][r_ + 1], UPV["ready"]))
        else:
            L_.append("u|top|3|Legendary|3|Legendary|3.0|-1|0|Legendary - the top rarity. Omni comes when all six categories are Legendary (1 of 6 now)")
        L_ += ["c|Rock_Stone_Cobble|Cobblestone|500|400", "c|Ore_Copper|Copper Ore|%d|250" % (300 if UPV["ready"] else 100)]
        L_.append("k|%s|%d|1|1|100 of an item -> 1 Enchanted once its recipe is unlocked in Collections." % (UPV["kst"], UPV["kp"]))
        lt_ = "Late game: shard items go straight into this pocket, no Collect. Needs this pocket at Legendary first." if UPV["lst"] == "need" else "Shard items then go straight in."
        L_.append("l|%s|%d|%d|1|%s" % (UPV["lst"], UPV["lp"], 1 if UPV["lst"] == "buy" else 0, lt_))
        if UPV["lst"] == "buy":
            L_ += ["li|Skyy_Ench_Cobblestone|Enchanted Cobblestone|64|64", "li|Skyy_Ench_Sandstone|Enchanted Sandstone|40|32", "li|Skyy_Ench_Shale|Enchanted Shale|16|16"]
        L_.append("r|%d|1|A hotbar stack you use tops back up from the Void every 2 seconds. Benches and inventory crafting use the Void too." % UPV["rf"])
        return "\n".join(L_)

    def f_upa(o):
        a_ = tuple(str(x_) for x_ in o)
        UPV["acts"].append(a_)
        if UPV["null"]:
            return None
        if UPV["ans"] is not None:
            x_ = UPV["ans"]
            UPV["ans"] = None
            return x_
        if a_[2] != UPV["tok"]:
            return "=That click was for an older copy of this view - nothing was done"
        if a_[0] == "up":
            UPV["rar"] += 1
            return "+Mining is now " + RN_[UPV["rar"]]
        if a_[0] == "cmpbuy":
            UPV["kst"] = "on"
            return "+Mining now has Auto-compact (%s coins)" % a_[4]
        if a_[0] == "cmptog":
            UPV["kst"] = "paused" if a_[4] == "on" else "on"
            return "+Auto-compact paused for Mining" if a_[4] == "on" else "+Auto-compact is on again for Mining"
        if a_[0] == "lnkbuy":
            UPV["lst"] = "on"
            return "+The Mining pocket now has Shard Link"
        if a_[0] == "refill":
            UPV["rf"] = ["hotbar", "full", "off"].index(a_[4])
            return "+Stack refill: " + ["Hotbar only", "Full inventory", "Off"][UPV["rf"]]
        return "+Picked up 5 items" if a_[0] == "takeall" else "+Deposited 3 items"
    vis_ = lambda c_, k_: sval(c_, "#SkyyInv%s.Visible" % k_) in (True, "true")
    BR.put("sacks:fn:upView", Fn(f_upv))
    p_ = one(ev(PT, {"a": "pup"}), "OLD10 UPG Upgrades without sacks:fn:upAct (0.8.42 has neither)")
    K.check("need SkyySacks 0.8.43" in cap_of(p_) and str(pgP.mode) == "p" and not UPV["reads"], "OLD10 UPG with only one of the two keys = a caption naming SkyySacks 0.8.43, no read (%s)" % cap_of(p_))
    BR.put("sacks:fn:upAct", Fn(f_upa))
    p_ = one(ev(PT, {"a": "pup"}), "OLD10 UPG Upgrades")
    cm = cmap(p_) if p_ else {}
    K.notes.append("OLD10 the first Upgrade box: %s" % [(k_, sval(cm, k_)) for k_ in ("#SkyyInvUTv2.Text", "#SkyyInvUx0.Text", "#SkyyInvUc0v1.Text", "#SkyyInvUb0.Text", "#SkyyInvUo0v1.Text", "#SkyyInvUo1v6.Text", "#SkyyInvUo2v8.Text", "#SkyyInvUo3v0.Text", "#SkyyInvUkL.Text")])
    K.check(str(pgP.mode) == "u" and int(pgP.usub) == 1 and UPV["reads"] == [(u6, "Mining")] and not UPV["acts"] and not CMP["open"] and PT.pm.getCustomPage() == pgP,
            "OLD10 UPG Upgrades = the view INSIDE the inventory: ONE upView read (the pocket), no act, no SkyySacks page (openPocket never called)")
    K.check(sval(cm, "#SkyyInvUkTv1.Text") == "MINING POCKET" and vis_(cm, "UkTv1") and not vis_(cm, "UkTv0") and sval(cm, "#SkyyInvUkL.Text") == "Lv 12  -  Normal"
            and TSEL_ in mk_of(p_, "SkyyInvUf1") and TSEL_ not in mk_of(p_, "SkyyInvUf0") and [sval(cm, "#SkyyInvUf%d.Text" % k_) for k_ in range(5)] == ["Items", "Upgrade", "Compact", "Link", "More"]
            and TSEL_ in mk_of(p_, "SkyyInvPt1"),
            "OLD10 UPG the header: the pocket in its rarity colour (Normal), level + rarity, the sub-tab row (Upgrade selected), the pocket tab stays selected")
    K.check(sval(cm, "#SkyyInvUTv2.Text") == "Upgrade to Unique (x1.5)" and vis_(cm, "UTv2") and sval(cm, "#SkyyInvUx0.Text") == "Space 6,720 -> 13,440"
            and sval(cm, "#SkyyInvUc0v1.Text") == "Cobblestone  500 / 400" and vis_(cm, "Uc0v1") and vis_(cm, "Uc1v1") and vis_(cm, "Ub0") and sval(cm, "#SkyyInvUb0.Text") == "Upgrade"
            and not vis_(cm, "Ub1") and sval(cm, "#SkyyInvUo0v1.Text") == "Normal" and sval(cm, "#SkyyInvUo1v6.Text") == "Buy - 73,500 coins" and vis_(cm, "Uo1v6")
            and sval(cm, "#SkyyInvUo2v8.Text") == "Needs Legendary" and sval(cm, "#SkyyInvUo3v0.Text") == "Hotbar only",
            "OLD10 UPG the Upgrade box: the next rarity in ITS colour + multiplier, space now -> after, the cost cells green, Upgrade; the overview (rarity colour, Buy gold, Needs Legendary, refill)")
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 UPG Upgrade (arms the Pay)")
    cm = cmap(p_) if p_ else {}
    K.check(not UPV["acts"] and int(pgP.uconf) == 1 and sval(cm, "#SkyyInvUb0.Text") == "Pay" and sval(cm, "#SkyyInvUb1.Text") == "Cancel" and vis_(cm, "Ub1")
            and sval(cm, "#SkyyInvUTv2.Text") == "Pay these items for Unique?", "OLD10 UPG Upgrade = Pay / Cancel with the cost (no call - two presses as the /pd page)")
    p_ = one(ev(PT, {"a": "ub:1"}), "OLD10 UPG Cancel")
    K.check(not UPV["acts"] and int(pgP.uconf) == 0 and sval(cmap(p_), "#SkyyInvUb0.Text") == "Upgrade", "OLD10 UPG Cancel = back, no call")
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG Upgrade again")
    tok_ = UPV["tok"]
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 UPG Pay")
    cm = cmap(p_) if p_ else {}
    K.check(UPV["acts"] == [("up", u6, tok_, "pk6", "0")] and str(sval(cm, "#SkyyInvUxM.Text")).startswith("Mining is now Unique") and sval(cm, "#SkyyInvUTv3.Text") == "Upgrade to Rare (x2.0)"
            and int(pgP.uconf) == 0, "OLD10 UPG Pay = ONE upAct {up, UUID, the drawing's token, its profile key, the rarity it showed}; the answer + ONE redraw (Unique -> Rare now)")
    pgP.lastMoveAt = 0
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG arm again")
    UPV["ans"] = "=Already upgraded - Mining is Rare now (nothing was taken)"
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 UPG Pay answered '='")
    K.check(str(sval(cmap(p_), "#SkyyInvUxM.Text")).startswith("Already upgraded") and int(pgP.uconf) == 0 and sval(cmap(p_), "#SkyyInvUb0.Text") == "Upgrade"
            and not vis_(cmap(p_), "Ub1"),
            "OLD10 UPG (fix) '=' on a Pay = the answer line + the Pay DISARMED: the redraw shows Upgrade, never a Pay for a cost the player did not see")
    n_ = len(UPV["acts"])
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 UPG the same press again at once (a queued double click)")
    cm = cmap(p_) if p_ else {}
    K.check(len(UPV["acts"]) == n_ and int(pgP.uconf) == 1 and sval(cm, "#SkyyInvUb0.Text") == "Pay"
            and "Pay these items for Rare?" in [sval(cm, "#SkyyInvUTv%d.Text" % k_) for k_ in range(9)],
            "OLD10 UPG (fix) after '=' a queued click on the same button only re-arms the Pay with the NEW cost shown - no call")
    tok_ = UPV["tok"]
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 UPG Pay on the cost now shown")
    K.check(len(UPV["acts"]) == n_ + 1 and UPV["acts"][-1][2] == tok_ and str(sval(cmap(p_), "#SkyyInvUxM.Text")).startswith("Mining is now Rare"),
            "OLD10 UPG after '=' the Pay on the shown cost runs AT ONCE (no 1.5 s wait) with the redrawn token (%s)" % (UPV["acts"][-1:],))
    pgP.lastMoveAt = 0
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG arm (null)")
    UPV["null"] = True
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 UPG a null answer")
    K.check(str(sval(cmap(p_), "#SkyyInvUxM.Text")) == "The Void could not do that here - nothing was done", "OLD10 UPG null = 'could not do that here - nothing was done'")
    UPV["null"] = False
    n_ = len(UPV["acts"])
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG arm (double click)")
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG the same press within 1.5 s")
    K.eq(len(UPV["acts"]), n_, "OLD10 UPG a second press of the same action within 1.5 s = no second call")
    p_ = one(ev(PT, {"a": "ub:4"}), "OLD10 UPG a button the drawing did not show")
    K.check(len(UPV["acts"]) == n_ and sval(cmap(p_), "#SkyyInvUxM.Text") == "Nothing to do there", "OLD10 UPG a forged button = 'Nothing to do there', no call")
    UPV["ready"] = 0
    p_ = one(ev(PT, {"a": "uv:1"}), "OLD10 UPG short items")
    cm = cmap(p_) if p_ else {}
    K.check(not vis_(cm, "Ub0") and vis_(cm, "Uc1v2") and sval(cm, "#SkyyInvUc1v2.Text") == "Copper Ore  100 / 250" and int(pgP.uconf) == 0,
            "OLD10 UPG items short = the cost line red, no Upgrade button (the Pay disarmed)")
    UPV["ready"] = 1
    # Compact
    pgP.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "uv:2"}), "OLD10 CMP the Compact tab")
    cm = cmap(p_) if p_ else {}
    K.check(int(pgP.usub) == 2 and TSEL_ in mk_of(p_, "SkyyInvUf2") and sval(cm, "#SkyyInvUTv6.Text") == "Auto-compact - 73,500 coins" and vis_(cm, "UTv6")
            and sval(cm, "#SkyyInvUc0v1.Text") == "Coins  1,000,000 / 73,500" and sval(cm, "#SkyyInvUb0.Text") == "Buy", "OLD10 CMP the box: price gold, the coins line green, Buy")
    one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Buy (arms)")
    n_ = len(UPV["acts"])
    tok_ = UPV["tok"]
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Pay")
    K.check(UPV["acts"][n_:] == [("cmpbuy", u6, tok_, "pk6", "73500")] and str(sval(cmap(p_), "#SkyyInvUTv7.Text")) == "Auto-compact: On",
            "OLD10 CMP Pay = ONE upAct cmpbuy with the price the drawing showed; On (green) after (%s)" % UPV["acts"][n_:])
    pgP.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Pause")
    K.check(UPV["acts"][-1][0] == "cmptog" and UPV["acts"][-1][4] == "on" and sval(cmap(p_), "#SkyyInvUb0.Text") == "Turn on", "OLD10 CMP Pause = cmptog with the shown state 'on'")
    n_ = len(UPV["acts"])
    one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Turn on within 1.5 s")
    K.eq(len(UPV["acts"]), n_, "OLD10 CMP a double click = one toggle (the guard is per action, not per value)")
    pgP.lastMoveAt = 0
    UPV["ans"] = "=Auto-compact changed since this view - nothing was done"
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Turn on answered '='")
    K.check(len(UPV["acts"]) == n_ + 1 and str(sval(cmap(p_), "#SkyyInvUxM.Text")).startswith("Auto-compact changed") and sval(cmap(p_), "#SkyyInvUb0.Text") == "Turn on",
            "OLD10 CMP (fix) '=' on a toggle = the answer line, the same button on the redraw")
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP the same toggle again at once")
    K.check(len(UPV["acts"]) == n_ + 2 and UPV["acts"][-1][0] == "cmptog" and UPV["acts"][-1][4] == "paused" and UPV["kst"] == "on",
            "OLD10 CMP (fix) after '=' on a toggle (no money) the same press again runs AT ONCE (%s)" % (UPV["acts"][-1:],))
    pgP.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Pause (back to paused)")
    n_ = len(UPV["acts"])
    pgP.lastMoveAt = 0
    UPV["kst"] = "buy"
    p_ = one(ev(PT, {"a": "uv:2"}), "OLD10 CMP buyable again (stand-in)")
    one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Buy (arms)")
    UPV["ans"] = "=The price is now 80,000 coins - nothing was taken"
    UPV["kp"] = 80000
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Pay answered '=' (price changed)")
    cm = cmap(p_) if p_ else {}
    K.check(len(UPV["acts"]) == n_ + 1 and int(pgP.uconf) == 0 and sval(cm, "#SkyyInvUb0.Text") == "Buy" and sval(cm, "#SkyyInvUTv6.Text") == "Auto-compact - 80,000 coins",
            "OLD10 CMP (fix) '=' on the Pay = disarmed, Buy with the NEW price shown (no Pay at a price the player did not see)")
    one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Buy again (arms on the new price)")
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 CMP Pay the new price")
    K.check(UPV["acts"][-1][0] == "cmpbuy" and UPV["acts"][-1][4] == "80000" and UPV["kst"] == "on", "OLD10 CMP (fix) the Pay after re-arming sends the price now shown (%s)" % (UPV["acts"][-1:],))
    UPV["kp"] = 73500
    # Link
    p_ = one(ev(PT, {"a": "uv:3"}), "OLD10 LNK the Link tab (needs Legendary)")
    cm = cmap(p_) if p_ else {}
    K.check(not vis_(cm, "Ub0") and "Legendary" in str(sval(cm, "#SkyyInvUx0.Text")) + str(sval(cm, "#SkyyInvUx1.Text")) and vis_(cm, "UTv8"), "OLD10 LNK below Legendary: the late-game note, no button")
    n_ = len(UPV["acts"])
    one(ev(PT, {"a": "ub:0"}), "OLD10 LNK a forged Buy")
    K.eq(len(UPV["acts"]), n_, "OLD10 LNK a forged Buy = no call")
    UPV["lst"] = "buy"
    p_ = one(ev(PT, {"a": "uv:3"}), "OLD10 LNK buyable")
    cm = cmap(p_) if p_ else {}
    K.check(sval(cm, "#SkyyInvUTv6.Text") == "Shard Link - 370,000 coins" and sval(cm, "#SkyyInvUc1v1.Text") == "Enchanted Cobblestone  64 / 64" and vis_(cm, "Uc3v1")
            and sval(cm, "#SkyyInvUb0.Text") == "Buy", "OLD10 LNK the price, the coins + item lines, Buy")
    one(ev(PT, {"a": "ub:0"}), "OLD10 LNK Buy (arms)")
    tok_ = UPV["tok"]
    p_ = one(ev(PT, {"a": "ub:0"}), "OLD10 LNK Pay")
    K.check(UPV["acts"][-1] == ("lnkbuy", u6, tok_, "pk6", "370000") and sval(cmap(p_), "#SkyyInvUTv7.Text") == "Shard Link: On",
            "OLD10 LNK Pay = ONE upAct lnkbuy with the shown price (%s)" % (UPV["acts"][-1:],))
    # More
    p_ = one(ev(PT, {"a": "uv:4"}), "OLD10 MORE the More tab")
    cm = cmap(p_) if p_ else {}
    K.check([sval(cm, "#SkyyInvUb%d.Text" % k_) for k_ in range(6)] == ["Take all out", "Deposit Mining", "Deposit every bag", "Hotbar only - on", "Full inventory", "Off"]
            and all(vis_(cm, "Ub%d" % k_) for k_ in range(6)), "OLD10 MORE Pick up all / Deposit <pocket> / Deposit every bag + the refill row (the choice marked '- on')")
    for k_, want_ in ((0, ("takeall", "")), (1, ("depcat", "")), (2, ("depevery", "")), (4, ("refill", "full"))):
        pgP.lastMoveAt = 0
        tok_ = UPV["tok"]
        p_ = one(ev(PT, {"a": "ub:%d" % k_}), "OLD10 MORE button %d" % k_)
        K.check((UPV["acts"][-1][0], UPV["acts"][-1][4]) == want_ and UPV["acts"][-1][2] == tok_, "OLD10 MORE button %d = upAct %s with the drawing's token" % (k_, want_))
    n_ = len(UPV["acts"])
    p_ = one(ev(PT, {"a": "ub:4"}), "OLD10 MORE the chosen refill")
    K.check(len(UPV["acts"]) == n_ and sval(cmap(p_), "#SkyyInvUb4.Text") == "Full inventory - on", "OLD10 MORE the refill you have = no call")
    # profile switch, off, another pocket, Items
    UPV["key"] = "pk7"
    p_ = one(ev(PT, {"a": "uv:1"}), "OLD10 UPG a profile switch")
    K.check("Your profile changed" in str(sval(cmap(p_), "#SkyyInvUxM.Text")), "OLD10 UPG a profile switch seen on a redraw is said")
    pgP.lastMoveAt = 0
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG arm on the new profile")
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG Pay on the new profile")
    K.eq(UPV["acts"][-1][3], "pk7", "OLD10 UPG the next press carries the new profile key")
    UPV["off"] = "off|The Void is paused (profile loading or switching) - try again in a moment"
    p_ = one(ev(PT, {"a": "uv:2"}), "OLD10 UPG the Void paused")
    cm = cmap(p_) if p_ else {}
    n_ = len(UPV["acts"])
    K.check("Void is paused" in str(sval(cm, "#SkyyInvUx0.Text")) and not any(vis_(cm, "Ub%d" % k_) for k_ in range(6)), "OLD10 UPG off = the reason, no button")
    pgP.lastMoveAt = 0
    one(ev(PT, {"a": "ub:0"}), "OLD10 UPG a press while off")
    K.eq(len(UPV["acts"]), n_, "OLD10 UPG ... a press = no call")
    UPV["off"] = None
    p_ = one(ev(PT, {"a": "pt:2"}), "OLD10 UPG another pocket")
    K.check(str(pgP.mode) == "u" and UPV["reads"][-1] == (u6, "Foraging") and sval(cmap(p_), "#SkyyInvUkTv%d.Text" % (UPV["rar"] + 1)) == "FORAGING POCKET",
            "OLD10 UPG another pocket tab = that pocket's Upgrades view")
    p_ = one(ev(PT, {"a": "uv:0"}), "OLD10 UPG Items")
    K.check(str(pgP.mode) == "p" and "#SkyyInvPg.Slots" in cmap(p_), "OLD10 UPG Items = the pocket grid again")
    BR.remove("sacks:fn:upAct")
    p_ = one(ev(PT, {"a": "pup"}), "OLD10 UPG Upgrades without upAct")
    K.check("need SkyySacks 0.8.43" in cap_of(p_) and str(pgP.mode) == "p", "OLD10 UPG without sacks:fn:upAct = a caption naming SkyySacks 0.8.43")
    K.check(not CMP["open"], "OLD10 UPG sacks:fn:openPocket was never called")
    K.notes.append("OLD10 ran: %d upView reads, %d upAct calls" % (len(UPV["reads"]), len(UPV["acts"])))
    BR.remove("sacks:fn:upView")
'''


def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.77 (the last old-menu rows - the charm rows' Bag + Power tab, the Void / Tannery / Trees fallbacks;''',
      '''"""Harness for SkyyMenu 0.3.78 (the last two old-page doors - the pocket Upgrades view, no Furnace / Tanning Full page; tools/menu_0_3_78_patch.py,
round oldmenu10). GENERATED by tools/menu_0_3_78_patch.py from the 0.3.77 harness (edit the patch, not this file): every 0.3.77 check runs
again on the 0.3.78 jar (CRAFT / INV4: the Tanning fallback names SkyySacks 0.8.40; OLD9 FALL: Upgrades without SkyySacks 0.8.43 names it;
INV6: Upgrades = the view, never openPocket; INV7: a forged Full page opens nothing; OLD9's ratchet = 'stays gone'), plus
  OLD10 STATIC  the ratchet: OLD_LEFT 3 -> 1 (Server Setup only); no openPocket / openTannery call, no Full page on the Furnace panel; the view
                reads upView per drawing and acts with its token + profile key + the shown value; '=' re-arms; the build asserts every part fits
       UPG      Upgrades = the view inside the inventory (ONE upView read, the pocket tab stays selected, no SkyySacks page): the header in the
                rarity colour, the sub-tab row, the box (next rarity in its colour, space, cost cells green / red), the overview; Upgrade =
                Pay / Cancel (no call); Pay = ONE upAct {up, UUID, token, key, shown rarity}; '=' then the same press again at once runs; null
                said; a double press = one call; a forged button = no call; items short = red + no button; Compact Buy -> Pay (cmpbuy, shown
                price) / Pause (cmptog, shown state, one toggle per double click); Link below Legendary = no button, Buy -> Pay (lnkbuy); More =
                Pick up all / Deposit <pocket> / Deposit every bag / refill (the chosen one sends nothing); a profile switch said + the new key
                sent; off = no button; another pocket stays on the view; Items = the grid; without SkyySacks 0.8.43 = a caption
The 0.3.77 harness text follows:
Harness for SkyyMenu 0.3.77 (the last old-menu rows - the charm rows' Bag + Power tab, the Void / Tannery / Trees fallbacks;''')
T.rep('VERSION = "0.3.77"\nJAR', 'VERSION = "0.3.78"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.76.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.77.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.76.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.77.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_77_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_78_patch.py")')
T.rep('"scratch", "oldmenu9", "menu"', '"scratch", "oldmenu10", "menu"')
T.rep('ADDED = []   # 0.3.77: no new class\n', 'ADDED = []   # 0.3.78: no new class\n')
EXPECT_BODY = '''    "InvPage": ["+f ua", "+f uconf", "+f ukey", "+f ulast", "+f unote", "+f usub", "+f utok", "+m fillUp", "+m hv", "+m rcol", "+m ubtn", "+m upPress",
                "+m upTab", "+m uset", "-m furnFull", "~c ", "~m bench", "~m build", "~m fillFurn", "~m fillPockets", "~m handleDataEvent", "~m nowGo", "~m pocketTab",
                "~m pocketUp", "~m tanning"],
    "InvData": ["+f UF_BTN", "+f UF_NAMES", "+f U_HELP", "~<clinit>"],   # the page data (+ panel 'u', no Full page) + the view's sub-tabs + help
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.77:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.78: the pocket Upgrades view, no Full page, the Tanning caption, the version strings
''' + EXPECT_BODY + '''
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.77"') == 1, "S VERSION")
''', '''    K.check(g.count('VERSION = "0.3.78"') == 1, "S VERSION")
''' + HARNESS_OLD10_STATIC)
# OLD9's ratchet compared 0.3.77 with 0.3.76: against 0.3.77 its rows stay gone; its live-door count is OLD10's (zero now)
T.rep('''    K.check(lefto_ - left2_ == set([("character", "trees"), ("character", "accessories")])
            and left2_ == set([("settings", "setup"), ("storage", "pocket"), ("smithing", "recipes")]),
            "OLD9 RATCHET OLD_LEFT lost character:trees + character:accessories; left = Server Setup (on purpose) + the tracked SkyySacks doors storage:pocket / smithing:recipes (%d -> %d: %s)"
            % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(("character", "trees") not in left2_ and ("character", "accessories") not in left2_, "OLD9 RATCHET (0.3.78: vs 0.3.77) character:trees + character:accessories stay gone")''')
T.rep('''    K.check(nwd_.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");') == 1 and nwd_.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");') == 1
            and 'handleCommand(this.playerRef, "tree "' not in nwd_ and "FOLLOW-UP: a" in g and "SkyySacks op 'sacks:fn:pocket'" in g,
            "OLD9 FIX RATCHET the live old-page doors (Upgrades = openPocket, the Tanning Full page = openTannery) are one each and tracked with a follow-up; no /tree left in the new screens")''',
      '''    K.check(nwd_.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");') == 0 and nwd_.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");') == 0
            and 'handleCommand(this.playerRef, "tree "' not in nwd_,
            "OLD9 FIX RATCHET (0.3.78) the two live old-page doors (Upgrades = openPocket, the Tanning Full page = openTannery) are gone; no /tree left in the new screens")''')
# CRAFT / INV4: the Tanning tab without sacks:fn:furnList = a caption naming SkyySacks 0.8.40 (no openTannery)
T.rep('''    K.check("needs SkyySacks 0.8.38" in cap_of(p_) and "Crafting page" not in cap_of(p_), "CRAFT Tanning tab without openTannery: (0.3.77) a caption naming SkyySacks 0.8.38, no old Crafting page (%s)" % cap_of(p_))''',
      '''    K.check("needs SkyySacks 0.8.40" in cap_of(p_) and "Crafting page" not in cap_of(p_), "CRAFT Tanning tab without furnList: (0.3.78) a caption naming SkyySacks 0.8.40, no old Crafting page (%s)" % cap_of(p_))''')
T.rep('''        K.check(TAN == [str(PK.pr.getUuid())] and cap_of(p_) == "Opening the Tannery", "INV4 the Tanning tab = sacks:fn:openTannery (%s)" % cap_of(p_))''',
      '''        K.check(TAN == [] and "needs SkyySacks 0.8.40" in cap_of(p_) and PK.pm.getCustomPage() == pg,
                "INV4 the Tanning tab without furnList = (0.3.78) a caption naming SkyySacks 0.8.40 - sacks:fn:openTannery (the old page) is never called (%s)" % cap_of(p_))''')
# OLD9 FALL: Upgrades without the view's bridge names SkyySacks 0.8.43
T.rep('''    p_ = one(ev(PT, {"a": "pup"}), "OLD9 FALL Upgrades without SkyySacks 0.8.39")
    K.check(not CMP["open"] and "need SkyySacks 0.8.39" in cap_of(p_) and PT.pm.getCustomPage() == pgP,
            "OLD9 FALL Upgrades without sacks:fn:openPocket = a caption naming SkyySacks 0.8.39, the page stays (%s)" % cap_of(p_))''',
      '''    p_ = one(ev(PT, {"a": "pup"}), "OLD9 FALL Upgrades without SkyySacks 0.8.43")
    K.check(not CMP["open"] and "need SkyySacks 0.8.43" in cap_of(p_) and PT.pm.getCustomPage() == pgP,
            "OLD9 FALL Upgrades without sacks:fn:upView / upAct = (0.3.78) a caption naming SkyySacks 0.8.43, the page stays (%s)" % cap_of(p_))''')
T.rep('''    p_ = one(ev(PT, {"a": "pup"}), "INV6 POCKET Upgrades")
    K.check(CMP["open"] == [(u6, "Mining")], "INV6 POCKET Upgrades = ONE sacks:fn:openPocket with the pocket (%s)" % CMP["open"])
''', HARNESS_UPG)
# oldmenu10fix: the Furnace tab / Right-now row without sacks:fn:furnList = a caption naming SkyySacks 0.8.40 (no sacks:fn:openFurnace)
T.rep('''    K.check(len(OPENED) == 1 and "Opening the Furnace" in cap_of(p_), "CRAFT Furnace tab: the pack's own Furnace page (sacks:fn:openFurnace)")''',
      '''    K.check(len(OPENED) == 0 and "Furnace panel needs SkyySacks 0.8.40" in cap_of(p_) and PK.pm.getCustomPage() == pg,
            "CRAFT Furnace tab without furnList: (oldmenu10fix) a caption naming SkyySacks 0.8.40, no SkyySacks Furnace page (%s)" % cap_of(p_))''')
T.rep('''    K.check(len(OPENED) == o0_ + 1 and str(pgF.mode) == "c", "INV7 FURN without sacks:fn:furnList the Furnace tab opens the pack's own page (0.3.55)")''',
      '''    K.check(len(OPENED) == o0_ and str(pgF.mode) == "c" and "Furnace panel needs SkyySacks 0.8.40" in cap_of(p_),
            "INV7 FURN without sacks:fn:furnList the Furnace tab = (oldmenu10fix) a caption naming SkyySacks 0.8.40, no old page (%s)" % cap_of(p_))''')
T.rep('''    K.check(str(pgF.mode) == "f" and str(pgF.fbench) == "Furnace", "INV7 NOW Go = the Furnace panel")
''', '''    K.check(str(pgF.mode) == "f" and str(pgF.fbench) == "Furnace", "INV7 NOW Go = the Furnace panel")
    fl_ = BR.remove("sacks:fn:furnList")
    o0_ = len(OPENED)
    p_ = one(ev(PK, {"a": "now:%d" % nt_.index("furn:Furnace")}), "INV7 NOW Go on the Furnace row without furnList")
    K.check(len(OPENED) == o0_ and "Furnace panel needs SkyySacks 0.8.40" in cap_of(p_),
            "INV7 NOW (oldmenu10fix) the Furnace row without furnList = a caption naming SkyySacks 0.8.40, no SkyySacks Furnace page (%s)" % cap_of(p_))
    BR.put("sacks:fn:furnList", fl_)
''')
# INV7: the Full page is gone - a forged 'fxp' opens nothing
T.rep('''    p_ = one(ev(PK, {"a": "fxp"}), "INV7 FURN Full page")
    K.check(len(OPENED) == o0_ + 1 and "Opening the Furnace" in cap_of(p_), "INV7 FURN Full page = the pack's own Furnace page (sacks:fn:openFurnace)")''',
      '''    p_ = one(ev(PK, {"a": "fxp"}), "INV7 FURN a forged Full page")
    K.check(len(OPENED) == o0_ and "Opening" not in cap_of(p_) and PK.pm.getCustomPage() == pgF, "INV7 FURN (0.3.78) no Full page: a forged 'fxp' opens nothing (%s)" % cap_of(p_))''')
if T.dst:
    T.finish()
