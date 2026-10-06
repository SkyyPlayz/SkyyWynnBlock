# Zone islands layout - all four islands in ONE world

Cloud draft, 2026-10-06. Paper design for SkyyWorldGen stage 2. Skyy's locks (docs/answered/world.md, 2026-10-03): *all the zone islands in the same world, so you can see Zone 2 from Zone 1* (far enough apart to need the portal / warp, close enough to see the next zone across the void);
islands **at least 3x the size**, a **random coastline**, **a mountain rising to the middle** (generally trending upward, harder biomes toward the middle as a *tendency*, not a hard rule, with more variance than the all-birch first test), **vanilla features kept** (rivers, caves, goblin camps ...) and **caves inside**;
the guardian + portal unlock must still matter. Base plan: `research/SkyyWorldGen-Plan.md` (rings, heights, towns, portals; it assumed one world per zone, so this document **replaces its section 2.1 / 2.2 geometry**). All engine facts (view distance, generator reuse) are **UNVERIFIED** (no game files).

## 0. What changes against the old plan

| Topic | Old plan (2026-10-01) | **Now (Skyy 2026-10-03)** |
|---|---|---|
| Worlds | one world per zone (`skywynn_z1..z4`) | **one world** `skywynn` holding all four islands |
| Size | R 640 / 704 / 768 / 832 ("medium") | **3x the area**: R 1,110 / 1,220 / 1,330 / 1,440 (x1.73 radius) |
| Shape | round, warped rings | **random coastline** (noise-warped outline), mountain in the middle, ring bands become tendencies |
| Travel | instance load per zone | **instant** summit portal / warp inside one world (no instance loading) |
| Seeing the next zone | no | yes, across a 220-block void gap, at the facing rim |
| Hub | none | the Zone 1 town (vanilla temple) at the landing rim; the **solo player's first stop** is the starter shards (Starter-Shards-Plan-2) |

## 1. Sizes

Scaling by sqrt(3) in radius gives exactly **3.0x land area** for every zone:

| Island | Old R | **New R** | Land area (chunks of 32x32) | Old area | Rim -> centre walking (5.5 b/s) | Sprint (7.0) |
|---|---|---|---|---|---|---|
| Zone 1 Emerald Wilds | 640 | **1,110** | 3,780 | 1,257 | 202 s (3.4 min) | 159 s |
| Zone 2 Howling Sands | 704 | **1,220** | 4,566 | 1,521 | 222 s | 174 s |
| Zone 3 Whisperfrost Frontiers | 768 | **1,330** | 5,427 | 1,810 | 242 s | 190 s |
| Zone 4 Devastated Lands | 832 | **1,440** | 6,362 | 2,124 | 262 s (4.4 min) | 206 s |
(Real trips are longer: terraces, rivers, caves.) For scale: the vanilla Goblin shard is r about 430 and the Oasis island 440-530, so these are 2-3x larger than anything vanilla builds as an island.
`layout.size` stays a row: **S 0.6 / M 1.0 / L 1.6 of R**; the default becomes "L-3x" (x1.73 of the old medium). Changing it needs a new world (geometry is baked into the world assets).

**Is 3x area or 3x radius?** Skyy said "at least 3x the size". I read it as area (so a typical walk is still 3-4 minutes); a 3x **radius** (R 1,920+) would mean 9x area, rim to centre 6+ minutes, a 9-minute detour per death. Open question 1.

## 2. Placement in the one world (coordinates in blocks; world origin = Zone 1 centre)

Islands sit on a gentle **arc** so each island's rim faces the previous one, with a **220-block void gap** between neighbours and **no two non-neighbours within 2,400 blocks**:

| Island | Centre (x, z) | Direction from previous | Distance centre to centre | Rim-to-rim gap |
|---|---|---|---|---|
| Zone 1 | (0, 0) | - | - | - |
| Zone 2 | (2,511, 443) | 10 degrees | 2,550 | 220 |
| Zone 3 | (4,100, 2,712) | 55 degrees | 2,770 | 220 |
| Zone 4 | (3,581, 5,657) | 100 degrees | 2,990 | 220 |
Non-neighbour distances (edge to edge): Zone 1 - 3 = 2,476, Zone 2 - 4 = 2,663, Zone 1 - 4 = 4,145. World extent used: x -1,110 .. 5,540, z -1,110 .. 7,097 (a 6,650 x 8,210 block box, about 53 million blocks, mostly void).
Zone 5 (the dinosaur caves, Lv 60-75) is **underground below Zone 4** in the same island (a cave layer under the caldera, y 20-130), entered through a portal in the caldera; no extra island (see section 7).

The first-person view: standing on the **facing rim** of Zone 1 (the east-north-east coast) a player sees the **west rim and the lower slopes of Zone 2** 220 blocks away; the mountains behind it (summit y about 240-300) show only if the client renders that far (view-distance note below).

## 3. The land shape (random coastline + mountain)

The old plan used a perfect circle with six concentric rings. New rules, applied by one shared **land mask** (a 2D noise-warped distance field):

| Part | Rule |
|---|---|
| Outline | `radius(theta) = R x (1 + 0.22 x noise(theta, seed) + 0.08 x noise2)`: 4-6 lobes, +/-25% of R, with 2-3 **bays** (inlets) and 2-3 **headlands** (peninsulas). The facing rim gets one big **headland** toward the neighbour island so the view across the gap is dramatic and the gap is shortest there (still >= 200 blocks) |
| Beaches and cliffs | the first 30-60 blocks inside the coast are beach / low cliff; a 16-block `SkyWynn_Edge` biome and the void beyond (as before) |
| Height | a smooth **height field** `y(d) = rimY + (summitY - rimY) x smooth(1 - d/R)^1.4 + noise`: rim about **150**, summit about **260** (up to 300 for Zone 4); gentle slopes with **plateaus, ridges and valleys** (noise 18-30 blocks) instead of the staircase terraces; terraced "ring" steps are kept only as 2-3 cliff bands where the biomes change tier |
| Mountain | the middle third rises; the summit (core) is a rocky crown 120-160 blocks wide with the guardian arena and the summit portal |
| Underside | tapers from about y 60 at the centre to the rim (as before) so it reads as a floating island; Zone 4's underside is hollow for Zone 5 |
| Rivers | 2-4 rivers per island run from the mountain to the sea (on V1 data: rivers pass through to the biome beneath; on V2 a river node) |
| Caves | cave networks in every island (vanilla cave carving through the stone layer; **volcanic caves** deeper, the hardest cave range per the mob refit); entrances on slopes and in cliff bands |

### 3.1 Biome / level tendency (not a hard ring)
The level bands from `research/cloud/Mob-Levels-Refit.md` (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60) are driven by a **blend**: `level_t = clamp(0.65 x (1 - d/R) + 0.25 x biomeTier + 0.10 x noise)`, so:
- **65% distance from the coast** (the "rim easy -> middle hard" rule),
- **25% the vanilla biome tier** (Tier 1/2/3 regions from the zone data),
- **10% random** so a hard pocket can sit near the coast and an easy glade near the summit.
This keeps the old ring ladder as the *average* trend (wg:fn:ring returns a band computed from this blend, not from a ring index): `wg:fn:ring(world, x, z)` stays the interface (SkyyMobs and SkyyGear only read it); only its internals change.

### 3.2 Vanilla features (the "keep the normal world gen" lock)
| Feature | How |
|---|---|
| Zone biome patterns (46 looks) | placed from the biome tables of Mob-Levels-Plan 4.2-4.5 with the new variance; no single-tree-type wall: in each ring bucket mix 3-6 biomes by weight (vanilla's own region / tile weights) so the blue forest is a **clearing**, not a final stripe |
| Rivers, lakes, caves | as above |
| Goblin camps, Trork camps, mineshafts, ruins, Kweebec villages | **vanilla prefabs placed by reference** with the vanilla spawn density per zone (same rules as the 3-ring test); never copy the files into the repo |
| Dungeons | one zone dungeon per island (the story-beat dungeon, SkyyDungeons plan) near the summit |
| Towns (LOCKED) | each island's **starter town built around a vanilla temple** at the landing; **30-35 outposts** across the four islands (one per biome group; `Outposts-List.md`) |
| Ores | Copper / Iron on Zone 1, Thorium / Cobalt on Zone 2, Adamantite / Mithril on Zones 3-4 (`Gathering-Tiers-Draft.md`) |

## 4. Landing, hub town, portal and guardian spots

| Spot | Position (relative to the island centre; rotated toward the previous island) | Notes |
|---|---|---|
| **Landing + town** | on the **rim facing the previous island** (Zone 1: the south rim for new players coming from the starter shard portal), about `R x 0.92` out | the starter town built around the vanilla temple; the previous island's summit portal and the warp both arrive here; respawn point; return portal; safe zone |
| **Summit portal** | the exact centre of the island (0, summit, 0), next to the guardian arena | opens only for players who unlocked the next island (per profile) and sends them to the **next island's landing town** (instant teleport inside the world) |
| **Guardian arena** | right beside the summit portal on the crown | the zone's guardian (Zone-Bosses-Ideas) |
| **Dungeon entrance** | on the summit slope, 150-250 blocks from the arena | instance world (own `bands.world`) |
| **Outposts** | in their biome group, never on a path that skips a ring | each an unlockable warp (found = unlocked) |

## 5. Travel, anti-bridging and anti-flying (the bypass question)

The risk of seeing the next island is that players try to reach it without the guardian: bridges, parkour, boats, gliders, ender-style items, dragons, falling "with style", or placing blocks over the void.

| Rule | Detail |
|---|---|
| **No land route** | the 220-block void gap is not crossable on foot; no bridges exist; the summit portal is the only direct way |
| **No-build void band** | **block placement is cancelled in the void and within 12 blocks of the coast** (a `wg:fn:land(x,z)` check on the land mask), plus fluids and decorations; towns allow normal building |
| **Block "scaffolding" tricks** | placing blocks needs a **supporting neighbour** on land; towers can climb but not extend into the void (the band check applies at any height) |
| No `/fly` on zone islands (LOCKED in the old plan); creative / admins exempt | |
| **Gliders / jetpacks / double jump** | from the rim (y 150) a glider with a 4:1 ratio would travel about 600 blocks, more than the 220-block gap, so **gliding is clamped over the void band** (a server-side velocity limit) and Double Jump / Acrobatics perks cannot carry a player across (check 3 in section 9) |
| **Dragons (later)** | flying dragons would cross the gap; rule: dragon flight over a void band works **only toward unlocked islands** (the "winds push you back" soft barrier at 60 blocks beyond the rim for locked ones); the Zone 5 dragon quest only happens after Zone 4 so this matters late |
| **Falling into the void** | kill at y -32 (the old plan) = the coin-loss death, softened by the Echo Shard accessory; respawn at the landing town of the **island you fell from** |
| **Portal gate** | per-profile unlock (the old `unlock.mode`); if a player arrives by another route a guard sends them back (`AddPlayerToWorldEvent` redirect UNVERIFIED) |
| **Boats** | no boats in the world (or boats cannot leave the coast water) |
| Admins | can build bridges for events; a `/wg bridge` admin tool (later) |

## 6. View distance, loading and cost (engine notes, UNVERIFIED)

| Topic | Note |
|---|---|
| Client view distance | Hytale's client renders chunks within the **server view distance** (the world config `ViewDistance`? default about 12 chunks = 384 blocks, UNVERIFIED). A 220-block gap is **inside** that radius, so the neighbour's rim chunks load; the mountains behind the rim are beyond it. To show the neighbour's mountain, either raise the view distance a little, keep the facing headland and a **foothill** near the rim (so what you see is the low slope and the lights of the town), or place **distant silhouette models** (props) on the void side - UNVERIFIED engine |
| Chunk cost | seeing the neighbour's rim loads about 30-60 extra chunks per player at the facing coast: cheap; no entity ticking beyond the simulation distance |
| Mob spawning | the far rim chunks are loaded for rendering only; spawn only where players are within simulation range (set `SimulationDistance` below the gap, UNVERIFIED) so a Zone 2 pack does not spawn from Zone 1 |
| Save size | one world file with four islands: a few hundred MB after exploration; regions per island; backups per world (one backup for all) |
| World gen | the V2 generator runs per chunk on demand; the land mask is a pure function of (x, z, seed): `wg:fn:land` is thread-safe and cheap, as is `wg:fn:ring` |
| Time | the shared sky and day cycle are the same everywhere (good); weather per zone (the zone's environment) |
| Instances | **no instance loading between zones** (the same world); dungeons and the starter shards remain instances |

## 7. Zone 5 in the same world
Zone 5 = the dinosaur caves under Zone 4 (OPEN-QUESTIONS R8): a cave layer (y 20-130) under the Zone 4 caldera, entered through the "Echoing Maw" portal / a descending tunnel at the caldera floor; Lv 60-75; its own town (the Egg Desk) in a big cavern; the dragon boss at Lv 75; the cave network carved by the same cave pass with a **lost-world** biome (jungle caves). The Zone 4 island must therefore be **hollow-friendly**: reserve the underside and a vertical shaft.

## 8. Build plan (stages)
| Stage | Content |
|---|---|
| 2.0 | the land mask + height field as pure functions; a debug command that prints the band at (x, z) |
| 2.1 | Zone 1 only, 3x area, random coast, one river, caves, mountain; no portals yet; compare against the 3-ring test |
| 2.2 | the vanilla features pass (goblin camps, villages, mineshafts) and the biome variance (blend) |
| 2.3 | Zone 2 and the facing headland + void band rules + the summit portal |
| 2.4 | Zones 3-4, outposts, the dungeon entrances, Zone 5 shaft |
| 2.5 | polish: silhouettes / fog, anti-glide, the Echo Shard death rule |

## 9. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether V2 world generation can reuse the vanilla Zone 1 generator's biome / region data (WorldGen plan T1) or must re-place biomes from our tables. |
| 2 | World / client view distance, simulation distance and whether chunks beyond the island are free (void columns are cheap). |
| 3 | Whether gliding / double jump can be clamped over the void band; boats; any "fly" items in vanilla. |
| 4 | `PlaceBlockEvent` cancellation by land mask (cost per placement). |
| 5 | The portal's target in the same world (a teleport to the landing point) and respawn per island. |
| 6 | Hole-friendly underside for Zone 5 (cave layer under the island). |
| 7 | Whether one big world's save and ticking behave with 4 islands and many players (the old plan preferred separate worlds for cost). |

## 10. Questions for Skyy
1. **3x the size**: 3x area (R 1,110-1,440, about 3-4 min rim to centre) or 3x radius (9x area)? (Recommended: 3x area.)
2. Is a **220-block gap** the right feeling (see the rim across), or smaller (150) / larger (400)?
3. Dragons may later fly the gaps toward unlocked islands only - OK?
4. Zone 5 as a **cave layer under Zone 4** (recommended) or its own island?
