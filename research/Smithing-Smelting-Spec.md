# Smithing from smelting + table-only Alchemy and Cooking: build spec

*Written 2026-09-23 by a research workflow (writer). Research only: no build script, mod folder, game file or other doc was changed.*
*Revised 2026-09-23 after a verifier pass: Campfire and Cooking now follow `research/Cooking-Skill-Spec.md` (2.5, 3.3, 5). Also fixed: the salvage numbers and the loop decision (2.4), a `classify` sketch (3.3), config ownership and migration (2.6), SkyySacks rule wording (4.1, 6.2, 6.3), and a state-item id (7.1).*
*Targets: **SkyySkills 0.4** (the same build as `research/Alchemy-Skill-Spec.md`), **SkyySacks 0.7.3** (after 0.7.2), **SkyyAccessories 0.4.2** (after 0.4.1). Edit the `tools/*_patch.py` chain, not generated scripts.*
*Skyy's calls (2026-09-23): "make smelting things in the furnace also gain smithing skill xp" and "remove the accessories for alchemy and cooking, leave them as table use only (but make sure they can draw from the sacks if you can)".*

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode (tools/dev: reflect, bc, bcfull, callers, cpgrep), in `Assets.zip` (read in memory), in our build scripts or in a server log. UNVERIFIED = design, inference or not yet tested in game. `[SKYY?]` = a number or choice for Skyy (they/them).

**How this fits with `research/Alchemy-Skill-Spec.md` (read it first).** That spec already defines the SkyySkills 0.4 plumbing. This spec **reuses** it and does not redefine it:
- Slots: Alchemy = 10, **Smithing = 11**, `CLASS_END = 10`, `ROW_SLOTS`, `PERK_SLOT` (its sections 9.1-9.4).
- Bridge: `skill:fn:addxp` and `skill:fn:craftxp` (its section 7).
- Config names: `smithing.smelt.enabled`, `smithing.xp.<outputId>`, `smithing.smeltDefault` (its section 12).

This spec **owns** four things:
1. The placed vanilla Furnace hook. The Alchemy spec left it as "Phase 2, UNVERIFIED". It is specified exactly here (section 3).
2. The Smithing XP numbers. They replace the Alchemy spec's 10.2 draft; the key names stay the same (section 2).
3. Retiring the bench accessories (section 6).
4. The sack draw at the tables (section 7).

It also **corrected** two claims in that spec. The Alchemy spec has since adopted both (VERIFIED, its current text):
- Its 10.2 said "no loops". Salvaging does turn bar-made items back into ore (section 2.4). Its 10.2 now reads "Loops (corrected)" and points here.
- Its 10.3 said the vanilla Furnace "waits for a test". A verified hook exists (section 3). Its 10.3 is now marked "superseded" and points here.

**How this fits with `research/Cooking-Skill-Spec.md`** (same 0.4 build; VERIFIED, the file exists):
- Cooking earns XP at the vanilla Cooking Bench through the shared `CraftSys`. It also adds three Cooking Bench recipes for the campfire dishes.
- It rules that a placed Campfire pays **no** Cooking XP (its 3.2 and 6.1).
- This spec follows that ruling. SmeltSys pays only at a Furnace and has no Campfire branch (section 2.5).

---

## 1. Verdicts in plain words

1. **Vanilla Furnace gives Smithing XP to the right player: YES.** VERIFIED path, UNVERIFIED in play.
   - The XP goes to the player who takes finished items out of a Furnace's output slots into their own inventory. It is paid the moment they arrive.
   - How: every such move reaches the player's own entity as the ECS event `InventoryChangeEvent`. The event carries a `MoveTransaction` of type `MOVE_TO_SELF`, whose "other container" is the Furnace window's container. It names the item, the slot it left, and how much landed.
   - This is the same event the vanilla quest system (`ObjectiveInventoryChangeSystem`) listens to.
   - Nothing has to be polled or registered per furnace, and several players at one furnace are told apart exactly.
   - Smelting itself (while the furnace burns) happens with no player attached, so the XP comes at collection, as in Minecraft. Details in section 3.
   - A placed Campfire pays nothing here: no Smithing, and no Cooking by the Cooking spec's 3.2 ruling (section 2.5).
2. **SkyySacks Furnace tab gives Smithing XP: YES, simple.**
   - The queue is per player and per profile. `ProcBench.finishUnit` is the one place a unit finishes.
   - Credit at completion through `skill:fn:craftxp`, as the Alchemy spec's 7.3 says.
   - Offline progress is replayed only while the player is online, so the XP always reaches the right profile. Section 4.
3. **The vanilla Alchemy Bench and Cooking Bench draw from sacks: YES, already. No new code is needed for the basic draw.**
   - Both are `"Type": "Crafting"` benches (VERIFIED, Assets.zip), so they open `SimpleCraftingWindow` (VERIFIED: `CraftingPlugin.setup` registers `BenchType.Crafting -> OpenBenchPageInteraction.SIMPLE_CRAFTING_ROOT`).
   - `SimpleCraftingWindow.handleAction` crafts from `CombinedItemContainer{inventory, getExtraResourcesSection().getItemContainer()}`, for both queued and instant crafts (VERIFIED bytecode). That section is exactly what the SkyySacks bag link (`CraftLinkTask`) fills.
   - A 0.5.2 server log shows the link feeding a `SimpleCraftingWindow` (`craft link: fed 11 item types ... consumed=0`), so the feed ran. Real consumption has never been seen in play (UNVERIFIED in play).
   - Two known gaps have a small fix (section 7):
     - The mirror holds only 36 slots, filled by largest pile first, so rare ingredients can be crowded out.
     - Crafted intermediates (flour, dough, salt, spices, glass vials) are not sack items.
4. **The Campfire and the Furnace (timed benches) do NOT draw from sacks through the bag link.** VERIFIED.
   - Their smelting reads only the block's own input slots (`ProcessingBenchBlock.getInputContainer()`). No class in that path references `MaterialExtraResourcesSection`.
   - The link only helps **bench tier upgrades** at those windows: `CraftingManager.startTierUpgrade` does read the extra section (VERIFIED).
   - Making a timed bench pull from sacks needs a new "top up the input slot" feature. It is optional, section 7.3.
5. **Retire three accessories, not two.** Alchemy Bench, Cooking Bench, and also the **Campfire** `[SKYY?]`.
   - All 3 Campfire recipes are cooked food (VERIFIED, Assets.zip).
   - In SkyySacks 0.7.2 an equipped Campfire accessory already puts those 3 foods into the /craft Crafting tab, where they craft instantly (VERIFIED code path).
   - Keep the item assets (no recipe), so owned copies stay valid items that do nothing. Section 6.
   - `research/Cooking-Skill-Spec.md` 3.3 recommends the same (its open question 3).

Corrections for the plan docs (for the main session; this pass edits nothing else):
- `SkyySacks-Plan.md` / `SkyyAccessories-Plan.md` say "the SkyySacks bag link already feeds every vanilla bench window". That is true for instant benches, false for timed-bench inputs (point 4).
- `SkyySacks-Plan.md` says "Accessories already owned stay as items but do nothing (no recipe)". That is right, but it needs the acc:has filter from section 6.2. Today an equipped old copy would keep unlocking /craft recipes, because `AccDefs.benchList` does not check the bench table for real held items (VERIFIED).

---

## 2. Smithing XP table

### 2.1 Sizing rule

- The shared curve is VERIFIED from `build_skyyskills_0.3.2.py` `LEVELS`: level 10 = 9,925 XP total, level 20 = 522,425, level 25 = 3,022,425, level 100 = 637,672,425.
- Mining pays per ore block. VERIFIED 0.3.2 defaults: Copper 5, Iron 8, Silver 10, Gold 12, Cobalt 15, Thorium 18, Mithril 25, Adamantite 30, Onyxium 40, Prisma 50.
- One ore block drops exactly 1 ore item plus a cobble (VERIFIED: `Ore_Copper_Stone` etc. DropList). So Mining XP per ore block = Mining XP per ore item.
- **Recommendation: a bar pays the same Smithing XP as the Mining XP of its ore (factor 1.0).** Mining and smelting the same ore then advances Mining and Smithing at the same pace. That is the literal reading of "comparable", and reforging and powders add on top later.
  - The Alchemy spec's draft (10.2) was about 2x. This spec halves it for two reasons: the salvage loop in 2.4, and ore bought from the Bazaar. It is one line per item either way `[SKYY?]`.

### 2.2 Per-output table (Furnace recipes VERIFIED in Assets.zip, all `OutputQuantity 1`)

| Furnace output | Input | Time (tier I) | Ore Mining XP (0.3.2) | **Smithing XP per item (recommended)** | Alchemy-spec 10.2 draft |
|---|---|---|---|---|---|
| Ingredient_Bar_Copper | Ore_Copper x1 | 10 s | 5 | **5** | 10 |
| Ingredient_Bar_Iron | Ore_Iron x1 | 14 s | 8 | **8** | 16 |
| Ingredient_Bar_Silver | Ore_Silver x1 | 4 s | 10 | **10** | 20 |
| Ingredient_Bar_Gold | Ore_Gold x1 | 10 s | 12 | **12** | 24 |
| Ingredient_Bar_Cobalt | Ore_Cobalt x1 | 18 s | 15 | **15** | 30 |
| Ingredient_Bar_Thorium | Ore_Thorium x1 | 18 s | 18 | **18** | 36 |
| Ingredient_Bar_Mithril | Ore_Mithril x1 | 30 s | 25 | **25** | 50 |
| Ingredient_Bar_Adamantite | Ore_Adamantite x1 | 20 s | 30 | **30** | 60 |
| Ingredient_Bar_Onyxium | Ore_Onyxium x1 | 4 s | 40 | **40** | 80 |
| Ingredient_Bar_Prisma | Ore_Prisma x1 | 4 s | 50 | **50** | 100 |
| Potion_Empty (glass vial) | Sands x1 | 10 s | sand 2 | **2** | 4 |
| 11 smoothed rocks (Rock_Aqua, _Basalt, _Lime, _Marble, _Quartzite, _Sandstone(+Red, White), _Shale, _Slate, _Volcanic) | 2 raw of that rock | 0 s | 1 per rock block | **1** (`smithing.smeltDefault`) | 1 |
| Rock_Dawnstone, Rock_Dawnstone_Cobble | Rock_Quartzite x2 | 2 s | - | **1** (default) | 1 |
| Soil_Clay_Cobble_Orange, Soil_Clay_Raw_Brick, Soil_Snow_Brick | 2 clay / snow | 2 s | - | **1** (default) | 1 |
| **Ingredient_Charcoal** (fuel byproduct, ExtraOutput: 1 per 2 fuel burned) | - | - | - | **0** (must be listed; see 2.3) | not listed |

Pace at the recommended numbers (VERIFIED arithmetic):
- Smithing 10 = about 1,241 iron bars.
- Smithing 20 = about 29,000 thorium bars.

That is exactly the Mining pace for the same ore.

### 2.3 Rules for unknown outputs (resolution order, same order in both hooks)

1. `smithing.xp.<exact output id>` if present. `0` = no XP.
2. The output id starts with `Ingredient_Bar_`: find its Furnace recipe with `CraftingPlugin.getBenchRecipes(BenchType.Processing, "Furnace")`. That static method is VERIFIED; `ProcessingBenchBlock.setupSlots` calls it, and its list holds `CraftingRecipe`.
   - Match `getPrimaryOutput().getItemId()`, take `getInput()[0].getItemId()` (the ore) and look it up with `SkillCfg.resolve(oreId)`.
   - If that is a Mining rule, XP = `max(1, round(miningXp x smithing.oreFactor))`. This covers future ores and mod ores with no config edit.
3. Otherwise `smithing.smeltDefault` (1).

**`Ingredient_Charcoal=0` is required.**
- In the vanilla Furnace, the fuel byproduct lands in the same output slots. SkyySacks mirrors vanilla `consumeOneFuel` into `out` (VERIFIED `ProcBench.burnOne`), and the vanilla bench JSON has `ExtraOutput` (VERIFIED).
- Without the zero, rule 3 would pay 1 XP per charcoal.
- The SkyySacks path never sees charcoal, because it credits recipe completions, not items.

### 2.4 Loop check (correction to the Alchemy spec 10.2 "no loops")

VERIFIED from Assets.zip (all 403 `Server/Item/Recipes/Salvage/*` files, read in memory):
- **144** salvage recipes return **ore** (an `Ore_*` item in `Output`). None of them returns a bar.
- Ore back per bar spent is small. This counts only recipes whose salvaged item has its own `Recipe` that uses `Ingredient_Bar_*`:
  - The median is **0.30** over the 126 such recipes.
  - The median is **0.25** over the 102 left after dropping the 24 on the placeholder bench `TODO` (see below).
  - Method: ore out per salvaged item, divided by bars in per crafted item. It uses the item's `Recipe` and `OutputQuantity` and the salvage `Input` quantity.
- Only one craftable item gives back as much ore as it cost. `Tool_Sickle_Copper` = 2 Wood_Trunk + 1 copper bar at the Farming Bench tier 4 (1.5 s). Salvaging it returns 1 Ore_Copper + 1 fibre (4 s).
- The 4 `Armor_Steel_Ancient_*` pieces return more ore than bars: 1.17 to 1.5 Ore_Iron per Ingredient_Bar_Bronze.
  - Their recipes name the bench `"Id": "TODO"`. No bench block has that id; the 15 real ids are Alchemybench, Arcanebench, Armor_Bench, Armory, Builders, Campfire, Cookingbench, Farmingbench, Furnace, Furniture_Bench, Loombench, Salvagebench, Tannery, Weapon_Bench, Workbench.
  - So players cannot craft them. Salvaging a piece obtained another way (loot, admin) is an ore drop, not a loop.
  - Recheck if a game update gives them a real bench.
- So "bar -> sickle -> salvage -> ore -> smelt" can repeat. Each lap costs 2 logs + fuel + about 15 s of bench time (1.5 s craft + 4 s salvage + 10 s smelt). It pays 5 Smithing XP.

What the loop does and does not do:
- **It creates no ore and no bars.** One copper bar goes in and one comes back out. Mining's ore supply and SkyyBazaar's ore and bar prices are untouched. The only products are Smithing XP and 1 fibre per lap.
- It turns logs into Smithing XP, about 2.5 Smithing XP per log. Chopping that log pays 6 Foraging. For comparison, mining and smelting one copper ore pays 5 Mining + 5 Smithing.
- The furnace is the slow step. Smelting is always timed, in the vanilla Furnace and in the SkyySacks Furnace tab (section 4.4 keeps it off the instant tabs).
- Players can run several furnaces at once, so time only limits one lap, not the hourly rate. **Logs are the real limit.**

Recommendation: accept it at factor 1.0 `[SKYY?]`.
- At the 2x draft it doubles, to 5 Smithing XP per log (close to the Foraging rate).
- Hardening, only if Skyy sees abuse (not in this build): a per-player "salvage debt". SmeltSys can see withdrawals from `Salvagebench` windows the same way it sees the Furnace. Each salvaged `Ore_X` would cancel the Smithing XP of one later `X` bar.
- Instant salvage in /craft (SkyySacks, section 6.3 item 4):
  - With a Salvage Bench accessory, the Crafting tab crafts **Salvagebench recipes instantly**. 0.7.2 merges every non-separate bench regardless of type (VERIFIED `benchRecipes`).
  - That removes the 4 s salvage wait from a lap, but not the 10 s smelt, so the verdict stays the same.
  - Stopping it would also switch off the Salvage Bench accessory. So it is Skyy's call, not a requirement for Smithing.

### 2.5 Furnace outputs that are not Smithing, and other benches

- **No food is smelted in the Furnace.** VERIFIED: 27 Furnace recipes, zero `Food_*` outputs.
- Glass, smoothed stone and bricks are "smelting things", so they pay the small default by Skyy's wording. Set `smithing.smeltDefault=0` to exclude them.
- **Campfire** (3 recipes, all food, 2 s): `Food_Fish_Raw -> Food_Fish_Grilled`, `Vegetables -> Food_Vegetable_Cooked`, `Meats -> Food_Wildmeat_Cooked` (VERIFIED).
  - This is Cooking, not Smithing, and `research/Cooking-Skill-Spec.md` owns it (VERIFIED: the file exists and targets the same 0.4 build).
  - That spec's ruling: a placed Campfire gives plain food and **no Cooking XP** (its 3.2, 6.1 and test 12).
  - Cooking XP and Grades for the three campfire dishes come from three new Cooking Bench recipes (`Skyy_Cook_Recipe_Wildmeat`, `_Fish`, `_Vegetable`) through the shared `CraftSys`.
  - So **SmeltSys has no Campfire branch** and pays nothing for Campfire output.
  - There is no `CookHook` stub. An earlier draft of this spec had one, and it would compete with the Cooking spec's real path.
  - The two specs share one open question (Cooking spec 3.2 "Later option" and its section 9 item 6): should the "collector is the cook" rule also pay Cooking at a Campfire? This spec uses that rule for the Furnace.
    - Answer here: **yes for the Furnace (built now), not for the Campfire in 0.4** `[SKYY?]`.
    - Why: at a Campfire it would also have to swap the collected food for graded items inside an inventory event. The Cooking Bench recipes already cover those dishes.
    - If Skyy wants it later: add a `Campfire` branch to this same SmeltSys (reuse `SmeltXp.moves`, `added` and `benchOf`) instead of a second `InventoryChangeEvent` system. Update the Cooking spec's 3.2 in the same pass.
  - The Campfire accessory's fate is in section 6.1.
- **Tannery** (8 leather recipes) pays nothing, and so does **Salvagebench** (it would be a loop). SmeltSys ignores every bench id except `Furnace`. VERIFIED: there is exactly one block per bench id (`Bench_Furnace` = "Furnace", `Bench_Campfire` = "Campfire", `Bench_Salvage` = "Salvagebench", `Bench_Tannery` = "Tannery").

### 2.6 xp.properties (replaces the smithing lines of the Alchemy spec's section 12, same keys plus three)

```
# Smithing: smelting XP per finished item. Vanilla Furnace = when you take it out of the output slots into your inventory;
# SkyySacks /craft Furnace tab = when a unit finishes (skill:fn:craftxp). Reforging / powders use skill:fn:addxp later.
smithing.smelt.enabled=true
smithing.vanillaFurnace=true
smithing.xp.Ingredient_Bar_Copper=5
smithing.xp.Ingredient_Bar_Iron=8
smithing.xp.Ingredient_Bar_Silver=10
smithing.xp.Ingredient_Bar_Gold=12
smithing.xp.Ingredient_Bar_Cobalt=15
smithing.xp.Ingredient_Bar_Thorium=18
smithing.xp.Ingredient_Bar_Mithril=25
smithing.xp.Ingredient_Bar_Adamantite=30
smithing.xp.Ingredient_Bar_Onyxium=40
smithing.xp.Ingredient_Bar_Prisma=50
smithing.xp.Potion_Empty=2
smithing.xp.Ingredient_Charcoal=0
# an Ingredient_Bar_* not listed: Mining XP of the ore its Furnace recipe uses x this (at least 1)
smithing.oreFactor=1.0
smithing.smeltDefault=1
```

Implementation notes:
- Every listed id goes through `must()` at build time; all are VERIFIED to exist in Assets.zip.
- The global `multiplier` applies (`SkillCfg.scaled`).
- `/skills reload` re-reads the keys and clears the per-id cache.
- None of these keys starts with `block.`, `prefix.` or `suffix.`, so the 0.3.2 block-rule loop in `SkillCfg.load` skips them (VERIFIED: that loop only picks up those three prefixes).

**One owner for the smithing lines, plus a migration note.** The `ensureDefaults` pattern appends a block only when its prefix is missing entirely. VERIFIED: `AcroCfg.ensureDefaults` in 0.3.2 returns as soon as any key starts with `acro.`, and "the code defaults apply either way".
- The Alchemy spec's section 12 block still carries its draft `smithing.*` lines (2x values). Its `AlchCfg.ensureDefaults` appends that block when no `alchemy.` key exists.
  - Build the 0.4 `DEFAULTS` with **only this section's** smithing lines, and drop the draft ones from the Alchemy block. That spec's section 12 already says this section replaces them.
  - Otherwise an existing file gets the `smithing.*` keys twice, and `java.util.Properties` keeps whichever it reads last.
- If `SmithCfg` stays its own class, `SmithCfg.ensureDefaults` appends this block when no key starts with `smithing.`. If it is folded into `AlchCfg`, the one Alchemy + Smithing block must hold these lines.
- **Code defaults must match this table**, including `Ingredient_Charcoal=0`: put the table into `XP` before reading the file. Then a file that lacks a key still gets this spec's number, and charcoal never falls through to `smeltDefault`.
- **Migration:**
  - No SkyySkills 0.4 has been built yet (VERIFIED: there is no 0.4 build script and no `tools/skills_0_4_patch.py` in the repo, and HANDOFF section 3 lists 0.4 as planned).
  - If a test build with the Alchemy draft numbers ever writes `smithing.*` keys into a world's `xp.properties`, those keys stay and beat the new defaults.
  - Before testing this spec in that world, delete the `smithing.*` lines, then restart or run `/skills reload`. `ReloadCmd` calls `SkillCfg.load()`, which runs `ensureDefaults` (VERIFIED 0.3.2), so the block is appended again.

---

## 3. Vanilla Furnace hook (SkyySkills 0.4)

### 3.1 Engine facts (all VERIFIED unless marked)

| Fact | Evidence |
|---|---|
| Smelting runs in `ProcessingBenchBlock.advanceProcessing(...)`, driven by `BenchSystems$ProcessingBenchTick` per placed bench, with no player. `CraftRecipeEvent` is never fired there | bytecode; Alchemy spec 3.1 agrees |
| The bench's containers are one `CombinedItemContainer` = **[0] fuel, [1] input, [2] output** | `ProcessingBenchBlock.setupSlots` builds `new CombinedItemContainer(new ItemContainer[]{fuel, input, output})` |
| Output slots use `setGlobalFilter(FilterType.ALLOW_OUTPUT_ONLY)`: players can take out but never put in | `setupSlots` offset 458-461 |
| `ProcessingBenchWindow.getItemContainer()` returns that same combined container (the window keeps `processingBenchBlock.getItemContainer()`) | window constructor offsets 103-106; getter bytecode |
| Every player move with a window resolves the window section to `ItemContainerWindow.getItemContainer()` | `InventoryUtils.getSectionById` |
| All three withdrawal paths end in a move whose destination gets `MoveTransaction.toInverted(source)` = `MOVE_TO_SELF` with `getOtherContainer()` = the bench's combined container: drag (`InventoryUtils.moveItem` -> `moveItemStackFromSlotToSlot`), shift-click (`smartMoveItem` -> `moveItemFromCheckToInventory` -> `moveItemStackFromSlot`), double-click gather (`combineItemStacksIntoSlot`) | bytecode of each |
| `ItemContainer.sendUpdate` dispatches `ItemContainerChangeEvent`. `CombinedItemContainer.sendUpdate` forwards to each child through `fromParent`. `MoveTransaction.fromParent` for `MOVE_TO_SELF` keeps `removeTransaction`, `moveType` and `otherContainer` and re-parents only the add part | bytecode |
| The player's `InventoryComponent` queues those events. `InventorySystems$InventoryChangeEventSystem` (subclassed for Storage, Hotbar, Backpack...) drains the queue each tick and calls `CommandBuffer.invoke(ref, new InventoryChangeEvent(type, inv, container, transaction))` on the player's own entity | bytecode |
| Vanilla listens to that event with `ObjectiveInventoryChangeSystem extends EntityEventSystem`, `getQuery()` = `Player.getComponentType()` | bytecode (the pattern to copy) |
| `ProcessingBenchWindow.handleAction` handles only `SetActiveAction` and `TierUpgradeAction`. There is no server-side "take all" | bytecode |
| The slot-to-slot move checks `cantAddToSlot` twice (target and swap-back), so a swap cannot push an item into the output slots | `ItemContainer.lambda$internal_moveItemStackFromSlot$5`; that the filter makes it refuse is inferred, UNVERIFIED in play |
| Mods can reference `com.hypixel.hytale.builtin.crafting.*` | SkyySacks 0.7.2 already uses `CraftingPlugin` and `CraftingManager` |

### 3.2 Why not the other options

| Option | Problem |
|---|---|
| `CraftRecipeEvent` | Never fired by processing benches |
| `registerChangeEvent` on each furnace's output container | Needs a per-furnace registry kept alive across chunk loads and tier upgrades (`setupSlots` can swap the containers). The event names no player, so shared furnaces would need a guess |
| Polling open windows (the `CraftLinkTask` pattern) | Misses a quick open-take-close, and needs baselines per furnace |
| Crediting at completion | No player is attached, the owner may be offline, and a shared furnace is ambiguous |

The player-side `InventoryChangeEvent` has none of these problems: it is per player, exact and synchronous (one tick late at most).

### 3.3 New classes and code

Constants (add next to the 0.3.2 ones):
```
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
MVT = "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction"
MVY = "com.hypixel.hytale.server.core.inventory.transaction.MoveType"
LTX = "com.hypixel.hytale.server.core.inventory.transaction.ListTransaction"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
SLT = "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction"
CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
PBW = "com.hypixel.hytale.builtin.crafting.window.ProcessingBenchWindow"
BWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow"
BTY = (already in 0.3.2) BlockType ; BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
CRP = "com.hypixel.hytale.builtin.crafting.CraftingPlugin" ; BTP = "com.hypixel.hytale.protocol.BenchType"
```

**`SmithCfg`** (or fold into the Alchemy spec's `AlchCfg`; that spec's `smeltFor(outId)` **is** this `forOutput`):
- Fields: `ENABLED`, `VANILLA`, `ORE_FACTOR`, `DEFAULT`, `XP` (HashMap id -> Long), `CACHE` (ConcurrentHashMap).
- `read(Properties)` and `ensureDefaults(Properties)`, following the `AcroCfg` pattern: append the block once when no key starts with `smithing.`. Read the ownership and migration note in 2.6 first.
- `forOutput(String id)` -> long, rules 2.3, cached.
- **The Alchemy spec's `RecipeXp.classify` Furnace branch must call `forOutput(primaryOutputId)`**, so `craftxp` (SkyySacks) and SmeltSys (vanilla) read identical numbers.
  - The Alchemy spec defines `classify` as returning `long[]{slot, xp per craft}` or null, with no cache of its own (VERIFIED, its section 13).
  - Sketch of the branch (javassist-safe; `getPrimaryOutput()` returns `MaterialQuantity` and `getQuantity()` returns int, VERIFIED reflect):
  ```java
  // inside RecipeXp.classify(CraftingRecipe rc), in its loop over rc.getBenchRequirement()
  if ("Furnace".equals(br[i].id)) {
    if (!{PKG}.SmithCfg.ENABLED) return null;                 // smithing.smelt.enabled=false
    {MQ} po = rc.getPrimaryOutput();
    if (po == null || po.getItemId() == null) return null;
    long per = {PKG}.SmithCfg.forOutput(po.getItemId());      // rules 2.3; SmithCfg.CACHE is the only cache
    long xp = per * (long) Math.max(1, po.getQuantity());    // per item, like SmeltSys (all 27 Furnace recipes output 1, VERIFIED)
    return xp > 0L ? new long[] { (long) {PKG}.SkillDefs.SMITHING, xp } : null;
  }
  ```
  - Do not cache `classify` results for Furnace recipes. `/skills reload` clears `SmithCfg.CACHE`, and a second cache would keep the old numbers.
  - `smithing.vanillaFurnace` gates only SmeltSys, not this branch. The SkyySacks tab keeps paying when the vanilla hook is off.

**`SmeltXp`** (static helpers, add before `SmeltSys`):
```java
// collect MOVE_TO_SELF moves whose source is a combined container (a bench window); recurse into ListTransaction
public static void moves(Object tx, java.util.ArrayList out) {
  if (tx instanceof {LTX}) {
    java.util.List l = (({LTX}) tx).getList();
    for (int i = 0; l != null && i < l.size(); i++) moves(l.get(i), out);
    return;
  }
  if (!(tx instanceof {MVT})) return;
  {MVT} mt = ({MVT}) tx;
  if (!mt.succeeded() || mt.getMoveType() != {MVY}.MOVE_TO_SELF) return;
  if (!(mt.getOtherContainer() instanceof {CIC})) return;
  out.add(mt);
}
public static int qty({IS} s, String id) {
  if (s == null || s.isEmpty() || id == null || !id.equals(s.getItemId())) return 0;
  return s.getQuantity();
}
// items of `id` that landed in THIS container (a move split over hotbar + storage arrives once per container, each with the full
// removeTransaction, so never count the remove side)
public static int added(Object at, String id) {
  if (at == null) return 0;
  if (at instanceof {LTX}) { int n = 0; java.util.List l = (({LTX}) at).getList(); for (int i = 0; l != null && i < l.size(); i++) n += added(l.get(i), id); return n; }
  if (at instanceof {IST}) { int n = 0; java.util.List l = (({IST}) at).getSlotTransactions(); for (int i = 0; l != null && i < l.size(); i++) n += added(l.get(i), id); return n; }
  if (at instanceof {SLT}) { {SLT} s = ({SLT}) at; int d = qty(s.getSlotAfter(), id) - qty(s.getSlotBefore(), id); return d > 0 ? d : 0; }
  return 0;
}
// bench id of the player's open processing window whose container is `src`, else null
public static String benchOf(java.util.List wins, Object src) {
  for (int i = 0; wins != null && i < wins.size(); i++) {
    Object w = wins.get(i);
    if (!(w instanceof {PBW})) continue;
    Object ic = (({PBW}) w).getItemContainer();
    if (ic != src) continue;
    {BTY} bt = (({BWN}) w).getBlockType();
    {BEN} b = bt == null ? null : bt.getBench();
    return b == null ? null : b.getId();
  }
  return null;
}
```

**`SmeltSys`**
- An `EntityEventSystem` for `InventoryChangeEvent`, **its own class, registered once** (the one-registerSystem-per-class rule, VERIFIED by the SkyyIslands 0.4 load failure).
- Build it with the 0.3.2 `event_system()` helper, but override `getQuery()` to return `Player.getComponentType()` (the vanilla objective system does exactly that). This is cheaper than `Archetype.empty()`, because the event fires on every inventory change.

```java
    {ICE} e = ({ICE}) ev;
    Object tx = e.getTransaction();
    if (!(tx instanceof {MVT}) && !(tx instanceof {LTX})) return;        // pickups, sweeps, /craft output: not moves -> cheap exit
    if (!{PKG}.SmithCfg.ENABLED || !{PKG}.SmithCfg.VANILLA) return;
    java.util.ArrayList mv = new java.util.ArrayList();
    {PKG}.SmeltXp.moves(tx, mv);
    if (mv.isEmpty()) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (pr == null || p == null || p.getWindowManager() == null) return;
    if ({PKG}.SkillXp.creative(st, r)) return;                          // creativeXp=false
    java.util.List wins = p.getWindowManager().getWindows();
    long smith = 0L;
    for (int m = 0; m < mv.size(); m++) {
      {MVT} mt = ({MVT}) mv.get(m);
      {CIC} src = ({CIC}) mt.getOtherContainer();
      String bench = {PKG}.SmeltXp.benchOf(wins, src);
      if (bench == null || !"Furnace".equalsIgnoreCase(bench) || src.getContainersSize() < 3) continue;   // Furnace only (2.5)
      {SLT} rt = mt.getRemoveTransaction();
      if (rt == null || src.getContainerForSlot(rt.getSlot()) != src.getContainer(2)) continue;   // OUTPUT part only (0 fuel, 1 input)
      {IS} before = rt.getSlotBefore();
      if (before == null || before.isEmpty()) continue;
      String id = before.getItemId();
      int got = {PKG}.SmeltXp.added(mt.getAddTransaction(), id);
      if (got <= 0) continue;
      long per = {PKG}.SmithCfg.forOutput(id);
      if (per > 0L) smith += per * (long) got;
    }
    if (smith <= 0L) return;
    if (smith > 1000000L) smith = 1000000L;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.SmeltTask(u, {PKG}.SkillDefs.SMITHING, {PKG}.SkillCfg.scaled(smith), {PKG}.SkillStore.pkey(u)));
```

**`SmeltTask`** (Runnable; the `BreakTask` / Alchemy `CraftTask` pattern):
1. `pr = Universe.get().getPlayer(u)`.
2. If `!key.equals(SkillStore.pkey(u))`, return: the profile switched in between.
3. If `pr` is valid: `SkillXp.gain(pr, slot, amt)`. That gives the chat line, level-ups, coins and publish.
4. Otherwise: `SkillStore.addK(key, u, null, slot, amt)`, a silent write. Owed level coins are paid on the next gain by the existing `payOwed` logic.

Registration in `setup()`: `getEntityStoreRegistry().registerSystem(new {PKG}.SmeltSys());`.

Probes to add to `B.probe` (all exist today):
- `InventoryChangeEvent.getTransaction`
- `MoveTransaction.getMoveType / getOtherContainer / getRemoveTransaction / getAddTransaction`
- `MoveType.MOVE_TO_SELF`
- `ListTransaction.getList`, `ItemStackTransaction.getSlotTransactions`
- `SlotTransaction.getSlot / getSlotBefore / getSlotAfter`
- `CombinedItemContainer.getContainer / getContainerForSlot / getContainersSize`
- `ProcessingBenchWindow.getItemContainer`, `BlockWindow.getBlockType`, `WindowManager.getWindows`
- `CraftingPlugin.getBenchRecipes(BenchType, String)`

### 3.4 Credit rule (what Skyy and players are told)

Smithing XP goes to **the player whose inventory receives finished items from a Furnace's output slots**, through drag, shift-click or double-click gather. The amount is counted per item actually received and paid when it arrives.

Nothing is paid when:
- the bars are thrown on the floor from the window;
- the furnace is broken;
- the output is full and the overflow is ejected into the world;
- the items come from the input or fuel slots;
- the bench is not a Furnace. A Campfire, Salvage bench or Tannery pays nothing here; Campfire Cooking XP is the Cooking spec's call (2.5).

At a shared furnace, whoever collects gets the XP (Minecraft's rule).

### 3.5 Anti-exploit

1. **Once per item.** Output slots are `ALLOW_OUTPUT_ONLY` (VERIFIED), so no item can be put back and collected twice. Every item in them was made there, either as a recipe output or as the charcoal byproduct (charcoal pays 0).
2. **Output part only.** The remove slot must map to container [2]. That stops "put smoothed rock or charcoal into the input or fuel slot, take it back" farms.
3. **Bench whitelist.** Only `Furnace` pays Smithing. `Salvagebench` is also a `ProcessingBenchWindow` and would otherwise turn gear -> ore -> bars into XP. `Tannery` is also excluded.
4. **Exact player.** The event is raised on the receiving player's entity, and the source must be a window **that player** has open. A split move (hotbar + storage) is counted from the add side, once per container.
5. **Creative:** no XP (`creativeXp=false`).
6. **Profile switch:** the pkey is captured at the event and re-checked in `SmeltTask`.
7. **No double count with SkyySacks.** Its Furnace-tab Collect adds items with `addItemStack` (VERIFIED `procCollect`). That is not a `MoveTransaction` from a bench, so SmeltSys ignores it. The tab pays at completion instead (section 4).
8. **Bounded.** Throughput is limited by furnace time and ore supply. One event is capped at 1,000,000 base XP.
9. **Loops:** see 2.4. The copper sickle loop creates no ore and is recommended for acceptance at factor 1.0 `[SKYY?]`; optional salvage debt if needed.

### 3.6 Known limits (accepted)

- XP comes at collection, not at completion. Bars left in a furnace pay when someone collects them.
- If a player closes the window within the same tick as the move (under about 33 ms), `benchOf` finds no window, so nothing is paid. This is theoretical.
- If the furnace is upgraded while the window is open, `setupSlots` may swap containers. The window then no longer matches, so those items pay nothing until the window is reopened (UNVERIFIED how the engine refreshes the window).
- **Side finding (not Smithing):** SkyyIslands' guard cancels damage, break, place and pickup for non-members, not block `Use` (HANDOFF 0.3 row). A visitor may be able to open an island furnace or chest and take its output. UNVERIFIED in play; worth a test.

---

## 4. SkyySacks Furnace tab hook (SkyySacks 0.7.3)

### 4.1 Exact place

This follows the Alchemy spec's 7.3 item 2, with one change and three additions. The code lives in `SkyySacks/build_skyysacks_0.7.2.py`.
- `ProcBench.finishUnit(ProcJob j)` (line 580): inside the `paid` output loop, only when real outputs were added, and only when `"Furnace".equalsIgnoreCase(this.bench)`, do `addTo(this.xpDone, j.recipe, 1)`.
  - Never count the `!paid` fallback (the inputs are returned), `burnOne` (charcoal), `cancel()` or `unloadFuel()`.
  - **The change replaces the Alchemy spec's rule; it does not add to it.**
    - Its 7.3 item 2 counts every paid unit on any bench and lets `craftxp` return 0 for Tannery.
    - Here only Furnace units are counted, so no Tannery ledger is stored or drained.
    - Build one `finishUnit` edit from this text. The Alchemy spec's 7.3 item 2 already says to follow this spec where they differ (VERIFIED).
    - The drain source string is the same in both: `"sacks:furnace"`.
- New field `public java.util.LinkedHashMap xpDone` (recipe id -> Integer). Initialize it in the constructor.
- **Addition 1, persist it:** write `xpDone` as `<bench>.xpDone` in `toProps` (line 756) and read it in `fromProps` (line 775) with the existing `ser` / `parseInto`.
  - Reason: a profile's queue can finish during a login and then sit unpaid while the player is on another profile, and a restart in between would lose it.
  - Clamp each count at 10,000 so a server without SkyySkills 0.4 cannot store an enormous back-payment.
- `ProcTask.run()` (line 2517): after the bench loop, drain once per run.
  - **Addition 2, only when `k.equals(SackPool.settledKey(u))`**: the profile switch has settled (the same guard `CraftLinkTask` uses).
  - For each `(recipe, n)` in a snapshot, call:
    ```java
    Object f = bridge().get("skill:fn:craftxp");
    if (!(f instanceof java.util.function.Function)) return;        // keep the ledger; SkyySkills 0.4 missing
    Object got = ((java.util.function.Function) f).apply(new Object[] { u, recipe, Integer.valueOf(n), "sacks:furnace", k });
    if (got instanceof Number) { pb.takeXp(recipe, n); ProcStore.markDirty(k); }
    ```
  - `takeXp` is a new synchronized method that subtracts exactly the snapshot count, so units finished meanwhile stay.
  - **Addition 3:** one `CraftLog.line(k, "SMITHING " + recipe + " x" + n + " -> " + got + " xp")` per paid batch, for support.

### 4.2 Credit rule: completion, not collect

Pay at **completion** (`finishUnit`).
- `procCollect` drains the `out` map. `cancel()` also dumps unfinished **inputs** (ore) into `out`, and `unloadFuel()` dumps fuel there (VERIFIED lines 636-659).
- So collect-time credit would need extra bookkeeping to avoid paying for returned ore. Completion is exact by construction.

### 4.3 Offline replay

`ProcBench.advance(now)` replays wall-clock time only when called. Every call site runs while the player is online, with their identity in scope (VERIFIED):
- `procQueue`, `procFuel`, `procCollect`, `procCancel`, `procUnload`, `buildProc` and `ProcTask`.
- `ProcTick` iterates `Universe.getPlayers()`.

After a login, the first `ProcTask` tick replays up to 256 queued units (`QUEUE_CAP`). `xpDone` collects them, and the same run pays one `craftxp` call per recipe. The player then sees one "+N Smithing XP" line and any level-ups.

### 4.4 Related /craft change (so the tab is the only instant-free smelting route)

- The Alchemy spec's 7.3 item 1 makes the /craft **craft** branch call `craftxp` for every instant craft.
- The Collections tab (`C:`) lists any recipe SkyyCollections' auto rule unlocks, **with no bench filter**. VERIFIED: `CollUnlocks.compute` scans every `CraftingRecipe`.
- The craft branch crafts it instantly (VERIFIED). A collection-unlocked bar recipe would therefore smelt instantly and still pay Smithing through `craftxp`.
- Filter Processing-bench recipes out of `C:` (section 6.3 item 5). Smelting then stays timed.

---

## 5. Cross-mod XP entry points (aligned with the Alchemy spec, section 7)

- **Generic grant, `skill:fn:addxp`:** `apply(Object[] { java.util.UUID player, String skill, Number baseXp, String source }) -> Boolean`.
  - `skill` must be an exact `NAMES` / `LABELS` entry listed in `bridge.addxp.skills` (default `Alchemy,Smithing`).
  - SkyySkills applies `multiplier` and the bridge caps. TRUE = accepted (queued on the world thread), FALSE = refused.
  - Future reforge and powder mods call it with `"Smithing"` (its 7.4). This spec adds nothing to it.
- **Recipe report, `skill:fn:craftxp`:** `apply(Object[] { UUID, String recipeId, Number crafts, String source [, String expectKey] }) -> Long`.
  - SkyySacks uses it for the Furnace tab (section 4). Its Furnace branch must read `SmithCfg.forOutput(primaryOutputId)`.
- **Vanilla Furnace (section 3):** in-process, no bridge. `SmeltSys -> SmeltTask -> SkillXp.gain`, reading the same `forOutput` table.
  - So both hooks share one table and one award path (`SkillXp.gain`: throttled chat line, level-up coins, `skill:<uuid>` republish).
- **Cooking:** `research/Cooking-Skill-Spec.md` (same 0.4 build) pays Cooking through `CraftSys` at the Cooking Bench. It uses `craftxp` only for a cooking recipe left in /craft, if any.
  - It needs nothing from SmeltSys, and a placed Campfire pays nothing (2.5).
  - Whether `Cooking` joins `bridge.addxp.skills` is that spec's call.

---

## 6. Retiring the Alchemy Bench, Cooking Bench (and Campfire) accessories

### 6.1 Is the Campfire a cooking accessory by Skyy's logic? Recommendation: yes, retire it `[SKYY?]`

- The Campfire's whole recipe list is 3 cooked foods (VERIFIED, 2.5).
- Its accessory `Skyy_Accessory_Campfire_T1` costs one campfire + 4 copper bars (VERIFIED item loop). In 0.7.2 it adds those foods to the /craft **Crafting** tab:
  - `benchRecipes(u, null)` merges every equipped bench except Alchemybench, Furnace and Tannery, and ignores bench type (VERIFIED lines 1694-1714).
  - The craft branch crafts instantly (VERIFIED).
- So it is exactly the "cooking recipes in /craft" the focus call removes.
- If Skyy keeps it, cooked food stays craftable from bags in /craft, which contradicts "Cooking table-only".
- `research/Cooking-Skill-Spec.md` 3.3 makes the same recommendation (its open question 3), so the two specs agree.

`RETIRED = {"Alchemybench", "Cookingbench", "Campfire"}` in both mods below.

### 6.2 SkyyAccessories 0.4.2 (line numbers are `build_skyyaccessories_0.4.1.py`)

1. **Keep the three rows in `BENCHES`** (lines 153-177) so the item assets are still generated. Add `RETIRED` and `ACTIVE = [b for b in BENCHES if b[0] not in RETIRED]`.
2. **Java arrays from `ACTIVE` only:** `BENCH_IDS`, `BENCH_NAMES`, `BENCH_MAX` (lines 244-261). That removes the three from the Omni's synthetic grants in `benchList` (lines 438-444). Add `AccDefs.RETIRED` (String[]) and `isRetired(id)` = `benchOf(id)` is in `RETIRED`.
3. **`benchList`** (line 421): after `String bn = benchOf(id)`, add `if (isRetired(id)) continue;`. An equipped old copy then drops out of `acc:has` (VERIFIED needed: today real held accessories bypass the table).
4. **`AccStore.has`** (lines 589-599): return false for retired ids. This covers the `acc:fn:has` answer.
5. **Equip refusal:** in the page handler (line 846 ff.), before `canEquip`: `if (AccDefs.isRetired(id)) { this.info = "This accessory was retired - brew at a real Alchemy Bench and cook at a real Cooking Bench now (both pull ingredients from your Magic Bags)"; rebuild(); return; }`.
   - The text leaves out the Campfire on purpose: a timed bench does not pull from bags (verdict 4).
   - The item never leaves the inventory (the existing "refused equips never leave the inventory" rule).
   - Keep Unequip unchanged, so already-equipped copies can be taken out.
6. **Bag page label** for a retired id already in the bag: `"<Name> <Roman> - retired, does nothing"` (via `AccDefs.pretty`). `rarityOf` returns 0, so it never counts for future accessory power.
7. **Item assets** (item loop, lines 1131-1148): for retired rows, build the node as today, then `del node["Recipe"]`. This mirrors the legacy talisman precedent at lines 1179-1193 (`del node["Recipe"]` at 1185).
   - Name: `"<Name> Accessory <Roman> (retired)"`.
   - Description: "Retired. Alchemy and Cooking are skills now: brew at a real Alchemy Bench and cook at a real Cooking Bench, which take ingredients straight from your Magic Bags. This accessory does nothing."
   - That covers 4 + 1 + 1 = 6 item ids: `Skyy_Accessory_Alchemybench_T1..T4`, `Skyy_Accessory_Cookingbench_T1`, `Skyy_Accessory_Campfire_T1`.
8. **Omni** (lines 1196-1207):
   - Build `omni_in` from `ACTIVE`: 10 top-tier accessories instead of 13, or 11 if the Campfire stays.
   - Replace `assert len(omni_in) == 13` with `assert len(omni_in) == len(ACTIVE) == 10`.
   - Generate the description from `ACTIVE`, and add: "(Alchemy and Cooking are table-only and are not covered.)"
9. **Counts in text:** the ready log (lines 1033-1034) uses `sum(b[3] for b in ACTIVE)`, which gives 24 active bench accessories instead of 30. Update the manifest text if it names Alchemy.

### 6.3 SkyySacks 0.7.3 (line numbers are `build_skyysacks_0.7.2.py`)

1. **`CraftPage.retiredBench(String id)`:** true for the three ids (case-insensitive).
2. **`buildTabs`** (line 1716): delete the `A:alch` line (1720).
3. **`recipesFor`** (line 1729): delete the `A:alch` branch.
   - Re-point the page registration `"SkyySacksAlchemy"` (line 2600) to `new CraftPageFactory("A:craft")`, so any old reference opens Crafting.
   - Check that `CraftPage.build` falls back to the first tab when `this.tab` is not in `this.tabs`.
4. **`separateBench`** (line 1689): keep only `Furnace` and `Tannery`.
   - **`benchRecipes`** (line 1694): skip any `BenchRequirement` whose `id` is retired, in both modes.
   - Optional `[SKYY?]`: also skip `br[i].type == BenchType.Processing` in the merged mode (`only == null`). This removes instant Salvagebench recipes from the Crafting tab (2.4). `BenchRequirement.type` is a public field (VERIFIED, Alchemy spec).
     - Side effect: once the Campfire is retired, Salvagebench is the only Processing bench left in the merged tab. The Salvage Bench accessory (1 tier, VERIFIED `BENCHES` in `build_skyyaccessories_0.4.1.py`) does nothing else.
     - So skipping Processing recipes turns that accessory off too, unless Salvage gets its own timed tab like Furnace and Tannery.
     - Not needed for Smithing. Salvage pays no XP, and instant salvage does not speed up the smelt step of the copper-sickle loop (2.4).
5. **`C:` tab** (`recipesFor`, `"C:"` branch): drop a recipe when **every** bench requirement is retired (table-only) or a Processing bench (Furnace, Tannery and Salvagebench belong to their own timed tab or are not offered).
   - VERIFIED need: SkyyCollections' auto rule has no bench filter, and the craft branch crafts instantly.
6. **Legacy `B:` tabs** (the 0.6.1 ids in `recipesFor`): apply the same retired filter.
7. **`accessories()`** (line 1633): skip retired bench names. That protects against an older SkyyAccessories that still publishes them.
8. **Ready log** (line 2607): remove "Alchemy" from the tab list.
9. Furnace tab XP (section 4) and bench-aware mirror (section 7.3).

### 6.4 What owners of these accessories see

- **In an inventory or chest:** the item still exists and renders; it is not an "unknown item". It is named "(retired)", has no recipe, and Equip refuses it with the message above.
- **Already equipped:** it stays in its bag slot, labelled "retired, does nothing".
  - It is gone from `acc:has`, so the /craft **Alchemy** tab disappears.
  - Cooking and Campfire recipes leave the Crafting tab.
  - **Unequip** returns it as usual.
- **Omni holders:** the Omni keeps covering the 10 active benches. It stops covering the three retired ones, at every tier.
- **Queued /craft processing:** unaffected. The Campfire was never a timed SkyySacks queue (`ProcStore.BENCHES = {"Furnace","Tannery"}`, VERIFIED).
- **Refund (optional) `[SKYY?]`:** ship standalone Workbench recipes that turn each retired accessory back into its vanilla bench item, plus the 4 copper bars; the Alchemy T2-T4 refunds also return that tier's upgrade materials.
  - Location: `Server/Item/Recipes/Skyy/Skyy_Refund_<Bench>_T<n>.json`.
  - Format: the vanilla Salvage files prove the standalone recipe format (`Input`, `PrimaryOutput`, `Output`, `BenchRequirement`, `TimeSeconds`; VERIFIED).
  - That a mod jar's standalone recipe asset is picked up is UNVERIFIED; test it.
  - Default: no refund, matching the plan text "stay as items but do nothing".

---

## 7. Drawing from sacks at the Alchemy and Cooking tables

### 7.1 What already works (no new code)

- Both tables open `SimpleCraftingWindow`, which crafts from inventory + the extra-resources section. Both queued crafts (potions, bread, pies: `TimeSeconds > 0`) and instant ones use it (VERIFIED, section 1.3).
- `CraftLinkTask` (every 300 ms, world thread; lines 1510-1583) feeds that section with the player's `BagMirror` for any `MaterialContainerWindow`, and syncs what the bench consumed back into the pool.
- It never checks accessories, so retiring them changes nothing here (VERIFIED).

Which ingredients can come from sacks (VERIFIED `SackDefs.catOf`, lines 123-135; the matching bag must be carried):

| From sacks | Not sack items (must be in the inventory) |
|---|---|
| `Plant_*`: berries, petals, fruits, crops incl. Health/Mana/Stamina crops, flowers, mushrooms. Farming bag | `Potion_Empty` and vials (Alchemy's base) |
| `Food_*`: raw meat and fish, eggs, cheese. Farming bag | `Ingredient_Flour`, `Ingredient_Dough`, `Ingredient_Salt`, `Ingredient_Spices` (Cooking intermediates) |
| `Ingredient_Life_Essence*`. Farming bag | `*Deco_Tankard_State_Filled_Water` (the water-filled state of `Deco_Tankard`, written as `Ingredient_Dough`'s recipe names it; it has no item file of its own), `Weapon_Daggers_Iron` (a morph input) |
| `Ingredient_Sac_Venom`, `Ingredient_Void_Essence`, `Ingredient_Bone_Fragment`, `Ingredient_Powder_Boom`. Combat bag | Fuel items that are not `Wood_*` (for example charcoal) |
| `Ingredient_Fibre`, `Ingredient_Stick`, `Wood_*` (also `Fuel`). Foraging bag | |
| `Rock_Salt`, crystal rocks. Mining bag | |

### 7.2 What does not work

- **Crowding:** `BagMirror.rebuild` (line 1407) sorts the pool by count (`CountCmp`, largest first, VERIFIED) and fills 36 slots with up to 4 stacks per item. A player with big piles of stone, logs or dirt fills the mirror with about 9 bulk items, so rarer alchemy and cooking ingredients never reach the bench. This is VERIFIED code behaviour; the in-play effect is UNVERIFIED.
- **Timed benches** (Campfire, Furnace, Tannery): the bag link cannot supply their inputs (VERIFIED, section 1.4). At those windows it only helps bench tier upgrades (`CraftingManager.startTierUpgrade` reads the extra section, VERIFIED). That is a small bonus, UNVERIFIED in play.

### 7.3 Smallest changes

1. **Bench-aware mirror (recommended, SkyySacks 0.7.3, small).**
   - In `CraftLinkTask`, for a `BenchWindow`, get the bench from `((BlockWindow) w).getBlockType().getBench()` and its recipes from `CraftingPlugin.getBenchRecipes(bench)` (static, VERIFIED).
   - Build a `wanted` set: the input `getItemId()` values, plus the input `getResourceTypeId()` values matched through `Item.getResourceTypes()`. Cache it per bench id.
   - `rebuild(caps, wanted)` fills wanted items first (1 stack each, then a second pass), then the rest by count as today.
   - At the Alchemy Bench (30 recipes, VERIFIED) and the Cooking Bench (22, VERIFIED) every sack-able ingredient then fits in the 36 slots. The Cooking spec's three campfire-dish recipes (25 in all) are picked up by the same per-bench scan with no extra code (UNVERIFIED until their Variant items load). The signature cache (`m.sig`) keeps it cheap.
2. **Campfire and Furnace from sacks (optional `[SKYY?]`, new behaviour).**
   - While a player has a `ProcessingBenchWindow` open, `CraftLinkTask` could top up each **non-empty** input slot of `getItemContainer().getContainer(1)` from the pool, for sack items of a carried category. It adds with `addItemStackToSlot`, verifies by recount, and only then does `SackPool.add(k, id, -added)`. That is the sweep's counted-transaction rule, with one `CraftLog` line.
   - The player starts it by placing one item, so nothing appears in a shared furnace uninvited.
   - Not needed for smelting: the SkyySacks Furnace tab already takes ore from bags (`procQueue` uses `materials(p, k)` = inventory + `BagMirror`, VERIFIED).
   - The Campfire has 3 one-input recipes, so pulling from `/pd` first is a minor chore.
   - Recommendation: skip for now and revisit if Skyy asks.

---

## 8. Test checklist for Skyy

Deploy together: SkyySkills 0.4 (with the Alchemy spec), SkyySacks 0.7.3, SkyyAccessories 0.4.2. Reconnect is enough.

**Vanilla Furnace (SkyySkills)**
1. Server log shows "[SkyySkills] 0.4 ready" and no "SmeltSys failed" lines. `xp.properties` holds the section 2.6 smithing lines once (copper = 5, `Ingredient_Charcoal=0`), not the Alchemy draft's copper = 10.
2. Place a Furnace in survival, smelt 5 copper ore, drag the 5 bars into your inventory: "+25 Smithing XP" (5 x 5).
3. Smelt 5 more and **shift-click** them out: +25 again. Smelt 3 more, then double-click a copper bar in your inventory to gather: +15.
4. Try to drag bars from your inventory **into** the output slots: refused. Put a bar back into the input: refused (not a valid ingredient).
5. Smelt 2 stone into smoothed rock, take it out: +1. Put that rock into the **input** slot and take it back: +0.
6. Let fuel make charcoal (it appears after 2 logs of fuel) and take it out: +0 Smithing.
7. Throw bars from the output onto the floor and pick them up: +0 (collect into your inventory to get XP).
8. With a second account at the same furnace: whoever takes the bars gets the XP, and the other gets nothing.
9. Salvage bench: salvage a copper sickle and take the ore out: +0 Smithing. Tannery leather: +0. Campfire: cook a raw fish and take it out: +0 Smithing and +0 Cooking (the Cooking spec's test 12).
10. Creative mode: take bars out: +0.
11. Profile switch (with SkyyProfiles): smelt on profile 1, switch, collect. The XP goes to the active profile shown in `/skills`.

**SkyySacks Furnace tab**

12. Queue 10 copper ore in `/craft` -> Furnace. As units finish: +5 per bar (+50 total), with `SMITHING ...` lines in `crafts.log`.
13. Queue 20, cancel after 5 finish: only 5 bars' XP. Unload fuel: no XP.
14. Queue 60 iron, log out for 15 minutes, log in: one "+N Smithing XP" line for everything that finished (8 per bar). `/skills stats smithing` shows it.
15. Collect the bars: no second XP payment.

**Accessories retired (SkyyAccessories + SkyySacks)**

16. An owned Alchemy Bench Accessory II in the inventory shows "(retired)"; Equip is refused with the table-use message and the item stays in the inventory.
17. An already-equipped Cooking Bench / Campfire / Alchemy accessory shows "retired, does nothing". `/craft` has no Alchemy tab, and no cooked food or cooking recipes appear in Crafting. Unequip returns the item.
18. The Omni still shows all other benches in `/craft`, and not alchemy or cooking recipes. The Omni recipe at a Workbench now asks for 10 accessories.
19. `/craft` Collections tab: no potions, no cooking and no furnace or salvage recipes, even if collections unlocked them.
20. There is no way to craft a new Alchemy, Cooking or Campfire accessory (not listed at the Workbench).

**Sack draw at the tables**

21. Alchemy Bench with berries and petals only in your Farming bag and a glass vial in your inventory: the Lesser Health Potion shows as craftable. Brew 1: the bag count drops by the ingredients, and the Alchemy spec's "+50 Alchemy XP" appears.
22. Cooking Bench with raw meat and sticks only in bags: craft a Meat Kebab; the bag counts drop.
23. With 20,000+ cobble in the Mining bag, the Alchemy Bench still sees the potion ingredients (bench-aware mirror).
24. Campfire / Furnace windows: the smelting inputs do not fill from bags (expected). Upgrading the Furnace tier with bars only in bags: note whether it works (a bonus, not required).
