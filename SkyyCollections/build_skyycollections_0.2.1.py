"""SkyyCollections 0.2.1 - build script (derived from 0.2 by tools/coll_0_2_1_patch.py - edit the patch, not this file; 0.2 was
written fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything
else follows research/Collections-Spec.md).

0.2.1: felled logs + "No tier yet" (feedback round 2), nothing else.
  - coll:fn:add accepts the source skills:felled by default (research/Tree-Fall-Spec.md 3.2): SkyySkills 0.4.2 credits every log
    that falls when its player cuts a tree. loadConfig adds it to bridge.add.sources unless bridge.add.felled=false (false also
    removes it when listed), so existing config files gain it without a rewrite. Caps and the profile check apply as before.
  - A collection without a tier shows "No tier yet" instead of "Tier -" (category card + collection page header).

0.2: SkyBlock-style ITEM collections (Skyy 2026-09-23: "we track the items you collect, not the broken item").
  Counting (spec section 3, hooks verified in HytaleServer.jar):
  - H1 CollBreakSys (BreakBlockEvent): remembers a GatherCtx (world, position, block, held item, ripe, engine deco flag, pkey) and
    defers to CollBreakTask (World.execute, so SkyyIslands' protection and every other cancelling system ran first). Cancelled -> 0.
    Placed block (our PlacedStore, seeded once from SkyySkills' placed/*.bin) or an engine "deco" block that drops itself -> 0,
    except ripe crops / berry bushes. If the same call stack handed items over through InteractivelyPickupItemEvent (the F pickup
    of loose blocks: BlockHarvestUtils.performPickupByInteraction fires BreakBlockEvent, then the Harvest drops) those EXACT stacks
    are credited (never twice); otherwise the engine's own drop helper is re-rolled: CollDrops.breakDrops = BlockHarvestUtils
    .getDrops with the tool entry resolved from the held item (Pickaxe / Shears / Scraper), like damageSingleBlock does.
  - H2 CollUseSys (UseBlockEvent.Post on a ripe harvestable block) opens a 2 s window; H3 CollPickupSys
    (InteractivelyPickupItemEvent) credits the exact crop stacks FarmingUtil.giveDrops hands over (CollPickupTask, cancel-checked).
    A pickup event with no break ctx and no use window (other mods) is ignored. Only F pickups of loose blocks and F-harvests fire
    that event (ground item pickups never do), so the window cannot credit someone else's items. Diagnostic: the first harvest
    pickup logs "F-harvest pickups reach SkyyCollections"; 5 ripe harvests without one log a warning (harvest fallback needed).
  - H4 CollPlaceSys (PlaceBlockEvent) records placed positions. H5 CollKillSys (DeathComponent on an NPCEntity, killer = the
    player behind Damage.EntitySource) re-rolls the NPC's drop list (Role.getDropListId -> ItemModule.getRandomItemDrops).
  - Creative gives nothing; a credit is dropped when the active profile changed between the event and the task; sanity caps
    256 per credit and 20,000 items per player per minute (config.properties). Trades, Bazaar, /craft, bags, /give, thrown items and
    ground pickups never count (none of them fires H1-H5).
  Registry (collections.properties, generated here, every item id checked against Assets.zip at build time): 105 collections (273 items) in
    Farming, Mining, Foraging (one per log type, 33) and Combat; Fishing counted but hidden; Onyxium hidden (no source yet).
    Undiscovered collections show as "???". Four curves Bulk 10 / Standard 9 / Rare 8 / Elite 7 tiers.
  Rewards per tier (collections.properties tier.* + rewards.properties): coins (coins:fn:add), gathering-skill XP lumps
    (III 500, V 2,500, VII 10,000, last tier 25,000) through SkyySkills' XP-grant bridge skill:fn:addxp {uuid, skill, Long, source}
    (orchestrator DECISION 6: SkyySkills 0.4 accepts Mining/Foraging/Farming/Alchemy/Smithing/Cooking; collections grant the
    first three), Combat pays double coins on III/V/VII/last instead of XP,
    recipe unlocks (explicit table only; the 0.1 auto rule is opt-in, auto=false), +1 score per tier. Coins and XP each have their
    own paid marker (_paid.<Id>, _paidxp.<Id>): a reward that cannot be paid (SkyyCoins / SkyySkills missing or refusing) stays owed
    and is retried every 30 s on the player's world thread; nothing is ever paid twice.
  Recipe unlocks go to coll:recipes:<uuid> in the SAME format as 0.1.3-0.1.5 (SkyySacks Collections tab); recipes on
    exclude.benches (Alchemybench, Cookingbench, Furnace, Tannery, Campfire, Salvagebench) are never listed.
  Coin-bypass (design lock): buys ONLY the next tier's recipe unlocks, one tier at a time, up to the curve wall (Bulk V, Standard IV,
    Rare III, Elite never); price = max(500, missing x bazaar:buy:<first item> x 5) with a per-curve fallback; second click within
    10 s confirms; coins:fn:take first, then _bought.<Id> is saved, refund on a failed save; logged to bypass.log.
  Migration (start(), never setup(): block assets load after setup): every counts file without _schema=2 is archived to
    counts-0.1/ and converted only where exact (a Breaking ItemId, no drop list, no Soft entry, no state-less tool entry, item in the
    registry) - Skyy's file becomes Cobblestone 22 + Ash Log 5; everything else is dropped and logged to migration-0.2.log;
    unlocks.properties -> unlocks-0.1.properties. A file first read before that pass is converted on load. Players with migrated
    data get one chat line. Note vs the spec wording: trunks carry a Scraper tool entry WITH a state (Stripped), which never breaks
    the block, so only state-less tool entries block a conversion (the spec's expected Ash Log +5 needs exactly that).
  Leaderboards: /collections top <collection|score> - every counts file on disk (one row per profile, "name (profile N)"),
    overlaid with the in-memory counts, cached 30 s. _name=<player> is written to each counts file.
  Page (/collections, /coll, /coll <name>): one inline page, three views switched with rebuild() (HOME categories -> CATEGORY grid of
    12 cards -> COLLECTION tier list with DONE / NEXT / LOCKED / BOUGHT chips and the Buy button) plus an Unlocked recipes view.
    1120 x 840 root with only Width/Height, no underscores in ids, TextButton + EventData matched with a trailing quote, dynamic
    text via b.set, no periodic updates, the page never closes itself before opening something else.
  Bridge (skyy.bridge): coll:recipes:<uuid> (unchanged), coll:<uuid> summary, coll:score:<uuid>, coll:last:<uuid>,
    coll:epoch:<uuid>, coll:list, coll:fn:count, coll:fn:tier, coll:fn:add (sources in bridge.add.sources, default skills:double).
  Per profile (tools/PROFILES-CONTRACT.md): counts/<pkey>.properties, caches keyed by pkey, UUID-keyed bridge values republished on
    a profile:epoch change (the 0.1.5 publish/syncEpoch chain), unreadable files never cached as empty.
0.1.5: per-profile storage; breaks counted only when not cancelled. 0.1.4: command rules. 0.1.3: recipe unlocks bridge.
Run:   python build_skyycollections_0.2.1.py          -> SkyyCollections/SkyyCollections-0.2.1.jar
       (--deploy copies to Mods/SkyyCollections.jar - Skyy's OK needed first)
"""
import sys, os, re, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.2.1"
HERE = os.path.dirname(os.path.abspath(__file__))

# ================= registry defaults (every id checked against Assets.zip) =================
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
with zipfile.ZipFile(ASSETS) as z:
    ITEM_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    LANG = {}
    for line in z.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
        m = re.match(r"items\.([A-Za-z0-9_]+)\.name\s*=\s*(.*)", line)
        if m:
            LANG[m.group(1)] = m.group(2).strip()

def must(i):
    if i not in ITEM_IDS:
        raise SystemExit("unknown item id in the collection defaults: " + i)
    return i

REG = []   # (id, category, curve, name, icon, [items], flags, from)
# Category order = CollReg.CATS (Java, generated from this tuple) = page order. Rewards look categories up BY NAME (coinsAt, xpAt,
# parseReg), so reordering is safe for them; the page shows the first 4 as cards, so the hidden Fishing must stay last.
CATS_PY = ("Farming", "Mining", "Foraging", "Combat", "Fishing")
assert CATS_PY[-1] == "Fishing"
def add(cid, cat, curve, name, items, frm, flags=""):
    items = list(items)
    assert items, cid
    for i in items:
        must(i)
    assert re.match(r"^[A-Za-z0-9]+$", cid), cid
    assert cat in CATS_PY and curve in "BSRE", cid
    for s in (name, frm):
        assert not re.search(r"[|=\n#@\\\"]", s), cid
    assert cid.lower() not in [r[0].lower() for r in REG], cid
    REG.append((cid, cat, curve, name, items[0], items, flags, frm))

# ---- Farming (Farming skill XP)
for c in ["Wheat", "Carrot", "Potato", "Corn", "Tomato", "Lettuce", "Onion", "Turnip", "Cauliflower", "Aubergine", "Chilli", "Rice",
          "Pumpkin", "Cotton"]:
    it = "Plant_Crop_%s_Item" % c
    add(c, "Farming", "S", LANG.get(it, c), [it], "ripe %s crops - broken or harvested with F" % c.lower())
add("Berries", "Farming", "S", "Wild Berries", ["Plant_Fruit_Berries_Red"], "ripe berry bushes - broken or harvested with F")
add("Apple", "Farming", "S", "Apple", ["Plant_Fruit_Apple"], "apples growing on apple trees")
add("WildFruit", "Farming", "R", "Wild Fruit", ["Plant_Fruit_Coconut", "Plant_Fruit_Mango", "Plant_Fruit_Pinkberry", "Plant_Fruit_Azure",
                                               "Plant_Fruit_Spiral", "Plant_Fruit_Windwillow"], "fruit growing on wild trees")
MUSH = sorted(i for i in ITEM_IDS if re.match(r"^Plant_Crop_Mushroom_(Cap|Common|Flatcap|Glowing|Shelve)_", i))
assert len(MUSH) == 19, MUSH
add("Mushroom", "Farming", "S", "Mushroom", MUSH, "wild mushrooms - picked with F or broken")
add("Cactus", "Farming", "S", "Cactus", ["Plant_Cactus_1", "Plant_Cactus_2", "Plant_Cactus_3", "Plant_Cactus_Ball_1", "Plant_Cactus_Flat_1",
                                          "Plant_Cactus_Flat_2", "Plant_Cactus_Flat_3"], "wild cactus")
SEEDS = sorted(i for i in ITEM_IDS if i.startswith("Plant_Seeds_") and i != "Plant_Seeds_Test_Tree")
add("Seeds", "Farming", "B", "Seeds", ["Plant_Seeds_Wheat"] + [s for s in SEEDS if s != "Plant_Seeds_Wheat"],
    "unripe crops - ripe crops - wild grass crops")
add("LifeEssence", "Farming", "B", "Essence of Life", ["Ingredient_Life_Essence"], "every ripe crop")
add("Petals", "Farming", "R", "Petals", ["Plant_Petals_Blood", "Plant_Petals_Azure", "Plant_Petals_Storm"], "health - mana and stamina herbs")
add("RawChicken", "Farming", "S", "Raw Chicken", ["Food_Chicken_Raw"], "chickens")
add("RawBeef", "Farming", "S", "Raw Beef", ["Food_Beef_Raw"], "cows - bison - camels")
add("RawPork", "Farming", "S", "Raw Pork", ["Food_Pork_Raw"], "pigs - wild pigs - warthogs")
add("Wildmeat", "Farming", "S", "Raw Wildmeat", ["Food_Wildmeat_Raw"], "deer - boar - sheep - birds and more")
add("RawFish", "Fishing", "S", "Raw Fish", ["Food_Fish_Raw", "Food_Fish_Raw_Uncommon", "Food_Fish_Raw_Rare", "Food_Fish_Raw_Epic",
                                           "Food_Fish_Raw_Legendary"], "fish (the Fishing category opens later)", "hidden")
# ---- Foraging (Foraging skill XP): one collection per log type (Skyy's call)
RARE_WOOD = {"Amber", "Azure", "Crystal", "Fire", "Ice", "Petrified", "Poisoned", "Spiral", "Stormbark"}
TRUNKS = sorted(i for i in ITEM_IDS if re.match(r"^Wood_[A-Za-z_]+_Trunk$", i))
assert len(TRUNKS) == 33, TRUNKS
def log(it):
    t = it[5:-6]
    curve = "B" if t == "Oak" else ("R" if t in RARE_WOOD else "S")
    name = LANG.get(it, t.replace("_", " ") + " Log")
    add(t.replace("_", "") + "Log", "Foraging", curve, name, [it], name.replace(" Log", "").lower() + " trees")
log("Wood_Oak_Trunk")
add("Fiber", "Foraging", "B", "Plant Fiber", ["Ingredient_Fibre"], "bushes - leaves - vines - reeds - moss - seaweed")
add("Stick", "Foraging", "B", "Stick", ["Ingredient_Stick"], "bushes - branches - brambles - berry bushes")
add("TreeSap", "Foraging", "S", "Tree Sap", ["Ingredient_Tree_Sap"], "branches - sap globs")
for it in [t for t in TRUNKS if t != "Wood_Oak_Trunk" and t[5:-6] not in RARE_WOOD] + [t for t in TRUNKS if t[5:-6] in RARE_WOOD]:
    log(it)
# ---- Mining (Mining skill XP)
add("Cobblestone", "Mining", "B", "Cobblestone", ["Rock_Stone_Cobble", "Rock_Stone_Cobble_Mossy"], "stone - aqua - calcite - ores in stone")
add("Sandstone", "Mining", "B", "Sandstone", ["Rock_Sandstone_Cobble", "Rock_Sandstone_Red_Cobble", "Rock_Sandstone_White_Cobble"],
    "the three sandstones and ores in sandstone")
add("Shale", "Mining", "B", "Shale Cobble", ["Rock_Shale_Cobble"], "shale and ores in shale")
add("Slate", "Mining", "B", "Slate Cobble", ["Rock_Slate_Cobble"], "slate and ores in slate")
add("Basalt", "Mining", "B", "Basalt Cobble", ["Rock_Basalt_Cobble"], "basalt and ores in basalt")
add("Volcanic", "Mining", "B", "Volcanic Rock", ["Rock_Volcanic_Cobble", "Rock_Magma_Cooled"], "volcanic rock - cooled magma")
add("Marble", "Mining", "S", "Marble Cobble", ["Rock_Marble_Cobble"], "marble")
add("Quartzite", "Mining", "S", "Quartzite Cobble", ["Rock_Quartzite_Cobble"], "quartzite")
add("Limestone", "Mining", "S", "Limestone", ["Rock_Lime_Cobble"], "limestone")
add("Ice", "Mining", "S", "Ice", ["Rock_Ice", "Rock_Ice_Permafrost"], "ice and permafrost")
add("Salt", "Mining", "S", "Salt Block", ["Rock_Salt"], "salt blocks")
add("Sand", "Mining", "B", "Sand", ["Soil_Sand", "Soil_Sand_Red", "Soil_Sand_White", "Soil_Sand_Ashen"], "sand of every colour")
RUBBLE = sorted(i for i in ITEM_IDS if i.startswith("Rubble_"))
add("Rubble", "Mining", "B", "Rubble", ["Rubble_Stone"] + [r for r in RUBBLE if r != "Rubble_Stone"], "gravel - loose rubble picked with F")
add("Clay", "Mining", "S", "Clay", ["Soil_Clay", "Soil_Clay_Ocean"], "clay - clay stalactites")
for metal, curve, frm in (("Copper", "S", "copper veins"), ("Iron", "S", "iron veins"), ("Silver", "R", "silver veins"), ("Gold", "R", "gold veins"),
                          ("Thorium", "R", "thorium veins in mud and sandstone"), ("Cobalt", "R", "cobalt veins in shale and slate"),
                          ("Adamantite", "E", "adamantite veins in magma"), ("Mithril", "E", "mithril veins")):
    add(metal, "Mining", curve, metal + " Ore", ["Ore_" + metal], frm)
add("Onyxium", "Mining", "E", "Onyxium Ore", ["Ore_Onyxium"], "no known source yet", "hidden")
add("Crystal", "Mining", "R", "Crystal Shards", sorted(i for i in ITEM_IDS if re.match(r"^Ingredient_Crystal_[A-Za-z]+$", i)),
    "crystal clusters - crystal golems")
add("Gemstone", "Mining", "E", "Gemstones", sorted(i for i in ITEM_IDS if re.match(r"^Rock_Gem_[A-Za-z]+$", i)), "gem blocks - crystal golems")
# ---- Combat (coins instead of skill XP)
for cid, curve, name, items, frm in (
        ("Bone", "S", "Bone Fragments", ["Ingredient_Bone_Fragment"], "skeletons - ghouls - skeleton horses"),
        ("Linen", "S", "Linen Scraps", ["Ingredient_Fabric_Scrap_Linen"], "skeletons - ghouls"),
        ("HideLight", "S", "Light Hide", ["Ingredient_Hide_Light"], "chickens - deer - antelope - camels"),
        ("HideMedium", "S", "Medium Hide", ["Ingredient_Hide_Medium"], "cows - boar - horses - hyenas"),
        ("HideHeavy", "R", "Heavy Hide", ["Ingredient_Hide_Heavy"], "polar bears - crocodiles - mosshorns - cave rex"),
        ("Wool", "S", "Wool Scraps", ["Ingredient_Fabric_Scrap_Wool"], "sheep (killed - shearing does not count yet)"),
        # Light first on purpose (spec 2.5 lists them A-Z): the first item is the coin-unlock price item (bazaar:buy:<first item>)
        # and SkyyBazaar 0.1.1 trades only Ingredient_Feathers_Light ("White Feathers"); Blue first would fall back to the curve price
        ("Feathers", "S", "Feathers", ["Ingredient_Feathers_Light", "Ingredient_Feathers_Blue", "Ingredient_Feathers_Dark",
                                       "Ingredient_Feathers_Red"], "birds"),
        ("Chitin", "R", "Sturdy Chitin", ["Ingredient_Chitin_Sturdy"], "scaraks - armadillos"),
        ("Venom", "R", "Venom Sac", ["Ingredient_Sac_Venom"], "scaraks - scorpions - snakes - cave spiders"),
        ("Shadoweave", "R", "Shadoweave Scraps", ["Ingredient_Fabric_Scrap_Shadoweave"], "outlanders"),
        ("Cindercloth", "R", "Cindercloth Scraps", ["Ingredient_Fabric_Scrap_Cindercloth"], "burnt skeletons - flame golems"),
        ("FireEssence", "R", "Essence of Fire", ["Ingredient_Fire_Essence"], "fire creatures"),
        ("IceEssence", "R", "Essence of Ice", ["Ingredient_Ice_Essence"], "frost skeletons"),
        ("VoidEssence", "R", "Essence of the Void", ["Ingredient_Void_Essence"], "void creatures - outlander casters"),
        ("LightningEssence", "E", "Essence of Lightning", ["Ingredient_Lightning_Essence"], "thunder spirits"),
        ("Voidheart", "E", "Voidheart", ["Ingredient_Voidheart"], "void creatures"),
        ("BoomPowder", "S", "Boom Powder", ["Ingredient_Powder_Boom"], "boomshrooms - broken or picked with F")):
    add(cid, "Combat", curve, name, items, frm)
ALL_ITEMS = [i for r in REG for i in r[5]]
assert len(ALL_ITEMS) == len(set(ALL_ITEMS)), "an item is in two collections"
print("registry:", len(REG), "collections,", len(ALL_ITEMS), "items")

CURVES = {"B": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
          "S": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000],
          "R": [25, 50, 100, 250, 500, 1000, 2500, 5000],
          "E": [10, 25, 50, 100, 250, 500, 1000]}
TIER_COINS = [50, 100, 200, 400, 800, 1500, 3000, 6000, 12000, 25000]
TIER_XP = [0, 0, 500, 0, 2500, 0, 10000, 0, 0, 0]
REG_TXT = [
    "# SkyyCollections 0.2 - collections (generated defaults; edit, then /collections reload)",
    "# coll.<Id>=<Category>|<Curve B/S/R/E>|<Name>|<Icon item>|<item,item,...>|<flags: hidden nobypass>|<where it comes from>",
    "# Categories: Farming, Mining, Foraging, Combat, Fishing (Fishing stays hidden until fishing ships; its items still count).",
    "# The ORDER of the coll. lines is the order on the page. A collection's total is the sum of its items (stored per item id,",
    "# so moving an item to another collection later never loses data). An item may be in one collection only.",
    "# Curves = item totals for tier I, II, ... (Bulk 10 tiers, Standard 9, Rare 8, Elite 7).",
]
for k in "BSRE":
    REG_TXT.append("curve.%s=%s" % (k, ",".join(str(x) for x in CURVES[k])))
REG_TXT += [
    "# Rewards on every tier (rewards.properties adds recipes and extras). Farming/Mining/Foraging collections pay the XP of their",
    "# skill through SkyySkills (skill:fn:addxp); the LAST tier of any collection pays tier.lastXp instead of its tier.xp slot.",
    "tier.coins=" + ",".join(str(x) for x in TIER_COINS),
    "tier.xp=" + ",".join(str(x) for x in TIER_XP),
    "tier.lastXp=25000",
    "# Combat collections pay no skill XP (class weapon skills cannot be granted from outside): coins x this on III, V, VII and the last tier",
    "combat.coinMultiplier=2",
]
for (cid, cat, curve, name, icon, items, flags, frm) in REG:
    REG_TXT.append("coll.%s=%s|%s|%s|%s|%s|%s|%s" % (cid, cat, curve, name, icon, ",".join(items), flags, frm))

REC = lambda i: "recipe:" + must(i) + "_Recipe_Generated_0"
BAG = lambda cat, size: "recipe:Skyy_Sack_%s_%s_Recipe_Generated_0" % (cat, size)
RW = [
    "# SkyyCollections 0.2 - tier rewards, ADDED to the default coins / skill XP of collections.properties",
    "# <CollectionId>.<tier number>=recipe:<RecipeId>,coins:<n>,xp:<Skill>:<n>",
    "# Recipe ids are <OutputItemId>_Recipe_Generated_<index>. Unknown ids and recipes on exclude.benches (config.properties) are",
    "# skipped and logged once. An unlocked recipe shows in /craft -> Collections and crafts there without its bench (materials",
    "# still needed). Every collection's tier I will also get its minion recipe once SkyyMinions exists.",
    "Wheat.1=" + REC("Tool_Sickle_Crude"), "Wheat.3=" + REC("Tool_Hoe_Copper"), "Wheat.4=" + REC("Tool_Sickle_Copper"),
    "Wheat.5=" + BAG("Farming", "Medium"), "Wheat.6=" + REC("Tool_Sickle_Iron"), "Wheat.7=" + REC("Tool_Hoe_Iron"), "Wheat.8=" + BAG("Farming", "Large"),
    "OakLog.1=" + REC("Tool_Hatchet_Copper"), "OakLog.3=" + BAG("Foraging", "Small"), "OakLog.5=" + BAG("Foraging", "Medium"),
    "OakLog.6=" + REC("Tool_Hatchet_Iron"), "OakLog.8=" + BAG("Foraging", "Large"),
    "Cobblestone.1=" + REC("Tool_Pickaxe_Copper"), "Cobblestone.3=" + BAG("Mining", "Small"), "Cobblestone.4=" + REC("Rock_Stone_Brick"),
    "Cobblestone.5=" + BAG("Mining", "Medium"), "Cobblestone.6=" + REC("Tool_Pickaxe_Iron"), "Cobblestone.8=" + BAG("Mining", "Large"),
    "Fiber.3=" + REC("Tool_Shears_Basic"),
    "Stick.3=" + REC("Weapon_Arrow_Crude"),
    "Bone.3=" + BAG("Combat", "Small"), "Bone.5=" + BAG("Combat", "Medium"), "Bone.8=" + BAG("Combat", "Large"),
    "Sandstone.4=" + REC("Rock_Sandstone_Brick"), "Shale.4=" + REC("Rock_Shale_Brick"), "Slate.4=" + REC("Rock_Slate_Brick"),
    "Basalt.4=" + REC("Rock_Basalt_Brick"), "Marble.4=" + REC("Rock_Marble_Brick"),
    "# Proposed ore line (research/Collections-Spec.md 4.3) - waiting for Skyy's OK. Remove the # of a line to enable it.",
]
PIECES = ["Head", "Hands", "Legs", "Chest"]
for metal, tools in (("Copper", []), ("Iron", []), ("Thorium", ["Tool_Pickaxe_Thorium", "Tool_Hatchet_Thorium"]),
                     ("Cobalt", ["Tool_Pickaxe_Cobalt", "Tool_Hatchet_Cobalt"]), ("Adamantite", ["Tool_Pickaxe_Adamantite", "Tool_Hatchet_Adamantite"]),
                     ("Mithril", ["Tool_Pickaxe_Mithril", "Tool_Hatchet_Mithril"])):
    if tools:
        RW.append("#%s.1=%s" % (metal, ",".join(REC(t) for t in tools)))
    for n, p in enumerate(PIECES):
        RW.append("#%s.%d=%s" % (metal, n + 2, REC("Armor_%s_%s" % (metal, p))))
    if metal == "Thorium":
        RW.append("#Thorium.6=" + REC("Tool_Hoe_Thorium"))

CFG = [
    "# SkyyCollections 0.2 settings. /collections reload re-reads this file, collections.properties and rewards.properties.",
    "# migrate = convert (0.1 block counts become item counts where the block gives exactly one known item) | reset (archive, start at 0)",
    "migrate=convert",
    "# auto = the 0.1 auto rule (a recipe unlocks when every started input reaches tier I). Off: with item counts it unlocks far too much",
    "auto=false",
    "# recipes on these benches are never unlocked by collections (timed processing and table-only crafting stay at their tables)",
    "exclude.benches=Alchemybench,Cookingbench,Furnace,Tannery,Campfire,Salvagebench",
    "# anti-exploit: most items one credit may add, most items per player per minute (0 = no cap). Admin /collections give is exempt",
    "cap.perCredit=256",
    "cap.perMinute=20000",
    "# coin-bypass: buy only the NEXT tier's recipe unlocks (never its coins, XP, score or leaderboard count), one tier at a time",
    "bypass.enabled=true",
    "# price = max(minPrice, missing items x unit x multiplier); unit = the SkyyBazaar instant-buy price, else the fallback per curve",
    "bypass.multiplier=5",
    "bypass.minPrice=500",
    "# fallback unit price per curve: Bulk,Standard,Rare,Elite",
    "bypass.fallback=2,5,25,100",
    "# highest tier coins can buy, per curve: Bulk,Standard,Rare,Elite (0 = never)",
    "bypass.walls=5,4,3,0",
    "# coll:fn:add sources other mods may use, any case (skills:double = SkyySkills double drops; add minion when SkyyMinions ships)",
    "# skills:felled = logs that fall when you cut a tree (SkyySkills 0.4.2)",
    "bridge.add.sources=skills:double,skills:felled",
    "# skills:felled is accepted even when missing from the list above (older config files); false turns felled-log counting off",
    "bridge.add.felled=true",
]

def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '\\n"'
def text_method(name, lines):
    body = "\n".join("  sb.append(%s);" % jstr(l) for l in lines)
    return "public static String %s() {\n  StringBuilder sb = new StringBuilder();\n%s\n  return sb.toString();\n}" % (name, body)

# ================= javassist =================
T = {
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PLB":  "com.hypixel.hytale.server.core.plugin.PluginBase",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "PGE":  "com.hypixel.hytale.protocol.packets.interface_.Page",
    "PGM":  "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "CMP":  "com.hypixel.hytale.component.Component",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC":   "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "OA":   "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "GM":   "com.hypixel.hytale.protocol.GameMode",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "EES":  "com.hypixel.hytale.component.system.EntityEventSystem",
    "ACH":  "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":   "com.hypixel.hytale.component.CommandBuffer",
    "EV":   "com.hypixel.hytale.component.system.EcsEvent",
    "QRY":  "com.hypixel.hytale.component.query.Query",
    "EST":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CHS":  "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BBE":  "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
    "PBE":  "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent",
    "UBE":  "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent",
    "UBP":  "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Post",
    "IPE":  "com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent",
    "BTY":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BTM":  "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap",
    "BGA":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering",
    "BTD":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering$BlockToolData",
    "BBD":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockBreakingDropType",
    "SBD":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.SoftBlockDropType",
    "BHU":  "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils",
    "BPH":  "com.hypixel.hytale.server.core.blocktype.component.BlockPhysics",
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "ITM":  "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "CRR":  "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe",
    "MQ":   "com.hypixel.hytale.server.core.inventory.MaterialQuantity",
    "BRQ":  "com.hypixel.hytale.protocol.BenchRequirement",
    "V3I":  "org.joml.Vector3i",
    "ODS":  "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem",
    "DTH":  "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "DMG":  "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DES":  "com.hypixel.hytale.server.core.modules.entity.damage.Damage.EntitySource",   # javassist source name (dotted nested)
    "NPC":  "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ROLE": "com.hypixel.hytale.server.npc.role.Role",
    "IMOD": "com.hypixel.hytale.server.core.modules.item.ItemModule",
    "PKG":  "com.skyy.collections",
}
def jv(src):
    for k, v in T.items():
        src = src.replace("@" + k + "@", v)
    assert "@" not in src, "unreplaced token in: " + src[src.index("@") - 60: src.index("@") + 60]
    return src

J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

for c, m in ((T["BBE"], "getBlockType"), (T["BBE"], "getTargetBlock"), (T["BBE"], "getItemInHand"), (T["PBE"], "getTargetBlock"),
             (T["UBE"], "getBlockType"), (T["UBP"], "getBlockType"), (T["IPE"], "getItemStack"), (T["IPE"], "isCancelled"),
             ("com.hypixel.hytale.component.system.CancellableEcsEvent", "isCancelled"),
             (T["BHU"], "getDrops"), (T["BGA"], "getToolData"), (T["BGA"], "getBreaking"), (T["BGA"], "getSoft"), (T["BGA"], "isSoft"),
             (T["BGA"], "getHarvest"), (T["BGA"], "shouldUseDefaultDropWhenPlaced"), (T["BTD"], "getStateId"), (T["BTD"], "getItemId"),
             (T["BTD"], "getDropListId"), (T["BTD"], "getTypeId"), (T["BBD"], "getQuantity"), (T["BBD"], "getItemId"),
             (T["BBD"], "getDropListId"), (T["SBD"], "getItemId"), (T["SBD"], "getDropListId"),
             (T["BTY"], "getAssetMap"), (T["BTY"], "getGathering"), (T["BTY"], "getStateForBlock"), (T["BTY"], "getId"),
             (T["BTM"], "getIndexOrDefault"), (T["BTM"], "getAsset"), (T["BTM"], "getNextIndex"),
             (T["BPH"], "isDeco"), (T["BPH"], "getComponentType"), (T["CHS"], "getChunkSectionReferenceAtBlock"), (T["CHS"], "getStore"),
             (T["NPC"], "getRole"), (T["NPC"], "getComponentType"), (T["ROLE"], "getDropListId"), (T["IMOD"], "get"),
             (T["IMOD"], "getRandomItemDrops"), (T["DTH"], "getDeathInfo"), (T["DMG"], "getSource"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource", "getRef"),
             (T["ODS"], "componentType"), ("com.hypixel.hytale.component.system.RefChangeSystem", "onComponentAdded"),
             (T["CRR"], "getAssetMap"), (T["CRR"], "getBenchRequirement"), (T["CRR"], "getInput"), (T["CRR"], "getId"), (T["MQ"], "getItemId"),
             (T["ITM"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap"),
             (T["PLA"], "getGameMode"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["GM"], "Creative"),
             (T["PGM"], "openCustomPage"), (T["PGM"], "setPage"), (T["PGE"], "None"), (T["PAGE"], "rebuild"), (T["LIFE"], "CanDismiss"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["BT"], "Activating"),
             (T["AC"], "setPermissionGroups"), (T["AC"], "addSubCommand"), (T["AC"], "requirePermission"), (T["AC"], "addAliases"),
             (T["AC"], "addUsageVariant"), (T["AC"], "withRequiredArg"), (T["AC"], "withOptionalArg"), (T["CTX"], "provided"),
             (T["PLB"], "start"), (T["PLB"], "shutdown"), (T["PLB"], "getDataDirectory"),
             (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"), (T["UNI"], "getWorld"), (T["PR"], "getUuid"), (T["PR"], "getUsername"),
             (T["PR"], "isValid"), (T["PR"], "getWorldUuid"), (T["PR"], "getReference"), (T["PR"], "sendMessage"), (T["PR"], "hasPermission"),
             (T["REF"], "isValid"), (T["REF"], "getStore"), (T["ST"], "getComponent"), (T["ST"], "getExternalData"),
             (T["EST"], "getWorld"), (T["WLD"], "execute"), (T["WLD"], "getName"), (T["WLD"], "getChunkStore"),
             (T["ACH"], "getReferenceTo"), ("com.hypixel.hytale.component.Archetype", "empty"),
             (T["MSG"], "raw"), (T["MSG"], "color"), (T["HSV"], "SCHEDULED_EXECUTOR"),
             (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"), (T["V3I"], "x"), (T["V3I"], "y"), (T["V3I"], "z")):
    B.probe(pool, c, m)

PKG = T["PKG"]
def K(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(T[sup]) if sup else None) if sup else pool.makeClass(PKG + "." + name)
util = K("CollUtil"); cio = K("CollIO"); rd = K("RegData"); reg = K("CollReg"); drp = K("CollDrops"); mig = K("CollMigrate")
cdat = K("CollData"); sto = K("CollStore"); rew = K("CollRewards"); unl = K("CollUnlocks"); cred = K("CollCredit"); byp = K("CollBypass")
plc = K("PlacedStore"); pend = K("CollPending"); gctx = K("GatherCtx")
btk = K("CollBreakTask"); ptk = K("CollPickupTask"); pltk = K("CollPlaceTask"); ktk = K("CollKillTask"); atk = K("CollAddTask"); rtk = K("CollRetryTask")
bsy = K("CollBreakSys", "EES"); usy = K("CollUseSys", "EES"); psy = K("CollPickupSys", "EES"); plsy = K("CollPlaceSys", "EES"); ksy = K("CollKillSys", "ODS")
tcmp = K("CollTopCmp"); top = K("CollTop"); fnc = K("CollFn"); page = K("CollPage", "PAGE")
ulc = K("CollUnlocksCmd", "APC"); rlc = K("CollReloadCmd", "APC"); gvc = K("CollGiveCmd", "APC"); tpc = K("CollTopCmd", "APC")
nmc = K("CollNameCmd", "APC"); cmd = K("CollCmd", "APC"); sav = K("CollSaver"); pl = K("SkyyCollectionsPlugin", "JP")
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, rew, unl, cred, byp, plc, pend, gctx, btk, ptk, pltk, ktk, atk, rtk, bsy, usy, psy, plsy, ksy,
       tcmp, top, fnc, page, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)

def M(cls, src):
    s = jv(src)
    try:
        cls.addMethod(CtNewMethod.make(s, cls))
    except Exception as e:
        print("COMPILE FAILED in", cls.getName(), ":\n", s[:600]); raise
def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))
def C(cls, src):
    s = jv(src)
    try:
        cls.addConstructor(CtNewConstructor.make(s, cls))
    except Exception as e:
        print("COMPILE FAILED (ctor) in", cls.getName(), ":\n", s[:600]); raise
def RUN(cls):
    cls.addInterface(pool.get("java.lang.Runnable"))
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'   # vanilla /help /who /ping pattern (SkyyEssentials 0.1)

# ================= fields =================
F(util, "public static @LOG@ LOG;")
for f in ("public String[] id;", "public int[] cat;", "public int[] curve;", "public String[] name;", "public String[] icon;",
          "public Object[] items;", "public boolean[] hidden;", "public boolean[] nobypass;", "public String[] from;",
          "public boolean[] iconOk;", "public java.util.HashMap itemColl;", "public java.util.HashMap byId;", "public Object[] thr;",
          "public long[] coins;", "public long[] xp;", "public long lastXp;", "public double combatMult;", "public int n;"):
    F(rd, f)
for f in ("public static volatile @PKG@.RegData D;", "public static java.nio.file.Path BASE;",
          "public static volatile java.util.HashMap REWARDS = new java.util.HashMap();",
          "public static volatile java.util.HashMap RECIPES = new java.util.HashMap();",
          "public static volatile boolean VALIDATED = false;",
          "public static volatile String MIGRATE = \"convert\";", "public static volatile boolean AUTO = false;",
          "public static volatile java.util.HashSet EXCLUDE = new java.util.HashSet();",
          "public static volatile long CAP_CREDIT = 256L;", "public static volatile long CAP_MINUTE = 20000L;",
          "public static volatile boolean BYPASS = true;", "public static volatile double BYP_MULT = 5.0;",
          "public static volatile long BYP_MIN = 500L;", "public static volatile long[] BYP_FALLBACK = new long[] { 2L, 5L, 25L, 100L };",
          "public static volatile int[] BYP_WALL = new int[] { 5, 4, 3, 0 };",
          "public static volatile java.util.HashSet ADD_SOURCES = new java.util.HashSet();",
          "public static final String[] CATS = new String[] { " + ", ".join('"%s"' % c for c in CATS_PY) + " };",
          "public static final String[] CURVES = new String[] { \"B\", \"S\", \"R\", \"E\" };",
          "public static final String[] CURVENAMES = new String[] { \"Bulk\", \"Standard\", \"Rare\", \"Elite\" };",
          "public static final String[] CATICON = new String[] { \"Plant_Crop_Wheat_Item\", \"Ore_Copper\", \"Wood_Oak_Trunk\", \"Ingredient_Bone_Fragment\", \"Food_Fish_Raw\" };",
          "public static final String[] ACCENT = new String[] { \"#e0c060\", \"#9fb8cc\", \"#7fcf7a\", \"#e07a6a\", \"#7fb8e0\" };",
          "public static final String[] EMPTY = new String[0];"):
    F(reg, f)
F(cdat, "public java.util.concurrent.ConcurrentHashMap items;")
F(cdat, "public java.util.concurrent.ConcurrentHashMap meta;")
F(cdat, "public volatile String name;")
for f in ("public static java.nio.file.Path DIR;",
          "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();"):
    F(sto, f)
F(rew, "public static final java.util.Set OWED = java.util.concurrent.ConcurrentHashMap.newKeySet();")
F(rew, "public static volatile long WARNC = 0L;")
F(rew, "public static volatile long WARNX = 0L;")
for f in ("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap PUBKEY = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SIG = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap CEPOCH = new java.util.concurrent.ConcurrentHashMap();"):
    F(unl, f)
F(cred, "public static final java.util.HashMap MINUTE = new java.util.HashMap();")
F(byp, "public static final java.util.concurrent.ConcurrentHashMap ARM = new java.util.concurrent.ConcurrentHashMap();")
F(plc, "public static java.nio.file.Path DIR;")
F(plc, "public static final int CAP = 400000;")
F(plc, "public static final java.util.HashMap WORLDS = new java.util.HashMap();")
F(plc, "public static final java.util.HashSet DIRTY = new java.util.HashSet();")
F(pend, "public static final java.util.concurrent.ConcurrentHashMap BREAK = new java.util.concurrent.ConcurrentHashMap();")
F(pend, "public static final java.util.concurrent.ConcurrentHashMap USE = new java.util.concurrent.ConcurrentHashMap();")
# harvest-hook diagnostic (test step 5): ripe-harvest windows opened, first window pickup seen, warned once
F(pend, "public static volatile int HOPEN = 0;")
F(pend, "public static volatile boolean HSEEN = false;")
F(pend, "public static volatile boolean HWARN = false;")
for f in ("public @BBE@ ev;", "public @PR@ pr;", "public java.util.UUID u;", "public String key;", "public String world;", "public int x;",
          "public int y;", "public int z;", "public @BTY@ bt;", "public String held;", "public boolean credit;", "public boolean ripe;",
          "public boolean deco;", "public boolean done;", "public Thread thread;", "public long nanos;", "public java.util.ArrayList pickups;"):
    F(gctx, f)
F(top, "public static final java.util.HashMap CACHE = new java.util.HashMap();")

# ================= CollUtil =================
M(util, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCollections] " + msg); } catch (Throwable t) { }
}""")
M(util, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyCollections] " + msg); } catch (Throwable t) { }
}""")
M(util, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# tools/PROFILES-CONTRACT.md storage-key helper, verbatim
M(util, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(util, r"""
public static long epochOf(java.util.UUID u) {
  try {
    Object o = bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) return ((Number) o).longValue();
    if (o != null) return Long.parseLong(String.valueOf(o).trim());
  } catch (Throwable t) { }
  return -1L;
}""")
M(util, r"""
public static String fmt(long n) {
  String s = String.valueOf(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (n < 0L) sb.append('-');
  return sb.reverse().toString();
}""")
M(util, r"""
public static String roman(int t) {
  String[] r = new String[] { "-", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""")
# 0.2.1: a collection with no tier says so (Skyy: 'Tier -' -> 'No tier yet')
M(util, r"""
public static String tierName(int t) {
  return t <= 0 ? "No tier yet" : "Tier " + roman(t);
}""")
# inline UI text: no quotes, braces, colons, semicolons, commas (the SkyySacks rule); dynamic text uses b.set instead
M(util, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ').replace('\n', ' ');
}""")
M(util, r"""
public static String clip(String t, int n) {
  if (t == null) return "";
  return t.length() <= n ? t : t.substring(0, n - 3) + "...";
}""")
M(util, r"""
public static String[] csv(String s) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == null) return new String[0];
  String[] p = s.split(",");
  for (int i = 0; i < p.length; i++) { String x = p[i].trim(); if (x.length() > 0) out.add(x); }
  return (String[]) out.toArray(new String[0]);
}""")
M(util, r"""
public static boolean creative(@ST@ st, @REF@ r) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p != null && p.getGameMode() == @GM@.Creative;
  } catch (Throwable t) { return false; }
}""")
M(util, r"""
public static String stateOf(@BTY@ bt) {
  try { return bt.getStateForBlock(bt.getId()); } catch (Throwable t) { return null; }
}""")
# leaderboard label: profile N >= 2 ("<uuid>-pN") shows "name (profile N)" (SkyySkills 0.3.2 SkillTop.label)
M(util, r"""
public static String label(String nm, String key) {
  if (key == null) return nm;
  int p = key.indexOf("-p");
  if (p <= 0 || p + 2 >= key.length()) return nm;
  return nm + " (profile " + key.substring(p + 2) + ")";
}""")
M(util, r"""
public static String armorPiece(String p) {
  if (p.equals("Head")) return "Helmet";
  if (p.equals("Chest")) return "Chestplate";
  if (p.equals("Legs")) return "Leggings";
  if (p.equals("Hands")) return "Gloves";
  return p;
}""")
# display name of an item / recipe output id (no lang lookup): Tool_Sickle_Crude -> Crude Sickle, Skyy_Sack_Mining_Small -> Small Mining Bag
M(util, r"""
public static String prettyItem(String id) {
  if (id == null) return "?";
  String[] p = id.split("_");
  if (id.startsWith("Skyy_Sack_") && p.length >= 4) return p[3] + " " + p[2] + " Bag";
  if (p.length == 3 && (p[0].equals("Tool") || p[0].equals("Weapon"))) return p[2] + " " + p[1];
  if (p.length == 3 && p[0].equals("Armor")) return p[1] + " " + armorPiece(p[2]);
  int from = 0;
  if (p.length > 1 && (p[0].equals("Rock") || p[0].equals("Ingredient") || p[0].equals("Plant") || p[0].equals("Food") || p[0].equals("Soil") || p[0].equals("Ore") || p[0].equals("Furniture") || p[0].equals("Tool") || p[0].equals("Weapon") || p[0].equals("Armor"))) from = 1;
  StringBuilder sb = new StringBuilder();
  for (int i = from; i < p.length; i++) { if (sb.length() > 0) sb.append(' '); sb.append(p[i]); }
  return sb.toString();
}""")
M(util, r"""
public static String prettyRecipe(String rid) {
  if (rid == null) return "?";
  int g = rid.indexOf("_Recipe_Generated_");
  return prettyItem(g > 0 ? rid.substring(0, g) : rid);
}""")

# ================= CollIO: every data-file read/write (leaf lock; the 0.1.5 pattern + Windows replace retry) =================
M(cio, r"""
public static synchronized java.util.Properties read(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  }
  return p;
}""")
M(cio, r"""
public static synchronized void write(java.nio.file.Path dir, String key, java.util.Properties p) throws java.io.IOException {
  java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dir.resolve(key + ".properties.tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, "SkyyCollections 0.2 - item counts, _paid/_paidxp = rewarded tier, _bought = coin-bypass tier"); } finally { out.close(); }
  java.nio.file.Path f = dir.resolve(key + ".properties");
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(cio, r"""
public static synchronized java.util.List readLines(java.nio.file.Path f) throws java.io.IOException {
  return java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
}""")
M(cio, r"""
public static synchronized void writeText(java.nio.file.Path f, String text) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Files.write(f, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
}""")
M(cio, r"""
public static synchronized void append(java.nio.file.Path f, String text) {
  if (text == null || text.length() == 0) return;
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(f, text.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not append to " + f.getFileName() + ": " + t); }
}""")
M(cio, r"""
public static synchronized boolean copyIfMissing(java.nio.file.Path src, java.nio.file.Path dst) throws java.io.IOException {
  if (!java.nio.file.Files.exists(src, new java.nio.file.LinkOption[0]) || java.nio.file.Files.exists(dst, new java.nio.file.LinkOption[0])) return false;
  java.nio.file.Files.createDirectories(dst.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Files.copy(src, dst, new java.nio.file.CopyOption[0]);
  return true;
}""")

# ================= RegData =================
C(rd, "public RegData() { this.n = 0; this.lastXp = 25000L; this.combatMult = 2.0; }")

# ================= CollReg: registry, curves, reward tables, config =================
reg.addMethod(CtNewMethod.make(text_method("regText", REG_TXT), reg))
reg.addMethod(CtNewMethod.make(text_method("rewardsText", RW), reg))
reg.addMethod(CtNewMethod.make(text_method("configText", CFG), reg))
M(reg, r"""
public static java.util.List splitLines(String s) {
  return java.util.Arrays.asList(s.split("\n"));
}""")
M(reg, r"""
public static long[] longs(String v, long[] def) {
  try {
    String[] p = @PKG@.CollUtil.csv(v);
    if (p.length == 0) return def;
    long[] out = new long[p.length];
    for (int i = 0; i < p.length; i++) out[i] = Long.parseLong(p[i]);
    return out;
  } catch (Throwable t) { return def; }
}""")
M(reg, r"""
public static int[] ints(String v, int[] def, int len) {
  try {
    String[] p = @PKG@.CollUtil.csv(v);
    if (p.length != len) return def;
    int[] out = new int[p.length];
    for (int i = 0; i < p.length; i++) out[i] = Integer.parseInt(p[i]);
    return out;
  } catch (Throwable t) { return def; }
}""")
M(reg, r"""
public static int catIndex(String s) {
  for (int i = 0; i < CATS.length; i++) if (CATS[i].equalsIgnoreCase(s)) return i;
  return -1;
}""")
M(reg, r"""
public static int curveIndex(String s) {
  for (int i = 0; i < CURVES.length; i++) if (CURVES[i].equalsIgnoreCase(s) || CURVENAMES[i].equalsIgnoreCase(s)) return i;
  return 1;
}""")
M(reg, r"""
public static boolean ascending(long[] a) {
  if (a == null || a.length == 0) return false;
  for (int i = 0; i < a.length; i++) if (a[i] <= 0L || (i > 0 && a[i] <= a[i - 1])) return false;
  return true;
}""")
M(reg, r"""
public static @PKG@.RegData parseReg(java.util.List lines) {
  @PKG@.RegData r = new @PKG@.RegData();
  Object[] thr = new Object[4];
  thr[0] = new long[] { 50L, 100L, 250L, 500L, 1000L, 2500L, 5000L, 10000L, 25000L, 50000L };
  thr[1] = new long[] { 50L, 100L, 250L, 500L, 1000L, 2500L, 5000L, 10000L, 20000L };
  thr[2] = new long[] { 25L, 50L, 100L, 250L, 500L, 1000L, 2500L, 5000L };
  thr[3] = new long[] { 10L, 25L, 50L, 100L, 250L, 500L, 1000L };
  r.coins = new long[] { 50L, 100L, 200L, 400L, 800L, 1500L, 3000L, 6000L, 12000L, 25000L };
  r.xp = new long[] { 0L, 0L, 500L, 0L, 2500L, 0L, 10000L, 0L, 0L, 0L };
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < lines.size(); i++) {
    String ln = String.valueOf(lines.get(i)).trim();
    if (ln.length() == 0 || ln.startsWith("#")) continue;
    int eq = ln.indexOf('=');
    if (eq <= 0) continue;
    String k = ln.substring(0, eq).trim();
    String v = ln.substring(eq + 1).trim();
    if (k.startsWith("coll.")) { rows.add(new String[] { k.substring(5).trim(), v }); continue; }
    for (int c = 0; c < 4; c++) {
      if (k.equalsIgnoreCase("curve." + CURVES[c])) {
        long[] a = longs(v, (long[]) thr[c]);
        if (ascending(a) && a.length <= 20) thr[c] = a; else @PKG@.CollUtil.warn("curve." + CURVES[c] + " must be 1-20 rising numbers - kept the default");
      }
    }
    if (k.equals("tier.coins")) r.coins = longs(v, r.coins);
    if (k.equals("tier.xp")) r.xp = longs(v, r.xp);
    if (k.equals("tier.lastXp")) { try { r.lastXp = Long.parseLong(v); } catch (Throwable t) { } }
    if (k.equals("combat.coinMultiplier")) { try { r.combatMult = Double.parseDouble(v); } catch (Throwable t) { } }
  }
  int n = rows.size();
  r.id = new String[n]; r.cat = new int[n]; r.curve = new int[n]; r.name = new String[n]; r.icon = new String[n];
  r.items = new Object[n]; r.hidden = new boolean[n]; r.nobypass = new boolean[n]; r.from = new String[n]; r.iconOk = new boolean[n];
  r.itemColl = new java.util.HashMap(); r.byId = new java.util.HashMap();
  int m = 0;
  for (int i = 0; i < n; i++) {
    String[] kv = (String[]) rows.get(i);
    String[] f = kv[1].split("\\|", -1);
    if (f.length < 5 || kv[0].length() == 0) { @PKG@.CollUtil.warn("collections.properties: bad line coll." + kv[0]); continue; }
    int cat = catIndex(f[0].trim());
    if (cat < 0) { @PKG@.CollUtil.warn("collections.properties: unknown category " + f[0] + " in coll." + kv[0]); continue; }
    if (r.byId.containsKey(kv[0].toLowerCase())) { @PKG@.CollUtil.warn("collections.properties: coll." + kv[0] + " is defined twice - the first one is used"); continue; }
    String[] its = @PKG@.CollUtil.csv(f[4]);
    java.util.ArrayList keep = new java.util.ArrayList();
    for (int j = 0; j < its.length; j++) {
      if (r.itemColl.containsKey(its[j])) { @PKG@.CollUtil.warn("collections.properties: item " + its[j] + " is in two collections - it only counts for the first"); continue; }
      keep.add(its[j]);
    }
    if (keep.isEmpty()) { @PKG@.CollUtil.warn("collections.properties: coll." + kv[0] + " has no items"); continue; }
    for (int j = 0; j < keep.size(); j++) r.itemColl.put(keep.get(j), Integer.valueOf(m));
    r.id[m] = kv[0];
    r.cat[m] = cat;
    r.curve[m] = curveIndex(f[1].trim());
    r.name[m] = f[2].trim().length() > 0 ? f[2].trim() : kv[0];
    r.items[m] = (String[]) keep.toArray(new String[0]);
    r.icon[m] = f[3].trim().length() > 0 ? f[3].trim() : (String) keep.get(0);
    String flags = f.length > 5 ? f[5].toLowerCase() : "";
    r.hidden[m] = "Fishing".equals(CATS[cat]) || flags.indexOf("hidden") >= 0;
    r.nobypass[m] = flags.indexOf("nobypass") >= 0;
    r.from[m] = f.length > 6 ? f[6].trim() : "";
    r.iconOk[m] = true;
    r.byId.put(kv[0].toLowerCase(), Integer.valueOf(m));
    m++;
  }
  r.n = m;
  r.thr = thr;
  return r;
}""")
M(reg, r"""
public static String loadReg() {
  java.nio.file.Path f = BASE.resolve("collections.properties");
  java.util.List lines = null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) @PKG@.CollIO.writeText(f, regText());
    lines = @PKG@.CollIO.readLines(f);
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not read collections.properties - using the built-in defaults: " + t); }
  @PKG@.RegData r = null;
  if (lines != null) r = parseReg(lines);
  if (r == null || r.n == 0) {
    if (lines != null) @PKG@.CollUtil.warn("collections.properties defines no collections - using the built-in defaults");
    r = parseReg(splitLines(regText()));
  }
  D = r;
  return r.n + " collections";
}""")
M(reg, r"""
public static String[] concat(String[] a, String[] b) {
  String[] o = new String[a.length + b.length];
  for (int i = 0; i < a.length; i++) o[i] = a[i];
  for (int i = 0; i < b.length; i++) o[a.length + i] = b[i];
  return o;
}""")
M(reg, r"""
public static String loadRewards() {
  java.nio.file.Path f = BASE.resolve("rewards.properties");
  java.util.List lines = null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) @PKG@.CollIO.writeText(f, rewardsText());
    lines = @PKG@.CollIO.readLines(f);
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not read rewards.properties - using the built-in defaults: " + t); }
  if (lines == null) lines = splitLines(rewardsText());
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < lines.size(); i++) {
    String ln = String.valueOf(lines.get(i)).trim();
    if (ln.length() == 0 || ln.startsWith("#")) continue;
    int eq = ln.indexOf('=');
    if (eq <= 0) continue;
    String k = ln.substring(0, eq).trim();
    int dot = k.lastIndexOf('.');
    if (dot <= 0) continue;
    int tier = 0;
    try { tier = Integer.parseInt(k.substring(dot + 1).trim()); } catch (Throwable t) { }
    if (tier < 1 || tier > 20) { @PKG@.CollUtil.warn("rewards.properties: bad tier in " + k); continue; }
    String key = k.substring(0, dot).trim().toLowerCase() + "." + tier;
    String[] toks = @PKG@.CollUtil.csv(ln.substring(eq + 1));
    String[] prev = (String[]) m.get(key);
    m.put(key, prev == null ? toks : concat(prev, toks));
  }
  REWARDS = m;
  VALIDATED = false;
  return m.size() + " reward row(s)";
}""")
M(reg, r"""
public static long cfgLong(java.util.Properties p, String k, long def) {
  try { return Long.parseLong(String.valueOf(p.getProperty(k, String.valueOf(def))).trim()); } catch (Throwable t) { return def; }
}""")
M(reg, r"""
public static java.util.HashSet lowerSet(String v) {
  java.util.HashSet s = new java.util.HashSet();
  String[] p = @PKG@.CollUtil.csv(v);
  for (int i = 0; i < p.length; i++) s.add(p[i].toLowerCase());
  return s;
}""")
M(reg, r"""
public static String loadConfig() {
  java.nio.file.Path f = BASE.resolve("config.properties");
  java.util.Properties p = new java.util.Properties();
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) @PKG@.CollIO.writeText(f, configText());
    p = @PKG@.CollIO.read(f);
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not read config.properties - using defaults: " + t); }
  MIGRATE = String.valueOf(p.getProperty("migrate", "convert")).trim().toLowerCase();
  AUTO = "true".equalsIgnoreCase(String.valueOf(p.getProperty("auto", "false")).trim());
  EXCLUDE = lowerSet(p.getProperty("exclude.benches", "Alchemybench,Cookingbench,Furnace,Tannery,Campfire,Salvagebench"));
  CAP_CREDIT = cfgLong(p, "cap.perCredit", 256L);
  CAP_MINUTE = cfgLong(p, "cap.perMinute", 20000L);
  BYPASS = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bypass.enabled", "true")).trim());
  try { BYP_MULT = Double.parseDouble(String.valueOf(p.getProperty("bypass.multiplier", "5")).trim()); } catch (Throwable t) { BYP_MULT = 5.0; }
  BYP_MIN = cfgLong(p, "bypass.minPrice", 500L);
  long[] fb = longs(p.getProperty("bypass.fallback"), new long[] { 2L, 5L, 25L, 100L });
  BYP_FALLBACK = fb.length == 4 ? fb : new long[] { 2L, 5L, 25L, 100L };
  BYP_WALL = ints(p.getProperty("bypass.walls"), new int[] { 5, 4, 3, 0 }, 4);
  java.util.HashSet srcs = lowerSet(p.getProperty("bridge.add.sources", "skills:double,skills:felled"));
  boolean felled = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bridge.add.felled", "true")).trim());
  if (felled) srcs.add("skills:felled"); else srcs.remove("skills:felled");
  ADD_SOURCES = srcs;
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS + " felled=" + felled;
}""")
M(reg, r"""
public static String loadAll() {
  String a = loadConfig();
  String b = loadReg();
  String c = loadRewards();
  return b + ", " + c + ", " + a;
}""")
M(reg, r"""
public static int maxTier(@PKG@.RegData R, int c) {
  return ((long[]) R.thr[R.curve[c]]).length;
}""")
M(reg, r"""
public static long threshold(@PKG@.RegData R, int c, int t) {
  long[] a = (long[]) R.thr[R.curve[c]];
  return t >= 1 && t <= a.length ? a[t - 1] : 0L;
}""")
M(reg, r"""
public static int tierOf(@PKG@.RegData R, int c, long n) {
  long[] a = (long[]) R.thr[R.curve[c]];
  int t = 0;
  for (int i = 0; i < a.length; i++) if (n >= a[i]) t = i + 1;
  return t;
}""")
M(reg, r"""
public static boolean excluded(@CRR@ r) {
  try {
    @BRQ@[] br = r.getBenchRequirement();
    if (br == null) return false;
    for (int i = 0; i < br.length; i++) if (br[i] != null && br[i].id != null && EXCLUDE.contains(br[i].id.toLowerCase())) return true;
  } catch (Throwable t) { }
  return false;
}""")
M(reg, r"""
public static boolean itemExists(String id) {
  try { return id != null && @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}""")
# after the asset stores loaded (start(), reload): recipe ids -> RECIPES["c.t"], registry item / icon check. Logged, never fatal.
M(reg, r"""
public static synchronized String validate() {
  @PKG@.RegData R = D;
  if (R == null) return "no registry";
  int bad = 0;
  StringBuilder bs = new StringBuilder();
  for (int c = 0; c < R.n; c++) {
    R.iconOk[c] = itemExists(R.icon[c]);
    String[] its = (String[]) R.items[c];
    for (int j = 0; j < its.length; j++) if (!itemExists(its[j])) { bad++; if (bs.length() < 400) bs.append(its[j]).append(' '); }
  }
  if (bad > 0) @PKG@.CollUtil.warn(bad + " collection item id(s) are not game items (typo in collections.properties?): " + bs);
  java.util.HashMap out = new java.util.HashMap();
  int ok = 0; int miss = 0; int excl = 0;
  StringBuilder ms = new StringBuilder();
  java.util.HashMap rw = REWARDS;
  for (int c = 0; c < R.n; c++) {
    int mx = maxTier(R, c);
    for (int t = 1; t <= mx; t++) {
      String[] toks = (String[]) rw.get(R.id[c].toLowerCase() + "." + t);
      if (toks == null) continue;
      java.util.ArrayList ids = new java.util.ArrayList();
      for (int i = 0; i < toks.length; i++) {
        if (!toks[i].startsWith("recipe:")) continue;
        String rid = toks[i].substring(7).trim();
        @CRR@ rr = null;
        try { rr = (@CRR@) @CRR@.getAssetMap().getAsset(rid); } catch (Throwable t2) { }
        if (rr == null) { miss++; if (ms.length() < 400) ms.append(rid).append(' '); continue; }
        if (excluded(rr)) { excl++; continue; }
        ids.add(rid);
        ok++;
      }
      if (!ids.isEmpty()) out.put(c + "." + t, (String[]) ids.toArray(new String[0]));
    }
  }
  java.util.Iterator it = rw.keySet().iterator();
  StringBuilder uk = new StringBuilder();
  while (it.hasNext()) {
    String k = (String) it.next();
    String cid = k.substring(0, k.lastIndexOf('.'));
    if (!R.byId.containsKey(cid) && uk.indexOf(cid + " ") < 0 && uk.length() < 300) uk.append(cid).append(' ');
  }
  if (uk.length() > 0) @PKG@.CollUtil.warn("rewards.properties names unknown collection(s): " + uk);
  RECIPES = out;
  VALIDATED = true;
  String res = ok + " recipe unlock(s)";
  if (miss > 0) { res = res + ", " + miss + " unknown recipe id(s) skipped"; @PKG@.CollUtil.warn("rewards.properties: unknown recipe id(s) skipped: " + ms); }
  if (excl > 0) res = res + ", " + excl + " on excluded benches skipped";
  return res;
}""")
M(reg, r"""
public static String[] recipesAt(int c, int t) {
  Object o = RECIPES.get(c + "." + t);
  return o == null ? EMPTY : (String[]) o;
}""")
M(reg, r"""
public static long coinsAt(@PKG@.RegData R, int c, int t) {
  long base = 0L;
  if (R.coins != null && R.coins.length > 0) base = R.coins[t - 1 < R.coins.length ? t - 1 : R.coins.length - 1];
  if ("Combat".equals(CATS[R.cat[c]])) {
    int mx = maxTier(R, c);
    if (t == 3 || t == 5 || t == 7 || t == mx) base = Math.round(base * R.combatMult);
  }
  String[] toks = (String[]) REWARDS.get(R.id[c].toLowerCase() + "." + t);
  if (toks != null) {
    for (int i = 0; i < toks.length; i++) {
      if (!toks[i].startsWith("coins:")) continue;
      try { base += Long.parseLong(toks[i].substring(6).trim()); } catch (Throwable e) { }
    }
  }
  return base < 0L ? 0L : base;
}""")
# Object[]{String skill, Long xp} per grant: Farming/Mining/Foraging collections pay their own skill (tier.xp, lastXp on the last tier)
M(reg, r"""
public static java.util.ArrayList xpAt(@PKG@.RegData R, int c, int t) {
  java.util.ArrayList out = new java.util.ArrayList();
  String cn = CATS[R.cat[c]];
  if (cn.equals("Farming") || cn.equals("Mining") || cn.equals("Foraging")) {
    long x = 0L;
    if (t == maxTier(R, c)) x = R.lastXp;
    else if (R.xp != null && t - 1 < R.xp.length) x = R.xp[t - 1];
    if (x > 0L) out.add(new Object[] { cn, Long.valueOf(x) });
  }
  String[] toks = (String[]) REWARDS.get(R.id[c].toLowerCase() + "." + t);
  if (toks != null) {
    for (int i = 0; i < toks.length; i++) {
      if (!toks[i].startsWith("xp:")) continue;
      String[] p = toks[i].split(":");
      if (p.length != 3) continue;
      try { long v = Long.parseLong(p[2].trim()); if (v > 0L) out.add(new Object[] { p[1].trim(), Long.valueOf(v) }); } catch (Throwable e) { }
    }
  }
  return out;
}""")
M(reg, r"""
public static String rewardText(@PKG@.RegData R, int c, int t) {
  StringBuilder sb = new StringBuilder();
  String[] rs = recipesAt(c, t);
  for (int i = 0; i < rs.length; i++) { if (sb.length() > 0) sb.append(" - "); sb.append(@PKG@.CollUtil.prettyRecipe(rs[i])).append(" recipe"); }
  long co = coinsAt(R, c, t);
  if (co > 0L) { if (sb.length() > 0) sb.append(" - "); sb.append('+').append(@PKG@.CollUtil.fmt(co)).append(" coins"); }
  java.util.ArrayList xs = xpAt(R, c, t);
  for (int i = 0; i < xs.size(); i++) {
    Object[] a = (Object[]) xs.get(i);
    if (sb.length() > 0) sb.append(" - ");
    sb.append('+').append(@PKG@.CollUtil.fmt(((Long) a[1]).longValue())).append(' ').append((String) a[0]).append(" XP");
  }
  return sb.length() == 0 ? "-" : sb.toString();
}""")
# one line per reward (chat after a tier-up; the first one is the "Next:" line on a card)
M(reg, r"""
public static java.util.ArrayList rewardLines(@PKG@.RegData R, int c, int t) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] rs = recipesAt(c, t);
  for (int i = 0; i < rs.length; i++) out.add(@PKG@.CollUtil.prettyRecipe(rs[i]) + " recipe");
  long co = coinsAt(R, c, t);
  if (co > 0L) out.add("+" + @PKG@.CollUtil.fmt(co) + " coins");
  java.util.ArrayList xs = xpAt(R, c, t);
  for (int i = 0; i < xs.size(); i++) {
    Object[] a = (Object[]) xs.get(i);
    out.add("+" + @PKG@.CollUtil.fmt(((Long) a[1]).longValue()) + " " + (String) a[0] + " XP");
  }
  return out;
}""")
# /coll <name>: exact id or name (spaces ignored), then a 3+ letter prefix; hidden collections are never matched
M(reg, r"""
public static int find(String q) {
  @PKG@.RegData R = D;
  if (R == null || q == null) return -1;
  String s = q.trim().toLowerCase().replace(" ", "").replace("_", "");
  if (s.length() == 0) return -1;
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    if (R.id[c].toLowerCase().equals(s) || R.name[c].toLowerCase().replace(" ", "").equals(s)) return c;
  }
  if (s.length() < 3) return -1;
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    if (R.id[c].toLowerCase().startsWith(s) || R.name[c].toLowerCase().replace(" ", "").startsWith(s)) return c;
  }
  return -1;
}""")
M(reg, r"""
public static String listString() {
  @PKG@.RegData R = D;
  StringBuilder sb = new StringBuilder();
  if (R == null) return "";
  for (int c = 0; c < R.n; c++) { if (sb.length() > 0) sb.append(','); sb.append(R.id[c]).append(':').append(CATS[R.cat[c]]); }
  return sb.toString();
}""")

# ================= CollDrops: the engine's break drops, with the tool entry resolved from the held item =================
M(drp, r"""
public static String toolKey(String held) {
  if (held == null) return null;
  if (held.startsWith("Tool_Pickaxe_")) return "Pickaxe";
  if (held.startsWith("Tool_Shears_")) return "Shears";
  if (held.equals("Tool_Bark_Scraper")) return "Scraper";
  return null;
}""")
# a Tools entry WITHOUT a State breaks the block with its own drops; entries WITH a State (Scraper -> Stripped) change the block
M(drp, r"""
public static boolean toolDependent(@BGA@ g) {
  try {
    java.util.Map td = g.getToolData();
    if (td == null || td.isEmpty()) return false;
    java.util.Iterator it = td.values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @BTD@ && ((@BTD@) o).getStateId() == null) return true;
    }
    return false;
  } catch (Throwable t) { return true; }
}""")
M(drp, r"""
public static @BTD@ toolData(@BGA@ g, String key) {
  if (g == null || key == null) return null;
  java.util.Map td = g.getToolData();
  if (td == null || td.isEmpty()) return null;
  Object o = td.get(key);
  if (o instanceof @BTD@) return (@BTD@) o;
  java.util.Iterator it = td.values().iterator();
  while (it.hasNext()) {
    Object v = it.next();
    if (v instanceof @BTD@ && key.equalsIgnoreCase(((@BTD@) v).getTypeId())) return (@BTD@) v;
  }
  return null;
}""")
# BlockHarvestUtils.damageSingleBlock: tool entry (no state) -> its drops; Breaking -> getDrops(bt, qty, itemId, list);
# soft -> getDrops(bt, 1, soft itemId, soft list); Soft AND Breaking on one block -> which applied is unknown -> nothing
M(drp, r"""
public static java.util.List breakDrops(@BTY@ bt, String held) {
  if (bt == null) return null;
  @BGA@ g = bt.getGathering();
  if (g == null) return null;
  @BTD@ td = toolData(g, toolKey(held));
  if (td != null) {
    if (td.getStateId() != null) return null;
    return @BHU@.getDrops(bt, 1, td.getItemId(), td.getDropListId());
  }
  @BBD@ br = g.getBreaking();
  if (g.isSoft()) {
    if (br != null) return null;
    @SBD@ so = g.getSoft();
    if (so == null) return null;
    return @BHU@.getDrops(bt, 1, so.getItemId(), so.getDropListId());
  }
  if (br == null) return null;
  int q = br.getQuantity();
  if (q <= 0) q = 1;
  return @BHU@.getDrops(bt, q, br.getItemId(), br.getDropListId());
}""")
# the engine's placed-block flag (damageSingleBlock: UseDefaultDropWhenPlaced && BlockPhysics.isDeco on the chunk SECTION ref,
# world coordinates -> the block drops itself). Read while the block still exists (BreakBlockEvent handler, world thread).
M(drp, r"""
public static boolean decoAt(@WLD@ w, @BTY@ bt, int x, int y, int z) {
  try {
    @BGA@ g = bt.getGathering();
    if (g == null || !g.shouldUseDefaultDropWhenPlaced()) return false;
    @CHS@ cs = w.getChunkStore();
    if (cs == null) return false;
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return false;
    @BPH@ bp = (@BPH@) cs.getStore().getComponent(sr, @BPH@.getComponentType());
    return bp != null && bp.isDeco(x, y, z);
  } catch (Throwable t) { return false; }
}""")

# ================= CollMigrate: 0.1 block counts -> 0.2 item counts (start(), or on first load of a file) =================
M(mig, r"""
public static boolean ready() {
  try {
    @BTM@ am = @BTY@.getAssetMap();
    return am != null && (am.getIndexOrDefault("Rock_Stone", -1) >= 0 || am.getNextIndex() > 100);
  } catch (Throwable t) { return false; }
}""")
M(mig, r"""
public static java.util.Properties convert(java.util.Properties old, StringBuilder log, String key) {
  java.util.Properties out = new java.util.Properties();
  @PKG@.RegData R = @PKG@.CollReg.D;
  boolean reset = "reset".equals(@PKG@.CollReg.MIGRATE);
  java.util.LinkedHashMap add = new java.util.LinkedHashMap();
  boolean had = false;
  java.util.Enumeration en = old.propertyNames();
  while (en.hasMoreElements()) {
    String k = (String) en.nextElement();
    String v = old.getProperty(k);
    if (k.startsWith("_")) { if (!k.equals("_schema") && !k.equals("_mignote")) out.setProperty(k, v); continue; }
    long n = 0L;
    try { n = Long.parseLong(String.valueOf(v).trim()); } catch (Throwable t) { log.append(key).append("  ").append(k).append('=').append(v).append("  dropped (not a number)\n"); continue; }
    if (n <= 0L) continue;
    had = true;
    if (reset) { log.append(key).append("  ").append(k).append('=').append(n).append("  reset\n"); continue; }
    String item = null;
    long mul = 1L;
    try {
      @BTM@ am = @BTY@.getAssetMap();
      int idx = am.getIndexOrDefault(k, -1);
      @BTY@ bt = null;
      if (idx >= 0) bt = (@BTY@) am.getAsset(idx);
      if (bt != null) {
        @BGA@ g = bt.getGathering();
        if (g != null && !g.isSoft() && g.getSoft() == null && !@PKG@.CollDrops.toolDependent(g)) {
          @BBD@ br = g.getBreaking();
          if (br != null && br.getItemId() != null && br.getDropListId() == null && R.itemColl.containsKey(br.getItemId())) {
            item = br.getItemId();
            if (br.getQuantity() > 1) mul = (long) br.getQuantity();
          }
        }
      }
    } catch (Throwable t) { }
    if (item == null && R.itemColl.containsKey(k)) item = k;
    if (item == null) { log.append(key).append("  ").append(k).append('=').append(n).append("  dropped (no exact item)\n"); continue; }
    long[] cur = (long[]) add.get(item);
    if (cur == null) { cur = new long[1]; add.put(item, cur); }
    cur[0] = cur[0] + n * mul;
    log.append(key).append("  ").append(k).append('=').append(n).append("  -> ").append(item).append(" +").append(n * mul).append('\n');
  }
  java.util.Iterator it = add.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    out.setProperty((String) e.getKey(), String.valueOf(((long[]) e.getValue())[0]));
  }
  out.setProperty("_schema", "2");
  if (had) out.setProperty("_mignote", "1");
  return out;
}""")
M(mig, r"""
public static java.util.Properties convertFile(java.nio.file.Path dir, String key, java.util.Properties old) throws java.io.IOException {
  java.nio.file.Path base = dir.getParent();
  @PKG@.CollIO.copyIfMissing(dir.resolve(key + ".properties"), base.resolve("counts-0.1").resolve(key + ".properties"));
  StringBuilder log = new StringBuilder();
  java.util.Properties np = convert(old, log, key);
  @PKG@.CollIO.write(dir, key, np);
  @PKG@.CollIO.append(base.resolve("migration-0.2.log"), "# " + new java.util.Date() + " (" + @PKG@.CollReg.MIGRATE + ")\n" + log);
  return np;
}""")
M(mig, r"""
public static String runStart(java.nio.file.Path dir) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  if (R == null || R.n == 0) { @PKG@.CollUtil.warn("migration skipped: no collections loaded - retried at the next start"); return "migration skipped"; }
  if (!ready()) { @PKG@.CollUtil.warn("migration skipped: block assets are not loaded yet - retried at the next start and when a file is first read"); return "migration skipped"; }
  int done = 0; int failed = 0;
  try {
    java.io.File[] fs = dir.toFile().listFiles();
    if (fs != null) {
      for (int i = 0; i < fs.length; i++) {
        String fn = fs[i].getName();
        if (!fn.endsWith(".properties")) continue;
        String key = fn.substring(0, fn.length() - 11);
        try {
          java.util.Properties p = @PKG@.CollIO.read(fs[i].toPath());
          if ("2".equals(String.valueOf(p.getProperty("_schema", "")).trim())) continue;
          convertFile(dir, key, p);
          done++;
        } catch (Throwable t) { failed++; @PKG@.CollUtil.warn("could not migrate counts/" + fn + " (left untouched, retried later): " + t); }
      }
    }
    java.nio.file.Path u = dir.getParent().resolve("unlocks.properties");
    java.nio.file.Path u2 = dir.getParent().resolve("unlocks-0.1.properties");
    if (java.nio.file.Files.exists(u, new java.nio.file.LinkOption[0]) && !java.nio.file.Files.exists(u2, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.move(u, u2, new java.nio.file.CopyOption[0]);
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("migration pass failed: " + t); }
  if (done > 0) @PKG@.CollUtil.info("migrated " + done + " counts file(s) from 0.1 block counts to item counts (originals in counts-0.1/, details in migration-0.2.log)");
  return done + " file(s) migrated" + (failed > 0 ? ", " + failed + " failed" : "");
}""")

# ================= CollData / CollStore: per-profile counts (pkey), the 0.1.5 read/save rules =================
C(cdat, "public CollData() { this.items = new java.util.concurrent.ConcurrentHashMap(); this.meta = new java.util.concurrent.ConcurrentHashMap(); this.name = null; }")
M(sto, r"""
public static @PKG@.CollData fromProps(java.util.Properties p) {
  @PKG@.CollData d = new @PKG@.CollData();
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {
    String k = (String) en.nextElement();
    String v = p.getProperty(k);
    if (k.equals("_name")) { d.name = v; continue; }
    long n = 0L;
    try { n = Long.parseLong(String.valueOf(v).trim()); } catch (Throwable t) { continue; }
    if (k.startsWith("_")) d.meta.put(k, Long.valueOf(n)); else d.items.put(k, Long.valueOf(n));
  }
  return d;
}""")
# null = the file exists but cannot be read: never cached as empty (the next flush would overwrite it), retried every 2 s
M(sto, r"""
public static @PKG@.CollData dataK(String key) {
  @PKG@.CollData d = (@PKG@.CollData) DATA.get(key);
  if (d != null) return d;
  Long bad = (Long) BROKEN.get(key);
  if (bad != null && System.currentTimeMillis() - bad.longValue() < 2000L) return null;
  java.util.Properties p = null;
  try {
    p = @PKG@.CollIO.read(DIR.resolve(key + ".properties"));
  } catch (Throwable t) {
    if (BROKEN.put(key, Long.valueOf(System.currentTimeMillis())) == null) @PKG@.CollUtil.warn("could not read counts/" + key + ".properties - nothing is counted for that profile and the file is left untouched until it reads again (retried every 2 s while needed): " + t);
    return null;
  }
  if (BROKEN.remove(key) != null) @PKG@.CollUtil.warn("counts/" + key + ".properties reads again");
  if (!p.isEmpty() && !"2".equals(String.valueOf(p.getProperty("_schema", "")).trim()) && @PKG@.CollMigrate.ready()) {
    try { p = @PKG@.CollMigrate.convertFile(DIR, key, p); } catch (Throwable t) { @PKG@.CollUtil.warn("could not migrate counts/" + key + ".properties on load: " + t); }
  }
  d = fromProps(p);
  @PKG@.CollData prev = (@PKG@.CollData) DATA.putIfAbsent(key, d);
  return prev != null ? prev : d;
}""")
M(sto, r"""
public static @PKG@.CollData data(java.util.UUID u) {
  return dataK(@PKG@.CollUtil.pkey(u));
}""")
M(sto, r"""
public static boolean save(String key) {
  try {
    @PKG@.CollData d = (@PKG@.CollData) DATA.get(key);
    if (d == null) return true;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = d.items.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    it = d.meta.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    p.setProperty("_schema", "2");
    if (d.name != null) p.setProperty("_name", d.name);
    @PKG@.CollIO.write(DIR, key, p);
    return true;
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not save counts/" + key + ".properties (retried at the next flush): " + t); return false; }
}""")
M(sto, r"""
public static void flushDirty() {
  java.util.ArrayList failed = new java.util.ArrayList();
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    it.remove();
    if (!save(key)) failed.add(key);
  }
  for (int i = 0; i < failed.size(); i++) DIRTY.put(failed.get(i), Boolean.TRUE);
}""")
M(sto, r"""
public static long sumMap(java.util.Map m, String[] its) {
  long s = 0L;
  for (int i = 0; i < its.length; i++) {
    Object o = m.get(its[i]);
    if (o instanceof Long) s += ((Long) o).longValue();
    else if (o instanceof String) { try { s += Long.parseLong(((String) o).trim()); } catch (Throwable t) { } }
  }
  return s;
}""")
M(sto, r"""
public static long sum(@PKG@.CollData d, @PKG@.RegData R, int c) {
  if (d == null || R == null || c < 0 || c >= R.n) return 0L;
  return sumMap(d.items, (String[]) R.items[c]);
}""")
# {old collection total, new collection total}; memory only, no I/O under the monitor
M(sto, r"""
public static synchronized long[] addLocked(@PKG@.CollData d, String key, @PKG@.RegData R, int c, String item, long q) {
  long before = sum(d, R, c);
  Long v = (Long) d.items.get(item);
  long nv = (v == null ? 0L : v.longValue()) + q;
  if (nv < 0L) nv = Long.MAX_VALUE;
  d.items.put(item, Long.valueOf(nv));
  DIRTY.put(key, Boolean.TRUE);
  return new long[] { before, sum(d, R, c) };
}""")
M(sto, r"""
public static long meta(@PKG@.CollData d, String k) {
  Object o = null;
  if (d != null) o = d.meta.get(k);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")
M(sto, r"""
public static synchronized void setMeta(@PKG@.CollData d, String key, String k, long v) {
  if (v <= 0L) d.meta.remove(k); else d.meta.put(k, Long.valueOf(v));
  DIRTY.put(key, Boolean.TRUE);
}""")
M(sto, r"""
public static void noteName(String key, String nm) {
  if (key == null || nm == null || nm.length() == 0) return;
  @PKG@.CollData d = (@PKG@.CollData) DATA.get(key);
  if (d == null || nm.equals(d.name)) return;
  d.name = nm;
  DIRTY.put(key, Boolean.TRUE);
}""")
M(sto, r"""
public static int countTier(@PKG@.CollData d, @PKG@.RegData R, int c) {
  return @PKG@.CollReg.tierOf(R, c, sum(d, R, c));
}""")
M(sto, r"""
public static int boughtTier(@PKG@.CollData d, @PKG@.RegData R, int c) {
  long b = meta(d, "_bought." + R.id[c]);
  int mx = @PKG@.CollReg.maxTier(R, c);
  return b > (long) mx ? mx : (int) b;
}""")
M(sto, r"""
public static int effTier(@PKG@.CollData d, @PKG@.RegData R, int c) {
  int a = countTier(d, R, c);
  int b = boughtTier(d, R, c);
  return a > b ? a : b;
}""")
# {score (count tiers of visible collections), found, maxed, bought tiers, total tiers}
M(sto, r"""
public static long[] stats(@PKG@.CollData d, @PKG@.RegData R) {
  long[] s = new long[5];
  if (d == null || R == null) return s;
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    long sm = sum(d, R, c);
    int ct = @PKG@.CollReg.tierOf(R, c, sm);
    int mx = @PKG@.CollReg.maxTier(R, c);
    s[0] += ct;
    if (sm > 0L) s[1]++;
    if (ct >= mx) s[2]++;
    s[3] += boughtTier(d, R, c);
    s[4] += mx;
  }
  return s;
}""")

# ================= CollRewards: coins + skill XP per tier, owed-and-retry (separate paid markers, never paid twice) =================
# true only when SkyyCoins really paid (its add fn returns the new balance, or null when nothing changed) - SkyySkills pattern
M(rew, r"""
public static boolean coinsAdd(java.util.UUID u, long n) {
  Object f = null;
  try {
    f = @PKG@.CollUtil.bridge().get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    if (r instanceof Number) return true;
  } catch (Throwable t) { }
  long now = System.currentTimeMillis();
  if (f != null && now - WARNC > 60000L) { WARNC = now; @PKG@.CollUtil.warn("coins:fn:add did not pay " + n + " coins to " + u + " - that collection reward stays owed and is retried"); }
  return false;
}""")
# SkyySkills 0.4 XP-grant bridge: apply(Object[]{UUID, String skill, Number baseXp, String source, String expectKey}) -> Boolean
# (expectKey = our profile key: SkyySkills refuses the grant if the active profile changed before it applies it)
M(rew, r"""
public static boolean xpAdd(java.util.UUID u, String skill, long n, String src, String key) {
  Object f = null;
  try {
    f = @PKG@.CollUtil.bridge().get("skill:fn:addxp");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, skill, Long.valueOf(n), src, key });
    if (Boolean.TRUE.equals(r)) return true;
  } catch (Throwable t) { }
  long now = System.currentTimeMillis();
  if (now - WARNX > 600000L) { WARNX = now; @PKG@.CollUtil.warn("skill:fn:addxp " + (f == null ? "is missing (SkyySkills 0.4+ not loaded)" : "refused " + n + " " + skill + " XP") + " - collection XP rewards stay owed and are retried"); }
  return false;
}""")
M(rew, r"""
public static boolean owedAny(@PKG@.CollData d, @PKG@.RegData R) {
  if (d == null || R == null) return false;
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    int ct = @PKG@.CollStore.countTier(d, R, c);
    if (ct <= 0) continue;
    if (@PKG@.CollStore.meta(d, "_paid." + R.id[c]) < (long) ct || @PKG@.CollStore.meta(d, "_paidxp." + R.id[c]) < (long) ct) return true;
  }
  return false;
}""")
M(rew, r"""
public static void mark(String key, @PKG@.CollData d, @PKG@.RegData R) {
  if (owedAny(d, R)) OWED.add(key); else OWED.remove(key);
}""")
# world thread, active profile only. {coins paid, xp paid, 1 = something is still owed}. synchronized: a queued retry on the old world
# thread can overlap a credit on the new one after a world switch - the paid markers are read and advanced under one monitor
# (SkyyCoins / SkyySkills never call back into this mod, so holding it across their functions cannot deadlock)
M(rew, r"""
public static synchronized long[] settle(@PKG@.CollData d, @PKG@.RegData R, int c, java.util.UUID u, String key) {
  long[] res = new long[3];
  if (d == null || R == null || R.hidden[c]) return res;
  if (!key.equals(@PKG@.CollUtil.pkey(u))) { res[2] = 1L; return res; }
  int ct = @PKG@.CollStore.countTier(d, R, c);
  String id = R.id[c];
  int pc = (int) @PKG@.CollStore.meta(d, "_paid." + id);
  for (int t = pc + 1; t <= ct; t++) {
    long n = @PKG@.CollReg.coinsAt(R, c, t);
    if (n > 0L && !coinsAdd(u, n)) { res[2] = 1L; break; }
    res[0] += n;
    @PKG@.CollStore.setMeta(d, key, "_paid." + id, (long) t);
  }
  int px = (int) @PKG@.CollStore.meta(d, "_paidxp." + id);
  for (int t = px + 1; t <= ct; t++) {
    java.util.ArrayList xs = @PKG@.CollReg.xpAt(R, c, t);
    boolean ok = true;
    for (int i = 0; i < xs.size(); i++) {
      Object[] a = (Object[]) xs.get(i);
      long amt = ((Long) a[1]).longValue();
      if (xpAdd(u, (String) a[0], amt, "coll:" + id + ":" + t, key)) { res[1] += amt; continue; }
      if (i == 0) { ok = false; break; }
      @PKG@.CollUtil.warn("extra XP reward " + a[0] + " " + amt + " for " + id + " " + t + " was refused and is skipped (the tier's first grant was paid)");
    }
    if (!ok) { res[2] = 1L; break; }
    @PKG@.CollStore.setMeta(d, key, "_paidxp." + id, (long) t);
  }
  return res;
}""")
M(rew, r"""
public static void settleAll(@PR@ pr, java.util.UUID u, String key) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  @PKG@.CollData d = @PKG@.CollStore.dataK(key);
  if (R == null || d == null) return;
  long coins = 0L; long xp = 0L;
  for (int c = 0; c < R.n; c++) {
    long[] r = settle(d, R, c, u, key);
    coins += r[0];
    xp += r[1];
  }
  mark(key, d, R);
  if ((coins > 0L || xp > 0L) && pr != null && pr.isValid()) {
    pr.sendMessage(@MSG@.raw("[Collections] Paid for earlier collection tiers: " + (coins > 0L ? "+" + @PKG@.CollUtil.fmt(coins) + " coins" : "") + (coins > 0L && xp > 0L ? ", " : "") + (xp > 0L ? "+" + @PKG@.CollUtil.fmt(xp) + " skill XP" : "")).color("#ffc800"));
  }
}""")

# ================= CollUnlocks: coll:recipes + summary keys, per profile (the 0.1.5 publish / epoch chain) =================
M(unl, r"""
public static java.util.TreeSet compute(@PKG@.CollData d) {
  java.util.TreeSet out = new java.util.TreeSet();
  @PKG@.RegData R = @PKG@.CollReg.D;
  if (d == null || R == null) return out;
  try {
    if (!@PKG@.CollReg.VALIDATED && @PKG@.CollMigrate.ready()) @PKG@.CollReg.validate();
    for (int c = 0; c < R.n; c++) {
      if (R.hidden[c]) continue;
      int eff = @PKG@.CollStore.effTier(d, R, c);
      for (int t = 1; t <= eff; t++) {
        String[] rs = @PKG@.CollReg.recipesAt(c, t);
        for (int i = 0; i < rs.length; i++) out.add(rs[i]);
      }
    }
    if (!@PKG@.CollReg.AUTO) return out;
    java.util.Iterator rit = @CRR@.getAssetMap().getAssetMap().values().iterator();
    while (rit.hasNext()) {
      @CRR@ r = (@CRR@) rit.next();
      if (r == null || @PKG@.CollReg.excluded(r)) continue;
      @MQ@[] in = r.getInput();
      if (in == null || in.length == 0) continue;
      boolean anyTier = false; boolean blocked = false;
      for (int i = 0; i < in.length; i++) {
        if (in[i] == null || in[i].getItemId() == null) continue;
        Object ci = R.itemColl.get(in[i].getItemId());
        if (!(ci instanceof Integer)) continue;
        int c = ((Integer) ci).intValue();
        long s = @PKG@.CollStore.sum(d, R, c);
        if (s <= 0L) continue;
        if (s >= @PKG@.CollReg.threshold(R, c, 1)) anyTier = true; else blocked = true;
      }
      if (anyTier && !blocked) { String rid = r.getId(); if (rid != null) out.add(rid); }
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("unlock compute failed: " + t); }
  return out;
}""")
M(unl, r"""
public static void bumpEpoch(java.util.UUID u) {
  Long e = (Long) CEPOCH.get(u);
  long n = e == null ? 1L : e.longValue() + 1L;
  CEPOCH.put(u, Long.valueOf(n));
  @PKG@.CollUtil.bridge().put("coll:epoch:" + u.toString(), Long.valueOf(n));
}""")
M(unl, r"""
public static void unpublish(java.util.UUID u) {
  java.util.Map b = @PKG@.CollUtil.bridge();
  b.remove("coll:recipes:" + u.toString());
  b.remove("coll:" + u.toString());
  b.remove("coll:score:" + u.toString());
  PUBLISHED.remove(u);
  EPOCH.remove(u);
  PUBKEY.remove(u);
}""")
# The counts file is loaded BEFORE this monitor (publish()); a key whose file cannot be read publishes nothing (never another
# profile's list). Three passes: SkyyProfiles flips its key function before it bumps the epoch (PROFILES-CONTRACT "Key flip timing").
M(unl, r"""
public static synchronized int publishLocked(java.util.UUID u) {
  try {
    int n = 0;
    for (int pass = 0; pass < 3; pass++) {
      long ep = @PKG@.CollUtil.epochOf(u);
      String key = @PKG@.CollUtil.pkey(u);
      @PKG@.CollData d = (@PKG@.CollData) @PKG@.CollStore.DATA.get(key);
      @PKG@.RegData R = @PKG@.CollReg.D;
      if (d == null || R == null) { unpublish(u); return 0; }
      java.util.TreeSet ids = compute(d);
      StringBuilder sb = new StringBuilder();
      java.util.Iterator it = ids.iterator();
      while (it.hasNext()) { if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }
      long[] s = @PKG@.CollStore.stats(d, R);
      java.util.Map b = @PKG@.CollUtil.bridge();
      b.put("coll:recipes:" + u.toString(), sb.toString());
      b.put("coll:" + u.toString(), "tiers=" + s[0] + ",found=" + s[1] + ",maxed=" + s[2] + ",recipes=" + ids.size() + ",score=" + s[0]);
      b.put("coll:score:" + u.toString(), Long.valueOf(s[0]));
      String sig = key + "|" + s[0] + "|" + s[3] + "|" + ids.size();
      Object last = SIG.put(u, sig);
      if (last == null || !last.equals(sig)) bumpEpoch(u);
      PUBLISHED.put(u, Integer.valueOf(ids.size()));
      EPOCH.put(u, Long.valueOf(ep));
      PUBKEY.put(u, key);
      n = ids.size();
      if (key.equals(@PKG@.CollUtil.pkey(u))) break;
    }
    return n;
  } catch (Throwable t) { @PKG@.CollUtil.warn("publish failed for " + u + ": " + t); return 0; }
}""")
M(unl, r"""
public static int publish(java.util.UUID u) {
  String key = @PKG@.CollUtil.pkey(u);
  @PKG@.CollData d = null;
  try { d = @PKG@.CollStore.dataK(key); } catch (Throwable t) { }
  int n = publishLocked(u);
  if (d != null) @PKG@.CollRewards.mark(key, d, @PKG@.CollReg.D);
  return n;
}""")
M(unl, r"""
public static boolean syncEpoch(java.util.UUID u) {
  try {
    if (u == null || !PUBLISHED.containsKey(u)) return false;
    Long seen = (Long) EPOCH.get(u);
    String key = (String) PUBKEY.get(u);
    if (seen != null && seen.longValue() == @PKG@.CollUtil.epochOf(u) && key != null && key.equals(@PKG@.CollUtil.pkey(u))) return false;
    publish(u);
    return true;
  } catch (Throwable t) { return false; }
}""")
M(unl, r"""
public static void baseline(java.util.UUID u) {
  if (u == null) return;
  if (!PUBLISHED.containsKey(u)) publish(u); else syncEpoch(u);
}""")
M(unl, r"""
public static void checkEpochs() {
  try {
    java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
    while (it.hasNext()) syncEpoch((java.util.UUID) it.next());
  } catch (Throwable t) { }
}""")
# first sight of a player this session (after the baseline publish): the one-time migration line
M(unl, r"""
public static void firstSight(@PR@ pr, java.util.UUID u) {
  try {
    String key = @PKG@.CollUtil.pkey(u);
    @PKG@.CollData d = @PKG@.CollStore.dataK(key);
    if (d == null || @PKG@.CollStore.meta(d, "_mignote") <= 0L) return;
    @PKG@.CollStore.setMeta(d, key, "_mignote", 0L);
    pr.sendMessage(@MSG@.raw("[Collections] Collections now count the items you gather (fiber, sticks, logs, stone, ores, crops, mob drops). Old block counts were converted where exact; the rest start at 0. /collections").color("#7fdcff"));
  } catch (Throwable t) { }
}""")
M(unl, r"""
public static void publishOnline() {
  try {
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) { publish(u); if (PUBLISHED.containsKey(u)) firstSight(pr, u); }
      try { @PKG@.CollStore.noteName(@PKG@.CollUtil.pkey(u), pr.getUsername()); } catch (Throwable t) { }
    }
    PUBLISHED.keySet().retainAll(online);
    EPOCH.keySet().retainAll(online);
    PUBKEY.keySet().retainAll(online);
  } catch (Throwable t) { }
}""")
M(unl, r"""
public static void republishAll() {
  java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
  while (it.hasNext()) publish((java.util.UUID) it.next());
}""")
M(unl, r"""
public static void publishLast(java.util.UUID u, @PKG@.RegData R, int c, long count, int tier) {
  try {
    if (R.hidden[c]) return;
    int mx = @PKG@.CollReg.maxTier(R, c);
    long next = tier < mx ? @PKG@.CollReg.threshold(R, c, tier + 1) : 0L;
    @PKG@.CollUtil.bridge().put("coll:last:" + u.toString(), R.id[c] + "|" + R.name[c] + "|" + tier + "|" + count + "|" + next + "|" + System.currentTimeMillis());
  } catch (Throwable t) { }
}""")
M(unl, r"""
public static void sendUnlocks(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  @PKG@.CollData d = @PKG@.CollStore.data(u);
  if (d == null) { pr.sendMessage(@MSG@.raw("[Collections] your collections could not be read right now - try again in a moment")); return; }
  java.util.TreeSet ids = compute(d);
  publish(u);
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = ids.iterator(); int n = 0;
  while (it.hasNext() && n < 12) { if (sb.length() > 0) sb.append(", "); sb.append(@PKG@.CollUtil.prettyRecipe((String) it.next())); n++; }
  pr.sendMessage(@MSG@.raw("[Collections] " + ids.size() + " recipe(s) unlocked" + (ids.size() > 0 ? ": " + sb + (ids.size() > 12 ? ", ..." : "") + "  -> /craft (Collections tab)" : ". Reach tier I of Wheat, Oak Log or Cobblestone for the first ones.")));
}""")

# ================= CollCredit: the one path every counted item takes =================
M(cred, r"""
public static synchronized long capMinute(java.util.UUID u, long q) {
  long cap = @PKG@.CollReg.CAP_MINUTE;
  if (cap <= 0L) return q;
  long now = System.currentTimeMillis();
  long[] w = (long[]) MINUTE.get(u);
  if (w == null || now - w[0] >= 60000L) { w = new long[] { now, 0L, 0L }; MINUTE.put(u, w); }
  long room = cap - w[1];
  if (room <= 0L) {
    if (w[2] == 0L) { w[2] = 1L; @PKG@.CollUtil.warn(u + " hit the collection cap of " + cap + " items per minute - further items this minute are not counted"); }
    return 0L;
  }
  long take = q < room ? q : room;
  w[1] = w[1] + take;
  return take;
}""")
M(cred, r"""
public static void announce(@PR@ pr, @PKG@.RegData R, int c, int from, int to) {
  for (int t = from; t <= to; t++) {
    pr.sendMessage(@MSG@.raw("COLLECTION UP  " + R.name[c] + " " + @PKG@.CollUtil.roman(t)).color("#ffc800"));
    java.util.ArrayList ls = @PKG@.CollReg.rewardLines(R, c, t);
    for (int i = 0; i < ls.size(); i++) pr.sendMessage(@MSG@.raw("   " + (String) ls.get(i)).color(((String) ls.get(i)).endsWith(" recipe") ? "#c8f0a0" : "#e8d8a0"));
  }
}""")
# world thread. key = the profile the item was gathered for; dropped when the active profile changed in between (spec 3.3).
M(cred, r"""
public static void creditOne(@PR@ pr, java.util.UUID u, String key, String item, long q, boolean admin) {
  try {
    @PKG@.RegData R = @PKG@.CollReg.D;
    if (R == null || item == null || q <= 0L || u == null || key == null) return;
    Object ci = R.itemColl.get(item);
    if (!(ci instanceof Integer)) return;
    int c = ((Integer) ci).intValue();
    if (!key.equals(@PKG@.CollUtil.pkey(u))) return;
    if (!admin) {
      if (@PKG@.CollReg.CAP_CREDIT > 0L && q > @PKG@.CollReg.CAP_CREDIT) q = @PKG@.CollReg.CAP_CREDIT;
      q = capMinute(u, q);
      if (q <= 0L) return;
    }
    @PKG@.CollUnlocks.baseline(u);
    @PKG@.CollData d = @PKG@.CollStore.dataK(key);
    if (d == null) return;
    long[] r = @PKG@.CollStore.addLocked(d, key, R, c, item, q);
    int ot = @PKG@.CollReg.tierOf(R, c, r[0]);
    int nt = @PKG@.CollReg.tierOf(R, c, r[1]);
    @PKG@.CollUnlocks.publishLast(u, R, c, r[1], nt);
    if (R.hidden[c]) return;
    boolean on = pr != null && pr.isValid();
    if (on && r[0] <= 0L && r[1] > 0L) pr.sendMessage(@MSG@.raw("New collection: " + R.name[c] + "!   /collections").color("#7fdcff"));
    if (nt <= ot) return;
    Object was = @PKG@.CollUnlocks.PUBLISHED.get(u);
    int before = was instanceof Integer ? ((Integer) was).intValue() : 0;
    long[] paid = @PKG@.CollRewards.settle(d, R, c, u, key);
    int now = @PKG@.CollUnlocks.publish(u);
    if (!on) return;
    announce(pr, R, c, ot + 1, nt);
    if (now > before) pr.sendMessage(@MSG@.raw("   " + (now - before) + " new recipe(s) in /craft - Collections tab").color("#c8f0a0"));
    if (paid[2] != 0L) pr.sendMessage(@MSG@.raw("   (some rewards are owed - they are paid automatically once SkyyCoins / SkyySkills accept them)").color("#c8b070"));
  } catch (Throwable t) { @PKG@.CollUtil.warn("credit failed: " + t); }
}""")
M(cred, r"""
public static void creditList(@PR@ pr, java.util.UUID u, String key, java.util.List stacks, boolean admin) {
  if (stacks == null || stacks.isEmpty()) return;
  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  for (int i = 0; i < stacks.size(); i++) {
    Object o = stacks.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    long[] v = (long[]) sum.get(is.getItemId());
    if (v == null) { v = new long[1]; sum.put(is.getItemId(), v); }
    v[0] = v[0] + (long) is.getQuantity();
  }
  java.util.Iterator it = sum.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    creditOne(pr, u, key, (String) e.getKey(), ((long[]) e.getValue())[0], admin);
  }
}""")

# ================= CollBypass: coins buy the NEXT tier's recipe unlocks only =================
M(byp, r"""
public static long unitPrice(@PKG@.RegData R, int c) {
  try {
    String first = ((String[]) R.items[c])[0];
    Object o = @PKG@.CollUtil.bridge().get("bazaar:buy:" + first);
    if (o instanceof Number && ((Number) o).longValue() > 0L) return ((Number) o).longValue();
  } catch (Throwable t) { }
  long[] fb = @PKG@.CollReg.BYP_FALLBACK;
  return fb[R.curve[c] < fb.length ? R.curve[c] : fb.length - 1];
}""")
# Object[]{Integer next tier, Long price, String refusal or null}
M(byp, r"""
public static Object[] offer(@PKG@.CollData d, @PKG@.RegData R, int c) {
  String err = null;
  int next = 0;
  long price = 0L;
  if (!@PKG@.CollReg.BYPASS) err = "Coin unlocks are turned off on this server.";
  else if (d == null || R == null || c < 0 || c >= R.n) err = "Collections are not loaded.";
  else if (R.hidden[c] || R.nobypass[c]) err = "Coin unlocks are not available for this collection.";
  else {
    long sm = @PKG@.CollStore.sum(d, R, c);
    int ct = @PKG@.CollReg.tierOf(R, c, sm);
    int bt = @PKG@.CollStore.boughtTier(d, R, c);
    int mx = @PKG@.CollReg.maxTier(R, c);
    int wall = @PKG@.CollReg.BYP_WALL[R.curve[c]];
    next = (ct > bt ? ct : bt) + 1;
    if (sm < 1L) err = "Collect one first - coin unlocks need a discovered collection.";
    else if (next > mx) err = "Every tier is unlocked.";
    else if (wall <= 0) err = "Coin unlocks are not available for " + @PKG@.CollReg.CURVENAMES[R.curve[c]] + " collections - gather it.";
    else if (next > wall) err = "Tier " + @PKG@.CollUtil.roman(next) + " must be gathered - coins unlock up to tier " + @PKG@.CollUtil.roman(wall) + " here.";
    else {
      long missing = @PKG@.CollReg.threshold(R, c, next) - sm;
      if (missing < 1L) missing = 1L;
      price = (long) Math.ceil((double) missing * (double) unitPrice(R, c) * @PKG@.CollReg.BYP_MULT);
      if (price < @PKG@.CollReg.BYP_MIN) price = @PKG@.CollReg.BYP_MIN;
    }
  }
  return new Object[] { Integer.valueOf(next), Long.valueOf(price), err };
}""")
M(byp, r"""
public static String unlockText(int c, int t) {
  String[] rs = @PKG@.CollReg.recipesAt(c, t);
  if (rs.length == 0) return "Tier " + @PKG@.CollUtil.roman(t) + " has no recipe - buying it only opens the next tier for buying.";
  StringBuilder sb = new StringBuilder("Unlocks ");
  for (int i = 0; i < rs.length; i++) { if (i > 0) sb.append(" - "); sb.append(@PKG@.CollUtil.prettyRecipe(rs[i])); }
  sb.append(". Its coins and XP come when you gather to it.");
  return sb.toString();
}""")
# page click (world thread): first click arms (10 s), the second pays: coins:fn:take -> save _bought -> refund if the save fails
M(byp, r"""
public static String click(@PR@ pr, java.util.UUID u, int c) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  String key = @PKG@.CollUtil.pkey(u);
  @PKG@.CollData d = @PKG@.CollStore.dataK(key);
  if (d == null || R == null || c < 0 || c >= R.n) return "Your collections could not be read right now.";
  Object[] o = offer(d, R, c);
  if (o[2] != null) return (String) o[2];
  int next = ((Integer) o[0]).intValue();
  long price = ((Long) o[1]).longValue();
  long now = System.currentTimeMillis();
  Object[] arm = (Object[]) ARM.get(u);
  boolean same = arm != null && ((Integer) arm[0]).intValue() == c && ((Integer) arm[1]).intValue() == next && ((Long) arm[2]).longValue() == price && now - ((Long) arm[3]).longValue() <= 10000L && key.equals(arm[4]);
  if (!same) {
    ARM.put(u, new Object[] { Integer.valueOf(c), Integer.valueOf(next), Long.valueOf(price), Long.valueOf(now), key });
    return "Click Buy again within 10 s to pay " + @PKG@.CollUtil.fmt(price) + " coins for the tier " + @PKG@.CollUtil.roman(next) + " unlocks of " + R.name[c] + ".";
  }
  ARM.remove(u);
  Object f = @PKG@.CollUtil.bridge().get("coins:fn:take");
  if (!(f instanceof java.util.function.Function)) return "Coin unlocks need SkyyCoins, which is not loaded.";
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(price) }); } catch (Throwable t) { }
  if (!Boolean.TRUE.equals(r)) return "You need " + @PKG@.CollUtil.fmt(price) + " coins in your purse.";
  String id = R.id[c];
  long before = @PKG@.CollStore.meta(d, "_bought." + id);
  @PKG@.CollStore.setMeta(d, key, "_bought." + id, (long) next);
  java.nio.file.Path logf = @PKG@.CollStore.DIR.getParent().resolve("bypass.log");
  String who = pr != null ? pr.getUsername() : u.toString();
  if (!@PKG@.CollStore.save(key)) {
    @PKG@.CollStore.setMeta(d, key, "_bought." + id, before);
    boolean back = @PKG@.CollRewards.coinsAdd(u, price);
    @PKG@.CollIO.append(logf, new java.util.Date() + "  FAILED-SAVE " + who + " " + key + " " + id + " tier " + next + " price " + price + (back ? " refunded" : " REFUND-FAILED") + "\n");
    return back ? "Could not save the purchase - your coins were refunded." : "Could not save the purchase and the refund failed - tell an admin (bypass.log).";
  }
  @PKG@.CollIO.append(logf, new java.util.Date() + "  BUY " + who + " " + key + " " + id + " tier " + next + " price " + price + "\n");
  @PKG@.CollUnlocks.publish(u);
  return "Bought the tier " + @PKG@.CollUtil.roman(next) + " unlocks of " + R.name[c] + " for " + @PKG@.CollUtil.fmt(price) + " coins. Gather to tier " + @PKG@.CollUtil.roman(next) + " for its coins and XP.";
}""")

# ================= PlacedStore (copied from SkyySkills 0.3.2) + one-time seed from SkyySkills' placed/*.bin =================
M(plc, r"""
public static long key(int x, int y, int z) {
  return ((((long) x) & 67108863L) << 38) | ((((long) z) & 67108863L) << 12) | (((long) y) & 4095L);
}""")
M(plc, r"""
public static String fileName(String w) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < w.length(); i++) {
    char c = w.charAt(i);
    sb.append(Character.isLetterOrDigit(c) || c == '-' || c == '_' ? c : '_');
  }
  return sb.toString() + ".bin";
}""")
M(plc, r"""
public static synchronized java.util.LinkedHashSet set(String w) {
  java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
  if (s != null) return s;
  s = new java.util.LinkedHashSet();
  try {
    java.nio.file.Path f = DIR.resolve(fileName(w));
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.DataInputStream in = new java.io.DataInputStream(new java.io.BufferedInputStream(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0])));
      try {
        int n = in.readInt();
        for (int i = 0; i < n; i++) s.add(Long.valueOf(in.readLong()));
      } finally { in.close(); }
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not load placed blocks for " + w + ": " + t); }
  WORLDS.put(w, s);
  return s;
}""")
M(plc, r"""
public static synchronized void add(String w, long k) {
  java.util.LinkedHashSet s = set(w);
  Long v = Long.valueOf(k);
  s.remove(v);
  s.add(v);
  if (s.size() > CAP) { java.util.Iterator it = s.iterator(); it.next(); it.remove(); }
  DIRTY.add(w);
}""")
M(plc, r"""
public static synchronized boolean remove(String w, long k) {
  boolean r = set(w).remove(Long.valueOf(k));
  if (r) DIRTY.add(w);
  return r;
}""")
M(plc, r"""
public static synchronized void snapshot(java.util.ArrayList names, java.util.ArrayList snaps) {
  java.util.Iterator it = DIRTY.iterator();
  while (it.hasNext()) {
    String w = (String) it.next();
    java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
    if (s != null) {
      long[] a = new long[s.size()];
      int i = 0;
      java.util.Iterator si = s.iterator();
      while (si.hasNext() && i < a.length) { a[i] = ((Long) si.next()).longValue(); i++; }
      names.add(w); snaps.add(a);
    }
  }
  DIRTY.clear();
}""")
M(plc, r"""
public static void flush() {
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList snaps = new java.util.ArrayList();
  snapshot(names, snaps);
  for (int j = 0; j < names.size(); j++) {
    String w = (String) names.get(j);
    long[] a = (long[]) snaps.get(j);
    try {
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = DIR.resolve(fileName(w) + ".tmp");
      java.io.DataOutputStream out = new java.io.DataOutputStream(new java.io.BufferedOutputStream(java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0])));
      try {
        out.writeInt(a.length);
        for (int i = 0; i < a.length; i++) out.writeLong(a[i]);
      } finally { out.close(); }
      java.nio.file.Files.move(tmp, DIR.resolve(fileName(w)), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable t) { @PKG@.CollUtil.warn("could not save placed blocks for " + w + ": " + t); }
  }
}""")
# first 0.2 start: copy SkyySkills' placed-block files (same key format) so blocks placed while only SkyySkills tracked them count as placed
M(plc, r"""
public static void seed(java.nio.file.Path from) {
  try {
    java.nio.file.Path mark = DIR.resolve("seeded.txt");
    if (java.nio.file.Files.exists(mark, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    int n = 0;
    java.io.File[] fs = null;
    if (from != null) fs = from.toFile().listFiles();
    if (fs != null) {
      for (int i = 0; i < fs.length; i++) {
        if (!fs[i].getName().endsWith(".bin")) continue;
        if (@PKG@.CollIO.copyIfMissing(fs[i].toPath(), DIR.resolve(fs[i].getName()))) n++;
      }
    }
    @PKG@.CollIO.writeText(mark, "placed-block files copied once from Skyy_SkyySkills/placed: " + n + "\n");
    if (n > 0) @PKG@.CollUtil.info("seeded placed blocks from SkyySkills (" + n + " world file(s))");
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not seed placed blocks from SkyySkills: " + t); }
}""")

# ================= pending contexts =================
M(pend, r"""
public static void prune(long now) {
  try {
    java.util.Iterator it = USE.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (now - ((long[]) e.getValue())[0] > 10000L) it.remove(); }
    it = BREAK.entrySet().iterator();
    long nn = System.nanoTime();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (nn - ((@PKG@.GatherCtx) e.getValue()).nanos > 10000000000L) it.remove(); }
    if (!HSEEN && !HWARN && HOPEN >= 5) {
      HWARN = true;
      @PKG@.CollUtil.warn(HOPEN + " ripe-crop F-harvests opened a pickup window but no InteractivelyPickupItemEvent arrived - F-harvested crops are NOT counted; the harvest fallback (Collections-Spec 3.1) is needed");
    }
  } catch (Throwable t) { }
}""")
C(gctx, "public GatherCtx() { this.pickups = new java.util.ArrayList(); this.done = false; }")

# ================= deferred tasks (world thread, after every system saw the event) =================
RUN(btk)
F(btk, "public @PKG@.GatherCtx g;")
C(btk, "public CollBreakTask(@PKG@.GatherCtx g) { this.g = g; }")
M(btk, r"""
public void run() {
  try {
    @PKG@.GatherCtx c = this.g;
    c.done = true;
    @PKG@.CollPending.BREAK.remove(c.u, c);
    if (c.ev.isCancelled()) return;
    boolean placed = @PKG@.PlacedStore.remove(c.world, @PKG@.PlacedStore.key(c.x, c.y, c.z));
    if (!c.credit || c.deco) return;
    if (placed && !c.ripe) return;
    if (!c.key.equals(@PKG@.CollUtil.pkey(c.u))) return;
    java.util.List stacks;
    if (!c.pickups.isEmpty()) {
      stacks = new java.util.ArrayList();
      for (int i = 0; i < c.pickups.size(); i++) {
        @IPE@ e = (@IPE@) c.pickups.get(i);
        if (e.isCancelled()) continue;
        @IS@ is = e.getItemStack();
        if (is != null && !is.isEmpty()) stacks.add(is);
      }
    } else {
      stacks = @PKG@.CollDrops.breakDrops(c.bt, c.held);
    }
    @PKG@.CollCredit.creditList(c.pr, c.u, c.key, stacks, false);
  } catch (Throwable t) { @PKG@.CollUtil.warn("break credit failed: " + t); }
}""")
RUN(ptk)
F(ptk, "public @IPE@ ev;")
F(ptk, "public @PR@ pr;")
F(ptk, "public java.util.UUID u;")
F(ptk, "public String key;")
C(ptk, "public CollPickupTask(@IPE@ ev, @PR@ pr, java.util.UUID u, String key) { this.ev = ev; this.pr = pr; this.u = u; this.key = key; }")
M(ptk, r"""
public void run() {
  try {
    if (this.ev.isCancelled()) return;
    @IS@ is = this.ev.getItemStack();
    if (is == null || is.isEmpty()) return;
    java.util.ArrayList one = new java.util.ArrayList();
    one.add(is);
    @PKG@.CollCredit.creditList(this.pr, this.u, this.key, one, false);
  } catch (Throwable t) { @PKG@.CollUtil.warn("pickup credit failed: " + t); }
}""")
RUN(pltk)
F(pltk, "public @PBE@ ev;")
F(pltk, "public String world;")
C(pltk, "public CollPlaceTask(@PBE@ ev, String world) { this.ev = ev; this.world = world; }")
M(pltk, r"""
public void run() {
  try {
    if (this.ev.isCancelled()) return;
    @V3I@ t = this.ev.getTargetBlock();
    if (t == null) return;
    @PKG@.PlacedStore.add(this.world, @PKG@.PlacedStore.key(t.x(), t.y(), t.z()));
  } catch (Throwable t) { @PKG@.CollUtil.warn("place record failed: " + t); }
}""")
RUN(ktk)
F(ktk, "public @PR@ pr;")
F(ktk, "public java.util.UUID u;")
F(ktk, "public String key;")
F(ktk, "public String drops;")
C(ktk, "public CollKillTask(@PR@ pr, java.util.UUID u, String key, String drops) { this.pr = pr; this.u = u; this.key = key; this.drops = drops; }")
M(ktk, r"""
public void run() {
  try {
    java.util.List l = @IMOD@.get().getRandomItemDrops(this.drops);
    @PKG@.CollCredit.creditList(this.pr, this.u, this.key, l, false);
  } catch (Throwable t) { @PKG@.CollUtil.warn("kill credit failed: " + t); }
}""")
RUN(atk)
F(atk, "public java.util.UUID u;")
F(atk, "public String key;")
F(atk, "public String item;")
F(atk, "public long qty;")
C(atk, "public CollAddTask(java.util.UUID u, String key, String item, long qty) { this.u = u; this.key = key; this.item = item; this.qty = qty; }")
M(atk, r"""
public void run() {
  try {
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return;
    if (@PKG@.CollUtil.creative(r.getStore(), r)) return;
    @PKG@.CollCredit.creditOne(pr, this.u, this.key, this.item, this.qty, false);
  } catch (Throwable t) { @PKG@.CollUtil.warn("bridge credit failed: " + t); }
}""")
RUN(rtk)
F(rtk, "public java.util.UUID u;")
C(rtk, "public CollRetryTask(java.util.UUID u) { this.u = u; }")
M(rtk, r"""
public void run() {
  try {
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    @PKG@.CollRewards.settleAll(pr, this.u, @PKG@.CollUtil.pkey(this.u));
  } catch (Throwable t) { @PKG@.CollUtil.warn("reward retry failed: " + t); }
}""")

# ================= ECS systems (one registerSystem per class) =================
def event_system(cls, name, event_cls, body):
    C(cls, "public %s() { super(%s.class); }" % (name, event_cls))
    M(cls, r"""
public @QRY@ getQuery() {
  return com.hypixel.hytale.component.Archetype.empty();
}""")
    M(cls, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
%s
  } catch (Throwable t) { @PKG@.CollUtil.warn("%s failed: " + t); }
}""" % (body, name))

# H1: BreakBlockEvent (also fired first by the F pickup of loose blocks) -> ctx + deferred CollBreakTask
event_system(bsy, "CollBreakSys", "@BBE@", r"""
    @BBE@ e = (@BBE@) ev;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    @V3I@ t = e.getTargetBlock();
    @BTY@ bt = e.getBlockType();
    if (t == null || bt == null) return;
    @PKG@.GatherCtx g = new @PKG@.GatherCtx();
    g.ev = e; g.pr = pr; g.u = pr.getUuid(); g.key = @PKG@.CollUtil.pkey(g.u); g.world = w.getName();
    g.x = t.x(); g.y = t.y(); g.z = t.z(); g.bt = bt;
    g.credit = !@PKG@.CollUtil.creative(st, r);
    @IS@ h = e.getItemInHand();
    g.held = null;
    if (h != null && !h.isEmpty()) g.held = h.getItemId();
    g.ripe = "StageFinal".equals(@PKG@.CollUtil.stateOf(bt));
    g.deco = @PKG@.CollDrops.decoAt(w, bt, g.x, g.y, g.z);
    g.thread = Thread.currentThread();
    g.nanos = System.nanoTime();
    @PKG@.CollPending.BREAK.put(g.u, g);
    w.execute(new @PKG@.CollBreakTask(g));""")

# H2: F on a ripe harvestable block (crop / berry bush) opens a 2 s window for its pickups (no credit here)
# Engine facts (HytaleServer.jar bytecode, checked for the 0.2 review): InteractivelyPickupItemEvent is fired ONLY by
# ItemUtils.interactivelyPickupItem, and its only callers are BlockHarvestUtils.performPickupByInteraction (F pickup of a loose
# block: fires BreakBlockEvent first, so H1's ctx claims those stacks) and FarmingUtil.giveDrops (HarvestCropInteraction; no
# BreakBlockEvent, sets the block directly). Item entities picked up from the ground never fire it, so the window can only ever see
# this player's own F-harvests. UseBlockInteraction.doInteraction fires Post right after InteractionContext.execute, which only
# pushes the block's root interaction onto the chain: the harvest (and its pickups) runs after Post, inside the open window.
event_system(usy, "CollUseSys", "@UBP@", r"""
    @UBE@ e = (@UBE@) ev;
    @BTY@ bt = e.getBlockType();
    if (bt == null) return;
    if (!"StageFinal".equals(@PKG@.CollUtil.stateOf(bt))) return;
    @BGA@ g = bt.getGathering();
    if (g == null || g.getHarvest() == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null || @PKG@.CollUtil.creative(st, r)) return;
    @PKG@.CollPending.USE.put(pr.getUuid(), new long[] { System.currentTimeMillis() });
    @PKG@.CollPending.HOPEN = @PKG@.CollPending.HOPEN + 1;""")

# H3: the exact stacks the engine hands over (ItemUtils.interactivelyPickupItem, before Player.giveItem)
event_system(psy, "CollPickupSys", "@IPE@", r"""
    @IPE@ e = (@IPE@) ev;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.GatherCtx g = (@PKG@.GatherCtx) @PKG@.CollPending.BREAK.get(u);
    if (g != null && !g.done && g.thread == Thread.currentThread() && System.nanoTime() - g.nanos < 250000000L) { g.pickups.add(e); return; }
    long[] use = (long[]) @PKG@.CollPending.USE.get(u);
    if (use == null || System.currentTimeMillis() - use[0] > 2000L) return;
    if (!@PKG@.CollPending.HSEEN) { @PKG@.CollPending.HSEEN = true; @PKG@.CollUtil.info("F-harvest pickups reach SkyyCollections - harvested crops count (no harvest fallback needed)"); }
    if (@PKG@.CollUtil.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    w.execute(new @PKG@.CollPickupTask(e, pr, u, @PKG@.CollUtil.pkey(u)));""")

# H4: placed positions (deferred, only when the place was not cancelled)
event_system(plsy, "CollPlaceSys", "@PBE@", r"""
    @PBE@ e = (@PBE@) ev;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    w.execute(new @PKG@.CollPlaceTask(e, w.getName()));""")

# H5: NPC killed by a player -> its drop list re-rolled for the killer (SkyySkills KillSys pattern)
C(ksy, "public CollKillSys() { super(); }")
M(ksy, r"""
public @QRY@ getQuery() {
  return com.hypixel.hytale.component.Archetype.empty();
}""")
M(ksy, r"""
public void onComponentAdded(@REF@ r, @CMP@ c, @ST@ s, @CB@ b) {
  try {
    if (r == null || !(c instanceof @DTH@)) return;
    @NPC@ npc = (@NPC@) s.getComponent(r, @NPC@.getComponentType());
    if (npc == null) return;
    @DMG@ d = ((@DTH@) c).getDeathInfo();
    if (d == null) return;
    Object src = d.getSource();
    if (!(src instanceof @DES@)) return;
    @REF@ k = ((@DES@) src).getRef();
    if (k == null || !k.isValid() || k.getStore() != s) return;
    @PR@ pr = (@PR@) s.getComponent(k, @PR@.getComponentType());
    if (pr == null || !pr.isValid()) return;
    if (@PKG@.CollUtil.creative(s, k)) return;
    String dl = null;
    try { @ROLE@ role = npc.getRole(); if (role != null) dl = role.getDropListId(); } catch (Throwable t) { }
    if (dl == null || dl.length() == 0) return;
    Object ext = s.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    w.execute(new @PKG@.CollKillTask(pr, u, @PKG@.CollUtil.pkey(u), dl));
  } catch (Throwable t) { @PKG@.CollUtil.warn("kill handler failed: " + t); }
}""")

# ================= leaderboards =================
tcmp.addInterface(pool.get("java.util.Comparator"))
C(tcmp, "public CollTopCmp() { }")
M(tcmp, r"""
public int compare(Object a, Object b) {
  long x = ((Long) ((Object[]) a)[1]).longValue();
  long y = ((Long) ((Object[]) b)[1]).longValue();
  if (x != y) return x > y ? -1 : 1;
  return String.valueOf(((Object[]) a)[0]).compareToIgnoreCase(String.valueOf(((Object[]) b)[0]));
}""")
# board -1 = score (count tiers, bought tiers excluded), else a collection index (its real total)
M(top, r"""
public static long value(java.util.Map m, @PKG@.RegData R, int board) {
  if (board >= 0) return @PKG@.CollStore.sumMap(m, (String[]) R.items[board]);
  long s = 0L;
  for (int c = 0; c < R.n; c++) if (!R.hidden[c]) s += @PKG@.CollReg.tierOf(R, c, @PKG@.CollStore.sumMap(m, (String[]) R.items[c]));
  return s;
}""")
M(top, r"""
public static synchronized java.util.ArrayList all(int board) {
  long now = System.currentTimeMillis();
  Object[] cached = (Object[]) CACHE.get(Integer.valueOf(board));
  if (cached != null && now - ((Long) cached[0]).longValue() < 30000L) return (java.util.ArrayList) cached[1];
  @PKG@.RegData R = @PKG@.CollReg.D;
  java.util.HashMap m = new java.util.HashMap();
  if (R == null) return new java.util.ArrayList();
  try {
    java.io.File[] fs = @PKG@.CollStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties")) continue;
      String key = fn.substring(0, fn.length() - 11);
      try {
        java.util.Properties p = @PKG@.CollIO.read(fs[i].toPath());
        if (!"2".equals(String.valueOf(p.getProperty("_schema", "")).trim())) continue;
        String nm = p.getProperty("_name");
        m.put(key, new Object[] { @PKG@.CollUtil.label(nm == null ? (key.length() > 8 ? key.substring(0, 8) : key) : nm, key), Long.valueOf(value(p, R, board)), key });
      } catch (Throwable t) { }
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("leaderboard scan failed: " + t); }
  java.util.Iterator it = @PKG@.CollStore.DATA.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String key = (String) e.getKey();
    @PKG@.CollData d = (@PKG@.CollData) e.getValue();
    String nm = d.name;
    m.put(key, new Object[] { @PKG@.CollUtil.label(nm == null ? (key.length() > 8 ? key.substring(0, 8) : key) : nm, key), Long.valueOf(value(d.items, R, board)), key });
  }
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.Iterator vi = m.values().iterator();
  while (vi.hasNext()) { Object[] row = (Object[]) vi.next(); if (((Long) row[1]).longValue() > 0L) rows.add(row); }
  java.util.Collections.sort(rows, new @PKG@.CollTopCmp());
  CACHE.put(Integer.valueOf(board), new Object[] { Long.valueOf(now), rows });
  return rows;
}""")
M(top, r"""
public static void send(@PR@ pr, int board) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  java.util.ArrayList rows = all(board);
  String title = board < 0 ? "Collection score" : R.name[board];
  pr.sendMessage(@MSG@.raw("[Collections] Top 10 - " + title + ":").color("#ffc800"));
  int n = rows.size() < 10 ? rows.size() : 10;
  if (n == 0) pr.sendMessage(@MSG@.raw("  nobody has collected any yet"));
  String me = @PKG@.CollUtil.pkey(pr.getUuid());
  int rank = 0;
  for (int i = 0; i < rows.size(); i++) if (me.equals(((Object[]) rows.get(i))[2])) { rank = i + 1; break; }
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) rows.get(i);
    long v = ((Long) e[1]).longValue();
    pr.sendMessage(@MSG@.raw("  " + (i + 1) + ". " + e[0] + " - " + @PKG@.CollUtil.fmt(v) + (board < 0 ? " tiers" : "")).color(i + 1 == rank ? "#ffe08a" : "#e6f0ff"));
  }
  if (rank > 10) pr.sendMessage(@MSG@.raw("  you: #" + rank + " of " + rows.size()));
}""")

# ================= bridge functions: coll:fn:count / coll:fn:tier / coll:fn:add =================
fnc.addInterface(pool.get("java.util.function.Function"))
F(fnc, "public String mode;")
C(fnc, "public CollFn(String mode) { this.mode = mode; }")
M(fnc, r"""
public Object apply(Object arg) {
  try {
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];
    @PKG@.RegData R = @PKG@.CollReg.D;
    if (R == null || u == null) return null;
    if ("add".equals(this.mode)) {
      String item = String.valueOf(a[1]);
      long q = ((Number) a[2]).longValue();
      String src = a.length > 3 && a[3] != null ? String.valueOf(a[3]).trim().toLowerCase() : "";
      String expect = null;
      if (a.length > 4 && a[4] != null) expect = String.valueOf(a[4]);
      if (!@PKG@.CollReg.ADD_SOURCES.contains(src) || q <= 0L || !R.itemColl.containsKey(item)) return Boolean.FALSE;
      @PR@ pr = @UNI@.get().getPlayer(u);
      if (pr == null || !pr.isValid()) return Boolean.FALSE;
      String key = @PKG@.CollUtil.pkey(u);
      if (expect != null && !expect.equals(key)) return Boolean.FALSE;
      @WLD@ w = @UNI@.get().getWorld(pr.getWorldUuid());
      if (w == null) return Boolean.FALSE;
      w.execute(new @PKG@.CollAddTask(u, key, item, q));
      return Boolean.TRUE;
    }
    Object ci = R.byId.get(String.valueOf(a[1]).toLowerCase());
    if (!(ci instanceof Integer)) return null;
    int c = ((Integer) ci).intValue();
    @PKG@.CollData d = @PKG@.CollStore.data(u);
    if ("count".equals(this.mode)) return Long.valueOf(@PKG@.CollStore.sum(d, R, c));
    if ("tier".equals(this.mode)) return Integer.valueOf(d == null ? 0 : @PKG@.CollStore.effTier(d, R, c));
    return null;
  } catch (Throwable t) { return null; }
}""")

# ================= CollPage: one inline page, views switched with rebuild() =================
F(page, "public int view;")       # 0 home, 1 category, 2 collection, 3 unlocked recipes
F(page, "public int cat;")
F(page, "public int pageNo;")
F(page, "public int coll;")
F(page, "public String status;")
F(page, "public int[] cards;")
C(page, r"""
public CollPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.view = 0; this.cat = 0; this.pageNo = 0; this.coll = -1; this.status = ""; this.cards = new int[12];
}""")
M(page, r"""
public static String bs(int fs, String bg, String hv) {
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", LabelStyle: (FontSize: " + fs + ", TextColor: #eef6ff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: " + hv + ", LabelStyle: (FontSize: " + fs + ", TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #111a26, LabelStyle: (FontSize: " + fs + ", TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
}""")
M(page, r"""
public static String btn(String id, int w, int h, String text, int fs, String bg, String hv) {
  return "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"" + @PKG@.CollUtil.safe(text) + "\"; " + bs(fs, bg, hv) + " }";
}""")
M(page, r"""
public static String lab(String id, String anchor, String text, int fs, boolean bold, String color, boolean center) {
  return "Label" + (id == null ? "" : " #" + id) + " { Anchor: (" + anchor + "); Text: \"" + @PKG@.CollUtil.safe(text) + "\"; Style: (FontSize: " + fs + (bold ? ", RenderBold: true" : "") + ", TextColor: " + color + (center ? ", HorizontalAlignment: Center" : "") + ", VerticalAlignment: Center); }";
}""")
M(page, r"""
public static String sp(int w, int h) {
  return "Group { Anchor: (Width: " + w + ", Height: " + h + "); }";
}""")
M(page, r"""
public static void bar(@UCB@ b, String parent, String id, int w, int h, int fill, String color) {
  if (fill < 0) fill = 0;
  if (fill > w) fill = w;
  b.appendInline(parent, "Group #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Background: #22324a; }");
  if (fill > 0) b.appendInline("#" + id, "Group { Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: " + h + "); Background: " + color + "; }");
}""")
M(page, r"""
public static void icon(@UCB@ b, String parent, int box, int size, String itemId) {
  int o = (box - size) / 2;
  b.appendInline(parent, "Group { Anchor: (Width: " + box + ", Height: " + box + "); ItemIcon { Anchor: (Width: " + size + ", Height: " + size + ", Left: " + o + ", Top: " + o + "); ItemId: \"" + itemId + "\"; } }");
}""")
M(page, r"""
public static void bind(@UEB@ ev, String id, String payload) {
  ev.addEventBinding(@BT@.Activating, "#" + id, @EVD@.of("a", payload));
}""")
M(page, r"""
public void catCard(@UCB@ b, @UEB@ ev, String parent, int cat, @PKG@.CollData d, @PKG@.RegData R) {
  int found = 0; int total = 0; int maxed = 0; long td = 0L; long tt = 0L;
  for (int c = 0; c < R.n; c++) {
    if (R.cat[c] != cat || R.hidden[c]) continue;
    total++;
    long sm = @PKG@.CollStore.sum(d, R, c);
    if (sm > 0L) found++;
    int ct = @PKG@.CollReg.tierOf(R, c, sm);
    int mx = @PKG@.CollReg.maxTier(R, c);
    td += ct; tt += mx;
    if (ct >= mx) maxed++;
  }
  String box = "SkyyCCatBox" + cat;
  b.appendInline(parent, "Group #" + box + " { Anchor: (Width: 520, Height: 230); Background: #142030(0.92); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 10); }");
  b.appendInline("#" + box, "Group #SkyyCCatTop" + cat + " { Anchor: (Height: 90); LayoutMode: Left; }");
  icon(b, "#SkyyCCatTop" + cat, 90, 80, @PKG@.CollReg.CATICON[cat]);
  b.appendInline("#SkyyCCatTop" + cat, "Group #SkyyCCatTxt" + cat + " { Anchor: (Width: 380, Height: 90); LayoutMode: Top; }");
  b.appendInline("#SkyyCCatTxt" + cat, lab(null, "Height: 46", @PKG@.CollReg.CATS[cat], 26, true, @PKG@.CollReg.ACCENT[cat], false));
  b.appendInline("#SkyyCCatTxt" + cat, lab("SkyyCCatFound" + cat, "Height: 30", "", 18, false, "#dce8f4", false));
  b.set("#SkyyCCatFound" + cat + ".Text", found + " of " + total + " found");
  b.appendInline("#" + box, sp(10, 6));
  bar(b, "#" + box, "SkyyCCatBar" + cat, 440, 18, tt > 0L ? (int) (440L * td / tt) : 0, @PKG@.CollReg.ACCENT[cat]);
  b.appendInline("#" + box, lab("SkyyCCatTiers" + cat, "Height: 30", "", 16, false, "#b8c8d8", false));
  b.set("#SkyyCCatTiers" + cat + ".Text", "Tiers " + td + " / " + tt + "     Maxed " + maxed);
  b.appendInline("#" + box, btn("SkyyCCat" + cat, 240, 46, "Open " + @PKG@.CollReg.CATS[cat], 18, "#2d3f66", "#41598c"));
  bind(ev, "SkyyCCat" + cat, "ccat" + cat);
}""")
M(page, r"""
public void buildHome(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  long[] s = @PKG@.CollStore.stats(d, R);
  int rec = @PKG@.CollUnlocks.compute(d).size();
  b.appendInline("#SkyyColl", lab(null, "Height: 46", "Collections", 28, true, "#f0e6ff", true));
  b.appendInline("#SkyyColl", lab(null, "Height: 26", "Gather items yourself to raise collections. Every tier unlocks rewards.", 16, false, "#c0b3d6", true));
  b.appendInline("#SkyyColl", lab("SkyyCSum", "Height: 30", "", 18, true, "#ffe08a", true));
  b.set("#SkyyCSum.Text", "Tiers " + s[0] + " / " + s[4] + "      Maxed " + s[2] + "      Recipes unlocked " + rec + "      Score " + s[0]);
  b.appendInline("#SkyyColl", sp(10, 12));
  for (int row = 0; row < 2; row++) {
    b.appendInline("#SkyyColl", "Group #SkyyCHRow" + row + " { Anchor: (Height: 232); LayoutMode: Left; }");
    catCard(b, ev, "#SkyyCHRow" + row, row * 2, d, R);
    b.appendInline("#SkyyCHRow" + row, sp(40, 230));
    catCard(b, ev, "#SkyyCHRow" + row, row * 2 + 1, d, R);
    b.appendInline("#SkyyColl", sp(10, 14));
  }
  b.appendInline("#SkyyColl", lab(null, "Height: 30", "Fishing - coming later", 16, false, "#7f94a8", true));
  b.appendInline("#SkyyColl", "Group #SkyyCFoot { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyCFoot", btn("SkyyCRecipes", 280, 48, "Unlocked recipes", 18, "#2d3f66", "#41598c"));
  b.appendInline("#SkyyCFoot", sp(20, 48));
  b.appendInline("#SkyyCFoot", btn("SkyyCRefresh", 180, 48, "Refresh", 18, "#27463a", "#3b6b54"));
  b.appendInline("#SkyyCFoot", sp(420, 48));
  b.appendInline("#SkyyCFoot", btn("SkyyCClose", 180, 48, "Close", 18, "#5a2a2a", "#7a3a3a"));
  bind(ev, "SkyyCRecipes", "crecipes");
  bind(ev, "SkyyCRefresh", "crefresh");
  bind(ev, "SkyyCClose", "cclose");
}""")
M(page, r"""
public void card(@UCB@ b, @UEB@ ev, String parent, int n, int c, @PKG@.CollData d, @PKG@.RegData R) {
  long sm = @PKG@.CollStore.sum(d, R, c);
  String box = "SkyyCCd" + n;
  b.appendInline(parent, "Group #" + box + " { Anchor: (Width: 262, Height: 170); Background: #142030(0.92); LayoutMode: Top; Padding: (Horizontal: 8, Vertical: 6); }");
  if (sm <= 0L) {
    b.appendInline("#" + box, lab(null, "Height: 96", "???", 26, true, "#6f7f90", true));
    b.appendInline("#" + box, lab(null, "Height: 40", "Gather one to discover it", 14, false, "#8a9aaa", true));
    return;
  }
  this.cards[n] = c;
  int ct = @PKG@.CollReg.tierOf(R, c, sm);
  int mx = @PKG@.CollReg.maxTier(R, c);
  long next = ct < mx ? @PKG@.CollReg.threshold(R, c, ct + 1) : 0L;
  b.appendInline("#" + box, "Group #SkyyCCdTop" + n + " { Anchor: (Height: 52); LayoutMode: Left; }");
  if (R.iconOk[c]) icon(b, "#SkyyCCdTop" + n, 50, 44, R.icon[c]); else b.appendInline("#SkyyCCdTop" + n, sp(50, 50));
  b.appendInline("#SkyyCCdTop" + n, btn("SkyyCCard" + n, 194, 44, R.name[c], 16, "#2d3f66", "#41598c"));
  bind(ev, "SkyyCCard" + n, "ccard" + n);
  b.appendInline("#" + box, sp(10, 8));
  bar(b, "#" + box, "SkyyCCdBar" + n, 230, 14, ct >= mx ? 230 : (int) (230L * sm / (next < 1L ? 1L : next)), ct >= mx ? "#d9b038" : @PKG@.CollReg.ACCENT[R.cat[c]]);
  b.appendInline("#" + box, lab("SkyyCCdProg" + n, "Height: 28", "", 16, true, "#e6f0ff", false));
  b.set("#SkyyCCdProg" + n + ".Text", @PKG@.CollUtil.tierName(ct) + "    " + (ct >= mx ? "MAXED" : @PKG@.CollUtil.fmt(sm) + " / " + @PKG@.CollUtil.fmt(next)));
  b.appendInline("#" + box, lab("SkyyCCdNext" + n, "Height: 40", "", 14, false, "#9fb0c0", false));
  java.util.ArrayList nx = ct >= mx ? null : @PKG@.CollReg.rewardLines(R, c, ct + 1);
  b.set("#SkyyCCdNext" + n + ".Text", nx == null ? "All tiers done" : (nx.isEmpty() ? "Next: tier " + @PKG@.CollUtil.roman(ct + 1) : "Next: " + @PKG@.CollUtil.clip((String) nx.get(0), 32)));
}""")
M(page, r"""
public void buildCat(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  java.util.ArrayList list = new java.util.ArrayList();
  java.util.ArrayList un = new java.util.ArrayList();
  for (int c = 0; c < R.n; c++) {
    if (R.cat[c] != this.cat || R.hidden[c]) continue;
    if (@PKG@.CollStore.sum(d, R, c) > 0L) list.add(Integer.valueOf(c)); else un.add(Integer.valueOf(c));
  }
  list.addAll(un);
  int pages = (list.size() + 11) / 12;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  for (int i = 0; i < 12; i++) this.cards[i] = -1;
  String acc = @PKG@.CollReg.ACCENT[this.cat];
  b.appendInline("#SkyyColl", "Group #SkyyCHead { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline("#SkyyCHead", btn("SkyyCBack", 150, 46, "< Back", 18, "#2d3f66", "#41598c"));
  b.appendInline("#SkyyCHead", sp(24, 46));
  b.appendInline("#SkyyCHead", lab(null, "Width: 640, Height: 46", @PKG@.CollReg.CATS[this.cat] + " Collections", 24, true, acc, false));
  b.appendInline("#SkyyCHead", lab("SkyyCPage", "Width: 260, Height: 46", "", 16, false, "#b8c8d8", false));
  b.set("#SkyyCPage.Text", "Page " + (this.pageNo + 1) + " / " + pages);
  bind(ev, "SkyyCBack", "cback");
  for (int row = 0; row < 3; row++) {
    b.appendInline("#SkyyColl", "Group #SkyyCGRow" + row + " { Anchor: (Height: 180); LayoutMode: Left; Padding: (Top: 5); }");
    for (int col = 0; col < 4; col++) {
      int n = row * 4 + col;
      int k = this.pageNo * 12 + n;
      if (k >= list.size()) break;
      if (col > 0) b.appendInline("#SkyyCGRow" + row, sp(10, 170));
      card(b, ev, "#SkyyCGRow" + row, n, ((Integer) list.get(k)).intValue(), d, R);
    }
  }
  b.appendInline("#SkyyColl", "Group #SkyyCFoot { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 6); }");
  if (pages > 1) {
    b.appendInline("#SkyyCFoot", btn("SkyyCPrev", 160, 48, "< Prev", 18, "#2d3f66", "#41598c"));
    b.appendInline("#SkyyCFoot", sp(16, 48));
    b.appendInline("#SkyyCFoot", btn("SkyyCNext", 160, 48, "Next >", 18, "#2d3f66", "#41598c"));
    b.appendInline("#SkyyCFoot", sp(368, 48));
    bind(ev, "SkyyCPrev", "cprev");
    bind(ev, "SkyyCNext", "cnext");
  } else {
    b.appendInline("#SkyyCFoot", sp(704, 48));
  }
  b.appendInline("#SkyyCFoot", btn("SkyyCHome", 180, 48, "Home", 18, "#27463a", "#3b6b54"));
  b.appendInline("#SkyyCFoot", sp(16, 48));
  b.appendInline("#SkyyCFoot", btn("SkyyCClose", 180, 48, "Close", 18, "#5a2a2a", "#7a3a3a"));
  bind(ev, "SkyyCHome", "chome");
  bind(ev, "SkyyCClose", "cclose");
}""")
M(page, r"""
public void buildDetail(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  int c = this.coll;
  this.cat = R.cat[c];
  long sm = @PKG@.CollStore.sum(d, R, c);
  int ct = @PKG@.CollReg.tierOf(R, c, sm);
  int bt = @PKG@.CollStore.boughtTier(d, R, c);
  int mx = @PKG@.CollReg.maxTier(R, c);
  int eff = ct > bt ? ct : bt;
  long next = ct < mx ? @PKG@.CollReg.threshold(R, c, ct + 1) : 0L;
  String acc = @PKG@.CollReg.ACCENT[R.cat[c]];
  b.appendInline("#SkyyColl", "Group #SkyyCHead { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline("#SkyyCHead", btn("SkyyCBack", 300, 46, "< Back to " + @PKG@.CollReg.CATS[R.cat[c]], 18, "#2d3f66", "#41598c"));
  b.appendInline("#SkyyCHead", sp(444, 46));
  b.appendInline("#SkyyCHead", btn("SkyyCHome", 160, 46, "Home", 18, "#27463a", "#3b6b54"));
  b.appendInline("#SkyyCHead", sp(16, 46));
  b.appendInline("#SkyyCHead", btn("SkyyCClose", 160, 46, "Close", 18, "#5a2a2a", "#7a3a3a"));
  bind(ev, "SkyyCBack", "cback");
  bind(ev, "SkyyCHome", "chome");
  bind(ev, "SkyyCClose", "cclose");
  b.appendInline("#SkyyColl", "Group #SkyyCDTop { Anchor: (Height: 96); LayoutMode: Left; }");
  if (R.iconOk[c]) icon(b, "#SkyyCDTop", 96, 80, R.icon[c]); else b.appendInline("#SkyyCDTop", sp(96, 96));
  b.appendInline("#SkyyCDTop", "Group #SkyyCDTxt { Anchor: (Width: 600, Height: 96); LayoutMode: Top; }");
  b.appendInline("#SkyyCDTxt", lab("SkyyCDName", "Height: 50", "", 30, true, acc, false));
  b.set("#SkyyCDName.Text", R.name[c]);
  b.appendInline("#SkyyCDTxt", lab("SkyyCDTier", "Height: 32", "", 20, false, "#dce8f4", false));
  b.set("#SkyyCDTier.Text", (ct <= 0 ? "No tier yet" : "Tier " + @PKG@.CollUtil.roman(ct) + " of " + @PKG@.CollUtil.roman(mx)) + (bt > ct ? "   (recipes bought up to tier " + @PKG@.CollUtil.roman(bt) + ")" : ""));
  b.appendInline("#SkyyCDTop", "Group #SkyyCDTxt2 { Anchor: (Width: 380, Height: 96); LayoutMode: Top; }");
  b.appendInline("#SkyyCDTxt2", lab("SkyyCDTotal", "Height: 50", "", 18, true, "#ffe08a", false));
  b.set("#SkyyCDTotal.Text", "Total collected: " + @PKG@.CollUtil.fmt(sm));
  b.appendInline("#SkyyCDTxt2", lab("SkyyCDCurve", "Height: 32", "", 16, false, "#9fb0c0", false));
  b.set("#SkyyCDCurve.Text", @PKG@.CollReg.CATS[R.cat[c]] + " - " + @PKG@.CollReg.CURVENAMES[R.curve[c]] + " collection");
  b.appendInline("#SkyyColl", "Group #SkyyCDBarRow { Anchor: (Height: 34); LayoutMode: Left; Padding: (Top: 6); }");
  bar(b, "#SkyyCDBarRow", "SkyyCDBar", 700, 22, ct >= mx ? 700 : (int) (700L * sm / (next < 1L ? 1L : next)), ct >= mx ? "#d9b038" : acc);
  b.appendInline("#SkyyCDBarRow", sp(16, 22));
  b.appendInline("#SkyyCDBarRow", lab("SkyyCDProg", "Width: 360, Height: 22", "", 16, false, "#dce8f4", false));
  b.set("#SkyyCDProg.Text", ct >= mx ? "MAXED" : @PKG@.CollUtil.fmt(sm) + " / " + @PKG@.CollUtil.fmt(next) + " to tier " + @PKG@.CollUtil.roman(ct + 1));
  b.appendInline("#SkyyColl", sp(10, 6));
  b.appendInline("#SkyyColl", "Group { Anchor: (Height: 2); Background: #33445a; }");
  b.appendInline("#SkyyColl", sp(10, 4));
  for (int t = 1; t <= mx; t++) {
    String st = "LOCKED"; String col = "#8a3a36"; String tc = "#9aa8b6";
    if (t <= ct) { st = "DONE"; col = "#3aa655"; tc = "#dcf5e0"; }
    else if (t <= bt) { st = "BOUGHT"; col = "#d98a2b"; tc = "#f5e0c0"; }
    else if (t == eff + 1) { st = "NEXT"; col = "#d9b038"; tc = "#fff0c0"; }
    b.appendInline("#SkyyColl", "Group #SkyyCTr" + t + " { Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 3); }");
    b.appendInline("#SkyyCTr" + t, "Group { Anchor: (Width: 110, Height: 34); Background: " + col + "; " + lab(null, "Full: 0", st, 16, true, "#ffffff", true) + " }");
    b.appendInline("#SkyyCTr" + t, sp(14, 34));
    b.appendInline("#SkyyCTr" + t, lab(null, "Width: 70, Height: 34", @PKG@.CollUtil.roman(t), 20, true, "#f0e6ff", false));
    b.appendInline("#SkyyCTr" + t, lab("SkyyCThr" + t, "Width: 130, Height: 34", "", 18, false, "#dce8f4", false));
    b.set("#SkyyCThr" + t + ".Text", @PKG@.CollUtil.fmt(@PKG@.CollReg.threshold(R, c, t)));
    b.appendInline("#SkyyCTr" + t, lab("SkyyCRew" + t, "Width: 740, Height: 34", "", 16, false, tc, false));
    b.set("#SkyyCRew" + t + ".Text", @PKG@.CollReg.rewardText(R, c, t) + (t > ct && t <= bt ? "   (coins and XP paid when reached)" : ""));
  }
  b.appendInline("#SkyyColl", lab("SkyyCFrom", "Height: 30", "", 16, false, "#8a9aaa", false));
  b.set("#SkyyCFrom.Text", "From: " + R.from[c]);
  b.appendInline("#SkyyColl", "Group #SkyyCBuyRow { Anchor: (Height: 54); LayoutMode: Left; Padding: (Top: 4); }");
  Object[] o = @PKG@.CollBypass.offer(d, R, c);
  if (o[2] == null) {
    int nt = ((Integer) o[0]).intValue();
    long price = ((Long) o[1]).longValue();
    b.appendInline("#SkyyCBuyRow", btn("SkyyCBuy", 520, 46, "Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins", 17, "#6a4a1a", "#8a6424"));
    bind(ev, "SkyyCBuy", "cbuy");
    b.appendInline("#SkyyCBuyRow", sp(16, 46));
    b.appendInline("#SkyyCBuyRow", lab("SkyyCBuyInfo", "Width: 540, Height: 46", "", 14, false, "#c8b070", false));
    b.set("#SkyyCBuyInfo.Text", @PKG@.CollBypass.unlockText(c, nt));
  } else {
    b.appendInline("#SkyyCBuyRow", lab("SkyyCBuyInfo", "Width: 1080, Height: 46", "", 14, false, "#7f94a8", false));
    b.set("#SkyyCBuyInfo.Text", (String) o[2]);
  }
}""")
M(page, r"""
public void buildRecipes(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  java.util.ArrayList lines = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    int ct = @PKG@.CollStore.countTier(d, R, c);
    int eff = @PKG@.CollStore.effTier(d, R, c);
    for (int t = 1; t <= eff; t++) {
      String[] rs = @PKG@.CollReg.recipesAt(c, t);
      for (int i = 0; i < rs.length; i++) {
        if (!seen.add(rs[i])) continue;
        lines.add(@PKG@.CollUtil.prettyRecipe(rs[i]) + "    (" + R.name[c] + " " + @PKG@.CollUtil.roman(t) + (t > ct ? " - bought" : "") + ")");
      }
    }
  }
  java.util.Iterator it = @PKG@.CollUnlocks.compute(d).iterator();
  while (it.hasNext()) { String rid = (String) it.next(); if (seen.add(rid)) lines.add(@PKG@.CollUtil.prettyRecipe(rid) + "    (auto rule)"); }
  b.appendInline("#SkyyColl", lab(null, "Height: 46", "Unlocked recipes", 28, true, "#f0e6ff", true));
  b.appendInline("#SkyyColl", lab("SkyyCRSub", "Height: 28", "", 16, false, "#c0b3d6", true));
  b.set("#SkyyCRSub.Text", lines.isEmpty() ? "No recipes yet - reach tier I of Wheat, Oak Log or Cobblestone for the first ones." : lines.size() + " recipe(s). Craft them in /craft - Collections tab (materials still needed, no bench).");
  b.appendInline("#SkyyColl", sp(10, 8));
  b.appendInline("#SkyyColl", "Group #SkyyCRCols { Anchor: (Height: 590); LayoutMode: Left; }");
  b.appendInline("#SkyyCRCols", "Group #SkyyCRCol0 { Anchor: (Width: 530, Height: 590); LayoutMode: Top; }");
  b.appendInline("#SkyyCRCols", sp(20, 590));
  b.appendInline("#SkyyCRCols", "Group #SkyyCRCol1 { Anchor: (Width: 530, Height: 590); LayoutMode: Top; }");
  int shown = lines.size() > 40 ? 39 : lines.size();
  for (int i = 0; i < shown; i++) {
    b.appendInline("#SkyyCRCol" + (i / 20), lab("SkyyCRn" + i, "Height: 28", "", 16, false, "#e6f0ff", false));
    b.set("#SkyyCRn" + i + ".Text", (String) lines.get(i));
  }
  if (lines.size() > 40) {
    b.appendInline("#SkyyCRCol1", lab("SkyyCRMore", "Height: 28", "", 16, true, "#ffe08a", false));
    b.set("#SkyyCRMore.Text", "... and " + (lines.size() - 39) + " more (/collections unlocks)");
  }
  b.appendInline("#SkyyColl", "Group #SkyyCFoot { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyCFoot", btn("SkyyCBack", 180, 48, "< Back", 18, "#2d3f66", "#41598c"));
  b.appendInline("#SkyyCFoot", sp(720, 48));
  b.appendInline("#SkyyCFoot", btn("SkyyCClose", 180, 48, "Close", 18, "#5a2a2a", "#7a3a3a"));
  bind(ev, "SkyyCBack", "cback");
  bind(ev, "SkyyCClose", "cclose");
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.RegData R = @PKG@.CollReg.D;
  @PKG@.CollData d = @PKG@.CollStore.data(u);
  b.appendInline((String) null, "Group #SkyyColl { Anchor: (Width: 1120, Height: 840); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyColl", "Group { Anchor: (Height: 3); Background: #b48fe0; }");
  if (R == null || d == null) {
    b.appendInline("#SkyyColl", lab(null, "Height: 80", "Your collections could not be read right now - try again in a moment.", 20, true, "#ffb0a0", true));
    b.appendInline("#SkyyColl", btn("SkyyCClose", 180, 48, "Close", 18, "#5a2a2a", "#7a3a3a"));
    bind(ev, "SkyyCClose", "cclose");
    return;
  }
  if (this.view == 2 && this.coll >= 0 && this.coll < R.n && !R.hidden[this.coll]) buildDetail(b, ev, d, R);
  else if (this.view == 1 && this.cat >= 0 && this.cat < 4) buildCat(b, ev, d, R);
  else if (this.view == 3) buildRecipes(b, ev, d, R);
  else { this.view = 0; buildHome(b, ev, d, R); }
  b.appendInline("#SkyyColl", lab("SkyyCStatus", "Height: 28", "", 16, true, "#ffe08a", true));
  b.set("#SkyyCStatus.Text", this.status == null ? "" : this.status);
}""")
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.CollUtil.warn("could not close the page: " + t); }
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("cclose\"") >= 0) { closePage(ref, st); return; }
    if (data.indexOf("cbuy\"") >= 0) { this.status = @PKG@.CollBypass.click(this.playerRef, this.playerRef.getUuid(), this.coll); rebuild(); return; }
    this.status = "";
    if (data.indexOf("chome\"") >= 0) { this.view = 0; rebuild(); return; }
    if (data.indexOf("cback\"") >= 0) { this.view = this.view == 2 ? 1 : 0; rebuild(); return; }
    if (data.indexOf("crefresh\"") >= 0) { rebuild(); return; }
    if (data.indexOf("crecipes\"") >= 0) { this.view = 3; rebuild(); return; }
    if (data.indexOf("cprev\"") >= 0) { if (this.pageNo > 0) this.pageNo = this.pageNo - 1; rebuild(); return; }
    if (data.indexOf("cnext\"") >= 0) { this.pageNo = this.pageNo + 1; rebuild(); return; }
    for (int i = 0; i < 4; i++) {
      if (data.indexOf("ccat" + i + "\"") >= 0) { this.view = 1; this.cat = i; this.pageNo = 0; rebuild(); return; }
    }
    for (int i = 0; i < 12; i++) {
      if (data.indexOf("ccard" + i + "\"") >= 0) {
        if (this.cards != null && i < this.cards.length && this.cards[i] >= 0) { this.coll = this.cards[i]; this.view = 2; }
        rebuild();
        return;
      }
    }
  } catch (Throwable t) { @PKG@.CollUtil.warn("page click failed: " + t); }
}""")
M(page, r"""
public static void openFor(@PR@ pr, @ST@ store, @REF@ ref, int coll) {
  @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
  if (player == null) return;
  @PKG@.CollPage p = new @PKG@.CollPage(pr);
  @PKG@.RegData R = @PKG@.CollReg.D;
  if (coll >= 0 && R != null && coll < R.n) { p.coll = coll; p.cat = R.cat[coll]; p.view = 2; }
  player.getPageManager().openCustomPage(ref, store, p);
}""")

# ================= commands (HANDOFF command rules: Adventurer group on player commands, admin = requirePermission + no groups) =================
C(ulc, r"""
public CollUnlocksCmd() {
  super("unlocks", "List the recipes your collections have unlocked");
  addAliases(new String[] { "recipes" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(ulc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.CollUnlocks.sendUnlocks(pr); }
  catch (Throwable t) { @PKG@.CollUtil.warn("/collections unlocks failed: " + t); pr.sendMessage(@MSG@.raw("[Collections] could not list your unlocks")); }
}""")
C(rlc, r"""
public CollReloadCmd() {
  super("reload", "Reload collections.properties, rewards.properties and config.properties (admin)");
  requirePermission("skyycollections.admin");
  setPermissionGroups(new String[0]);
}""")
M(rlc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyycollections.admin")) { pr.sendMessage(@MSG@.raw("[Collections] no permission (skyycollections.admin)")); return; }
    String a = @PKG@.CollReg.loadAll();
    String v = @PKG@.CollReg.validate();
    @PKG@.CollUtil.bridge().put("coll:list", @PKG@.CollReg.listString());
    @PKG@.CollTop.CACHE.clear();
    @PKG@.CollUnlocks.republishAll();
    pr.sendMessage(@MSG@.raw("[Collections] reloaded: " + v + "; " + a));
  } catch (Throwable t) { @PKG@.CollUtil.warn("/collections reload failed: " + t); pr.sendMessage(@MSG@.raw("[Collections] reload failed - see the server log")); }
}""")
F(gvc, "public @RA@ collArg;")
F(gvc, "public @RA@ numArg;")
C(gvc, r"""
public CollGiveCmd() {
  super("give", "Test helper (admin): credit n items of a collection to yourself through the normal path");
  this.collArg = withRequiredArg("collection", "collection id or name, e.g. Wheat, OakLog, Cobblestone", @ATY@.STRING);
  this.numArg = withRequiredArg("amount", "how many of the collection's first item", @ATY@.STRING);
  requirePermission("skyycollections.admin");
  setPermissionGroups(new String[0]);
}""")
M(gvc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyycollections.admin")) { pr.sendMessage(@MSG@.raw("[Collections] no permission (skyycollections.admin)")); return; }
    String q = String.valueOf(ctx.get(this.collArg));
    int c = @PKG@.CollReg.find(q);
    @PKG@.RegData R = @PKG@.CollReg.D;
    if (c < 0 || R == null) { pr.sendMessage(@MSG@.raw("[Collections] no collection matches " + q)); return; }
    long n = 0L;
    try { n = Long.parseLong(String.valueOf(ctx.get(this.numArg)).trim()); } catch (Throwable t) { }
    if (n < 1L || n > 1000000L) { pr.sendMessage(@MSG@.raw("[Collections] amount must be 1 - 1000000")); return; }
    String item = ((String[]) R.items[c])[0];
    java.util.UUID u = pr.getUuid();
    @PKG@.CollCredit.creditOne(pr, u, @PKG@.CollUtil.pkey(u), item, n, true);
    @PKG@.CollData d = @PKG@.CollStore.data(u);
    pr.sendMessage(@MSG@.raw("[Collections] +" + n + " " + item + " -> " + R.name[c] + " " + @PKG@.CollUtil.fmt(@PKG@.CollStore.sum(d, R, c))));
  } catch (Throwable t) { @PKG@.CollUtil.warn("/collections give failed: " + t); pr.sendMessage(@MSG@.raw("[Collections] give failed - see the server log")); }
}""")
F(tpc, "public @RA@ boardArg;")
C(tpc, r"""
public CollTopCmd() {
  super("top", "Top 10 of a collection or of the collection score: /collections top cobblestone | score");
  this.boardArg = withRequiredArg("board", "a collection name (cobblestone, oaklog, wheat...) or score", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(tpc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String q = String.valueOf(ctx.get(this.boardArg)).trim();
    int board = -1;
    if (!q.equalsIgnoreCase("score")) {
      board = @PKG@.CollReg.find(q);
      if (board < 0) { pr.sendMessage(@MSG@.raw("[Collections] no collection matches " + q + " - try /collections top score")); return; }
    }
    @PKG@.CollTop.send(pr, board);
  } catch (Throwable t) { @PKG@.CollUtil.warn("/collections top failed: " + t); pr.sendMessage(@MSG@.raw("[Collections] could not read the leaderboard")); }
}""")
# usage variant /collections <name> (optional args are not positional - HANDOFF command rules; subcommands win over variants)
F(nmc, "public @RA@ nameArg;")
C(nmc, r"""
public CollNameCmd() {
  super("Open one collection: /collections <name>");
  this.nameArg = withRequiredArg("name", "collection name, e.g. wheat, oak, cobblestone", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(nmc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String q = String.valueOf(ctx.get(this.nameArg));
    int c = @PKG@.CollReg.find(q);
    if (c < 0) { pr.sendMessage(@MSG@.raw("[Collections] no collection matches " + q + " - /collections shows them all")); return; }
    @PKG@.CollPage.openFor(pr, store, ref, c);
  } catch (Throwable t) { @PKG@.CollUtil.warn("/collections <name> failed: " + t); pr.sendMessage(@MSG@.raw("[Collections] could not open the page")); }
}""")
F(cmd, "public @OA@ actionArg;")
C(cmd, r"""
public CollCmd() {
  super("collections", "Your collections; /collections <name> | unlocks | top <collection|score>");
  addAliases(new String[] { "coll" });
  this.actionArg = withOptionalArg("action", "unlocks | reload", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.CollUnlocksCmd());
  addSubCommand(new @PKG@.CollReloadCmd());
  addSubCommand(new @PKG@.CollGiveCmd());
  addSubCommand(new @PKG@.CollTopCmd());
  addUsageVariant(new @PKG@.CollNameCmd());
}""")
M(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (ctx.provided(this.actionArg)) {
      String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
      if (a.equals("unlocks") || a.equals("recipes")) { @PKG@.CollUnlocks.sendUnlocks(pr); return; }
      if (a.equals("reload")) { pr.sendMessage(@MSG@.raw("[Collections] use /collections reload")); return; }
    }
    @PKG@.CollPage.openFor(pr, store, ref, -1);
  } catch (Throwable t) { @PKG@.CollUtil.warn("/collections failed: " + t); pr.sendMessage(@MSG@.raw("[Collections] could not open the page")); }
}""")

# ================= 1 s saver: epochs + first publish (1 s), save (10 s), owed rewards (30 s), placed blocks + pruning (60 s) =================
RUN(sav)
F(sav, "public long ticks;")
C(sav, "public CollSaver() { this.ticks = 0L; }")
M(sav, r"""
public static void retryOwed() {
  if (@PKG@.CollRewards.OWED.isEmpty()) return;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ pr = (@PR@) it.next();
    try {
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (!@PKG@.CollRewards.OWED.contains(@PKG@.CollUtil.pkey(u))) continue;
      @WLD@ w = @UNI@.get().getWorld(pr.getWorldUuid());
      if (w != null) w.execute(new @PKG@.CollRetryTask(u));
    } catch (Throwable t) { }
  }
}""")
M(sav, r"""
public static synchronized void pruneMinute(long now) {
  java.util.Iterator it = @PKG@.CollCredit.MINUTE.values().iterator();
  while (it.hasNext()) { long[] w = (long[]) it.next(); if (now - w[0] > 120000L) it.remove(); }
}""")
M(sav, r"""
public void run() {
  this.ticks = this.ticks + 1L;
  try { @PKG@.CollUnlocks.checkEpochs(); } catch (Throwable t) { }
  try { @PKG@.CollUnlocks.publishOnline(); } catch (Throwable t) { }
  if (this.ticks % 10L == 0L) { try { @PKG@.CollStore.flushDirty(); } catch (Throwable t) { } }
  if (this.ticks % 30L == 0L) { try { retryOwed(); } catch (Throwable t) { } }
  if (this.ticks % 60L == 0L) {
    long now = System.currentTimeMillis();
    try { @PKG@.PlacedStore.flush(); } catch (Throwable t) { }
    try { @PKG@.CollPending.prune(now); } catch (Throwable t) { }
    try { synchronized (@PKG@.CollCredit.class) { pruneMinute(now); } } catch (Throwable t) { }
    try {
      java.util.Iterator it = @PKG@.CollBypass.ARM.values().iterator();
      while (it.hasNext()) { Object[] a = (Object[]) it.next(); if (now - ((Long) a[3]).longValue() > 60000L) it.remove(); }
    } catch (Throwable t) { }
  }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture saver;")
C(pl, "public SkyyCollectionsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.CollUtil.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyCollections");
  @PKG@.CollReg.BASE = base;
  @PKG@.CollStore.DIR = base.resolve("counts");
  @PKG@.PlacedStore.DIR = base.resolve("placed");
  String s = @PKG@.CollReg.loadAll();
  @PKG@.PlacedStore.seed(getDataDirectory().resolveSibling("Skyy_SkyySkills").resolve("placed"));
  getEntityStoreRegistry().registerSystem(new @PKG@.CollBreakSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.CollUseSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.CollPickupSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.CollPlaceSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.CollKillSys());
  getCommandRegistry().registerCommand(new @PKG@.CollCmd());
  java.util.Map b = @PKG@.CollUtil.bridge();
  b.put("coll:fn:count", new @PKG@.CollFn("count"));
  b.put("coll:fn:tier", new @PKG@.CollFn("tier"));
  b.put("coll:fn:add", new @PKG@.CollFn("add"));
  b.put("coll:list", @PKG@.CollReg.listString());
  this.saver = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.CollSaver(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] 0.2.1 ready - item collections, /collections; migration + recipe check run at start; " + s);
}""")
# start() runs after every asset store loaded (setup() runs before them - spec section 6, Skyy's server log)
M(pl, r"""
protected void start() {
  try { super.start(); } catch (Throwable t) { }
  String m = "migration failed";
  String v = "recipe check failed";
  try { m = @PKG@.CollMigrate.runStart(@PKG@.CollStore.DIR); } catch (Throwable t) { @PKG@.CollUtil.warn("migration failed: " + t); }
  try { v = @PKG@.CollReg.validate(); } catch (Throwable t) { @PKG@.CollUtil.warn("recipe check failed: " + t); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] started - " + m + "; " + v);
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.saver != null) this.saver.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CollStore.flushDirty(); } catch (Throwable t) { }
  try { if (!@PKG@.CollStore.DIRTY.isEmpty()) @PKG@.CollStore.flushDirty(); } catch (Throwable t) { }
  try { @PKG@.PlacedStore.flush(); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.CollUtil.bridge();
    b.remove("coll:fn:count"); b.remove("coll:fn:tier"); b.remove("coll:fn:add"); b.remove("coll:list");
  } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL:
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyCollections", VERSION, "SkyWynn collections, Hypixel SkyBlock style: the ITEMS you gather (fiber, sticks, every log type, cobble, ores, crops, mob drops) count toward ~100 collections in Farming, Mining, Foraging and Combat. Tiers pay coins (SkyyCoins), gathering skill XP (SkyySkills) and recipe unlocks for the SkyySacks craft page; coin unlocks for early tiers; leaderboards. /collections. Per profile with SkyyProfiles (optional). Zero dependencies.", PKG + ".SkyyCollectionsPlugin"),
           OUT, {})  # page built inline (no .ui files: see memory hytale-ui-rules)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCollections.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCollections" % VERSION, disable_prefix="Skyy:")
