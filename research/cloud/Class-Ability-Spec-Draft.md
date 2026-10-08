# Class ability spec draft - numbers for all 7 classes

Cloud draft, 2026-10-06. Paper numbers only; nothing built. It replaces the older `Class-Abilities-Draft.md` (which used 4 Wynncraft-style spells; Skyy's 2026-10-04 locks changed the structure).
Inputs: `research/classes/*.md` (the 7 class files; LOCKED rows are kept exactly as written, the *proposed* rows are improved), `research/classes/README.md` (rules + modifier pool),
`docs/answered/classes.md` (Mana pools, wand / staff Mana, traversal costs). Companion drafts: `Modifier-Pool-Spec.md`, `Class-Tree-Paths.md`, `Soul-Orb-Spec.md` (written next).

Labels as in the class files: 🟢 locked · 🔵 proposed · 🟠 open. **All numbers are placeholders until a playtest**; they are written so one row changes one number.

## 1. The system in one page

| Rule | Value | Source |
|---|---|---|
| Abilities per class | 5 designed (A1, A1-alt x2, A2, A2-alt), a character owns 4, **2 equipped** (the two rune lines) | locked 2026-10-04 |
| Ability level | **1 to 15**, "levels by use" | proposal (this spec) |
| Points | 1 point per level from Lv 2 = **14 points** per ability | proposal |
| Modifiers | 4 per ability, **2 equipped**, no doubling; each unlocked + levelled **per ability** | locked |
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
| 🟢 **A1 Meteor** | 30 Mana / 14 s | Pick a spot within 25 blocks; after 1 s a meteor hits a **4-block area** for **3.0 H** | +2% damage | 3.84 H |
| 🔵 **A1-alt A Starfall** | 36 / 18 s | For 3 s, **12 stars** fall on a 6-block area, each 0.3 H (about 4 stars hit one enemy = 3.6 H); more total damage, spread out | +2% damage | 4.6 H |
| 🔵 **A1-alt B Arcane Beam** | 30 / 18 s | Channel a 20-block beam up to 3 s; damage ramps **1x -> 3x** (0.5, 1.0, 1.5 H per second = 3.0 H), single-target | +2% damage, ramp start +1% | 3.84 H |
| 🟢 **A2 Mana Barrier** | 20 / 30 s | 12 s (Skyy 2026-10-07: "at least 12 seconds"), a placed DOME on the ground (Follow upgrade = moves with you): while inside, damage you take **drains Mana instead of Health** (1 Mana per 2 HP); ends early at 0 Mana | ratio +0.05 HP per Mana (2.0 -> 2.7); **absorbs at most 100% of your max Health per cast** | 2.7 HP per Mana |
| 🔵 **A2-alt Frost Nova** | 24 / 22 s | **Freeze** enemies within 5 blocks 2 s (a hit breaks it after 1 s: 0.5 H), then **Chill** 3 s; 1.0 H on freeze | damage +2%, freeze +0.03 s | 1.9 H total, 2.4 s freeze |
Note: Mage Mana scale (+10/Sorcery level) makes 30-36 Mana a clear but affordable cost; at Sorcery 1 the pool is 40.

### 2.4 Priest (Divinity; healer + protector; heals as % of max Health)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Sacred Heal** | 25 Mana / 14 s | **Instant heal** for everyone within 9 blocks: **25% max Health** (the Priest heals themself 20% more = 30%); plus a heal-over-time of **40% of the instant heal over 4 s** | instant +0.5% of max Health, HoT % +0.5 points, HoT duration +0.05 s (the three upgrade separately in the tree) | 32% (38% Priest), HoT 47% over 4.7 s |
| 🔵 **A1-alt A Sanctuary** | 35 / 28 s | Holy zone, 8 s, 7 blocks: allies inside heal **4% max Health per second** and take **10% less damage** | heal +0.1%/s, reduction +0.4% | 5.4%/s, 15.6% less |
| 🔵 **A1-alt B Martyr's Grace** | 30 / 18 s | Instant **45% max Health** heal on the lowest-health ally within 15 blocks; chains to 2 more allies (each 25% less) | heal +0.7% | 55% |
| 🟢 **A2 Shield Bubble** | 28 / 24 s | Place a **5-block bubble** for 8 s; blocks projectiles, absorbs damage for allies inside; **HP = 100% of the caster's max Health**; it can break | HP +3% of caster's max Health | 142% |
| 🔵 **A2-alt Guardian Spirit** | 30 / 45 s | Mark an ally within 20 blocks for 10 s; if they would die they **survive at 30% Health** once | survive Health +1% | 44% |
**Heal caps still apply** (live rows `priestHeal.maxPerHit` / `maxPerSecond`): ability heals are a **separate channel** with their own cap: **no single ability may heal one target more than 60% of its max Health per cast** (Martyr's Grace 55% is the highest). Heal-on-hit stays as today until all Priest abilities exist (class file).
Divinity XP: ability heals pay 1 XP per HP on others, 1.25 on self through the live heal bridge (shield bubble absorbs pay 0.5 XP per HP absorbed).

### 2.5 Berserker (Fury; party damage buffer + sustained melee)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Enrage** | 14 / 30 s | Party within 8 blocks gets a damage buff that **grows +10% -> +20% over 10 s**, holds 5 s, then ends; **you get double: +20% -> +40%** | peak +1% (party 20 -> 34%), duration unchanged; **self capped at +60%** | party peak 34%, self 60% (capped) |
| 🔵 **A1-alt A Blood Frenzy** | 16 / 30 s | The rage grows with **every hit you land**: +2% per hit for you, +1% for the party, up to 20 stacks (self 40%, party 20%); ends 5 s after your last hit | +0.1% per stack per level | self 54%, party 27% |
| 🔵 **A1-alt B Warlord's Banner** | 20 / 40 s | Plant a banner for 15 s: party within 8 blocks **+15% damage**, you **+25%** while near it | +0.5% | +22% / +32% |
| 🟢 **A2 Whirlwind** | 12 / 14 s | **Spin 3 s**, hit everything within 3 blocks every 0.5 s: 0.5 H a tick (3.0 H total), heals you **10% of the damage** | +2% damage, heal +0.2% | 3.84 H, 13% |
| 🔵 **A2-alt Earthsplitter** | 14 / 12 s | 12-block shockwave line, 2.0 H, **knocks up 1 s**; +1% per 1% of your Health missing (**cap +50%**) | +2% damage | 2.56 H (3.84 H at low Health) |

### 2.6 Monk (class skill OPEN; disruptor, single-target control; costs Mana and Stamina)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Flowing Form** | 6 Mana to start, then **0.5 Mana + 0.3 Stamina per second**; CD 40 s | Aura (5 blocks): enemies are **Awed**; **only you** gain **+25% move speed and +20% attack speed**; every hit you land = 1 combo, each combo **slows Awed enemies 1% (cap 15%) and lowers their defence 1% (cap 15%)**; at **15 combo your buff doubles**; lasts **30 s** (tree), ends early if Mana or Stamina runs out; enemies stay Awed 10 s after | buff +1% (to +39% / +34%); Awe per combo +0.05% | doubled at 15 combo: +78% move, +68% attack speed (**cap +60% each**) |
| 🔵 **A1-alt A Hundred Fists** | 8 + 0.6 Mana, 0.3 Stamina per second / 40 s | Flowing Form where every **10 combo** releases a **shockwave** on all Awed enemies (1.0 H each) | +2% shockwave damage | 1.28 H |
| 🔵 **A1-alt B Still Water** | 18 / 25 s | 10 s stance: **deflect front projectiles**, **counter melee hits** (each blocked hit strikes back 1.0 H); every counter adds Awe | counter +2% | 1.28 H |
| 🟢 **A2 Palm Strike** | 8 / 6 s | Single-target strike, **stun 0.75 s + knockback 4 blocks**, 1.2 H | damage +2%, stun +0.01 s, **CD -0.1 s (to 4.6 s)** | 1.54 H, 0.9 s, 4.6 s CD |
| 🔵 **A2-alt Cyclone Kick** | 10 / 8 s | Spinning kick: everything within 3 blocks takes 0.8 H and is **pushed 5 blocks** | damage +2%, push +0.1 block | 1.02 H, 6.4 blocks |
Stamina pool is only about 12, so Flowing Form's drain is deliberately small (30 s = 9 Stamina); if a Monk row adds Stamina per class level later the drain can rise.

### 2.7 Assassin (Assassination; priority killer + debuffer)
| Ability | Cost / CD | Base | Per level | At Lv 15 |
|---|---|---|---|---|
| 🟢 **A1 Cloak + First Strike** | 14 / 30 s | **Invisible 8 s** (breaks when you attack). **First Strike**: your next hit within 10 s of casting gets **+100% crit chance** (max crit is 150%, overcrit above 100%, triple crit above 200%; SkyyGear change) | cloak +0.2 s, First Strike crit damage +3% | 10.8 s cloak |
| 🔵 **A1-alt A Shadow Clone** | 20 / 35 s | Cloak + a **decoy** mobs attack for 5 s; it bursts when it ends: 2.0 H in 4 blocks | clone HP +3%, burst +2% | 2.56 H |
| 🔵 **A1-alt B Vanishing Act** | 16 / 28 s | Instant 3 s cloak + 4-block smoke: enemies inside lose track of you 2 s and are **Slowed 25%**; First Strike as A1 | smoke +0.05 s, slow +0.5% | 3.7 s, 32% |
| 🟢 **A2 Toxin** | 12 / 16 s | Vial: **4-block poison cloud** 5 s; **Poison** 0.25 H per second (1.25 H total) + **Weakened** (deal 15% less damage) | poison +2%, Weaken +0.5% | 1.6 H, 22% |
| 🟢 **A2-alt God Killer** | 14 / 45 s | Your next attack on a **boss or mini-boss** (within 12 s) does **2x**, **3x** if a backstab; stacks with First Strike | multiplier +0.03 | 2.4x / 3.4x |

## 3. Modifier overview (full steps in `Modifier-Pool-Spec.md`)
Each ability's four modifiers are exactly the ones in its class file (kept). Levelling: Lv 1 = unlocked, steps per level in the pool spec, max Lv 5, no doubling.

## 4. Power ledger (how the layers add up)
Every ability's effect at its limit is **<= 2.0x its Lv 1 effect** so the layers cannot snowball:

| Layer | Adds (share of the Lv 1 effect) |
|---|---|
| Ability levels 1 -> 15 | +28% |
| Two modifiers at max level (about +25% each; "kind" modifiers like Pierce / Chain are priced by an equivalent) | +50% |
| Class-tree path (a behaviour change, **trade-off**, not a pure buff) | +20% |
| **Sum** | **x1.98 (cap x2.0)** |

Cooldown reductions, Haste and Efficiency modifiers are priced inside the +50% (an Efficiency 5 = -25% cost, worth +25%).

## 5. Power budget (the check from the task)
Rule of thumb: a damage ability used on cooldown may add **at most 50% of the weapon's damage rate**, and the **two equipped damage abilities together at most 80%**; a support ability's group healing may not exceed **6% max Health per second** for the party, and a single target may not be healed more than 60% per cast.

### 5.1 Damage abilities (martial: share of 1 H/s weapon rate; script-checked)
| Class | Ability | E0 (H) | CD | Max E (H, x1.98) | Share of weapon DPS at max |
|---|---|---|---|---|---|
| Warrior | Shield Shockwave | 1.00 | 12 s | 1.98 | 16% |
| Warrior | Iron Chain | 0.60 | 14 s | 1.19 | 8% |
| Archer | Pinning Shot | 1.20 | 12 s | 2.38 | 20% |
| Archer | Rapid Fire (net extra over normal shooting) | 4.50 | 20 s | 8.91 | 45% |
| Archer | Explosive Arrow (net extra) | 1.00 | 14 s | 1.98 | 14% |
| Archer | Arrow Rain | 2.00 | 20 s | 3.96 | 20% |
| Archer | Hunter's Net | 0.50 | 18 s | 0.99 | 6% |
| Berserker | Whirlwind | 3.00 | 14 s | 5.94 | 42% |
| Berserker | Earthsplitter (+50% at low Health) | 2.00 | 12 s | 3.96 | 33% |
| Monk | Palm Strike | 1.20 | 6 s | 2.38 | 40% |
| Monk | Cyclone Kick | 0.80 | 8 s | 1.58 | 20% |
| Monk | Hundred Fists (per 10 combo) | 1.00 | 8 s | 1.98 | 25% |
| Assassin | Toxin (over 5 s) | 1.25 | 16 s | 2.48 | 15% |
| Assassin | Shadow Clone burst | 2.00 | 35 s | 3.96 | 11% |
Worst pairs: Archer Pinning + Rapid Fire = 65% (under 80%); Berserker Whirlwind + Earthsplitter would be 75%; Monk Palm + Hundred Fists 65%. All pass.
(Changes I made to proposed or placeholder rows to pass: **Rapid Fire CD set to 20 s** (it would be 56% at 16 s), Arrow Rain 2.0 H.)

### 5.2 Mage (mana-limited, so the check is damage per Mana against the charged staff shot = 0.10 H per Mana)
| Ability | E0 (H) | Cost | H per Mana | Ratio at max (x1.98) |
|---|---|---|---|---|
| Meteor | 3.0 | 30 | 0.100 | 1.98x |
| Starfall | 3.6 | 36 | 0.100 | 1.98x |
| Arcane Beam | 3.0 | 30 | 0.100 | 1.98x |
| Frost Nova | 1.5 | 24 | 0.062 | 1.24x (it is mostly crowd control) |
Cap: max **2.0x** the staff's damage per Mana. (Original proposal had Arcane Beam at 1.5 x charged - 40 Mana for 6 H = 0.15 per Mana, which would have been 3x; I rebalanced to 0.5 H per second ramp and cost 30.)

### 5.3 Support abilities
| Ability | E0 | CD | Max effect (x1.98) | Metric | Check |
|---|---|---|---|---|---|
| Rallying Guard | 20% reduction | 24 s on / 6 s | 30% (capped) | effective HP x1.43 for 25% uptime | ok (+14%) |
| Bulwark Stance | 50% front | 28 s on / 8 s | 60% | front only | ok |
| Unbreakable | 5 s no-death | 40 s | 6.4 s | once per 40 s | ok |
| Sacred Heal | 25% + 10% HoT | 14 s | 45% (+ HoT) per cast | group HPS = 35% x1.98 / 14 = **4.9%/s** | under 6%/s |
| Sanctuary | 32% + 10% DR over 8 s | 28 s | 63% + 20% | 2.3%/s | ok |
| Martyr's Grace | 45% single (+2 chain) | 18 s | 55% (cap 60%) | 5.0%/s single | ok |
| Shield Bubble | 100% caster HP | 24 s | 142% | absorbs about 4%/s of one health bar | ok |
| Guardian Spirit | one save | 45 s | 44% | rare | ok |
| Enrage | party peak 20% | 30 s (15 s on) | 34% | average party bonus 14% at max; Berserker self capped at +60% | ok (party average cap 20%) |
| Blood Frenzy | self 40% / party 20% | 30 s | 54% / 27% | needs hits | ok |
| Warlord's Banner | +15% / +25% | 40 s (15 s on) | +22% / +32% | uptime 38% -> average +8% | ok |
| Mana Barrier | 2 HP per Mana | 30 s | 2.7 HP per Mana, **max absorb 100% max Health** | one health bar | ok |
| Flowing Form | +25% move / +20% attack | 40 s (30 s on) | +60% caps | uptime 75% | **watch: highest uptime**; its cap +60% attack speed at 15 combo is the strongest solo buff; consider cap +50% |

## 6. Findings (changes / flags for Skyy and the local session)
| # | Finding |
|---|---|
| 1 | **Physical classes lack Mana** (section 1.2). Needs a +2 Mana per class level row, or Stamina costs. |
| 2 | Rapid Fire needs a 20 s cooldown or its base needs to be about 0.35 H per arrow, else it passes 50%. |
| 3 | Arcane Beam as written ("1x to 3x per second") is ambiguous; I fixed the unit (0.5 / 1.0 / 1.5 H). |
| 4 | Enrage's "the Berserker gets the same buff but bigger" needs a number: I used **x2, hard cap +60%** (a Berserker at L15 would otherwise reach +68%). |
| 5 | Flowing Form is the strongest self buff; I added caps (+60%) and a long CD (40 s). Candidates to lower: cap 50%. |
| 6 | The existing class-file "At Lv X" language says "+1% per level" for Rallying Guard and Pinning Shot; both hit a cap at Lv 11 here, so Lv 12-15 grow duration instead (levels must always give something). |
| 7 | Priest ability heals are a separate cap channel (60% of max Health per target per cast); the live per-hit cap rows stay for heal-on-hit. |
| 8 | Ability XP (levels by use) is its own track, not class skill XP; "uses that do something" are defined per ability in section 7. |

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
| Mana Barrier | absorbs at least 4 HP |
| Sacred Heal / Sanctuary / Martyr's Grace | heals at least one hurt ally (or the Priest when hurt) |
| Shield Bubble | absorbs or blocks something |
| Guardian Spirit | the mark is applied to a hurt ally (the save counts double) |
| Enrage / Blood Frenzy / Banner | at least one ally or enemy hit during the buff |
| Whirlwind / Earthsplitter | hits at least one enemy |
| Flowing Form | at least 5 combo reached |
| Hundred Fists / Still Water | a shockwave / a counter happens |
| Cloak + First Strike | the first strike lands |
| Shadow Clone / Vanishing Act | a mob attacks the clone / loses track |
| Toxin | poisons at least one enemy |
| God Killer | the empowered hit lands on a boss |

## 8. Server Setup rows (sketch)
`abilities.maxLevel` (15), `abilities.usesCoefficient` (4.5) and `abilities.usesExponent` (1.5), `abilities.usePerSeconds` (3), `abilities.modifier.costs` (1,1,1,2,2), `abilities.<ability>.cost / cooldown / base / perLevel` (35 abilities x 3-4 rows, generated from this table),
`abilities.budget.*` (the caps in section 5, shown in Server Setup as warnings when an admin edit breaks them), `mana.physicalPerLevel` (2).

## 9. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Max Mana per class today and whether a physical per-level row is feasible in SkyySkills (Priest 5 / Mage 10 rows exist). |
| 2 | The class skill XP curve (flat curve LIVE since 0.4.12): ability levels are separate; check nothing else uses "level" for abilities. |
| 3 | Real H values per level (SkyyGear base damage curve F(L)); the budget assumes 1 H per second as the martial weapon rate. |
| 4 | Whether the rune engine supports channelled abilities (Arcane Beam), toggled auras (Flowing Form drain per second) and a persistent bubble entity. |
| 5 | The engine limits behind the open items in the class files (taunt, glide, mid-air jump ...) are untouched by this spec. |

## 10. Questions for Skyy
1. Mana for the five physical classes: +2 per class level, or Stamina costs? (Recommended: +2 Mana per class level.)
2. Ability level cap 15 and 14 points (two modifiers maxed): right size, or more points?
3. Berserker self cap +60%: OK?
