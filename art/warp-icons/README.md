# Warp icons - one picture per warp theme (64 x 64)

**Status: APPROVED v1 (Skyy 2026-10-17 on `sheet.png`: "these all look great!").** Wired into SkyyMenu 0.3.37 (tiles) and
SkyyEssentials 0.1.14 (/warpadmin icon pick) so they can be seen in game; a redraw only changes the PNGs here (ids stay).

Skyy (2026-10-17, docs/answered/world.md): "if posible i want a bunch of custom icons we can set to a warp when making it. for mining
fishing foraging farming and what not. probably 1 per zone."

## Files
| File | What |
|---|---|
| `Common/Icons/ItemsGenerated/Skyy_Menu_Icon_Warp<Name>.png` | 11 icons: Mining, Foraging, Farming, Fishing, Combat, Dungeon, Boss, Shop, Portal, Cave, Home |
| `sheet.png` | review sheet: each icon 1x on checker + navy, 2x, 32 px, on light, and a Teleport page mock |
| `manifest.json` | icons (id, theme, file, bytes, sha256), the 3 reused themes, palettes |

Also in the pick list, NOT redrawn (approved `art/menu-icons-2`): Signpost (the warp signpost = the default when no icon is picked), Hub, Spawn.
Zone homes (/sethome) always wear Home; island homes wear My Island.

## How it is used
- The theme id (`mining`, `fishing`, ...) is what SkyyEssentials saves per warp (`Skyy_SkyyEssentials/warpicons.properties`).
- SkyyMenu ships each PNG as the icon-only item `Skyy_Menu_Icon_Warp<Name>` (checked against `manifest.json`: sha256 + bytes).
- New theme = add a builder + a row to `ICONS` in the generator, run it, then add the row to SkyyMenu's `WARP_ICONS` and Essentials' `WICON_*`.

## Tools
`python tools/art/make_warp_icons.py` writes everything above (deterministic; `--check` builds twice, compares, checks hard alpha, writes
nothing). Reuses `tools/art/make_menu_icons.py` (painter, palettes - imported, not edited). Original pixels only.

## Open questions for Skyy (each with today's default)
1. Are these the right themes (one per zone)? Any to add / drop? [these 11 + Warp / Hub / Spawn]
2. Any icon to redraw? [none]
