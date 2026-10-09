# Zone archipelagos - worldgen spec (SkyyWorldGen 0.3+)

Cloud draft, 2026-10-09. Paper design: nothing built, nothing run against game files. Turns Skyy's island-layout lock into node-level
HytaleGenerator plans for Zones 1-5, the gap between zones, the squashed cave bands down to the lava caverns, the travel points and a
staged build plan. Every number is a PLACEHOLDER that the build script writes from ONE Python table (as `SkyyWorldGen/build_skyyworldgen_0.1.py`
already does); arithmetic was done in python (method shown where it matters). Inputs read: `docs/answered/world.md` (all),
`research/SkyyWorldGen-Plan.md` (all, incl. the "Island layout" section at the end), `research/cloud/WorldGen-Stage-2-Draft.md`,
`research/cloud/Zone-Islands-Layout.md`, `research/cloud/Zone-1-Town-Layout.md`, `research/cloud/Starter-Shards-Plan-2.md`,
`research/Mods-Folder-Survey.md` (Welkin section), `research/Zone-1-Town-Build-Plan.md` (the SkyyWorldGen 0.2 line), `research/cloud/Dragon-Quest-Spec.md`
(flight rules), `research/cloud/Zone-4-5-Materials.md`, and `SkyyWorldGen/build_skyyworldgen_0.1.py` + `SkyyWorldGen/test_skyyworldgen_0.1.py` (read only).

## Decisions followed (not re-decided) - `docs/answered/world.md`

| Line | Decision | What it means here |
|---|---|---|
| 56 | **LOCKED 2026-10-09 (island layout)**: each zone = a few islands joined by land necks / arches / built bridges; zones distinct and far apart (dragon or portal only); deep caves down to the vanilla lava caverns, vertically squashed | the whole spec |
| 55 | IDEA 2026-10-09: Welkin as a technique source | technique only, own numbers, no files (section 3.1) |
| 17 | LOCKED 2026-10-03 stage 2: random shape, vanilla features kept, trend upward to a mountain in the middle, at least 3x the size, caves inside, biomes random like vanilla (outside-in = a tendency) | each archipelago climbs to a central summit isle; total land per zone about 3x the old medium island (section 4) |
| 18 | LOCKED 2026-10-03: all zone islands in ONE world; see Zone 2 from Zone 1; guardian + portal unlock must still matter | one world `skywynn`; the "see it" half clashes with the newer line 56 - Question 1 |
| 12 | R8 LOCKED: Zone 5 = the dinosaur caves UNDER Zone 4, Lv 60-75, dragon boss at 75 | Zone 5 = the deep cave layer of the Zone 4 summit isle (section 5.5) |
| 27-30 | LOCKED 2026-10-01: summit portal opens after the guardian; a town with a warp at each landing, built around a vanilla temple; outpost per biome with a warp; bands Z1 1-20, Z2 20-30, Z3 30-45, Z4 45-60 | travel points (section 7), level bands per island (section 5) |
| 52-54 | LOCKED 2026-10-06 / 10-08: the Zone 1 town v2 plan, vanilla temple at its centre, door to the sea, spawn at the foot of its causeway | the Zone 1 arrival isle carries that town on its south coast, inland = north toward the mountain |
| 19, 13 | LOCKED: starter shards (repair bridge, then build) stay SkyyIslands instances | untouched; shard 3's portal lands in the Zone 1 town |
| 15 | ANSWERED: island deaths keep items | unchanged (0.1 lines 22-25: the template's `Death` override) |

Never edit: Welkin's or vanilla's files. We describe techniques and choose our own numbers (section 3.1 says why each differs).

---

## 0. Plain words (for Skyy)

- Each zone becomes a **cluster of 4-6 islands** around one tall **summit isle** (the zone's mountain, guardian and summit portal).
  The outer islands are each one biome family (birch woods, gorge mountains, swamp ...) and link to the summit isle by a **land neck**
  (wide, walkable land), a **rock arch** (a thin natural stone span over the void) or a **built bridge** (a gap our town tool fills).
- Zones sit **1,100 blocks apart** across open void: too far to glide or bridge. Travel between zones = summit portal, town warp, or
  (much later) your dragon.
- Under every big island: **three cave layers** - upper tunnels, deep caves, and **lava caverns with a lava sea** - squeezed to about
  two thirds of their natural height, so islands stay about 110-215 blocks tall (the Zone 4 caldera isle 218, because Zone 5 lives inside it) instead of 250+.
- Zone 5 is the extra-deep cave layer under the Zone 4 caldera (jungle caverns, then the lava lake and the dragon's lair).
- Built in small steps: first a throwaway proof world (two islands, one neck, one arch), then caves, then Zone 1, then one zone per version.

---

## 1. What the repo already proves (SkyyWorldGen 0.1, deployed + VERIFIED in game 2026-10-03, `docs/log/2026-10.md` lines 43-49)

Only these node types and JSON shapes count as proven: they are emitted by `SkyyWorldGen/build_skyyworldgen_0.1.py`, generated
offline by its harness (`SkyyWorldGen/test_skyyworldgen_0.1.py` lines 18-24: section C column survey, G2 landing check) and seen in game.

| Piece | Proven shape | 0.1 lines |
|---|---|---|
| Geometry table -> JSON + Java from one Python dict | `GEOMETRY` (radius, Base, rings, curves, seeds, export names) | 154-178, asserts 209-226 |
| 2D distance | `Exported` (`SingleInstance` true) -> `YOverride 0` -> `Cache` (Capacity 3) -> `FastGradientWarp` (`WarpScale`, `WarpPersistence`, `WarpLacunarity`, `WarpOctaves`, `WarpFactor`, `Seed`) -> `YOverride 0` -> `Distance` with a `Manual` curve | 229-237 |
| Curves | `{"Type":"Manual","Points":[{"In","Out"}]}` | 240-241 |
| 3D island | `Min` of top and bottom `Sum`s; each `Sum` = `CurveMapper` on `BaseHeight` (`BaseHeightName` "Base", `Distance` true) + `CurveMapper` on the imported distance + `Normalizer` of `SimplexNoise2D` (top) / `SimplexNoise3D` with `ScaleXZ` / `ScaleY` (underside); density unit = blocks / K (K 12) | 244-262 |
| World structure | `NoiseRange`, `Biomes` [{Biome, Min, Max}] with ranges up to 100,000, `DefaultBiome`, `DefaultTransitionDistance`, `MaxBiomeEdgeDistance`, `Density` = `Imported`, `SpawnPositions` `List`, `Framework` `DecimalConstants` (Base / Water / Bedrock) | 265-273 |
| Void biome | `DAOTerrain` + `Constant` 0 density, `Constant` material `{"Solid":"Empty"}`, `Constant` environment, `Constant` tint | 276-280 |
| Land biome | `DAOTerrain` + `Imported` island; `Solidity` material with a `Queue` (`SpaceAndDepth` DEPTH_INTO_FLOOR -> `ConstantThickness` layers, then `Constant`) and an `Empty` queue; `Constant` environment; `DensityDelimited` tint over a `Normalizer`ed `SimplexNoise2D` with `Delimiters` / `Range` | 283-300 |
| Props | `Mesh2D` positions (`Mesh` generator, `Jitter`, `ScaleX/Y/Z`, `Seed`) -> `Constant` assignment -> `Prefab` (`WeightedPrefabPaths`, `LoadEntities`, `Random` directionality with a `Floor` pattern of `BlockSet`s, `ColumnLinear` scanner with `MaxY` / `MinY` relative to Base, `TopDownOrder`, `ResultCap`) | 301-311 |
| Instance template | `WorldGen` {Type HytaleGenerator, WorldStructure, SeedOverride}, `SpawnProvider`, `Death` override, kept world (no removal conditions) | 315-346 |
| Build-time id checks against `Assets.zip` (read only) | our ids never clash with vanilla; every vanilla id referenced exists | 366-397 |
| Plugin mirror of the geometry | `WgZones` generated from GEOMETRY; ring by plain (unwarped) distance | 614-680 (ring: 675) |

**Not proven by the repo (UNVERIFIED until a harness or game test):** `Max`, `Offset`, `Anchor`, `Clamp`, `PositionsCellNoise`,
`Selector` / `Switch`, `Mix`, `YSampled`, any cave technique, fluid materials (lava, water) in a material provider, a material or
environment provider delimited by a density, cave environments, custom environments + spawn files, prefab props on cave floors.
(`research/SkyyWorldGen-Plan.md` section 1 lists several as existing asset types from the jar's class list; their JSON keys are unseen.)

---

## 2. The world frame

| Item | Value | Why |
|---|---|---|
| World | ONE world `skywynn` (new; `skywynn_z1` from 0.1 stays until Skyy says delete) | line 18 lock; a new name avoids a seam with 0.1's saved chunks (Plan risk "Updating worldgen") |
| Base | 140 for the whole world (`Framework` is one per structure) | same as 0.1, so the proven BaseHeight maths and harness windows carry over |
| Height | blocks y 0-319, void kill at y -32 (Plan section 1, VERIFIED there) | every number below stays inside y 8-240 |
| Zone hull | the circle that holds all of one zone's islands: Z1 1,700, Z2 1,990, Z3 1,910, Z4 2,180 blocks radius | from the island tables (section 5) |
| **Gap between zones** | **1,100 blocks hull edge to hull edge** (neighbours); non-neighbours 4,600-6,100 | see below |
| Zone centres (= summit isle centres) | Z1 (0, 0), Z2 (4,790, 0), Z3 (7,290, 4,331), Z4 (4,695, 8,826); Zone 5 under Z4 | an arc (0, 60, 120 degrees per step), each centre = previous + hull + 1,100 + hull |
| World extent used | x -1,700 .. 9,200, z -1,990 .. 11,006 (mostly void) | python, from the centres and hulls |

**Why 1,100** (python): the highest coast-side launch point is a coastal hill at about y 190; a 4:1 glide (the ratio the Layout draft
assumed; any vanilla or modded glider is UNVERIFIED) from y 190 down to the y -32 kill plane covers (190 + 32) x 4 = **888** blocks.
1,100 = 888 x 1.24, a 24% margin, rounded to about 34 chunks of 32. Launching from a summit gains nothing: the crowns are 600-800 blocks
inland. Walking or block-bridging 1,100 blocks of void is out of reach even before the no-build band (section 7.3). Dragons cross it
in about 55-75 s at an assumed 15-20 blocks/s (UNVERIFIED), so the dragon wing-stamina setting must allow at least 90 s
(`research/cloud/Dragon-Quest-Spec.md` "Flight rules").
**Cost of 1,100:** the next zone is NOT visible from the facing rim at a normal view distance (the Layout draft's ~384-block view radius is
UNVERIFIED). The older lock (line 18) wanted it visible; the newer lock (line 56) wants "far enough apart you need dragons or portals".
Question 1 offers the trade.

---

## 3. The archipelago recipe (one recipe, every zone)

### 3.1 Technique (own words) and how ours differs from Welkin

| Welkin idea (`research/Mods-Folder-Survey.md`) | Ours | Why ours differs |
|---|---|---|
| island cells picked at RUN time from a jittered cell grid (~470 grid, jitter 90) | island centres picked at BUILD time by our Python table (a jittered hand layout around the summit isle, seeds per zone), written as constants | the plugin must know every island exactly: town spot, summit portal, guardian, outposts, `wg:fn:ring` levels, no-build band. A runtime cell grid would put the town somewhere unknown |
| one ~80-block gradient warp on the outline | `FastGradientWarp` **40** (`WarpScale` 300) per island | big islands (R 280-800) get bays and headlands of about 5-14% of R; 80 would swallow our 40-110-block joins. 0.1 used 24 on R 384 (line 168) |
| Simplex "tops" faded by distance | the 0.1 top curve (mountain trend) + a shared `SimplexNoise2D` "bumps" field capped by a per-island fade (`Min(bumps, fade)`) | `Min` + `Normalizer` + `CurveMapper` are proven nodes; a multiply node is not |
| noise-shaped sloped underside | a per-island **keel**: flat at its lowest y under the inner 75% of R, then a steep skirt up to the rim (smoothstep from u 0.75 to 1.0), + the proven 0.1 `SimplexNoise3D` underside term | keeps the cave shell guard computable (section 6.3) |
| islands are separate blobs | islands + **join beads** (necks, arches, bridgeheads) | Skyy's "ways they connect" |

### 3.2 The fields (everything per island is 2D and cached per column)

Per island i (centre cx, cz, radius R_i), u = d_i / R_i:

| Export (prefix `SkyWynn-W-`) | Dim | Built from | Value |
|---|---|---|---|
| `D-<id>` (one per island) | 2D | `YOverride 0` -> `Cache` -> `FastGradientWarp` (40 / 300, seed `SkyWynn-<id>`) -> **offset** -> `Distance` (the 0.1 chain, lines 229-237, plus the offset) | warped distance from the island centre, blocks |
| `Top2D` | 2D | `Max` over islands of `CurveMapper(D-i -> top_i(u))` and over beads of `CurveMapper(bead distance -> bead top)`; outside an island the curve drops to -1000 | ground height above Base, blocks |
| `Bot2D` | 2D | the same with `Min` and bottom curves (+1000 outside) | underside height above Base, blocks (negative = below) |
| `Fade2D` | 2D | `Max` over islands of `CurveMapper(D-i -> 0 at the rim, hill amplitude in the middle)` | hill cap |
| `Code2D` (the WorldStructure density) | 2D | `Max` over islands of `Sum(Constant(base_i), CurveMapper(D-i -> 0..90 by u, -100000 beyond R_i + 24))` + one shared `Normalizer(SimplexNoise2D)` +-10 for patchy borders; beads carry the lower island's rim code | biome code: zone x 1000 + island x 100 + band (0-99); void < 0 |
| `LavaOK2D` | 2D | `Max` over islands with lava caverns of `CurveMapper(D-i -> 1 inside 0.7 R_i, -1 beyond 0.72 R_i)` | where lava caverns may exist |
| `Land` | 3D | section 3.4 | the terrain every land biome imports |

Why 2D first: the 3D density then costs about what 0.1 costs (two BaseHeight curves, one 3D noise, the cave noise), no matter how
many islands exist. All per-island work happens once per column inside `Cache` (0.1 pattern).

### 3.3 Joins

| Join | Shape | Numbers (ours) | Notes |
|---|---|---|---|
| **Land neck** | a chain of round "beads" from 20 blocks inside rim A to 20 blocks inside rim B, spacing 0.7 x bead radius, each bead unwarped, top = the straight ramp between the two rim heights, bottom = top - 26 | bead radius 30 (neck 55-65 wide after the bead overlap); spans 60-70 blocks rim to rim; 6-7 beads | the main roads. Gets the lower island's rim biome. Caves never carve in a neck (shell guard: too thin) |
| **Rock arch** | the same chain with bead radius 12 (about 20-24 wide), top = ramp + an upward bow of +6 at mid-span, bottom = top - 10 at mid-span, top - 22 at the ends | spans 80-110; 16-19 beads | a thin stone span with void under it. Material: stone surface (no grass), so the arch reads as rock. Guard rail: none (it is a feature); 20+ wide so it is walkable |
| **Built bridge** | two **bridgehead** beads (radius 14, flat top at rim height) jutting 16 blocks out from each rim, leaving an exact open span between them | open span 32-40 blocks; **always along the x or z axis** | SkyyTowns stamps the bridge piece (rotations are 90-degree only, VERIFIED in `research/Zone-1-Town-Build-Plan.md`); bridgeheads are unwarped so the span is exact |

Join beads are unwarped on purpose: the island outline wobbles by up to 40 blocks, which could close a 40-block span or tear a neck.

### 3.4 Node-level JSON plans

Shapes marked `"$Todo"` use a node whose keys the repo has not proven (section 1). Everything else copies the proven 0.1 shapes.

**a) One island's distance** (per island; 0.1 lines 229-237 + an offset):
```json
{"Type":"Exported","ExportAs":"SkyWynn-W-D-1A","SingleInstance":true,"Inputs":[
 {"Type":"YOverride","Value":0,"Inputs":[{"Type":"Cache","Capacity":3,"Inputs":[
  {"Type":"FastGradientWarp","WarpScale":300,"WarpPersistence":0.5,"WarpLacunarity":2,"WarpOctaves":2,"WarpFactor":40,"Seed":"SkyWynn-1A","Inputs":[
   {"Type":"Offset","$Todo":"move the sample point by (-cx, 0, -cz) = (0, 0, -1060); keys UNVERIFIED (or Anchor)","Inputs":[
    {"Type":"YOverride","Value":0,"Inputs":[{"Type":"Distance","Curve":{"Type":"Manual","Points":[{"In":0,"Out":0},{"In":8000,"Out":8000}]}}]}]}]}]}]}]}
```

**b) The 2D height fields** (top shown; bottom is the same with `Min` and +1000 outside):
```json
{"Type":"Exported","ExportAs":"SkyWynn-W-Top2D","SingleInstance":true,"Inputs":[
 {"Type":"YOverride","Value":0,"Inputs":[{"Type":"Cache","Capacity":3,"Inputs":[
  {"Type":"Max","$Todo":"keys UNVERIFIED; fallback = negate (Normalizer -1..1 -> 1..-1) + Min + negate","Inputs":[
   {"Type":"CurveMapper","Curve":{"Type":"Manual","Points":"top_1A(u) in blocks, then R+8 -> -1000"},"Inputs":[{"Type":"Imported","Name":"SkyWynn-W-D-1A"}]},
   {"Type":"CurveMapper","Curve":"...","Inputs":[{"Type":"Imported","Name":"SkyWynn-W-D-1E"}]},
   {"Type":"CurveMapper","Curve":"bead: 0..r -> bead top, r+6 -> -1000","Inputs":["bead distance (offset Distance, no warp)"]}]}]}]}]}
```

**c) The 3D land** (the 0.1 `Min(top_sum, bottom_sum)` of lines 244-262, with the per-island distance curve replaced by the 2D fields,
then the caves of section 6):
```json
{"Type":"Exported","ExportAs":"SkyWynn-W-Land","SingleInstance":true,"Inputs":[{"Type":"Min","Inputs":[
 {"Type":"Sum","Inputs":[
  {"Type":"CurveMapper","Curve":"BaseHeight -400..400 -> +33.3..-33.3 (= -(y-Base)/K, K 12; 0.1 line 250)","Inputs":[{"Type":"BaseHeight","BaseHeightName":"Base","Distance":true}]},
  {"Type":"Normalizer","FromMin":-1000,"FromMax":1000,"ToMin":-83.3,"ToMax":83.3,"Inputs":[{"Type":"Imported","Name":"SkyWynn-W-Top2D"}]},
  {"Type":"Min","Inputs":[
   {"Type":"Normalizer","FromMin":-1,"FromMax":1,"ToMin":0,"ToMax":2.5,"Inputs":[{"Type":"SimplexNoise2D","Scale":90,"Octaves":3,"Lacunarity":2,"Persistence":0.5,"Seed":"SkyWynn-W-Bumps"}]},
   {"Type":"Imported","Name":"SkyWynn-W-Fade2D"}]}]},
 {"Type":"Sum","Inputs":[
  {"Type":"CurveMapper","Curve":"BaseHeight -400..400 -> -33.3..+33.3","Inputs":[{"Type":"BaseHeight","BaseHeightName":"Base","Distance":true}]},
  {"Type":"Normalizer","FromMin":-1000,"FromMax":1000,"ToMin":83.3,"ToMax":-83.3,"Inputs":[{"Type":"Imported","Name":"SkyWynn-W-Bot2D"}]},
  {"Type":"Normalizer","FromMin":-1,"FromMax":1,"ToMin":-0.6,"ToMax":0.6,"Inputs":[{"Type":"SimplexNoise3D","ScaleXZ":40,"ScaleY":20,"Octaves":2,"Lacunarity":2,"Persistence":0.5,"Seed":"SkyWynn-W-Under"}]}]},
 {"Type":"Imported","Name":"SkyWynn-W-Caves"}]}]}
```
(`Normalizer` of a 2D field into blocks/K reuses the proven node; whether it clamps outside From is UNVERIFIED, so the +-1000 sentinels
sit exactly on From.) Bumps: 0 to 2.5 density = 0 to 30 blocks, capped by the fade (0 at the rim).

**d) World structure** (0.1 lines 265-273, ranges are codes):
```json
{"Type":"NoiseRange","DefaultBiome":"SkyWynn_Void","DefaultTransitionDistance":16,"MaxBiomeEdgeDistance":16,
 "Density":{"Type":"Imported","Name":"SkyWynn-W-Code2D"},
 "Biomes":[{"Biome":"SkyWynn_Void","Min":-1000000,"Max":0},
           {"Biome":"SkyWynn_Z1_1A_Shore","Min":1100,"Max":1130},{"Biome":"SkyWynn_Z1_1A_Plains","Min":1130,"Max":1170},"... one row per look, section 5"],
 "SpawnPositions":{"Type":"List","Positions":[{"X":0.5,"Y":"town spawn Y","Z":1365.5}]},
 "Framework":[{"Type":"DecimalConstants","Entries":[{"Name":"Base","Value":140},{"Name":"Water","Value":140},{"Name":"Bedrock","Value":0}]}]}
```

**e) Land biome** = the 0.1 `biome_land` (lines 283-312) per look: `Terrain` imports `SkyWynn-W-Land`; material layers per look (grass,
sand, snow, ash); arch beads get a stone-only look; `EnvironmentProvider` becomes depth-banded in step 0.4 (section 6.4); props as 0.1.

---

## 4. Size target

Line 17 says "at least 3x the size". The Layout draft read that as 3x the old medium island's AREA (its Question 1, still open). This spec
keeps that target as the **total land of each zone's islands** (python: sum of pi x R^2, before the outline warp):

| Zone | Islands | Land (M blocks^2) | x old medium | Layout single island |
|---|---|---|---|---|
| 1 | 5 | 3.82 | 2.97 | 3.87 |
| 2 | 4 | 4.85 | 3.11 | 4.68 |
| 3 | 6 | 5.54 | 2.99 | 5.56 |
| 4 | 4 (+ Zone 5 below) | 5.87 | 2.70 | 6.51 |

Zone 4 sits a little under because Zone 5's caverns add about 1.45 M blocks^2 of cave floor under it.

---

## 5. Per-zone plans

Coordinates are blocks from the zone centre (x east, z south; angle 0 = east, 90 = south). "Span" = rim-to-rim distance of a join.
Heights are absolute y (Base 140). Rim / peak = ground height at the coast / at the island's highest point; "Under" = the lowest point
of the underside (the flat keel under the inner 75% of R; it rises steeply to the rim outside that). Lava islands keep the keel at y 30 or lower: lava floor y 44 - 12-block shell = 32. Bands come from `research/SkyyWorldGen-Plan.md` 4.5 (Zone 1) and
`research/cloud/WorldGen-Stage-2-Draft.md` section 2 (Zones 2-5); inside an island the level follows the Layout 3.1 blend
(65% distance from the coast, 25% biome tier, 10% noise). Unlinked island pairs are at least 124 blocks apart after the outline warp
(nominal gap minus 2 x 40), so they can only be joined by a player-built bridge (allowed inside a zone, section 7.3).

### 5.1 Zone 1 - Emerald Wilds (Lv 1-20), hull 1,700

| Id | Island | Centre | R | Join to 1E | Span | Biome looks (vanilla keys) | Lv | Rim / peak / under y | Caves |
|---|---|---|---|---|---|---|---|---|---|
| 1A | Arrival Isle (town) | (0, 1,060) | 400 | **neck** (main road north) | 60 | Plains_Spawn shore, Plains_Smooth, Plains_Birch | 1-6 | 146 / 172 / 58 | upper + deep (no lava near the town) |
| 1B | Birchwood | (-1,109, -404) | 500 | **arch** | 80 | Forest_Birch, Forest_Flower, Forest_Aspen (Kweebec village) | 5-9 | 150 / 184 / 30 | all three |
| 1C | Gorgeback | (1,109, -404) | 520 | **neck** | 60 | Mountain_Tier1/2 + Trork camps, Plains_Gorge, Forest_Gully | 6-12 | 152 / 196 / 30 | all three (iron) |
| 1D | Fenmoss | (0, -1,060) | 420 | **bridge** (z axis) | 40 | Forest_Swamp, Forest_Autumn, Forest_Moss, Plains_Gorge T3 | 11-15 | 148 / 180 / 50 | upper + deep |
| 1E | Azure Crown (summit isle) | (0, 0) | 600 | - | - | foothills Plains_Tallgrass (rim) -> Mountain_Tier3 slopes -> **Forest_Azure crown** | rim 6-10 -> crown 14-18; guardian 19-20 | 156 / 214 / 28 | all three |

Codes: 1A 1100-1199, 1B 1200, 1C 1300, 1D 1400, 1E 1500 (band 0-35 foothills, 35-65 slopes, 65-99 Azure). The town (Zone-1 town v2,
270 x 230 blocks) sits on 1A's south coast: temple at (0, 1,365), coast 85-101 blocks south of it, inland = north = toward the crown
(matches `research/cloud/Zone-1-Town-Layout.md` section 3). Temple to crown: 1,365 blocks = 248 s walking (was 185 s on the single
island; outposts and warps cover it). The Fenmoss bridge is the only way onto the hardest outer island without building.

### 5.2 Zone 2 - Howling Sands (Lv 20-30), hull 1,990

| Id | Island | Centre | R | Join to 2D | Span | Biome looks | Lv | Rim / peak / under y | Caves |
|---|---|---|---|---|---|---|---|---|---|
| 2A | Steppe Landing (town) | (-1,390, 0) | 600 | **arch** (long sandstone arch) | 110 | Savannah_Forest / Plains / Boab / Rock, Mudflats, Plateau overlay | 20-23 | 144 / 166 / 52 | upper + deep |
| 2B | Scrubreach | (675, 1,169) | 600 | **neck** | 70 | Scrub_Bushland, tar pits | 22-25 | 146 / 176 / 30 | all three |
| 2C | Red Dunes | (690, -1,195) | 600 | **arch** | 100 | Desert_Oasis / Rock / Springs / Red / Hotsprings, Plateau_Desert | 24-27 | 148 / 190 / 30 | all three (Cobalt deep) |
| 2D | Mushroom Mesa (summit isle) | (0, 0) | 680 | - | - | Desert_Barren rim -> Desert_Mushroom, Desert_Oasis_Hidden crown | rim 23-26 -> crown 27-29; guardian 30 | 150 / 204 / 28 | all three |

No built bridge in Zone 2 (desert = arches). The two arches are the zone's landmark.

### 5.3 Zone 3 - Whisperfrost Frontiers (Lv 30-45), hull 1,910 (most biomes, most islands)

| Id | Island | Centre | R | Join to 3E | Span | Biome looks | Lv | Rim / peak / under y | Caves |
|---|---|---|---|---|---|---|---|---|---|
| 3A | Redwood Landing (town) | (-1,320, 0) | 540 | **neck** | 60 | Forest_Redwood (Kweebec villages), Plains_Shire | 30-32 | 150 / 182 / 48 | upper + deep |
| 3B | Fir Tundra | (-234, 1,329) | 540 | **arch** | 90 | Forest_Fir, Forest_Tundra, Mountain T1 | 32-34 | 152 / 196 / 30 | all three |
| 3F | Hotspring Shelf | (-764, -764) | 280 | **arch** | 80 | Plains_Hotsprings, hot caves (Adamantite) | 32-35 | 150 / 170 / 60 | upper + deep (hot caves) |
| 3C | Cedar Reach | (1,269, 462) | 560 | **neck** | 70 | Forest_Cedar, Forest_Cedar_Mixed | 36-38 | 154 / 200 / 30 | all three |
| 3D | Frozen Plains | (0, -1,284) | 520 | **bridge** (z axis) | 44 | Plains_Frozen, Plains_Tundra, Forest_Frozen, Forest_Frozen_Light, Plains_Frozen_Frost | 37-43 | 156 / 206 / 30 | all three |
| 3E | Everfrost Peak (summit isle) | (0, 0) | 720 | - | - | Mountain T2 rim -> Mountain T3 glacial crown, Outlander village (+2 env) | rim 33-37 -> crown 41-44; guardian 45 | 160 / 240 / 26 | all three (Mithril pocket near the crown) |

3F sits 124-125 blocks from 3A and 3D (python): the classic "build your own bridge" shortcut, as Skyy allowed.

### 5.4 Zone 4 - Devastated Lands (Lv 45-60), hull 2,180

| Id | Island | Centre | R | Join to 4D | Span | Biome looks | Lv | Rim / peak / under y | Caves |
|---|---|---|---|---|---|---|---|---|---|
| 4A | Cinder Landing (town) | (-1,510, 0) | 640 | **neck** | 70 | Wastes_Grasslands | 45-47 | 148 / 172 / 50 | upper + deep |
| 4B | Geyser Wastes | (990, 1,180) | 640 | **arch** (basalt) | 100 | Wastes_Geysers, Forest_Ghost, Desert_Dunes, Forest_Swamp Z4 (needs `Env_Zone4_Forests` or our spawn file: Plan 4.4 gap) | 48-50 | 150 / 190 / 30 | all three |
| 4C | Ashfall | (0, -1,480) | 640 | **bridge** (z axis) | 40 | Desert_Ash, Wastes_Ash, Wastes_Lava | 53-57 | 152 / 198 / 30 | all three |
| 4D | Caldera (summit isle) | (0, 0) | 800 | - | - | Forest_Burned, Forest_Roots slopes -> caldera bowl | rim 50-53 -> caldera 58-60; guardian 60 | 156 / caldera rim 226, floor 196 / **8** | Zone 4 upper band only, then Zone 5 |

### 5.5 Zone 5 - Dinosaur Caves (Lv 60-75), under 4D

| Layer | y (absolute) | Extent | Content | Lv |
|---|---|---|---|---|
| Echoing Maw shaft | caldera floor 196 -> 140 | a carved cylinder, radius 14, at 4D's centre | the descent (stairs / ledges prefab) + the Zone 5 portal pad at the top | - |
| Egg Desk cavern (town) | 112-140 | one big cavern, about 120 x 90, under the shaft | Zone 5 town + warp | safe |
| Jungle caverns | 60-150 | 4D inner 85% (radius 680, about 1.45 M blocks^2 of floor) | tall caverns (24-40 high), light shafts to the surface, jungle / Crystalwood props, fossil pits | 60-65 outer, 65-70 middle |
| Lava lake + dragon lair | 20-60, lava sea at y 30 | inner 50% (radius 400) | the lava caverns of Zone 5, Drakonite, the lair arena (no ore inside) | 70-75, dragon 75 |
| Shell | 8-20 | - | solid rock, never carved (shell guard) | - |

Zone 5 is under 4D only (the old draft had 2.35 M blocks^2 under "Z4's inner 60%"; ours is 1.45 M). Option: a deep root tunnel under
the 4A neck adds more (Question 5). Biomes are chosen per column, so Zone 5 cannot have its own biome rows: it changes by depth through
materials, environment bands and floor props (section 6.4).

---

## 6. Caves: squashed bands down to the lava caverns

### 6.1 Bands (Zones 1-4 surface islands)

| Band | y (absolute) | Thickness under a y 150 rim | Natural height (our reference) | What |
|---|---|---|---|---|
| 1 Upper caves | ground -6 .. 110 | 40 | 60 | worm tunnels + small rooms; entrances on slopes and cliff bands; the island's main ore tier |
| 2 Deep caves | 110 .. 76 | 34 | 50 | wider tunnels, mid caverns; the next ore tier |
| 3 Lava caverns | 76 .. 44; **lava sea surface y 52**, cavern floors y 44-48 | 32 | 45 | big flat caverns, lava lakes, basalt / magma rock |
| Shell | >= 12 blocks above the underside | - | - | never carved |

**Squash factor (python):** natural reference 60 + 50 + 45 = 155 blocks from a rim surface to the lava floor; ours 40 + 34 + 32 = 106,
rounded from 104 (150 -> 46) = **x0.67**. Inside the bands the cave noise uses `ScaleY` = **0.6 x ScaleXZ**, so caverns are about 1.7x
wider than tall: deep, but the island stays short. The reference heights are our own design numbers, not vanilla's (vanilla's real
cave and lava depths are a local check).

Who gets which bands: band 3 only on islands with R >= 500 and only where `LavaOK2D` is positive (inside 0.7 R, where the keel is flat, so the 12-block shell always fits), so lava never sits
near a cliff face. Arrival isles (towns) get bands 1-2 only. Under a summit crown the column is taller, so band 1 is thicker there
(the crown's own tunnels), bands 2-3 keep their y.

Zone 4 / 5 column under 4D: Zone 4 upper caves ground .. 150, Zone 5 jungle caverns 150 .. 60 (`ScaleY` 0.8 x for taller caverns),
lava caverns 60 .. 20 with the lava sea at y 30, shell 8 .. 20. Island height there: crown rim 226 to underside 8 = 218 blocks,
the tallest thing in the world, on purpose (it holds a whole zone).

### 6.2 Cave nodes (own numbers; UNVERIFIED technique until 0.4's harness)

| Part | Nodes (proven ones in plain text) | Numbers |
|---|---|---|
| Worm tunnels | two `SimplexNoise3D` fields, each folded to its absolute value with a `CurveMapper` (-1 -> 1, 0 -> 0, 1 -> 1); tunnel where BOTH are under a threshold (`Max` of the two, or negate + `Min`) | `ScaleXZ` 64, `ScaleY` 38, threshold 0.07 (tunnels about 4-7 wide) |
| Caverns | one `SimplexNoise3D`; cavern where it is over a threshold that depends on the band (a `CurveMapper` of BaseHeight added to it) | `ScaleXZ` 96, `ScaleY` 58; threshold 0.62 in band 2, 0.45 in band 3 (bigger), never in band 1 |
| Band gate | `CurveMapper` on BaseHeight: +10 above ground - 6 (no carving at the very surface except entrance zones), 0 inside the bands, +10 below y 44 | numbers above |
| Shell guard | `Sum(BaseHeight curve, -Bot2D)` = height above the underside, through a `CurveMapper`: +10 when under 12 blocks, 0 above 16 | 12 / 16 |
| Lava gate | `LavaOK2D` < 0 adds +10 to the cavern term below y 76 | 0.7 R |
| Result | `SkyWynn-W-Caves` = positive (solid) except inside a tunnel or cavern; `Land` takes `Min` with it | - |
| Entrances | where the band gate is relaxed by a sparse `SimplexNoise2D` (about 1 entrance per 150 x 150 blocks, on slopes) | - |

### 6.3 Lava and the void

The danger: a biome's `Empty` material queue fills every empty voxel of the column, including the open void UNDER the island, so a
naive "lava below y 52" makes lava pillars under every island. Plan, in order of preference (all UNVERIFIED):
1. `Empty` queue = lava fluid only where y < 52 AND the voxel is above the underside (`Bot2D`) - needs a density-delimited material
   provider and the fluid material syntax.
2. If 1 is impossible: no fluid in the generator; lava-lake **prefab props** placed on band-3 cave floors (`Floor` pattern, `ColumnLinear`
   scanner with `MinY` / `MaxY` around y 44-52 relative to Base - the 0.1 prop shape).
3. Last resort: a plugin pass that places lava source blocks in generated band-3 cavern floors on chunk load (cost + engine hook UNVERIFIED).
Either way the shell guard keeps 12+ blocks of rock between any lava and the underside, so nothing pours into the void.

### 6.4 Depth-banded environments (mobs follow the environment)

`EnvironmentProvider` `DensityDelimited` on BaseHeight (the 0.1 tint delimiter shape, untested for environments): surface env above
band 1; the zone's vanilla cave env in bands 1-2 (`Env_Zone1_Caves_*` style ids, UNVERIFIED); a volcanic cave env in band 3; Zone 5 =
our own `Env_SkyWynn_Z5_Jungle` / `Env_SkyWynn_Z5_Lair` with our own spawn files (Plan T6). SkyyMobs' lookup is 2D (x, z), so a cave mob
takes its island band; Zone 5 needs a depth rule in `wg:fn:ring` (y below 150 under 4D = Zone 5 band, section 8).

---

## 7. Travel points

### 7.1 Per zone (world coordinates; y = ground, set by the harness)

| Zone | Town + temple (arrival, warp, respawn, return portal) | Summit portal + guardian arena | Other |
|---|---|---|---|
| 1 | 1A south coast, temple (0, 1,365) | 1E crown (0, 0) -> Zone 2 town | starter shard 3 portal -> Zone 1 town; 9 outposts (Outposts-List) |
| 2 | 2A west coast, temple (2,895, 0) | 2D crown (4,790, 0) -> Zone 3 town | 8 outposts |
| 3 | 3A west coast, temple (5,525, 4,331) | 3E crown (7,290, 4,331) -> Zone 4 town | 8 outposts |
| 4 | 4A west coast, temple (2,640, 8,826) | 4D caldera floor (4,695, 8,826): guardian arena + the Echoing Maw (opens after the Lv 60 guardian) | 6 outposts; Zone 4 hidden behind `zones.max` 3 (Plan stage 3b) |
| 5 | Egg Desk cavern under the Maw, about (4,695, y 112-140, 8,826) | dragon lair, lava caverns about y 30-60 under 4D | 3 outposts |

Town spots are on each arrival isle's coast, R - 95 out from its centre (the Zone 1 town geometry). Walks town -> crown: Z1 248 s, Z2 344 s,
Z3 320 s, Z4 373 s (python, straight line at 5.5 b/s) - outposts and the menu warps carry the real travel. Option (build-time): rotate
each zone's table so its town faces the previous zone (nicer for dragon flights; no gameplay change while zones are out of sight).

### 7.2 Dragon roosts (later, when dragons exist - `research/cloud/Dragon-Quest-Spec.md`)

| Roost | Where | Rule |
|---|---|---|
| Town roost | a flat ledge on each town's coast | take-off / landing pad; the start of zone-to-zone flights |
| Summit roost | beside each summit portal | so a flight can skip the climb only to zones already unlocked |
| Zone 5 | none underground; the Egg Desk has a "call your dragon" spot in the Maw shaft | caves are walk-only |

Dragon flight over the zone gap works only toward unlocked zones (the Layout draft's "winds push you back" 60 blocks past the hull
for locked ones). No `/fly` on zone islands (Plan, LOCKED there).

### 7.3 Building and the void

| Area | Rule (replaces the Layout draft's "no build within 12 blocks of the coast") |
|---|---|
| Inside a zone hull + 150 | building allowed, also over the void between islands (Skyy: "ways we build to get between them"); towns, arenas and the summit stay protected |
| Zone gap (beyond hull + 150) | block placement cancelled (`wg:fn:land` / `wg:fn:zoneOf` check), gliding clamped (Layout check 3, UNVERIFIED) |
| Falling | void kill at y -32, respawn at the town of the zone you fell from; items kept (line 15) |

---

## 8. Plugin side (one Python table -> JSON + Java, as 0.1)

| Key | Change |
|---|---|
| `wg:fn:ring` | returns `"Z1\|1C\|6-12\|Gorgeback"` style: the island from plain (unwarped) distance to each centre, the band from the Layout 3.1 blend; Zone 5 rule: under 4D and y < 150 -> the Zone 5 layer band |
| `wg:fn:zoneOf` (new) | (x, z) -> zone or null (inside hull + 150), for the build rule and the dragon wind |
| `wg:fn:land` | (x, z) -> on an island (plain distance, 40-block warp tolerance) |
| `/zone info` | island id, band, distance to its centre, cave band at your y |
| Geometry | baked; changing it = a new world version (Plan risk) |

---

## 9. Performance (UNVERIFIED; measure with the harness)

2D terms per column: about 21 islands + about 150 join beads (6 necks x 6-7, 6 arches x 16-19, 6 bridgeheads) + 4 small maps, all
inside `Cache`, once per column. 3D per voxel: about what 0.1 costs plus 3 cave noises. Budget: per-chunk generation time in the
harness at most 2x 0.1's. If over: fewer arch beads (radius 16, spacing 11), or one `PositionsCellNoise` over a positions `List` of bead
points (if that node takes a list - UNVERIFIED), or a `Switch` per zone hull (UNVERIFIED).

---

## 10. Staged build plan (each version small and testable)

`SkyyWorldGen 0.2` is already planned as the Zone 1 town P0 partner (landing = the town spawn, `research/Zone-1-Town-Build-Plan.md`), on
the 0.1 test island. This spec starts after it. Every version: a new build script (first one: `SkyyWorldGen/build_skyyworldgen_0.3.py`) from the current SET
version + its harness (`SkyyWorldGen/test_skyyworldgen_0.3.py` and so on) (offline chunk generation like 0.1's section C).

| Version | What | Harness proof | Skyy test | Round |
|---|---|---|---|---|
| **0.3 Node proof** | throwaway admin world `skywynn_proof`: two offset islands (R 200 / 260), one neck, one arch, one bridgehead pair; 2D fields + code map | offset moves the island; `Max` unions; bead joins solid end to end; arch has void under it; bridge span exact (36 +- 0); biome code per island | fly around in creative: two islands, neck, arch | lean (one mod, no saved data; proof world deleted after) |
| **0.4 Caves + lava** | the section 6 cave mask, shell guard, lava (option 1, else 2), depth environments, on the proof world | no carving within 12 of the underside; no lava / fluid below any underside; tunnels connect bands 1-3; band thickness = table +- 3 | walk down from an entrance to the lava sea | lean |
| **0.5 Zone 1 archipelago** | world `skywynn`, 5 islands of 5.1, joins, caves, biome looks per island, landing = town spot on 1A; `wg:fn:ring` v2; `/zone 1` points to it; `skywynn_z1` kept | column survey per island (biomes, bands, rim / peak / under +- 6), town area flat enough for SkyyTowns, generation time | walk town -> neck -> crown; the arch; the Fenmoss bridgeheads | **full** (new world, landing move, several systems) |
| 0.5.1 | SkyyTowns re-stamps the town on 1A; bridge pieces at bridgeheads; the in-zone / zone-gap build rule | bridge piece fits the 40 span | cross the Fenmoss bridge; building over the zone gap refused | full (permissions, saved data) |
| **0.6 Zone 2** | Zone 2 table, summit portal 1E -> 2A town (per-profile unlock), zone-gap glide clamp | 1,100 gap; no land between hulls | unlock + portal; can't cross by gliding | full |
| 0.7 Zone 3 | Zone 3 (6 islands) + portal 2D -> 3A | as 0.6 | as 0.6 | full |
| 0.8 Zone 4 | Zone 4, hidden behind `zones.max` 3; 4D deep root to y 8, Zone 4 caves above y 150 only | 4D underside >= y 8, Zone 5 band left solid | Skyy flips `zones.max` 4 | full |
| 0.9 Zone 5 | Zone 5 layers under 4D (caverns, Maw shaft, Egg Desk cavern, lava lake, lair), own envs + spawn files | cavern volume, light shafts, no lava past the shell | a Lv 60 mob in the jungle caverns; the Maw opens after the Zone 4 guardian | full |
| later | dragon roosts + flight rules (needs a flying mount: Dragon-Quest local check 1) | - | - | full |

---

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Your 2026-10-03 line wanted to SEE Zone 2 from Zone 1; your 2026-10-09 line wants zones far apart (dragon / portal only). 1,100 blocks is safe from gliding but out of sight. Which matters more? | [far apart, 1,100 blocks, not visible; option: 500 blocks + a server rule that stops gliding over the gap, so you can see the next rim] |
| 2 | "At least 3x the size": total land of each zone's islands about 3x the old planned island (each zone about 3.8-5.9 M blocks^2), or smaller and denser? | [about 3x total land per zone] |
| 3 | Inside a zone, may players build their own bridges between islands (outside towns)? | [yes; only the gap between zones is no-build] |
| 4 | The joins: Zone 1 = 2 necks, 1 arch, 1 built bridge; deserts get long arches. Should some built bridges be broken ones you repair (like the starter shards), or always finished? | [finished; repair quests later if wanted] |
| 5 | Zone 5 under the Zone 4 caldera only (about 1.45 M blocks^2 of cavern floor), or also a deep tunnel under a second Zone 4 island? | [caldera only first] |
| 6 | Cave depth: islands about 110-215 blocks tall with a lava sea at y 52 (caves squeezed to about two thirds) - deep enough? | [yes, x0.67] |

## For the local session (UNVERIFIED - needs `Assets.zip` / `HytaleServer.jar` or a harness run)

| # | Check |
|---|---|
| 1 | `Offset` / `Anchor` JSON keys: move a `Distance` sample point by (cx, cz) (0.3 harness) |
| 2 | `Max` keys (else negate + `Min`); whether `Normalizer` clamps outside From..To; whether `CurveMapper` holds the end values past its first / last point |
| 3 | Vanilla V2 cave technique (read the release `Server/HytaleGenerator/Biomes/` Plains1 files read-only; `research/SkyyWorldGen-Plan.md` 3.4 step 7 says they band caves by height): learn the shape, write our own numbers |
| 4 | Fluid materials (lava, water) in a material provider; a material provider delimited by a density; how `Framework` Water acts (0.1 has Water 140 and no water in the void) |
| 5 | `EnvironmentProvider` `DensityDelimited` keys; vanilla cave environment ids per zone; a volcanic cave env; custom env + spawn file (Plan T6) |
| 6 | Prefab props on cave floors (`ColumnLinear` with a band below the surface) for lava pools and Zone 5 jungle props |
| 7 | Vanilla cave and lava depths in the normal world (to tune the x0.67 squash against what Skyy remembers) |
| 8 | Glider / glide ratio in vanilla 0.6 / 0.7 and in installed mods (the 1,100 gap assumes 4:1); server view distance (is 1,100 out of sight?) |
| 9 | Generation time per chunk with about 170 2D terms (budget 2x 0.1); `PositionsCellNoise` over a `List`; `Switch` / `Selector` keys |
| 10 | `SingleInstance` exports: is an imported noise computed once per position (cave noise shared by all islands)? |
| 11 | Flying mount for dragons (Dragon-Quest local check 1) and its speed (gap crossing time) |
| 12 | Bridge prefab length limits for SkyyTowns pieces (32-40 span) |
