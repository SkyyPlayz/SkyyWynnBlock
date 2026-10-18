# Zone gathering spots + seeds behind collections + crop islands - spec

Written 2026-10-18 (SPEC agent, docs only; nothing built, nothing deployed). Answers go in `docs/answered/world.md` (+ `economy.md` for prices);
close each question with `python tools/qa_append.py`. Skyy uses they/them. This spec does NOT re-decide anything locked; it fills the gap
between three things that already exist: the **Zone-Regen spec** (zone protection + regrow, written, not built), the **live Eternal-seed
collection lock** (Collections 0.2.24 + Bazaar 0.1.19) and the **live SkyyShards 0.4.2 Farming shard** (one Wheat island, grows with 8 / 24
Eternal Wheat seeds today).

## 0. Decision lines (word for word)

**world.md 2026-10-17 WARPS FOR PLAYERS + WARP ICONS** (Skyy, the relevant half):
"youll be able to do all that stuff everywhere on every zone, but i plan to make spots dedicated to each in each zone. so before you get your
island setup you can go find a farm in the hub. (then we can lock seeds behind collections so you have to find it in the zones and collect it
to unlock it first before you can farm it on your island. then you need like collection 4 to get eternal seeds, and it costs eternal seeds of
that kind, (and some other things like dirt and base components for the collection totem pole) to make a new island on the farm shard. so if i
want to add carrots i need carrot collection 4, like 100 eternal carrot seeds to start, dirt, stone, totem pole components. then i can add the
island. then to upgrade it you need a lot more eternal seeds and building blocks. 100 to make the island. 200 more to upgrade it. then 500 to
upgrade it to T3 current max. so the max carrot island would have 800 eternal carrots growing on it."

**economy.md 2026-10-16 ETERNAL SEEDS LOCKED BY COLLECTION** (live): "oh yeah lets lock the eternal seeds with the collection. give them at
like collection level 3 or 4" -> each crop's Eternal Seed bag (recipe AND Bazaar buy) unlocks at that crop's collection tier 4 by default
(Server Setup row `eternal.tier`, 1-10). Unlock only, no seeds given.

**world.md 2026-10-10 SERVER WORLD PLAN** (LOCKED): "for the server, ill hire people to help make full custom islands, and they will all be
protected, and to the mining and gathering like skyblock does". **world.md 2026-10-15 PROTECTION, TWO KINDS**: FULL region and SKYBLOCK region
(break only listed resource blocks, they swap to an unbreakable placeholder for a few seconds, trees fall whole and respawn).

Related still-true lines: the same 2026-10-17 warp line "(if posible i want a bunch of custom icons we can set to a warp when making
it. for mining fishing foraging farming and what not. probably 1 per zone.)" -> built (Essentials 0.1.14 / Menu 0.3.37); economy.md 2026-10-04
crop order (T1 Wheat, Carrot, Lettuce, Potato; T2 Corn, Cotton, Onion, Rice, Tomato, Turnip; T3 Aubergine, Cauliflower, Chilli; T4 Pumpkin);
bags.md R3 "coins never skip collections, recipes or bags".

## 1. What is already live (do not rebuild)

| Piece | Where | State |
|---|---|---|
| Eternal Seed collection lock, tier 4 (recipe + Bazaar buy refusal via `coll:fn:eternal`) | SkyyCollections 0.2.24+, SkyyBazaar 0.1.19+ | LIVE (Server Setup row `eternal.tier`) |
| Zone ore veins per zone (vanilla vein copies, new ores x0.85) | SkyyWorldGen 0.7.4 | LIVE in NEW chunks only |
| Farming shard: private world, hub + 6 fixed slots on a hexagon 48 blocks out, bridge per slot, island prefab 3 sizes (Small 13x13 / Medium 21x21 / Large 29x29, grown in place), eternal Wheat only, Harvest Spirit totem, storage, Collect, per-crop `ISL` table | SkyyShards 0.4.2 (`build_skyyshards_0.4.2.py` `ISL`, `grow=(seed,8,24)`) | LIVE, ONE crop. Code comment: "buying other types for slots 2-6 = a later round" |
| Grow gate today: coins + 8 / 24 Eternal Wheat seeds + Wheat collection IV / VI | SkyyShards | LIVE - to be replaced (section 5) |
| Warp list for players + custom warp icons + Teleport page | Essentials 0.1.14, Menu 0.3.37 | LIVE |
| Zone protection / region modes / regrow / scaffolding spec (`SkyyZones`, phases Z1-Z4, probes Z1+) | `research/cloud/Zone-Regen-Spec.md` | WRITTEN, NOT BUILT (no `SkyyZones/` folder) |
| Normal (non-eternal) seed recipe locks | `research/Gathering-Progression-Spec.md` 3.5 + F15 ("previous pair's key crop at III") | NOT BUILT (only Eternal is) |
| Crop collections, Enchanted crops, Farmer's Workbench pair order | SkyyCollections / `tools/skyyench.py` | LIVE |

## 2. Survey of existing mods first (PROJECT-RULES 2)

Done from Skyy's Mods folder with `python tools/mod_check.py - <name>` (CurseForge was not searched online this round - see UNVERIFIED).
Nothing in the folder is a gathering-node or crop-island mod.

| Mod (Mods folder) | What it does | Verdict |
|---|---|---|
| Farming_Overhaul 2.4.0 (Krynnx) | 16 crop block overrides (`Plant_Crop_<X>_Block`) | already in the pack; our code reacts by id only (PACK.md); nothing to reuse for nodes |
| SeedDropsV1.1.2 (Familiar) | seed drop tweaks on crop blocks | CLASH RISK: overrides the same crop blocks. Pack it only if the choice is recorded in PACK.md. Not needed: seeds come from collections |
| AdvancedFarming 1.3.1 | hoes / sickles (we build our own, 2026-10-06) | not used here |
| LuckyMining 1.0.8 (Buuz135) | UI only | ignore |
| vein-mining 2.5.0, treeharvester | gather helpers | already handled by SkySkills / SkyyTrees (Zone-Regen 1.3) |
| AleAndHearth, Aetherhaven, Resource_Chickens, NoCube_Resource_Bags | unrelated or resource-shaped items | not a fit |

Result: **build ours** (SkyBlock-style node regrow = `SkyyZones`, spec exists). What we learn from SkyBlock (Zone-Regen 1.1, own words): shared
public farms, crops refill on a timer, amounts tuned to player count; ores swap to a placeholder then return; fixed spots in the Dwarven Mines.

## 3. Part 1 - zone gathering spots

**What a spot is:** a named SKYBLOCK region (Zone-Regen 3.0) inside a zone world, drawn by the builders (or by an admin on the generated
prototype zones), tagged with ONE skill and listing its resource blocks: a **Mine** (stone + that zone's ores), a **Grove** (that zone's
trees; trees fall whole and respawn), a **Farm** (a field of ripe crops of that zone's crop pair), a **Pond** (fishing; FULL-mode water,
nothing to break). Everything outside spots stays FULL (nothing breaks, no drops). Skyy: "youll be able to do all that stuff everywhere on
every zone" = every zone has all four kinds; default **1 spot per skill per zone = 4 per zone**, and the hub gets the Farm so a player can
farm before an island exists.

| Zone | Mine (ores) | Grove (logs) | Farm (crops, default split of the 7 bench pairs) | Warp icon |
|---|---|---|---|---|
| Hub / Z1 town | - | - | **Hub Farm**: pair 1 Wheat + Lettuce (open recipes) | farming |
| Zone 1 | Copper, Iron | Zone 1 woods | + pair 2 Carrot + Corn (field behind the hub) | mining / foraging / farming / fishing |
| Zone 2 | Thorium, Lead | Zone 2 woods | pair 3 Cauliflower + Turnip, pair 4 Pumpkin + Aubergine | same four |
| Zone 3 | Cobalt, Chromium | Zone 3 woods | pair 5 Tomato + Chilli | same four |
| Zone 4 | Adamantite, Slag | Zone 4 woods | pair 6 Cotton + Rice | same four |
| Zone 5 | Mithril, Titanium | Zone 5 woods | pair 7 Potato + Onion | same four |

(Ore pairs are Skyy's table in `research/Zone-Tiers-Idea.md`; wood tiers per `research/Gathering-Progression-Spec.md` 2.2; both unchanged. The
crop split is MY default: pair order = the Farmer's Workbench order, 2 / 2 / 1 / 1 / 1 over Z1-Z5 after the hub. Crops are planted, so the
real crop gate is the collection lock in section 4; the zone only decides where the free ripe crop is found.)

**Respawn:** the Zone-Regen numbers, all Server Setup rows in seconds: stone 3, Copper 4, Iron 5, Thorium 6, Cobalt 8, Adamantite 10, Mithril
12, Onyxium 15, gems 30, crops 10 (the crop returns to its first stage and ripens again), whole trees 45 / 60 / 90. New ores follow their base
ore's row (default: Lead = Thorium row, Chromium = Cobalt, Slag = Adamantite, Titanium = Mithril).

**Who owns a spot on a shared zone world:** nobody. Zone worlds are shared by every player; a spot is public and state is per BLOCK, not per
player (Zone-Regen section 8 multiplayer fairness: a block you break regrows for everybody; anti-hog and macro limits in its section 7).
Regions are owned by the world (admins edit them, `skyyzones.admin`). Skill-level gates per spot are the Zone-Regen section 6 table (Z1 Iron
Mining 10 ... eternal-seed area Farming 40); FULL-mode areas never pay. Player islands and shard worlds are NOT spots and never regrow through
SkyyZones (shards have their own `shard.regrowSec`).

**What is needed to make them real:** SkyyZones Z1-Z4 from the Zone-Regen spec (its engine probes first). Until the hired builders deliver
hand-built islands, the SkyyWorldGen zone islands keep vanilla breaking; spots there are just admin-drawn regions for testing.

## 4. Part 2 - seeds locked behind collections

**Reading (stated):** Skyy wants a player to FIND a crop in the zones, HARVEST it (that fills its collection, so the zone Farm spots are the
free entry), and only then be allowed to craft / buy seeds of it. This differs from the older Gathering-Progression Q8 ("seed of pair N
unlocks from pair N-1's key crop at collection III"). New rule, default: **a crop's own collection unlocks its seeds**, because a spot lets
you harvest a crop with no seed yet - no chicken-and-egg.

| Seed kind | Unlock | Where the lock is enforced |
|---|---|---|
| Normal seeds `Plant_Seeds_<Crop>` | Wheat + Lettuce: open (as locked in Gathering-Progression). Every other crop: that crop's collection **II** [default; Server Setup row `seed.tier`, 1-10, like `eternal.tier`] | recipe `KnowledgeRequired` on the vanilla seed recipe (Farmingbench is a Crafting bench, F4 / F15 VERIFIED) + Sacks `/craft` + Bazaar buy refusal |
| Eternal seeds `Plant_Seeds_<Crop>_Eternal` | that crop's collection **IV** (LIVE) | same three places (LIVE) |
| Island for that crop (section 5) | same collection IV + the cost items | SkyyShards Islands tab |

How the lock works per door (all but the new function reuse live paths):
- **Recipes (bench + Sacks /craft):** SkyyCollections adds a second managed recipe set next to the eternal one (`coll:locked` + the KnowSync,
  F5). The `/craft` re-check in Sacks already reads `coll:fn:eternal`; add `coll:fn:seed` (same signature, `""` = allowed), Sacks calls both.
- **Bazaar:** the buy / buy-order path already asks `coll:fn:eternal`; ask `coll:fn:seed` too. Selling stays open (F21). Coins never skip it (R3).
- **Drops:** wild crops and zone-spot crops give the CROP, never a seed of a locked kind. Default: a seed drop of a locked kind is replaced by
  the crop's base item (a hook on the harvest / pickup event, no loot table edit); UNVERIFIED how Seed Drops / Farming Overhaul change vanilla
  seed drops. Seeds already in an inventory stay usable (never take anything away).
- **Planting is not gated by the engine** (a seed needs no recipe to plant). Accepted: the gates are recipe, `/craft` and Bazaar; no planting
  block (dupe / loss risk). A seed found in a chest still plants.

## 5. Part 3 - crop islands for Eternal seeds (the 100 / +200 / +500)

**What the numbers mean (my reading - Question 1):** the three costs are seeds that become the plants. "100 to make the island. 200 more to
upgrade it. then 500 to upgrade it to T3 ... the max carrot island would have 800 eternal carrots growing on it" = the seeds are spent and each
one is one eternal plant standing on the island. So the island has **100 plants at T1 (Small), 300 at T2 (Medium), 800 at T3 (Large)**,
cumulative 100 / 300 / 800. Seeds are the crop's own `Plant_Seeds_<Crop>_Eternal`.

| Step | Eternal seeds of that crop | Also | Collection gate |
|---|---|---|---|
| Make the island (a free slot) | 100 | dirt, stone, totem-pole components (Skyy: "base components for the collection totem pole") | that crop's collection IV |
| Upgrade T1 -> T2 (Medium) | +200 | more building blocks | collection IV (default; today's code uses VI for Large) |
| Upgrade T2 -> T3 (Large) | +500 | more building blocks | collection IV (default) |

Default building blocks (PLACEHOLDER, Server Setup rows `island.<crop>.cost.*`): make = 200 Dirt + 100 Stone + the island's Harvest Spirit
totem I parts (priced by the existing `shard:fn:totem "cost"`); Medium = +400 Dirt + 200 Stone; Large = +1,000 Dirt + 500 Stone. Counted by the
AGENT-BRIEF rule (inventory before / after, items first, nothing lost if a step fails). These replace today's `grow=(seed, 8, 24)` and the 9.4
table of `research/Gathering-Shards-Spec.md` (8 / 24 seeds + coins). No coins in the cost unless Skyy wants a sink (Question 4).

**Footprint check (arithmetic):** tiles today: Small 13x13 = 169, Medium 21x21 = 441, Large 29x29 = 841 including the grass rim and totem
pillar. 800 plants would need nearly all of Large as soil, so **Large grows to 33x33 (1,089)** with a 1-tile rim (about 31x31 = 961 soil minus
the pillar). Slot spacing 48 allows it (the build assert needs 48 > 2 x 16.5 + 8 = 41). Small keeps 13x13 (11x11 = 121 soil), Medium 21x21
(19x19 = 361). Plants never exceed seeds spent; rows fill to the paid count.

**Output:** production stays the lazy rate formula (`rate = base x size factor x totem rate`). With plants 100 / 300 / 800 the factors
1 / 1.6 / 2.4 would make the big island barely better per seed. Default: factors **1 / 3 / 8** (= plant counts), with shard storage and the
12 items / min worker cap (skills.md 2026-10-16) as the real throttle. Question 3.

**Other crops:** `ISL` gets one row per crop (14): production item, collection, skill XP, `Plant_Crop_<X>_Block_Eternal`, Enchanted id. Island
TYPE = crop. Slot rule unchanged: any island in any of the 6 slots, no order lock; one island per crop per player (Question 5). Orchard /
Ranching / Mining / Foraging / Combat islands are NOT in this spec (they keep the Gathering-Shards-Spec 9.4 costs until Skyy sets theirs).
Six slots hold at most six crops at once (cap from the live design) - Question 10.

## 6. Build plan - one mod per builder

| # | Mod | Scope | Round |
|---|---|---|---|
| B1 | NEW `SkyyZones` 0.1 | regions FULL / SKYBLOCK, resource-block list, placeholder + regrow, whole-tree respawn, scaffolding, admin region commands, Server Setup rows (Zone-Regen phases Z1-Z4 after probes) | ULTRACODE (new system, permissions) |
| B2 | SkyyCollections 0.2.28+ | `seed.tier` row, normal-seed recipe lock set, `coll:fn:seed`, KnowSync add (F15), page text | full round with B3 (recipes, saved data) |
| B3 | SkyyBazaar + SkyySacks (one builder each; tiny) | Bazaar asks `coll:fn:seed`; Sacks `/craft` re-check; no price changes | with B2 |
| B4 | SkyyShards 0.5 | `ISL` rows for 14 crops, buy-island flow (100 seeds + blocks), +200 / +500 upgrades, Large 33x33, size factors, config rows, Islands tab cost list as a red / green requirement list (Menu-Pattern), migration of the existing Wheat island (keep size; recompute plant count; never take seeds) | FULL round (items could be lost / duplicated) |
| - | Essentials / Menu | nothing new - warp icons are live; admins just create the farm / mine / grove / pond warps | none |

Order: B2 + B3 first (small), B4 next, B1 last (needs probes and the hired builders). B4 can ship before B1: the island needs only the
collection and seeds, not a spot. Pin as one set with rollback floors: SkyyShards 0.5 is a floor once a non-Wheat island exists; B2 and B3
go together (Bazaar without `coll:fn:seed` just allows the buy).

## 7. Risks

- Without the Hub Farm, crops past pair 1 can only be harvested from a bought crop or the player's own farm; whether Bazaar-bought crops
  fill collections is unchecked (see UNVERIFIED).
- Regrow load on busy spots (Zone-Regen 9: journal + 60 s snapshot, restart cleanup).
- Eternal seeds cost 800+ coins on the Bazaar (economy.md 10-15); 100 seeds is a big sum there, but the buy is locked behind collection IV
  and players grow seeds themselves; re-run the money-loop check with island costs.
- 800 seeds x up to 6 islands of regrow work in the shard region: only while someone is inside (`shard.regrowSec`).

## Questions for Skyy (each with a default)

1. The 100 / +200 / +500: are those the seeds that become the plants (100 / 300 / 800 plants growing, seeds spent)? [Yes - T1 100, T2 300, T3 800, cumulative]
2. Which collection tier for a crop's NORMAL seeds, and for the Medium / Large upgrades? [II for normal seeds (row `seed.tier`); IV for island make + both upgrades]
3. Should bigger islands pay more per seed (size factors 1 / 3 / 8) or stay 1 / 1.6 / 2.4? [1 / 3 / 8]
4. Any coins in the island costs, or only seeds + dirt + stone + totem parts? [no coins]
5. One island per crop per player, or several of the same crop? [one]
6. Grow Large from 29x29 to 33x33 so 800 plants fit? [yes]
7. How many spots per zone and what crop split? [4 per zone; split as in section 3]
8. Locked-seed drops from grass / harvest: replace with the crop, or drop nothing? [replace with the crop]
9. Hub Farm crops: pair 1 only (Wheat + Lettuce), or also Carrot and Potato (the other T1 crops)? [pair 1 + Carrot, so the Carrot collection can start]
10. Only 6 slots per shard means 6 crops max on the farm shard; add more slots later, or is 6 enough for now? [6 enough; revisit at rebirth]

## UNVERIFIED

- No CurseForge search this round (Mods folder only); an outside crop-node mod is not excluded.
- Whether harvesting a zone-spot crop credits the crop's collection (SkyyCollections ignores "placed" blocks, build line ~585); spot crops must
  not count as placed - needs a probe. Same for Bazaar-bought crops.
- Engine: crop stage reset on SkyyZones' timer (Zone-Regen probe Z4), F-harvest vs break, how Seed Drops / Farming Overhaul change vanilla
  seed drops, 1,089 tilled tiles per island in a shard region.
- Exact collection thresholds for tiers II / IV per crop (curve letters in Gathering-Progression 3.5; numbers not re-read).
- That the build assert allows a 33x33 Large at ring 48 (arithmetic yes; not run).
- Totem Pole kit ids and costs ("collection totem pole" in Skyy's line is read as the island's Harvest Spirit totem parts).
