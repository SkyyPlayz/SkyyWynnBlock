# Class ability icons - Mage, Priest, Monk, Assassin (20 icons, 64 x 64)

ART-RESUME items 4 (Mage + Priest) and 6 (the other classes, one class per commit).

| Class | Status |
|---|---|
| Mage, Priest | **APPROVED + committed** (e87a4d9). Skyy, word for word: "The ability icons look great, commit them" |
| Monk | **Reviewed once, waiting for Skyy's OK on the fix**, not committed. Review sheet: `sheet-monk.png`. Skyy, word for word (2026-10-08): "They all look great, except the cyclone kick. The foot looks weird" -> Cyclone Kick redrawn (v2 foot); then Skyy, word for word: "Either wrap the foot or give his shoes don’t leave it bare" -> v3: the foot is wrapped in linen (no bare skin); then Skyy, word for word: "Use shoes instead, make the foot vertical like the first image" -> v4: the foot stands up again like the first image, in a soft Monk shoe. The other 4 Monk icons unchanged |
| Assassin | **NEW - waiting for Skyy's review**, not committed. Review sheet: `sheet-assassin.png` |

None of them is wired in or seen in game yet. Original pixels drawn from code (Python + numpy + Pillow). No vanilla Hytale file,
other mod or reference picture was read, copied, traced or recoloured. The approved Mage + Priest PNGs are byte-identical to the
committed ones (checked after adding Monk + Assassin).

**Start here:** `sheet-monk.png`, then `sheet-assassin.png` (one class at a time). `sheet.png` shows every done class together.

## 1. Files

| File | What |
|---|---|
| `Common/Icons/Abilities/Mage/Meteor.png` ... `ArcaneBeam.png` | 5 Mage icons, 64 x 64 RGBA |
| `Common/Icons/Abilities/Priest/SacredHeal.png` ... `MartyrsGrace.png` | 5 Priest icons, 64 x 64 RGBA |
| `Common/Icons/Abilities/Monk/FlowingForm.png`, `PalmStrike.png`, `CycloneKick.png`, `HundredFists.png`, `StillWater.png` | 5 Monk icons (NEW) |
| `Common/Icons/Abilities/Assassin/CloakFirstStrike.png`, `Toxin.png`, `GodKiller.png`, `ShadowClone.png`, `VanishingAct.png` | 5 Assassin icons (NEW) |
| `sheet.png` | every done class: big labels, plain page, class colour swatch + APPROVED / FOR REVIEW tag per class, dark HUD strip |
| `sheet-monk.png`, `sheet-assassin.png` | the same layout for ONE new class each (for review one class at a time) |
| `manifest.json` | every file: path, bytes, sha256, size, class, slot, ability text, what the icon shows, colour ramps |
| `README.md` | this file |

Every icon: round, alpha 0 outside the circle and 255 inside (hard alpha only, so straight vs premultiplied alpha does not
matter). No pure `#000000` / `#ffffff` pixel. File names have no spaces or symbols (`ManaBarrier.png`, `MartyrsGrace.png`,
`CloakFirstStrike.png` for "Cloak + First Strike").

## 2. Ability -> meaning -> icon

From `research/cloud/Class-Ability-Shapes.md` sections 4 Mage, 5 Priest, 7 Monk, 8 Assassin (Priest numbers:
`docs/answered/classes.md` lines 142-146).
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

### Monk (class colour Saffron `#f08a30`, LOCKED; martial / wind / calm) - NEW

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Flowing Form** | A1, LOCKED, 6 Mana + drain / 40 s | 30 s aura (5 blocks): enemies Awed; every hit = 1 combo stack (max 20), +2% move / +1.5% attack speed per stack | a glowing saffron chi orb inside three teal-white wind ribbons swirling round it, three small combo pips |
| **Palm Strike** | A2, LOCKED, 8 / 6 s | single-target strike: stun 0.75 s + knockback 4 blocks, 1.2 H | an open palm thrust forward (bare hand, linen-wrapped wrist + palm band), saffron impact glow and 10 burst rays |
| **Cyclone Kick** (v4) | A2-alt, PROPOSED, 10 / 8 s | spinning kick: everything within 3 blocks takes 0.8 H and is pushed 5 blocks | a kick: linen-wrapped shin coming in from the lower left, the foot standing UP at its end (toes up, sole facing the kick, heel at the bottom) in a soft earth-brown Monk shoe - light tan sole edge, instep strap, padded collar; a long saffron whirl arc sweeping right-to-bottom and a short one upper-left, both clear of the shoe |
| **Hundred Fists** | A1-alt A, PROPOSED, 8 + drain / 40 s | Flowing Form where every 10th hit releases a shockwave on all Awed enemies | a big linen-wrapped fist between two small saffron after-image fists with motion streaks, impact sparks above |
| **Still Water** | A1-alt B, PROPOSED, 18 / 25 s | 10 s stance: deflect front projectiles, counter melee hits (1.0 H), every counter adds Awe | one water drop falling to a calm pond (two ripple rings) under a saffron sun with rays on the horizon |

Monk look: saffron rim, dark rust field (`#4a2416` -> `#170b09`), linen hand wraps like the Monk class emblem's wrapped fist.

### Assassin (class colour `#b58cff`; stealth / poison / the kill) - NEW

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Cloak + First Strike** (`CloakFirstStrike.png`) | A1, LOCKED, 14 / 30 s | invisible 8 s (breaks on attack); next hit within 10 s gets +100% crit chance | a pointed shadow-violet hood with lilac eyes, its lower half fading into the dark; a big gold 4-point crit star |
| **Toxin** | A2, LOCKED, 12 / 16 s | thrown vial: 4-block poison cloud 5 s, Poison 0.25 H/s + Weakened 15% | a tilted corked glass vial of bubbling green poison, a toxic green cloud spilling out, drips |
| **God Killer** | A2-alt, LOCKED, 14 / 45 s | next hit on a boss / mini-boss within 12 s does 2x, 3x on a backstab | a steel dagger (gold guard, wrapped grip, violet pommel gem) stabbing down through a cracked gold boss crown |
| **Shadow Clone** | A1-alt A, PROPOSED, 20 / 35 s | cloak + a decoy mobs attack for 5 s; it bursts for 2.0 H | the hooded assassin in front with a glowing lilac shadow copy of itself behind, burst sparks off the copy |
| **Vanishing Act** | A1-alt B, PROPOSED, 16 / 28 s | instant 3 s cloak + 4-block smoke: enemies inside lose you 2 s, Slowed 25% | an iron smoke bomb (violet band, lit fuse) bursting into a big cloud of violet-grey smoke |

Assassin look: lilac rim, dark plum field (`#33224e` -> `#0e0916`) - redder and darker than the Mage's navy, so the two violet-ish
classes do not mix up. The dagger matches the Assassin class emblem (gold guard, violet gem).

Mage vs Priest at a glance: blue rim + navy field + cool arcane colours vs gold rim + warm umber field + gold / ivory / soul-cyan.
The Priest's cyan is the soul-cage v2 cyan from the Priest class emblem, so the two families match.

## 3. Defaults used (Skyy can change)

| Choice | Default used |
|---|---|
| Frame style | **round dark frame, class-colour rim**: a dark slate band (r 31.6 -> 28.6 px), a bevelled class-colour rim (28.6 -> 26.2 px), a 1 px dark line, all top-lit |
| Background | **dark, class tint**: radial field, Mage navy `#26335e` -> `#0e1226`, Priest warm umber `#43381e` -> `#15100c`, Monk dark rust `#4a2416` -> `#170b09`, Assassin dark plum `#33224e` -> `#0e0916` |

Skyy approved both defaults with the Mage + Priest set; Monk + Assassin use the same frame and the same kind of field.

## 4. Colours

Class colours (= the class emblem colours, `research/cloud/class-art/README.md`): Mage `#7fb0e0`, Priest `#f2e6a0`,
Monk Saffron `#f08a30` (LOCKED by Skyy), Assassin `#b58cff`.

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
| FEATHER `#5a4c64 ... #fbf6ea`, STEEL `#2a2c40 ... #f0f2f4` | Guardian wings, Shield Bubble shield face; STEEL also the Assassin dagger |
| MONK_RIM `#5a2208 #8e3a10 #c45c1c #f08a30 #f8b462 #fde0b0` | Monk rim (from Saffron `#f08a30`) |
| SAFFRON `#561a0c ... #f08a30 ... #fff2d0` | Monk orb, whirls, impact, after-images, sun |
| LINEN `#4e3a34 ... #f8f0dc`, SKIN `#4a2220 ... #f8d0aa` | Monk hand / foot wraps, bare palm / foot |
| WIND `#163e4e ... #eafaf2`, WATER `#10304e ... #ccf0f4` | Flowing Form wind ribbons, Still Water drop + pond |
| ASSN_RIM `#2e1c5a #4c3290 #7a5cc8 #b58cff #d4bcff #f0e8ff` | Assassin rim (from `#b58cff`) |
| SHADE `#100a1a ... #8e7ab0`, LILAC `#3e2478 ... #f0e8ff` | Assassin hoods, eyes, shadow clone, bomb band |
| POISON `#123214 ... #ecffd0`, GLASS `#22303e ... #e6f6f2`, WOOD `#3a2214 ... #d0a868` | Toxin vial, cloud, cork; bomb fuse |
| SMOKE `#241e30 ... #e6e4ee`, IRON `#12121c ... #7c7c94` | Vanishing Act smoke + bomb; dagger grip |

Full ramps: `manifest.json` -> `ramps_dark_to_light`. Shadows lean violet / blue, lights lean warm (hue-shifted).

## 5. 32 px readability pass (done once per class)

### Monk
First drafts were redrawn before the pass: Cyclone Kick's foot (it read as a stick) became a side kick with the foot flexed up;
Hundred Fists' overlapping after-images (one blob) became two separate small fists; Still Water lost its filled ripple centre.
Then at 32 px:
- Palm Strike: removed the two impact rings (mud), brighter skin, stronger glow behind the hand.
- Cyclone Kick: removed the four little wind dashes (they looked like clock ticks); thicker, brighter whirl arcs.
- Hundred Fists: removed the shockwave ring (it looked like a second rim); main fist 8% bigger.
- Still Water: darker water, brighter + thicker ripple rings. Flowing Form: unchanged (read fine).
Before / after: `/workspace/ability-icons-art/review/readability-32px-monk.png` (review only, outside this folder).

**Cyclone Kick v2 (after Skyy: "They all look great, except the cyclone kick. The foot looks weird"):** the old foot stood up
at the end of the shin with its sole turned toward the viewer, so it read as a blob / mallet. New foot = clean SIDE PROFILE,
pointed along the kick: sloping instep, rounded toes with two toe creases at the front, a round heel bump below and behind the
ankle, the arch and ball of the foot underneath (a shade darker), bare skin with only a narrow linen band at the ankle; the
leg tapers from a thick calf to a slim ankle (linen wraps kept). Tried and dropped: a foot standing up like an L (still read
as a mallet) and a bent-knee leg (the thigh made it read less as a kick). 32 px pass: the toes touched the right arc's thick
head and merged with it, so the two saffron arcs now sit above-left and below-right of the leg (125-degree sweeps) and the
foot is moved 2-3 px toward the centre - the leg and foot cross no arc, so the foot outline stays clean at 32 px.
Old vs new: `/workspace/ability-icons-art/review/cyclone-kick-old-vs-new.png`.

**Cyclone Kick v3 (after Skyy: "Either wrap the foot or give his shoes don’t leave it bare"):** chose WRAPS (matches the Monk's
linen hand / shin wraps; shoes would be a new look). The whole foot is now wrapped in the same linen as the shin - no bare skin
anywhere. Same side-profile silhouette (toes forward, heel back). To keep the foot from melting into the shin (all one linen
"stick" at first try): the foot is a step lighter than the shin (the shin a step darker), the foot has fewer, softer wrap
layers than the shin, a darker linen sole underneath, a wrapped toe end with a tuck line, a blunter toe (so it does not read
as a blade), and a small SAFFRON cloth tie with a knot tail round the ankle that separates leg and foot (and adds the class
colour). Bare vs wrapped: `/workspace/ability-icons-art/review/cyclone-kick-wrapped-foot.png`.

**Cyclone Kick v4 (after Skyy: "Use shoes instead, make the foot vertical like the first image"):** the leg is back in the FIRST
pose (same angle and place as the first Cyclone Kick): linen-wrapped shin from the lower left, the foot standing up at the end
of it - toes up, sole facing the kick direction, heel at the bottom. No bare skin, no foot wraps: it wears a soft Monk shoe -
warm earth-brown cloth upper with a rounded toe box, a THICK light tan sole along the kicking side (ball pad at the top,
thinner arch, heel block at the bottom, so the sole edge reads as a shoe bottom even at 32 px), stitched seam inside the sole,
a tan instep strap and a darker padded collar where the wrapped shin goes in. The saffron ankle tie from v3 is gone (it was
part of the wraps). Whirl arcs moved: the shoe fills the upper-right quarter, and the old arc head ran into the toe at 32 px,
so now one long arc sweeps from the right round to the bottom and a short one sits upper-left - neither touches the shoe.
First image vs wrapped (v3) vs shoe (v4): `/workspace/ability-icons-art/review/cyclone-kick-shoe.png`.

### Assassin
First fix before the pass: hoods were too dark on the plum field - brighter cloth + stronger lilac glow behind. Then at 32 px:
- Cloak + First Strike: bigger crit star with more glow.
- God Killer: wider, brighter blade (it got lost at 32 px).
- Vanishing Act: bigger, lighter bomb with a brighter violet band and glow, bigger fuse spark.
- Toxin, Shadow Clone: unchanged (read fine).
Before / after: `/workspace/ability-icons-art/review/readability-32px-assassin.png`.

### Mage + Priest (approved set)
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
python3 tools/art/make_ability_sheet.py      # sheet.png + sheet-<class>.png (classes still in review) + manifest.json
python3 tools/art/validate_ability_icons.py  # size, RGBA, hard alpha, no #000/#fff, distinct, deterministic
```
- `ability_icon_core.py` = paint engine (masks at 8x, bevel from an erosion distance, top light, frame + field).
- `make_ability_icons.py` = one function per icon (shapes + colours) and the ramps. Change a class colour in `MAGE_RIM` /
  `PRIEST_RIM` and `K.Style(...)`.
- `ability_icon_meta.py` = the ability text used by the sheet and manifest, and each class's review status
  (`CLASS_INFO[...]["review"]`: set it to `"approved"` + the answer when Skyy OKs a class - its sheet-<class>.png then stops being made).
- Adding a class: a `K.Style(...)` + rim ramp, one painter function per ability, rows in `ICONS`, entries in `META` / `CLASS_INFO`.
- `--out DIR` on each script writes somewhere else (default: `art/ability-icons/` next to `tools/`).

## 7. UNVERIFIED (for the main session)

1. The path `Common/Icons/Abilities/<Class>/<Name>.png` is new (from ART-RESUME). Whether the SkyyHud Abilities widget and the
   class / tree page can show a PNG from a mod path in a custom UI image, or only through an item icon (then each icon needs a hidden
   display item, like the class emblem question in `research/cloud/class-art/README.md`), is not checked.
2. How the HUD scales a 64 px icon (nearest vs linear) and what size it is drawn at - the sheet shows 64 and 32 px box-filtered.
3. Frame / gold colours vs the real vanilla HUD and window colours (not compared to Assets.zip from this box).
4. Not seen in game or in Blockbench - flat PNGs only.

## 8. Open questions for Skyy (each with a default)

Mage + Priest: answered ("The ability icons look great, commit them" - frame + background defaults kept).

### Monk
| # | Question | Default |
|---|---|---|
| 1 | Cyclone Kick v4: upright foot in a soft earth-brown shoe with a tan sole - OK? (darker shoe, or a saffron strap instead of tan?) | **[brown shoe, tan sole + strap - as drawn]** |
| 2 | Hundred Fists: add a shockwave ring for "every 10th hit"? (taken out - it looked like a second rim at 32 px) | **[no ring; the fist flurry says it]** |
| 3 | Still Water: calm pond + sun (the calm stance), or show the deflect (an arrow bouncing off)? | **[calm pond + sun]** |
| 4 | Flowing Form: teal-white wind round a saffron orb, or all saffron? | **[teal wind - more contrast, reads as speed]** |

### Assassin
| # | Question | Default |
|---|---|---|
| 1 | File name for "Cloak + First Strike": `CloakFirstStrike.png`? | **[yes]** |
| 2 | Cloak and Shadow Clone both use the hood (Cloak = one fading hood, Clone = hood + shadow copy). OK, or Cloak as something else (e.g. a fading dagger)? | **[hood for both - same assassin, reads as "me" vs "two of me"]** |
| 3 | Toxin poison green, or violet poison to match the class colour? | **[green - reads as poison at a glance]** |
| 4 | God Killer: gold crown = "boss". OK? | **[yes]** |

### All classes
| # | Question | Default |
|---|---|---|
| 1 | Guardian Spirit (passive) / locked abilities: marks on the icon? | **[no marks; the HUD shows "Passive" / dims locked ones]** |
| 2 | Next: Warrior, Berserker, Archer the same way, one class per commit? | **[yes, after Monk + Assassin are OK'd]** |
