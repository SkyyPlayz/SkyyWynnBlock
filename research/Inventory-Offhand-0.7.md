# Inventory buttons + offhand weapon slot on Hytale 0.7.0 (research, 2026-10-13)

Read-only research on the 0.7.0 release (server jar, Assets.zip, client install). Skyy's words: docs/answered/gear.md + ui.md 2026-10-13.

## A. Buttons in the inventory
- **Real buttons inside the vanilla inventory: NO.** The inventory screen is drawn from client-only files
  (`Client/Data/Game/Interface/InGame/Pages/Inventory/InventoryPage.ui`, `GamePageNavigation.ui`); a server asset pack cannot reach them.
  The server can only pick a page (`SetPage`), not add to one. `HudComponent` only shows / hides vanilla HUD parts.
- **Detecting Tab:** no "inventory opened" packet among 144 client->server packets. `ClientOpenWindow` (PocketCrafting) might fire on Tab
  - UNVERIFIED; probe = log PocketCraftWindow open / close while pressing Tab.
- **New 0.7 server UI (`modules.ui`, Noesis XAML, Page.Serverside, clickable HUD widgets `UIHudWidget` in 11 slots):** real and powerful
  (Grid / Button / TabControl / animations / nine-slice / sounds), but **switched OFF** unless the server JVM runs with
  `-Dhytale.serverside_ui_preview=true` (a dev preview; plugins can't enable it). No item grids or inventory windows. Watch it for later.
- **Our own inventory-like page with real inventory slots: NO** (probes P1 / P2 2026-10-02: the client draws no inventory next to a
  custom page; research/Skyy-UI-Inventory.md is wrong on that point).

| Option | 0.7 | Effort | What Skyy sees |
|---|---|---|---|
| d2. Hub page on a hotkey / item / command | YES | low | one key opens the hub; Tab stays vanilla |
| d1. Vanilla inventory + a chest-style "SkyWynn" panel of hub icons (setPageWithWindows + Bench + a ContainerWindow; clicks caught by an inbound packet filter, items never move) | panel YES, click-as-button UNVERIFIED | medium | the real inventory with a hub-icon panel beside it |
| c. HUD button bar over the inventory | only with the Noesis preview flag | high | - |

Recommendation: d2 now, probe d1, revisit Noesis when Hytale turns it on.

## B. Offhand (utility "Z" slot) as the weapon slot
- The slot is `InventoryComponent$Utility` with its selector wheel. What may go in = item JSON `"Utility": {"Usable": true}` (vanilla:
  shields, torches, Weapon_Kunai). **So weapons CAN go there: data only.**
- Input routing (`InteractionContext.forInteraction`): with an EMPTY hotbar hand the utility item gets every input (left, right, abilities).
  With a hotbar item held, per-input `Priorities` (MainHand vs OffHand) decide; a tool with no right-click lets right click fall through to the
  utility item already.

| Design | 0.7 | Note |
|---|---|---|
| D1. Hotbar tool keeps left click; utility weapon gets right click + ability keys (Priorities OffHand) | YES (engine), client UNVERIFIED | data only |
| D2. Empty "fists" hotbar slot -> the utility weapon gets BOTH mouse buttons | YES (engine), client + animation UNVERIFIED | data only |
| D3. Weapon takes left click even while a tool is held | YES but breaks mining / placing | not recommended |
| D4. A key swaps the utility weapon into the active hand and back | YES (plugin item move) | needs code |

Best fit: **D1 + D2** (all item JSON in SkyyGear / SkyyArmory). Risk to probe first: left-hand swing animations from the offhand may look wrong.
