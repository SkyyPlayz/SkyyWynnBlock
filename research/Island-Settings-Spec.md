# Island settings: build spec (SkyyIslands 0.5, on top of 0.4.4)

*Written 2026-09-24 by the research workflow `skywynn-island-settings` (writer). Research only: no build script, mod folder or game file was changed.*
*Builds on `SkyyIslands/build_skyyislands_0.4.4.py` (one island per profile, `islands/<pkey>.properties`, GuardDamage/Break/Place/Pickup/Use). Owner: Skyy (they/them).*

**Skyy's ask (2026-09-24):** "for island visitors, look into some minecraft skyblock mods. they usually have a settings menu where you can control all of that. (and a lot more, like the island biome. turning on and off visitors and what not.)"

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode or reflection (`tools/dev/reflect.py`, `bc.py`, `bcfull.py`, `cpgrep.py`), read from `Assets.zip`, an installed mod jar (read-only), or our own 0.4.4 script. UNVERIFIED = design or inference that still needs the in-game test in section 9. `[SKYY?]` = a choice Skyy should confirm.

---

## 0. Verdict (plain words)

**Yes, a SkyBlock-style settings menu can be built in one version, and nearly everything Skyy named is possible now.** The key finding: Hytale already ships its own protection rules (the trigger-volume "no use / no door / no harvest / no build / no damage" systems in `com.hypixel.hytale.builtin.triggervolumes.system.TriggerVolumeRuleSystems$*`). They cancel exactly the events our guards listen to and classify blocks with the same `BlockType` tests we need (`isDoor()`, `getFarming().getStages()`). So every per-role flag below copies the engine's own test instead of guessing.

| Skyy asked for | 0.5? | How (all VERIFIED unless noted) |
|---|---|---|
| Roles (who may do what) | **Now** | Owner / Co-op member / Trusted / Visitor + a ban list. One click per grid cell. |
| Per-role permission flags | **Now** | 14 flags (build, break, chests, doors, benches, furnaces, beds, seats, crops, animals, mobs, pickup, drop, other blocks) on 8 engine events. |
| Visitors on/off | **Now** | Public / Friends only / Closed, visitor limit, expel, ban, lock/unlock. Custom logic, enforced at `/island visit`, on arrival and by a 5 s sweep. |
| PvP | **Now** | `WorldConfig.setPvpEnabled` per island world; the engine enforces it. |
| Mob spawning | **Now** | `WorldConfig.setSpawningNPC`; what spawns depends on the biome. |
| **Island biome** | **Now** | A biome is a **preset = grass tint + Environment asset**: it changes grass colour, sky/weather pool, water tint, ambient sound and the wildlife table. Vanilla `/chunk tint` and the builder-tools `/environment` command use the same calls, including the live resend to players. 11 presets (4.4). |
| Weather lock | **Now (dry weathers only)** | Vanilla `/weather set` pattern. Rain/storm are left out on purpose: forced rain gives crops a permanent x2.5 growth bonus (`Server/Farming/Modifiers/Water.json`). |
| Visitor landing point | **Now** | 5-argument `teleportPlayerToLoadingInstance(..., spawnTransform)`. |
| Visit notifications | **Now** | Chat ping to the owner and co-op when someone arrives. |
| Time lock (always day/night) | **Later** | Possible, but pausing time freezes furnaces, crops and coops (they read `WorldTimeResource.getGameTime()`), and skipping nights speeds them up. This needs a design call first (4.8). |
| Visits while the owner is offline | **Later** | `/island visit <player>` needs the target online today (`PLAYER_REF`). |
| Split animals/monsters spawning, custom roles, island warps list, visitor keep-inventory | **Later** | See 4.8. |

**Biome verdict: feasible now, as 11 presets.** The engine keeps colour and "biome" apart. **Colour** is a per-column tint (`BlockChunk.setTint`). The **Environment** is a per-block index (`BlockChunk.setEnvironment` / `EnvironmentChunk.setColumn`). It drives the weather forecast, water tint, the AmbienceFX conditions (48 ambience files key on `EnvironmentIds`) and the NPC spawn rules (96 `Server/NPC/Spawn/World/*.json` files list `Environments`). What is **not** possible: Minecraft-style terrain per biome (the island's blocks stay as built) or authoring new Environment assets at runtime. We only pick from the 122 shipped ones.

---

## 1. What the SkyBlock plugins do

My own summary of the plugin docs (sources in section 10).

| Plugin | Roles | Settings menu | Visitor control | Biome |
|---|---|---|---|---|
| **BentoBox / BSkyBlock** | Banned < Visitor < Coop (session, ends when the granter logs off) < Trusted (persistent) < Member < Sub-owner < Owner. One number per rank. | `/island settings`: owner edits, others see it read-only. Each flag icon **cycles the minimum rank** on click. Basic/Advanced/Expert view toggle hides rarely used flags. On/off "settings flags" (PvP, spawning) sit apart from the rank flags. | `ALLOW_VISITS_FLAG` master switch, `LOCK` flag, `/island ban/unban/banlist`, `team kick` for members, visit ping to members. No visitor headcount cap. | Biomes addon: `/island biomes`, whole island / chunk / radius, unlock cost + use cost. |
| **SuperiorSkyblock2** | Guest < Coop < Member < Moderator < Admin < Leader, with per-player overrides. | Separate menus for Settings (island flags), Permissions (role x privilege grid), Biomes, Warps, Members, Bank, Bans, Visitors. | `/island open`/`close`, `/island expel`, `/island ban`/`pardon`/`bans`, a Visitors menu with a per-player expel. Turning PvP on sends visitors to spawn first. | Biome menu, admin-priced. |
| **IridiumSkyblock** | Thin: a "trust" tier below members, the rest via LuckPerms. | Bank, upgrades. | Trust / untrust. | Biome shop paid in Crystals, per dimension. |
| **ASkyBlock** (legacy) | Owner + team. | `/is settings`: the owner toggles PvP, spawning, fire and so on. Who may use the menu is itself a permission node. | Ban / expel. | Paid biome change. |
| **Hypixel SkyBlock** | Owner, co-op (removing a co-op member needs a vote), guests. | Island Settings page or talking to Jerry. | Three combinable toggles: Visits by Anyone / Friends / Guild. Rank-based guest cap (1 by default). Guest roster with one-click kick (temporary). `/guestlocation` sets where guests land. | Biome customisation (a progression reward). |

**Common flags and their usual defaults** (BentoBox shipped defaults, SuperiorSkyblock2 privileges):

| Flag | Usual default |
|---|---|
| Place / break blocks | Member |
| Chests / containers | Member |
| Doors, trapdoors, gates | **Visitor** (open by default) |
| Crafting table | **Visitor** in BentoBox |
| Furnace / anvil / brewing | Member |
| Beds | Member |
| Farm animals: hurt, breed, shear, milk | Member |
| Hostile mobs | Visitor |
| Item pickup / drop | Visitor in BentoBox (SkyyIslands 0.4.4 is stricter: members only) |
| PvP | Off |
| Visits allowed | On |
| Change settings | Owner |

**Five things every system agrees on:** (1) visitors look but don't touch by default. (2) "Can anyone visit" is its own switch, separate from build rights. (3) An owner can see who is on the island now and remove one person in one click. (4) Expel (temporary) and ban (persistent) are two separate actions. (5) The biome is a reward or cost, not a free base setting.

---

## 2. SkyWynn roles (recommendation: 4 roles + a ban list)

| Rank | Role (UI name) | Who | How you get it | How you lose it | Stored |
|---|---|---|---|---|---|
| 3 | **Owner** | The player whose **active profile** owns the island | Created the island | Never (profile delete is SkyyProfiles' business) | Island file name = owner pkey |
| 2 | **Co-op** (Member) | Shares the island: builds, uses chests, runs the farm | Owner: `/island invite <player>` (0.4.4 command, unchanged) | Owner: `/island kick <name>` or the Members tab | `members=` list of **profile keys** |
| 1 | **Trusted** | A friend who may help build and craft but **not** open your chests or furnaces (by default) | Owner: `/island trust <player>`, or "Trust" next to a visitor on the Visitors tab | Owner: `/island untrust <name>` | `trusted=` list of profile keys |
| 0 | **Visitor** | Everyone else, **including you and your co-op on another profile** | Being there | n/a | n/a |
| -1 | **Banned** | Can't enter. Denied everything, even doors | Owner: `/island ban <player>` | Owner: `/island unban <name>` | `banned=` list of **player UUIDs** (a ban hits the person, every profile) |

Why this set:
- It keeps `/island invite` = co-op exactly as in 0.4.4 (design lock batch 2 #6: "players can share and visit each other's private islands").
- **Trusted** is the only new rank, and it is the one both BentoBox and Iridium use for "helper, not family". Players ask for it constantly.
- **No BentoBox "Coop" session rank and no Sub-owner.** SkyWynn already uses the word co-op for members, and a rank that expires when someone logs off adds a lot of state for little gain. Sub-owner only matters for big teams; the co-op cap is 5 `[SKYY?]`.
- **Membership is bound to a profile key (pkey), not a UUID.** This is the one semantic change from 0.4.4 (section 8.1). A bare UUID entry already equals that player's profile-1 key (`tools/PROFILES-CONTRACT.md`), so every existing `members=` line keeps working untouched.
- Admins (`skyyislands.admin`) act as Owner for every flag and entry check, as in 0.4.4. They cannot edit someone else's settings in 0.5 (an admin settings command is "later").
- Who may do what: settings, ban, unban, trust, untrust, kick, lock and unlock are **Owner only**. **Expel** is Owner **or co-op** (so a co-op member can remove a griefer while the owner is away).

---

## 3. Permission flags

### 3.1 Semantics (BentoBox "minimum rank")
Each flag stores one **minimum role**: `visitor | trusted | member | owner`. A role may do it when `rank >= min`. The Owner is always allowed. The grid (section 6.2) shows it as YES/NO cells per role. **Clicking a cell for role R:** if R is allowed now, set `min = R + 1` (denies R and every rank below it). If R is denied now, set `min = R` (allows R and every rank above it). Always one click, never an impossible state like "visitors may but co-op may not".

### 3.2 The 14 flags, defaults and hooks

| # | id | Grid label (hint line) | Default min | Visitor / Trusted / Co-op | 0.4.4 behaviour | Engine hook (all VERIFIED) |
|---|---|---|---|---|---|---|
| 0 | `build` | Place blocks | trusted | no / yes / yes | co-op only | `PlaceBlockEvent` (CancellableEcsEvent) |
| 1 | `break` | Break blocks (hitting and breaking) | trusted | no / yes / yes | co-op only | `BreakBlockEvent`, `DamageBlockEvent`, `UseBlockEvent$Pre` with `InteractionType.Primary` |
| 2 | `containers` | Chests & barrels (also breaking them) | member | no / no / yes | co-op only | `UseBlockEvent$Pre` (ICancellableEcsEvent), block classified CONTAINER |
| 3 | `doors` | Doors, trapdoors, fence gates | visitor | yes / yes / yes | everyone | `UseBlockEvent$Pre`, `BlockType.isDoor()` |
| 4 | `crafting` | Crafting benches (Workbench, Armory, Builder's...) | trusted | no / yes / yes | co-op only | `UseBlockEvent$Pre`, `getBench().getType() != Processing` |
| 5 | `processing` | Furnace, campfire, tannery, salvager (also breaking them) | member | no / no / yes | co-op only | `UseBlockEvent$Pre`, `BenchType.Processing` |
| 6 | `beds` | Beds (sleep, set respawn) | trusted | no / yes / yes | co-op only | `UseBlockEvent$Pre`, `getBeds() != null` |
| 7 | `seats` | Chairs & benches (sit) | **visitor** | yes / yes / yes | co-op only (**loosened**) | `UseBlockEvent$Pre`, `getSeats() != null` |
| 8 | `harvest` | Crops & plants (F-harvest, hitting crops) | trusted | no / yes / yes | co-op only | `UseBlockEvent$Pre` + `BreakBlockEvent` + `DamageBlockEvent` on crop/plant blocks |
| 9 | `animals` | Farm animals (hurt, interact, coops) | member | no / no / yes | **not guarded** | `Damage` (DamageEventSystem, filter group) with an NPC victim in the animal list; `UseEntityEvent$Pre` on that NPC; coop block use |
| 10 | `mobs` | Fight hostile mobs | visitor | yes / yes / yes | not guarded (same) | `Damage` with any other NPC victim |
| 11 | `pickup` | Pick up items | trusted | no / yes / yes | co-op only | `InteractivelyPickupItemEvent` |
| 12 | `drop` | Drop items | trusted | no / yes / yes | **not guarded** | `DropItemEvent$PlayerRequest` (CancellableEcsEvent, `Store.invoke(ref, ev)` on the dropper) |
| 13 | `other` | Lanterns, coffins, teleporters, other blocks | trusted | no / yes / yes | co-op only | `UseBlockEvent$Pre`, anything not matched above |

Two pseudo-flags exist for the bridge only (not in the grid): `enter` (may this player be on the island now, section 4.1) and `settings` (owner only).

### 3.3 Block classifier (exact, first match wins; javassist-safe)
Class `IslandPerms`, static methods. The type names are the fully qualified ones in 0.4.4's `BTY` and friends.
```java
// flag ids: BUILD=0 BREAK=1 CONTAINERS=2 DOORS=3 CRAFTING=4 PROCESSING=5 BEDS=6 SEATS=7 HARVEST=8 ANIMALS=9 MOBS=10 PICKUP=11 DROP=12 OTHER=13
public static boolean isCrop(BlockType bt) {                 // the engine's own NoHarvestUse test
  FarmingData f = bt.getFarming();
  return f != null && f.getStages() != null;                 // tilled soil has FarmingData but no stages -> not a crop
}
public static boolean isHarvestPlant(BlockType bt) {         // Aetherhaven isHarvestStyleBreak + a Plant_ filter
  if (isCrop(bt)) return true;
  BlockGathering g = bt.getGathering();
  return g != null && g.getHarvest() != null && String.valueOf(bt.getId()).startsWith("Plant_");
}
public static int containerKind(BlockType bt) {              // -1, CONTAINERS or PROCESSING
  Bench b = bt.getBench();
  if (b != null && b.getType() == BenchType.Processing) return PROCESSING;
  java.util.Map im = bt.getInteractions();
  Object rid = im == null ? null : im.get(InteractionType.Use);
  if (rid != null && String.valueOf(rid).indexOf("Container") >= 0) return CONTAINERS;   // Open_Container, Open_Treasure_Container
  return -1;
}
public static int useFlag(BlockType bt, InteractionType t) { // UseBlockEvent$Pre
  if (t == InteractionType.Primary) return BREAK;            // hitting a bed/treasure chest = breaking it
  if (t != InteractionType.Use && t != InteractionType.Secondary) return -1;   // collisions, pick: not guarded
  if (bt.isDoor()) return DOORS;                             // the engine's own NoDoorOpen test
  Bench b = bt.getBench();
  if (b != null) return b.getType() == BenchType.Processing ? PROCESSING : CRAFTING;
  if (bt.getBeds() != null) return BEDS;
  if (isCrop(bt)) return HARVEST;
  if (containerKind(bt) == CONTAINERS) return CONTAINERS;
  if (bt.getSeats() != null) return SEATS;
  if (String.valueOf(bt.getId()).startsWith("Coop_")) return ANIMALS;
  return OTHER;
}
public static int breakFlag(BlockType bt) { return isHarvestPlant(bt) ? HARVEST : BREAK; }   // Break + DamageBlock
```
**Extra rule (anti-loot):** a break, damage-block or Primary-use on a block with `containerKind(bt) >= 0` needs **both** `break` **and** that container flag. Breaking a chest drops its contents, so this stops a trusted builder from looting by breaking.

**Why this is exact (Assets.zip scan of every block item, parents resolved, VERIFIED):**
- 46 doors, trapdoors and fence gates carry `IsDoor: true` (`Use` = `Door` / `Door_Horizontal`).
- 46 containers have `Use` = `Open_Container`, plus 1 `Open_Treasure_Container`.
- Benches: `Bench.Type` Crafting (Alchemy, Arcane, Armour, Cooking, Farming, Furniture, Loom, Trough, Weapon, WorkBench), DiagramCrafting (Armory), StructuralCrafting (Builders), Processing (Campfire, Furnace, Salvage, Tannery). `BlockType.processConfig` puts the bench's root interaction under `InteractionType.Use`, so bench use goes through `UseBlockEvent$Pre` (bytecode).
- 15 beds have `Beds` + `Use` → inline `Bed` (and `Primary` → `Check_Can_Break_Respawn`).
- 31 seats have `Seats` + `Use` → `Block_Seat`.
- 103 blocks have `Farming`, 97 of them crops/saplings/cactus with stages. `Soil_Dirt_Tilled` has only a `SoilConfig`.
- 47 `Use` → inline `ChangeState` (lanterns, trophies), plus coffins, `OpenCustomUI` blocks (Teleporter, Launchpad, spawner block), `Coop_Chicken` (`UseCoop`), `Deco_Kweebec_Plush`: all go to OTHER, or ANIMALS for the coop.
- `UseBlockInteraction.doInteraction` fires the event only when `getInteractions().get(type)` exists (bytecode), so plain blocks never reach GuardUse.

**Harvest paths (VERIFIED):** the unarmed Use chain in `Server/Item/Unarmed/Interactions/Empty.json` is `UseBlock → (fail) UseEntity → (fail) BreakBlock {Harvest: true}`. Crops **with** a Use interaction fire `UseBlockEvent$Pre` (the engine's `NoHarvestUse` checks exactly `getFarming().getStages()`). Crops **without** one reach `BlockHarvestUtils.performPickupByInteraction`, which fires `BreakBlockEvent`. Hitting fires `DamageBlockEvent` and then `BreakBlockEvent` (`performBlockBreak`). All three are covered. (This corrects the Hytale research note: 0.4.4 GuardUse does catch F-harvest on crops that have a Use interaction, and GuardBreak catches the rest.)

### 3.4 Entity flags (animals / mobs)
- **Hurt:** a new class `GuardHurt extends com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem` (no-arg constructor). Copied from the engine's `TriggerVolumeRuleSystems$DamageRuleFilter`:
  - `getGroup()` returns `DamageModule.get().getFilterDamageGroup()`, so it runs before the damage is applied.
  - `getQuery()` returns `NPCEntity.getComponentType()` (a ComponentType is a Query; DamageRuleFilter returns `TransformComponent.getComponentType()`).
  - `handle(int, ArchetypeChunk, Store, CommandBuffer, EcsEvent)` casts to `Damage`. If `getSource()` is a `Damage$EntitySource` (`Damage$ProjectileSource` extends it, so arrows count), take `getRef()` and read `PlayerRef` via `buf.getComponent(ref, PlayerRef.getComponentType())`. If it is a player, check `animals` or `mobs` for that player's role and `d.setCancelled(true)` on a deny.
  - Victim class: `NPCEntity.getRoleName()` (the engine's `resolveEntityName`). It is an **animal** when it is in `ANIMALS`, a comma list the build script reads from `Assets.zip` at build time: every role under `Server/NPC/Roles/Creature/Livestock/` (70, including all `Tamed_*`) and `Creature/Critter/` (7), plus config `animals.extra=`. Everything else is a mob.
- **Use (interact with an animal):** `GuardUseEntity` on `UseEntityEvent$Pre` (ICancellableEcsEvent, invoked on the **player** by `UseEntityInteraction.firstRun`, bytecode). Target = `getTargetEntity()`. An animal needs `animals`; any other NPC → `other`.
- **Not guardable (VERIFIED gap):** milking and shearing with a bucket or shears run `ContextualUseNPCInteraction`, which fires **no** event. Visitors can milk or shear. Harmless, documented.
- **PvP** is not a flag. The engine's `DamageSystems$PlayerDamageFilterSystem` reads `WorldConfig.isPvpEnabled()` (section 4.2).

### 3.5 "Levers and buttons": not a thing in this Hytale build (VERIFIED)
`Deco_Lever` and `Deco_Plate` have **no BlockType interactions**. The lever's `"Secondary": "Block_Secondary"` sits on the *item* (placing it), and no redstone-style mechanism exists. The closest are the 47 toggle blocks (lanterns etc., `ChangeState`), which fall under `other`. If a later Hytale update adds working switches, they land in `other` automatically.

### 3.6 Guard classes (ONE registerSystem per class)
The 0.4.4 base `GuardSystem` loses `exempt()` and gains `int flagFor(EcsEvent)` (-1 = not guarded) and `int extraFlag(EcsEvent)` (-1 = none). `handle()` computes `rank = IslandPerms.rank(ownerKey, pr)` and allows when `rank >= min[flag] && (extra < 0 || rank >= min[extra])`. On a deny it cancels via `ICancellableEcsEvent.setCancelled(true)` (covers both base types) and sends a throttled message (existing WARNED, 3 s) naming the rule, e.g. `[Island] Chests & barrels on Skyy's island: co-op only.` The other-profile text stays.

| Class | Event | flagFor / extraFlag |
|---|---|---|
| GuardDamage (0.3) | DamageBlockEvent | `breakFlag(bt)` / `containerKind(bt)` |
| GuardBreak (0.3) | BreakBlockEvent | `breakFlag(bt)` / `containerKind(bt)` |
| GuardPlace (0.3) | PlaceBlockEvent | BUILD / -1 |
| GuardPickup (0.3) | InteractivelyPickupItemEvent | PICKUP / -1 |
| GuardUse (0.4.4) | UseBlockEvent$Pre | `useFlag(bt, type)` / Primary: `containerKind(bt)` |
| **GuardDrop** (new) | DropItemEvent$PlayerRequest | DROP / -1. **Hard deny** for the owner on another profile (section 8.2) |
| **GuardUseEntity** (new) | UseEntityEvent$Pre | ANIMALS or OTHER / -1 |
| **GuardHurt** (new, extends DamageEventSystem) | Damage (filter group) | ANIMALS or MOBS |

---

## 4. Island settings

| Setting | Values | Default | Hook | When |
|---|---|---|---|---|
| Who may visit | Public / Friends only (co-op + trusted) / Closed (co-op only) | Public (= 0.4.4) | custom: `/island visit`, arrival check, 5 s sweep | **Now** |
| Visitor limit | 1..`visit.limitMax` (config, default 10) | 5 `[SKYY?]` | `World.getPlayerRefs()` (thread-safe) | **Now** |
| Expel | one visitor to the hub + 60 s re-entry block | n/a | `HubCmd.sendToHub` on the island's world thread | **Now** |
| Ban list | UUIDs, max 100 | empty | custom | **Now** |
| Lock / unlock | lock = Closed and remember the previous mode | n/a | alias of "Who may visit" | **Now** |
| Visit ping | on/off | on | chat to online owner + co-op | **Now** |
| Visitor landing point | island spawn / a point you set | island spawn | 5-arg teleport | **Now** |
| PvP | on/off | off (= template) | `WorldConfig.setPvpEnabled` + `markChanged` | **Now** |
| Mob spawning | on/off | off (= template) | `WorldConfig.setSpawningNPC` + `markChanged` | **Now** |
| Biome | 11 presets | Void Sky (= today) | tint + Environment + live resend | **Now** |
| Weather lock | biome default + 7 dry weathers | biome default | WeatherResource + WorldConfig | **Now** |
| Time lock | n/a | n/a | exists, see 4.8 | **Later** |

### 4.1 Visitors: mode, limit, expel, ban, lock (all custom, no engine blocker)
- **Entry rule** `mayEnter(settings, rank, uuid, world)`: false if banned; false if mode Closed and `rank < member`; false if mode Friends and `rank < trusted`; false within 60 s of an expel from this island (memory map `EXPELLED`, key `worldName|uuid`); false if `rank == visitor` and the current visitor count is already at the limit. Admins are always true.
- **Where it is checked:**
  1. **`IslandCmd.visit()`** before calling `go()`, so a refused player never even loads the world.
  2. **Arrival:** `IslandReady` already hears `PlayerReadyEvent` on **every** world switch (0.2.1 fact). 0.5 keeps login routing for the first ready of a session. Every later ready schedules `ArrivalTask` (1.5 s, the RouteTask/RouteDispatch pattern onto the player's world thread). If the world is an island and `!mayEnter` → `HubCmd.sendToHub(...)` plus a reason message. If the player is a visitor → welcome line (`Visiting Skyy's island - PvP off - you may: doors, seats, hostile mobs`) and the visit ping.
  3. **Sweep:** `SeenTick` (already every 5 s) dispatches `SweepTask` with `w.execute(...)` to each loaded island world that has players. On that world thread it walks `w.getPlayerRefs()` and expels anyone who fails `mayEnter` without the limit clause. This catches `/tpa`, vanilla `/teleport`, respawns, profile switches while standing on the island, and ban/lock changes.
- **Visitor count** = players in `w.getPlayerRefs()` with rank visitor. VERIFIED: `World.playerRefs = Collections.unmodifiableCollection(ConcurrentHashMap.values())`, so it can be read from any thread. The limit is enforced on arrival, give or take one on simultaneous arrivals; lowering it never expels anyone already there (SkyBlock norm).
- **Expel** uses the proven login-routing call `HubCmd.sendToHub(store, ref, pr, world)` (adds a `Teleport` component on the target's world thread). `InstancesPlugin.exitInstance` is not used: it throws when there is no return point, and its return point may be another island.
- **Ban** of someone inside → immediate expel. **Lock/Closed/Friends** while visitors are inside → the same sweep runs at once.

### 4.2 PvP (VERIFIED engine flag)
Vanilla `WorldConfigSetPvpCommand` pattern: `w.getWorldConfig().setPvpEnabled(b); w.getWorldConfig().markChanged();` `WorldConfigSaveSystem` persists it to the island world's own `config.json`. It is per world, so per island. **Turning PvP on expels current visitors** (rank 0) with a message, as SuperiorSkyblock2 does to stop PvP traps. Trusted and co-op stay and get a warning. Visitors arriving later see "PvP is ON here" in the welcome line.

### 4.3 Mob spawning (VERIFIED engine flag, biome-dependent)
`setSpawningNPC(b)` + `markChanged()` (vanilla `SpawnCommand$DisableCommand`). Read by `WorldSpawningSystem`, `SpawnJobSystem`, `SpawnControllerSystem` and `SpawnMarkerSystems$Ticking`. **What spawns comes from the Environment:** `Env_Default_Void` (today's biome) appears in **zero** spawn rules, so spawning ON does nothing on a Void Sky island. The UI says "needs a biome with wildlife". Turning it off does not remove mobs already spawned. One switch covers animals and monsters together; splitting them is later.

### 4.4 Biome (feasible now): presets, how it is applied, persistence

**Presets** (tint = `Default.Colors[0/1]` of the matching Orbis tile in `Server/World/Default/Zones/*`; wildlife = NPC ids whose `Server/NPC/Spawn/World/*.json` lists that environment; all VERIFIED from Assets.zip):

| key | Label | Grass tint (ARGB int) | Environment | Weather pool | Wildlife when spawning is on |
|---|---|---|---|---|---|
| `void` | Void Sky (default) | #5b9e28 (-10772952, 0.4.2 GRASS) | Env_Default_Void | Default_Void only | none (0 rules) |
| `plains` | Plains | #5b9e28 | Env_Zone1_Plains | Zone1 sunny, fireflies, cloudy, fog, rain, storm | cows, sheep, pigs, chickens, horses, deer, foxes, rabbits; wolves; void larvae at night (28 ids) |
| `forest` | Forest | #3b8e32 (-12874190) | Env_Zone1_Forests | inherits Env_Zone1 | boars, bunnies, bears, owls, birds (22) |
| `autumn` | Autumn | #c07321 (-4164831) | Env_Zone1_Autumn | autumn windy, rain, sunny | Zone1 forest set (22) |
| `azure` | Azure Forest | #2f868a (-13662582) | Env_Zone1_Azure | inherits Env_Zone1 | 26 ids |
| `swamp` | Swamp | #445f0f (-12296433) | Env_Zone1_Swamps | swamp, swamp fog/rain, fireflies | wild pigs, frogs, fen stalker, skeletons (20) |
| `savanna` | Savanna | #d7be35 (-2638283) | Env_Zone2_Savanna | inherits Env_Zone2 (sunny, blazing, cloudy, thunder) | antelope, hyenas, meerkats, sand skeletons (17) |
| `oasis` | Desert Oasis | #b9b828 (-4605912) | Env_Zone2_Oasis | sunny, blazing, haze, cloudy | crocodiles, flamingos, sand lizards, sand skeletons (19) |
| `tundra` | Tundra | #487e4d (-12026291) | Env_Zone3_Tundra | inherits Env_Zone3 | cows, moose, wild pigs, skeleton scouts (14) |
| `glacial` | Glacial | #699587 (-9857657) | Env_Zone3_Glacial | snow, snow storm, northern lights | polar bears, bison, penguins, frost skeletons (21) |
| `wastes` | Ash Wastes | #786133 (-8888013) | Env_Zone4_Wastes | inherits Env_Zone4 | undead cows, skeleton horses, burnt skeletons, wraiths (7) |

Note the natural (not forced) rain of Plains, Swamp and others waters crops the normal vanilla way. That is fine; only a *locked* rain would be an exploit.

**Apply (world thread; `BiomeApply.apply(World w, String key)`). Every call below is VERIFIED; the sequence is the vanilla builder-tools `BuilderState.environment` plus `ChunkTintCommand`:**
```java
int idx = Environment.getAssetMap().getIndex(envId);      // Integer.MIN_VALUE = missing -> refuse (EnvironmentCommand does this check)
for (int cx = -R; cx <= R; cx++) for (int cz = -R; cz <= R; cz++) {        // R = config biome.radiusChunks, default 4
  WorldChunk c = w.getChunkIfLoaded(ChunkUtil.indexChunk(cx, cz));
  if (c == null) continue;
  BlockChunk bc = c.getBlockChunk();
  EnvironmentChunk ec = bc.getEnvironmentChunk();
  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) { bc.setTint(x, z, argb); ec.setColumn(x, z, idx); }
  bc.setEnvironment(0, 0, 0, idx);   // BlockChunk.setEnvironment nulls cachedEnvironmentsPacket + markNeedsSaving (bytecode);
                                     // setTint already nulls cachedTintmapPacket + markNeedsSaving
  c.markNeedsSaving();
  w.getNotificationHandler().updateChunkTints(c.getIndex());          // vanilla /chunk tint
  w.getNotificationHandler().updateChunkEnvironments(c.getIndex());   // vanilla builder-tools /environment
}
WorldConfig cfg = w.getWorldConfig();                                  // future chunks of THIS island
cfg.setWorldGenProvider(new VoidWorldGenProvider(new com.hypixel.hytale.protocol.Color((byte) r, (byte) g, (byte) b), envId));
cfg.markChanged();
```
- `EnvironmentChunk.setColumn(x, z, idx)` rewrites a whole 320-block column in one call: 1,024 calls per chunk, about 80k for R=4. It keeps its own block counts (bytecode). **Fallback** if the in-game test shows stale columns: the builder-tools per-block loop `bc.setEnvironment(x, y, z, idx)`, restricted to y 64..255.
- Whether the live resend shows the change without re-entering is **UNVERIFIED in game** (0.4.2's tint fix was "seen after re-entering"). The vanilla commands rely on these same resend calls, so it should update live.
- The world's live generator is not swapped. New chunks generated before the next reload use the old values; the arrival re-apply fixes them.
- **Arrival re-apply:** 0.4.2's `RelightNow` (every arrival) generalises `FillTask.tintChunk` into `BiomeApply.fixChunk(chunk, argb, idx)`. For each loaded chunk within R, when `bc.getTint(8, 8) != argb` or `bc.getEnvironment(8, 128, 8) != idx`, apply to that chunk. `FillTask` uses the island's biome tint instead of the `GRASS` constant.
- **Cost / gating** (every plugin treats the biome as a reward): 0.5 ships `biome.cost=0` (coins via `coins:fn:take`; a refusal means no change) and `biome.cooldownSeconds=60`. Admins trim the list with `biomes=`. Tying unlocks to Exploration zone discovery (Zone 2 biomes after discovering Zone 2) is `[SKYY?]`, later.

### 4.5 Weather lock (dry weathers only)
The vanilla `WeatherSetCommand.setForcedWeather(World, String, ComponentAccessor)` sequence (VERIFIED), on the island world thread with `store = w.getEntityStore().getStore()`:
`((WeatherResource) store.getResource(WeatherResource.getResourceType())).setForcedWeather(id); cfg.setForcedWeather(id); cfg.markChanged();`
`id = null` means biome default (vanilla `WeatherResetCommand` passes null). `WeatherSystem$WorldAddedSystem` copies `getForcedWeather()` back into the resource when the world loads, so the lock survives unload and reload.
Choices (ids VERIFIED in `Server/Weathers/`): Biome default, Clear `Zone1_Sunny`, Fireflies `Zone1_Sunny_Fireflies`, Cloudy `Zone1_Cloudy_Medium`, Fog `Zone1_Foggy_Light`, Snow `Zone3_Snow`, Northern Lights `Zone3_Northern_Lights`, Skylands `Skylands_Sunny` (no environment uses the Skylands weathers, so the lock is the only way to see them on a sky island).
**Excluded:** `Zone1_Rain`, `Zone1_Rain_Light`, `Zone1_Storm`, `Zone3_Rain`. `Server/Farming/Modifiers/Water.json` lists them as watering weathers (x2.5 growth), and `WaterGrowthModifierAsset.checkIfRaining` reads `WeatherResource.getForcedWeatherIndex()` (bytecode). A locked rain would be a permanent farm boost.

### 4.6 Visitor landing point (Hypixel `/guestlocation`)
"Set to where I stand" works only while the owner stands on their own island world. It stores `visit.spawn=x,y,z,rx,ry,rz` (same as `hub.properties`). In `IslandCmd.go()` for a non-member visitor, call `InstancesPlugin.teleportPlayerToLoadingInstance(ref, store, future, ret, spawnTransform)`. The 5-arg overload is VERIFIED; for an already loaded world, `future = CompletableFuture.completedFuture(w)` (UNVERIFIED in game; fallback = keep today's `teleportPlayerToInstance` and follow it with a `Teleport` component to the point). Co-op always lands at the island spawn.

### 4.7 Visit ping
On a visitor's arrival, if `visit.notify=1`: message the owner (`Universe.get().getPlayer(ownerUuid)`, VERIFIED) and online co-op members (`[Island] Steve is visiting your island. /island settings to expel or ban.`). Throttle: one ping per visitor per 60 s.

### 4.8 Later (with the reason)
- **Time lock (always day or night).** APIs VERIFIED: `WorldTimeResource.setDayTime(hour/24.0, world, store)` + `WorldConfig.setGameTimePaused(true)` + `markChanged()`, the vanilla `/time` + `/pausetime` pattern. **But** `FarmingSystems$Ticking` (soil, coops), `BenchSystems$ProcessingBenchTick` (furnaces) and `WaterGrowthModifierAsset` read `WorldTimeResource.getGameTime()` (bytecode). Pausing probably freezes furnaces, crops and coops on that island. The alternative, a night skip (`setDayTime` always moves time *forward*, bytecode), speeds them up like sleeping in a bed would. Skyy picks one: "Always day (skips nights, same as sleeping)" or no time lock. Day *length* has no live setter (`get*DurationSecondsOverride` are getter-only), so it is **not possible**.
- **Visits while the owner is offline, island warps list, "visit a random public island".** `/island visit` takes `PLAYER_REF` (online only). An offline-name lookup exists (`ArgTypes.GAME_PROFILE_LOOKUP`, used by vanilla `/ban`), but it is a network lookup; test before use. Co-op members get a "Go" button to islands they belong to even when the owner is offline (section 6.5), so co-op does not need this.
- **Visitor keep-inventory / invincible visitors** (BentoBox). `WorldConfig.setDeathConfigOverride(MutableDeathConfig)` with `ItemsLossMode.NONE` exists (VERIFIED), but it applies to the whole world, owner included, and it touches the death-penalty design. That is an admin decision.
- **Split animal and monster spawning, leaf decay, crop growth toggles.** No engine switch; spawning is one boolean.
- **Party / guild visit sources** (Hypixel "Visits: Friends/Guild"). SkyyParty publishes no bridge key today; guilds are not built yet.
- **Fire spread.** `setDisabledFluidTickers(Set)` exists, but `"Fire"` resolution is UNVERIFIED and fire is rare on islands.
- **Custom roles, per-player overrides** (SuperiorSkyblock2/Hypixel), **admin `/island admin settings <player>`**, **island size border** (belongs with the size-tier upgrades), **BentoBox Basic/Expert view** (14 flags fit on one page, so no density toggle is needed).

---

## 5. Defaults and migration

**A new island starts with:** Public visits, limit 5, visit ping on, no landing point, PvP off, spawning off, biome Void Sky, weather biome default. Flags as in 3.2. Visitors may walk around, open doors, sit and fight hostile mobs. They may **not** place, break, open chests, benches or furnaces, sleep, harvest, touch animals, pick up or drop items, or use other blocks. Trusted may build, break, craft, sleep, harvest, pick up, drop and use other blocks, but not chests, furnaces or animals. Co-op may do everything.

**All defaults live in `Skyy_SkyyIslands/config.properties`** (`defaults.perm.<id>=`, `defaults.visit.mode=` ...). It is written with these values on first run, the SkyySkills `xp.properties` pattern. A key missing from an island file means "use the config default". So a server builder can fix a bad default for every island that never touched that setting, which is BentoBox's "Island Defaults" tab done as a file.

**Migration of 0.4.4 islands (no code migration needed):**
- An island file without `settings=1` simply reads config defaults. Nothing is written until the owner changes something.
- The defaults equal 0.4.4 behaviour for visitors and co-op, with **three deliberate changes**, listed in the in-game changelog line:
  1. `seats` is visitor-allowed (0.4.4 blocked sitting).
  2. `animals` is co-op only (0.4.4 did not guard hurting animals).
  3. `drop` is trusted+ (0.4.4 did not guard drops). Without this, visitors whose pickups are blocked lose what they drop.
- `members=` entries written by 0.4.4 are bare UUIDs, which **are** each player's profile-1 key. They keep matching on profile 1 with no rewrite. New invites store `pkey(target)`. SkyyProfiles is not live yet (HANDOFF section 3), so in practice nobody loses access.
- The world `config.json` of old islands already has `IsPvpEnabled: false`, `IsSpawningNPC: false` and the Void environment. Nothing to change.
- Nobody is Trusted or Banned after the upgrade.

---

## 6. UI and commands

### 6.1 Page frame (inline only; SkyyProfiles `ProfilePage` / SkyyTrees pattern)
- Class `IslandSettingsPage extends com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage`, constructor `super(pr, CustomPageLifetime.CanDismiss)`, `public void build(Ref, UICommandBuilder, UIEventBuilder, Store)`, `public void handleDataEvent(Ref, Store, String)`. Opened with `player.getPageManager().openCustomPage(ref, store, page)`.
- Root: `Group #SkyyIsSet { Anchor: (Width: 1100, Height: 720); Background: #0b1524(0.96); Padding: (Horizontal: 18, Vertical: 12); LayoutMode: Top; }`. Only Width/Height in the root anchor. **Big and readable:** title FontSize 20, row labels 15 bold, hints 11, buttons 36-56 px tall.
- Header: `Island Settings` + profile label (`IslandStore.profileLabel`) + `Your island - only you can change these`.
- **Tab row:** four `TextButton`s, 250x42: `#SkyyIsTabPerm` "Permissions", `#SkyyIsTabVis` "Visitors", `#SkyyIsTabIsl` "Island", `#SkyyIsTabMem` "Members". Payloads `tabperm`, `tabvis`, `tabisl`, `tabmem`. The active tab uses the gold style.
- Body `#SkyyIsBody` (Height 560). Footer: `Label #SkyyIsInfo` (status line) and `TextButton #SkyyIsClose`.
- **Rules (HANDOFF section 2):**
  - No underscores in ids (`#SkyyIsPc03v`, never `#Skyy_Is`).
  - Every click is `ev.addEventBinding(CustomUIEventBindingType.Activating, "#Id", EventData.of("a", "payload"))`, matched in `handleDataEvent` with `data.indexOf("payload\"")`. Payloads are letters and digits only.
  - Every click ends in `rebuild()`. No MouseEntered/MouseExited handlers, no timers, no periodic updates (lists refresh on click or the `Refresh` button).
  - Never close the page right before opening another. "Go" buttons close the page and then teleport, which is fine.
  - Names pass through the `safe()` sanitiser (SkyyProfiles).
  - Destructive buttons (Ban, Kick, Reset) take two clicks: the first turns the button into `Confirm?` (page field `confirm`), the second acts.

### 6.2 Permissions tab (the grid)
- Header row: `What` (420 px) | `Visitor` | `Trusted` | `Co-op` | `Owner` (150 px each).
- 14 rows x 36 px. The left cell stacks the label (15 bold) over its hint (11). Cells are `TextButton #SkyyIsPc<nn><r>` (`nn` = 00..13, `r` = v/t/m), text `YES` (green `#2f6a3a`) or `NO` (red `#6a2f2f`), payload `pc<nn><r>`. The Owner column is a grey label `always`.
- The click rule is 3.1.
- Top right: `Reset to defaults` (`#SkyyIsReset`, confirm) and a legend line: "Click to allow or deny. Allowing a role also allows every role to its right."

### 6.3 Visitors tab
- "Who may visit": three 320x56 buttons `#SkyyIsVm0` Public (anyone), `#SkyyIsVm1` Friends only (co-op + trusted), `#SkyyIsVm2` Closed (co-op only). Payloads `vm0`, `vm1`, `vm2`. Closing expels at once (4.1).
- Visitor limit: `#SkyyIsVlm` [-], a label with N, `#SkyyIsVlp` [+], range 1..limitMax.
- Visit ping: toggle `#SkyyIsVn`.
- Landing point: `#SkyyIsVs1` "Set to where I stand" (greyed with an info line when you are not on your island) and `#SkyyIsVs0` "Use island spawn".
- "On your island now": up to 8 rows (name, role) with `#SkyyIsVe<n>` Expel, `#SkyyIsVt<n>` Trust, `#SkyyIsVb<n>` Ban (confirm). The page keeps the snapshot of UUIDs taken at build time. `#SkyyIsVr` Refresh.
- "Banned": up to 8 names with `#SkyyIsVu<n>` Unban, plus `#SkyyIsBp`/`#SkyyIsBn` paging.

### 6.4 Island tab
- **Biome:** 11 cards in 2 rows. Each card is a 36x36 swatch `Group` (`Background: #rrggbb`) plus a 140x36 `TextButton #SkyyIsBi<nn>`; the current biome is highlighted, payload `bi<nn>`. Hint: "Changes grass colour, sky and weather, water colour, ambient sound and wildlife (when mob spawning is on). 60 s cooldown."
- **PvP:** toggle `#SkyyIsIp`, hint "Turning PvP on sends visitors to the hub".
- **Mob spawning:** toggle `#SkyyIsIs`, hint "Needs a biome with wildlife - Void Sky has none".
- **Weather:** cycle button `#SkyyIsIw` showing the current choice, hint "Rain and storms can't be locked (they water crops)".

### 6.5 Members tab
- "Co-op (max 5)": name + `#SkyyIsMk<n>` Kick (confirm).
- "Trusted (max 20)": two columns, name + `#SkyyIsMu<n>` Untrust.
- "Islands you are co-op on": owner name + `#SkyyIsMg<n>` Go. It closes the page and runs `IslandCmd.go(store, ref, pr, world, ownerKey, false)`, which loads unloaded islands via `Universe.addWorld` (0.4.4), so it works while the owner is offline. Source: a `MEMBER_OF` index (member pkey → island keys) built in `loadIslandWorlds()` and kept current by `addMember` / `kick`.
- A help box explains the command equivalents.

### 6.6 Commands (all subcommands of `/island`, each an `AbstractPlayerCommand` with `setPermissionGroups(new String[] { "hytale:Adventurer" })`)
Required arguments only, because optional args are flags and not positional. Constructors are added before the `IslandCmd` constructor that calls `addSubCommand(new ...)` (javassist order, as in 0.4.4). Names typed as text (`STRING`) are matched case-insensitively against the island's stored `name.<key>` entries; a 36-char UUID also works. That is how an offline player can be unbanned, untrusted or kicked without a network lookup.

| Command | Args | Who | Does |
|---|---|---|---|
| `/island settings` (alias `options`) | none | owner of the active island | opens the page |
| `/island expel <player>` | `PLAYER_REF` | owner or co-op of the island you stand on (else your own island) | target must be inside with rank < co-op → hub + 60 s block |
| `/island ban <player>` | `PLAYER_REF` | owner | refuses co-op ("kick first") and yourself; removes trust; expels |
| `/island unban <name>` | `STRING` | owner | removes from the ban list |
| `/island bans` (alias `banlist`) | none | owner | lists bans in chat |
| `/island trust <player>` | `PLAYER_REF` | owner | refuses banned, co-op and yourself; max 20 |
| `/island untrust <name>` | `STRING` | owner | |
| `/island kick <name>` (alias `remove`) | `STRING` | owner | removes a co-op member; expels them when inside and Closed |
| `/island lock` | none | owner | mode → Closed (saves the previous mode) + sweep |
| `/island unlock` | none | owner | mode → saved previous mode (default Public) |

Unchanged: `/island`, `info`, `home` (`go`), `visit <player>` (`warp`, now with the entry check and landing point), `invite <player>` (`add`, now stores `pkey(target)`, capped at `coop.max`), `/hub`, `/sethub`. The old `--action` flag form keeps working. The `/island` root description lists the new subcommands.

---

## 7. Storage (per island = per profile) and bridge keys

### 7.1 `Skyy_SkyyIslands/islands/<pkey>.properties` (0.4.4 keys `world`, `created`, `kit`, `members` stay)
```
settings=1                               # written on the first change; absent = pure config defaults
members=<pkey>,<pkey>                    # co-op (bare UUID = that player's profile 1)
trusted=<pkey>,...
banned=<uuid>,...
name.<pkey or uuid>=Steve                # display names, refreshed whenever the player is seen
ownerName=Skyy
perm.build=trusted                       # one per flag id; values visitor|trusted|member|owner
visit.mode=public                        # public|friends|closed
visit.prev=public                        # restored by /island unlock
visit.limit=5
visit.notify=1
visit.spawn=8.5,129.0,8.5,0,0,0          # absent = island SpawnProvider
pvp=0
spawning=0
biome=void
biome.changed=<millis>                   # cooldown
weather=                                 # empty = biome default, else a preset key (clear, fireflies, cloudy, fog, snow, aurora, skylands)
```
- The file stays per profile (`IslandStore.read/write(key)`, atomic tmp+move, 0.4.4).
- **New cache:** `IslandStore.SETTINGS` (ConcurrentHashMap, pkey → parsed `IslandSettings`: `int[] perm`, `int mode`, the lists as comma strings, and so on). `write()` refreshes the entry. Guards and bridge calls read only the cache. This matters because 0.4.4 `isMember` reads the file from disk on every guarded event, and 0.5 adds hurt/use-entity/drop events.
- Rank lookup: `IslandPerms.rank(String ownerKey, UUID who)` returns -1 banned, 3 when `pkey(who)` equals ownerKey, 2 when it is in members, 1 when trusted, else 0.

### 7.2 `Skyy_SkyyIslands/config.properties` (admin, new)
```
defaults.perm.build=trusted ... (all 14)
defaults.visit.mode=public
defaults.visit.limit=5
visit.limitMax=10
coop.max=5
trusted.max=20
bans.max=100
expel.cooldownSeconds=60
biomes=void,plains,forest,autumn,azure,swamp,savanna,oasis,tundra,glacial,wastes
biome.cost=0
biome.cooldownSeconds=60
biome.radiusChunks=4
weathers=clear,fireflies,cloudy,fog,snow,aurora,skylands
animals.extra=                            # extra NPC role names that count as farm animals (pet mods)
```

### 7.3 Bridge (`System.getProperties().get("skyy.bridge")`, UUID-keyed per contract rule 3; Functions are plain classes, no lambdas)
| Key | Value | Use |
|---|---|---|
| `island:<uuid>` | world name of the active profile's island (0.4.4) | unchanged |
| `island:perm:fn` | `Function` apply(`Object[] { UUID player, String worldName, String flag }`) → `Boolean`, or `null` when the world is not an island or the flag is unknown. Flags: the 14 ids + `enter` + `settings`. Admins → TRUE. | "may this player do X here" |
| `island:role:fn` | `Function` apply(`Object[] { UUID, String worldName }`) → `"owner" | "member" | "trusted" | "visitor" | "banned"` or null | HUD label, other mods |
| `island:owner:fn` | `Function` apply(`String worldName`) → owner pkey String (the owner UUID = first 36 chars) or null | |
| `island:epoch` | `Long`, +1 on every settings change of any island | cache invalidation for other mods |

Follow-ups for other mods (each its own build, none needed for 0.5 to work):
- SkyyEssentials 0.1.1: `/tpa` and `/tpahere` into an island world ask `enter` before teleporting. Until then the arrival check and sweep expel within about 5 s.
- SkyyMenu: an "Island settings" button that dispatches `/island settings`.
- SkyyMinions (future): asks `containers`.
- SkyyHud (later): shows "Visiting X - PvP off" from `island:role:fn`.

---

## 8. Anti-exploit and edge cases

1. **Co-op on another profile = visitor.** Membership is a pkey, so a co-op member who switches profile loses co-op rights on that island, exactly like the owner on their own other profile (0.4.4 rule). This closes the cross-profile item-transfer route: put items in a shared chest on profile A, switch, take them out on profile B. Messages say "switch to profile X".
2. **Owner on another profile** is a visitor (0.4.4). In 0.5 the drop flag is also **hard-denied** for them whatever the grid says, so they can't drop items on their own island from profile B and pick them up on profile A. (Dropping in the hub and switching profile is a general SkyyProfiles question, flagged there, not solved here.)
3. **Breaking a container/furnace needs break AND containers/processing** (3.3 extra rule), because breaking drops contents.
4. **Visitors inside when settings change:** Closed/Friends/ban → immediate sweep and expel. PvP on → visitors expelled. A lower limit only affects new arrivals. Flag changes apply on the next event (cache). Biome and weather apply at once on a loaded island, else on the next load.
5. **Other ways in** (`/tpa`, vanilla `/teleport`, a respawn, logging in on the island): the arrival check on every `PlayerReadyEvent`, plus the 5 s sweep. Login inside an island still routes to the hub first (0.2).
6. **Offline owners:** settings and guards come from the file and cache, so nothing needs the owner online. Visiting a player needs them online (0.4.4 `PLAYER_REF`); co-op members use "Go" on the Members tab. WorldConfig values (PvP, spawning, weather, worldgen biome) persist in the island's own `config.json` via `markChanged()`. The arrival hook re-applies them idempotently in case the island was unloaded while they changed.
7. **Expel is temporary** (60 s block, memory only). **Ban** is persistent and per person (UUID, all profiles). You can't ban co-op (kick first) or yourself, and banning removes trust.
8. **Admins** bypass everything and are never expelled. The sweep skips them.
9. **Farming boosts:** rain can't be locked (x2.5 growth) and time lock is deferred (freeze vs speed-up).
10. **Biome spam:** 60 s cooldown and an optional coin cost. Only loaded chunks within R change; the rest are fixed on arrival.
11. **Visitor deaths:** pickup is denied to visitors, so if a visitor dies on the island surface their drops stay with the island. PvP is off by default, hostile mobs exist only if spawning is on, and void deaths lose items anyway (0.4). Documented; visitor keep-inventory is "later".
12. **Milking and shearing** can't be guarded (no event). Pets from third-party mods count as hostile unless listed in `animals.extra`.
13. **Third-party remote-storage mods** (installed but not in our pack, e.g. AutoStorage, whose `ClaimProtectionProvider` only knows SimpleClaims) could bypass the container guard. The SkyWynn pack should not ship them without an `island:perm:fn` compat.
14. **Profile switch while standing on an island:** rank is resolved live (`pkey`); the sweep re-checks within 5 s.
15. **Race at the visitor limit:** give or take one. Acceptable.
16. **Names:** `name.<key>` is refreshed whenever the player is seen, so renamed players show their new name. STRING commands match any stored name.
17. **Performance:** guards read the cache (7.1). The sweep touches only loaded islands with players. The biome apply is about 80k cheap calls, once per change.

---

## 9. In-game test checklist (append to TEST-CHECKLIST.md when built; 2 accounts: A = owner, B = other player; C optional)

1. Deploy only with Skyy's OK (never `--deploy` from this spec). The server log shows `SkyyIslands 0.5 ready`, no "already registered" and no guard errors on first join.
2. **Migration:** an island made by 0.4.4. B visits: doors and **sitting** work. Chest, furnace, workbench, bed, lantern, crop F-harvest, punching a crop, place, break, pickup and **drop** are refused, each with a message naming the rule. Hitting a cow is refused; hitting a hostile mob works.
3. `/island settings` opens a big page with all 4 tabs; each tab switch rebuilds without a client error.
4. **Grid:** A sets Chests → Visitor YES. B can open the chest. Set it back → refused again. Clicking Co-op NO makes that flag owner-only (a co-op test account is refused).
5. **Trust:** `/island trust B`. B builds, breaks, crafts, harvests and sleeps, but can't open the chest or furnace, and can't **break** the chest (anti-loot rule). `/island untrust B` → visitor again.
6. **Co-op:** `/island invite B`. B does everything. `/island kick B` → visitor. (With SkyyProfiles: B on profile 2 is a visitor.)
7. **Visitors mode:** Friends → B (not trusted) is refused at `/island visit`. If B is inside (via `/tpa`), they are sent to the hub within about 5 s. Closed, `/island lock` and `/island unlock` restore the previous mode.
8. **Limit:** limit 1, B inside → C is refused ("island is full").
9. **Expel:** `/island expel B` → B lands in the hub. B tries again within 60 s → refused; after 60 s → allowed.
10. **Ban:** `/island ban B` while B is inside → hub; B is refused at visit and via tpa. B logs off; `/island unban <B's name>` works offline. `/island bans` lists them.
11. **PvP:** on → visitor B is expelled with a message; A and a co-op member can hit each other; off again → no damage.
12. **Spawning + biome:** Void Sky + spawning on → nothing spawns. Plains + spawning on → animals appear by day, wolves and void larvae at night. Off → no new spawns.
13. **Biome:** pick Autumn. The grass turns orange-brown **without** re-entering (if not: note it, re-enter, confirm the fallback). Sky, weather and ambience change, water tint changes. Restart the server → still Autumn. Build out to a new chunk far away → it is Autumn too. A second change within 60 s → cooldown message.
14. **Weather:** Snow → it snows on the island only (the hub unchanged). Biome default → normal. Restart → the lock persists. Rain is not offered.
15. **Landing point:** set it; B visits and lands there; co-op lands at the island spawn.
16. **Visit ping:** A (anywhere) gets "B is visiting your island".
17. **Members tab Go:** A logs off; co-op B clicks Go → the island loads and B arrives.
18. **Bridge:** from any mod or `/rolls`-style debug: `island:perm:fn` for B on A's island with `containers` → FALSE, then TRUE after the grid change.
19. **Persistence:** restart; all settings, lists and WorldConfig values are unchanged; `islands/<pkey>.properties` shows `settings=1` and only the changed keys.

---

## 10. Build notes and sources

**Build (one version, about +1,400 lines in `build_skyyislands_0.5.py`, copied from 0.4.4):**
- Class order for javassist (a method before its callers): IslandSettings → IslandStore additions (cache, MEMBER_OF, lists, names) → IslandPerms (constants, classifier, rank, `mayEnter`) → GuardSystem rework + GuardUse/Break/Damage/Place/Pickup → GuardDrop, GuardUseEntity, GuardHurt → ExpelTask / ArrivalTask / SweepTask → BiomeApply / WorldApply (PvP, spawning, weather) → PermFn, RoleFn, OwnerFn → IslandSettingsPage → 10 subcommand classes → IslandCmd constructor → plugin setup.
- Plugin setup adds one `registerSystem` each for GuardDrop, GuardUseEntity and GuardHurt, puts the 3 bridge functions, and writes `config.properties` defaults.
- The script reads `Assets.zip` at build time (Python zipfile, read-only, in memory) for the animal role list.
- Add `B.probe` lines for every new engine call listed in sections 3-4.
- javassist limits hold throughout: no lambdas, generics, varargs, autoboxing (`Boolean.valueOf`, `Long.valueOf`), enhanced-for, inner classes (all helpers are top-level), String switch (if/else on int ids), try-with-resources. Synchronized blocks hold a single call. f-string braces doubled.

**Engine evidence (all VERIFIED this session):**
- Engine protection rules: `TriggerVolumeRuleSystems$NoDoorOpen/NoHarvestUse/NoUseBlock/NoUseEntity/NoBuild/NoDestroyBlockBreak/NoDestroyBlockDamage/DamageRuleFilter`.
- Event dispatch: `UseBlockInteraction.doInteraction`, `UseEntityInteraction.firstRun`, `BlockHarvestUtils.performBlockBreak/performPickupByInteraction`, `InventoryPacketHandler` (DropItemEvent$PlayerRequest), `ContextualUseNPCInteraction` (no event).
- `BlockType` getBench/getBeds/getSeats/getFarming/getGathering/getInteractions/isDoor/processConfig; `Bench.getType()`, `BenchType`.
- Damage: `Damage`, `Damage$EntitySource`, `Damage$ProjectileSource`, `DamageModule.getFilterDamageGroup`, `NPCEntity.getRoleName`.
- World settings: `WorldConfig` setters + `markChanged` + `WorldConfigSaveSystem`; vanilla `WorldConfigSetPvpCommand`, `SpawnCommand$DisableCommand`, `WeatherSetCommand/WeatherResetCommand`, `WeatherSystem$WorldAddedSystem`, `TimeCommand`, `WorldConfigPauseTimeCommand`, `WorldTimeResource.setDayTime`.
- Biome calls: `BlockChunk.setTint/setEnvironment/getEnvironmentChunk`, `EnvironmentChunk.setColumn`, `WorldNotificationHandler.updateChunkTints/updateChunkEnvironments` (used by `ChunkTintCommand` and `BuilderToolsPlugin$BuilderState.environment`), `Environment.getAssetMap().getIndex` (`EnvironmentCommand`), `VoidWorldGenProvider(Color, String)`.
- Other: `World.getPlayerRefs` (concurrent), `Universe.getPlayer(UUID)`, `InstancesPlugin.teleportPlayerToLoadingInstance` 5-arg, `ArgTypes.GAME_PROFILE_LOOKUP` (vanilla ban/unban).
- Farming time and rain: `FarmingSystems$Ticking`, `BenchSystems$ProcessingBenchTick`, `WaterGrowthModifierAsset.checkIfRaining`.
- Assets: `Server/Environments/*` (122), `Server/Weathers/*` (87), `Server/NPC/Spawn/World/*` (96), `Server/Audio/AmbienceFX/*` (48 keyed on EnvironmentIds), `Server/World/Default/Zones/*/Tile.*.json` tints, `Server/Farming/Modifiers/Water.json`, `Server/Item/Unarmed/Interactions/Empty.json`, every `Server/Item/Items/**` BlockType.
- Installed mod (read-only): `Aetherhaven-3.1.3.jar` `TownTerritoryGuard.classifyUseBlock/isHarvestStyleBreak`, `TownMemberPermissions`, `TownMemberPermissionsPage`.

**Web sources (summarised in my own words in section 1):**
- BentoBox: https://docs.bentobox.world/en/latest/BentoBox/Island-Protection,-Flags-%26-Ranks/ · https://docs.bentobox.world/en/latest/BentoBox/Flags/ · https://docs.bentobox.world/en/latest/BentoBox/About/Teams/ · https://docs.bentobox.world/en/latest/gamemodes/BSkyBlock/Commands/ · https://docs.bentobox.world/en/latest/addons/Visit/ · https://docs.bentobox.world/en/latest/addons/Biomes/ · https://github.com/BentoBoxWorld/BentoBox/blob/develop/src/main/java/world/bentobox/bentobox/lists/Flags.java
- SuperiorSkyblock2: https://wiki.bg-software.com/superiorskyblock/overview/island-privileges · https://wiki.bg-software.com/superiorskyblock/overview/island-flags · https://wiki.bg-software.com/superiorskyblock/overview/menus · https://wiki.bg-software.com/superiorskyblock/overview/commands-and-permissions/player-commands · https://github.com/BG-Software-LLC/SuperiorSkyblock2/issues/2412
- IridiumSkyblock: https://iridium-development.gitbook.io/iridiumskyblock/general/features · https://iridium-development.gitbook.io/iridiumskyblock/general/permissions
- ASkyBlock: https://github.com/tastybento/askyblock/wiki/Permissions
- Hypixel SkyBlock (wiki mirrors): https://hypixelskyblock.minecraft.wiki/w/Private_Island · https://hypixelskyblock.minecraft.wiki/w/Settings · https://hypixelskyblock.minecraft.wiki/w/Guests_Management · https://hypixel-skyblock.fandom.com/wiki/Co-op
