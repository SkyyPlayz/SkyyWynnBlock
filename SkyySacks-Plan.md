# SKYYSACKS — RESEARCH + BUILD PLAN
*Standalone Hytale sack mod. Researched from the community SkyBlock wiki 2026-09-22.*

**Lock (2026-09-23 batch 2):** Magic Bags / sacks are **core QoL**, not an optional later feature (`SkyWynn-Decisions.md` 4.4). In play they are Magic Bags that open onto the pocket dimension (see `HANDOFF.md`). The research below is still the SkyBlock model this mod is built from.

## How SkyBlock sacks actually work (wiki-verified)
- A sack doesn't hold items like a chest — **holding it grants per-item-type capacity in a per-player pool**. Multiple sacks of the same type = capacities ADD.
- Sacks count while in **inventory or the Sack of Sacks** (most sacks; a few event sacks excepted).
- **Tiers (capacity per item type):** Small **640** · Medium **2,240** · Large **20,160** (Gemstone Sack is special-cased ~6× bigger per tier).
- **Pocket Sack-in-a-Sack**: anvil upgrade, +200% of base capacity per application, max 3 → up to 7× base.
- **Sack of Sacks**: a bag that holds sacks (upgradeable slots); sacks inside still function.
- Withdrawing = open sack, click item (like collecting a bazaar order). Quick-sell to Bazaar works even from stored sacks.
- Sacks are **untradeable** (no AH/trade/backpack-transfer) — prevents economy cheese.
- Sacks unlock via collection milestones (e.g., Mining Sack at Coal V/VII/IX per tier).
- Enchanted Sacks (Large only) store the compacted forms; work with auto-compactors.
- Category sacks: Agronomy (crops), Husbandry (animal drops), Mining, Combat, Foraging, Fishing, Gemstone, Nether, Lava Fishing, + special (Slayer/Dungeon/Rune/Spooky/Winter).

## SKYYSACKS DESIGN (Skyy's spec: auto-collect + craft-from + nesting)
**Model: per-player pool + capacity-granting sack items** (SkyBlock-faithful — much more robust than per-sack-instance storage: no dupes, no lost-item edge cases, stacking capacity for free).

1. **Sack items** (custom items, soulbound): category × tier (Small/Medium/Large). v1 categories mapped to vanilla Hytale materials, **config-driven JSON lists** so SkyWynn can re-map later:
   - Mining Sack (ores, stone, gravel...), Foraging Sack (logs, saplings, apples), Farming Sack (crops, seeds), Combat Sack (mob drops), Fishing Sack, Builder's Sack (dirt/sand/common blocks — our addition)
2. **Capacity scan**: player's sack set = inventory ∪ backpacks ∪ Sack of Sacks (recursive scan of the storage graph — Skyy's "works even in the backpack" requirement). Rescan on inventory change events, cached.
3. **Auto-pickup routing**: item pickup intercepted → if covered by an active sack and pool has room → straight into pool (with SkyyHud pickup-log hook later: "+32 Oak Log → Sack"). Overflow → normal inventory.
4. **/sacks UI** (custom page, proven framework): grid of pooled items w/ counts + capacity bars, withdraw 1/stack/all buttons, search box (Void Vault UI heritage — most of this window exists in SkyyHighPack).
5. **Craft-from-sacks**: bench-link tech from SkyyHighPack (vault→bench, IN PRODUCTION for months) pointed at the sack pool. Works from anywhere the sack is active — the headline feature.
6. **Sack of Sacks**: bag item holding sacks; contained sacks stay active. (Nested sack-of-sacks: allowed, why not.)
7. **Pocket Sack-in-a-Sack** upgrade item: +200% ×3 — v0.3.
8. SkyWynn hooks (later): sack-routed pickups still count toward **collections**; bazaar quick-sell-from-sacks; sacks unlocked by collection milestones; GFS command.

## Build phases
- **v0.1**: pool + capacity scan (inventory-only) + auto-pickup routing + /sacks UI + persistence (LayoutStore pattern) + Small/Medium/Large Mining+Foraging+Farming sacks w/ recipes
- **v0.2**: Sack of Sacks + backpack nesting scan + Combat/Fishing/Builder's sacks + withdraw QoL (search, sort)
- **v0.3**: **bench-link crafting integration** + Pocket Sack-in-a-Sack + config-driven category editing
- **v0.4**: SkyWynn integration (collections, bazaar, GFS, SkyyHud widgets: "sack value"/"sack fill" )

## Tech confidence
| Piece | Proven by |
|---|---|
| Per-player persistent pool + UI | SkyyHighPack Void Vault (in production) |
| Bench consumes from external storage | SkyyHighPack bench-link (in production) |
| Pickup interception | PJ-HyperPickup / ItemMagnet mods (in collection) — port their event hook pattern |
| Custom bag items | Extended Backpacks / rpqs-backpacks / NoCube's bags (in collection) |
| Custom items + recipes | Our packs' recipe-adder assets (in production) |
| UI pages/windows | /packsettings + Void Vault + SkyyHud editor |

Open Qs for Skyy: keep SkyBlock's exact capacities (640/2,240/20,160)? Sacks soulbound (recommended)? Auto-pickup default ON per sack with a per-category toggle in the sack UI?

---
## v0.2 page design (Skyy, 2026-09-22 — modelled on Hypixel SkyBlock's sack GUI)
- Category tabs (Mining / Foraging / Farming) as TextButtons; right-clicking a Mining sack opens on Mining (item JSON `Page.Id` = `SkyySacksMining` etc., three registered page factories). `/sacks` opens on the first non-empty category.
- Capacity line: `Mining 431 / 640` (sum of pooled items in the category vs. sack tiers carried).
- 9x4 grid of `Button` cells; a cell = `ItemIcon { ItemId }` + count label; empty cells are dim placeholders.
  Left click = withdraw a stack (64 or what is left); right click = withdraw 1. `MouseEntered` updates an info line (tooltips need `TooltipStyle` from Common.ui, not reachable from inline docs).
- Buttons: **Pick up all** (withdraw every item of the category until storage is full) and **Deposit all** (sweep storage + hotbar + backpack now, capped by capacity).
- Later: greyed cells for every item the category accepts (enumerate the item asset store by prefix), sack-of-sacks, bench link.

### Findings 2026-09-22 (late)
- Withdrawals must be exempt from the auto-sweep (10 min) or the 2s sweep re-pools them instantly; Deposit all clears the exemption. (0.3.1)
- Pool is player-owned; sack items are capacity only. Skyy: keep it ("seems helpful").
- Client hard-crashes if a page update is sent from a MouseEntered handler; hover info dropped.
- Chest-style "inventory below the page": experiment 0.3.0 uses `openCustomPageWithWindows` + `ContainerWindow(SimpleItemContainer(9))`; fallback = virtual chest via `setPageWithWindows` (many mods: Trash commands, AccessoryPouch, InvSee).

## Locked (Skyy, 2026-09-22 ~23:00): MAGIC BAGS
- Name: Magic Bag; flavor: a bag with a pocket dimension. Command `/pd` (pocket dimension), aliases `/bags`, `/sacks`.
- Strict: must carry a bag of the category to open/withdraw; pool persists per player (never lost, dropping bags is safe).
- Rarity caps each item (640 / 2240 / 20160 per item type); best bag carried; storage, hotbar or backpack all count.
- NEXT MILESTONE: crafting tables AND inventory crafting pull ingredients from the bags (SkyyHighPack vault→bench pattern).

## Crafting from bags — research notes (2026-09-22 ~23:15)
- SkyyHighPack's "vault→bench" was a hack: `VaultSystem` (EntityTickingSystem) checked `player.getWindowManager().getWindows()` for a `com.hypixel.hytale.builtin.crafting.window.BenchWindow` and, while open, `addItemStack`-ed vault items into the inventory; auto-collect swept them back. Works, but spams the inventory.
- Cleaner engine hook: `BenchWindow` and `SimpleCraftingWindow` (pocket crafting) implement `MaterialContainerWindow` -> `getExtraResourcesSection()` returns `MaterialExtraResourcesSection` with `setItemContainer(ItemContainer)`, `setExtraMaterials(com.hypixel.hytale.protocol.ItemQuantity[])`, `setValid(boolean)`, `toPacket()`; `window.invalidateExtraResources()` refreshes. Agent research running to confirm crafting CONSUMES from that container.
- Mirror container plan: per player a `SimpleItemContainer` rebuilt from the pool (one stack per item id, `min(count, ItemStack.getItem().getMaxStack())`, `setItemStackForSlot`), `registerChangeEvent(Consumer)` -> on removal transactions decrement the pool and refill on the next tick.
- CONFIRMED (agent, bytecode): `SimpleCraftingWindow.handleAction(CraftRecipeAction)` builds `CombinedItemContainer{inventory, extraResourcesSection.getItemContainer()}` and `CraftingManager` both checks and CONSUMES from it (`removeInputFromInventory`); `setExtraMaterials` is display-only; vanilla `feedExtraResourcesSection` = nearby chests; `invalidateExtraResources()` after each craft resets it (so re-apply per tick). No window-open event exists. Pocket crafting = `FieldCraftingWindow` (no hook). Implemented in 0.5.0 (untested).

## Pocket crafting — decision 2026-09-23
Pocket crafting (`FieldCraftingWindow`) computes craftability CLIENT-side from the real inventory and never sends the craft request
when greyed, so no server-side injection can make it see the bags (agent research, bytecode). Skyy rejected dumping bag
contents into the inventory (volumes far too large). DECISION: own crafting page — a **Craft tab in /pd** (+ `/craft`): lists
the Fieldcraft recipe set with have/need over inventory + bags, buttons Craft / x10 / All, crafting through
`CraftingManager.craftItem(ref, store, recipe, qty, new CombinedItemContainer{inventory, bagMirror})` (engine consumes + gives output).
### Craft page + bench accessories (Skyy 2026-09-23 morning)
Own crafting page = inventory crafting. Default tab set = Fieldcraft categories (`FieldcraftCategory.getAssetMap().getAssetMap().values()`,
`CraftingPlugin.getAvailableRecipesForCategory("Fieldcraft", catId)` -> recipe ids -> `CraftingRecipe.getAssetMap().getAsset(id)`).
Have/need via `container.countRemovableMaterial(MaterialQuantity)` on `CombinedItemContainer{inventory.getCombinedBackpackStorageHotbar(), bagMirror}`;
craft via `store.getComponent(ref, CraftingManager.getComponentType()).craftItem(ref, store, recipe, qty, combined)`.
Bench accessories: items `Skyy_Accessory_<BenchId>`; when carried (later: in the accessory bag) the page adds that bench's recipe tabs.
OPEN: whether `craftItem` rejects bench recipes when no bench window is open (agent tracing `isValidBenchForRecipe`).
Recipe SOURCES for the page (merge, dedupe): (1) Fieldcraft basics, (2) bench accessories carried, (3) collection unlocks — SkyyCollections
publishes `coll:recipes:<uuid>` (comma-separated recipe ids) via the JVM bridge; end state = no benches needed at all.
Accessory tiers (Skyy): `Skyy_Accessory_Workbench_T1/T2/T3` etc.; T(n+1) is crafted from T(n) + the same materials the real bench
needs for its tier-(n+1) upgrade (read from the bench asset's tier requirements, e.g. Workbench T2 = 30 copper bar, 20 iron, 20 ...).
Reference implementations for accessories: TerrariaAddons (AccessoryPouch, CoinPouch: ContainerWindow + filters) and
EndgameAndQoL (AccessoryPouchUI). Accessory BAG = SkyyAccessories (roster #23), but bench accessories can live in the inventory first.
- CraftingManager.craftItem validates bench recipes against `this.blockType` + a REAL placed bench block at (x,y,z) (`setBench`), so it is
  unusable for accessory-unlocked recipes. 0.6.0 crafts itself: `CraftingManager.getInputMaterials(recipe, qty)` (static) ->
  `container.canRemoveMaterials(list)` / `removeMaterials(list)` -> `SimpleItemContainer.addOrDropItemStack(store, ref, container, stack)`.
  Knowledge: `PlayerConfigData.setKnownRecipes(Set)` if we ever need vanilla to know a recipe.

## Accessory bag research (cheap agent, 2026-09-23) - copy TerrariaAddons
Reference: `Mods/TerrariaAddons-1.7.4.jar` (main `de.fevzi.TerrariaAddons.TerrariaAddons`), class
`de/fevzi/TerrariaAddons/items/accessoryPouch/AccessoryPouchSharedContainer`:
- static Map<UUID, SimpleItemContainer>; `getOrCreateContainer(Inventory, UUID)` -> `loadContainer(uuid)` reads
  `<user.dir>/AccessoryPouchData/<uuid>.json` (BsonDocument: capacity, items[{itemId, quantity, durability, maxDurability, metadata}])
  and rebuilds via `setItemStackForSlot`; `registerAutoSave` subscribes to `ItemContainer$ItemContainerChangeEvent` -> `saveContainer`.
- Open: item `AccessoryPouch.json` `Container.Capacity: 2`, `Interactions.Secondary.Interactions[0].Type = "AccessoryPouch"` ->
  class extends `OpenItemStackContainerInteraction`; `firstRun()` applies `setSlotFilter(ACCESSORY_ONLY_FILTER)` (item categories
  contain `Items.Accessories`) and opens the VANILLA container page: `setPageWithWindows(..., Page.Bench, ..., new ContainerWindow(...))`.
- Upgrades: `upgradeContainer(inventory, uuid, capacity)` builds a bigger SimpleItemContainer and copies items.
- Effects: per-accessory `EntityTickingSystem` calls `hasItemInPouch(inventory, uuid, itemId)` every tick and puts/removes an
  `EntityStatMap` modifier (StaticModifier, MULTIPLICATIVE) -> nothing to re-apply on login.
- Engine has NO accessory slots (Inventory = hotbar/storage/backpack/utility/tools/armor only). FlyRing just scans the real inventory.
Plan for SkyyAccessories 0.1: same shape - `Skyy_SkyyAccessories/<uuid>.properties` (slot=itemId), SimpleItemContainer per player,
opened by right-clicking an "Accessory Bag" item (our OpenCustomUI page or the vanilla ContainerWindow), filter = our
`Skyy_Accessory_*` ids, `hasAccessory(uuid, id)` published on the bridge as `acc:has:<uuid>` = "id,id" so the Sacks craft page
can add a `B:<Bench>` tab per carried bench accessory without a dependency.

BUILT 2026-09-23: SkyyAccessories 0.1 (bag + 30 tiered bench accessories) and Sacks 0.6.1 (tiered bench tabs from the bag). See HANDOFF.

## Change (Skyy, 2026-09-23 late): alchemy and cooking are table-only
Alchemy and Cooking are skills now, so their bench accessories go: no Alchemy Bench or Cooking Bench accessory, no Alchemy tab and no cooking recipes in /craft. You brew and cook at the real tables, and those tables draw ingredients from your sacks (the SkyySacks bag link already feeds every vanilla bench window). The Omni accessory stops counting them. Accessories already owned stay as items but do nothing (no recipe). Smelting in the furnace (vanilla Furnace and the SkyySacks Furnace tab) gives Smithing XP.
