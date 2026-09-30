# Durability switch - research (2026-09-30)

Skyy (2026-09-30, OPEN-QUESTIONS "LOCKED 2026-09-30"): *"make durability a toggle in the server setup settings. off by default. so your
tools/ weapons, and armor never break."* -> one Server Setup switch **Item durability**, default **OFF**. OFF = tools, weapons and armor
never lose durability (so never break). ON = vanilla. Items that are already worn keep their durability (no auto-repair).

Everything below was read from the live `HytaleServer.jar` (Implementation-Revision-Id d2feeb39...) and `Assets.zip` with the tools/dev
helpers (callers.py, bcfull2.py, reflect.py, cpgrep.py + two small scratch scripts), in a bare JVM. Nothing was built or deployed.

## 0. Answer in one paragraph

There is **no engine switch** for durability (GameplayConfig `ItemDurability` only holds `BrokenPenalties`) and **no event to cancel**.
But every vanilla durability loss takes its amount from **one of four numbers on loaded assets** (`Item.durabilityLossOnHit`,
`ItemTool$DurabilityLossBlockTypes.durabilityLossOnHit`, `BlockSelectorToolData.durabilityLossOnUse`,
`ModifyInventoryInteraction.adjustHeldItemDurability`), plus the death percentage the engine copies into `DeathComponent`. Recommended:
**SkyyEssentials 0.1.6** gets a live kit row `gameplay.durability` (default `false`). While it is OFF, a small class sets those asset
numbers to 0 at runtime (saving the originals), and a `RefChangeSystem<DeathComponent>` sets the death percentage to 0. Switching it ON
puts the saved numbers back. No item stack is ever rewritten, no metadata is touched, and the SkyyGear rolls, the client and the other
mods do not notice. Damaged items stay as they are. A "repair gear of online players" admin action is trivial and safe, so it is
offered as a separate, optional action.

---

## 1. How durability is stored (bytecode)

- **Per stack, saved with the item.** `ItemStack` fields `durability` and `maxDurability`, `ItemStack.CODEC` keys `Durability` and
  `MaxDurability` (`ItemStack.<clinit>`, ldc "Durability" at 115, "MaxDurability" at 157). A new stack copies the item's
  `Item.getMaxDurability()` into both (`ItemStack.<init>(String,int,BsonDocument)` offsets 86-108). So changing an item asset's
  MaxDurability later does **not** change stacks that already exist.
- `ItemStack.isUnbreakable()` = `maxDurability <= 0`. `ItemStack.isBroken()` = `!isUnbreakable() && durability == 0`.
- `ItemStack.withDurability(d)` = a new stack with `clamp(d, 0, maxDurability)`, the same id, quantity, quality and **metadata**.
  `withIncreasedDurability(x)` = `withDurability(durability + x)`. Stacks are immutable.
- **Item asset fields** (all `protected`, non-final; bare-JVM defaults from `new Item("Test_Item")`): `maxDurability`,
  `durabilityLossOnHit` (default 0), `durabilityLossOnDeath` (default **true**), `repairable` (default true), `consumable` (default false).
  Public getters: `getMaxDurability`, `getDurabilityLossOnHit`, `getDurabilityLossOnDeath`, `isRepairable`, `isConsumable`.
- Tool block costs: `Item.getTool().getDurabilityLossBlockTypes()` -> `ItemTool$DurabilityLossBlockTypes[]` (block types / block sets +
  `durabilityLossOnHit`). Hammer cost: `Item.getBlockSelectorToolData().getDurabilityLossOnUse()`.

Vanilla items with durability (Assets.zip, Parent chains resolved): 117 armor pieces, 155 weapons, 22 hatchets/pickaxes/bark scraper,
5 shovels, 4 hoes, 4 sickles (in the weapon count), 2 hammers. **Shields have no MaxDurability** (all 17 `Weapon_Shield_*` resolve to
none), gliders none. Typical costs: sword 0.21 per hit, axe 0.56, battleaxe 0.45, shortbow 0.58, armor 0.5-1 per hit, pickaxe/hatchet
0.25 per block, shovel 0.05 per block, hammer 1 per block-set switch.

**Durability that is NOT wear (must keep working):** watering cans (per-state MaxDurability 20/50, `Repairable:false`,
`DurabilityLossOnDeath:false`), buckets, mugs and tankards (`Consumable:true` and/or `DurabilityLossOnDeath:false`, emptied through
`BrokenItem`), fertilizer (5 uses, `DurabilityLossOnDeath:false`), Bandage_Potion_Test. In vanilla every "charges / fill level" item
sets `DurabilityLossOnDeath:false`; every wear item keeps the default `true`.

## 2. Every way durability is lost

### 2.1 The common gate

`ItemUtils.canDecreaseItemStackDurability(Ref, ComponentAccessor)` (whole method):
```
0-10:  Player p = accessor.getComponent(ref, Player.getComponentType())
14-15: p == null -> return false            (NPCs never lose durability)
19-33: return p.getGameMode() != GameMode.Creative
```
It is only a per-player Creative check. It cannot be used as a server switch.

### 2.2 The loss paths (complete list of writers)

`callers.py com/hypixel` for `withDurability`, `withIncreasedDurability`, `withRestoredDurability`, `withMaxDurability`,
`updateItemStackDurability`, `decreaseItemStackDurability`, `canDecreaseItemStackDurability` and the durability constructors of
`ItemStack` finds exactly these durability-lowering sites (everything else is a reader, a repair, a refill or /give):

| # | Trigger | Engine site (bytecode offset) | Amount comes from | Gate |
|---|---|---|---|---|
| L1 | **Weapon hits** (melee, and every projectile impact: `Damage$ProjectileSource extends Damage$EntitySource`, so the shooter's *currently held* item loses again on hit) | `DamageSystems$DamageAttackerTool.handle`: `cause.isDurabilityLoss()`@5, source instanceof EntitySource@20, hotbar active slot@76, `ItemUtils.decreaseItemStackDurability(attacker, itemInHand, -1, slot)`@105 | `Item.getDurabilityLossOnHit()` of the held item, only when it has a `Weapon` (or `Armor`) config (`decreaseItemStackDurability`@134-155) | canDecrease@3 of decrease, cause flag |
| L2 | **Armor when hit** (any cause with DurabilityLoss: Physical, Projectile, Environment = fall, drowning, suffocation, out-of-world, Environmental = cactus/bushes) | `DamageSystems$DamageArmor.handle`: `cause.isDurabilityLoss()`@16, armor container@30, one random non-broken piece@87, `decreaseItemStackDurability(victim, piece, -3, slot)`@110 | `Item.getDurabilityLossOnHit()` of that piece (`decrease`@65-86; if it broke: `StatModifiersManager.scheduleRecalculate()`@128) | same |
| L3 | **Tool breaking / damaging blocks** | `BlockHarvestUtils.applyItemDurabilityLoss`: `!isUnbreakable`@9, canDecrease@19, hotbar active slot@49, `calculateDurabilityUse(item, blockType)`@59, `updateItemStackDurability(-loss)`@81. Called from `damageSingleBlock`@2179 and `performBlockDamage`@305 (per swing / per block of a break shape); callers `BreakBlockInteraction.interactWithBlock`, `ExplosionUtils.processTargetBlocks` | `calculateDurabilityUse`: soft block -> 0; no Tool -> 0; no DurabilityLossBlockTypes -> `Item.getDurabilityLossOnHit()`@50; else the matching entry's `durabilityLossOnHit`@171/@233, fallback `Item.getDurabilityLossOnHit()`@250 | canDecrease, unbreakable |
| L4 | **Bows / crossbows / launchers firing** | `LaunchProjectileInteraction.firstRun`: canDecrease@327, `!isUnbreakable`@335, `getWeapon()!=null`@343, `updateItemStackDurability(-lossOnHit)`@385; a broken launcher gives the projectile `BrokenPenalties.getWeapon`@415 | `Item.getDurabilityLossOnHit()` | canDecrease, unbreakable |
| L5 | **Hammer cycling a placed block** | `CycleBlockGroupInteraction.interactWithBlock`: canDecrease@322, `!isUnbreakable`@330, `updateItemStackDurability(-lossOnHit)`@360 | `Item.getDurabilityLossOnHit()` (0 on vanilla hammers) | canDecrease |
| L6 | **Hammer switching the held block set** (packet `SwitchHotbarBlockSet`) | `InventoryPacketHandler.lambda$handle$2`: canDecrease@321, `!isUnbreakable`@329, `updateItemStackDurability(-durabilityLossOnUse)`@349 | `BlockSelectorToolData.getDurabilityLossOnUse()` (1.0 on Tool_Hammer_Crude) | canDecrease |
| L7 | **Interaction assets** `ModifyInventory` with `AdjustHeldItemDurability` | `ModifyInventoryInteraction.firstRun`: only `requiredGameMode`@31-70 (no canDecrease: works in Creative too unless RequiredGameMode is set); `adjustHeldItemDurability == 0 -> return`@239-248; `held.withIncreasedDurability(adjust)`@267; broken -> `BrokenItem` ("Empty" removes, another id replaces)@295-355; break message + `SFX_Item_Break`@415-502; `setItemStackForSlot`@516 | the interaction's own `adjustHeldItemDurability` (table 2.3) | RequiredGameMode only |
| L8 | **Death** | `DeathSystems$DropPlayerDeathItems.onComponentAdded`: Creative -> skip@34-46; `pct = DeathComponent.getItemsDurabilityLossPercentage()`@61, `> 0`@66; every non-empty, non-broken stack of `InventoryComponent.EVERYTHING` whose `Item.getDurabilityLossOnDeath()`@125 -> `withIncreasedDurability(-maxDurability * pct / 100)`@136-149 -> `CombinedItemContainer.replaceItemStackInSlot`@162 | `DeathSystems$PlayerDropItemsConfig` copies `World.getDeathConfig()` (the world's `DeathConfigOverride`, else GameplayConfig `Death`) into the component (`setItemsDurabilityLossPercentage`@39). Default.json: **10 %** of max per death | Creative, item flag |
| L9 | Other plugins calling the public `ItemUtils.updateItemStackDurability` / `LivingEntity.updateItemStackDurability` / `withDurability` themselves | - | whatever the plugin passes | - |

`ItemUtils.updateItemStackDurability` (L1-L6 all end here): `stack.withIncreasedDurability(delta)`@3 ->
`container.replaceItemStackInSlot(slot, old, new)`@14 -> when the new stack is broken and the old was not: red chat line
`server.general.repair.itemBroken` + `SFX_Item_Break` (UI)@24-100.

Not durability losses: `RefillContainerInteraction` (sets the fill level of cans/buckets up), `RepairItemInteraction` (repair kit:
`withRestoredDurability(newMax)` = durability and max both set to a new, penalised max@196-223), `GiveCommand` (`/give ... durability`),
`ItemStack.cleanCopy/withQuantity/withMetadata/...` (copy the fields). **Fishing does not exist in this build** (no class). Shields: no
durability; a shield bash hits through L1, which wears the **main-hand** hotbar item, not the shield.

### 2.3 Vanilla `ModifyInventory` durability costs (Assets.zip, all 21 files)

| Interaction (file) | Adjust | BrokenItem | What it is | Rule R1 below |
|---|---|---|---|---|
| Hatchet_Chop_Damage (hatchets, Tool_Bark_Scraper via Scraper_Chop) | -1 | - | hatchet hitting an entity (tools have no Weapon config, so L1 skips them) | zero |
| Pickaxe_Mine_Damage | -1 | - | pickaxe hitting an entity | zero |
| Hoe_Till | -1 | - | tilling soil | zero |
| Sickle_Swing_Left_Selector / _Right_Selector | -1 | - | sickle harvesting a crop (HarvestCrop `RequireNotBroken`) | zero |
| Ice_Staff_Primary_Entry, Weapon_Staff_Crystal_Ice (inline) | -0.5 | - | staff cast (RequiredGameMode Adventure + Ice Essence) | zero |
| Weapon_Stick_Fire_Projectile_Charged_0..3, Weapon_Stick_Fire_Secondary_Entry | -0.5 | - | fire stick casts | zero |
| Debug_Durability_Condition_Primary | -1 | - | debug item | zero |
| Consume_Charge_Durability (2 inline: the `DurabilityModify` default and the `Failed` branch) | -1 | - | drink charges (Food_EffectCondition_Drink) | zero (the one deviation, see 5.3) |
| Fertilizer_Use | -1 | Empty | fertilizer charges | keep |
| Watering_Can_Use, Watering_Can_Use_3x3 | -1 | Tool_Watering_Can | water level | keep |
| Container_Bucket x3, Deco_Bucket x3, Deco_Mug, Deco_Tankard (inline) | -1 | the empty item | fluid / drink charges | keep |

## 3. The knobs that exist (and why none of them is a switch)

- **GameplayConfig `ItemDurability`** = `ItemDurabilityConfig` with only `getBrokenPenalties()` (reflect). `BrokenPenalties.getWeapon /
  getArmor / getTool(double)` = what a *broken* item still does (Default.json 0.75 each; read by `DamageCalculatorSystems`@74-98,
  `ArmorDamageReduction`, `StatModifiersManager.computeStatModifiers`, `BlockHarvestUtils.damageSingleBlock`@773-800,
  `LaunchProjectileInteraction`@405). It does not stop any loss.
- **GameplayConfig `Death`** `ItemsDurabilityLossPercentage` (Default.json 10; ForgottenTemple / Portal use ItemsLossMode None) - death
  only (L8), and a world may override it (`WorldConfig.getDeathConfigOverride()`, `World.getDeathConfig`@1-23).
- **DamageCause `DurabilityLoss`** (Server/Entity/Damage: Physical, Projectile, Environment, Environmental = true; Command = false;
  field `protected boolean durabilityLoss`) - L1 + L2 only. Only `DamageArmor` and `DamageAttackerTool` read it.
- Item flags `MaxDurability`, `DurabilityLossOnHit`, `DurabilityLossOnDeath`; tool `DurabilityLossBlockTypes`,
  `BreakShapeDurabilityMode` (PerSwing / PerBlock); hammer `DurabilityLossOnUse`; interaction `AdjustHeldItemDurability`.
- **No cancellable event.** `cpgrep urability` lists no durability event. `InventoryChangeEvent` (ECS) only has getters and is queued:
  `InventorySystems$InventoryChangeEventSystem.tick` polls `InventoryComponent.getChangeEvents()` and `CommandBuffer.invoke`s it on a
  later tick. `ItemContainer$ItemContainerChangeEvent` is dispatched synchronously by `ItemContainer.sendUpdate` (after the write,
  per container, `registerChangeEvent`). Both arrive after the change.
- The old global `LivingEntityInventoryChangeEvent` **no longer exists** in this jar (see 6: Serilum's DisabledDurability used it).

## 4. The options, ranked

| Rank | Mechanism | Covers | Reliability | Compatibility | Effort |
|---|---|---|---|---|---|
| **1 (recommended)** | **Zero the costs at runtime**: reflection sets the 4 asset numbers to 0 while OFF (originals saved, put back when ON) + a DeathComponent system for L8 | L1-L8 (and L9 plugins that read those numbers, e.g. vein-mining, SimpleEnchantments) | high: every vanilla path multiplies one of those numbers; with 0 nothing changes (`updateItemStackDurability(-0.0)` writes an identical stack, `ModifyInventory` returns at 248, no break message) | high: no stack rewrite, no metadata, no extra events, modded items are covered (they are Item assets), client gets nothing new | low-medium (one class, one system, 2 listeners, 1 row) |
| 2 | **Restore after the loss** (ECS `InventoryChangeEvent` or per-container `registerChangeEvent`: same id / qty / max / metadata, lower durability -> put the old value back) | L1-L9 | medium: the engine has already sent the break chat line + `SFX_Item_Break` when an item at < one hit of durability reaches 0, and restoring it to the tiny value makes **every following hit** spam the break line again (costs are 0.05-1 per use); one-tick dip | medium: any other code that replaces a stack with a more worn copy of the same item in the same slot gets "repaired" (false positive); doubles armor-container events (SkyyGear's GearFxInvSys runs twice per hit); charge items need a filter | medium |
| 3 | **Early plugin ClassTransformer** patching `ItemUtils.canDecreaseItemStackDurability`, `ModifyInventoryInteraction.firstRun`, `DropPlayerDeathItems` | all, exact | highest | low: needs an `earlyplugins/` folder and `--accept-early-plugins` on a dedicated server (auto-accepted only with `--singleplayer`), prints "This is unsupported and may cause stability issues" (`EarlyPluginLoader.loadEarlyPlugins`@189-285), breaks on engine updates, not deployable through `UserData/Mods` | high | 
| 4 | Flip every `DamageCause.durabilityLoss` to false | L1, L2 only | partial | ok | low |
| 5 | Unregister `DamageArmor` / `DamageAttackerTool` (`ComponentRegistry.unregisterSystem(Class)` exists) | L1, L2 only | fragile, re-registering an engine system from a plugin ties it to the plugin | poor | medium |
| 6 | Asset-pack override (JSON: DurabilityLossOnHit 0 / MaxDurability 0 on every item) | new stacks only for MaxDurability; no modded items | not a runtime toggle (restart + pack switch) | copies vanilla files (project rule), per-stack MaxDurability means old stacks keep breaking | medium |
| 7 | A GameplayConfig value | death only (`ItemsDurabilityLossPercentage`) | - | - | - |
| 8 | Creative mode / per player | - | not an option | - | - |
| 9 | Serilum "DisabledDurability" style (refill every slot to max on every inventory change) | - | the event it uses is gone from this engine | auto-repairs (against Skyy's rule) and would refill watering cans / buckets | - |

## 5. Recommended design (for the SkyyEssentials 0.1.6 builder)

### 5.1 The row

- New kit category `("gameplay", "Gameplay")` (id <= 16, label <= 20).
- Row `gameplay.durability`, label **"Item durability"** (15), type `bool`, default `"false"`, flags `live,danger` with
  `confirm=on` (turning it ON asks: "Turn item durability ON? Tools, weapons and armor wear out and can break again." - 79 chars),
  help (98): "Off: tools, weapons and armor never lose durability or break. Worn items keep their current value."
- Binding `field:EssDur.ON@config.properties:gameplay.durability;after=EssDur.changed` (`public static volatile boolean ON = false`;
  TCfg appends `gameplay.durability=false` to older files, like 0.1.5's `privacy.staffBypass`). First 0.1.6 start = OFF at once.
- Because a `field:` value can also arrive through hand edit + reload, import, restore and undo, add a 1-second idempotent watcher on
  `HytaleServer.SCHEDULED_EXECUTOR` (`if (ON == appliedOn) return; apply(ON)`) next to `after=`. The watcher alone would be enough.

### 5.2 EssDur.apply(boolean on) - the whole switch

One `synchronized (EssDur.class) { applyLocked(on); }` (javassist: one call inside). Keep an `IdentityHashMap` object -> `Double` original
(explicit `new Double(...)`, no autoboxing) per point, so ON restores exactly what was there.

1. `Item.getAssetMap().getAssetMap().values()` (iterator loop): for every Item with `durabilityLossOnHit != 0` record + set 0
   (`Field Item.durabilityLossOnHit`, `setAccessible(true)`, `setDouble`). Covers L1, L2, L4, L5 and the L3 fallback.
2. Same Items: `getTool() != null && getTool().getDurabilityLossBlockTypes() != null` -> each entry's `durabilityLossOnHit` (L3).
3. Same Items: `getBlockSelectorToolData() != null` -> `durabilityLossOnUse` (L6).
4. `Interaction.getAssetMap().getAssetMap().values()`: every `ModifyInventoryInteraction` with `adjustHeldItemDurability < 0` **and
   `brokenItem == null`** (rule R1, table 2.3) -> record + set 0 (L7). Inline interactions are in this map too (`SimpleInteraction.next /
   failed` are String ids; generated ids follow `AssetExtraInfo`'s `"*<root>_<key>"` pattern).
5. ON: write every recorded original back, clear nothing (the map stays so a second OFF finds the same originals).

Log one INFO line per change: `Item durability OFF: <a> hit costs, <b> tool block costs, <c> hammer costs, <d> interaction costs set
to 0` (the counts come from the live asset maps; vanilla alone has 26 tool files with DurabilityLossBlockTypes, 1 hammer with
DurabilityLossOnUse and 16 ModifyInventory costs that R1 zeroes). A missing field (engine update) -> one warning, the switch reports
itself unavailable; never throw.

Bare-JVM proof (scratch probe, deleted): reflective `setDouble` on `Item.durabilityLossOnHit`, `DurabilityLossBlockTypes
.durabilityLossOnHit`, `BlockSelectorToolData.durabilityLossOnUse` and `ModifyInventoryInteraction.adjustHeldItemDurability` works and
the engine's own getters (`getDurabilityLossOnHit`, `getDurabilityLossOnUse`) return the new values. None of these fields is final.

### 5.3 Rule R1's one deviation

`Consume_Charge_Durability` has two `ModifyInventory -1` without BrokenItem. Every vanilla drink item with durability (mug, tankard,
buckets) overrides the `DurabilityModify` var with its own BrokenItem version, so only the chain's `Failed` branch still uses a zeroed
cost: while durability is OFF an interrupted drink does not use up a charge. Harmless and in the player's favour. If Skyy wants it
exact, also keep instances whose id starts with `*Consume_Charge_Durability` (id format UNVERIFIED - log the zeroed ids once at start).
Third-party charge items that use ModifyInventory without BrokenItem would also stop using charges while OFF (none on the SkyWynn set).

### 5.4 Death (L8)

`EssDurDeath extends RefChangeSystem` (precedent: SkyyCollections): `componentType()` = `DeathComponent.getComponentType()`,
`getQuery()` = `Player.getComponentType()`, `getDependencies()` = `{ new SystemDependency(Order.AFTER,
DeathSystems$PlayerDropItemsConfig.class), new SystemDependency(Order.BEFORE, DeathSystems$DropPlayerDeathItems.class) }` (both
`public static`; the engine's own pair is `PlayerDropItemsConfig BEFORE DropPlayerDeathItems`), `onComponentAdded`: `if (!EssDur.ON)
comp.setItemsDurabilityLossPercentage(0.0)`; set/removed empty. It runs on the world thread. The respawn page then reads "0%"
(`RespawnPage.build`@154-178 prints `server.general.itemsDurabilityLoss` with the component's percentage). This also catches per-world
`DeathConfigOverride`s, which zeroing the GameplayConfig assets would miss. One `registerSystem` for the class.

### 5.5 Lifecycle

- `HytaleServer.boot`: `PluginManager.setup()`@80 -> `LoadAssetEvent` (all packs, mods included)@131-154 -> `PluginManager.start()`@444.
  So: `setup()` registers the system and the two listeners; **`start()` calls `apply(ON)`** (every asset is loaded by then).
- `getEventRegistry().register(LoadedAssetsEvent.class, Item.class, consumer)` and the same for `Interaction.class` (the vanilla
  CraftingPlugin pattern, `EventRegistry.register(Class, Object, Consumer)`): ignored before `start()`; after it (asset editor / hot
  reload) re-run `apply(ON)`, which records originals only for objects it has not seen. Consumers are small classes, no lambdas.
- Known edge: an asset hot-reloaded **while OFF** whose parent is a zeroed item inherits 0 and would stay 0 after switching ON.
  Only happens with runtime asset reloads; a restart fixes it.

### 5.6 Build probes (B.probe / pool field checks)

`Item.durabilityLossOnHit`, `ItemTool$DurabilityLossBlockTypes.durabilityLossOnHit`, `BlockSelectorToolData.durabilityLossOnUse`,
`ModifyInventoryInteraction.adjustHeldItemDurability` + `brokenItem` (fields); `Item.getAssetMap`, `Item.getTool`,
`ItemTool.getDurabilityLossBlockTypes`, `Item.getBlockSelectorToolData`, `Interaction.getAssetMap`, `AssetMap.getAssetMap`,
`DeathComponent.setItemsDurabilityLossPercentage`, `DeathSystems$PlayerDropItemsConfig`, `DeathSystems$DropPlayerDeathItems`,
`LoadedAssetsEvent`, `EventRegistry.register(Class,Object,Consumer)`.

### 5.7 Behaviour

OFF: no weapon, armor, tool, bow, hammer, hoe, sickle, staff or death wear for anyone; NPCs never had any; Creative unchanged. Crafted
items still come at full durability. Watering cans, buckets, mugs, fertilizer and food charges still run out. Broken items stay broken
and keep the vanilla BrokenPenalties (x0.75). Vanilla repair kits still work (and still lower MaxDurability). ON: exactly vanilla.

## 6. Items that are already worn or broken

They keep their value (nothing in 5.2 touches a stack). A repair **is** trivial and safe for the inventories of online players, so offer
it as a separate optional action row (not part of the switch):

- `gameplay.repairOnline`, label "Repair gear of online players" (29), `action`, flags `danger` (`confirm=always`), help (98):
  "Fills worn tools, weapons and armor of everyone online to full. Cans, buckets and charges skipped."
- For each online player, on **their world thread** (`world.execute`): `InventoryComponent.getCombined(store, ref,
  InventoryComponent.EVERYTHING)`, each slot where `stack.getMaxDurability() > 0 && stack.getDurability() < stack.getMaxDurability()`
  and the Item is wear (`getArmor() || getWeapon() || getTool() || getUtility() || getBlockSelectorToolData()` non-null,
  `isRepairable()`, `!isConsumable()`, `getDurabilityLossOnDeath()` - skips cans, buckets, mugs, fertilizer) ->
  `replaceItemStackInSlot(slot, stack, stack.withDurability(stack.getMaxDurability()))` (compare-and-set: a slot that changed meanwhile
  is left alone; the engine's death code writes the same way@162). `withDurability` keeps id, quantity, quality, metadata (SkyyGear
  rolls) and the current, possibly repair-lowered max. Then `EntityStatMap.getStatModifiersManager().scheduleRecalculate()` when an
  armor piece changed (what the engine does when armor breaks). Answer "working on it", then "Repaired N items for M players".
- Not covered (not trivial): offline players, chests, SkyyVault/SkyyProfiles snapshots, auction listings, dropped items.

## 7. SkyyGear

- SkyyGear 0.1 (live) / 0.1.1 multiply armor lock amounts by `BrokenPenalties.getArmor(0.0)` when `stack.isBroken()`
  (`GearArmor.addSums` / `brokenFactor`, mirroring `StatModifiersManager.computeStatModifiers`). The switch does not touch BrokenPenalties
  and makes no new broken pieces, so pieces broken before stay x0.75 in both the engine and SkyyGear: consistent, **no SkyyGear change**.
- No stack is rewritten, so SkyyGear metadata (rolls, identify state) is never touched; the craft-roll "full durability" signature is
  unaffected. Armor hits still write an identical stack (vanilla already fires one armor-container change per hit), so GearFxInvSys
  load is unchanged. After the optional repair action, SkyyGear re-evaluates on that armor change (lower-only) and on GearTick (<= 1 s).
- SkyyGear must not add its own durability code; if it ever needs the state it reads `config:fn:SkyyEssentials` op `get
  gameplay.durability` over the bridge.

## 8. Which mod owns the switch: SkyyEssentials

- It is a server-wide rule for vanilla items and must work without SkyyGear (SkyyGear is the optional rolled-gear system).
- SkyyEssentials already carries server-wide parts on the config kit (kit 1.1, `config.properties`, TCfg appends new keys, Server
  Setup page "Essentials") and is patch-based: next version = `tools/essentials_0_1_6_patch.py` reading
  `SkyyEssentials/build_skyyessentials_0.1.5.py` (the SET pin; no 0.1.6 patch exists yet).
- One owner avoids two mods zeroing and restoring the same asset numbers. Without SkyyEssentials a server simply has vanilla durability.

## 9. Other mods seen in UserData/Mods (read only, nothing copied)

- **vein-mining 2.4.0** calls `updateItemStackDurability` with `getDurabilityLossOnHit`, **SimpleEnchantments 1.2.0** reads
  `getDurabilityLossBlockTypes` / `getDurabilityLossOnHit` / `canDecreaseItemStackDurability`: both follow the zeroed numbers.
- **Perfect Parries 0.9.4** applies its own configured `parryDurabilityLoss` with `withDurability`: not covered (not on the SkyWynn set).
- **Serilum DisabledDurability 1.0** (server 2026.02.19, needs Serilum:Hybrid): on `LivingEntityInventoryChangeEvent` it sets every slot
  below max back to max (auto-repair, refills charge items). That event class is gone from this engine; it is disabled in every local
  world. Do not enable it next to the switch.

## 10. In-game tests (after a 0.1.6 build; game closed for deploy)

1. Fresh start of 0.1.6: Server Setup -> Essentials -> Gameplay shows "Item durability" OFF; `config.properties` has
   `gameplay.durability=false`; the server log has the "Item durability OFF: ... set to 0" line.
2. OFF, note each item's durability bar/tooltip before and after: sword and axe hits on a mob; shortbow shot + arrow hit; crossbow shot;
   take mob hits, fall damage and cactus damage in full armor; mine stone (pickaxe), chop a log (hatchet), dig (shovel); hatchet and
   pickaxe hitting a mob; till with a hoe; harvest with a sickle; ice staff / fire stick casts; hammer: switch the held block set and
   cycle a placed block. Nothing may change, no "item broken" chat line, no break sound, no flicker of the bar.
3. OFF: die with worn gear (Default gameplay) -> the respawn page reads 0 % durability loss; after respawn every item has its old value.
4. OFF: watering can runs dry after its uses, a water bucket empties when placed, a mug drink uses a charge, fertilizer runs out after
   5 uses, food still consumes.
5. An item that was already worn keeps its value; an already broken sword stays broken (lower damage) and an already broken armor piece
   keeps its lower stats (SkyyGear locks included).
6. Switch ON in Server Setup (confirm question shows): the same actions as step 2 wear items again at once; die -> 10 %. Switch OFF: wear
   stops at once, values stay where they were.
7. Change the value by hand in `config.properties` + the kit reload, and by `/modconfig` undo: the switch follows within 1 s.
8. Restart with OFF and with ON: the state survives.
9. Another world / instance (e.g. a portal or dungeon instance): same result as step 2.
10. SkyyGear: a rolled weapon and rolled armor keep their rolls and tooltip after 50 hits; armor locks unchanged.
11. Optional action "Repair gear of online players" (if built): worn gear of two online players goes to full, a SkyyGear-rolled item
    keeps its rolls, a watering can / bucket / fertilizer is not refilled, armor stats update, the chat answer counts the items.
12. Creative player: unchanged (vanilla already never wears in Creative, except RequiredGameMode-less ModifyInventory - now also 0).

## 11. UNVERIFIED

1. The client keeps the old `adjustHeldItemDurability` (ModifyInventory packets are cached, `Interaction.cachedPacket`) and
   `BlockSelectorToolData.durabilityLossOnUse` it received at login. Inventory is server-authoritative, so no client-side dip is expected
   - test step 2 (hammer, hatchet on a mob, hoe) checks it.
2. Whether the kit calls `after=` on hand edit / reload / import (hence the 1-second watcher).
3. The generated inline-interaction id format (only for the optional Consume_Charge keep rule).
4. RefChangeSystem ordering against the DeathSystems pair works as declared (standard dependency API, precedent in SkyyExploration /
   SkyyCollections, not run).
5. Asset hot-reload while OFF (5.5 edge).
6. Everything in section 10.

## 12. Method

Commands (inside tools/dev, TEMP/TMP in the scratch folder, `-XX:-UsePerfData`): `cpgrep.py urability`; `callers.py com/hypixel` with the
durability method names; `bcfull2.py` / a scratch `bcany.py` (constructors and `<clinit>`) on every site in 2.2; `reflect.py` + a
scratch field lister for Item, ItemTool$DurabilityLossBlockTypes, BlockSelectorToolData, ModifyInventoryInteraction, DamageCause,
DeathConfig, DeathComponent, InventoryChangeEvent, ItemContainer, LoadedAssetsEvent, RefChangeSystem, EarlyPluginLoader; Assets.zip
JSON scans (GameplayConfigs, Entity/Damage, every item's durability fields with Parent chains resolved, every `AdjustHeldItemDurability`
/ `DurabilityLossBlockTypes` / `DurabilityLossOnUse` / `DurabilityLossOnDeath`); a bare-JVM probe of the reflective writes; a read-only
scan of UserData/Mods constant pools and of the local worlds' `config.json`. The scratch folder tools/dev/scratch/durability was
deleted afterwards.
