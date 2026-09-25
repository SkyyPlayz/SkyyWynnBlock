# SkyyCollections 0.2: build spec (item-based collections, SkyBlock-style)

*Written 2026-09-23 by the research workflow (writer for "collections"). Research only: no build script, mod folder, save or game file was changed.*
*Revised 2026-09-23 after the verifier reports: SkyBlock facts tightened (section 1), Parent-merge method (2.1), Bark and Scraper (2.3, 3.2), livestock-harvest gap (2.5), bench filter by id (4.3), 0.2 reward scope + ore line (4.3), bypass examples (4.4), leaderboard design (5.5), migration moved to `start()` (6).*
*Design note 2026-09-24: the coin-bypass lock is now tiered (early game and the first half of mid game; toward late game those items cannot be bought or sold). Section 4.4's per-curve walls are what SkyyCollections 0.2 shipped, not the new lock. Exact cutoffs are open. This file is still a spec; it does not change the jar.*
*Builds on SkyyCollections 0.1.5 (`SkyyCollections/build_skyycollections_0.1.5.py`, per-profile storage, built, not deployed). Suggested path: a new `tools/coll_0_2_patch.py` that generates `build_skyycollections_0.2.py` from 0.1.5, the same way the other mods are patched.*

**Skyy's call (2026-09-23):** "for collections we track the items you collect, not the broken item. so we wouldn't track bushes, we would track fiber and sticks. logs (of the different types.) stone, copper, iron, berries, wheat etc." and "look at how hypixel skyblock does collections."

**Legend.** VERIFIED = seen in a cited web source, in `HytaleServer.jar` bytecode (tools/dev), in `Assets.zip`, in our own build scripts, or in Skyy's save files (read-only). UNVERIFIED = design, estimate or not yet tested in game. `[SKYY?]` = a number or choice for Skyy (they/them) to confirm.

---

## 0. Summary

1. **Today is wrong in two ways.** 0.1.4/0.1.5 count the broken block's id, +1 per break, from `BreakBlockEvent` (VERIFIED, `CollSystem.handle`, `CollStore.bump(u, bt.getId(), 1L)`). They also count blocks the player placed (Skyy's save holds `Furniture_Crude_Torch=1`). VERIFIED.
2. **0.2 counts items.** A break credits the items that block drops, computed by the engine's own helper `BlockHarvestUtils.getDrops`. This is the code SkyySkills 0.3 already uses for double drops. F-pickups and F-harvests credit the exact stacks the engine hands over, through `InteractivelyPickupItemEvent`. Mob kills credit the killed NPC's drop list. VERIFIED hooks. The UI stops showing bushes and grass.
3. **Things the research notes missed, now checked in the jar:**
   - Pressing F to pick up a loose block (rubble, mushrooms, fruit) fires `BreakBlockEvent` **and** `InteractivelyPickupItemEvent`. Counting both would double count. VERIFIED, `BlockHarvestUtils.performPickupByInteraction`.
   - Crop F-harvest also delivers its exact stacks through `InteractivelyPickupItemEvent`. VERIFIED, `FarmingUtil.giveDrops`.
   - The engine has its own placed-block flag, `BlockPhysics.markDeco`/`isDeco`. Leaves, bushes, grass, vines and branches set `UseDefaultDropWhenPlaced`, so a placed one drops itself. VERIFIED. Logs, stone and ores do not, so we still need our own placed-block tracker.
   - The tool drop key (`Pickaxe`, `Shears`) comes from the break interaction, not the item. We can still work it out from the held item. VERIFIED.
4. **Collection list: about 100 collections** in Farming, Mining, Foraging and Combat. Each has exact item ids (section 2). There is one collection per log type (33 wood types), as Skyy asked. Variants share one collection where SkyBlock would group them: sandstone colours, rubble, feathers, mushrooms, crystals, gems. Collections you have not found yet stay hidden, as in SkyBlock.
5. **Tiers: four curves (Bulk, Standard, Rare, Elite)** with 10, 9, 8 and 7 tiers. The first tier costs 50 for common items, as in SkyBlock and 0.1.x. Rewards per tier:
   - recipe unlocks through the existing `coll:recipes:<uuid>` bridge, shown in the SkyySacks /craft Collections tab
   - coins
   - lump sums of gathering-skill XP through `skill:fn:addxp`
   - a collection score

   Coin-bypass buys a tier's **recipe unlocks only**, at steep prices. **Design lock as of 2026-09-24:** that bypass is allowed in the early game and the first half of mid game. Toward late game those items can no longer be bought or sold (bazaar/market). The per-curve walls below (Bulk V / Standard IV / Rare III / Elite never) are what 0.2 shipped under the older lock, not the new cutoff. The exact cutoff per collection and tier is open. Many items will also have level requirements; which level type (skill vs class vs combat) is open.
6. **The auto-unlock rule goes off by default.** With correct item counts, Plant Fiber at tier I would unlock up to 119 recipes. Recipes that ask for a resource type (113 recipes use `Wood_Trunk`) are invisible to it. VERIFIED from Assets.zip.
7. **Migration:** old counts are converted only where the old block gives exactly one known item. Skyy's file becomes **Cobblestone 22, Ash Log 5**. Everything else (bushes, grass, gravel, the torch) cannot be converted and restarts at 0. The old files are kept in `counts-0.1/`. The migration runs in `start()`, after the game assets have loaded; in `setup()` every block lookup would fail (section 6). VERIFIED from Skyy's server log.

---

## 1. How Hypixel SkyBlock collections work

Summarised in my own words. The official wiki (wiki.hypixel.net) shut down in July 2026, so the Minecraft Wiki mirror is the main source.

- A collection tracks an **item**, never a block or a mob. Examples: "Cobblestone", not "Stone"; "Iron Ingot", not "Iron Ore". VERIFIED ([Collections](https://hypixelskyblock.minecraft.wiki/w/Collections)).
- Progress comes from getting the item yourself (breaking, harvesting, killing) or from your minions. Items from NPC merchants, the Bazaar or the Trading window do not count. VERIFIED ([Collections](https://hypixelskyblock.minecraft.wiki/w/Collections); [forum: bazaar](https://hypixel.net/threads/does-buying-resources-from-bazaar-count-towards-collection.2957095/)). You have to pick the items up; items left on the ground give nothing. VERIFIED, informal forum answers ([forum: pickup](https://hypixel.net/threads/do-i-need-to-pick-up-items-for-them-to-count-on-collections.5560065/)). Whether a raw item that another player drops on the ground (not a trade) counts when you pick it up: no source found, UNVERIFIED. SkyWynn never counts ground pickups anyway (3.3).
- A compressed form ("Enchanted X") that you **obtain**, for example from a minion, counts as the number of base items needed to craft it (the wiki's example is 160 for Enchanted Rotten Flesh). VERIFIED ([Collections](https://hypixelskyblock.minecraft.wiki/w/Collections); [forum: minion enchanted items](https://hypixel.net/threads/does-collecting-enchanted-items-from-minions-count-towards-your-collection.2998462/)). Whether crafting one yourself from items you already collected adds the progress a second time: no source says either way, UNVERIFIED (it would double count, so probably not). SkyWynn has no compressed items, so this is out of scope.
- Categories are Farming, Mining, Combat, Foraging and Fishing, plus Boss and Rift. VERIFIED. A collection appears in the menu once you have collected it. VERIFIED (research notes).
- **Tiers:** each collection has about 9 to 12 numbered tiers. Every tier gives +4 SkyBlock XP. VERIFIED, re-fetched. Tiers also give one or more of: a recipe (a minion at tier I, then armor, sacks, accessories, utility items), a lump of skill XP at certain tiers, an NPC trade, an enchant-cost discount or a stat. VERIFIED.
- **Co-op:** collections are shared by the whole co-op profile, and a recipe one member unlocks is unlocked for everyone. Skills stay per player. VERIFIED, re-fetched ([Co-op](https://hypixelskyblock.minecraft.wiki/w/Co-op)).
- **Menu:** `/collections` or the SkyBlock Menu has three layers: category icons, then an item grid for the category, then one page per collection with its tier list. VERIFIED (research notes). The glass-pane colours (green done, yellow current, red locked) come from the research notes and were **not** re-confirmed. UNVERIFIED.
- **Coin-bypass:** no SkyBlock source checked describes paying coins to skip a collection tier. UNVERIFIED (absence of evidence, not a positive source). The SkyWynn coin-bypass is Skyy's own design. The 2026-09-23 wording ("early, steep, off at the endgame wall") is tightened on 2026-09-24: early game and the first half of mid game only, then a buy-and-sell wall. See `SkyWynn-Decisions.md` change notes and row 1.2.

| Collection (category) | Tier thresholds | Reward shape (highlights) | Status |
|---|---|---|---|
| Wheat (Farming), 11 tiers | 50 · 100 · 250 · 500 · 1k · 2.5k · 10k · 15k · 25k · 50k · 100k | I minion · II first armor + Beginner sack · III enchant-XP discount · IV compressed item · V Enchanted Bread + Small sack · VI farming armor (+ Farming Island) · VII talisman · VIII Medium sack · IX +25,000 Farming XP · X Large sack · XI Large Enchanted sack (+ Enchanted Hay Bale) | VERIFIED, re-fetched [Wheat](https://hypixelskyblock.minecraft.wiki/w/Wheat) |
| Cobblestone (Mining), 10 tiers | 50 · 100 · 250 · 1k · 2.5k · 5k · 10k · 25k · 40k · 70k | I minion · III auto-smelter · IV compressed · V compactor · VI +1,000 Mining XP · VII/IX haste accessories · X top compactor | VERIFIED, re-fetched [Cobblestone](https://hypixelskyblock.minecraft.wiki/w/Cobblestone) |
| Oak Log (Foraging), 9 tiers | 50 · 100 · 250 · 500 · 1k · 2k · 5k · 10k · 25k | I minion · II leaf armor · III compressed · IV/VI/IX storage chests · VIII +10,000 Foraging XP | VERIFIED (research notes) [Oak Log](https://hypixelskyblock.minecraft.wiki/w/Oak_Log) |
| Iron Ingot (Mining), 12 tiers | 50 · 100 · 250 · 1k · 2.5k · 5k · 10k · 25k · 50k · 100k · 200k · 400k | I minion · II golem/prospecting armor · III discount · IV compressed · then utility chains (hoppers, auto-deleters) up to XII | VERIFIED (research notes) [Iron Ingot](https://hypixelskyblock.minecraft.wiki/w/Iron_Ingot) |

**Pattern to copy:**
- Early tiers are cheap and full of rewards.
- Middle tiers space out and pay lumps of skill XP.
- Late tiers are 10 to 40 times more expensive and gate the prestige recipes.
- Sacks climb one size at a time across the whole line: Wheat gives Beginner (II), Small (V), Medium (VIII), Large (X) and Large Enchanted (XI). VERIFIED ([Wheat](https://hypixelskyblock.minecraft.wiki/w/Wheat)). SkyWynn's three bag sizes use a similar spread in 4.3 (III / V / VIII).

---

## 2. SkyWynn collection list

### 2.1 Rules

- **The collection item is what the player receives, never the block.** Bushes feed Plant Fiber and Stick. Stone feeds Cobblestone. An ore vein feeds its ore plus the host rock's cobble. VERIFIED drop data below.
- **Categories follow SkyySacks.** `SackDefs.catOf(itemId)` is the category classifier. It is already shipped and keeps bags and collections consistent. VERIFIED, `build_skyysacks_0.7.2.py`. Its rules:
  - `Ore_`, `Rubble_`, `Rock_`, `Soil_` go to Mining.
  - `Wood_`, Stick, Fibre and Bark go to Foraging.
  - `Plant_`, `Food_`, `Fish_` and Life Essence go to Farming.
  - Bones, hides, chitin, sacs, feathers, fabric scraps, Voidheart, Boom Powder and `*_Essence` go to Combat.

  The registry may override a category. The only override in the defaults: Tree Sap goes to Foraging, because `catOf` returns null for it.
- **Storage keeps item ids.** A collection's total is the sum of its member items. Regrouping later never loses data.
- **Hidden until discovered:** a collection shows as "???" until its total is 1 or more. That is how SkyBlock shows collections you have not unlocked. It also keeps the 33 log types from cluttering the page.
- **Fishing is hidden.** Its items (Raw Fish from killing fish) are still counted, so the category can open with progress already in place when fishing ships.

**Drop facts behind the lists.** All VERIFIED, read in memory from `Assets.zip`: `Server/Item/Items/**` Gathering blocks (with `Parent` merged), `Server/Drops/**`, and `Server/NPC/Roles/**` `DropList`.

**How `Parent` is merged (method).** The engine merges a child item into its `Parent` **field by field**, not as whole objects: `com.hypixel.hytale.codec.builder.BuilderCodec.inherit` first copies every field of the parent, then `readAndInheritField` → `decodeAndInheritJson(field, reader, target, parentValue, ...)` decodes each field the child declares on top of the parent's value. VERIFIED bytecode. So a child that restates only part of a nested object keeps the parent's other keys. Example: `Rock_Aqua` and `Rock_Calcite` declare only `Breaking: {GatherType: Rocks}` and still get `ItemId: Rock_Stone_Cobble` from `Rock_Stone`; the same rule gives every trunk the Scraper entry of `Wood_Oak_Trunk` (2.3). VERIFIED assets. A naive whole-object override would make Aqua and Calcite drop themselves. The tables below assume this field-level merge. A verifier re-checked about 15 rows against it (Rock_Stone/Aqua/Calcite, Apple trunk → Oak Log, grass → Empty, the Chicken drop list, several recipe tiers) and all held; the other rows were not re-checked one by one. At runtime the counts come from the engine (`getDrops`, 3.2), so a table slip would only mislabel a "Fed by" note, unless it put an item into the wrong collection's member list.

| Source | What it really gives |
|---|---|
| `Plant_Bush*` (20 kinds) | Plant Fiber (50% + a second 20% roll), Stick (50%). With shears: the bush block itself |
| `Plant_Grass_*` (every kind) | **Nothing.** The drop list is `Empty`. The research note calling these "self-drop" was wrong |
| `Plant_Leaves_*` (43) | Plant Fiber (50%). Palm leaves (Arid/Oasis) give Palm Tree Log |
| Vines, reeds, moss, seaweed | Plant Fiber |
| `Wood_*_Branch_*` | Stick + Tree Sap |
| `Wood_*_Trunk` and `_Full` | That log. Exception: `Wood_Apple_Trunk_Full` gives **Oak Log** |
| `Rock_Stone`, `Rock_Aqua`, `Rock_Calcite` | Cobblestone (`Rock_Stone_Cobble`). The research note calling Rock_Stone "self-drop" was wrong |
| `Ore_<Metal>_<Host>` | `Ore_<Metal>` + the host rock's cobble (for example Copper Ore + Cobblestone; Thorium in mud gives Soil_Dirt) |
| `Soil_Gravel*` | Stone Rubble 1-2 by hand, 2-3 with a pickaxe (tool entry) |
| `Soil_Grass*`, `Soil_Mud`, `Soil_Needles` | Soil_Dirt (not a collection) |
| Ripe crop (`StageFinal`), break or F | Crop item 1-2 + Essence of Life 2-4 + 50% eternal seeds |
| Unripe crop (Stage1-3) | That crop's seeds only |
| Ripe berry bush | Wild Berries 1-2 + Essence of Life + Stick |
| Chicken / Cow / Boar / Sheep | Raw Chicken + Light Hide / Raw Beef + Medium Hide / Raw Wildmeat + Medium Hide / Raw Wildmeat + Light Hide + Wool Scraps |
| Skeleton | Bone Fragments 1-2 + Linen Scraps 1-3 |

**Curve column:** B = Bulk, S = Standard, R = Rare, E = Elite (section 4).

### 2.2 Farming (Farming skill XP)

| Id | Name | Item id(s) | Fed by | Curve |
|---|---|---|---|---|
| Wheat | Wheat | `Plant_Crop_Wheat_Item` | ripe `Plant_Crop_Wheat_Block`(+`_Eternal`), break or F | S |
| Carrot | Carrot | `Plant_Crop_Carrot_Item` | ripe carrot crop | S |
| Potato | Potato | `Plant_Crop_Potato_Item` | ripe potato crop | S |
| Corn | Corn | `Plant_Crop_Corn_Item` | ripe corn crop | S |
| Tomato | Tomato | `Plant_Crop_Tomato_Item` | ripe tomato crop | S |
| Lettuce | Lettuce | `Plant_Crop_Lettuce_Item` | ripe lettuce crop | S |
| Onion | Onion | `Plant_Crop_Onion_Item` | ripe onion crop | S |
| Turnip | Turnip | `Plant_Crop_Turnip_Item` | ripe turnip crop | S |
| Cauliflower | Cauliflower | `Plant_Crop_Cauliflower_Item` | ripe cauliflower crop | S |
| Aubergine | Aubergine | `Plant_Crop_Aubergine_Item` | ripe aubergine crop | S |
| Chilli | Chilli | `Plant_Crop_Chilli_Item` | ripe chilli crop | S |
| Rice | Rice | `Plant_Crop_Rice_Item` | ripe rice crop | S |
| Pumpkin | Pumpkin | `Plant_Crop_Pumpkin_Item` | ripe pumpkin crop | S |
| Cotton | Cotton | `Plant_Crop_Cotton_Item` | ripe cotton crop | S |
| Berries | Wild Berries | `Plant_Fruit_Berries_Red` | ripe `Plant_Crop_Berry_Block` / `_Wet_` / `_Winter_`, break or F | S |
| Apple | Apple | `Plant_Fruit_Apple` | `Plant_Crop_Apple_Block` / `_Wall` on apple trees | S |
| WildFruit | Wild Fruit | `Plant_Fruit_Coconut`, `_Mango`, `_Pinkberry`, `_Azure`, `_Spiral`, `_Windwillow` | fruit blocks on trees (self-drop, F-pickup) | R |
| Mushroom | Mushroom | the 19 `Plant_Crop_Mushroom_Cap_*`, `_Common_*`, `_Flatcap_*`, `_Glowing_*`, `_Shelve_*` (not Boomshroom) | mushroom blocks (self-drop, F-pickup) | S |
| Cactus | Cactus | `Plant_Cactus_1`, `_2`, `_3`, `_Ball_1`, `_Flat_1`, `_Flat_2`, `_Flat_3` | cactus blocks (self-drop); the Cactee mob | S |
| Seeds | Seeds | every `Plant_Seeds_*` (including `_Eternal`, `Wild`) | unripe crops, ripe crops (eternal 50%), wild grass crop | B |
| LifeEssence | Essence of Life | `Ingredient_Life_Essence` | every ripe crop (2-4); the Spirit_Root mob | B |
| Petals | Petals | `Plant_Petals_Blood`, `_Azure`, `_Storm` | Health / Mana / Stamina herb crops (break) | R |
| RawChicken | Raw Chicken | `Food_Chicken_Raw` | Chicken (all kinds), Bramblekin | S |
| RawBeef | Raw Beef | `Food_Beef_Raw` | Cow, Bison, Camel | S |
| RawPork | Raw Pork | `Food_Pork_Raw` | Pig, Wild Pig, Warthog | S |
| Wildmeat | Raw Wildmeat | `Food_Wildmeat_Raw` | 78 roles (deer, boar, sheep, birds, ...) | S |
| *(Fishing, hidden)* RawFish | Raw Fish | `Food_Fish_Raw` (+ `_Uncommon`, `_Rare`, `_Epic`, `_Legendary`) | killing fish NPCs (30 roles) | S |

Meat is in Farming in both SkyBlock and SkyySacks (the `Food_` rule). VERIFIED.

### 2.3 Foraging (Foraging skill XP)

**Logs: one collection per wood type (Skyy's call).** Id = `<Type>Log`, item = `Wood_<Type>_Trunk`, fed by `Wood_<Type>_Trunk` and `Wood_<Type>_Trunk_Full`. Official names come from `server.lang`. VERIFIED, all 33 exist.

| Curve | Logs |
|---|---|
| B | Oak Log (`Wood_Oak_Trunk`; also fed by `Wood_Apple_Trunk_Full` and the `Plant_Fern_*_Trunk` blocks) |
| S | Ash, Aspen, Bamboo, Banyan, Beech, Birch, Bottletree, Camphor, Cedar, Dry, Blue Fig (`Fig_Blue`), Fir, Gumboab, Jungle, Maple, Palm Tree (`Palm`), Palo, Redwood, Sallow, Wild Wisteria (`Wisteria_Wild`), Windwillow, Apple, Burnt |
| R | Amber, Azure, Crystalwood (`Crystal`), Fire, Frostwood (`Ice`), Petrified, Poisoned, Spiral, Stormbark |

Note: Palm Tree Log also drops from `Plant_Leaves_Palm_Arid` and `_Oasis`. VERIFIED. Which logs are Rare is a guess from the wood names. `[SKYY?]`

| Id | Name | Item id | Fed by | Curve |
|---|---|---|---|---|
| Fiber | Plant Fiber | `Ingredient_Fibre` | bushes (0.7 each on average), leaves (0.5), vines, reeds, moss, seaweed, some flowers | B |
| Stick | Stick | `Ingredient_Stick` | bushes (0.5), branches, brambles, berry bushes | B |
| TreeSap | Tree Sap | `Ingredient_Tree_Sap` | branches, `Tree_Sap_Glob` | S |

**Deferred, not registered in 0.2: Tree Bark (`Ingredient_Tree_Bark`).** Bark comes from the Bark Scraper (`Tool_Bark_Scraper`) on a trunk. The hit switches the trunk to its `Stripped` state and drops the `Bark` list; no `BreakBlockEvent` fires. Why, VERIFIED (`BlockHarvestUtils.damageSingleBlock` + assets):
- The Scraper's interaction (`Scraper_Chop.json`) is built like the pickaxe and shears ones: a `BreakBlock` step with `Tool: Scraper`, plus `MatchTool: true`.
- Break or state change is decided **per block**. A block's tool entry with a `State` swaps the block to that state; a tool entry without one breaks the block normally (and fires `BreakBlockEvent`).
- Today only the trunks have a Scraper entry (`Wood_Oak_Trunk`: `Tools: [{Type: Scraper, State: Stripped, DropList: Bark}]`, inherited by the ~70 other trunk blocks), and all of them use the state.
- `MatchTool: true` means a Scraper hit on a block with no Scraper entry does nothing at all.

Counting bark later needs a `DamageBlockEvent` hook plus a check for the stripped state. UNVERIFIED. Curve when added: S. Side note: the stripped state is a timed Farming stage that turns back into the normal trunk; a trunk broken while stripped drops `Wood_Stripped_Deco`, not the log (VERIFIED, the state's own `Gathering`), so it gives no log credit, which is correct.

### 2.4 Mining (Mining skill XP)

| Id | Name | Item id(s) | Fed by | Curve |
|---|---|---|---|---|
| Cobblestone | Cobblestone | `Rock_Stone_Cobble`, `Rock_Stone_Cobble_Mossy` | `Rock_Stone`, `Rock_Stone_Mossy`, `Rock_Aqua`, `Rock_Calcite`, every `Ore_*_Stone` | B |
| Sandstone | Sandstone | `Rock_Sandstone_Cobble`, `Rock_Sandstone_Red_Cobble`, `Rock_Sandstone_White_Cobble` | the three sandstones, `Ore_*_Sandstone` | B |
| Shale | Shale Cobble | `Rock_Shale_Cobble` | `Rock_Shale`, `Ore_*_Shale` | B |
| Slate | Slate Cobble | `Rock_Slate_Cobble` | `Rock_Slate`, `Ore_*_Slate` | B |
| Basalt | Basalt Cobble | `Rock_Basalt_Cobble` | `Rock_Basalt`, `Ore_*_Basalt` | B |
| Volcanic | Volcanic Rock | `Rock_Volcanic_Cobble`, `Rock_Magma_Cooled` | `Rock_Volcanic*`, `Ore_*_Volcanic`, `Ore_Adamantite_Magma*` | B |
| Marble | Marble Cobble | `Rock_Marble_Cobble` | `Rock_Marble` | S |
| Quartzite | Quartzite Cobble | `Rock_Quartzite_Cobble` | `Rock_Quartzite` | S |
| Limestone | Limestone | `Rock_Lime_Cobble` | `Rock_Lime` | S |
| Ice | Ice | `Rock_Ice`, `Rock_Ice_Permafrost` | ice blocks (self-drop) | S |
| Salt | Salt Block | `Rock_Salt` | salt blocks (self-drop) | S |
| Sand | Sand | `Soil_Sand`, `Soil_Sand_Red`, `Soil_Sand_White`, `Soil_Sand_Ashen` | sand (self-drop) | B |
| Rubble | Rubble | every `Rubble_*` (Stone, Stone_Mossy, Sandstone ×3, Basalt, Slate, Shale, Volcanic, Magma_Cooled, Quartzite, Calcite, Chalk, Aqua, Ice, Lime, Marble) | gravel of every kind (`Soil_*Gravel*`), loose rubble pieces (F-pickup) | B |
| Clay | Clay | `Soil_Clay`, `Soil_Clay_Ocean` | clay (self-drop), clay stalactites | S |
| Copper | Copper Ore | `Ore_Copper` | `Ore_Copper_Stone` / `_Sandstone` / `_Shale`; the Klops_Miner mob | S |
| Iron | Iron Ore | `Ore_Iron` | 7 `Ore_Iron_*` veins; Klops_Miner | S |
| Silver | Silver Ore | `Ore_Silver` | 6 `Ore_Silver_*` veins | R |
| Gold | Gold Ore | `Ore_Gold` | 6 `Ore_Gold_*` veins (including Calcite) | R |
| Thorium | Thorium Ore | `Ore_Thorium` | `Ore_Thorium_Mud*`, `_Sandstone` | R |
| Cobalt | Cobalt Ore | `Ore_Cobalt` | `Ore_Cobalt_Shale`, `_Slate*` | R |
| Adamantite | Adamantite Ore | `Ore_Adamantite` | `Ore_Adamantite_Magma*` | E |
| Mithril | Mithril Ore | `Ore_Mithril` | `Ore_Mithril_Stone` | E |
| *(hidden)* Onyxium | Onyxium Ore | `Ore_Onyxium` | **no gathering source found.** No block drops it and no NPC drop list names it. Stays hidden until a source exists. UNVERIFIED where it comes from | E |
| Crystal | Crystal Shards | `Ingredient_Crystal_Blue`, `_Cyan`, `_Green`, `_Pink`, `_Purple`, `_Red`, `_White`, `_Yellow` | `Rock_Crystal_*` (Small/Medium/Large/Block); crystal golems; frost/sand skeleton mages | R |
| Gemstone | Gemstones | `Rock_Gem_Diamond`, `_Emerald`, `_Ruby`, `_Sapphire`, `_Topaz`, `_Voidstone`, `_Zephyr` | gem blocks (self-drop); crystal golems | E |

`Ore_Prisma` also exists with no source. VERIFIED. It is left out of the registry.

### 2.5 Combat (coins instead of skill XP, see 4.3)

| Id | Name | Item id(s) | Fed by (VERIFIED NPC drop lists) | Curve |
|---|---|---|---|---|
| Bone | Bone Fragments | `Ingredient_Bone_Fragment` | 32 roles: skeletons, ghouls, skeleton horses | S |
| Linen | Linen Scraps | `Ingredient_Fabric_Scrap_Linen` | 45 roles: skeletons, ghouls | S |
| HideLight | Light Hide | `Ingredient_Hide_Light` | 35 roles: chicken, deer, antelope, camel, ... | S |
| HideMedium | Medium Hide | `Ingredient_Hide_Medium` | 25 roles: cow, boar, horse, hyena, ... | S |
| HideHeavy | Heavy Hide | `Ingredient_Hide_Heavy` | 10 roles: polar bear, crocodile, mosshorn, cave rex, emberwulf | R |
| Wool | Wool Scraps | `Ingredient_Fabric_Scrap_Wool` | Sheep (killed). Shearing is **not counted in 0.2**, see the gap note below the table | S |
| Feathers | Feathers | `Ingredient_Feathers_Blue`, `_Dark`, `_Light`, `_Red` | 21 bird roles | S |
| Chitin | Sturdy Chitin | `Ingredient_Chitin_Sturdy` | 13 roles: scaraks, armadillo | R |
| Venom | Venom Sac | `Ingredient_Sac_Venom` | 8 roles: scaraks, scorpion, snakes, cave spider | R |
| Shadoweave | Shadoweave Scraps | `Ingredient_Fabric_Scrap_Shadoweave` | 9 outlander roles | R |
| Cindercloth | Cindercloth Scraps | `Ingredient_Fabric_Scrap_Cindercloth` | 14 roles: burnt skeletons, flame golem | R |
| FireEssence | Essence of Fire | `Ingredient_Fire_Essence` | 20 roles | R |
| IceEssence | Essence of Ice | `Ingredient_Ice_Essence` | 11 frost skeleton roles | R |
| VoidEssence | Essence of the Void | `Ingredient_Void_Essence` | 8 void roles and outlander casters | R |
| LightningEssence | Essence of Lightning | `Ingredient_Lightning_Essence` | Spirit_Thunder | E |
| Voidheart | Voidheart | `Ingredient_Voidheart` | 5 void roles | E |
| BoomPowder | Boom Powder | `Ingredient_Powder_Boom` | Boomshroom plants (break or F). In Combat because the SkyySacks Combat bag holds it `[SKYY?]` | S |

The other hides (`Hide_Dark`, `_Soft`, `_Scaled`, `_Storm`, `_Prismic`) appear in no NPC drop list that was found. They are left out until a source shows up.

**Gap: harvesting tamed livestock is not counted in 0.2 `[SKYY?]`.**
- Shears on a **tamed** sheep are a normal, non-lethal way to get wool. `Tamed_Sheep` has `IsHarvestable`, needs `Tool_Shears_Basic` in hand, and drops `Drop_Sheep_Harvest` (1-3 Wool Scraps + 0-1 Poop), then waits 11-14 h. Tamed chickens and skrill give feathers the same way (`Drop_Chicken_Harvest`, `Drop_Skrill_Harvest`); tamed cows give milk, which is not a collection. Wild sheep cannot be sheared. All VERIFIED in Assets.zip.
- None of H1-H5 sees it. The NPC's `DropItem` action (`ActionDropItem.execute`) rolls the list and calls `ItemUtils.throwItem`, so the items land on the ground with no player attached, and walking over them fires no event (3.3). VERIFIED bytecode.
- A later hook needs the moment of the harvest plus the player who did it (the NPC's `$Harvest` state, or the interaction that sets it). Which engine class exposes that is UNVERIFIED.
- Until then, wool and feathers count only from kills. Skyy to accept this for 0.2, or ask for the extra hook.

### 2.6 Not collections (decided)

| Thing | Why |
|---|---|
| Grass (`Plant_Grass_*`) | Gives nothing |
| Bushes, leaves and other plant **blocks** | They are sources, not items |
| Flowers, saplings, coral, ferns | Decoration that drops itself; saplings do not drop from leaves (VERIFIED `Tree_Leaves` = fibre only) |
| Soil_Dirt and its variants, snow, mud | Filler, like SkyBlock (which has no Dirt collection) `[SKYY?]` |
| Crafted or processed items: bars, planks, leather, bolts, flour, charcoal, bread | Crafting outputs never count (SkyBlock rule) |
| Placed furniture or deco (`Furniture_Crude_Torch`, ...) | Placed items |
| Weapons, armor, potions and arrows dropped by mobs | Gear, not materials |
| `Ingredient_Salt`, `Food_Egg` | Salt: only from containers. Eggs: from nests, and from chickens laying them on their own (`ProduceItem`, `Drop_Chicken_Produce`), with no player action that a hook could see (VERIFIED assets) |
| Tree Bark | Later (no break event, 2.3) |

---

## 3. What counts

### 3.1 The hooks

Every system is an ECS system on the player's entity, following the `CollSystem`/SkyySkills pattern. VERIFIED patterns:
- `EntityEventSystem`, with `super(<Event>.class)` and `getQuery() = Archetype.empty()`
- the player comes from `chunk.getReferenceTo(idx)` plus the `PlayerRef` component

Awards are **deferred with `world.execute(Runnable)`** and paid only if `event.isCancelled()` is still false once the task runs. SkyySkills 0.1 `BreakTask` does the same (VERIFIED), so SkyyIslands protection and any other cancelling system have already run.

| # | System (new class) | Event / engine class | What it does |
|---|---|---|---|
| H1 | `CollBreakSys` | `com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent`: `getBlockType()`, `getTargetBlock()`, `getItemInHand()` (VERIFIED) | **Sync:** skip creative. Store a `GatherCtx` for the player: world, position, block id, held item id, `placed` (in PlacedStore), `ripe` (state `StageFinal`), the pkey, and an empty list of pickups. **Deferred** (`CollBreakTask`): if cancelled → nothing. Remove the position from PlacedStore. If placed and not a ripe crop → nothing. If the ctx caught pickup stacks (H3) → credit **those exact stacks**. Otherwise credit `CollDrops.breakDrops(bt, heldItemId)` (a re-roll, 3.2) |
| H2 | `CollUseSys` | `UseBlockEvent$Post` (VERIFIED, SkyySkills `HarvestSys`) | **Sync:** if the block is in state `StageFinal` and `getGathering().getHarvest() != null` (a ripe crop or berry bush), store a use ctx: position, ripe=true, valid for 2,000 ms. No credit here |
| H3 | `CollPickupSys` | `com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent` (cancellable, `getItemStack()`/`setItemStack()`), fired on the player's ref by `ItemUtils.interactivelyPickupItem` **before** `Player.giveItem` (VERIFIED) | **Sync:** if the player has a break ctx from this same tick → add the stack to that ctx (H1's deferred task credits it). Otherwise, if there is a use ctx under 2 s old → queue `CollPickupTask`, which credits `getItemStack()` if not cancelled. **No ctx → ignore** (another mod or a reward calling `interactivelyPickupItem`) |
| H4 | `CollPlaceSys` | `PlaceBlockEvent` (VERIFIED, SkyySkills `PlaceSys`) | Deferred: if not cancelled → `PlacedStore.add(world, key(x,y,z))` |
| H5 | `CollKillSys extends com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem` | `onComponentAdded(DeathComponent)` on an `NPCEntity`; killer = `DeathComponent.getDeathInfo().getSource()` as `Damage.EntitySource` → `getRef()` → `PlayerRef` (VERIFIED, SkyySkills `KillSys`; `ProjectileSource` extends `EntitySource`) | Skip creative. `NPCEntity.getRole().getDropListId()` → `ItemModule.get().getRandomItemDrops(id)` → credit the killer (a re-roll). The NPC's own inventory dump (`Role.isPickupDropOnDeath()`) is **not** counted |

**Why H1 and H3 must share one ctx (VERIFIED bytecode, a new finding).**
- A break interaction whose config has `harvest=true` (the F pickup of a loose "harvestable" block) calls `BlockHarvestUtils.performPickupByInteraction`.
- That method first fires `BreakBlockEvent`, then removes the block.
- It then rolls the **Harvest** drops and calls `ItemUtils.interactivelyPickupItem` for each stack, which fires `InteractivelyPickupItemEvent`.
- Both events come in the same call stack. `world.execute` always runs afterwards, so the deferred break task knows whether pickups arrived.
- Crediting both would double count. Crediting only the break's re-roll would use the wrong table: Breaking/Soft instead of Harvest.

Crop F-harvest takes a different path: `UseBlockEvent.Post` → HarvestCrop → `FarmingUtil.giveDrops` rolls `getDrops` once → `interactivelyPickupItem`. VERIFIED. So H3 gives the exact crop stacks without the SkyySkills poll (`HarvestTask`).

**Fallback, if H3 never fires in game:** copy SkyySkills' `HarvestGate` + `HarvestTask` poll. On a confirmed harvest, credit `getDrops(bt, 1, harvest.getItemId(), harvest.getDropListId())`. UNVERIFIED which one is needed. Test item T9.

### 3.2 `CollDrops`: copy SkyySkills, then fix the tool case

Copy `Perks.toolDependent(BlockGathering)` and `Perks.breakDrops(BlockType)` from `build_skyyskills_0.3.2.py` (VERIFIED code):

| Case | Drops |
|---|---|
| `isSoft()` with a Soft entry | `BlockHarvestUtils.getDrops(bt, 1, soft.getItemId(), soft.getDropListId())` |
| Breaking entry | `getDrops(bt, breaking.getQuantity(), breaking.getItemId(), breaking.getDropListId())` |
| Both Soft and Breaking | Nothing (which one applied is unknown) |

`getDrops` works like this (VERIFIED bytecode):
- With no item id and no drop list, it returns the block's **own item** × quantity.
- Otherwise it rolls the drop list `quantity` times through `ItemModule.getRandomItemDrops`, and adds the item id if one is set.

**Tool-dependent blocks.** SkyySkills skips these; Collections resolves them.
- The engine looks up `BlockGathering.getToolData().get(toolId)` (a `BlockGathering$BlockToolData`, with `getStateId()`, `getItemId()`, `getDropListId()`).
- `toolId` is the break interaction's private `toolId` field. VERIFIED (`BreakBlockInteraction.interactWithBlock` → `performBlockDamage` → `damageSingleBlock`).
- In the assets, three break interactions set it, all the same shape (a `BreakBlock` step): `"Tool": "Pickaxe"` (`Pickaxe_Block_Break`, reached from the pickaxe's `Primary: Pickaxe_Attack`), `"Tool": "Shears"` (`Shears_Block_Break`, reached from `Tool_Shears_Basic` → `Shears_Attack`), and `"Tool": "Scraper"` with `MatchTool: true` (`Scraper_Chop`, held item `Tool_Bark_Scraper`). VERIFIED.
- Whether a tool breaks the block or only changes its state is a property of the **block's** tool entry (`getStateId()`), not of the tool. The Scraper never breaks anything today only because every block with a Scraper entry (the trunks) gives it a state (2.3 note). VERIFIED.

So:

```
key = held.startsWith("Tool_Pickaxe_") ? "Pickaxe"
    : held.startsWith("Tool_Shears_")  ? "Shears"
    : held.equals("Tool_Bark_Scraper") ? "Scraper"
    : null
td  = key == null ? null : toolData.get(key)
td != null && td.getStateId() == null  -> drops = getDrops(bt, 1, td.getItemId(), td.getDropListId())
td != null && td.getStateId() != null  -> nothing (a state change, no break)
otherwise                              -> the normal Soft/Breaking path above (the engine does the same when the key is missing, VERIFIED)
```

What this gives in practice:
- Shears entries have no item or list, so shears on a bush yield the bush block. That is not a collection item, so there is 0 credit, which is correct.
- A pickaxe on gravel yields 2-3 Stone Rubble.
- The Scraper case is there so that a future block with a stateless Scraper entry is read correctly. With today's assets it always lands on the state branch, and no H1 event arrives for it anyway.

The link from held item to toolId goes by the tool family's interaction name. VERIFIED from the assets. The in-game result is UNVERIFIED (T6).

**Re-roll caveat (same as SkyySkills' double drop).** H1 (normal breaks) and H5 (kills) roll the drop list again. The count is right on average but can differ by one from what landed on the ground. Guaranteed drops are exact every time: logs, cobble, ores, fixed quantities. VERIFIED behaviour of `getDrops`.
Option B for later: match the spawned ground items, which would make these exact too. `BlockHarvestUtils.spawnDrops` → `ItemComponent.generateItemDrops` → `addEntities(holders, AddReason.SPAWN)` (VERIFIED), with the spawn point at `(x+0.5, y, z+0.5)`. A `RefSystem` on `ItemComponent` could match new ground items to a pending break at that point. UNVERIFIED, so not in 0.2. Note: `spawnDrops` itself is `private static` (VERIFIED, reflection), so a mod cannot call or override it without `setAccessible`; Option B has to observe the item entities it adds (the `RefSystem` idea) or start from the public `performBlockBreak` / `performBlockDamage`.

### 3.3 Anti-exploit

| Rule | How | Status |
|---|---|---|
| Placed blocks never count | Copy SkyySkills' `PlacedStore`: per-world LRU of 400,000 positions, file `Skyy_SkyyCollections/placed/<world>.bin`, filled by H4. H1 removes the position and gives 0. **Exception:** ripe crops and berry bushes (always planted). F-pickups (H3) of a placed position also give 0. On the first 0.2 start, seed the store once, read-only, from `Skyy_SkyySkills/placed/*.bin` if present (same key format and code) | Pattern VERIFIED (SkyySkills); seeding UNVERIFIED |
| The engine's own guard | `BlockPlaceUtils.tryPlaceBlock` → `BlockPhysics.markDeco` when `canBePlacedAsDeco()`. `damageSingleBlock` then drops the block itself for `UseDefaultDropWhenPlaced` blocks (leaves, bushes, grass, reeds, vines, branches, berry bushes). This agrees with our PlacedStore | VERIFIED |
| Items a player drops or throws never count | We never count ground pickups. The engine has no pickup event for walking over items (`PlayerItemEntityPickupSystem` → `Player.giveItem`, no event) and no thrower field on `ItemComponent` | VERIFIED |
| Creative gives nothing | `Player.getGameMode() == GameMode.Creative` (SkyySkills `SkillXp.creative`) | VERIFIED pattern |
| Trades, Bazaar, /craft, furnace/tannery queues, bag withdrawals, `/give`, quest or starter-chest items never count | None of them fires H1-H5 | VERIFIED by design |
| Cancelled actions | Deferred `isCancelled()` check (island protection, other mods) | VERIFIED pattern |
| Explosions and physics (leaf decay, falling blocks) | No player behind them → no credit | VERIFIED (`naturallyRemoveBlockByPhysics`, no player ref) |
| Kills | Credit only the killer (`Damage.EntitySource`). Classless players' kills count too (SkyBlock counts every kill) `[SKYY?]` | pattern VERIFIED |
| Sanity cap | At most 256 per single credit and 20,000 units per player per minute. Anything above is dropped, with one log line per player per minute | UNVERIFIED numbers |
| Profile switch in flight | The deferred task drops the credit if `pkey(u)` differs from the pkey stored in the ctx (same rule as the Alchemy spec, section 6 point 8) | design |

### 3.4 Sacks

- Collections count **at the source**, before any item reaches a container. The SkyySacks 2 s sweep (`SackTick` → `SweepTask`, storage only) cannot hide an item from collections, and a withdrawal cannot add one. VERIFIED design; the SkyySacks code was read.
- This meets the SkyySacks plan note "sack-routed pickups still count toward collections". VERIFIED.
- SkyySacks keeps reading `coll:recipes:<uuid>` for its Collections tab, which lists the recipes and crafts them without a bench. VERIFIED, `CraftPageGen.collectionRecipes` + `recipesFor("C:")`. The format is unchanged.
- Bag perks tied to collections are later ideas, not 0.2. Example: +50% cap for an item whose collection is maxed. `[SKYY?]`

### 3.5 Per-profile storage (tools/PROFILES-CONTRACT.md)

- Files: `Skyy_SkyyCollections/counts/<pkey>.properties`. `pkey` = the contract helper, already in 0.1.5 (VERIFIED): profile 1 = `<uuid>`, profile N = `<uuid>-pN`. Caches and the dirty set are keyed by the pkey string, as in 0.1.5.
- File keys:
  - `<itemId>=<long>` for registry items only
  - `_schema=2`
  - `_paid.<CollId>=<tier>`: the highest tier whose coins/XP were paid. It advances only after the payment succeeds; unpaid tiers are retried on the next credit or saver tick (SkyySkills `.paid` pattern)
  - `_bought.<CollId>=<tier>`: the highest tier bought with coins
  - `_name=<player name>`: last known name, written on join, for the leaderboards (5.5)
  - Keys starting with `_` are metadata. No item id starts with `_`.
- Bridge values stay keyed by UUID and are republished on a `profile:epoch:<uuid>` change. This reuses 0.1.5's `syncEpoch` / `CollRecheck` chain unchanged. VERIFIED code.
- Saver: every 5 s for the epoch check, and a flush every 10 s. The final flush runs in `shutdown()` (0.1.5 `CollSaver`). VERIFIED.

### 3.6 Co-op (later, not in 0.2)

- SkyBlock shares collections across a co-op profile and shows how much each member contributed. VERIFIED.
- SkyWynn's co-op lock is "share and visit islands" (design lock, batch 2, item 6). Collections stay per profile in 0.2.
- To leave room for later: a co-op profile would get a shared key `coop-<id>`, with member lines `<itemId>@<uuid>=n` for contributions. The shape of the file format allows this. UNVERIFIED.
- The Bestiary (kill counts → stats, decision 6.9) is a separate future system, not part of item collections.

---

## 4. Tiers and rewards

### 4.1 Curves (thresholds = total items collected)

| Curve | Tiers | Thresholds | Used for |
|---|---|---|---|
| **B** Bulk | 10 | 50 · 100 · 250 · 500 · 1,000 · 2,500 · 5,000 · 10,000 · 25,000 · 50,000 | fiber, sticks, cobble and host rocks, sand, rubble, seeds, Essence of Life, Oak Log |
| **S** Standard | 9 | 50 · 100 · 250 · 500 · 1,000 · 2,500 · 5,000 · 10,000 · 20,000 | crops, common logs, copper, iron, common mob drops |
| **R** Rare | 8 | 25 · 50 · 100 · 250 · 500 · 1,000 · 2,500 · 5,000 | silver, gold, thorium, cobalt, crystals, exotic logs, rare mob drops |
| **E** Elite | 7 | 10 · 25 · 50 · 100 · 250 · 500 · 1,000 | adamantite, mithril, gemstones, Voidheart, Essence of Lightning |

**Why these numbers.**
- Hytale yields per action are close to SkyBlock's: 1 per log, cobble or ore; about 1.5 per ripe crop or kill; 0.5-0.7 fiber per bush or leaf. VERIFIED drop tables.
- SkyWynn has no minions or fortune yet; the only multiplier is the SkyySkills double drop, up to 50%. So the top ends are about 1/2 to 1/8 of SkyBlock's (Wheat 100k → 20k, Cobblestone 70k → 50k).
- Tier I stays 50 for common items. That matches SkyBlock and 0.1.x (`TIERS[0]=50`).

All numbers are UNVERIFIED balance `[SKYY?]` and live in `collections.properties`.

### 4.2 Rewards on every tier (defaults)

| Tier | I | II | III | IV | V | VI | VII | VIII | IX | X |
|---|---|---|---|---|---|---|---|---|---|---|
| Coins (`coins:fn:add`) | 50 | 100 | 200 | 400 | 800 | 1,500 | 3,000 | 6,000 | 12,000 | 25,000 |
| Skill XP (Farming/Mining/Foraging) | – | – | 500 | – | 2,500 | – | 10,000 | – | – | – |
| Last tier of the collection | +25,000 skill XP, in place of that tier's slot above |
| Collection score | +1 per tier, like SkyBlock's +4 SkyBlock XP per tier. Published as `coll:score:<uuid>` for a future SkyBlock Level |

All UNVERIFIED `[SKYY?]`.

- **Coins:** `coins:fn:add` `apply(Object[]{UUID, Long}) -> Long`. VERIFIED, SkyyCoins 0.1.5 docstring.
- **Skill XP:** `skill:fn:addxp` `apply(Object[]{UUID player, String skill, Number baseXp, String source}) -> Boolean` with source `"coll:<CollId>:<tier>"`. VERIFIED contract, `research/Alchemy-Skill-Spec.md` 7.1. SkyySkills 0.4 is **not built yet**.
- **Needed in SkyySkills:** the Alchemy spec only lets `bridge.addxp.skills` (default `Alchemy,Smithing`) be granted from outside. "Gathering ... cannot be granted from outside." SkyySkills must add `Mining,Foraging,Farming` to that default `[SKYY?]`. Until then the call returns FALSE and the reward stays owed (`_paid` does not advance). This is the only change Collections needs in another mod.
- **Combat collections** pay **double coins** on the III/V/VII/last tiers instead of XP. The reason is VERIFIED: class weapon skills cannot be granted from outside (same contract). The ×2 multiplier itself is a new balance number, UNVERIFIED `[SKYY?]`.
- **Chat on a tier:** a gold line "COLLECTION UP  Wheat V", then one line per reward (coins, XP, each recipe name). The first item of a collection shows "New collection: Wheat!". There is no per-item chat spam.

### 4.3 Recipe unlocks (`rewards.properties`, explicit only)

- **Format:** `<CollId>.<tier>=recipe:<RecipeId>,recipe:<RecipeId>,coins:<n>,xp:<Skill>:<n>`. Explicit entries **add to** the defaults in 4.2.
- **Recipe ids:** `<OutputItemId>_Recipe_Generated_<index>`. VERIFIED from Skyy's `crafts.log` (for example `Ingredient_Bar_Copper_Recipe_Generated_0`, `Furniture_Crude_Torch_Recipe_Generated_0`) and from the item-embedded `Recipe` lists in Assets.zip.
- **Filters:** `CollUnlocks` skips ids missing from `CraftingRecipe.getAssetMap()`, logged once. It also skips every recipe whose `BenchRequirement.id` is on an **excluded bench list**: config `exclude.benches`, default `Alchemybench,Cookingbench,Furnace,Tannery,Campfire,Salvagebench`, matched case-insensitively.
  - **Do not filter on `BenchRequirement.type`.** Alchemybench and Cookingbench recipes are `Type: Crafting`, so a `type == Processing` check would let them through. VERIFIED, every BenchRequirement in Assets.zip:

    | Type | Bench ids |
    |---|---|
    | `Processing` | Campfire, Furnace, Salvagebench, Tannery |
    | `Crafting` | Alchemybench, Cookingbench, Workbench, Farmingbench, Armor_Bench, Weapon_Bench, Furniture_Bench, Loombench, Arcanebench, Builders (12), Fieldcraft, and a few odd ids (`TODO`, `Architects`, `ArmorBench`) |
    | `StructuralCrafting` | Builders (906 recipes, including the bricks below) |
    | `DiagramCrafting` | Armory |

  - SkyySacks 0.7.2 also works by bench id: `separateBench()` = Alchemybench, Furnace, Tannery (VERIFIED). It uses that list to split tabs, and it lacks Cookingbench, Campfire and Salvagebench, so Collections keeps its own list. The type check the first draft cited (`benchRecipes(u, processing)`) was SkyySacks 0.6.8 and is gone in 0.7.x (VERIFIED).
  - Excluding the processing benches keeps the instant Collections tab from skipping furnace time and fuel.
- Cooking and alchemy recipes are never listed, because Skyy made those table-only. The `exclude.benches` default enforces it.

**What "unlocked" means today:** the recipe shows in /craft → Collections and can be crafted there **without the bench or bench tier**. The materials are still needed. VERIFIED SkyySacks behaviour. That is early access, like SkyBlock. A hard lock, where the recipe cannot be crafted anywhere else, is the open spike in the Mod Roster ("can we gate recipes per player?"). It is not in 0.2.

**Default table** (vanilla ids VERIFIED in Assets.zip; the bench each normally needs is in brackets):

| Collection | Tier → recipe |
|---|---|
| Wheat (S) | I `Tool_Sickle_Crude_Recipe_Generated_0` [Farmingbench T2] · III `Tool_Hoe_Copper_Recipe_Generated_0` [Farmingbench T2] · IV `Tool_Sickle_Copper_Recipe_Generated_0` [T4] · V Medium Farming Bag · VI `Tool_Sickle_Iron_Recipe_Generated_0` [T5] · VII `Tool_Hoe_Iron_Recipe_Generated_0` [T4] · VIII Large Farming Bag |
| Oak Log (B) | I `Tool_Hatchet_Copper_Recipe_Generated_0` [Workbench] · III Small Foraging Bag · V Medium Foraging Bag · VI `Tool_Hatchet_Iron_Recipe_Generated_0` [Workbench] · VIII Large Foraging Bag |
| Cobblestone (B) | I `Tool_Pickaxe_Copper_Recipe_Generated_0` [Workbench] · III Small Mining Bag · IV `Rock_Stone_Brick_Recipe_Generated_0` [Builders] · V Medium Mining Bag · VI `Tool_Pickaxe_Iron_Recipe_Generated_0` [Workbench] · VIII Large Mining Bag |
| Plant Fiber (B) | III `Tool_Shears_Basic_Recipe_Generated_0` [Farmingbench] |
| Stick (B) | III `Weapon_Arrow_Crude_Recipe_Generated_0` [Workbench / Weapon_Bench] |
| Bone Fragments (S) | III Small Combat Bag · V Medium Combat Bag · VIII Large Combat Bag |
| Sandstone / Shale / Slate / Basalt / Marble (B/S) | IV `Rock_<Rock>_Brick_Recipe_Generated_0` [Builders] (Sandstone, Shale, Slate, Basalt, Marble all VERIFIED) |
| Every collection | I = its **minion recipe** once SkyyMinions exists (SkyBlock pattern; the entry is simply added to `rewards.properties` then) |

- **Bag ids:** `Skyy_Sack_<Mining|Foraging|Farming|Combat>_<Small|Medium|Large>` (VERIFIED, `sack_item()` in SkyySacks 0.7.2). Recipe id = `..._Recipe_Generated_0` (pattern UNVERIFIED for Skyy items).
- Today these bags are also craftable at a Workbench. The unlock only matters once SkyySacks takes Medium and Large off the Workbench. That is a SkyySacks follow-up; test it before relying on it. UNVERIFIED `[SKYY?]`. The SkyySacks plan already says "Sacks unlock via collection milestones".
- Talismans (SkyyAccessories) are good later rewards. Their ids are being renamed to rarity names, so they are left out of the defaults.
- **Bricks:** the Builders brick recipes are `StructuralCrafting` (VERIFIED). Whether the /craft Collections tab crafts that type through `CraftingManager.craftItem` is UNVERIFIED; test it (T14) before relying on the brick unlocks.
- **Scope of 0.2, plainly:** every collection gets the default coins / skill XP / score curve from 4.2. Explicit recipe unlocks cover only the rows above, plus the ore line below if Skyy takes it. The other collections (94 of the 105 registry rows, a third of them log types; 88 if the ore line is taken) ship with **no recipe reward** in 0.2. SkyBlock gives almost every collection several curated recipes, so this is the biggest gap against the model. Filling them is 0.3 work, as SkyWynn items (armor sets, accessories, minions) appear. `[SKYY?]`

**Proposed ore line** (vanilla ids and benches VERIFIED in Assets.zip; the tier choices are UNVERIFIED design `[SKYY?]`). SkyBlock gives each ore its own armor and tools (Iron Ingot II = armor, section 1). Copper and Iron tools already sit on Cobblestone, Oak Log and Wheat, so these ore collections take the armor, and the higher metals also take their tools. Recipe id = `<id>_Recipe_Generated_0`.

| Collection | Tier → recipe [bench it normally needs] |
|---|---|
| Copper (S) | II `Armor_Copper_Head` · III `Armor_Copper_Hands` · IV `Armor_Copper_Legs` · V `Armor_Copper_Chest` [Armor_Bench] |
| Iron (S) | II-V the same four `Armor_Iron_*` pieces [Armor_Bench] |
| Thorium (R) | I `Tool_Pickaxe_Thorium` + `Tool_Hatchet_Thorium` [Workbench T2] · II-V `Armor_Thorium_Head/Hands/Legs/Chest` [Armor_Bench T2] · VI `Tool_Hoe_Thorium` [Farmingbench T6] |
| Cobalt (R) | I `Tool_Pickaxe_Cobalt` + `Tool_Hatchet_Cobalt` [Workbench T2] · II-V `Armor_Cobalt_*` [Armor_Bench T2] |
| Adamantite (E) | I `Tool_Pickaxe_Adamantite` + `Tool_Hatchet_Adamantite` [Workbench T3] · II-V `Armor_Adamantite_*` [Armor_Bench T3] |
| Mithril (E) | I `Tool_Pickaxe_Mithril` + `Tool_Hatchet_Mithril` [Workbench T3] · II-V `Armor_Mithril_*` [Armor_Bench T3] |

- Silver and Gold have no vanilla armor or tools (VERIFIED), so they stay on the default curve.
- Weapons are left out because they are class-locked.
- An unlock skips the bench tier ("What unlocked means", above). For Adamantite and Mithril that is early access to tier-3 gear; the bars still need the Furnace. `[SKYY?]`

**Auto rule: off by default in 0.2** (`auto=false`). It stays available as an opt-in. Reasons (VERIFIED):
- With correct item counts, Plant Fiber at tier I would unlock every recipe that uses fiber and has no other started input: up to 119 recipes. Sticks: 28, Tree Sap: 27.
- `MaterialQuantity.getItemId()` is null for resource-type inputs (113 recipes take `ResourceTypeId: Wood_Trunk`), so the rule misses them anyway.

### 4.4 Coin-bypass

**Current design lock (2026-09-24), not yet in the jar:** coins can bypass collections in the **early game** and the **first half of mid game**. Toward late game those items can no longer be **bought or sold** (bazaar/market), so that progression is earned. Many items will have level requirements. **Open:** the exact cutoff per collection and per tier, and which level type gates an item (skill vs class vs combat level). Do not treat the numbers in this section as that cutoff.

**What SkyyCollections 0.2 actually shipped** (code follow-up, do not edit the jar from this spec): bypass is on, and it still uses the older per-curve walls (`bypass.walls=5,4,3,0`: Bulk through V, Standard through IV, Rare through III, Elite never). That is wider than "early + first half of mid," and it does not remove items from the bazaar. SkyyBazaar 0.1.1 has no late-game sell wall. The paragraph that used to say "nothing is built yet" is out of date: 0.2's bypass page is live (HANDOFF: Cobblestone "Buy tier III unlocks").

The rules below are the **0.2 implementation** of the older lock. They stay here so the built behavior is documented. They are not the 2026-09-24 lock.

**Rules (0.2, older lock):**
- **What you buy:** only the next tier's **recipe unlocks**. Buying does not raise the count, does not pay that tier's coins/XP/score, and does not count for leaderboards. The tier shows as **BOUGHT** (amber). When the real count later passes the threshold, the tier becomes DONE and pays its normal rewards once, through `_paid`.
- **Who can buy:** the collection must be discovered (at least 1 collected). Tiers go one at a time; the previous tier must be done or bought. The tier must be at or below the curve's **wall**: Bulk ≤ V, Standard ≤ IV, Rare ≤ III, Elite never. Those numbers are the 0.2 config. They are not the 2026-09-24 cutoff (that one is open, above). A per-collection flag `nobypass` exists for lines that should never be buyable.
- **Price:**
  ```
  price = max(500, ceil(missing × unit × 5))
  missing = threshold − current count
  unit = bazaar:buy:<first item of the collection>, else a fallback per curve (B 2, S 5, R 25)
  ```
  `bazaar:buy:<itemId>` is a Long. VERIFIED, SkyyBazaar 0.1.1 docstring. It is 5× the price of simply buying the items, even though bought items never count `[SKYY?]`.
  Examples. SkyyBazaar 0.1.1 base prices are Wheat 2 and Iron Ore 8 (VERIFIED, `PRODUCTS`). The bridge key holds the instant-buy price for 1, `ceil(base × demand factor × 1.10)` (VERIFIED, `Market.publish` → `quote`), so 3 and 9 at neutral demand:
  - Wheat 260 → tier IV (500) = 240 × 3 × 5 = **3,600 coins**.
  - Iron 30 → tier II (100) = 70 × 9 × 5 = **3,150 coins**.

  The price follows Bazaar demand (factor 0.25-4.0). The curve fallback (B 2, S 5, R 25) is used only when the `bazaar:buy:` key is missing.
- **Payment:**
  - `coins:fn:take` `apply(Object[]{UUID, Long}) -> Boolean` runs first. VERIFIED signature.
  - Then `_bought.<CollId>=<tier>` is written and `coll:recipes` republished.
  - If the write fails → refund with `coins:fn:add`.
  - Every purchase is logged to `Skyy_SkyyCollections/bypass.log`.
  - A second click within 10 s confirms (the Bazaar "Sell inventory" pattern).
- **Unlock set:** effective tier = max(count tier, bought tier).

---

## 5. UI

### 5.1 Rules

HANDOFF section 2 rules plus Skyy's size requests:
- One inline `CustomUIPage` (`CollPage`) with `build()` public. No `.ui` files.
- Views switch with `rebuild()` inside the same page (SkyyMenu 0.1.1 pattern, VERIFIED working). The page must **never** close itself and open another page: the SkyyMenu "hangs on Loading..." bug is caused by `setPage(None)` followed by an open (HANDOFF log 22:30, VERIFIED).
- Root: `b.appendInline((String) null, "Group #SkyyColl { Anchor: (Width: 1120, Height: 840); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }")`. The anchor holds only Width and Height, so the page system centres it. The size sits between the live Sacks craft page (1000×830) and the HUD editor (1330×930), per Skyy's "bigger" requests.
- **Element ids use no underscores:** `#SkyyCTitle`, `#SkyyCCat0`..`3`, `#SkyyCCard0`..`11`, `#SkyyCBar0`..`11`, `#SkyyCTier0`..`11`, `#SkyyCBuy`, `#SkyyCBack`, `#SkyyCHome`, `#SkyyCPrev`, `#SkyyCNext`, `#SkyyCRefresh`, `#SkyyCClose`.
- **Buttons:** `TextButton` with `TextButtonStyle(Default/Hovered/Pressed)`, bound by `ev.addEventBinding(CustomUIEventBindingType.Activating, "#Id", EventData.of("a", "<payload>"))`. `handleDataEvent` matches `data.indexOf("<payload>\"")`. The closing quote keeps `ccard1"` and `ccard11"` apart. VERIFIED pattern.
- **Text:** fixed labels go in `appendInline`, cleaned with SkyySkills' `safe()`. Every dynamic text (names, numbers with commas) is set with `b.set("#Id.Text", v)`, which HANDOFF calls "safe for anything".
- **Icons:** `ItemIcon { Anchor: (...); ItemId: "<id>"; }` (VERIFIED, SkyySkills page renders). Progress bars: a background `Group` with a fill `Group` of computed width (VERIFIED, SkyySkills).
- **Font sizes:** title 28, headers 20-24, body 16-18, small 14. Nothing under 13. The current page uses 11-15.
- **No periodic updates.** The page only rebuilds on a click. There is a Refresh button. `PageManager` drops every page click while `customPageRequiredAcknowledgments != 0`: each open or update adds 1, each client ack takes 1 away (HANDOFF log 22:30, VERIFIED). Nothing is ever sent from hover handlers either; those crash the client (HANDOFF section 2).
- **Colours:**

  | Category | Accent |
  |---|---|
  | Farming | `#e0c060` |
  | Mining | `#9fb8cc` |
  | Foraging | `#7fcf7a` |
  | Combat | `#e07a6a` |

  | Tier status | Chip |
  |---|---|
  | DONE | `#3aa655` |
  | NEXT | `#d9b038` |
  | LOCKED | `#8a3a36` |
  | BOUGHT | `#d98a2b` |

  The status colours copy the SkyBlock pane colours reported in the research notes.

### 5.2 View HOME (`/collections`, `/coll`)

```
+--------------------------------------------------------------------------------------------+
|                          Collections                         (FontSize 28, bold)            |
|   Gather items yourself to raise collections. Every tier unlocks rewards.   (16)            |
|   Tiers 34 / 812    Maxed 2    Recipes unlocked 11    Score 34     (18, set via b.set)      |
|  +-------------------------------------+   +-------------------------------------+          |
|  | [icon 80] Farming          (26)     |   | [icon 80] Mining            (26)    |          |
|  | 12 of 26 found             (18)     |   | 9 of 24 found               (18)    |          |
|  | [=========-------] bar 440x18       |   | [=====-----------]                  |          |
|  | Tiers 18 / 237   Maxed 1   (16)     |   | Tiers 10 / 228              (16)    |          |
|  | [ Open Farming ] TextButton 240x48  |   | [ Open Mining ]                     |          |
|  +-------------------------------------+   +-------------------------------------+          |
|  (same for Foraging and Combat: cards 520 x 230)                                            |
|  Fishing - coming later (grey label, no button)                                             |
|  [ Unlocked recipes ]   [ Refresh ]                                    [ Close ]            |
+--------------------------------------------------------------------------------------------+
```

- **Icons:** Farming `Plant_Crop_Wheat_Item`, Mining `Ore_Copper`, Foraging `Wood_Oak_Trunk`, Combat `Ingredient_Bone_Fragment`. All exist (VERIFIED).
- **Payloads:** `ccat0`..`ccat3`, `crecipes` (a text list of unlocked recipes with Back), `crefresh`, `cclose`.

### 5.3 View CATEGORY (item grid)

- A "< Back" button (`cback` → HOME), the title "Farming Collections" (24), and "Page 1 / 3" (16).
- A grid of **4 columns × 3 rows = 12 cards** per page. Each card is 262×170 with Background `#142030(0.9)` and `LayoutMode: Top`:
  - `ItemIcon` 56×56 plus `TextButton #SkyyCCardN` (250×40, FontSize 18), text "Wheat  VII" (roman tier; "Wheat  -" at tier 0). Clicking it opens that collection's detail view (`ccardN`).
  - Bar 230×14, filled toward the next tier (full and gold when maxed).
  - Label 16: "1,240 / 2,500", or "MAXED".
  - Label 14 (dim): "Next: Medium Farming Bag" (the first reward of the next tier).
  - **Undiscovered:** the card shows "???" (22) and "Gather one to discover it" (14), with no icon and no button.
- **Order:** the registry's fixed order, like SkyBlock's fixed grid; undiscovered cards go last.
- **Footer:** `cprev` / `cnext` (only when there are several pages), `chome`, `cclose`.
- **Height budget:** 60 header + 3×180 + 70 footer + padding = about 700 of 840.

### 5.4 View COLLECTION (detail, the SkyBlock "per-item page")

```
[ < Back to Farming ]                                               [ Home ] [ Close ]
[icon 72]  Wheat                  (30, bold)
           Tier VII of IX         (20)       Total collected: 1,240  (18)
           [======================------------]  700 x 22     1,240 / 2,500 to Tier VIII
 ------------------------------------------------------------------------------------------
 [DONE  ]  I     50       Crude Sickle recipe - +50 coins                                   (row 44 high)
 [DONE  ]  II    100      +100 coins
 [BOUGHT]  III   250      Copper Hoe recipe - +200 coins - +500 Farming XP (paid when reached)
 [NEXT  ]  IV    500      Copper Sickle recipe - +400 coins
 [LOCKED]  V     1,000    Medium Farming Bag - +800 coins - +2,500 Farming XP
 ...  one row per tier (up to 10) ...
 From: ripe wheat, broken or F-harvested  (16, dim)
 [ Buy Tier IV unlocks - 3,600 coins ]   (only when 4.4 allows; 1st click -> "Click again within 10 s to pay 3,600 coins")
```

- **Row:** `Group` with `LayoutMode: Left`. It holds a status chip `Group` (110 wide, coloured), `Label` roman (60, 20 bold), `Label` threshold (120, 18) and `Label` rewards (660, 16, set via `b.set`).
- **Payloads:** `cback` (→ that category, same page number), `chome`, `cclose`, `cbuy`.
- A purchase result shows in a status label; the view then rebuilds.
- `/coll <name>` opens this view directly (3+ letter prefix, like `/skills` args).

### 5.5 Commands

The HANDOFF command rules are VERIFIED patterns in 0.1.4/0.1.5.

| Command | Who | What |
|---|---|---|
| `/collections` (`/coll`) `[name]` | `setPermissionGroups({"hytale:Adventurer"})` | Opens HOME, or the detail view for `name` |
| `/collections unlocks` (`recipes`) | Adventurer | Chat list of unlocked recipes (kept from 0.1.3) |
| `/collections reload` | `requirePermission("skyycollections.admin")` + `setPermissionGroups(new String[0])` | Re-reads `collections.properties`, `rewards.properties` and `config.properties` |
| `/collections give <CollId> <n>` | admin, same as above; self only | **Test helper:** credits `n` of the collection's first item through the normal credit path, source `admin` (like `/skills xp`) |
| `/collections top <CollId>`, `/collections top score` | Adventurer | Top 10 in chat. Decision 8.5 (leaderboards: TAKE) applies, so this is **in 0.2** as the minimum, designed below |

**Leaderboard design (0.2 minimum).** Copied from the working `/skills top` in SkyySkills 0.3.2 (`SkillTop.all` + `TopCmp`, VERIFIED code):
- Scan every `counts/*.properties` on disk, one row per profile key; profile N ≥ 2 shows as "name (profile N)" (SkyySkills `label()`).
- Read the files the way SkyySkills 0.3.2 does: an NIO stream under the store's IO lock (`readProps`). Its note says a plain `FileInputStream` held open on Windows makes the save's `ATOMIC_MOVE` fail (tested on the game JRE). VERIFIED code comment.
- Overlay the in-memory counts of online players (they may be newer than the file), sort by value (ties by name), cache the result 30 s per board.
- `top <CollId>` ranks by the **real count** (the sum of the member items), so bought tiers never rank. `top score` ranks by count tiers (`coll:score`, bought tiers excluded).
- Needs a `_name=<player name>` line in each counts file, written on join (3.5). SkyySkills stores `name` the same way.
- A full file scan every 30 s at most is fine for hundreds of profiles. A server with thousands would need a stored index. UNVERIFIED scale.
- A page view (a "Top 10" button on the detail view) and a HUD widget are later `[SKYY?]`.

---

## 6. Migration of saved counts

**Facts (VERIFIED, read-only):**
- The only 0.1.x data is Skyy's test file `...\Saves\HUD mod\mods\Skyy_SkyyCollections\counts\d8ddde89-98b2-4739-983e-a39773d582b6.properties`.
- Every value is under 50, so no tier was ever reached and no recipe ever unlocked:
  ```
  Furniture_Crude_Torch=1  Plant_Bush=26  Plant_Bush_Green=4  Plant_Flower_Common_White2=1  Plant_Grass_Lush_Short=1
  Plant_Grass_Sharp=26  Plant_Grass_Sharp_Short=1  Plant_Grass_Sharp_Tall=4  Plant_Grass_Sharp_Wild=4
  Rock_Stone=22  Soil_Grass=1  Soil_Gravel=5  Wood_Ash_Trunk=3  Wood_Ash_Trunk_Full=2
  ```
- `unlocks.properties` holds only the header and `auto=true`.
- An orphaned `Skyy_0.1.1 SkyyCollections/` folder exists. Leave it alone.

**Rule: convert when exact, otherwise restart.** It covers every `counts/*.properties` without `_schema=2` (all profiles).

**When it runs: in `start()`, never in `setup()`.** VERIFIED from Skyy's server log (`Saves\HUD mod\logs\2026-09-23_22-42-07_server.log`, read-only): plugin `setup()` runs in the Setup phase (SkyyCollections 0.1.4 logged "ready" there), the item, block and recipe asset stores load only after "Setup phase completed", and `start()` ("Enabled plugin ...") runs after every asset has loaded. In `setup()` every BlockType lookup below would fail and every old count would be dropped. Order:
- `setup()`: load `config.properties` and `CollReg` (plain files, no asset lookups), register the systems, commands and bridge functions.
- `start()` (a `PluginBase` lifecycle method, VERIFIED by reflection; the Skyy mods do not override it yet): run the migration, then check the recipe ids of `rewards.properties` against `CraftingRecipe.getAssetMap()`.
- Guards: a file that already has `_schema=2` is skipped, so the pass never runs twice. If `CollReg` is empty or the BlockType asset map is empty, abort the whole pass without writing anything, log it, and try again on the next start.

1. Copy the file to `counts-0.1/<same name>`. Never delete it.
2. For each old key K:
   - Look up `BlockType.getAssetMap().getAsset(BlockType.getAssetMap().getIndexOrDefault(K, -1))`. These methods are VERIFIED on `BlockTypeAssetMap`.
   - Convert **only** when the gathering has no Soft entry, no tool entries, a Breaking entry with `ItemId != null` and `DropListId == null`, and that item is in the registry. Then item += count × `Breaking.getQuantity()`.
   - Otherwise drop the key and log it to `migration-0.2.log`. That covers drop lists (random), tool-dependent blocks, "Empty" (grass gives nothing) and non-registry items.
   - A key that is already a registry item id with no block conversion is kept as-is.
3. Write the new file with `_schema=2`.
4. Rename `unlocks.properties` to `unlocks-0.1.properties` and write the new `rewards.properties` (auto rule off).

| Old key | Result for Skyy's file | Why |
|---|---|---|
| `Rock_Stone=22` | **Cobblestone +22** | Breaking `ItemId: Rock_Stone_Cobble`, quantity 1 (VERIFIED) |
| `Wood_Ash_Trunk=3`, `Wood_Ash_Trunk_Full=2` | **Ash Log +5** | `_Full` Breaking `ItemId: Wood_Ash_Trunk` (VERIFIED). The base trunk drops itself, and its id is the registry item |
| `Plant_Bush=26`, `Plant_Bush_Green=4` | dropped | Soft drop list with random rolls. It would have been about 21 fiber and 15 sticks on average, but that cannot be exact |
| `Plant_Grass_*` (36) | dropped | The `Empty` drop list: grass never gave anything |
| `Soil_Gravel=5` | dropped | Drop list, and the result depends on the tool (1-2 or 2-3) |
| `Soil_Grass=1` | dropped | Gives Soil_Dirt, which is not a collection |
| `Plant_Flower_Common_White2=1`, `Furniture_Crude_Torch=1` | dropped | Not collections (and the torch was placed) |

`config.properties` `migrate=convert|reset` (default `convert`). `reset` just archives and starts from zero.

**What players see:**
- On the first join after 0.2, one chat line per player with migrated data: "Collections now count the items you gather (fiber, sticks, logs, stone, ores, crops, mob drops). Old block counts were converted where exact; the rest start at 0."
- `/collections` shows the new pages. For Skyy: Cobblestone 22/50 and Ash Log 5/50 are discovered; everything else is "???".

---

## 7. Bridge keys

`System.getProperties().get("skyy.bridge")`. Published in `setup()`, removed in `shutdown()`. Per-player values are keyed by UUID and describe the active profile.

| Key | Value | Readers | Status |
|---|---|---|---|
| `coll:recipes:<uuid>` | `"id,id,..."`, the recipe unlocks (count tiers ∪ bought tiers, explicit table, filtered). **Same format as 0.1.3-0.1.5** | SkyySacks Collections tab, SkyyMenu tooltip | exists (VERIFIED) |
| `coll:<uuid>` | `"tiers=34,found=31,maxed=2,recipes=11,score=34"` | SkyyMenu profile tooltip, HUD | new |
| `coll:score:<uuid>` | Long total count tiers (bought tiers excluded) | future SkyBlock Level, leaderboards | new |
| `coll:last:<uuid>` | `"<CollId>|<Name>|<tier>|<count>|<next>|<millis>"` for the last collection that moved | SkyyHud "collection tracker" widget (read on the HUD's own tick; the HUD Coins widget pattern) | new |
| `coll:epoch:<uuid>` | Long, +1 on every tier change or bypass purchase | HUD/Menu refresh cue | new |
| `coll:fn:count` | `Function apply(Object[]{UUID, String collId}) -> Long` (active profile) | quests, NPCs, other mods | new |
| `coll:fn:tier` | `Function apply(Object[]{UUID, String collId}) -> Integer` (effective tier) | quest gates, Bazaar or NPC unlocks | new |
| `coll:fn:add` | `Function apply(Object[]{UUID, String itemId, Number qty, String source [, String expectKey]}) -> Boolean`. `source` must be listed in `bridge.add.sources` (default `skills:double`; `minion` added when SkyyMinions ships). Capped per call and per minute like 3.3; refused for creative, offline or unknown items; never for Bazaar or crafting | SkyySkills double-drop perk (optional follow-up: SkyBlock counts extra drops), SkyyMinions (decision 3.7 "minion items count") | new |
| `coll:list` | `"Wheat:Farming,Carrot:Farming,...,OakLog:Foraging,..."` (registry order) | SkyyMenu, HUD settings | new |

**Profile keys read (contract):** `profile:fn:key`, `profile:epoch:<uuid>`. **Keys called:** `coins:fn:add`, `coins:fn:take`, `bazaar:buy:<itemId>`, `skill:fn:addxp`. Each is optional; a missing key means that reward or feature is skipped or owed. The zero-dependency rule holds.

---

## 8. In-game test checklist for Skyy

Setup: deploy SkyyCollections 0.2 with the rest of the set. Watch the first join in the server log for `[SkyyCollections]` warnings, the migration lines and "already registered".

- [ ] **T1 Migration:** `/coll` → HOME shows 4 category cards and a grey Fishing line. Mining shows Cobblestone 22/50; Foraging shows Ash Log 5/50; everything else is "???". `counts-0.1/` exists in the data folder.
- [ ] **T2 Bushes:** break 20 bushes by hand. Plant Fiber rises by about 14 and Stick by about 10. "Plant Bush" never appears. The first fiber gives the chat line "New collection: Plant Fiber!".
- [ ] **T3 Grass:** break 20 grass blocks. Nothing changes.
- [ ] **T4 Shears:** break bushes with shears. The bush block drops and no collection changes.
- [ ] **T5 Logs:** chop an oak tree. Oak Log rises by exactly the number of logs picked up. Chop a birch → a separate Birch Log card.
- [ ] **T6 Stone and ore:** mine 10 stone → Cobblestone +10. Mine a copper vein → Copper Ore +1 **and** Cobblestone +1 per block. Gravel by hand → Rubble +1-2 each; with a pickaxe → +2-3 each.
- [ ] **T7 Placed blocks:** place 5 oak logs and 5 cobble, then break them. No change. Place a bush, then break it. No change (the bush drops itself).
- [ ] **T8 Creative:** in creative, break stone. No change.
- [ ] **T9 F-harvest:** F-harvest ripe wheat. Wheat, Seeds and Essence of Life rise by **exactly** what went into the inventory. If nothing happens, H3 does not fire, so switch to the HarvestTask fallback (3.1). F-harvest a berry bush → Wild Berries.
- [ ] **T10 Break ripe or unripe:** break ripe wheat by hand → it counts (may differ by 1 from the ground drops). Break unripe wheat → Seeds only.
- [ ] **T11 Loose pickups:** F-pick loose rubble or a mushroom → +1, counted once (not twice). Place a mushroom, then F-pick it → no change.
- [ ] **T12 Kills:** kill a chicken → Raw Chicken + Light Hide rise. Kill a skeleton → Bone Fragments + Linen Scraps.
- [ ] **T13 Does not count:** buy 64 cobble on the Bazaar, craft copper bars in /craft, drop and pick up items, let the bags sweep items, withdraw from a bag. No collection changes. Shear a tamed sheep: no change either (known 0.2 gap, 2.5).
- [ ] **T14 Tier I:** `/collections give Wheat 50` (admin), or gather for real. You get the gold "COLLECTION UP Wheat I" line and +50 coins, and the Crude Sickle shows in /craft → Collections and crafts there without a Farming Bench. Then `/collections give Cobblestone 500` and craft Stone Brick from the Collections tab (a `StructuralCrafting` recipe, 4.3).
- [ ] **T15 Skill XP:** at tier III you get "+500 Farming XP" if SkyySkills allows gathering skills in `bridge.addxp.skills`. Otherwise the log says it is owed and it pays after that change.
- [ ] **T16 Page flow:** Farming card → grid (big text, icons, bars) → click Wheat → tier list with DONE/NEXT/LOCKED colours → Back → the same grid page → Home → Close. Click fast many times: every click responds and nothing sticks on Loading. Open it from the SkyWynn Menu too; if that hangs, it is the known SkyyMenu bug, not this page.
- [ ] **T17 Coin-bypass (tests SkyyCollections 0.2's older walls, not the 2026-09-24 tiered lock):** with 5,000 coins and Iron at 30, click "Buy Tier II unlocks" once (confirm text), then again. Coins drop by the price, the tier shows BOUGHT, and Iron stays at 30. No coins or XP are paid for that tier until 100 are really gathered. On 0.2 you cannot buy past the shipped wall (Standard IV). The 2026-09-24 rule (early + first half of mid game, then no buy and no sell) is not what this test checks, and it is not built.
- [ ] **T18 Persistence:** restart the server. Counts, paid tiers and bought tiers remain.
- [ ] **T19 Profiles** (once SkyyProfiles is deployed): switch profile. Counts belong to the new profile, and /craft → Collections follows within about 1 s.
- [ ] **T20 Two players:** each has their own counts; A's breaks never move B's page.

---

## Appendix A: build notes (0.1.5 → 0.2)

- **Keep:** `CollStore.pkey/countsKey/save/flushDirty`, `CollUnlocks.publish/syncEpoch/recheck/checkEpochs`, `CollRecheck`, `CollSaver`, the commands' permission setup. All VERIFIED code in 0.1.5.
- **Replace:** `CollSystem` becomes H1-H5 plus `GatherCtx`; `CollStore.bump(u, blockId, 1)` becomes `CollStore.addItem(pkey, itemId, qty)`, which returns the tier crossings for that item's collection; `TIERS` becomes per-curve arrays; `CollUnlocks.compute` becomes the explicit table plus bought tiers (auto opt-in); `CollPage` gets 3 views.
- **Lifecycle:** `setup()` = config, `CollReg`, systems, commands, bridge functions. `start()` = migration + recipe-id check. Nothing that reads an asset map (BlockType, Item, CraftingRecipe) runs in `setup()`, because those maps are still empty then (section 6, VERIFIED server log).
- **Add:** `CollReg` (registry from `collections.properties`, written with the section 2 defaults on first run: `coll.<Id>=<Category>|<Curve>|<Name>|<IconItem>|<itemId,itemId,...>`, plus `hidden`/`nobypass` flags), `CollDrops`, `PlacedStore` (copied), `CollRewards` (owed-and-retry payments), `CollBypass`, and the bridge Functions (`CollCountFn`, `CollTierFn`, `CollAddFn`).
- **javassist rules** (HANDOFF toolchain): no lambdas, generics, enhanced-for, inner classes or String-switch; methods added in dependency order; `DeathSystems$OnDeathSystem` and `UseBlockEvent$Post` use the `$` names as SkyySkills does. Probe every engine method at build time with `B.probe`: `InteractivelyPickupItemEvent.getItemStack`, `BlockHarvestUtils.getDrops`, `BlockHarvestUtils.shouldPickupByInteraction`, `BlockGathering.getToolData`, `BlockGathering$BlockToolData.getStateId`, `Role.getDropListId`, `ItemModule.getRandomItemDrops`, `BlockTypeAssetMap.getIndexOrDefault`.

## Appendix B: open points for Skyy `[SKYY?]`

1. 33 separate log collections (as asked) with the undiscovered ones hidden: OK? Which woods are "Rare"?
2. Rock grouping (Cobblestone, Sandstone ×3 colours, Shale, Slate, Basalt, Volcanic, Marble, Quartzite, Limestone), and Dirt not being a collection.
3. The curve thresholds, the coin table and the skill XP lumps. Combat paying double coins instead of XP.
4. Boom Powder and Wool in Combat (matching the bags) or in Farming.
5. Coin-bypass. The 0.2 walls (Bulk V / Standard IV / Rare III / Elite none) and the ×5 Bazaar price are what shipped. The 2026-09-24 lock replaces the wall with a tiered cutoff (early game + first half of mid game, then no buy and no sell) plus level requirements on many items. Later the same day, every **gear** item got a level requirement (`SkyyGear-Plan.md`). Exact cutoff per collection/tier, and skill vs class vs combat level, are open. Do not retune 0.2 from this line until those are answered.
6. Whether the SkyySkills double drops count (via `coll:fn:add`, the SkyBlock-like choice).
7. Classless kills count: yes by default.
8. SkyySacks follow-up: Medium/Large bags only through collections.
9. SkyySkills follow-up: allow `Mining,Foraging,Farming` in `bridge.addxp.skills`.
10. Shearing and plucking tamed livestock not counted in 0.2 (2.5 gap note): accept, or add a hook later?
11. 0.2 recipe-unlock scope (4.3): about 90 collections with no recipe reward yet; take the proposed ore line?
12. The ×2 Combat coin multiplier (4.2).

## Sources

- Hypixel SkyBlock Wiki (Minecraft Wiki mirror): [Collections](https://hypixelskyblock.minecraft.wiki/w/Collections), [Wheat](https://hypixelskyblock.minecraft.wiki/w/Wheat), [Cobblestone](https://hypixelskyblock.minecraft.wiki/w/Cobblestone), [Co-op](https://hypixelskyblock.minecraft.wiki/w/Co-op) (all re-fetched 2026-09-23); [Oak Log](https://hypixelskyblock.minecraft.wiki/w/Oak_Log), [Iron Ingot](https://hypixelskyblock.minecraft.wiki/w/Iron_Ingot) (from the research notes).
- Hypixel forums: [bazaar purchases](https://hypixel.net/threads/does-buying-resources-from-bazaar-count-towards-collection.2957095/), [pickup required](https://hypixel.net/threads/do-i-need-to-pick-up-items-for-them-to-count-on-collections.5560065/), [minion enchanted items](https://hypixel.net/threads/does-collecting-enchanted-items-from-minions-count-towards-your-collection.2998462/), [sacks](https://hypixel.net/threads/do-items-count-for-collection-when-they-go-into-your-sack.3036097/) (informal answers only, UNVERIFIED).
- **Jar** (tools/dev reflect.py / bc.py / bcfull.py / callers.py): `BlockHarvestUtils.damageSingleBlock`, `performBlockDamage`, `performPickupByInteraction`, `shouldPickupByInteraction`, `getDrops`, `spawnDrops`; `BlockGathering.isHarvestable`; `BreakBlockInteraction.interactWithBlock` (fields `toolId`, `matchTool`, `harvest`); `FarmingUtil.giveDrops`; `ItemUtils.interactivelyPickupItem`; `BlockPlaceUtils.tryPlaceBlock` → `BlockPhysics.markDeco`; `BlockPhysics.isDeco`; `Role.getDropListId`; `ItemModule.getRandomItemDrops`; `NPCEntity.getRole`; `BlockTypeAssetMap.getIndexOrDefault/getAsset(int)`; `BlockHarvestUtils` modifiers by reflection (`spawnDrops` private static); `BuilderCodec.inherit/readAndInheritEntry/readAndInheritField`; `ActionDropItem.execute` → `ItemUtils.throwItem`; `PluginBase.setup/start`.
- **Assets.zip** (read in memory): `Server/Item/Items/**` (Gathering, `Parent` merge, `Recipe` lists), `Server/Drops/**`, `Server/NPC/Roles/**`, `Server/Item/Interactions/Weapons/{Pickaxe,Shears}/Attacks/*_Block_Break.json`, `Server/Item/Interactions/Weapons/Hatchet/Attacks/Chop/Scraper_Chop.json`, `Server/Item/Items/Tool/Hatchet/Tool_Bark_Scraper.json`, `Server/Item/Items/Wood/Oak/Wood_Oak_Trunk.json` (Tools + `Stripped` state), `Server/NPC/Roles/Creature/Livestock/Tamed/*.json` + `Sheep.json`, `Server/Drops/NPCs/Livestock/*_Harvest.json`, every `BenchRequirement` (Type/Id census), `Server/Languages/en-US/server.lang`.
- **Our code and data:** `SkyyCollections/build_skyycollections_0.1.5.py`, `SkyySkills/build_skyyskills_0.3.2.py`, `SkyySacks/build_skyysacks_0.7.2.py`, `SkyyMenu/build_skyymenu_0.1.1.py`, `SkyyBazaar/build_skyybazaar_0.1.1.py`, `SkyyCoins/build_skyycoins_0.1.5.py`, `research/Alchemy-Skill-Spec.md`, `tools/PROFILES-CONTRACT.md`, `HANDOFF.md`, `SkyWynn-Decisions.md`, `SkyWynn-Master-Plan.md`, `SkyWynn-Mod-Roster.md`, `SkyySacks-Plan.md`. Skyy's save (`Skyy_SkyyCollections/counts/*.properties`, `unlocks.properties`, `Skyy_SkyySacks/crafts.log`, `logs/2026-09-23_22-42-07_server.log`), read-only. Also `SkyySacks/build_skyysacks_0.6.8.py` (old type check), `SkyySkills/build_skyyskills_0.3.2.py` (`SkillTop`), `SkyWynn-Decisions.md` row 8.5.
