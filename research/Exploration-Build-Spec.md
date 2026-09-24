# Exploration build spec (this round)

*For the build agents of the Exploration round. Written 2026-09-24 from `SkyyExploration-Plan.md` (Skyy's picks, they/them), `research/Exploration-Research.md` and a fresh engine pass. Every engine name below was re-checked this pass with `tools/dev` (reflect.py, reflectmod.py, bc.py, bcfull.py, callers.py, cpgrep.py, clinit.py) against the release `HytaleServer.jar`, and with python `zipfile` against `Assets.zip`. VERIFIED = seen in bytecode or assets. NEEDS A TEST = the pieces are verified but the behavior has not been seen in game.*

**Scope = the 'Build now' table only:** SkyyExploration 0.1 (new), SkyySkills 0.4.1 (patch on 0.4), SkyyTrees 0.2 (on 0.1). No deploy. Build with plain `python <script>` (it must end with `assembled ...jar`), then `python tools/ci/lint.py` (0 fails). Do not commit.

**Out of scope (later, server):** A1 discovery spots, A2 secret spots, A3 island arrival, A7 dungeon/cave clears, B3 finder sense, C1 Echo Shards, C2 island %, C3 zone hunt, C4 egg hunt, C5 museum, D1/D2 warps and scrolls, D4 lootrun camps, D5 map reveal, cosmetics, and the bag restructure.

---

## 0. Verdicts

| Question | Verdict |
|---|---|
| **When is chest loot generated?** | **When the chest's block entity is ADDED to the chunk store, not when it is opened.** `builtin.adventure.stash.StashPlugin$StashSystem` (a `RefSystem` on the ChunkStore, query `Query.and(ItemContainerBlock, BlockModule$BlockStateInfo)`) runs `onEntityAdded` when `World.getWorldConfig().isBlockSpawnersResolved()` is true. It calls `StashPlugin.stash(info, container, clear)`: `getDroplist()`, `ItemModule.get().getRandomItemDrops(droplist)`, a slot shuffle with `new Random(HashUtil.hash(x, y, z))`, and `addItemStackToSlot`. Then, when `StashGameplayConfig.isClearContainerDropList()` (default **true**, constructor `iconst_1`), it calls `setDroplist(null)` + `markNeedsSaving()`. World loot chests come from `Block_Spawner_Block`s. `builtin.blockspawner.BlockSpawnerPlugin$BlockSpawnerSystem.onEntityAdded` picks a `BlockSpawnerTable` entry with `HashUtil.random(seed, x, y, z, salt)`, removes the spawner entity, and sets the chest block with the entry's components. Those components carry `ItemContainerBlock.Droplist` (46 entries in `Server/Item/Block/Spawners/**`, all resolving to `Server/Drops/Prefabs/*`). **Consequence:** when a player opens a world chest it is already full and its drop list is already null. |
| **Most robust "world-generated loot chest" signal** | **A drop list present on the `ItemContainerBlock` at the moment its entity is added**, captured by our own ChunkStore `RefSystem` that is ordered **BEFORE** `StashPlugin$StashSystem` (`SystemDependency(Order.BEFORE, StashPlugin$StashSystem.class)`). No player can create a drop list. Placed chests never have one: all 47 container block types in Assets have no default `Droplist`, and `BlockPlaceUtils.tryPlaceBlock` puts only `PlacedByInteractionComponent(uuid)` on the new block entity. Only the engine (spawner tables, prefabs) or an admin (`/stash set`, group `hytale:WorldEditor`) can set one. `PlacedByInteractionComponent` (registered on the ChunkStore as `"PlacedByInteraction"` with a codec, so it is saved) is the **second guard** at open time, and a REMOVE of the block entity drops the record. The droplist-at-open and PlacedBy-only signals were rejected: the drop list is gone by then, and code-placed chests (SkyyIslands' starter chest) carry no PlacedBy. |
| **Title display** | **Chat prefix through the `PlayerChatEvent` formatter.** `PlayerChatEvent` is an `IAsyncEvent`. `GamePacketHandler` dispatches it with `EventBus.dispatchForAsync(...).dispatch(e)`, and on completion it runs `e.getFormatter().format(sender, content)` and sends the `Message` to every target. We register `getEventRegistry().registerAsyncGlobal((short) 30000, PlayerChatEvent.class, Function)`. 30000 is above `EventPriority.LAST` = 21844, so we run after every standard handler. `Function.apply(future)` returns `future.thenApply(wrap)`, and `wrap` sets a formatter that calls the PREVIOUS formatter and prepends the title with `Message.join(new Message[] {...})`. This is the exact pattern of the installed RPGLeveling 0.3.13 `RpgChatFormatHook` (`registerAsyncGlobal(LAST, ...)`, `getFormatter` then `setFormatter`, `thenApply`). **Nameplate: not used in 0.1.** `entity.nameplate.Nameplate.setText` exists, but `PlayerSystems$NameplateRefSystem` / `DisplayNameSystems$SyncDisplayName` own it, so a fight is likely. The title also shows on `/explore` and on the bridge (`explore:title:<uuid>`) for SkyyHud / SkyyParty later. |
| Zone lookup (A6) | `Player.getWorldMapTracker().getCurrentZone()` returns `WorldMapTracker$ZoneDiscoveryInfo` (a record) or null. The engine updates it in `updateCurrentZoneAndBiome` (`UPDATE_SPEED` 1.0 s). Our key is `regionName()` (the zone folder, e.g. `Zone1_Tier1`, the same key the engine's `discoverZone(World, regionName)` uses). The display name is `server.lang` `map.region.<regionName>`, and `zoneName()` is the zone (`Emerald_Wilds`). 27 regions have a `Discovery` block (`Server/World/Default/Zones/*/Zone.json`). The engine's set (`PlayerConfigData.getDiscoveredZones`) is per account, so our record is per profile. |
| Flying / creative checks (A5) | `MovementStatesComponent.getMovementStates()` exposes public booleans `flying`, `gliding`, `mounting` and others (reflect). `Player.getGameMode()` returns `protocol.GameMode` {`Adventure`, `Creative`}. No XP and no record while `flying` or in `Creative`. Teleports do not block (Skyy Q8). |

---

## 1. Engine facts used (all VERIFIED 2026-09-24)

| Piece | Exact name | How verified |
|---|---|---|
| Loot roll | `builtin.adventure.stash.StashPlugin.stash(BlockModule$BlockStateInfo, ItemContainerBlock, boolean) -> ListTransaction` | bcfull (full body above) |
| Roll trigger | `StashPlugin$StashSystem extends component.system.RefSystem`, `onEntityAdded(Ref, AddReason, Store, CommandBuffer)`, gated by `WorldConfig.isBlockSpawnersResolved()` | bcfull; `StashPlugin.setup` does `getChunkStoreRegistry().registerSystem(new StashSystem(ItemContainerBlock.getComponentType()))` |
| Clear flag | `StashGameplayConfig.isClearContainerDropList()`, key `"ClearContainerDropList"`, default true | clinit + ctor bytecode |
| Spawner resolve | `builtin.blockspawner.BlockSpawnerPlugin$BlockSpawnerSystem.onEntityAdded`: `BlockSpawnerTable.getEntries().get(HashUtil.random(...))`, `CommandBuffer.removeEntity(ref, RemoveReason.REMOVE)`, `CommandBuffer.run(...)` with `BlockSpawnerEntry.getBlockComponents()` | bc |
| Container component | `server.core.modules.block.components.ItemContainerBlock`: `getComponentType()`, `getDroplist()`, `setDroplist(String)`, `getItemContainer() -> SimpleItemContainer`, `getWindows() -> Map` (key = player `UUIDComponent.getUuid()`, value = `ContainerBlockWindow`) | reflectmod; `OpenContainerInteraction.interactWithBlock` bytecode (putIfAbsent(uuid, window), remove on failure) |
| Block entity position | `BlockModule$BlockStateInfo.getComponentType()/getIndex()/getSectionRef()`; `ChunkSection.getComponentType()/getX()/getY()/getZ()`; `ChunkUtil.xFromIndex/yFromIndex/zFromIndex(int)`, `ChunkUtil.worldCoordFromLocalCoord(int,int)`; world = `((ChunkStore) store.getExternalData()).getWorld()` | StashPlugin.stash bytecode offsets 0-176 (copy it exactly) |
| Placed-by tag | `server.core.modules.interaction.components.PlacedByInteractionComponent.getComponentType()/getWhoPlacedUuid()`; put by `BlockPlaceUtils.tryPlaceBlock` (offsets 452-475) on the block entity AFTER it exists; ChunkStore component `"PlacedByInteraction"` with CODEC (persisted) | bcfull, bc `InteractionModule#setup` |
| Ordering API | `component.dependency.SystemDependency(Order, Class)`, `Order.BEFORE`; `ISystem.getDependencies() -> Set`; `ComponentRegistry.registerSystem` calls `Dependency.validate` (throws `IllegalArgumentException` when the target class is not registered) BEFORE `registerSystem0` (so a failed attempt registers nothing) | reflect + bc `ComponentRegistry#registerSystem` offsets 197-242 |
| Core plugins first | `PluginManager`: "Loading pending core plugins!" then "Loading plugins!" (StashPlugin is a core plugin; its system exists before our `setup()`) | cpgrep strings |
| Add/remove reasons | `component.AddReason` {SPAWN, LOAD}; `component.RemoveReason` {REMOVE, UNLOAD, BUILDER_TOOLS_UNDO} | reflect |
| Open state keeps the entity | `BlockOperations.setBlockInteractionState(..., "OpenWindow", ...)` calls `setBlock(..., settings 198)`; bit 2 set, so `BlockEntity.setBlockEntity` is skipped (the container entity is not replaced when a chest opens) | bcfull |
| Use event | `server.core.event.events.ecs.UseBlockEvent$Post` (`getTargetBlock() -> Vector3i`, `getBlockType()`, `getContext()`), fired by `UseBlockInteraction.doInteraction` (offset 254); chest block `Interactions.Use = "Open_Container"` | callers + Assets |
| Open window | `server.core.entity.entities.player.windows.ContainerBlockWindow extends BlockWindow`; `BlockWindow.getX()/getY()/getZ()/getBlockType()` (public); `Player.getWindowManager().getWindows() -> List` | reflectmod |
| Multi-block origin | `BlockSection.getFiller(int,int,int)`; origin = target - `FillerBlockUtil.unpackX/Y/Z(filler)` when filler != 0; `BlockModule.getBlockEntity(World, int, int, int) -> Ref` | StashCommand#getItemContainerBlock offsets 174-248 |
| Extra roll | `server.core.modules.item.ItemModule.get().getRandomItemDrops(String) -> List` (of `ItemStack`) | reflectmod + stash bytecode |
| Storage-first give | `Player.getInventory().getCombinedStorageHotbarBackpack()` + `SimpleItemContainer.addOrDropItemStack(Store, Ref, ItemContainer, ItemStack)` | SkyySkills 0.4 Perks.give (probed there) |
| Zone | `Player.getWorldMapTracker()`, `WorldMapTracker.getCurrentZone()`, `WorldMapTracker$ZoneDiscoveryInfo.regionName()/zoneName()/display()`; `PlayerZoneCommand` prints `server.map.region.%s` of `regionName()` | reflectmod + bc |
| Chunk key | `math.util.ChunkUtil.indexChunkFromBlock(double, double) -> long`, `xOfChunkIndex(long)`, `zOfChunkIndex(long)` | reflect |
| Movement / mode | `entity.movement.MovementStatesComponent.getComponentType()/getMovementStates()`; `protocol.MovementStates` public booleans `flying gliding mounting onGround ...`; `Player.getGameMode()`; `protocol.GameMode.Creative` | reflect |
| Chat | `server.core.event.events.player.PlayerChatEvent` (`getSender()`, `getFormatter()`, `setFormatter(Formatter)`, `DEFAULT_FORMATTER`), `PlayerChatEvent$Formatter.format(PlayerRef, String) -> Message` (interface); `event.EventRegistry.registerAsyncGlobal(short, Class, Function)`; `event.EventPriority` FIRST -21844 .. LAST 21844 | reflect + bc GamePacketHandler + RPGLeveling bcmod |
| Message | `server.core.Message.join(Message[])`, `raw(String)`, `color(String)`, `translation(String)`, `insert(Message)` | reflect |
| Instances | `builtin.instances.InstancesPlugin` constant `INSTANCE_PREFIX` = `"instance-"`; SkyyIslands worlds are `skyy-island-<pkey>` | cpgrep + SkyyIslands 0.4.4 |
| Name clash | vanilla has `/eventtitle` (not `/title`); no vanilla or Skyy `/title`, `/titles`, `/explore` | cpgrep over command classes + repo grep |

---

## 2. SkyyExploration 0.1 (new mod)

### 2.1 Build and identity
- Script: `SkyyExploration/build_skyyexploration_0.1.py` (new; the SkyyTrees 0.1 layout: `T` token map + `M/F/C` helpers, `B.probe` for every engine member in section 1, Assets checks, `B.manifest("SkyyExploration", VERSION, ...)`, `m["IncludesAssetPack"] = False`, `B.assemble(jar, m, OUT, {})`). Package `com.skyy.explore`, main `com.skyy.explore.SkyyExplorationPlugin`. Display name `"0.1 SkyyExploration"`.
- **Zero hard dependencies.** It never references another mod's classes; everything goes through the `skyy.bridge` map. Without SkyySkills, the XP waits in an owed ledger (2.7). Without SkyyTrees, the tree luck is 0. Without SkyyCoins, Scavenger does nothing. Without SkyyProfiles, `pkey = uuid`.
- Data dir: `getDataDirectory().resolveSibling("Skyy_SkyyExploration")`.
- javassist rules as usual: no lambdas, generics, varargs (explicit arrays: `Message.join(new Message[] { a, b })`, `Query.and(new Query[] { ... })`), autoboxing (`Long.valueOf`), enhanced-for, inner classes, String switch or try-with-resources. Add each method before its callers. A synchronized block holds one call only (use `synchronized` static methods). Double the f-string braces.

### 2.2 Classes and systems (ONE registerSystem per class)
| Class | Kind | Registered on | Job |
|---|---|---|---|
| `ChestSpawnSys` | `RefSystem`, query `Query.and(new Query[] { ItemContainerBlock.getComponentType(), BlockModule$BlockStateInfo.getComponentType() })`, `getDependencies()` = `HashSet{ new SystemDependency(Order.BEFORE, StashPlugin$StashSystem.class) }` | `getChunkStoreRegistry()` | capture loot chests (2.3) |
| `ChestSpawnLateSys` | same code, **no** dependency | ChunkStore, **only if** registering `ChestSpawnSys` threw `IllegalArgumentException` (StashPlugin disabled or missing; then nobody clears drop lists, so the late copy still sees them). Log one WARN. | fallback |
| `ChestOpenSys` | `EntityEventSystem(UseBlockEvent$Post.class)`, query `Archetype.empty()` (SkyySkills HarvestSys pattern) | `getEntityStoreRegistry()` | schedule an `OpenCheck` for registered loot-chest positions |
| `ExpTick` | `EntityTickingSystem`, query `Player.getComponentType()`, `isParallel(int,int)` returns false, a 1 s per-player throttle (TreeTick / AcroSys pattern) | EntityStore | epoch check, open-window scan, chunks, zones, owed flush, titles |
| `OpenCheck` | Runnable | `world.execute` + `HytaleServer.SCHEDULED_EXECUTOR` re-schedule | verify that the window really opened, then award |
| `ChatHook` / `ChatWrap` / `TitleFormatter` | `Function`, `Function`, `implements PlayerChatEvent$Formatter` | `getEventRegistry().registerAsyncGlobal((short) ExpCfg.CHAT_PRIORITY, PlayerChatEvent.class, new ChatHook())` | chat title prefix (2.8) |
| `ExpSaver` | Runnable, `SCHEDULED_EXECUTOR.scheduleWithFixedDelay` 2 s | - | journal appends, dirty property files (every 5th run = 10 s), retainOnline every 30 s |
| data / logic | `ExpDefs` (generated tables), `ExpCfg`, `ExpData`, `ExpStore`, `ChestReg`, `ExpAward`, `ExpXp`, `ExpTitles`, `ExpStatsFn`, `ExpTitleFn` | - | - |
| UI / commands | `ExplorePage extends CustomUIPage` (public `build`), `ExploreCmd`, `ExploreQuietCmd`, `TitleCmd`, `TitleSetCmd` (usage variant), `ExploreAdminCmd` + `ExAdminReloadCmd`, `ExAdminStatsCmd`, `ExAdminResetCmd` | `getCommandRegistry()` | 2.9, 2.10 |

### 2.3 A4: first open of each world loot chest

**Capture (ChestSpawnSys.onEntityAdded, world thread, no file I/O):**
1. `ItemContainerBlock icb = store.getComponent(ref, ItemContainerBlock.getComponentType())`, then the `BlockStateInfo`, `ChunkSection` and world x/y/z exactly as `StashPlugin.stash` computes them. World name = `((ChunkStore) store.getExternalData()).getWorld().getName()`. Skip excluded worlds (2.14 `exploration.excludeWorldPrefixes`).
2. `String dl = icb.getDroplist()`.
   - `dl != null`: `ChestReg.put(world, pack(x,y,z), dl, placedBy)`. `placedBy` = `PlacedByInteractionComponent.getWhoPlacedUuid()` if the component is on the entity now (present at LOAD for saved chests, e.g. an admin `/stash set` chest), else `"-"`. Increment the capture counter for the world.
   - `dl == null` and `reason == AddReason.SPAWN` and the position is registered: a fresh non-loot container replaced it (player placement, prefab paste, chunk regeneration), so `ChestReg.remove`. A LOAD without a drop list is the normal "already rolled" reload, so the entry is kept.
3. `onEntityRemove`: `RemoveReason.REMOVE` or `BUILDER_TOOLS_UNDO` calls `ChestReg.remove`. `UNLOAD` keeps the entry.
4. `pack(x,y,z)` = `((long)(x & 0x3FFFFFF) << 38) | ((long)(z & 0x3FFFFFF) << 12) | (long)(y & 0xFFF)`.

**Open detection (two paths, both call `ExpAward.chestOpened(pr, ref, world, x, y, z)`, which is idempotent per profile):**
- **Event path.** `ChestOpenSys.handle` on `UseBlockEvent$Post`. It gets the `PlayerRef` from `chunk.getReferenceTo(idx)` and resolves the origin: `w.getChunkStore().getChunkSectionReferenceAtBlock(x,y,z)`, then the `BlockSection`, then `getFiller`, then origin = target - unpack (StashCommand math). It looks up `ChestReg` at the raw position and then at the origin. Only for a registered, not-yet-opened (this profile) position does it queue `OpenCheck(u, world, x, y, z, pkey)` with `w.execute`.
- **`OpenCheck` (HarvestTask pattern: next tick, then every `chests.pollMs` 100 ms until `chests.pollMaxMs` 2000).** `Ref be = BlockModule.getBlockEntity(world, x, y, z)`, `ItemContainerBlock c = world.getChunkStore().getStore().getComponent(be, ...)`, `UUIDComponent uc` = the player entity's `UUIDComponent`. Opened = `c.getWindows().containsKey(uc.getUuid())`.
- **Backup path.** In `ExpTick` each second, every `ContainerBlockWindow` in `Player.getWindowManager().getWindows()` gives `getX/getY/getZ`. If that position is registered and not opened on this profile, award. This covers a chest where `UseBlockEvent$Post` does not fire (NEEDS A TEST) for any window kept open 1 s or more.

**Award, `ExpAward.chestOpened` (world thread), in this order:**
1. Refuse (no record, retry on the next open) when: creative; `MovementStates.flying` (Skyy's no-flying rule, applied to every source); `profile:busy:<uuid>` present; `pkey(u)` differs from the key captured by the event; the player is not in that world.
2. Guard: when `PlacedByInteractionComponent` is on `be` and its uuid differs from the recorded `placedBy` (a recorded `"-"` counts as differs), a player-placed chest now sits where the loot chest was. Remove the registry entry, log DEBUG and stop.
3. Record `world x y z` in the profile's opened set (memory), `chests++`, `saveSoon` (2 s).
4. XP = `ExpCfg.chestXp(droplist)` (2.15), added to owed, then `ExpXp.flush(u)` (2.7).
5. Chest luck (2.4), then Scavenger (2.4b).
6. Chat (not quiet-able): `[Exploration] Loot chest found - Goblin chest tier 2 - +600 Exploration XP (12 chests)`. The label comes from the drop list id (`Zone<Z>_<Faction>_Tier<T>` gives `<Faction> chest tier <T>`, `Encounters` gives `Treasure`), else `Loot chest`.
7. `ExpTitles.check(u)` (new title line).

### 2.4 B2: chest luck (one extra roll, storage first)
- Chance = `min(luck.max, level x luck.perLevel + treeLuck)`. `level` = `skill:fn:level` of `Object[]{UUID, "Exploration"}` (Integer; 0 without SkyySkills). `treeLuck` = `tree:fn:bonus` of `Object[]{UUID, "Exploration.ELuck"}` (Double; 0 when absent).
- On success (`ThreadLocalRandom`): `List drops = ItemModule.get().getRandomItemDrops(droplist)`. For each non-empty `ItemStack`: `SimpleItemContainer.addOrDropItemStack(store, ref, player.getInventory().getCombinedStorageHotbarBackpack(), stack)`. The roll goes to the opener's inventory (storage first, dropped at the feet when full), never into the chest. Then `luck++` and chat `Chest luck! Extra roll: +3 Iron Ore +1 Copper Bar ...` (at most 3 items named, then `...`).
- Only ever inside step 5 of a first open, and never while `profile:busy` is present.
- **2.4b Scavenger (tree node, draft):** chance = `tree:fn:bonus` of `Object[]{UUID, "Exploration.EScav"}`. On success, `coins:fn:add` of `Object[]{UUID, Long.valueOf(scav.coinsPerLevel x level)}`. Skip silently without SkyyCoins or at level 0.

### 2.5 A5: map coverage
In `ExpTick` (1 s, world thread), for each player:
- Skip when creative, `flying`, `gliding && !chunks.payWhileGliding`, `mounting && !chunks.payWhileMounted`, the `MovementStatesComponent` is missing, `Player.isWaitingForClientReady()`, or the world is excluded.
- `long ck = ChunkUtil.indexChunkFromBlock(pos.x(), pos.z())` from `TransformComponent.getPosition()`. When `ck` differs from the last tick and is **not** in this profile's chunk set for this world: add it, then `total++`. If `paid[world] < chunks.maxPaidPerWorld`: `paid[world]++` and owed += `round(chunks.xp x zoneMult)`. `zoneMult` = `chunks.zoneMult[Z-1]` for `Zone<Z>` from the current region, 1.0 for Oceans or no zone.
- A flying or creative second does not record the chunk, so walking it later still pays. A teleport destination chunk counts (Skyy Q8).
- Chat, aggregated: at most one line per `chunks.feedbackMs` (30 s), hidden by `/explore quiet`: `+1,240 Exploration XP from 18 new chunks (340 here)`.

### 2.6 A6: Hytale zone discovery, per profile
In `ExpTick`, with the same skip rules as 2.5 (creative, flying):
- `ZoneDiscoveryInfo zi = player.getWorldMapTracker().getCurrentZone()`. If it is null (Void / Flat / hand-built worlds), do nothing.
- `String r = zi.regionName()`. If it is not in the profile's zone set: add it, owed += `zone.xp.<r>` (unknown region: `zone.xpDefault`), then chat `[Exploration] Discovered Drifting Plains (Emerald Wilds) +500 Exploration XP (7 of 27)`. Names come from build-time tables baked from `Server/Languages/en-US/server.lang` (`map.region.*`, `map.zone.*`); an unknown region shows its id.
- The key is global (not per world): generating a second default-generator world cannot re-earn a region. Display:false regions (shores, shallow seas) count, with smaller XP.
- No engine banner of our own by default (`zones.banner=false`). The engine already shows its banner once per ACCOUNT, and a second banner could overlap it. With `true`: `EventTitleUtil.showEventTitleToPlayer(pr, Message.translation("server.map.region." + r), Message.raw("+500 Exploration XP"), false)`.

### 2.7 XP to SkyySkills (no boosters) and the owed ledger
- Every source adds to `ExpData.owed` (a per-profile file field). `ExpXp.flush(u)` runs right after an award and every `bridge.retryMs` (5 s) while owed > 0. It calls `skill:fn:addxp` with `Object[]{UUID, "Exploration", Long.valueOf(min(owed, 500000)), "exploration", pkey}`. The 5th element `expectKey` makes Skills refuse the call if the active profile changed. TRUE (Boolean) means owed -= amount and earned += amount. FALSE or a missing Function keeps it: the page shows `N XP waiting for SkyySkills 0.4.1`, and the server log warns once per session.
- SkyyExploration **never multiplies** anything: config values are base values. SkyySkills 0.4.1 bypasses its multiplier and every tree or booster bonus for the Exploration slot (section 3). That satisfies Skyy Q3.
- Known edge (documented, not fixed): a profile switch between Skills' `offer` and its queued `BridgeTask` drops that one grant. Both run on the same world thread, and switches are manual and rare.

### 2.8 D3: titles and their display
**Table (build-time `ExpDefs.TITLES`: id, name, kind, requirement).** Ids are lowercase, one word, no underscores.

| id | Name | Earned by (active profile) |
|---|---|---|
| wanderer | Wanderer | Exploration 5 |
| pathfinder | Pathfinder | Exploration 10 |
| trailblazer | Trailblazer | Exploration 15 |
| wayfarer | Wayfarer | Exploration 20 |
| explorer | Explorer | Exploration 25 |
| voyager | Voyager | Exploration 30 |
| cartographer | Cartographer | Exploration 40 |
| pioneer | Pioneer | Exploration 50 |
| worldwalker | Worldwalker | Exploration 75 |
| echoseeker | Echo Seeker | Exploration 100 |
| wildswalker | Wilds Walker | Zone1_Spawn + Zone1_Tier1..3 discovered |
| sandstrider | Sand Strider | Zone2_Tier1..3 |
| frostranger | Frost Ranger | Zone3_Tier1..3 |
| ashwalker | Ash Walker | Zone4_Tier4..5 |
| deepdiver | Deep Diver | Oceans |
| worldseer | World Seer | all 13 named (Display:true) regions |
| treasurehunter | Treasure Hunter | 25 loot chests |
| relicseeker | Relic Seeker | 100 loot chests |
| hoarder | Hoarder | 250 loot chests |
| roamer | Roamer | 1,000 chunks (all worlds) |
| farstrider | Far Strider | 10,000 chunks |

- **Earned is derived, never stored** (level from `skill:fn:level`, plus the zone set and the counters), so nothing can be duped or lost. Only the **selected** id is stored (`title=` in the profile file). A selected title that is not earned (after a profile switch, or a table change) acts as none.
- `ExpTitles.check(u)` runs after each award and each 1 s tick (level changes). A newly earned title posts one chat line: `New title unlocked: Wayfarer - use it with /title wayfarer`.
- **Display = chat prefix (verdict, section 0).** `ChatWrap.apply(e)` does: `PlayerChatEvent ev = (PlayerChatEvent) e; Formatter prev = ev.getFormatter();`. If `prev instanceof TitleFormatter`, return `ev`. Otherwise `ev.setFormatter(new TitleFormatter(prev == null ? PlayerChatEvent.DEFAULT_FORMATTER : prev))` and return `ev`.
- `TitleFormatter.format(sender, content)` does: `Message m = prev.format(sender, content); String t = (String) ExpTitles.CHAT.get(sender.getUuid());`. If `t == null`, return `m`. Otherwise return `Message.join(new Message[] { Message.raw("[" + t + "] ").color(colorOf(kind)), m })`. Colors: level `#9fd0ff`, zone `#9adf86`, chest `#ffd27a`, chunk `#c8a0ff`.
- **Thread:** the formatter runs on the async chat thread. It reads only `ExpTitles.CHAT` (a `ConcurrentHashMap` UUID to display String, filled by `ExpTick` on the world thread). It never touches components or files.
- Config `titles.chatPrefix=true`, `titles.chatPriority=30000`.

### 2.9 `/explore` page (inline, section 2 rules)
Rules: `appendInline` only, no `.ui` files, no underscores in ids, root anchor Width/Height only, `TextButton` + `EventData.of("a", payload)`, payloads matched with a trailing quote (`data.indexOf("exuse1\"")`), dynamic text through `b.set("#Id.Text", ...)`, no MouseEntered handlers, no periodic updates (rebuild only on clicks), and never close a page before opening another (the Skills / Tree buttons run the command while this page is open).

```
#SkyyExRoot  Group  Anchor (Width 860, Height 620)  Background #0b1524(0.96)  Padding (H 16, V 10)  LayoutMode Top
 #SkyyExHead  Group Height 36 LayoutMode Left
   TextButton #SkyyExTab0 "Overview" (120x32)  #SkyyExTab1 "Zones"  #SkyyExTab2 "Titles"   (6 px gaps; active tab = the "on" style)
   Label #SkyyExLvl (Width 460, align End, 14 bold, #e0a040)  "Exploration 12 - 34.5k XP"  / "SkyySkills not installed"
 Label #SkyyExNote (Height 18, 11, #9fb8cc)  "Loot chests, new chunks, zones - once each per profile - nothing while flying or in creative - XP boosters never apply"
 Group (Height 2, Background #e0a040)
 #SkyyExBody  Group Height 500 LayoutMode Top
   Overview: 2 rows of 3 cards #SkyyExCard0..5 (Group 268x110, #142030(0.9), LayoutMode Left: ItemIcon 56 + Labels title 16 bold / value 13 / sub 11)
     0 Tool_Map                   "Level 12"           "+1.2 max Stamina from Exploration"
     1 Objective_Treasure_Map     "7 of 27 zones"      "5 of 13 named regions"
     2 Furniture_Ancient_Chest_Small "12 loot chests"  "3 chest luck rolls won"
     3 Deco_Map                   "340 chunks here"    "1,204 in all worlds - 24,660 left to pay here"
     4 Rock_Gem_Ruby              "4.5% chest luck"    "level 3.6% + tree 0.9%"
     5 Deco_Scroll                "Wayfarer"           "5 of 21 titles - /title"
     Label #SkyyExOwed (Height 20, #ffb080) "N Exploration XP waiting for SkyySkills 0.4.1" (only when owed > 0)
   Zones: Group LayoutMode Left: #SkyyExZoneL / #SkyyExZoneR (Width 404, LayoutMode Top)
     L: Emerald Wilds (6), Howling Sands (5), Oceans (1); R: Whisperfrost Frontiers (9), Devastated Lands (6)
     header Label 22 bold in zone color; row Label 20: "Drifting Plains  - found" (#9adf86) | "Drifting Plains  - 500 XP" (#7f94a8)
   Titles: Label #SkyyExCur "Your title: Wayfarer" + TextButton #SkyyExNone "No title" (payload exnone)
     two columns of rows #SkyyExT<i> (Height 38, LayoutMode Left): Label name (150, kind color) | Label requirement (170) |
     TextButton #SkyyExUse<i> "Use" (70x28, payload exuse<i>) | Label "In use" | Label "Locked" (#b07a68)
 #SkyyExFoot  Group Height 44 LayoutMode Left Padding (Top 8)
   TextButton #SkyyExSkills "< Skills" (payload exskills -> CommandManager.get().handleCommand(pr, "skills"); only when skill:fn:level exists)
   TextButton #SkyyExTree "Exploration tree" (payload extree -> "tree exploration"; only when bridge tree:names contains Exploration)
   Label #SkyyExMsg (Width 480, 12 bold, #ffe08a)
```
Clicks: `extab<n>` switches the tab. `exuse<i>` selects the title (only if earned), then saveSoon, republish, `rebuild()`. `exnone` clears it.

### 2.10 Commands (HANDOFF COMMAND RULES)
| Command | Class | Permission |
|---|---|---|
| `/explore` (aliases `exploration`, `discoveries`) opens the page on Overview | `ExploreCmd extends AbstractPlayerCommand` | `setPermissionGroups(new String[] { "hytale:Adventurer" })` |
| `/explore quiet` toggles the aggregated chunk XP line (per profile) | `ExploreQuietCmd` subcommand | Adventurer |
| `/title` (alias `titles`) opens the page on the Titles tab | `TitleCmd` | Adventurer |
| `/title <title>`: an id, or a name typed without spaces, case-insensitive (`echoseeker`), 3+ letter prefix; `off` or `none` clears it; a locked title prints its requirement | `TitleSetCmd` = usage variant (description-only ctor + `withRequiredArg("title", ..., ArgTypes.STRING)`, parent `addUsageVariant`) | Adventurer (on the variant too) |
| `/exploreadmin reload` / `stats` / `resetme` | `ExploreAdminCmd` + subcommands | `requirePermission("skyyexploration.admin")` + `setPermissionGroups(new String[0])` on each |

`stats` prints the registry size per world, the captures since start, whether the late fallback is active, and online players' counts. `resetme` clears YOUR active profile's exploration record. It is a test helper: XP already paid to SkyySkills stays.

### 2.11 Storage (tools/PROFILES-CONTRACT.md)
`<world save>/mods/Skyy_SkyyExploration/`:
- `config.properties` (2.14; written with defaults on first run, `/exploreadmin reload`).
- `chests/<worldFile>.log`: world registry journal (not per profile). Lines `A <x> <y> <z> <droplist> <placedByUuid|->` and `R <x> <y> <z>`. Loaded for every file in `setup()`, so it is in memory before any chunk loads. It is compacted (atomic rewrite) at load when lines > 2 x live entries + 1000. Appended by `ExpSaver` from a `ConcurrentLinkedQueue`. `worldFile` = the world name with every char outside `[A-Za-z0-9.-]` replaced by `-`, plus `-` + `Integer.toHexString(name.hashCode())`.
- `players/<pkey>.properties`: `name`, `v=1`, `title`, `quiet`, `owed`, `earned`, `chests`, `luck`, `total` (chunks, all worlds), `zones=<comma list of regionNames>`, `paid.<worldFile>=<n>`. Atomic write (tmp, then `ATOMIC_MOVE`, 5 x 20 ms retries on Windows `FileSystemException`). A file that exists but cannot be read is never overwritten: that player earns nothing until it reads, the server log warns, and the page says so.
- `players/<pkey>/chests.txt`: opened loot chests, lines `<worldFile> <x> <y> <z>`, append-only.
- `players/<pkey>/chunks/<worldFile>.bin`: chunk indices, 8-byte big-endian longs, append-only. A torn last record (size % 8 != 0) is ignored on load. Loaded lazily, on the player's world thread, the first time they tick in that world (at most ~200 KB at the 25k cap), into `it.unimi.dsi.fastutil.longs.LongOpenHashSet` (fastutil ships in HytaleServer.jar; the engine uses it).
- Memory: `ExpStore.DATA` = `ConcurrentHashMap<String pkey, ExpData>`, `OWNER` = pkey to UUID. `ChestReg.W` = `ConcurrentHashMap<String world, ConcurrentHashMap<Long, String "droplist|placedBy">>`.
- Threads: player files are read only on world threads. Writes go through the saver on the scheduler (2 s journals and `saveSoon`, 10 s dirty props), plus a full flush in `shutdown()` (call `super.shutdown()`).

### 2.12 Bridge keys
| Key | Shape | Dir |
|---|---|---|
| `explore:<uuid>` | String `"level:12,zones:7/27,chests:12,chunks:1204,title:wayfarer"` (active profile) | writes |
| `explore:title:<uuid>` | String display name of the selected title, absent = none | writes |
| `explore:fn:title` | `Function apply(UUID) -> String` or null | writes (setup; removed in shutdown) |
| `skill:stats:Exploration` | `Function apply(Object[]{UUID, Integer level, Boolean next}) -> List<String>`. now: `"+4.5% chest luck - an extra roll from loot chests"`, `"Found 7 of 27 zones - 12 loot chests - 1204 chunks"`, `"Title: Wayfarer (/title)"`. next: `"+0.3% chest luck"`, `"Unlocks the title Pathfinder"` if one | writes (SkyySkills 0.4 already reads `skill:stats:<SkillName>`) |
| `skill:fn:addxp`, `skill:fn:level`, `skill:fn:xp` | SkyySkills 0.4 contracts | reads |
| `tree:fn:bonus` | `Object[]{UUID, "Exploration.ELuck"}` or `"Exploration.EScav"` -> Double | reads |
| `tree:names` | String comma list (SkyyTrees 0.2) | reads (Tree button) |
| `coins:fn:add` | `Object[]{UUID, Long}` -> Long | reads (Scavenger) |
| `profile:fn:key`, `profile:epoch:<uuid>`, `profile:busy:<uuid>` | contract | reads |

UUID-keyed values describe the ACTIVE profile. They are republished within 1 s of an epoch change and removed for players gone for 30 s (`retainOnline`, the Trees pattern) and in `shutdown`.

### 2.13 Profiles
- `pkey(u)` = the contract helper. Every file and cache is keyed by pkey. One key per operation: the `OpenCheck` carries the key from the use event and re-checks it in step 1 of the award.
- Epoch (`ExpTick`, 1 s, world thread): the first non-null value is a baseline. A later different value means: forget `lastChunk`, the aggregated chunk line and the flush timer; reload through pkey; republish `explore:*`; recompute `ExpTitles.CHAT`. Data is never moved between keys.
- `profile:busy:<uuid>` present: no chest award and no luck or coin give (the only item moves). Chunks and zones still record.
- Skyy Q1: progress is per profile. The engine's own map reveal and discovered-zone set stay per account, so a new profile "keeps the map" and re-earns our XP. That is the intended split.

### 2.14 config.properties defaults
```
# SkyyExploration 0.1 - /exploreadmin reload (perm skyyexploration.admin). Comments on their own lines.
exploration.excludeWorldPrefixes=instance-,skyy-island-
exploration.excludeWorlds=
noFlyingXp=true
creativeXp=false
chests.enabled=true
chests.base=400
chests.zoneMult=1,2,4,8
chests.tierMult=1,1.5,2,3,4
chests.xpDefault=500
# chest.xp.<DroplistId>=<xp> lines generated for all 46 spawner-table drop lists + Drop_Goblin_Thief + Trork_Camp_Chest
chests.pollMs=100
chests.pollMaxMs=2000
luck.enabled=true
luck.perLevel=0.003
luck.max=0.5
scav.coinsPerLevel=10
chunks.enabled=true
chunks.xp=60
chunks.zoneMult=1,1.5,2,3
chunks.maxPaidPerWorld=25000
chunks.payWhileGliding=true
chunks.payWhileMounted=true
chunks.feedbackMs=30000
zones.enabled=true
zones.banner=false
zone.xpDefault=1000
# zone.xp.<RegionName>=<xp> lines (table 2.15)
titles.chatPrefix=true
titles.chatPriority=30000
bridge.retryMs=5000
```
The build generates the `chest.xp.*` and `zone.xp.*` lines. It asserts every id exists (`Server/Drops/**/<id>.json`, `Zones/<id>/Zone.json` with a Discovery block) and that every drop list referenced by a `Server/Item/Block/Spawners/**` entry's `ItemContainerBlock.Droplist` is in the table.

### 2.15 XP sizing (shared 100-level curve: level 10 = 9,925 cumulative, 15 = 67,425, 20 = 522,425, 25 = 3,022,425, 30 = 8,022,425)
- **Chests:** `chests.base x zoneMult[Z] x tierMult[T]` for `Zone<Z>_*_Tier<T>`.
  - Zone1: T1 400, T2 600, T3 800, T4 1,200
  - Zone2: 800, 1,200, 1,600, 2,400
  - Zone3: 1,600, 2,400, 3,200, 4,800
  - Zone4: 3,200, 4,800, 6,400, 9,600
  - Other drop lists (`Portals_Oasis`, `Drop_Goblin_Thief`, `Trork_Camp_Chest`, admin ones): 500.
- **Zones (named, Display:true):**
  - Zone1_Spawn (First Gate of the Echo) 250, Zone1_Tier1 (Drifting Plains) 500, Zone1_Tier2 (Seedling Woods) 1,500, Zone1_Tier3 (The Fens) 3,000
  - Oceans (Crystalline Depths) 2,000
  - Zone2_Tier1 (Golden Steppes) 5,000, Zone2_Tier2 (Badlands) 8,000, Zone2_Tier3 (Desolate Basin) 12,000
  - Zone3_Tier1 (Frostmarch Tundra) 15,000, Zone3_Tier2 (Boreal Reach) 22,000, Zone3_Tier3 (The Everfrost) 30,000
  - Zone4_Tier4 (Cinder Wastes) 45,000, Zone4_Tier5 (Charred Woodlands) 60,000
  - Named total: 204,250.
- **Zones (hidden shores and shallows):** Zone1 100 each (x2), Zone2 500 (x2), Zone3 1,500 (x6), Zone4 4,000 (x4). Total 26,200. All zones: 230,450.
- **Chunks:** 60 x zone multiplier (1 / 1.5 / 2 / 3), capped at 25,000 paid chunks per world per profile (at most about 1.5M-4.5M per world).
- **Expected pace** (a sprinter crosses about 12 fresh chunks a minute): level 5 in minutes, 10 in about 15 min, 15 in about 1.5 h, 20 in about 6-8 h, about 25 for a fully explored default world. Level 100 is not reachable yet (Skyy accepts it; the server content adds more later).
- **Per-level rewards (SkyySkills):** +0.1 max Stamina per level (+2.5 at level 25, +10 at 100) and coins `coinsPerLevel x level` like every skill.

### 2.16 Anti-exploit
- Player-placed chests never count: they have no drop list at add (verified in assets and in `tryPlaceBlock`), plus the PlacedBy guard at open, plus a SPAWN without a drop list clears a stale entry. Break and replace: REMOVE drops the entry.
- Each chest, chunk and zone pays once per profile. Zone keys are global, so new worlds do not re-earn them. Chunks are capped per world. Instance and island worlds are excluded (dungeon instances would otherwise re-spawn chests under a new world name every run).
- Nothing pays while flying or in creative. Teleports pay (Skyy). `MovementStates` is client-reported: a hacked client could spoof `flying=false` (accepted for now; the server's no-/fly rule is the real guard later).
- No boosters: enforced in SkyySkills 0.4.1 code, not only by config (section 3).
- Luck and coins are given once, inside the first-open award, never while busy, into the opener's own inventory. The opened-chest record is saved within 2 s (`saveSoon`) to keep a crash-and-reopen double roll window tiny.
- Several players and one chest: each profile gets its own XP and its own roll (Wynn's per-player chest copy). Intended.
- Admin `/stash set <droplist>` makes a real loot chest (WorldEditor group only). That is the future path for hand-built island chests: builder-placed chests keep the builder's PlacedBy, which the capture records, so they are accepted.

### 2.17 Known limits (documented)
- Chests generated **before** SkyyExploration was installed are not recognised (their drop list was cleared when they rolled). New terrain works. The `stats` admin line shows the captures.
- Prefab chests with fixed preset items and no drop list (31 in 7,842 prefabs) and empty world crates or barrels do not count. Only real loot chests do.
- Flying mounts are not detected (`chunks.payWhileMounted` switch).

### 2.18 In-game test checklist (SkyyExploration)
1. Server log: `SkyyExploration ready`, no `already registered`, no WARN about the late fallback.
2. Walk into NEW terrain of a generated world. After at most 30 s: `+N Exploration XP from K new chunks`. `/explore` shows the chunk count.
3. `/fly` and fly over new land: the count does not rise. Land and walk: it rises. Creative: nothing.
4. Walk into a new region: `[Exploration] Discovered <name> ... +XP (n of 27)`. The Zones tab shows it green.
5. Find a structure chest in new terrain and open it: `Loot chest found ... +XP`. Re-open it: nothing. Break it and place your own chest there: nothing. Open a chest you placed: nothing. Open the island starter chest: nothing.
6. Chest luck: set `luck.perLevel=1.0`, run `/exploreadmin reload`, open a new loot chest: `Chest luck! Extra roll: ...` and the items are in storage first.
7. `/title`, then click Use on an earned title. Chat shows `[Wayfarer] name: msg`. `/title off` removes it. `/title zzz` shows an error. A locked title shows its requirement.
8. Profiles: create profile 2. `/explore` is empty, the title is none, chunks pay again. Switch back: the old record and title return.
9. Without SkyySkills (or with 0.4): XP still records, and the page shows `N XP waiting`. After 0.4.1 it is paid within 5 s.
10. SkyySkills `multiplier=2.0` plus `/skills reload`: the chest XP is unchanged (the Mining XP doubles).
11. Two accounts, one chest: both get XP and their own roll.
12. `/exploreadmin stats` shows registry counts. `/exploreadmin resetme` empties your record.

---

## 3. SkyySkills 0.4.1 (patch on 0.4)
- Source of truth: **`tools/skills_0_4_1_patch.py`** (the `skills_0_4_patch.py` style: `rep(old, new)` with asserted single anchors, newline-agnostic, 0.4 untouched). It writes `SkyySkills/build_skyyskills_0.4.1.py` with `VERSION = "0.4.1"` and a `0.4.1` docstring block pointing here.

### 3.1 Slot and row
- `EXTRA_ROWS` gets `("Exploration", "Exploration", "Tool_Map", "#e0a040")` appended, so **slot 13** (append-only; existing slots unchanged). Assert `len(SLOT_NAMES) == 14` and `SLOT_NAMES[13] == "Exploration"`. `must("Tool_Map")` passes (it is in Assets).
- `SkillDefs`: `EXPLORATION = 13`; `ROW_SLOTS = { 0, 1, 2, 10, 11, 12, 4, 13, 3 }` (Exploration after Acrobatics, class row last); `PERK_SLOT = { 0, 1, 2, 3, 4, 10, 11, 12, 13 }`; `perkRow(13) = 8`.
- `levelsOf`: append `EXPLORATION` after `COOKING`, so `skill:<uuid>` ends `...,Cooking:3,Exploration:12,<class skills>`. `skill:fn:level` and `skill:fn:xp` answer `"Exploration"` through `indexOf` (no code change).
- Player files gain `Exploration=<xp>` and `Exploration.paid=<level>`. Old files load with 0. **Never downgrade to 0.4 after Exploration XP exists** (`snap()` drops unknown keys on save).

### 3.2 XP grant, boosters bypassed (code-enforced)
- `SkillDefs.boostable(int s)` returns `s != EXPLORATION`.
- `BridgeXp.offer`: `long amt = SkillDefs.boostable(slot) ? SkillCfg.scaled(base) : base;` and the tree boost line only runs `if (SkillDefs.boostable(slot) && (!grant || SkillBonus.grantBonus(slot)))`.
- `SkillBonus.xpBonus(u, s)` returns 0.0 for a non-boostable slot.
- `BridgeCfg` load: after `GRANT` is built from `bridge.addxp.skills`, set `GRANT[EXPLORATION] = ExplCfg.ENABLED` (grantable even with an old 0.4 xp.properties line). Force `BONUS_XP[EXPLORATION] = false` and `BONUS_ADDXP[EXPLORATION] = false`; if either list names it, log one WARN `Exploration never gets XP bonuses (Skyy) - ignored`.
- The block-rule parser (`block./prefix./suffix.` lines) ignores a rule naming Exploration, with a WARN. Exploration XP only arrives through `skill:fn:addxp`. The admin `/skills xp exploration <n>` stays raw.
- The per-minute bridge cap (`bridge.maxXpPerMinute`) still counts Exploration (a safety bound, not a booster).

### 3.3 Per-level reward (existing perk machinery)
- `PerkCfg.KEYS` gets `"exploration"` appended. `HP`, `STA` and `MANA` default arrays get a 9th entry: `STA[8] = 0.1`, the others 0. The existing 1 s `Perks.tick` sums it into the `skyyskill_stamina` MAX modifier. Coins per level: the generic `coinsPerLevel x level` (no change).
- New xp.properties block, appended once to an existing file with no `exploration.enabled` key (`ExplCfg.ensureDefaults`, the `AlchCfg` pattern); `/skills reload` re-reads it; the code defaults are the same numbers:
```
# ---------- Exploration (SkyySkills 0.4.1) ----------
# Comments must stay on their own lines.
# Exploration XP only comes from other mods through skill:fn:addxp (SkyyExploration: loot chests, new chunks, zones).
# It never gets the xp multiplier or any skill-tree / booster bonus (Skyy). exploration.enabled=false refuses it.
exploration.enabled=true
perk.exploration.staminaPerLevel=0.1
# Acrobatics skill-tree dodge nodes (SkyyTrees 0.2, skill:bonus dodge.acrobatics) add at most this much dodge push.
acro.treeDodgeMax=0.25
```

### 3.4 Acrobatics tree reader (dodge)
- `Acro.boost`: `f = dodgeBonus(level) + treeDodge(u)`, where `treeDodge = min(max(SkillBonus.sum(u, "dodge.acrobatics"), 0), AcroCfg.TREE_DODGE_MAX)`. It applies only while `acro.dodgeBoost=true`. A level-0 player with tree points still gets the tree part.
- Speed, jump and fall from the Acrobatics tree need **no** Skills change: they arrive as the movement protocol source `trees.acrobatics`, and MoveSync (the applier) and the `stat:owner:fallDamage` owner already sum every source.

### 3.5 UI
- **/skills page:** the root `#SkyySkills` grows to Height **690** (9 rows: 8 x 58 + Acrobatics 72, plus 4 px gaps). The footer text gains `- explore`.
- **Tree buttons:** `SkillBonus.treeName(ACROBATICS) = "acrobatics"` and `treeName(EXPLORATION) = "exploration"`. New `SkillBonus.treeAvailable(slot)` = `treesOn()` and (bridge `tree:names` is a String containing the slot's LABEL; or, when `tree:names` is absent (SkyyTrees 0.1), slot in Mining/Foraging/Farming/Cooking). The row `Tree` button and the Stats page `Skill tree` button use `treeAvailable`. The button ids stay `#SkyySkTree<i>`, payload `sktree<slot>`.
- **Stats page (Exploration):**
  - `how(13)` = `"Earn XP by exploring - open loot chests for the first time - walk into new chunks (not while flying) - discover Hytale's zones. Once each per profile. XP boosters never apply"`.
  - `lines()`: row 8 gives `"+X max Stamina"` via `stat(STA)`, plus the `skill:stats:Exploration` hook lines (SkyyExploration), plus on `!next` the line `"Exploration XP ignores the xp multiplier and every skill-tree or booster bonus"`. When the hook is absent: `"Install SkyyExploration to earn Exploration XP"`. The coins line is generic.
- **Stats page (Acrobatics):** `treeLine` for Acrobatics reads `move:<uuid>["trees.acrobatics"]` (speed, jump, fallDamage) and `dodge.acrobatics`: `"Skill tree: +5% speed, +0.2 blocks jump, -5% fall damage, +10% dodge push"`.
- The skill argument help in `/skills stats|top|xp` lists `exploration` (the 3+ letter prefix `exp` already resolves).

### 3.6 Test checklist (SkyySkills 0.4.1)
1. `/skills`: 9 rows, Exploration (map icon) after Acrobatics, no overlap at the bottom. With SkyyTrees 0.2, `Tree` buttons on the Acrobatics and Exploration rows open `/tree acrobatics` / `/tree exploration`.
2. `/skills xp exploration 1175` gives level 5, coins for levels 1-5, and max Stamina +0.5 (stamina bar or `/skills stats exploration`).
3. `/skills stats exploration` shows `+0.5 max Stamina`, the SkyyExploration lines, the no-boosters line, and next level `+0.1 max Stamina` + coins.
4. `multiplier=2.0`, then `/skills reload`: SkyyExploration XP is exact, Mining is doubled. Add `Exploration` to `bridge.bonus.xpSkills`, then reload: one WARN, still exact.
5. An existing 0.4 xp.properties gets the Exploration block appended once (restart twice: not duplicated).
6. Profiles: Exploration XP is per profile. `/skills top exploration` works.
7. Dodge with Acrobatics tree dodge nodes: a longer push. With `acro.dodgeBoost=false`: no push.

---

## 4. SkyyTrees 0.2 (on 0.1)
- Source of truth: **`tools/trees_0_2_patch.py`** (asserted `rep` anchors on `SkyyTrees/build_skyytrees_0.1.py`, which stays untouched). It writes `SkyyTrees/build_skyytrees_0.2.py` with `VERSION = "0.2"`.

### 4.1 Template changes (generic)
- `TREES += ["Acrobatics", "Exploration"]`, `TCOLOR += ["#c8a0ff", "#e0a040"]`, `NT = 6`, `N = 72`. Replace every literal 48: `TreeData.lv/off` arrays, `TreeCfg.EN`/`LIST` arrays, the asserts, and the `"of 48 nodes"` text (use `TreeDefs.N`). Assert `len(ROWS) == 72` and unique ids.
- `KINDS += ["RSPD", "RJMP", "RFALL", "RDODGE", "LUCK", "SCAV", "SOON"]` (existing kind numbers unchanged).
- **Per-tree Dust rate:** `dust.xpPerDust.<Tree>` keys override `dust.xpPerDust` (defaults: Acrobatics 2, Exploration 5; others use the global 10). `TreeCalc.dustEarned(int t, long xp)`; every caller passes the tree. Texts show the tree's own rate. Reason: Acrobatics XP is capped at 240/min and Exploration is one-time, so at 10 XP per Dust neither tree could be levelled.
- **`SOON` kind (placeholder card):** never unlockable, never counted in "nodes on", state "Coming later" (card `#1a1a24` / `#8890a0`). Detail panel: `"Draft - Skyy designs the rest of the Exploration tree later"`. Buy button disabled: `"Coming later"`. No node lines in trees.properties.
- **New bridge key `tree:names`** = `"Mining,Foraging,Farming,Cooking,Acrobatics,Exploration"` (put in setup, removed in shutdown). SkyySkills 0.4.1 and SkyyExploration read it for their Tree buttons.
- **Page:** 6 tabs: `TextButton #SkyyTrTab0..5` Width **96** + 4 px gaps; `#SkyyTrLvl` 140, `#SkyyTrTok` 110, `#SkyyTrDust` 120 (fits the 972 px inner width). The Exploration tab's `#SkyyTrNote` reads `"Draft tree - Skyy designs the rest later - nothing here boosts Exploration XP"`.
- `/tree` help and the usage variant accept `acrobatics|exploration` (prefixes `acr`/`exp`). The ctor description string is updated. The commands keep the Adventurer group.
- Per profile: unchanged (`players/<pkey>.properties`, `Acrobatics.<Id>=level`, `Exploration.<Id>=level`, `.off`, `.respecAt`).

### 4.2 Acrobatics tree (12 nodes, verified hooks only)
| S | Tier | Id | Name | Icon | Kind | max | per | At max | Hook |
|---|---|---|---|---|---|---|---|---|---|
| 1 | I | RSpeed | Fleet Foot | Armor_Leather_Light_Legs | RSPD | 25 | 0.004 | +10% speed | move protocol `trees.acrobatics` flat speed |
| 2 | I | RJump | Spring Step | Ingredient_Feathers_Light | RJMP | 20 | 0.02 | +0.4 blocks | flat jump (blocks) |
| 3 | I | RStamina | Second Wind | Food_Bread | STA | 15 | 0.2 | +3 max Stamina | `skyytree_stamina` MAX modifier (**required Stamina node**) |
| 4 | II | RFall | Soft Landing | Glider | RFALL | 10 | 0.01 | -10% fall damage | flat fallDamage (negative) |
| 5 | II | RDodge | Quick Dodge | Ingredient_Feathers_Blue | RDODGE | 10 | 0.01 | +10% dodge push | `skill:bonus` `dodge.acrobatics` (Skills 0.4.1) |
| 6 | III | RStamina2 | Marathon | Food_Pie_Apple | STA | 15 | 0.2 | +3 max Stamina | `skyytree_stamina` |
| 7 | III | RSpeed2 | Sprinter | Armor_Leather_Light_Legs | RSPD | 10 | 0.005 | +5% speed | move protocol |
| 8 | IV | RJump2 | High Jumper | Ingredient_Feathers_Red | RJMP | 10 | 0.03 | +0.3 blocks | move protocol |
| 9 | IV | RFall2 | Featherfall | Ingredient_Feathers_Dark | RFALL | 10 | 0.005 | -5% fall damage | move protocol |
| 10 | V | RStamina3 | Endurance | Food_Wildmeat_Cooked | STA | 20 | 0.1 | +2 max Stamina | `skyytree_stamina` |
| 11 | V | RDodge2 | Evasion | Glider | RDODGE | 10 | 0.01 | +10% dodge push | `dodge.acrobatics` |
| 12 | VI | RSpeed3 | Windrunner | Armor_Leather_Light_Legs | RSPD | 5 | 0.01 | +5% speed | move protocol |

- Totals at max: +20% speed, +0.7 blocks jump, -15% fall damage, +20% dodge push (Skills cap `acro.treeDodgeMax` 0.25), +8 max Stamina. The template maxima and tiers are unchanged. The build checks every icon with `must()`; swap an icon if an id is missing.
- `TreeFx`:
  - `stats()`: `sta = MStamina + RStamina + RStamina2 + RStamina3`.
  - New `acroPost(u, v)` (called by `TreeTick` every second, right after the `trees.tools` post): source `"trees.acrobatics"`, entry `{layer "flat", speed Float(RSpeed + RSpeed2 + RSpeed3), jump Float(RJump + RJump2), fallDamage Float(-(RFall + RFall2))}`, all zeros removes it, never touches another source (tools/skyymove.py rule 1). SkyyTrees only posts; SkyySkills 0.2+ / SkyyAccessories 0.3+ apply it, and the fallDamage owner (SkyySkills) sums it.
  - `bonusMap`: `putNZ(m, "dodge.acrobatics", RDodge + RDodge2)`.
  - `clearOne`: also removes `move:<uuid>["trees.acrobatics"]`.
- Acrobatics fall XP interplay: more fall reduction means a bigger fall is needed to take the 1+ damage that pays XP. That is why fall nodes total only 15%, with Skills' -50% at level 100 (multiplier 0.35).

### 4.3 Exploration tree (SMALL first draft, clearly marked)
| S | Tier | Id | Name | Icon | Kind | max | per | At max | Hook |
|---|---|---|---|---|---|---|---|---|---|
| 1 | I | EHeart | Wanderer's Heart | Plant_Fruit_Apple | HP | 25 | 0.4 | +10 max Health | `skyytree_health` (**required Health node**) |
| 2 | I | ELuck | Treasure Sense | Rock_Gem_Ruby | LUCK | 20 | 0.005 | +10% chest luck | `tree:fn:bonus("Exploration.ELuck")` read by SkyyExploration 2.4 |
| 3 | I | EScav | Scavenger | Ingredient_Bar_Gold | SCAV | 15 | 0.01 | 15% chance: coins = 10 x Exploration level on a first-opened loot chest | `tree:fn:bonus("Exploration.EScav")`, SkyyExploration 2.4b, `coins:fn:add` |
| 4 | II | EHeart2 | Hearty Wanderer | Plant_Fruit_Berries_Red | HP | 10 | 1.0 | +10 max Health | `skyytree_health` |
| 5-12 | II-VI | ESoon5..ESoon12 | Coming later | Deco_Scroll | SOON | template max | 0 | - | none |

- `TreeFx.stats()`: `hp = FVigor + AHearty + CFed + EHeart + EHeart2`.
- Nothing in this tree posts `xp.exploration`, and SkyySkills 0.4.1 would ignore it anyway.
- `"Wanderer's Heart"`: the apostrophe is fine in a label (the node-card name goes through `safe()`; no comma or colon). The build asserts that `,` and `:` are absent.
- Draft Dust cost at 5 XP/Dust: about 989k Dust, which is about 4.9M Exploration XP for the 4 nodes (reachable around level 25-27).

### 4.4 Test checklist (SkyyTrees 0.2)
1. `/tree acrobatics` and `/tree exploration`: 6 tabs fit on one row, 12 cards per tree, Exploration S5-S12 show "Coming later" and cannot be bought.
2. Buy Second Wind 1: max Stamina +0.2 within 1 s (it survives relog; respec removes it).
3. Fleet Foot 10 (use `debug.extraTokens`/`extraDust`): visibly faster sprint. `/skills stats acrobatics` shows the `Skill tree:` line.
4. Spring Step: a higher jump. Soft Landing: less fall damage (a known drop height).
5. Quick Dodge: a longer dodge push (needs SkyySkills 0.4.1).
6. Treasure Sense 20: `/explore` chest luck shows `+ tree 10%`. Scavenger procs pay coins.
7. Wanderer's Heart: max Health +0.4 per level.
8. Profile switch: the other profile's trees apply within 1 s. Logout: no stale `trees.acrobatics` source (other players unaffected).
9. With SkyySkills 0.4 (not 0.4.1): the Exploration tab shows level 0 and says it needs SkyySkills 0.4.1; dodge nodes do nothing.

---

## 5. Cross-mod contract summary (new or changed this round)
| Key | Writer | Reader(s) | Shape |
|---|---|---|---|
| `skill:fn:addxp` skill `"Exploration"` | SkyySkills 0.4.1 | SkyyExploration | `Object[]{UUID, "Exploration", Long, "exploration", pkey}` -> Boolean; boosters bypassed |
| `skill:<uuid>` `Exploration:<lvl>` | SkyySkills 0.4.1 | HUD / Menu later | String |
| `skill:stats:Exploration` | SkyyExploration | SkyySkills 0.4.x Stats page | `Function(Object[]{UUID, Integer, Boolean}) -> List` |
| `skill:bonus:<uuid>["trees"]` + `dodge.acrobatics` | SkyyTrees 0.2 | SkyySkills 0.4.1 | Double fraction |
| `move:<uuid>["trees.acrobatics"]` | SkyyTrees 0.2 | SkyySkills / SkyyAccessories appliers | `{layer flat, speed, jump, fallDamage}` |
| `tree:fn:bonus` `Exploration.ELuck` / `.EScav` | SkyyTrees 0.2 | SkyyExploration | Double |
| `tree:names` | SkyyTrees 0.2 | SkyySkills 0.4.1, SkyyExploration | String comma list |
| `explore:<uuid>`, `explore:title:<uuid>`, `explore:fn:title` | SkyyExploration | HUD / Party / Menu later | String / String / Function |

**Deploy pairing (for the round's HANDOFF entry):** SkyyExploration 0.1 + SkyySkills 0.4.1 + SkyyTrees 0.2 go together. `tools/deploy_set.py` SET: add `("SkyyExploration", "0.1")`, set Skills to `0.4.1` and Trees to `0.2`. Each mod still loads alone. TEST-CHECKLIST gets a new section with 2.18, 3.6 and 4.4, riskiest first: chest capture ordering, the chat prefix, the Stamina modifiers.

## 6. NEEDS A TEST (engine pieces verified, behavior not seen in game)
1. `ChestSpawnSys` ordered BEFORE `StashPlugin$StashSystem` sees the drop list on freshly generated chests (the capture counter in `/exploreadmin stats` must rise while exploring new terrain).
2. `UseBlockEvent$Post` fires for `Open_Container` chests (the 1 s window scan is the backup).
3. The chat prefix survives other chat mods (nhulston Essentials inside Skyys-Modpack replaces the formatter at NORMAL; we wrap later, at 30000).
4. `getCurrentZone()` returns the Zone1 regions in the default world, and `MovementStates.flying` is true under `/fly` (SkyyEssentials) and in creative flight.
5. The Skills / Trees StaticModifier Stamina bonuses show on the stamina bar (vanilla base 10).
