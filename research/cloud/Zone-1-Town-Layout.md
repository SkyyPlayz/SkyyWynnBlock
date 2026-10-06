# Zone 1 starter town layout - the Department of Arrivals

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `docs/answered/world.md` (R9 and the 2026-10-01 town locks), `research/SkyyWorldGen-Plan.md` (section 2.3 towns), `research/cloud/Zone-Islands-Layout.md`, `Starter-Shards-Plan-2.md`, `NPC-Shops-Spec.md`, `Barks-Signs-Tips.md`, `Zone-Specials-Spec.md`, `Elites-Events-Spec.md`, `Tab-Economy.md`, `Story-Script-Draft.md`, `Outposts-List.md`, `HANDOFF.md` section 1. Map: `research/cloud/Zone-1-Town-Map.png` (made with Pillow from the same rectangles as the ASCII map below). Every size and number is a placeholder (a Server Setup row, `town.*`). All game-file facts are **UNVERIFIED**.

## 0. Decisions followed (not re-decided)

| Lock | What it means here |
|---|---|
| World R9 + 2026-10-01 | Zone 1 has a **main town = the hub**, **built around a VANILLA temple** (prefab placed by reference, never committed). Outposts are separate (Zone 1: 9, `Outposts-List.md`); the town is not one of the 34. The town has a **warp** (unlocked with the zone) and the **return portal / respawn / arrival** all land here |
| Zone-Islands-Layout 4 | Town at the **landing rim**, about `R x 0.92` = **1,021 blocks** from the island centre (R 1,110); the summit portal is at the exact centre, so the walk town -> summit is about **186 s** at 5.5 b/s. Town = safe zone |
| Starter-Shards-Plan-2 6 | Players arrive from shard 3's portal (`starter.portalTarget` = `hub` today, `zone1` after SkyyWorldGen) and "arrive at the Zone 1 temple; first warp unlocked" (Story quest 12) |
| NPC-Shops-Spec 4 | Zone 1 shops: **General Goods, Forager, Miner, Farmer**; R3: shops never sell unlocks or accessories; prices from the Bazaar base |
| Barks-Signs-Tips | 8 NPC types (clerk banker smith guide guard shop vendor keeper), sign places, the Mossby mail sign |
| Zone-Specials-Spec | **The Board** = a notice board in every town (specials, clerk of the week, countdown) |
| Elites-Events-Spec 2.5 | **Event Vendor** in the zone's town; tokens buy cosmetics, never unlocks |
| Tab-Economy | the Tab hall comes **later** (menu entry first), so only a reserved plot now |
| HANDOFF | live mods: SkyyBank 0.1.6, SkyyBazaar 0.1.4, SkyyAuctions 0.1.2, SkyyVault 0.1.5, SkyyGuilds 0.1.6, SkyyMenu 0.3.8 (menu pages). NPC shops, Board, events, Tab are **not built** |
| Story-Script-Draft 2 | the temple is a **waiting room**: benches, ticket machines, "NOW SERVING" Board, Clerk Mossby. Town is not a hostile place (Barks voice) |

## 1. The idea in one paragraph

A new player steps out of the starter portal into the **temple hall** (Waiting Room), takes a ticket, meets Mossby, and walks out the south door into a **sunny square** with the warp pad, the door home, and a long sea-view promenade. Everything a SkyBlock player needs in the first hour is **within 70 blocks** of the temple door (shops, bank, Bazaar, AH). The Summit Road leaves north through a guarded gate toward the mountain. Plenty of **filler space** (park, homes) means later buildings fit without moving anything.

## 2. Site, sizes and orientation

| Item | Value | Notes |
|---|---|---|
| Town box | **224 x 192 blocks** (7 x 6 chunks of 32) | centre = temple centre; x east, z south, **north = inland toward the mountain** |
| Island position | town centre at `(0, y, +1,021)` from the island centre (south rim, as the Zone-Islands table) | **UNVERIFIED** axis names; rotate the whole plan if the world's "south" differs |
| Coast | the void edge sits about **+90 blocks south** of the temple centre (the promenade fence); matches 1,110 - 1,021 = 89 | so the town is flat to the coast and has the sea view |
| Ground | one **flattened terrace**, y about 148 (rim about 150), blended 16 blocks into the terrain | **UNVERIFIED** height; the land mask must hold a flat "town stamp" (WorldGen 2.1) |
| Safe zone | the town box + 24 blocks: no mobs, no PvP, no void-fall into the coin penalty (respawn at the pad); `town.safeRadius` | |
| Building | the town box is **build-protected** (admins only; there is no island owner here); players may not break NPC buildings | Question 3 |
| Walk times | temple door -> any building **<= 104 blocks = 19 s walking** (section 11) | |

## 3. Districts

Coordinates are blocks from the temple centre (x east, z south). Sizes are outside dimensions. The ASCII map in section 5 and the PNG use exactly these rectangles.

| # | District | Where (x, z) | Size | Purpose | Phase |
|---|---|---|---|---|---|
| 1 | **Temple = Department of Arrivals** | -20..20, -20..20 | about 40 x 40 (vanilla prefab, **UNVERIFIED**) | arrival, respawn bed benches, ticket machines, Mossby's desk, the Board, Z1.1 quest | P0 |
| 2 | **Waiting Square** | -40..40, -40..56 | 80 x 96 | open plaza around the temple; paths meet; the warp pad, the door home, Pebble's rock; build-protected | P0 |
| 3 | **Market Row (east)** | 48..108, -44..-2 | 60 x 42 | Bazaar hall, Auction House, four shop stalls | P1-P2 |
| 4 | Bazaar hall | 48..80, -44..-20 | 32 x 24 | the Bazaar page (SkyyBazaar); a broker NPC, a price board | P1 |
| 5 | Auction House | 84..108, -44..-20 | 24 x 24 | the AH page (SkyyAuctions); clerk NPC | P1 |
| 6 | **Shop stalls** | 48..102, -14..-2 | 4 x (12 x 12) | General Goods, Forager, Miner, Farmer (2 blocks apart, faces the lane) | P2 |
| 7 | **Bank row (west)** | -108..-52, -44..-20 | 28 x 24 + 24 x 24 | **Bank** (SkyyBank, banker NPC) and the **Vault + Guild House** (SkyyVault, SkyyGuilds guild bank) | P1 |
| 8 | **Forge Quarter** | -100..-44, 40..64 | 28 x 24 Forge + 24 x 24 Crafting Hall | smith NPC, anvil / reforge / identify (SkyyGear pages), crafting benches (towns have benches; outposts do not) | P2 |
| 9 | **Tab Hall (reserved)** | -108..-60, 10..34 | 48 x 24 | empty walled plot, sign "Under Renovation"; the Tab comes later | P4 |
| 10 | **Event Square** | 48..108, 28..64 | 60 x 36 | the **Event Vendor** kiosk and a stage for the event countdown; closed until events exist | P3 |
| 11 | **Promenade** | -108..108, 68..88 | 216 x 20 | the sea walk along the rim, a low fence, void signs, benches, lanterns; the viewpoint toward Zone 2 | P0 |
| 12 | **North Gate + Summit Road** | -12..12, -96..-88; road -4..4, -88..-40 | 24 x 8 gate; 9 x 48 road | guard post; the road leaves to the island interior and the first outpost (Greenfield Annex) | P1 |
| 13 | **Orchard park** and **Kweebec homes** | -108..-48, -92..-52 and 48..108, -92..-52 | 60 x 40 each | decoration and future houses (a Kweebec village look); the quiet place; later: pets, housing | P0 / later |

Area check: town box 224 x 192 = 43,008 blocks^2 = 42 chunks. The built blocks above use about 38%; the rest is lanes, grass and room to grow.

## 4. Paths and distances

| Path | Route | Width | Block |
|---|---|---|---|
| Summit Road | North Gate -> Square (x -4..4) | 9 | gravel + cobble edge |
| Market Lane | west edge to east edge at z 0..6 (passes the temple's east and west side doors) | 7 | cobble |
| Square paving | the square around the temple | - | stone brick |
| Promenade | along z 68..88, linked by two stairs to the square (x about -28 and 28) | 20 | smooth stone, fence at the edge |
| Spur paths | 3-wide cobble to every building door | 3 | cobble |

Distances (straight line from the temple south door at (0, 20)): Bazaar door (64, -20) = 75 b; AH door (96, -20) = 104 b; General stall (54, -2) = 58 b; Bank door (-66, -20) = 77 b; Forge door (-86, 40) = 88 b; Warp pad (-20, 40) = 28 b; Event Square (78, 46) = 82 b. At 5.5 b/s the longest is about 19 s (AH). Verified below (python).

## 5. Map (top-down, 8 blocks per cell, north up)

Legend: `T` temple, `.` square, `=` summit road, `-` market lane, `G` north gate, `g` guard, `o` orchard, `h` homes, `K` bank, `V` vault + guild, `B` Bazaar, `A` Auction House, `1 2 3 4` General / Forager / Miner / Farmer, `H` Tab Hall plot, `F` forge, `W` crafting hall, `E` event square, `P` promenade, `~` void, `a` arrival pad, `M` Mossby desk, `b` Board, `m` mail box, `w` warp pad, `d` door to the home shard, `p` Pebble's rock. The temple is 5 cells wide; the sampling drops thin items, so the PNG is the better picture.

```
oooooooo    GGGG    hhhhhhhh
oooooooo     gg     hhhhhhhh
oooooooo     ==     hhhhhhhh
oooooooo     ==     hhhhhhhh
oooooooo     ==     hhhhhhhh
oooooooo     ==     hhhhhhhh
VVVVKKKK     ==     BBBBAAAA
VVVVKKKK .......... BBBBAAAA
VVVVKKKK .m........ BBBBAAAA
VVVVKKKK .mTTbbTT.. BBBBAAAA
         ..TTMMTT.. 1123344
         ..TTTTTT.. 1123344
-----------TTTTTT-----------
HHHHHHH  ..TTaaTT..
HHHHHHH  ..TTTTTT..
HHHHHHH  .......... EEEEEEEE
         ..w....d.. EEEEEEEE
 FFFFWWWW..wpp..d.. EEEEEEEE
 FFFFWWWW...pp..... EEEEEEEE
 FFFFWWWW           EEEEEEEE
PPPPPPPPPPPPPPPPPPPPPPPPPPPP
PPPPPPgPPPPPPPPPPPPPPgPPPPPP
PPPPPPPPPPPPPPPPPPPPPPPPPPPP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```
Full-size picture: `research/cloud/Zone-1-Town-Map.png` (north up, void at the bottom, every NPC and pad marked).

## 6. Arrival, warp and portals relative to the temple

| Point | Position (x, z) | Behaviour |
|---|---|---|
| **Arrival Pad** (inside the hall) | (0, 12), just inside the south door | the starter-shard portal exit, **respawn**, void-fall return, "return portal" from Zone 2; first sight is the benches, the Board and Mossby (Story 2.1). `town.arrivalPad` |
| **Warp Pad** (outside) | (-20, 40) in the Square | where **warps arrive** (menu warp to the town, found outposts' "back to town"); a ring of 8 stone blocks, sign "Warp: where do you want to wait instead?" (new line, section 9); keeps arrivals from crowding the hall |
| **Door to the home shard** | (20, 40) | the existing `/hub` / island entry (SkyyIslands): a stone arch with a sign; a way home that costs nothing |
| **Summit portal** | not in town; the island centre, 1,021 blocks north | per `Zone-Islands-Layout.md`; the town only has the **Summit Road** gate and the sign `skywynn.sign.summit.N` is at the summit, not here |
| Summit Road gate | (0, -92) | the first leg out; a guard; the road forks to the first outposts after about 60 blocks |
| Respawn | benches inside the hall; **no bed per player** needed | the hall benches are the respawn anchor |

The Zone 2 headland faces **east-north-east** (Zone-Islands 2): the **east end of the promenade** gets a viewpoint (a railed bay, sign `skywynn.sign.void.2`) where the player sees the Zone 2 rim across the 220-block gap. That is the "see Zone 2 from Zone 1" lock made visible in town.

## 7. Every NPC, placed (names are working names)

| # | NPC | Type | Position (x, z) | Does | Bark / sign |
|---|---|---|---|---|---|
| 1 | **Clerk Mossby** (Kweebec, sleepy) | clerk | (0, -10) desk, north hall | Z1.1 Take A Number, the form chain (Z1.2-Z1.5), hands the ticket, mail receiver | `bark.clerk.*`; sign `town.1`, `town.2`, `town.7` (Mail for Mossby) at the mail box (-26, -24) |
| 2 | **Pebble** (talking rock; Story: "ticket #2, still next") | guide | (-8, 48) rock in the Square | tips (exact), wrong but cheerful; **he walks off for quest Z1.2** (a stamp) so the rock stays empty during it | `bark.guide.*`; Question 4 |
| 3 | **Banker** | banker | inside the Bank, (-66, -32) | SkyyBank page (deposit, withdraw, interest) | `bark.banker.*`; sign `town.8` |
| 4 | **Vault keeper** | banker | Vault House, (-96, -32) | SkyyVault pages (the vault pages) | `bark.banker.*` |
| 5 | **Guild clerk** | clerk | Vault House, (-90, -26) | guild bank, create / invite (SkyyGuilds pages) | `bark.clerk.*` |
| 6 | **Bazaar broker** | shop | Bazaar hall, (64, -32) | opens the Bazaar page (buy 1.10 x, sell 0.90 x of base); price board on the wall | `bark.shop.*`; sign `town.10` |
| 7 | **Auction clerk** | clerk | AH, (96, -32) | opens the AH page; needs 2 new signs | `bark.clerk.*` |
| 8 | **General Goods** | shop | stall 1, (54, -8) | torches, bread, Crude arrows, bandages, lowest tools (NPC-Shops 4) | `bark.shop.*` |
| 9 | **Forager** | shop | stall 2, (68, -8) | logs, sticks, fibre, sap, basic wands / staff | `bark.shop.*` |
| 10 | **Miner** | shop | stall 3, (82, -8) | cobble, rubble, coal, copper ore and ingots | `bark.shop.*` |
| 11 | **Farmer** | shop | stall 4, (96, -8) | seeds, hoe, water bucket, crops | `bark.shop.*` |
| 12 | **Smith** | smith | Forge, (-86, 52) | reforge / identify pages (SkyyGear), sells nothing that R3 forbids; the "ring the bell" sign | `bark.smith.*`; sign `town.9` |
| 13 | **Event Vendor** | vendor | Event Square, (78, 46) | event tokens -> cosmetics, Pet Treat bundle, titles (never unlocks) | `bark.vendor.*`; P3 |
| 14-17 | **Guards x4** | guard | North Gate (0, -86), Square NW (-30, -30), Promenade (-60, 78) and (60, 78) | flavour, directions ("the Bazaar is east. Probably."), keep the square tidy | `bark.guard.*`; 4 guards, no combat role |
| - | Crafting benches (not NPCs) | - | Crafting Hall interior (-56, 52) | vanilla Workbench, Furnace, Anvil, Cooking table etc., placed by hand | - |
| - | Outpost keepers | keeper | **not in town** (outposts only) | - | `bark.keeper.*` |

Counts: **13 talkers + 4 guards = 17 NPCs** (rows 1-17). Names for the Banker, Smith etc. stay roles until Skyy picks (Barks Q3). Voice rules: barks 90 characters, signs 60, wrong-but-friendly, never "you died".

## 8. Signs (existing lines only, with positions)

| Key | Line | Place |
|---|---|---|
| `town.1` | Department of Arrivals - Please Take A Number | over the temple door |
| `town.2` | Now Serving: Someone. Probably You. | on the Board frame |
| `town.7` | Mail For Mossby: Please Do Not Wake Him | the letter box |
| `town.8` | Bank: Safe, Dry And Faintly Smug | bank door |
| `town.9` | Forge: Ring The Bell. Not That One. | forge door |
| `town.10` | Bazaar: Prices Change. Smiles Do Not. | Bazaar door |
| `void.1-5` | the five edge signs | along the promenade fence, every ~40 blocks |
| `tab.1-5` | The Tab hall lines | **later**, on the reserved plot; not placed in P0-P3 |
| `border.1` | Leaving the Emerald Wilds | **not in town** (island exit) |

New lines needed (add to `Barks-Signs-Tips.md` later; max 60 chars): Auction House, Warp Pad, Door Home, Vault + Guild, Crafting Hall, Event Square, Summit Road. Suggestions: "Auction House: Going Once. Going Twice. Gone.", "Warp Pad: Stand Still. Be Somewhere Else.", "Door Home: Your Shard Misses You".

## 9. Build notes

| Topic | Note |
|---|---|
| Temple | the vanilla temple prefab placed by reference at the stamp centre. **Size, door side, interior and which prefab are UNVERIFIED** (WorldGen plan stage 0: list the Assets.zip prefabs); the plan assumes about 40 x 40 with a south door. If it is bigger, grow the Square (it is the layout's elastic part) and keep the districts' distances |
| Pieces | prefab pieces (placed by reference): vanilla Kweebec / village houses for homes, shop stalls and banks (retextured buildings are not needed); fences, benches, lanterns, signs, banners are vanilla blocks; the Warp Pad ring, the stone arch for the home door, the ticket machines and the Board are **our own small prefab** (built from vanilla blocks, committed as code) |
| Blocks | stone brick (square), cobble / gravel (roads), smooth stone (promenade), oak / ash planks (stalls), wool banners; **only vanilla blocks** |
| Interior of the hall | 4 rows of benches (x +-4..16, z -4..8), ticket machines at (+-12, 16), the Board on the north wall at (0, -18) above the desk (ASCII `b`), Mossby's desk at (0, -10), the Arrival Pad at (0, 12) |
| Terrain | the town stamp is one land-mask rule (`wg:fn:town`) that flattens, **forbids rivers and caves** inside the box + 16, and blends the edge |
| Stamp as code | paste order: 1 terrace, 2 square + roads, 3 buildings, 4 NPC spawn markers, 5 signs; deterministic (like the starter-shard build) |
| NPC placement | admin tool in game (`/shopadmin` style) per NPC-Shops 5; the NPC list becomes a table of (id, type, x, z, facing), a Server Setup page |
| Guard rails | the promenade fence is a vanilla fence; players cannot place blocks within 12 blocks of the coast (Zone-Islands 5) |
| Lang | all text via `skywynn.sign.*` / `skywynn.bark.*` keys; no names hard-coded |

## 10. Phases (what exists now vs later)

| Phase | Content | Needs |
|---|---|---|
| **Now (exists)** | the old **/hub** temple town in the vanilla world (the Forgotten Temple, +1,000 Exploration XP discovery); live pages: Bank, Bazaar, AH, Vault, Guilds, SkyyMenu (reachable from anywhere by menu / command, no NPC) | nothing |
| **P0** | temple stamp + Square + Promenade + Arrival Pad + Mossby + benches + park (WorldGen stage 2.1: Zone 1 island, no portals) | land mask town rule, temple prefab, Mossby NPC |
| **P1** | Bank, Vault + Guild, Bazaar, AH buildings with NPCs opening **existing pages**; Board (Zone-Specials phase 1 page); North Gate; Warp Pad; home door; the guards | NPC -> custom page route (UNVERIFIED), the Board page |
| **P2** | the four shops (SkyyEconomy 0.2), Forge Quarter, crafting hall; sell-back and daily limits | NPC-Shops build |
| **P3** | Event Vendor + Event Square (events + tokens) | Elites-Events P1-P2 |
| **P4** | Tab Hall on the reserved plot (Tab-Economy), pets / housing in the homes district | Tab build, Pets |
The layout never moves between phases; empty plots (Tab, Event Square, homes) are fenced "Under Renovation" so nobody builds there.

## 11. Checks (python-verified)

| Check | Result |
|---|---|
| Town centre at 0.92 R | 1,110 x 0.92 = 1,021.2 blocks; summit walk 1,021 / 5.5 = 186 s |
| Coast distance | 1,110 - 1,021 = 89 blocks south of the temple centre = the void at z +89 |
| Town box | 224 x 192 = 43,008 = 42 chunks (7 x 6) |
| Buildings overlap | the rectangle list was checked by script: 0 overlaps |
| Longest walk from the temple door | AH door 104 b / 5.5 = 19 s |

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Which vanilla temple prefab (name, **size, door side**, interior) and whether it can be placed by reference at a flat stamp; whether more than one temple exists for Zone 1 (a Forgotten Temple is the old hub). |
| 2 | How the **starter portal** and respawn target an exact position (the Arrival Pad) in the same world. |
| 3 | Whether a placed vanilla NPC (Kweebec) can open a custom page (the Bazaar page route) and speak barks; a rock-like NPC model for Pebble. |
| 4 | Whether flat-terrace stamping and "no rivers / caves in the box" is possible in the V2 generator; the real rim height. |
| 5 | Whether the world has fixed compass axes (which way is "south") and where Zone 2's rim faces. |
| 6 | Which vanilla village / Kweebec building prefabs can be reused for banks, stalls, homes. |
| 7 | Build-protection region for the town box (the island guards of SkyyIslands may not apply). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Bank, Bazaar and AH as **walk-in buildings with NPCs** (the layout) - or stay menu-only and the buildings only decorative? | Buildings with NPCs; the menu still works everywhere |
| 2 | One town **Warp Pad** outside plus the Arrival Pad inside (two points) - OK? | Yes |
| 3 | Is the town **build-protected** (no player building), or may players build in the homes / park plots later? | Protected; homes plot opened for housing later |
| 4 | Pebble: a rock in the Square that **leaves for quest Z1.2** (stays until the quest) - or always there? | Leaves during the quest only |
| 5 | A "Summit Express" warp straight from the town to the summit (skipping the 3-minute walk), or no - the Guardian is meant to be earned? | No (walk or outposts) |
| 6 | Where does the **class pick / class trainer** live (the Waiting Room clerk, or a class hall)? | Mossby's desk, one class NPC later |
| 7 | Should the Event Vendor / Tab hall plots be visible (sealed) now, or built only when they ship? | Sealed and signed "Under Renovation" |
