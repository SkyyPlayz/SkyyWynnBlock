# /rebirth page (Nexus of the Void) - layout spec + mockups

Cloud draft, 2026-10-13. Paper design only; nothing built. The pictures and the generator are in `research/cloud/rebirth-page-1013/`.
The numbers (levels, points, XP, caps) are placeholders from `research/cloud/Rebirth-Research.md`. The layout sizes are the real proposal.

## Decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/skills.md` lines 114-116 (REBIRTH / NEW GAME+) | What resets (skill + class levels, coins + bank) and what stays (island, shard upgrades, gear, collection knowledge). Each rebirth raises the caps and gives a stat boost, points, a title and new content. |
| `docs/answered/skills.md` line 117 (REBIRTH TREE) | ONE menu, ONE tree radiating from the black hole. Rebirth when CLASS is max. Points are separate per skill. XP keeps counting past max. Costs start cheap and scale fast. About 8 levels in a row open the next row (no unlock points). |
| `docs/answered/skills.md` line 118 (REBIRTH CONTROL) | The Nexus is the controller: hover = requirements (met / not met) + what you get; click; then confirm. |
| `docs/answered/skills.md` line 120 (FISHING SKILL) | Fishing has its own arm. |
| `docs/answered/gear.md` lines 168-172 | Lifelong tools go back to Crude / level 0 but keep rarity + stats (listed in the confirm step). |
| `research/Rebirth-Ideas.md` "Locked same day" | If one big tree cannot be drawn, fall back to one tree per skill around the Nexus (picture f). |
| `docs/answered/ui.md` lines 80-82 (LOCKED 2026-10-10) | Pages use the SKY WINDOW kit (`art/ui-kit-sky/`). |
| `docs/answered/ui.md` line 28 | Menu hover tooltips are on by default. |
| `docs/answered/ui.md` line 93 (2026-10-13 VISUALS GO-AHEAD) | The local session reviews this before building. Extra care on layout. |
| `HANDOFF.md` section 2 + `research/Vanilla-UI-Style-Guide.md` | Inline pages only. No underscores in ids. Page root = Width / Height only (centred). **Never send a page update from a hover handler** (so hover can only show a tooltip, never change the page). |
| `research/cloud/Rebirth-Research.md` sections 2.3-2.7 | 8 arms x 11 nodes (rows 3 / 3 / 2 / 2 / 1, 5 levels each, keystone 1 level). Points = floor(B x sqrt(r)), B 12 class / 8 skill, r under 0.25 pays 0. Level cost = ceil(1.08^k). +3 % stats per rebirth. Bank bonus. 3-second count on the confirm button. |

## Files

| File | What it shows |
|---|---|
| `research/cloud/rebirth-page-1013/a_idle_1080p.png` | Main page, nobody hovering. The Nexus sleeps (Class 96 / 110). |
| `research/cloud/rebirth-page-1013/a_layout_annotated_1080p.png` | The same page with every panel box, the row radii, the Nexus and the chip ring marked. |
| `research/cloud/rebirth-page-1013/b_hover_notmet_1080p.png` | Hovering the Nexus while a requirement is NOT met. |
| `research/cloud/rebirth-page-1013/c_hover_met_1080p.png` | Hovering the Nexus with every requirement met (the Nexus is awake and glows gold). |
| `research/cloud/rebirth-page-1013/d_confirm_1080p.png` + `d_confirm_ready_crop.png` | After the click: the confirm step, counting (2 s left), then ready (Rebirth enabled, hovered). |
| `research/cloud/rebirth-page-1013/e_node_tooltip_1080p.png` | Hovering a part-levelled node (node tooltip), with another node selected in the right panel. |
| `research/cloud/rebirth-page-1013/f_fallback_tabs_1080p.png` | FALLBACK: one tab per arm and a row ladder going outward from a fixed Nexus. |
| `research/cloud/rebirth-page-1013/g_check_1366x768.png` | The 1366 x 768 fit check of the main page (A scaled, B unscaled). |
| `research/cloud/rebirth-page-1013/h_states_crop.png` | Nexus states, node states (2x), confirm button states (count and hold), the plain-text tooltip fallback, the locked node tooltip, arm colours. |
| `research/cloud/rebirth-page-1013/make_rebirth.py` | Pillow generator. Deterministic (checked: two runs give the same bytes, about 5 s). It asserts the tree layout: every node inside the canvas, at least 10 px between nodes, chips clear of the Nexus and the nodes. |

How it is drawn: the generator imports `research/cloud/ui-mockups-1013/make_mockups.py` for the 9-slice kit drawing, `world()`,
`button()`, the colours and the fonts, so this set matches the approved HUD / Settings mockups. The Nexus is loaded at render
time from `research/cloud/icons-1013/icons/Skyy_Nexus_Of_The_Void.png`. Re-run the generator after the icon is redrawn (the wisp
soul) and every picture updates. Fonts are stand-ins (Liberation Sans for Nunito Sans / Lexend); the game font is a little wider.

## 1. Main page (pictures a-e)

All positions are page-local px. 1 UI = 1 px at 1920 x 1080. The page is centred, so on screen it is at 160, 64.

| Part | Box (x, y, w, h) | Kit / look |
|---|---|---|
| Page root | 1600 x 952 (Width / Height only) | `Frame` (Border 32) |
| Header | 24, 18, 1552, 38 | `Header` (H 60, V 0) + `HeaderOrnament` 236 x 22 at y 6. Title "Rebirth - Nexus of the Void", Bold 18 `#b4c8c9`. `Close` 32 x 32 at 1540, 21. |
| Left panel | 24, 66, 316, 862 | `Panel` (Border 12) |
| Tree canvas | 356, 66, 888, 862 | `PanelInset` (Border 8) + a static void background picture (dark radial tint, faint stars, faint rings at the row radii) |
| Right panel | 1260, 66, 316, 862 | `Panel` |
| Gaps | 16 between panels; 24 to the frame | - |

There is no footer row. The tree needs the full height. Back sits at the bottom of the left panel, and Close is in the header.

### 1.1 Left panel - "Your rebirth" + points per arm

| Item | Position (page-local) | Look |
|---|---|---|
| Title "Your rebirth" | 40, 88 (left-middle) | Bold 16 `#afc2c3` |
| Nexus state line | 40, 112 | Bold 13. Asleep: `#ffcc00` "Nexus asleep - Class 96 / 110". Awake: `#39f493` "Nexus awake - Class 110 / 110". |
| 6 property rows | from y 142, every 24 px, 284 wide | Label 14 `#96a9be`, value Bold 14, right-aligned. Rebirths 6 / 10; Stat boost +18 % (green); Class cap 110; Skill caps +60; Bank bonus +1.10 % (green); Title Void-Touched VI (gold). |
| Gold line | y 284 | 1 px `#E8A93B(0.35)` |
| "Points to spend" + caption | y 306 / 326 | Bold 16 + 13 `#878e9c` "Each arm spends its own points." |
| 8 arm rows | `Row` (Border 8) 292 x 50, x 36, from y 340, every 54 px | 10 x 10 colour square at +12, +12; name Bold 15 `#d6e4ee` at +30, +17; sub-line 12 `#7f93a6` "Levels 27 / 55 - Row 4: 5 / 8"; points Bold 20, right-aligned at +280, with "pts" 12 under it. The points are **gold when the arm can afford its next level**, else grey. |
| Note | y 784-820 | 13 `#878e9c`: "Gold = enough for the next level. Prices rise with each level bought in an arm (cheap first)." |
| Back | 40, 876, 284 x 36 | `Secondary`, Bold 15 |

### 1.2 Tree canvas - the radiating tree

| Item | Value |
|---|---|
| Centre | 800, 497 page-local (960, 561 on screen) = the canvas centre |
| Arms | 8, every 45 degrees, Class straight up, then clockwise: Foraging (NE), Mining (E), Smithing (SE), Alchemy (S), Farming (SW), Fishing (W), Cooking (NW). Neighbours share a theme (Mining - Smithing, Farming - Alchemy, Fishing - Cooking). The shortest names are on the left / right arms, where a chip lies along its spoke. The 8 directions match the 8 little branches drawn in the Nexus icon, so each spoke continues one of them. |
| Rows (radius from the centre) | R1 178, R2 233, R3 288, R4 342, R5 390 (steps 55 / 55 / 54 / 48) |
| Nodes per row | 3 / 3 / 2 / 2 / 1. In a row the nodes sit on a line across the spoke: sideways -48 / 0 / +48 (3 nodes) or -27 / +27 (2 nodes). Row 5 = the keystone on the spoke. |
| Node size | 36 x 36 (keystone 44 x 44). The closest gap between two nodes (any arms) is 11.5 px (checked by the generator), so the 2 px selected ring still leaves 6 px. |
| Lines | Spoke from the Nexus plate (r 78) out to R5; at each row a fork starts 26 px before the row and runs to each side node. **Lit** (arm colour, 3 px, soft glow) up to the last OPEN row; the rest dim `#2c3448` 2 px. Lines show which rows are open; the nodes show the levels. |
| Arm chips | On r 120, 22 high, rounded, `#0b1224(0.92)` + a 1 px border in the arm colour; the arm name in CAPITALS, Bold 12, arm colour, 8 px side padding. |
| Nexus button | 144 x 144 hit area, centred. Picture layer 200 x 200: a dark plate (r 72, `#0b0818`), a 3 px ring, the 128 x 128 Nexus icon in the middle. See 1.4 for the states. |
| Margins | The outer keystone edge (+ ring) is 12 px or more inside the canvas. |

**Node states** (crop h, 2x; one picture per arm colour and state in game):

| State | When | Look |
|---|---|---|
| Locked | Row is 2 or more rows beyond the open ones | `#121825` disc, `#343c4e` rim, grey padlock |
| Next row | The first row that is not open yet | Dim disc, rim in arm colour at 40 %, "5/8" Bold 12 `#9aa6b6` = the levels in the row before / 8. Every node of that row shows it, so the player sees how far it is. |
| Open, level 0 | Row open, nothing bought | Dark disc, 5 grey ring segments, "0" Bold 15 `#96a9be` |
| Level 1-4 | Part levelled | Disc tinted with the arm colour (22 %), lit ring segments = the level, digit Bold 15 white |
| Maxed | 5 / 5 | Disc arm colour 62 %, all ring segments GOLD `#E8A93B`, soft glow |
| Keystone | Row 5 | 44 px, one full ring segment, an inner ring line |
| Hover | Mouse over | + 2 px white ring at r+2 (the TextButton Hovered background) |
| Selected | Last clicked | + 2 px `#ffe2a8` ring at r+4 |

### 1.3 Right panel - selected node, how it works, legend

| Item | Position | Look |
|---|---|---|
| "Selected node" | 1276, 88 | Bold 16 |
| Node well | 1276, 106, 284 x 268 | `PanelInset`. The node picture (selected) at the top left; name Bold 17 white; "Mining - Row 2" Bold 13 in the arm colour; what it does 13 `#878e9c`; rows Level / Now (green) / Next level (info blue) / Cost / You have (gold when enough, red when not), 14 px, every 24 px |
| Buy | 1288, 326, 260 x 40 | `Primary` "Buy level 4"; `Primary_Disabled` when the arm cannot afford it or the node is maxed |
| Status line | 1276, 396 | 13: "Click a node to select it here." or, after a buy, Bold green "+ Void-Forged Pick level 3 bought." |
| Gold line, "How the tree works" | y 414 / 436 | 6 lines, 13 `#96a9be`, every 19 px |
| Gold line, "Node states" legend | y 580 / 602 | 6 real node pictures + labels, every 44 px; ends at y 882 (inside 928) |

Buying is **click node -> Buy** (two clicks). A single click never spends points.

### 1.4 The Nexus - states and tooltips

| State | Look (crop h) |
|---|---|
| Asleep (a requirement not met) | Violet ring `#5b4a8f`, icon at 62 % brightness, no glow |
| Hover, asleep | + a white 2 px ring at r 76, a faint violet glow |
| Awake (all met) | Gold ring `#E8A93B`, a gold + violet glow, full-bright icon |
| Hover, awake | Awake + the white ring |
| Pressed | The icon shrinks to 120 px |
| Click while asleep | Nothing opens. The status line says "Reach Class 110 first." (red) |
| Click while awake | The confirm step (2) |

**Nexus tooltip** (pictures b + c): 400 wide (the vanilla tooltip MaxWidth), padding 16, `#0a101c(0.98)` + a 1 px `#E8A93B(0.6)`
border. Drawn just right of the Nexus plate (the client decides where a tooltip goes; UNVERIFIED).

| Block | Lines |
|---|---|
| Head | "Nexus of the Void" Bold 18 `#d8c8ff`; "Rebirth 7 of 10 - the void imprints your soul" 13 grey |
| REQUIREMENTS (gold Bold 13) | One line each: an icon (green tick / red cross / yellow warning), the name 14, the value Bold 14 right-aligned in the same colour: Class level 96 / 110 (cross) or 110 / 110 (tick); Rebirths done 6 / 10; No open Bazaar or AH orders OK; Not in combat OK; Mailbox empty: a WARNING (3 items), never a blocker |
| WHAT YOU GET (at Class 110 when not met) | 8 arms in 2 columns: colour square, name, points Bold 14 gold (grey "0" + "needs 25 %" for a skill under a quarter of its cap XP). Then All stats +3 % (18 -> 21 %); Caps Class 110 -> 120, skills +10; Bank interest +0.38 % (3.2M at reset); Title Void-Touched VII; "Next Mining point in 817,500 XP" (info blue) |
| Call to action | Not met: "Reach Class 110 to wake the Nexus" Bold 15 `#ffcc00`. Met: "Click the Nexus to rebirth" Bold 15 `#39f493`. |

Height 495 px for this content (fits at 1080 at any cursor height after clamping).

The scenario points come from the Rebirth-Research formula (python3, `math.floor(B * sqrt(r))`): Class r 1.0 -> 12; Mining r 2.3 -> 12;
Foraging r 1.2 -> 8; Farming r 0.6 -> 6; Fishing r 0.1 -> 0; Alchemy r 0.3 -> 4; Smithing r 0.8 -> 7; Cooking r 0.26 -> 4. Bank: 0.25 x
log10(1 + 3.2M / 100K) = 0.38. Next Mining point: (13 / 8)^2 x 2.4M - 2.3 x 2.4M = 817,500 XP (2.4M = placeholder XP to cap). Mining
has 27 levels bought, so its next level costs ceil(1.08^27) = 8.

**Plain-text fallback** (crop h): if the rich tooltip cannot be built, the vanilla `TextTooltip` (one label, 16 px, MaxWidth 400,
Padding 24) carries the same facts as text: "NO / OK" in place of the icons, the points in one sentence. The right panel then shows
nothing extra on hover (hover can never change the page).

**Node tooltip** (picture e): the same box. Name Bold 18 in the arm colour; "Smithing arm - Row 1 - node 2"; what it does; Level,
Now, Next level; Cost "3 Smithing points"; You have (gold or red); call to action "Click to select, then Buy" (green) or "Not
enough Smithing points" (red). Locked node (crop h): "locked", the effect at level 1, a red-cross line "Levels in Row 2 3 / 8" and
"Spend 5 more levels in Row 2 to open this row."

## 2. Confirm step (picture d)

| Part | Box (modal-local) | Look |
|---|---|---|
| Dim | the whole screen | `#000000(0.55)` over the page |
| Modal | 900 x 610, centred | `Frame` + `Header` "Rebirth 7 - touch the Nexus?" + `Close` (= Not yet) |
| Intro | centre, y 78 | 14 `#96a9be` "The void imprints your soul. Levels and coins reset; your progress stays." |
| RESETS / YOU KEEP | two `Panel` 418 x 236 at 24, 96 and 458, 96 | Title Bold 15 red / green + gold line; 6 lines each, 14 px, every 28 px, a small square bullet in the title colour |
| YOU GAIN | `Panel` 852 x 158 at 24, 344 | 8 `PanelInset` chips 200 x 34 (4 x 2, gap 10): colour square, arm name Bold 14, "+12" Bold 16 gold. Then one green Bold 14 line: "+3 % all stats (18 -> 21 %)  Caps +10  Bank +0.38 %  Title Void-Touched VII" |
| Note | centre, y 532 | Counting: Bold 13 `#ffcc00` "Read the lists - Rebirth unlocks in 2 s." Ready: 13 grey "This cannot be undone. Items are never deleted." |
| Buttons | y 554, 40 high | "Not yet" `Secondary` 220 wide at x 44; Rebirth 280 wide at x 576 |

**Rebirth button** (crop h):

| Option | States |
|---|---|
| A - 3-second count [recommended; Rebirth-Research 2.7] | "Rebirth (3)" -> "(2)" -> "(1)" in `Secondary_Disabled`, then "Rebirth 7" in `Danger` (Hovered when the mouse is on it). The server re-sends the label once a second (a timer, NOT a hover handler). |
| B - hold to confirm | `Danger` "Hold to rebirth", a gold fill grows over 1.5 s while the mouse is held, "Rebirth!" at full. Needs press / release events (UNVERIFIED). Only if A feels too weak. |

Resets / keeps lines follow `research/cloud/Rebirth-Research.md` 2.1 (the open choice "quests and zones stay" is Rebirth-Research Q5).

## 3. Fallback layout (picture f)

Use it if the engine cannot place children freely in a page, or show diagonal line pictures (section 5, items 1-3).

| Part | Box (page-local) | Look |
|---|---|---|
| Page | 1120 x 870 (inside the verified 1120 x 952) | `Frame`, same header |
| Tabs | 8 x `Tab*` 130 x 44 at y 66, gap 4, from x 24 | Arm name Bold 15 + the points in gold (enough for the next level) or grey; a 2 px line in the arm colour along the bottom (bright on the chosen tab) |
| Nexus column | `Panel` 24, 122, 260 x 724 | The Nexus button (same states + tooltip) fixed at the top; "Rebirth 7" + "Hover for details, click to rebirth"; the "Your rebirth" rows; "How the tree works"; Back at the bottom |
| Arm ladder | `Panel` 300, 122, 796 x 724 | Title "Mining arm" in the arm colour + "11 points to spend - next level costs 8" gold, right-aligned. 5 columns (Row 1 nearest the Nexus .. Row 5 keystone), 136 wide, gap 22. Column head: "Row 3" + "open - 5 levels" / "needs 8 in Row 3". |
| Node cards | 136 x 120, gap 10, centred in a 380 px column | `Row` / `Row_Selected`; name Bold 14; 5 level bars (6 high, arm colour, gold when maxed); "Level 3 / 5"; the effect 12 green; "Next: 8 pts" or "MAX". Locked = the card at 55 %, padlock, "Locked", "Row 3: 5 / 8" on the next row. |
| Connectors | 2 px straight lines only | out of each card -> a vertical bus in the gap -> into each card of the next column; arm colour when that row is open, else `#2c3448`. No diagonal lines, no pictures needed. |
| Selected node | `PanelInset` 764 x 150 at 316, 642 | node picture, name, effect; Level / Now / Next level; Cost / You have; `Primary` "Buy level 4" 170 x 40 |
| Status line | 316, 814 | Bold 14 green "+ Void-Forged Pick level 3 bought - 7 Mining points spent." |

Everything in the fallback is a plain Group / Label / TextButton at a fixed spot: it needs no rotation, no free placement beyond
what the hub pages already do, and no pan / zoom.

## 4. 1366 x 768 (picture g)

| Case | Result |
|---|---|
| A - the client scales the UI to the screen height (x 0.711) | The page becomes 1138 x 677 and fits with 114 px spare on each side. Smallest text 12 -> 8.5 px, node digit 15 -> 10.7 px, node 36 -> 26 px. Readable, and the same scale as the approved HUD check (`research/cloud/ui-mockups-1013/f_check_1366x768.png`). |
| B - no scaling (1 UI = 1 px) | The page is larger than the screen: 117 px cut on each side, 92 px top and bottom. The fallback page (1120 x 870) fits the width but not the height. The same is true of every page we have (1120 x 930), so this is the page system's question (Layout-Spec item 7), not this page's. |

## For the local session (UNVERIFIED - needs the game or HytaleServer.jar)

1. **Free placement in a page:** dozens of children at fixed Left / Top in one Group (the HUD does this; a page with about 100
   positioned TextButtons has not been tried). One probe page with 88 buttons at the listed spots.
2. **Diagonal lines:** the UI cannot rotate (`docs/answered/ui.md` line 20, the quest-arrow note). The plan uses PICTURES: one
   line picture per arm and per "rows open" state (8 arms x 5 states = 40 PNGs, generated at build time into the jar, each placed
   at its arm's bounding box), plus the static canvas background. Check that a transparent PNG Background on a Group draws
   above the canvas and below the buttons, and how many texture uploads one page may carry.
3. **Page width 1600:** 1120 is the widest verified page (`research/Settings-Spec.md` line 28). If 1600 does not render, use the
   fallback (f).
4. **Pan / zoom:** NOT needed. The whole tree fits at 1:1 (radius 390 + the keystone in an 862 px canvas). This removes the
   pan / zoom question raised in `research/Rebirth-Ideas.md`.
5. **Rich hover tooltips:** the vanilla `TextTooltip` is one plain label (16 px, MaxWidth 400). Coloured lines, icons and
   two columns (pictures b, c, e) need a richer tooltip (e.g. TextSpans in TooltipText, or a tooltip with child elements). If
   neither works, use the plain-text fallback in crop h. Never build the tooltip from MouseEntered (HANDOFF section 2 crash rule).
   The probe "tooltip" in `tools/skyyui.py` (TooltipText + TextTooltipStyle inline) comes first.
6. **Tooltip position:** the client places tooltips (probably at the cursor). The mockups draw them beside the hovered thing.
7. **Hold to confirm (option B):** needs press / release events on a button. Only Activating is proven. Option A (3 s count) needs
   only a server timer re-sending the label + `Disabled`; the `Disabled` look is itself a kit probe ("disabled-prop").
8. **The dim overlay + modal inside the same page:** a full-page Group shown / hidden by click handlers (click may rebuild). The
   proven alternative is the kit's `confirm_view` (an in-page confirm, SkyyRanks) replacing the tree area.
9. **Nexus "alive" effects** (slow swirl when asleep, pulse when awake) would need frame-swapped pictures on a timer. The mockups
   use still pictures; animation is optional.
10. **Per-state node pictures:** 8 arm colours x (locked, next-row, level 0-5) + keystone states + hover / selected overlays are
    generated pictures (no vanilla art). The digit is a Label on top, so only the disc + ring needs pictures.
11. **Text fit** with the real Nunito / Lexend tables (kit `text_width`): the longest are "Void-Forged Pick" (Bold 14 in a 136 px card),
    "Mining 11" in a 130 px tab, "SMITHING" / "FORAGING" chips, "Reach Class 110 to wake the Nexus" (Bold 15 in 368 px).
12. **The Nexus icon:** the generator loads `research/cloud/icons-1013/icons/Skyy_Nexus_Of_The_Void.png` (128 x 128). After the wisp
    redraw, re-run `python3 research/cloud/rebirth-page-1013/make_rebirth.py` and check the 8 icon branches still line up with the
    8 spokes (they point N, NE, E ... in the current icon).
13. **Numbers:** every number is a placeholder (Rebirth-Research); XP-to-cap per skill comes from SkyySkills.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is the main layout right: the whole star tree on one page (no pan / zoom), your rebirth + points on the left, the selected node + Buy on the right? | [yes, as drawn in a] |
| 2 | Arm colours and order (Class top, then Foraging, Mining, Smithing, Alchemy, Farming, Fishing, Cooking clockwise)? | [as drawn; colours in crop h] |
| 3 | Buying: click a node, then press Buy (two clicks), or buy straight from a click on the node? | [click + Buy - no accidental spends] |
| 4 | Confirm step: a 3-second count before Rebirth works, or hold the button for 1.5 s? | [3-second count] |
| 5 | Mailbox not empty: only a warning, or a blocker? | [warning only] |
| 6 | Show "next row 5/8" on the nodes of the next row (as drawn), or only in the tooltip? | [on the nodes] |
| 7 | If the big page cannot be built, is the tab-per-arm page (f) a good backup? | [yes] |

## Reuse note

No existing Hytale rebirth / prestige page was surveyed for this sheet (cloud has no CurseForge access); the layout reuses our own
kit and the approved mockup kit. A survey per PROJECT-RULES section 2 belongs to the rebirth spec round.
