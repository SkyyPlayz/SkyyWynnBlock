# SkyWynn pets - 15 launch pets (ART-RESUME queue #7) - DRAFT

Status: **draft for Skyy's review, NOT committed.** Original art made by code (nothing copied, traced or recoloured from vanilla).
Look: "cute Hytale" (Skyy 2026-10-08: "keep the kinda hytale style, and make the pets cute"): chunky boxes, big heads,
big glinting eyes on the face, a soft blush, short legs, painted light (top-lit, violet shadows, warm highlights, no pure black/white).
Starts from the approved v2 box concepts (`research/cloud/pet-art/`), now as real models.

## v2 (2026-10-08): the 4 rideables redone
Skyy's review of v1: Horse, Camel, Ram, Mouflon "look a little weird"; make them more like Hytale's horses; Ram "dorky".
v2 keeps the cute-Hytale paint and friendly eyes, but the 4 rideables now follow real-animal / vanilla-horse proportions
(original models; vanilla pictures were only looked at, never copied):
- **Horse**: long thick neck + long head angled down, proper muzzle with noseband, dark mane strip + forelock, white blaze,
  taller legs, white feathered fetlock cuffs, chunky dark hooves, long dark tail. Blue saddle on top.
- **Camel**: two humps (Bactrian) with the saddle between them, S-curved neck with shaggy throat, droopy lip, knobby knees,
  wide padded feet, blue blanket with side drapes + tassels.
- **Ram**: tough war ram: big ridged horns curling round the sides of the head, heavy brow, narrow amber eyes (not scary),
  dark face, low heavy stance, thick wool chest, wool leg cuffs, steel chest plate with gold studs, red + gold saddle cloth.
- **Mouflon**: wild mountain sheep: short red-brown coat, pale saddle patch, white belly / rump / lower legs / muzzle,
  dark flank line + chest, big dark crescent horns; slim. Priest tack: cream cloth, gold trim, gold browband.
The other 11 pets are byte-identical to v1. Same ids, paths and animation names.

## The 15 pets (Pets-Spec section 5)
| # | Pet | Role | Height (1.0x) | Texture | Nodes / tris | Animations |
|---|---|---|---|---|---|---|
| 1 | Rabbit | skill - Farming | 0.68 block (ears) | 128x64 | 17 / 152 | Idle, Walk (hop), Run |
| 2 | Chicken | skill - Farming | 0.53 | 128x64 | 18 / 164 | Idle, Walk, Run |
| 3 | Goat | skill - Mining | 0.66 | 128x64 | 20 / 188 | Idle, Walk, Run |
| 4 | Warthog | skill - Mining | 0.48 | 128x64 | 19 / 176 | Idle, Walk, Run |
| 5 | Bear (cub) | skill - Foraging | 0.68 | 128x64 | 15 / 128 | Idle, Walk, Run |
| 6 | Turkey | skill - Foraging | 0.51 | 128x64 | 24 / 236 | Idle, Walk, Run |
| 7 | Wolf (pup) | combat | 0.65 | 128x64 | 18 / 164 | Idle, Walk, Run |
| 8 | Boar (striped boarlet) | combat | 0.41 | 128x64 | 15 / 128 | Idle, Walk, Run |
| 9 | Hawk | class - Archer | 0.53 | 128x32 | 18 / 164 | Idle (perched), Walk (hop), Fly |
| 10 | Ram (v2: war ram) | class - Warrior + mount | 1.01 | 256x160 | 46 / 500 | Idle, Walk, Run |
| 11 | Skrill ("stormwing", original) | class - Mage | 0.48 (hovers) | 128x64 | 21 / 200 | Idle (hover), Walk, Fly |
| 12 | Tusker (red war-hog) | class - Berserker | 0.54 | 128x64 | 21 / 200 | Idle, Walk, Run |
| 13 | Mouflon (v2: wild sheep) | class - Priest + mount | 1.17 | 256x96 | 41 / 440 | Idle, Walk, Run |
| 14 | Horse (v2) | mount | 1.55 | 256x192 | 45 / 488 | Idle, Walk, Run |
| 15 | Camel (v2: two humps) | mount | 1.64 | 256x160 | 47 / 512 | Idle, Walk, Run |

Heights are the Lv 100 (1.0x) size; Pets-Spec section 6 shrinks pets to 0.6x at Lv 1. Pebble (0.99 block) is the size peer:
small pets sit at about half of Pebble. The 4 rideables are bigger (v2): Ram ~1 block, Mouflon ~1.2, Horse ~1.55, Camel ~1.65.

## Files (laid out like the inside of a mod jar)
```
Common/NPC/SkyyPets/<Pet>/Models/<Pet>.blockymodel      model (Hytale character format, 64 px per block, shading flat)
Common/NPC/SkyyPets/<Pet>/Models/<Pet>_Texture.png      texture
Common/NPC/SkyyPets/<Pet>/Animations/Default/*.blockyanim   Idle / Walk / Run (Fly for Hawk + Skrill)
Common/Icons/ModelsGenerated/SkyyPets_<Pet>.png         128x128 model icon (3/4 view, premultiplied edges)
Common/Icons/ItemsGenerated/SkyyPets_Pet_<Pet>.png      64x64 pet item icon
source/<Pet>.bbmodel                                    Blockbench project (texture + animations inside)
sheet.png  manifest.json  README.md
```
The `Models/` subfolder is the vanilla layout: Blockbench auto-loads `../Animations/` when you open the model.

## Proposed ids (the pet system is not built yet - main session decides)
- Pet item: `SkyyPets_Pet_<Pet>` (icon above). NPC / model asset: `SkyyPets_<Pet>`. Name key: `skyypets.pet.<pet>.name`.
- Nameplate / level text: hang on `Head`. Rider seat (Ram, Mouflon, Horse, Camel): the `Saddle` node.
- All node names per pet are in `manifest.json`.

## How to edit
- Generator: `python3 tools/art/make_pets.py art/pets [Pet ...]` (geometry + paint in `pets_models.py`, animations in
  `pets_anims.py`). Then `make_pets_previews.py art/pets <review dir>` (icons + sheet), `make_pets_manifest.py`, `validate_pets.py`.
  Previews use `pets_render.py` (small software renderer). `bb_validate_pets.js` re-checks in Blockbench over its debug port
  and re-saves `source/*.bbmodel` (needs the `ws` node package; edit its require path).
  Deterministic: two runs give identical bytes. Needs Python 3 + numpy + Pillow.
- By hand: open `source/<Pet>.bbmodel` in Blockbench 5.2.1 + Hytale Models plugin, export with File > Export > Hytale Blockymodel.

## How it was checked
- Blockbench 5.2.1 + Hytale Models 0.10.0: all 15 open as Hytale Character, 0 validator errors/warnings, 0 console errors,
  textures auto-load at the right size, all 45 animations auto-load and bind to real nodes.
- `validate_pets.py`: 4375 checks (v2), 0 failures (node count, unique names, unit quaternions, UVs inside the texture and
  fully painted, textures multiple of 32, cut-out alpha, no pure black/white, icons 128/64 RGBA).
- Mirrored parts: Blockbench reads a mirrored face's `offset.x` as the RIGHT edge of the region. The generator writes it that way
  (checked in Blockbench screenshots).

## UNVERIFIED in game
1. Not tested in Hytale (no game client on the art box). Blockbench + plugin only.
2. NPC / model asset JSON (hitbox, eye height, walk speed, which anim plays when) is not here - main session writes it.
3. Animation names `Idle`, `Walk`, `Run`, `Fly` follow common vanilla names; the exact vanilla slot names are unchecked.
4. Mount seat offset on `Saddle`, and whether a mod can ride a custom model.
5. Runtime scaling 0.6x -> 1.0x by level (Pets-Spec 9 item 5).
6. Blinks use the vanilla-style 0.1 stretched lid quad.
