# Mob Levels: Plan (SkyyMobs) - 2026-09-30

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 5 (and the zone bands LOCKED 2026-10-01).

Design plan only. Nothing is built, committed or deployed. Every number is a PLACEHOLDER until Skyy picks it (section 17 lists the
questions with recommended defaults). Skyy uses they/them.

Input: `research/Mob-Levels-Research.md` (how other Hytale mods do it, the engine hooks, the zone and biome data),
`research/PreRelease-Compat-Report.md` (0.7 beta), OPEN-QUESTIONS.md (SkyyGear material levels, LOCKED 2026-09-30), SkyySkills 0.4.8,
SkyyGear 0.1.2, SkyyIslands 0.5.4, `tools/CONFIG-CONTRACT.md`. New checks for this plan (read-only, release and 0.7.0-pre.4 jars and
Assets.zip): the Zone 3 / Zone 4 biome and spawn data, the custom (overlay) biome names, the 0.7 raid "shard" files, and a member diff
of every engine call SkyyMobs needs (section 12).

Skyy's request (2026-09-30): levels set by the biome where the mob spawns. Zone 1 is the base; "the blue forest and other biomes in
zone 1 have slightly harder/higher level mobs", and "zone 2 is a pretty big step up". Inside a zone, rate the biomes by rarity: the
rarer the biome, the higher the level. Plan now, build later.

---

## 0. The short version

- **New standalone mod SkyyMobs** (zero dependencies). When a hostile mob spawns or loads, it gets a level from where it spawned, its
  max health and damage are scaled, and the vanilla nameplate shows `[Lv 9] Trork Warrior`. No ticking, no custom UI.
- **Where the level comes from** (section 2): on a normal Hytale world, the region + biome at the spawn point. On worlds without
  Hytale's zone data (the hand-built island chain, SkyyWorldGen, 0.7 portal shards) the mob's **environment**. Builders can paint
  environments on the islands with the vanilla `/setenvironment` builder command, which also picks vanilla's mob list for that spot.
- **Rarity rating** (section 3): RR = region (Tier 1 = 1, Tier 2 = 4, Tier 3 = 7) + scarcity inside the region (0-2) + threat (+1 when
  vanilla spawns Tier 2/3 mobs there) + Skyy's pick (+1 for the blue forest). It runs 0-10 in each zone. It maps onto the zone's level band.
- **Bands:** Zone 1 = Lv 1-10, Zone 2 = 15-25, Zone 3 = 30-40, Zone 4 = 45-60. Each zone ends on a SkyyGear tier and every zone step
  is a 4-level gap (11-14, 26-29, 41-44), so crossing a zone border always reads as a big jump on the plate. Encounter spots, dungeons
  and elites fall into the gaps. Blue forest (`Forest_Azure`) = 8-10, the top of Zone 1, with Autumn and Moss forests. (The research
  draft had 1-12 / 15-28 / 30-42; changed after the critique, section 15 #15.)
- **Per level:** max health +4% and damage +2% (lowered from the research's 6% / 3% after the critique, section 15). Combat XP rises by
  itself because SkyySkills pays XP from max health. Drops, a level-gap XP rule and better gear odds come in stage 2 through `mob:fn:level`.
- **Fit with gear:** mob level is roughly the class weapon skill (the SkyyGear gear gate) you should have: Zone 1 ends at Copper 10,
  Zone 2 runs Iron 15 to Cobalt 25, Zone 3 runs to Mithril 40 (Adamantite 35 in the middle), Zone 4 needs our own gear. **Pacing warning:** with the
  Hypixel skill curve, weapon skill 25 needs about 3 million XP, far more than kills pay today (section 7).
- **0.7 beta:** every engine call the plan needs still exists, except `BlockChunk.getEnvironment(Vector3d)`, which is removed; use the
  `(int, int, int)` form that exists in both versions (section 12).

---

## 1. Design goals

1. Level is picked **once** (spawn or chunk load) and never changes for that mob. No ticking systems, no periodic nameplate updates.
2. **Deterministic:** the roll is seeded from the world seed + mob UUID + role, so a reloaded mob keeps its level.
3. **Readable:** vanilla nameplate, vanilla look. The level is visible before you fight.
4. **Every number editable** in Server Setup (SkyyMenu, `tools/skyycfg.py` kit). The files and the game always agree.
5. **Works on every kind of world** SkyWynn uses: classic worldgen, hand-built islands, World Gen 2, instances.
6. **Hostile mobs only** by default. Passive animals never get levels.

---

## 2. How a mob gets its level

### 2.1 The lookup chain (first match wins)

Done in a HolderSystem `onEntityAdd` (reasons SPAWN and LOAD), on the world thread. It runs after `RoleBuilderSystem` and
`EntityStatsSystems$Setup`, the same order MmoMobScaling uses (research appendix A).

| Step | Source | Used for | Key looked up |
|---|---|---|---|
| 0 | The saved nameplate already reads `[Lv N]` (LOAD only) | keeping the exact level after a reload (2.3) | - |
| 1 | `scale.role` fixed level | bosses, special NPCs | role id |
| 2 | `bands.world` | hub, dungeon and shard instances, any world an admin pins | world name or `prefix*` |
| 3 | Private island world (SkyyIslands `island:owner:fn` knows it) | player islands | `bands.islands` |
| 4 | Classic worldgen: region + biome at the spawn point | normal Hytale worlds | `bands.biome`: `Zone1_Tier3.Forest_Azure`, then `Zone1_Tier3.*_Trork` patterns, then `Zone1_Tier3.*` |
| 5 | Environment: the saved spawn environment, else the block environment at the spawn point | islands, World Gen 2, shards, caves | `bands.env`: `Env_Zone1_Azure` |
| 6 | Zone from the region name or the env id prefix (`Env_Zone2_...`) | an unknown environment | `bands.zone`: `Zone2` |
| 7 | `bands.default` (0 = no level) | anything else | - |

On a classic world, step 4 wins. Step 5 then only adds its **Bonus** column (encounter spots, villages, dungeons: +1 or +2).

Engine sources (research appendix A, VERIFIED unless marked):
- Spawn point = `NPCEntity.getLeashPoint()` (saved as `LeashPos`); fall back to the current position.
- Region + biome = `ChunkGenerator.getZoneBiomeResultAt(seed, x, z)` -> `getZoneResult().getZone().name()` + `getBiome().getName()`.
  Only when `world.getChunkStore().getGenerator()` is a classic `ChunkGenerator`.
- Spawn environment = `NPCEntity.getEnvironment()` (saved as `Env`). It is `Integer.MIN_VALUE` for mobs from spawn markers and
  beacons (Trork camps, cave beacons, encounters). The fallback is then the block environment at the leash point:
  `BlockChunk.getEnvironment(int x, int y, int z)`, 3D so caves get their cave environment. The release `Vector3d` form only floors and
  calls this one (bytecode checked). The `Vector3d` form is gone in 0.7.
- Environment id = `Environment.getAssetMap().getAsset(index).getId()`.

### 2.2 Overlays, rivers and caves

- Hytale paints **custom biomes** over the tile biomes: mountains (`Mountain_Tier1..3`), Trork camps (`Forest_Birch_Trork`,
  `Plains_Tallgrass_Trork`, ...), Kweebec villages, rivers (`River_*`), lakes (`Lake`, `Lake_Swamp`, ...), plateaus (`Plateau_*`), dunes
  (`Dunes_*`), tar pits, hidden oases. Whether `getBiome()` returns the overlay or the tile biome underneath is UNVERIFIED.
  The tables cover both cases:
  - Overlays that matter get their own rows (mountains, Trork camps, plateaus, hidden oasis). Patterns like `Zone1_Tier2.*_Trork`
    keep the table short.
  - Water and dune overlays are in `bands.passThrough` (`River_*,Lake*,Dunes_*,*_Mudflats`). They use the tile biome underneath through
    `zone.biomePatternGenerator().getBiome(...)`. That call exists, but its argument order is UNVERIFIED. If it fails, the region row
    `Zone1_Tier3.*` applies.
- **Caves:** `bands.caves = above` (default). The 2D biome lookup gives the biome of the ground above, so a cave under the blue forest is
  8-10. Vanilla also grades cave beacons by region tier, so this matches. `env` uses the cave environment rows instead.

### 2.3 Keeping the level after a reload

A mob can unload and load many times. Three layers, best first:
1. **The nameplate is the save slot.** The Nameplate component has a codec, so it should save with the mob (UNVERIFIED). On LOAD,
   `[Lv N]` is read back from it.
2. If there is no plate (plates off, or the text changed), the level is **recomputed**: same seed, and the saved spawn environment
   beats the leash point. A role can move its leash with `ActionSetLeashPosition`, so the leash alone could give a different biome
   after a reload.
3. Kept in memory by entity UUID for the damage filter and the bridge. Removed in `onEntityRemoved`.

Health multipliers are always recomputed from the level on LOAD. A curve change in Server Setup therefore reaches every mob after it
reloads. Band changes only affect new spawns, because the level is kept.

### 2.4 Who gets a level

- `WorldSupport.getDefaultPlayerAttitude() == HOSTILE` (VERIFIED). NEUTRAL too when `levels.hostileOnly` is off. FRIENDLY, REVERED and
  IGNORE never.
- `levels.exclude` role patterns (default `Test_*`). Unknown role ids are ignored with one WARN. 0.7 removes 23 roles (section 12).
- The level roll: uniform inside the band, from the seeded random. The `bands.roleShift` option (off) puts strong species (base HP 100+)
  in the top half of the band and weak ones (under 60) in the bottom half, the RPGLeveling style.
- `bands.night` (default 0) adds levels to void mobs (`*_Void` roles) that spawn at night.
- Final level = band roll + env bonus, capped at `levels.max` (100).

---

## 3. The rarity rating (how the default bands were picked)

The game never computes this. It only reads the band tables, and admins edit bands directly. The rating shows why each default is
where it is. The `/mobs survey` command (stage 1.1) measures real area shares, and the tables can be re-rated from them.

**RR = Region + Scarcity + Threat + Pick** (0-10 in each zone)

| Part | Points | Source |
|---|---|---|
| Region | Tier 1 = 1, Tier 2 = 4, Tier 3 = 7 (Zone 4: Tier 4 = 1, Tier 5 = 4). The start area `Zone1_Spawn` = 0 | Region tier comes first: a Tier 3 biome is rarer across the zone than any Tier 1 biome (research 3.2) |
| Scarcity | Share of its region's ground: 30% or more = 0, 15% up to 30% = 1, under 15% = 2. Overlay patches = 1 until surveyed | Research estimate: weight / SizeModifier^2 (smaller SizeModifier = bigger patches, bytecode) |
| Threat | +1 when vanilla spawns its Tier 2 or Tier 3 mob list there (bears, spiders, praetorians, polar bears ...) | `Server/NPC/Spawn/World/*` environment lists |
| Pick | +1 for `Forest_Azure` only | Skyy named the blue forest. By strict area Autumn and Moss are rarer (question 2) |

**Band from RR:** level low = zone floor + round((RR - lowest RR) x (zone top - 2 - zone floor) / (highest RR - lowest RR)), using the
zone's own lowest and highest RR (the start area `Zone1_Spawn` is a fixed 1-2 row and does not count). The high end is low + 2.
Zone 1: low = 1 + round((RR - 1) x 7 / 9). Zones 2 and 3: low = floor + round((RR - 2) x 8 / 7). Zone 4: low = 45 + round((RR - 2) x 13 / 5).

---

## 4. Level tables (defaults, PLACEHOLDERS)

### 4.1 Zone bands

| Zone | Band | Regions | Vanilla ores / SkyyGear level there |
|---|---|---|---|
| Zone 1 Emerald Wilds | **1-10** | Spawn 1-2, Drifting Plains 1-5, Seedling Woods 3-7, The Fens 6-10 | copper, iron (Copper 10 at the end) |
| (gap) | 11-14 | Zone 1 encounter / dungeon bonus (+1 / +2), Zone 1 dungeons, elites | |
| Zone 2 Howling Sands | **15-25** | Golden Steppes 15-19, Badlands 20-22, Desolate Basin 22-25 | thorium, cobalt (Iron 15, Thorium 20, Cobalt 25) |
| (gap) | 26-29 | Zone 2 encounters, dungeons, elites | |
| Zone 3 Whisperfrost Frontiers | **30-40** | Frostmarch Tundra 30-33, Boreal Reach 33-37, The Everfrost 37-40 | cobalt (Adamantite 35, Mithril / Onyxium 40) |
| (gap) | 41-44 | Zone 3 encounters, dungeons, elites | |
| Zone 4 Devastated Lands | **45-60** | Cinder Wastes 45-50, Charred Woodlands 53-60 | adamantite (our own gear, later) |
| Oceans (deep) | 5-10 | few hostile mobs | |

Shore and shallow-ocean regions (`Zone1_Shore_Tier2`, `Zone3_Shallow_Ocean_Tier1`, ...) take the lowest band of the matching land
region.

### 4.2 Zone 1 - Emerald Wilds (1-10)

| Region | Biome (key `Region.Biome`) | Area % in region | Region | Scarcity | Threat | Pick | **RR** | **Level** |
|---|---|---|---|---|---|---|---|---|
| Zone1_Spawn | Plains_Spawn | 100 | 0 | 0 | 0 | | **0** | **1-2** |
| Tier1 Drifting Plains | Plains_Smooth | 37.4 | 1 | 0 | 0 | | **1** | **1-3** |
| Tier1 | Plains_Birch | 15.4 | 1 | 1 | 0 | | **2** | **2-4** |
| Tier1 | Forest_Birch, Forest_Flower | 23.6 each | 1 | 1 | 1 | | **3** | **3-5** |
| Tier1 | Mountain_Tier1, `*_Trork` camps (overlays) | ? | 1 | 1 | 1 | | **3** | **3-5** |
| Tier2 Seedling Woods | Plains_Gorge | 46.7 | 4 | 0 | 0 | | **4** | **3-5** |
| Tier2 | Plains_Tallgrass | 23.4 | 4 | 1 | 0 | | **5** | **4-6** |
| Tier2 | Forest_Aspen, Forest_Gully | 15.0 each | 4 | 1 | 1 | | **6** | **5-7** |
| Tier2 | Mountain_Tier2, `*_Trork` camps | ? | 4 | 1 | 1 | | **6** | **5-7** |
| Tier3 The Fens | Plains_Gorge | 32.3 | 7 | 0 | 0 | | **7** | **6-8** |
| Tier3 | Forest_Swamp | 18.4 | 7 | 1 | 1 | | **9** | **7-9** |
| Tier3 | Mountain_Tier3, `*_Trork` camps | ? | 7 | 1 | 1 | | **9** | **7-9** |
| Tier3 | Forest_Autumn, Forest_Moss | 10.3 each | 7 | 2 | 1 | | **10** | **8-10** |
| Tier3 | **Forest_Azure (the blue forest)** | 28.7 | 7 | 1 | 1 | +1 | **10** | **8-10** |

Fallback rows: `Zone1_Tier1.*` 1-5, `Zone1_Tier2.*` 3-7, `Zone1_Tier3.*` 6-10. Kweebec villages are friendly (no levels). Rivers and
lakes pass through to the tile biome underneath.

### 4.3 Zone 2 - Howling Sands (15-25)

| Region | Biome | Area % | Region | Scarcity | Threat | **RR** | **Level** |
|---|---|---|---|---|---|---|---|
| Tier1 Golden Steppes | Savannah_Forest, Savannah_Plains | 25.5 each | 1 | 1 | 0 | **2** | **15-17** |
| Tier1 | Savannah_Boab, Savannah_Rock | 19.1 each | 1 | 1 | 0 | **2** | **15-17** |
| Tier1 | Savannah_Mudflats (overlay, savanna env) | ? | 1 | 1 | 0 | **2** | **15-17** |
| Tier1 | `Plateau_*` (overlay, plateau env) | ? | 1 | 1 | 1 | **3** | **16-18** |
| Tier1 | Scrub_Bushland | 10.8 | 1 | 2 | 1 | **4** | **17-19** |
| Tier2 Badlands | Desert_Oasis, Desert_Rock, Desert_Springs | 28.1 each | 4 | 1 | 1 | **6** | **20-22** |
| Tier2 | Desert_Red | 15.8 | 4 | 1 | 1 | **6** | **20-22** |
| Tier2 | overlays: `Plateau_Desert_*`, Desert_Hotsprings, Desert_Oasis_Hidden, Dunes_Desert_Oasis, Scrub_Tar_Pits | ? | 4 | 1 | 1 | **6** | **20-22** |
| Tier3 Desolate Basin | Desert_Barren, Desert_Mushroom | 50 each | 7 | 0 | 1 | **8** | **22-24** |
| Tier3 | overlays: `Plateau_Desert_*`, Desert_Oasis_Hidden, Scrub_Tar_Pits, Desert_Mushroom_Foot | ? | 7 | 1 | 1 | **9** | **23-25** |

Fallbacks: `Zone2_Tier1.*` 15-19, `Zone2_Tier2.*` 20-22, `Zone2_Tier3.*` 22-25. The coarse buckets put all of Badlands at 20-22.
Desert_Red (15.8%) sits right on a bucket edge, so the survey may split it off.

### 4.4 Zone 3 - Whisperfrost Frontiers (30-40)

Vanilla threat by environment: Tundra = Tier 1 list, Forests / Mountains = Tier 2, Glacial = Tier 3 (checked in the spawn files).

| Region | Biome | Area % | Env | Region | Scarcity | Threat | **RR** | **Level** |
|---|---|---|---|---|---|---|---|---|
| Tier1 Frostmarch Tundra | Forest_Redwood | 39.1 | Forests | 1 | 0 | 1 | **2** | **30-32** |
| Tier1 | Plains_Shire | 15.6 | Tundra | 1 | 1 | 0 | **2** | **30-32** |
| Tier1 | Forest_Fir | 28.7 | Forests | 1 | 1 | 1 | **3** | **31-33** |
| Tier1 | Forest_Tundra | 11.0 | Tundra | 1 | 2 | 0 | **3** | **31-33** |
| Tier1 | Plains_Hotsprings | 5.6 | Tundra | 1 | 2 | 0 | **3** | **31-33** |
| Tier2 Boreal Reach | Forest_Cedar | 56 | Forests | 4 | 0 | 1 | **5** | **33-35** |
| Tier2 | Plains_Frozen | 18 | Glacial | 4 | 1 | 1 | **6** | **35-37** |
| Tier2 | Forest_Cedar_Mixed | 16 | Forests | 4 | 1 | 1 | **6** | **35-37** |
| Tier2 | Plains_Tundra | 10 | Tundra | 4 | 2 | 0 | **6** | **35-37** |
| Tier3 The Everfrost | Forest_Frozen, Forest_Frozen_Light, Plains_Frozen_Frost | 32 / 32 / 36 | Glacial | 7 | 0 | 1 | **8** | **37-39** |
| any | overlays (mountains etc.) | ? | | region | 1 | 1 | T1 3 / T2 6 / T3 9 | 31-33 / 35-37 / **38-40** |

Outlander villages and undead encounter patches are environment patches inside the tile biomes, not custom biomes. They add their env
Bonus (+2) to the biome band.

### 4.5 Zone 4 - Devastated Lands (45-60)

Two regions only (Tier 4 = 1 point, Tier 5 = 4). Threat: Wastes = Tier 1 list, Forests / Volcanoes = Tier 2. `Env_Zone4_Crucible` has no
vanilla spawns.

| Region | Biome | Area % | Env | **RR** | **Level** |
|---|---|---|---|---|---|
| Tier4 Cinder Wastes | Wastes_Grasslands | 28 | Wastes | **2** | **45-47** |
| Tier4 | Wastes_Geysers | 23 | Volcanoes | **3** | **48-50** |
| Tier4 | Forest_Ghost | 21 | Forests | **3** | **48-50** |
| Tier4 | Desert_Dunes, Forest_Swamp | 14 each | Wastes / Crucible | **3** | **48-50** |
| Tier5 Charred Woodlands | Desert_Ash, Wastes_Ash | 25 each | Wastes | **5** | **53-55** |
| Tier5 | Wastes_Lava (volcano) | 25 | Volcanoes | **6** | **55-57** |
| Tier5 | Forest_Burned, Forest_Roots | 12.5 each | Forests | **7** | **58-60** |

### 4.6 Environment table (`bands.env`)

**Band** is used when no biome is known: islands, SkyyWorldGen, shards, unknown worlds. **Bonus** is added to the biome band on classic
worlds. Keys accept a trailing `*`.

| Zone | Environment | Band | Bonus |
|---|---|---|---|
| 1 | Env_Zone1_Plains, Env_Zone1_Shores, Env_Zone1_Kweebec | 1-3 | 0 |
| 1 | Env_Zone1_Forests | 3-5 | 0 |
| 1 | Env_Zone1_Mountains | 3-7 | 0 |
| 1 | Env_Zone1_Trork | 3-8 | 0 |
| 1 | Env_Zone1_Swamps | 7-10 | 0 |
| 1 | Env_Zone1_Autumn, **Env_Zone1_Azure** | 8-10 | 0 |
| 1 | Env_Zone1_Caves* | 3-7 | 0 |
| 1 | Env_Zone1_Caves_Volcanic_T1 / T2 / T3 | 3-5 / 5-7 / 7-9 | 0 |
| 1 | Env_Zone1_Caves_Goblins, Env_Zone1_Mineshafts | 3-8 | +1 |
| 1 | Env_Zone1_Encounters, _Graveyard, _Mage_Towers | 5-9 | +2 |
| 1 | Env_Zone1_Dungeons | 7-10 | +2 |
| 2 | Env_Zone2_Savanna, Env_Zone2_Shores | 15-17 | 0 |
| 2 | Env_Zone2_Scrub | 17-19 | 0 |
| 2 | Env_Zone2_Plateaus | 16-22 | 0 |
| 2 | Env_Zone2_Deserts | 20-24 | 0 |
| 2 | Env_Zone2_Oasis | 20-25 | 0 |
| 2 | Env_Zone2_Feran, Env_Zone2_Scarak | 18-23 | +1 |
| 2 | Env_Zone2_Caves* (volcanic T1 / T2 / T3: 16-18 / 20-22 / 23-25) | 16-22 | 0 |
| 2 | Env_Zone2_Mineshafts, Env_Zone2_Caves_Goblins | 18-22 | +1 |
| 2 | Env_Zone2_Encounters, _Mage_Towers | 20-24 | +2 |
| 2 | Env_Zone2_Dungeons | 22-25 | +2 |
| 3 | Env_Zone3_Tundra / _Shores / _Forests / _Mountains / _Glacial | 30-33 / 30-32 / 30-35 / 33-37 / 35-40 | 0 |
| 3 | Env_Zone3_Caves* | 31-37 | 0 |
| 3 | Env_Zone3_Trork | 33-38 | +1 |
| 3 | Env_Zone3_Outlander*, Env_Zone3_Encounters | 36-40 | +2 |
| 4 | Env_Zone4_Wastes / _Shores / _Crucible | 45-50 / 45-47 / 48-50 | 0 |
| 4 | Env_Zone4_Volcanoes / _Forests / _Jungles | 48-57 / 48-60 / 50-58 | 0 |
| 4 | Env_Zone4_Encounters* | 53-60 | +2 |
| 4 | Env_Zone4_Villages* | 55-60 | +2 |
| 0.7 | Env_Portal_Goblin_Surface / _Cave / _Cave_Deep / _Cave_Void | 5-8 / 7-10 / 9-11 / 10-12 | 0 |

`bands.zone` fallback (the zone's first region): Zone1 1-5, Zone2 15-19, Zone3 30-33, Zone4 45-50, Oceans 5-10. `bands.default` 1-3.
`bands.islands` 1-3.

### 4.7 The island chain (the real SkyWynn world)

The hand-built zone islands have no classic zone data. Two ways they get levels, both in stage 1:
- **Paint environments** with vanilla `/setenvironment <Env>` (builder tools; server.lang: "Sets the environment in the selected area").
  Paint start plains `Env_Zone1_Plains` (1-3), then forests (3-5), mountains (3-7), swamps (7-10), and the far end `Env_Zone1_Azure`
  (8-10). Vanilla world spawns pick their mob list from the same environment, so the right mobs and the right levels come together.
  Whether world spawns follow a painted environment is UNVERIFIED (stage 0 test 2, section 13).
- **Pin a band per world** in `bands.world` (for example `z1-island` = 1-10) for anything unpainted.

Finer control (admin-marked areas, or our own SkyWynn environments) is stage 3.

---

## 5. What scales per level

All values are Server Setup rows (section 9). L = level.

| Thing | Formula (default) | Example | Engine |
|---|---|---|---|
| **Max health** | x (1 + 0.04 x (L - 1)), cap x4 | Lv 10 x1.36, Lv 15 x1.56, Lv 25 x1.96, Lv 40 x2.56, Lv 60 x3.36 | StaticModifier MAX, MULTIPLICATIVE, fixed key `skyymobs_level` (VERIFIED recipe) |
| **Damage dealt** | x (1 + 0.02 x (L - 1)), cap x2.5 | Lv 10 x1.18, Lv 25 x1.48, Lv 60 x2.18 | DamageEventSystem, Filter group, BEFORE ArmorDamageReduction (same slot as SkyyGear GearHitSys; the two multipliers stack in either order). Returns at once unless the attacker is a levelled NPC (one map read) |
| Armor / damage taken | **none** in stage 1. Health already does this job and keeps XP-by-health honest. Stage 3 option: -0.3% damage taken per level, cap 20%, so SkyyGear True Damage has something to cut through | - | - |
| Health on SPAWN | full (maximize) | | `maximizeStatValue` |
| Health on LOAD | re-apply the modifier, **keep the health fraction** (a wounded mob stays wounded). `scale.healOnLoad` = full heal instead | | `getModifier` / `removeModifier` / `putModifier` |
| **Combat XP** | free: SkyySkills pays max health x 0.2 (clamp 1-500), and max health includes the level multiplier (UNVERIFIED) | Skeleton Fighter Lv 1 = 7 XP, Lv 10 = 10 XP | SkyySkills 0.4.8 KillSys |
| Level-gap XP (stage 2, SkyySkills) | Full XP within +-5 levels of your class weapon skill; below that -5% per level, floor 10%. **Party share uses each member's own skill** | Lv 15 player on Lv 5 mobs: 75%; on Lv 1 mobs: 55% | `mob:fn:level` + `class:skill:<uuid>` + `skill:fn:level` |
| Bonus drops (stage 2, SkyyMobs) | chance of 1 extra roll of the mob's own drop list = 1% x (L - 1), cap 50%; only when a player has kill credit | Lv 10 9%, Lv 45 44% | MmoMobScaling pattern: `Role.getDropListId()` -> `ItemModule.getRandomItemDrops` -> `ItemComponent.generateItemDrops` |
| Gear rarity (stage 2, SkyyGear) | every rarity weight above Normal x (1 + 0.02 x (L - 1)) on `odds.mob` | Lv 30: Unique+ weights x1.58 | SkyyGear reads `mob:fn:level` |
| Coins (stage 2) | 0 per level (off). Later an accessory ("Scavenger" idea) pays coins per mob level | | `coins:fn:add` |

Worked examples (vanilla base health x multiplier, XP = 0.2 x max health):

| Mob | Where | Level | Health | XP |
|---|---|---|---|---|
| Skeleton_Fighter (36) | Drifting Plains / blue forest | 1 / 10 | 36 / 49 | 7 / 10 |
| Bear_Grizzly (124) | Birch forest / blue forest | 5 / 10 | 144 / 169 | 29 / 34 |
| Skeleton_Burnt_Praetorian (226) | blue forest | 10 | 307 | 61 |
| Trork_Warrior (61) | Trork camp in The Fens | 9 | 81 | 16 |
| Skeleton_Sand_Guard (61) / Hyena (103) | Golden Steppes | 16 | 98 / 165 | 20 / 33 |
| Crocodile (145) | hidden oasis, Desolate Basin | 24 | 278 | 56 |
| Skeleton_Frost_Knight (74) / Bear_Polar (103) | The Everfrost | 38 | 184 / 255 | 37 / 51 |
| Emberwulf (193) / Rex_Cave (400) | Charred Woodlands | 58 | 633 / 1,312 | 127 / 262 |

The zone step shows in same-kind mobs: a Lv 10 skeleton (49 HP) against a Lv 16 sand skeleton (98 HP) is 2x the health and
more damage. Vanilla species health barely climbs after Zone 2 (Zone 3 frost skeletons 74, wolves 103), so levels carry most of the
Zone 3-4 difficulty.

---

## 6. How the level shows

- **Nameplate** (vanilla `Nameplate` component, set once): `[Lv 9] Trork Warrior`. Format row `plate.format` = `[Lv {level}] {name}`.
  Vanilla hostile roles have no nameplate, so we add one the way vanilla `/entity nameplate` and `DisplayNameSupport` do.
- **Name** = server.lang `npcRoles.<Role>.name` (for example "Trork Warrior", not just "Trork"). If the lookup fails: the role id with
  spaces, with `_Wander`, `_Surge`, `_Static` and `_Sleep` endings removed (row `plate.strip`).
- **Colour band** (if the client shows colour, UNVERIFIED; off as a trial until Skyy has seen it), by absolute level, in the vanilla UI kit's
  own colours:

  | Levels | Colour | Kit name |
  |---|---|---|
  | 1-14 | `#d6e4ee` | row-name white |
  | 15-29 | `#ffcc00` | warning yellow |
  | 30-44 | `#E8A93B` | gold |
  | 45-60 | `#ff6b6b` | error red |
  | 61+ and bosses | `#CC66CC` | Mythic (Skyy's lock) |

  A nameplate is the same for every viewer, so "red when it out-levels **you**" cannot go on the plate. `/mobs` gives that comparison
  per player instead.
- **No health on the plate.** It would need a periodic refresh: EndlessLeveling's hot path, and against our "no periodic updates" rule.
- `plate.mode` = `all` (every levelled mob) / `elite` (elites and bosses only, stage 3) / `off`.
- Optional later: the level in death messages and the kill feed (`DisplayNameComponent` Message, as MmoMobScaling does), the band in
  the SkyyHud location line ("The Fens - Lv 7-12", SkyyExploration already reads the zone), and a vanilla boss bar for 0.7 bosses.
- `/mobs` (player): "Mobs here: Lv 8-10 (Zone 1 - The Fens - Forest Azure). You: Swordsmanship 6 - these are 2-4 levels above you."
  Chat lines use the vanilla status colours.

---

## 7. Fit with SkyyGear item levels and class weapon skills

SkyyGear LOCK (2026-09-30): gear level by material = Crude / Wood 0, Copper 10, Bronze / Iron 15, Thorium 20, Cobalt 25, Adamantite 35,
Mithril / Onyxium 40. It is checked against your **class weapon skill** (Archery, Swordsmanship, Sorcery, Fury, Divinity).

**Rule of thumb:** mob level is about the weapon skill (and gear level) that fights it comfortably. Fighting 3-5 levels up is the intended
challenge. Each zone's top level is the gear tier you should leave it with (Zone 1 Copper 10, Zone 2 Cobalt 25, Zone 3 Mithril 40).

| Zone | Mob levels | Gear you should reach there | Weapon skill at the end | Cumulative XP (Hypixel curve) | Typical kill XP |
|---|---|---|---|---|---|
| 1 | 1-10 | Crude -> Copper 10 | ~10 | 9,925 | 7-61, about 15 |
| 2 | 15-25 | Iron 15 -> Thorium 20 -> Cobalt 25 | ~25 | 3,022,425 | 20-56, about 35 |
| 3 | 30-40 | Adamantite 35 -> Mithril 40 | ~40 | 25,522,425 | 35-50 |
| 4 | 45-60 | our own gear (none yet); SkyyGear `stat.levelFull` 40 -> 60 then | 60 | 111,672,425 | 60-260 |

**Pacing problem (for Skyy, not a SkyyMobs bug).** Weapon skill 10 takes about 660 Zone 1 kills, which is fine. Skill 15 takes about
+1,600 Zone 2 kills. Skill 25 (Cobalt) takes about +84,000 kills at today's 0.2 XP per max health, and skill 40 (Mithril) about +450,000 more. The gear gate therefore cannot be met
from combat alone once you are past Iron. Options, all SkyySkills rows:
- a shorter curve for class weapon skills (`levels.scale`);
- a level XP bonus `combat.levelBonus` (XP x (1 + 0.05 x (L - 1)), so Lv 25 x2.2);
- a higher `combat.perHealth`.

This needs a decision and a playtest before Zone 2 gear gates matter (question 7).

---

## 8. Which mod owns it

**New mod SkyyMobs** (display name `0.1 SkyyMobs`, no dependencies; every cross-mod call is optional and goes through the bridge).

Why not an existing mod:
- SkyySkills (11k lines) owns XP, not mobs.
- SkyyGear owns items.
- SkyyExploration owns zones and discovery, but mob stats would bloat it.

SkyyMobs becomes the home of the whole mob layer: levels now, elites and boss levels later, and the `setLevel` hook that future
SkyyDungeons / slayers / raids use.

Bridge keys (java.lang types only):

| Key | Shape | Stage |
|---|---|---|
| `mob:fn:level` | Function(Object[]{String world, UUID npc}) -> Integer (-1 = no level). Any thread (reads a ConcurrentHashMap) | 1 |
| `mob:fn:band` | Function(Object[]{String world, Integer x, Integer z}) -> String `"8-10\|Zone 1 - The Fens - Forest Azure"` from the per-chunk cache; null when not cached (never computes off the world thread) | 2 |
| `mob:fn:setLevel` | Function(Object[]{String world, UUID npc, Integer level}) -> Boolean; queued onto the world thread | 3 |
| `config:def:SkyyMobs` / `config:fn:SkyyMobs` / `config:epoch:SkyyMobs` | the kit | 1 |

Readers: SkyySkills (gap XP, level bonus), SkyyGear (rarity shift), SkyyHud (band line), SkyyParty (none needed: the party share goes
through SkyySkills).

---

## 9. Config rows (Server Setup, `tools/skyycfg.py` kit 1.1)

Files: `Skyy_SkyyMobs/config.properties` and `Skyy_SkyyMobs/bands.properties`. Node `skyymobs.admin`. Categories: `levels` Levels,
`bands` Bands, `scale` Scaling, `plate` Nameplate, `tools` Admin tools (stage 2 adds `rewards`, stage 3 `elite`). Every row is `live`
unless marked. `new` = applies to new spawns only.

| Key | Label | Type | Default | Min-max / opts | Flags | Help (draft) |
|---|---|---|---|---|---|---|
| part.levels | Mob levels | bool | true | | part, danger | Off = new mobs get no level. Mobs that have one keep it. |
| levels.hostileOnly | Hostile mobs only | bool | true | | new | Off = neutral fighters (boar, Scarak) get levels too. Animals never. |
| levels.max | Highest mob level | int | 100 | 1-1000 | new | Band + bonus never goes above this. |
| levels.exclude | Never level these | table `text;type;Note` | `Test_*` | | new | Role ids or `prefix*`. |
| bands.biome | Level by biome | table `int\|int;type;Min\|Max` | section 4.2-4.5 | 0-1000 | new | Key `Zone1_Tier3.Forest_Azure`, `Zone1_Tier3.*_Trork`, `Zone1_Tier3.*`. |
| bands.env | Level by environment | table `int\|int\|int;type;Min\|Max\|Bonus` | section 4.6 | 0-1000 | new | Band where no biome is known; Bonus is added on biome worlds. |
| bands.world | Level by world | table `int\|int;type;Min\|Max` | (empty) | 0-1000 | new | World name or `prefix*`. 0-0 = no levels in that world. |
| bands.zone | Zone fallback | table `int\|int;type;Min\|Max` | Zone1 1-5, Zone2 15-20, Zone3 30-33, Zone4 45-50, Oceans 5-10 | 0-1000 | new | When the region or env is unknown. |
| bands.passThrough | Use the land underneath | text | `River_*,Lake*,Dunes_*,*_Mudflats` | max 500 | new | Overlay biomes that take the tile biome below them. |
| bands.default | When nothing matches | range | 1-3 | 0-1000 | new | 0 = no level. |
| bands.islands | Private islands | range | 1-3 | 0-1000 | new | SkyyIslands island worlds. 0 = no level. |
| bands.caves | Cave mobs | choice | above | `above\|Ground above,env\|Cave environment` | new | |
| bands.night | Night bonus (void mobs) | int | 0 | 0-20, levels | new | |
| bands.roleShift | Stronger species roll higher | bool | false | | new | |
| scale.hp | Health per level | dec | 0.04 | 0-1, step=0.01 | | Max health x (1 + this x (level - 1)). |
| scale.hpCap | Health multiplier cap | dec | 4 | 1-100, x | | |
| scale.dmg | Damage per level | dec | 0.02 | 0-1, step=0.01 | | Mob damage x (1 + this x (level - 1)), before armour. |
| scale.dmgCap | Damage multiplier cap | dec | 2.5 | 1-100, x | | |
| scale.healOnLoad | Heal mobs on chunk reload | bool | false | | adv | Off = a wounded mob keeps its health share. |
| scale.role | Fixed level by role | table `int\|dec;type;Level\|Health x` | (empty; stage 3 fills bosses) | 0-1000 | new | Level 0 = roll as usual; Health x on top of the level. |
| plate.mode | Level nameplates | choice | all | `all\|All levelled,elite\|Elites and bosses,off\|Off` | new | |
| plate.format | Nameplate text | text | `[Lv {level}] {name}` | max 60, check= must hold {level} | new | |
| plate.strip | Name endings to drop | text | `_Wander,_Surge,_Static,_Sleep` | max 200 | new | Used when there is no translated name. |
| plate.color | Colour by level (trial) | bool | false | | new | UNVERIFIED client support: off until Skyy has seen it. |
| plate.colors | Level colours | table `text;type;Colour` | 1 #d6e4ee, 15 #ffcc00, 30 #E8A93B, 45 #ff6b6b, 61 #CC66CC | check= #rrggbb | new | Key = lowest level of the band. |
| tools.survey | Measure biome sizes | action, value=int | 4000 | 500-20000, blocks | | Samples worldgen around you; writes survey.txt. |
| tools.relevel | Re-level loaded mobs | action | | | danger | Recomputes level and health of every loaded mob in your world. |
| tools.strip | Remove levels (loaded mobs) | action | | | danger | Before uninstalling: strips health modifiers and level plates. |

Stage 2 rows: SkyyMobs `rewards.bonusDrop` (dec 1, % per level), `rewards.bonusDropCap` (int 50, %), `rewards.coins` (dec 0,
coins per level). SkyySkills `combat.gap.on` (bool false), `combat.gap.window` (int 5), `combat.gap.pct` (int 5, %), `combat.gap.floor`
(int 10, %), `combat.gap.party` (bool true), `combat.levelBonus` (dec 0). SkyyGear `odds.levelShift` (dec 0.02). Stage 3 rows: `elite.*`
(section 11) and `bands.area` (admin boxes). Each row lives in the mod that runs its code (kit rule).

---

## 10. Commands

| Command | Who | What |
|---|---|---|
| `/mobs` | player (`hytale:Adventurer`) | The band where you stand, the region / biome name, and how it compares to your class weapon skill |
| `/mobs inspect` | admin | Nearest mob within 8 blocks: level, the lookup step and key used (for example "step 4 `Zone1_Tier3.Forest_Azure`"), band, multipliers, plate text. The main test tool |
| `/mobs set <level>` | admin | Sets the nearest mob's level (testing) |
| `/mobs survey [radius]` | admin | Samples `getZoneBiomeResultAt` every 64 blocks (radius 4000 = about 15,600 samples, 2,000 per tick). Prints each region's share of its zone and each biome's share of its region; writes `survey.txt` with the RR each implies |
| `/mobs relevel`, `/mobs strip` | admin | Same as the tool rows |

Admin subcommands: `requirePermission("skyymobs.admin")` + `setPermissionGroups(new String[0])` (lint `perm_group_leaks`). `/mobs` is
free in the release and 0.7 (checked the vanilla command classes) and in every Skyy mod (SkyyIslands only has a "mobs" island
permission row).

---

## 11. Bosses, elites, dungeons, raids and shards (later)

- **Elites (stage 3):** a 3% chance per spawn (seeded, so a reload keeps it): +3 levels, x2 health, x1.3 damage, "Elite" in front of the
  name, plate colour one band up, a guaranteed SkyyGear drop roll with a rarity shift. Rows `elite.chance`, `elite.levels`, `elite.hp`,
  `elite.dmg`, `elite.prefix`, `elite.gearRoll`. Optional: flock leader +1.
- **Bosses:** fixed levels from `scale.role` (for example the 0.7 `Skeleton_Elite` at its zone top +3 with Health x1.5; `Trork_Chieftain`
  +2), never a random roll. Our own bosses (slayers, dungeon and island story bosses) set theirs with `mob:fn:setLevel` right after
  spawning.
- **Dungeons:** story-beat dungeons sit on their zone island, so their instance world gets a `bands.world` band in the gap
  above that zone (Zone 1 dungeon 11-13, Zone 2 26-28, Zone 3 41-43). The one endgame capstone sits above Zone 4 (61-70).
- **Raids / shards (0.7 beta):** the Goblin Breach portal leads to a goblin "shard" instance (section 12). Proposal: the shard band =
  the band of the zone where the portal was opened, +1 level for each void surge stage (vanilla escalates 6 stages in 10 minutes). The
  alternative is party-scaled: the party's average weapon skill. Research this when the beta goes live (Skyy's note in HANDOFF).
  Raids stay side content (Decisions 7.6).

---

## 12. What the 0.7 beta changes

From `research/PreRelease-Compat-Report.md` plus checks for this plan against 0.7.0-pre.4:

- **Engine members:** every call SkyyMobs needs has the same name and descriptor in both jars:
  - `NPCEntity.getEnvironment` / `getLeashPoint` / `getSpawnConfiguration` / `saveLeashInformation`
  - `Nameplate.setText` / `getText`
  - `EntityStatMap.putModifier` / `getModifier` / `removeModifier` / `maximizeStatValue`
  - the `StaticModifier` constructor
  - `ChunkGenerator.getZoneBiomeResultAt`, `ZoneBiomeResult.getBiome` / `getZoneResult`
  - `WorldSupport.getDefaultPlayerAttitude`
  - the HolderSystem and DamageEventSystem hooks
  - `DisplayNameSupport.setDisplayName`, `I18nModule.getMessage(s)`
  - `Environment.getAssetMap` / `getId`

  **Removed:** `BlockChunk.getEnvironment(Vector3d)` and `(Vector3i)`. Use `getEnvironment(int, int, int)`, which is in both versions.
  The research recipe named the removed one; this plan is already corrected. Only names and descriptors were compared, not behaviour.
  `ChunkStore` getters moved to the new superclass `ChunkGrid` and still resolve.
- **Raids / shards:** `Server/PortalTypes/Goblin_Breach.json` opens instance `Portals/Portals_Goblins`.
  - It is a World Gen 2 world (`HytaleGenerator`), so there is no classic zone data. Levels come from `bands.world` or the
    `Env_Portal_Goblin_*` rows.
  - The time limit is 600 s.
  - Void surges escalate through `Portal_Goblin_Surge_Tier1..6` (larva up to void spawn).
  - Loot chests come in Tier 1-5. Dying there loses 50% of your items (`GameplayConfigs/PortalsGoblins.json`).
  - How instance worlds are named, which `bands.world` would match, is UNVERIFIED.
- **Elite boss:** new `Skeleton_Elite` (350 HP) with a Phase 2 role, run by the Encounter Manager (`Encounter_Skeleton_Elite`).
  Encounter spawns come from markers, so their environment is `MIN_VALUE` and the lookup falls through to steps 4-5. Bosses get fixed
  levels (section 11).
- **Vanilla now grades by zone x tier too:** new `Zone1..4_Encounters_Tier1..4` chest spawners and drop lists. This backs the band
  design, and SkyyGear chest odds could key on it later.
- **Elemental damage types** (Fire, Earth, Water, Wind, Lightning, Crush) and rune abilities (ItemLevel 10 / 20). The damage filter scales
  by attacker, not by type, so a mob's elemental hits scale as well. A future "damage taken" option must include ability damage.
- **23 NPC roles removed** (mostly old goblins and the Goblin dungeon). The role and exclude tables must tolerate unknown ids (warn once).
- Mana 100, food and HUD changes: no effect on mob levels. The new vanilla commands (`/abilities`, `/beam`, `/knockback`, `/wilderness`,
  `/ephemeral`) do not clash with `/mobs`.
- **Build:** against the release jar as usual, plus a link check against the pre-release jar before shipping (compat report 8.9).

---

## 13. Build order

**Stage 0 - two in-game checks before any code (about 15 minutes)**
1. Nameplate colour: `/entity nameplate` on a mob with three markup tries (a `<color=#ff6b6b>` tag, a `§c` code, a `{#ff6b6b}` token).
   This decides `plate.color`.
2. `/setenvironment Env_Zone1_Azure` on a selection in a test world, then wait for a night spawn: do Azure mobs appear? This decides
   the island plan (4.7).

**Stage 1 - SkyyMobs 0.1 (levels, health, damage, nameplate)**, `SkyyMobs/build_skyymobs_0.1.py` + `test_skyymobs_0.1.py`
1. Config kit rows and the default band files (section 9). Default tables are generated from Python lists in the build script.
2. `LevelHook` (HolderSystem): who gets a level (2.4) -> lookup chain (2.1) with a per-chunk cache of the 2D worldgen result -> roll ->
   health modifier -> nameplate -> UUID map. Build-time `B.probe` for every engine member in section 12, including
   `getEnvironment(III)`.
3. `LevelDamage` (DamageEventSystem, Filter group, before ArmorDamageReduction).
4. `/mobs`, `/mobs inspect`, `/mobs set` (inspect first: it is the test tool).
5. Bridge `mob:fn:level`.
6. One registerSystem per class; the supplier and component classes are top-level (javassist limits). If registering a component fails
   under javassist, use the UUID map (UNVERIFIED which one works).
7. Build (`assembled ...jar`), `tools/ci/lint.py` 0 fails, a link check against the 0.7 jar, sonnet review, then the main session
   pins it in the SET.

**Stage 1.1:** `/mobs survey`, `tools.relevel`, `tools.strip`. Re-rate the scarcity column from real numbers and update the defaults.

**Stage 2 - rewards:**
- SkyySkills: gap XP rule including the party share, and `combat.levelBonus`.
- SkyyGear: `odds.levelShift`.
- SkyyMobs: bonus drop roll (after `DeathSystems$TickCorpseRemoval`, before `CorpseRemoval`, within 2 blocks so SkyyGear tags the gear),
  coins row, `mob:fn:band`.
- SkyyHud band line (optional).

**Stage 3 - elites and places:**
- Elites.
- Boss rows in `scale.role`.
- `mob:fn:setLevel`.
- `bands.area` admin boxes for the island chain.
- Shard scaling.
- Optional mob defence.

In-game tests for stage 1:
1. Server log `[SkyyMobs] 0.1 ready`, no WARN lines.
2. Drifting Plains: a skeleton shows `[Lv 1]`..`[Lv 3] Skeleton Fighter`. `/mobs inspect` says step 4, key `Zone1_Tier1.Plains_Smooth`.
3. Blue forest: mobs are Lv 8-10. `/mobs` shows "Lv 8-10 (Zone 1 - The Fens - Forest Azure)".
4. A Trork camp: `[Lv N] Trork Warrior`. inspect shows step 4 with a `*_Trork` row, or step 5 `Env_Zone1_Trork` (marker spawn).
5. A cave under the blue forest: Lv 8-10 (caves = ground above).
6. Kill a Lv 10 grizzly: about 34 Combat XP (169 max HP x 0.2). If it shows 25 (124 x 0.2), max health did not include the modifier.
7. Let a Lv 10 skeleton hit you with no armour: damage x1.18 against a Lv 1 skeleton of the same kind.
8. Walk away until the chunk unloads, come back: same level, health share kept.
9. `/mobs set 30` on a mob: the plate and health update.
10. A kweebec, a cow, a sheep: no plate.
11. A skeleton archer's arrow: scaled or not? (projectile source, UNVERIFIED)
12. Server Setup -> Mobs: change `scale.hp` to 0.1, reload the chunk: health follows. Change a biome band: only new spawns change.
13. A private island (SkyyIslands): mobs are Lv 1-3.

---

## 14. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Unpainted hand-built islands | every mob falls to the world or default band | paint with `/setenvironment` (4.7), `bands.world`, and stage 3 areas |
| Health modifiers saved with the mob | uninstalling SkyyMobs leaves mobs buffed forever (UNVERIFIED whether modifiers persist) | fixed key; `tools.strip` before uninstalling; documented in the mod's help text |
| Other mob-scaling mods installed (MmoMobScaling, EndlessLeveling, RPGLeveling are in UserData\Mods; none is in PACK.md) | stacked multipliers, fighting nameplates | at startup SkyyMobs WARNs when it sees a known mob-scaling plugin; the pack keeps only one |
| No colour on nameplates | plain text | the vanilla look is still met; the colour rows stay off |
| Ranged mob damage is not an `EntitySource` | archers and mages unscaled | test 11; if so, also match the projectile source's shooter |
| Overlay vs tile biome, base-biome argument order | wrong row for rivers and dunes | patterns + passThrough + region fallback rows |
| Kill XP pacing (section 7) | gear gates beyond Iron unreachable | question 7; SkyySkills rows |
| Balance: late mobs as bullet sponges | Zone 4 grind | 4% / 2% and caps (section 15); every number is a row |
| 0.7 instance world names unknown | shard bands will not match | env rows `Env_Portal_Goblin_*` work without them |
| javassist component registration | no per-mob component | UUID map fallback |

---

## 15. Self-critique (and the fixes, already applied above)

| # | Problem found in the first draft | Kind | Fix | Where |
|---|---|---|---|---|
| 1 | Research numbers 6% HP / 3% damage give Lv 60 x4.54: a Lv 60 Emberwulf would have 876 HP. Our gear already adds 1.5-2.5x player power by Zone 3-4 (SkyyGear full power at item level 40 plus the skill tree), so mobs would out-scale players | feel | 4% / 2% (Lv 60 x3.36 / x2.18) plus caps. Zone 2 is still a clear step (same-kind mobs about 2x) | 5 |
| 2 | Lookup put the environment first. On classic worlds the environment is coarser than the biome (`Env_Zone1_Plains` covers Tier 1 **and** Tier 3 plains), so the blue forest's Gorge plains would read Lv 1-3 | correctness | biome first on classic worlds; environment adds only its Bonus there, and is the band source elsewhere | 2.1, 4.6 |
| 3 | `BlockChunk.getEnvironment(Vector3d)` is removed in 0.7 | 0.7 | use `(int, int, int)` (in both versions) | 2.1, 12 |
| 4 | Level could "jump" after a reload when a role moved its leash point (a Lv 3 back as Lv 9) | feel | the saved nameplate is the save slot; the saved spawn env beats the leash on recompute | 2.3 |
| 5 | Maximizing health on every LOAD heals wounded mobs (run away, come back, full health). Not maximizing can leave health above max after a curve change | feel | SPAWN = full; LOAD = keep the health fraction | 5 |
| 6 | Party XP share (50% within 48 blocks) lets a Lv 40 friend power-level a newcomer on Lv 40 mobs | exploit | the stage 2 gap rule applies to each member's own skill, party share included | 5, 9 |
| 7 | AFK mob farms in the blue forest at night (Lv 8-10 void mobs) pay more XP and loot | exploit | XP, bonus drops and the rarity shift only on player kill credit (SkyySkills' rule), never on fall, lava or drowning deaths; bonus drop chance capped at 50%; watch in the beta | 5, 9 |
| 8 | Plates on every skeleton in a 5-skeleton group make clutter | feel | short format; `plate.mode` all / elite / off | 6 |
| 9 | Shared plates cannot say "too strong for you" | feel | absolute zone colour ladder; `/mobs` compares the band to your own weapon skill | 6 |
| 10 | 300 mobs loading at once (teleport into a big area) = 300 worldgen lookups in one tick | perf | per-chunk cache of the 2D result (cleared on config epoch); the env lookup is an array read | 13 |
| 11 | UUID map could leak if a removal is missed | perf | remove in `onEntityRemoved`; sweep on world unload | 2.3 |
| 12 | The survey over a big radius could stall the world thread | perf | 2,000 samples per tick, admin only | 10 |
| 13 | The damage filter runs on every hit in the game | perf | returns at once unless the attacker is a levelled NPC; one map read | 5 |
| 14 | Weapon-skill pacing makes gear gates beyond Iron unreachable from kills | balance | surfaced as a Skyy decision with SkyySkills options, not hidden in mob numbers | 7, 17 |
| 15 | The research bands (Zone 1 1-12, Zone 2 15-28, Zone 3 30-42) did not match Skyy's words ("slightly" higher in the blue forest, "a pretty big step" to Zone 2): the blue forest sat 9 levels above spawn but the step into Zone 2 was 3 levels (12 -> 15), and Zone 2 -> 3 only 2 (28 -> 30). On the plate a zone border looked smaller than a biome border | feel | every zone ends on a SkyyGear tier and every zone step is +5 levels: 1-10 (Copper 10), 15-25 (Iron 15 -> Cobalt 25), 30-40 (to Mithril 40), 45-60. The blue forest moves to 8-10. The gaps hold encounters, dungeons and elites | 0, 4, 7 |

Left as is on purpose: inside a zone the spread (Zone 1: 1-10) is still wider than one zone step, because vanilla's own region tiers
already grade each zone from its centre to its edge. Neighbouring biomes differ by 1-3 levels and their bands overlap (Fens plains 6-8
next to the blue forest 8-10). Crossing into the next zone always jumps at least 5 levels and brings stronger species.

---

## 16. UNVERIFIED (needs an in-game test or a build)

1. Colour markup in nameplate text (stage 0 test 1).
2. Whether world spawns follow a painted `/setenvironment` environment (stage 0 test 2).
3. Whether the Nameplate component saves with the mob (the level's save slot).
4. Whether EntityStatMap modifiers save with the mob (uninstall residue).
5. Whether SkyySkills' `getMax()` includes the MAX modifier (test 6).
6. Whether `ZoneBiomeResult.getBiome()` returns the overlay or the tile biome; the argument order of `biomePatternGenerator().getBiome`.
7. The argument order of `I18nModule.getMessage` for names.
8. Registering an ECS component through javassist (fallback: UUID map).
9. Whether ranged mob damage is an `EntitySource` with the shooter (test 11).
10. Whether marker / beacon spawns (Trork camps, encounters) carry `MIN_VALUE` as the environment, and the `Env` round trip after a reload.
11. Whether SkyyGear tags bonus drops as unidentified (stage 2).
12. 0.7 instance world names (shard and dungeon `bands.world` patterns).
13. The overlay area shares (the survey fills them in).

---

## 17. Questions for Skyy (recommended default in brackets)

1. **Scale and bands:** Lv 1-60 with Zone 1 = 1-10, Zone 2 = 15-25, Zone 3 = 30-40, Zone 4 = 45-60, each zone ending on a gear tier
   with a 5-level step to the next (the research draft was 1-12 / 15-28 / 30-42)? [yes]
2. **Blue forest:** top of Zone 1 at 8-10 alongside Autumn and Moss (draft, +1 "your pick"), or strict rarity (blue forest 7-9,
   below Autumn and Moss)? [draft: 8-10]
3. **Which mobs:** hostile only, or neutral fighters too (boar, Scarak)? Animals never. [hostile only]
4. **Numbers:** health +4% and damage +2% per level (lowered from the research's 6% / 3%, section 15 #1)? [4% / 2%]
5. **Mob armour:** none for now; an optional defence per level later so True Damage matters? [none]
6. **XP:** health-based XP now, then the stage 2 gap rule (+-5 free, -5% per level, floor 10%, party share included)? [yes, stage 2]
7. **Pacing:** weapon skill 25 (Cobalt) needs about 3M XP. Shorten the class weapon skill curve, add a level XP bonus, or raise XP
   per health? [a level XP bonus of 5% per level plus a playtest, then decide the curve]
8. **Drops:** +1% bonus drop chance per level (cap 50%) and better SkyyGear rarity (+2% per level on Unique+ weights) in stage 2?
   Coins per level? [yes / yes / no coins yet]
9. **Night:** extra levels for void mobs at night? [0]
10. **Nameplate:** `[Lv 9] Trork Warrior`, colour ladder white / yellow / gold / red / purple if the test works, on every levelled mob?
    [yes / yes / all]
11. **Spread:** random inside the band, or stronger species higher? [random]
12. **Island chain:** paint environments with `/setenvironment` plus a per-world band; private islands 1-3? [yes]
13. **Caves:** the band of the ground above? [yes]
14. **Elites (stage 3):** 3% chance, +3 levels, x2 health, x1.3 damage, "Elite" prefix, a guaranteed gear roll? [yes]
15. **Shards (0.7 raids):** band of the zone the portal opened in, +1 per void surge stage, or party-scaled? [decide when the beta is live]
16. **Mod name:** SkyyMobs? [yes]

---

## Sources

`research/Mob-Levels-Research.md` (all mod comparisons, web sources and appendix A engine facts), `research/PreRelease-Compat-Report.md`,
OPEN-QUESTIONS.md (SkyyGear material levels, mob level request), HANDOFF.md (raids / shards note 2026-09-30), docs/plans/SkyWynn-Decisions.md
(island chain, dungeons, raids), docs/plans/SkyyDungeons-Plan.md, `tools/CONFIG-CONTRACT.md`, `research/Vanilla-UI-Style-Guide.md` (colours),
`research/Overall-Level-Spec.md`, SkyySkills/build_skyyskills_0.4.8.py (KillSys, level curve, `skill:fn:level`),
SkyyGear/build_skyygear_0.1.2.py (`odds.mob`, `stat.levelFull`, `class:skill:`), SkyyIslands/build_skyyislands_0.5.4.py
(`island:owner:fn`), SkyyCoins 0.1.5 (`coins:fn:add`).

New read-only checks for this plan (release 0.6.8 and 0.7.0-pre.4, in memory, nothing extracted):
- Assets.zip:
  - `Server/World/Default/Zones/Zone3_*` and `Zone4_*` `Tile.*.json` (Weight, SizeModifier, Environment)
  - the `Custom.*.json` overlay names for Zones 1-2
  - `Server/NPC/Spawn/World/*` environment lists (Zone 3 / 4 threat tiers)
  - `Server/Environments/**` tags
  - role MaxHealth values
  - server.lang (`commands.environment.desc`)
  - pre-release: `Server/PortalTypes/Goblin_Breach.json`, `GameplayConfigs/PortalsGoblins.json`, `NPC/Spawn/Beacons/Portals/*`,
    `Environments/Unique/Env_Portal_Goblin_*`, `NPC/Roles/.../Skeleton_Elite.json`, `Item/Block/Spawners/Zone*_Encounters_Tier*`
- HytaleServer.jar:
  - a method/descriptor diff of the section 12 members
  - `BlockChunk.getEnvironment` bytecode (tools/dev/bcfull.py)
  - the `EnvironmentCommand` constant pool (`setenvironment`, `setenv`)
  - the command classes' constant pools (no vanilla `/mobs`)

> 2026-10-03 note (main session): for loot levels, `mob:fn:levelAt(world, x, y, z)` (research/Loot-Unid-Spec.md) replaces the `mob:fn:band` call of section 8; zone bands are the 2026-10-01 ones (1-20 / 20-30 / 30-45 / 45-60).
