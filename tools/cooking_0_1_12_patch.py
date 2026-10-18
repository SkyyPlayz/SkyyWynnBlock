"""Derive SkyyCooking/build_skyycooking_0.1.12.py from the LIVE SkyyCooking 0.1.11 (build_skyycooking_0.1.11.py = the tools/deploy_set.py SET
pin, DERIVED by tools/cooking_0_1_11_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.1.11 (nothing else changed). Line endings kept.
Run:  python tools/cooking_0_1_12_patch.py   then   python SkyyCooking/build_skyycooking_0.1.12.py   (never --deploy)
Check: python SkyyCooking/test_skyycooking_0.1.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.1.12 = OUR OWN PIES, SALAD, DRINKS, BUTTER + SLICED BREAD (lean round cook12). SKYY'S WORDS (docs/answered/project.md 2026-10-18, popup):
 Q "Connor's More Food Stuff has no licence and uses heal effects missing from the current game, so it can't be packed yet. What now?"
 -> "Make our own dishes" (earlier the same day, on its CurseForge page: "this would be good too, if we can use it"). That mod is All
 Rights Reserved: NOTHING of it is used - no file opened, no id, recipe, number or name; research/Farming-Mods-Survey.md section 1 only
 told us the KINDS of food (pies, a salad, drinks, butter, sliced bread). Every dish below is ours: our names, our recipes from vanilla
 ingredients only, our numbers from SkyyCooking's own food-family rules, vanilla models / icons / sounds read from Assets.zip at build time.
 1. TWELVE NEW OWN DISHES (OWN list, Cooking Bench, graded G0-G12 like every own dish, gradedOwn): base ids Food_Skyy_<Name> (graded
    copies Skyy_Cook_Food_Skyy_<Name>_G<g>, so cook:prefix / the Farming sack / the Food Pouch take them with no change):
      tier  dish                 bench      recipe (vanilla ids)                                                     makes
      T1    Butter               Prepared 3s  1 Milk Bucket (resource Milk_Bucket)                                    1 + the bucket back
      T1    Sliced Bread         Baked 3s     1 Ingredient_Dough + 2 Fuel                                             2
      T1    Berry Cordial        Prepared 1s  1 water Tankard (*Deco_Tankard_State_Filled_Water) + 3 Red Berries      1 + the Tankard back
      T1    Vegetable Broth      Baked 3s     1 water Tankard + 1 Carrot + 1 Onion + 1 Salt + 1 Fuel                  1 + the Tankard back
      T2    Farmhouse Salad      Prepared 1s  1 Lettuce + 1 Tomato + 1 Turnip + 1 Cheese                              1
      T2    Spiced Cider         Prepared 2s  1 water Tankard + 2 Apples + 1 Spices                                   1 + the Tankard back
      T2    Pinkberry Milkshake  Prepared 2s  1 Milk Bucket + 2 Pinkberries                                           1 + the bucket back
      T3    Tropical Smoothie    Prepared 2s  1 Milk Bucket + 1 Mango + 1 Coconut + 2 Red Berries                     1 + the bucket back
      T3    Cottage Pie          Baked 5s     1 Dough + 1 Meats + 2 Potatoes + 3 Fuel                                 1
      T3    Fisherman's Pie      Baked 5s     1 Dough + 2 Raw Fish + 1 Onion + 3 Fuel                                 1
      T3    Coconut Cream Pie    Baked 5s     1 Dough + 1 Coconut + 1 Milk Bucket + 3 Fuel                            1 + the bucket back
      T3    Forager's Pie        Baked 5s     1 Dough + 2 Mushrooms + 1 Cauliflower + 3 Fuel                          1
    Containers come back like vanilla's own recipes do (Food_Cheese returns Container_Bucket, Ingredient_Dough returns the empty
    Deco_Tankard): own_returns() adds them from the inputs, so nothing is lost and no new container item exists.
 2. NUMBERS = SkyyCooking's food-family rules, nothing new (0.1.8 / 0.1.10, unchanged): the recipe's ingredient families set the bars
    (Veggie Health, Fruit Mana, Meat Stamina, Mushroom Strength, Grain = half Health + half Stamina, Dairy, Egg & Fish = half Stamina +
    half Mana; share per family 1 / 0.6 / 0.45 for 1 / 2 / 3 families), the tier sets the size (instant Health / Mana 5 / 8 / 12 %, Stamina
    10 / 20 / 30 %; over time 0.5 / 0.8 / 1.2 % every 2 s, Stamina +10 / 20 / 30 % max, Strength +2 / 4 / 6), Grade x (1 + 0.32 g), 6:00
    x 2^(g/5). Grade 0 values (instant; over time), printed by the build ("0.1.12 new dishes"):
      (now = instant, % of max; then = the over-time buff, 6:00 at Grade 0; XP = base Cooking XP per craft)
      T1 Butter               Dairy                now Mana 2.5%, Stamina 5%              then Mana 0.3%/2s, Stamina +5%                           850 XP
      T1 Sliced Bread         Grain                now Health 2.5%, Stamina 5%            then Health 0.3%/2s, Stamina +5%                        8850 XP
      T1 Berry Cordial        Fruit                now Mana 5%                            then Mana 0.5%/2s                                        850 XP
      T1 Vegetable Broth      Veggie               now Health 5%                          then Health 0.5%/2s                                     1350 XP
      T2 Farmhouse Salad      Veggie+Dairy         now Health 4.8%, Mana 2.4%, Stamina 6% then Health 0.5%/2s, Mana 0.2%/2s, Stamina +6%          2550 XP
      T2 Spiced Cider         Fruit                now Mana 8%                            then Mana 0.8%/2s                                       3650 XP
      T2 Pinkberry Milkshake  Fruit+Dairy          now Mana 7.2%, Stamina 6%              then Mana 0.7%/2s, Stamina +6%                          1400 XP
      T3 Tropical Smoothie    Fruit+Dairy          now Mana 10.8%, Stamina 9%             then Mana 1.1%/2s, Stamina +8.9%                        2000 XP
      T3 Cottage Pie          Veggie+Meat+Grain    now Health 8.1%, Stamina 20.2%         then Health 0.8%/2s, Stamina +20.4%                    11100 XP
      T3 Fisherman's Pie      Veggie+Grain+Dairy   now Health 8.1%, Mana 2.7%, Stamina 13.5% then Health 0.8%/2s, Mana 0.3%/2s, Stamina +13.8%      14950 XP
      T3 Coconut Cream Pie    Fruit+Grain+Dairy    now Health 2.7%, Mana 8.1%, Stamina 13.5% then Health 0.3%/2s, Mana 0.8%/2s, Stamina +13.8%      12350 XP
      T3 Forager's Pie        Veggie+Mushroom+Grain now Health 8.1%, Stamina 6.8%          then Health 0.8%/2s, Stamina +6.6%, Strength +2.8      10850 XP
    BALANCE (vs the existing dishes): the tiers sit where their effort sits - T1 = one cheap step (one bucket of milk, one dough, one
    tankard of water: the price of vanilla's T1 Roast Vegetable / Grilled Fish up to a little more), T2 = 3-4 ingredients like the vanilla
    skewers and salads, T3 = a dough + 3 fuel pie or a 4-ingredient smoothie like vanilla's T3 pies / Caesar / Popcorn. Sliced Bread: one
    dough + 2 fuel gives TWO T1 slices; bread (T2) is one dough + 3 fuel for ONE loaf: the two slices restore about what the loaf does at once
    (2 x 2.5 % health + 2 x 5 % stamina vs 4 % + 10 %) but only a T1 buff (one buff per bar - a second slice never adds a second buff), so
    slicing is a convenience, not a gain. Butter (one milk) is a weaker cousin of Cheese's role with a small buff (Cheese stays a raw
    snack). No new effect: the instant part is the same inline copy of vanilla Food_Instant_Heal_T1 every dish uses, the over-time parts are
    this jar's Skyy_Cook_Fx_<bar>_<k> ladder (new dishes only add ladder steps their weights need; Food_Instant_Heal_T2 / T3 - missing
    from the current game - are never named).
    COOKING XP = the LOCKED difficulty rule (Skyy 2026-10-04: "the easier to craft the less xp. the harder to craft the more."): chain raw x
    950 x (20 % + 15 % per extra crafting step + 5 % Prepared / 10 % Baked + 5 % per ingredient tier above 1, Milk T2), x the craft's
    output count (new: Sliced Bread makes 2 - every other own dish makes 1, so their XP is unchanged). The build's checks still hold: an
    easy dish pays less than any 3-step one, no own dish is a much faster levelling route than the vanilla best (<= 1.15 x), the meat-pie
    route keeps level 50 in 25-30 h. Values printed by the build ("0.1.8 own dish XP").
 3. LOOKS (vanilla, read from Assets.zip at build time, never committed): pies = the Pie model (Forager's Pie with the vanilla Mushroom pie
    texture), salad = the Caesar salad, Sliced Bread = the bread, Butter = the Cheese model, drinks = the vanilla filled Tankard (Cordial,
    Broth, Cider) / filled Mug (Milkshake, Smoothie) model, icon, icon angle and the vanilla drink animation (Deco_Tankard's
    PlayerAnimationsId; the eat charge plays its "Consume" animation like Template_Food's, no mouth crumbs) + drink sounds (SFX_Health_Potion_Low_Drink_Local while drinking, SFX_Water_MoveOut when done). Drinks still eat
    through the food chain (Cooking's 1.875 s fast eat, never cancelled by a hit) so the Food Pouch takes them like any dish. Quality by
    tier: T1 Common, T2 Uncommon, T3 Rare (the vanilla dishes' pattern). Art of our own = follow-up.
 4. ORDER: the OWN list is sorted by tier, then name (PROJECT-RULES "sort by tier everywhere"): the Server Setup graded list, /cook's dish
    list and the Food Pouch's tie order follow it. The Cooking Bench's own recipe order is the engine's (UNVERIFIED).
 5. NOT TIER-TAGGED: food is "left untagged on purpose" in tools/tier_tags.py (its docstring), so no tier tag row is added; the tooltip
    shows the tier through the Quality colour like every dish.
 6. SAVED DATA: none changes. New item ids only; cooking.properties is not rewritten (xp.<new dish> lines missing = the built-in value,
    the loader's rule since 0.1; gradedOwn grades them even when a live graded= line lists only the old dishes); supplies files untouched.
 ROLLBACK: to 0.1.11 = redeploy SkyyCooking-0.1.11.jar. Safe until players own a new dish; after that the new dishes (and Food Pouch
    stores holding them: pouch.<id> lines stay in the store file, unusable, and come back when 0.1.12+ returns) become Invalid Items -
    deploy-forward only once they exist in the world. No config / saved-data migration to undo.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.11.py"), os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.12.py"))
assert P.has('VERSION = "0.1.11"\n') and P.has("DERIVED from build_skyycooking_0.1.10.py by tools/cooking_0_1_11_patch.py") and not P.has("OUR OWN PIES"), \
    "not the generated SkyyCooking 0.1.11 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.12 = OUR OWN PIES"):].rstrip() + "\n\n"

# ---------- docstring + version
P.rep('''"""SkyyCooking 0.1.11 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.10.py by tools/cooking_0_1_11_patch.py
(0.1.10 / 0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_10_patch.py /
_0_1_9_patch.py / _0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py /
_0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.11.py           -> SkyyCooking/SkyyCooking-0.1.11.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''', '''"""SkyyCooking 0.1.12 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.11.py by tools/cooking_0_1_12_patch.py
(0.1.11 / 0.1.10 / 0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by
tools/cooking_0_1_11_patch.py / _0_1_10_patch.py / _0_1_9_patch.py / _0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py / _0_1_5_patch.py /
_0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.12.py           -> SkyyCooking/SkyyCooking-0.1.12.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''' + NOTE)
P.rep('VERSION = "0.1.11"\n', 'VERSION = "0.1.12"\n')

# ---------- 1. the twelve new dishes, their looks + container returns; the whole OWN list sorted by tier, then name
P.rep('''    ("Food_Skyy_Lunch_Tray", "Lunch Tray", 3, "Baked", 5, "Food_Popcorn", [("I", "Ingredient_Dough", 1), ("R", "Meats", 1), ("R", "Fruits", 1), ("R", "Mushrooms", 1), ("R", "Fuel", 3)]),
]
OWN_IDS = [o[0] for o in OWN]
''', '''    ("Food_Skyy_Lunch_Tray", "Lunch Tray", 3, "Baked", 5, "Food_Popcorn", [("I", "Ingredient_Dough", 1), ("R", "Meats", 1), ("R", "Fruits", 1), ("R", "Mushrooms", 1), ("R", "Fuel", 3)]),
]
# ---- 0.1.12 (Skyy 2026-10-18 popup: "Make our own dishes"): our own pies, salad, drinks, butter and sliced bread - our names, recipes and
# numbers, vanilla ingredients only (see the 0.1.12 note at the top). _TW = a tankard of water (the vanilla Ingredient_Dough input form).
_TW = "*Deco_Tankard_State_Filled_Water"
NEW_OWN = [
    ("Food_Skyy_Butter", "Butter", 1, "Prepared", 3, "Food_Bread", [("R", "Milk_Bucket", 1)]),
    ("Food_Skyy_Sliced_Bread", "Sliced Bread", 1, "Baked", 3, "Food_Bread", [("I", "Ingredient_Dough", 1), ("R", "Fuel", 2)]),
    ("Food_Skyy_Berry_Cordial", "Berry Cordial", 1, "Prepared", 1, "Food_Kebab_Fruit", [("I", _TW, 1), ("I", "Plant_Fruit_Berries_Red", 3)]),
    ("Food_Skyy_Vegetable_Broth", "Vegetable Broth", 1, "Baked", 3, "Food_Vegetable_Cooked", [("I", _TW, 1), ("I", "Plant_Crop_Carrot_Item", 1), ("I", "Plant_Crop_Onion_Item", 1), ("I", "Ingredient_Salt", 1), ("R", "Fuel", 1)]),
    ("Food_Skyy_Farmhouse_Salad", "Farmhouse Salad", 2, "Prepared", 1, "Food_Salad_Caesar", [("I", "Plant_Crop_Lettuce_Item", 1), ("I", "Plant_Crop_Tomato_Item", 1), ("I", "Plant_Crop_Turnip_Item", 1), ("I", "Food_Cheese", 1)]),
    ("Food_Skyy_Spiced_Cider", "Spiced Cider", 2, "Prepared", 2, "Food_Kebab_Fruit", [("I", _TW, 1), ("I", "Plant_Fruit_Apple", 2), ("I", "Ingredient_Spices", 1)]),
    ("Food_Skyy_Pinkberry_Milkshake", "Pinkberry Milkshake", 2, "Prepared", 2, "Food_Kebab_Fruit", [("R", "Milk_Bucket", 1), ("I", "Plant_Fruit_Pinkberry", 2)]),
    ("Food_Skyy_Tropical_Smoothie", "Tropical Smoothie", 3, "Prepared", 2, "Food_Salad_Berry", [("R", "Milk_Bucket", 1), ("I", "Plant_Fruit_Mango", 1), ("I", "Plant_Fruit_Coconut", 1), ("I", "Plant_Fruit_Berries_Red", 2)]),
    ("Food_Skyy_Cottage_Pie", "Cottage Pie", 3, "Baked", 5, "Food_Pie_Meat", [("I", "Ingredient_Dough", 1), ("R", "Meats", 1), ("I", "Plant_Crop_Potato_Item", 2), ("R", "Fuel", 3)]),
    ("Food_Skyy_Fisherman_Pie", "Fisherman's Pie", 3, "Baked", 5, "Food_Pie_Pumpkin", [("I", "Ingredient_Dough", 1), ("I", "Food_Fish_Raw", 2), ("I", "Plant_Crop_Onion_Item", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Coconut_Cream_Pie", "Coconut Cream Pie", 3, "Baked", 5, "Food_Pie_Apple", [("I", "Ingredient_Dough", 1), ("I", "Plant_Fruit_Coconut", 1), ("R", "Milk_Bucket", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Forager_Pie", "Forager's Pie", 3, "Baked", 5, "Food_Pie_Meat", [("I", "Ingredient_Dough", 1), ("R", "Mushrooms", 2), ("I", "Plant_Crop_Cauliflower_Item", 1), ("R", "Fuel", 3)]),
]
NEW_IDS = [o[0] for o in NEW_OWN]
assert len(NEW_IDS) == 12 and not set(NEW_IDS) & set(o[0] for o in OWN) and len(set(o[1] for o in OWN + NEW_OWN)) == len(OWN) + 12, "0.1.12: 12 new ids + names"
OWN_QTY = {"Food_Skyy_Sliced_Bread": 2}                 # makes 2 (every other own dish 1)
# looks: (kind, pie texture) - kind "tankard" / "mug" = the vanilla filled drink item's model + icon + drink animation + drink sounds,
# "cheese" = the vanilla Cheese model + icon; None = the donor dish's own look
NEW_LOOK = {"Food_Skyy_Butter": ("cheese", None), "Food_Skyy_Berry_Cordial": ("tankard", None), "Food_Skyy_Vegetable_Broth": ("tankard", None),
            "Food_Skyy_Spiced_Cider": ("tankard", None), "Food_Skyy_Pinkberry_Milkshake": ("mug", None), "Food_Skyy_Tropical_Smoothie": ("mug", None),
            "Food_Skyy_Forager_Pie": (None, "Items/Consumables/Food/Pie_Textures/Mushroom.png")}
TIER_QUALITY = {1: "Common", 2: "Uncommon", 3: "Rare"}
DRINK_SFX, DRINK_DONE_SFX = "SFX_Health_Potion_Low_Drink_Local", "SFX_Water_MoveOut"
_SND = set(os.path.basename(n)[:-5] for n in ANAMES if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json"))
assert DRINK_SFX in _SND and DRINK_DONE_SFX in _SND, "0.1.12: a drink sound is missing from Assets.zip"
RETURNS = {("R", "Milk_Bucket"): "Container_Bucket", ("I", _TW): "Deco_Tankard"}   # vanilla Food_Cheese / Ingredient_Dough return these
for _rid in RETURNS.values(): assert _rid in V_ITEMS, "0.1.12: container %s missing" % _rid
assert "Filled_Water" in (rd(V_ITEMS["Deco_Tankard"]).get("State") or {}), "0.1.12: the water Tankard state is gone"
def own_returns(ins):
    out = []
    for k, x, q in ins:
        if (k, x) in RETURNS: out.append({"ItemId": RETURNS[(k, x)], "Quantity": q})
    return out
def own_look(oid, t, v):
    """0.1.12: a new dish's vanilla look (model / texture / icon / animation / sounds) + its tier's Quality, on the flat donor JSON v"""
    if oid not in NEW_IDS: return
    v["Quality"] = TIER_QUALITY[t]
    kind, tex = NEW_LOOK.get(oid, (None, None))
    bt = v.setdefault("BlockType", {})
    if tex:
        bt["CustomModelTexture"] = [{"Texture": tex, "Weight": 1}]
    if kind == "cheese":
        ch = rd(V_ITEMS["Food_Cheese"])
        v["BlockType"] = dict((k, copy.deepcopy(x)) for k, x in ch["BlockType"].items())
        v["Icon"], v["Scale"] = ch["Icon"], ch["Scale"]
        v.pop("IconProperties", None)
    elif kind in ("tankard", "mug"):
        src = rd(V_ITEMS["Deco_Tankard" if kind == "tankard" else "Deco_Mug"])
        st = src["State"]["Filled_Water"]
        for k in ("CustomModel", "CustomModelTexture", "CustomModelScale", "CustomModelAnimation", "Opacity", "HitboxType"):
            bt.pop(k, None)
            if k in st["BlockType"]: bt[k] = copy.deepcopy(st["BlockType"][k])
        v["Icon"], v["Scale"], v["IconProperties"] = st["Icon"], st["Scale"], copy.deepcopy(st["IconProperties"])
        v["PlayerAnimationsId"] = copy.deepcopy(src["PlayerAnimationsId"])
        iv = v.setdefault("InteractionVars", {})
        # the charge plays the item's own "Consume" animation (= the drink animation above), like Template_Food's charge; the donor's
        # side-bite animation + mouth crumbs are dropped
        iv["Consume_Charge"] = {"Interactions": [{"Parent": "Consume_Charge_Food_T1_Inner", "Effects": {"ItemAnimationId": "Consume"}}]}
        iv["ConsumeSFX"] = {"Interactions": [{"Parent": "Consume_SFX", "Effects": {"LocalSoundEventId": DRINK_SFX}}]}
        iv["ConsumedSFX"] = {"Interactions": [{"Parent": "Consumed_SFX", "Effects": {"LocalSoundEventId": DRINK_DONE_SFX}}]}
    for p in [v.get("Icon"), bt.get("CustomModel"), bt.get("CustomModelAnimation")] + [x.get("Texture") for x in bt.get("CustomModelTexture", [])]:
        if p and "Common/" + p not in V_COMMON: raise SystemExit("0.1.12: %s's look file %s is not in Assets.zip" % (oid, p))
    an = (v.get("PlayerAnimationsId") or {}).get("Animations", {}) if isinstance(v.get("PlayerAnimationsId"), dict) else {}
    for a in an.values():
        for k in ("FirstPerson", "ThirdPerson"):
            if a.get(k) and "Common/" + a[k] not in V_COMMON: raise SystemExit("0.1.12: %s's animation %s is not in Assets.zip" % (oid, a[k]))
OWN = OWN + NEW_OWN
OWN.sort(key=lambda o: (o[2], o[1]))                  # PROJECT-RULES: sort by tier, then name
OWN_IDS = [o[0] for o in OWN]
''')
P.rep('''                       "Output": [{"ItemId": oid, "Quantity": 1}],
''', '''                       "Output": [{"ItemId": oid, "Quantity": OWN_QTY.get(oid, 1)}] + own_returns(ins),   # 0.1.12: + containers back
''')
P.rep('''               "Food_Skyy_Hearty_Stew": ["Veggie", "Meat", "Mushroom"], "Food_Skyy_Lunch_Tray": ["Fruit", "Meat", "Mushroom", "Grain"]}
''', '''               "Food_Skyy_Hearty_Stew": ["Veggie", "Meat", "Mushroom"], "Food_Skyy_Lunch_Tray": ["Fruit", "Meat", "Mushroom", "Grain"]}
EXPECT_FAMS.update({"Food_Skyy_Butter": ["Dairy"], "Food_Skyy_Sliced_Bread": ["Grain"], "Food_Skyy_Berry_Cordial": ["Fruit"],   # 0.1.12
                    "Food_Skyy_Vegetable_Broth": ["Veggie"], "Food_Skyy_Farmhouse_Salad": ["Veggie", "Dairy"], "Food_Skyy_Spiced_Cider": ["Fruit"],
                    "Food_Skyy_Pinkberry_Milkshake": ["Fruit", "Dairy"], "Food_Skyy_Tropical_Smoothie": ["Fruit", "Dairy"],
                    "Food_Skyy_Cottage_Pie": ["Veggie", "Meat", "Grain"], "Food_Skyy_Fisherman_Pie": ["Veggie", "Grain", "Dairy"],
                    "Food_Skyy_Coconut_Cream_Pie": ["Fruit", "Grain", "Dairy"], "Food_Skyy_Forager_Pie": ["Veggie", "Mushroom", "Grain"]})
''')
P.rep('''for oid, nm, t, cat, sec, donor, ins in OWN:
    v = flat_dish(donor)
    v.pop("Recipe", None)
''', '''for oid, nm, t, cat, sec, donor, ins in OWN:
    v = flat_dish(donor)
    v.pop("Recipe", None)
    own_look(oid, t, v)                                # 0.1.12: the new dishes' vanilla looks + Quality by tier (no-op for the older ones)
''')

# ---------- 2. the 0.1.10 legacy all-round levels: only the dishes 0.1.9 had (a new dish never had an all-round share)
P.rep('''for (_d, _g) in list(DISH_NUM):
    if _d in RAW: continue
    for _b, (_k, _v) in numbers(DISH_FAMS[_d], DISH_TIER[_d], _g)[3].items(): USED_0_1_9[_b].add(_k)
ALLROUND = _AR_NOW
LEGACY_FX = dict((b, sorted(USED_0_1_9[b] - USED[b])) for b in BARS)
assert all(USED[b] <= USED_0_1_9[b] for b in BARS) and not LEGACY_FX["Strength"], "0.1.10: the families' own levels are a subset of 0.1.9's"
''', '''for (_d, _g) in list(DISH_NUM):
    if _d in RAW or _d in NEW_IDS: continue            # 0.1.12: the new dishes never had an all-round share
    for _b, (_k, _v) in numbers(DISH_FAMS[_d], DISH_TIER[_d], _g)[3].items(): USED_0_1_9[_b].add(_k)
ALLROUND = _AR_NOW
USED_NEW = dict((b, set()) for b in BARS)              # 0.1.12: the ladder steps the new dishes apply
for (_d, _g) in list(DISH_NUM):
    if _d in NEW_IDS:
        for _b, (_k, _v) in DISH_NUM[(_d, _g)][3].items(): USED_NEW[_b].add(_k)
LEGACY_FX = dict((b, sorted(USED_0_1_9[b] - USED[b])) for b in BARS)
assert all(USED[b] - USED_NEW[b] <= USED_0_1_9[b] for b in BARS) and not LEGACY_FX["Strength"], "0.1.10: the families' own levels are a subset of 0.1.9's"
print("0.1.12 new ladder steps (only the new dishes need them): " + ", ".join("%s %s" % (b, sorted(USED[b] - USED_0_1_9[b])) for b in BARS))
''')

# ---------- 3. the asset self-check: an own recipe outputs itself first, then only the containers its inputs return; '*' state inputs
P.rep('''    elif iid in OWN_IDS:
        rc = node["Recipe"]
        if [o["ItemId"] for o in rc["Output"]] != [iid]: errs.append("own dish %s: its recipe must output itself" % iid)
        for inp in rc["Input"]:
            if "ItemId" in inp: need("item", inp["ItemId"], "recipe " + iid)
''', '''    elif iid in OWN_IDS:
        rc = node["Recipe"]
        if rc["Output"][0]["ItemId"] != iid or rc["Output"][1:] != own_returns(inputs_of(rc)): errs.append("own dish %s: its recipe must output itself (+ its containers)" % iid)
        for inp in rc["Input"]:
            if "ItemId" in inp and inp["ItemId"].startswith("*"):   # 0.1.12: '*<Item>_State_<State>' (vanilla Ingredient_Dough's form)
                _m = re.match(r"^\\*(\\w+?)_State_(\\w+)$", inp["ItemId"])
                if not _m or _m.group(1) not in V_ITEMS or _m.group(2) not in (rd(V_ITEMS[_m.group(1)]).get("State") or {}):
                    errs.append("recipe %s: unknown state input %r" % (iid, inp["ItemId"]))
            elif "ItemId" in inp: need("item", inp["ItemId"], "recipe " + iid)
''')

# ---------- 4. XP: an own dish's COOK entry carries its output count; XP per craft = per unit x the count (1 for every older dish)
P.rep('''    COOK[_oid] = (inputs_of(_r), 1, float(_r["TimeSeconds"]), False)
for _oid in OWN_IDS:
    DIFF[_oid] = diff_share(_oid)
    XP[_oid] = rnd_to(K_XP * DIFF[_oid] * chain_raw(_oid) / 100.0, 50)
''', '''    COOK[_oid] = (inputs_of(_r), int(_r["Output"][0]["Quantity"]), float(_r["TimeSeconds"]), False)   # 0.1.12: Sliced Bread makes 2
for _oid in OWN_IDS:
    DIFF[_oid] = diff_share(_oid)
    XP[_oid] = rnd_to(K_XP * DIFF[_oid] * chain_raw(_oid) * COOK[_oid][1] / 100.0, 50)   # 0.1.12: x the output count (1 = unchanged)
''')
P.rep('''print("0.1.8 own dish XP (difficulty share %, chain raw -> XP): " + ''', '''print("0.1.12 new dishes (tier, families, instant %; over time; XP per craft): " + "; ".join("%s T%d %s inst %s; over %s; %d XP" % (
    _oid, DISH_TIER[_oid], "+".join(DISH_FAMS[_oid]), ", ".join("%s %s" % (b, pct_s(v)) for b, v in DISH_NUM[(_oid, 0)][1].items()),
    ", ".join("%s %s" % (b, pct_s(v[1])) for b, v in DISH_NUM[(_oid, 0)][3].items()), XP[_oid]) for _oid in NEW_IDS))
print("0.1.8 own dish XP (difficulty share %, chain raw -> XP): " + ''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.1.12: no system / command added"
P.finish()
