# Modifier pool spec - the 17 shared modifiers

Cloud draft, 2026-10-06. Exact behaviour of every modifier per kind of ability, level steps, caps and rules. Rules from `research/classes/README.md` (LOCKED 2026-10-04): 4 modifiers per ability, **2 equipped**, **no doubling**, shared pool, each ability unlocks and levels each modifier **separately**,
**Ricochet = projectiles only**, **Chain = effects only**. Level system from `Class-Ability-Spec-Draft.md`: modifier level 1-5, point cost 1 / 1 / 1 / 2 / 2 (7 points to max one; an ability has 14 points = two maxed).
Numbers are placeholders. Companion: availability counts below were computed from the 7 class files (every one of the 140 modifier slots on the 35 abilities is covered).

## 1. Ability kinds (so one modifier can be defined once per kind)

| Kind | Abilities (examples) |
|---|---|
| **P - Projectile** | Pinning Shot, Rapid Fire, Explosive Arrow, Meteor (a falling projectile), Palm Strike's struck enemy (treated as a launched body) |
| **Z - Zone / cloud** | Arrow Rain, Hunter's Net, Starfall, Sanctuary, Frost Nova, Toxin, Vanishing Act (smoke), Shield Bubble (a placed volume) |
| **S - Strike / cone / line / spin** | Shield Shockwave (cone), Earthsplitter (line), Whirlwind (spin), Cyclone Kick, Palm Strike, Iron Chain, Hundred Fists (shockwave) |
| **B - Buff / aura / banner** | Rallying Guard, Enrage, Blood Frenzy, Warlord's Banner, Flowing Form |
| **T - Stance** | Bulwark Stance, Unbreakable, Still Water, Mana Barrier |
| **H - Heal** | Sacred Heal, Martyr's Grace |
| **W - Ward / mark / save** | Guardian Spirit, God Killer, Cloak + First Strike, Shadow Clone |
| **C - Channel** | Arcane Beam, Rapid Fire (3 s burst) |

## 2. The 17 modifiers (level 1 -> 5)

Each row: the step values, then the effect **per kind**. Steps are per level of the modifier on **that ability**; max level 5. "Base" = the ability's own value at its current ability level.

### 2.1 Numeric modifiers
| Modifier | Steps (L1 / 2 / 3 / 4 / 5) | Effect by kind | Cap |
|---|---|---|---|
| ⏳ **Duration+** | +10 / 20 / 30 / 40 / 50% duration (min +0.5 s) | **B/T/Z**: the effect lasts longer. **P (status)**: root / mark / stun last longer. **H**: the heal-over-time lasts longer. **C**: channel / burst lasts longer (Rapid Fire: +10% arrows per level, Beam +0.3 s). **W**: cloak / save window longer | status duration max **+2 s** over base; cloak max **+4 s**; no effect on one-shot instant heals |
| ⭕ **Radius+** | +8 / 16 / 24 / 32 / 40% radius or length (min +0.5 block) | **Z**: bigger area. **B**: bigger party circle. **S**: cone / line / spin reach. **P**: explosion radius | max radius **x1.5** of base, **12 blocks** absolute |
| 💪 **Power+** | +5 / 10 / 15 / 20 / 25% of the main effect | **damage** abilities +% damage; **H** +% heal; **shield** +% HP; **buff / defence** +% points of the buff (the percent is applied to the *value*, i.e. 20% -> 25% at L5, not +25 points); **CC** +% duration of the stun / root | defence and buff percents never above their ability cap (Class-Ability-Spec-Draft); stun max **3 s**, root max **4 s** |
| 💧 **Efficiency** | -5 / -10 / -15 / -20 / -25% Mana and Stamina cost | any ability with a cost (also drain-per-second of Flowing Form) | cost never below **50%** of base |
| 🩸 **Leech** | heals you 4 / 6 / 8 / 10 / 12% of damage the ability deals | **S, P, B, T** with damage (Whirlwind, Enrage, Blood Frenzy, Unbreakable) | at most **5% of max Health per second** |
| 🛡️ **Ward** | a shield of 4 / 6 / 8 / 10 / 12% of max Health for 5 s, on you (or on **allies** for support abilities: Rallying Guard, Martyr's Grace, Banner, Mana Barrier) | any ability | shields do not stack: the **largest** applies, cap **40%** max Health in total |
| ⚡ **Haste** | +10 / 15 / 20 / 25 / 30% move speed **and** attack speed for 3 s (+0.2 s per level) after the cast | any ability | does not stack with Flowing Form or Enrage: the **highest** speed bonus applies; total speed bonus cap **+60%** |
| 🐌 **Slow** | targets hit are slowed 15 / 20 / 25 / 30 / 35% for 2 s (+0.2 s per level) | **P, S, C, Z**: each hit target; **B/T**: attackers (Still Water counters apply it) | strongest slow applies; cap **40%**; bosses take **half** |
| 💥 **Knockback+** | pushes targets 2 / 3 / 4 / 5 / 6 blocks | **S, P, Z, T**: the push on hit / on end (Mana Barrier: when it ends) | cap **8 blocks**; bosses **half**; never into the Void (target is stopped at an edge); mini-bosses 75% |
| 🧲 **Pull** | draws targets 2 / 3 / 4 / 5 / 6 blocks toward the centre of the effect | **Z** (the net's centre), **S** (Whirlwind spin, Iron Chain's drag) | cap **8 blocks**; bosses immune; elites **half** |
| 🔥 **Lingering** | leaves a zone for 2 / 3 / 4 / 5 / 6 s after the effect ends, radius 70% of the main area, ticking **15% of the base damage / heal per second** | **P** (impact), **Z** (after the cloud), **S** (after a line) | max total lingering damage **90%** of the base hit |
| 👣 **Follow** | the placed zone **moves with you**; zone strength 80 / 85 / 90 / 95 / 100% of base while following; radius +5% per level | **Z, B(banner)** that are placed (Sanctuary, Shield Bubble) | a following zone cannot be re-placed; follow ends if you die |
| 🔁 **Echo** | the ability **repeats once** after 1 s at 30 / 40 / 50 / 60 / 70% strength | any ability except channels, stances and cloak; Starfall, Hundred Fists, heals, zones | cannot echo an echo; echoes cost nothing |

### 2.2 Shape modifiers (they change the *form*, not a stat)
| Modifier | Steps | Effect by kind | Cap |
|---|---|---|---|
| 🔱 **Split** | splits into **3 copies** each at 35 / 40 / 45 / 50 / 55% of the original damage / effect | **P**: a fan (+/- 12 degrees) of 3; **Z**: 3 smaller zones around the centre (radius 60%); **S**: 3 lines in a fan; summons (Shadow Clone: 2 -> 3 clones with HP at the %) | the copies never share one target for more than 2 hits (the third copy is a miss on the same target); total on one target max **x1.65** |
| 📌 **Pierce** | passes through **+1 enemy per level** (each later enemy takes **80%** of the previous) | **P, C, S(line)**: hits more enemies; Beam: +1 enemy behind the first | max 6 enemies in total |
| 🎱 **Ricochet** | **+1 bounce per level** after a hit; each bounce at **70%** damage, range **8 blocks**, never the same enemy twice, walls and obstacles block it, it can miss | **P only** (Rapid Fire arrows; Palm Strike treats the struck enemy as a launched body that bounces into others and stuns them 50%) | max 5 bounces; never on zones, heals, buffs |
| ⛓️ **Chain** | **+1 jump per level**, instant, range **6 blocks**, each jump at **75%** strength, no target twice | **effects only**: heals (Martyr's Grace: allies), buffs / marks (Guardian Spirit marks +1 ally), debuffs / poison (Toxin: jumps when a poisoned enemy dies), hooks (Iron Chain: hooks the nearest other enemy) | max 5 jumps; never on pure damage projectiles (that is Ricochet) |

## 3. Composition rules (so two equipped modifiers never break an ability)
| Rule | Detail |
|---|---|
| **No doubling** | the same modifier cannot be equipped twice on one ability, and a level-5 modifier cannot be "stacked" with another copy; level it instead (LOCKED) |
| **Different parameters multiply, same parameter adds** | e.g. Power+ (+25% damage) and Echo (+70% repeat) multiply their own parts; two modifiers that both raise duration would add (not a case in the pool because each ability offers one) |
| **Ledger** | each modifier maxed adds about **+25%** of the ability's Lv 1 effect to the power ledger (x1.98 total with levels and path); "shape" modifiers are priced by an equivalent; the table below shows the **expected** extra effect at max |
| **Boss rules** | Pull: bosses immune; Knockback+ and Slow halved; stun / root halved; elites 75% |
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
| Echo | +70% x 1 repeat (but only on one use per cooldown) |
| Split | +20% to +65% depending on targets |
| Pierce / Chain | +1 to 5 extra targets at 80% / 75% |
| Ricochet | +1 to 5 bounces at 70% |
Echo (+70%) and Lingering (+90% nominal) are the **strongest on paper**; both are priced with a smaller effective value because Echo needs a living target after 1 s and Lingering needs them to stay. If a playtest shows them above +30%, lower Echo's L5 to 60% and Lingering's tick to 12%.

## 4. Availability (computed from the 7 class files)
Counts of how many of the 35 abilities offer each modifier (140 slots in total):

| Modifier | Offered by | Abilities |
|---|---|---|
| Power+ | 28 | almost everything except Hunter's Net, Rapid Fire, Explosive Arrow, Whirlwind, Cyclone Kick, Vanishing Act, Toxin, ... |
| Duration+ | 26 | buffs, stances, zones, channels, cloaks |
| Radius+ | 20 | zones, auras, cones |
| Knockback+ | 9 | Bulwark Stance, Shield Shockwave, Explosive Arrow, Mana Barrier, Earthsplitter, Still Water, Palm Strike, Cyclone Kick, Shadow Clone |
| Slow | 9 | Shield Shockwave, Iron Chain, Rapid Fire, Arcane Beam, Frost Nova, Earthsplitter, Palm Strike, Cyclone Kick, Vanishing Act |
| Efficiency | 8 | Sacred Heal, Martyr's Grace, Guardian Spirit, Flowing Form, Hundred Fists, Cloak, Vanishing Act, God Killer |
| Ward | 6 | Rallying Guard, Bulwark Stance, Mana Barrier, Martyr's Grace, Warlord's Banner, Still Water |
| Split | 6 | Pinning Shot, Hunter's Net, Explosive Arrow, Meteor, Earthsplitter, Shadow Clone |
| Leech | 4 | Unbreakable, Enrage, Blood Frenzy, Whirlwind |
| Chain | 4 | Iron Chain, Martyr's Grace, Guardian Spirit, Toxin |
| Lingering | 4 | Arrow Rain, Explosive Arrow, Meteor, Toxin |
| Haste | 4 | Blood Frenzy, Cyclone Kick, Cloak + First Strike, God Killer |
| Pull | 3 | Iron Chain, Hunter's Net, Whirlwind |
| Pierce | 3 | Pinning Shot, Rapid Fire, Arcane Beam |
| Ricochet | 2 | Rapid Fire, Palm Strike |
| Echo | 2 | Starfall, Hundred Fists |
| Follow | 2 | Sanctuary, Shield Bubble |
All 17 modifiers appear; no ability offers the same modifier twice; Ricochet is on projectile abilities (+ Palm Strike's launched body), Chain only on effect abilities.

## 5. Findings
| # | Finding |
|---|---|
| 1 | **Palm Strike + Ricochet** (class file: "the struck enemy is launched into others and stuns them too") breaks the "projectiles only" rule on paper. I defined the struck enemy as a **launched body** (a projectile in engine terms), so the lock holds. If the engine cannot launch bodies into others, swap Ricochet for Haste or Chain. |
| 2 | **Iron Chain + Chain** ("also hooks the nearest enemy") and **Toxin + Chain** (poison jumps) are effects, so allowed; **Martyr's Grace + Chain** already is the base design (chains to 2 more), so Chain's levels add jumps on top: base 2 jumps + 5 = 7 allies; cap jumps at 4 total for Martyr's Grace (Class-Ability-Spec-Draft: single heal capped at 60%). |
| 3 | **Power+ on Rallying Guard / Bulwark** is "+% of the value" (20% -> 25%), not +25 points; capped by the ability's own damage-reduction cap (30%). |
| 4 | Only 2 abilities offer **Echo** and 2 **Follow**; fine (they are special). 28 abilities offer Power+, so Power+ is the "default" pick; make sure its max (+25%) is not strictly the best choice: Radius / Duration / Efficiency give comparable or better situational value. |
| 5 | **Efficiency** on Flowing Form lowers the drain per second, not only the start cost. |

## 6. Server Setup rows (sketch)
`mods.<id>.steps` (5 numbers per modifier), `mods.<id>.cap` (per kind where listed), `mods.pointCosts` (1,1,1,2,2), `mods.bossFactor` (stun/root/slow/knockback 0.5, pull 0), `mods.pvp` (off). Ability tables (Class-Ability-Spec-Draft) pick which 4 modifiers an ability offers.

## 7. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether the rune engine's modifier runestones (Fork, Ricochet, AoE scale, Duration, Damage) cover these (VERIFIED in the report: Expansion, Extended Duration, Fork, Ricochet exist) and which need our own composition (Leech, Ward, Haste, Echo, Follow, Lingering, Pull, Chain). |
| 2 | Per-ability separate levels are our own system (vanilla runes have no levels): the modifier level lives in our profile data and writes the rune modifier's numbers. |
| 3 | "Launched body" Ricochet for Palm Strike. |
| 4 | Whether a boss flag exists for the boss rules (SkyyMobs elite / boss ids). |
