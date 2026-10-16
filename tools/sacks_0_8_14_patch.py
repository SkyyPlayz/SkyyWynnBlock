"""Derive SkyySacks/build_skyysacks_0.8.14.py from the SET pin 0.8.13 (the GENERATED build_skyysacks_0.8.13.py; edit THIS file, then
regenerate: python tools/sacks_0_8_14_patch.py; never re-run sacks_0_8_13_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.13 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_14_patch.py   then   python SkyySacks/build_skyysacks_0.8.14.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.14.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.14 = EVERY ENCHANTED ITEM HAS ITS VOID HOME + A BIGGER, SCROLLING /craft LIST (round sacks0814, 2026-10-16). Skyy's words (docs/answered/bags.md,
gear.md, ui.md, 2026-10-16):
  1. BUG "deposit didnt put all the enchanted stuff in my pocket." -> 0.8.13 was frozen to the 20 Enchanted rows of 52298ac. The tables are
     LIVE again: SackDefs.enchCat = tools/skyyench.py (102 rows: the 20 + the C1 rows; every row's Void category - Mining / Foraging /
     Farming / Combat / Smithing, all five already Void categories) and RecipeCmp's tier table = tools/tier_tags.py now (the C1 Enchanted
     rows sort at their base's tier, Enchanted crops grouped with their crop). Deposit All / Deposit <category> / the pickup sweep take
     them (all go through SackDefs.homeOf -> enchCat).
  2. "there was no need to add the enchanted essence of life. greater essence already exists and is literally the exact same thing. remove the
     enchanted, and just use the vanilla version." -> tools/skyyench.py retires the Skyy_Ench_LifeEssence row (RETIRED_C1 / RETIRED_TO /
     VANILLA_ENCH); the Life Essence collection's Enchanted item = vanilla Ingredient_Life_Essence_Concentrated, whose Void home is Farming
     (homeOf: every Ingredient_Life_Essence* -> Farming, unchanged). A held Skyy_Ench_LifeEssence has no Void home any more (it stays in the
     inventory; none can be in the Void - 0.8.13 never homed it); SkyyCollections converts held ones 1:1 in its next round.
  3. /craft (Skyy, screenshot: 9 small rows a page, Page 1/4, empty space below) "there is a lot of empty space at the bottom. scale up the
     actual items you craft, especially the names and the cost. then reduce the items show on page to 6 and allow scroll instead of pages."
     -> ONE scrolling list (skyyui.scroll_list: TopScrolling + the vanilla scrollbar on the list well, as SkyyCollections / SkyyClasses /
     SkyyAccessories 0.5.21) that fills the page below the tabs / search / note, rows 92 high (+6): an 80 px slot (72 px icon), the name
     22 px bold, the tier tag 17 px, the cost chips a 36 px icon + 17 px bold have / need; about 6 rows show at once (6.6 with one tab row
     and the search row). No Prev / Next on the recipe views (the ADD FUEL picker keeps its pages); Search, the tabs, Craftable only,
     Craft / x10 / All unchanged (same events: craft:<i>:<n> / pq:<i>:<n>, i = the row's place in the whole list). The Furnace / Tannery
     queue tabs scroll the same way. At most 150 rows are drawn (a closing line says how many more - search or Craftable only narrows it).
     Skyy (same day) "i dont mind scrolling, but if there are only a few items try to scale them to all fit." -> three row sizes picked
     per build by the row count (CraftPage.rowSize): 92 high (normal, the list scrolls), 128, or 168 (~1.8x: bigger icon, name, cost) when
     every row fits the list at that size - e.g. 1-3 rows = 168, 4 = 128 with one tab row + the search row.
  4. Accessories are crafted only in the Accessory Bag (SkyyAccessories 0.5.21) -> /craft never lists an accessory recipe: the Artifacts tab
     is gone and every /craft list (Crafting, Gear, Farming, Collections, the bench tabs, search) skips artifact() recipes (Skyy_Talisman_*,
     Skyy_Acc*, acc:defs ids). sacks:fn:craftPay and the bench link are unchanged (other mods' calls).
  5. Skyy (screenshot: Farming 'Needs Farming Lv 10 (you: 3)' with every material met) "remove the level cap on upgrading the pocket
     dimensions. if i have the stuff, my lvl shouldn't stop me on this" -> VoidStore.upgrade no longer checks the level gate; the Upgrade
     box shows "Pay the items below to upgrade" instead of the 'Needs <cat> Lv' line and is ready when the items are there. Costs, space
     and the pd.gate.* config lines unchanged (their Server Setup rows say "not used").
  6. tools/skyywbtab.py TAB_TEXT "Accessories & Bags" -> "Bags"; SkyySacks no longer writes the tab's two lang lines (SkyyAccessories, the
     owner, does - "Bags" from its next build; until then the tab still reads "Accessories & Bags").
  7. (critic fix) a row's Craft / x10 / All / Queue events carry the recipe id (craft:<i>:<n>:<recipeId>); the click is resolved by id against
     the list shown now (CraftPage.rowOf) - a stale click whose recipe is gone says "That row changed - nothing was crafted".
No saved-data change, no new setting / command / system / bridge key.
ROLLBACK to 0.8.13: safe (the C1 Enchanted stacks already in the Void stay stored and listed by id; 0.8.13 just stops taking new ones).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.13.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.14.py"))
assert P.has('VERSION = "0.8.13"\n') and P.has("SACKS_HOME_JAVA = ") and P.has('"A:art", "Artifacts"'), "not the live generated SkyySacks 0.8.13"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.14 = EVERY ENCHANTED ITEM"):].rstrip() + "\n"


def between(a, b, inclusive_b=False):
    """the unique text from anchor a up to (not including) the first b after it"""
    assert P.s.count(a) == 1, "anchor count %d: %s" % (P.s.count(a), a[:120])
    i = P.s.index(a)
    j = P.s.index(b, i)
    return P.s[i:j + (len(b) if inclusive_b else 0)]


# ================================================================================================ header, version
P.rep('''ROLLBACK to 0.8.12: safe (roll SkyyCollections back to 0.2.21 with it: two /recipes owners otherwise).
"""
''', '''ROLLBACK to 0.8.12: safe (roll SkyyCollections back to 0.2.21 with it: two /recipes owners otherwise).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.13"\n', 'VERSION = "0.8.14"\n')

# ================================================================================================ 1 + 2: the LIVE tables again
P.rep('''    if f == "enchanted":
        _b = dict(TT.ENCH_BASE).get(i[len("Skyy_Ench_"):])
''', '''    if f == "enchanted":   # 0.8.14: + the C1 rows (tier_tags.ENCH_C1: Enchanted Corn / Lettuce / ... group with their crop)
        _b = dict(tuple(TT.ENCH_BASE) + tuple(TT.ENCH_C1)).get(i[len("Skyy_Ench_"):])
''')
P.rep(between("# 0.8.13: FROZEN to the table 0.8.12 was built with (tools/tier_tags.py at 52298ac", "assert all(1 <= _t <= len(TT.LADDER)"),
      '''# 0.8.14: LIVE again (0.8.13 froze it to 52298ac): tools/tier_tags.py now - the C1 Enchanted rows sort at their base's tier
TT_IDS = sorted(TT.ROWS)
TT_TIERS = [TT.tier(_i) for _i in TT_IDS]
TT_GRPS = [_tt_grp(_i) for _i in TT_IDS]
assert _tt_grp("Skyy_Ench_Corn") == ("Corn", 1) and "Skyy_Ench_LifeEssence" not in TT_IDS, "0.8.14: the C1 rows are in the tier table"
''')
P.rep(between("# 0.8.13: FROZEN to tools/skyyench.py at 52298ac (the 20 rows 0.8.12 homes", "defs.addMethod(CtNewMethod.make(SACKS_HOME_JAVA, defs))\n",
              inclusive_b=True),
      '''# 0.8.14 (Skyy "deposit didnt put all the enchanted stuff in my pocket."): LIVE again - every tools/skyyench.py row (102: the 20 + the C1
# rows; the retired Skyy_Ench_LifeEssence has none - its collection uses the vanilla Greater Essence of Life, homeOf -> Farming)
assert len(EN.IDS) == 102 and "Skyy_Ench_LifeEssence" not in EN.IDS and set(t[5] for t in EN.TABLE) <= set(PD_CATS), "0.8.14: skyyench rows"
assert EN.VANILLA_ENCH["LifeEssence"] == ("Ingredient_Life_Essence_Concentrated", "Farming")
defs.addMethod(CtNewMethod.make(EN.sacks_home_java(), defs))
''')

# ================================================================================================ 3: the bigger rows + ONE scrolling list
P.rep('''CP_BODY_H = {  # the tallest body of each view - every one fits CSH.inner_h (two crafter tab rows, the search + campfire lines)
    "craft": 2 * 42 + 40 + 22 + 24 + 9 * 62 + 26 + 40,
    "proc": 2 * 42 + 22 + 26 + 22 + 18 + 22 + 42 + 42 + 7 * 62 + 26 + 40,
''', '''CP_BODY_H = {  # the tallest body of each view - every one fits CSH.inner_h (two crafter tab rows, the search + campfire lines)
    # 0.8.14: the recipe views = the fixed lines + ONE scrolling list (CraftPage.listOpen: the rest of the body); at least 4 rows of 98 show
    "craft": 2 * 42 + 40 + 22 + 24 + 4 * 98 + 26 + 40,
    "proc": 2 * 42 + 22 + 26 + 22 + 18 + 22 + 46 + 42 + 4 * 98 + 26 + 40,
''')
P.rep('''for _n, _v in CP_CONST.items():
    assert '\\\\' not in _v and "\\n" not in _v, _n
''', '''# 0.8.14 (Skyy "scale up the actual items you craft, especially the names and the cost ... allow scroll instead of pages"): the bigger row
# texts + the list (skyyui.scroll_list on the list well; its height is filled in at runtime: LIST_A + h + LIST_B)
_CP_LIST = SUI.scroll_list("SkyyCList", h=4321, well=True)
assert _CP_LIST.count("Height: 4321") == 1 and "TopScrolling" in _CP_LIST
SUI.check_markup(_CP_LIST)
CP_CONST.update({
    "L_NAMEB": _lst(22, "white", True), "L_NAMEDIMB": _lst(22, "disabled", True), "L_TIERB": _lst(17, "gold", True),
    "L_HAVEB": _lst(17, "have", True), "L_OUTB": _lst(17, "outOfStock", True), "L_CAPB": _lst(16, "caption"),
    # Skyy 10-16 "i dont mind scrolling, but if there are only a few items try to scale them to all fit." -> two larger row sizes
    "L_NAME2": _lst(28, "white", True), "L_NAMEDIM2": _lst(28, "disabled", True), "L_TIER2": _lst(20, "gold", True),
    "L_HAVE2": _lst(19, "have", True), "L_OUT2": _lst(19, "outOfStock", True), "L_CAP2": _lst(18, "caption"),
    "L_NAME3": _lst(32, "white", True), "L_NAMEDIM3": _lst(32, "disabled", True), "L_TIER3": _lst(22, "gold", True),
    "L_HAVE3": _lst(21, "have", True), "L_OUT3": _lst(21, "outOfStock", True), "L_CAP3": _lst(20, "caption"),
    "LIST_A": _CP_LIST.split("4321")[0], "LIST_B": _CP_LIST.split("4321")[1]})
CP_ROW_H, CP_ROWS_MAX = 92, 150            # a row 92 high + 6 below; at most 150 rows drawn (packet size)
CP_FIXED = {"tabs": 42, "search": 40, "note": 22, "camp": 24, "foot": 26 + 40,
            "proc": 26 + 22 + 18 + 22 + 46, "fuel": 42}
assert CSH.inner_h - (CP_FIXED["tabs"] + CP_FIXED["search"] + CP_FIXED["note"] + CP_FIXED["foot"]) >= 6 * (CP_ROW_H + 6), "6 rows with one tab row"
for _n, _v in CP_CONST.items():
    assert '\\\\' not in _v and "\\n" not in _v, _n
''')
P.rep('''cpg.addMethod(CtNewMethod.make(jt(r"""
public static String gap(int w) {
  return "Group { Anchor: (Width: " + w + "); }";
}"""), cpg))
''', '''cpg.addMethod(CtNewMethod.make(jt(r"""
public static String gap(int w) {
  return "Group { Anchor: (Width: " + w + "); }";
}"""), cpg))
# 0.8.14: the scroll list's height = the body minus what the view put above it (usedH) and the foot; at most CP_ROWS_MAX rows, then a line
cpg.addField(CtField.make("public static final int BODYH = %d;" % CSH.inner_h, cpg))
cpg.addField(CtField.make("public static final int MAXROWS = %d;" % CP_ROWS_MAX, cpg))
cpg.addField(CtField.make("public int usedH;", cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static int listH(int used) {
  int h = BODYH - used - 4;
  return h < 200 ? 200 : h;
}"""), cpg))
# Skyy 10-16 "i dont mind scrolling, but if there are only a few items try to scale them to all fit.": three row sizes, picked per build by the
# row count - 0 = normal (92 high, ~6 show, the list scrolls), 1 = 128 high, 2 = 168 high (~1.8x) when every row fits at that size
cpg.addField(CtField.make("public static final int[] ROWHS = new int[] { 92, 128, 168 };", cpg))
cpg.addField(CtField.make("public int rowSz;", cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static int rowSize(int n, int used) {
  int avail = listH(used) - 8;
  if (n < 1) n = 1;
  if (n * (ROWHS[2] + 6) <= avail) return 2;
  if (n * (ROWHS[1] + 6) <= avail) return 1;
  return 0;
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public String pick3(String a, String b2, String c) {
  return this.rowSz == 2 ? c : (this.rowSz == 1 ? b2 : a);
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public int pickI(int a, int b2, int c) {
  return this.rowSz == 2 ? c : (this.rowSz == 1 ? b2 : a);
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static void listOpen(@UCB@ b, int used) {
  b.appendInline("#SkyyCraftBody", LIST_A + listH(used) + LIST_B);
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static void listMore(@UCB@ b, int shown, int total) {
  if (total <= shown) return;
  b.appendInline("#SkyyCList", lbl("SkyyCMoreRows", 1100, 40, L_TEXTC));
  b.set("#SkyyCMoreRows.Text", "Showing the first " + shown + " of " + total + " - search or turn on Craftable only to see the rest.");
}"""), cpg))
''')

# drawRow: the bigger row, into the list
P.rep(between('''public void drawRow(@UCB@ b, @UEB@ ev, int i, @CRR@ r, @CIC@ mats, int lim, String note, int allN, boolean timed, String each) {''',
              '''  b.appendInline("#" + rid, gap(8));
  boolean ok = allN > 0;'''),
      '''public void drawRow(@UCB@ b, @UEB@ ev, int i, @CRR@ r, @CIC@ mats, int lim, String note, int allN, boolean timed, String each) {
  // 0.8.14 (Skyy "scale up the actual items you craft, especially the names and the cost"): 92 high (the larger sizes when only a few rows:
  // rowSz, Skyy "if there are only a few items try to scale them to all fit."), into the scroll list #SkyyCList
  int rh = ROWHS[this.rowSz];
  int slot = pickI(80, 112, 148);
  int ico = pickI(72, 104, 140);
  int tw = pickI(680, 650, 610);
  int hh = pickI(34, 40, 46);
  int inh = pickI(40, 48, 56);
  int cic = pickI(36, 44, 52);
  @MQ@ outq = r.getPrimaryOutput();
  String outId = outq == null ? "?" : outq.getItemId();
  String rid = "SkyyCRow" + i;
  b.appendInline("#SkyyCList", "Group #" + rid + " { Anchor: (Height: " + rh + ", Bottom: 6); LayoutMode: Left; Padding: (Horizontal: 10); Background: " + (lim > 0 ? BG_ROW : BG_ROWDIM) + "; }");
  b.appendInline("#" + rid, "Group { Anchor: (Width: " + slot + ", Height: " + slot + ", Top: " + ((rh - slot) / 2) + "); Padding: (Full: 4); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: " + ico + ", Height: " + ico + "); ItemId: \\"" + @PKG@.SacksPage.safe(outId) + "\\"; } }");
  b.appendInline("#" + rid, gap(14));
  b.appendInline("#" + rid, "Group #SkyyCTxt" + i + " { Anchor: (Width: " + tw + ", Height: " + rh + "); LayoutMode: Top; Padding: (Top: " + ((rh - hh - inh - 4) / 2) + "); }");
  b.appendInline("#SkyyCTxt" + i, "Group #SkyyCHd" + i + " { Anchor: (Height: " + hh + "); LayoutMode: Left; }");
  b.appendInline("#SkyyCHd" + i, lbl("SkyyCName" + i, tw - 180, hh, lim > 0 ? pick3(L_NAMEB, L_NAME2, L_NAME3) : pick3(L_NAMEDIMB, L_NAMEDIM2, L_NAMEDIM3)));
  b.set("#SkyyCName" + i + ".Text", pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "") + (note == null ? "" : note));
  String tt = @PKG@.RecipeCmp.tierText(outId);
  if (tt.length() > 0) {
    b.appendInline("#SkyyCHd" + i, lbl("SkyyCTier" + i, 180, hh, pick3(L_TIERB, L_TIER2, L_TIER3)));
    b.set("#SkyyCTier" + i + ".Text", tt);
  }
  b.appendInline("#SkyyCTxt" + i, "Group #SkyyCIn" + i + " { Anchor: (Height: " + inh + ", Top: 4); LayoutMode: Left; }");
  @MQ@[] in = r.getInput();
  int n = 0;
  for (int q = 0; in != null && q < in.length; q++) if (in[q] != null) n++;
  boolean wide = n <= (timed ? 2 : (this.rowSz == 0 ? 3 : 2));
  int max = wide ? n : (timed ? pickI(4, 3, 2) : pickI(5, 4, 3));
  int lw = wide ? (timed ? pickI(200, 200, 190) : (n <= 2 ? pickI(250, 240, 220) : 180)) : pickI(86, 96, 104);
  String sHave = pick3(L_HAVEB, L_HAVE2, L_HAVE3);
  String sOut = pick3(L_OUTB, L_OUT2, L_OUT3);
  String sCap = pick3(L_CAPB, L_CAP2, L_CAP3);
  int shown = 0;
  for (int q = 0; in != null && q < in.length && shown < max; q++) {
    if (in[q] == null) continue;
    int have = mats.countRemovableMaterial(in[q]);
    int need = in[q].getQuantity();
    String iid = in[q].getItemId();
    String nm = iid != null ? pretty(iid) : (in[q].getResourceTypeId() != null ? @PKG@.SackDefs.rtName(in[q].getResourceTypeId()) : "?");
    String cid = "SkyyCC" + i + "x" + q;
    if (iid != null) b.appendInline("#SkyyCIn" + i, "ItemIcon { Anchor: (Width: " + cic + ", Height: " + cic + ", Top: " + ((inh - cic) / 2) + "); ItemId: \\"" + @PKG@.SacksPage.safe(iid) + "\\"; }");
    b.appendInline("#SkyyCIn" + i, lbl(cid, lw + (iid == null ? cic : 0), inh, have >= need ? sHave : sOut));
    b.set("#" + cid + ".Text", " " + ((wide || iid == null) ? nm + " " : "") + @PKG@.SacksPage.shortNum((long) have) + "/" + need);
    b.appendInline("#SkyyCIn" + i, gap(6));
    shown++;
  }
  if (shown < n) {
    b.appendInline("#SkyyCIn" + i, lbl("SkyyCMore" + i, 40, inh, sCap));
    b.set("#SkyyCMore" + i + ".Text", "+" + (n - shown));
  }
  if (timed) {
    b.appendInline("#SkyyCIn" + i, lbl("SkyyCEach" + i, 110, inh, sCap));
    b.set("#SkyyCEach" + i + ".Text", each == null ? "" : each);
  }
''')
P.rep('''  b.appendInline("#" + rid, btn(bid + i, timed ? "Queue" : "Craft", 120, 13, ok ? B_PRI : B_PRIDIS));
  b.appendInline("#" + rid, gap(6));
  b.appendInline("#" + rid, btn(tid + i, "x10", 70, 13, ok ? B_SEC : B_SECDIS));
  b.appendInline("#" + rid, gap(6));
  b.appendInline("#" + rid, btn(aid + i, "All " + allN, 110, 13, ok ? B_SEC : B_SECDIS));
''', '''  b.appendInline("#" + rid, btn(bid + i, timed ? "Queue" : "Craft", 120, (rh - 32) / 2, ok ? B_PRI : B_PRIDIS));
  b.appendInline("#" + rid, gap(6));
  b.appendInline("#" + rid, btn(tid + i, "x10", 70, (rh - 32) / 2, ok ? B_SEC : B_SECDIS));
  b.appendInline("#" + rid, gap(6));
  b.appendInline("#" + rid, btn(aid + i, "All " + allN, 110, (rh - 32) / 2, ok ? B_SEC : B_SECDIS));
''')
# foot: pages <= 0 = a scrolling view (no pager)
P.rep('''  b.appendInline("#SkyyCNav", btn("SkyyCPrev", "< Prev", 120, 0, pageNo > 0 ? B_SEC : B_SECDIS));
  b.appendInline("#SkyyCNav", lbl("SkyyCPage", 200, 32, L_CAPC));
  b.set("#SkyyCPage.Text", "Page " + (pageNo + 1) + " / " + pages);
  b.appendInline("#SkyyCNav", btn("SkyyCNext", "Next >", 120, 0, pageNo < pages - 1 ? B_SEC : B_SECDIS));
  if (pageNo > 0) ev.addEventBinding(@BT@.Activating, "#SkyyCPrev", @EVD@.of("a", "prev"));
  if (pageNo < pages - 1) ev.addEventBinding(@BT@.Activating, "#SkyyCNext", @EVD@.of("a", "next"));
''', '''  if (pages > 0) {   // 0.8.14: pages 0 = a scrolling view (the recipe lists) - no pager; the ADD FUEL picker keeps its pages
    b.appendInline("#SkyyCNav", btn("SkyyCPrev", "< Prev", 120, 0, pageNo > 0 ? B_SEC : B_SECDIS));
    b.appendInline("#SkyyCNav", lbl("SkyyCPage", 200, 32, L_CAPC));
    b.set("#SkyyCPage.Text", "Page " + (pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyCNav", btn("SkyyCNext", "Next >", 120, 0, pageNo < pages - 1 ? B_SEC : B_SECDIS));
    if (pageNo > 0) ev.addEventBinding(@BT@.Activating, "#SkyyCPrev", @EVD@.of("a", "prev"));
    if (pageNo < pages - 1) ev.addEventBinding(@BT@.Activating, "#SkyyCNext", @EVD@.of("a", "next"));
  }
''')
# build(): what sits above the list
P.rep('''  if (this.tab != null && this.tab.startsWith("P:")) { buildProc(b, ev, p, u, k); return; }
''', '''  // 0.8.14: the height above the scroll list (tab rows, the search row, the materials line, the campfire line) + the foot below it
  this.usedH = 42 * (tabRow + 1) + (srow ? 40 : 0) + 22 + (campTab ? 24 : 0) + 66;
  if (this.tab != null && this.tab.startsWith("P:")) { buildProc(b, ev, p, u, k); return; }
''')
P.rep('''  int per = 9;
  int pages = (this.rows.size() + per - 1) / per; if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    @CRR@ r = (@CRR@) this.rows.get(i);
    int lim = limit(r, mats);
    drawRow(b, ev, i, r, mats, lim, campTab ? campRowNote(p, u, k, r) : "", lim, false, "");
  }
  if (this.rows.size() == 0) {
    b.appendInline("#SkyyCraftBody", lbl("SkyyCEmpty", 1152, 30, L_TEXTC));
    b.set("#SkyyCEmpty.Text", searching ? ("Nothing matches " + this.query + " in Crafting, Artifacts, Gear or Farming.") : (campTab ? "No campfire dishes are loaded." : "No recipes here yet."));
  }
  if (srow) b.set("#SkyyCSearchInfo.Text", searching ? (this.rows.size() + " found in Crafting, Artifacts, Gear and Farming") : "searches Crafting, Artifacts, Gear and Farming");
  foot(b, ev, this.pageNo, pages, only, true, false);
''', '''  // 0.8.14 (Skyy "reduce the items show on page to 6 and allow scroll instead of pages"): ONE scrolling list, every row (up to MAXROWS)
  listOpen(b, this.usedH);
  this.rowSz = rowSize(this.rows.size() < MAXROWS ? this.rows.size() : MAXROWS, this.usedH);   // few rows -> larger rows that all fit
  int drawn = 0;
  for (int i = 0; i < this.rows.size() && i < MAXROWS; i++) {
    @CRR@ r = (@CRR@) this.rows.get(i);
    int lim = limit(r, mats);
    drawRow(b, ev, i, r, mats, lim, campTab ? campRowNote(p, u, k, r) : "", lim, false, "");
    drawn++;
  }
  listMore(b, drawn, this.rows.size());
  if (this.rows.size() == 0) {
    b.appendInline("#SkyyCList", lbl("SkyyCEmpty", 1100, 40, L_TEXTC));
    b.set("#SkyyCEmpty.Text", searching ? ("Nothing matches " + this.query + " in Crafting, Gear or Farming.") : (campTab ? "No campfire dishes are loaded." : "No recipes here yet."));
  }
  if (srow) b.set("#SkyyCSearchInfo.Text", searching ? (this.rows.size() + " found in Crafting, Gear and Farming") : "searches Crafting, Gear and Farming");
  foot(b, ev, 0, 0, only, true, false);
''')
# buildProc: the same list below its status / output / fuel lines
P.rep('''  if (this.fuelPick && view.needsFuel && !broken) { fuelPicker(b, ev, p, k, bench, view); return; }
''', '''  if (this.fuelPick && view.needsFuel && !broken) { fuelPicker(b, ev, p, k, bench, view); return; }
  this.usedH = this.usedH + 26 + 22 + 18 + 22 + 46 + (view.needsFuel ? 42 : 0);   // 0.8.14: status, progress, bar, queue, output (+ fuel) lines
''')
P.rep('''  int per = 7;
  int pages = (this.rows.size() + per - 1) / per; if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    @CRR@ r = (@CRR@) this.rows.get(i);
    int lim = limit(r, mats);
    int allN = lim < room ? lim : room;
    drawRow(b, ev, i, r, mats, lim, "", allN, true, @PKG@.ProcBench.dur(@PKG@.ProcBench.unitMs(r, bench, tier)) + " each");
  }
  if (this.rows.size() == 0) {
    b.appendInline("#SkyyCraftBody", lbl("SkyyCEmpty", 1152, 30, L_TEXTC));
    b.set("#SkyyCEmpty.Text", tier > 0 ? "No recipes here yet." : ("Equip a " + bench + " accessory in your accessory bag to queue more."));
  }
  foot(b, ev, this.pageNo, pages, only, true, true);
''', '''  listOpen(b, this.usedH);   // 0.8.14: one scrolling list, as the instant tabs
  this.rowSz = rowSize(this.rows.size() < MAXROWS ? this.rows.size() : MAXROWS, this.usedH);
  int drawn = 0;
  for (int i = 0; i < this.rows.size() && i < MAXROWS; i++) {
    @CRR@ r = (@CRR@) this.rows.get(i);
    int lim = limit(r, mats);
    int allN = lim < room ? lim : room;
    drawRow(b, ev, i, r, mats, lim, "", allN, true, @PKG@.ProcBench.dur(@PKG@.ProcBench.unitMs(r, bench, tier)) + " each");
    drawn++;
  }
  listMore(b, drawn, this.rows.size());
  if (this.rows.size() == 0) {
    b.appendInline("#SkyyCList", lbl("SkyyCEmpty", 1100, 40, L_TEXTC));
    b.set("#SkyyCEmpty.Text", tier > 0 ? "No recipes here yet." : ("Equip a " + bench + " accessory in your accessory bag to queue more."));
  }
  foot(b, ev, 0, 0, only, true, true);
''')

# ================================================================================================ 4: no accessory recipe in /craft
P.rep('''  t.add(new String[] {{ "A:art", "Artifacts" }});   // 0.8.7: every accessory recipe (artifact())
''', '''  // 0.8.14: no Artifacts tab - accessories are crafted in the Accessory Bag only (SkyyAccessories 0.5.21)
''')
P.rep('''  else if (tabId.equals("A:art")) grp = 3;   // 0.8.7
''', '''  // 0.8.14: no A:art (Artifacts) tab any more
''')
P.rep('''    // 0.8.7: an accessory recipe shows on the Artifacts tab only (never Crafting / Smithing / Farming)
    if (grp >= 0 && (artifact(rc) ? 3 : tabGroup(rc)) != grp) continue;
''', '''    // 0.8.14: an accessory recipe is never listed in /craft (any tab) - the Accessory Bag crafts them (SkyyAccessories 0.5.21)
    if (artifact(rc)) continue;
    if (grp >= 0 && tabGroup(rc) != grp) continue;
''')
P.rep('''    if (tableOnly(rc)) continue;
    if (!{PKG}.KnowSync.allowed(rc, u, this.known, this.coll)) continue;
    {MQ} po = rc.getPrimaryOutput();
    if (nameMatches(q,''', '''    if (tableOnly(rc)) continue;
    if (artifact(rc)) continue;   // 0.8.14: no accessory recipe in /craft search either
    if (!{PKG}.KnowSync.allowed(rc, u, this.known, this.coll)) continue;
    {MQ} po = rc.getPrimaryOutput();
    if (nameMatches(q,''')

# ================================================================================================ 5: no level gate on the Void upgrade
# Skyy 2026-10-16 (screenshot: Farming 'Upgrade to Unique (x1.5) ... Needs Farming Lv 10 (you: 3)', every material met, UPGRADE greyed):
# "remove the level cap on upgrading the pocket dimensions. if i have the stuff, my lvl shouldn't stop me on this" -> the upgrade checks
# the materials only. The pd.gate.* rows stay in the file / Server Setup (marked unused) so no config line changes; the build-time space
# check at the old gate levels (_gate_room_check) and every cost / space number are unchanged.
P.rep('''  int lv = level(u, k, ci);
  int g = @PKG@.SackCfg.gate(to);
  if (lv < g) return "-Needs " + cat + " Lv " + g + " (you: " + lv + ")";
''', '''  // 0.8.14 (Skyy "if i have the stuff, my lvl shouldn't stop me on this"): no level gate - the materials alone decide
''')
P.rep('''    int g = @PKG@.SackCfg.gate(to);
    boolean gateOk = lv >= g;
    t3 = gateOk ? ("Level gate " + cats[ci] + " Lv " + g + " - done") : ("Needs " + cats[ci] + " Lv " + g + " (you: " + lv + ")");
    gcol = gateOk ? "@C:have@" : "@C:out@";
    cost = @PKG@.SackCfg.parseCost(@PKG@.SackCfg.cost(ci, to));
    ready = gateOk && cost != null;
''', '''    // 0.8.14 (Skyy "remove the level cap on upgrading the pocket dimensions"): no 'Needs <cat> Lv' line - the cost cells below decide
    t3 = "Pay the items below to upgrade";
    cost = @PKG@.SackCfg.parseCost(@PKG@.SackCfg.cost(ci, to));
    ready = cost != null;
''')
P.rep('''] + [_pdrow("pd.gate." + PD_RAR[i + 1], "Level needed for %s" % PD_RAR[i + 1], "void", "int", str(g), "1", "10000", "", "live,adv",
            "A category needs this storage level before its %s upgrade (coins never skip it)." % PD_RAR[i + 1], "PD_GATE_" + PD_RAR[i + 1].upper(),''',
      '''] + [_pdrow("pd.gate." + PD_RAR[i + 1], "Level for %s (not used)" % PD_RAR[i + 1], "void", "int", str(g), "1", "10000", "", "live,adv",
            "Not used since SkyySacks 0.8.14 - the %s upgrade needs only its items (Skyy: no level cap)." % PD_RAR[i + 1], "PD_GATE_" + PD_RAR[i + 1].upper(),''')

# ================================================================================================ 6: the Workbench tab name has ONE writer
# tools/skyywbtab.py TAB_TEXT "Accessories & Bags" -> "Bags" (accessories left the bench). Both jars wrote its two lang lines (langdup WARN);
# a different value in each would FAIL langdup until SkyyAccessories is rebuilt, so SkyySacks stops writing them - SkyyAccessories (the
# tab's OWNER) writes the name; its next build reads "Bags" from the shared table.
P.rep('''lang.extend(WB.LANG_LINES)   # 0.7.10: the Workbench tab name (the same two lines SkyyAccessories 0.5.2 ships)
''', '''# 0.8.14: the Workbench tab name lines (WB.LANG_LINES) are SkyyAccessories' only (one writer per lang key, tools/ci/langdup.py)
''')
P.rep('''    for l in WB.LANG_LINES:
        assert l in lang, l
''', '''    for l in WB.LANG_LINES:
        assert l not in lang, l   # 0.8.14: SkyyAccessories (the owner) writes the tab name
''')

# ================================================================================================ 7: the click names its recipe (critic fix)
# A row's events carry the recipe id (craft:<i>:<n>:<recipeId> / pq:<i>:<n>:<recipeId>); the click is resolved BY ID against the list the
# page holds now (place i first, then a search); an id no longer listed = "That row changed - nothing was crafted" (never another recipe).
P.rep('''    ev.addEventBinding(@BT@.Activating, "#" + bid + i, @EVD@.of("a", a0 + i + ":1"));
    ev.addEventBinding(@BT@.Activating, "#" + tid + i, @EVD@.of("a", a0 + i + ":10"));
    ev.addEventBinding(@BT@.Activating, "#" + aid + i, @EVD@.of("a", a0 + i + ":0"));
''', '''    String rk = ":" + String.valueOf(r.getId());   // 0.8.14: the recipe id rides along (resolved by id - rowOf)
    ev.addEventBinding(@BT@.Activating, "#" + bid + i, @EVD@.of("a", a0 + i + ":1" + rk));
    ev.addEventBinding(@BT@.Activating, "#" + tid + i, @EVD@.of("a", a0 + i + ":10" + rk));
    ev.addEventBinding(@BT@.Activating, "#" + aid + i, @EVD@.of("a", a0 + i + ":0" + rk));
''')
P.rep('''cpg.addMethod(CtNewMethod.make(jt(r"""
public boolean handleProc(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, String data, String act) {''', '''# 0.8.14 (critic fix): "<i>:<n>:<recipeId>" -> that recipe in the CURRENT list (place i if it still holds it, else a search by id); null =
# the id is not listed any more (or an old two-part event) - the caller crafts nothing
cpg.addMethod(CtNewMethod.make(jt(r"""
public @CRR@ rowOf(String rest) {
  if (rest == null || this.rows == null) return null;
  String[] parts = rest.split(":", 3);
  if (parts.length < 3 || parts[2].length() == 0) return null;
  int idx = -1;
  try { idx = Integer.parseInt(parts[0]); } catch (Throwable t) { idx = -1; }
  String rid = parts[2];
  if (idx >= 0 && idx < this.rows.size()) {
    @CRR@ r0 = (@CRR@) this.rows.get(idx);
    if (r0 != null && rid.equals(String.valueOf(r0.getId()))) return r0;
  }
  for (int i = 0; i < this.rows.size(); i++) {
    @CRR@ r1 = (@CRR@) this.rows.get(i);
    if (r1 != null && rid.equals(String.valueOf(r1.getId()))) return r1;
  }
  return null;
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public boolean handleProc(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, String data, String act) {''')
P.rep('''    String[] parts = act.substring(3).split(":");
    int idx = -1; int want = 0;
    try { idx = Integer.parseInt(parts[0]); want = Integer.parseInt(parts[1]); } catch (Throwable t) { idx = -1; }
    if (this.rows != null && idx >= 0 && idx < this.rows.size()) {
      int tier = accTier(accessories(p, u), bench);
      if (tier <= 0) this.info = "equip a " + bench + " accessory to queue";
      else this.info = procQueue(p, st, ref, k, bench, tier, (@CRR@) this.rows.get(idx), want);
    }
''', '''    String[] parts = act.substring(3).split(":");
    int want = 0;
    try { want = Integer.parseInt(parts[1]); } catch (Throwable t) { want = -1; }
    @CRR@ pr0 = want < 0 ? null : rowOf(act.substring(3));   // 0.8.14: by recipe id (critic fix)
    if (pr0 == null) this.info = "That row changed - nothing was queued. Try again.";
    else {
      int tier = accTier(accessories(p, u), bench);
      if (tier <= 0) this.info = "equip a " + bench + " accessory to queue";
      else this.info = procQueue(p, st, ref, k, bench, tier, pr0, want);
    }
''')
P.rep('''    String[] parts = act.substring(6).split(":");
    int idx = -1; int want = 0;
    try { idx = Integer.parseInt(parts[0]); want = Integer.parseInt(parts[1]); } catch (Throwable t) { idx = -1; }
    if (this.rows == null || idx < 0 || idx >= this.rows.size()) return;
    @CRR@ r = (@CRR@) this.rows.get(idx);
''', '''    String[] parts = act.substring(6).split(":");
    int want = 0;
    try { want = Integer.parseInt(parts[1]); } catch (Throwable t) { return; }
    @CRR@ r = rowOf(act.substring(6));   // 0.8.14 (critic fix): by recipe id against the list shown now - never another row's recipe
    if (r == null) { this.info = "That row changed - nothing was crafted. Try again."; rebuild(); return; }
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added or removed"
assert '"A:art"' not in P.s and "SACKS_HOME_JAVA" not in P.s and "52298ac" in P.s   # (52298ac stays only in the 0.8.13 history notes)
P.finish()
