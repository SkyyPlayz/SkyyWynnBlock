# Farming + food mods survey (2026-10-18)

Skyy's words are in `docs/answered/project.md` (last lines, 2026-10-18) and the Glymera line from the main session. Four mods, read only
(jars unzipped into scratch, deleted after). Licences: CurseForge pages fetched 2026-10-18 (the licence field only; the linked licence
page text was not readable).

## Summary

| Mod | Licence | Verdict |
|---|---|---|
| _Connor's_ More Food Stuff V0.1 (WonderBoots) | not found (CurseForge page not found by search or URL guess) = treat as All Rights Reserved | DO NOT PACK YET. It needs Food_Instant_Heal_T2/T3 effects that the current Assets.zip no longer has. Re-check when the author updates; meanwhile build the few dishes we like ourselves into SkyyCooking |
| Farming Overhaul 2.4.0 (Krynnx) | All Rights Reserved | REFERENCE ONLY. Notes below |
| Advanced Farming 1.3.1 (Counter / Thecounters03) | All Rights Reserved (CurseForge field) | CANNOT FOLD. Build our own Infinite Water Bucket (spec below) |
| GlymeraFarmer 13.0.0 + GlymeraIrrigation 10.0.0 (GlymeraCraft) | page says "All Rights Reserved" AND "Free for personal and server use. No attribution required." | REFERENCE ONLY for the farming totems. Do not fold; ask GlymeraCraft if we ever want code |

## 1. More Food Stuff (_Connor_ / WonderBoots)

Jar: manifest only says Group `_Connor_`, Name `More Food Stuff`, Version 1.0.0 (file name V0.1), no licence file, no Java (assets only).
13 items (all `Parent: Template_Food`, vanilla eat chain `Root_Secondary_Consume_Food_T1/T2/T3`, vanilla models, own textures):

| Id | Recipe (all at `Cookingbench`) | Tier / quality |
|---|---|---|
| `Food_Bread_Slices` | 1 `Food_Bread` -> 6 (Prepared, 2 s) | T1 Common |
| `Food_Butter` | 1 `Ingredient_Salt` + 1 Milk_Bucket resource (Prepared, 2 s) | T1 Common |
| `Food_Drink_Apple` | `Deco_Tankard` + `Plant_Fruit_Apple` -> 3 (Prepared) | T2 Uncommon |
| `Food_Drink_Berry` | `Deco_Tankard` + `Plant_Fruit_Berries_Red` -> 3 | T2 |
| `Food_Drink_Mango` | `Deco_Tankard` + `Plant_Fruit_Mango` -> 3 | T2 |
| `Food_Drink_Milk` | `Deco_Tankard` + Milk_Bucket -> 5 | T2 |
| `Food_Drink_Berry_Shake` | Tankard + Red Berries + Milk_Bucket -> 5 | T2 |
| `Food_Drink_Coconut_Milk` | Tankard + `Plant_Fruit_Coconut` + Milk_Bucket -> 5 | T2 |
| `Food_Salad_Corn` | `Plant_Crop_Lettuce_Item` + `Plant_Crop_Corn_Item` (Prepared, 1 s) | T2 |
| `Food_Pie_Berry` | Dough + 4 Red Berries + Spices + 3 Fuel (Baked, 5 s) | T3 Rare |
| `Food_Mango_Pie` (lang key `Food_Pie_Mango`) | Dough + Mango + Spices + 3 Fuel | T3 Rare |
| `Food_Pie_Azure` | Dough + `Plant_Fruit_Azure` + Spices + 3 Fuel | T3 Rare |
| `Food_Pie_Pink_Berry` | Dough + 4 `Plant_Fruit_Pinkberry` + Spices + 3 Fuel; also `Potion_Health_Instant_Greater` (40% heal) | T3 Legendary |

Findings:
- **It will not load clean on the current game.** Its items use `Food_Instant_Heal_T2`, `Food_Instant_Heal_T3` (effects). The cached
  current Assets.zip (tools/dev/scratch/serverjar/assets-3942760463-...) only has `Food_Instant_Heal_T1`; the vanilla dishes now use
  an inline `Consume_Charge` + `Effect` var. This is the same 0.7 change that stopped SkyyCooking 0.1.7 (log 2026-10-14). Expect an
  asset-validation error or dishes that heal nothing. Not tested on a smoke server (that needs the game closed + a scratch world copy).
- Sloppy bits: Berry Juice reuses the Apple icon, Milk reuses the Shake icon; descriptions are hand-typed ("Health Regen II", "2:30")
  and not tied to the real numbers.
- **Clashes with our food:**
  - SkyyCooking (FP1 done): grades a fixed list (15 vanilla dishes + 11 own: pies, salads, kebabs, bread, popcorn ...) as
    `Skyy_Cook_Food_<Dish>_G1..G12`. Connor's dishes are NOT in that list: they stay plain, never graded, pay Cooking XP only through
    the generic rule (`cook.xp.default=10`, log names it once), and their vanilla buff chains do not know our graded buffs (documented
    limit in the Cooking spec). Its `Food_Pie_*` ids do not match ours (`Food_Pie_Apple`, `_Meat`, `_Pumpkin`): no id clash.
  - Food Pouch (Flask-Pouch-Spec): loaded ids exist only for SkyyCooking's own list; pack-mod foods are left out on purpose ("PACK rules
    forbid copying their numbers"; FP2 = "pack-mod foods with their authors' OK"). So Connor's foods never go in the Pouch.
  - Farming collections / Bazaar: `Food_*` ids go to the Farming sack (`catOf`). Collections only list products SkyyCollections names;
    Bazaar lists only ids in `products.properties` (checked against the live asset map). Nothing auto-lists Connor's ids, nothing clashes.
  - `More Foods.zip` (Mods folder): overrides vanilla `Food_Beef/Chicken/Pork/Wildmeat_*` and adds T20/T50 effects; no id overlap with
    Connor's. (More Foods is not listed in PACK.md - the grep found no row; out of scope here, noted.)
- **Duplicates (rule 2):** Connor's Apple Pie = none (his pies are Berry/Mango/Azure/Pink Berry), but "Milk", "Butter", "Bread
  Slices", "Corn Salad" are new things; our SkyyCooking has Bread / Cheese / salads. Nothing is the same dish. Drinks are the only new
  family (Tankard + fruit). Best-of: keep ours for anything both have; none overlap today.

Recommendation: **not packed now** (no licence we can see, broken effect ids on 0.7). When Connor posts a build for the current game:
(1) read the licence; if All Rights Reserved, ask in the CurseForge comments / author's page for modpack permission (Aures-style);
(2) smoke test it; (3) if packed, react by id at runtime only: add the 13 ids to `products.properties` as Bazaar commodities (Farming
sack already takes `Food_*`), add `cook.xp.<id>` lines in `xp.properties` (suggest pies 60, drinks 30, salad 25, butter/bread 15 -
Skyy decides), and optionally let SkyyCooking grade them (needs the author's OK: grading copies their numbers). If not packed: our own
Tankard drinks + a Butter item as SkyyCooking dishes are cheap (vanilla assets only).

## 2. Farming Overhaul 2.4.0 (Krynnx) - reference only

Almost all JSON. Java is two classes: `org.Krynnx.Overhaul` (listens to `LoadAssetEvent`, rewrites the seed-drop weights of 14 crops'
`ItemDropList` by reflection from `config.json`) and `FarmingConfig`. Nothing about AoE is in Java.

- **AoE tilling** (`Hoe_Till_Heavy`, secondary of `Tool_Hoe_Heavy`): a `Condition` on `Crouching`. Crouching = single block
  `ChangeBlock` (vanilla). Not crouching (`Failed`) = `Selector` with `Id: AOECircle`, `Range: 2`, `Offset Z -2`, a `Filter` of type
  `Block` listing the 16 `Soil_*` ids; `HitBlock` runs `ChangeBlock` with the `Changes` map (every `Soil_*` -> `Soil_Dirt_Tilled`),
  `RequireNotBroken`, then `ModifyInventory AdjustHeldItemDurability -1` per block, plus a `Cooldown` id `KrynnxHeavy`. "Tillable" =
  being a key of the `Changes` map; ChangeBlock does nothing to any other block.
- **AoE watering** (`Watering_Can_Use_Charge`): `Charging` with `Next` {"0": `Watering_Can_Use`, "0.15": `Watering_Can_Use_3x3`} - hold
  longer = bigger. The AF can (below) is the cleaner example: `UseWateringCan` inside a `Selector` `AOECylinder` (Range 3/5/7/9, Height 1,
  Offset Y -1), `RefreshModifiers: ["Water"]`, `Duration 86400`, `RunTime 0.2`, `CancelOnItemChange`.
- **Sickle area harvest** (`Sickle_Swing_Left/Right` + `_Selector` + `_Effect`): `Selector` `Horizontal`, `ToLeft`/`ToRight`,
  `EndDistance 4.0`, `Length 40`, `ExtendTop/Bottom 0.5`, `TestLineOfSight false`; `HitBlock` = `HarvestCrop` (`RequireNotBroken`), `Failed` =
  `Block_Break_Adventure`, `Next` = durability -1. "Grown" is decided by the engine's `HarvestCrop` (only a final-stage crop yields;
  otherwise it fails and the fallback breaks the plant). Their "fix" is a quick animation + chaining (`Sickle_Attack` = `Chaining`
  ChainingAllowance 1.25 of left then right) so holding the button repeats.

Compared with ours (SkyyGear 0.3.27): our can is the code path `GearCan.before/after` + `GearCanWater` (subclass of
`UseWateringCanInteraction`, squares 1/3/5/7/9/11, `cells()` picks the soil, hold-and-sweep via a `LAST` map and `can.holdSec`, water bar =
item durability, never below 0.001). Our hoe reads vanilla's `Hoe_Till` `Changes` map from Assets.zip at build time (`TILL_FROM`, better
than their hand-typed list: survives a game update). Our Harvester uses `SkyyGearHarvest` (HarvestCrop + tier rule).

Anything of theirs that would fix a weak spot of ours:
1. **Empty can as its own item.** Their cans are an Empty item and a `Filled_Water` state; at 0 durability `ModifyInventory
   BrokenItem: <empty can>` swaps the item. Ours keeps one item and holds durability at 0.001 because "a 0-durability tool may count as
   broken to the client" (UNVERIFIED, fix round note). If that ever shows (greyed can, can't click to refill), the swap is the proven
   fix; also gives a different empty model/icon. Cost: lifelong-can metadata must move across the swap (our can carries per-profile
   data), so only do it if the bug shows.
2. **Refill via vanilla `RefillContainer`** (`Watering_Can_Fill`, `AllowedFluids Water_Source, Water`, `States.Filled_Water`). Ours uses a
   hand-made 0.25-block raycast `water()`. If refilling from the island pond fails (the 0.5.20 note says "the watering can filling from
   it" is UNVERIFIED in game), compare with vanilla's fill raycast; theirs simply reuses it.
3. **Primary + secondary both fill, `Failed` falls through to watering** (`Parent: Watering_Can_Fill_No_Anim`, `Failed: Use_Charge`):
   one click = "fill if you look at water, else water". Ours does the same in code (`water()` first).
4. Their `Offset Y -1`, `Height 1` cylinder is a flat layer under the hit block only; ours picks soil at y or y-1 - equivalent.
Nothing they do is missing in ours; no change recommended unless a bug shows.

## 3. Advanced Farming 1.3.1 (Counter / Thecounters03, co-author JeCodeLeSoir)

Licence: CurseForge field "All Rights Reserved" -> **cannot fold, copy or ship any of its files.** PACK.md already says "ideas only".
Java: only `CheckItemBroken` (an interaction type that fails when the held item is broken) - used by its sickles/hoes.
Items: Infinite Water Bucket; 4 watering cans (Thorium 3x3, Cobalt 5x5, Adamantite 7x7, Mithril 9x9; each an Empty item + a `Filled_Water`
variant, MaxDurability 20 for Cobalt, "grow 2.5x faster"; recipe 3 bar + the previous can at `Farmingbench` tier 3/4/5/6); 4 "Advanced"
hoes (Thorium..Mithril, 3x3..9x9 `AOECylinder`); 5 sickles (Iron..Mithril, `HarvestCrop` swings); Advanced + Telescopic Shears; a leaf
resource type + salvage recipes.

**How the Infinite Water Bucket works (`Infinite_Water_Bucket.json`, ~80 lines, all vanilla pieces):**
- `MaxStack 1`, `Quality Legendary`, `ItemLevel 15`, category `Items.Tools`, tag `Container`, `PlayerAnimationsId Item`.
- Look: a block-style item, vanilla `Blocks/Decorative_Sets/Village/Bucket_Full.blockymodel` + vanilla `Bucket_Texture_Water.png`,
  `CustomModelScale 0.75`. It ships NO model or texture - it points at vanilla paths (both exist in the current Assets.zip). Only its
  own icon PNG (`Icons/ItemsGenerated/Infinite_Water_Bucket.png`) is shipped.
- Secondary interaction = `PlaceFluid`, `FluidToPlace: Water_Source`, `RemoveItemInHand: false` (the bucket stays),
  `Next` = `ModifyInventory { AdjustHeldItemDurability -1, BrokenItem: Container_Bucket }`, sound `SFX_WATER_MoveOut`. The item has no
  `MaxDurability`, so the -1 has nothing to wear out (UNVERIFIED that the engine leaves it alone; the mod's page says it works, and the
  bucket cannot break). It places a real SOURCE block every click, nothing else (no refill step, no cooldown).
- Recipe: 15 `Plant_Crop_Mana3` + 8 `Container_Bucket` at `Farmingbench` / `Farming` (no tier). `Plant_Crop_Mana3` is the top (Mana III)
  alchemy crop - exists in the current Assets.zip.
- Refilling cans: it does not touch cans. The placed source is water, and a can refills from any `Water_Source` by `RefillContainer`.

**Our own "Infinite Water Bucket" - build spec (small, lean round):**
- Owner: **SkyyGear** (it owns the lifelong watering cans; same file group as `GearCan`). Item `Tool_SkyyInfiniteWaterBucket` (our id).
- Assets, all generated at build time from vanilla: copy the vanilla `Container_Bucket_State_Filled_Water` / `Container_Bucket` JSON
  shape from Assets.zip (read in memory), set the model path to vanilla `Blocks/Miscellaneous/Bucket_Full.blockymodel` + vanilla
  `Bucket_Texture_Water.png` (reference by path, ship nothing), icon generated like the other tool icons (tinted vanilla bucket icon).
- Interaction: `PlaceFluid Water_Source`, `RemoveItemInHand false`, no durability, no `BrokenItem`. Safety: add a Server Setup row
  `bucket.cooldownSec` [1] and `bucket.maxPerMinute` [0 = off], and a switch `bucket.enabled` [true]. Each placed source can flood a
  field: tell Skyy (default: allowed anywhere vanilla water placement is allowed).
- Gate: crafted at the **Farmingbench**, tier line of the late-game farming items. Defaults: Farming skill 40 [40], Farming collection
  gate on the top crop's collection [Mana III crop = the final collection tier], cost 15 `Plant_Crop_Mana3` + 8 `Container_Bucket`
  (AF's numbers are a lead, not a licence issue - they are a recipe idea; we may pick our own: suggest 10 Mana III crops + 6 buckets
  + 1 Mithril Watering Can so it sits above the top can). Quality Legendary. Tier tag via `tools/tier_tags.py` (a round that adds a
  tiered item adds it there).
- Cans: a placed source refills the lifelong can through the existing `GearCan.water()` check; the can itself is not changed. Optional
  extra [no]: right-click the bucket on the can = instant full fill (needs new code, not asked).
- Ponds: SkyyIslands 0.5.20 pond = 46 Water_Source cells at island 1 (x1-5, z7-11). A pond is free and always there; the bucket is
  the late-game replacement for building your own pond (sources next to every field). Nothing changes in SkyyIslands. Check:
  a placed source must not break an island's 179 pond cells check (it only reads blocks in the pond area; a player-made source nearby
  does not matter).
- Duplicates (rule 2): vanilla has a normal water bucket (Container_Bucket + Water state, single use), no infinite one. Packed mods
  `InfiniteBuckets` / `Infinite Water Supply` exist on CurseForge (not in Skyy's Mods folder, not surveyed - question 3).
- Test: place on stone, on air above a field, on a tilled block; second click while the first source still flows; swap to a can and
  refill; inventory still has the bucket; relog; creative vs adventure.

## 4. GlymeraFarmer 13.0.0 + GlymeraIrrigation 10.0.0 (GlymeraCraft) - reference only, for farming totems

Licence: CurseForge shows "All Rights Reserved" but the description says "Free for personal and server use. No attribution required." =
usable on a server we run; NOT redistribution/modpack permission. We do not ship its jar in a pack download and must not copy its code or
tables. Treat as reference; ask GlymeraCraft before any fold.

Our totem plans: `research/Gathering-Shards-Spec.md` 9.3 (Farming totems "themed workers": Harvest Spirit = auto-harvest starter,
Rain, Fertilizer, ... ; collectors start as a placed Totem Pole; tiered area like AutoFarmer/HyRise 3x3..7x7) and 9.3.1 (forms). Note: the
shard islands are eternal plants inside a shard world, so planting is not needed there; the island farm is where a planting totem helps.

How the Kweebec farmer works (`GlymeraFarmer.class`, Java + 1 chest item + 2 NPC roles; ~15 files):
- **Pieces:** `Furniture_Farmer_Chest` (copy of a crude chest, capacity 36, family Farmer, crafted from a Crude Chest Small + Wheat Seed at
  the Fieldcraft bench / Workbench; recipe written at runtime into a generated pack `GlymeraFarmerCrafting`); NPC role `GlymeraFarmer`
  (Kweebec_Sapling look, invulnerable, Seek its locked target, else wander radius 2); NPC `GlymeraFarmerMarker` (Kweebec_Seedling, stands
  still) used as a visible target marker the farmer walks to.
- **Chest registry:** `chests.json` in the plugin data dir (owner UUID, x/y/z, world, seed id); `activeChests` map; `maxActiveChests`
  (3) per player. A seed placed in the chest defines the crop (`seedToMapping`: ~14 standard + eternal + 6 "special" alchemy crops).
  Seed is never used up.
- **Finding chests:** every `chestScanTickMs` (5 s) it looks at each online player: block positions within `chestScanRadius` (48) in
  loaded chunks (`ChunkStore.getChunkReference`, `getBlock`), keeps the chest block id `Furniture_Farmer_Chest`, reads
  `ItemContainerBlock` for the seed.
- **State machine** (`farmerTick`, every `farmerTickMs` 2000 ms): WAITING_FOR_SEED -> SCANNING -> HARVESTING / PLANTING -> DEPOSITING
  -> CHEST_FULL, with IDLE/MOVING_TO_HARVEST/MOVING_TO_PLANT/MOVING_TO_CHEST and stuck (30 s) and return (60 s) timeouts that teleport
  the farmer to the chest.
- **Finding grown crops:** `findNearestMatureCrop` scans the block ids of the mapped crop's final stage (`<Crop>_Block_State_Definitions_StageFinal`,
  and `_Eternal` variants) within `scanRadius` (16) of the farmer and `maxWorkRadius` (32) of the chest; harvest has priority over planting.
- **Finding farmland:** `findNearestEmptyFarmland` = a block of `Soil_Dirt_Tilled` (+ the Watered / Fertilized state definitions
  `*Soil_Dirt_Tilled_State_Definitions_Watered` etc.; `Soil_Dirt_Crystal` for alchemy crops) with `Air`/`Empty` above. `isReachable` and
  `workDistance` 3.5 decide when it works.
- **Plant:** `placeCropBlock` sets the crop block with its starting growth state by hand: `FarmingData.getStartingStageSet`, creates a
  `FarmingBlock` component (`setCurrentStageSet`, `setLastTickGameTime` from `WorldTimeResource.getGameTime`, `setGrowthProgress`,
  `setGeneration`), then `BlockSection.scheduleTick`/`setTicking` so the vanilla growth system advances it.
- **Harvest:** `nativeHarvest` = vanilla `FarmingUtil`-style harvest (breakBlock with the stage set after harvest = replant for
  crops that regrow) and adds the drops to its own `inventory` (random min/max; eternal crops keep growing); at `depositThreshold` (16)
  items it walks to the chest and `depositItems` into the `ItemContainer` (`addItemStack`); chest full = state CHEST_FULL.
- **Chunk unload / respawn:** `isChestChunkLoaded` / `getChunkIfLoaded` each tick; if the chest's chunk is not loaded the farmer is
  despawned (`removeEntity`, `RemoveReason.REMOVE`) and respawned (`spawnFarmerAtChest`) when it loads again; `cleanupOldEntities` on
  start, `removeDuplicateFarmers` + `cleanupFarmersNearChest` guard duplicates (entities survive restarts otherwise). Class `W7` is its
  chunk helper: `TickingPin` (a ChunkStore system that keeps a chunk's block components ticking), `ChunkPreLoadProcessEvent` hook,
  `getChunkIfInMemory/NonTicking` loads, `setBlockTicking`, `pinTicking`.
- **Work area:** a SQUARE since 6.0.0: `maxWorkRadius` 32 = 65x65 around the chest (changelog: was a circle). Config file
  `mods/Glymera_GlymeraFarmer/config.json` (scanRadius 16, workDistance 3.5, depositThreshold 16, maxActiveChests 3, enableSpecialCrops).
- **GlymeraIrrigation** (code only, `IrrigationPlace/Break/UseBlockSystem` + `ChunkFarm` per chunk): farmland within a config radius 1-8
  (default 4) of water stays watered; it only "dehydrates its own blocks" (so a watering can's water is not removed). Idea for us:
  a Rain / Water totem is the same job as this.

What our totem could reuse (ideas, not code):
1. **No NPC for the real work.** The Kweebec walk, marker, timeouts and teleport exist for looks. A Totem Pole should do the work in
   a world tick over its square (like our Harvester `HarvestCrop` + `GearCan.cells` and the Collections fills) and show wisps as a
   particle. Far less breakage, no duplicate-NPC cleanup. Keep a small wisp entity only if Skyy wants a visible worker.
2. **Square work area, tier = radius** (matches AutoFarmer 3x3..7x7 in the spec). Their 65x65 is a free-for-all; ours should be
   3/5/7/9/11 like the cans.
3. **Chunk rule:** only work while the totem's chunk is loaded (no forced loading); on unload do nothing, on load catch up by game time
   (the shard "lastRun" idea already in 9.3). Lets a totem be idle without any despawn code.
4. **Planting by hand needs a `FarmingBlock` component** (stage set, last tick game time, growth, `scheduleTick`). If a totem plants
   or replants, copy this recipe (VERIFY on current engine; Glymera 13.0.0 is current). Harvest by reusing our `SkyyGearHarvest` /
   vanilla `HarvestCrop` path, deposit into an `ItemContainerBlock` chest beside the pole (the same container API they use) or the
   shard's storage.
5. **Config ideas** worth copying into Server Setup rows: tick ms, scan radius, deposit threshold, max totems per player, stuck timeout.
6. Seed chosen by what is in the chest (seed never used up) is a simple, nice UX for a "planting" totem; for eternal crops on shard
   islands, nothing to plant.

## Questions for Skyy (defaults in [brackets])

1. More Food Stuff: wait for the author's update before packing, and meanwhile add Berry Milkshake / Tankard drinks / Butter as our own
   SkyyCooking dishes? [Wait; do not build our own copies yet - 75 foods are planned, check back each month.]
2. Infinite Water Bucket: build our own in SkyyGear as in section 3 (late-game, above the top watering can)? [Yes, lean round, with
   Server Setup rows bucket.enabled / bucket.cooldownSec].
3. Survey CurseForge's `InfiniteBuckets` / `Infinite Water Supply` for a licence-OK (MIT/PD/CC BY) bucket to fold before we build?
   [Yes, one quick check before the build round.]
4. Bucket recipe gate: Farming skill 40 + top Mana III crop collection + Mithril Watering Can? [Yes, 10 Mana III crops + 6 buckets + 1 Mithril can.]
5. Farming totems: do the work in a world tick (no Kweebec walker), wisps as particles only? [Yes; a visible worker only later if you ask.]
6. Ask GlymeraCraft (and Krynnx) for modpack permission? [No - we build ours; reference only.]
