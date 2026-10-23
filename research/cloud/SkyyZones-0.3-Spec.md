# SkyyZones 0.3 - build spec (Z3 whole trees + crops, Z3b scaffolding, Z4 gates + fair play) (2026-10-23)

Cloud draft, docs only, no game files read. Inputs: `research/cloud/SkyyZones-Spec-Check.md`, `research/cloud/Zone-Gathering-Review.md`,
`research/cloud/Zone-Regen-Spec.md` (sections 3.4, 4.4, 4.5, 5, 6, 7), the shipped `SkyyZones/build_skyyzones_0.2.0.py` header and config rows,
`SkyySkills/build_skyyskills_0.4.63.py` (felled-tree code, 0.4.2 notes), `tools/tier_tags.py`, `tools/CONFIG-CONTRACT.md`, `tools/deploy_set.py`
(read only). Every default in those drafts is taken (Skyy 2026-10-20 "figure it out" / "recommended on all") unless a line below says otherwise.
Anything that needs `HytaleServer.jar`, `Assets.zip` or a live world is marked **UNVERIFIED** and listed at the end.

## Decisions followed (quoted, not re-decided)

| Source | Skyy's words / the locked line | What this spec does with it |
|---|---|---|
| Skyy 2026-10-23 (relayed by the local session; to be recorded in `docs/answered/world.md`) - answer to `research/cloud/Zone-Gathering-Review.md` Question 1 (ore veins outside spots) | "unbreakable. (instead of gathering spots, i plan to make pretty much the entire island besides the towns a gathering location." | NEW MODEL (section 1.1): a whole zone island is ONE gathering area; towns are carved out as FULL regions; outside a gathering area every block (ore, tree, crop too) is unbreakable. No small "spots". Supersedes the spot sizing / spot list parts of `research/Zone-Gathering-Spec.md` and review G7. |
| `docs/answered/world.md` line 63 | "they will all be protected, and to the mining and gathering like skyblock does" | Only listed resource blocks break; everything else stays FULL. |
| `docs/answered/world.md` line 75 | "placing is limited to a few things like scaffolding that vanishes after a few seconds" + "trees break down, then respawn after a bit." | Z3b scaffolding; Z3 trees fall whole and come back (no stump). |
| `docs/answered/world.md` line 115 | "Build SkyyZones (Recommended)" | One mod; no pack mod (Protect Area ARR). |
| `docs/answered/world.md` line 120 | spec defaults taken: "45-90 s trees; break gate Iron 10 / Thorium-Cobalt 20 / Adamantite 30 / Mithril 40; ... anti-AFK 15 min + 300 breaks/min; contested limit 120 / 10 min; ... scaffolding only 8 s x 24 with the item; ... no ghost preview; one hit fells a tree" | All numbers below. |
| `docs/answered/world.md` line 118 | "lock collecting with F to the same limits as your tool" | Unchanged (SkyyGear's tier lock); SkyyZones adds the SKILL gate on top. |
| `docs/answered/world.md` lines 106, 122 | Hub farm + crop islands 100 / 300 / 800 | Crop regrow (Z3) is what makes zone farming work (review R4: SkyyZones 0.3 is the first gathering round). Since the town is FULL, a hub farm inside the town is its own small SKYBLOCK region with `crops`. |
| `docs/answered/gear.md` line 145 | "i wouldnt allow vein mine on a hammer" ... "when breaking ore, only breaks the connected ore of that type" | Vein Mine extras pass the same guard; hammers stay one block in protected worlds (already true: each extra is a real event). |
| `docs/answered/gear.md` line 66 | Tree Feller "should REUSE that mechanic ... instead of a second felling system" | In a gathering area the whole tree falls anyway; Tree Feller extras on a falling tree are refused as "growing back" spots, so it can never pay twice. |
| `docs/answered/project.md` line 12 (R9) | "tree felling XP (felled logs full XP + collections, leaves normal XP, placed logs never)" | We keep SkyySkills' felled-tree crediting; we only add the snapshot, the clean-up and the respawn. |
| `docs/answered/economy.md` line 147 | "dont gate anything for 'Other players'" | Every new part defaults ON (scaffolding, gates, fair-play rules). |
| `PROJECT-RULES.md` section 2 (check existing mods) | survey in `docs/answered/world.md` line 75 (Block Regen, Aura BlockFill, OrbisGuard, HyProtect, VoidProtect) + line 115 | No fit to pack; ideas only (per-block delay from Block Regen). Nothing new to survey for Z3 / Z3b / Z4. |
| `PROJECT-RULES.md` section 4 | times in seconds, Server Setup for everything, one-time migrations only rewrite old defaults | Section 4 rows, section 5 migration. |

## 1. What 0.3 adds (plain words)

0. **Whole island = gathering area (Skyy 2026-10-23):** a zone island outside its towns is one gathering area (section 1.1); everything not
   listed, and everything inside a town, is unbreakable.
1. **Whole trees (Z3):** anywhere in a gathering area, breaking one trunk block brings the whole tree down (logs + leaves drop as vanilla, XP and
   collections as today). The spot stays bare, then the exact tree comes back after 45 / 60 / 90 s (by the wood's zone).
2. **Crops (Z3):** in a gathering area, only RIPE listed crops break or F-harvest. The crop drops back to its first stage and is ripe again 10 s later.
3. **New zone ores (Z3, review G3):** Lead, Chromium, Slag and Titanium get their own resource types and regrow times (6 / 8 / 10 / 12 s).
4. **Scaffolding (Z3b):** a new item "Scaffolding" may be placed in gathering areas (so across the island, never in or touching a town); it vanishes after 8 s, at most 24 per player, gives nothing back.
5. **Skill gates (Z4):** breaking a listed block can need a skill level (Iron Mining 10, Thorium / Cobalt 20, Adamantite 30, Mithril 40); walking in stays free.
6. **Fair play (Z4):** anti-AFK (15 min standing in one place), a 300 breaks / minute cap, "let others have a turn" only when a 16-block patch is contested,
   a 3 s hit lock against block sniping, and a bot-rhythm FLAG (no punishment) on `/zones status`.

### 1.1 The island-wide gathering model (Skyy 2026-10-23, Builder A, 0.3.0)

"Unbreakable" = exactly today's refusal: no crack, no drop, no XP, no collection (cancelled DamageBlockEvent / BreakBlockEvent, probes Z18 / Z19
answered in `SkyyZones/build_skyyzones_0.2.0.py`). It covers every block that is not a listed resource type of the gathering area: dirt, grass,
sand, leaves, plants, builds, wood decor, and ALSO ore / logs / crops that lie outside a gathering area (towns, decor, the void rim).

| Layer (first match wins) | Where | Mode | Breakable |
|---|---|---|---|
| 1 | builder mode / `zones.opBypass` | - | everything (unchanged) |
| 2 | inside any region (highest priority wins, as 0.1.0) | the region's mode | FULL: nothing. SKYBLOCK: the union of the SKYBLOCK regions' types there + the world's `gather.types` if the world is a gathering world |
| 3 | NEW: a world listed in `zones.gatherWorlds`, no region at that spot | SKYBLOCK | the `gather.types` list only (default: every ore type, `gem`, `logs`, `crops` - NOT `stone`) |
| 4 | a world in `zones.worlds`, no region | FULL | nothing (unchanged) |
| 5 | any other world | not protected | vanilla (player islands, shards, solo pack - unchanged) |

What an admin does per zone island (no huge boxes, no spot list):

1. Server Setup -> Zones -> Protection: add the zone world to `zones.worlds` AND to `zones.gatherWorlds` (the check hook refuses a gather world
   that is not also protected, so a rollback to 0.2.0 - which ignores `zones.gatherWorlds` - fails CLOSED: the island turns fully FULL, never open).
2. `/zones wand` + `/zones region create <town> full` around each town (plus `addbox` for odd shapes): the town is carved out. Towns need no
   priority trick: any region beats the world layer.
3. Mines where stone should break too: `/zones region create <mine> skyblock stone` (stone joins the island's types there - union rule).
4. Per-zone gates when several zones share one world: a SKYBLOCK region over that zone's part with `gate` (0.3.1); one zone per world needs only the type gates.

Effects: the 64-box / 512 x 384 x 512 box limits no longer matter for islands; region lookup is cheaper (no boxes at all for most breaks);
`zones:fn:check` answers the same layers; `/zones info` says "Gathering area (whole island)" / "Town - protected"; the area title shows
"Gathering area" when you leave a town. `regen.maxDepleted` (20,000 a world): a felled tree counts as ONE entry (its positions sit in a
separate set), so a busy island never pushes ore back early because of trees.

Not in 0.3 (stays Z5 or later): drops straight to inventory (probe Z8), the overcrowding log, per-address limits (Z12), `gateEntry`, a ghost
preview, the zone-special multiplier, SkyyTowns using SkyyZones, fixing hoe / bucket writes (no engine event, `SkyyZones/build_skyyzones_0.2.0.py` GAP note).

## 2. Versions, builders, order

| Step | Builder (model) | Mod it touches (only this one) | Output | Round |
|---|---|---|---|---|
| 0 | Probe builder (Opus) | NEW `SkyyZoneProbe/` (op-only probe mod, never pinned in the SET; like `SkyyGatherProbe/`) | `SkyyZoneProbe/build_skyyzoneprobe_0.1.0.py` | lean; one Skyy test session (section 9 steps P1-P6) |
| 1 | Builder A (Opus) | `SkyyZones` 0.2.0 -> **0.3.0** (island-wide gathering layer 1.1 + Z3 trees + crops + new ore types + migration Mig030) | `tools/zones_0_3_0_patch.py` -> `SkyyZones/build_skyyzones_0.3.0.py`, `SkyyZones/test_skyyzones_0.3.0.py` | **full** (saved data, migration, item dupe risk) |
| 2 | Builder B (Opus), after A is reviewed + fixed | `SkyyZones` 0.3.0 -> **0.3.1** (Z3b scaffolding + Z4 gates + fair play) | `tools/zones_0_3_1_patch.py` -> `SkyyZones/build_skyyzones_0.3.1.py`, `SkyyZones/test_skyyzones_0.3.1.py` | **full** (new item, permissions / commands, saved data) |
| 3 | Builder C (Opus), parallel to A | `SkyySkills` 0.4.63 -> **0.4.64** (one change: a block placed in SkyyZones builder mode is NOT marked "placed") | `tools/skills_0_4_64_patch.py` -> `SkyySkills/build_skyyskills_0.4.64.py` | lean (one behaviour, no saved-data format change) |
| Review | Sonnet critics per builder (lenses: dupes / lost items, restart safety, migration, perm leaks, UI wording) | - | - | - |

Why C: hired builders place every server ore and tree in builder mode. SkyySkills' `PlacedStore` marks every PlaceBlockEvent
(`SkyySkills/build_skyyskills_0.4.63.py` line 18385 and the 0.4.2 notes: "natural only (not in PlacedStore ...)"), so the FIRST break / fell of a
hand-built resource pays no XP (a regrown block pays again, probe Z5). Fix in C: at PlaceBlockEvent, skip the mark when bridge
`zones:build:<uuid>` is TRUE (key already published by SkyyZones 0.1.0). UNVERIFIED: whether PlacedStore survives a restart (if it does,
blocks placed before 0.4.64 stay marked until broken once - acceptable; note in the test).

Launch with the saved workflow `.claude/workflows/skywynn-round.js` (Workflow `skywynn-round`), `quotes` = the `docs/answered/world.md` line 75
and line 120 words above. Builders follow `tools/AGENT-BRIEF.md` (patch scripts: edit the patch, never the generated script; no commits; no deploy).

## 3. Exact ids, keys, files, lang keys

### 3.1 New / changed ids

| Thing | Id / key | Notes |
|---|---|---|
| Scaffolding item + block (0.3.1) | `Skyy_Scaffold` | SkyyZones asset (`Server/Item/Items/SkyyZones/Skyy_Scaffold.json`, generated at build time like `Skyy_Zones_Wand`); vanilla look BY PATH (a plank / lattice model + texture from `Assets.zip`, never copied into git). Block json pattern: `SkyyIslands/build_skyyislands_0.5.24.py` line 8963 (a `BlockType` with DrawType / Material). UNVERIFIED: which vanilla model fits, and that a climbable or solid-top scaffold is possible. |
| Scaffold recipe | Workbench, 4 sticks -> 8 `Skyy_Scaffold` | Question 2. Stick id UNVERIFIED (build check against `Assets.zip`). |
| New resource types (0.3.0) | `type.lead=Ore_Lead_Sandstone_SkyWynn`, `type.chromium=Ore_Chromium_Shale_SkyWynn`, `type.slag=Ore_Slag_Volcanic_SkyWynn`, `type.titanium=Ore_Titanium_Basalt_SkyWynn` | EXACT ids from `tools/tier_tags.py` `ZONE_METALS` (family `zone_ore_block`). Never `Ore_Lead*`: TerrariaToolsWeapons owns `Ore_Lead*` ids (`tools/tier_tags.py` comment). The build check accepts an id from `Assets.zip` OR `tools/tier_tags.py` `WG_IDS` (SkyyWorldGen makes them). |
| Tree wood groups (0.3.0, build time) | `TREE_GROUP` = wood -> 1 / 2 / 3 | From `tools/tier_tags.py` `LOGS` (15 tiers, 3 per zone): T1-T3 (Zone 1 woods: Oak, Birch, Beech, Ash, Aspen, Apple, Maple, Azure) = group 1; T4-T6 (Zone 2: Dry, Palm, Bottletree, Amber, Gumboab, Palo) = group 2; T7-T15 (Zones 3-5) = group 3. A wood not in `LOGS` (pack mod) uses the `regrow.logs` seconds. Build asserts all 34 vanilla trunks get a group. |
| Journal lines (0.3.0) | `G x y z <type> <regrowAt ms> <shapeId> <group>` (tree down), `R x y z` (tree back, origin) | appended to `regen/<world>.journal` BEFORE the first block changes; 0.2.0 lines (`D`, `R`, `V`) unchanged. |
| Shape store (0.3.0) | `regen/<world>.shapes`: `S <shapeId> <count>` then `<dx> <dy> <dz> <blockId> <rotation>` lines | append-only, written + flushed before the `G` line; compacted with the 60 s snapshot (shapes no `G` entry uses are dropped); identical shapes share an id (hash of the lines). |
| Crop entries (0.3.0) | the normal `D` line with type `crops`, placeholder token `stage1` | restore writes the crop's ripe state (UNVERIFIED how - probe P3). |
| Scaffold lines (0.3.1) | `T x y z <blockId> <vanishAt ms> <uuid>` | before the place is allowed; on start every due `T` is removed (loaded chunk now, else at chunk load). |
| Region fields (0.3.1) | `region.<id>.gate=Mining:10[,Foraging:5]` and `region.<id>.placeAllow=<ids, comma>` (`none` = nothing) | already kept verbatim since 0.1.0 (`SkyyZones/build_skyyzones_0.2.0.py` line 1519) - now read. No `placeAllow` line = the `scaffold.ids` row. |
| Bridge | `zones:version` "0.3.0" / "0.3.1"; `zones:fn:check` unchanged signature, new action `harvest` (F-harvest of a crop) | waiting tree / crop / scaffold spots answer `deny` for break / place like 0.2.0 waiting spots. |
| Skill level read (0.3.1) | `skill:fn:level` apply(Object[]{ UUID, String skill }) -> Number | same call as `SkyyGear/build_skyygear_0.3.40.py` line 18608. -2 (no SkyySkills) = gates off, warned once; an unknown skill name is refused in Server Setup. |

### 3.2 Commands (all under `/zones`, admin subcommands: `requirePermission(...)` + `setPermissionGroups(new String[0])`, lint `perm_group_leaks`)

| Command | Version | Does |
|---|---|---|
| `/zones region gate <id> <Skill:Level[,Skill:Level]\|none>` | 0.3.1 | sets / clears `region.<id>.gate` (skyyzones.admin) |
| `/zones place add <id> <ids\|look>` / `/zones place remove <id> <ids>` | 0.3.1 | the region's `placeAllow` list (skyyzones.admin) |
| `/zones info` | 0.3.0 / 0.3.1 | + "Tree down: grows back in N s (shape 312 blocks)", "Crop: ripe / not ripe", "Scaffold: vanishes in N s", "Needs Mining 10 (you: 7)" |
| `/zones status` | 0.3.0 / 0.3.1 | + trees down per world, crops waiting, scaffolds live, refused breaks last hour per reason (gate / afk / rate / turn / hit lock), flagged players (name + why) |
| `/zones restore <id\|all>` | 0.3.0 / 0.3.1 | + every felled tree written back, every crop ripe, every scaffold removed (REQUIRED before any rollback) |

### 3.3 Lang keys (only SkyyZones writes them; `tools/ci/langdup.py` keeps one writer per key)

| Key (both `items.` and `server.items.` like the wand) | Text |
|---|---|
| `items.Skyy_Scaffold.name` | Scaffolding |
| `items.Skyy_Scaffold.description` | Style Guide section 15 colours (as `WAND_DESC`): yellow "Place:" + soft white "a short-lived block in gathering areas" / dim grey "Vanishes after a few seconds. Gives nothing back." |

Player messages (action bar, at most one per `msg.gapSec` 2 s, vanilla notification, no chat spam): "This area is protected." (as now),
"Growing back - wait a moment." (as now), "This tree is growing back.", "Not ripe yet.", "Requires Mining 10 (you: 7).",
"Stretch your legs - move a little to keep mining.", "Slow down a little.", "Let others have a turn - try another vein.",
"Someone else is mining this block.", "Scaffolding can't go here.", "Too far away.", "This tree is too big to regrow - tell an admin."

### 3.4 Tier tags (`tools/tier_tags.py` rules)

- No new TIERED item: `Skyy_Scaffold` has no tier (like stone / dirt: "Left untagged on purpose" family) -> no tag, not added to the table.
- `tools/tier_tags.py` is IMPORTED read-only at build time for `LOGS` (tree groups) and `ZONE_METALS` / `WG_IDS` (new ore types). If a round adds a
  tiered item later, it goes into that table first (PROJECT-RULES 4).
- SkyyZones writes no lang key for any vanilla / SkyyWorldGen / pack id (the tags of logs, crops and ores stay SkyyCollections' and SkyyWorldGen's).

## 4. Server Setup rows (SkyWynn Menu -> Server Setup -> Zones; `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`)

Rules kept: every setting has a row, game and file agree, times in seconds (`s`), distances in `blocks`, KEEP=10, `0 = off` where said,
`danger` on part switches that put blocks back. New pages: `trees` "Trees + crops", `scaffold` "Scaffolding", `guard` "Gates + fair play".

| Key | Label | Page | Type | Default | Min-max | Unit | Flags | File | Ver |
|---|---|---|---|---|---|---|---|---|---|
| `zones.gatherWorlds` | Whole-world gathering areas (towns = FULL regions) | zones | text | empty | 0-400 chars | - | live | `Skyy_SkyyZones/config.properties` (key absent = default, no migration) | 0.3.0 |
| `gather.types` | Resource types in a gathering world | zones | text | `copper,iron,gold,silver,thorium,cobalt,adamantite,mithril,onyxium,lead,chromium,slag,titanium,gem,logs,crops` | 0-400 chars | - | live | same | 0.3.0 |
| `regrow` table: `logs` | (existing table) | regen | int\|text | **60,none** (was 0,none) | 0-3600 | s | live | `Skyy_SkyyZones/regen.properties` | 0.3.0 |
| `regrow` table: `crops` | (existing table) | regen | int\|text | **10,stage1** (was 0,none) | 0-3600 | s | live | same | 0.3.0 |
| `regrow` table: `lead` / `chromium` / `slag` / `titanium` | (existing table) | regen | int\|text | 6 / 8 / 10 / 12, `Rock_Bedrock` | 0-3600 | s | live | same | 0.3.0 |
| `type` table: `lead` / `chromium` / `slag` / `titanium` | (existing table) | types | text | ids in 3.1 | - | - | live | `Skyy_SkyyZones/types.properties` | 0.3.0 |
| `tree.sec1` | Trees grow back (Zone 1 woods) | trees | int | 45 | 5-3600 | s | live | `Skyy_SkyyZones/trees.properties` (new) | 0.3.0 |
| `tree.sec2` | Trees grow back (Zone 2 woods) | trees | int | 60 | 5-3600 | s | live | same | 0.3.0 |
| `tree.sec3` | Trees grow back (Zone 3-5 woods) | trees | int | 90 | 5-3600 | s | live | same | 0.3.0 |
| `tree.maxBlocks` | Biggest tree that regrows | trees | int | 600 | 50-4000 | blocks | live,adv | same | 0.3.0 |
| `tree.clearSec` | Clear what is left of a tree after | trees | int | 3 | 1-30 | s | live,adv | same | 0.3.0 |
| `scaffold.on` | Scaffolding in gathering areas | scaffold | bool | true | - | - | live,danger | `Skyy_SkyyZones/scaffold.properties` (new) | 0.3.1 |
| `scaffold.ids` | Blocks players may place (default list) | scaffold | text | `Skyy_Scaffold` | 0-400 chars | - | live,adv | same | 0.3.1 |
| `scaffold.lifeSec` | Scaffolding vanishes after | scaffold | int | 8 | 2-120 | s | live | same | 0.3.1 |
| `scaffold.maxPerPlayer` | Most scaffolding per player | scaffold | int | 24 | 1-200 | - | live | same | 0.3.1 |
| `scaffold.reach` | Scaffolding reach | scaffold | int | 6 | 2-12 | blocks | live,adv | same | 0.3.1 |
| `gates.on` | Skill gates | guard | bool | true | - | - | live | `Skyy_SkyyZones/guard.properties` (new) | 0.3.1 |
| `gate` table: type -> Skill \| Level | Skill needed per resource type | guard | text\|int | iron Mining 10; thorium, cobalt, lead, chromium Mining 20; adamantite, slag Mining 30; mithril, titanium Mining 40; onyxium Mining 45 | level 0-100 | - | live | same | 0.3.1 |
| `abuse.on` | Fair-play rules | guard | bool | true | - | - | live | same | 0.3.1 |
| `abuse.afkSec` | Stop breaks after standing still | guard | int | 900 | 0 (off), 60-7200 | s | live | same | 0.3.1 |
| `abuse.afkRadius` | Counts as standing still within | guard | int | 4 | 1-16 | blocks | live,adv | same | 0.3.1 |
| `abuse.afkMove` | Move this far to mine again | guard | int | 8 | 2-32 | blocks | live,adv | same | 0.3.1 |
| `abuse.maxPerMin` | Most breaks a minute | guard | int | 300 | 0 (off), 30-3000 | - | live | same | 0.3.1 |
| `abuse.rateRestSec` | Pause after too many breaks | guard | int | 10 | 1-120 | s | live,adv | same | 0.3.1 |
| `abuse.cellCap` | Turn limit on a busy patch | guard | int | 120 | 0 (off), 10-5000 | - | live | same | 0.3.1 |
| `abuse.cellWindowSec` | Turn limit counts over | guard | int | 600 | 60-3600 | s | live | same | 0.3.1 |
| `abuse.cellRestSec` | Turn limit pause | guard | int | 60 | 5-600 | s | live | same | 0.3.1 |
| `abuse.cellSize` | Busy patch size (cube side) | guard | int | 16 | 4-64 | blocks | live,adv | same | 0.3.1 |
| `abuse.contestSec` | Patch counts as busy for | guard | int | 60 | 5-600 | s | live,adv | same | 0.3.1 |
| `abuse.hitLockSec` | Hit lock (others' half-mined blocks) | guard | int | 3 | 0 (off), 1-10 | s | live | same | 0.3.1 |
| `abuse.botFlag` | Flag perfect-rhythm breaking | guard | bool | true | - | - | live,adv | same | 0.3.1 |
| `abuse.botGapMs` | Rhythm spread below this = flag | guard | int | 15 | 1-200 | ms | live,adv | same | 0.3.1 |
| `abuse.botSample` | Breaks checked for rhythm | guard | int | 200 | 50-2000 | - | live,adv | same | 0.3.1 |
| Regions table: + `gate` and `placeAllow` in the editable composite | Regions | regions | (custom `ZRegKit`) | - | 200 chars a cell | - | live | `Skyy_SkyyZones/regions.properties` | 0.3.1 |

Notes: `abuse.botGapMs` is the one sub-second threshold, so it stays in `ms` (an allowed unit in `tools/CONFIG-CONTRACT.md`); every other time
is seconds. Check hooks: `stage1` is accepted only on the `crops` row and `none` is required on `logs` (no stump); a gate skill must be one
SkyySkills answers (-1 = refused); `scaffold.ids` ids must exist and must not be a listed resource block (no "place an ore to mine it" path, spec 7 X1).
The two new pages say on screen: "Regions: world, boxes, new and deleted regions are commands (wand corners)" (spec check 3a).
`zones.gatherWorlds` check hook: every name must also be in `zones.worlds` (fail closed on rollback) and must not be a player island / shard
world (`skyy-island-*`, `skyy-shard-*`); `gather.types` names must be existing types. How Server Setup edits regions under the island model:
the island itself is two rows (`zones.gatherWorlds`, `gather.types`); towns / mines / per-zone gate areas stay rows of the existing Regions table
(mode, priority, types, flags, title, and in 0.3.1 gate + placeAllow editable there; boxes and new regions by `/zones wand`).

## 5. One-time migration Mig030 (0.3.0, PROJECT-RULES 4)

| Step | Rule |
|---|---|
| Marker | `Skyy_SkyyZones/migrate-0.3.0.done` - present = do nothing |
| Snapshot first | copy `regen.properties` + `types.properties` into the kit's `config-history/` (verified readable) BEFORE any write; a failed copy = no migration, warned |
| `regrow.logs` / `regrow.crops` | rewrite ONLY a line still holding the 0.2.0 default text `0,none` -> `60,none` / `10,stage1`; any other value kept + logged ("regrow.logs hand-edited to X - kept") |
| New types / rows | append `type.lead` ... `type.titanium` and `regrow.lead` ... `regrow.titanium` ONLY if that key is absent; never touch a present line |
| Bytes | the file's own line endings (CRLF or LF) and every other byte kept; the kit's line-preserving writer |
| Log + Undo | one Server Setup -> Changes line per changed key (`via=migration`) so Undo works |
| New files | `trees.properties`, `scaffold.properties`, `guard.properties` are seeded from DEFAULTS (missing file = written once, like `regen.properties` in 0.2.0) - no migration |

## 6. Behaviour rules the builders must keep

### 6.1 Trees (Builder A)

1. Trigger: a hand break (or Vein / Feller extra) of a `logs` block in a gathering area (SKYBLOCK region or gathering world, 1.1), not builder
   mode. A tree that crosses into a town (FULL) region: refused whole ("This area is protected.") - never half a tree.
2. ZGuard (first system, still standing): breadth-first search over the 26 neighbours - trunk / branch / roots ids of the SAME wood + connected
   `Plant_Leaves_*` (reuse SkyySkills' FellDefs idea: wood + leaf families from `Assets.zip` at build time), up to `tree.maxBlocks`. Over the cap:
   the break is REFUSED ("This tree is too big to regrow - tell an admin", logged with position) - never a hole forever.
3. Write order: shape (`.shapes`, flushed) -> `G` line (flushed) -> mark every shape position as waiting -> let the event through. A failed write
   CANCELS the break (no drop), as 0.2.0.
4. The engine's physics fells the rest (no event; `SkyySkills/build_skyyskills_0.4.63.py` 0.4.2 notes) and SkyySkills credits the felled logs
   (unchanged). After `tree.clearSec`, any shape block still standing (thick-tree base logs, stuck leaves) is broken with `performBlockBreak` as
   that player (one real event each, the same way SkyyTrees' Tree Feller does; ZGuard lets these through by a "clearing" position set) - so
   "one hit fells a tree" holds and nothing is paid twice (positions already air are skipped).
5. Other breaks on waiting tree positions (Tree Feller extras, other players): refused "This tree is growing back." (no drop, no XP).
6. Respawn at `regrowAt` (`tree.sec<group>` x `regen.speedMult` x jitter): ALL-OR-NOTHING per tree, trunks bottom-up then leaves, through the
   0.2.0 pass (`regen.passBatch` writes per tick, a big tree may take several ticks). A player inside any shape cell: wait, retry every 1 s; after
   30 tries write it skipping only the occupied cells (they follow when free), warn once. A cell holding something else (admin edit) is left alone,
   logged. Chunk unloaded: restored at chunk load (0.2.0 catch-up). A `V` line + next-start check like 0.2.0 ores (origin still air -> write again).
7. `region deleted / retyped`, `regen.enabled` off, `/zones restore`: trees come back at once (as 0.2.0 ores).
8. Rate cap: a whole tree counts as ONE break.

### 6.2 Crops (Builder A)

- Only a RIPE (StageFinal) listed crop breaks or F-harvests; an unripe one is refused "Not ripe yet." (no drop). Soil stays protected.
- Break: `D` line first, placeholder `stage1` (the same crop at its first stage), at `regrowAt` set it ripe. F-harvest (no break event; the engine
  resets the stage): register the same entry at the F-harvest hook (the 0.1.0 guard already sees it), force ripe at the timer. Vanilla growth ticking
  the placeholder is harmless (entry dropped when already ripe). All ripe-state reads / writes: probe P3 (UNVERIFIED).
- Hoe tilling / watering / fertilizing still have no event (0.1.0 GAP) - unchanged; note in `/zones info`.

### 6.3 Scaffolding (Builder B)

- Allowed only: a gathering area (SKYBLOCK region or gathering world), `scaffold.on`, held item in the region's `placeAllow` (gathering world
  with no region: `scaffold.ids`), target cell is air, every one of its 6 neighbours is also gathering area (never touching a town / FULL
  region), not inside any player's box, within `scaffold.reach` of the player's eyes, not a waiting position.
- Island-wide means scaffolding works on every cliff, but also over the void rim: 24 blocks that vanish after 8 s cannot cross between zone islands
  (they are far apart, `docs/answered/world.md` line 56), so no extra void rule in 0.3 (Question 7).
- `T` line first, then the engine places it (the item is used up as usual; a cancelled place keeps the item - probe Z5b answered in
  `SkyyZones/build_skyyzones_0.2.0.py`). Over `scaffold.maxPerPlayer`: the player's oldest scaffold vanishes first.
- Vanish at `vanishAt`: `setBlock` air only if the cell still holds that scaffold id (no refund, no drop, no event - probe Z5). Hand break of a
  scaffold: event cancelled (no drop, no XP - Z19) and the cell set to air by us. Restart: due `T` entries removed. Each placement counts toward
  `abuse.maxPerMin`.

### 6.4 Gates + fair play (Builder B)

- Gate = the highest of the region's `gate` and the type's `gate` row, per skill; checked on break, F-harvest and the tree trigger. Level read once per
  break through `skill:fn:level` (cached 5 s per player). Walking in is never stopped.
- A1 AFK: anchor = position at the last break that moved more than `abuse.afkRadius`; still within it after `abuse.afkSec` -> regen breaks refused
  until the player is `abuse.afkMove` from the anchor.
- A2 rate: rolling 60 s count; Vein Mine / Tree Feller extras count half (detected as a second break by the same player in the same world tick -
  UNVERIFIED that extras land in the same tick, probe P5); over the cap -> refused `abuse.rateRestSec` + one admin log line.
- C2 turn limit: cell = `abuse.cellSize` cube; only when ANOTHER player broke in that cell within `abuse.contestSec`; more than `abuse.cellCap`
  breaks there in `abuse.cellWindowSec` -> that cell refused for `abuse.cellRestSec`. Solo players are never limited.
- C3 hit lock: a block another player damaged within `abuse.hitLockSec` takes no damage from you (DamageBlockEvent cancel = no crack, probe Z18
  answered). If probe P4 shows damage is per player anyway, the builder sets the default to 0 and says so.
- A3: after `abuse.botSample` breaks, a gap spread under `abuse.botGapMs` puts the player on `/zones status` "flagged" - never a punishment.
- All counters are memory only (reset at restart); builder mode and `zones.opBypass` skip every rule.
- Island-wide impact: players spread over a whole island instead of crowding a few spots, so the turn limit (C2) will bite rarely - it stays as
  the guard for popular veins; the 16-block patch is the unit, not a region. Anti-AFK and the rate cap are per player and unchanged. Memory:
  counters keyed by player + patch, patches older than `abuse.cellWindowSec` pruned each minute (a whole island cannot grow the map without bound).
- Gates: with no per-spot regions, the TYPE gates (`gate` table) carry the rule island-wide; a region `gate` is only needed where several zones
  share one world or for a special area.

## 7. Harness checks (`SkyyZones/test_skyyzones_0.3.0.py`, `SkyyZones/test_skyyzones_0.3.1.py`; bare JVMs, `-Xverify:all`, every new path run)

| # | 0.3.0 check |
|---|---|
| A1 | shape search on synthetic trees: single trunk, 2x2 thick tree, branches + roots, two touching trees of different woods stay separate, leaves of another wood not taken, cap 600 -> refusal |
| A2 | write order: `.shapes` then `G` before any block change; a failing write cancels the break (no drop) |
| A3 | journal replay: 0.2.0 files (`D` / `R` / `V`, torn line, `.bad` copy) read unchanged; `G` + shapes round trip; snapshot compaction drops unused shapes |
| A4 | respawn all-or-nothing, trunks first; occupied cell retry, forced write after 30 tries skipping it; changed cell left + logged; chunk-unloaded catch-up; `V` re-check after a simulated crash |
| A5 | clearing pass: leftover base logs broken through the "clearing" set; air cells skipped; other players' breaks on waiting tree cells refused |
| A6 | `TREE_GROUP` from `tools/tier_tags.py`: Oak 1, Maple 1, Gumboab 2, Redwood 3, Crystal 3; all 34 trunks mapped; unknown wood -> `regrow.logs` seconds |
| A7 | crops: unripe break + F-harvest refused; ripe break -> `stage1` -> ripe at timer; F-harvest entry; already-ripe entry dropped |
| A8 | Mig030: old defaults rewritten, hand-edited kept + logged, snapshot exists before the write, Changes line with Undo, marker, CRLF and LF files byte-identical apart from the changed values, absent type / regrow lines appended, second run no-op |
| A9 | new ore types: ids match `tools/tier_tags.py` `WG_IDS`; no pattern matches `Ore_Lead_*` ids of other mods |
| A0 | layers 1.1: gathering world + no region = `gather.types` only; dirt / leaves / planks / an unlisted ore refused with no crack and no drop; FULL town region inside it refuses ores + logs too; mine region adds `stone` (union); region beats world layer at any priority; a gather world missing from `zones.worlds` refused by the check hook; a tree crossing a town boundary refused whole; a felled tree = one `regen.maxDepleted` entry |
| A10 | kit build check 01 (every key a row, DEFAULTS parse), check hooks (`stage1` only on crops, `none` required on logs), `tools/ci/lint.py` 0 fails, `tools/ci/langdup.py` clean, the jar has no `.ui` file, log line `[SkyyZones] 0.3.0 ready` |

| # | 0.3.1 check |
|---|---|
| B1 | scaffold allow / deny matrix: air only, edge rule (6 neighbours inside), FULL next door, reach, inside a player, waiting spot, `placeAllow` none / list / default |
| B2 | `T` line before the place; vanish at `lifeSec` only if the id is still there; cap 24 oldest-first; restart removes due `T`; hand break = no drop + air; rate cap counts placements |
| B3 | `Skyy_Scaffold` item json + lang keys (both prefixes), description colours from `tools/skyyui.py`, recipe ids exist in `Assets.zip` |
| B4 | gates: max(region, type) per skill; `skill:fn:level` -2 -> gates off + one warning; -1 skill refused in Server Setup; message text with "you: N" |
| B5 | AFK anchor + unlock distance; rate cap with half-weight extras; turn limit only when contested (solo never); hit lock 3 s and 0 = off; bot flag on synthetic gaps (flag only) |
| B6 | `/zones status` + `/zones info` new lines; `/zones region gate`, `/zones place add/remove` permission (lint `perm_group_leaks`); builder mode + op bypass skip every rule |
| B7 | `/zones restore all` also removes scaffolds; log line `[SkyyZones] 0.3.1 ready`; `python tools/smoke_test.py --jar SkyyZones/SkyyZones-0.3.1.jar` PASS |

SkyySkills 0.4.64 (Builder C): a PlaceBlockEvent with `zones:build:<uuid>` TRUE adds no PlacedStore mark; FALSE / missing key = as 0.4.63; the
`[SkyySkills] 0.4.64 ready` line; its own `SkyySkills/test_skyyskills_0.4.64.py`.

Cross-check before pin: `python tools/ci/crosscheck.py --jar SkyyZones/SkyyZones-0.3.1.jar SkyySkills/SkyySkills-0.4.64.jar --baseline`.

## 8. Rollback / FLOOR notes (text for `tools/deploy_set.py`, the main session adds them)

| Pin | FLOOR comment |
|---|---|
| `("SkyyZones", "0.3.0")` | FLOOR (SkyyZones 0.3.0 trees + crops): before rolling back below 0.3.0 run `/zones restore all` (felled trees come back, crops ripe), wait until `/zones status` shows 0 waiting, stop the server. 0.2.0 skips `G` lines (counted as bad lines) and would leave felled trees missing for good. `trees.properties`, `regen/<world>.shapes` and `migrate-0.3.0.done` may stay; 0.2.0 reads `regrow.logs` / `regrow.crops` above 0 as 0 (warned) and ignores the new ore types' regrow (they still break, no regrow). 0.2.0 ignores `zones.gatherWorlds`: those worlds (always also in `zones.worlds`) turn fully FULL - nothing breaks outside drawn SKYBLOCK regions until 0.3.0 is back. |
| `("SkyyZones", "0.3.1")` | FLOOR (SkyyZones 0.3.1 scaffolding): before rolling back below 0.3.1 run `/zones restore all` (removes every scaffold) - 0.3.0 skips `T` lines and would leave scaffolds standing forever. `scaffold.properties` / `guard.properties` may stay. `Skyy_Scaffold` items in inventories become unknown items on 0.3.0 (UNVERIFIED what the engine shows). |
| `("SkyySkills", "0.4.64")` | safe both ways (no saved-data change); on 0.4.63 builder-placed blocks are marked placed again. |

0.3.0 and 0.3.1 can deploy together; SkyySkills 0.4.64 has no dependency either way. Deploy path unchanged (PROJECT-RULES 3: backup, smoke test, `python tools/deploy_set.py --yes`).

## 9. In-game test steps (Skyy; test world copy first, op account + one normal account)

Probe session first (Step 0, `SkyyZoneProbe`, op only):

- P1. `/zoneprobe tree` while looking at a natural tree trunk, then break it: the probe logs every removed block and tick (does the whole tree fall, in how many passes, thick trees?).
- P2. `/zoneprobe tree write` near you: writes a saved tree back around you (stuck, pushed out, or leaves fall?).
- P3. `/zoneprobe crop` on an unripe and a ripe crop: logs the block id / state / stage; F-harvest one; `/zoneprobe crop ripe` sets it ripe.
- P4. Two accounts hit the same block in turn: shared damage or per player?
- P5. With Vein Mine on, mine an ore vein: are the extra breaks in the same tick?
- P6. `/zoneprobe scaffold`: places the candidate scaffold look; can you stand on / climb it?

SkyyZones 0.3.0 + 0.3.1 (after deploy):

0. Op, on a COPY of a zone world: Server Setup -> Zones -> Protection: add the world to "Protected worlds" and "Whole-world gathering areas"; `/zones wand` + `/zones region create town full` around the town. Normal account: outside the town an ore, a log and a ripe crop break; dirt, grass, leaves and a building block do not (no crack, no drop). Inside the town nothing breaks, ores included. `/zones info` says "Gathering area (whole island)" outside and "Town - protected" inside.
0b. Stone outside a mine: refused. `/zones region create mine1 skyblock stone` round a cave: stone breaks there and grows back in 3 s.
1. Normal account: chop one trunk block anywhere on the island - the whole tree falls, logs + leaves drop, Foraging XP + collection count as today.
2. A thick (2x2) tree: one cut brings all of it down within about 3 s; nothing is left floating.
3. Try to place a block or break a leaf where the tree stood: refused. Wait 45 s (Zone 1 wood): the same tree is back, same shape.
4. Stand inside the tree's spot when the timer ends: it waits; step out and it grows back (no trap).
5. Restart the server while a tree is down: it comes back (never stays missing). `/zones status` waiting 0 afterwards.
6. A crop field on the island (outside the town): unripe crop - "Not ripe yet."; ripe crop by break AND by F - drops, back to first stage, ripe again about 10 s later; the crop collection counts.
7. A Lead / Chromium / Slag / Titanium ore in a region: grows back after its own time (6 / 8 / 10 / 12 s), not 5 s. Server Setup -> Zones -> Regrowing blocks shows the rows; Changes shows the migration lines with Undo.
8. Give yourself Scaffolding (or craft it): place it on the island - it vanishes after 8 s; the 25th one makes your first vanish; it gives nothing back; it can't go in a town or touching the town's edge.
9. Restart while scaffolding stands: it is gone after the start.
10. Mining 5 character on Iron anywhere on the island: "Requires Mining 10 (you: 5)." Mining 10 can. `/zones region create grove1 skyblock` + `/zones region gate grove1 Foraging:10` over a forest: a low Foraging character can't fell there, walking in still works.
11. Stand still and mine for 15 min (or set `abuse.afkSec` to 60 for the test): breaks stop with the "Stretch your legs" note; walk 8 blocks and mining works again.
12. Two accounts mine the same small vein: after 120 breaks in 10 min one gets "Let others have a turn"; alone, no limit ever.
13. Account B finishes a block A just hit: no damage for 3 s. `/zones status` shows refused breaks per reason.
14. Builder mode: place an ore, break it with a normal account - Mining XP is paid (SkyySkills 0.4.64).
15. Op: `/zones restore all` - every tree, crop and scaffold back to normal; `/zones status` 0 waiting.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | The skill gates were set before "20 levels per zone" (Iron Mining 10, Thorium / Cobalt 20, Adamantite 30, Mithril 40). Cobalt now sits in Zone 3 (Lv 40+), Adamantite in Zone 4, Mithril in Zone 5. Keep these numbers or move each gate to its metal's band start (Iron 8, Thorium 20, Cobalt 40, Adamantite 60, Mithril 80)? | [keep the locked numbers for 0.3; all are Server Setup rows, revisit at the balance pass] |
| 2 | How do players get Scaffolding? | [craft at the Workbench: 4 sticks -> 8 Scaffolding] |
| 3 | Tree regrow by zone: Zone 1 woods 45 s, Zone 2 woods 60 s, Zone 3-5 woods 90 s. OK? | [yes] |
| 4 | Silver and gold ore regrow time (the builder chose 6 s in 0.2.0). | [keep 6 s] |
| 5 | In gathering areas leaves can't be broken on their own - they only drop when the whole tree falls (so no sickle stick farming in zones). OK? | [yes] |
| 6 | Mushrooms as a gathering crop (Zone 4+): in this round or later? | [later, after the crop probe shows how mushrooms grow] |
| 7 | Scaffolding works across the whole island, also over the void edge (24 blocks, gone after 8 s - too short to cross to another island). OK, or keep it away from the void edge? | [OK as is] |
| 8 | Plain stone (and cobble) outside mines: unbreakable, so players can't dig tunnels through the island; stone breaks only inside mine areas the admins draw. OK? | [yes] |
| 9 | Gems, gold and silver everywhere on the island like the ores? | [yes, in the default island list] |

## For the local session (UNVERIFIED - needs `HytaleServer.jar`, `Assets.zip` or a live world)

1. Natural tree fall (P1, probes Z2 / Z16): whole tree in how many physics passes; thick trees leave base logs; hand-built trees fall the same way.
2. Tree rewrite around a player and leaf behaviour on a rewritten tree (P2, Z16 / Z17); cost of a 600-block rewrite per tick (Z3).
3. Crop stage ids / states, how to read "ripe", how to set ripe from code, whether growth ticks the `stage1` placeholder (P3, Z4); whether `Plant_Crop_*_Block` covers the Mushroom (`Plant_Crop_Mushroom_Cap_Brown`).
4. Block damage shared or per player (P4, Z10) - decides the `abuse.hitLockSec` default.
5. Vein Mine / Tree Feller extras in the same world tick as the hand break (P5) - decides the half-weight detection.
6. A usable vanilla model / texture path for `Skyy_Scaffold` and whether it can be climbed (P6, Z14 follow-up); the stick ingredient id for the recipe.
7. Whether SkyySkills' PlacedStore persists across restarts (Builder C note) and whether hand-built zone blocks placed before 0.4.64 still pay no XP on the first break.
8. The `ZRegKit` composite cell (200 characters) with `gate` + `placeAllow` added - fits for long box lists? Else split into a second table.
9. What a player sees holding `Skyy_Scaffold` after a rollback to 0.3.0 (unknown item).
10. `regen/<world>.shapes` size on a busy server (many different natural trees) and the compaction time on the 60 s snapshot.
12. Island model: which world(s) the hand-built server zones will live in (one world per zone like `skywynn_zones2`, or several zones in one) -
    decides whether per-zone region gates are needed; `docs/answered/world.md` must get Skyy's 2026-10-23 "unbreakable ..." line (local session records it).
13. Peak waiting entries on a whole island (generated veins everywhere, natural trees): measure `/zones status` after a play session; shapes file
    growth with many unique natural trees; memory of the patch counters.
14. Natural generated trees near the void edge or over caves: does physics fell them the same, and does a respawn over a cave hold (support)?
15. `research/Zone-Gathering-Spec.md` and `research/cloud/Zone-Gathering-Review.md` still describe small spots (G7 spot sizing, spot lists) -
    main session: mark them superseded by the island model.
11. `research/cloud/Zone-Regen-Spec.md` section 6 forest / farm gates (Foraging 10 / 20 ..., Farming 10 / 20 ...) are not type rows here - admins set them per region with `/zones region gate`; confirm that is enough for the first hand-built zone.
