"""Test tools/tier_tags.py (research/Tier-Tags-Plan.md round T0).   python tools/test_tier_tags.py   (exit 0 = PASS)

Checks: the 15-step ladder (TT_VERSION 2, SkyyGear 0.3.22 round G1: T1 Copper .. T15 Lumen, Onyxium T16, Crude shares T1) + display(internal)
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
ok(TT.TT_VERSION == "2" and TT.LADDER == ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite",
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
    "Wood_Oak_Trunk": "T1 Copper", "Wood_Apple_Trunk": "T1 Copper", "Wood_Maple_Trunk": "T2 Iron", "Wood_Dry_Trunk": "T4 Thorium",
    "Wood_Redwood_Trunk": "T7 Cobalt", "Wood_Sallow_Trunk": "T10 Adamantite", "Wood_Fig_Blue_Trunk": "T10 Adamantite",
    "Plant_Crop_Wheat_Item": "T1 Copper", "Plant_Crop_Carrot_Item": "T2 Iron", "Plant_Crop_Potato_Item": "T16 Onyxium",
    "Plant_Seeds_Wheat": "T1 Copper", "Plant_Seeds_Onion_Eternal": "T16 Onyxium",
    "Skyy_Ench_Copper": "T1 Copper", "Skyy_Ench_Oak": "T1 Copper", "Skyy_Ench_Wheat": "T1 Copper", "Skyy_Ench_Potato": "T16 Onyxium",
    "Skyy_Ench_Adamantite": "T10 Adamantite", "Skyy_Ench_Sallow": "T10 Adamantite", "Skyy_Ench_Stick": "T1 Crude",
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
COUNTS = {"ore": 7, "bar": 8, "log": 34, "crop": 14, "seed": 28, "enchanted": 55 + len(ENCH_ORES), "tool": 34, "armory": 11,
          "can": 6 + 10, "harvester": 4 + 12, "forever_tool": 27, "armory_metal": 76, "zone_ore_block": 4, "zone_ore": 4, "zone_bar": 4, "alloy": 5,
          "mining_armor": 32}          # SkyyGear 0.3.23 (G2): + the forever tools of Bronze + the 8 zone metals (pickaxe / hatchet / multitool 27), cans Mithril + 9, Harvesters Cobalt / Adamantite / Mithril + 9 (TT.OWN_IDS); SkyyGear 0.3.21: the zone Mining sets (Lead .. Lumen x 4 slots, TT.OWN_IDS); tools01: enchanted 17 -> 18 (+ the Enchanted Stick); C1 (SkyyCollections 0.2.21): 18 -> 55 (37 own items on a tiered base); SkyyGear 0.3.12: its OWN watering can + Harvester ladders (TT.OWN_IDS, not in Assets.zip)
for f, n in COUNTS.items():
    ok(len(TT.ids_in(f)) == n, "family %s has %d ids, want %d" % (f, len(TT.ids_in(f)), n))
ok(set(TT.families()) == set(COUNTS), "families: %s" % TT.families())
ok(len(TT.ids_for("SkyyCollections")) == 7 + 8 + 34 + 14 + 28 + 55 + len(ENCH_ORES), "SkyyCollections owns %d" % len(TT.ids_for("SkyyCollections")))
ok(TT.ids_for("SkyyGear") == sorted(TT.ids_in("tool") + TT.ids_in("can") + TT.ids_in("harvester") + TT.ids_in("mining_armor") + TT.ids_in("forever_tool")) and TT.ids_for("SkyyArmory") == sorted(TT.ids_in("armory") + TT.ids_in("armory_metal")), "owners")
ok(sorted(TT.OWN_IDS) == sorted(TT.ids_in("can") + TT.ids_in("harvester") + TT.ids_in("mining_armor") + TT.ids_in("forever_tool")) and TT.tag_for("Tool_WaterCan_Crude") == "T1 Crude"
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
ok(all(r[2] in TT.OWNERS and 1 <= r[0] <= 16 for r in TT.ROWS.values()), "rows in range")
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
ok(sorted(TT.ids_in("enchanted") + list(TT.ENCH_UNTAGGED)) == sorted(EN.IDS), "Enchanted ids = skyyench.IDS")
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
ok(TT.RARITY_NOUNS == ("Egg",) and TT.rarity_tag("Rare", "Egg") == "Rare Egg" and TT.rarity_tag("Mythic", "Egg") == "Mythic Egg", "rarity_tag")
ok(TT.rarity_ids_for("SkyyPets") == sorted(EGG.IDS) and len(TT.RARITY_ROWS) == 30, "the 30 egg rows, owner SkyyPets")
ok(all(r[2] == "egg" and r[3] == "SkyyPets" for r in TT.RARITY_ROWS.values()), "family egg")
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
for lv, want in ((0, 1), (5, 1), (9, 1), (10, 1), (14, 1), (15, 2), (16, 2), (17, 3), (20, 4), (22, 5), (24, 6), (25, 7), (27, 7), (28, 8), (31, 9),
                 (34, 9), (35, 10), (37, 11), (39, 12), (40, 13), (44, 13), (45, 14), (49, 14), (50, 15), (60, 15)):
    ok(TT.tier_for_level(lv) == want, "tier_for_level(%d) = %d, want %d" % (lv, TT.tier_for_level(lv), want))
ok(TT.tier_for_level(40, "Weapon_Sword_Onyxium") == 16, "Onyxium id = T16")
ok(TT.level_tag(1) == "T1 Crude" and TT.level_tag(9) == "T1 Crude" and TT.level_tag(10) == "T1 Copper" and TT.level_tag(15) == "T2 Iron"
   and TT.level_tag(22) == "T5 Lead" and TT.level_tag(5, "Armor_Onyxium_Head") == "T16 Onyxium", "level_tag")
ok(TT.combat_tag("Armor_Bronze_Head", 15) == "T3 Bronze" and TT.combat_tag("Armor_Wood_Chest", 1) == "T1 Crude" and TT.combat_tag("Armor_Kweebec_Chest", 15) == "T2 Iron"
   and TT.combat_tag("Armor_Cloth_Wool_Chest", 1) == "T1 Crude", "combat_tag: metal word first, else the level band")
ok([t for _l, t in TT.LEVEL_BANDS] == list(range(15, 1, -1)) and [l for l, _t in TT.LEVEL_BANDS] == sorted([l for l, _t in TT.LEVEL_BANDS], reverse=True),
   "LEVEL_BANDS: one start per step T2..T15, highest first")

# ---- TOOL_METALS starts with SkyyGear's TOOL_TIERS words at display(internal) (Bronze: its own step T3 above Iron's internal tier; the SET
# pin's build script, text only), then the zone metals + alloys
try:
    import deploy_set
    gv = dict(deploy_set.SET)["SkyyGear"]
    gsrc = open(os.path.join(ROOT, "SkyyGear", "build_skyygear_%s.py" % gv), encoding="utf8").read()
    m = re.search(r"^TOOL_TIERS = (\[.*?\])\s*$", gsrc, re.M | re.S)
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
    vanilla = [i for i in TT.ROWS if not i.startswith("Skyy_") and i not in TT.OWN_IDS and i not in TT.WG_IDS and i not in TT.AR_IDS]   # AR_IDS: SkyyArmory's build   # OWN_IDS: SkyyGear's build; WG_IDS: SkyyWorldGen's
    missing = sorted(i for i in vanilla if i not in ids)
    ok(not missing, "not in Assets.zip: %s" % missing)
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
