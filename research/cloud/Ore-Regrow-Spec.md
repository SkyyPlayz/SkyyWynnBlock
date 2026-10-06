# Ore regrow spec - veins that grow back in the shared zone world

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/cloud/WorldGen-Stage-2-Draft.md` (section 3 ores, Q1 / Q2, UNVERIFIED 9), `research/cloud/Zone-4-5-Materials.md` (Ember density, Q2 "no regrow in profile worlds"), `research/cloud/Gathering-Tiers-Draft.md`, `research/cloud/Collection-Unlocks-Draft.md` (0.1 curves), `research/cloud/Pocket-Shards-Spec.md`, `docs/answered/*.md` (no lock on regrow; Fortune on all tiers is LOCKED, bags.md 2026-10-06). All numbers are placeholders and Server Setup rows (times in seconds). Saved data (a registry) = a **full round** (PROJECT-RULES 4).

## 0. Why (python-checked)

| Fact | Number |
|---|---|
| Zone 1 Iron | ~21,800 ore (~4,800 veins at ~4.5 ore) |
| One player to Iron collection VII / VIII / IX (S curve 5,000 / 10,000 / 20,000) | **23% / 46% / 92%** of the whole island's Iron (the Stage 2 draft's "23%" is tier VII) |
| Zone 3 Mithril pocket | ~4,600 ore: **10 players at 250 each = gone in ~2 h** (1.8 players-to-gate at 2,500) |
| One player mining 280 ore/h (Zone-4-5 placeholder) | 5,000 ore = 18 h, 10,000 = 36 h, 20,000 = 71 h |
| Without regrow, Iron is empty after | 4.4 players at 5,000 each |

So a shared world with a finite ore pile punishes the later players. Regrow is the fix. Zone-4-5 Q2 ("no regrow") was written for per-profile worlds; the zone islands are shared, so it is replaced for the zone islands only (section 9 for profile worlds).

## 1. What SkyBlock does (search snippets; the wiki pages are blocked)

| Fact | Source |
|---|---|
| Mined ores become **Stone or Bedrock** (depends on the area); in the Gold Mine / Deep Caverns most ores then **respawn at random spots**; in the Dwarven Mines ores have **fixed spawn places** | [Hypixel SkyBlock Wiki: Ores](https://hypixel-skyblock.fandom.com/wiki/Ores), [Dwarven Mines](https://hypixelskyblock.minecraft.wiki/w/Gates_to_the_Mines) (snippets) |
| A developer quote: ores respawn "30 minutes" (including mithril), with a plan to shorten it (old thread, **UNVERIFIED** today) | [SkyBlock Patch 0.11](https://hypixel.net/threads/3749492) (snippet) |
| Every ore block is a shared resource; Hypixel mines are instanced per lobby, not one eternal world | search results |
| Server plugins use the same pattern (placeholder block, timer, per-block regen) | [BlockRegen](https://speedgot.ajg0702.us/resources/9885), [RegenOre](https://modrinth.com/plugin/regenore) (snippets) |

We copy: **placeholder block + timer + fixed spots**. We differ: one persistent world, so we need a persisted registry (section 3) and a chunk catch-up rule (section 5).

## 2. Which blocks regrow, and how we tell them apart

**Only worldgen ore veins regrow.** A block regrows only if its exact position is in the **vein registry**, written by WorldGen when it places the vein (Stage 2.7). The test is **position membership, never block id**, so:

| Case | Result |
|---|---|
| Ore block placed by a player (same id) | not in the registry: breaks normally, drops, **never regrows**, never counts for a collection (existing rule: ore counts only when broken by the player from a natural block; placed blocks never count) |
| Player digs a natural ore, places stone in the hole | the entry is cancelled (section 7); nothing is created from player work |
| Ore from other mods / vanilla veins outside our zones | not touched |
| Zone-island ore in a player-claimed area (a plot) | still regrows, unless claim rules say no building there (open: Q5) |
| Profile worlds and private islands | **no regrow** (section 9) |

Registry entry = `packed x,y,z (int32 chunk-local) + oreType (byte)` = about 5 bytes per ore block. All zone ore is ~650,000 blocks (Z1 98k, Z2 79k, Z3 60k, Z4 ~250k at the old Ember density), so about **3 MB on disk**. It is stored per chunk (a sidecar next to the chunk, or a per-region file), written once at worldgen and edited only when a vein is mined. A "depleted" flag + `regrowAt` (epoch seconds) is added per mined entry.

## 3. The block while it regrows

A new block, **Depleted Vein** (`Skyy_Depleted_Vein`, working name): a dark cracked host-rock look with a faint dust particle, **unbreakable by tools** (very high Quality, no drops, no XP, no collection), not placeable by players, not pushed by fluids. Lore line on inspect: "ORE UNDER REVIEW. Department of Arrivals thanks you for your patience." If a custom block is not allowed (UNVERIFIED 1) fall back to the host rock (Stone / Basalt) with the registry marker doing all the work; the unbreakable bedrock-like look is only to stop players treating it as a free tunnel wall. Bedrock itself is rejected: vanilla bedrock may not be breakable-by-us and cannot show a different texture per zone.

## 4. Regrow timers per tier (the balance python)

Model: N players mining 280 ore/h each in the zone; supply per hour = ore blocks x access x 3,600 / T, where **access** = the share of the zone players actually reach (walk range from the town and paths; 25% = healthy, 10% = a very busy server). Target: **utilisation (demand / supply) <= ~50% at 25% access**. Regrow is per block (each mined block returns after its own timer).

| Ore (zone) | Ore blocks | N | Demand/h | Max T for 50% at 25% access | Chosen `ore.regrowSec` | Util. at 25% / 10% access |
|---|---|---|---|---|---|---|
| Copper (Z1) | 76,000 | 25 | 7,000 | 4,886 | **600** | 6% / 15% |
| Iron (Z1) | 21,800 | 20 | 5,600 | 1,752 | **900** | 26% / 64% |
| Thorium (Z2) | 63,900 | 15 | 4,200 | 6,846 | **1,200** | 9% / 22% |
| Cobalt (Z2, Z3) | 15,300 / 34,700 | 15 / 10 | 4,200 / 2,800 | 1,639 / 5,577 | **1,200** | 37% / 92% (Z2), 11% / 27% (Z3) |
| Adamantite (Z3) | 20,800 | 10 | 2,800 | 3,343 | **1,500** | 22% / 56% |
| Mithril (Z3 pocket) | 4,600 | 10 | 2,800 | 739 | **900** | 61% / 152% (see below) |
| Mithril (Z4) | 32,100 | 10 | 2,800 | 5,159 | **1,800** | 17% / 44% |
| Ember (Z4, new density, section 8) | ~71,000 | 20 | 5,600 | 5,725 | **1,800** | 16% / 39% |
| Ember (Z5, 3.5 / cell) | ~9,600 | 6 | 1,680 | 2,571 | **1,200** | 23% / 58% |
| Amberite (Z5) | 50,400 | 6 | 1,680 | 13,500 | **2,400** | 9% / 22% |
| Drakonite (Z5 deep) | 4,400 | 6 | 1,680 | 1,179 | **900** | 38% / 95% |

Rule of thumb in the table: **the timer follows the pocket size, not the rarity** (small pockets get short timers, or they would be empty for everyone). Rarity is already protected by the pickaxe gate, the collection gates and price. Two small pockets (Z3 Mithril, Z5 Drakonite) still run tight at 10% access: the cheap fix is a bigger pocket (Z3 Mithril veins 0.4 -> 0.8 / cell = ~9,200 ore), not a shorter timer (Q3). Jitter: each timer is `T x (0.8 .. 1.2)` so blocks do not pop in as one wave. Zone-specials hooks (`research/cloud/Zone-Specials-Spec.md`, "ore regrows faster today" = `T x 0.75`) read the same row.

## 5. Chunk-unloaded behaviour (catch-up on load)

- Time is **wall-clock** (`regrowAt` epoch seconds). An unloaded chunk is never ticked.
- On chunk load: every depleted entry with `regrowAt <= now` is restored **at once, in the same load pass** (nobody can see it, the chunk was empty); entries still waiting go to the timer queue.
- Restore at load is chunked to <= `ore.loadBatch` 400 blocks per tick if the chunk already has a player within 48 blocks (avoids a spike, no visible pop-wave).
- Server downtime counts as time passed (`ore.offlineCounts` true). Off = timers freeze while the server is down (Q4).
- `ore.regrowNoPlayer` (the draft's 32-block rule, default 32 in the Stage 2 draft): see the anti-camp section; this spec proposes default **0 (off)**.

## 6. Anti-camp and fairness

Camping means standing on a vein and farming it every cycle, or blocking others. With the 32-block "no player near" rule the vein NEVER regrows while anyone stands there, which makes a camper a lock; so the default drops it and uses these instead:

| Measure | Row | Default | Why |
|---|---|---|---|
| Timer runs while players are near | `ore.regrowNoPlayer` | 0 (off); old draft value 32 | stops one player locking a vein; set 32 back if pop-in beside the player feels bad |
| Never place inside a player | (code) | on | a block that would trap a player waits 5 s and retries; never suffocate |
| Per-block jitter, random order | `ore.regrowJitter` | 0.2 | no instant refill-all; farming a vein is not a predictable loop |
| Vein fatigue (soft) | `ore.fatigueOre` / `ore.fatigueWindow` | **off** (0) | optional: after M ore from one 16x16 cell in W seconds, that player's swing time x1.5 there. Off by default: yield caps feel bad, the timers already limit a camper to ~(vein size) ore per T |
| Per-player yield cap | none | none | breaks Fortune fantasy; collection gates and R3 already pace |
| Collections | unchanged | | only natural, player-broken blocks count |
| AFK / macro | `ore.afkCheck` | idea only | reuse any existing anti-AFK later; not part of this build |

A camper at one 6-ore vein with T = 900 gets 6 ore per 15 min = 24 ore/h, far under the 280/h of someone walking veins, so camping loses by itself.

## 7. Exploits

| Exploit | Closed by |
|---|---|
| Place an ore block, mine it for drops / collection | not in the registry: nothing drops from a "placed" id for collections; regrow never applies |
| Mine natural ore, place real ore there, repeat | the registry entry is already depleted; placed ore is a placed block; nothing counts |
| Replace the Depleted Vein with another block | Depleted Vein is unreplaceable / unplaceable-over; if forced (admin tool, other mod), reconcile on next timer: block != placeholder -> entry dropped, host-rock stays |
| Explosion / other mod removes the vein | a once-per-minute reconcile on loaded chunks: a registry entry whose block is neither ore nor placeholder becomes depleted (regrowAt = now + T) if the position is air / host rock, dropped otherwise |
| Piston / fluid pushes Depleted Vein | block flagged immovable (UNVERIFIED 4) |
| Duplicate drops through the regrow | the regrow re-places the BLOCK only, never an item; one block mined = one drop roll |
| Collection farming via restart loops | timers are wall-clock, persisted; a restart does not reset them |
| Mining Fortune doubling the pile | see section 7a |

### 7a. Mining Fortune and Pocket Shards

- Fortune raises **items per block**; it never changes how a block depletes. Demand in BLOCKS = items needed / average Fortune multiplier. Fortune +100 (LOCKED: Fortune on all tiers) halves the blocks needed, so late game the timers above are **conservative** (the table is the no-Fortune worst case).
- **No "ore stays" chance** from Fortune (an infinite-ore loop); a block always depletes when broken.
- **Pocket Shards do not mine the world.** They are item-producing minion-like blocks (Pocket-Shards-Spec) with their own delay and "count when collected" rule, so they put **zero** pressure on the shared ore and are the renewable income for players who dislike the grind. Shared-world regrow and shards never interact; no row links them.
- A **private mine** (profile worlds, private islands): not in this spec; if Skyy adds one, ore there is `ore.regrowProfile` 0 (off) by Zone-4-5 Q2 unless asked.

## 8. Ember density fix (Q2)

Zone 4 Ember is 3.0 veins / cell x 7 = **21 ore / cell**, 10x the Z4 Mithril (2.1) and almost 6x Z1 Iron (3.6). With regrow the pile is no longer the limit, so the extra density only makes the ore cheap to find (shorter walks = faster than the 280 / h pace) and fills the world with 11,000-coin ore (the Zone-4-5 Bazaar base). Proposal:

| Row | Old | New |
|---|---|---|
| `ore.z4.ember.veinsPerCell` | 3.0 (1 surface + 2 cave) | **1.0** (0.4 surface + 0.6 cave) |
| Ember ore / cell, Z4 | 21 | **7** (~71,000 total, 25,447 cells x 40% share) |
| `ore.z5.ember.veinsPerCell` | 1.0 | **0.5** (3.5 / cell, ~9,600 total) |
| Demand check | 20 players to R curve VIII (5,000) = 100,000 ore = 47% of old pile | = 140% of the new pile, **covered by regrow** (supply 142,000/h at T 1,800 and full access) |

It stays "the bulk ore" of Zone 4 (Stage 2 draft default) because 7 / cell is still twice Iron's 3.6, but no longer 10x. If Skyy wants it as rare as other metals, use 3 / cell (30,500 ore) and T 900. Amberite at 11 / cell is the next outlier (flagged, not changed here: Q6).

## 9. Profile worlds

No regrow (Zone-4-5 Q2 stays for profile worlds): a profile world is the player's own, finite ore is an intended pace (SkyBlock islands have none anyway), and Pocket Shards are the renewable source there. Row `ore.regrowProfile` default 0 for owners who want it.

## 10. Performance and persistence

| Item | Number / rule |
|---|---|
| Registry size | ~650,000 ore blocks x 5 B = ~3.3 MB on disk, loaded **per chunk** (~25 entries avg, ~125 B) |
| Depleted entries at any time | players x ore/h x T/3,600; 20 players, 280/h, T 1,800 = **~2,800** per zone; cap `ore.maxDepleted` 20,000 (oldest restored early) |
| Tick cost | one pass per second over a time-ordered queue (min-heap or timing wheel) of loaded-chunk entries; pops only due items, max `ore.passBatch` 200 per pass; no per-block ticking |
| Block writes | batched per chunk, one lighting / network update per batch (UNVERIFIED 3 for cost) |
| Persistence | `regrowAt` + oreType in the chunk sidecar, written with the chunk on save and at most every 60 s; write temp file, rename |
| Self-heal | on load: a Depleted Vein block with no entry gets `regrowAt = now + T` with the oreType from the registry; an entry with no placeholder (lost write) = ore restored. Either loss is recoverable |
| Disable | `ore.regrow.enabled` false: stop the queue, **restore every depleted entry on chunk load** (nothing stays stuck) |

## 11. Server Setup rows (seconds)

`ore.regrow.enabled` true, `ore.<ore>.regrowSec` (table in section 4), `ore.regrowJitter` 0.2, `ore.regrowNoPlayer` 0 (blocks; 32 = old draft), `ore.offlineCounts` true, `ore.loadBatch` 400, `ore.passBatch` 200, `ore.maxDepleted` 20,000, `ore.fatigueOre` 0, `ore.fatigueWindow` 600, `ore.regrowProfile` 0, `ore.<z>.ember.veinsPerCell` (section 8). Menu: Server Setup -> World -> Ore regrow (live: timers, jitter, enabled; restart: density rows only apply to NEW chunks).

## 12. Build stages

| Stage | Work | Done when | Round |
|---|---|---|---|
| R0 | probes (section list below) | answers recorded | none |
| R1 | Depleted Vein block + registry writer in WorldGen (stage 2.7 hook) | `/wg survey` counts registry entries = ore blocks | full |
| R2 | break hook -> placeholder + `regrowAt`; timer queue; persist | mine, wait, ore returns; restart keeps timers | full |
| R3 | chunk catch-up, reconcile, self-heal, disable path | unloaded 2 h then load: all restored | full |
| R4 | Server Setup rows, `/wg regrow status` (counts, next due) | rows live-edit | lean |
| R5 | zone-special hook, Ember density change | Ember survey = 7 / cell within 20% | lean |

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Can a mod register an unbreakable, non-placeable custom block with a host-rock texture and a particle? Else the host-rock fallback. |
| 2 | Is there a block-break event with the position and the player (to tell a tool break from an explosion / fluid), and a block-change event for other removals? |
| 3 | Setting a block on a loaded chunk from a tick task: cost per batch of 200, lighting and network cost; can writes be queued off the main thread? |
| 4 | Immovable flag for blocks (pistons, fluids, physics) and "not replaceable" (Depleted Vein over by fluids / placement). |
| 5 | Where per-chunk sidecar data can live (own file next to the chunk, or the chunk's own metadata) and whether a chunk-load event fires with the chunk loaded, in time to restore blocks. |
| 6 | Does V2 worldgen let us hook ore placement to write registry entries, or do we scan the finished chunk once (cost)? (WorldGen UNVERIFIED 1.) |
| 7 | Block hardness / Quality of the Depleted Vein high enough that no tool breaks it; creative / admin breaking should drop the entry. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Mined veins on the shared zone islands grow back (replaces Zone-4-5 "no regrow" for zone islands only)? | [yes] |
| 2 | Regrow even when a player stands nearby (anti-lock), or keep the draft's "only when nobody is within 32 blocks"? | [regrow nearby too, row `ore.regrowNoPlayer` 0] |
| 3 | The small pockets (Z3 Mithril ~4,600, Z5 Drakonite ~4,400): enlarge them (Mithril veins 0.4 -> 0.8) or keep them small with a 900 s timer? | [900 s timer now; enlarge Mithril if the server is busy] |
| 4 | Do timers run while the server is off? | [yes, wall-clock] |
| 5 | Ore inside a player's claimed plot or built-up area: regrow or not? | [regrow; claim rules are separate] |
| 6 | Ember from 21 to 7 ore / cell (Zone 4) and 3.5 (Zone 5); also lower Amberite (11 / cell)? | [Ember yes; Amberite left alone] |
| 7 | Add the optional vein fatigue (slower swing after many ore from one cell) or no caps at all? | [no caps, row exists] |
| 8 | A private mine in profile worlds (renewable) later, or Pocket Shards only? | [shards only] |
