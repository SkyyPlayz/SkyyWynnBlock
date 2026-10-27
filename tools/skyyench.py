"""skyyench - THE ENCHANTED MATERIALS TABLE (Gathering-Shards-Spec phase 1 = research/Gathering-Progression-Spec.md phase A + Skyy's
2026-10-06 updates). ONE source of truth for every jar that knows the Enchanted items:

    SkyyCollections 0.2.11+  ships the items (asset pack: item JSON + recipe, quality, icons, textures, the cube model), the Workbench tab
                             "Compressing" (runtime append, emit_tab), the unlock tiers (merged at validate like the Lantern rows), the
                             recipe knowledge sync and the coll:fn:add alias (credit = base x RATIO)
    SkyySacks 0.8.1+         SackDefs.homeOf: Skyy_Ench_<Key> -> the Void category of its base (sacks_home_java)
    SkyyBazaar 0.1.10+       a product per item, priced as a PROCESSED good from its recipe (100 x the input's raw value x (1 + premium))

Skyy's words this follows (docs/answered/bags.md + gear.md, word for word there):
  - 2026-10-05 "i want to use sky blocks enchanted iron and enchanted cobble. (basically compressed materials.)"
  - 2026-10-06 spec Q3 "Always 100" (100 base = 1 Enchanted), Q4 launch with 18 Enchanted items, no Enchanted Blocks yet
  - 2026-10-06 art review: "they should be enchanted ingots, not ore ... the only one that makes sense is rubble ... all kinda of rubble
    count towards rubble ... in the game the logs are blocks! just do an enchanted looking version of the same resource! a shiny coppy of
    the vanilla block." -> metals from INGOTS, stone = Cobblestone + Rubble (any rubble), one Enchanted log per key log
  - 2026-10-06 spec Q10 tweak "Enchanted premium" -> sold a bit ABOVE 100x base, capped below any loop (the processed-goods 22% rule)
  - 2026-10-11 UPGRADE COST "it costs a enchanted iron ingot to upgrade copper to iron" (phase 3 spends them; this phase makes them)

  - 2026-10-16 (docs/answered/gear.md) "there was no need to add the enchanted essence of life. greater essence already exists and is
    literally the exact same thing. remove the enchanted, and just use the vanilla version." -> the LifeEssence row is retired (RETIRED_C1 /
    RETIRED_TO); the Life Essence collection's Enchanted item = vanilla Ingredient_Life_Essence_Concentrated (VANILLA_ENCH, Void: Farming)

  - 2026-10-17 (docs/answered/gear.md FURNACE CHARM DESIGN, research/Zone-Ores-Alloys-Spec.md 5): "Collections for base metals only, no alloy
    collections." + "Keep your speed/fuel numbers and Eternal Flame at Charcoal tier 7." -> round ores01 (SkyyCollections 0.2.25) adds five
    rows (TABLE_ORES, appended to TABLE_C1 so tools/tier_tags.py tags them like the C1 rows): Enchanted Lead / Chromium / Slag / Titanium
    Ingot from the SkyyWorldGen 0.7.3 ingots (EXTERNAL_INPUTS - not in Assets.zip) + Enchanted Charcoal (vanilla Ingredient_Charcoal)

  - 2026-10-16 COLLECTIONS SPEC Q3 "Own items now" (docs/answered/economy.md): EVERY collection gets its own Enchanted item - round C1
    (SkyyCollections 0.2.21) appends one row per visible collection that had none (rows 21-103, the C1 block below; research/
    Collections-Tools-Redesign-Spec.md). SkyySacks homes them and SkyyBazaar lists them at THEIR next build (they read this table then).

Rules kept here (the build scripts assert them):
  - RATIO 100 is a BUILD-TIME constant (a runtime ratio could not change the baked recipe and would mis-credit items players hold).
  - REVERSE RECIPE (round E1 = SkyyCollections 0.2.34 + SkyyBazaar 0.2.2; Skyy 2026-10-16 "lets add a way to craft them back into the 100
    normal items" + 2026-10-25 docs/answered/bags.md "allow crafting enchanted items, and crafting them back into 100 work in the
    inventory"): every Enchanted item (and the vanilla pair VANILLA_ENCH: Greater Essence of Life) crafts back into RATIO of its base -
    1 -> RATIO, never another ratio. e1_files() builds them (standalone recipe files REV_DIR + REV_PREFIX<Key>); check_assets(e1=True)
    allows exactly these and nothing else that makes a base item. Built only by a build that passes e1=True (SkyyCollections 0.2.34+);
    an older pin's rebuild (e1 False) stays byte-identical and still refuses a reverse recipe. SkyyBazaar 0.2.2+ models every one of
    them in its money-loop checks (reverse_rows()).
  - POCKET CRAFTING (E1): the 100 -> 1 recipes are ALSO at the vanilla inventory crafting (bench Fieldcraft) in our own Fieldcraft category
    FIELD_CAT ("Compressing"; vanilla has only Tools), same recipe id + KnowledgeRequired = the same collection unlock as the Workbench
    tab. Every reverse recipe is OPEN (KnowledgeRequired false; research/Collections-Tools-Redesign-Spec.md 4.2 "anyone holding one
    (Bazaar, AH, gift) can open it" + Skyy 2026-10-16 "if i need copper but only have enchanted copper, i can craft it back to 100
    copper"; = SkyySacks' Void Unpack button, which has no unlock check either), so no known-recipe entry is managed for it; the vanilla
    pair's two recipes are open too (its vanilla Farmer's Workbench recipe is open to everyone).
  - Crafting is never a collection credit (the base items counted when gathered); only a GIVER that creates an Enchanted item credits it,
    through SkyyCollections' coll:fn:add alias (base x RATIO, once, at creation).
  - Icons / textures are a "shiny copy of the vanilla resource", GENERATED at build time from Assets.zip (nothing vanilla is committed).
  - Pure Python, deterministic (same Assets.zip -> same bytes).
"""
import os, json, copy

ENCH_VERSION = "1"            # bump when the table or the runtime tab protocol changes
RATIO = 100                   # Skyy 2026-10-06 "Always 100"
STACK = 100                   # Skyy: "use Hytale stack numbers"
PREFIX = "Skyy_Ench_"
RECIPE_SUFFIX = "_Recipe_Generated_0"
QUALITY = "Skyy_Enchanted"    # own quality: the vanilla Epic texture set + drop glow, label "Enchanted"
QUALITY_LABEL = "Enchanted"
QUALITY_COLOR = "#c77dff"
QUALITY_VALUE = 4             # = vanilla Epic; below SkyyAuctions' technical threshold (8)
TAB_ID = "Workbench_SkyyCompressing"
TAB_NAME_KEY = "server.benchCategories.workbench.skyycompressing"
TAB_TEXT = "Compressing"
TAB_LANG = ["benchCategories.workbench.skyycompressing=" + TAB_TEXT, TAB_NAME_KEY + "=" + TAB_TEXT]
BENCH_ID = "Workbench"
ART_DIR = "SkyyCollections/Ench"          # Common/<...> for textures / the cube model; icons in Icons/ItemsGenerated/
# ench1fix2: the item flavour-text colour code (research/Vanilla-UI-Style-Guide.md 15; the same hex as tools/skyyui.py rowName / rowSub) -
# lang <color> spans; a lang line break is the two characters backslash + n. Used only by build_assets(e1=True).
TIP_NL = "\\n"
TIP_NAME = "#d6e4ee"          # a line's label (stat NAME: soft white)
TIP_GOOD = "#7ee08a"          # what helps (green)
TIP_LEVEL = "#e8c25a"         # unlock / progress (gold)
TIP_DIM = "#7f93a6"           # minor info (dim grey)


def _tc(col, text):
    return '<color is="%s">%s</color>' % (col, text)


# (Key, input kind I = item / R = resource type, input id, collection id, default unlock tier, Void category, display name, look)
# Unlock tiers = Gathering-Progression-Spec 3.2 grammar: tier III on the S / R / B curves, tier II on the E curve (Adamantite).
# look: ("ingot", metal) | ("cube", base block item) | ("rubble", base item) | ("crop", base crop item)
TABLE = [
    ("Cobblestone", "I", "Rock_Stone_Cobble",      "Cobblestone", 3, "Mining",   "Enchanted Cobblestone",      ("cube", "Rock_Stone_Cobble")),
    ("Rubble",      "R", "Rubble",                 "Rubble",      3, "Mining",   "Enchanted Rubble",           ("rubble", "Rubble_Stone")),
    ("Copper",      "I", "Ingredient_Bar_Copper",  "Copper",      3, "Mining",   "Enchanted Copper Ingot",     ("ingot", "Ingredient_Bar_Copper")),
    ("Iron",        "I", "Ingredient_Bar_Iron",    "Iron",        3, "Mining",   "Enchanted Iron Ingot",       ("ingot", "Ingredient_Bar_Iron")),
    ("Thorium",     "I", "Ingredient_Bar_Thorium", "Thorium",     3, "Mining",   "Enchanted Thorium Ingot",    ("ingot", "Ingredient_Bar_Thorium")),
    ("Cobalt",      "I", "Ingredient_Bar_Cobalt",  "Cobalt",      3, "Mining",   "Enchanted Cobalt Ingot",     ("ingot", "Ingredient_Bar_Cobalt")),
    ("Adamantite",  "I", "Ingredient_Bar_Adamantite", "Adamantite", 2, "Mining", "Enchanted Adamantite Ingot", ("ingot", "Ingredient_Bar_Adamantite")),
    ("Oak",         "I", "Wood_Oak_Trunk",         "OakLog",      3, "Foraging", "Enchanted Oak Log",          ("cube", "Wood_Oak_Trunk")),
    ("Maple",       "I", "Wood_Maple_Trunk",       "MapleLog",    3, "Foraging", "Enchanted Maple Log",        ("cube", "Wood_Maple_Trunk")),
    ("Gumboab",     "I", "Wood_Gumboab_Trunk",     "GumboabLog",  3, "Foraging", "Enchanted Gumboab Log",      ("cube", "Wood_Gumboab_Trunk")),
    ("Redwood",     "I", "Wood_Redwood_Trunk",     "RedwoodLog",  3, "Foraging", "Enchanted Redwood Log",      ("cube", "Wood_Redwood_Trunk")),
    ("Sallow",      "I", "Wood_Sallow_Trunk",      "SallowLog",   3, "Foraging", "Enchanted Sallow Log",       ("cube", "Wood_Sallow_Trunk")),
    ("Wheat",       "I", "Plant_Crop_Wheat_Item",  "Wheat",       3, "Farming",  "Enchanted Wheat",            ("crop", "Plant_Crop_Wheat_Item")),
    ("Carrot",      "I", "Plant_Crop_Carrot_Item", "Carrot",      3, "Farming",  "Enchanted Carrot",           ("crop", "Plant_Crop_Carrot_Item")),
    ("Cauliflower", "I", "Plant_Crop_Cauliflower_Item", "Cauliflower", 3, "Farming", "Enchanted Cauliflower",  ("crop", "Plant_Crop_Cauliflower_Item")),
    ("Pumpkin",     "I", "Plant_Crop_Pumpkin_Item", "Pumpkin",    3, "Farming",  "Enchanted Pumpkin",          ("crop", "Plant_Crop_Pumpkin_Item")),
    ("Tomato",      "I", "Plant_Crop_Tomato_Item", "Tomato",      3, "Farming",  "Enchanted Tomato",           ("crop", "Plant_Crop_Tomato_Item")),
    ("Cotton",      "I", "Plant_Crop_Cotton_Item", "Cotton",      3, "Farming",  "Enchanted Cotton",           ("crop", "Plant_Crop_Cotton_Item")),
    ("Potato",      "I", "Plant_Crop_Potato_Item", "Potato",      3, "Farming",  "Enchanted Potato",           ("crop", "Plant_Crop_Potato_Item")),
    # round tools01 (Skyy 2026-10-16 "make enchanted sticks too, and require them in the later tool upgrades."): same ratio + place as the
    # others (100 Sticks -> 1, Workbench Compressing tab, unlocked at Stick collection tier III); the stick is an item (no block) -> the
    # "ingot" look path (its own model + a shiny copy of its texture). Its Void category is Foraging (SkyySacks reads this table at build).
    ("Stick",       "I", "Ingredient_Stick",       "Stick",       3, "Foraging", "Enchanted Stick",            ("ingot", "Ingredient_Stick")),
]
# ---- round C1 (SkyyCollections 0.2.21; Skyy 2026-10-16 "Own items now"): one Enchanted item for EVERY visible collection that had none.
# Same ratio / bench / tab / quality as the 20 above; input = the collection's FIRST item (metals: the ingot like Copper ... Adamantite;
# Sand and Crystal take their vanilla resource type, which holds exactly that collection's items); unlock tier = the spec 3.3 grammar
# (Elite curve II, every other curve III); Void category = the collection's (hides: Smithing, like SkyySacks homes the hides). Looks: the
# same four art paths (logs / stone = "cube", crops / fruit / meat / petals / gems = the vanilla block model "crop", items = "ingot").
TABLE_C1 = [
    ("Corn",        "I", "Plant_Crop_Corn_Item",      "Corn",        3, "Farming", "Enchanted Corn",        ("crop", "Plant_Crop_Corn_Item")),
    ("Lettuce",     "I", "Plant_Crop_Lettuce_Item",   "Lettuce",     3, "Farming", "Enchanted Lettuce",     ("crop", "Plant_Crop_Lettuce_Item")),
    ("Onion",       "I", "Plant_Crop_Onion_Item",     "Onion",       3, "Farming", "Enchanted Onion",       ("crop", "Plant_Crop_Onion_Item")),
    ("Turnip",      "I", "Plant_Crop_Turnip_Item",    "Turnip",      3, "Farming", "Enchanted Turnip",      ("crop", "Plant_Crop_Turnip_Item")),
    ("Aubergine",   "I", "Plant_Crop_Aubergine_Item", "Aubergine",   3, "Farming", "Enchanted Aubergine",   ("crop", "Plant_Crop_Aubergine_Item")),
    ("Chilli",      "I", "Plant_Crop_Chilli_Item",    "Chilli",      3, "Farming", "Enchanted Chilli",      ("crop", "Plant_Crop_Chilli_Item")),
    ("Rice",        "I", "Plant_Crop_Rice_Item",      "Rice",        3, "Farming", "Enchanted Rice",        ("crop", "Plant_Crop_Rice_Item")),
    ("Berries",     "I", "Plant_Fruit_Berries_Red",   "Berries",     3, "Farming", "Enchanted Wild Berries", ("crop", "Plant_Fruit_Berries_Red")),
    ("Apple",       "I", "Plant_Fruit_Apple",         "Apple",       3, "Farming", "Enchanted Apple",       ("crop", "Plant_Fruit_Apple")),
    ("WildFruit",   "I", "Plant_Fruit_Coconut",       "WildFruit",   3, "Farming", "Enchanted Coconut",     ("crop", "Plant_Fruit_Coconut")),
    ("Mushroom",    "I", "Plant_Crop_Mushroom_Cap_Brown", "Mushroom", 3, "Farming", "Enchanted Mushroom",   ("crop", "Plant_Crop_Mushroom_Cap_Brown")),
    ("Cactus",      "I", "Plant_Cactus_1",            "Cactus",      3, "Farming", "Enchanted Cactus",      ("crop", "Plant_Cactus_1")),
    ("Seeds",       "I", "Plant_Seeds_Wheat",         "Seeds",       3, "Farming", "Enchanted Seeds",       ("ingot", "Plant_Seeds_Wheat")),
    # round sacks0814 (Skyy 2026-10-16 "there was no need to add the enchanted essence of life. greater essence already exists and is literally the
    # exact same thing. remove the enchanted, and just use the vanilla version."): the LifeEssence row is RETIRED (RETIRED_C1 below) - the
    # Life Essence collection's Enchanted item is the vanilla Ingredient_Life_Essence_Concentrated (VANILLA_ENCH)
    ("Petals",      "I", "Plant_Petals_Blood",        "Petals",      3, "Farming", "Enchanted Petals",      ("crop", "Plant_Petals_Blood")),
    ("RawChicken",  "I", "Food_Chicken_Raw",          "RawChicken",  3, "Farming", "Enchanted Raw Chicken", ("crop", "Food_Chicken_Raw")),
    ("RawBeef",     "I", "Food_Beef_Raw",             "RawBeef",     3, "Farming", "Enchanted Raw Beef",    ("crop", "Food_Beef_Raw")),
    ("RawPork",     "I", "Food_Pork_Raw",             "RawPork",     3, "Farming", "Enchanted Raw Pork",    ("crop", "Food_Pork_Raw")),
    ("Wildmeat",    "I", "Food_Wildmeat_Raw",         "Wildmeat",    3, "Farming", "Enchanted Raw Wildmeat", ("crop", "Food_Wildmeat_Raw")),
    ("Fiber",       "I", "Ingredient_Fibre",          "Fiber",       3, "Foraging", "Enchanted Plant Fiber", ("ingot", "Ingredient_Fibre")),
    ("TreeSap",     "I", "Ingredient_Tree_Sap",       "TreeSap",     3, "Foraging", "Enchanted Tree Sap",    ("ingot", "Ingredient_Tree_Sap")),
] + [(_k, "I", "Wood_%s_Trunk" % _w, _c, 3, "Foraging", "Enchanted %s" % _n, ("cube", "Wood_%s_Trunk" % _w)) for _k, _w, _c, _n in (
    ("AppleLog", "Apple", "AppleLog", "Apple Log"), ("Ash", "Ash", "AshLog", "Ash Log"), ("Aspen", "Aspen", "AspenLog", "Aspen Log"),
    ("Bamboo", "Bamboo", "BambooLog", "Bamboo Log"), ("Banyan", "Banyan", "BanyanLog", "Banyan Log"), ("Beech", "Beech", "BeechLog", "Beech Log"),
    ("Birch", "Birch", "BirchLog", "Birch Log"), ("Bottletree", "Bottletree", "BottletreeLog", "Bottletree Log"),
    ("Burnt", "Burnt", "BurntLog", "Burnt Log"), ("Camphor", "Camphor", "CamphorLog", "Camphor Log"), ("Cedar", "Cedar", "CedarLog", "Cedar Log"),
    ("Dry", "Dry", "DryLog", "Dry Log"), ("FigBlue", "Fig_Blue", "FigBlueLog", "Blue Fig Log"), ("Fir", "Fir", "FirLog", "Fir Log"),
    ("Jungle", "Jungle", "JungleLog", "Jungle Log"), ("Palm", "Palm", "PalmLog", "Palm Log"), ("Palo", "Palo", "PaloLog", "Palo Log"),
    ("Windwillow", "Windwillow", "WindwillowLog", "Windwillow Log"), ("WisteriaWild", "Wisteria_Wild", "WisteriaWildLog", "Wild Wisteria Log"),
    ("Amber", "Amber", "AmberLog", "Amber Log"), ("Azure", "Azure", "AzureLog", "Azure Log"), ("CrystalLog", "Crystal", "CrystalLog", "Crystalwood Log"),
    ("Fire", "Fire", "FireLog", "Fire Log"), ("IceLog", "Ice", "IceLog", "Frostwood Log"), ("Petrified", "Petrified", "PetrifiedLog", "Petrified Log"),
    ("Poisoned", "Poisoned", "PoisonedLog", "Poisoned Log"), ("Spiral", "Spiral", "SpiralLog", "Spiral Log"),
    ("Stormbark", "Stormbark", "StormbarkLog", "Stormbark Log"))] + [
    ("Sandstone",   "I", "Rock_Sandstone_Cobble",     "Sandstone",   3, "Mining", "Enchanted Sandstone",    ("cube", "Rock_Sandstone_Cobble")),
    ("Shale",       "I", "Rock_Shale_Cobble",         "Shale",       3, "Mining", "Enchanted Shale",        ("cube", "Rock_Shale_Cobble")),
    ("Slate",       "I", "Rock_Slate_Cobble",         "Slate",       3, "Mining", "Enchanted Slate",        ("cube", "Rock_Slate_Cobble")),
    ("Basalt",      "I", "Rock_Basalt_Cobble",        "Basalt",      3, "Mining", "Enchanted Basalt",       ("cube", "Rock_Basalt_Cobble")),
    ("Volcanic",    "I", "Rock_Volcanic_Cobble",      "Volcanic",    3, "Mining", "Enchanted Volcanic Rock", ("cube", "Rock_Volcanic_Cobble")),
    ("Marble",      "I", "Rock_Marble_Cobble",        "Marble",      3, "Mining", "Enchanted Marble",       ("cube", "Rock_Marble_Cobble")),
    ("Quartzite",   "I", "Rock_Quartzite_Cobble",     "Quartzite",   3, "Mining", "Enchanted Quartzite",    ("cube", "Rock_Quartzite_Cobble")),
    ("Limestone",   "I", "Rock_Lime_Cobble",          "Limestone",   3, "Mining", "Enchanted Limestone",    ("cube", "Rock_Lime_Cobble")),
    ("Ice",         "I", "Rock_Ice",                  "Ice",         3, "Mining", "Enchanted Ice",          ("cube", "Rock_Ice")),
    ("Salt",        "I", "Rock_Salt",                 "Salt",        3, "Mining", "Enchanted Salt",         ("cube", "Rock_Salt")),
    ("Sand",        "R", "Sands",                     "Sand",        3, "Mining", "Enchanted Sand",         ("cube", "Soil_Sand")),
    ("Clay",        "I", "Soil_Clay",                 "Clay",        3, "Mining", "Enchanted Clay",         ("cube", "Soil_Clay")),
    ("Silver",      "I", "Ingredient_Bar_Silver",     "Silver",      3, "Mining", "Enchanted Silver Ingot", ("ingot", "Ingredient_Bar_Silver")),
    ("Gold",        "I", "Ingredient_Bar_Gold",       "Gold",        3, "Mining", "Enchanted Gold Ingot",   ("ingot", "Ingredient_Bar_Gold")),
    ("Mithril",     "I", "Ingredient_Bar_Mithril",    "Mithril",     2, "Mining", "Enchanted Mithril Ingot", ("ingot", "Ingredient_Bar_Mithril")),
    ("Crystal",     "R", "Crystal_Shards",            "Crystal",     3, "Mining", "Enchanted Crystal Shards", ("ingot", "Ingredient_Crystal_Blue")),
    ("Gemstone",    "I", "Rock_Gem_Diamond",          "Gemstone",    2, "Mining", "Enchanted Diamond",      ("crop", "Rock_Gem_Diamond")),
    ("Bone",        "I", "Ingredient_Bone_Fragment",  "Bone",        3, "Combat", "Enchanted Bone",         ("ingot", "Ingredient_Bone_Fragment")),
    ("Linen",       "I", "Ingredient_Fabric_Scrap_Linen", "Linen",   3, "Combat", "Enchanted Linen",        ("ingot", "Ingredient_Fabric_Scrap_Linen")),
    ("HideLight",   "I", "Ingredient_Hide_Light",     "HideLight",   3, "Smithing", "Enchanted Light Hide", ("ingot", "Ingredient_Hide_Light")),
    ("HideMedium",  "I", "Ingredient_Hide_Medium",    "HideMedium",  3, "Smithing", "Enchanted Medium Hide", ("ingot", "Ingredient_Hide_Medium")),
    ("HideHeavy",   "I", "Ingredient_Hide_Heavy",     "HideHeavy",   3, "Smithing", "Enchanted Heavy Hide", ("ingot", "Ingredient_Hide_Heavy")),
    ("Wool",        "I", "Ingredient_Fabric_Scrap_Wool", "Wool",     3, "Combat", "Enchanted Wool",         ("ingot", "Ingredient_Fabric_Scrap_Wool")),
    ("Feathers",    "I", "Ingredient_Feathers_Light", "Feathers",    3, "Combat", "Enchanted Feather",      ("ingot", "Ingredient_Feathers_Light")),
    ("Chitin",      "I", "Ingredient_Chitin_Sturdy",  "Chitin",      3, "Combat", "Enchanted Chitin",       ("ingot", "Ingredient_Chitin_Sturdy")),
    ("Venom",       "I", "Ingredient_Sac_Venom",      "Venom",       3, "Combat", "Enchanted Venom Sac",    ("ingot", "Ingredient_Sac_Venom")),
    ("Shadoweave",  "I", "Ingredient_Fabric_Scrap_Shadoweave", "Shadoweave", 3, "Combat", "Enchanted Shadoweave", ("ingot", "Ingredient_Fabric_Scrap_Shadoweave")),
    ("Cindercloth", "I", "Ingredient_Fabric_Scrap_Cindercloth", "Cindercloth", 3, "Combat", "Enchanted Cindercloth", ("ingot", "Ingredient_Fabric_Scrap_Cindercloth")),
    ("FireEssence", "I", "Ingredient_Fire_Essence",   "FireEssence", 3, "Combat", "Enchanted Essence of Fire", ("ingot", "Ingredient_Fire_Essence")),
    ("IceEssence",  "I", "Ingredient_Ice_Essence",    "IceEssence",  3, "Combat", "Enchanted Essence of Ice", ("ingot", "Ingredient_Ice_Essence")),
    ("VoidEssence", "I", "Ingredient_Void_Essence",   "VoidEssence", 3, "Combat", "Enchanted Essence of the Void", ("ingot", "Ingredient_Void_Essence")),
    ("LightningEssence", "I", "Ingredient_Lightning_Essence", "LightningEssence", 2, "Combat", "Enchanted Essence of Lightning", ("ingot", "Ingredient_Lightning_Essence")),
    ("Voidheart",   "I", "Ingredient_Voidheart",      "Voidheart",   2, "Combat", "Enchanted Voidheart",    ("ingot", "Ingredient_Voidheart")),
    ("BoomPowder",  "I", "Ingredient_Powder_Boom",    "BoomPowder",  3, "Combat", "Enchanted Boom Powder",  ("ingot", "Ingredient_Powder_Boom")),
]
TABLE_20 = list(TABLE)          # the first 20 rows (0.2.11 - 0.2.20) - frozen tables of older rounds read only these
# round sacks0814 (Skyy 2026-10-16, docs/answered/gear.md "NO ENCHANTED ESSENCE OF LIFE"): rows taken OUT of the table. A Skyy_Ench_<Key> of a
# retired row is no Enchanted material any more (no Void home, no Bazaar product, no recipe at the next SkyyCollections build); SkyyCollections
# converts held ones 1:1 into RETIRED_TO[<id>] in its next round. (index in TABLE_C1 as SkyyCollections 0.2.21 / 0.2.22 built it, the row)
RETIRED_C1 = ((13, ("LifeEssence", "I", "Ingredient_Life_Essence", "LifeEssence", 3, "Farming", "Enchanted Essence of Life",
                    ("ingot", "Ingredient_Life_Essence"))),)
RETIRED_TO = {"Skyy_Ench_LifeEssence": "Ingredient_Life_Essence_Concentrated"}     # retired Enchanted id -> the item that replaces it, 1:1
# collections whose Enchanted item is a VANILLA compressed item (Skyy 2026-10-16 standing rule: "use the vanilla compressed version if one
# exists" - checked 10-16: only Life Essence has one): collection id -> (the vanilla item id, its Void category). Vanilla Greater Essence of
# Life = 100 Essence of Life at the Farmer's Workbench (vanilla recipe); SkyySacks' homeOf already puts every Ingredient_Life_Essence* in Farming.
VANILLA_ENCH = {"LifeEssence": ("Ingredient_Life_Essence_Concentrated", "Farming")}
TABLE_C1_0221 = list(TABLE_C1)  # TABLE_C1 exactly as SkyyCollections 0.2.21 / 0.2.22 were built (83 rows) - for a rebuild of those pins only
for _i, _r in RETIRED_C1:
    TABLE_C1_0221.insert(_i, _r)
TABLE_0221 = TABLE + TABLE_C1_0221   # the 103-row table of SkyyCollections 0.2.21 / 0.2.22 (frozen; never for a new build)
# ---- round ores01 (SkyyCollections 0.2.25; Skyy 2026-10-17 "Collections for base metals only, no alloy collections."): the four new zone
# metals (their collections count the RAW ore, like Thorium; the Enchanted item is made from the INGOT, like every metal row) + Charcoal (the
# /craft Furnace's fuel byproduct; its collection is credited by SkyySacks through coll:fn:add source sacks:furnace). Unlock tiers = the
# grammar (Rare curve III: Lead / Chromium; Elite curve II: Slag / Titanium - the partner metals' rows; Charcoal Standard III). The ingots
# are SkyyWorldGen 0.7.3 items (EXTERNAL_INPUTS), so their art is a tinted copy of the vanilla Iron ingot (ART_TINT) until drawn icons land.
# Enchanted Charcoal homes in the Smithing Void like Ingredient_Charcoal (SkyySacks SMITH_EXACT); its collection sits in Mining (the
# collections page has no Smithing category).
TABLE_ORES = [
    ("Lead",     "I", "Ingredient_Bar_Lead_SkyWynn",     "Lead",     3, "Mining",   "Enchanted Lead Ingot",     ("ingot", "Ingredient_Bar_Iron")),
    ("Chromium", "I", "Ingredient_Bar_Chromium_SkyWynn", "Chromium", 3, "Mining",   "Enchanted Chromium Ingot", ("ingot", "Ingredient_Bar_Iron")),
    ("Slag",     "I", "Ingredient_Bar_Slag_SkyWynn",     "Slag",     2, "Mining",   "Enchanted Slag Ingot",     ("ingot", "Ingredient_Bar_Iron")),
    ("Titanium", "I", "Ingredient_Bar_Titanium_SkyWynn", "Titanium", 2, "Mining",   "Enchanted Titanium Ingot", ("ingot", "Ingredient_Bar_Iron")),
    ("Charcoal", "I", "Ingredient_Charcoal",             "Charcoal", 3, "Smithing", "Enchanted Charcoal",       ("rubble", "Ingredient_Charcoal")),
]
# inputs that are not in Assets.zip: the item id -> the mod that defines it (SkyyCollections' build checks them against that jar when it exists)
EXTERNAL_INPUTS = {"Ingredient_Bar_Lead_SkyWynn": "SkyyWorldGen", "Ingredient_Bar_Chromium_SkyWynn": "SkyyWorldGen",
                   "Ingredient_Bar_Slag_SkyWynn": "SkyyWorldGen", "Ingredient_Bar_Titanium_SkyWynn": "SkyyWorldGen"}
# the placeholder palette of research/Zone-Ores-Alloys-Spec.md 2.6 (Lead dull blue-grey, Chromium mirror silver-cyan, Slag rust-black, Titanium
# pale white-gold): key -> (target RGB, strength 0-1); the look's vanilla art is recoloured toward it (brightness kept) before the shine
ART_TINT = {"Lead": ((112, 124, 150), 0.70), "Chromium": ((190, 232, 240), 0.65), "Slag": ((120, 62, 40), 0.80),
            "Titanium": ((244, 230, 190), 0.70)}
TABLE_C1_0224 = list(TABLE_C1)  # TABLE_C1 exactly as SkyyCollections 0.2.24 / SkyySacks 0.8.19 / SkyyBazaar 0.1.19 were built (82 rows)
TABLE_C1 = TABLE_C1 + TABLE_ORES
TABLE_0224 = TABLE + TABLE_C1_0224   # the 102-row table of those pins (frozen; legacy_0224)
TABLE = TABLE + TABLE_C1
KEYS = [t[0] for t in TABLE]
IDS = [PREFIX + k for k in KEYS]
RIDS = [i + RECIPE_SUFFIX for i in IDS]
CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")          # C1: + Combat / Smithing (the mob-drop collections)
# sacks0814: 20 + 82 (the C1 Life Essence row retired -> its collection uses the vanilla Greater Essence of Life, VANILLA_ENCH); ores01: + 5
assert len(TABLE_20) == 20 and len(TABLE) == 107 and len(set(KEYS)) == 107 and all(t[5] in CATS for t in TABLE)
assert len(TABLE_0224) == 102 and TABLE == TABLE_0224 + TABLE_ORES and len(TABLE_ORES) == 5
assert len(TABLE_0221) == 103 and TABLE_0221[:20] == TABLE_20 and [t for t in TABLE_0221 if t[0] not in KEYS] == [r for _i, r in RETIRED_C1]
assert len(set(t[3] for t in TABLE)) == 107 and not set(VANILLA_ENCH) & set(t[3] for t in TABLE), "one Enchanted item per collection"
assert sorted(EXTERNAL_INPUTS) == sorted(t[2] for t in TABLE_ORES if t[2].endswith("_SkyWynn")) and set(ART_TINT) <= set(t[0] for t in TABLE_ORES)
assert not [t for t in TABLE if t[2] in EXTERNAL_INPUTS and t[7][1] in EXTERNAL_INPUTS], "an external input needs a vanilla look base"
assert all(PREFIX + r[0] in RETIRED_TO and r[3] in VANILLA_ENCH for _i, r in RETIRED_C1) and all(c in CATS for _v, c in VANILLA_ENCH.values())
assert all(t[1] in ("I", "R") and 1 <= t[4] <= 3 for t in TABLE)
# ---- round level-bands (SkyyCollections 0.2.28; Skyy 2026-10-18 docs/answered/gear.md COLLECTION UNLOCK LADDER + ALLOYS: "and enchanted bronze when
# both reach 6. use that pattern for all of the alloys. (and you can either craft 100 bronze into enchanted bronze, or smelt enchanted iron and
# copper together for enchanted bronze."): the six Enchanted ALLOYS. Alloys have no collection, so these rows are NOT in TABLE (SkyySacks /
# SkyyBazaar / tools/tier_tags.py read TABLE and stay as they are); a build that ships or lists them opts in by reading TABLE_ALLOYS (SkyyCollections
# 0.2.28 ships them; the Bazaar / Sacks pick them up at their next build). Column 3 = the FIRST parent collection (its tier VI line lists the
# recipe; SkyyCollections also lists it at the second parent's tier VI - both must be reached, ALLOY_PARENTS); column 4 = that tier (6).
TABLE_ALLOYS = [
    ("Bronze",   "I", "Ingredient_Bar_Bronze",            "Copper",     6, "Mining", "Enchanted Bronze Ingot",   ("ingot", "Ingredient_Bar_Bronze")),
    ("Dusk",     "I", "Ingredient_Bar_Dusk_SkyWynn",      "Thorium",    6, "Mining", "Enchanted Dusk Ingot",     ("ingot", "Ingredient_Bar_Iron")),
    ("Azurvane", "I", "Ingredient_Bar_Azurvane_SkyWynn",  "Cobalt",     6, "Mining", "Enchanted Azurvane Ingot", ("ingot", "Ingredient_Bar_Iron")),
    ("Cinder",   "I", "Ingredient_Bar_Cinder_SkyWynn",    "Adamantite", 6, "Mining", "Enchanted Cinder Ingot",   ("ingot", "Ingredient_Bar_Iron")),
    ("Lumen",    "I", "Ingredient_Bar_Lumen_SkyWynn",     "Mithril",    6, "Mining", "Enchanted Lumen Ingot",    ("ingot", "Ingredient_Bar_Iron")),
    ("Electrum", "I", "Ingredient_Bar_Electrum_SkyWynn",  "Gold",       6, "Mining", "Enchanted Electrum Ingot", ("ingot", "Ingredient_Bar_Iron")),
]
ALLOY_PARENTS = {"Bronze": ("Copper", "Iron"), "Dusk": ("Thorium", "Lead"), "Azurvane": ("Cobalt", "Chromium"), "Cinder": ("Adamantite", "Slag"),
                 "Lumen": ("Mithril", "Titanium"), "Electrum": ("Gold", "Silver")}          # = SkyyWorldGen WG_ALLOYS (input A, input B)
ALLOY_EXTERNAL = dict((t[2], "SkyyWorldGen") for t in TABLE_ALLOYS if t[2].endswith("_SkyWynn"))
ALLOY_TINT = {"Dusk": ((168, 114, 110), 0.70), "Azurvane": ((70, 140, 222), 0.70), "Cinder": ((190, 54, 20), 0.75),
              "Lumen": ((255, 242, 192), 0.70), "Electrum": ((232, 228, 198), 0.65)}          # SkyyWorldGen 0.7.3 alloy palettes (bright step)
ALLOY_LABEL = {"Bronze": "Bronze Ingots", "Dusk": "Dusk Ingots", "Azurvane": "Azurvane Ingots", "Cinder": "Cinder Ingots",
               "Lumen": "Lumen Ingots", "Electrum": "Electrum Ingots"}
assert [t[0] for t in TABLE_ALLOYS] == list(ALLOY_PARENTS) and all(t[3] == ALLOY_PARENTS[t[0]][0] and t[4] == 6 for t in TABLE_ALLOYS)
assert not set(t[0] for t in TABLE_ALLOYS) & set(KEYS) and sorted(ALLOY_TINT) == sorted(t[0] for t in TABLE_ALLOYS if t[2] in ALLOY_EXTERNAL)
assert sorted(ALLOY_LABEL) == sorted(ALLOY_PARENTS) and not set(ALLOY_EXTERNAL) & set(EXTERNAL_INPUTS)
for _t in TABLE:
    assert all(c.isalnum() for c in _t[0]) and '"' not in _t[6] and "\\" not in _t[6] and "|" not in _t[6], _t


# round coll24 (SkyyCollections 0.2.24 + SkyyBazaar 0.1.19; the C1 critic: "gifts up to ~40 Enchanted Mithril free could become a coin
# source"): every Enchanted GIFT (collection tier gifts in rewards.properties, rebirth rank gifts) is sized to the items that tier asks for:
# at most GIFT_SHARE percent of the tier's STEP (its amount minus the tier before) in base items, i.e. n Enchanted <= GIFT_SHARE x step /
# (100 x RATIO), never above the old size. So a gift is worth at most GIFT_SHARE % (x the Bazaar's Enchanted premium) of what the player
# gathered for that tier - a small bonus on gathering, never a coin source of its own. 0 = that tier gives no item (coins / XP stay).
GIFT_SHARE = 10


def gift_size(step, cap=64):
    """the Enchanted gift for a tier (or rebirth rank) whose step is `step` base items: GIFT_SHARE % of it in Enchanted items, <= cap"""
    return max(0, min(int(cap), (GIFT_SHARE * int(step)) // (100 * RATIO)))


assert gift_size(1000) == 1 and gift_size(999) == 0 and gift_size(25000, 20) == 20 and gift_size(10 ** 9) == 64


# Skyy 2026-10-16 (coll24 popup "404 low tiers would give no Enchanted item... OK?" -> "Give base items there (Recommended)"): a tier whose
# Enchanted gift rounds to 0 gives the collection's BASE item (its first item - what the player gathers) instead: GIFT_SHARE % of the step
# in base items, at least 1, at most 64 (one reward token's limit) - the same value cap, so every tier gives something.
def base_gift_size(step, cap=64):
    return max(1, min(int(cap), (GIFT_SHARE * int(step)) // 100))


assert base_gift_size(10) == 1 and base_gift_size(50) == 5 and base_gift_size(999) == 64 and base_gift_size(150) == 15


def coll_ench(coll_id):
    """the Enchanted item of a collection: Skyy_Ench_<Key> of its TABLE row, else its VANILLA_ENCH item, else None"""
    for t in TABLE:
        if t[3] == coll_id:
            return PREFIX + t[0]
    v = VANILLA_ENCH.get(coll_id)
    return v[0] if v else None


def row(key):
    for t in TABLE:
        if t[0] == key:
            return t
    return None


def cat_of(item_id):
    """the Python mirror of the Java SackDefs.enchCat (SkyySacks 0.8.1): the Void category of an Enchanted id, else None"""
    if not isinstance(item_id, str) or not item_id.startswith(PREFIX):
        return None
    t = row(item_id[len(PREFIX):])
    return t[5] if t else None


def tier_key(key):
    return "ench.tier." + key.lower()


def _jarr(vals):
    return "new String[] { " + ", ".join('"%s"' % v for v in vals) + " }"


def sacks_home_java():
    """the SackDefs method SkyySacks 0.8.1 compiles: enchCat(id) -> the category of a KNOWN Enchanted id, null otherwise (an unknown
    Skyy_Ench_ id is never stored: it belongs to no category)"""
    return ("public static String enchCat(String itemId) {\n"
            "  if (itemId == null || !itemId.startsWith(\"%s\")) return null;\n"
            "  String[] ids = %s;\n"
            "  String[] cats = %s;\n"
            "  for (int i = 0; i < ids.length; i++) if (ids[i].equals(itemId)) return cats[i];\n"
            "  return null;\n"
            "}") % (PREFIX, _jarr(IDS), _jarr([t[5] for t in TABLE]))


def _home_java(ids, table):
    """sacks_home_java for another (frozen) table - legacy_0221"""
    return sacks_home_java().replace(_jarr(IDS), _jarr(ids), 1).replace(_jarr([t[5] for t in TABLE]), _jarr([t[5] for t in table]), 1)


# ================================================================================================================ art (build time)
def _shine(img, outline):
    """the "shiny copy": brighter, a violet enchant tint, two diagonal glints; outline = a soft violet rim around the silhouette (icons)"""
    w, h = img.w, img.h
    out = img.copy()
    src = img
    for y in range(h):
        for x in range(w):
            r, g, b, a = src.get(x, y)
            if a == 0:
                continue
            m = (r + g + b) / 3.0
            r, g, b = m + (r - m) * 1.25, m + (g - m) * 1.25, m + (b - m) * 1.25      # a little more colour
            r, g, b = r * 1.08 + 6, g * 1.08 + 6, b * 1.08 + 6                        # a little brighter
            t = 0.07
            r, g, b = r * (1 - t) + 199 * t, g * (1 - t) + 125 * t, b * (1 - t) + 255 * t   # a hint of the enchant violet
            d = (x + (h - 1 - y)) / float(w + h)
            glint = 0.0
            for c0, half, k in ((0.40, 0.035, 0.50), (0.60, 0.018, 0.35)):
                e = abs(d - c0)
                if e < half:
                    glint = max(glint, k * (1.0 - e / half))
            r, g, b = r + (255 - r) * glint, g + (255 - g) * glint, b + (255 - b) * glint
            out.put(x, y, (_c8(r), _c8(g), _c8(b), a))
    if outline:
        for y in range(h):
            for x in range(w):
                if src.get(x, y)[3] >= 64:
                    continue
                near = 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and src.get(xx, yy)[3] >= 128:
                        near += 1
                if near:
                    out.put(x, y, (205, 130, 255, 110 + 30 * min(near, 3)))
    return out


def _c8(v):
    v = int(round(v))
    return 0 if v < 0 else (255 if v > 255 else v)


def _tint(img, key):
    """ores01: recolour a vanilla look toward ART_TINT[key] (the shading kept: a pixel of mean brightness becomes the target colour; alpha kept)"""
    if key not in ART_TINT:
        return img
    (tr, tg, tb), k = ART_TINT[key]
    ms = [sum(img.get(x, y)[:3]) / 3.0 for y in range(img.h) for x in range(img.w) if img.get(x, y)[3] > 0]
    tm = (sum(ms) / len(ms)) if ms else 1.0          # the art's mean brightness shows the target colour itself
    out = img.copy()
    for y in range(img.h):
        for x in range(img.w):
            r, g, b, a = img.get(x, y)
            if a == 0:
                continue
            m = (r + g + b) / 3.0
            f = m / tm
            out.put(x, y, (_c8(r * (1 - k) + tr * f * k), _c8(g * (1 - k) + tg * f * k), _c8(b * (1 - k) + tb * f * k), a))
    return out


def _items(z):
    out = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            try:
                out[n.rsplit("/", 1)[1][:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception:
                pass
    return out


def _inh(items, i, k):
    seen = set()
    x = items.get(i)
    while x is not None and i not in seen:
        seen.add(i)
        if k in x:
            return x[k]
        i = x.get("Parent")
        x = items.get(i) if i else None
    return None


def _btk(items, i, k):
    """C1: the first BlockType along the Parent chain that has key k (the 20 rows of 0.2.20 find it on the item itself - same bytes)"""
    seen = set()
    x = items.get(i)
    while x is not None and i not in seen:
        seen.add(i)
        bt = x.get("BlockType")
        if isinstance(bt, dict) and k in bt:
            return bt[k]
        i = x.get("Parent")
        x = items.get(i) if i else None
    return None


def _cube_model(z, SA):
    """the Enchanted cube model: Assets.zip Blocks/Structures/Base_Shapes/Cube_Overlay.blockymodel (ONE 32-unit box) re-laid out at build
    time: the four sides read the texture's left 32x32, top + bottom its right 32x32, the box drawn at half a block (stretch 0.5)"""
    m = json.loads(SA._read(z, "Blocks/Structures/Base_Shapes/Cube_Overlay.blockymodel").decode("utf-8-sig"))
    assert len(m["nodes"]) == 1 and m["nodes"][0]["shape"]["type"] == "box", "Cube_Overlay changed"
    m = copy.deepcopy(m)
    sh = m["nodes"][0]["shape"]
    sh["settings"]["size"] = {"x": 32, "y": 32, "z": 32}
    sh["stretch"] = {"x": 0.5, "y": 0.5, "z": 0.5}
    m["nodes"][0]["position"] = {"x": 0, "y": 8, "z": 0}
    m["nodes"][0]["name"] = "SkyyEnchCube"
    lay = sh["textureLayout"]
    for f in ("front", "back", "left", "right", "top", "bottom"):
        assert f in lay, "Cube_Overlay textureLayout lost face " + f
        lay[f] = {"offset": {"x": 32 if f in ("top", "bottom") else 0, "y": 0}, "mirror": {"x": False, "y": False}, "angle": 0}
    return json.dumps(m, indent=2).encode("utf-8")


def build_assets(z, SA, e1=False):
    """{jar path: bytes | str} for SkyyCollections (Server/... JSON as str, Common/... art as bytes) + the lang lines.
    z = Assets.zip (read-only), SA = tools/skyyart.py. e1 (SkyyCollections 0.2.34+): the recipes also at the inventory crafting's
    Compressing tab and the description says so + names the way back (the reverse recipes themselves come from e1_files)."""
    items = _items(z)
    files, lang = {}, []
    cube_rel = "Items/%s/EnchCube.blockymodel" % ART_DIR
    files["Common/" + cube_rel] = _cube_model(z, SA)
    for (key, kind, inp, coll, tier, cat, name, look) in TABLE:
        eid = PREFIX + key
        lk, base = look
        assert base in items, "Enchanted %s: base %s is not in Assets.zip" % (key, base)
        icon_src = _inh(items, base, "Icon")
        icon = SA.png_encode(_shine(_tint(SA.png_decode(SA._read(z, icon_src)), key), True))
        assert SA.png_size(icon) == (64, 64), (key, SA.png_size(icon))
        icon_rel = "Icons/ItemsGenerated/SkyyCollections_Ench_%s.png" % key
        files["Common/" + icon_rel] = icon
        tex_rel = "Items/%s/%s.png" % (ART_DIR, key)
        props = None
        if lk == "ingot":
            model = _inh(items, base, "Model")
            tex = SA.png_encode(_shine(_tint(SA.png_decode(SA._read(z, _inh(items, base, "Texture"))), key), False))
            props = _inh(items, base, "IconProperties")
            sound = _inh(items, base, "ItemSoundSetId")
        elif lk == "cube":
            bt = _inh(items, base, "BlockType")
            t0 = bt["Textures"][0]
            sp, tp = (t0["Sides"], t0["UpDown"]) if "Sides" in t0 else (t0["All"], t0["All"])          # C1: one texture on every face
            side, top = SA.png_decode(SA._read(z, sp)), SA.png_decode(SA._read(z, tp))
            assert (side.w, side.h, top.w, top.h) == (32, 32, 32, 32), (key, side.w, side.h, top.w, top.h)
            atlas = SA.Img(64, 32)
            for y in range(32):
                for x in range(32):
                    atlas.put(x, y, side.get(x, y))
                    atlas.put(32 + x, y, top.get(x, y))
            tex = SA.png_encode(_shine(atlas, False))
            model = cube_rel
            props = {"Scale": 1, "Translation": [0, -3], "Rotation": [22.5, 45, 22.5]}
            sound = _inh(items, base, "ItemSoundSetId")
        else:   # rubble / crop: the vanilla block's own CustomModel + a shiny copy of its first texture
            model = _btk(items, base, "CustomModel")
            tex = SA.png_encode(_shine(SA.png_decode(SA._read(z, _btk(items, base, "CustomModelTexture")[0]["Texture"])), False))
            props = _inh(items, base, "IconProperties") or {"Scale": 1, "Translation": [0, -3], "Rotation": [22.5, 45, 22.5]}
            sound = _inh(items, base, "ItemSoundSetId")
        files["Common/" + tex_rel] = tex
        node = {
            "TranslationProperties": {"Name": "server.items.%s.name" % eid, "Description": "server.items.%s.description" % eid},
            "Categories": ["Items"],
            "Quality": QUALITY,
            "Icon": icon_rel,
            "Model": model,
            "Texture": tex_rel,
            "IconProperties": props,
            "PlayerAnimationsId": "Item",
            "MaxStack": STACK,
            "Tags": {"Type": ["Ingredient"]},
            "DropOnDeath": True,
            "Recipe": {
                "Input": [{"ItemId": inp, "Quantity": RATIO}] if kind == "I" else [{"ResourceTypeId": inp, "Quantity": RATIO}],
                "BenchRequirement": bench_req(e1),
                "OutputQuantity": 1,
                "TimeSeconds": 1,
                "KnowledgeRequired": True,
            },
        }
        if e1:   # smoke 2026-10-27: the engine refuses a Fieldcraft (inventory) recipe with a delay - "should not have a delay (TimeSeconds)"
            del node["Recipe"]["TimeSeconds"]
        if sound:
            node["ItemSoundSetId"] = sound
        files["Server/Item/Items/SkyyCollections/%s.json" % eid] = json.dumps(node, indent=2)
        # ench01fix: no promise of a use this phase lacks (the Anvil tier-up is phase 3) and no "already collected" claim (the ingots'
        # collections count ORE); crafting simply never adds collection credit
        desc = ("%d %s pressed into one. Crafting it adds nothing to your collections. Saved for tool and gear upgrades (coming soon). "
                "Workbench, Compressing tab - or /craft - once unlocked in /collections."
                % (RATIO, base_label(key)))
        if e1:      # E1: the tool / gear upgrades that spend them are live (SkyyGear tier-ups); inventory crafting + the way back
            # ench1fix2: sectioned + colour coded (research/Vanilla-UI-Style-Guide.md 15, Skyy 2026-10-24): what it is first, then WHERE,
            # then each direction on its own line with who may craft it, minor info dim last (a lang line break = the two characters \n)
            desc = TIP_NL.join([
                "%d %s pressed into one. Spent on tool and gear upgrades." % (RATIO, base_label(key)),
                "",
                _tc(TIP_NAME, "Where:") + " inventory (Compressing tab), Workbench (Compressing tab) or /craft",
                _tc(TIP_NAME, "Make one:") + " " + _tc(TIP_LEVEL, "once unlocked in /collections"),
                _tc(TIP_NAME, "Craft it back into %d:" % RATIO) + " " + _tc(TIP_GOOD, "anyone, no unlock needed"),
                _tc(TIP_DIM, "Crafting adds nothing to your collections.")])
        lang += ["items.%s.name=%s" % (eid, name), "server.items.%s.name=%s" % (eid, name),
                 "items.%s.description=%s" % (eid, desc), "server.items.%s.description=%s" % (eid, desc)]
    files["Server/Item/Qualities/%s.json" % QUALITY] = json.dumps({
        "QualityValue": QUALITY_VALUE,
        "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltipEpic.png",
        "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltipEpicArrow.png",
        "SlotTexture": "UI/ItemQualities/Slots/SlotEpic.png",
        "BlockSlotTexture": "UI/ItemQualities/Slots/SlotEpic.png",
        "SpecialSlotTexture": "UI/ItemQualities/Slots/SlotEpic.png",
        "TextColor": QUALITY_COLOR,
        "LocalizationKey": "server.general.qualities." + QUALITY,
        "VisibleQualityLabel": True,
        "RenderSpecialSlot": True,
        "ItemEntityConfig": {"ParticleSystemId": "Drop_Epic"}}, indent=2)
    lang += ["general.qualities.%s=%s" % (QUALITY, QUALITY_LABEL), "server.general.qualities.%s=%s" % (QUALITY, QUALITY_LABEL)]
    lang += TAB_LANG
    # the tab icon = the Enchanted Cobblestone icon (64 x 64 like the vanilla tab icons)
    ref = SA.png_size(SA._read(z, "Icons/CraftingCategories/Workbench/Processing.png"))
    tab = files["Common/Icons/ItemsGenerated/SkyyCollections_Ench_Cobblestone.png"]
    assert SA.png_size(tab) == ref, (SA.png_size(tab), ref)
    files["Common/" + tab_icon_path()] = tab
    return files, lang


BASE_LABEL = {"Cobblestone": "Cobblestone", "Rubble": "stone Rubble (any kind but Ice or Dawnstone)", "Copper": "Copper Ingots", "Iron": "Iron Ingots",
              "Thorium": "Thorium Ingots", "Cobalt": "Cobalt Ingots", "Adamantite": "Adamantite Ingots", "Oak": "Oak Logs",
              "Maple": "Maple Logs", "Gumboab": "Gumboab Logs", "Redwood": "Redwood Logs", "Sallow": "Sallow Logs", "Wheat": "Wheat",
              "Carrot": "Carrots", "Cauliflower": "Cauliflowers", "Pumpkin": "Pumpkins", "Tomato": "Tomatoes", "Cotton": "Cotton",
              "Potato": "Potatoes", "Stick": "Sticks"}
# C1 (0.2.21): the base of every new row, as the description says it ("100 <label> pressed into one")
BASE_LABEL.update({"Corn": "Corn", "Lettuce": "Lettuce", "Onion": "Onions", "Turnip": "Turnips", "Aubergine": "Aubergines",
                   "Chilli": "Chillies", "Rice": "Rice", "Berries": "Wild Berries", "Apple": "Apples", "WildFruit": "Coconuts",
                   "Mushroom": "Brown Cap Mushrooms", "Cactus": "Cactus Bottoms", "Seeds": "Wheat Seed Bags",
                   "Petals": "Blood Petals", "RawChicken": "Raw Chicken", "RawBeef": "Raw Beef", "RawPork": "Raw Pork",
                   "Wildmeat": "Raw Wildmeat", "Fiber": "Plant Fiber", "TreeSap": "Tree Sap",
                   "Sandstone": "Sandstone Cobble", "Shale": "Shale Cobble", "Slate": "Slate Cobble", "Basalt": "Basalt Cobble",
                   "Volcanic": "Volcanic Cobble", "Marble": "Marble Cobble", "Quartzite": "Quartzite Cobble", "Limestone": "Limestone Cobble",
                   "Ice": "Ice blocks", "Salt": "Salt Blocks", "Sand": "Sand (any colour)", "Clay": "Clay", "Silver": "Silver Ingots",
                   "Gold": "Gold Ingots", "Mithril": "Mithril Ingots", "Crystal": "Crystal Shards (any colour)", "Gemstone": "Diamonds",
                   "Bone": "Bone Fragments", "Linen": "Linen Scraps", "HideLight": "Light Hides", "HideMedium": "Medium Hides",
                   "HideHeavy": "Heavy Hides", "Wool": "Wool Scraps", "Feathers": "White Feathers", "Chitin": "Sturdy Chitin",
                   "Venom": "Venom Sacs", "Shadoweave": "Shadoweave Scraps", "Cindercloth": "Cindercloth Scraps",
                   "FireEssence": "Essence of Fire", "IceEssence": "Essence of Ice", "VoidEssence": "Essence of the Void",
                   "LightningEssence": "Essence of Lightning", "Voidheart": "Voidhearts", "BoomPowder": "Boom Powder"})
# ores01 (0.2.25)
BASE_LABEL.update({"Lead": "Lead Ingots", "Chromium": "Chromium Ingots", "Slag": "Slag Ingots", "Titanium": "Titanium Ingots",
                   "Charcoal": "Charcoal"})
for _t in TABLE_C1:
    if _t[7][1].startswith("Wood_"):
        BASE_LABEL.setdefault(_t[0], _t[6][len("Enchanted "):] + "s")
assert sorted(BASE_LABEL) == sorted(KEYS)

# ================================================================================================================ round E1 (2026-10-25)
# Pocket crafting + the reverse recipe (rules at the top). Every function takes the table it works on (default: TABLE) - SkyyCollections
# passes its live table (TABLE + TABLE_ALLOYS), SkyyBazaar the same rows.
FIELD_ID = "Fieldcraft"                     # the vanilla inventory crafting bench (Server/Item/Category/Fieldcraft/Tools.json = its one tab)
FIELD_CAT = "SkyyCompressing"               # our own FieldcraftCategory asset: a "Compressing" tab in the inventory crafting
FIELD_CAT_PATH = "Server/Item/Category/Fieldcraft/%s.json" % FIELD_CAT
FIELD_CAT_ORDER = 1                         # after vanilla Tools (Order 0)
REV_DIR = "Server/Item/Recipes/SkyyCollections/"
REV_PREFIX = "SkyyCollections_Unpack_"      # + key: 1 Enchanted -> RATIO base
PACK_PREFIX = "SkyyCollections_Pack_"       # + collection id: a VANILLA_ENCH pair's 100 -> 1 in the inventory / Compressing tab
REV_SECONDS = 1


def bench_req(e1=False):
    """the BenchRequirement of every Enchanted recipe: the Workbench Compressing tab (+ E1: the inventory crafting's Compressing tab)"""
    out = [{"Type": "Crafting", "Id": BENCH_ID, "Categories": [TAB_ID]}]
    if e1:
        out.append({"Type": "Crafting", "Id": FIELD_ID, "Categories": [FIELD_CAT]})
    return out


def rev_out(t):
    """the item a row's reverse recipe gives: the input item; a resource-type row (any rubble / sand / crystal) gives its look's vanilla
    item (Rubble_Stone, Soil_Sand, Ingredient_Crystal_Blue - the plain kind; the Bazaar loop check proves no colour pays)"""
    return t[2] if t[1] == "I" else t[7][1]


def reverse_rows(table=None):
    """[(recipe id, input id, output id, output qty, knowledge required, forward recipe id)]: one per row + one per VANILLA_ENCH pair, plus
    the vanilla pair's pocket 100 -> 1 (input = its base, output = the vanilla item). Every one is open (knowledge required False,
    forward recipe id None: the spec 4.2 rule - anyone holding an Enchanted item can craft it back)."""
    table = TABLE if table is None else table
    out = []
    for t in table:
        eid = PREFIX + t[0]
        out.append((REV_PREFIX + t[0], eid, rev_out(t), RATIO, False, None))
    for coll in sorted(VANILLA_ENCH):
        vid = VANILLA_ENCH[coll][0]
        base = VANILLA_BASE[coll]
        out.append((PACK_PREFIX + coll, base, vid, 1, False, None))
        out.append((REV_PREFIX + coll, vid, base, RATIO, False, None))
    return out


# the vanilla pair's base (its vanilla recipe: 100 Ingredient_Life_Essence -> 1 at the Farmer's Workbench - e1_files checks it in Assets.zip)
VANILLA_BASE = {"LifeEssence": "Ingredient_Life_Essence"}
assert sorted(VANILLA_BASE) == sorted(VANILLA_ENCH)


def _recipe_json(inp, qin, out, qout, kr):
    return json.dumps({"Input": [{"ItemId": inp, "Quantity": qin}], "PrimaryOutput": {"ItemId": out, "Quantity": qout},
                       "Output": [{"ItemId": out, "Quantity": qout}], "BenchRequirement": bench_req(True),
                       "KnowledgeRequired": kr}, indent=2) + "\n"   # no TimeSeconds: Fieldcraft refuses a delay (smoke 2026-10-27)


def e1_files(z, table=None):
    """{jar path: str}: the inventory crafting category + every reverse_rows recipe (standalone, the vanilla Salvage format). z = Assets.zip
    (read-only): the vanilla pair's recipe must still be 100 -> 1 (else the pocket copy / the reverse would change its ratio)."""
    table = TABLE if table is None else table
    names = set(z.namelist())
    assert "Server/Item/Category/Fieldcraft/Tools.json" in names and FIELD_CAT_PATH not in names, "E1: the vanilla Fieldcraft categories moved"
    tools = json.loads(z.read("Server/Item/Category/Fieldcraft/Tools.json").decode("utf-8-sig"))
    assert set(tools) == set(["Name", "Icon", "Order"]) and tools["Order"] < FIELD_CAT_ORDER, ("E1: Fieldcraft/Tools changed", tools)
    items = _items(z)
    for coll in VANILLA_ENCH:
        r = items[VANILLA_ENCH[coll][0]].get("Recipe") or {}
        assert r.get("Input") == [{"ItemId": VANILLA_BASE[coll], "Quantity": RATIO}] and r.get("OutputQuantity", 1) == 1 and \
            not r.get("KnowledgeRequired"), ("E1: the vanilla %s recipe is not %d -> 1 (open) any more" % (coll, RATIO), r)
    files = {FIELD_CAT_PATH: json.dumps({"Name": TAB_NAME_KEY, "Icon": tab_icon_path(), "Order": FIELD_CAT_ORDER}, indent=2) + "\n"}
    for rid, inp, out, q, kr, _fwd in reverse_rows(table):
        qin = RATIO if q == 1 else 1
        files[REV_DIR + rid + ".json"] = _recipe_json(inp, qin, out, q, kr)
    return files


def tab_order(table=None):
    """the Compressing tabs' order (EnchRank): each forward recipe, then its reverse; the vanilla pair last"""
    table = TABLE if table is None else table
    out = []
    for t in table:
        out += [PREFIX + t[0] + RECIPE_SUFFIX, REV_PREFIX + t[0]]
    for coll in sorted(VANILLA_ENCH):
        out += [PACK_PREFIX + coll, REV_PREFIX + coll]
    return out


assert len(reverse_rows()) == len(TABLE) + 2 * len(VANILLA_ENCH) and len(set(r[0] for r in reverse_rows())) == len(reverse_rows())
assert not [r for r in reverse_rows() if r[4]] and len(set(r[2] for r in reverse_rows() if r[1].startswith(PREFIX))) == len(TABLE),     "E1: a reverse recipe behind an unlock, or two Enchanted items would unpack into the same base item"
# ench01fix: the Rubble recipe takes ResourceTypeId "Rubble" = Rubble_Stone and every Rubble_* whose Parent is Rubble_Stone, EXCEPT
# Rubble_Ice(_Medium) (type Ice) and Rubble_Dawnstone(_Medium) (no parent, no type); the Rubble COLLECTION still counts all of them.
# One recipe can take only one resource type and vanilla items are never overridden, so the label says so (a known gap).


def legacy_0221():
    """the table exactly as SkyyCollections 0.2.21 / 0.2.22 were built (103 rows, Skyy_Ench_LifeEssence included), as a namespace a frozen
    rebuild of those pins can use in place of this module (TABLE / KEYS / IDS / RIDS / BASE_LABEL / cat_of / row / sacks_home_java; the
    functions of this module see the live 102 rows, so build_assets / check_assets / emit_tab must be given the namespace's lists - the
    SkyyBazaar 0.1.17 TABLE_20 freeze pattern). tools/tier_tags.py no longer lists Skyy_Ench_LifeEssence in ENCH_UNTAGGED."""
    import types
    ns = types.SimpleNamespace(**dict((k, v) for k, v in globals().items() if not k.startswith("__")))
    ns.TABLE = list(TABLE_0221)
    ns.KEYS = [t[0] for t in ns.TABLE]
    ns.IDS = [PREFIX + k for k in ns.KEYS]
    ns.RIDS = [i + RECIPE_SUFFIX for i in ns.IDS]
    ns.BASE_LABEL = dict(BASE_LABEL, LifeEssence="Essence of Life")
    ns.row = lambda key: ([t for t in ns.TABLE if t[0] == key] or [None])[0]
    ns.cat_of = lambda i: (ns.row(i[len(PREFIX):]) or [None] * 6)[5] if isinstance(i, str) and i.startswith(PREFIX) else None
    ns.base_label = lambda key: ns.BASE_LABEL[key]
    ns.sacks_home_java = lambda: _home_java(ns.IDS, ns.TABLE)
    return ns


def legacy_0224():
    """ores01: the table exactly as SkyyCollections 0.2.24 / SkyySacks 0.8.19 / SkyyBazaar 0.1.19 were built (102 rows, before TABLE_ORES), as
    a namespace for a frozen rebuild of those pins (the legacy_0221 pattern: give build_assets / check_assets / emit_tab its lists)"""
    import types
    ns = types.SimpleNamespace(**dict((k, v) for k, v in globals().items() if not k.startswith("__")))
    ns.TABLE = list(TABLE_0224)
    ns.TABLE_C1 = list(TABLE_C1_0224)
    ns.KEYS = [t[0] for t in ns.TABLE]
    ns.IDS = [PREFIX + k for k in ns.KEYS]
    ns.RIDS = [i + RECIPE_SUFFIX for i in ns.IDS]
    ns.BASE_LABEL = dict((k, v) for k, v in BASE_LABEL.items() if k in ns.KEYS)
    ns.row = lambda key: ([t for t in ns.TABLE if t[0] == key] or [None])[0]
    ns.cat_of = lambda i: (ns.row(i[len(PREFIX):]) or [None] * 6)[5] if isinstance(i, str) and i.startswith(PREFIX) else None
    ns.base_label = lambda key: ns.BASE_LABEL[key]
    ns.sacks_home_java = lambda: _home_java(ns.IDS, ns.TABLE)
    return ns


def base_label(key):
    return BASE_LABEL[key]


def tab_icon_path():
    return "Icons/CraftingCategories/SkyyCollections/Compressing.png"


def check_assets(files, z, e1=False):
    """build checks: every TABLE item (20 since tools01, 103 since C1, 107 since ores01), one quality, every Model / Texture / Icon / sound / particle / quality texture exists in Assets.zip or the
    jar, no vanilla path replaced, the recipe = RATIO x the base, KnowledgeRequired, the Compressing tab, no reverse recipe in the jar"""
    names = set(z.namelist())

    def exists(p):
        q = "Common/" + p
        return q in names or q in files or (q.endswith(".png") and q[:-4] + "@2x.png" in names)
    its = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    assert sorted(its) == sorted(IDS), sorted(its)
    sounds = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Audio/ItemSounds/") and n.endswith(".json"))
    parts = set(n.rsplit("/", 1)[1][:-len(".particlesystem")] for n in names if n.endswith(".particlesystem"))
    vitems = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    for (key, kind, inp, coll, tier, cat, name, look) in TABLE:
        n = its[PREFIX + key]
        for k in ("Model", "Texture", "Icon"):
            assert exists(n[k]), (key, k, n[k])
        assert n["Quality"] == QUALITY and n["MaxStack"] == STACK and "BlockType" not in n and "Parent" not in n, key
        assert n.get("ItemSoundSetId") is None or n["ItemSoundSetId"] in sounds, (key, n.get("ItemSoundSetId"))
        r = n["Recipe"]
        assert r["KnowledgeRequired"] is True and r["OutputQuantity"] == 1 and len(r["Input"]) == 1, key
        i0 = r["Input"][0]
        assert i0["Quantity"] == RATIO and (i0.get("ItemId") == inp if kind == "I" else i0.get("ResourceTypeId") == inp), key
        assert kind == "R" or inp in vitems or inp in EXTERNAL_INPUTS, (key, inp)          # ores01: the SkyyWorldGen ingots
        assert inp not in vitems or inp not in EXTERNAL_INPUTS, (key, inp, "an external input became a vanilla id")
        assert r["BenchRequirement"] == bench_req(e1), key
    q = json.loads(files["Server/Item/Qualities/%s.json" % QUALITY])
    for k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture", "BlockSlotTexture", "SpecialSlotTexture"):
        assert exists(q[k]), k
    assert q["ItemEntityConfig"]["ParticleSystemId"] in parts and q["QualityValue"] < 8
    clash = sorted(p for p in files if p in names)
    assert not clash, "an Enchanted asset would replace a vanilla file: %s" % clash
    # every ITEM recipe here makes an Enchanted item (no un-compress inside an item JSON)
    for p, t in files.items():
        if p.startswith("Server/") and p.endswith(".json") and '"Recipe"' in t:
            assert p.rsplit("/", 1)[1][:-5].startswith(PREFIX), p
    rev = [p for p in files if p.startswith(REV_DIR) and p.rsplit("/", 1)[1].startswith((REV_PREFIX, PACK_PREFIX))]
    if not e1:
        assert not rev and FIELD_CAT_PATH not in files, "a reverse recipe / the inventory tab in a jar built without e1: %s" % rev[:3]
        return "%d Enchanted items (ratio %d, stack %d), quality %s, %d art files, Workbench tab '%s'" % (
            len(its), RATIO, STACK, QUALITY, sum(1 for p in files if p.startswith("Common/")), TAB_TEXT)
    # E1: exactly the reverse_rows recipes of the shipped table: 1 -> RATIO of the forward's base (or RATIO -> 1 for the vanilla pair's
    # pocket copy), both Compressing tabs, every one open (KnowledgeRequired false)
    want = dict((rid, (inp, out, q, kr)) for rid, inp, out, q, kr, _f in reverse_rows(TABLE))
    got = {}
    for p in rev:
        d = json.loads(files[p])
        assert len(d["Input"]) == 1 and len(d["Output"]) == 1 and d["Output"][0] == d["PrimaryOutput"], p
        assert d["BenchRequirement"] == bench_req(True) and d["KnowledgeRequired"] in (True, False), p
        got[p.rsplit("/", 1)[1][:-5]] = (d["Input"][0]["ItemId"], d["Output"][0]["ItemId"], d["Output"][0]["Quantity"], d["KnowledgeRequired"])
        assert (d["Input"][0]["Quantity"], d["Output"][0]["Quantity"]) in ((1, RATIO), (RATIO, 1)), p
    assert got == want, "E1: the reverse recipes differ from reverse_rows: %s" % sorted(set(got.items()) ^ set(want.items()))[:4]
    for (key, kind, inp, coll, tier, cat, name, look) in TABLE:
        o = want[REV_PREFIX + key]
        assert o[0] == PREFIX + key and o[2] == RATIO and o[3] is False and its[o[0]]["Recipe"]["KnowledgeRequired"] is True, key   # the way back: open
        assert o[1] == inp if kind == "I" else (o[1] == look[1] and its[o[0]]["Recipe"]["Input"][0]["ResourceTypeId"] == inp), (key, o)
    cat = json.loads(files[FIELD_CAT_PATH])
    assert cat["Name"] == TAB_NAME_KEY and exists(cat["Icon"]) and FIELD_CAT_PATH not in names, cat
    return "%d Enchanted items (ratio %d, stack %d), quality %s, %d art files, Workbench tab '%s' + inventory crafting tab %s; %d reverse / pocket recipes" % (
        len(its), RATIO, STACK, QUALITY, sum(1 for p in files if p.startswith("Common/")), TAB_TEXT, FIELD_CAT, len(rev))


# ================================================================================================================ the Compressing tab
# Same engine facts as tools/skyywbtab.py (its probe() runs in the SkyyCollections build): the Workbench tabs are the ordered array
# CraftingBench.categories (protected), rebuilt into each window from getCategories(); a tab is APPENDED at runtime to every Workbench
# CraftingBench (copy-on-write) by its one owner (SkyyCollections), re-applied after an asset reload (LoadedAssetsEvent); the recipes
# land in it through their BenchRequirement Categories; the order inside the tab = a TreeSet in TABLE order (EnchRank).
CB = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench"
CBC = CB + "$BenchCategory"
BIC = CB + "$BenchItemCategory"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
BT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
CRP = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
BRR = "com.hypixel.hytale.builtin.crafting.BenchRecipeRegistry"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
LAE = "com.hypixel.hytale.assetstore.event.LoadedAssetsEvent"
LOGT = "com.hypixel.hytale.logger.HytaleLogger"


def emit_tab(pool, CtField, CtNewMethod, CtNewConstructor, pkg, mod, e1=False):
    """<pkg>.EnchRank (order), <pkg>.EnchTab (append + sort), <pkg>.EnchTabL (asset reloads). Returns the CtClass list.
    e1 (SkyyCollections 0.2.34+): the order = tab_order() (each forward recipe, then its reverse) and sort() also orders the inventory
    crafting's Compressing tab (bench Fieldcraft, category FIELD_CAT); without e1 the classes are byte-identical to before."""
    tok = {"@PKG@": pkg, "@CB@": CB, "@CBC@": CBC, "@BIC@": BIC, "@BEN@": BEN, "@BT@": BT, "@CRP@": CRP, "@BRR@": BRR, "@LAE@": LAE,
           "@LOGT@": LOGT, "@MOD@": mod}

    def T(src):
        for k, v in tok.items():
            src = src.replace(k, v)
        assert "@" not in src, src[:200]
        return src
    rank = pool.makeClass(pkg + ".EnchRank")
    rank.addInterface(pool.get("java.util.Comparator"))
    tab = pool.makeClass(pkg + ".EnchTab")
    lis = pool.makeClass(pkg + ".EnchTabL")
    lis.addInterface(pool.get("java.util.function.Consumer"))

    def F(c, s):
        c.addField(CtField.make(T(s), c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(T(s), c))
    F(rank, "public static final String[] ORDER = %s;" % _jarr(tab_order() if e1 else RIDS))
    rank.addConstructor(CtNewConstructor.make("public EnchRank() { }", rank))
    M(rank, """
public static int rank(String id) {
  if (id == null) return 9999;
  for (int i = 0; i < ORDER.length; i++) if (ORDER[i].equals(id)) return i;
  return 999;
}""")
    M(rank, """
public int compare(Object a, Object b) {
  String x = (String) a;
  String y = (String) b;
  int rx = rank(x);
  int ry = rank(y);
  if (rx != ry) return rx < ry ? -1 : 1;
  return x.compareTo(y);
}""")
    F(tab, "public static final String ID = \"%s\";" % TAB_ID)
    F(tab, "public static final String NAME = \"%s\";" % TAB_NAME_KEY)
    F(tab, "public static final String TEXT = \"%s\";" % TAB_TEXT)
    F(tab, "public static final String ICON = \"%s\";" % tab_icon_path())
    F(tab, "public static final String BENCH = \"%s\";" % BENCH_ID)
    F(tab, "public static final String PROTO = \"%s\";" % ENCH_VERSION)
    if e1:
        F(tab, "public static final String FBENCH = \"%s\";" % FIELD_ID)
        F(tab, "public static final String FCAT = \"%s\";" % FIELD_CAT)
    F(tab, "public static @LOGT@ LOG;")
    F(tab, "public static java.lang.reflect.Field CATS;")
    F(tab, "public static java.lang.reflect.Field REGS;")
    F(tab, "public static java.lang.reflect.Field CMAP;")
    F(tab, "public static volatile boolean CATS_BAD = false;")
    F(tab, "public static volatile boolean MAP_BAD = false;")
    F(tab, "public static volatile boolean WARN_SCAN = false;")
    F(tab, "public static volatile boolean WARN_SORT = false;")
    F(tab, "public static volatile String LAST = \"not started\";")
    M(tab, """
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[@MOD@] " + m); } catch (Throwable t) { }
}""")
    M(tab, """
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[@MOD@] " + m); } catch (Throwable t) { }
}""")
    M(tab, """
public static java.lang.reflect.Field catsField() {
  if (CATS != null) return CATS;
  if (CATS_BAD) return null;
  try {
    java.lang.reflect.Field f = @CB@.class.getDeclaredField("categories");
    f.setAccessible(true);
    CATS = f;
    return f;
  } catch (Throwable t) {
    CATS_BAD = true;
    warn("Compressing tab: the game changed (CraftingBench.categories: " + t + ") - the Enchanted recipes are not shown at the Workbench; /craft still makes them");
    return null;
  }
}""")
    M(tab, """
public static boolean mapFields() {
  if (REGS != null && CMAP != null) return true;
  if (MAP_BAD) return false;
  try {
    java.lang.reflect.Field a = @CRP@.class.getDeclaredField("registries");
    a.setAccessible(true);
    java.lang.reflect.Field b = @BRR@.class.getDeclaredField("categoryMap");
    b.setAccessible(true);
    REGS = a;
    CMAP = b;
    return true;
  } catch (Throwable t) {
    MAP_BAD = true;
    warn("Compressing tab: the game changed (recipe registry: " + t + ") - the tab lists its recipes in the engine's own order");
    return false;
  }
}""")
    M(tab, """
public static @CBC@ mine() {
  return new @CBC@(ID, NAME, ICON, (@BIC@[]) null);
}""")
    # 0 = already there (same name + icon), 1 = appended, 2 = an entry with our id replaced in place, -1 = failed. Copy-on-write.
    M(tab, """
public static int applyTo(@CB@ b) {
  java.lang.reflect.Field f = catsField();
  if (f == null || b == null) return -1;
  try {
    @CBC@[] cur = b.getCategories();
    int n = cur == null ? 0 : cur.length;
    for (int i = 0; i < n; i++) {
      if (cur[i] == null || !ID.equals(cur[i].getId())) continue;
      if (ICON.equals(cur[i].getIcon()) && NAME.equals(cur[i].getName())) return 0;
      @CBC@[] cp = new @CBC@[n];
      for (int j = 0; j < n; j++) cp[j] = cur[j];
      cp[i] = mine();
      f.set(b, cp);
      return 2;
    }
    @CBC@[] out = new @CBC@[n + 1];
    for (int k = 0; k < n; k++) out[k] = cur[k];
    out[n] = mine();
    f.set(b, out);
    return 1;
  } catch (Throwable t) { return -1; }
}""")
    M(tab, """
public static int locked(@CB@ b) {
  int r = -1;
  synchronized (b) { r = applyTo(b); }
  return r;
}""")
    M(tab, """
public static int scan(java.util.Collection c) {
  if (c == null) return 0;
  if (catsField() == null) return -1;
  java.util.IdentityHashMap seen = new java.util.IdentityHashMap();
  int ok = 0;
  int bad = 0;
  java.util.Iterator it = c.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @BT@)) continue;
    @BEN@ be = ((@BT@) o).getBench();
    if (!(be instanceof @CB@) || !BENCH.equals(be.getId())) continue;
    if (seen.put(be, be) != null) continue;
    if (locked((@CB@) be) < 0) bad++; else ok++;
  }
  if (bad > 0 && !WARN_SCAN) {
    WARN_SCAN = true;
    warn("Compressing tab: could not add the tab to " + bad + " Workbench definition(s) - the Enchanted recipes are not shown there; /craft still makes them");
  }
  return (bad > 0 && ok == 0) ? -1 : ok;
}""")
    M(tab, """
public static int scanAll() {
  try {
    return scan(@BT@.getAssetMap().getAssetMap().values());
  } catch (Throwable t) {
    if (!WARN_SCAN) { WARN_SCAN = true; warn("Compressing tab: could not read the block types (" + t + ")"); }
    return -1;
  }
}""")
    if not e1:
        M(tab, """
public static String sort() {
  if (!mapFields()) return "the engine's order (registry unavailable)";
  try {
    java.util.Map regs = (java.util.Map) REGS.get(null);
    Object reg = regs == null ? null : regs.get(BENCH);
    if (reg == null) return "no Workbench recipes loaded yet";
    java.util.Map cm = (java.util.Map) CMAP.get(reg);
    Object cur = cm.get(ID);
    if (cur instanceof java.util.TreeSet && ((java.util.TreeSet) cur).comparator() instanceof @PKG@.EnchRank)
      return "table order, " + ((java.util.Set) cur).size() + " recipes";
    java.util.TreeSet ts = new java.util.TreeSet(new @PKG@.EnchRank());
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    cm.put(ID, ts);
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    return "table order, " + ts.size() + " recipes";
  } catch (Throwable t) {
    if (!WARN_SORT) { WARN_SORT = true; warn("Compressing tab: could not order the recipes (" + t + ") - they stay in the engine's own order"); }
    return "the engine's order";
  }
}""")
    else:
        # E1: the same ordering for one (bench, tab) pair, applied to the Workbench tab and the inventory crafting tab
        M(tab, """
public static String sortIn(String bench, String cat) {
  try {
    java.util.Map regs = (java.util.Map) REGS.get(null);
    Object reg = regs == null ? null : regs.get(bench);
    if (reg == null) return "no " + bench + " recipes loaded yet";
    java.util.Map cm = (java.util.Map) CMAP.get(reg);
    Object cur = cm.get(cat);
    if (cur instanceof java.util.TreeSet && ((java.util.TreeSet) cur).comparator() instanceof @PKG@.EnchRank)
      return "table order, " + ((java.util.Set) cur).size() + " recipes";
    java.util.TreeSet ts = new java.util.TreeSet(new @PKG@.EnchRank());
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    cm.put(cat, ts);
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    return "table order, " + ts.size() + " recipes";
  } catch (Throwable t) {
    if (!WARN_SORT) { WARN_SORT = true; warn("Compressing tab: could not order the recipes (" + t + ") - they stay in the engine's own order"); }
    return "the engine's order";
  }
}""")
        M(tab, """
public static String sort() {
  if (!mapFields()) return "the engine's order (registry unavailable)";
  String a = sortIn(BENCH, ID);
  String b = sortIn(FBENCH, FCAT);
  return a + "; inventory crafting: " + b;
}""")
    M(tab, """
public static String start() {
  int n = scanAll();
  String s = sort();
  String line;
  if (n > 0) line = "Workbench tab '" + TEXT + "' on " + n + " Workbench definition(s); order: " + s + " (ench protocol " + PROTO + ")";
  else if (n == 0) line = "Workbench tab '" + TEXT + "': no Workbench block type found yet (the asset reload listener adds it later)";
  else line = "Workbench tab '" + TEXT + "' could not be added - see the warning above";
  LAST = line;
  if (n >= 0) info(line); else warn(line);
  return line;
}""")
    M(tab, """
public static void onLoaded(Object e) {
  try {
    @LAE@ ev = (@LAE@) e;
    if (ev.getAssetClass() == @BT@.class) {
      java.util.Map m = ev.getLoadedAssets();
      if (m != null) scan(m.values());
      scanAll();
    } else sort();
  } catch (Throwable t) { }
}""")
    lis.addConstructor(CtNewConstructor.make("public EnchTabL() { }", lis))
    M(lis, """
public void accept(Object e) {
  try { @PKG@.EnchTab.onLoaded(e); } catch (Throwable t) { }
}""")
    return [rank, tab, lis]


def setup_java(pkg):
    return ("  // 0.2.11 Workbench tab 'Compressing' (tools/skyyench.py): re-applied after an asset reload (new BlockType objects / recipe sets)\n"
            "  %s.EnchTab.LOG = getLogger();\n"
            "  try {\n"
            "    getEventRegistry().register(%s.class, %s.class, new %s.EnchTabL());\n"
            "    getEventRegistry().register(%s.class, %s.class, new %s.EnchTabL());\n"
            "  } catch (Throwable twb) { %s.EnchTab.warn(\"Compressing tab: no asset reload listener (\" + twb + \") - a live asset reload drops the tab until a restart\"); }\n"
            % (pkg, LAE, BT, pkg, LAE, CRR, pkg, pkg))
