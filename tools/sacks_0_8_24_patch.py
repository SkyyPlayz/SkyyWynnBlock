"""Derive SkyySacks/build_skyysacks_0.8.24.py from the SET pin 0.8.23 (the GENERATED build_skyysacks_0.8.23.py; edit THIS file, then
regenerate: python tools/sacks_0_8_24_patch.py; never re-run sacks_0_8_23_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.23 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_24_patch.py   then   python SkyySacks/build_skyysacks_0.8.24.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.24.py [--dir <folder inside tools/dev/scratch/>] [--keep]
Built against tools/tier_tags.py TT_VERSION 3 (SkyyGear 0.3.29 round: 20 levels per zone, 15 tree tiers, 15 crop tiers) - ship with it.

0.8.24 (2026-10-18) = EVERY VOID CATEGORY GETS THE SAME SPACE BUFF + FAIR UPGRADE COSTS ON THE 15-STEP TIERS (docs/answered/bags.md 2026-10-18).
Skyy (screenshots: Pocket > Foraging Lv 23 Unique 4,393 / 5,175 "+225 space"; upgrade to Rare costs Oak-tier logs 2,000 + Maple-tier 1,000 +
Gumboab-tier 500 + Tree Sap 250 | Farming Lv 4 Unique 900 / 900 full; upgrade costs Wheat 2,000 + Carrot 1,000 + Cauliflower 500 + Essence of
Life 250): "when you buffed how much the foraging sack holds, you forgot to do the same for the rest of them.   (lets adjust what the upgrade
cost based on the new metal, farming, and gathering tiers.) i want the upgrade cost to be fair. expensive but manageable".
  1. WHY FORAGING LOOKED BUFFED: every category already used ONE rule (space = level x pd.perLevel x the rarity; the 0.8.9 buff 100 -> 150 per
     level went to all six). Foraging is big only because its LEVEL is: logs come in by the dozen (Tree Feller, Skills 0.4.50's bigger
     fell caps) - Skyy's live profile counts 4,704 Foraging items (Lv 23) but ~200 Farming items (Lv 4); the Farming space is full mostly of
     Essence of Life (539) and eggs, which do not raise its level much. So the buff every category gets is a STARTING SPACE that does not
     depend on how fast that category levels: space = (pd.base + level x pd.perLevel) x the rarity multiplier, pd.base = 1,500 (10 levels'
     worth) - the SAME rule and the same numbers for all six (VoidStore.capOf, the only space formula; nothing reads a per-category space).
     pd.base 0 = exactly the 0.8.23 rule. The "+225 space" per level is unchanged (still 150 x the rarity). Space only grows.
     Skyy's live profile (rarity, saved best level): Mining Lv 7 Normal 1,050 -> 2,550 | Foraging Lv 23 Unique 5,175 -> 7,425 | Farming Lv 4
     Unique 900 -> 3,150 | Fishing Lv 3 Normal 450 -> 1,950 | Combat Lv 4 Normal 600 -> 2,100 | Smithing Lv 5 Normal 750 -> 2,250.
  2. THE COSTS, RE-TIERED (tools/tier_tags.py TT_VERSION 3; research/Level-Bands-20-Spec.md 1 / 5 / 6): each step asks only for tiers the
     player has reached at that point - Unique = Zone 1 early (T1-T2), Rare = Zone 1 late (T1-T3), Legendary = Zone 2 late (up to T6).
     The old Rare costs asked for Zone 2 (Gumboab T6, Cauliflower T5, Thorium T4) and the old Legendary for Zone 3-4 (Redwood T9, Sallow T12,
     Cobalt T7, Adamantite T10) - that was the unfair part. No Enchanted item in any cost (Skyy 2026-10-18, gear.md: no Enchanted till Dusk).
     A log id counts its whole v3 tree tier (SackDefs.LOGT_*, now the 15 groups of tier_tags.LOGS: "Oak-tier" = Oak + Birch, "Beech-tier" =
     Beech, Ash, Aspen, Apple, "Maple-tier" = Maple + Azure ...). Fishing keeps its costs (no fish ladder yet - Skyy: "fishing can wait for an
     overhaul"). Our zone metals (Lead ore / ingot, Dusk ingot) come from SkyyWorldGen (in the SET; the build checks its pinned jar has them).
     Fair = "expensive but manageable": 1-2 h of focused gathering for Unique, 3.5-6 h for Rare, 8-11 h for Legendary (assumed rates, below;
     the build prints each step's hours and stops if one goes past 2.5 / 6 / 12 h or any step costs more items than in 0.8.23).
       step       | category | 0.8.23 cost (total)                                      | 0.8.24 cost (total)
       Unique     | Mining   | Cobble 500, Copper 250, Iron 100 (850)                   | Cobble 400, Copper ore 250, Iron ore 100 (750)
       Rare       | Mining   | Cobble 2000, Copper 1000, Iron 1000, Thorium 250 (4250)  | Cobble 1000, Copper ore 600, Iron ore 500 (2100)
       Legendary  | Mining   | Cobble 5000, Iron 2500, Thorium 1000, Cobalt 500, Adamantite 100 (9100) | Cobble 2000, Copper 750, Iron 750, Thorium 500, Lead 300 (4300)
       Unique     | Foraging | Oak 500, Fibre 500, Sap 100 (1100)                       | Oak-tier 400, Beech-tier 200, Fibre 250, Sap 100 (950)
       Rare       | Foraging | Oak 2000, Maple 1000, Gumboab 500, Sap 250 (3750)        | Oak-tier 1000, Beech-tier 1000, Maple-tier 500, Sap 250 (2750)
       Legendary  | Foraging | Oak 5000, Maple 2000, Gumboab 1000, Redwood 1000, Sallow 500, Sap 500 (10000) | Beech 2000, Maple 1500, Dry 1000, Bottletree 750, Gumboab 500, Sap 500 (6250)
       Unique     | Farming  | Wheat 500, Lettuce 250, Ess. of Life 100 (850)           | Wheat 400, Lettuce 200, Ess. of Life 100 (700)
       Rare       | Farming  | Wheat 2000, Carrot 1000, Cauliflower 500, EoL 250 (3750) | Wheat 750, Lettuce 500, Carrot 500, EoL 250 (2000)
       Legendary  | Farming  | Wheat 5000, Carrot 2000, Pumpkin 1000, Tomato 1000, Cotton 500, EoL 500 (10000) | Wheat 1500, Carrot 1000, Corn 750, Cauliflower 500, Turnip 500, EoL 500 (4750)
       Unique     | Combat   | Bone 250, Linen 100 (350)                                | Bone 200, Linen 50 (250)
       Rare       | Combat   | Bone 1000, Linen 500, Venom 100, Chitin 100, Shadoweave 100 (1800) | Bone 750, Linen 200, Venom 50, Chitin 50 (1050)
       Legendary  | Combat   | Bone 2500, Linen 1000, Venom 250, Chitin 250, Void Ess. 100, Voidheart 10 (4110) | Bone 1500, Linen 400, Venom 150, Chitin 150, Shadoweave 100, Void Ess. 100 (2400)
       Unique     | Smithing | Light Leather 200, Copper Ingot 100 (300)                | Light Leather 60, Copper Ingot 150 (210)
       Rare       | Smithing | Light 750, Medium 500, Copper 250, Iron 100 (1600)       | Light 100, Medium 60, Copper 200, Iron 150, Bronze 100 (610)
       Legendary  | Smithing | Light 2000, Medium 1000, Heavy 250, Iron 250, Thorium 100 (3600) | Medium 150, Heavy 100, Iron 300, Thorium 200, Lead 150, Dusk 100 (1000)
       Fishing    | (all)    | Raw Fish 100 / 500 + Bluegill 50 / 1500 + Catfish 150 + Minnow 150 | unchanged
     Assumed focused rates (FAIR_RATES below, printed by the build; ESTIMATES - Skyy's live profile gathered ~2,900 logs + 1,800 sticks / sap /
     fibre in its first session, 115 ores, 43 crops, 16 bones, 18 Linen): logs 800 / h (Zone 1, Tree Feller; 500 / h for a tier you travel to),
     ore 300 / h (Vein Burst + Fortune), crops 400 / h (a grown field + Fortune), bones 150 / h, Linen 40 / h, venom / chitin 15 / h,
     hides -> leather 40 / h, bars = ore smelted. Every step is far below what the category holds at its old gate level (>= 1.25x, checked).
  3. SAVED DATA: none changes. Rarities, best levels and stored items are kept; space only grows (pd.base >= 0 adds, the rule is otherwise
     0.8.23's); a category already over its space keeps every item (only new intake stops - unchanged code).
  4. ONE-TIME CONFIG UPDATE (PROJECT-RULES 4; SackMig0824 = SackMig089's code, run right AFTER it in setup, before SackCfg.reload): the 15
     changed pd.cost.* lines move from the 0.8.23 default to the 0.8.24 one ONLY while they still hold it (text without spaces); a hand-edited,
     doubled or continued line is kept and named in an INFO line; the commented template lines holding the old default get the new one; a
     verified History copy first, one change-log line per moved value (Server Setup -> Changes -> Undo), the marker line skyysacks-0.8.24-void
     appended (runs once), every other byte and each line's own ending kept. A pre-0.8.9 file: SackMig089 moves it to the 0.8.9 values first
     (= the 0.8.23 ones), then SackMig0824 moves it on. pd.base is a NEW row (Server Setup -> SkyyVoid and Crafting -> "Starting space"):
     no line = the new default 1,500, no migration needed.
  5. RecipeCmp's /craft sort table is re-baked from tools/tier_tags.py TT_VERSION 3 (logs / crops / seeds on the 15-step tree and crop
     ladders; the Mushroom cap + spores group as one crop family "Mushroom" - crop, spores, Eternal spores).
  6. (SkyyCollections 0.2.28 hand-off) THE FURNACE TAB'S ALLOY ROWS RESPECT RECIPE KNOWLEDGE (CraftPage.alloyOk = KnowSync.allowedOut, the
     test the instant tabs use): SkyyWorldGen 0.7.5's Enchanted smelts Alloy_Ench_<Alloy> (1 Enchanted A + 1 Enchanted B -> 2) are drawn
     greyed "- your collections unlock this (/collections)" and procQueue refuses them until SkyyCollections grants the output (both input
     collections at VI - Collections flags them KnowledgeRequired at run time and teaches the output id). An Alloy_Ench_ id counts as
     knowledge-required even without that flag (no SkyyCollections = locked, never free). Plain alloy rows keep only the Furnace Charm gate.
  7. (same hand-off) the 6 Enchanted alloys (tools/skyyench.py TABLE_ALLOYS: Skyy_Ench_Bronze / Dusk / Azurvane / Cinder / Lumen / Electrum)
     get a Void home: MINING, their TABLE_ALLOYS category, like every other Enchanted metal (so the Bazaar's Mining tab matches; SackDefs.enchCat;
     the build checks SkyyCollections 0.2.28 ships the 6 items).
  8. (SkyyArmory 0.1.38 Soul Cage hand-off; gear.md 2026-10-18 popup "Use the worst one (Recommended)") WORST FIRST: a recipe input that is
     a RESOURCE TYPE (Armory 0.1.38's SkyyArmory_Any_<SoulOrb | SoulCage_metal>) matched by rolled gear takes the LOWEST rarity first (normal,
     unique, rare, set, legendary, fabled, untiered, mythic), then the lowest level, then slot order; plain / unrolled stacks count as the
     lowest (CraftPage.wear reads the SkyyGear document "r" / "lvl" - no Gear bridge answers rarity). /craft instant crafts (craftOne) and the
     timed queue (procQueue) take those inputs through CraftPage.takeWorst, the rest through the engine as before; recipes with no rolled match
     are untouched. sacks:fn:craftHave / craftPay (SkyyGear's Smithing Craft tab) now copy the rolled stacks such an input matches (with their
     document) so a rolled orb counts 1 / 1, and pay worst first; any OTHER stack with metadata still refuses the payment; a refund gives the
     rolled stack back as itself (receipt [6]). Exactly the needed whole items go; a take that cannot finish puts every stack back - nothing taken.
  No new command / system / bridge key. ROLLBACK to 0.8.23: safe (no saved data; stored Enchanted alloys stay in the pool file but have no
  category in 0.8.23, so they are not shown or taken in until 0.8.24 returns; Enchanted alloy smelts become queueable by charm alone). The space falls back to level x 150 x rarity (nothing is
  deleted; an over-full category just stops taking new items); a config the update moved keeps the 0.8.24 cost lines (0.8.23 reads them -
  costs naming Beech / Dry / Bottletree logs then count 0.8.23's 5-group log tiers) - Undo them in Server Setup -> Changes first if wanted.
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)
import tier_tags as TT

assert TT.TT_VERSION == "3", "0.8.24 is built on tools/tier_tags.py TT_VERSION 3 (the 15 tree / crop tiers)"
P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.23.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.24.py"))
assert P.has('VERSION = "0.8.23"\n') and P.has("public synchronized long fuelTotalMs() {") and P.has('smig = pool.makeClass(PKG + ".SackMig089")'), \
    "not the live generated SkyySacks 0.8.23"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.24 (2026-10-18)"):].rstrip() + "\n"

# ---- header, version
P.rep('''  ROLLBACK to 0.8.22: safe (page layout only).
"""
''', '''  ROLLBACK to 0.8.22: safe (page layout only).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.23"\n', 'VERSION = "0.8.24"\n')

# ---- 1. the starting space (one rule for all six) + 2. the re-tiered costs
OLD_COST_START = "PD_COST = {\n"
_i = P.s.index(OLD_COST_START)
_j = P.s.index("}\n", _i) + 2
OLD_COST_BLOCK = P.s[_i:_j]
assert OLD_COST_BLOCK.count("PD_COST = {") == 1 and '("Smithing", 3)' in OLD_COST_BLOCK
NEW_COST_BLOCK = '''# 0.8.24 (Skyy "lets adjust what the upgrade cost based on the new metal, farming, and gathering tiers.) i want the upgrade cost to be fair.
# expensive but manageable"): the 15-step tiers of tools/tier_tags.py TT_VERSION 3 - Unique = Zone 1 early (T1-T2), Rare = Zone 1 late
# (T1-T3), Legendary = Zone 2 late (up to T6); no Enchanted item (gear.md 2026-10-18); a log id = its whole v3 tree tier (LOG_TIERS below).
# Fishing unchanged (no fish ladder yet - Skyy: "fishing can wait for an overhaul"). The 0.8.23 table stays as PD_COST_0823 (the migration).
PD_COST = {
    ("Mining", 1): [("Rock_Stone_Cobble", 400), ("Ore_Copper", 250), ("Ore_Iron", 100)],
    ("Mining", 2): [("Rock_Stone_Cobble", 1000), ("Ore_Copper", 600), ("Ore_Iron", 500)],
    ("Mining", 3): [("Rock_Stone_Cobble", 2000), ("Ore_Copper", 750), ("Ore_Iron", 750), ("Ore_Thorium", 500), ("Ore_Lead_SkyWynn", 300)],
    ("Foraging", 1): [("Wood_Oak_Trunk", 400), ("Wood_Beech_Trunk", 200), ("Ingredient_Fibre", 250), ("Ingredient_Tree_Sap", 100)],
    ("Foraging", 2): [("Wood_Oak_Trunk", 1000), ("Wood_Beech_Trunk", 1000), ("Wood_Maple_Trunk", 500), ("Ingredient_Tree_Sap", 250)],
    ("Foraging", 3): [("Wood_Beech_Trunk", 2000), ("Wood_Maple_Trunk", 1500), ("Wood_Dry_Trunk", 1000), ("Wood_Bottletree_Trunk", 750),
                      ("Wood_Gumboab_Trunk", 500), ("Ingredient_Tree_Sap", 500)],
    ("Farming", 1): [("Plant_Crop_Wheat_Item", 400), ("Plant_Crop_Lettuce_Item", 200), ("Ingredient_Life_Essence", 100)],
    ("Farming", 2): [("Plant_Crop_Wheat_Item", 750), ("Plant_Crop_Lettuce_Item", 500), ("Plant_Crop_Carrot_Item", 500),
                     ("Ingredient_Life_Essence", 250)],
    ("Farming", 3): [("Plant_Crop_Wheat_Item", 1500), ("Plant_Crop_Carrot_Item", 1000), ("Plant_Crop_Corn_Item", 750),
                     ("Plant_Crop_Cauliflower_Item", 500), ("Plant_Crop_Turnip_Item", 500), ("Ingredient_Life_Essence", 500)],
    ("Fishing", 1): [("Food_Fish_Raw", 100)],
    ("Fishing", 2): [("Food_Fish_Raw", 500), ("Fish_Bluegill_Item", 50)],
    ("Fishing", 3): [("Food_Fish_Raw", 1500), ("Fish_Catfish_Item", 150), ("Fish_Minnow_Item", 150)],
    ("Combat", 1): [("Ingredient_Bone_Fragment", 200), ("Ingredient_Fabric_Scrap_Linen", 50)],
    ("Combat", 2): [("Ingredient_Bone_Fragment", 750), ("Ingredient_Fabric_Scrap_Linen", 200), ("Ingredient_Sac_Venom", 50),
                    ("Ingredient_Chitin_Sturdy", 50)],
    ("Combat", 3): [("Ingredient_Bone_Fragment", 1500), ("Ingredient_Fabric_Scrap_Linen", 400), ("Ingredient_Sac_Venom", 150),
                    ("Ingredient_Chitin_Sturdy", 150), ("Ingredient_Fabric_Scrap_Shadoweave", 100), ("Ingredient_Void_Essence", 100)],
    ("Smithing", 1): [("Ingredient_Leather_Light", 60), ("Ingredient_Bar_Copper", 150)],
    ("Smithing", 2): [("Ingredient_Leather_Light", 100), ("Ingredient_Leather_Medium", 60), ("Ingredient_Bar_Copper", 200),
                      ("Ingredient_Bar_Iron", 150), ("Ingredient_Bar_Bronze", 100)],
    ("Smithing", 3): [("Ingredient_Leather_Medium", 150), ("Ingredient_Leather_Heavy", 100), ("Ingredient_Bar_Iron", 300),
                      ("Ingredient_Bar_Thorium", 200), ("Ingredient_Bar_Lead_SkyWynn", 150), ("Ingredient_Bar_Dusk_SkyWynn", 100)],
}
'''
P.rep(OLD_COST_BLOCK, NEW_COST_BLOCK + OLD_COST_BLOCK.replace("PD_COST = {", "PD_COST_0823 = {   # 0.8.23's defaults (SackMig0824's old values)", 1))
P.rep('''PD_PER_LEVEL, PD_MAX_LEVEL = 150, 250   # 0.8.9 (Skyy "make the level ups give a little more storage"): 100 -> 150
''', '''PD_PER_LEVEL, PD_MAX_LEVEL = 150, 250   # 0.8.9 (Skyy "make the level ups give a little more storage"): 100 -> 150
# 0.8.24 (Skyy "when you buffed how much the foraging sack holds, you forgot to do the same for the rest of them."): every category starts
# with this much space before levels - space = (pd.base + level x pd.perLevel) x the rarity multiplier, the same for all six (0 = 0.8.23)
PD_BASE = 1500
''')
P.rep('''assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
''', '''assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
assert sorted(PD_COST_0823) == sorted(PD_COST) and all(PD_COST[("Fishing", r)] == PD_COST_0823[("Fishing", r)] for r in (1, 2, 3))
# 0.8.24: each step asks only for tiers reached by then (TT v3: Unique <= T2 Zone 1 early, Rare <= T3 Zone 1 late, Legendary <= T6 Zone 2);
# no Enchanted item (gear.md 2026-10-18: nothing Enchanted below Dusk); every tiered category names at least one item of its step's top band
PD_STEP_TOP = {1: 2, 2: 3, 3: 6}
assert all(TT.tier(i) is None or TT.tier(i) <= PD_STEP_TOP[r] for (c, r), v in PD_COST.items() for i, _q in v), "0.8.24: a cost above its zone"
assert not [i for v in PD_COST.values() for i, _q in v if i.startswith("Skyy_Ench_")], "0.8.24: no Enchanted item in a Void cost"
# (Mining has no ore of its own at T3 / T6 - Bronze and Dusk are alloys = Smithing bars - so its tops are Iron T2 and Lead T5)
_TOPS = {("Foraging", 1): 2, ("Foraging", 2): 3, ("Foraging", 3): 6, ("Farming", 1): 2, ("Farming", 2): 3, ("Farming", 3): 6,
         ("Mining", 1): 2, ("Mining", 2): 2, ("Mining", 3): 5, ("Smithing", 1): 1, ("Smithing", 2): 3, ("Smithing", 3): 6}
assert all(max(TT.tier(i) or 0 for i, _q in PD_COST[k]) == t for k, t in _TOPS.items()), "0.8.24: each step reaches its band's top tier"
# 0.8.24 FAIRNESS ("expensive but manageable"): focused hours per step at ASSUMED rates (items / hour; research notes in the patch docstring).
# Bars = ore smelted (the ore rate), leather = hides tanned. Printed so a later re-balance has the numbers; ~1 h Unique, 3-5 h Rare, 8-12 h Legendary.
FAIR_RATES = {"log": 800, "log_far": 500, "ore": 300, "crop": 400, "bone": 150, "linen": 40, "rare_drop": 15, "leather": 40, "sap": 150, "fibre": 250}
def _fair_kind(i, r):
    f = TT.family(i)
    if f == "log":
        return "log_far" if (TT.tier(i) or 1) > (2 if r < 3 else 3) else "log"
    if f in ("ore", "zone_ore", "bar", "zone_bar", "alloy"):
        return "ore"
    if f == "crop":
        return "crop"
    return {"Ingredient_Bone_Fragment": "bone", "Ingredient_Fabric_Scrap_Linen": "linen", "Ingredient_Tree_Sap": "sap", "Ingredient_Fibre": "fibre",
            "Rock_Stone_Cobble": None, "Ingredient_Life_Essence": None}.get(i, "leather" if i.startswith("Ingredient_Leather_") else "rare_drop")
_FAIR_MAIN = ("log", "log_far", "ore", "crop", "bone", "leather")    # gathered one after the other: their hours add up
def _fair_hours(c, r):
    """the main items' hours added up, or the slowest side item (sap, fibre, Linen, rare drops come in alongside) if that takes longer;
    cobble / Essence of Life come along with the rest"""
    main, side = 0.0, 0.0
    for i, q in PD_COST[(c, r)]:
        k = _fair_kind(i, r)
        if k in _FAIR_MAIN:
            main += q / float(FAIR_RATES[k])
        elif k:
            side = max(side, q / float(FAIR_RATES[k]))
    return max(main, side)
_fair = dict(((c, r), _fair_hours(c, r)) for c in PD_CATS if c != "Fishing" for r in (1, 2, 3))
assert all(_fair[(c, 1)] <= 2.5 and _fair[(c, 2)] <= 6.0 and _fair[(c, 3)] <= 12.0 for c in PD_CATS if c != "Fishing"), _fair
assert all(sum(q for _i, q in PD_COST[k]) <= sum(q for _i, q in PD_COST_0823[k]) for k in PD_COST), "0.8.24: no step got dearer in items"
print("fair hours (assumed rates %s): %s" % (FAIR_RATES, " | ".join("%s %s" % (c, "/".join("%.1f" % _fair[(c, r)] for r in (1, 2, 3)))
                                                                     for c in PD_CATS if c != "Fishing")))
''')
P.rep('''            room = g * PD_PER_LEVEL * PD_MULT[r - 1]
''', '''            room = (PD_BASE + g * PD_PER_LEVEL) * PD_MULT[r - 1]   # 0.8.24: + the starting space
''')
P.rep('''_pdt = dict(("pd.cost.%s.%s" % (c, PD_RAR[r]), ",".join("%s:%d" % x for x in v)) for (c, r), v in PD_COST.items())
''', '''_pdt = dict(("pd.cost.%s.%s" % (c, PD_RAR[r]), ",".join("%s:%d" % x for x in v)) for (c, r), v in PD_COST_0823.items())   # 0.8.24: 0.8.9 = 0.8.23
''')
P.rep('''MIG089_MK = 'skyysacks-0.8.9-void'
''', '''MIG089_MK = 'skyysacks-0.8.9-void'
# 0.8.24: the one-time config update (SackMig0824, right after SackMig089): every cost line whose default changed, 0.8.23 -> 0.8.24
MIG0824 = [("pd.cost.%s.%s" % (c, PD_RAR[r]), ",".join("%s:%d" % x for x in PD_COST_0823[(c, r)]), ",".join("%s:%d" % x for x in PD_COST[(c, r)]), "t")
           for c in PD_CATS for r in (1, 2, 3) if PD_COST_0823[(c, r)] != PD_COST[(c, r)]]
MIG0824_MK = 'skyysacks-0.8.24-void'
assert len(MIG0824) == 15 and not [m for m in MIG0824 if m[0].startswith("pd.cost.Fishing.")]
''')
# the tier logs = the 15 TT v3 tree tiers (key log = the first name = its Foraging armor set)
P.rep('''LOG_TIERS = (('Oak', 'Birch', 'Beech', 'Ash', 'Aspen'), ('Maple', 'Azure'), ('Gumboab', 'Dry', 'Bottletree', 'Palo'), ('Redwood', 'Fir', 'Cedar', 'Poisoned', 'Spiral'), ('Sallow', 'Burnt', 'Petrified', 'Bamboo', 'Camphor', 'Banyan', 'Jungle', 'Fig_Blue', 'Fire', 'Crystal'))
LOG_IDS = [["Wood_%s_Trunk" % w for w in t] for t in LOG_TIERS]
_flat = [i for t in LOG_IDS for i in t]
assert len(_flat) == len(set(_flat)) == 26 and [t[0] for t in LOG_IDS] == ["Wood_Oak_Trunk", "Wood_Maple_Trunk", "Wood_Gumboab_Trunk",
                                                                          "Wood_Redwood_Trunk", "Wood_Sallow_Trunk"]
''', '''# 0.8.24: the 15 tree tiers of tools/tier_tags.py TT_VERSION 3 (LOGS, 3 per zone, all 34 vanilla trunks; key log first = the tier's name
# "Oak-tier logs", "Beech-tier logs" ...). Was 0.8.8's 5 groups (26 logs): ('Oak', 'Birch', 'Beech', 'Ash', 'Aspen'), ('Maple', 'Azure'), ...
LOG_TIERS = tuple(tuple(TT.LOGS[_t]) for _t in sorted(TT.LOGS))
LOG_IDS = [["Wood_%s_Trunk" % w for w in t] for t in LOG_TIERS]
_flat = [i for t in LOG_IDS for i in t]
assert sorted(TT.LOGS) == list(range(1, 16)) and all(TT.tier(i) == n + 1 for n, t in enumerate(LOG_IDS) for i in t)
assert len(_flat) == len(set(_flat)) == 34 and [t[0] for t in LOG_IDS][:6] == ["Wood_Oak_Trunk", "Wood_Beech_Trunk", "Wood_Maple_Trunk",
                                                                              "Wood_Dry_Trunk", "Wood_Bottletree_Trunk", "Wood_Gumboab_Trunk"]
assert [t[0] for t in LOG_IDS][2::3] == ["Wood_Maple_Trunk", "Wood_Gumboab_Trunk", "Wood_Redwood_Trunk", "Wood_Sallow_Trunk", "Wood_Crystal_Trunk"]
''')
# the cost ids made by SkyyWorldGen (our zone metals; not in Assets.zip): in the SET, and in its pinned jar
P.rep('''    want = sorted(set(i for v in PD_COST.values() for i, _q in v) | set(i for t in REFUND_BY_RANK for i in re.findall(r"([A-Za-z0-9_]+):", t)))
    bad = [i for i in want if i not in ids]
''', '''    want = sorted(set(i for v in PD_COST.values() for i, _q in v) | set(i for t in REFUND_BY_RANK for i in re.findall(r"([A-Za-z0-9_]+):", t)))
    # 0.8.24: our zone metals (Lead ore / ingot, Dusk ingot) are SkyyWorldGen's items (tier_tags.WG_IDS): made by its build (ore veins + Furnace /
    # SkyyAlloy recipes), not Assets.zip - the SET must hold SkyyWorldGen and its pinned jar must carry each item file
    wg = [i for i in want if i in TT.WG_IDS]
    wg_made = set()   # the PrimaryOutput of every recipe the pinned SkyyWorldGen jar ships (its SkyyAlloy smelts make vanilla Bronze bars too)
    if wg or "Ingredient_Bar_Bronze" in want:
        _ds = open(os.path.join(HERE, "..", "tools", "deploy_set.py"), encoding="utf8").read()
        _m = re.search(r'\\("SkyyWorldGen", "([0-9.]+)"\\)', _ds[_ds.index("SET = ["):])
        assert _m, "0.8.24: Void costs use SkyyWorldGen items (%s) but SkyyWorldGen is not in tools/deploy_set.py SET" % wg
        _wj = os.path.join(HERE, "..", "SkyyWorldGen", "SkyyWorldGen-%s.jar" % _m.group(1))
        if os.path.isfile(_wj):
            with zipfile.ZipFile(_wj) as _z:
                _have = set(os.path.basename(n)[:-5] for n in _z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
                for _n in _z.namelist():
                    if _n.startswith("Server/Item/Recipes/") and _n.endswith(".json"):
                        _po = json.loads(_z.read(_n).decode("utf-8-sig")).get("PrimaryOutput") or {}
                        if _po.get("ItemId"):
                            wg_made.add(_po["ItemId"])
            _miss = [i for i in wg if i not in _have]
            if _miss:
                raise SystemExit("0.8.24: the pinned SkyyWorldGen %s jar has no item file for %s" % (_m.group(1), _miss))
            print("Void costs: %s come from the pinned SkyyWorldGen %s (item files present; its recipes make %s)" % (
                ", ".join(wg), _m.group(1), ", ".join(sorted(i for i in wg_made if i in want or i in wg))))
        else:
            print("note: SkyyWorldGen-%s.jar not found - the zone metal cost ids %s were checked against tier_tags.WG_IDS only" % (_m.group(1), wg))
    want = [i for i in want if i not in TT.WG_IDS]
    bad = [i for i in want if i not in ids]
''')
P.rep('''    nosrc = [i for i in want if ('"%s"' % i) not in drops and ('"*%s_State' % i) not in drops and i not in crafted]
''', '''    nosrc = [i for i in want if ('"%s"' % i) not in drops and ('"*%s_State' % i) not in drops and i not in crafted
             and i not in wg_made]   # 0.8.24: + made by a pinned SkyyWorldGen recipe (Bronze = the SkyyAlloy Copper + Iron smelt)
''')
# the default file text: the formula line, the 0.8.24 marker line, the #pd.base template line
P.rep('''    "# The Void (SkyyVoid): space of a category = storage level x pd.perLevel x the rarity multiplier; level L needs pd.step.<Category>",
''', '''    "# The Void (SkyyVoid): space of a category = (pd.base + storage level x pd.perLevel) x the rarity multiplier; level L needs pd.step.<Category>",
''')
P.rep('''    "# SkyySacks 0.8.9 defaults (marker %s): 150 space per level, curve 1.75, Smithing costs leather + bars, Combat costs fabric." % MIG089_MK,
] + (["#pd.perLevel=%d" % PD_PER_LEVEL,''', '''    "# SkyySacks 0.8.9 defaults (marker %s): 150 space per level, curve 1.75, Smithing costs leather + bars, Combat costs fabric." % MIG089_MK,
    "# SkyySacks 0.8.24 defaults (marker %s): every category starts with pd.base space; upgrade costs follow the 15-step tiers." % MIG0824_MK,
] + (["#pd.base=%d" % PD_BASE, "#pd.perLevel=%d" % PD_PER_LEVEL,''')
# SackCfg: the field, its loader, the logged signature, the INFO line
P.rep('''_PD_CFG_FIELDS = (["public static volatile int PD_PER_LEVEL = %d;" % PD_PER_LEVEL,''',
      '''_PD_CFG_FIELDS = (["public static volatile int PD_BASE = %d;" % PD_BASE] + ["public static volatile int PD_PER_LEVEL = %d;" % PD_PER_LEVEL,''')
P.rep('''_PD_LOAD = ['  PD_PER_LEVEL = intKey(p, "pd.perLevel", %d, 1, 100000);' % PD_PER_LEVEL,
''', '''_PD_LOAD = ['  PD_BASE = intKey(p, "pd.base", %d, 0, 1000000);' % PD_BASE,   # 0.8.24
            '  PD_PER_LEVEL = intKey(p, "pd.perLevel", %d, 1, 100000);' % PD_PER_LEVEL,
''')
P.rep('''_PD_SIG = ' + "," + '.join(["PD_PER_LEVEL", "PD_MAX_LEVEL", "PD_CURVE"]''', '''_PD_SIG = ' + "," + '.join(["PD_BASE", "PD_PER_LEVEL", "PD_MAX_LEVEL", "PD_CURVE"]''')
P.rep('''log("[SkyySacks] config: Void - " + PD_PER_LEVEL + " items per storage level (max level "''',
      '''log("[SkyySacks] config: Void - " + PD_BASE + " starting space + " + PD_PER_LEVEL + " items per storage level (max level "''')
# VoidStore.capOf: the ONE space formula (the page's "Space a -> b", the "+N space" per level, the sweep, the bridges all call it)
P.rep('''public static long capOf(int level, int rank) {
  double c = Math.floor((double) level * (double) @PKG@.SackCfg.PD_PER_LEVEL * @PKG@.SackCfg.mult(rank) + 1.0E-6);''',
      '''public static long capOf(int level, int rank) {
  // 0.8.24 (Skyy "you forgot to do the same for the rest of them"): + pd.base, the same starting space for every category
  double base = (double) Math.max(0, @PKG@.SackCfg.PD_BASE);
  double c = Math.floor((base + (double) level * (double) @PKG@.SackCfg.PD_PER_LEVEL) * @PKG@.SackCfg.mult(rank) + 1.0E-6);''')
# the Server Setup row
P.rep('''SACK_CFG_ROWS += [
    _pdrow("pd.perLevel", "Space per storage level",''', '''SACK_CFG_ROWS += [
    # 0.8.24 (Skyy "when you buffed how much the foraging sack holds, you forgot to do the same for the rest of them.")
    _pdrow("pd.base", "Starting space", "void", "int", str(PD_BASE), "0", "1000000", "", "live",
           "Space every category has before levels (x its rarity). Same for all six. 0 = none.", "PD_BASE"),
    _pdrow("pd.perLevel", "Space per storage level",''')
# the 0.8.9 migration's asserts: its NEW values are the 0.8.23 ones (= SackMig0824's old values) where 0.8.24 changed them
P.rep('''for _k, _o, _n, _t in MIG089:
    assert ("#%s=%s" % (_k, _n)) in SACK_CFG_LINES, _k                  # the new default file holds the new value
''', '''for _k, _o, _n, _t in MIG089:
    assert ("#%s=%s" % (_k, _n)) in SACK_CFG_LINES or (_k, _n) in [(m[0], m[1]) for m in MIG0824], _k   # 0.8.24: or SackMig0824 moves it on
''')
# SackMig0824 = SackMig089's code (generated from the same block, names / texts swapped) - built right after SackMig089
_a = P.s.index("MIG089_LINE = ")
_b = P.s.index("}'''), smig))\n\n# ================= 0.7.10: the Workbench tab") + len("}'''), smig))\n")
MIG_SRC = P.s[_a:_b]
assert MIG_SRC.count("smig = pool.makeClass") == 1 and MIG_SRC.count("public static synchronized String run(") == 1
M = MIG_SRC
for o, n in (("MIG089", "MIG0824"), ("SackMig089", "SackMig0824"), ("smig", "smig24"), ("0.8.9", "0.8.24"), ("0.8.8", "0.8.23"),
             ("Smithing costs leather + metal bars, Combat costs fabric (not feathers), 150 space per level",
              "Void upgrade costs on the 15-step tiers (every category also starts with pd.base space)"),
             ("(Smithing costs leather + bars, Combat costs fabric, 150 space per level)", "(Void upgrade costs on the 15-step tiers)"),
             ("(Void costs / space)", "(Void upgrade costs)"), ("Void costs / space update", "Void upgrade costs update")):
    assert o in M, o
    M = M.replace(o, n)
assert "0.8.9" not in M and "0.8.8" not in M and "SackMig089" not in M and M.count('"SkyySacks 0.8.24"') == 1
MIG_NEW = ('''# ================= 0.8.24 SackMig0824: SackMig089's code for the 0.8.23 -> 0.8.24 cost defaults (Skyy "i want the upgrade cost to be fair.
# expensive but manageable"); setup() runs it right after SackMig089 (a pre-0.8.9 file: 0.8.8 -> 0.8.9 -> 0.8.24), before SackCfg.reload
for _k, _o, _n, _t in MIG0824:
    assert ("#%s=%s" % (_k, _n)) in SACK_CFG_LINES, _k                  # the new default file holds the new value
assert sum(1 for l in SACK_CFG_LINES if MIG0824_MK in l) == 1 and [l for l in SACK_CFG_LINES if MIG0824_MK in l][0].startswith("# ")
''' + M)
P.rep('''    @PKG@.SackPool.warn("could not update config.properties for SkyySacks 0.8.9 (Void costs / space; the file is used as it is): " + t);
    return "";
  }
}\'\'\'), smig))
''', '''    @PKG@.SackPool.warn("could not update config.properties for SkyySacks 0.8.9 (Void costs / space; the file is used as it is): " + t);
    return "";
  }
}\'\'\'), smig))
''' + MIG_NEW)
P.rep('''  {PKG}.SackMig089.run({PKG}.SackCfg.FILE);   // 0.8.9: untouched 0.8.8 cost / space defaults -> the new ones, once (History first; Undo)
''', '''  {PKG}.SackMig089.run({PKG}.SackCfg.FILE);   // 0.8.9: untouched 0.8.8 cost / space defaults -> the new ones, once (History first; Undo)
  {PKG}.SackMig0824.run({PKG}.SackCfg.FILE);  // 0.8.24: untouched 0.8.23 Void cost defaults -> the 15-step tier ones, once (History first; Undo)
''')
P.rep('''          smig,   # 0.8.9: SackMig089
''', '''          smig,   # 0.8.9: SackMig089
          smig24,   # 0.8.24: SackMig0824
''')
P.rep('''one item limit per category = level x pd.perLevel x the rarity multiplier;''',
      '''one item limit per category = (pd.base + level x pd.perLevel) x the rarity multiplier;''')
P.rep('''print("Void: %s | level L needs step %s x (L-1)^%g to %d | space = level x %d x %s | gates %s | Pocket %s" % (
    "/".join(PD_CATS), "/".join(str(PD_STEP[c]) for c in PD_CATS), PD_CURVE, PD_MAX_LEVEL, PD_PER_LEVEL,''',
      '''print("Void: %s | level L needs step %s x (L-1)^%g to %d | space = (%d + level x %d) x %s | gates %s | Pocket %s" % (
    "/".join(PD_CATS), "/".join(str(PD_STEP[c]) for c in PD_CATS), PD_CURVE, PD_MAX_LEVEL, PD_BASE, PD_PER_LEVEL,''')
P.rep('''"live,adv", "Items it takes - itemId:amount pairs, commas between. A log id counts its whole wood tier.",''',
      '''"live,adv", "Items it takes - itemId:amount pairs, commas between. A log id counts its whole tree tier.",''')

# ---- 5. RecipeCmp: tools/tier_tags.py TT_VERSION 3 (+ the Mushroom family)
P.rep('''def _tt_grp(i):
    f = TT.family(i)
    if f == "crop":
        return i[len("Plant_Crop_"):-len("_Item")], 0
''', '''def _tt_grp(i):
    f = TT.family(i)
    # 0.8.24 (TT_VERSION 3): the 15th crop Mushroom - its cap (Plant_Crop_Mushroom_Cap_Brown) and spores group as one crop family
    if i in [_m[0] for _m in TT.MUSHROOM_ROWS]:
        return "Mushroom", (0 if f == "crop" else (3 if "Eternal" in i else 2))
    if f == "crop":
        return i[len("Plant_Crop_"):-len("_Item")], 0
''')
P.rep('''assert TT.TT_VERSION == "2" and TT.tier("Ingredient_Bar_Thorium") == 4 and len(TT.LADDER) == 16, "0.8.22: tools/tier_tags.py = the 15-step ladder"
''', '''# 0.8.24: TT_VERSION 3 (20 levels per zone; the metal numbers are unchanged, logs / crops on their own 15-step ladders)
assert TT.TT_VERSION == "3" and TT.tier("Ingredient_Bar_Thorium") == 4 and len(TT.LADDER) == 16, "0.8.24: tools/tier_tags.py = TT_VERSION 3"
assert TT.tier("Wood_Maple_Trunk") == 3 and TT.tier("Plant_Crop_Turnip_Item") == 6 and TT.tier("Plant_Crop_Mushroom_Cap_Brown") == 15
assert _tt_grp("Plant_Seeds_Mushroom") == ("Mushroom", 2) and _tt_grp("Plant_Spores_Mushroom_Eternal") == ("Mushroom", 3) and \\
    _tt_grp("Plant_Crop_Mushroom_Cap_Brown") == ("Mushroom", 0)
''')

# ---- 6. (Collections 0.2.28 hand-off) the Furnace tab's SkyyAlloy rows respect recipe knowledge (KnowSync.allowed, as the instant tabs do):
# SkyyWorldGen 0.7.5's Enchanted smelts Alloy_Ench_<Alloy> stay locked until SkyyCollections grants them (both input collections at VI; it
# flags them KnowledgeRequired at run time and teaches the output id). An Alloy_Ench_ id counts as KnowledgeRequired here even without that
# flag (no SkyyCollections = locked, never free). Plain alloys (no knowledge) keep only the Furnace Charm gate.
P.rep('''# 0.7.3: tab ids are A:craft / A:smith / A:farm / P:<bench> / C: only''', '''# 0.8.24: may this player smelt this alloy row? true = not an alloy, or a plain alloy (no knowledge); an Enchanted alloy smelt
# (Alloy_Ench_<Alloy>, SkyyWorldGen 0.7.5) or any knowledge-flagged alloy only once KnowSync.allowedOut says the player knows its output
cpg.addMethod(CtNewMethod.make(f"""
public static boolean alloyOk({CRR} r, java.util.Set known, java.util.Set coll) {{
  if (r == null || {PKG}.ProcBench.alloyNeed(r) <= 0) return true;
  String rid = String.valueOf(r.getId());
  boolean kr = r.isKnowledgeRequired() || rid.startsWith("Alloy_Ench_");
  if (!kr) return true;
  {MQ} po = r.getPrimaryOutput();
  return {PKG}.KnowSync.allowedOut(true, po == null ? null : po.getItemId(), rid, known, coll);
}}""", cpg))
# 0.7.3: tab ids are A:craft / A:smith / A:farm / P:<bench> / C: only''')
P.rep('''  if (aneed > {PKG}.ProcBench.smelt(k)[0]) return''', '''  if (aneed > 0) {{   // 0.8.24: an Enchanted alloy smelt needs its collections first (KnowSync, as the other tabs)
    java.util.UUID au = null;
    try {{ au = java.util.UUID.fromString(k.substring(0, 36)); }} catch (Throwable ta) {{ au = null; }}
    if (!alloyOk(r, {PKG}.KnowSync.known(p), au == null ? new java.util.HashSet() : collectionRecipes(au)))
      return "your collections unlock this smelt (see /collections) - nothing was taken";
  }}
  if (aneed > {PKG}.ProcBench.smelt(k)[0]) return''')
P.rep('''    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (@PKG@.ProcBench.alloyNeed(r0) > ctier) l0 = 0;   // 0.8.20: a locked alloy is never "can make"''', '''    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (@PKG@.ProcBench.alloyNeed(r0) > ctier) l0 = 0;   // 0.8.20: a locked alloy is never "can make"
    if (!alloyOk(r0, aKnown, aColl)) l0 = 0;   // 0.8.24: nor an Enchanted alloy smelt the collections have not unlocked''')
P.rep('''    if (aneed > ctier) { lim = 0; lockNote = " - Furnace Charm T" + aneed + " unlocks this"; }   // 0.8.20: greyed, no buttons''',
      '''    if (!alloyOk(r, aKnown, aColl)) { lim = 0; lockNote = " - your collections unlock this (/collections)"; }   // 0.8.24: greyed, no buttons
    else if (aneed > ctier) { lim = 0; lockNote = " - Furnace Charm T" + aneed + " unlocks this"; }   // 0.8.20: greyed, no buttons''')
_bp = P.s.index("public void buildProc(@UCB@ b, @UEB@ ev, @PLA@ p, java.util.UUID u, String k) {")
_fp = P.s.index("  this.fuelPick = false;\n  boolean only = Boolean.TRUE.equals(ONLY.get(u));\n", _bp)
assert _fp < P.s.index('if (!alloyOk(r0, aKnown, aColl)) l0 = 0;')
_seg = P.s[_fp:P.s.index('if (!alloyOk(r0, aKnown, aColl)) l0 = 0;')]
P.rep(_seg, _seg.replace("  this.fuelPick = false;\n", '''  this.fuelPick = false;
  java.util.Set aKnown = @PKG@.KnowSync.known(p);       // 0.8.24: once per page, for the alloy rows
  java.util.HashSet aColl = collectionRecipes(u);
''', 1))

# ---- 7. (Collections 0.2.28 hand-off) the 6 Enchanted alloys (tools/skyyench.py TABLE_ALLOYS: Skyy_Ench_Bronze / Dusk / Azurvane / Cinder /
# Lumen / Electrum) get a Void home: MINING, their TABLE_ALLOYS category (like every other Enchanted metal; the Bazaar tab matches).
P.rep('''defs.addMethod(CtNewMethod.make(EN.sacks_home_java(), defs))
''', '''# 0.8.24: + the 6 Enchanted alloys (TABLE_ALLOYS, SkyyCollections 0.2.28) -> their own category column (Mining, like the other Enchanted metals)
ALLOY_ENCH = [EN.PREFIX + _t[0] for _t in EN.TABLE_ALLOYS]
assert ALLOY_ENCH == ["Skyy_Ench_" + _w for _w in ("Bronze", "Dusk", "Azurvane", "Cinder", "Lumen", "Electrum")] and not set(ALLOY_ENCH) & set(EN.IDS)
assert [_t[5] for _t in EN.TABLE_ALLOYS] == ["Mining"] * 6 and EN.cat_of("Skyy_Ench_Copper") == "Mining"
_HOME_TABLE = list(EN.TABLE) + list(EN.TABLE_ALLOYS)
defs.addMethod(CtNewMethod.make(EN._home_java(EN.IDS + ALLOY_ENCH, _HOME_TABLE), defs))
_cj = os.path.join(HERE, "..", "SkyyCollections", "SkyyCollections-0.2.28.jar")
if os.path.isfile(_cj):
    import zipfile as _azf
    with _azf.ZipFile(_cj) as _z:
        _ci = set(os.path.basename(n)[:-5] for n in _z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    assert set(ALLOY_ENCH) <= _ci, "0.8.24: SkyyCollections 0.2.28 has no item file for %s" % sorted(set(ALLOY_ENCH) - _ci)
    print("Enchanted alloys -> Mining: %s (all in SkyyCollections 0.2.28)" % ", ".join(ALLOY_ENCH))
else:
    print("note: SkyyCollections-0.2.28.jar not found - the Enchanted alloy ids were taken from tools/skyyench.py TABLE_ALLOYS only")
''')

# ---- 8. (SkyyArmory 0.1.38 Soul Cage hand-off; docs/answered/gear.md 2026-10-18 popup "Use the worst one (Recommended)") WORST FIRST:
# a recipe input that is a RESOURCE TYPE matched by rolled gear (a stack with a SkyyGear document - Armory 0.1.38's SkyyArmory_Any_<SoulOrb /
# SoulCage_metal> types) takes the LOWEST rarity first, then the lowest level ("lvl"), then slot order; plain / unrolled stacks count as the
# lowest. No Gear bridge answers rarity, so the SkyyGear document is read (key "SkyyGear": "r" rarity id, "lvl"). Only resource inputs that
# match at least one rolled stack go this way; everything else is the engine's removeMaterials as before. Exactly the needed whole items are
# taken; a take that cannot finish puts every stack back as it was (same object) and nothing else is removed.
P.rep('''# review fix (instant crafts): what is left of the literally removed items `took` after paying `done` crafts of `inputs` (per[i] each), or''',
      '''# 0.8.24 WORST FIRST (Skyy popup "Use the worst one"): the rank of a rolled gear stack - -1 = plain / unrolled / no SkyyGear document (the
# lowest), else rarity rank x 100000 + level. Rarity ranks by worth (Gear's R_ID order is not): normal, unique, rare, set, legendary, fabled,
# untiered, mythic; an unknown rarity id = normal.
cpg.addMethod(CtNewMethod.make("""
public static int gearRank(String r) {
  if (r == null) return 0;
  String x = r.trim().toLowerCase();
  if (x.equals("unique")) return 1;
  if (x.equals("rare")) return 2;
  if (x.equals("set")) return 3;
  if (x.equals("legendary")) return 4;
  if (x.equals("fabled")) return 5;
  if (x.equals("untiered")) return 6;
  if (x.equals("mythic")) return 7;
  return 0;
}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static long wear({IS} it) {{
  if (it == null || it.isEmpty()) return -1L;
  try {{
    org.bson.BsonDocument md = it.getMetadata();
    if (md == null || md.isEmpty()) return -1L;
    org.bson.BsonValue g = md.get("SkyyGear");
    if (g == null || !g.isDocument()) return -1L;
    org.bson.BsonDocument d = g.asDocument();
    org.bson.BsonValue rv = d.get("r");
    int r = gearRank(rv != null && rv.isString() ? rv.asString().getValue() : null);
    org.bson.BsonValue lv = d.get("lvl");
    long l = lv != null && lv.isNumber() ? (long) lv.asNumber().intValue() : 0L;
    if (l < 0L) l = 0L;
    if (l > 99999L) l = 99999L;
    return (long) r * 100000L + l;
  }} catch (Throwable t) {{ return -1L; }}
}}""", cpg))
# the slots of c a resource-type input takes from, worst first (stable: equal ranks keep slot order); null = no rolled stack matches (the
# engine's own order stays)
cpg.addMethod(CtNewMethod.make(f"""
public static short[] worstSlots({IC} c, {MQ} mq) {{
  if (c == null || mq == null || mq.getItemId() != null || mq.getResourceTypeId() == null) return null;
  String rt = mq.getResourceTypeId();
  short cap = c.getCapacity();
  short[] s = new short[cap];
  long[] w = new long[cap];
  int n = 0;
  boolean gear = false;
  for (short i = 0; i < cap; i++) {{
    {IS} it = c.getItemStack(i);
    if (it == null || it.isEmpty() || it.getItemId() == null) continue;
    if (mq.isItemExcluded(it.getItemId()) || rtUnits(it.getItemId(), rt) <= 0) continue;
    long v = wear(it);
    if (v >= 0L) gear = true;
    s[n] = i;
    w[n] = v;
    n++;
  }}
  if (!gear) return null;
  for (int a = 1; a < n; a++) {{
    short ks = s[a];
    long kw = w[a];
    int b = a - 1;
    while (b >= 0 && w[b] > kw) {{ s[b + 1] = s[b]; w[b + 1] = w[b]; b--; }}
    s[b + 1] = ks;
    w[b + 1] = kw;
  }}
  short[] out = new short[n];
  for (int i = 0; i < n; i++) out[i] = s[i];
  return out;
}}""", cpg))
# take the rolled-gear resource inputs worst first from c; the answer = the inputs left for the engine (in order), or null = a take could not
# finish (every stack it touched is back as it was - nothing taken)
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.List takeWorst({IC} c, java.util.List inputs) {{
  java.util.ArrayList rest = new java.util.ArrayList();
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList ui = new java.util.ArrayList();
  boolean ok = true;
  for (int q = 0; ok && inputs != null && q < inputs.size(); q++) {{
    {MQ} mq = ({MQ}) inputs.get(q);
    short[] ws = worstSlots(c, mq);
    if (ws == null) {{ rest.add(mq); continue; }}
    long need = (long) mq.getQuantity();
    for (int j = 0; ok && j < ws.length && need > 0L; j++) {{
      {IS} it = c.getItemStack(ws[j]);
      if (it == null || it.isEmpty()) continue;
      int un = rtUnits(it.getItemId(), mq.getResourceTypeId());
      if (un <= 0) un = 1;
      long wantI = (need + (long) un - 1L) / (long) un;
      int take = wantI < (long) it.getQuantity() ? (int) wantI : it.getQuantity();
      us.add(Short.valueOf(ws[j]));
      ui.add(it);
      {ISS} tx = c.removeItemStackFromSlot(ws[j], take);
      int got = 0;
      if (tx != null && tx.succeeded()) {{ {IS} rem = tx.getRemainder(); got = take - (rem == null ? 0 : rem.getQuantity()); }}
      if (got != take) ok = false;
      need -= (long) got * (long) un;
    }}
    if (need > 0L) ok = false;
  }}
  if (ok) return rest;
  for (int i = us.size() - 1; i >= 0; i--) c.setItemStackForSlot(((Short) us.get(i)).shortValue(), ({IS}) ui.get(i));
  return null;
}}""", cpg))
# review fix (instant crafts): what is left of the literally removed items `took` after paying `done` crafts of `inputs` (per[i] each), or''')
# procQueue + craftOne: the worst-first take, then the engine for the rest
P.rep('''    Object tx = mats.removeMaterials(inputs);
    boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();''',
      '''    java.util.List restIn = takeWorst(mats, inputs);   // 0.8.24: rolled gear by resource type - the worst first (Skyy "Use the worst one")
    Object tx = (restIn == null || restIn.isEmpty()) ? null : mats.removeMaterials(restIn);
    boolean flag = restIn != null && (restIn.isEmpty() || (tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded()));''')
P.rep('''  Object tx = mats.removeMaterials(inputs);
  boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();''',
      '''  java.util.List restIn = takeWorst(mats, inputs);   // 0.8.24: rolled gear by resource type - the worst first (Skyy "Use the worst one")
  Object tx = (restIn == null || restIn.isEmpty()) ? null : mats.removeMaterials(restIn);
  boolean flag = restIn != null && (restIn.isEmpty() || (tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded()));''')
# sacks:fn:craftHave / craftPay: the copy also holds the ROLLED gear stacks a resource-type input of the recipe matches (the stack itself, its
# document kept), so "1 / 1" shows and the payment takes the worst one; every other stack with metadata stays out as before
P.rep('''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] plainCopy(@IC@[] cs) {
  int n = 0;''', '''# 0.8.24: plainCopyFor(cs, r) = plainCopy + the rolled gear stacks (CraftPage.wear >= 0) a resource-type input of r matches, copied as they
# are (pcp[4] boolean[] = such a slot); r null = plainCopy exactly
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean gearFor(@CRR@ r, @IS@ it) {
  if (r == null || it == null || it.isEmpty() || it.getItemId() == null || @PKG@.CraftPage.wear(it) < 0L) return false;
  @MQ@[] in = r.getInput();
  for (int i = 0; in != null && i < in.length; i++) {
    if (in[i] == null || in[i].getItemId() != null || in[i].getResourceTypeId() == null) continue;
    if (!in[i].isItemExcluded(it.getItemId()) && @PKG@.CraftPage.rtUnits(it.getItemId(), in[i].getResourceTypeId()) > 0) return true;
  }
  return false;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] plainCopyFor(@IC@[] cs, @CRR@ r) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) if (cs[c] != null) n += cs[c].getCapacity();
  if (n < 1) n = 1;
  @SIC@ copy = new @SIC@((short) n);
  int[] ci = new int[n];
  short[] si = new short[n];
  int[] q0 = new int[n];
  boolean[] mt = new boolean[n];
  for (int i = 0; i < n; i++) ci[i] = -1;
  int at = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      int here = at;
      at++;
      if (it == null || it.isEmpty() || it.getItemId() == null) continue;
      if (@PKG@.SweepTask.plainFresh(it)) copy.setItemStackForSlot((short) here, new @IS@(it.getItemId(), it.getQuantity()));
      else if (gearFor(r, it)) { copy.setItemStackForSlot((short) here, it); mt[here] = true; }
      else continue;
      ci[here] = c;
      si[here] = s;
      q0[here] = it.getQuantity();
    }
  }
  return new Object[] { copy, ci, si, q0, mt };
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] plainCopy(@IC@[] cs) {
  if (cs != null) return plainCopyFor(cs, (@CRR@) null);
  int n = 0;''')
# applyCopy: + the rolled stacks it takes (whole) recorded for an exact refund
P.rep('''public static String applyCopy(Object[] pcp, @IC@[] cs) {
  @SIC@ copy = (@SIC@) pcp[0];''', '''public static String applyCopyM(Object[] pcp, @IC@[] cs, java.util.ArrayList metaOut) {
  @SIC@ copy = (@SIC@) pcp[0];
  boolean[] mt = null;
  if (pcp.length > 4) mt = (boolean[]) pcp[4];   // (javassist: no array ?: null)''')
P.rep('''    if (real == null || real.isEmpty() || real.getQuantity() < d) return "your inventory changed during the payment - nothing was taken";
    @ISS@ tx = c.removeItemStackFromSlot(si[i], d);''', '''    if (real == null || real.isEmpty() || real.getQuantity() < d) return "your inventory changed during the payment - nothing was taken";
    if (mt != null && mt[i] && metaOut != null) {   // 0.8.24: a rolled stack - refunded as itself (only whole stacks: gear does not stack)
      if (d != real.getQuantity()) return "a rolled item would be split - nothing was taken";
      metaOut.add(real);
    }
    @ISS@ tx = c.removeItemStackFromSlot(si[i], d);''')
P.rep('''  return null;
}""".replace("@ISS@", ISS)), sbr))
''', '''  return null;
}""".replace("@ISS@", ISS)), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String applyCopy(Object[] pcp, @IC@[] cs) {
  return applyCopyM(pcp, cs, (java.util.ArrayList) null);
}"""), sbr))
''')
P.rep('''  @CIC@ mats = payView(p, k, r, (@SIC@) plainCopy(payConts(p.getInventory()))[0]);''',
      '''  @CIC@ mats = payView(p, k, r, (@SIC@) plainCopyFor(payConts(p.getInventory()), r)[0]);   // 0.8.24: + rolled gear for resource inputs''')
# metaTouched: the rolled stacks the copy held may change (they are the payment); any other stack with metadata still refuses
P.rep('''# true when a stack WITH metadata (rolled gear, a named item, a filled container) changed since the snapshot''',
      '''# 0.8.24: metaTouched, but the slots plainCopyFor copied as rolled gear (pcp[4]) may change - they are what the payment takes
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean metaTouchedM(@IC@[] cs, java.util.ArrayList snap, Object[] pcp) {
  int[] ci = (int[]) pcp[1];
  short[] si = (short[]) pcp[2];
  boolean[] mt = null;
  if (pcp.length > 4) mt = (boolean[]) pcp[4];   // (javassist: no array ?: null)
  for (int c = 0; c < cs.length; c++) {
    @IS@[] a = (@IS@[]) snap.get(c);
    if (a == null || cs[c] == null) continue;
    for (short s = 0; s < a.length; s++) {
      @IS@ was = a[s];
      if (was == null || was.isEmpty()) continue;
      org.bson.BsonDocument md = was.getMetadata();
      if (md == null || md.isEmpty()) continue;
      boolean ok = false;
      for (int i = 0; mt != null && i < mt.length && !ok; i++) if (mt[i] && ci[i] == c && si[i] == s) ok = true;
      if (ok) continue;
      if (!sameStack(was, cs[c].getItemStack(s))) return true;
    }
  }
  return false;
}"""), sbr))
# true when a stack WITH metadata (rolled gear, a named item, a filled container) changed since the snapshot''')
P.rep('''  Object[] pcp = plainCopy(cs);
  @SIC@ copy = (@SIC@) pcp[0];''', '''  Object[] pcp = plainCopyFor(cs, r);   // 0.8.24: + the rolled gear a resource input matches (worst first below)
  @SIC@ copy = (@SIC@) pcp[0];''')
P.rep('''    try { mats.removeMaterials(inputs); } catch (Throwable t0) { @PKG@.SackPool.warn("craft bridge: removeMaterials threw (checked below): " + t0); }''',
      '''    java.util.List restIn = @PKG@.CraftPage.takeWorst(mats, inputs);   // 0.8.24: rolled gear by resource type - the worst first
    if (restIn == null) throw new IllegalStateException("the worst-first take could not finish");   // -> rolled back below, nothing taken
    if (!restIn.isEmpty()) {
      try { mats.removeMaterials(restIn); } catch (Throwable t0) { @PKG@.SackPool.warn("craft bridge: removeMaterials threw (checked below): " + t0); }
    }''')
P.rep('''    String moved = applyCopy(pcp, cs);   // the copy's losses -> the real inventory slots (read back)''',
      '''    String moved = applyCopyM(pcp, cs, metaT);   // the copy's losses -> the real inventory slots (read back); 0.8.24: rolled ones recorded''')
P.rep('''    else if (metaTouched(cs, snap)) bad = "a stack with extra data (rolled gear or a named item) would be used - nothing was taken";''',
      '''    else if (metaTouchedM(cs, snap, pcp)) bad = "a stack with extra data (rolled gear or a named item) would be used - nothing was taken";''')
P.rep('''  java.util.LinkedHashMap bagT = new java.util.LinkedHashMap();
  String bad = null;
  boolean synced = false;''', '''  java.util.LinkedHashMap bagT = new java.util.LinkedHashMap();
  java.util.ArrayList metaT = new java.util.ArrayList();   // 0.8.24: the rolled stacks paid (refunded as themselves)
  String bad = null;
  boolean synced = false;''')
P.rep('''  RECEIPTS.put(rc, new Object[] { u, k, invT, bagT, new long[] { now, 0L }, rid });''',
      '''  RECEIPTS.put(rc, new Object[] { u, k, invT, bagT, new long[] { now, 0L }, rid, metaT });   // 0.8.24: + [6] the rolled stacks''')
# craftRefund: the rolled stacks go back as themselves first (their count leaves the by-id refund)
P.rep('''  @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();
  java.util.Iterator ii = invT.entrySet().iterator();''', '''  @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();
  if (e.length > 6 && e[6] instanceof java.util.ArrayList) {   // 0.8.24: a rolled item comes back with its document, not as a fresh stack
    java.util.ArrayList mts = (java.util.ArrayList) e[6];
    invT = new java.util.LinkedHashMap(invT);
    for (int i = 0; i < mts.size(); i++) {
      @IS@ s0 = (@IS@) mts.get(i);
      if (s0 == null || s0.isEmpty()) continue;
      addCount(invT, s0.getItemId(), -s0.getQuantity());
      total += (long) s0.getQuantity();
      int b0 = @PKG@.CraftPage.countItem(c, s0.getItemId());
      c.addItemStack(s0);
      if (@PKG@.CraftPage.countItem(c, s0.getItemId()) - b0 >= s0.getQuantity()) continue;
      try {
        @PR@ pr = @UNI@.get().getPlayer(u);
        @REF@ rf = pr.getReference();
        @SIC@.addOrDropItemStack(rf.getStore(), rf, c, s0);
        try { @PKG@.CraftLog.later(k, "CRAFT-REFUND-SPILL " + s0.getItemId() + " (rolled) dropped at the player (inventory full)"); } catch (Throwable t3) { }
      } catch (Throwable t) {
        @PKG@.SackPool.warn("craft refund: a rolled " + s0.getItemId() + " did not fit and could not be dropped for " + u + " - LOST, give it back by hand: " + t);
      }
    }
  }
  java.util.Iterator ii = invT.entrySet().iterator();''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.24 adds no system / command"
assert P.s.count("SackMig0824.run(") == 1 and P.s.count('pool.makeClass(PKG + ".SackMig0824")') == 1
P.finish()
