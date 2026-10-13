# HUD + Settings mockups (Sky Window kit) - layout spec

Cloud draft, 2026-10-13. Paper design only; nothing built. Pictures and generator are in `research/cloud/ui-mockups-1013/`:

| File | What it shows |
|---|---|
| `research/cloud/ui-mockups-1013/a_quest_1080p.png` + `a_quest_crop.png` | (a) Quest widget in game + 5 states at 1:1 |
| `research/cloud/ui-mockups-1013/b_feed_1080p.png` + `b_feed_crop.png` | (b) Notification feed in game + opacity stages, card life, merging, card types |
| `research/cloud/ui-mockups-1013/c_skillxp_1080p.png` + `c_skillxp_crop.png` | (c) Skill-XP flash: before / during / after, level up, hidden skill |
| `research/cloud/ui-mockups-1013/d_settings_1080p.png` + `d_settings_crop.png` | (d) Settings -> Messages page (Chat / Feed / Off per message type) |
| `research/cloud/ui-mockups-1013/e_layout_1080p.png` + `e_layout_clean_1080p.png` | the whole proposed 1080p HUD, annotated and clean |
| `research/cloud/ui-mockups-1013/f_check_1366x768.png` | the 1366 x 768 check (A scaled, B unscaled worst case) |
| `research/cloud/ui-mockups-1013/make_mockups.py` | Pillow generator; deterministic (checked: two runs give the same bytes, about 6 s) |

The page uses the real kit textures from `art/ui-kit-sky/Common/UI/Custom/SkyyKit/`, 9-sliced the way the client does it (@2x
texture, Border in UI units, 1 UI = 1 px at 1080p). Fonts are stand-ins: Liberation Sans in place of the game's Nunito Sans
(Default) and Lexend Bold (Secondary). The game font is a little wider, so the build must run the kit's `text_width` fit check.

## Decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/ui.md` line 89 (2026-10-12 CHAT OVERFLOW) | Skill XP leaves chat and flashes on the HUD skill list, batched every ~2 s. A second system, the FEED (small stacking cards that fade, bottom-left), merges repeats ("Pumpkin x9"). Chat keeps level-ups, rank-ups, rare drops, quest / party / guild / server lines. Per-player Settings send each message type to Chat / Feed / Off; the server defaults live in Server Setup. |
| `docs/answered/ui.md` line 92 (2026-10-12 QUEST WIDGET = ESSENTIAL) | An always-on HUD quest widget (SkyyHud) showing the next 1-3 tasks, progress and where to go. It never needs a menu. |
| `research/Tutorial-Plan.md` lines 11-18 | Tasks are not linear: the widget always shows the next 1-3 UNDONE tasks. "I know how to play" hides tutorial tasks, but the widget stays for quests. |
| `docs/answered/ui.md` line 16 (LOCKED 2026-10-03) | HUD boxes are as small as their text, and the side padding equals the top / bottom padding. |
| `docs/answered/ui.md` lines 80-82 (LOCKED 2026-10-10) | Pages use the SKY WINDOW kit. |
| `docs/answered/ui.md` line 93 (2026-10-13 VISUALS GO-AHEAD) | The local session reviews this before building. Extra care on layout. |
| `HANDOFF.md` section 2 + `research/Vanilla-UI-Style-Guide.md` sections 4-6 | Inline documents only. No underscores in ids. A page root has Width / Height only (centred). Kit colours. Never send a page update from a hover handler. |
| `research/Settings-Spec.md` sections 2.2 + 4.2 | The existing per-player switches and tabs. The verified page size is 1120 wide x 952 high. |

How SkyyHud draws widgets today (read-only, `SkyyHud/build_skyyhud_0.3.18.py`):

| Fact | Lines |
|---|---|
| Built-in default spots: Coords tl 8,8; Zone tr 8,8; Game Clock bl 8,40; Coins br 8,8; Online tr 8,206 | 635-636, 683 |
| Party tl 8,320 (340 x 116); Guild tl 8,444 (260 x 94) | 641-645 |
| Skills tl 8,544; 180 wide; rows 20; font 12; pad 3; level column 40 | 654-658 |
| Combat t 0,130 (180 x 37), under the vanilla compass and boss bar (BossBar.ui Top 57, 66 high) | 166, 662-667 |
| Minimap tr 8,40, 160 x 160 | 676-678 |
| Dynamic Seasons (theirs) br 0,250, 96 x 320 | 687-689 |
| Abilities tl 8,760, 220 x 59 | 694-697 |
| Every box: `Background: #0b1524(0.72)`; default text `#eaf6ff` | 2432, 2443, 2140 |
| Anchors and clamps work in a 1920 x 1080 space (tl / t / tr / l / c / r / bl / b / br + dx / dy) | 2117-2124, 2450-2510 |

## 1. The proposed 1080p layout (picture e)

All positions are at 100 % size and UI scale 1 (1 UI = 1 px at 1920 x 1080). The generator checks every box against every other
box and against the shaded vanilla areas. **Result: no overlaps at 1080p.**

| Widget | Anchor | Box (x, y, w, h) | Change |
|---|---|---|---|
| **Quest (NEW)** | tl 8,42 | 8, 42, 300, 149 (3 tasks) | new; sits right under Coords (8..34) |
| Party | tl 8,200 | 8, 200, 340, 116 | MOVED from tl 8,320 so it clears the quest widget |
| Guild | tl 8,324 | 8, 324, 260, 94 | MOVED from tl 8,444 |
| **Feed (NEW)** | bl 8,488 | 8, 452, 280, 140 max | new; its bottom edge is 8 px above the chat (est.) |
| Skills | tr 8,240 | 1732, 240, 180, 3 + 20 x lines + 3 | MOVED from tl 8,544 to the right edge, where Skyy keeps it (the 2026-10-06 Seasons screenshot) |
| Abilities | br 460,21 | 1240, 1000, 220, 59 | MOVED from tl 8,760: right of the hotbar, out of the chat area |
| Coords, Zone, Minimap, Game Clock, Coins, Combat, Online, Seasons | unchanged | - | - |

Arithmetic (python3): the feed bottom edge is 1080 - 488 = 592 = chat top (600, est.) - 8. Its top is 592 - 140 = 452. The gap to
Guild is 452 - (324 + 94) = 34. The gap from Quest to Party is 200 - (42 + 149) = 9. Abilities: br dx = 1920 - 220 - 1240 = 460.

Moves only change the BUILT-IN default. Saved layouts are never moved (the 0.3.16 rule).

### Vanilla HUD areas (shaded red; ESTIMATES unless cited)

| Area | Box used (x, y, w, h) | Source |
|---|---|---|
| Compass | 700, 8, 520, 40 | est. |
| Boss bar | 660, 57, 600, 66 | BossBar.ui Top 57, 66 high (SkyyHud line 166) |
| Chat | 8, 600, 560, 360 | est. |
| Chat input (only while typing) | 8, 966, 560, 30 | est. |
| Held item name | 760, 904, 400, 30 | est. |
| Health / Stamina / Mana | 690, 940, 540, 54 | est. |
| Hotbar | 690, 1000, 540, 68 | est. |
| Vanilla item pickup popups | 1560, 760, 352, 220 | est. (Dynamic Seasons already sits inside this area at its own spot) |

## 2. (a) Quest widget - drawn by SkyyHud, data from SkyyQuests

| Item | Value |
|---|---|
| Size | 300 wide. Height follows the content: 149 with 3 tasks, 124 with 2, 99 with 1 (bar + where). |
| Box | `#0b1524(0.72)` (the SkyyHud box) + a 1 px gold hairline `#E8A93B(0.45)`, drawn as four 1 px Groups (no texture) |
| Padding | 10 on all sides (Skyy's equal-padding rule) |
| Rows, top to bottom | header 18 / gap 6 / gold line 1 px `#E8A93B(0.35)` / gap 7 / task 1 name 18 / gap 4 / bar 6 / gap 4 / where 15 / gap 8 / task 2 17 / gap 8 / task 3 17 |
| Header | gold diamond (8 px) + quest or chapter name, Bold 13 `#E8A93B`; step count "3 / 21" 12 `#878e9c`, right-aligned |
| Task 1 (do this now) | gold diamond + name Bold 14 `#d6e4ee`; progress "6/10" Bold 14 `#ffffff`, right-aligned |
| Task 1 bar | indented 14, height 6; the vanilla ProgressBar (`Common/ProgressBar.png` + `ProgressBarFill.png`, as in the Combat widget); the mock shows the fill as `#7caa4a` |
| Where to go | 12 `#7caacc` (info): an 8-way arrow in a ring + "NE  42 m  -  Old Grove". With no direction: text only. |
| Tasks 2-3 | hollow diamond, name 13 `#96a9be`, progress 12 `#878e9c`. A long name ends in "..." (fit to width). |

**States** (crop a):

| # | State | Look |
|---|---|---|
| 1 | Default | Next 3 undone tasks in suggested order |
| 2 | Task done | Tick + `#39f493` green name / progress / bar. The where line becomes "Done!  +25 coins  +40 Foraging XP" (Bold 12 green) for **2.5 s**, then the list moves up one. |
| 3 | Quest (not tutorial) | Same layout, quest name in the header |
| 4 | Compact | 1 task (player setting "Tasks shown: 1 / 2 / 3") |
| 5 | Nothing to do | "No active quests" in `#96a9be` + "Pick one at the quest board in the hub". The player setting "Hide when empty" is ON by default. |

**Direction:** the arrow is north-up, the same as the minimap. It shows the world direction to the target, so it needs no head turn
and the 1 s tick is enough: 8 pictures, one per direction (`N`, `NE` ...), because HUD pictures cannot rotate (`docs/answered/ui.md`
line 20). The fallback is the text "NE" alone. The distance is in blocks ("42 m"), rounded to 1 below 100 and to 10 above it.

**Refresh:** a progress change is pushed at once (shape unchanged = Set the texts and bar Value only). Done, next task or a task-count
change = the shape re-send (at most once per 1.5 s, the 0.3.8 rule). The distance and arrow use the existing 1 s tick.

**Limits:** at most 3 tasks; names cut to fit 300 px; one quest at a time. A "tracked quest" choice belongs in the quest log page.

## 3. (b) Notification feed - drawn by SkyyHud, fed by every mod through the bridge

| Item | Value |
|---|---|
| Anchor | bl 8,488 (bottom edge 8 px above the chat). The stack grows UPWARD; the newest card is at the bottom, next to the chat. |
| Card | 280 wide; 32 high (one line) or 44 (two lines); gap 4 |
| Height budget | 140 px = 4 one-line cards (4 x 32 + 3 x 4). A two-line card counts its real height, so only 3 cards fit then. The oldest card leaves first. |
| Card box | `#0b1524(0.72)` + 1 px hairline `#E8A93B(0.30)` |
| Icon | 22 x 22 at x 6, centred in the first 32 px. It is the item's own icon if the HUD can show one (UNVERIFIED), else a category picture. |
| Name | Bold 14 at x 36, `#d6e4ee`. Coins and double drops use gold `#E8A93B`, heals `#39f493`, pet XP `#d2b8ff`. |
| Count | Bold 14 `#ffffff`, right-aligned, 10 px from the right edge ("x9", "7/10") |
| Second line | 12 `#7f93a6` at y 33 + a 4 px bar (`#7caa4a`) up to x 270 (collection progress) |

**Timing** (all server settings in Server Setup, shown in seconds):

| Step | Default |
|---|---|
| Card fully shown | 4.0 s |
| Fade | 4.0 -> 5.0 s in 3 steps: 60 % at 4.3 s, 25 % at 4.7 s, gone at 5.0 s (crop b, panels A and B) |
| Merge window | The same key (item id / message type) within **3 s** of the card's last change adds to its count ("Pumpkin x1 -> x4 -> x9") and restarts its 4 s |
| Merge highlight | The count turns gold and the hairline goes bright (`#E8A93B(0.85)`) for 0.3 s |
| Overflow | A 5th card pushes the oldest out at once (no fade) |
| Rate | At most 1 HUD update per 250 ms per player for the feed; extra pushes in that window are merged |

**Card types:** item pickup; double drop / perk proc; collection progress (two lines); coins (interest, payments); heal / buff;
pet XP / guild XP; quest progress ("Chop logs 7/10"). Repeats merge by key: `pickup:<itemId>`, `coins:interest` and so on.

## 4. (c) Skill-XP flash - drawn by SkyyHud's Skills widget, numbers from SkyySkills

Skills widget maths are unchanged: 180 wide, 20 px rows, font 12, pad 3, 40 px level column.

| Item | Value |
|---|---|
| Batch | XP per skill is added up for **2.0 s**, then one flash shows the total ("+79") |
| Flash length | **3.0 s**. 0-0.5 s: full tint. 0.5-3.0 s: the tint fades in 2 steps (30 % -> 14 % -> 0). The "+79" stays until 3.0 s. A new batch during a flash adds to the number and restarts the 3 s. |
| Row tint | `#E8A93B` at 30 % + a 2 px gold left edge (`#E8A93B(0.95)`) |
| Gain text | Bold 12 `#39f493`, right-aligned 6 px left of the level column. Over 999 it shortens: "+1,240" then "+12.4k". |
| XP bar | 2 px along the row bottom, 6 px in from both sides; fill `#39f493(0.9)` on `#000000(0.5)` = progress to the next level |
| Level up | "LEVEL UP" Bold 12 `#E8A93B` + the level number in gold for 3 s. Chat keeps its level-up line (CHAT OVERFLOW point 4). |
| Hidden skill | If the skill's line is OFF in the widget, a temporary row (name and level in `#b7cedd`) joins at the bottom for the flash, then leaves. The box grows 20 px; a bottom-anchored box grows upward. Widget setting: "Show hidden skills while gaining XP: Show / Hide" [Show]. |
| Widget off / not installed | The route falls back to Chat |

## 5. (d) Settings -> Messages page - drawn by SkyyMenu (Settings), routes read by every mod

| Item | Value |
|---|---|
| Page | 1100 x 860, centred (fits the verified 1120 x 952). Kit `Frame` (Border 32); `Header` 1052 x 38 at 24,18 (H 60, V 0); `HeaderOrnament` 236 x 22 at Top -12; `Close` 32 x 32. Title "Settings", Bold 18 `#b4c8c9`. |
| Tabs | 8 x `Tab*` (H 20, V 12), 128 x 44, gap 4, at y 66. **Messages** is new and first; the other 7 are Settings-Spec section 2.1. The tab text is 15 Bold. |
| Left panel | `Panel` 716 x 642 at 24,122. Title "Where each message goes" 16 Bold `#afc2c3` + a caption 13 `#878e9c`. |
| Rows | `Row` / `Row_Hovered` / `Row_Selected` (Border 8), 692 x 48, gap 4. Name Bold 15 `#d6e4ee`; help line 12 `#7f93a6` (example text, cut to fit). |
| Segmented toggle | 3 x `Tertiary` 92 x 30, gap 2 (280 wide), 16 px from the panel's right edge. The chosen one uses `Tertiary_Active` with a white label; the others have a `#bdcbd3` label, Bold 13. A small gold dot (5 px, `#E8A93B`) marks the server default. |
| Locked row | The options the server locks are `Tertiary` at 45 % with `#797b7c` labels and are not bound (System and server = always Chat) |
| Right panel | `Panel` 324 x 642 at 752,122. Preview of the selected row (a real feed card at 1:1 in a `PanelInset`, the same line as chat text), what Off means, a legend, and "Open HUD Editor" (Secondary 292 x 36). |
| Footer | Status line Bold 15 `#39f493` ("+  Coins: Chat - saved.") at y 784; gold line; Back (Secondary 150 x 36), Reset to defaults (Danger 210 x 36, with a confirm), Close (Secondary 150 x 36). |

**Rows and server defaults** (11 rows; 11 x 52 = 572 px fits the 642 px panel with its 60 px title):

| Row | Options | Default |
|---|---|---|
| Item pickups | Chat / Feed / Off | Feed |
| Double drops and perk procs | Chat / Feed / Off | Feed |
| Skill XP | Chat / **Skill list** / Off | Skill list |
| Skill level-ups | Chat / Feed / Off | Chat |
| Coins (interest, payments) | Chat / Feed / Off | Feed |
| Collection progress | Chat / Feed / Off | Feed |
| Collection rank-ups (with unlocked recipes) | Chat / Feed / Off | Chat |
| Quest progress | Chat / Feed / Off | Feed |
| Heals and buffs | Chat / Feed / Off | Feed |
| Pet and guild XP | Chat / Feed / Off | Feed |
| System and server | Chat (locked) | Chat |

Clicking an option saves at once and rebuilds the page (click handlers may rebuild). Nothing happens on hover.

## 6. 1366 x 768 check (picture f)

- **A - the client scales the UI to the screen height (x 0.711):** the 1080p layout as it is. 14 px text becomes about 10 px and 12 px
  becomes about 8.5 px. It is still readable, and there are no new overlaps.
- **B - the client does NOT scale (worst case; 1 UI = 1 px):** corner anchors keep their offsets on a 1366 x 768 screen. The
  generator finds:
  - Party and Guild (when shown) run into the chat;
  - Dynamic Seasons runs into the pickup popups;
  - the Feed has to shrink to 81 px (2 cards) to stay above the chat, and then touches Party (when shown).

  Rule for the build: feed height = min(140, chat top - 8 - (the lowest shown top-left box above it) - 8), and never fewer than
  1 card. If 1 card does not fit, the feed moves to the right of the chat (x 576) instead.
- The 1100 x 860 page does not fit 768 px unscaled. That is true of every existing page too (they are 1120 x 930).

## 7. Who draws what

| Part | Mod | Bridge (plain java.lang types; `skyy.bridge` map) |
|---|---|---|
| Quest widget | SkyyHud (new widget id `Quest`, APPENDED to `Widgets.IDS`) | SkyyQuests publishes `quest:fn:hud` apply(UUID) -> Object[] {title, count, then per task: name, progress, Double frac or null, where, Integer dir 0-7 or -1, Boolean done} |
| Feed | SkyyHud (new widget id `Feed`) | `feed:fn:push` accept(Object[] {UUID, String type, String key, String name, Long count, String colour, String sub, Double frac}). Each sender first asks `settings:fn:route` -> "chat" / "feed" / "off". |
| Skill-XP flash | SkyyHud (the Skills widget) | SkyySkills keeps the per-skill 2 s sums; `skill:fn:flash` apply(UUID) -> Object[] {skill, Long gain, Double frac, Boolean levelUp} |
| Messages tab + routes | SkyyMenu (Settings, `research/Settings-Spec.md`) | `settings:fn:route` apply(UUID, String type); the server defaults are in Server Setup through `tools/skyycfg.py` |

**Migration:** the Settings-Spec ON / OFF switches that these rows replace (`skills.xpGain`, `skills.doubleDrop`, `coll.tierUp`,
`bank.interest` ...) map ON -> the row's default and OFF -> Off. This is a one-time migration under PROJECT-RULES section 4.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Feed spot: bottom-left directly ABOVE the chat (Party / Guild / Skills / Abilities defaults move to make room), or in the empty lower right above the Coins (no moves needed)? | [above the chat, as drawn] |
| 2 | Move the built-in Skills widget to the right edge (tr 8,240) like your own layout, and Abilities next to the hotbar? Saved layouts never move. | [yes] |
| 3 | Quest arrow: north-up like the minimap ("NE 42 m"), or turning with your view (needs a faster update)? | [north-up] |
| 4 | Feed card time 4 s + 1 s fade, merge window 3 s, at most 4 cards? | [yes; all editable in Server Setup] |
| 5 | Skill XP: flash on the skill list, and also show a skill row that is switched off while it gains XP? | [yes, temporary row] |
| 6 | Messages tab: first tab of Settings, 11 rows as listed, System locked to Chat? | [yes] |
| 7 | HUD box look: keep SkyyHud's `#0b1524(0.72)` with a thin gold line on the new widgets, or vanilla `#000000(0.2)` (Style Guide Q7)? | [SkyyHud box + gold hairline] |
| 8 | Quest widget when there is nothing to do: hide it, or show "No active quests"? | [hide] |

## For the local session (UNVERIFIED - needs the game or HytaleServer.jar)

1. **The vanilla HUD positions** (chat, hotbar, vitals, compass, pickup popups, held item name) are estimates. Take one 1080p
   screenshot with chat open and measure them, then re-run the generator with the real `VANILLA` boxes. If the chat is taller, the
   feed's `bl` dy grows.
2. **HUD fade:** there is no proof that a HUD element can animate or change its alpha smoothly. The plan is server-stepped Sets of
   the card's `Background` alpha and the label `TextColor` alpha (3 steps). SkyyHud's tick is 1 s, so the feed needs its own
   250 ms timer, or the fallback: 1 s steps (100 % -> 50 % -> gone).
3. **Partial HUD updates for the feed:** a card added or removed = a shape change. Check that the 1.5 s shape re-send limit
   (0.3.8) is not too slow for the feed. A fixed 4-slot document (empty slots hidden), changed with Sets only, avoids re-sends.
   [recommended]
4. **Item icons in a HUD** (ItemGridSlot or an item icon Background in a HUD document) are unproven. The fallback is category
   pictures from our asset pack. A pack picture as a HUD Background is itself still UNVERIFIED (the 0.3.18 ability-icon trial).
5. **Arrow pictures in the HUD:** same pack-picture risk as item 4; the text-only fallback is "NE 42 m".
6. **Hiding vanilla pickup popups:** can the server stop the client's own item pickup popups (the 201 toasts in the 2026-10-11
   session) once the feed shows pickups? Otherwise both show.
7. **Does the client scale the HUD and pages with screen height?** This decides 1366 x 768 case A vs B (picture f).
8. **The text fit** with the real Nunito / Lexend glyph tables (kit `text_width`): the longest labels are "Double drops and perk
   procs" (15 Bold), "Skill list" in a 92 px button, and "Craft a crafting accessory" in the 300 px quest widget.
9. **Is the HUD still visible behind a custom page?** Picture d shows the world only.
10. Kit textures used on the page: `Frame`, `Header`, `HeaderOrnament`, `Close`, `Tab*`, `Panel`, `PanelInset`, `Row*`,
    `Tertiary*`, `Secondary*`, `Danger`. All are from `art/ui-kit-sky/` and still need their in-game probe (kit README open point 9).
