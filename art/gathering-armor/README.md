# Gathering armor: Foraging (one set per tree)

## OAK (F1 Grove)

Status: APPROVED by Skyy 2026-10-08: "Yes, the Oak armor looks good, commit it". Not yet seen in game.

Skyy: "lets still make the farming and gathering armor, but use vanilla for mining, and armory for combat gear."
Skyy: "do a design per tree type in that set, so every hardwood gets its own design in that trees color"

![sheet](sheet-oak.png)

## Files
| What | Path |
|---|---|
| Models + textures | `Common/Items/Armors/SkyyForaging/F1_Grove/Oak/{Head,Chest,Hands,Legs}.blockymodel` + `<Piece>_Texture.png` |
| Icons (64x64) | `Common/Icons/ItemsGenerated/Armor_Foraging_Oak_{Head,Chest,Hands,Legs}.png` |
| Blockbench projects | `source/F1_Grove/Oak/{Head,Chest,Hands,Legs}.bbmodel` (textures embedded; one folder per tree so the shared `source/` never clashes) |
| Review sheet | `sheet-oak.png` |
| Hashes, node lists | `manifest.json` |

Path note: ART-RESUME has two spellings for the icon names. This uses the tree-name one from the
Foraging bullet: `Armor_Foraging_<Tree>_<Piece>.png`.

## Look
- Copper-tier echo (tier 1) from the approved concept: layered bark plates with jagged edges, a laced
  gap down the chest with a faint green sap vein, a twisted vine belt, jagged bark tassels front and back.
- Oak colours: grey-brown furrowed oak bark, pale cut-oak rims, oak-leaf green, twine rope, moss-grey cloth.
- Oak extras: an acorn belt clasp and an acorn badge on the helmet.
- Head: open-face bark helmet with a brim, a small 3-point bark crown and 2 oak leaves (face stays visible).
- Chest: bark cuirass, 2 breast plates, rounded bark shoulder plates, ONE vine with 2 leaves over the LEFT shoulder, cloth sleeves with rope bands.
- Hands: bark bracers with rope bands, fingerless rope-wrapped bark gauntlets.
- Legs: moss-grey cloth trousers, bark knee caps, bark greaves with 2 rope bands, bark boots with a rope wrap.
- Not bulky: plates sit about 1 unit off the body, same as the Dark Leather set.

## Format
Hytale `.blockymodel` "character" attachments (root nodes named after player bones, `isPiece`), 64 units per
block, 1 texel per unit (same density as vanilla armor), integer box sizes, flat shading, textures in 32 px steps.
Mirrored L-/R- parts share texels (negative stretch, no mirror flag). Original geometry and pixels only.

| Piece | Boxes | Leaf quads | Texture |
|---|---|---|---|
| Head | 10 | 2 | 96x128 |
| Chest | 18 | 2 | 96x128 |
| Hands | 8 | 0 | 96x32 |
| Legs | 9 | 0 | 96x64 |

## Checked
- `validate_foraging.py`: structure, UVs in bounds / no overlaps, alpha 0/255 only, no pure black or white,
  textures in 32 px steps, icons 64x64, byte-identical rebuild. PASS.
- `check_fit_foraging.py`: rest-pose fit on the player rig. Remaining overlaps are only arms touching the torso at rest
  (like vanilla) and the front tassels just touching the trousers (0.07 units).
- Blockbench 5.2.1 + Hytale Models plugin 0.10.0: every piece opens as `hytale_character` with no validator warnings
  and no console errors; the plugin's own "Import Attachment" puts all 4 pieces on the right bones of the vanilla
  player; re-export round trip matches (only the plugin's added `isPiece: false` flags differ).
- NOT checked in game yet.

## Decisions (Skyy kept every default, 2026-10-08)
1. Tier folder name: `F1_Grove` (default). Could be `Grove` or `T1` instead.
2. Helmet: open-face bark helmet with the crown on it (ART-RESUME default "helmet in every tier"). The design doc
   only has a bark crown. Easy to switch to crown-only.
3. Sap glow: very faint (tier 1). Could be stronger.
4. Acorn clasp + acorn helmet badge as the Oak mark (default yes).
5. Vine with leaves on the LEFT shoulder only (concept). Could be both shoulders.
6. Front tassels pass through the legs when walking (vanilla skirts do too).
7. No item / recipe JSON yet: art only.

## BIRCH (F1 Grove)

Status: APPROVED by Skyy 2026-10-09: "Yes, the Birch armor looks good, commit it". Not yet seen in game.
Defaults kept: separate models per tree, catkins as the mark, rounded edges, vine + faint sap kept.

![sheet](sheet-birch.png)

| What | Path |
|---|---|
| Models + textures | `Common/Items/Armors/SkyyForaging/F1_Grove/Birch/{Head,Chest,Hands,Legs}.blockymodel` + `<Piece>_Texture.png` |
| Icons (64x64) | `Common/Icons/ItemsGenerated/Armor_Foraging_Birch_{Head,Chest,Hands,Legs}.png` |
| Blockbench projects | `source/F1_Grove/Birch/{Head,Chest,Hands,Legs}.bbmodel` |
| Review sheet | `sheet-birch.png` |

- Same F1 family and the same fit as Oak (geometry derived from `tools/art/ga_oak.py` in `ga_birch.py`).
- Colours: off-white papery birch bark (never pure white), charcoal lenticel dashes and black knot "eyes", pale
  yellow heartwood where the bark peels, light spring-green leaves, cool sage cloth.
- Birch mark: hanging CATKINS. 3 hang under a carved heartwood knot clasp on the belt, and 2 hang at the left temple of the helmet.
- Shape changes vs Oak: taller, thinner 3-point crown; ROUNDED (scalloped) plate edges and hems instead of jagged;
  rolled-bark curls along both shoulder plates and the tops of the front tassels; a twisted birch-bark belt (no ivy);
  small twig sprigs (2 leaves) tucked into the bracer rope bands; toothed birch leaves.
- Ideas from studying The Armory mod (nothing copied): long smooth grain bands instead of speckle, a soft outline +
  light rim on every plate edge, and alpha-cut quads for small silhouette details (catkins, sprigs) so nothing gets bulky.
- Size: 48 boxes + 11 quads. Textures Head 96x128, Chest 96x128, Hands 96x32, Legs 96x64.
- Checked the same way as Oak (structure PASS, byte-identical rebuild, fit, Blockbench + Hytale plugin: no validator
  issues, all 4 pieces attach to the vanilla player). Not checked in game.

## Rebuild
```
GA_DESIGN=ga_oak   python3 tools/art/make_foraging_armor.py      # models + textures (design ga_<tree>.py, painter ga_paint.py)
GA_DESIGN=ga_birch python3 tools/art/make_foraging_armor.py
python3 tools/art/make_foraging_icons.py art/gathering-armor F1_Grove Birch
python3 tools/art/make_foraging_sheet.py art/gathering-armor F1_Grove Birch
GA_TREE=Birch python3 tools/art/validate_foraging.py
python3 tools/art/make_foraging_manifest.py                      # one shared manifest for every tree
```
