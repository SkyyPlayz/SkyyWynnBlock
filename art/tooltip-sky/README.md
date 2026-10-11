# SkyyGear rarity frames - "SKY WINDOW" (Isles of the Void) - final textures

**Status: final production textures for Skyy's review and an in-game test. Not wired in and not committed yet.**
All pixels are original. No vanilla file was copied, traced or recoloured; vanilla files were only read for sizes and the 9-slice border.

Skyy (2026-10-10), on `art/ui-sky-mockups/sheet.png`: "I like 2 the best. Of the themes". Earlier: "lighter softer look, maybe like
flowing clouds, with softer light glowy almost water color magic looking swirls and shapes ... for the rarities, you keep the clody/ sky
theme so some get more stormy, some get more sunny ... legendary could have blue lighting, mythic its night, and the clouds open up to
show a magical stary/ galactic scene bordered by clouds shining purple from the purple moon." Skyy also loved the menu emblem's glow and
its sparkly water.

- Generator: `python tools/art/make_tooltip_sky.py`. It is pure Python with no Pillow, uses every CPU core, takes about 20 s, and is
  deterministic (two runs give identical bytes).
- Validator: `python tools/art/validate_tooltip_sky.py`. It prints one line per check and ends with ALL OK.
- Review sheet: `sheet.png`, 2060 px wide.
  - At the top: Legendary and Mythic at @2x 1:1 (UI scale 2), with the real SkyyGear 0.2.19 tooltip layout. That layout is the
    Wynncraft-style top part (name, attack speed, label/value rows, green + and red - rolled rows, Class Req, Lv. Min) and the
    SkyBlock-style bottom part (bold gold Ability with its text and Mana Cost, an italic flavour line, "This item can be reforged!",
    and the bold RARITY TYPE line).
  - Then one block per rarity at UI scale 1, using the 1x textures:
    - 3 tooltip sizes (360 / 420 / 480 UI wide), with the arrow at 3 positions;
    - the raw @2x texture at x2 with the 9-slice cuts dashed;
    - the arrow at x2;
    - the slot at @2x and at 1x, with a dark icon;
    - a 9-slot inventory row.
  - The sheet font is a stand-in 5x7 bitmap font. The game's own font is narrower.

## The look (changes from the mockup)
- **Frame:** a crisp, bevelled gold frame in the emblem gold, made of two gold tubes with dark outlines.
  - Between them runs a sky-gradient ribbon with a soft cloud streak (Mythic: a night ribbon with a moon streak).
  - Inside that sits a thin line in the rarity colour, then the dark text panel with a soft rarity glow at its edge.
  - Outside the frame there is a soft halo in the rarity colour (alpha 110 or less).
- **Corners:** each corner has a round gold-ringed window with a bevelled ring, an inner shadow and a glass sheen. Each window holds a
  finished tiny sky scene.
- Every corner also has a **glowing gold star point** aimed out of the box, ending in a sparkle.
- **Studs:** two gold studs sit on the ribbon beside each window.

| Rarity | Mood | Top-left window | Top-right window | Bottom windows (floating isle + sparkly waterfall) |
|---|---|---|---|---|
| Normal #FFFFFF | CLEAR DAY | soft sun + white puffs | drifting clouds, two tiny birds | green isle, leafy tree, white clouds |
| Unique #FFFF55 | GOLDEN SUN | big rayed sun | god rays, gold-rimmed clouds | golden tree, sun rays |
| Rare #FF55FF | PINK CLOUD DRIFT | pink cotton clouds over a pale sun | pink clouds, drifting petals | pink blossom tree |
| Legendary #55FFFF | SLATE STORM | slate thunderhead + **blue lightning** (forked) + rain | second storm cloud + bolt + rain | rain, wind-bent tree, cyan glow |
| Fabled #FF5555 | CRIMSON TEMPEST | crimson thunderhead + **red-gold lightning** | tempest swirl + bolt + rain | red-tinted rock, rain |
| Mythic #CC66CC | STAR NIGHT | the clouds part on a **spiral galaxy** + stars | the **purple moon**; cloud edges lit purple | night isle with a glowing crystal; purple-lit cloud sea, stars |
| Set #55FF55 | GREEN DAWN | dawn sun rising over the cloud sea, aurora | **aurora** curtains (green / teal) | faint aurora above the isle |
| Untiered #FFAA00 | EMBER SUNSET | low orange sun, soft sunset wisps | sunset clouds + **floating embers** | embers, autumn tree, low sun |

- **Arrow:** the gold frame folds down into a V.
  - The arrow's top rows lie over the tooltip's bottom rim. Inside the V the bands are drawn at the same depth as the rim, so the gold
    lines and the ribbon bend into the V without a seam.
  - Outside the V the top rows are transparent, so the arrow never paints over corner art.
  - A gem in the rarity colour sits inside the V, and a sparkle marks the tip.
- **Slots:** a gold bevel frame, a rarity line, a soft inner glow and a gold star stud in each corner.
  - Inside is a soft mid-tone mood sky that gets darker toward the centre, under the icon, with a soft cloud bank at the bottom.
  - A small accent sits top right: a sun, the rayed sun, the low sun, the moon, a bolt, or pink clouds.
  - Mythic uses a lifted violet night with sparse stars.

## Files (paths relative to the asset pack root)
| File | Size | Notes |
|---|---|---|
| `Common/UI/SkyyGear/Tooltips/Tooltip_<R>@2x.png` | 107 x 107 | 9-slice, border 48 px (= `Border: 24` UI), stretch strip 48..58 |
| `Common/UI/SkyyGear/Tooltips/Tooltip_<R>.png` | 54 x 54 | optional 1x twin, border 24 px, strip 24..29 (vanilla ships no 1x tooltip) |
| `Common/UI/SkyyGear/Tooltips/Tooltip_<R>Arrow@2x.png` (+ 1x 33 x 24) | 66 x 48 | never stretched |
| `Common/UI/SkyyGear/Slots/Slot_<R>@2x.png` (+ 1x 74 x 74) | 148 x 148 | scaled whole |

`<R>` is one of Normal, Unique, Rare, Legendary, Fabled, Mythic, Set, Untiered. `manifest.json` has:
- the bytes and sha256 of every file;
- the contrast table;
- for each rarity, the exact quality-asset field values:

```
"ItemTooltipTexture":      "UI/SkyyGear/Tooltips/Tooltip_<R>.png"
"ItemTooltipArrowTexture": "UI/SkyyGear/Tooltips/Tooltip_<R>Arrow.png"
"SlotTexture" = "BlockSlotTexture" = "SpecialSlotTexture" = "UI/SkyyGear/Slots/Slot_<R>.png"
```
These are plain names with no `@2x`; the client finds the `@2x` file itself, the same way vanilla's quality JSON does.

## Text contrast (the opaque panel centre, measured by the generator and checked by the validator)
The table gives the lowest contrast of white, grey 170, green, red, gold, aqua and the rarity colour.

| Normal | Unique | Rare | Legendary | Fabled | Mythic | Set | Untiered |
|---|---|---|---|---|---|---|---|
| 5.37 | 5.39 | 5.47 | 5.43 | 5.72 | 5.83 | 5.16 | 5.52 |

- The lowest value is always red #FF5555, except Fabled, where red and its own rarity colour tie.
- The dim grey 130 measures 4.2-5.0:1. That is fine for a de-emphasised line.
- The panel is fully opaque, so the game world behind it cannot lower the contrast.

## 9-slice safety
- The tooltip is drawn on a 108 px canvas. Inside the stretch strip, every pixel depends only on its depth from the edge. Column 54 and
  row 54 are then dropped.
- All corner art (windows, star points, studs, glows) lives inside the 48 px corner patches and fades out before px 47.
- The validator checks that @2x columns and rows 48..58 are identical, and the same for 1x 24..29.

## For the builder (nothing was edited)
In SkyyGear's quality-asset block (`spec 2.1: the 7 quality assets`, build_skyygear_0.2.20.py ~line 2413):
1. Set the five texture fields to the manifest values above.
2. Ship the PNGs in the jar under `Common/UI/SkyyGear/...`, copied from `art/tooltip-sky/` (do not regenerate them at build time).
3. Change the `az_texture(...)` asserts so they check the jar's own `EXTRA` files instead of `Assets.zip`.

## Open points / unsure (default in brackets)
1. **In-game check first.** We assume the client keeps `Border: 24` when it swaps in a quality's tooltip texture, which is what the .ui
   shows for the default texture. Two more things are unverified: that the soft halo (alpha 110 or less) blends cleanly, and that a 1x
   twin is ever used. [Deploy one rarity, or all 8, and look at a tooltip at UI scale 1 and 2.]
2. **The frame sits further out than vanilla's.** The visible gold frame starts 3 UI in from the texture edge, where vanilla's box
   starts about 11 UI in. So our tooltips look about 8 UI larger per side than the vanilla box. The text padding (24 / 21 UI) is
   unchanged, and the text sits well inside the panel. [Keep. It is the approved mockup layout.]
3. **Arrow placement.** The client sets the arrow's x position. On a narrow tooltip it could land on a bottom corner window; the V then
   covers part of the window. The client might also flip the arrow when the tooltip opens below the slot. [Test with slots at the
   screen edges.]
4. **The Mythic frame stays gold.** The mockup used a lilac ring. The brief asked for one gold frame family, so Mythic is set apart by
   its night ribbon, purple halo and line. [Gold. A lilac Mythic ring is a one-line change.]
5. **Slot readability.** The slot centres are a mid-tone, lifted to a luminance of at least about 0.075. Measured by the validator:
   4.7-6.2:1 against a light icon and 1.9-2.5:1 against a very dark icon. The night and storm skies are lifted toward lighter mood
   tones, so Mythic is a lighter violet than its tooltip. [Keep. Try darker centres if pale icons look washed out in game.]
6. **The windows are tiny.** Each window is about 14 UI across, so at UI scale 1 the scenes read as coloured glints. They read best at
   UI scale 2. [Keep; it is an engine limit.]
