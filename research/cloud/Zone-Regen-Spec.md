# Zone protection + regrowing resource blocks (SkyyZones) - spec

**Updated 2026-10-15 (Skyy's "SERVER WORLD PROTECTION, TWO KINDS", `docs/answered/world.md` line 75): two region modes - FULL and SKYBLOCK. Placeholders last a few SECONDS (not minutes), placing is a short allow-list of vanishing blocks, trees fall whole and respawn. Sections 0, 1, 3, 4, 7, 9, 11 and the questions changed; section numbers are unchanged.**

Cloud draft, 2026-10-10; revised 2026-10-15. Paper design: nothing built, no game files read. Every number is a PLACEHOLDER and a Server Setup row
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
| `world.md` 75 | **2026-10-15 SERVER WORLD PROTECTION, TWO KINDS:** "full protect. player cant break or place anything. doesn't get any items when breaking the blocks." + "the second protection will be the sky block style where you still cant break anything, and placing is limited to a few things like scaffolding that vanishes after a few seconds. but when you mine stone, you get stone, and it swaps to an unbreakable block for a few seconds, then swaps back. (look into how skyblocks mining works.) trees break down, then respawn after a bit." | the two region modes (section 3.0); regrow = seconds; scaffolding (3.4); whole-tree respawn (4.5). Replaces the old "stripped trunk" idea and the minutes-long timers |

Older drafts this replaces for the SERVER: `research/cloud/Zone-Archipelago-Spec.md` section 7.3 ("building allowed inside a zone hull")
stays true for the SOLO pack only; on the server line 63 wins (no building in zones). `research/cloud/Ore-Regrow-Spec.md` (regrow of
every worldgen vein through a position registry) is parked for the server: hand-built zones use the simpler region + block-list model below.

---

## 0. Plain words (for Skyy)

- On the server, every zone world is **locked by default**: nobody breaks, places, digs, empties a bucket or blows anything up.
- Each area (region) the builders draw is in one of **two modes**:
  - **FULL** - nothing can be broken or placed, and a hit gives no items at all (towns, spawn, decoration, the walls of a mine).
  - **SKYBLOCK** - still no building and nothing breaks, EXCEPT the resource blocks the builders listed (stone, ores, logs, crops).
    Break one and you get the normal drop + XP + collection credit; the block turns into an **unbreakable placeholder for a few
    seconds**, then turns back. You may place only a short list of things (e.g. **scaffolding**) and those **vanish after a few seconds**.
    **Trees fall whole** (all the logs drop) and the **whole tree grows back after a while**.
- Breaking works like vanilla: Mining / Foraging / Farming XP, collections, Fortune, Tree Feller, Vein Mine - all already handled by
  SkyySkills / SkyyCollections / SkyyTrees.
- Some regions need a skill level ("Requires Mining 10"). You can still walk through to explore; you just can't break there yet.
- Simple rules stop one player hogging a busy vein, macros and AFK farming (section 7).
- Player islands don't change: you build and break freely there, nothing regrows (Pocket Shards are the renewable source).

---

## 1. What Hypixel SkyBlock does (ideas in our own words; most wiki pages were blocked, so search snippets only; mining research added 2026-10-15)

| Place | What happens | Source |
|---|---|---|
| Mines (Gold Mine, Deep Caverns, Dwarven Mines) | a mined ore turns into **stone or bedrock** depending on the area; in most mines ores come back at **random spots**, in the Dwarven Mines at **fixed spots**; some later mines turn ore into air and never refill | [Ores (fandom)](https://hypixel-skyblock.fandom.com/wiki/Ores), [Dwarven Mines](https://hypixelskyblock.minecraft.wiki/w/Gates_to_the_Mines) |
| Gates | Deep Caverns need **Mining V**; ores need a minimum **Breaking Power** from the pickaxe, while **Mining Speed** only changes how fast | [SkyKings mining guide](https://skykings.net/guides/mining), [Mining (official wiki)](https://wiki.hypixel.net/Mining), [Pickaxes](https://hypixel-skyblock.fandom.com/wiki/Pickaxes) |
| The Park (foraging) | one wood type per area; old Floating Islands gated each area by a Foraging level (I-V); the Park replaced them in 0.7.4 and was revamped again in the 2025 Foraging Update; entry needs Foraging I | [The Park](https://wiki.hypixel.net/Park), [Floating Islands](https://hypixel-skyblock.fandom.com/wiki/Floating_Islands), [Lumber Jack](https://hypixel-skyblock.fandom.com/wiki/Lumber_Jack), [Foraging update notes](https://hypixelskyblock.minecraft.wiki/w/Changelog/2025/June_5) |
| Farming Islands | The Barn (Farming I: potatoes, carrots) and Mushroom Desert (Farming V: cane, cactus) are shared public farms; one patch note "added a lot more crops and increased the respawn rate" (so crops refill on a timer and the amount was tuned to player count) | [Farming Islands](https://wiki.hypixel.net/Farming_Islands), [SkyBlock 0.11.4](https://hypixel.net/threads/4145813) |
| Busy mines | Hypixel splits players over many copies (lobbies) of the same mine; Crystal Hollows lobbies close after a while | [Crystal Hollows talk](https://hypixelskyblock.minecraft.wiki/w/Talk:Crystal_Hollows), [Patch 0.19.3](https://hypixel.net/threads/5465058) |
| Macros / AFK | automation that plays for you is banned; a "disallowed AFK methods" list (glitches, third-party software, taped keys) | third-party summaries only ([mod page quoting it](https://www.modpackindex.com/mod/116734/autoskyblockrejoin)) - official text not found |
| Server plugins (Minecraft) | same pattern: placeholder block + timer per block | [BlockRegen](https://speedgot.ajg0702.us/resources/9885), [RegenOre](https://modrinth.com/plugin/regenore) |

### 1.1 How SkyBlock mining works (2026-10-15 research; own words; the exact numbers are community-measured, not official)

| Idea | What Hypixel does | What we take |
|---|---|---|
| Block strength | every block has a "Block Strength" (toughness); stone is low, rare ores high | each type keeps a `strength` row = how long a hand break takes; reserved, used only if we later take over break speed (Question 11) |
| Mining speed | a tool stat; time to break goes DOWN as speed goes up. Community estimate: ticks = roundup(300 x block strength / mining speed), seconds = ticks / 20; a floor of about 6 ticks (0.3 s) per block, but a block that already breaks in 1 tick can be mined every tick; their speed number is about 10x vanilla's Efficiency scale (talk-page claims, unverified, from 2021) | our tools already scale speed through vanilla `Quality` + SkyyGear stats; SkyyZones does NOT replace the break time (see 1.2) |
| Breaking power | a SEPARATE tool stat: the minimum power an ore needs before the tool can break it at all (coal 1, iron / lapis 2, diamond 4, highest need 8 although tools reach 12); speed never overrides it | = our hard gate. Vanilla Hytale has no such number, so the gate is (a) the region skill level (section 6) and (b) tool Quality tiers from SkyyGear (`SkyyGatherProbe`); the type row `needTier` is reserved for a Breaking-Power-like check (Question 11) |
| Placeholder | a mined ore turns into **stone or bedrock** by area (some late mines: air, never refilled); sulphur always air | stone look for easy mines, bedrock for contested ores; the placeholder is **unbreakable** (not on the allow-list) |
| Respawn timing | per area, not per player: ores come back at random spots in most mines, at fixed spots in the Dwarven Mines / Crystal Hollows, never in Glacite Mineshafts; exact seconds are not on the pages we could read | **fixed spot + a per-type timer in seconds**; the table in 4.2 is our own placeholder numbers |
| Placed blocks | blocks a player placed on their own island / garden pay no Mining XP | already true: `PlacedStore` in SkyySkills; scaffolding pays nothing (Z5 / Z15) |
| Fortune | a separate stat that multiplies the drop count | already SkyySkills' Fortune |

Sources: [Mining (official wiki)](https://wiki.hypixel.net/Mining), [Ores](https://hypixel-skyblock.fandom.com/wiki/Ores), [Pickaxes](https://hypixel-skyblock.fandom.com/wiki/Pickaxes), [Stat](https://hypixelskyblock.minecraft.wiki/w/Stat), [Talk: Mining Speed](https://hypixelskyblock.minecraft.wiki/w/Talk:Mining_Speed) (the formula; unofficial, 2021).

### 1.2 Decision: we do not rebuild break speed

SkyBlock speeds or slows a break by a formula on top of vanilla. Hytale's own tool + block quality already decides break time and SkyyGear
tunes it; copying Hypixel's formula would fight that. SkyyZones therefore only decides WHETHER a block may break and what happens after - the
same split as Hypixel's Breaking Power (allowed?) vs Mining Speed (how fast?). A later "mining speed stat" belongs to SkyyGear (Question 11).

### 1.3 Learn from (read-only ideas, no code or assets copied)

- **Block Regen 1.4.0 by NopeFR** (Hytale, ARR - NOT packable, 0.6 only; surveyed 2026-10-15): learn (a) a **delay per block** type (our type
  rows), (b) a **ghost countdown preview** - while a block is regrowing, show the player what is coming back and when (candidate for a faint
  particle / the action bar; Question 12), (c) a **floor rule** - a regrowing block respects the ground under it (our "never place into a
  player / support" checks, 4.3). We keep our own journal, gates and anti-abuse; it has none of those.
- **OrbisGuard** (ARR, region flags, needs Hyxin - not packed): learn its flag vocabulary for regions (build, block-break, use, pvp,
  mob-griefing, explosions, fluids) so our `flags` row (5.3) uses familiar words. Aura BlockFill (ARR, whole-mine resets) and HyProtect
  0.1.2 (MIT, spawn radius only) give nothing we need; VoidProtect 1.1.0 (Mods folder) is still to be checked by the local session.
- Server-plugin pattern in Minecraft (BlockRegen, RegenOre, see the table above): placeholder + timer per block - same as ours.

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

### 3.0 The two region modes

Every region has `mode=full` or `mode=skyblock`. A protected world with no region is **full** (deny everything).

| | FULL | SKYBLOCK |
|---|---|---|
| Break | denied - no crack, **no drop, no XP, no collection** | denied EXCEPT listed resource blocks (section 4) |
| Drops | none: the break is cancelled in the handler so the engine never rolls drops (probe Z19) | normal drop + XP + collections from the uncancelled event |
| Place / bucket | denied | denied EXCEPT the `placeAllow` list (scaffolding etc., 3.4); allowed blocks vanish after `scaffold.lifeSec` |
| Use (doors, seats, beds, benches, NPCs) | allowed; containers / furnaces denied unless the flag says so | same |
| Pickup of dropped items | allowed (nothing drops) | allowed |
| Typical use | towns, spawn, the hub, decor, mine walls | mines, forests, farms |

A SKYBLOCK region can lie over a FULL one: `priority` picks the winner (draw the resource area higher). This is the simple world-level
protection; the 14 island role flags are not reused here.

### 3.1 Layers (first match wins, top to bottom)

| # | Layer | Who / where | Result |
|---|---|---|---|
| 1 | Not a protected world | any world not in `zones.worlds` (solo pack, player islands, hub test worlds) | SkyyZones does nothing (SkyyIslands / vanilla rules) |
| 2 | Builder mode | has `skyyzones.build` AND switched `/zones build on` (off at every login) | everything allowed; breaks in a region do NOT start a regrow and are logged |
| 3 | SKYBLOCK region + listed block | `mode=skyblock` and the block's id is in one of the region's resource types | allowed if the gate (section 6) and anti-abuse (section 7) pass, then the regen flow (section 4) |
| 3b | SKYBLOCK region + place allow-list | `PlaceBlockEvent` with a block on `placeAllow` and under the per-player cap | allowed; the block is registered to vanish (3.4) |
| 4 | Region flag | a region may allow `use.containers`, `use.benches`, `pvp` | as the flag says |
| 5 | Default (incl. every FULL region) | everything else in a protected world | **denied**, a break gives nothing |

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

### 3.4 Temporary placing (scaffolding)

- `placeAllow` (Server Setup, per region, default scaffolding blocks only - id UNVERIFIED, probe Z14): the ONLY things a player may place in a SKYBLOCK region.
- Every allowed placement is written to the journal as a **temporary block** (`T x y z <id> <vanishAt>`) BEFORE it matters: after
  `scaffold.lifeSec` (placeholder 8 s) the block is removed again (scaffolding is only allowed on air). Crash = on restart every due `T`
  entry is removed (never a scaffold left forever).
- Limits: `scaffold.maxPerPlayer` live blocks (default 24, the oldest vanishes first), only on air, never inside a player's box, never
  inside or next to a FULL region (no bridging into a town), `scaffold.reach` blocks from the player.
- Items: placing consumes the item as usual (`scaffold.free` = free from the hotbar; Question 10). The vanishing block gives **nothing
  back** unless `scaffold.refund` (default off, no dupe path). Breaking it by hand is allowed and drops nothing (no XP, no collection).
- No XP / collection: SkySkills' `PlacedStore` already skips placed blocks; our own writes must be skipped or marked there (probe Z5 / Z15).
- A bridge needs the player to keep placing (8 s life): the intended "climb to the ledge" feel, not a permanent path.

### 3.3 Messages

Refused break: action-bar line, at most one per 2 s per player: "This area is protected." / "Requires Mining 10" / "Let others have a
turn - try another vein." (section 7). Vanilla-style toast, no chat spam (HANDOFF UI rules).

---

## 4. Break flow

### 4.1 Step by step

FULL mode never reaches this flow (the break is cancelled, no drop). The flow below is SKYBLOCK only.

| Step | Where | What |
|---|---|---|
| 1 | Break handler (sync) | block id in a resource type of the region at (x, y, z)? gate passed? anti-abuse passed? position not already depleted? -> else cancel |
| 2 | Break handler (sync) | **journal line written first** (depleted: pos, original id, type, regrowAt) - same "record before the block changes" rule as luggage (`SkyyExploration` 63-71) |
| 3 | Engine | removes the block and drops the items (vanilla drop list, tool, Fortune via SkyySkills) |
| 4 | SkyySkills / SkyyCollections (deferred) | XP + collection credit (unchanged code) |
| 5 | Our deferred task (`world.execute`, next tick) | if the spot is now air (or the engine's leftover), place the type's placeholder; if a player already filled it (impossible in a zone) or it is not air, log and keep the entry |
| 6 | Timer | at `regrowAt` (a few seconds later) put the original block back (section 4.3 if a player stands there) |

While the spot is a placeholder a hit on it is refused with no crack ("Growing back..."); an optional ghost countdown is Question 12.

### 4.2 Types, placeholders and timers (python: blocks needed = r x T / (3,600 x 0.5))

r = blocks per hour one active player takes from that type (a placeholder, measured later); U = target share of the type's blocks that
are depleted at peak (50%). With only seconds of downtime the per-player number is tiny (about 2 blocks), so the real limit is the
player's own mining speed and the crowd on one spot (C2), not scarcity. All timers are **seconds** and Server Setup rows. Hypixel keeps ore
gone longer but also has many ore spots per mine; Skyy asked for "a few seconds", so these start short and stay tunable.

| Type (default id) | Blocks (examples) | Placeholder | Regrow s | r / h | Blocks per active player | XP (existing row) |
|---|---|---|---|---|---|---|
| `stone` | Cobble, Shale, Slate, Basalt in mines | unbreakable stone look (`Rock_Bedrock` fallback) | **3** | 1,200 | 2 | 1 |
| `copper` | Ore_Copper_* | Rock_Bedrock | **4** | 600 | 2 | 5 |
| `iron` | Ore_Iron_* | Rock_Bedrock | **5** | 500 | 2 | 8 |
| `thorium` | Ore_Thorium_* | Rock_Bedrock | **6** | 450 | 2 | 18 |
| `cobalt` | Ore_Cobalt_* | Rock_Bedrock | **8** | 400 | 2 | 15 |
| `adamantite` | Ore_Adamantite_* | Rock_Bedrock | **10** | 350 | 2 | 30 |
| `mithril` | Ore_Mithril_* | Rock_Bedrock | **12** | 300 | 2 | 25 |
| `onyxium` (and later Ember etc.) | Ore_Onyxium_* | Rock_Bedrock | **15** | 250 | 3 | 40 |
| `gem` | Rock_Gem_*, Rock_Crystal_* | Rock_Bedrock | **30** | 60 | 1 | 40 / 8 |
| `crop` | Plant_Crop_* at StageFinal | the same crop's first stage | **10** | 1,500 | 9 | 3-20 |
| `tree1` / `tree2` / `tree3` (F1 / F2 / F3-F5 woods) | whole tree (all trunk + leaf blocks) - section 4.5 | none: the whole tree is removed, then re-grown | **45 / 60 / 90** | 40 trees | 2 trees | per log, as today (6 / 10 / 10-30) |

(python: stone 1,200 x 3 / 1,800 = 2.0; iron 500 x 5 / 1,800 = 1.4 -> 2; onyxium 250 x 15 / 1,800 = 2.1 -> 3; crop 1,500 x 10 / 1,800 =
8.3 -> 9; tree 40 x 60 / 1,800 = 1.3 -> 2.) Rarity stays protected by tool Quality, the skill gates, collections and price, not by the wait.
Jitter: each timer x (0.8 .. 1.2) so a vein refills block by block. `strength` / `needTier` per type are reserved (1.1; unused at first).
Zone-special hook ("resources regrow faster today", `research/cloud/Zone-Specials-Spec.md`) = a multiplier row read here.

### 4.3 When the block comes back

| Case | Rule |
|---|---|
| A player stands in the spot (feet / head box) | wait 1 s and try again; never place a solid block into a player (the luggage `occupied` check, `SkyyExploration` 4605). After 12 tries still blocked: log once, keep trying every 5 s |
| A mob / item in the spot | place anyway (items stay, mobs are pushed by the engine - UNVERIFIED; else treat like a player) |
| The placeholder is gone (admin edit, other mod) | restore the original anyway; log "placeholder missing" |
| Chunk unloaded at regrowAt | nothing is ticked; on chunk load every due entry is restored in the same pass (nobody can see it), the rest go back on the timer (Ore-Regrow-Spec section 5). `regen.loadBatch` 400 per tick if a player is within 48 blocks |
| Server off | timers are wall-clock; downtime counts (`regen.offlineCounts` true) |
| Region or type deleted / regen switched off | every depleted entry in it is restored at once (or at chunk load); nothing stays stuck as bedrock |

### 4.4 Crops

Two ways to "harvest": breaking a ripe crop (BreakBlockEvent) and F-harvest (Use + `FarmingUtil.giveDrops`, no BreakBlockEvent, the
engine resets the stage itself - `SkyyCollections` 3217-3218). Rules: only **StageFinal** crops of a listed type break or F-harvest;
unripe crops are protected. After a break: placeholder = the crop's first stage, our timer sets StageFinal after the `crop` timer (10 s). After an
F-harvest the engine already reset the stage: we still register the entry and force StageFinal at the timer. Soil under crops is
protected. Vanilla growth may also tick the placeholder (UNVERIFIED, probe Z4): if it does, timer and growth race harmlessly
(whichever is first; the entry is cleared when the block is already ripe).

### 4.5 Trees fall whole, then respawn (replaces the stripped-trunk idea)

- A tree is the connected set of trunk + leaf blocks of a listed wood in a SKYBLOCK region. Hit a listed trunk block: the **whole tree**
  comes down in one go - every trunk block drops its normal log (one drop roll each, Fortune as today), leaves drop what they drop in
  vanilla (`tree.leafDrops`), XP and collections per log as today.
- Before anything changes, the tree is **recorded**: a `G` journal line with origin, wood, `regrowAt` and a shape id (4.5.1). The shape is
  read from the world when the first block is hit (connected trunk / leaf blocks, up to `tree.maxBlocks` 600). Hand-built trees regrow
  exactly as built, natural trees as generated.
- **How it comes down** (probes Z2 / Z16): preferred - let the engine / SkyyTrees remove the rest (each extra log fires its own
  BreakBlockEvent, so protection, XP and collections apply) and record the shape from those events. Fallback: cancel the first break and
  remove every block ourselves through `performBlockBreak`, one normal event each.
- **No stump placeholder**: a bare patch (or a "regrowing" ghost, Question 12) shows where it was; the footprint stays un-placeable.
- **Respawn** (`tree1/2/3` timers, 4.2): the saved shape is written back in one pass, grouped by chunk (the `regen.passBatch` limit
  applies, a big tree may take a few ticks). A player inside the shape: retry like 4.3 or skip those blocks and retry (Z17).
- A tree stopped half-way by another plugin is simply restored whole with the rest.
- **Tree Feller** (`SkyyTrees` 787-789) becomes redundant here (a hit already fells the tree); keep its cooldown and perk text but never pay
  more than the tree's logs. **Vein Mine** (gear.md 145): each extra block is checked like a hand break (listed type, same region, gate),
  connected ore of the same type only. **Hammers**: no 3x3 in protected worlds (gear.md 145); the hammer breaks one block.
- Extra blocks from Vein Mine count toward the rate cap at half weight; a whole tree counts as one break (section 7).

#### 4.5.1 Shape store

`G x y z <wood> <regrowAt epoch s> <shapeId>` in the journal plus `regen/<world>.shapes` (`shapeId`, then `dx dy dz blockId` lines relative
to the origin, run-length packed, ~4 bytes per block: a 200-block tree is ~800 bytes). Identical trees share a shape id; natural trees get
their own. The shape is written BEFORE the first block is removed.

---

## 5. How builders mark regions and block lists

### 5.1 In game

| Command / item (admin, `skyyzones.admin`; builders `skyyzones.build`) | Does |
|---|---|
| `/zones wand` | gives the Zone Wand (our own item `Skyy_Zones_Wand`, vanilla stick look by path). Hit a block = corner A, Use a block = corner B (positions from `UseBlockEvent$Pre` / `DamageBlockEvent`, the wand never breaks anything). If the vanilla builder-tool selection can be read (probe Z6) the wand also accepts it |
| `/zones region create <id> <full or skyblock> [type,type...]` | new region (mode, 3.0) from the A-B box; `/zones region mode <id> <full or skyblock>` changes it; `/zones region addbox <id>` adds another box (a region = a list of boxes, so caves and L-shaped mines fit) |
| `/zones place add <id> <block id or "look">` / `remove` | the region's place allow-list (3.4) |
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
| `scaffold.lifeSec` 8, `scaffold.maxPerPlayer` 24, `scaffold.reach` 6, `scaffold.refund` false, `scaffold.free` false; `tree.maxBlocks` 600, `tree.leafDrops` vanilla | | live |
| `regen.jitter` 0.2, `regen.offlineCounts` true, `regen.loadBatch` 400, `regen.passBatch` 200, `regen.maxDepleted` 20,000, `regen.speedMult` 1.0 | | live |
| anti-abuse rows | section 7 | live |

### 5.3 Data files (`Skyy_SkyyZones/`, plain text, game and file always agree - CONFIG-CONTRACT)

```
# regions.properties  (one region = several lines, ids [a-z0-9_]; mode = full or skyblock, default full)
region.z1_copper_mine.world=skywynn_server
region.z1_copper_mine.boxes=120,40,-300..180,90,-240;150,30,-260..170,40,-250
region.z1_copper_mine.mode=skyblock
region.z1_copper_mine.types=stone,copper
region.z1_copper_mine.placeAllow=Scaffolding_+
region.z1_copper_mine.gate=Mining:0
region.z1_copper_mine.flags=
region.z1_copper_mine.priority=10

# types.properties
type.copper.blocks=Ore_Copper_+          # + = every id starting with this
type.copper.placeholder=Rock_Bedrock
type.copper.regrowSec=4
type.copper.skill=Mining

# regen/<world>.journal  (append-only, one line per change; snapshot regen/<world>.snap every 60 s, temp file + rename)
D x y z <original id> <type> <regrowAt epoch s>      # depleted
R x y z                                             # restored
T x y z <block id> <vanishAt epoch s>               # temporary (scaffold) block, removed at vanishAt
G x y z <wood> <regrowAt epoch s> <shapeId>         # whole tree felled, shape in regen/<world>.shapes
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
| C2 | Camping a contested node | **contested cell cap**: cell = 16 x 16 x 16; if a player took more than `regen.cellCap` blocks from one cell in `regen.cellWindow` while another player also broke in that cell in the last 60 s, that player's further breaks there are refused for `regen.cellRest` ("Let others have a turn - try another vein"). Solo camping is never limited. With seconds-long regrow this is the main fairness rule; tune it from play | 120 / 600 s / 60 s |
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

Python check, why C2 is needed: with an 8-block Iron node and T 5, a camper can take min(8 x 3,600 / 5, 500) = **500 / h** - a full player's
rate from just 8 blocks (old T 60: 480) - so on a busy server one person holds a node; C2 only bites when someone else is competing in the same cell.
Scaffold placing counts toward the A2 rate cap.

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
| Depleted entries at peak | 60 players x 700 blocks/h x 6 s average / 3,600 = **~70** (temp scaffolding adds at most 60 x 24 = 1,440); cap `regen.maxDepleted` 20,000 (oldest restored early) |
| Memory / disk | ~16 bytes per entry in memory; 5,000 entries = 80 KB; journal lines ~50 bytes, compacted into the snapshot every 60 s |
| Region lookup | per world: boxes in a chunk-keyed map (chunk -> box list), so a break checks only the few boxes touching its chunk |
| Timer | one min-heap ordered by `regrowAt`; a 1 s tick pops due entries, at most `regen.passBatch` 200 block writes per tick, grouped by chunk (one network / light update per batch, cost UNVERIFIED probe Z3) |
| Write order | journal line BEFORE the placeholder (crash = a block that regrows early, never a bedrock hole forever; with waits of seconds the flush gap can lose an entry, so `/zones audit` runs at start and restores any placeholder with no live entry); snapshot = temp file + rename; journal flushed at most every 5 s and at shutdown |
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
| Z3 | whole-tree fell + respawn (4.5, shape store), Vein Mine checks, crops (stage reset, F-harvest) | a tree falls whole and grows back as built; crops ripen again | full |
| Z3b | SKYBLOCK scaffolding (3.4): place allow-list, vanish timer, journal `T`, per-player cap; FULL mode gives no drops | scaffold vanishes after `scaffold.lifeSec` and restart cleans leftovers; FULL region gives nothing | full |
| Z4 | gates (section 6) + anti-abuse C2 / C3 / A1-A3 + status page | each rule triggers in a 2-player test | full |
| Z5 | drops to inventory (if Z8 passes), overcrowding log, zone-special multiplier, SkyyTowns uses SkyyZones | | lean |

Built and tested on a scratch copy of a test world first (smoke test), then on the first hand-built server zone.

### Engine probes (all UNVERIFIED - for the local session)

| # | Question |
|---|---|
| Z1 | Does a block set from `world.execute` right after a BreakBlockEvent survive (the engine finished removing the original first), or must we wait a tick and check for air? |
| Z2 | (changed 2026-10-15) When one trunk of a natural tree is broken, does the engine fell the whole tree itself, in how many events, and can we read every removed block (to record the shape) before it changes? |
| Z3 | Cost of 200 `setBlock` writes in one tick on loaded chunks (lighting + network); can they be grouped per chunk? |
| Z4 | Crop stage blocks: the id / state of a crop's first stage and StageFinal; does vanilla farming tick grow a placeholder on untilled / tilled soil? |
| Z5 | Does our own `setBlock` fire `PlaceBlockEvent`? (If yes SkyySkills' PlacedStore would mark regrown ores as "placed" and they would pay no XP - we would need to skip our own writes there.) |
| Z6 | Can a mod read the vanilla builder-tool selection (box corners)? Else our own wand only. |
| Z7 | Chunk-load event with the chunk ready for block writes (catch-up). |
| Z8 | Cancel the ground drop and hand the same items to the breaker (inventory / bags), without breaking SkyyCollections' exact-stack crediting. |
| Z9 | Fluids flowing into protected areas; any mob that breaks blocks. |
| Z10 | Block damage progress: shared per block or per player (for C3)? |
| Z11 | (parked) Stripped log ids - not needed now that trees are removed whole. |
| Z12 | Player network address readable from `PlayerRef` (L2). |
| Z13 | Particle outline sent to one player only (show command) - the SkyyTownProbe marker probe used `ParticleUtil` with a player list. |
| Z14 | Scaffolding in vanilla Hytale: is there a scaffold block / item, how is it placed; else can we ship a `Skyy_Scaffold` block? Does `PlaceBlockEvent` give the block id and position so we can allow-list? |
| Z15 | Removing a block a player placed from a timer: does the engine refund the item, play a break effect, or fire a BreakBlockEvent we must ignore? |
| Z16 | Whole-tree capture and rewrite: read all connected trunk + leaf blocks (with rotation / state) and write them back in a batch (cost for 200 blocks, relation to Z3); does leaf decay interfere with a regrown tree? |
| Z17 | A tree rewritten around a standing player: pushed out, stuck, or must we skip those blocks? |
| Z18 | An unbreakable placeholder with no crack: confirm cancelling `DamageBlockEvent` hides the crack, and an action-bar line is allowed on a refused hit. |
| Z19 | FULL region: confirm cancelling BreakBlockEvent in the handler means NO drop is rolled; pick-up and use of dropped items are unaffected. |

---

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | One mod for both protection and regrow ("SkyyZones"), or two mods (SkyyZones + SkyyRegen)? | [one mod, SkyyZones] |
| 2 | "Few seconds" regrow: stone 3 s, Copper 4, Iron 5, Thorium 6, Cobalt 8, Adamantite 10, Mithril 12, Onyxium 15, gems 30, crops 10, whole trees 45 / 60 / 90 s - OK as a start? | [yes, all editable in Server Setup; the old minutes-long numbers are dropped] |
| 3 | Skill gates: block BREAKING below the level (you can still walk in), or block ENTERING like SkyBlock's Deep Caverns? And the levels (Iron Mining 10, Thorium / Cobalt 20, Adamantite 30, Mithril 40)? | [break gate; those levels] |
| 4 | Placeholders: bedrock for ores (an unbreakable stone look for plain mine stone), a seedling for crops; trees have no placeholder - the whole tree vanishes and regrows (stripped-trunk idea dropped)? | [yes] |
| 5 | Solo pack: should generated zone islands get ore regrow too (the older `research/cloud/Ore-Regrow-Spec.md`), or stay fully vanilla? | [vanilla, no regrow in solo] |
| 6 | Drops straight into your inventory / bags in SKYBLOCK resource areas (nobody can grab them), or on the ground like vanilla? (FULL areas give nothing either way) | [straight to inventory, if the engine allows] |
| 7 | Anti-AFK: refuse breaks after 15 min standing in one spot, and a hard cap of 300 breaks a minute? | [yes] |
| 8 | "Let others have a turn" - limit a player only when someone else is mining the same spot (120 blocks per 10 min, then a 60 s rest)? | [yes, only when contested] |
| 9 | New 2026-10-15: which parts of the server world are FULL and which SKYBLOCK - spawn / towns / decor FULL, mines / forests / farms SKYBLOCK, anything else FULL? | [yes: only resource areas are SKYBLOCK] |
| 10 | Scaffolding: which blocks may be placed (just scaffolding?), how long (8 s), how many at once (24), must the player carry the item or is it free? | [scaffolding only, 8 s, 24, needs the item] |
| 11 | Mining speed and breaking power like SkyBlock (two new tool stats), or keep our tool Quality + skill levels? (1.1 / 1.2) | [keep Quality + levels; add later in SkyyGear if wanted] |
| 12 | While a block or tree grows back, show a faint "ghost" preview of what returns (idea from Block Regen) or just the placeholder / bare patch? | [just the placeholder; ghost later] |
| 13 | Trees: does a whole tree fall in one hit (even with a small axe), or only with enough axe power? Do leaves drop saplings / sticks as in vanilla? | [one hit fells the whole tree; vanilla leaf drops] |

## For the local session

- All 19 probes in section 11 (Z1-Z19; Z2 reworded for whole trees, Z11 parked) are UNVERIFIED and need `HytaleServer.jar` / a test session; Z1, Z2, Z5 decide whether the simple
  flow works (a Z5 "yes" needs a SkyySkills / SkyyCollections change: skip SkyyZones' own block writes in their placed-block trackers).
- Block ids UNVERIFIED: `Rock_Bedrock` is used by SkyySkills (`must("Rock_Bedrock")`, `SkyySkills/build_skyyskills_0.4.29.py` 1466) but
  its look / breakability inside a protected zone is untested; whole-tree capture (Z2 / Z16); crop stage ids (Z4).
- SkyyTownProbe T9 (`/townprobe zone`, `docs/tests/2026-10.md` 674) result not logged - its guard is the template for 3.2.
- Rollback-floor note to add to `tools/deploy_set.py` once SkyyZones ships: run `/zones restore all` before rolling it back.
- Nothing is built yet; building waits for Skyy's play test (RESUME queue) and runs as one ultracode round. Suggested order: Z0 probes -> Z1 modes + guards (FULL first, the smallest) -> Z2 regen -> Z3 / Z3b trees + scaffolding.
- `research/cloud/Zone-Archipelago-Spec.md` 7.3 and `research/cloud/Ore-Regrow-Spec.md` should get a one-line pointer to this file
  (solo-only / parked for the server) - main session call.
