# SkyWynn Menu - icons sheet 2: Teleport page, shared buttons, Shards tile (64 x 64 each)

**Status: DRAFT v1 for Skyy's review. Not committed, not wired in.**

Skyy (2026-10-15, looking at the Teleport page's vanilla icons - grass block, bench, gold, plank stubs, an arrow, a flag): "lets do our
own icons in every menu too." This is the FIRST sheet of that job: the SkyyMenu Teleport page, the buttons every page shares, the
Players page Accept / Deny buttons, and the one main tile still on a vanilla icon (Shards).

## Family look
The same as the approved sheet 1 (`art/menu-icons/`, Skyy: "beautiful! i love it"): 64 x 64 RGBA, hard alpha, a 1 px violet-black
outline `#120e1c` tinted toward the part it touches, light from the top left (lit bevels top / left, dark bevels bottom / right,
contact shadows, inner lines), every pixel snapped to a 6-7 step ramp, no `#000000` / `#ffffff`. The generator imports sheet 1's
painter and palettes and adds only: `ruby` (Close / Deny), `skin` + `hair` (Player), `wooddim` / `golddim` / `stonedim` (locked and
empty warps) and `beam` (the warm light in Hub and Spawn).

| Group | Tint | Icons |
|---|---|---|
| Teleport page | Travel gold / amber | MyIsland, Hub, Spawn, Warp, WarpLocked, NoWarps |
| Main menu tile | Travel gold / amber | Shards |
| Buttons on every page | Admin steel (Close has a red X) | Back, Prev, Next, Close |
| Players page | Social violet head, steel buttons (green / red) | Player, Accept, Deny |

## Icons (`Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png`)
| Name | Replaces (vanilla) | Where in SkyyMenu 0.3.25 | Shows |
|---|---|---|---|
| MyIsland | `Soil_Grass` | `ENTRIES ("tp", 11)` + `PLAYER_ACTIONS` slot 31 (Visit Their Island) | a small floating island with a big gold map-pin home marker planted in it; the pin holds a little house. Unlike the Island Menu tile (round island + cottage + flag) |
| Hub | `Hub_Portal_Default` | `ENTRIES ("tp", 13)` + `PLAYER_ACTIONS` 29 (Send Teleport Request) | a stone town gate: two battlemented towers with amber banners, a gold keystone, warm town light and a road through the arch, a tiled plaza in front. Unlike Teleport's gold portal ring |
| Spawn | `Spawn_Portal` | `ENTRIES ("tp", 15)` + `PLAYER_ACTIONS` 30 (Invite Them Here) | a round stone spawn pad with a gold inlay ring and a beam of warm light up to a gold star |
| Warp | `Tool_Map` | `ICON_WARP` (every unlocked warp) | a wooden signpost (gold cap, stone foot): a big board pointing right with a painted gold arrow, a small board pointing left |
| WarpLocked | `Tool_Map` (+ the greyed text) | NEW constant `ICON_WARP_LOCKED` | the same signpost in dim grey-brown, a gold padlock in front |
| NoWarps | `Tool_Map` | NEW constant `ICON_NO_WARPS` (`NO_WARPS_SLOT` 31) | a bare grey signpost, a dashed outline where the board would be |
| Shards | `Portal_Device` | `ENTRIES ("main", 11)` | an amber hex shard crystal (violet portal window, gold star) floating over a tiny island with two small amber crystals: "your shard islands". Same hex-shard shape as the Hub Shard / Shard Portals (research/cloud/icons-1013) but amber (Travel) and floating |
| Back | `Weapon_Arrow_Iron` | `ICON_BACK` (slot 45) | a thick steel return arrow: points left, the tail curls round on the right (gold tip) |
| Prev | `Weapon_Arrow_Crude` | `ICON_PREV` (slot 48) | a steel double chevron pointing left (front bright, back dark) |
| Next | `Weapon_Arrow_Iron` | `ICON_NEXT` (slot 50) | the mirror of Prev, pointing right (lit the same way) |
| Close | `Furniture_Flag_Small_Red` | `ICON_CLOSE` (slot 49) | a square riveted steel plate with a big red X |
| Player | `Armor_Leather_Light_Head` | `ICON_PLAYER` (player list fallback, `NO_PLAYERS_SLOT`, `PLAYER_HEAD_SLOT`) | a generic blocky player head in 3/4 view (brown hair, two eyes) on violet shoulders |
| Accept | `Ingredient_Crystal_Green` | `ENTRIES ("players", 47)` | a round emerald button in a steel ring with a cream check |
| Deny | `Ingredient_Crystal_Red` | `ENTRIES ("players", 51)` | a round ruby button in a steel ring with a cream X (round, so it never looks like the square Close plate) |

**Warp icons in game:** every warp uses the one `ICON_WARP` constant (`fillWarps`, `put(slots, WARP_SLOTS[i], ICON_WARP, ...)`); warps
do NOT carry their own item icon (the menu reads only the warp's id, world and position). The bench / gold / plank stubs Skyy
saw are the vanilla pictures of `Hub_Portal_Default`, `Spawn_Portal` and `Tool_Map` (the in-game look was not checked by this round).
So one generic Warp icon + a locked variant + an empty variant cover the page.

The other files:
- `sheet.png` (1556 x 1908): every icon at 64 px on checker and on menu navy plus 2x, labelled and grouped; all at 32 px on navy;
  all at 64 px on a light background; a mock of the 9 x 6 Teleport page (My Island 11, Hub 13, Spawn 15, warps 19 / 20 / 21 with
  21 locked, Back 45, Close 49) and a mock of the main view with the SkyyMenu 0.3.25 slots (sheet-1 icons, the new Shards at 11
  and the new Close at 49; Wardrobe 36 and Edit 53 marked "vanilla"). New icons have a gold frame in the mocks.
- `manifest.json`: per icon id, file, bytes, sha256, category, group, `replaces_vanilla_id`, the SkyyMenu spot, what it shows; the
  file list; the palettes.

## Tools
- `python tools/art/make_menu_icons_2.py` writes everything above. Pure Python 3 (no Pillow / numpy); imports
  `tools/art/make_menu_icons.py` (sheet 1, not edited) and `tools/art/emblem_png.py`. Deterministic: two runs give the same bytes
  (checked: icons, sheet, manifest).
- `python tools/art/validate_menu_icons_2.py` checks size, hard alpha, no black / white, the dark outline, fill and 1 px margin,
  that every icon is unique (also against sheet 1), no name clash with sheet 1, manifest ids / hashes / replaced ids, determinism.
  It reads no game file; the vanilla path-clash check runs only with `--assets <path to a COPY of Assets.zip>`. Result: ALL OK.

No vanilla file was read, copied, traced or recoloured.

## How SkyyMenu could wire them (for the next SkyyMenu patch; this art round did NOT touch any build script)
1. Ship them like the sheet-1 icons: a list `MENU_ICONS_2 = [("MyIsland", "My Island"), ...]` and, per entry,
   `ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("art/menu-icons-2/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm,
   "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, "art/menu-icons-2/manifest.json", _label, "Farming_Collar")`.
   `icon_item_png` already checks bytes + sha256 against the manifest's `files` list (paths relative to `art/menu-icons-2/`).
   The `len(ICON_ITEMS) == ...` assert (line ~11186) must count the new ones.
2. Constants: `ICON_BACK = "Skyy_Menu_Icon_Back"`, `ICON_PREV = "..._Prev"`, `ICON_NEXT = "..._Next"`, `ICON_CLOSE = "..._Close"`,
   `ICON_WARP = "..._Warp"`, `ICON_PLAYER = "..._Player"`; the vanilla-id check loop at ~line 1177 / 1212 must accept our icon ids
   (`iid in ICON_ITEMS`, as line 1130 / 1202 already do).
3. New constants `ICON_WARP_LOCKED`, `ICON_NO_WARPS` -> MenuData + `fillWarps`: `open ? ICON_WARP : ICON_WARP_LOCKED` and the
   "No warps yet" put uses `ICON_NO_WARPS`.
4. `ENTRIES`: ("tp", 11) `Skyy_Menu_Icon_MyIsland`, ("tp", 13) `..._Hub`, ("tp", 15) `..._Spawn`, ("players", 47) `..._Accept`,
   ("players", 51) `..._Deny`, ("main", 11) `..._Shards` (and drop "Shards" from the line ~2111 exception list).
   `PLAYER_ACTIONS` 29 / 30 / 31 may reuse Hub / Spawn / MyIsland (see question 3).

## Open questions for Skyy (each with today's default)
1. Close: a steel plate with a red X, or the red X alone? [steel plate - it reads as a button and stays apart from Deny]
2. Accept / Deny: round steel-ringed buttons with a check / X, or keep crystals but our own? [round buttons]
3. Player actions (Send Teleport Request, Invite Them Here, Visit Their Island) still show the vanilla Hub / Spawn / grass looks -
   reuse Hub / Spawn / MyIsland there too? [yes, reuse - a later sheet can draw their own]
4. Shards: amber (Travel) floating shard, or the void-violet of the Hub Shard? [amber, the Travel colour like Teleport / Island Menu]
5. Warp locked: dim + padlock, or full colour + padlock? [dim + padlock, matches the greyed "(locked)" text]
6. Player: the fallback head shows brown hair - keep one generic head, or a hooded / faceless silhouette? [generic head]
