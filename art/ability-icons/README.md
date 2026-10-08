# Class ability icons - Mage, Priest, Monk, Assassin, Warrior, Berserker (30 icons, 64 x 64)

ART-RESUME items 4 (Mage + Priest) and 6 (the other classes, one class per commit).

| Class | Status |
|---|---|
| Mage, Priest | **APPROVED + committed** (e87a4d9). Skyy, word for word: "The ability icons look great, commit them" |
| Monk | **APPROVED + committed** (59913fc). Review sheet as approved: `sheet-monk.png`. Skyy, word for word (2026-10-08): "They all look great, except the cyclone kick. The foot looks weird" -> Cyclone Kick redrawn (v2 foot); then Skyy, word for word: "Either wrap the foot or give his shoes don’t leave it bare" -> v3: the foot is wrapped in linen (no bare skin); then Skyy, word for word: "Use shoes instead, make the foot vertical like the first image" -> v4: the foot stands up again like the first image, in a soft Monk shoe. The other 4 Monk icons unchanged; then Skyy, word for word: "Yes, the shoe looks good, commit the Monk icons" |
| Assassin | **APPROVED + committed** (dbe4bd8). Review sheet as approved: `sheet-assassin.png`. Skyy, word for word (2026-10-08): "The hood looks a little weird, do an assassins creed style hood, with a face mask" -> hood v2 (beak hood + face mask) on Cloak + First Strike and Shadow Clone. Toxin, God Killer, Vanishing Act unchanged; then Skyy, word for word: "Yes, the Assassin hood looks good, commit them" |
| Warrior | **APPROVED + committed** (1cf4d85). Review sheet as approved: `sheet-warrior.png`. Skyy, word for word (2026-10-08): "Yes, the Warrior icons look good, commit them" (draft v1 approved as drawn, all defaults kept) |
| Berserker | **APPROVED + committed** (the Berserker commit after 1cf4d85). Review sheet as approved: `sheet-berserker.png`. Skyy, word for word (2026-10-08): "Yes, the Berserker icons look good, commit them" (draft v1 approved as drawn, all defaults kept) |

None of them is wired in or seen in game yet. Original pixels drawn from code (Python + numpy + Pillow). No vanilla Hytale file,
other mod or reference picture was read, copied, traced or recoloured. The approved Mage + Priest PNGs are byte-identical to the
committed ones (checked after adding Monk + Assassin).

`sheet.png` shows every class together; `sheet-monk.png` / `sheet-assassin.png` / `sheet-warrior.png` / `sheet-berserker.png` are the per-class sheets Skyy approved.

## 1. Files

| File | What |
|---|---|
| `Common/Icons/Abilities/Mage/Meteor.png` ... `ArcaneBeam.png` | 5 Mage icons, 64 x 64 RGBA |
| `Common/Icons/Abilities/Priest/SacredHeal.png` ... `MartyrsGrace.png` | 5 Priest icons, 64 x 64 RGBA |
| `Common/Icons/Abilities/Monk/FlowingForm.png`, `PalmStrike.png`, `CycloneKick.png`, `HundredFists.png`, `StillWater.png` | 5 Monk icons (approved) |
| `Common/Icons/Abilities/Assassin/CloakFirstStrike.png`, `Toxin.png`, `GodKiller.png`, `ShadowClone.png`, `VanishingAct.png` | 5 Assassin icons (approved) |
| `Common/Icons/Abilities/Warrior/RallyingGuard.png`, `ShieldShockwave.png`, `IronChain.png`, `BulwarkStance.png`, `Unbreakable.png` | 5 Warrior icons (approved) |
| `Common/Icons/Abilities/Berserker/Enrage.png`, `Whirlwind.png`, `Earthsplitter.png`, `BloodFrenzy.png`, `WarlordsBanner.png` | 5 Berserker icons (approved) |
| `sheet.png` | every done class: big labels, plain page, class colour swatch + APPROVED / FOR REVIEW tag per class, dark HUD strip |
| `sheet-monk.png`, `sheet-assassin.png` | the same layout for ONE class each (kept as Skyy reviewed + approved them) |
| `sheet-warrior.png` | the same layout for the Warrior icons only (kept as Skyy reviewed + approved it) |
| `sheet-berserker.png` | the same layout for the Berserker icons only (kept as Skyy reviewed + approved it) |
| `manifest.json` | every file: path, bytes, sha256, size, class, slot, ability text, what the icon shows, colour ramps |
| `README.md` | this file |

Every icon: round, alpha 0 outside the circle and 255 inside (hard alpha only, so straight vs premultiplied alpha does not
matter). No pure `#000000` / `#ffffff` pixel. File names have no spaces or symbols (`ManaBarrier.png`, `MartyrsGrace.png`,
`CloakFirstStrike.png` for "Cloak + First Strike").

## 2. Ability -> meaning -> icon

From `research/cloud/Class-Ability-Shapes.md` sections 4 Mage, 5 Priest, 7 Monk, 8 Assassin, 2 Warrior, 6 Berserker (Priest numbers:
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

### Monk (class colour Saffron `#f08a30`, LOCKED; martial / wind / calm) - APPROVED

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Flowing Form** | A1, LOCKED, 6 Mana + drain / 40 s | 30 s aura (5 blocks): enemies Awed; every hit = 1 combo stack (max 20), +2% move / +1.5% attack speed per stack | a glowing saffron chi orb inside three teal-white wind ribbons swirling round it, three small combo pips |
| **Palm Strike** | A2, LOCKED, 8 / 6 s | single-target strike: stun 0.75 s + knockback 4 blocks, 1.2 H | an open palm thrust forward (bare hand, linen-wrapped wrist + palm band), saffron impact glow and 10 burst rays |
| **Cyclone Kick** (v4) | A2-alt, PROPOSED, 10 / 8 s | spinning kick: everything within 3 blocks takes 0.8 H and is pushed 5 blocks | a kick: linen-wrapped shin coming in from the lower left, the foot standing UP at its end (toes up, sole facing the kick, heel at the bottom) in a soft earth-brown Monk shoe - light tan sole edge, instep strap, padded collar; a long saffron whirl arc sweeping right-to-bottom and a short one upper-left, both clear of the shoe |
| **Hundred Fists** | A1-alt A, PROPOSED, 8 + drain / 40 s | Flowing Form where every 10th hit releases a shockwave on all Awed enemies | a big linen-wrapped fist between two small saffron after-image fists with motion streaks, impact sparks above |
| **Still Water** | A1-alt B, PROPOSED, 18 / 25 s | 10 s stance: deflect front projectiles, counter melee hits (1.0 H), every counter adds Awe | one water drop falling to a calm pond (two ripple rings) under a saffron sun with rays on the horizon |

Monk look: saffron rim, dark rust field (`#4a2416` -> `#170b09`), linen hand wraps like the Monk class emblem's wrapped fist.

### Assassin (class colour `#b58cff`; stealth / poison / the kill) - APPROVED

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Cloak + First Strike** (`CloakFirstStrike.png`) | A1, LOCKED, 14 / 30 s | invisible 8 s (breaks on attack); next hit within 10 s gets +100% crit chance | (hood v2) an Assassin's-Creed-style hood: sharp eagle-beak peak dipping down between two glowing lilac eyes, draped sides, a dark cloth face mask over nose + mouth; the hood's lower edge fades into the dark; a big gold 4-point crit star |
| **Toxin** | A2, LOCKED, 12 / 16 s | thrown vial: 4-block poison cloud 5 s, Poison 0.25 H/s + Weakened 15% | a tilted corked glass vial of bubbling green poison, a toxic green cloud spilling out, drips |
| **God Killer** | A2-alt, LOCKED, 14 / 45 s | next hit on a boss / mini-boss within 12 s does 2x, 3x on a backstab | a steel dagger (gold guard, wrapped grip, violet pommel gem) stabbing down through a cracked gold boss crown |
| **Shadow Clone** | A1-alt A, PROPOSED, 20 / 35 s | cloak + a decoy mobs attack for 5 s; it bursts for 2.0 H | (hood v2) the assassin in the beak hood + face mask in front, a glowing lilac shadow copy of itself (same hood + mask) behind, burst sparks off the copy |
| **Vanishing Act** | A1-alt B, PROPOSED, 16 / 28 s | instant 3 s cloak + 4-block smoke: enemies inside lose you 2 s, Slowed 25% | an iron smoke bomb (violet band, lit fuse) bursting into a big cloud of violet-grey smoke |

Assassin look: lilac rim, dark plum field (`#33224e` -> `#0e0916`) - redder and darker than the Mage's navy, so the two violet-ish
classes do not mix up. The dagger matches the Assassin class emblem (gold guard, violet gem).

### Warrior (class colour `#e0b060`; tank + crowd control - shield wall / steel / rally) - APPROVED

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Rallying Guard** | A1, LOCKED, 12 / 24 s | you + party within 6 blocks take 20% less damage 6 s; mobs within 8 turn to you 4 s | a swallow-tailed crimson war banner (gold trim) on an oak spear with a steel leaf head, a small steel guard-shield emblem on the cloth, amber rally-cry arcs either side of the spear head |
| **Shield Shockwave** | A2, LOCKED, 10 / 12 s | 6-block cone: stun 1.5 s, 1.0 H | a round oak-plank shield (riveted iron rim, steel boss) slamming right, three amber shock arcs fanning out in a cone, two gold stun stars |
| **Iron Chain** | A2-alt, PROPOSED, 12 / 14 s | 15-block chain hooks the first enemy, drags it to you, stun 1 s, 0.6 H | a heavy steel hook (eye, shank, J curve + barb) flying to the upper right on interlocking iron links, amber pull streaks along the chain |
| **Bulwark Stance** | A1-alt A, PROPOSED, 14 / 28 s | 8 s: 50% less from the front, front projectiles blocked, 30% slower, allies behind take 25% less | a tall gold-rimmed steel tower shield planted on the ground (crimson pale, gold boss, rivets), three red-fletched arrows stuck in its face, an impact spark |
| **Unbreakable** | A1-alt B, PROPOSED, 16 / 40 s | taunt 8 blocks; 5 s you cannot drop below 1 HP; end heal 20% of damage taken | a closed steel great helm (eye slits, breath holes, riveted iron cross bands) cracked all over but held together - the cracks glow amber-gold - chips flying off |

Warrior look: amber-gold rim from the class colour `#e0b060`, dark GUNMETAL field (`#2a3a44` -> `#0b1216`, a cool steel-teal). Why: the
rim is warm gold, so a warm field would make it a second Priest (gold rim + umber field) or Monk (saffron rim + rust field); the cool
steel field keeps the three warm-rimmed classes apart at a glance, reads as "steel / armour", and is greyer + greener than the Mage's
navy. The Warrior rim ramp is more orange and more saturated than the Priest's pale lemon-gold. Spear + crimson banner match the
Warrior class emblem (longsword + spear, ruby / red accents).

### Berserker (class colour `#d9443f`; party damage buffer + sustained melee - fury / blood / the axe) - APPROVED

| Icon | Slot | What the ability does | What the icon shows |
|---|---|---|---|
| **Enrage** | A1, LOCKED, 14 / 30 s | players within 8 + party within 16: damage +10 -> +20% over 10 s, holds 5 s; you x2 | a horned beast skull (bone, long upswept horns, cracked brow) with glowing red eyes in a blaze of blood-red + ember rage fire |
| **Whirlwind** | A2, LOCKED, 12 / 14 s | spin 3 s, hit everything within 3 blocks every 0.5 s, heal 10% of the damage | the class emblem's bearded double-bit battleaxe (red-wrapped haft, ruby socket) mid-spin, a faint red after-image, two blood-red whirl ribbons |
| **Earthsplitter** | A2-alt, PROPOSED, 14 / 12 s | 12-block shockwave line, 2.0 H, knock-up 1 s; stronger the lower your Health | the battleaxe buried blade-first in scorched ground, a glowing ember-orange crack splitting the earth toward you, rock chunks flung up |
| **Blood Frenzy** (`BloodFrenzy.png`) | A1-alt A, PROPOSED toggle | every swing stacks (max 25, 6 s decay); aura buffs allies half | three curved blood-red claw slashes with bright cores, blood drops, three stack pips (two lit red, one bone) |
| **Warlord's Banner** (`WarlordsBanner.png`) | A1-alt B, PROPOSED, 40 / 40 s | plant a banner 30 s, 12 blocks: +8 / 12 / 16% damage + defence + attack speed; kills extend it | a tall iron war standard (spear finial, crossbar) in a glowing red aura ring, a tattered dark banner with a red border + red crossed-axe sign |

Berserker look: blood-red rim from the class colour `#d9443f`, dark OXBLOOD field (`#42161e` -> `#120609`, a deep wine red). Why: red is
the only red class, so the rim already reads; the field stays in the same hue family (like Mage navy / Assassin plum) for a hot, angry
read. It is cooler (wine, not orange) and a little darker than the Monk's rust `#4a2416`, so the Monk's saffron-on-rust and the
Berserker's red-on-oxblood stay apart at 32 px (checked side by side in `review/berserker-v1.png`); far from the Warrior's cool
gunmetal. The battleaxe is the class emblem's bearded double-bit axe (red-wrapped haft, ruby). Warlord's Banner is a HANGING dark
war standard on an iron pole (vs the Warrior's sideways crimson swallowtail on a spear) so the two banners do not mix up.

Mage vs Priest at a glance: blue rim + navy field + cool arcane colours vs gold rim + warm umber field + gold / ivory / soul-cyan.
The Priest's cyan is the soul-cage v2 cyan from the Priest class emblem, so the two families match.

## 3. Defaults used (Skyy can change)

| Choice | Default used |
|---|---|
| Frame style | **round dark frame, class-colour rim**: a dark slate band (r 31.6 -> 28.6 px), a bevelled class-colour rim (28.6 -> 26.2 px), a 1 px dark line, all top-lit |
| Background | **dark, class tint**: radial field, Mage navy `#26335e` -> `#0e1226`, Priest warm umber `#43381e` -> `#15100c`, Monk dark rust `#4a2416` -> `#170b09`, Assassin dark plum `#33224e` -> `#0e0916`, Warrior gunmetal `#2a3a44` -> `#0b1216`, Berserker oxblood `#42161e` -> `#120609` |

Skyy approved both defaults with the Mage + Priest set; Monk, Assassin, Warrior and Berserker use the same frame and the same kind of field.

## 4. Colours

Class colours (= the class emblem colours, `research/cloud/class-art/README.md`): Mage `#7fb0e0`, Priest `#f2e6a0`,
Monk Saffron `#f08a30` (LOCKED by Skyy), Assassin `#b58cff`, Warrior `#e0b060`, Berserker `#d9443f`.

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
| SMOKE `#241e30 ... #e6e4ee`, IRON `#12121c ... #7c7c94` | Vanishing Act smoke + bomb; dagger grip; SMOKE also the Assassin face mask (hood v2); IRON also the Warrior chain links, helm bands, shield boss flange |
| WAR_RIM `#4a2a10 #7e5220 #b4823a #e0b060 #f2d08c #fbeccc` | Warrior rim (from `#e0b060`) |
| AMBER `#5a2c0e ... #fff0cc`, CRIMSON `#2e0c18 ... #f08c66`, OAK `#2c1a14 ... #d8b47e` | Warrior shout / shock arcs + glowing cracks; banner, pale + fletching; spear shaft, shield planks, arrow shafts. STEEL + GOLD reused for blades, shields, helm, trim |
| BERS_RIM `#4a0e16 #7e1a22 #b02c30 #d9443f #ee7a64 #f8b8a0` | Berserker rim (from `#d9443f`) |
| BLOOD `#2a0612 ... #ffc8a8`, BONE `#3c2e2a ... #f4ecd8`, STONE `#1c161c ... #a8968a`, CHAR `#120c12 ... #544044` | Berserker rage fire, slashes, haft wraps, banner sign + aura; beast skull, stack pip; scorched ground + rocks; dark banner cloth. FIRE (Mage) reused for the ember crack + inner flames; IRON / STEEL / OAK for the axe + standard |

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

**Hood v2 (after Skyy: "The hood looks a little weird, do an assassins creed style hood, with a face mask"):** one shared
hood drawing, so both icons that show the hooded assassin changed - Cloak + First Strike and Shadow Clone (no other icon uses
it). The old hood was a soft rounded cowl with an oval face hole. New hood: a taller, sharp triangular peak with a lit centre
seam; at the front the peak comes DOWN as an eagle beak - a sharp point that dips into the face opening right between the
eyes, with a lit brim edge along both sides of the point so it reads against the dark face. Draped sides fall from the cheeks
to wide shoulders (side folds). Lower face: a dark grey-violet cloth face mask over nose and mouth (top hem peaks over the
nose and is lit, diagonal wrap folds meeting under the nose); the two glowing lilac eyes sit in the shadow between beak and
mask, set a bit wider and higher than before. Shadow Clone's copy has the same beak hood and mask in lilac. Cloak + First
Strike: the fade-out now starts lower (below the mask) so the masked face stays solid and only the shoulders melt into the
dark. Lilac rim, plum field, gold crit star, clone sparks unchanged.
Before / after: `/workspace/ability-icons-art/review/assassin-hood-v2.png`.

### Berserker (draft v1)
Built at 64 px, checked at 32 px (box-filtered) and fixed before the review sheet:
- Enrage: first horns were short stubs (read as ears) - now long, upswept, tapering horns, so the skull reads as a horned beast.
- Whirlwind: axe 25% bigger, whirl ribbons thicker (the axe was lost inside the spin).
- Earthsplitter: the axe floated over the ground - now drawn first and covered by the ground, so the blade is buried; the haft
  now runs up-right out of the ground and the head sits higher so the blade still shows at 32 px.
- Blood Frenzy: slashes were pink - darker blood red with a lighter core.
- Warlord's Banner: unchanged (read fine).
Validator: all 30 PASS; the closest pair at 32 px is still Rallying Guard vs Unbreakable (12.9, want > 10).
Review image: `/workspace/ability-icons-art/review/berserker-v1.png` (review only, outside this folder). Approved as drawn.

### Warrior (draft v1)
Built straight at 64 px, then checked at 32 px (box-filtered) and fixed before the review sheet:
- Rallying Guard: moved the whole banner + spear down 5 px (the spear head ran into the rim).
- Iron Chain: links were a solid "stick with holes" - now big face-on rings alternating with short edge-on iron bars, a thicker hook;
  the pull streaks moved away from the chain (at 32 px they merged into it), 2 instead of 3.
- Bulwark Stance: dropped the dust puffs (brown dots) and a glancing arrow (unreadable); three arrows stuck in the face instead.
- Unbreakable: the gold cross bands drowned the cracks at 32 px - bands are now riveted IRON, so the amber-gold cracks (dark edge,
  bright core, soft glow) are the only gold on the helm; cracks thicker.
- Shield Shockwave: unchanged (read fine).
Closest pair at 32 px (validator): Rallying Guard vs Unbreakable, mean abs diff 12.9 (want > 10).
Review image: `/workspace/ability-icons-art/review/warrior-v1.png` (review only, outside this folder). Approved as drawn.

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

### Berserker (answered - all defaults kept)
| # | Question | Default |
|---|---|---|
| 1 | Field: dark oxblood (wine red, like the rim) - OK, or a neutral scorched-charcoal so the red rim pops more? | **[oxblood `#42161e` -> `#120609`]** |
| 2 | Enrage as a horned beast skull in rage fire (the beast within), or a roaring face / war cry? | **[horned skull - big silhouette at 32 px]** |
| 3 | Whirlwind + Earthsplitter both show the emblem's double-bit battleaxe - OK, or a mace for one of them (the emblem's second weapon)? | **[axe for both - spin vs buried; different poses]** |
| 4 | Blood Frenzy as three claw slashes - the Berserker uses axes / maces, not claws; OK as a "frenzy of hits" sign, or axe-cut slashes (straighter)? | **[curved slashes as drawn]** |
| 5 | Warlord's Banner: dark cloth with a red crossed-axe sign hanging from an iron standard (so it is not the Warrior's crimson swallowtail) - OK? | **[yes]** |

### Warrior (answered - all defaults kept)
| # | Question | Default |
|---|---|---|
| 1 | Field colour: dark gunmetal (cool steel-teal) so the gold rim is not a second Priest / Monk - OK, or a warm dark (bronze / oxblood)? | **[gunmetal `#2a3a44` -> `#0b1216`]** |
| 2 | Rim: the class colour `#e0b060` (amber-gold) like every other class, even though it sits near the Priest's pale gold? | **[yes, class colour - the field tells them apart]** |
| 3 | Rallying Guard as a war banner on a spear (rally + guard-shield emblem), or a war horn / shout? | **[banner - reads "rally" at 32 px; spear matches the emblem]** |
| 4 | Shield Shockwave round oak shield vs Bulwark Stance tall steel tower shield - two different shields OK? | **[yes - round = bash, tower = wall]** |
| 5 | Unbreakable as a cracked great helm held together by glowing gold cracks? | **[yes - "cracked but not broken"]** |
| 6 | Banner / pale / fletching colour: crimson (emblem ruby), or the Warrior amber? | **[crimson - contrast with the gold rim]** |

Mage + Priest: answered ("The ability icons look great, commit them" - frame + background defaults kept).
Monk: answered ("Yes, the shoe looks good, commit the Monk icons" - the defaults below were kept as drawn).
Assassin: answered ("Yes, the Assassin hood looks good, commit them" - the defaults below were kept as drawn).
Warrior: answered ("Yes, the Warrior icons look good, commit them" - the defaults above were kept as drawn).
Berserker: answered ("Yes, the Berserker icons look good, commit them" - the defaults above were kept as drawn).

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
| 5 | Hood v2 (Assassin's-Creed-style beak hood + face mask): mask colour dark grey-violet - OK, or same violet as the hood / black? | **[dark grey-violet - separates mask from hood at 32 px]** |

### All classes
| # | Question | Default |
|---|---|---|
| 1 | Guardian Spirit (passive) / locked abilities: marks on the icon? | **[no marks; the HUD shows "Passive" / dims locked ones]** |
| 2 | Next: Warrior, Berserker, Archer the same way, one class per commit? | **[yes, after Monk + Assassin are OK'd]** |
