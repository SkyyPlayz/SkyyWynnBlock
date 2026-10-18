"""Test tools/tier_tags.py (research/Tier-Tags-Plan.md round T0).   python tools/test_tier_tags.py   (exit 0 = PASS)

Checks: the ladder + display = internal + 1; the plan's tier for sample ids of every family; family counts (plan 1.2); every vanilla id in
the table exists in Assets.zip (the cached copy, tools/serverjar.py - read-only; skipped with a note when no copy exists); the Enchanted
rows = tools/skyyench.py TABLE (minus Cobblestone / Rubble) at their base's tier; TOOL_METALS = SkyyGear's TOOL_TIERS + 1 (the SET pin's
build script, read as text); the band rule; the tag / described() format.
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
ok(TT.LADDER == ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"), "ladder")
ok([TT.display(i) for i in range(8)] == list(range(1, 9)), "display = internal + 1")
ok([TT.to_internal(d) for d in range(1, 9)] == list(range(8)), "to_internal")
ok(TT.tag_text(3) == "T3 Iron" and TT.tag_text(1) == "T1 Crude" and TT.tag_text(8) == "T8 Onyxium", "tag_text")
ok(TT.ladder_tag(2, "Totem") == "T2 Totem" and TT.ladder_tag(3, "Loot") == "T3 Loot" and TT.ladder_tag(2, "Bench") == "T2 Bench", "ladder_tag")
ok(TT.ladder_tag(3, "Charm") == "T3 Charm" and TT.ladder_tag(5, "Charm") == "T5 Charm", "ores01: the Furnace Charm ladder word")
for bad in (lambda: TT.display(8), lambda: TT.to_internal(0), lambda: TT.ladder_tag(2, "Gem")):
    try:
        bad()
        FAILS.append("an out-of-range call did not raise")
    except AssertionError:
        pass

# ---- the plan's samples (popup: "Match the tool": Copper ore / Oak / Wheat = T2, T1 = Crude / wood starters)
SAMPLES = {
    "Ore_Copper": "T2 Copper", "Ore_Iron": "T3 Iron", "Ore_Onyxium": "T8 Onyxium", "Ingredient_Bar_Bronze": "T3 Iron",
    "Ingredient_Bar_Copper": "T2 Copper", "Ingredient_Bar_Mithril": "T7 Mithril",
    "Wood_Oak_Trunk": "T2 Copper", "Wood_Apple_Trunk": "T2 Copper", "Wood_Maple_Trunk": "T3 Iron", "Wood_Dry_Trunk": "T4 Thorium",
    "Wood_Redwood_Trunk": "T5 Cobalt", "Wood_Sallow_Trunk": "T6 Adamantite", "Wood_Fig_Blue_Trunk": "T6 Adamantite",
    "Plant_Crop_Wheat_Item": "T2 Copper", "Plant_Crop_Carrot_Item": "T3 Iron", "Plant_Crop_Potato_Item": "T8 Onyxium",
    "Plant_Seeds_Wheat": "T2 Copper", "Plant_Seeds_Onion_Eternal": "T8 Onyxium",
    "Skyy_Ench_Copper": "T2 Copper", "Skyy_Ench_Oak": "T2 Copper", "Skyy_Ench_Wheat": "T2 Copper", "Skyy_Ench_Potato": "T8 Onyxium",
    "Skyy_Ench_Adamantite": "T6 Adamantite", "Skyy_Ench_Sallow": "T6 Adamantite",
    "Tool_Pickaxe_Crude": "T1 Crude", "Tool_Pickaxe_Wood": "T1 Crude", "Tool_Hoe_Copper": "T2 Copper", "Tool_Pickaxe_Scrap": "T2 Copper",
    "Tool_Sickle_Steel_Rusty": "T3 Iron", "Tool_Hatchet_Onyxium": "T8 Onyxium",
    "Weapon_Staff_Wood": "T1 Crude", "Weapon_Wand_Tribal": "T3 Iron", "Weapon_Staff_Onyxium": "T8 Onyxium",
}
for i, want in SAMPLES.items():
    ok(TT.tag_for(i) == want, "tag_for(%s) = %r, want %r" % (i, TT.tag_for(i), want))
for i in ("Skyy_Ench_Cobblestone", "Skyy_Ench_Rubble", "Ore_Silver", "Ore_Gold", "Ore_Prisma", "Ingredient_Bar_Gold", "Rock_Stone_Cobble",
          "Rock_Gem_Ruby", "Ingredient_Bone_Fragment", "Ingredient_Hide_Soft", "Ingredient_Hide_Prismic",
          "Ingredient_Leather_Soft", "Ingredient_Leather_Heavy", "Plant_Seeds_Oak", "Ore_Copper_Stone", ""):
    ok(TT.tag_for(i) is None and TT.tier(i) is None and TT.owner(i) is None, "%s must stay untagged" % i)
ok(TT.internal("Ore_Copper") == 1 and TT.internal("Tool_Pickaxe_Crude") == 0, "internal()")

# ---- described()
ok(TT.described("Ore_Copper", "Can be smelted.") == "T2 Copper - Can be smelted.", "described with text")
ok(TT.described("Plant_Crop_Wheat_Item", "") == "T2 Copper" and TT.described("Plant_Crop_Wheat_Item") == "T2 Copper", "described without text")
ok(TT.described("Wood_Oak_Trunk", "  x  ") == "T2 Copper - x", "described trims")

# ---- counts (plan 1.2)
# ores01 (SkyyWorldGen 0.7.3): + 4 zone ore blocks / raw ores / ingots + 4 alloys (owner SkyyWorldGen); the Enchanted ingots of the new
# metals (tools/skyyench.py TABLE_ORES, SkyyCollections 0.2.25) take their base's tier -> enchanted 55 + those rows
ENCH_ORES = [t for t in getattr(EN, "TABLE_ORES", []) if t[2] in TT.ROWS]
COUNTS = {"ore": 7, "bar": 8, "log": 34, "crop": 14, "seed": 28, "enchanted": 55 + len(ENCH_ORES), "tool": 34, "armory": 11,
          "can": 6, "harvester": 4, "zone_ore_block": 4, "zone_ore": 4, "zone_bar": 4, "alloy": 5,
          "mining_armor": 32}          # SkyyGear 0.3.21: the zone Mining sets (Lead .. Lumen x 4 slots, TT.OWN_IDS); tools01: enchanted 17 -> 18 (+ the Enchanted Stick); C1 (SkyyCollections 0.2.21): 18 -> 55 (37 own items on a tiered base); SkyyGear 0.3.12: its OWN watering can + Harvester ladders (TT.OWN_IDS, not in Assets.zip)
for f, n in COUNTS.items():
    ok(len(TT.ids_in(f)) == n, "family %s has %d ids, want %d" % (f, len(TT.ids_in(f)), n))
ok(set(TT.families()) == set(COUNTS), "families: %s" % TT.families())
ok(len(TT.ids_for("SkyyCollections")) == 7 + 8 + 34 + 14 + 28 + 55 + len(ENCH_ORES), "SkyyCollections owns %d" % len(TT.ids_for("SkyyCollections")))
ok(TT.ids_for("SkyyGear") == sorted(TT.ids_in("tool") + TT.ids_in("can") + TT.ids_in("harvester") + TT.ids_in("mining_armor")) and TT.ids_for("SkyyArmory") == TT.ids_in("armory"), "owners")
ok(sorted(TT.OWN_IDS) == sorted(TT.ids_in("can") + TT.ids_in("harvester") + TT.ids_in("mining_armor")) and TT.tag_for("Tool_WaterCan_Crude") == "T1 Crude"
   and TT.tag_for("Tool_WaterCan_Iron") == "T3 Iron" and TT.tag_for("Tool_WaterCan_Adamantite") == "T6 Adamantite"
   and TT.tag_for("Tool_Sickle_Harvester_Thorium") == "T4 Thorium", "SkyyGear 0.3.12 own ids: the can T1 Crude .. T6 Adamantite, the Harvester .. T4 Thorium")
ok(all(r[2] in TT.OWNERS and 1 <= r[0] <= 8 for r in TT.ROWS.values()), "rows in range")

# ---- ores01: the zone metals (research/Zone-Ores-Alloys-Spec.md 2.3 / 2.5 / 3; Skyy's Q6 default "T4 Lead", "T5 Chromium", "T6 Slag", "T7 Titanium")
ZM = {"Lead": (4, "Sandstone", "Thorium"), "Chromium": (5, "Shale", "Cobalt"), "Slag": (6, "Volcanic", "Adamantite"), "Titanium": (7, "Basalt", "Mithril")}
AL = {"Dusk": (4, "Thorium", "Lead"), "Azurvane": (5, "Cobalt", "Chromium"), "Cinder": (6, "Adamantite", "Slag"), "Lumen": (7, "Mithril", "Titanium"), "Electrum": (3, "Bronze", "Silver")}   # Electrum = the Bronze tier (Gold / Silver untagged)
want_wg = []
for m, (t, h, partner) in ZM.items():
    for i in ("Ore_%s_%s_SkyWynn" % (m, h), "Ore_%s_SkyWynn" % m, "Ingredient_Bar_%s_SkyWynn" % m):
        want_wg.append(i)
        ok(TT.tag_for(i) == "T%d %s" % (t, m) and TT.word(i) == m and TT.tier(i) == TT.tier("Ore_" + partner), "%s: %s (partner %s T%s)" % (i, TT.tag_for(i), partner, TT.tier("Ore_" + partner)))
        ok(TT.described(i, "x") == "T%d %s - x" % (t, m), "%s described()" % i)
for a, (t, x, y) in AL.items():
    i = "Ingredient_Bar_%s_SkyWynn" % a
    want_wg.append(i)
    ok(TT.tag_for(i) == "T%d %s" % (t, a) and TT.family(i) == "alloy" and TT.tier(i) == TT.tier("Ingredient_Bar_" + x), "%s: %s" % (i, TT.tag_for(i)))
ok(sorted(want_wg) == TT.ids_for("SkyyWorldGen") == sorted(TT.WG_IDS) and len(TT.WG_IDS) == 17, "SkyyWorldGen owns exactly the 17 zone-metal ids (+ Electrum)")
ok(all(i.endswith("_SkyWynn") for i in TT.WG_IDS), "every SkyyWorldGen id ends _SkyWynn")
ok(TT.tag_for("Ingredient_Bar_Bronze") == "T3 Iron" and TT.owner("Ingredient_Bar_Bronze") == "SkyyCollections", "vanilla Bronze unchanged (T3, Collections' key)")
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

# ---- band rule
for lv, want in ((0, 1), (5, 1), (9, 1), (10, 2), (14, 2), (15, 3), (20, 4), (25, 5), (30, 5), (34, 5), (35, 6), (40, 7), (60, 7)):
    ok(TT.tier_for_level(lv) == want, "tier_for_level(%d) = %d, want %d" % (lv, TT.tier_for_level(lv), want))
ok(TT.tier_for_level(40, "Weapon_Sword_Onyxium") == 8, "Onyxium id = T8")

# ---- TOOL_METALS = SkyyGear TOOL_TIERS + 1 (the SET pin's build script, text only)
try:
    import deploy_set
    gv = dict(deploy_set.SET)["SkyyGear"]
    gsrc = open(os.path.join(ROOT, "SkyyGear", "build_skyygear_%s.py" % gv), encoding="utf8").read()
    m = re.search(r"^TOOL_TIERS = (\[.*?\])\s*$", gsrc, re.M | re.S)
    gear = ast.literal_eval(m.group(1))
    ok([(w, t + 1) for w, t in gear] == list(TT.TOOL_METALS), "TOOL_METALS != SkyyGear %s TOOL_TIERS + 1: %s" % (gv, gear))
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
    vanilla = [i for i in TT.ROWS if not i.startswith("Skyy_") and i not in TT.OWN_IDS and i not in TT.WG_IDS]   # OWN_IDS: SkyyGear's build; WG_IDS: SkyyWorldGen's
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
