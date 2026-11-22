# Shard clicker art - Hytale look (sample for Skyy, 2026-11-22)

Skyy 2026-11-22 (on the Combat clicker screenshot): "please upgrade all the visuals in all the clickers. i want the islands, the totems
and the monsters to all lo9ok like and match the Hytale look and feel." Same day, locked: every shard clicker becomes ONE island per zone
(the zone's crops / ores / mobs / animals / fruits are upgrades of that island). This is STEP 1 (a sample sheet to approve); the build round
comes after Skyy's answer.

## Files

| File | What | In git? |
|---|---|---|
| `make_clicker_art.py` | the generator (pure Python, deterministic: two runs = same bytes) | yes |
| `clicker-hytale-samples-own.png` | sample sheet, OUR OWN drawing in the voxel style (our painted textures, our voxel monsters / totem / spirit) + today's art on the right | yes |
| `clicker-art/clicker-hytale-samples.png` | sample sheet built from the REAL game art (Hytale block textures + the game's model icons, read from Assets.zip) + today's art | NO - `clicker-art/` is git-ignored (vanilla-derived) |

Run: `python research/ui-theme-art/make_clicker_art.py` (~15 s; Assets.zip read-only; today's art is read from the built
`SkyyShards-0.4.29.jar`).

## What the samples show (left = new, right = today's 0.4.29 art)

- (A) Combat Zone 1 town island (Medium, 700 x 400): a voxel floating island block by block - grass top, dirt, stone (mossy near the top,
  darker deep stone underneath), sides darken with depth, warm sunlit tops / cool shaded sides; voxel houses (plank walls, log corners, lit
  windows, door, stepped roof), a cobble watch tower, voxel trees, a cobble road, grass tufts + flowers. Four monsters stand on it, and the
  same four as the page's 110 x 140 cards: vanilla sheet = Rat, Spider, Skeleton Fighter, Trork Warrior (the game's own model icons); own
  sheet = our voxel Rat, Spider, Skeleton, Goblin.
- (B) Spirit totem (120 x 220, as ClkTotem): a voxel totem pole (stone plinth, carved log with two glowing faces, plank wings, glowing spirit
  block) with its spirit floating above (vanilla sheet: the game's Spirit_Root = Lumber spirit; own sheet: our voxel root spirit).
- (C) Farming Zone 1 island (Small, 520 x 300) with 3 crop plots (tilled soil framed by planks): wheat, carrot, lettuce.

## How the build round would make the real pictures (never committed)

1. Move the renderer (Vox, island / house / tree / totem models, resize, crop) into the SkyyShards build as the new `CLK_ART_SRC` part, the
   way 0.4.23-0.4.28 draw today's art; it reads Assets.zip at build time (`tools/skyyart.py` `assets()` + `png_decode`) and writes PNG bytes
   straight into the jar (`Common/UI/Custom/SkyyShards/Map/Clk*.png`). No vanilla-derived PNG ever lands in the repo (PROJECT-RULES 2).
2. Sources (all checked in Assets.zip 2026-11-22): `Common/BlockTextures/` Soil_Grass_Sunny (+ _Side), Soil_Dirt, Rock_Stone (+ _2, _Mossy),
   Rock_Stone_Cobble_Side, Soil_Dirt_Tilled, Wood_Village_Wall_01, Wood_Lightwood / Hardwood_Planks, Wood_Apple_Trunk_Side; roofs
   `Common/Blocks/Structures/Roofs/Slope_Textures/Redwood.png`; leaves `Common/Blocks/Foliage/Leaves/Ball_Textures/Oak.png`;
   monsters / spirits / animals `Common/Icons/ModelsGenerated/<Role>.png` (128 x 128) - ALL 62 Combat roles of today's CZ_POOL + Trork_Warrior
   have one, as do Spirit_Root / Ember / Frost / Thunder and every ranch animal (Chicken, Cow, Pig, Boar, Sheep, Turkey, Goat, Bison);
   crops `Common/Icons/ItemsGenerated/Plant_Crop_<Crop>(_Stage_4).png`. Zone looks from the zone's own blocks (Zone 2 sand, Zone 3 snow /
   cold grass, Zone 4 burnt soil ...: `Soil_Grass_Cold_*`, `Soil_Grass_Burnt_*`, `Soil_Dirt_Burnt` exist).
3. One island per zone: ONE base island picture per zone (its zone's ground blocks), SHARED by every shard, and each shard's things drawn
   as separate small pictures on the island's spots (as trees / nodes / monsters are today): houses + tower (Combat), quarry terraces + ore
   nodes (Mining), plots (Farming), trees (Foraging / Orchard), pens (Ranching). Upgrades (more crops / ores / mobs / animals) = more spots
   filled, never a new island picture.
4. Monsters: one 110 x 140 card per vanilla ROLE (62) from its model icon, cropped, soft top light, ground shadow - replaces today's 32
   family x tint drawings, so every monster looks exactly like the game's.

## Sizes vs the page + picture budget (tools/ci/ui_budget.py: SET 26.60 Mpx today, WARN > 45, FAIL > 60)

| Pictures | Today (0.4.29) | Proposed | Mpx today -> proposed |
|---|---|---|---|
| Monsters | 32 @2x 220 x 280 | 62 per role @1x 110 x 140 (the icons are 128 px - @2x adds nothing) | 1.97 -> 0.95 |
| Islands | 9 (Isl / QIsl / TIsl x 3 sizes) | 5 zone bases x 3 sizes, shared by all shards | 2.63 -> 4.38 (one size per zone, page-scaled: 2.20 - UNVERIFIED that the page scales cleanly) |
| Crops / trees / stumps / nodes / rubble | 67 @2x 220 x 280 | the same at @1x 110 x 140 | 4.13 -> 1.03 |
| Island features (houses, tower, plots, terraces, pens) | inside the island pictures | ~20 small @1x pictures | 0 -> ~0.30 |
| Totem / spirit | 1 + 1 | 1 totem + 4 spirits | ~0.05 -> ~0.08 |

Estimate: SkyyShards 11.37 -> about 9.3 Mpx (7.1 with one island size per zone); the SET about 24.5 Mpx (well under 45). Everything at @2x would add ~6 Mpx (still under 45, not
needed for 128 px sources).

## Open questions for Skyy (default in [brackets])

1. Which look - the game's own art (vanilla textures + the game's model icons, built into the jar at build time, never in the repo) or our
   own voxel drawings in the same style? [the game's own art - it matches Hytale exactly and every monster / animal / spirit already exists]
2. Island camera - the blocky isometric view of the sample (sides and layers visible) or flatter / more top-down like today?
   [the sample's isometric view]
3. Monster pictures - one per monster (62, each the real model) or one per family as today (rat, wolf, spider ...)? [one per monster]
4. Combat town extras - houses + watch tower + trees + road as drawn, or also walls / a gate that grow with Town level? [as drawn now;
   walls / gate with Town level later]
5. Spirits - the game's spirits for the totems (Root = Lumber / Harvest, Ember = Quarry, Frost, Thunder ...)? [yes: Root for Foraging /
   Farming / Orchard / Ranching, Ember for Mining, Thunder for Combat]
6. Zone islands - one base island per zone shared by every shard (Zone 1 grass, Zone 2 sand, Zone 3 snow, Zone 4 burnt, Zone 5 ...), each
   shard adding its own things on top? [yes, shared bases]
