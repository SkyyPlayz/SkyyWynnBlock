# Accessory Bag - menu icon (64 x 64)

**Status: FINAL (Option B gems + leather tweak v2). Not committed, not wired in.**

Skyy's answers (2026-10-08, word for word):
1. "Use Option B gem colors"
   -> gems left to right: Health red, Stamina yellow, Mana blue, Regeneration green, Speed cyan.
2. "Make it a little brighter with a more leather look (still black leather, just lighter"
   -> leather tweak v2 (see "Leather tweak v2" below). The sheet's section 6 shows before vs after at 4x.

## What it is
A new, ORIGINAL item icon for the Accessory Bag, to replace the vanilla `Utility_Bag_Seed` icon that the SkyWynn Menu tile
("Accessory Bag", SkyyMenu ENTRIES) and the Workbench "Accessories & Bags" tab (`tools/skyywbtab.py` ICON_SRC) still show.

The look: a chunky black leather satchel with a gold carry handle, a front flap with a stepped (rounded) edge, a leather strap
tongue, a small gold clasp bar on the tongue, and 5 small cut gems in a row on the clasp in the 5 booster-line colours. 3/4 view, transparent background, a
1 px dark outline, light from above.

## Files (mod-jar layout)
| Path | Size | What |
|---|---|---|
| `Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png` | 64 x 64 RGBA | the icon |
| `sheet.png` | 1520 x 1580 | FINAL sheet: actual size, 32 px, 4x, 8x on dark + light, menu mock, gem list with line names, before vs after at 4x |
| `manifest.json` | - | file list (bytes, sha256), gem list, view settings, the box list of the little 3D model, palettes |

Generators (in `tools/art/`, next to this folder's parent):
- `make_accessory_bag_icon.py` - draws the icon (`--gems lines` = default and FINAL; `--gems model` = the old draft gems, kept only for reference; `--look v2` = default and FINAL leather, `--look v1` = the previous darker leather, used for the before / after).
- `make_accessory_bag_sheet.py` - draws the icon + `sheet.png` + `manifest.json`. Run this one: `python tools/art/make_accessory_bag_sheet.py`.
Deterministic (two runs = same bytes, checked). Pure Python + numpy + Pillow. No vanilla file is read.

## How it was made
1. A small blocky 3D bag built from 16 boxes (cubes only, like a Hytale item model): body, base, side gussets, flap lid + stepped
   crown, front flap + stepped hem, strap tongue + stepped tip, clasp bar, handle mounts, posts and top bar.
2. Every face is painted from code like a Hytale texture: light from the top ("imaginary spotlight"), a lit bevel on top edges,
   AO along bottom edges and in corners, a lit vertical edge on the corner facing the light, soft low-frequency leather folds (no
   noise), muted brass stitching on the flap / tongue edges, crisp top-edge highlights and dark lower edges on all gold.
3. Rendered in 3/4 view (orthographic, yaw 30, pitch 22 - same rasterizer idea as `tools/art/render_blocky.py`, adapted to
   paint faces directly instead of reading a texture atlas) at 8x supersampling, with a soft cast shadow (light from above,
   a little from the left), then box-filtered to 64 x 64.
4. 64 px hand-tuning in code: hard alpha (every pixel is fully see-through or fully solid), 1 px contact lines where a part sits
   in front of another (under the flap, round the tongue and clasp, under the handle), a warm rim light on the top / left edge
   and a faint cool rim on the right / bottom edge (so the black bag reads on dark menus), a 1 px outline (violet-black next to
   leather, brown-black next to gold), and **hand-placed 3 x 3 pixel gems** (glint top-left, dark bottom-right, a lit gold rim
   above each gem, dark gold between and under them), plus gold glint pixels on the handle.
5. Iterated 9 times against the rules (then the gems were switched to Option B on Skyy's pick): v1 gems floated flat over a sloped clasp and the flap / body were one dark block; later
   passes slanted the gem row with the clasp, lightened the flap a step above the body, added the hem shadow + contact lines,
   lengthened the tongue so it shows under the clasp, added the rims, and cooled the leather so it reads as black, not brown.

Colour rules kept: no `#000000` and no `#ffffff` (darkest pixel = the outline `#0a0710`, brightest = the Speed gem glint
`#dafcff`; the gem hexes are exact - the darkness floor runs before the gems are placed); shadows lean violet / blue, lights lean warm; leather v2 `#0f0b16` .. `#8c7a7a` (v1 was `#0c0914` .. `#6b5a60`), gold `#3e1f08` .. `#fff2cc`.

## Leather tweak v2 (Skyy: "Make it a little brighter with a more leather look (still black leather, just lighter")
What changed (only the leather; the gold handle, clasp and the 5 gems are unchanged - every pixel that is fully gold or gem is
byte-identical to v1, checked; only the 1-px edge pixels where gold meets leather pick up the lighter leather):
- **Lighter black leather:** a new 8-step ramp `#0f0b16 #18131f #221b28 #2d2431 #3a2e3b #4c3e47 #67565c #8c7a7a`, about one to
  two steps lighter than v1. Soft charcoal-black: cool violet in the shadows, a touch warm in the sheen, so it reads as black
  leather, not grey or brown (a first try at `#433949`-ish flap tones looked grey-lavender and was pulled back).
- **Soft sheen:** a soft highlight spot on the upper-left of each rounded face (flap, body, lid) plus a stronger sheen on the
  top (rounded) edges.
- **Worn edges:** all leather faces are slightly lighter along their edges and lighter again at the corners (rubbed leather).
- **Stitching:** lighter warm-grey dashed thread (`#4e4250` .. `#a39488`) along the flap edge and flap sides, round the strap
  tongue, down the body's front corners, along the body's bottom edge and on the bag's side.
- **Grain:** a faint pebbled grain + broad mottling from soft sine layers (smooth value change, no per-pixel noise).
- **Folds:** two soft vertical slump folds in the body leather below the flap. (A horizontal fold line on the flap was tried
  and dropped: it made stripes at 64 px.)
- **Fixes on the way (v2 only):** the 1-px contact lines now only appear between different parts (v1 also darkened steep top
  faces); the flap front stops 0.03 below the lid so they no longer flicker into speckles.
- Iterations: v2a too light / grey-lavender and the grain made horizontal streaks -> v2b darker, rounder sheen, softer grain
  -> v2c horizontal flap fold dropped, z-fight fixed -> v2d contact-line fix (gold kept as v1) + slightly warmer mids.
- Still checked readable at 64 px and 32 px on dark and light (sheet sections 1, 2, 4, 6).

## Gem colours (left to right) and where they come from
FINAL = Option B (Skyy: "Use Option B gem colors"): the first 5 booster lines in SkyyAccessories' table
(`SkyyAccessories/build_skyyaccessories_0.5.8.py` BOOSTERS: Health = Red, Stamina = Yellow, Mana = Blue, Regeneration = Green,
Speed = Cyan), in that order. Each gem is drawn with 4 tones (dark / mid / light / glint):

| # | Line | Colour | dark | mid | light | glint | Source of the hexes |
|---|---|---|---|---|---|---|---|
| 1 | Health | red | `#8a1a20` | `#d23a3a` | `#ff8a80` | `#ffe0dc` | `tools/art/make_bags.py` ACC_GEMS |
| 2 | Stamina | yellow | `#8a6800` | `#d6a800` | `#ffe066` | `#fff8d6` | `tools/art/make_bags.py` ACC_GEMS |
| 3 | Mana | blue | `#163f8f` | `#2f6fe0` | `#86b4ff` | `#e2eeff` | `tools/art/make_bags.py` ACC_GEMS |
| 4 | Regeneration | green | `#17702f` | `#2fb34f` | `#86eb98` | `#e2ffe6` | `tools/art/make_bags.py` ACC_GEMS |
| 5 | Speed | cyan | `#2a8a9a` | `#4ac0cc` | `#8ae6ee` | `#dafcff` | `tools/art/make_accessory_icons.py` WING |

**Cyan source:** the build table only says the word "Cyan" (gem Rock_Gem_Zephyr, Ingredient_Crystal_Cyan) and has no hex.
The exact cyan used by the APPROVED accessory icons is the Speed icon's wing ramp, `WING = ramp('#0c3a44', '#2a8a9a',
'#4ac0cc', '#8ae6ee', '#dafcff')` in `tools/art/make_accessory_icons.py` line 87 (same ramp in the approved concept
`research/cloud/accessory-art/make_icons_v2.py`; the accessory-art README calls it "cyan wings (Zephyr colour)"). The gem uses
its stops 2-5 (the darkest stop `#0c3a44` is that icon's outline tone). This replaces the earlier guessed cyan (make_bags.py
Legendary gem ramp, mid `#1fb6c6`).

Note: the in-game Accessory Bag MODEL (make_bags.py ACC_GEMS, SkyyAccessories 0.5.8) still has red, blue, yellow, green, violet
gems, so the held bag and this icon now differ in gem order / the 5th colour (see the open question below).

## UNVERIFIED
- How it looks in the real menu: the menu mock on the sheet is my drawing (84 px slots, 62 px icon from SkyyMenu's ItemGrid
  `SlotSize 84` / `SlotIconSize 62`), not the game's slot art. The Workbench tab draws its icon at an unknown smaller size.
- Alpha: vanilla generated icons are premultiplied (repo note). This icon has only alpha 0 or 255, so it is the same either way.
- Wiring (main session's job): the menu tile takes an ITEM id (today `Utility_Bag_Seed`), so it needs an item whose `Icon` is
  `Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png` (or the Accessory Bag item itself); the Workbench tab wants its icon under
  `Icons/CraftingCategories/<Mod>/AccessoriesBags.png` (skyywbtab.py), so the build would copy this PNG there.
- The bag's exact shape is my own design; it follows the toned-down model in make_bags.py (`build_accessory`: black leather
  body + flap, gold handle, small gold clasp bar on the flap tongue holding 5 small gems) but is not a render of it.

## Open questions for Skyy (default in brackets)
1. The held Accessory Bag model (make_bags.py) still has red, blue, yellow, green, violet gems. Change the model's gems to
   match this icon (Health red, Stamina yellow, Mana blue, Regeneration green, Speed cyan)? That is the main session's job.
   [yes, so the bag and its icon match]
2. Should the gems glow? [no]
3. Use the same PNG for the Workbench "Accessories & Bags" tab? [yes]
