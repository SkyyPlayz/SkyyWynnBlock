# Zone 1 town - build plan (the Department of Arrivals)

Plan only, 2026-10-08 (Skyy: "yes plan the zone 1 town while i test"). Nothing built. The paper design is
`research/cloud/Zone-1-Town-Layout.md` (v2, organic) + `research/cloud/Zone-1-Town-Map.png`. Skyy's locks: `docs/answered/world.md`
2026-10-06 (vanilla temple at the centre, right behind spawn; Skyy upgrades its exterior later) and 2026-10-08 ("keep v2, its hub enough").
Other inputs: `research/SkyyWorldGen-Plan.md`, `research/cloud/Zone-Islands-Layout.md`, `research/cloud/WorldGen-Stage-2-Draft.md`,
`research/cloud/NPC-Shops-Spec.md`, `research/cloud/Starter-Shards-Plan-2.md`, `SkyyWorldGen/build_skyyworldgen_0.1.py`,
`SkyyIslands/build_skyyislands_0.5.5.py`, `SkyyBazaar` (page registration), HANDOFF sections 2-3.
Engine facts were read from the release `Assets.zip` and `HytaleServer.jar` (read-only, javap-style reflection + bytecode through the
repo's jpype toolchain). **VERIFIED** = seen in those files or proven in game. **UNVERIFIED** = needs the probe round (section 9).

## 0. In plain words

- The temple is the **vanilla spawn temple** - the same one at your `/hub` today. It is about 23 x 21 blocks, plus a 5-wide stone
  causeway that runs 11 blocks out of its door. It already sits on its own little hill, and its upper hall already has benches.
- We can place it facing south (door to the sea). Spawn = the foot of its causeway. You walk off the steps into the Waiting Square.
- Buildings turn only in 90-degree steps. "Organic" comes from the winding lanes, odd plazas and mixed angles, not from tilted houses.
- **Recommended way to build:** a mod "stamps" the town into the world (paste prefabs, lay roads, place NPCs) from data files, piece by
  piece. It keeps a ledger, so we can update one piece later without touching anything else - and it never overwrites a piece you
  edited by hand (your temple exterior work is safe).
- Works on today's test island first (so you can walk it soon), then gets stamped again onto the big stage 2 island.
- First step: a small **probe round** (admin-only test mod) to prove the 6 things we could not prove offline.

## 1. The 7 checks from the layout doc

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Which vanilla temple: name, size, door side, interior; can it sit on a knoll? | **VERIFIED** (asset). Placement look **UNVERIFIED** | `Server/Prefabs/Monuments/Unique/Temple/Portal/Grasslands_Spawn/Unique_Portal_Grasslands_Monuments_Unique_Portal_Grasslands_001.prefab.json` - the prefab the vanilla world's spawn zone places (`Server/World/Default/Zones/Zone1_Temple/Zone.json`, UniquePrefabs "Temple", `Rotations: ["ROTATION_90"]`). Box 35 x 30 x 40 (x, y, z), 19,297 block entries. Details in section 2. It brings its own 13-block foundation and grass skirt, so it IS a knoll. Can be placed by a V2 prefab prop or a runtime paste (both APIs VERIFIED, rows 3-4) |
| 2 | Can portal arrival / respawn target an exact outdoor block? | **VERIFIED** | SkyyWorldGen 0.1: instance `SpawnProvider` point + `/zone setlanding` sync (WgApplyLanding) + trips land with `teleportPlayerToLoadingInstance(..., landing)`. In game 2026-10-03 (docs/log): void death respawned at the landing (0 143 344), `/zone 1` lands there. Same calls work for the town spawn |
| 3 | Rotation: 90-degree steps or free angles? | **VERIFIED: 90-degree steps** | `PrefabRotation` has only ROTATION_0/90/180/270. Probed: ROTATION_0 keeps the prefab's +z, ROTATION_90 turns +z to +x. V2 `StaticDirectionality` takes Rotation 0/90/180/270 (vanilla the vanilla Desert1 Oasis biome file (Assets.zip) places Feran huts that way). Free angles exist only as a builder tool (`BlockSelection.rotateArbitrary`, used by `/rotate`); it resamples blocks - look **UNVERIFIED**, not planned |
| 4 | Can the generator keep a **sloped** town (no rivers / caves)? Real rim height? | **VERIFIED possible** both ways; look **UNVERIFIED** | V2: density nodes `Mix`, `Sum`, `CurveMapper`, `Distance`, `Anchor`/`Offset`, `PositionsCellNoise` + a `List` of points (all in the jar; vanilla Oasis uses `PositionsCellNoise` over a `List`). Runtime: `WorldChunk.setBlock` cut / fill (SkyyIslands' FillTask already places a whole starter island this way, live). Rim height: test island ground y 143-144 at the landing (VERIFIED, harness + in game). Stage 2 rim ~150 is a placeholder (not built) |
| 5 | Can a placed Kweebec NPC open our page and bark? A rock model for Pebble? | **Pieces VERIFIED, chain UNVERIFIED** | `NPCPlugin.spawnNPC(Store, role, ?, pos, rot)`; role JSON "Variant" pattern (vanilla `Temple_Kweebec_Merchant` = Variant of `Kweebec_Merchant` + Invulnerable); entity component `Interactions.setInteractionId(InteractionType, rootId)` + `setInteractionHint`; page ids via `OpenCustomUIInteraction.registerSimple` (SkyyBazaar registers "SkyyBazaar", live). Vanilla NPC actions only have `OpenShop` / `OpenBarterShop` (no "open custom page" action). Rock model: the only rock models are `Server/Models/Projectiles/Items/Rubble/Rubble_Stone_Mossy.json` (a thrown-rubble projectile, small) and the `Golem_Crystal_*` golems; a proper Pebble needs our own Blockbench model (as an NPC look **UNVERIFIED**). NPC survives a restart without duplicates **UNVERIFIED** |
| 6 | World compass axes; where Zone 2 faces | **VERIFIED** | `Vector3iUtil`: NORTH = (0,0,-1), SOUTH = +z, EAST = +x. The layout's "x east, z south" is right. From the town (south rim, about (0, +1,015)) Zone 2's centre (2,511, 443) lies **east-north-east**, rim about 1,355 blocks away - too far to see at normal view distance (**UNVERIFIED** view distance). The east headland viewpoint still points the right way |
| 7 | Build protection for an irregular town limit | **Events VERIFIED; the area check is new code** | SkyyIslands guards `BreakBlockEvent`, `PlaceBlockEvent`, `DamageBlockEvent`, `UseBlockEvent$Pre` (live since 0.3) but per WORLD (`allow()` passes any world with no island owner). The town needs a point-in-polygon test on (x, z) against a stored polygon. Plain maths, no engine risk. Explosions / fluids / mob griefing **UNVERIFIED** |

What SkyyWorldGen 0.1 already proves: V2 assets shipped in our jar make a world (in game, 2026-10-03), V2 `Prefab` props place
vanilla prefabs (the birch / azure trees), a persistent instance world with a fixed spawn + respawn point. It does NOT paste anything
at runtime. Runtime pasting is proven by vanilla code: `SpawnPrefabInteraction.firstRun` (`PrefabStore.findAssetPrefabPath` ->
`PrefabBufferUtil.getCached` -> `PrefabUtil.paste(buffer, world, pos, Rotation, Random, int, int, accessor)`) and the world-events
`PrefabPasteAction` (load the paste region, **snapshot** it with `PrefabSnapshotUtil.createSnapshot`, paste; `PrefabRemoveAction`
pastes the snapshot back = undo). We copy that pattern.

## 2. The temple (Grasslands_Spawn) - what is inside

| Part | Prefab coordinates (y up; +z = south when placed with ROTATION_0) |
|---|---|
| Ground level | y 13 (= anchorY). Below: stone / dirt foundation y 0-12 |
| Main body | x -5..17, z -17..3 (about 23 x 21), stepped walls up to the roof at y 28 (about 16 above ground) |
| Door | south side (+z), about x 5..7 at y 16-17, 4 blocks above ground |
| Causeway | 5 wide (x 4..8), z 4..14, steps down from the door to the ground. **Spawn goes on its foot** |
| Upper hall | y 17+, about 17 x 13 inside; already holds 14 `Furniture_Temple_Light_Bench`, 12 statues, candles, a brazier = the Waiting Room |
| Crypt | y 3-12 under the hall: 9 `Forgotten_Temple_Portal_Enter` blocks (the vanilla Forgotten Temple dungeon portal, with a map marker), a `Golem_Crystal_Earth` spawn marker (the "temple guardian" golem), 2 `Block_Spawner_Block` (Zone1_Encounters_Tier2 / Tier3) |
| Children | 3 `Prefab_Spawner_Block` at y 20 (`Monuments.Unique.Temple.Bridge.Spawners_Full.Start.*`) - what they add after a runtime paste is **UNVERIFIED** |
| Palette | Rock_Marble_Brick, Rock_Stone, Rock_Marble_Cobble, Rock_Chalk, Rock_Stone_Brick, mossy stone, vines (use the same blocks for the square) |

Other temples in the jar (not chosen): `.../Temple/Portal/Grasslands/` (same building, 35x30x40), `.../Temple/Temple/Unique_Temple_001/002`
(31 x 67 x 67, much taller), Drylands 40x32x39, Snowlands 52x34x50, Firelands 27x44x54 (the Zone 2-4 town temples later).

**Town coordinates (temple centre = (0, 0), x east, z south):** temple body (-11..11, -10..10); door (0, 10); **spawn (0, 22) facing south**
(the layout said (0, 27) - 5 blocks closer); Mossby's desk in the hall about (0, -4). The rest of the layout stays as drawn. Rotation:
**ROTATION_0** (door south, to the sea). The paste offset between the prefab anchor and the target block is **UNVERIFIED** (the probe measures it).

## 3. Vanilla pieces we can use (ids from Assets.zip; size = x y z)

| District | Vanilla pieces | Notes |
|---|---|---|
| 1 Temple | the temple above | ROTATION_0 |
| 2 Waiting Square | paving Rock_Marble_Brick, Rock_Stone_Brick_Smooth, Rock_Marble_Cobble; `Furniture_Temple_Light_Bench`, `Furniture_Temple_Light_Lantern`, `Furniture_Village_Statue`; `Npc/Kweebec/Oak/Seats/Small/*` (5x4x5); `Npc/Kweebec/Oak/Lampposts/*` (1-4 x 8-10 x 2-4); `Npc/Kweebec/Oak/Well/Kweebec_Oak_Well_001` (8x14x8) at the Warp Pad | rings of temple stone round the temple |
| 3 Market plaza | `Npc/Kweebec/Oak/Water_Pool/*` (6x6x5) as the fountain; `Furniture_Village_Crate`, `Furniture_Tavern_Barrel`, `Furniture_Village_Planter` | |
| 4 Bazaar hall, 5 Auction House, 7 Bank / Vault + Guild, 8 Forge + Crafting Hall | **no fitting vanilla hall.** Nearest: `Npc/Outlander/Houses/Tier3/*` (25x22x28, Outlander style - wrong mood), `Npc/Kweebec/Oak/Houses_Large/*` (26-27 x 30 x 24-26 tree houses) | build **our own simple hall prefabs** (generated at build time from vanilla block ids, sized per the layout); Skyy restyles later. Inside: `Furniture_Village_Counter`, `Furniture_Village_Chest_Large`, `Furniture_Village_Bookcase`, vanilla benches (`Bench_Furnace`, `Bench_Armory`, `Bench_Armour`, `Bench_Salvage`, `Bench_Cooking`, `Bench_Alchemy`, `Bench_Loom`, `Bench_Lumbermill`, `Bench_Farming`, `Bench_Builders`, `Bench_Furniture`, `Bench_Arcane`) |
| 6 Shop stalls | `Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001..008` (7-8 x 9-10 x 7) | each carries a vanilla `Kweebec_Merchant` spawn marker - paste WITHOUT entities, our own NPC instead |
| 9 Tab Hall plot | `Wood_Softwood_Fence` + `Wood_Softwood_Fence_Gate`, `Furniture_Construction_Sign` | "Under Renovation" |
| 10 Event Square | stairs `Rock_Stone_Brick_Stairs` / `Rock_Marble_Brick_Stairs`, `Furniture_Human_Ruins_Banner(_Double/_Triple)`, `Furniture_Village_Brazier` | our own small stage prefab |
| 11 Promenade | `Wood_Hardwood_Fence`, Kweebec Oak lampposts every 20, `Furniture_Village_Bench`; **`Monuments/Incidental/Grasslands/Houses/Towers/Lighthouses/Incidental_Grasslands_Lighthouses_..._001` (8x21x8) on the Zone 2 headland** | |
| 12 North Gate | `Npc/Kweebec/Oak/Guard_Towers/*` (8-10 x 10-16 x 8-9) either side + our own arch | towers carry 2-6 vanilla guard markers - paste without entities. (`Npc/Outlander/Gates/*` exist but are hostile-faction style) |
| 13 Orchard + Kweebec homes | `Trees/Oak/*`, `Trees/Fruit/*`, `Npc/Kweebec/Oak/Garden/Large|Medium/*` (8-13 x 9 x 9); homes `Npc/Kweebec/Oak/Houses_Small/*` (15x24x18, 26x30x26), `Houses_Large/*`, `Bunny_Area/*` (13-15 x 9-10 x 13-16) | Kweebec houses are tall tree houses: keep them in district 13 |
| 9 filler houses | `Monuments/Incidental/Quartzite/Cottage/Incidental_Quartzite_001` (9x12x10), `Monuments/Incidental/Softwood/Cottage/Incidental_Softwood_001` (7x13x10), `.../Grasslands/Houses/Plains/..._001` (13x12x9), `.../Grasslands/Hunting/Cabins/*_001/002` (12x11x11, 9x10x11), `.../Grasslands/Farms/Structures/*` (10-13 x 8-12 x 10), `Npc/Outlander/Houses/Tier0/*` (9x14x11) | "Incidental" pieces may look ruined - pick by screenshot in the probe |
| Lanes near spawn | `Spawn/Pathways/Spawn_Zone1_Pathway_001..005` (5x2x7-9) | vanilla's own spawn path pieces |
| Signs, lights, fences | `Furniture_Village_Sign`, `Furniture_Kweebec_Sign`; `Furniture_Kweebec_Lantern`, `Deco_Lantern`; `Wood_Softwood_Fence`, `Metal_Iron_Fence` | sign TEXT support **UNVERIFIED** (fallback: NPC nameplates / hologram) |

## 4. How the town gets into the world

| Way | Good | Bad |
|---|---|---|
| A. Bake into the V2 world gen (props at `List` positions, `Static` rotation, a flatten density, road masks) | no runtime work; vanilla does villages this way (Desert1_Oasis Feran village) | only affects chunks not generated yet; changing the town later = a new world; can't place our NPCs; useless if stage 2 ends up on the V1 generator (still open) |
| **B. Runtime stamp by a mod (recommended)** | works on any world (test island now, stage 2 later, V1 or V2); each piece versioned and updatable; snapshot + undo; NPCs and protection in the same mod | Java work; the stamp needs the chunks loaded; a big one-time job (spread over ticks) |

**Recommended:** B for everything, plus one small A part in stage 2: the island generator keeps the town area clean (no caves, rivers,
trees or big rocks inside the town limit + a gentle slope). Until stage 2 exists, the stamp's own terrain step levels the ground.

**Mods that change:**
- **SkyyTowns 0.1 (new mod)** - the stamper, the ledger, town protection, the safe zone, town NPCs, `/town` admin commands, Server Setup
  page "Towns". Outposts (30-35) and the Zone 2-4 towns reuse it later. (Keeping it out of SkyyWorldGen keeps the world-gen jar about
  terrain only.)
- **SkyyWorldGen 0.2** - landing point = the town spawn; bridge key `wg:fn:landing` / `wg:fn:zone`; stage 2 later adds the clean town area.
- Later phases: SkyyBank / SkyyVault / SkyyGuilds / SkyyBazaar / SkyyAuctions only need their page ids registered for NPC use (Bazaar
  already is); SkyyExploration re-points the "Zone 1 Temple" discovery to the town temple's coordinates (V2 worlds have no zone data).

## 5. Stamp order (deterministic, one piece at a time)

1. **Terrain** - inside the town limit: cut / fill to the target height field (layout: about 2 blocks rise per 25 to the north + a
   4-block knoll), smooth the edge over 12 blocks. Never outside the limit.
2. **Temple** - paste at the centre, ROTATION_0, ground = prefab y 13.
3. **Square + plazas** - paving blobs (rings of temple stone round the temple).
4. **Lanes** - splines from `roads.json`, one block at a time, following the new ground; stairs where the slope is steep.
5. **Buildings** - prefabs (filler houses, stalls, halls, gate towers), entities stripped.
6. **Props** - lamps, benches, fences, trees, wells.
7. **Signs.**
8. **NPCs** - spawned from `npcs.json`, invulnerable, with their page interaction.
9. **Points** - spawn / landing, warp pad, door home; the protection polygon + safe zone turn on last.

Each step writes its pieces to the ledger. A crash mid-way resumes at the first unfinished piece.

## 6. Data files

In the jar (generated by the build script, committed as Python tables - no vanilla files committed):
- pieces.json in the town data folder (planned) - one row per piece: id, phase, kind (prefab / blocks / road / npc / point), source (vanilla prefab path or our
  prefab), origin (dx, dz from the town centre; y from the ground), rotation (0/90/180/270), entities on/off, version.
- roads.json in the town data folder (planned) - spline control points (5-8 each), width, block mix.
- limit.json in the town data folder (planned) - the town limit polygon (and the +24 safe-zone ring), the height field numbers.
- npcs.json in the town data folder (planned) - id, role, x, z, facing, page id, bark key.
- `Server/Prefabs/SkyWynn/Town/*.prefab.json` - our own pieces (hall shells, Board, ticket machine, warp ring, home arch, stage).
- `Server/NPC/Roles/SkyWynn/*.json` - town roles as Variants of vanilla Kweebec roles (invulnerable, idle / watch, no barter shop).
- `Server/Item/RootInteractions/SkyWynn/*.json` + `Server/Item/Interactions/SkyWynn/*.json` - one "open page X" interaction per page id (folders VERIFIED; vanilla test file `Server/Item/Interactions/Tests/OpenCustomUI.json` shows the type; the NPC Use chain **UNVERIFIED** until the probe).

In the world (`<world>/mods/Skyy_SkyyTowns/`):
- `towns.properties` - which town sits in which world at which anchor.
- `ledger-<town>.properties` - per piece: version stamped, time, box, block hash after stamping, `locked` flag.
- `snapshots/<piece>-<time>.prefab.json` - what was there before each stamp (undo).
- `config.properties` - Server Setup rows `town.*` (safe radius, protection on/off, NPC bark range, scale).

## 7. Updating the town without wrecking changes

- The town is build-protected, so normal players cannot change it. Admin edits are the only thing to protect.
- **Re-stamp only changed pieces**: a piece is stamped again only when its version in the jar is newer than the ledger.
- **Never overwrite hand edits**: before a re-stamp the mod hashes the piece's box. If it differs from the hash saved after the last
  stamp, someone edited it: skip it, say so (`/town status`), unless an admin forces it.
- **Your temple exterior work:** edit freely in game, then `/town capture temple` saves the edited area as our own prefab in the world
  data (`PrefabStore.saveServerPrefab`, VERIFIED API) and marks the piece locked. Later we copy it into the jar if you want it shipped.
- **Undo**: every stamp keeps a snapshot; `/town undo <piece>` pastes it back (vanilla `PrefabRemoveAction` pattern).
- **Dry run**: `/town build --dry` lists what would change (pieces, block counts) and touches nothing.
- **New world** (stage 2): the ledger is per world, so the town is stamped fresh there; captured pieces come along.
- Nothing is ever written outside the town limit box.

## 8. Phases and rounds

| Round | Content | Mods | Size (PROJECT-RULES 4) | Done when (Skyy test) |
|---|---|---|---|---|
| **T0 probe** | section 9 | SkyyTownProbe 0.1 (new, admin-only, removed after) | **lean** | the 6 probe answers are in docs/log |
| **P0** | terrain, temple, Waiting Square, spawn steps + landing, Promenade + fence, orchard, 9 filler houses, Mossby (NPC, no quest yet), benches; ledger / snapshots / capture / undo; protection + safe zone; Server Setup "Towns" | SkyyTowns 0.1 (new) + SkyyWorldGen 0.2 | **ultracode** (new system, saved data, world edits, permissions, 2 mods) | `/zone 1` lands on the temple steps; the town is walkable; breaking blocks in town is refused; `/town undo` works |
| **P1** | Bank, Vault + Guild, Bazaar, AH (hall shells + NPCs opening the live pages); the Board; North Gate + Summit Road; Warp Pad; home door; 4 guards; town map sign | SkyyTowns 0.2 (+ page-id registration in Bank / Vault / Guilds / Auctions where missing) | **full** (several mods) | each NPC opens its page; menus still work everywhere |
| **P2** | 4 stalls (needs the NPC shop system, `research/cloud/NPC-Shops-Spec.md` - economy = its own **ultracode** round first), Forge Quarter, Crafting Hall (vanilla benches) | SkyyTowns 0.3 (+ SkyyShops) | stamping **lean**; shops **ultracode** | buy / sell at a stall |
| **P3** | Event Square + Event Vendor | SkyyTowns 0.4 (+ events system) | **lean** once events exist | |
| **P4** | Tab Hall on the reserved plot; homes / pets | later | - | |

Empty plots stay sealed "Under Renovation" from P0 on, so the layout never moves.

**Dependency:** the final town lives on the stage 2 island (`research/cloud/WorldGen-Stage-2-Draft.md`, Zone-Islands-Layout stage 2.1). P0 does not wait
for it: it stamps onto today's test island (`skywynn_z1`, landing (0.5, 144, 344.5); temple centre about (0, ~250) so the coast is ~95
blocks south). When stage 2.1 ships, the stamp runs again on the new island. Stage 2.1 should add: a town mask at the landing (no caves,
rivers, trees, boulders; slope kept), and the landing = the town spawn.

## 9. Probe round T0 (SkyyTownProbe 0.1, admin-only, on the test island)

| Command | Proves | Pass |
|---|---|---|
| `/townprobe temple [0-3]` | runtime paste of the temple (load paste region, snapshot, paste, rotation); the anchor offset; whether the 3 child Prefab_Spawner blocks add anything; time taken | temple appears whole, door faces the chosen way; log prints anchor offset + ms |
| `/townprobe undo` | snapshot paste-back | the ground is back as before |
| `/townprobe lane` | a 40-block cobble spline that follows the ground, with a step where steep | looks like a path, no floating blocks |
| `/townprobe piece <prefab path> [rot]` | stalls / cottages / lighthouse with entities OFF | no vanilla merchant / guards spawn |
| `/townprobe npc` | spawn a town Kweebec (Variant role) with Use -> open the "SkyyBazaar" page + a hint; a bark in chat within 8 blocks; still there once (not twice) after a restart | F / right-click opens the Bazaar page |
| `/townprobe pebble` | the `Rubble_Stone_Mossy` projectile model (scaled up) as an NPC; else Pebble gets our own Blockbench rock | a mossy rock stands there, or we know we need a model |
| `/townprobe zone` | a 20-block polygon where break / place / use are refused for non-admins | refused inside, allowed outside |
| `/townprobe sign` | writing text on `Furniture_Village_Sign` | text shows (or: not supported -> use nameplates) |

Optional T0b (only if stage 2 picks V2): a throwaway V2 probe world with the temple as a `Static` prop at a `List` position + a flatten
density - shows whether a 35 x 40 prefab generates whole across chunk borders.

## 10. Risks

| Risk | Answer |
|---|---|
| Stamping ~50,000 blocks^2 of terrain + prefabs lags the server | spread over ticks per chunk; admin-triggered `/town build` in P0; time it in the probe |
| Chunks not loaded when stamping | `PrefabUtil.loadPasteRegionAsync` first (vanilla pattern); blocks only on the world thread |
| The crypt: Forgotten Temple portal + Earth Crystal Golem + encounter spawners inside a safe town | question 2 below |
| Temple prefab children (bridge spawners) add blocks we don't expect | probe; else strip those 3 blocks |
| NPCs duplicate after restarts, or vanish | ledger keeps each NPC's UUID; respawn only when missing (probe) |
| Explosions, fluids or mobs break protected blocks | add guards per event found; the snapshot can repair |
| "Incidental" houses look ruined | pick filler houses from probe screenshots |
| The Zone 1 Temple discovery reward stops working in a V2 world | SkyyExploration points it at the town temple coordinates |
| Stage 2 generator choice (V1 vs V2) still open | runtime stamp works either way |
| Our town prefabs reference vanilla block ids that change in 0.7 | build script checks every id against Assets.zip (as SkyyWorldGen does) |

## 11. Questions for Skyy (default in brackets)

1. Use the vanilla **spawn temple** (the one at today's `/hub`), door facing the sea, spawn at the foot of its causeway? [yes]
2. The temple's **crypt** has the Forgotten Temple portal, the Earth Crystal Golem (green crystal source) and two mob spawners. In the
   safe town: keep it all as vanilla, keep only the portal, or seal the crypt? [keep it all - the guardian under the old temple is part
   of the story; the safe zone stops at the hall floor]
3. Big buildings (Bank, Bazaar, AH, Forge...) have no vanilla match. OK to start with plain stone-and-timber halls that you restyle
   later (like the temple)? [yes]
4. Build P0 on today's test island first so you can walk it, then move it to the big island? [yes]
5. Stalls = Kweebec Oak market stalls; filler houses = vanilla cottages / cabins; Kweebec tree houses only in the homes district? [yes]
6. Layout Q2-Q7 still open: spawn on the outside steps [yes]; town protected, homes later [yes]; Pebble leaves in Z1.2 [yes]; walks
   17-24 s fine [yes]; walk-in Bank / Bazaar / AH with NPCs, menus still work [yes]; sealed plots visible [yes, "Under Renovation"].

**Recommended first round:** T0 probe (lean, SkyyTownProbe 0.1, admin-only, removed after Skyy's test). Then P0 as an ultracode round.
