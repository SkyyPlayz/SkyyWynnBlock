"""Test tools/tier_tags.py (research/Tier-Tags-Plan.md round T0).   python tools/test_tier_tags.py   (exit 0 = PASS)

Checks (TT_VERSION 3, SkyyGear 0.3.29 = 20 levels per zone: METAL_BANDS / ZONE_TOPS / LEVEL_BANDS / LEVEL_CRUDE 5, the 15 tree + 15 crop tiers,
the Mushroom spores, the Foraging / Farming / Fishing armor rows): the 15-step ladder (TT_VERSION 2, SkyyGear 0.3.22 round G1: T1 Copper .. T15 Lumen, Onyxium T16, Crude shares T1) + display(internal)
+ the TT_VERSION 1 -> 2 renumber map; the tier for sample ids of every family; family counts (plan 1.2); every vanilla id in the table exists
in Assets.zip (the cached copy, tools/serverjar.py - read-only; skipped with a note when no copy exists); the Enchanted rows =
tools/skyyench.py TABLE (minus Cobblestone / Rubble) at their base's tier; TOOL_METALS starts with SkyyGear's TOOL_TIERS words (the SET pin's
build script, read as text) at display(internal); the level band rule (LEVEL_BANDS); the tag / described() format.
"""
import os, re, sys, ast, zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import tier_tags as TT
import skyyench as EN

FAILS = []
NOTES = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)


# ---- ladder
ok(TT.TT_VERSION == "3" and TT.LADDER == ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite",
                                          "Slag", "Cinder", "Mithril", "Titanium", "Lumen", "Onyxium"), "the 15-step ladder + Onyxium T16")
ok(TT.GEAR_INTERNAL == ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"), "Gear's internal tiers")
ok([TT.display(i) for i in range(8)] == [1, 1, 2, 4, 7, 10, 13, 16], "display(internal) = the ladder step of Gear's tier word")
ok([TT.to_internal(d) for d in (1, 2, 3, 4, 7, 16)] == [1, 2, None, 3, 4, 7], "to_internal (T1 = Copper, T3 Bronze has no internal tier)")
ok([TT.renumber(d) for d in range(1, 9)] == [1, 1, 2, 4, 7, 10, 13, 16], "renumber: T1 Crude .. T8 Onyxium -> the new numbers")
ok(TT.tag_text(2) == "T2 Iron" and TT.tag_text(1) == "T1 Copper" and TT.tag_text(16) == "T16 Onyxium" and TT.tag_text(1, "Crude") == "T1 Crude"
   and TT.tag_text(15) == "T15 Lumen", "tag_text")
ok([TT.metal_tier(w) for w in ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag",
                               "Cinder", "Mithril", "Titanium", "Lumen", "Onyxium")] == list(range(1, 17)), "metal_tier = Skyy's zone order")
ok(TT.metal_word("Wood") == "Crude" and TT.metal_word("Scrap") == "Copper" and TT.metal_word("Steel") == "Iron" and TT.metal_word("Lead") == "Lead"
   and TT.metal_word("Stone") is None, "metal_word")
ok(TT.ladder_tag(2, "Totem") == "T2 Totem" and TT.ladder_tag(3, "Loot") == "T3 Loot" and TT.ladder_tag(2, "Bench") == "T2 Bench", "ladder_tag")
ok(TT.ladder_tag(3, "Charm") == "T3 Charm" and TT.ladder_tag(5, "Charm") == "T5 Charm", "ores01: the Furnace Charm ladder word")
for bad in (lambda: TT.display(8), lambda: TT.to_internal(0), lambda: TT.to_internal(17), lambda: TT.ladder_tag(2, "Gem")):
    try:
        bad()
        FAILS.append("an out-of-range call did not raise")
    except AssertionError:
        pass

# ---- samples (popup "Match the tool": materials = the tool metal that works them; TT_VERSION 2: the word stays, the number is its ladder step)
SAMPLES = {
    "Ore_Copper": "T1 Copper", "Ore_Iron": "T2 Iron", "Ore_Thorium": "T4 Thorium", "Ore_Cobalt": "T7 Cobalt", "Ore_Onyxium": "T16 Onyxium",
    "Ingredient_Bar_Bronze": "T3 Bronze", "Ingredient_Bar_Copper": "T1 Copper", "Ingredient_Bar_Mithril": "T13 Mithril",
    # TT_VERSION 3 (spec 5 / 6): 15 tree tiers + 15 crop tiers, 3 per zone
    "Wood_Oak_Trunk": "T1 Copper", "Wood_Apple_Trunk": "T2 Iron", "Wood_Maple_Trunk": "T3 Bronze", "Wood_Dry_Trunk": "T4 Thorium",
    "Wood_Gumboab_Trunk": "T6 Dusk", "Wood_Redwood_Trunk": "T9 Azurvane", "Wood_Sallow_Trunk": "T12 Cinder", "Wood_Fig_Blue_Trunk": "T14 Titanium",
    "Wood_Crystal_Trunk": "T15 Lumen", "Wood_Stormbark_Trunk": "T15 Lumen", "Wood_Ice_Trunk": "T9 Azurvane",
    "Plant_Crop_Wheat_Item": "T1 Copper", "Plant_Crop_Carrot_Item": "T3 Bronze", "Plant_Crop_Turnip_Item": "T6 Dusk",
    "Plant_Crop_Potato_Item": "T13 Mithril", "Plant_Crop_Onion_Item": "T14 Titanium", "Plant_Crop_Mushroom_Cap_Brown": "T15 Lumen",
    "Plant_Seeds_Wheat": "T1 Copper", "Plant_Seeds_Onion_Eternal": "T14 Titanium", "Plant_Seeds_Mushroom": "T15 Lumen",
    "Plant_Spores_Mushroom_Eternal": "T15 Lumen",
    "Skyy_Ench_Copper": "T1 Copper", "Skyy_Ench_Oak": "T1 Copper", "Skyy_Ench_Wheat": "T1 Copper", "Skyy_Ench_Potato": "T13 Mithril",
    "Skyy_Ench_Adamantite": "T10 Adamantite", "Skyy_Ench_Sallow": "T12 Cinder", "Skyy_Ench_Stick": "T1 Crude", "Skyy_Ench_Mushroom": "T15 Lumen",
    "Skyy_Ench_Beech": "T2 Iron", "Skyy_Ench_CrystalLog": "T15 Lumen",
    "Armor_Foraging_F1_Head": "T1 Copper", "Armor_Foraging_F2_Legs": "T3 Bronze", "Armor_Foraging_Crystalwood_Chest": "T15 Lumen",
    "Armor_Farming_P7_Hands": "T14 Titanium", "Armor_Farming_Mushroom_Head": "T15 Lumen", "Armor_Fishing_A5_Head": "T10 Adamantite",
    "Tool_Pickaxe_Crude": "T1 Crude", "Tool_Pickaxe_Wood": "T1 Crude", "Tool_Hoe_Copper": "T1 Copper", "Tool_Pickaxe_Scrap": "T1 Copper",
    "Tool_Sickle_Steel_Rusty": "T2 Iron", "Tool_Hatchet_Onyxium": "T16 Onyxium", "Tool_Pickaxe_Cobalt": "T7 Cobalt", "Tool_Hammer_Crude": "T1 Crude",
    "Weapon_Staff_Wood": "T1 Crude", "Weapon_Wand_Wood_Rotten": "T1 Crude", "Weapon_Wand_Tribal": "T2 Iron", "Weapon_Staff_Onyxium": "T16 Onyxium",
}
for i, want in SAMPLES.items():
    ok(TT.tag_for(i) == want, "tag_for(%s) = %r, want %r" % (i, TT.tag_for(i), want))
for i in ("Skyy_Ench_Cobblestone", "Skyy_Ench_Rubble", "Ore_Silver", "Ore_Gold", "Ore_Prisma", "Ingredient_Bar_Gold", "Rock_Stone_Cobble",
          "Rock_Gem_Ruby", "Ingredient_Bone_Fragment", "Ingredient_Hide_Soft", "Ingredient_Hide_Prismic",
          "Ingredient_Leather_Soft", "Ingredient_Leather_Heavy", "Plant_Seeds_Oak", "Ore_Copper_Stone", ""):
    ok(TT.tag_for(i) is None and TT.tier(i) is None and TT.owner(i) is None, "%s must stay untagged" % i)
ok(TT.internal("Ore_Copper") == 1 and TT.internal("Tool_Pickaxe_Crude") == 0 and TT.internal("Tool_Pickaxe_Wood") == 0
   and TT.internal("Ingredient_Bar_Bronze") is None and TT.internal("Ore_Cobalt") == 4, "internal()")

# ---- described()
ok(TT.described("Ore_Copper", "Can be smelted.") == "T1 Copper - Can be smelted.", "described with text")
ok(TT.described("Plant_Crop_Wheat_Item", "") == "T1 Copper" and TT.described("Plant_Crop_Wheat_Item") == "T1 Copper", "described without text")
ok(TT.described("Wood_Oak_Trunk", "  x  ") == "T1 Copper - x", "described trims")

# ---- counts (plan 1.2)
# ores01 (SkyyWorldGen 0.7.3): + 4 zone ore blocks / raw ores / ingots + 4 alloys (owner SkyyWorldGen); the Enchanted ingots of the new
# metals (tools/skyyench.py TABLE_ORES, SkyyCollections 0.2.25) take their base's tier -> enchanted 55 + those rows
ENCH_ORES = [t for t in getattr(EN, "TABLE_ORES", []) if t[2] in TT.ROWS]
# SkyyCollections 0.2.28 (level-bands): + the six Enchanted alloys (tools/skyyench.py TABLE_ALLOYS - not in its TABLE), at their alloy bar's tier
ENCH_ALLOYS = [t for t in getattr(EN, "TABLE_ALLOYS", []) if t[2] in TT.ROWS]
COUNTS = {"ore": 7, "bar": 8, "log": 34, "crop": 15, "seed": 28, "spore": 2, "enchanted": 56 + len(ENCH_ORES) + len(ENCH_ALLOYS), "foraging_armor": 60,
          "farming_armor": 60, "fishing_armor": 20, "tool": 34, "armory": 11,          # 0.3.29: + the Mushroom (crop, 2 spores, its Enchanted item), the gathering armor rows
          "can": 6 + 10, "harvester": 4 + 12, "forever_tool": 27, "armory_metal": 76 + 80, "zone_ore_block": 4, "zone_ore": 4, "zone_bar": 4, "alloy": 5,
          "mining_armor": 32, "bucket": 1, "rod": 8, "reel": 7, "fish": 27,
          "ut": 64}          # ut28 (SkyyGear 0.3.47): the first 28 Zone 1-5 Untiered items (tools/ut28.py; 55 SkyyGear + 9 SkyyArmory ids)          # fish2 (SkyyFishing 0.2.0): its rods / reels / fish (TT.FI_IDS); SkyyGear 0.3.31: + the Infinite Water Bucket (T4 Thorium, TT.OWN_IDS)
          #          # SkyyGear 0.3.23 (G2): + the forever tools of Bronze + the 8 zone metals (pickaxe / hatchet / multitool 27), cans Mithril + 9, Harvesters Cobalt / Adamantite / Mithril + 9 (TT.OWN_IDS); SkyyGear 0.3.21: the zone Mining sets (Lead .. Lumen x 4 slots, TT.OWN_IDS); tools01: enchanted 17 -> 18 (+ the Enchanted Stick); C1 (SkyyCollections 0.2.21): 18 -> 55 (37 own items on a tiered base); SkyyGear 0.3.12: its OWN watering can + Harvester ladders (TT.OWN_IDS, not in Assets.zip)
for f, n in COUNTS.items():
    ok(len(TT.ids_in(f)) == n, "family %s has %d ids, want %d" % (f, len(TT.ids_in(f)), n))
ok(set(TT.families()) == set(COUNTS), "families: %s" % TT.families())
ok(len(TT.ids_for("SkyyCollections")) == 7 + 8 + 34 + 15 + 28 + 2 + 56 + len(ENCH_ORES) + len(ENCH_ALLOYS), "SkyyCollections owns %d" % len(TT.ids_for("SkyyCollections")))
_GA = TT.ids_in("foraging_armor") + TT.ids_in("farming_armor") + TT.ids_in("fishing_armor")
ok(TT.ids_for("SkyyGear") == sorted(TT.ids_in("tool") + TT.ids_in("can") + TT.ids_in("harvester") + TT.ids_in("mining_armor") + TT.ids_in("forever_tool") + TT.ids_in("bucket") + _GA + [i for i in TT.ids_in("ut") if TT.owner(i) == "SkyyGear"]) and TT.ids_for("SkyyArmory") == sorted(TT.ids_in("armory") + TT.ids_in("armory_metal") + [i for i in TT.ids_in("ut") if TT.owner(i) == "SkyyArmory"]), "owners")
import ut28 as UT28          # ut28 (SkyyGear 0.3.47): the family = the table, the zone's alloy tag, owner by the copy's builder
ok(sorted(TT.UT_IDS) == TT.ids_in("ut") == sorted(UT28.IDS) and all(TT.tag_for(r[0]) == "T%d %s" % (TT.metal_tier(UT28.ZONE_ALLOY[r[3]]), UT28.ZONE_ALLOY[r[3]])
   and TT.owner(r[0]) == ("SkyyGear" if r[4] == "gear" else "SkyyArmory") for r in UT28.rows()) and TT.tag_for("Armor_UT_OasisWarden_Head") == "T6 Dusk"
   and TT.tag_for("Weapon_Longsword_UT_AzureArc") == "T3 Bronze" and TT.tag_for("Weapon_Bo_UT_CrushingTail") == "T15 Lumen" and not UT28.check(), "ut28: the 64 Untiered rows")
ok(sorted(TT.OWN_IDS) == sorted(TT.ids_in("can") + TT.ids_in("harvester") + TT.ids_in("mining_armor") + TT.ids_in("forever_tool") + TT.ids_in("bucket") + _GA) and TT.tag_for("Tool_WaterCan_Crude") == "T1 Crude"
   and TT.tag_for("Tool_WaterCan_Copper") == "T1 Copper" and TT.tag_for("Tool_WaterCan_Iron") == "T2 Iron"
   and TT.tag_for("Tool_WaterCan_Adamantite") == "T10 Adamantite" and TT.tag_for("Tool_Sickle_Harvester_Crude") == "T1 Crude"
   and TT.tag_for("Tool_Sickle_Harvester_Thorium") == "T4 Thorium", "SkyyGear 0.3.12 own ids: the can T1 Crude .. T10 Adamantite, the Harvester .. T4 Thorium")
# SkyyGear 0.3.23 (round G2): the new metals' forever tools at their metal's own step, every id of a non-vanilla tool metal ends _SkyWynn
ok(TT.tag_for("Tool_Pickaxe_Bronze_SkyWynn") == "T3 Bronze" and TT.tag_for("Tool_Pickaxe_Lead_SkyWynn") == "T5 Lead"
   and TT.tag_for("Tool_Hatchet_Pickaxe_Multitool_Lumen_SkyWynn") == "T15 Lumen" and TT.tag_for("Tool_Sickle_Harvester_Cobalt") == "T7 Cobalt"
   and TT.tag_for("Tool_WaterCan_Mithril") == "T13 Mithril" and TT.tag_for("Tool_WaterCan_Azurvane_SkyWynn") == "T9 Azurvane"
   and all(i.endswith("_SkyWynn") for i in TT.ids_in("forever_tool")) and "Tool_Pickaxe_Lead" not in TT.ROWS,
   "SkyyGear 0.3.23 own forever tools: T3 Bronze .. T15 Lumen, _SkyWynn ids (never TerrariaToolsWeapons' Tool_Pickaxe_Lead)")
# SkyyArmory 0.1.33 (round A1): its 76 new-metal weapons at their metal's step, owner SkyyArmory (its lang writes the tags)
ok(sorted(TT.AR_IDS) == TT.ids_in("armory_metal") and TT.tag_for("Weapon_Wand_SoulCage_Lead_SkyWynn") == "T5 Lead"
   and TT.tag_for("Weapon_Fist_Gauntlets_Lumen_SkyWynn") == "T15 Lumen" and TT.tag_for("Weapon_Crossbow_Thorium_Wynn") == "T4 Thorium"
   and all(TT.combat_tag(i, 0) == TT.tag_for(i) for i in TT.AR_IDS), "SkyyArmory 0.1.33 rows = combat_tag of each id (T5 Lead .. T15 Lumen)")
# SkyyArmory 0.1.34 (round A2): + the 80 vanilla-family weapons of the 8 zone metals (spears included), same family / owner
ok(len(TT.A2_WEAPONS) == 80 and set(TT.A2_WEAPONS) <= TT.AR_IDS and TT.tag_for("Weapon_Spear_Lead_SkyWynn") == "T5 Lead"
   and TT.tag_for("Weapon_Shield_Lumen_SkyWynn") == "T15 Lumen" and TT.tag_for("Weapon_Sword_Dusk_SkyWynn") == TT.combat_tag("Weapon_Sword_Dusk_SkyWynn", 0),
   "SkyyArmory 0.1.34 A2 rows (T5 Lead .. T15 Lumen)")
ok(all(r[2] in TT.OWNERS and 1 <= r[0] <= 16 for r in TT.ROWS.values()), "rows in range")
# fish2 (SkyyFishing 0.2.0, research/cloud/Fishing-Stage2-Build.md 2 / 3): rods + reels at their SHOWN metal (T5 / T6 = Chromium / Azurvane on the
# Adamantite / Mithril ids), Wooden = "T1 Crude", fish "T<n> Fish" (zone floor 1 / 4 / 7 or the rod that lands the minimum weight)
_FI = {"SkyyFishing_Rod_Bamboo": "T1 Crude", "SkyyFishing_Rod_Copper": "T1 Copper", "SkyyFishing_Rod_Iron": "T2 Iron", "SkyyFishing_Rod_Thorium": "T4 Thorium",
       "SkyyFishing_Rod_Cobalt": "T7 Cobalt", "SkyyFishing_Rod_Adamantite": "T8 Chromium", "SkyyFishing_Rod_Mithril": "T9 Azurvane",
       "SkyyFishing_Rod_Onyxium": "T16 Onyxium", "SkyyFishing_Reel_Bamboo": "T1 Crude", "SkyyFishing_Reel_Mithril": "T9 Azurvane",
       "SkyyFishing_Fish_OverdueMinnow": "T1 Fish", "SkyyFishing_Fish_PonderingPike": "T2 Fish", "SkyyFishing_Fish_OasisCarp": "T4 Fish",
       "SkyyFishing_Fish_MirageSturgeon": "T7 Fish", "SkyyFishing_Fish_FrostCod": "T7 Fish", "SkyyFishing_Fish_GlassPike": "T8 Fish",
       "SkyyFishing_Fish_SleeperAisle9": "T9 Fish"}
for i, want in _FI.items():
    ok(TT.tag_for(i) == want, "fish2: tag_for(%s) = %r, want %r" % (i, TT.tag_for(i), want))
ok(TT.ids_for("SkyyFishing") == sorted(TT.FI_IDS) == sorted(TT.ids_in("rod") + TT.ids_in("reel") + TT.ids_in("fish")) and len(TT.FI_IDS) == 42
   and "SkyyFishing_Reel_Onyxium" not in TT.ROWS and TT.internal("SkyyFishing_Rod_Adamantite") is None and TT.ladder_tag(4, "Fish") == "T4 Fish"
   and TT.described("SkyyFishing_Fish_OasisCarp", "x") == "T4 Fish - x", "fish2: SkyyFishing owns its 42 ids, own ladder Fish")
ok(all(TT.word(i) == "Crude" for i in TT.ROWS if i.split("_")[2:3] and i.split("_")[2] in ("Crude", "Wood") and i.startswith(("Tool_", "Weapon_")))
   and all(TT.tier(i) == 1 for i in TT.ROWS if TT.word(i) == "Crude"), "every Crude / Wood tool or weapon says 'T1 Crude'")

# ---- ores01: the zone metals (research/Zone-Ores-Alloys-Spec.md 2.3 / 2.5 / 3) at their OWN ladder step (TT_VERSION 2: one above the metal
# before them in Skyy's zone order - the partner + 1 for the new ore, + 2 for the alloy)
ZM = {"Lead": (5, "Sandstone", "Thorium"), "Chromium": (8, "Shale", "Cobalt"), "Slag": (11, "Volcanic", "Adamantite"), "Titanium": (14, "Basalt", "Mithril")}
AL = {"Dusk": (6, "Thorium", "Lead"), "Azurvane": (9, "Cobalt", "Chromium"), "Cinder": (12, "Adamantite", "Slag"), "Lumen": (15, "Mithril", "Titanium"), "Electrum": (3, "Bronze", "Silver")}   # Electrum = the Bronze tier (Gold / Silver untagged)
want_wg = []
for m, (t, h, partner) in ZM.items():
    for i in ("Ore_%s_%s_SkyWynn" % (m, h), "Ore_%s_SkyWynn" % m, "Ingredient_Bar_%s_SkyWynn" % m):
        want_wg.append(i)
        ok(TT.tag_for(i) == "T%d %s" % (t, m) and TT.word(i) == m and TT.tier(i) == TT.tier("Ore_" + partner) + 1, "%s: %s (partner %s T%s)" % (i, TT.tag_for(i), partner, TT.tier("Ore_" + partner)))
        ok(TT.described(i, "x") == "T%d %s - x" % (t, m), "%s described()" % i)
for a, (t, x, y) in AL.items():
    i = "Ingredient_Bar_%s_SkyWynn" % a
    want_wg.append(i)
    ok(TT.tag_for(i) == "T%d %s" % (t, a) and TT.family(i) == "alloy" and TT.tier(i) == TT.tier("Ingredient_Bar_" + x) + (0 if a == "Electrum" else 2), "%s: %s" % (i, TT.tag_for(i)))
ok(sorted(want_wg) == TT.ids_for("SkyyWorldGen") == sorted(TT.WG_IDS) and len(TT.WG_IDS) == 17, "SkyyWorldGen owns exactly the 17 zone-metal ids (+ Electrum)")
ok(all(i.endswith("_SkyWynn") for i in TT.WG_IDS), "every SkyyWorldGen id ends _SkyWynn")
ok(TT.tag_for("Ingredient_Bar_Bronze") == "T3 Bronze" and TT.owner("Ingredient_Bar_Bronze") == "SkyyCollections", "vanilla Bronze = its own step T3 Bronze (Collections' key)")
ok([TT.tier("Armor_Mining_%s_Head" % m) for m in ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")] == [5, 6, 8, 9, 11, 12, 14, 15]
   and TT.tag_for("Armor_Mining_Lumen_Legs") == "T15 Lumen", "the zone Mining sets follow the ladder (T5 Lead .. T15 Lumen)")
ok(TT.word("Ore_Iron") == "Iron" and TT.word("Rock_Stone") is None, "word() falls back to the ladder noun")
for k, b, _x in [(t[0], t[2], 0) for t in ENCH_ORES]:
    ok(TT.tag_for(TT_E := "Skyy_Ench_" + k) == TT.tag_for(b), "%s tag %s = its base %s" % (TT_E, TT.tag_for(TT_E), TT.tag_for(b)))

# ---- shadowed (DynamicSeasons seeds)
ok(all(TT.shadowed(i) for i in TT.ids_in("seed")) and not any(TT.shadowed(i) for i in TT.ROWS if TT.family(i) != "seed"), "shadowed = the seeds only")
ok(len(TT.visible_ids_for("SkyyCollections")) == len(TT.ids_for("SkyyCollections")) - 28, "visible_ids_for = ids_for minus the 28 seeds")
ok("DynamicSeasons" in TT.shadowed("Plant_Seeds_Wheat") and TT.shadowed("Plant_Crop_Wheat_Item") is None, "shadowed() text")

# ---- Enchanted = skyyench TABLE at the base's tier
ench_keys = [t[0] for t in EN.TABLE]
ok(sorted(TT.ids_in("enchanted") + list(TT.ENCH_UNTAGGED)) == sorted(EN.IDS + [EN.PREFIX + t[0] for t in ENCH_ALLOYS]), "Enchanted ids = skyyench.IDS + TABLE_ALLOYS")
ok(len(ENCH_ALLOYS) == 6 and [TT.tag_for(EN.PREFIX + t[0]) for t in ENCH_ALLOYS] == ["T3 Bronze", "T6 Dusk", "T9 Azurvane", "T12 Cinder", "T15 Lumen", "T3 Electrum"], "the Enchanted alloys take their alloy bar's tag")
for t in EN.TABLE:
    eid = EN.PREFIX + t[0]
    if eid in TT.ENCH_UNTAGGED:
        continue
    base = t[2] if t in ENCH_ORES else t[7][1]      # ores01: an external (SkyyWorldGen) base has a vanilla LOOK base in t[7]
    if eid in TT.ENCH_OWN:          # tools01: the Enchanted Stick's base has no row - its own tier (T1)
        ok(TT.tier(eid) == TT.ENCH_OWN[eid] and TT.tier(base) is None, "%s own tier %s (base %s untagged)" % (eid, TT.tier(eid), base))
        continue
    ok(TT.tier(eid) == TT.tier(base) and TT.tier(base) is not None, "%s tier %s vs base %s %s" % (eid, TT.tier(eid), base, TT.tier(base)))

# ---- rarity-tagged items: the 30 pet eggs (SkyyPets 0.4.0, tools/skyyeggs.py) - "Rare Egg - ..." first, no T-number
import skyyeggs as EGG
ok(TT.RARITY_NOUNS == ("Egg", "Dragon Egg") and TT.rarity_tag("Legendary", "Dragon Egg") == "Legendary Dragon Egg" and TT.rarity_tag("Rare", "Egg") == "Rare Egg" and TT.rarity_tag("Mythic", "Egg") == "Mythic Egg", "rarity_tag")
ok(TT.rarity_ids_for("SkyyPets") == sorted(EGG.IDS) and len(TT.RARITY_ROWS) == 37, "the 30 egg rows + 3 dragon eggs + 4 secret eggs, owner SkyyPets")
ok(TT.rarity_ids_for("SkyyPets", "secretegg") == sorted(EGG.SECRET_EGG_IDS) and all(TT.tag_for(i) == "Legendary Egg" and TT.tier(i) is None for i in EGG.SECRET_EGG_IDS),
   "SkyyPets 0.4.19: the 4 secret dragon eggs 'Legendary Egg' (no 'Dragon' in the tag - a secret)")
ok(all(r[2] == "egg" and r[3] == "SkyyPets" for i, r in TT.RARITY_ROWS.items() if i in EGG.IDS), "family egg")
_DE = sorted(e[0] for e in EGG.DRAGON_EGGS if e[3] == "SkyyPets")
ok(TT.rarity_ids_for("SkyyPets", "dragonegg") == _DE and len(_DE) == 3 and all(TT.tag_for(i) == "Legendary Dragon Egg" and TT.tier(i) is None for i in _DE)
   and all(TT.tag_for(e[0]) is None for e in EGG.DRAGON_EGGS if e[3] != "SkyyPets"), "SkyyPets 0.4.11: our 3 dragon eggs 'Legendary Dragon Egg', Aures' eggs untagged")
for _c in EGG.CATEGORIES:
    for _r in EGG.RARITIES:
        _i = EGG.egg_id(_c, _r)
        ok(TT.tag_for(_i) == _r + " Egg" and TT.tier(_i) is None and TT.owner(_i) is None, "%s: tag %s, no metal tier" % (_i, TT.tag_for(_i)))
        ok(EGG.flavor(_c, _r).startswith(TT.tag_for(_i) + TT.SEP), "%s: the egg flavor starts with the table's tag" % _i)
        ok(TT.described(_i, EGG.flavor(_c, _r)[len(TT.tag_for(_i) + TT.SEP):]) == EGG.flavor(_c, _r), "%s: described() = the flavor" % _i)
for bad in (lambda: TT.rarity_tag("Shiny", "Egg"), lambda: TT.rarity_tag("Rare", "Gem")):
    try:
        bad()
        FAILS.append("a bad rarity tag did not raise")
    except AssertionError:
        pass

# ---- band rule (LEVEL_BANDS = the level.material band starts of the ladder metals)
for lv, want in ((0, 1), (3, 1), (7, 1), (8, 2), (14, 2), (15, 3), (19, 3), (20, 4), (27, 4), (28, 5), (35, 6), (40, 7), (47, 7), (48, 8), (55, 9),
                 (60, 10), (68, 11), (75, 12), (80, 13), (87, 13), (88, 14), (94, 14), (95, 15), (103, 15), (150, 15)):
    ok(TT.tier_for_level(lv) == want, "tier_for_level(%d) = %d, want %d" % (lv, TT.tier_for_level(lv), want))
ok(TT.tier_for_level(40, "Weapon_Sword_Onyxium") == 16, "Onyxium id = T16")
ok(TT.level_tag(1) == "T1 Crude" and TT.level_tag(4) == "T1 Crude" and TT.level_tag(5) == "T1 Copper" and TT.level_tag(8) == "T2 Iron"
   and TT.level_tag(28) == "T5 Lead" and TT.level_tag(5, "Armor_Onyxium_Head") == "T16 Onyxium", "level_tag")
ok(TT.combat_tag("Armor_Bronze_Head", 15) == "T3 Bronze" and TT.combat_tag("Armor_Wood_Chest", 1) == "T1 Crude" and TT.combat_tag("Armor_Kweebec_Chest", 6) == "T1 Copper"
   and TT.combat_tag("Armor_Cloth_Wool_Chest", 1) == "T1 Crude", "combat_tag: metal word first, else the level band")
ok([t for _l, t in TT.LEVEL_BANDS] == list(range(15, 1, -1)) and [l for l, _t in TT.LEVEL_BANDS] == sorted([l for l, _t in TT.LEVEL_BANDS], reverse=True),
   "LEVEL_BANDS: one start per step T2..T15, highest first")

# ---- TT_VERSION 3 (SkyyGear 0.3.29, research/Level-Bands-20-Spec.md 1): METAL_BANDS / ZONE_TOPS / family remap / the gathering ladders
_MB = [(1, 8), (8, 15), (15, 23), (20, 28), (28, 35), (35, 43), (40, 48), (48, 55), (55, 63), (60, 68), (68, 75), (75, 83), (80, 88), (88, 95),
       (95, 103), (100, 108)]
ok([TT.band(w) for w in TT.LADDER] == _MB and TT.band("Crude") == TT.band("Wood") == TT.band("Armor_Copper") == (1, 8) and TT.band("Stone") is None,
   "METAL_BANDS = Skyy's approved table (Copper 1-8 ... Lumen 95-103, Onyxium 100-108)")
ok(all(TT.tier_for_level(TT.band(w)[0]) == TT.metal_tier(w) for w in TT.LADDER[:15]), "every metal's band start shows its own T")
ok(TT.ZONE_TOPS == (20, 40, 60, 80, 100) and [TT.zone_of_level(x) for x in (1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 140)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5],
   "ZONE_TOPS + zone_of_level")
ok(TT.LEVEL_CRUDE == 5 and TT.LEVEL_CRUDE_V2 == 10 and TT.LEVEL_BANDS_V2[0] == (50, 15) and TT.LEVEL_BANDS[0] == (95, 15) and TT.LEVEL_BANDS[-1] == (8, 2),
   "LEVEL_BANDS / _V2 ends")


def _lt(lv, bands, crude):          # spec 1.1: the 59 family starts keep the T they show (old LEVEL_BANDS_V2 / LEVEL_CRUDE_V2 vs new)
    t = next((t_ for l_, t_ in bands if lv >= l_), 1)
    return (t, t == 1 and lv < crude)


_FAM_OLD = (5, 10, 15, 20, 25, 30, 35, 40, 45)
ok([TT.remap_family_start(x) for x in _FAM_OLD] == [3, 6, 8, 20, 40, 50, 60, 80, 91], "remap_family_start = spec 1.1 (3, 6, 8, 20, 40, 50, 60, 80, 91)")
ok(all(_lt(x, TT.LEVEL_BANDS_V2, TT.LEVEL_CRUDE_V2) == _lt(TT.remap_family_start(x), TT.LEVEL_BANDS, TT.LEVEL_CRUDE) for x in _FAM_OLD),
   "every non-metal family keeps its T (and its Crude word) after the remap")
ok(sorted(TT.LOGS) == list(range(1, 16)) and all(len(v) >= 2 for v in TT.LOGS.values()) and len(TT.ids_in("log")) == 34
   and len(TT.LOG_TIERS_V2) == 34 and TT.LOG_TIERS_V2["Wood_Maple_Trunk"] == 2, "15 tree tiers, 34 trunks once; the v2 table kept")
ok([TT.tier("Plant_Crop_%s_Item" % c) for c in TT.CROP_LADDER[:14]] == list(range(1, 15)) and TT.CROP_LADDER[-1] == "Mushroom"
   and dict(TT.CROPS)["Potato"] == 13 and len(TT.CROPS) == 14 and TT.CROP_TIERS_V2["Plant_Crop_Potato_Item"] == 16, "15 crop tiers (Mushroom 15th)")
ok(TT.spore_name("Plant_Seeds_Mushroom") == "Mushroom Spores" and TT.spore_name("Plant_Spores_Mushroom_Eternal") == "Eternal Mushroom Spores"
   and TT.spore_name("Plant_Seeds_Wheat") is None and TT.family("Plant_Seeds_Mushroom") == "spore" and not TT.shadowed("Plant_Seeds_Mushroom")
   and "Plant_Spores_Mushroom_Eternal" in TT.CO_IDS, "the Mushroom is planted from SPORES (Skyy), family spore, not shadowed")
ok([TT.tier(TT.gather_armor_id("Foraging", c, "Head")) for _t, c, _l, _n in TT.FORAGING_ARMOR] == list(range(1, 16))
   and [c for _t, c, _l, _n in TT.FORAGING_ARMOR if c.startswith("F") and c[1:].isdigit()] == ["F1", "F2", "F3", "F4", "F5"]
   and [t for t, c, _l, _n in TT.FORAGING_ARMOR if c in ("F1", "F2", "F3", "F4", "F5")] == [1, 3, 6, 9, 12]
   and [t for t, c, _l, _n in TT.FARMING_ARMOR if c.startswith("P") and c[1:].isdigit()] == [1, 3, 5, 7, 10, 11, 14]
   and [TT.tier("Armor_Fishing_A%d_Legs" % k) for k in range(1, 6)] == [1, 2, 4, 7, 10], "gathering armor: old ids at the new slots, Fishing unchanged")

# ---- TOOL_METALS starts with SkyyGear's TOOL_TIERS words at display(internal) (Bronze: its own step T3 above Iron's internal tier; the SET
# pin's build script, text only), then the zone metals + alloys
try:
    import deploy_set
    gv = dict(deploy_set.SET)["SkyyGear"]
    gsrc = open(os.path.join(ROOT, "SkyyGear", "build_skyygear_%s.py" % gv), encoding="utf8").read()
    m = re.search(r"^TOOL_TIERS = (\[.*?\])[ \t]*(?:#[^\n]*)?$", gsrc, re.M | re.S)          # 0.3.23 ends the line with a comment
    gear = ast.literal_eval(m.group(1))
    ok([w for w, t in gear] == [w for w, t in TT.TOOL_METALS[:len(gear)]], "TOOL_METALS words != SkyyGear %s TOOL_TIERS: %s" % (gv, gear))
    ok(all(TT.metal_tier(w) == (3 if w == "Bronze" else TT.display(t)) for w, t in gear), "TOOL_METALS T != display(SkyyGear %s internal tier)" % gv)
    ok([w for w, t in TT.TOOL_METALS[len(gear):]] == ["Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"],
       "TOOL_METALS ends with the 8 zone metals / alloys")
except (OSError, AttributeError, KeyError) as e:
    FAILS.append("could not read SkyyGear's TOOL_TIERS: %s" % e)

# ---- every vanilla id exists in Assets.zip (cached copy)
try:
    import serverjar
    az = serverjar.assets_zip()
except Exception as e:     # no cached copy / no game: the table checks above still ran
    az = None
    NOTES.append("Assets.zip check skipped (%s)" % e)
if az:
    with zipfile.ZipFile(az) as z:
        ids = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    vanilla = [i for i in TT.ROWS if not i.startswith("Skyy_") and i not in TT.OWN_IDS and i not in TT.WG_IDS and i not in TT.AR_IDS and i not in TT.CO_IDS and i not in TT.FI_IDS and i not in TT.UT_IDS]   # FI_IDS: SkyyFishing's build; AR_IDS: SkyyArmory's build   # OWN_IDS: SkyyGear's build; WG_IDS: SkyyWorldGen's
    missing = sorted(i for i in vanilla if i not in ids)
    ok(not missing, "not in Assets.zip: %s" % missing)
    ok(not [i for i in TT.UT_IDS if i in ids] and not [r for r in UT28.rows() if r[4] == "gear" and r[5] not in ids], "ut28: no Untiered id in Assets.zip, every SkyyGear copy's base is")
    ok(not [i for i in TT.WG_IDS if i in ids], "ores01: no SkyyWorldGen id exists in Assets.zip")
    # the plan's family lists are complete: every vanilla trunk, bar (minus Silver / Gold / Prisma) and crop item is in the table
    for pat, skip in ((r"^Wood_[A-Za-z_]+_Trunk$", ()), (r"^Ingredient_Bar_", ("Silver", "Gold", "Prisma")),
                      (r"^Plant_Crop_[A-Za-z]+_Item$", ())):
        left = sorted(i for i in ids if re.match(pat, i) and i not in TT.ROWS and i.split("_")[-1] not in skip)
        ok(not left, "vanilla %s ids missing from the table: %s" % (pat, left))
    NOTES.append("%d vanilla ids found in %s" % (len(vanilla), os.path.basename(os.path.dirname(az))))

for n in NOTES:
    print("note:", n)
if FAILS:
    print("FAIL (%d):" % len(FAILS))
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("test_tier_tags PASS: %d rows, families %s" % (len(TT.ROWS), ", ".join("%s %d" % (f, len(TT.ids_in(f))) for f in TT.families())))
