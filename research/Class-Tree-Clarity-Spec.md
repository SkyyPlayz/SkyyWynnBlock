# Class Tree Clarity - abilities, loadout, the OR pick, the panel overlap (spec, 2026-10-23)

Owner: Skyy (they/them). Status: SPEC (UI agent, 2026-10-23). Nothing built. Mock: `research/class-tree-clarity-mock.png`.
Where answers go: Skyy's answers to section 7 -> `docs/answered/classes.md` (one line, word for word, via `python tools/qa_append.py`);
the build -> the rounds in section 9; decisions found here that need Skyy -> `OPEN-QUESTIONS.md` by the main session.

Skyy 2026-10-23 (screenshot Trees > Class > Priest, Bulwark Row 2 Shield Bubble selected; docs/answered/classes.md line 226): "the few
things that confused me. where/ how to i unlock the ability's (i found it, but it was weird. use the ability icons.) where do i equip
the ability's and modifiers now? and last, our alternatives on the second ability are either or, how do you actually pick one or the
other? these all need to be clear in the tree"

Rules this follows: research/Menu-Pattern.md 3.4 (one Primary per view, locked shows how to unlock, no new menu), Vanilla-UI-Style-Guide
15 (bigger, colour coded text) + 16 (node maps: one page packet per click, no hover tooltips / AssetImage swaps until probed),
HANDOFF section 2, tools/CONFIG-CONTRACT.md (every new number = a Server Setup row), docs/answered/classes.md 10-04 (A1, A2, A2-alt,
two A1-alts, pick ONE), 10-08 (4 abilities, 2 primaries on Ability 2 / 3, 2 alts on crouch + Ability 2 / 3), 10-14 (abilities and
modifiers controlled in the class tree panel), 10-16 (abilities where you unlock them, modifiers out of the tree, both slots open with
the ability), 10-23 (a few flat modifier-type upgrades stay in the tree).

## 1. How it works TODAY (SkyyTrees 0.5.0 + SkyyClasses 0.1.46, read from the build scripts)

### 1.1 How an ability is unlocked

- The class tree (tools/trees_v3_data.py) gives each ability free with a ROW: the row's `free` = `("abil", <line>, <id>)`. You never
  click or buy it; it is yours the moment the row opens, and a row opens on the TOTAL points spent anywhere in that tree (0 / 5 / 10 /
  15 / 20 / 25).
- Priest: Devotion row 1 Sacred Heal (A1, 0 points); at 5 points THREE at once: Devotion row 2 Martyr's Grace (A1-alt B), Bulwark row 2
  Shield Bubble (A2), Hallowed Ground row 2 Sanctuary (A1-alt A); Bulwark row 5 Guardian Spirit (A2-alt, 20 points). Every class has the
  same pattern (A1 row 1, A2 + the A1-alts at row 2, A2-alt at row 5 - Warrior's Guardian's Oath sits at Bulwark row 5).
- On the map the ability is the row's FREE DIAMOND on the branch spine: `skyymap.FREE_FRAC` 0.7 x the node size (28 px on a class page),
  the tree colour when open, grey when locked, and NO icon (`SkyyTrees/build_skyytrees_0.5.0.py` node_map call: `node_icon` returns None
  for a free code). Free perks of the skill trees use the exact same diamond.
- The panel then says `Free ability of row 2`, `Yours - free with row 2`, `Cost: free with its row`, and the Learn button is greyed.

Why it felt weird: the ability - the most important thing on the page - is the SMALLEST, iconless shape, looks exactly like a skill tree
perk, cannot be clicked to get it (Learn is grey), and you get it by spending points on OTHER nodes, in any branch. Nothing says "this is
an ability" or which key it goes on.

### 1.2 Where abilities and modifiers are equipped today

- Only in the **Loadout** view: the `Talents | Loadout` button pair under the zoom row (`#SkyyTrMLo`, action `tmlo`) swaps the map for the
  0.4.0 Abilities well + Lattice (TM_LOADOUT, unchanged code): click an ability card (`tyca`) -> its modifier tiles show; the Lattice has
  4 rows = Ability 2 / Ability 3 / crouch + Ability 2 / crouch + Ability 3 (p1 p2 a1 a2), each with 2 modifier slots (rebirths add 2).
  Hold an ability, click a row (the two trade places: class:fn:abilDo `hold` / `place`); hold a modifier, click a slot (`mod`,
  `clearMod`). Out of combat only.
- Casting: the real Ability 2 / Ability 3 keys (+ crouch for the alts); Ability 1 = the weapon signature; `/cast 1-4` stays as backup.
- The map panel never mentions the Loadout by name - the free ability's Next line says "equip it under Abilities", a page name that no
  longer exists since 0.5.0.

### 1.3 The either-or alternatives today

- The either-or pair is the two **Ability 1 alts** (A4a / A4b; Priest Sanctuary OR Martyr's Grace). Guardian Spirit (A2-alt) is NOT
  either-or - it is the 4th ability (10-08: 4 abilities, all in the loadout).
- Both A1-alts come free with row 2 of two DIFFERENT branches, so with 5 points you own both. SkyyClasses 0.1.42: when the tree owns both
  A4a and A4b, `Abil.treeOwnsPick` = false and the pick is "free again - one is used at a time".
- **The pick can only be changed on the old SkyyClasses /cast page** (ClassPage > Abilities, the Ability 1 alt card, `abpick` / `abyes`
  -> `Abil.setPick`; it swaps the old alt for the new one in the same key row). Nothing in the Trees page shows or changes it: the
  Loadout only shows whichever alt is picked (default A = Sanctuary), the map shows both as owned diamonds. So a player cannot find it.

### 1.4 The overlapping text (the bug in the screenshot)

The two lines drawn on top of each other are the panel's **Now** label and the **Next** label (`#SkyyTrMNow`, `#SkyyTrMNext`).

- For a free ability the Now text is `"Now: " + TreeClass.doesOf(<ability>)[1]` (TreeV3.detNow -> freeNow) = SkyyClasses' whole "what it
  does" sentence - Shield Bubble's is 245 characters.
- The Now label is `default` style (16 px), wrap on, **fixed height TR_DET_LINE_H = 44 (2 lines)**, no WrapMaxLines. At 424 px wide that
  sentence is **5 lines (~109 px)**, so lines 3-5 spill out of the label and draw over Next ("Free - it unlocks with its row; equip it
  under Abilities") and the top of Cost. Hytale labels do not clip.
- Why no build check caught it: `tv3_fit` measures the upgrades' Now lines, but the free ability's text arrives at run time from
  SkyyClasses (its own DOES check measures 424 px at 13 px <= 4 lines - a different size and box).
- Same risk elsewhere in that panel: State (44), Need (66) and How (107, `max_lines=False`) are wrapped fixed boxes with no line cap.

## 2. Fix 1 - abilities look like abilities (ability icons, a bigger shape, "ABILITY")

1. **New node kind `ability`** for every class row free with an `abil` hook (skill-tree free perks stay diamonds). In `tools/skyymap.py`:
   a rounded-square frame `ABIL_FRAC` = 1.3 x the node size (52 px on a class page; 40 px discs, 44 px capstones), its own pictures
   `<C>Ability` (yours: class-colour frame), `<C>AbilityPicked` (the A1-alt in use: frame + a small gold corner tick), `AbilityOther`
   (the A1-alt not picked: grey frame, the icon still drawn), `AbilityLocked` (grey frame + padlock + the points it needs drawn at run
   time as a small label "5"). The ability still sits ON the branch spine where the row opens it (Skyy 10-16 placement unchanged).
2. **The icon = the ability's own approved art**: `node_icon` returns `SkyyAbility_<Class>_<Id>` (the rune items SkyyClasses ships, e.g.
   `SkyyAbility_Priest_ShieldBubble`; passive Guardian Spirit = `SkyyClasses_Icon_GuardianSpirit`) - the same ids as
   `AbilDefs.ICON` / `ClassArt.abilIcon`. Build time: SkyyTrees takes them from `trees_v3_data.CLASS_LINES` (no new table). Run time: if
   SkyyClasses is missing the ItemIcon shows nothing - fall back to the class icon (`TreeClass.CICON`) exactly like abilIcon does.
3. **A label under every ability node**: `ABILITY` (gold, 13 px bold); the A1-alts read `ALT - IN USE` / `ALT - OR`. Static text per
   node, drawn by `mapDraw` as part of the node (+5 labels per class page; element guard `SUI.assert_map_elements` still applies).
4. `skyymap.check()` must still pass at 100 / 150 / 200 % with the bigger node (discs >= 6 px apart). If a class map fails, shrink to
   48 px before moving anything; the row placement is Skyy's.
5. **The panel for an ability node** (replaces the talent block when the selected node is an ability; same panel, no new page):
   - caption `Priest - Bulwark - Row 2`; a 64 px ability icon + name (tipName, class colour) + a gold tag `ABILITY` (or `ABILITY 1 ALT - OR`);
   - state line: `Yours - free with row 2 (5 points)` (green) / `Opens when you have spent 5 points anywhere in this tree - you have 3` (red);
   - `Unlocks Shield Bubble:` (gold) + the DOES sentence (soft white `#d6e4ee`, 14 px, its own box: 5 lines, WrapMaxLines 5);
   - one dim line: `Lv 7 - 20 Mana - 2 Stamina - 24 s cooldown` (the panel's existing stats line [125 + row]);
   - no Learn button for an ability (nothing to buy): the Primary slot is empty, or PICK for an A1-alt (section 4).
6. **When a row opens** (the Learn click that crosses a gate - already one rebuild): the result line says
   `Row 2 open - new abilities: Shield Bubble, Sanctuary, Martyr's Grace. Click one to set its key.` (no extra packet).

## 3. Fix 2 - equip abilities and modifiers right on the ability node (Loadout stays)

One menu, no new page: the **ability node's panel** does the equipping; the **Loadout** view stays as the all-4-at-once overview with the
same actions (both call the same class:fn:abilDo verbs).

1. **Key buttons** (the panel, under the stats line): caption `Key - click to equip:` and 4 small buttons in a 2 x 2 grid (210 x 32):
   `Ability 2` / `Ability 3` / `Crouch + Ab 2` / `Crouch + Ab 3`. The row the ability sits in = the selected look. Click = class:fn:abilDo
   `place <ability> <row>` (the ability there trades places - today's rule), then ONE rebuild. In combat: refused with SkyyClasses' text
   in the result line, still one rebuild.
2. **Modifier slots** (under the keys): caption `Modifiers - 2 slots:` + the ability's 2 slot tiles (210 x 34: `Power Lv 2` / `Empty`;
   rebirth slots 3-4 show when owned) and the ability's modifiers as small tiles (138 x 30, 3 per line): unlocked = `Power 2` (white),
   locked = `Follow Lv 8` (grey, the ability level that unlocks it). Click a modifier = it goes into the first empty slot (`mod`); both
   full = it is held (cyan outline) and the next slot click places it; click a filled slot with nothing held = `clearMod`. Each click one
   rebuild. One dim line: `Modifiers unlock by ability level - no points.`
3. **The Loadout view** keeps its 4 key rows + modifier slots (unchanged actions) and gains the A1-alt line from section 4 so the pick
   is in both places. Rename the button pair to `Talents | Loadout (keys)` only if it fits 210 px at 17 px bold (check
   `SUI.text_width`); else keep `Loadout`.
4. Texts: every "under Abilities" becomes "on its node or in Loadout"; the Loadout empty hint becomes
   `No abilities yet - Sacred Heal comes free with Devotion row 1.` (per class: the row-1 ability name).
5. Data: `class:fn:abilPanel` already answers the rows, owned flags, slots, modifier names / levels, the pick (o[4]) and the stats line;
   `class:fn:abilMods` the modifier list. SkyyTrees calls them only while an ability node is selected or the Loadout is open (as today).
6. Probe mode (`/tree probe`): view only, as today.

## 4. Fix 3 - the either-or Ability 1 alt: an OR pair with a PICK button

1. **On the map**: the two A1-alt nodes are joined by a dashed gold line along their row's ring with an `OR` pill at its middle (both sit
   on row 2 of different branches; the arc is a build-time picture in `skyymap.base_picture`, a new edge kind `or`, never lit - zero run
   time cost). The picked alt = `<C>AbilityPicked` + `ALT - IN USE`; the other = `AbilityOther` (grey frame, icon visible) + `ALT - OR`.
   Classes with one alt (Assassin) get no OR line. Warrior (rows 2 and 5 of one branch) = the arc becomes a straight dashed spoke; the
   builder checks it never crosses a node (`skyymap.check`).
2. **The panel of either alt** shows `Pick one Ability 1 alt:` + both as side-by-side cards (icon, name, `In use` green / `Pick me`
   yellow) with an `OR` pill between them, then the selected one's `Unlocks ...:` text, then the switch rule in one short paragraph.
   Primary button (the Learn slot): **`Pick Martyr's Grace`** when the selected alt is not in use; when it is in use the button reads
   `In use` greyed. Click = NEW class:fn:abilDo verb `alt <A|B>` -> `Abil.setPick` (the new alt takes the old one's key row; each keeps
   its own level, uses and modifiers - all are stored per ability already). One rebuild.
3. **Before both are owned**: the owned one is the alt automatically (today's `treeOwnsPick` path); the other alt node shows locked with
   `Opens at 20 points - then you pick one` (Warrior) - no Pick button.
4. **Switching rule (default)**: free, any time **out of combat** (skill:fn:combat, as every loadout change), with
   - the newly picked alt **starts on its full cooldown** (stops cast A -> switch -> cast B), and
   - a **10 s wait** between two switches (stops spam).
   No respec needed (respec stays for points). Refusals ("In combat", "Wait 6 s") go to the result line.
5. The old /cast page alt card stays as a backup and calls the same `setPick` with the same rule; its "buy it in your class tree" text
   becomes "pick it on its node in /tree class".

## 5. Fix 4 - the overlapping text

1. **Now (the immediate fix, any panel)**: every wrapped fixed-height label in the map panel gets `max_lines = floor(h / line_height)`:
   State 2, Now 2, Next 2, Need 3, How 6 (was `max_lines=False`). Then a long text is cut at the box edge instead of drawing over the
   next line. Builder: a build check `SUI.assert_wrapped_fits(<markup>)` (kit) failing any `Wrap: true` label with a fixed Height and no
   `WrapMaxLines` in the map panel (kit-wide use later, after a sweep).
2. **Free ability text gets its own room**: with section 2.5 the DOES sentence moves into the ability block's `Unlocks` box (14 px, 5
   lines, ~100 px) and the Now / Next lines are not used for ability nodes, so nothing is cut.
3. **SkyyClasses DOES check** (the writer): add `SUI.text_lines("Unlocks " + name + ": " + does, 424, 14) <= 5` next to the 0.1.30
   checks so a future ability text that would not fit fails the SkyyClasses build.
4. Free PERK nodes (skill trees) keep Now / Next; their texts are build-time and already measured by `tv3_fit` - extend `tv3_fit` to the
   free perk texts (`freeNow`) as well.

## 6. Panel budget (758 px inside the 774 panel, `SUI.fit` must pass)

Shared top: head 64 + 22 + 22, zoom 38, Talents | Loadout 38, separator 10, caption 20 = 214. Shared foot: Respec 50 + result line 44 = 94.

- **Ability node (owned or locked)**: icon / name / tag 68, state 22, Unlocks text 100 (the "Unlocks X:" words start the text), stats 22,
  keys caption 20 + 2 x 2 grid 68, modifiers caption 20 + slots 40 + tiles 2 x 32, hint 18 = 442 -> total 750 (no Primary row).
- **A1-alt not in use**: icon / name / tag 68, state 22, "Pick one" 22 + OR cards 104, Unlocks text 100, switch rule 3 lines 54, Primary
  (Pick) 50 = 420 -> total 728; once picked it shows the owned-ability layout (keys + modifiers), with the OR cards shrunk to one line
  `Ability 1 alt: Sanctuary (in use) OR Martyr's Grace` (22) in place of the hint.

The builder runs `SUI.fit` for each variant; the mock (5x7 bitmap font, wider) shows content and order, not final pixel sizes.

## 7. New Server Setup rows (SkyyClasses, section `abil`, tools/CONFIG-CONTRACT.md)

| Key | Type | Default | Range | Label (<= 40) | Help (<= 100) |
|---|---|---|---|---|---|
| `abil.altSwitch.wait` | int, s | 10 | 0-600 | Ability 1 alt switch wait | Seconds before a player can switch their Ability 1 alt again (0 = no wait). |
| `abil.altSwitch.cooldown` | bool | on | - | New alt starts on cooldown | A freshly picked Ability 1 alt starts on its full cooldown. |

No new SkyyTrees numbers (node sizes are layout, not server settings). Live rows, no migration (no saved value changes; the alt line
`alt=A|B` already exists in `abilities/<pkey>.properties`). The switch time is kept in memory only (resets on restart - fine).

## 8. Questions for Skyy (default in [brackets])

1. Switching the Ability 1 alt: free out of combat, the new one starts on cooldown, 10 s between switches? [yes]
2. The two alts sit in different branches (Priest Devotion + Hallowed Ground). Keep them there joined by an OR line, or move both next
   to each other in one branch? [keep them, OR line - the branches' themes stay]
3. Equip on the ability node AND keep the Loadout overview, or only one place? [both - the node for one ability, Loadout for all 4]
4. Should a newly unlocked ability go into an empty key row by itself? [yes, if a row is empty; never moves one you placed]
5. Ability node look: a bigger rounded square with the ability icon + an ABILITY label (mock)? [yes]

## 9. Build split

| Part | Mod / version | Round |
|---|---|---|
| Section 5.1 (max_lines on the panel labels) + 5.4 + the "under Abilities" text | SkyyTrees **0.5.2** (queued, not started; panel-only, no saved data) | add to 0.5.2's lean part |
| Sections 2, 3, 4.1-4.3, 5.2, 6 (ability node kind, icons, labels, OR arc, ability panel, key + modifier buttons, PICK) + kit (`skyymap` ability kind + `or` edge, `assert_wrapped_fits`) | SkyyTrees **0.5.4** (after 0.5.3's class-tree modifier rework - both rewrite the class panel; 0.5.4 derives from 0.5.3) + kit 1.10 | full round (several mods, loadout state, UI) |
| Section 4.2 verb `abilDo alt`, 4.4 rule + section 7 rows, 4.5 /cast text, 5.3 DOES check, panel field o[130] = seconds until the next switch | SkyyClasses **0.1.47** (SET pin 0.1.46) | same full round as Trees 0.5.4 |

Not 0.5.1 (zoomfix is running, kit 1.9 zoom only) and not 0.5.3 (its migration / refund round should stay separate). Rollback:
Trees 0.5.4 needs Classes >= 0.1.47 for PICK (an older SkyyClasses refuses the unknown verb -> the button says "Update SkyyClasses");
add the pair to `tools/deploy_set.py` checks.

## 10. For the local session (UNVERIFIED)

- UNVERIFIED in game: that a 52 px ability node + label passes `skyymap.check` on all 8 class maps at 150 / 200 % (run it first).
- UNVERIFIED: Hytale `WrapMaxLines` cuts a fixed-height label cleanly (the kit uses it on vanilla styles; no probe of a cut line yet).
- UNVERIFIED: an ItemIcon of a Quality Debug / HideFromSearch rune item draws on a custom page (the Lattice already draws
  `ap[120..124]` rune icons, so very likely yes).
- UNVERIFIED: whether a newly unlocked ability already auto-lands in an empty key row (`AbilStore.slots` defaults) - read before Q4.
- The OR arc needs both alts on the same ring (true for 7 classes, Warrior differs: rows 2 and 5 of Bulwark) - check the generated map.
- The screenshot's overlap is explained from the code (5 wrapped lines in a 44 px label); confirm by opening Priest > Shield Bubble on
  0.5.2.
- Element count per class page: +5 labels, +2 OR pictures - well under 1,000.
