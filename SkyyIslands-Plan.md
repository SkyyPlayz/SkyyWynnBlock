# SkyyIslands — plan (research 2026-09-23, agent-verified against HytaleServer.jar)
Use the engine's own instances system: `com.hypixel.hytale.builtin.instances.InstancesPlugin`.
- Template world shipped in the jar at `Server/Instances/SkyyIsland/` (instance.bson = WorldConfig, chunks/*.region.bin, resources/*.json)
  — the same layout EndlessLeveling uses for `Server/Instances/Archangels_Sanctum/`. Build the starter island once in creative, copy its folder.
- Create/load: `InstancesPlugin.spawnInstance("SkyyIsland", "island-<uuid>", fromWorld, transform) -> CompletableFuture<World>`
  (reuses the world if `Universe.getWorld(key)` is loaded; else copies the template and calls `Universe.makeWorld(name, path, config)`).
  From scratch alternative: `WorldConfig` + `setWorldGenProvider(FlatWorldGenProvider|VoidWorldGenProvider)` + `Universe.makeWorld`.
- Persistence: `WorldConfig.setDeleteOnRemove(false)`, `setDeleteOnUniverseStart(false)`; unload when empty via
  `InstancesPlugin.safeRemoveInstance(world)` -> `WorldEmptyCondition.REMOVE_WHEN_EMPTY` (RemovalSystem does it).
- Teleport: `InstancesPlugin.teleportPlayerToInstance(ref, accessor, world, transform)` (stores a return point);
  `InstancesPlugin.exitInstance(ref, accessor)` = /hub. Raw: `Teleport.createForPlayer(world, transform)` component added on the world thread.
- Prefab paste (for later island expansions): `PrefabStore.get()` + `PrefabUtil.paste(...)`.
- Co-op invites: not in the engine; keep owner uuid -> world key + member list in `Skyy_SkyyIslands/islands/<uuid>.properties`.
- UNVERIFIED: login while the island world is unloaded (probably falls back to the default world) — test.
Spike plan: `/island` (create or load + teleport), `/hub` (exitInstance), `/island invite <player>`, `/island visit <player>`.

## 0.1 spike built 2026-09-23 (SkyyIslands/build_skyyislands_0.1.py) - bytecode-verified facts
- `instance.bson` in every reference mod is PLAIN JSON (WorldConfig codec), not BSON. Keys: WorldGen {Type: Void|HytaleGenerator...},
  SpawnProvider {Id: Global, SpawnPoint}, Instance {RemovalConditions:[{Type: WorldEmpty}]}, DeleteOnRemove, Version 4.
- `spawnInstance(asset, key, fromWorld, transform)`: if `Universe.getWorld(name)` is loaded -> returns it; otherwise it ALWAYS
  `copyAndLoadInstance` = copies the template to `Universe.validateWorldPath(name)` (worlds folder) with a fresh UUID.
  So a persisted island must be re-opened with `Universe.addWorld(name)` (checks `isWorldLoadable(name)` = folder + config.json),
  never with spawnInstance again (that would give a fresh copy). We store `world.getName()` per player.
- `teleportPlayerToLoadingInstance(ref, accessor, future, returnTransform|null, spawnTransform|null)`: null return = current
  transform; null spawn = world SpawnProvider. `exitInstance(ref, accessor)` throws IllegalArgumentException when not in an instance.
- Blocks: `world.getChunkAsync(ChunkUtil.indexChunk(cx, cz))` -> `WorldChunk.setBlock(worldX, y, worldZ, "Soil_Grass")` (world
  coords; chunk = 32 blocks, `>> 5`). Block ids = item asset file names (Soil_Grass, Soil_Dirt, Rock_Stone, Wood_Oak_Trunk,
  Plant_Leaves_Oak, Furniture_Crude_Chest_Small). setBlock runs physics via runAsync when off the world thread; we run it on-thread.
- Still unverified: folder survives unload; addWorld reload keeps blocks; login while unloaded; void death. See TEST-CHECKLIST.md.

0.4 (2026-09-23): chest filling = WorldChunk.getBlockComponentEntity(x,y,z) (live Ref; getBlockComponentHolder is a COPY) -> Store.getComponent(ref, ItemContainerBlock.getComponentType()) -> getItemContainer().addItemStack; must run on the world thread; the container exists right after setBlock. Void death = universal y<-32 kill (DamageCause.OUT_OF_WORLD), no per-world config; respawn = world DeathConfig RespawnController -> SpawnProvider.
