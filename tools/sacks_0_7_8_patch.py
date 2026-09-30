"""Derive SkyySacks/build_skyysacks_0.7.8.py from the SET pin 0.7.7 (edit THIS file, then regenerate: python tools/sacks_0_7_8_patch.py).
0.7.8 = COOKED FOOD STAYS OUT OF THE FARMING BAG. Skyy's decision 2026-09-30 (verbatim): "my cooked food went into my farming sack. id
keep cooked food out." (screenshot: the Mythic Omni Bag's Farming tab held cooked dishes). Until 0.7.7, SackDefs.catOf sent every Food_*
id and every Skyy_Cook_* graded dish (0.7.3, research/Cooking-Skill-Spec.md 3.4) to Farming.
 - THE RULE: the Farming bag keeps RAW farm produce only - Plant_*, Fish_*, raw animal products (Food_*_Raw / Food_*_Raw_* incl. the rare
   fish, Food_Egg), life essence, poop. Cooked / prepared food never goes in: every other Food_* id (Bread, Candy Cane, Cheese, Grilled
   Fish, Kebabs, Pies, Popcorn, Salads, Cooked Vegetables, Cooked Wildmeat), every Skyy_Cook_* graded dish and SkyyCooking's cook:prefix
   items. Classified by ONE helper, SackDefs.cooked(id); a build check classifies every Food_ id of Assets.zip against the table below.
 - Server Setup -> Bags and Crafting -> "Cooked food in the Farming bag" (bags.cookedFood, config kit tools/skyycfg.py 1.1, live, default
   OFF = Skyy's lock). ON = exactly the 0.7.7 routing.
 - SackDefs.homeOf(id) = the 0.7.7 catOf unchanged (the bag an item BELONGS to): everything that reads a pool uses it - the bag page grid
   and its counts, pickCat, withdraw (clicks, Pick up all), the bench link + /craft materials (BagMirror.rebuild) and the how-to-craft
   counts (haveOf) - so cooked food ALREADY in a Farming pool stays visible, can be taken out or used, and is never deleted.
   SackDefs.catOf(id) = where a NEW item may go = homeOf minus cooked food while the switch is off; its only caller is SweepTask.sweep,
   i.e. the 2 s auto-pickup routing AND Deposit all, for every bag type and the Mythic Omni Bag. (SkyySacks has no /pd deposit
   subcommand and no shift-click / inventory-screen moves: the sweep is the only way items enter a pool.) SkyyCollections coll:fn:where
   does not depend on the classification (the Farming bag unlocks from Wheat).
 - The Farming tab says "Cooked food no longer goes into this bag - N cooked items are still here to take out" on its existing info
   line (no new markup) while stored cooked food remains; the how-to-craft view names what the bag holds with the switch.
 - Food_Bread stays the Farming bag's recipe material (BAG_MAT: the Normal Farming Bag recipe + the how-to-craft view; the bag icon is
   Utility_Bag_Seed) - only the storage rule changes; bread now simply stays in the inventory, where the Workbench finds it.
 - Rebuild fix: the Mythic tooltip colour follows SkyyGear 0.1 / the kit RARITY palette (Skyy's lock: Mythic #CC66CC) - 0.7.7 stopped at
   build line ~306 because BAG_RARITY still carried Wynn's #aa00aa for the Skyy_Bag_Mythic tooltip. Page colours are checked against
   tools/skyyui.py RARITY too (read as text; the page is not a kit page). No other bag behaviour changes.
 - Review fixes (sonnet review of 0.7.8): (1) the bag page grid shows 36 cells - while the switch is off, stored cooked entries come FIRST
   on the Farming tab (each group keeps the count order), so none hides behind raw produce; (2) the note says "1 cooked item is" /
   "N cooked items are"; (3) Deposit all on the Farming tab adds "cooked food stays in your inventory" while the switch is off and the
   inventory holds cooked food (SweepTask.cookedHeld), instead of only "nothing to deposit (or sack full)".
Everything else is 0.7.7 (bags, tiers, Omni, recipes, collection unlocks, /craft, Furnace / Tannery, settings, config rows).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.7.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.8.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def Q(txt):
    """Inner Java blocks written jt(r@Q3@ ... @Q3@) here (the outer raw strings of this patch use the same triple quote)."""
    return txt.replace("@Q3@", "'" * 3)


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


# ================= docstring + version =================
rep('"""SkyySacks 0.7.7 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.7.py            -> SkyySacks/SkyySacks-0.7.7.jar' + LF
    + '       python build_skyysacks_0.7.7.py --deploy   -> also',
    '"""SkyySacks 0.7.8 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.8.py            -> SkyySacks/SkyySacks-0.7.8.jar' + LF
    + '       python build_skyysacks_0.7.8.py --deploy   -> also')
rep('vanilla-look bag page; crafted gear goes through SkyyGear gear:fn:roll when it exists.' + LF + '"""' + LF,
    'vanilla-look bag page; crafted gear goes through SkyyGear gear:fn:roll when it exists.' + LF
    + '0.7.8 (derived from 0.7.7 by tools/sacks_0_7_8_patch.py - edit the patch, not this file; Skyy 2026-09-30 "my cooked food went into my' + LF
    + 'farming sack. id keep cooked food out."): COOKED FOOD STAYS OUT OF THE FARMING BAG - the Farming bag keeps raw produce (Plant_*, Fish_*,' + LF
    + 'Food_*_Raw incl. the rare fish, Food_Egg, life essence, poop); cooked / prepared Food_*, Skyy_Cook_* dishes and cook:prefix items stay in' + LF
    + 'the inventory. One helper SackDefs.cooked(id); catOf (new items: auto-pickup + Deposit all, every bag and the Omni) leaves cooked food' + LF
    + 'out while Server Setup "Cooked food in the Farming bag" (bags.cookedFood, default OFF) is off; homeOf (= the 0.7.7 catOf) keeps cooked' + LF
    + 'food already stored visible, retrievable and usable - never deleted. Rebuild fix: Mythic tooltip #cc66cc (SkyyGear 0.1 / kit RARITY).' + LF
    + 'Review fixes: stored cooked food is listed first on the Farming tab (switch off) so the 36-cell grid never hides it; the note is' + LF
    + 'singular / plural; Deposit all on the Farming tab says cooked food stays in the inventory (SweepTask.cookedHeld).' + LF
    + '"""' + LF)
rep('VERSION = "0.7.7"', 'VERSION = "0.7.8"')

# ================= the bag table: Farming holds raw food; the cooked / raw table =================
rep('             "Farming": "plants, food and cooked dishes, fish and life essence",' + LF,
    '             "Farming": "plants, raw food, fish and life essence",' + LF)
COOKED_TABLE = r'''# 0.7.8 COOKED FOOD (Skyy 2026-09-30, verbatim: "my cooked food went into my farming sack. id keep cooked food out."): the Farming bag
# keeps RAW farm produce only. SackDefs.cooked(id) is THE classification (Java); cooked_py below is its build-time mirror, checked against
# every Food_ id of Assets.zip (_food_check) and by SkyySacks/test_skyysacks_0.7.8.py against the compiled class:
#   cooked = a Skyy_Cook_* graded dish (not the Skyy_Cook_Recipe_* recipe items, which never pool), an id with SkyyCooking's cook:prefix
#            (bridge, starts with Skyy_Cook), or a Food_* id that is not raw;
#   raw    = Food_*_Raw / Food_*_Raw_* (beef, chicken, pork, wildmeat, the fish fillets incl. Uncommon / Rare / Epic / Legendary) and
#            Food_Egg / Food_Egg_*; Plant_*, Fish_*, life essence and poop are never cooked.
# A new Food_ id is cooked unless it carries "_Raw" (Skyy: keep cooked food out) - _food_check prints it so the table can be updated.
# FARM_HOLDS_COOKED = the 0.7.7 Farming text, shown by the how-to-craft view while bags.cookedFood is on.
FOOD_COOKED = ("Food_Bread", "Food_Candy_Cane", "Food_Cheese", "Food_Fish_Grilled", "Food_Kebab_Fruit", "Food_Kebab_Meat",
               "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Pie_Apple", "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Popcorn",
               "Food_Salad_Berry", "Food_Salad_Caesar", "Food_Salad_Mushroom", "Food_Vegetable_Cooked", "Food_Wildmeat_Cooked")
FOOD_RAW = ("Food_Beef_Raw", "Food_Chicken_Raw", "Food_Egg", "Food_Fish_Raw", "Food_Fish_Raw_Epic", "Food_Fish_Raw_Legendary",
            "Food_Fish_Raw_Rare", "Food_Fish_Raw_Uncommon", "Food_Pork_Raw", "Food_Wildmeat_Raw")
FARM_HOLDS_COOKED = "plants, food and cooked dishes, fish and life essence"
assert '"' not in FARM_HOLDS_COOKED and "\\" not in FARM_HOLDS_COOKED
def cooked_py(i, prefix=None):
    if i is None:
        return False
    if i.startswith("Skyy_"):
        if i.startswith("Skyy_Cook_Recipe_"):
            return False
        if i.startswith("Skyy_Cook_"):
            return True
        return bool(prefix) and prefix.startswith("Skyy_Cook") and i.startswith(prefix)
    if not i.startswith("Food_"):
        return False
    if i == "Food_Egg" or i.startswith("Food_Egg_"):
        return False
    return not (i.endswith("_Raw") or "_Raw_" in i)
assert all(cooked_py(i) for i in FOOD_COOKED) and not any(cooked_py(i) for i in FOOD_RAW) and not set(FOOD_COOKED) & set(FOOD_RAW)
assert cooked_py(BAG_MAT["Farming"]), "the Farming bag material (Food_Bread) is cooked food - it stays in the inventory (0.7.8)"
def _food_check():
    import zipfile
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - the cooked / raw food table was not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        ids = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    food = sorted(i for i in ids if i.startswith("Food_"))
    for i in list(FOOD_COOKED) + list(FOOD_RAW):
        if i not in ids:
            print("WARNING: %s (cooked / raw table) is no longer in Assets.zip" % i)
    new = [i for i in food if i not in FOOD_COOKED and i not in FOOD_RAW]
    for i in new:
        print("WARNING: new vanilla food %s - classified %s by the rule; add it to FOOD_COOKED / FOOD_RAW" % (i, "COOKED" if cooked_py(i) else "RAW"))
    bad = [i for i in ("Plant_", "Fish_") for j in ids if j.startswith(i) and cooked_py(j)]
    if bad:
        raise SystemExit("0.7.8: a Plant_ / Fish_ id classified as cooked food")
    print("food rule: %d vanilla Food_ ids - cooked (stay out of the Farming bag): %s | raw (Farming bag): %s"
          % (len(food), ", ".join(i[5:] for i in food if cooked_py(i)), ", ".join(i[5:] for i in food if not cooked_py(i))))
'''
rep('for _i in list(BAG_MAT.values()) + list(BAG_BOLTS):' + LF + '    assert _i in ITEM_NAME, "no display name for " + _i' + LF,
    'for _i in list(BAG_MAT.values()) + list(BAG_BOLTS):' + LF + '    assert _i in ITEM_NAME, "no display name for " + _i' + LF
    + COOKED_TABLE)
rep('_bag_ids_check()' + LF + '# 0.7.7 (spec 3.2): SkyyGear owns the rarity look.',
    '_bag_ids_check()' + LF + '_food_check()' + LF + '# 0.7.7 (spec 3.2): SkyyGear owns the rarity look.')

# ================= rebuild fix: Mythic tooltip = SkyyGear 0.1 / kit RARITY #CC66CC =================
rep("# QualityValue (< 8: SkyyAuctions treats >= 8 as technical), vanilla texture set reused by hue, drop particle). Mythic page text" + LF
    + "# is #cc66cc (#aa00aa is too dark to read on the page); the tooltip keeps Wynn's #aa00aa. Review fix: the drop particles are SkyyGear's" + LF,
    "# QualityValue (< 8: SkyyAuctions treats >= 8 as technical), vanilla texture set reused by hue, drop particle). Mythic is #cc66cc on" + LF
    + "# the page AND in the tooltip (0.7.8 rebuild fix: Skyy's lock, SkyyGear 0.1 RARITIES + tools/skyyui.py RARITY adopted #CC66CC - Wynn's" + LF
    + "# #aa00aa reads ~2.8:1 on the dark panels; 0.7.7 kept it on the tooltip and stopped rebuilding). Review fix: the drop particles are SkyyGear's" + LF)
rep('              ("Skyy_Bag_Mythic",    "Mythic",    "#aa00aa", "#cc66cc", 6, "Epic",      "Drop_Epic")]',
    '              ("Skyy_Bag_Mythic",    "Mythic",    "#cc66cc", "#cc66cc", 6, "Epic",      "Drop_Epic")]')
rep('    bad = ["%s %s (bags) vs %s" % (k, mine[k][0], got[k]) for k in sorted(mine) if got.get(k) != mine[k][0]]' + LF,
    '    # 0.7.8: the spec table still lists Wynn\'s Mythic #AA00AA; the kit lock (tools/skyyui.py RARITY, SkyyGear 0.1) moved it to #CC66CC' + LF
    + '    bad = ["%s %s (bags) vs %s" % (k, mine[k][0], got[k]) for k in sorted(mine) if got.get(k) != mine[k][0]' + LF
    + '           and not (k == "mythic" and mine[k][0] == "#cc66cc" and got.get(k) == "#aa00aa")]' + LF)
KIT_CHECK = r'''# 0.7.8: the bag page rarity colours = the kit RARITY palette (tools/skyyui.py, LOCKED 2026-09-25; Mythic #CC66CC on pages). Read as text
# (the _camp_defaults_check pattern) - the bag page is not built with the kit, so the kit is not imported here. A missing or unreadable kit
# file is a note, never a stop.
def _kit_palette_check():
    import re
    p = os.path.join(HERE, "..", "tools", "skyyui.py")
    try:
        txt = open(p, encoding="utf8", errors="replace").read()
    except Exception as e:
        print("note: could not read tools/skyyui.py (%s) - bag page colours not checked against the kit RARITY palette" % e)
        return
    m = re.search(r"^RARITY\s*=\s*\{(.*?)\}", txt, re.M | re.S)
    kit = dict((k.lower(), v.lower()) for k, v in re.findall(r'"([A-Za-z]+)"\s*:\s*"(#[0-9A-Fa-f]{6})"', m.group(1))) if m else {}
    if not kit:
        print("note: tools/skyyui.py has no RARITY table this build can read - bag page colours not checked against the kit")
        return
    bad = ["%s page %s vs kit %s" % (r[1], r[3], kit.get(r[1].lower())) for r in BAG_RARITY if kit.get(r[1].lower()) != r[3].lower()]
    if bad:
        raise SystemExit("0.7.8: the bag page rarity colours differ from the kit RARITY palette (tools/skyyui.py): " + "; ".join(bad))
    print("bag page rarity colours match the kit RARITY palette (%s)" % ", ".join("%s %s" % (r[1], r[3]) for r in BAG_RARITY))
_kit_palette_check()
'''
rep('_gear_colour_check()' + LF + 'SMITH_JAVA = ', '_gear_colour_check()' + LF + KIT_CHECK + 'SMITH_JAVA = ')

# ================= config file template: the new switch =================
rep('    "#bags.freeRecipes=false",' + LF,
    '    "#bags.freeRecipes=false",' + LF
    + '    "# Cooked food in the Farming bag (true or false): false keeps cooked and prepared food (bread, pies, kebabs, salads, graded dishes)",' + LF
    + '    "# out of the Farming bag - it stays in your inventory; raw produce still goes in. Cooked food already in a bag stays until taken out.",' + LF
    + '    "#bags.cookedFood=false",' + LF)

# ================= SackDefs: the switch field, holds(), cooked() / homeOf() / catOf() =================
rep('defs.addField(CtField.make("public static final String[] HOLDS = " + _jarr([BAG_HOLDS[c] for c in BAG_CATS]) + ";", defs))' + LF,
    'defs.addField(CtField.make("public static final String[] HOLDS = " + _jarr([BAG_HOLDS[c] for c in BAG_CATS]) + ";", defs))' + LF
    + '# 0.7.8: Server Setup "Cooked food in the Farming bag" (bags.cookedFood, default OFF = Skyy\'s lock), bound by the config kit and loaded by' + LF
    + '# SackCfg.reload; read by catOf on every sweep, so a change applies at once. holds(ci) = the how-to-craft text of a bag type with the switch.' + LF
    + 'defs.addField(CtField.make("public static volatile boolean COOKED_FARM = false;", defs))' + LF
    + 'defs.addField(CtField.make("public static final String HOLDS_FARM_COOKED = " + jlit(FARM_HOLDS_COOKED) + ";", defs))' + LF
    + 'defs.addMethod(CtNewMethod.make("""' + LF
    + 'public static String holds(int ci) {' + LF
    + '  if (ci < 0 || ci >= HOLDS.length) return "";' + LF
    + '  if (COOKED_FARM && "Farming".equals(CATS[ci])) return HOLDS_FARM_COOKED;' + LF
    + '  return HOLDS[ci];' + LF
    + '}""", defs))' + LF)
NEW_CATOF = r'''# 0.7.8 THE COOKED / RAW RULE (Skyy 2026-09-30, "id keep cooked food out"): ONE helper, cooked(id) (the table + cooked_py at the top).
#  - homeOf(id) = the bag an item BELONGS to = the 0.7.7 catOf, unchanged (0.7.3: graded Skyy_Cook_* dishes and cook:prefix items are
#    Farming, the Skyy_Cook_Recipe_* recipe items never pool). Every path that READS a pool uses it: the bag page grid + counts, pickCat,
#    withdraw (clicks, Pick up all), the bench link and /craft materials (BagMirror.rebuild), haveOf - so cooked food already stored in a
#    Farming pool stays visible, can be taken out or used, and is never deleted.
#  - catOf(id) = where a NEW item may go: homeOf, but cooked food -> null while COOKED_FARM is off. Its only caller is SweepTask.sweep = the
#    auto-pickup routing and Deposit all, for every bag type and the Mythic Omni Bag.
defs.addMethod(CtNewMethod.make("""
public static boolean cooked(String itemId) {
  if (itemId == null) return false;
  if (itemId.startsWith("Skyy_")) {
    if (itemId.startsWith("Skyy_Cook_Recipe_")) return false;
    if (itemId.startsWith("Skyy_Cook_")) return true;
    try {
      Object b = System.getProperties().get("skyy.bridge");
      Object p = (b instanceof java.util.Map) ? ((java.util.Map) b).get("cook:prefix") : null;
      if (p instanceof String && ((String) p).startsWith("Skyy_Cook") && itemId.startsWith((String) p)) return true;
    } catch (Throwable t) { }
    return false;
  }
  if (!itemId.startsWith("Food_")) return false;
  if (itemId.equals("Food_Egg") || itemId.startsWith("Food_Egg_")) return false;
  if (itemId.endsWith("_Raw") || itemId.indexOf("_Raw_") >= 0) return false;
  return true;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String homeOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  // 0.7.3 (research/Cooking-Skill-Spec.md 3.4): graded dishes (the Grade is in the id, no metadata) belong to the Farming bag; the
  // Skyy_Cook_Recipe_* recipe-variant items never do; a cook:prefix bridge value (SkyyCooking) counts when it starts with Skyy_Cook.
  // 0.7.8: the same answer through cooked() - catOf keeps them out of NEW intake while the switch is off.
  if (itemId.startsWith("Skyy_")) return cooked(itemId) ? "Farming" : null;
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
defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  String c = homeOf(itemId);
  if (c != null && !COOKED_FARM && cooked(itemId)) return null;
  return c;
}""", defs))
'''
seg('defs.addMethod(CtNewMethod.make("""' + LF + 'public static String catOf(String itemId) {',
    '# 0.7.6: the bag caps are admin settings (SACK_CAPS): public static volatile, read on every sweep',
    ['if (itemId.startsWith("Skyy_Cook_")) return "Farming";', 'itemId.startsWith("Food_")', '.replace("@SMITH@", SMITH_JAVA).replace("@SAP@", TREE_SAP), defs))'],
    NEW_CATOF)
# jlit is defined below the class setup in 0.7.7 (before SackDefs is compiled) - make sure the new HOLDS_FARM_COOKED line can use it
assert s.index("def jlit(txt):") < s.index('HOLDS_FARM_COOKED = " + jlit(FARM_HOLDS_COOKED)')

# ================= SackPool: stored counts by homeOf + cookedTotal =================
rep('    if (cat.equals({PKG}.SackDefs.catOf((String) e.getKey()))) t += ((Long) e.getValue()).longValue();',
    '    if (cat.equals({PKG}.SackDefs.homeOf((String) e.getKey()))) t += ((Long) e.getValue()).longValue();')
rep('# integration fix: true when the pool of key k is loaded (or its file does not exist yet).',
    '# 0.7.8: how many COOKED items the pool of key k still holds (they belong to the Farming bag; the Farming tab notes them while' + LF
    + '# bags.cookedFood is off - they stay until taken out or used)' + LF
    + 'sp.addMethod(CtNewMethod.make(f"""' + LF
    + 'public static long cookedTotal(String k) {{' + LF
    + '  long t = 0L;' + LF
    + '  java.util.Iterator it = pool(k).entrySet().iterator();' + LF
    + '  while (it.hasNext()) {{' + LF
    + '    java.util.Map.Entry e = (java.util.Map.Entry) it.next();' + LF
    + '    if ({PKG}.SackDefs.cooked((String) e.getKey())) t += ((Long) e.getValue()).longValue();' + LF
    + '  }}' + LF
    + '  return t;' + LF
    + '}}""", sp))' + LF + LF
    + '# integration fix: true when the pool of key k is loaded (or its file does not exist yet).')

# ================= SackCfg: load bags.cookedFood (hand edits), log it; the row's after= hook =================
rep('    boolean fr = boolKey(p, "bags.freeRecipes", false);' + LF,
    '    boolean fr = boolKey(p, "bags.freeRecipes", false);' + LF
    + '    boolean ck = boolKey(p, "bags.cookedFood", false);' + LF)
rep('    boolean freeChanged = first || fr != FREE_RECIPES;' + LF,
    '    boolean freeChanged = first || fr != FREE_RECIPES;' + LF
    + '    boolean cookChanged = first || ck != com.skyy.sacks.SackDefs.COOKED_FARM;' + LF)
rep('    FREE_RECIPES = fr;' + LF + '    if (capsChanged) {' + LF,
    '    FREE_RECIPES = fr;' + LF + '    com.skyy.sacks.SackDefs.COOKED_FARM = ck;' + LF + '    if (capsChanged) {' + LF)
rep('    if (first && !ORDERWARNED && (cs > cm || cm > cr || cr > cl || cl > co)) {' + LF,
    '    if (cookChanged) {' + LF
    + '      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: cooked food in the Farming bag " + (ck ? "ON (cooked food and dishes pool into the Farming bag)" : "OFF (the Farming bag takes raw produce only; cooked food already stored stays until taken out)")); } catch (Throwable t5) { }' + LF
    + '    }' + LF
    + '    if (first && !ORDERWARNED && (cs > cm || cm > cr || cr > cl || cl > co)) {' + LF)
rep('# ================= KnowSync (0.7.7, research/Bag-Restructure-Spec.md 5.2 / 5.3): the bag recipe knowledge =================',
    '# 0.7.8: after= hook of the bags.cookedFood row (the kit set SackDefs.COOKED_FARM already; the next sweep uses it): one log line' + LF
    + 'scfg.addMethod(CtNewMethod.make(jt(r' + "'''" + LF
    + 'public static void cookedChanged(String key) {' + LF
    + '  try {' + LF
    + '    if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: cooked food in the Farming bag " + (@PKG@.SackDefs.COOKED_FARM ? "ON - cooked food and dishes pool into the Farming bag" : "OFF - the Farming bag takes raw produce only; cooked food already stored stays until taken out"));' + LF
    + '  } catch (Throwable t) { }' + LF
    + '}' + "'''" + '), scfg))' + LF + LF
    + '# ================= KnowSync (0.7.7, research/Bag-Restructure-Spec.md 5.2 / 5.3): the bag recipe knowledge =================')

# ================= pool readers use homeOf (the sweep keeps catOf) =================
rep('  String cat = {PKG}.SackDefs.catOf(id);' + LF + '  if (cat == null || !caps(p.getInventory()).containsKey(cat)) return 0;',
    '  // 0.7.8: homeOf - stored cooked food (Farming) can always be taken out with a Farming bag / the Omni on you' + LF
    + '  String cat = {PKG}.SackDefs.homeOf(id);' + LF + '  if (cat == null || !caps(p.getInventory()).containsKey(cat)) return 0;')
rep('  String c = {PKG}.SackDefs.catOf(id);' + LF + '  if (k != null && c != null && caps != null && caps.containsKey(c)) n += {PKG}.SackPool.get(k, id);',
    '  String c = {PKG}.SackDefs.homeOf(id);' + LF + '  if (k != null && c != null && caps != null && caps.containsKey(c)) n += {PKG}.SackPool.get(k, id);')
rep('    if (this.cat.equals(@PKG@.SackDefs.catOf((String) e.getKey()))) entries.add(e);',
    '    if (this.cat.equals(@PKG@.SackDefs.homeOf((String) e.getKey()))) entries.add(e);')
rep('    String cat = {PKG}.SackDefs.catOf(id);' + LF + '    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;',
    '    String cat = {PKG}.SackDefs.homeOf(id);' + LF + '    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;')
rep('b.set("#SkyySNbHolds.Text", "A " + cat + " Bag holds " + @PKG@.SackDefs.HOLDS[ci] + ". Matching',
    'b.set("#SkyySNbHolds.Text", "A " + cat + " Bag holds " + @PKG@.SackDefs.holds(ci) + ". Matching')
rep('    if (sm > 0L) shown = "Hides and fabric scraps now live in the Smithing bag - " + sm + " items wait there (Smithing tab)";' + LF + '  }' + LF,
    '    if (sm > 0L) shown = "Hides and fabric scraps now live in the Smithing bag - " + sm + " items wait there (Smithing tab)";' + LF + '  }' + LF
    + '  // 0.7.8 (Skyy 2026-09-30): cooked food stays out of the Farming bag; what is already stored stays in the grid and can be taken out' + LF
    + '  if (shown.length() == 0 && "Farming".equals(this.cat) && !@PKG@.SackDefs.COOKED_FARM) {' + LF
    + '    long ck = @PKG@.SackPool.cookedTotal(k);' + LF
    + '    if (ck > 0L) shown = "Cooked food no longer goes into this bag - " + num(ck) + (ck == 1L ? " cooked item is" : " cooked items are") + " still here to take out";' + LF
    + '  }' + LF)

# ================= review fixes =================
# (finding 1) the page draws 4 x 9 = 36 cells from the count-sorted entries; with 36+ raw entries, low-count cooked food could sit past cell
# 36 while the note says it is there - and since cooked food can no longer enter the bag, taking it out is the whole point. While the switch
# is off, the Farming tab lists stored cooked entries first (two lists after the CountCmp sort, each keeping the count order; no lambdas).
rep('  java.util.Collections.sort(entries, new @PKG@.CountCmp());' + LF + '  for (int r = 0; r < 4; r++) {' + LF,
    '  java.util.Collections.sort(entries, new @PKG@.CountCmp());' + LF
    + '  // 0.7.8 review fix: 36 cells - while cooked food stays out, stored cooked entries come FIRST on the Farming tab (each group keeps the' + LF
    + '  // count order), so none hides behind raw produce; taking it out is the only way it leaves' + LF
    + '  if ("Farming".equals(this.cat) && !@PKG@.SackDefs.COOKED_FARM) {' + LF
    + '    java.util.ArrayList ckFirst = new java.util.ArrayList();' + LF
    + '    java.util.ArrayList rawRest = new java.util.ArrayList();' + LF
    + '    for (int q = 0; q < entries.size(); q++) {' + LF
    + '      java.util.Map.Entry ce = (java.util.Map.Entry) entries.get(q);' + LF
    + '      if (@PKG@.SackDefs.cooked((String) ce.getKey())) ckFirst.add(ce); else rawRest.add(ce);' + LF
    + '    }' + LF
    + '    ckFirst.addAll(rawRest);' + LF
    + '    entries = ckFirst;' + LF
    + '  }' + LF
    + '  for (int r = 0; r < 4; r++) {' + LF)
# (finding 3) Deposit all with only cooked food on hand said "nothing to deposit (or sack full)" - no hint that it is refused on purpose.
# cookedHeld counts the cooked items in storage + hotbar + backpack (the containers Deposit all sweeps); world thread like the sweep.
HELD = Q(r'''# 0.7.8 review fix: how many cooked items the inventory holds (storage, hotbar, backpack = what Deposit all sweeps); world thread. Deposit
# all on the Farming tab says they stay in the inventory while bags.cookedFood is off.
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static int cookedHeld(@INV@ inv) {
  if (inv == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      if (@PKG@.SackDefs.cooked(it.getItemId())) n += it.getQuantity();
    }
  }
  return n;
}@Q3@), swp))
''')
rep('# withdraw up to n of an item into STORAGE; returns how many actually left the pool' + LF,
    HELD + '# withdraw up to n of an item into STORAGE; returns how many actually left the pool' + LF)
rep('      this.info = moved > 0 ? ("deposited " + moved + " items") : "nothing to deposit (or sack full)";' + LF,
    '      this.info = moved > 0 ? ("deposited " + moved + " items") : "nothing to deposit (or sack full)";' + LF
    + '      // 0.7.8 review fix: on the Farming tab, say that the cooked food on hand is refused on purpose (bags.cookedFood off)' + LF
    + '      if ("Farming".equals(this.cat) && !{PKG}.SackDefs.COOKED_FARM && {PKG}.SweepTask.cookedHeld(player.getInventory()) > 0) this.info = this.info + " - cooked food stays in your inventory";' + LF)

# ================= the Server Setup row =================
COOK_HELP = "On: cooked and prepared food goes into the Farming bag too. Off: raw produce only, cooked stays out."
assert len(COOK_HELP) <= 100, len(COOK_HELP)
rep('     "field:SackCfg.FREE_RECIPES@config.properties:bags.freeRecipes;confirm=always;after=SackCfg.freeChanged"),' + LF + '] + [',
    '     "field:SackCfg.FREE_RECIPES@config.properties:bags.freeRecipes;confirm=always;after=SackCfg.freeChanged"),' + LF
    + '    # 0.7.8 (Skyy 2026-09-30, "id keep cooked food out"): default OFF = Skyy\'s lock; ON = the 0.7.7 routing. Live: catOf reads it on every' + LF
    + '    # sweep; cooked food already stored is never touched either way.' + LF
    + '    ("bags.cookedFood", "Cooked food in the Farming bag", "bags", "bool", "false", "", "", "", "", "live",' + LF
    + '     "' + COOK_HELP + '",' + LF
    + '     "field:SackDefs.COOKED_FARM@config.properties:bags.cookedFood;after=SackCfg.cookedChanged"),' + LF
    + '] + [')

# ================= ready line =================
rep('bag recipes unlock through SkyyCollections, free without it or with bags.freeRecipes), /craft (',
    'bag recipes unlock through SkyyCollections, free without it or with bags.freeRecipes; the Farming bag keeps raw produce - cooked food stays out unless bags.cookedFood is on), /craft (')

# ================= self-checks =================
assert s.count("SackDefs.catOf(") == 1 and "String cat = {PKG}.SackDefs.catOf(id);" + LF + "      if (cat == null) continue;" in s, \
    "catOf (new intake) must have exactly one caller: SweepTask.sweep"
assert s.count("SackDefs.homeOf(") == 5, "homeOf: catTotal, withdraw, haveOf, the page grid, BagMirror.rebuild"
assert s.index("public static volatile boolean COOKED_FARM = false;") < s.index("public static boolean cooked(String itemId) {") \
    < s.index("public static String homeOf(String itemId) {") < s.index("public static String catOf(String itemId) {")
assert s.index("public static String catOf(String itemId) {") < s.index("public static long catTotal(String k, String cat) {{") \
    < s.index("public static long cookedTotal(String k) {{")
assert s.index("public static long cookedTotal(String k) {{") < s.index("public void render(@UCB@ b, @UEB@ ev, @PLA@ player, String k, java.util.HashMap caps, java.util.HashMap ranks) {")
assert '#aa00aa", "#cc66cc", 6' not in s and '"#cc66cc", "#cc66cc", 6' in s
assert "#bags.cookedFood=false" in s and '"bags.cookedFood", "Cooked food in the Farming bag"' in s
assert 'BAG_MAT = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread"' in s, "BAG_MAT unchanged"
import re as _re
for m in _re.finditer(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in m.group(1), "UI id with underscore: " + m.group(1)
for pay in ('"tab:" + cats[c]', '"craft")', '"cell:" + idx + ":stack"', '"cell:" + idx + ":one"', '"pickall"', '"depall"'):
    assert pay in s, "bag page payload lost: " + pay
assert s.count("0.7.7") > 0 and 'VERSION = "0.7.8"' in s
# review fixes: cooked first on the Farming grid (after the sort, before the cells), cookedHeld before its caller, the Deposit all hint
assert s.index("java.util.Collections.sort(entries, new @PKG@.CountCmp());") < s.index("ckFirst.addAll(rawRest);") \
    < s.index('b.appendInline("#SkyySBody", "Group #SkyySRow" + r')
assert s.index("public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers) {{") \
    < s.index("public static int cookedHeld(@INV@ inv) {") < s.index("public void handleDataEvent({REF} ref, {ST} st, String data) {{") \
    and s.count("SweepTask.cookedHeld(") == 1 and s.count(" - cooked food stays in your inventory") == 1
assert '(ck == 1L ? " cooked item is" : " cooked items are")' in s

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
