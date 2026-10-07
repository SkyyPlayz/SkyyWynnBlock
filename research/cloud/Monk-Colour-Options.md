# Monk class colour options

LOCKED: Saffron #f08a30 (Skyy, 2026-10-06 - docs/answered/gear.md line 87). The options below are history.

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `CLOUD-RESUME.md` ("Monk class colour + emblem check"),
`research/cloud/class-art/README.md`, `research/cloud/class-art/make_emblems.py` (read-only, used to draw the emblems),
`SkyyProfiles/build_skyyprofiles_0.1.2.py` + `0.1.5.py` (`ClassDefs.COLORS`), `tools/skills_0_4_4_patch.py` (`SkillDefs.COLORS`),
`research/classes/Monk.md`, `docs/answered/classes.md`, `research/Vanilla-UI-Style-Guide.md` (section 5 colours).
Picture: `research/cloud/class-art/monk-colour-options.png` (7 swatches per candidate, plus protan / deutan / tritan rows, plus the Monk emblem at 128).

## 1. Where things stand

| Fact | Source |
|---|---|
| The other 6 class colours are verified in the build script: Warrior `#e0b060`, Berserker `#d9443f`, Archer `#8fd67a`, Assassin `#b58cff`, Mage `#7fb0e0`, Priest `#f2e6a0` | `SkyyProfiles/build_skyyprofiles_0.1.2.py` line ~195-214 (unchanged in 0.1.5) |
| The Monk has no colour of its own. The slot still holds the old Shaman colour `#ff7a5c` (Skyy swapped Shaman for Monk, 2026-10-03) | `SkyyProfiles/build_skyyprofiles_0.1.5.py` line 373 |
| No colour or theme hint from Skyy for the Monk (grep of `docs/answered/classes.md` and `research/classes/Monk.md`: none). Only the feel: "graceful, fast, skips across the battlefield like a stone on water", Paths Wind Dancer / Iron Fist / Serene | `research/classes/Monk.md` |
| The class colour is used in more than the Profiles card: the same hex is the Monk's **skill colour** (`SkillDefs.CLASS_ROWS`) and a lint list of allowed data colours (`UI_DATA_COLORS`) | `tools/skills_0_4_4_patch.py`, `SkyyProfiles/build_skyyprofiles_0.1.5.py` line 380 |
| Hue gaps left: the 6 colours sit at red, gold, cream, green, blue, violet. Free: orange, teal / cyan, pink, white | by hue |

## 2. Candidates and numbers

How measured (python, no libraries): distance = CIEDE2000 (about 2 = barely visible, 5-10 = clearly different, 15+ = never confused).
Contrast = WCAG ratio of the colour as text on the background (4.5 = normal text, 3 = large text / icons).
Dark background = the vanilla row colour `#101925`; slate = the emblem rim `#34465a` (a guess, UNVERIFIED). The real panel texture
(`Common/ContainerPatch.png`) is not readable in the cloud. White = a white label on the colour (a badge). Colour-blind = Machado 2009 matrices,
severity 1.0, linear RGB.

| | Candidate | Hex | Nearest of the 6 (normal) | Min dist normal | Min dist protan | deutan | tritan | On dark | On slate | White text |
|---|---|---|---|---|---|---|---|---|---|---|
| A | Coral (proposal) | `#ff7a5c` | Berserker | 14.8 | 11.6 | **4.5** | 11.9 | 6.90 | 3.77 | 2.56 |
| B | Saffron orange | `#f08a30` | Warrior | 14.4 | 9.1 | 6.1 | 11.0 | 7.06 | 3.86 | 2.51 |
| C | Jade teal | `#38c9a8` | Archer | 16.8 | 14.8 | 18.8 | **8.7** | 8.49 | 4.65 | 2.08 |
| D | Rose pink | `#ff7fb5` | Assassin | **22.5** | **8.6** | 18.8 | 11.8 | 7.54 | 4.13 | 2.35 |
| E | Silver-white | `#d4dce6` | Mage | 17.9 | 16.4 | 18.9 | 16.5 | 12.78 | 7.00 | 1.38 |
| F | Sky cyan | `#4fd8e8` | Mage | 18.5 | 10.6 | 7.5 | 10.4 | 10.37 | 5.68 | 1.70 |

Baseline, the 6 existing colours among themselves: min distance 15.5 normal (Warrior / Priest), 6.1 protan and 4.6 deutan (Warrior / Archer),
10.4 tritan (Archer / Mage). So a new colour that reaches about 5+ in every colour-blind row is no worse than today. For reference the six
on the dark row: Warrior 8.9, Berserker 4.1 (the weakest), Archer 10.2, Assassin 6.9, Mage 7.7, Priest 14.0.

### Distance to the skill colours (the Monk's skill row uses the same hex)

| | Closest skill colour | Distance | Closest chat colour | Distance |
|---|---|---|---|---|
| A Coral | Combat `#ff8a7a` | **5.7** | `#ff9d6b` | 10.3 |
| B Saffron | Cooking `#ffb070` | 9.9 (Exploration `#e0a040` 10.2) | `#ff9d6b` | 9.4 |
| C Jade | Alchemy `#7fe0d0` | 9.3 | `#a8e8c0` | 13.0 |
| D Rose | Combat `#ff8a7a` | 19.4 | `#ff9d6b` | 30.3 |
| E Silver | Smithing `#c0c8d0` | **4.9** | `#9fd8ff` | 13.1 |
| F Cyan | Alchemy `#7fe0d0` | 11.6 | `#a0f0e0` | 13.5 |

## 3. Reading it

1. **A Coral (the proposal) is the weakest.** 14.8 from Berserker is just under the 15.5 the existing set already manages, but the real problems are
   deuteranopia (4.5 to Warrior, it collapses into the same mustard) and the **Combat skill colour (5.7)**, which sits on the same Skills page.
   On the emblem the brown Bo staff also disappears on a coral field.
2. **B Saffron** is the classic monk-robe colour but it crowds the gold family (Warrior 14.4, Cooking and Exploration about 10) and goes mustard for protan / deutan.
3. **C Jade teal** is the only candidate in a free hue AND with strong protan / deutan (14.8 / 18.8). Its weak row is tritan (8.7 to Mage, still near
   the existing 10.4). It fits the theme (flowing water, "stone on water", jade and bamboo; the Bo staff is bamboo). Weak point: Alchemy `#7fe0d0` at 9.3 (not a class, and Alchemy is lighter).
4. **D Rose pink** is the most distinct for normal sight (22.5, and 19+ from every skill colour) but goes grey-blue for protan (8.6 to Mage). Less "monk",
   more "lotus / cherry blossom" - a fun, bold pick, and the only one nobody will mistake.
5. **E Silver-white** has the best colour-blind rows but is nearly a non-colour: 1.38 on white, clashes with Smithing (4.9), and reads as "locked / grey" next to the greyed cards.
6. **F Sky cyan** is too close to Mage in a family sense (18.5 normal, but 7.5 deutan) and to Alchemy.

## 4. Recommendation

**C Jade teal `#38c9a8`.** Best worst-case over all three colour-blind views (8.7) with a free hue, good contrast on the dark background (8.49, passes text),
and a theme fit. Runner-up **D Rose pink `#ff7fb5`** if Skyy wants the boldest standout. Drop A.

- White text on any of the colours fails (2.1 to 2.6), as it already does for 5 of the 6 existing classes (only Berserker passes at 4.3). Rule: class
  colour is used as TEXT on the dark panel, never as a badge background with white text; use `#101925` text on a coloured badge (8.49 for jade).
- Emblem with C: the field is the class colour darkened, so jade gives a deep teal shield with the gold trim and brown Bo staff clearly readable (see the PNG, row C). No change to the emblem code beyond one hex in `CLASSES`.
- Not a mod choice but worth knowing: the existing pair Warrior / Archer is already 4.6 apart for deuteranopia. A fix would be an Archer nudge, not a Monk one.

## 5. What changing it touches (for the local session)

| Where | Change |
|---|---|
| `ClassDefs.COLORS` (SkyyProfiles) + `UI_DATA_COLORS` (the same file, line 380) | the Monk (ex Shaman) entry |
| `SkillDefs.CLASS_ROWS` colour (SkySkills) and its lint list `UI_PAGE_COLORS` | the same hex, asserted equal to `SkillDefs.COLORS` |
| `research/cloud/class-art/make_emblems.py` `CLASSES` + README table | one hex (cloud-side) |
| Every colour already placed in saved data? | none: the colour is code, not saved |

## For the local session (UNVERIFIED)

1. The real vanilla panel colour behind pages (`Common/ContainerPatch.png`, `Assets.zip`); the dark column above uses the row colour `#101925` and the slate guess `#34465a`.
2. Whether the Monk's slot in `SkillDefs` shares the class hex (as for the other six) or a separate value; if separate, only the class card changes.
3. Check the new hex in game on the Profiles class card, the Skills page, chat and the Stats page, next to Alchemy (jade case).
4. The colour-blind rows are a simulation (Machado matrices), not a person's test. A single test by a colour-blind player would settle the Warrior / Archer pair.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Monk class colour | [C Jade teal `#38c9a8`; runner-up D Rose pink `#ff7fb5`; A Coral dropped] |
| 2 | Should I also nudge Archer so Warrior / Archer is readable for deuteranopia (not the Monk's fault)? | [no, leave as is] |
| 3 | Class colour on a badge: dark text instead of white (white fails contrast on 5 of the 6 existing colours) | [yes, dark text] |
