# Zone Reset - `/zone <n> reset` + `/zone <n> reset undo` (SkyyWorldGen 0.7.10 spec)

Written 2026-10-23 by a research agent (no code changed). Where this goes: build round `wg0710` (SkyyWorldGen 0.7.10, full round).
Answers / decisions about it go to `docs/answered/world.md`; open choices are in section 12 (main session asks Skyy).

Skyy (they/them) 2026-10-23, word for word:
- "ive explored most of zone 1 already. make a new zone 1 with the new structures. (and make sure better maps works in the zones."
- "dont worry about generating from the same seed or anything. id prefer a fresh regenerate every time. (maybe add a command i can do in
  game. like /zone 1 reset   which would regenerate that zone on a new seed, so every chunk is new and new structures will generate on it.)"
- "but if you can, also add an undo incase someone does it by accident."

BetterMap part of the first quote: already done. `mods/BetterMap/config.json` allowedWorlds lists skywynn_zones2 (+ zones3-5), kept
by `deploy_set sync_bettermap_worlds`. The zone map is drawn from the real chunks (WgZ2Gen.getGenerator = `ChunkWorldMap`), so
regenerated chunks show up on the map. (Not yet checked: whether the CLIENT keeps showing cached old tiles until rejoin. See probe P7.)

## 1. What the world looks like today (measured on a read-only copy, 2026-10-23)

World `NewBetaTest/universe/worlds/skywynn_zones2`, seed 20261014, generator `SkyWynnZones2`, 22 region files, 83 MB, 7442 stored chunks.
The island layout is in `mods/Skyy_SkyyWorldGen/zone2_layout_20261014.bin` (gzip DataOutputStream, LAY_MAGIC 1515929655, LAY_VER **2**,
23 entries = 5 main islands + 18 islet slots; format = `WgZ2Isles.saveLayout` in `SkyyWorldGen/build_skyyworldgen_0.7.9.py`).

| Zone | main island centre / R | land bounds (blocks, main + islets) | stored chunks | region files (all single-zone) |
|---|---|---|---|---|
| 1 | -746, 526 / 1110 | x -1854..410, z -485..1197 (6 islets) | 7001 (95 %) | -2.-2 -2.-1 -2.0 -2.1 -1.-2 -1.-1 -1.0 -1.1 0.-2 0.-1 0.0 0.1 1.-1 1.0 (14 files, ~78 MB) |
| 2 | -4224, 384 / 1220 | x -5200..-3544, z -632..1328 | 49 | -5.0 |
| 3 | 1280, 4800 / 1330 | x 276..2176, z 3784..6238 | 196 | 0.5 0.6 1.4 1.5 |
| 4 | 3712, -2560 / 1440 | x 2414..4312, z -3408..-1944 | 147 | 2.-4 3.-3 |
| 5 | -1792, 3456 / 900 | x -2168..-1384, z 3128..3840 | 49 | -2.3 |

Zones 2-5 only have their 7 x 7 landing pre-load (WgZ2Pre) stored. Zone 1 chunks go out as far as 800 blocks past its land (void chunks
loaded by view distance). No region file holds two zones, but the design still works chunk by chunk (section 4), so this never matters.
Zone 1 landing = server spawn: `zones.spawnPoint=-912.5 124 691.5 109` in `mods/Skyy_SkyyWorldGen/config.properties`.

## 2. The region file format (proven: HytaleServer.jar bytecode + every live file parsed)

`com.hypixel.hytale.storage.IndexedStorageFile` ("HytaleIndexedStorage", VERSION 1), one file per 32 x 32 chunks, name
`<rx>.<rz>.region.bin` (`IndexedStorageChunkStorageProvider.toFileName`), rx = chunkX >> 5, chunk = 32 blocks (`ChunkUtil.BITS 5`).
- Header 32 bytes: magic (20) + version + blobCount (1024) + segmentSize (4096), big-endian ints.
- Index: blobCount x int at offset 32 = the first segment of that chunk's blob, 0 = no chunk. Blob index = `ChunkUtil.indexColumn(x & 31,
  z & 31)` = `(z & 31) << 5 | (x & 31)`.
- Segments after the index: blob header (src length + compressed length) + zstd data (`DEFAULT_COMPRESSION_LEVEL 3`).
- `removeBlob(i)` only writes 0 into the index entry. The used-segment bitmap is rebuilt from the index when the file opens, so freed
  segments get reused and the file never shrinks. Dropping a chunk offline = zero 4 bytes (a Python one-liner, used by the harness).
- Engine API on the file (proven): `open(Path, OpenOption...)`, `keys()`, `readBlob(int) -> ByteBuffer`, `writeBlob(int, ByteBuffer)`,
  `removeBlob(int)`, `getBlobIndex(int)`, `force(boolean)`, `close()`.

## 3. The design

### 3.1 A new seed per zone ("generation" g)
- New file `mods/Skyy_SkyyWorldGen/zone2_seeds_<worldSeed>.properties`: `zone.<k>.gen=<g>` (0 = the world seed, as today) and
  `zone.<k>.seed=<int>`, written atomically (tmp + ATOMIC_MOVE), a history line per change. A missing file means every zone is on gen 0,
  so 0.7.10 changes nothing until someone runs a reset.
- `seed_k(g) = g == 0 ? worldSeed : mix(worldSeed, k, g)` (a 32-bit hash, never 0 and never the world seed).
- Each zone's island entries (main island + islets) for gen g > 0 go in their own immutable file:
  `zone2_layout_<worldSeed>_z<k>_g<g>.bin` (the same LAY_VER 2 format, holding only that zone's entries). The live layout =
  the gen-0 file with zone k's entries replaced by its current gen file. Older gen files stay as long as a backup needs them
  (section 6), so undo never has to pick again.
- **Generation (WgZ2Gen.generateWith):** find the chunk's OWNER zone (section 4). If the owner's gen > 0, call
  `super.generate(seed_k, ...)` and use seed_k in WgZ2Fn (veins, mirrors, crop swaps, rims, rivers, waterfalls). Every other chunk is
  generated exactly as in 0.7.9 (byte-identical: harness check H1).
- **The pick for a new gen** (off the world thread, the same `WgZ2Pick` path): run the 0.7 island pick on seed_k for zone k only, with two
  extra rules: (a) the new centre must sit inside zone k's slot (at most `zones.resetSlot`, default 600 blocks, from the gen-0 centre);
  (b) the new land must keep the GAP rule (at least `zone_gap` 900 blocks from every other zone's current land). Then check the area is at
  least 70 % of gen 0's. If any of this fails, try g+1, up to 20 tries. If all 20 fail: "no new seed fits zone k - nothing changed".
  Probe P1 checks how often a pick fits.
- Islet counts use the CURRENT Server Setup values (a reset is the one time `zones.islets1` / `zones.islets25` take effect on an
  existing world).

### 3.2 `/zone <n> reset` (admin)
Admin only, like every /zone command: `requirePermission("skyyworldgen.admin")` + `setPermissionGroups(new String[0])`
(COMMAND RULES; lint perm_group_leaks). Usage variants on the existing `/zone <zone>` command (ZoneCmd.addUsageVariant):

| Typed | What it does |
|---|---|
| `/zone 1 reset` | dry run: picks the new seed (async) and shows the plan: zone, old gen -> new gen, chunks stored / loaded, players inside, new landing, backup size, how many backups are kept. Nothing is changed. The plan is cached for 120 s. |
| `/zone 1 reset confirm` | does it (section 3.3). Refused if the plan is older than 120 s or the world changed (stored-chunk count). |
| `/zone 1 reset undo` | dry run of the undo: which backup (stamp, gen), what goes back, what is lost (section 6.3). |
| `/zone 1 reset undo confirm` | the undo. |
| `/zone resets` (or `/zone 1 reset list`) | the kept backups per zone: stamp, gen, size, who ran it. |

Only one reset or undo runs at a time on the server. While one runs, `/zone <n>` travel into that zone is refused ("Zone n is being
rebuilt").

### 3.3 The reset steps (live, path a) - all on skywynn_zones2's world thread unless marked async
1. **Players out.** Everyone in zone k (owner zone of their chunk) gets moved through the bridge: `island:fn:gohome` (their island), else
   `island:fn:hub`, else the default world spawn. Zone k's `/zone` travel and the login routing (WgSpawnHome) send nobody into zone k
   until step 9. Wait until no player is in zone k (max 30 s, else stop and undo nothing - nothing has changed yet).
2. **Let pending saves finish.** Poll `ChunkSavingSystems$Data.getQueueDepth() == 0` and `getInFlightSaveCount() == 0` (max 30 s),
   then `World.lockSaving()`. This is vanilla's own `/worldgen reload --clear` path (proven, `WorldGenReloadCommand.clearChunks`).
   Vanilla also calls `clearSaveQueue()` there, but that empties the WHOLE world's queue, so we only call it after the queue is empty.
3. **Backup (async on the backup thread, saving locked).** Every stored chunk of zone k (`IChunkSaver.getIndexes()` filtered by owner)
   is copied blob for blob with `IndexedStorageFile.readBlob` into `mods/Skyy_SkyyWorldGen/zone-resets/skywynn_zones2/z<k>-<stamp>/
   chunks/<rx>.<rz>.region.bin` (opened with `IndexedStorageFile.open`, same format). The live region files come from
   `ChunkStore.getStorageData()` -> `IndexedStorageCache.getOrTryOpen(rx, rz, false)` (probe P2). Then the tied data (3.4) goes into
   the same folder, plus `manifest.properties` (zone, old gen + seed, new gen + seed, old landing, chunk list + blob sha1s, who / when).
   The backup is read back and the sha1s compared. If anything fails: unlock saving, change nothing, say why.
4. **Write the new gen.** Save `zone2_layout_<seed>_z<k>_g<new>.bin`, then `zone2_seeds_<seed>.properties` (atomic). From now on the
   generator builds zone k from the new seed.
5. **Drop stored chunks.** `IChunkSaver.removeHolder(x, z)` for every stored zone-k chunk (proven: the vanilla clear path). Then
   `IChunkSaver.flush()`.
6. **Regenerate loaded chunks.** For every LOADED zone-k chunk (`ChunkGrid.getChunkIndexes()` filtered by owner):
   `ChunkStore.getChunkReferenceAsync(index, 9)`, the flags vanilla's `/chunk regenerate` and `/worldgen reload --clear` use (proven
   call; what the bits mean, and whether it fires ChunkPreLoadProcessEvent with `isNewlyGenerated()` true, is probe P3).
   Fallback if P3 fails: unload them (`ChunkGrid.remove(ref, RemoveReason.UNLOAD)`, probe P4) so they generate fresh on the next visit.
7. `World.unlockSaving()`.
8. **New landing (zone 1 = server spawn).** From the new pick's land point (lx, lz): load that chunk async (it generates on the new seed),
   find the highest solid ground block in the 3 x 3 around it, landing = ground + 2. Then `WgCmds.cfgSet("zones.spawnPoint", ...)` for
   zone 1 (through the config kit: a History snapshot + a change-log line with Undo). Zones 2-5 keep using the pure landing from the
   layout (`landingOf`). The WgZ2Pre landing pre-load runs once for zone k.
9. Zone k opens again. The admin gets a summary (chunks backed up / dropped / regenerated, new landing, backup stamp, "restart soon to
   finish the pack-mod tidy" when step 3.4-B is queued). One INFO log line covers all of it.

Path b (the fallback if P2-P4 fail; same code): `/zone 1 reset confirm` writes `zone-resets/pending.properties` and says "restart the
server to finish". Then in SkyyWorldGen setup(), if skywynn_zones2 is not loaded yet (probe P5), steps 3-5 run on the files directly
(`IndexedStorageFile.open` + readBlob / removeBlob), no player can be inside, and step 8 runs when the world loads.

### 3.4 Data tied to the zone's land
Only rows or entries whose position is in zone k (owner rule, section 4) are touched. The old rows go into the backup first.

A - ours, done live through `skyy.bridge` functions (java.lang types only; a missing mod means that step is skipped and the summary says so):
| Data | File | What the reset does |
|---|---|---|
| SkyyZones regrowing blocks | `Skyy_SkyyZones/regen/skywynn_zones2.snap` + `.journal` (`D x y z ...` / `R x y z`) | new `zones:fn:dropBox` (world, x0, z0, x1, z1): forget the waiting blocks there WITHOUT putting them back, and journal an `R` line for each. Must run before step 6, or a regrow would write an old ore into the new terrain. |
| SkyyZones regions | `Skyy_SkyyZones/regions.properties` | kept (admin regions are boxes, not land). The summary lists every region in zone k: "check region <id>, the land under it is new". |
| SkyyExploration loot chests | `Skyy_SkyyExploration/chests/skywynn-zones2-4779f1c7.log` (`A x y z table by` / `R x y z`) | new `explore:fn:dropBox`: an `R` line for each live record in the box (in the journal's own format). |
| SkyyExploration luggage | `Skyy_SkyyExploration/luggage/skywynn-zones2-4779f1c7.tsv` (16 sites, all in Zone 1 today) | the same function drops the sites in the box (the blocks are gone with the chunks). |
| SkyyExploration player progress | `players/<pkey>/chunks/<wf>.bin`, `zones.txt`, `chests.txt` | KEPT. Each source pays once per profile; resetting it would pay exploration XP again (section 12, Q3). |
| SkyyWorldGen | `zone2_layout_*`, `zone2_seeds_*`, `config.properties` zones.spawnPoint | as in 3.1 / 3.3 step 8. Ore veins / mirrors / crop swaps have no file: they are part of the chunk and come back new. Landing pre-load: no marker file (it skips stored chunks via getIndexes), so it reruns by itself. |
| SkyyMobs | config only | nothing: mobs live in the chunks and go with them. |

B - pack mods and vanilla resources. They keep this in memory and write it back, so editing it live does not stick. Done in
SkyyWorldGen setup() on the NEXT start, before skywynn_zones2 loads (probe P5), from `zone-resets/tidy.properties`:
| Data | File (world folder) | Tidy |
|---|---|---|
| StructureV2 + DungeonBosses | `structurev2-spawns.json` (version 2: spawns / pending / latentBossIslands / defeatedBossIslands / defeatedIceArenas / bossIslandArenaBounds; entries have x / z or anchorX / anchorZ or minX..maxZ). Not written for zones2 yet. DungeonBosses has no file of its own (boss islands are in this one). | drop every entry whose position / bounds centre is in zone k: new placements in zone k are no longer blocked by the old maxInstancesPerWorld counts (boss_island 20, frozen_tower 14, ice_boss 12) and old latent boss islands no longer appear over the new land. |
| RiverBridges | `riverbridges-spawns.json` (`bridges[]` x / y / z) | drop entries in zone k. |
| BetterMap fog | `mods/BetterMap/Data/skywynn_zones2/<uuid>.bin` + `cave-<uuid>.bin` (int version, int count, count x long `(x << 32) or (z & 0xffffffff)` in 16-block map cells) | drop cells in zone k, so the new land starts under fog again (default on, section 12 Q2). BetterMap reads these only when a player joins, so the start is a safe time. |
| Vanilla map markers | `resources/BlockMapMarkers.json` (`"x,y,z"` keys; today 1: the Forgotten Temple portal at -928,112,710) | drop markers in zone k (the block is gone; a new one adds its own marker). |
| Vanilla spawn suppression | `resources/SpawnSuppressionController.json` (today 1: Spawn_Camp at -739,112,525) | drop entries in zone k. |
| Kept | TriggerVolumeData (player perk spheres), SharedUserMapMarkers (players' own markers), WorldEventStorage (world-wide), `snapshots/` (empty), `instance.bson`, `config.json` | untouched. |

Between a live reset and the next start, StructureV2 still counts the old zone-k structures (only the max-per-world types) and could
paste an old PENDING structure into the new land. That is harmless but untidy, and the summary asks for a restart.

## 4. Which chunks are a zone's (only those, never another zone's land)
Owner of a chunk = the zone whose land is NEAREST: the distance from the chunk's 32 x 32 square to each layout entry's bounding box
(main island + islets, the zone's CURRENT gen plus every gen still in a backup). This is a Voronoi split; zones are at least 900 blocks
apart (GAP rule, also required of every new pick), so far-out void chunks go to the nearest zone. On today's world this gives
Zone 1: 7001 chunks, Zone 2: 49, Zone 3: 196, Zone 4: 147, Zone 5: 49, and no chunk is close to two zones. Zone 1's farthest void chunk is
800 blocks out; the nearest other land (Zone 5) is 1931 blocks from Zone 1's land. The owner test is ONE static method
(`WgZ2Isles.ownerOf(L, cx, cz)`), used by the generator, the reset, the tidy and the harness. Its unit tests include chunks on the line
between two zones.

## 5. Engine APIs

Proven in HytaleServer.jar bytecode (2026-10-23 game build):
- `IChunkSaver`: `getIndexes()`, `removeHolder(int, int)`, `saveHolder(int, int, Holder)`, `flush()`; `IChunkLoader`: `loadHolder`,
  `getIndexes`; `ChunkStore.getSaver()`, `getStorageData()`.
- `World.lockSaving()` / `unlockSaving()` / `isSavingLocked()`, `World.execute(Runnable)`; `ChunkSavingSystems$Data.clearSaveQueue()`,
  `getQueueDepth()`, `getInFlightSaveCount()`, `waitForSavingChunks()`.
- `ChunkGrid.getChunkIndexes()`, `getChunkReferenceAsync(long, int)` with flags 9 (vanilla /chunk regenerate + /worldgen reload --clear),
  `remove(Ref, RemoveReason)`.
- `IndexedStorageFile` (section 2) and `IndexedStorageChunkStorageProvider$IndexedStorageCache.getOrTryOpen(int, int, boolean)` /
  `getOrCreate`.
- `WorldGenChunksClearedEvent(World)`: vanilla fires it after a full clear. No pack mod listens to it (StructureV2, DungeonBosses,
  RiverBridges, BetterMap checked), so it does not help us.
- StructureV2 and RiverBridges place on `ChunkPreLoadProcessEvent` when `isNewlyGenerated()` is true. A chunk with no stored data is
  newly generated by definition, so new structures place on every dropped chunk the next time it loads.

Needs a probe (round step 0, `SkyyWorldGen/probe_zone_reset.py` in a bare JVM + the harness server run):
- **P1** the pick on other seeds: for each zone, the 20 salts' picks - fit rate, centre shift, area. If the vanilla zone mask turns out
  to be seed-independent, nearly every salt fits.
- **P1b** one `ChunkGenerator` instance generating with two seeds: the chunks differ, seed S is byte-identical before and after seed S'
  runs, and the extra memory per seed.
- **P2** `ChunkStore.getStorageData()` is an `IndexedStorageCache` for ChunkStorage Type "Hytale", and reading blobs with saving locked
  is safe.
- **P3** flags 9: the bits, a loaded chunk is replaced in place, players near it get the new blocks, and ChunkPreLoadProcessEvent
  isNewlyGenerated is true. Otherwise use P4.
- **P4** `ChunkGrid.remove(ref, UNLOAD)` on a chunk nobody is near.
- **P5** load order: our setup() runs before Universe loads skywynn_zones2 (path b and the 3.4-B tidy depend on it). Otherwise run the
  tidy in the world's add / pre-load event, before its first chunk loads.
- **P6** `/zone <zone> reset [confirm|undo] [confirm]` as usage variants of 2 / 3 / 4 args next to `/zone <zone>`. Otherwise use
  `/zone reset <n> [confirm|undo [confirm]]` (subcommand).
- **P7** BetterMap / client map tiles redraw without a rejoin.

## 6. Backups + undo
### 6.1 What a backup holds
`mods/Skyy_SkyyWorldGen/zone-resets/skywynn_zones2/z<k>-<stamp>/`: `chunks/*.region.bin` (zone k's blobs only), `manifest.properties`,
`tied/` (the zone-k rows removed from each file in 3.4, with their source path), and `landing.txt` (the old zones.spawnPoint). Size:
Zone 1 today is about 78 MB of region data. A fresh zone is mostly the 7 x 7 pre-load (under 2 MB) until people explore it.
### 6.2 Keeping
New Server Setup row `zones.resetKeep` "Resets kept per zone (undo)", int, default 3, 1-5, live. After a successful reset the oldest
backups of that zone beyond the limit are deleted, and so are gen layout files that no backup needs any more. These are files the mod
made itself in its own folder. Undo works as a stack: each undo restores the newest kept backup and then removes it.
### 6.3 `/zone <n> reset undo confirm`
Same frame as 3.3 (players out, saves drained, lockSaving), then:
1. A safety backup of the CURRENT zone-k chunks (`z<k>-<stamp>-undo/`, counted in resetKeep, so an undo can be undone by a reset undo of
   that one).
2. `removeHolder` for every zone-k chunk stored now, then write the backup's blobs back with `IndexedStorageFile.writeBlob` on the live
   files (the cache's own instance, P2). Fallback: `IChunkSaver.saveHolder` from `IChunkLoader`-decoded holders.
3. Restore the seed + gen pointer (`zone2_seeds`), zones.spawnPoint (cfgSet, History + Undo line), and the 3.4-A rows (bridge
   `*:fn:restoreBox`). Queue the 3.4-B rows for the next start (re-insert StructureV2 / RiverBridges / markers entries, BetterMap cells).
4. Loaded zone-k chunks: unload / reload so they come from storage (P3 / P4).

**Undo limits (say these on the dry run):**
- Everything that happened in zone k after the reset is gone: builds, mined blocks, placed chests and their contents, mobs, dropped
  items, structures that spawned on the new land, SkyyZones regrow timers there.
- Players' inventories, coins, XP, quests and exploration progress are NOT rolled back. Loot taken from the new land stays. The restored
  old chests come back with the contents they had at reset time, so loot can exist twice. This is acceptable for an admin tool, but
  the dry run says so.
- Beds / respawn points players set on the new land point at old terrain again.
- Only the last `zones.resetKeep` resets per zone can be undone, newest first.
- Undo needs the same SkyyWorldGen layout format (LAY_VER 2). A later jar that changes it must migrate the backups or refuse undo.

## 7. What is lost on a reset (today's Zone 1)
- Every block change on Zone 1: Skyy's builds, mined ore, placed blocks, chest contents, crops, the 16 luggage sites, NPCs / pets left
  standing there. All of it is in the backup until the backup ages out.
- The Zone 1 landing moves (the server spawn). A bed / home point on Zone 1 may now be inside rock or over void. The respawn falls back
  to the HomeOrSpawnPoint rules (section 12 Q4).
- Admin SkyyZones regions in Zone 1 (none today) keep their boxes over new land.
- Kept: player inventories / progress, Zones 2-5 (byte-identical), every other world, StructureV2 settings.

## 8. Risks
| Risk | Guard |
|---|---|
| A wrong owner test deletes another zone's chunks | one tested `ownerOf`; the harness checks every non-zone-k chunk is byte-identical after reset AND after undo; the dry run prints the counts per zone |
| An old chunk is saved back after removeHolder | lockSaving + empty save queue first; loaded zone-k chunks regenerated / unloaded before unlockSaving |
| A crash mid-reset | backup before any change; a `zone-resets/inprogress.properties` journal; on start, an unfinished reset is finished, or put back from its backup (whichever step it reached) |
| The new pick never fits (P1) | 20 salts, then refuse with nothing changed |
| StructureV2's world-thread prefab freeze (0.7.9 fix) | generate stays off the world thread; getUniquePrefabs keeps the 0.7.9 safe path for every seed |
| Memory of a second vanilla seed | P1b measures it; only zones with gen > 0 load it |
| A regrow writes old ore into the new land | zones:fn:dropBox before step 6 |
| Pack-mod state stale until restart | the summary asks for a restart; the tidy runs before the world loads |
| Disk use | resetKeep (default 3) x the zone's stored size |

## 9. Server Setup rows (World Gen > Zones, via tools/skyycfg.py)
- `zones.resetKeep` (int, 3, 1-5, live): "Resets kept per zone (undo)".
- `zones.resetSlot` (int, 600, 200-900, step 50, blocks, live): "How far a reset island may move".
- `zones.resetMap` (bool, true, live): "Reset clears the BetterMap fog".
- (action) `zones.resetList`: "Zone resets kept", shows the `/zone resets` text.

## 10. Build spec - round wg0710 (FULL round: saved data, several mods, a new system)
Mods: SkyyWorldGen 0.7.10 (`tools/worldgen_0_7_10_patch.py` from the 0.7.9 generated script) + SkyyZones 0.2.1 (`zones:fn:dropBox`
/ `restoreBox`) + SkyyExploration 0.3.4 (`explore:fn:dropBox` / `restoreBox` for chests + luggage). These three pin and roll back
TOGETHER (WorldGen without the other two skips 3.4-A with a WARN). ROLLBACK floor: once any zone has gen > 0, rolling WorldGen back
below 0.7.10 regenerates that zone's unexplored chunks on the OLD seed next to new-seed chunks (seams). Before a rollback run
`/zone <n> reset undo` until every zone is gen 0, or accept the seams. Put this in deploy_set.py as a FLOOR comment.

Steps: P1-P7 probes -> WgZ2Isles.ownerOf + per-gen layout files + seeds file -> generator per-zone seed -> pick with slot + gap rules ->
reset / undo engine (3.3, 6.3) -> startup tidy (3.4-B) + in-progress recovery -> the commands -> Server Setup rows -> bridge functions in
Zones / Exploration.

Harness `SkyyWorldGen/test_skyyworldgen_0.7.10.py` (+ the offline scratch parts of `tools/smoke_test.py`):
- H1 gen 0 for every zone = 0.7.9 output byte-identical (sample chunks of all 5 zones).
- H2 ownerOf: today's counts (7001 / 49 / 196 / 147 / 49), border chunks, nothing owned twice.
- H3 a gen-1 pick for each zone: inside the slot, GAP kept, area >= 70 %; seed file + gen layout round-trip.
- H4 on a scratch COPY of NewBetaTest (offline, the file path b code): reset zone 1 -> only zone-1 index entries are gone, every other
  chunk's blob is byte-identical, the backup sha1s match, the 3.4 files keep every non-zone-1 row byte-identical.
- H5 undo on the same copy -> every region file's chunk set and blobs byte-identical to the original (the index of a re-written blob may
  point at a different segment: compare blobs, not file bytes), tied files byte-identical, seeds file back to gen 0.
- H6 resetKeep: four resets keep three backups; the gen files no backup needs are removed.
- H7 scratch server boot (smoke pattern, game closed): a reset scratch world loads, zone-1 landing chunks regenerate on the new seed
  (stored chunks reappear around the new landing), StructureV2 logs placements in zone 1 if any fall in the pre-load (or run with
  `zones.pregenRadius` 8 on the copy), no SEVERE from our mods.
- H8 the live path in that scratch server: run `/zone 1 reset confirm` from the console (no players), then check H4's invariants on the
  stopped server's files.
- lint 0 fails; crosscheck --jar --baseline; COMMAND RULES (every new variant admin-only).

In-game test steps for Skyy (after deploy):
1. `/zone 1 reset`: read the plan (chunks, new landing, backups kept: 0 of 3).
2. `/zone 1 reset confirm`: you are sent to your island; the summary says done.
3. `/zone 1`: new land at the new landing, new trees / ores / structures; `/spawn` goes there too.
4. Open the map (BetterMap): Zone 1 is under fog again and draws the new land as you walk.
5. Walk around 5 minutes: StructureV2 structures (towers, goblin bases, mineshafts) appear on new chunks.
6. Restart the server once; the log shows "zone reset tidy: zone 1 ..." with the counts.
7. `/zone 1 reset undo`, then `/zone 1 reset undo confirm`: the old Zone 1 (your builds) is back and the landing is the old one.
8. Zones 2-5 look unchanged throughout.

## 11. Offline one-shot (not built - superseded)
Before the change of plan an offline script `tools/reset_zone_land.py` was scoped (drop zone 1's 14 region files, reset the tied data,
backup to `backups/zone-reset-<stamp>/`). It is not needed now: the same file logic is path b inside the mod. None of it was written.

## 12. Choices for Skyy (defaults in brackets; the main session asks)
- Q1 Where players inside the zone go on a reset: [their island (`island:fn:gohome`), else /hub].
- Q2 Reset clears the BetterMap fog for that zone: [yes, so the new land is explored again].
- Q3 Exploration rewards (zones / chunks / chests) pay again on the new land: [no - each source pays once per profile].
- Q4 Players whose bed / home is in the reset zone: [respawn falls back to the server spawn = the new landing].
- Q5 Resets kept per zone for undo: [3].
