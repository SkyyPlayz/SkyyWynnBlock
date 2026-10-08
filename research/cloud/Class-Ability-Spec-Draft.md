# Class ability spec draft - numbers for all 7 classes

Cloud draft, 2026-10-06. Paper numbers only; nothing built. It replaces the older `Class-Abilities-Draft.md` (which used 4 Wynncraft-style spells; Skyy's 2026-10-04 locks changed the structure).
Inputs: `research/classes/*.md` (the 7 class files; LOCKED rows are kept exactly as written, the *proposed* rows are improved), `research/classes/README.md` (rules + modifier pool),
`docs/answered/classes.md` (Mana pools, wand / staff Mana, traversal costs). Companion drafts: `Modifier-Pool-Spec.md`, `Class-Tree-Paths.md`, `Soul-Orb-Spec.md` (written next).

**Refresh 2026-10-08 (cloud):** brought in line with every 2026-10-07 line of `docs/answered/classes.md` (lines 111-148; cited below as "L<n>"), balance tables recomputed with python3. Change list: `research/cloud/Ability-Refresh-1007.md`.

Labels as in the class files: 🟢 locked · 🔵 proposed · 🟠 open. **All numbers are placeholders until a playtest**; they are written so one row changes one number.

## 1. The system in one page

| Rule | Value | Source |
|---|---|---|
| Abilities per class | 5 designed (A1, A1-alt x2, A2, A2-alt), a character owns 4, **2 equipped** (the two rune lines) | locked 2026-10-04 |
| Ability level | **1 to 15**, "levels by use" | proposal (this spec) |
| Points | 1 point per level from Lv 2 = **14 points** per ability | proposal |
| Modifiers | 4 per ability (**5 on the 11 abilities Skyy gave Echo / Floor / Follow on 2026-10-07**: Meteor, Mana Barrier, Sacred Heal, Martyr's Grace, Shield Bubble, Blood Frenzy, Warlord's Banner, Whirlwind, Still Water, Palm Strike, God Killer), **2 equipped**, no doubling; each unlocked + levelled **per ability** | locked (L111-L145) |
| Modifier level | 1 to 5: Lv 1 costs 1 point (unlock), Lv 2-3 cost 1 each, Lv 4-5 cost 2 each = **7 points to max one** | proposal |
| So | 14 points = **exactly two modifiers maxed**, or three half-way; you cannot max all four (the choice is the build). Swapping which 2 are equipped is free; points stay where they were spent | proposal |
| Uses to level | uses needed for level n = `round(4.5 x n^1.5)`: Lv 2 13, Lv 3 23, Lv 5 50, Lv 10 142, Lv 15 261 (**total 1,570 uses**; about 12-15 hours of normal play with the ability equipped) | proposal |
| What counts as a use | only uses that **do something** (hit an enemy, heal a hurt ally, absorb damage, taunt a mob, root/stun an enemy ...); max 1 counted use per ability per 3 s; spam at nothing earns nothing | locked intent |
| Class tree | separate layer: Wynncraft-style paths that change HOW an ability works (`Class-Tree-Paths.md`) | locked |

### 1.1 Reference units

| Unit | Meaning |
|---|---|
| **H** | one full-power hit of the class weapon at the player's level (martial: a full swing / full draw; Mage: a charged staff shot; Priest: a charged wand shot). All damage numbers below are multiples of H, so they scale with gear level automatically |
| Weapon DPS | 1 H per second for martial classes (the budget check below) |
| Mana pools | Mage 30 + 10 per Sorcery level; Priest 30 + 5 per Divinity level (LOCKED); others 10 base (+ Overall Level 0.2 each) today |
| Mana regen | 5 per second out of combat, **50% in combat**, a 6 s pause after taking damage (live) |
| Traversal costs | Mana : Stamina 2 : 1 for magical ones, more Stamina for physical (LOCKED 2026-10-05); not changed here |

### 1.2 Mana for the five physical-ish classes (a finding)
Warrior, Archer, Berserker, Monk and Assassin have only about 10 Mana, so any ability at 10+ Mana cannot be cast twice in a row and a level-1 character cannot cast the 14-24 Mana abilities below at all.
**Proposal (needs Skyy):** the same kind of per-class-skill row Mage and Priest already have: **+2 Mana per class skill level** for these five (a Warrior at Swordsmanship 20 has 50 Mana), plus costs in this spec stay small (8-20). Without it, give these classes Stamina costs instead of Mana (also a valid answer; Stamina is only about 12).

## 2. Per-ability tables

Columns: **Cost** (Mana, plus Stamina where noted), **CD** (cooldown), **Base** (what it does at Lv 1), **Per level** (the small gain each ability level adds; the **cap** says where it stops so no value runs away), **At Lv 15**.
Level gains are written to add up to about **+28%** of the ability's main effect at Lv 15 (see the power ledger in section 11).

### 2.1 Warrior (Swordsmanship; tank + crowd control)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Rallying Guard** | 12 Mana / 24 s | You + party within 6 blocks take **20% less damage** for 6 s; mobs within 8 blocks turn to attack you for 4 s | +1% reduction (**cap 30% at Lv 11**); Lv 12-15: +0.25 s duration each | 30% for 7 s (effective HP x1.43 vs x1.25 at Lv 1 = +14%) |
| 🔵 **A1-alt A Bulwark Stance** | 14 / 28 s | 8 s: **50% less damage from the front**, front projectiles blocked; you move 30% slower; allies right behind you take 25% less | front reduction +1% (cap 60% at Lv 11); slow -0.7% (30% -> 20%); allies +0.5% | 60% front, 20% slow, 32% behind |
| 🔵 **A1-alt B Unbreakable** | 16 / 40 s | Taunt within 8 blocks; for 5 s you **cannot drop below 1 HP**; at the end heal 20% of the damage you took | end heal +1% (to 34%); duration +0.1 s | 34% heal, 6.4 s |
| 🟢 **A2 Shield Shockwave** | 10 / 12 s | 6-block cone, stun **1.5 s**, one weapon hit (1.0 H) | damage +3%, stun +0.03 s | 1.42 H, 1.9 s |
| 🔵 **A2-alt Iron Chain** | 12 / 14 s | Chain 15 blocks: hooks the first enemy, drags it to you, stuns **1.0 s**, 0.6 H | damage +3%, stun +0.02 s | 0.85 H, 1.3 s |

### 2.2 Archer (Archery; crowd control + focus marker)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Pinning Shot** | 10 / 12 s | Piercing arrow (30 blocks, hits up to 2 enemies): 1.2 H, **Rooted 2 s**, **Marked 6 s** (+15% damage taken from everyone) | damage +2%, Mark +1% (**cap 25% at Lv 11**), root +0.02 s; Lv 12-15: Mark +0.3 s | 1.54 H, Mark 25% for 7.2 s, root 2.3 s |
| 🔵 **A1-alt A Arrow Rain** | 16 / 20 s | 6-block area for 3 s, total 2.0 H per enemy standing in it, enemies **Slowed 30%**; still inside after 2 s: **Rooted 1.5 s + Marked** | damage +2%, slow +0.5% | 2.6 H, slow 37% |
| 🔵 **A1-alt B Hunter's Net** | 14 / 18 s | Net bursts into a **4-block root zone** for 3 s, 0.5 H, everything caught **Marked 8 s** (10%) | Mark +0.7% (cap 20%), zone +0.05 s | Mark 20%, 3.7 s |
| 🟢 **A2 Rapid Fire** | 14 / 20 s | **15 arrows in 3 s**, each 0.5 H (7.5 H total, 4.5 H more than normal shooting) | arrow damage +2% | 0.64 H each |
| 🟢 **A2-alt Explosive Arrow** | 12 / 14 s | Your next charged shot does **2x** in a 4-block explosion | multiplier +0.03 (2.0 -> 2.4) | 2.4x |

### 2.3 Mage (Sorcery; burst damage, glass cannon; H = a charged staff shot, 10 Mana)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Meteor** | 30 Mana / 14 s | Pick a spot within 25 blocks; after 1 s a meteor hits a **4-block area** for **3.0 H**; **Echo modifier** (L111): a second, weaker meteor on the same spot 1 s later | +2% damage | 3.84 H (Echo 5: +1.15 H) |
| 🔵 **A1-alt A Starfall** | 36 / 18 s | For 3 s, **12 stars** fall on a 6-block area, each 0.3 H (about 4 stars hit one enemy = 3.6 H); more total damage, spread out | +2% damage | 4.6 H |
| 🔵 **A1-alt B Arcane Beam** | 30 / 18 s | Channel a 20-block beam up to 3 s; damage ramps **1x -> 3x** (0.5, 1.0, 1.5 H per second = 3.0 H), single-target | +2% damage, ramp start +1% | 3.84 H |
| 🟢 **A2 Mana Barrier** | 20 / 30 s | **12 s** (L112: "at least 12 seconds"; Duration+ adds on top), a **placed DOME on the ground** (L113); while you stand inside, damage you take **drains Mana instead of Health** (1 Mana per 2 HP, L112); ends early at 0 Mana; **Ward** extends the protection to allies inside (small shield, L113); **Follow** modifier / skill-tree upgrade = the dome moves with you (L113); look: faint mostly-transparent tint + soft brighter rim, never blocks the view or flashes (L114). Uptime 12 / 30 s = 40% | ratio +0.05 HP per Mana (2.0 -> 2.7); **absorbs at most 100% of your max Health per cast** | 2.7 HP per Mana |
| 🔵 **A2-alt Frost Nova** | 24 / 22 s | **Freeze** enemies within 5 blocks 2 s (a hit breaks it after 1 s: 0.5 H), then **Chill** 3 s; 1.0 H on freeze | damage +2%, freeze +0.03 s | 1.9 H total, 2.4 s freeze |
Note: Mage Mana scale (+10/Sorcery level) makes 30-36 Mana a clear but affordable cost; at Sorcery 1 the pool is 40.

### 2.4 Priest (Divinity; healer + protector; heals as % of max Health)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Sacred Heal** | 25 Mana / 14 s | **Instant heal** for everyone within 9 blocks: **25% max Health** (the Priest heals themself 20% more = 30%); plus a heal-over-time of **40% of the instant heal over 4 s** | instant +0.5% of max Health, HoT % +0.5 points, HoT duration +0.05 s (the three upgrade separately in the tree) | 32% (38% Priest), HoT 47% over 4.7 s |
| ↳ Sacred Heal **Echo** (L141) | - | a second, weaker **instant** heal pulses 1 s later in the same circle (no second HoT) | Echo level: stronger | Echo 5: +9.6% |
| 🔵 **A1-alt A Sanctuary** | 35 / 28 s | Holy zone, **12 s, 8 blocks** (L142, was 8 s / 7 blocks): allies inside heal **5% max Health per second** (L142 "^5" read as 5%, was 4%) and take **10% less damage** (unchanged) = 60% max Health per cast | heal +0.1%/s, reduction +0.4% | **6.4%/s** (fixed: 5 + 14 x 0.1; the old row said 5.4), 15.6% less, 77% per cast |
| 🔵 **A1-alt B Martyr's Grace** | 30 / 18 s | Instant **75% max Health** heal (L143; above the 60% per-cast cap below - this ability is the exception) on the **lowest-health** target within **30 blocks** (L143, was 15); chains to the next-lowest, **-15 points per jump** (75 / 60 / 45 / 30 / 15 = up to 5 targets, 225% in total); **every party member in range first** (lowest first), then non-party players; **the Priest counts as a party member** (healed first when lowest, last when near full). **Chain modifier** (L144): +1 target per level AND a smaller drop, level 5 = **10 targets at a 7-point drop** (75 -> 12). **Echo** (L145): the whole chain repeats 1 s later at reduced strength | **the drop per jump -0.25 points** (15 -> 11.5; the 75% first heal does not grow - it is already above the cap) | 75 / 63.5 / 52 / 40.5 / 29 = 260% in total (+16%) |
| 🟢 **A2 Shield Bubble** | 28 / 24 s | Place a **6-block bubble** for **12 s** (L145); blocks projectiles, absorbs damage for allies inside; **HP = 100% of the caster's max Health**; it can break; **heal pulse** (default 8% max Health, everyone inside) each time its HP drops to **75 / 50 / 25 / 0%** = 4 pulses, the last as it breaks (L147) = 32% per bubble; **Echo** (L145): a weaker bubble forms once in the same place when it ends or breaks (HP and pulses at the Echo %) | HP +3% of caster's max Health (pulses stay 8%: a Server Setup row) | 142% HP |
| 🔵 **A2-alt Guardian Spirit** | **PASSIVE** while equipped; **20 Mana per save** (proposed; no Mana = no save) | **30-block AURA** around the Priest, **no tagging** (L146); class-skill-tree toggle: **party members only [default] / every player in the aura** (L146): when someone in it - **or the Priest** - would die, they **survive at 30% Health** (L145); **per-player cooldown 12 s, doubling each save** (12, 24, 48 ...) - one player dying non-stop is saved at 0, 12, 36, 84 s; resets after **30 s out of combat** (L145 default) | survive Health +1% | 44% |
**Heal caps still apply** (live rows `priestHeal.maxPerHit` / `maxPerSecond`): ability heals are a **separate channel** with their own cap: **no single ability may heal one target more than 60% of its max Health per cast** - **except Martyr's Grace** (75% first heal, L143), whose first heal is capped at **90%** even with Power+ (proposed). An Echo pulse is a separate cast (1 s later). Heal-on-hit stays as today until all Priest abilities exist (class file).
Soul tethers are now called **Bindings**; starting one needs line of sight, a locked Binding keeps draining through walls (L140; weapon rule, not an ability - `research/cloud/Soul-Orb-Spec.md` owns it).
Divinity XP: ability heals pay 1 XP per HP on others, 1.25 on self through the live heal bridge (shield bubble absorbs pay 0.5 XP per HP absorbed).

### 2.5 Berserker (Fury; party damage buffer + sustained melee)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Enrage** | 14 / 30 s | At activation, players within 8 blocks + party members within 16 (**picked once**, the buff stays on them wherever they go - **not an aura**; L127, confirmed L128; Radius+ widens both circles) get a damage buff that **grows +10% -> +20% over 10 s**, holds 5 s, then ends; **you get double: +20% -> +40%** | peak +1% (party 20 -> 34%), duration unchanged; **self capped at +60%** | party peak 34%, self 60% (capped) |
| 🔵 **A1-alt A Blood Frenzy** | **TOGGLE** (L129): **1 Mana + 0.5 Stamina per attack** (every swing, hit or miss) + **0.2 Mana + 0.1 Stamina per second** (proposed numbers); Mana / Stamina regen continues; off when either runs out; 10 s before it can be switched on again | **Every hit you land = 1 stack** (one per landed swing, not per enemy), max **25** (L129), **each stack decays 6 s after it was gained** (L129). Per stack **you: +1.5% damage, +1% attack speed, +0.5% move speed** (L136-L138; 25 stacks = +37.5% / +25% / +12.5%; Enrage peaks +40% damage, Flowing Form +30% attack speed and no damage). **Allies get half of each through an AURA** - players within 8 blocks + party within 16, **only while inside** (L130). **Floor** modifier: min stack 5 / 10 once reached, never with Duration+ (L130) | **+2% of the per-stack values** per level (x1.28 at Lv 15) | self per stack 1.92% damage / 1.28% attack / 0.64% move = **+48% / +32% / +16% at 25**; allies half |
| 🔵 **A1-alt B Warlord's Banner** | **40 Mana upfront** (L135, was 20), nothing while it stands, Mana regen continues / **40 s, counted from when the banner falls** (proposed; from planting it would be 75-100% uptime) | Plant a banner for **30 s**, **12-block** range (L132): in range, players **+8% damage, +8% defence, +8% attack speed**, party **+12%** each, you **+16%** each (L132 + L134); the banner **falls when its time ends OR when you leave its range** (L135); **each mob killed in range +1 s** (mini-boss +3, boss +5, total cap 60 s; L133); **Echo** (L132): the buff lingers briefly at reduced strength after the banner falls | **+2% of each tier value** per level | players / party / you **+10.2% / +15.4% / +20.5%** each |
| 🟢 **A2 Whirlwind** | 12 / 14 s | **Spin 3 s**, hit everything within 3 blocks every 0.5 s: 0.5 H a tick (3.0 H total), heals you **10% of the damage**; **Echo** (L139): a weaker spin repeats once 1 s after the spin ends | +2% damage, heal +0.2% | 3.84 H, 13% (Echo 5: +1.15 H) |
| 🔵 **A2-alt Earthsplitter** | 14 / 12 s | 12-block shockwave line, 2.0 H, **knocks up 1 s**; +1% per 1% of your Health missing (**cap +50%**) | +2% damage | 2.56 H (3.84 H at low Health) |

### 2.6 Monk (class skill OPEN; disruptor, single-target control; costs Mana and Stamina)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Flowing Form** | 6 Mana to start, then **0.5 Mana + 0.3 Stamina per second**; CD 40 s | Aura (5 blocks): enemies are **Awed** (L128: distracted ~1 s - lose their target - then -1% defence and -0.5% move per TOTAL combo landed during the ability, caps -20% / -10%); **combo stacks** (L128): every hit = 1 stack, max 20, each stack decays 5 s after gained; per stack **you** gain **+2% move speed and +1.5% attack speed** (+40% / +30% at 20); lasts **30 s** (tree), ends early if Mana or Stamina runs out; enemies stay Awed 10 s after. **The 15-combo doubling is gone** (L128) | **+2% of the per-stack values** per level (x1.28 at Lv 15); Awe caps unchanged | per stack +2.56% move / +1.92% attack = **+51% / +38% at 20** (under the +60% speed cap) |
| 🔵 **A1-alt A Hundred Fists** | 8 + 0.6 Mana, 0.3 Stamina per second / 40 s | Flowing Form (same combo stacks) where every **10th hit** releases a **shockwave** on all Awed enemies (1.0 H each), **at most one shockwave per 8 s** (proposed: fast wraps land 10 hits in ~3 s; at 5 s the Monk pair with Palm Strike reaches 87% > the 80% rule) | +2% shockwave damage | 1.28 H |
| 🔵 **A1-alt B Still Water** | 18 / 25 s | 10 s stance: **deflect front projectiles**, **counter melee hits** (each blocked hit strikes back 1.0 H); every counter adds Awe. **Echo** (L124): when the stance ends the melee **counters come back for ~3 s while you move freely** (break stance to attack and still block + counter); a block + counter **interrupts your own attack** (hit mid-swing = block + counter instead); Echo levels = a longer echo (3.0 / 3.5 / 4.0 / 4.5 / 5.0 s) | counter +2% | 1.28 H |
| 🟢 **A2 Palm Strike** | 8 / 6 s | Single-target strike, **stun 0.75 s + knockback 4 blocks**, 1.2 H; **Echo** (L123): a second, weaker palm strike on the same target 1 s later (its stun counts toward the boss stunlock window, section 2.8) | damage +2%, stun +0.01 s, **CD -0.1 s to a floor of 5.0 s (Lv 11)** (was to 4.6 s: with Echo it would pass the 50% budget) | 1.54 H, 0.9 s, 5.0 s CD |
| 🔵 **A2-alt Cyclone Kick** | 10 / 8 s | Spinning kick: everything within 3 blocks takes 0.8 H and is **pushed 5 blocks** | damage +2%, push +0.1 block | 1.02 H, 6.4 blocks |
Stamina pool is only about 12, so Flowing Form's drain is deliberately small (30 s = 9 Stamina); if a Monk row adds Stamina per class level later the drain can rise.

### 2.7 Assassin (Assassination; priority killer + debuffer)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Cloak + First Strike** | 14 / 30 s | **Invisible 8 s** (breaks when you attack). **First Strike**: your next hit within 10 s of casting gets **+100% crit chance** (max crit is 150%, overcrit above 100%, triple crit above 200%; SkyyGear change) | cloak +0.2 s, First Strike crit damage +3% | 10.8 s cloak |
| 🔵 **A1-alt A Shadow Clone** | 20 / 35 s | Cloak + a **decoy** mobs attack for 5 s; it bursts when it ends: 2.0 H in 4 blocks | clone HP +3%, burst +2% | 2.56 H |
| 🔵 **A1-alt B Vanishing Act** | 16 / 28 s | Instant 3 s cloak + 4-block smoke: enemies inside lose track of you 2 s and are **Slowed 25%**; First Strike as A1 | smoke +0.05 s, slow +0.5% | 3.7 s, 32% |
| 🟢 **A2 Toxin** | 12 / 16 s | Vial: **4-block poison cloud** 5 s; **Poison** 0.25 H per second (1.25 H total) + **Weakened** (deal 15% less damage) | poison +2%, Weaken +0.5% | 1.6 H, 22% |
| 🟢 **A2-alt God Killer** | 14 / 45 s | Your next attack on a **boss or mini-boss** (within 12 s) does **2x**, **3x** if a backstab; stacks with First Strike; **Echo** (L118): the empowered strike repeats once 1 s later at reduced strength (the echo keeps the boss multiplier, not First Strike's crit - proposed) | multiplier +0.03 | 2.4x / 3.4x (Echo 5: +0.72x / +1.02x) |

### 2.8 Stunlock rule (L120-L121, all classes)
Combo hits may **stunlock any enemy** (wraps are fast enough to; L119). **Bosses and mini-bosses break out**: after **3 s x the number of players stunlocking them** of continuous stunlock (1 player 3 s, 2 players 6 s, 3 = 9 s, **cap 4 players = 12 s**; Server Setup rows) the boss **gets a hit on you** to break free (L121). Proposed: ability stuns (Palm Strike + its Echo, Shield Shockwave, Iron Chain) count toward the same continuous-stun timer, so an Echo cannot skip the breakout.

## 3. Modifier overview (full steps in `Modifier-Pool-Spec.md`)
Each ability's modifiers are exactly the ones in its class file (kept; 4, or 5 where Skyy added one on 2026-10-07). Levelling: Lv 1 = unlocked, steps per level in the pool spec, max Lv 5 (Floor: 2), no doubling.

**Added 2026-10-07** (`research/cloud/Modifier-Pool-Spec.md` section 2.3 has each one's exact behaviour):

| Ability | New modifier | What it does here | Line |
|---|---|---|---|
| Meteor | 🔁 Echo | second, weaker meteor on the same spot 1 s later | L111 |
| Mana Barrier | 👣 Follow | the placed dome moves with you (also a class-tree upgrade) | L113 |
| God Killer | 🔁 Echo | the empowered strike repeats once 1 s later | L118 |
| Palm Strike | 🔁 Echo | second, weaker palm strike on the same target 1 s later | L123 |
| Still Water | 🔁 Echo | counters return ~3 s after the stance while you move freely (levels: longer) | L124 |
| Blood Frenzy | 🧱 **Floor** (new, 18th modifier) | min stack 5 (Lv 1) / 10 (Lv 2) once reached; never with Duration+ | L130 |
| Warlord's Banner | 🔁 Echo | the buff lingers briefly at reduced strength after the banner falls | L132 |
| Whirlwind | 🔁 Echo | a weaker spin repeats once 1 s after the spin ends | L139 |
| Sacred Heal | 🔁 Echo | a second, weaker instant heal 1 s later in the same circle | L141 |
| Martyr's Grace | 🔁 Echo | the whole chain repeats 1 s later at reduced strength | L145 |
| Shield Bubble | 🔁 Echo | a weaker bubble forms once in the same place when it ends / breaks | L145 |
| Martyr's Grace | ⛓️ Chain (changed) | +1 target per level AND a smaller drop: Lv 5 = 10 targets, 7-point drop | L144 |

**Echo strength (recomputed, section 5):** a repeat at **20 / 22.5 / 25 / 27.5 / 30%** (was 30-70%) of the ability **at its own level, without the other equipped modifier's bonus**; at the old 70% Meteor + Power+ reached 2.5x the staff's damage per Mana and Palm Strike 65% of weapon DPS.

## 4. Power ledger (how the layers add up)
Every ability's effect at its limit is **<= 2.0x its Lv 1 effect** so the layers cannot snowball:

| Layer | Adds (share of the Lv 1 effect) |
|---|---|
| Ability levels 1 -> 15 | +28% |
| Two modifiers at max level (about +25% each; "kind" modifiers like Pierce / Chain are priced by an equivalent; **Echo 5 = +30%**, Floor 2 = about +25%) | +50% (+55% with Echo) |
| Class-tree path (a behaviour change, **trade-off**, not a pure buff) | +20% |
| **Sum** | **x1.98 (cap x2.0)**; with Echo x2.03 on paper - the section 5 checks below pass because Echo copies the ability **without** the other modifier |

Cooldown reductions, Haste and Efficiency modifiers are priced inside the +50% (an Efficiency 5 = -25% cost, worth +25%).

## 5. Power budget (recomputed 2026-10-08 with python3)
Rule of thumb: a damage ability used on cooldown may add **at most 50% of the weapon's damage rate**, and the **two equipped damage abilities together at most 80%**; a support ability's group healing may not exceed **6% max Health per second** for the party (averaged over its cooldown), and a single target may not be healed more than 60% per cast (Martyr's Grace: 75%, capped 90%).
Method: **Max E** = the old ledger value (E0 x 1.98), or for an Echo ability the larger of that and **Lv 15 value x the best other modifier at Lv 5 + Lv 15 value x 30% (Echo 5)**; share = Max E / cooldown against 1 H per second.

### 5.1 Damage abilities (martial: share of 1 H/s weapon rate)
| Class | Ability | E0 (H) | CD | Max E (H) | How max is counted | Share of weapon DPS at max |
|---|---|---|---|---|---|---|
| Warrior | Shield Shockwave | 1.00 | 12 s | 1.98 | x1.98 ledger | 16% |
| Warrior | Iron Chain | 0.60 | 14 s | 1.19 | x1.98 ledger | 8% |
| Archer | Pinning Shot | 1.20 | 12 s | 2.38 | x1.98 ledger | 20% |
| Archer | Arrow Rain | 2.00 | 20 s | 3.96 | x1.98 ledger | 20% |
| Archer | Hunter's Net | 0.50 | 18 s | 0.99 | x1.98 ledger | 6% |
| Archer | Rapid Fire (net extra over normal shooting) | 4.50 | 20 s | 8.91 | x1.98 ledger | 45% |
| Archer | Explosive Arrow (net extra) | 1.00 | 14 s | 1.98 | x1.98 ledger | 14% |
| Berserker | Whirlwind (+ Echo, L139) | 3.00 | 14 s | 6.91 | Lv 15 3.84 x Duration+ 1.5 + Echo 1.15 | 49% |
| Berserker | Earthsplitter (+50% at low Health) | 2.00 | 12 s | 3.96 | x1.98 ledger | 33% |
| Monk | Palm Strike (+ Echo, L123; CD floor 5.0 s) | 1.20 | 5 s | 2.38 | Lv 15 1.54 x Power+ 1.25 + Echo 0.46 | 48% |
| Monk | Cyclone Kick | 0.80 | 8 s | 1.58 | x1.98 ledger | 20% |
| Monk | Hundred Fists (one wave per 8 s at most) | 1.00 | 8 s | 1.98 | Lv 15 1.28 x Power+ 1.25 + Echo 0.38 | 25% |
| Assassin | Toxin (over 5 s) | 1.25 | 16 s | 2.48 | x1.98 ledger | 15% |
| Assassin | Shadow Clone burst | 2.00 | 35 s | 3.96 | x1.98 ledger | 11% |
| Assassin | God Killer (+ Echo, L118; boss only) | 2.4x / 3.4x hit | 45 s | +3.42 H over a normal hit (backstab 2.4 extra + Echo 1.02) | Lv 15 + Echo 30% | 8% |
Worst pairs: Archer Pinning + Rapid Fire = **64%**; Monk Palm Strike + Hundred Fists = **72%**; Berserker Whirlwind alone 49% (its A1s are buffs); all **pass** the 80% rule.
(Changes made to pass: **Echo 5 = 30%** (at 70%: Palm Strike 65%, Whirlwind 60%); **Palm Strike's CD stops at 5.0 s** (4.6 s + Echo = 52%); **Hundred Fists at most one wave per 8 s** (5 s: Monk pair 87%). Older: Rapid Fire CD 20 s, Arrow Rain 2.0 H.)
Not in the damage rule: Still Water counters (only when you are hit) and the self buffs (Blood Frenzy, Banner) - see 5.3.

### 5.2 Mage (mana-limited, so the check is damage per Mana against the charged staff shot = 0.10 H per Mana)
| Ability | E0 (H) | Cost | Max (H) | H per Mana | Ratio at max |
|---|---|---|---|---|---|
| Meteor (+ Echo, L111) | 3.0 | 30 | 5.95 (3.84 x Power+ 1.25 + Echo 1.15) | 0.198 | 1.98x |
| Starfall (+ Echo) | 3.6 | 36 | 7.14 (4.61 x 1.25 + 1.38) | 0.198 | 1.98x |
| Arcane Beam | 3.0 | 30 | 5.94 | 0.198 | 1.98x |
| Frost Nova | 1.5 | 24 | 2.97 | 0.124 | 1.24x (it is mostly crowd control) |
Cap: max **2.0x** the staff's damage per Mana. Echo at the old 70% would make Meteor + Power+ **2.50x** (fails); at 30% it is 1.98x (passes). Echoes cost nothing.

### 5.3 Support abilities
| Ability | Base | CD / uptime | At max | Metric | Check |
|---|---|---|---|---|---|
| Rallying Guard | 20% reduction | 24 s on / 6 s | 30% (capped) | effective HP x1.43 for 25% uptime | ok (+14%) |
| Bulwark Stance | 50% front | 28 s on / 8 s | 60% | front only | ok |
| Unbreakable | 5 s no-death | 40 s | 6.4 s | once per 40 s | ok |
| Sacred Heal (+ Echo, L141) | 25% + HoT 10% = 35% per ally | 14 s | Lv 15 47%; + Power+ 5 + Echo 5 = 68.4% | group **2.5%/s** -> 3.36%/s -> **4.89%/s** | under 6%/s |
| Sanctuary (L142: 12 s, 8 blocks, 5%/s) | 60% per cast | 28 s (43% uptime) | Lv 15 6.4%/s; + Power+ 5 + Duration+ 5 = 8.0%/s for 18 s = 144% | average **2.14%/s** -> 2.74 -> **5.14%/s** | ok on average (8%/s while standing in it - watch) |
| Martyr's Grace (L143-L145) | 75 / 60 / 45 / 30 / 15 = 225% | 18 s | Lv 15 260%; Chain 5 = 10 targets 435%; + Power+ (first heal capped 90%) 540%; + Echo 5 x1.3 | party of 5: **2.5%/s** each -> Lv 15 + Power+ + Echo **4.44%/s**; 10 targets + Echo 3.14%/s | ok; first target up to 90% + 22.5% echo per cast (the exception) |
| Shield Bubble (L145, L147) | HP 100% caster max Health; 4 pulses x 8% = 32% heal | 24 s (12 s on) | HP 142%; + Echo 5: a 30% bubble + 4 pulses of 2.4% | pulse healing **1.33%/s** -> **1.73%/s** with Echo | ok |
| Guardian Spirit (passive, L145-L146) | save at 30% Health, 20 Mana | per player 12 / 24 / 48 s ... (saves at 0, 12, 36, 84 s if one player keeps dying) | 44% Health | 3 saves of one player in a 60 s fight, Mana-limited | ok (the doubling stops "keep one tank alive forever") |
| Enrage (L127) | party +10 -> +20%, self x2 | 30 s (15 s on) | party peak 34%, self capped 60% | average over the cooldown: party **8.3% -> 13.0%**, self 16.7% -> 23.3% | ok (party average cap 20%) |
| Blood Frenzy (L129-L130, L136-L138) | per stack 1.5% dmg / 1% attack / 0.5% move, 25 max, 6 s decay | toggle (about 100% uptime) | 25 stacks: self DPS **x1.72** (Lv 15 x1.85); allies half | real stacks = hits per s x 6 s x (1 + attack speed): 1 hit/s **6.4 stacks (x1.17)**, 1.5/s 9.9 (x1.26), 2/s 13.6 (x1.37); 25 needs about 3.3 hits/s; Floor 10 = +15% dmg / +10% attack always | **watch**: highest always-on buff; Mana per attack + the 6 s pause after damage limit it (10 Mana lasts ~7 s while being hit; regen 2.5/s in combat outruns the 1.45/s cost when not hit) |
| Warlord's Banner (L132-L135) | in range: you +16% dmg / def / attack (DPS x1.346), party x1.254, players x1.166 | 30 s on; CD 40 s **after it falls** | Lv 15 tiers 10.2 / 15.4 / 20.5% | uptime **43%** -> self average +14.8% DPS; 60 s with kills -> 60% / +20.7% (CD from planting: 75% / +25.9%) | ok with the CD after the fall |
| Mana Barrier (L112-L113) | 2 HP per Mana, 12 s dome | 30 s (40% uptime; Duration+ 5 60%) | 2.7 HP per Mana, **max absorb 100% max Health per cast** | one health bar per cast | ok |
| Flowing Form (L128) | per stack +2% move / +1.5% attack, 20 max, 5 s decay | 40 s (30 s on, 75%) | 20 stacks +40% / +30% (Lv 15 +51% / +38%) | real stacks: 1 hit/s 5.4, 2/s 11.8, wraps (~3.3/s) 20 | ok - the 15-combo doubling is gone (L128), so the old +60% cap is never reached |

## 6. Findings (changes / flags for Skyy and the local session)
| # | Finding |
|---|---|
| 1 | **Physical classes lack Mana** (section 1.2). Needs a +2 Mana per class level row, or Stamina costs. |
| 2 | Rapid Fire needs a 20 s cooldown or its base needs to be about 0.35 H per arrow, else it passes 50%. |
| 3 | Arcane Beam as written ("1x to 3x per second") is ambiguous; I fixed the unit (0.5 / 1.0 / 1.5 H). |
| 4 | Enrage's "the Berserker gets the same buff but bigger" needs a number: I used **x2, hard cap +60%** (a Berserker at L15 would otherwise reach +68%). |
| 5 | ~~Flowing Form cap +60% at the 15-combo doubling~~ - the doubling is gone (L128); 20 stacks give +40% / +30% (Lv 15 +51% / +38%). The strongest always-on buff is now **Blood Frenzy** (toggle, x1.72 DPS at 25 stacks) - realistic stacks are 6-14 at 1-2 hits per second (section 5.3). |
| 6 | The existing class-file "At Lv X" language says "+1% per level" for Rallying Guard and Pinning Shot; both hit a cap at Lv 11 here, so Lv 12-15 grow duration instead (levels must always give something). |
| 7 | Priest ability heals are a separate cap channel (60% of max Health per target per cast); the live per-hit cap rows stay for heal-on-hit. |
| 8 | Ability XP (levels by use) is its own track, not class skill XP; "uses that do something" are defined per ability in section 7. |
| 9 | **Echo** is now on 11 abilities (was 2). At the pool's old 30-70% it broke three budgets (Meteor 2.50x per Mana, Palm Strike 65%, Whirlwind 60%) -> Echo steps **20 / 22.5 / 25 / 27.5 / 30%**, and an echo copies the ability **without** the other equipped modifier. Still Water + Banner echoes are time-based instead (section 3). |
| 10 | **Martyr's Grace 75%** (L143) is above the 60% per-cast heal cap: it is the named exception; its ability levels shrink the drop per jump instead of growing the 75%, and Power+ caps the first heal at 90%. |
| 11 | **Warlord's Banner** with a CD counted from planting would be up 75% (100% with kill extensions to 60 s); counting the 40 s CD **from when it falls** gives 43-60%. |
| 12 | **Guardian Spirit** is a passive (L145): it needs a Mana price per save (proposed 20) and a use rule (saves are rare - each counts as 5 uses, section 7). |
| 13 | 11 abilities now offer **5** modifiers (the 2026-10-04 lock said "aim 3-4"); still 2 equipped and 14 points = two maxed, so the extra choice is fine. |

## 7. What counts as a use (per ability)
| Ability | Counts when ... |
|---|---|
| Rallying Guard | at least one party member or mob in range (taunt hits a mob) |
| Bulwark Stance | the front blocks or reduces at least one hit |
| Unbreakable | the 1 HP clause saves you at least once (or a mob is taunted) |
| Shield Shockwave / Iron Chain / Palm Strike / Cyclone Kick | hits at least one enemy |
| Pinning Shot / Arrow Rain / Hunter's Net | marks / roots at least one enemy |
| Rapid Fire / Explosive Arrow | at least 5 arrows hit / the blast hits an enemy |
| Meteor / Starfall / Beam / Frost Nova | hits at least one enemy |
| Mana Barrier | absorbs at least 4 HP (you or, with Ward, an ally inside the dome) |
| Sacred Heal / Sanctuary / Martyr's Grace | heals at least one hurt ally (or the Priest when hurt) |
| Shield Bubble | absorbs or blocks something |
| Guardian Spirit (passive) | a save happens; **each save counts as 5 uses** (saves are rare; proposed) |
| Enrage / Banner | at least one ally or enemy hit during the buff (Banner: also each mob killed in range, max 1 per 3 s) |
| Blood Frenzy (toggle) | every **10 stacks gained** while on (max 1 per 3 s) - a toggle left on must not level by idling |
| Whirlwind / Earthsplitter | hits at least one enemy |
| Flowing Form | at least 5 combo reached |
| Hundred Fists / Still Water | a shockwave / a counter happens (also a counter during Still Water's Echo) |
| Cloak + First Strike | the first strike lands |
| Shadow Clone / Vanishing Act | a mob attacks the clone / loses track |
| Toxin | poisons at least one enemy |
| God Killer | the empowered hit lands on a boss |

## 8. Server Setup rows (sketch)
`abilities.maxLevel` (15), `abilities.usesCoefficient` (4.5) and `abilities.usesExponent` (1.5), `abilities.usePerSeconds` (3), `abilities.modifier.costs` (1,1,1,2,2), `abilities.<ability>.cost / cooldown / base / perLevel` (35 abilities x 3-4 rows, generated from this table),
`abilities.budget.*` (the caps in section 5, shown in Server Setup as warnings when an admin edit breaks them), `mana.physicalPerLevel` (2).
New with the 2026-10-07 lines: `stunlock.secondsPerPlayer` (3) + `stunlock.maxPlayers` (4) (L121); `banner.killSeconds` (1) / `banner.miniBossSeconds` (3) / `banner.bossSeconds` (5) / `banner.maxSeconds` (60) (L133); `banner.cost` (40) (L135); `frenzy.maxStacks` (25) / `frenzy.decaySeconds` (6) / `frenzy.manaPerAttack` (1) / `frenzy.staminaPerAttack` (0.5) / `frenzy.manaPerSecond` (0.2) / `frenzy.staminaPerSecond` (0.1) (L129); `flowing.maxStacks` (20) / `flowing.decaySeconds` (5) (L128); `bubble.pulsePercent` (8) (L147); `guardian.manaPerSave` (20) / `guardian.firstCooldown` (12) / `guardian.outOfCombatReset` (30) / `guardian.radius` (30) (L145-L146); `martyr.range` (30) / `martyr.firstHeal` (75) / `martyr.drop` (15) (L143); `barrier.seconds` (12) (L112).

## 9. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Max Mana per class today and whether a physical per-level row is feasible in SkyySkills (Priest 5 / Mage 10 rows exist). |
| 2 | The class skill XP curve (flat curve LIVE since 0.4.12): ability levels are separate; check nothing else uses "level" for abilities. |
| 3 | Real H values per level (SkyyGear base damage curve F(L)); the budget assumes 1 H per second as the martial weapon rate. |
| 4 | Whether the rune engine supports channelled abilities (Arcane Beam), toggled auras (Flowing Form drain per second) and a persistent bubble entity. |
| 5 | The engine limits behind the open items in the class files (taunt, glide, mid-air jump ...) are untouched by this spec. |
| 6 | Engine hooks for the 2026-10-07 lines: a **cheat-death hook** for Guardian Spirit (cancel a lethal hit, set 30% Health); a **visible but see-through dome** (Mana Barrier look, L114) and whether a placed entity can follow a player (Follow); **per-player stunlock timer** on bosses + forcing the boss's hit (L121); a toggle ability with **per-swing costs** (Blood Frenzy) and an aura that buffs only while inside; kill events inside a radius (Banner extension). |
| 7 | **Vanilla attack rates** (hits per second) for axes / maces / wraps / gauntlets - the Blood Frenzy / Flowing Form stack estimates in section 5.3 assume 1-3.3 hits per second. |
| 8 | `research/cloud/Class-Tree-Paths.md` (read-only here) still has stale lines: E5 Serenity ("the buff doubles at 20 combo, not 15" - the doubling is gone, L128), B3 Crimson Frenzy ("+2.5% (was +2%)" - now 1.5% per stack, L136), LB2 Radiant Pulse (overlaps Sacred Heal's Echo, L141), W2 Shared Fury (kill extension now belongs to the Banner, L133), W1 War Horn ("party radius +3" vs Enrage's 8 / 16 ranges, L127); and no Mana Barrier **Follow** node although L113 says Follow is also a skill-tree upgrade. |

## 10. Questions for Skyy
| # | Question | Recommended default |
|---|---|---|
| 1 | Mana for the five physical classes: +2 per class level, or Stamina costs? | [+2 Mana per class level] |
| 2 | Ability level cap 15 and 14 points (two modifiers maxed): right size, or more points? | [15 / 14] |
| 3 | Berserker Enrage self cap +60%: OK? | [yes] |
| 4 | Echo strength: L5 = 30% (was 70%) so Meteor / Palm Strike / Whirlwind stay inside the budget? | [30%] |
| 5 | Warlord's Banner cooldown: 40 s counted from when the banner falls, not from planting? | [from the fall] |
| 6 | Blood Frenzy cost: 1 Mana + 0.5 Stamina per swing, 0.2 Mana + 0.1 Stamina per second? | [yes] |
| 7 | Martyr's Grace levels shrink the drop per jump (15 -> 11.5) instead of raising the 75%; Power+ caps the first heal at 90%? | [yes] |
| 8 | Guardian Spirit: 20 Mana per save; each save counts as 5 ability uses? | [yes] |
| 9 | Stunlock: ability stuns (Palm Strike + Echo, Shield Shockwave) count toward the boss breakout timer? | [yes] |
| 10 | Hundred Fists: at most one shockwave per 8 s? | [8 s] |
