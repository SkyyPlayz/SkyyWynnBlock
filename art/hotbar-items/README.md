# Hotbar ability item icons - APPROVED (37 icons, 64 x 64)

ART-RESUME queue item #8. **Status: APPROVED + committed** (the hotbar commit after 13a4372). Skyy, word for word (2026-10-08):
"Start the hotbar icons" / then "Yes, the hotbar icons look good, commit them" (draft v1 approved as drawn, all defaults kept). Not wired in, not seen in game (SkyyClasses phase I2, the hotbar items, is not built yet).

Review sheet as approved: `sheet.png` (mock hotbar at the top, then every item at 4x / 64 px / 32 px; kept as Skyy reviewed it).

## 1. What the spec says (`research/cloud/Ability-Input-Design.md` section 2)

- A hotbar ability item is a **soulbound hotbar item that casts one thing when you SELECT its slot**, then puts you straight back on
  your weapon. The cooldown shows as the item's **durability bar**. One item per ability; players get them from the Abilities page
  ("Put on hotbar"); they cannot go in chests / trades / the Bazaar / AH.
- Two kinds: **mirror** items (the same ability as its key - "Meteor" item = the Meteor on Ability 2) and **utility** items with no
  key of their own: **Loadout** (next saved rune loadout, later), **Hints** (replay the class tutorial), later pet / emote calls.
- Design question 5 default: the two equipped mirrors + utility items. `research/cloud/Class-Ability-Shapes.md` question 10 default: a mirror item
  casts the WALKING shape only.
- Keys since then (`docs/answered/classes.md` line 153): 4 abilities, 2 primary on Ability 2 / 3, 2 alt on crouch + Ability 2 / 3.
  `OPEN-QUESTIONS.md` still asks "hotbar ability items still wanted as a backup way to cast? [no for now - keys only]" - Skyy's
  "Start the hotbar icons" is taken as yes for the art; the question stays for the main session.
- No mod code, item ids or icon paths exist for these items yet - the ids and paths below are PROPOSED.

## 2. Files

| File | What |
|---|---|
| `Common/Icons/ItemsGenerated/SkyyClasses_AbilityItem_<Class>_<Ability>.png` | 35 mirror items, one per class ability (Mage ... Archer, same names as `art/ability-icons/`) |
| `Common/Icons/ItemsGenerated/SkyyClasses_AbilityItem_Loadout.png`, `..._Hints.png` | 2 utility items |
| `sheet.png` | review sheet: mock hotbar strip + every item at 4x / 64 / 32 px |
| `manifest.json` | every file: path, bytes, sha256, proposed item id, kind, class, the ability icon it mirrors, slot, what it shows |
| `README.md` | this file |

Path: the same `Common/Icons/ItemsGenerated/<ItemId>.png` layout as the other item icons in this repo (Accessory Bag, Dark Leather).

## 3. The look (and why)

- **Mirror item = the ability's own glyph on a square class TABLET.** The glyph is painted by the same painter as the approved round
  ability icon (so the item and the key ability are obviously the same thing), at 95% size, on a square stone tablet with chamfered
  corners, a bevelled border in the class rim colour, four small steel corner studs, the class field colour on the face, and a
  visible 2.5 px THICKNESS to the lower right (a blocky slab you could pick up). Transparent around it, like an item.
- Why it does not get mixed up with the round HUD icon: square slab vs round button, thickness, no dark outer ring. Checked: every
  mirror item differs from its own round icon by 27.7 or more at 32 px (mean abs diff; two different round icons of one class differ
  by about 13).
- **Utility items**: a neutral STEEL rim with GOLD studs on a dark slate face - no class uses steel, so a utility item never looks
  like one class's item.
  - **Loadout**: a violet faceted rune stone with a carved rune, two gold arrows chasing each other round it (swap to the next).
  - **Hints**: an open book (wine leather cover, warm pages with text lines) with a glowing gold question mark rising off it.
- The game draws the cooldown (durability) bar across the bottom of the slot - the bottom of every tablet is just border, so the
  bar never hides the glyph.
- Same rules as the ability icons: hard alpha, no pure `#000` / `#fff`, top-left light, hue-shifted ramps, ORIGINAL pixels (no vanilla
  file, other mod or reference picture used).

## 4. Defaults used (Skyy can change)

| Choice | Default used |
|---|---|
| Which mirror items | all 35 class abilities drawn (the game hands out only the ones a player puts on the hotbar) |
| Mirror look | the approved ability glyph on a square class tablet (not a new drawing per ability) |
| Utility items | Loadout + Hints (pet / emote calls later, when those exist) |
| Utility colours | steel rim, gold studs, slate face `#2c3344` -> `#0d1018` |
| Tablet | front 4.5..55.5 x 4.0..55.0 px, chamfer 6, depth 2.5 px lower right, border 2.8 px, glyph at 95% |
| Ids / paths | `SkyyClasses_AbilityItem_<Class>_<Ability>` / `SkyyClasses_AbilityItem_<Utility>` in `Common/Icons/ItemsGenerated/` |
| Model | icon only (the item is never really held - select = cast + instant return) |

## 5. 32 px readability

First try: glyph at 80% on a smaller tablet - two items of one class were too alike at 32 px (Warrior Rallying Guard vs Bulwark
Stance 7.9, want > 10). Now: a bigger tablet face (thinner border, less depth) and the glyph at 95%. Closest pair 11.3 (Rallying
Guard vs Bulwark Stance); every item vs its own round icon >= 27.7. `validate_hotbar_items.py`: all 37 PASS.

## 6. How to rebuild

```
python3 tools/art/make_hotbar_items.py      # the 37 PNGs (--only Meteor,Loadout to redo some)
python3 tools/art/make_hotbar_sheet.py      # sheet.png + manifest.json
python3 tools/art/validate_hotbar_items.py  # size, RGBA, hard alpha, no #000/#fff, distinct, distinct from the round icon, deterministic
```
The glyphs come from `make_ability_icons.py` (the approved painters) - change an ability icon there and its item follows. Nothing in
`art/ability-icons/` is written by these scripts.

## 7. UNVERIFIED (for the main session)

1. Item ids and the icon path are proposals - nothing in SkyyClasses defines them yet (phase I2).
2. Whether a Hytale item can ship with only an icon (no held / dropped model) - if it needs a model, a flat tablet model can follow.
3. How the hotbar draws a 64 px item icon (scale, filtering) and where the durability bar sits - the sheet's hotbar is a mock.
4. Not seen in game.

## 8. Open questions for Skyy (answered - all defaults kept: "Yes, the hotbar icons look good, commit them")

| # | Question | Default |
|---|---|---|
| 1 | Mirror items show the SAME glyph as the ability icon, on a square class tablet - OK, or a different object per ability (scroll, rune, charm)? | **[same glyph on a tablet - one look to learn, clearly "the Meteor item"]** |
| 2 | Draw items for all 35 abilities, or only some? | **[all 35 - the game gives out only what a player puts on the hotbar]** |
| 3 | Utility items: Loadout + Hints now? (pet / emote calls later) | **[yes, these two]** |
| 4 | Utility rim: neutral steel (no class colour) - OK? | **[steel rim, gold studs]** |
| 5 | Item id / file name pattern `SkyyClasses_AbilityItem_<Class>_<Ability>.png`? | **[yes - the main session may rename]** |
| 6 | Hints uses a "?" sign (a symbol, not text) - OK? | **[yes]** |
| 7 | Separate "on cooldown" / locked icon versions? | **[no - the durability bar shows the cooldown]** |
| 8 | Still wanted at all? (`OPEN-QUESTIONS.md`: "[no for now - keys only]") | **[yes - Skyy: "Start the hotbar icons"; wiring stays the main session's call]** |
