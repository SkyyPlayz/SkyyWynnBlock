# SkyWynn Menu - tile icons (64 x 64 each)

**Status: DRAFT v1 for Skyy's review. Not committed, not wired in.**

Skyy (2026-10-10): "lets make an Icon for everything in this menu." One original item icon per tile of the SkyWynn Menu main view
(SkyyMenu 0.3.15 `ENTRIES`, view `main`). Drawn in the same style and with the same tooling as the approved menu emblem
(`art/menu-emblem/`, Skyy: "perfect! use it").

## Family look
- 64 x 64 RGBA (vanilla item icon size), hard alpha (0 or 255), a 1 px violet-black outline `#120e1c`. The outline is tinted a
  little toward the part it touches: brown-black next to gold, as on the emblem and the bag.
- Light from the top left on every icon: a lit bevel and rim on top / left edges, a darker bevel and rim on bottom / right edges,
  a contact shadow under parts that sit in front of others, and 1 px inner lines round the front parts.
- Every pixel is snapped to a 6-7 step ramp for its material. Shadows lean violet / blue and lights lean warm. There is no
  `#000000` and no `#ffffff`.
- Each category has its own tint:

  | Category | Tint | Tiles |
  |---|---|---|
  | Travel | gold / amber | Teleport, Island Menu |
  | Your stuff | teal | Your Profile, Pets, Pocket Dimension, Accessory Bag, HUD Editor, Crafting, Skills, Collections |
  | Money | green / gold | Bank, Vault, Bazaar, Auction House, Reforge, Identify |
  | Social | violet | Players, Party, Guild |
  | Admin | gray / steel | Hover Tooltips, Settings, Mods, Server Setup |

## Icons (`Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png`, main-view slot in brackets)
| Name | Slot | Shows |
|---|---|---|
| YourProfile | 4 | a blocky player bust in a gold-rimmed teal portrait medallion |
| Pets | 5 | **fallback only** (the tile keeps showing the pet's own art): a teal collar with gold studs and buckle, and a gold tag with a paw print |
| HoverTooltips | 8 | a pale steel speech bubble with a navy "i" and a hover pointer |
| Teleport | 10 | a gold portal ring with amber gem studs round swirling amber energy, on a stone plinth |
| PocketDimension | 11 | a teal drawstring pouch with a violet-teal swirl rising out of its void opening |
| AccessoryBag | 12 | **reused**: a byte copy of the approved `art/accessory-bag-icon` icon (already shipped as `Skyy_Menu_Icon_AccessoryBag`) |
| HudEditor | 13 | a teal screen with HUD widgets (health / mana bars, minimap, hotbar), a dashed gold edit box and a pointer |
| Crafting | 14 | a wooden workbench with a teal 3 x 3 crafting mat and a little hammer |
| Skills | 15 | a gold star badge: teal medallion, gold rim, two ribbon tails |
| Collections | 16 | **extra** (it is in the menu but was not on the list of 22): an open teal album with 8 framed slots, each holding a different find |
| IslandMenu | 20 | a round floating island with a cottage (amber roof, lit window), a bush, an amber flag and clouds. On purpose it looks unlike the emblem: no star, no waterfall, a rounded shape |
| Bank | 21 | a stone bank front (green roof, gold coin in the pediment, 4 columns) with a stack of gold coins |
| Vault | 22 | a big green-steel safe with a gold wheel dial, hinges, bolts and a green lock lamp |
| Bazaar | 23 | a market stall (green / cream striped awning, green cloth counter) with gold scales weighing coins against an emerald |
| AuctionHouse | 24 | a mahogany gavel with gold bands over a sound block with a green felt top |
| Reforge | 25 | a steel anvil with a glowing amber blade blank and a gold spark burst |
| Identify | 26 | a gold magnifying glass over a cut emerald; the gem shows magnified in the lens |
| Players | 30 | a violet player-list board with 3 rows of head + name; your row is highlighted with a gold dot |
| Party | 31 | 3 violet player busts; the front one is bigger and wears a gold star |
| Guild | 32 | a violet swallowtail banner with gold trim and a gold shield crest, on a gold crossbar |
| Settings | 39 | two steel cogs, one big and one small |
| Mods | 40 | a thick steel puzzle piece with rivets and a teal gem |
| ServerSetup | 41 | a steel cog wearing a gold crown (ruby + 2 amethysts) |

The other files:
- `sheet.png` (1500 x 2190): every icon at 64 px on checker and on menu navy plus 2x, labelled and grouped by category; all icons at
  32 px; all icons on a light background; a mock of the 9 x 6 SkyWynn Menu (navy `#0b1524` panel, gold accent bar, Close button)
  with every icon in its real slot.
- `manifest.json`: tiles (item id, slot, category, file), bytes + sha256 of every file, and the palettes.

## Tools
- `python tools/art/make_menu_icons.py` writes everything above. It is pure Python 3 (no Pillow / numpy) and reuses
  `tools/art/emblem_png.py`. It is deterministic: two runs give the same bytes (checked).
- `python tools/art/validate_menu_icons.py` checks size, hard alpha, no black / white, the outline, fill and margin, that every icon
  is unique, that the bag is a byte copy, the manifest hashes, determinism, and that no path clashes with vanilla Assets.zip
  (read only). Result: ALL OK.

No vanilla file was copied, traced or recoloured. Three vanilla icons were only looked at (read from Assets.zip into scratch, since
deleted) to check icon size and density.

## How SkyyMenu could wire them (for the next SkyyMenu patch; this art round did NOT touch any build script)
Add one entry per icon to `ICON_ITEMS` (same pattern as `Skyy_Menu_Icon_AccessoryBag`):
`"Skyy_Menu_Icon_<Name>": ("art/menu-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png",
"Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png", "art/menu-icons/manifest.json", "<Tile>", "<vanilla held look>")`, then point
each `ENTRIES` row at its id. For Pets, `ICON_PETS = "Skyy_Menu_Icon_Pets"` (pet art still wins). The bag needs no change.

## Open questions for Skyy (each with today's default)
1. Players: a player-list board, or something else (globe / signpost)? [list board]
2. Collections was not on the list. Use the album icon too? [yes]
3. Hover Tooltips: admin gray, or teal like the other personal options? [gray, since it sits with Settings]
4. Reforge and Identify count as "money" (green / gold) here. OK? [yes]
