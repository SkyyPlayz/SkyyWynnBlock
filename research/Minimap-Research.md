# Minimap research: BetterMap + Cartographer (2026-10-03)

Request (Skyy, 2026-10-03, docs/answered/ui.md "REQUEST 2026-10-03 (Skyy): MINIMAP"): add the Cartographer minimap, but last time BetterMap + Cartographer together were
"hella laggy" because "it loads the maps twice" -> make a "Bettermaps+minimap mod that adds a minimap that piggybacks off of better maps".
Roster row 20 already plans **SkyyMap**: ONE renderer for full map + minimap + party + quest layers.

How this was researched (read-only, ideas only, nothing copied): the map mods in `UserData\Mods` were copied into a scratch folder and read
with javassist bytecode dumps (the `tools/dev/bcmod.py` method); every engine reference of each mod was link-checked against the live
`HytaleServer.jar` (0.6.8); the vanilla client UI files (`Client/Data/Game/Interface`) were read; the July world logs (the last time Skyy ran
both mods) were read; licences come from the public project pages (nothing licence-related is inside any of the archives).

---

## For Skyy (plain words)

- **BetterMap does not replace or cover the normal map.** It IS the normal Hytale map (M key), made smarter on the server: it remembers
  where you have been, adds waypoints, a waypoint bar inside the map screen, a cave view and player dots. The map pictures are still made by
  Hytale's own map maker on the server (one per world) and sent to your game in small pieces. BetterMap only decides which pieces to keep
  sending (and how sharp they are).
- **Cartographer makes a second picture of the same map.** It takes the same map pieces from Hytale's map maker, glues about 150 of them
  into one big 440 x 440 picture, compresses it as a PNG and sends the whole picture to your game again - up to once a second while you
  move - plus little pictures for the arrow and the dots. Each player's minimap also wakes up 8 times a second on EVERY world that has
  players.
- **So "it loads the maps twice" is basically right.** The map is *made* once, but your game *receives and draws* it twice (small pieces for
  the big map + big PNG pictures for the minimap). The server spends time gluing and compressing pictures, partly on the world thread: the
  July logs show Cartographer hiccups of 60 to 840 ms on the world thread. Server and game run on the same PC for you, so you feel both.
- **Cartographer is also out of date.** It was made for Hytale 0.5 (that is its last update). On today's 0.6.8 it loads with an "outdated
  mod" warning and 3 of the engine functions it calls no longer exist (its mob / creature dots break).
- **Licences:** BetterMap is open source (AGPL-3.0): fine to use in the pack, but copying its code would force that SkyWynn mod to become
  AGPL too. Cartographer is MIT (copying allowed with credit), but its design is exactly the laggy part. FastMiniMap and Wayfinder (also in
  your Mods folder) are "All Rights Reserved" (ideas only).
- **Recommendation: don't add Cartographer. Build SkyyMap 0.1 = just a minimap** that listens to the exact map pieces BetterMap already sends
  to your game (same map, same system) and shows the area around you in a HUD corner. Each map piece goes to the minimap only once, as a
  tiny picture (a few hundred bytes), instead of a big new picture every second. No second map maker, no BetterMap code inside (no licence
  trouble, and BetterMap updates cannot break it). It even shows BetterMap's cave view and waypoints, and it still works in worlds where
  BetterMap is off (it then uses the plain map). Later the same mod adds party and quest dots to BOTH maps - the roster's SkyyMap plan.
- **First step:** a small test build (SkyyUiProbe) to check that your game shows server-sent pictures in the HUD the way we need.
- **Questions for you:** (1) OK to skip Cartographer? (2) OK to do the probe, then SkyyMap 0.1? (3) Round or square minimap, which corner,
  default size? (4) Mobs on the minimap? (they cost the most - I'd leave them off) (5) BetterMap sends usage stats to its authors' stats site
  by default (hstats) - switch that off on the public server?

---

## 1. What is installed

| Mod | File in `UserData\Mods` | Author (CurseForge) | Manifest key | Manifest ServerVersion | Link check vs 0.6.8 | "HUD mod" world |
|---|---|---|---|---|---|---|
| BetterMap | BetterMap-1.3.8.jar | Paralaxe + Theobosse (team Ninesliced) | `dev.ninesliced:BetterMap` | `>=0.6.0-pre.0 <0.7.0` | 1,837 engine refs, **0 missing** | off |
| Cartographer | Cartographer-0.1.4.jar | Geminiz1978 (manifest group "Wyoba") | `Wyoba:cartographer_minimap` | `>=0.5.3 <0.6.0` | 223 refs, **3 missing** | off |
| FastMiniMap | FastMiniMap-2.4.1.jar | maksimovc | `thenexusgates:FastMiniMap` | `>=0.5.1 <0.6.0` | 159 refs, 0 missing | off |
| Wayfinder [Minimap] | x3Dev-Wayfinder-1.8.0.jar | Alexr03 | `x3Dev:Wayfinder` | `>=0.0.1` | 193 refs, **14 missing** (broken) | off |
| MultipleHUD | MultipleHUD-1.0.8.jar | Buuz135 | `Buuz135:MultipleHUD` | `>=0.5.0` | not needed on 0.6.8 | off |

- **"Last time" = Skyy's own bundle `Skyys-Modpack.jar`** (1.3.1 in July, 1.5.0 now; disabled in "HUD mod"). Its SubPlugins include
  BetterMap 1.3.7, Cartographer 0.1.4 and MultipleHUD 1.0.8. The July 3-4 server logs (game **0.5.6**) of the worlds "test all modspacks" and
  "The Pack! Me and E" show both enabled from it (stack frames `ThirdParty(Skyy:1.3.1 Skyys Modpack)//dev.ninesliced...`).
- 0.6.8 still loads plugins whose ServerVersion does not match: `PluginManager` logs per plugin "targets server version range '%s' which
  does not match the running server version" and a SEVERE "One or more plugins are targeting a different server version..." unless the JVM
  property `hytale.allow_outdated_mods` is set.
- 0.6.8 has keyed multi-HUD built in (`HudManager.customHuds`, `addCustomHud(PlayerRef, CustomUIHud)`, `CustomUIHud(PlayerRef, String key
  [, int zOrder])`). SkyyHud already uses its own key (`super(pr, "skyyhud_main")`, `SkyyHud/build_skyyhud_0.3.12.py` line 2003).
  MultipleHUD is obsolete for us.

---

## 2. BetterMap 1.3.8 - how it works

### 2.1 Replace / hide / cover the vanilla map? No: it rewires the vanilla map on the server

How the vanilla map works (engine 0.6.8):
- Per world, `WorldMapManager` (its own `TickingThread`) owns ONE generator (`IWorldMap`, normally
  `com.hypixel.hytale.server.worldgen.map.GeneratorChunkWorldMap`) and a cache of per-chunk images (`images`, `generating`,
  `generationQueue`; `getImageIfInMemory(x,z)` = no work, `getImageAsync(x,z)` = generate if missing). Unseen images are dropped after a
  keep-alive (`isWorldMapImageVisibleToAnyPlayer`).
- Per player, `WorldMapTracker` (`Player.getWorldMapTracker()`) walks a `CircleSpiralIterator` around the player within
  `getEffectiveViewRadius`, fetches images from the manager and sends `UpdateWorldMap { MapChunk[] chunks, MapMarker[] addedMarkers,
  String[] removedMarkers }` on `NetworkChannel.WorldMap` (it skips the tick while that channel is not writable). It has no "map is open"
  check: tiles stream with the map closed too.
- `MapImage` = `width, height, int[] palette, byte bitsPerIndex, byte[] packedIndices` (palette-compressed). Vanilla
  `WorldMapSettings.imageScale` = 0.5 -> 16 x 16 px per 32-block chunk.
- The client draws the tiles natively in `MapPage.ui` `#MapContainer` (masked by `MapMask.png`). There is no client-side mod.

What BetterMap changes (`dev.ninesliced.utils.WorldMapHook`, all by reflection on the vanilla objects):
- `hookPlayerMapTracker`: sets the tracker's private `viewRadiusOverride` and replaces its private `spiralIterator` with
  `WorldMapHook$RestrictedSpiralIterator`, which walks the player's EXPLORED chunks nearest-first -> the vanilla tracker keeps loading and
  sending explored chunks = the persistent map.
- `manageLoadedChunks` + `managers.ChunkStreamingManager`: computes load / unload deltas, takes the tracker's private `loadedLock`, edits its
  private `loaded` set and sends unloads as `UpdateWorldMap` with `MapChunk(x, z, null)`.
- `hookWorldMapResolution`: sets `WorldMapSettings.imageScale` to the MapQuality scale (`ModConfig$MapQuality`: LOW 0.25 / MEDIUM 0.5 /
  HIGH 1.0, chunk caps 80,000 / 25,000 / 8,000) and calls `WorldMapManager.clearImages()` - this changes the shared tiles of that world for
  every reader.
- `updateWorldMapConfigs` / `sendMapSettingsToPlayer`: edits `UpdateWorldMapSettings` (zoom `minScale` 10 / `maxScale` 256, marker and
  teleport permissions).
- **Map screen UI:** the vanilla `MapPage.ui` has a hidden `Group #ServerContent` (Top 100, Right 50, 250 x 60). BetterMap fills it through
  the anchor id `"MapServerContent"` (`UpdateAnchorUI` packet + `AnchorActionModule` handlers `bettermap_openManager`, `bettermap_openConfig`,
  `bettermap_openAdminConfig`, `bettermap_create`, `bettermap_toggleExpand`) with its waypoint bar. Vanilla uses the same slot for the creative
  hub's Return button (`builtin.creativehub.ui.ReturnToHubButtonUI`). Nothing covers or hides the map.
- **Markers:** BetterMap waypoints are vanilla `UserMapMarker`s (`managers.WaypointManager.addMarker / getUserMarkers`); death, spawn, POI and
  warp markers pass through privacy wrappers (`providers.*PrivacyProvider`); the player radar is a vanilla marker provider registered as
  `"BetterMapPlayerRadar"` (`WorldMapManager.addMarkerProvider`). All of them reach the client in the vanilla marker stream.

### 2.2 Where the data comes from
- **Surface map:** the vanilla generator, on the server, from world chunk data; cached per world, shared by all players. BetterMap does not
  generate surface tiles.
- **Cave mode (default ON):** BetterMap's own second generator. `providers.CaveModeWorldMap implements IWorldMap` + `CaveModeImageBuilder` read
  blocks (`WorldChunk.getBlock`, light levels, `FluidSection`s, `BlockType` tint / particle colours; chunks via
  `ChunkStore.getChunkReferenceAsync`) for a Y-window around the player (radius 4 chunks), build `MapImage`s and send them straight to that
  one player (`WorldMapHook.processCaveOverlayAsync` -> `lambda$processCaveOverlayAsync$4` -> `UpdateWorldMap` via `sendPacket`). They never
  enter the shared cache.
- **Saved data** (`<world>/mods/BetterMap/`): `config.json`, `player_configs/<uuid>.json`, `Data/<world>/<uuid>.bin`
  (`ExplorationPersistence`: int version, int count, count x long chunk index - e.g. 20,280 bytes = 2,534 chunks), `Data/<world>/cave-<uuid>.bin`,
  `global_waypoint_y.json`. No images are saved; tiles are regenerated by the generator.

### 2.3 Defaults and gotchas that matter for SkyWynn (from a real `config.json` + `ModConfig` constructor)
- `allowedWorlds` = `["default", "world"]`, **exact match** (`ModConfig.isTrackedWorld(name)` = `allowedWorlds != null &&
  allowedWorlds.contains(name)`, used by `listeners.ExplorationListener.isTrackedWorld`). Any other world (a hub with another name, island
  instances) gets the plain vanilla map. No wildcards.
- `hstatsEnabled: true` by default: `dev.ninesliced.hstats.HStats` posts to `https://api.hstats.dev/api/server/add-plugin` and
  `.../update-server` (switch in config / admin UI). Public server -> owner's choice.
- `mapQuality` MEDIUM, `maxChunksToLoad` 10,000, `explorationRadius` 16 chunks, `updateRateMs` 500, `radarEnabled` true,
  `caveModeEnabled` true, `locationEnabled` false.
- Thread safety: the July logs (BetterMap 1.3.7) show SEVERE `PlayerRef.getComponent(Player) called async with player in world` from
  `ExplorationManager.getAllExploredCaveChunks` <- `WorldMapHook.getHydratedSharedCaveExploredChunks` <- `processCaveOverlayAsync`
  ("The Pack! Me and E" log 2026-07-04_10-20-53 lines 2161, 2186). The same call is still in 1.3.8
  (`ExplorationManager.lambda$getAllExploredCaveChunks$0` -> `PlayerRef.getComponent`). UNVERIFIED in game on 1.3.8.
- It ships byte-identical copies of the vanilla `UserA.png`..`UserF.png` marker icons (`Common/UI/Custom/Common/`).

---

## 3. Cartographer 0.1.4 - how its minimap works

### 3.1 Pipeline (package `dev.wyoba.wayfinderminimap`, main `WayfinderMinimapPlugin`)
1. `dynamic.DynamicMinimapSession.start`: `HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate(tickSafe, 500, 50 ms)` per player;
   `tickSafe` throttles to `panIntervalMs` (default `updateSpeed` 2 -> 125 ms; 0 -> 50 ms, 1 -> 75 ms).
2. `tick()`: loops over ALL worlds; for every world with at least 1 player it posts `world.execute(...)`, which runs `renderTick` only if
   this player is in that world. Tasks per second = sessions x populated worlds x 8.
3. `renderTick` (world thread): position / yaw; `detectDeath`; `updateSelfArrow` (renders a PNG per yaw bucket and delivers it); every
   250 ms `updateMarkers` -> `DynamicEntityScanner.scan` walks the entity store for NPCs and players, `colorIcon` renders dot PNGs; every
   600 ms `DynamicMinimapRenderer.terrainSignature` hashes the in-memory map images of the whole buffer; coords / compass / clock / biome text.
4. Terrain: when the player passes 80 % of the pan margin, or the signature changed (at most every 1000 ms; 15 s warm-up),
   `scheduleTerrainRender` runs `renderTerrain(WorldMapManager, x, z, settings)` on the "CartographerMinimap-Render" thread: for every
   chunk of the buffer `getImageAsync(cx, cz).getNow(null)` (same vanilla cache; may queue generation), decode the palette (`BitFieldArr`),
   draw into a `BufferedImage` (nearest-neighbour), `ImageIO.write("PNG")`.
5. Back on the world thread: `DynamicAssetPublisher.deliver / deliverWithRebuild` wraps the PNG in a `CommonAsset` (hashed), sends
   `AssetInitialize` + `AssetPart`(s) + `AssetFinalize`, and on the first terrain of a HUD also `RequestCommonAssetsRebuild`; every frame gets
   a new asset path (frame counter); then `DynamicMinimapHud.setTerrain` sets `#WayfinderMmTerrain.AssetPath` + `.Anchor`.
6. HUD: `DynamicMinimapHud extends CustomUIHud` (key `cartographerDynamicMinimapHud`), inline markup `Group #WayfinderMmRoot { Group
   #WayfinderMmClip { MaskTexturePath: <runtime mask PNG>; Background: #0a1218(0.92); AssetImage #WayfinderMmTerrain {...} Group
   #WayfinderMmMarkers { AssetImage #WayfinderMmMk<n> ... } } }`; between renders it only pans (`setObject(...Terrain.Anchor)`).

Default sizes (`DynamicMinimapSettings` + `DynamicMinimapRenderer`): 220 px map, zoom 96 blocks radius -> 1.15 px per block, pan margin
110 px -> **440 x 440 px buffer covering about 12 x 12 chunks (144-169 vanilla tiles) per render.**

### 3.2 Why BetterMap + Cartographer = double work (the answer to Skyy's question)

| Part | One or two? | Proof |
|---|---|---|
| Surface tile generator | **One** - both use the world's vanilla `WorldMapManager` | Cartographer `renderTerrain` / `terrainSignature` take the `WorldMapManager`; BetterMap only reconfigures it (2.1) |
| Data sent to the client | **Two** - the map stream (`MapChunk` palette tiles, a few hundred bytes each, est.) AND a whole re-encoded 440 x 440 PNG per refresh (tens of KB, est.) + arrow / dot PNGs, as runtime assets | `WorldMapTracker.writeUpdatePacket` vs `DynamicAssetPublisher.deliverBytes` |
| Server-side renderer | **Two** - the vanilla generator + Cartographer's java.awt compositing + PNG encoding per player | `renderTerrain`, `toPng` |
| Client-side drawing | **Two** - native map tiles + a new big HUD texture per refresh (+ a `RequestCommonAssetsRebuild` per HUD build) | `deliverWithRebuild` |
| World-thread work | **Extra** - 8 posts/s per player per populated world, entity scans every 250 ms, hashing, PNG renders of arrow / dots, asset sends | `tick`, `renderTick`, `updateMarkers`, `updateSelfArrow` |
| BetterMap side effects | HIGH quality = 4x pixels per tile for Cartographer to decode; BetterMap's bigger view radius keeps more tiles alive | `hookWorldMapResolution` |

Log evidence (game 0.5.6, Skyys-Modpack with both enabled): every session start has one `[World|default] Task took 121-186 ms ...
dev.wyoba.wayfinderminimap.dynamic.DynamicMinimapSession$$Lambda`; the 2026-07-04 09:54 session ("test all modspacks",
`logs/2026-07-04_09-54-41_server.log`) has 8 of them: **840 ms** (line 1725) and seven of 62-92 ms. No `Task took` line names BetterMap.

### 3.3 Cartographer on 0.6.8
- Out-of-range manifest (warning, see 1). Missing engine methods: `Role.getWorldSupport()` and `Role.getMarkedEntitySupport()` (used by
  `DynamicEntityScanner.colorFor`) and `AssetModule.registerPack(String, Path, PluginManifest, boolean)` (bundled asset-editor bridge).
  `renderTick` and `updateMarkers` catch `Throwable`, so near any NPC the marker pass would abort silently every 250 ms (UNVERIFIED in game).
- The latest CurseForge file (0.1.4) targets game 0.5. Packaging: placeholder website, stray `cartographer_minimap.json(.bak)` and a stray
  per-player settings file inside the jar, and a shaded `com.azuredoom.hytale.asseteditor.runtime` library (another author's code).
- The package name and the legacy `Hud/WayfinderMinimap.ui` (header "WAYFINDER") overlap with x3Dev's Wayfinder by name, but the code and UI
  are different; no proof of a fork.

---

## 4. The other minimaps in the Mods folder (ideas only)
- **FastMiniMap 2.4.1** (All Rights Reserved): also reads the vanilla `WorldMapManager` (`getImageIfInMemory`, `getImageAsync`); renders
  128 x 128-block PNG tiles with a tile cache and per-tile signatures; content-hash asset paths; delivers each tile once per player; sends
  `RequestCommonAssetsRebuild` **only for the first tile of a session** (`FastMiniMapSession.getOrRenderTile`: `rebuild = !terrainActivated`);
  lets the client scale tiles (`tileDisplayPixels` = max(128, 128 x pixels-per-block)); public layer APIs (`FastMiniMapMobLayerApi`,
  `FastMiniMapPlayerLayerApi`, `FastMiniMapWorldMarkerApi`). Links cleanly on 0.6.8. Still a second PNG pipeline.
- **Wayfinder 1.8.0** (All Rights Reserved): no images at all - a 40 x 40 grid of solid-colour `Group` cells (1,600 cells, `.Background`
  set per update). Broken on 0.6.8 (old `MapImage.data`, `math.vector.Vector3d`, `CustomUIHud(PlayerRef)` ...).

---

## 5. Licences

| Mod | Licence and where it is stated | Depend on it at runtime and ship SkyWynn publicly? | Reuse its code? | Put it in the pack? |
|---|---|---|---|---|
| BetterMap | **AGPL-3.0**, standard text, no added exceptions (CurseForge "License"; GitHub `ninesliced/Hytale-BetterMap` `LICENSE.md`). Nothing inside the jar. | **Yes, if we only talk to the engine** (packets, vanilla tile cache, vanilla markers): no obligations at all. **Calling BetterMap's own classes** (linking or reflection into its internals) is, in the FSF's reading of the GPL family, one combined program -> that SkyWynn mod should then be released under AGPL-3.0 (source public + offered to players who use it over the network, AGPL section 13). | Only into an AGPL-licensed SkyWynn mod, keeping its notices. Practically moot: our javassist toolchain cannot compile its Java (lambdas, generics) - we would rewrite anyway. | Yes: AGPL allows redistribution with the licence and a source link. PACK.md way = server owners install it from CurseForge. |
| Cartographer | **MIT** (CurseForge "License"); no notice text in the jar | (not recommended to use) | Allowed with the MIT copyright + permission notice (credit Geminiz1978 / Cartographer). The shaded AzureDoom library is a separate work. | Allowed, not recommended (0.5 only, laggy design). |
| FastMiniMap | **All Rights Reserved** (CurseForge) | Server owners may install it themselves | No | Do not bundle |
| Wayfinder | **All Rights Reserved** (CurseForge) | - | No | No (broken on 0.6.8 anyway) |

- SkyWynn itself has no LICENSE file (default: all rights reserved). Choosing AGPL for one mod would be Skyy's call. This is not legal
  advice; the FSF view on plugins is an interpretation, not settled law.
- Side note: `Skyys-Modpack.jar` (Skyy's private bundle) repackages about 25 other authors' plugins (BetterMap and Cartographer among them;
  the others' licences were not checked here) - keep it private, never publish it.
- Side note: `research/Exploration-Research.md` line 149 lists BetterMap's `ExploredChunksTracker` under "Mods to copy from" - under AGPL that
  can only be an idea, not code (unless that mod goes AGPL).

---

## 6. What BetterMap exposes that a minimap add-on could reuse

1. **No official API, events or shared cache for add-ons** (README, CurseForge page). Its Open Collective page says: "We plan to implement a
   minimap, a webmap, a developper API and much more!" -> BetterMap may ship its own minimap / API later.
2. **Internal public classes** (callable, no contract): `exploration.ExplorationTracker.getInstance().getPlayerData(player).getExploredChunks()`
   (`ExploredChunksTracker.isChunkExplored(long)`, `getVersion()`, `forEachExploredChunk`), `managers.ExplorationManager.getAllExploredChunks(world)`,
   `managers.WaypointManager.getUserMarkers(player)`, `managers.PlayerRadarManager.getRadarData(world)`, `managers.CaveModeManager.getState(player)`.
   Robustness data point: BetterMap 1.3.7 (inside Skyys-Modpack) -> 1.3.8 kept all 653 public signatures, but 71 of 162 classes changed
   inside. Using these = the AGPL question above + breakage whenever they refactor (their planned API may restructure).
3. **Data files** (2.2): readable, undocumented binary, change with versions.
4. **The robust bridge is the engine layer that BetterMap itself feeds** (Hytale types only - survives BetterMap updates, works without
   BetterMap, no AGPL question):
   - **Outbound packet tap:** `com.hypixel.hytale.server.core.io.adapter.PacketAdapters.registerOutbound(PlayerPacketWatcher)` (or a
     `PlayerPacketFilter` that never blocks; SkyySacks 0.7.12 already uses `registerOutbound`). Per player it sees every `UpdateWorldMap`
     (tiles incl. BetterMap's cave tiles and unloads, added / removed markers) and `ClearWorldMap` - exactly what the big map receives.
   - **Shared tile cache:** `world.getWorldMapManager().getImageIfInMemory(cx, cz)` (never `getImageAsync` = never triggers generation).
   - **Markers already sent:** `player.getWorldMapTracker().getSentMarkers()` -> `Map<String, MapMarker>` (`id`, `name`, `markerImage`,
     `transform`), BetterMap's privacy filters already applied.
   - **Our own layers** (party, quests, islands): `WorldMapManager.addMarkerProvider(key, MarkerProvider)` with
     `update(World, Player, MarkersCollector)` - they appear on the big map AND come back through the tap for the minimap.
   - Risk = Hytale updates, not BetterMap updates (e.g. `MapImage` changed format between 0.5 and 0.6: Wayfinder still calls the old
     `MapImage.data`).

---

## 7. What the client can draw in a HUD (facts)
- Element types used in the client's own UI files: `Group` (1,313), `Label`, `Button`, `ProgressBar`, `DropdownBox`, `ActionButton`,
  `TextButton`, `ItemGrid`, ..., `CircularProgressBar`, `AssetImage` (2). **There is no map / minimap element and no rotation property.** The
  vanilla map view is native (`MapPage.ui #MapContainer`) and cannot be reused in a HUD, so a HUD minimap must ship its own pixels. There is no
  vanilla minimap `HudComponent` (the list has `Compass`, `Hotbar`, `ObjectivePanel`, ...); the native compass already shows map markers
  (BetterMap advertises its player radar on it).
- **Images:** `AssetImage { AssetPath: "<common asset path>" }` - vanilla uses it for Memory icons with a runtime path
  (`InGame/Pages/Inventory/Memories/Memory.ui`). Runtime PNGs: subclass `com.hypixel.hytale.server.core.asset.common.CommonAsset`
  (0.6.8 constructors `(String name, byte[])` and `(String name, String hash, byte[])`, abstract `getBlob0()`), then send
  `AssetInitialize(asset.toPacket(), size)` + `AssetPart(<= 2.5 MB pieces)` + `AssetFinalize`. Both image minimaps send one
  `RequestCommonAssetsRebuild` (FastMiniMap: first tile only, later tiles none) - its client cost is UNVERIFIED.
- Round shape: `Group { MaskTexturePath: ... }`; colour cells: `Background: #rrggbb(a)`; move / size: `Anchor`; the client scales images
  (FastMiniMap shows 128 px tiles larger) - the scaling filter (sharp or blurry) is UNVERIFIED.
- **North-up only**, unless pictures are re-rendered per heading (Cartographer pre-renders its arrow per yaw bucket).
- HUD plumbing: keyed `CustomUIHud`, `update(false, UICommandBuilder)` with `appendInline / set / setObject / remove` - fits the SkyWynn
  inline-only rule (HANDOFF section 2). Panning = 1-2 `setObject(".Anchor")` commands.
- Future risk for every HUD minimap: Hytale's UI move to NoesisGUI (roster row 19).

---

## 8. Options, ranked

Effort scale: S = config / one test session; M = one builder round; L = a few rounds; XL = a big multi-round system.

### 1st - (a, engine flavour) SkyyMap 0.1: a minimap that piggybacks on BetterMap's map stream (RECOMMENDED)
- **What:** a new mod, no hard dependency. A `PlayerPacketWatcher` on outbound `UpdateWorldMap` / `ClearWorldMap` keeps, per player, the
  `MapImage` references of a small window around the player (e.g. 9 x 9 chunks; null image = unloaded; fallback
  `getImageIfInMemory`). Each tile is turned into a small indexed PNG straight from its palette (PLTE + IDAT via `java.util.zip.Deflater` +
  `CRC32`, no java.awt), cached by content hash and shared by all players; each player gets each tile once (delivered-hash set). HUD = keyed
  `CustomUIHud` with an N x N `AssetImage` grid inside a masked `Group` (vanilla look via `tools/skyyui.py`); pan = one Anchor set; edge
  tiles swap when you cross a chunk border. Markers come from the same packets (waypoints, BetterMap radar players, our party dots). ONE
  world-thread task per world per tick reads all minimap players' positions (no per-player x per-world explosion).
- **Piggyback level:** it automatically shows BetterMap's resolution, its cave view (cave tiles come through the tap) and its markers with
  its privacy filters - without touching BetterMap's code. In worlds BetterMap does not track (2.3) it shows the plain vanilla map.
- **Performance:** zero extra tile generation; server CPU = one tiny PNG per new / changed tile (shared); network = a few hundred bytes per
  new tile per player (est.: 9 x 9 start ~20-50 KB, then ~9 tiles per chunk crossed); world thread: one small task per world per tick.
  Compare Cartographer: tens of KB per refresh (~1/s while moving) + 8 posts/s per player per populated world.
- **Effort:** M-L = one lean probe round + one full build round (new mod / new system).
- **Risks:** client behaviour with runtime assets (rebuild hitch, reconnect, cache growth - content hashes keep it bounded), scaling blur
  (pre-scale tiles 2x if needed), packet-tap thread safety (the watcher runs on whatever thread writes the packet - it must only store
  references, never block), HUD placement next to SkyyHud widgets and the compass, worlds with the map disabled (islands? UNVERIFIED),
  Hytale changing `MapImage` / `UpdateWorldMap`.

### 2nd - (c) Interim with the existing mods (until SkyyMap 0.1 is tested)
- **c1 (recommended interim):** BetterMap only, no third-party minimap; the native compass already shows map markers. Effort S, zero extra
  cost. Suggested BetterMap settings: `hstatsEnabled` false (if Skyy agrees), add the hub world name to `allowedWorlds`, keep MEDIUM.
- **c2:** if Skyy wants a minimap right now: FastMiniMap 2.4.1 instead of Cartographer (links on 0.6.8, per-tile cache, first-tile-only
  rebuild). Still a second PNG pipeline (expected lighter than Cartographer - UNVERIFIED), All Rights Reserved (install from CurseForge,
  never bundle), 0.5-targeted (outdated warning), no SkyWynn integration. Effort S + a test session.
- **c3 (not recommended):** Cartographer with knobs (slowest `updateSpeed`, smaller `sizePixels` / `zoomBlocks`, `showEntities` off; BetterMap
  LOW / MEDIUM and cave mode off). This only shrinks the double pipeline; there is no setting that makes Cartographer reuse BetterMap's
  client-side map; it still posts tasks to every populated world and has broken NPC markers on 0.6.8.

### 3rd - (b) The full SkyyMap of roster row 20 (grows out of option 1)
- 0.2: party + quest + island markers as vanilla marker providers (both maps at once). 0.3: SkyyHud widget / Settings integration.
- Only if ever needed: our own persistent exploration replacing BetterMap. That needs the same private-field reflection on
  `WorldMapTracker` (`spiralIterator` is a private final field, `loaded`, `loadedLock`) that took BetterMap ~300 commits incl. a WorldMap
  thread-crash fix in 1.3.7 (`setViewRadiusOverride` is public, persistence is not). Effort XL for that part. Benefits: island / instance
  worlds (BetterMap's exact-name `allowedWorlds`), vanilla look, one codebase, no third-party dependency.

### 4th - (d) Other routes
- **d1:** wait for BetterMap's own planned minimap / developer API, or contribute a minimap upstream (AGPL, Maven / javac build - outside our
  toolchain). Zero work now, unknown timeline, no SkyWynn layers unless their API allows.
- **d2:** a Wayfinder-style colour-cell minimap (idea only): no runtime assets at all -> no rebuild / cache risk; low resolution (24-40
  cells across), up to N x N set commands per full refresh. The fallback if the probe shows runtime images misbehave.
- **d3 (not recommended):** fork BetterMap into SkyyMap - the whole mod must be AGPL with source offered to players, needs javac / Maven
  (we have none), and every upstream fix must be merged by hand.
- **d4 (not recommended):** the literal "add-on" that calls BetterMap's internal classes - AGPL obligations + breaks on their refactors; its
  only gain (cave / exploration data) already comes through the packet tap.

---

## 9. Recommendation

1. Do **not** add Cartographer (0.5-only, broken NPC markers on 0.6.8, re-encodes a 440 px PNG about once a second, posts world tasks per
   player per populated world, logged 60-840 ms world-thread stalls).
2. Keep **BetterMap** for the big map (owner settings: hstats on/off, `allowedWorlds` incl. the hub, quality MEDIUM, cave mode on - watch the
   logs for the async SEVERE line).
3. Build **SkyyMap 0.1 = minimap only**, option 1 above, after a lean probe. Then grow it into the roster's SkyyMap (party / quest layers
   through vanilla marker providers). Full round for the build (new mod, new system).

### Probe plan (lean round, SkyyUiProbe; Skyy watches; trial features stay off by default - `skyyui.PROBED`)
- **P1** keyed `CustomUIHud` with an inline `AssetImage` showing a runtime PNG (`CommonAsset` subclass + `AssetInitialize / AssetPart /
  AssetFinalize`); variant A without, variant B with one `RequestCommonAssetsRebuild`. Skyy notes hitches or a blank image.
- **P2** a 9 x 9 grid of 16 x 16 tiles shown at 24-32 px inside a round mask; pan 4 times a second; check smoothness, blur, clipping.
- **P3** reconnect and world switch: are delivered images still shown? (if not: re-deliver on `PlayerReadyEvent`).
- **P4** the outbound tap only logs per player: `UpdateWorldMap` count, chunks, null chunks, markers - for one minute with BetterMap on and
  off (proves the piggyback and measures the stream).
- **P5** in an island world: does the world map stream at all?

### SkyyMap 0.1 sketch (for the builder; javassist rules apply)
- `MapTap implements PlayerPacketWatcher` (registered in `start()`, deregistered in `shutdown()`, the Sacks pattern): on `UpdateWorldMap`
  store `chunkIndex -> MapImage` (null = remove) in a per-player `ConcurrentHashMap`, trimmed to the window; on `ClearWorldMap` clear; copy
  added / removed markers into a per-player marker map. No locks, no allocation-heavy work.
- `TilePng`: `MapImage` palette + packed indices -> indexed PNG bytes; global LRU `hash -> bytes`; encoding off the world thread.
- `TileAsset extends CommonAsset` (`getBlob0` returns the bytes); per-player delivered set; content-hash paths under one folder.
- `MiniHud extends CustomUIHud` (key e.g. `skyymap_minimap`, own zOrder): root, masked clip group, tile grid, marker dots, arrow (8-16
  pre-rendered headings delivered once), optional coords label; element ids without underscores.
- `MiniTick`: every 200-250 ms one `world.execute` per world with minimap players -> read `TransformComponent` on the world thread -> pan,
  swap tiles, update markers; send only changes.
- Settings: Server Setup rows via `tools/skyycfg.py` (enabled by default, size px, radius chunks, corner, update ms, show markers / party /
  coords); player switches per `research/Settings-Spec.md` 1.2-1.3; `/minimap` on | off | size | corner (Adventurer permission group).
- Party dots from the existing SkyyParty bridge keys; later quest / island markers as marker providers.

### UNVERIFIED (needs the probe or a test)
- Client cost of `RequestCommonAssetsRebuild`, and whether 0.6.8 shows runtime assets without it after the first one.
- Client scaling filter for small `AssetImage` tiles.
- Runtime assets after reconnect / world switch.
- Byte sizes above (palette tiles "a few hundred bytes", Cartographer PNG "tens of KB") are estimates.
- BetterMap 1.3.8 async SEVERE still happening in game (code path still present).
- Cartographer's marker failure near NPCs on 0.6.8.
- Whether the world map streams in SkyyIslands island worlds.

---

## 10. Proof index (class#method, files, logs)
- Vanilla: `server.core.universe.world.worldmap.WorldMapManager` (`getImageIfInMemory`, `getImageAsync`, `addMarkerProvider`, `clearImages`),
  `server.core.universe.world.WorldMapTracker` (`tick`, `loadImages`, `unloadImages`, `writeUpdatePacket`, `getSentMarkers`,
  `setViewRadiusOverride`), `worldmap.WorldMapSettings` (imageScale 0.5), `protocol.packets.worldmap.{UpdateWorldMap, MapChunk, MapImage,
  MapMarker, ClearWorldMap, UpdateWorldMapVisible}`, `protocol.packets.interface_.{UpdateAnchorUI, HudComponent}`,
  `server.core.entity.entities.player.hud.{HudManager, CustomUIHud}`, `server.core.io.adapter.PacketAdapters`,
  `server.core.asset.common.CommonAsset`, `server.core.plugin.PluginManager` (outdated-plugin messages),
  `Client/Data/Game/Interface/InGame/Pages/MapPage.ui` (`#MapContainer`, `#ServerContent`).
- BetterMap: `BetterMap#setup`, `utils.WorldMapHook#{hookPlayerMapTracker, manageLoadedChunks, hookWorldMapResolution, updateWorldMapConfigs,
  sendMapSettingsToPlayer, processCaveOverlayAsync}`, `WorldMapHook$RestrictedSpiralIterator`, `managers.ChunkStreamingManager`,
  `managers.MapAnchorManager` ("MapServerContent"), `providers.{CaveModeWorldMap, CaveModeImageBuilder, PlayerRadarProvider}`,
  `configs.{ModConfig, ModConfig$MapQuality, ExplorationPersistence}`, `hstats.HStats`, `listeners.ExplorationListener#isTrackedWorld`.
- Cartographer: `dynamic.DynamicMinimapSession#{start, tick, renderTick, scheduleTerrainRender, updateSelfArrow, updateMarkers}`,
  `dynamic.DynamicMinimapRenderer#{renderTerrain, terrainSignature, toPng, pixelsPerBlock, panMarginPixels, bufferPixels}`,
  `dynamic.DynamicAssetPublisher#deliverBytes`, `dynamic.DynamicMinimapHud#{buildMarkup, setTerrain, pan}`,
  `dynamic.DynamicEntityScanner#colorFor`, `dynamic.DynamicMinimapSettings` (defaults).
- FastMiniMap: `render.FastMiniMapRenderer#{renderMapTile, resolveTile, tileDisplayPixels}`, `session.FastMiniMapSession#getOrRenderTile`,
  `asset.FastMiniMapAssetPublisher#deliverBytes`.
- Logs: `UserData/Saves/test all modspacks/logs/2026-07-03_*` and `2026-07-04_09-54-41_server.log` (lines 17, 1626, 1653, 1725);
  `UserData/Saves/The Pack! Me and E/logs/2026-07-04_10-20-53_server.log` (lines 2161, 2186).
- Reproduce: copy a jar from `UserData\Mods` into `tools/dev/scratch/<task>/`, then `python tools/dev/bcmod.py <jar> <class#method>`.

## Sources
- BetterMap on CurseForge: https://www.curseforge.com/hytale/mods/bettermap
- BetterMap source, licence, readme, changelog: https://github.com/ninesliced/Hytale-BetterMap
- BetterMap plans: https://opencollective.com/bettermap
- Cartographer on CurseForge: https://www.curseforge.com/hytale/mods/cartographer
- FastMiniMap on CurseForge: https://www.curseforge.com/hytale/mods/fast-minimap
- Wayfinder on CurseForge: https://www.curseforge.com/hytale/mods/wayfinder
