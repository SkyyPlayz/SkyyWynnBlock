# SkyWynn UI sky mockups - "Isles of the Void" tooltip + slot directions (CONCEPT)

**Status: concept mockups for Skyy to pick a direction. These are not final assets. Nothing is wired in and nothing is committed.**
All pixels are original. No vanilla file was copied, traced or recoloured; vanilla files were only read to check sizes and borders.

Skyy (2026-10-10): "how about we come up with several approaches, and for the Isles of the void theams, make some simple mockups, and
refile from there. your menu item was really cool, i liked how the thing on top glowed, and the water was sparkly. im picturing a
lighter softer look, maybe like flowing clouds, with softer light glowy almost water color magic looking swirls and shapes. (then for
the rarities, you keep the clody/ sky theme so some get more stormy, some get more sunny. but they all kinda match the color theme,
legendary could have blue lighting, mythic its night, and the clouds open up to show a magical stary/ galactic scene bordered by
clouds shining purple from the purple moon."

- Sheet: `sheet.png` (3282 x 2412). It has 4 columns, one per approach. Each column shows:
  - a Legendary tooltip and a Mythic tooltip at real size, with sample text, on a light in-game sky;
  - the raw 107 px textures at x3, with the 9-slice cuts dashed;
  - 8 slot frames at @2x, and 4 more at 1x;
  - the 8 rarity moods as small 1x tooltips;
  - the engine limits for that approach.
- Generator: `python tools/art/make_ui_sky_mockups.py`. It is pure Python with no Pillow, uses every CPU core, takes about 20 s, and is
  deterministic (two runs give identical bytes). It reuses `emblem_png.py` and `make_tooltip_frames.py` (Canvas, nine_slice,
  placeholder sword).
- Every mock tooltip is a real 107 x 107 @2x 9-slice texture, built the same way as `art/tooltip-frames/`. The generator checks that
  the stretch strip (columns and rows 48..58) is uniform. The sheet then 9-slices it the way the client does: 48 px corners stay
  fixed and the edges and centre stretch. **What you see is what the engine can actually show.**

## The big engine fact behind every approach
The tooltip texture has only **four 24 x 24 UI-unit corners** of free art. The edges and centre are stretched, not tiled, so anything
placed along an edge smears.

A real tooltip is 320-480 UI units wide. The ornaments are therefore small next to the box: compare the x3 raw textures with the 1:1
heroes on the sheet. Every approach keeps its mood art (sun, storm, galaxy, island) in the corners. The stretched parts can only hold
things that look the same along the whole edge: smooth cloud rolls, gold lines, sky-gradient ribbons and watercolour streaks.

The text area must stay dark. The text colours are fixed (white, grey, green, red, gold, aqua and the rarity colour), so a light
"parchment-sky" centre would make them unreadable. Every approach therefore uses a soft, 98 % opaque, mood-tinted twilight panel. The
"lighter, softer" look lives in the frame.

## Rarity moods (shared by all four approaches)
| Rarity | Mood | Sky and extras |
|---|---|---|
| Normal (#FFFFFF) | CLEAR DAY | soft blue sky, white clouds, small sun top left |
| Unique (#FFFF55) | GOLDEN SUN | warm golden horizon, bigger sun with rays |
| Rare (#FF55FF) | PINK DRIFT | cloudier: more puffs, pink / lavender cotton clouds |
| Legendary (#55FFFF) | BLUE STORM | slate storm clouds, **blue lightning** bolts |
| Fabled (#FF5555) | RED TEMPEST | darker crimson thunderheads, red-gold lightning |
| Mythic (#CC66CC) | STAR NIGHT | night: **the clouds part on galaxy holes** (nebula and stars), and the **purple moon** sits top right, rim-lighting the clouds purple |
| Set (#55FF55) | GREEN DAWN | mint dawn clouds, green aurora ribbon, pale dawn sun |
| Untiered (#FFAA00) | EMBER SUNSET | orange sunset (the sun is low, bottom left), floating embers |

## The 4 approaches

### 1 CLOUD FRAME
- **Look:**
  - two soft rolled cloud bands run around the box;
  - big puffy clouds sit in each corner, with a watercolour glow halo in the rarity colour;
  - the text panel is a flat twilight blue, with a soft rarity glow on its edge;
  - the mood lives in the corner puffs: a sun peeking out, a bolt across the puffs, or the Mythic galaxy hole with the moon.
- **Engine limits:**
  - puffs fit only in the corners;
  - the edges are smooth, featureless cloud rolls, so wide tooltips show long plain runs between the puffs;
  - the clouds cannot "flow" or animate, because tooltip textures are static.
- **Strength:** closest to "flowing clouds", and the most obviously "sky".
- **Risk:** at 1x the corner puffs are small, so the frame reads mostly as a soft pale rim.

### 2 SKY WINDOW
- **Look:**
  - a thin ornate gold frame in the emblem gold, with a soft sky-gradient ribbon between two gold lines;
  - each corner is a round gold-ringed **window onto a tiny sky scene** in the rarity mood: sun or moon and storm at the top, a
    floating isle with a waterfall over a cloud sea at the bottom;
  - a glowing gold star point is aimed out of each corner ("the thing on top glowed").
- **Engine limits:**
  - the window is about 13 UI units across, so the scenes are tiny at 1x;
  - there can be no crest or ornament at the top centre, because the edges stretch;
  - in return, the gold lines stay crisp at any tooltip size.
- **Strength:** the most "premium" and readable look, closest to the menu emblem.
- **Risk:** the least "soft and watercolour".

### 3 WATERCOLOUR SWIRL
- **Look:**
  - no hard frame;
  - a pale watercolour sky wash, whose stretched edges turn into **flowing streaks** (bands that run along the edge, like wind lines);
  - pigment blooms with darker, dried-paint rims in the corners;
  - glowing magic spiral swirls and sparkles;
  - the panel is a soft, feathered ink pool with no outline;
  - Mythic's blooms become galaxy pools.
- **Engine limits:**
  - blooms and swirls fit only in the corners;
  - any texture along an edge can only run along that edge (streaks), never across it;
  - it uses soft partial alpha almost everywhere. Vanilla only uses soft alpha in its shadow, so **the blending needs an in-game check**.
- **Strength:** the closest match to "softer light glowy almost water color magic looking swirls".
- **Risk:** soft alpha over a busy world can look muddy, and the frame is the least "sky island" of the four.

### 4 FLOATING ISLE
- **Look:**
  - a soft sky-blue rim and a thin gold line;
  - **tiny floating islands with waterfalls** hang off the bottom corners, with sparkly mist, like the menu emblem;
  - a glowing 8-point gold compass star sits top left (the emblem's star);
  - the mood's sky object sits top right: sun, storm cloud with lightning, or the purple moon in a galaxy hole.
- **Engine limits:**
  - each island must fit inside a 24 UI corner;
  - the waterfall ends at the texture edge;
  - the arrow is placed by the client and overlaps the bottom rim, so on a narrow tooltip it can sit on a bottom island.
- **Strength:** the most "Isles of the Void"-specific, and ties straight back to the menu emblem.
- **Risk:** the islands are very small at 1x.

## Text contrast (measured by the generator on the centre colour composited over a light sky, worst case)
The table gives the lowest contrast of white, grey 170, green, red, gold, aqua and the rarity colour. In every case the lowest value
comes from **red** (#FF5555).

| | Normal | Unique | Rare | Legendary | Fabled | Mythic | Set | Untiered |
|---|---|---|---|---|---|---|---|---|
| all 4 approaches | 5.1 | 5.1 | 5.3 | 5.2 | 5.5 | 5.7 | 4.8 | 5.2 |

Everything passes the AA level of 4.5:1. Two notes:
- The dim "Can be reforged" grey (130) reaches 3.9-4.9:1. That is fine for a de-emphasised line, and passes 3:1 for large text.
- The watercolour pool would drop to about 4.2 if it were 93 % opaque, so it is kept at 98 % like the others.

## Pixel density - is there a limit? (Skyy's question)
**Yes. Hytale UI textures come in exactly one high-density variant: `@2x`, which is 2 texture pixels per UI unit. Nothing denser is
ever used.**

The evidence (all read only):
- Every density-suffixed PNG in Assets.zip is `@2x`: 193 in `Common/UI` and 25 in `Common/Icons`.
- The client's own `Client/Data` has 1406 PNGs: 710 are `@2x`, and none are `@3x` or `@4x`.
- `HytaleClient.exe` contains the file suffix string `@2x.png` and no `@3x.png` or `@4x.png`. The client asks for the plain name
  (for example `ItemTooltipRare.png`) and looks for the `@2x` file itself. 35 client textures also ship a 1x twin.

`Border` is measured in **UI units**, not texture pixels:
- `ItemTooltip.ui` gives `Border: 24`, which is the 48 px corners of the 107 px @2x texture.
- The vanilla button `Primary@2x.png` is 440 x 88 with `HorizontalBorder: 80` and `VerticalBorder: 12`, which is 160 and 24 texture px.

A few vanilla `@2x` files are not exactly double their 1x twin (for example 6 -> 18 px and 10 -> 18 px). They are still drawn at the
size the `.ui` gives them, so the client simply scales a texture to its box. So a denser texture would not break anything for
whole-scaled images (slots, icons, the arrow). It would just be **downscaled**, and the extra detail is thrown away on screen. For
9-slice textures it is **unverified**: the client may cut the corners at 2 x Border px or scale them by texture size, so a denser
tooltip could get wrong corners.

**Practical limit:** design at exactly 2 px per UI unit:
- tooltip 107 x 107 with 48 px corners;
- arrow 66 x 48;
- slot 148 x 148.

That is the most detail the engine is built to show. More detail has to come from cleaner shapes, not more pixels.

## Open questions for Skyy (recommended default in brackets)
1. **Which direction?** [A hybrid of **1 + 3**: the Cloud Frame's soft cloud rolls, with Watercolour Swirl corners (blooms, glowing
   swirls, sparkles). It best matches "flowing clouds ... watercolour magic swirls". Take the glowing gold star point from 2 or 4 as
   the "thing that glows" accent.]
2. **Text panel.** It must stay dark for the fixed text colours. [A deep, mood-tinted twilight panel, 98 % opaque, with a soft rarity
   glow on its edge.]
3. **Rarity order:** sunny to cloudy to stormy to night (Normal clear, Unique golden, Rare pink cloud drift, Legendary blue storm,
   Fabled red tempest, Mythic star night). [Yes.]
4. **Set and Untiered moods.** [Set = green dawn with an aurora; Untiered = ember sunset.]
5. **Mythic galaxy.** It can only appear in the 4 corners plus the moon; the centre stretches, so it must be flat. [Corner galaxy
   holes, the purple moon top right, purple rim-lit clouds.]
6. **Slot centres.** The sky-tinted slot fills are mid-tone, so dark icons read well and white icons slightly less. [Mid-tone fill
   that darkens toward the centre.]
7. **Arrow.** It is 66 x 48 and never stretched, so it can carry a small ornament. [Match the rim: a cloud tip for 1/3, a gold point
   for 2/4.]
8. **In-game check before final art.** [Ship ONE rarity of the chosen direction as a test texture first, to confirm the 9-slice
   Border and the soft-alpha blending for quality textures. Same open risk as `art/tooltip-frames/` question 1.]
