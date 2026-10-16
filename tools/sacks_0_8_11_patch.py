"""Derive SkyySacks/build_skyysacks_0.8.11.py from the SET pin 0.8.10 (the GENERATED build_skyysacks_0.8.10.py; edit THIS file, then
regenerate: python tools/sacks_0_8_11_patch.py; never re-run sacks_0_8_10_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.10 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_11_patch.py   then   python SkyySacks/build_skyysacks_0.8.11.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.11.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.11 = THE CRAFTING HUB + CRAFTER LOOK + ADD FUEL + SORT BY TIER + BENCHES USE THE ACCESSORY BAG + VOID DEPOSIT ALL (round craft01,
2026-10-16, with SkyyAccessories 0.5.19 + SkyyMenu 0.3.31). Skyy's words (docs/answered/ui.md + bags.md 2026-10-16): "we need a crafting tab
at the top. unless we want to roll crafting and smithing into 1 page called crafting with separate crafting and smithing pages. (and upgrade
the look of the crafter while were at it.)"; "id add an add fuel button which pops up a selector. you pick which fuel from the list of what
you have. then type in a number. but keep the quick load bar we currently have." + "but sort it by how much you have. so if you have 1000
sticks they will show up first in the list."; "sort this by tier. crops, enchanted crops, seeds then enhances seeds in that order. (sort
everything by tier in all shops and crafting.)"; "accessory's go straight to the accessory bag now. but the bench cant pull from the bag to
craft the next tier yet."; "move deposit all to the top, and make it deposit everything from your in inventory into the right bag. instead
of just smithing items into the smithing bag. (change what is currently deposit all to deposit smithing.)"
A. CRAFTING HUB TAB (tools/HUBS-CONTRACT.md, kit 1.6): /craft is the REAL tab hub:tab:smithing:recipes = {"SkyySacks", "Crafting", order 5,
   "craft", CraftHubOpen, null, icon "smithing_recipes"} (put in setup, removed in shutdown - only while it still holds our array; SkyyMenu
   0.3.30's stand-in steps aside). The hub id stays "smithing" (saved shortcuts tab:smithing:recipes / hub:smithing keep working); SkyyMenu
   0.3.31 titles that hub "Crafting" and its Gear tab "Smithing". The craft page is a kit 1.6 ROW SHELL page (sky theme, 1200 x 960): row 1
   (Home + the hubs, Crafting active), the X, the hub's tab strip (Crafting active, Smithing = SkyyGear's /smithing) - HubBar.route first
   in handleDataEvent ("self" redraws, a tab that opened elsewhere is acknowledged, a failed one says so on the result line). The kit's 59
   Sky Window files + the smithing_recipes tab icon (art/hub-tab-icons, sha256 = its manifest) ship in this jar (byte-identical to the
   other jars that ship them).
B. CRAFTER LOOK: the sky kit everywhere (Primary / Secondary / Tertiary sky buttons, Row / PanelInset row backgrounds, SlotEmpty frames, the
   vanilla label colours); the crafter's tabs = Primary (active) / Secondary; every recipe row = the output in a slot frame + its name (+ the
   tier tag "T3 Iron" in gold) over one chip per input: its item icon + "have/need" (green / red; up to 4 inputs also show the name),
   then Craft (Primary) / x10 / All N - greyed out (Disabled look, not bound) when nothing can be made. Fits 1080 (kit assert).
C. SORT BY TIER (PROJECT-RULES 4): every /craft list (tabs, search, Collections, Campfire, Furnace / Tannery) = tier, then name -
   no more craftable-first. The tier = tools/tier_tags.py (THE table, read at build time: ores, bars, logs, crops, seeds, Eternal seeds,
   Enchanted, tools ...), else an id's _T<n> / rarity word, else its tool metal word (tier_tags.TOOL_METALS); untiered first (0). Crop
   families group per crop inside their tier: crop, Enchanted crop, seeds, Eternal seeds (then the other items of that tier by ItemLevel).
D. FURNACE ADD FUEL: next to the quick-load bar (kept as it is) an ADD FUEL button opens a picker of every fuel you own (inventory + the
   Void), most first; pick one, type an amount (empty = all that fits; max = what you have / the room left), LOAD loads it (several
   rebuilds of the mirror when it is more than the mirror offers at once; counted before and after, booked to the Void once).
E. BENCHES USE THE ACCESSORY BAG (SkyyAccessories 0.5.19 acc:fn:bag; without it nothing changes):
   - a bench shows the bag's accessories that its recipes use (added to the window's extra-materials LIST only - never to a container);
   - a bench craft click (CraftRecipeAction, the inbound filter's PreCraftTask, before the vanilla handler) MOVES each accessory the recipe
     needs and the inventory lacks from the bag into the inventory (bag take -> inventory add, counted; no room = back into the bag + one
     chat line); the vanilla craft then uses it like any inventory item; AccSettle (queued behind the vanilla handler) puts back into the
     bag whatever the craft did not use (inventory count above the count before the move; refused by the bag = stays in the inventory).
     Every accessory is in exactly one place at every moment: no dupe, no loss. Logged in crafts.log (ACCBAG lines).
   - /craft (the Artifacts tab): the bag's accessories count in the have / need chips and the limits (a copy container next to the
     inventory and the Void); a craft takes them from that copy and EXACTLY what the copy lost leaves the bag right after (bag take, one per
     item, same world-thread click - nothing can change the bag in between).
F. VOID DEPOSIT ALL = EVERY BAG: a DEPOSIT ALL button at the top of the Void page (next to Craft) puts every Void item you carry (storage,
   hotbar, backpack) into its own category, all six, each up to its space (SweepTask.sweep with no category: the per-category limits,
   whole fish with their weight, cooked food stays as before); the side button is now DEPOSIT <CATEGORY> (the old Deposit all).
REVIEW FIXES (round craft01fix, the critics): A1 the bench put-back runs in TWO hops (the scheduler 250 ms after the click, then the world
   thread) so it can never run before the vanilla craft handler of that click; B1 an open bench refreshes when the Accessory Bag list changes
   (its signature is part of the bench link's staleness test, and the benches are re-sent after a put-back); B2 /craft takes the needed
   accessories from the bag BEFORE anything is removed (a refused take = nothing used; unused ones go back); A4 no sweep (automatic,
   Deposit <bag>, DEPOSIT ALL) takes a stack with extra data except a whole fish; A5 the bench list / moves use exact item-id inputs, the need
   summed per id; B4 tier, then name (ItemLevel no longer part of the order); B6 the materials line names the Accessory Bag only while
   SkyyAccessories 0.5.19 is running; B5 the crafter's own tool / weapon / armor tab is called GEAR (the hub's SMITHING tab is /smithing);
   A2 / B3 every bench move bag -> inventory is written to crafts.log with its ids and bag slots (a crash between the bag save and the next
   inventory save can be reconciled from it).
SAVED DATA: none new (crafts.log gets ACCBAG lines; the Accessory Bag files change only through SkyyAccessories' own take / put).
ROLLBACK to 0.8.10: safe (no file format change); the Crafting tab then comes back as SkyyMenu's stand-in.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.10.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.11.py"))
assert P.has('VERSION = "0.8.10"\n') and P.has("fishWithdraw") and not P.has("AccLink"), "not the live generated SkyySacks 0.8.10"
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.11 = THE CRAFTING HUB"):].rstrip() + "\n"


def block(start, end):
    """the unique text from `start` up to and including the first `end` after it"""
    assert P.s.count(start) == 1, "block start count %d: %s" % (P.s.count(start), start[:120])
    i = P.s.index(start)
    j = P.s.index(end, i)
    return P.s[i:j + len(end)]


# ================================================================================================ header, version, imports
P.rep('''   drops the oldest one; a fish refunded by id comes back plain (value can only go down, never a dupe).
"""
''', '''   drops the oldest one; a fish refunded by id comes back plain (value can only go down, never a dupe).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.10"\n', 'VERSION = "0.8.11"\n')
P.rep('''import skyyench as EN    # 0.8.1: the Enchanted materials table (one source with SkyyCollections 0.2.11 + SkyyBazaar 0.1.10)
''', '''import skyyench as EN    # 0.8.1: the Enchanted materials table (one source with SkyyCollections 0.2.11 + SkyyBazaar 0.1.10)
import tier_tags as TT   # 0.8.11: THE tier table (sort by tier, PROJECT-RULES 4) - read only
''')
P.rep('''plt = pool.makeClass(PKG + ".PickLate")   # 0.8.6: the one late retry of an unclaimed block-spot drop (tools/sacks_0_8_6_patch.py)
''', '''plt = pool.makeClass(PKG + ".PickLate")   # 0.8.6: the one late retry of an unclaimed block-spot drop (tools/sacks_0_8_6_patch.py)
# 0.8.11 (tools/sacks_0_8_11_patch.py): the Accessory Bag link (benches + /craft) and the Crafting hub tab's open Function
acl = pool.makeClass(PKG + ".AccLink")
aset = pool.makeClass(PKG + ".AccSettle")
chop = pool.makeClass(PKG + ".CraftHubOpen")
_JT.update({"PGM": PGM, "BRQ": BRQ})
''')

# ================================================================================================ C. the tier table + RecipeCmp
P.rep('''# ================= RecipeCmp: craftable first, then material progression, then name =================
rcmp.addInterface(pool.get("java.util.Comparator"))''', '''# ================= RecipeCmp: 0.8.11 tier, then name (PROJECT-RULES 4 "Sort by tier everywhere") =================
# 0.8.11: the build-time copy of tools/tier_tags.py (THE table): every tiered id -> its DISPLAY tier (T1 Crude .. T8 Onyxium), and for the
# crop families the crop + its place (0 crop, 1 Enchanted crop, 2 seeds, 3 Eternal seeds; 9 = not a crop family). The tool metal words
# (tier_tags.TOOL_METALS) tier everything else made of a ladder metal.
def _tt_grp(i):
    f = TT.family(i)
    if f == "crop":
        return i[len("Plant_Crop_"):-len("_Item")], 0
    if f == "seed":
        if i.endswith("_Eternal"):
            return i[len("Plant_Seeds_"):-len("_Eternal")], 3
        return i[len("Plant_Seeds_"):], 2
    if f == "enchanted":
        _b = dict(TT.ENCH_BASE).get(i[len("Skyy_Ench_"):])
        if _b and TT.family(_b) == "crop":
            return _b[len("Plant_Crop_"):-len("_Item")], 1
    return "", 9
TT_IDS = sorted(TT.ROWS)
TT_TIERS = [TT.tier(_i) for _i in TT_IDS]
TT_GRPS = [_tt_grp(_i) for _i in TT_IDS]
assert all(1 <= _t <= len(TT.LADDER) for _t in TT_TIERS) and all('"' not in _i and "," not in _i for _i in TT_IDS)
assert _tt_grp("Plant_Crop_Wheat_Item") == ("Wheat", 0) and _tt_grp("Skyy_Ench_Wheat") == ("Wheat", 1) and \\
    _tt_grp("Plant_Seeds_Wheat") == ("Wheat", 2) and _tt_grp("Plant_Seeds_Wheat_Eternal") == ("Wheat", 3) and _tt_grp("Ore_Iron") == ("", 9)
print("tier sort: %d ids from tools/tier_tags.py (%d crop-family ids), %d tool metal words" % (
    len(TT_IDS), sum(1 for _g in TT_GRPS if _g[1] < 9), len(TT.TOOL_METALS)))
_jsa = lambda xs: "new String[] { " + ", ".join(jlit(str(x)) for x in xs) + " }"
_jia = lambda xs: "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }"
rcmp.addField(CtField.make("public static final String[] TT_IDS = %s;" % _jsa(TT_IDS), rcmp))
rcmp.addField(CtField.make("public static final int[] TT_TIER = %s;" % _jia(TT_TIERS), rcmp))
rcmp.addField(CtField.make("public static final String[] TT_GRP = %s;" % _jsa([_g[0] for _g in TT_GRPS]), rcmp))
rcmp.addField(CtField.make("public static final int[] TT_RANK = %s;" % _jia([_g[1] for _g in TT_GRPS]), rcmp))
rcmp.addField(CtField.make("public static final String[] LADDER = %s;" % _jsa(TT.LADDER), rcmp))
rcmp.addField(CtField.make("public static final String[] METAL_W = %s;" % _jsa([_w for _w, _t in TT.TOOL_METALS]), rcmp))
rcmp.addField(CtField.make("public static final int[] METAL_T = %s;" % _jia([_t for _w, _t in TT.TOOL_METALS]), rcmp))
rcmp.addField(CtField.make("public static java.util.HashMap TTMAP;", rcmp))
rcmp.addInterface(pool.get("java.util.Comparator"))''')
P.rep('''# 0.8.8 (Skyy "make sure this is sorted by tier too"): the tier of an item id - _T<n> = n; _Common .. _Mythic = 1..6; the Omni accessory
# after every tier; else the material ladder (tierOf: none / Crude 0 .. Onyxium 8)
rcmp.addMethod(CtNewMethod.make("""
public static int tierKey(String id) {
  if (id == null) return 0;
  if (id.startsWith("Skyy_Acc") && id.endsWith("_Omni")) return 99;
  int u = id.lastIndexOf("_T");
  if (u >= 0 && u + 2 < id.length() && id.length() - u <= 5) {
    boolean dig = true;
    for (int i = u + 2; i < id.length(); i++) if (!Character.isDigit(id.charAt(i))) dig = false;
    if (dig) return Integer.parseInt(id.substring(u + 2));
  }
  String[] w = new String[] { "_Common", "_Uncommon", "_Rare", "_Epic", "_Legendary", "_Mythic" };
  for (int i = 0; i < w.length; i++) if (id.endsWith(w[i])) return i + 1;
  return tierOf(id);
}""", rcmp))''', '''# 0.8.11: the tier_tags index of an id (-1 = not in the table)
rcmp.addMethod(CtNewMethod.make("""
public static synchronized java.util.HashMap ttMap() {
  if (TTMAP == null) {
    java.util.HashMap m = new java.util.HashMap();
    for (int i = 0; i < TT_IDS.length; i++) m.put(TT_IDS[i], Integer.valueOf(i));
    TTMAP = m;
  }
  return TTMAP;
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static int ttIndex(String id) {
  if (id == null) return -1;
  Object o = ttMap().get(id);
  return o == null ? -1 : ((Integer) o).intValue();
}""", rcmp))
# 0.8.11: the display tier of a tool metal word in the id (a whole _-separated word: Tool_Pickaxe_Iron, Weapon_Sword_Cobalt), 0 = none
rcmp.addMethod(CtNewMethod.make("""
public static int metalTier(String id) {
  if (id == null) return 0;
  String[] w = id.split("_");
  for (int i = 0; i < w.length; i++) for (int j = 0; j < METAL_W.length; j++) if (w[i].equals(METAL_W[j])) return METAL_T[j];
  return 0;
}""", rcmp))
# 0.8.11: an own-ladder tier suffix _T<n> (accessories, bags), 0 = none
rcmp.addMethod(CtNewMethod.make("""
public static int suffixTier(String id) {
  if (id == null) return 0;
  int u = id.lastIndexOf("_T");
  if (u >= 0 && u + 2 < id.length() && id.length() - u <= 5) {
    for (int i = u + 2; i < id.length(); i++) if (!Character.isDigit(id.charAt(i))) return 0;
    return Integer.parseInt(id.substring(u + 2));
  }
  return 0;
}""", rcmp))
# 0.8.8 (Skyy "make sure this is sorted by tier too") / 0.8.11 (Skyy "sort everything by tier in all shops and crafting."): the tier of an
# item id - the Omni accessory after every tier; _T<n> = n; _Common .. _Mythic = 1..6; tools/tier_tags.py's display tier; else the tool
# metal word (T1 Crude / Wood .. T8 Onyxium); untiered = 0
rcmp.addMethod(CtNewMethod.make("""
public static int tierKey(String id) {
  if (id == null) return 0;
  if (id.startsWith("Skyy_Acc") && id.endsWith("_Omni")) return 99;
  int st = suffixTier(id);
  if (st > 0) return st;
  String[] w = new String[] { "_Common", "_Uncommon", "_Rare", "_Epic", "_Legendary", "_Mythic" };
  for (int i = 0; i < w.length; i++) if (id.endsWith(w[i])) return i + 1;
  int x = ttIndex(id);
  if (x >= 0) return TT_TIER[x];
  return metalTier(id);
}""", rcmp))
# 0.8.11: the tier tag a recipe row shows next to its name: "T3 Iron" (the table / a metal word), "T2" (an own ladder _T<n>), "" = none
rcmp.addMethod(CtNewMethod.make("""
public static String tierText(String id) {
  if (id == null) return "";
  int st = suffixTier(id);
  if (st > 0) return "T" + st;
  int x = ttIndex(id);
  int t = x >= 0 ? TT_TIER[x] : metalTier(id);
  if (t < 1 || t > LADDER.length) return "";
  return "T" + t + " " + LADDER[t - 1];
}""", rcmp))''')
P.rep('''rcmp.addMethod(CtNewMethod.make("""
public static int sortKey(String id) { return tierKey(id) * 1000000 + level(id); }""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static String sortName(String id) {
  if (id == null) return "";
  String n = com.skyy.sacks.SackDefs.dname(id);
  if (n == null) n = id.replace('_', ' ');
  return n.toLowerCase() + " " + id;
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  Object[] x = (Object[]) a; Object[] y = (Object[]) b;
  boolean cx = ((Integer) x[1]).intValue() > 0; boolean cy = ((Integer) y[1]).intValue() > 0;
  if (cx != cy) return cx ? -1 : 1;
  int tx = ((Integer) x[2]).intValue(); int ty = ((Integer) y[2]).intValue();
  if (tx != ty) return tx < ty ? -1 : 1;
  return ((String) x[3]).compareTo((String) y[3]);
}""", rcmp))''', '''# 0.8.11: tier first; inside a tier the crop families come first, grouped per crop (sortName: "<crop> <0..3> ..."), then everything else by
# name (review fix B4: the written rule is tier, then name - 0.8.8's ItemLevel term is gone; the tier is at most 99)
rcmp.addMethod(CtNewMethod.make("""
public static int sortKey(String id) {
  int t = tierKey(id);
  int x = ttIndex(id);
  if (x >= 0 && TT_RANK[x] < 9) return t * 10000000;
  return t * 10000000 + 1000000;
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static String sortName(String id) {
  if (id == null) return "";
  String n = com.skyy.sacks.SackDefs.dname(id);
  if (n == null) n = id.replace('_', ' ');
  int x = ttIndex(id);
  String pre = (x >= 0 && TT_RANK[x] < 9) ? (TT_GRP[x].toLowerCase() + " " + TT_RANK[x] + " ") : "";
  return pre + n.toLowerCase() + " " + id;
}""", rcmp))
# 0.8.11 (PROJECT-RULES 4): tier, then name - no craftable-first any more (rows that cannot be made are greyed out; "Craftable only" hides them)
rcmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  Object[] x = (Object[]) a; Object[] y = (Object[]) b;
  int tx = ((Integer) x[2]).intValue(); int ty = ((Integer) y[2]).intValue();
  if (tx != ty) return tx < ty ? -1 : 1;
  return ((String) x[3]).compareTo((String) y[3]);
}""", rcmp))''')

# ================================================================================================ F. the Void page: DEPOSIT ALL (every bag)
P.rep('''    "head": SUI.label("SkyyVHead", "", "strong", w=VIN_W - 160, h=V_TOP_H, size=20, col=J_("hcol", "#ffffff")),
''', '''    "head": SUI.label("SkyyVHead", "", "strong", w=VIN_W - 160 - V_DEPALL_W - 10, h=V_TOP_H, size=20, col=J_("hcol", "#ffffff")),
    # 0.8.11 (Skyy "move deposit all to the top, and make it deposit everything from your in inventory into the right bag"): every category
    "depevery": SUI.button("SkyyVDepEvery", "Deposit all", "primary", "small", w=V_DEPALL_W, anchor={"left": 10}),
''')
P.rep('''V_TOP_H, V_MAIN_H, V_INFO_H, V_UP_H = 34, 478, 26, 226
''', '''V_TOP_H, V_MAIN_H, V_INFO_H, V_UP_H = 34, 478, 26, 226
V_DEPALL_W = 186   # 0.8.11: the DEPOSIT ALL button in the top row (every category)
''')
P.rep('''    "pick": SUI.button("SkyyVPick", "Pick up all", "secondary", w=167),
    "depall": SUI.button("SkyyVDepAll", "Deposit all", "secondary", w=167, anchor={"left": 6}),
''', '''    "pick": SUI.button("SkyyVPick", "Pick up all", "secondary", w=156),
''')
P.rep('''_vflat = []
for _mk in VM.values():''', '''# 0.8.11 (Skyy "change what is currently deposit all to deposit smithing."): the side button names the open category - one markup per
# category, picked at runtime (static Text: the proven inline way; never a b.set on a button)
V_DEPCAT = [SUI.button("SkyyVDepAll", "Deposit " + _c, "secondary", w=178, anchor={"left": 6}, fit=False) for _c in PD_CATS]
page.addField(CtField.make("public static final String[] DEPCAT = new String[] { %s };" % ", ".join(jlit(_m) for _m in V_DEPCAT), page))
assert len(V_DEPCAT) == 6 and 156 + 6 + 178 == V_SIDE_W
_vflat = list(V_DEPCAT)
for _mk in VM.values():''')
P.rep('''  b.appendInline("#SkyyVTop", @@craft@@);
  ev.addEventBinding(@BT@.Activating, "#SkyyVCraft", @EVD@.of("a", "craft"));''', '''  b.appendInline("#SkyyVTop", @@depevery@@);   // 0.8.11: every bag
  ev.addEventBinding(@BT@.Activating, "#SkyyVDepEvery", amtEvt("depevery"));
  b.appendInline("#SkyyVTop", @@craft@@);
  ev.addEventBinding(@BT@.Activating, "#SkyyVCraft", @EVD@.of("a", "craft"));''')
P.rep('''  b.appendInline("#SkyyVBtnsB", @@depall@@);
''', '''  b.appendInline("#SkyyVBtnsB", DEPCAT[ci]);   // 0.8.11: "Deposit <category>" (the old Deposit all)
''')
P.rep('''    if (a.equals("depall")) {
      @PKG@.SackPool.clearKeptCat(k, this.cat);''', '''    // 0.8.11 DEPOSIT ALL = EVERY BAG: every category's kept counts cleared, then one sweep with no category (each up to its own space)
    if (a.equals("depevery")) {
      for (int c = 0; c < cats.length; c++) @PKG@.SackPool.clearKeptCat(k, cats[c]);
      @PKG@.SackPool.forgetSeen(u);
      java.util.HashMap swept = new java.util.HashMap();
      int moved = @PKG@.SweepTask.sweep(player, k, (String) null, true, swept, @PKG@.VoidStore.capsK(u, k), (java.util.HashMap) null);
      java.util.HashSet into = new java.util.HashSet();
      java.util.Iterator si = swept.keySet().iterator();
      while (si.hasNext()) { String c0 = @PKG@.SackDefs.homeOf((String) si.next()); if (c0 != null) into.add(c0); }
      this.info = moved > 0 ? ("+Deposited " + num((long) moved) + " items into " + into.size() + (into.size() == 1 ? " bag" : " bags")) : "-Nothing to deposit (or those bags are full)";
      if (!@PKG@.SackDefs.COOKED_FARM && @PKG@.SweepTask.cookedHeld(player.getInventory()) > 0) this.info = this.info + " - cooked food stays in your inventory";
      @PKG@.SackPool.saveSoon(k);
      rebuild();
      return;
    }
    if (a.equals("depall")) {
      @PKG@.SackPool.clearKeptCat(k, this.cat);''')

# review fix A4: the sweep (automatic, Deposit <bag>, DEPOSIT ALL) never takes a stack carrying extra data - the pool only counts ids, so it
# would lose that data (whole fish keep theirs through fishEntry, 0.8.10)
P.rep('''      if (take <= 0) continue;
      String fe = null;   // 0.8.10: a whole fish goes in with its entry (weight, length, catcher) or not at all''', '''      if (take <= 0) continue;
      if (!{PKG}.SackDefs.isCatch(id) && it.getMetadata() != null && !it.getMetadata().isEmpty()) continue;   // 0.8.11 review fix A4: plain stacks only
      String fe = null;   // 0.8.10: a whole fish goes in with its entry (weight, length, catcher) or not at all''')
# review fix B5: the crafter's own tool / weapon / armor tab is GEAR (the hub's row 2 SMITHING is SkyyGear's /smithing page)
P.rep('''  t.add(new String[] {{ "A:smith", "Smithing" }});''', '''  t.add(new String[] {{ "A:smith", "Gear" }});   // 0.8.11 review fix B5: not "Smithing" (the hub tab of that name is /smithing)''')
P.rep('''  return "Smithing shows gear for your class - " + hidden + " hidden (Show all is in /smithing). Materials: your inventory, then the Void.";''',
      '''  return "Gear shows the gear for your class - " + hidden + " hidden (Show all is in Smithing). Materials: your inventory, then the Void.";''')

# ================================================================================================ E. AccLink + AccSettle (before LinkRec)
ACCLINK = r"""# ================= 0.8.11 AccLink: THE ACCESSORY BAG LINK (tools/sacks_0_8_11_patch.py docstring E; SkyyAccessories 0.5.19 acc:fn:bag) =================
# acc:fn:bag apply(Object[]{"list"|"take"|"put", UUID, key, id, slot}) - SkyyAccessories owns the bag; null = refused / absent (nothing moves)
acl.addMethod(CtNewMethod.make(jt(r'''
public static Object call(Object[] a) {
  try {
    Object f = @PKG@.SackPool.bridge().get("acc:fn:bag");
    if (!(f instanceof java.util.function.Function)) return null;
    return ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { return null; }
}'''), acl))
acl.addMethod(CtNewMethod.make(jt(r'''
public static String[] list(java.util.UUID u, String k) {
  if (u == null || k == null) return new String[0];
  Object r = call(new Object[] { "list", u, k });
  if (!(r instanceof String) || ((String) r).length() == 0) return new String[0];
  return ((String) r).split(",");
}'''), acl))
# review fix B1: the bag's list as one string (a cheap signature - an open bench refreshes when it changes)
acl.addMethod(CtNewMethod.make(jt(r'''
public static String sig(java.util.UUID u, String k) {
  if (u == null || k == null) return "";
  Object r = call(new Object[] { "list", u, k });
  return (r instanceof String) ? (String) r : "";
}'''), acl))
acl.addMethod(CtNewMethod.make(jt(r'''
public static int take(java.util.UUID u, String k, String id) {
  Object r = call(new Object[] { "take", u, k, id });
  return (r instanceof Integer) ? ((Integer) r).intValue() : -1;
}'''), acl))
acl.addMethod(CtNewMethod.make(jt(r'''
public static boolean put(java.util.UUID u, String k, String id, int slot) {
  return Boolean.TRUE.equals(call(new Object[] { "put", u, k, id, Integer.valueOf(slot) }));
}'''), acl))
acl.addMethod(CtNewMethod.make(jt(r'''
public static int countIn(@IC@ c, String id) {
  int n = 0;
  if (c == null || id == null) return 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n += it.getQuantity();
  }
  return n;
}'''), acl))
# a bench's display list: one ItemQuantity per bag accessory its recipes use (BagMirror.wants: item ids + resource types)
acl.addMethod(CtNewMethod.make(jt(r'''
public static @IQ@[] extras(java.util.UUID u, String k, java.util.Set wanted) {
  String[] ids = list(u, k);
  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  for (int i = 0; i < ids.length; i++) {
    if (wanted == null || !wanted.contains(ids[i])) continue;   // review fix A5: an accessory is an ITEM input (never a resource type)
    Integer c = (Integer) sum.get(ids[i]);
    sum.put(ids[i], Integer.valueOf(c == null ? 1 : c.intValue() + 1));
  }
  @IQ@[] out = new @IQ@[sum.size()];
  java.util.Iterator it = sum.entrySet().iterator();
  int n = 0;
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); out[n++] = new @IQ@((String) e.getKey(), ((Integer) e.getValue()).intValue()); }
  return out;
}'''), acl))
# /craft: a COPY of the bag accessories the shown / clicked recipes use (one 1-stack per bag slot), next to the inventory and the Void; null =
# none. What a craft takes from it leaves the bag through book() - never put on a bench window
acl.addMethod(CtNewMethod.make(jt(r'''
public static @SIC@ cont(String[] ids, java.util.Set wanted) {
  int n = 0;
  for (int i = 0; ids != null && i < ids.length; i++) if (wanted != null && wanted.contains(ids[i]) && @PKG@.ProcBench.item(ids[i]) != null) n++;
  if (n == 0) return null;
  @SIC@ c = new @SIC@((short) n);
  int s = 0;
  for (int i = 0; i < ids.length && s < n; i++) {
    if (wanted == null || !wanted.contains(ids[i]) || @PKG@.ProcBench.item(ids[i]) == null) continue;
    c.setItemStackForSlot((short) s, new @IS@(ids[i], 1));
    s++;
  }
  return c;
}'''), acl))
# review fix B2 (/craft): BEFORE the removal - the accessories the craft needs beyond what the inventory + the Void hold (exact item ids, the
# need summed per id) leave the bag first; one take refused = every one taken goes back and null is returned (nothing is used). Returns
# Object[]{ id, Integer bag slot } per item taken (may be empty)
acl.addMethod(CtNewMethod.make(jt(r'''
public static java.util.ArrayList takeFor(java.util.UUID u, String k, java.util.List inputs, @IC@ base) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.LinkedHashMap need = new java.util.LinkedHashMap();
  for (int i = 0; inputs != null && i < inputs.size(); i++) {
    @MQ@ mq = (@MQ@) inputs.get(i);
    if (mq == null || mq.getItemId() == null) continue;
    Integer c = (Integer) need.get(mq.getItemId());
    need.put(mq.getItemId(), Integer.valueOf((c == null ? 0 : c.intValue()) + mq.getQuantity()));
  }
  String[] ids = null;
  java.util.Iterator it = need.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    if (ids == null) ids = list(u, k);
    int inBag = 0;
    for (int j = 0; j < ids.length; j++) if (ids[j].equals(id)) inBag++;
    if (inBag == 0) continue;
    int shortN = ((Integer) e.getValue()).intValue() - countIn(base, id);
    for (int q = 0; q < shortN && q < inBag; q++) {
      int slot = take(u, k, id);
      if (slot < 0) {
        for (int b = out.size() - 1; b >= 0; b--) { Object[] t0 = (Object[]) out.get(b); put(u, k, (String) t0[0], ((Integer) t0[1]).intValue()); }
        return null;
      }
      out.add(new Object[] { id, Integer.valueOf(slot) });
    }
  }
  return out;
}'''), acl))
# the copy container of exactly the taken accessories (the craft removes from it after the inventory and the Void)
acl.addMethod(CtNewMethod.make(jt(r'''
public static @SIC@ contOf(java.util.ArrayList taken) {
  if (taken == null || taken.isEmpty()) return null;
  @SIC@ c = new @SIC@((short) taken.size());
  for (int i = 0; i < taken.size(); i++) c.setItemStackForSlot((short) i, new @IS@((String) ((Object[]) taken.get(i))[0], 1));
  return c;
}'''), acl))
# after the removal: every taken accessory the craft did not use goes back into its bag slot (refused = into the inventory, never lost)
acl.addMethod(CtNewMethod.make(jt(r'''
public static int unused(@ST@ st, @REF@ ref, @PLA@ p, java.util.UUID u, String k, @SIC@ c, java.util.ArrayList taken) {
  if (c == null || taken == null) return 0;
  int back = 0;
  for (short s = 0; s < c.getCapacity(); s++) {
    @IS@ it = c.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    Object[] t0 = (Object[]) taken.get(s);
    String id = (String) t0[0];
    c.removeItemStackFromSlot(s, it.getQuantity());
    if (put(u, k, id, ((Integer) t0[1]).intValue())) { back++; continue; }
    @SIC@.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, 1));
  }
  return back;
}'''), acl))
# review fix B1: the player's open bench windows re-send their lists (the bag changed): the vanilla code re-feeds, the filter re-attaches
acl.addMethod(CtNewMethod.make(jt(r'''
public static int touch(@PLA@ p) {
  int n = 0;
  try {
    @WM@ wm = p.getWindowManager();
    if (wm == null) return 0;
    java.util.List ws = wm.getWindows();
    for (int i = 0; ws != null && i < ws.size(); i++) {
      Object w = ws.get(i);
      if ((w instanceof @SCW@ || w instanceof @PBW@) && w instanceof @MCW@) { ((@MCW@) w).invalidateExtraResources(); n++; }
    }
  } catch (Throwable t) { }
  return n;
}'''), acl))
# one plain unit of id out of the inventory (counted); false = none there
acl.addMethod(CtNewMethod.make(jt(r'''
public static boolean removeOne(@IC@ c, String id) {
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
    if (it.getMetadata() != null && !it.getMetadata().isEmpty()) continue;
    int b0 = countIn(c, id);
    c.removeItemStackFromSlot(s, 1);
    if (countIn(c, id) == b0 - 1) return true;
  }
  return false;
}'''), acl))
# BENCH: one accessory id from the bag into the inventory (bag take, then a counted add); no room = back into the bag (refused there = it
# drops at the player's feet - never lost). Returns the bag slot (>= 0 moved), -1 not in the bag / refused, -2 no room (why gets a mark)
acl.addMethod(CtNewMethod.make(jt(r'''
public static int pull(@PLA@ p, @ST@ st, @REF@ ref, java.util.UUID u, String k, String id, StringBuilder why) {
  @IC@ dst = p.getInventory().getCombinedStorageHotbarBackpack();
  int b0 = countIn(dst, id);
  int slot = take(u, k, id);
  if (slot < 0) return -1;
  boolean ok = false;
  try { dst.addItemStack(new @IS@(id, 1)); } catch (Throwable t) { }
  ok = countIn(dst, id) > b0;
  if (ok) return slot;
  if (!put(u, k, id, slot)) {
    @SIC@.addOrDropItemStack(st, ref, dst, new @IS@(id, 1));
    @PKG@.SackPool.warn("bench: " + id + " could not go back into the Accessory Bag of " + k + " - dropped at the player instead");
  }
  if (why != null) why.append('x');
  return -2;
}'''), acl))
# BENCH: before the vanilla handler - every accessory input of the recipe the inventory lacks for `crafts` crafts and the bag holds is moved
# into the inventory. Returns the moves: Object[]{ id, Integer bag slot, Integer inventory count before the moves of that id }
acl.addMethod(CtNewMethod.make(jt(r'''
public static java.util.ArrayList pullFor(@PLA@ p, @ST@ st, @REF@ ref, java.util.UUID u, String k, @CRR@ r, int crafts, StringBuilder why) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (p == null || r == null || k == null) return out;
  @MQ@[] in = r.getInput();
  if (in == null) return out;
  String[] ids = null;
  @IC@ inv = p.getInventory().getCombinedStorageHotbarBackpack();
  java.util.LinkedHashMap per = new java.util.LinkedHashMap();   // review fix A5: the need summed per item id
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null || in[i].getItemId() == null) continue;
    Integer c0 = (Integer) per.get(in[i].getItemId());
    per.put(in[i].getItemId(), Integer.valueOf((c0 == null ? 0 : c0.intValue()) + in[i].getQuantity()));
  }
  java.util.Iterator pi = per.entrySet().iterator();
  while (pi.hasNext()) {
    java.util.Map.Entry pe = (java.util.Map.Entry) pi.next();
    String id = (String) pe.getKey();
    if (ids == null) ids = list(u, k);
    int inBag = 0;
    for (int j = 0; j < ids.length; j++) if (ids[j].equals(id)) inBag++;
    if (inBag == 0) continue;
    long need = (long) ((Integer) pe.getValue()).intValue() * (long) crafts;
    int base = countIn(inv, id);
    long have = (long) base;
    while (have < need && inBag > 0) {
      int slot = pull(p, st, ref, u, k, id, why);
      if (slot < 0) break;
      out.add(new Object[] { id, Integer.valueOf(slot), Integer.valueOf(base) });
      have++;
      inBag--;
    }
  }
  return out;
}'''), acl))
# BENCH, after the vanilla handler (AccSettle): what the craft did not use goes back into the bag (newest first; the inventory count above
# the count before the moves); the bag refuses = it stays in the inventory. Returns how many went back
acl.addMethod(CtNewMethod.make(jt(r'''
public static int settle(@PLA@ p, @ST@ st, @REF@ ref, java.util.UUID u, String k, java.util.ArrayList pulled) {
  if (pulled == null || pulled.isEmpty() || p == null) return 0;
  @IC@ dst = p.getInventory().getCombinedStorageHotbarBackpack();
  int back = 0;
  for (int i = pulled.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) pulled.get(i);
    String id = (String) e[0];
    int base = ((Integer) e[2]).intValue();
    if (countIn(dst, id) <= base) continue;
    if (!removeOne(dst, id)) continue;
    if (put(u, k, id, ((Integer) e[1]).intValue())) { back++; continue; }
    @SIC@.addOrDropItemStack(st, ref, dst, new @IS@(id, 1));
  }
  return back;
}'''), acl))
# AccSettle: the world task queued behind the vanilla craft handler (FIFO) - settle() on the same player in the same world (another world =
# the moved accessory simply stays in the inventory: never lost)
aset.addInterface(pool.get("java.lang.Runnable"))
aset.addField(CtField.make(jt("public @PR@ pr;"), aset))
aset.addField(CtField.make("public java.util.UUID world;", aset))
aset.addField(CtField.make("public String key;", aset))
aset.addField(CtField.make("public java.util.ArrayList pulled;", aset))
aset.addField(CtField.make("public boolean onWorld;", aset))   # review fix A1: false = still on the scheduler (hop 1)
aset.addConstructor(CtNewConstructor.make(jt("public AccSettle(@PR@ pr, java.util.UUID w, String k, java.util.ArrayList pulled) { this.pr = pr; this.world = w; this.key = k; this.pulled = pulled; }"), aset))
aset.addMethod(CtNewMethod.make(jt(r'''
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID w = this.pr.getWorldUuid();
    if (w == null || !w.equals(this.world)) return;
    // review fix A1: hop 1 (the scheduler, 250 ms after the click) -> hop 2 on the world thread: the vanilla craft handler of that click
    // has been queued and run by then, so the put-back never comes before it
    if (!this.onWorld) {
      this.onWorld = true;
      @WLD@ wld = @UNI@.get().getWorld(w);
      if (wld != null) wld.execute(this);
      return;
    }
    @REF@ r = this.pr.getReference();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    int n = @PKG@.AccLink.settle(p, st, r, this.pr.getUuid(), this.key, this.pulled);
    @PKG@.CraftLog.line(this.key, "ACCBAG bench settle moved=" + this.pulled.size() + " back=" + n + " used=" + (this.pulled.size() - n));
    @PKG@.AccLink.touch(p);   // review fix B1: the open benches show the bag as it is now
  } catch (Throwable t) { @PKG@.SackPool.warn("bench: putting unused accessories back into the Accessory Bag failed: " + t); }
}'''), aset))
# BENCH (PreCraftTask, world thread, before the vanilla handler of a CraftRecipeAction): an instant bench (SimpleCraftingWindow) only
acl.addMethod(CtNewMethod.make(jt(r'''
public static int benchPre(@PLA@ p, @PR@ pr, @ST@ st, @REF@ ref, int winId, String recipeId, int qty) {
  if (p == null || pr == null || recipeId == null || winId <= 0) return 0;
  @WM@ wm = p.getWindowManager();
  if (wm == null) return 0;
  Object w = wm.getWindow(winId);
  if (!(w instanceof @SCW@)) return 0;
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0;
  Object o = @CRR@.getAssetMap().getAsset(recipeId);
  if (!(o instanceof @CRR@)) return 0;
  StringBuilder why = new StringBuilder();
  java.util.ArrayList pulled = pullFor(p, st, ref, u, k, (@CRR@) o, qty < 1 ? 1 : qty, why);
  if (why.length() > 0) pr.sendMessage(@MSG@.raw("[SkyyVoid] Make room in your inventory - the bench could not take the accessory out of your Accessory Bag."));
  if (pulled.isEmpty()) return 0;
  StringBuilder ids = new StringBuilder();
  for (int i = 0; i < pulled.size(); i++) { Object[] e = (Object[]) pulled.get(i); ids.append(' ').append(e[0]).append("@slot").append(e[1]); }
  // review fix A2 / B3: the move is in crafts.log (bag saved -> inventory; a crash in between can be reconciled from this line)
  @PKG@.CraftLog.line(k, "ACCBAG bench " + recipeId + " x" + qty + " moved from the bag to the inventory:" + ids);
  java.util.UUID wu = pr.getWorldUuid();
  @PKG@.AccSettle as = new @PKG@.AccSettle(pr, wu, k, pulled);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(as, 250L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) {
    as.onWorld = true;
    @WLD@ wld = wu == null ? null : @UNI@.get().getWorld(wu);
    if (wld == null) settle(p, st, ref, u, k, pulled); else wld.execute(as);
  }
  return pulled.size();
}'''), acl))

# ================= LinkRec (0.7.12): one open crafting window's link state (identity: the window object) ================="""
P.rep('''# ================= LinkRec (0.7.12): one open crafting window's link state (identity: the window object) =================''', ACCLINK)

# the bench display: + the bag accessories its recipes use (the list only - never a container)
P.rep('''  @IQ@[] merged = @PKG@.BagMirror.merge(base, m.quantities());
  sec.setExtraMaterials(merged);''', '''  @IQ@[] merged = @PKG@.BagMirror.merge(base, m.quantities());
  merged = @PKG@.BagMirror.merge(merged, @PKG@.AccLink.extras(u, m.key, wanted));   // 0.8.11: the Accessory Bag (shown; moved at the click)
  rec.accSig = @PKG@.AccLink.sig(u, m.key);
  sec.setExtraMaterials(merged);''')
P.rep('''lrec.addConstructor(CtNewConstructor.make("public LinkRec(Object w) { this.win = w; this.chg = -1L; this.ver = -1; }", lrec))''', '''lrec.addField(CtField.make("public String accSig;", lrec))   # 0.8.11 review fix B1: the Accessory Bag list the window was given
lrec.addConstructor(CtNewConstructor.make("public LinkRec(Object w) { this.win = w; this.chg = -1L; this.ver = -1; }", lrec))''')
P.rep('''      stale = rec.ver != m.ver;
    }''', '''      stale = rec.ver != m.ver;
      if (!stale && !@PKG@.AccLink.sig(u, k).equals(rec.accSig == null ? "" : rec.accSig)) stale = true;   // 0.8.11 review fix B1: the bag changed
    }''')
# the bench click: PreCraftTask carries the recipe of a CraftRecipeAction; after the bag link, the accessories move
P.rep('''pct.addField(CtField.make("public int id;", pct))
''', '''pct.addField(CtField.make("public int id;", pct))
pct.addField(CtField.make("public String rid;", pct))   # 0.8.11: the CraftRecipeAction's recipe (null = a tier upgrade)
pct.addField(CtField.make("public int qty;", pct))
''')
P.rep('''    @PKG@.BenchLink.preCraft(p, pr.getUuid(), this.id);
  } catch (Throwable t) { @PKG@.BenchLink.warnOnce("precraft", "craft link: pre-craft check failed (logged once): " + t); }''', '''    @PKG@.BenchLink.preCraft(p, pr.getUuid(), this.id);
    if (this.rid != null) @PKG@.AccLink.benchPre(p, pr, st, r, this.id, this.rid, this.qty);   // 0.8.11: the Accessory Bag
  } catch (Throwable t) { @PKG@.BenchLink.warnOnce("precraft", "craft link: pre-craft check failed (logged once): " + t); }''')
P.rep('''    w.execute(new @PKG@.PreCraftTask(pr, wu, a.id));''', '''    @PKG@.PreCraftTask pt = new @PKG@.PreCraftTask(pr, wu, a.id);
    if (a.action instanceof @CRA@) { pt.rid = ((@CRA@) a.action).recipeId; pt.qty = ((@CRA@) a.action).quantity; }   // 0.8.11
    w.execute(pt);''')

# ================================================================================================ A + B + D. the craft page
CRAFT_KIT = r'''# ================= 0.8.11 CRAFTING HUB + CRAFTER LOOK (tools/sacks_0_8_11_patch.py docstring A / B / D) =================
# The kit's HubBar (kit 1.6 row) in THIS jar (cross-jar classes are not allowed); the craft page = a row shell in the Crafting hub (id
# "smithing"; SkyyMenu 0.3.31 titles it Crafting), tab "recipes" ("Crafting"). Sky theme: buttons, rows, slot frames from the kit.
assert SUI.HUB_THEME == "sky" and SUI.KIT_HUB_VERSION == "1.6" and ("smithing", "recipes", 20, "SkyySacks", "Recipes", "craft") in SUI.HUB_TABS
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True)
CP_W, CP_H = 1200, 960
CSH = SUI.hub_shell("SkyyCraft", CP_W, CP_H, "smithing", row=True)
assert CSH.body == "SkyyCraftBody" and CSH.inner_w == 1152 and CSH.inner_h == 822 and CP_H <= SUI.MAX_PAGE_H
CP_HUB_TAB, CP_HUB_LABEL, CP_HUB_ORDER, CP_HUB_ICON = "recipes", "Crafting", 5, "smithing_recipes"
assert CP_HUB_ORDER < 10, "0.8.11: Crafting is the hub's first tab (before SkyyGear's Smithing / Gear, order 10)"
CP_BODY_H = {  # the tallest body of each view - every one fits CSH.inner_h (two crafter tab rows, the search + campfire lines)
    "craft": 2 * 42 + 40 + 22 + 24 + 9 * 62 + 26 + 40,
    "proc": 2 * 42 + 22 + 26 + 22 + 18 + 22 + 42 + 42 + 7 * 62 + 26 + 40,
    "pick": 2 * 42 + 22 + 26 + 22 + 18 + 22 + 42 + 42 + 40 + 7 * 52 + 26 + 40,
    "amount": 2 * 42 + 22 + 26 + 22 + 18 + 22 + 42 + 42 + 40 + 132 + 26 + 40}
assert all(_v <= CSH.inner_h for _v in CP_BODY_H.values()), CP_BODY_H
_bst = lambda kind, **kw: SUI.theme_button_style(kind, "small", theme="sky", **kw)
_lst = lambda size, col, bold=False, align=None: SUI.text_style(size, SUI.color(col), bold=bold, halign=align)
CP_CONST = {
    "B_PRI": _bst("primary"), "B_SEC": _bst("secondary"), "B_TER": _bst("tertiary"), "B_TERON": _bst("tertiary", selected=True),
    "B_PRIDIS": _bst("primary", disabled=True), "B_SECDIS": _bst("secondary", disabled=True),
    "BG_ROW": SUI.theme_bg("row", "sky"), "BG_ROWDIM": SUI.theme_bg("inset", "sky"), "BG_SLOT": SUI.theme_bg("slot", "sky"),
    "BG_PANEL": SUI.theme_bg("panel", "sky"), "C_TRACK": SUI.color("progressTrack"), "C_FILL": SUI.color("progressFill"),
    "L_NAME": _lst(16, "white", True), "L_NAMEDIM": _lst(16, "disabled", True), "L_HAVE": _lst(13, "have", True),
    "L_OUT": _lst(13, "outOfStock", True), "L_TIER": _lst(13, "gold", True), "L_CAP": _lst(13, "caption"),
    "L_CAPC": _lst(13, "caption", align="Center"), "L_INFO": _lst(15, "gold", True, "Center"), "L_STAT": _lst(16, "gold", True, "Center"),
    "L_TEXTC": _lst(14, "value", align="Center"), "L_HEAD": _lst(15, "gold", True), "L_OUTL": _lst(14, "outOfStock"),
    "L_TEXT": _lst(14, "value"),
    # the inline text fields (kit): the search box and the ADD FUEL amount box
    "SEARCH_MK": SUI.text_field("SkyyCSearchBox", "SkyyCSearch", w=420, h=32, placeholder="Search items - type a name and press Enter",
                                max_length=40, size=14),
    "FUEL_MK": SUI.text_field("SkyyCFuelBox", "SkyyCFuelAmt", w=240, h=32, placeholder="empty is all that fits", max_length=9, size=14),
}
for _n, _v in CP_CONST.items():
    assert '\\' not in _v and "\n" not in _v, _n
    cpg.addField(CtField.make("public static final String %s = %s;" % (_n, jlit(_v)), cpg))
for _mk in (CP_CONST["SEARCH_MK"], CP_CONST["FUEL_MK"]):
    SUI.check_markup(_mk)
SUI.check_sky_paths([_m for _p, _m in CSH.appends] + [CP_CONST[_k] for _k in CP_CONST if _k.startswith(("B_", "BG_"))])
CP_SHELL = CSH.java("b")
CP_HUBBUILD = SUI.java_hub_build(CSH, CP_HUB_TAB, cls="@PKG@.HubBar")
# 0.8.11 fields: the ADD FUEL picker state (per page instance)
for _d in ("public boolean fuelPick;", "public String fuelSel;", "public int fuelPage;", "public String[] fuelList;"):
    cpg.addField(CtField.make(_d, cpg))
# a sky TextButton (small, 32 high; top = its offset in a taller row) and an empty Label (its Text by b.set: any character is safe)
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String btn(String id, String text, int w, int top, String st) {
  return "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: 32" + (top > 0 ? ", Top: " + top : "") + "); Padding: (Horizontal: 10); Text: \"" + @PKG@.SacksPage.safe(text) + "\"; " + st + " }";
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String lbl(String id, int w, int h, String st) {
  return "Label #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; Style: " + st + "; }";
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String gap(int w) {
  return "Group { Anchor: (Width: " + w + "); }";
}"""), cpg))
'''
P.rep('''# ================= CraftPage (inventory crafting v1: Fieldcraft + bench accessories + collection unlocks) =================
''', CRAFT_KIT + '''
# ================= CraftPage (inventory crafting v1: Fieldcraft + bench accessories + collection unlocks) =================
''')

# ---- D. the fuel load of N items (several mirror rebuilds when the Void holds more than the mirror offers at once); the quick bar = 64
OLD_FUEL = block('''cpg.addMethod(CtNewMethod.make(f"""
public static String procFuel(''', '''}}""", cpg))
''')
P.rep(OLD_FUEL, r'''# 0.8.11 ADD FUEL: up to `want` items of one fuel into the fuel slot (room = FUEL_CAP - loaded), taken from the inventory + the Void through
# materialsFor (counted before / after each removal, booked by BagMirror.sync), in rounds while the mirror offers less than asked
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String procFuelN(@PLA@ p, @ST@ st, @REF@ ref, String k, String bench, String id, int want) {
  if (@PKG@.ProcStore.BROKEN.containsKey(k)) return "your " + bench + " data could not be loaded - nothing was taken";
  if (@PKG@.ProcBench.fuelQuality(id) <= 0.0) return pretty(id) + " does not burn";
  @PKG@.ProcBench pb = @PKG@.ProcStore.of(k, bench);
  pb.advance(System.currentTimeMillis());
  int room = @PKG@.ProcBench.FUEL_CAP - pb.fuelCount();
  if (room <= 0) return "the fuel slot is full (" + @PKG@.ProcBench.FUEL_CAP + " items)";
  int goal = want < room ? want : room;
  if (goal <= 0) return "nothing to load";
  @MQ@ one = new @MQ@(id, (String) null, (String) null, 1, (org.bson.BsonDocument) null);
  int loaded = 0; int consumed = 0; int rounds = 0;
  StringBuilder audit = new StringBuilder();
  while (loaded < goal && rounds < 200) {
    rounds++;
    @CIC@ mats = materialsFor(p, k, java.util.Collections.singleton(id));
    int have = mats.countRemovableMaterial(one);
    int n = goal - loaded;
    if (n > have) n = have;
    if (n <= 0) break;
    java.util.ArrayList l = new java.util.ArrayList();
    l.add(new @MQ@(id, (String) null, (String) null, n, (org.bson.BsonDocument) null));
    if (!mats.canRemoveMaterials(l)) break;
    int before = mats.countRemovableMaterial(one);
    mats.removeMaterials(l);
    int after = mats.countRemovableMaterial(one);
    int took = before - after;
    if (took < 0) took = 0;
    if (took > n) took = n;
    if (took > 0) pb.addFuel(id, took);
    loaded += took;
    consumed += @PKG@.BagMirror.of(k).sync();
    audit.append(' ').append(before).append("->").append(after);
    if (took <= 0) break;
  }
  saveSoon(k);
  @PKG@.CraftLog.line(k, "FUEL " + bench + " " + id + " asked=" + want + " room=" + room + " loaded=" + loaded + " fromBags=" + consumed + " counts" + audit);
  return loaded > 0 ? ("loaded " + loaded + " " + pretty(id) + " into the " + bench + (consumed > 0 ? " - " + consumed + " from the Void" : "")) : ("you have no " + pretty(id));
}"""), cpg))
# the quick-load bar (kept as it is, Skyy "but keep the quick load bar we currently have."): up to 64 of that fuel
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String procFuel(@PLA@ p, @ST@ st, @REF@ ref, String k, String bench, String id) {
  return procFuelN(p, st, ref, k, bench, id, 64);
}"""), cpg))
# how many of one fuel the player owns: the inventory + the Void (the settled key only)
cpg.addMethod(CtNewMethod.make(jt(r"""
public static long fuelHave(@PLA@ p, String k, String id) {
  long n = (long) countItem(p.getInventory().getCombinedBackpackStorageHotbar(), id);
  if (k != null) n += @PKG@.SackPool.get(k, id);
  return n;
}"""), cpg))
# ADD FUEL's list (Skyy "sort it by how much you have. so if you have 1000 sticks they will show up first in the list."): every fuel the player
# owns, Object[]{ id, Long have }, most first, then by name
cpg.addMethod(CtNewMethod.make(jt(r"""
public static java.util.ArrayList fuelsOwned(@PLA@ p, String k) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList fl = @PKG@.ProcBench.fuels();
  for (int i = 0; i < fl.size(); i++) {
    String fid = (String) fl.get(i);
    long h = fuelHave(p, k, fid);
    if (h > 0L) out.add(new Object[] { fid, Long.valueOf(h), pretty(fid).toLowerCase() + " " + fid });
  }
  for (int i = 1; i < out.size(); i++) {
    Object[] cur = (Object[]) out.get(i);
    int j = i - 1;
    while (j >= 0) {
      Object[] pv = (Object[]) out.get(j);
      long a = ((Long) pv[1]).longValue(); long b = ((Long) cur[1]).longValue();
      boolean after = a < b || (a == b && ((String) pv[2]).compareTo((String) cur[2]) > 0);
      if (!after) break;
      out.set(j + 1, pv);
      j--;
    }
    out.set(j + 1, cur);
  }
  return out;
}"""), cpg))
''')

# ---- B. the recipe row, the fuel picker, the Furnace / Tannery view (replaces 0.7.3's buildProc)
OLD_BUILDPROC = block('''cpg.addMethod(CtNewMethod.make(f"""
public void buildProc(''', '''}}""", cpg))
''')
P.rep(OLD_BUILDPROC, r'''# 0.8.11 (Skyy "upgrade the look of the crafter"): ONE recipe row - the output in a sky slot frame + its name (and the tier tag) over one chip
# per input (its item icon + have / need, green / red; up to 4 inputs (3 on a timed tab) also name the input), then Craft / Queue (Primary),
# x10, All N - the Disabled look and no binding when nothing can be made. Events unchanged: craft:<i>:<n> / pq:<i>:<n>.
cpg.addMethod(CtNewMethod.make(jt(r"""
public void drawRow(@UCB@ b, @UEB@ ev, int i, @CRR@ r, @CIC@ mats, int lim, String note, int allN, boolean timed, String each) {
  @MQ@ outq = r.getPrimaryOutput();
  String outId = outq == null ? "?" : outq.getItemId();
  String rid = "SkyyCRow" + i;
  b.appendInline("#SkyyCraftBody", "Group #" + rid + " { Anchor: (Height: 58, Bottom: 4); LayoutMode: Left; Padding: (Horizontal: 8); Background: " + (lim > 0 ? BG_ROW : BG_ROWDIM) + "; }");
  b.appendInline("#" + rid, "Group { Anchor: (Width: 50, Height: 50, Top: 4); Padding: (Full: 3); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: 44, Height: 44); ItemId: \"" + @PKG@.SacksPage.safe(outId) + "\"; } }");
  b.appendInline("#" + rid, gap(10));
  b.appendInline("#" + rid, "Group #SkyyCTxt" + i + " { Anchor: (Width: 730, Height: 58); LayoutMode: Top; Padding: (Top: 3); }");
  b.appendInline("#SkyyCTxt" + i, "Group #SkyyCHd" + i + " { Anchor: (Height: 24); LayoutMode: Left; }");
  b.appendInline("#SkyyCHd" + i, lbl("SkyyCName" + i, 586, 24, lim > 0 ? L_NAME : L_NAMEDIM));
  b.set("#SkyyCName" + i + ".Text", pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "") + (note == null ? "" : note));
  String tt = @PKG@.RecipeCmp.tierText(outId);
  if (tt.length() > 0) {
    b.appendInline("#SkyyCHd" + i, lbl("SkyyCTier" + i, 140, 24, L_TIER));
    b.set("#SkyyCTier" + i + ".Text", tt);
  }
  b.appendInline("#SkyyCTxt" + i, "Group #SkyyCIn" + i + " { Anchor: (Height: 28); LayoutMode: Left; }");
  @MQ@[] in = r.getInput();
  int n = 0;
  for (int q = 0; in != null && q < in.length; q++) if (in[q] != null) n++;
  boolean wide = n <= (timed ? 3 : 4);
  int max = wide ? n : (timed ? 5 : 6);
  int shown = 0;
  for (int q = 0; in != null && q < in.length && shown < max; q++) {
    if (in[q] == null) continue;
    int have = mats.countRemovableMaterial(in[q]);
    int need = in[q].getQuantity();
    String iid = in[q].getItemId();
    String nm = iid != null ? pretty(iid) : (in[q].getResourceTypeId() != null ? @PKG@.SackDefs.rtName(in[q].getResourceTypeId()) : "?");
    String cid = "SkyyCC" + i + "x" + q;
    if (iid != null) b.appendInline("#SkyyCIn" + i, "ItemIcon { Anchor: (Width: 26, Height: 26); ItemId: \"" + @PKG@.SacksPage.safe(iid) + "\"; }");
    b.appendInline("#SkyyCIn" + i, lbl(cid, (wide ? 144 : 74) + (iid == null ? 26 : 0), 26, have >= need ? L_HAVE : L_OUT));
    b.set("#" + cid + ".Text", " " + ((wide || iid == null) ? nm + " " : "") + @PKG@.SacksPage.shortNum((long) have) + "/" + need);
    b.appendInline("#SkyyCIn" + i, gap(8));
    shown++;
  }
  if (shown < n) {
    b.appendInline("#SkyyCIn" + i, lbl("SkyyCMore" + i, 50, 26, L_CAP));
    b.set("#SkyyCMore" + i + ".Text", "+" + (n - shown));
  }
  if (timed) {
    b.appendInline("#SkyyCIn" + i, lbl("SkyyCEach" + i, 110, 26, L_CAP));
    b.set("#SkyyCEach" + i + ".Text", each == null ? "" : each);
  }
  b.appendInline("#" + rid, gap(8));
  boolean ok = allN > 0;
  String bid = timed ? "SkyyPQ" : "SkyyCCraft";
  String tid = timed ? "SkyyPTen" : "SkyyCTen";
  String aid = timed ? "SkyyPAll" : "SkyyCAll";
  b.appendInline("#" + rid, btn(bid + i, timed ? "Queue" : "Craft", 120, 13, ok ? B_PRI : B_PRIDIS));
  b.appendInline("#" + rid, gap(6));
  b.appendInline("#" + rid, btn(tid + i, "x10", 70, 13, ok ? B_SEC : B_SECDIS));
  b.appendInline("#" + rid, gap(6));
  b.appendInline("#" + rid, btn(aid + i, "All " + allN, 110, 13, ok ? B_SEC : B_SECDIS));
  if (ok) {
    String a0 = timed ? "pq:" : "craft:";
    ev.addEventBinding(@BT@.Activating, "#" + bid + i, @EVD@.of("a", a0 + i + ":1"));
    ev.addEventBinding(@BT@.Activating, "#" + tid + i, @EVD@.of("a", a0 + i + ":10"));
    ev.addEventBinding(@BT@.Activating, "#" + aid + i, @EVD@.of("a", a0 + i + ":0"));
  }
}"""), cpg))
# the result line + the pager (+ the page's own toggles): every view ends with it
cpg.addMethod(CtNewMethod.make(jt(r"""
public void foot(@UCB@ b, @UEB@ ev, int pageNo, int pages, boolean only, boolean craftOnly, boolean refresh) {
  b.appendInline("#SkyyCraftBody", lbl("SkyyCInfo", 1152, 26, L_INFO));
  b.set("#SkyyCInfo.Text", this.info == null ? "" : this.info);
  b.appendInline("#SkyyCraftBody", "Group #SkyyCNav { Anchor: (Height: 36, Top: 4); LayoutMode: Left; }");
  b.appendInline("#SkyyCNav", btn("SkyyCPrev", "< Prev", 120, 0, pageNo > 0 ? B_SEC : B_SECDIS));
  b.appendInline("#SkyyCNav", lbl("SkyyCPage", 200, 32, L_CAPC));
  b.set("#SkyyCPage.Text", "Page " + (pageNo + 1) + " / " + pages);
  b.appendInline("#SkyyCNav", btn("SkyyCNext", "Next >", 120, 0, pageNo < pages - 1 ? B_SEC : B_SECDIS));
  if (pageNo > 0) ev.addEventBinding(@BT@.Activating, "#SkyyCPrev", @EVD@.of("a", "prev"));
  if (pageNo < pages - 1) ev.addEventBinding(@BT@.Activating, "#SkyyCNext", @EVD@.of("a", "next"));
  if (craftOnly) {
    b.appendInline("#SkyyCNav", gap(40));
    b.appendInline("#SkyyCNav", btn("SkyyCOnly", "Craftable only " + (only ? "ON" : "OFF"), 230, 0, only ? B_TERON : B_TER));
    ev.addEventBinding(@BT@.Activating, "#SkyyCOnly", @EVD@.of("a", "onlyc"));
  }
  if (refresh) {
    b.appendInline("#SkyyCNav", gap(8));
    b.appendInline("#SkyyCNav", btn("SkyyPRefresh", "Refresh", 130, 0, B_SEC));
    ev.addEventBinding(@BT@.Activating, "#SkyyPRefresh", @EVD@.of("a", "prefresh"));
  }
}"""), cpg))
# D. ADD FUEL (Skyy "id add an add fuel button which pops up a selector. you pick which fuel from the list of what you have. then type in a
# number."): the list (most first, 7 a page, Pick) -> the amount (empty = all that fits; max = what you have / the room) -> LOAD
cpg.addMethod(CtNewMethod.make(jt(r"""
public void fuelPicker(@UCB@ b, @UEB@ ev, @PLA@ p, String k, String bench, @PKG@.ProcBench view) {
  int room = @PKG@.ProcBench.FUEL_CAP - view.fuelCount();
  if (room < 0) room = 0;
  java.util.ArrayList owned = fuelsOwned(p, k);
  long selHave = 0L;
  for (int i = 0; this.fuelSel != null && i < owned.size(); i++) {
    Object[] e = (Object[]) owned.get(i);
    if (this.fuelSel.equals(e[0])) selHave = ((Long) e[1]).longValue();
  }
  if (this.fuelSel != null && selHave <= 0L) this.fuelSel = null;
  b.appendInline("#SkyyCraftBody", "Group #SkyyPFHead { Anchor: (Height: 36, Bottom: 4); LayoutMode: Left; }");
  b.appendInline("#SkyyPFHead", lbl("SkyyPFTitle", 880, 32, L_HEAD));
  if (this.fuelSel != null) {
    long max = selHave < (long) room ? selHave : (long) room;
    b.set("#SkyyPFTitle.Text", "Add " + pretty(this.fuelSel) + " to the " + bench);
    b.appendInline("#SkyyPFHead", btn("SkyyPFBack", "< Back", 130, 0, B_SEC));
    ev.addEventBinding(@BT@.Activating, "#SkyyPFBack", @EVD@.of("a", "pfback"));
    b.appendInline("#SkyyCraftBody", "Group #SkyyPFSel { Anchor: (Height: 128, Bottom: 4); LayoutMode: Left; Padding: (Full: 12); Background: " + BG_PANEL + "; }");
    b.appendInline("#SkyyPFSel", "Group { Anchor: (Width: 96, Height: 96); Padding: (Full: 6); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: 84, Height: 84); ItemId: \"" + @PKG@.SacksPage.safe(this.fuelSel) + "\"; } }");
    b.appendInline("#SkyyPFSel", gap(16));
    b.appendInline("#SkyyPFSel", "Group #SkyyPFCol { Anchor: (Width: 980, Height: 104); LayoutMode: Top; }");
    b.appendInline("#SkyyPFCol", lbl("SkyyPFName", 980, 28, L_NAME));
    b.set("#SkyyPFName.Text", pretty(this.fuelSel));
    b.appendInline("#SkyyPFCol", lbl("SkyyPFHave", 980, 26, L_TEXT));
    b.set("#SkyyPFHave.Text", "You have " + @PKG@.SacksPage.num(selHave) + " (inventory + the Void). Room in the fuel slot: " + @PKG@.SacksPage.num((long) room) + ".");
    b.appendInline("#SkyyPFCol", "Group #SkyyPFAmtRow { Anchor: (Height: 40, Top: 6); LayoutMode: Left; }");
    b.appendInline("#SkyyPFAmtRow", FUEL_MK);
    b.appendInline("#SkyyPFAmtRow", gap(10));
    b.appendInline("#SkyyPFAmtRow", btn("SkyyPFLoad", "Load", 140, 0, max > 0L ? B_PRI : B_PRIDIS));
    b.appendInline("#SkyyPFAmtRow", gap(12));
    b.appendInline("#SkyyPFAmtRow", lbl("SkyyPFMax", 400, 32, L_CAP));
    b.set("#SkyyPFMax.Text", max > 0L ? ("up to " + @PKG@.SacksPage.num(max) + " - empty loads all of them") : "the fuel slot is full");
    if (max > 0L) {
      ev.addEventBinding(@BT@.Activating, "#SkyyPFLoad", @EVD@.of("a", "pfload").append("@FuelAmt", "#SkyyCFuelAmt.Value"));
      ev.addEventBinding(@BT@.Validating, "#SkyyCFuelAmt", @EVD@.of("a", "pfload").append("@FuelAmt", "#SkyyCFuelAmt.Value"), false);
    }
    foot(b, ev, 0, 1, false, false, false);
    return;
  }
  b.set("#SkyyPFTitle.Text", "Pick a fuel - most first (your inventory + the Void)");
  b.appendInline("#SkyyPFHead", btn("SkyyPFCancel", "Cancel", 130, 0, B_SEC));
  ev.addEventBinding(@BT@.Activating, "#SkyyPFCancel", @EVD@.of("a", "pfcancel"));
  int per = 7;
  int pages = (owned.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.fuelPage >= pages) this.fuelPage = pages - 1;
  if (this.fuelPage < 0) this.fuelPage = 0;
  int start = this.fuelPage * per;
  this.fuelList = new String[per];
  for (int j = 0; j < per && start + j < owned.size(); j++) {
    Object[] e = (Object[]) owned.get(start + j);
    String fid = (String) e[0];
    this.fuelList[j] = fid;
    String rid = "SkyyPFRow" + j;
    b.appendInline("#SkyyCraftBody", "Group #" + rid + " { Anchor: (Height: 48, Bottom: 4); LayoutMode: Left; Padding: (Horizontal: 8); Background: " + BG_ROW + "; }");
    b.appendInline("#" + rid, "Group { Anchor: (Width: 42, Height: 42, Top: 3); Padding: (Full: 3); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: 36, Height: 36); ItemId: \"" + @PKG@.SacksPage.safe(fid) + "\"; } }");
    b.appendInline("#" + rid, gap(12));
    b.appendInline("#" + rid, lbl("SkyyPFN" + j, 640, 48, L_NAME));
    b.set("#SkyyPFN" + j + ".Text", pretty(fid));
    b.appendInline("#" + rid, lbl("SkyyPFC" + j, 300, 48, L_HAVE));
    b.set("#SkyyPFC" + j + ".Text", "x " + @PKG@.SacksPage.num(((Long) e[1]).longValue()));
    b.appendInline("#" + rid, btn("SkyyPFPick" + j, "Pick", 120, 8, B_PRI));
    ev.addEventBinding(@BT@.Activating, "#SkyyPFPick" + j, @EVD@.of("a", "pfpick:" + j));
  }
  if (owned.isEmpty()) {
    b.appendInline("#SkyyCraftBody", lbl("SkyyPFNone", 1152, 30, L_TEXTC));
    b.set("#SkyyPFNone.Text", "No fuel on you or in the Void - logs, planks, sticks and charcoal burn.");
  }
  foot(b, ev, this.fuelPage, pages, false, false, false);
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public void buildProc(@UCB@ b, @UEB@ ev, @PLA@ p, java.util.UUID u, String k) {
  String bench = this.tab.substring(2);
  int tier = accTier(accessories(p, u), bench);
  boolean broken = @PKG@.ProcStore.BROKEN.containsKey(k);
  @PKG@.ProcBench pb = @PKG@.ProcStore.get(k, bench);
  if (pb != null && pb.advance(System.currentTimeMillis()) > 0) @PKG@.ProcStore.markDirty(k);
  @PKG@.ProcBench view = pb != null ? pb : new @PKG@.ProcBench(bench);
  String[] d = view.describe(tier, tier > 0);
  String stat = broken ? ("Your " + bench + " file could not be read - it was left untouched. Tell an admin.") : d[0];
  b.appendInline("#SkyyCraftBody", lbl("SkyyPStat", 1152, 26, L_STAT));
  b.set("#SkyyPStat.Text", stat);
  b.appendInline("#SkyyCraftBody", lbl("SkyyPProg", 1152, 22, L_TEXTC));
  b.set("#SkyyPProg.Text", d[1]);
  int pct = 0;
  try { pct = Integer.parseInt(d[4]); } catch (Throwable t) { }
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  int fw = pct * 1100 / 100;
  b.appendInline("#SkyyCraftBody", "Group #SkyyPBarRow { Anchor: (Height: 18); LayoutMode: Left; Padding: (Left: 26, Top: 4); }");
  b.appendInline("#SkyyPBarRow", "Group #SkyyPBar { Anchor: (Width: 1100, Height: 10); LayoutMode: Left; Background: " + C_TRACK + "; }");
  if (fw > 0) b.appendInline("#SkyyPBar", "Group { Anchor: (Width: " + fw + ", Height: 10); Background: " + C_FILL + "; }");
  b.appendInline("#SkyyCraftBody", lbl("SkyyPQueue", 1152, 22, L_CAPC));
  b.set("#SkyyPQueue.Text", d[2]);
  b.appendInline("#SkyyCraftBody", "Group #SkyyPOutRow { Anchor: (Height: 36, Bottom: 6, Top: 4); LayoutMode: Left; }");
  b.appendInline("#SkyyPOutRow", lbl("SkyyPOut", 540, 32, L_HAVE));
  b.set("#SkyyPOut.Text", d[3]);
  b.appendInline("#SkyyPOutRow", btn("SkyyPCollect", "Collect", 140, 0, B_PRI));
  b.appendInline("#SkyyPOutRow", gap(8));
  b.appendInline("#SkyyPOutRow", btn("SkyyPCancel", "Cancel queue", 170, 0, B_SEC));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCollect", @EVD@.of("a", "pcollect"));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCancel", @EVD@.of("a", "pcancel"));
  java.util.ArrayList raw = (tier > 0 && !broken) ? recipesFor(this.tab, u) : new java.util.ArrayList();
  @CIC@ mats = viewMats(p, k, procWanted(raw));
  this.fuelIds = new String[4];
  if (view.needsFuel) {
    b.appendInline("#SkyyPOutRow", gap(8));
    b.appendInline("#SkyyPOutRow", btn("SkyyPUnload", "Unload fuel", 160, 0, B_SEC));
    ev.addEventBinding(@BT@.Activating, "#SkyyPUnload", @EVD@.of("a", "punload"));
    b.appendInline("#SkyyCraftBody", "Group #SkyyPFuelRow { Anchor: (Height: 36, Bottom: 6); LayoutMode: Left; }");
    b.appendInline("#SkyyPFuelRow", lbl("SkyyPFuelLbl", 100, 32, L_HEAD));
    b.set("#SkyyPFuelLbl.Text", "Load fuel");
    java.util.ArrayList fl = @PKG@.ProcBench.fuels();
    java.util.ArrayList have = new java.util.ArrayList();
    for (int i = 0; i < fl.size(); i++) {
      String fid = (String) fl.get(i);
      int c = mats.countRemovableMaterial(new @MQ@(fid, (String) null, (String) null, 1, (org.bson.BsonDocument) null));
      if (c > 0) have.add(new Object[] { fid, Integer.valueOf(c) });
    }
    boolean[] used = new boolean[have.size()];
    int shown = 0;
    for (int sI = 0; sI < 4; sI++) {
      int bi = -1; int bc = 0;
      for (int i = 0; i < have.size(); i++) {
        if (used[i]) continue;
        int c = ((Integer) ((Object[]) have.get(i))[1]).intValue();
        if (c > bc) { bc = c; bi = i; }
      }
      if (bi < 0) break;
      used[bi] = true;
      String fid = (String) ((Object[]) have.get(bi))[0];
      this.fuelIds[sI] = fid;
      int n = bc < 64 ? bc : 64;
      b.appendInline("#SkyyPFuelRow", btn("SkyyPFuel" + sI, pretty(fid) + " x" + n, 196, 0, B_SEC));
      b.appendInline("#SkyyPFuelRow", gap(6));
      ev.addEventBinding(@BT@.Activating, "#SkyyPFuel" + sI, @EVD@.of("a", "pfuel:" + sI));
      shown++;
    }
    if (shown == 0) {
      b.appendInline("#SkyyPFuelRow", lbl("SkyyPNoFuel", 640, 32, L_OUTL));
      b.set("#SkyyPNoFuel.Text", "No fuel on you or in the Void - logs, planks, sticks and charcoal burn.");
      b.appendInline("#SkyyPFuelRow", gap(194));
    } else {
      b.appendInline("#SkyyPFuelRow", gap(4 + 202 * (4 - shown)));
    }
    b.appendInline("#SkyyPFuelRow", btn("SkyyPAddF", "Add fuel", 150, 0, this.fuelPick ? B_TERON : B_PRI));
    ev.addEventBinding(@BT@.Activating, "#SkyyPAddF", @EVD@.of("a", "paddf"));
  }
  if (this.fuelPick && view.needsFuel && !broken) { fuelPicker(b, ev, p, k, bench, view); return; }
  this.fuelPick = false;
  boolean only = Boolean.TRUE.equals(ONLY.get(u));
  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {
    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (only && l0 <= 0) continue;
    @MQ@ o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(@PKG@.RecipeCmp.sortKey(id0)), @PKG@.RecipeCmp.sortName(id0) });   // 0.8.11: tier, then name
  }
  java.util.Collections.sort(ent, new @PKG@.RecipeCmp());
  this.rows = new java.util.ArrayList();
  for (int i = 0; i < ent.size(); i++) this.rows.add(((Object[]) ent.get(i))[0]);
  int room = @PKG@.ProcBench.QUEUE_CAP - view.queued();
  if (room < 0) room = 0;
  int per = 7;
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
}"""), cpg))
''')

# ---- the Furnace / Tannery clicks (exact "a" values) + ADD FUEL
OLD_HANDLEPROC = block('''cpg.addMethod(CtNewMethod.make(f"""
public boolean handleProc(''', '''}}""", cpg))
''')
P.rep(OLD_HANDLEPROC, r'''cpg.addMethod(CtNewMethod.make(jt(r"""
public boolean handleProc(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, String data, String act) {
  if (this.tab == null || !this.tab.startsWith("P:")) return false;
  String bench = this.tab.substring(2);
  if (act.equals("prefresh")) { this.info = ""; rebuild(); return true; }
  if (act.equals("pcollect")) { this.info = procCollect(p, st, ref, k, bench); rebuild(); return true; }
  if (act.equals("pcancel")) { this.info = procCancel(p, st, ref, k, bench); rebuild(); return true; }
  if (act.equals("punload")) { this.info = procUnload(p, st, ref, k, bench); rebuild(); return true; }
  // 0.8.11 ADD FUEL
  if (act.equals("paddf")) { this.fuelPick = !this.fuelPick; this.fuelSel = null; this.fuelPage = 0; this.info = ""; rebuild(); return true; }
  if (act.equals("pfcancel")) { this.fuelPick = false; this.fuelSel = null; this.info = ""; rebuild(); return true; }
  if (act.equals("pfback")) { this.fuelSel = null; this.info = ""; rebuild(); return true; }
  if (act.startsWith("pfpick:")) {
    int i = -1;
    try { i = Integer.parseInt(act.substring(7)); } catch (Throwable t) { i = -1; }
    if (this.fuelList != null && i >= 0 && i < this.fuelList.length && this.fuelList[i] != null) { this.fuelSel = this.fuelList[i]; this.info = ""; }
    rebuild();
    return true;
  }
  if (act.equals("pfload")) {
    String id = this.fuelSel;
    if (id == null || !this.fuelPick) { rebuild(); return true; }
    String amt = jsonStr(data, "@FuelAmt");
    @PKG@.ProcBench pb = @PKG@.ProcStore.of(k, bench);
    pb.advance(System.currentTimeMillis());
    int room = @PKG@.ProcBench.FUEL_CAP - pb.fuelCount();
    if (room < 0) room = 0;
    long have = fuelHave(p, k, id);
    long max = have < (long) room ? have : (long) room;
    long n = @PKG@.SacksPage.parseAmt(amt, max);
    if (n == -2L) { this.info = "type a number (or leave it empty for all that fits)"; rebuild(); return true; }
    if (n > max) n = max;
    if (n <= 0L) { this.info = room <= 0 ? ("the fuel slot is full (" + @PKG@.ProcBench.FUEL_CAP + " items)") : ("you have no " + pretty(id)); rebuild(); return true; }
    this.info = procFuelN(p, st, ref, k, bench, id, (int) n);
    this.fuelPick = false;
    this.fuelSel = null;
    rebuild();
    return true;
  }
  if (act.startsWith("pfuel:")) {
    int i = -1;
    try { i = Integer.parseInt(act.substring(6)); } catch (Throwable t) { i = -1; }
    if (this.fuelIds != null && i >= 0 && i < this.fuelIds.length && this.fuelIds[i] != null) this.info = procFuel(p, st, ref, k, bench, this.fuelIds[i]);
    rebuild();
    return true;
  }
  if (act.startsWith("pq:")) {
    String[] parts = act.substring(3).split(":");
    int idx = -1; int want = 0;
    try { idx = Integer.parseInt(parts[0]); want = Integer.parseInt(parts[1]); } catch (Throwable t) { idx = -1; }
    if (this.rows != null && idx >= 0 && idx < this.rows.size()) {
      int tier = accTier(accessories(p, u), bench);
      if (tier <= 0) this.info = "equip a " + bench + " accessory to queue";
      else this.info = procQueue(p, st, ref, k, bench, tier, (@CRR@) this.rows.get(idx), want);
    }
    rebuild();
    return true;
  }
  return false;
}"""), cpg))
''')

# ---- A + B. build(): the hub row shell, the crafter's own tabs, search, rows (+ the Accessory Bag in the counts)
OLD_BUILD = block('''cpg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{''', '''}}""", cpg))
''')
P.rep(OLD_BUILD, r'''# 0.8.11: the page view's counts + the Accessory Bag's accessories the shown recipes use (a copy - never crafted from here)
cpg.addMethod(CtNewMethod.make(jt(r"""
public @CIC@ viewMatsAcc(@PLA@ p, java.util.UUID u, String k, java.util.Set wanted) {
  @CIC@ base = viewMats(p, k, wanted);
  if (this.settling) return base;
  @SIC@ ac = @PKG@.AccLink.cont(@PKG@.AccLink.list(u, k), wanted);
  return ac == null ? base : new @CIC@(new @IC@[] { base, ac });
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  if (u != null) @PKG@.ProcTask.PAGEOPEN.put(u, Boolean.TRUE);   // 0.7.18: the 1 s task keeps visiting (the profile notice)
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
@SHELL@
  @HUBBUILD@
  this.key = null;
  this.settling = false;
  if (p == null) return;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) {
    this.settling = true;
    k = @PKG@.SackPool.pkey(u);
    if (this.info == null || this.info.length() == 0) this.info = "the Void paused (profile loading or switching) - its counts come back in a moment";
  } else if (this.info != null && this.info.startsWith("the Void paused")) this.info = "";
  this.key = k;
  // 0.7.7: what this build filters with (recipesFor / searchRecipes / buildTabs read these fields)
  this.known = @PKG@.KnowSync.known(p);
  this.coll = collectionRecipes(u);
  // 0.7.15: the Omni joins the Collections tab only while it is unlocked (all five Legendary bag recipes) AND every Legendary bag is carried
  this.omniOk = @PKG@.SweepTask.legendCount(p.getInventory()) >= @PKG@.SackDefs.CATS.length && @PKG@.KnowSync.omniUnlocked(this.coll);
  this.tabs = buildTabs(p, u, k);
  boolean known = false;
  for (int i = 0; this.tab != null && i < this.tabs.size(); i++) if (this.tab.equals(((String[]) this.tabs.get(i))[0])) known = true;
  if (!known && this.tabs.size() > 0) { this.tab = ((String[]) this.tabs.get(0))[0]; this.pageNo = 0; }
  boolean searching = this.query != null && this.query.length() > 0 && this.tab != null && this.tab.startsWith("A:");
  // the crafter's own tabs (the vanilla tab rule: the active one Primary, the others Secondary) after "< The Void"
  int tabRow = 0; int inRow = 0;
  b.appendInline("#SkyyCraftBody", "Group #SkyyCTabs0 { Anchor: (Height: 36, Bottom: 6); LayoutMode: Left; }");
  b.appendInline("#SkyyCTabs0", btn("SkyyCBags", "< The Void", 130, 0, B_TER));
  b.appendInline("#SkyyCTabs0", gap(8));
  ev.addEventBinding(@BT@.Activating, "#SkyyCBags", @EVD@.of("a", "bags"));
  for (int i = 0; i < this.tabs.size(); i++) {
    int cap = tabRow == 0 ? 8 : 9;
    if (inRow >= cap) { tabRow++; inRow = 0; b.appendInline("#SkyyCraftBody", "Group #SkyyCTabs" + tabRow + " { Anchor: (Height: 36, Bottom: 6); LayoutMode: Left; }"); }
    String[] t = (String[]) this.tabs.get(i);
    boolean sel = t[0].equals(this.tab) && !searching;
    if (inRow > 0) b.appendInline("#SkyyCTabs" + tabRow, gap(6));
    b.appendInline("#SkyyCTabs" + tabRow, btn("SkyyCTab" + i, t[1], 120, 0, sel ? B_PRI : B_SEC));
    ev.addEventBinding(@BT@.Activating, "#SkyyCTab" + i, @EVD@.of("a", "tab:" + i));
    inRow++;
  }
  // 0.7.3 search row (Crafting / Artifacts / Smithing / Farming): the kit TextField; Enter (Validating) or Search sends "@SearchQuery"
  boolean srow = false;
  if (this.tab != null && this.tab.startsWith("A:") && (@PKG@.SackCfg.SEARCH.get() || searching)) {
    srow = true;
    b.appendInline("#SkyyCraftBody", "Group #SkyyCSearchRow { Anchor: (Height: 34, Bottom: 6); LayoutMode: Left; }");
    if (@PKG@.SackCfg.SEARCH.get()) {
      b.appendInline("#SkyyCSearchRow", SEARCH_MK);
      if (searching) b.set("#SkyyCSearch.Value", this.query);
      b.appendInline("#SkyyCSearchRow", gap(8));
      b.appendInline("#SkyyCSearchRow", btn("SkyyCSearchGo", "Search", 120, 0, B_SEC));
      b.appendInline("#SkyyCSearchRow", gap(6));
      ev.addEventBinding(@BT@.Validating, "#SkyyCSearch", @EVD@.of("a", "csearch").append("@SearchQuery", "#SkyyCSearch.Value"), false);
      ev.addEventBinding(@BT@.Activating, "#SkyyCSearchGo", @EVD@.of("a", "csearch").append("@SearchQuery", "#SkyyCSearch.Value"));
    }
    b.appendInline("#SkyyCSearchRow", btn("SkyyCSearchClear", "Clear", 110, 0, B_TER));
    ev.addEventBinding(@BT@.Activating, "#SkyyCSearchClear", @EVD@.of("a", "cclear"));
    b.appendInline("#SkyyCSearchRow", gap(12));
    b.appendInline("#SkyyCSearchRow", lbl("SkyyCSearchInfo", 460, 32, L_CAP));
  }
  b.appendInline("#SkyyCraftBody", lbl("SkyyCMatNote", 1152, 22, L_CAPC));
  b.set("#SkyyCMatNote.Text", (@PKG@.SackPool.bridge().get("acc:fn:bag") instanceof java.util.function.Function) ? "Materials come from your inventory, the Void and your Accessory Bag - sorted by tier." : "Materials come from your inventory and the Void - sorted by tier.");
  // 0.7.4 Campfire tab: the emergency-cook line
  boolean campTab = this.tab != null && this.tab.equals("K:camp");
  if (campTab) {
    b.appendInline("#SkyyCraftBody", lbl("SkyyCCampNote", 1152, 24, L_STAT));
    b.set("#SkyyCCampNote.Text", campNote());
  }
  if (this.tab != null && this.tab.startsWith("P:")) { buildProc(b, ev, p, u, k); return; }
  this.fuelPick = false;
  this.fuelSel = null;
  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : (searching ? searchRecipes(u, this.query) : recipesFor(this.tab, u));
  smithNote(b, searching);   // 0.7.17: "N hidden" on the Smithing tab when gear:fn:classShow hid some
  @CIC@ mats = campTab ? viewMats(p, k, wantedOf(raw)) : viewMatsAcc(p, u, k, wantedOf(raw));   // 0.8.11: + the Accessory Bag
  boolean only = Boolean.TRUE.equals(ONLY.get(u));
  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {
    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (only && l0 <= 0) continue;
    @MQ@ o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(@PKG@.RecipeCmp.sortKey(id0)), @PKG@.RecipeCmp.sortName(id0) });   // 0.8.11: tier, then name
  }
  java.util.Collections.sort(ent, new @PKG@.RecipeCmp());
  this.rows = new java.util.ArrayList();
  for (int i = 0; i < ent.size(); i++) this.rows.add(((Object[]) ent.get(i))[0]);
  int per = 9;
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
}""".replace("@SHELL@", CP_SHELL).replace("@HUBBUILD@", CP_HUBBUILD)), cpg))
''')

# ---- the clicks: the hub bar FIRST, exact "a" values, the craft as one method (+ the Accessory Bag copy booked right after the removal)
OLD_HDE = block('''cpg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''', '''}}""", cpg))
''')
P.rep(OLD_HDE, r'''# the craft of one /craft row (world thread, inside the click): the 0.7.x checks and booking unchanged; returns the result line.
# 0.8.11: the Accessory Bag's accessories the recipe uses count through a COPY container (the limit); review fix B2: before the removal the
# ones the craft needs leave the bag (AccLink.takeFor - refused = nothing used), the removal uses exactly those, the unused ones go back
cpg.addMethod(CtNewMethod.make(jt(r"""
public String craftOne(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, @CRR@ r, int want, boolean campTab) {
  if (campTab && (campfireTier(u) <= 0 || !campfireRecipe(r) || !tableOnly(r))) return "equip the Campfire accessory in your accessory bag to cook here";
  boolean okR = true;
  if ("C:".equals(this.tab)) {
    String rid = String.valueOf(r.getId());
    okR = collectionRecipes(u).contains(rid) || (rid.equals(@PKG@.SackDefs.recipeOf(@PKG@.SackDefs.OMNI)) && @PKG@.SweepTask.legendCount(p.getInventory()) >= @PKG@.SackDefs.CATS.length && @PKG@.KnowSync.omniUnlocked(collectionRecipes(u)));
  } else if (this.tab != null && this.tab.startsWith("A:")) {
    okR = @PKG@.KnowSync.allowed(r, u, @PKG@.KnowSync.known(p), collectionRecipes(u));
  }
  if (!okR) return String.valueOf(r.getId()).equals(@PKG@.SackDefs.recipeOf(@PKG@.SackDefs.OMNI)) ? @PKG@.KnowSync.omniLockText(collectionRecipes(u), @PKG@.SweepTask.legendCount(p.getInventory())) : "You have not unlocked this recipe";
  if (!hasItemOutput(r)) return "this recipe gives no item - nothing was used";
  @SIC@ accC = campTab ? null : @PKG@.AccLink.cont(@PKG@.AccLink.list(u, k), wantedOne(r));
  @CIC@ base = materialsFor(p, k, wantedOne(r));
  @CIC@ mats = accC == null ? base : new @CIC@(new @IC@[] { base, accC });
  int lim = limit(r, mats);
  int qty = want == 0 ? lim : (want < lim ? want : lim);
  if (qty <= 0) return "not enough materials";
  java.util.List inputs = @CRM@.getInputMaterials(r, qty);
  int n = inputs == null ? 0 : inputs.size();
  if (n == 0) return "this recipe has no inputs";
  if (!mats.canRemoveMaterials(inputs)) return "not enough materials";
  if (!preCraft(st, ref, r, qty)) {
    @PKG@.CraftLog.line(k, "CRAFT-REFUSED " + r.getId() + " x" + qty + " (CraftRecipeEvent$Pre cancelled - nothing used)");
    return "this craft was refused - nothing was used";
  }
  // review fix B2: the accessories the craft needs leave the bag BEFORE anything is removed (a refused take = nothing used)
  java.util.ArrayList taken = null;
  @SIC@ accT = null;
  if (accC != null) {
    taken = @PKG@.AccLink.takeFor(u, k, inputs, base);
    if (taken == null) return "your Accessory Bag changed - nothing was used";
    accT = @PKG@.AccLink.contOf(taken);
    mats = accT == null ? base : new @CIC@(new @IC@[] { base, accT });
    if (!mats.canRemoveMaterials(inputs)) { @PKG@.AccLink.unused(st, ref, p, u, k, accT, taken); return "not enough materials"; }
  }
  java.util.HashMap snapB = snapshot(mats);
  int[] before = new int[n]; int[] per = new int[n];
  for (int i = 0; i < n; i++) {
    @MQ@ mq = (@MQ@) inputs.get(i);
    before[i] = mats.countRemovableMaterial(mq);
    per[i] = mq.getQuantity() / qty; if (per[i] <= 0) per[i] = 1;
  }
  Object tx = mats.removeMaterials(inputs);
  boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();
  int[] after = new int[n]; int done = qty;
  for (int i = 0; i < n; i++) {
    after[i] = mats.countRemovableMaterial((@MQ@) inputs.get(i));
    int removed = before[i] - after[i]; if (removed < 0) removed = 0;
    int c2 = removed / per[i]; if (c2 < done) done = c2;
  }
  if (done < 0) done = 0;
  java.util.LinkedHashMap took = removedItems(snapB, snapshot(mats));
  StringBuilder audit = new StringBuilder();
  String accNote = "";
  if (taken != null && !taken.isEmpty()) {
    int back = @PKG@.AccLink.unused(st, ref, p, u, k, accT, taken);
    int fromBag = taken.size() - back;
    audit.append(" accBagTaken=").append(taken.size()).append(" accBagBack=").append(back);
    if (fromBag > 0) accNote = " (" + fromBag + " from your Accessory Bag)";
  }
  java.util.LinkedHashMap left = reserve(took, inputs, per, done);
  if (left == null) {
    int lo = 0; int hi = done - 1;
    done = 0;
    left = reserve(took, inputs, per, 0);
    while (lo <= hi) {
      int md = (lo + hi) / 2;
      java.util.LinkedHashMap l2 = reserve(took, inputs, per, md);
      if (l2 != null) { done = md; left = l2; lo = md + 1; } else hi = md - 1;
    }
  }
  for (int i = 0; i < n; i++) {
    @MQ@ mq = (@MQ@) inputs.get(i);
    String mid = mq.getItemId() != null ? mq.getItemId() : ("res:" + mq.getResourceTypeId());
    audit.append(" ").append(mid).append("=").append(before[i]).append("->").append(after[i]);
  }
  java.util.Iterator li = left.entrySet().iterator();
  while (li.hasNext()) {
    java.util.Map.Entry le = (java.util.Map.Entry) li.next();
    int back = ((Integer) le.getValue()).intValue();
    if (back <= 0) continue;
    giveBack(st, ref, p, (String) le.getKey(), back);
    audit.append(" returned ").append((String) le.getKey()).append('*').append(back);
  }
  @PKG@.BagMirror m = @PKG@.BagMirror.of(k);
  int consumed = m.sync();
  if (consumed > 0) @PKG@.SackPool.saveSoon(k);
  @MQ@[] outs = r.getOutputs();
  @MQ@ outq = r.getPrimaryOutput();
  if ((outs == null || outs.length == 0) && outq != null) outs = new @MQ@[] { outq };
  String campId = null;
  if (campTab && done > 0) campId = campCall(p, u, k, r, done);
  int campAt = -1;
  if (campId != null && outq != null && outs != null) {
    for (int pq = 0; pq < outs.length && campAt < 0; pq++) if (outs[pq] == outq) campAt = pq;
    for (int pq = 0; pq < outs.length && campAt < 0; pq++) if (outs[pq] != null && outq.getItemId() != null && outq.getItemId().equals(outs[pq].getItemId())) campAt = pq;
  }
  int given = 0;
  int gearN = 0;
  int gearDrop = 0;
  if (done > 0 && outs != null) {
    for (int q = 0; q < outs.length; q++) {
      if (outs[q] == null || outs[q].getItemId() == null) continue;
      long total = (long) outs[q].getQuantity() * (long) done; if (total > 100000L) total = 100000L;
      String gid = outs[q].getItemId();
      if (q == campAt) gid = campId;
      Object[] rolled = null;
      if (!campTab) rolled = gearRoll(u, gid, (int) total, String.valueOf(r.getId()));
      if (rolled != null) {
        @IC@ dstC = p.getInventory().getCombinedStorageHotbarBackpack();
        int beforeC = countItem(dstC, gid);
        int gotN = 0;
        for (int gi = 0; gi < rolled.length; gi++) {
          @IS@ gs = (@IS@) rolled[gi];
          @SIC@.addOrDropItemStack(st, ref, dstC, gs);
          gotN += gs.getQuantity();
        }
        if (gotN < (int) total) @SIC@.addOrDropItemStack(st, ref, dstC, new @IS@(gid, (int) total - gotN));
        int inInv = countItem(dstC, gid) - beforeC;
        if (inInv < (int) total) gearDrop += (int) total - (inInv < 0 ? 0 : inInv);
        gearN += gotN;
      } else {
        @SIC@.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(gid, (int) total));
      }
      given += (int) total;
    }
  }
  if (campTab) audit.append(" campfire=").append(campId == null ? "plain" : campId);
  if (gearN > 0) audit.append(" gear=").append(gearN);
  if (gearDrop > 0) audit.append(" gearDropped=").append(gearDrop);
  @PKG@.CraftLog.write(k, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());
  if (done > 0 && !campTab) {
    try {
      Object xf = @PKG@.SackPool.bridge().get("skill:fn:craftxp");
      if (xf instanceof java.util.function.Function) ((java.util.function.Function) xf).apply(new Object[] { u, String.valueOf(r.getId()), Integer.valueOf(done), "sacks:craft", k });
    } catch (Throwable t) { }
  }
  if (done > 0 && given == 0) @PKG@.SackPool.warn("craft: " + done + " crafts of " + r.getId() + " paid but the recipe has no item output (" + u + ")");
  String nm = pretty(outq == null ? "?" : outq.getItemId());
  if (campTab) { int cg = gradeOfId(campId); nm = nm + (cg > 0 ? " Grade " + cg : " (plain)"); }
  if (done == qty) return "crafted " + qty + " x " + nm + (consumed > 0 ? " (" + consumed + " from the Void)" : "") + accNote;
  if (done > 0) return "crafted " + done + " of " + qty + " x " + nm + " - extra materials were returned" + accNote;
  return "could not remove the materials - nothing was used";
}"""), cpg))
# a hub click that left this page open on screen is answered with a no-op update (the client's "Loading..." ends); never to a replaced page
cpg.addMethod(CtNewMethod.make(jt(r"""
public void hubAck(@REF@ ref, @ST@ st) {
  try {
    @PLA@ hp = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (hp == null || hp.getPageManager() == null || hp.getPageManager().getCustomPage() != this) return;
    @UCB@ c = new @UCB@();
    c.set("#SkyyCInfo.Text", this.info == null ? "" : this.info);
    sendUpdate(c, false);
  } catch (Throwable t) { }
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    // 0.8.11 CRAFTING HUB (kit 1.6): row 1 (Home + the hubs), the X and the hub's tabs FIRST
    String hr = null;
    try { hr = @PKG@.HubBar.route(this.playerRef, data, "smithing", "recipes"); } catch (Throwable t) { hr = null; }
    if ("close".equals(hr)) { close(); return; }
    if (hr != null) {
      if (hr.equals("self")) { rebuild(); return; }
      if (hr.equals("back") || hr.equals("bridge") || hr.equals("command")) { hubAck(ref, st); return; }
      this.info = "That tab could not open right now - try again.";
      rebuild();
      return;
    }
    String act = jsonStr(data, "a");
    // 0.7.3 search: only the search bindings carry "@SearchQuery" (the typed text)
    if (data.indexOf("\"@SearchQuery\"") >= 0) {
      this.query = cleanQuery(jsonStr(data, "@SearchQuery"));
      this.pageNo = 0;
      this.info = this.query.length() == 0 ? "type a word (for example iron or sword) and press Enter or Search" : "";
      rebuild();
      return;
    }
    if (act.equals("cclear")) { this.query = ""; this.pageNo = 0; this.info = ""; rebuild(); return; }
    if (act.equals("prev")) { if (this.fuelPick) this.fuelPage--; else this.pageNo--; rebuild(); return; }
    if (act.equals("next")) { if (this.fuelPick) this.fuelPage++; else this.pageNo++; rebuild(); return; }
    if (act.equals("onlyc")) { if (Boolean.TRUE.equals(ONLY.get(u))) ONLY.remove(u); else ONLY.put(u, Boolean.TRUE); this.pageNo = 0; rebuild(); return; }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    if (act.equals("bags")) { p.getPageManager().openCustomPage(ref, st, new @PKG@.SacksPage(this.playerRef, (String) null)); return; }
    for (int i = 0; this.tabs != null && i < this.tabs.size(); i++) {
      if (act.equals("tab:" + i)) { this.tab = ((String[]) this.tabs.get(i))[0]; this.pageNo = 0; this.info = ""; this.query = ""; this.fuelPick = false; this.fuelSel = null; rebuild(); return; }
    }
    String k = @PKG@.SackPool.settledKey(u);
    if (k == null) { this.info = "the Void paused (profile loading or switching) - try again in a moment"; rebuild(); return; }
    if (this.key != null && !this.key.equals(k)) { this.info = "your profile changed - this page now shows it"; this.pageNo = 0; this.fuelPick = false; this.fuelSel = null; rebuild(); return; }
    if (handleProc(ref, st, p, u, k, data, act)) return;
    if (!act.startsWith("craft:")) return;
    String[] parts = act.substring(6).split(":");
    int idx = -1; int want = 0;
    try { idx = Integer.parseInt(parts[0]); want = Integer.parseInt(parts[1]); } catch (Throwable t) { idx = -1; }
    if (this.rows == null || idx < 0 || idx >= this.rows.size()) return;
    @CRR@ r = (@CRR@) this.rows.get(idx);
    this.info = craftOne(ref, st, p, u, k, r, want, "K:camp".equals(this.tab));
    rebuild();
  } catch (Throwable t) { @PKG@.SackPool.warn("craft page event failed: " + t); }
}"""), cpg))
''')

# ---- A. the Crafting tab's open Function + register (after the CraftPage)
P.rep('''# ================= ProcTask (world thread, every 1s per player): advance Furnace/Tannery, notify, refresh an open Furnace/Tannery tab =================''',
      r'''# ================= 0.8.11 CraftHubOpen: hub:tab:smithing:recipes ("Crafting") - the craft page for the UUID on its world thread =================
# FALSE = the bar runs /craft instead (HUBS-CONTRACT 1). Never close-then-open: openCustomPage replaces the page on screen.
chop.addInterface(pool.get("java.util.function.Function"))
chop.addConstructor(CtNewConstructor.make("public CraftHubOpen() { }", chop))
chop.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    if (st == null) return Boolean.FALSE;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return Boolean.FALSE;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return Boolean.FALSE;
    pm.openCustomPage(r, st, new @PKG@.CraftPage(pr, (String) null));
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.SackPool.warn("the Crafting > Crafting tab could not open the craft page: " + t);
    return Boolean.FALSE;
  }
}"""), chop))
chop.addMethod(CtNewMethod.make(jt(r"""
public static int register() {
  Object[] e = @PKG@.HubBar.putIcon("smithing", "%s", "SkyySacks", "%s", %d, "craft", new @PKG@.CraftHubOpen(), null, "%s");
  return e == null ? 0 : 1;
}""" % (CP_HUB_TAB, CP_HUB_LABEL, CP_HUB_ORDER, CP_HUB_ICON)), chop))

# ================= ProcTask (world thread, every 1s per player): advance Furnace/Tannery, notify, refresh an open Furnace/Tannery tab =================''')

# setup (ready line + register), shutdown (remove), the classes written
P.rep('''  this.procTicker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.ProcTick(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - SkyyVoid:''', '''  this.procTicker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.ProcTick(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  int hubTab = 0;   // 0.8.11: the Crafting hub's Crafting tab (hub:tab:smithing:recipes)
  try {{ hubTab = {PKG}.CraftHubOpen.register(); }} catch (Throwable th) {{ {PKG}.SackPool.warn("the Crafting hub tab could not be registered - /craft still works: " + th); }}
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - SkyyVoid:''')
P.rep('''UI kit {KIT_ID}; auto-pickup " + {PKG}.PickBook.state());''', '''UI kit {KIT_ID}; auto-pickup " + {PKG}.PickBook.state() + "; Crafting hub tab " + (hubTab == 1 ? "on" : "OFF") + " (/craft, sorted by tier, Furnace Add fuel); benches + /craft use the Accessory Bag (SkyyAccessories 0.5.19 acc:fn:bag); the Void's Deposit all fills every bag");''')
P.rep('''  {PKG}.SackPool.CLOSED = true;   // 0.7.11 review fix 10: the shutdown latch (SackPool.settledKey answers null from here on)
''', '''  {PKG}.SackPool.CLOSED = true;   // 0.7.11 review fix 10: the shutdown latch (SackPool.settledKey answers null from here on)
  try {{ {PKG}.HubBar.removeAll(); }} catch (Throwable t) {{ }}   // 0.8.11: our hub tab only (keys that still hold our array)
''')
P.rep('''          smig):  # 0.8.9: SackMig089
''', '''          smig,   # 0.8.9: SackMig089
          hubb, acl, aset, chop):   # 0.8.11: HubBar (kit 1.6), AccLink, AccSettle, CraftHubOpen
''')

# the jar: the kit's 59 Sky Window files + the Crafting tab icon (art/hub-tab-icons, sha256 = its manifest)
P.rep('''jar = os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)
B.assemble(jar,''', '''# 0.8.11: the Sky Window kit art (all 59, byte-identical in every hub jar - HUBS-CONTRACT 2.7) + the smithing_recipes tab icon pair at the kit
# 1.6 hook path (the same bytes SkyyMenu 0.3.30+ ships: whichever jar loads last, the picture is the same)
import hashlib as _hl
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p for p in _kit) and not set(_kit) & set(files)
files.update(_kit)
_TAM = json.load(open(os.path.join(HERE, "..", "art", "hub-tab-icons", "manifest.json"), encoding="utf8"))
_pp = SUI.hub_tab_icon_paths("smithing", CP_HUB_TAB)
for _fn, _jp in (("%s.png" % CP_HUB_ICON, _pp[2]), ("%s_on.png" % CP_HUB_ICON, _pp[3])):
    _data = open(os.path.join(HERE, "..", "art", "hub-tab-icons", _fn), "rb").read()
    _me = [f for f in _TAM["files"] if f["path"] == _fn]
    assert len(_me) == 1 and _hl.sha256(_data).hexdigest() == _me[0]["sha256"] and len(_data) == _me[0]["bytes"], "0.8.11: %s = its manifest entry" % _fn
    assert _jp.startswith("Common/UI/Custom/SkyyHubTabs/") and _jp not in files
    files[_jp] = _data
print("0.8.11 kit art: %d Sky Window files + the Crafting tab icon pair" % len(_kit))
jar = os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)
B.assemble(jar,''')
P.rep('''    B.enable_in_world("HUD mod", "Skyy:%s SkyySacks" % VERSION, disable_prefix="Skyy:")''', '''    B.enable_in_world("HUD mod", "Skyy:%s SkyySacks" % VERSION, disable_prefix="Skyy:")
assert SUI.check_jar_kit(jar, need=("Header", "Frame_Smithing", "Row", "PanelInset", "SlotEmpty", "Primary", "Secondary", "Tertiary", "Close")) == 59''')

assert P.s.count("AccLink.") >= 9 and "AccLink.book" not in P.s and P.s.count("RecipeCmp.sortKey") == 2
P.finish()
