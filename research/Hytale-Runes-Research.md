# Hytale Runes (Abilities) - Research

*Research only (2026-09-30). No code, no deploy. Written for Skyy's question: "runes are cool AF, they have ability stones and
modifiers - look into how they work, this is likely how we will make the abilities for our classes."*

Sources read (read-only):
- PRE-RELEASE = `install\pre-release\...\latest` - server jar manifest `Implementation-Version: 0.7.0-pre.4` (Chapter I "Out of the Breach").
- RELEASE = `install\release\...\latest` - `0.6.8` (what SkyWynn runs today).
- Method: full entry diff of both `HytaleServer.jar` (390 new entries, 49 gone) and both `Assets.zip` (5673 new, 793 gone, 2019 changed),
  bytecode + codec documentation strings of every new ability class (javassist dump), the new asset JSON, `server.lang` and the
  client's `client.lang` diff, and the client's own `.ui` files in `Client\Data\Game\Interface`.

Every claim is tagged **VERIFIED** (seen in bytecode or asset, source named) or **INFERRED** (reasoned, not seen running).
Nothing here has been seen in game yet. Section 7 lists what must be checked in game.

---

## 0. The short version

- "Runes" are ordinary **items with a new `Ability` block** (Hytale calls them **Runestones**). There are two kinds:
  **Ability runestones** (`"Slot": "Primary"`, Skyy's "ability stones") and **Modifier runestones** (`"Slot": "Support"`, Skyy's
  "modifiers"). VERIFIED `Server/Item/Items/Rune/**`, `ItemAbility` codec.
- Every player gets **two ability lines**, each = 1 ability slot + 2 modifier slots (6 slots total), plus a **50-slot Runestone
  Storage** bag. Both are new inventory sections saved on the player (-11 and -12). VERIFIED `InventoryComponent` constants.
- You arrange them at the **Runebinder's Lattice** bench (block `Bench_Abilities`, or the admin command `/abilities`).
- The **"Use Ability 2"** key casts line 1, **"Use Ability 3"** casts line 2. "Ability 1" stays the weapon's Signature attack.
  VERIFIED `InteractionContext.forInteraction`.
- A cast needs **a weapon in hand** (any weapon, or only the families the rune lists in `Weapons`), costs **Mana** (or Stamina /
  Health), and starts a **cooldown**. VERIFIED `ItemAbility.canUseWith`, `AbilityCastUtil`, `TriggerCooldownInteraction`.
- A modifier rune changes **named numbers of the ability next to it** (Damage x1.5, AoE x2, Duration +2, Fork +2, Ricochet +2, Cost,
  Cooldown, Speed...), can **convert its element** or **add on-hit effects**. It only fits next to an ability whose tags it matches.
  VERIFIED `ImpactModifiers.collect`, `AbilitySupportSlotFilter`.
- **It is almost entirely data-driven.** A new ability or modifier is JSON (item + root interaction + interactions), using a new
  toolbox of server interactions (`LaunchAbilityProjectile`, `SpawnAbilityEntity`, `GrantAbilityCharges`, `PullEntityAbility`,
  `SplitAbilityProjectile`, `TriggerAbilityFX`, `ApplyAbilityEffects`, `GroundedCondition`, `OpenAbilityBench`). VERIFIED
  `AbilitiesPlugin.setup`.
- **Vanilla Mana changes from max 0 to max 100** in this beta. VERIFIED `Server/Entity/Stats/Mana.json` (release 0/0, pre-release 100/100).
- For SkyWynn this fits decision rows **9.1 / 9.2** (class abilities ON the engine rune system) very well. The main limits are
  client-side: only **2 ability lines**, only 2 keys, fixed bench and HUD layout.

---

## 1. What is new (asset and code inventory)

### 1.1 New assets (PRE-RELEASE vs RELEASE, VERIFIED by entry diff)

| Area | New files |
|---|---|
| Rune items | `Server/Item/Items/Rune/Ability/` Rune_ChainHook, Rune_ChargedShot, Rune_Enrage, Rune_Fireball, Rune_GroundSlam, Rune_PoisonImbue, Rune_WindStrike (+ `_Debug/` Debug_Rune_Frostbolt, Debug_Rune_Tornado). `Server/Item/Items/Rune/Modifier/` Rune_Aoe_Up, Rune_Convert_Lightning, Rune_Convert_Wind, Rune_Damage_Up, Rune_Duration_Up, Rune_Fork, Rune_Ricochet (+ `_Debug/` Debug_Rune_Burning, Debug_Rune_Fork, Debug_Rune_Speed, Debug_Rune_Test) |
| Crafting material | `Server/Item/Items/Ingredient/Goblin/Ingredient_Rune_Shard.json` ("Runestone Shard", MaxStack 25) |
| Bench | `Server/Item/Items/Bench/Bench_Abilities.json` ("Runebinder's Lattice", Use = `OpenAbilityBench`, **no recipe**) |
| Casts | `Server/Item/RootInteractions/Abilities/Root_Ability_*.json` (7 + 2 debug) and `Server/Item/Interactions/Abilities/**` (ChainHook, ChargedShot, Enrage, Fireball, GroundSlam, PoisonImbue, WindStrike, `Ability_Cast_Fail`, `Ability_Split`, debug Frostbolt/Tornado) |
| Elements | `Server/Abilities/Elements/` Earth, Fire, Lightning, Water, Wind (each only `{"DamageCause": ...}`) |
| Damage causes | `Server/Entity/Damage/` **Earth, Water, Wind, Lightning, Crush** (Earth/Water/Wind/Lightning are children of `Elemental`, with their own damage-number colour) |
| Effects | `Server/Entity/Effects/Abilities/` ChargedShot charge stages, Enrage buff/slow, Frost chill/freeze/slow, GroundSlam lock, Hooked, Poison imbue + stacks A/B/C, Wind buff |
| Projectiles | `Server/ProjectileConfigs/Abilities/*` (ChargedShot 1-4, Fireball, WindStrike, ChainHook, GroundSlam, Debug Frostbolt), `Server/Models/Projectiles/Abilities/*` |
| FX / sound | particles (`Server/Particles/Abilities/**`, `.../Combat/Abilities/**`, bench particles), sounds (`SFX_Ability_*`), `CameraEffect/CameraShake Ability_Cast_Generic`, trails, new sword animation `Cast_Enchant` |
| Art | `Common/Items/Runes/` (Rune_Ability / Rune_Modifier / Rune_Shard models + 14 textures), `Common/Icons/ItemsGenerated/Rune_*.png`, **`Common/Icons/Abilities/<RuneItemId>.png`** (HUD icons, 7 files - none for ChainHook), `Common/Blocks/Benches/Abilities_Bench*` |
| Admin kit | `Server/MacroCommands/Kit_Abilities.json` ("kit abilities" gives the 7 ability + 7 modifier runes) |
| Goblin Lab (whole new area) | `GoblinLab_*` blocks, the Goblin Tinkerer's Workbench (`GoblinLab_Workbench`, category **Runestones** `GoblinLab_Runes`), augment/"device repair" pages `Common/UI/Custom/Pages/Augment*.ui` |

Changed vanilla assets that matter here (VERIFIED diff):
- `Server/Entity/Stats/Mana.json`: `InitialValue 0 / Max 0` -> `100 / 100` (same regen: +1 per 0.2 s after 6 s without damage, not while charging).
- `Template_Weapon_Crossbow.json`: the ammo reload moved from `Ability3` to the new `Ability4` (frees Ability3 for runes). Most other
  weapon changes are durability numbers.
- `Server/Item/Unarmed/Interactions/Empty.json`: the vanilla `"Wielding": "Double_Jump"` line is gone (not rune-related, noted for SkyySkills' Empty.json override).

### 1.2 New server code (VERIFIED jar diff)

- New builtin plugin **`Hytale:Abilities`** (`com.hypixel.hytale.builtin.abilities.AbilitiesPlugin`, manifest deps EntityModule,
  InteractionModule, NPC). Its `setup()` registers:
  - asset store **`Abilities/Elements`** (`Element`, loads after DamageCause and EntityEffect);
  - interaction types `ApplyAbilityEffects`, `LaunchAbilityProjectile`, `SpawnAbilityEntity`, `TriggerAbilityFX`, `PullEntityAbility`,
    `SplitAbilityProjectile`, `GrantAbilityCharges`, `GroundedCondition`, `OpenAbilityBench`;
  - components `AbilityCharges`, `AbilityEntityRepeat`, `AbilityProjectileTrail`, `PulledByAbility`, `AbilityProjectileSplit`;
  - systems `AbilityPullSystem`, `AbilityChargeMeleeAttackSystem`, `AbilityChargeRangedAttackSystem`, `AbilityChargeHitSystem`,
    `RuneEffectDamageSystem`, `AbilityEntityRepeatSystem`, `AbilityProjectileTrailSystem`, `ReactionDamageSystem`;
  - command **`/abilities`** (opens your bench) with subcommand `/abilities give` (one of every item that has an Ability block).
- In the core server:
  - `server.core.asset.type.item.config.ItemAbility` (the `Ability` block of an item; `Item.getAbility()`), protocol `ItemAbility`,
    enums `AbilitySlot {Primary, Support}` and `AbilityCostType {None, Mana, Stamina, Health}`.
  - `InventoryComponent$AbilitySlots` (component id **"AbilitySlotsInventory"**) and `InventoryComponent$RuneBag` ("RuneBagInventory"),
    their `InventoryChangeEvent` systems, slot filters `AbilitySlotAddFilter`, `AbilitySupportSlotFilter`, `AbilityItemAddFilter`.
  - `AbilityCastUtil` (cost / cooldown of the casting ability), `ImpactModifiers` (resolved modifier values of a cast),
    `AbilityCastSnapshotSystem`.
  - **`InteractionChainStartEvent`** - a new cancellable ECS event fired when any interaction chain starts.
  - `DamageSystems$ScaleOutgoingDamageFromEntityEffects` + a new **`OutgoingDamage`** field on EntityEffect (damage dealt +%/flat by
    damage cause - Enrage uses it).
  - New fields on existing interactions: `StatsCondition.UseAbilityCost`, `ChangeStat.UseAbilityCost`, `TriggerCooldown.UseAbilityCooldown`,
    `DamageEntity.DamageAttribute`, `ApplyEffect.DurationAttribute`, `AOECircleSelector/StabSelector.SizeAttribute`.
  - `InteractionType.Ability4` (release had Ability1-3), `WindowType.AbilityBench`, `UpdatePlayerInventory` now carries the
    ability and rune-bag sections.

### 1.3 New client files (VERIFIED)

- `Client/Data/Game/Interface/InGame/Pages/Abilities/AbilityBenchPanel.ui` (NEW): title "Runebinder's Lattice", two panels
  "Ability 1" and "Ability 2", each an `ItemGrid` with 1 big ability slot (`#Ability1MainGrid`) and a 2-slot modifier grid (`#Ability1ModifierGrid`).
- `.../Pages/Abilities/RuneBagPanel.ui` (NEW): "Runestone Storage", 5 per row, 8 rows visible, scrollbar.
- `.../Hud/Abilities/AbilitiesHud.ui` + `Ability.ui` (CHANGED): new `#Ability1Slot` / `#Ability2Slot` next to the Signature meter,
  Ready / NotReady frames, a cooldown fill, and three error sounds named `ErrorWrongWeaponSound`, `ErrorCooldownSound`, `ErrorResourceSound`.
- `client.lang` (NEW keys): `inventory.abilityBench.*`, `itemTooltip.abilityRunestone` / `modifierRunestone`, a full tooltip block
  `itemTooltip.stats.ability.*` (Cooldown, "Cost: {cost} {type}", "Requires: {weapons}", "Compatible with: {tags}", "On hit:",
  tag names for the vanilla tags, attribute names for AoeScale / Cooldown / Cost / Damage / Duration / Fork / ProjectileSize / Ricochet
  / RicochetRange / Speed / SplitChildDamage / SplitChildScale), `settings.bindings.Ability4ItemAction = Use Ability 4`, and a
  chapter pop-up "Runic Abilities Unlocked".
- The client exe contains the literal prefix `Icons/Abilities/` (VERIFIED string). INFERRED: the HUD loads `Icons/Abilities/<RuneItemId>.png`.

---

## 2. How runes work, end to end

### 2.1 A rune is an item with an `Ability` block (VERIFIED `ItemAbility` codec + docs)

Ability runestone example (`Rune_Fireball.json`, VERIFIED):
```
"Quality": "Rare", "ItemLevel": 10, "MaxStack": 1, "Categories": ["Items.Ingredients"],
"Ability": { "Slot": "Primary", "Cooldown": 12, "Cost": 25, "CostType": "Mana",
             "Tags": ["damage.elemental.fire", "mechanic.projectile", "mechanic.aoe"],
             "Cast": "Root_Ability_Fireball" }
```
Modifier runestone example (`Rune_Fork.json`, VERIFIED):
```
"Ability": { "Slot": "Support", "AppliesTo": ["mechanic.projectile"],
             "AttributeModifiers": { "Fork": [ { "CalculationType": "Additive", "Amount": 2 } ] } }
```
All `Ability` keys and what the engine's own documentation strings say about them:

| Key | For | Meaning (VERIFIED from `ItemAbility` codec docs) |
|---|---|---|
| `Slot` | both | `Primary` (ability) or `Support` (modifier). Required. |
| `Cooldown` | Primary | Seconds between casts. The cast chain arms it with `TriggerCooldown { UseAbilityCooldown: true }`. A Support modifier on the `Cooldown` attribute scales it (multiplier, base 1). |
| `Cost` + `CostType` | Primary | Resource per cast (`Mana`, `Stamina`, `Health`, `None`). Gated with `StatsCondition { UseAbilityCost }`, spent with `ChangeStat { UseAbilityCost }`. A modifier on `Cost` scales it (multiplier, base 1). |
| `Weapons` | Primary | "Weapon families (Family item tags, e.g. Staff, Sword) the caster must hold to cast this ability. Empty or absent means no restriction." Matched as item tag `Family=<name>`. No vanilla rune uses it. |
| `Tags` | Primary | Dotted tags (`damage.elemental.fire`, `mechanic.aoe`...). Every dotted prefix also matches (`damage.elemental.fire` is also `damage.elemental` and `damage`). Registered as tag `Ability:<tag>`. |
| `Attributes` | Primary | Named tunable numbers the interactions bind to (e.g. `Duration`, `FreezeDuration`, `Fork`, `SplitChildDamage`). |
| `Cast` | Primary | The root interaction cast "when the ability fires from its bench slot (Ability2/Ability3). Abilities cast only from the bench; an ability item held in the hand exposes no interactions." |
| `AppliesTo` | Support | Tags the ability must have for this modifier to fit. Empty = fits any ability. |
| `AttributeModifiers` | Support | `{ "<Attribute>": [ {CalculationType, Amount}... ] }` applied "left to right across the line". |
| `OnHitEffects` | Support | EntityEffect ids applied to everything the ability damages. |
| `ConvertElement` | Support | Elemental DamageCause the ability's elemental damage converts to (e.g. Wind); numbers and visuals recolour; "the rightmost conversion in the line wins". |

Rune data lives on the **item type** (the asset), not on the stack: casting reads `stack.getItem().getAbility()` (VERIFIED
`ImpactModifiers.collect`, `InteractionContext.forInteraction`). There is **no per-stack roll** on a rune. INFERRED: two different
strengths of the "same" rune need two item ids.

### 2.2 Where runes are stored (VERIFIED)

- `InventoryComponent.ABILITIES_SECTION_ID = -11`, `DEFAULT_ABILITIES_CAPACITY = 6` (`ABILITIES_LINES = 2` x `ABILITIES_LINE_WIDTH = 3`).
  Slot 0 = line 1 ability, 1-2 = its modifiers; slot 3 = line 2 ability, 4-5 = its modifiers.
- `RUNE_BAG_SECTION_ID = -12`, `DEFAULT_RUNE_BAG_CAPACITY = 50`. Only items with an `Ability` block go in (`AbilityItemAddFilter`).
- Both are ECS components on the player, registered with save ids `AbilitySlotsInventory` / `RuneBagInventory` (EntityModule), created
  by `PlayerSystems$PlayerInitSystem` (hard-coded 6 and 50), sent to the client in `UpdatePlayerInventory` (`PlayerSendInventorySystem`).
- Slot filters (set by `ItemContainerUtil.trySetAbilityFilters(container, 3)`):
  - every `i % 3 == 0` slot takes only `Slot: Primary` items (`AbilitySlotAddFilter`);
  - the other slots take only `Slot: Support` items **and only if** the line's ability slot is filled **and** the modifier's
    `AppliesTo` matches the ability's tags (`AbilitySupportSlotFilter.testAdd`).
- When an ability is swapped out, modifiers that no longer fit are moved to the rune bag (`InventoryUtils.prepareAbilityPrimaryChange`,
  `collectInvalidSupports`, `rehomeEvictedSupports`).
- `InventoryComponent.EVERYTHING` is built in `setupCombined(...)` from Storage, Armor, Hotbar, Utility, Backpack, Tool only.
  INFERRED: runes are not part of "all inventory" operations (clear / drop-all on death), so they likely survive death.

### 2.3 How a cast happens (VERIFIED `InteractionContext.forInteraction` + `getRootInteractionId`)

1. The player presses **Use Ability 2** or **Use Ability 3** (InteractionType `Ability2` / `Ability3`).
2. `forInteraction` reads the hotbar item in hand and the `AbilitySlots` component. `Ability2` -> slot 0, `Ability3` -> slot 3.
3. The rune is used only if `ItemAbility.canUseWith(heldItem)`: the held item must exist, must have a **Weapon** block, and, if the rune
   lists `Weapons`, must carry one of those `Family` tags.
4. If the player holds **any** item, the chain's "held item" becomes that rune in section -11 (or nothing if it cannot be used).
   The root interaction is the rune's `Cast`. **So while holding any item, Ability2/Ability3 no longer run the held item's own
   Ability2/Ability3 interactions.** With an empty hand, the old unarmed behaviour stays. (Only exception: an entity-level
   `Interactions` component override is checked first.)
5. The client HUD shows three failure states (wrong weapon / cooldown / not enough resource) with a fail sound (VERIFIED `Ability.ui`).

A typical vanilla cast chain (`Ability_Fireball_Cast.json`, VERIFIED):
```
StatsCondition { UseAbilityCost: true, Failed: "Ability_Cast_Fail" }
  -> Parallel [ TriggerCooldown { UseAbilityCooldown: true },
                ChangeStat { UseAbilityCost: true },
                Simple (cast animation 1 s) -> LaunchAbilityProjectile { Projectile, Scale 1.5,
                                                 ScaleAttribute "ProjectileSize", SpeedAttribute "Speed" } ]
Projectile hit / miss -> Ability_Split, Ability_Fireball_Impact (TriggerAbilityFX + AOECircle Selector,
                         SizeAttribute "AoeScale") -> Ability_Fireball_Hit (DamageEntity Fire 24, DamageAttribute "Damage")
```
Details (VERIFIED `AbilityCastUtil`, `TriggerCooldownInteraction`):
- Cost is the rune's `Cost` x the cast's `Cost` attribute (default 1). **In Creative the cost is ignored.**
- The cooldown is keyed by the rune's `Cast` root id, length `Cooldown` x the cast's `Cooldown` attribute.
- Root interactions use `RequireNewClick: true` (one cast per press).

### 2.4 How modifiers are applied (VERIFIED `ImpactModifiers.collect` / `snapshotForCast`)

- When a chain starts from section -11, `AbilityCastSnapshotSystem` (listens to `InteractionChainStartEvent`) builds an
  `ImpactModifiers` snapshot and stores it in the chain (`ImpactModifiers.CAST_SNAPSHOT`).
- Start values = the ability's `Attributes`. Then for each modifier in slots +1, +2 of that line (left to right) that `appliesToAbility`:
  every attribute starts at **1.0 if the ability does not define it**; `Additive` adds `Amount`, `Multiplicative` multiplies.
  `OnHitEffects` are collected; `ConvertElement` - last one wins.
- Interactions read the numbers by name through their `...Attribute` fields: `DamageAttribute` (scales damage), `DurationAttribute`,
  `ScaleAttribute`, `SizeAttribute`, `SpeedAttribute`, `LifetimeAttribute`, `EffectDurationAttribute`. `SplitAbilityProjectile` reads
  `Fork`, `Ricochet`, `RicochetRange`, `SplitChild<X>`.
- Attribute names seen: `Damage`, `AoeScale`, `Duration`, `Cost`, `Cooldown`, `Speed`, `ProjectileSize`, `Fork`, `Ricochet`,
  `RicochetRange`, `SplitChildDamage`, `SplitChildScale`, plus ability-specific ones (`FreezeDuration`, `ShortFreezeDuration`).
  Any name works on the server; only the listed ones have client tooltip text (VERIFIED `client.lang`).
- The snapshot travels with the chain into projectiles, spawned entities and charges, so a modifier affects the whole ability.
- On-hit effects are applied by `RuneEffectDamageSystem` to every entity the ability damages (Damage meta `ImpactModifiers.DAMAGE_MODIFIERS`).
- Elements: `ReactionDamageSystem` supports **elemental reactions** (a victim carrying one element's effect, hit by another element,
  gets a reaction effect and can lose the state). The `Element` asset has `DamageCause`, `OnHitEffect`, `Reactions`. **The vanilla
  Element files only set `DamageCause`, so reactions are built but unused in this beta.** VERIFIED `Element`, `Abilities/Elements/*.json`.

### 2.5 The vanilla runes (VERIFIED item + interaction JSON)

Ability runestones (all Quality Rare, ItemLevel 10, recipe 3 shards):

| Rune | Cost / CD | Tags | What it does |
|---|---|---|---|
| Fireball | 25 Mana / 12 s | fire, projectile, aoe | 1 s cast, fireball, 24 Fire in radius 2.5 on impact |
| Charged Shot | needs 10 to start (checked, not spent), then spends 10/20/30/50 by release stage / 4 s | water, projectile, charged, duration | hold to charge 4 stages (you slow, then root); frost bolt 12/24/38/55 Water, slow / chill / freeze; full charge shatters into icicles (built-in Fork 3). Stage costs are hard-coded in JSON, so Cost modifiers do not touch them |
| Chain Hook | 15 / 6 s | physical, projectile, aoe, duration | chain projectile, 3 Bludgeoning, pulls the target to you (`PullEntityAbility`), Hooked 0.8 s |
| Enrage | 20 / 16 s | buff, duration | 10 s: +30% damage dealt, +20% damage taken (EntityEffect `OutgoingDamage` / `DamageResistance`) |
| Ground Slam | 30 / 18 s | earth, melee, aoe | must be on ground; ground wave 15 Earth, stone spike 35 Earth + launch up |
| Imbue Poison | 10 / 18 s | buff, poison, duration | 12 s buff: weapon hits add stacking poison (3 stacks, 2 Poison per s, 6 s each) via `GrantAbilityCharges` Trigger OnHit |
| Wind Strike | 20 / 10 s | buff, wind, aoe, duration | next 3 weapon swings each launch a piercing wind arc (8 Wind) via `GrantAbilityCharges` OnPrimaryActivation, MaxCharges 3 |

Modifier runestones: Expansion (AoeScale x2), Extended Duration (Duration +2), Fork (+2 projectiles on first hit), Ricochet (+2 hits)
are Uncommon, ItemLevel 20, recipe 2 shards. Amplify Damage (Damage x1.5), Lightning Conversion, Wind Conversion are Quality
`Developer` with no recipe (admin-only for now). The debug set (Burning on-hit, Speed trade-off with Cost x0.5 / Cooldown x0.5,
Frostbolt, Tornado) is `[TMP]` in the lang file.

### 2.6 How runes are obtained (VERIFIED)

- **Runestone Shards** drop from Goblin Burner (weighted choice), Goblin Feastmaster (2), Skeleton Elite (2), Void Spawn Entombed (2),
  Void Spawn Surge (2), and Shiny Scrap Piles (weighted choice) (`Server/Drops/**`).
- Runes are **crafted** at the **Goblin Tinkerer's Workbench** (`GoblinLab_Workbench`, category "Runestones"), with
  `RequiredAugmentTags: ["goblin_lab_power"]` - the Goblin Lab's power generator must be repaired first. The Goblin Lab is new
  content beyond the Forgotten Temple.
- The **Runebinder's Lattice** has no recipe; it is placed in the `Forgotten_Temple_Goblins` instance (map marker in
  `BlockMapMarkers.json`). Any block whose Use interaction is `OpenAbilityBench` becomes a bench (codec doc).
- Admins: `/abilities`, `/abilities give`, macro `kit abilities`. INFERRED: `/abilities` has no player permission group in its
  constructor, so by our COMMAND RULES it is admin-only by default.

### 2.7 The client UI (VERIFIED client `.ui` + lang)

- Bench = page `Bench` + window `AbilityBench` over the player's 6 ability slots (`AbilityBenchWindow`), shown with the rune bag panel.
  The layout (2 lines, 1 + 2 slots) is fixed in the client's `AbilityBenchPanel.ui`.
- HUD: two ability slots beside the Signature meter, cooldown fill, error sounds. Bench labels say "Ability 1 / Ability 2" while the
  keys are named "Use Ability 2 / 3" (lang). INFERRED: players will see that naming mismatch.
- Tooltips: "Ability Runestone" / "Modifier Runestone", cost, cooldown, "Requires: {weapons}", "Compatible with: {tags}", modifier lines
  as percentages. Tag and attribute names come from `client.itemTooltip.stats.ability.tagName.<tag>` / `attributeName.<attr>` in the
  client's own language file.

---

## 3. Modding: what a server plugin / asset pack can do

| Question | Answer | Tag |
|---|---|---|
| Add new ability stones? | **Yes, pure JSON**: an item with `Ability { Slot: Primary, Cast, Cost, Cooldown, Tags, Attributes, Weapons }`, a root interaction and interactions built from vanilla + ability interaction types. The client learns the item (incl. `cast`, cost, cooldown, weapons) from the item packet. | VERIFIED codec + protocol `ItemAbility` fields |
| Add new modifiers? | **Yes, pure JSON**: `Slot: Support` + `AppliesTo` + `AttributeModifiers` / `OnHitEffects` / `ConvertElement`. New attribute names work if our interactions bind them by name. | VERIFIED |
| New mechanics (heal a party, mark, teleport...)? | Either compose existing interactions (Selector + ApplyEffect + ChangeStat...) in JSON, or register a new server interaction type in Java (`getCodecRegistry(Interaction.CODEC).register(...)`, as `AbilitiesPlugin` does). | VERIFIED pattern; INFERRED for our javassist toolchain (building a `BuilderCodec` from javassist is still UNVERIFIED, see Cooking-Skill-Spec) |
| Change existing runes? | Override the vanilla JSON in our asset pack (same id), or ship our own ids and hide vanilla. | INFERRED (normal asset override) |
| New elements / reactions? | JSON: `Server/Abilities/Elements/<Id>.json` (`DamageCause`, `OnHitEffect`, `Reactions`) + a `Server/Entity/Damage/<Cause>.json`. | VERIFIED codec |
| Restrict a rune to a class? | (a) JSON `Weapons: [...]` = only castable with those weapon families, which already maps to our class weapon locks. (b) Code: cancel the cast in an `EntityEventSystem<InteractionChainStartEvent>` when `ctx.getHeldItemSectionId() == -11` and the class does not own that rune; the server then sends the client a cancel packet. (c) Code: on `InventoryChangeEvent` for the AbilitySlots component, move disallowed runes back to the bag. (d) Class-only modifiers: give class abilities a private tag (e.g. `class.mage`) and put it in the modifier's `AppliesTo`. | (a),(d) VERIFIED mechanism; (b) VERIFIED `InteractionManager.syncStart` cancel -> `sendCancelPacket`, and the portal curse system uses exactly this; (c) VERIFIED event, item move INFERRED |
| Read which runes a player has? | `store.getComponent(ref, InventoryComponent$AbilitySlots.getComponentType()).getInventory().getItemStack(0..5)`; rune bag via `InventoryComponent$RuneBag`. World thread only. | VERIFIED API |
| Grant / remove runes? | Add to the rune bag or directly into a slot (vanilla slot filters apply to adds); `Player.giveItem` works for normal inventory. | VERIFIED filters; INFERRED that programmatic slot adds respect them |
| Open the bench from our menu? | Same call as `/abilities`: `player.getPageManager().setPageWithWindows(ref, store, Page.Bench, true, new Window[]{ new AbilityBenchWindow(abilitySlots.getInventory()) })`. | VERIFIED `AbilitiesCommand.execute` |
| Hook "ability used"? | `InteractionChainStartEvent` (cancellable; `getType()` Ability2/3, `getContext().getHeldItem()` = the rune stack, `getRootInteractionId()`). | VERIFIED |
| Hook "rune slotted / removed"? | `InventoryChangeEvent` fired for the `AbilitySlots` and `RuneBag` components. | VERIFIED `InventorySystems$InventoryChangeEventSystem` |
| Hook ability damage? | Damage events; `Damage` carries `ImpactModifiers.DAMAGE_MODIFIERS` meta only when the cast had modifier values, so it is not a reliable "was an ability" flag. | VERIFIED meta; INFERRED limit |
| Cooldowns? | Cooldown id = the rune's `Cast` root id in the player's `CooldownHandler` (`isOnCooldown`, `getCooldown`, `resetCooldown`). | VERIFIED class + keying; INFERRED plugin access path |
| Change a player's ability numbers without a modifier rune (skill tree, gear "-% Spell Cost")? | No official hook: only slotted support runes feed `ImpactModifiers`. A plugin could replace the `CAST_SNAPSHOT` meta with its own `ImpactModifiers` (public constructor) in its own chain-start system that runs after `AbilityCastSnapshotSystem`. | VERIFIED pieces; INFERRED that it works (system order, client-predicted parts) |
| Trigger a cast from code (click combos)? | Not supported by design; the cast comes from the client pressing Ability2/3. Server-started chains might skip client-side animation parts. | INFERRED |

**Locked client-side (cannot be changed by a server mod), VERIFIED unless noted:**
- Exactly 2 ability lines of 1 + 2 slots: client bench `.ui`, HUD `#Ability1Slot/#Ability2Slot`, server hard-codes slot 0 / 3 for
  Ability2 / Ability3 and capacity 6. A 3rd line would be neither visible nor castable.
- The two keys (Use Ability 2 / 3), the HUD look, error sounds, the tooltip layout.
- Tooltip text for tags and attributes is in the client language file; INFERRED: our own tags / attribute names will show as raw
  keys or blank in tooltips.
- INFERRED: the HUD icon comes from `Icons/Abilities/<RuneItemId>.png` - we can ship our own PNG under that path in our asset pack.

---

## 4. Design implications for SkyWynn

### 4.1 Fit with what is locked

- **Decision 9.1 / 9.2 (OPEN)** - "build class abilities on the engine rune system; tree nodes double as modifier-rune unlocks".
  The beta supports this shape directly: ability runes = class spells, modifier runes = tree unlocks.
- **SkyyClasses-Plan**: "Ability keys, no click-combos" matches the engine (key presses, not click combos). Wynncraft's 4 spells
  per class do not fit 1:1: the engine gives **2 active spells** + the weapon's Signature (Ability 1). INFERRED: a class tree could
  unlock more runes and the player picks 2 as a loadout (Wynn-style "build" choice).
- **6.4 Mana (LOCKED: use Hytale's mana)**: the beta makes vanilla Mana 100 / 100 and every vanilla rune costs Mana (10-50).
  SkyySkills 0.4.6 posts base Mana as `base - EntityStatType(Mana).max`, so our base stays 10 / 20 (VERIFIED in the patch header) -
  but then **a base-10 player can afford no vanilla rune**. Skyy must choose: (a) move our base to vanilla scale (100, Mage / Priest
  more), or (b) keep 10 / 20 and price our class runes 2-8 Mana. (a) is simpler and keeps vanilla runes usable. OPEN QUESTION for Skyy.
- **6.12 skill-upgrade points** ("raise damage, lower raw cost"): no engine hook besides modifier runes. Options: tiered rune items
  (`Skyy_Rune_Fireball_2`), or the INFERRED `CAST_SNAPSHOT` injection.
- **Elements (5.8 / 9.3)**: the engine's ability elements are **Fire, Water, Earth, Wind, Lightning** - the same five as Wynncraft
  (Fire, Water, Earth, Air, Thunder). VERIFIED names. So SkyyGear's Wynn five can use the engine damage causes
  (`Fire`, `Water`, `Earth`, `Wind`, `Lightning`), and ability damage, gear element damage and gear element defence can all key off the
  same causes. INFERRED design; 9.3's "keep Wynn's five on gear" still holds and now costs nothing.

### 4.2 How class abilities could be built (proposal, INFERRED)

- Each class gets its own **Skyy ability runes** with `Weapons` = its weapon families (item `Tags.Family`, VERIFIED values seen:
  Bow, Crossbow, Sword, Longsword, Spear, Staff, Magic (Weapon_Staff_Crystal_Flame), Axe, Battleaxe, Mace, Club, Wand, Spellbook,
  Dagger). Examples: Archer (Bow, Crossbow), Warrior (Sword, Longsword, Spear), Mage (Staff, Magic), Berserker (Axe, Battleaxe,
  Mace, Club), Priest (Wand, Spellbook), Assassin (Dagger).
- Because SkyyClasses already blocks other classes' weapons, `Weapons` is most of the class lock for free. A small SkyyClasses system
  on `InteractionChainStartEvent` closes the gap (e.g. a Mage holding a bow): cancel + the existing weapon-lock popup.
- Tag each class rune `class.<name>`; class modifier runes use `AppliesTo: ["class.<name>"]` so they only fit that class's spells.
- **Tree unlocks = which runes you may slot** (9.1): SkyyClasses checks the tree on `InventoryChangeEvent` (AbilitySlots) and returns
  locked runes to the bag with a message. Alternatively the tree node just *gives* the rune item once.
- Reuse vanilla building blocks first: Mage = Fireball / Charged Shot style; Archer = Chain Hook / Fork / Ricochet projectiles;
  Warrior = Wind Strike style charges; Berserker = Enrage / Ground Slam; Priest = an AoE heal (Selector AOECircle + ApplyEffect with a
  heal effect) - needs one new heal composition, INFERRED doable in JSON.
- Give each class rune its HUD icon at `Common/Icons/Abilities/<id>.png` and a shard-style recipe or a tree/quest source.
- Bench access: place a Runebinder's Lattice in the hub, and/or a "Runes" button in SkyyMenu that opens the bench (VERIFIED call).

### 4.3 Rune modifiers vs SkyyGear modifiers

| | Rune modifiers | SkyyGear modifiers |
|---|---|---|
| Lives on | the item **type** (asset); no per-stack roll | per-stack metadata (rarity, rolls, reforge) |
| Affects | only the ability in the same line (its named attributes) | the player's stats / damage |
| Stacking | left to right, Additive / Multiplicative, base 1 | our own rules |

- **Complement**: gear = who you are, runes = what your spells do. Gear "Spell Damage", "-% Spell Cost" (6.4, accessory only) and
  elemental damage fit on the gear side, applied to ability damage through the normal damage pipeline or the new EntityEffect
  `OutgoingDamage` (VERIFIED new field, per damage cause) - no conflict with runes.
- **Watch-outs** (INFERRED): SkyyGear must skip items with an `Ability` block (no rolls on runes, or tooltips / identity break);
  runes use vanilla `Quality` (Rare / Uncommon), which may clash visually with SkyyGear rarity names; "reforge" does not apply to
  runes because their numbers are per type. Decision 5.7 "powders" (gear sockets) are a different thing from rune modifier slots.

### 4.4 Other SkyWynn mods affected when 0.7 goes live (INFERRED unless noted)

- **SkyyProfiles**: 0.1.3 snapshots exactly six sections (Hotbar, Storage, Backpack, Armor, Utility, Tool - VERIFIED build header). It
  does **not** save sections -11 / -12, so runes would follow the player across profiles (a Mage's runes on the Warrior profile).
  Must add both sections to the per-profile snapshot.
- **SkyySkills**: base Mana formula keeps working (VERIFIED formula), but the numbers need Skyy's decision (4.1). Its Empty.json
  override should be re-checked because vanilla removed the unarmed `Wielding: Double_Jump`.
- **SkyyClasses weapon-skill XP**: ability damage from projectiles / spawned entities may not be attributed to the class weapon skill
  the way melee hits are. Check in game.
- No current SkyWynn item binds Ability2 / Ability3 (VERIFIED grep of build scripts), so the new "Ability2/3 always go to runes"
  routing breaks nothing of ours. `Ability4` is new and free for an item-bound action (crossbow reload uses it in vanilla).

### 4.5 What to build first once 0.7 is live (proposal)

1. **Probe round** (admin only): `kit abilities` + `/abilities` on a test world; confirm keys, HUD, costs vs our Mana, cooldowns,
   Creative cost-free, death and world-switch behaviour of the 6 slots + bag.
2. **Skyy decisions**: Mana scale (4.1), keep or hide vanilla runes, 2-spell loadout vs Wynn's 4, where the bench lives.
3. **SkyyProfiles**: add sections -11 / -12 to the profile snapshot (before any player gets runes).
4. **SkyyClasses**: the class gate (chain-start cancel + slot check) and a menu button to open the bench.
5. **Asset pack**: 1-2 runes per class from vanilla building blocks, with `Weapons` + `class.*` tags + HUD icons.
6. Later: class modifier runes as tree unlocks (9.2), elemental reactions for Wynn's five, gear hooks via `OutgoingDamage`.

### 4.6 Risks

- **Beta churn**: this is `0.7.0-pre.4`. Many strings are `[TMP]`, there are `_Debug` runes, Developer-quality modifiers and a
  `Patchlines: ["dev"]` pop-up. Field names, slot counts, costs or the Goblin Lab gating may change before release. Build nothing
  against it until it ships; re-run this diff on the release build.
- SkyWynn runs on release 0.6.8 today: none of these classes exist there, so any mod that references them would fail to load on
  0.6.8. Rune features must ship only after the pack moves to 0.7.
- Client-locked limits (2 lines, 2 keys, tooltip names) can't be widened by us.
- Our `CAST_SNAPSHOT` / custom-interaction ideas depend on unverified details (system order, client prediction).

---

## 5. Full list of the new ability interaction types (VERIFIED codec docs)

| Type | What it does (engine doc, shortened) | Key fields |
|---|---|---|
| `LaunchAbilityProjectile` | server-side projectile along the look; hit chain where it lands; `Pierce` flies through (hit chain per entity), miss chain at course end | Projectile, IgnorePitch, Pierce, Distance, Lifetime, Scale, ScaleAttribute, SizeAttribute, SpeedAttribute, Spectral, TrailParticles/Interval/Scale/Color |
| `SplitAbilityProjectile` | on first entity hit, splits when the cast carries Fork or Ricochet; no-op otherwise; put it in the ProjectileHit chain | ForkSpread, RicochetRange; reads Fork, Ricochet, SplitChild<X> |
| `SpawnAbilityEntity` | stationary ability entity (e.g. tornado) at the aim point; lives Lifetime s; runs each Repeats chain at its interval; ignores damage | Model, Repeats[{Interval, Chain}], Lifetime, LifetimeAttribute, ScaleAttribute, Range |
| `GrantAbilityCharges` | buff on the caster + charges; each Trigger (OnPrimaryActivation = weapon attack released, OnHit = weapon attack lands) spends a charge and runs PerActivationInteraction with the cast's values | Effect, Duration, DurationAttribute, Trigger, MaxCharges, PerActivationInteraction |
| `PullEntityAbility` | reels the hit entity to the caster; guard toward the caster resists; big entities can be exempt | Delay, ReelTime, Arc, StopRange, MaxTargetWidth, Effect, EffectDuration, EffectDurationAttribute |
| `ApplyAbilityEffects` | applies one of several effects per application (acts as stacks) | Effects[], Duration, DurationAttribute, RuneEffects |
| `TriggerAbilityFX` | world particles + sound at the hit point, scaled by an attribute; use instead of Effects in server-simulated chains | SystemId, SoundEventId, Scale, ScaleAttribute, Color |
| `GroundedCondition` | fails unless on ground (or within Tolerance blocks) | Tolerance, Failed |
| `OpenAbilityBench` | opens the using player's bench; author as any block's Use | - |

---

## 6. Source index (for re-checking on the release build)

- Server jar: `com/hypixel/hytale/builtin/abilities/**`, `server/core/asset/type/item/config/ItemAbility`,
  `server/core/inventory/InventoryComponent` (+ `$AbilitySlots`, `$RuneBag`), `server/core/inventory/container/ItemContainerUtil.trySetAbilityFilters`,
  `server/core/inventory/container/filter/Ability*Filter`, `server/core/entity/InteractionContext.forInteraction / getRootInteractionId`,
  `server/core/modules/interaction/interaction/util/AbilityCastUtil`, `server/core/modules/projectile/component/ImpactModifiers`,
  `server/core/modules/projectile/system/AbilityCastSnapshotSystem`, `server/core/modules/interaction/event/InteractionChainStartEvent`,
  `server/core/entity/InteractionManager.syncStart`, `server/core/modules/entity/player/PlayerSystems$PlayerInitSystem`,
  `server/core/inventory/InventoryUtils.prepareAbilityPrimaryChange`, `manifests.json` (Hytale:Abilities).
- Assets: `Server/Item/Items/Rune/**`, `Server/Item/RootInteractions/Abilities/**`, `Server/Item/Interactions/Abilities/**`,
  `Server/Abilities/Elements/*`, `Server/Entity/Damage/{Earth,Water,Wind,Lightning}.json`, `Server/Entity/Effects/Abilities/*`,
  `Server/Entity/Stats/Mana.json`, `Server/Item/Items/Bench/Bench_Abilities.json`, `Server/Item/Items/Ingredient/Goblin/Ingredient_Rune_Shard.json`,
  `Server/Item/Items/Puzzles/Goblins/Lab/GoblinLab_Tinkering_Bench.json`, `Server/Drops/**` (shards), `Server/MacroCommands/Kit_Abilities.json`.
- Client: `Client/Data/Game/Interface/InGame/Pages/Abilities/*.ui`, `.../Hud/Abilities/*.ui`, `Client/Data/Shared/Language/en-US/client.lang`.

---

## 7. What must be seen in game (all UNVERIFIED until then)

1. The default keys for Use Ability 1 / 2 / 3 / 4, and that Ability 2 casts bench line 1 and Ability 3 casts line 2.
2. The HUD: both slots appear once runes are slotted; cooldown fill; wrong-weapon / cooldown / no-Mana fail sounds.
3. Casting with an empty hand, a tool, and a non-listed weapon (expect: nothing / fail state).
4. Mana: vanilla 100 on a plain world; with SkyySkills base Mana 10 / 20, confirm runes fail for lack of Mana.
5. Runes after death, world switch (PlayerReadyEvent), relog, and a SkyyProfiles switch (expect: they leak across profiles today).
6. A cancelled cast (`InteractionChainStartEvent`) looks clean on the client (no stuck animation, no cooldown, no Mana spent).
7. Our own rune with a custom tag / attribute: what the tooltip shows; whether a missing `Icons/Abilities/<id>.png` falls back
   (vanilla Chain Hook has none).
8. Modifiers: Fork / Ricochet / Expansion / Extended Duration visibly change a cast; a modifier refuses to go next to a non-matching ability.
9. Goblin Lab path: shard drops, the Tinkerer's Workbench Runestones tab after repairing the power generator.
10. Whether ability damage is credited to the class weapon skill by SkyyClasses.
