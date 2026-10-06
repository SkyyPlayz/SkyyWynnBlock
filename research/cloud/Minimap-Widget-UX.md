# Minimap widget UX (SkyyHud, piggybacking on BetterMap)

Cloud draft, 2026-10-06. Design only; the local session checks the engine and licences. Skyy's locks (docs/answered/ui.md, 2026-10-03): our own minimap becomes a **SkyyHud widget**, **requires BetterMap and reuses its map** (no second map generator), **DapperMap-like settings, no info panel**, creature markers optional; read the engine's own map stream, **never BetterMap's AGPL code**; defaults **round, top-right, about 160 px, north-up**; mob dots **off by default** and throttled when on.
Probe results (docs/log/2026-10.md, 2026-10-04): runtime HUD pictures **show**; the round mask is clean; the engine's map pictures are **96 px per chunk** (image scale 3.0, up to 780 colours, 12-bit palette): 81 tiles = **542 KB raw, about 200 ms on the shared scheduler thread** (DapperMap's tick ran **40-57 ms** on the world thread, hence the lag);
the client **keeps delivered pictures across world changes**; a player can have **many custom HUDs keyed by name** (so the minimap is its own HUD key, e.g. `SkyyHudMinimap`, not part of `skyyhud_main`); `MapImage` = width, height, palette (0xRRGGBBAA), bitsPerIndex, packed indices, row 0 = north; island worlds sent **0 map packets** in 9 s (map off).
Also: `research/Minimap-Research.md` (BetterMap 1.3.8 internals, the outbound-packet-tap route, what the client can draw: **no rotation, no map element**, `AssetImage` + masks). Anything not in those files is UNVERIFIED.

## 0. The widget in one picture

```
              (top-right of the screen, a movable HUD widget)
        .---------------.
       /   . . . . . . .  \        a round 160 px map, north up
      |   . . . . ^ . . .  |       ^ = your arrow (pre-rendered per heading)
      |  . party o . . . .  |      o = party member dot, * = waypoint
       \   . . . . . * . . /       a thin ring with N E S W ticks
        '---------------'
            x 1,204  z -77          (coordinates line under the map, optional; NOT an info panel)
```

## 1. What the player gets (settings, grouped like DapperMap, minus the info panel)

Skyy liked DapperMap's settings menu (Display, Markers, Position, Colours, Integrations); we keep those groups and drop **Info Panel**. Player settings live in the **SkyyHud settings page** (a "Minimap" tab) and the **HUD editor** (drag / resize); they are **per player** (not per profile).

### 1.1 Display
| Setting | Options | Default | Notes |
|---|---|---|---|
| Show minimap | on / off | on (if BetterMap is installed) | master switch; off removes the HUD key entirely |
| **Zoom (radius)** | 64 / 96 / 128 / **160** / 224 / 320 blocks | 160 | quick keys later (plus / minus) |
| **Size** | 96 - 320 px, step 16 | **160** | HUD editor can drag-resize |
| Interface scale | 0.75x - 1.5x | 1.0 | multiplies the size on screen |
| **Shape** | **Circle** / Rounded square / Square | **Circle** | a mask, no extra data |
| **Rotation** | **North up** (fixed) | north up | **the client cannot rotate HUD pictures**: the setting is shown greyed "North up (the game cannot rotate the map)" - the **arrow** rotates (see 1.4) |
| Update speed | **Smooth (0.25 s) / Normal (0.5 s) / Battery saver (1 s)** | Normal | how often the **pan and arrow** update (not tile generation) |
| Texture resolution | **Low 16 / Normal 24 / High 32** px per chunk | **Normal 24** (16 on low-end) | sharper map vs more bytes; each level uses its own tile cache |
| Opacity | 40 - 100% | 90% | |
| Border | none / thin / thick | thin | colour in 1.5 |
| Compass ring (N E S W ticks) | on / off | on | cheap, static pictures |

### 1.2 Markers
| Marker | Default | Throttle |
|---|---|---|
| **You** (arrow) | on | pan every update tick |
| **Party members** (coloured dots with the first letter) | on | 1 Hz, from `party:*` bridge (no map work) |
| **Waypoints** (BetterMap / Hytale world map markers: homes, temples, outposts, warps) | on | only when the marker list changes (diff on the packet tap) |
| **Towns / outposts / warps** (SkyyExploration discovered) | on | on change |
| **Quest targets** (SkyyQuests, later) | on | on change |
| **Death location** (last death) | on | on change |
| **Other players** (BetterMap's radar players, its privacy rules) | off | 1 Hz, max 20 |
| **Creatures / mobs** | **OFF** (Skyy's lock) | 0.5-1 Hz, **max 30**, hostile only; neutral / animals separate toggles |
| **Zone border / level hint** (a tiny "Lv 18-20" text under the ring when the zone changes) | off | on zone change |
| Marker size | small / normal / large | normal |
Each marker type has its own colour (1.5) and a **Show names on hover** is not possible (HUD has no hover): names only appear in the big map.

### 1.3 Position (HUD editor)
Placed and resized with the **SkyyHud HUD editor** like every widget: anchor (TopRight default), offset x / y, drag handles, snap to edges, a **Reset position** button, and the **layout export / import code** includes the minimap. **Auto-avoid:** if another SkyyHud widget overlaps the default top-right area, the editor shows a warning (no auto-move).

### 1.4 The arrow and heading
North-up pictures; the **player arrow** is pre-rendered in **16 heading steps** (22.5 degrees, 8 x 8 px, white outline) and swapped when the heading changes by a step: 16 tiny assets (about 100 B each), delivered once per connection, and a swap of one `AssetImage` path per update tick. A free **"rotate" mode is not offered** (it would need all tiles re-rendered per heading, like Cartographer, which is exactly the lag source).

### 1.5 Colours
Border, background fill (behind unexplored tiles), the arrow, each marker type, the ring ticks. Presets: **Vanilla** (default: the kit's frame colours), **Dark**, **High contrast**, **Gold**. Colours are `#rrggbb` pickers (a text box plus 8 swatches); no per-pixel recolouring of the map itself.

### 1.6 Integrations (the old "Integrations" group, adapted)
| Setting | Behaviour |
|---|---|
| Use BetterMap data | **required** (shown as status: "BetterMap 1.3.8 found / not found: the minimap cannot show anything"); in worlds BetterMap does not track it shows the plain engine map or "No map here" |
| BetterMap markers | on (markers already filtered by BetterMap) |
| BetterMap cave mode | follows BetterMap's state for the player (cave tiles come through the same packets) |
| Hytale world map markers | on |
| SkyWynn layers (party / explore / quests) | on |
| **No info panel** | (Skyy: not needed) |

## 2. Server Setup (admin) rows
`minimap.enabled`, `minimap.requireBetterMap` (on), `minimap.maxZoom` (320), `minimap.minInterval` (0.25 s), `minimap.maxResolution` (32), `minimap.maxMarkers` (60), `minimap.mobDotsAllowed` (on, default player off), `minimap.mobMax` (30), `minimap.mobInterval` (1 s), `minimap.otherPlayers` (off), `minimap.defaultShape` (circle), `minimap.defaultSize` (160), `minimap.tilesPerTick` (4), `minimap.allowedWorlds` (all), `minimap.disabledWorlds` (islands without map, dungeons). Times in seconds (project rule).

## 3. The tile pipeline and performance budget (the DapperMap lesson)

| Stage | Where | Budget |
|---|---|---|
| 1 Read the engine's map tiles | an **outbound packet tap** (`UpdateWorldMap`) + `getImageIfInMemory` only (never `getImageAsync`) | **no world-thread map work**; the tap only stores references |
| 2 Downscale + encode | a **dedicated worker thread** (not the shared scheduler): 96 -> 16 / 24 / 32 px per chunk, quantize to the palette (<= 64 colours), tiny **indexed PNG** (about 100-250 B at 16 px; 250-500 B at 24; 400-900 B at 32), **a few tiles per tick** (default 4, queue ordered by distance from the player) | 9.6 us to encode a tile in the probe; downscale about 50 us; **target < 0.5 ms per tick on the worker** |
| 3 Cache | hash-addressed, **shared by all players** (the tile of a chunk is the same for everyone at the same resolution); bounded LRU (2,000 tiles per resolution) | memory about 1 MB per 2,000 tiles |
| 4 Deliver | **each tile once per connection** (the client keeps pictures across world changes: delivered-hash set per player, reset only on a real re-login) | first fill (R 160 / 24 px): 121 tiles x ~350 B = **about 40 KB**; each chunk crossed = about 11 new tiles = **about 4 KB** |
| 5 Pan + arrow | the HUD update tick: **1-2 `Anchor` sets and one `AssetImage` swap** per player per tick | **<= 50 us per player per tick**, one **world-thread task per world per tick** that reads all minimap players' positions (no per-player x per-world explosion) |
| 6 Markers | party 1 Hz, waypoints on change, mobs 0.5-1 Hz max 30 | batched into the same tick |
| Total server cost target | **<= 1 ms per world tick for 20 minimap players** | DapperMap measured **40-57 ms** per tick |
| Network target | steady **< 6 KB/min** per player while walking (11 new tiles per chunk; walking speed 5.5 b/s = a chunk every 6 s) | |

### 3.1 Zoom x size x resolution (what is actually sent)
Pixels per chunk shown on screen = `32 x size / (2 x radius)`:
| Size | Radius 80 | 160 (default) | 320 |
|---|---|---|---|
| 128 px | 25.6 px / chunk | 12.8 | 6.4 |
| **160 px** | 32 | **16 (native for Low)** | 8 |
| 240 px | 48 | 24 | 12 |
The client **scales** images (sharp or blurry UNVERIFIED), so the build picks the **nearest higher resolution tier** (16 / 24 / 32) to avoid blur; the number of tiles needed (radius 64 / 96 / 128 / 160 / 224 / 320) is **25 / 49 / 81 / 121 / 225 / 441**. A zoom change reloads from the cache (no regeneration); a new resolution tier fills lazily (nearest tiles first).

### 3.2 When the map is not available
| Case | Behaviour |
|---|---|
| World with no map packets (starter island, instances) | the widget shows a **grey disc with the arrow and "No map here"** in small text (or hides, a setting `minimap.noMap=hide/show`); it never retries every tick |
| BetterMap not installed | the widget is **hidden** and Server Setup shows a red status; the Stats of why in `/skyhud` |
| Hytale `MapImage` format change | the version check fails closed: hide + log once |
| Dungeon / zone with "map off" | same as no map |

## 4. HUD integration notes
- **Own HUD key** (`SkyyHudMinimap`); the HUD framework (SkyyHud-Plan) places it in the editor like any widget, with the shared theme (vanilla frame, colours of the kit).
- Round shape: `Group { MaskTexturePath }` (the probe showed the round mask clean).
- Do **not** update the HUD more than once per `Update speed` tick (PageManager drops clicks if a page self-refreshes; HUDs are separate but keep calls low).
- Compass: the native compass already shows map markers (BetterMap radar); the minimap's ring is separate and can be turned off to avoid duplication.
- Future risk: Hytale's UI move to NoesisGUI (roster row 19) may change HUD pictures; keep the widget behind a small adapter.

## 5. Phases
| Phase | Content |
|---|---|
| 1 | tile pipeline (tap + worker + cache + deliver once), the round widget, arrow, party dots, zoom / size / shape / resolution, HUD editor placement |
| 2 | markers (waypoints, towns, death), colours + presets, ring, opacity, settings tab |
| 3 | mob dots (throttled), other players, quest targets, cave mode follow, per-world rules |
| 4 | polish: sharp scaling check, cache tuning, the NoesisGUI adapter question |

## 6. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | **Licence check**: reading the engine packet stream (not BetterMap's classes) is the plan; confirm BetterMap's licence on redistribution of anything derived; Skyy asked to **never use BetterMap's AGPL code**. |
| 2 | Whether `UpdateWorldMap` tiles are sent to a player in worlds BetterMap tracks **before** the big map is opened (the hub sent 3,209 chunks / 37 MB on join). |
| 3 | The client's scaling filter for HUD images (sharp vs blurry) and whether many `AssetImage`s in one HUD cost much. |
| 4 | **Unload / reconnect**: the probe steps 6 (reconnect) and p3resend were not run; the delivered-hash set must reset when the client cache is cleared (check a re-login). |
| 5 | Palette handling: engine tiles use up to 780 colours; indexed PNG needs <= 256 (or quantize to 64 for smaller files); check the look. |
| 6 | The cost of `RequestCommonAssetsRebuild` for each new picture (FastMiniMap sends one per first tile). |
| 7 | A keybinding for zoom (client keys are fixed; maybe a `/minimap zoom` command or a HUD button). |

## 7. Questions for Skyy
1. Default resolution **Normal 24** (a bit sharper, 40 KB first fill) or **Low 16** (smallest)? (Recommended: Normal 24, auto Low on a slow link is not detectable.)
2. Should the widget show "No map here" on the starter island and in dungeons, or hide itself?
3. Heading arrow in 16 steps is enough? (A smoother arrow needs 36 steps = 36 tiny assets.)
