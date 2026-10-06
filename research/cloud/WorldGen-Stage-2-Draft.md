# WorldGen stage 2 - Zones 2-5: what each island generates (biomes, ores, trees, crops, structures)

Cloud draft, 2026-10-06. Paper design; nothing built. The next stage after `research/SkyyWorldGen-Plan.md` (stage 1 = the Zone 1 test
island, SkyyWorldGen 0.1, live). Geometry (one world, island sizes, centres, coast, height field, level blend, anti-bridging) is
`research/cloud/Zone-Islands-Layout.md` and is NOT repeated here; this file fills each island with content.
Inputs read: `research/SkyyWorldGen-Plan.md` (sections 0, 3.2-4.5, 7), `research/cloud/Zone-Islands-Layout.md`, `research/cloud/Gathering-Tiers-Draft.md`,
`research/cloud/Zone-4-5-Materials.md`, `research/cloud/Mob-Levels-Refit.md` (section 3), `research/cloud/Outposts-List.md`,
`research/cloud/SkyyFishing-Spec-Draft.md` (section 5), `research/cloud/Gathering-Reconciliation-Applied.md`, `docs/answered/world.md`, `docs/log/2026-10.md`.
Every number is a placeholder and a Server Setup row (section 8; times in seconds).

**Decisions followed (not re-decided)** - `docs/answered/world.md`:
- LOCKED 2026-10-01 zone bands Z1 1-20, Z2 20-30, Z3 30-45, Z4 45-60 (guardians 20 / 30 / 45 / 60); R8 Zone 5 = dinosaur caves under Zone 4, Lv 60-75, dragon at 75.
- LOCKED 2026-10-03 WORLDGEN STAGE 2: random island shape, keep the normal world-gen patterns / structures / features (rivers, mountains,
  goblin camps), trend upward to a mountain, at least 3x the size, caves inside, biomes "more random like vanilla" (outside-in = a tendency).
- LOCKED 2026-10-03: all zone islands in ONE world, the next zone visible across the void; guardian + portal unlock must still matter.
- LOCKED 2026-10-01: summit portal opens after the guardian; a town with a warp at each landing, built around a VANILLA temple; at
  least one outpost per biome (group); no separate hub island. LOCKED 2026-10-06: the Zone 1 temple sits at the town centre behind spawn.
- `docs/answered/economy.md` R3 (no shop sells unlocks); `docs/answered/mobs.md` R5 (no oceans, no mob coins); the Gathering ladder
  (`docs/answered/bags.md` LOCKED 2026-10-05 BIG DIRECTION: tiers, collections unlock the next tier).

## 1. The five zones at a glance

| Zone | Island (Layout 1-2) | Levels | Climate | Ore tiers | Tree tiers | Wild crops | Fishing water |
|---|---|---|---|---|---|---|---|
| 1 Emerald Wilds | R 1,110 at (0, 0) | 1-20 | temperate | T1 Copper, T2 Iron | F1 (+F2 edge, F4 Azure clearing) | group A (+B at the core) | ponds, rivers |
| 2 Howling Sands | R 1,220 at (2,511, 443) | 20-30 | savanna -> desert | T3 Thorium, T4 Cobalt (core) | F2 | groups B, C | oases |
| 3 Whisperfrost | R 1,330 at (4,100, 2,712) | 30-45 | taiga -> glacier | T4 Cobalt, T5 Adamantite, T6 Mithril (core) | F3, F4 Petrified, F5 Frostwood | groups C, D (hot-spring terraces) | ice holes |
| 4 Devastated Lands | R 1,440 at (3,581, 5,657) | 45-60 | ash / volcanic | T6 Mithril, T8 Ember | F5 Fire / Stormbark, burnt F1 | eternal I (rare) | lava (stage 3) |
| 5 Dinosaur Caves | cave layer y 20-130 under Z4's inner 60% (Layout 7) | 60-75 | lost-world jungle caves | T8 Ember (upper), T9 Amberite, T10 Drakonite | F2 Jungle / F5 Crystalwood (glow groves) | eternal II-III (cave farms) | underground lakes |

Ore spine = `research/cloud/Gathering-Tiers-Draft.md` 1.2 and `research/cloud/Zone-4-5-Materials.md` 1-2. Where the two drafts differ the
newer one wins: Mithril starts in the Zone 3 CORE (Layout said "Zones 3-4"), Onyxium (T7) has no source and stays a hole (Zone-4-5 Q1).
Gathering-Tiers section 4 lists "F2, F3" for Zone 2, but its 2.2 puts F3 (Cedar, Fir, Redwood, Amber) in Zone 3 - this draft keeps F3 in Zone 3.

## 2. Biomes per zone (level bands from `research/cloud/Mob-Levels-Refit.md` 3)

Placement = the Layout 3.1 blend (65% distance from the coast, 25% biome tier, 10% noise). "Share" = target share of the island's land
(checked in `/viewport`); the rim column is where it mostly sits (1.0 = coast, 0 = summit).

| Zone | Biome group (vanilla keys) | Lv | Share | Mostly at | Outpost (`research/cloud/Outposts-List.md`) |
|---|---|---|---|---|---|
| 2 | Savannah_Forest / Plains / Boab / Rock, Mudflats | 20-22 | 30% | 1.0-0.7 | Steppe Stop, Boab Branch |
| 2 | Plateau_* (savanna env) | 21-23 | 10% | 0.7-0.6 | Mudflat Mailbox |
| 2 | Scrub_Bushland, tar pits | 22-24 | 15% | 0.6-0.5 | Bushland Booth, Tar Pit Terminal |
| 2 | Desert_Oasis / Rock / Springs / Red / Hotsprings, Plateau_Desert | 25-27 | 25% | 0.5-0.3 | Oasis Office, Red Dune Depot |
| 2 | Desert_Barren, Desert_Mushroom, Oasis_Hidden (summit) | 27-30 | 20% | 0.3-0 | Barren Bureau |
| 3 | Forest_Redwood (Kweebec villages), Plains_Shire | 30-32 | 22% | 1.0-0.75 | Redwood Registry |
| 3 | Forest_Fir, Forest_Tundra, Plains_Hotsprings | 32-34 | 20% | 0.75-0.6 | Fir Filing, Hotspring Hostel |
| 3 | Forest_Cedar | 36-38 | 15% | 0.6-0.45 | Cedar Cabinet |
| 3 | Plains_Frozen, Forest_Cedar_Mixed, Plains_Tundra | 37-39 | 18% | 0.5-0.35 | Frozen Plains Pantry, Outlander Row |
| 3 | Forest_Frozen, Forest_Frozen_Light, Plains_Frozen_Frost | 41-43 | 15% | 0.35-0.2 | Everfrost Edge |
| 3 | Mountain T3 / glacial summit | 43-45 | 10% | 0.2-0 | Glacier Gate |
| 4 | Wastes_Grasslands | 45-47 | 20% | 1.0-0.75 | Cinder Check-in |
| 4 | Wastes_Geysers, Forest_Ghost, Desert_Dunes, Forest_Swamp Z4 | 48-50 | 25% | 0.75-0.5 | Geyser Gate, Ghost Grove Guardhouse |
| 4 | Desert_Ash, Wastes_Ash | 53-55 | 20% | 0.5-0.33 | Ash Annex |
| 4 | Wastes_Lava | 55-57 | 15% | 0.33-0.22 | Magma Mile Marker |
| 4 | Forest_Burned, Forest_Roots, caldera | 58-60 | 20% | 0.22-0 | Ember Roots Retreat |
| 5 | lost-world jungle caves (fossil pits) | 60-65 | 45% | outer caves | Fossil Pit Post |
| 5 | raptor caverns, amber groves | 65-70 | 35% | middle | Raptor Roost Rest |
| 5 | lava-lake approach, dragon lair | 70-75 | 20% | deep centre | Lava Lake Landing |

Zone 4 note (Plan 4.4, VERIFIED there): `Env_Zone4_Crucible` (the Z4 swamp) has no world spawn file - use `Env_Zone4_Forests` on that
look or our own spawn file. Zone 5 has no vanilla biome at all: its caves need our own V2 biome + environment + spawn file (stage 2.6).

## 3. Ores (per 16 x 16 column area, over the island's whole height; python-checked totals)

Shares follow the level blend (the harder ore sits further in). "Total" = island cells x share x ore per cell (Z1 15,120 cells, Z2 18,265,
Z3 21,708, Z4 25,447, Z5 9,161 = pi x R^2 / 256; the Layout's 32 x 32 chunk counts x 4).

| Zone | Ore (tier) | Host rock | y band | Share of land | Veins / cell | Vein size | Ore / cell | Island total |
|---|---|---|---|---|---|---|---|---|
| 1 | Copper (T1) | Stone, Sandstone | 90-200 | 70% (rim, middle) | 1.2 | 4-8 | 7.2 | ~76,000 |
| 1 | Iron (T2) | Stone, Slate | 70-230 | 40% (middle, mountain) | 0.8 | 3-6 | 3.6 | ~21,800 |
| 2 | Thorium (T3) | Mud, Sandstone | 90-200 | 70% | 1.0 | 3-7 | 5.0 | ~63,900 |
| 2 | Cobalt (T4) | Shale, Slate | 70-160 | 35% (desert core) | 0.6 | 2-6 | 2.4 | ~15,300 |
| 3 | Cobalt (T4) | Shale, Slate | 90-200 | 50% (rim) | 0.8 | 2-6 | 3.2 | ~34,700 |
| 3 | Adamantite (T5) | Magma / Basalt near hot springs + deep caves | 60-140 | 40% | 0.6 | 2-6 | 2.4 | ~20,800 |
| 3 | Mithril (T6) | Rock (Quality 5) | 180-260 | 15% (summit) | 0.4 | 2-5 | 1.4 | ~4,600 |
| 4 | Mithril (T6) | Rock, Basalt | 80-200 | 60% | 0.6 | 2-5 | 2.1 | ~32,100 |
| 4 | Ember (T8) | Basalt, Volcanic Rock | surface 150-260 + caves 40-140 | 40% | 3.0 | 5-9 | 21 (Zone-4-5 2) | ~214,000 |
| 5 | Ember (T8) | Basalt | 100-130 (upper caves) | 30% | 1.0 | 5-9 | 7.0 | ~19,200 |
| 5 | Amberite (T9) | Fossil Seam (new) | 30-120 | 50% | 2.0 | 4-7 | 11 | ~50,400 |
| 5 | Drakonite (T10) | dark Basalt + Fossil Seam | 20-60 | 15% (deep) | 0.8 | 3-5 | 3.2 | ~4,400 |
| all | Silver, Gold (decor / economy, no tier) | any | any | 20% | 0.2 | 2-4 | 0.6 | small |

Stone families (Gathering-Tiers 1.3) follow the land: S1 (Cobblestone, Sand, Rubble, Clay, Sandstone) on Z1-Z2; S2 (Shale, Slate,
Limestone, Marble, Quartzite, Salt) on Z2-Z3; S3 (Basalt, Volcanic, Ice) on Z3-Z5. Crystal shards in Z2+ caves (E curve specials).

Rules: no vein within 40 blocks of a town or outpost (Zone-4-5); no vein in a guardian arena or the dragon lair; ores count for
collections only when broken by the player (Collections-Spec).
**Supply check (python):** one player taking Iron to collection VIII (5,000) uses 23% of the Zone 1 Iron; the Zone 3 Mithril pocket is
only ~4,600 ore. Zone-4-5 Q2 ("no regrow in profile worlds") was written for per-profile worlds; the zone islands are ONE SHARED world,
so this draft proposes **vein regrow**: a mined vein refills after `ore.regrowSec` 1,800 s when no player is within 32 blocks (Q1).
The Ember density (21 / cell, taken as given from Zone-4-5) is 3-10x the other ores; keep it only if Ember is meant to be the bulk ore (Q2).

## 4. Trees (Gathering-Tiers 2.2 groups)

| Zone | Tree tier | Logs (vanilla tree prefabs by reference) | Where | Density |
|---|---|---|---|---|
| 1 | F1 Common | Oak, Birch, Ash, Aspen, Beech | plains edges, birch / flower / aspen forests | vanilla per biome |
| 1 | F2 (edge) | Apple, Maple, Wild Wisteria | Forest_Autumn, Forest_Moss clearings (inner) | 10% of trees there |
| 1 | F4 Azure | Azure | the blue-forest clearing near the summit | vanilla |
| 2 | F2 Uncommon | Palo, Gumboab, Bottletree, Banyan, Blue Fig | savanna, scrub, oases | sparse (savanna 1 tree / 600 m2) |
| 2 | F1 (oasis) | Palm | oases | - |
| 3 | F3 Northern | Cedar, Fir, Redwood, Amber | rim to middle forests | dense |
| 3 | F4 Petrified | Petrified | frozen plains, Everfrost edge | rare (5%) |
| 3 | F5 Frostwood | Frostwood | Forest_Frozen, summit slopes | 30% of trees there |
| 4 | F1 Burnt | Burnt, Dry | ash plains, ghost forest | common |
| 4 | F5 Fire / Stormbark | Fire, Stormbark | Forest_Burned, Forest_Roots, geysers | 40% there |
| 5 | F2 Jungle / F5 Crystalwood | Jungle (cave jungle), Crystalwood (glow groves) | outer caves / amber groves | under cave openings (light) |

Hatchet gates come from Tool-Levels (logs are always multi-hit); Tree Sap (the Lantern collection) drops from F2+ logs on every island.
UNVERIFIED (local): which vanilla prefab folders hold each tree, and whether Fire / Frostwood / Stormbark / Crystalwood exist as trees or only as logs.

## 5. Crops and wild plants

Crops are planted, so zones do not gate them (Gathering-Tiers 3.2). The world only places **wild patches** that drop seeds and give a
first taste; the real path is the collection recipe.

| Zone | Wild patches | Seeds you find | Also |
|---|---|---|---|
| 1 | Wheat, Carrot, Lettuce, Corn (group A); a few Pumpkins near the core | A seeds; B seeds 2% | Wild Berries, Apples, Mushrooms in forests |
| 2 | Cauliflower, Turnip, Aubergine, Pumpkin (B); Chilli, Tomato at oases (C) | B, C seeds | Cactus, Wild Fruit |
| 3 | Cotton, Rice (C) on hot-spring terraces; Potato, Onion (D) in Shire fields | C, D seeds | Petals, frost berries |
| 4 | none in the ash; one "eternal seed" chance on the Geyser Gate fields (0.5%) | eternal I | Essence of Life (rare) |
| 5 | cave farms under light shafts | eternal II-III (0.2%) | glowing mushrooms |

Patch density: `crop.wild.perCell` 0.05 (one patch per ~20 cells), 6-14 plants, regrow `crop.wild.regrowSec` 1,200 s.

## 6. Structures per island

| Structure | Per island | Placement | Source |
|---|---|---|---|
| Landing town + vanilla temple | 1 | facing rim, R x 0.92 (Layout 4) | vanilla temple prefab by reference (which temple per zone: local check) |
| Summit portal + guardian arena | 1 | centre crown | our prefab / pasted by the plugin |
| Zone dungeon entrance | 1 | summit slope, 150-250 blocks from the arena | SkyyDungeons |
| Outposts | Z2 8, Z3 8, Z4 6, Z5 3 | in their biome patch, >= 250 blocks apart | 5 templates (Outposts-List 3) |
| Vanilla features kept | Z2: tar pits, plateaus, ruins; Z3: Kweebec villages (Redwood), Outlander villages (core, +2 env), mineshafts; Z4: ghost towns, geysers, Zone 4 villages | vanilla density per zone | vanilla prefabs by reference (Plan 3.4 step 6: V1 prefab names -> V2 paths, UNVERIFIED) |
| Rivers | 2-4 (Z2: dry riverbeds + oases; Z3: frozen rivers; Z4: lava rivers) | mountain -> coast | V2 river node or carved |
| Caves | every island; Z3 hot caves (Adamantite); Z4 volcanic caves (Ember) | entrances on slopes and cliff bands | vanilla carving |
| Zone 5 shaft "Echoing Maw" | 1 (Z4 caldera floor) | caldera centre -> cave layer | ours |
| Zone 5 Egg Desk town | 1 big cavern | under the caldera | ours |
| Zone 5 set pieces | fossil ribs / skeletons (Amberite veins inside), amber groves, the lava lake + dragon lair | deep centre | ours |

## 7. Build stages (after stage 2.1-2.2 = Zone 1 at 3x with the vanilla features, Layout 8)

| Stage | Content | Done when (Skyy test) | Round |
|---|---|---|---|
| 2.3 | Zone 2 island + the facing headland + void band rules + Zone 1 summit portal to Zone 2 | the Zone 2 rim is visible from Zone 1; the portal opens only after the guardian / summit rule | full |
| 2.3b | Zone 2 content: biome table 2, ores, F2 trees, wild B/C crops, 8 outposts, oasis fishing water | `/wg band` prints the expected band; Thorium found in 5 minutes | full |
| 2.4 | Zone 3 island + content (ice-hole water, hot caves, Kweebec / Outlander villages) | Mithril only near the summit | full |
| 2.5 | Zone 4 island + content, hidden behind `zones.max` 3 until our Lv 50+ gear (Plan 3b) | Skyy flips `zones.max` 4 | full |
| 2.6 | Zone 5 cave layer: our own V2 cave biome + environment + spawn file, Egg Desk, the shaft | a Lv 60 mob spawns in the jungle caves | full |
| 2.7 | ore / crop regrow timers (Q1), resource survey command (`/wg survey <zone>` counts ores per cell) | survey matches section 3 within 20% | lean |

## 8. Server Setup rows (WorldGen page)

`ore.<zone>.<ore>.{share,veinsPerCell,veinMin,veinMax,yMin,yMax}`, `ore.townClear` 40, `ore.regrowSec` 1,800, `ore.regrowNoPlayer` 32,
`tree.<zone>.<tier>.share`, `crop.wild.perCell` 0.05, `crop.wild.regrowSec` 1,200, `crop.wild.seedChance.<group>`, `zones.max` 3.
Geometry and shares are baked into the world assets: changing them needs a new world version (Plan risk "Updating worldgen"); only
regrow timers, seed chances and `zones.max` are live.

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | V2 ore placement: is there a vein / ore-scatter node in V2 (or only V1 `OreVein` data)? per-cell density and y bands in V2 terms |
| 2 | Vanilla ore block ids and their host-rock rules for Copper..Mithril; whether `Ore_Prisma` / `Ore_Onyxium` blocks exist (Zone-4-5 local 1) |
| 3 | Which vanilla temple prefab exists per zone (desert, frost, ash) for each landing town |
| 4 | Tree prefab folders per log type (Palo, Gumboab, Frostwood, Fire, Stormbark, Crystalwood) and whether they exist as trees |
| 5 | Wild crop prefabs / blocks (Plant_Crop_*) placeable by V2 props; whether seeds drop from wild crops |
| 6 | Zone 2-4 vanilla features in V2: tar pits, Kweebec / Outlander villages, ghost towns, geysers, mineshafts (Plan 3.4 step 6) |
| 7 | A cave layer under a floating island (y 20-130) with our own environment + spawn file (Plan T6); light shafts into it |
| 8 | Hytale chunk size (32 x 32 assumed by the Layout) vs the 16 x 16 "per chunk" in Zone-4-5; this draft uses 16 x 16 cells |
| 9 | Block regrow: can the server re-place an ore block on a timer (tick task) without a chunk reload; cost for ~200k veins |
| 10 | Fishing water per zone: ice-hole breaking and lava fluid for fishing (SkyyFishing UNVERIFIED 2) |
| 11 | Spawn files for Zone 4 `Crucible` and every Zone 5 cave environment (Plan 4.4 spawn gap) |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | The zone islands are shared by everyone: should mined ore veins grow back (30 minutes after the last player leaves the spot)? | [yes, 1,800 s] |
| 2 | Ember Ore is very common in Zone 4 (the bulk ore there), or as rare as the other metals? | [bulk ore, as the Zone 4-5 draft says] |
| 3 | Mithril first appears at the Zone 3 summit (a small pocket), then common in Zone 4 - OK? | [yes] |
| 4 | Wild crops: a few wild patches per zone that drop seeds, or no wild crops at all (seeds only from collections)? | [wild patches] |
| 5 | Zone 2 trees: sparse savanna (realistic, little wood), or denser groves so Foraging works there? | [denser groves near oases and scrub] |
| 6 | Build order: Zone 2 then 3, with Zone 4 hidden until our Lv 50+ gear? | [yes] |
