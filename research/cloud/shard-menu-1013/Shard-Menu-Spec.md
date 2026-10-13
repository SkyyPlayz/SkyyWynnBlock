# Shard menu (Sky Window kit) - layout spec

Cloud draft, 2026-10-13. Paper design only; nothing is built. The pictures and the generator are in `research/cloud/shard-menu-1013/`.
It is one page with four tabs. It opens from the shard portal on your main island (right-click, like a vanilla portal's menu) and
from the menu stand on the shard's hub island.

| File | What it shows |
|---|---|
| `research/cloud/shard-menu-1013/shard_0_layout.png` | **Layout first:** the page shell with every region and its pixel box, plus each tab's grid at 1:4 |
| `research/cloud/shard-menu-1013/shard_a_collect_1080p.png` | Collect tab, in game at 1920 x 1080 |
| `research/cloud/shard-menu-1013/shard_b_upgrades_1080p.png` | Upgrades tab: Storage (affordable, hovered), Auto-Compactor (missing items), Time Compressor (requirement not met) |
| `research/cloud/shard-menu-1013/shard_c_islands_1080p.png` | Islands tab: the 8-slot ring map, with slot 3 selected |
| `research/cloud/shard-menu-1013/shard_d_totems_1080p.png` | Totems tab: the placed totems, the free places and the selected totem |
| `research/cloud/shard-menu-1013/shard_e_states.png` | States: tabs, the summary strip (portal / hub / storage full), buy buttons, the maxed card, slot states, the side-panel variants, status chips |
| `research/cloud/shard-menu-1013/shard_e2_empty_states.png` | Empty Collect (nothing stored) and empty Totems (none placed), both at 1:1 |
| `research/cloud/shard-menu-1013/shard_f_check_1366x768.png` | The 1366 x 768 fit check (A scaled, B unscaled) |
| `research/cloud/shard-menu-1013/make_shard_menu.py` | Pillow generator. It is deterministic (checked: two runs give the same bytes, about 4 s) and it checks the layout itself (below) |

How it is drawn:
- **Kit textures:** the real Sky Window kit from `art/ui-kit-sky/Common/UI/Custom/SkyyKit/`, 9-sliced the way the client does it
  (@2x texture, Border in UI units, 1 UI = 1 px at 1080p).
- **Shared code:** the kit helpers, colours, fonts and placeholder world are imported from
  `research/cloud/ui-mockups-1013/make_mockups.py`, so this set matches the approved HUD / Settings mockups.
- **Fonts:** Liberation Sans stands in for the game's Nunito Sans and Lexend.
- **Shard icon:** `research/cloud/icons-1013/icons/Skyy_Shard_Portal_Farming.png`.
- **Placeholder pictures:** every other picture (crops, totems, the upgrade symbols, the island map) is a simple placeholder drawn by
  the script. None of it is item art or vanilla art.
- **Layout self-check:** every run checks that each box sits inside its parent, that no box overlaps a sibling, that no two text
  boxes overlap, and that every label fits its width. The last run printed `layout: OK`. I also looked at every PNG and at 1:1 crops.

## Decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/skills.md` line 108 (SHARD ISLANDS) | A shard is a portal to a private mini island. The Farming shard starts with 1 small Wheat island and 1 T1 Harvest Spirit. All plants are eternal. Upgrades cost Eternal Seeds. Islands have 3 sizes. You buy new islands for new crops. Shards are the ONLY automation. |
| `docs/answered/skills.md` lines 110-111 (SHARDS 2 + LAYOUT popup) | XP and collections come **when you collect**. The shard menu has 3 parts: **Collect**, **shard upgrades** (auto-compactor, time compressor) and **Islands** (add / upgrade). Protected: no building. Islands sit in **fixed slots around a hub**, any island in any slot, with 1 pre-made bridge per slot that appears when the slot is filled, and each island grows in place. **The same menu opens from the portal on your island** ("needs a really cool design"). |
| `docs/answered/skills.md` lines 112-113 (SHARDS 3) | 6 shards. One shared totem system with themed workers (Farming = Sprites). Totems work like SkyBlock minions: info, upgrade, modifiers, **pick up to move**. Shards can be picked up and moved. **Each shard has a max storage, upgraded in the shard.** |
| `docs/answered/skills.md` line 105 (FARMING TOTEMS popups) | No fuel needed, with an **optional booster fuel slot**. Tier up (Totem -> Pole -> bigger Pole) on the **Anvil Upgrade tab** with Enchanted materials. **2 minion-style upgrade slots**. |
| `research/Shard-Islands-Ideas.md` | The summary of the above, plus the totem list (Harvest Spirit = the starting totem) |
| `research/Gathering-Progression-Spec.md` section 2.3 | The 7 crop pairs (Wheat / Lettuce ... Potato / Onion) and the 14 `Plant_Seeds_<Crop>_Eternal` ids used in the costs |
| `.claude/skills/skywynn-art/SKILL.md` section 2 | Enchanted = 100 of the vanilla item (the compactor ratio) |
| `docs/answered/ui.md` lines 80, 82, 83 (LOCKED 2026-10-10) | Pages use the SKY WINDOW kit (gold frame, corner sky windows, dark readable panels). Each hub has its own frame mood; World = clear sky. |
| `docs/answered/ui.md` line 93 (2026-10-13 VISUALS GO-AHEAD) | The local session reviews this before building. Extra care on layout. |
| `HANDOFF.md` section 2 + `research/Vanilla-UI-Style-Guide.md` | Inline documents only. No underscores in ids. Page root = Width / Height only (centred). Never send a page update from a hover handler. No metadata ItemStacks in an `ItemGridSlot`. |
| `research/Settings-Spec.md` line 28 | Verified page sizes: 1120 wide and 952 high. This page is 1100 x 860. |

## 1. What opens it, and the two views

| Opened from | Strip button | Footer | Extra |
|---|---|---|---|
| **Portal view** (right-click the placed shard portal on your main island) | **Enter Shard** (Primary 180 x 44) | **Pick up Shard** (Secondary 170 x 36, with a confirm) + Close | "Go to totem" is disabled ("inside the shard only") |
| **Hub view** (right-click the menu stand on the shard's hub island) | **Back to Island** (Secondary 180 x 44) | Close only | "Go to totem" is enabled |

Both views share the same tabs and the same contents. Only the strip button, the subtitle line, Pick up Shard and Go to totem change
(see `research/cloud/shard-menu-1013/shard_e_states.png`, part 2).

## 2. The shell (the same on every tab) - page coordinates, 1100 x 860

| Region | Box (x, y, w, h) | Kit / style |
|---|---|---|
| Page | 0, 0, 1100, 860, centred (at 410, 110 on a 1080p screen) | `Frame_World` (Border 32; the World hub mood = clear sky). Content padding 24. |
| Header | 24, 18, 1052, 38 | `Header` (H 60, V 0). `HeaderOrnament` 236 x 22 at Top -12. Title = the shard name ("Farming Shard"), Bold 18 `#b4c8c9`. `Close` 32 x 32 at 1040, 21. |
| Summary strip | 24, 66, 1052, 76 | `Panel` (Border 12) |
| - shard icon | 36, 72, 64, 64 | the Shard Portal icon of this shard (64 px, 1:1) |
| - summary | text at x 114. Line 1 centred on y 92; line 2 centred on y 116 | Line 1: "3 islands · 4 totems · Time x1.25 · 412 items / hour", Bold 15 `#d6e4ee`, max 470 wide. Line 2 (13, `#878e9c`) says where you are. |
| - storage mini bar | x 590..840; label at y 90; bar 250 x 10 at y 104; line at y 126 | "Storage 3,140 / 5,000"; a green fill; "Full in 4 h 31 m". When full it turns red: "Storage FULL", "Production stopped - collect now". With no totems the line reads "No totems - nothing is harvested" (`#ffcc00`). |
| - main button | 880, 82, 180 x 44 | Enter Shard (Primary) or Back to Island (Secondary), Bold 16 |
| Tabs | y 152, each 260 x 44, gap 4, starting at x 24 / 288 / 552 / 816 | `Tab` / `Tab_Hovered` / `Tab_Selected` (H 20, V 12), Bold 15. The order is Collect, Upgrades, Islands, Totems. |
| Content area | 24, 206, 1052, 564 | Two layouts: **left 700 + right 340** (`Panel` at 24,206 and 736,206, gap 12), or **3 cards of 340** (gap 16) on Upgrades |
| Status line | centred on y 785, x 40 | Bold 15. Green `#39f493` after an action, `#b7cedd` for info. |
| Gold line | 24, 800, 1052, 1 | `#E8A93B(0.35)` |
| Footer | y 808, 36 high | Pick up Shard 44,808 170 x 36 (portal view only); Close 906,808 150 x 36 |

Panel title: Bold 16 `#afc2c3` at panel x+16, centred on y+22. Caption: 13 `#878e9c` centred on y+43. A right-aligned summary (13 Bold)
can sit at the panel's right edge -16, on the title line.

## 3. Tab: Collect (`research/cloud/shard-menu-1013/shard_a_collect_1080p.png`)

| Part | Box / rule |
|---|---|
| Left panel | "Stored in this shard" + caption; "6 kinds" on the right |
| Rows | `Row` 676 x 56, gap 4, from y 268 (x 36). Up to **6 rows** fit (ending at y 624). Past 6, the list scrolls (`ScrollTrack` 6 wide, inside the row's right edge). Each row has: a 44 px `SlotEmpty` with the item icon at x+8; the name in Bold 15 (Enchanted items in gold); a sub line in 12 `#7f93a6` (the island it came from + "0.4 XP each"); the amount in Bold 17 white, right-aligned 16 px left of the button; a **Collect** button (`Tertiary` 96 x 30) at the row's right edge -12. |
| Storage block | a gold line at y 640; "Storage" + "3,140 / 5,000 (63 %)" on y 660; a stacked bar 668 x 16 at y 674 (one colour per item); a legend at y 705 (10 px swatches, 12 px names); "Full in 4 h 31 m at 412 items / hour. A full shard stops producing." at y 728; "Raise the limit in Upgrades -> Storage. Each Enchanted item counts as 1." at y 747 |
| Right panel | "Collect all" + caption. A `PanelInset` 308 x 222 holds: the item total; **+Farming XP** in green; the collections each item feeds (rank + "+gain"), each with a bar whose new part shows brighter green. |
| Where the items go | "Sacks first, then your inventory." + a tick and "Everything fits." in green. When not everything fits: "Inventory full: 420 Carrot stay here." in `#ffcc00` (the rest stays in the shard). |
| Rule line | "Farming XP and collection progress are only given when you collect." (Skyy's rule) |
| Collect all | `Primary` 308 x 48 at 752, 706. Above it: "Last collected 7 h 37 m ago". |
| Empty | The rows area becomes a `PanelInset` with "Nothing to collect yet / Your islands are growing. Come back soon." Collect all uses `Primary_Disabled`. (`research/cloud/shard-menu-1013/shard_e2_empty_states.png`) |

The sample numbers were worked out with python3 by the generator:
- Items: 1,720 + 18 + 636 + 4 + 410 + 352 = 3,140 stored.
- Farming XP: the sum of count x XP each = 2,178.
- Wheat collection: +1,720 + 18 x 100 = +3,520. Enchanted items count 100 each.
- Time to full: (5,000 - 3,140) / 412 per hour = 4.51 h, shown as 4 h 31 m.
- Rate: 330 per hour x 1.25 = 412 per hour (floor). The next level is 330 x 1.50 = 495.

## 4. Tab: Upgrades (`research/cloud/shard-menu-1013/shard_b_upgrades_1080p.png`)

Three `CardFrame` cards (Border 32), each 340 x 564, at x 24 / 380 / 736. Inside a card (y is measured from the card top; content
inset 24):

| y | Part |
|---|---|
| 26 | 64 px icon, centred |
| 110 | name, Bold 18 |
| 134 | "Level 3 / 8", Bold 14 `#b7cedd` (gold when maxed) |
| 148 | level pips: 22 x 8 each, gap 4. Gold = owned; a green outline = the next level. |
| 164 | (Auto-Compactor only) **On / Off** switch: 2 x `Tertiary` 64 x 24. It saves on click. |
| 198 | `PanelInset` 292 x 66: "Now" with its value in white, and "Next" with its value in green ("Fully upgraded" in gold when maxed) |
| 282 | 2-line description, 13 `#96a9be` |
| 328 | "Cost" + "have / need". Then 3 cost rows, 28 high: a 22 px icon, the name (13), and "have / need" (Bold 13) in **green when you have enough, red when you don't**. |
| 432 | Requirement: a tick + "Needs Farming 10 (you: 12)" in green, or an "x" + the same line in red |
| 496 | Buy button, 292 x 44 |

**Buy button states** (`research/cloud/shard-menu-1013/shard_e_states.png`, part 3):

| State | Look |
|---|---|
| Affordable | `Primary` "Upgrade to Level 4" (Hovered shown) |
| Items missing | `Primary_Disabled` "Missing 2 items" (the count of red cost rows) |
| Requirement not met | `Primary_Disabled` "Needs Farming 20" |
| Maxed | `Tertiary_Active` "MAX LEVEL" in gold; the cost block is replaced by "Nothing left to buy here." |

A click buys, saves, rebuilds the page and writes a status line. Nothing happens on hover.

**Proposed upgrade ladders** (all PLACEHOLDER numbers, editable in Server Setup):

| Upgrade | Levels | Effect per level |
|---|---|---|
| Storage | 8 | 1,000 / 2,500 / 5,000 / 10,000 / 20,000 / 40,000 / 80,000 / 160,000 items. Each Enchanted item counts as 1. |
| Auto-Compactor | 2 | I: crops -> Enchanted (100 : 1), only for crops whose Enchanted recipe you have unlocked. II: + seeds and other drops. On / Off switch. |
| Time Compressor | 5 | x1.10 / x1.25 / x1.50 / x1.75 / x2.00 to everything the shard makes |

Costs = coins + this shard's Enchanted crops + Eternal Seeds (`Plant_Seeds_<Crop>_Eternal`), plus a Farming-level requirement.

## 5. Tab: Islands (`research/cloud/shard-menu-1013/shard_c_islands_1080p.png`)

**Left panel:** "Islands around the hub" + "Pick a slot. Any island fits any slot; it grows in place." + "5 of 8 slots open" on the right.

**Map:** a `PanelInset` 676 x 496 at 36, 262, with a sky picture inside.

| Part | Rule |
|---|---|
| Hub | the hub island (portal arch + menu stand) at the map centre (374, 510), labelled "Hub (portal + menu)" |
| Slots | **8 fixed slots** on an ellipse, rx 250 / ry 168, numbered clockwise from the top (1 = N, 2 = NE ... 8 = NW). Each slot is a 92 px clickable circle. |
| Label | a dark pill (`#0a1222(0.67)`, 20 high) with Bold 13 text, 12 px under the circle. Slot 1's label sits to its RIGHT, so it stays clear of its own bridge. Under the label: 3 size pips (10 x 4; gold = the current size). |
| Bridges | drawn hub -> island for **filled** slots only (wood planks, 12 wide). Empty and locked slots show a faint dotted line where the bridge will appear. |

**Slot states** (`research/cloud/shard-menu-1013/shard_e_states.png`, part 5):

| State | Look | Label |
|---|---|---|
| Filled | a floating island drawn at its size: S r 26 / M r 34 / L r 42 | "Carrot · Small" |
| Selected | gold ring + a soft gold glow + a gold label | - |
| Hovered | a white ring + a 14 % white fill (a hover STYLE only, no page update) | - |
| Empty | a dashed white circle (r 30) + a gold "+" | "Add island" |
| Locked | a dim dashed circle, a dark fill and a padlock | "Farming 15" |

**Right panel** (side panel for the selected slot):

| Selected | Contents |
|---|---|
| **Filled** (drawn) | title "Slot 3 - Carrot Island"; "Island size": 3 `Tertiary` 100 x 30 (owned = Active with a gold label, next = a green label, later = 60 % faded). Then a `PanelInset` 308 x 128 with "now -> next" for: Size (blocks) 8 x 8 -> 12 x 12, Farm plots 64 -> 144, Totem places 1 -> 2, Carrot / hour 57 -> 129. Then "Cost to grow to Medium" (3 cost rows), **Grow to Medium** (`Primary` 308 x 44 at 752, 664) and **Totems on this island (n)** (`Secondary` 308 x 36 at 752, 718; it opens the Totems tab with that island's filter). |
| **Empty** (states, part 6) | "Pick a crop. Its island starts Small." A 3 x 2 grid of crop tiles (`Row` / `Row_Selected`, 100 x 74): a 32 px icon and the name. Locked crops are faded, with the reason in red 11 ("Carrot V", "Farming 15"). A note: one island per crop. Then "Cost to add a Corn island" and an Add / Missing button. |
| **Locked** (states, part 6) | a padlock 64; "Opens at Farming 15" (Bold 17 gold); "You are Farming 12" + a bar + "12 / 15"; the full list of when each slot opens |
| **Fully grown** (states, part 6) | all 3 sizes owned; the numbers without arrows; `Primary_Disabled` "Fully grown"; a hint to use totems |

Island sizes (PLACEHOLDER): Small 8 x 8 = 64 plots, 1 totem place; Medium 12 x 12 = 144, 2 places; Large 16 x 16 = 256, 3 places.
Slot openings (PLACEHOLDER): slots 1-4 at the start, then 5 / 6 / 7 / 8 at Farming 10 / 15 / 20 / 25. Slot 1 starts as the Wheat
island (Skyy's starting state).

## 6. Tab: Totems (`research/cloud/shard-menu-1013/shard_d_totems_1080p.png`)

**Left panel:**

| Part | Rule |
|---|---|
| Header | "Totems in this shard"; "4 of 6 places used" on the right |
| Filters | `Tertiary` buttons 28 high at y 246: All (4) / Wheat (3) / Lettuce (1) / Carrot (0). The active one = `Tertiary_Active`. Each is as wide as its text + 28. |
| Totem rows | `Row` 676 x 64, gap 4, from y 286. Each has: a 52 px slot with the totem icon; the name + tier in Bold 15; the island, workers and range in 12; a **status chip** top-right; "Upgrade slots n / 2" at the bottom right. The selected row = `Row_Selected`. |
| Free places | ghost rows (`Row` at 50 %, a dashed slot + "+"): "Free totem place - Carrot Island" / "Stand on the island and place a totem from your hotbar." with "x2" when there are several |
| Footer hint | how to craft totems (Farmer's Workbench), tier them up (Anvil, Upgrade tab), and how many places each island size gives |

6 rows fit (ending at y 690). Past that, the list scrolls.

**Status chips** (states, part 7): rounded, 20 high, Bold 12, an 18 % fill and a 75 % outline in the status colour.

| Chip | Colour |
|---|---|
| Working | `#39f493` |
| Waiting: nothing ripe | `#ffcc00` |
| Stopped: storage full | `#ff6b6b` |
| Picked up | `#878e9c` |

**Right panel** (the selected totem). This is the same block the totem's own right-click info page shows.

| Part | Rule |
|---|---|
| Header | a 72 px slot icon; name Bold 17; "Tier II of III · Wheat Island"; 3 tier pips |
| Stats | a `PanelInset` 308 x 104: Workers (2 Farming Sprites), Range, Harvest speed, Status |
| Upgrade slots | 2 x a 56 px slot, each with its name and effect (Wider Area +2 range; Auto-Replant on). "click a slot to change" (a picker of the matching items you carry) |
| Booster fuel (optional) | a 56 px slot + "Life Essence x12" + "+20 % growth · 31 m left" |
| Next tier | a `PanelInset` 308 x 64: "Next: Tier III", "Anvil -> Upgrade tab", the next stats in green |
| Buttons | **Pick up** (`Secondary` 150 x 36: the totem goes to your inventory with its slots and fuel) + **Go to totem** (enabled in the hub view; `Secondary_Disabled` + "inside the shard only" in the portal view) |
| None placed | a how-to panel (3 steps). Every place shows as a free-place row. The strip shows "0 totems · 0 items / hour". (`research/cloud/shard-menu-1013/shard_e2_empty_states.png`) |

## 7. 1366 x 768 (`research/cloud/shard-menu-1013/shard_f_check_1366x768.png`)

- **A - the client scales the UI to the screen height (x 0.711):** the whole page fits. 13 px text becomes about 9.2 px and 11 px
  becomes about 7.8 px. The 11 px texts are the slot numbers, the locked-crop reasons and "inside the shard only": they stay
  readable but small, so the build may raise them to 12.
- **B - the client does NOT scale (1 UI = 1 px):** 860 > 768, so 46 px is cut at the top and at the bottom. The header and the footer
  buttons are lost. Every existing 1100+ x 860+ page has the same problem (`research/cloud/ui-mockups-1013/Layout-Spec.md`
  section 6). The fallback, if B turns out to be true, is a compact 1100 x 720 variant (not drawn): fold the strip into the header,
  48 px rows and 500 px cards.

## 8. Build notes (proposed owner and ids)

- **Owner:** the shard mod (proposed SkyyShards, the reworked Pocket Shards in `research/cloud/Pocket-Shards-Spec.md`). One page
  class, with the tab kept in the page state. Every tab click rebuilds the page (click handlers may rebuild).
- **Element ids:** no underscores. The prefix is `#SkyySh`: `#SkyyShTab0..3`, `#SkyyShRow0..`, `#SkyyShSlot1..8`, `#SkyyShBuy0..2`,
  `#SkyyShCollectAll`, `#SkyyShEnter`, `#SkyyShPickup`, `#SkyyShTotem0..`.
- **Kit:** `Frame_World`, `Header`, `HeaderOrnament`, `Close`, `Tab*`, `Panel`, `PanelInset`, `CardFrame`, `Row*`, `Primary*`,
  `Secondary*`, `Tertiary*`, `SlotEmpty`, `ScrollTrack` / `ScrollHandle*`. All of them go through `tools/skyyui.py`.
- **Item icons** in rows and cost lines: `item_icon(id, item_id, size)` (`research/Vanilla-UI-Style-Guide.md` section 2), or an
  `ItemGridSlot` with `new ItemStack(id, qty)` ONLY - never a stack that may carry metadata.
- **Map:** a background picture (sky) plus 8 Buttons. Each Button's background = an island picture picked by crop x size, or the
  empty / locked picture. A slot's picture changes only on a page rebuild. Bridges are part of per-slot overlay pictures (filled /
  planned), so there is no runtime drawing.
- **Server Setup** (`tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`): the storage, compactor and compressor ladders and their costs;
  island sizes and costs; slot openings; Sacks-first on or off; the offline production cap.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Tabs: Collect / Upgrades / Islands / Totems, in that order, with Collect first because it is what you do most? | [yes] |
| 2 | How many fixed island slots around the hub, and when do they open? | [8 slots; 1-4 at the start, then Farming 10 / 15 / 20 / 25] |
| 3 | One island per crop in a shard, or may the same crop take two slots? | [one per crop] |
| 4 | Island sizes: Small 8 x 8 / Medium 12 x 12 / Large 16 x 16, with 1 / 2 / 3 totem places? | [yes] |
| 5 | Storage: 8 levels (1,000 -> 160,000 items), with each Enchanted item counting as 1? | [yes] |
| 6 | Auto-Compactor: 2 levels (crops, then + seeds and drops) with an On / Off switch? | [yes] |
| 7 | Time Compressor: 5 levels, x1.10 -> x2.00? | [yes] |
| 8 | Where do collected items go: Sacks first, then the inventory, with the rest staying in the shard? | [yes] |
| 9 | Per-item Collect buttons as well as Collect all? | [yes] |
| 10 | The portal view has a "Pick up Shard" button (with a confirm), or is a shard only picked up by breaking it? | [button + confirm] |
| 11 | A "Go to totem" button that teleports you next to a totem (inside the shard only)? | [yes] |
| 12 | Frame mood: the World hub's clear sky for every shard, or each shard its own sky (Mining dusk, Combat storm ...)? | [World clear sky] |
| 13 | Upgrades and islands cost coins too, or only items (Enchanted crops + Eternal Seeds)? | [coins + items] |

## For the local session (UNVERIFIED - needs the game or HytaleServer.jar)

1. **Portal right-click menu:** can a placed block (the shard portal) open our custom page on right-click (a block interaction ->
   `openCustomPage`) the way a vanilla portal opens its own menu? The same is needed for the menu stand on the hub island and for
   the totem info page.
2. **Private shard islands:** an instance or world per player per shard, how many a server can hold, and the teleport in / out
   (Enter Shard / Back to Island). This is the engine question already open in `research/Shard-Islands-Ideas.md`.
3. **Picture buttons on the map:** a Button with a pack picture as its Background (TexturePath) at 92 x 92, plus a full-size picture
   Background on a Group (the sky). `docs/answered/ui.md` line 78 says the .ui language supports it; it is not yet probed in OUR
   pages with OUR jar's pictures.
4. **Hover styles** on the slot Buttons and the rows: style-only (Hovered background), with no event (`HANDOFF.md` section 2: never
   update a page from MouseEntered).
5. **Item icons in rows and cost lines:** `item_icon` / ItemGridSlot with plain `new ItemStack(id, qty)`. Check that the ids exist:
   `Plant_Crop_*` (Wheat, Lettuce, Carrot, Corn ...), `Plant_Seeds_Wheat`, the 14 `Plant_Seeds_<Crop>_Eternal`, a Life Essence id,
   and our future Enchanted crop ids.
6. **Upgrade-slot picker:** clicking an empty totem slot opens a list of the matching items you carry. Dragging from the inventory
   into a custom page is NOT assumed.
7. **Text fit** with the real Nunito / Lexend glyphs (kit `text_width`). The longest labels are "3 islands · 4 totems · Time x1.25 ·
   412 items / hour" (Bold 15, 470 max), "Auto-Compactor (100 Lettuce each) · 50 XP each" (12, 330 max), "Totems on this island (3)"
   (Bold 14 in 308) and "Waiting: nothing ripe" (a chip). The `·` glyph exists in Nunito (check), or use " - ".
8. **Kit textures used here that no page has used yet:** `Frame_World`, `CardFrame`, `SlotEmpty` at 44 / 52 / 56 / 72 (it is a 74 UI
   texture with no Border, so it will be scaled). These need the in-game probe (kit README open point 9).
9. **1366 x 768:** does the client scale pages to the screen height (case A) or not (case B)? This decides whether the compact 1100 x
   720 variant is needed.
10. **Before speccing the system:** PROJECT-RULES section 2 asks for a survey of existing minion / garden / instanced-island mods
    (CurseForge + Skyy's Mods folder) before we build our own. This mockup does not replace that survey.
