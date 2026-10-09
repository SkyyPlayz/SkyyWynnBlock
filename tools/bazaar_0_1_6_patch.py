"""Derive SkyyBazaar/build_skyybazaar_0.1.6.py (and SkyyBazaar/test_skyybazaar_0.1.6.py) from the LIVE 0.1.5 (build_skyybazaar_0.1.5.py =
the tools/deploy_set.py SET pin; 0.1.5 and every older script stay untouched).
Run:  python tools/bazaar_0_1_6_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.6.py   then   python SkyyBazaar/test_skyybazaar_0.1.6.py
(never --deploy: coordinated deploy). SkyyBazaar uses patch scripts (0.1.1 .. 0.1.5 came from tools/bazaar_0_1_1_patch.py ..
tools/bazaar_0_1_5_patch.py): edit THIS file, never the generated build script.

0.1.6 = A SEARCH BAR. Skyy's own words (2026-10-09, LOCKED in docs/answered/economy.md): "bizzar needs a search bar too"
 - A search row under the purse line: the kit's vanilla search field (tools/skyyui.py search_field: the InputBox patch, 30 high, the tinted
   SearchIcon + the ClearButtonStyle x, placeholder text) + Search (Secondary) + Clear (Secondary) + a caption. The search field look was
   seen working by Skyy on probe page 11 (docs/log/2026-09.md 2026-09-30 "PROBE RESULTS: 19 work - ... search field"); skyyui.PROBED
   was never filled in, so the build passes trial=True / assert_proven(allow=("search-field",)) and says why here.
 - HOW IT FILTERS (the SkyyMenu 0.3.12 Server Setup / SkyyAuctions 0.1.2 pattern - Enter or the Search button, never on every key:
   HANDOFF section 2 "never periodic page updates", the kit's search_field note "a Skyy page filters on Enter / a button"): Enter in the
   field (Validating) or Search applies the typed text; every binding carries the field text ("@BzFind"), so what was typed survives
   other clicks (kept as a draft, put back on every rebuild) but only Enter / Search change the list. A repeated Enter / Search with the
   same text (a double click) keeps the results page instead of jumping back to page 1 (the debounce).
 - MATCHING: case-insensitive substring; the text is split into words and EVERY word must appear in the product's display name or its
   item id (the id also as words: Ore_Copper -> "ore copper"), so "copper", "COPP", "ore cop", "tree sap" and "ingredient_tree" all hit.
   Across ALL tabs (Catalog.categories(), each product once, tab order then the tab's own order; only usable products, like a tab).
 - RESULTS VIEW: the sub line reads 'Search: <text>   -   N products in all tabs' (<text> cut to 20 characters + "..." so the longest
   40-character search fits the header label; the field keeps the full text); no tab is highlighted; the grid + pager page through
   the results ("Page 1 of 2   -   60 results"; nothing found: 'No matches - try fewer letters or Clear'). Clear (or an
   empty Enter / Search, or clicking a tab) goes back to the normal view: the tab you were on, on the grid page you left.
 - Selecting a result and trading it is the 0.1.5 detail view unchanged (Buy 1 / Buy <stack> / Sell ... / custom amount / Sell inventory).
 - No price / order / economy / Trader / Catalog / Market change; nothing saved (the search lives on the open page only).
Only BzPage changes (plus the version text); every other block is asserted byte-identical below.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.5.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.6.py")
tsrc = os.path.join(ROOT, "SkyyBazaar", "test_skyybazaar_0.1.5.py")
tdst = os.path.join(ROOT, "SkyyBazaar", "test_skyybazaar_0.1.6.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
assert 'VERSION = "0.1.5"' in s and "sacks:fn:" in s and "SkyyBzFind" not in s, "the source must be the generated 0.1.5 script"
REG0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# everything outside the page section stays 0.1.5's byte for byte (checked at the end)
KEEP = [block("# ================= BzUtil =================", "# ================= BzPage (0.1.3"),
        block("def check_assets(products, spread):", "# ================= javassist ="),
        block("fac.addInterface(pool.get(\"java.util.function.Function\"))", "# ================= plugin ="),
        block("# ================= 0.1.3: ACCESS AUDIT", "jar = os.path.join(HERE, \"SkyyBazaar-%s.jar\" % VERSION)")]

# ================================================================================================================ docstring + version
rep('''"""SkyyBazaar 0.1.5 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.5.py            -> SkyyBazaar/SkyyBazaar-0.1.5.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.5 is GENERATED from build_skyybazaar_0.1.4.py by tools/bazaar_0_1_5_patch.py - edit the patch, not this file; 0.1.4 came
       from 0.1.3 by tools/bazaar_0_1_4_patch.py, 0.1.3 from 0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)
''', '''"""SkyyBazaar 0.1.6 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.6.py            -> SkyyBazaar/SkyyBazaar-0.1.6.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.6 is GENERATED from build_skyybazaar_0.1.5.py by tools/bazaar_0_1_6_patch.py - edit the patch, not this file; 0.1.5 came
       from 0.1.4 by tools/bazaar_0_1_5_patch.py, 0.1.4 from 0.1.3, 0.1.3 from 0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older
       script is kept as it was)

0.1.6 (2026-10-09) - A SEARCH BAR (Skyy 2026-10-09: "bizzar needs a search bar too"; details in the tools/bazaar_0_1_6_patch.py docstring):
 - a search row under the purse line: the kit's vanilla search field (magnifier, clear x, placeholder) + Search + Clear. Enter or Search
   filters EVERY tab's products by display name or item id (case-insensitive, parts of words, every typed word must match); the results
   page with the normal grid / pager and a 'Search: <text>' line; Clear, an empty search or a tab click goes back to the tab you were on.
 - only BzPage changes: no price / trade / saved-data change.
''')
rep('VERSION = "0.1.5"', 'VERSION = "0.1.6"')

# ================================================================================================================ page layout
rep('''BZ_ACT_W, BZ_ACT_GAP = 190, 10
''', '''BZ_ACT_W, BZ_ACT_GAP = 190, 10
# 0.1.6: the search row (the kit's vanilla search field, 30 high like @DefaultDropdownBoxStyle SearchInputStyle, centred in a button-high row)
BZ_FIND_TOP, BZ_FIND_W, BZ_FIND_BW = 4, 420, 150
''')
rep('''BZ_PARTS = [BZ_HEAD_H, 2 * BZ_TABS_M + SUI.BTN_H,''', '''BZ_PARTS = [BZ_HEAD_H, BZ_FIND_TOP + SUI.BTN_H, 2 * BZ_TABS_M + SUI.BTN_H,''')
rep('''BZM["TABROW"] = SUI.group("SkyyBzTabs", "Left", h=SUI.BTN_H, anchor={"top": BZ_TABS_M, "bottom": BZ_TABS_M})
''', '''# 0.1.6: the search row. search_field is gated UNVERIFIED in the kit, but Skyy saw its probe page (11) work on 2026-09-30
# (docs/log/2026-09.md "PROBE RESULTS: 19 work - ... search field"); skyyui.PROBED was never filled in -> trial=True here and
# assert_proven(allow=("search-field",)) below. Enter (Validating) / Search apply the text, Clear goes back (no live typing).
BZM["FINDROW"] = SUI.group("SkyyBzFindRow", "Left", h=SUI.BTN_H, anchor={"top": BZ_FIND_TOP})
BZ_FIND_HINT_W = BZ_IW - BZ_FIND_W - 2 * (10 + BZ_FIND_BW) - 14
BZ_FIND = [SUI.search_field("SkyyBzFindBox", "SkyyBzFind", w=BZ_FIND_W, placeholder="Search every tab - name or item id", max_length=40,
                            trial=True, anchor={"top": (SUI.BTN_H - SUI.SEARCH_H) // 2}),
           SUI.button("SkyyBzFindGo", "Search", "secondary", w=BZ_FIND_BW, anchor={"left": 10}),
           SUI.button("SkyyBzFindClr", "Clear", "secondary", w=BZ_FIND_BW, sound="cancel", anchor={"left": 10}),
           SUI.label("SkyyBzFindHint", "Enter or Search looks in every tab", "caption", w=BZ_FIND_HINT_W, h=SUI.BTN_H, anchor={"left": 14})]
assert BZ_FIND_HINT_W >= 200, BZ_FIND_HINT_W
BZM["TABROW"] = SUI.group("SkyyBzTabs", "Left", h=SUI.BTN_H, anchor={"top": BZ_TABS_M, "bottom": BZ_TABS_M})
''')
rep('''    ap.append(("SkyyBzHead", BZM["PURSE"]))
    ap.append(("SkyyBz", BZM["TABROW"]))''', '''    ap.append(("SkyyBzHead", BZM["PURSE"]))
    ap.append(("SkyyBz", BZM["FINDROW"]))
    for mk in BZ_FIND:
        ap.append(("SkyyBzFindRow", mk))
    ap.append(("SkyyBz", BZM["TABROW"]))''')
rep('''    SUI.assert_proven(_ap)
    assert SUI.used_height(_ap, "SkyyBz") == BZ_SH.inner_h,''', '''    SUI.assert_proven(_ap, allow=("search-field",), what="bazaar page (0.1.6 search field: probe page 11 seen by Skyy 2026-09-30)")
    assert SUI.used_width(_ap, "SkyyBzFindRow") == BZ_IW, ("search row", SUI.used_width(_ap, "SkyyBzFindRow"), BZ_IW)
    assert SUI.used_height(_ap, "SkyyBz") == BZ_SH.inner_h,''')
rep('''BZ_PAGER = SUI.pager("SkyyBz", "SkyyBzPg", BZ_IW, prev_on=SUI.J("this.pageNo > 0"), next_on=SUI.J("this.pageNo < pages - 1"))''',
    '''# 0.1.6 fix (review): the caption label is 340 wide (kit default 260) so "No matches - try fewer letters or Clear" (280 px) and
# "Page 999 of 999   -   9999 products" fit between Prev / Next (measured at the end of the layout)
BZ_PG_CAP_W = 340
BZ_PAGER = SUI.pager("SkyyBz", "SkyyBzPg", BZ_IW, prev_on=SUI.J("this.pageNo > 0"), next_on=SUI.J("this.pageNo < pages - 1"),
                     caption_w=BZ_PG_CAP_W)''')
rep('''    "TABROW": SUI.java_append("SkyyBz", BZM["TABROW"]),''', '''    "FIND": "\\n".join([SUI.java_append("SkyyBz", BZM["FINDROW"])] + [SUI.java_append("SkyyBzFindRow", mk) for mk in BZ_FIND]),
    "TABROW": SUI.java_append("SkyyBz", BZM["TABROW"]),''')
rep('''print("page: %d x %d plain window,''', '''assert BZ_H <= SUI.MAX_PAGE_H, ("0.1.6 page height", BZ_H)
# 0.1.6 fix (review): the runtime header / pager texts measured at their worst case against their labels (the kit only checks static text)
_WC = max((chr(c) for c in range(32, 127)), key=lambda c: SUI.text_width(c, 16))
BZ_TXT_WORST = {
    "header (20 widest characters + ...)": (SUI.text_width("Search: " + _WC * 20 + "...   -   9999 products in all tabs", 16), BZ_IW - 350),
    "pager no matches": (SUI.text_width("No matches - try fewer letters or Clear", 16), BZ_PG_CAP_W),
    "pager results": (SUI.text_width("Page 999 of 999   -   9999 results", 16), BZ_PG_CAP_W),
    "pager products": (SUI.text_width("Page 999 of 999   -   9999 products", 16), BZ_PG_CAP_W),
    "pager empty tab": (SUI.text_width("No products in this tab", 16), BZ_PG_CAP_W)}
for _k, (_tw, _lw) in BZ_TXT_WORST.items():
    assert _tw <= _lw, ("0.1.6 text wider than its label", _k, _tw, _lw)
assert 2 * 150 + 2 * 12 + BZ_PG_CAP_W <= BZ_IW, ("pager row", BZ_PG_CAP_W, BZ_IW)
print("0.1.6 text widths (px / label): " + ", ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in BZ_TXT_WORST.items()))
print("page: %d x %d plain window,''')

# ================================================================================================================ page fields
rep('''page.addField(CtField.make("public int pageNo;", page))
''', '''page.addField(CtField.make("public int pageNo;", page))
# 0.1.6 search: query = the applied search ("" = the normal tab view), findDraft = the field text (every binding carries it; put back on
# every rebuild), catPage = the tab's grid page when the search started (Clear goes back to it)
page.addField(CtField.make("public String query;", page))
page.addField(CtField.make("public String findDraft;", page))
page.addField(CtField.make("public int catPage;", page))
''')
rep('''  this.pageNo = 0;
  @PKG@.Product p = @PKG@.Catalog.get(sel);''', '''  this.pageNo = 0;
  this.query = "";
  this.findDraft = "";
  this.catPage = 0;
  @PKG@.Product p = @PKG@.Catalog.get(sel);''')
rep('''  {EVD} d = {EVD}.of("a", a);
  if (amt) d = d.append("@BzAmount", "#SkyyBzAmt.Value");
  return d;
}}""", page))''', '''  {EVD} d = {EVD}.of("a", a);
  if (amt) d = d.append("@BzAmount", "#SkyyBzAmt.Value");
  // 0.1.6: the search field is on every page state - every binding carries its text (kept as the draft; only find applies it)
  d = d.append("@BzFind", "#SkyyBzFind.Value");
  return d;
}}""", page))
# 0.1.6 search helpers (static: the harness calls them directly). findNorm: trimmed, inner whitespace runs -> one space, at most 40 chars.
page.addMethod(CtNewMethod.make(r"""
public static String findNorm(String q) {
  if (q == null) return "";
  StringBuilder sb = new StringBuilder();
  boolean sp = false;
  for (int i = 0; i < q.length(); i++) {
    char c = q.charAt(i);
    if (Character.isWhitespace(c) || Character.isISOControl(c)) { sp = sb.length() > 0; continue; }
    if (sp) { if (sb.length() >= 40) break; sb.append(' '); sp = false; }
    if (sb.length() >= 40) break;
    sb.append(c);
  }
  return sb.toString().trim();
}""", page))
# the lower-case words of a normalized search ("" -> none)
page.addMethod(CtNewMethod.make(r"""
public static String[] findWords(String q) {
  String n = findNorm(q).toLowerCase(java.util.Locale.ROOT);
  if (n.length() == 0) return new String[0];
  java.util.ArrayList out = new java.util.ArrayList();
  int i = 0;
  while (i < n.length()) {
    int j = n.indexOf(' ', i);
    if (j < 0) j = n.length();
    if (j > i) out.add(n.substring(i, j));
    i = j + 1;
  }
  String[] w = new String[out.size()];
  for (int k = 0; k < w.length; k++) w[k] = (String) out.get(k);
  return w;
}""", page))
# true when EVERY word is part of the display name or the item id (the id also with '_' as spaces); case-insensitive
page.addMethod(CtNewMethod.make(jt(r"""
public static boolean findMatch(@PKG@.Product p, String[] w) {
  if (p == null || w == null || w.length == 0) return false;
  String id = p.id == null ? "" : p.id;
  String hay = ((p.name == null ? "" : p.name) + " " + id + " " + id.replace('_', ' ')).toLowerCase(java.util.Locale.ROOT);
  for (int i = 0; i < w.length; i++) if (hay.indexOf(w[i]) < 0) return false;
  return true;
}"""), page))
# every usable product of every tab that matches, each once: tab order, then the tab's own order
page.addMethod(CtNewMethod.make(jt(r"""
public static java.util.ArrayList findAll(String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] w = findWords(q);
  if (w.length == 0) return out;
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayList cats = @PKG@.Catalog.categories();
  for (int c = 0; c < cats.size(); c++) {
    java.util.ArrayList raw = @PKG@.Catalog.inCat((String) cats.get(c));
    for (int i = 0; i < raw.size(); i++) {
      @PKG@.Product p = (@PKG@.Product) raw.get(i);
      if (p == null || seen.contains(p.id) || !findMatch(p, w)) continue;
      seen.add(p.id);
      if (@PKG@.Catalog.usable(p.id)) out.add(p);
    }
  }
  return out;
}"""), page))''')

# ================================================================================================================ render
rep('''  java.util.ArrayList list = new java.util.ArrayList();
  java.util.ArrayList raw = this.cat == null ? new java.util.ArrayList() : @PKG@.Catalog.inCat(this.cat);
  for (int i = 0; i < raw.size(); i++) { @PKG@.Product q = (@PKG@.Product) raw.get(i); if (@PKG@.Catalog.usable(q.id)) list.add(q); }
  int total = list.size();''', '''  java.util.ArrayList list = new java.util.ArrayList();
  // 0.1.6: a search lists the matches of EVERY tab instead of the open tab
  boolean searching = this.query != null && this.query.length() > 0;
  if (searching) list = findAll(this.query);
  else {
    java.util.ArrayList raw = this.cat == null ? new java.util.ArrayList() : @PKG@.Catalog.inCat(this.cat);
    for (int i = 0; i < raw.size(); i++) { @PKG@.Product q = (@PKG@.Product) raw.get(i); if (@PKG@.Catalog.usable(q.id)) list.add(q); }
  }
  int total = list.size();''')
rep('''  if (hidC > 0) sub = hidC + " more tabs do not fit the page (" + @MAXT@ + " tabs) - tell an admin";
@SHELL@
@HEAD@
  b.set("#SkyyBzSub.Text", sub);
  b.set("#SkyyBzPurse.Text", purse);''', '''  if (hidC > 0) sub = hidC + " more tabs do not fit the page (" + @MAXT@ + " tabs) - tell an admin";
  // 0.1.6 fix: the header shows at most 20 characters of the search (the field keeps the full text) so a 40-character search fits
  String qs = this.query == null ? "" : this.query;
  if (qs.length() > 20) qs = qs.substring(0, 20) + "...";
  if (searching) sub = "Search: " + qs + "   -   " + total + (total == 1 ? " product" : " products") + " in all tabs";
@SHELL@
@HEAD@
  b.set("#SkyyBzSub.Text", sub);
  b.set("#SkyyBzPurse.Text", purse);
@FIND@
  String fd = this.findDraft == null ? "" : this.findDraft;
  if (fd.length() > 0) b.set("#SkyyBzFind.Value", fd);
  ev.addEventBinding(@BT@.Validating, "#SkyyBzFind", evd("find", amtOn), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyBzFindGo", evd("find", amtOn));
  ev.addEventBinding(@BT@.Activating, "#SkyyBzFindClr", evd("fclear", amtOn));''')
rep('''    boolean ton = c.equals(this.cat);''', '''    boolean ton = !searching && c.equals(this.cat);''')
rep('''  b.set("#SkyyBzPgPage.Text", total <= 0 ? "No products in this tab" : ("Page " + (this.pageNo + 1) + " of " + pages + "   -   " + total + " products"));''',
    '''  String none = searching ? "No matches - try fewer letters or Clear" : "No products in this tab";
  b.set("#SkyyBzPgPage.Text", total <= 0 ? none : ("Page " + (this.pageNo + 1) + " of " + pages + "   -   " + total + (searching ? (total == 1 ? " result" : " results") : " products")));''')

# ================================================================================================================ clicks
rep('''      this.amount = v;
    }}
''', '''      this.amount = v;
    }}
    // 0.1.6: every binding carries the search field text - keep it as the draft (only Enter / Search apply it)
    if (data.indexOf("\\\\"@BzFind\\\\"") >= 0) this.findDraft = findNorm({PKG}.BzUtil.jsonStr(data, "@BzFind"));
''')
rep('''    if (a.equals("close")) {{ close(); return; }}
''', '''    if (a.equals("close")) {{ close(); return; }}
    // 0.1.6 search: find applies the draft (empty = the normal view; the same text again keeps the results page - a double Enter / click);
    // fclear (or an empty find, or a tab) goes back to the tab and grid page the search started from
    if (a.equals("find")) {{
      String q = this.findDraft == null ? "" : this.findDraft;
      boolean was = this.query != null && this.query.length() > 0;
      if (q.length() == 0) {{ if (was) this.pageNo = this.catPage; this.query = ""; }}
      else if (!q.equals(this.query)) {{ if (!was) this.catPage = this.pageNo; this.query = q; this.pageNo = 0; }}
      this.info = "";
      rebuild();
      return;
    }}
    if (a.equals("fclear")) {{
      if (this.query != null && this.query.length() > 0) this.pageNo = this.catPage;
      this.query = "";
      this.findDraft = "";
      this.info = "";
      rebuild();
      return;
    }}
''')
rep('''      if (a.equals("tab:" + i)) {{ this.cat = this.tabs[i]; this.pageNo = 0; this.info = ""; rebuild(); return; }}''',
    '''      if (a.equals("tab:" + i)) {{ this.cat = this.tabs[i]; this.pageNo = 0; this.query = ""; this.findDraft = ""; this.info = ""; rebuild(); return; }}''')

# ================================================================================================================ checks on the result
for kb in KEEP:
    assert kb in s, "a block that must stay 0.1.5's changed: %s" % kb[:90]
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert "@@" not in s and s.count('VERSION = "0.1.6"') == 1
for _a, _b in (("public static String findNorm(", "public static String[] findWords("), ("public static String[] findWords(", "public static boolean findMatch("),
               ("public static boolean findMatch(", "public static java.util.ArrayList findAll("),
               ("public static java.util.ArrayList findAll(", "public void render("), ("public {EVD} evd(", "public void render(")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:60], _b[:60])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, len(s.split(LF)), "lines")

# ================================================================================================================ the harness
t, TNL = load(tsrc)
assert 'VERSION, OLD_VERSION, SACKS_VERSION = "0.1.5", "0.1.4", "0.7.13"' in t


def trep(old, new, count=1):
    global t
    n = t.count(old)
    assert n == count, "harness anchor count %d != %d: %s" % (n, count, old[:120])
    t = t.replace(old, new)


T_HEAD = '''"""Bare-JVM harness for SkyyBazaar 0.1.6 (the search bar - tools/bazaar_0_1_6_patch.py), GENERATED from test_skyybazaar_0.1.5.py by that
patch: every 0.1.5 check is carried forward (now on the 0.1.6 jar with the SET-pinned SkyySacks 0.7.14), section B compares 0.1.5 -> 0.1.6
(only BzPage + the version text change), and section Q (new) EXECUTES every search path:
  Q  findNorm / findWords (trim, whitespace runs, 40 chars, lower case); findMatch (case, parts of words, the item id and its words, every
     word must match); findAll over ALL tabs (each product once, tab order, unusable ids left out, no match = empty); render in the results
     view (sub line 'Search: <text>   -   N products in all tabs', no tab highlighted, the grid = the results, pager 'N results', no-result
     text, the field value put back, markup checked); event wiring (Validating #SkyyBzFind -> find, #SkyyBzFindGo -> find, #SkyyBzFindClr ->
     fclear, EVERY binding carries @BzFind); clicks through handleDataEvent: find (draft applied, page 1), the same find again (results page
     kept), Next / Prev on the results, a cell click selects a result and the detail view trades it (buy1), a draft typed then another
     click (kept, not applied), fclear / empty find / a tab click -> the normal view on the tab + grid page the search started from; no
     file written by any search click.
The 0.1.5 docstring follows.

'''
trep('"""Bare-JVM harness for SkyyBazaar 0.1.5 (sell', T_HEAD + 'Bare-JVM harness for SkyyBazaar 0.1.5 (sell')
trep('VERSION, OLD_VERSION, SACKS_VERSION = "0.1.5", "0.1.4", "0.7.13"', 'VERSION, OLD_VERSION, SACKS_VERSION = "0.1.6", "0.1.5", "0.7.14"')
trep('MARK = ".skyybazaar-0.1.5-harness"', 'MARK = ".skyybazaar-0.1.6-harness"')
trep('os.path.join(SCRATCH_ROOT, "bazaar015", "bz-run")', 'os.path.join(SCRATCH_ROOT, "bazaar016", "bz-run")')
trep('open(os.path.join(SCRATCH, MARK), "w").write("SkyyBazaar 0.1.5 harness scratch\\n")',
     'open(os.path.join(SCRATCH, MARK), "w").write("SkyyBazaar 0.1.6 harness scratch\\n")')
# B: 0.1.5 -> 0.1.6 = only BzPage beyond the version text; the whole Catalog (seed tables included) identical
_b0 = t.index("    # ---------------- B. class compare 0.1.4 -> 0.1.5")
_b1 = t.index("    # ---------------- X. engine-access audit")
t = t[:_b0] + '''    # ---------------- B. class compare 0.1.5 -> 0.1.6 (generated by tools/bazaar_0_1_6_patch.py)
    za, zb = zipfile.ZipFile(OLD), zipfile.ZipFile(JAR)
    ca = dict((n.split("/")[-1][:-6], za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n.split("/")[-1][:-6], zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    check(sorted(cb) == sorted(ca), "B: the same classes as 0.1.5: %s / %s" % (sorted(set(cb) - set(ca)), sorted(set(ca) - set(cb))))
    ob, nb = OLD_VERSION.encode(), VERSION.encode()
    same = sorted(c for c in ca if ca[c] == cb.get(c))
    vers = sorted(c for c in ca if c in cb and ca[c] != cb[c] and ca[c].replace(ob, nb) == cb[c])
    other = sorted(c for c in ca if c in cb and ca[c] != cb[c] and c not in vers)
    check(other == ["BzPage"], "B: changed beyond the version text: exactly BzPage (%s)" % other)
    check(set(vers) <= {"SkyyBazaarPlugin", "CfgRows", "CfgFn", "CfgFile", "CfgPub"}, "B: version-text-only classes: %s" % vers)
    for c in ("Coins", "Market", "Inv", "Product", "BzUtil", "Catalog", "Trader", "TradeResult", "Bags", "BzCmd", "BzPageFactory",
              "BzAdminCmd", "BzAdmPriceCmd", "BzAdmPriceShowCmd", "BzAdmReloadCmd", "BzAdmResetCmd", "BzAdmInfoCmd", "BzTick", "BzCfg"):
        check(c in same, "B: %s byte-identical %s -> %s" % (c, OLD_VERSION, VERSION))
    Cat = JClass(PKG + "Catalog")
    man = json.loads(zb.read("manifest.json"))
    check(man["Version"] == VERSION and man["Main"] == "com.skyy.bazaar.SkyyBazaarPlugin", "B: manifest %s" % man["Version"])
    print("B. class compare %s -> %s: %d identical, %d version-text only (%s), changed: BzPage only"
          % (OLD_VERSION, VERSION, len(same), len(vers), ", ".join(vers)))

''' + t[_b1:]
# Q: the search, inserted before L (uses the K section's render / player / page helpers)
T_Q = r'''    # ---------------- Q. 0.1.6 search (every new code path EXECUTED)
    Prod = Jc("Product")
    check(str(Page.findNorm("  Tree \t  SAP  ")) == "Tree SAP" and str(Page.findNorm(None)) == "" and str(Page.findNorm("   ")) == ""
          and len(str(Page.findNorm("x" * 60))) == 40 and str(Page.findNorm("a\nb")) == "a b", "Q: findNorm trims, joins whitespace, 40 chars")
    check([str(w) for w in Page.findWords("  Copper   ORE ")] == ["copper", "ore"] and len(Page.findWords("")) == 0, "Q: findWords lower-case words")
    pc_ = Prod("Ore_Copper", "Mining", 5.0, "Copper Ore")
    W = lambda q: Page.findWords(q)
    for q, exp in (("copper", True), ("COPPER", True), ("CoPp", True), ("ore cop", True), ("ore_copper", True), ("ore copper", True),
                   ("per o", True), ("iron", False), ("copper iron", False), ("", False), ("mining", False)):
        check(bool(Page.findMatch(pc_, W(q))) == exp, "Q: findMatch Copper Ore / %r -> %s" % (q, exp))
    check(not Page.findMatch(None, W("x")) and not Page.findMatch(pc_, None), "Q: findMatch null-safe")
    reset_state()
    dq = os.path.join(SCRATCH, "search")
    os.makedirs(dq)
    start(dq)
    cats = [str(c) for c in Cat.categories()]
    allp = []
    for c in cats:
        for p_ in Cat.inCat(c):
            if str(p_.id) not in allp:
                allp.append(str(p_.id))

    def expect(q):
        ws = [w for w in str(Page.findNorm(q)).lower().split(" ") if w]
        out = []
        for pid in allp:
            p_ = Cat.get(pid)
            hay = (str(p_.name) + " " + pid + " " + pid.replace("_", " ")).lower()
            if ws and all(w in hay for w in ws):
                out.append(pid)
        return out
    for q in ("copper", "ORE", "sap", "tree sap", "ingredient_tree", "log", "seed", "zzzz", "", "  ", "ore cop", "Ore_"):
        got = [str(p_.id) for p_ in Page.findAll(q)]
        check(got == expect(q) and len(set(got)) == len(got), "Q: findAll(%r) = %d products across all tabs (expected %d)" % (q, len(got), len(expect(q))))
    ores = [str(p_.id) for p_ in Page.findAll("ore")]
    tabs_hit = sorted(set(str(Cat.tabsOf(Cat.get(i)).get(0)) for i in ores))
    check(len(ores) >= 8 and "Ore_Copper" in ores and "Ore_Iron" in ores, "Q: 'ore' finds %d products (tabs %s)" % (len(ores), tabs_hit))
    multi = [str(p_.id) for p_ in Page.findAll("e")]
    check(len(multi) > 52, "Q: 'e' matches more than one grid page (%d)" % len(multi))
    check(len(Page.findAll("zzzz")) == 0 and len(Page.findAll("")) == 0, "Q: no match / empty -> no results")
    # an unknown (unusable) product is never listed
    real_cu = KMap.REAL.remove("Ore_Copper")
    KMap.KNOWN.remove("Ore_Copper")
    Cat.WARNED.add("Ore_Copper")
    check(not Cat.usable("Ore_Copper") and "Ore_Copper" not in [str(p_.id) for p_ in Page.findAll("copper")], "Q: an unusable product is left out")
    KMap.KNOWN.add("Ore_Copper")
    if real_cu is not None:
        KMap.REAL.put("Ore_Copper", real_cu)
    Cat.WARNED.remove("Ore_Copper")
    check(Cat.usable("Ore_Copper"), "Q: Copper Ore usable again")
    # the page: normal view, then the results view
    set_purse(100000)
    p = player(storage=[("Ore_Copper", 3)])
    setp(p)
    before = files(dq)
    pg = Page(pref(), None)
    ap, sets, binds = render(pg, p)
    for _p, mk in ap:
        try:
            SUI.check_markup(mk, root=(_p is None))
            OKS[0] += 1
        except Exception as e:
            FAILS.append("Q page markup %s: %s" % (mk[:60], e))
    fr = " ".join(mk for _p, mk in ap if "SkyyBzFind" in mk)
    check("#SkyyBzFindBox" in fr and "#SkyyBzFind " in fr and "SearchIcon.png" in fr and "ClearInputIcon.png" in fr
          and 'PlaceholderText: "Search every tab - name or item id"' in fr and "MaxLength: 40" in fr and "#SkyyBzFindGo" in fr
          and "#SkyyBzFindClr" in fr, "Q: the search row (kit search field, placeholder, Search, Clear) is on the normal page")
    bl = [(t_, s_, d_) for t_, s_, d_ in binds]
    bm = dict((s_, (t_, d_)) for t_, s_, d_ in bl)
    check(bm.get("#SkyyBzFind", ("", ""))[0] == "Validating" and '"a":"find"' in bm["#SkyyBzFind"][1]
          and bm.get("#SkyyBzFindGo", ("", ""))[0] == "Activating" and '"a":"find"' in bm["#SkyyBzFindGo"][1]
          and '"a":"fclear"' in bm.get("#SkyyBzFindClr", ("", ""))[1], "Q: wiring: Enter + Search -> find, Clear -> fclear")
    check(all('"@BzFind":"#SkyyBzFind.Value"' in d_ for _t, _s, d_ in bl) and len(bl) > 50, "Q: every binding (%d) carries @BzFind" % len(bl))
    tab0 = str(pg.cat)
    pg.pageNo = 0
    # a draft typed, then another click (Next): kept, not applied
    pg.handleDataEvent(None, TSTORE, '{"a":"next","@BzFind":"  Copper  "}')
    check(str(pg.findDraft) == "Copper" and str(pg.query) == "" and pg.pageNo in (0, 1), "Q: a typed draft is kept but not applied by another click")
    pg.pageNo = 1 if len([x for x in Cat.inCat(tab0)]) > 52 else 0
    keep_page = pg.pageNo
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"e"}')
    check(str(pg.query) == "e" and pg.pageNo == 0 and pg.catPage == keep_page, "Q: find applies 'e', page 1, remembers grid page %d" % keep_page)
    ap, sets, binds = render(pg, p)
    sd = dict(sets)
    n_e = len(multi)
    check(sd.get("#SkyyBzSub.Text", "") == "Search: e   -   %d products in all tabs" % n_e, "Q: header: %s" % sd.get("#SkyyBzSub.Text"))
    pages_e = (n_e + 51) // 52
    check(sd.get("#SkyyBzPgPage.Text", "") == "Page 1 of %d   -   %d results" % (pages_e, n_e), "Q: pager: %s" % sd.get("#SkyyBzPgPage.Text"))
    check(sd.get("#SkyyBzFind.Value", "") == "e", "Q: the field shows the search text after the rebuild")
    check(pg.cells is not None and [str(c) for c in pg.cells[:min(52, n_e)]] == multi[:52], "Q: the grid lists the first 52 results in order")
    # the same find again keeps the page; Next / Prev page through the results
    pg.handleDataEvent(None, TSTORE, '{"a":"next","@BzFind":"e"}')
    check(pg.pageNo == 1, "Q: Next on the results -> page 2")
    ap, sets, binds = render(pg, p)
    check(dict(sets).get("#SkyyBzPgPage.Text", "").startswith("Page 2 of %d" % pages_e) and [str(c) for c in pg.cells if c is not None] == multi[52:104],
          "Q: page 2 of the results lists results 53-%d" % min(104, n_e))
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"e"}')
    check(pg.pageNo == 1 and str(pg.query) == "e", "Q: the same search again (double Enter / click) keeps the results page")
    pg.handleDataEvent(None, TSTORE, '{"a":"prev","@BzFind":"e"}')
    check(pg.pageNo == 0, "Q: Prev on the results -> page 1")
    # a narrower search: Copper Ore, select it, trade from the results view
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"COPPER ore"}')
    ap, sets, binds = render(pg, p)
    cu = expect("COPPER ore")
    check(str(pg.query) == "COPPER ore" and [str(c) for c in pg.cells if c is not None] == cu and "Ore_Copper" in cu,
          "Q: 'COPPER ore' -> %s" % cu)
    ci = [str(c) for c in pg.cells].index("Ore_Copper")
    pg.handleDataEvent(None, TSTORE, '{"a":"cell:%d","@BzFind":"COPPER ore"}' % ci)
    check(str(pg.sel) == "Ore_Copper" and str(pg.query) == "COPPER ore", "Q: a result cell selects it and keeps the search")
    c0 = purse()
    qb = int(Mkt.quote("Ore_Copper", 1, True))
    pg.handleDataEvent(None, TSTORE, '{"a":"buy1","@BzAmount":"","@BzFind":"COPPER ore"}')
    check(held(p, "Ore_Copper") == 4 and c0 - purse() == qb and str(pg.query) == "COPPER ore", "Q: Buy 1 from the results view: %s" % pg.info)
    ap, sets, binds = render(pg, p)
    check(dict(sets).get("#SkyyBzDName.Text", "") == "Copper Ore" and dict(sets).get("#SkyyBzSub.Text", "").startswith("Search: COPPER ore"),
          "Q: detail + results view together")
    # no results
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"zzqq"}')
    ap, sets, binds = render(pg, p)
    sd = dict(sets)
    check(sd.get("#SkyyBzPgPage.Text", "") == 'No matches - try fewer letters or Clear' and all(c is None for c in pg.cells)
          and sd.get("#SkyyBzSub.Text", "") == "Search: zzqq   -   0 products in all tabs", "Q: no results: %s" % sd.get("#SkyyBzPgPage.Text"))
    # 0.1.6 fix (review): the runtime texts fit their labels - the pager caption is 340 wide, a long search is cut to 20 characters in the header
    _lw = lambda ident: int(re.search(r"Label #" + ident + r" \{ Anchor: \([^)]*Width: (\d+)", " ".join(mk for _p, mk in ap)).group(1))
    check(_lw("SkyyBzPgPage") == 340 and SUI.text_width(sd.get("#SkyyBzPgPage.Text", ""), 16) <= 340,
          "Q fix: the no-match caption fits the 340 px pager label (%d px)" % SUI.text_width(sd.get("#SkyyBzPgPage.Text", ""), 16))
    long_q = "ore " * 9 + "oreo"
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"%s"}' % long_q)
    ap, sets, binds = render(pg, p)
    sd = dict(sets)
    hd = sd.get("#SkyyBzSub.Text", "")
    check(len(long_q) == 40 and str(pg.query) == long_q and hd.startswith("Search: ore ore ore ore ore ...   -   ")
          and SUI.text_width(hd, 16) <= _lw("SkyyBzSub") and sd.get("#SkyyBzFind.Value", "") == long_q,
          "Q fix: a 40-character search is cut to 20 + ... in the header (%s, %d px of %d) and kept whole in the field" % (hd, SUI.text_width(hd, 16), _lw("SkyyBzSub")))
    wsub = "Search: " + "W" * 20 + "...   -   9999 products in all tabs"
    check(SUI.text_width(wsub, 16) <= _lw("SkyyBzSub") and SUI.text_width("Page 999 of 999   -   9999 products", 16) <= 340,
          "Q fix: worst-case header (%d px) and pager (%d px) texts fit" % (SUI.text_width(wsub, 16), SUI.text_width("Page 999 of 999   -   9999 products", 16)))
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"zzqq"}')
    ap, sets, binds = render(pg, p)
    # Clear -> the tab + grid page the search started from
    pg.handleDataEvent(None, TSTORE, '{"a":"fclear","@BzFind":"zzqq"}')
    check(str(pg.query) == "" and str(pg.findDraft) == "" and pg.pageNo == keep_page and str(pg.cat) == tab0,
          "Q: Clear -> normal view, tab %s, grid page %d" % (tab0, keep_page))
    ap, sets, binds = render(pg, p)
    check(not dict(sets).get("#SkyyBzSub.Text", "").startswith("Search:") and "#SkyyBzFind.Value" not in dict(sets)
          and dict(sets).get("#SkyyBzPgPage.Text", "").endswith(" products"), "Q: the normal view after Clear")
    # an empty find = Clear; a tab click ends a search
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"log"}')
    check(str(pg.query) == "log", "Q: find 'log'")
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"   "}')
    check(str(pg.query) == "" and pg.pageNo == keep_page, "Q: an empty search -> the normal view")
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"log"}')
    nt = len(pg.tabs)
    pg.handleDataEvent(None, TSTORE, '{"a":"tab:%d","@BzFind":"log"}' % (nt - 1))
    check(str(pg.query) == "" and str(pg.findDraft) == "" and str(pg.cat) == str(pg.tabs[nt - 1]) and pg.pageNo == 0, "Q: a tab click ends the search")
    # without the @BzFind key (an old client payload) nothing breaks and the draft stays
    pg.findDraft = "abc"
    pg.handleDataEvent(None, TSTORE, '{"a":"prev"}')
    check(str(pg.findDraft) == "abc", "Q: a payload without @BzFind keeps the draft")
    # the results view: tab buttons all Secondary (no tab open)
    pg.handleDataEvent(None, TSTORE, '{"a":"find","@BzFind":"ore"}')
    ap, sets, binds = render(pg, p)
    tabsr = [mk for _p, mk in ap if _p == "SkyyBzTabs" and "#SkyyBzTab" in mk]
    pg.handleDataEvent(None, TSTORE, '{"a":"fclear"}')
    ap2, sets2, _b2 = render(pg, p)
    tabsn = [mk for _p, mk in ap2 if _p == "SkyyBzTabs" and "#SkyyBzTab" in mk]
    check(len(tabsr) == len(tabsn) == nt and sum(1 for i in range(nt) if tabsr[i] != tabsn[i]) == 1,
          "Q: in the results view no tab is drawn open (exactly the open tab differs from the normal view)")
    stop()
    after = files(dq)
    ch = churn(before, after)
    ch = [c for c in ch if c != "trades.log" and c != "market.properties"]
    check(not ch, "Q: no search click writes a file (only the Buy 1 trade's log / market): %s" % ch)
    print("Q. search: findNorm / findWords / findMatch (case, parts, item id words, every word), findAll over all %d tabs (%d for 'ore', %d for 'e'), "
          "the results view (header, pager, field value, grid), wiring (Validating / Search / Clear, @BzFind on every binding), clicks "
          "(draft kept, find, same find keeps the page, Next / Prev, select + Buy 1, no results, Clear / empty / tab -> back)" % (len(cats), len(ores), n_e))

'''
trep("    # ---------------- L. money loops on the 0.1.5 runtime table", T_Q + "    # ---------------- L. money loops on the 0.1.6 runtime table")
compile(t, tdst, "exec")
open(tdst, "w", encoding="utf8", newline="").write(t.replace(LF, TNL))
print("wrote", tdst, len(t.split(LF)), "lines")
