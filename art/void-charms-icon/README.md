# Void Charms - SkyWynn Menu tile icon (64 x 64) + Character hub tab icon (72 x 72)

**Status: APPROVED 2026-10-17 - Skyy picked A (gold chain + glow) and the new Character tab icon
Not committed, not wired in.**

Skyy (2026-10-17, screenshot of the SkyWynn Menu Home shortcuts, tooltip "Void Charms - ID Skyy_Menu_Icon_AccessoryBag", a brown
satchel): "lets change the icon for void charms to be more fitting". Asked for candidates, Skyy picked "a glowing void amulet on a
chain" -> this folder is that amulet, with two small variations for comparison.

## Files
| File | What |
|---|---|
| `Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png` | **A (chosen)**, 64 x 64: gold link chain in a soft arc, round gold setting with four diagonal prongs, a swirling dark-violet void orb with a glass glint and a bright core, a violet glow ring that fades outward, lilac sparkles |
| `candidates/VoidCharms_A_ArcChainGlow.png` | the same as above |
| `candidates/VoidCharms_B_VChainBright.png` | variation: straight V chain, stronger glow (bigger ring + three light rays, brighter orb) |
| `candidates/VoidCharms_C_SteelDrop.png` | variation: dark steel chain, teardrop setting, no glow ring (the light stays inside the orb) |
| `hub-tab/character_accessories.png` + `_on.png` | A as a faded 72 x 72 (@2x = 36 x 36 UI) hub tab icon, same fade + contrast rules as `art/hub-tab-icons/` (min label contrast 1.07 / 1.04 x target = passes); drop-in for that folder's teal amulet |
| `sheet.png` | the three at 64 px (checker, menu navy, light), 2x and 32 px; each in a SkyWynn Menu row mock next to Pocket Dimension, Pets and Collections (plus the old satchel); old vs new hub tab on the real Sky tab textures |
| `manifest.json` | files (bytes, sha256), candidates, chosen = A |

## Look
Same family as `art/menu-icons/` (painter and palettes imported from `tools/art/make_menu_icons.py`, not edited): hard alpha, 1 px
violet-black outline tinted toward the part it touches, light from the top left, every pixel on a material ramp, no pure black / white.
Colours: the menu family's `gold` / `steel` and `void` (dark violet) ramps - the void theme, kept clearly apart from Pocket Dimension
(teal pouch + teal-blue swirl), Pets (teal collar + paw tag) and the old teal hub-tab amulet.

## Tools
`python tools/art/make_void_charms_icon.py` writes everything above; deterministic (two runs = same bytes, checked). Original pixels
only; the sheet reads only our own art (`art/menu-icons`, `art/accessory-bag-icon`, `art/hub-tab-icons`, `art/ui-kit-sky`).

## For the main session (wiring - not done here)
- SkyyMenu `ICON_ITEMS`: point `Skyy_Menu_Icon_AccessoryBag` at `art/void-charms-icon/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png`
  (manifest `art/void-charms-icon/manifest.json`), or add a new id `Skyy_Menu_Icon_VoidCharms` and move the tile to it.
- The Workbench "Accessories & Bags" tab (`tools/skyywbtab.py`) and the in-world bag keep the satchel unless Skyy wants them changed.
- Hub tab: copy `hub-tab/*.png` over the `character_accessories` pair if Skyy wants the tab to match.

## Open questions for Skyy (each with today's default)
1. A, or one of the variations (V chain + strong glow / steel teardrop)? [A]
2. Also swap the Character hub "Accessories" tab picture to the void amulet? [yes]
