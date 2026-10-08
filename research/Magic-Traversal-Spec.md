# Magic traversals: SkyyArmory 0.1.1 + SkyyClasses 0.1.12 (+ SkyyGear tooltip words) - build spec

> **2026-10-07 Skyy: NO VOID PROTECTION on any traversal** ("dont put any void protection on any traversal."). The void rules below
> (blink floorCheck, the void hop halving) are being REMOVED in SkyyArmory 0.1.7; falling into the void is a race to get back out.

Date 2026-10-05. Locks: docs/answered/classes.md lines 30-33 + 37 (LOCKED 2026-10-04), research/classes/Mage.md + research/classes/Priest.md.
Current code: SkyyArmory 0.1 (`SkyyArmory/build_skyyarmory_0.1.py`, spec `research/SkyyArmory-Spec.md`, S:), SkyyClasses 0.1.11
(`SkyyClasses/build_skyyclasses_0.1.11.py`, C:), SkyyGear 0.2.3 (`SkyyGear/build_skyygear_0.2.3.py`, G:).
Marks: **VERIFIED** = read in HytaleServer.jar bytecode / reflection, Assets.zip, or our own build scripts (class + method or asset path
given). **INFERRED** = follows from verified facts, not seen running. **UNVERIFIED** = needs the game (listed in section 5 / 6).
Engine checks ran read-only with tools/dev reflect.py / bc.py / cpgrep.py; scratch tools/dev/scratch/travspec/ deleted.

## 0. Plain words (for Skyy)

- **Staff, hold = BLINK.** You vanish and reappear 10 blocks the way you look (up too). Behind you a line of light hangs for 3 s and
  burns every enemy standing in it (30% of the charged shot's damage per second). You never land inside a block, never over open void
  (the blink shortens to the last safe spot), never in another world. If you were already falling hard, you keep falling (no
  fall-damage escape). Costs the staff's Mana only - **no Stamina, no Stamina pause any more**.
- **Wand, hold = HOP BACK + BURST.** You hop away from where you look (look down = straight up) and the orb flies; where it ends it
  bursts (6 blocks: the enemy you hit takes the full shot, the others around take 60%), and a glowing heal orb (9 blocks) stays for
  3.5 s: you and your party members inside heal 20% of the burst's damage every second. The hop shrinks when there is no ground behind
  you. Your old heal-share on damage stays as it is.
- **Quick shots.** Wand taps pierce (through up to 3 enemies, 16 blocks, stop at blocks). Staff taps do not pierce, fly 24 blocks and hit
  15% harder per Mana than a wand tap.
- **Everything with a number is a Server Setup -> Armory row** (table in 1.4); the few values that must be fixed in the jar say so.
- Players: your blasts hurt other players only where the world's PvP is on, and never your party. Teleport distance upgrades and the
  "set my own distance" option come with the class trees (the Mage tree's Riftwalker lane); 0.1.1 ships the server-wide 10.

## 1. Behaviour per weapon (numbers)

### 1.1 Staff (Mage; the 8 ladder staffs `Weapon_Staff_Wood .. _Onyxium`, S:15.2)
| Step | What happens | Default |
|---|---|---|
| Hold >= 1.0 s | Mana check (the staff's C: 10 / 20 / 30 / 50 / 80 / 120 / 170 / 170); too little = no-ammo click, nothing spent | as 0.1 |
| Cast | Mana -C. **Stamina -5 and the 1.5 s regen pause are gone.** Animation CastSummonCharged, sound SFX_Staff_Ice_Shoot | fixed |
| Blink | From your feet, straight along the look direction (yaw + pitch): the farthest free spot <= `blink.distance`, stepped 0.5 blocks; a spot is free when the two blocks of your body are passable and (if `blink.floorCheck` > 0) a block exists within that many blocks below. The first blocked / unloaded / out-of-range step ends the scan 0.3 blocks short. Nothing free beyond 1 block = no blink (Mana still spent, trail still drawn where you stand - 7.3) | 10 blocks, floor 12 |
| Fall | Your falling speed is kept (`blink.keepFall` on) - landing speed decides fall damage, so a blink never erases a damaging fall; blinking upward while falling slowly is fine | on |
| Trail | A capsule from where you were to where you landed, radius `blink.trailWidth` / 2, for `blink.trailSeconds`; every `blink.tickMs` each hostile inside takes `blink.trailPercent` % x the staff's charged damage x (tickMs / 1000); the same enemy is hit at most once per tick; light particles along the line | 1.5 wide, 3 s, 30%/s, 500 ms |
| Tap | Quick shot: 1/5 Mana, no pierce, dies at `quick.range.staff` blocks or on any hit; damage = the 0.1 quick damage x (1 + `quick.staffBonus` %) | 24 blocks, +15% |

Example (Iron staff, no levels): charged 88 -> trail 26 per second per enemy, 79 for the full 3 s; Mana 30; blink 10 blocks.

### 1.2 Wand (Priest; the 7 metal wands + the Wood wand's hold stays SkyySkills' vanilla orb, S:2.4)
| Step | What happens | Default |
|---|---|---|
| Hold >= 0.35 s | Mana check C: 10 / 15 / 25 / 40 / 60 / 85 / 85 (Wood 5 via SkyySkills) | as 0.1 |
| Cast | Mana -C, the charged orb `SkyyArmory_Orb_<M>` flies (30 blocks/s, as 0.1) | as 0.1 |
| Hop | At the moment the orb spawns you are pushed OPPOSITE to your look direction with `hop.force` (Set velocity; dagger-dash feel). Look down = straight up. If no block lies within `hop.groundCheck` blocks under the spot ~3 blocks behind you, the force halves | 13, check 6 |
| Burst | Where the orb ends (enemy or block): every hostile within `aoe.radius` except the enemy it hit takes `aoe.percent` % of the orb's damage (the hit enemy keeps the full vanilla hit). No block damage, no knockback (`aoe.knockback` off) | 6 blocks, 60% |
| Heal orb | A glowing sphere of `orb.radius` lives `orb.seconds` at the burst point; every `orb.tickMs` the Priest and each party member inside heal `orb.healPercent` % of the burst's damage (the orb's real direct-hit damage; on a block hit the asset damage x tune); goes through SkyyClasses' heal entry (caps, Divinity XP, chat feedback) | 9 blocks, 3.5 s, 20%/s, 1000 ms |
| Life-steal | SkyyClasses 0.1.11's heal share on landed Priest damage is unchanged; the burst's extra hits feed it too under the existing per-second budget | as 0.1.11 |
| Tap | Quick shot pierces: after each enemy hit the shot continues from the far side of that enemy (up to `pierce.max` enemies), stops at blocks or at `quick.range.wand` | 3, 16 blocks |

Example (Iron wand, no levels): orb 88 -> others 53 each; heal orb 17.6 per second to each ally inside (3 ticks = 53), Classes caps apply.

### 1.3 Shared rules
- Hostile = any `NPCEntity` with an `EntityStatMap` that is not the caster; players count only when the world's PvP flag is on AND
  `trav.players` is on AND they are not in the caster's party (party:fn:members). The engine itself also cancels player-on-player
  damage with PvP off (2.7). Creative-mode casters get no XP (SkyySkills rule) but everything else works.
- Allies = the caster + party members (`orb.allies` = party); `all` = every non-hostile player in range.
- Caster dead / logged out / in another world: trails and orbs finish on their own clock; damage ticks stop (no credit without a
  shooter), heals continue without XP. Max `trav.maxLive` (64) live trails + orbs per world; the oldest is dropped.
- No new cooldowns: the hold time + Mana are the limiter (`blink.cooldown` exists, default 0 - 7.5).

### 1.4 Server Setup rows (SkyWynn Menu > Server Setup > Armory; kit 12-tuples, categories `trav`, `blink`, `hop`, `burst`, `quick`)
| Key | Label (<= 40) | Type | Default | Range | Flags | Help (<= 100) |
|---|---|---|---|---|---|---|
| part.trav | Magic traversals | bool | true | | live,part,danger | Off = staff holds fire the old orb, wands only shoot; no blink / hop / burst / heal orb / pierce. |
| staff.mode | Staff hold | opt blink,orb | blink | | live | blink = teleport + light trail; orb = the 0.1 charged orb. |
| blink.distance | Blink distance (blocks) | int | 10 | 3-20 | live | Server-wide until the class trees add upgrades and the own setting. |
| blink.floorCheck | Blink needs ground within (blocks) | int | 12 | 0-64 | live | 0 = off. Shortens a blink over open void to the last spot with ground below. |
| blink.keepFall | Blink keeps falling speed | bool | true | | live | On = no fall-damage escape. Off = the teleport stops your fall. |
| blink.trailOn | Light trail | bool | true | | live | Off = blink only. |
| blink.trailWidth | Trail width (blocks) | dec | 1.5 | 0.5-4 | live | |
| blink.trailSeconds | Trail lasts (s) | dec | 3 | 0.5-8 | live | |
| blink.trailPercent | Trail damage (% of charged per second) | int | 30 | 0-200 | live | Per enemy standing in it. |
| blink.tickMs | Trail tick (ms) | int | 500 | 250-1000 | live | Damage every this often. |
| blink.cooldown | Blink cooldown (s) | dec | 0 | 0-10 | live | 0 = none. A blink inside the cooldown still fires the trail; Mana is spent. |
| hop.force | Wand hop force | dec | 13 | 0-25 | live | 0 = no hop. 13 = the vanilla dagger dash. |
| hop.groundCheck | Hop needs ground within (blocks) | int | 6 | 0-32 | live | 0 = off. No ground behind you = half the hop. |
| burst.radius | Burst radius (blocks) | dec | 6 | 1-12 | live | |
| burst.percent | Burst damage to others (%) | int | 60 | 0-100 | live | % of the orb's damage; the enemy hit directly takes the full shot. |
| burst.knockback | Burst knockback | bool | false | | live | Pushes enemies away from the burst (small). |
| orb.radius | Heal orb radius (blocks) | dec | 9 | 1-16 | live | |
| orb.seconds | Heal orb lasts (s) | dec | 3.5 | 0.5-8 | live | |
| orb.healPercent | Heal orb (% of burst damage per second) | int | 20 | 0-100 | live | Each ally inside, every second. |
| orb.tickMs | Heal orb tick (ms) | int | 1000 | 250-2000 | live | |
| orb.allies | Heal orb heals | opt party,all | party | | live | party = the Priest + party members; all = every player who is not an enemy. |
| trav.players | Hit players (world PvP on) | bool | true | | live | Trail and burst hit other players only where PvP is on; never party members. |
| trav.maxLive | Most live trails + orbs per world | int | 64 | 8-256 | live | Oldest dropped first. |
| trav.fx | Traversal particles and sounds | bool | true | | live | |
| pierce.max | Wand quick shot pierces (enemies) | int | 3 | 1-10 | live | |
| quick.range.wand | Wand quick shot range (blocks) | int | 16 | 4-64 | live | Replaces 0.1's reach-in-seconds row (kept hidden, 3.1). |
| quick.range.staff | Staff quick shot range (blocks) | int | 24 | 4-64 | live | |
| quick.staffBonus | Staff quick shot bonus (%) | int | 15 | 0-100 | live | Staff taps hit this much harder per Mana than wand taps. |
| staff.stamina | Staff cast Stamina (fixed in the jar) | ro | 0 | | ro | Was 5 + a 1.5 s regen pause. Build constant STAFF_STAMINA. |
| hop.mode | Hop mode (fixed in the jar) | ro | server | | ro | server = the Java push (live force, ground check); asset = the client dash (3.1). |

## 2. Engine approach per feature (evidence)

### 2.1 The hook that starts everything: the charged launch (VERIFIED)
SkyyArmory 0.1's `ArmorySpawnSys` is a `HolderSystem` on `ProjectileComponent` acting on `AddReason.SPAWN` for its own projectile ids
(S:2.3; build line 1884 `onEntityAdd`). `ProjectileComponent` exposes `getProjectileAssetName()`, `getCreatorUuid()` and
`getSimplePhysicsProvider()` (reflect); `ProjectileComponent#shoot` sets the velocity to the aim direction x MuzzleVelocity before
`addEntity` (S:2.3, VERIFIED) - so at spawn the orb's velocity IS the caster's look direction, pitch included, and the creator UUID
resolves to the caster (`EntityStore.getRefFromUUID`, the ShotTrack pattern, C:171). 0.1.1 adds a sibling **`ArmoryTravSys`**
(RefSystem, Query Transform + ProjectileComponent, the ShotTrack shape C:170-172) with `onEntityAdded(SPAWN)` and `onEntityRemove`;
one `registerSystem` per class (brief rule).

### 2.2 Staff blink
- **Marker projectile (PROPOSED).** `SkyyArmory_Staff_Cast_<M>` keeps its shape but launches `SkyyArmory_Blink_<M>` instead of the orb:
  a fully resolved legacy Projectile (Damage 0, MuzzleVelocity 30, Gravity 0, TimeToLive irrelevant - S:2.3) whose model asset
  `SkyyArmory_Marker` is the orb model copy with no DefaultAttachment, no Particles, no Trails (the base texture
  `Projectile_default.png` is 100% transparent, S:2.3) -> invisible. `ArmoryTravSys.onEntityAdded` reads the marker's velocity (=
  direction), zeroes it (`SimplePhysicsProvider.getVelocity()` is the live vector, S:2.3), does the blink, and keeps the marker as the
  **trail entity** for `blink.trailSeconds`, then `buf.removeEntity(ref, REMOVE)`. With `staff.mode = orb` or `part.trav` off the system
  instead spawns `SkyyArmory_StaffOrb_<M>` with the marker's velocity (`ProjectileComponent.assembleDefaultProjectile(TimeResource,
  String, Vector3d, Rotation3f)` static + `CommandBuffer.addEntity`, the `LaunchProjectileInteraction#firstRun` path S:2.3) and removes
  the marker. INFERRED: a projectile at rest never raises hit events (`SimplePhysicsProvider#tick` sweeps the movement vector, S:2.3;
  zero move = no sweep); the 60 s DespawnComponent is far beyond 3 s.
- **Why the marker stays alive:** the trail's damage is `new Damage(new Damage$ProjectileSource(casterRef, markerRef),
  DamageCause.PROJECTILE, amount)` -> `DamageSystems.executeDamage(targetRef, buf, dmg)` (both VERIFIED: `Damage(Source, DamageCause,
  float)`, `Damage$ProjectileSource(Ref, Ref)`, `DamageSystems.executeDamage(Ref, CommandBuffer, Damage)`). That is exactly the shape of
  a vanilla orb hit (`ProjectileComponent#onProjectileHitEvent`, S:2.3), so SkyyGear's spell level scaling (ProjectileSource by the
  launch record, G:136), ArmoryTuneSys' tune (our id) and SkyyClasses' class lock (launch record, C:176-177) all treat trail ticks like
  orb hits. INFERRED: the launch record is keyed by the projectile and lives until `onEntityRemove` (C:172), so it is valid for 3 s.
- **Scan (VERIFIED pieces, INFERRED whole).** Block read = SkyySkills 0.4.15's `blockIdAt` (`World.getChunkStore()` ->
  `ChunkStore.getChunkSectionReferenceAtBlock(x,y,z)` -> `BlockSection.get(x,y,z)` -> `BlockType.getAssetMap().getAsset(id)`; never
  loads a chunk; build 5296-5312) - the same read `ExplodeInteraction#firstRun` uses (bytecode offsets 180-246). Passable test:
  `BlockType.EMPTY` or `!BlockType.blocksLineOfSight(id)` (static, VERIFIED exists; which non-solid materials pass = INFERRED, probe T4) -
  a glass wall or fence blocks the blink like it blocks walking. Body = the blocks at feet y and y+1 for the stepped point (0.5-block
  steps along the unit direction, D <= `blink.distance`). Invalid section ref (unloaded chunk) = stop. Alternative for the direction:
  `TargetUtil.getLook(Ref, ComponentAccessor)` / `getTargetBlock(Ref, double, ComponentAccessor)` (VERIFIED static) - the build may use
  `getTargetBlock` as the first-wall raycast and the step scan only for the floor and body checks (constant SCAN_MODE).
- **Teleport (VERIFIED).** `Teleport.createForPlayer(Vector3dc, Rotation3fc)` (static) put on the player
  (`buf.putComponent(ref, Teleport.getComponentType(), t)`); `TeleportSystems$PlayerMoveSystem#onComponentAdded` compares
  `Teleport.getWorld()` with the store's world and calls `teleportToPosition` (same world) or `teleportToWorld` - we only ever build the
  same-world form (no World argument = INFERRED null world = same world; the island-visit and warp commands are the other users).
  `teleportToPosition` sets `TransformComponent.teleportPosition / teleportRotation`, writes a `TeleportRecord`, validates windows, and
  sends `ClientTeleport` through `TeleportSystems.queueAndSendClientTeleport(PlayerRef, Vector3d, Rotation3f, Rotation3f,
  boolean resetVelocity)` with `Teleport.isResetVelocity()`; `Teleport.withoutVelocityReset()` exists (reflect) -> `blink.keepFall` on =
  `createForPlayer(...).withoutVelocityReset()`. The client acks (`TeleportAckTracker`); `KnockbackPredictionSystems$ClearOnTeleport`
  clears pending knockback. Rotation: the player's current `HeadRotation.getRotation()` / `TransformComponent.getRotation()` (VERIFIED
  getters) so the view does not snap.
- **Fall damage (VERIFIED formula, research/Double-Jump-Spec.md 1.4):** `DamageSystems$FallDamagePlayers#tick` compares the last
  |clientVelocity.y| at landing with `MovementConfig.getMinFallSpeedToEngageRoll()` (21). A blink that keeps velocity changes nothing;
  a blink 10 blocks up then falling reaches ~25 b/s only from 10 blocks of free fall (v = sqrt(2 x 32 x h)) - normal game fall rules.
- **FX (VERIFIED assets + API):** entity effect `Portal_Teleport` (`Server/Entity/Effects/Portals/Portal_Teleport.json`: ModelVFX +
  `Portal_Going_Through_Blue` particles, 0.5 s) via `EffectControllerComponent.addEffect(Ref, EntityEffect, ComponentAccessor)`;
  sound `SFX_Portal_Neutral_Teleport_Local` via `SoundUtil.playSoundEvent3d` (Double-Jump-Spec 1.4). Trail particles:
  `ParticleUtil.spawnParticleEffect(String, Vector3dc, ComponentAccessor)` (VERIFIED, 20 overloads) at 1-block steps every tick with
  `SkyyArmory_Trail_Light` = a build-time recolour (#ffe9a0) of 0.1's `SkyyArmory_Orb_Glow_Blue` copy chain (S:2.3). Visible to every
  viewer = INFERRED (the viewer-list overload exists).

### 2.3 Wand hop
- **Server hop (PROPOSED default, VERIFIED path):** in `ArmoryTravSys.onEntityAdded` for `SkyyArmory_Orb_<M>`: direction = -(orb
  velocity normalised); push = `Velocity.addInstruction(new Vector3d(dir x force), VelocityConfig, ChangeVelocityType.Set)` on the
  caster - `PlayerVelocityInstructionSystem#tick` turns every instruction into a `ChangeVelocity` packet (Set / Add, bytecode 138-197) -
  the exact path SkyySkills' double jump and `Acro.boost` use in production (Double-Jump-Spec 1.4, 3.4). VelocityConfig = the dagger
  dash's (`Daggers_Dash_Backward.json`: AirResistance 0.97 / 0.96, Ground 0.94 / 0.82, Threshold 5, Exp). Ground check: `blockIdAt`
  down from (feet + dir_horizontal x 3) for `hop.groundCheck` blocks; nothing = force / 2. Latency ~1 tick + ping, like the double
  jump (known, accepted there).
- **Asset hop (fallback, constant HOP_MODE = "asset", VERIFIED by vanilla use):** a 4th Parallel element in `SkyyArmory_Wand_Cast_<M>`:
  `{"Type":"ApplyForce","Force":13,"Direction":{"X":0,"Y":0,"Z":5},"AdjustVertical":true,"ChangeVelocityType":"Set","VelocityConfig":
  {...dagger dash...}}` - `Weapon_Sword_Primary_Thrust_Force.json` (Z -10 = forward, AdjustVertical, VerticalClamp [-85, 20]) and
  `Daggers_Dash_Backward.json` (Z +5 = backward, Force 13, Set) prove the fields; `ApplyForceInteraction` is `config/client` (the client
  applies it, the server only tracks `ApplyForceState`, bytecode) -> instant, client-predicted, but the force is build-time and the
  server cannot shrink it for the void (INFERRED: AdjustVertical rotates the whole vector by pitch, so looking down pushes up-back).

### 2.4 Wand burst
- **Direct hit:** vanilla (`onProjectileHitEvent`, Damage PROJECTILE, S:2.3). A new Inspect-group `DamageEventSys` (the PriestHealSys
  pattern, C:4667 "after the damage landed") sees a landed Damage whose source is a `ProjectileSource` of one of our 7 orb ids: it
  reads the amount after every modifier (G:9851 notes the same read), the target ref, the position (`Damage.HIT_LOCATION` MetaKey,
  VERIFIED field; fallback the target's Transform) and runs the burst at once (orb still alive -> ProjectileSource valid, launch
  record intact): `TargetUtil.getAllEntitiesInSphere(Vector3d, double, ComponentAccessor)` (VERIFIED static; it is what
  `DeployableAoeConfig#handleDetection` uses, bytecode 58) -> filter hostiles (1.3), skip the direct target ->
  `executeDamage(other, buf, new Damage(new ProjectileSource(caster, orb), PROJECTILE, amount x burst.percent))`.
- **Miss (block hit):** `ArmoryTravSys.onEntityRemove` for an orb that dealt no direct hit (a per-orb flag set by the hit system):
  position = the orb's `TransformComponent.getPosition()` at removal (`LegacyProjectileSystems$TickingSystem#tick` reads the Transform,
  calls `onProjectileDeath(ref, pos, ...)`, then `removeEntity` - bytecode 135-150 - so the position is current at removal; INFERRED
  that components are still readable inside onEntityRemove, as ShotTrack's own onEntityRemove relies on). Amount = the asset damage x
  ArmoryTuneSys' tune (no level factor available: INFERRED acceptable; the orb is the same for the heal orb). System order against
  `GearShotTrack.onEntityRemove` is unknown -> the miss burst uses `Damage$EntitySource(caster)` if the record is gone (G:9834: a plain
  EntitySource projectile hit is scaled by the shooter's live record "pick") - UNVERIFIED in game, test T6.
- **Not the engine's Explode:** `ExplosionUtils#processTargetEntity` builds `new Damage(source, DamageCause.ENVIRONMENT, amount)` and
  attaches `KnockbackComponent` AFTER the damage event without checking cancellation (bytecode 148-317; C:190 "a blocked bomb still
  pushes"). ENVIRONMENT would bypass armour / class / Gear spell rules -> we do the AoE ourselves. `burst.knockback` on = we put a
  `KnockbackComponent` (`setVelocity / setVelocityConfig / setVelocityType / setDuration`, reflect) with a Point vector away from the
  centre, force 5 (the `Explode_Generic` values) - INFERRED that `KnockbackSystems$ApplyKnockback` consumes it like the explosion's.
- **FX:** particles `Explosion_Small` + sound `SFX_Staff_Flame_Fireball_Impact` (both VERIFIED in
  `Weapon_Stick_Fire_Impact_Base.json`), scaled by burst.radius / 2.

### 2.5 Heal orb
- A world-thread list (`TravTick`, an `EntityTickingSystem` on `Player` with `isParallel` false, the AcroSys / HealTask pattern; it runs
  the per-world list once per tick behind a tick-stamp guard) holds `{world, centre, radius, until, hpPerTick, casterUuid}`. Each
  tick due: `getAllEntitiesInSphere` -> players only -> allies (1.3) -> `class:fn:heal` (new, 3.2) with
  `Object[]{casterUuid, targetUuid, Double hp, "armory:orb"}`; SkyyClasses applies room / per-second budget / Divinity XP / feedback
  with its existing `HealTask.heal` (C:3531-3546: `EntityStatMap.get(Health)`, `addStatValue`, VERIFIED path). SkyyClasses absent ->
  `addStatValue` directly, no XP.
- Why not a vanilla AoE deployable: `DeployableAoeConfig` + `ApplyEffects` (`Projectile_Config_Healing_Totem_Deploy.json`: Type Aoe,
  Cylinder, LiveDuration, ApplyEffects [`Healing_Totem_Heal` = Health +5 per 1 s]) is VERIFIED to exist and
  `DeployablesUtils.spawnDeployable(CommandBuffer, Store, DeployableConfig, Ref, Vector3d, Rotation3f, String)` is public, but an
  `EntityEffect`'s `StatModifiers` are asset constants - a heal of "20% of this burst" needs code anyway, and "team" there means the
  engine's team, not our party. Kept as the fallback look (constant ORB_LOOK = "particles" | "totem").
- **FX:** `Totem_Heal_Simple_Test` (VERIFIED `Server/Particles/Deployables/Healing_Totem/`) at the centre every tick + a ring of
  `SkyyArmory_Orb_Glow_Blue` points at the radius every 0.5 s (8 points); sound `SFX_Deployable_Totem_Heal_Spawn` once.

### 2.6 Quick shots: pierce and range
- **Range (VERIFIED mechanism):** `ArmoryTravSys` records each quick orb's spawn position; `TravTick` checks our live quick orbs every
  tick and `buf.removeEntity(ref, REMOVE)` when |pos - start| > range (per family). 0.1's `quick.life` DespawnComponent swap stays as
  the hard ceiling (hidden row, default = 0.1's). Legacy projectiles otherwise fly until a hit or 60 s (S:2.3).
- **Pierce (INFERRED, probe T7):** the hit system (2.4) sees a landed quick-orb hit on target E with hits-so-far < `pierce.max`:
  it spawns a continuation `SkyyArmory_QuickOrb_<M>` via `assembleDefaultProjectile` + `addEntity` at E's position + dir x (E's
  bounding-box half-extent + 0.5) with the dying orb's velocity (read before the dead timer runs: `getSimplePhysicsProvider()
  .getVelocity()`), creator = the caster (so GearShotTrack / ShotTrack make a launch record from the wand still in hand), and carries
  the hit count + the original start position (range continues from the first launch). The direct hit stays vanilla; ArmoryTuneSys and
  Gear scale the next hits the same. UNVERIFIED: `assembleDefaultProjectile`'s Holder needs the creator UUID set the way
  `LaunchProjectileInteraction` does (bytecode T2 in the harness: list its `putComponent` calls and mirror them).

### 2.7 PvP, allies, Stamina (VERIFIED)
- `DamageSystems$PlayerDamageFilterSystem#handle`: with `WorldConfig.isPvpEnabled()` false and an `EntitySource` whose ref is a
  `Player`, the Damage on a player is cancelled (bytecode 61-123); `ProjectileSource extends EntitySource` (reflect) -> all our hits
  obey the world flag on top of our own `trav.players` / party rule. `/worldconfig` `WorldConfigSetPvpCommand` toggles it.
- Allies: `party:fn:members` (SkyyParty bridge, used by C:3511-3522). SkyyIslands has no border walls (its protection is event-based:
  island build line 106; grep border / barrier / wall = none) - a blink obeys blocks exactly like walking; cross-world is impossible
  by construction (2.2).
- Stamina: `Server/Entity/Stats/Stamina.json` Max 10 (VERIFIED); 0.1 adds `SkyyArmory_Staff_Stamina` (ChangeStat Stamina -5) and
  `_Stamina_Delay` (StaminaRegenDelay Set -1.5) into every `SkyyArmory_Staff_Cast_<M>` Parallel (build 593-594, 37). 0.1.1 drops both
  elements and both interaction files (build-time: ChangeStat is client-predicted, S:7). The 1.0 s Charging key, the Mana check and the
  cast timing are unchanged.

## 3. Code changes

### 3.1 SkyyArmory 0.1.1 (`tools/armory_0_1_1_patch.py` reads `SkyyArmory/build_skyyarmory_0.1.py`, writes `build_skyyarmory_0.1.1.py`; 0.1 has no patch history, so this is the first patch - `rep` anchors asserted)
1. Constants: `STAFF_STAMINA = 0` (drop the two Stamina elements + files when 0), `HOP_MODE = "server"`, `SCAN_MODE = "step"`,
   `ORB_LOOK = "particles"`, `TRAIL_COLOR = "#ffe9a0"`.
2. Assets: 8 `SkyyArmory_Blink_<M>` projectiles + model asset `SkyyArmory_Marker` (2.2); `SkyyArmory_Trail_Light` particle copies; the
   staff charged Launch steps name the Blink id; the 8 StaffOrb projectiles stay (orb mode + fallback). Wand chains unchanged
   (asset hop only when HOP_MODE = "asset").
3. Java: `ArmoryTravSys` (RefSystem: SPAWN -> blink / hop / quick start positions; onEntityRemove -> miss burst, record cleanup),
   `ArmoryHitSys` (Inspect-group DamageEventSys: burst on direct hit, pierce continuation, direct-hit flag), `TravTick`
   (EntityTickingSystem on Player: trails, heal orbs, quick ranges, per-world lists, maxLive), pure helpers `TravMath` (`scan`,
   `segDist`, `hopVector`, `tickDamage`, `healPerTick` - static, no engine types, for the bare-JVM harness). Registration = the 0.1 try /
   fallback pattern (build 2241-2249), one registerSystem per class; `part.trav` off = the three systems idle.
4. Config: the rows of 1.4 (kit `emit(..., KEEP=10)` - 0.1's KEEP stays as it is if already 10; change 20 -> 10); `quick.life` keeps its
   key, flag `hidden` (kit allows? else label "(ceiling)"); migration none (missing keys read defaults).
5. Bridge: `armory:fn:info` answers 2 more elements: `[8] String travWords` ("Blink 10 blocks + light trail" / "Hop back + burst, heal
   orb"), `[9] String quickWords` ("pierces, 16 blocks" / "24 blocks"); `armory:trav` -> String of the live traversal numbers for
   SkyyMenu help; reads `class:fn:heal`, `class:fn:ally` (3.2), `party:fn:members` (fallback when SkyyClasses is absent).
6. Log: one INFO line at start with the traversal defaults; WARN once per failing Java part (the 0.1 wording).

### 3.2 SkyyClasses 0.1.12 (`tools/classes_0_1_12_patch.py` on the generated 0.1.11)
1. New bridge `class:fn:heal` -> `Function(Object[]{UUID healer, UUID target, Double hp, String why})` -> Double healed: room clamp,
   `HealBudget.take` with hitCap = the healer's wand charged cap (0.1.11 `capOf`), `addStatValue`, Divinity XP via `skill:fn:healxp`
   (self -> the self rate, as 0.1.7), the 0.1.6 chat feedback throttle; refuses (0.0) when the healer is not a Priest or `priestHeal.
   enabled` is off. New bridge `class:fn:ally` -> `Function(Object[]{UUID a, UUID b})` -> Boolean (same party; later guilds).
2. Card text: Mage "Hold to blink the way you look and leave a trail of light.", Priest "Hold to hop back and burst - the glow heals your
   party." (UI text rule: no , : ; { } " ' _).
3. Nothing else: PriestHealSys, caps, kits, commands, rows unchanged (the patch asserts it).

### 3.3 SkyyGear 0.2.4 tooltip words (small; `tools/gear_0_2_4_patch.py`)
The wand / staff tooltip (G:62, 7621) adds one line after "Charged shot - N Mana - damage": `armory:fn:info[8]`, and appends
`armory:fn:info[9]` to the "Quick shot" line when the array has >= 10 elements (older SkyyArmory = no change). armorySig already
hashes the answers (G:5303) so the line refreshes when Skyy changes rows.

### 3.4 Deploy order and pins
SkyyClasses 0.1.12 -> SkyyArmory 0.1.1 -> SkyyGear 0.2.4 (each works alone: Armory without Classes heals directly without XP; Gear
without the new Armory prints the old lines). Rollback floors unchanged. SkyyMenu MODS_VERSIONS + help text follow in its own round.

## 4. Safety and exploit table
| Risk | Rule | Evidence |
|---|---|---|
| Blink into a block | body blocks (feet, head) must be passable at the landing step; stop 0.3 short of the first blocked step | 2.2 scan; `blocksLineOfSight` INFERRED as the passable test (T4) |
| Blink out of the world / over void | `blink.floorCheck` 12: the landing spot needs a block below; y clamped to the loaded section range (invalid section = stop) | 2.2; world height limits INFERRED from section refs |
| Through walls | a wall is a blocked step; thin walls (1 block) are not skipped because steps are 0.5 and both body blocks are tested | 2.2 |
| Island protection | SkyyIslands protects blocks by events, no borders exist; blink obeys solid blocks like walking | 2.7 |
| Cross-world | only the same-world `Teleport` is ever built | 2.2 VERIFIED |
| Fall-damage escape | keepFall on: the fall speed survives the blink | 2.2 VERIFIED formula |
| Void hop | hop halves with no ground behind; the hop goes away from the look direction so a player looking into the void hops toward land | 2.3 |
| PvP / friendly fire | engine cancels with PvP off; our filter adds `trav.players` + never party; heal orb heals allies only | 2.7 VERIFIED + 1.3 |
| Spam / cost | hold time + Mana; trails capped by `trav.maxLive`; one damage per enemy per tick; `blink.cooldown` optional | 1.3 |
| Death / logout / world change mid-effect | effects finish on their own clock; damage ticks need a valid caster ref; heals continue (no XP); PlayerReadyEvent on world switch does nothing here | 1.3 |
| Marker abuse | Damage 0, invisible, removed after the trail; a stray collision deals 0 | 2.2 INFERRED (T5) |
| Server cost | trail: 1 box query + <= N segment distances every 500 ms + ~10 particle spawns; orb: 1 sphere query per second + 9 spawns per 0.5 s; quick ranges: 1 distance per live quick orb per tick; 64 live effects per world max | 2.5, 2.6 |
| Client desync | nothing client-predicted changes at runtime (Mana / hold keys build-time, S:7); the server hop is a ChangeVelocity packet like the double jump | 2.3 |
| Creative / admins | no special case except XP (SkyySkills) | - |

## 5. Harness plan (`SkyyArmory/test_skyyarmory_0.1.1.py`, bare JVM, `-Xverify:all -XX:-UsePerfData`, TEMP in tools/dev/scratch/armory011/; `SkyyClasses/test_skyyclasses_0.1.12.py`; `python tools/ci/lint.py` 0 fails)
- T1 decode every generated interaction / projectile / model / particle file standalone (the 0.1 T-series) + assert: no
  `SkyyArmory_Staff_Stamina*` file, no Stamina key in any staff chain, every staff charged Launch names `SkyyArmory_Blink_<M>`, every
  Blink projectile has Damage 0 / Gravity 0, `SkyyArmory_Marker` has no attachment / particles / trails.
- T2 bytecode probes (the 0.1 `probe_sig` list, build 1152): `Teleport.createForPlayer(Vector3dc, Rotation3fc)`, `withoutVelocityReset`,
  `Velocity.addInstruction`, `TargetUtil.getAllEntitiesInSphere / InBox`, `ProjectileComponent.assembleDefaultProjectile`,
  `EffectControllerComponent.addEffect`, `Damage.HIT_LOCATION`, `DamageSystems.executeDamage(Ref, CommandBuffer, Damage)` - a game
  update that renames one stops the build; plus print the `putComponent` list of `LaunchProjectileInteraction#firstRun` (2.6).
- T3 `TravMath` unit tests on a fake 3-D passable grid: wall at 6 -> lands 5.7; open void -> last floored step; up through a ceiling;
  straight up with floorCheck; segment distances; hop vectors for look up / down / level; damage and heal per tick.
- T4 config: every row of 1.4 emits, defaults parse, `quick.life` hidden, KEEP 10.
- T5 SkyyClasses: `class:fn:heal` refuses non-Priests and respects HealBudget; `class:fn:ally` on fake party answers.
- Lint rules unchanged (perm_group_leaks n/a: no commands added).

## 6. Test steps for Skyy (game closed for the deploy; backup first; Server Setup -> Armory shows the new rows)
1. Mage, Iron staff, open field: hold 1 s -> you appear ~10 blocks ahead; a gold line hangs 3 s; Stamina bar untouched. Walk a mob into
   the line: it takes damage twice a second (chat / health bar). Blink up a cliff by looking up.
2. Stand 3 blocks from a wall, blink into it -> you land just in front, never inside. Blink at a glass pane -> blocked (report: should
   glass count as open? T4 default says no).
3. Blink off an island edge over the void -> you stop at the last block with ground below. Fall from height and blink midway -> you still
   take the fall damage.
4. Priest, Iron wand: hold -> you hop back (look at the floor: you hop straight up), the orb bursts on a mob: nearby mobs take ~60%, a
   glowing sphere stays ~3.5 s, you and a party member inside heal every second (chat feedback). A party member outside heals nothing.
5. Wand tap at two mobs in a line: both hit; the shot vanishes at a wall and at ~16 blocks. Staff tap: one mob only, ~24 blocks, a bit
   more damage than the wand tap at the same Mana.
6. PvP world off: blink trail / burst on another player = nothing. PvP on, party member = nothing; stranger = damage.
7. Server Setup: set blink.distance 20 and hop.force 0, cast again (live, no restart); set staff.mode orb -> the staff hold fires the
   old orb; part.trav off -> everything vanilla-0.1 again.
8. Watch the log for WARN lines from ArmoryTravSys / ArmoryHitSys / TravTick; `/skyycfg` history shows the row changes.

## 7. Open questions (each with the recommended default)
1. Blink when NO free spot exists ahead (you face a wall): spend the Mana and draw the trail at your feet (default), or refund the Mana?
   [default: spend + trail - keeps the client-predicted Mana honest; a refund would desync the bar for a moment]
2. Fall damage: keep the falling speed through a blink (default on, no escape), or make a blink a soft landing (off)?
3. Hop mode: server push (default; live force + void check, ~1 tick + ping late) or the client dash (instant, fixed force, no void check)?
4. Direct-hit enemy: full shot only (default), or full shot + the 60% burst too?
5. Burst knockback: off (default) or the small explosion push on?
6. Heal orb allies: party only (default) or every non-hostile player? And should the orb heal pay Divinity XP like the heal share
   (default yes, through class:fn:heal)?
7. Trail damage on players (PvP on): yes like any damage (default), or trails never hurt players?
8. Pierce count 3 (default; "several") - or unlimited within 16 blocks?
9. Staff quick-shot bonus +15% per Mana (default) - Skyy's "a little more"?
10. Cooldowns: none (default; Mana + hold time) - or a `blink.cooldown` of 2 s?
11. Glass / fences / leaves as blink blockers: block (default, like walking) - or let the blink pass transparent blocks?
12. `quick.life` row: hide (default) or remove; `hop.mode` / `staff.stamina` shown as read-only info rows (default yes).

## 8. Skyy's answers 2026-10-05 (BEAT the defaults above - docs/answered/classes.md, LOCKED 2026-10-05)

- A blink that does not move you costs NOTHING (no Mana, no Stamina) - not "spend" as in question 1.
- Every traversal costs Mana AND Stamina. Magical ones (staff blink, wand hop) = 2 parts Mana : 1 part Stamina (e.g. 10 + 5, 20 + 10);
  physical ones (Monk ...) more Stamina than Mana. Section 1's Stamina removal applies to the quick / normal staff casts only.
- Wand heal orb heals EVERYONE in range who is not hostile, party members MORE (pick a default ratio, e.g. party 100% / others 50%, as a row);
  any traversal lock-on targets party members only.
- Wand quick-shot pierce has NO cap - only its range (16 blocks) limits it.
- Everything else = the recommended defaults in section 7.
