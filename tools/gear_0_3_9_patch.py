"""Derive SkyyGear/build_skyygear_0.3.9.py from the LIVE 0.3.8 (build_skyygear_0.3.8.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_8_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_9_patch.py      then      python SkyyGear/build_skyygear_0.3.9.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.9.py

0.3.9 (2026-10-15, lean round "gear039" = fixes from Skyy's live test + the /smithing cleanup Skyy asked for the same afternoon):
1. THE DISCONNECT ("Failed to parse or resolve document for Custom UI AppendInline command. Selector: #SkyyGPFig"): the /smithing piece
   page (a set card clicked) appended two labels with "VerticalAlignment: Top" into #SkyyGPFig - the client only knows Start / Center / End
   (Assets.zip .ui files: Center / End only; tools/skyyui.py allows Start / Center / End), so the whole inline document failed to parse and
   the player was kicked. EVERY set card's piece page did it since 0.2.23 (the page had never been opened in game). The Upgrade preview's
   "rolls new lines" label (#SkyyGColRoll, 0.2.22) had the same value. All three are "Start" now.
2. VALIDATE BEFORE SEND: GearUi.ap / st / on wrap every appendInline / b.set(".Text") / addEventBinding of the /smithing Craft tab and the
   Anvil / Identify page. GearUi.bad(doc) checks a document the way the client parses it (balanced { } ( ) outside quotes, every { opens
   'Type' or 'Type #Id', ids letters + digits, no @ / $ / % / ';;', HorizontalAlignment / VerticalAlignment in Start / Center / End,
   LayoutMode one of the vanilla modes, ItemId a loaded item, no negative Width / Height). A bad part is NOT sent: one gear WARN (once per
   part), its element ids are remembered for that build, and every later append into / set of / event on them is skipped too (a missing
   parent would disconnect as well). A good page sends exactly what 0.3.8 sent.
3. THE CRAFT TAB = THE LEVELLING GATHERING GEAR ONLY (Skyy 2026-10-15: "id only have the gathering gear that levels up craft and upgrade
   there. id leave the combat gear and weapons in the normal crafter"; "craft shows tools and multi tools, when they have their own tab up
   top"; "we need a mining armor tab, a farming armor tab, and a foraging armor tab"): the left list is MINING ARMOR, FORAGING ARMOR (bark),
   FARMING ARMOR (crop), FISHING ARMOR (angler, 0.3.6 - so it is not orphaned). Combat armor, weapons, tools and multitools are no longer
   on the Craft tab (their bench recipes, rolls, Smithing XP and the bench-accessory rule are untouched); the class filter is gone (it only
   filtered combat gear). GearSmith.cat: a Foraging / Farming / Fishing piece is its own category (5 / 6 / 7; before 0.3.9 it fell into
   Combat armor - the "Farming P1 Set" card a Mage saw there); Mining stays 1.
4. FIRST TIER ONLY (Skyy: "all the gathering armor is made, then upgrades like the tools from there right?"): a gathering piece that a tier-up
   ladder of the Anvil leads to (GearUp.tab = upgrade + lifelong + garmor ladders) is NOT crafted: its set shows as a "Tier up on the Anvil"
   card (also the Foraging / Farming / Fishing tiers that have no recipe at all), its piece rows say from which piece, the materials and the
   skill level of the step, with a "To the Anvil" button. GearSmith.craft refuses it, and so does CraftRecipeEvent$Pre (GearCraftPreSys:
   bench, pocket crafting and SkyySacks 0.8.6 /craft, which fires the event) - Creative still crafts, like the lifelong tools. A piece no
   ladder leads to stays craftable (Mithril / Onyxium mining sets: garmor.ladders stops at Adamantite). Combat armor is never touched.
   Pieces players already own keep working (only crafting is refused). Clearing garmor.ladders in Server Setup makes them craftable again.
5. THE IDENTIFY TAB (Skyy: "id separate identify and anvil." + "allow users to select the ones they want to identify, and do them all at
   once"): /smithing tabs Craft | Anvil | Identify | Tools | Multitool (Identify while part.anvil + identify.command are on). The Anvil lists
   only identified gear (Reforge / Level up / Upgrade / Sigils; no re-identify strip); the Identify tab lists only unidentified gear and
   mystery bags (Identify, Re-identify of an item that stays on it, Identify all, the reveal cards). Each row has a tick box; Select all /
   Clear; "Identify picked" identifies exactly the ticked items in one go (GearIdent.allInC - each paid on its own, stops when coins run
   out, the same checks as Identify all), then the reveal page with one card each; a ticked item that left the inventory is skipped with a
   line. Ticks live on the page. /identify opens the Identify tab; /reforge and /upgrade keep opening the Anvil. Every action's logic and
   cost is unchanged (stale clicks of the other tab are dropped).
REVIEW FIXES: F1 the veto is the Server Setup row gear.gatherAnvilOnly (default ON, live; OFF = benches / /craft craft every tier as in 0.3.8,
the Craft tab still shows first tiers + tier-up cards); F2 part.upgrade off = nothing is refused and every tier is a normal card; F3 Back from
the reveal page after Identify returns to the Identify tab; F4 the Identify tab lists, under the unidentified gear, the items from a bag that
still have re-identify uses (with the cost) - picking one shows the re-identify strip as before; F5 no "click Show all" line.
SAVED DATA: one new config row (gear.gatherAnvilOnly, absent = ON; no one-time update), no item key, no file. ROLLBACK 0.3.9 -> 0.3.8 is item-safe (the piece page then disconnects again).
"""
import os
import ast
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.8.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.9.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.8"' in s and "GENERATED by tools/gear_0_3_8_patch.py" in s and "0.3.9" not in s[:400], "not the generated 0.3.8 script"
assert "GearUi.ap(" not in s and "anIdM" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def between(a, b):
    """the exact text from anchor a (inclusive) to the next anchor b (exclusive)"""
    assert s.count(a) == 1, "anchor a count %d: %s" % (s.count(a), a[:120])
    i = s.index(a)
    j = s.index(b, i)
    return s[i:j]


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.8":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.8" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.8 - build script (javassist via jpype). GENERATED by tools/gear_0_3_8_patch.py from the LIVE 0.3.7 (itself GENERATED by
tools/gear_0_3_7_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.8.py -> SkyyGear/SkyyGear-0.3.8.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.8.py
''', '''"""SkyyGear 0.3.9 - build script (javassist via jpype). GENERATED by tools/gear_0_3_9_patch.py from the LIVE 0.3.8 (itself GENERATED by
tools/gear_0_3_8_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.9.py -> SkyyGear/SkyyGear-0.3.9.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.9.py

0.3.9 = THE /smithing PIECE PAGE DISCONNECT FIX + VALIDATE BEFORE SEND + THE CRAFT TAB CLEANUP + THE IDENTIFY TAB (notes:
tools/gear_0_3_9_patch.py): the vertical alignment "Top" (not a client value) in the piece page / Upgrade preview is "Start"; every inline
document of the Craft tab and the Anvil / Identify page is checked before it is sent (a bad part is skipped + logged, never a kick); the
Craft tab lists only Mining / Foraging / Farming / Fishing armor, first tier craftable, higher tiers = Anvil tier-up cards (bench / pocket /
/craft refuse them too); /smithing gets an Identify tab (tick bags, Identify picked) and the Anvil lists identified gear only.

--- 0.3.8 notes ---
''')
rep('VERSION = "0.3.8"\n', 'VERSION = "0.3.9"\n')

# ================================================================================================================ 1. the root cause
rep("VerticalAlignment: Top", "VerticalAlignment: Start", count=3)

# ================================================================================================================ 2. validate before send (GearUi)
before('M(gui, "public static boolean tex() { return @PKG@.GearCfg.UI_FRAMES; }")', r'''# 0.3.9 VALIDATE BEFORE SEND (tools/gear_0_3_9_patch.py item 2): a document the client cannot parse disconnects the player, so the Craft tab
# and the Anvil / Identify page send every part through ap / st / on: a bad part is skipped (one WARN), and so is everything inside it
F(gui, "public static final java.util.Map BADB = java.util.Collections.synchronizedMap(new java.util.WeakHashMap());")          # builder -> HashSet skipped ids
F(gui, "public static final long[] UIN = new long[2];")          # 0 parts checked, 1 parts skipped
F(gui, 'public static final String[] ALIGNS = new String[] { "Start", "Center", "End" };')
F(gui, 'public static final String[] LAYOUTS = new String[] { "Top", "Left", "Middle", "Center", "TopScrolling", "Full", "CenterMiddle", "MiddleCenter", "Right", "Bottom", "LeftWrap", "LeftCenterWrap" };')
M(gui, r"""
public static String selId(String sel) {
  if (sel == null) return null;
  String x = sel.trim();
  if (x.startsWith("#")) x = x.substring(1);
  int k = 0;
  while (k < x.length() && Character.isLetterOrDigit(x.charAt(k))) k++;
  return x.substring(0, k);
}""")
# the element a { at i opens: { type, id or null }; null = the { opens no element (the client's parse error)
M(gui, r"""
public static String[] elemAt(String d, int i) {
  int j = i - 1;
  while (j >= 0 && Character.isWhitespace(d.charAt(j))) j--;
  int e = j + 1;
  while (j >= 0 && (Character.isLetterOrDigit(d.charAt(j)) || d.charAt(j) == '_')) j--;
  String w = d.substring(j + 1, e);
  if (w.length() == 0) return null;
  String id = null;
  if (j >= 0 && d.charAt(j) == '#') {
    id = w;
    j--;
    while (j >= 0 && Character.isWhitespace(d.charAt(j))) j--;
    e = j + 1;
    while (j >= 0 && Character.isLetter(d.charAt(j))) j--;
    w = d.substring(j + 1, e);
    if (w.length() == 0) return null;
  }
  if (!Character.isUpperCase(w.charAt(0))) return null;
  for (int k = 0; k < w.length(); k++) if (!Character.isLetter(w.charAt(k))) return null;
  int p = j;
  while (p >= 0 && Character.isWhitespace(d.charAt(p))) p--;
  if (p >= 0 && d.charAt(p) != '{' && d.charAt(p) != '}' && d.charAt(p) != ';') return null;
  return new String[] { w, id };
}""")
M(gui, r"""
public static String enumBad(String d, String key, String[] ok) {
  int i = d.indexOf(key);
  while (i >= 0) {
    int j = i + key.length();
    int k = j;
    while (k < d.length() && Character.isLetter(d.charAt(k))) k++;
    String v = d.substring(j, k);
    boolean f = false;
    for (int m = 0; m < ok.length; m++) if (ok[m].equals(v)) f = true;
    if (!f) return key.trim() + " " + v + " is not a value the client knows";
    i = d.indexOf(key, k);
  }
  return null;
}""")
M(gui, r"""
public static String itemBad(String d) {
  String key = "ItemId: \"";
  int i = d.indexOf(key);
  while (i >= 0) {
    int j = i + key.length();
    int k = d.indexOf('"', j);
    if (k < 0) return "an unterminated ItemId";
    String id = d.substring(j, k);
    if (id.length() == 0 || @PKG@.Gear.item(id) == null) return "ItemId " + id + " is no loaded item";
    i = d.indexOf(key, k + 1);
  }
  return null;
}""")
# null = the client can parse it; else why not
M(gui, r"""
public static String bad(String d) {
  if (d == null || d.trim().length() == 0) return "an empty document";
  int n = d.length();
  char[] st = new char[n + 1];
  int sp = 0;
  boolean q = false;
  for (int i = 0; i < n; i++) {
    char ch = d.charAt(i);
    if (q) {
      if (ch == '\\') { i++; continue; }
      if (ch == '"') q = false;
      continue;
    }
    if (ch == '"') { q = true; continue; }
    if (ch == '@' || ch == '$' || ch == '%') return "a document variable / placeholder (" + ch + ")";
    if (ch == ';' && i + 1 < n && d.charAt(i + 1) == ';') return "';;'";
    if (ch == '{') {
      String[] el = elemAt(d, i);
      if (el == null) return "a { that opens no element";
      if (el[1] != null && (el[1].length() == 0 || !Character.isLetter(el[1].charAt(0)) || el[1].indexOf('_') >= 0)) return "the element id #" + el[1] + " (letters and digits only)";
    }
    if (ch == '{' || ch == '(') { st[sp] = ch; sp++; continue; }
    if (ch == '}' || ch == ')') {
      if (sp == 0) return "a bracket closes before it opens";
      sp--;
      char o = st[sp];
      if ((ch == '}' && o != '{') || (ch == ')' && o != '(')) return "brackets cross";
    }
  }
  if (q) return "an unterminated quote";
  if (sp != 0) return "unbalanced brackets";
  String r = enumBad(d, "HorizontalAlignment: ", ALIGNS);
  if (r == null) r = enumBad(d, "VerticalAlignment: ", ALIGNS);
  if (r == null) r = enumBad(d, "LayoutMode: ", LAYOUTS);
  if (r == null && (d.indexOf("Width: -") >= 0 || d.indexOf("Height: -") >= 0)) r = "a negative Width / Height";
  if (r == null) r = itemBad(d);
  return r;
}""")
M(gui, r"""
public static void idsOf(String d, java.util.HashSet out) {
  boolean q = false;
  for (int i = 0; d != null && i < d.length(); i++) {
    char ch = d.charAt(i);
    if (q) { if (ch == '\\') i++; else if (ch == '"') q = false; continue; }
    if (ch == '"') { q = true; continue; }
    if (ch != '{') continue;
    String[] el = elemAt(d, i);
    if (el != null && el[1] != null) out.add(el[1]);
  }
}""")
M(gui, r"""
public static boolean skipped(@UCB@ b, String sel) {
  java.util.HashSet bs = (java.util.HashSet) BADB.get(b);
  if (bs == null) return false;
  String p = selId(sel);
  return p != null && bs.contains(p);
}""")
M(gui, r"""
public static void ap(@UCB@ b, String sel, String d) {
  UIN[0] = UIN[0] + 1L;
  boolean inBad = skipped(b, sel);
  String why = inBad ? null : bad(d);
  if (!inBad && why == null) { b.appendInline(sel, d); return; }
  java.util.HashSet bs = (java.util.HashSet) BADB.get(b);
  if (bs == null) { bs = new java.util.HashSet(); BADB.put(b, bs); }
  idsOf(d, bs);
  UIN[1] = UIN[1] + 1L;
  if (why != null) @PKG@.Gear.warnOnce("uidoc:" + sel + ":" + why, "a page part was NOT sent (it would disconnect the player): " + why + " - into " + sel + ": " + (d == null ? "null" : (d.length() > 300 ? d.substring(0, 300) : d)));
}""")
M(gui, r"""
public static void st(@UCB@ b, String sel, String v) {
  if (skipped(b, sel)) return;
  b.set(sel, v);
}""")
M(gui, r"""
public static void on(@UCB@ b, @UEB@ ev, @BT@ t, String sel, @EVD@ data) {
  if (skipped(b, sel)) return;
  ev.addEventBinding(t, sel, data);
}""")
M(gui, 'public static String uiText() { return "page parts checked " + UIN[0] + ", skipped " + UIN[1]; }')
''')

# ================================================================================================================ 5a. the tab row: + Identify (5)
rep('''  boolean lt = @PKG@.GearCfg.LL_ON;          // 0.3.0: the Tools tab (/toolpoints)
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0) + (lt ? 1 : 0);''', '''  boolean lt = @PKG@.GearCfg.LL_ON;          // 0.3.0: the Tools tab (/toolpoints)
  boolean it = @PKG@.GearCfg.ANVIL_ON && @PKG@.GearCfg.IDENTIFY_CMD;          // 0.3.9: the Identify tab (/identify)
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0) + (lt ? 1 : 0) + (it ? 1 : 0);''')
rep('''  int[] order = new int[] { 3, 0, 4, 1, 2 };
  for (int j = 0; j < order.length; j++) {
    int m = order[j];
    if (m == 3 && !cr) continue;''', '''  int[] order = new int[] { 3, 0, 5, 4, 1, 2 };
  for (int j = 0; j < order.length; j++) {
    int m = order[j];
    if (m == 5 && !it) continue;
    if (m == 3 && !cr) continue;''')
rep('''    String nm = m == 3 ? "Craft" : (m == 0 ? (@PKG@.GearCfg.ANVIL_ON ? "Anvil" : "Reforge") : (m == 1 ? "Upgrade" : (m == 4 ? "Tools" : "Multitool")));''',
    '''    String nm = m == 3 ? "Craft" : (m == 0 ? (@PKG@.GearCfg.ANVIL_ON ? "Anvil" : "Reforge") : (m == 1 ? "Upgrade" : (m == 4 ? "Tools" : (m == 5 ? "Identify" : "Multitool"))));''')

# ================================================================================================================ 4a. the Pre veto (a stub now, its body once GearSmith exists)
after('''M(gll, "public static boolean noCraft(String id) { return @PKG@.GearCfg.LL_ON && @PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0; }")
''', '''# 0.3.9: a higher-tier gathering armor piece is tiered up on the Anvil, never crafted (null = may craft; the body is set after GearSmith)
M(gll, "public static String craftVeto(String id) { return null; }")
''')
rep('''        @PKG@.GearLog.line("CRAFT-BLOCK-LIFELONG " + (pr0 == null ? "?" : pr0.getUsername() + " " + pr0.getUuid()) + " " + id0 + " recipe " + rc0.getId());
        return;
      }
    }
''', '''        @PKG@.GearLog.line("CRAFT-BLOCK-LIFELONG " + (pr0 == null ? "?" : pr0.getUsername() + " " + pr0.getUuid()) + " " + id0 + " recipe " + rc0.getId());
        return;
      }
    }
    // 0.3.9 (Skyy: "all the gathering armor is made, then upgrades like the tools"): a gathering piece an Anvil ladder leads to is not crafted
    String tv0 = id0 == null ? null : @PKG@.GearLL.craftVeto(id0);
    if (tv0 != null) {
      @REF@ r1 = chunk.getReferenceTo(idx);
      @PR@ pr1 = r1 == null ? null : (@PR@) st.getComponent(r1, @PR@.getComponentType());
      @PLA@ p1 = r1 == null ? null : (@PLA@) st.getComponent(r1, @PLA@.getComponentType());
      if (p1 == null || p1.getGameMode() != @GM@.Creative) {
        e.setCancelled(true);
        if (pr1 != null) pr1.sendMessage(@MSG@.raw("[Gear] " + @PKG@.Gear.itemName(id0) + " - " + tv0 + " Gathering armor is crafted once at its first tier.").color(@PKG@.GearDefs.C_BAD));
        @PKG@.GearLog.line("CRAFT-BLOCK-TIERUP " + (pr1 == null ? "?" : pr1.getUsername() + " " + pr1.getUuid()) + " " + id0 + " recipe " + rc0.getId());
        return;
      }
    }
''')

# ================================================================================================================ 4b. the row gear.gatherAnvilOnly (review F1)
after('''    ("garmor.ladders.fishing", "Fishing armor tier-up costs", "garmor", "text", GA2_LAD_DEF[2], "0", "2000", "", "", "live,danger",
     "Angler set tiers on the Anvil, like garmor.ladders: A>B(Id*2), ladders joined by commas.", "field:GearCfg.GA_LAD2;check=GearUp.checkLadders"),
''', '''    # 0.3.9 FIRST TIER ONLY (Skyy "all the gathering armor is made, then upgrades like the tools"): the bench / pocket / /craft veto
    ("gear.gatherAnvilOnly", "Higher gathering armor tiers: Anvil only", "garmor", "bool", "true", "", "", "", "", "live,danger",
     "On = armor tiers the Anvil reaches are not crafted (benches, /craft). Off = every tier crafts.", "field:GearCfg.GARM_ANVIL"),
''')
rep('''           "lifelong.perkSteady", "rebirth.stats"}''', '''           "lifelong.perkSteady", "rebirth.stats",
           # 0.3.9: the gathering armor craft veto (item supply = economy)
           "gear.gatherAnvilOnly"}''')
after('''assert all(32 <= ord(_c) < 127 for _c in G36_HEAD) and "=" not in G36_HEAD
''', '''G39_HEAD = "# ---- gathering armor: higher tiers only on the Anvil (SkyyGear 0.3.9) ----"
G39_ROWK = ["gear.gatherAnvilOnly"]
assert all(32 <= ord(_c) < 127 for _c in G39_HEAD) and "=" not in G39_HEAD
''')
rep('''    L += ["", G36_HEAD]         # 0.3.6: the new rows (no one-time update adds them; absent = the default)
    for k in G36_ROWK:
        scal(k)
''', '''    L += ["", G36_HEAD]         # 0.3.6: the new rows (no one-time update adds them; absent = the default)
    for k in G36_ROWK:
        scal(k)
    L += ["", G39_HEAD]         # 0.3.9: the new row (no one-time update adds it; absent = the default ON)
    for k in G39_ROWK:
        scal(k)
''')
rep('''              ("LL_PSTEADY", "double", "10.0"), ("RB_STATS", "boolean", "true"), ("SND_ON", "boolean", "true")]''',
    '''              ("LL_PSTEADY", "double", "10.0"), ("RB_STATS", "boolean", "true"), ("SND_ON", "boolean", "true"),
              ("GARM_ANVIL", "boolean", "true")]          # 0.3.9 gear.gatherAnvilOnly ''')
rep('''  SND_ON = pbool(p, "sounds.enabled", true);
''', '''  SND_ON = pbool(p, "sounds.enabled", true);
  GARM_ANVIL = pbool(p, "gear.gatherAnvilOnly", true);          // 0.3.9 (review F1)
''')

# ================================================================================================================ 3 + 4. GearSmith: categories, tier-up groups
rep('''F(gsm, 'public static final String[] CAT_NAME = new String[] { "Combat armor", "Gathering armor", "Weapons", "Tools", "Multitools" };')''',
    '''F(gsm, 'public static final String[] CAT_NAME = new String[] { "Combat armor", "Mining armor", "Weapons", "Tools", "Multitools", "Foraging armor", "Farming armor", "Fishing armor" };')
# 0.3.9: the categories the Craft tab shows, in order (Skyy: only the gathering gear that levels up; 5-7 = Foraging / Farming / Fishing)
F(gsm, "public static final int[] SHOW = new int[] { 1, 5, 6, 7 };")
M(gsm, "public static boolean isGath(int c) { return c == 1 || c == 5 || c == 6 || c == 7; }")
M(gsm, "public static boolean isSet(int c) { return c == 0 || isGath(c); }")
M(gsm, r"""
public static boolean shown(int c) {
  for (int i = 0; i < SHOW.length; i++) if (SHOW[i] == c) return true;
  return false;
}""")''')
rep('''  if (s == 2) return (@PKG@.GearMine.isPiece(id) || @PKG@.GearMine.setFor(id) != null) ? 1 : 0;''',
    '''  if (s == 2) {
    if (@PKG@.GearMine.isPiece(id) || @PKG@.GearMine.setFor(id) != null) return 1;
    int gi = @PKG@.GearGArm.index(id);          // 0.3.9: Foraging / Farming / Fishing pieces are their own categories (before: Combat armor)
    if (gi >= 0) return @PKG@.GearGArm.famOn(@PKG@.GearGArm.IFAM[gi]) ? 5 + @PKG@.GearGArm.IFAM[gi] : -1;
    return 0;
  }''')
rep('''  if (c == 0 || c == 1) return s + " Set";
  return plural(s);''', '''  if (isSet(c)) return s + " Set";
  return plural(s);''')
before('''# the player switches (SkyyMenu settings; memory only without it)''', r'''# 0.3.9 FIRST TIER ONLY: the piece an Anvil ladder step turns into id (null = no step leads there)
M(gsm, r"""
public static String prevOf(String id) {
  if (id == null) return null;
  Object[] tb = @PKG@.GearUp.tab();
  String[] f = (String[]) tb[0];
  String[] t = (String[]) tb[1];
  for (int i = 0; i < t.length && i < f.length; i++) if (id.equals(t[i])) return f[i];
  return null;
}""")
# the Craft tab's view: null = a craftable card; else why not (a gathering piece some Anvil ladder step leads to while upgrading is on;
# combat gear never)
M(gsm, r"""
public static String tierUpOnly(String id) {
  if (id == null || !@PKG@.GearCfg.UP_ON || !isGath(cat(id))) return null;
  String p = prevOf(id);
  if (p == null) return null;
  return "Not crafted: tier up a " + @PKG@.Gear.itemName(p) + " on the Anvil (it keeps its rarity).";
}""")
# THE VETO (benches, pocket crafting, /craft, the Craft tab's button): tierUpOnly while gear.gatherAnvilOnly is on (review F1 / F2: off or
# part.upgrade off = every tier is crafted at a bench as in 0.3.8)
M(gsm, "public static String anvilOnly(String id) { return @PKG@.GearCfg.GARM_ANVIL ? tierUpOnly(id) : null; }")
# the skill a gathering piece levels with (its tier-up needs the band start of the new tier)
M(gsm, r"""
public static String gathSkill(String id) {
  if (@PKG@.GearMine.index(id) >= 0) return "Mining";
  String g = @PKG@.GearGArm.gateOf(id);
  return g == null ? "its skill" : g;
}""")
# the pieces of a gathering category that exist without a recipe (the higher tiers): Mining = the metal pieces, 5-7 = one 0.3.6 family
M(gsm, r"""
public static String[] gathIds(int c) {
  if (c == 1) return @PKG@.GearCfg.GM_ON ? @PKG@.GearMine.IDS : new String[0];
  int f = c - 5;
  if (f < 0 || f > 2 || !@PKG@.GearGArm.famOn(f)) return new String[0];
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.GearGArm.IDS.length; i++) if (@PKG@.GearGArm.IFAM[i] == f) l.add(@PKG@.GearGArm.IDS[i]);
  String[] a = new String[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
  return a;
}""")
''')
# the tier-up helpers (GearUp is defined before GearSmith) + the gathering ids of a category, in front of groups()
_G_OLD = between('''# THE CARDS of category c: ArrayList of Object[] { String key, String[] outs, String[] rids, Integer lo, Integer hi, Integer cat }''',
                 '''# a document to preview an item at the level the player would make it (no lines)''')
_G_NEW = r'''# what the step up to id costs: "1 Enchanted Iron Ingot - needs Mining 18"
M(gsm, r"""
public static String tierNeed(String id) {
  String p = prevOf(id);
  if (p == null) return "";
  Object[] c = null;
  try { c = @PKG@.GearUp.cost(p, id); } catch (Throwable t) { c = null; }
  StringBuilder sb = new StringBuilder();
  if (c != null) {
    String[] ids = (String[]) c[0];
    int[] q = (int[]) c[1];
    for (int i = 0; i < ids.length && i < q.length; i++) {
      if (sb.length() > 0) sb.append(", ");
      sb.append(q[i]).append(" ").append(matName(ids[i]));
    }
  }
  if (sb.length() == 0) sb.append("no materials set up");
  return sb.toString() + " - needs " + gathSkill(id) + " " + @PKG@.GearLevel.band(id)[0];
}""")
# THE CARDS of category c: ArrayList of Object[] { String key, String[] outs, String[] rids, Integer lo, Integer hi, Integer cat, Boolean tierUp }
# 0.3.9: an anvil-only piece has rid null; a set of only such pieces is a tier-up card (tierUp TRUE); the higher gathering tiers without a
# recipe are added from their ids (only pieces a ladder leads to, only loaded items)
M(gsm, r"""
public static java.util.ArrayList groups(java.util.UUID u, int c, boolean all) {
  java.util.ArrayList rs = recipes();
  java.util.LinkedHashMap g = new java.util.LinkedHashMap();
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < rs.size(); i++) {
    Object[] r = (Object[]) rs.get(i);
    String out = (String) r[1];
    if (cat(out) != c || !shows(u, out, all)) continue;
    String k = isSet(c) ? setKey(out) : famKey(out);
    java.util.ArrayList l = (java.util.ArrayList) g.get(k);
    if (l == null) { l = new java.util.ArrayList(); g.put(k, l); }
    l.add(r);
    seen.add(out);
  }
  if (isGath(c)) {
    String[] gi = gathIds(c);
    for (int i = 0; i < gi.length; i++) {
      if (seen.contains(gi[i]) || cat(gi[i]) != c || @PKG@.Gear.item(gi[i]) == null || tierUpOnly(gi[i]) == null) continue;
      String k = setKey(gi[i]);
      java.util.ArrayList l = (java.util.ArrayList) g.get(k);
      if (l == null) { l = new java.util.ArrayList(); g.put(k, l); }
      l.add(new Object[] { null, gi[i], null });
      seen.add(gi[i]);
    }
  }
  java.util.ArrayList res = new java.util.ArrayList();
  java.util.Iterator it = g.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] a = ((java.util.ArrayList) e.getValue()).toArray();
    int[] key = new int[a.length];
    String[] tie = new String[a.length];
    int lo = 9999;
    int hi = 0;
    for (int i = 0; i < a.length; i++) {
      String out = (String) ((Object[]) a[i])[1];
      int[] b = @PKG@.GearLevel.band(out);
      if (b[0] < lo) lo = b[0];
      if (b[1] > hi) hi = b[1];
      int si = slotIx(out);
      key[i] = isSet(c) ? (si < 0 ? 4 : si) : b[0];
      tie[i] = out;
    }
    sortBy(a, key, tie);
    String[] outs = new String[a.length];
    String[] rids = new String[a.length];
    boolean tu = true;
    for (int i = 0; i < a.length; i++) {
      outs[i] = (String) ((Object[]) a[i])[1];
      rids[i] = (String) ((Object[]) a[i])[0];
      if (rids[i] != null && tierUpOnly(outs[i]) != null) rids[i] = null;
      if (rids[i] != null) tu = false;
    }
    res.add(new Object[] { e.getKey(), outs, rids, Integer.valueOf(lo), Integer.valueOf(hi), Integer.valueOf(c), Boolean.valueOf(tu) });
  }
  Object[] ga = res.toArray();
  int[] gk = new int[ga.length];
  String[] gt = new String[ga.length];
  for (int i = 0; i < ga.length; i++) { gk[i] = ((Integer) ((Object[]) ga[i])[3]).intValue(); gt[i] = (String) ((Object[]) ga[i])[0]; }
  sortBy(ga, gk, gt);
  java.util.ArrayList sorted = new java.util.ArrayList();
  for (int i = 0; i < ga.length; i++) sorted.add(ga[i]);
  return sorted;
}""")
M(gsm, "public static boolean tierUp(Object[] g) { return g != null && g.length > 6 && Boolean.TRUE.equals(g[6]); }")
'''
rep(_G_OLD, _G_NEW)
rep('''  try {
    for (int i = 0; i < outs.length; i++) {
      String sid = @PKG@.GearMine.setFor(outs[i]);
      if (sid == null) continue;''', '''  try {
    for (int i = 0; i < outs.length; i++) {
      int gai = @PKG@.GearGArm.index(outs[i]);          // 0.3.9: a Foraging / Farming / Fishing set's full-set bonus
      if (gai >= 0) return "Full set (all 4): " + @PKG@.GearGArm.bonusText(@PKG@.GearGArm.IFAM[gai], @PKG@.GearGArm.ITIER[gai]);
      String sid = @PKG@.GearMine.setFor(outs[i]);
      if (sid == null) continue;''')
rep('''public static String typeWord(String[] outs, int c) {
  if (c == 1) return "Mining";''', '''public static String typeWord(String[] outs, int c) {
  if (c == 1) return "Mining";
  if (c >= 5 && c <= 7) return @PKG@.GearGArm.FSK[c - 5];          // 0.3.9''')
rep('''  String[] rids = (String[]) g[2];
  int n = outs.length;
  if (al == null) return new Object[] { Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(n), "Browse only - needs SkyySacks 0.7.17", @PKG@.GearDefs.C_GRAY };''',
    '''  String[] rids = (String[]) g[2];
  int n = outs.length;
  if (tierUp(g)) return new Object[] { Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(n), "Tier up on the Anvil", @PKG@.GearDefs.C_LABEL };          // 0.3.9
  if (al == null) return new Object[] { Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(n), "Browse only - needs SkyySacks 0.7.17", @PKG@.GearDefs.C_GRAY };''')
rep('''  String out = (String) row[1];
  @CRR@ rc = (@CRR@) row[2];
  java.util.function.Function pay = @PKG@.Gear.fn("sacks:fn:craftPay");''', '''  String out = (String) row[1];
  @CRR@ rc = (@CRR@) row[2];
  String avo = anvilOnly(out);          // 0.3.9: a higher-tier gathering piece is tiered up on the Anvil
  if (avo != null) return r0(avo);
  java.util.function.Function pay = @PKG@.Gear.fn("sacks:fn:craftPay");''')

# ================================================================================================================ 3. SmithPage: the left list, cards, piece page
_L_OLD = between('''  boolean mt = @PKG@.GearUi.multiTab();
  for (int c = 0; c < @PKG@.GearSmith.CAT_NAME.length; c++) {
    if (c == 4 && !mt) continue;''', '''  b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 10); }");
  boolean rq = @PKG@.GearSmith.requip();''')
rep(_L_OLD, '''  for (int j = 0; j < @PKG@.GearSmith.SHOW.length; j++) {          // 0.3.9: Mining / Foraging / Farming / Fishing armor only, no class filter
    int c = @PKG@.GearSmith.SHOW[j];
    b.appendInline("#SkyyGLeft", "TextButton #SkyyGCat" + c + " { Anchor: (Height: 40); Text: \\"" + @PKG@.GearSmith.CAT_NAME[c] + "\\"; " + @PKG@.GearUi.btn(c == this.cat ? 0 : 1) + " }");
    b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 6); }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGCat" + c, @EVD@.of("a", "cat:" + c));
  }
  b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 10); }");
  b.appendInline("#SkyyGLeft", "Label #SkyyGNote { Anchor: (Height: 110); Text: \\"\\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Start, Wrap: true); }");
  b.set("#SkyyGNote.Text", "Gathering armor is crafted once at its first tier, then tiered up on the Anvil. Combat armor and weapons: craft them at a bench.");
''')
rep('''  b.set(cid + "S.Text", "Lv " + lo + (hi > lo ? "-" + hi : "") + (tw.length() > 0 ? " - " + tw : "") + (c >= 2 ? " - " + outs.length''',
    '''  b.set(cid + "S.Text", "Lv " + lo + (hi > lo ? "-" + hi : "") + (tw.length() > 0 ? " - " + tw : "") + (!@PKG@.GearSmith.isSet(c) ? " - " + outs.length''')
rep('''+ " / " + pages + " (" + n + (this.cat <= 1 ? " sets" : " families") + ")");''', '''+ " / " + pages + " (" + n + (@PKG@.GearSmith.isSet(this.cat) ? " sets" : " families") + ")");''')
# review F5: no class filter any more - the empty-category line names the category only
rep('''    boolean any = !@PKG@.GearSmith.groups(u, this.cat, true).isEmpty();
    b.set("#SkyyGNone1.Text", any ? "Nothing here for your class - click Show all." : "Nothing in " + @PKG@.GearSmith.CAT_NAME[this.cat] + " can be crafted on this server yet.");''',
    '''    b.set("#SkyyGNone1.Text", "Nothing in " + @PKG@.GearSmith.CAT_NAME[this.cat] + " can be crafted on this server yet.");''')
# the tier-up row (a piece no recipe makes here): icon | name + band, from which piece, the step's materials + skill | To the Anvil
before('''M(spg, r"""
public void piecesArea(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv) {''', r'''# 0.3.9: one tier-up row (height 74) of a piece that is tiered up on the Anvil, never crafted here
M(spg, r"""
public void tierRow(@UCB@ b, @UEB@ ev, int i, String out, java.util.UUID u) {
  String gid = "#SkyyGPc" + i;
  b.appendInline("#SkyyGRows", "Group " + gid + " { Anchor: (Height: 74); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline(gid, @PKG@.GearUi.cell(56, out));
  b.appendInline(gid, @PKG@.GearUi.gap(8));
  b.appendInline(gid, "Group " + gid + "T { Anchor: (Width: 330); LayoutMode: Top; }");
  int[] bd = @PKG@.GearLevel.band(out);
  b.appendInline(gid + "T", "Label " + gid + "N { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set(gid + "N.Text", @PKG@.Gear.itemName(out) + "  [Lv " + bd[0] + (bd[1] > bd[0] ? "-" + bd[1] : "") + "]");
  String p = @PKG@.GearSmith.prevOf(out);
  b.appendInline(gid + "T", "Label " + gid + "U { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 13, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 9); }");
  b.set(gid + "U.Text", p == null ? "Not crafted here." : "Tier up a " + @PKG@.Gear.itemName(p) + " on the Anvil");
  b.appendInline(gid + "T", "Label " + gid + "W { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 13, TextColor: #ffffff, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 8); }");
  b.set(gid + "W.Text", @PKG@.GearSmith.tierNeed(out));
  b.appendInline(gid, @PKG@.GearUi.gap(8));
  b.appendInline(gid, "Group " + gid + "B { Anchor: (Width: 160); LayoutMode: Top; Padding: (Top: 12); }");
  b.appendInline(gid + "B", "TextButton " + gid + "Go { Anchor: (Height: 40); Text: \"To the Anvil\"; " + @PKG@.GearUi.btn(1) + " }");
  ev.addEventBinding(@BT@.Activating, gid + "Go", @EVD@.of("a", "mode:0"));
}""")
''')
rep('''  b.set("#SkyyGPRoll.Text", how + (lv >= 0 ? " and is made at your level (Lv " + lv + " here)." : ".") + " Materials: inventory first, then your bags.");''',
    '''  b.set("#SkyyGPRoll.Text", @PKG@.GearSmith.tierUp(g) ? "Higher tiers are not crafted: tier up the set below on the Anvil - it keeps its rarity, the new tier levels with your skill." : how + (lv >= 0 ? " and is made at your level (Lv " + lv + " here)." : ".") + " Materials: inventory first, then your bags.");          // 0.3.9''')
rep('''  for (int i = start; i < outs.length && i < start + per; i++) pieceRow(b, ev, i, rids[i], outs[i], u, inv);''',
    '''  for (int i = start; i < outs.length && i < start + per; i++) {
    if (rids[i] == null) tierRow(b, ev, i, outs[i], u);          // 0.3.9: tiered up on the Anvil, never crafted here
    else pieceRow(b, ev, i, rids[i], outs[i], u, inv);
  }''')
rep('''  if (c == 0 || c == 1) {          // a whole SET at once (a weapon / tool family is one tier at a time)
    b.appendInline("#SkyyGPRight", "Group #SkyyGPAll { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");''',
    '''  if (@PKG@.GearSmith.tierUp(g)) {          // 0.3.9: a tier-up set - the way to the Anvil instead of Craft every missing piece
    b.appendInline("#SkyyGPRight", "Group #SkyyGPAll { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
    b.appendInline("#SkyyGPAll", "TextButton #SkyyGBtnAnv { Anchor: (Width: 330, Height: 44); Text: \\"Open the Anvil\\"; " + @PKG@.GearUi.btn(0) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnAnv", @EVD@.of("a", "mode:0"));
  } else if (c == 0 || c == 1) {          // a whole SET at once (a weapon / tool family is one tier at a time)
    b.appendInline("#SkyyGPRight", "Group #SkyyGPAll { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");''')
rep('''  if (this.cat == 4 && !@PKG@.GearUi.multiTab()) this.cat = 0;''', '''  if (!@PKG@.GearSmith.shown(this.cat)) this.cat = 1;          // 0.3.9: only the gathering armor categories''')
rep('''  for (int c = 0; c < @PKG@.GearSmith.CAT_NAME.length && this.cards.isEmpty() && !this.picked; c++) {
    if (c == 4 && !@PKG@.GearUi.multiTab()) continue;
    java.util.ArrayList g = @PKG@.GearSmith.groups(u, c, all);''', '''  for (int j = 0; j < @PKG@.GearSmith.SHOW.length && this.cards.isEmpty() && !this.picked; j++) {
    int c = @PKG@.GearSmith.SHOW[j];
    java.util.ArrayList g = @PKG@.GearSmith.groups(u, c, all);''')
rep('''      if (cc >= 0 && cc < @PKG@.GearSmith.CAT_NAME.length && (cc != 4 || @PKG@.GearUi.multiTab())) { this.picked = true;''',
    '''      if (cc >= 0 && @PKG@.GearSmith.shown(cc)) { this.picked = true;''')
rep('''        if (gc > 1) { this.info = "-Craft every missing piece is for armor sets - craft one tier at a time."; rebuild(); return; }''',
    '''        if (!@PKG@.GearSmith.isSet(gc)) { this.info = "-Craft every missing piece is for armor sets - craft one tier at a time."; rebuild(); return; }''')

# ================================================================================================================ 5. the Anvil / Identify page
# review F3: the Identify tab flag is declared before GearIdent.backFor (which reads it); Back from the reveal page lands on that tab
before('''M(gidn, r"""
public static String backFor(Object page) {''', '''F(rpg, "public boolean anIdM;")          # 0.3.9: true = the page is on its Identify tab
F(rpg, "public int anNUn;")          # 0.3.9: the Identify tab's rows: [0, anNUn) unidentified, the rest re-identify candidates
''')
rep('''  if (page != null && page.getClass().getName().endsWith("ReforgePage")) return "reforge";''',
    '''  if (page instanceof @PKG@.ReforgePage) return ((@PKG@.ReforgePage) page).anIdM ? "identify" : "reforge";          // 0.3.9 review F3''')
rep('''           "public int anSig;", "public long anSgArm;", "public String anSgFp;"):
    F(rpg, _f)''', '''           "public int anSig;", "public long anSgArm;", "public String anSgFp;"):
    F(rpg, _f)
# 0.3.9 THE IDENTIFY TAB: true = this page is on its Identify tab; the ticked rows ("section:slot:fingerprint", page only)
F(rpg, "public java.util.HashSet anTick;")
M(rpg, r"""
public boolean anFitsMode(@IS@ it) {
  if (it == null || it.isEmpty()) return false;
  boolean un = @PKG@.GearAnvil.unid(it, @PKG@.GearAnvil.docOf(it));
  if (this.anIdM) return un || @PKG@.GearUnid.rerollable(it);
  return !un;
}""")
M(rpg, r"""
public static boolean anReidRow(int sec, @IS@ it) {
  if (sec < 0 || sec > 2 || it == null || it.isEmpty() || !@PKG@.GearUnid.rerollable(it)) return false;
  @BD@ d = @PKG@.GearUnid.rerollDoc(it);
  return @PKG@.GearUnid.rerolls(@PKG@.GearUnid.boxOf(d)) < @PKG@.GearCfg.REROLL_MAX;
}""")
# the Anvil: identified gear. The Identify tab: unidentified gear first ([0, anNUn)), then (review F4) the identified items from a bag that
# still have re-identify uses (hotbar / inventory / backpack - where re-identify works)
M(rpg, r"""
public java.util.ArrayList anRows(@INV@ inv) {
  java.util.ArrayList all = @PKG@.GearAnvil.rows(inv);
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList re = new java.util.ArrayList();
  for (int i = 0; i < all.size(); i++) {
    int[] rw = (int[]) all.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it == null || it.isEmpty()) continue;
    boolean un = @PKG@.GearAnvil.unid(it, @PKG@.GearAnvil.docOf(it));
    if (un == this.anIdM) out.add(rw);
    else if (this.anIdM && anReidRow(rw[0], it)) re.add(rw);
  }
  this.anNUn = out.size();
  for (int i = 0; i < re.size(); i++) out.add(re.get(i));
  return out;
}""")
M(rpg, r"""
public static String anKey(@INV@ inv, int[] rw) {
  @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
  if (it == null || it.isEmpty()) return null;
  return rw[0] + ":" + rw[1] + ":" + @PKG@.GearForge.fp(it);
}""")
M(rpg, r"""
public java.util.HashSet anTicks() {
  if (this.anTick == null) this.anTick = new java.util.HashSet();
  return this.anTick;
}""")''')
# GearAnvil: the Identify tab switch + the tab click on the other Smithing pages
rep('''# the best Appraisal Tool in the player's Accessory Bag: n = tier (1 = the first id), 0 = none, -1 = no acc:fn:has (SkyyAccessories off)''',
    '''# 0.3.9: the Identify tab shows while the Anvil and /identify are on; its click on another Smithing page (mode:5) -> /identify
M(gav, "public static boolean idTab() { return @PKG@.GearCfg.ANVIL_ON && @PKG@.GearCfg.IDENTIFY_CMD; }")
M(gav, r"""
public static boolean idTabGo(String data, @PR@ pr) {
  if (data == null || !"mode:5".equals(@PKG@.Gear.jsonStr(data, "a"))) return false;
  if (idTab() && pr != null) {
    try { @CMGR@.get().handleCommand(pr, "identify"); } catch (Throwable t) { @PKG@.Gear.warn("the Identify tab could not open /identify: " + t); }
  }
  return true;
}""")
# the best Appraisal Tool in the player's Accessory Bag: n = tier (1 = the first id), 0 = none, -1 = no acc:fn:has (SkyyAccessories off)''')
rep('''public boolean anPick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (!@PKG@.GearAnvil.fits(it)) return false;''', '''public boolean anPick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (!@PKG@.GearAnvil.fits(it)) return false;
  if (!anFitsMode(it)) return false;          // 0.3.9: the Anvil takes identified gear, the Identify tab unidentified gear (+ re-identify)''')
rep('''    if (it != null && !it.isEmpty()) this.info = "-" + @PKG@.Gear.itemName(it.getItemId()) + " cannot go on the anvil - pick a weapon, armor piece, tool or mystery bag from the list.";''',
    '''    if (it != null && !it.isEmpty()) this.info = "-" + @PKG@.Gear.itemName(it.getItemId()) + (this.anIdM ? " needs no identifying - pick an unidentified item or a mystery bag from the list."
        : (@PKG@.GearAnvil.fits(it) ? " is unidentified - identify it on the Identify tab first." : " cannot go on the anvil - pick a weapon, armor piece or tool from the list."));''')
# the help column: Reforge + Upgrade on the Anvil, Identify on the Identify tab
rep('''  String g = @PKG@.GearDefs.C_GRAY;
  b.appendInline("#SkyyGAnvil", @PKG@.GearAnvil.head("SkyyGHelpR"));''', '''  String g = @PKG@.GearDefs.C_GRAY;
  if (this.anIdM) { anHelpId(b, u); return; }          // 0.3.9
  b.appendInline("#SkyyGAnvil", @PKG@.GearAnvil.head("SkyyGHelpR"));''')
rep('''  b.set("#SkyyGHow3.Text", @PKG@.GearCfg.UP_ON ? "Costs the next tier's materials (inventory, then bags) - no coins." : "");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 10); }");
  b.appendInline("#SkyyGAnvil", @PKG@.GearAnvil.head("SkyyGHelpI"));
  b.set("#SkyyGHelpI.Text", "Identify");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow4 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + g + ", VerticalAlignment: Center); }");
  b.set("#SkyyGHow4.Text", "Reveals unidentified gear and mystery bags for coins.");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow5 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + (@PKG@.GearAnvil.idGateT(anTier(u)) != null ? @PKG@.GearDefs.C_GOLD : g) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGHow5.Text", @PKG@.GearAnvil.toolLineT(anTier(u)));
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 10); }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow6 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
  b.set("#SkyyGHow6.Text", "Tip: hold an item when you type /reforge, /upgrade or /identify.");
}""")''', '''  b.set("#SkyyGHow3.Text", @PKG@.GearCfg.UP_ON ? "Costs the next tier's materials (inventory, then bags) - no coins." : "");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 10); }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow6 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
  b.set("#SkyyGHow6.Text", "Tip: hold an item when you type /reforge or /upgrade. Unidentified gear: the Identify tab.");
}""")''')
before('''# nothing on the anvil: what the Anvil does (or the Revealed list after Identify all)''', '''# 0.3.9 the Identify tab's help column (the 0.2.26 Identify lines)
M(rpg, r"""
public void anHelpId(@UCB@ b, java.util.UUID u) {
  String g = @PKG@.GearDefs.C_GRAY;
  b.appendInline("#SkyyGAnvil", @PKG@.GearAnvil.head("SkyyGHelpI"));
  b.set("#SkyyGHelpI.Text", "Identify");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow4 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + g + ", VerticalAlignment: Center); }");
  b.set("#SkyyGHow4.Text", "Reveals unidentified gear and mystery bags for coins.");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow5 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + (@PKG@.GearAnvil.idGateT(anTier(u)) != null ? @PKG@.GearDefs.C_GOLD : g) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGHow5.Text", @PKG@.GearAnvil.toolLineT(anTier(u)));
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow7 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + g + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGHow7.Text", "Tick the boxes in the list, then Identify picked - or Identify all.");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 10); }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGHow6 { Anchor: (Height: 22); Text: \\"\\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
  b.set("#SkyyGHow6.Text", "Tip: hold an item when you type /identify. Reforge, level up, upgrade: the Anvil tab.");
}""")
''')
# the panel: re-identify only on the Identify tab, Sigils / Reforge / Upgrade only on the Anvil
rep('''  boolean rr = !un && (this.selSec == 0 || this.selSec == 1 || this.selSec == 2) && @PKG@.GearUnid.rerollable(sel);
  // 0.3.4: the Sigil strip while the player carries any Sigil (an identified item that is no mystery bag)
  int[] sgh = null;
  if (!un && !@PKG@.GearUnid.isBox(sel.getItemId()) && @PKG@.GearCfg.SIG_ON) sgh = @PKG@.GearSigil.carried(inv);''',
    '''  boolean rr = this.anIdM && !un && (this.selSec == 0 || this.selSec == 1 || this.selSec == 2) && @PKG@.GearUnid.rerollable(sel);          // 0.3.9: Identify tab
  // 0.3.4: the Sigil strip while the player carries any Sigil (an identified item that is no mystery bag)
  int[] sgh = null;
  if (!this.anIdM && !un && !@PKG@.GearUnid.isBox(sel.getItemId()) && @PKG@.GearCfg.SIG_ON) sgh = @PKG@.GearSigil.carried(inv);''')
rep('''  if (un) { anIdentify(b, ev, u, sel, inv, have); return; }
  anReforge(b, ev, u, sel, d, inv, have);''', '''  if (this.anIdM) {          // 0.3.9: the Identify tab identifies; an item it already revealed is worked on at the Anvil
    if (un) anIdentify(b, ev, u, sel, inv, have);
    else anNote(b, "Identified. Reforge, level it up or upgrade it on the Anvil tab.");
    return;
  }
  if (un) { anNote(b, "Unidentified - identify it on the Identify tab first."); return; }
  anReforge(b, ev, u, sel, d, inv, have);''')
before('''# the right column (562 x 656)
M(rpg, r"""
public void anPanel(''', r'''# 0.3.9: a plain note in the cards row (an item the other tab works on)
M(rpg, r"""
public void anNote(@UCB@ b, String txt) {
  b.appendInline("#SkyyGActs", "Label #SkyyGActNote { Anchor: (Width: 562); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearDefs.C_LABEL + ", HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGActNote.Text", txt);
}""")
''')
# the list: Identify all + the tick row only on the Identify tab
rep('''  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  int nUn = @PKG@.GearIdent.items(inv, un);
  if (nUn > 0) {''', '''  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  int nUn = this.anIdM ? @PKG@.GearIdent.items(inv, un) : 0;          // 0.3.9: Identify all only on the Identify tab
  if (nUn > 0) {''')
rep('''    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnAll", @EVD@.of("a", "idall"));
  }
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead {''', '''    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnAll", @EVD@.of("a", "idall"));
    // 0.3.9 Skyy "allow users to select the ones they want to identify, and do them all at once": Select all / Clear + Identify picked
    java.util.HashSet tk = anTicks();
    int kq = 0;
    int kn = 0;
    long kc = 0L;
    for (int q = 0; q < this.anNUn && q < this.rows.size(); q++) {
      int[] rq0 = (int[]) this.rows.get(q);
      String kk = anKey(inv, rq0);
      if (kk == null || !tk.contains(kk)) continue;
      @IS@ iq = @PKG@.GearStamp.at(inv, rq0[0], rq0[1]);
      kn++;
      kq = kq + iq.getQuantity();
      kc = kc + @PKG@.GearIdent.costOf(iq) * (long) iq.getQuantity();
    }
    boolean allOn = kn > 0 && kn == this.anNUn;
    b.appendInline("#SkyyGListBox", "Group #SkyyGIdSel { Anchor: (Height: 52); LayoutMode: Left; Padding: (Bottom: 8); }");
    b.appendInline("#SkyyGIdSel", "TextButton #SkyyGBtnTickAll { Anchor: (Width: 130, Height: 44); Text: \\"" + (allOn ? "Clear" : "Select all") + "\\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGIdSel", "Group { Anchor: (Width: 8); }");
    b.appendInline("#SkyyGIdSel", "TextButton #SkyyGBtnIdSel { Anchor: (Width: 200, Height: 44); Text: \\"Identify picked\\"; " + @PKG@.GearUi.btn(gate != null || kn == 0 ? 3 : 0) + " }");
    b.appendInline("#SkyyGIdSel", "Group { Anchor: (Width: 8); }");
    b.appendInline("#SkyyGIdSel", "Label #SkyyGSelCost { Anchor: (Width: 124, Height: 44); Text: \\"\\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + (kn > 0 ? @PKG@.GearDefs.C_GOLD : @PKG@.GearDefs.C_LABEL) + ", VerticalAlignment: Center, Wrap: true, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); }");
    b.set("#SkyyGSelCost.Text", kn == 0 ? "Tick items below" : kq + " picked - " + @PKG@.Gear.fmt(kc) + " coins");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnTickAll", @EVD@.of("a", "tickall"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnIdSel", @EVD@.of("a", "idsel"));
  }
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead {''')
rep('''  b.set("#SkyyGHeadItem.Text", "Your gear (" + this.rows.size() + ")");
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  // fix round: ui.frames off''',
    '''  b.set("#SkyyGHeadItem.Text", (this.anIdM ? "Unidentified (" + this.anNUn : "Your gear (" + this.rows.size()) + ")");          // 0.3.9
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  // fix round: ui.frames off''')
rep('''  int per = t ? 200 : (rqOn ? (nUn > 0 ? 6 : 8) : (nUn > 0 ? 10 : 12));''', '''  int per = t ? 200 : (rqOn ? (nUn > 0 ? 5 : 8) : (nUn > 0 ? 10 : 12));          // 0.3.9: the tick row (52) takes one Requip-page row
  if (!t && this.anIdM && this.anNUn < this.rows.size() && per > 1) per = per - 1;          // review F4: room for the Re-identify head''')
rep('''  int lh = t ? (nUn > 0 ? 574 : 626) : per * 46 + (rqOn ? 212 : 0);''', '''  int lh = t ? (nUn > 0 ? 522 : 626) : per * 46 + (rqOn ? 212 : 0);          // 0.3.9: Identify all 52 + the tick row 52''')
rep('''    b.set("#SkyyGEmpty1.Text", "No weapons, armor, tools or mystery bags on you.");''',
    '''    b.set("#SkyyGEmpty1.Text", this.anIdM ? "No unidentified gear or mystery bags on you." : "No identified weapons, armor or tools on you.");          // 0.3.9''')
_AL = between('''public void anList(@UCB@ b, @UEB@ ev, @INV@ inv, java.util.UUID u, java.util.ArrayList un) {''', '''public void anBuild(@REF@ ref''')
_ROW_A, _ROW_B = ('''    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \\"" + @PKG@.Gear.safe(id) + "\\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262);''',
    '''    String rid = "#SkyyGRow" + i;
    if (this.anIdM && i == this.anNUn) {          // 0.3.9 review F4: the Re-identify list under the unidentified gear
      b.appendInline("#SkyyGList", "Label #SkyyGReHead { Anchor: (Height: 44); Padding: (Horizontal: 6); Text: \\"\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
      b.set("#SkyyGReHead.Text", "Re-identify (" + (this.rows.size() - this.anNUn) + ") - from a bag, uses left");
      b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    }
    if (this.anIdM && i < this.anNUn) {          // 0.3.9: the tick box left of an Identify-tab row (the row itself still puts the item on the anvil)
      boolean tkd = anTicks().contains(anKey(inv, rw));
      b.appendInline("#SkyyGList", "Group #SkyyGRowW" + i + " { Anchor: (Height: 44); LayoutMode: Left; TextButton #SkyyGTick" + i + " { Anchor: (Width: 52, Height: 44); Text: \\"" + (tkd ? "X" : "") + "\\"; " + @PKG@.GearUi.btn(tkd ? 0 : 1) + " } Group { Anchor: (Width: 6); } Button " + rid + " { Anchor: (Width: 412, Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \\"" + @PKG@.Gear.safe(id) + "\\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 210); Padding: (Horizontal: 10, Vertical: 5); Text: \\"\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(@PKG@.GearAnvil.rarOf(it)) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \\"\\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); } } }");
      ev.addEventBinding(@BT@.Activating, "#SkyyGTick" + i, @EVD@.of("a", "tick:" + i));
    } else
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \\"" + @PKG@.Gear.safe(id) + "\\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262);''')
assert _AL.count(_ROW_A) == 1
rep(_AL, _AL.replace(_ROW_A, _ROW_B))
_AL2 = between('''public void anList(@UCB@ b, @UEB@ ev, @INV@ inv, java.util.UUID u, java.util.ArrayList un) {''', '''public void anBuild(@REF@ ref''')
_SUB_A = '''    b.set("#SkyyGRowSub" + i + ".Text", @PKG@.GearAnvil.rowSub(it));'''
assert _AL2.count(_SUB_A) == 1
rep(_AL2, _AL2.replace(_SUB_A, '''    b.set("#SkyyGRowSub" + i + ".Text", this.anIdM && i >= this.anNUn ? "Re-id " + @PKG@.Gear.fmt(@PKG@.GearUnid.rerollCostOf(@PKG@.GearUnid.rerollDoc(it))) + " coins" : @PKG@.GearAnvil.rowSub(it));          // 0.3.9 review F4'''))
rep('''  this.rows = @PKG@.GearAnvil.rows(inv);
  java.util.ArrayList un = @PKG@.GearIdent.rows(inv);
  long have = @PKG@.GearForge.purse(u);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 0, 1066, "Anvil");''', '''  this.rows = anRows(inv);          // 0.3.9: identified gear on the Anvil, unidentified gear on the Identify tab
  java.util.ArrayList un = @PKG@.GearIdent.rows(inv);
  long have = @PKG@.GearForge.purse(u);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", this.anIdM ? 5 : 0, 1066, this.anIdM ? "Identify" : "Anvil");''')
# Identify all clears the ticks; Identify picked = allInC on exactly the ticked rows
rep('''  int want = @PKG@.GearIdent.items(inv, rs);
  anClear();
  java.util.ArrayList rec = anRec();
  rec.clear();''', '''  int want = @PKG@.GearIdent.items(inv, rs);
  anClear();
  anTicks().clear();          // 0.3.9
  java.util.ArrayList rec = anRec();
  rec.clear();''')
before('''# the clicks: Other = the next Sigil that fits; Apply = arm (10 s, this exact item), then GearSigil.apply (the item stays on the anvil)''',
       r'''# 0.3.9 Identify picked: anIdAll on exactly the ticked rows still on the player (same guard, gate, allInC, reveal); a ticked item that left is
# skipped with a line
M(rpg, r"""
public void anIdSel(@INV@ inv) {
  if (!anGuard("identified")) return;
  java.util.UUID u = this.playerRef.getUuid();
  String gate = @PKG@.GearAnvil.idGateT(anTier(u));
  if (gate != null) { this.info = "-" + gate; return; }
  java.util.HashSet tk = anTicks();
  if (tk.isEmpty()) { this.info = "-Tick the items you want to identify first."; return; }
  java.util.ArrayList all = @PKG@.GearIdent.rows(inv);
  java.util.ArrayList rs = new java.util.ArrayList();
  java.util.HashSet found = new java.util.HashSet();
  for (int i = 0; i < all.size(); i++) {
    int[] rw = (int[]) all.get(i);
    String k = anKey(inv, rw);
    if (k != null && tk.contains(k)) { rs.add(rw); found.add(k); }
  }
  int gone = tk.size() - found.size();
  tk.clear();
  if (rs.isEmpty()) { this.info = "-The ticked items are not on you any more - nothing was identified."; return; }
  int want = @PKG@.GearIdent.items(inv, rs);
  anClear();
  java.util.ArrayList rec = anRec();
  rec.clear();
  @IC@[] by = new @IC@[6];
  for (int s = 0; s < by.length; s++) by[s] = @PKG@.GearStamp.section(inv, s);
  java.util.ArrayList rvL = new java.util.ArrayList();
  Object[] r = @PKG@.GearIdent.allInC(by, rs, u, this.playerRef.getUsername(), rec, rvL);
  int done = ((Integer) r[0]).intValue();
  long spent = ((Long) r[1]).longValue();
  int skipped = ((Integer) r[2]).intValue();
  String first = (String) r[3];
  String stop = (String) r[4];
  if (done > 0) this.anIdAt = System.currentTimeMillis();
  String head = "Identified " + done + " of " + want + (done > 0 ? " for " + @PKG@.Gear.fmt(spent) + " coins" : "");
  String left = gone > 0 ? " - " + gone + " ticked item" + (gone == 1 ? "" : "s") + " had left your inventory (skipped)" : "";
  if (stop != null) this.info = "-" + head + " - stopped: " + stop + left;
  else if (skipped > 0) this.info = "-" + head + " - skipped " + skipped + " (" + first + ")" + left;
  else if (gone > 0) this.info = "-" + head + left;
  else this.info = "+Identified " + done + (done == 1 ? " item" : " items") + " for " + @PKG@.Gear.fmt(spent) + " coins.";
  if (done > 0 && @PKG@.GearIdent.reveal(u, rvL, "Identified " + done + (done == 1 ? " item!" : " items!"), "Click the cards to see what you got.", @PKG@.GearIdent.backFor(this))) @PKG@.GearIdent.revTell(this.playerRef, this.info);
}""")
''')
# the clicks: the tab switch, the ticks, Identify picked; a stale click of the other tab does nothing
rep('''  if (a.equals("mode:3")) { @PKG@.GearSmith.craftTab(data, this.playerRef); return true; }
  if (a.startsWith("mode:")) {
    if (a.equals("mode:2") && @PKG@.GearUi.multiTab()) {''', '''  if (a.equals("mode:3")) { @PKG@.GearSmith.craftTab(data, this.playerRef); return true; }
  if (a.equals("mode:5") || (a.equals("mode:0") && this.anIdM)) {          // 0.3.9: Anvil <-> Identify on the same page
    boolean want = a.equals("mode:5");
    if (want && !@PKG@.GearAnvil.idTab()) return true;
    if (want != this.anIdM) { this.anIdM = want; anClear(); anRec().clear(); anTicks().clear(); this.pageNo = 0; this.info = ""; }
    rebuild();
    return true;
  }
  if (a.startsWith("mode:")) {
    if (a.equals("mode:2") && @PKG@.GearUi.multiTab()) {''')
rep('''  if (a.equals("forge") || a.equals("lvl") || a.equals("up")) {
    long nw = System.currentTimeMillis();''', '''  // 0.3.9: a stale click of the other tab (the page was rebuilt in between) does nothing
  if (this.anIdM && (a.equals("forge") || a.equals("lvl") || a.equals("up") || a.equals("sg") || a.equals("sgn"))) { rebuild(); return true; }
  if (!this.anIdM && (a.equals("id") || a.equals("rr") || a.equals("idall") || a.equals("idsel") || a.equals("tickall") || a.startsWith("tick:"))) { rebuild(); return true; }
  if (a.startsWith("tick:")) {
    int ti = -1;
    try { ti = Integer.parseInt(a.substring(5)); } catch (Throwable t5) { ti = -1; }
    if (ti >= 0 && this.rows != null && ti < this.anNUn && ti < this.rows.size()) {
      String k = anKey(inv, (int[]) this.rows.get(ti));
      if (k != null) { if (!anTicks().remove(k)) anTicks().add(k); }
    }
    rebuild();
    return true;
  }
  if (a.equals("tickall")) {
    java.util.HashSet tk = anTicks();
    int on = 0;
    for (int q = 0; this.rows != null && q < this.anNUn && q < this.rows.size(); q++) { String k = anKey(inv, (int[]) this.rows.get(q)); if (k != null && tk.contains(k)) on++; }
    boolean clear = this.rows != null && on > 0 && on == this.anNUn;
    tk.clear();
    if (!clear) for (int q = 0; this.rows != null && q < this.anNUn && q < this.rows.size(); q++) { String k = anKey(inv, (int[]) this.rows.get(q)); if (k != null) tk.add(k); }
    rebuild();
    return true;
  }
  if (a.equals("idsel")) { anIdSel(inv); rebuild(); return true; }
  if (a.equals("forge") || a.equals("lvl") || a.equals("up")) {
    long nw = System.currentTimeMillis();''')
# /identify = the Identify tab
rep('''      @PKG@.ReforgePage ap = new @PKG@.ReforgePage(pr);
      ap.anPreselect(p.getInventory(), true);''', '''      @PKG@.ReforgePage ap = new @PKG@.ReforgePage(pr);
      ap.anIdM = true;          // 0.3.9: /identify opens the Identify tab
      ap.anPreselect(p.getInventory(), true);''')
# the hooks: the Pre veto body, the Identify tab click on the other Smithing pages
rep('''for _pg in (rpg, mpg, spg):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearLL.tabGo($3, this.playerRef)) return; }"))
''', '''for _pg in (rpg, mpg, spg):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearLL.tabGo($3, this.playerRef)) return; }"))
# 0.3.9: the Identify tab click on the Craft / Tools / Multitool pages (the Anvil page switches in place); the gathering tier-up craft veto
for _pg in (mpg, spg, lpg):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearAnvil.idTabGo($3, this.playerRef)) return; }"))
gll.getDeclaredMethod("craftVeto").setBody(J("{ return @PKG@.GearSmith.anvilOnly($1); }"))
''')

# ================================================================================================================ 2b. wrap the sends of the two pages
def _first_arg(t, i):
    """t[i:] starts right after '(' - the first top-level argument"""
    depth, q, j = 0, False, i
    while j < len(t):
        c = t[j]
        if q:
            if c == "\\":
                j += 2
                continue
            if c == '"':
                q = False
        elif c == '"':
            q = True
        elif c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                return t[i:j]
            depth -= 1
        elif c == "," and depth == 0:
            return t[i:j]
        j += 1
    raise AssertionError("no argument end")


def _wrap(t):
    n0 = t.count("b.appendInline(")
    t = t.replace("b.appendInline(", "@PKG@.GearUi.ap(b, ")
    out, i, ns = [], 0, 0
    while True:
        j = t.find("b.set(", i)
        if j < 0:
            out.append(t[i:])
            break
        a = _first_arg(t, j + 6)
        if a.rstrip().endswith('.Text"') and not t[j - 1:j].isalnum() and t[j - 1:j] != ".":
            out.append(t[i:j] + "@PKG@.GearUi.st(b, ")
            ns += 1
        else:
            out.append(t[i:j + 6])
        i = j + 6
    t = "".join(out)
    ne = t.count("ev.addEventBinding(")
    t = t.replace("ev.addEventBinding(", "@PKG@.GearUi.on(b, ev, ")
    return t, n0, ns, ne


WRAPPED = []
for _a, _b in (('''# the figure of a set (64 px cells: Head top centre, Hands left of Chest, Legs bottom centre) or the tier ladder (up to 8 icons) into a group''',
                '''# the shared click guards: false = refused (this.info says why)'''),
               ('''# a column of plain text lines (head + lines with their colours) in #SkyyGCols''',
                '''# the shared guard of the identify clicks (forge / lvlUp / upDo keep their own, the same three checks)''')):
    _old = between(_a, _b)
    _new, _n0, _ns, _ne = _wrap(_old)
    assert _n0 > 30 and _ns > 20 and _ne > 10, (_n0, _ns, _ne)
    rep(_old, _new)
    WRAPPED.append((_n0, _ns, _ne))
print("0.3.9 wrapped sends (appendInline / set Text / events): Craft tab %s, Anvil / Identify %s" % (WRAPPED[0], WRAPPED[1]))

# ================================================================================================================ the manifest
rep('''/smithing = one page with Craft (set cards, class filter, crafts into Requip), Anvil (pick an item: Reforge, Level up, Upgrade or Identify it in one panel; /reforge, /upgrade and /identify open it),''',
    '''/smithing = one page with Craft (the gathering armor that levels up: Mining, Foraging, Farming and Fishing sets - the first tier is crafted, higher tiers are tiered up on the Anvil; crafts into Requip; combat armor and weapons are crafted at the benches), Anvil (pick an identified item: Reforge, Level up or Upgrade it in one panel; /reforge and /upgrade open it), Identify (unidentified gear and mystery bags: identify one, the ticked ones or all, re-identify; /identify opens it),''')

# ================================================================================================================ checks on the result
assert "VerticalAlignment: Top" not in s
assert s.index("public static String bad(String d)") < s.index("public static void ap(@UCB@ b") < s.index("public static int tabs(@UCB@ b")
assert s.index("public static boolean isSet(int c)") < s.index("public static int cat(String id)") < s.index("public static String anvilOnly(String id)") < s.index("public static java.util.ArrayList groups(")
assert s.index("public static String anvilOnly(String id)") < s.index('gll.getDeclaredMethod("craftVeto").setBody(')
assert s.index('F(rpg, "public boolean anIdM;")') < s.index("public static String backFor(Object page)") and s.index("public static String tierUpOnly(") < s.index("public static String anvilOnly(")
assert "click Show all" not in s and "GARM_ANVIL = pbool(" in s
assert s.index("public void tierRow(") < s.index("public void piecesArea(")
assert s.index("public boolean anFitsMode(") < s.index("public boolean anPick(@INV@ inv, int s, int slot) {\n  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);\n  if (!@PKG@.GearAnvil.fits(it)) return false;\n  if (!anFitsMode")
assert s.index("public void anHelpId(") < s.index("public void anPanel(") and s.index("public void anNote(") < s.index("public void anPanel(")
assert s.index("public void anIdSel(") < s.index("public boolean anEvent(")
assert s.index("public static boolean idTabGo(") < s.index("public static int toolTier(")
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.8 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.8 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
