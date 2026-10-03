# Crit indicator: how damage numbers reach the client, and how SkyyGear can make crits stand out (engine research)

*Written 2026-10-03. Read-only research. Only this file was written. Scratch dumps lived under `tools/dev/scratch/critnum/` and were
deleted afterwards. No build script, jar, doc or game file was touched.*

*Skyy's ask (2026-10-03, verbatim, OPEN-QUESTIONS "LOCKED 2026-10-03"): "we need the numbers to change for a crit indicator, like make
the damage numbers bold and red on crit or something."*

*Inputs: `tools/AGENT-BRIEF.md`; `SkyyGear/build_skyygear_0.2.1.py` (the SET pin: GearHit.hitAmount / weaponHit, GearHitSys, GearLeechSys,
GearFx.setup, the dmg_system helper, Gear.regSetting); `research/Settings-Spec.md` 1.3; `research/Vanilla-UI-Style-Guide.md` (fonts).
Engine checks against the release `HytaleServer.jar` (Implementation-Version 0.6.8) with `tools/dev` (reflect / bcfull / clinit / cpgrep /
callers style dumps); `Assets.zip` read in memory; the client's own files read-only (`Client/Data/Game/Interface/InGame/EntityUI/*.ui`,
`Client/Data/Shared/UI/Fonts/*.json`, printable strings of `HytaleClient.exe`); installed mods read-only (copies in scratch, ideas only,
no code copied): `MMOSkillTree-1.6.0.jar`, `Perfect Parries-0.9.4.jar`, `StunningCombat-1.4.0.jar`, `NotEnoughPotions-2.3.0.jar`,
`MGAspectro.jar`, `HyboardsPack3.4.jar`, `Alec's Tamework! v3.4.5.jar`, `EndlessLeveling.jar` (all 258 files in `UserData/Mods` were
scanned for combat-text / entity-UI / crit references).*

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode, `Assets.zip`, the client's files or an installed mod's bytecode / JSON.
INFERRED = strongly implied, not proven. UNVERIFIED = needs an in-game test.

---------------------------------------------------------------------------------------------------------------------------------------

## 0. The answer in plain words

- **A damage number is a tiny per-hit message with only two things in it: the text (the damage as a whole number) and the hit angle.**
  No colour, no size, no "crit" flag. Colour, size and animation come from ONE shared style the server sends when you join
  (`Server/Entity/UI/CombatText.json`: white `#ffffff`, 48 px, 0.4 s). (VERIFIED)
- **Vanilla numbers are already bold.** The client's own `CombatText.ui` says `RenderBold: true`. That file lives in the client, not in
  `Assets.zip`, so no server can change bold or the font. "Bigger" is possible (font size), "bolder" is not. (VERIFIED)
- **What a server CAN do on a crit** (best first):
  1. **Red + bigger number.** Ship a second, red style and, only for the player who hit, switch that one mob to the red style for about
     half a second around the crit. The crit's own number is then drawn red and bigger. The mod MMOSkillTree 1.6.0 (installed on Skyy's
     PC, same server branch) does exactly this for its crits. (VERIFIED in its bytecode; the client side is UNVERIFIED by us)
  2. **An extra "CRIT!" popup** next to the number (a second message to the same player). Zero risk. (VERIFIED: two mods do it)
  3. **Vanilla's own crit sparks**: the `Impact_Critical` particle burst that Hytale plays on dagger backstabs and bow headshots, plus an
     optional hit sound. (VERIFIED)
- **Vanilla has no special number for headshots, backstabs or charged hits.** Its only "crit look" is that `Impact_Critical` spark burst.
- **Numbers only ever go to the player who dealt the damage** (nobody else sees your numbers), so a red crit number is per player by
  design; the sparks can be "only you" or "everyone nearby".
- **Recommendation (section 9):** do 1 + 2 + 3 in the next SkyyGear, behind settings, after a short probe build that settles the two
  client questions in section 8.

---------------------------------------------------------------------------------------------------------------------------------------

## 1. How a damage number travels (VERIFIED unless marked)

### 1.1 The damage pipeline (where things happen)

`Gather group -> Filter group -> DamageSystems$ApplyDamage (health is subtracted) -> Inspect group`.
Proof: `DamageSystems$ApplyDamage.<clinit>` builds `DEPENDENCIES = { SystemGroupDependency(AFTER, getGatherDamageGroup()),
SystemGroupDependency(AFTER, getFilterDamageGroup()), SystemGroupDependency(BEFORE, getInspectDamageGroup()) }`.

| Group | Systems that matter here |
|---|---|
| Filter | SkyyGear `GearHitSys` (crit roll, BEFORE `ArmorDamageReduction`), engine armor, `GearArmorSys`, `GearTrueSys` |
| (between) | `DamageSystems$ApplyDamage` - the health change |
| Inspect | `DamageSystems$EntityUIEvents` (**the number**), `$PlayerHitIndicators` (victim's indicator), `$ApplyParticles`, `$ApplySoundEffects`, `$HitAnimation`, `$ReticleEvents`; SkyyGear `GearLeechSys` (unordered) |

A cancelled Damage reaches no later system: `EventSystem.shouldProcessEvent` returns false for a cancelled `ICancellableEcsEvent`, and
`EntityEventSystem.handleInternal` returns early on false. So a number (and anything SkyyGear adds in Inspect) only appears for damage that
landed.

### 1.2 The sender: `DamageSystems$EntityUIEvents` (Inspect group)

Query = `Visible AND UIComponentList` (constructor). `handle(int, ArchetypeChunk, Store, CommandBuffer, Damage)`, in order:
1. `if (damage.getAmount() <= 0) return;`
2. source must be `Damage$EntitySource` (`Damage$ProjectileSource extends Damage$EntitySource`, so arrows / bolts / spell projectiles
   count; fall, drowning, environment, commands never show a number);
3. attacker `Ref` valid; attacker must have a valid `PlayerRef` (**only players get numbers**);
4. attacker's `EntityTrackerSystems$EntityViewer` component (via `commandBuffer.getComponent(attackerRef, EntityViewer.getComponentType())`);
5. `Float angle = damage.getIfPresentMetaObject(Damage.HIT_ANGLE)`;
6. `queueUpdateFor(targetRef, damage.getAmount(), angle, viewer)`:
   `viewer.queueUpdate(targetRef, new CombatTextUpdate(angle == null ? 0 : angle, Integer.toString((int) Math.floor(amount))))`.

This is the **only** place in the whole server jar that builds a `CombatTextUpdate` (cpgrep over every class). So the number goes to
exactly one client: the attacker's.

### 1.3 The per-hit packet: `com.hypixel.hytale.protocol.CombatTextUpdate`

`extends ComponentUpdate` (type `ComponentUpdateType.CombatText`). Fields: **`public float hitAngleDeg; public String text;`** - nothing
else. `NULLABLE_BIT_FIELD_SIZE = 0`: the text is not nullable (never send null). `MAX_SIZE` 16 MB (no practical length limit).

It travels inside `protocol.EntityUpdate { int networkId; ComponentUpdateType[] removed; ComponentUpdate[] updates; }`.
`EntityViewer.queueUpdate(Ref, ComponentUpdate)`: throws `IllegalArgumentException("Entity is not visible!")` when the target is not in
`viewer.visible`, else `updates.computeIfAbsent(ref, ...).queueUpdate(update)`; `EntityTrackerSystems$EntityUpdate.queueUpdate` is a plain
`List.add` under a `StampedLock`, and `toUpdatesArray()` keeps list order. **Several updates for one entity in one tick are all sent, in
the order they were queued - no de-duplication.** That ordering is what makes trick 1 work (a style switch queued before the number).

### 1.4 The style: `EntityUIComponent` assets (`Server/Entity/UI/*.json`)

`EntityUIModule.setup`: asset store path `"Entity/UI"`, codec types `"EntityStat"` (`EntityStatUIComponent`) and `"CombatText"`
(`CombatTextUIComponent`), animation event types `"Scale"`, `"Position"`, `"Opacity"`. Vanilla ships exactly two assets:

| Asset | Content |
|---|---|
| `Server/Entity/UI/CombatText.json` | `Type CombatText`, `HitboxOffset (0,-100)`, `RandomPositionOffsetRange X 20-60 / Y 10-30`, `ViewportMargin 100`, `Duration 0.4`, `HitAngleModifierStrength 2.0`, `FontSize 48`, `TextColor #ffffff`, `AnimationEvents`: Scale 0-0.4 (1 -> 0.5), Position 0.1-1 (Y -80), Opacity 0.4-1 (1 -> 0) |
| `Server/Entity/UI/Healthbar.json` | `Type EntityStat`, `EntityStat Health`, `HitboxOffset (0,-30)` |

Every `CombatTextUIComponent` field is `appendInherited` (a `"Parent": "CombatText"` delta works). **Validators (an asset outside them
fails to load):** `StartScale` / `EndScale` range **0..1** (no "scale punch" above 1 - bigger must come from `FontSize`), `StartAt` /
`EndAt` 0..1 (fractions of `Duration`), `Duration` 0.1..10, `ViewportMargin` up to 200, `HitAngleModifierStrength` up to 10,
`TextColor` / `AnimationEvents` / `RandomPositionOffsetRange` non-null.

The client gets the styles from `protocol.packets.assets.UpdateEntityUIComponents` (packet id 73, compressed: `UpdateType type; int maxId;
Map<Integer, protocol.EntityUIComponent> components`), built by `EntityUIComponentPacketGenerator` (`Init` at join, `AddOrUpdate` /
`Remove` on asset changes). The protocol `EntityUIComponent` carries `combatTextColor`, `combatTextFontSize`, `combatTextDuration`,
`combatTextAnimationEvents`, `combatTextRandomPositionOffsetRange`, `combatTextViewportMargin`, `combatTextHitAngleModifierStrength`.

### 1.5 Which style an entity uses: the `UIComponentList` component

- `UIComponentSystems$Setup` (HolderSystem, query `AllLegacyLivingEntityTypesQuery` = every living entity incl. players) ensures a
  `UIComponentList` and calls `update()`.
- `UIComponentList.update()`: `next = EntityUIComponent.getAssetMap().getNextIndex(); if (componentIds.length <= next) { componentIds =
  Arrays.copyOf(componentIds, next); for (i = oldLen; i < next; i++) componentIds[i] = i; }` - **every living entity carries EVERY loaded
  EntityUI asset.** The saved `"Components"` name list is ignored (the codec's `afterDecode` sets `componentIds = EMPTY` and calls
  `update()`).
- `UIComponentSystems$Update` (QUEUE_UPDATE_GROUP) sends `protocol.UIComponentsUpdate { int[] components }` (not nullable) **only to
  viewers the entity just became visible to** (`Visible.newlyVisibleTo`). `UIComponentSystems$Remove` only sends a remove when the
  component goes away; `onComponentSet` / `onComponentAdded` do nothing.
- On every `LoadedAssetsEvent` for `EntityUIComponent`, `EntityUIModule.onLoadedAssetsEvent` runs `update()` on every list in every world.
- Consequence A: a `UIComponentsUpdate` a mod queues to ONE viewer stays in effect for that viewer until the mod sends another one or the
  entity leaves and re-enters view (then vanilla re-sends the real list).
- Consequence B: **if a mod ships a second CombatText asset, every living entity gets it** - and (MMOSkillTree's notes, section 3) the
  client draws one popup per CombatText component, i.e. two numbers on every hit for every player, unless the mod strips its asset from
  the lists.
- `EntityUIComponent.getAssetMap().getIndex(key)` is case-insensitive and returns `Integer.MIN_VALUE` for an unknown key; `getAsset(int)`
  returns null out of range.

### 1.6 The client side (read-only look)

- `Client/Data/Game/Interface/InGame/EntityUI/CombatText.ui`: `Group #Container { LayoutMode: Middle; Anchor (200 x 200) }` holding
  `Label #Text { Style: (HorizontalAlignment: Center, VerticalAlignment: Center, RenderBold: true) }`. Client-local file (not in
  `Assets.zip`) - servers cannot change it. No `FontName` = the Default font = NunitoSans (style guide).
- NunitoSans glyph tables (`Client/Data/Shared/UI/Fonts/NunitoSans-*.json`, 566 glyphs): ASCII, Latin-1 (`¡ × »`), some punctuation
  (`• … † ‡ ‹ ›`). **Missing: ★ ✦ ✶ ⚔ ⚡ ✖ ❤ ▲ ↑.** Marker text must stay ASCII / Latin-1.
- Markup: the client has a markup parser (`<color is="#...">`, `<b>`, `<i>` appear in `client.lang` strings) and a `MarkupEnabled`
  property, but no `.ui` file uses `MarkupEnabled` and the combat-text label does not set it. INFERRED: `<color ...>` inside
  `CombatTextUpdate.text` would show as literal text. Do not use.
- Client class names (strings in `HytaleClient.exe`, NativeAOT, logic not readable): `ClientCombatTextUIComponent`,
  `CombatTextUIComponentRenderer`, `EntityUIComponentRenderer`1`, `EntityUIContainer`, `EntityUIDrawTask`; settings
  `client.settings.displayCombatText` (**a player can hide all numbers**), `EntityUIMaxEntities`, `EntityUIMaxDistance`,
  `EntityUIHideDelay`, `EntityUIFadeIn/OutDuration`. A world can also turn numbers off (`CombatConfig.DisplayCombatText` ->
  `ClientFeature.DisplayCombatText`).

### 1.7 The victim side (not the numbers - for completeness)

`DamageSystems$PlayerHitIndicators` (Inspect) sends `protocol.packets.player.DamageInfo { Vector3d damageSourcePosition; float
damageAmount; protocol.DamageCause damageCause }` to a **damaged player**. `protocol.DamageCause = { String id; String damageTextColor }`
(from the `DamageTextColor` key of `Server/Entity/Damage/*.json`; vanilla sets it only on `Poison.json` = `#00FF00`). `DamageCause.toPacket()`
is called nowhere else, so `DamageTextColor` never reaches the attacker's numbers. The client textures
`Common/UI/DamageIndicators/HitIndicatorBasic / Blocked / Critic / Melee.png` are the victim's direction arrows; the client picks one
(the packet has no crit flag). Neither helps a crit number on a mob.

---------------------------------------------------------------------------------------------------------------------------------------

## 2. Vanilla special hits (VERIFIED)

- **No special number style exists** for crits, headshots, backstabs or charged hits (one `CombatTextUpdate` constructor call in the
  whole jar, always the floored amount, always the one shared style).
- Special hits are interaction JSON: `AngledDamage` (dagger backstab: `Angle 180, AngleDistance 80`) and `TargetedDamage.Head`
  (`Weapon_Shortbow_Primary_Shoot_Damage_Strength_4.json`, `DamageCalculator Class Charged` - the strongest charge step) replace the
  hit's `DamageEffects` with
  **`WorldParticles: Impact_Critical`** (daggers also switch the sound to `SFX_Daggers_T2_Stab_Impact`). 33 vanilla files use
  `Impact_Critical` (dagger and shortbow interactions, every dagger / shortbow item's `InteractionVars`, the deprecated sword swing down).
- `Server/Particles/Combat/Impact/Critical/Impact_Critical.particlesystem` = spawners `Impact_Critical_Flash`, `_Sparks`, `_Sparks_Red`,
  `_Sparks_Small`. (There is also a `Critical` weapon trail, `Server/Entity/Trails/Critical.json` - a trail, not a per-hit effect.)
- No vanilla sound event is named crit / headshot / backstab; only `SFX_Daggers_T1/T2_Stab_Impact` come close.
- **How SkyyGear triggers vanilla's crit look:** `ParticleUtil.spawnParticleEffect("Impact_Critical", Vector3dc pos, ComponentAccessor)`
  (all players within 75 blocks - the overload's hard-coded radius) or `spawnParticleEffect("Impact_Critical", pos, List<Ref> players,
  accessor)` (only those players). SkyySkills 0.4.14 already compiles the list form (`spawnParticleEffect("Impact_Feathers_Black", p,
  java.util.Collections.singletonList(ref), store)`) and `SoundUtil.playSoundEvent3d(SoundEvent.getAssetMap().getIndex(...),
  SoundCategory.SFX, pos, store)`. Position: `Damage.HIT_LOCATION` meta (`Vector4d`) when present, else the target's `TransformComponent`
  position (vanilla `ApplyParticles` does the same).

---------------------------------------------------------------------------------------------------------------------------------------

## 3. How installed mods do it (read-only, ideas only - none is enabled in the "HUD mod" test world)

The test world's `config.json` enables only the Skyy mods + `Serj:More Crossbow Tiers` + `Helios:Saplings From Trees`. No deployed Skyy
jar touches combat text or entity UI today.

| Mod | What it does (VERIFIED in its bytecode / JSON) | Take-away |
|---|---|---|
| **MMOSkillTree 1.6.0** (Ziggfreed; ServerVersion `>=0.6.0-pre.13 <0.7.0`, same branch as our 0.6.8) | Ships `Server/Entity/UI/MMO_CombatText_Red.json` and `_Gold.json` (`"Parent": "CombatText"`, red / gold `TextColor`, bigger `FontSize`, `Duration 0.5`). **`EntityCombatTextSanitizeSystem`**: HolderSystem on `UIComponentList`, ordered AFTER `UIComponentSystems$Setup` (unordered fallback ctor), sets the protected `componentIds` by reflection to the list minus every `CombatTextUIComponent` index except vanilla `"CombatText"`. **`ColoredCombatTextService.applyForViewer`**: if the target is in `viewer.visible`: `viewer.queueUpdate(target, new UIComponentsUpdate(nonCombatTextIds + styleIdx))`, then `viewer.queueUpdate(target, new CombatTextUpdate(angle, text))`, then queues a restore = `UIComponentsUpdate(originalIds)` due **520 ms** later (expires after 5 s), drained every tick by one of its ticking systems (checks both refs valid + still visible). Its crit roll sits in the **Filter** group and emits `"CRIT!"` (lang key, angle -20) in the red style - so vanilla's own number for that hit (Inspect, later in the same dispatch) is ALSO drawn red. Its asset comment: "the client renders one popup per CombatText component, so each colour genuinely needs its own asset". | The full recipe for a red crit number, field-tested on our server branch. |
| **Perfect Parries 0.9.4** | `CombatLabelEmitterSystem` (Inspect) -> `CombatLabel.showLabelToViewer`: `new CombatTextUpdate(0, "CRITICAL" / "PARRIED" / "STUNNED" ...)` to the attacker's viewer (or every viewer). Registers its own Damage meta key with `Damage.META_REGISTRY.registerMetaObject(Function)`. | A text marker is a one-liner; uppercase ASCII words. |
| **StunningCombat 1.4.0** | `DamageNumberSystem` (Inspect, BEFORE `EntityUIEvents`) draws numbers as **particles** (`NumberParticleRenderer`, ~586 asset files: digit textures + `SC_Dig*` / `SC_DigCrit*` systems) to nearby players, then **`damage.setAmount(0)`** so vanilla's number is skipped. | Full control of the look, but asset-heavy and the `setAmount(0)` hack breaks every later Inspect reader of the amount (SkyyGear's own `GearLeechSys` life steal reads `d.getAmount()` in Inspect). Not for SkyyGear. |
| **NotEnoughPotions 2.3.0** | `HideHealthBarInteraction`: reflection on `UIComponentList.components` / `componentIds` + a live `UIComponentsUpdate` to every viewer (hides a morphed player's health bar). | More field proof that a live mid-life `UIComponentsUpdate` is accepted by the client. |
| **MGAspectro** | `Server/Entity/Damage/Red_Text_Fire.json` etc. (`DamageTextColor`) used by its weapons. | Per 1.7 that colour only reaches a damaged player's `DamageInfo`; it does not colour the attacker's numbers. |
| HyboardsPack 3.4 / Alec's Tamework 3.4.5 / EndlessLeveling | Constant-pool references only (not dumped): `HyboardGlideDamageMaskSystem` names `DamageSystems$EntityUIEvents` (an ordering dependency), Tamework's `InteractionPresentationEffects` queues its own `CombatTextUpdate` to an `EntityViewer`, EndlessLeveling augments name `Impact_Critical`. | Same building blocks. |

---------------------------------------------------------------------------------------------------------------------------------------

## 4. What a server mod can change per hit (ranked)

| # | Change | What the player sees | Who sees it | Risk | Evidence |
|---|---|---|---|---|---|
| 1 | **Crit style swap** (crit asset + strip + per-viewer `UIComponentsUpdate` before the number + timed restore) | The crit's own number red and bigger (font size 60+, own animation) | Attacker only | Medium: needs the strip (else double numbers for all), a restore window (other numbers on that mob turn red for ~0.5 s), client behaviour UNVERIFIED by us | MMOSkillTree 1.6.0 (VERIFIED bytecode) |
| 2 | **Marker popup** (extra `CombatTextUpdate`, e.g. `"CRIT!"`, `"CRIT!!"` on an overcrit) | A second popup next to the number; red too when combined with 1 | Attacker only | None (plain vanilla message, ASCII text, never null) | Perfect Parries, MMOSkillTree (VERIFIED) |
| 3 | **Vanilla crit sparks** `Impact_Critical` (+ optional `SFX_Daggers_T2_Stab_Impact`) | Red/white spark burst on the mob - the backstab / headshot look | Choice: attacker only (list) or everyone within 75 blocks | None | Vanilla JSON + `ParticleUtil` (VERIFIED) |
| 4 | Change the number's TEXT (e.g. `"123!"`) | - | - | Only by suppressing vanilla's own number (`setAmount(0)` in Inspect = breaks life steal and other Inspect readers; or replacing `EntityUIEvents`) | Not recommended |
| 5 | Particle digits (StunningCombat style) | Custom-drawn numbers | Everyone nearby | Hundreds of assets + needs 4's suppression | Not recommended |
| 6 | Client-only style via a per-player `UpdateEntityUIComponents` (no server asset, no strip) | Same as 1 | Attacker only | A later real asset update can shrink the client's table -> an unknown index -> client error / disconnect risk; no mod does it | Probe only, not recommended |
| 7 | Markup / symbols in the text | - | - | Markup likely shown literally (1.6); ★ ✦ ⚔ not in the font | No |
| 8 | Bold | Already bold | - | Client file, cannot change | No |
| 9 | Damage-cause colour (`DamageTextColor`) | Only a damaged PLAYER's own indicator | PvP victim | Changes the cause (resistances, kill text, SkyyGear family checks) | No |

---------------------------------------------------------------------------------------------------------------------------------------

## 5. The exact hook for SkyyGear (next version after 0.2.1; SkyyGear has no patch scripts - copy the finished script)

Line numbers are `build_skyygear_0.2.1.py` today; the class.method is the anchor.

### 5.1 Where the crit is decided

- `GearHit.hitAmount(double amount, int[] t, boolean spell, boolean chg, double r1, double r2)` (line 8720): `ch = (GearCfg.CRIT_BASE +
  t[I_CC]) / 100.0; crit = ch > 0 && r1 < ch; overcrit = crit && ch > 1 && r2 < ch - 1` - the crit is never returned, only the amount.
- Its only weapon caller: `GearHit.weaponHit(...)` (line 9721), line 9750:
  `double a = hitAmount((double) a0, t, spell, chg, rnd.nextDouble(), rnd.nextDouble());`
- `weaponHit` runs from `GearHitSys` (Filter, BEFORE `ArmorDamageReduction`, `dmg_system(ghsy, ...)` line 9786), which stores the
  per-Damage `Object[] info` with `GearHit.put(d, info)` (line 9884, IdentityHashMap `GearHit.INFO`). `GearLeechSys` (Inspect,
  **unordered**, line 9930) does `GearHit.take(d)` - so do NOT hang the crit flag on `INFO` (the crit system could run after the take).

**Change:** draw `double r1 = rnd.nextDouble(), r2 = rnd.nextDouble();` into locals, keep the hitAmount call, then compute the level
with the same formula (0 none, 1 crit, 2 overcrit) - or add a `hitAmount` overload that writes the level into an `int[1]`. When level > 0
and `a > 0`, record it in a NEW table `GearHit.CRIT` (IdentityHashMap Damage -> Integer, same 512-entry clear rule and synchronized
put / take helpers as `INFO`). Optional: also feed the existing `/gear charged`-style probe so an admin can read "last hit: crit x2.6".

### 5.2 `GearCritSys` - Inspect group, ordered BEFORE `DamageSystems$EntityUIEvents`

Use the existing helper: `dmg_system(gcsy, "GearCritSys", "getInspectDamageGroup", "EUI", "BEFORE", "EUI", body)` (a new
`gcsy = mk("GearCritSys", PB["DES"])` - not `gcrt`, which is already `GearCraftTask`; no `GearCrit*` class exists yet) with
`GearCritSys.EUI = GearFx.cls("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$EntityUIEvents")` set in
`GearFx.setup` (line 10742), registered like `GearHitSys` (ordered first, `GearCritSysU` unordered fallback + one WARN). Body, in order
(javassist-safe; `buf` = the CommandBuffer):

1. `Integer lv = GearHit.takeCrit(d); if (lv == null || !(d.getAmount() > 0.0f)) return;` (cancelled damage never gets here, 1.1).
2. `src instanceof Damage$EntitySource` -> `att = src.getRef()`, valid; player switch on for that player (5.6); `vic = chunk.getReferenceTo(idx)`.
3. `EntityViewer v = (EntityViewer) buf.getComponent(att, EntityViewer.getComponentType()); if (v == null || !v.visible.contains(vic)) return;`
4. **Style swap (option 1):** `UIComponentList l = (UIComponentList) buf.getComponent(vic, UIComponentList.getComponentType());`
   `int ci = EntityUIComponent.getAssetMap().getIndex(CRIT_ASSET);` If `l != null && l.getComponentIds() != null && ci !=
   Integer.MIN_VALUE`: `int[] orig = java.util.Arrays.copyOf(ids, ids.length)` (the SERVER list - the swap never changes it, so it is
   always the right "original"); `swapped` = every id whose `getAsset(id)` is NOT a `CombatTextUIComponent`, then `ci` (plain loop, no
   generics); `v.queueUpdate(vic, new UIComponentsUpdate(swapped))`; register / extend the restore entry for (att, vic) (5.3).
   Vanilla's `EntityUIEvents` then queues the number for the same viewer later in the same dispatch -> the client gets
   `[UIComponents(crit), CombatText("<number>")]` in that order (1.3) -> red number.
5. **Marker (option 2):** `Float ang = (Float) d.getIfPresentMetaObject(Damage.HIT_ANGLE);`
   `v.queueUpdate(vic, new CombatTextUpdate((ang == null ? 0.0f : ang.floatValue()) - 20.0f, lv.intValue() > 1 ? "CRIT!!" : "CRIT!"));`
   (text from a config row, ASCII only, never null; the -20 degree angle nudges its drift sideways - the asset's
   `HitAngleModifierStrength` bends the Position animation by the angle and `RandomPositionOffsetRange` scatters both popups anyway.)
6. **Sparks (option 3):** position = `HIT_LOCATION` meta or the victim's `TransformComponent` position (+ about half the bounding-box
   height); `ParticleUtil.spawnParticleEffect("Impact_Critical", pos, java.util.Collections.singletonList(att), buf)` for "only me", or
   the overload without the list for everyone within 75 blocks. Optional sound via `SoundUtil.playSoundEvent3dToPlayer` /
   `playSoundEvent3d`.

If the BEFORE ordering could not be registered (fallback class), the number may already be queued before the swap: then skip the swap
and only send the marker (or send the marker right after the swap so at least "CRIT!" is red).

### 5.3 The restore (puts the vanilla style back)

Entry per (attacker ref, victim ref): `int[] orig`, `long readyMs`, `long expiryMs` (now + 5 s). A new crit on the same pair only pushes
`readyMs` out (never stores a swapped list as "original"). When due, on the world thread: both refs valid AND
`viewer.visible.contains(victim)` -> `viewer.queueUpdate(victim, new UIComponentsUpdate(orig))`; drop entries past `expiryMs` or whose
victim left view (vanilla re-sends the real list when it comes back, 1.5).
- Drain it from a tiny new per-player `EntityTickingSystem` (`GearCritTick`, every tick, only looks at that player's own entries) -
  `GearTick` runs once a second (too coarse) and `GearLockSys` has another job; or `HytaleServer.SCHEDULED_EXECUTOR` + `world.execute`
  (SkyyGear already schedules with `@HSV@.SCHEDULED_EXECUTOR`). Never call `queueUpdate` off the world thread.
- Timing: `readyMs = now + (crit asset Duration x 1000) + 20..50 ms` (MMOSkillTree: 520 ms for 0.5 s). Whether an earlier restore (even
  in the same packet) is safe is probe question 8.2.

### 5.4 `GearCritClean` - the strip (MANDATORY whenever the crit asset is in the jar)

HolderSystem, `getQuery() = UIComponentList.getComponentType()`, dependency `SystemDependency(Order.AFTER,
UIComponentSystems$Setup.class)` (unordered fallback), `onEntityAdd(Holder, AddReason, Store)`: get the list (call `update()` if its ids
are null / empty), keep every id that is not a `CombatTextUIComponent` plus vanilla `getIndex("CombatText")`, and write the result into
the protected `componentIds` with `UIComponentList.class.getDeclaredField("componentIds")` + `setAccessible(true)` + `Field.set` (cache
the Field; on any Throwable WARN once and leave the list alone). `onEntityRemoved`: nothing. Patterns already in the repo: SkyyMobs 0.1.3
`LevelHook` (HolderSystem ordered AFTER engine setup systems), SkyySkills 0.4.x reflection.
- It must run even when the crit effect is switched off in settings - otherwise every player sees two numbers on every hit (1.5 B).
- Same rule as MMOSkillTree's sanitizer, so both mods can run together (each strips the other's variants; their swaps can briefly undo
  each other - harmless).
- Known gap: an EntityUI asset reload at runtime (`LoadedAssetsEvent`) re-runs `update()` and re-adds the crit index to every list; those
  entities show double numbers to viewers who see them NEWLY afterwards until they reload. Rare (boot is fine). Optional cure: also listen
  to that event and re-strip, or re-strip in the per-viewer path.

### 5.5 The crit asset (generated into the jar by the build script, like the existing `Server/Item` / `Server/Languages` files)

`Server/Entity/UI/SkyyGear_CritText.json` (asset id = file name; SkyyGear's manifest already has `"IncludesAssetPack": true`):

```json
{
  "Type": "CombatText",
  "Parent": "CombatText",
  "Duration": 0.55,
  "FontSize": 62,
  "TextColor": "#FF4040",
  "AnimationEvents": [
    { "Type": "Scale",    "StartAt": 0,    "EndAt": 0.35, "StartScale": 1, "EndScale": 0.6 },
    { "Type": "Position", "StartAt": 0.1,  "EndAt": 1,    "PositionOffset": { "X": 0, "Y": -90 } },
    { "Type": "Opacity",  "StartAt": 0.55, "EndAt": 1,    "StartOpacity": 1, "EndOpacity": 0 }
  ]
}
```

Our own numbers. `AnimationEvents` is an array leaf (no per-element merge), so it is restated in full. Keep every value inside the
validators of 1.4 (Scale and StartAt / EndAt 0..1). `Type` + `Parent` together: INFERRED fine (MMOSkillTree omits `Type`); the server log
at boot shows any asset error. Optional: ship 2-3 colour variants (red / orange / gold) and let an admin row pick one by id (the colour
itself cannot be a live setting - assets load at boot).

### 5.6 Settings (Server Setup + player switch)

- Admin rows (tools/skyycfg.py, `crit.*` block next to `crit.base` / `crit.baseDamage`): `crit.fx.style` (on/off, option 1),
  `crit.fx.marker` (on/off) + `crit.fx.text` (default `CRIT!`) + `crit.fx.textOver` (`CRIT!!`), `crit.fx.sparks` (off / self /
  everyone), `crit.fx.sound` (off / on), optional `crit.fx.color` (asset id).
- Player switch with the existing helper (Settings-Spec 1.3; next to `gear.blockedPopup`, line 12388):
  `Gear.regSetting("gear.critFx", "Crit effects", "combat", true, "Red damage number and CRIT! on your critical hits")`.

### 5.7 Engine API used (all VERIFIED on 0.6.8)

`EntityTrackerSystems$EntityViewer.getComponentType()`, `.visible` (public `Set<Ref>`), `.queueUpdate(Ref, ComponentUpdate)`;
`UIComponentList.getComponentType()`, `.getComponentIds()`, `.update()`, protected `int[] componentIds`;
`EntityUIComponent.getAssetMap()` -> `IndexedLookupTableAssetMap.getIndex(Object)` / `.getAsset(int)` / `.getNextIndex()`;
`CombatTextUIComponent` (instanceof); `new protocol.UIComponentsUpdate(int[])`; `new protocol.CombatTextUpdate(float, String)`;
`Damage.HIT_ANGLE` (`MetaKey<Float>`), `Damage.HIT_LOCATION` (`MetaKey<Vector4d>`), `Damage.getIfPresentMetaObject(MetaKey)`;
`DamageModule.get().getInspectDamageGroup()`; `SystemDependency(Order, Class)`; `UIComponentSystems$Setup`;
`DamageSystems$EntityUIEvents`; `HolderSystem.onEntityAdd(Holder, AddReason, Store)` / `onEntityRemoved(Holder, RemoveReason, Store)`;
`ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor)` and `(String, Vector3dc, ComponentAccessor)`;
`SoundUtil.playSoundEvent3d(int, SoundCategory, Vector3d, ComponentAccessor)`, `playSoundEvent3dToPlayer(Ref, int, SoundCategory,
Vector3d, ComponentAccessor)`.

---------------------------------------------------------------------------------------------------------------------------------------

## 6. Per player vs everyone

- **Numbers:** vanilla sends each number only to the player who dealt it (1.2). The crit swap and the marker are queued to that player's
  `EntityViewer` only, so only they see red. Party members never see your numbers at all (vanilla). Works the same on mobs and, in PvP,
  on the player you hit (that player only gets their own `DamageInfo` indicator).
- **Sparks / sound:** your choice - the list overload (attacker only) or the broadcast overload (everyone within 75 blocks, like vanilla's
  backstab sparks).
- **Opt-outs:** the player switch `gear.critFx`; the client's own "display combat text" setting hides every number (the swap is then
  harmless); a world's `CombatConfig.DisplayCombatText` can turn numbers off for everyone.

---------------------------------------------------------------------------------------------------------------------------------------

## 7. Risks (and how to avoid each)

1. **Client parse / disconnect risk:** never send a null `text` or a null `int[]` (both non-nullable in the protocol); only send component
   indices of assets the server really loaded (`getIndex != Integer.MIN_VALUE`); keep the asset inside its validators or it does not load
   (then the code must fall back to marker-only). Never invent client-only indices (option 6).
2. **`IllegalArgumentException("Entity is not visible!")`** from `queueUpdate` - check `viewer.visible.contains(target)` at swap AND at
   restore time.
3. **Double numbers for everyone** if the crit asset ships without `GearCritClean` (1.5 B), or after a runtime EntityUI asset reload (5.4).
4. **The red window:** for ~0.5 s after a crit, any other number on that mob for that player is red too (fast weapons, DoTs). Shorter
   Duration = shorter window. Restoring early may cut the crit popup short (UNVERIFIED, 8.2).
5. **In-flight popups:** the swap may make a still-floating white number from a hit just before vanish or restyle; the health bar might
   blink when its component is re-sent (both UNVERIFIED).
6. **Ordering:** the swap must be queued BEFORE vanilla's number (`SystemDependency BEFORE DamageSystems$EntityUIEvents`); a future server
   that renames that class drops SkyyGear to the unordered fallback (marker only).
7. **Threading:** every `queueUpdate` on the world thread (damage systems are; restores via a ticking system or `world.execute`).
8. **Do not use `damage.setAmount(0)` to hide vanilla's number** (StunningCombat's trick): SkyyGear's `GearLeechSys` and vanilla
   `PlayerHitIndicators` read the amount in Inspect.
9. **Text:** ASCII / Latin-1 only (no ★ ✦ ⚔), no markup.
10. **Other mods:** MMOSkillTree (or anything that adds CombatText variants) strips SkyyGear's variant and vice versa - by design; swaps
    may briefly undo each other.
11. **Cost:** one extra `UIComponentsUpdate` (a few bytes) + one restore + one marker per crit; negligible.

---------------------------------------------------------------------------------------------------------------------------------------

## 8. UNVERIFIED items and the probe that settles them

8.1 The client draws the number with the style that is active when the number arrives, and one popup per CombatText component
    (MMOSkillTree's design and comment say yes; we cannot read the NativeAOT client logic).
8.2 What a `UIComponentsUpdate` does to popups that are still floating: if they survive, the restore can go in the SAME packet right after
    vanilla's number (a second Inspect system AFTER `EntityUIEvents`) = zero red window; if they vanish, keep the ~Duration+50 ms delay.
    MMOSkillTree's 520 ms delay hints at "they vanish" (INFERRED).
8.3 Health bar blink on swap; `"Type"` + `"Parent"` together in the asset; markup shows literally.

Probe build (admin-only `/gear critprobe [same|delay]`, forces every hit of the admin to count as a crit for 10 minutes; trial switch off
by default, per the UI rules):
1. Join the "HUD mod" world, hold any gear weapon, run `/gear critprobe delay`.
2. Hit a mob several times slowly: each number is red and bigger, with "CRIT!" beside it, and there is only ONE number per hit (no white +
   red pair) - confirms 8.1 and the strip.
3. Turn the probe off and hit again: numbers are white 48 px again within half a second.
4. A second player (or an alt) watches you hit the same mob: they see no numbers from your hits (vanilla), only sparks if set to everyone.
5. Run `/gear critprobe same` and hit a mob: if the red crit number still shows fully, the same-packet restore (8.2) is safe - report it.
6. Hit fast with daggers in `delay` mode: note whether numbers right after a crit are also red (the window) and whether the health bar
   blinks (8.3).
7. Walk away until the mob unloads from view, come back, hit it: one white number per normal hit.
8. Client setting "display combat text" off: no numbers, no errors, no disconnect.
9. Check the server log at boot for an asset error on `SkyyGear_CritText` and for the GearCritSys / GearCritClean ordering WARNs.

---------------------------------------------------------------------------------------------------------------------------------------

## 9. Recommendation for Skyy

Make crits show as a **red, bigger number with a "CRIT!" tag and vanilla's own crit spark burst** - the same look Hytale uses for dagger
backstabs and bow headshots, plus the colour you asked for. Bold is already on for every number (the game's client sets it and no server
can change it), so "bigger and red" is the strongest the game allows. The safe parts ("CRIT!" popup and sparks) can ship right away; the
red number needs SkyyGear to add one extra style file, quietly remove that style from every mob so normal hits never show twice, and flip
it on for just the attacker for half a second on a crit - exactly what the MMOSkillTree mod on your PC already does on this game
version. Only the attacker sees the red number (that is how Hytale numbers work), sparks can be "just me" or "everyone nearby", and both
an admin row and a player switch can turn it off. Suggested order: a small probe build first (section 8, about 5 minutes of testing),
then the real feature in the next SkyyGear version as a lean round (one mod, no saved-data change).
