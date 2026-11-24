"""Derive SkyyMenu/build_skyymenu_0.3.68.py + SkyyMenu/test_skyymenu_0.3.68.py from the SET pin SkyyMenu 0.3.67 (generated - never re-run
its patch). Run:  python tools/menu_0_3_68_patch.py   then   python SkyyMenu/build_skyymenu_0.3.68.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.68.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Pairs with SkyyGear 0.3.60 (tools/gear_0_3_60_patch.py: gear:fn:shop read / act).

0.3.68 (2026-11-23, round skl2) = THE SKILL PAGE WORKSHOP. Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'SKILL PAGE = GEAR WORKSHOP' +
'RETIRE THE OLD MENU'): "and the upgrading, reforging, and applying sigls to both tools and armor should all happen here." / "when everything is in
the new system id like to disable the old menu compleatly, so instead of adding things like the full tree button, just build it all into the new
system and remove the old "Full tree""; 2026-11-23 "looks better. go head and build everything on your list."
  1. THE WORKSHOP (a third view of the SKILL TREE panel, like the inline tree - no old page, no 'Full page' link): the gear card's TOOL and its
     4 ARMOUR slots are clickable (click = that item on the workshop); the tool card's button is now "Workshop" (was "Upgrade" = the old
     Smithing hub); the tree panel's "Full tree" button (the old /tree page) is now "Workshop" / "Skill tree" (Skyy: remove the old Full tree).
     The title reads WORKSHOP; the item row = its icon (the stack's own tooltip + rarity colour), its name in its rarity colour, slot / rarity /
     level / tier / where it is, your coins; three cards: UPGRADE (the next tier in its rarity colour, the skill / collection rows, every
     material have / need in green / red, the why line), REFORGE / LEVEL UP (the cost line, the level-up line, both buttons), SIGIL (this item's
     rarity, the Sigil that fits in its colour, Other, Apply -> Confirm sigil).
  2. WHICH ITEM: the tool = the one you picked last on this page (while it is still there), else the tool in your hand when it is this skill's,
     else the card's tool (the skill's Requip preset) when you carry it, else your best-tier tool of the skill you carry. Armour slot k = the
     preset's piece (worn first, else carried) or - without a preset piece - what you wear there. Not carried = said ("Requip puts it on").
  3. EVERY number, rule and text comes from SkyyGear 0.3.60 gear:fn:shop = the Anvil's own code (GearForge.reforge / levelUp, GearUp.upgrade,
     GearSigil.apply, their refusals, costs and previews); this page only draws the answer and sends the click with the drawn item's place,
     id and key + the profile token: a stale page / double click / item moved / profile switch / not enough coins or items = the Anvil's
     refusal, nothing paid twice (every action changes the key). '=One moment.' = the caption only. Without SkyyGear 0.3.60 = said, nothing
     changes. Reads and acts on the world thread (the page's own build / event).
No new class, command, system, picture, lang key or saved file (SkillPage / SkillData members only).
ROLLBACK to 0.3.67: safe alone (the Upgrade button opens the Smithing hub again; nothing saved).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.67.py"), os.path.join(MOD, "build_skyymenu_0.3.68.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.67.py"), os.path.join(MOD, "test_skyymenu_0.3.68.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.67"\n') and P.has("public void fillPick(") and not P.has("public void fillWork("), "not the generated SkyyMenu 0.3.67 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.67: THE REQUIP SLOT PICKER''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.68: THE SKILL PAGE WORKSHOP: click the tool or an armour piece on a skill page = Upgrade / Reforge / Level up / Sigils for it right there
       (SkyyGear 0.3.60 gear:fn:shop = the Anvil's own code, same costs and rules); the old Full tree button is now Workshop / Skill tree
       (notes: tools/menu_0_3_68_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.68.py.
0.3.67: THE REQUIP SLOT PICKER''')
P.rep('VERSION = "0.3.67"\n', 'VERSION = "0.3.68"\n')

# ---------- sizes
P.rep('''SK_TRLW, SK_TRBW, SK_TROW = 130, 100, 120                  # the header row: the title, Learn / Respec, Full tree
''', '''SK_TRLW, SK_TRBW, SK_TROW = 130, 100, 120                  # the header row: the title, Learn / Respec, Full tree (0.3.68: Workshop / Skill tree)
# 0.3.68 (skl2): THE WORKSHOP = the tree panel's third view (SK_MI x SK_TMH): the item row + three cards (Upgrade, Reforge / Level up, Sigil)
SK_WHH, SK_WGAP, SK_WCG = 50, 6, 8                         # the item row, the gap under it, the gap between the cards
SK_WCW = (SK_MI - 2 * SK_WCG) // 3                         # a card (257)
SK_WCH = SK_TMH - SK_WHH - SK_WGAP                         # its height (208)
SK_WCI = SK_WCW - 12                                       # its inner width (pad 6)
SK_WQH = SK_WCH - 12 - 18 - 4 - 30                         # its rows box (title 18, gap 4, buttons 30)
SK_WNW, SK_WCW2 = 560, 160                                 # the item name / info column, the coins label
SK_WSLOT = ["Head", "Chest", "Hands", "Legs"]
SK_WCOL = {"green": "#7ee08a", "red": "#ff7a7a", "dim": "#7f93a6", "text": "#d6e4ee", "gold": "#e8c25a", "action": "#ffcc00"}   # Style Guide 15
assert SK_WQH >= 7 * 19 and 48 + 8 + SK_WNW + SK_WCW2 <= SK_MI and SK_WHH + SK_WGAP + SK_WCH == SK_TMH, "0.3.68: the workshop fits the tree panel"
''')
# ---------- the page markup: Workshop button, the tree panel title id, the third view
P.rep('''    ap.append(("#" + gt, G_.glass_button(SK + "GtU", "Upgrade", "secondary", w=110, h=26, size=12, anchor={"top": 4})))''',
      '''    ap.append(("#" + gt, G_.glass_button(SK + "GtU", "Workshop", "secondary", w=110, h=26, size=12, anchor={"top": 4})))   # 0.3.68: was Upgrade (the old hub)''')
P.rep('''    ap.append(("#" + trr, lab(None, "SKILL TREE", 15, "accentHi", bold=True, w=SK_TRLW, h=30)))''',
      '''    ap.append(("#" + trr, lab(SK + "TrT", "SKILL TREE", 15, "accentHi", bold=True, w=SK_TRLW, h=30)))   # 0.3.68: WORKSHOP while it shows''')
P.rep('''    v1_ = SUI.keep_hide(SUI.keep_at0(G_.glass_group(SK + "TrV1", SK_MI, SK_TMH, layout="Left")))
    hm_, kids_ = SUI.keep_holder(SK + "TrH", SK_MI, SK_TMH, [v0_, v1_], anchor={"top": 4})''',
      '''    v1_ = SUI.keep_hide(SUI.keep_at0(G_.glass_group(SK + "TrV1", SK_MI, SK_TMH, layout="Left")))
    v2_ = SUI.keep_hide(SUI.keep_at0(G_.glass_group(SK + "TrV2", SK_MI, SK_TMH, layout="Top")))   # 0.3.68: the workshop
    hm_, kids_ = SUI.keep_holder(SK + "TrH", SK_MI, SK_TMH, [v0_, v1_, v2_], anchor={"top": 4})''')
P.rep('''    assert used_ <= SK_TMH - 16, ("0.3.61: the node panel fits", used_)
''', '''    assert used_ <= SK_TMH - 16, ("0.3.61: the node panel fits", used_)
    # 0.3.68 (skl2): THE WORKSHOP view - the item row (icon, name holder + info line, coins) + three cards (title, rows box, buttons)
    v2 = "#" + SK + "TrV2"
    wh = SK + "Wh"
    ap.append((v2, G_.glass_group(wh, SK_MI, SK_WHH, layout="Left")))
    ap.append(("#" + wh, G_.glass_grid(SK + "Wi", 1, 1, drag=False, slot=48, icon=40)))
    wt = SK + "Wt"
    ap.append(("#" + wh, G_.glass_group(wt, SK_WNW, SK_WHH, layout="Top", anchor={"left": 8})))
    ap.append(("#" + wt, G_.glass_group(SK + "Wnm", SK_WNW, 26, layout="Left")))
    ap.append(("#" + wt, lab(SK + "Wl", "", 12, "dim", w=SK_WNW, h=20)))
    ap.append(("#" + wh, lab(SK + "Wc", "", 13, "xp", bold=True, w=SK_WCW2, h=SK_WHH, halign="End")))
    wk = SK + "Wk"
    ap.append((v2, G_.glass_group(wk, SK_MI, SK_WCH, layout="Left", anchor={"top": SK_WGAP})))
    for c_, (cid_, title_, btns_) in enumerate((("Wu", "UPGRADE", (("WuB", "Upgrade", "primary", SK_WCI),)),
                                                 ("Wf", "REFORGE / LEVEL UP", (("WfB", "Reforge", "primary", (SK_WCI - 5) // 2), ("WlB", "Level up", "secondary", (SK_WCI - 5) // 2))),
                                                 ("Ws", "SIGIL", (("WsN", "Other", "secondary", 80), ("WsB", "Apply sigil", "primary", SK_WCI - 85))))):
        cd_ = SK + cid_
        ap.append(("#" + wk, G_.glass_group(cd_, SK_WCW, SK_WCH, role="inset", layout="Top", pad=6, anchor={"right": SK_WCG} if c_ < 2 else None)))
        ap.append(("#" + cd_, lab(None, title_, 12, "accentHi", bold=True, w=SK_WCI, h=18)))
        ap.append(("#" + cd_, G_.glass_group(cd_ + "q", SK_WCI, SK_WQH, layout="Top")))
        br_ = cd_ + "r"
        ap.append(("#" + cd_, G_.glass_group(br_, SK_WCI, 30, layout="Left", anchor={"top": 4})))
        for k_, (bid_, bt_, kind_, bw_) in enumerate(btns_):
            ap.append(("#" + br_, G_.glass_button(SK + bid_, bt_, kind_, w=bw_, h=30, size=13, anchor={"left": 5} if k_ else None)))
        assert sum(b_[3] for b_ in btns_) + 5 * (len(btns_) - 1) <= SK_WCI, ("0.3.68: a card's buttons fit", cid_)
        assert SUI.text_width(title_, 12, bold=True) <= SK_WCI, ("0.3.68: a card title fits", title_)
    for t_ in ("Not enough coins", "Cannot level up", "Confirm sigil", "Cannot upgrade", "Identify it first"):
        assert SUI.text_width(t_, 13, bold=True) <= (SK_WCI - 5) // 2 - 8 or t_ in ("Cannot upgrade",), ("0.3.68: a button text fits", t_)
''')
P.rep('''("#" + SK + "TrO", "tr"), ("#" + SK + "ShGo", "sh"), ("#" + SK + "TrL", "tl"), ("#" + SK + "TrR", "trs")]   # 0.3.61: + Learn, Respec''',
      '''("#" + SK + "TrO", "tr"), ("#" + SK + "ShGo", "sh"), ("#" + SK + "TrL", "tl"), ("#" + SK + "TrR", "trs"),   # 0.3.61: + Learn, Respec
        ("#" + SK + "WuB", "wu"), ("#" + SK + "WfB", "wf"), ("#" + SK + "WlB", "wl"), ("#" + SK + "WsB", "ws"), ("#" + SK + "WsN", "wn")]   # 0.3.68: the workshop''')
# ---------- the run-time templates (a coloured row, a bold coloured row, the item name)
P.rep('''assert not [k_ for k_, g_ in _tok61.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], ("0.3.61: the tree markups are proven", _tok61)
''', '''assert not [k_ for k_, g_ in _tok61.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], ("0.3.61: the tree markups are proven", _tok61)
# 0.3.68 (skl2): the workshop's run-time markups - a row (12 px, wraps up to 3 lines) / a bold row (13 px) in a Style Guide 15 / rarity colour,
# the item name (16 px bold, its rarity colour). 7771 = the id number, 7772 = the height, #123457 = the colour (Java checks it is #rrggbb)
_wr = sk_wrap(SK + "Wr7771", 12, "#123457", False, SK_WCI, 7772, 3, 0)
_wb = sk_wrap(SK + "Wr7771", 13, "#123457", True, SK_WCI, 7772, 3, 0)
_wn = SUI.glass_label(SK + "WnN", "", 16, "#123457", bold=True, w=SK_WNW, h=26)
for _mk in (_wr, _wb, _wn):
    SUI.check_markup(_mk, prefix=SK, kit_paths=True)
    assert "@" not in _mk and "\\n" not in _mk and "Scrolling" not in _mk and _mk.count("#123457") == 1, "0.3.68: a run-time markup line Java can hold"
_tok68 = SUI.proven_tokens([("#" + SK + "Wuq", _m) for _m in (_wr, _wb, _wn)])
assert not [k_ for k_, g_ in _tok68.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], ("0.3.68: the workshop markups are proven", _tok68)
SK_WROW, SK_WROWB, SK_WNAME = _wr, _wb, _wn
_w68 = SUI.text_width("Level up to Lv 24: Coins 1,200 (need 300) Weapon Iron Bar", 12) / float(len("Level up to Lv 24: Coins 1,200 (need 300) Weapon Iron Bar"))
SK_WCN = int(SK_WCI / (_w68 * 1.08))                       # characters on one 12 px line of a card (a little room for wide letters)
SK_WCB = int(SK_WCN * 12 / 13.0)
assert 30 <= SK_WCN <= 45, ("0.3.68: the row line length", SK_WCN)
SK_WRUN = 3 * 20 + 1                                       # the workshop's run-time elements at most (rows + the name)
assert SK_WRUN < SK_TMAXN * 3, "0.3.68: the workshop draws less than the tree it replaces (the page budget below counts the tree)"
''')
P.rep('''F(sdat, "public static final String[] TDID = %s;" % jarr([r_[0] for r_ in SK_TD_ROWS]))   # 0.3.61: the node panel's labels
''', '''F(sdat, "public static final String[] TDID = %s;" % jarr([r_[0] for r_ in SK_TD_ROWS]))   # 0.3.61: the node panel's labels
for _n, _v in (("WROW", SK_WROW), ("WROWB", SK_WROWB), ("WNAME", SK_WNAME), ("WGREEN", SK_WCOL["green"]), ("WRED", SK_WCOL["red"]), ("WDIM", SK_WCOL["dim"]),
               ("WTEXT", SK_WCOL["text"]), ("WGOLD", SK_WCOL["gold"]), ("WACT", SK_WCOL["action"]),
               ("W_NOGEAR", "The workshop needs SkyyGear 0.3.60 - Upgrade, Reforge and Sigils are not on this server right now"),
               ("W_NOANS", "The Anvil could not answer right now - nothing changed. Try again."),
               ("W_HINT", "Click the tool or an armour piece above"),
               ("W_DESC", "Re-rolls every modifier for its rarity."),
               ("W_UNID", "Unidentified: identify it with /identify first, then come back.")):   # fix round (critic)   # 0.3.68: the workshop (W_DESC = the Anvil's Reforge card line)
    F(sdat, "public static final String %s = %s;" % (_n, jstr(_v)))
for _n, _v in (("WQH", SK_WQH), ("WCN", SK_WCN), ("WCB", SK_WCB)):   # 0.3.68
    F(sdat, "public static final int %s = %d;" % (_n, _v))
F(sdat, "public static final String[] WSLOT = %s;" % jarr(SK_WSLOT))   # 0.3.68
''')
# ---------- SkillPage fields + constructor
P.rep('''"public int tsel;", "public String ttok;"''', '''"public boolean wopen;", "public int wsel;", "public int wsig;", "public String wtok;", "public String wpin;", "public String gtool;",
           "public String[] garm;", "public String[] wloc;", "public String[] wid;", "public String[] wkey;", "public int[] wch;", "public int wacts;",   # 0.3.68: the workshop
           "public int tsel;", "public String ttok;"''')
P.rep('''  this.tinline = false;
}""")
# 0.3.58: THE PETS SCREEN DATA''', '''  this.tinline = false;
  this.wopen = false;   // 0.3.68: the workshop
  this.wsel = 0;
  this.wsig = 0;
  this.wtok = null;
  this.wpin = null;
  this.gtool = null;
  this.garm = new String[4];
  this.wloc = new String[5];
  this.wid = new String[5];
  this.wkey = new String[5];
  this.wch = new int[0];
  this.wacts = 0;
}""")
# 0.3.58: THE PETS SCREEN DATA''')
# ---------- fillGear: remember the card's tool + the preset's armour ids; the TOOL / ARMOUR slots are clickable
P.rep('''  this.presetN = -1;
  boolean worn = false;''', '''  this.presetN = -1;
  this.gtool = null;   // 0.3.68: the card's tool + the preset's armour (the workshop's targets)
  this.garm = new String[4];
  boolean worn = false;''')
P.rep('''    for (int k = 4; k < 13 && tool == null; k++) { if (toolOf(ids[k], pre)) { tool = ids[k]; from = "From your " + sk + " preset"; } }''',
      '''    for (int k = 4; k < 13 && tool == null; k++) { if (toolOf(ids[k], pre)) { tool = ids[k]; from = "From your " + sk + " preset"; } }
    for (int k = 0; k < 4; k++) { if (ids[k] != null && ids[k].length() > 0 && !"keep".equals(marks[k]) && !"empty".equals(marks[k])) this.garm[k] = ids[k]; }   // 0.3.68''')
P.rep('''  b.set("#SkyySkpGtI.Slots", @PKG@.InvPage.act(tl));
}""")''', '''  b.set("#SkyySkpGtI.Slots", @PKG@.InvPage.act(tl));
  this.gtool = tool;   // 0.3.68: a click on the tool / an armour slot = it on the workshop
}""")''')
P.rep('''  b.set("#SkyySkpTrO.Text", on ? "Full tree" : "Open tree");''',
      '''  b.set("#SkyySkpTrO.Text", on ? "Workshop" : "Open tree");   // 0.3.68 (Skyy: "remove the old Full tree"): the inline view's door = the workshop''')
# ---------- the workshop methods (before build / handleDataEvent)
WORK_JAVA = r'''# 0.3.68 (skl2): THE WORKSHOP. Targets (world thread, the page's own inventory read), the SkyyGear 0.3.60 gear:fn:shop read drawn into the
# tree panel's third view, the clicks sent back with the drawn item's place + id + key and the read's profile token (tools/gear_0_3_60_patch.py)
M(skpg, r"""
public static boolean okHex(String h) {
  if (h == null || h.length() != 7 || h.charAt(0) != '#') return false;
  for (int i = 1; i < 7; i++) {
    char c = h.charAt(i);
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))) return false;
  }
  return true;
}""")
M(skpg, r"""
public static @IC@ wsec(@INV@ inv, int s) {
  if (inv == null) return null;
  if (s == 0) return inv.getHotbar();
  if (s == 1) return inv.getStorage();
  if (s == 2) return inv.getBackpack();
  if (s == 3) return inv.getArmor();
  return null;
}""")
M(skpg, r"""
public static @IS@ wat(@INV@ inv, String at) {
  if (at == null) return null;
  int c = at.indexOf(':');
  if (c <= 0) return null;
  int s = @PKG@.InvPage.toInt(at.substring(0, c), -1);
  int k = @PKG@.InvPage.toInt(at.substring(c + 1), -1);
  @IC@ ic = wsec(inv, s);
  if (ic == null || k < 0 || k >= ic.getCapacity()) return null;
  @IS@ x = ic.getItemStack((short) k);
  return x == null || x.isEmpty() ? null : x;
}""")
M(skpg, r"""
public static int held(@INV@ inv) {
  try { return inv == null ? -1 : (int) inv.getActiveHotbarSlot(); } catch (Throwable t) { return -1; }
}""")
# a carried stack of exactly that id: hotbar, bag, backpack (hand first when asked) - the place, or null
M(skpg, r"""
public static String wfind(@INV@ inv, String id, boolean hand) {
  if (inv == null || id == null || id.length() == 0) return null;
  int a = held(inv);
  if (hand && a >= 0) { @IS@ x = wat(inv, "0:" + a); if (x != null && id.equals(x.getItemId())) return "0:" + a; }
  for (int s = 0; s < 3; s++) {
    @IC@ c = wsec(inv, s);
    for (int i = 0; c != null && i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x != null && !x.isEmpty() && id.equals(x.getItemId())) return s + ":" + i;
    }
  }
  return null;
}""")
# the best-tier carried tool of the skill (the first of the best tier)
M(skpg, r"""
public static String wbest(@INV@ inv, String pre) {
  String best = null;
  int bt = -2;
  for (int s = 0; inv != null && s < 3; s++) {
    @IC@ c = wsec(inv, s);
    for (int i = 0; c != null && i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || !toolOf(x.getItemId(), pre)) continue;
      int t = -1;
      try { t = @PKG@.InvCraft.tier(x.getItemId()); } catch (Throwable e) { t = -1; }
      if (t > bt) { bt = t; best = s + ":" + i; }
    }
  }
  return best;
}""")
# the five targets: [0..4] = the place ("<section>:<slot>") of the tool + the 4 armour pieces, [5..9] = why there is none
M(skpg, r"""
public String[] wtargets(@INV@ inv) {
  String[] out = new String[10];
  int si = idx(this.skill);
  String pre = si >= 0 ? @PKG@.SkillData.TOOLP[si] : "";
  if (inv == null) { for (int k = 0; k < 5; k++) out[5 + k] = "Your inventory cannot be read right now"; return out; }
  if (pre.length() == 0) out[5] = "No tool for " + this.skill + " - pick an armour piece";
  else {
    String at = null;
    @IS@ p0 = wat(inv, this.wpin);
    if (p0 != null && this.wpin.startsWith("3:") == false && toolOf(p0.getItemId(), pre)) at = this.wpin;
    int a = held(inv);
    if (at == null && a >= 0) { @IS@ h = wat(inv, "0:" + a); if (h != null && toolOf(h.getItemId(), pre)) at = "0:" + a; }
    if (at == null && this.gtool != null) at = wfind(inv, this.gtool, true);
    if (at == null) at = wbest(inv, pre);
    out[0] = at;
    if (at == null) out[5] = this.gtool != null ? "Your " + @PKG@.InvCraft.name(this.gtool) + " is not on you - carry it to work on it" : "No " + this.skill + " tool on you";
  }
  for (int k = 0; k < 4; k++) {
    String id = this.garm == null ? null : this.garm[k];
    String sn = @PKG@.SkillData.WSLOT[k].toLowerCase();
    if (id != null) {
      @IS@ w = wat(inv, "3:" + k);
      String at = w != null && id.equals(w.getItemId()) ? "3:" + k : wfind(inv, id, false);
      if (at == null && w != null) at = "3:" + k;   // fix round (critic): the preset's piece is not on you - the piece you wear there instead
      out[1 + k] = at;
      if (at == null) out[6 + k] = "Your " + @PKG@.InvCraft.name(id) + " is not on you - Requip puts it on";
    } else {
      out[1 + k] = wat(inv, "3:" + k) != null ? "3:" + k : null;
      if (out[1 + k] == null) out[6 + k] = "You wear nothing on your " + sn;
    }
  }
  return out;
}""")
# one row into a card's rows box: 12 px (bold: 13 px) in a checked colour, 1-3 lines; u = {used height, rows skipped}; false = did not fit
M(skpg, r"""
public static boolean wrow(@UCB@ b, String box, int id, String txt, String hex, boolean bold, int[] u) {
  String t = txt == null ? "" : txt;
  int per = bold ? @PKG@.SkillData.WCB : @PKG@.SkillData.WCN;
  if (t.length() > 3 * per) t = @PKG@.MenuUtil.clip(t, 3 * per);
  int lines = t.length() <= per ? 1 : (t.length() <= 2 * per ? 2 : 3);
  int h = 2 + 16 * lines;
  if (u[0] + h > @PKG@.SkillData.WQH) { u[1] = u[1] + 1; return false; }
  String hx = okHex(hex) ? hex : @PKG@.SkillData.WTEXT;
  b.appendInline(box, (bold ? @PKG@.SkillData.WROWB : @PKG@.SkillData.WROW).replace("7771", String.valueOf(id)).replace("7772", String.valueOf(h)).replace("#123457", hx));
  b.set("#SkyySkpWr" + id + ".Text", t);
  u[0] = u[0] + h + 1;
  return true;
}""")
# fix round (critic): the Upgrade card's rows - { text, colour, how many rows of the Anvil it holds }; blocking (red) ones first
M(skpg, r"""
public static int wh(String t, boolean bold) {
  int per = bold ? @PKG@.SkillData.WCB : @PKG@.SkillData.WCN;
  int n = t == null ? 0 : Math.min(t.length(), 3 * per);
  return 2 + 16 * (n <= per ? 1 : (n <= 2 * per ? 2 : 3)) + 1;
}""")
M(skpg, r"""
public static int wneed(java.util.ArrayList rt) {
  int n = 0;
  for (int i = 0; i < rt.size(); i++) n = n + wh(((String[]) rt.get(i))[0], false);
  return n;
}""")
M(skpg, r"""
public static String stCol(String st) {
  int s = @PKG@.InvPage.toInt(st, -1);
  return s > 0 ? @PKG@.SkillData.WGREEN : (s == 0 ? @PKG@.SkillData.WRED : @PKG@.SkillData.WTEXT);
}""")
M(skpg, r"""
public static java.util.ArrayList wuprows(java.util.ArrayList fq, java.util.ArrayList fm, boolean pair) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int pass = 0; pass < 2; pass++) {
    boolean red = pass == 0;
    for (int i = 0; i < fq.size(); i++) {
      String[] q = (String[]) fq.get(i);
      String c = stCol(q[2]);
      if (@PKG@.SkillData.WRED.equals(c) == red) out.add(new String[] { q[3], c, "1" });
    }
    String[] open = null;
    for (int i = 0; i < fm.size(); i++) {
      String[] m = (String[]) fm.get(i);
      long need = @PKG@.InvPage.toLong(m[3], 0L);
      long hv = @PKG@.InvPage.toLong(m[4], 0L);
      if ((hv < need) != red) continue;
      String t = @PKG@.MenuUtil.clip(m[5], @PKG@.SkillData.WCN - 14) + "  " + @PKG@.MenuUtil.fmt(hv) + " / " + @PKG@.MenuUtil.fmt(need);
      if (pair && open != null && open[0].length() + 4 + t.length() <= @PKG@.SkillData.WCN) { open[0] = open[0] + "    " + t; open[2] = "2"; open = null; continue; }
      String[] r = new String[] { t, red ? @PKG@.SkillData.WRED : @PKG@.SkillData.WGREEN, "1" };
      out.add(r);
      open = null;
      if (pair) open = r;
    }
  }
  return out;
}""")
M(skpg, r"""
public void workShell(@UCB@ b) {
  b.set("#SkyySkpTrV0.Visible", false);
  b.set("#SkyySkpTrV1.Visible", false);
  b.set("#SkyySkpTrV2.Visible", true);
  b.set("#SkyySkpTrL.Visible", false);
  b.set("#SkyySkpTrR.Visible", false);
  b.set("#SkyySkpTrO.Text", "Skill tree");
  b.set("#SkyySkpTrT.Text", "WORKSHOP");
  b.set("#SkyySkpTrP.Text", @PKG@.SkillData.W_HINT);
}""")
M(skpg, r"""
public void wnone(@UCB@ b, String what, String why) {
  b.appendInline("#SkyySkpWnm", @PKG@.SkillData.WNAME.replace("#123457", @PKG@.SkillData.WDIM));
  b.set("#SkyySkpWnN.Text", what + " - nothing to work on");
  b.set("#SkyySkpWl.Text", @PKG@.MenuUtil.clip(why == null ? "" : why, 110));
  int[] u = new int[2];
  wrow(b, "#SkyySkpWuq", 0, @PKG@.SkillData.W_HINT, @PKG@.SkillData.WDIM, false, u);
  this.wch = new int[0];
}""")
M(skpg, r"""
public void fillWork(@UCB@ b, @REF@ ref, @ST@ st) {
  workShell(b);
  this.wtok = null;
  this.wch = new int[0];
  for (int k = 0; k < 5; k++) { this.wloc[k] = null; this.wid[k] = null; this.wkey[k] = null; }
  java.util.UUID u = this.playerRef.getUuid();
  @INV@ inv = null;
  try { @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); inv = p == null ? null : p.getInventory(); } catch (Throwable t) { inv = null; }
  String[] tg = wtargets(inv);
  if (this.wsel < 0 || this.wsel > 4) this.wsel = 0;
  int n = this.wsel;
  String what = n == 0 ? "TOOL" : @PKG@.SkillData.WSLOT[n - 1].toUpperCase();
  if (@PKG@.InvCraft.fn("gear:fn:shop") == null) { wnone(b, what, @PKG@.SkillData.W_NOGEAR); return; }
  if (tg[n] == null) { wnone(b, what, tg[5 + n]); return; }
  StringBuilder sp = new StringBuilder();
  for (int k = 0; k < 5; k++) { if (k > 0) sp.append(';'); sp.append(tg[k] == null ? "-" : tg[k]); }
  String[] ls = lines("gear:fn:shop", new Object[] { u, "read", sp.toString() });
  String[] h = null;
  if (ls != null && ls.length > 0) h = ls[0].split("\\|", -1);
  if (h == null || h.length < 7 || !"ok".equals(h[0])) { wnone(b, what, @PKG@.SkillData.W_NOANS); return; }
  long purse = @PKG@.InvPage.toLong(h[2], -1L);
  b.set("#SkyySkpWc.Text", purse >= 0L ? "Coins " + @PKG@.MenuUtil.fmt(purse) : "");
  String ns = String.valueOf(n);
  String[] fi = null;
  String[] ff = null;
  String[] fl = null;
  String[] fu = null;
  String[] fw = null;
  String[] fs = null;
  java.util.ArrayList fq = new java.util.ArrayList();
  java.util.ArrayList fm = new java.util.ArrayList();
  java.util.ArrayList fc = new java.util.ArrayList();
  for (int i = 1; i < ls.length; i++) {
    String[] f = ls[i].split("\\|", -1);
    if (f.length < 3 || !ns.equals(f[1])) continue;
    String c = f[0];
    if ("i".equals(c) && f.length >= 15) fi = f;
    else if ("f".equals(c) && f.length >= 6) ff = f;
    else if ("l".equals(c) && f.length >= 6) fl = f;
    else if ("u".equals(c) && f.length >= 6) fu = f;
    else if ("w".equals(c) && f.length >= 4) fw = f;
    else if ("s".equals(c) && f.length >= 5) fs = f;
    else if ("q".equals(c) && f.length >= 4) fq.add(f);
    else if ("m".equals(c) && f.length >= 6) fm.add(f);
    else if ("c".equals(c) && f.length >= 8) fc.add(f);
  }
  if (fi == null || !(fi[2] + ":" + fi[3]).equals(tg[n])) { wnone(b, what, "Nothing there any more"); return; }
  this.wtok = h[1];
  this.wloc[n] = tg[n];
  this.wid[n] = fi[4];
  this.wkey[n] = fi[5];
  // the item row: its icon (the stack's own tooltip + rarity colour), the name in its rarity colour, slot / rarity / level / tier / where
  @IS@ stk = wat(inv, tg[n]);
  java.util.ArrayList sl = new java.util.ArrayList();
  if (stk != null) sl.add(@PKG@.InvPage.slot(stk)); else sl.add(new @IGS@());
  b.set("#SkyySkpWi.Slots", @PKG@.InvPage.act(sl));
  int qty = @PKG@.InvPage.toInt(fi[14], 1);
  b.appendInline("#SkyySkpWnm", @PKG@.SkillData.WNAME.replace("#123457", okHex(fi[9]) ? fi[9] : @PKG@.SkillData.WTEXT));
  b.set("#SkyySkpWnN.Text", @PKG@.MenuUtil.clip(fi[6] + (qty > 1 ? "  x" + qty : ""), 44));
  String tt = tierText(fi[4]);
  String info = what + "  -  " + ("1".equals(fi[11]) ? fi[8] + "  -  Lv " + fi[10] : "no rarity") + (tt.length() > 0 ? "  -  " + tt : "") + "  -  " + fi[13]
      + ("1".equals(fi[12]) ? "  -  unidentified" : "");
  b.set("#SkyySkpWl.Text", @PKG@.MenuUtil.clip(info, 110));
  // UPGRADE: the next tier (its rarity colour), the skill / collection rows, every material have / need, the why line (kept room first)
  int[] uu = new int[2];
  if (fu != null) {
    wrow(b, "#SkyySkpWuq", 0, fu[3], fu[4], true, uu);
    String wt = fw == null ? "" : fw[3];
    int wl = wt.length() <= @PKG@.SkillData.WCN ? 1 : (wt.length() <= 2 * @PKG@.SkillData.WCN ? 2 : 3);
    int keep = wt.length() > 0 ? 2 + 16 * wl + 1 : 0;
    // fix round (critic): what blocks the upgrade first - the red skill / collection rows, then the missing materials - then the rest; when they
    // do not all fit, two materials of one colour share a line; still too many = "+ N more" (red when a missing one is among them)
    java.util.ArrayList rt = wuprows(fq, fm, false);
    if (uu[0] + wneed(rt) + keep > @PKG@.SkillData.WQH) rt = wuprows(fq, fm, true);
    int k = 1;
    int hid = 0;
    boolean hidRed = false;
    for (int i = 0; i < rt.size(); i++) {
      String[] r = (String[]) rt.get(i);
      int h = wh(r[0], false);
      if (hid > 0 || uu[0] + h + keep + (i < rt.size() - 1 ? 19 : 0) > @PKG@.SkillData.WQH) { hid = hid + @PKG@.InvPage.toInt(r[2], 1); if (@PKG@.SkillData.WRED.equals(r[1])) hidRed = true; continue; }
      wrow(b, "#SkyySkpWuq", k, r[0], r[1], false, uu);
      k = k + 1;
    }
    if (hid > 0) { wrow(b, "#SkyySkpWuq", k, "+ " + hid + " more" + (hidRed ? " - some are missing" : " - you have them"), hidRed ? @PKG@.SkillData.WRED : @PKG@.SkillData.WDIM, false, uu); k = k + 1; }
    if (wt.length() > 0) wrow(b, "#SkyySkpWuq", k, wt, "2".equals(fw[2]) ? @PKG@.SkillData.WRED : @PKG@.SkillData.WDIM, false, uu);
    b.set("#SkyySkpWuB.Text", fu[5]);
  }
  // REFORGE / LEVEL UP: the cost line, the Anvil's line, the level-up line; both buttons
  int[] uf = new int[2];
  if (ff != null) {
    int fst = @PKG@.InvPage.toInt(ff[2], 2);
    wrow(b, "#SkyySkpWfq", 20, ff[4], fst == 2 ? @PKG@.SkillData.WDIM : (fst == 1 ? @PKG@.SkillData.WRED : @PKG@.SkillData.WGREEN), true, uf);
    wrow(b, "#SkyySkpWfq", 21, @PKG@.SkillData.W_DESC, @PKG@.SkillData.WDIM, false, uf);
    b.set("#SkyySkpWfB.Text", ff[5]);
  }
  if (fl != null) {
    int lst = @PKG@.InvPage.toInt(fl[2], 2);
    wrow(b, "#SkyySkpWfq", 22, fl[4], lst == 2 ? @PKG@.SkillData.WDIM : (lst == 1 ? @PKG@.SkillData.WRED : @PKG@.SkillData.WGOLD), true, uf);
    b.set("#SkyySkpWlB.Text", fl[5]);
  }
  if ("1".equals(fi[12])) wrow(b, "#SkyySkpWfq", 23, @PKG@.SkillData.W_UNID, @PKG@.SkillData.WRED, false, uf);   // fix round (critic)
  // SIGIL: this item's rarity, the picked Sigil that fits (its colour), its refusal, Other / Apply -> Confirm sigil
  int[] us = new int[2];
  if (fs != null) {
    int sst = @PKG@.InvPage.toInt(fs[2], 2);
    if (sst != 0 || fc.size() == 0) {
      wrow(b, "#SkyySkpWsq", 40, fs[3], @PKG@.SkillData.WDIM, false, us);
      b.set("#SkyySkpWsB.Text", "Cannot apply");
    } else {
      int[] ch = new int[fc.size()];
      int pick = -1;
      for (int i = 0; i < ch.length; i++) { ch[i] = @PKG@.InvPage.toInt(((String[]) fc.get(i))[2], -1); if (ch[i] == this.wsig) pick = i; }
      if (pick < 0) pick = 0;
      this.wch = ch;
      this.wsig = ch[pick];
      String[] c = (String[]) fc.get(pick);
      wrow(b, "#SkyySkpWsq", 40, "This item: " + fs[3], okHex(fs[4]) ? fs[4] : @PKG@.SkillData.WTEXT, false, us);
      wrow(b, "#SkyySkpWsq", 41, c[6], okHex(c[4]) ? c[4] : @PKG@.SkillData.WTEXT, true, us);
      boolean arm = "1".equals(c[7]);
      if (c[5].length() > 0) wrow(b, "#SkyySkpWsq", 42, c[5], @PKG@.SkillData.WRED, false, us);
      else wrow(b, "#SkyySkpWsq", 42, arm ? "Click Confirm sigil within 10 s - no way back" : "Apply, then Confirm sigil - one Sigil is used", arm ? @PKG@.SkillData.WGOLD : @PKG@.SkillData.WDIM, false, us);
      if (ch.length > 1) {
        StringBuilder o = new StringBuilder();
        for (int i = 0; i < fc.size(); i++) { if (i == pick) continue; String[] c2 = (String[]) fc.get(i); if (o.length() > 0) o.append(", "); o.append(c2[6].indexOf(' ') > 0 ? c2[6].substring(0, c2[6].indexOf(' ')) : c2[6]); }
        wrow(b, "#SkyySkpWsq", 43, "Other fits: " + o.toString(), @PKG@.SkillData.WACT, false, us);
      }
      b.set("#SkyySkpWsB.Text", c[5].length() > 0 ? "Cannot apply" : (arm ? "Confirm sigil" : "Apply sigil"));
    }
  }
}""")
# ---- the clicks: open / close, pick a slot, Other, the four actions (ONE gear:fn:shop act each; the answer = the caption + ONE packet)
M(skpg, r"""
public void openWork(int k) {
  if (k < 0 || k > 4) { say("Nothing there"); return; }
  this.wopen = true;
  if (k != this.wsel) { this.wsel = k; this.wsig = 0; }
  this.tcap = "";
  redraw();
}""")
M(skpg, r"""
public void closeWork() {
  this.wopen = false;
  this.tcap = "";
  redraw();
}""")
M(skpg, r"""
public void sigOther() {
  if (!this.wopen || this.wch == null || this.wch.length < 2) { say("No other Sigil fits this item"); return; }
  int k = 0;
  for (int i = 0; i < this.wch.length; i++) if (this.wch[i] == this.wsig) k = i;
  this.wsig = this.wch[(k + 1) % this.wch.length];
  this.tcap = "";
  redraw();
}""")
M(skpg, r"""
public void workAct(String op) {
  if (!this.wopen) { say("Open the workshop first - click the tool or an armour piece"); return; }
  if (@PKG@.InvCraft.fn("gear:fn:shop") == null) { say(@PKG@.SkillData.W_NOGEAR); return; }
  int n = this.wsel;
  if (n < 0 || n > 4 || this.wtok == null || this.wloc[n] == null || this.wid[n] == null || this.wkey[n] == null) { say("Nothing to work on there - nothing changed"); return; }
  int R = 0;
  if ("sg".equals(op)) {
    R = this.wsig;
    if (R <= 0 || this.wch == null || this.wch.length == 0) { say("No Sigil you carry fits this item - nothing changed"); return; }
  }
  this.wacts = this.wacts + 1;
  Object r = call("gear:fn:shop", new Object[] { this.playerRef.getUuid(), "act", this.wtok, op, this.wloc[n], this.wid[n], this.wkey[n], Integer.valueOf(R) });
  if (!(r instanceof String) || ((String) r).length() < 2) { say(@PKG@.SkillData.W_NOANS); return; }
  String m = (String) r;
  String msg = @PKG@.MenuUtil.clip(m.substring(1), 170);
  if (m.charAt(0) == '=' && msg.startsWith("One moment")) { say(msg); return; }
  if (m.charAt(0) == '+' && n == 0) this.wpin = this.wloc[0];
  this.tcap = msg;
  redraw();
}""")
'''
P.rep('''M(skpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;''', WORK_JAVA + '''M(skpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;''')
P.rep('''  try { inl = fillMap(b, ev); } catch (Throwable t) { inl = false; @PKG@.MenuUtil.warn("skill page: the inline tree failed: " + t); }''',
      '''  if (!this.wopen) { try { inl = fillMap(b, ev); } catch (Throwable t) { inl = false; @PKG@.MenuUtil.warn("skill page: the inline tree failed: " + t); } }   // 0.3.68: not under the workshop''')
P.rep('''  try { fillShard(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the shard card failed: " + t); }
  this.builds = this.builds + 1;''', '''  if (this.wopen) {   // 0.3.68: the workshop in the tree panel
    try { fillWork(b, ref, st); } catch (Throwable t) { this.wtok = null; @PKG@.MenuUtil.warn("skill page: the workshop failed: " + t); }
  }
  ev.addEventBinding(@BT@.SlotClicking, "#SkyySkpGtI", @EVD@.of("a", "wt"), false);   // 0.3.68: the tool / an armour piece = it on the workshop
  ev.addEventBinding(@BT@.SlotClicking, "#SkyySkpGaI", @EVD@.of("a", "wa"), false);
  try { fillShard(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the shard card failed: " + t); }
  this.builds = this.builds + 1;''')
P.rep('''  this.tsel = -1;   // 0.3.61''', '''  this.tsel = -1;   // 0.3.61
  this.wsel = 0;   // 0.3.68: the workshop starts on the new skill's tool (it stays open)
  this.wsig = 0;
  this.wpin = null;''')
P.rep('''    if (a.equals("up")) { hub("smithing", "upgrade", "Upgrade"); return; }''',
      '''    if (a.equals("up") || a.equals("wt")) { openWork(0); return; }   // 0.3.68: Workshop / the tool slot (was the old Smithing hub)
    if (a.equals("wa")) { int k = @PKG@.InvPage.ival(d, "SlotIndex", -1); if (k < 0 || k > 3) { say("Nothing there"); return; } openWork(k + 1); return; }
    if (a.equals("wu")) { workAct("up"); return; }
    if (a.equals("wf")) { workAct("forge"); return; }
    if (a.equals("wl")) { workAct("lvl"); return; }
    if (a.equals("ws")) { workAct("sg"); return; }
    if (a.equals("wn")) { sigOther(); return; }''')
P.rep('''    if (a.equals("tr")) { openTree(); return; }''',
      '''    if (a.equals("tr")) {   // 0.3.68: Skill tree (back from the workshop) / Workshop (was Full tree = the old /tree page) / Open tree (no inline tree)
      if (this.wopen) { closeWork(); return; }
      if (this.tinline) { openWork(this.wsel); return; }
      openTree();
      return;
    }''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.68: no system / command"
_i = P.s.index
assert _i("public void fillWork(@UCB@ b, @REF@ ref, @ST@ st)") < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.pref = ref;\n  this.pst = st;\n  String lk = @PKG@.SkillData.LK;") \
    and _i("public void workAct(String op)") < _i('if (a.equals("wu")) { workAct("up"); return; }') and _i("public static boolean toolOf(String id, String pre)") < _i("public static String wbest("), \
    "0.3.68: methods before their callers"
P.finish()


# ======================================================================= the HARNESS (every 0.3.67 check runs again on the 0.3.68 jar, plus SKL2)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


EXPECT_68 = '''EXPECT = {   # 0.3.68: the skill page workshop (SkillPage / SkillData), the version strings
    "SkillPage": ["+f garm", "+f gtool", "+f wacts", "+f wch", "+f wid", "+f wkey", "+f wloc", "+f wopen", "+f wpin", "+f wsel", "+f wsig", "+f wtok",
                  "+m closeWork", "+m fillWork", "+m held", "+m okHex", "+m openWork", "+m sigOther", "+m stCol", "+m wat", "+m wbest", "+m wfind",
                  "+m wh", "+m wneed", "+m wnone", "+m workAct", "+m workShell", "+m wrow", "+m wsec", "+m wtargets", "+m wuprows", "~c ", "~m build", "~m fillGear", "~m handleDataEvent",
                  "~m mapShell", "~m pickSkill"],
    "SkillData": ["+f WACT", "+f WCB", "+f WCN", "+f WDIM", "+f WGOLD", "+f WGREEN", "+f WNAME", "+f WQH", "+f WRED", "+f WROW", "+f WROWB", "+f WSLOT",
                  "+f WTEXT", "+f W_DESC", "+f W_HINT", "+f W_NOANS", "+f W_NOGEAR", "+f W_UNID", "~<clinit>"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the config kit's version text
    "SkyyMenuPlugin": ["~m setup"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],
}
'''
HARNESS_SKL2 = r'''    # ---- SKL2 (0.3.68; Skyy 11-22 "and the upgrading, reforging, and applying sigls to both tools and armor should all happen here." + "remove the
    # old Full tree"): the workshop on a fresh stand-in player, with a Python stand-in of SkyyGear 0.3.60 gear:fn:shop (its real answers:
    # SkyyGear/test_skyygear_0.3.60.py) that reads the player's REAL inventory and keys each place by its id + a version (every action bumps it)
    for iid_ in ("Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Hoe_Iron", "SkyyFishing_Rod_Wood", "Weapon_Sword_Iron", "Armor_Iron_Head",
                 "Armor_Iron_Chest", "Armor_Iron_Legs", "Armor_Iron_Hands", "Armor_Cloth_Chest"):
        if amap.get(iid_) is None:
            it_ = Ucls.allocateInstance(ITc.class_)
            E.jf(ITc.class_, "id").set(it_, iid_)
            E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
            E.jf(ITc.class_, "maxStack").setInt(it_, 1)
            amap.put(iid_, it_)
    PW = E.player(uid=UUIDc(0x68, 0x68), name="SkyyWork")
    byU.put(PW.pr.getUuid(), PW.pr)
    for f_, sl_, iid_ in (("hotbar", 0, "Tool_Pickaxe_Copper"), ("hotbar", 1, "Tool_Hatchet_Iron"), ("hotbar", 2, "Weapon_Sword_Iron"), ("storage", 3, "Tool_Hoe_Iron"),
                          ("storage", 4, "SkyyFishing_Rod_Wood"), ("storage", 5, "Tool_Pickaxe_Iron"), ("storage", 7, "Armor_Iron_Legs"), ("armor", 0, "Armor_Iron_Head")):
        PW.slots[f_].getInventory().addItemStackToSlot(JShort(sl_), ISc(iid_, 1))
    try:
        PW.inv.setActiveHotbarSlot(JByte(0))
    except Exception:
        try:
            E.jf(PW.inv.getClass(), "activeHotbarSlot").setByte(PW.inv, JByte(0))
        except Exception as ex_:
            K.notes.append("SKL2 could not set the active hotbar slot: %s" % ex_)
    K.notes.append("SKL2 active hotbar slot: %s" % PW.inv.getActiveHotbarSlot())
    SECW = ["hotbar", "storage", "backpack", "armor"]
    WS = {"tok": "ep1", "ver": {}, "calls": [], "reads": [], "purse": 5000, "mode": "ok", "arm": None, "hex": "#55FFFF", "unid": 0,
          "qs": [(1, "Mining Lv 30 (you 60)"), (0, "Iron collection IV (you II)")], "mats": [("Ingredient_Bar_Iron", 20, 12, "Iron Bar"), ("Rock_Stone", 5, 9, "Stone")]}

    def w_stack(loc_):
        sec_, sl_ = [int(x_) for x_ in loc_.split(":")]
        if sec_ < 0 or sec_ > 3:
            return None
        c_ = PW.slots[SECW[sec_]].getInventory()
        if sl_ < 0 or sl_ >= int(c_.getCapacity()):
            return None
        s_ = c_.getItemStack(JShort(sl_))
        return None if s_ is None or s_.isEmpty() else s_

    def w_key(loc_, iid_):
        return "%s/%d" % (iid_, WS["ver"].get(loc_, 0))

    def w_fn(o):
        if str(o[1]) == "read":
            spec_ = str(o[2])
            WS["reads"].append(spec_)
            if WS["mode"] == "null":
                return None
            rows_ = ["ok|%s|%d|1|1|1|0" % (WS["tok"], WS["purse"])]
            for n_, loc_ in enumerate(spec_.split(";")):
                st_ = None if loc_ == "-" else w_stack(loc_)
                if st_ is None:
                    rows_.append("x|%d|empty" % n_)
                    continue
                i_ = str(st_.getItemId())
                sec_, sl_ = loc_.split(":")
                ky_ = w_key(loc_, i_)
                arm_ = lambda R_: 1 if WS["arm"] == (ky_, R_) else 0
                rows_ += ["i|%d|%s|%s|%s|%s|Nice %s|3|Legendary|%s|20|1|%d|%s %d|1" % (n_, sec_, sl_, i_, ky_, i_, WS["hex"], WS["unid"], SECW[int(sec_)].title(), int(sl_) + 1),
                          "f|%d|0|500|Coins 500|Reforge" % n_, "l|%d|1|900|Level up to Lv 21: Coins 900 (need 400)|Not enough coins" % n_,
                          "u|%d|2|Next: Better %s (Lv 21)|#55FFFF|Cannot upgrade" % (n_, i_)]
                rows_ += ["q|%d|%d|%s" % (n_, q_[0], q_[1]) for q_ in WS["qs"]] + ["m|%d|%s|%d|%d|%s" % ((n_,) + m_) for m_ in WS["mats"]]
                rows_ += ["w|%d|2|Not enough Iron Bar (need 8)." % n_,
                          "s|%d|0|Normal|#ffffff" % n_, "c|%d|2|1|#FF55FF||Rare Sigil (x1): Normal -> RARE|%d" % (n_, arm_(2)),
                          "c|%d|3|2|#55FFFF||Legendary Sigil (x2): Normal -> LEGENDARY|%d" % (n_, arm_(3))]
            return "\n".join(rows_)
        tok_, op_, loc_, iid_, key_, R_ = str(o[2]), str(o[3]), str(o[4]), str(o[5]), str(o[6]), int(o[7])
        WS["calls"].append((tok_, op_, loc_, iid_, key_, R_))
        if WS["mode"] == "moment":
            return "=One moment."
        if WS["mode"] == "nullact":
            return None
        if tok_ != WS["tok"]:
            return "=Your profile changed - here is your gear again. Nothing changed."
        st_ = w_stack(loc_)
        if st_ is None or str(st_.getItemId()) != iid_ or w_key(loc_, iid_) != key_:
            return "-That item moved or changed - nothing changed. Here is your gear again."
        if op_ == "sg" and WS["arm"] != (key_, R_):
            WS["arm"] = (key_, R_)
            return "=Click Confirm sigil to spend one Sigil - no way back."
        WS["arm"] = None
        WS["ver"][loc_] = WS["ver"].get(loc_, 0) + 1
        WS["purse"] -= 500
        return "+Done %s on %s" % (op_, iid_)
    BR.put("gear:fn:shop", Fn(w_fn))
    BR.put("requip:fn:presets", Fn(lambda o: "ok|0|2|18\n0|Combat|3|0|1|1\n1|Mining|2|1|1|1"))
    BR.put("requip:fn:preset", Fn(f_pre))
    BR.put("skill:fn:prog", Fn(lambda o: PROG))
    for k_ in ("tree:fn:map", "tree:fn:act"):
        BR.remove(k_)

    def w_ev(obj, what):
        E.pump(PW)
        f_ = len(E.sent(PW))
        PW.pm.getCustomPage().handleDataEvent(PW.ref, PW.st, json.dumps(obj))
        ps_ = pages(PW, f_)
        K.eq(len(ps_), 1, what + ": exactly ONE page packet")
        E.pump(PW)
        return ps_[0] if ps_ else None

    def w_mk(p_, ident):
        m_ = re.search(r"Label #%s \{[^}]*\}" % ident, mkt(p_))
        return m_.group(0) if m_ else ""
    SPW = SKP.open(PW.ref, PW.st, PW.pr, "Mining", "test")
    E.pump(PW)
    p_ = w_ev({"a": "sk:1"}, "SKL2 Mining page")
    cm = cmap(p_) if p_ else {}
    bw_ = [(a_, b_, c_.replace(" ", "")) for a_, b_, c_ in binds_of(p_)]
    K.check("Workshop" in mkt(p_) and ("SlotClicking", "#SkyySkpGtI", '{"a":"wt"}') in bw_ and ("SlotClicking", "#SkyySkpGaI", '{"a":"wa"}') in bw_ and not WS["reads"],
            "SKL2 PAGE the tool card's button = Workshop; the tool + armour slots are clickable; nothing asked before the workshop opens (%s)" % [b_ for b_ in bw_ if "Skp" in b_[1]][:3])
    l0_ = int(E.CM.lines.size())
    p_ = w_ev({"a": "up"}, "SKL2 OPEN Workshop (the tool card's button)")
    cm = cmap(p_) if p_ else {}
    mk_ = mkt(p_)
    SPW = PW.pm.getCustomPage()
    K.check(bool(SPW.wopen) and int(SPW.wsel) == 0 and vis_(cm, "TrV2") and hid_(cm, "TrV0") and hid_(cm, "TrV1") and hid_(cm, "TrL") and hid_(cm, "TrR")
            and sval(cm, "#SkyySkpTrO.Text") == "Skill tree" and sval(cm, "#SkyySkpTrT.Text") == "WORKSHOP" and int(E.CM.lines.size()) == l0_
            and str(SPW.getClass().getSimpleName()) == "SkillPage",
            "SKL2 OPEN Workshop = the tree panel's WORKSHOP view on this page (no old hub, no command), Skill tree to go back")
    K.eq(WS["reads"][-1:], ["0:0;3:0;-;-;1:7"], "SKL2 WHICH the read asks: the held pickaxe (hotbar 1), the worn helmet, no chest (not carried), no hands (nothing worn), the preset's legs in the bag")
    K.check(sval(cm, "#SkyySkpWnN.Text") == "Nice Tool_Pickaxe_Copper" and "#55FFFF" in w_mk(p_, "SkyySkpWnN") and str(sval(cm, "#SkyySkpWl.Text")).startswith("TOOL  -  Legendary  -  Lv 20")
            and str(sval(cm, "#SkyySkpWl.Text")).endswith("Hotbar 1") and sval(cm, "#SkyySkpWc.Text") == "Coins 5,000" and "Tool_Pickaxe_Copper" in cm.get("#SkyySkpWi.Slots", ""),
            "SKL2 DRAW the item row: icon, the name in its rarity colour, TOOL / rarity / level / where, your coins (%s)" % sval(cm, "#SkyySkpWl.Text"))
    K.check(sval(cm, "#SkyySkpWr0.Text") == "Next: Better Tool_Pickaxe_Copper (Lv 21)" and "#55FFFF" in w_mk(p_, "SkyySkpWr0") and "RenderBold: true" in w_mk(p_, "SkyySkpWr0")
            and sval(cm, "#SkyySkpWr1.Text") == "Iron collection IV (you II)" and "#ff7a7a" in w_mk(p_, "SkyySkpWr1")
            and sval(cm, "#SkyySkpWr2.Text") == "Iron Bar  12 / 20" and "#ff7a7a" in w_mk(p_, "SkyySkpWr2")
            and sval(cm, "#SkyySkpWr3.Text") == "Mining Lv 30 (you 60)" and "#7ee08a" in w_mk(p_, "SkyySkpWr3") and sval(cm, "#SkyySkpWr4.Text") == "Stone  9 / 5"
            and "#7ee08a" in w_mk(p_, "SkyySkpWr4") and sval(cm, "#SkyySkpWr5.Text") == "Not enough Iron Bar (need 8)." and "#ff7a7a" in w_mk(p_, "SkyySkpWr5")
            and sval(cm, "#SkyySkpWuB.Text") == "Cannot upgrade" and "#SkyySkpWr23" not in mkt(p_),
            "SKL2 DRAW UPGRADE: the next tier in its rarity colour, (fix round) the blocking rows first - red collection row, missing material - then "
            "the green rows, every material have / need, the why line, the button; no unidentified line on an identified item")
    K.check(sval(cm, "#SkyySkpWr20.Text") == "Coins 500" and "#7ee08a" in w_mk(p_, "SkyySkpWr20") and sval(cm, "#SkyySkpWr21.Text") == "Re-rolls every modifier for its rarity."
            and sval(cm, "#SkyySkpWr22.Text") == "Level up to Lv 21: Coins 900 (need 400)" and "#ff7a7a" in w_mk(p_, "SkyySkpWr22")
            and sval(cm, "#SkyySkpWfB.Text") == "Reforge" and sval(cm, "#SkyySkpWlB.Text") == "Not enough coins",
            "SKL2 DRAW REFORGE / LEVEL UP: the cost (green), the Anvil's line, the level-up line (red: coins short), both buttons")
    K.check(sval(cm, "#SkyySkpWr40.Text") == "This item: Normal" and sval(cm, "#SkyySkpWr41.Text") == "Rare Sigil (x1): Normal -> RARE" and "#FF55FF" in w_mk(p_, "SkyySkpWr41")
            and sval(cm, "#SkyySkpWr43.Text") == "Other fits: Legendary" and sval(cm, "#SkyySkpWsB.Text") == "Apply sigil" and list(SPW.wch) == [2, 3] and int(SPW.wsig) == 2,
            "SKL2 DRAW SIGIL: this item's rarity, the lowest Sigil that fits in its colour, Other fits, Apply sigil")
    K.check(not re.search(r"(?:Vertical|Horizontal)Alignment: (?:Top|Bottom)\b", mk_) and "Scrolling" not in mk_ and nometa(p_), "SKL2 DRAW no Top / Bottom alignment, no scrolling, no grid metadata")
    # ACT: the four buttons = ONE act each (token, op, place, id, key; the Sigil's R)
    k0_ = w_key("0:0", "Tool_Pickaxe_Copper")
    n0_ = len(WS["calls"])
    p_ = w_ev({"a": "wf"}, "SKL2 ACT Reforge")
    K.check(WS["calls"][n0_:] == [("ep1", "forge", "0:0", "Tool_Pickaxe_Copper", k0_, 0)] and sval(cmap(p_), "#SkyySkpCap.Text") == "Done forge on Tool_Pickaxe_Copper"
            and WS["reads"][-1] == "0:0;3:0;-;-;1:7" and "#SkyySkpWr0" in mkt(p_) and sval(cmap(p_), "#SkyySkpWc.Text") == "Coins 4,500",
            "SKL2 ACT Reforge = ONE gear:fn:shop act (token, forge, place, id, key), the answer = the caption, the page redrawn (read again) (%s)" % WS["calls"][n0_:])
    n0_ = len(WS["calls"])
    w_ev({"a": "wf"}, "SKL2 SAFE the same click on the redrawn page")
    K.check(WS["calls"][n0_][4] != k0_, "SKL2 SAFE the next click sends the NEW key (the stale key is never sent again)")
    w_ev({"a": "wl"}, "SKL2 ACT Level up")
    w_ev({"a": "wu"}, "SKL2 ACT Upgrade")
    K.eq([c_[1] for c_ in WS["calls"][-2:]], ["lvl", "up"], "SKL2 ACT Level up / Upgrade = ONE act each (lvl, up)")
    # Sigil: Apply arms (the stand-in = the Anvil's two clicks), the button reads Confirm sigil; Other = the next one; Confirm = the act with that R
    n0_ = len(WS["calls"])
    p_ = w_ev({"a": "ws"}, "SKL2 ACT Apply sigil")
    K.check(WS["calls"][n0_][1:] == ("sg", "0:0", "Tool_Pickaxe_Copper", w_key("0:0", "Tool_Pickaxe_Copper"), 2) and str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("Click Confirm sigil")
            and sval(cmap(p_), "#SkyySkpWsB.Text") == "Confirm sigil" and "#e8c25a" in w_mk(p_, "SkyySkpWr42"),
            "SKL2 ACT Apply sigil = act sg with the Rare Sigil (2); armed: the caption + Confirm sigil + the gold 10 s line")
    p_ = w_ev({"a": "wn"}, "SKL2 ACT Other")
    K.check(int(PW.pm.getCustomPage().wsig) == 3 and sval(cmap(p_), "#SkyySkpWr41.Text") == "Legendary Sigil (x2): Normal -> LEGENDARY" and sval(cmap(p_), "#SkyySkpWsB.Text") == "Apply sigil"
            and len(WS["calls"]) == n0_ + 1, "SKL2 ACT Other = the next Sigil that fits (no call); its arm is not this one's")
    w_ev({"a": "ws"}, "SKL2 ACT Apply the Legendary")
    p_ = w_ev({"a": "ws"}, "SKL2 ACT Confirm the Legendary")
    K.check([c_[5] for c_ in WS["calls"][-2:]] == [3, 3] and str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("Done sg"), "SKL2 ACT Apply + Confirm = two acts with R 3, done")
    # SAFE: '=One moment.' = the caption only; a profile switch between draw and click; the item moved; no answer
    WS["mode"] = "moment"
    p_ = w_ev({"a": "wf"}, "SKL2 SAFE double click")
    K.check(sval(cmap(p_), "#SkyySkpCap.Text") == "One moment." and "#SkyySkpWr0" not in mkt(p_), "SKL2 SAFE '=One moment.' = the caption only (no redraw)")
    WS["mode"] = "ok"
    WS["tok"] = "ep2"
    n0_ = len(WS["reads"])
    p_ = w_ev({"a": "wf"}, "SKL2 SAFE profile switch")
    K.check(WS["calls"][-1][0] == "ep1" and str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("Your profile changed") and len(WS["reads"]) == n0_ + 1
            and str(PW.pm.getCustomPage().wtok) == "ep2", "SKL2 SAFE a profile switch between draw and click = refused, said, redrawn with the new token")
    PW.slots["hotbar"].getInventory().removeItemStackFromSlot(JShort(0))
    PW.slots["hotbar"].getInventory().addItemStackToSlot(JShort(0), ISc("Tool_Pickaxe_Iron", 1))
    n0_ = len(WS["calls"])
    p_ = w_ev({"a": "wf"}, "SKL2 SAFE the item moved")
    K.check(WS["calls"][n0_][3] == "Tool_Pickaxe_Copper" and str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("That item moved") and WS["reads"][-1] == "0:0;3:0;-;-;1:7"
            and sval(cmap(p_), "#SkyySkpWnN.Text") == "Nice Tool_Pickaxe_Iron", "SKL2 SAFE another item in that place = the stand-in refuses (key), said, the new item drawn")
    WS["mode"] = "nullact"
    p_ = w_ev({"a": "wf"}, "SKL2 SAFE no answer")
    K.eq(sval(cmap(p_), "#SkyySkpCap.Text"), "The Anvil could not answer right now - nothing changed. Try again.", "SKL2 SAFE a null act answer = said")
    WS["mode"] = "ok"
    # ARMOUR: Head (worn), Chest (not carried), Hands (nothing worn), Legs (in the bag)
    p_ = w_ev({"a": "wa", "SlotIndex": 0}, "SKL2 ARMOUR Head")
    K.check(int(PW.pm.getCustomPage().wsel) == 1 and sval(cmap(p_), "#SkyySkpWnN.Text") == "Nice Armor_Iron_Head" and str(sval(cmap(p_), "#SkyySkpWl.Text")).startswith("HEAD  -  Legendary"),
            "SKL2 ARMOUR a click on the Head slot = the worn helmet on the workshop")
    w_ev({"a": "wl"}, "SKL2 ARMOUR Level up the helmet")
    K.eq(WS["calls"][-1][1:4], ("lvl", "3:0", "Armor_Iron_Head"), "SKL2 ARMOUR Level up = act lvl on the worn helmet's place")
    n0_ = len(WS["calls"])
    p_ = w_ev({"a": "wa", "SlotIndex": 1}, "SKL2 ARMOUR Chest (not carried)")
    K.check(str(sval(cmap(p_), "#SkyySkpWnN.Text")) == "CHEST - nothing to work on" and "Requip puts it on" in str(sval(cmap(p_), "#SkyySkpWl.Text")), "SKL2 ARMOUR a preset piece you do not carry = said")
    p_ = w_ev({"a": "wf"}, "SKL2 ARMOUR Reforge with nothing there")
    K.check(len(WS["calls"]) == n0_ and str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("Nothing to work on there"), "SKL2 ARMOUR nothing there = said, NO act")
    p_ = w_ev({"a": "wa", "SlotIndex": 2}, "SKL2 ARMOUR Hands (nothing worn)")
    K.check("You wear nothing on your hands" in str(sval(cmap(p_), "#SkyySkpWl.Text")), "SKL2 ARMOUR no preset piece + nothing worn = said")
    w_ev({"a": "wa", "SlotIndex": 3}, "SKL2 ARMOUR Legs (in the bag)")
    w_ev({"a": "wu"}, "SKL2 ARMOUR Upgrade the legs")
    K.eq(WS["calls"][-1][1:4], ("up", "1:7", "Armor_Iron_Legs"), "SKL2 ARMOUR the preset's legs in the bag = their place")
    # FIX (critic): the preset's chest is not on you but you wear another chest = that chest on the workshop
    ac_ = PW.slots["armor"].getInventory()          # the stand-in item has no armour data: the armour slot filter refuses it - put it past the filter
    m_ = None
    k_ = ac_.getClass()
    while k_ is not None and m_ is None:
        for dm_ in k_.getDeclaredMethods():
            if str(dm_.getName()) == "internal_setSlot":
                m_ = dm_
        k_ = k_.getSuperclass()
    m_.setAccessible(True)
    m_.invoke(ac_, JShort(1), ISc("Armor_Cloth_Chest", 1))
    K.check(w_stack("3:1") is not None, "SKL2FIX ARMOUR the stand-in chest is worn")
    p_ = w_ev({"a": "wa", "SlotIndex": 1}, "SKL2FIX ARMOUR Chest (another one worn)")
    w_ev({"a": "wf"}, "SKL2FIX ARMOUR Reforge the worn chest")
    K.check(sval(cmap(p_), "#SkyySkpWnN.Text") == "Nice Armor_Cloth_Chest" and WS["calls"][-1][1:4] == ("forge", "3:1", "Armor_Cloth_Chest"),
            "SKL2FIX ARMOUR the preset's piece not on you + another piece worn there = the worn piece on the workshop (act on 3:1) (%s / %s / %s / %s)"
            % (sval(cmap(p_), "#SkyySkpWnN.Text"), sval(cmap(p_), "#SkyySkpWl.Text"), WS["calls"][-1], WS["reads"][-1:]))
    m_.invoke(ac_, JShort(1), None)
    K.check(w_stack("3:1") is None, "SKL2FIX ARMOUR the stand-in chest is off again")
    # FIX (critic): many upgrade materials - the missing ones are always drawn (first); two short ones share a line; too many = "+ N more"
    WS["mats"] = [("Ore_Coal", 10, 30, "Coal"), ("Ore_Tin", 10, 30, "Tin"), ("Ore_Lead", 10, 30, "Lead"), ("Ore_Zinc", 10, 30, "Zinc"),
                  ("Ore_Gold", 10, 2, "Gold"), ("Ore_Ruby", 10, 1, "Ruby")]
    p_ = w_ev({"a": "wa", "SlotIndex": 0}, "SKL2FIX UPGRADE six materials")
    cm = cmap(p_)
    wr_ = [(sval(cm, "#SkyySkpWr%d.Text" % i_), w_mk(p_, "SkyySkpWr%d" % i_)) for i_ in range(1, 20) if sval(cm, "#SkyySkpWr%d.Text" % i_) is not None]
    tx_ = " / ".join(str(t_) for t_, m_ in wr_)
    K.check(len(wr_) > 2 and wr_[0][0] == "Iron collection IV (you II)" and "Gold  2 / 10" in str(wr_[1][0]) and "Ruby  1 / 10" in str(wr_[1][0]) and "#ff7a7a" in wr_[1][1]
            and (all(x_ in tx_ for x_ in ("Coal  30 / 10", "Tin  30 / 10", "Lead  30 / 10", "Zinc  30 / 10", "Mining Lv 30")) or "more - you have them" in tx_)
            and "some are missing" not in tx_ and str(wr_[-1][0]) == "Not enough Iron Bar (need 8).",
            "SKL2FIX UPGRADE six materials: the red rows first, two missing materials on one line, the rest shown (or '+ N more - you have them'), the why line kept (%s)" % tx_)
    WS["mats"] = [("Ore_%d" % i_, 10, 30, "Mat%d" % i_) for i_ in range(12)] + [("Ore_Gold", 10, 2, "Gold"), ("Ore_Ruby", 10, 1, "Ruby")]
    p_ = w_ev({"a": "wa", "SlotIndex": 0}, "SKL2FIX UPGRADE fourteen materials")
    cm = cmap(p_)
    wr_ = [(sval(cm, "#SkyySkpWr%d.Text" % i_), w_mk(p_, "SkyySkpWr%d" % i_)) for i_ in range(1, 20) if sval(cm, "#SkyySkpWr%d.Text" % i_) is not None]
    tx_ = " / ".join(str(t_) for t_, m_ in wr_)
    K.check(len(wr_) > 2 and "Gold  2 / 10" in tx_ and "Ruby  1 / 10" in tx_ and any(str(t_).startswith("+ ") and str(t_).endswith("more - you have them") for t_, m_ in wr_)
            and str(wr_[-1][0]) == "Not enough Iron Bar (need 8)." and "the Anvil lists them" not in mkt(p_) and "Scrolling" not in mkt(p_),
            "SKL2FIX UPGRADE fourteen materials: the missing ones drawn, the rest '+ N more - you have them' (no old-menu pointer), the why line kept (%s)" % tx_)
    WS["mats"] = [("Ore_%d" % i_, 10, 30, "Mat%d" % i_) for i_ in range(12)] + [("Ore_Gold%d" % i_, 10, 2, "Gold%d" % i_) for i_ in range(12)]
    p_ = w_ev({"a": "wa", "SlotIndex": 0}, "SKL2FIX UPGRADE too many missing")
    cm = cmap(p_)
    wr_ = [(sval(cm, "#SkyySkpWr%d.Text" % i_), w_mk(p_, "SkyySkpWr%d" % i_)) for i_ in range(1, 20) if sval(cm, "#SkyySkpWr%d.Text" % i_) is not None]
    K.check(any(str(t_).startswith("+ ") and str(t_).endswith("more - some are missing") and "#ff7a7a" in m_ for t_, m_ in wr_) and "Mat0" not in " ".join(str(t_) for t_, m_ in wr_),
            "SKL2FIX UPGRADE more missing materials than fit: the red ones first, '+ N more - some are missing' in red (%s)" % [str(t_) for t_, m_ in wr_])
    WS["mats"] = [("Ingredient_Bar_Iron", 20, 12, "Iron Bar"), ("Rock_Stone", 5, 9, "Stone")]
    # FIX (critic): unidentified gear says where to identify it
    WS["unid"] = 1
    p_ = w_ev({"a": "wa", "SlotIndex": 0}, "SKL2FIX unidentified")
    K.check(sval(cmap(p_), "#SkyySkpWr23.Text") == "Unidentified: identify it with /identify first, then come back." and "#ff7a7a" in w_mk(p_, "SkyySkpWr23")
            and str(sval(cmap(p_), "#SkyySkpWl.Text")).endswith("unidentified"), "SKL2FIX unidentified = a red line naming /identify in the Reforge card")
    WS["unid"] = 0
    p_ = w_ev({"a": "wa", "SlotIndex": 9}, "SKL2 ARMOUR a bad slot")
    K.eq(sval(cmap(p_), "#SkyySkpCap.Text"), "Nothing there", "SKL2 ARMOUR a bad slot index = said")
    # EVERY SKILL PAGE: the tool + an armour piece of Mining, Foraging, Farming, Fishing, Combat = ONE act each on the right place
    want_ = {1: ("0:0", "Tool_Pickaxe_Iron"), 2: ("0:1", "Tool_Hatchet_Iron"), 3: ("1:3", "Tool_Hoe_Iron"), 4: ("1:4", "SkyyFishing_Rod_Wood"), 0: ("0:2", "Weapon_Sword_Iron")}
    got_ = {}
    for si_ in (1, 2, 3, 4, 0):
        w_ev({"a": "sk:%d" % si_}, "SKL2 SKILLS page %d" % si_)
        K.check(bool(PW.pm.getCustomPage().wopen) and int(PW.pm.getCustomPage().wsel) == 0, "SKL2 SKILLS the workshop stays open on the new skill's tool (%d)" % si_)
        w_ev({"a": "wf"}, "SKL2 SKILLS tool act %d" % si_)
        t_ = WS["calls"][-1]
        w_ev({"a": "wa", "SlotIndex": 0}, "SKL2 SKILLS armour %d" % si_)
        w_ev({"a": "ws"}, "SKL2 SKILLS armour act %d" % si_)
        a_ = WS["calls"][-1]
        got_[si_] = ((t_[1], t_[2], t_[3]), (a_[1], a_[2], a_[3]))
    K.eq(got_, dict((k_, (("forge",) + v_, ("sg", "3:0", "Armor_Iron_Head"))) for k_, v_ in want_.items()),
         "SKL2 SKILLS Mining / Foraging / Farming / Fishing / Combat: the tool (held / preset / best carried) + the helmet = ONE act each on its place")
    # NO GEAR / NO ANSWER / A BAD COLOUR
    WS["mode"] = "null"
    p_ = w_ev({"a": "sk:1"}, "SKL2 FALL no read answer")
    K.check("The Anvil could not answer" in str(sval(cmap(p_), "#SkyySkpWl.Text")), "SKL2 FALL a null read = said")
    WS["mode"] = "ok"
    WS["hex"] = 'red"; } Label { Text: "x'
    p_ = w_ev({"a": "sk:1"}, "SKL2 SAFE a bad colour")
    K.check('Label { Text: "x' not in mkt(p_) and "#d6e4ee" in w_mk(p_, "SkyySkpWnN"), "SKL2 SAFE a colour that is not #rrggbb never reaches the markup (the text colour instead)")
    WS["hex"] = "#55FFFF"
    BR.remove("gear:fn:shop")
    n0_ = len(WS["calls"])
    p_ = w_ev({"a": "sk:1"}, "SKL2 FALL no SkyyGear 0.3.60")
    K.check("needs SkyyGear 0.3.60" in str(sval(cmap(p_), "#SkyySkpWl.Text")), "SKL2 FALL without gear:fn:shop = said in the workshop")
    p_ = w_ev({"a": "wf"}, "SKL2 FALL a click without SkyyGear 0.3.60")
    K.check(len(WS["calls"]) == n0_ and "needs SkyyGear 0.3.60" in str(sval(cmap(p_), "#SkyySkpCap.Text")), "SKL2 FALL a click = said, nothing called")
    BR.put("gear:fn:shop", Fn(w_fn))
    # Skill tree <-> Workshop; with the inline tree the old Full tree is gone (Workshop instead)
    p_ = w_ev({"a": "tr"}, "SKL2 Skill tree (close the workshop)")
    K.check(not bool(PW.pm.getCustomPage().wopen) and not vis_(cmap(p_), "TrV2") and vis_(cmap(p_), "TrV0") and sval(cmap(p_), "#SkyySkpTrO.Text") == "Open tree",
            "SKL2 TREE Skill tree = back to the tree panel (here no inline tree: Open tree)")
    BR.put("tree:fn:map", Fn(tm_map))
    BR.put("tree:fn:act", Fn(tm_act))
    TMW["mode"], TMW["n"], TMW["s"] = "ok", 5, 32
    p_ = w_ev({"a": "sk:1"}, "SKL2 TREE inline")
    K.check(vis_(cmap(p_), "TrV1") and sval(cmap(p_), "#SkyySkpTrO.Text") == "Workshop" and "Full tree" not in mkt(p_), "SKL2 TREE the inline tree's button = Workshop (the old Full tree is gone)")
    c0_ = len(TMW["calls"])
    l0_ = int(E.CM.lines.size())
    p_ = w_ev({"a": "tr"}, "SKL2 TREE Workshop from the inline tree")
    K.check(bool(PW.pm.getCustomPage().wopen) and vis_(cmap(p_), "TrV2") and len(TMW["calls"]) == c0_ and int(E.CM.lines.size()) == l0_ and "#SkyySkpTn0 " not in mkt(p_),
            "SKL2 TREE Workshop = the workshop (no /tree command, the map not drawn under it)")
    p_ = w_ev({"a": "tr"}, "SKL2 TREE back")
    K.check(not bool(PW.pm.getCustomPage().wopen) and vis_(cmap(p_), "TrV1") and len(TMW["calls"]) == c0_ + 1, "SKL2 TREE Skill tree = the inline tree again")
    w_ev({"a": "wt"}, "SKL2 the tool slot")
    K.check(bool(PW.pm.getCustomPage().wopen) and int(PW.pm.getCustomPage().wsel) == 0, "SKL2 a click on the tool slot = the tool on the workshop")
    for k_ in ("tree:fn:map", "tree:fn:act", "gear:fn:shop", "requip:fn:presets", "requip:fn:preset", "skill:fn:prog"):
        BR.remove(k_)
    PW.pm.getCustomPage().handleDataEvent(PW.ref, PW.st, '{"a":"close"}')
    E.pump(PW)
'''
T.rep('''"""Harness for SkyyMenu 0.3.67 (the Requip slot picker + Auto best gear; tools/menu_0_3_67_patch.py, round req2).
GENERATED by tools/menu_0_3_67_patch.py from the 0.3.66 harness (edit the patch, not this file): every 0.3.66 check runs again on the
0.3.67 jar''', '''"""Harness for SkyyMenu 0.3.68 (the skill page workshop; tools/menu_0_3_68_patch.py, round skl2).
GENERATED by tools/menu_0_3_68_patch.py from the 0.3.67 harness (edit the patch, not this file): every 0.3.67 check runs again on the
0.3.68 jar (TREEMAP1: the inline tree's button reads Workshop, not Full tree), plus
  SKL2 (EXECUTED on a fresh stand-in player with a REAL inventory and a Python stand-in of SkyyGear 0.3.60 gear:fn:shop (read / act; its
       real answers = the Anvil's own code: SkyyGear/test_skyygear_0.3.60.py)):
       OPEN    Workshop / the tool slot / an armour slot = the WORKSHOP view of the tree panel (ONE packet, no old hub, no command)
       WHICH   the held tool of the skill, the preset's armour worn or carried, the worn piece without a preset piece; not carried = said
       DRAW    the item row (rarity-coloured name, slot / rarity / level / where, coins), UPGRADE (next tier in its colour, rows + materials have /
               need green / red, why), REFORGE / LEVEL UP, SIGIL (the Sigil that fits in its colour, Other, Apply -> Confirm sigil)
       ACT     each button = ONE act (token, op, place, id, key, R); the answer = the caption + ONE packet; Other = no call
       SAFE    '=One moment.' = the caption only; a stale token / the item moved = refused + redrawn; the new key is sent next; nothing there = no
               act; a bad colour never reaches the markup; no answer / no SkyyGear 0.3.60 = said
       SKILLS  Mining / Foraging / Farming / Fishing / Combat: the tool + the helmet = ONE act each on the right place
       TREE    Skill tree <-> Workshop; the inline tree's old Full tree button is now Workshop
  SKL2FIX (fix round): a worn non-preset piece is worked on; the Upgrade card draws the blocking rows first, pairs materials, '+ N more';
       unidentified gear names /identify
The 0.3.67 harness text follows:
Harness for SkyyMenu 0.3.67 (the Requip slot picker + Auto best gear; tools/menu_0_3_67_patch.py, round req2).
GENERATED by tools/menu_0_3_67_patch.py from the 0.3.66 harness (edit the patch, not this file): every 0.3.66 check runs again on the
0.3.67 jar''')
T.rep('VERSION = "0.3.67"\nJAR', 'VERSION = "0.3.68"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.66.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.67.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.66.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.67.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_67_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_68_patch.py")')
T.rep('"scratch", "req2", "menu"', '"scratch", "skl2", "menu"')
T.rep('ADDED = []   # 0.3.67: no new class\n', 'ADDED = []   # 0.3.68: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.67:', 'if "--expect-dump" in sys.argv:'), EXPECT_68)
T.rep('''    K.check(g.count('VERSION = "0.3.67"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.68"') == 1, "S VERSION")
    K.check("0.3.68: the workshop fits the tree panel" in g and "0.3.68: a card's buttons fit" in g and "0.3.68: the workshop markups are proven" in g
            and "0.3.68: the row line length" in g, "SKL2 STATIC the build asserts the workshop fits, its buttons fit, its run-time markups are proven")''')
T.rep('''and vis_(cm, "TrL") and vis_(cm, "TrR") and sval(cm, "#SkyySkpTrO.Text") == "Full tree"''',
      '''and vis_(cm, "TrL") and vis_(cm, "TrR") and sval(cm, "#SkyySkpTrO.Text") == "Workshop"''')
T.rep('''            "TREEMAP1 DRAW the inline view: branch titles, SkyyTrees' points line, Learn / Respec / Full tree (%s)" % sval(cm, "#SkyySkpTrP.Text"))''',
      '''            "TREEMAP1 DRAW the inline view: branch titles, SkyyTrees' points line, Learn / Respec / (0.3.68) Workshop (%s)" % sval(cm, "#SkyySkpTrP.Text"))''')
T.rep('''    # ---- MENUFIX1 (0.3.60; Skyy 11-21: "crafting doesnt work at all.",''', HARNESS_SKL2 + '''    # ---- MENUFIX1 (0.3.60; Skyy 11-21: "crafting doesnt work at all.",''')
if T.dst:
    T.finish()
