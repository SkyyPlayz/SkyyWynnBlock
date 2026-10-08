# Fishing UI mockup - the click-bar minigame + the Fishing Bench page

Cloud draft, 2026-10-06. Paper design; nothing built. Picture: `research/cloud/Fishing-UI-Mockup.png` (A = the screen during a fight,
B = the six HUD widget states at 1:1, C = the Fishing Bench page, all four tabs at 1:1).
Inputs read: `research/cloud/SkyyFishing-Spec-Draft.md` (sections 2-4, 6, 11, 13), `research/Vanilla-UI-Style-Guide.md` (sections 0-6),
`HANDOFF.md` section 2, `tools/skyyui.py` (`COLOR`, `RARITY`, `QUALITY`), `docs/answered/ui.md`, `docs/answered/skills.md`, `docs/log/2026-10.md`.

**Decisions followed (not re-decided):**
- `docs/answered/skills.md` LOCKED 2026-10-06 FISHING: our own bench; parts crafted in one tab, rod rigged "in another tab in the bench";
  OUR click minigame - "as you click the bar goes up, and the fish pulls the bar goes down"; the "!" bite sign; length + weight on fish.
- `HANDOFF.md` section 2 rule 0 + `research/Vanilla-UI-Style-Guide.md`: every page from `tools/skyyui.py`, vanilla colours / frames /
  sounds, inline pages only, no underscores in ids, page root = Width / Height only, never periodic page updates, never a page update from a
  hover handler, ItemGridSlot only as `new ItemStack(id, qty)`, BIG readable pages that fit 1080 px.
- `docs/answered/ui.md` R9: menu hover tooltips stay ON - but nothing here NEEDS a hover: every number is printed on the row or in the
  right panel (the stuck-tooltip-after-Esc risk, and the "no hover info" rule for this mockup).
- `docs/answered/ui.md` 2026-10-03: HUD boxes as small as their text, side padding = top / bottom padding; HUD panel = vanilla `#000000(0.2)`.
- Spec Q3 default: fish foods are cooked at the Cooking Bench; the Recipes tab only lists them.

## 1. HUD or page? (the main design call)

| Part | Where | Why |
|---|---|---|
| Bite "!" | in the world (above the bobber) + a small HUD widget | the player is looking at the water, not a menu |
| The bar fight (0-12 s) | **HUD widget** (SkyyHud-style, inline document) | the style guide forbids **periodic page updates**; a page also grabs the mouse, so "click Use fast" would click the page, not the rod. The SkyyHud 0.3.12 combat widget already updates a bar + countdown live and is VERIFIED in game (log 2026-10-03) |
| Result (landed / lost) | the same HUD widget, 2-3 s, + one chat line | no page to close |
| Crafting, rigging, filleting, recipes | **one page**, four tabs (`tab_row`) | click-driven; rebuild on click is allowed |
| Angler's Ledger (book) | its own page later (stage 2) | not in this mockup |

So the minigame never opens a page. UNVERIFIED engine limits for the HUD path are in the local list (refresh rate, click input).

## 2. The Fishing widget (picture part B)

One HUD group `#SkyyFishW`, centred horizontally, about 150 px above the vitals (picture part A; vanilla HUD positions UNVERIFIED).
Size 440 x 96 at the readable text scale (title 16 px, captions 13 px). Shown only while a line is out; hidden otherwise.

| Element | Id (no underscores) | Kit look |
|---|---|---|
| Panel | `#SkyyFishW` | `panel(id, "hud")` = `#000000(0.2)`, padding 20 / 10 |
| State word (left) | `#SkyyFishWHead` | `label` bold 16; colour by state (table below) |
| Timer / grade (right) | `#SkyyFishWTime` | `label` bold 16, `value` colour; `warning` under 4 s |
| Bar | `#SkyyFishWBar` | `stat_bar(id, 400, 22, fill=...)` (drops its fill at 0); track `progressTrack` |
| Start tick | `#SkyyFishWTick` | 2 px `gold` line at `fish.barStart` (35 % default; moves with the Weighted Sinker) |
| Hint line (left) | `#SkyyFishWHint` | `caption` 13 |
| Click rate (right) | `#SkyyFishWCps` | `info` 13 bold - shows "7 per s" so a slow clicker sees why they lose |
| Fish icon (landed only) | `#SkyyFishWIcon` | `item_icon` 40 px of the species item |

### 2.1 States

| # | State | Head word / colour | Bar | Lines | How long |
|---|---|---|---|---|---|
| 0 | Line out, waiting | widget hidden (optional tiny "Line out" row, Server Setup `fish.hud.waitHint` off) | - | - | until bite / 60 s idle |
| 1 | **Bite** | BITE / `warning` `#ffcc00`, "Use now" right | warning-yellow, drains over `fish.biteWindow` 1.2 s | "1.2 s window" | 1.2 s |
| 2 | **Fight** | REEL IN / `title` | `progressBlue` `#4a7caa`, gold start tick | "Click Use fast" + click rate | until 0 / 100 / time-up |
| 3 | **Surge** | SURGE / `error` `#ff6b6b` | fill turns error red for the 0.6 s surge | "The fish pulls hard" | 0.6 s every 3 s |
| 4 | Almost | REEL IN | `progressGreen` `#7caa4a` above 80 | timer `warning` under 4 s | - |
| 5 | **Landed** | LANDED / `success` `#39f493`; grade name right in `SUI.QUALITY` colour | hidden | icon + "Trout 2.41 kg 52 cm"; gold "Personal record" / "Server record" only when true | 3 s (`fish.hud.resultSec`) |
| 6 | **Lost** | IT GOT AWAY / `error` | hidden | "The bar ran empty" or "Out of time" | 2 s |

Treasure and junk use state 5 with the kind as the grade line: "Lost Property - Great" (gold) / "Junk - Old Boot" (`disabled`).
Species, grade and weight stay hidden until landing (spec section 2 "Roll ... shown only after landing").
Grade colours use `SUI.QUALITY` (the game's item qualities: Common `#c9d2dd`, Uncommon `#3e9049`, Rare `#2770b7`, Epic `#8b339e`,
Legendary from the kit) - fish grades are item qualities, not SkyyGear rarities.

### 2.2 Update rule (no flicker, no spam)

| Event | What the server sends |
|---|---|
| Each accepted click | nothing on its own; the bar value changes in the server state |
| Every `fish.hud.tickMs` 100 ms (placeholder, shown as 0.1 s in Server Setup) during a fight | `set` on `#SkyyFishWBar` fill, `#SkyyFishWTime`, `#SkyyFishWCps` (3 b.set lines, the combat widget pattern) |
| State change (bite, surge on / off, landed, lost) | rebuild the widget document once |
| Over 12 cps | clicks ignored (`fish.maxCps`), the cps line turns `warning` "max 12" |

Accessibility: `fish.holdAssist` (spec Q4, off) - when on, the hint line reads "Hold Use to reel".

## 3. The Fishing Bench page (picture part C)

Opened by Use on the bench block (vanilla `OpenCustomUI` interaction, HANDOFF section 2). Kit: `page_shell(prefix, 1000, 760,
"Fishing Bench")` (+12 / +6 px ornaments = 778 px tall, fits 1080 with the HUD around it); body padding 17; `tab_row` of 4 tabs
(active = Primary, others Secondary, 5 px apart); a `status_line` above the footer; footer `button_row`, Close = Secondary + cancel
sound, right side. Every tab is the same page rebuilt on a tab click (no close-then-open). Prefix `SkyyFb` (ids `#SkyyFbTabParts` ...).

### 3.1 Tab PARTS (craft)

| Area | Content | Kit |
|---|---|---|
| Hint | "Craft rods, reels, hooks, lines and sinkers. Recipes open with Fish + metal collections." | `label` default |
| Left list 520 px | `section` heads ROD / REEL / HOOK / LINE / SINKER; one `static_row` per recipe: icon, name, one-line sub (the part's main stat + level), right tag | `scroll_list(well=True)` |
| Row tag | "Owned" `info` / "Craft" `success` (all ingredients there) / blank `rowBadge` (known, missing items) / the missing collection ("Pond Fish VI") greyed | `state_word` |
| Locked rows | shown greyed with the collection that unlocks them - R3: never a coin price | `disabled` colour |
| Right panel | 64 px item frame, name 18 px, "Tier 1 - Fishing Lv 10"; STATS `property_row`s; NEEDS rows "have / need" in `have` green or `outOfStock` red; collection gates "done" | `panel("well")` |
| Craft button | Primary, full panel width; Disabled look when anything is missing (and ignored in `handleDataEvent`) | `button(... disabled=True)` |
| Status | "- Need 3 more Plant Fibre" / "+ Crafted Copper Rod" | `status_line` |

Upgrade rule shown in the panel: "Upgrades from: Bamboo Rod" (each tier is crafted from the one below; the old item is consumed).

### 3.2 Tab RIG

| Area | Content |
|---|---|
| Left well "Your rig" | big 72 px rod slot (quality frame of the rod's SkyyRolls rarity - `quality_frame`, UNVERIFIED probe 8, else a plain frame) + name / rarity / level; four rows REEL / HOOK / LINE / SINKER, each a 44 px slot, part name, and a small Secondary "Remove" button (free, nothing destroyed - spec 4) |
| Empty slot | a grey "+" in the slot, name "empty" in `disabled` |
| Right well "Rig total" | `property_row`s: Max fish weight, Reel Power, Fishing Speed, Treasure Chance, Grade luck, Bar start, Time limit, Double catch, Junk, Fishing Wisdom. Bonuses in `success`, "-" in `disabled`; a capped stat shows "20 (cap)" in `warning` |
| Bottom "Parts in your bags" | `item_grid(id, 16, 2, tooltips=False)` of the parts the player carries (bags + inventory). Click = fit it into its slot (swaps the old part back to the bag). Slots get `new ItemStack(id, qty)` only - a part's tier / name is in its item id, so no metadata is needed |
| Footer | "Take rod out" (Secondary) left, Close right |

Rule: no rod in the slot -> the right well says "Put a rod in first" and the part rows are disabled.

### 3.3 Tab FILLET

| Area | Content |
|---|---|
| Column heads | FISH / GRADE / WEIGHT / FILLETS (`column_spec` heads) |
| List | every whole fish in the Fish Cooler + inventory: 44 px icon in its quality frame, name, grade (quality colour), weight "2.41 kg", fillets (1 per `fish.fillet.kgPer` 0.5 kg, max 40), a small "Fillet" button; under 0.5 kg: "0 - too small" + a disabled "Sell only" |
| Weight on the row | read by the server from the fish's metadata and printed as TEXT - the icon is `new ItemStack(id, 1)` without metadata (HANDOFF metadata rule) |
| Rare and better | the first click turns the row into a one-row `confirm_view(compact=True)`: "Fillet a Rare Catfish? Selling whole pays more." Confirm / Cancel |
| Under the list | "Fish Cooler 7 / 27" caption |
| Footer | "Fillet all Common" (Secondary; Common only, never a Rare+), "Open Cooler", Close |
| Status | "+ 15 Pond Fillets from Catfish 7.80 kg" |

### 3.4 Tab RECIPES

| Area | Content |
|---|---|
| Hint | "Fish foods. Cook them at the Cooking Bench - SkyyCooking grades them." |
| Left list 440 px | dishes (Grilled Fish, Fish Skewer, Fish Sticks, Chowder, Frost Cod Stew, Cinderfin Jerky): icon, name, focus line ("Stamina + Health"), tag Known `info` / Locked `disabled` |
| Right panel | ingredients have / need, "Effect at grade C" property rows (Stamina / Health now + over time, numbers from `research/cloud/Food-Expansion-Draft.md`), "Where: Cooking Bench" |
| Button | "Show in Cooking Bench" (Secondary) - only if a page link exists; else left out |
| Status | "= Recipe list only - nothing is cooked here" (`info`) |

## 4. Height budget (inner 966 x 688 = 1000 - 34, 760 - 38 - 34; checked with python)

| Part | px |
|---|---|
| Tabs 36 + gap 10 | 46 |
| Hint 20 + gap 8 | 28 |
| Lists / wells | 532 |
| Status line + gap | 34 |
| Separator gap + footer 36 | 48 |
| **Total** | **688 = inner height** (`sh.fit(...) == 0`) |

Rows: 51 px pitch on Parts (static rows 48 + gap 3, the kit `ROW_GAP`); Fillet / Recipes rows 52 + 4. Longer lists scroll (`scroll_list`);
no pager needed (nothing here moves under the cursor except Fillet, where the server re-reads the clicked fish by its slot before acting).

## 5. Sounds

| Action | Kit sound |
|---|---|
| Tab, Remove, Fillet, Open Cooler, list rows | light |
| Craft (Primary) | save |
| Close, Cancel in a confirm | cancel |
| Bite / landed / lost (HUD) | world sounds (splash; a vanilla pickup sound for landed; ids UNVERIFIED) - not UI sounds |

## 6. Server Setup rows added by this UI

`fish.hud.tickMs` 100 (shown as 0.1 s), `fish.hud.resultSec` 3, `fish.hud.lostSec` 2, `fish.hud.waitHint` off, `fish.hud.offsetY`
150 (px above the vitals), `fish.fillet.confirmFrom` Rare, `fish.fillet.allCommon` on. The SkyyHud widget editor may also move the widget
(SkyyHud drag canvas), like the other widgets.

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | HUD refresh: how often a HUD `set` can be sent per player without lag (the combat widget runs about 1 per s); 10 per s for a 12 s fight is the target, 4 per s the fallback (the bar then moves in steps) |
| 2 | Click input: does every right-click "Use" with the rod reach the server (one interaction per click, no client cooldown / hold-repeat)? If not, the fight needs another input (attack click, or a key bound through a HUD) - spec UNVERIFIED 7 |
| 3 | Does the HUD widget stay visible while the player holds Use (no "using item" overlay hiding it)? |
| 4 | Vanilla HUD positions at 1080p (hotbar, health / stamina / mana, the reticle) so `fish.hud.offsetY` avoids them |
| 5 | `quality_frame` (probe page 8) for fish grades and the rod's rarity; fallback = the plain item frame + coloured grade text (as drawn) |
| 6 | The real ContainerPatch / Header / button textures: the PNG uses flat stand-ins; the build uses `page_shell` / `button` |
| 7 | Splash / pickup sound ids for bite and landed; the "!" above the bobber (particle, model or floating text) |
| 8 | Whether a whole fish with weight metadata shows its weight in the vanilla tooltip at all (we print it on the row anyway) |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Bar fight as a small HUD widget near the bottom of the screen (you keep looking at the water), not a pop-up page? | [HUD widget] |
| 2 | Show your click rate ("7 per s") during the fight? | [yes] |
| 3 | Show the fish's species / grade only after it is landed (surprise), or the grade colour on the bar from the start? | [only after landing] |
| 4 | Fillet a Rare or better fish: ask once first? | [yes, ask from Rare] |
| 5 | Horizontal bar (as drawn) or a vertical bar like Stardew? | [horizontal - matches the combat widget] |
| 6 | Recipes tab: list only (cook at the Cooking Bench), or also cook right at the Fishing Bench? | [list only - spec Q3] |

## v2 (cloud draft, 2026-10-08)

Picture: `research/cloud/Fishing-UI-Mockup.png` (v2; v1 kept as `research/cloud/Fishing-UI-Mockup-v1.png`). Generator:
`research/cloud/fishing-ui/make_fishing_ui_v2.py` (Pillow, deterministic - two runs give the same bytes; it asserts both pages use exactly
their inner height, 688 / 688). Parts A-F: A the screen during a fight (50 %), B the minigame widget states, C the catch card, D the Fishing
Bench RIG tab, E the Pond Fish collection page, F the kit colours used.

**Decisions followed (v2 adds to the v1 list above):** `docs/answered/skills.md` 87 (junk = vanilla items, LOCKED 2026-10-06), 88 (all 4 hooks /
lines / sinkers, one of each on a rod), 90 (8 rod items, the fitted reel lives on the rod, icon shows the default reel, LOCKED 2026-10-07);
`docs/answered/gear.md` 102 (rod icons = the local 3D renders, LOCKED 2026-10-07); `research/Rod-Reel-Look.md`; `HANDOFF.md` section 2;
`research/Vanilla-UI-Style-Guide.md` sections 2-6 and 13.

### What changed vs v1

| Area | v1 | v2 |
|---|---|---|
| Sizes / text | vanilla 13-14 px text | the kit's **readable** scale (row names 18, subs 15, property rows 16 / 26 px, captions 15); buttons + tabs 44 px, small row actions 92 x 32 |
| Buttons | mixed-case labels | vanilla labels: bold, UPPERCASE, `#bfcdd5` / `#bdcbd3`; Disabled look `#797b7c` (empty LINE row) |
| Property rows | values right-aligned | `property_row` layout: bold key column, value left-aligned beside it (WorldEventPropertyRow) |
| Bench page | all 4 tabs | the **RIG** tab only (the gear-slot page asked for): rod slot 72 px + REEL / HOOK / LINE / SINKER rows, Rig total well, a 13 x 2 `item_grid` of parts. Parts / Fillet / Recipes stay as drawn in v1 |
| Rod + reel | rod and reel as separate rows | reel fitted ON the rod (skills.md 90): example Copper Rod with an Iron Reel; the icon shows the rod's default reel, the text shows the fitted one |
| Catch card | one LANDED line inside the widget | its own HUD card (460 x 132, same `#000000(0.2)` panel): 68 px slot, name in rarity colour, weight + length, record line in gold. Variants: record fish, plain fish, Lost Property, junk |
| Junk | "Junk - Old Boot" | a vanilla item (Stick) shown with an empty labelled slot - the real build uses the vanilla icon by item id, nothing copied |
| Fish names / icons | working names, rough icons | the catalog species (`research/cloud/Fish-Species-Catalog.md`) with our own icons from `research/cloud/fish-art/icons/`; lengths from the spec formula, K fitted to each species' min weight / min length |
| Collection page | not drawn | **new**: Pond Fish page (plain list window): tier + progress bar, 8 tier rows on the well, species grid 5 x 2 (found = icon + rarity bar, missing = dark shape + "?"), detail well for the picked fish (where, when, your best, caught, server record, sell price per kg) |
| Background | flat grey strip | the HUD states drawn over water, so the translucent panel is judged where it really sits |

Rarity on fish uses the pack ladder (`SUI.RARITY`), following the catalog proposal (species rarity = grade). That is still an open catalog
question; if Skyy keeps the spec's separate grade roll, only the word + colour swap to `SUI.QUALITY`.

### Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Catch card: a separate card for 3 s after a catch (as drawn), or only a chat line? | [card + one chat line] |
| 2 | Fish rarity: the pack ladder (Normal / Unique / Rare / Legendary / Fabled / Mythic, as drawn), or the game's item qualities (Common .. Legendary)? | [pack ladder - matches the fish icons] |
| 3 | Collection page: show the species grid (found / missing, your best, server record) here, or keep that for the Angler's Ledger book later? | [here now; the Ledger adds seasons and records later] |
| 4 | Show the server record weight to everyone on the collection page? | [yes, weight only, no player name] |
| 5 | Rig tab: one-click fit from the parts grid (click a part = it goes into its slot, the old one back to your bag)? | [yes] |
| 6 | v1 questions 1-6 above still stand (HUD widget, click rate, hidden species, fillet confirm, horizontal bar, recipes list only). | [as in v1] |

### For the local session

| # | Check |
|---|---|
| 1 | All v1 UNVERIFIED items (HUD refresh rate, click input, HUD positions, `quality_frame`, sound ids) still apply |
| 2 | Real textures: frame, tabs, buttons, ornaments are flat stand-ins; render the RIG and collection pages with `page_shell` / `tab_row` / `static_row` / `item_grid` and compare with this sheet |
| 3 | Rod icons in the rig slot and the parts grid are stand-ins drawn by the generator; use the local renders (`models-local/art/fishing`, `tools/art/make_fishing.py`) |
| 4 | Junk icon: the vanilla item's own icon by id (`Ingredient_Stick` etc.) via `ItemIcon` - confirm the ids from `Drops_Fishing_Trap_Crude.json` |
| 5 | Does a HUD document allow an `ItemIcon` (catch card)? If not: the fish name + weight only, icon in the chat line |
| 6 | Collection page: does SkyyCollections own it (a detail page) or SkyyFishing (its own page)? Cross-mod data only through `skyy.bridge` |
