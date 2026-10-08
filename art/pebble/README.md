# Pebble - the talking rock NPC (SkyWynn)

Pebble is the SkyWynn guide: a talking rock who has been "here four thousand years". He stands in the Waiting Square
in front of the Zone 1 temple and walks new players through the starter shards.

This folder is laid out like the inside of a mod jar. Copy `Common/` straight into the mod.
All geometry and pixels are original. No vanilla file was copied, traced or recoloured. The vanilla Rabbit was
only used to check scale, file format, folder layout and node naming.

## What you get

| File | What it is |
|---|---|
| `Common/NPC/SkyyTowns/Pebble/Pebble.blockymodel` | The model: 25 nodes, Hytale character format (64 units = 1 block) |
| `Common/NPC/SkyyTowns/Pebble/Pebble_Texture.png` | The texture: 256 x 192, painted light and shadow, cut-out alpha |
| `Common/Icons/ModelsGenerated/Pebble.png` | The model icon: 128 x 128, 3/4 view like the vanilla model icons |
| `Common/NPC/SkyyTowns/Pebble/Animations/Default/Idle.blockyanim` | Slow breathing wobble, sprout sway, a blink (3.0 s, loops) |
| `.../Animations/Default/Walk.blockyanim` | Waddle: the rock rolls from foot to foot (0.67 s, loops) |
| `.../Animations/Default/Talk.blockyanim` | Mouth opens and closes, little head bounce, brows and arm gestures (0.67 s, loops) |
| `.../Animations/Default/Wave.blockyanim` | A hop, then a pebble-arm wave with happy squinting eyes (1.07 s) |
| `.../Animations/Damage/Hurt.blockyanim` | A wince: leans back, eyes shut, brows down (0.4 s) |
| `.../Animations/Damage/Death.blockyanim` | Crumbles into a pile, then pops back together (1.6 s, holds the last frame) |
| `source/Pebble.bbmodel` | Blockbench project with the texture and all 6 animations inside |
| `sheet.png` | Review sheet: front, side, back, icon and one frame of each animation |
| `manifest.json` | Every file with its size; node names; animation lengths |

## Sizes

- **Height:** 63 units = **0.99 blocks**, from the ground to the sprout tip. The rock body stops at about 0.8 blocks.
  That puts the top of the body at about hip height on a player (knee to hip).
- **Footprint:** 61 x 45 units (0.95 x 0.71 blocks), including the little arms.
- **Texture:** 256 x 192. That is more than the vanilla Rabbit (160 x 160).
  Density is 1 texel per unit, the same as every vanilla creature.
  Both sides are multiples of 32. Every face's UV is exactly the face size (the plugin's UV-lock rule).
- **Nodes:** 25 (the limit is 255). Geometry is boxes and flat quads only. Rest-pose stretch is 1.0, except the
  two hidden blink lids (see below).

## Node names (for nameplates, chat bubbles and effects)

The character faces +Z. `R-` means Pebble's own right side (the -X side), the same as vanilla.

- `Origin` - the empty root node at ground level.
- `Body` - the lower rock half. Its pivot sits near the ground so the whole rock can roll when it waddles.
  - `Body-Wide` and `Body-Base` give the lower half its rounded shape.
  - `L-Foot` and `R-Foot` are the two stubby feet.
  - `L-Arm` and `R-Arm` are the two little pebble arms.
  - **`Head`** is the upper rock half and carries the face. **Hang the nameplate and chat bubble on this node.**
    - Its pivot is 21 units above the ground and its top is at 44 units.
    - The highest point of the model (the sprout) is 63 units up. A nameplate about 45 units above the
      `Head` pivot clears the sprout.
    - `Head-Wide`, `Head-Bulge`, `Head-Top` and `Crown` round off the top half.
    - `Moss-Cap` and `Moss-Tuft` are the moss clumps. `Sprout`, `Sprout-Leaf-L` and `Sprout-Leaf-R` make the sprout.
    - The face is `L-Eye`, `R-Eye`, `L-Eyelid`, `R-Eyelid`, `Mouth`, `L-Brow` and `R-Brow` (the moss eyebrows).

## How to edit

- **In Blockbench** (with the Hytale Models plugin): open `source/Pebble.bbmodel`.
  - When you are done, use File > Export > Export Hytale Blockymodel.
  - Export each animation with Animation > Export Blockyanim.
  - Save the texture as `Pebble_Texture.png`.
- **With the generator** (the way these files were made): run `python3 tools/art/make_pebble.py art/pebble`.
  - Then run `python3 tools/art/make_pebble_previews.py art/pebble <preview dir>` for the icon and sheet.
  - Then run `python3 tools/art/validate_pebble.py art/pebble` to check the files.
  - Geometry is in `pebble_model.py`, animations in `pebble_anims.py`, and the texture painting in `make_pebble.py`.
  - The scripts are deterministic: two runs give identical bytes.
  - The scripts need Python 3 with numpy and Pillow.
- **Opening `Pebble.blockymodel` directly in Blockbench:** the plugin auto-loads animations from `../Animations/`
  next to a model. Vanilla keeps its models in a `Models/` subfolder. With the path asked for here
  (`Pebble/Pebble.blockymodel`), Blockbench will not find the animations by itself. Load them with
  Animation > Import, or open the `.bbmodel` instead.

## How it was checked

- **Blockbench 5.2.1 with the Hytale Models plugin 0.10.0:**
  - The `.blockymodel` opened as a Hytale Character with no console errors and no failed validator checks.
    Those checks cover node count and texture/UV size.
  - It shows 25 groups, the 256 x 192 texture was auto-loaded, and the UV size matches the texture.
  - All 6 `.blockyanim` files loaded and bound to real nodes. All 371 keyframes match the files.
  - Exporting from Blockbench gives back the same nodes, positions, rotations, sizes and UVs as the file (0 differences).
  - The `.bbmodel` re-opens with the texture and animations and exports the same model again.
- **Key-by-key schema check against the vanilla Rabbit files:** every key used here is also used by vanilla.
  - The one extra key is the top-level `"format": "character"`, which the plugin itself writes on export.
  - The animation files use the same top-level keys and the same 5 channels as vanilla.
- **Texture rules:** no pure black or white, shadows shift toward blue-violet, light is painted in from above,
  and the colour patches are flat (no grain).
- **Previews:** `sheet.png` comes from a small renderer that reads the real files.
  Side-by-side Blockbench screenshots of the same poses match it. Lighting is approximate.

## UNVERIFIED in game

1. **Not tested in Hytale itself.** There is no game client on the art machine. Everything above was checked in
   Blockbench plus the plugin only.
2. **The NPC / model asset JSON is not part of this folder.** It sets the hitbox, eye height, nameplate offset,
   which animation plays when, and walk speed. The main session writes it.
3. **`Talk` and `Wave` are custom animation names.** Vanilla creatures have no slots with these names.
   How they get triggered (dialogue, greeting) is up to the main session.
4. **Walk speed:** one waddle cycle is 0.67 s and each foot slides 6 units. The playback speed may need tuning to
   match Pebble's move speed.
5. **Blink and mouth use stretch:**
   - The blink lids rest at stretch 0.1, exactly like the vanilla Rabbit's eyelids.
   - The mouth stretches up to 2.6x tall while talking, so its pixels stretch during speech.
   - This is the same method vanilla uses for blinks, but the in-game look is unchecked.
6. **Cut-out pixels on the quads:** the corners of the eyes, lids and mouth are transparent. This relies on cut-out
   alpha on quads. The vanilla texture also uses 0/255 alpha.
7. **Death then "pop back":** the game may despawn the NPC right after Death and cut off the pop-back. It works
   best if Pebble cannot actually die.
8. **Icon:** the framing copies the vanilla model icons (3/4 view, sitting on the bottom edge). Edge pixels are
   premultiplied, which is what the vanilla icon's edge pixels look like. The game's icon pipeline itself was not
   checked.
9. **Shading:** every node uses the `flat` shading mode, like the vanilla Rabbit. In-game light, bloom and AO will
   look a bit different from the previews.

## Open questions for Skyy (my default in brackets)

1. **Size** - 0.99 blocks to the sprout tip, body to hip height. OK? [keep]
2. **Face** - dot eyes, a smile, moss eyebrows and a faint warm blush on the cheeks. Keep the blush? [keep it, it is subtle]
3. **Arms** - Pebble has two tiny pebble arms, used for the wave and talk gestures. Keep them, or go hop-only with no arms? [keep the arms]
4. **Top** - patchy moss with drips, plus one two-leaf sprout. More or less moss? [keep as is]
5. **Can Pebble die?** - Hurt and Death are made, but a guide NPC is usually invulnerable. [make Pebble invulnerable and keep Death as a spare gag]
6. **File layout** - `Pebble/Pebble.blockymodel` as asked, or the vanilla style `Pebble/Models/Model.blockymodel`?
   The vanilla style lets Blockbench auto-load the animations. [keep the requested path]
