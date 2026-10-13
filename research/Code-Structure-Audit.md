# Code structure + lag audit (before the merge)

Skyy 2026-10-13: "During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working
together in the smoothest easiest lag free way possible" (docs/answered/project.md). Read-only audit; feeds research/Architecture-Spec.md.

**Status:** complete 2026-10-13 (part 1 pack-wide + part 2 all six groups).

## Part 1 - pack-wide findings

### 1. A global lock in every bridge call (biggest cheap win, effort S)
- The shared `bridge()` helper runs `synchronized(java.lang.System.class)` and then `System.getProperties().get("skyy.bridge")` (a
  synchronized Hashtable) on EVERY call. It is copied into 25 of the 31 jars (source: the `tools/skyycfg.py` kit snippet + older patches).
- `pkey()` (profile key lookup through `profile:fn:key`) adds a UUID.toString() + string concat per call; used by Skills, Classes,
  Islands, Exploration, Trees, Accessories, Pets.
- Effect: every per-hit, per-tick or per-pickup bridge read from every world thread and the scheduler queues on one JVM-wide monitor
  that the engine and the JDK also lock.
- **Fix now:** cache the map once in a `static volatile` field (double-checked); never lock on System.class after that. **Fix in Core:**
  one Bridge class with typed handles resolved once.

### 2. Join-time work on the world thread
- ~24 "Task took 34-112 ms" WARNs (logs 2026-10-10/11), almost all in the burst after a join / world switch: GearStampTask 34 ms,
  WdRepairTask 36 ms, the Armory pack / Mana checks, Merchants' old-merchant cleanup, plus anonymous CompletableFuture tasks 63-112 ms.
- PlayerReadyEvent fires on EVERY world switch (/hub, /island, /zone): Gear 7 handlers, Menu 12, Classes 4, Islands 4, Essentials 3,
  Hud 2, Sacks 2 - all paid again each switch.
- **Fix:** run asset-only checks once at start; spread join work over a few ticks; on a world switch only redo world-specific work.

### 3. ~32 separate periodic timers (mostly every 1-2 s)
- Hud, Sacks (4), Coins, Collections, Bank, Skills, Trees, Vault, Merchants, Pets, Wardrobe, Essentials (3), Menu (2), Classes,
  Exploration, Fishing, Party, Islands, Accessories, Guilds, Bazaar, Auctions, Mobs, Profiles. Usual pattern: loop online players ->
  `world.execute` per player. At 50 players that is roughly 1,000+ world-thread hops per second just for polling (UNVERIFIED per timer).
- **Fix:** one SkyyCore ticker (one heartbeat, one pass per world, one `world.execute` per world) with period divisors; event-driven
  where possible (inventory change, XP gain, join).

### 4. Other
- SkyyProfiles' DATA cache never drops an entry (memory grows with every unique player).
- Config kit (`Cfg*`) copied into 27 jars; `CfgSaveTask` in Skills, Accessories, Menu, Exploration.

## What goes into SkyyCore (merge phase 1)
Bridge registry with typed handles; one ticker + a per-world join dispatcher; one save + profile-data service (atomic write, journal,
off the world thread, dirty-flag batching); one config kit; one UI page base (Sky* runtime + HubBar). Pilot adopters drop their own
timers. smoke_test / harnesses should flag "Task took" WARNs for com.skyy.* as a regression gate.

## Quick wins before the merge (all small)
1. Bridge map in a static volatile field, no System.class lock - fix the `tools/skyycfg.py` snippet once, every rebuilt mod picks it up.
2. Move join-time asset checks (GearStampTask, WdRepairTask, Armory pack / Mana checks, Merchants cleanup) out of the join tick.
3. On PlayerReadyEvent, skip full re-init unless the world actually changed.

## Part 2 - per-mod findings (all six groups, 2026-10-13)

Severity 1-5 (5 = worst). "World thread" = blocks the game for every player in that world.

### Top findings, worst first
| # | Mod | Where | Problem | Fix | Effort | Sev |
|---|---|---|---|---|---|---|
| 1 | Coins | CoinStore.setK / saveK | EVERY balance change writes a whole file inside one global lock on the caller's (world) thread; 5x20 ms sleep retries | write-behind: memory authoritative, one writer thread flushes dirty keys every 1-2 s + on quit / shutdown; journal for transfers | M | 4 |
| 2 | Skills | SkillTop.all (leaderboard) | on cache miss reads EVERY player file on the world thread (100-500 ms at 1000 profiles), grows with total profiles | in-memory leaderboard index, built off the world thread | M | 4 |
| 3 | Merchants (+Exploration, Islands) | MerchReg.moveRetry / ExpIO.moveRetry / IslandStore.write0 | tmp write + move with Thread.sleep(20) retries ON the world thread = the logged 82 ms stall (Avast) | one shared writer thread ("SkyyIO"), no sleeps on world threads | M | 4 |
| 4 | Hud | Widgets.text Gclock / Day | reads a world store resource OFF the world thread (thread-safety risk) | cache world time per world from one world hop per second | M | 4 |
| 5 | Gear | GearTick + damage path | the same armor / weapon stacks re-walked 8-10x per player per second, and totals rebuilt up to 3x per hit | one per-player stats snapshot, invalidated on inventory / level / config change | M | 3 |
| 6 | Gear | GearOpened.load / take / kick | whole chest-record file read inside a class lock that world threads wait on; file never compacted | read outside the lock; compact on load | S | 3 |
| 7 | Gear | join stamp scan | join scan rewrites stacks, which re-triggers itself; 34 ms per join | suppress self-triggered scans; cap slots per tick; stagger join scans | M | 3 |
| 8 | Hud | TickTask on the shared scheduler | all players x every widget every second on the ENGINE's one scheduler thread; calls Skills / Classes functions off the world thread | own executor; skip hidden widgets / unchanged players; publish combat state as plain values | M | 3 |
| 9 | Menu (+kit, Skills, Trees, Classes) | atomic writes with fsync on HytaleServer.SCHEDULED_EXECUTOR | one slow disk write stalls every mod's timers and hops | one shared single-thread writer ("SkyyIO") | M | 3 |
| 10 | Menu | GrantTask.grantNow | file checks under a class lock on the world thread ~4 s after join | file checks on the scheduler, hop only to give the item | S | 3 |
| 11 | Skills | PlacedStore | 400k boxed Longs per world; whole set copied under a lock world threads need | primitive long set + journal, copy / write off-lock | M | 3 |
| 12 | Fishing | FishTick per player per tick | allocation + ~8 component lookups per player per tick; BSON parse 30x/s while a rod is held | early-out unless a rod is held; cache rig per stack | M | 3 |
| 13 | Bazaar | BzTick every 10 s | rewrites market.properties + re-quotes every product forever, under the Market lock | dirty only on change; publish only changed ids | S | 3 |
| 14 | Guilds | GuildTick every 5 s | fsync-writes every active guild inside the one GuildStore lock; O(members^2) info strings | snapshot under lock, write outside; flush XP every 60 s | M | 3 |
| 15 | Auctions | AhTick every 10 s | 50 players x full listing scan (BSON) on the shared scheduler | owed-count index updated on commit | M | 3 |
| 16 | Bank | payAll | whole payout holds the BankStore lock that world-thread deposits / withdraws need (1000 accounts = 2-5 s) | lock per file | S | 3 |
| 17 | Menu | bridge keySet scans | Settings / Server Setup pages scan the WHOLE bridge (thousands of keys) per page | mods publish to a small index | M | 2 |
| 18 | Exploration | ExpTick + LgCore.second | ~6 bridge calls + 8 string concats per player per second; one global ExpStore monitor; site loops repeated per player | event-driven publishing; per-world site sweep | M | 2 |
| 19 | Armory | TravTick | grapple / soul per-tick work for idle players | gate on "Armory item in hand" | M | 2 |
| 3b | Accessories | AccLanternHide.tick | per viewer, EVERY tick, walks the whole visible-entity set (150k-450k archetype lookups/s at 50 players) | keep a per-world set of lantern helper refs and remove only those | M | 4 |
| 9b | Sacks | SweepTask (2 s) + CraftTick (300 ms) + ProcTick (1 s) | world hops for EVERY player even idle (~240 hops/s), ~6 full inventory scans per sweep | event / dirty-flag driven; hop only players with an open window or queue | M-L | 3 |
| 9c | Sacks | SackPool.saveSoon / saveNow | a full pool file fsync per call (up to ~16/s while crafting) on the shared scheduler | debounce 1 s, own writer thread, save only dirty keys | S | 3 |
| 9d | Wardrobe | WdRepairTask + WdTx + WdJournal | cold disk load (the logged 36 ms) and 3 fsyncs per Equip on the world thread; one global journal lock across worlds | pre-warm off-thread; journal sync then async data write; lock per profile | S-M | 3 |
| 9e | Sacks + Accessories | KnowSync / AccKnow | re-split the recipes CSV into a new set every 1-2 s per player | cache by coll:epoch | S | 3 |
| 20 | SkyyUiProbe | packet tap | adapter on EVERY outbound packet of every player | keep probes out of the production pack | S | 2 |

### Pack-wide patterns (confirmed by all sub-audits)
- **`synchronized(System.class)` in bridge()** - Gear, Exploration, Mobs, Merchants, Cooking, Coins, Bank, Bazaar, Auctions, Party, Guilds, Profiles, Essentials (x2), Armory, Ranks, Menu ...; Islands, Fishing and Hud already use the lock-free form - copy that.
- **5+ different atomic-write implementations** with different safety (only some fsync), most with sleep retries; **5 debounced-save systems**; **4 coin-helper conventions**; pkey / busy / epoch helpers copied everywhere; the config kit compiled into ~27 jars.
- **Shared scheduler overload:** ~32 polling timers + file writes all on the engine's ONE scheduler thread.
- **Polling that should be events:** Coins death detection (1 s per player), Menu GivenTick, Guilds XP poll, Classes / Exploration profile checks.
- Data safety is mostly good (tmp + move, re-queued failed saves); crash-loss windows 0.5-10 s. Trees: a save can be lost if the player quits mid-save (evict only after the save succeeds).

### Data-safety fixes found (do with the quick wins)
- **Collections writes counts and the reward-paid markers WITHOUT fsync** - after a power loss a stale "paid" marker could pay a reward twice. Add fsync + atomic move like the other mods. (sev 3)
- **Sacks pool vs inventory crash window** - a crash between a refill / sweep and the next 10 s pool save can dupe or lose items; saveSoon after each refill / sweep batch (debounced 1 s). (sev 3)

### Plan
1. **Quick-wins round (before the merge, after the 0.7 port):** lock-free bridge in the `tools/skyycfg.py` snippet and every hand-written copy; Coins write-behind; SkillTop index; no sleep-retries on world threads (one SkyyIO writer); Hud world-time + own executor; Gear stats snapshot; Accessories lantern-hide; Sacks / Wardrobe hops + saves; Collections fsync + Sacks crash window; Bazaar / Guilds / Bank lock fixes; UiProbe out of the pack once Skyy's kit test is done.
2. **Merge phase 1 = SkyyCore:** typed Bridge, one Ticker + per-world join dispatcher, SkyyIO writer + save service, config kit, UI page base, coin / profile helpers - every merged mod drops its own copies.
3. **Regression gate:** smoke_test flags "Task took" WARNs from com.skyy.* classes.
