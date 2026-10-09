# Dark Leather light armor (SkyWynn) — candidate light armor design

Original light-armor set for Skyy's SkyWynn pack: near-black charcoal leather, navy cloth, brown straps and buckles,
amber trim. Half-plate chest with ONE low leather shoulder plate that wraps the shoulder (LEFT by default; the right shoulder is a leather
sleeve plus a strap brace). Close-fitting leather half-helm with the motifs from Skyy's helmet reference: slim amber
crest rising to a spike, small V brow with a faceted amber diamond gem, small swept-back amber fins, and a dark visor
with a T/V opening and vertical grille bars painted on the shell.

## Skyy's feedback (round 1, word for word)

> "It looks great! But it's supposed to be light armor, so I try to slim it up and scale it down, especially the
> shoulder pads and the helmet, try to make them slim"

What changed in this revision (the old version is in the "before vs after" row of `sheet_with_refs.png`):
- Every piece sits closer to the body: about 0.5-1 unit off it, like vanilla light armor. Plates and belts are thinner.
- Shoulder: one low 14x3x18 leather plate plus one thin lame (was a 22x9x25 plate, a raised dome and two lames); overall the shoulder went from 26 wide x 20 tall to 18 x 9.
- Helmet: one close shell (0.5 off the head) plus a 1.5-thick cap, replacing the 4-step box. The visor, grille and
  cheek trims are painted on instead of built from boxes. Crest 4 wide (was 6), V brow and gem smaller, fins half
  size and closer to the head, crown spikes dropped. The shell top is 5.5 units lower (crest tip 8 units lower); the helm is 31 wide and 30.5 tall instead of 34 by 36.
- 54 boxes / 648 tris down to 43 boxes / 516 tris.

## Skyy's feedback (round 2, word for word)

> "Looks great! If just try to make the shoulder pad wrap around the shoulder a little bit if you can"

What changed (only the LEFT shoulder pad; everything else is untouched). Close-ups are in section 4 of `sheet.png`;
the before/after is row 6 of `sheet_with_refs.png`:
- The top plate is 13x3x16 (was 14x3x18) and slopes down a little more (27 degrees, was 20), so it follows the
  shoulder instead of sticking out flat.
- New thin front flap (8x6, 1.25 thick) under the front edge, covering the front of the deltoid. It angles in
  against the arm and has an amber edge, a stitched seam and a rivet.
- New thin back flap (8x8, 1.25 thick), the same but longer, so it reaches further around the back and down the arm.
- The outer lame is now a thin 2x6x14 strip close to the outer upper arm (was a 6x3x17 step out at the plate's edge),
  closing the cup on the outside. It has an amber bottom edge and two small rivets.
- The pauldron is 15 wide x 13.5 tall x 17.8 deep overall (was 17.6 x 8.9 x 19.6). It is narrower and shallower but
  hangs lower, because it now wraps down instead of overhanging.
- 43 boxes / 516 tris up to 45 boxes / 540 tris (Chest 16 boxes / 192 tris up to 18 / 216). Chest texture stays 96x160.

**Status: committed as a new possible light armor design (2026-10-08).** Skyy: "Yes commit it as a new possible light armor design". NOT verified in the Hytale game.

## What is here

| file | what |
|---|---|
| `Common/Items/Armors/SkyyDarkLeather/{Head,Chest,Hands,Legs}.blockymodel` | the 4 slot models (Hytale `character` format, boxes only) |
| `Common/Items/Armors/SkyyDarkLeather/{Head,Chest,Hands,Legs}_Texture.png` | hand-painted textures, 64 px per block, sides multiples of 32 |
| `Common/Icons/ItemsGenerated/Armor_SkyyDarkLeather_{Head,Chest,Hands,Legs}.png` | 64x64 inventory icons |
| `source/{Head,Chest,Hands,Legs}.bbmodel` | Blockbench projects (textures embedded) for editing |
| `sheet.png` | review sheet: full set front / side / back / 3-4, each piece alone, the icons |
| `manifest.json` | file list, hashes, node names, counts |

`sheet_with_refs.png` (this folder) also shows Skyy's 3 reference images. **Local only — never commit it.**

Sizes, node names and triangle counts live in `manifest.json` (regenerate it rather than trusting a copy here).

## How to edit

1. Open `source/<Piece>.bbmodel` in Blockbench 5.2.1 with the Hytale Models plugin (0.10.0 used here).
2. Edit, then export the `.blockymodel` back over `Common/Items/Armors/SkyyDarkLeather/<Piece>.blockymodel`.
   The plugin writes `isPiece: false` onto box nodes; vanilla mostly omits it. Both load. Re-export the texture
   next to the model as `<Piece>_Texture.png`.
3. Or edit the generator and rebuild from scratch (deterministic — two runs give identical bytes):

```
python3 tools/art/make_dark_leather.py <this folder>
python3 tools/art/make_icons.py        <this folder>
python3 tools/art/make_sheet.py        <this folder>
python3 tools/art/make_manifest.py     <this folder>
python3 tools/art/validate.py          <this folder>   # structure, UVs, stretch, determinism
python3 tools/art/check_fit.py <model dir> <out.png>   # overlaps + body poke-through at rest
```

Geometry and paint live in `tools/art/dl_design.py` (one dict + one paint function per part); colours in
`tools/art/dl_paint.py` (`RAMPS`). Mirrored parts are declared once with `mirror=True` (R- side, or a name ending
in R); the build mirrors position, rotation and stretch and the copy shares the original's texels.

## Verified (Blockbench 5.2.1 + Hytale Models plugin 0.10.0)

- Each `.blockymodel` opens as `hytale_character`, auto-loads its `_Texture.png` at the right size, and the plugin's
  Validator reports no errors and no warnings.
- Re-exporting with the plugin codec reproduces every node, size, UV rect, position and rotation (within 0.001).
  The only difference: the plugin adds `settings.isPiece: false` on box nodes, which we omit. Vanilla does both.
- Imported as attachments onto the vanilla player model, every piece node attaches to the matching bone
  (Head; Pelvis/Belly/Chest/L-Arm/R-Arm; forearms + hands; pelvis + thighs/calves/feet).
  Player 21 cubes before, 64 after (+43), 4 collections (Head, Chest, Hands, Legs), all textures shown on the player.

## NOT verified

- Never loaded in the Hytale game or its item pipeline. No item / recipe JSON was written (art only).
- No walking / attack poses checked. The tabard and back panel hang from Pelvis, so they will pass through the
  thighs while walking — vanilla cloth does the same.
- Icons are software renders, not the game's own icon renderer.
- Cross-piece overlap at rest is in the same range as vanilla armor sets (hips vs hanging hands, belt vs breeches).
  See `tools/art/check_fit.py`.

## Open questions (defaults used)

| question | default used |
|---|---|
| output paths (no convention found in the repo) | `Common/Items/Armors/SkyyDarkLeather/` and `Common/Icons/ItemsGenerated/Armor_SkyyDarkLeather_*` |
| which shoulder gets the plate | LEFT |
| gem colour (the helmet ref shows blue) | amber / orange |
| gem fullbright | off |
| crown spikes | dropped (they added bulk); could return as one small prong per side |
| helmet type | leather half-helm with a painted visor (not a cloth hood) |
| tabard length | to about the knee; tattered hem |
| triangle budget (about 600 asked) | 540 (Head 96, Chest 216, Hands 96, Legs 132) |
