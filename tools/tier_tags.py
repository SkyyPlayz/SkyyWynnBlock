"""tier_tags - THE tier table (research/Tier-Tags-Plan.md, round T0). Every build that shows a tier tag imports it (`import tier_tags as TT`)
so a renumbering is ONE edit here. Pure Python, no game files read at import (tools/test_tier_tags.py checks every id against Assets.zip).

Skyy 2026-10-15: "(make sure we add the T1 and T2 and so on tags to the flavor text of every item we give a tire. to make it easy".
Popup answers on the plan (2026-10-15): numbering "Match the tool (Recommended)" (materials take the tier of the tool that works them:
Copper ore / Oak / Wheat = T2; T1 = Crude / wood starter things only); format "T3 Iron - text (Recommended)"; own ladders "Yes, tag them
(Recommended)" (T2 Totem, T3 Loot, T2 Bench); "Leave untagged (Recommended)" for mob drops, gems and stone.

ONE ladder: T1 Crude, T2 Copper, T3 Iron, T4 Thorium, T5 Cobalt, T6 Adamantite, T7 Mithril, T8 Onyxium. Code keeps its 0-based internal tier
(GearTool TOOL_TIERS, Shards documents: 0 = Crude); what players SEE is display = internal + 1 (plan C1). No saved data changes.

API
    tag_for(id)            -> "T2 Copper" (None = untagged)
    tier(id)               -> 2 (display tier, 1-8) or None;  internal(id) -> 1 (0-based) or None
    family(id) / owner(id) -> "ore" / "SkyyCollections" (None = not in the table)
    ids_for(owner) / ids_in(family) -> sorted ids
    shadowed(id)           -> why a lang tag is NOT seen in game today (an enabled pack mod points the item at its own Description key),
                              None = visible; the key is still written (it shows once that mod is off), never counted as a visible tag
    described(id, text)    -> "T2 Copper - <text>" (text empty / None -> "T2 Copper"); the tag is always the FIRST phrase
    display(internal_tier) -> internal + 1;  to_internal(display_tier) -> display - 1
    tag_text(display_tier[, noun]) -> "T3 Iron";  ladder_tag(n, word) -> "T2 Totem" (own ladders: Totem, Loot, Bench, Talisman)
    metal_tier(word)       -> display tier of a tool metal word (Gear TOOL_TIERS + 1), None if not a ladder metal
    tier_for_level(lv, id) -> display tier of a weapon / armor from its SkyyGear level band (plan 1.2; ids with Onyxium = T8)

Owners (plan section 3, one writer per key): SkyyCollections = vanilla MATERIAL keys (ores, bars, logs, crops, seeds) +
its Enchanted items; SkyyGear = vanilla tool / weapon / armor keys; SkyyArmory = its 11 vanilla staff / wand keys (Gear must skip them).
Weapons / armor / gathering armor / rods / fish / totems / accessories / Lost Loot are tagged by their own rounds (T2 / T3) with the
rules below (tier_for_level, ladder_tag); only the families with fixed id lists live in ROWS today.
Left untagged on purpose: stone / dirt / sand, Silver / Gold / Prisma, gems, mob drops (hides + leathers too), food, tree seeds,
the Enchanted Cobblestone / Rubble.
"""

TT_VERSION = "1"
LADDER = ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")   # index = internal tier (0-7)
SEP = " - "                      # format A: "T3 Iron - text"
OWN_LADDERS = ("Totem", "Loot", "Bench", "Talisman")
OWNERS = ("SkyyCollections", "SkyyGear", "SkyyArmory")
# Hides + leathers are NOT tagged (coordinator 2026-10-15): the plan's Soft T1 ... Prismic T8 order was a PLACEHOLDER (economy.md price
# order) and Skyy picked "Leave untagged" for things the design gives no real tier - a wrong tag is worse than none.


def display(internal_tier):
    """internal 0-based tier (code, saved documents) -> the number players see"""
    assert isinstance(internal_tier, int) and 0 <= internal_tier < len(LADDER), internal_tier
    return internal_tier + 1


def to_internal(display_tier):
    assert isinstance(display_tier, int) and 1 <= display_tier <= len(LADDER), display_tier
    return display_tier - 1


def noun(display_tier):
    return LADDER[to_internal(display_tier)]


def tag_text(display_tier, word=None):
    """'T3 Iron' (word: an own-ladder noun instead of the metal)"""
    return "T%d %s" % (display_tier, word or noun(display_tier))


def ladder_tag(n, word):
    """own ladders (plan C8 / C9, Skyy 'Yes, tag them'): 'T2 Totem', 'T3 Loot', 'T2 Bench', 'T3 Talisman'"""
    assert word in OWN_LADDERS and isinstance(n, int) and n >= 1, (n, word)
    return "T%d %s" % (n, word)


# ------------------------------------------------------------------------------------------------ tool metals (= SkyyGear TOOL_TIERS + 1)
TOOL_METALS = (("Crude", 1), ("Wood", 1), ("Copper", 2), ("Scrap", 2), ("Bronze", 3), ("Iron", 3), ("Steel", 3), ("Thorium", 4),
               ("Cobalt", 5), ("Adamantite", 6), ("Mithril", 7), ("Onyxium", 8))


def metal_tier(word):
    for w, t in TOOL_METALS:
        if w == word:
            return t
    return None


def tier_for_level(level, item_id=""):
    """weapon / armor band (plan 1.2): Lv 0-9 T1, 10-14 T2, 15-19 T3, 20-24 T4, 25-34 T5, 35-39 T6, 40+ T7; Onyxium ids T8"""
    if "Onyxium" in (item_id or ""):
        return 8
    for lo, t in ((40, 7), (35, 6), (25, 5), (20, 4), (15, 3), (10, 2)):
        if level >= lo:
            return t
    return 1


# ------------------------------------------------------------------------------------------------ the fixed-id families
ROWS = {}            # id -> (display tier, family, owner)


def _add(item_id, t, fam, owner):
    assert item_id not in ROWS, "tier_tags: %s is in two families" % item_id
    assert 1 <= t <= len(LADDER) and owner in OWNERS, (item_id, t, owner)
    ROWS[item_id] = (t, fam, owner)


ORES = (("Copper", 2), ("Iron", 3), ("Thorium", 4), ("Cobalt", 5), ("Adamantite", 6), ("Mithril", 7), ("Onyxium", 8))   # plan 1.2 (M1-M7)
for _m, _t in ORES:
    _add("Ore_" + _m, _t, "ore", "SkyyCollections")
for _m, _t in ORES + (("Bronze", 3),):
    _add("Ingredient_Bar_" + _m, _t, "bar", "SkyyCollections")

# logs = the forest ZONE tier (plan C4): F1 Grove T2, F2 Autumn / Azure T3, F3 Savanna T4, F4 Northern T5, F5 Wastes T6; Orchard side group T2
LOGS = {
    2: ("Oak", "Birch", "Beech", "Ash", "Aspen",
        "Apple", "Amber", "Stormbark", "Windwillow", "Wisteria_Wild", "Palm", "Ice", "Sadwillow"),     # F1 Grove + Orchard (M1)
    3: ("Maple", "Azure"),                                                                              # F2
    4: ("Gumboab", "Dry", "Bottletree", "Palo"),                                                        # F3
    5: ("Redwood", "Fir", "Cedar", "Poisoned", "Spiral"),                                               # F4
    6: ("Sallow", "Burnt", "Petrified", "Bamboo", "Camphor", "Banyan", "Jungle", "Fig_Blue", "Fire", "Crystal"),   # F5
}
for _t in sorted(LOGS):
    for _w in LOGS[_t]:
        _add("Wood_%s_Trunk" % _w, _t, "log", "SkyyCollections")

# crops = the LOCKED Farmer's Workbench pairs (Gathering-Progression-Spec 2.3, P1-P7) at the tool that harvests them at normal speed
# (Gathering-Shards-Spec 7.3, newer: pair Mk = internal hoe / sickle tier k = display k+1; plan C5): P1 Wheat / Lettuce = T2 Copper,
# P2 Carrot / Corn = T3 Iron ... P7 Potato / Onion = T8 Onyxium (Potato is the LAST pair, not an early crop). Seeds + eternal seeds = their crop
CROPS = (("Wheat", 2), ("Lettuce", 2), ("Carrot", 3), ("Corn", 3), ("Cauliflower", 4), ("Turnip", 4), ("Pumpkin", 5), ("Aubergine", 5),
         ("Tomato", 6), ("Chilli", 6), ("Cotton", 7), ("Rice", 7), ("Potato", 8), ("Onion", 8))
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

# vanilla tools (plan 1.2: 32 + 2 hammers) -> SkyyGear (round T2); tier = the metal word after the family (Gear TOOL_TIERS + 1)
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

# SkyyArmory's 11 vanilla staff / wand keys (plan section 3): Armory keeps them and prefixes the tag itself; SkyyGear's generator skips them
ARMORY_VANILLA = tuple("Weapon_Staff_" + m for m in ("Wood", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")) + \
    ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal")
for _id in ARMORY_VANILLA:
    _w = _id.split("_")[2]
    _add(_id, metal_tier(_w) or {"Tribal": 3}[_w], "armory", "SkyyArmory")   # Tribal = SkyyGear's Lv 15 row -> T3 (plan 1.2 band)

# SkyyGear's OWN tiered items (round gear0312 = SkyyGear 0.3.12; Skyy 2026-10-15 "lets add a T1 crude watering can, (made of wood.) upgrades
# to a T2 copper T3 iron and so no" + the Harvester = hoe + sickle): the lifelong watering can ladder (Crude .. Adamantite like the pickaxe -
# Mithril / Onyxium wait for their Enchanted items) and the Harvester ladder (Crude .. Thorium like the hoe). These ids are made by SkyyGear's
# build (not in Assets.zip): OWN_IDS. Tier = the metal word (Gear TOOL_TIERS + 1).
CAN_TIERS = ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite")
HARVESTER_TIERS = ("Crude", "Copper", "Iron", "Thorium")
for _w in CAN_TIERS:
    _add("Tool_WaterCan_" + _w, metal_tier(_w), "can", "SkyyGear")
for _w in HARVESTER_TIERS:
    _add("Tool_Sickle_Harvester_" + _w, metal_tier(_w), "harvester", "SkyyGear")
OWN_IDS = frozenset(["Tool_WaterCan_" + _w for _w in CAN_TIERS] + ["Tool_Sickle_Harvester_" + _w for _w in HARVESTER_TIERS])


# ------------------------------------------------------------------------------------------------ lookups
def tier(item_id):
    r = ROWS.get(item_id)
    return r[0] if r else None


def internal(item_id):
    t = tier(item_id)
    return None if t is None else to_internal(t)


def family(item_id):
    r = ROWS.get(item_id)
    return r[1] if r else None


def owner(item_id):
    r = ROWS.get(item_id)
    return r[2] if r else None


def tag_for(item_id):
    t = tier(item_id)
    return None if t is None else tag_text(t)


def described(item_id, text=None):
    """the flavour text with the tag as its first phrase: 'T2 Copper - <text>', or just 'T2 Copper' when text is empty"""
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


del _m, _t, _w, _c, _k, _b, _id
