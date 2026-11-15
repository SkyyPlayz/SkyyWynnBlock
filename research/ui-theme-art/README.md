# SkyWynn UI theme "Skyglass" - concept art (plan P0b), draft v1

**Status: concept art for Skyy's review. Nothing is wired in or built yet.** Where this goes: `research/` (INDEX.md "research"). Answers go to
`docs/answered/ui.md`. Plan: `research/Inventory-Screen-Plan.md` (P0b Theme art).

Skyy's words behind it (docs/answered/ui.md):
- 2026-11-12 popups: "Custom look" for "Every SkyWynn menu (Recommended)", meaning one SkyWynn theme replaces the vanilla look, screen by screen.
- 2026-11-14: "try to make the menus simple and easy to understand, look good, but also contain as much as makes sense, so we can keep the
  number of menus down".
- 2026-11-14: "i like this right now tab, when we build the new inventory. lets keep these in the empty space to the right of the inventory.
  and below the hot bar, add buttons for teleports. by default have island and hub there with a way to edit it so you can add more."
  Skyy then answered "Yes, start art".

Runeteria's screen gave the ideas only. Its art, colours and layout details were not copied.

## v2 (2026-11-14, after Skyy's review)
Skyy's review, recorded in docs/answered/ui.md:
- The accent was chosen: Sky Azure, LOCKED. The gold trim and "Stash to Void" stay.
- Mockup notes, word for word: "what is on the right side of the character? and im not seeing the thing to pick what goes in the off
  hand. for crafting, id keep the vanilla look, and add vanilla style tabs for every bench you add. (the normal crafting bench adds to the
  default crafting section. but all the others get their own tab. but keep the search and the toggle to only show craftable. and above
  the inventory it has an inventory button, swap those out, so you have craft, to show the crafting section you show in that picture,
  next to it have the pocket dimensions. make a new image showing what ittl look like when you pick the mining pocket."
- Also: "the skills and righht now things on the side are way to big".

What changed:
- **Character slot column, now labelled.** Every slot has a caption under it: Head / Chest / Hands / Legs on the left;
  **Off-hand**, Utility, Utility, Tool on the right.
  - **Off-hand** is vanilla's utility slot under the character (CharacterPanel.ui `#ItemGridSpecialSlot`, with its key-binding label).
    It is the item held in the off hand: a lantern, a shield, a torch and so on.
  - Clicking it opens **"Pick off-hand"**, a list of the items you own that can go in the off hand, plus Empty. This mirrors vanilla's
    item-slot selector popover. The Craft mockup shows the picker open; the Mining mockup shows a Lantern equipped.
  - **Utility** = the other utility-section items you can swap to with the off-hand key.
  - **Tool** = our tool slot (the Multitool / tool fetch). That one is a proposal; see the open questions.
- **Inventory crafting now uses the VANILLA crafting layout,** drawn in our colours. I read only the layout and sizes from
  `Client/.../Pages/Inventory/BasicCraftingPanel.ui`, `BasicCraftingIngredient.ui` and `Common/Container.ui`; no pixels were copied.
  - Icon-only bench tabs sit on the panel's top edge. Vanilla's are 82 x 62 with a 44 icon; ours are 72 x 52 with a 36 icon.
  - The title reads "CRAFTING > Default", like vanilla's category arrow.
  - Search and the Craftable-only toggle sit in the header.
  - Then the recipe ItemGrid (vanilla has 3 per row; ours has 4, and it scrolls), the ingredient list (item name as the title,
    then rows of slot + name + have / need), and the item preview with Craft, then Craft x10 | Craft All.
  - **First tab = Default** (hand recipes + the Workbench talisman's recipes merged). **One more tab per other equipped bench talisman**
    (Armor, Weapon, Alchemy, Arcane, Farming ...).
- **The row above the inventory is now `[Craft][Mining][Foraging][Farming][Fishing][Combat][Smithing]`.** The Inventory tab is gone.
  - The row sits **between the top panel and the grid**, and its tabs hang from the top panel's bottom edge: the selected tab is part
    of the panel above. This keeps it where Skyy saw the old row and shows that it switches the top panel.
  - **Craft** shows crafting in the top panel.
  - **A pocket** shows that Void bag in the top panel: its space bar + Upgrades link, search + filter chips, the bag grid (6 per row,
    scrolls), the selected item, ONE amount box above the buttons (Skyy 10-10), Withdraw / Deposit / Sell / Unpack, the sell / unpack
    values and Auto-compact.
  - The player's 9 x 4 inventory, the hotbar and the teleport row always stay below.
  - The inventory header now holds "27 / 36", "Stash to Void" and Sort.
- **New image:** `inventory-mockup-mining.png`, with the Mining pocket selected. It holds our own Enchanted ingot / stone icons, because
  no ore icons of ours exist.
- **Compact right column.**
  - Skills is a list: one 29 px row each with a 24 px icon, name, thin XP line and level, plus Total level.
  - Right now has 32 px rows.
  - The column is 400 wide, down from 684.
- **The window is narrower:** 1644 wide and centred, with 76 px grid pitch. The freed width went to the centre column (760).
- **Fix:** the vanilla ItemGrid is a **74 px slot + 2 px spacing = 76 px pitch** (InGame/Common.ui `DefaultItemSlotSize 74`,
  `DefaultItemSlotSpacing 2`). v1 said 74 with no gap. The 9 x 4 grid is 682 px wide.
- v1 is kept as `inventory-mockup-v1.png`. The generator still draws it, byte for byte the same as the committed v1.

## Files
| File | What it is |
|---|---|
| `inventory-mockup.png` | v2. 1920 x 1080. The Inventory tab with Craft selected (the off-hand picker open). |
| `inventory-mockup-mining.png` | v2. The same screen with the Mining pocket selected in the top panel. |
| `inventory-mockup-v1.png` | v1, kept for comparison. |
| `theme-sheet.png` | The kit. Every part is labelled with its size in px. It shows the palette with hex codes, the window frame + 9-slice cut, the title plate, the tab bar, buttons (3 kinds x 4 states), slots, the rarity frames, the controls and the tooltip. |
| `accent-options.png` | The same panel, tab bar, slot row and buttons in 3 accents, so Skyy can pick one. |
| `make_ui_theme.py` | The generator. It is deterministic: two runs give the same bytes (checked). |

## The look
- **Base:** dark navy glass panels, a thin **gold trim** on the window frame and gold fading hairlines under panel titles. The gold
  keeps us in the Sky Window family Skyy approved on 2026-10-10.
- **ONE accent: Sky Azure `#45A8FF`.** It marks the selected tab, the selected slot, the primary button, focus, toggles, links and
  progress.
- **Green = ready / have, red = missing / danger, gold = level / XP.** These follow Style Guide section 15.
- **Shape:** chamfered (cut) corners instead of round ones. They keep crisp pixels at every size and make our own shape. The small
  accent diamond gem repeats on window corners, panel titles, the title plate and slot rarity gems.

### Palette
| Role | Hex | Use |
|---|---|---|
| Accent | `#45A8FF` | selected, primary, focus |
| Accent hi | `#8FCBFF` | links, highlight lines |
| Accent lo | `#2A78C8` | hover lines |
| Primary button face | `#2F86D8` -> `#1C5EA6` | white label (about 5:1) |
| Gold trim / hi / lo | `#C9A04E` / `#F1D58C` / `#6B5122` | frame, ornament lines, level pills |
| Window body | `#101A2C` -> `#0C1422` | page body |
| Panel | `#152138` -> `#111B2D`, border `#22324B` | panels |
| Inset (well) | `#09101C`, border `#18243A` | lists, fields, previews, bars |
| Title text | `#EEF5FF` | titles, tab labels |
| Body text | `#C2D1E2` | body |
| Row name / value | `#D6E4EE` | names, stat names (kit `rowName`) |
| Dim | `#7F93A6` | minor info (kit `rowSub`) |
| Ready / have | `#4FD88A` | ready, have, + values |
| Missing / danger | `#FF6B6B` | need, danger, - values (kit `error`) |
| Level / XP | `#E8C25A` | levels, XP bars (Style Guide 15) |
| Action | `#FFCC00` | "Click: ..." lines (Style Guide 15) |
| Health / Mana / Stamina / Defense | `#E5484D` / `#4D8DFF` / `#F0C53A` / `#9FB0C6` | vitals |
| Rarity (gear, LOCKED) | Normal `#FFFFFF`, Unique `#FFFF55`, Rare `#FF55FF`, Legendary `#55FFFF`, Fabled `#FF5555`, Mythic `#CC66CC`, Set `#55FF55`, Untiered `#FFAA00` | `tools/skyyui.py` RARITY |
| Rarity (pets / eggs / vanilla qualities) | Common `#C9D2DD`, Uncommon `#3E9049`, Rare `#2770B7`, Epic `#8B339E`, Legendary `#BB8A2C`, Mythic `#CC66CC` | `tools/skyyui.py` QUALITY |

### Part sizes (px = UI units at 1080p, UI scale 1; textures ship @2x)
| Part | Size | 9-slice border |
|---|---|---|
| Window frame | any size; chamfer 10, 1 px edge + 2 px gold + 1 px inner line, 26 px corner brackets + 11 px accent gem | 32 |
| Top-edge ornament | gem 15 + two 110 px fading gold wings | none (separate texture) |
| Title plate | height 32, width = text + 64 | H 32 / V 0 |
| Panel / inset panel | any size; chamfer 6 / 5 | 8 |
| Panel title | 16 caps, tracking 1.5, accent gem + fading gold underline (max 330) | (separator texture) |
| Top tab | 117 x 54 at 1080p (12 tabs + coins / bank / mail / close fit 1888), icon 24 | H 12 / V 8 |
| Bag tab (sub-tab row) | 98 x 36, icon 24 | H 12 / V 8 |
| Page chip | height 30, width = text + 24 | 6 |
| Button | 40 high (small 32), chamfer 5; Primary / Secondary / Danger x Normal / Hover / Pressed / Disabled; + a green "Ready" state | 8 |
| Close / icon button | 40 x 40, glyph 16-20 | 8 |
| Item slot | **74 x 74**, spacing 2 = **76 pitch** (vanilla ItemGrid), icon 64, chamfer 4 | none (fixed size) |
| Rarity frame | 2 px frame in the rarity colour (62 % over the panel) + 7 px inner glow + 11 x 11 corner gem top right | none |
| Hotbar marker | the selected-slot frame + 28 x 6 notch under the slot | none |
| Key cap | 22 high (18 inside slots), width = text + 10 | 4 |
| Toggle | 44 x 24, knob 18 | none |
| Search box | height 32, icon 16 | 8 |
| Scrollbar | 8 wide | 3 |
| Progress bar | XP 10 high, vitals 6 high | 2 |
| Level pill | height 22, width = text + 18 | H 8 / V 0 |
| List row | 40-52 high, selected = 3 px accent bar + tint | 6 |
| Tooltip | 372 wide; rarity hairline + top glow + 2 corner gems | 12 |

## The Inventory tab (v1 mockup; v2 changes above)
- **Top row:** the 12 tabs (Inventory selected) with our hub-tab icons, then COINS, BANK, mail (with a badge) and close.
- **Left: Character.**
  - 4 armour slots on the left and Off-hand / Utility / Utility / Tool on the right, with the player preview in the middle.
  - Void Charms row (5 shown, "9 / 18", "All charms >").
  - Pet + Mount cards.
  - Class card: emblem, level pill and class XP bar.
  - Health / Mana / Stamina / Defense, a combat line, and the "Stats by source" button.
- **Centre top: inventory crafting.**
  - Page chips All | Hand | Workbench | Armor | Weapon | Alchemy | Arcane | Farming, the Craftable-only toggle, search and a recipe count.
  - A 5 x 3 recipe grid that scrolls.
  - The detail panel: result, its stats, inputs have / need, a "Ready" line + XP, and Craft / x10 / All.
- **Centre bottom.**
  - Bag tabs: Inventory | Mining | Foraging | Farming | Fishing | Combat | Smithing.
  - The 9 x 4 grid, then the hotbar 1-9 with key caps and the active marker.
  - Under the hotbar, a **TELEPORT row**: Island, Hub, + and Edit.
  - A footer with slots used, "Stash to Void" and Sort.
- **Right.**
  - Skills: 11 skills with icon, name, level and XP bar, plus a Total level card and "Open Skills >".
  - Below it, **Right now** beside the inventory: quest, unspent points, a daily with progress, egg ready, Furnace ready and Bazaar
    filled rows.
- **Bottom:** the key-hint line.
- Item pictures are only our own committed icons:
  - `research/cloud/{enchanted,accessory,fish,fishing}-art`;
  - `art/{pets,pet-eggs,gathering-armor,class-emblems,hotbar-items,hub-tab-icons,warp-icons,tree-node-icons}`.
- The figure in the preview is a blocky stand-in. The rows and numbers are samples.

## How to regenerate
```
python research/ui-theme-art/make_ui_theme.py            # all five PNGs (needs Pillow; ~15 s)
python research/ui-theme-art/make_ui_theme.py theme-sheet.png   # just one
```
- Pillow is not installed on Skyy's system Python. For this round it was installed into a scratch folder (`pip install --target`) and
  deleted afterwards. Re-install it the same way, or with `pip install pillow`.
- Fonts are Windows' Bahnschrift and Segoe UI, used as stand-ins.

## For the build (P1 shell, kit `tools/skyyui.py`)
- **Textures:** the window frame, panel, inset, tab (4 states), bag tab, chip (2 states), the buttons (3 kinds x 4 states + green),
  the slot (empty / hover / selected), 8 + 6 rarity slot overlays (frame + glow + gem), the hotbar notch, key cap, toggle (on / off),
  input box (normal / focus), the scrollbar track + thumb, the progress track + fills, the level pill, the row (3 states), the tooltip
  frame per rarity, the title plate, the ornament and the separator.
  - All of them are drawn @2x and live under `Common/UI/Custom/SkyyKit/` (the only path that works: the 2026-10-15 probe k1b).
  - Glyphs (search, X, +, pencil, chevron, heart, drop, bolt, shield, coin, mail) become small 2x icons.
- **9-slice borders:** see the sizes table. Chamfers live inside the corner patches, and every stretch strip is flat colour or a
  vertical gradient only, so it stretches cleanly.
- **Slot 74 + spacing 2 = 76 pitch** (the engine ItemGrid). The 9 x 4 grid + hotbar = 682 px wide. The slot art is the ItemGrid `SlotBackground`
  (k1h proved it shows on empty slots).
- **Rarity frames:**
  - real items: through the quality textures under `UI/ItemQualities/...` (engine rule from uiprobe05);
  - server-drawn display slots: the hidden per-rarity display item (Style Guide 15 "RARITY ON ICONS").
- Text colours become kit COLOR entries (theme table `THEME["skyglass"]` next to `"sky"`). The accent is ONE constant, so changing the
  accent is one line.
- The page must stay under ~1,600 elements (plan section 7). The mockup has about 36 + 9 + 15 grid slots plus about 120 other parts.

## Open questions for Skyy - v2 (default in [brackets])
1. **Bench tabs icon-only** (vanilla style, with the bench name in the title "CRAFTING > Armor bench" and a tooltip), or icon + name?
   [Icon-only, like vanilla.]
2. **Where the Craft / pocket row sits:** between the top panel and the grid, hanging from the panel (as drawn), or on top of the
   top panel? [Between them, as drawn.]
3. **The Tool slot** under the utility slots is our proposal (Multitool / tool fetch); vanilla has no tool slot in survival. Keep it,
   or show a third Utility slot? [Keep Tool if SkyyGear's Multitool can live there; otherwise Utility.]
4. **The off-hand picker** lists items from the bag only, or from the bag + Void pockets? [Bag + Void.]
5. **Bag tab for Supplies** (plan: "+ Supplies if fitting"): 7 tabs fit at 760 wide; an 8th would need narrower labels. [Leave it out;
   Supplies stays in Storage.]
6. **Pocket grid filter chips** (All / Ingots / Stone per pocket)? [Yes, per pocket kind.]

## Open questions for Skyy - v1 (default in [brackets]; 1 and 8 answered 11-14)
1. **Accent colour?** Sky Azure / Sun Gold / Aurora Teal (`accent-options.png`). [Sky Azure `#45A8FF`: it fits the name SkyWynn and
   reads as "sky". Gold stays as the trim, so gold is not doubled. It stays clear of the Unique yellow and the Untiered orange, and Teal
   would sit next to the Legendary cyan.]
2. **Keep the thin gold trim** (the Sky Window family) or go fully flat? [Keep the trim: it is subtle and ties to the approved tooltips.]
3. **Chamfered corners** instead of rounded ones? [Chamfered.]
4. **Inventory crafting page chips:** show every bench page, or only the benches whose talisman is equipped? [Only the equipped ones +
   All / Hand. The mockup shows 8 for the look.]
5. **The 7 bag tabs as names + icons** (as drawn) or icons only to save room? [Names + icons. Skyy's rule: names visible.]
6. **Skills column as a 3 x 4 card grid** with level pill + XP bar (as drawn)? [Yes.]
7. **Right now panel height:** about 8 rows fit. Should more rows scroll or show "+3 more"? [Scroll.]
8. **Footer buttons under the grid** ("Stash to Void" + Sort), not in the plan text? ["Stash to Void" = deposit everything that has a
   Void bag. Keep both.]

## UNVERIFIED
- The client fonts available to custom UI. The sheet uses stand-in fonts, and the game font is narrower.
- That 12 tabs at 104 px (v2) fit with the game font ("Collections" is the longest label); v2 uses a condensed stand-in.
- That an ItemGrid can be 4 wide (recipes) / 6 wide (pocket) with SlotsPerRow and scroll like vanilla's 3-wide recipe grid (vanilla does this, so likely).
- That the off-hand picker can list items and set the utility slot from a server page (the probe moved items between sections, not a picker).
- A live 3D player preview inside a custom page. Fallback: the class emblem + a static portrait.
- Whether Off-hand / Utility / Tool map onto real inventory sections. The plan says utility -5; the Tool slot may be ours (Multitool).
- The Void Charms row at 76 px pitch (5 per row fits; the full bag stays in Storage).
- That every 9-slice border above holds at the drawn sizes. This needs a probe page with every texture, like the k1 probes.
- The 1,600-element budget with all panels live.
