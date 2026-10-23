# Pet tooltip layout (design, 2026-10-23)

Design only - no code changed. Builder: SkyyPets next version (0.4.14+), Lean round (one mod, no saved data). Picture of the three
examples below: `research/pet-tooltip-preview.png` (made with a stdlib script; the game's font and tooltip frame look different, the
colours and line order are what count).

## 1. Decisions followed

- Skyy 2026-10-23 (screenshot of "Common Rat - Lv 1"): "can you make the pets flavor text more clear. its hard to read and understand, i want it color coded, and spaced out clearly with the pet type at the top. so if its a mount, or combat, you can see that immediately"
- Skyy 2026-10-18 (Style Guide section 15, standing rule): "make all the flavor text use a slightly bigger font, and color code everything. so you can see what stats it gives at a glance" -> ONE colour code, name / level first, what it GIVES next, minor info last. Pets was named as the first user.
- PROJECT-RULES 4 "Tier tags": tier / rarity comes first on the name line (pets have a rarity, not a tier tag; the rarity word + rarity colour is that first item).
- Menu Pattern / one look: the kit colours only (tools/skyyui.py `COLOR`, `QUALITY`, `RARITY`), no new styling.

## 2. Where it is built today

`SkyyPets/build_skyypets_0.4.13.py` (generated from the patch chain `tools/pets_*_patch.py`; the NEW version is a new
`tools/pets_0_4_14_patch.py` that reads 0.4.13 - never edit the generated script):

| What | Where (0.4.13 line) |
|---|---|
| The tooltip text, one `StringBuilder` | `PetPageC.tip(PetRec r, String id, int mode)` ~12137-12166 (written by `P.rep` / `M(PAGEC ...)`; older versions: tools/pets_0_4_0_patch.py 1590-1607, pets_0_4_10 / 0_4_11 insert the element + dragon lines) |
| Set as the grid cell's hover text | `PetPageC.cell()` ~12168: `g.setName(petName + " - Lv n")`, `g.setDescription(tip(...))` |
| Click hint (last line, `+`/`-` prefix = can / cannot) | `PetPageC.hint()` ~12117 |
| Type words today ("Mount + Fighter", "Combat pet", "Gathering pet", "Pet") | `PetKind.roleWords(roles)` ~2311, via `PetsCfg.roleText(kind)` ~3570 |
| Role table (kind -> tokens gathering / combat / pet / fighter / mount) | `ROLES` ~1165-1184; Ram = `fighter,mount` |
| Buff text "+0.2 Max Stamina, +0.05 Speed %" (one comma line) | `PetBuff.petText(r, id, pct)` ~5826, `PetBuff.text(double[])`, `buffsAt()` ~12106 (max-level line) |
| Dragon lines (stage, shows-only-in-summon-slot, DOWN) | `PetDragon.card(r, id)` ~7332, + `PetFight.cardLine` ~7263 (fights), `PetRide.cardLine(kind, lv)` ~4195 (ride) |
| Fuse / rebirth wording | `PetOps.fuseInfo` ~9098, `PetOps.rebInfo` ~9228 |
| Rarity colours | `PetPageC.rcol(rar)` / `RCOL` = `RARITY_COLORS` ~1008 (vanilla quality colours + SkyyGear Mythic) |
| Footer colours | `TIP_FOOT = "#ffff55"` ~11708 (hint) and `COL["disabled"]` `#797b7c` (cannot) |

Same text is reused by the Hatchery egg-slot description (`g.setDescription("You own n ... Fusing: ...")` ~11581, two places) - give that
one the same section style in the same round (type line = the egg's pet kind type).

## 3. Pet types (what the top line says)

Computed from the role tokens of the kind (`PetsCfg.roles(kind)`), NOT from the skill, in this order:

| Roles | Top line | Colour of the type word |
|---|---|---|
| fighter + mount (Ram; a dragon that can ride, Lv >= ride level) | `FIGHTER + MOUNT` | FIGHTER red `#e8554a`, `+` dim, MOUNT cyan `#4fc3d9` |
| fighter (Wolf, Skeleton, Tusker, VoidCrawler, dragons below ride level) | `FIGHTER - <Skill>` | red `#e8554a` |
| mount (Horse, Camel) | `MOUNT - <Skill>` | cyan `#4fc3d9` |
| anything else = only boosts your stats (gathering kinds, combat-boost kinds like Boar / Hawk / Fox, plain critters like Rat) | `BONUS - <Skill>` | pale blue `#b7cedd` (kit `value`) |

- `<Skill>` (Combat / Farming / Mining / Foraging / Fishing / Exploration / Cooking / Alchemy ...) is the kind's skill, soft white `#d6e4ee`,
  separated by a dim `-`. This keeps Skyy's filter words (Bonus / Fighters / Mounts): "combat" in Skyy's sentence = a pet that FIGHTS.
  A combat-STAT pet that does not fight (Boar) is BONUS - Combat, so nobody expects it to bite.
- A dragon below the ride level shows `FIGHTER - Combat` and a dim RIDING line "Ride it from Lv 10"; at ride level it flips to
  `FIGHTER + MOUNT` and the RIDING section turns green ("unlocked"). Dragons are Fighter + Mount from Lv 10 (Skyy 2026-10-18, default ride level `DRAGON_RIDE_LV`).
- New type colours `#e8554a` / `#4fc3d9` are NEW tokens: add them to `tools/skyyui.py` (`COLOR["petFighter"]`, `COLOR["petMount"]`) and a line to
  Style Guide section 15, plus the test. Everything else below is already in section 15 / the kit. (Skyy to confirm the two colours - default stands.)
- Admin switched-off kind or unknown kind: top line `OFF` / `UNKNOWN` in red `#ff7a7a`, then the existing "gives nothing" line at the top, not buried at the bottom.

## 4. Colour code (all from Style Guide section 15 / kit)

| Use | Colour |
|---|---|
| Type word (top line) | see section 3, big |
| Pet name | rarity colour (`rcol`): Common `#c9d2dd`, Uncommon `#3e9049`, Rare `#2770b7`, Epic `#8b339e`, Legendary `#bb8a2c`, Mythic `#CC66CC` |
| Level, XP, rebirths, fuse counts (progress numbers) | gold `#e8c25a` |
| Section headers (BUFFS NOW, FIGHTING ...) | `#9aacbc` (kit `section`), ALL CAPS |
| Stat NAME | soft white `#d6e4ee` |
| Stat VALUE (+ buffs) | green `#7ee08a`; red `#ff7a7a` if a value ever costs (negative) |
| Element word | Fire `#ff6a3d`, Water `#4fa8ff`, Earth `#5dbb4a`, Thunder `#ffd84d`, Air `#c8f5ee` (already in `tip()`) |
| Unlocked / ready | `#39f493` (kit `success`) |
| Locked / cannot / dragon DOWN | `#ff7a7a` (`#797b7c` grey when it is just not available) |
| Minor info (rarity bonus, ids, "None yet", owned since) | dim `#7f93a6` |
| Click hint | yellow `#ffcc00` (section 15 "actions"); cannot = `#797b7c` as today. NOTE: today's code uses `#ffff55` (`TIP_FOOT`); section 15 says `#ffcc00`. Use `#ffcc00` and change `TIP_FOOT`/`TIP_FOOT1` (also used by the other tabs) in the same patch so every pet tooltip matches. |

## 5. Line-by-line layout (every section is followed by one empty line `\n\n`)

Order always: TYPE / name / (element + stage for dragons) / BUFFS NOW / FIGHTING / RIDING / AT LV max / SUMMON SLOT / PROGRESS / ABILITIES / click / minor.
A section that does not apply is left out entirely (no "none" noise, except Abilities which stays as "None yet" until pets have any).

### Example A - Common Rat, Lv 1 (BONUS, Exploration)

| # | Text | Colours |
|---|---|---|
| 1 | `BONUS - Exploration` | BONUS `#b7cedd` big, `-` `#7f93a6`, skill `#d6e4ee` |
| 2 | `Common Rat  Lv 1  rarity bonus x1` | name `#c9d2dd`, `Lv 1` `#e8c25a`, rest `#7f93a6` |
| 3 | (blank) | |
| 4 | `BUFFS NOW` | `#9aacbc` |
| 5 | `+0.2 Max Stamina` | value `#7ee08a`, name `#d6e4ee` |
| 6 | `+0.05 Speed %` | same |
| 7 | (blank) | |
| 8 | `AT LV 50 (MAX FOR NOW)` | `#9aacbc` (shown only while Lv < cap) |
| 9-10 | `+10 Max Stamina`, `+2.5 Speed %` | green / soft white |
| 11 | (blank) | |
| 12 | `SUMMON SLOT` | `#9aacbc` |
| 13 | `Not for summoning (Fighters and Mounts only)` | `#7f93a6` (Fighter / Mount: the line becomes the buffs at 50 %, see B) |
| 14 | (blank) | |
| 15 | `PROGRESS` | `#9aacbc` |
| 16 | `Level 1 / 50  (up to 100 with rebirths)` | `Level` soft white, `1 / 50` gold, bracket dim |
| 17 | `XP 0 / 120 to Lv 2` | gold numbers; at cap: `XP max level - ready to rebirth` (gold) |
| 18 | `Levels from Exploration (50% / other 5%)` | soft white + dim bracket |
| 19 | `Rebirths 0 / 5  next at Lv 50` | gold + dim; ready: `ready to rebirth` green |
| 20 | `Fusing 1 / 4 Common Rats` | soft white, gold `1 / 4`; ready: `ready: 4 -> 1 Uncommon` green |
| 21 | (blank) | |
| 22 | `ABILITIES` / `None yet` | header `#9aacbc`, text `#7f93a6` |
| 23 | (blank) | |
| 24 | `Click: put it in your pet slot` | `#ffcc00` |
| 25 | `Owned 2026-10-21 - id a1b2c3` | `#7f93a6` (kept for bug reports; slot line "In your pet slot (full buffs)" goes before it, soft white, when slotted) |

### Example B - Rare Wolf, Lv 24 (FIGHTER, Combat)

1. `FIGHTER - Combat` (red big) / `Rare Wolf  Lv 24  rarity bonus x1.25` (name `#2770b7`).
2. BUFFS NOW (PET SLOT): `+4.8 Strength`, `+2.4 Crit Damage %` (the header carries "(PET SLOT)" for any summonable kind so the two slots are clear).
3. FIGHTING (SUMMON SLOT): `Fights beside you, buffs at 50%` (soft white, `50%` green) then the 50 % stat lines in green / white.
   For a non-dragon fighter there is no bite-% data in the card today (`PetFight.cardLine` is dragon-only) - the line shows just the summon
   buffs; do not invent a number. Not summonable (slot locked) -> `Summon slot is locked` red-grey `#797b7c`.
4. AT LV 50, PROGRESS (Level / XP / "Levels from Combat" / Rebirths / Fusing `2 / 4 Rare Wolves`), ABILITIES, click, minor as A.
(Numbers in the preview are illustrative, not the real MELEE stat table.)

### Example C - Rare Fire Dragon, Lv 12 (FIGHTER + MOUNT)

1. `FIGHTER + MOUNT` (red + dim + cyan, big) / `Rare Fire Dragon  Lv 12  rarity bonus x1.25`.
2. `Fire  - its damage counts with Fire weapons` (`Fire` in `#ff6a3d`, rest dim) - only when `elemOf(kind)` is set.
3. `Biteling, size x1.2  - Flyling at Lv 30` (soft white + dim) = today's `PetDragon.card` first line, cut to the stage; `Still growing` when it applies. DOWN: red line `Down - back in 12 s` right under it.
4. BUFFS NOW (PET SLOT): lines as B.
5. FIGHTING (SUMMON SLOT): `Bites for 25.5% of your damage` / `Health 112% of yours` (values green) / `Shows only in the summon slot` (dim). From `PetFight.cardLine` pieces (`share`, `hpFrac`) - make it return two plain lines instead of one sentence. Off on the server: `Dragon fighting is off on this server.` dim.
6. RIDING: `Ride it from Lv 10  unlocked` (gold `10`, green word; below ride level the word is `locked` red and the lines read `Ride it from Lv 10`), `F on it in the summon slot`, `Jump to take off and fly` (or `Jump to glide`). Off: `Riding is off on this server.` dim. From `PetRide.cardLine` - split into lines.
7. AT LV 50, PROGRESS (`Fusing dragons cannot be fused` dim), ABILITIES, click, minor as A. "One dragon per profile" goes into the dim minor block as `One dragon per profile.`

## 6. Rules per pet type

- BONUS: no FIGHTING / RIDING. SUMMON SLOT section = one dim line "Not for summoning (Fighters and Mounts only)". Gathering kinds also show `Levels from <Skill>` in PROGRESS.
- FIGHTER: BUFFS NOW (PET SLOT) + FIGHTING (SUMMON SLOT, summon-slot buffs at `SLOT2_PCT`%). Element line when set.
- MOUNT (Horse, Camel): RIDING section replaces FIGHTING: "Ride it: F on it in the summon slot" (use the mount-pet text that exists in `PetRide`/mount phase 5 - the builder reads it, not invented here), size note if `pets.mount.scale` != 1.
- FIGHTER + MOUNT (Ram): both sections: FIGHTING says "Fights when you are not riding it" (Skyy 2026-10-08: "a pet can be both a Mount and a fighter. so it fights when not ridden"), then RIDING.
- Dragon: as C; one dragon per profile; stage line; no fusing; element line.
- Switched off by the server / unknown kind: first line OFF / UNKNOWN (red), message under it, no buff sections.
- Fuse / Rebirth click modes: only the last hint line and the PROGRESS line of that mode change (hint colours as section 4); the layout does not.
- Every kind: no line longer than ~45 characters (the client tooltip wraps at its own width, section 7); numbers lead (`+0.2 Max Stamina`), words are plain (Strength, not `str`).

## 7. What the markup can / cannot do

PROVEN (in game, same grid-slot description we use today):
- `<color is="#rrggbb">text</color>` spans, one or more per line; `\n` line breaks; `\n\n` blank line (the current click hint uses it).
- Only the client's own tooltip size/frame (item quality frame); ASCII / Latin-1 text (no star, arrow, heart glyphs - Nunito lacks them).

CANNOT (so the design does not use it):
- Bigger font. The ItemGridSlot description font size is the client's; Style Guide section 15 says the same ("Item lang text: keep the client's
  size"). The "big" type line in the preview is NOT possible in this tooltip: colour + ALL CAPS + position carry it. Section headers also ALL CAPS.
- Per-line alignment, tables, icons, dividers, progress bars.
- A custom Pets tooltip (a real `Group` hover with `FontSize` 14-16, `tooltip_panel` in the kit) would allow size, but the pet cell is an
  `ItemGridSlot`, whose tooltip is the client's. That would be a bigger change (own hover panel, drawn on HoverEvent = never periodic page updates, HANDOFF section 2) - not proposed here.

UNVERIFIED (test in game, 5-line probe, before relying on it):
1. `<b>` / `<i>` inside the description (they exist in `client.lang` strings; not proven for ItemGridSlot) - design does not need them; if bold works, bold the type word and stat values.
2. Several `<color>` spans on one line (stat value + name): Item lang text does it; the grid-slot description has only been proven with one span per line (footer) and the rarity span + text on the first line (current tip line 1, so two segments work). Fallback if broken: whole line one colour (value colour).
3. The tooltip's max width / wrap point (client `@DefaultTextTooltipStyle` = 400 px max width, 24 px padding per the kit `TOOLTIP_MAX_W`): the longest line (the Dragon element line, ~45 chars) may wrap - shorten to `Fire - counts with Fire weapons` if it does.
4. Leading spaces / double spaces (`Lv 1  rarity bonus`) may be collapsed; use ` - ` if so.
5. A tooltip with ~30 lines (Dragon at Lv 12) may be taller than the 1080 screen at high GUI scale; fallback: drop AT LV 50 for dragons or merge ABILITIES into one line.
6. `#ffcc00` vs `#ffff55` for the footer: only a colour swap, no risk.

## 8. Builder checklist

1. New patch `tools/pets_0_4_14_patch.py`: replace `tip()` with the section layout (helpers `sec(title)`, `stat(value, name)`, `col(hex, text)`; hex from kit constants emitted at build time, as `TIP_FOOT` already is).
2. `PetBuff`: add `lines(double[] t)` (one `+value name` per buff, coloured) beside `petText` - keep `petText` (other callers: Hatchery, chat).
3. `PetKind.roleWords` -> `PetKind.typeLine(roles, skill, canRide)` returning the coloured two-part line; keep `roleWords` for old callers (filters, admin).
4. Split `PetFight.cardLine` / `PetRide.cardLine` / `PetDragon.card` into plain lines (no embedded sentences with `\n`).
5. Add the two type colours to the kit + guide section 15 + `tools/skyyui_test.py`; `TIP_FOOT` -> `#ffcc00`.
6. One-line-per-fact rule: if `tip` output grows a line > 45 chars, shorten wording, not the colours.
7. Test in game: Common Rat (A), Wolf (B), Fire Dragon below / at Lv 10 (C), Ram, Horse, a Boar (BONUS - Combat), a pet in the summon slot, Fuse / Rebirth modes, a switched-off kind; screenshot to Skyy.
