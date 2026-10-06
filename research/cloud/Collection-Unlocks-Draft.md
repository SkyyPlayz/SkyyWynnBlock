# Collection unlocks - draft (Mining, Foraging, Farming)

Cloud draft, 2026-10-06. Ties the tier ladder (`Gathering-Tiers-Draft.md`) to collection levels, SkyBlock style (`SkyBlock-Gathering-Progression.md`). Existing rules kept: **R3 - coins never skip collections, tiers, recipes or bags**;
items from player-placed blocks, the Bazaar, trades, bag withdrawals never count; compressed (Enchanted) items count as their base amount; every accessory tier / bag size is crafted FROM the previous one (LOCKED 2026-10-03).
Data from `research/Collections-Spec.md` (curves B / S / R / E, current reward shape: coins + skill XP lump + score + recipe unlocks) and `SkyyCollections/build_skyycollections_0.2.6.py` (the 159 registry ids).
All thresholds and rewards are proposals for Skyy; all item names are working names; recipe ids UNVERIFIED.
Reconciled 2026-10-06, see research/cloud/Gathering-Numbers-Reconciled.md (sections 0, 2, 3, 4, 6: Fortune ladder, Feller rewards dropped, Haste accessory relabelled Prospector).

## 0. The unlock grammar (the same for every key collection)

| Collection tier | What it unlocks (the pattern) | SkyBlock equivalent |
|---|---|---|
| **I** | the **Pocket Shard** (minion) recipe for this material (T I) + coins | minion at tier I |
| **II** | a **skill XP lump** (+ a small Fortune-free coin bonus as today) | XP / first armor |
| **III** | **bag or storage** (only on the bag-key collections) or the **previous tier's tool upgrade** (see gate rows) | portal / small storage |
| **IV** | **the next tier's gathering tool(s)** - THE GATE (pickaxe + shovel / hatchet / hoe + sickle) | axe / pickaxe recipe |
| **V** | the **Enchanted (compressed) recipe** for this material (160 base -> 1 Enchanted; Enchanted Block later) | Enchanted X recipe |
| **VI** | the **gathering armor set** for this tier (Foraging first; Mining / Farming later) | armor |
| **VII** | **Pocket Shard upgrades / accessory** (compactor chain, Prospector / lantern accessories) | compactors, talismans |
| **VIII** | a bigger **skill XP lump** | +10k XP |
| **IX** | the **capstone**: Super-compactor / Enchanted Block / a **small permanent Fortune** perk | Super Compactor, large sack |
Shorter curves compress the same idea: **R (8 tiers)** drops the VII row (merge into VIII), **E (7 tiers)** moves the gate to III and the Enchanted recipe to IV.

### 0.1 Curve thresholds (from the Collections spec)
| Curve | Tiers | Thresholds (total items) |
|---|---|---|
| B Bulk | 10 | 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 / 10,000 / 25,000 / 50,000 |
| S Standard | 9 | 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 / 10,000 / 20,000 |
| R Rare | 8 | 25 / 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 |
| E Elite | 7 | 10 / 25 / 50 / 100 / 250 / 500 / 1,000 |

### 0.2 The gate rule (the anti-skip rule)
**Tier N+1's tools are crafted from tier N+1's ingots / wood / ... but their RECIPE appears only when the tier-N key collection reaches its gate tier** (S/R: IV, E: III). You cannot buy the recipe (R3), and the material itself is behind the previous tool's breaking Quality, so a player always passes through the previous tier first.

## 1. MINING

Key collections: Cobblestone (B), Copper (S), Iron (S), Thorium (R), Cobalt (R), Adamantite (E), Mithril (E). Mining pickaxes also unlock their **shovel** for soils / stone.

| Collection | Curve | I | II | III | IV | V | VI | VII | VIII | IX / X |
|---|---|---|---|---|---|---|---|---|---|---|
| **Cobblestone** (+ the S1 stone group) | B 10 tiers | Cobblestone Pocket Shard | +500 Mining XP | **Copper pickaxe + shovel** (T1 tools) | Enchanted Cobblestone | Compactor (Pocket Shard upgrade: compresses to blocks) | +1,000 Mining XP | Prospector accessory recipe (Rare, Fortune +3) | Prospector accessory recipe (Legendary, Fortune +6) | **X: Super Compactor** (to Enchanted form) |
| **Copper Ore** | S 9 | Copper Pocket Shard | +400 XP | Smelter recipe tip (the Mining bag key is Iron, not Copper) | **Iron pickaxe + shovel** | Enchanted Copper | Mining gear T1 (Copper-trimmed Miner's set, later idea) | Auto-Smelter upgrade | +2,000 XP | **IX: Enchanted Copper Block** + Mining Fortune +1 |
| **Iron Ore / Ingot** | S 9 | Iron Pocket Shard; **Mining Bag (Normal)** (existing bag key, tiers I / III / V / VII) | +600 XP | Mining Bag (Unique) | **Thorium pickaxe + shovel** | Enchanted Iron; Mining Bag (Rare) at V | Mining gear T2 | Mining Bag (Legendary); Storage upgrade | +3,000 XP | Enchanted Iron Block + Fortune +1 |
| **Thorium Ore** | R 8 | Thorium Pocket Shard | +800 XP | Thorium Compactor chain tier | **Cobalt pickaxe + shovel** | Enchanted Thorium | Mining gear T3 | - | +4,000 XP | Enchanted Thorium Block + Fortune +1.5 |
| **Cobalt Ore** | R 8 | Cobalt Pocket Shard | +1,000 XP | - | **Adamantite pickaxe + shovel** | Enchanted Cobalt | Mining gear T4 | - | +5,000 XP | Enchanted Cobalt Block + Fortune +2 |
| **Adamantite Ore** | E 7 | Adamantite Pocket Shard | +1,500 XP | **Mithril pickaxe + shovel** (gate III) | Enchanted Adamantite | Mining gear T5 | - | - | - | VII: Enchanted Block + Fortune +2 |
| **Mithril Ore** | E 7 | Mithril Pocket Shard | +2,000 XP | **Onyxium pickaxe** (once Onyxium exists; placeholder) | Enchanted Mithril | Mining gear T6 | - | - | - | VII: Enchanted Block + Fortune +2.5 |
Stone groups: **S1 (Cobblestone, Sand, Rubble, Clay, Sandstone)**, **S2 (Shale, Slate, Limestone, Marble, Quartzite, Salt)**, **S3 (Basalt, Volcanic, Ice)** each share the same simple pattern: I Pocket Shard, II XP, IV Enchanted form of the key stone, VI a building recipe pack (new blocks), IX XP lump. Crystals and Gemstones (E/R): I Pocket Shard, III Crystal Lantern / gem accessories (Accessory-Table), later magic-weapon upgrades.

## 2. FORAGING

Key collections: Oak (B), Birch (S), Maple (S, F2), Redwood (R, F3), Azure (R, F4), Frostwood or Crystalwood (R, F5), Tree Sap (S), Plant Fiber (B), Stick (B). The nine other common logs follow the common-log pattern.

| Collection | Curve | I | II | III | IV | V | VI | VII | VIII | IX / X |
|---|---|---|---|---|---|---|---|---|---|---|
| **Oak Log** | B 10 | Oak Pocket Shard; **Foraging Bag (Normal)** | +400 Foraging XP | Foraging Bag (Unique) | **Copper hatchet** (T1) | Enchanted Oak | **Wood armor -> Softwood armor set** | Foraging Bag (Rare) | +2,000 XP | **X: Foraging Bag (Legendary)** + Fortune +1 |
| **Birch Log** | S 9 | Birch Pocket Shard | +500 XP | Wood-tool upgrades pack | **Iron hatchet** | Enchanted Birch | **Lightwood armor set** | free slot (e.g. a Foraging XP lump or a Foraging Bag step; Skyy picks) | +2,500 XP | IX: Enchanted Birch Block + Fortune +1 |
| **Maple Log** (F2 key) | S 9 | Maple Pocket Shard | +600 XP | Maple tool handles | **Thorium hatchet** | Enchanted Maple | **Hardwood armor set** | free slot (e.g. a Foraging XP lump or a Foraging Bag step; Skyy picks) | +3,000 XP | Enchanted Block + Fortune +1.5 |
| **Redwood Log** (F3 key) | R 8 | Redwood Pocket Shard | +800 XP | - | **Cobalt hatchet** | Enchanted Redwood | **Drywood / Darkwood armor set** | - | +4,000 XP | Enchanted Block + Fortune +2 |
| **Azure Log** (F4 key) | R 8 | Azure Pocket Shard | +1,000 XP | - | **Adamantite hatchet** | Enchanted Azure | **Darkwood armor set** | - | +5,000 XP | Enchanted Block + Fortune +2 |
| **Frostwood / Crystalwood** (F5 key) | R 8 | Pocket Shard | +1,200 XP | - | **Mithril hatchet** | Enchanted | **Redwood -> Goldenwood armor set** | - | +6,000 XP | Enchanted Block + Fortune +2.5 |
| **Tree Sap** | S 9 | Sap Pocket Shard | +400 XP | **Lantern (Normal)** recipe | Sap crafts: Resin | Lantern (Unique) at V | - | **Lantern (Rare)** at VII | +2,500 XP | **IX: Lantern (Legendary)** (LOCKED 2026-10-05; tiers proposed here) |
| **Plant Fiber, Stick** | B 10 | Pocket Shards | +300 XP | Crude armor pieces / rope (the Crude set uses fibre + sticks) | Enchanted Fiber | rope / bridge-repair kits | - | - | +1,500 XP | - |

## 3. FARMING

Key collections: Wheat (S), Carrot (S), Corn (S), Pumpkin (S), Tomato (S), Cotton (S), Rice (S), Potato (S), Seeds (B), plus Wild Berries, Apple, Mushroom, Cactus.

| Collection | Curve | I | II | III | IV | V | VI | VII | VIII | IX |
|---|---|---|---|---|---|---|---|---|---|---|
| **Wheat** | S 9 | Wheat Pocket Shard; **Farming Bag (Normal)** | +400 Farming XP | Farming Bag (Unique) | **Copper hoe + sickle** | Enchanted Wheat (Hay Bale); Bag (Rare) at V | Farm armor T1 (later idea) | Farming Bag (Legendary) | +2,500 XP | Enchanted Hay Bale + Fortune +1 |
| **Carrot** | S 9 | Pocket Shard | +400 XP | - | **Iron hoe + sickle** | Enchanted Carrot | - | Seed recipes B (unlock crop group B seeds) | +2,500 XP | Enchanted Block + Fortune +1 |
| **Corn** | S 9 | Pocket Shard | +500 XP | - | seed recipes for group C (Chilli, Tomato, Cotton, Rice) | Enchanted Corn | - | Thorium hoe + sickle | +3,000 XP | Fortune +1.5 |
| **Pumpkin** | S 9 | Pocket Shard | +500 XP | - | **Cobalt hoe + sickle** | Enchanted Pumpkin | Farm armor T2 | Seed recipes group D | +3,000 XP | Fortune +2 |
| **Tomato, Cotton, Rice** | S 9 | Pocket Shard | +600 XP | Cooking recipes (SkyyCooking hook) | **Adamantite hoe + sickle** (Cotton) | Enchanted forms | Farm armor T3 | Eternal seed I recipe | +3,500 XP | Fortune +2 |
| **Potato, Onion** | S 9 | Pocket Shard | +600 XP | Cooking recipes | **Mithril hoe + sickle** (Potato) | Enchanted | Farm armor T4 | Eternal seed II / III recipes | +4,000 XP | Fortune +2.5 |
| **Seeds** | B 10 | Seed Pocket Shard | +300 XP | - | Seed pouch / larger seed stacks | - | - | - | - | - |
Crops that are **ingredients** for food (Cooking collections) still unlock Cooking recipes: pair these rows with SkyyCooking's recipe knowledge so a crop collection also teaches a dish.

## 4. Fortune perks - one number so it stays small (optional)

Skyy asked for fortune and speed on the ladder. Proposal: each **maxed key collection** (top tier) adds a small permanent **Fortune** of its skill (Mining / Foraging / Farming): +1 / +1 / +1.5 / +2 / +2 / +2.5 for the tier 1..6 key collections, **10 per skill at the end, the same ladder for all three skills** (`coll.fortune.cap` 10). Tools and armor add more (tool level, set bonus), so collections only nudge. Fortune budget: the per-source caps of `research/cloud/Gathering-Numbers-Reconciled.md` 1.1 (tool 25, armor 15, accessories 10, pets 10, collections 10) under the global 100.

## 5. Counting rules (kept)

| Rule | Detail |
|---|---|
| What counts | items you receive from breaking / harvesting / killing yourself, and from **your own Pocket Shards when you collect them** (Pocket-Shards-Spec) |
| Enchanted items | count as their base amount (160 each); an Enchanted Block (160 Enchanted) counts as 160 x 160 = 25,600 base (SkyBlock behaviour; see `Enchanted-Materials-Draft.md`) |
| Not counted | Bazaar / AH / NPC / trade / bag withdrawals / admin gives / player-placed blocks |
| Coins | never buy a tier or a recipe (R3) |

## 6. Rewards that need other mods (flag)
| Reward | Needs |
|---|---|
| Pocket Shards recipes | SkyyMinions / Pocket Shards (not built) |
| Gathering armor | SkyyGear 0.2.x armor stats + SkyyArmory-style art (Foraging armor LOCKED, Mining / Farming later) |
| Tool recipes | SkyyGear tool levels round (gate by Mining / Foraging / Farming level) |
| Enchanted items | Enchanted-Materials-Draft (new items, bench) |
| Cooking recipe unlocks | SkyyCooking recipe-knowledge hook |
| Fortune perks | SkyySkills / SkyyGear stat `mfort` `ffort` `farmfort` (Stats page) |
| Accessories (Prospector, Lantern) | SkyyAccessories lines + the Accessory Table |

## 7. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | The collection reward system today: only recipe unlocks through `coll:recipes:<uuid>`; extending it to **tool recipes, armor recipes and perks** is a SkyyCollections change; coins/XP already exist. |
| 2 | Which recipes already exist as vanilla items (Copper / Iron / ... tools, Wood armor, the Farming Bench woods) vs which are ours (Enchanted, Pocket Shards, Lantern). |
| 3 | The tool recipe gate mechanism: the Workbench recipe lists must hide / lock a recipe until its collection tier is reached (the bag recipes already do this - SkyySacks reads `coll:recipes`). |
| 4 | The existing bag-key unlocks (Mining = Iron, Foraging = Oak, Farming = Wheat; tiers I / III / V / VII) are used as is; check they do not collide with the tool gates above. |
| 5 | Thresholds vs real gathering rates (the Collections spec assumed 1 item per action); with Pocket Shards and double drops the totals may fall faster. |

## 8. Questions for Skyy
1. Is the **gate tier (IV)** for "next tool" right, or earlier (III) so the climb is quicker?
2. Pocket Shard at tier I for every collection: all 159, or only the 30 launch types (Pocket-Shards-Spec)?
3. Do you want the small Fortune perks from collections (section 4) or keep Fortune only on tools / armor / accessories?
