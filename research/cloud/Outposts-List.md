# Outposts list - 34 unlockable warps across the zones

Cloud draft, 2026-10-06. Locks: **R9 (2026-10-02): about 30-35 outpost towns, shared between near-identical biome variants, each an unlockable warp**; "every zone's starter town is built around a vanilla temple; plus at least one outpost town per biome in every zone, each with an unlockable warp, found = unlocked" (docs/answered/world.md, 2026-10-01);
**warps**: each zone has a main town warp unlocked with the zone (SkyyWorldGen plan). Inputs: biome tables and level bands from `research/cloud/Mob-Levels-Refit.md` (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60) and the geometry in `research/cloud/Zone-Islands-Layout.md` (all islands in one world, mountain in the middle, rim landing town),
shops from `research/cloud/NPC-Shops-Spec.md`, discovery from SkyyExploration. Names are working names in the lore voice ("Branch Offices" of the Department of Arrivals). Positions and prefabs are **UNVERIFIED** until the biomes exist in world gen.

## 0. Rules

| Rule | Value |
|---|---|
| Count | **34** = Zone 1: 9, Zone 2: 8, Zone 3: 8, Zone 4: 6, Zone 5: 3 (plus the five **main towns**, which are not counted) |
| One per biome **group** | near-identical biome variants share one outpost (e.g. Savannah Forest + Plains + Boab share the Steppe Stop) - R9 |
| Placement | **inside its biome patch**, at the **ring distance** in the table (fraction of the island radius from the centre), never on a route that skips a ring; at least **250 blocks** from the next outpost |
| **Found = unlocked** | walking into the outpost's discovery radius (**24 blocks**) unlocks its warp for that **profile** and pays Exploration XP; warps are per profile (SkyyExploration backbone) |
| Warp rules | a free warp from the `/warps` page (SkyyMenu warps tab); **60 s cooldown**; not in combat (`skill:fn:combat`); not from or to another island except through the **town / summit portal** (an outpost warp never crosses the void: **anti-skip**); arrival in a **24-block safe bubble** (no hostile spawns, no PvP) |
| Services | a **bed** (set respawn), a **small shop** (3-5 basics from the NPC-Shops-Spec), a **campfire**; outposts do **not** have a bank, an AH or a crafting bench set (those stay in the towns, so towns stay worth visiting) |
| Respawn | after death you return to the **last bed you set** (an outpost bed or the town); default row `outpost.respawn=on` |
| Exploration XP on first visit | Zone 1: 100, Zone 2: 150, Zone 3: 200, Zone 4: 300, Zone 5: 400 (rows) |
| Titles | 5 outposts of a zone = "Regional Officer of <Zone>"; all 34 = **"Branch Manager"** (the lore joke) |
| Stamps | every outpost visit also gives a **stamp** on the Form 27-B/6 (cosmetic, `Story-Script-Zones-2-5` spine): a collection of 34 stamps shown on the Exploration page |
| Look | five reskinned templates (section 3), not 34 hand-built places |

## 1. The list

Columns: **#** (id `outpost.z<zone>.<name>`), **Name**, **Biome group** (vanilla biome keys), **Level band** (from the refit), **Ring** (distance from the island centre as a fraction of R: 1.0 = coast, 0 = summit), **Shop** (what the outpost shop sells, NPC-Shops-Spec; "G" General, "F" Forager, "M" Miner, "Fa" Farmer), **Notes**.

### Zone 1 - Emerald Wilds (Lv 1-20)
| # | Name | Biome group | Levels | Ring | Shop | Notes |
|---|---|---|---|---|---|---|
| Z1-1 | **Greenfield Annex** | Plains_Smooth, Plains_Birch | 1-5 | 0.80 | G | the first outpost new players meet after the town; tutorial sign |
| Z1-2 | **Birchwood Bureau** | Forest_Birch, Forest_Flower, Mountain_Tier1 and Trork camps nearby | 5-7 | 0.68 | F, G | Trork camp warning sign |
| Z1-3 | **Gorge Gate Post** | Plains_Gorge (Tier 2 and Tier 3 share) | 7-14 | 0.55 | G | wide range (7-14) because the two regions share a look |
| Z1-4 | **Tallgrass Tally** | Plains_Tallgrass | 9-11 | 0.52 | Fa | farm patch, seed vendor |
| Z1-5 | **Aspen Rest** | Forest_Aspen, Forest_Gully | 10-12 | 0.48 | F | cabin in the aspens |
| Z1-6 | **Stonefoot Station** | Mountains (Tier 1-3 share) | 5-18 | 0.40 | M | next to a cave entrance; mining sign |
| Z1-7 | **Mirebridge Mailroom** | Forest_Swamp | 16-18 | 0.30 | G | boardwalk outpost over the water |
| Z1-8 | **Autumn Archive** | Forest_Autumn, Forest_Moss | 18-20 | 0.22 | F | orange leaves, a record shelf |
| Z1-9 | **Azure Quiet Desk** | Forest_Azure (the blue forest) | 18-20 | 0.15 | G | the blue-forest visitor desk; a Pebble statue |

### Zone 2 - Howling Sands (Lv 20-30)
| # | Name | Biome group | Levels | Ring | Shop | Notes |
|---|---|---|---|---|---|---|
| Z2-1 | **Steppe Stop** | Savannah_Forest, Savannah_Plains | 20-22 | 0.80 | G | the first Zone 2 outpost; camel hitch |
| Z2-2 | **Boab Branch** | Savannah_Boab, Savannah_Rock | 20-22 | 0.70 | G | a hollow boab tree "office" |
| Z2-3 | **Mudflat Mailbox** | Savannah_Mudflats, Plateau_* | 21-23 | 0.60 | G | stilts over the flats |
| Z2-4 | **Bushland Booth** | Scrub_Bushland | 22-24 | 0.52 | F | a thorn-fenced booth |
| Z2-5 | **Oasis Office** | Desert_Oasis, Desert_Springs, Desert_Hotsprings, Oasis_Hidden, Dunes_Oasis | 25-27 | 0.42 | G | water, shade, a quiet pool; stable master's second office |
| Z2-6 | **Red Dune Depot** | Desert_Red, Desert_Rock, desert overlays | 25-27 | 0.36 | M | red sandstone; ore vendors |
| Z2-7 | **Barren Bureau** | Desert_Barren, Desert_Mushroom | 27-29 | 0.26 | G | mushroom roof |
| Z2-8 | **Tar Pit Terminal** | Scrub_Tar_Pits, Desert_Oasis_Hidden overlays | 28-30 | 0.16 | M | near the summit path |

### Zone 3 - Whisperfrost Frontiers (Lv 30-45)
| # | Name | Biome group | Levels | Ring | Shop | Notes |
|---|---|---|---|---|---|---|
| Z3-1 | **Redwood Registry** | Forest_Redwood, Plains_Shire | 30-32 | 0.80 | F | giant redwood hut |
| Z3-2 | **Fir Filing** | Forest_Fir, Forest_Tundra | 32-34 | 0.70 | F | snow-roofed cabin |
| Z3-3 | **Hotspring Hostel** | Plains_Hotsprings | 32-34 | 0.62 | G | a hot pool (decorative, cold-resist buff later) |
| Z3-4 | **Cedar Cabinet** | Forest_Cedar | 36-38 | 0.52 | F | a cedar lodge |
| Z3-5 | **Frozen Plains Pantry** | Plains_Frozen, Forest_Cedar_Mixed, Plains_Tundra | 37-39 | 0.44 | G | the food stop |
| Z3-6 | **Everfrost Edge** | Forest_Frozen, Forest_Frozen_Light, Plains_Frozen_Frost | 41-43 | 0.30 | G | warm-up tent (fire) |
| Z3-7 | **Glacier Gate** | overlay mountains (Tier 3), glacial | 43-45 | 0.18 | M | beside the summit path |
| Z3-8 | **Outlander Row** | the reclaimed Outlander village patches | 39-45 | 0.38 | G | a **peaceful** village rebuilt as an outpost (a story beat: the Outlanders left) |

### Zone 4 - Devastated Lands (Lv 45-60)
| # | Name | Biome group | Levels | Ring | Shop | Notes |
|---|---|---|---|---|---|---|
| Z4-1 | **Cinder Check-in** | Wastes_Grasslands | 45-47 | 0.80 | G | first Zone 4 stop; heat supplies |
| Z4-2 | **Geyser Gate** | Wastes_Geysers | 48-50 | 0.62 | G | steam vents around |
| Z4-3 | **Ghost Grove Guardhouse** | Forest_Ghost, Desert_Dunes, Forest_Swamp (Z4) | 48-50 | 0.55 | G | pale trees |
| Z4-4 | **Ash Annex** | Desert_Ash, Wastes_Ash | 53-55 | 0.38 | M | ash-coated bunker |
| Z4-5 | **Magma Mile Marker** | Wastes_Lava | 55-57 | 0.28 | M | cooled-rock platform |
| Z4-6 | **Ember Roots Retreat** | Forest_Burned, Forest_Roots | 58-60 | 0.18 | G | beside the caldera path |

### Zone 5 - the Dinosaur Caves (Lv 60-75), under Zone 4
| # | Name | Biome group | Levels | Ring (cave map) | Shop | Notes |
|---|---|---|---|---|---|---|
| Z5-1 | **Fossil Pit Post** | the lost-world jungle caves | 60-65 | 0.7 | G | next to a bone pit |
| Z5-2 | **Raptor Roost Rest** | the raptor cavern | 65-70 | 0.5 | G | nest warning |
| Z5-3 | **Lava Lake Landing** | the dragon-nest approach | 70-75 | 0.3 | M | the last stop before the dragon |
(Zone 5's own town, the Egg Desk, is the zone's main warp.)

Totals: 9 + 8 + 8 + 6 + 3 = **34** outposts (+ 5 main towns = 39 warp points).

## 2. Counting against the lock ("at least one outpost per biome")
All 46 biome looks from the Mob-Levels plan are covered by the **34 groups** (R9: near-identical variants share). Sharing used: Z1 (Smooth + Birch), (Aspen + Gully), (Autumn + Moss), (Birch + Flower), mountains T1-T3, gorge T2 / T3; Z2 (savannah x4, oasis x5, plateau overlays); Z3 (redwood + shire, fir + tundra, frozen x3); Z4 (grassland, geysers, ghost + dunes + swamp, ash x2, burned + roots).
Biomes with **no outpost** on purpose: the **shores / shallow water** (they take the lowest band of the matching land region; the nearest outpost covers them), the **deep oceans** (none in the world-gen islands), and **caves** (reached from the nearby outpost).

## 3. The five outpost templates (reskinned prefabs)
| Template | Used in | Pieces |
|---|---|---|
| **Plains hut** | Zone 1 plains and Zone 2 savanna | a small timber hut, a sign post, a bed, a campfire, a hitching post, 1 shop stall |
| **Forest cabin** | Zone 1 forests, Zone 3 forests | a log cabin on a platform, a lantern, a bed, a shop counter |
| **Desert tent** | Zone 2 deserts | a canvas tent, a water jar, a bed mat, a stall |
| **Frost lodge** | Zone 3 frozen biomes | a snow-roofed lodge, a stove / fire, a bed, a stall |
| **Ash bunker** | Zone 4, Zone 5 | a half-buried stone shelter, a brazier, a bed, a stall |
Each template has: **1 shop NPC (a named clerk)**, 1 bed, 1 campfire, a **sign with the outpost name and a stamp**, a discovery marker block, 4 light sources, and a **24-block safe bubble** (spawn rule + a marker). Names and clerks reuse the lore's silly tone ("Clerk Fenwick: Branch Office 7. We have a pen."). Prefabs are **placed by reference or generated, never committed** (PROJECT-RULES 2).

## 4. Data format (one line per outpost, `outposts.properties`, editable in game)
```
outpost.z1.greenfield=Greenfield Annex|zone=1|biome=Plains_Smooth,Plains_Birch|ring=0.80|levels=1-5|template=plains|shop=general|xp=100
```
The world-gen places it at the generated position (the biome map), writes the position to `outposts.positions` once and never moves it (shared world rule). The warp record `warp:outpost:<id>` per profile lists the unlocked ones; SkyyExploration owns the "found" state (`explore:` keys).

## 5. Server Setup rows
`outposts.enabled`, `outposts.respawn` (on), `outposts.warpCooldownSeconds` (60), `outposts.combatBlock` (on), `outposts.safeRadius` (24), `outposts.discoverRadius` (24), per-zone XP, the table above (editable list: name, ring, shop, enabled).

## 6. Build notes and phases
| Phase | Content |
|---|---|
| 1 | the data format, discovery + warp unlock, the warps page by zone, the safe bubble, one template |
| 2 | the five templates, shops (NPC shops), beds / respawn, signs, the stamp collection |
| 3 | world-gen placement from the biome map, spacing check, the Zone 5 caves |
| 4 | titles, quest hooks ("Branch Office delivery"), outpost events |

## 7. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | The biome patches and their sizes in the generated islands (the placement finds one patch per group; a small patch might not hold 34). |
| 2 | How warps are stored today (SkyyExploration backbone / SkyyMenu warps page) and whether per-profile unlocks fit; world spawn is unchanged by the warps page (LOCKED). |
| 3 | The safe-bubble rule (a spawn blocker marker) and bed / respawn integration (Hytale's respawn point API). |
| 4 | Vanilla **Kweebec village** prefabs as friendly outposts in Zone 1 forests (they are friendly: "no levels"); a cheap way to place real villages instead of Template B. |
| 5 | Spacing and performance: 34 outposts means 34 small prefabs plus shops (NPC entities) loaded only near players. |

## 8. Questions for Skyy
1. Outpost **beds set respawn** (recommended) - or respawn always at the zone town?
2. Warp cost: free with a 60 s cooldown (recommended) or a small coin fee?
3. Is **"Branch Office"** the naming voice you want for outposts (matches the Department of Arrivals), or plain place names?
