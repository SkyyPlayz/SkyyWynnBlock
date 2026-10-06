# Zone 1 starter town layout - the Department of Arrivals (v2, organic)

Cloud draft, 2026-10-06 (v2 the same day, after Skyy's map review). Paper design; nothing built. Inputs read: `docs/answered/world.md` (R9, the 2026-10-01 town locks and the **2026-10-06 lock: "too square, look at skyblocks hub ... keep the vanilla temple right behind where you spawn in and the center of the town ... the town was built around an ancient temple"**), `research/SkyyWorldGen-Plan.md` (2.3 towns), `research/cloud/Zone-Islands-Layout.md`, `Starter-Shards-Plan-2.md`, `NPC-Shops-Spec.md`, `Barks-Signs-Tips.md`, `Zone-Specials-Spec.md`, `Elites-Events-Spec.md`, `Tab-Economy.md`, `Story-Script-Draft.md`, `Outposts-List.md`, `HANDOFF.md` section 1. Map: `research/cloud/Zone-1-Town-Map.png` (v2); the old square map is kept as `Zone-1-Town-Map-v1.png` to compare. Every size and number is a placeholder (a Server Setup row, `town.*`). All game-file facts are **UNVERIFIED**.

## v1 -> v2 changes

| Topic | v1 | v2 |
|---|---|---|
| Shape | rectangles on a grid, one straight cross road | **organic**: winding roads that follow the slope (contours), irregular paved plazas, buildings turned to face their lane |
| Temple | centre, arrival pad *inside* the hall | centre **and on a small knoll** (the oldest thing here); **spawn is on its south steps, temple right behind you** |
| Districts | 13 districts | **same 13 districts, same numbers, same sides of town** (bank west, market east, forge south-west, events south-east, gate north) |
| Plazas | one 80 x 96 rectangle | one round-ish **Waiting Square** around the temple + 6 small irregular plazas (market, bank, forge yard, event ring, gate, viewpoint) |
| Coast | straight fence line | a wavy cliff edge; the east end bends north into a **headland viewpoint** toward Zone 2 |
| Filler | none | 9 small unnamed **filler houses** along the lanes (a lived-in town; future shops or homes) |
| Walks | straight lines, longest 19 s | measured **along the roads**: core services 17-24 s, North Gate 31 s (section 5) |
| ASCII map | 8-block grid | dropped (a grid cannot show curves); the PNG is the map |

## 0. Decisions followed (not re-decided)

| Lock | What it means here |
|---|---|
| World 2026-10-06 (Skyy) | keep the district layout; make it **organic like the Hypixel SkyBlock Hub**; the **vanilla temple at the centre, right behind spawn**; the town grew around the ancient temple; **Skyy upgrades its exterior later** (we never edit the prefab here) |
| World R9 + 2026-10-01 | Zone 1 main town = the hub, built around a vanilla temple (placed by reference, never committed); outposts separate (9 in Zone 1); town warp; return portal / respawn / arrival land here |
| Zone-Islands-Layout 4 | town at the landing rim (R 1,110); summit portal at the island centre; town = safe zone |
| Starter-Shards-Plan-2 6 | players arrive from shard 3's portal "at the Zone 1 temple; first warp unlocked" (Story quest 12) |
| NPC-Shops-Spec 4 | Zone 1 shops: General Goods, Forager, Miner, Farmer; R3: shops never sell unlocks or accessories |
| Barks-Signs-Tips / Zone-Specials / Elites-Events / Tab-Economy | 8 NPC types and the signs; the Board; the Event Vendor (cosmetics only); the Tab hall later (reserved plot) |
| HANDOFF | live pages: SkyyBank 0.1.6, SkyyBazaar 0.1.4, SkyyAuctions 0.1.2, SkyyVault 0.1.5, SkyyGuilds 0.1.6, SkyyMenu 0.3.8. NPC shops, Board, events, Tab are **not built** |
| Story-Script-Draft 2 | the temple hall is the **Waiting Room**: benches, ticket machines, "NOW SERVING" Board, Clerk Mossby |

## 1. The idea in one paragraph

You step off the starter portal onto the **worn south steps of an ancient temple**. The temple is right behind you; in front, a round, sun-warmed **Waiting Square** spills downhill toward the sea. The town was never planned: it grew outward from the temple, so its lanes **curl around the knoll and follow the slope**, widen into little plazas where they meet, and squeeze between houses turned every which way. Five lanes leave the square like roots: **Summit Road** north, **Market Way** east, **Bank Street** west, **Forge Lane** south-west and **Fair Lane** south-east; two stairs drop to the **cliff Promenade**. Everything a first-hour player needs is within about **24 s of walking**.

## 2. What we take from the Hypixel SkyBlock Hub

| Hub fact (search snippets; the wiki pages are blocked here) | Source | Used how |
|---|---|---|
| The **Village is the spawn point and the centre** of the Hub; it "splits off into other areas focused on specific Skills" | [hypixel-skyblock.fandom.com/wiki/Village](https://hypixel-skyblock.fandom.com/wiki/Village), [Locations/Hub Island](https://hypixelskyblock.minecraft.wiki/w/Locations/Hub_Island) | spawn at the centre; lanes leave the centre toward themed districts (and on out to the outposts) |
| The Village holds the **Auction House, Bank, Library, Blacksmith, Bazaar Alley, Tavern, Farmhouse** and more, packed close | same | every service in walking reach of spawn; filler houses between them |
| **Bazaar Alley** is its own narrow spot, with the **Trade Center next to it** | [Trade Center](https://hypixel-skyblock.fandom.com/wiki/Trade_Center) | Bazaar + AH + stalls clustered round one **market plaza** (district 3) |
| Unnamed connector spots like **Village Plaza, Barrier Street** sit between areas | [Locations](https://hypixelskyblock.minecraft.wiki/w/Locations), [Village Plaza](https://hypixel-skyblock.fandom.com/wiki/Village_Plaza) | small irregular plazas where lanes meet |
| A **Hub map in front of spawn** | [Island](https://hypixelskyblock.minecraft.wiki/w/Island) | a town map sign by the spawn steps (next to the Board) |

From memory, **UNVERIFIED**: the Hub's lanes are not straight; they bend around buildings and hills, plazas are odd-shaped, and areas blend into each other with no hard edge. We copy only that **idea** (no build, no layout data).

## 3. Site, sizes and orientation

| Item | Value | Notes |
|---|---|---|
| Town area | an irregular blob about **270 x 230 blocks**, about **49,600 blocks^2** of land inside the town limit (python, section 12) | centre = temple centre; x east, z south, **north = inland toward the mountain** |
| Island position | temple about **1,015 blocks** south of the island centre (0.91 R); summit walk 1,015 / 5.5 = **185 s** | v1 said 1,021; the wavy coast moved the void edge (below). **UNVERIFIED** axis names |
| Coast | the cliff edge waves between **85 and 101 blocks** south of the temple; the east end curls north to a headland (Zone 2 viewpoint) | the Promenade runs ~11 blocks inside the edge |
| Ground | not one flat terrace any more: a **gentle slope**, about 2 blocks per 25 rising north, plus a **4-block knoll** under the temple; roads keep to the contours | **UNVERIFIED** heights; the land mask rule `wg:fn:town` still forbids rivers / caves and smooths, but keeps the slope |
| Safe zone | the town limit + 24 blocks: no mobs, no PvP; `town.safeRadius` | |
| Building | build-protected (admins only) | Question 3 |

## 4. Districts (same 13 as v1; positions moved, numbers kept)

Coordinates are blocks from the temple centre (x east, z south); "size" is the footprint. Shapes are in the PNG.

| # | District | Centre (x, z) | Size / shape | Purpose | Phase |
|---|---|---|---|---|---|
| 1 | **Temple = Department of Arrivals** | 0, 0 on the knoll | about 40 x 40 (vanilla prefab, **UNVERIFIED**), south door | Waiting Room hall, Mossby, the Board, Z1.1 quest | P0 |
| 2 | **Waiting Square** | 0, 10 | round-ish plaza, 96 x 92 (about 6,700 b^2), paving rings round the temple | spawn steps, warp pad, door home, Pebble; all five lanes start here | P0 |
| 3 | **Market Row (east)** | plaza 86, -16 | irregular plaza 45 x 44 | Bazaar, AH and the four stalls around one plaza | P1-P2 |
| 4 | Bazaar hall | 80, -50 | L-shape 34 x 26, turned -10 deg | the Bazaar page; broker; price board | P1 |
| 5 | Auction House | 118, -24 | octagon, 28 across, domed | the AH page; clerk | P1 |
| 6 | **Shop stalls** | on the plaza's south-east curve | 4 x (12 x 10), each turned to face the plaza | General Goods, Forager, Miner, Farmer | P2 |
| 7 | **Bank Row (west)** | plaza -84, -32 | small plaza 38 x 32 | Bank (28 x 22, -80, -60) and Vault + Guild (L 26 x 26, -116, -34) | P1 |
| 8 | **Forge Quarter (south-west)** | yard -80, 48 | yard 31 x 28 | Forge (L 28 x 24, -104, 50; smith) and Crafting Hall (22 x 17, -52, 60; benches) | P2 |
| 9 | **Tab Hall (reserved)** | -112, 22 | 40 x 22 sealed plot, off a short lane from Bank Row | "Under Renovation"; the Tab later | P4 |
| 10 | **Event Square (south-east)** | 86, 52 | round 46 x 42, three amphitheatre steps + a stage | Event Vendor; event countdown | P3 |
| 11 | **Promenade** | along the cliff | 280 blocks long, 9 wide, fence + lanterns every 20 | sea walk, void signs; **east headland = Zone 2 viewpoint** (124, 60) | P0 |
| 12 | **North Gate + Summit Road** | gate 4, -110 | gate 26 x 7 with a small gate plaza; road 110 blocks of S-curves | guard; the way to the interior and the first outpost | P1 |
| 13 | **Orchard park (NW)** and **Kweebec homes (NE)** | -84, -95 and 75, -95 | orchard in bent rows; 9 houses along a looping lane | quiet places; future housing / pets | P0 / later |

Plus 9 **filler houses** (8-12 blocks, mixed angles) along Summit Road, Bank Street, Market Way and Forge Lane: decoration now, spare shop / NPC homes later.

## 5. Roads and walk times

| Road | From -> to | Width | Look |
|---|---|---|---|
| Summit Road | square north -> North Gate, 3 S-bends up the slope | 8 | gravel, cobble edge |
| Market Way | square east -> market plaza, rises a little | 7 | cobble |
| Bank Street | square north-west -> bank plaza, curves round the knoll | 7 | cobble |
| Forge Lane | square south-west -> forge yard, downhill | 6 | cobble |
| Fair Lane | square south-east -> Event Square | 6 | cobble |
| Homes Lane / Orchard Path | off Summit Road, looping NE / NW | 5 | packed dirt |
| Small lanes | Tab plot, forge -> promenade, market -> homes, events -> market | 4 | dirt |
| Promenade + 2 stairs | the cliff walk; stairs from the square's south rim | 9 / 4 | smooth stone, fence |

Walk lengths **along the roads** from the spawn point (0, 27), at 5.5 b/s (python, from the same spline points as the PNG):

| To | Blocks | Seconds |
|---|---|---|
| Mossby's desk (in through the south door) | 33 | 6.0 |
| Warp Pad / Door Home | 29 / 31 | 5.3 / 5.6 |
| Crafting Hall / Forge door | 80 / 95 | 14.5 / 17.3 |
| Event Vendor | 94 | 17.1 |
| Bazaar door / Farmer stall / General stall | 117 / 120 / 122 | 21.3 / 21.8 / 22.2 |
| Bank door / Vault + Guild | 125 / 132 | 22.7 / 24.0 |
| Auction House door | 133 | 24.2 |
| Tab Hall plot (P4) / North Gate | 164 / 169 | 29.8 / 30.7 |

The bends add about 25% over v1's straight lines; that is the price of "organic". If it feels long, shrink the town (`town.scale`) rather than straighten roads.

## 6. Map

`research/cloud/Zone-1-Town-Map.png` (1600 x 1112): north up, void at the bottom, contour lines every 2 blocks, numbered markers 1-19 with a legend. Drawn with Pillow from the coordinates in sections 4, 5, 7 (deterministic). The v1 map is `Zone-1-Town-Map-v1.png`.

## 7. Arrival, warp and portals

| Point | Position (x, z) | Behaviour |
|---|---|---|
| **Spawn = Arrival Pad** | (0, 27) on the temple's south steps, facing south | starter-shard portal exit, **respawn**, void-fall return, Zone 2 return portal. The temple fills the view behind you; the square, the sea and the lanes are in front. `town.arrivalPad` |
| Temple hall (Waiting Room) | inside, 7 blocks behind spawn | benches, ticket machines, Mossby, the Board: the first quest says "turn around and take a number" |
| **Warp Pad** | (-24, 44) | where warps arrive; a stone ring; keeps warps off the spawn steps |
| **Door to the home shard** | (26, 44) | stone arch to the player's island; free |
| Town map sign | beside the spawn steps | the Hub-style "map in front of spawn" (new sign line) |
| North Gate | (4, -110) | Summit Road leaves here; the summit is ~1,015 blocks north, not in town |
| Zone 2 viewpoint | (124, 60) headland | railed bay, sign `skywynn.sign.void.2`; Zone 2's rim faces east-north-east (Zone-Islands 2) |

## 8. Every NPC, placed (names are working names)

| # | NPC | Type | Position (x, z) | Does | Bark / sign |
|---|---|---|---|---|---|
| 1 | **Clerk Mossby** (Kweebec) | clerk | (0, -8) desk, north hall | Z1.1 Take A Number, form chain Z1.2-Z1.5, mail | `bark.clerk.*`; `town.1`, `town.2`, `town.7` at the mail box (-27, -16) |
| 2 | **Pebble** (talking rock) | guide | (-8, 50) in the square | tips; walks off during Z1.2 | `bark.guide.*`; Question 4 |
| 3 | Banker | banker | Bank, (-80, -56) | SkyyBank page | `bark.banker.*`; `town.8` |
| 4 | Vault keeper | banker | Vault + Guild, (-118, -38) | SkyyVault pages | `bark.banker.*` |
| 5 | Guild clerk | clerk | Vault + Guild, (-112, -28) | SkyyGuilds pages, guild bank | `bark.clerk.*` |
| 6 | Bazaar broker | shop | Bazaar hall, (78, -52) | Bazaar page (buy 1.10 x, sell 0.90 x base) | `bark.shop.*`; `town.10` |
| 7 | Auction clerk | clerk | AH, (118, -24) | AH page | `bark.clerk.*` |
| 8-11 | General Goods / Forager / Miner / Farmer | shop | the four stalls on the market plaza's south-east curve, about 30 blocks from (86, -16) | NPC-Shops 4 stock lists | `bark.shop.*` |
| 12 | Smith | smith | Forge, (-104, 48) | reforge / identify pages | `bark.smith.*`; `town.9` |
| 13 | Event Vendor | vendor | Event Square stage, (86, 52) | tokens -> cosmetics, titles (never unlocks) | `bark.vendor.*`; P3 |
| 14-17 | Guards x4 | guard | North Gate (4, -100), square NW (-34, -26), Promenade (-64, 75) and (64, 89) | directions, flavour, no combat | `bark.guard.*` |
| - | Crafting benches | - | Crafting Hall (-52, 60) | vanilla stations, hand-placed | - |

Counts: **13 talkers + 4 guards = 17 NPCs** (unchanged from v1). Voice rules: barks 90 characters, signs 60, wrong-but-friendly.

## 9. Signs

Same keys as v1: `town.1` (temple door), `town.2` (Board), `town.7` (mail box), `town.8` (Bank), `town.9` (Forge), `town.10` (Bazaar), `void.1-5` along the Promenade fence (~every 55 blocks over its 280), `tab.1-5` later on the plot, `border.1` not in town. New lines needed (max 60 chars, for `Barks-Signs-Tips.md` later): Auction House, Warp Pad, Door Home, Vault + Guild, Crafting Hall, Event Square, Summit Road, **Town Map** ("You Are Here. The Temple Was Here First.").

## 10. Build notes

| Topic | Note |
|---|---|
| Temple | vanilla prefab by reference at the knoll top; **size, door side, interior UNVERIFIED**. Spawn sits on its door side, whichever that is: rotate the whole town plan to match. Skyy restyles the exterior later; the town only touches the ground around it |
| Organic, but buildable | lanes are drawn as **splines** (5-8 control points each, in the stamp code); the stamp paints them 1 block at a time, following the ground height; buildings are prefabs rotated in **90-degree steps** in game (**UNVERIFIED**: free-angle placement), so the map's small tilts become "turned to face the lane" by choosing the nearest rotation and nudging the lane |
| Paving | square: stone brick in rings round the temple; plazas: mixed cobble / gravel edges (irregular blobs, not rectangles); lanes: cobble, dirt at the edges of town |
| Pieces | vanilla village / Kweebec houses for homes, stalls, filler; fences, lanterns, benches, signs vanilla; Warp ring, home arch, ticket machines, the Board = our own small prefabs from vanilla blocks |
| Stamp order | 1 terrain smooth (keep slope + knoll), 2 square + plazas, 3 lanes, 4 buildings, 5 trees, 6 NPC markers, 7 signs; deterministic |
| NPC placement | admin tool in game; NPC list = (id, type, x, z, facing), a Server Setup page |
| Guard rails | Promenade fence; no player blocks within 12 of the coast (Zone-Islands 5) |

## 11. Phases (unchanged order)

| Phase | Content |
|---|---|
| Now (exists) | the old /hub temple town in the vanilla world; live pages by menu / command |
| **P0** | temple + knoll, Waiting Square, spawn steps, Promenade, Mossby, benches, orchard, filler houses |
| **P1** | Bank, Vault + Guild, Bazaar, AH with NPCs opening existing pages; Board; North Gate; Warp Pad; home door; guards; town map sign |
| **P2** | the four stalls, Forge Quarter, Crafting Hall |
| **P3** | Event Square + Event Vendor |
| **P4** | Tab Hall on the reserved plot; pets / housing in the homes |

The layout never moves between phases; empty plots are sealed "Under Renovation".

## 12. Checks (python-verified)

| Check | Result |
|---|---|
| Town position | void edge ~95 blocks south -> 1,110 - 95 = 1,015 = 0.914 R; summit walk 185 s |
| Town land area | 49,611 blocks^2 inside the limit and north of the cliff (grid count) |
| Plaza areas | square 6,726; market 1,462; event 1,539; bank 968; forge 700; gate 314; viewpoint 368 |
| Lengths | Summit Road 110 blocks (gate at z -110); Promenade 280 |
| Walks | section 5 table, along the splines; longest service walk AH 133 b = 24.2 s |
| Map | 1600 x 1112 PNG, < 450 KB; no label overlaps (placement script checks label boxes) |

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Which vanilla temple prefab: name, **size, door side**, interior; can it sit on a knoll (raised ground) by reference? |
| 2 | Can the starter portal / respawn target an exact outdoor block (the steps)? |
| 3 | Prefab rotation: only 90-degree steps, or free angles? (drives how "tilted" buildings can be) |
| 4 | Can the V2 generator smooth a **sloped** town (keep the slope, no rivers / caves) instead of a flat terrace? Real rim height? |
| 5 | Can a placed Kweebec NPC open a custom page and bark? A rock model for Pebble? |
| 6 | World compass axes, and where Zone 2's rim faces (east headland viewpoint). |
| 7 | Build protection for an irregular town limit (a polygon, or a box + exceptions?). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Does v2 read "Hub enough"? More bends / more filler houses, or calmer? | Keep v2 |
| 2 | Spawn on the temple's **outside steps** (temple behind you), with the Waiting Room hall just inside - OK? | Yes |
| 3 | Town is build-protected; open the homes area for housing later? | Protected; homes later |
| 4 | Pebble leaves during quest Z1.2 only? | Yes |
| 5 | Walks are now 17-24 s to services (v1: up to 19 s). Fine, or shrink the town 15%? | Fine |
| 6 | Bank, Bazaar, AH as walk-in buildings with NPCs (menu still works everywhere)? | Yes |
| 7 | Sealed plots (Tab Hall, Event Square) visible now? | Sealed, "Under Renovation" |
