# SkyWynn hub tab icons - a faded picture behind each tab's word (72 x 72 @2x)

**Status: DRAFT v1 for Skyy's review. Not committed, not wired in.**

Skyy (2026-10-15): "can you give the tabs in the character page custom designs? so the pet tab still says pets, but also shows a
little pet icon behind the word?" Style picked in a popup: "Icon first, themed later".

Every hub tab (Hubs-Spec 1.2, 33 tabs) gets a faded icon that sits BEHIND its word, and every hub (plus Home) gets one for the new
hub row. Each has a normal file and a brighter `_on` file for the active (selected) tab. `contact-sheet.png` shows them all on the
real Sky tab textures.

## Size and placement
- **72 x 72 px, an @2x texture = 36 x 36 UI units.** The Sky tab (`art/ui-kit-sky`, `Tab*@2x.png`) is 44 UI high, so the icon leaves
  4 UI clear above and below. It works on every tab width from 110 to 190 UI (Character and the hub row: 8 tabs = 115 UI).
- One motif per icon, centred (checked: the bounding box centre is within 1 px of the middle). Put it centred in the tab, UNDER the
  label: e.g. a 36 x 36 Group (Anchor centred) with `Background: "SkyyKit/HubTab/<hub>_<tab>.png"` behind the tab's text.
  Use `<hub>_<tab>_on.png` while that tab is the active one (`Tab_Selected`).
- Texture root (Hubs-Spec 7.1): ship the files in the jar as `Common/UI/Custom/SkyyKit/HubTab/<hub>_<tab>@2x.png` and write the
  markup path without `@2x`. The files here have no `@2x` in their names because the task named them `<hub>_<tab>.png`; the jar copy
  step adds it.

## How it is faded (so the word stays readable)
Each motif is painted first as a normal family icon (same painter as `art/menu-icons` / `art/menu-icons-2`: palette ramps, light
from the top left, bevels, contact shadows, a 1 px tinted dark outline). Then:
1. colours are pulled toward a cool slate grey (normal 30 %, `_on` 10 %);
2. one overall alpha (normal 0.62, `_on` 0.86) - every file is partly transparent (no pixel at 255);
3. bright parts are compressed smoothly toward a brightness cap (soft knee), then any pixel still too bright is darkened / made more
   transparent until the label passes.

Contrast target (WCAG ratio of the kit label over the icon on the tab, checked on EVERY icon pixel against the brightest pixel of
the tab texture's text band): normal files >= 5.0 on `Tab`, >= 4.5 on `Tab_Hovered`, >= 5.0 on `Tab_Pressed` (label `#bdcbd3`);
`_on` files >= 4.5 on `Tab_Selected` (labels `#bfcdd5` and `#bdcbd3`). All 82 pass (worst 1.06 x target normal, 1.03 x on).
Light motifs (the cream bunny, the recipe scroll) therefore come out as muted grey shapes; dark / saturated ones keep more colour.

## Icons (`<hub>_<tab>.png` + `<hub>_<tab>_on.png`)
| Hub | Tab | Shows |
|---|---|---|
| character | stats | a red heart with three rising gold bars inside it |
| character | skills | a gold star medal (teal centre, gold star) on two teal ribbons |
| character | trees | a branching tree: a trunk splitting into three round green crowns, each with a gold node (a skill tree) |
| character | class | a crossed wooden staff (violet orb in a gold claw) and steel sword (gold guard) |
| character | pets | a sitting cream bunny facing left (long ears with pink insides, round tail) |
| character | accessories | a gold chain amulet with a teal diamond gem in a round gold setting |
| character | collections | an open teal book with text lines and a gold bookmark ribbon |
| character | profiles | a gold picture frame holding a teal player portrait |
| storage | pocket | a leather drawstring sack with a gold cord and a violet pocket-dimension swirl |
| storage | requip | a steel chestplate with teal pauldrons on a gold clothes hanger |
| storage | vault | a round steel vault door (bolt ring, side hinge) with a gold spoked wheel |
| storage | bank | a stone bank: four columns, green roof, gold coin in the pediment, steps |
| market | bazaar | a market stall: green / cream striped awning, wooden counter, fruit and a crate |
| market | auctions | an auction gavel (mahogany head, gold bands) over its sound block |
| market | merchants | gold balance scales with a coin and an emerald on the pans |
| smithing | gear | a steel knight helmet with a T visor, rivets and an amber plume |
| smithing | recipes | a recipe scroll with a 3 x 3 crafting grid (ingot, two sticks, emerald) |
| smithing | reforge | a steel anvil with a glowing amber blade blank and three sparks |
| smithing | upgrade | a big gold up-arrow with an amber star in its shaft |
| smithing | multitool | a pick-axe multitool: pick spike one side, axe blade the other, gold collar |
| smithing | identify | a gold magnifying glass showing an emerald through its lens |
| world | teleport | an upright gold portal ring with a violet swirl and four amber studs |
| world | island | a floating island with one round tree and a small waterfall |
| world | explore | a gold compass with a cream face and a red / steel needle |
| world | quests | a wooden job board (mahogany roof) with a pinned paper showing an amber "!" |
| social | players | a blocky player head in 3/4 view (brown hair) on violet shoulders |
| social | party | three violet player busts over a gold star |
| social | guild | a violet guild banner with a gold edge, shield and star on a gold rod |
| settings | settings | three slider tracks with teal fill and steel knobs |
| settings | hud | a steel screen frame with HUD parts: hearts, a mana bar, a crosshair, a hotbar |
| settings | layout | a 2 x 2 grid of steel tiles; the fourth is gold and lifted out of its spot |
| settings | mods | a steel puzzle piece with a teal face |
| settings | setup | a steel wrench in front of a steel cog (Server Setup) |

Hub row (`hubrow_<hub>.png` + `_on`): **home** a little house (mahogany roof, lit windows, chimney); **character** a front-view
blocky player head on teal shoulders with a gold-and-emerald collar gem; **storage** a wooden chest with gold bands and lock;
**market** a coin stack beside a big gold coin with an emerald; **smithing** two crossed smithing hammers; **world** a blue globe with
green islands and a gold ring; **social** two violet busts; **settings** a steel cog with a gold centre ring.

Colour families follow the menu-icon categories: Character teal + gold, Storage teal / leather / steel, Market green + gold,
Smithing steel + amber, World amber / gold, Social violet, Settings steel.

## Files
- 82 PNGs (41 icons x normal / `_on`), 72 x 72 RGBA, about 70 KB in all.
- `manifest.json`: per icon hub, tab, label, what it shows, both file names and the worst contrast (as a multiple of its target);
  the file list with bytes + sha256; the size, fade and contrast rules; the worst tab background colours used.
- `contact-sheet.png` (review only, not shipped): every icon behind its word on the Sky `Tab` (normal) and `Tab_Selected` (`_on`) at
  @2x, each icon alone on checker (normal / on / unfaded source), and each bar at 1x with one tab active. The words use the sheet's
  5 x 7 bitmap font, not the game font (the game font is narrower; long words at 1x are shrunk on the sheet only).

## Tools
- `python tools/art/make_hub_tab_icons.py [--sheet <png>]` writes the PNGs + manifest (and the sheet). Pure Python 3, imports
  `tools/art/make_menu_icons.py` (not edited) and `tools/art/emblem_png.py`; reads only our own `art/ui-kit-sky` Tab textures.
  Deterministic (two runs = same bytes, sheet included).
- `python tools/art/make_hub_tab_icons.py --check`: 33 + 8 icons, manifest = files (bytes + sha256), no stray PNGs, no vanilla path in
  the generator, 72 x 72 RGBA, partly transparent, contrast on every pixel, motif size / 1 px margin / centred, unique, deterministic,
  `_on` brighter than normal. Result: ALL OK.

No vanilla file was read, copied, traced or recoloured.

## Open points for Skyy (default in brackets)
1. Strength: the fade is set by the readability rule (label >= 5 : 1 on the plain tab). Stronger icons would need a darker label
   area or a lower rule. [keep the rule - the word always wins]
2. Normal vs active: the active tab shows a brighter, more colourful icon. Or show the icon ONLY on the active tab? [both, brighter
   on active]
3. Hub row Character is a player head; the Social > Players tab is a player head too (3/4 view, violet). [keep, they sit in
   different rows]
4. "Themed later": these are one look for all hubs; a later batch can recolour per hub mood.
