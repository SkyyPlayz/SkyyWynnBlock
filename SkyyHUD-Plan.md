# SKYYHUD — BUILD PLAN (working name)
*The first SkyWynn-adjacent thing we BUILD. Standalone HUD-customization mod for Hytale: testbed for our
UI framework while we wait on the NoesisGUI rework + inventory changes. 2026-09-22.*

## Ground rules (locked by Skyy)
1. **Zero external dependencies.** Any library we'd use gets bundled INTO the released jar (only EndgameAndQoL in the collection does this right — everything else that needs HyUI makes users install it separately). We don't even need a lib: our packs already drive the engine's `CustomUIHud`/`CustomUIPage` directly.
2. Widget priority: **shared-everywhere widgets first**, unique ones later.
3. Every widget individually movable/scalable/toggleable; preset bundles that can be split; **layout export/import codes**.
4. Released standalone (Mod Browser when possible) — must "just work" solo, AND slot into the future SkyWynn pack as its HUD layer.
5. **Look and feel.** Every UI we add must copy Hytale's native style (locked 2026-09-25 in `HANDOFF.md`). Players should not feel like they are in a modded UI.

## Reality check that reshapes the phasing
The census below sorts by *shared vs unique*, but the build order is actually forced by **where the data lives**:
- **Server-data widgets** (coords, clock, zone, target health, effects, durability...): our server mod knows all of this → CAN ALL BE BUILT IN ONE GO. The framework is the real work; each widget after that is small.
- **Client-data widgets** (FPS, CPS, keystrokes, ping-as-measured, memory): the server literally doesn't have this data. These need the future companion client mod → deferred, not because they're hard, but because they're impossible server-side. (Ping the server DOES know. FPS it never will.)

## CENSUS — Better HUD's 40 widgets (the completeness benchmark, 1.5M downloads)
*Classified: [S] = shared across all HUD mods (Lunar/Badlion/HudBase/CustomHud/etc.) · [C] = common in several · [U] = unique-ish to Better HUD · strike = vanilla-HUD-editing, client-side in Hytale*

**Bars/vanilla (Hytale equivalents where they exist):**
Health Bar [S], Armor Bar [S], Air Bar [C], Hunger/Saturation [S] (→ Hytale stamina/food), Experience Bar [S] (→ our skill/class XP when in pack; vanilla has none), Jump Bar [C], Mount Health [C], Hotbar/Crosshair/Off-Hand (vanilla-move: client-side, later mod)

**Info text/instruments:**
Coordinates [S] · Compass [S] · Biome [S] (→ zone/region) · Game Clock [S] · System Clock [S] · FPS [S→client-data] · Connection/players [C] (server knows!) · CPS [C→client-data] · XP Info [S] · Light Level [C] · Distance-to-block [U] · Session time (Lunar staple, not in BH) [S]

**Item/inventory:**
Holding Bar (held item card) [S] · Armor Bars w/ durability [S] · Item Pickup log [S] · Full Inv. Indicator [U] · Block Viewer (WAILA-style) [C] · Sign Reader [U]

**Entities:**
Mob Info (target health plate) [S] · Player Info (inspect other players' gear) [C] · Horse Info [C] (→ mount stats)

**Effects/flavor:**
Potion Display w/ amplifiers+timers [S] · Heal Indicator [U] · Blood Splatters [U] · Water Drops [U] · Vignette/Helmet/Portal overlay tweaks [U, client-side in Hytale]

**Scoreboard** [S] (→ our sidebar widget system IS this)

**From other mods, not in Better HUD (add to reach "all of them"):**
Keystrokes [S, client-data] · Combo counter [C, PvP] · Reach display [C, PvP] · Memory/TPS [C; TPS server-side ✓] · Day counter [C] · Item counter [C] · Custom text widget with variables `{zone} {purse}` [U→CustomHud, POWERFUL] · Coordinates-with-death-point [C] · Boss bar position [C]

## BUILD PHASES
**v0.1 — Framework + Tier-1 server-data widgets (the one-go batch):**
- Widget engine on `CustomUIHud`: per-widget anchor (9-point grid) + pixel offset + scale + toggle, z-order, per-player state persisted server-side
- Edit mode (command/keybind → full-screen editor page): widget list, anchor grid, nudge steppers, live preview — the proven /packsettings interaction pattern; true drag-to-move attempted after (engine event support permitting)
- Widgets: Coordinates, Compass, Zone/Biome, Game Clock, Real Clock, Day Counter, Session Time, Connection (players online + our ping), Held Item card, Target Health plate, Effect Display w/ timers, Armor/Tool Durability, TPS
- 2 starter bundles: "Explorer" (coords/compass/zone/clock) + "Combat" (target plate/effects/durability) — both splittable
**v0.2 — Tier-2 common widgets + differentiators:** Item Pickup log, Full-Inv warning, Light Level, Block Viewer (WAILA plate), Mount stats, layout export/import codes, custom text widget with variables
**v0.3 — SkyWynn-native widgets (Skyy: BEFORE the unique ones):** purse/balance, quest tracker (compass-marker default + on-demand beacon/trail flash — see QoL catalog quest-nav spec), skill XP bars, collection progress popup, minion status, bazaar/AH alerts, **party widget (LOCKED spec: each member's name + HP + stamina + mana bars, tied to the same party system that feeds map positions)**, class/mana + cooldowns... — each lands as soon as the pack system feeding it exists (they can't precede their data sources, so this phase interleaves with pack development; the FRAMEWORK hooks for them ship in v0.1 so adding each is trivial)
**v0.4 — Unique/flavor widgets (last, per Skyy):** Distance, Sign Reader, Player Inspect, Heal Indicator, Item Counter, Boss-bar reposition, blood-splatter/water-drop overlays (if VFX hooks allow), layout gallery (server-hosted, player-voted)
**Client companion (much later, Mod Browser):** FPS/CPS/keystrokes/memory + vanilla HUD element moving — the "works on any server" Lunar-style editor

## TEST PLAN (per release, the usual gauntlet + HUD-specific)
Loader manifest check · class-load sweep · live linkage sweep vs current server jar · headless A/B boot —
plus: widget state survives relog + server restart; two simultaneous players see independent layouts; edit mode
on a 2nd monitor-sized window; layout code round-trip; every widget toggled off = zero HUD packets sent.

## ARCHITECTURE LESSON (2026-09-22, learned the hard way — 3 client crashes)
Custom-UI `appendInline` on HUDs is a minefield: multi-line docs crash the client parser, null selectors don't resolve on HUDs, and even file-element selectors failed for us where they work for others. **Final architecture: ZERO inline UI.** All widgets live statically in `SkyyHud.ui` (named root, every widget predeclared), and the server only uses the fully documented ops: `append(file)`, `set("#id.Visible", bool)`, `set("#id_t.Text", str)`, and `setObject("#id.Anchor", Anchor)` — per-player positioning via the official Anchor codec. Editor page: same pattern (static file + set + bindings). This rule applies to ALL future SkyWynn UI (sacks page already follows the page-side conventions; migrate it to static files too if it ever misbehaves).
Also learned: world mod lists are directly editable at `Saves/<world>/config.json` → mod enabling never needs the UI; and the game only accepts synthetic mouse/keyboard sporadically (Windows foreground-lock) → test loop = self-testing builds (auto-attach + auto-grant on join) + reading `UserData/Logs/*_client.log`, with a human doing only the world-load click.

## LOCKED ANSWERS (Skyy, 2026-09-22)
1. Name: **SkyyHud** ✔
2. Versioning for ALL our mods: 0.1 → 0.1.1 style, version at the START of the display name — e.g. **"0.1.1 SkyyHud"** — so they group/sort in the in-game mod list ✔
3. Edit mode v1 = anchor-grid + nudge steppers ✔ (drag-to-move as follow-up)
4. Build order: shared widgets → SkyWynn-native widgets → unique/flavor widgets ✔ (native ones interleave with pack development since they need their data sources)
5. **Edit-HUD hotkey, rebindable in our settings** ✔ — engine caveat: in-world global keys aren't server-receivable today, so v0.1 opens the editor via command + a button in our windows, and the chosen hotkey works anywhere one of our UIs is open; true global hotkey lands the moment the engine (or the companion client mod) allows it.

---
## Editor v2 vision (Skyy, 2026-09-22 after first render of 0.2.4)
- The editor should show **every widget that is currently ON, in place**, and let the player **click-and-drag** each one to wherever they want it (Lunar-style), not a table of buttons.
- A **settings button** on the editor opens a second menu (popup) where widgets are **toggled on/off** (and later: per-widget scale/options).
- The 0.2.x button-grid editor stays as the fallback until drag is proven. Research task running: which Custom UI events carry drag/mouse coordinates (Dropped / DragCancelled / ElementReordered / MouseButtonReleased) and how SkillHud/HyUI position elements. Design options if true drag is impossible: drop-target grid cells (click widget, click destination), or arrow nudging with live preview.
- Rules for any implementation: inline documents only, no underscores in IDs, TextButton controls (see HANDOFF.md §2).

## Reference: Lunar Client HUD editor (Skyy, 2026-09-22 23:20, screenshots in session)
Lunar: every widget is shown live; click-and-drag moves it; drag the blue corner to resize; X removes; cog opens per-widget settings.
Constraint: Lunar is client-side; our Custom UI never receives mouse coordinates (research 2026-09-22). Achievable equivalent:
1. **Drag via the engine's item-drag** — the preview panel is an `ItemGrid` bound to a plugin `SimpleItemContainer`; each ON widget is a
   "chip" item in a cell; `Dropped` reports `slotIndex`/`sourceSlotId` -> snap the widget to that cell (grid = e.g. 16x9 cells of a
   1080p screen); arrows for fine nudging. HyUI ItemGrid (`AreItemsDraggable`) is the reference implementation.
2. **X** and **cog** per chip (TextButtons next to the chip or on a selected-widget bar): X hides the widget; cog opens a popup page
   with Size-/Size+, anchor presets, widget options. Resize by dragging is impossible -> size buttons.
3. Keep the current button grid as "advanced" fallback.
Order: after Magic Bags crafting link.
Per-widget settings (Lunar "Coordinates" page as reference, Skyy 23:22): scale; sub-field toggles (X / Y / Z / direction / biome
each on/off, "move each individually" later); list mode vertical|horizontal; text shadow; background on/off; background + border
colour (preset palette, no colour picker inline); **profiles** = named saved layouts (Default / UHC / SkyBlock / PvP) built on the
existing export/import codes (`/skyyhud profile save <name>` / `load <name>`). Cog on the chip opens this as a popup page.
Drag recipe (agent research 2026-09-22 23:40, HyUI bytecode): use a **virtual** `ItemGrid` (NO `InventorySectionId` — that opts into
native inventory moves) with `AreItemsDraggable: true` and a slot list built inline (HyUI `ItemGridBuilder.withSlots` emits it;
extract the exact emitted `.ui` text from HyUI's bytecode before building). Bind `CustomUIEventBindingType.Dropped` on the grid
selector; payload JSON keys: `SlotIndex` (target), `SourceSlotId`, `SourceItemGridIndex`, `ItemStackQuantity`, `PressedMouseButton`,
`ItemStackId`. The engine does nothing itself for virtual grids: on Dropped, map SourceSlotId -> widget, SlotIndex -> grid cell ->
anchor/offset, save, rebuild the page. `SlotMouseDragCompleted`/`SlotClickPressWhileDragging` give live hover during the drag.
Window ids 0/-1 are invalid if the native path is ever used.

## Status 2026-09-24
SkyyHud 0.3.7: per-widget text colour (13), bold, italic and glow (faked - Hytale has no text glow) with a live preview; the Zone widget shows
'Your Island' / 'Island' / the Hytale zone name / 'Hub' instead of raw world names. 0.3.8: Party and Guild widgets.
