# Code structure + lag audit (before the merge)

Skyy 2026-10-13: "During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working
together in the smoothest easiest lag free way possible" (docs/answered/project.md). Read-only audit; feeds research/Architecture-Spec.md.

**Status:** part 1 (pack-wide measurements, below) done 2026-10-13; part 2 (per-mod ranked findings) in progress - six read-only
sub-audits, appended here when they report.

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
