# Starter shards plan 2 - a buildable plan

Cloud draft, 2026-10-06. Turns `research/cloud/Starter-Shard-Layout.md` (3 shards, gaps, budget) into a plan the local session can build. Skyy's lock (2026-10-03): *"make the island 3x with a small hill, more trees, a cave, and that bridge to the second island with mobs, and add the 3rd island with the portal; the boss comes later"* (docs/answered/world.md).
Also: R8 - the **first gap is a broken bridge you repair, the later gaps you build** (Isles-of-the-Void-Lore). Facts used: a chunk is **32 blocks**; the island template box is **3 x 3 chunks, y 96-191** (LOCKED 2026-09-25) with size upgrades 4x4 .. 9x9 planned; `/island reset` = 24 h cooldown, 3 confirms; instances are copied from `Server/Instances/SkyyIsland` (SkyyIslands plan);
starter coins and the kit chest are once per profile. Everything not marked VERIFIED is UNVERIFIED (no game files here).

## 0. What changes against the first layout (Starter-Shard-Layout.md)
| Topic | First layout | **Plan 2** |
|---|---|---|
| Shard 1 size | R 30 | **R 56** (area about 3x a 3x3-box island's usable ground; the box default becomes **5 x 5 chunks**, 160 x 160, y 96-191) |
| Terrain | flat | a **small hill** (top +10 blocks), a pond, a stream, **more trees**, a bigger **cave** with two rooms |
| Gaps | 12 / 14 | **14 (repair) / 16 (build)**, scaled with the bigger shards |
| Shard 2 | R 14 | **R 20**: crude workshop, 12 weak mobs |
| Shard 3 | R 18 | **R 26**: toll hut, camp, **portal plaza**; **the boss is optional for now** |
| Existing islands | not covered | **options in section 7** |

## 1. The footprint (coordinates relative to the shard-1 centre, y = ground)

| Shard | Centre (x, y, z) | Radius | Gap to the next | Chunks (x range) |
|---|---|---|---|---|
| **1 Home** | (0, 140, 0) | 56 | **14** (repair) | -2 .. 1 |
| **2 Crude** | (90, 138, 0) | 20 | **16** (build) | 2 .. 3 |
| **3 Toll + portal** | (152, 142, 0) | 26 | - | 4 .. 5 |
Total span x -56 .. 178 (8 chunks), z -56 .. 56 (4 chunks) = about 32 template chunks. The **5 x 5 box** (+/-80) holds shard 1 and the start of shard 2; shards 2-3 lie in **protected extension chunks east** of the box.
**Box upgrades (LOCKED 2026-09-25: later 6x6 .. 9x9) grow west, north and south only; the east side stays at +80**, so the chain never moves or gets built over (a row `island.box.eastLimit`).

## 2. Shard 1 - the home shard (R 56)

| Feature | Position | Size and contents | Used by |
|---|---|---|---|
| **Spawn mound** and Pebble's rock | (0, 0) | the existing spawn / starter chest / bed here | Q1 |
| **The hill** | (-14, -16) | 28 across, top **+10 blocks** (y 150); a small viewpoint with 2 trees and a signpost "You can see the next shard from here" | look, tutorial |
| **Forest** | NW and W (-40 .. -10, -40 .. 0) | **36 trees**: 14 oak, 10 birch, 8 ash, 4 apple; leaves give fibre | Q2, Crude armor |
| **Meadow with bushes** | N and E | about **30 bushes**, 12 flowers | fibre and sticks |
| **Pond** | (-6, 28), 10 x 8, 3 deep | water | Q5 |
| **Stream** | from the pond east to the cliff, 2 wide | decorative; **no fish needed** | looks |
| **Farm patch** | (10, 30), flat 9 x 9 soil | 5 starter seeds in the first chest; 1 water block touching | Q5 |
| **Cave** | entrance NE (40, -20), 3 x 3 | tunnel 25 long into a **first room** 9 x 9 (stone, 3 coal) and a **second room** 11 x 8 (copper vein of **10**, a small stone chest with 20 sticks and fibre) with torch brackets; a small shaft up to a "window" | Q4 |
| **Boulders and rubble** | around the east shore | 8 boulders = about 24 Stone Rubble | Crude armor |
| **Workbench spot** | next to the chest | a flat 4 x 4 area, a "table goes here" sign | Q3 |
| **The broken bridge** | east edge (56, 0) | the posts of a bridge **14 blocks long**: the first **4 blocks** exist, the rest of the **planks are missing**; the posts show where they go; a **Bridge Repair Kit** recipe appears when the quest starts | Q7 |
| **Rim fence** | the whole coast | a low rock lip so nobody falls by accident (the Void is still below) | safety |
| **Bed / respawn** | beside the chest | respawn for shard 1 | all |
Shard 1 holds **no hostile mobs** (spawning off on it; friendly animals later: a chicken or two near the farm, optional).

### 2.1 Resource budget (checked against the quests)
| Need | Quest | Provided |
|---|---|---|
| 10 logs | Q2 | **150+** (36 trees x ~4-5) |
| Workbench + Accessory Bag | Q3 | logs, sticks, fibre (plenty) |
| 20 cobble + 5 copper | Q4 | 100+ stone blocks in the cave, **10 copper**, 3 coal |
| 5 wheat | Q5 | 5 seeds + 81-block patch + pond; growth time UNVERIFIED (let it run while doing Q4) |
| Collection tier I | Q6 | any of the above |
| Bridge repair (14 blocks, 3 wide): **about 24 planks + 8 sticks + 6 fibre** | Q7 | from the 150 logs |
| Crude armor set: 31 fibre, 11 sticks, 10 rubble, 2 logs | Q8 | meadow (30 bushes about 15 fibre), leaves (fibre), forest, boulders |
| Gap-2 bridge: 3 wide x 16 = **48 blocks** of stone / planks | Q10 | cave stone + more logs |
Extra supply of fibre and sticks is on shard 2 too (bushes, a chest).

## 3. Shard 2 - the Crude shard (R 20)

| Feature | Details |
|---|---|
| Landing | the repaired bridge ends at a stone arch; **checkpoint A** (banner + bed) |
| **Crude Smithy** | a ruined hut with a Workbench slot, 8 bushes, 6 boulders (fibre, sticks, rubble) |
| **Mob camp** | 12 mobs in **3 groups of 4** (two groups of **Skeleton Fighters**, one of **wolves**), all **Lv 1-3** (`bands.islands`); the vanilla Zone 1 "Tier 1" list (Mob-Levels-Plan 5.3) |
| Fight ring | a flat ring 20 across with two rock walls to hide behind and a small raised mound |
| Chest | a loot chest on the far side (a few coins, 20 arrows, a Crude shortbow if the player's class is Archer; class-aware lean 50%) |
| Edge | the west edge faces shard 1 (repaired), the east edge faces shard 3 (**16-block gap with only the first 3 blocks of stone**) |

## 4. Shard 3 - toll shard and portal plaza (R 26)

| Feature | Details |
|---|---|
| Landing | the player's **own bridge** ends at a small stone dock; **checkpoint B** |
| **Camp** | 6 **Trork** mobs (Trork Warriors Lv 3-5) around a fire and tent; barrels with fibre, a few coins |
| **Toll hut** | a wooden booth with a lowered gate; **Warden Gumbo** stands in front (Lv 6 Trork Warrior with boss scaling x6 health) - **optional now** (section 6) |
| **Portal plaza** | a circular stone plaza 14 across, **the portal frame ("the one with the sad face")** at its east side, dark until the Portal Shard is placed; benches, lanterns, a signpost "Department of Arrivals - next stop" |
| Arena | the 26-radius ring around the hut with fences on three sides; a ramp |
| Exit | the portal to the Zone 1 hub (see section 6) |

## 5. Bridges (repair vs build) in detail
| Gap | What the player does | Materials |
|---|---|---|
| **1 -> 2 (14 blocks)** | the posts and 4 planks stand; the player places the **missing planks** (a "ghost" outline of the missing block positions shows via a helper block or particle; the repair kit recipe makes 12 planks in one craft) | 24 planks + 8 sticks + 6 fibre (kit) |
| **2 -> 3 (16 blocks)** | the player **builds across freely** (3 wide); the first 3 stone blocks exist as a hint | 48 blocks; the cave's stone covers it |
Rules: block placement in the void is allowed **only inside the starter extension** (a no-build void band elsewhere; compare `Zone-Islands-Layout.md` section 5). Fall = respawn at the last checkpoint with no coin loss in the starter chain (a row `starter.deathPenalty=false`).

## 6. The portal and the boss ("add the boss later")
| Stage | Behaviour |
|---|---|
| **Now (no boss)** | the **Portal Shard** is a **chest reward at the toll hut** (guarded by the 6 Trorks); placing it in the frame lights the portal; Warden Gumbo is **not spawned** (row `starter.gumbo.enabled=false`) |
| Later (boss) | Gumbo spawns, drops the Portal Shard (the Story-Script quest 11 text); the chest then holds only coins |
| **Portal target** | row `starter.portalTarget`: **`hub`** (the existing `/hub`, today's temple town) until SkyyWorldGen exists, then **`zone1`** (the Zone 1 island landing town, Zone-Islands-Layout) |
| First warp | arriving unlocks the first warp (Exploration) as in the story |

## 7. Islands that already exist (options)
| Option | What | When to use |
|---|---|---|
| **A. New islands only (recommended default)** | new profiles get the new template; existing islands are **not touched** | always |
| **B. "Add the chain" on request** | an island menu button (owner only) appends shards 2-3 **to the east extension chunks** of an existing island **without changing shard 1**: needs the island box not to extend past x +80 east; if the player has built there, the button is greyed with the reason | players who want the story |
| C. `/island reset` | rebuilds the whole island from the new template (24 h cooldown, 3 confirms - LOCKED) | players who accept losing their build; the reset keeps the Starter chain progress flag |
| D. Existing profiles skip the chain | the quest flag is auto-set for profiles with progress (RESUME / story rule): they get the shards via B only if they ask | always |
**Do not** resize an existing island's shard 1 automatically (builds). The island size tiers (4x4 .. 9x9) stay a separate purchase and **never extend east of +80**.

## 8. Generation plan (how it is built)
| Step | Work | Tool |
|---|---|---|
| 1 | build the 3-shard template **by hand once in creative** (as the old template was) in a scratch world, then copy the region files into `Server/Instances/SkyyIsland` (new version `SkyyIsland2`); never commit vanilla-derived files: only our own builder output | creative + copy, as SkyyIslands did for v1 |
| 2 | **or** generate by code with `PrefabUtil.paste` and `setBlock`: shard shapes from a script (noise discs), trees and the cave from prefab pieces; deterministic | `tools/` script (local) |
| 3 | spawn points: Pebble's rock, checkpoints A/B, mob camp markers (or a spawn script on entry for shard 2/3) | SkyyIslands code |
| 4 | protect extension chunks: no break / place except the two bridge sections and the player's own box | SkyyIslands guards |
| 5 | the portal frame + plaza prefab; the target row | SkyyIslands / SkyyWorldGen |
| 6 | the quest hooks: positions, flags (SkyyQuests) | SkyyQuests |
| 7 | `starter.*` rows in Server Setup | config kit |
| Template size | about 32 chunks of blocks (a few hundred KB) | |

## 9. Safety and tests
| Test | Pass |
|---|---|
| New profile arrives on shard 1; Pebble and the chest are there | yes |
| All 12 quests are completable with the shard resources only (no outside items) | budget table |
| A death on shard 2 respawns at checkpoint A (no coin loss) | row |
| Hostile mobs on shard 1: none; on shard 2: 12; on shard 3: 6 (+ Gumbo if enabled) | counts |
| Visitors (co-op members) walk the shards but the Portal Shard drops per profile | profile flag |
| Existing island untouched after the update (hash of region files) | A |
| Island box upgrade 4x4 .. 9x9 does not move or overwrite shards 2-3 | east limit |

## 10. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Island template box size / terrain extent today (the "3x" is measured against it; I assumed about 3,000 blocks of usable ground). |
| 2 | Whether chunks outside the 3x3 box exist in the template and can hold the shards; `bands.islands` there; whether the box limit uses a build-protection region or WorldConfig bounds. |
| 3 | Hostile spawning on a copied island world (WorldGen plan stage 0 test 2); fallback script spawn. |
| 4 | Whether a chest guarded by mobs can hold the Portal Shard as a quest item (SkyyQuests). |
| 5 | The vanilla Tier 1 mob names and Trork roles (Skeleton_Fighter, Wolf, Trork_Warrior). |
| 6 | Wheat growth time and the starter chest seeds. |
| 7 | Where `/hub` points today (the portal target default). |

## 11. Questions for Skyy
1. Default box 5 x 5 chunks (about 2.8x area) and the east side fixed at +80: OK?
2. Portal Shard from a chest now, Gumbo later - or keep Gumbo from the start?
3. For existing islands: option A only, or A + B ("Add the chain" button)?
