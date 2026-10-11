# SkyWynn Menu item - new emblem (64 x 64 icon + held model)

**Status: DRAFT v1 for Skyy's review. Not committed, not wired in.** ART-RESUME item 17.

Skyy (2026-10-09): "lets make a new icon for the menu". Skyy picked the **SkyWynn emblem**. Today the menu item (id `Skyy_Menu`, the
last hotbar slot, SkyyMenu) borrows the vanilla Voidheart look (`MENU_ITEM_LOOK = "Ingredient_Voidheart"` in
`SkyyMenu/build_skyymenu_0.3.12.py`). This folder is the replacement: our own held model, texture and icon.

Defaults used (ART-RESUME item 17, Skyy can change them): compass star over the island [yes]; sky blue + grass green + gold [yes];
keep a soft glow [yes].

## What it is
A small floating sky island with a gold compass star above it, so it reads as "the SkyWynn hub":
- grass top (lit bevel rim, a few flower and blade-tip pixels), a soil band with grass hanging over the edge, pebbles and roots;
- a stepped rocky underside that narrows to a point (4 layers + a side chunk, darker and mossier further down);
- a tiny stream on top that runs off the front edge as a **waterfall** and breaks into mist below the island;
- 3 small **cloud wisps** round the rock, and a small tree at the back left;
- a gold 8-point **compass star** (long N / E / S / W points, short diagonals, pinwheel bevel, sky-blue gem in the centre) floating
  above the island. In 3D it is two crossed quads + a small gold core, so it reads from every side. The star is `fullbright` (it glows).

All geometry and pixels are original. No vanilla file was copied, traced or recoloured. The vanilla Voidheart was only read (from
Assets.zip, read only) to check the file format, the texel density, the icon size and how big the held model is.

## Files (mod-jar layout - copy `Common/` into the jar)
| Path | Size | What |
|---|---|---|
| `Common/Items/SkyyMenu/Skyy_Menu.blockymodel` | 19 nodes | held item model (vanilla blockymodel format, 1 texel per unit) |
| `Common/Items/SkyyMenu/Skyy_Menu_Texture.png` | 128 x 64 RGBA | the texture (cut-out alpha on the star + waterfall quads) |
| `Common/Icons/ItemsGenerated/Skyy_Menu.png` | 64 x 64 RGBA | the item icon (= vanilla item icon size), hard alpha |
| `sheet.png` | 1180 x 1000 | review sheet: icon 1x / 2x / 4x / 32 px / on light, hotbar mock (9 slots + 1-slot views), 5 renders of the real model, texture, palette |
| `manifest.json` | - | file list (bytes, sha256), part list, bounds, suggested item fields, palettes |

Generator: `python tools/art/make_menu_emblem.py` (pure Python 3, no Pillow / numpy; PNG + raster helpers in `tools/art/emblem_png.py`).
Deterministic (two runs = same bytes, checked). Check: `python tools/art/validate_menu_emblem.py` (ALL OK).

## Model
- Nodes: `R-Attachment` (none, root - same as the Voidheart) > `Emblem` (none, yawed 165 deg like the Voidheart's `Body`, so the
  waterfall / showcase side faces the same way in the hand as the Voidheart's eye) > 17 parts: `Grass`, `Soil`, `Rock-Upper`,
  `Rock-Mid`, `Rock-Low`, `Rock-Tip`, `Rock-Chunk`, `Leaves`, `Trunk`, `Stream`, `Cloud-A`, `Cloud-B`, `Cloud-R`, `Star-Core`
  (boxes) and `Star-Ray-A`, `Star-Ray-B`, `Waterfall` (double-sided quads; the two star quads share one 13 x 13 texture area).
- Keys are exactly the vanilla ones (node, box, quad, none and textureLayout keys checked against the Voidheart); boxes use the
  standard cross unwrap (`unwrapMode` full), quads `custom`; shading `standard` like the Voidheart, `fullbright` on the star.
- **Size vs the Voidheart** (item space, rotations applied):

  | | width x height x depth | vertical centre |
  |---|---|---|
  | Voidheart (`Ingredient_Voidheart`) | 28.6 x 34.3 x 19.7 units (core box 16 x 16 x 13) | 13.1 |
  | Skyy_Menu emblem | 24.0 x 36.5 x 22.6 units (island 20 x 3 x 18 grass cap) | 13.2 |

  Same scale class (tallest side 6% more, because of the star), same centre height, so it sits in the hand like the Voidheart.
  Texture density is the same 1 texel per unit; the texture is 128 x 64 (Voidheart 64 x 64) because the island has more parts.

## Icon
Rendered from the model in 3/4 view (yaw 24, pitch 20, 8x supersampled, box-filtered to 64), then hand-tuned in code: hard alpha,
warm rim light on the top / left edge and a cool shade on the bottom / right edge (reads on dark hotbars), 1 px violet-black outline
`#120e1c`, and the star drawn flat-on as a crisp 17 px sprite from the same star painter (the crossed quads smear at 64 px), with a
tiny glint beside it. No `#000000` / `#ffffff` pixels. Fills 42 x 60 px of the 64 x 64 slot.

## How SkyyMenu should wire it (for the main session / the next SkyyMenu round - this art round did NOT touch any build script)
In the next SkyyMenu patch (derived from the current pinned version, not by editing `build_skyymenu_0.3.12.py`):
1. Drop `MENU_ITEM_LOOK = "Ingredient_Voidheart"` / `look = look_of(MENU_ITEM_LOOK)` for the menu item and give `Skyy_Menu` its own
   look (values from `manifest.json` "suggested_item_fields"):
   ```
   "Icon": "Icons/ItemsGenerated/Skyy_Menu.png",
   "Model": "Items/SkyyMenu/Skyy_Menu.blockymodel",
   "Texture": "Items/SkyyMenu/Skyy_Menu_Texture.png",
   "Scale": 1.2, "PlayerAnimationsId": "Item",
   "IconProperties": {"Scale": 0.9, "Rotation": [0, 0, 0], "Translation": [0, -13]},
   "Light": {"Color": "#432", "Radius": 1}
   ```
   (Scale / PlayerAnimationsId / IconProperties / Light radius = the Voidheart's own values, so hand pose and size stay the same;
   only the light colour changes from violet `#103` to a faint warm gold.)
2. Ship the three files in the jar at `Common/Items/SkyyMenu/Skyy_Menu.blockymodel`, `Common/Items/SkyyMenu/Skyy_Menu_Texture.png`,
   `Common/Icons/ItemsGenerated/Skyy_Menu.png`, read from `art/menu-emblem/` and checked against `art/menu-emblem/manifest.json`
   (sha256 + bytes) the same way `icon_item_png()` checks the Accessory Bag icon; assert none of the paths exists in vanilla `COMMON`.
3. Other places that still name the Voidheart as the menu's picture: the `MODS` row `"icon": "Ingredient_Voidheart"` (line ~441 of
   0.3.12) can become `"Skyy_Menu"` once the item ships; the `need_item(MENU_ITEM_LOOK)` loop entry goes away.

## Open questions for Skyy (each with today's default)
1. Keep the little tree on the island? [yes - it says "SkyBlock island"; drop it if the hotbar looks busy]
2. Star or crown above the island? [compass star]
3. Glow colour in game? [faint warm gold `#432`, radius 1]
