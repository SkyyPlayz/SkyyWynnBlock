# GlymeraWorker 11.0.0 - what it teaches the shard totem poles (LEARN only)

Mod: GlymeraCraft, **All Rights Reserved** (CurseForge page not re-read here; `research/Farming-Mods-Survey.md` section 4 notes the sister mod GlymeraFarmer also says "free for personal and server use"). Jar read in scratch (manifest, 3 asset JSONs, byte-code names / constants / numbers); **no code copied, nothing packed, nothing shipped.**
Signposts: `INDEX.md`; sister study `research/Farming-Mods-Survey.md` section 4 (GlymeraFarmer - same author, same design, same helper class W7; read that first); totem rules `research/Gathering-Shards-Spec.md` 9.2 / 9.3 / 9.3.1 / 10.6; answers `docs/answered/skills.md`, `docs/answered/world.md` (2026-10-23 GLYMERAWORKER line).

## 1. Decisions followed first (nothing here re-decides them)
- Skyy 2026-10-23: "this one could be helpful for figuring out the mechanics of the totem poles in the shards" -> LEARN only, not packed (an auto-miner NPC duplicates our shard totems; no-duplicates rule).
- Skyy 2026-10-11 SHARDS 3 + 2026-10-16 TOTEM WORKERS: totems work "like the minions in skyblock" - right-click = info / upgrade / augments, pick up to move; worker starts at 12 items / min and scales; Fortune; augments crafted at the totem workbench (`docs/answered/skills.md`).
- Skyy 2026-10-18 balance Q23 and 2026-10-21 IDLE PAY: late game "100% idle", 20-100 % while away, 3 days -> production stays **lazy offline maths** (spec 9.2). Workers are looks, not the engine (spec 10.6).
- Skyy 2026-10-16 MORETOTEMS REMOVED + PROJECT-RULES 2: no copied code / assets from others; no duplicate systems.
- Nothing is switched off "for other players" during dev.

## 2. What the mod is (facts)
- Files: `manifest.json` (`IncludesAssetPack: true`, Main `de.glymera.worker.GlymeraWorker`), `Server/Item/Items/Furniture/Worker/Furniture_Worker_Chest.json` (a crude-chest copy: `ItemContainerBlock` capacity 36, `Open_Container` use, tag Family Worker, MaxStack 10), two NPC roles `GlymeraWorker.json` and `GlymeraMarker.json`, classes `GlymeraWorker` (+ ChestData / ChestState / WorkerConfig / ChestRecord) and `W7` (+ `TickingPin`).
- **Worker role:** Type Generic, appearance `Feran_Civilian` (the "Outlander Peon"), `Invulnerable`, `DisableDamageGroups [Player, Self]`, `KnockbackScale 0`, separation on (distance 2), Walk motion (speed 6, climb 1.2). Instruction 1: Sensor `Target` slot `LockedTarget` range 100 -> body `Seek` (stop 1, slow-down 3) + head `Watch`. Instruction 2: otherwise `WanderInCircle` radius 2. `SetInteractable` hint "Worker".
- **Marker role:** appearance `Kweebec_Seedling`, invulnerable, speed 0.1 (stands still); the code shrinks its model scale to 0.01 -> invisible.
- Defaults: scanRadius 16, chestScanRadius 48, workerTickMs 2000, chestScanTickMs 5000, miningDistance 3.5, maxActiveChests 3, stuckTimeoutMs 30000, returnTimeoutMs 60000, depositThreshold 16, maxWorkRadius 32, craftingEnabled true.

## 3. Their mechanic -> engine API / asset -> use for our totems
| Their mechanic | Engine API / asset (names seen) | Use for our totems |
|---|---|---|
| Config object (above) in its own `config.json` | gson, plugin data dir | Idea only: ours go through `tools/skyycfg.py` (Server Setup). Per-player cap 3 maps to a `totem.maxPerPlayer`-style line only if Skyy wants it [no cap]. |
| Chest registry `chests.json` (owner, x/y/z, world, target) + in-memory `activeChests`, reloaded on start | `getDataDirectory`, `ConcurrentHashMap` | We already persist totems in `shards/<pkey>.properties` (spec section 12). Nothing to take. |
| **Finding placed chests:** every 5 s per online player, scan loaded chunks within 48 blocks; test "does this chunk contain the chest block id" first, then each block; item id children (variants) included | `ChunkStore.getChunkReference`, `ChunkUtil.chunkCoordinate / indexChunk`, `BlockTypeAssetMap.getIndex / getChildren`, `BlockModule.getComponent(ItemContainerBlock ...)` | **Avoid** polling for placed blocks: our totems are known from the saved record at place time (pad -> record). Reuse only the "check the chunk's block-type set before the block loop" trick for any pad / node scan. |
| **Target block comes from the chest's first item** (`Item.getBlockId`), plus all variants of it | `Item.getBlockId`, `BlockType.getAssetMap` | UI idea: a totem's "works on" could be a sample-item slot. Our island already says the crop / ore, so keep island type (question 3). |
| **Marker trick:** the worker NPC only knows "walk to my LockedTarget". The mod spawns a second invisible still NPC at (x+0.5, y, z+0.5) over the target block and sets it as the worker's locked target. No path-finding code of its own. | `NPCPlugin.get().spawnEntity(store, roleIndex, pos, rot, ...)`, `NPCEntity`, `MarkedEntitySupport.setMarkedEntity("LockedTarget", ref)`, `ModelComponent` scale via reflection + `isNetworkOutdated`, `UUIDComponent` | **Proves** named-role NPC spawn + engine path-seek works. If Skyy wants a visible Sprite / Golem walking to a crop or ore node, this is the cheapest route: a role JSON with `Seek` on `LockedTarget` + a marker role. Cosmetic only; output stays lazy maths. |
| State machine WAITING_FOR_ITEM -> SCANNING -> MOVING_TO_BLOCK -> MINING -> MOVING_TO_CHEST -> DEPOSITING -> CHEST_FULL / IDLE, 2 s tick on the scheduled executor, hops to the world thread with `world.execute` | `HytaleServer.SCHEDULED_EXECUTOR`, `World.execute(Runnable)` | CHEST_FULL = stop equals our "storage full -> sleeping animation" (spec 9.2). Take the **states as an animation script** for a visible worker (walk, swing, carry, drop), not as the production loop. |
| Block search: nearest matching block within scanRadius of the worker AND maxWorkRadius of the chest, height clamp, `isReachable` (12 empty-neighbour checks) | `W7.getBlock`, world height 319 | A visual worker needs "nearest ripe crop / ore node in range": use our own cell list (the totem's range square), not a world scan. |
| **Mining = direct block removal:** block set to `Empty`, +1 of the block's own id added to an in-memory map. No loot table, tool, Fortune or XP. | `BlockOperations.setBlock` (via W7), `BlockType.getId` | **Do not copy the economy.** Ours pays at Collect (XP, collections, Fortune, augments). Their block is gone for good; shard nodes are eternal, so a worker must only animate, never remove a shard block. |
| Deposit at 16 items / when idle: `new ItemStack(id, qty)` -> `ItemContainer.addItemStack`; full test by capacity | `ItemContainerBlock`, `ItemContainer.addItemStack` | Our deposit is storage-tier maths, not a chest. Lesson: **check the add result** (they ignore leftovers); we keep count-before / count-after (AGENT-BRIEF). |
| Stuck 30 s -> drop the marker and rescan; no return in 60 s -> **teleport the worker to the chest** | `TransformComponent.setPosition`, `Store.putComponent` | For a visible worker: a stuck wisp snaps back to its totem. |
| Chunk not loaded -> worker removed, re-spawned when loaded. `W7.TickingPin` (a chunk system) vetoes the NonTicking flag on pinned chunks so they keep ticking | `RefChangeSystem`, `NonTicking`, `ChunkStore.REGISTRY`, `ChunkPreLoadProcessEvent` | **Avoid.** It is how a world-tick design fakes offline work; we use lazy maths, which is why "100 % idle" costs us nothing while empty. |
| Cleanup: on start remove every entity with the worker / marker role index; `removeDuplicateWorkers` removes extras within 40 blocks of a chest; shutdown despawns each | `Role.getRoleIndex`, `Store.forEachChunk`, `Store.removeEntity(ref, RemoveReason.REMOVE)` | **Copy the idea** for any visual NPC: spawned NPCs survive restarts, so wipe by role index in `start()`; do not trust saved uuids alone. |
| Per-player limit: over 3 chests -> the block is set `Empty`, the item is returned to the player's storage, a chat line is sent | `PlayerRef.getUuid`, `Inventory.getStorage().addItemStack`, `Message.raw` | Same refund pattern for any "too many totems" case (storage-first); refund only after the block is seen removed. |
| Recipe written at run time into a generated pack folder `mods/GlymeraWorkerCrafting` and registered | `AssetModule.registerPack`, `AssetPack.PackSource.MODS` | **Avoid** writing into the mods folder at run time. Our recipes ship in jar assets (Totem Bench). |
| Invulnerable, no knockback, separation, interactable NPC through role flags | role JSON | Same flags for our visual workers so players cannot kill or push them. |

## 4. Risks
- Engine API is 0.7-era and partly reflection-based (they set `ModelComponent.scale` and `isNetworkOutdated` by reflection): a game update may break the invisible-marker trick. Prefer a plain role that wanders near the totem for looks.
- NPCs outlive restarts and world unloads; a crash leaves strays. Needs the wipe-on-start rule.
- Server load: a 5 s scan x players x radius 48 is heavy; shard worlds are small, so cap visible workers (1 per totem).
- Mining deletes blocks; shards forbid breaking. A visual worker must never change blocks.
- Licence ARR: ideas and engine names only. Appearances `Feran_Civilian` and `Kweebec_Seedling` are vanilla ids (fine to reference).
- Names above come from constant-pool strings and numbers of the jar, not from running it; control flow was read from byte-code but not run.

## 5. Questions for Skyy (defaults in [brackets])
1. Should totem workers be **visible walking NPCs** (Sprite / Dryad / Golem walking to crops and swinging) or stay particles with an animation? [particles first; add one walking worker per totem as a cosmetic round once probe N1 passes]
2. When a worker "works" a node, the node never disappears? [yes - shards stay eternal]
3. Pick a totem's target by **dropping a sample item into a slot** (their Worker Chest idea) on top of the island type? [no - island type decides]
4. A cap on placed totem poles per player like their 3 chests? [no cap; tiers and the 6 island slots limit it]

## 6. For the local session (UNVERIFIED - nothing below was run)
- Probe N1 (spec section 11): spawn one role that `Seek`s a `LockedTarget` inside a copy of a shard world. Check signatures on the current jar with `tools/dev/reflect.py com.hypixel.hytale.server.npc.NPCPlugin` and `...role.support.MarkedEntitySupport`.
- Cheaper cosmetic worker: a role with only `WanderInCircle` around its totem (no marker) - probe that first.
- If workers ship: role ids `Skyy_Worker_*`, wipe all on `start()`, one per totem, despawn when nobody is in the shard, never touch blocks.
- Keep real-time chunk pinning out unless a later spec asks for it.
