"""tier_tags - THE tier table (research/Tier-Tags-Plan.md, round T0). Every build that shows a tier tag imports it (`import tier_tags as TT`)
so a renumbering is ONE edit here. Pure Python, no game files read at import (tools/test_tier_tags.py checks every id against Assets.zip).

Skyy 2026-10-15: "(make sure we add the T1 and T2 and so on tags to the flavor text of every item we give a tire. to make it easy".
Popup answers on the plan (2026-10-15): numbering "Match the tool (Recommended)" (materials take the tier of the tool that works them:
Copper ore / Oak / Wheat = T2; T1 = Crude / wood starter things only); format "T3 Iron - text (Recommended)"; own ladders "Yes, tag them
(Recommended)" (T2 Totem, T3 Loot, T2 Bench); "Leave untagged (Recommended)" for mob drops, gems and stone.

THE 15-STEP METAL LADDER (TT_VERSION 2, SkyyGear 0.3.22 round G1, research/Metals-Tools-Fortune-Spec.md 3.1; Skyy 2026-10-17 popup "tools
follow ONE tier ladder of all 15 metals in zone order - Copper, Iron, Bronze, Thorium, Lead, Dusk, Cobalt, Chromium, Azurvane, Adamantite, Slag,
Cinder, Mithril, Titanium, Lumen - each one tier above the last (so the tier tags renumber, e.g. Thorium becomes T4, Lumen T15)?" -> "Yes, full
15-step ladder (Recommended)"; spec Q1 default "both T1, Crude > Copper stays", Onyxium (parked, Zone 6) T16):
  T1 Copper (and Crude / Wood / Scrap), T2 Iron (and Steel), T3 Bronze, T4 Thorium, T5 Lead, T6 Dusk, T7 Cobalt, T8 Chromium, T9 Azurvane,
  T10 Adamantite, T11 Slag, T12 Cinder, T13 Mithril, T14 Titanium, T15 Lumen, T16 Onyxium.
Every tag keeps its WORD and gets the new number (TT_VERSION 1 = 2026-10-15: T1 Crude .. T8 Onyxium = Gear internal + 1; OLD_TO_NEW maps it).
Code keeps its 0-based internal tool tier (SkyyGear TOOL_TIERS, Shards documents, line caps: 0 = Crude .. 7 = Onyxium = GEAR_INTERNAL);
what players SEE is the ladder number: display(internal) = metal_tier(GEAR_INTERNAL[internal]). No saved data changes.

API
    tag_for(id)            -> "T1 Copper" (None = untagged)
    word(id)               -> "Copper" / "Lead" / "Crude" (the tag's word: WORDS - zone metals, Crude-tier items - else the ladder noun)
    tier(id)               -> 1 (display tier, 1-16) or None;  internal(id) -> Gear's 0-based tool tier of the tag word or None
    family(id) / owner(id) -> "ore" / "SkyyCollections" (None = not in the table)
    ids_for(owner) / ids_in(family) -> sorted ids
    shadowed(id)           -> why a lang tag is NOT seen in game today (an enabled pack mod points the item at its own Description key),
                              None = visible; the key is still written (it shows once that mod is off), never counted as a visible tag
    described(id, text)    -> "T2 Copper - <text>" (text empty / None -> "T2 Copper"); the tag is always the FIRST phrase
    display(internal_tier) -> the ladder T of Gear's internal tier (0 Crude -> 1, 1 Copper -> 1, 2 Iron -> 2, 3 Thorium -> 4 ... 7 -> 16)
    to_internal(display_tier) -> the highest Gear internal tier shown at that T (1 -> 1 Copper) or None (no vanilla tool metal there)
    tag_text(display_tier[, noun]) -> "T3 Iron";  ladder_tag(n, word) -> "T2 Totem" (own ladders: Totem, Loot, Bench, Talisman, Charm)
    metal_tier(word)       -> ladder T of a metal word (TOOL_METALS: Gear's tool words + the zone metals / alloys), None if no metal
    metal_word(word)       -> the word a tag shows for it (Crude / Wood -> Crude, Scrap -> Copper, Steel -> Iron)
    tier_for_level(lv, id) -> ladder T of a weapon / armor from its SkyyGear level band start (LEVEL_BANDS; ids with Onyxium = T16)
    level_tag(lv, id)      -> its tag: "T1 Crude" (Lv 0-9), "T1 Copper" (10-14), "T2 Iron" ... (SkyyGear's combat armor flavour tag)
    combat_tag(id, lv)     -> the combat armor flavour tag: the id's metal word first ("T3 Bronze"), else level_tag
    renumber(old_display)  -> the TT_VERSION 1 number (T1 Crude .. T8 Onyxium) -> today's (for the L1 rebuilds of baked tables)

Owners (plan section 3, one writer per key): SkyyCollections = vanilla MATERIAL keys (ores, bars, logs, crops, seeds) +
its Enchanted items; SkyyGear = vanilla tool / weapon / armor keys; SkyyArmory = its 11 vanilla staff / wand keys (Gear must skip them);
SkyyWorldGen = its OWN zone metals (round ores01, SkyyWorldGen 0.7.3, research/Zone-Ores-Alloys-Spec.md 2.5: Lead / Chromium / Slag /
Titanium ore blocks + raw ores + ingots and the Dusk / Azurvane / Cinder / Lumen alloy ingots - ids WG_IDS, not in Assets.zip).
Zone metals show their OWN word at their OWN ladder step (WORDS): "T5 Lead", "T9 Azurvane" (TT_VERSION 1 put them at the zone partner's tier,
"T4 Lead" - the 15-step ladder above replaced that).
Weapons / armor / gathering armor / rods / fish / totems / accessories / Lost Loot are tagged by their own rounds (T2 / T3) with the
rules below (tier_for_level, ladder_tag); only the families with fixed id lists live in ROWS today.
Left untagged on purpose: stone / dirt / sand, Silver / Gold / Prisma, gems, mob drops (hides + leathers too), food, tree seeds,
the Enchanted Cobblestone / Rubble.
"""

TT_VERSION = "2"
LADDER = ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder",
          "Mithril", "Titanium", "Lumen", "Onyxium")        # index = display tier - 1 (T1 .. T16); Crude shares T1 (word "Crude")
GEAR_INTERNAL = ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")   # SkyyGear's internal tool tier 0-7
OLD_LADDER = GEAR_INTERNAL      # TT_VERSION 1: the number was internal + 1 (T1 Crude, T2 Copper, T3 Iron ... T8 Onyxium)
CRUDE_WORDS = ("Crude", "Wood")    # T1 items of these words keep the word "Crude" in their tag ("T1 Crude"); every other T1 item says Copper
SEP = " - "                      # format A: "T3 Iron - text"
OWN_LADDERS = ("Totem", "Loot", "Bench", "Talisman", "Charm")      # ores01: + Charm (the Furnace Charm line, SkyyAccessories 0.5.25)
OWNERS = ("SkyyCollections", "SkyyGear", "SkyyArmory", "SkyyWorldGen")
# Hides + leathers are NOT tagged (coordinator 2026-10-15): the plan's Soft T1 ... Prismic T8 order was a PLACEHOLDER (economy.md price
# order) and Skyy picked "Leave untagged" for things the design gives no real tier - a wrong tag is worse than none.


def display(internal_tier):
    """SkyyGear's internal 0-based tool tier (code, saved documents) -> the ladder number players see"""
    assert isinstance(internal_tier, int) and 0 <= internal_tier < len(GEAR_INTERNAL), internal_tier
    return metal_tier(GEAR_INTERNAL[internal_tier])


def to_internal(display_tier):
    """the highest SkyyGear internal tier shown at this ladder number (T1 -> 1 Copper), None = no vanilla tool metal at that step"""
    assert isinstance(display_tier, int) and 1 <= display_tier <= len(LADDER), display_tier
    hit = [i for i, w in enumerate(GEAR_INTERNAL) if metal_tier(w) == display_tier]
    return hit[-1] if hit else None


def noun(display_tier):
    assert isinstance(display_tier, int) and 1 <= display_tier <= len(LADDER), display_tier
    return LADDER[display_tier - 1]


def tag_text(display_tier, word=None):
    """'T3 Iron' (word: an own-ladder noun instead of the metal)"""
    return "T%d %s" % (display_tier, word or noun(display_tier))


def ladder_tag(n, word):
    """own ladders (plan C8 / C9, Skyy 'Yes, tag them'): 'T2 Totem', 'T3 Loot', 'T2 Bench', 'T3 Talisman'"""
    assert word in OWN_LADDERS and isinstance(n, int) and n >= 1, (n, word)
    return "T%d %s" % (n, word)


# ------------------------------------------------------------------------------------------------ tool metals (SkyyGear TOOL_TIERS words first)
# The first 12 = SkyyGear TOOL_TIERS' words in its order (their ladder T; Gear's internal tier stays 0-7 for caps / saved data), then the
# zone metals + alloys (G2 / A1 make tools and weapons of them; SkyyGear 0.3.22 reads this table for the tier gate and the tier power).
TOOL_METALS = (("Crude", 1), ("Wood", 1), ("Copper", 1), ("Scrap", 1), ("Bronze", 3), ("Iron", 2), ("Steel", 2), ("Thorium", 4),
               ("Cobalt", 7), ("Adamantite", 10), ("Mithril", 13), ("Onyxium", 16),
               ("Lead", 5), ("Dusk", 6), ("Chromium", 8), ("Azurvane", 9), ("Slag", 11), ("Cinder", 12), ("Titanium", 14), ("Lumen", 15))
OLD_TO_NEW = {}


def metal_tier(word):
    for w, t in TOOL_METALS:
        if w == word:
            return t
    return None


for _i, _w in enumerate(OLD_LADDER):
    OLD_TO_NEW[_i + 1] = metal_tier(_w)
assert OLD_TO_NEW == {1: 1, 2: 1, 3: 2, 4: 4, 5: 7, 6: 10, 7: 13, 8: 16}, OLD_TO_NEW
assert [metal_tier(w) for w in LADDER] == list(range(1, len(LADDER) + 1)), "every ladder noun sits at its own step"


def renumber(old_display):
    """a TT_VERSION 1 number (T1 Crude, T2 Copper, T3 Iron ... T8 Onyxium) -> today's ladder number (for baked tables in other mods)"""
    return OLD_TO_NEW[old_display]


def metal_word(word):
    """the word a tag shows for a tool metal word: Crude / Wood -> Crude, Scrap -> Copper, Steel -> Iron, a ladder noun -> itself"""
    t = metal_tier(word)
    if t is None:
        return None
    return "Crude" if word in CRUDE_WORDS else (word if word in LADDER else noun(t))


# weapon / armor level bands (the SkyyGear level.material band STARTS of the ladder metals: Copper 10, Iron 15, Bronze 17 (spec 3.1 slot),
# Thorium 20, Lead 22, Dusk 24, Cobalt 25, Chromium 28, Azurvane 31, Adamantite 35, Slag 37, Cinder 39, Mithril 40, Titanium 45, Lumen 50);
# (lowest level, T), highest first. Java mirrors (SkyyGear GearView.tierFor, SkyyBazaar / SkyyAuctions sort) are built from this table.
LEVEL_BANDS = ((50, 15), (45, 14), (40, 13), (39, 12), (37, 11), (35, 10), (31, 9), (28, 8), (25, 7), (24, 6), (22, 5), (20, 4), (17, 3),
               (15, 2))


def tier_for_level(level, item_id=""):
    """weapon / armor band: Lv 0-14 T1, 15-16 T2, 17-19 T3, 20-21 T4 ... 45-49 T14, 50+ T15 (LEVEL_BANDS); Onyxium ids T16"""
    if "Onyxium" in (item_id or ""):
        return metal_tier("Onyxium")
    for lo, t in LEVEL_BANDS:
        if level >= lo:
            return t
    return 1


LEVEL_CRUDE = 10          # below the Copper band start a T1 weapon / armor says "Crude" (TT_VERSION 1 showed Lv 0-9 as T1 Crude)


def level_tag(level, item_id=""):
    """the tag of a weapon / armor from its level band start: 'T1 Crude' (Lv 0-9), 'T1 Copper' (10-14), 'T2 Iron', ... 'T16 Onyxium'"""
    t = tier_for_level(level, item_id)
    return tag_text(t, "Crude" if t == 1 and level < LEVEL_CRUDE else None)


def combat_tag(item_id, level):
    """a weapon / armor tag: its first metal word from word 2 on (Armor_Bronze_Head -> 'T3 Bronze', Armor_Wood_* -> 'T1 Crude'), else level_tag
    of its level band start (SkyyGear 0.3.22 critic M2: Bronze shares Iron's 15-23 band but is its own step)"""
    for w in (item_id or "").split("_")[1:]:
        if metal_tier(w):
            return tag_text(metal_tier(w), metal_word(w))
    return level_tag(level, item_id)


# ------------------------------------------------------------------------------------------------ the fixed-id families
ROWS = {}            # id -> (display tier, family, owner)
WORDS = {}           # id -> the word its tag shows instead of the ladder noun (zone metals "T5 Lead", Crude-tier items "T1 Crude"); absent = noun


def _add(item_id, t, fam, owner):
    assert item_id not in ROWS, "tier_tags: %s is in two families" % item_id
    assert 1 <= t <= len(LADDER) and owner in OWNERS, (item_id, t, owner)
    ROWS[item_id] = (t, fam, owner)


ORES = tuple((_m, metal_tier(_m)) for _m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"))  # T1 .. T16
for _m, _t in ORES:
    _add("Ore_" + _m, _t, "ore", "SkyyCollections")
for _m, _t in ORES + (("Bronze", metal_tier("Bronze")),):
    _add("Ingredient_Bar_" + _m, _t, "bar", "SkyyCollections")

# round ores01 (SkyyWorldGen 0.7.3; research/Zone-Ores-Alloys-Spec.md 2.3 / 2.5 / 3): each zone's NEW metal + its alloy, tagged with their own
# word; TT_VERSION 2: at their OWN ladder step (Lead T5, Dusk T6, Chromium T8, Azurvane T9, Slag T11, Cinder T12, Titanium T14, Lumen T15).
# Zone 1's alloy is vanilla Bronze (row above, T3). Ids end "_SkyWynn" (TerrariaToolsWeapons owns Ore_Lead* / Ingredient_Bar_Lead);
# SkyyWorldGen's build makes them.
ZONE_METALS = tuple((_m, metal_tier(_m), _h) for _m, _h in (("Lead", "Sandstone"), ("Chromium", "Shale"), ("Slag", "Volcanic"),
                                                             ("Titanium", "Basalt")))   # (word, tier, host)
ALLOYS = tuple((_m, metal_tier(_m)) for _m in ("Dusk", "Azurvane", "Cinder", "Lumen")) + \
    (("Electrum", metal_tier("Bronze")),)   # spec 8 (Skyy 2026-10-17 "add Electrum (Gold + Silver, unlocked at the Bronze furnace tier)"): T3
for _m, _t, _h in ZONE_METALS:
    for _id, _f in (("Ore_%s_%s_SkyWynn" % (_m, _h), "zone_ore_block"), ("Ore_%s_SkyWynn" % _m, "zone_ore"),
                    ("Ingredient_Bar_%s_SkyWynn" % _m, "zone_bar")):
        _add(_id, _t, _f, "SkyyWorldGen")
        WORDS[_id] = _m
for _m, _t in ALLOYS:
    _add("Ingredient_Bar_%s_SkyWynn" % _m, _t, "alloy", "SkyyWorldGen")
    WORDS["Ingredient_Bar_%s_SkyWynn" % _m] = _m
WG_IDS = frozenset(i for i, r in ROWS.items() if r[2] == "SkyyWorldGen")      # made by SkyyWorldGen's build (not in Assets.zip)

# logs = the forest ZONE tier (plan C4) at the hatchet metal that cuts them: F1 Grove Copper, F2 Autumn / Azure Iron, F3 Savanna Thorium,
# F4 Northern Cobalt, F5 Wastes Adamantite; Orchard side group Copper (TT_VERSION 2: T1 / T2 / T4 / T7 / T10)
LOGS = {
    1: ("Oak", "Birch", "Beech", "Ash", "Aspen",
        "Apple", "Amber", "Stormbark", "Windwillow", "Wisteria_Wild", "Palm", "Ice", "Sadwillow"),     # F1 Grove + Orchard (M1)
    2: ("Maple", "Azure"),                                                                              # F2
    4: ("Gumboab", "Dry", "Bottletree", "Palo"),                                                        # F3
    7: ("Redwood", "Fir", "Cedar", "Poisoned", "Spiral"),                                               # F4
    10: ("Sallow", "Burnt", "Petrified", "Bamboo", "Camphor", "Banyan", "Jungle", "Fig_Blue", "Fire", "Crystal"),   # F5
}
for _t in sorted(LOGS):
    for _w in LOGS[_t]:
        _add("Wood_%s_Trunk" % _w, _t, "log", "SkyyCollections")

# crops = the LOCKED Farmer's Workbench pairs (Gathering-Progression-Spec 2.3, P1-P7) at the tool that harvests them at normal speed
# (Gathering-Shards-Spec 7.3, newer: pair Mk = internal hoe / sickle tier k; plan C5) at that metal's ladder step (TT_VERSION 2): P1 Wheat /
# Lettuce = T1 Copper, P2 Carrot / Corn = T2 Iron, P3 T4 Thorium, P4 T7 Cobalt, P5 T10 Adamantite, P6 T13 Mithril, P7 Potato / Onion = T16
# Onyxium (Potato is the LAST pair, not an early crop). Seeds + eternal seeds = their crop
CROPS = tuple((_c, display(_k)) for _k, _cs in ((1, ("Wheat", "Lettuce")), (2, ("Carrot", "Corn")), (3, ("Cauliflower", "Turnip")),
                                                 (4, ("Pumpkin", "Aubergine")), (5, ("Tomato", "Chilli")), (6, ("Cotton", "Rice")),
                                                 (7, ("Potato", "Onion"))) for _c in _cs)
for _c, _t in CROPS:
    _add("Plant_Crop_%s_Item" % _c, _t, "crop", "SkyyCollections")
    _add("Plant_Seeds_" + _c, _t, "seed", "SkyyCollections")
    _add("Plant_Seeds_%s_Eternal" % _c, _t, "seed", "SkyyCollections")


# Enchanted materials (SkyyCollections' own items, tools/skyyench.py TABLE): the tier of the base; Cobblestone / Rubble stay untagged
ENCH_BASE = (("Copper", "Ingredient_Bar_Copper"), ("Iron", "Ingredient_Bar_Iron"), ("Thorium", "Ingredient_Bar_Thorium"),
             ("Cobalt", "Ingredient_Bar_Cobalt"), ("Adamantite", "Ingredient_Bar_Adamantite"),
             ("Oak", "Wood_Oak_Trunk"), ("Maple", "Wood_Maple_Trunk"), ("Gumboab", "Wood_Gumboab_Trunk"),
             ("Redwood", "Wood_Redwood_Trunk"), ("Sallow", "Wood_Sallow_Trunk"),
             ("Wheat", "Plant_Crop_Wheat_Item"), ("Carrot", "Plant_Crop_Carrot_Item"), ("Cauliflower", "Plant_Crop_Cauliflower_Item"),
             ("Pumpkin", "Plant_Crop_Pumpkin_Item"), ("Tomato", "Plant_Crop_Tomato_Item"), ("Cotton", "Plant_Crop_Cotton_Item"),
             ("Potato", "Plant_Crop_Potato_Item"))
ENCH_UNTAGGED = ("Skyy_Ench_Cobblestone", "Skyy_Ench_Rubble")
for _k, _b in ENCH_BASE:
    _add("Skyy_Ench_" + _k, ROWS[_b][0], "enchanted", "SkyyCollections")
# round C1 (SkyyCollections 0.2.21, Skyy 2026-10-16 "Own items now"): every collection's own Enchanted item (tools/skyyench.py TABLE_C1) takes
# the tier of its base when the base has one here (logs, crops, the Mithril ingot, wheat seeds); stone / sand / fruit / meat / mob drops /
# Silver / Gold stay untagged (Skyy "Leave untagged" for things the design gives no tier)
import skyyench as _EN        # pure Python table, no game files at import
ENCH_C1 = tuple((_t[0], _t[2]) for _t in _EN.TABLE_C1 if _t[1] == "I" and _t[2] in ROWS)
for _k, _b in ENCH_C1:
    _add("Skyy_Ench_" + _k, ROWS[_b][0], "enchanted", "SkyyCollections")
    if _b in WORDS:                      # ores01: Enchanted Lead Ingot = "T5 Lead" like its base
        WORDS["Skyy_Ench_" + _k] = WORDS[_b]
ENCH_UNTAGGED = ENCH_UNTAGGED + tuple("Skyy_Ench_" + _t[0] for _t in _EN.TABLE_C1 if (_t[0], _t[2]) not in ENCH_C1)
# round tools01 (Skyy 2026-10-16 "make enchanted sticks too"): the Enchanted Stick. Its base (Ingredient_Stick) has no row (sticks are a wood
# starter material: no vanilla Description key to tag), so its tier is set here: T1 Crude (sticks = the Crude sickle's / bare hands' material)
ENCH_OWN = {"Skyy_Ench_Stick": 1}
for _e, _t in sorted(ENCH_OWN.items()):
    _add(_e, _t, "enchanted", "SkyyCollections")
    WORDS[_e] = "Crude"

# vanilla tools (plan 1.2: 32 + 2 hammers) -> SkyyGear (round T2); tier = the metal word after the family (its ladder T; word metal_word)
TOOLS = ("Tool_Hammer_Crude", "Tool_Hammer_Iron",
         "Tool_Hatchet_Adamantite", "Tool_Hatchet_Cobalt", "Tool_Hatchet_Copper", "Tool_Hatchet_Crude", "Tool_Hatchet_Iron",
         "Tool_Hatchet_Mithril", "Tool_Hatchet_Onyxium", "Tool_Hatchet_Thorium", "Tool_Hatchet_Wood",
         "Tool_Hoe_Copper", "Tool_Hoe_Crude", "Tool_Hoe_Iron", "Tool_Hoe_Thorium",
         "Tool_Pickaxe_Adamantite", "Tool_Pickaxe_Cobalt", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Crude", "Tool_Pickaxe_Iron",
         "Tool_Pickaxe_Mithril", "Tool_Pickaxe_Onyxium", "Tool_Pickaxe_Scrap", "Tool_Pickaxe_Thorium", "Tool_Pickaxe_Wood",
         "Tool_Shovel_Cobalt", "Tool_Shovel_Copper", "Tool_Shovel_Crude", "Tool_Shovel_Iron", "Tool_Shovel_Thorium",
         "Tool_Sickle_Copper", "Tool_Sickle_Crude", "Tool_Sickle_Iron", "Tool_Sickle_Steel_Rusty")
for _id in TOOLS:
    _add(_id, metal_tier(_id.split("_")[2]), "tool", "SkyyGear")
    if metal_word(_id.split("_")[2]) != noun(metal_tier(_id.split("_")[2])):
        WORDS[_id] = metal_word(_id.split("_")[2])          # Crude / Wood -> "T1 Crude" (Scrap / Steel show the ladder noun)

# SkyyArmory's 11 vanilla staff / wand keys (plan section 3): Armory keeps them and prefixes the tag itself; SkyyGear's generator skips them
ARMORY_VANILLA = tuple("Weapon_Staff_" + m for m in ("Wood", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")) + \
    ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal")
for _id in ARMORY_VANILLA:
    _w = _id.split("_")[2]
    _add(_id, metal_tier(_w) or {"Tribal": tier_for_level(15)}[_w], "armory", "SkyyArmory")   # Tribal = SkyyGear's Lv 15 row -> T2 Iron
    if _w in CRUDE_WORDS:
        WORDS[_id] = "Crude"

# SkyyGear's OWN tiered items (round gear0312 = SkyyGear 0.3.12; Skyy 2026-10-15 "lets add a T1 crude watering can, (made of wood.) upgrades
# to a T2 copper T3 iron and so no" + the Harvester = hoe + sickle): the lifelong watering can ladder (Crude .. Adamantite like the pickaxe -
# Mithril / Onyxium wait for their Enchanted items) and the Harvester ladder (Crude .. Thorium like the hoe). These ids are made by SkyyGear's
# build (not in Assets.zip): OWN_IDS. Tier = the metal word's ladder T (the Crude ones say "T1 Crude").
CAN_TIERS = ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite")
HARVESTER_TIERS = ("Crude", "Copper", "Iron", "Thorium")
for _w in CAN_TIERS:
    _add("Tool_WaterCan_" + _w, metal_tier(_w), "can", "SkyyGear")
for _w in HARVESTER_TIERS:
    _add("Tool_Sickle_Harvester_" + _w, metal_tier(_w), "harvester", "SkyyGear")
for _id in ("Tool_WaterCan_Crude", "Tool_Sickle_Harvester_Crude"):
    WORDS[_id] = "Crude"
# SkyyGear 0.3.21 (LOCAL-RESUME queue 1, Skyy 2026-10-17 Quirk's approved sets): the zone MINING ARMOR sets - each zone's metal + alloy
# retexture that zone's vanilla base armor; tier + word = their ingot's (ZONE_METALS / ALLOYS above: "T5 Lead", "T9 Azurvane"). Made by
# SkyyGear's build (not in Assets.zip). Ids end in the slot word (SkyyGear reads the slot from the last id part); Armor_Lead_* is
# TerrariaToolsWeapons' - hence Armor_Mining_<Metal>_<Slot>.
MINING_ARMOR_SLOTS = ("Head", "Chest", "Hands", "Legs")
MINING_ARMOR = tuple((_m, metal_tier(_m)) for _m in ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"))
assert all(dict([(_m, _t) for _m, _t, _h in ZONE_METALS] + list(ALLOYS))[_m] == _t for _m, _t in MINING_ARMOR)
for _m, _t in MINING_ARMOR:
    for _sl in MINING_ARMOR_SLOTS:
        _add("Armor_Mining_%s_%s" % (_m, _sl), _t, "mining_armor", "SkyyGear")
        WORDS["Armor_Mining_%s_%s" % (_m, _sl)] = _m
OWN_IDS = frozenset(["Tool_WaterCan_" + _w for _w in CAN_TIERS] + ["Tool_Sickle_Harvester_" + _w for _w in HARVESTER_TIERS]
                    + ["Armor_Mining_%s_%s" % (_m, _sl) for _m, _t in MINING_ARMOR for _sl in MINING_ARMOR_SLOTS])
# SkyyGear 0.3.23 (round G2, research/Metals-Tools-Fortune-Spec.md 3.3; Skyy 2026-10-17 "Yes, full 15-step ladder (Recommended)" + "Yes, all
# defaults (Recommended)"): the forever tools of the metals the vanilla tool ladder lacks - pickaxe / hatchet / multitool (family forever_tool)
# of Bronze + the 8 zone metals and alloys, the Harvester from Cobalt up and the watering can from Mithril up. Tier + word = the metal's own
# ladder step ("T3 Bronze", "T5 Lead"). Ids of a non-vanilla tool metal end "_SkyWynn" (TerrariaToolsWeapons owns Tool_Pickaxe_Lead; SkyyGear's
# level.material.<Metal>_SkyWynn bands match only these). Made by SkyyGear's build (OWN_IDS, not in Assets.zip). Rows only: no number moves.
G2_METALS = ("Bronze", "Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")
G2_FOREVER = tuple(_p % _g for _p in ("Tool_Pickaxe_%s_SkyWynn", "Tool_Hatchet_%s_SkyWynn", "Tool_Hatchet_Pickaxe_Multitool_%s_SkyWynn")
                   for _g in G2_METALS)
G2_HARVESTERS = tuple("Tool_Sickle_Harvester_" + _g for _g in ("Cobalt", "Adamantite", "Mithril")) + \
    tuple("Tool_Sickle_Harvester_%s_SkyWynn" % _g for _g in G2_METALS)
G2_CANS = ("Tool_WaterCan_Mithril",) + tuple("Tool_WaterCan_%s_SkyWynn" % _g for _g in G2_METALS)
for _fam_g, _ids_g in (("forever_tool", G2_FOREVER), ("harvester", G2_HARVESTERS), ("can", G2_CANS)):
    for _id_g in _ids_g:
        _w_g = _id_g.split("_")[-2] if _id_g.endswith("_SkyWynn") else _id_g.split("_")[-1]
        _add(_id_g, metal_tier(_w_g), _fam_g, "SkyyGear")
OWN_IDS = OWN_IDS | frozenset(G2_FOREVER + G2_HARVESTERS + G2_CANS)
# SkyyArmory 0.1.33 (round A1, spec 4.1 Group A; rows added by the SkyyGear 0.3.23 builder at the main session's request 2026-10-18): the 9
# metal families in the 8 zone metals / alloys (Weapon_<Family>_<M>_SkyWynn; the Monk gauntlets Weapon_Fist_Gauntlets_*, the Priest soul cage
# Weapon_Wand_SoulCage_*) + the Thorium / Cobalt / Adamantite / Mithril crossbows the Armory ladder lacked (Weapon_Crossbow_<M>_Wynn). Owner
# SkyyArmory (its lang writes the "T5 Lead - " tags itself; one writer per key). Made by SkyyArmory's build (AR_IDS, not in Assets.zip).
A1_FAMILIES = ("Wand", "Staff", "Spellbook", "Kunai", "Bo", "Fist_Gauntlets", "Wand_SoulCage", "GreatShield", "Crossbow")
A1_WEAPONS = tuple("Weapon_%s_%s_SkyWynn" % (_f, _g) for _f in A1_FAMILIES for _g in G2_METALS[1:]) + \
    tuple("Weapon_Crossbow_%s_Wynn" % _g for _g in ("Thorium", "Cobalt", "Adamantite", "Mithril"))
for _id_g in A1_WEAPONS:
    _w_g = _id_g.split("_")[-2]
    _add(_id_g, metal_tier(_w_g), "armory_metal", "SkyyArmory")
AR_IDS = frozenset(A1_WEAPONS)


# ------------------------------------------------------------------------------------------------ rarity-tagged items (no T-number)
# Pet eggs (research/Pet-Eggs-Spec.md 1.1, round pets040 = SkyyPets 0.4.0): eggs are tiered by RARITY, so their tag is the rarity + noun as
# the first phrase - "Rare Egg - Right-click to hatch ..." (a "T3 Egg" would read as Iron). Kept apart from ROWS (the metal ladder): tag_for()
# answers both, families() / ids_in() / ids_for() stay the metal ladder's; rarity_ids_for(owner) lists these. Ids from tools/skyyeggs.py.
RARITY_LADDER = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic")
RARITY_NOUNS = ("Egg",)
RARITY_ROWS = {}     # id -> (rarity, noun, family, owner)


def rarity_tag(rarity, noun_word):
    """'Rare Egg' (rarity = a RARITY_LADDER word, noun_word = a RARITY_NOUNS word)"""
    assert rarity in RARITY_LADDER and noun_word in RARITY_NOUNS, (rarity, noun_word)
    return "%s %s" % (rarity, noun_word)


def _add_rarity(item_id, rarity, noun_word, fam, owner_mod):
    assert item_id not in ROWS and item_id not in RARITY_ROWS, "tier_tags: %s is in two tables" % item_id
    rarity_tag(rarity, noun_word)
    RARITY_ROWS[item_id] = (rarity, noun_word, fam, owner_mod)


import skyyeggs as _EGG        # pure Python table, no game files
assert _EGG.RARITIES == RARITY_LADDER
for _c in _EGG.CATEGORIES:
    for _r in _EGG.RARITIES:
        _add_rarity(_EGG.egg_id(_c, _r), _r, "Egg", "egg", "SkyyPets")


def rarity_tag_for(item_id):
    r = RARITY_ROWS.get(item_id)
    return None if r is None else rarity_tag(r[0], r[1])


def rarity_ids_for(owner_mod):
    return sorted(i for i, r in RARITY_ROWS.items() if r[3] == owner_mod)


# ------------------------------------------------------------------------------------------------ lookups
def tier(item_id):
    r = ROWS.get(item_id)
    return r[0] if r else None


def internal(item_id):
    """SkyyGear's internal tool tier of the tag word (Crude 0 .. Onyxium 7), None = untagged or a word Gear has no internal tier for"""
    w = word(item_id)
    return GEAR_INTERNAL.index(w) if w in GEAR_INTERNAL else None


def family(item_id):
    r = ROWS.get(item_id)
    return r[1] if r else None


def owner(item_id):
    r = ROWS.get(item_id)
    return r[2] if r else None


def word(item_id):
    """the word the tag shows: WORDS (zone metals, Crude-tier items) else the ladder noun of its tier (None = untagged)"""
    t = tier(item_id)
    return None if t is None else WORDS.get(item_id) or noun(t)


def tag_for(item_id):
    t = tier(item_id)
    return rarity_tag_for(item_id) if t is None else tag_text(t, WORDS.get(item_id))


def described(item_id, text=None):
    """the flavour text with the tag as its first phrase: 'T1 Copper - <text>', or just 'T1 Copper' when text is empty"""
    tg = tag_for(item_id)
    assert tg, "tier_tags: %s has no tier" % item_id
    text = (text or "").strip()
    return tg + SEP + text if text else tg


def ids_for(owner_mod):
    return sorted(i for i, r in ROWS.items() if r[2] == owner_mod)


def ids_in(fam):
    return sorted(i for i, r in ROWS.items() if r[1] == fam)


# Lang tags an enabled pack mod hides today (the key is still written; it works when that mod is off). The fix is plan path (c): the
# tag comes from SkyyGear's tooltip code by id later. DynamicSeasons 7.0.2 (BlueOrbit:DynamicSeasons, PACK_THIRD_PARTY) ships its own
# item JSON for all 28 Plant_Seeds_<Crop>[_Eternal] with Description = server.items.Plant_Seeds_<Crop>[_Eternal]_Seasonal.description
# (coordinator review 2026-10-15; SkyyCollections 0.2.18's build lists every such override as a WARN).
SHADOWED_FAMILIES = {"seed": "shadowed by DynamicSeasons -> SkyyGear tooltip later (plan path c)"}


def shadowed(item_id):
    return SHADOWED_FAMILIES.get(family(item_id))


def visible_ids_for(owner_mod):
    """the ids of owner_mod whose lang tag shows in game today (ids_for minus shadowed)"""
    return [i for i in ids_for(owner_mod) if not shadowed(i)]


def families():
    return sorted(set(r[1] for r in ROWS.values()))


del _m, _t, _w, _c, _k, _b, _id, _h, _f, _i, _e
