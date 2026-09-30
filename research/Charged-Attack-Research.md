# Charged attacks: what Hytale has, and how SkyyGear can tell a charged hit (engine research + stat design)

*Written 2026-09-30. Read-only research. Only this file was written. Scratch dumps lived under `tools/dev/scratch/charged/` and were
deleted afterwards. No build script, jar, doc or game file was touched.*

*Skyy's ask (2026-09-30, verbatim): "in hytale every weapon has a charged attack. id also add a modifier to weapons and armor that boosts
charge attack damage." Skyy's lock from the same day: a stat that does nothing yet must never roll. So this modifier only ships if
SkyyGear can really tell a charged attack when the damage lands (OPEN-QUESTIONS, "LOCKED 2026-09-30", target SkyyGear 0.1.2).*

*Inputs: `tools/AGENT-BRIEF.md`, HANDOFF (status, round 9 log), OPEN-QUESTIONS, `SkyyGear/build_skyygear_0.1.py` (GearHit, GearShot,
GearShotTrack, GearHitSys, the STATS / RARITY_DEF / CFG_ROWS tables) and `build_skyygear_0.1.1.py` (header), `research/SkyyGear-Stage1-Spec.md`
2.2-2.3 and 4.2-4.3, `SkyyGear-Stat-Catalog.md`, `SkyyTrees/build_skyytrees_0.2.4.py` (root overrides + EffectCondition trees),
`research/Swing-Speed-Spec.md`, `research/Classes-Berserker-Priest-Spec.md`. Engine checks with `tools/dev` (reflect.py, bcfull.py,
clinit.py, cpgrep.py, callers.py) against the release `HytaleServer.jar`; `Assets.zip` read in memory (a Python walker that follows every
weapon item's Interactions / RootInteractions / InteractionVars / ProjectileConfigs, like the engine's own tooltip walk); installed mods
read-only (`More_Crossbow_Tiers.zip`, `MoreArrows_Skovos.jar`, `H1Z.Working Blunderbusses.zip`, `EndgameAndQoL5.4.1.jar`,
`Arcane_Power_V3.1.1.zip`, `Reforged_Weapons_4.4.zip`).*

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode or in `Assets.zip` / installed-mod JSON. INFERRED = strongly implied, not
proven. UNVERIFIED = needs Skyy's in-game test.

---

## 0. Verdict: YES, and without touching a single vanilla file

1. **Hytale itself already labels charged damage in two ways, and a server plugin can read both at damage time.**
   - **The damage class.** Every `DamageEntity` step has a `DamageCalculator` with a `Class`: `Unknown`, `Light`, `Charged` or
     `Signature` (engine enum `DamageClass`, VERIFIED). When the step deals damage, the engine puts a `DamageSequence` on the `Damage`
     object under the meta key `DamageCalculatorSystems.DAMAGE_SEQUENCE`, and that object carries the exact `DamageCalculator` that was
     used (VERIFIED bytecode, section 2.1). The engine's own `DamageCalculatorSystems$SequenceModifier` reads that meta key inside a
     damage system, the same way SkyyGear's `GearHitSys` would. So `GearHitSys` can ask "is this `Class: Charged`?" with one call.
   - **The hold-to-charge step.** Hytale's own weapon tooltip (`WeaponDamageDataCollector`, run by `ItemModule` whenever items load)
     walks every weapon's interaction chain and labels any damage reached through a charge step of more than 0 s as `"charged"`
     (VERIFIED bytecode, section 2.2). SkyyGear can run the same walk once per item and remember which `DamageCalculator` objects sit
     behind a charge step. At damage time the calculator from the meta key is looked up in that list.
2. **Why both are needed.** The four "modern" weapon families (Sword, Battleaxe, Mace, Daggers) plus the Shortbow, the Crossbow and the
   Ice staff tag their charged damage `Class: Charged`. The older families (Axe, Longsword, Flail clubs, Spear, Staff, Wand, Spellbook,
   the Void scythe) do NOT tag it: their charged step is `Unknown` class. Also, the dagger pounce from behind (backstab) and the
   full-draw bow headshot use a separate calculator without the tag. The tooltip-style walk covers all of those.
3. **Thrown and cast projectiles from the older families** (spear throw, staff / wand / spellbook orb) do not go through a `DamageEntity`
   step at all. They are "legacy" projectiles whose damage the projectile itself deals (`Damage$ProjectileSource`). Those weapons can
   only launch that projectile from their charged step, so SkyyGear's existing launch tracker (`GearShotTrack`) marks the shot as
   charged when it is launched (section 2.4).
4. **Recommended: signals 1 + 2 + 3 together, all Java, zero asset overrides** (section 3). Confidence: **high** for the mechanism
   (every link is bytecode-proven and mirrors code the engine itself runs); **medium-high** until one in-game probe confirms it (section
   6). The exact UNVERIFIED list is in section 2.6.
5. **"Every weapon has a charged attack" is almost true.** Exceptions (VERIFIED): the 13 plain **Clubs** (a charged down-swing exists in
   Assets.zip and in every club's InteractionVars, but `Club_Attack` is a plain 2-hit chain, so it never runs), the **Kunai**, the
   **Crystal Flame staff** (its charged fireball hurts through an explosion, not a damage step), and the **Crossbow** (no hold-to-charge;
   its `Charged` hit is the 3rd bolt in a row on the same target). The new stat must not roll on the first three (section 4.4).

---

## 1. Every vanilla charged attack, per weapon family

How the table was made: a walker over `Assets.zip` resolved every non-debug `Weapon_*` item (Parent chain), its `Interactions` roots,
every `Charging` step's `Next` times, every `Replace` var (item override or default), every `Selector` hit, every `ProjectileConfig`
`ProjectileHit` chain and every `LaunchProjectile`. "Normal" and "Charged" numbers are the **Iron** item where one exists (range over the
family in brackets). All VERIFIED in Assets.zip. Hold times are the `Charging` `Next` keys (in seconds; nested charges add up).

| Family (gear?) | Root (Primary) | Charging step (hold) | Charged damage step | Class tag | Normal hit | Charged hit |
|---|---|---|---|---|---|---|
| **Sword** (23, yes) | `Root_Weapon_Sword_Primary` (cooldown 0.25) | `Weapon_Sword_Primary` 0.2 s -> stamina check (0.1) -> `Weapon_Sword_Primary_Thrust` 0.65 s | Thrust dash: `Weapon_Sword_Primary_Thrust_Selector` -> var `Thrust_Damage` -> `Weapon_Sword_Primary_Thrust_Damage` | **Charged** | swings 10 / 10 / 18 | **26** (21-51) |
| **Battleaxe** (14, yes) | `Root_Weapon_Battleaxe_Primary` (0.75) | `Weapon_Battleaxe_Primary` 0.2 s -> `..._Downstrike` 0.65 s | var `Downstrike_Damage` -> `Weapon_Battleaxe_Primary_Downstrike_Damage` | **Charged** | 18 / 23 / 36 | **29** (23-57; lower than the 3rd swing on Iron) |
| **Mace** (12, yes) | `Root_Weapon_Mace_Primary` (0.75) | each chain swing: stamina check -> 0.2 s -> `Weapon_Mace_Primary_Swing_{Left,Right,Up_Left}_Charged` 2.0 s | var `Swing_*_Charged_Damage` -> `Weapon_Mace_Primary_Swing_*_Charged_Damage` | **Charged** | 29 | **41** (33-81) |
| **Daggers** (16, yes) | `Root_Weapon_Daggers_Primary` (0.2) | `Weapon_Daggers_Primary` 0.2 s -> `..._Pounce` 0.4 s | Pounce sweep / stab: vars `Pounce_Sweep_Damage`, `Pounce_Stab_Damage` | **Charged**, but the item's **backstab** `AngledDamage` calculator is untagged | 6 / 6 / 8 / 12 | **31** (20-61), backstab e.g. 59 |
| **Axe** (13, yes) | `Axe_Attack` | `Axe_Attack` 1.390 s | `Axe_Swing_Left_Charged` -> var `Axe_Swing_Left_Charged_Damage` | **none** (Unknown) | 17 / 17 | **34** (16-216) |
| **Longsword** (18, yes) | `Longsword_Attack` | `Longsword_Attack` 1.565 s | `Longsword_Stab_Charged` -> var `Longsword_Stab_Charged_Damage` | **none** | 16 x3 | **48** (24-307) |
| **Club, flail + zombie limbs** (9, yes) | `Club_Flail_Attack` | 1.390 s | `Club_Flail_Spin_Swing_Left_Charged` | **none** | 7 / 7 (arm), 19 (steel flail) | **16** (all) |
| **Club, plain** (13, yes) | `Club_Attack` = plain `Chaining` | **none wired** | `Club_Swing_Down_Charged` exists + each club sets `Club_Swing_Down_Charged_Damage` (Iron 34), but nothing reaches it | - | 17 / 17 | **no charged attack** |
| **Void scythe** (`Weapon_Battleaxe_Scythe_Void`, yes) | `Battleaxe_Scythe_Void_Attack` | 1.670 s | `Battleaxe_Swing_Left_Charged` | **none** | 112 | **224** |
| **Spear** (17, yes) | `Spear_Attack` | 1.0 s | `Spear_Throw_Charged` -> **legacy** `LaunchProjectile` `Spear_<Material>` | - (projectile damage) | stab 6 | **throw 15** (10-30) |
| **Shortbow** (13, yes) | `Root_Weapon_Shortbow_Primary_Shoot` | var `Primary_Shoot_Charge`: 0.1 / 0.3 / 0.6 / 0.9 / 1.2 s = draw strength 0-4 | `ProjectileConfig` hit -> var `Primary_Shoot_Damage_Strength_N` | **Charged on EVERY draw** (strength 4 headshot `TargetedDamage` untagged) | - | **6 / 9 / 12 / 16 / 19** (up to 12-37 at full draw) |
| Shortbow Signature Volley (same bows) | same root, when Signature charges are full | 0 / 0.75 / 1.5 s | volley arrows | **Signature** (never counts) | - | - |
| **Crossbow** (2 + 4 More Crossbow Tiers, yes) | `Root_Weapon_Crossbow_Primary_Signature` | **no hold** (`..._Overcharge` = `Simple` 0 s -> reload; unwired) | 3rd bolt in a row on the same target (`EffectCondition` `Crossbow_Combo_2`) -> var `Combo_Projectile_Damage` | **Charged** (a combo, not a charge) | bolt 10 | **27** (MCT Cobalt 43) |
| **Staff** (19 orb staffs, yes) | `Staff_Primary` (Primary and Secondary) | 1.0 s (costs Mana) | `Staff_Cast_*` -> **legacy** `LaunchProjectile` `Skeleton_Mage_Corruption_Orb` | - | melee 5 / 5 | **orb 25** |
| Staff, Crystal Red / Crystal Fire Trork | `Staff_Primary` | 1.0 s | legacy `Fireball` | - | 5 | **60** |
| Staff, Frost | `Staff_Primary` | 1.0 s | legacy `Ice_Ball` | - | 5 | **20** |
| Staff, Crystal Ice | `Root_Ice_Staff_Primary_Wrapper` | 1.0 s | `Projectile_Config_Ice_Ball` -> `Ice_Ball_Damage` | **Charged** | secondary rapid `Ice_Bolt` 5 is **also tagged Charged** (no hold) | **20** |
| Staff, Crystal Flame | `Root_Weapon_Stick_Fire_Primary_Entry` | 0 / 0.5 / 1.0 / 1.5 / 2.0 s | fireball configs -> `Explode_Generic` (10 / 20 / 30 / 40) | - (explosion, no `DamageEntity`) | - | **not detectable** |
| **Wand** (Wood, Tribal, Wood_Rotten; yes) | `Wand_Primary` | 0.35 s (Mana 25) | `Wand_Cast_Left_Charged` -> legacy orb | - | 6 / 8 | **orb 25** |
| Wand Root / Stoneskin | own casts | - | no damage at all | - | - | - |
| **Spellbook** (5, yes) | `Spellbook_Primary` | 1.0 s (Mana 100) | `Spellbook_Cast_Hurl_Charged` -> legacy orb | - | 1 | **orb 25** |
| Spellbook Rekindle Embers | inline | 0.8 s | summons Risen NPCs, no damage | - | - | - |
| **Kunai** (yes) | inline Secondary | - | throw 6, no charge | - | 6 | **no charged attack** |
| Prototype bows `Weapon_Shortbow_Combat/_Pull/_Bomb/_Ricochet` | `Bow_Combat_Shoot_Charging` / `Bow_Ricochet_...` | 0.1 ... 1.0 s | projectile configs | **none** | - | 2 ... 20 |
| Prototype bow `Weapon_Shortbow_Vampire` | `Bow_Shoot_Charging` | 0.2 / 0.6 / 1.0 s | legacy `Arrow_NoCharge` / `_HalfCharge` / `_FullCharge` | - | - | 4 / 2 / 20 |
| Blunderbuss (not gear: `Weapon_Gun` is in `gear.exclude`) | `Gun_Shoot_Flintlock_Charging` | 2.0 s | legacy `Gun_Blunderbuss_Bullet` | - | swing 5 | 200 |
| Claws (not gear: `Weapon_Claws_` excluded) | inline | 2.43 s | `Daggers_Stab/Lunge_Double_Charged` | none | 5 | 5 |
| Arrows / darts used as melee (ammo, not gear) | `Knife_Attack` | 0.5 s | `Knife_Throw_Charged` legacy | - | 1-10 | 2 |

Notes (VERIFIED):
- The Sword, Battleaxe, Mace and Daggers charged steps sit behind a `StatsCondition` (Stamina 0.1). Without stamina the hold falls back to
  the normal swing (`Failed` edge).
- Every vanilla `BaseDamage` map (957 of 957 in `Server/Item`) has exactly one damage cause, so one hit = one `Damage` object (this
  matters in 2.1: the meta key goes on the first `Damage` only).
- `Class` is used ONLY by weapon interactions in all of Assets.zip (18 `Charged`, 14 `Light`, 9 `Signature`); no entity effect (poison,
  burn damage over time) carries a class, so a damage-over-time tick can never look "charged".
- Third-party mods follow the same convention: More Crossbow Tiers' crossbows use `Parent: Template_Weapon_Crossbow` and override
  `Combo_Projectile_Damage` with `Parent: Weapon_Crossbow_Damage_Combo_Projectile` (so the `Charged` tag is inherited); MoreArrows
  (24 `Charged`), H1Z Working Blunderbusses (tags its charged flintlock shot `Charged`), Arcane Power (15 `Charged`) and EndgameAndQoL
  (parents on `Longsword_Stab_Charged_Damage`, `Spear_Throw_Charged_Projectile`) all reuse the vanilla parents or the vanilla tag.

---

## 2. Engine facts (the proof)

### 2.1 The damage class travels on the Damage object (VERIFIED bytecode)

- `DamageClass` enum (`...interaction.config.server.combat.DamageClass`, `public final`): `UNKNOWN, LIGHT, CHARGED, SIGNATURE`.
- `DamageCalculator` (`public`): `getDamageClass()` returns the field `damageClass`; the constructor defaults it to `UNKNOWN`. Its codec
  field `"Class"` is `appendInherited` with the engine's own documentation string: *"The class of the damage being created, used by the
  damage system to apply modifiers based on equipment of the source."*
- `DamageEntityInteraction.attemptEntityDamage0(Source, InteractionContext, Ref, Ref, Vector4d)`:
  - offset 65: `var7 = this.damageCalculator`; offsets 213-231 / 311-351: replaced by the `AngledDamage` / `TargetedDamage` entry's own
    calculator when that entry has one (backstab, headshot).
  - 703-732: `new DamageCalculatorSystems$DamageSequence(sequence, var7)` then `damages[0].putMetaObject(DamageCalculatorSystems.DAMAGE_SEQUENCE, seq)`.
  - 902-908: `commandBuffer.invoke(targetRef, damage)` - the meta key is set **before** the damage event is dispatched.
  - `tick0` 188-213: the source is `new Damage$EntitySource(context.getOwningEntity())` (plain EntitySource, for melee and for
    `ProjectileConfig` hits alike - what `GearHitSys` already expects).
- `DamageCalculatorSystems.DAMAGE_SEQUENCE` is `public static final MetaKey`, registered with `Damage.META_REGISTRY.registerMetaObject()`.
  `DamageCalculatorSystems$DamageSequence` is `public static` with `public DamageCalculator getDamageCalculator()`.
- **Engine precedent for reading it in a damage system:** `DamageCalculatorSystems$SequenceModifier.handle(..., Damage)` offset 13-32:
  `damage.getIfPresentMetaObject(DAMAGE_SEQUENCE)` -> `DamageSequence.getDamageCalculator()`. That system runs AFTER the Gather and
  Filter groups and BEFORE `ApplyDamage` (its constructor), so the meta key is still on the `Damage` while `GearHitSys` (Filter group)
  runs.
- Only three classes write `DAMAGE_SEQUENCE`: `DamageEntityInteraction`, `ActiveEntityEffect.tickDamage` (effect damage over time, whose
  calculators never carry a class in Assets.zip) and nobody else (cpgrep). The legacy `ProjectileComponent` does NOT, so a spear throw
  or a staff orb arrives without it (that is why signal 3 exists).
- `Damage` implements `IMetaStore`; `getIfPresentMetaObject(MetaKey)` is an interface **default** method (reflection). From javassist,
  call it through the interface: `((com.hypixel.hytale.server.core.meta.IMetaStore) d).getIfPresentMetaObject(key)`.
- `DamageCalculator` overrides `equals` / `hashCode` **by value** (bytecode: compares step, minimum, random %, type, base damage). Two
  different steps with the same numbers are "equal", so any lookup table keyed by calculator must be an `IdentityHashMap`.

### 2.2 Hytale's own "charged" rule: the weapon tooltip walk (VERIFIED bytecode)

- `ItemModule.computeWeaponData` handles `LoadedAssetsEvent` for items: for every item with a `Weapon` section it calls
  `WeaponDamageDataCollector.calculate(item, Primary)` -> `ItemWeapon.setBasicDamageBreakdown` and `calculate(item, Ability1)` ->
  `setUltimateDamageBreakdown`. (SkyyGear already reads `getBasicDamageBreakdown` for its base damage line.)
- `calculate`: `rootId = item.getInteractions().get(type)`; `root = RootInteraction.getAssetMap().getAsset(rootId)`;
  `ctx = InteractionContext.withoutEntity()`; `ctx.setInteractionVarsGetter(c -> item.getInteractionVars())`;
  `InteractionManager.walkChain(collector, type, ctx, root)` (all `public`, the walk is `public static`).
- The collector interface `...interaction.config.data.Collector` (public): `start()`, `collect(CollectorTag, InteractionContext,
  Interaction) -> boolean`, `into(InteractionContext, Interaction)`, `outof()`, `finished()`.
- `ChargingInteraction.walk`: for every `Next` entry it walks the child with the edge tag `ChargingInteraction$ChargingTag.of(key)`
  (`getSeconds()` = the `Next` key), and the `Failed` child with `StringTag "Failed"`.
- `WeaponDamageDataCollector.into` (the label rule): edge `ChargingTag` with `getSeconds() > 0` -> label `"charged"`; `ChargingTag` 0 ->
  no label; `AngledDamageTag` -> `"backstab"`; `TargetedDamageTag` -> its key (e.g. `Head`); `StringTag` `"Failed"` or `"Blocked"` ->
  no label; otherwise the parent's label is kept. A `DamageEntityInteraction` records its `getDamageCalculator()` under the label. A
  `ProjectileInteraction` walks `getConfig().getInteractions().get(InteractionType.ProjectileHit)` (a RootInteraction id) with a second
  collector (`applyProjectileHitDamage`).
- Checked against the table in section 1 with the same rule in Python: the sword's 0.2 s edge labels the stamina check "charged", its
  `Failed` edge (no stamina) resets to normal, the nested 0 s edge (released early) resets to normal, the 0.65 s edge labels the thrust
  "charged". Same shape for Battleaxe, Mace, Daggers. Axe / Longsword / Flail / Scythe / Spear / Staff / Wand / Spellbook charged steps
  all sit behind one edge of 0.35 s or more. The shortbow's 0.1-1.2 s draws are all "charged" by this rule.

### 2.3 Inherited tags (VERIFIED codec path, INFERRED at runtime)

An item's override such as `"Thrust_Damage": {"Interactions": [{"Parent": "Weapon_Sword_Primary_Thrust_Damage", "DamageCalculator":
{"BaseDamage": {"Physical": 26}}}]}` names only the damage. The `Class` still arrives: `DamageEntityInteraction`'s `DamageCalculator`
field is `appendInherited`; `BuilderCodec` implements `InheritCodec`; `BuilderField.decodeAndInheritJson` (offsets 75-128) decodes a
nested `InheritCodec` value with the PARENT's value as its base (`InheritCodec.decodeAndInheritJson(reader, parentValue, extra)`), and
`DamageCalculator.Class` is itself `appendInherited`. The game already relies on this (the same overrides also inherit knockback,
particles and camera effects). `AngledDamage` / `TargetedDamage` entries are array / map elements decoded fresh, so the calculator an
item puts inside them has **no** class (backstab, headshot) - VERIFIED in the 12 dagger and 11 shortbow items that do it.

### 2.4 Legacy projectiles (VERIFIED, one INFERRED link)

- `LaunchProjectileInteraction.firstRun` -> `ProjectileComponent.assembleDefaultProjectile(time, this.projectileId, ...)`; the
  component exposes `getProjectileAssetName()` and `getCreatorUuid()` (reflection). That the asset name is exactly `projectileId` is
  INFERRED (the constructor takes the id string).
- The hit is `new Damage$ProjectileSource(shooter, projectile)` from `ProjectileComponent` (Classes spec, callers.py) with no
  `DAMAGE_SEQUENCE`. `GearShotTrack.onEntityAdded` already records every projectile with a `ProjectileComponent` or a
  `StandardPhysicsProvider` by UUID with the shooter's held item; `GearHitSys` finds that record for a `ProjectileSource` hit
  (`GearShotTrack.find`). So a launch-time "charged" flag rides along exactly per projectile.
- `LaunchProjectileInteraction.getProjectileId()` is public, so the walk of 2.2 can list, per item, which projectile ids its charged
  steps launch and which its normal steps launch.

### 2.5 What the SkyyTrees 0.2.4 approach would look like here (for comparison)

SkyyTrees ships an asset pack: two OVERRIDES of vanilla root files (same path and id: `Pickaxe_Attack`, `Hatchet_Attack`) whose new
content is a decision tree of instant `EffectCondition` steps keyed on 40 hidden effects per tool that `TreeTick` puts on the player,
ending in `TriggerCooldown` and the unchanged vanilla interaction. The charged-attack analogue would override each family's charged
step (about 15 vanilla files) to `ApplyEffect` a short hidden "Skyy_Gear_Charged" effect on the user before the damage, and `GearHitSys`
would test the attacker's active effects. It is ranked last in section 3 (timing windows, file conflicts, client prediction).

### 2.6 UNVERIFIED without the game (exact list)

1. That `DAMAGE_SEQUENCE` really is on the `Damage` when `GearHitSys` sees it, for melee AND `ProjectileConfig` arrows (bytecode says
   yes: set at 725-732, dispatched at 902-908; the engine's `SequenceModifier` reads it later in the same dispatch).
2. That an item's inline override inherits `Class: Charged` from its `Parent` in the running asset store (codec path proven, 2.3).
3. That SkyyGear's own walk reaches the same `DamageEntityInteraction` instances the engine runs, so the calculator identity matches.
   Strongly implied: both resolve `Replace` vars through `Item.getInteractionVars()` -> `RootInteraction` -> the `Interaction` asset map,
   and `attemptEntityDamage0` uses the field reference (`getfield damageCalculator`), which is what `getDamageCalculator()` returns.
4. `ProjectileComponent.getProjectileAssetName()` equals the `LaunchProjectile` `ProjectileId` (INFERRED, 2.4).
5. That registering a plugin listener for `LoadedAssetsEvent` (Item / Interaction / RootInteraction) works for the index rebuild; the
   fallback (re-walk an item whose calculator is missing) does not need it.
6. Player feel only, not detection: which `Next` step runs when a hold is released between two keys.

Everything else in this file is VERIFIED.

---

## 3. Detection options, ranked

| # | Option | Reliability | Compatibility with other mods | Effort | Verdict |
|---|---|---|---|---|---|
| **1** | **Engine-native, three signals** (3.1): the `Charged` class via `DAMAGE_SEQUENCE`, plus a charged-calculator index built with the tooltip walk, plus a launch-time flag for legacy projectiles | High (every link proven; mirrors `SequenceModifier` and `WeaponDamageDataCollector`) | Highest: no vanilla file touched; mods that reuse vanilla parents or the tag work unchanged (More Crossbow Tiers, MoreArrows, H1Z, Arcane Power); SkyyTrees' root overrides and a future Attack Speed override are walked like vanilla | Moderate: 4 small classes (~250 lines javassist) + a build-time self-check | **Recommended** |
| 2 | Signal A only + asset overrides that add `"Class": "Charged"` to the 6 untagged vanilla bases (`Axe_Swing_Left_Charged_Damage`, `Longsword_Stab_Charged_Damage`, `Club_Flail_Spin_Swing_Left_Charged_Damage`, `Battleaxe_Swing_Left_Charged_Damage`, `Daggers_Stab/Lunge_Double_Charged_Damage`) | Medium: still misses backstab / headshot calculators and every legacy projectile (needs signal C anyway) | Lower: overrides vanilla files (a mod shipping the same file wins silently); the only engine reader of the class is the attacker-armor `DamageClassEnhancement` lookup (no vanilla armor uses it, VERIFIED), so the side effect is nil today | Low | Fallback if the walk ever breaks |
| 3 | Signal A only | High where it applies | Highest | Tiny | Not enough: the stat would do nothing on Axe, Longsword, Flail, Scythe, Spear, Staff, Wand, Spellbook (about 100 gear items) - breaks Skyy's lock |
| 4 | SkyyTrees-style interaction wrap + hidden effect on the attacker | Low-medium: the effect must outlive the swing but not the next tap; arrows land later; `EffectCondition` client simulation UNVERIFIED | Low: ~15 vanilla file overrides, collides with any mod or future SkyyGear override of the same roots | High | No |
| 5 | Read the attacker's `InteractionManager` chain at damage time | Low: no public link from a `Damage` to the running step; projectile hits run in their own chains | - | High | No |

### 3.1 The recommended design (for the SkyyGear 0.1.2 builder)

**A hit counts as a charged attack when (checked in this order):**
1. The `Damage` has a `DamageSequence` and its calculator's class is `SIGNATURE` -> **not charged** (signature abilities, e.g. the
   shortbow Volley, which charges 0.75 / 1.5 s but is tagged `Signature`).
2. The class is `CHARGED` and Server Setup `charged.classTag` is on -> **charged** (signal A).
3. The calculator is in the charged-calculator index with a charge edge of at least `charged.minSeconds` -> **charged** (signal B).
4. No `DamageSequence` (legacy projectile, `Damage$ProjectileSource`) and the launch record says `charged` -> **charged** (signal C).
5. Anything else -> not charged.

**New classes / fields (javassist-safe: no lambdas, no generics, named classes):**
- `GearChargedVars implements java.util.function.Function` - field `java.util.Map vars`; `apply(Object)` returns it (the vars getter
  the walk needs; `WeaponDamageDataCollector.lambda$calculate$0` returns `item.getInteractionVars()`).
- `GearChargedWalk implements ...interaction.config.data.Collector` - the label stack of 2.2 (a float per frame: -1 = normal, else the
  charge edge seconds). `collect` stores the pending tag and returns false; `into` computes the child label from the pending tag
  (`ChargingTag` > 0 -> its seconds; `ChargingTag` 0 -> -1; `StringTag` Failed / Blocked -> -1; else inherit), pushes it, and:
  - `DamageEntityInteraction` -> record `getDamageCalculator()` plus every `getAngledDamage()[i].getDamageCalculator()` and every
    `getTargetedDamage()` value's `getDamageCalculator()` (non-null) with the label;
  - `LaunchProjectileInteraction` -> record `getProjectileId()` with the label;
  - `ProjectileInteraction` -> walk its `ProjectileHit` root with a NEW `GearChargedWalk` seeded with the current label (the engine uses
    a second collector too; do not re-enter `start()` on the same one).
  `outof` pops. `into` may receive a null interaction (the engine checks) - skip it.
- `GearChargedIndex` - a `volatile java.util.IdentityHashMap` snapshot `DamageCalculator -> Float` (best charged seconds, -1 = only
  normal, -2 = reached both ways = ambiguous), a `ConcurrentHashMap` `itemId -> Boolean hasCharged`, and a `ConcurrentHashMap`
  `itemId + "|" + projectileId -> Integer` (1 charged launch only, 0 normal only, -1 both). `ensure(itemId)` walks every entry of
  `Item.getInteractions()` (Primary, Secondary, Ability1-3 ...; labels keep it correct) under a lock, copies the snapshot, adds the
  item, swaps it in. Reads never lock. Rebuild everything on `LoadedAssetsEvent` for Item / Interaction / RootInteraction when that
  registration works; otherwise a calculator that is missing after `ensure(heldItem)` triggers one re-walk of that item, then counts as
  "unknown" (falls back to rules 1-2 only). One INFO line at start: items walked, charged steps, ambiguous calculators (WARN with ids
  when > 0).
- `GearCharged.isCharged(Damage d, String weaponId, GearShot shot)` - rules 1-5 above. `weaponId` is the item the hit's stats come from
  (`main` for melee, the launch record's `main` for projectiles), used only for `ensure`.
- `GearShot.charged` (new boolean) - set in `GearShotTrack.onEntityAdded` for `ProjectileComponent` shots:
  `GearChargedIndex.launch(mh.getItemId(), lp.getProjectileAssetName()) == 1`.
- Build-time placeholders to add to the existing probe list (the `PB` table and the method-exists asserts around line 896):
  `DamageCalculatorSystems`, `DamageCalculatorSystems$DamageSequence#getDamageCalculator`, `DamageCalculator#getDamageClass`,
  `DamageClass` (`CHARGED`, `SIGNATURE`), `IMetaStore#getIfPresentMetaObject`, `InteractionManager#walkChain`,
  `InteractionContext#withoutEntity/#setInteractionVarsGetter`, `Collector`, `ChargingInteraction$ChargingTag#getSeconds`,
  `StringTag#getTag`, `DamageEntityInteraction#getAngledDamage/#getTargetedDamage`, `TargetedDamage#getDamageCalculator`,
  `LaunchProjectileInteraction#getProjectileId`, `ProjectileInteraction#getConfig`, `ProjectileConfig#getInteractions`,
  `ProjectileComponent#getProjectileAssetName`.
- **Build-time self-check (the SkyyTrees pattern):** port the Python walk used for section 1 into the build script and stop the build
  when Hytale changes what this relies on: each family in section 1 still has its charged step (e.g. `Axe_Attack` is `Charging` with a
  1.390 key to `Axe_Swing_Left_Charged`, `Weapon_Sword_Primary_Thrust_Damage` has `Class: Charged`, `Club_Attack` is still a plain
  `Chaining`). Bake the list of weapon id prefixes with a charged attack into the jar as the pool-filter fallback when the runtime walk
  fails (4.4).

**GearHitSys hook (inside the existing `if (ok[0])` block, before `hitAmount`):**
```java
boolean chg = false;
if (@PKG@.GearCfg.CHG_ON && t[@PKG@.GearHit.I_CHG] != 0) {
  String wid = main == null || main.isEmpty() ? null : main.getItemId();
  chg = @PKG@.GearCharged.isCharged(d, wid, rec != null ? rec : nr);   // rec = ProjectileSource record, nr = plain-source launch record
}
double a = @PKG@.GearHit.hitAmount((double) a0, t, spell, chg, rnd.nextDouble(), rnd.nextDouble());
if (chg && @PKG@.GearCfg.CHG_LOG) @PKG@.GearLog.line("CHARGED " + u + " " + wid + " " + a0 + " -> " + a);
```
The `t[I_CHG] != 0` test means a player without the stat never pays for the lookup. The existing record variables in `GearHitSys` are
`rec` (ProjectileSource path) and `nr` (plain-EntitySource projectile path); both are `GearShot`.

---

## 4. The modifier

### 4.1 Name, key, unit, slots

- **Name: "Charged Attack Damage"** (tooltip label, 21 characters; the longest current label is 20). It says what it does in Hytale's
  own terms. Rejected: "Charge Damage" (sounds like a dash), "Heavy Attack Damage" (Hytale never says heavy), Wynn's "Main Attack
  Damage %" (Scrap in the catalog and means something else).
- **Key: `chg`** (matches the STATS key rule `^[a-z][a-zA-Z]*$`, unique; not `cd`-anything, so it is never confused with Crit Damage).
- **Unit: %.**  **Slots: `wa`** (weapons and armor, Skyy's ask). Equipment later if Skyy wants it (`wae`).
- **Live: 1** (it only ships together with the detection).

### 4.2 Numbers (PLACEHOLDER, same machinery as every stat)

Proposed STATS row: `("chg", "Charged Attack Damage", "wa", "%", 30, 5, 1, "")` - max 30 at 100 % power like Damage and Crit Damage (the
closest conditional multiplier), weight 5 like the other situational lines (Life Steal, Health Regen %), because it only fires on the
slow charged hits. Rolls follow spec 2.3 (`v = randInt(round(max x low% x f), round(max x high% x f))`, Java `Math.round`):

| Rarity (low-high power) | f = 25 % (Crude, Wood) | f = 55 % | f = 100 % (full-level gear) |
|---|---|---|---|
| Normal (30-60 %) | 2-5 % | 5-10 % | 9-18 % |
| Unique (35-70 %) | 3-5 % | 6-12 % | 11-21 % |
| Rare (40-80 %) | 3-6 % | 7-13 % | 12-24 % |
| Legendary (45-95 %) | 3-7 % | 7-16 % | 14-29 % |
| Fabled (50-110 %) | 4-8 % | 8-18 % | 15-33 % |
| Mythic (60-130 %) | 5-10 % | 10-21 % | 18-39 % |
| Set (45-95 %) | 3-7 % | 7-16 % | 14-29 % |

(With the 0.1.1 level table Iron 15 gives f = 47.5 %, Mithril / Onyxium 40 give f = 85 %.) A full Mythic set (weapon + 4 armor) tops
out near +195 % on charged hits only - the same ceiling Crit Damage has on crits. Skyy tunes it in Server Setup -> Gear -> Stats.

### 4.3 How it combines

`GearHit.hitAmount` gets one more parameter and one more factor, a **separate multiplier** after Strength / Magical Power and before the
crit roll:

```
a = amount x (1 + Damage%/100) x (1 + (Strength or Magical Power) x per/100) x (1 + Charged Attack Damage%/100 if charged) x crit x overcrit
```

- Separate (not added into Damage %), so it stays worth rolling on a weapon that already has high Damage %; the factor is clamped at 0
  like the others (gear:extra may be negative).
- Crits multiply it (a charged crit gets both). Hytale armor and SkyyGear Defense reduce the result as usual.
- True Damage and the flat element lines are NOT multiplied (they are added after armor by `GearTrueSys`, design review 8 / lock 17).
- Totals: `GearStats.totals` sums it from the weapon and every active armor piece plus `gear:extra` (it is not weapon-only).
  `gear:stats:<uuid>` and `/gear` pick it up through `S_KEYS` automatically.
- Bows: every drawn arrow counts by default (Hytale tags every shortbow draw `Charged` and its tooltip calls every draw charged), so on a
  bow it behaves like "bow damage %" that grows with the draw's own damage. `charged.minSeconds` 0.9 would limit the WALK signal to the
  last two draws, but the class tag still counts every draw unless `charged.classTag` is off (Q2).
- Staffs, wands, spellbooks: the orb IS their charged attack (it can only be launched by holding), so every spell hit counts. Spells use
  Magical Power and Strength is for melee (lock 22); Charged Attack Damage stacks on top of either (Q3).
- Crossbows: the 3rd bolt in a row on the same target counts (Hytale's `Charged` class). The crossbow has no hold-to-charge in vanilla.
- Stats order in the table: insert the row right after `cd` (display order = table order: Damage, Strength, Magical Power, Crit Chance,
  Crit Damage, Charged Attack Damage, True Damage ...). Gear documents store modifiers by key name (`GearData.mod(key, value)`), so the
  new index shifts nothing on saved items; update the two asserts that pin `SPEC_KEYS` / the live list, and spec 4.2.

### 4.4 Where it may roll (Skyy's "never roll a stat that does nothing")

- **Weapons:** only items for which `GearChargedIndex` finds a charged damage step, a `Charged`-class step, or a charged launch
  (`hasCharged(itemId)`, checked in `GearRoll` when the pool is built; crafting, identify, reforge and `/gear give` all go through it).
  Vanilla result: it rolls on Sword, Longsword, Axe, Battleaxe (incl. Void scythe), Mace, Daggers, flail clubs, Spear, Shortbow
  (incl. prototypes), Crossbow (incl. More Crossbow Tiers), orb Staffs, Frost / Crystal Ice / Crystal Red / Crystal Fire Trork staffs,
  the 3 damage wands and the 5 damage spellbooks. It does NOT roll on the 13 plain Clubs, the Kunai, the Crystal Flame staff, Wand Root /
  Stoneskin, Spellbook Rekindle Embers.
- **Armor:** always in the pool (armor helps whatever weapon is held, like Magical Power on armor).
- **`charged.on` OFF** -> the stat leaves the pool too (it would do nothing), exactly like `pool.later` treats coming-later stats; items
  that already have it keep the line (grey "off on this server" suffix is optional polish).
- If the runtime walk fails (engine change), the pool falls back to the baked prefix list from the build-time self-check.

### 4.5 Server Setup rows (kit tuple order: key, label, cat, type, default, min, max, opts, unit, flags, help, bind)

```python
("charged.on", "Charged Attack Damage in combat", "combat", "bool", "true", "", "", "", "", "live",
 "Charged Attack Damage boosts charged hits. Off = it does nothing and stops rolling.", "field:GearCfg.CHG_ON"),
("charged.classTag", "Count hits Hytale tags Charged", "combat", "bool", "true", "", "", "", "", "live,adv",
 "Also count Hytale's own Charged hits: every bow draw, the crossbow 3rd hit, other mods.", "field:GearCfg.CHG_CLASS"),
("charged.minSeconds", "Shortest charge that counts", "combat", "dec", "0", "0", "10", "", "s", "live,adv",
 "Hold-to-charge hits count from this charge step. 0 = every step Hytale calls charged." + PH, "field:GearCfg.CHG_MIN"),
("charged.log", "Log charged hits", "combat", "bool", "false", "", "", "", "", "live,adv",
 "One gear.log line per charged hit (testing only).", "field:GearCfg.CHG_LOG"),
```
plus the automatic `stat` table row `stats.chg = 30,5` (Max at 100 % | Weight) from the STATS entry. All help texts are under the kit's
100-character limit.

### 4.6 Tooltip and commands

- Modifier line, same look as every % line: **`Charged Attack Damage: +12%`** (Unique colour rules unchanged). No suffix needed.
- Optional polish: the weapon's base damage line can also show Hytale's own "charged" row from `ItemWeapon.getBasicDamageBreakdown()`
  (entries with label key `charged`, e.g. Iron sword "Charged 26"), so players see what the stat multiplies.
- New ADMIN sub-command **`/gear charged`** (read-only probe; `requirePermission("skyygear.admin")` + `setPermissionGroups(new String[0])`):
  prints the held item's charged steps from the index - count, charge seconds, class tag, base damage range, charged launches, and
  "no charged attack" when `hasCharged` is false.

---

## 5. Open questions for Skyy

1. **Clubs have no charged attack in this Hytale build** (the charged down-swing is in the files, `SwingDownCharging` / `SwingDownCharged`
   animations exist, every club already sets its damage, e.g. Iron 34 vs 17). Keep clubs without the stat, or wire it later with an
   override of `Club_Attack` shaped like `Axe_Attack` (a 1.39 s charge)? That override changes vanilla weapon behaviour (SkyyClasses /
   Berserker territory). Default: leave clubs alone; the stat does not roll on them.
2. **Bows:** every drawn arrow counts (Hytale's own view), or only the last draws (0.9 s+, set `charged.classTag` off +
   `charged.minSeconds` 0.9)? Default: every draw.
3. **Spells:** every staff / wand / spellbook orb counts, so for a Mage or Priest the stat acts like extra spell damage on every cast. OK?
   Default: yes.
4. **Crossbow:** the 3rd-bolt combo counts as its charged attack. OK? Default: yes.
5. **Numbers:** max 30 %, weight 5 (placeholders).

---

## 6. Probe and test plan (in game, after the 0.1.2 build)

Setup: Server Setup -> Gear -> Combat `charged.log` ON; an admin test item with Charged Attack Damage (reroll with `/gear reroll` until
it shows, or give a Mythic); a training target or passive mob; `/gear read` to see the line.

1. `/gear charged` holding one weapon of each family: the list matches section 1 (counts and hold times); plain Club, Kunai and Crystal
   Flame staff say "no charged attack". The start log shows items walked / charged steps / 0 ambiguous.
2. Sword: tap swings -> no `CHARGED` line in gear.log; hold until the thrust dash -> one `CHARGED` line, damage = normal x (1 + stat).
   Hold with no stamina -> normal swing, no line.
3. Same for Battleaxe downstrike, Mace charged swing (2.2 s), Daggers pounce (also from behind = backstab), Axe (1.39 s), Longsword stab
   (1.565 s), flail spin, Void scythe.
4. Shortbow: tap, half draw, full draw -> all logged (default); full-draw headshot logged. Signature Volley -> never logged.
5. Crossbow (vanilla Iron and a More Crossbow Tiers one): bolts 1 and 2 on one target not logged, bolt 3 logged.
6. Spear: stab not logged, throw logged; throw then swap to another weapon before it lands -> still logged (launch record).
7. Staff, wand, spellbook orbs (need Mana): logged; staff melee not logged. Crystal Ice charged ball logged (its rapid bolt too - Hytale
   tags it Charged; note it).
8. Armor only: plain weapon + a chest piece with the stat -> charged hits boosted, normal hits unchanged.
9. `charged.on` OFF -> no lines, no bonus, and 30 rerolls of a sword / chest piece never show the stat. Clubs never roll it with the
   switch ON either (armor still can).
10. Crit + charged: with high Crit Chance a charged crit shows both factors in the logged numbers.
11. Two players, two worlds: no cross-talk; no lag spike at start or at the first hit of a new weapon.

Bare-JVM harness additions (`test_skyygear_0.1.2.py`): `hitAmount` with and without `chg` (factor, clamps, crit order); the
`GearChargedWalk` label machine driven directly with `ChargingTag.of(0.2f)`, `ChargingTag.of(0f)`, `StringTag.of("Failed")`,
`ChargingTag.of(0.65f)` and a reflectively built `DamageEntityInteraction` / `DamageCalculator` (constructible: both have public no-arg
constructors); the rule order of `isCharged` with a fake `IdentityHashMap` snapshot (Signature beats everything, class tag switch,
minSeconds, ambiguous -> not charged, legacy flag only without a sequence); every class loads under `-Xverify:all`.
