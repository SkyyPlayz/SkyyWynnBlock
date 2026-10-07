# SkyyHud minimap widget - build spec (2026-10-06, rev 3)

**Rev 3 (same day, fix round after the three build critics):** a layout change re-attaches only when the drawn frame changes (size,
zoom, shape, ring on / off) - otherwise one small update (box Anchor, ring picture, dots, speed, detail); no attach before a world's
map stream started (islands: no empty disc - it attaches with the first map packet); the tap runs for every connected player (keys
only while the minimap is off) and its bound counts map pieces (2,048 per player, then keys only); the join burst's pieces inside the
player's window are kept (position read for it) and chunk (-1,-1) keeps the stream's own piece (the engine map cannot hold it); each
player encodes at the detail its tile size needs (16 / 24 / 32, up to `hud.mm.detail`, default now 32); `hud.mm.minInterval` default
0.25 s (Smooth works; faster choices hidden under a slower cap); markers / fill leftovers follow the update rate, the arrow alone
follows a turn at once, rim party dots re-pinned at every pan; the 6,000 cap counts map pieces only and tells the player once; the
budget grows with the players still filling (3-10 ms, up to 3x `tilesPerTick`, 64 max); the watchdog never doubles a stuck tick and
restarts a dead thread at most 3 times; a fast reconnect gets a new session; the Online widget's default moved to tr 8,206. Where
rev 2 text below differs, rev 3 wins.

**Rev 2 (same day, spec-critic fixes, builder):** memory (no MapImage in the shared cache, per-player references only until
encoded, unknown position at join = keys counted + images dropped, a per-connection picture cap), shared-cache correctness (key =
the CONTENT of the map piece, never the coordinates; the cache fallback only for chunks the player's OWN stream already sent -
privacy), alpha-weighted downscale, `Math.floorMod` slots, the HUD document pre-built on the minimap thread (the world thread only
hands it over), `scheduleWithFixedDelay` + per-player catch + a watchdog, a pause flag shared by `onRemove` and the minimap
thread's updates, a TIME budget served round-robin, sizes in 7 steps (all masks sent once, one rebuild), the heading formula
re-derived from the ENGINE (the old "Dir widget formula" was wrong), "BetterMap active" = the map stream was seen, a clean-room
rule. Each change is marked **(rev 2)** below; the critic's points that stay open are in section 10 / 11.

Next SkyyHud version after the SET pin 0.3.13 (call it **0.3.14**; patch script `tools/hud_0_3_14_patch.py` reading the generated
`SkyyHud/build_skyyhud_0.3.13.py`, the patch-script rule in tools/AGENT-BRIEF.md). Full round (new system, several threads, new
third-party dependency).

Inputs: docs/answered/ui.md (REQUEST / TESTED / LOCKED / ANSWERED 2026-10-03 MINIMAP lines), research/Minimap-Research.md,
research/cloud/Minimap-Widget-UX.md (cloud UX draft - this spec replaces its numbers where they differ), docs/log/2026-10.md
2026-10-03 / 2026-10-04 SkyyUiProbe 0.4 lines, `SkyyUiProbe/build_skyyuiprobe_0.4.py` (the probe code that worked),
`SkyyHud/build_skyyhud_0.3.13.py` (widget system), the probe's server log `HUD mod/logs/2026-10-04_06-06-19_server.log` lines
2363-2432, and new bare-JVM probes made for this spec (section 9, marked **NEW**).

---

## 0. For Skyy (plain words)

- The minimap is **one more SkyyHud widget**. You place it in the HUD editor like the clock or the party box, and its Settings page
  has the DapperMap-style choices (on / off, zoom, size, round or square, update speed, which dots to show). **No info panel.**
- It **needs BetterMap**. If BetterMap is not installed, the minimap simply stays off and the server log says so once. Nothing else
  breaks.
- It does **not** make its own map. It reuses the map pieces Hytale (with BetterMap) already sends to your game for the big map. It
  shrinks each piece once, on its own background thread, into a tiny picture (a few hundred bytes), sends that picture to you once,
  and then only slides the pictures around as you walk. Your game keeps the pictures even when you change worlds.
- **Why it should not lag like DapperMap:** DapperMap did its map work on the world thread (37-57 ms hiccups each time). Ours does
  zero map work on the world thread. The shrinking costs about 0.1 ms per map piece on a side thread, and while you walk it sends
  about 1-2 KB per second (the big map itself sent 13-37 MB when you joined a world in the probe).
- Default look (your answers): **round, top-right, 160 px, north-up**. The map cannot turn with you (the game cannot rotate HUD
  pictures) - your **arrow** turns instead (16 directions).
- Dots: **you** (arrow), **party members**, **waypoints / map markers** (BetterMap's and the game's, from the same map stream) are
  on by default. **Other players** off. **Mobs off** (and see question 1).

---

## 1. What the player sees and does

### 1.1 The widget
```
        .---------------.
       /  . . . . . . .  \      round 160 px (size 100%), north up
      |  . . . . ^ . . .  |     ^ = you (16 headings), o = party, * = marker
      |  . o . . . . * .  |     thin vanilla-kit ring, small N tick at the top
       \  . . . . . . .  /
        '---------------'
```
- A widget id **`Minimap`** ("Minimap") APPENDED to `Widgets.IDS` (after `Combat`), like Skills / Combat were.
- Placed, dragged, snapped, sized, exported / imported, saved in profiles and in the server default layout exactly like every other
  widget (the existing layout line `en,anchor,x,y,size,...`). **Size %** = the widget's existing size field: 100% = 160 px,
  **(rev 2) in 7 steps 50 / 75 / 100 / 125 / 150 / 175 / 200 % = 80-320 px** (the editor's Size- / Size+ move the Minimap 25 %;
  any other stored value snaps to the nearest step when it is loaded), so there are only 7 round + 7 square masks: all 14 are
  sent at the first attach of a connection with ONE `RequestCommonAssetsRebuild` (never one per size change). The clamps use the
  widget's own box (160 x 160 x size), so it never leaves the screen. **(rev 2) Default position `tr 8,40`** - right under the Zone
  widget (`tr 8,8`); `tr 8,8` would cover it.
- Unexplored / not-yet-received ground = the kit's dark panel fill (no "loading" text, no per-tick retries).
- World with no map stream (starter island, instance, map off - P5: island world 0 packets): widget hidden (question 2).

### 1.2 Player settings (the widget's Settings page, DapperMap groups minus Info Panel)
All per player, stored in the layout line (section 4.4). Rows use the kit's vanilla buttons (tools/skyyui.py), same page size rules
as the Combat / Skills settings pages.

| Group | Row | Choices | Default |
|---|---|---|---|
| Display | Show minimap | On / Off (= the widget's `en`) | On (when BetterMap is there) |
| Display | Zoom (radius) | 64 / 96 / 128 / **160** / 224 / 320 blocks (only up to the admin max) | 160 |
| Display | Size | the editor's size % (100% = 160 px) | 100% |
| Display | Shape | **Round** / Square | Round |
| Display | Rotation | "North up (the game cannot rotate HUD pictures)" - info row, no button | - |
| Display | Update speed | Smooth 0.25 s / **Normal 0.5 s** / Saver 1 s (never faster than the admin minimum) | Normal |
| Display | Ring | On / Off (the border ring + N tick) | On |
| Markers | Party members | On / Off | On |
| Markers | Map markers (waypoints, homes, warps, death, BetterMap's POIs - whatever the big map gets) | On / Off | On |
| Markers | Other players (BetterMap radar markers in the stream) | On / Off | Off |
| Markers | Mobs | On / Off - only shown when the admin allows it (phase 2, question 1) | Off |
| Markers | Marker size | Small / Normal / Large | Normal |
| Colours | Ring colour | the 13 kit colours every widget has | Default (kit frame colour) |
| Colours | Party dot colour | the 13 kit colours | Default (kit green) |
| Integrations | BetterMap | status line: "BetterMap 1.3.8 found" / "BetterMap not installed - the minimap is off" | - |

Left out on purpose: Info Panel (Skyy), rotate-with-player (impossible).
(rev 2) Also left out, each listed for Skyy (section 11) instead of hidden:
- **Texture resolution** (DapperMap Display group): admin-only (`hud.mm.detail`), because a per-player choice multiplies the pictures
  each CLIENT keeps for its whole session (section 4.4 cap) and the encode work, not because of the cache (the cache key already
  carries the detail). Question 7.
- **Opacity**: no proven HUD opacity property (UNVERIFIED); question 8 (a probe line in the next SkyyUiProbe if Skyy wants it).
- **BetterMap cave mode**: the minimap shows whatever map pieces the stream sends, so BetterMap's cave view replaces the surface
  pieces for that player with no minimap switch (a "Show cave view" row would need a cave / surface flag the stream does not
  carry). Known limitation, question 9. The Integrations row is a status line only.
- **Position / Rotation** (DapperMap groups): Position = the HUD editor (drag, Snap to, arrows); Rotation = the info row above.
- **Mobs** stay phase 2 (question 1); their row is not drawn until built.

### 1.3 Commands
`/skyyhud minimap` (alias in the existing `/skyyhud` tree) = opens the Minimap settings page; `/skyyhud minimap on|off` = the
widget's `en`. Player command rules (HANDOFF section 3): every variant `setPermissionGroups(new String[] { "hytale:Adventurer" })`.
No admin subcommand (admin settings are Server Setup rows).

---

## 2. Server Setup rows (tools/skyycfg.py, category "Minimap" under HUD, `KEEP=10`)

| Key | Label | Type | Default | Range / choices | Notes |
|---|---|---|---|---|---|
| `hud.mm.enabled` | Minimap widget | bool | on | | off = the widget is removed for everyone (HUD key removed), tap does nothing |
| `hud.mm.defaultOn` | New players see the minimap | bool | on | | only for players without the Minimap entry in their layout (rev 3: = players who never saved a HUD layout) |
| `hud.mm.maxRadius` | Largest zoom (blocks) | choice | 224 | 64/96/128/160/224/320 | 320 = up to 529 pictures in one HUD as built (client cost UNVERIFIED) |
| `hud.mm.detail` | Sharpest map detail (px per chunk) | choice | **32** (rev 3) | 16 / 24 / 32 | upper bound; (rev 3) each player gets the smallest of 16 / 24 / 32 that is at least its tile size on screen; a source tile smaller than it is used as is |
| `hud.mm.minInterval` | Fastest update (seconds) | dec (s) | **0.25** (rev 3) | 0.25-2 | caps the players' Update speed; (rev 3) choices faster than the cap are hidden; the arrow alone is not capped (one Set when the heading changes) |
| `hud.mm.tilesPerTick` | Map pieces shrunk per 0.25 s | int | **24** (rev 2) | 1-64 | count cap for one filling player, (rev 3) up to 3x (64 max) while several fill; the time budget is 3 ms + 1 ms per extra filling player (10 ms max), served round-robin (section 6) |
| `hud.mm.partyDots` | Party dots allowed | bool | on | | |
| `hud.mm.otherPlayers` | Other-player dots allowed | bool | on | | players still choose (default off) |
| `hud.mm.disabledWorlds` | Worlds without minimap | text | "" | comma list, `*` suffix = prefix match | e.g. dungeon instances |

(rev 2) `hud.mm.mobDots` is NOT a row in v1 (phase 2, question 1): a row that does nothing would mislead an admin.

Times in seconds (project rule). Binding: `field:MmCfg.<NAME>@config.properties:mm.<key>` in the existing
`Skyy_SkyyHud/config.properties` (one file). (rev 2) A key missing from an existing file means its default - the file is NOT
rewritten at start (a one-time migration would have to follow the migration rules for nothing); the kit writes a key the first
time an admin changes it; a NEW install's file is written with every key and its comment. `after=Minimap.cfgChanged` on the rows
that change what is drawn re-lays every minimap out on the next tick (live).

---

## 3. BetterMap dependency check (at start; widget off + ONE log line if missing)

- Manifest key **`dev.ninesliced:BetterMap`** (BetterMap-1.3.8.jar `manifest.json`: Group `dev.ninesliced`, Name `BetterMap`,
  ServerVersion `>=0.6.0-pre.0 <0.7.0`).
- Check (engine 0.6.8, verified by reflection for this spec): `PluginManager.get().getPlugin(new PluginIdentifier("dev.ninesliced",
  "BetterMap"))` -> `PluginBase` or null; `PluginBase.isEnabled()`; version for the log line from `getManifest()`.
- WHEN: plugin load order between SkyyHud and BetterMap is not guaranteed, so do the check **lazily once** and cache the answer for the
  server's life (a mod cannot be added without a restart). **(rev 2, as built)** at the FIRST `PlayerConnectEvent` (a PluginManager
  map read under its read lock - cheap on the event thread), so the minimap session and the tap exist BEFORE that player's first map
  burst (the burst's chunk keys are what the privacy-safe sweep may read); a PlayerReadyEvent does the same check if no connect was
  seen (plugin reload). Log exactly one line:
  `[SkyyHud] minimap: BetterMap 1.3.8 found - minimap on` or
  `[SkyyHud] minimap: BetterMap (dev.ninesliced:BetterMap) is not installed or disabled - the minimap widget stays off`.
- Missing: the Minimap widget is never attached, the tap is never registered, the editor / Settings preview show "Needs BetterMap"
  (the Party / Guild / Skills "mod absent" convention), every other widget unchanged.
- We never call a BetterMap class (AGPL - Minimap-Research.md section 5). Presence check only through the engine's PluginManager.
- **(rev 2) "found" is only the first gate.** BetterMap loaded does not mean the map is on in THIS world (its own `Enabled` /
  `allowedWorlds`, or a world with the map off). The real gate is per world: the attach needs `WorldMapManager.isWorldMapEnabled()`,
  and a minimap whose player got NO `UpdateWorldMap` within 15 s of the attach in that world is removed again (one log line per
  world name: `minimap: no map stream in world 'X' - hidden there`); the next world change tries again.
- **(rev 2) Clean room (AGPL):** the builder works ONLY from the engine jar (HytaleServer.jar) and recorded packets / logs - never
  opens the BetterMap jar. The "other players" marker rule comes from a recorded packet in game (U7), never from BetterMap's
  decompiled constants. Our jar contains no BetterMap class name; its only BetterMap string is the manifest key
  `dev.ninesliced:BetterMap`. PACK.md gets a one-line clean-room note (section 7).

---

## 4. Engine approach (with evidence)

### 4.1 Map stream source: the outbound packet tap
- `PacketAdapters.registerOutbound(PlayerPacketWatcher)` in `start()`, `deregisterOutbound` in `shutdown()` - the SkyySacks 0.7.12
  pattern; **proven in game** by SkyyUiProbe 0.4 `MapTap` (P5 counted 55 UpdateWorldMap / 3,209 chunks in 'default', 113 / 2,260 in
  'skywynn_z1', ClearWorldMap at every world change).
- Packets: `UpdateWorldMap { MapChunk[] chunks (chunkX, chunkZ, MapImage image - null image = unload), MapMarker[] addedMarkers,
  String[] removedMarkers }`, `ClearWorldMap` (sent at every world change: Universe.resetPlayer -> WorldMapTracker.clear).
- **(rev 2) The tap only queues the packet reference** (the probe's proven shape): one volatile read when no minimap runs, else
  `instanceof UpdateWorldMap / ClearWorldMap`, a ConcurrentHashMap get, an AtomicInteger bound (20,000 packets per player between
  two drains, beyond = counted as dropped) and a lock-free queue add. It never blocks, never throws, never reads the packet. Every
  0.25 s the MINIMAP thread drains the queue and does the bookkeeping, so a queued packet lives at most one tick (the hub's join
  burst - 3,209 chunks in 5.2 s - is ~150 chunks per tick, ~2 MB of 96 px pieces held for a quarter second).
- Drain, per chunk (minimap thread): the chunk key goes into the player's **streamed set** (a primitive long set, this world only:
  "the stream sent this player this chunk"); a null image removes it (and the known entry); an image is kept as a reference ONLY when
  the chunk lies in the player's **keep window** (last chunk +- (h + 2), h = the half window of section 4.5) - and only until the
  minimap thread has encoded it (then just its content key stays, a short String). **Unknown position** (join / world change: the
  burst arrives before `PlayerRef.getTransform()` is valid) = every image is dropped and only the keys are counted.
- **Sweep (rev 2, explicit):** at the attach and at every chunk crossing, every window chunk without a known entry that IS in the
  player's streamed set is taken from `world.getWorldMapManager().getImageIfInMemory(cx, cz)` (a ConcurrentHashMap read, never
  generates - probe ENGINE FACT; P2 in game took all 81 tiles from it). **Never `getImageAsync`.** A chunk the player's own stream
  never sent is NEVER read from the engine cache: that cache holds the whole generated map, so reading it would show unexplored
  ground and bypass what BetterMap lets this player see (critic B6). The sweep counts its misses (after BetterMap's `clearImages()`
  the cache is empty until the engine regenerates - a slow fill to expect, visible in the log line).
- Keep window == trim window: an entry outside it is removed at every chunk crossing, so an out-of-window change can never leave a
  stale piece (the next visit sweeps the engine's current piece).
- Markers: added / removed ids into a per-player map (minimap thread, from the drain); `ClearWorldMap` clears the streamed set, the
  known entries and the markers.

### 4.2 Tile sizes: what the engine actually sends (NEW finding)
- Vanilla 0.6.8 world maps: `GeneratorChunkWorldMap.getWorldMapSettings()` and `ChunkWorldMap.getWorldMapSettings()` both build
  `new WorldMapSettings(null, 3.0f, 2.0f, 3, 32, ...)` -> **imageScale 3.0 = 96 x 96 px per chunk** (bytecode, this spec) - exactly what
  the probe measured (BetterMap was OFF in "HUD mod": its config.json `"dev.ninesliced:BetterMap": { "Enabled": false }`).
- **BetterMap ON**: `ExplorationListener.onPlayerJoinWorld` / `onPlayerReady` -> (only if `isTrackedWorld`) ->
  `WorldMapHook.hookWorldMapResolution(world)` sets the manager's `WorldMapSettings.imageScale` by reflection to the MapQuality scale
  (`ModConfig$MapQuality.<clinit>`: LOW 0.25 / **MEDIUM 0.5** / HIGH 1.0) and calls `clearImages()`. The engine reads `getImageScale()`
  in `WorldMapManager.flushGenerationQueue` and `WorldMapTracker.loadImages / loadWorldMap / processPendingReloadChunks`.
  -> In BetterMap's tracked worlds (default MEDIUM) the tiles are **16 x 16 px** - already minimap size; only re-encoding is needed.
  In untracked worlds (BetterMap `allowedWorlds` is an exact-name list, default `["default", "world"]`) tiles stay **96 px**.
- So the pipeline must take ANY source size (8 / 16 / 32 / 96 px) and produce `min(source, hud.mm.detail)` px tiles.
- (rev 2, critic D18) The BetterMap lines above are a bytecode READING, not seen in game (U5): the sizes and the ~1.3 KB/s / ~260 B
  numbers in section 5 are ESTIMATES; the first-fill log line reports the real pieces and KB.

### 4.3 Tile cache and the downscale worker
- **Own thread**: one daemon `java.util.concurrent.ScheduledExecutorService` named `SkyyHud-Minimap` (a top-level ThreadFactory class -
  javassist: no inner classes), started at the first attach, shut down in `shutdown()`. NOT `HytaleServer.SCHEDULED_EXECUTOR` (the probe
  spent 198-215 ms there for 81 raw 96 px tiles; that executor is shared).
- One 0.25 s tick on that thread does everything except HudManager calls: drain the tap queues, pick up to `hud.mm.tilesPerTick`
  (default 8) tiles **nearest-to-a-player first**, downscale + encode, deliver, pan every player whose update interval is due.
- Downscale (pure Java, no java.awt): unpack the `MapImage` (`MapPng.unpack` of the probe: bitsPerIndex 4/8/12/16, LSB-first, row 0 =
  north), average each target pixel's source block (integer block edges `x * src / dst`, so any ratio works) **(rev 2) alpha-weighted**
  (premultiplied: RGB summed times alpha, divided by the alpha sum) and **threshold the alpha** (average >= 128 -> opaque, else fully
  transparent - so unexplored / unloaded pixels never leave dark fringes), **quantize to 5 bits per channel** (`v5 = (v * 31 + 127) /
  255`, back to 8 bits as `v5 << 3 | v5 >> 2`), every transparent pixel = the one palette entry 0x00000000; build a fresh palette
  (HashMap of the 0xRRGGBBAA keys, `Integer.valueOf` - no autoboxing), then the probe's PNG writer (indexed <= 256 colours with tRNS,
  else RGBA; Deflater + CRC32). A source no larger than the target is quantized + re-encoded only.
- **Shared cache (rev 2)** (all players): key = the CONTENT of the piece - `w x h, bits, palette length, packed length, CRC32 of the
  palette + packed bytes` + `/detail` - never `world|cx|cz` (critic B6: BetterMap sends per-player pieces - cave view, exploration
  fog - so two players can get different pieces for the same chunk, and a coordinate key would show one player's piece to the
  other). Value = the encoded picture only (`MmAsset`: name, sha256, PNG bytes). It holds **no MapImage** (critic A1: a strong
  reference would keep ~14 KB per entry alive). LRU, capacity `max(4,096, players x window slots)` (critic A5). Asset name
  `UI/SkyyHud/mm/<hash16>.png` (sha256 of the PNG, the engine's CommonAsset.hash), so identical pieces are one asset.
- Per player only small things stay: chunk key -> content key (String) for the keep window, the streamed set, the slot table.

### 4.4 Per-connection delivery
- A `CommonAsset` subclass (`MmAsset`, constructor `(String name, byte[])`, `getBlob0()` returns the kept bytes - the base class only
  keeps a WeakReference) sent to THAT player as `AssetInitialize + AssetPart + AssetFinalize` in one write (CommonAssetModule.sendAsset's
  sequence, not broadcast). **Proven in game** (P1a: picture shown, 949 B, 8 ms, no rebuild).
- **Each tile once per connection**: per-player delivered-hash set. NOT cleared on world change - **P3 proved in game** the client keeps
  delivered pictures across world changes (shown 3 times, never re-sent). Cleared on `PlayerDisconnectEvent` (reconnect behaviour
  UNVERIFIED - probe step 6 never ran - so we re-send after a reconnect: safe either way).
- `RequestCommonAssetsRebuild`: tiles never. **(rev 2)** ONE per connection, right after ALL 14 masks (7 sizes x round / square -
  a square "mask" is a plain opaque square, so both shapes clip the same proven way) were sent at the first attach. A later size
  or shape change needs no rebuild.
- **(rev 2) Per-connection cap:** a client keeps every delivered picture for its whole session (P3), so each connection gets at
  most 6,000 map pictures; past that, new pieces show the dark fill and ONE log line says so (client memory for a long session
  is UNVERIFIED - U11). The first-fill log line counts the content-hash dedup hits.
- Pictures made once per server (as MapImages, the probe's generators): the 14 masks, a ring per size and colour (drawn lazily),
  **16 arrow headings** at 32 px and the dots at 16 px (the client scales an AssetImage to its Anchor - P2 showed 96 px pieces at
  32 px), a 2 x 2 dark "not yet" picture.

### 4.5 HUD document
- Its **own HUD key `SkyyHudMinimap`** (zOrder 5, the probe's) through the engine's HudManager (`addCustomHud` / `removeCustomHud` on
  the world thread only - probe `MapAttach / MapDetach`); never inside `skyyhud_main` (that HUD's `show()` re-sends every widget on shape
  changes, which would wipe and re-append hundreds of AssetImages; probe docstring "HUD SLOT"). Re-attached on PlayerReadyEvent + 1.5 s
  like the main HUD (world change clears every registered HUD: Player.resetManagers).
- **(rev 2) No document building on the world thread** (critic C10): the minimap thread builds the document once per geometry
  (size, shape, radius, ring, marker size, the box anchor) into a `UICommandBuilder` it caches (LRU 64; every player with the same
  layout shares it; slots carry their canonical anchors and the "not yet" picture). `MmHud` overrides `show()` with
  `update(true, cachedBuilder)`, so `HudManager.addCustomHud` on the world thread only copies the cached command array and writes the
  packet. The first minimap tick after the attach sends the player's own slot anchors + pictures (one update).
- Inline markup only (HANDOFF section 2; no underscores in ids): root `Group #SkyyMmRoot { Anchor: (Full: 0); }` (a HUD root) -> box
  `#SkyyMmBox` (the SkyyHud layout anchor, Widgets.anchorSrcWH) -> clip `Group #SkyyMmClip { MaskTexturePath: <mask>; Background: <dark> }`
  (inset by the ring width) -> grid `Group #SkyyMmGrid` holding a **ring buffer** of `w x w` `AssetImage #SkyyMmT<n>` slots
  (**(rev 2)** w = 2 h + 1, h = ceil(clip / (2 t)) - 11 x 11 at the default - and `slot = Math.floorMod(cx, w) + w * Math.floorMod(cz,
  w)`: Java's `%` is negative for negative chunks), the grid spanning `2 w - 1` tile positions so it re-bases (all slot anchors) only
  every few chunks (the probe's 17 for 9) -> map-marker dots `#SkyyMmMk<n>` (40) and party dots `#SkyyMmPt<n>` (8) INSIDE the grid
  (they pan with it for free; an unused dot sits far outside the clip) -> `#SkyyMmArrow` (centre) -> `#SkyyMmRing`.
- Tile display size t = `round(clip_px * 32 / (2 * radius))` px (160 px, r 160 -> 15 px per chunk). The client scales pictures
  (blur vs sharp UNVERIFIED - U2).

### 4.6 Player marker + facing
- Position and heading from `PlayerRef.getTransform().getPosition()` and `PlayerRef.getHeadRotation().yaw()` read on the minimap
  thread - exactly what SkyyHud 0.3.13's Coords and Dir widgets do on their 1 s tick (in game since 0.2.x) - so **no world-thread
  task for positions** (better than the probe's one-read-per-world). Pan = 1 `setObject("#SkyyMmGrid.Anchor")`.
- **(rev 2) Heading index, re-derived (critic D16 - the old line was wrong twice):** the "Dir widget" is not a shipped widget (it is
  not in `Widgets.IDS`) and it reads yaw as DEGREES with yaw 0 = "S", while the ENGINE (`Transform.getDirection`, bytecode, a probe
  ENGINE FACT) takes yaw in RADIANS: direction x = -sin(yaw), z = -cos(yaw), so yaw 0 faces -Z = north and a growing yaw turns toward
  -X = west (counter-clockwise on a north-up map). The minimap therefore uses the probe's `MapGeo.bucket` maths extended to 16:
  `bearing = -yaw * 180 / PI` (degrees clockwise from north), `index = floor((bearing mod 360 + 11.25) / 22.5) % 16`, **index 0 = N,
  1 = NNE, ... 4 = E, 8 = S, 12 = W** - arrow picture k is the north arrow turned k x 22.5 deg CLOCKWISE on screen. The harness checks
  every yaw from -4 pi to 4 pi: rounded to the nearest 8-way direction it equals the probe's 8-way bucket. The direction in game is
  UNVERIFIED (U10: the probe drew its 8 arrows but nobody reported which way they pointed).
- Map orientation: row 0 of a MapImage = north (-Z); screen up = north.

### 4.7 Party and waypoint markers (cheap, in v1)
- **Party**: bridge `party:fn:members` (what the Party widget already reads) -> member UUIDs -> `Universe.get().getPlayer(uuid)`
  (PlayerRef) -> same `getWorldUuid()` as the viewer -> `getTransform()`; 1 Hz; at most 8 dots; off-screen members pinned to the
  rim (a small dot on the ring edge in their direction).
- **Map markers**: the per-player marker map from the tap (`MapMarker.id`, `transform` position, `markerImage` name): every marker
  the big map gets - BetterMap waypoints, death / spawn / POI / warp markers, its radar players - with BetterMap's privacy filters
  already applied. Recomputed only when the marker map changed or the player crossed a chunk; drawn as our own dot pictures coloured
  by kind (`markerImage` name -> kind; using the client's own marker icon assets in an AssetImage is UNVERIFIED - phase 2 nicety).
  **(rev 2, clean room)** "Other players" = markers whose `markerImage` name contains "player" (any case) - a rule from the engine's
  own marker naming, NOT from BetterMap's code; the real names are recorded in game first (U7: the first in-game session logs the
  distinct `markerImage` names once). Max 40 in view, nearest first.
- **Mobs**: NOT in v1 (needs an entity-store scan = world-thread work, DapperMap's biggest cost). Phase 2: one world-thread task per
  world per second, hostile only, max 30, only when a player turned it on and the admin allows it (question 1).

---

## 5. Performance budget (numbers)

Measured: P1a / P2 / P5 (probe 0.4 in game); **NEW** = bare JVM for this spec (scratch bench, best of 5 runs x 200 tiles,
synthetic terrain tiles calibrated against the probe's real ones: synthetic 96 px PNG 11,010 B vs real 6,691 B average, so real
sizes are ~0.6 x the synthetic ones).

| Item | Number | Source |
|---|---|---|
| Raw 96 px tile as PNG (what the probe sent) | 6,691 B avg, 81 tiles 541,975 B, ~200 ms | P2 log line 2368 |
| Downscale 96 -> 16 px + 5-bit quantize + PNG | **78 us**/tile, 427 B synthetic (**~260 B real**), <= 64 colours | NEW |
| Downscale 96 -> 24 px | 96 us, 650 B synthetic (~390 B real) | NEW |
| Downscale 96 -> 32 px | 131 us, 891 B synthetic (~540 B real) | NEW |
| Re-encode a native 16 px tile (BetterMap MEDIUM), no quantize | 18 us, 688 B (palette-heavy -> quantize it too) | NEW |
| Picture delivery overhead (3 packets) | ~110 B per picture | P1a 949 B for an 838 B PNG |
| Pan update (one Anchor set, protocol bytes) | **127 B** | NEW (CustomHud.computeSize) |
| Pan + arrow swap | 212 B | NEW |
| Chunk crossing at r 160 (pan + 11 slot anchors + 11 paths) | 1,961 B | NEW |
| Each party dot move | ~87 B | NEW (474 B for pan + 4 dots) |

Budget the build must meet (harness asserts the CPU ones on the bare JVM; the in-game log line in section 8 reports the rest):

| | Budget |
|---|---|
| World thread | **0 map work**. Only HudManager add / remove at attach / detach (+ phase 2 mobs: 1 task per world per second) |
| Tap per packet | one volatile read when off; < 5 us when on (instanceof, map put, queue add) |
| Minimap thread per 0.25 s tick | **(rev 2)** encoding stops at a **3 ms time budget** (covering every map read, CRC and encode) or `tilesPerTick` (24) pieces, whichever comes first, players served ROUND-ROBIN with an equal share among the players still filling (each player's pieces nearest first; one fast flyer cannot starve the others), the leftover going round again + pans <= 50 us per player. Harness, 20 players walking + one flying: p95 tick 3.5 ms |
| 20 players walking (all new ground, no cache sharing) | ~39 tiles/s -> ~4 ms CPU per second = 0.4% of one core |
| First fill, r 160, 160 px | 121 tiles: ~0.1 ms each -> ~12 ms of encoding = 4-5 ticks (**~1-1.5 s**), 121 x ~370 B = **~45 KB** + HUD document (~20 KB for 121 slots); 10 players joining at once share the budget: ~5-12 s for all (cache hits are free) |
| Walking (5.6 blocks/s = a chunk every ~5.7 s), Normal speed | pans 2 x 127 B/s + per crossing (11 tiles x ~370 B + 1,961 B) / 5.7 s -> **~1.3 KB/s (~80 KB/min)** |
| Standing still | **0 B/s** (pans only when the position moved >= 1 display px; arrow only when the heading index changes) |
| Server memory | **(rev 2)** tile cache max(4,096, players x slots) x ~0.4 KB (~1.6 MB at 4,096; no MapImage in it); per player: content keys for the keep window (short Strings), the streamed set (8 B a chunk), the delivered-name set, MapImage references only until encoded (one tick) |
| Compare | DapperMap: 37-57 ms world-thread ticks (log, 2026-10-03); probe raw path: 554 KB + 200 ms for one fill |

Sprinting / flying faster than the worker: tiles fill nearest first; missing ones show the dark fill until encoded (never blocks).

---

## 6. Threads and lifecycle (summary for the builder)

| Event | Thread | Work |
|---|---|---|
| `setup()` | main | config rows, commands, the disconnect listener (no thread, no tap yet) |
| PlayerReadyEvent + 1.5 s | scheduler -> world thread | SkyyHud's AttachTask (main HUD) then ONE cheap request queued for the minimap thread |
| request | `SkyyHud-Minimap` | first time: the BetterMap check (+ the tap registered only when found); gates (widget on, admin on, world not disabled, map enabled); the cached document; masks + ONE rebuild (first of the connection) -> `world.execute(MmAttach)` |
| MmAttach | world thread | `HudManager.addCustomHud` -> `MmHud.show()` = `update(true, cachedBuilder)` (no building) |
| tap callback | the writer's thread | the packet reference into the player's queue (4.1) |
| 0.25 s tick | `SkyyHud-Minimap` | drain, sweep, encode (time budget, round-robin), deliver, pan, markers; `CustomUIHud.update` from this thread (as SkyyHud's own tick does) |
| HUD `onRemove` (world change) | engine (world thread) | **(rev 2)** synchronized on the MmHud with the minimap thread's `push`: sets `gone`; a push after it is dropped, a push in flight finishes first; session paused, delivered set KEPT |
| PlayerDisconnectEvent | event thread | a request: the minimap thread drops the session, its maps and its delivered set |
| watchdog | the 1 s SkyyHud tick (shared scheduler) | **(rev 2)** a minimap thread that has not ticked for 5 s while sessions exist is replaced (one log line) |
| `shutdown()` | main | deregister tap, stop the executor, remove every minimap HUD (world thread per player, best effort) |

(rev 2, critic C11) The executor is a single daemon thread from a top-level `ThreadFactory` class, scheduled with
`scheduleWithFixedDelay` (a slow tick never queues up), the whole tick and EACH player inside it wrapped in `catch (Throwable)` with
an error counter (the first error of each kind is logged once) - one bad player can never stop the minimap for everyone.

javassist limits apply (no lambdas, generics, inner classes, autoboxing, enhanced-for, varargs); protected engine members only from a
subclass on `this` (the 0.3 IllegalAccessError lesson); the build's ACCESS AUDIT copied from the probe build.

---

## 7. What the MAIN session must add (not the builder)

1. `tools/deploy_set.py`: `PACK_THIRD_PARTY` += `"dev.ninesliced:BetterMap"` (it is installed: `UserData\Mods\BetterMap-1.3.8.jar`;
   "HUD mod" config.json has it `"Enabled": false` today - the deploy enables it). Pin SkyyHud 0.3.14.
2. `PACK.md` third-party row: BetterMap (`dev.ninesliced:BetterMap`) | Paralaxe + Theobosse (Ninesliced) | 1.3.8 | BetterMap-1.3.8.jar |
   persistent explored map, waypoints, cave view; the SkyyHud minimap reads the map it streams. Licence AGPL-3.0: install from
   CurseForge (https://www.curseforge.com/hytale/mods/bettermap), never bundled; SkyWynn never calls its code.
3. **hstats OFF**: BetterMap's `config.json` key `"hstatsEnabled": false` (ModConfig.load reads `hstatsEnabled`; default true posts
   to api.hstats.dev). The file is written by BetterMap at its first start (research: `<world>/mods/BetterMap/config.json` - confirm
   the folder after the first start). Either Skyy flips it in BetterMap's admin config in game, or the main session edits the file
   with the game closed (a write into UserData = same rule as the deploy: only with Skyy's standing deploy permission + a backup).
4. Same file, `allowedWorlds`: keep `"default"` (the hub) and add `"skywynn_z1"` (question 3) - an exact-name list, no wildcards.
5. Log line + TEST-CHECKLIST section + HANDOFF version row at deploy as usual. Optional: retire SkyyUiProbe after the widget is tested.
6. **(rev 2)** PACK.md clean-room note under the BetterMap row: "SkyyHud's minimap reads only the engine's map packets and
   WorldMapManager; it was built from the engine jar and recorded packets, never from BetterMap's code (AGPL-3.0)."

---

## 8. Harness plan (`SkyyHud/test_skyyhud_0.3.14.py`, bare JVM `-Xverify:all -XX:-UsePerfData`, TEMP in scratch; EXECUTE the paths)

1. **Encoder**: MapImages packed at 4 / 8 / 12 / 16 bits, sizes 8 / 16 / 32 / 96, random palettes up to 780 colours -> downscale ->
   PNG; decode every PNG in Python (zlib + PLTE) and compare every pixel with a Python reference box-average + 5-bit quantize. Odd
   cases: palette index out of range, short packed array, 1-colour tile (Zone 1 sent 1-colour tiles), 0-size -> refused, never thrown.
2. **Cache**: same MapImage twice = one encode; a new MapImage for the same chunk = new hash; LRU cap holds; hash = sha256 like the
   engine's CommonAsset.
3. **Delivery**: a tile goes once per connection; world change (onRemove + re-attach) does NOT re-send; disconnect + reconnect DOES;
   one rebuild after the first mask, none for tiles; the 3-packet sequence and byte counts = `computeSize`.
4. **Tap**: drive the real watcher with real `UpdateWorldMap` / `ClearWorldMap` objects (null images, 3,209-chunk bursts, markers
   added / removed); off = one read; bound respected; out-of-window chunks dropped; never throws (feed it garbage).
5. **Pan / ring buffer**: walk across every chunk border in 8 directions, teleports (re-base), all 6 zoom radii x 3 sizes; every
   visible slot holds the right chunk; only changed slots get commands; heading index for yaw -720..720 step 0.5 matches the Dir
   widget's formula.
6. **BetterMap check**: PluginManager with / without the plugin (stub PluginBase) -> widget on / off; exactly ONE log line; tap never
   registered when missing.
7. **HUD**: both keys through the real HudManager (`skyyhud_main` untouched by minimap code); HudManager calls only from the world
   thread (wrapped executor asserts); no underscore ids; document sizes for 25..441 slots logged.
8. **Layout line**: new Minimap fields round-trip; export / import code; server default layout; a 0.3.13 jar's `WLayout.parse` reads a
   0.3.14 file with the Minimap entry and every old widget intact (rollback); `/skyyhud reset` gives the default minimap.
9. **Config**: the new rows through skyycfg (`KEEP=10`), bounds, hand-edited bad values refused.
10. **Budget**: 500 tiles 96 -> 16 px in < 100 ms on the minimap thread (bench says ~40 ms); a 20-player simulated walk keeps every
    0.25 s tick within the 3 ms budget (+ pans); zero calls on a thread named like the world thread. **(rev 2)** + a heap check:
    20 simulated players walking leave < 30 MB retained and the shared cache holds no MapImage; round-robin fairness (a flyer
    does not starve a walker); the document build time per size logged.
12. **(rev 2)** Alpha: a half-transparent edge block averages without a dark fringe (Python reference, premultiplied + threshold).
    Negative chunks: walks across 0 in both axes (floorMod slots). Privacy: two players with DIFFERENT pieces for the same chunk
    each see their own; a chunk the player's stream never sent is never read from the engine cache. Race: `onRemove` interleaved
    with a tick's push (no update after onRemove). One throwing player does not stop the others; the watchdog restarts a dead tick.
11. One JVM loads every class; the probe's ACCESS AUDIT; `python tools/ci/lint.py` 0 fails; `python tools/ci/crosscheck.py --jar <jar>
    --baseline`.

Layout storage (for 8): reuse `lines` as the marker bit mask (party 1, markers 2, other players 4, mobs 8; default 3) and add a 15th
field `mm` written ONLY for Minimap when not default: `z<radius>.s<r|q>.u<250|500|1000>.g<ring 0|1>.k<marker size 0-2>.c<party colour>`
(ring colour = the existing `col` field). The builder confirms the 0.3.13 parser ignores a 15th field (it did for the 14th).
(rev 2) With a 15th field the 14th (`ocol`) is written as `def` and the 13th as `-` when the marker mask is the default 3; the
party colour `c` is a palette key (`def` = the kit green). Unknown / bad parts of `mm` fall back to their defaults one by one.

## 9. In-game test steps (Skyy; BetterMap enabled by the deploy)

1. Join the hub: the round minimap shows top-right (under the Zone name) within a few seconds (more when many players join at
   once), the real map around you, your arrow in the middle. Server log: one
   `[SkyyHud] minimap: BetterMap 1.3.8 found` line and a `minimap: first fill N pieces, X KB, Y ms on SkyyHud-Minimap` line.
2. Walk / sprint in a straight line for 30 s, then in circles: the map slides smoothly, no hitches, no blank pieces lingering more
   than a moment. Turn on the spot: the arrow turns (16 steps), the map does not.
3. `/skyyhud` editor: the Minimap box is there; drag it to another corner, resize to 50% and 200%, Settings: Zoom 64 then 224, Shape
   Square then Round, Update speed Saver then Smooth - each change shows at once.
4. Set a BetterMap waypoint near you: a marker dot appears on the minimap. Party up with a second player (if possible): their dot.
5. Teleport to Zone 1 and back to the hub: the minimap comes back each time without a long refill (pictures are kept).
6. Go to your island: the minimap hides (no map there) and comes back on return.
7. Relog: the minimap comes back (pictures re-sent once - check the log line's KB).
8. Server log after 10 min: no `Task took` lines naming SkyyHud, no SEVERE from SkyyHud. Tell me how sharp the map looks (blurry?).
9. (Optional) Disable BetterMap in the world mods, restart: no minimap, the one log line "not installed", every other widget normal.

---

## 10. UNVERIFIED (the build / test must settle)

| # | Item | Default until proven |
|---|---|---|
| U1 | Panning in game: the probe's P2 session logged **0 HUD updates** - pans were never exercised | in-game step 2 |
| U2 | Client scaling filter (sharp vs blurry) - Skyy's p2 vs p2sharp verdict never logged | 16 px tiles shown at ~16 px at default zoom |
| U3 | Reconnect keeps pictures? (probe step 6 never ran) | re-send after reconnect |
| U4 | Mask without RequestCommonAssetsRebuild; masks per size | one rebuild per new mask |
| U5 | BetterMap ON -> 16 px tiles reach the tap (bytecode says so; p4 with BetterMap on never ran) | pipeline takes any size |
| U6 | Client cost of 225-441 AssetImages in one HUD | admin max 224 |
| U7 | Radar-marker id prefix for "Other players"; vanilla marker icons usable in AssetImage | own dots; harness with recorded ids |
| U8 | Real downscaled sizes (bench used calibrated synthetic tiles) | log line reports real KB |
| U9 | BetterMap 1.3.8 async SEVERE (`PlayerRef.getComponent called async`, cave overlay) still happens - BetterMap's bug, not ours | watch the log |
| U10 | (rev 2) Arrow direction in game (engine maths: yaw radians, 0 = north, growing yaw = west) | the engine fact |
| U11 | (rev 2) Client memory / FPS with thousands of delivered pictures in a long session | cap 6,000 per connection + log |
| U12 | (rev 2) Updates from the minimap thread in the moment between the engine's UI reset and our HUD's onRemove at a world change - SkyyHud's own tick has always done the same without trouble | the pause flag |
| U13 | (rev 2) "Other players" marker names (U7) and the first in-game marker names (logged once) | rule: markerImage contains "player" |

## 11. Questions for Skyy (defaults in brackets)

1. Mob dots: ship the minimap first without mobs and add them (throttled, hostile only, max 30) after you confirm no lag?
   [yes - phase 2]
2. Worlds with no map (starter island, instances): hide the minimap, or show a grey circle saying "No map here"? [hide]
3. Add Zone 1 (`skywynn_z1`) to BetterMap's allowedWorlds so Zone 1 gets the remembered map and the small fast tiles? [yes]
4. Default zoom 160 blocks at 160 px OK (DapperMap's default was 160 blocks at 240 px)? [yes, 160 px]
5. Largest zoom players may pick: 224 blocks (safe) or 320 (up to 441 pictures - may cost client FPS)? [224]
6. Update speed default Normal (0.5 s) or Smooth (0.25 s, ~2x the pan traffic)? [Normal]
7. (rev 2) Map detail per player (16 / 24 / 32 px, like DapperMap's texture resolution) or admin-only? Per player means up to 3x the
   pictures each client keeps. [admin-only, 16 px]
8. (rev 2) Opacity: worth a probe line (a see-through minimap)? [no]
9. (rev 2) BetterMap cave view simply shows on the minimap too (no separate switch). OK? [yes]
