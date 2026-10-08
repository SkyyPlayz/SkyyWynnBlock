# Class ability SHAPES - 4 abilities, 2 primary + 2 alt, 4 shapes each, for every class

Cloud draft, 2026-10-08. Design only, no code. It applies Skyy's newest ability-key decisions to every class: which 4 abilities a
character owns, how each one behaves in its 4 shapes (walking / sprinting / mid-air as a PRIMARY, crouch as an ALT), what each shape
costs, which pairs make good primaries, and where the engine may say no. Numbers are placeholders in the style of
`research/cloud/Class-Ability-Spec-Draft.md` (base cost / cooldown taken from there; every shape line says what changes).

Marks: **LOCKED** = Skyy's line, **PROPOSED** = a default for Skyy to accept or change, **UNVERIFIED** = needs the game
(SkyyKeyProbe K-list in `research/cloud/Ability-Input-Design.md` section 6, engine probes P-list in
`research/cloud/Class-Ability-Engine-Spec.md` section 16).

## 0. Decisions this follows (`docs/answered/classes.md`, newest wins)

| Line | Skyy's decision | What this spec does with it |
|---|---|---|
| 153 | "we decided 4 ability's, 2 active at a time. the 2 you pick are your primary ability's, and work when walking or sprinting. thew other 2 are set to crouch. so crouching uses your alt ability's." | 4 owned abilities; 2 PRIMARY on Ability 2 / Ability 3; the other 2 are ALT on crouch + Ability 2 / 3. Crouch = a different ability, not a stance of the same one |
| 154 | "we can still do same ability 4 shapes. walking sprinting and mid air, crouch 3 shapes on the primary, and secondary is crouch, but the crouch version is a little different than if you had that ability set to a primary." | every ability has up to 4 shapes: walking, sprinting, mid-air (as a primary) and crouch (as an alt). The crouch shape is "a little different", not a new ability |
| 155 | cost / cooldown "depends on what they change about the ability"; mid-roll cast allowed ("hit sprint and ability 2 at the same time, and dodge and cast at the same time") | cost / cooldown set PER SHAPE below; section 9 defines the mid-roll cast |
| 156 | "if it doesnt we can just skip mid roll cast" | mid-roll cast is dropped (no workaround) if K4 / K11 say the press does not reach the server during a roll |
| 151, 152 | roll = the sprint press (Skyy holds sprint; a tap rolls); never rebind; no new client keys; combos + hotbar items wanted | sprint is read as a STATE at the press (sprinting shape); the roll itself is never an ability trigger |
| 150 | Monk free air jump by CROUCH; Plunge Punch = crouch near the apex; the jump key in mid-air is not seen | crouch in mid-air belongs to MOVEMENT (double jump, Monk air jump, Plunge). In the air the keys always cast the mid-air shape of a PRIMARY; alts cannot be cast in the air |
| 47, 54 | A1 -> A2 -> A2-alt -> one of two A1-alts (locks out the other); 5 designed, 4 owned, 2 equipped | the 4 owned = A1, A2, A2-alt, A1-alt (A or B). "2 equipped" now means 2 PRIMARY; the other 2 are not idle, they are the alts |
| 50, 51 | abilities level by use; 2 modifiers equipped, per-ability trees | levels and modifiers belong to the ABILITY, not the shape - every shape shares them |
| 104-105 | one hold = traversal + attack | the keys here are Ability 2 / 3 only; Ability 1 = weapon signature (vanilla), clicks untouched |
| Input design Q3 (2026-10-08) | crouch shapes never move you ("safe near a ledge") | kept as a design rule (section 8); a crouch shape may still be stronger or cost more |

The whole idea in one line: **four abilities, two keys, four shapes.** Ability 2 / Ability 3 fire your two primaries; the shape follows
what your body is doing (walking, sprinting, in the air). Hold crouch and the same two keys fire your two alts in their crouch shape.

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **Primary** | one of the 2 abilities on Ability 2 / Ability 3 while standing, walking, sprinting or in the air |
| **Alt** | one of the other 2 owned abilities, cast with crouch held + Ability 2 / Ability 3 |
| **Walking shape** | the designed ability (class file / spec draft), cast standing or walking. Base cost / cooldown |
| **Sprinting shape** | cast while sprint is held: the "momentum" version - longer reach, placed ahead, starts on the move; may move you a little |
| **Mid-air shape** | cast while airborne >= 150 ms: the "from above" version - lands below you, forms on landing, or works while you hang |
| **Crouch shape** | the alt's only shape: the "precise / here / self" version - centred on you or placed at your feet, often a short stand-still; never moves you |
| **H** | one full-power weapon hit at the player's level (spec draft 1.1) |
| **Cost / CD** | Mana (+ Stamina where named) / cooldown. "same" = the walking shape's numbers |

Shape priority when states overlap: **mid-air > crouch > sprinting > walking** (crouch in the air is ignored, line 150). Cooldown is
PER ABILITY (one clock), whatever shape was cast; the shape only decides how long that clock is (section 8).

## 2. Warrior (tank + crowd control; Swordsmanship)

Owned 4: A1 Rallying Guard, A2 Shield Shockwave, A2-alt Iron Chain, A1-alt (Bulwark Stance or Unbreakable).

### Rallying Guard (LOCKED; base 12 Mana / 24 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | you + party within 6 blocks take 20% less damage 6 s; mobs within 8 turn to you 4 s | 12 / 24 |
| Sprinting | **Charge Rally**: picks the party circle now AND every ally you run past within 4 blocks in the next 1.5 s; taunt radius 6 | 12 / 24 |
| Mid-air | **Rally on landing**: the circle + taunt form where you land (up to 1 s later); taunt radius 10 (a shout from above) | 12 / 24 |
| Crouch (alt) | **Hold the Line**: taunt only, radius 16, 6 s; no party reduction; YOU take 10% less while they come | 8 / 18 |

### Shield Shockwave (LOCKED; base 10 / 12 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 6-block cone, stun 1.5 s, 1.0 H | 10 / 12 |
| Sprinting | **Charging Slam**: a 2-block step forward, cone 7 blocks, 1.2 H, stun 1.2 s | 12 / 12 |
| Mid-air | **Ground Pound**: a 4-block circle under your landing spot, stun 1.5 s, 1.0 H, small knock-up | 10 / 14 |
| Crouch (alt) | **Ring**: 360 degrees, 3 blocks, same stun, 0.8 H | 10 / 10 |

### Iron Chain (PROPOSED; base 12 / 14 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | chain 15 blocks, hooks the first enemy, drags it to you, stun 1 s, 0.6 H | 12 / 14 |
| Sprinting | **Meet Halfway**: you and the hooked enemy are pulled to the middle (closes the gap fast); stun 0.8 s | 12 / 14 |
| Mid-air | **Hook Down**: aimed at the ground ahead; the hooked enemy is yanked up 1 s and dropped (knock-up), 0.8 H | 12 / 16 |
| Crouch (alt) | **Anchor**: chain 20 blocks, slower drag, the enemy lands at your feet stunned 1.5 s + rooted 1 s | 12 / 16 |

### A1-alt A Bulwark Stance (PROPOSED; base 14 / 28 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 8 s stance: 50% less from the front, front projectiles blocked, you move 30% slower, allies behind you take 25% less | 14 / 28 |
| Sprinting | **Bracing Run**: 6 s, 40% front reduction, NO move slow (you keep running) | 14 / 28 |
| Mid-air | **Drop Guard**: the stance starts as you land; the landing pushes enemies within 2 blocks back 1 block | 14 / 28 |
| Crouch (alt) | **Bulwark Wall**: 10 s, 60% front, you cannot move, allies behind take 35% less | 12 / 28 |

### A1-alt B Unbreakable (PROPOSED; base 16 / 40 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | taunt 8 blocks; 5 s you cannot drop below 1 HP; at the end heal 20% of the damage taken | 16 / 40 |
| Sprinting | **Last Charge**: taunts every mob you pass within 3 blocks during the 5 s (moving taunt); end heal 15% | 16 / 40 |
| Mid-air | **Defiant Landing**: starts at landing; the first 1 s after landing you take 50% less; 4 s floor | 16 / 40 |
| Crouch (alt) | **Dig In**: 6 s floor, no taunt, you cannot move, end heal 30% | 14 / 40 |

**Combos:** Rallying Guard + Shield Shockwave (the tank set: protect, then stun); Unbreakable + Iron Chain (solo brawler: pull one,
survive). Bulwark Stance as an ALT (Bulwark Wall) is the "hold a doorway" button. **Engine risk:** taunt = clearing / setting an NPC
target (P12, UNVERIFIED); the 2-block step in Charging Slam moves the player from the server (the wand hop route, VERIFIED pattern).

## 3. Archer (crowd control + focus marker; Archery)

Owned 4: A1 Pinning Shot, A2 Rapid Fire, A2-alt Explosive Arrow, A1-alt (Arrow Rain or Hunter's Net).

### Pinning Shot (LOCKED; base 10 / 12 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | piercing arrow 30 blocks (2 enemies), 1.2 H, Rooted 2 s, Marked 6 s (+15%) | 10 / 12 |
| Sprinting | **Running Pin**: fired on the move, 24 blocks, root 2.5 s (kiting shot) | 10 / 12 |
| Mid-air | **Rain Pin**: 3 arrows fan down, root in a 3-block patch below you, each 0.6 H, Mark as usual | 12 / 12 |
| Crouch (alt) | **Steady Aim**: 40 blocks, +1 pierce, Mark 20%, you stand still 0.5 s | 10 / 14 |

### Rapid Fire (LOCKED; base 14 / 20 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 15 arrows in 3 s, each 0.5 H | 14 / 20 |
| Sprinting | **Running Fire**: 12 arrows over 3 s while you keep sprinting, wider spread | 14 / 20 |
| Mid-air | **Hover Fire**: slow-fall while the arrows go (the bow Escape rhythm), 15 arrows in 2.5 s | 16 / 20 |
| Crouch (alt) | **Braced**: 15 arrows in 2 s, +10% arrow damage, you cannot move | 14 / 22 |

### Explosive Arrow (LOCKED; base 12 / 14 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | your next charged shot does 2x in a 4-block explosion | 12 / 14 |
| Sprinting | **Quick Fuse**: your next shot of ANY draw explodes, 1.5x, 3 blocks | 10 / 12 |
| Mid-air | **Mortar**: the next charged shot lobs high and lands as a 5-block explosion, 2x, knock-up | 12 / 16 |
| Crouch (alt) | **Set Charge**: the next charged shot sticks and explodes 1 s after impact, 2.5x, 4 blocks | 12 / 16 |

### A1-alt A Arrow Rain (PROPOSED; base 16 / 20 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 6-block area where you aim, 3 s, 2.0 H total, Slowed 30%; still inside after 2 s = Rooted 1.5 s + Marked | 16 / 20 |
| Sprinting | **Trailing Rain**: the rain follows 4 blocks behind you for 3 s (covers a retreat) | 16 / 20 |
| Mid-air | **Overhead Rain**: centred below you, 7 blocks, starts 0.5 s sooner | 16 / 22 |
| Crouch (alt) | **Kneeling Volley**: 1 s stand-still, 8-block area, 4 s, slow 40% | 20 / 24 |

### A1-alt B Hunter's Net (PROPOSED; base 14 / 18 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | net bursts into a 4-block root zone 3 s, 0.5 H, Marked 8 s | 14 / 18 |
| Sprinting | **Snare Line**: the net lands behind you as a 2 x 6 strip (trips pursuers) | 14 / 18 |
| Mid-air | **Drop Net**: falls straight down, 5 blocks, root 3.5 s | 14 / 20 |
| Crouch (alt) | **Set Trap**: placed at your feet, invisible, arms after 1 s, fires when an enemy steps in (lasts 20 s) | 12 / 18 |

**Combos:** Pinning Shot + Rapid Fire (root, then unload - 64% of weapon DPS, the draft's worst pair, still under 80%); Hunter's Net +
Explosive Arrow (bunch them, blow them up). Set Trap as an alt makes a crouching Archer a trapper. **Engine risk:** on 0.6.8 the
crossbow reload sits on Ability 3 (K13, UNVERIFIED) - Archers may get line 2 only through the hotbar item until 0.7; Hover Fire needs
a slow-fall the bow Escape already plans (SkyyArmory, UNVERIFIED until it ships).

## 4. Mage (burst damage, glass cannon; Sorcery; H = a charged staff shot)

Owned 4: A1 Meteor, A2 Mana Barrier, A2-alt Frost Nova, A1-alt (Starfall or Arcane Beam).

### Meteor (LOCKED; base 30 / 14 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | pick a spot within 25 blocks; after 1 s a meteor hits a 4-block area for 3.0 H | 30 / 14 |
| Sprinting | **Comet**: lands 1 s later where you are RUNNING to (your spot + 6 blocks forward), 3 blocks, 3.0 H | 30 / 14 |
| Mid-air | **Under Me**: lands where you will land, timed with your landing (no extra delay), 4 blocks | 30 / 16 |
| Crouch (alt) | **Meteor on Me**: centred on you, 0.5 s delay, 5 blocks, 2.5 H, you take none of it | 26 / 14 |

### Mana Barrier (LOCKED; base 20 / 30 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | dome placed where you look (<= 8 blocks), 12 s; inside it damage drains Mana instead of Health (1 per 2 HP) | 20 / 30 |
| Sprinting | **Barrier Ahead**: dome placed 6 blocks ahead on your path (you run into it) | 20 / 30 |
| Mid-air | dome placed at your landing spot | 20 / 30 |
| Crouch (alt) | **Pocket Dome**: 4-block dome centred on you, 10 s, 2.5 HP per Mana | 18 / 28 |

### Frost Nova (PROPOSED; base 24 / 22 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | freeze enemies within 5 blocks 2 s (a hit breaks it after 1 s, 0.5 H), then Chill 3 s; 1.0 H | 24 / 22 |
| Sprinting | **Frost Wake**: a freezing strip 2 x 8 behind you for 3 s, freeze 1.5 s | 24 / 22 |
| Mid-air | **Frost Drop**: the nova fires on landing, 6 blocks, freeze 2 s, 1-block push | 24 / 24 |
| Crouch (alt) | **Deep Freeze**: 4 blocks, freeze 3 s, hits do not break it for 2 s | 26 / 24 |

### A1-alt A Starfall (PROPOSED; base 36 / 18 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 12 stars over 3 s on a 6-block area you aim at, each 0.3 H | 36 / 18 |
| Sprinting | **Star Trail**: the stars fall along your path for 3 s (a line behind you) | 36 / 18 |
| Mid-air | **Starfall Below**: centred under you, 7 blocks, 12 stars in 2 s | 36 / 20 |
| Crouch (alt) | **Star Shower**: centred on you, 6 blocks, 16 stars over 4 s, you cannot move | 40 / 22 |

### A1-alt B Arcane Beam (PROPOSED; base 30 / 18 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | channel a 20-block beam up to 3 s, ramp 1x -> 3x (0.5 / 1.0 / 1.5 H per second) | 30 / 18 |
| Sprinting | **Sweep Beam**: 15 blocks, 2 s, flat 1.5x, wider, you keep moving | 28 / 18 |
| Mid-air | **Beam Down**: aimed below, 12 blocks, 2 s, you slow-fall while channelling | 30 / 20 |
| Crouch (alt) | **Focused Beam**: 25 blocks, 4 s, ramp to 3.5x, you cannot move | 34 / 22 |

**Combos:** Meteor + Mana Barrier (the locked pair: burst + survive); Arcane Beam + Frost Nova (freeze, then beam the frozen crowd).
Pocket Dome as an alt = the "oh no" button while crouch-sneaking near a ledge. **Engine risk:** Under Me needs the landing point
predicted (the Meteor delay becomes "when onGround flips", K11 / P-tick UNVERIFIED); channels (Beam) are engine kind CHANNEL (engine
spec 5, unbuilt); slow-fall while channelling reuses the Levitate / bow Escape mechanism (UNVERIFIED cost).

## 5. Priest (healer + protector; Divinity; heals in % of max Health)

Owned 4: A1 Sacred Heal, A2 Shield Bubble, A2-alt Guardian Spirit, A1-alt (Sanctuary or Martyr's Grace).

### Sacred Heal (LOCKED; base 25 / 14 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | instant heal 25% max Health for everyone within 9 blocks (Priest 30%) + HoT 40% of it over 4 s | 25 / 14 |
| Sprinting | **Running Blessing**: a 6-block circle travels with you for 2 s and heals everyone it touches once, 20% + HoT | 25 / 14 |
| Mid-air | **Beacon**: the circle drops where you land, radius 10 | 25 / 14 |
| Crouch (alt) | **Kneel**: 1 s channel, heal +20%, HoT doubled, you stand still | 28 / 16 |

### Shield Bubble (LOCKED; base 28 / 24 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | place a 6-block bubble where you look (<= 8), 12 s, HP 100% of your max Health, 4 heal pulses at 75 / 50 / 25 / 0% | 28 / 24 |
| Sprinting | **Bubble Ahead**: placed 6 blocks ahead on your path | 28 / 24 |
| Mid-air | placed below you on landing | 28 / 24 |
| Crouch (alt) | **Around Me**: centred on you, 5 blocks, HP 110% (the Follow modifier still makes it move) | 28 / 26 |

### Guardian Spirit (PROPOSED passive, line 145-146; no base press)
| Shape | What changes | Cost / CD |
|---|---|---|
| All primary shapes | **the passive is always on while owned** (30-block aura, save at 30% Health, Mana per save). A press as a primary = **Spirit Call** (PROPOSAL): the ally you look at within 60 blocks is watched 10 s - their next lethal hit is saved even outside the aura (normal doubling rules) | 15 / 20 |
| Crouch (alt) | **Spirit Pulse** (PROPOSAL): resets the doubling counter of the ally you look at (their next save is a 12 s one again) | 20 / 60 |

Default if Skyy wants no press at all: the key shows "Passive - always on" once (input design 3), and the Priest's effective primaries
are the other 3. Question 4.

### A1-alt A Sanctuary (PROPOSED; base 35 / 28 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | holy zone 12 s, 8 blocks, placed under you: allies heal 5% max Health per second, take 10% less | 35 / 28 |
| Sprinting | **Pilgrim's Path**: placed 5 blocks ahead | 35 / 28 |
| Mid-air | placed at your landing spot | 35 / 28 |
| Crouch (alt) | **Inner Sanctum**: 5 blocks centred on you, 7% per second, 15% less damage, 10 s | 35 / 30 |

### A1-alt B Martyr's Grace (PROPOSED; base 30 / 18 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 75% heal on the lowest ally within 30 blocks, chains -15 per jump (party first, the Priest counts as party) | 30 / 18 |
| Sprinting | **Grace in Motion**: the FIRST target is the ally you look at (if any), then lowest-first | 30 / 18 |
| Mid-air | **Descent**: the chain starts from YOU, then lowest-first (a self-save while escaping) | 30 / 18 |
| Crouch (alt) | **Martyr's Vow**: 1 s channel, first heal 90%, drop -20 (90 / 70 / 50 / 30 / 10) | 34 / 20 |

**Combos:** Sacred Heal + Shield Bubble (the locked pair); Martyr's Grace + Sanctuary is not possible (both are A1-alts - one is
owned). Kneel as an alt = the big heal when the party stands still. **Engine risk:** Running Blessing is a short moving zone (engine
kind ZONE with Follow, E3); Spirit Call / Spirit Pulse need the Guardian Spirit save counters per target (engine 7.1, memory) -
cheap once the passive exists; the lethal-damage hook order is P5 (UNVERIFIED).

## 6. Berserker (party damage buffer + sustained melee; Fury)

Owned 4: A1 Enrage, A2 Whirlwind, A2-alt Earthsplitter, A1-alt (Blood Frenzy or Warlord's Banner).

### Enrage (LOCKED; base 14 / 30 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | players within 8 + party within 16 picked ONCE; damage +10 -> +20% over 10 s, holds 5 s; you x2 | 14 / 30 |
| Sprinting | **War Charge**: picked now AND anyone you pass within 4 blocks in the next 2 s | 14 / 30 |
| Mid-air | **War Leap**: the buff starts when you land, allies picked then, ranges +2 | 14 / 30 |
| Crouch (alt) | **Lone Rage**: self only, peak +10 points, holds 8 s | 10 / 26 |

### Whirlwind (LOCKED; base 12 / 14 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | spin 3 s, hit everything within 3 blocks every 0.5 s (0.5 H a tick), heal 10% of the damage | 12 / 14 |
| Sprinting | **Cyclone Charge**: spin at sprint speed 2.5 s, radius 2.5, wide turns only | 12 / 14 |
| Mid-air | **Spinning Drop**: the spin starts on landing with a 1.0 H slam | 12 / 16 |
| Crouch (alt) | **Grinder**: no movement, ticks every 0.4 s, radius 3.5, 3 s | 12 / 16 |

### Earthsplitter (PROPOSED; base 14 / 12 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 12-block shockwave line, 2.0 H, knock-up 1 s; +1% per 1% Health missing (cap +50%) | 14 / 12 |
| Sprinting | **Running Split**: 16 blocks, narrower, 1.8 H | 14 / 12 |
| Mid-air | **Crater**: a 5-block circle under your landing, 2.0 H, knock-up 1 s | 14 / 14 |
| Crouch (alt) | **Fissure**: 1 s wind-up, 8 blocks, 2.4 H, hit enemies Slowed 2 s | 16 / 14 |

### A1-alt A Blood Frenzy (PROPOSED toggle; 1 Mana + 0.5 Stamina per swing, 0.2 + 0.1 per second)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | toggle on (0 stacks) / off; 25 stacks max, 6 s decay; aura buffs allies half | per swing / 10 s before re-toggle |
| Sprinting | **Charging Frenzy**: toggles on at 3 stacks (you charged in) | same |
| Mid-air | toggles on at landing; the landing counts as 2 stacks | same |
| Crouch (alt) | **Blood Bank**: toggles on with half the stacks you had when it last ended (within 20 s); aura 6 / party 12 | same |

A toggle that is ON turns OFF on any press (any shape), free. Shapes only change how it turns on.

### A1-alt B Warlord's Banner (PROPOSED; base 40 Mana / 40 s after the fall)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | plant at your feet: 30 s, 12 blocks, +8 / 12 / 16% damage + defence + attack speed; kills extend; falls when you leave | 40 / 40 |
| Sprinting | **Vanguard Banner**: planted 6 blocks ahead | 40 / 40 |
| Mid-air | planted where you land, radius +2 | 40 / 40 |
| Crouch (alt) | **Rooted Banner**: 10 blocks, 40 s; leaving range PAUSES your own buff instead of felling it | 45 / 40 |

**Combos:** Enrage + Whirlwind (the locked pair: buff, then spin); Blood Frenzy + Earthsplitter (always-on frenzy, low-Health
nukes). Grinder as an alt = the "stand in the door" spin. **Engine risk:** the sprint-speed spin and the landing slam need the
player's move state read mid-channel (K3 at cast only is enough: the shape is fixed at the press); kill events inside the banner
(engine 10, UNVERIFIED P11 banner model).

## 7. Monk (self-speed disruptor; class skill OPEN; costs Mana + Stamina)

Owned 4: A1 Flowing Form, A2 Palm Strike, A2-alt Cyclone Kick, A1-alt (Hundred Fists or Still Water).

Monk note: crouch in the AIR is the free air jump and the Plunge Punch (line 150). A Monk's alts therefore work only on the ground,
like every class; in the air the keys always fire the primaries' mid-air shapes.

### Flowing Form (LOCKED; base 6 Mana + 0.5 Mana / 0.3 Stamina per s; CD 40 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 30 s aura 5 blocks: enemies Awed; every hit = 1 combo stack (max 20, 5 s decay), +2% move / +1.5% attack per stack | 6 + drain / 40 |
| Sprinting | **Flow Sprint**: starts at 2 stacks; sprinting costs no Stamina for the first 3 s | same |
| Mid-air | starts on landing; your first bound or air jump after it is free | same |
| Crouch (alt) | **Centred**: starts with 3 stacks, aura 4 blocks, drain -25% | 6 + drain / 40 |

### Palm Strike (LOCKED; base 8 / 6 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | single-target strike, stun 0.75 s + knockback 4 blocks, 1.2 H | 8 / 6 |
| Sprinting | **Rushing Palm**: a 2-block step in, knockback 6, stun 0.5 s | 8 / 6 |
| Mid-air | **Falling Palm**: strikes down; the enemy is knocked DOWN (stun 1 s), no knockback | 8 / 7 |
| Crouch (alt) | **Rooting Palm**: no knockback, stun 1.25 s, applies Awe (keep them for the combo) | 8 / 6 |

### Cyclone Kick (PROPOSED; base 10 / 8 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | spinning kick: everything within 3 blocks takes 0.8 H and is pushed 5 blocks | 10 / 8 |
| Sprinting | **Sweeping Kick**: a forward arc 4 blocks, push 6, you keep your momentum | 10 / 8 |
| Mid-air | **Dropping Kick**: lands as a 4-block ring, push 5 + small knock-up | 10 / 9 |
| Crouch (alt) | **Leg Sweep**: 3 blocks, no push, enemies knocked down (stun 1 s) | 10 / 9 |

### A1-alt A Hundred Fists (PROPOSED; base 8 + drain / 40 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | Flowing Form where every 10th hit releases a shockwave on all Awed enemies (1.0 H, max one per 8 s) | 8 + drain / 40 |
| Sprinting | starts at 2 stacks; the first shockwave comes at 8 hits | same |
| Mid-air | starts on landing; the landing counts as 1 combo | same |
| Crouch (alt) | **Tempest Palms**: a shockwave every 12th hit, 1.3 H, radius -1 | same |

### A1-alt B Still Water (PROPOSED; base 18 / 25 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | 10 s stance: deflect front projectiles, counter melee hits (1.0 H each), every counter adds Awe | 18 / 25 |
| Sprinting | **Flowing Water**: 6 s, counters only (no deflect), you keep moving | 16 / 22 |
| Mid-air | **Falling Water**: the stance starts on landing; the landing counters everything within 2 blocks (0.5 H) | 18 / 25 |
| Crouch (alt) | **Deep Still**: 12 s, 360-degree deflect, counters 1.3 H, you cannot move | 20 / 28 |

**Combos:** Flowing Form + Palm Strike (the locked pair: speed up, control one); Still Water + Cyclone Kick (counter, then clear the
ring). Palm Strike + Hundred Fists is the draft's hottest Monk pair (72%, passes). **Engine risk:** Awe = clearing an NPC target
(P12, UNVERIFIED); the Monk moves already read crouch in the air (SkyyArmory 0.1.12 round) - the stance resolver must let that
through untouched (K11 UNVERIFIED for the first 100 ms of a vault).

## 8. Assassin (priority killer + debuffer; Assassination)

Owned 4: A1 Cloak + First Strike, A2 Toxin, A2-alt God Killer, A1-alt (Shadow Clone or Vanishing Act).

### Cloak + First Strike (LOCKED; base 14 / 30 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | invisible 8 s (breaks on attack); First Strike: next hit within 10 s gets +100% crit chance | 14 / 30 |
| Sprinting | **Dash Cloak**: cloak 6 s + 20% move speed for 3 s | 14 / 30 |
| Mid-air | **Silent Landing**: cloak 8 s, no fall damage, no landing sound | 14 / 30 |
| Crouch (alt) | **Still Shadow**: cloak 11 s while you stay still (moving drops it to the normal 8 s); First Strike +20% crit damage | 12 / 30 |

### Toxin (LOCKED; base 12 / 16 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | vial thrown where you look (<= 20): 4-block poison cloud 5 s, Poison 0.25 H/s + Weakened 15% | 12 / 16 |
| Sprinting | **Lobbed Vial**: thrown 28 blocks, cloud 3.5 blocks | 12 / 16 |
| Mid-air | **Drop**: cloud below you, lands 0.3 s earlier | 12 / 16 |
| Crouch (alt) | **Pool**: cloud at your feet, 5 blocks, 6 s | 12 / 18 |

### God Killer (LOCKED; base 14 / 45 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | next attack on a boss / mini-boss within 12 s does 2x, 3x on a backstab; stacks with First Strike | 14 / 45 |
| Sprinting | **Hunter's Rush**: window 8 s, +15% move speed during it | 14 / 45 |
| Mid-air | **Death from Above**: the empowered hit also counts as a backstab if it lands while you fall | 14 / 45 |
| Crouch (alt) | **Patient Kill**: 1 s stand-still to arm, window 20 s | 14 / 50 |

### A1-alt A Shadow Clone (PROPOSED; base 20 / 35 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | cloak + a decoy at your spot that mobs attack 5 s; it bursts 2.0 H in 4 blocks | 20 / 35 |
| Sprinting | **Decoy Run**: the decoy keeps running your way for 3 s | 20 / 35 |
| Mid-air | the decoy appears where you land | 20 / 35 |
| Crouch (alt) | **Patient Clone**: decoy at your feet 8 s, NO cloak, burst 2.5 H | 18 / 35 |

### A1-alt B Vanishing Act (PROPOSED; base 16 / 28 s)
| Shape | What changes | Cost / CD |
|---|---|---|
| Walking | instant 3 s cloak + 4-block smoke: enemies inside lose you 2 s, Slowed 25%; First Strike as A1 | 16 / 28 |
| Sprinting | **Smoke Trail**: a 2 x 8 smoke strip behind you | 16 / 28 |
| Mid-air | **Smoke Drop**: smoke where you land, 5 blocks | 16 / 28 |
| Crouch (alt) | **Ambush Smoke**: 4-block smoke, cloak 5 s as long as you stay inside it | 16 / 30 |

**Combos:** Cloak + God Killer (the boss killer: cloak, Shadow Step, triple-crit strike); Vanishing Act + Toxin (smoke + poison,
the debuffer). Patient Kill as an alt = arm it while sneaking up. **Engine risk:** decoys need an NPC-target API (P12, UNVERIFIED);
"lands while you fall" = the damage hook reading the attacker's onGround flag (K3 state names, UNVERIFIED).

## 9. Shared rules (all classes)

| Rule | Design |
|---|---|
| Picking primaries | on the class page / tree page (inline, vanilla look, `tools/skyyui.py`): the 4 owned abilities are listed; "Primary" toggles on exactly 2; the other 2 become the alts automatically (no empty alt slot). Only OUT OF COMBAT (`skill:fn:combat` = 0); in combat the toggles are greyed out with "Leave combat first". Saved per profile (`eq1`, `eq2` in the engine's abilities file; `alt1`, `alt2` derived) |
| Order on the keys | Ability 2 = the first primary, Ability 3 = the second; crouch + Ability 2 = the first alt, crouch + Ability 3 = the second. The page lets you swap the order with one click (the same ability never changes key by accident) |
| 3 owned abilities only (before the A1-alt unlock) | 2 primaries + 1 alt; crouch + the other key shows "No alt yet" once |
| Which shape fires | read at the PRESS, never re-read during the cast: airborne >= `abil.airMinMs` (150 ms) = mid-air; else crouch held >= `abil.crouchMinMs` (100 ms) = the ALT's crouch shape; else sprint held = sprinting; else walking. Crouch in the air is ignored (movement owns it) |
| Cooldown | one clock per ABILITY; the shape sets its length; a primary cast and an alt cast of the same ability cannot overlap (one ability is either primary or alt anyway) |
| Costs | per shape (section tables); refusals (no Mana, on cooldown, wrong weapon) cost nothing, fail sound + "Ready in 4 s" at most once a second |
| Levels / modifiers | belong to the ability: every shape counts uses, every shape gets the 2 equipped modifiers. A shape that cannot use a modifier (Follow on a self-centred crouch dome) ignores it |
| Crouch shapes never move you | design rule: sneaking near a ledge and pressing a key is always safe. A crouch shape may be stronger, longer or cost more |
| Mid-roll cast | the roll is the sprint PRESS (SkyySkills). Sprint + Ability 2 together = roll AND cast: the shape is **sprinting** if sprint is still held at the press, else **walking** (default; Q3). The roll is never cancelled by the cast; the cast never cancels the roll. If K4 / K11 show the Ability press is swallowed during the roll, mid-roll cast is dropped (line 156), not emulated |
| HUD | SkyyHud Abilities widget (engine 12 H2): **two rows** = the primaries with cooldown bars; while crouch is held the rows switch to the alts (names + bars), so the player always sees what the keys do right now. Alts on cooldown while not crouching = a small dot after the primary's name. On 0.7 the vanilla rune HUD shows the 2 primaries only (2 mirrored slots); alts stay in the widget (Q5) |
| First-use hints | per owned ability, once: "Press your Use Ability 2 key: Meteor" / "Sprint + key: Comet" / "In the air: Under Me" / "Crouch + key: Meteor on Me" (one per shape over the first casts; the hints name the ACTION since the server cannot read binds) |
| Toggles (Blood Frenzy) | the shape only changes how it turns ON; any press turns it OFF |
| Passives (Guardian Spirit) | always on while owned, primary or alt; a press follows section 5 (Q4) |
| Server Setup rows | `abil.shapes` (on / off), `abil.shapes.sprint`, `abil.shapes.air`, `abil.crouchMinMs` 100, `abil.airMinMs` 150, `abil.rollCast` (on; auto-off if the probe fails), and per shape `ab.<Ability>.<shape>.mana / .stamina / .cooldown` (generated from the tables; category abilx, live). Player `/settings`: sprint shapes on / off, mid-air shapes on / off, hints |

## 10. Build order

| Step | Classes / abilities | Why first |
|---|---|---|
| S1 (engine E1) | the shape resolver (press -> shape) + the primary / alt data per profile; walking shape only, all 4 owned abilities on the keys | nothing lands without it |
| S2 | **Mage + Priest**: Meteor, Mana Barrier, Sacred Heal, Shield Bubble - all 4 shapes each | the old default: casters test "on me" / "below me" / "ahead" shapes; both are already the engine's first abilities (E1 / E3) |
| S3 | Monk + Assassin: Flowing Form, Palm Strike, Cloak, Toxin | crouch = precise; the Monk's crouch-in-air collision is tested here |
| S4 | Warrior + Berserker: Rallying Guard, Shield Shockwave, Enrage, Whirlwind | taunt / NPC target API (P12) decides the Warrior |
| S5 | Archer: Pinning Shot, Rapid Fire | last: the crossbow Ability 3 conflict clears on 0.7 (K13) |
| S6+ | the A2-alts, then the A1-alts (2 per class), class by class | they unlock later in play anyway |

Each step = a lean SkyyClasses version when no new engine kind is needed (the shapes are data rows + small executor branches); a full
round where a step adds a kind (CHANNEL for Arcane Beam, moving ZONE for Running Blessing).

## 11. Questions for Skyy (each with a recommended default)

| # | Question | Recommended default |
|---|---|---|
| 1 | Sprinting shapes may move you a little (Charging Slam's 2-block step, Rushing Palm, Meet Halfway)? Crouch shapes never do. | **[Yes - small steps only, never a full dash; crouch never moves you]** |
| 2 | Cost / cooldown per shape as in the tables (most "same", stronger or bigger shapes +2-4 Mana / +2 s)? | **[Yes; every number a live row]** |
| 3 | Mid-roll cast: shape = sprinting if sprint is held at the press, else walking? | **[Yes]** |
| 4 | Guardian Spirit as a passive: no press at all, or the proposed Spirit Call (primary press) + Spirit Pulse (crouch)? | **[Passive only for the first build; Spirit Call / Pulse as a later add if the Priest feels one key short]** |
| 5 | HUD: 2 rows that switch to the alts while crouch is held (one widget), or 4 rows always? | **[2 rows that switch; 4 rows as a /settings option]** |
| 6 | Order on the keys: the page lets you swap which primary is Ability 2 / 3 (and which alt)? | **[Yes, one click, out of combat]** |
| 7 | Before the A1-alt unlock a character owns 3: 2 primaries + 1 alt, the other crouch key says "No alt yet"? | **[Yes]** |
| 8 | Toggle (Blood Frenzy): shapes change only how it turns on; any press turns it off? | **[Yes]** |
| 9 | Build order Mage + Priest -> Monk + Assassin -> Warrior + Berserker -> Archer (4 shapes of A1 + A2 first, alts' shapes later)? | **[Yes]** |
| 10 | Hotbar ability items (input design section 2): still wanted now that crouch doubles the keys? | **[Keep them for later; a mirror item casts the WALKING shape only]** |

## For the local session (UNVERIFIED)

- All of SkyyKeyProbe K1-K15 (`research/cloud/Ability-Input-Design.md` 6). This spec leans most on **K3** (which movement states the
  press carries: crouching, sprinting, jumping, falling, onGround), **K4** (do Ability 2 / 3 fire while crouching, sprinting, in the
  air, during the roll), **K11** (onGround during the roll and the first 100 ms of a jump / vault - decides `abil.airMinMs` and whether a
  Monk vault counts as mid-air), **K12** (held key repeat), **K13** (0.6.8 crossbow reload on Ability 3), **K15** (0.7 rune route exposes
  the same states). Skyy 2026-10-08: the key probe session waits until Hytale 0.7 - no rush.
- Engine probes that shapes add weight to: **P12** (clear / set an NPC target: taunts, Awe, decoys), **P5** (lethal hook order: Guardian
  Spirit), **P11** (banner entity), the landing-point prediction for "on landing" shapes (Under Me, Beacon, Crater: the executor waits
  for onGround to flip, with a 2 s timeout -> the cast fires where you are).
- Slow-fall while casting (Hover Fire, Beam Down) reuses whatever the bow Escape / Levitate build ships (SkyyArmory) - confirm the
  mechanism is callable from SkyyClasses through the bridge.
- `acro.doubleJump.trigger` on Skyy's live SkyySkills file (`jump` vs `crouch`) - decides how often crouch-in-air collides.
- The shape rows multiply the per-ability Server Setup rows by 4 (35 abilities x 4 shapes x 3 numbers = 420 rows): keep them in the
  Advanced category (abilx) and generate them from this file's tables, or store a per-shape DELTA (same / +2 / +2 s) to keep the page
  short - a `tools/skyycfg.py` call.
- Every number here is a placeholder in the spec draft's units (H, % max Health); no budget was recomputed for the sprint / air / crouch
  shapes - they sit within +-20% of the walking shape by design, so the draft's section 5 checks still hold at the worst case.
