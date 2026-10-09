# Gathering armor: Foraging (one set per tree)

## Tier progression rule (all foraging tiers)

Skyy 2026-10-09: "Beautiful I want the armor sets consistent across the set, but each set should be a little different
visually, so they start simple and get a little cooler each set you get to that's better".

- One consistent family look across ALL tiers (same bark-plate armor, same fit).
- Trees in the same tier are EQUAL in coolness: only the wood colours, plate shape and mark change.
- Each higher tier is visibly a bit cooler than the last. F1 Grove = simple. F2 = a clear but modest step up.
  F3, F4 and F5 keep escalating (F5 the most impressive).

## OAK (F1 Grove)

**v2 (2026-10-09, APPROVED by Skyy: "they all look great!"):** repainted in the in-game Oak wood colours (Skyy: "make sure to
match each armor set to its in game wood variant." / "Yes, redo Oak and Birch to match their in-game wood"): red-brown
oak bark, orange-tan heartwood on cut rims, the game's oak-leaf green. Same models, shapes and acorn mark (textures only).

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

**v2 (2026-10-09, APPROVED by Skyy: "they all look great!"):** repainted in the in-game Birch wood colours (same Skyy quotes as
Oak v2): warm cream bark with soft vertical fibre streaks, grey-brown lenticels and knots (softer than v1's black),
pale tan heartwood, the game's lime yellow-green birch leaves. Same models, shapes and catkin mark (textures only).

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

## BEECH (F1 Grove)

Status: APPROVED by Skyy 2026-10-09 (v2): "Yes, the Beech armor looks good, commit it". Not yet seen in game.
v1 feedback (Skyy): "beech looks too much like iron, i need to look a little more like beech wood in the game".
Defaults kept: small copper accent leaf, warmer + lighter than Oak with vertical grain, loden-green cloth, husk badge on the crown.

![sheet](sheet-beech.png)

| What | Path |
|---|---|
| Models + textures | `Common/Items/Armors/SkyyForaging/F1_Grove/Beech/{Head,Chest,Hands,Legs}.blockymodel` + `<Piece>_Texture.png` |
| Icons (64x64) | `Common/Icons/ItemsGenerated/Armor_Foraging_Beech_{Head,Chest,Hands,Legs}.png` |
| Blockbench projects | `source/F1_Grove/Beech/{Head,Chest,Hands,Legs}.bbmodel` |
| Review sheet | `sheet-beech.png` |

- Same F1 family and the same fit as Oak (geometry derived from `tools/art/ga_oak.py` in `ga_beech.py`).
- Colours follow the in-game Beech wood (hues only, sampled from the game's Beech trunk / log end / planks / leaves;
  our own pixels): warm orange-brown bark with long vertical grain streaks and a few small knots, tan heartwood with a
  dark red-brown rim on cut edges, the game's fresh beech green leaves with one copper accent leaf per side, deep
  loden-green cloth.
- Reads as WOOD, not metal: every plank its own tone, gentle bevels (no bright hard rims), slightly wavy hand-cut plate
  edges with small notches and rounded corners.
- Beech mark: the BEECHNUT HUSK (pale spiky four-part husk split open around a dark nut) as the belt clasp, hanging on
  a twig with two beech leaves, plus a small husk badge at the base of the middle crown point.
- Shape vs Oak (jagged) and Birch (rounded): broad overlapping wooden plates, leaf-shaped crown points, a second plate
  on each shoulder, broad tassel panels, smooth beech belt, beech leaves on the right shoulder + vine on the left.
- Size: 47 boxes + 13 quads. Textures Head 96x128, Chest 96x128, Hands 96x32, Legs 96x64.
- Checked the same way as Oak and Birch (structure PASS, byte-identical rebuild, fit, Blockbench + Hytale plugin: no
  validator issues, all 4 pieces attach to the vanilla player). Not checked in game.

## ASH (F1 Grove)

Status: APPROVED by Skyy 2026-10-09: "they all look great!". Not yet seen in game.
Defaults kept: five seed keys on the belt, slate cloth, bark matched to the game.

![sheet](sheet-ash.png)

| What | Path |
|---|---|
| Models + textures | `Common/Items/Armors/SkyyForaging/F1_Grove/Ash/{Head,Chest,Hands,Legs}.blockymodel` + `<Piece>_Texture.png` |
| Icons (64x64) | `Common/Icons/ItemsGenerated/Armor_Foraging_Ash_{Head,Chest,Hands,Legs}.png` |
| Blockbench projects | `source/F1_Grove/Ash/{Head,Chest,Hands,Legs}.bbmodel` |
| Review sheet | `sheet-ash.png` |

- Same F1 family and the same fit as Oak (geometry derived from `tools/art/ga_oak.py` in `ga_ash.py`).
- Colours follow the in-game Ash wood (hues only, sampled from the game's Ash trunk / log end / hardwood planks /
  leaves; our own pixels): dark plum-brown bark with lighter ridges around long narrow diamond furrows (ash bark),
  pale tan heartwood on cut edges, the game's deep blue-green ash leaves (pinnate: leaflet pairs on a stem),
  straw-tan seed keys, cool slate cloth.
- Ash mark: the SAMARA cluster - 5 winged seed keys fanning down from a carved heartwood clasp on the belt, and a
  bunch of 3 keys at the left temple.
- Shape vs Oak (jagged), Birch (rounded), Beech (broad smooth): CHEVRON plates (each plate ends in a shallow V, rows
  offset so they make a diamond lattice), V-pointed hems, samara-wing crown points, a raised ridge along each shoulder.
- Size: 47 boxes + 13 quads. Textures Head 96x128, Chest 96x128, Hands 96x32, Legs 96x64.
- Checked the same way as the others (structure PASS, byte-identical rebuild, fit, Blockbench + Hytale plugin: no
  validator issues, all 4 pieces attach to the vanilla player). Not checked in game.

## ASPEN (F1 Grove)

Status: APPROVED by Skyy 2026-10-09: "Yes, the Aspen armor looks good, commit it". Not yet seen in game.
Defaults kept: golden leaves, russet cloth, eye scars as drawn.

![sheet](sheet-aspen.png)

| What | Path |
|---|---|
| Models + textures | `Common/Items/Armors/SkyyForaging/F1_Grove/Aspen/{Head,Chest,Hands,Legs}.blockymodel` + `<Piece>_Texture.png` |
| Icons (64x64) | `Common/Icons/ItemsGenerated/Armor_Foraging_Aspen_{Head,Chest,Hands,Legs}.png` |
| Blockbench projects | `source/F1_Grove/Aspen/{Head,Chest,Hands,Legs}.bbmodel` |
| Review sheet | `sheet-aspen.png` |

- Same F1 family and the same fit as Oak (geometry derived from `tools/art/ga_oak.py` in `ga_aspen.py`).
- Colours follow the in-game Aspen wood (hues only, sampled from the game's Aspen trunk / log end / softwood planks /
  golden aspen leaves; our own pixels): pale khaki-cream bark with soft horizontal bands, short dark dashes and dark
  EYE-SHAPED scars (aspen bark), pale cream heartwood with rings, the game's golden-orange aspen leaves, russet cloth
  (the colour of the aspen's softwood planks).
- Aspen mark: TREMBLING ROUND LEAVES - 4 round golden leaves on long stalks hanging at different angles from a carved
  heartwood clasp on the belt, plus a bunch of 3 at the left temple and single leaves on the shoulder, bracers and crown.
- Shape vs Oak (jagged), Birch (rounded), Beech (broad smooth), Ash (chevrons): SLENDER TALL VERTICAL SLATS - narrow
  upright plates with thin gap lines, ending at staggered lengths with rounded tips and open gaps at the hems (light,
  airy); slim round-topped spire crown points; longer slat tassels.
- Size: 45 boxes + 12 quads. Textures Head 96x128, Chest 96x128, Hands 96x32, Legs 96x64.
- Checked the same way as the others (structure PASS, byte-identical rebuild, fit, Blockbench + Hytale plugin: no
  validator issues, all 4 pieces attach to the vanilla player). Not checked in game.

## Rebuild
```
GA_DESIGN=ga_oak   python3 tools/art/make_foraging_armor.py      # models + textures (design ga_<tree>.py, painter ga_paint.py)
GA_DESIGN=ga_birch python3 tools/art/make_foraging_armor.py
GA_DESIGN=ga_beech python3 tools/art/make_foraging_armor.py
GA_DESIGN=ga_ash   python3 tools/art/make_foraging_armor.py
GA_DESIGN=ga_aspen python3 tools/art/make_foraging_armor.py
python3 tools/art/make_foraging_icons.py art/gathering-armor F1_Grove Birch
python3 tools/art/make_foraging_sheet.py art/gathering-armor F1_Grove Birch
GA_TREE=Birch python3 tools/art/validate_foraging.py
python3 tools/art/make_foraging_manifest.py                      # one shared manifest for every tree
```
