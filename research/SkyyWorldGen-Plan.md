# SkyyWorldGen: plan (World Gen V2 zone islands) - 2026-10-01

Research and plan only. Skyy said "dont build yet, just make a plan", so nothing here is built, packed or deployed. Every number is a
**PLACEHOLDER** until Skyy picks it (section 8 has the questions). Skyy uses they/them.

Input: the two read-only research briefs of 2026-10-01 (web, and engine: release 0.6 and 0.7.0-pre `Assets.zip` + `HytaleServer.jar`,
plus the World Gen V2 mods installed in `UserData/Mods`). Re-checked for this plan, release only: `Server/HytaleGenerator/WorldStructures/Portals_Oasis.json`
and `Density/Map_Portals.json` (a warped `Distance` island with void around it already ships in **release**), and the vanilla
`Server/Instances/Regions/Zone1_Plains1..Zone4_Volcanic1` instances. The plan has to fit these locks and plans:
SkyWynn-Decisions.md (batch 1 #2, change notes 2026-09-24 #4, row 7.1), SkyyIslands-Plan.md, DESIGN-STATUS.md open question 12,
research/Mob-Levels-Plan.md + Mob-Levels-Research.md, research/Gear-Levels-Wynn-Spec.md, SkyyExploration-Plan.md, and the pacing answer
in OPEN-QUESTIONS.md (2026-10-01: flatten the class skill curve).

*Reviewed 2026-10-01 by a critic + editor pass (engine facts re-read from `Assets.zip` and `HytaleServer.jar`, read only). Section 9 lists
every correction and what was proved offline.* **Legend:** VERIFIED = seen in the release `Assets.zip` / jar bytecode / an installed mod
file. INFERRED = likely, not proven. **UNVERIFIED** = web-only claim or cannot be proven offline (the stage 0 checks T1-T13 in 7.3 settle
what can be settled in game). Web-only claims (licences, contest placements, timings, 0.7 patch notes) are always UNVERIFIED here.

---

## 0. Plain words (for Skyy)

- **Yes, World Gen V2 can do this.** DESIGN-STATUS question 12 is answered. Hytale already ships the trick in the release game: the
  Oasis portal world is one round island with empty void around it, and the land type is picked by **distance from the centre**.
  That is exactly "easy outside, hard in the middle".
- **What V2 is:** a world generator made of JSON files ("node graphs", written by hand or with the in-game node editor). A mod can ship its own set
  of these files. No game files are edited, and the terrain itself needs no Java.
- **The plan:** four floating islands, **one per Hytale zone**, and each one is **its own world** (that is how Hytale's own test
  zones are done). You land on the outer rim. Each ring you walk inward is the next "level" of the game (1-1, 1-2 ... 1-6), and each
  ring sits a little higher. The hardest biome is the summit in the middle, where the zone's guardian will live. Reach it (until bosses
  exist; then beat its guardian) and the next island unlocks. The hub stays the shared spawn (for solo play: question 2).
- **Every ring has a level range, and so does every biome in it** (a biome's range = its ring's range; section 4 lists them). The ranges
  plug into the mob level plan (Zone 1 = Lv 1-10, Zone 2 = 15-25, Zone 3 = 30-40, Zone 4 = 45-60) and into the gear bands (Wood 1-13,
  Copper 10-18, Iron 15-23 ... Mithril 40-49). The rings overlap by 1-2 levels, so the climb feels steady. The guardian sits in the
  gap between zones. The player-side number is the **class weapon skill** (the SkyyGear gate, Mob-Levels-Plan 7), not Overall Level
  (that is an average of 9 skills, Overall-Level-Spec).
- **Honest limit:** our own gear starts at Lv 50, so Zone 4's four inner rings (mobs Lv 50-60) have no better gear to find than the Lv 49
  cap. Zones 1-3 line up with gear; Zone 4 waits for our own tiers (question 3).
- **The catch:** V2 does not have Hytale's normal biome list yet. There is no blue forest, no autumn forest and no swamp in V2. We
  have to make V2 versions of them ourselves (same trees, same grass colours, same Hytale mobs). That is the real work.
- **Untouched:** the normal Hytale world (it stays the solo hub and wild world) and your private SkyyIslands islands.
- **Smallest proof first:** one small Zone 1 test island in a throwaway save, then the full Zone 1, then Zones 2-3, then Zone 4 (built but
  hidden until our own Lv 50+ gear exists).

---

## 1. How World Gen V2 works (short)

| Piece | What it does | Where (inside `Assets.zip`, read only) |
|---|---|---|
| Engine | Plugin `com.hypixel.hytale.builtin.hytalegenerator.plugin.HytaleGenerator` (998 class files, 785 top-level, VERIFIED). It registers the world-gen type `"HytaleGenerator"` (`HandleProvider`). V1, the normal world, is `com.hypixel.hytale.server.worldgen` (type `"Hytale"`, `"Name":"<folder under Server/World>"`) | `HytaleServer.jar` |
| Picking V2 | A world's `config.json` or an `instance.bson` (plain JSON) says `"WorldGen":{"Type":"HytaleGenerator","WorldStructure":"<id>","SeedOverride":"<text>"}`. Those are the only two fields (`HandleProvider.setWorldStructureName` / `setSeedOverride`; the default structure name is `Default`) | `Server/Instances/Regions/Zone1_Plains1/instance.bson` |
| WorldStructure | One type (`NoiseRange`, `BasicWorldStructureAsset`). One density map that the engine reads per column (vanilla maps wrap it in `YOverride 0`, so treat it as **2D**), plus a list `Biomes:[{Biome,Min,Max}]`: each biome owns a value range of that map. Also `DefaultBiome` (INFERRED: used for values no range covers; `Portals_Goblins` leaves 320-370 uncovered), `DefaultTransitionDistance` (blend width, 16-32 in vanilla files), `MaxBiomeEdgeDistance` (same value in every vanilla file), `SpawnPositions`, `Framework` (shared positions + Base/Water/Bedrock heights) | `Server/HytaleGenerator/WorldStructures/*` |
| Biome | `Name`, `Terrain` (`DAOTerrain` + a 3D density, positive = solid), `MaterialProvider` (blocks; the vanilla files mark the `Empty` material REQUIRED), `Props` (trees, rocks, prefabs; the `Assignments/` folder holds shared prop sets), `EnvironmentProvider` (only `Constant` and `DensityDelimited` exist; the environment id drives mobs, weather and sound), `TintProvider` (`Constant`, `DensityDelimited`, `Mix`) | `Server/HytaleGenerator/Biomes/*` |
| Density nodes | 81 asset types (VERIFIED by class list): `Distance`, `Anchor`, `Offset`, `Angle`, `PositionsCellNoise`, `SimplexNoise2D/3D`, `WhiteNoise`, `CurveMapper`, `Sum`/`Min`/`Max`/`Mix`, warps (`FastGradientWarp`, `GradientWarp`), `BaseHeight`, `YOverride`, `YSampled`, `Cache`, `Selector`/`Switch`, `Normalizer`, `Clamp`. There is **no image or bitmap node** | `Server/HytaleGenerator/Density/*` |
| Sharing | `"ExportAs":"X"` publishes a node (the `Exported` density has a global id); `{"Type":"Imported","Name":"X"}` reuses it. **One global namespace across all mods** (docs; consistent with `Exported` having an `Id` and with Welkin replacing vanilla files by name; what happens on a clash between two mods is UNVERIFIED) | everywhere |
| Tools | `/worldgen2` (`/wg2`): `create` (alias `editor`) = "Open the Biome Creator dialog"; `concurrency <low> <normal> <high>` = worker thread counts, resets on restart, 0 = default. `/viewport [radius] [--delete]` = a live worldgen preview around the player (radius in chunks; the command asks for the `hytale:WorldEditor` permission group). JSON files carry `$NodeEditorMetadata` / `$Position` keys from the node editor (which in-game tool opens it is UNVERIFIED). `/worldgenbenchmark` exists in the core but **V2 does not support it** (no V2 class references `IBenchmarkableWorldGen`, and the lang string says "doesn't support benchmarking"). A global `Settings/Settings.json` sets `StatsCheckpoints` (1/100/500/1000: timing lines in the log), the three concurrency values, `TargetViewDistance` 512 and `TargetPlayerCount` 3 | `server.lang` 1414-1423, 2556-2563; `Settings/Settings.json` |

Rules that shape this plan:
- **Biomes are chosen per column (x, z).** The map is 2D, so islands cannot be stacked. The island **shape** (floating, with an
  underside) comes from each biome's 3D `Terrain`. Vanilla example: `Biomes/Experimental/Islands_Roots.json` (BaseHeight + CurveMapper + Simplex).
- **Rings are native.** Release `Density/Map_Portals.json` exports `Biome-Map-Portals` (`SingleInstance: true`): `YOverride 0` ->
  `Cache` (capacity 1) -> `Sum` of three parts: Simplex noise (scaled to +-0.1), an inverted `PositionsCellNoise` (Manhattan
  Distance2Div, +-0.4) and a `FastGradientWarp` (WarpFactor **200**, WarpScale 250) of `Distance` through a manual curve (440 -> 1,
  460 -> 0.5, 480 -> 0.5, 490 -> 0.3, 510 -> 0.3, 530 -> -1, 540 -> -2), scaled to +-0.5. `Portals_Oasis.json` maps 0..2 =
  `Desert1_Oasis`, -0.1..0 = `Void_Buffer_Oasis`, -2..-0.1 = `Void`. So vanilla's island is lumpy (a 200-block warp on a radius of
  about 500); our rings use a much milder warp. The 0.7 Goblin shard is simpler: its density is just `YOverride 0` -> `Cache` ->
  `Distance` (a manual curve), and the biome ranges are in **blocks**: 0-320 main biome, 370-430 edge biome, 430+ `Void`
  (`Portals_Goblin_Biome_Distance.json`, 0.7 pre-release file; the `NoiseRange` type is the same in release).
- **`Distance` is origin-based and 3D (VERIFIED, bytecode).** `DistanceDensity.process` is `Calculator.distance(x, y, z, 0, 0, 0)`
  of the sample position, then the curve. That is why vanilla wraps it in `YOverride 0`. An island centred on the world origin needs
  no `Anchor`; an off-centre one does (`Anchor` / `Offset`). Only "is the sample position in world block coordinates" is left for T3.
- **No painted-map node.** The 81 density types include no image or bitmap node (VERIFIED). Hand-drawn layouts must be built from shapes
  (positions lists, cells, ellipsoids) or a custom Java density type (engine-internal, untested).
- **Height is 320 blocks, y 0-319** (`ChunkUtil.HEIGHT` 320, `MIN_Y` 0; VERIFIED). Entities below y -32 die (`ChunkUtil.MIN_ENTITY_Y` -32,
  VERIFIED; SkyyIslands-Plan.md 0.4 note).
- **Mobs follow the environment**, not the biome: `Server/NPC/Spawn/World/**` files list `"Environments":[...]` with mob ids and
  weights (`WorldNPCSpawn`, `WorldSpawnManager`; VERIFIED). Vanilla already tiers them: `Wander_Zone1_Tier1` = `Env_Zone1_Plains`
  (Skeleton_Fighter), `Tier2` = Forests / Mountains / Autumn (+ Burnt_Praetorian_Wander), `Tier3` = Swamps / Azure (+ Skeleton_Mage,
  Burnt_Praetorian). Rules spawn on a `SpawnBlockSet` (`Soil` in these files). There is **no level** in spawn data: levels are our
  SkyyMobs layer.
- **V2 worlds have no zone or biome data at runtime (INFERRED).** `getZoneBiomeResultAt` is only called from V1 classes
  (`ChunkGenerator`, `BiomeDataSystem`, the locate and memories code) and V2 has no zone concept. So expect no vanilla zone discovery
  banner, no zone name on the compass, `/locate` and `/player zone` empty (stage 0 T9). What is saved is the **environment per
  block** (`BlockChunk.getEnvironment(int,int,int)`, `NPCEntity.getEnvironment()`).
- **Vanilla's release V2 biome roster is a small prototype set**: Plains1 (Oak, Gorges, Mountains, River, Shore, Deeproot), Desert1,
  Taiga1, Boreal1 (Hedera, Henges), Volcanic1, `Oceans`, plus `Experimental/`, `Examples/` and `Generative/` files. It changes between
  versions: 0.7 removes `Plains1_Deeproot`, 5 `Generative_*` biomes and `Test_Graph`, and adds `Forests1_Oak` and the Goblin portal
  biomes (release has no `Forests1_Oak`). The blue forest exists only as the V1 tile `Zone1_Tier3/Tile.Forest_Azure.json` (tint
  #2F798A / #2F868A) and the environment asset `Env_Zone1_Azure`; no V2 biome uses it. **We do not import vanilla V2 biome or export
  names.**

---

## 2. World shape

### 2.1 One world per island (recommended) vs one shared world

| | **One world per zone island (recommended)** | One world with four islands |
|---|---|---|
| Vanilla precedent | Yes: `Instances/Regions/Zone1_Plains1` ... `Zone4_Volcanic1` and every `Portals_*` world | None |
| Ring maths | Island centred at (0, 0): one `Distance` curve. `Distance` is origin-based (VERIFIED, section 1 rules) | Needs an offset per island (`Offset`/`Anchor`, or `Selector` over a positions list); clunky |
| Gating | Cheap: only our `/zone` and the menu open the world. Other teleports (vanilla `/tp`, warps, other mods) can still enter it unless we also guard `AddPlayerToWorldEvent` (risk 7.2, T11) | Players could fly or bridge across the void; needs a fence |
| Levels and loot | Ring maths per world (`wg:fn:ring`), plus a `loot.level.world.<world>` fallback per world name. **Leave SkyyMobs `bands.world` empty for these worlds**: it is lookup step 2 and would outrank the ring step (5.2) | One table with island offsets |
| Shared constants | Each island gets its own Base height, sky, weather and size | Base height is shared world-wide |
| Cost | Only the world a player is in generates and ticks; empty worlds unload (`WorldEmpty`) | One big world, all islands in one save |
| Loses | You cannot see the next island from this one (fine: lore says the void split the world) | |
| Shared state | Everything in a shared world is shared: looted chests, mined ore, felled trees and placed blocks stay changed for the next profile or player (risk 7.2) | Same, in one save |

World names `skywynn_z1` .. `skywynn_z4`. Instance templates `Server/Instances/SkyWynn_Zone1` .. `SkyWynn_Zone4` inside the
SkyyWorldGen jar (the same layout SkyyIslands uses for `Server/Instances/SkyyIsland`). The worlds are **shared**: one per save (or
per server), not per profile (the locked rule: shared worlds, SkyyExploration Q9). Unlock progress is per profile. The vanilla instance files
of the same kind (`Zone1_Plains1/instance.bson`) also set `GameMode` Adventure, `IsSpawningNPC` true, `IsSpawnMarkersEnabled` true and
`DeleteOnRemove` false: copy those keys into our templates.

### 2.2 Size and void

Island radius R (the edge of the land), PLACEHOLDER, chosen once per world from a size preset (a default, section 8):

| Island | R (medium) | Land area | Rim -> centre in a straight line, running at 5.5 blocks/s (sprint 7.0) |
|---|---|---|---|
| Zone 1 Emerald Wilds | 640 | about 1,260 chunks (32 x 32) | 116 s, about 1.9 min (sprint 1.5) |
| Zone 2 Howling Sands | 704 | about 1,520 | 128 s, about 2.1 min (sprint 1.7) |
| Zone 3 Whisperfrost Frontiers | 768 | about 1,810 | 140 s, about 2.3 min (sprint 1.8) |
| Zone 4 Devastated Lands | 832 | about 2,120 | 151 s, about 2.5 min (sprint 2.0) |

Speeds: `Server/Entity/MovementConfig/Default.json` BaseSpeed 5.5, run x1.0, sprint x1.273 (VERIFIED). Terrace climbs and detours make
real trips longer. For scale: the vanilla Goblin shard is r about 430 (0.7 file), the Oasis island about 440-530. Small preset = 0.6 x R,
large = 1.6 x R.
Beyond R: a thin cliff edge (16 blocks of `SkyWynn_Edge` biome) and then our own `SkyWynn_Void` biome (Constant 0 terrain, empty
material) to the end of the world. Void columns still run every stage, but they are cheap. Stage 4 option: a few tiny floating
islets in the void band (R to R+200) for Echo Shards and secrets (SkyyExploration C1).

Heights (PLACEHOLDER): rim top y about 150, each ring inward one terrace (+10 to +14) higher, the summit up to about y 240.
The underside tapers from about y 60 under the centre to nothing at the rim. Falling off means the void kill at y -32, which is the
coin-loss death (10-25%) that the half-shards Echo Shard accessory protects against. The lore fits. Two guards: put the `SpawnProvider` Y
well above the ground (vanilla `Zone1_Plains1` spawns at Y 200 over terrain below it), and give the rim a low lip or boulder ring, because
the rim is where Lv 1-2 players fight and knockback would otherwise drop them into the void.

### 2.3 Travel and unlock (fits the locked chain + hub)

| Step | How |
|---|---|
| Go to an island | `/zone` (UNVERIFIED free: vanilla only has `/player zone` and `/locate zone`; other mods unchecked) opens a list of unlocked islands; a SkyyMenu tile "Zone Islands" does the same. Later: a gate in the hub (vanilla `Instance_Gateway` block or a `PortalTypes/*.json` + `Portal_Device`, both configurable) |
| First visit | `InstancesPlugin.spawnInstance("SkyWynn_Zone1", "skywynn_z1", fromWorld, transform)` copies the template and generates. Persist with `setDeleteOnRemove(false)` + `setDeleteOnUniverseStart(false)`; reopen later with `Universe.addWorld(name)`, never `spawnInstance` again (that makes a fresh copy). Same flow as SkyyIslands 0.1 |
| Arrive | The **landing point** on the south rim: `SpawnPositions` (a `List` position) and the instance `SpawnProvider` point, about (0, top, R - 40). Death in that world respawns here (SkyyIslands 0.4 note: respawn = the world's DeathConfig / `SpawnProvider`) |
| Leave | `/hub` = `InstancesPlugin.exitInstance` (SkyyIslands already does it) |
| Unlock the next island | Server Setup row `unlock.mode` = `summit` / `skill` / `guardian` / `open` (question 1). Default today: `summit` (stand on the summit spot). After the SkyySkills flatten ships: `skill` (summit plus class weapon skill at least the zone's top level, 10 / 25 / 40). When bosses exist: `guardian` (beat the summit guardian). The Zone 4 summit unlocks nothing until the capstone dungeon exists |
| Unlock storage | Per profile: `Skyy_SkyyWorldGen/progress/<profile or uuid>.properties`, SkyyProfiles-aware when present |
| Gate enforcement | `/zone` and the menu check the unlock. `AddPlayerToWorldEvent` exists in the release jar, so a guard can send back a player who arrives another way; whether the event can redirect or cancel is UNVERIFIED (T11). Until then the gate is soft |
| No flying | `/fly` is blocked on zone islands (SkyyExploration answer Q8); creative and admins are exempt |
| Warps | The landing town is the free starter warp (SkyyExploration D1). Warps to other towns come later with quests |

### 2.4 The vanilla world, the hub and the server

- **Vanilla world: untouched.** It stays the solo hub (the Zone 1 start area; the Temple discovery reward, +1,000 Exploration XP, already lives there, OPEN-QUESTIONS 2026-10-01) and
  a free wild world. SkyyMobs classic step 4 levels apply there. It is just not the spine. On 0.7, mods can ship whole worlds that
  show in the world list (UNVERIFIED: web patch notes only, no matching class or asset found offline); a later option is a "SkyWynn"
  world whose default world is a small V2 hub islet (question 2).
- **Hub = shared spawn**, as locked. On a server the hub and the chain are hand-built (Decisions 7.1). SkyyWorldGen helps there too:
  a builder can generate the four islands and hand-polish them, and the ring levels keep working if the layout keeps its centre.
- **Private islands (SkyyIslands 0.5): untouched.** They keep their `Void` template, `FillTask` building and settings. Different world
  names (`island-<uuid>`) and different asset prefixes, so nothing collides. SkyyMobs keeps `bands.islands` 1-3 for them.

---

## 3. Biome layout per island as game levels

### 3.1 The options

| Layout | Play | V2 fit | Level lookup | Verdict |
|---|---|---|---|---|
| **Rings, easy rim -> hard centre** (Skyy's idea) | Clear: walking inward = harder. The summit is a natural boss spot. Every rim point is safe | Native (Map_Portals pattern) | `hypot(x, z)` -> ring; exact and cheap | **Recommended** |
| Off-centre rings ("cross the island") | Land on one side, the core sits past the middle; reads as a journey | Native: same curve fed by `Offset` distance | `hypot(x - fx, z - fz)` | A later toggle (`layout.focus`), same assets |
| Spiral / path (Angle + Distance) | Most "level 1-1 -> 1-2"-like route | Possible (`Angle` node), hard to tune | Angle + distance maths | No: easy and hard arms touch (a Lv 2 meadow next to a Lv 9 swamp) unless walls are added |
| Hand-drawn region map | Best art control | Not native (no image node): shapes by hand or a Java density type | Polygon tables | No for the generator; it is what the hand-built server chain is |
| Plan B: V1 painted mask (`Zones.json` `MaskMapping` + a `Mask.png`) | Gets every real Hytale biome, real zone data (vanilla discovery, `/locate`) and SkyyMobs classic step 4 | VERIFIED: `MaskMapping` maps a colour straight to region ids (`#78ff27` = `Zone1_Tier1`, `#5bbf1d` = Tier2, `#3d8013` = Tier3 ...), so a painted image CAN pin the tiers; a V1 `Server/World/Void` world with a `Void` zone exists, and V1 worlds are picked by `{"Type":"Hytale","Name":"<folder>"}`. UNVERIFIED: whether a mod world folder may point at the `Default` world's `Zones/*` (each vanilla world folder holds its own copy, and we may not copy game files into the pack), the image scale per block, and what land beside a `Void` zone looks like (V1 terrain is a column from y 0, so probably a mesa, not a floating island). The `Default` world uses noise (`Mask.json`); `Mask.png` is used by `Flat`, `Instance_Creative_Hub`, `Instance_Default_Old`, `Void` | Classic step 4 | Fallback only if V2 biome authoring proves too slow. Not free: it needs a research spike first |

### 3.2 Recommended: warped, terraced rings

- **Six rings per island.** The rim, four rings and the core summit. Each ring is one game level (Zone 1 = "1-1" to "1-6").
- **Warped edges** (`FastGradientWarp`, amplitude about 24 blocks) so it does not look like a target from above.
- **Terraces:** each inner ring sits one step higher, so you climb toward the hardest biome. Stage 2b: three or four gaps per terrace
  wall (an `Angle` mask) become the "level entrances", with a small gate landmark (a prefab at a fixed `List` position) at each.
- **Inside a ring, the zone's Hytale biomes appear as patches** (a `PositionsCellNoise` value added on top of the ring value; 3.4).
  The biome's rarity rating (RR) orders the rings (rarer biomes sit further in); ties inside the same RR are placed by hand in section 4.
- **Landing point:** south rim, flat clearing, later the landing town (free warp, SkyyExploration D1).
- **Core summit:** the zone's hardest biome, the guardian arena and the story-dungeon entrance (Decisions batch 1 #7, SkyyDungeons-Plan.md),
  placed by a Prefab prop at a fixed position (0, y, 0).
- **Exploration:** each ring is a named discovery (the V2 stand-in for A6 zone discovery, which cannot fire on V2). SkyyExploration spots are
  circles (position + radius), so the summit and the landing town can be normal spots, but a ring is an annulus: ring discoveries must be
  `custom` checklist entries that SkyyWorldGen completes through `explore:fn:complete` when a player first stands in a ring (`wg:fn:ring`).
  That function only completes entries an admin already defined, and the 0.2 backbone has no bridge call that defines entries, so this needs
  one small SkyyExploration addition (a define-entry bridge call or a shipped default checklist for `skywynn_z1`..`z4`; stage 2 dependency).

### 3.3 Ring geometry (fractions of R; blocks from the centre at the medium size)

| Ring (game level) | Fraction of R | Share of land | Zone 1 (R 640) | Zone 2 (704) | Zone 3 (768) | Zone 4 (832) |
|---|---|---|---|---|---|---|
| R0 Rim / landing (-1) | 0.88-1.00 | 23% | 563-640 | 620-704 | 676-768 | 732-832 |
| R1 (-2) | 0.70-0.88 | 28% | 448-563 | 493-620 | 538-676 | 582-732 |
| R2 (-3) | 0.52-0.70 | 22% | 333-448 | 366-493 | 399-538 | 433-582 |
| R3 (-4) | 0.36-0.52 | 14% | 230-333 | 253-366 | 276-399 | 300-433 |
| R4 (-5) | 0.18-0.36 | 10% | 115-230 | 127-253 | 138-276 | 150-300 |
| Core summit (-6) | 0.00-0.18 | 3% | 0-115 | 0-127 | 0-138 | 0-150 |

The easy rings get the most ground (that is where most kills to reach the next band happen); the hard core is small, about 40-70 chunks
(3% of 1,257 to 2,123 chunks). The walk inward is nearly even per level step: ring widths are 77 / 115 / 115 / 103 / 115 / 115 blocks in
Zone 1 and 100 / 150 / 149 / 133 / 150 / 150 in Zone 4, so area share only decides how many mobs a ring holds. Fractions and areas above
were re-computed and check out.

### 3.4 How it is built in V2 (one recipe, reused per zone)

All asset ids start `SkyWynn_` and every export name starts `SkyWynn-` (Welkin overwrites vanilla `Map_Default` and `Zone1_Plains1` by
file name; we never reuse a vanilla file name or export name).

1. `SkyWynn-Zn-Dist`: `YOverride 0` -> `Cache` -> `Distance` (the vanilla order in `Map_Portals`), the 2D distance from the world origin.
2. `SkyWynn-Zn-DistWarp`: `FastGradientWarp` of it (`WarpFactor` about 24, `WarpScale` 250 like vanilla; INFERRED that the factor is
   the sideways shift in blocks. Vanilla uses 200).
3. `SkyWynn-Zn-RingMap` (the WorldStructure density): `Sum` of a staircase `CurveMapper` on DistWarp (core = 5, R4 = 4 ... R0 = 0,
   beyond R + 16 = -1) and `PositionsCellNoise` CellValue x 0.98 for the patches. Biome ranges: core `[5, 6)`, R4 `[4, 4.5)` Swamp,
   `[4.5, 5)` Autumn / Moss, ... edge `[-0.5, 0)`, void `[-2, -0.5)`. Notes: keep each staircase step narrow (8 blocks or less), because
   inside a step the sum slides into the next ring's lowest range (the same biome shows at every ring border) and the border follows
   the cell shapes; the CellValue source decides patch shares (Welkin feeds it a normalised Simplex, which is bell-shaped, so range widths
   are not area shares; a flat source such as `WhiteNoise` is INFERRED to be even; check shares in `/viewport`, T12).
   **Stage 1 shortcut:** copy the 0.7 Goblin pattern instead: density = warped `Distance` in blocks, biome ranges in blocks (rim
   `[0.88R, R)` ...), no patches. Add the staircase and patches in stage 2.
4. `SkyWynn-Zn-Island` (3D, imported by every biome's Terrain): solid between an underside curve (deepest at the centre, zero at R) and
   the top surface (Base + terrace step per ring + the biome's hills), from `BaseHeight`, `YValue` and `CurveMapper` like
   `Islands_Roots`. Every biome: `Terrain = Min(own hills, SkyWynn-Zn-Island)`. The terrace step must read the pure staircase
   (DistWarp through a `CurveMapper`), not the patched ring value of step 3, or every patch cell becomes its own plateau.
5. Materials and tint per biome: vanilla **block ids** (`Soil_Grass`, `Rock_Stone` ...) and tint colours taken from each V1 biome
   (`Tile.Forest_Azure.json` uses #2F798A / #2F868A). Values, not copied files.
6. Props: trees, rocks and ruins by vanilla **prefab paths** (`Prefab` prop, `WeightedPrefabPaths` with `Path` + `Weight`, `LoadEntities`
   true for chests; VERIFIED shape in `Assignments/Boreal1/Boreal1_Hedera_Boulders.json`), ores by block id per ring. V1 tiles list their
   prefabs through `PrefabPatterns` files with dotted ids and globs (`Zones.Zone1_Tier3.PrefabPatterns.Forest_Azure`,
   `Monuments.Challenge.Grass.*`), V2 uses slash folders (`Rock_Formations/Rocks/Slate/Medium`), so each biome's prop list is a hand
   translation (whether the folder names match is UNVERIFIED, T1). V1-only features (Trork camps, Kweebec villages, monuments, mineshafts,
   cave beacons, rivers, lakes) have no V2 equivalent yet and are scope on top of the 46 biome looks (risk 7.2).
7. `EnvironmentProvider`: the vanilla environment of that Hytale biome (`Env_Zone1_Azure` ...), so Hytale's own mobs, weather and sound
   come along. `DensityDelimited` by height for caves (`Env_Zone1_Caves_*`), as vanilla `Plains1_Oak` does.
8. Performance: 3D nodes inside `Cache` + `YSampled` (`SampleDistance`, `SampleOffset`, `Interpolate` keys exist; "distance 8" is from the
   pre-release docs performance page, UNVERIFIED offline), everything else 2D. Tune threads with `/worldgen2 concurrency`.

---

## 4. LEVEL TABLE

Rules:
- **One band per ring, so one range per biome.** The ring is the level; a biome's level range is its ring's band (Skyy asked for a range
  per biome: every biome row below carries one). The rarity rating (RR, Mob-Levels-Plan 3 and 4.2-4.5: region tier + scarcity + threat +
  Skyy's pick) orders the rings, rarer biomes further in. Ties inside one RR are placed by hand.
- Zone bands stay **Z1 1-10, Z2 15-25, Z3 30-40, Z4 45-60** (Mob-Levels-Plan 4.1). The zone gaps (11-14, 26-29, 41-44) hold the
  summit guardian and the core dungeon. **Zone 4 has no gap row in Mob-Levels-Plan** (4.1 lists three gaps) and its section 11 puts the
  endgame capstone at 61-70, so the Zone 4 guardian at 61-63 is a new row at the bottom of the capstone band, not a gap level.
- Neighbouring rings overlap by 1-2 levels (checked: every overlap in 4.1-4.4 is 1 or 2, no gaps, no hole between a zone's core and its
  guardian). That also hides the small mismatch between the warped ring edge you see and the exact circle the level maths uses
  (section 5, up to about 24 blocks, a quarter of a ring width).
- **Env bonus can push a mob past its ring.** Step 5 of the lookup (5.2) still adds an environment's Bonus (+1 / +2: encounters, dungeons,
  villages, Outlander) on islands. A Zone 3 core mob in an `Env_Zone3_Outlander` patch can reach 42 and a Zone 4 village mob 62, inside
  the guardian rows. Default: allowed (it reads as an elite spot), never above the zone's guardian row; or keep bonus environments out of
  the core.
- **Gear:** found gear rolls inside the ring band, then is moved into its material band (Gear-Levels-Wynn-Spec 2 and 5): a band that
  starts above the ring pulls the item up to its start (a Stone item from a Lv 3-5 ring is Lv 5), a band that ends below pushes it down
  to its cap. The "Found gear" column lists the materials whose band covers the ring. **Zone 4 limit:** vanilla materials stop at 49
  (Mithril / Onyxium 40-49, Prisma 45-49; Gear spec answer 3), our own tiers come later, so rings R2-core (mobs 50-60) cannot offer a gear
  upgrade yet.
- **Class weapon skill:** the number a player compares with the band is their class weapon skill (the SkyyGear gate), not Overall Level.
  Players should arrive at a ring about 2-5 levels below its band start and leave above its top; fighting 3-5 levels up is the intended
  hard fight (Mob-Levels-Plan 7). The flattened class curve (OPEN-QUESTIONS 2026-10-01: skill 20 in hours, 40 in days; SkyySkills round
  queued in RESUME.md 3i, not built yet) sets how long each ring takes. Ring widths (3.3) set how many mobs there are.
- Because the ring is the level (5.2 step 3b), every biome in a ring takes the ring band whatever its classic row says. The island bands
  below differ from the classic-world `bands.biome` rows in places marked `*` (see each zone's footnote); classic worlds keep
  Mob-Levels-Plan 4.2-4.5. Ring and zone **names** are working names: vanilla region names where they exist (First Gate of the Echo,
  Drifting Plains, Seedling Woods, The Fens, Golden Steppes, Badlands, Desolate Basin, Frostmarch Tundra, Boreal Reach, The Everfrost,
  Cinder Wastes, Charred Woodlands; `server.lang` `map.region.*`), invented ones otherwise (Birch Woods, Scrublands, Azure Heart, ...).

### 4.1 Zone 1 - Emerald Wilds (Lv 1-10)

| Ring | Working name | Hytale biomes (RR) | Environment | Mob Lv | Found gear (material band) |
|---|---|---|---|---|---|
| R0 | 1-1 First Gate of the Echo (landing) | Plains_Spawn (0), shore edge | Env_Zone1_Plains, Env_Zone1_Shores | **1-2** | Wood / Crude 1-13, Copper armor 1-18 |
| R1 | 1-2 Drifting Plains | Plains_Smooth (1), Plains_Birch (2)* | Env_Zone1_Plains | **1-3** | Wood / Crude, Copper armor |
| R2 | 1-3 Birch Woods | Forest_Birch (3), Forest_Flower (3), Mountain_Tier1 + Trork camps (3), Plains_Gorge T2 (4) | Forests, Mountains, Trork | **3-5** | + Stone, Bone, Trork, Wool, Leather_Soft (5-12) |
| R3 | 1-4 Seedling Woods | Plains_Tallgrass (5)*, Forest_Aspen (6), Forest_Gully (6), Mountain_Tier2 + Trork (6) | Plains, Forests, Mountains | **5-7** | same, toward the Wood cap 13 |
| R4 | 1-5 The Fens | Plains_Gorge T3 (7)*, Forest_Swamp (9), Mountain_Tier3 + Trork (9), Forest_Autumn (10)*, Forest_Moss (10)* | Plains, Swamps, Autumn | **7-9** | + Linen, Leather_Light, Scrap (10-17); first Copper 10-18; iron ore |
| Core | 1-6 Azure Heart (summit) | **Forest_Azure** (10, Skyy's pick) | Env_Zone1_Azure | **8-10** | Copper 10-18 |
| Guardian | Zone 1 guardian + core dungeon | arena prefab | Env_Zone1_Dungeons (+2) | **11-13** | Copper Lv 11-14 (the gap) |

\* Classic rows (Mob-Levels-Plan 4.2): Plains_Birch 2-4, Plains_Tallgrass 4-6, Plains_Gorge T3 6-8, Autumn and Moss 8-10. On the island
they take their ring's band. Autumn and Moss sit one level under the blue forest core, which keeps the blue forest as the hardest place
(Skyy's pick, Mob-Levels-Research 3.3). Kweebec villages (friendly, no levels) can sit in R1-R2; rivers and lakes are props, not rings.

### 4.2 Zone 2 - Howling Sands (Lv 15-25)

| Ring | Name | Hytale biomes (RR) | Environment | Mob Lv | Found gear |
|---|---|---|---|---|---|
| R0 | 2-1 Golden Steppes shore (landing) | Savannah_Forest (2), Savannah_Plains (2), shore | Env_Zone2_Savanna, _Shores | **15-17** | Iron / Bronze 15-23; Cotton, Leather_Medium, Tribal 15-22 |
| R1 | 2-2 Golden Steppes | Savannah_Boab (2), Savannah_Rock (2), Mudflats (2), Plateau overlay (3) | Savanna, Plateaus | **16-18*** | Iron |
| R2 | 2-3 Scrublands (name invented: Scrub_Bushland is a Golden Steppes biome in vanilla) | Scrub_Bushland (4), tar pits | Env_Zone2_Scrub | **17-19** | Iron, top of the 15-22 families |
| R3 | 2-4 Badlands | Desert_Oasis, Desert_Rock, Desert_Springs, Desert_Red (6), Desert_Hotsprings, Plateau_Desert | Env_Zone2_Deserts, _Plateaus | **19-22*** | + Thorium 20-28; Silk, Leather_Heavy, Steel 20-27 |
| R4 | 2-5 Desolate Basin | Desert_Barren (8) | Env_Zone2_Deserts | **22-24** | Thorium |
| Core | 2-6 Mushroom Hollow (summit) | Desert_Mushroom (8)*, Desert_Oasis_Hidden (9), Desert_Mushroom_Foot | Deserts, Env_Zone2_Oasis | **23-25** | Thorium, first Cobalt 25-38 |
| Guardian | Zone 2 guardian + core dungeon | arena prefab | Env_Zone2_Dungeons (+2) | **26-28** | Cobalt Lv 26-29 |

\* Classic rows: Boab / Rock 15-17, Badlands 20-22, Desert_Mushroom 22-24 (the only Mushroom row at 22-24; its hidden-oasis and Foot overlays
are 23-25). Nudged for overlap and so the summit biome is the top of the zone.

### 4.3 Zone 3 - Whisperfrost Frontiers (Lv 30-40)

| Ring | Name | Hytale biomes (RR) | Environment | Mob Lv | Found gear |
|---|---|---|---|---|---|
| R0 | 3-1 Frostmarch shore (landing) | Forest_Redwood (2, Kweebec villages), Plains_Shire (2), shore | Env_Zone3_Forests, _Tundra, _Shores | **30-32** | Cobalt 25-38; Doomed, Void, Frost, Flame, Praetorian 25-32 |
| R1 | 3-2 Frostmarch Tundra | Forest_Fir (3), Forest_Tundra (3), Plains_Hotsprings (3), Mountain T1 | Forests, Tundra | **31-33** | Cobalt; Cindercloth, Ancient, Crystal 30-37 |
| R2 | 3-3 Boreal Reach | Forest_Cedar (5) | Env_Zone3_Forests | **33-35** | Cobalt |
| R3 | 3-4 Boreal Heights | Plains_Frozen (6), Forest_Cedar_Mixed (6), Plains_Tundra (6), Mountain T2 | Glacial, Forests, Tundra, Mountains | **35-37** | + Adamantite 35-43; Scarab, Spectral, Silversteel, Demon 35-42 |
| R4 | 3-5 The Everfrost | Forest_Frozen (8), Forest_Frozen_Light (8), Plains_Frozen_Frost (8) | Env_Zone3_Glacial | **37-39** | Adamantite |
| Core | 3-6 Everfrost Summit | Mountain T3 (9), Outlander village (+2 env bonus) | Glacial, Env_Zone3_Outlander* | **38-40** | Adamantite, first Mithril / Onyxium 40-49 |
| Guardian | Zone 3 guardian + core dungeon | arena prefab | Env_Zone3_Encounters (+2) | **41-43** | Mithril Lv 41-44; Crystal_Flame / Crystal_Ice 40-47 |

Zone 3 rows match the classic rows (Mob-Levels-Plan 4.4) exactly; no `*` needed. Outlander and encounter patches add +2 on top (rules above).

### 4.4 Zone 4 - Devastated Lands (Lv 45-60)

| Ring | Name | Hytale biomes (RR) | Environment | Mob Lv | Found gear |
|---|---|---|---|---|---|
| R0 | 4-1 Cinder shore (landing) | Wastes_Grasslands (2), shore | Env_Zone4_Wastes, _Shores | **45-47** | Mithril / Onyxium 40-49, Prisma 45-49 |
| R1 | 4-2 Cinder Wastes | Wastes_Geysers (3), Forest_Ghost (3), Desert_Dunes (3), Forest_Swamp Z4 (3), ghost towns | Volcanoes, Forests, Wastes, Crucible | **47-50*** | Mithril, Prisma |
| R2 | 4-3 Ashlands | Desert_Ash (5), Wastes_Ash (5) | Env_Zone4_Wastes | **50-53*** | capped at 49 until our own tiers (Gear spec question 3, answered 2026-10-01) |
| R3 | 4-4 Lava Fields | Wastes_Lava (6) | Env_Zone4_Volcanoes | **53-56*** | same |
| R4 | 4-5 Charred Woodlands | Forest_Burned (7), Forest_Roots (7) | Env_Zone4_Forests | **56-59*** | same |
| Core | 4-6 Caldera (summit) | volcano caldera, Zone 4 village patch (+2) | Volcanoes, Env_Zone4_Villages* | **58-60** | same |
| Guardian | Zone 4 guardian; then the one endgame capstone dungeon (Decisions batch 1 #7) | arena prefab | Env_Zone4_Encounters* | **61-63** | own tiers 50+ (later) |

\* Classic rows (Mob-Levels-Plan 4.5): R1 biomes 48-50, Ash biomes 53-55, Wastes_Lava 55-57, Burned / Roots 58-60. Filled in so Zone 4 has no
hole at 51-52 (the classic table jumps 50 -> 53). The caldera summit is a feature we build; it is not a vanilla tile biome.
**Spawn gap:** `Env_Zone4_Crucible` (the vanilla Zone 4 swamp's environment, `Tile.Forest_Swamp.json`) has no world spawn file (VERIFIED, no
match under `Server/NPC/Spawn`), and neither do `Env_Zone4_Villages*` / `Env_Zone4_Encounters*` (VERIFIED: no match in any spawn folder; whatever stands there comes from
markers or prefabs, INFERRED). A Zone 4 swamp look on
`Crucible` would be empty unless we give it another environment or our own spawn file. Zone 4 world spawn files exist only for Forests,
Wastes, Volcanoes, Jungles and Shores. Zone 4's guardian row (61-63) is explained in the rules above.

### 4.5 The whole ladder

| Zone | R0 | R1 | R2 | R3 | R4 | Core | Guardian | Leave with |
|---|---|---|---|---|---|---|---|---|
| 1 | 1-2 | 1-3 | 3-5 | 5-7 | 7-9 | 8-10 | 11-13 | Copper, weapon skill about 12 |
| 2 | 15-17 | 16-18 | 17-19 | 19-22 | 22-24 | 23-25 | 26-28 | Cobalt, skill about 27 |
| 3 | 30-32 | 31-33 | 33-35 | 35-37 | 37-39 | 38-40 | 41-43 | Mithril, skill about 42 |
| 4 | 45-47 | 47-50 | 50-53 | 53-56 | 56-59 | 58-60 | 61-63 | capstone dungeon; skills go on to 100 later |

Oceans (Crystalline Depths) get no island in this plan. A later side island can use the 13 ocean looks at Lv 5-10 (Mob-Levels-Plan 4.1).

---

## 5. How mob levels and gear levels read the island at runtime

### 5.1 SkyyWorldGen publishes the geometry (bridge keys, java.lang types only)

| Key | Shape | Notes |
|---|---|---|
| `wg:fn:ring` | Function(Object[]{String world, Integer x, Integer z}) -> String `"Z1\|R3\|5-7\|Seedling Woods"`, null when the world is not a SkyyWorldGen world | Pure maths (`hypot` against the radius baked into that world's assets), any thread, no chunk reads. Same string style as `mob:fn:band`, so readers split on `\|` |
| `wg:fn:zone` | Function(String world) -> String `"Zone1\|Emerald Wilds"` | For SkyyExploration zone discovery and the SkyyHud location line |
| `wg:fn:unlocked` | Function(Object[]{UUID player, Integer zone}) -> Boolean | For menus, gates and quests |
| `config:def/fn/epoch:SkyyWorldGen` | the config kit | Rows below |

The ring **bands and names** live in one table, SkyyWorldGen `rings.properties` (Server Setup page "Rings"). SkyyMobs and SkyyGear only
read them. The **geometry is not editable at runtime**: the radius R and the ring fractions are numbers inside the generated density JSON
(V2 assets take no runtime parameters), so the build script writes them once into both the JSON and the Java constants from one Python
table. Consequences: the size preset (`layout.size`, default medium) picks which template a world is created from, it
cannot change a world that already exists, and each preset is its own set of WorldStructure + density files (3 sizes x 4 zones = 12
sets, generated, or ship medium only until Skyy asks for more). Changing a fraction later means a new world version (risk 7.2).

### 5.2 SkyyMobs lookup chain (Mob-Levels-Plan 2.1, one new step)

| Step | Source | On a SkyyWorldGen island |
|---|---|---|
| 0-2 | saved plate, `scale.role` (guardians), `bands.world` | Guardians get fixed levels from `scale.role` (the Guardian rows above). `bands.world` must stay **empty for `skywynn_z*`**: step 2 outranks 3b, so a row there would switch the ring bands off |
| 3 | private island | not these worlds |
| **3b (new)** | `wg:fn:ring` at the leash point (`NPCEntity.getLeashPoint()`) | **Wins:** the ring band. Works for marker and beacon spawns too (their `getEnvironment()` is `Integer.MIN_VALUE`) |
| 4 | classic zone + biome | skipped (no `ChunkGenerator` on V2) |
| 5 | environment (`NPCEntity.getEnvironment()`, else `BlockChunk.getEnvironment(int,int,int)`) | Adds only its **Bonus** column (dungeons, villages, encounters +1 / +2), like on classic worlds. It is the full fallback if SkyyWorldGen is missing |
| 6-7 | zone prefix, default | `Env_Zone2_...` -> `bands.zone` |

No `bands.world` safety rows (the first draft had `skywynn_z1` 1-10 ... `z4` 45-60; they would have overridden step 3b). The safety net
without SkyyWorldGen is step 5, the environment rows of Mob-Levels-Plan 4.6, which already cover every environment these islands use.
Caves: the ring lookup is 2D (x, z), so a cave mob inherits the ring above it automatically; `bands.caves` only matters on classic worlds.

Why geometry and not the environment as the main source: several rings share one vanilla environment (Zone 2 rim and R1 are both
`Env_Zone2_Savanna`), marker spawns have no saved environment, and the maths needs no world read. The warped edge (about 24 blocks) can
put a mob one ring off near a border; the 1-2 level overlap hides that. Stage 4 option: one custom environment per ring
(`Env_SkyWynn_Z1_R3`, `Parent` = the vanilla one, `SpawnDensity` set, our own spawn files) makes the environment exact and gives each
ring its own mob list.

### 5.3 Mob lists

Stage 1-3: vanilla environments per ring, so vanilla's own tiers come along (Plains = Tier 1 list; Forests / Mountains / Autumn = Tier 2;
Swamps / Azure = Tier 3, with Skeleton_Burnt_Praetorian and Skeleton_Mage in the blue forest; VERIFIED in `Wander_Zone1_Tier1..3`). So the
mob mix follows the environment, not the ring: a Plains patch inside R4 (Lv 7-9) still spawns only the Tier 1 list (Skeleton_Fighter and
wolves) at Lv 7-9, which the level scale makes harder but does not diversify. Two island gotchas to test: the spawn rule's `SpawnBlockSet`
(`Soil` in these files) must contain our ground blocks, and 0.7 spawn markers check the ground below (`ValidateBelowPosition`, up to 192
blocks; 0.7 only, VERIFIED in the pre-release jar).

### 5.4 Chest and drop gear levels (Gear-Levels-Wynn-Spec 5)

- **Lookup 1 (new, for SkyyWorldGen worlds):** `wg:fn:ring(world, x, z)`: pure maths, any thread, no cache. A chest on the rim rolls Lv 1-2,
  in the Zone 1 core 8-10. Do **not** route this through `mob:fn:band`: that call reads SkyyMobs' per-chunk cache and returns null for a
  chunk where no mob has spawned yet (Mob-Levels-Plan 8), which is exactly the chest case. **Lookup 2:** `mob:fn:band(world, x, z)` for
  other worlds (SkyyMobs stage 2). **Lookup 3:** `loot.level.world.skywynn_zN` (default rows 1-10 / 15-25 / 30-40 / 45-60) when neither mod
  answers. **4:** the material band start. This adds one step to Gear-Levels-Wynn-Spec 5 (its chain is mob band, world row, band start).
- Then the material clamp: a Wood sword from the Zone 3 rim stays 13; an Iron sword is never below 15.
- Guardian drops: the guardian's level +/- `loot.mobSpread` (the gap levels 11-14, 26-29, 41-44), so the guardian is the bridge to
  the next island's gear.
- What materials a ring offers comes from the assets: each ring's chest prefabs and ore blocks (section 4 "Found gear").
- Still LOCKED: every found weapon and armor piece is unidentified (2026-10-01). The pacing answer (flatten) unblocks Gear spec stage 4.

---

## 6. Assets alone vs plugin code; what to learn from

### 6.1 Split

| Assets only (JSON in the jar; the in-game node editor writes the same JSON) | Plugin code (SkyyWorldGen, small Java, `build_skyyworldgen_0.x.py` pattern) |
|---|---|
| 4 WorldStructures per size preset (medium first) + 1 test structure, the ring map, island mask, warps | Create, persist and reopen the four worlds (`spawnInstance`, `Universe.addWorld`, `WorldEmpty` unload) |
| 46 biome looks (13 + 11 + 12 + 10 land tiles, section 7.2) plus `SkyWynn_Edge`, `SkyWynn_Void` and the summits | `/zone`, SkyyMenu tile, `/hub` hand-off, landing teleport |
| Props: trees, rocks, ruins, chests, ores (vanilla prefab paths and block ids) | Unlock state per profile, `unlock.mode`, summit / guardian check |
| Environments per biome (vanilla ids); later custom ring environments + spawn files | Bridge keys `wg:fn:ring`, `wg:fn:zone`, `wg:fn:unlocked` |
| 4 `instance.bson` templates (`HytaleGenerator`, `SeedOverride`, SpawnProvider; copy `GameMode`, `IsSpawningNPC`, `IsSpawnMarkersEnabled`, `DeleteOnRemove` from the vanilla region instances) | Server Setup rows: `layout.size` (applies to new worlds only), `layout.focus` (later), `unlock.mode`, `fly.block`, `rings.*` bands and names (geometry is baked, see 5.1) |
| Landing, gate and summit prefab positions (`List` positions) | `/fly` block, Exploration hooks (`explore:fn:complete` for ring discovery; defining the entries needs the SkyyExploration addition in 3.2), admin `/zone info` (ring, band, distance) |
| Optional `PortalTypes` / `Instance_Gateway` for a hub gate | Gate guard on `AddPlayerToWorldEvent` (T11). Only if needed: the asset-map fix that MajorDungeons uses (risk 2): its `HytaleGeneratorAssetMapFix` copies entries into the generator's `AssetManager` maps (worldStructure, biome, density, assignment, blockMask, propDistribution, positionProvider, prop) on `LoadedAssetsEvent` (VERIFIED in the installed jar) |

### 6.2 Mods to learn from (ideas, not files)

Project rule: **clean-room**. ARR or no licence = study only. MIT = could be reused with its notice, but we still take ideas only
unless Skyy says otherwise. GPLv3 = never copy (it would force the pack under GPL). **Licences, contest placements and the timing number
below come from the CurseForge pages (web research of 2026-10-01) and are UNVERIFIED offline: none of the installed archives carries a
licence file or a licence field in its manifest.** Check the page before relying on a licence. "Installed" = the file sits in
`UserData\Mods` and was inspected read only for this review.

| Mod | Licence (web) | Learn |
|---|---|---|
| Vanilla `Portals_Oasis` + `Map_Portals` (release), `Portals_Goblins` (0.7) | game files | The ring + void pattern, edge buffer biome, spawn positions (VERIFIED, section 1) |
| Welkin (wyvernling, contest 10th). Installed, pure asset zip, no jar | ARR | A one-biome `WelkinWorldStructure` (`DefaultBiome` only) over a density of `PositionsCellNoise` blobs (MaxDistance 600, 470-block grid) through a `FastGradientWarp` 80; own spawn files per island env (`Spawns_Welkin_BigIsles_*`); two instances (`Welkin`, `Nimbus`). VERIFIED: it ships copies of vanilla `Map_Default.json`, `Map_Portals.json`, `Zone1_Plains1.json` ... under the vanilla names, which is the warning. Its "permanent portal" is UNVERIFIED (no `PortalTypes` in the zip) |
| Veil Islands (Iced_Fox_Studios, 4th). Not installed | ARR | A floating-island dimension with its own mobs, ores and merchants (web only) |
| Skyreach Ravines (TheBreadley, 9th). Installed | ARR | Floating mage tower on a sky island; 2 biome entries, 1 instance, `PortalTypes`; travel by an item (Ancient Gateway, web) |
| Necromancer's Spire (legendary_workshop, 1st). Installed, a jar with `Main` + `IncludesAssetPack` | ARR | Key + ritual entry, a 200-block dungeon tower (web): model for the summit dungeon. It ships V2 assets in a jar and has no asset-map fix class, which is evidence for T1 |
| Neymeros (posnep, 8th). Installed, pure asset zip | ARR | about 15 biome files and 13 instances (`Neymeros_World`, `Biolume_Swamp`, `Nytheris_Peaks` ...) over one map density, `PortalTypes`; the "about 175 ms for a heavy biome" cost number is web only (UNVERIFIED) |
| Dragons Fantasy Scenes (DragonstoneMC, 3rd). Installed zip | **GPLv3** | `/instance` flow (its manifest says so) over many instances (hundreds of files under `Server/Instances`). Study only |
| TheLostWorlds (MrZip). Installed zip, licence unknown | unknown: study only | 7 WorldStructures and a `Skylands_Garden` instance; V2 on release |
| Skylandsea (Krah). Not installed | MIT | Islands joined by bridges; its web node viewer is a handy dev tool (no noise preview in game) |
| SouzaSkyblock, realBritakee/voidworldgenerator. Not installed | MIT | Per-player void islands, void generator registration |
| MajorDungeons (`HytaleGeneratorAssetMapFix`). Installed jar | none | Warning sign: mod V2 assets may need a nudge to reach the generator. VERIFIED in the jar: it patches the `AssetManager` maps on `LoadedAssetsEvent` |

---

## 7. Build stages, risks, in-game checks

### 7.1 Stages (smallest proof first; each ends with a Skyy test, deploy per the usual round rules)

| Stage | What | Done when |
|---|---|---|
| **0 Proofs** (throwaway save, scratch test pack, no SkyWynn jar) | T1-T13 below, with a hand-written 3-biome test structure | Each check has a yes / no |
| **1 Zone 1 test island** (SkyyWorldGen 0.1) | One world `skywynn_z1`, small preset (R 384), 3 rings (meadow rim, birch-forest middle, azure-look core), void around, landing point, `/zone 1`, `/hub`, persist and reopen. Vanilla envs only. Assets use the Goblin shortcut (warped `Distance` in blocks as the density, no patches) | Skyy walks rim -> core, sees Tier 1 -> Tier 3 mobs, falls off and respawns at the landing |
| **2 Full Zone 1** (0.2) | Medium preset, 6 rings, all Zone 1 biome looks as patches (staircase + cells), terraces, summit, ores and chests per ring, `wg:fn:*` bridge, `rings.properties`, ring discovery (needs the SkyyExploration define-entry addition, 3.2), `unlock.mode=summit` | Ring bands show on mobs once SkyyMobs exists (`/mobs inspect` says step 3b) |
| 2b | Terrace gaps as level entrances, gate landmarks, landing town clearing | |
| **3 Zones 2-3** (0.3) | Two more islands, unlock chain, travel menu, `fly.block`, gate guard (T11) | A fresh profile can only open Zone 1; the summit opens Zone 2 |
| **3b Zone 4** | The island and its Lv 45-60 rings are built, but hidden behind a `zones.max` row (default 3) until our own Lv 50+ gear tiers exist (question 3) | Zone 4 opens only when Skyy flips `zones.max` to 4 |
| **4 Polish** | Guardians (SkyyMobs `scale.role`), summit dungeons (SkyyDungeons), custom ring environments + spawn files, void islets with Echo Shards, off-centre toggle, 0.7 whole-world option, shared-world reset and protection (risk 7.2) | |

Dependencies: SkyyMobs (planned, Mob-Levels-Plan section 13) gives the levels; until it ships the islands still work, just without
level plates. SkyyGear 0.2 stage 4 gives ring-levelled loot. SkyySkills' flatter class curve (queued after the 2026-10-06 reset) is what
makes `unlock.mode=skill` playable: with today's curve, skill 25 needs about 3.0 million XP (Gear-Levels-Wynn-Spec 0), so until the flatten
ships the default stays `summit`.

### 7.2 Risks

| Risk | Effect | Answer |
|---|---|---|
| Authoring cost | 46 biome looks (V1 land tiles: Zone 1 13, Zone 2 11, Zone 3 12, Zone 4 10) plus V1-only features V2 does not have yet (Trork camps, Kweebec and Outlander villages, monuments, mineshafts, cave beacons and dungeons, rivers, lakes) | One shared island mask and terrain per zone; biomes differ by materials, tint, props and env. Start with one look per ring; add the V1-only features later. Plan B (V1 painted mask) needs its own research spike first (3.1) |
| Mod assets not reaching the generator | Island does not generate | Evidence it works: installed Welkin, Neymeros and Dragonstone (zips) and NecromancerSpire (a jar with assets, no fix class) all ship V2 assets; MajorDungeons patches the `AssetManager` maps as a precaution. Stage 0 T1. If it fails, copy the reflective fix idea (our own code) |
| Release vs 0.7 | 0.7 removes `YFor2D` (GradientWarp), `GraphGenerator` `IsSingleInstance` (the density `Exported` `SingleInstance` stays), vanilla V2 biomes | Target release; never use removed keys or vanilla V2 exports; plugin uses `getEnvironment(int,int,int)`, and the 0.7 5-arg `spawnInstance` and async teleport (PreRelease-Compat-Report). "Whole-world mods are 0.7-only" is a web claim, UNVERIFIED |
| Global names | Clashes with other mods; `Settings/Settings.json` is one global file (Welkin ships one) | `SkyWynn-` prefix on every export, `SkyWynn_` on every file; never ship our own `Settings.json` |
| Performance | Each island about 1,300-2,100 chunks of land with a body up to 180 blocks thick; 3D warps and material providers are costly; the V2 worker pools and request queue are one shared plugin singleton; the default settings aim at `TargetPlayerCount` 3 / `TargetViewDistance` 512 | `Cache` + `YSampled`; 2D warps only; measure with the `StatsCheckpoints` log lines and tune with `/worldgen2 concurrency` (`/worldgenbenchmark` does not work on V2); small preset as the fallback |
| Spawns on floating ground | No mobs if `SpawnBlockSet` (`Soil` in the Zone 1 files), `ValidateBelowPosition` (0.7) or a missing spawn file rejects our island: rock summits (Mountain, Everfrost) may spawn nothing; `Env_Zone4_Crucible` has no spawn file | Stage 0 T4; custom spawn files if needed |
| Release "no NPC / ore spawns inside structures" (Welkin, Skyreach claim, web) | Empty ruins | Stage 0 T8 |
| **Gate bypass** | Any teleport that is not `/zone` (vanilla `/tp`, warps, other mods) can enter a locked island | Guard `AddPlayerToWorldEvent` (T11); soft gate until then |
| **Shared-world wear and griefing** | A profile or player entering later finds chests already looted, ore mined, trees felled; players can place blocks anywhere | Locked as shared (SkyyExploration Q9), so plan stage 4 work: chest and ore refill timers or per-profile loot, an admin `/zone reset <n>` (re-copy the template, unlock progress kept), and block protection reusing the SkyyIslands visitor flags. Not a question yet |
| **Updating worldgen after release** | Saved chunks keep the old terrain, unexplored chunks generate with the new assets, so a seam appears | Fixed `SeedOverride` per zone template (INFERRED deterministic); after release change worldgen only as a new world version (`skywynn_z1b`), never in place |
| **Baked geometry** | R and the ring fractions live in the JSON; editing them in `rings.properties` would put `wg:fn:ring` out of step with the terrain | Only bands and names are editable (5.1); geometry comes from one Python table that writes both JSON and Java |
| **Zone 4 gear cap** | Mobs Lv 50-60 but gear stops at Lv 49 until our own tiers | Question 3: Zone 4 built but hidden (`zones.max`) |
| **Pacing not built yet** | With today's curve `unlock.mode=skill` at 25 / 40 is unreachable | Default `summit` until the SkyySkills flatten ships (7.1) |
| No zone data on V2 | No vanilla discovery banner, compass zone name, `/locate`; SkyyExploration A6 cannot fire | Ring discoveries through `explore:fn:complete` (3.2); T9 |
| Experiments ruining a save | Lost world | Only throwaway saves until stage 2; never the live world |
| Height 320 | Summit cap | Summit at y 240 or below |
| Ring edge vs level maths | A mob one ring off near a border (warp up to about 24 blocks against rings 77-150 blocks wide) | 1-2 level overlap; custom ring environments in stage 4 |

### 7.3 Only verifiable in game

- T1: the prefixed `Server/HytaleGenerator/**` assets of a mod load on the installed release build (no "Couldn't find" log lines), from a jar and from a zip; V1 prefab folder names resolve in V2 `Prefab` props.
- T2: the plugin's `spawnInstance` of a `HytaleGenerator` instance generates, persists, and reopens with `Universe.addWorld`; login while unloaded.
- T3: the `Distance` sample position is in world block coordinates (the node is origin-based, VERIFIED); the island sits at (0, 0) with void around.
- T4: vanilla `Env_Zone1_Plains` / `Env_Zone1_Azure` spawn their mobs on a floating island (grass, and also stone and snow ground).
- T5: `NPCEntity.getEnvironment()` returns the ring environment for V2 mobs.
- T6: a custom environment with `Parent` + `SpawnDensity` and our own spawn file spawns (stage 4 path).
- T7: generation time for an R 640 island while walking and while falling or gliding.
- T8: chests in V2 prefabs get loot, SkyyGear's unidentified tag and SkyyExploration's first-open XP; NPCs and ores inside structures.
- T9: on a V2 world `/player zone`, the compass, the discovery banner and `WorldMapTracker.getCurrentZone()` give nothing.
- T10: which spawn wins, the structure's `SpawnPositions` or the instance `SpawnProvider`, and that a `SpawnProvider` Y above the ground lands a player on the rim.
- T11: `AddPlayerToWorldEvent` can redirect or bounce a player who entered by another route.
- T12: patch shares match the planned ranges (check in `/viewport`), the staircase step width (8 blocks or less) keeps the ring border tidy, and the `FastGradientWarp` factor really is blocks.
- T13: a terrace step (+10 to +14 blocks over the step width) is walkable, and the gaps work as entrances.

---

## 8. Questions for Skyy (recommended default in brackets)

**ANSWERED 2026-10-01 by Skyy: (1) unlock = reach the summit today, then class skill 10 / 25 / 40 once the flatter curve ships,
then beat the summit guardian once bosses exist (the recommended staged rule); (2) solo players start on a SMALL HUB ISLAND (a fifth
world) and travel to the zone islands from it - NOT the normal Hytale world; (3) SHIFT ZONE 4 DOWN to about Lv 40-49 so vanilla gear
covers it (our own tiers extend it later) - Zone 3 / Zone 4 level tables, guardian gaps and the Mob-Levels-Plan bands need a re-fit
(proposed: Zone 3 30-38 with its guardian at 38-40, Zone 4 40-49 with a capstone at 50 - confirm when building).**

Only three, because only these change what gets built. Earlier drafts also asked about ring direction, island size, biome looks and terraces:
they are now defaults (below), each one a setting or a stage-2 call, not a blocker.

1. **What unlocks the next island, and what does "finish" mean until bosses exist?** The lock says finish the zone's island first, but there
   are no guardians yet (SkyyDungeons is planned). [**Reach the summit** until the flatter skill curve ships, then reach the summit with
   class weapon skill at least the zone's top level (10 / 25 / 40), then beat the summit guardian once bosses exist. One row,
   `unlock.mode` = `summit` / `skill` / `guardian` / `open`.]
2. **Where does a solo player start, and what is the hub?** The locked spine says the hub is the shared spawn. For solo play the plan keeps
   the normal Hytale world as the hub and wild world, with the four islands as separate worlds reached by `/zone` and the menu. The other
   option is for SkyyWorldGen to build a small fifth hub island world and start new profiles there. [**Keep the normal world as the hub.**]
3. **Zone 4 timing.** Zone 4 mobs are Lv 45-60, but vanilla gear stops at Lv 49 and our own Lv 50+ tiers do not exist yet, so its four inner
   rings would have no gear upgrade. [**Build Zone 4 with the others but keep it hidden** (`zones.max` row, default 3) until our own tiers
   exist.]

Decided by default (change the row if you disagree): concentric rings, easy rim to hard summit, landing on the south rim (an off-centre
core is a later `layout.focus` toggle); medium size, R 640 growing to 832 for Zone 4, about 2 minutes rim to centre running (applies to
new worlds only; small x0.6 and large x1.6 are separate asset sets); every Hytale biome of the zone appears as patches in its ring (46
looks), but stage 1 starts with 3 looks and Hytale's own mobs per ring, custom mob lists later; terraces with a few gaps as level
entrances; the guardian and core dungeon sit in the zone gap levels (11-13, 26-28, 41-43) and Zone 4's guardian at 61-63 (the bottom of
the 61-70 capstone band); the blue forest is the Zone 1 summit, with Autumn and Moss one level under it; island ring bands are their own
rows and classic worlds keep Mob-Levels-Plan 4.2-4.5; zone worlds are shared per save, unlocks are per profile; no `/fly` on zone islands.

---

## 9. Review log (critic + editor pass, 2026-10-01)

**Proved offline this pass** (release `Assets.zip` and jar unless marked; read only; scratch under `tools/dev/scratch/worldgen-critic`,
deleted afterwards):
- `DistanceDensity` is the 3D distance from (0, 0, 0); `Map_Portals` structure, curve points, warp factor 200; `Portals_Oasis` ranges;
  `Portals_Goblins` (0.7) raw-distance density and block-unit ranges; no image density node; 81 density types; 998 / 785 class files.
- `HandleProvider` has only `worldStructureName` and `seedOverride`; commands `worldgen2` (create, concurrency) and `viewport`; `/worldgenbenchmark`
  is unsupported on V2; `Settings/Settings.json` keys; `ChunkUtil` HEIGHT 320, MIN_Y 0, MIN_ENTITY_Y -32; BaseSpeed 5.5, sprint x1.273.
- Release V2 biome roster (no `Forests1_Oak` in release); no V2 biome uses `Env_Zone1_Azure`; every environment id used in section 4 exists;
  `Wander_Zone1_Tier1..3` environments and mobs; `SpawnBlockSet` `Soil`; `Env_Zone4_Crucible` and the Zone 4 village / encounter envs have no spawn files.
- Vanilla region names (`map.region.*`); V1 land tile counts 13 / 11 / 12 / 10; `MaskMapping` colours; `Server/World/Void` exists.
- Installed mods: Welkin ships vanilla-named files; MajorDungeons asset-map patch fields; Necromancer's Spire has no fix class; Welkin / Neymeros /
  Dragonstone / TheLostWorlds contents; `AddPlayerToWorldEvent` exists. Ring geometry arithmetic (fractions, areas, chunk counts) re-computed.

**Changed in this pass**
1. Section 1: class count (890 -> 998 / 785), density types (90 -> 81), tool commands rewritten (`/worldgen2` has `create` = Biome Creator and
   `concurrency`; `/worldgenbenchmark` does not work on V2), `MaxBiomeEdgeDistance` and the global `Settings.json` added, `Forests1_Oak` removed
   from the release roster (0.7 only), the blue-forest claim corrected, `Map_Portals` described exactly (vanilla warp 200, not a clean circle).
2. `Distance` origin question settled (VERIFIED, 3D, needs `YOverride 0`); recipe step 1 order fixed (`YOverride` -> `Cache` -> `Distance`).
3. Travel times fixed (running at 5.5 blocks/s gives 1.9 / 2.1 / 2.3 / 2.5 minutes; the old column called it sprint, which is faster).
4. **Level tables:** unmarked deviations from the classic rows now carry `*` (Plains_Birch, Plains_Tallgrass, Plains_Gorge T3, Desert_Mushroom);
   footnotes list the classic values; the "RR decides the ring" claim softened; Zone 4 has no gap row (guardian 61-63 sits at the bottom of the
   61-70 capstone band); env Bonus can push a mob 2 past its ring (documented); per-biome range stated explicitly; the Zone 4 gear cap (Lv 49)
   documented; invented ring names marked; Zone 3 matches classic exactly. Overlaps re-checked: every neighbouring pair overlaps by 1-2, no gaps.
5. **5.2 bug:** the proposed `bands.world` safety rows would have outranked the ring step (step 2 beats 3b) and switched ring levels off; removed.
6. **5.4 bug:** chests would have called `mob:fn:band`, which is cache-only and null for chunks without mob spawns; now `wg:fn:ring` first.
7. **5.1 infeasible:** `rings.properties` could not hold editable geometry (R and the fractions are baked into JSON; V2 assets take no runtime
   parameters); now bands and names only, size presets are separate asset sets chosen at world creation.
8. **3.2 infeasible:** "ring entries added to the Exploration checklist automatically" does not match the 0.2 backbone (circle spots; the bridge can
   only complete admin-defined `custom` entries); needs one SkyyExploration addition (defined).
9. 3.4: staircase notes (step width, border spill, bell-shaped CellValue, terrace height must read the pure staircase), Goblin-pattern stage 1
   shortcut, V1 `PrefabPatterns` vs V2 prefab path translation, performance wording marked UNVERIFIED where it came from docs.
10. 3.1 Plan B corrected (colours do pin region ids; a V1 Void world exists; the open points are listed; it is not free).
11. Section 6.2: every licence, placement and timing figure marked web / UNVERIFIED; installed mods inspected; Neymeros, Welkin, Skyreach rows
    corrected; TheLostWorlds added.
12. Risks: gate bypass, shared-world wear, post-release seams, baked geometry, Zone 4 gear cap, unbuilt pacing, no zone data, spawn-file gaps added;
    benchmark advice fixed. Checks T9-T13 added. Stage 3 split into Zones 2-3 and a hidden Zone 4. Dependencies mention the flatten.
13. Questions cut from six to three (ring direction, size, biome looks and terraces became defaults); question 2 now asks the real hub question.

**Still UNVERIFIED (cannot be proven offline):** everything marked UNVERIFIED above, chiefly the licences and contest placements, the 0.7
"worlds in the world list" claim, whether V2 samples positions in world block coordinates, spawn behaviour on island ground, the
`WarpFactor` unit, an `AddPlayerToWorldEvent` redirect, V1 prefab folder names in V2 props, and login while a persisted world is unloaded.

---

## Sources

- Hytale: https://hytale.com/news/2026/1/the-future-of-world-generation, https://hytale.com/news/2026/7/community-spotlight-worldgen-v2,
  https://hytale.com/news/2026/5/hytale-new-worlds-modding-contest-retrospective, patch notes https://hytale.com/news/2026/4/hytale-pre-release-patch-notes-update-5,
  https://hytale.com/news/2026/5/pre-release-patch-notes-update-6, https://hytale.com/news/2026/9/pre-release-patch-notes-update-7
- Docs: https://pre-release.docs.hytale.com/assets/instances/, https://pre-release.docs.hytale.com/creating-content/world-generation/how-to-edit-and-create-biomes/,
  https://pre-release.docs.hytale.com/creating-content/world-generation/performance-optimization/, https://pre-release.docs.hytale.com/assets/environments/,
  https://hytalemodding.dev/en/docs/official-documentation/worldgen/technical-hytale-generator/world-structure (and `/density`),
  https://github.com/HyperSystemsDev/HytaleServerDocs/blob/main/docs/worldgen/BIOMES.md
- Contest: https://hytale.curseforge.com/newworldscontest/, https://blog.curseforge.com/hytale-new-worlds-modding-contest-meet-the-winners/,
  mod pages `https://www.curseforge.com/hytale/mods/<slug>` (welkin, veil-islands-a-thrones-and-merchants-world, skyreach-ravines,
  necromancers-spire, neymeros, dragons-fantasy-scenes), https://www.curseforge.com/hytale/worlds/skylandsea,
  https://www.curseforge.com/hytale/mods/souzaskyblock, https://github.com/realBritakee/voidworldgenerator
- Game files (read only): `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip` (`Server/HytaleGenerator/WorldStructures/Portals_Oasis.json`,
  `Density/Map_Portals.json`, `Biomes/Experimental/Islands_Roots.json`, `Biomes/Void.json`, `Biomes/Default_Void/Default_Void.json`, `Settings/Settings.json`,
  `Assignments/Boreal1/Boreal1_Hedera_Boulders.json`, `Server/Instances/Regions/Zone1_Plains1/instance.bson`, `Server/Environments/**`, `Server/NPC/Spawn/World/**`,
  `Server/World/Default/Zones.json` + `Zones/*/Tile.*.json`, `Server/World/Void/`, `Server/Entity/MovementConfig/Default.json`, `Server/Languages/en-US/server.lang`),
  the same under `install\pre-release\...` (`Portals_Goblins.json`), `Server\HytaleServer.jar` (classes named above), `UserData\Mods\` (installed V2 mods)
- Repo: SkyWynn-Decisions.md, SkyyIslands-Plan.md, DESIGN-STATUS.md (question 12), SkyyExploration-Plan.md, OPEN-QUESTIONS.md (2026-10-01),
  RESUME.md 3i, research/Mob-Levels-Plan.md, research/Mob-Levels-Research.md, research/Gear-Levels-Wynn-Spec.md,
  research/PreRelease-Compat-Report.md, research/Island-Settings-Spec.md, SkyyIslands/build_skyyislands_0.5.5.py
