# Class ability icons - Mage + Priest (10 icons, 64 x 64)

ART-RESUME NEXT ITEM 5. Candidate for Skyy's review - **not committed, not wired in, not seen in game.**
Original pixels drawn from code (Python + numpy + Pillow). No vanilla Hytale file, other mod or reference picture was read,
copied, traced or recoloured.

**Start here:** `sheet.png` (both classes, every icon at 4x, 2x, actual 64 px and 32 px, plus a dark HUD strip).

## 1. Files

| File | What |
|---|---|
| `Common/Icons/Abilities/Mage/Meteor.png` ... `ArcaneBeam.png` | 5 Mage icons, 64 x 64 RGBA |
| `Common/Icons/Abilities/Priest/SacredHeal.png` ... `MartyrsGrace.png` | 5 Priest icons, 64 x 64 RGBA |
| `sheet.png` | review sheet (big labels, plain page, class colour swatch per group) |
| `manifest.json` | every file: path, bytes, sha256, size, class, slot, ability text, what the icon shows, colour ramps |
| `README.md` | this file |

Every icon: round, alpha 0 outside the circle and 255 inside (hard alpha only, so straight vs premultiplied alpha does not
matter). No pure `#000000` / `#ffffff` pixel. File names have no spaces (`ManaBarrier.png`, `MartyrsGrace.png`).

## 2. Ability -> meaning -> icon

From `research/cloud/Class-Ability-Shapes.md` sections 4 + 5 (Priest numbers: `docs/answered/classes.md` lines 142-146).
One icon per ability - all 4 shapes (walking / sprinting / mid-air / crouch) share it.

### Mage (class colour `#7fb0e0`; arcane / cosmic / frost)

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Meteor** | A1, LOCKED, 30 / 14 s | pick a spot within 25 blocks; 1 s later a meteor hits a 4-block area for 3.0 H | a faceted burning rock diving to the lower left, three-tongued fire trail with a violet arcane fringe, embers |
| **Mana Barrier** | A2, LOCKED, 20 / 30 s | a dome (12 s) where you look; inside it, damage drains Mana instead of Health | a glassy blue hex-panel dome on a rune ring, a glowing mana crystal inside |
| **Frost Nova** | A2-alt, PROPOSED, 24 / 22 s | freeze enemies within 5 blocks for 2 s, then Chill 3 s | a six-armed ice crystal with a gem core, six ice shards bursting outward |
| **Starfall** | A1-alt A, PROPOSED, 36 / 18 s | 12 stars fall over 3 s on a 6-block area | three pale starlight stars falling to the lower left with violet streaks |
| **Arcane Beam** | A1-alt B, PROPOSED, 30 / 18 s | channel a 20-block beam up to 3 s that ramps 1x -> 3x | a violet orb in a gold 4-prong cradle firing a beam of light that widens (the ramp), one rune ring round it |

### Priest (class colour `#f2e6a0`; holy / light / protection)

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Sacred Heal** | A1, LOCKED, 25 / 14 s | instant 25% max Health heal (Priest 30%) to everyone within 9 blocks + heal over time | a bold gold healing cross (flared ends, ivory inset) bursting a 12-ray sunburst |
| **Shield Bubble** | A2, LOCKED, 28 / 24 s | a 6-block bubble for 12 s with HP = your max Health; 4 heal pulses at 75 / 50 / 25 / 0% | a soul-cyan bubble with a highlight streak round a gold heater shield with a soul gem |
| **Guardian Spirit** | A2-alt, PROPOSED passive | 30-block aura: an ally (or you) who would die survives at 30% Health if you have the Mana | spread angel wings + gold halo round a cyan soul flame |
| **Sanctuary** | A1-alt A, PROPOSED (numbers LOCKED) | holy zone 12 s, 8 blocks: allies heal 5% max Health / s, take 10% less damage | an ivory gothic arch with a soul-gem keystone, holy light in the doorway, on a glowing gold rune circle |
| **Martyr's Grace** | A1-alt B, PROPOSED (numbers LOCKED) | 75% heal on the lowest ally within 30 blocks, chains -15 per jump | a big haloed rose heart with a heal plus, gold light bolts chaining to a smaller and a smallest heart |

Mage vs Priest at a glance: blue rim + navy field + cool arcane colours vs gold rim + warm umber field + gold / ivory / soul-cyan.
The Priest's cyan is the soul-cage v2 cyan from the Priest class emblem, so the two families match.

## 3. Defaults used (Skyy can change)

| Choice | Default used |
|---|---|
| Frame style | **round dark frame, class-colour rim**: a dark slate band (r 31.6 -> 28.6 px), a bevelled class-colour rim (28.6 -> 26.2 px), a 1 px dark line, all top-lit |
| Background | **dark, class tint**: radial field, Mage navy `#26335e` -> `#0e1226`, Priest warm umber `#43381e` -> `#15100c` |

## 4. Colours

Class colours (= the class emblem colours, `research/cloud/class-art/README.md`): Mage `#7fb0e0`, Priest `#f2e6a0`.

| Ramp (dark -> light) | Used for |
|---|---|
| FRAME `#0e111a #171c28 #212838 #2d3649 #3e4a60 #55627a` | the dark frame band (both classes) |
| MAGE_RIM `#1f2f5c #2f4f88 #4f7fba #7fb0e0 #b2d4f2 #e0eefa` | Mage rim |
| PRIEST_RIM `#4a3416 #7c6028 #b39a4c #dccb7c #f2e6a0 #fcf5d4` | Priest rim |
| FIRE `#4c1020 ... #fff1c0`, ROCK `#1c1222 ... #c8987a` | Meteor |
| ARCANE `#22104a #3a1a7e #5a2cb4 #8250e2 #ab82f6 #d2bcff #f1e8ff` | Arcane Beam, Starfall trails, Meteor fringe |
| MANA `#0e1f56 ... #2f6fe0 ... #def0ff` | Mana Barrier (mid = the approved Mana blue `#2f6fe0`) |
| ICE `#173a6e ... #f0fbff` | Frost Nova |
| STARLIGHT `#3a2c78 ... #fbf6e6` | Starfall stars (violet shadows, warm-white light) |
| GOLD `#3e2208 ... #fff4cc`, HOLY `#6e4e1c ... #fff9e4` | Priest gold + ivory light; Arcane Beam cradle |
| SOUL `#0f4a58 ... #dcfcf8` | Priest soul cyan (bubble, gems, Guardian soul) |
| ROSE `#4a0f26 ... #ffe2d6` | Martyr's Grace hearts |
| FEATHER `#5a4c64 ... #fbf6ea`, STEEL `#2a2c40 ... #f0f2f4` | Guardian wings, Shield Bubble shield face |

Full ramps: `manifest.json` -> `ramps_dark_to_light`. Shadows lean violet / blue, lights lean warm (hue-shifted).

## 5. 32 px readability pass (done once)

The first full set was checked at 32 px (box-filtered), then fixed:
- Meteor: brighter rock + lit facet, one crack instead of two (the rock was muddy).
- Mana Barrier: bigger hex cells (fewer lines = less noise); earlier pass: crystal inside the dome, glassier dome.
- Frost Nova: removed the frost ring (at 32 px it looked like a second frame); bigger outward shards, stronger glow.
- Starfall: 3 bigger stars instead of 4, fewer background dots.
- Arcane Beam: 1 rune ring instead of 2 (two looked like a spring); the beam is now light (glow, no dark outline).
- Guardian Spirit / Martyr's Grace: thicker halos; Martyr's Grace thicker chain bolts and a bigger last heart. Sanctuary: thicker ring.
- Earlier pass: Sacred Heal lost its outer ring (it read as a wheel / shield).
Before / after picture (outside this folder, review only): `/workspace/ability-icons-art/review/readability-32px-before-after.png`.

## 6. How to edit / rebuild

Scripts are in `tools/art/` (deterministic - two runs give the same bytes; checked):
```
python3 tools/art/make_ability_icons.py      # the 10 PNGs  (--only Meteor,FrostNova to redo some)
python3 tools/art/make_ability_sheet.py      # sheet.png + manifest.json
python3 tools/art/validate_ability_icons.py  # size, RGBA, hard alpha, no #000/#fff, distinct, deterministic
```
- `ability_icon_core.py` = paint engine (masks at 8x, bevel from an erosion distance, top light, frame + field).
- `make_ability_icons.py` = one function per icon (shapes + colours) and the ramps. Change a class colour in `MAGE_RIM` /
  `PRIEST_RIM` and `K.Style(...)`.
- `ability_icon_meta.py` = the ability text used by the sheet and manifest.
- `--out DIR` on each script writes somewhere else (default: `art/ability-icons/` next to `tools/`).

## 7. UNVERIFIED (for the main session)

1. The path `Common/Icons/Abilities/<Class>/<Name>.png` is new (from ART-RESUME). Whether the SkyyHud Abilities widget and the
   class / tree page can show a PNG from a mod path in a custom UI image, or only through an item icon (then each icon needs a hidden
   display item, like the class emblem question in `research/cloud/class-art/README.md`), is not checked.
2. How the HUD scales a 64 px icon (nearest vs linear) and what size it is drawn at - the sheet shows 64 and 32 px box-filtered.
3. Frame / gold colours vs the real vanilla HUD and window colours (not compared to Assets.zip from this box).
4. Not seen in game or in Blockbench - flat PNGs only.

## 8. Open questions for Skyy (each with a default)

| # | Question | Default |
|---|---|---|
| 1 | Frame: round dark frame with a class-colour rim? | **[yes - as drawn]** |
| 2 | Background: dark with a class tint? | **[yes - as drawn]** |
| 3 | Meteor fire: orange fire with a violet tail fringe, or all-violet "arcane fire"? | **[orange + violet fringe - reads as a meteor first]** |
| 4 | Guardian Spirit is a passive: add a "passive" mark on the icon (e.g. no cooldown sweep, or a small corner badge)? | **[no mark on the icon; the HUD says "Passive"]** |
| 5 | Locked / not-yet-owned abilities: a grey copy of each icon (like the class emblems), or let the HUD dim it? | **[HUD dims it at runtime; grey copies only if the UI cannot dim]** |
| 6 | One icon per ability (all 4 shapes share it), or a small corner mark per shape (sprint / air / crouch)? | **[one icon per ability]** |
| 7 | Same frame + style for the other 5 classes (Monk, Assassin, Warrior, Berserker, Archer), one class per commit? | **[yes, after this set is OK'd]** |
