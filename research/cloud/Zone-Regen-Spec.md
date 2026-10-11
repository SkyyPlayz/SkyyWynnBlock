# Zone protection + regrowing resource blocks (SkyyZones) - spec

Cloud draft, 2026-10-10. Paper design: nothing built, no game files read. Every number is a PLACEHOLDER and a Server Setup row
(times in seconds). Arithmetic in python (method shown). Builds on `research/cloud/Ore-Regrow-Spec.md` (the earlier worldgen-vein draft)
and changes its scope (section 1). Saved data, permissions, items that could be lost or duplicated, a new system = **full round / ultracode**
(PROJECT-RULES 4).

## Decisions followed (not re-decided) - `docs/answered/world.md`

| Line | Skyy's words / decision | What it means here |
|---|---|---|
| 63 | **LOCKED 2026-10-10 SERVER WORLD PLAN:** "for the server, ill hire people to help make full custom islands, and they will all be protected, and to the mining and gathering like skyblock does" -> hand-built zones, the whole zone PROTECTED; only marked resource blocks (ores, logs, crops, stone in mines) break, drop + pay XP / collections, turn into a placeholder (e.g. bedrock / stripped) and REGROW after a timer; generated islands stay the prototype / test worlds + the players' own islands; "new system needed later: zone protection + regenerating resource blocks (SkyyZones / SkyyRegen, spec first)" | the whole spec |
| 64 | LOCKED 2026-10-10: TWO MODES - SOLO pack = vanilla generation masked into islands; SERVER = hand-placed biomes / custom islands with progression paths, Zone 1 quests guide closely | protection + regen are SERVER features, off in the solo pack (section 10) |
| 62 | LOCKED 2026-10-10: keep vanilla generation, only mask it | the solo pack keeps vanilla breaking; nothing here touches WorldGen |
| 56 | LOCKED 2026-10-09: each zone = a few linked islands, zones far apart | regions are drawn per island / area inside a zone world |
| 36-46 | LOCKED 2026-09-25 island roles + flags | player islands keep SkyyIslands' rules unchanged (section 10) |
| 30 | LOCKED 2026-10-01 zone bands Z1 1-20, Z2 20-30, Z3 30-45, Z4 45-60 | per-zone gate defaults (section 6) |
| `docs/answered/gear.md` 145 | LOCKED 2026-10-10: "hammers wont work great for the server plan, but would be fine for solo ... vein mine have levels ... capped at 8 ... on ORE only CONNECTED ore of the SAME type" | hammers OFF in protected zones; Vein Mine works but every extra block must itself be a marked resource (section 4.5) |

Older drafts this replaces for the SERVER: `research/cloud/Zone-Archipelago-Spec.md` section 7.3 ("building allowed inside a zone hull")
stays true for the SOLO pack only; on the server line 63 wins (no building in zones). `research/cloud/Ore-Regrow-Spec.md` (regrow of
every worldgen vein through a position registry) is parked for the server: hand-built zones use the simpler region + block-list model below.

---

## 0. Plain words (for Skyy)

- On the server, every zone world is **locked by default**: nobody breaks, places, digs, empties a bucket or blows anything up.
- Builders draw **resource regions** (a mine, a forest, a farm) with a wand and say which blocks inside are resources (e.g. "Iron ore,
  Cobblestone"). Only those blocks break - everything else in the region (walls, rails, lamps, leaves) stays protected.
- Breaking a resource works like vanilla: the normal drop, Mining / Foraging / Farming XP, collection credit, Fortune, Tree Feller,
  Vein Mine - all already handled by SkyySkills / SkyyCollections / SkyyTrees. Then the spot becomes a **placeholder** (bedrock for ores
  and mine stone, a stripped log for logs, a seedling for crops) and **grows back** after the block's timer (stone 20 s ... Onyxium 240 s).
- Some regions need a skill level ("Requires Mining 10"). You can still walk through to explore; you just can't break there yet.
- Simple rules stop one player hogging a busy vein, macros and AFK farming (section 7).
- Player islands don't change: you build and break freely there, nothing regrows (Pocket Shards are the renewable source).

---

## 1. What Hypixel SkyBlock does (ideas in our own words; most wiki pages were blocked, so search snippets only)

| Place | What happens | Source |
|---|---|---|
| Mines (Gold Mine, Deep Caverns, Dwarven Mines) | a mined ore turns into **stone or bedrock** depending on the area; in most mines ores come back at **random spots**, in the Dwarven Mines at **fixed spots**; some later mines turn ore into air and never refill | [Ores (fandom)](https://hypixel-skyblock.fandom.com/wiki/Ores), [Dwarven Mines](https://hypixelskyblock.minecraft.wiki/w/Gates_to_the_Mines) |
| Gates | Deep Caverns need **Mining V**; ores need a minimum **Breaking Power** from the pickaxe, while **Mining Speed** only changes how fast | [SkyKings mining guide](https://skykings.net/guides/mining), [Mining (official wiki)](https://wiki.hypixel.net/Mining), [Pickaxes](https://hypixel-skyblock.fandom.com/wiki/Pickaxes) |
| The Park (foraging) | one wood type per area; old Floating Islands gated each area by a Foraging level (I-V); the Park replaced them in 0.7.4 and was revamped again in the 2025 Foraging Update; entry needs Foraging I | [The Park](https://wiki.hypixel.net/Park), [Floating Islands](https://hypixel-skyblock.fandom.com/wiki/Floating_Islands), [Lumber Jack](https://hypixel-skyblock.fandom.com/wiki/Lumber_Jack), [Foraging update notes](https://hypixelskyblock.minecraft.wiki/w/Changelog/2025/June_5) |
| Farming Islands | The Barn (Farming I: potatoes, carrots) and Mushroom Desert (Farming V: cane, cactus) are shared public farms; one patch note "added a lot more crops and increased the respawn rate" (so crops refill on a timer and the amount was tuned to player count) | [Farming Islands](https://wiki.hypixel.net/Farming_Islands), [SkyBlock 0.11.4](https://hypixel.net/threads/4145813) |
| Busy mines | Hypixel splits players over many copies (lobbies) of the same mine; Crystal Hollows lobbies close after a while | [Crystal Hollows talk](https://hypixelskyblock.minecraft.wiki/w/Talk:Crystal_Hollows), [Patch 0.19.3](https://hypixel.net/threads/5465058) |
| Macros / AFK | automation that plays for you is banned; a "disallowed AFK methods" list (glitches, third-party software, taped keys) | third-party summaries only ([mod page quoting it](https://www.modpackindex.com/mod/116734/autoskyblockrejoin)) - official text not found |
| Server plugins (Minecraft) | same pattern: placeholder block + timer per block | [BlockRegen](https://speedgot.ajg0702.us/resources/9885), [RegenOre](https://modrinth.com/plugin/regenore) |

**We copy:** fixed spots, a placeholder, a timer per block type, skill gates per area, "tune the node count to the player count".
**We differ:** ONE persistent world (no lobby copies) -> fairness rules (section 7) and a crash-safe timer store (section 9); we gate
**breaking**, not walking in ("go explore", line 64); our gates are Skyy's tool levels + skill levels, not Breaking Power.

---

## 2. What the code does today (read only - cited so builders reuse it)

| Fact | File + lines |
|---|---|
| SkyyIslands guards Break / Damage / Place / Pickup / Use / Drop / UseEntity, but **only in island worlds** (`isIslandWorld`, returns at once elsewhere) - zone worlds are NOT protected today | `SkyyIslands/build_skyyislands_0.5.5.py` 347-349 (event classes), 1663-1664, 4169-4184 (guard handle, world check 4175), 4186-4199, 5972-5974 (registration) |
| Block classifier to reuse (crop / harvest plant / container / bench / door / bed / seat) | same file 2437-2490 (`IslandPerms.isCrop`, `isHarvestPlant`, `containerKind`, `breakFlag`, `useFlag`) |
| An area guard (in-memory polygon, break / dig / place / use refused for non-admins) exists as a probe; its in-game result (TEST T9) is not in the log yet | `SkyyTownProbe/build_skyytownprobe_0.2.py` 79, 3495-3570; `docs/tests/2026-10.md` 674; plan `research/Zone-1-Town-Build-Plan.md` 34, 92 |
| XP pays from BreakBlockEvent, **deferred** with `world.execute` and paid only if the event is still not cancelled (so any guard that cancels wins); placed blocks pay nothing (`PlacedStore`, per world) | `SkyySkills/build_skyyskills_0.4.29.py` 889-897, 1440-1447 (`ignorePlaced`), 11943-12035 (PlacedStore) |
| XP per block (Mining: stone 1, Copper 5, Iron 8, Cobalt 15, Thorium 18, Mithril 25, Adamantite 30, Onyxium 40, gems 40; logs 6 / 10-30; crops 3-20, ripe only) | same file 1462-1495 |
| Explosions / fire fire `EnvironmentBreakBlockEvent` | same file 1053, 13654 |
| Natural tree fall is watched (only the hit block fires an event; physics removes the rest) | same file 560-583 |
| Scraper -> Stripped on oak trunks changes the block with **no** BreakBlockEvent | same file 9589-9591 |
| Collections credit from BreakBlockEvent, deferred + cancel-checked; placed / deco blocks give 0 | `SkyyCollections/build_skyycollections_0.2.8.py` 169-183, 3186-3200 |
| Tree Feller breaks each log through `performBlockBreak` = a real BreakBlockEvent each (protection, XP, collections apply) | `SkyyTrees/build_skyytrees_0.3.5.py` 787-789 |
| Unbreakable-block guards (Break + Damage cancelled outside Creative) and "registry written BEFORE the block is placed" | `SkyyExploration/build_skyyexploration_0.2.5.py` 63-71, 1033-1034, 5351-5394 |
| Setting / clearing a block from code and "never place a solid block into a player" | same file 4590-4601 (`place` / `clear`), 4605 (`occupied`) |
| Tool Quality gates ore; no vanilla pickaxe has Quality on OreCopper / OreIron / ... so hard gates need SkyyGear overrides | `SkyyGatherProbe/build_skyygatherprobe_0.1.py` 32; `docs/log/2026-10.md` line 143 |

**Consequence:** SkyyZones only has to (a) cancel what is not allowed, synchronously, and (b) swap in the placeholder + run the timer.
Drops, XP, Fortune, collections, Feller and Vein Mine already flow from the uncancelled BreakBlockEvent.

---

## 3. Protection model (deny by default, allow-list per region)

### 3.1 Layers (first match wins, top to bottom)

| # | Layer | Who / where | Result |
|---|---|---|---|
| 1 | Not a protected world | any world not in `zones.worlds` (solo pack, player islands, hub test worlds) | SkyyZones does nothing (SkyyIslands / vanilla rules) |
| 2 | Builder mode | has `skyyzones.build` AND switched `/zones build on` (off at every login) | everything allowed; breaks in a region do NOT start a regrow and are logged |
| 3 | Resource region + listed block | the block's id is in one of the region's resource types | allowed if the gate (section 6) and anti-abuse (section 7) pass, then the regen flow (section 4) |
| 4 | Region flag | a region may allow `use.containers`, `use.benches`, `pvp`, `place` (e.g. a future plot area) | as the flag says |
| 5 | Default | everything else in a protected world | **denied** |

### 3.2 What "denied" covers (events - VERIFIED in our scripts, behaviour in a zone UNVERIFIED)

| Action | Event | Default in a zone |
|---|---|---|
| Break / dig progress | `BreakBlockEvent`, `DamageBlockEvent` | denied (no crack animation either) |
| Place / bucket | `PlaceBlockEvent` | denied |
| Hit-to-break via Use Primary, Scraper strip, F-harvest | `UseBlockEvent$Pre` (Primary; Scraper / crop Use) | denied unless the block is a listed resource |
| Doors, seats, beds, crafting benches, NPCs | `UseBlockEvent$Pre`, `UseEntityEvent$Pre` | **allowed** (towns need them) |
| Chests, furnaces | `UseBlockEvent$Pre` (container / processing) | denied unless the region flag allows |
| Explosions, fire | `EnvironmentBreakBlockEvent` | cancelled in protected worlds |
| Fluids, mob griefing | UNVERIFIED (probe Z9) | builders avoid open source blocks near builds |

Guards cancel **in the handler** (synchronously), like `SkyyIslands` 4169-4184 and `SkyyExploration` 5351-5394, so every deferred
XP / collection task sees the cancel.

### 3.3 Messages

Refused break: action-bar line, at most one per 2 s per player: "This area is protected." / "Requires Mining 10" / "Let others have a
turn - try another vein." (section 7). Vanilla-style toast, no chat spam (HANDOFF UI rules).

---

## 4. Break flow

### 4.1 Step by step

| Step | Where | What |
|---|---|---|
| 1 | Break handler (sync) | block id in a resource type of the region at (x, y, z)? gate passed? anti-abuse passed? position not already depleted? -> else cancel |
| 2 | Break handler (sync) | **journal line written first** (depleted: pos, original id, type, regrowAt) - same "record before the block changes" rule as luggage (`SkyyExploration` 63-71) |
| 3 | Engine | removes the block and drops the items (vanilla drop list, tool, Fortune via SkyySkills) |
| 4 | SkyySkills / SkyyCollections (deferred) | XP + collection credit (unchanged code) |
| 5 | Our deferred task (`world.execute`, next tick) | if the spot is now air (or the engine's leftover), place the type's placeholder; if a player already filled it (impossible in a zone) or it is not air, log and keep the entry |
| 6 | Timer | at `regrowAt` put the original block back (section 4.3 if a player stands there) |

### 4.2 Types, placeholders and timers (python: blocks needed = r x T / (3,600 x 0.5))

r = blocks per hour one active player takes from that type (a placeholder, measured later); U = target share of the type's blocks that
are depleted at peak (50%). "Blocks per active player" tells builders how big to make a node set: a mine expecting 20 players on Iron needs
about 20 x 17 = **340** Iron blocks.

| Type (default id) | Blocks (examples) | Placeholder | Regrow s | r / h | Blocks per active player | XP (existing row) |
|---|---|---|---|---|---|---|
| `stone` | Cobble, Shale, Slate, Basalt in mines | Rock_Bedrock | **20** | 1,200 | 13 | 1 |
| `copper` | Ore_Copper_* | Rock_Bedrock | **45** | 600 | 15 | 5 |
| `iron` | Ore_Iron_* | Rock_Bedrock | **60** | 500 | 17 | 8 |
| `thorium` | Ore_Thorium_* | Rock_Bedrock | **90** | 450 | 22 | 18 |
| `cobalt` | Ore_Cobalt_* | Rock_Bedrock | **120** | 400 | 27 | 15 |
| `adamantite` | Ore_Adamantite_* | Rock_Bedrock | **150** | 350 | 29 | 30 |
| `mithril` | Ore_Mithril_* | Rock_Bedrock | **180** | 300 | 30 | 25 |
| `onyxium` (and later Ember etc.) | Ore_Onyxium_* | Rock_Bedrock | **240** | 250 | 33 | 40 |
| `gem` | Rock_Gem_*, Rock_Crystal_* | Rock_Bedrock | **600** | 60 | 20 | 40 / 8 |
| `log1` (F1 common woods) | Wood_<Oak / Birch / ...>_Trunk | the stripped trunk of the same wood (UNVERIFIED ids), else Rock_Bedrock | **60** | 900 | 30 | 6 |
| `log2` (F2) | uncommon woods | stripped / bedrock | **75** | 800 | 33 | 10 |
| `log3` (F3-F5) | northern / strange woods | stripped / bedrock | **90** | 700 | 35 | 10-30 |
| `crop` | Plant_Crop_* at StageFinal | the same crop's first stage | **45** | 1,500 | 38 | 3-20 |

Why these are much shorter than `research/cloud/Ore-Regrow-Spec.md` (600-2,400 s): that draft refilled whole generated islands
(tens of thousands of ore). Hand-built mines are small, so short timers keep them looking full, like SkyBlock. Rarity stays protected by
tool Quality, the skill gates, collections and price. Jitter: each timer x (0.8 .. 1.2) so a vein refills block by block.
Zone-special hook ("resources regrow faster today", `research/cloud/Zone-Specials-Spec.md`) = a multiplier row read here.

### 4.3 When the block comes back

| Case | Rule |
|---|---|
| A player stands in the spot (feet / head box) | wait 5 s and try again; never place a solid block into a player (the luggage `occupied` check, `SkyyExploration` 4605). After 12 tries (60 s) still blocked: log once, keep trying every 30 s |
| A mob / item in the spot | place anyway (items stay, mobs are pushed by the engine - UNVERIFIED; else treat like a player) |
| The placeholder is gone (admin edit, other mod) | restore the original anyway; log "placeholder missing" |
| Chunk unloaded at regrowAt | nothing is ticked; on chunk load every due entry is restored in the same pass (nobody can see it), the rest go back on the timer (Ore-Regrow-Spec section 5). `regen.loadBatch` 400 per tick if a player is within 48 blocks |
| Server off | timers are wall-clock; downtime counts (`regen.offlineCounts` true) |
| Region or type deleted / regen switched off | every depleted entry in it is restored at once (or at chunk load); nothing stays stuck as bedrock |

### 4.4 Crops

Two ways to "harvest": breaking a ripe crop (BreakBlockEvent) and F-harvest (Use + `FarmingUtil.giveDrops`, no BreakBlockEvent, the
engine resets the stage itself - `SkyyCollections` 3217-3218). Rules: only **StageFinal** crops of a listed type break or F-harvest;
unripe crops are protected. After a break: placeholder = the crop's first stage, our timer sets StageFinal after 45 s. After an
F-harvest the engine already reset the stage: we still register the entry and force StageFinal at the timer. Soil under crops is
protected. Vanilla growth may also tick the placeholder (UNVERIFIED, probe Z4): if it does, timer and growth race harmlessly
(whichever is first; the entry is cleared when the block is already ripe).

### 4.5 Logs, trees, Feller, Vein Mine, hammers

- Only listed trunk ids break; leaves, branches and roots stay protected (and keep the tree looking whole).
- A stripped placeholder keeps supporting the tree, so physics should not fell it (UNVERIFIED, probe Z2). If the engine drops the tree
  before our placeholder lands, fallback: cancel the break and do it ourselves (place the placeholder, give the drops through the engine's
  drop helper as `SkyyCollections` CollDrops does, and pay XP / collection through the bridge) - more work, only if Z2 fails.
- **Tree Feller** (`SkyyTrees` 787-789): each extra log fires its own BreakBlockEvent, so each must be a listed log in the region; each gets
  a placeholder + timer. The Feller cooldown already limits it.
- **Vein Mine** (gear.md 145): same - each extra block is checked like a hand break (listed type, same region, gate). Connected ore of the
  same type only, as Skyy locked.
- **Hammers**: no 3x3 in protected worlds (gear.md 145: solo only); the hammer still breaks the one block it hits.
- Extra blocks from Feller / Vein Mine count toward the rate cap at half weight (section 7).

---

## 5. How builders mark regions and block lists

### 5.1 In game

| Command / item (admin, `skyyzones.admin`; builders `skyyzones.build`) | Does |
|---|---|
| `/zones wand` | gives the Zone Wand (our own item `Skyy_Zones_Wand`, vanilla stick look by path). Hit a block = corner A, Use a block = corner B (positions from `UseBlockEvent$Pre` / `DamageBlockEvent`, the wand never breaks anything). If the vanilla builder-tool selection can be read (probe Z6) the wand also accepts it |
| `/zones region create <id> [type,type...]` | new region from the A-B box; `/zones region addbox <id>` adds another box (a region = a list of boxes, so caves and L-shaped mines fit) |
| `/zones type add <type> <block id or "look">` | adds a block id to a type; `look` = the block you are looking at (all its variants by prefix with `+`) |
| `/zones show <id> [seconds]` | particle outline of every box for 30 s (only to you) |
| `/zones info` | for the block you look at: world protected?, region(s), type, gate, depleted until |
| `/zones build on / off` | builder bypass, off at every login; on = a HUD tag "BUILD MODE" |
| `/zones status` | depleted count per region / type, next due, refused breaks last hour, flagged players (section 7) |
| `/zones restore <id> / all` | puts every depleted block of a region back now |
| `/zones audit <id>` | scans a region for placeholder blocks with no journal entry (lost write) and offers to restore them to the type's default block |

### 5.2 Server Setup (SkyWynn Menu -> Server Setup -> Zones; `tools/skyycfg.py`, times in seconds)

| Page / row | Default | Live? |
|---|---|---|
| `zones.worlds` (protected worlds, one per line) | empty (nothing protected until the server world exists) | live |
| `regen.enabled` | true | live (off = restore everything) |
| Types table: `type.<id>` = blocks / placeholder / regrowSec / skill | section 4.2 | live (new timers apply to the next break) |
| Regions table: `region.<id>` = world / boxes / types / gate / flags / priority | none | live (edits from the wand land here) |
| `regen.jitter` 0.2, `regen.offlineCounts` true, `regen.loadBatch` 400, `regen.passBatch` 200, `regen.maxDepleted` 20,000, `regen.speedMult` 1.0 | | live |
| anti-abuse rows | section 7 | live |

### 5.3 Data files (`Skyy_SkyyZones/`, plain text, game and file always agree - CONFIG-CONTRACT)

```
# regions.properties  (one region = several lines, ids [a-z0-9_])
region.z1_copper_mine.world=skywynn_server
region.z1_copper_mine.boxes=120,40,-300..180,90,-240;150,30,-260..170,40,-250
region.z1_copper_mine.types=stone,copper
region.z1_copper_mine.gate=Mining:0
region.z1_copper_mine.flags=
region.z1_copper_mine.priority=10

# types.properties
type.copper.blocks=Ore_Copper_+          # + = every id starting with this
type.copper.placeholder=Rock_Bedrock
type.copper.regrowSec=45
type.copper.skill=Mining

# regen/<world>.journal  (append-only, one line per change; snapshot regen/<world>.snap every 60 s, temp file + rename)
D x y z <original id> <type> <regrowAt epoch s>      # depleted
R x y z                                             # restored
```

Overlapping regions: the higher `priority` wins for gate and flags; resource types are the union. Box limits: 512 x 384 x 512 per box,
64 boxes per region (keeps the lookup cheap).

---

## 6. Per-zone level gates

Gate = a skill level to **break** in that region (walking in stays free: "go explore", line 64). Tool Quality gates stay on top
(SkyyGear). Defaults follow the SUGGESTED access levels of `research/cloud/Gathering-Tiers-Draft.md` line 64 (not locked - Question 3).

| Zone (band) | Mines | Forests | Farms |
|---|---|---|---|
| Zone 1 (1-20) | stone + Copper: none; Iron: **Mining 10** | F1: none; F2 (blue forest edge): Foraging 10 | group A: none; B: Farming 10 |
| Zone 2 (20-30) | Thorium + Cobalt: **Mining 20** | F2: Foraging 10; F3 start: 20 | C: Farming 20 |
| Zone 3 (30-45) | Adamantite: **Mining 30**; Mithril: **Mining 40** | F3 / F4: Foraging 20 / 30 | D: Farming 30 |
| Zone 4 (45-60) | Onyxium / Ember: Mining 45 | F5: Foraging 40 | eternal seeds: Farming 40 |
| Zone 5 (60-75) | deep ores: Mining 50 | - | - |

A region flag `gateEntry` (default off) can instead turn players back at the edge (SkyBlock's Deep Caverns style) for a special area.
Levels read from SkyySkills over the bridge (`skill:` keys, plain java types).

---

## 7. Anti-abuse (concrete rules, all rows)

| # | Problem | Rule | Row (default) |
|---|---|---|---|
| C1 | One player "locks" a vein by standing next to it | regrow never waits for players to leave (only for a player INSIDE the block's space, 4.3) | - |
| C2 | Camping a contested node | **contested cell cap**: cell = 16 x 16 x 16; if a player took more than `regen.cellCap` blocks from one cell in `regen.cellWindow` while another player also broke in that cell in the last 60 s, that player's further breaks there are refused for `regen.cellRest` ("Let others have a turn - try another vein"). Solo camping is never limited | 120 / 600 s / 60 s |
| C3 | Block sniping (finishing someone else's half-broken block) | **hit lock**: a block another player damaged in the last `regen.hitLockMs` takes no damage from you | 3,000 ms |
| C4 | Too few nodes for the crowd | builder rule: size node sets with the 4.2 table; `/zones status` shows a region's peak depleted share; above 70% for 10 min logs "region X is overcrowded" | 0.7 |
| A1 | AFK with an auto-clicker on one node | **stand-still rule**: if the player's position stayed within 4 blocks for `regen.afkSeconds`, regen breaks are refused until they move 8+ blocks ("Stretch your legs - move a little to keep mining") | 900 s |
| A2 | Macro speed | **rate cap**: more than `regen.maxPerMin` regen breaks in 60 s (Feller / Vein Mine extras count half) -> refused for 10 s + one admin log line. 300 = a steady 5 blocks/s, above any hand play (python: 5 x 60) | 300 |
| A3 | Perfect-rhythm bots | **flag only**: after 200 regen breaks, if the gaps between breaks vary less than 15 ms (standard deviation), the player goes on `/zones status` "flagged"; no automatic punishment (false positives) | 15 ms, on |
| L1 | Alts farming high-tier nodes | gates are per profile and per skill level: a new alt only reaches the free Zone 1 nodes | - |
| L2 | Several alts on one busy node | C2 counts each account; optional `regen.maxPerAddress` accounts from one network address breaking in one region (0 = off; households share addresses - UNVERIFIED that the address is readable) | 0 |
| L3 | Alts feeding items to a main | items are tradeable by design; collections and XP go only to the breaker's own active profile (existing code); the economy limits are SkyyEconomy's job | - |
| X1 | Placing an ore to mine it again | placing is denied in zones; builder-mode breaks start no regrow and pay as usual only if `regen.builderPays` | false |
| X2 | Restart / profile-switch loops | timers are wall-clock and in the journal; switching profile changes nothing in the world | - |
| X3 | Duplicate drops through the regrow | the timer restores a BLOCK, never an item; one break = one drop roll | - |
| X4 | Breaking the placeholder | not on any allow-list -> protected by the default layer | - |

Python check, why C2 is needed: with an 8-block Iron node and T 60, a camper can take min(8 x 3,600 / 60, 500) = **480 / h** - almost a
full player's rate - so on a busy server one person could hold a node; C2 only bites when someone else is competing in the same cell.

---

## 8. Multiplayer fairness

| Topic | Rule |
|---|---|
| Who gets the block | the player whose hit breaks it (vanilla), protected by C3 |
| Drops | vanilla ground drops; option `regen.dropsToInventory` (default **true** if probe Z8 works): drops go straight to the breaker's inventory / bags so nobody grabs them; else the engine's pickup delay (UNVERIFIED owner lock) |
| XP / collections | breaker only, as today; parties share nothing from gathering (unchanged) |
| Same world for all | no lobby copies (one persistent world); crowding is handled by node counts (4.2) and C2 |
| New vs. veteran | lower-zone nodes stay useful (cheap timers, no gate), so high players do not need to camp them; gates keep new players out of nothing they need |
| PvP | off in resource regions by default (`pvp` flag) |

---

## 9. Performance and restart safety

| Item | Number / rule (python) |
|---|---|
| Depleted entries at peak | 60 players x 700 blocks/h x 75 s average / 3,600 = **~875**; cap `regen.maxDepleted` 20,000 (oldest restored early) |
| Memory / disk | ~16 bytes per entry in memory; 5,000 entries = 80 KB; journal lines ~50 bytes, compacted into the snapshot every 60 s |
| Region lookup | per world: boxes in a chunk-keyed map (chunk -> box list), so a break checks only the few boxes touching its chunk |
| Timer | one min-heap ordered by `regrowAt`; a 1 s tick pops due entries, at most `regen.passBatch` 200 block writes per tick, grouped by chunk (one network / light update per batch, cost UNVERIFIED probe Z3) |
| Write order | journal line BEFORE the placeholder (crash = a block that regrows early, never a bedrock hole forever); snapshot = temp file + rename; journal flushed at most every 5 s and at shutdown |
| Start | load snapshot + replay journal; due entries in loaded chunks restore in the first ticks, the rest at chunk load |
| Lost write | `/zones audit` finds placeholders with no entry and restores them to the type's first block id |
| Turning off | `regen.enabled` false or removing the mod: restore every entry first (`/zones restore all`); rollback note for `tools/deploy_set.py`: "before rolling SkyyZones back, run /zones restore all" |

---

## 10. What stays on player islands (and the solo pack)

| World | Rules |
|---|---|
| Player islands (SkyyIslands) | unchanged: the 14 role flags (`research/Island-Settings-Spec.md` section 3; `docs/answered/world.md` 36-46) - owners and trusted build and break freely; crops grow the vanilla way; trees replant from saplings (SkyySkills `placed.skipSaplings`); **no regrow** (finite by design, `research/cloud/Ore-Regrow-Spec.md` section 9); Pocket Shards are the renewable source |
| Starter shards (SkyyIslands) | same as player islands |
| Solo pack zone islands (WorldGen) | not in `zones.worlds` -> vanilla breaking + building (Archipelago 7.3), hammers allowed; towns protected by SkyyTowns. Ore regrow of generated veins = the parked Ore-Regrow draft (Question 5) |
| Server zone worlds | everything in this spec |
| Server towns | protected the same way (no resource regions); SkyyTowns can later use SkyyZones regions instead of its own polygon (one guard, not two) |

---

## 11. Build phases (each small and testable)

| Phase | Work | Done when | Round |
|---|---|---|---|
| Z0 | engine probes (below), one op-only probe pack, one test session | answers logged | probe |
| Z1 | SkyyZones 0.1: protected worlds, deny-by-default guards (3.2), builder mode, regions + wand + show / info, Server Setup Zones page | in a protected test world nothing breaks / places; builder mode does; wand regions save + reload | **full** (permissions, saved data) |
| Z2 | regen for stone + ores: types table, journal, placeholder, timer, catch-up, audit, restore | mine ore -> bedrock -> back after T; restart mid-timer keeps it; unloaded chunk catches up | **full** (saved data, item dupe risk) |
| Z3 | logs (stripped placeholder, Feller + Vein Mine checks), crops (stage reset, F-harvest) | a tree keeps standing; Feller logs all regrow; crops ripen again | full |
| Z4 | gates (section 6) + anti-abuse C2 / C3 / A1-A3 + status page | each rule triggers in a 2-player test | full |
| Z5 | drops to inventory (if Z8 passes), overcrowding log, zone-special multiplier, SkyyTowns uses SkyyZones | | lean |

Built and tested on a scratch copy of a test world first (smoke test), then on the first hand-built server zone.

### Engine probes (all UNVERIFIED - for the local session)

| # | Question |
|---|---|
| Z1 | Does a block set from `world.execute` right after a BreakBlockEvent survive (the engine finished removing the original first), or must we wait a tick and check for air? |
| Z2 | Breaking one trunk of a natural tree with a solid placeholder put back next tick: does physics still fell the tree? |
| Z3 | Cost of 200 `setBlock` writes in one tick on loaded chunks (lighting + network); can they be grouped per chunk? |
| Z4 | Crop stage blocks: the id / state of a crop's first stage and StageFinal; does vanilla farming tick grow a placeholder on untilled / tilled soil? |
| Z5 | Does our own `setBlock` fire `PlaceBlockEvent`? (If yes SkyySkills' PlacedStore would mark regrown ores as "placed" and they would pay no XP - we would need to skip our own writes there.) |
| Z6 | Can a mod read the vanilla builder-tool selection (box corners)? Else our own wand only. |
| Z7 | Chunk-load event with the chunk ready for block writes (catch-up). |
| Z8 | Cancel the ground drop and hand the same items to the breaker (inventory / bags), without breaking SkyyCollections' exact-stack crediting. |
| Z9 | Fluids flowing into protected areas; any mob that breaks blocks. |
| Z10 | Block damage progress: shared per block or per player (for C3)? |
| Z11 | Stripped log ids for every wood (Scraper only proves Oak); else bedrock / a darker log for the rest. |
| Z12 | Player network address readable from `PlayerRef` (L2). |
| Z13 | Particle outline sent to one player only (show command) - the SkyyTownProbe marker probe used `ParticleUtil` with a player list. |

---

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | One mod for both protection and regrow ("SkyyZones"), or two mods (SkyyZones + SkyyRegen)? | [one mod, SkyyZones] |
| 2 | Regrow timers: stone 20 s, Copper 45, Iron 60, Thorium 90, Cobalt 120, Adamantite 150, Mithril 180, Onyxium 240, gems 600, logs 60-90, crops 45 - OK as a start? | [yes, all editable in Server Setup] |
| 3 | Skill gates: block BREAKING below the level (you can still walk in), or block ENTERING like SkyBlock's Deep Caverns? And the levels (Iron Mining 10, Thorium / Cobalt 20, Adamantite 30, Mithril 40)? | [break gate; those levels] |
| 4 | Placeholders: bedrock for ores and mine stone, a stripped log for logs, a seedling for crops? | [yes] |
| 5 | Solo pack: should generated zone islands get ore regrow too (the older `research/cloud/Ore-Regrow-Spec.md`), or stay fully vanilla? | [vanilla, no regrow in solo] |
| 6 | Drops straight into your inventory / bags in resource areas (nobody can grab them), or on the ground like vanilla? | [straight to inventory, if the engine allows] |
| 7 | Anti-AFK: refuse breaks after 15 min standing in one spot, and a hard cap of 300 breaks a minute? | [yes] |
| 8 | "Let others have a turn" - limit a player only when someone else is mining the same spot (120 blocks per 10 min, then a 60 s rest)? | [yes, only when contested] |

## For the local session

- All 13 probes in section 11 (Z1-Z13) are UNVERIFIED and need `HytaleServer.jar` / a test session; Z1, Z2, Z5 decide whether the simple
  flow works (a Z5 "yes" needs a SkyySkills / SkyyCollections change: skip SkyyZones' own block writes in their placed-block trackers).
- Block ids UNVERIFIED: `Rock_Bedrock` is used by SkyySkills (`must("Rock_Bedrock")`, `SkyySkills/build_skyyskills_0.4.29.py` 1466) but
  its look / breakability inside a protected zone is untested; stripped log ids per wood (Z11); crop stage ids (Z4).
- SkyyTownProbe T9 (`/townprobe zone`, `docs/tests/2026-10.md` 674) result not logged - its guard is the template for 3.2.
- Rollback-floor note to add to `tools/deploy_set.py` once SkyyZones ships: run `/zones restore all` before rolling it back.
- `research/cloud/Zone-Archipelago-Spec.md` 7.3 and `research/cloud/Ore-Regrow-Spec.md` should get a one-line pointer to this file
  (solo-only / parked for the server) - main session call.
