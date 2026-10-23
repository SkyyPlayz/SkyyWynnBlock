# Zone gathering spots spec - review (2026-10-23)

Reviews `research/Zone-Gathering-Spec.md` (written 2026-10-18) against `research/cloud/Ore-Regrow-Spec.md`, `research/cloud/Zone-Regen-Spec.md`,
`research/Zone-Ores-Alloys-Spec.md`, `research/cloud/Zone-4-5-Materials.md` and the Zone-5 crop rule. Docs only; nothing built, no game files read.

## Decisions followed

- `docs/answered/world.md` 2026-10-17 WARPS FOR PLAYERS: "i plan to make spots dedicated to each in each zone ... lock seeds behind collections ...
  100 to make the island. 200 more to upgrade it. then 500 to upgrade it to T3 ... 800 eternal carrots" (the root of the spec).
- `docs/answered/world.md` 2026-10-22 CROP ISLANDS (popup): Skyy chose "100 / 300 / 800" - spec Q1 is CONFIRMED; its other 9 questions take
  their defaults (Skyy 2026-10-20 "recommended on all"). So the 10 questions in the spec are all closed; only the gaps below remain.
- `docs/answered/world.md` 2026-10-18 GATHERING TIER LOCK + ZONE SPAWNS: F-pickup limited to your tool's tier; crops/trees spawn only around
  their zone (Zone 1 shows up to T5; first mushrooms in Zone 4); ore generation left as set.
- `docs/answered/world.md` 2026-10-18 (add): "in zone 5 you can find every crop type, but mostly just the 3 for zone 5" (Potato, Onion, Mushroom).
- `docs/answered/world.md` 2026-10-20 SKYYZONES SPEC DEFAULTS: every default of `research/cloud/Zone-Regen-Spec.md` taken (3-15 s ore regrow,
  45-90 s trees, gates Iron 10 / Thorium-Cobalt 20 / Adamantite 30 / Mithril 40).
- `docs/answered/world.md` 2026-10-18 PROTECT AREA -> OUR OWN SKYYZONES; 2026-10-10 / 10-15 server world plan + two protection kinds (LOCKED).
- `docs/answered/economy.md` 2026-10-16 ETERNAL SEEDS LOCKED BY COLLECTION (tier 4, row `eternal.tier`) and 2026-10-05 crop order (vanilla Farming Bench).
- `docs/answered/project.md` PROJECT-RULES 2 (check existing mods, no duplicates) - the spec's section 2 survey is Mods-folder only (see UNVERIFIED).

## 1. What shipped since the spec (so what is still useful)

| Piece | Spec said (10-18) | Now (10-23) | Effect on the spec |
|---|---|---|---|
| `SkyyZones` | "WRITTEN, NOT BUILT, no folder" | `SkyyZones/` exists; 0.1.0 protection (FULL / SKYBLOCK regions, builder mode, wand, area titles) + 0.2.0 (Z2) regrow of stone + ores (journal, snapshot, placeholder, catch-up, `/zones status/restore/audit`), LIVE since 2026-10-20 (TEST-CHECKLIST 212, 214) | Spec section 3 "what is needed" and section 6 B1 are mostly DONE for mines. Still open: whole-tree respawn (Zone-Regen Z3), crops (4.4), scaffolding (Z3b), skill gates (Z4), anti-abuse. Build script header: `SkyyZones/build_skyyzones_0.2.0.py`. |
| Regrow numbers | spec section 3 copied Zone-Regen 4.2 | built as `regrow.<type>` rows + `regen.*` rows in `Skyy_SkyyZones/regen.properties` (not `types.properties`) | Spec's row names ("Server Setup rows in seconds") should cite the built names. |
| `SkyyShards` | 0.4.2, grow = 8 / 24 Eternal Wheat seeds | 0.4.5 (P7b, 2026-10-22): "upgrades = 1 h of zone income; idle 20-100 %; storage 3 days"; grow rows in `SkyyShards/build_skyyshards_0.4.5.py` | Section 5 costs (100 / +200 / +500 seeds) now collide with the P7b upgrade pricing; B4 must reconcile (see G5). |
| `SkyyWorldGen` | 0.7.4 | 0.7.8 (spawn remap for new chunks only, 369 ids); new ores Lead / Chromium / Slag / Titanium + Electrum shipped (Zone-Ores spec section 8) | Ore columns of the spec's zone table are real now; the regrow `type.` table must list the new ores (G3). |
| `SkyyCollections` | 0.2.24 eternal lock | 0.2.32; `eternal.tier` live; NO `seed.tier` / `coll:fn:seed` yet (nothing in the log) | B2 / B3 still entirely open. |
| Warp icons / Teleport page | Essentials 0.1.14 / Menu 0.3.37 | live | nothing to do; admins only need to create warps. |
| `research/cloud/Ore-Regrow-Spec.md` | used as input | "parked for the SERVER" (its own header, 2026-10-10); only valid for generated veins in the solo pack | Do NOT use its timers (600-2,400 s) for spots - see C1. |
| Crop islands count | Q1 open | CONFIRMED 100 / 300 / 800 | Section 5 reading stands. |

Still useful now: sections 3 (spot definition), 4 (seed locks), 5 (island costs / sizes), 6 B2-B4. Stale: sections 1 row "Zone-Regen ... NOT BUILT", the B1 line, the 8 / 24 seeds text.

## 2. Contradictions

| # | Where | Contradiction | Recommendation |
|---|---|---|---|
| C1 | `research/cloud/Ore-Regrow-Spec.md` section 4 vs `research/cloud/Zone-Regen-Spec.md` 4.2 | Regrow 600-2,400 s (registry of worldgen veins, Depleted Vein block) vs 3-15 s (SKYBLOCK region, bedrock placeholder). Two systems, two timer tables. | Gathering spec correctly follows Zone-Regen. Add one line: "Ore-Regrow numbers are NOT used; generated veins OUTSIDE a SKYBLOCK region keep vanilla breaking". Also decide what happens to veins in the zone islands outside any spot (FULL = unbreakable, so nobody mines them - see Q1). |
| C2 | spec section 3 table vs `research/cloud/Zone-4-5-Materials.md` section 2 | Spec: Zone 4 Mine = Adamantite + Slag, Zone 5 = Mithril + Titanium. Zone-4-5: Zone 4 = Ember ("Cindersteel T8"), Zone 5 = Amberite + Drakonite. `research/cloud/Zone-Regen-Spec.md` 6 gates: Z3 Adamantite / Mithril, Z4 Onyxium / Ember, Z5 deep ores. Three different ore-by-zone lists. | Pick one list. Skyy's own table is `research/Zone-Tiers-Idea.md` (spec follows it) and WorldGen 0.7.x places Lead / Chromium / Slag / Titanium by it. Mark Zone-4-5 and Zone-Regen section 6 as superseded for ore placement, or ask Skyy where Ember / Amberite / Drakonite live (Q2). |
| C3 | spec section 3 respawn text vs Zone-Regen 4.2 | Spec names stone / Copper / Iron / Thorium / Cobalt / Adamantite / Mithril / Onyxium and "Lead = Thorium row ..." but not Electrum, Ember, Amberite, Drakonite, Slag's own row. | Add them to the types table (G3). |
| C4 | spec Zone 5 Farm = "pair 7 Potato + Onion" vs world.md 2026-10-18 | Skyy: Zone 5 has EVERY crop, mostly Potato, Onion, Mushroom. Spec gives Zone 5 only two crops and never mentions Mushroom. | Zone 5 Farm lists every crop type (all 14 + Mushroom), weights favour Potato / Onion / Mushroom (G1). |
| C5 | spec section 3 Farm split vs the tier lock (world.md 10-18) | Tier lock: crops spawn "around their zone with leeway, Zone 1 up to T5"; the spec's split puts Carrot + Corn (vanilla order "2") and Pumpkin / Aubergine ("6") in Z1 / Z2 and ignores the leeway. Also `docs/answered/economy.md` 10-04 says Potato is T1 while 10-05 puts Potato / Onion at "40" (top). | The Farm table must use the SAME crop-tier table as worldgen's spawn remap (WorldGen 0.7.8), not a new pairing. Reconcile Potato (T1 vs top). Ask Skyy only if the two sources disagree after reading `tools/tier_tags.py`. |
| C6 | spec section 4 "Wheat + Lettuce open" vs section 3 Hub Farm | Hub Farm default is pair 1, but Q9 default adds Carrot; the table says pair 1 only. Table and Q9 differ. | Edit the table to "Wheat, Lettuce, Carrot" (Q9 default took effect). |
| C7 | spec section 4 normal-seed gate vs `research/Gathering-Progression-Spec.md` 3.5 / F15 | New rule (own crop collection II) replaces older "previous pair's key crop at III". Only the spec's text says so. | Record the supersede in `docs/answered/world.md` / the old spec when B2 starts. |
| C8 | spec section 5 "Large 33x33" vs P7b Shards "storage 3 days of a full Totem N island" | Shards 0.4.5 sized storage and idle rates to the existing sizes; a bigger Large changes both. | B4 recomputes storage + worker cap for 800 plants (G5). |

## 3. Gaps and missing numbers

| # | Gap | What is needed |
|---|---|---|
| G1 | No crop list per Farm spot with ripe-crop COUNT, field size, and refill rule | Per spot: crop weights, plants per field (say 150-300), refill = Zone-Regen `crop` 10 s. Zone 5 = all crops (C4). |
| G2 | Mushroom, Tree Sap, flowers, herbs, gems | Spec has 4 skills (mine / grove / farm / pond) but Skyy's tier-lock line adds mushrooms (Zone 4+). Foraging spots (mushrooms) and gem blocks are not placed. Add a gem row + Mushroom (forage) type. |
| G3 | Types table has no rows for Lead, Chromium, Slag, Titanium, Electrum, Ember etc. | Add `regrow.<type>` per ore. Default: own row = base ore row + 1 step (Lead 6, Chromium 8, Slag 10, Titanium 12, Electrum 8). The spec says "follows base ore" but `regen.defaultSec` is 5 s and an unlisted type silently regrows in 5 s - a loophole for Titanium. |
| G4 | Pond spot (fishing) | A FULL-mode water region "nothing to break" has no config: fish tier per zone, fishing-rod gate, who sets the pond. Link to `SkyyFishing` and its zone fish tables; no Zone-Regen type needed. |
| G5 | Island cost table vs P7b | 100 / +200 / +500 seeds + Dirt / Stone are placeholder numbers; P7b made upgrades "1 h of zone income". Needs a coin/economy check (`python tools/balance_model.py --econ --check`): 100 Eternal seeds at ~800+ coins each (economy.md 10-15) = 80k+ coins of seeds for one T1 island. Is that intended given the collection IV gate? |
| G6 | Totem pole parts | "collection totem pole" read as Harvest Spirit totem parts (UNVERIFIED in spec). No ids / costs. |
| G7 | Spot sizing | How many blocks per Mine / Grove; how many players one spot serves; Zone-Regen 8 fairness numbers. A 2x2 field of ore feeds nobody. Suggest: ~300 ore blocks of the zone's ores per Mine, 30 trees per Grove, 200 plants per Farm (placeholder, tune from `/zones status`). |
| G8 | Normal-seed drop replacement ("locked-seed drop becomes the crop") | Needs a hook; spec admits it is unverified how Farming Overhaul / SeedDrops change the vanilla seed drops. |
| G9 | Planting not gated | Accepted in spec, but then a seed found/bought elsewhere plants past the collection. Fine; note the exploit (a friend gives seeds) in the spec. |
| G10 | Migration of the existing Wheat island | Spec says "keep size, recompute plant count, never take seeds" but not what happens to the old `grow.medium.*` rows or to islands that paid the old 8 / 24 seeds + coins. Needs a one-time migration (CONFIG-CONTRACT migration rules: only rewrite old defaults, History snapshot, Undo line, run-once marker). |

## 4. Config keys needed (Server Setup rows via `tools/skyycfg.py`, see `tools/CONFIG-CONTRACT.md`; times in seconds)

| Mod | Row | Default | Notes |
|---|---|---|---|
| `SkyyCollections` | `seed.tier` | 2 | int 1-10, same style as `eternal.tier`; hand-edited lines are checked by the kit (kit 1.1 fix 1) |
| `SkyyCollections` | `seed.free` (list: Wheat, Lettuce, Carrot) | those three | crops whose seeds never need a collection (Q9 default) |
| `SkyyShards` | `island.<crop>.cost.make` / `.med` / `.large` (seed count) | 100 / 200 / 500 | one table row `island.cost` with columns crop \| make \| upgrade1 \| upgrade2, per the one-table pattern in `tools/CONFIG-CONTRACT.md` (do not add 3 x 14 = 42 flat rows) |
| `SkyyShards` | `island.<crop>.blocks.*` | 200 / 100 etc. | Dirt / Stone per step; the table above again |
| `SkyyShards` | `island.size.large` | 33 | needs the build assert (48 > 2 x 16.5 + 8 = 41) |
| `SkyyShards` | `island.factor` (1 / 3 / 8) | 1 / 3 / 8 | production factor per size |
| `SkyyShards` | `island.perCrop` | 1 | max islands of the same crop per player (Q5) |
| `SkyyZones` | `regrow.<lead|chromium|slag|titanium|electrum|ember|amberite|drakonite>` | see G3 | rows in `Skyy_SkyyZones/regen.properties` |
| `SkyyZones` | `regrow.crop` | 10 | exists in spec; built? check `regen.properties` (0.2.0 has stone + ores) |
| `SkyyZones` | `regrow.tree1/2/3` | 45 / 60 / 90 | Z3 round |
| `SkyyZones` | `spot.<id>` (region flag `skill=mine|grove|farm|pond`) | none | Regions table; gate per skill: Zone-Regen section 6 numbers |
| `SkyyZones` | `regen.defaultSec` | 5 | WARNING: turn off the silent default for ores (G3) - set to 0 = "unlisted block is not a resource" |
| `SkyyWorldGen` | none new | | crop spawn weights per zone already in the 0.7.8 remap |

## 5. Build-order risks

| # | Risk | Why | Mitigation |
|---|---|---|---|
| R1 | B2 + B3 are "small" but touch saved data | `SkyyCollections` KnowSync, recipes, `SkyySacks` `/craft`, `SkyyBazaar` buy path; coins are involved (R3 "coins never skip collections") | Full round (spec says so) with the three together; rollback floor: Bazaar without `coll:fn:seed` just allows the buy (safe), Collections without it is a no-op. |
| R2 | B4 vs P7b | Shards 0.4.5 just retuned costs and storage | Start B4 from 0.4.5, re-run `--econ --check` (24 / 0 today) and `--gather` with the 100 / 300 / 800 numbers BEFORE building. |
| R3 | 1,089-tile island in a shard region | tilled-tile count and worker cap; UNVERIFIED | Probe first (G5 / local session item 3). |
| R4 | B1 is "last" but is already mostly done | Z2 live; the next SkyyZones round is Z3 (trees, crops) not "new mod". | Re-label B1 as SkyyZones 0.3 (trees + crops + scaffolding) and make it the FIRST builder round: crops are what makes the Hub Farm real; `seed.free` crops can be harvested for the collection only through it. |
| R5 | Seeds locked before any Farm spot exists | A player with no island and no spot can never get Carrot seeds if `seed.free` is empty | Ship B2 only together with the Hub Farm region (or with the 3 free crops). |
| R6 | Collections ignore "placed" blocks | A regrown spot crop might look placed (probe Z5 says Skills PlacedStore is safe for `setBlock` regrow; the same must be checked for Collections) | Probe on the first Farm spot; local session item 2. |
| R7 | Hired builders deliver the islands later | Until then admins draw regions on the prototype zone islands | Document the admin steps in `SkyyZones/README.md` (`/zones wand`, region modes) and one test region per skill. |

## 6. TEST PLAN (Skyy, in game, after each round; world NewBetaTest, op account + 1 normal account)

Spot basics (SkyyZones 0.3 round; mines already testable now):
1. Op: `/zones` wand, draw a SKYBLOCK region around a few Copper + Iron ore blocks in Zone 1, list them as `copper` / `iron`. Mine one: it drops ore + XP, swaps to bedrock, returns in about 4-5 s (Server Setup shows the row).
2. Same region: try to break a block that is NOT listed (dirt, a wall) - nothing breaks, no drops. Try to place a block - refused.
3. Restart the server while a block is bedrock: the block comes back (never stays bedrock). `/zones status` shows waiting 0 afterwards.
4. Stand in the block's space when the timer ends: it waits and comes back after you step off (no trap).
5. Mine one of the new ores (Lead, Chromium, Slag, Titanium) in a region: its regrow time is its own row, not the 5 s default.
6. Second player mines the same ore the first player broke seconds ago: gets "Growing back - wait a moment."; no double drop.
7. Grove: chop a tree in a region (after the tree round): the whole tree falls, drops arrive, it regrows in 45 / 60 / 90 s by tier.
8. Farm: break/F-harvest a ripe crop in a Farm region: crop returns to first stage and ripens again; confirm the crop collection counts (not "placed").
9. Zone 5 Farm: every crop type appears, mostly Potato / Onion / Mushroom (world.md 10-18); tool-tier lock stops picking a crop above your tier.
10. Pond: fish at the Pond warp; nothing breaks around; fish match the zone.
11. Warp icons: mining / foraging / farming / fishing warps show in the player Teleport page with the right icon.
12. Gates: a Mining 5 character cannot mine Iron in Zone 1 (gate 10) - gets a clear message; Mining 10 can.

Seeds (Collections/Bazaar/Sacks round):
13. Fresh character, Wheat / Lettuce / Carrot: seeds craftable and buyable. Cauliflower seeds: refused (recipe, `/craft`, Bazaar buy) with the same wording as the Eternal lock.
14. Harvest Cauliflower at the Farm spot until Cauliflower collection II: seeds unlock in the bench, `/craft`, Bazaar. Eternal seeds still need collection IV.
15. Coins cannot skip: a rich character with Cauliflower collection I still cannot buy seeds.
16. Wild locked-seed drops are replaced by the crop; seeds already in inventory still plant.

Crop islands (Shards round):
17. Carrot collection IV + 100 Eternal Carrot seeds + dirt/stone + totem parts: the Islands tab shows red/green requirement lines, then Carrot island appears in a free slot with 100 plants.
18. Upgrade to Medium (+200 seeds): 300 plants; Large (+500): 800 plants fit on 33x33; check no seeds lost if you cancel or lack one item (items first, nothing lost).
19. Existing Wheat island keeps its size; seeds spent stay spent; production and storage match the P7b rules (compare 3-day storage text).
20. Try a second Carrot island: refused (one per crop); fill all 6 slots with different crops; the 7th is refused with a clear line.
21. Production output over 10 min on T1 / T2 / T3 matches the 1 / 3 / 8 factors within the worker cap.

## Questions for Skyy

1. Veins that stay in zone islands OUTSIDE any spot (the generated Zone 1-5 ores): FULL = nothing breaks, so only spots are minable. Is that what you want, or should the ore veins outside spots still break (no regrow, vanilla)? [FULL everywhere outside spots, as in world.md 10-10 / 10-15; revisit after the first builder zone]
2. Where do Ember, Amberite and Drakonite live? `research/cloud/Zone-4-5-Materials.md` puts Ember in Zone 4 and Amberite + Drakonite in Zone 5, but the spec's table (from your zone-tiers table) puts Adamantite + Slag in Zone 4 and Mithril + Titanium in Zone 5. [Keep your table; Ember / Amberite / Drakonite become extra Zone 4 / 5 deep-cave rows with Mining 45 / 50 gates]
3. Zone 5 crop list: all 14 crops plus Mushroom, weighted to Potato / Onion / Mushroom (your 10-18 line). Should the Zone 5 Farm spot also hold a field of EVERY crop so a player can finish a missing collection there? [yes, one mixed field, weights 70 % the three, 30 % the rest]
4. Zones 1-4 crop pairs: use the same crop-tier table as worldgen spawns (with the "up to T5 in Zone 1" leeway), instead of the spec's 2 / 2 / 1 / 1 / 1 split? [yes, same table, one source of truth]
5. 100 Eternal seeds at ~800+ coins each is 80k+ coins per T1 island. Keep the seed counts as you said, and tune the Bazaar price instead, or lower the price for island seeds only? [keep 100 / 200 / 500; tune later with the money-loop check]
6. Free seeds: Wheat, Lettuce and Carrot never need a collection (so the first Farm can start). Okay? [yes]
7. Hub Farm spots: harvest only (no planting), regrows in 10 s, for everybody. [yes]

## For the local session (UNVERIFIED, needs Assets.zip / HytaleServer.jar / the test world)

1. Does `BlockOperations.setBlock` for the crop regrow (crop stage reset) count as "placed" for SkyyCollections (like SkyySkills `PlacedStore`, Zone-Regen probe Z5)? Run on the first Farm region.
2. Vanilla seed drops and how Farming Overhaul / SeedDrops change them; where to hook a "replace a locked seed with the crop" rule.
3. A 33x33 Large island at ring 48 in a shard region: build assert, tilled tile count, lighting/network cost of 800 plants.
4. `tools/skyycfg.py` table rows: can one `island.cost` table (crop | make | up1 | up2) hold 14 crops without hitting the row-count limits in `tools/CONFIG-CONTRACT.md`?
5. Crop stage reset on SkyyZones' timer (probe Z4): does vanilla growth tick the placeholder; F-harvest vs break.
6. Exact collection thresholds for II / IV of each crop (`SkyyCollections` curve letters).
7. Totem Pole kit ids and costs (spec G6).
8. `SkyyZones` 0.2.0 `regen.properties`: confirm `regrow.crop`, `regrow.tree1-3` rows exist or are only planned (spec read from the build header only).
9. CurseForge search for a gathering-node / crop-island mod (PROJECT-RULES 2 survey was Mods-folder only).
