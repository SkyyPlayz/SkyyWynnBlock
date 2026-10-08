# Modifier pool spec - the 18 shared modifiers

Cloud draft, 2026-10-06. Exact behaviour of every modifier per kind of ability, level steps, caps and rules. Rules from `research/classes/README.md` (LOCKED 2026-10-04): 4 modifiers per ability, **2 equipped**, **no doubling**, shared pool, each ability unlocks and levels each modifier **separately**,
**Ricochet = projectiles only**, **Chain = effects only**. Level system from `Class-Ability-Spec-Draft.md`: modifier level 1-5, point cost 1 / 1 / 1 / 2 / 2 (7 points to max one; an ability has 14 points = two maxed).
Numbers are placeholders. Companion: availability counts below were computed from the 7 class files (every one of the 151 modifier slots on the 35 abilities is covered).

**Refresh 2026-10-08 (cloud):** follows every 2026-10-07 line of `docs/answered/classes.md` (lines 111-148, cited "L<n>"): Echo added to 9 more abilities (L111, L118, L123, L124, L132, L139, L141, L145), **Floor** = the 18th modifier (L130), Follow on Mana Barrier (L113), Martyr's Grace Chain (L144), stunlock breakout (L120-L121), no void protection on traversals (L116-L117). Change list: `research/cloud/Ability-Refresh-1007.md`.

## 1. Ability kinds (so one modifier can be defined once per kind)

| Kind | Abilities (examples) |
|---|---|
| **P - Projectile** | Pinning Shot, Rapid Fire, Explosive Arrow, Meteor (a falling projectile), Palm Strike's struck enemy (treated as a launched body) |
| **Z - Zone / cloud** | Arrow Rain, Hunter's Net, Starfall, Sanctuary, Frost Nova, Toxin, Vanishing Act (smoke), Shield Bubble (a placed volume), **Mana Barrier** (a placed dome since L113) |
| **S - Strike / cone / line / spin** | Shield Shockwave (cone), Earthsplitter (line), Whirlwind (spin), Cyclone Kick, Palm Strike, Iron Chain, Hundred Fists (shockwave) |
| **B - Buff / aura / banner** | Rallying Guard, Enrage (targets picked once, not an aura - L127), Blood Frenzy (toggle aura, L129-L130), Warlord's Banner (placed, L132), Flowing Form (combo stacks, L128) |
| **T - Stance** | Bulwark Stance, Unbreakable, Still Water |
| **H - Heal** | Sacred Heal, Martyr's Grace |
| **W - Ward / mark / save** | Guardian Spirit (a **passive** save aura since L145), God Killer, Cloak + First Strike, Shadow Clone |
| **C - Channel** | Arcane Beam, Rapid Fire (3 s burst) |

## 2. The 17 modifiers (level 1 -> 5)

Each row: the step values, then the effect **per kind**. Steps are per level of the modifier on **that ability**; max level 5. "Base" = the ability's own value at its current ability level.

### 2.1 Numeric modifiers
| Modifier | Steps (L1 / 2 / 3 / 4 / 5) | Effect by kind | Cap |
|---|---|---|---|
| ⏳ **Duration+** | +10 / 20 / 30 / 40 / 50% duration (min +0.5 s) | **B/T/Z**: the effect lasts longer (Blood Frenzy: each stack decays later, 6 -> 9 s; Banner: base 30 -> 45 s, the 60 s kill cap stays). **P (status)**: root / mark / stun last longer. **H**: the heal-over-time lasts longer. **C**: channel / burst lasts longer (Rapid Fire: +10% arrows per level, Beam +0.3 s). **W**: cloak / save window longer | status duration max **+2 s** over base; cloak max **+4 s**; no effect on one-shot instant heals |
| ⭕ **Radius+** | +8 / 16 / 24 / 32 / 40% radius or length (min +0.5 block) | **Z**: bigger area. **B**: bigger party circle. **S**: cone / line / spin reach. **P**: explosion radius | max radius **x1.5** of base; **12 blocks** absolute for damage areas; support ranges above 12 (Enrage 8 / 16, Blood Frenzy aura, Banner 12, Martyr's Grace 30, Guardian Spirit 30) only x1.5, absolute 40 |
| 💪 **Power+** | +5 / 10 / 15 / 20 / 25% of the main effect | **damage** abilities +% damage; **H** +% heal; **shield** +% HP; **buff / defence** +% points of the buff (the percent is applied to the *value*, i.e. 20% -> 25% at L5, not +25 points); **CC** +% duration of the stun / root | defence and buff percents never above their ability cap (Class-Ability-Spec-Draft); stun max **3 s**, root max **4 s** |
| 💧 **Efficiency** | -5 / -10 / -15 / -20 / -25% Mana and Stamina cost | any ability with a cost (also drain-per-second of Flowing Form, Guardian Spirit's Mana per save) | cost never below **50%** of base |
| 🩸 **Leech** | heals you 4 / 6 / 8 / 10 / 12% of damage the ability deals | **S, P, B, T** with damage (Whirlwind, Enrage, Blood Frenzy, Unbreakable) | at most **5% of max Health per second** |
| 🛡️ **Ward** | a shield of 4 / 6 / 8 / 10 / 12% of max Health for 5 s, on you (or on **allies** for support abilities: Rallying Guard, Martyr's Grace, Banner, Mana Barrier - allies inside the dome, L113 -, Guardian Spirit - the saved player) | any ability | shields do not stack: the **largest** applies, cap **40%** max Health in total |
| ⚡ **Haste** | +10 / 15 / 20 / 25 / 30% move speed **and** attack speed for 3 s (+0.2 s per level) after the cast | any ability | does not stack with Flowing Form, Enrage, Blood Frenzy or the Banner's attack speed: the **highest** speed bonus applies; total speed bonus cap **+60%** (Blood Frenzy: only while above 10 stacks) |
| 🐌 **Slow** | targets hit are slowed 15 / 20 / 25 / 30 / 35% for 2 s (+0.2 s per level) | **P, S, C, Z**: each hit target; **B/T**: attackers (Still Water counters apply it) | strongest slow applies; cap **40%**; bosses take **half** |
| 💥 **Knockback+** | pushes targets 2 / 3 / 4 / 5 / 6 blocks | **S, P, Z, T**: the push on hit / on end (Mana Barrier: when it ends) | cap **8 blocks**; bosses **half**; mini-bosses 75%. The old "never into the Void (target stopped at an edge)" is **kept only as a question**: Skyy's no-void-protection lines (L116-L117) cover traversals (player moves), not pushing mobs - [default: keep the edge stop for mobs so their drops are not lost] |
| 🧲 **Pull** | draws targets 2 / 3 / 4 / 5 / 6 blocks toward the centre of the effect | **Z** (the net's centre), **S** (Whirlwind spin, Iron Chain's drag) | cap **8 blocks**; bosses immune; elites **half** |
| 🔥 **Lingering** | leaves a zone for 2 / 3 / 4 / 5 / 6 s after the effect ends, radius 70% of the main area, ticking **15% of the base damage / heal per second** | **P** (impact), **Z** (after the cloud), **S** (after a line) | max total lingering damage **90%** of the base hit |
| 👣 **Follow** | the placed zone **moves with you**; zone strength 80 / 85 / 90 / 95 / 100% of base while following; radius +5% per level | placed **Z** abilities: Sanctuary, Shield Bubble, **Mana Barrier** (the dome moves with you; also a class-tree upgrade - L113) | a following zone cannot be re-placed; follow ends if you die |
| 🔁 **Echo** | the ability **repeats once** after 1 s at **20 / 22.5 / 25 / 27.5 / 30%** strength (was 30-70%; recomputed - see 3.1), copying the ability at its own level **without the other equipped modifier's bonus**; two abilities echo by time instead (2.3) | the 11 abilities that offer it (section 4): damage, heals, the bubble, a banner and one stance (Still Water) - not channels or cloaks | cannot echo an echo; echoes cost nothing; an echo stun counts toward the boss stunlock timer |

### 2.2 Shape modifiers (they change the *form*, not a stat)
| Modifier | Steps | Effect by kind | Cap |
|---|---|---|---|
| 🔱 **Split** | splits into **3 copies** each at 35 / 40 / 45 / 50 / 55% of the original damage / effect | **P**: a fan (+/- 12 degrees) of 3; **Z**: 3 smaller zones around the centre (radius 60%); **S**: 3 lines in a fan; summons (Shadow Clone: 2 -> 3 clones with HP at the %) | the copies never share one target for more than 2 hits (the third copy is a miss on the same target); total on one target max **x1.65** |
| 📌 **Pierce** | passes through **+1 enemy per level** (each later enemy takes **80%** of the previous) | **P, C, S(line)**: hits more enemies; Beam: +1 enemy behind the first | max 6 enemies in total |
| 🎱 **Ricochet** | **+1 bounce per level** after a hit; each bounce at **70%** damage, range **8 blocks**, never the same enemy twice, walls and obstacles block it, it can miss | **P only** (Rapid Fire arrows; Palm Strike treats the struck enemy as a launched body that bounces into others and stuns them 50%) | max 5 bounces; never on zones, heals, buffs |
| ⛓️ **Chain** | **+1 jump per level**, instant, range **6 blocks**, each jump at **75%** strength, no target twice | **effects only**: heals, debuffs / poison (Toxin: jumps when a poisoned enemy dies), hooks (Iron Chain: hooks the nearest other enemy). **Martyr's Grace** (L144): +1 target per level AND a smaller drop, drop = 63 / (targets - 1) points so the last target always gets 12%: Lv 1 6 targets / 12.6, Lv 2 7 / 10.5, Lv 3 8 / 9.0, Lv 4 9 / 7.9, **Lv 5 10 targets / 7.0** (75 -> 12) | max 5 jumps (Martyr's Grace: 9 jumps = 10 targets); never on pure damage projectiles (that is Ricochet). Guardian Spirit no longer offers Chain (passive aura, L146) |

### 2.3 New and per-ability modifiers (2026-10-07)
| Modifier | Steps | Ability | Behaviour | Line |
|---|---|---|---|---|
| 🧱 **Floor** (new, 18th) | **2 levels**: min stack **5 / 10**; point cost **2 / 3** (5 points, priced like a 5-level modifier - proposed) | Blood Frenzy only | you still start at 0; once your stacks pass the floor they never decay below it (until the toggle goes off) | L130 |
| | | | **cannot be equipped together with Duration+** (the only exclusive pair) | L130 |
| 🔁 Echo | 20-30% repeat | Meteor | second, weaker meteor on the same spot 1 s later | L111 |
| 🔁 Echo | 20-30% repeat | Starfall / Hundred Fists | a weaker shower / each shockwave repeats once | class files |
| 🔁 Echo | 20-30% repeat | God Killer | the empowered strike repeats 1 s later with the boss multiplier (not First Strike's crit - proposed) | L118 |
| 🔁 Echo | 20-30% repeat | Palm Strike | second, weaker palm strike on the same target 1 s later | L123 |
| 🔁 Echo | 20-30% repeat | Whirlwind | a weaker spin (base 3 s) once 1 s after the spin ends | L139 |
| 🔁 Echo | 20-30% repeat | Sacred Heal | a weaker instant heal 1 s later in the same circle (no extra HoT) | L141 |
| 🔁 Echo | 20-30% repeat | Martyr's Grace | the whole chain repeats 1 s later at the Echo % | L145 |
| 🔁 Echo | 20-30% | Shield Bubble | a weaker bubble forms once in the same place when it ends / breaks: HP and its 4 heal pulses at the Echo % | L145, L147 |
| 🔁 Echo | **time**: 3.0 / 3.5 / 4.0 / 4.5 / 5.0 s | Still Water | after the stance the melee **counters return** (full strength) while you move freely; a block + counter **interrupts your own attack** | L124 |
| 🔁 Echo | **time**: 2 / 3 / 4 / 5 / 6 s at 50% | Warlord's Banner | after the banner falls its buff lingers on everyone who was in range | L132 |

## 3. Composition rules (so two equipped modifiers never break an ability)
| Rule | Detail |
|---|---|
| **No doubling** | the same modifier cannot be equipped twice on one ability, and a level-5 modifier cannot be "stacked" with another copy; level it instead (LOCKED) |
| **Different parameters multiply, same parameter adds** | e.g. Power+ (+25% damage) and Echo (+70% repeat) multiply their own parts; two modifiers that both raise duration would add (not a case in the pool because each ability offers one) |
| **Ledger** | each modifier maxed adds about **+25%** of the ability's Lv 1 effect to the power ledger (x1.98 total with levels and path); "shape" modifiers are priced by an equivalent; the table below shows the **expected** extra effect at max |
| **Exclusive pair** | **Floor + Duration+** cannot be equipped together (L130) |
| **Boss rules** | Pull: bosses immune; Knockback+ and Slow halved; stun / root halved; elites 75% |
| **Stunlock breakout** | combo hits may stunlock any enemy; a **boss / mini-boss** breaks out after **3 s x players stunlocking it** (cap 4 = 12 s) of continuous stun by **hitting you** (L120-L121); ability stuns and Echo stuns count toward the same timer [proposed] |
| **Players** | Knockback / Pull / Slow / stun apply to players only where PvP is on (SkyyIslands / PvP setting) |
| **Counting a use** | a modifier does not change what counts as a use (Class-Ability-Spec-Draft section 7) |
| **Respec** | swapping which 2 are equipped is free; spent points stay (Class-Ability-Spec-Draft section 1) |

### 3.1 Expected extra effect at level 5 (for the ledger)
| Modifier | Extra effect (typical single-target fight) |
|---|---|
| Power+ | +25% |
| Duration+ | +20 to 30% (buffs / zones), +10% (status) |
| Radius+ | +10 to 40% (more targets), 0% single target |
| Efficiency | +25% (cost) |
| Leech | up to +5% of max Health per second sustain |
| Ward | up to 12% of max Health per cast |
| Haste | +30% speed for 4 s |
| Slow | 35% slow (a control effect, about +15% damage taken equivalent) |
| Knockback+ / Pull | control, 0% damage, +small safety |
| Lingering | up to +50% over time (15% x 6 s = 90% of a base hit), only if enemies stay |
| Follow | +20% effective uptime of a zone |
| Echo | +30% x 1 repeat (was +70%); Still Water / Banner: a few seconds more of the effect |
| Floor | Lv 2 = 10 stacks held: +15% damage, +10% attack speed, +5% move (about +25%) |
| Split | +20% to +65% depending on targets |
| Pierce / Chain | +1 to 5 extra targets at 80% / 75% |
| Ricochet | +1 to 5 bounces at 70% |
Lingering (+90% nominal) is the **strongest on paper**, priced lower because enemies must stay in it; if a playtest shows it above +30%, lower its tick to 12%.
**Echo recomputed (python3, Lv 15 ability x Power+ 5 + Echo 5):** at the old 70% Meteor reached **2.50x** the staff's damage per Mana (cap 2.0x), Palm Strike **65%** and Whirlwind **60%** of weapon DPS (cap 50%); at 50% 2.24x / 58% / 55%; at **30%: 1.98x / 48% (with Palm Strike's CD floor 5.0 s) / 49%** - all pass. Healing with Echo 5: Sacred Heal 4.89%/s, Shield Bubble 1.73%/s (cap 6%/s). Full tables: `research/cloud/Class-Ability-Spec-Draft.md` section 5.

## 4. Availability (recomputed 2026-10-08 from the 7 class files' graphs)
Counts of how many of the 35 abilities offer each modifier (**151 slots**: 24 abilities x 4 + 11 abilities x 5):

| Modifier | Offered by | Abilities |
|---|---|---|
| Power+ | 28 | Rallying Guard, Bulwark Stance, Unbreakable, Shield Shockwave, Iron Chain, Pinning Shot, Arrow Rain, Meteor, Starfall, Arcane Beam, Mana Barrier, Frost Nova, Sacred Heal, Sanctuary, Martyr's Grace, Shield Bubble, Guardian Spirit, Enrage, Blood Frenzy, Warlord's Banner, Earthsplitter, Flowing Form, Hundred Fists, Still Water, Palm Strike, Cloak + First Strike, Shadow Clone, God Killer |
| Duration+ | 25 | Rallying Guard, Bulwark Stance, Unbreakable, Pinning Shot, Arrow Rain, Hunter's Net, Rapid Fire, Starfall, Arcane Beam, Mana Barrier, Frost Nova, Sacred Heal, Sanctuary, Shield Bubble, Enrage, Blood Frenzy, Warlord's Banner, Whirlwind, Flowing Form, Still Water, Cloak + First Strike, Shadow Clone, Vanishing Act, Toxin, God Killer |
| Radius+ | 21 | Rallying Guard, Unbreakable, Shield Shockwave, Arrow Rain, Hunter's Net, Explosive Arrow, Meteor, Starfall, Frost Nova, Sacred Heal, Sanctuary, Shield Bubble, Guardian Spirit, Enrage, Warlord's Banner, Whirlwind, Flowing Form, Hundred Fists, Cyclone Kick, Vanishing Act, Toxin |
| **Echo** | **11** (was 2) | Meteor, Starfall, Sacred Heal, Martyr's Grace, Shield Bubble, Warlord's Banner, Whirlwind, Hundred Fists, Still Water, Palm Strike, God Killer |
| Knockback+ | 9 | Bulwark Stance, Shield Shockwave, Explosive Arrow, Mana Barrier, Earthsplitter, Still Water, Palm Strike, Cyclone Kick, Shadow Clone |
| Slow | 9 | Shield Shockwave, Iron Chain, Rapid Fire, Arcane Beam, Frost Nova, Earthsplitter, Palm Strike, Cyclone Kick, Vanishing Act |
| Efficiency | 8 | Sacred Heal, Martyr's Grace, Guardian Spirit, Flowing Form, Hundred Fists, Cloak + First Strike, Vanishing Act, God Killer |
| Ward | 7 | Rallying Guard, Bulwark Stance, Mana Barrier, Martyr's Grace, Guardian Spirit, Warlord's Banner, Still Water |
| Split | 6 | Pinning Shot, Hunter's Net, Explosive Arrow, Meteor, Earthsplitter, Shadow Clone |
| Haste | 4 | Blood Frenzy, Cyclone Kick, Cloak + First Strike, God Killer |
| Leech | 4 | Unbreakable, Enrage, Blood Frenzy, Whirlwind |
| Lingering | 4 | Arrow Rain, Explosive Arrow, Meteor, Toxin |
| Chain | 3 | Iron Chain, Martyr's Grace, Toxin |
| **Follow** | **3** (was 2) | Mana Barrier, Sanctuary, Shield Bubble |
| Pierce | 3 | Pinning Shot, Rapid Fire, Arcane Beam |
| Pull | 3 | Iron Chain, Hunter's Net, Whirlwind |
| Ricochet | 2 | Rapid Fire, Palm Strike |
| **Floor** | **1** (new) | Blood Frenzy |
All 18 modifiers appear; no ability offers the same modifier twice; Ricochet is on projectile abilities (+ Palm Strike's launched body), Chain only on effect abilities. The 11 abilities with 5 are the ones Skyy added a modifier to on 2026-10-07.

## 5. Findings
| # | Finding |
|---|---|
| 1 | **Palm Strike + Ricochet** (class file: "the struck enemy is launched into others and stuns them too") breaks the "projectiles only" rule on paper. I defined the struck enemy as a **launched body** (a projectile in engine terms), so the lock holds. If the engine cannot launch bodies into others, swap Ricochet for Haste or Chain. |
| 2 | **Iron Chain + Chain** ("also hooks the nearest enemy") and **Toxin + Chain** (poison jumps) are effects, so allowed. **Martyr's Grace + Chain**: the old "cap at 4 jumps" is replaced by Skyy's L144 - up to 10 targets with a 7-point drop (section 2.1). |
| 3 | **Power+ on Rallying Guard / Bulwark** is "+% of the value" (20% -> 25%), not +25 points; capped by the ability's own damage-reduction cap (30%). |
| 4 | **Echo** is now on 11 abilities and **Follow** on 3 (L111-L145); Echo's steps were lowered to 20-30% so it fits the budget. 28 abilities offer Power+, so Power+ is the "default" pick; make sure its max (+25%) is not strictly the best choice: Radius / Duration / Efficiency give comparable or better situational value. |
| 5 | **Efficiency** on Flowing Form lowers the drain per second, not only the start cost (Blood Frenzy offers no Efficiency; its per-swing cost is fixed). |
| 6 | **Floor** has only 2 levels (Skyy's 5 / 10); priced 2 + 3 points so maxing it costs 5 of the ability's 14 points. |
| 7 | Echo on a **stance** (Still Water) and a **banner** is time-based (counters return / buff lingers), not a repeat - the old "no Echo on stances" rule is lifted for Still Water (L124). |

## 6. Server Setup rows (sketch)
`mods.<id>.steps` (5 numbers per modifier; Floor 2), `mods.<id>.cap` (per kind where listed), `mods.pointCosts` (1,1,1,2,2), `mods.floor.pointCosts` (2,3), `mods.floor.stacks` (5,10), `mods.echo.steps` (20,22.5,25,27.5,30), `mods.echo.stillWaterSeconds` (3,3.5,4,4.5,5), `mods.echo.bannerSeconds` (2,3,4,5,6) + `mods.echo.bannerStrength` (50), `mods.exclusive` (floor:duration), `mods.bossFactor` (stun/root/slow/knockback 0.5, pull 0), `stunlock.secondsPerPlayer` (3) / `stunlock.maxPlayers` (4), `mods.pvp` (off). Ability tables (Class-Ability-Spec-Draft) pick which 4 modifiers an ability offers.

## 7. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether the rune engine's modifier runestones (Fork, Ricochet, AoE scale, Duration, Damage) cover these (VERIFIED in the report: Expansion, Extended Duration, Fork, Ricochet exist) and which need our own composition (Leech, Ward, Haste, Echo, Follow, Lingering, Pull, Chain). |
| 2 | Per-ability separate levels are our own system (vanilla runes have no levels): the modifier level lives in our profile data and writes the rune modifier's numbers. |
| 3 | "Launched body" Ricochet for Palm Strike. |
| 4 | Whether a boss flag exists for the boss rules (SkyyMobs elite / boss ids). |
| 5 | Floor + the exclusive-pair rule and the time-based Echoes (Still Water, Banner) are our own code, not rune data. |
| 6 | `research/classes/README.md` pool (synced into every class file by `tools/class_pages.py --sync-pool`) has no **Floor** entry and still says "Each ability offers 4"; the generic Echo text there says nothing about the new strength. Local session: add Floor + re-sync (cloud agents may not edit it). |
| 7 | Whether a placed dome entity can follow a player (Mana Barrier / Sanctuary / Shield Bubble Follow). |

## 8. Questions for Skyy (2026-10-08 refresh)
| # | Question | Recommended default |
|---|---|---|
| 1 | Echo strength: L1-L5 = 20 / 22.5 / 25 / 27.5 / 30% (was 30-70%) so Meteor, Palm Strike and Whirlwind stay inside the budget? | [30% at L5] |
| 2 | Floor (2 levels) costs 2 + 3 ability points? | [yes, 5 points] |
| 3 | Knockback+ may push mobs into the void? (your no-void-protection lines cover traversals) | [no - keep the edge stop for mobs so drops are not lost] |
| 4 | Ability stuns and Echo stuns count toward the boss stunlock breakout timer? | [yes] |
