# SkyyGear rarity tooltip frames + slot frames ("magic scroll", 8 rarities)

**Status: DRAFT v1 for Skyy's review. Not committed, not wired in.** All pixels are original. Nothing here was copied from or traced
over vanilla art.

Skyy (2026-10-10): "can we design cool images with the rarity color bonuses? and can we do custom shaped borders, for cool custom
frame shapes?", then "lets start normal with a cool magic scroll look."

- Generator: `python tools/art/make_tooltip_frames.py`. It is deterministic and uses pure Python, with no Pillow.
- Validator: `python tools/art/validate_tooltip_frames.py`.
- Review sheet: `sheet.png`. The Normal scroll is shown large at the top. Below it each rarity appears at 3 tooltip sizes with the arrow
  at 3 positions, plus its slot at 1x and @2x and a 9-slot inventory mock.

## The look
Every rarity is a **scroll**:
- a parchment rim, rolled up on the LEFT and RIGHT edges;
- a thin ink line in the rarity colour;
- a dark ink-washed text area, `#1b181f`. The lowest contrast there is 5.3:1, so white, grey, green, red, gold, aqua and the rarity
  colour all stay readable.

Runes are drawn on the roll ends. The look gets more magical with rarity:

| Rarity | Colour | Knobs / roll | Sheet corner shape | Extras |
|---|---|---|---|---|
| Normal | #FFFFFF | wooden ball knobs, brown ink line | square | faint brown runes and ink marks |
| Unique | #FFFF55 | brass knobs with a spike | **notched** | small yellow studs |
| Rare | #FF55FF | silver rods, magenta gem finials | **cut (chamfered)** | small gems on the corners |
| Legendary | #55FFFF | gold knobs, cyan gem, little gold curls | rounded | gold filigree rings with cyan gems, inner gold line, glowing runes |
| Fabled | #FF5555 | gold crown finials with red gems | small chamfer | **double frame** (red + gold), gold-framed corner plates |
| Mythic | #CC66CC | obsidian knobs with purple **flames** | chamfered | bright glowing runes, a pale inner line, a purple glow aura instead of a shadow |
| Set | #55FF55 | wooden knobs with **leaves** | rounded | **chain links** on the corners |
| Untiered | #FFAA00 | charred knobs with orange crystal **spikes** (different at each corner) | **jagged / torn**, burnt edge (different at each corner) | ember glow |

Slots use the same idea: a parchment rim, the rarity ink line, a dark centre, and the rarity's corner shape and ornaments (notch, cut
plus gems, gold bracket, corner plates, flames, leaves plus link, spikes).

## Files (paths are relative to the asset pack root)
| File | Size | Notes |
|---|---|---|
| `Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>@2x.png` | 107 x 107 | same size as vanilla `ItemTooltip*@2x.png`; 9-slice border 48 px |
| `Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>.png` | 54 x 54 | 1x, border 24 px. Vanilla ships no 1x file, so this one is optional |
| `Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>Arrow@2x.png` (+ 1x 33 x 24) | 66 x 48 | same size as the vanilla arrow |
| `Common/UI/SkyyGear/Slots/Slot_<Rarity>@2x.png` (+ 1x 74 x 74) | 148 x 148 | same size as vanilla `Slot*@2x.png` |

`<Rarity>` is one of Normal, Unique, Rare, Legendary, Fabled, Mythic, Set, Untiered. `manifest.json` lists the bytes and sha256 of
every file.

## Step-1 facts (vanilla, read only)
- **Files.** Assets.zip has ONLY `@2x` files:
  - `Common/UI/ItemQualities/Tooltips/ItemTooltip<Q>@2x.png`, 107 x 107;
  - `...ItemTooltip<Q>Arrow@2x.png`, 66 x 48;
  - `Common/UI/ItemQualities/Slots/Slot<Q>@2x.png`, 148 x 148.

  The quality JSON names them without `@2x` (for example `"UI/ItemQualities/Tooltips/ItemTooltipRare.png"`), so the client looks up
  the `@2x` file itself.
- **The tooltip is a 9-slice.** The client file `Client/Data/Game/Interface/InGame/Tooltips/ItemTooltip.ui` sets:
  - `@TextureBorder = 24`;
  - `Background: (TexturePath: "ItemTooltipDefault.png", Border: @TextureBorder)`;
  - MinWidth 320, MaxWidth 480 UI units;
  - text `Padding: (Full: 24, Top: 21)`.

  So the border is 24 UI units, which is 48 px in the @2x texture. Each corner patch is 48 x 48 and never stretches. The edges stretch
  along one axis. The 11 px centre (48..58) stretches both ways. The vanilla art agrees: its rounded corner plus frame runs ~31 px in
  from the edge, which only works with a 48 px border.
- **What the vanilla tooltip texture looks like.**
  - A soft drop shadow ~21 px wide with partial alpha, at most 26.
  - The box sits at x 22..84 and y 21..84, with rounded corners.
  - From the edge in: a dark rim 6 px wide (`#161a24`), then a trim line 4 px wide in the quality colour (lighter on top), then a flat
    dark centre `#161a24`.
  - Alpha is partial only in the shadow and on the anti-aliased corners. Transparent areas are fine, so **shaped borders work**, as
    long as the shape sits inside the corner patches.
- **The arrow.** It is defined as `Group #Arrow { Anchor: (Width: 33, Height: 24, Bottom: -8) }` and is never stretched.
  - Row r of the arrow lands on tooltip row 75 + r. Its top 10 rows lie over the box's bottom rim, and the point hangs below the box.
  - The client code sets the arrow's x position; that position is not in the .ui file.
- **Slots.**
  - `InGame/Common.ui` sets `@DefaultItemSlotSize = 74`, `SlotIconSize: 64`, and `RenderItemQualityBackground: true` on the hotbar and
    inventory grids.
  - The quality slot texture is drawn at whatever slot size the grid uses: 74 normally, and smaller in some grids (fuel 64, legend 46).
  - No Border is given for it, so it is scaled as a whole. Shapes do not distort because slots are square.
  - The vanilla slot is a plain 4 px dark rim, a 4 px quality trim and a diagonal gradient fill. Only its outermost corner pixel is
    transparent.

## How these were built to stretch safely
- The tooltip is drawn on a 108 px canvas with exactly the vanilla box placement (22 / 21 / 86 / 86). Inside the strip 48..59 the
  drawing ignores the position along the strip, so every strip pixel depends only on its depth from the edge. Column 54 and row 54 are
  then dropped, which gives 107 px with an 11 px strip.
- The validator checks that columns 48..58 and rows 48..58 are identical (1x: 24..29).
- The rolls are vertical cylinders, which look the same at any height, so they can stretch. Knobs, runes, gems, filigree, plates,
  flames, leaves, links, spikes and torn corners all sit inside the corner patches.
- Hard alpha (255) on every frame and ornament pixel. Soft alpha (at most 110) only in the drop shadow, or in the coloured glow for
  Mythic, Untiered, Fabled and Legendary.
- The arrow continues the parchment rim. Its top 10 rows repeat the rim's bottom bands (same depths), so the rim seems to fold down
  into a V. Ornaments sit at the tip: a gem, a flame, a leaf, or jagged edges for Untiered.

## How SkyyGear should point at them (for the builder; nothing was edited)
In the RARITIES / quality-asset block of the SkyyGear build script (`spec 2.1: the 7 quality assets`, near line 2354 in 0.2.18):
1. Set the texture fields per rarity:
   - `ItemTooltipTexture = "UI/SkyyGear/Tooltips/Tooltip_<Name>.png"`
   - `ItemTooltipArrowTexture = "UI/SkyyGear/Tooltips/Tooltip_<Name>Arrow.png"`
   - `SlotTexture` = `BlockSlotTexture` = `SpecialSlotTexture` = `"UI/SkyyGear/Slots/Slot_<Name>.png"`
2. Ship the `@2x` PNGs, and the optional 1x ones, in the jar under `Common/UI/SkyyGear/...`.
3. The script's `az_texture(...)` asserts check that the texture exists in Assets.zip. They must instead check the jar's own `EXTRA`
   files.
4. The PNGs are original and SkyWynn-owned, so they can be committed. Copy them into the jar from `art/tooltip-frames/`; do not
   regenerate them at build time.

## Risks / open questions for Skyy (default in brackets)
1. **In-game check needed.** We assume the client keeps `Border: 24` when it swaps in a quality's tooltip texture, as the .ui shows
   for the default. If it drew the quality texture without the 9-slice, the corners would scale. [Check one rarity in game first.]
2. **Arrow position and direction.** The client places the arrow's x. Near the far left or right of a narrow tooltip, the V could
   sit on top of a roll or a corner ornament. The client might also flip the arrow when the tooltip opens below the slot.
   [Test with a slot at the screen edges.]
3. **Rune "along the edges".** Runes cannot repeat along the edges, because a 9-slice edge is stretched and the runes would smear.
   They sit on the roll ends and sheet corners instead. [Keep.]
4. **Ornament size.** The corner patch is only 24 UI units, so knobs and gems are small (about 5-12 UI px). They read clearly at UI
   scale 2 and are tiny at UI scale 1. [Keep; bigger would need a bigger Border, which only the client controls.]
5. **Slot centres are darker than vanilla** (ink-wash, so icons pop). Some dark item icons may read less well. [Keep.]
6. **Rolls are on the left and right, not the top and bottom.** Top / bottom rolls would collide with the arrow, which overlays the
   bottom rim. [Left and right.]
