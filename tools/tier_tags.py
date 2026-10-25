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

20 LEVELS PER ZONE (TT_VERSION 3, SkyyGear 0.3.29 round level-bands, research/Level-Bands-20-Spec.md 1 / 5 / 6; Skyy 2026-10-18
docs/answered/gear.md "im changing it so we have 20 levels per zone. so bronze gear would be like 15-23 thorium would start at 20" + on the
table "perfect! make sure all the gear follows that. tools, weapons, armor. ... (make sure the Tiers listed in the items flavor text get updated
too, to match the new order.)" + "we have 15 tiers of mining armor sets. we need to update foraging, and farming, to match"):
  METAL_BANDS = THE level band of every metal (min, cap) - tools, weapons, combat armor, Mining sets, gathering armor by T, Untiered by zone.
  Zone z starts at 20 x (z - 1) (Zone 1 at Lv 1); its three steps start at base, base + 8, base + 15 (Copper 1-8, Iron 8-15, Bronze 15-23,
  Thorium 20-28 ... Lumen 95-103, Onyxium 100-108). ZONE_TOPS = the mob zone tops 20 / 40 / 60 / 80 / 100 (was 20 / 30 / 45 / 60 / 75).
  LEVEL_BANDS (start -> T) = METAL_BANDS' ladder starts (Lv 1-7 T1, 8-14 T2, 15-19 T3, 20-27 T4 ... 95+ T15); LEVEL_CRUDE 10 -> 5.
  The ladder NUMBERS of metals do not change (T1 Copper .. T15 Lumen, T16 Onyxium); the GATHERING ladders do: 15 tree tiers (LOGS: 3 per zone,
  spec 5 table), 15 crop tiers (CROPS + the 15th crop Mushroom, planted from SPORES - Skyy "make sure they use spores, not seeds"), and the
  Foraging / Farming armor ladders at T1 .. T15 (FORAGING_ARMOR / FARMING_ARMOR; Fishing keeps its 5 sets at T1 / T2 / T4 / T7 / T10).
  The TT_VERSION 2 tables stay for proofs and one-time migrations: LEVEL_BANDS_V2, LEVEL_CRUDE_V2, METAL_BANDS_V2, LOG_TIERS_V2, CROP_TIERS_V2.
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
    level_tag(lv, id)      -> its tag: "T1 Crude" (Lv 0-4), "T1 Copper" (5-7), "T2 Iron" (8-14) ... (SkyyGear's combat armor flavour tag)
    band(metal)            -> METAL_BANDS[metal] = (min, cap) (Crude / Wood / Armor_Copper = Copper's 1-8; None = no metal)
    zone_of_level(lv)      -> the zone 1-5 of a mob / chest level (ZONE_TOPS: <= 20 Zone 1, <= 40 Zone 2, <= 60 Zone 3, <= 80 Zone 4, else 5)
    remap_family_start(s)  -> a TT_VERSION 2 non-metal family band start -> today's (spec 1.1: the old -> new metal anchors, straight lines)
    spore_name(id)         -> "Mushroom Spores" / "Eternal Mushroom Spores" for the spore ids (None = not a spore item)
    combat_tag(id, lv)     -> the combat armor flavour tag: the id's metal word first ("T3 Bronze"), else level_tag
    renumber(old_display)  -> the TT_VERSION 1 number (T1 Crude .. T8 Onyxium) -> today's (for the L1 rebuilds of baked tables)

Owners (plan section 3, one writer per key): SkyyCollections = vanilla MATERIAL keys (ores, bars, logs, crops, seeds) +
its Enchanted items; SkyyGear = vanilla tool / weapon / armor keys; SkyyArmory = its 11 vanilla staff / wand keys (Gear must skip them);
SkyyWorldGen = its OWN zone metals (round ores01, SkyyWorldGen 0.7.3, research/Zone-Ores-Alloys-Spec.md 2.5: Lead / Chromium / Slag /
Titanium ore blocks + raw ores + ingots and the Dusk / Azurvane / Cinder / Lumen alloy ingots - ids WG_IDS, not in Assets.zip).
Zone metals show their OWN word at their OWN ladder step (WORDS): "T5 Lead", "T9 Azurvane" (TT_VERSION 1 put them at the zone partner's tier,
"T4 Lead" - the 15-step ladder above replaced that).
SkyyFishing = its own rods, reels and fish (round fish2, SkyyFishing 0.2.0: ids FI_IDS, not in Assets.zip; fish use the own-ladder word
"Fish", rods / reels T5 / T6 show Chromium / Azurvane on the Adamantite / Mithril ids).
Weapons / armor / gathering armor / totems / accessories / Lost Loot are tagged by their own rounds (T2 / T3) with the
rules below (tier_for_level, ladder_tag); only the families with fixed id lists live in ROWS today.
Left untagged on purpose: stone / dirt / sand, Silver / Gold / Prisma, gems, mob drops (hides + leathers too), food, tree seeds,
the Enchanted Cobblestone / Rubble.
"""

TT_VERSION = "3"          # 3 = 20 levels per zone + the 15-step gathering ladders (SkyyGear 0.3.29); 2 = the 15-step metal ladder (0.3.22)
LADDER = ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder",
          "Mithril", "Titanium", "Lumen", "Onyxium")        # index = display tier - 1 (T1 .. T16); Crude shares T1 (word "Crude")
GEAR_INTERNAL = ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")   # SkyyGear's internal tool tier 0-7
OLD_LADDER = GEAR_INTERNAL      # TT_VERSION 1: the number was internal + 1 (T1 Crude, T2 Copper, T3 Iron ... T8 Onyxium)
CRUDE_WORDS = ("Crude", "Wood")    # T1 items of these words keep the word "Crude" in their tag ("T1 Crude"); every other T1 item says Copper
SEP = " - "                      # format A: "T3 Iron - text"
OWN_LADDERS = ("Totem", "Loot", "Bench", "Talisman", "Charm", "Fish")      # ores01: + Charm (the Furnace Charm line, SkyyAccessories 0.5.25); fish2: + Fish (SkyyFishing 0.2.0)
OWNERS = ("SkyyCollections", "SkyyGear", "SkyyArmory", "SkyyWorldGen", "SkyyFishing")          # fish2: + SkyyFishing (its rods, reels and fish)
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


# ------------------------------------------------------------------------------------------------ THE level bands (TT_VERSION 3)
# Skyy 2026-10-18 (approved table, research/Level-Bands-20-Spec.md 1): 20 levels per zone; zone z's base = 20 x (z - 1) (Zone 1: Lv 1); its 3 steps
# start at base, base + 8, base + 15 and each ends where the next step starts (the alloy runs 3 levels into the next zone; the last two = the
# same pattern past 100, Q2 default). ONE band per metal everywhere: tools, weapons, combat armor, the Mining sets, gathering armor (by T), the
# Untiered rows (the zone's alloy). Crude / Wood / Armor_Copper share Copper's band. Every build imports THIS table (Gear, Armory, Mobs, Bazaar,
# Auctions) - the next re-band is one edit here.
ZONE_TOPS = (20, 40, 60, 80, 100)          # the mob zone tops (TT_VERSION 2 / SkyyMobs 0.1.10: 20, 30, 45, 60, 75)
ZONE_TOPS_V2 = (20, 30, 45, 60, 75)
ZONE_STEPS = (0, 8, 15)                    # a zone's three steps start at base + these


def _zone_base(z):
    return 20 * (z - 1)


METAL_BANDS = {}
for _i, _w in enumerate(LADDER):
    _z, _s = _i // 3 + 1, _i % 3
    _lo = max(1, _zone_base(_z) + ZONE_STEPS[_s])          # Zone 1 starts at Lv 1
    _hi = (_zone_base(_z) + ZONE_STEPS[_s + 1]) if _s < 2 else (_zone_base(_z + 1) + 3)
    METAL_BANDS[_w] = (_lo, _hi)
for _w in ("Crude", "Wood", "Armor_Copper"):
    METAL_BANDS[_w] = METAL_BANDS["Copper"]
assert [METAL_BANDS[_w] for _w in LADDER] == [(1, 8), (8, 15), (15, 23), (20, 28), (28, 35), (35, 43), (40, 48), (48, 55), (55, 63), (60, 68),
                                               (68, 75), (75, 83), (80, 88), (88, 95), (95, 103), (100, 108)], "Skyy's approved band table"
# TT_VERSION 2 (SkyyGear 0.3.22 - 0.3.28 level.material defaults; Armor_Copper 1-18, Crude / Wood 1-13) - kept for proofs + migrations
METAL_BANDS_V2 = {"Crude": (1, 13), "Wood": (1, 13), "Copper": (10, 18), "Armor_Copper": (1, 18), "Iron": (15, 23), "Bronze": (15, 23),
                  "Thorium": (20, 28), "Lead": (22, 30), "Dusk": (24, 32), "Cobalt": (25, 38), "Chromium": (28, 40), "Azurvane": (31, 41),
                  "Adamantite": (35, 43), "Slag": (37, 45), "Cinder": (39, 47), "Mithril": (40, 49), "Titanium": (45, 55), "Lumen": (50, 60),
                  "Onyxium": (40, 49)}
assert set(METAL_BANDS_V2) == set(METAL_BANDS)


def band(metal):
    """(min, cap) of a metal word (METAL_BANDS), None = no metal"""
    return METAL_BANDS.get(metal)


def zone_of_level(level):
    """the zone 1-5 of a mob / chest level (ZONE_TOPS); above the last top = 5"""
    for _z, _t in enumerate(ZONE_TOPS[:-1]):
        if level <= _t:
            return _z + 1
    return len(ZONE_TOPS)


# spec 1.1: a NON-metal family band start (cloth, leather, Stone, Doomed, Prisma ...) maps through the old -> new metal anchors (straight lines,
# rounded half up) so every family keeps the T it shows; width stays SkyyGear level.bandWidth 8
FAMILY_ANCHORS = ((1, 1), (15, 8), (20, 20), (25, 40), (35, 60), (40, 80), (49, 100))


def remap_family_start(s):
    """a TT_VERSION 2 family band start (1-49) -> today's start"""
    for (_a, _b), (_c, _d) in zip(FAMILY_ANCHORS, FAMILY_ANCHORS[1:]):
        if _a <= s <= _c:
            return int(_b + (s - _a) * float(_d - _b) / (_c - _a) + 0.5)
    raise AssertionError("remap_family_start: %r outside 1-49" % s)


# weapon / armor level bands = the band STARTS of the ladder metals (Iron 8, Bronze 15, Thorium 20, Lead 28, Dusk 35, Cobalt 40, Chromium 48,
# Azurvane 55, Adamantite 60, Slag 68, Cinder 75, Mithril 80, Titanium 88, Lumen 95); (lowest level, T), highest first. Java mirrors (SkyyGear
# GearView.tierFor, SkyyBazaar / SkyyAuctions sort) are built from this table.
LEVEL_BANDS = ((95, 15), (88, 14), (80, 13), (75, 12), (68, 11), (60, 10), (55, 9), (48, 8), (40, 7), (35, 6), (28, 5), (20, 4), (15, 3),
               (8, 2))
assert LEVEL_BANDS == tuple((METAL_BANDS[_w][0], metal_tier(_w)) for _w in reversed(LADDER[1:15])), "LEVEL_BANDS = METAL_BANDS' starts"
LEVEL_BANDS_V2 = ((50, 15), (45, 14), (40, 13), (39, 12), (37, 11), (35, 10), (31, 9), (28, 8), (25, 7), (24, 6), (22, 5), (20, 4), (17, 3),
                  (15, 2))          # TT_VERSION 2 (SkyyGear 0.3.22 - 0.3.28), proofs only


def tier_for_level(level, item_id=""):
    """weapon / armor band: Lv 0-7 T1, 8-14 T2, 15-19 T3, 20-27 T4 ... 88-94 T14, 95+ T15 (LEVEL_BANDS); Onyxium ids T16"""
    if "Onyxium" in (item_id or ""):
        return metal_tier("Onyxium")
    for lo, t in LEVEL_BANDS:
        if level >= lo:
            return t
    return 1


LEVEL_CRUDE = 5           # below this a T1 weapon / armor says "Crude" (Lv 3 Stone "T1 Crude", Lv 6 Scrap "T1 Copper", as before the re-band)
LEVEL_CRUDE_V2 = 10       # TT_VERSION 1 / 2


def level_tag(level, item_id=""):
    """the tag of a weapon / armor from its level band start: 'T1 Crude' (Lv 0-4), 'T1 Copper' (5-7), 'T2 Iron' (8-14), ... 'T16 Onyxium'"""
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

# logs (TT_VERSION 3, research/Level-Bands-20-Spec.md 5 - Skyy "we just need to split each zone into 3 tiers of trees"): 15 tree tiers, 3 per zone
# (Zone 1 Emerald Grove + Autumn / Azure forests, Zone 2 savanna / desert, Zone 3 Borea / north, Zone 4 wastes / volcanic, Zone 5 jungle) at the
# hatchet metal that cuts them at normal speed (T1 Copper .. T15 Lumen; the 15-step hatchet ladder exists since SkyyGear 0.3.23). All 34 vanilla
# trunks placed once. The first name of each group = its Foraging armor set (FORAGING_ARMOR).
LOGS = {
    1: ("Oak", "Birch"),
    2: ("Beech", "Ash", "Aspen", "Apple"),
    3: ("Maple", "Azure"),
    4: ("Dry", "Palm"),
    5: ("Bottletree", "Amber"),
    6: ("Gumboab", "Palo"),
    7: ("Fir", "Cedar"),
    8: ("Spiral", "Poisoned", "Windwillow"),
    9: ("Redwood", "Ice"),
    10: ("Burnt", "Sadwillow"),
    11: ("Petrified", "Wisteria_Wild"),
    12: ("Sallow", "Fire"),
    13: ("Jungle", "Bamboo"),
    14: ("Banyan", "Camphor", "Fig_Blue"),
    15: ("Crystal", "Stormbark"),
}
for _t in sorted(LOGS):
    for _w in LOGS[_t]:
        _add("Wood_%s_Trunk" % _w, _t, "log", "SkyyCollections")
# TT_VERSION 2 (5 zone tiers F1-F5 at T1 / T2 / T4 / T7 / T10 + the Orchard side group at T1): proofs / migrations only
_LOGS_V2 = {1: ("Oak", "Birch", "Beech", "Ash", "Aspen", "Apple", "Amber", "Stormbark", "Windwillow", "Wisteria_Wild", "Palm", "Ice", "Sadwillow"),
            2: ("Maple", "Azure"), 4: ("Gumboab", "Dry", "Bottletree", "Palo"), 7: ("Redwood", "Fir", "Cedar", "Poisoned", "Spiral"),
            10: ("Sallow", "Burnt", "Petrified", "Bamboo", "Camphor", "Banyan", "Jungle", "Fig_Blue", "Fire", "Crystal")}
LOG_TIERS_V2 = dict(("Wood_%s_Trunk" % _w, _t) for _t, _ws in _LOGS_V2.items() for _w in _ws)
assert sorted(LOG_TIERS_V2) == sorted(i for i, r in ROWS.items() if r[1] == "log") and len(LOG_TIERS_V2) == 34

# crops (TT_VERSION 3, spec 6): 15 crop tiers, 3 per zone, in the LOCKED Farmer's Workbench pair order (P1 Wheat / Lettuce ... P7 Potato / Onion)
# + the 15th crop Mushroom (spec Q12 default; planted from SPORES - Skyy 2026-10-18 "make sure they use spores, not seeds"). Seeds + Eternal seeds
# = their crop. CROPS = the 14 Plant_Crop_<Crop>_Item crops (the pair crops), (crop, T); the Mushroom rows are their own (MUSHROOM_ROWS).
CROP_LADDER = ("Wheat", "Lettuce", "Carrot", "Corn", "Cauliflower", "Turnip", "Pumpkin", "Aubergine", "Tomato", "Chilli", "Cotton", "Rice",
               "Potato", "Onion", "Mushroom")          # index = T - 1
CROPS = tuple((_c, _i + 1) for _i, _c in enumerate(CROP_LADDER) if _c != "Mushroom")
for _c, _t in CROPS:
    _add("Plant_Crop_%s_Item" % _c, _t, "crop", "SkyyCollections")
    _add("Plant_Seeds_" + _c, _t, "seed", "SkyyCollections")
    _add("Plant_Seeds_%s_Eternal" % _c, _t, "seed", "SkyyCollections")
# the Mushroom: the vanilla cap (the Farming collection's / Enchanted Mushroom's item), the vanilla spore bag (id Plant_Seeds_Mushroom kept, its
# NAME says Mushroom Spores) and our Eternal spores (made by SkyyCollections' build, CO_IDS - not in Assets.zip). Family "spore" (not "seed":
# DynamicSeasons does not shadow them, and every shown name says spores - SPORE_NAMES)
MUSHROOM_ROWS = (("Plant_Crop_Mushroom_Cap_Brown", "crop"), ("Plant_Seeds_Mushroom", "spore"), ("Plant_Spores_Mushroom_Eternal", "spore"))
for _id, _f in MUSHROOM_ROWS:
    _add(_id, CROP_LADDER.index("Mushroom") + 1, _f, "SkyyCollections")
SPORE_NAMES = {"Plant_Seeds_Mushroom": "Mushroom Spores", "Plant_Spores_Mushroom_Eternal": "Eternal Mushroom Spores"}
CO_IDS = frozenset(["Plant_Spores_Mushroom_Eternal"])          # made by SkyyCollections' build (not in Assets.zip)


def spore_name(item_id):
    """the shown name of a spore item ("Mushroom Spores"), None = not one"""
    return SPORE_NAMES.get(item_id)


# TT_VERSION 2 (the pairs at their hoe metal: P1 T1, P2 T2, P3 T4, P4 T7, P5 T10, P6 T13, P7 T16; no Mushroom): proofs / migrations only
CROP_TIERS_V2 = dict(("Plant_Crop_%s_Item" % _c, _t) for _t, _cs in ((1, ("Wheat", "Lettuce")), (2, ("Carrot", "Corn")), (4, ("Cauliflower", "Turnip")),
                                                                     (7, ("Pumpkin", "Aubergine")), (10, ("Tomato", "Chilli")), (13, ("Cotton", "Rice")),
                                                                     (16, ("Potato", "Onion"))) for _c in _cs)
assert sorted(CROP_TIERS_V2) == sorted("Plant_Crop_%s_Item" % _c for _c, _t in CROPS)


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
# round level-bands (SkyyCollections 0.2.28, Skyy 2026-10-18 "and enchanted bronze when both reach 6. use that pattern for all of the alloys"):
# the six Enchanted alloys (tools/skyyench.py TABLE_ALLOYS - not in its TABLE: alloys have no collection) take their alloy bar's tier and word
# (T3 Bronze, T6 Dusk, T9 Azurvane, T12 Cinder, T15 Lumen, T3 Electrum)
ENCH_ALLOYS = tuple((_t[0], _t[2]) for _t in _EN.TABLE_ALLOYS)
for _k, _b in ENCH_ALLOYS:
    _add("Skyy_Ench_" + _k, ROWS[_b][0], "enchanted", "SkyyCollections")
    if _b in WORDS:
        WORDS["Skyy_Ench_" + _k] = WORDS[_b]

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
    _add(_id, metal_tier(_w) or {"Tribal": tier_for_level(remap_family_start(15))}[_w], "armory", "SkyyArmory")   # Tribal = SkyyGear's Tribal row (TT 3: Lv 8) -> T2 Iron
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
# SkyyGear 0.3.31 (Skyy 2026-10-18 "lets make something similar" + popup "Mid game"): our own Infinite Water Bucket - crafted only with a T4
# Thorium lifelong watering can or better, so it carries that tier ("T4 Thorium"). Family "bucket"; made by SkyyGear's build (OWN_IDS).
IWB_ID = "Tool_SkyyInfiniteWaterBucket"
_add(IWB_ID, metal_tier("Thorium"), "bucket", "SkyyGear")
OWN_IDS = OWN_IDS | frozenset([IWB_ID])
# SkyyGear 0.3.29 (round level-bands, research/Level-Bands-20-Spec.md 5 + 6; Skyy 2026-10-18 "we have 15 tiers of mining armor sets. we need to
# update foraging, and farming, to match"): the GATHERING ARMOR ladders. Foraging + Farming = 15 sets at T1 .. T15 (tag = the ladder noun, like
# the logs / crops they gather: "T3 Bronze"); the old set ids keep their ids and looks at new tier slots (Foraging F1 = T1, F2 = T3, F3 = T6,
# F4 = T9, F5 = T12; Farming P1 = T1, P2 = T3, P3 = T5, P4 = T7, P5 = T10, P6 = T11, P7 = T14), the new ones are Armor_<Skill>_<Tree / Crop>_<Slot>.
# Fishing keeps its 5 angler sets at their metal (T1 / T2 / T4 / T7 / T10). (T, id code, look = the tree / crop / metal, set name). Made by
# SkyyGear's build (OWN_IDS). GATHER_SLOTS = the engine's ArmorSlot order.
GATHER_SLOTS = ("Head", "Chest", "Hands", "Legs")
FORAGING_ARMOR = ((1, "F1", "Oak", "Grove Bark"), (2, "Beech", "Beech", "Beech Bark"), (3, "F2", "Maple", "Autumn Bark"),
                  (4, "Dry", "Dry", "Dry Bark"), (5, "Bottletree", "Bottletree", "Bottletree Bark"), (6, "F3", "Gumboab", "Savanna Bark"),
                  (7, "Fir", "Fir", "Fir Bark"), (8, "Spiral", "Spiral", "Spiral Bark"), (9, "F4", "Redwood", "Northern Bark"),
                  (10, "Burnt", "Burnt", "Burnt Bark"), (11, "Petrified", "Petrified", "Petrified Bark"), (12, "F5", "Sallow", "Wastes Bark"),
                  (13, "Jungle", "Jungle", "Jungle Bark"), (14, "Banyan", "Banyan", "Banyan Bark"), (15, "Crystalwood", "Crystalwood", "Crystalwood Bark"))
FARMING_ARMOR = ((1, "P1", "Wheat", "Wheat Harvest"), (2, "Lettuce", "Lettuce", "Lettuce Harvest"), (3, "P2", "Carrot", "Carrot Harvest"),
                 (4, "Corn", "Corn", "Corn Harvest"), (5, "P3", "Cauliflower", "Cauliflower Harvest"), (6, "Turnip", "Turnip", "Turnip Harvest"),
                 (7, "P4", "Pumpkin", "Pumpkin Harvest"), (8, "Aubergine", "Aubergine", "Aubergine Harvest"), (9, "Tomato", "Tomato", "Tomato Harvest"),
                 (10, "P5", "Chilli", "Chilli Harvest"), (11, "P6", "Cotton", "Cotton Harvest"), (12, "Rice", "Rice", "Rice Harvest"),
                 (13, "Potato", "Potato", "Potato Harvest"), (14, "P7", "Onion", "Onion Harvest"), (15, "Mushroom", "Mushroom", "Mushroom Harvest"))
FISHING_ARMOR = tuple((metal_tier(_m), "A%d" % (_k + 1), _m, _m + " Angler") for _k, _m in enumerate(("Copper", "Iron", "Thorium", "Cobalt", "Adamantite")))
GATHER_ARMOR = (("Foraging", FORAGING_ARMOR), ("Farming", FARMING_ARMOR), ("Fishing", FISHING_ARMOR))
assert [r[0] for r in FORAGING_ARMOR] == list(range(1, 16)) == [r[0] for r in FARMING_ARMOR] and [r[0] for r in FISHING_ARMOR] == [1, 2, 4, 7, 10]
assert [r[2] for r in FORAGING_ARMOR] == [LOGS[_t][0] if _t != 15 else "Crystalwood" for _t in range(1, 16)], "a Foraging set = its tier's key tree"
assert [r[2] for r in FARMING_ARMOR] == list(CROP_LADDER), "a Farming set = its tier's crop"


def gather_armor_id(skill, code, slot):
    return "Armor_%s_%s_%s" % (skill, code, slot)


GA_IDS = []
for _sk, _rows in GATHER_ARMOR:
    for _t, _code, _look, _nm in _rows:
        for _sl in GATHER_SLOTS:
            _add(gather_armor_id(_sk, _code, _sl), _t, _sk.lower() + "_armor", "SkyyGear")
            GA_IDS.append(gather_armor_id(_sk, _code, _sl))
OWN_IDS = OWN_IDS | frozenset(GA_IDS)
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
# SkyyArmory 0.1.34 (round A2, spec 4.1 Group B; rows added by the Movement 2 builder at the main session's request 2026-10-18): the 10
# vanilla metal families in the 8 zone metals / alloys (Weapon_<Family>_<M>_SkyWynn - the zone partner's vanilla item with our art + numbers).
# Owner SkyyArmory (its lang writes the "T5 Lead - " tags itself); family armory_metal like A1.
A2_FAMILIES = ("Sword", "Longsword", "Axe", "Battleaxe", "Mace", "Club", "Daggers", "Spear", "Shortbow", "Shield")
A2_WEAPONS = tuple("Weapon_%s_%s_SkyWynn" % (_f, _g) for _f in A2_FAMILIES for _g in G2_METALS[1:])
for _id_g in A2_WEAPONS:
    _add(_id_g, metal_tier(_id_g.split("_")[-2]), "armory_metal", "SkyyArmory")
AR_IDS = frozenset(A1_WEAPONS + A2_WEAPONS)
# SkyyFishing 0.2.0 (round fish2, research/cloud/Fishing-Stage2-Build.md 2 / 3; Skyy 2026-10-20 "just go with the recommended on all of them"):
# its 8 rods, 7 reels and 27 fish. Owner SkyyFishing (its lang writes the tags; one writer per key). Made by SkyyFishing's build (FI_IDS, not in
# Assets.zip). The rod / reel ids keep their 0.1 words (no saved-data change); rods + reels T5 / T6 SHOW the Zone 3 metals (spec question 1:
# Adamantite and Mithril ore only exist in Zones 4 / 5): Rod_Adamantite = "T8 Chromium", Rod_Mithril = "T9 Azurvane" (WORDS), like Bamboo shows
# "T1 Crude" (sticks, Wooden). Fish: own-ladder word "Fish"; a fish's tier = max(its zone's first step - Z1 T1, Z2 T4, Z3 T7 -, the tier of the
# lowest rod that lands its minimum weight) (spec question 3) - SkyyFishing's build re-checks that rule against its species table.
FI_RODS = (("Bamboo", "Crude"), ("Copper", "Copper"), ("Iron", "Iron"), ("Thorium", "Thorium"), ("Cobalt", "Cobalt"), ("Adamantite", "Chromium"),
           ("Mithril", "Azurvane"), ("Onyxium", "Onyxium"))          # (id word, shown metal)
FI_REELS = FI_RODS[:7]                                               # no Onyxium reel yet (stage 3)
FI_FISH = (("OverdueMinnow", 1), ("Bluegill", 1), ("RustbackTrout", 1), ("QueuePerch", 1), ("MisfiledCarp", 1), ("StampedCatfish", 1),
           ("MirebridgeEel", 1), ("PonderingPike", 2), ("GoldenKoi", 1), ("Goldfish", 1),
           ("OasisCarp", 4), ("Sandskipper", 4), ("DunePiranha", 4), ("MirageEel", 4), ("TarPitGudgeon", 4), ("LostLuggageGrouper", 4),
           ("MirageSturgeon", 7), ("Sandsalmon", 4),
           ("FrostCod", 7), ("WhisperChar", 7), ("SnowmeltTrout", 7), ("IceboundSalmon", 7), ("PermitLamprey", 7), ("GlassPike", 8),
           ("WhisperSturgeon", 9), ("BlizzardHalibut", 8), ("SleeperAisle9", 9))
for _fam_f, _pre_f, _rows_f in (("rod", "SkyyFishing_Rod_", FI_RODS), ("reel", "SkyyFishing_Reel_", FI_REELS)):
    for _w_f, _m_f in _rows_f:
        _add(_pre_f + _w_f, metal_tier(_m_f), _fam_f, "SkyyFishing")
        if _m_f in CRUDE_WORDS:
            WORDS[_pre_f + _w_f] = "Crude"                    # "T1 Crude" (Wooden); T8 Chromium / T9 Azurvane = the ladder nouns
for _k_f, _t_f in FI_FISH:
    _add("SkyyFishing_Fish_" + _k_f, _t_f, "fish", "SkyyFishing")
    WORDS["SkyyFishing_Fish_" + _k_f] = "Fish"
FI_IDS = frozenset(i for i, r in ROWS.items() if r[2] == "SkyyFishing")      # made by SkyyFishing's build (not in Assets.zip)
assert len(FI_IDS) == 8 + 7 + 27 and tag_text(ROWS["SkyyFishing_Rod_Adamantite"][0]) == "T8 Chromium"


# ------------------------------------------------------------------------------------------------ rarity-tagged items (no T-number)
# Pet eggs (research/Pet-Eggs-Spec.md 1.1, round pets040 = SkyyPets 0.4.0): eggs are tiered by RARITY, so their tag is the rarity + noun as
# the first phrase - "Rare Egg - Right-click to hatch ..." (a "T3 Egg" would read as Iron). Kept apart from ROWS (the metal ladder): tag_for()
# answers both, families() / ids_in() / ids_for() stay the metal ladder's; rarity_ids_for(owner) lists these. Ids from tools/skyyeggs.py.
RARITY_LADDER = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic")
RARITY_NOUNS = ("Egg", "Dragon Egg")          # SkyyPets 0.4.11: + our elemental dragon eggs ("Legendary Dragon Egg")
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
# Dragon eggs (SkyyPets 0.4.11, research/Dragon-Pet-Spec.md 2): OUR three elemental dragon eggs are Legendary items -> "Legendary Dragon Egg - ..."
# (family dragonegg). Aures' two Nestkeeper eggs are THEIR items (their lang, their text): never tagged by us.
for _e in _EGG.DRAGON_EGGS:
    if _e[3] == "SkyyPets":
        _add_rarity(_e[0], "Legendary", "Dragon Egg", "dragonegg", "SkyyPets")
# Secret dragon eggs (SkyyPets 0.4.19, research/cloud/Secret-Dragons-Spec.md): Legendary items too, but tagged plain "Legendary Egg - ..."
# (family secretegg) - the secret stays a secret (Skyy: "no quest or explanation - players figure them out").
for _e in getattr(_EGG, "SECRET_EGGS", []):
    _add_rarity(_e[0], "Legendary", "Egg", "secretegg", "SkyyPets")


# UT-28 (SkyyGear 0.3.47 round ut28, research/cloud/UT-28-Build-Sheet.md section 6): the first 28 Zone 1-5 Untiered items (64 ids, tools/ut28.py)
# tagged with their ZONE'S ALLOY (gear.md 285 "UT = the zone's alloy"): Z1 T3 Bronze, Z2 T6 Dusk, Z3 T9 Azurvane, Z4 T12 Cinder, Z5 T15 Lumen.
# Family "ut"; owner = the mod that builds the copy (SkyyGear 55, SkyyArmory 9 - its round writes their lang). Not in Assets.zip (UT_IDS).
import ut28 as _UT28        # pure Python table, no game files
for _u28r in _UT28.rows():
    _add(_u28r[0], metal_tier(_UT28.ZONE_ALLOY[_u28r[3]]), "ut", "SkyyGear" if _u28r[4] == "gear" else "SkyyArmory")
UT_IDS = tuple(_UT28.IDS)
del _u28r


def rarity_tag_for(item_id):
    r = RARITY_ROWS.get(item_id)
    return None if r is None else rarity_tag(r[0], r[1])


def rarity_ids_for(owner_mod, fam="egg"):
    """the rarity-tagged ids of one mod and family (default "egg" = the 30 category eggs, as before 0.4.11; "dragonegg" = the dragon eggs)"""
    return sorted(i for i, r in RARITY_ROWS.items() if r[3] == owner_mod and r[2] == fam)


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


del _m, _t, _w, _c, _k, _b, _id, _h, _f, _i, _e, _z, _s, _lo, _hi, _sk, _rows, _code, _look, _nm, _sl, _fam_f, _pre_f, _rows_f, _w_f, _m_f, _k_f, _t_f
