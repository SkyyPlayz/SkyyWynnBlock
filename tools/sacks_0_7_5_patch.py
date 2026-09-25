"""Derive SkyySacks/build_skyysacks_0.7.5.py from 0.7.4 (edit THIS file, then regenerate: python tools/sacks_0_7_5_patch.py).
0.7.5 = THE SMITHING BAG (Skyy's beta backlog, HANDOFF 2026-09-24 20:10, item 1: "SMITHING SACK holding everything for smithing
(ingots/bars, hides, leather, ...) - replaces 'bars in the Mining bag'; TREE SAP into the Foraging sack") + the bags page shows every tab
(HANDOFF "Feedback on the build round": "show all four tabs, with how to craft the missing bag"). BETA-TEST bug "Sacks still do not hold
ingots" is fixed by the Smithing bag.
 - New 5th category "Smithing" (SackDefs.CATS order Mining, Foraging, Farming, Combat, Smithing): Small / Medium / Large Smithing Bag items
   (Skyy_Sack_Smithing_Small|Medium|Large, same caps 640 / 2,240 / 20,160 per item), Workbench recipes like the other four (Small = 3 Bolt of
   Wool + 4 Light Leather; Medium = Small + 3 Bolt of Linen; Large = Medium + 3 Bolt of Silk), right-click page id SkyySacksSmithing.
 - What pools into it (catOf, checked BEFORE Combat): Ingredient_Bar_* (every bar / ingot), Ingredient_Leather_*, Ingredient_Hide_*,
   Ingredient_Bolt_* (cloth armor + bag recipes), Ingredient_Fabric_Scrap_* (weapon / armor / tool recipes), Ingredient_Strap_Leather,
   Ingredient_Stud_Iron. Research (Assets.zip: gear recipes are the inline "Recipe" -> "Input" block of each item JSON; all 188 recipes
   under Server/Item/Items/Weapon, Armor and Tool counted): bars 142 uses, leather 119, fabric scraps 65, bolts 45, hides 0 (no gear
   recipe takes hides - they become leather at the Tannery); no Assets.zip file names Ingredient_Sinue_Cindersinue ("Cindersinew")
   except its own item file, so it is not pooled. The rest of those recipe inputs are gathering drops that stay in their field's bag
   (Fibre / Stick / Tree Sap = Foraging, essences / Voidheart / Venom Sac / feathers / Boom Powder = Combat, gems / rubble = Mining,
   Life Essence / crops = Farming).
   Chitin (Ingredient_Chitin_Sturdy) STAYS in Combat: it is a Scarak / Scorpion drop used by one furniture recipe and by no weapon, armor or
   tool recipe. Hides and fabric scraps LEAVE Combat. The pool is keyed by item id, so hides / scraps already pooled under Combat simply show
   and withdraw in the Smithing tab now (no file migration); carrying a Smithing bag is needed to reach them (strict access, locked).
 - Tree sap (Ingredient_Tree_Sap - what every Tree_Sap_Glob_* drop list gives; Tree_Sap_Glob itself is the placeable glob block and is
   not pooled) pools into the Foraging bag.
 - The bags page (/pd, /sacks, /bags, right-click) ALWAYS shows all five tabs. Tabs of bags you carry keep the gold/brown style; a bag you do
   not carry has a grey tab, and selecting it shows HOW TO CRAFT it instead of its items: what it holds, the Small recipe as big item icons
   (bag = 3 Bolt of Wool + 4 <material>, at a Workbench), "You have x / 3 ... and y / 4 ..." (inventory + any bag you carry - what a
   Workbench can use), the Medium / Large upgrades and caps, and how many items already wait in that bag ("nothing is ever lost"). The old
   small "You need a magic bag" page is gone: with no bag at all the page opens on that view (first bag that has items stored, else Mining).
 - The Combat tab tells a player without a Smithing bag how many items wait in the Smithing bag (hides and fabric scraps moved there).
 - A withdraw that fails because the bag is gone now says "you need a <cat> bag on you" instead of "storage is full".
 - ONE bag table (BAG_CATS / BAG_MAT / BAG_BOLTS / BAG_HOLDS in the build script) feeds the SackDefs arrays (tab order, how-to-craft view),
   the item JSON recipes and the lang text, so the page cannot describe a recipe the item does not have. The ids and names are checked
   against Assets.zip at build time (read-only, in memory) when it is present.
Everything else in 0.7.4 is untouched: sweep / withdraw / deposit rules, caps per item, settledKey + profile:busy gates, bench mirror,
/craft tabs (Crafting, Smithing, Farming, Campfire, Furnace, Tannery, Collections), search, processing queues, Smithing XP, config.
The page root grows from 900 to 1000 wide (five tabs + Craft); every page is still inline, root anchor Width/Height only, no underscores.
Review fixes (0.7.5 review): SackPool.saveNow gets fsync + ATOMIC_MOVE (the pool file now also holds the Smithing bag); the dead
GrantTask / SackReady self-test source is removed (it was never in the jar); #SkyySNbHolds / #SkyySNbUp get room for three lines.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.4.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


def seg(start, end, must_have, new):
    """Replace s[start : end) (end exclusive, both anchors unique) after checking the old segment is the one we expect."""
    global s
    assert s.count(start) == 1, "segment start not unique: " + start[:90]
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(end) == 1, "segment end not unique: " + end[:90]
    old = s[i:j]
    for m in must_have:
        assert m in old, "segment %r lacks %r" % (start[:50], m[:80])
    s = s[:i] + new + s[j:]


# ---------------- docstring + version ----------------
rep('"""SkyySacks 0.7.4 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.4.py            -> SkyySacks/SkyySacks-0.7.4.jar' + LF
    + '       python build_skyysacks_0.7.4.py --deploy   -> also',
    '"""SkyySacks 0.7.5 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.5.py            -> SkyySacks/SkyySacks-0.7.5.jar' + LF
    + '       python build_skyysacks_0.7.5.py --deploy   -> also')
rep('recipe that gives no item is refused before materials move (every tab); Campfire-exclusive recipes only; the graded id replaces exactly' + LF
    + 'one output entry.' + LF + '"""',
    'recipe that gives no item is refused before materials move (every tab); Campfire-exclusive recipes only; the graded id replaces exactly' + LF
    + 'one output entry.' + LF
    + '0.7.5 (derived from 0.7.4 by tools/sacks_0_7_5_patch.py - edit the patch, not this file): SMITHING BAG (Skyy\'s beta backlog item 1) -' + LF
    + 'a 5th category with Small / Medium / Large Smithing Bag items and Workbench recipes; it pools every bar / ingot, leather, hide, cloth' + LF
    + 'bolt, fabric scrap, leather strap and iron stud (hides and fabric scraps leave Combat; already pooled stacks show in the Smithing tab,' + LF
    + 'the pool is keyed by item id). Tree sap pools into Foraging. The bags page always shows all five tabs: a bag you do not carry has a' + LF
    + 'grey tab that shows how to craft it (big recipe icons, your counts, upgrades, items already waiting in it). One bag table in this' + LF
    + 'script feeds the tabs, the how-to-craft view, the item recipes and the lang text (ids / names checked against Assets.zip).' + LF
    + 'Review fixes: the pool file save (SackPool.saveNow) is tmp + fsync + atomic rename like ProcStore; the never-shipped self-test grant' + LF
    + '(GrantTask / SackReady) is gone from the source; the two longest wrapped texts of the how-to-craft view have room for three lines.' + LF
    + '"""')
rep('VERSION = "0.7.4"', 'VERSION = "0.7.5"')

# ---------------- the bag table (python, before SackDefs uses it) ----------------
BAG_TABLE = r'''
# 0.7.5: THE BAG TABLE - one source for the SackDefs arrays (tab order + the "how to craft" view of a bag you do not carry), the Workbench
# recipes in the item JSON and the lang text, so the page can never describe a recipe the bag item does not have. The first four rows are
# exactly the 0.7.4 recipes; Smithing is new (Skyy's beta backlog 2026-09-24 item 1). ITEM_NAME = Assets.zip server.lang items.<id>.name.
BAG_CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")
BAG_MAT = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread", "Combat": "Ingredient_Bone_Fragment",
           "Smithing": "Ingredient_Leather_Light"}
BAG_BOLTS = ("Ingredient_Bolt_Wool", "Ingredient_Bolt_Linen", "Ingredient_Bolt_Silk")   # Small (with BAG_MAT), Medium, Large upgrade
BAG_BOLT_QTY, BAG_MAT_QTY = 3, 4
BAG_HOLDS = {"Mining": "ore, rubble, rock and soil",
             "Foraging": "logs, planks, sticks, fibre, bark and tree sap",
             "Farming": "plants, food and cooked dishes, fish and life essence",
             "Combat": "bones, feathers, essences, venom sacs, chitin, voidhearts and boom powder",
             "Smithing": "bars and ingots, leather, hides, cloth bolts, fabric scraps, leather straps and iron studs"}
ITEM_NAME = {"Ingredient_Bar_Copper": "Copper Ingot", "Wood_Oak_Trunk": "Oak Log", "Food_Bread": "Bread",
             "Ingredient_Bone_Fragment": "Bone Fragments", "Ingredient_Leather_Light": "Light Leather",
             "Ingredient_Bolt_Wool": "Bolt of Wool", "Ingredient_Bolt_Linen": "Bolt of Linen", "Ingredient_Bolt_Silk": "Bolt of Silk"}
# 0.7.5 Smithing bag contents (SackDefs.catOf, checked before Combat). Research = the inline "Recipe" -> "Input" block of all 188 item
# JSONs with a recipe under Assets.zip Server/Item/Items/Weapon, Armor and Tool: bars 142 inputs, leather 119, fabric scraps 65, cloth
# bolts 45 (cloth armor; bolts are also the bag recipes); no gear recipe takes hides - they become leather at the Tannery. Strap and
# stud are smithing parts no recipe uses yet. The other inputs of those recipes are gathering drops that stay in their field's bag;
# chitin stays Combat (no weapon, armor or tool recipe uses it). Hides and fabric scraps were Combat until 0.7.4.
SMITH_PREFIX = ("Ingredient_Bar_", "Ingredient_Leather_", "Ingredient_Hide_", "Ingredient_Bolt_", "Ingredient_Fabric_Scrap_")
SMITH_EXACT = ("Ingredient_Strap_Leather", "Ingredient_Stud_Iron")
TREE_SAP = "Ingredient_Tree_Sap"   # every Tree_Sap_Glob_* drop list gives this item -> Foraging bag
assert BAG_CATS[:4] == ("Mining", "Foraging", "Farming", "Combat") and set(BAG_MAT) == set(BAG_CATS) == set(BAG_HOLDS)
for _t in list(BAG_HOLDS.values()) + list(ITEM_NAME.values()) + list(BAG_MAT.values()) + list(BAG_BOLTS):
    assert '"' not in _t and "\\" not in _t and "\n" not in _t, _t
for _i in list(BAG_MAT.values()) + list(BAG_BOLTS):
    assert _i in ITEM_NAME, "no display name for " + _i
def _bag_ids_check():
    import zipfile, re
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - bag recipe / Smithing bag ids not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        ids = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        lang = {}
        for line in z.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
            m = re.match(r"items\.([A-Za-z0-9_]+)\.name\s*=\s*(.*)", line)
            if m:
                lang[m.group(1)] = m.group(2).strip()
    bad = [i for i in list(BAG_MAT.values()) + list(BAG_BOLTS) + list(SMITH_EXACT) + [TREE_SAP] if i not in ids]
    if bad:
        raise SystemExit("0.7.5: unknown item id(s) in the bag table: " + ", ".join(bad))
    for i, nm in sorted(ITEM_NAME.items()):
        if lang.get(i) and lang[i] != nm:
            print("WARNING: %s is called %r in server.lang but the bags page says %r - update ITEM_NAME" % (i, lang[i], nm))
    fam = []
    for p in SMITH_PREFIX:
        got = sorted(i for i in ids if i.startswith(p))
        if not got:
            raise SystemExit("0.7.5: no item id starts with " + p + " any more - re-check the Smithing bag")
        fam.append("%s* %d" % (p, len(got)))
    print("smithing bag holds: " + ", ".join(fam) + ", " + ", ".join(SMITH_EXACT) + " | tree sap -> Foraging (" + TREE_SAP + ")")
_bag_ids_check()
SMITH_JAVA = " || ".join(['itemId.startsWith("%s")' % p for p in SMITH_PREFIX] + ['itemId.equals("%s")' % i for i in SMITH_EXACT])
def _jarr(vals):
    return "new String[] { " + ", ".join('"%s"' % v for v in vals) + " }"
'''.lstrip(LF)
rep('_camp_defaults_check()' + LF + LF + 'for c, m in ((PLA, "getInventory")',
    '_camp_defaults_check()' + LF + LF + BAG_TABLE + LF + 'for c, m in ((PLA, "getInventory")')

# ---------------- SackDefs: 5 categories, Smithing + tree sap in catOf, the how-to-craft arrays ----------------
SACKDEFS = r'''# 0.7.5: category order = BAG_CATS (tabs, right-click page ids, item JSON); MAT / MATN / HOLDS / BOLT / BOLTN / MATQ / BOLTQ = the bag table
# (the "how to craft" view of a bag you do not carry reads them - same numbers as the item JSON recipes below).
defs.addField(CtField.make("public static final String[] CATS = " + _jarr(BAG_CATS) + ";", defs))
defs.addField(CtField.make("public static final String[] MAT = " + _jarr([BAG_MAT[c] for c in BAG_CATS]) + ";", defs))
defs.addField(CtField.make("public static final String[] MATN = " + _jarr([ITEM_NAME[BAG_MAT[c]] for c in BAG_CATS]) + ";", defs))
defs.addField(CtField.make("public static final String[] HOLDS = " + _jarr([BAG_HOLDS[c] for c in BAG_CATS]) + ";", defs))
defs.addField(CtField.make("public static final String[] BOLT = " + _jarr(BAG_BOLTS) + ";", defs))
defs.addField(CtField.make("public static final String[] BOLTN = " + _jarr([ITEM_NAME[b] for b in BAG_BOLTS]) + ";", defs))
defs.addField(CtField.make("public static final int MATQ = %d;" % BAG_MAT_QTY, defs))
defs.addField(CtField.make("public static final int BOLTQ = %d;" % BAG_BOLT_QTY, defs))
defs.addMethod(CtNewMethod.make("""
public static int catIndex(String cat) {
  if (cat == null) return -1;
  for (int i = 0; i < CATS.length; i++) if (CATS[i].equals(cat)) return i;
  return -1;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  // 0.7.3 (research/Cooking-Skill-Spec.md 3.4): graded dishes (the Grade is in the id, no metadata) go to the Farming bag; the
  // Skyy_Cook_Recipe_* recipe-variant items never do. A cook:prefix bridge value (SkyyCooking) is honoured when it starts with Skyy_Cook.
  if (itemId.startsWith("Skyy_")) {
    if (itemId.startsWith("Skyy_Cook_Recipe_")) return null;
    if (itemId.startsWith("Skyy_Cook_")) return "Farming";
    try {
      Object b = System.getProperties().get("skyy.bridge");
      Object p = (b instanceof java.util.Map) ? ((java.util.Map) b).get("cook:prefix") : null;
      if (p instanceof String && ((String) p).startsWith("Skyy_Cook") && itemId.startsWith((String) p)) return "Farming";
    } catch (Throwable t) { }
    return null;
  }
  if (itemId.startsWith("Ore_") || itemId.startsWith("Rubble_") || itemId.startsWith("Rock_") || itemId.startsWith("Soil_")) return "Mining";
  // 0.7.5: tree sap joins the Foraging bag
  if (itemId.startsWith("Wood_") || itemId.equals("Ingredient_Stick") || itemId.equals("Ingredient_Fibre") || itemId.equals("Ingredient_Tree_Bark") || itemId.equals("@SAP@")) return "Foraging";
  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_") || itemId.startsWith("Fish_")) return "Farming";
  if (itemId.startsWith("Ingredient_Life_Essence") || itemId.equals("Ingredient_Poop")) return "Farming";
  // 0.7.5 Smithing bag: bars / ingots, leather, hides, cloth bolts, fabric scraps, strap, stud - checked BEFORE Combat, which held hides and
  // fabric scraps until 0.7.4 (the pool is keyed by item id, so those stacks simply show in the Smithing tab now)
  if (@SMITH@) return "Smithing";
  if (itemId.startsWith("Ingredient_Bone") || itemId.startsWith("Ingredient_Chitin")
      || itemId.startsWith("Ingredient_Sac_") || itemId.startsWith("Ingredient_Feathers")
      || itemId.equals("Ingredient_Voidheart") || itemId.equals("Ingredient_Powder_Boom")
      || (itemId.startsWith("Ingredient_") && itemId.endsWith("_Essence"))) return "Combat";
  return null;
}""".replace("@SMITH@", SMITH_JAVA).replace("@SAP@", TREE_SAP), defs))
'''.lstrip(LF)
seg("defs.addField(CtField.make('public static final String[] CATS = new String[] { \"Mining\", \"Foraging\", \"Farming\", \"Combat\" };', defs))" + LF,
    'defs.addMethod(CtNewMethod.make("""' + LF + 'public static int tierCap(String tier) {',
    ['public static String catOf(String itemId) {', 'itemId.startsWith("Ingredient_Hide_")', 'itemId.startsWith("Ingredient_Fabric_Scrap_")',
     'itemId.equals("Ingredient_Tree_Bark")) return "Foraging";', 'return "Combat";'],
    SACKDEFS)

# ---------------- SacksPage: every tab, the how-to-craft view, render() split from build() ----------------
rep('page.addField(CtField.make("public String noticeKey;", page))' + LF,
    'page.addField(CtField.make("public String noticeKey;", page))' + LF
    + '# 0.7.5: true when the last build showed a bag the player carries (item grid); false = the how-to-craft view (no item buttons)' + LF
    + 'page.addField(CtField.make("public boolean carried;", page))' + LF)

PAGE = r'''# 0.7.5: every tab can be selected, carried or not (a bag you do not carry shows how to craft it). Default: a carried bag with items, a
# carried bag, a bag that has items stored, else the first category.
page.addMethod(CtNewMethod.make(f"""
public String pickCat(String k, java.util.HashMap caps) {{
  String[] cats = {PKG}.SackDefs.CATS;
  if (this.cat != null && {PKG}.SackDefs.catIndex(this.cat) >= 0) return this.cat;
  for (int c = 0; c < cats.length; c++) if (caps.containsKey(cats[c]) && {PKG}.SackPool.catTotal(k, cats[c]) > 0L) return cats[c];
  for (int c = 0; c < cats.length; c++) if (caps.containsKey(cats[c])) return cats[c];
  for (int c = 0; c < cats.length; c++) if ({PKG}.SackPool.catTotal(k, cats[c]) > 0L) return cats[c];
  return cats[0];
}}""", page))
# 0.7.5 how-to-craft helpers: 20160 -> "20,160" (set() text only - inline text goes through safe(), which drops commas)
page.addMethod(CtNewMethod.make("""
public static String num(long v) {
  String d = String.valueOf(v < 0L ? -v : v);
  StringBuilder sb = new StringBuilder();
  int n = d.length();
  for (int i = 0; i < n; i++) {
    if (i > 0 && (n - i) % 3 == 0) sb.append(',');
    sb.append(d.charAt(i));
  }
  return (v < 0L ? "-" : "") + sb.toString();
}""", page))
# how many of an item the player carries (storage + hotbar + backpack) - the same containers SweepTask.caps scans
page.addMethod(CtNewMethod.make(f"""
public static int countInv({INV} inv, String id) {{
  if (inv == null || id == null) return 0;
  int n = 0;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      if (id.equals(it.getItemId())) n += it.getQuantity();
    }}
  }}
  return n;
}}""", page))
# what a Workbench can use of an item: the inventory plus the pool when the player carries that item's bag (BagMirror feeds only those)
page.addMethod(CtNewMethod.make(f"""
public static long haveOf({INV} inv, String k, java.util.HashMap caps, String id) {{
  long n = (long) countInv(inv, id);
  String c = {PKG}.SackDefs.catOf(id);
  if (k != null && c != null && caps != null && caps.containsKey(c)) n += {PKG}.SackPool.get(k, id);
  return n;
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String iconBox(String id, String n) {
  return "Group { Anchor: (Width: 86, Height: 86); Background: #1d3a5f; ItemIcon { Anchor: (Width: 64, Height: 64, Left: 11, Top: 5); ItemId: \\"" + safe(id) + "\\"; } Label { Anchor: (Width: 80, Height: 20, Right: 4, Bottom: 3); Text: \\"" + safe(n) + "\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); } }";
}""", page))
# 0.7.5: the view of a bag the player does not carry - what it holds, the Small recipe as big icons, the player's counts, the upgrades, how
# many items already wait in it. Long texts go through set() (commas and colons are safe there); #SkyySInfo exists here too (profileNotice).
# Review fix: the two longest wrapped texts (#SkyySNbHolds up to 169 chars for Smithing, #SkyySNbUp 188 chars) get room for three lines
# (62 / 60 high) in case the client wraps earlier than the ~2 lines a 968 px wide label should need. Height budget of this view: 2 + 46
# tabs + 22 grey-tab note + 36 + 62 + 30 + 96 + 30 + 60 + 34 + 30 + 44 = 492 of the 580 inside the 600 high root.
page.addMethod(CtNewMethod.make(f"""
public void buildNoBag({UCB} b, {PLA} player, String k, java.util.HashMap caps) {{
  int ci = {PKG}.SackDefs.catIndex(this.cat);
  if (ci < 0) ci = 0;
  String cat = {PKG}.SackDefs.CATS[ci];
  String mat = {PKG}.SackDefs.MAT[ci];
  String bolt = {PKG}.SackDefs.BOLT[0];
  int bq = {PKG}.SackDefs.BOLTQ;
  int mq = {PKG}.SackDefs.MATQ;
  {INV} inv = player == null ? null : player.getInventory();
  long stored = {PKG}.SackPool.catTotal(k, cat);
  b.appendInline("#SkyySacks", "Label #SkyySNbTitle {{ Anchor: (Height: 36); Text: \\"\\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyySNbTitle.Text", cat + " Bag - you do not carry one yet");
  b.appendInline("#SkyySacks", "Label #SkyySNbHolds {{ Anchor: (Height: 62); Text: \\"\\"; Style: (FontSize: 15, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }}");
  b.set("#SkyySNbHolds.Text", "A " + cat + " Bag holds " + {PKG}.SackDefs.HOLDS[ci] + ". Matching items in your storage go into it by themselves.");
  b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 30); Text: \\"How to craft one\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #e0b060, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Group #SkyySNbRecipe {{ Anchor: (Height: 96); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyySNbRecipe", iconBox("Skyy_Sack_" + cat + "_Small", ""));
  b.appendInline("#SkyySNbRecipe", "Label {{ Anchor: (Width: 48, Height: 86); Text: \\"=\\"; Style: (FontSize: 30, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySNbRecipe", iconBox(bolt, String.valueOf(bq)));
  b.appendInline("#SkyySNbRecipe", "Label {{ Anchor: (Width: 48, Height: 86); Text: \\"+\\"; Style: (FontSize: 30, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySNbRecipe", iconBox(mat, String.valueOf(mq)));
  b.appendInline("#SkyySNbRecipe", "Label {{ Anchor: (Width: 20, Height: 86); Text: \\"\\"; }}");
  b.appendInline("#SkyySNbRecipe", "Label #SkyySNbWhere {{ Anchor: (Width: 560, Height: 86); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center, Wrap: true); }}");
  b.set("#SkyySNbWhere.Text", "Small " + cat + " Bag = " + bq + " " + {PKG}.SackDefs.BOLTN[0] + " + " + mq + " " + {PKG}.SackDefs.MATN[ci] + ", crafted at a Workbench.");
  long hb = haveOf(inv, k, caps, bolt);
  long hm = haveOf(inv, k, caps, mat);
  boolean ready = hb >= (long) bq && hm >= (long) mq;
  b.appendInline("#SkyySacks", "Label #SkyySNbHave {{ Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + (ready ? "#9fd8a2" : "#e0a070") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyySNbHave.Text", "You have " + num(hb) + " / " + bq + " " + {PKG}.SackDefs.BOLTN[0] + " and " + num(hm) + " / " + mq + " " + {PKG}.SackDefs.MATN[ci] + (ready ? " - ready to craft" : ""));
  b.appendInline("#SkyySacks", "Label #SkyySNbUp {{ Anchor: (Height: 60); Text: \\"\\"; Style: (FontSize: 14, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }}");
  b.set("#SkyySNbUp.Text", "A Small bag holds " + num((long) {PKG}.SackDefs.tierCap("Small")) + " of each item. Upgrade it at a Workbench: Medium = Small " + cat + " Bag + " + bq + " " + {PKG}.SackDefs.BOLTN[1] + " (" + num((long) {PKG}.SackDefs.tierCap("Medium")) + " of each), Large = Medium " + cat + " Bag + " + bq + " " + {PKG}.SackDefs.BOLTN[2] + " (" + num((long) {PKG}.SackDefs.tierCap("Large")) + " of each).");
  b.appendInline("#SkyySacks", "Label #SkyySNbStored {{ Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + (stored > 0L ? "#ffd27a" : "#8fa4b8") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyySNbStored.Text", stored > 0L ? (num(stored) + " items are waiting in your " + cat + " Bag - carry one to reach them. Nothing is ever lost.") : ("Nothing is stored in a " + cat + " Bag yet."));
  b.appendInline("#SkyySacks", "Label #SkyySInfo {{ Anchor: (Height: 30); Text: \\"" + safe(this.info) + "\\"; Style: (FontSize: 15, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Label #SkyySNbHint {{ Anchor: (Height: 44); Text: \\"\\"; Style: (FontSize: 14, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }}");
  b.set("#SkyySNbHint.Text", "A Workbench can use the materials in the bags you carry. In /craft the bag recipes are on the Crafting tab while a Workbench accessory is equipped.");
}}""", page))
# 0.7.5: build() only resolves the profile key, the player and the carried bags; render() draws the page from those (the page always shows
# this profile's data, so the key is always set and both views have #SkyySInfo for profileNotice).
page.addMethod(CtNewMethod.make(f"""
public void render({UCB} b, {UEB} ev, {PLA} player, String k, java.util.HashMap caps) {{
  this.key = k;
  this.cat = pickCat(k, caps);
  this.carried = caps.containsKey(this.cat);
  this.cells = new String[36];
  String bs = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 15, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String tabOn = "Style: TextButtonStyle(Default: (Background: #e0b060, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #f0c878, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #b08040, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String tabNo = "Style: TextButtonStyle(Default: (Background: #26303c, LabelStyle: (FontSize: 15, TextColor: #8a9aab, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3a4858, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #1a222c, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String tabNoOn = "Style: TextButtonStyle(Default: (Background: #8fa4b8, LabelStyle: (FontSize: 15, TextColor: #0b1524, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a8bccf, LabelStyle: (FontSize: 15, TextColor: #0b1524, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #6f8498, LabelStyle: (FontSize: 15, TextColor: #0b1524, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 1000, Height: 600); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySacks", "Group {{ Anchor: (Height: 2); Background: #e0b060; }}");
  b.appendInline("#SkyySacks", "Group #SkyySTabs {{ Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 8); }}");
  String[] cats = {PKG}.SackDefs.CATS;
  boolean missing = false;
  for (int c = 0; c < cats.length; c++) {{
    boolean has = caps.containsKey(cats[c]);
    if (!has) missing = true;
    boolean sel = cats[c].equals(this.cat);
    String sty = has ? (sel ? tabOn : bs) : (sel ? tabNoOn : tabNo);
    b.appendInline("#SkyySTabs", "TextButton #SkyySTab" + cats[c] + " {{ Anchor: (Width: 140, Height: 36); Text: \\"" + cats[c] + "\\"; " + sty + " }}");
    b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 8, Height: 36); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySTab" + cats[c], {EVD}.of("a", "tab:" + cats[c]));
  }}
  b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 26, Height: 36); Text: \\"\\"; }}");
  b.appendInline("#SkyySTabs", "TextButton #SkyySTabCraft {{ Anchor: (Width: 145, Height: 36); Text: \\"Craft\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySTabCraft", {EVD}.of("a", "craft"));
  if (missing) b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 22); Text: \\"Grey tabs are bags you do not carry - click one to see how to craft it\\"; Style: (FontSize: 13, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  if (!this.carried) {{ buildNoBag(b, player, k, caps); return; }}
  Integer capObj = (Integer) caps.get(this.cat);
  long capacity = capObj == null ? 0L : (long) capObj.intValue();
  long stored = {PKG}.SackPool.catTotal(k, this.cat);
  b.appendInline("#SkyySacks", "Label #SkyySCap {{ Anchor: (Height: 34); Text: \\"" + safe(this.cat + " bag - holds up to " + capacity + " of each item - " + stored + " stored") + "\\"; Style: (FontSize: 18, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = {PKG}.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (this.cat.equals({PKG}.SackDefs.catOf((String) e.getKey()))) entries.add(e);
  }}
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  for (int r = 0; r < 4; r++) {{
    b.appendInline("#SkyySacks", "Group #SkyySRow" + r + " {{ Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 6); }}");
    for (int c = 0; c < 9; c++) {{
      int idx = r * 9 + c;
      if (idx < entries.size()) {{
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
        String id = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = id;
        b.appendInline("#SkyySRow" + r, "Button #SkyySCell" + idx + " {{ Anchor: (Width: 86, Height: 86); Style: ButtonStyle( Default: ( Background: #1d3a5f ), Hovered: ( Background: #2f5a8f ), Disabled: ( Background: #1a2c3c ) ); ItemIcon {{ Anchor: (Width: 64, Height: 64, Left: 11, Top: 5); ItemId: \\"" + safe(id) + "\\"; }} Label {{ Anchor: (Width: 80, Height: 18, Right: 4, Bottom: 3); Text: \\"" + cnt + "\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); }} }}");
        ev.addEventBinding({BT}.Activating, "#SkyySCell" + idx, {EVD}.of("a", "cell:" + idx + ":stack"));
        ev.addEventBinding({BT}.RightClicking, "#SkyySCell" + idx, {EVD}.of("a", "cell:" + idx + ":one"));
      }} else {{
        this.cells[idx] = null;
        b.appendInline("#SkyySRow" + r, "Group {{ Anchor: (Width: 86, Height: 86); Background: #142030(0.9); }}");
      }}
      b.appendInline("#SkyySRow" + r, "Label {{ Anchor: (Width: 6, Height: 86); Text: \\"\\"; }}");
    }}
  }}
  // 0.7.5: hides and fabric scraps moved from Combat to Smithing - the Combat tab says where they went when no Smithing bag is carried
  String shown = this.info == null ? "" : this.info;
  if (shown.length() == 0 && "Combat".equals(this.cat) && !caps.containsKey("Smithing")) {{
    long sm = {PKG}.SackPool.catTotal(k, "Smithing");
    if (sm > 0L) shown = "Hides and fabric scraps now live in the Smithing bag - " + sm + " items wait there (Smithing tab)";
  }}
  b.appendInline("#SkyySacks", "Label #SkyySInfo {{ Anchor: (Height: 30); Text: \\"" + safe(shown) + "\\"; Style: (FontSize: 15, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Group #SkyySAct {{ Anchor: (Height: 48); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyySAct", "TextButton #SkyySPickAll {{ Anchor: (Width: 200, Height: 38); Text: \\"Pick up all\\"; " + bs + " }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 14, Height: 38); Text: \\"\\"; }}");
  b.appendInline("#SkyySAct", "TextButton #SkyySDepAll {{ Anchor: (Width: 200, Height: 38); Text: \\"Deposit all\\"; " + bs + " }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 14, Height: 38); Text: \\"\\"; }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 420, Height: 38); Text: \\"left click takes a stack - right click takes one\\"; Style: (FontSize: 14, TextColor: #8fa4b8, VerticalAlignment: Center); }}");
  ev.addEventBinding({BT}.Activating, "#SkyySPickAll", {EVD}.of("a", "pickall"));
  ev.addEventBinding({BT}.Activating, "#SkyySDepAll", {EVD}.of("a", "depall"));
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  String k = {PKG}.SackPool.pkey(u);
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  java.util.HashMap caps = player == null ? new java.util.HashMap() : {PKG}.SweepTask.caps(player.getInventory());
  render(b, ev, player, k, caps);
}}""", page))
# 0.7.5: why a take-out moved nothing - the bag of that tab is gone (dropped / stored away since the page was drawn) or storage is full
page.addMethod(CtNewMethod.make(f"""
public static String noRoom({PLA} p, String cat) {{
  if (p != null && cat != null && !{PKG}.SweepTask.caps(p.getInventory()).containsKey(cat)) return "you need a " + cat + " bag on you to take items out";
  return "storage is full";
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    String[] cats = {PKG}.SackDefs.CATS;
    for (int c = 0; c < cats.length; c++) {{
      if (data.indexOf("tab:" + cats[c] + "\\"") >= 0) {{ this.cat = cats[c]; this.info = ""; rebuild(); return; }}
    }}
    if (data.indexOf("\\"craft\\"") >= 0) {{
      {PLA} pl0 = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (pl0 != null) pl0.getPageManager().openCustomPage(ref, st, new {PKG}.CraftPage(this.playerRef, (String) null));
      return;
    }}
    // 0.7.5: the how-to-craft view (a bag the player does not carry) has no item buttons - a stray event only refreshes it
    if (!this.carried) {{ rebuild(); return; }}
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    String k = {PKG}.SackPool.settledKey(u);
    if (k == null) {{ this.info = "bags paused (profile loading or switching) - try again in a moment"; rebuild(); return; }}
    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; rebuild(); return; }}
    for (int i = 0; i < 36; i++) {{
      if (this.cells == null || this.cells[i] == null) continue;
      int n = 0;
      if (data.indexOf("cell:" + i + ":stack\\"") >= 0) n = 64;
      else if (data.indexOf("cell:" + i + ":one\\"") >= 0) n = 1;
      if (n == 0) continue;
      int added = {PKG}.SweepTask.withdraw(player, k, this.cells[i], n);
      this.info = added > 0 ? ("took " + added + " " + this.cells[i]) : noRoom(player, this.cat);
      {PKG}.SackPool.saveSoon(k);
      rebuild();
      return;
    }}
    if (data.indexOf("pickall\\"") >= 0) {{
      int total = 0;
      for (int i = 0; i < 36; i++) {{
        if (this.cells == null || this.cells[i] == null) continue;
        int added; int guard = 0;
        do {{ added = {PKG}.SweepTask.withdraw(player, k, this.cells[i], 64); total += added; guard++; }} while (added > 0 && guard < 64);
      }}
      this.info = total > 0 ? ("picked up " + total + " items") : noRoom(player, this.cat);
      {PKG}.SackPool.saveSoon(k);
      rebuild();
      return;
    }}
    if (data.indexOf("depall\\"") >= 0) {{
      {PKG}.SackPool.clearExempt(k);
      int moved = {PKG}.SweepTask.sweep(player, k, this.cat, true);
      this.info = moved > 0 ? ("deposited " + moved + " items") : "nothing to deposit (or sack full)";
      {PKG}.SackPool.saveSoon(k);
      rebuild();
      return;
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sacks page event failed: " + t); }}
}}""", page))

'''.lstrip(LF)
seg('page.addMethod(CtNewMethod.make(f"""' + LF + 'public String pickCat(String k, java.util.HashMap caps) {{' + LF,
    '# 0.7.2: the active profile changed while this page is open (ProcTask, world thread).',
    ['if (this.cat != null && caps.containsKey(this.cat)) return this.cat;',
     'You need a magic bag on you to reach in. Craft a Mining, Foraging, Farming or Combat bag at a workbench.',
     'if (!caps.containsKey(cats[c])) continue;', 'this.info = added > 0 ? ("took " + added + " " + this.cells[i]) : "storage is full";',
     'int moved = {PKG}.SweepTask.sweep(player, k, this.cat, true);'],
    PAGE)

# ---------------- plugin: right-click page id of the new bag + ready line ----------------
rep('  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCombat", new {PKG}.SacksPageFactory("Combat"));' + LF,
    '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCombat", new {PKG}.SacksPageFactory("Combat"));' + LF
    + '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksSmithing", new {PKG}.SacksPageFactory("Smithing"));' + LF)
rep('ready - /pd, /craft (Crafting, Smithing, Farming, Campfire accessory tab',
    'ready - /pd (Mining, Foraging, Farming, Combat and Smithing bags - every tab shown, a bag you do not carry shows how to craft it), /craft (Crafting, Smithing, Farming, Campfire accessory tab')

# ---------------- assets: the bag table drives the item JSON + lang ----------------
seg('mats = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread", "Combat": "Ingredient_Bone_Fragment"}' + LF,
    '        desc = "A magic bag that opens onto your pocket dimension.',
    ['for cat in ("Mining", "Foraging", "Farming", "Combat"):', '"Ingredient_Bolt_Wool", "Quantity": 3}, {"ItemId": mats[cat], "Quantity": 4}',
     '"Ingredient_Bolt_Linen", "Quantity": 3}', '"Ingredient_Bolt_Silk", "Quantity": 3}', 'what = {"Mining": "ore, rubble, rock and soil"'],
    '# 0.7.5: the bag table (BAG_CATS / BAG_MAT / BAG_BOLTS / BAG_HOLDS near the top) - the first four rows are the 0.7.4 recipes unchanged' + LF
    + 'for cat in BAG_CATS:' + LF
    + '    items = {' + LF
    + '        "Small":  sack_item(cat, "Small", "Common",   [{"ItemId": BAG_BOLTS[0], "Quantity": BAG_BOLT_QTY}, {"ItemId": BAG_MAT[cat], "Quantity": BAG_MAT_QTY}]),' + LF
    + '        "Medium": sack_item(cat, "Medium", "Uncommon", [{"ItemId": "Skyy_Sack_%s_Small" % cat, "Quantity": 1}, {"ItemId": BAG_BOLTS[1], "Quantity": BAG_BOLT_QTY}]),' + LF
    + '        "Large":  sack_item(cat, "Large", "Rare",     [{"ItemId": "Skyy_Sack_%s_Medium" % cat, "Quantity": 1}, {"ItemId": BAG_BOLTS[2], "Quantity": BAG_BOLT_QTY}]),' + LF
    + '    }' + LF
    + '    for tier, node in items.items():' + LF
    + '        files["Server/Item/Items/Utility/Skyy_Sack_%s_%s.json" % (cat, tier)] = json.dumps(node, indent=2)' + LF
    + '        lang.append("items.Skyy_Sack_%s_%s.name=%s %s Bag" % (cat, tier, tier, cat))' + LF
    + '        lang.append("server.items.Skyy_Sack_%s_%s.name=%s %s Bag" % (cat, tier, tier, cat))' + LF
    + '        caps = {"Small": 640, "Medium": 2240, "Large": 20160}[tier]' + LF
    + '        what = BAG_HOLDS[cat]' + LF)

# ---------------- review fix: SackPool.saveNow durability ----------------
# The per-profile pool file now also holds the whole Smithing bag (bars, leather, hides, bolts). Its save gets the same tmp + fsync +
# ATOMIC_MOVE (fallback: plain replace) pattern ProcStore.save and SackCfg.reload already use, so a crash or power cut mid-save leaves
# either the old or the new file, never a truncated one. saveNow is a plain (non f-string) method body: single braces.
rep('    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);' + LF
    + '    try { p.store(out, "SkyySacks pool"); } finally { out.close(); }' + LF
    + '    java.nio.file.Files.move(tmp, DIR.resolve(k + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });' + LF,
    '    java.nio.file.Path dst = DIR.resolve(k + ".properties");' + LF
    + '    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());' + LF
    + '    try { p.store(out, "SkyySacks pool"); out.flush(); out.getFD().sync(); } finally { out.close(); }' + LF
    + '    try { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }' + LF
    + '    catch (Throwable am) { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }' + LF)

# ---------------- review fix: drop the dead self-test grant ----------------
# GrantTask + SackReady (free Small Mining Sack + ore on join, guarded only by an in-memory map) were never written to the jar (not in the
# writeFile loop) and never registered, but the source stayed one edit away from a restart-repeatable free-item grant. Removed.
rep('grt  = pool.makeClass(PKG + ".GrantTask")' + LF + 'srd  = pool.makeClass(PKG + ".SackReady")' + LF, '')
seg('# ==== SELF-TEST: GrantTask + SackReady (strip once verified in-game) ====', '# ================= SacksPageFactory (right-click',
    ['grt.addInterface(pool.get("java.lang.Runnable"))', 'GRANTED.putIfAbsent(u, Boolean.TRUE)', 'srd.addInterface(pool.get("java.util.function.Consumer"))',
     '}}""", srd))'], '')

# ---------------- checks ----------------
assert 'VERSION = "0.7.5"' in s
# review fixes: pool save is fsync + atomic like ProcStore / SackCfg; the self-test grant is gone (no class, no makeClass, no writeFile)
_i_save = s.index("public static void saveNow(String k) {")
_save = s[_i_save:s.index('}""", sp))', _i_save)]
assert "out.getFD().sync();" in _save and "StandardCopyOption.ATOMIC_MOVE" in _save and "catch (Throwable am)" in _save, "pool save not hardened"
assert "Files.newOutputStream(tmp" not in _save
assert s.count("out.getFD().sync();") == 3, "expected fsync in SackCfg.reload, SackPool.saveNow and ProcStore.save"
_code = s[s.index('VERSION = "0.7.5"'):]   # the docstring names the removed classes; the code must not
assert "GrantTask" not in _code and "SackReady" not in _code and "GRANTED" not in _code and "grt." not in _code and "srd." not in _code, "left over"
assert s.count("BAG_CATS = (") == 1 and s.count("_bag_ids_check()") == 2 and s.count("for cat in BAG_CATS:") == 1
assert "for cat in (\"Mining\", \"Foraging\", \"Farming\", \"Combat\"):" not in s and "mats[cat]" not in s
# SackDefs: the table arrays come before any method, catIndex before its callers (javassist: no forward references)
i_defs = s.index('defs.addField(CtField.make("public static final String[] CATS = " + _jarr(BAG_CATS)')
assert s.index("def _jarr(vals):") < i_defs < s.index("public static int catIndex(String cat) {") < s.index("public static String catOf(String itemId) {")
assert s.index("public static String catOf(String itemId) {") < s.index("public static int tierCap(String tier) {")
assert 'itemId.startsWith("Ingredient_Hide_") || itemId.startsWith("Ingredient_Chitin")' not in s, "hides still in Combat"
assert s.index("if (@SMITH@) return \"Smithing\";") < s.index('|| (itemId.startsWith("Ingredient_") && itemId.endsWith("_Essence"))) return "Combat";'), "Smithing must be checked before Combat"
# SacksPage: helpers before callers, every method once
i_page = s.index("public String pickCat(String k, java.util.HashMap caps) {{")
order = ["public static String safe(String t) {", "public String pickCat(String k, java.util.HashMap caps) {{", "public static String num(long v) {",
         "public static int countInv({INV} inv, String id) {{", "public static long haveOf({INV} inv, String k, java.util.HashMap caps, String id) {{",
         "public static String iconBox(String id, String n) {", "public void buildNoBag({UCB} b, {PLA} player, String k, java.util.HashMap caps) {{",
         "public void render({UCB} b, {UEB} ev, {PLA} player, String k, java.util.HashMap caps) {{", "public static String noRoom({PLA} p, String cat) {{"]
pos = [s.index(o) for o in order]
assert pos == sorted(pos), "SacksPage method order: " + repr(pos)
for o in order[1:]:
    assert s.count(o) == 1, "not unique: " + o
i_render = s.index(order[7])
i_pbuild = s.index("public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{", i_page)
i_phde = s.index("public void handleDataEvent({REF} ref, {ST} st, String data) {{", i_page)
assert i_render < i_pbuild < i_phde < s.index("public void profileNotice(String k) {{", i_page), "render before build before handleDataEvent"
assert s.index(order[8]) < i_phde, "noRoom must come before handleDataEvent"
assert s.index('page.addField(CtField.make("public boolean carried;", page))') < i_page
# both views carry #SkyySInfo (profileNotice sets it whenever this.key != null - and the key is now always set)
assert s.count('Label #SkyySInfo {{ Anchor: (Height: 30);') == 2 and s.count('c.set("#SkyySInfo.Text"') == 1
assert "You need a magic bag on you to reach in" not in s and "this.key = null;" not in s[i_page:i_phde]
# every tab drawn, none skipped; five page ids registered
assert "if (!caps.containsKey(cats[c])) continue;" not in s
for c in ("Mining", "Foraging", "Farming", "Combat", "Smithing"):
    assert s.count('"SkyySacks%s", new {PKG}.SacksPageFactory("%s")' % (c, c)) == 1, c
# UI rules: no underscore in element ids, root anchor only Width/Height, no periodic updates
import re as _re
for m in _re.finditer(r"#(SkyyS[A-Za-z0-9_]*)", s):
    assert "_" not in m.group(1), "UI id with underscore: " + m.group(1)
assert "Group #SkyySacks {{ Anchor: (Width: 1000, Height: 600);" in s
assert "cp.live(" not in s and "public void live(" not in s, "periodic refresh came back"
# every 0.7.4 profile / busy rule untouched
assert s.count("public static String settledKey(java.util.UUID u) {") == 1, "settledKey changed"
assert 'b.get("profile:busy:" + u.toString()) != null) return null;' in s, "busy gate lost"
assert s.count("String k = {PKG}.SackPool.settledKey(u);") >= 2, "item moves must stay on settledKey"
assert "    String k = {PKG}.SackPool.settledKey(u);" + LF + "    if (k == null) {{ this.info = \"bags paused (profile loading or switching) - try again in a moment\"; rebuild(); return; }}" in s

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
