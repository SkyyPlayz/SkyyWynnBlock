"""Derive SkyyMenu/build_skyymenu_0.3.61.py + SkyyMenu/test_skyymenu_0.3.61.py from the SET pin SkyyMenu 0.3.60 (generated - never re-run
its patch). Run:  python tools/menu_0_3_61_patch.py   then   python SkyyMenu/build_skyymenu_0.3.61.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.61.py   (+ the end-to-end draw on the REAL SkyyTrees 0.6.10: SkyyTrees/test_skyytrees_0.6.10.py, phase inline)
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.60 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.61 (2026-11-22, round treemap1, with SkyyTrees 0.6.10) = THE SKILL TREE INLINE ON EVERY SKILL PAGE. Skyy 2026-11-21 (Smithing skill page):
"i wan it to show the smithing skill tree below, not a button to open the old skill tree." (docs/answered/ui.md 2026-11-21 INVENTORY + SKILLS
TAB TEST, point 3; left over from menufix1 / 0.3.60).
  THE TREE PANEL (the lower middle of the skill page, where 'SKILL TREE / Open tree' was - same 808 x 318 panel, nothing else moves):
    header row: SKILL TREE | the tree's points line (SkyyTrees' own: "7 of 30 points free - row 4 opens at 15") | Learn (Rank up once the
    selected node has a rank) | Respec (Confirm while armed) | Full tree (the old /tree page - the small link Skyy's words allow).
    under it ONE holder (kit 1.9 keep_holder, .Visible only): the inline tree = the MAP (520 x 264: the tree's branches side by side, rows top
    to bottom, each node = SkyyTrees' own /tree map state picture SkyyTrees/Map/Node/<state>.png + its icon + a click square - NO new picture,
    the selected node gets the /tree map's Halo.png) + the NODE PANEL (258 wide: name, rank, state, now, next, cost, needs - the /tree page's own
    texts; nothing selected = how to use it, PERKS NOW, the respec price, on Combat the ABILITIES line).
    Combat = your class tree ("Class"); a skill without a tree (Ranching, Orchard) / class trees off / no class yet = SkyyTrees' own sentence
    in the map box.
  THE BRIDGE (SkyyTrees 0.6.10, plain java.lang types): tree:fn:map apply(Object[] { UUID, tree name, Integer selected }) -> lines (read only,
    every build); tree:fn:act apply(Object[] { UUID, profile token (from the read), "learn" | "respec", arg }) -> "+done" / "-refused" /
    "=info" (SkyyTrees runs its EXACT TreeV3.buy / respec: points, gates, paths, costs, History, coins, combat; the token, the world thread and a
    350 ms same-op guard there). The menu adds no rule and no number: a click = ONE act call, the answer as the caption, ONE page packet
    (rebuild); "=One moment." (a double click) = the caption only. Learn sends "<tree>|<k>|<node code>" as drawn - SkyyTrees refuses a node
    that is no longer the k-th of that tree ("That tree changed"); a stale token = "Your profile changed" and the selection is cleared.
  CHECKED before drawing (else the 0.3.60 view): the header (17 fields, canvas = 520 x 264, node size 12-40), every node line (k in order,
    inside the canvas, the state picture name [A-Za-z0-9] only, the icon id [A-Za-z0-9_] or '-' and drawn only when the server knows it), at
    most 120 nodes + 8 branches; the map is drawn whole or not at all.
  FALLBACK (SkyyTrees 0.6.9 or older = no tree:fn:map / tree:fn:act, or an answer that fails a check): EXACTLY the 0.3.60 panel - the points
    from tree:<uuid>, the ABILITIES line, PERKS NOW, the 'Open tree' button (/tree <skill>); Learn / Respec hidden.
  ELEMENTS: the skill page stays under the ~1,600 budget (printed at build: shell + at most 120 nodes x 3 + 8 branch labels + the halo).
  Every bound click still answers with exactly ONE page packet; no Top / Bottom alignment; inline pages only; slot lists through InvPage.act.
  No new command, setting, lang key, system, picture or saved data. ROLLBACK to 0.3.60: safe alone (nothing saved; the panel = Open tree).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.60.py"), os.path.join(MOD, "build_skyymenu_0.3.61.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.60.py"), os.path.join(MOD, "test_skyymenu_0.3.61.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.60"\n') and P.has("tools/menu_0_3_60_patch.py") and P.has("public static java.util.ArrayList act(")
assert not P.has("tree:fn:map"), "not the generated SkyyMenu 0.3.60 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.60: MENU FIX ROUND''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.61: THE SKILL TREE INLINE ON EVERY SKILL PAGE (Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill
       tree."): the tree panel draws that skill's tree (Combat = your class tree) with SkyyTrees' own map pictures - click a node to see it,
       Learn / Rank up, the points line, Respec (two presses), a small Full tree link; SkyyTrees 0.6.10 tree:fn:map + tree:fn:act; without
       them the 0.3.60 panel with Open tree (notes: tools/menu_0_3_61_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.61.py.
0.3.60: MENU FIX ROUND''')
P.rep('VERSION = "0.3.60"\n', 'VERSION = "0.3.61"\n')

# ---------- the geometry of the tree panel
P.rep('''SK_HDBW = SK_MI - 72 - 12 - 300 - 8 - 84 - 12              # the header's XP bar
''', '''SK_HDBW = SK_MI - 72 - 12 - 300 - 8 - 84 - 12              # the header's XP bar
# 0.3.61: THE INLINE TREE (Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree."): the tree
# panel = a header row + ONE holder (the 0.3.60 view, or the map canvas + the node panel). The canvas = SkyyTrees 0.6.10 TreeLineFn W x H.
SK_TMW, SK_TMH = 520, 264                                  # the map canvas (= SkyyTrees 0.6.10 TL_W x TL_H; checked on every read)
SK_TDW = SK_MI - SK_TMW - 10                               # the node panel (258)
SK_TDI = SK_TDW - 16                                       # its text width (pad 8)
SK_TRLW, SK_TRBW, SK_TROW = 130, 100, 120                  # the header row: the title, Learn / Respec, Full tree
SK_TRPW = SK_MI - SK_TRLW - 2 * (SK_TRBW + 6) - SK_TROW    # the points line (326)
SK_TMAXN, SK_TBMAX, SK_TSMIN, SK_TSMAX = 120, 8, 12, 40    # at most 120 nodes / 8 branches a tree, node size 12-40 px (else the 0.3.60 view)
SK_TMAP_DIR = "SkyyTrees/Map/"                             # SkyyTrees' own map pictures (its jar ships them; this jar ships none)
assert SK_TDW >= 250 and SK_TRPW >= 300 and 30 + 4 + SK_TMH + 20 == IV_BODY_H - SK_HD_H - SK_GR_H - SK_PA_H - 3 * 8, "0.3.61: the tree panel fits"
''')

# ---------- the markup: the header row + the holder (0.3.60 view | the inline tree)
P.rep('''    # D) SKILL TREE: points + PERKS NOW + Open tree
    tr = SK + "Tr"
    ap.append(("#" + md, G_.glass_group(tr, SK_M, SK_TR_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    trr = SK + "Trr"
    ap.append(("#" + tr, G_.glass_group(trr, SK_MI, 30, layout="Left")))
    ap.append(("#" + trr, lab(None, "SKILL TREE", 15, "accentHi", bold=True, w=160, h=30)))
    ap.append(("#" + trr, lab(SK + "TrP", "", 13, "xp", bold=True, w=SK_MI - 160 - 170, h=30)))
    ap.append(("#" + trr, G_.glass_button(SK + "TrO", "Open tree", "primary", w=170, h=30, size=14)))
    # the Combat page's ABILITIES line (Skyy 11-14: "the COMBAT skill page holds your class (abilities, class tree, combat gear)"; read only,
    # SkyyClasses class:fn:abil - the 4 slots' names + state; empty on every other skill)
    ap.append(("#" + tr, lab(SK + "TrA", "", 13, "gold", bold=True, w=SK_MI, h=22, anchor={"top": 6})))
    ap.append(("#" + tr, lab(None, "PERKS NOW", 12, "dim", bold=True, w=SK_MI, h=20, anchor={"top": 8})))
    for k_ in range(SK_TRN):
        ap.append(("#" + tr, lab(SK + "Tl%d" % k_, "", 13, "text", w=SK_MI, h=26)))
    assert 20 + 30 + 28 + 28 + SK_TRN * 26 <= SK_TR_H, ("0.3.57: the tree panel fits (+ the ABILITIES line)", SK_TR_H)
''', '''    # D) SKILL TREE (0.3.61): the header row (points, Learn, Respec, Full tree) + ONE holder: the 0.3.60 view (ABILITIES + PERKS NOW - the
    # fallback without SkyyTrees 0.6.10) or the INLINE TREE (the map canvas + the node panel); .Visible only (kit 1.9 keep_holder)
    tr = SK + "Tr"
    ap.append(("#" + md, G_.glass_group(tr, SK_M, SK_TR_H, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    trr = SK + "Trr"
    ap.append(("#" + tr, G_.glass_group(trr, SK_MI, 30, layout="Left")))
    ap.append(("#" + trr, lab(None, "SKILL TREE", 15, "accentHi", bold=True, w=SK_TRLW, h=30)))
    ap.append(("#" + trr, lab(SK + "TrP", "", 13, "xp", bold=True, w=SK_TRPW, h=30)))
    ap.append(("#" + trr, SUI.keep_hide(G_.glass_button(SK + "TrL", "Learn", "primary", w=SK_TRBW, h=30, size=13, anchor={"right": 6}))))
    ap.append(("#" + trr, SUI.keep_hide(G_.glass_button(SK + "TrR", "Respec", "secondary", w=SK_TRBW, h=30, size=13, anchor={"right": 6}))))
    ap.append(("#" + trr, G_.glass_button(SK + "TrO", "Open tree", "primary", w=SK_TROW, h=30, size=13)))
    v0_ = SUI.keep_at0(G_.glass_group(SK + "TrV0", SK_MI, SK_TMH, layout="Top"))
    v1_ = SUI.keep_hide(SUI.keep_at0(G_.glass_group(SK + "TrV1", SK_MI, SK_TMH, layout="Left")))
    hm_, kids_ = SUI.keep_holder(SK + "TrH", SK_MI, SK_TMH, [v0_, v1_], anchor={"top": 4})
    ap.append(("#" + tr, hm_))
    ap.extend(kids_)
    v0 = "#" + SK + "TrV0"
    # the Combat page's ABILITIES line (Skyy 11-14: "the COMBAT skill page holds your class (abilities, class tree, combat gear)"; read only,
    # SkyyClasses class:fn:abil - the 4 slots' names + state; empty on every other skill)
    ap.append((v0, lab(SK + "TrA", "", 13, "gold", bold=True, w=SK_MI, h=22, anchor={"top": 6})))
    ap.append((v0, lab(None, "PERKS NOW", 12, "dim", bold=True, w=SK_MI, h=20, anchor={"top": 8})))
    for k_ in range(SK_TRN):
        ap.append((v0, lab(SK + "Tl%d" % k_, "", 13, "text", w=SK_MI, h=26)))
    assert 6 + 22 + 8 + 20 + SK_TRN * 26 <= SK_TMH, ("0.3.61: the 0.3.60 view fits its holder", SK_TMH)
    # the inline tree: the canvas (no LayoutMode - every node sits by its own Anchor, appended at run time) + the node panel
    v1 = "#" + SK + "TrV1"
    ap.append((v1, G_.glass_group(SK + "Tm", SK_TMW, SK_TMH, role="inset", layout=None)))
    ap.append(("#" + SK + "Tm", SUI.keep_at0(lab(SK + "TmM", "", 14, "dim", w=SK_TMW, h=SK_TMH, halign="Center"))))
    ap.append((v1, "Group { Anchor: (Width: 10); }"))
    td = SK + "Td"
    ap.append((v1, G_.glass_group(td, SK_TDW, SK_TMH, role="inset", layout="Top", pad=8)))
    used_ = 0
    for id_, sz_, col_, bold_, h_, lines_, top_ in SK_TD_ROWS:
        ap.append(("#" + td, sk_wrap(SK + id_, sz_, col_, bold_, SK_TDI, h_, lines_, top_)))
        used_ += h_ + top_
    assert used_ <= SK_TMH - 16, ("0.3.61: the node panel fits", used_)
''')
# the node panel's rows + the wrapping label (the kit's glass colours; Wrap + a character clip: a text never runs past its box)
P.rep('''def _sk_page():
    ap = SUI.Appends()''', '''# 0.3.61: the node panel rows: (id, size, colour, bold, height, max lines, top gap) - name, rank, state, now, next, cost, needs
SK_TD_ROWS = [("Dn", 14, "title", True, 20, 1, 0), ("Dr", 12, "gold", True, 16, 1, 2), ("Ds", 12, "text", False, 30, 2, 4),
              ("Dw", 12, "green", False, 44, 3, 4), ("Dx", 12, "text", False, 44, 3, 4), ("Dc", 12, "dim", False, 16, 1, 4),
              ("De", 12, "red", False, 44, 3, 4)]
SK_TD_CLIP = dict((r_[0], (34 if r_[0] == "Dn" else (40 * r_[5] - 4))) for r_ in SK_TD_ROWS)   # characters (12 px ~ 6 px a character, 242 px)


def sk_wrap(ident, size, col, bold, w, h, lines, top):
    """0.3.61: a Skyglass label that wraps onto `lines` lines inside its box (Wrap: true; WrapMaxLines is not proven in game - the run time
    clips every text to SK_TD_CLIP characters, about `lines` lines of 242 px)"""
    st = SUI.text_style(size, SUI.glass_col(col), bold=bold, wrap=lines > 1)
    return "Label #%s { %sStyle: %s; }" % (SUI.check_id(ident), SUI._anchor(w, h, {"top": top} if top else None), st)


def _sk_page():
    ap = SUI.Appends()''')
# the bindings: + Learn, Respec (the node clicks are bound at run time)
P.rep('''        ("#" + SK + "TrO", "tr"), ("#" + SK + "ShGo", "sh")]
    return ap, binds''', '''        ("#" + SK + "TrO", "tr"), ("#" + SK + "ShGo", "sh"), ("#" + SK + "TrL", "tl"), ("#" + SK + "TrR", "trs")]   # 0.3.61: + Learn, Respec
    return ap, binds''')
P.rep('''           + ["Tl%d" % k_ for k_ in range(SK_TRN)] + ["Gr%d" % k_ for k_ in range(SK_GN // 2)]''',
      '''           + ["Tl%d" % k_ for k_ in range(SK_TRN)] + ["Gr%d" % k_ for k_ in range(SK_GN // 2)]
           + ["TrL", "TrR", "TrH", "TrV0", "TrV1", "Tm", "TmM", "Td"] + [r_[0] for r_ in SK_TD_ROWS]   # 0.3.61''')
# the run-time markups of the inline tree (checked like every page markup) + the element budget
P.rep('''SK_RUNTIME_MAX = SK_GN * (_cell_el + 1) + 2      # the 12 cells + their XP fills + the header / shard bar fills
SK_ELEMENTS = SK_SHELL_ELEMENTS + SK_RUNTIME_MAX
assert SK_ELEMENTS <= 800, "0.3.57: the skill page stays well under the ~1,600 element budget (%d static + %d at run time)" % (SK_SHELL_ELEMENTS, SK_RUNTIME_MAX)''',
      '''# 0.3.61: the inline tree's run-time markups (Python samples -> Java templates): a node = SkyyTrees' state picture (Group Background) + its
# icon (ItemIcon) + the click square (the kit's map_hit), the selected node's halo, a branch title. Pictures: SkyyTrees/Map/Node/<state>.png
# and SkyyTrees/Map/Halo.png - SkyyTrees ships them (0.6.9 lean pictures); this jar ships none (tools/ci/ui_budget.py unchanged).
SUI.register_map_textures([SK_TMAP_DIR + "Node/Ready.png", SK_TMAP_DIR + "Halo.png"])
_tn = SUI.map_pic(SK + "Tn7771", 7772, 7773, 7774, 7774, SK_TMAP_DIR + "Node/Ready.png")
_ti = SUI.item_icon(SK + "Tn7771I", "Rock_Stone", size=7775, anchor={"left": 7776, "top": 7777})
_th = SUI.map_hit(SK + "Tn7771B", 7776, 7777, 7775)
_ts = SUI.map_pic(SK + "Ts", 7776, 7777, 7775, 7775, SK_TMAP_DIR + "Halo.png")
_tb = SUI.glass_label(SK + "Tb7771", "", 11, "accentHi", bold=True, w=7778, h=16, halign="Center", anchor={"left": 7776, "top": 7777})
for _mk in (_tn, _ti, _th, _ts, _tb):
    SUI.check_markup(_mk, prefix=SK, kit_paths=True)
    assert "@" not in _mk and "\\n" not in _mk and "Scrolling" not in _mk, "0.3.61: a run-time markup line Java can hold"
_tok61 = SUI.proven_tokens([("#" + SK + "Tm", _m) for _m in (_tn, _ti, _th, _ts, _tb)])
assert not [k_ for k_, g_ in _tok61.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_))], ("0.3.61: the tree markups are proven", _tok61)
SK_TNODE = _tn.replace("7771", "{I}").replace("7772", "{L}").replace("7773", "{T}").replace("7774", "{S}").replace("Node/Ready.png", "Node/{N}.png")
SK_TICON = _ti.replace("7771", "{I}").replace("7775", "{Z}").replace("7776", "{L}").replace("7777", "{T}").replace("Rock_Stone", "{D}")
SK_THIT = _th.replace("7771", "{I}").replace("7775", "{Z}").replace("7776", "{L}").replace("7777", "{T}")
SK_THALO = _ts.replace("7775", "{Z}").replace("7776", "{L}").replace("7777", "{T}")
SK_TBR = _tb.replace("7771", "{I}").replace("7778", "{W}").replace("7776", "{L}").replace("7777", "{T}")
for _t, _keys in ((SK_TNODE, "ILTSN"), (SK_TICON, "IZLTD"), (SK_THIT, "IZLT"), (SK_THALO, "ZLT"), (SK_TBR, "IWLT")):
    assert not re.search(r"777\\d", _t) and all(("{%s}" % c_) in _t for c_ in _keys), ("0.3.61: a template with every placeholder", _t)
_cnt = lambda mk_: len(re.findall(r"(?:^|(?<=[;{}]))\\s*[A-Z][A-Za-z]*(?:\\s+#[A-Za-z0-9{}]+)?\\s*\\{", SUI._strip_quoted(mk_)))
SK_TREE_RUNTIME = SK_TMAXN * (_cnt(_tn) + _cnt(_ti) + _cnt(_th)) + SK_TBMAX * _cnt(_tb) + _cnt(_ts)
SK_RUNTIME_MAX = SK_GN * (_cell_el + 1) + 2 + SK_TREE_RUNTIME      # the 12 cells + their XP fills + the header / shard bar fills + 0.3.61 the tree
SK_ELEMENTS = SK_SHELL_ELEMENTS + SK_RUNTIME_MAX
assert SK_TREE_RUNTIME == SK_TMAXN * 3 + SK_TBMAX + 1, ("0.3.61: a node = 3 elements", SK_TREE_RUNTIME)
assert SK_ELEMENTS <= 1200, "0.3.61: the skill page stays well under the ~1,600 element budget (%d static + %d at run time)" % (SK_SHELL_ELEMENTS, SK_RUNTIME_MAX)
print("0.3.61 inline tree: canvas %d x %d, node panel %d; at most %d nodes (%d elements) + %d branch titles + the halo; skill page worst case %d elements"
      % (SK_TMW, SK_TMH, SK_TDW, SK_TMAXN, SK_TMAXN * 3, SK_TBMAX, SK_ELEMENTS))''')

# ---------- the Java data
P.rep('''F(sdat, "public static final String[] LADDER = %s;" % jarr(list(_TT57.LADDER)))''', '''F(sdat, "public static final String[] LADDER = %s;" % jarr(list(_TT57.LADDER)))
for _n, _v in (("TW", SK_TMW), ("TH", SK_TMH), ("TMAXN", SK_TMAXN), ("TBMAX", SK_TBMAX), ("TSMIN", SK_TSMIN), ("TSMAX", SK_TSMAX)):   # 0.3.61
    F(sdat, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("TNODE", SK_TNODE), ("TICON", SK_TICON), ("THIT", SK_THIT), ("THALO", SK_THALO), ("TBR", SK_TBR)):   # 0.3.61
    F(sdat, "public static final String %s = %s;" % (_n, jstr(_v)))
F(sdat, "public static final String[] TDID = %s;" % jarr([r_[0] for r_ in SK_TD_ROWS]))   # 0.3.61: the node panel's labels
F(sdat, "public static final int[] TDCLIP = %s;" % jints([SK_TD_CLIP[r_[0]] for r_ in SK_TD_ROWS]))''')
P.rep('''           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;"):
    F(skpg, _f)''', '''           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;",
           "public int tsel;", "public String ttok;", "public int[] tcodes;", "public int[] tranks;", "public int tacts;", "public boolean tinline;"):   # 0.3.61: the inline tree
    F(skpg, _f)''')
P.rep('''  this.builds = 0;
  this.answers = 0;
}""")
# 0.3.58: THE PETS SCREEN DATA''', '''  this.builds = 0;
  this.answers = 0;
  this.tsel = -1;
  this.ttok = null;
  this.tcodes = null;
  this.tranks = null;
  this.tacts = 0;
  this.tinline = false;
}""")
# 0.3.58: THE PETS SCREEN DATA''')

# ---------- the Java: fillMap (after fillTree), the build, the clicks
P.rep('''M(skpg, r"""
public void fillShard(@UCB@ b) {''', '''# 0.3.61: THE INLINE TREE. tree:fn:map (SkyyTrees 0.6.10) = "ok|<token>|<tv>|<name>|<colour>|<level>|<points>|<spent>|<points line>|<respec
# line>|<W>|<H>|<node size>|<armed>|<any spent>|<busy>|<bad>" then b|<i>|<name>|<l>|<t>|<w>|<spent>, n|<k>|<code>|<l>|<t>|<state picture>|<icon or ->|
# <name>|<rank r / m or ->, d|<k>|<code>|<caption>|<name>|<rank>|<state>|<now>|<next>|<cost>|<needs>|<how>|<state#>|<can>; or "none|<why>".
# Everything is checked BEFORE anything is drawn (false = the 0.3.60 view); a click node = ONE packet (rebuild).
M(skpg, r"""
public static boolean okName(String s, int max, boolean us) {
  if (s == null || s.length() < 1 || s.length() > max) return false;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    boolean ok = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || (us && c == '_');
    if (!ok) return false;
  }
  return true;
}""")
M(skpg, r"""
public static int tni(String s) { return @PKG@.InvPage.toInt(s == null ? "" : s.trim(), -99999); }""")
M(skpg, r"""
public static void mapShell(@UCB@ b, boolean on) {
  b.set("#SkyySkpTrV0.Visible", !on);
  b.set("#SkyySkpTrV1.Visible", on);
  b.set("#SkyySkpTrL.Visible", on);
  b.set("#SkyySkpTrR.Visible", on);
  b.set("#SkyySkpTrO.Text", on ? "Full tree" : "Open tree");
}""")
M(skpg, r"""
public static void tdetail(@UCB@ b, String[] t) {
  for (int i = 0; i < @PKG@.SkillData.TDID.length; i++) {
    String x = t != null && i < t.length && t[i] != null ? t[i] : "";
    b.set("#SkyySkp" + @PKG@.SkillData.TDID[i] + ".Text", @PKG@.MenuUtil.clip(x, @PKG@.SkillData.TDCLIP[i]));
  }
}""")
# PERKS NOW for the node panel (nothing selected): the Stats rows' notes of this skill, as the 0.3.60 list (names + values)
M(skpg, r"""
public String perksLine() {
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList rs = this.srows;
  for (int i = 0; rs != null && i < rs.size(); i++) {
    Object x = rs.get(i);
    if (!(x instanceof String[])) continue;
    String[] r = (String[]) x;
    if (r.length != 3 || r[2] == null || r[2].length() == 0) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(r[0]).append(' ').append(r[1]);
  }
  return sb.length() == 0 ? "PERKS NOW  none yet - learn nodes to add them" : "PERKS NOW  " + sb.toString();
}""")
M(skpg, r"""
public boolean fillMap(@UCB@ b, @UEB@ ev) {
  this.ttok = null;
  this.tcodes = null;
  this.tranks = null;
  this.tinline = false;
  if (@PKG@.InvCraft.fn("tree:fn:map") == null || @PKG@.InvCraft.fn("tree:fn:act") == null) return false;
  java.util.UUID u = this.playerRef.getUuid();
  int si = idx(this.skill);
  String tn = si >= 0 ? @PKG@.SkillData.TREE[si] : this.skill;
  Object o = call("tree:fn:map", new Object[] { u, tn, Integer.valueOf(this.tsel) });
  if (!(o instanceof String) || ((String) o).length() == 0) return false;
  String[] ls = ((String) o).split("\\n");
  if (ls[0].startsWith("none|")) {
    mapShell(b, true);
    b.set("#SkyySkpTrL.Visible", false);
    b.set("#SkyySkpTrR.Visible", false);
    b.set("#SkyySkpTmM.Text", @PKG@.MenuUtil.clip(ls[0].substring(5), 90));
    b.set("#SkyySkpTrP.Text", "No tree to show here");
    String ab = "Combat".equals(this.skill) ? abilLine(u) : "";
    tdetail(b, new String[] { "NO TREE", "", "Full tree opens every skill tree you have.", perksLine(), "", "", ab });
    this.tsel = -1;
    this.tinline = true;
    return true;
  }
  String[] h = ls[0].split("\\\\|", -1);
  int W = @PKG@.SkillData.TW;
  int H = @PKG@.SkillData.TH;
  if (h.length < 17 || !"ok".equals(h[0]) || tni(h[10]) != W || tni(h[11]) != H) return false;
  int s = tni(h[12]);
  if (s < @PKG@.SkillData.TSMIN || s > @PKG@.SkillData.TSMAX) return false;
  java.util.ArrayList bs = new java.util.ArrayList();
  java.util.ArrayList ns = new java.util.ArrayList();
  String[] dl = null;
  for (int i = 1; i < ls.length; i++) {
    String[] f = ls[i].split("\\\\|", -1);
    if (f[0].equals("b")) { if (f.length < 7) return false; bs.add(f); }
    else if (f[0].equals("n")) { if (f.length < 9) return false; ns.add(f); }
    else if (f[0].equals("d")) { if (f.length < 14) return false; dl = f; }
  }
  int n = ns.size();
  if (n < 1 || n > @PKG@.SkillData.TMAXN || bs.size() > @PKG@.SkillData.TBMAX) return false;
  int[] cs = new int[n];
  int[] lx = new int[n];
  int[] ty = new int[n];
  int[] rk = new int[n];
  for (int k = 0; k < n; k++) {
    String[] f = (String[]) ns.get(k);
    int l = tni(f[3]);
    int t = tni(f[4]);
    cs[k] = tni(f[2]);
    if (tni(f[1]) != k || cs[k] == -99999 || l < 0 || t < 0 || l + s > W || t + s > H) return false;
    if (!okName(f[5], 48, false) || !("-".equals(f[6]) || okName(f[6], 100, true))) return false;
    lx[k] = l;
    ty[k] = t;
    int sl = f[8].indexOf(" /");
    rk[k] = sl > 0 ? tni(f[8].substring(0, sl)) : -1;
  }
  for (int i = 0; i < bs.size(); i++) {
    String[] f = (String[]) bs.get(i);
    int l = tni(f[3]);
    int t = tni(f[4]);
    int w = tni(f[5]);
    if (tni(f[1]) != i || l < 0 || t < 0 || w < 1 || l + w > W || t + 16 > H) return false;
  }
  // every check passed: draw the whole map
  this.ttok = h[1];
  this.tcodes = cs;
  this.tranks = rk;
  this.tinline = true;
  if (this.tsel >= n) this.tsel = -1;
  int sel = this.tsel;
  mapShell(b, true);
  b.set("#SkyySkpTmM.Text", "");
  b.set("#SkyySkpTrP.Text", @PKG@.MenuUtil.clip(h[8], 52));
  b.set("#SkyySkpTrR.Text", "1".equals(h[13]) ? "Confirm" : "Respec");
  b.set("#SkyySkpTrL.Text", sel >= 0 && cs[sel] >= 0 && rk[sel] >= 1 ? "Rank up" : "Learn");
  for (int i = 0; i < bs.size(); i++) {
    String[] f = (String[]) bs.get(i);
    int sp = tni(f[6]);
    b.appendInline("#SkyySkpTm", @PKG@.SkillData.TBR.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(tni(f[5])))
        .replace("{L}", String.valueOf(tni(f[3]))).replace("{T}", String.valueOf(tni(f[4]))));
    b.set("#SkyySkpTb" + i + ".Text", @PKG@.MenuUtil.clip(f[2].toUpperCase() + (sp > 0 ? "  " + sp : ""), 30));
  }
  if (sel >= 0) {   // the /tree map's cyan halo under the selected node (inside the canvas)
    int hz = (s * 44 + 16) / 32;
    int hl = lx[sel] + (s - hz) / 2;
    int ht = ty[sel] + (s - hz) / 2;
    if (hl < 0) hl = 0;
    if (ht < 0) ht = 0;
    if (hl + hz > W) hl = W - hz;
    if (ht + hz > H) ht = H - hz;
    b.appendInline("#SkyySkpTm", @PKG@.SkillData.THALO.replace("{Z}", String.valueOf(hz)).replace("{L}", String.valueOf(hl)).replace("{T}", String.valueOf(ht)));
  }
  int isz = (s * 18 + 16) / 32;
  int hsz = (s * 26 + 16) / 32;
  for (int k = 0; k < n; k++) {
    String[] f = (String[]) ns.get(k);
    String ks = String.valueOf(k);
    b.appendInline("#SkyySkpTm", @PKG@.SkillData.TNODE.replace("{I}", ks).replace("{L}", String.valueOf(lx[k])).replace("{T}", String.valueOf(ty[k]))
        .replace("{S}", String.valueOf(s)).replace("{N}", f[5]));
    if (!"-".equals(f[6]) && @PKG@.InvPage.known(f[6])) {
      b.appendInline("#SkyySkpTm", @PKG@.SkillData.TICON.replace("{I}", ks).replace("{Z}", String.valueOf(isz)).replace("{L}", String.valueOf(lx[k] + (s - isz) / 2))
          .replace("{T}", String.valueOf(ty[k] + (s - isz) / 2)).replace("{D}", f[6]));
    }
    b.appendInline("#SkyySkpTm", @PKG@.SkillData.THIT.replace("{I}", ks).replace("{Z}", String.valueOf(hsz)).replace("{L}", String.valueOf(lx[k] + (s - hsz) / 2))
        .replace("{T}", String.valueOf(ty[k] + (s - hsz) / 2)));
    ev.addEventBinding(@BT@.Activating, "#SkyySkpTn" + ks + "B", @EVD@.of("a", "tn:" + ks));
  }
  String lv = tni(h[5]) >= 0 ? "  Lv " + tni(h[5]) : "";
  if (sel >= 0 && dl != null && tni(dl[1]) == sel) {
    tdetail(b, new String[] { dl[4], dl[5], dl[6], dl[7], dl[8], dl[9], dl[10] });
  } else {
    String ab = "Combat".equals(this.skill) ? abilLine(u) : "";
    tdetail(b, new String[] { "PICK A NODE", h[3].toUpperCase() + " TREE" + lv, "Click a node on the map to see it - then Learn or Rank up here.", perksLine(), h[9], "", ab });
  }
  return true;
}""")
M(skpg, r"""
public void fillShard(@UCB@ b) {''')
P.rep('''  try { fillTree(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the tree failed: " + t); }
  try { fillShard(b); }''', '''  try { fillTree(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: the tree failed: " + t); }
  boolean inl = false;   // 0.3.61: the inline tree (SkyyTrees 0.6.10); else the 0.3.60 view with Open tree
  try { inl = fillMap(b, ev); } catch (Throwable t) { inl = false; @PKG@.MenuUtil.warn("skill page: the inline tree failed: " + t); }
  if (!inl) {
    this.ttok = null;
    this.tcodes = null;
    this.tranks = null;
    this.tinline = false;
    mapShell(b, false);
  }
  try { fillShard(b); }''')
P.rep('''M(skpg, r"""
public void pickSkill(int i) {
  if (i < 0 || i >= @PKG@.SkillData.ORDER.length) { say("No such skill"); return; }
  this.skill = @PKG@.SkillData.ORDER[i];
  this.sel = -1;''', '''# 0.3.61: a node click = that node selected (its panel), ONE packet
M(skpg, r"""
public void pickNode(int k) {
  if (!this.tinline || this.tcodes == null || k < 0 || k >= this.tcodes.length) { say("Nothing there"); return; }
  this.tsel = k;
  this.tcap = "";
  redraw();
}""")
# 0.3.61: Learn / Rank up / Respec = ONE tree:fn:act call with the token of the drawn map; the answer = the caption + ONE packet (rebuild);
# a double click inside SkyyTrees' 350 ms guard ("=One moment.") = the caption only
M(skpg, r"""
public void treeAct(String op) {
  if (!this.tinline || this.ttok == null || @PKG@.InvCraft.fn("tree:fn:act") == null) { say("The skill tree is not on this server right now"); return; }
  int si = idx(this.skill);
  String tn = si >= 0 ? @PKG@.SkillData.TREE[si] : this.skill;
  String arg = tn;
  if ("learn".equals(op)) {
    if (this.tcodes == null || this.tsel < 0 || this.tsel >= this.tcodes.length) { say("Click a node on the map first"); return; }
    arg = tn + "|" + this.tsel + "|" + this.tcodes[this.tsel];
  }
  this.tacts = this.tacts + 1;
  Object r = call("tree:fn:act", new Object[] { this.playerRef.getUuid(), this.ttok, op, arg });
  if (!(r instanceof String) || ((String) r).length() < 2) { say("The skill tree could not answer right now - nothing changed. Try again."); return; }
  String m = (String) r;
  String msg = @PKG@.MenuUtil.clip(m.substring(1), 170);
  if (m.charAt(0) == '=' && msg.startsWith("One moment")) { say(msg); return; }
  if (msg.startsWith("Your profile changed") || msg.startsWith("That tree changed")) this.tsel = -1;
  this.tcap = msg;
  redraw();
}""")
M(skpg, r"""
public void pickSkill(int i) {
  if (i < 0 || i >= @PKG@.SkillData.ORDER.length) { say("No such skill"); return; }
  this.skill = @PKG@.SkillData.ORDER[i];
  this.sel = -1;
  this.tsel = -1;   // 0.3.61''')
P.rep('''    if (a.equals("tr")) { openTree(); return; }
    if (a.equals("sh")) { shard(); return; }
    say("Pick a skill on the right");''', '''    if (a.equals("tr")) { openTree(); return; }
    if (a.equals("sh")) { shard(); return; }
    if (a.startsWith("tn:")) { pickNode(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }   // 0.3.61: the inline tree
    if (a.equals("tl")) { treeAct("learn"); return; }
    if (a.equals("trs")) { treeAct("respec"); return; }
    say("Pick a skill on the right");''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.61: no new system / command"
P.finish()
print("wrote", P.dst)

# ======================================================================= the HARNESS (derived from the 0.3.60 harness: every 0.3.60 check
# runs again on the 0.3.61 jar - without tree:fn:map = the 0.3.60 panel, unchanged - plus TREEMAP1 on a Python stand-in of SkyyTrees 0.6.10)
# ======================================================================= the HARNESS
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.60 (the menu fix round of Skyy's 11-21 test; tools/menu_0_3_60_patch.py).
GENERATED by tools/menu_0_3_60_patch.py from the 0.3.59 harness (edit the patch, not this file): every 0.3.59 check runs again on the
0.3.60 jar''', '''"""Harness for SkyyMenu 0.3.61 (the skill tree inline on every skill page; tools/menu_0_3_61_patch.py, round treemap1).
GENERATED by tools/menu_0_3_61_patch.py from the 0.3.60 harness (edit the patch, not this file): every 0.3.60 check runs again on the
0.3.61 jar (without tree:fn:map every TAB1 check = the 0.3.60 panel with Open tree, unchanged), plus
  TREEMAP1 (EXECUTED on a Python stand-in of SkyyTrees 0.6.10 tree:fn:map / tree:fn:act - the real SkyyTrees side, and this page drawing it
       end to end, run in SkyyTrees/test_skyytrees_0.6.10.py phases line + inline):
       FALL    no keys = the 0.3.60 view (PERKS NOW, Open tree; Learn / Respec hidden); Learn / Respec / a node click there = said, no call
       DRAW    the Mining page asks tree:fn:map (uuid, "Mining", -1) and draws: every node = its state picture SkyyTrees/Map/Node/<state>.png
               at its place + an icon only for an item the server knows + a click square bound tn:<k>; the branch titles; the points line;
               Learn / Respec / Full tree; nothing selected = PICK A NODE
       PICK    a node click = ONE packet: asked with that node, the halo, the node panel (name, rank, state, now, next, cost, needs), Rank up
       ACT     Learn = ONE tree:fn:act (the drawn token, "learn", "<tree>|<k>|<code>"), the answer as the caption, ONE packet; "=One moment." =
               the caption only (no rebuild); "That tree changed" / "Your profile changed" clear the selection; null = said; Respec = ONE
               act ("respec", "<tree>"); Combat asks "Class"; none = the sentence in the map box, no Learn
       CHECK   an answer that fails a check (canvas size, a node outside / out of order / a bad picture name / 121 nodes / a null / a throw) =
               the 0.3.60 view, nothing of the map drawn
       BUDGET  the page with the biggest tree SkyyMenu draws (120 nodes) under the ~1,600 element budget; no Top / Bottom alignment
The 0.3.60 harness text follows:
Harness for SkyyMenu 0.3.60 (the menu fix round of Skyy's 11-21 test; tools/menu_0_3_60_patch.py).
GENERATED by tools/menu_0_3_60_patch.py from the 0.3.59 harness (edit the patch, not this file): every 0.3.59 check runs again on the
0.3.60 jar''')
T.rep('VERSION = "0.3.60"\nJAR', 'VERSION = "0.3.61"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.59.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.60.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.59.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.60.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_60_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_61_patch.py")')
T.rep('"scratch", "menufix1", "menu"', '"scratch", "treemap1", "menu"')
T.rep('ADDED = []   # 0.3.60: no new class\n', 'ADDED = []   # 0.3.61: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.60:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.61: the inline tree on the skill page
    "SkillPage": ["+f tacts", "+f tcodes", "+f tinline", "+f tranks", "+f tsel", "+f ttok", "+m fillMap", "+m mapShell", "+m okName", "+m perksLine",
                  "+m pickNode", "+m tdetail", "+m tni", "+m treeAct", "~c ", "~m build", "~m handleDataEvent", "~m pickSkill"],
    "SkillData": ["+f TBMAX", "+f TBR", "+f TDCLIP", "+f TDID", "+f TH", "+f THALO", "+f THIT", "+f TICON", "+f TMAXN", "+f TNODE", "+f TSMAX", "+f TSMIN", "+f TW",
                  "~<clinit>"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''        want = sorted(["manifest.json"] + [k_ for k_ in SUI.glass_texture_files() if k_ not in _zn])''',
      '''        _zo = set(zipfile.ZipFile(OLD_JAR).namelist())   # 0.3.61: only the ones the OLD jar still had (0.3.60 already left them out)
        want = sorted(["manifest.json"] + [k_ for k_ in SUI.glass_texture_files() if k_ not in _zn and k_ in _zo])''')
T.rep('''    K.check(g.count('VERSION = "0.3.60"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.61"') == 1, "S VERSION")
    # 0.3.61: the inline tree - the tree panel / node panel fit, the run-time markups proven
    K.check("0.3.61: the tree panel fits" in g and "0.3.61: the node panel fits" in g and "0.3.61: the tree markups are proven" in g,
            "TREEMAP1 STATIC the build asserts the tree panel + node panel fit and the tree markups are proven")''')
T.rep('''    K.check(ms_ is not None and int(ms_.group(1)) <= 800, "TAB1 STATIC the skill page's element budget assert is <= 800 (the ~1,600 client budget)")''',
      '''    K.check(ms_ is not None and int(ms_.group(1)) <= 1200, "TAB1 STATIC the skill page's element budget assert is <= 1200 (0.3.61: + the inline tree, at most 120 nodes; the ~1,600 client budget)")''')
T.rep('''    K.eq(diff, sorted(["manifest.json"] + [k for k in glass if k not in shipped]), "S non-class jar entries changed = manifest + the Skyglass pictures no page uses (left out)")''',
      '''    K.eq(diff, ["manifest.json"], "S non-class jar entries changed = manifest only (0.3.61: no picture of its own - the tree pictures are SkyyTrees')")
    K.check(not [n_ for n_ in zn.namelist() if "SkyyTrees/" in n_], "TREEMAP1 STATIC this jar ships no SkyyTrees picture (ui_budget unchanged)")''')
HARNESS_TM = r'''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
    SKPt = JV("SkillPage")
    ukt = str(PK.pr.getUuid())
    for k_ in ("tree:fn:map", "tree:fn:act"):
        BR.remove(k_)
    BR.put("tree:" + ukt, "Mining:2/30,Class:0/23")
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    E.pump(PK)
    SPT = SKPt.open(PK.ref, PK.st, PK.pr, "Mining", "test")
    E.pump(PK)
    vis_ = lambda c_, k_: sval(c_, "#SkyySkp%s.Visible" % k_) in (True, "true")
    hid_ = lambda c_, k_: sval(c_, "#SkyySkp%s.Visible" % k_) in (False, "false")

    def tm_ev(obj, what):
        E.pump(PK)
        f_ = len(E.sent(PK))
        PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, json.dumps(obj))
        ps_ = pages(PK, f_)
        K.eq(len(ps_), 1, what + ": exactly ONE page packet")
        E.pump(PK)
        return ps_[0] if ps_ else None

    def mkt(p_):
        return "\n".join(str(c_.text) for c_ in cmds_of(p_) if c_.text is not None) if p_ is not None else ""

    def elt(p_):
        return len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", re.sub(r'"(?:[^"\\]|\\.)*"', '""', mkt(p_))))
    p_ = tm_ev({"a": "sk:1"}, "TREEMAP1 FALL Mining without SkyyTrees 0.6.10")
    cm = cmap(p_) if p_ else {}
    K.check(vis_(cm, "TrV0") and hid_(cm, "TrV1") and hid_(cm, "TrL") and hid_(cm, "TrR") and sval(cm, "#SkyySkpTrO.Text") == "Open tree"
            and sval(cm, "#SkyySkpTrP.Text") == "Points  28 free   2 spent of 30" and "#SkyySkpTn0" not in mkt(p_),
            "TREEMAP1 FALL no tree:fn:map = the 0.3.60 view: PERKS NOW, Open tree, the tree:<uuid> points; Learn / Respec hidden; no map")
    for a_, want_ in (("tl", "The skill tree is not on this server right now"), ("trs", "The skill tree is not on this server right now"), ("tn:0", "Nothing there")):
        p_ = tm_ev({"a": a_}, "TREEMAP1 FALL " + a_)
        K.eq(sval(cmap(p_), "#SkyySkpCap.Text"), want_, "TREEMAP1 FALL %s without the inline tree = said" % a_)
    # the stand-in of SkyyTrees 0.6.10 (its real answers: SkyyTrees/test_skyytrees_0.6.10.py)
    TMW = {"calls": [], "acts": [], "tok": "tokA", "ans": "+Done: Vein Sense rank 2/3 - 27 points left.", "n": 5, "mode": "ok", "s": 32, "armed": False}

    def tm_map(o):
        sk_, sel_ = str(o[1]), int(o[2])
        TMW["calls"].append((str(o[0]), sk_, sel_))
        m_ = TMW["mode"]
        if m_ == "null":
            return None
        if m_ == "throw":
            raise RuntimeError("stand-in throws")
        if sk_ in ("Ranching", "Orchard"):
            return "none|No %s skill tree on this server" % sk_
        s_ = TMW["s"]
        hd_ = ["ok", TMW["tok"], "20", sk_ if sk_ != "Class" else "Warrior", "#8fc8ff", "30", "30", "2", "28 of 30 points free - row 2 opens at 5",
               "Respec: your free respec of this run", "520" if m_ != "badW" else "600", "264", str(s_), "1" if TMW["armed"] else "0", "1", "0", "0"]
        out_ = ["|".join(hd_), "b|0|Veins|6|6|250|2", "b|1|Strikes|264|6|250|0"]
        texs_ = ["Ready", "SkyL13", "Locked", "SkyFree", "CapLocked"]
        for k_ in range(TMW["n"]):
            l_, t_ = 6 + (k_ % 12) * (s_ + 4), 26 + (k_ // 12) * (s_ + 4)
            if m_ == "outside" and k_ == 2:
                l_ = 515
            tex_ = texs_[k_ % 5] if (m_ != "badtex" or k_ != 1) else 'Ready.png"; } Label { Text: "x'
            kk_ = 7 if (m_ == "order" and k_ == 3) else k_
            out_.append("n|%d|%d|%d|%d|%s|%s|Node %d|%s" % (kk_, (100 + k_) if k_ != 3 else -4, l_, t_, tex_, ("Rock_Stone", "Nope_Item", "-", "-", "Wood_Oak_Trunk")[k_ % 5],
                                                         k_, "-" if k_ == 3 else "%d / 3" % (1 if k_ == 1 else 0)))
        if 0 <= sel_ < TMW["n"]:
            out_.append("d|%d|%d|Mining - Veins - Row 1|Node %d|Rank %d / 3|Ready to learn|Now: +2%% Mining Fortune|Next rank: +4%%|Cost: 1 point a rank - 28 of 30 free|Ready to unlock|How it works|1|1"
                        % (sel_, 100 + sel_, sel_, 1 if sel_ == 1 else 0))
        return "\n".join(out_)

    def tm_act(o):
        TMW["acts"].append((str(o[1]), str(o[2]), str(o[3])))
        return TMW["ans"]
    BR.put("tree:fn:map", Fn(tm_map))
    BR.put("tree:fn:act", Fn(tm_act))
    p_ = tm_ev({"a": "sk:1"}, "TREEMAP1 DRAW Mining")
    cm, mk_ = (cmap(p_) if p_ else {}), mkt(p_)
    nd_ = re.findall(r'Group #SkyySkpTn(\d+) \{ Anchor: \(Left: (\d+), Top: (\d+), Width: 32, Height: 32\); Background: "SkyyTrees/Map/Node/([A-Za-z0-9]+)\.png"; \}', mk_)
    K.check(TMW["calls"][-1] == (ukt, "Mining", -1), "TREEMAP1 DRAW asked tree:fn:map (uuid, Mining, -1) (%s)" % TMW["calls"][-1:])
    K.eq([(int(a_), int(b_), int(c_), d_) for a_, b_, c_, d_ in nd_], [(0, 6, 26, "Ready"), (1, 42, 26, "SkyL13"), (2, 78, 26, "Locked"), (3, 114, 26, "SkyFree"), (4, 150, 26, "CapLocked")],
         "TREEMAP1 DRAW every node = its state picture at its place")
    K.check(mk_.count("ItemIcon #SkyySkpTn") == 2 and 'ItemId: "Rock_Stone"' in mk_ and 'ItemId: "Wood_Oak_Trunk"' in mk_ and "Nope_Item" not in mk_,
            "TREEMAP1 DRAW an icon only for an item the server knows (Rock_Stone, Wood_Oak_Trunk; not Nope_Item, not '-')")
    hb_ = [b_ for b_ in binds_of(p_) if b_[1].startswith("#SkyySkpTn")]
    K.check([b_[1] for b_ in hb_] == ["#SkyySkpTn%dB" % k_ for k_ in range(5)] and all(json.loads(b_[2]).get("a") == "tn:%d" % k_ for k_, b_ in enumerate(hb_)),
            "TREEMAP1 DRAW every click square bound tn:<k> (%s)" % hb_[:2])
    K.check(vis_(cm, "TrV1") and hid_(cm, "TrV0") and vis_(cm, "TrL") and vis_(cm, "TrR") and sval(cm, "#SkyySkpTrO.Text") == "Full tree"
            and sval(cm, "#SkyySkpTrP.Text") == "28 of 30 points free - row 2 opens at 5" and sval(cm, "#SkyySkpTrR.Text") == "Respec" and sval(cm, "#SkyySkpTrL.Text") == "Learn"
            and sval(cm, "#SkyySkpTb0.Text") == "VEINS  2" and sval(cm, "#SkyySkpTb1.Text") == "STRIKES" and sval(cm, "#SkyySkpTmM.Text") == "",
            "TREEMAP1 DRAW the inline view: branch titles, SkyyTrees' points line, Learn / Respec / Full tree (%s)" % sval(cm, "#SkyySkpTrP.Text"))
    K.check(sval(cm, "#SkyySkpDn.Text") == "PICK A NODE" and sval(cm, "#SkyySkpDr.Text") == "MINING TREE  Lv 30" and "#SkyySkpTs " not in mk_
            and sval(cm, "#SkyySkpDx.Text") == "Respec: your free respec of this run" and str(sval(cm, "#SkyySkpDw.Text")).startswith("PERKS NOW"),
            "TREEMAP1 DRAW nothing selected = PICK A NODE, the tree + level, PERKS NOW, the respec price; no halo")
    K.check(not re.search(r"(?:Vertical|Horizontal)Alignment: (?:Top|Bottom)\b", mk_), "TREEMAP1 DRAW no Top / Bottom alignment in the packet")
    K.notes.append("TREEMAP1 Mining (5 nodes): %d elements in the packet" % elt(p_))
    # PICK
    p_ = tm_ev({"a": "tn:1"}, "TREEMAP1 PICK node 1")
    cm, mk_ = (cmap(p_) if p_ else {}), mkt(p_)
    K.check(TMW["calls"][-1] == (ukt, "Mining", 1) and "#SkyySkpTs " in mk_ and 'Background: "SkyyTrees/Map/Halo.png"' in mk_
            and sval(cm, "#SkyySkpDn.Text") == "Node 1" and sval(cm, "#SkyySkpDr.Text") == "Rank 1 / 3" and sval(cm, "#SkyySkpDs.Text") == "Ready to learn"
            and sval(cm, "#SkyySkpDw.Text") == "Now: +2% Mining Fortune" and sval(cm, "#SkyySkpDc.Text") == "Cost: 1 point a rank - 28 of 30 free" and sval(cm, "#SkyySkpTrL.Text") == "Rank up",
            "TREEMAP1 PICK a click = asked with node 1, the halo, the node panel, Rank up (the node has a rank) (%s / %s)" % (sval(cm, "#SkyySkpDn.Text"), sval(cm, "#SkyySkpTrL.Text")))
    hz_ = re.search(r"Group #SkyySkpTs \{ Anchor: \(Left: (-?\d+), Top: (-?\d+), Width: (\d+), Height: (\d+)\)", mk_)
    K.check(hz_ is not None and int(hz_.group(3)) == 44 and int(hz_.group(1)) == 36 and int(hz_.group(2)) == 20, "TREEMAP1 PICK the halo = 44 px around the 32 px node (%s)" % (hz_.groups() if hz_ else None,))
    p_ = tm_ev({"a": "tn:99"}, "TREEMAP1 PICK out of range")
    K.eq(sval(cmap(p_), "#SkyySkpCap.Text"), "Nothing there", "TREEMAP1 PICK out of range = said")
    # ACT
    n0_ = len(TMW["acts"])
    p_ = tm_ev({"a": "tl"}, "TREEMAP1 ACT Learn")
    K.check(TMW["acts"][n0_:] == [("tokA", "learn", "Mining|1|101")] and sval(cmap(p_), "#SkyySkpCap.Text") == "Done: Vein Sense rank 2/3 - 27 points left."
            and "#SkyySkpTn0 " in mkt(p_), "TREEMAP1 ACT Learn = ONE act (token, learn, Mining|1|101), the answer = the caption, the page redrawn (%s)" % TMW["acts"][n0_:])
    TMW["ans"] = "=One moment."
    p_ = tm_ev({"a": "tl"}, "TREEMAP1 ACT double click")
    K.check(sval(cmap(p_), "#SkyySkpCap.Text") == "One moment." and "#SkyySkpTn0 " not in mkt(p_) and int(PK.pm.getCustomPage().tsel) == 1,
            "TREEMAP1 ACT '=One moment.' = the caption only (no rebuild), the selection kept")
    TMW["ans"] = "-No free points - 30 of 30 spent (1 point a level)"
    p_ = tm_ev({"a": "tl"}, "TREEMAP1 ACT not enough points")
    K.eq(sval(cmap(p_), "#SkyySkpCap.Text"), "No free points - 30 of 30 spent (1 point a level)", "TREEMAP1 ACT a refusal is the caption")
    TMW["ans"] = "=Your profile changed - here is its tree. Nothing changed."
    p_ = tm_ev({"a": "tl"}, "TREEMAP1 ACT stale token")
    K.check(str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("Your profile changed") and int(PK.pm.getCustomPage().tsel) == -1 and TMW["calls"][-1][2] == -1,
            "TREEMAP1 ACT a stale token = said, the selection cleared (the redraw asks with -1)")
    n0_ = len(TMW["acts"])
    p_ = tm_ev({"a": "tl"}, "TREEMAP1 ACT Learn with nothing selected")
    K.check(sval(cmap(p_), "#SkyySkpCap.Text") == "Click a node on the map first" and len(TMW["acts"]) == n0_, "TREEMAP1 ACT Learn with nothing selected = said, no call")
    tm_ev({"a": "tn:4"}, "TREEMAP1 pick node 4")
    TMW["ans"] = "=That tree changed - here it is again. Nothing changed."
    TMW["tok"] = "tokB"
    tm_ev({"a": "tn:4"}, "TREEMAP1 redraw with the new token")
    tm_ev({"a": "tl"}, "TREEMAP1 ACT tree changed")
    K.check(TMW["acts"][-1] == ("tokB", "learn", "Mining|4|104") and int(PK.pm.getCustomPage().tsel) == -1, "TREEMAP1 ACT the token of the LAST draw is sent; That tree changed clears the selection")
    TMW["ans"] = None
    n0_ = len(TMW["acts"])
    p_ = tm_ev({"a": "trs"}, "TREEMAP1 ACT Respec, no answer")
    K.check(TMW["acts"][n0_:] == [("tokB", "respec", "Mining")] and str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("The skill tree could not answer"),
            "TREEMAP1 ACT Respec = ONE act (respec, Mining); a null answer = said")
    TMW["ans"] = "=Click Respec again within 10 s to reset your whole Mining tree - every point comes back - free (your free respec of this run)"
    TMW["armed"] = True
    p_ = tm_ev({"a": "trs"}, "TREEMAP1 ACT Respec armed")
    K.check(str(sval(cmap(p_), "#SkyySkpCap.Text")).startswith("Click Respec again") and sval(cmap(p_), "#SkyySkpTrR.Text") == "Confirm", "TREEMAP1 ACT armed = said + the button reads Confirm")
    TMW["armed"] = False
    TMW["ans"] = "+Done"
    # Combat asks Class; none
    p_ = tm_ev({"a": "sk:0"}, "TREEMAP1 Combat")
    K.check(TMW["calls"][-1] == (ukt, "Class", -1) and sval(cmap(p_), "#SkyySkpDr.Text") == "WARRIOR TREE  Lv 30" and str(sval(cmap(p_), "#SkyySkpDe.Text")).startswith("ABILITIES"),
            "TREEMAP1 Combat asks the class tree (Class); the panel's last line = the ABILITIES line (%s)" % sval(cmap(p_), "#SkyySkpDe.Text"))
    p_ = tm_ev({"a": "sk:10"}, "TREEMAP1 Ranching")
    cm = cmap(p_) if p_ else {}
    K.check(sval(cm, "#SkyySkpTmM.Text") == "No Ranching skill tree on this server" and vis_(cm, "TrV1") and hid_(cm, "TrL") and hid_(cm, "TrR") and "#SkyySkpTn0" not in mkt(p_),
            "TREEMAP1 none = SkyyTrees' sentence in the map box, no Learn / Respec, no node")
    # CHECK: an answer that fails a check = the 0.3.60 view
    for m_, why_ in (("badW", "another canvas size"), ("outside", "a node outside the canvas"), ("badtex", "a picture name with markup"), ("order", "nodes out of order"),
                     ("null", "a null answer"), ("throw", "a throw"), ("many", "121 nodes")):
        TMW["mode"] = "ok" if m_ == "many" else m_
        TMW["n"] = 121 if m_ == "many" else 5
        TMW["s"] = 20 if m_ == "many" else 32
        p_ = tm_ev({"a": "sk:1"}, "TREEMAP1 CHECK " + why_)
        cm = cmap(p_) if p_ else {}
        K.check(vis_(cm, "TrV0") and hid_(cm, "TrV1") and hid_(cm, "TrL") and sval(cm, "#SkyySkpTrO.Text") == "Open tree" and "#SkyySkpTn" not in mkt(p_) and "#SkyySkpTb0" not in mkt(p_),
                "TREEMAP1 CHECK %s = the 0.3.60 view, nothing of the map drawn" % why_)
    TMW["mode"], TMW["n"], TMW["s"] = "ok", 5, 32
    # BUDGET: the biggest tree SkyyMenu draws (120 nodes at 20 px: 12 a row)
    TMW["n"], TMW["s"] = 120, 20
    p_ = tm_ev({"a": "sk:1"}, "TREEMAP1 BUDGET 120 nodes")
    p_2 = tm_ev({"a": "tn:7"}, "TREEMAP1 BUDGET 120 nodes, one picked")
    TMW["n"], TMW["s"] = 5, 32
    nn_ = len(re.findall(r"Group #SkyySkpTn\d+ ", mkt(p_)))
    K.check(nn_ == 120 and elt(p_) < 1600 and elt(p_2) < 1600, "TREEMAP1 BUDGET the page with 120 nodes: %d elements, %d picked (budget ~1,600)" % (elt(p_), elt(p_2)))
    for k_ in ("tree:fn:map", "tree:fn:act"):
        BR.remove(k_)
    BR.remove("tree:" + ukt)
    if PK.pm.getCustomPage() is not None:
        PK.pm.getCustomPage().handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    E.pump(PK)
'''
T.rep('''    # ---- MENUFIX1 (0.3.60; Skyy 11-21: "crafting doesnt work at all."''', HARNESS_TM + '''    # ---- MENUFIX1 (0.3.60; Skyy 11-21: "crafting doesnt work at all."''')
if T.dst:
    T.finish()
    print("wrote", T.dst)
