"""Derive SkyyAuctions/build_skyyauctions_0.1.3.py from the GENERATED 0.1.2 script (the SET pin):
    python tools/auctions_0_1_3_patch.py
    python SkyyAuctions/build_skyyauctions_0.1.3.py          (must end 'assembled ...SkyyAuctions-0.1.3.jar')
    python SkyyAuctions/test_skyyauctions_0.1.3.py           (harness)
Edit THIS patch, never the generated script.

0.1.3 (2026-10-09) = Skyy LOCKED 2026-10-09 (docs/answered/economy.md): "auction house needs sorting filters too" -> sort by price
low / high, ending soonest, newest listed; filters by category, rarity, level range (+ keep the search). Browse page only - no listing /
buy / bid / coin / claim logic changes, no new saved data, no config keys, no migration.

A. SORT (unchanged comparator AhSort 0..3, relabelled): "Price low-high" (the default = what 0.1.2 did), "Price high-low", "Ending
   soonest", "Newest listed". A cycle button (the kit has no proven dropdown: skyyui UNVERIFIED "dropdown", PROBED is empty).
B. CATEGORY row, 8 buttons: All, Weapons, Armor, Tools, Accessories, Materials, Consumables, Other. Computed at browse time
   (AhItem.fcat, cached per item id + the record's stored category) - so listings made before 0.1.3 sort into the new buttons too and
   nothing is rewritten on disk. Rules (AhItem.fcatRule, pure): ACCESSORIES (stored, Skyy_Talisman_*, Skyy_Accessory_* except the Bag)
   -> Skyy_Unid_Weapon_* WEAPONS / Skyy_Unid_Armor_* ARMOR (research/Loot-Unid-Spec.md: "SkyyAuctions 0.1.3 AH categories") -> the
   stored WEAPONS / ARMOR / CONSUMABLES (0.1's engine checks at listing time) -> TOOLS (the item's Tool or Glider block, Tool_*,
   Items.Tools, SkyyFishing rods + rod parts) -> OTHER for Furniture.* -> MATERIALS (stored BLOCKS, Items.Ingredients, Blocks.*,
   Ingredient_ / Ore_ / Metal_ / Rock_ / Wood_ / Plant_ / Soil_ / Cloth_ / Rubble_) -> OTHER (incl. mystery bags Skyy_Unid_Bag_*, which
   can become a weapon OR armor piece, Magic Bags, keys, furniture). Consumables kept as its own button (0.1.2 had it; Skyy's list did
   not name it - dropping it would hide food / potions under Other). 0.1.2's "Blocks" button is now part of Materials.
C. RARITY: 0.1.2's filter, unchanged (SkyyGear ladder from gear:tiers incl. Mythic / Set and any tier SkyyGear adds later, e.g.
   Untiered, then the vanilla tiers). The button shows gold while a rarity is picked. NOTE (fixer 2026-10-09): docs/answered/economy.md
   LOCKED 2026-10-08 market wall = Mythic + UT + Sets never bought / sold on Auctions (built in the UT/Mythic round, not yet). Kept in
   the cycle for now (Skyy asked for them by name; nothing is blocked today); once the wall lands those tiers can never match -> that
   round should skip wall tiers in this cycle (the in-game steps tell Skyy they show the empty state then).
D. LEVEL RANGE: two 3-digit text fields "min" / "max" (Enter or any click applies, like the search box). A listing's level =
   gear:fn:level (SkyyGear) cached per listing id + rev + gear:tiers + config:epoch:SkyyGear (like the rarity cache). While a bound is
   set, listings without a level (non-gear) are hidden. min > max is swapped; a non-number keeps the old bound and says so. Without
   SkyyGear the row says "Level filter needs SkyyGear" and no level field is bound (no event refers to a missing element).
E. RESET button (red while anything differs from the defaults): category All, sort Price low-high, rarity Any, search and levels empty,
   page 1. Every filter / sort change goes back to page 1; the pager clamps as before. A summary line ("Showing Weapons, Rare, Lv 10 to
   20, 'sword'"; the search part cut at 18 characters so the worst case, "Showing Consumables, Legendary, Lv 100 to 200, 'WWWWWWWWWWWWWWWW..'",
   measures 583 of its 636 px with the game's NunitoSans metrics) sits next to Reset; the empty text says to Reset when filters hide
   everything.
F. LAYOUT (1080 fit): one more 46 px row; the 8 listing rows keep 58 px with a 3 px gap (was 4): 126 top + 3 x 46 + 22 + 8 x 61 + 46
   pager + 30 status = 850 of the 852 inner px (page 1120 x 880, unchanged). Widths: categories 8 x 130 + 7 x 5 = 1075; search row
   330+100+90+230+200+100 + 5 x 6 = 1080; level row 64+80+34+80+10+636+6+160 = 1070 (without SkyyGear 268+10+636+6+160 = 1080).
   Kept the page's own button styles (BS / BS_ON / BS_RED / BS_BLUE) so the Browse view does not mix two looks; moving the whole AH
   onto tools/skyyui.py is its own round (the Bazaar did it in 0.1.3).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.2.py")
dst = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:120])
    s = s.replace(old, new)


def rep_method(cls, head, new_src):
    """Replace one whole M(cls, r'''...''') block whose Java starts with `head` by new_src (Java text from 'public ...' to the last '}')."""
    global s
    start_mark = 'M(%s, r"""\n%s' % (cls, head)
    assert s.count(start_mark) == 1, "method anchor count %d: %s" % (s.count(start_mark), head)
    a = s.index(start_mark)
    b = s.index('\n}""")', a) + len('\n}""")')
    s = s[:a] + 'M(%s, r"""\n%s\n}""")' % (cls, new_src.strip("\n").rstrip("}").rstrip()) + s[b:]


rep('VERSION = "0.1.2"', 'VERSION = "0.1.3"')
s = ('"""0.1.3 (2026-10-09): Auction House sort + filters (Skyy: "auction house needs sorting filters too") - sort price low / high,\n'
     '  ending soonest, newest listed; category (All, Weapons, Armor, Tools, Accessories, Materials, Consumables, Other), rarity, level\n'
     '  range (SkyyGear level), Reset. Browse page only. Notes in tools/auctions_0_1_3_patch.py.\n' + s[3:])

# ======================================================================= probes (the new engine members read at browse time)
rep('''(T["ITM"], "getWeapon"), (T["ITM"], "getArmor"),''',
    '''(T["ITM"], "getWeapon"), (T["ITM"], "getArmor"), (T["ITM"], "getCategories"), (T["ITM"], "getAssetMap"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),''')

# ======================================================================= AhItem: filter categories + level cache
MAT_PREFIX = ["Ingredient_", "Ore_", "Metal_", "Rock_", "Wood_", "Plant_", "Soil_", "Cloth_", "Rubble_"]
TOOL_PREFIX = ["Tool_", "SkyyFishing_Rod", "SkyyFishing_Line", "SkyyFishing_Hook", "SkyyFishing_Sinker", "SkyyFishing_Reel"]
rep('''F(itm, "public static String[] TIER_NAME;")''',
    '''# 0.1.3 browse filter categories (computed at browse time from the item id + the stored 0.1 category; nothing on disk changes)
F(itm, 'public static final String[] FCAT = new String[] { "ALL", "WEAPONS", "ARMOR", "TOOLS", "ACCESSORIES", "MATERIALS", "CONSUMABLES", "OTHER" };')
F(itm, 'public static final String[] FCAT_LABEL = new String[] { "All", "Weapons", "Armor", "Tools", "Accessories", "Materials", "Consumables", "Other" };')
F(itm, "public static final String[] MAT_PREFIX = new String[] { %s };" % ", ".join(jstr(_p) for _p in @MATP@))
F(itm, "public static final String[] TOOL_PREFIX = new String[] { %s };" % ", ".join(jstr(_p) for _p in @TOOLP@))
F(itm, "public static final java.util.concurrent.ConcurrentHashMap FCACHE = new java.util.concurrent.ConcurrentHashMap();")
F(itm, "public static final java.util.concurrent.ConcurrentHashMap LCACHE = new java.util.concurrent.ConcurrentHashMap();")
F(itm, "public static String[] TIER_NAME;")'''.replace("@MATP@", repr(MAT_PREFIX)).replace("@TOOLP@", repr(TOOL_PREFIX)))

rep('''# the filter tier of a listing, cached per id + rev + gear:tiers + SkyyGear's config epoch''',
    '''# 0.1.3 the browse category of an item (pure, bare-JVM tested): id rules + the stored 0.1 category + the item asset's Categories
# ("|Items.Ingredients|Blocks.Ores|") and Tool / Glider block (tool). First match wins (tools/auctions_0_1_3_patch.py B).
M(itm, r"""
public static String fcatRule(String id0, String stored0, String cats0, boolean tool) {
  String id = id0 == null ? "" : id0;
  String stored = stored0 == null ? "" : stored0;
  String cats = cats0 == null ? "" : cats0;
  if ("ACCESSORIES".equals(stored) || id.startsWith("Skyy_Talisman_") || (id.startsWith("Skyy_Accessory_") && !id.equals("Skyy_Accessory_Bag"))) return "ACCESSORIES";
  if (id.startsWith("Skyy_Unid_Weapon_")) return "WEAPONS";
  if (id.startsWith("Skyy_Unid_Armor_")) return "ARMOR";
  if ("WEAPONS".equals(stored) || "ARMOR".equals(stored) || "CONSUMABLES".equals(stored)) return stored;
  if (tool || cats.indexOf("|Items.Tools|") >= 0) return "TOOLS";
  String[] tp = TOOL_PREFIX;
  for (int i = 0; i < tp.length; i++) if (id.startsWith(tp[i])) return "TOOLS";
  if (cats.indexOf("|Furniture.") >= 0) return "OTHER";
  if ("BLOCKS".equals(stored) || cats.indexOf("|Items.Ingredients|") >= 0 || cats.indexOf("|Blocks.") >= 0) return "MATERIALS";
  String[] mp = MAT_PREFIX;
  for (int i = 0; i < mp.length; i++) if (id.startsWith(mp[i])) return "MATERIALS";
  return "OTHER";
}""")
# the browse category of a listing, cached per item id + stored category (the item asset is read once; no asset = id rules only)
M(itm, r"""
public static String fcat(@BD@ r) {
  String id = @PKG@.AhRec.subStr(r, "item", "id", "");
  String stored = @PKG@.AhRec.str(r, "category", "MISC");
  String k = id + "|" + stored;
  Object o = FCACHE.get(k);
  if (o instanceof String) return (String) o;
  String cats = "|";
  boolean tool = false;
  try {
    Object a = @ITM@.getAssetMap().getAsset(id);
    if (a instanceof @ITM@) {
      @ITM@ it = (@ITM@) a;
      try { tool = it.getTool() != null || it.getGlider() != null; } catch (Throwable t) { tool = false; }
      try {
        String[] cs = it.getCategories();
        for (int i = 0; cs != null && i < cs.length; i++) if (cs[i] != null) cats = cats + cs[i] + "|";
      } catch (Throwable t) { }
    }
  } catch (Throwable t) { }
  String c = fcatRule(id, stored, cats, tool);
  if (FCACHE.size() > 20000) FCACHE.clear();
  FCACHE.put(k, c);
  return c;
}""")
# 0.1.3 the SkyyGear level of a listing (gear:fn:level on {id, a CLONE of the metadata}) or -1 (not gear / no SkyyGear), cached like
# tierOfRec per id + rev + gear:tiers + SkyyGear's config epoch
M(itm, r"""
public static int levelOfRec(@BD@ r) {
  tiers();
  String id = @PKG@.AhRec.id(r);
  String rev = String.valueOf(@PKG@.AhRec.lng(r, "rev", 0L));
  Object ep = null;
  try { ep = @PKG@.AhUtil.bridge().get("config:epoch:SkyyGear"); } catch (Throwable t) { ep = null; }
  String k = TIER_KEY + "|" + ep;
  Object o = LCACHE.get(id);
  if (o instanceof String[]) {
    String[] a = (String[]) o;
    if (a[0].equals(rev) && a[1].equals(k)) { try { return Integer.parseInt(a[2]); } catch (Throwable t) { } }
  }
  @BD@ it = @PKG@.AhRec.sub(r, "item");
  Object lv = gcall("gear:fn:level", gx(@PKG@.AhRec.str(it, "id", ""), @PKG@.AhRec.sub(it, "meta")));
  int n = lv instanceof Number ? ((Number) lv).intValue() : -1;
  if (n < 0) n = -1;
  if (LCACHE.size() > 20000) LCACHE.clear();
  LCACHE.put(id, new String[] { rev, k, String.valueOf(n) });
  return n;
}""")
# the filter tier of a listing, cached per id + rev + gear:tiers + SkyyGear's config epoch''')

# ======================================================================= AhPage: fields, sort names, evd
rep('''F(page, 'public static final String[] SORT_NAME = new String[] { "Lowest price", "Highest price", "Ending soon", "Newest" };')''',
    '''F(page, 'public static final String[] SORT_NAME = new String[] { "Price low-high", "Price high-low", "Ending soonest", "Newest listed" };')
# 0.1.3 level range (0 = no bound) + whether this render shows the level fields (SkyyGear loaded) - evd binds them only then
F(page, "public int lvMin;")
F(page, "public int lvMax;")
F(page, "public boolean lvShown;")''')
rep('''  this.cat = 0; this.sort = 0; this.rar = 0; this.query = ""; this.browsePage = 0;''',
    '''  this.cat = 0; this.sort = 0; this.rar = 0; this.query = ""; this.browsePage = 0;
  this.lvMin = 0; this.lvMax = 0; this.lvShown = false;''')
rep('''  if ("browse".equals(this.view)) d = d.append("@AhSearch", "#SkyyAhSearch.Value");''',
    '''  if ("browse".equals(this.view)) {
    d = d.append("@AhSearch", "#SkyyAhSearch.Value");
    if (this.lvShown) d = d.append("@AhLvMin", "#SkyyAhLvMin.Value").append("@AhLvMax", "#SkyyAhLvMax.Value");
  }''')

# ======================================================================= Browse: results + render
rep('''# ---- Browse (46 + 46 + 22 + 8 x 62 + 46 = 656, + top 126 + status 30 = 812)''',
    '''# 0.1.3 browse helpers: a typed level (0 = none, -1 = not a number), the summary line, any filter on
M(page, r"""
public static int parseLv(String s) {
  if (s == null) return 0;
  String t = s.trim();
  if (t.length() == 0) return 0;
  if (t.length() > 4) return -1;
  for (int i = 0; i < t.length(); i++) { char c = t.charAt(i); if (c < '0' || c > '9') return -1; }
  int v = Integer.parseInt(t);
  return v > 999 ? 999 : v;
}""")
M(page, r"""
public static String lvText(int a, int z) {
  if (a > 0 && z > 0) return a == z ? "Lv " + a : "Lv " + a + " to " + z;
  if (a > 0) return "Lv " + a + "+";
  if (z > 0) return "Lv up to " + z;
  return "";
}""")
M(page, r"""
public boolean filtersOn() {
  return this.cat != 0 || this.rar != 0 || this.lvMin > 0 || this.lvMax > 0 || (this.query != null && this.query.length() > 0);
}""")
M(page, r"""
public String filterLine() {
  @PKG@.AhItem.tiers();
  String[] fl = @PKG@.AhItem.FCAT_LABEL;
  String[] tn = @PKG@.AhItem.TIER_NAME;
  String s = "";
  if (this.cat > 0 && this.cat < fl.length) s = s + ", " + fl[this.cat];
  if (this.rar > 0 && tn != null && this.rar <= tn.length) s = s + ", " + tn[this.rar - 1];
  if (this.lvMin > 0 || this.lvMax > 0) s = s + ", " + lvText(this.lvMin, this.lvMax);
  if (this.query != null && this.query.length() > 0) s = s + ", '" + @PKG@.AhItem.clip(this.query, 18) + "'";
  if (s.length() == 0) return "Showing every listing";
  return @PKG@.AhItem.clip("Showing " + s.substring(2), 80);
}""")
# ---- Browse (3 x 46 + 22 + 8 x 61 + 46 = 654, + top 126 + status 30 = 850 of 852)''')

rep_method("page", "public java.util.ArrayList results(long now) {", r"""
public java.util.ArrayList results(long now) {
  java.util.ArrayList all = @PKG@.AhStore.active(now);
  java.util.ArrayList out = new java.util.ArrayList();
  @PKG@.AhItem.tiers();
  String[] fc = @PKG@.AhItem.FCAT;
  String cat = fc[this.cat < 0 || this.cat >= fc.length ? 0 : this.cat];
  String tn = null;
  String[] tnames = @PKG@.AhItem.TIER_NAME;
  if (this.rar > 0 && tnames != null && this.rar <= tnames.length) tn = tnames[this.rar - 1];
  boolean lv = (this.lvMin > 0 || this.lvMax > 0) && @PKG@.AhItem.gearOn();
  String q = this.query == null ? "" : this.query.trim().toLowerCase();
  for (int i = 0; i < all.size(); i++) {
    @BD@ r = (@BD@) all.get(i);
    if (!"ALL".equals(cat) && !cat.equals(@PKG@.AhItem.fcat(r))) continue;
    if (tn != null && !tn.equals(@PKG@.AhItem.tierOfRec(r))) continue;
    if (lv) {
      int l = @PKG@.AhItem.levelOfRec(r);
      if (l < 0 || (this.lvMin > 0 && l < this.lvMin) || (this.lvMax > 0 && l > this.lvMax)) continue;
    }
    if (q.length() > 0 && @PKG@.AhRec.str(r, "search", "").indexOf(q) < 0) continue;
    out.add(r);
  }
  java.util.Collections.sort(out, new @PKG@.AhSort(this.sort < 0 || this.sort >= SORT_NAME.length ? 0 : this.sort));
  return out;
}""")

# renderBrowse: the category row (8), the search row (+ sort / rarity / refresh), the NEW level row (+ summary + Reset), rows 58 + 3
OLD_TOP = '''  b.appendInline("#SkyyAh", "Group #SkyyAhCats { Anchor: (Height: 46); LayoutMode: Left; }");
  for (int i = 0; i < 7; i++) {
    if (i > 0) sp(b, "#SkyyAhCats", 5, 40);
    btn(b, ev, "#SkyyAhCats", "SkyyAhCat" + i, 148, 40, @PKG@.AhItem.CAT_LABEL[i], i == this.cat ? BS_ON : BS, "cat:" + i);
  }'''
NEW_TOP = '''  String[] fl = @PKG@.AhItem.FCAT_LABEL;
  if (this.cat < 0 || this.cat >= fl.length) this.cat = 0;
  if (!this.lvShown) { this.lvMin = 0; this.lvMax = 0; }
  b.appendInline("#SkyyAh", "Group #SkyyAhCats { Anchor: (Height: 46); LayoutMode: Left; }");
  for (int i = 0; i < fl.length; i++) {
    if (i > 0) sp(b, "#SkyyAhCats", 5, 40);
    btn(b, ev, "#SkyyAhCats", "SkyyAhCat" + i, 130, 40, fl[i], i == this.cat ? BS_ON : BS, "cat:" + i);
  }'''
rep(OLD_TOP, NEW_TOP)
rep('''  btn(b, ev, "#SkyyAhFilt", "SkyyAhSort", 220, 40, "Sort: " + SORT_NAME[this.sort < 0 || this.sort > 3 ? 0 : this.sort], BS, "sort");''',
    '''  btn(b, ev, "#SkyyAhFilt", "SkyyAhSort", 230, 40, "Sort: " + SORT_NAME[this.sort < 0 || this.sort >= SORT_NAME.length ? 0 : this.sort], BS, "sort");''')
rep('''  btn(b, ev, "#SkyyAhFilt", "SkyyAhRar", 190, 40, "Rarity: " + (this.rar == 0 ? "Any" : @PKG@.AhItem.TIER_NAME[this.rar - 1]), BS, "rar");
  sp(b, "#SkyyAhFilt", 6, 40);
  btn(b, ev, "#SkyyAhFilt", "SkyyAhRefresh", 100, 40, "Refresh", BS_BLUE, "refresh");''',
    '''  btn(b, ev, "#SkyyAhFilt", "SkyyAhRar", 200, 40, "Rarity: " + (this.rar == 0 ? "Any" : @PKG@.AhItem.TIER_NAME[this.rar - 1]), this.rar == 0 ? BS : BS_ON, "rar");
  sp(b, "#SkyyAhFilt", 6, 40);
  btn(b, ev, "#SkyyAhFilt", "SkyyAhRefresh", 100, 40, "Refresh", BS_BLUE, "refresh");
  b.appendInline("#SkyyAh", "Group #SkyyAhLv { Anchor: (Height: 46); LayoutMode: Left; }");
  if (this.lvShown) {
    txt(b, "#SkyyAhLv", "SkyyAhLvLab", 64, 40, 15, true, "#cfe3ff", null, false, "Level");
    b.appendInline("#SkyyAhLv", "Group #SkyyAhLvMinBox { Anchor: (Width: 80, Height: 40); Background: #16263a; }");
    b.appendInline("#SkyyAhLvMinBox", "TextField #SkyyAhLvMin { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 3; PlaceholderText: \\"min\\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
    if (this.lvMin > 0) b.set("#SkyyAhLvMin.Value", String.valueOf(this.lvMin));
    ev.addEventBinding(@BT@.Validating, "#SkyyAhLvMin", evd("search"), false);
    txt(b, "#SkyyAhLv", "SkyyAhLvTo", 34, 40, 15, true, "#cfe3ff", "Center", false, "to");
    b.appendInline("#SkyyAhLv", "Group #SkyyAhLvMaxBox { Anchor: (Width: 80, Height: 40); Background: #16263a; }");
    b.appendInline("#SkyyAhLvMaxBox", "TextField #SkyyAhLvMax { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 3; PlaceholderText: \\"max\\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
    if (this.lvMax > 0) b.set("#SkyyAhLvMax.Value", String.valueOf(this.lvMax));
    ev.addEventBinding(@BT@.Validating, "#SkyyAhLvMax", evd("search"), false);
    sp(b, "#SkyyAhLv", 10, 40);
  } else {
    txt(b, "#SkyyAhLv", "SkyyAhLvOff", 268, 40, 14, false, "#8fa4b8", null, false, "Level filter needs SkyyGear");
    sp(b, "#SkyyAhLv", 10, 40);
  }
  txt(b, "#SkyyAhLv", "SkyyAhFiltTxt", 636, 40, 14, false, "#9fb8cc", null, false, filterLine());
  sp(b, "#SkyyAhLv", 6, 40);
  btn(b, ev, "#SkyyAhLv", "SkyyAhReset", 160, 40, "Reset", filtersOn() || this.sort != 0 ? BS_RED : BS, "reset");''')
rep('''    String e = (this.query != null && this.query.length() > 0) ? "No match for '" + this.query + "'" : "Nothing listed here yet - be the first: Create BIN";
    txt(b, "#SkyyAh", "SkyyAhEmpty", 0, 496, 20, true, "#9fb8cc", "Center", false, e);''',
    '''    boolean qOn = this.query != null && this.query.length() > 0;
    String e;
    if (this.cat != 0 || this.rar != 0 || this.lvMin > 0 || this.lvMax > 0) e = "Nothing matches these filters - click Reset to see every listing";
    else if (qOn) e = "No match for '" + this.query + "'";
    else e = "Nothing listed here yet - be the first: Create BIN";
    txt(b, "#SkyyAh", "SkyyAhEmpty", 0, 488, 20, true, "#9fb8cc", "Center", false, e);''')
# the row gap + the empty-row filler, only inside renderBrowse (the Manage view has the same two lines and keeps them)
_rb = s.index('public void renderBrowse(')
_rb_end = s.index('\n}""")', _rb)
_seg = s[_rb:_rb_end]
_GAP, _FILL = '      sp(b, "#SkyyAh", 0, 4);', '      if (idx >= total) { sp(b, "#SkyyAh", 0, 62); continue; }'
assert _seg.count(_GAP) == 1 and _seg.count(_FILL) == 1
_seg = _seg.replace(_GAP, '      sp(b, "#SkyyAh", 0, 3);').replace(_FILL, _FILL.replace("0, 62)", "0, 61)"))
s = s[:_rb] + _seg + s[_rb_end:]

# the level fields are shown (and bound by evd) only on a Browse render while SkyyGear is loaded; set before renderTop's buttons
rep('''  renderTop(b, ev, u, p);
  if ("item".equals(this.view))''', '''  this.lvShown = "browse".equals(this.view) && @PKG@.AhItem.gearOn();
  renderTop(b, ev, u, p);
  if ("item".equals(this.view))''')

# ======================================================================= events: field reading + browse actions (pure, harness-run)
rep('''M(page, r"""
public void finish(@RES@ r, @REF@ ref, @ST@ st, @PLA@ p) {''', '''# 0.1.3 the Browse text fields carried by every Browse event (search, level min / max); returns a warning for a bad level or null
M(page, r"""
public String readFields(String data) {
  if (data == null) return null;
  String bad = null;
  if (data.indexOf("\\"@AhSearch\\"") >= 0) {
    String q = @PKG@.AhUtil.jsonStr(data, "@AhSearch").trim();
    if (q.length() > 40) q = q.substring(0, 40);
    if (!q.equals(this.query)) { this.query = q; this.browsePage = 0; }
  }
  if (data.indexOf("\\"@AhLvMin\\"") >= 0 || data.indexOf("\\"@AhLvMax\\"") >= 0) {
    int a = parseLv(@PKG@.AhUtil.jsonStr(data, "@AhLvMin"));
    int z = parseLv(@PKG@.AhUtil.jsonStr(data, "@AhLvMax"));
    if (a < 0 || z < 0) {
      bad = "A level is a whole number like 10 or 25 - the old level filter is kept.";
      if (a < 0) a = this.lvMin;
      if (z < 0) z = this.lvMax;
    }
    if (a > 0 && z > 0 && a > z) { int t = a; a = z; z = t; }
    if (a != this.lvMin || z != this.lvMax) { this.lvMin = a; this.lvMax = z; this.browsePage = 0; }
  }
  return bad;
}""")
# 0.1.3 every Browse button (categories, sort, rarity, search / refresh, clear, reset, pager); false = not a Browse action
M(page, r"""
public boolean browseAct(String a) {
  if (a == null) return false;
  if (a.startsWith("cat:")) {
    int i = argInt(a, "cat:");
    if (i >= 0 && i < @PKG@.AhItem.FCAT.length) { this.cat = i; this.browsePage = 0; }
    return true;
  }
  if (a.equals("sort")) { this.sort = (this.sort + 1) % SORT_NAME.length; this.browsePage = 0; return true; }
  if (a.equals("rar")) { @PKG@.AhItem.tiers(); this.rar = (this.rar + 1) % (@PKG@.AhItem.TIER_NAME.length + 1); this.browsePage = 0; return true; }
  if (a.equals("refresh") || a.equals("search")) return true;
  if (a.equals("clear")) { this.query = ""; this.browsePage = 0; return true; }
  if (a.equals("reset")) {
    this.cat = 0; this.sort = 0; this.rar = 0; this.query = ""; this.lvMin = 0; this.lvMax = 0; this.browsePage = 0;
    say("Filters reset - every listing, lowest price first.", 0);
    return true;
  }
  if (a.equals("prev")) { if (this.browsePage > 0) this.browsePage--; return true; }
  if (a.equals("next")) { this.browsePage++; return true; }
  return false;
}""")
M(page, r"""
public void finish(@RES@ r, @REF@ ref, @ST@ st, @PLA@ p) {''')
rep('''    if (data.indexOf("\\"@AhSearch\\"") >= 0) {
      String q = @PKG@.AhUtil.jsonStr(data, "@AhSearch").trim();
      if (q.length() > 40) q = q.substring(0, 40);
      if (!q.equals(this.query)) { this.query = q; this.browsePage = 0; }
    }
    if (data.indexOf("\\"@AhPrice\\"") >= 0) {''', '''    String lvBad = readFields(data);
    if (data.indexOf("\\"@AhPrice\\"") >= 0) {''')
rep('''    else if (a.startsWith("cat:")) { int i = argInt(a, "cat:"); if (i >= 0 && i < 7) { this.cat = i; this.browsePage = 0; } }
    else if (a.equals("sort")) { this.sort = (this.sort + 1) % 4; this.browsePage = 0; }
    else if (a.equals("rar")) { @PKG@.AhItem.tiers(); this.rar = (this.rar + 1) % (@PKG@.AhItem.TIER_NAME.length + 1); this.browsePage = 0; }
    else if (a.equals("refresh") || a.equals("search")) { }
    else if (a.equals("clear")) { this.query = ""; this.browsePage = 0; }
    else if (a.equals("prev")) { if (this.browsePage > 0) this.browsePage--; }
    else if (a.equals("next")) { this.browsePage++; }
''', '''    else if (browseAct(a)) { }
''')
rep('''    rebuild();
  } catch (Throwable t) { @PKG@.AhUtil.warn("auction page click failed: " + t); }''',
    '''    if (lvBad != null && this.status.length() == 0) say(lvBad, 2);
    rebuild();
  } catch (Throwable t) { @PKG@.AhUtil.warn("auction page click failed: " + t); }''')

# ======================================================================= checks
for _gone in ("AhItem.CAT_LABEL[i]", "i < 7) { this.cat", "% 4; this.browsePage", '"Lowest price", "Highest price"', "0, 496, 20"):
    assert _gone not in s, "left over: " + _gone
for _need in ("@PKG@.AhItem.fcat(r)", "@PKG@.AhItem.levelOfRec(r)", "else if (browseAct(a)) { }", "String lvBad = readFields(data);",
              '"SkyyAhReset", 160, 40', "this.lvShown = \"browse\".equals(this.view)"):
    assert s.count(_need) == 1, "missing: " + _need
# methods before callers: readFields / browseAct sit before handleDataEvent and after argInt / say; fcat / levelOfRec before results
assert s.index("public static int argInt(") < s.index("public boolean browseAct(") < s.index("public void handleDataEvent(")
assert s.index("public static int parseLv(") < s.index("public String readFields(")
assert s.index("public String filterLine()") < s.index("public void renderBrowse(")
assert s.index("public static String fcatRule(") < s.index("public static String fcat(") < s.index("public java.util.ArrayList results(")
# 1080 fit: 126 top + 3 x 46 + 22 head + 8 x (58 + 3) + 46 pager + 30 status within 880 - 2 x 14 (root padding)
assert 126 + 3 * 46 + 22 + 8 * (58 + 3) + 46 + 30 <= 880 - 2 * 14
assert 8 * 130 + 7 * 5 <= 1080 and 330 + 100 + 90 + 230 + 200 + 100 + 5 * 6 <= 1080
assert 64 + 80 + 34 + 80 + 10 + 636 + 6 + 160 <= 1080 and 268 + 10 + 636 + 6 + 160 <= 1080
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
