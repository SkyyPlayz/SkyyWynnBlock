# Hytale 0.7.0 port (release, 2026-10-12)

`python tools/ci/crosscheck.py` against the 0.7.0 release jar (installed 2026-10-12 17:58): **NOT READY, 39 fails in 11 mods** (all
ACCESS = a called engine method no longer exists; classes still load, the feature throws NoSuchMethodError when that line runs).
Earlier pre-release audits: research/PreRelease-Compat-Report.md, research/PreRelease-Compat-Audit-1002.md (0.7.0-pre.4: only 3
methods); the final release changed much more (WorldChunk block access, PageManager).

## Fails per mod

```
      1 SkyyArmory
      2 SkyyBank
     11 SkyyExploration
      3 SkyyGatherProbe
      1 SkyyGear
      9 SkyyIslands
      4 SkyyMenu
      5 SkyyMerchants
      1 SkyyMobs
      1 SkyyProfiles
      1 SkyyWorldGen
```

## Removed method -> what 0.7 has (from the 0.7 jar by reflection)

| Removed (calls) | 0.7 replacement to use |
|---|---|
| PageManager.handleEvent (6) | handleLegacyCustomPageEvent(Ref, Store, ...) |
| PageManager.clearCustomPageAcknowledgements (4) | clearLegacyCustomPageAcknowledgements() |
| ISpawnProvider.getSpawnPoint(World, UUID) (4) | getSpawnPointAsync(World, UUID) -> CompletableFuture<Transform> (or getSpawnPoints()) |
| World.getChunkIfLoaded / getChunkAsync (6) | chunk access moved to the ChunkStore / ChunkGrid ECS: World.getChunkStore() + WorldChunk.getComponentType() - needs a probe of ChunkGrid |
| WorldChunk.getBlock / getBlockType / getHeight / getFluidId / setBlock / breakBlock / getBlockChunk / getBlockComponentEntity (14) | gone from WorldChunk - find the 0.7 block accessors on ChunkGrid / BlockChunk / sections (probe) |
| BlockChunk.getEnvironment(III) (3) | readEnvironmentRuns(int, int, EnvironmentRunCursor) |
| ChunkLightingManager.invalidateLightInChunk (1) | invalidateLightInChunkSection(s)(ChunkGrid, ...) / invalidateLightAtBlock |
| CombatTextUpdate.<init> (1, SkyyGear crit popup) | CombatTextUpdate(float, String, Color) |

## Probe 2026-10-13 (reflection on the 0.7 release jar): where block access went

Block reads / writes are no longer methods on WorldChunk; they go through the ChunkStore ECS. Leads for the port builders (read the
bytecode of these with javassist, read only, before writing code):
- **Write a block:** `universe.world.chunk.BlockOperations.setBlock(ChunkStore, Ref<ChunkStore>, x, y, z, blockId, BlockType, ...)`
  (static; a second overload takes the ChunkSection + BlockSection directly). Replaces WorldChunk.setBlock / breakBlock.
- **Read a block id:** `builtin.adventure.worldevents.condition.spawner.Spawner.getBlockId(x, y, z, ChunkStore)` (static) is a ready
  reference implementation of "block at world x,y,z"; `universe.world.accessor.BlockReader.getBlock(x,y,z)` /
  `SectionReader.getBlock + getEnvironment(x,y,z)` are the reader interfaces; `server.spawning.util.SpawnPositionChunkCache.getBlockId`
  another user.
- **Height:** `BlockChunk.setHeightmapColumn(HeightmapColumn)` -> `HeightmapColumn.getHeight(x,z)` (IHeightmap: Legacy / Tree).
- **Fluid:** `chunk.section.FluidSection.getFluidId(x,y,z)` / `getFluid` / `setFluid`.
- **Environment:** `SectionReader.getEnvironment(x,y,z)` or `BlockChunk.readEnvironmentRuns(...)`.
- **Chunk lookup:** `World.getChunkStore()` (a ChunkGrid) + `WorldChunk.getComponentType()`; find the "chunk ref at block / index"
  method on ChunkGrid (pre-release audit: `getChunkSectionReferenceAtBlock`, `getStore` moved to ChunkGrid).
- **Lighting:** `ChunkLightingManager.invalidateLightInChunkSection(s)(ChunkGrid, ...)` via `World.getChunkLighting()`.
Raw lists: tools/dev/scratch/api07/ (local only).

## Full fail list

```
FAIL ACCESS SkyyBank com.skyy.bank.BankPage -> entity.entities.player.pages.PageManager.handleEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/CustomPageEvent;)V: no such method
FAIL ACCESS SkyyBank com.skyy.bank.BankPage -> entity.entities.player.pages.PageManager.clearCustomPageAcknowledgements()V: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.FillTask -> universe.world.chunk.WorldChunk.getBlockComponentEntity(III)Lcom/hypixel/hytale/component/Ref;: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.FillTask -> universe.world.chunk.WorldChunk.setBlock(IIILjava/lang/String;)Z: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.FillTask -> universe.world.chunk.WorldChunk.getBlock(III)I: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.HubCmd -> universe.world.spawn.ISpawnProvider.getSpawnPoint(Luniverse/world/World;Ljava/util/UUID;)Lcom/hypixel/hytale/math/vector/Transform;: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.IslandBuild -> universe.world.World.getChunkAsync(J)Ljava/util/concurrent/CompletableFuture;: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.RelightNow -> universe.world.lighting.ChunkLightingManager.invalidateLightInChunk(Luniverse/world/storage/ChunkStore;II)Z: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.RelightNow -> universe.world.World.getChunkIfLoaded(J)Luniverse/world/chunk/WorldChunk;: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.TintFix -> universe.world.chunk.WorldChunk.getBlockChunk()Luniverse/world/chunk/BlockChunk;: no such method
FAIL ACCESS SkyyIslands com.skyy.islands.TintFix -> universe.world.World.getChunkIfLoaded(J)Luniverse/world/chunk/WorldChunk;: no such method
FAIL ACCESS SkyyGear com.skyy.gear.GearCrit -> com.hypixel.hytale.protocol.CombatTextUpdate.<init>(FLjava/lang/String;)V: no such method
FAIL ACCESS SkyyMenu com.skyy.menu.MenuPage -> universe.world.spawn.ISpawnProvider.getSpawnPoint(Luniverse/world/World;Ljava/util/UUID;)Lcom/hypixel/hytale/math/vector/Transform;: no such method
FAIL ACCESS SkyyMenu com.skyy.menu.MenuPage -> entity.entities.player.pages.PageManager.handleEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/CustomPageEvent;)V: no such method
FAIL ACCESS SkyyMenu com.skyy.menu.MenuPage -> entity.entities.player.pages.PageManager.clearCustomPageAcknowledgements()V: no such method
FAIL ACCESS SkyyMenu com.skyy.menu.PageGuard -> entity.entities.player.pages.PageManager.handleEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/CustomPageEvent;)V: no such method
FAIL ACCESS SkyyProfiles com.skyy.profiles.ProfSwitch -> universe.world.spawn.ISpawnProvider.getSpawnPoint(Luniverse/world/World;Ljava/util/UUID;)Lcom/hypixel/hytale/math/vector/Transform;: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.AdminPage -> entity.entities.player.pages.PageManager.handleEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/CustomPageEvent;)V: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.AdminPage -> entity.entities.player.pages.PageManager.clearCustomPageAcknowledgements()V: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.ExGuard -> entity.entities.player.pages.PageManager.handleEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/CustomPageEvent;)V: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.ExplorePage -> entity.entities.player.pages.PageManager.handleEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/protocol/packets/interface_/CustomPageEvent;)V: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.ExplorePage -> entity.entities.player.pages.PageManager.clearCustomPageAcknowledgements()V: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.LgEng -> universe.world.World.getChunkIfLoaded(J)Luniverse/world/chunk/WorldChunk;: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.LgEng -> universe.world.chunk.WorldChunk.getBlockType(III)Lasset/type/blocktype/config/BlockType;: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.LgEng -> universe.world.chunk.WorldChunk.getHeight(II)S: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.LgEng -> universe.world.chunk.WorldChunk.getFluidId(III)I: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.LgEng -> universe.world.chunk.WorldChunk.setBlock(IIILjava/lang/String;)Z: no such method
FAIL ACCESS SkyyExploration com.skyy.explore.LgEng -> universe.world.chunk.WorldChunk.breakBlock(IIII)Z: no such method
FAIL ACCESS SkyyGatherProbe com.skyy.gatherprobe.GpTrees -> universe.world.chunk.WorldChunk.getBlock(III)I: no such method
FAIL ACCESS SkyyGatherProbe com.skyy.gatherprobe.GpTrees -> universe.world.World.getChunkIfLoaded(J)Luniverse/world/chunk/WorldChunk;: no such method
FAIL ACCESS SkyyGatherProbe com.skyy.gatherprobe.GpTrees -> universe.world.chunk.WorldChunk.getHeight(II)S: no such method
FAIL ACCESS SkyyMobs com.skyy.mobs.MobLevel -> universe.world.chunk.BlockChunk.getEnvironment(III)I: no such method
FAIL ACCESS SkyyWorldGen com.skyy.worldgen.WgOpen -> universe.world.spawn.ISpawnProvider.getSpawnPoint(Luniverse/world/World;Ljava/util/UUID;)Lcom/hypixel/hytale/math/vector/Transform;: no such method
FAIL ACCESS SkyyMerchants com.skyy.merchants.MerchEng -> universe.world.World.getChunkIfLoaded(J)Luniverse/world/chunk/WorldChunk;: no such method
FAIL ACCESS SkyyMerchants com.skyy.merchants.MerchEng -> universe.world.chunk.WorldChunk.getHeight(II)S: no such method
FAIL ACCESS SkyyMerchants com.skyy.merchants.MerchEng -> universe.world.chunk.WorldChunk.getBlockType(III)Lasset/type/blocktype/config/BlockType;: no such method
FAIL ACCESS SkyyMerchants com.skyy.merchants.MerchEng -> universe.world.chunk.WorldChunk.getFluidId(III)I: no such method
FAIL ACCESS SkyyMerchants com.skyy.merchants.MerchEng -> universe.world.chunk.BlockChunk.getEnvironment(III)I: no such method
FAIL ACCESS SkyyArmory com.skyy.armory.SoulDrop -> universe.world.chunk.BlockChunk.getEnvironment(III)I: no such method
```
