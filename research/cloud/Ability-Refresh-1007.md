# Ability refresh 2026-10-07 - class abilities + modifier pool brought up to date

Cloud draft, 2026-10-08. Paper numbers only; nothing built. Edited in place: `research/cloud/Class-Ability-Spec-Draft.md` and
`research/cloud/Modifier-Pool-Spec.md`. Context read: `research/classes/*.md`, `research/cloud/Monk-Kit-Spec.md`,
`research/cloud/Class-Tree-Paths.md` (read-only, not edited).

## 1. Decisions followed (`docs/answered/classes.md`, every line dated 2026-10-07)

| Line | Decision | Used in |
|---|---|---|
| 111 | Meteor gains Echo | both files |
| 112 | Mana Barrier 12 s, damage drains Mana (1 per 2 HP), ends at 0 Mana | ability spec |
| 113 | Mana Barrier = placed dome + Follow modifier / tree upgrade; Ward extends it to allies | both |
| 114 | dome visible but see-through, no flashing | ability spec |
| 115-117 | Shadow Step; no void protection on any traversal | pool spec (Knockback+ question only) |
| 118 | God Killer gains Echo | both |
| 119, 122 | fist attack chains, gauntlet speed; wraps can stunlock one enemy | stack-rate estimates |
| 120-121 | stunlock: bosses / mini-bosses break out after 3 s x players (cap 4) by hitting you | both |
| 123 | Palm Strike gains Echo | both |
| 124 | Still Water Echo: counters return ~3 s while moving; block + counter interrupts your attack | both |
| 125-126, 131 | Berserker traversals; Warrior shield traversal shelved | not ability numbers (no change) |
| 127-128 | Enrage targets picked once (8 / party 16), not an aura; Flowing Form combo stacks (20, 5 s decay), doubling gone, Awe distract + per-total-combo debuff | ability spec |
| 129-130 | Blood Frenzy toggle, 25 stacks, 6 s decay, Mana + Stamina per attack, small drain; ally AURA (8 / 16, only inside); Floor modifier 5 / 10, never with Duration+ | both |
| 132-135 | Warlord's Banner 30 s / 12 blocks, 8 / 12 / 16% damage + defence + attack speed, Echo, kills extend it (1 / 3 / 5 s, cap 60), 40 Mana upfront, falls at the end or when you leave | both |
| 136-138 | Blood Frenzy per stack +1.5% damage, +1% attack speed, +0.5% move | ability spec |
| 139 | Whirlwind gains Echo | both |
| 140 | soul tethers = Bindings (line of sight to start, then through walls) | one note (weapon rule) |
| 141 | Sacred Heal gains Echo | both |
| 142 | Sanctuary 12 s, 8 blocks, 5% max Health / s | ability spec |
| 143-144 | Martyr's Grace 30 blocks, 75% first heal, -15 per jump, party first, Priest = party member; Chain up to 10 targets with a 7-point drop | both |
| 145-147 | Martyr's Grace + Shield Bubble Echo; bubble 6 blocks / 12 s; Guardian Spirit passive save (30 blocks, 30% Health, Mana, doubling per-player cooldown), aura with party / all toggle; bubble heal pulses at 75 / 50 / 25 / 0% | both |
| 148 | make Monk + Assassin playable; Shadoweave Lv 35; cloud mod | not ability numbers (no change) |

## 2. What changed

| Ability / rule | Was | Now | classes.md line |
|---|---|---|---|
| Meteor | modifiers without Echo | + Echo (2nd meteor 1 s later) | 111 |
| Mana Barrier | 6 s, kind "stance" | 12 s placed dome (kind Zone), Follow, Ward on allies inside, see-through look; uptime 40% | 112-114 |
| God Killer | no Echo | + Echo (keeps the boss multiplier, not First Strike's crit - proposed) | 118 |
| Palm Strike | no Echo; CD fell to 4.6 s | + Echo; CD floor 5.0 s (budget) | 123 |
| Still Water | no Echo ("no Echo on stances") | Echo = counters return 3.0-5.0 s while moving | 124 |
| Enrage | "party within 6" wording | players 8 + party 16, picked once, not an aura | 127 |
| Flowing Form | +25% / +20% buff, doubled at 15 combo, cap +60% | per stack +2% move / +1.5% attack, 20 max, 5 s decay; Lv 15 +51% / +38%; doubling gone | 128 |
| Blood Frenzy | 16 Mana / 30 s; +0.1% per stack per level; self 54% / party 27% | toggle; 1 Mana + 0.5 Stamina per swing, 0.2 + 0.1 per s (proposed); per stack 1.5 / 1 / 0.5%; Lv 15 +48% / +32% / +16% at 25; allies half in the aura | 129-130, 136-138 |
| Floor | (did not exist) | 18th modifier, Blood Frenzy only, 2 levels (5 / 10 stacks), 2 + 3 points, never with Duration+ | 130 |
| Warlord's Banner | +15% / +25%, 20 Mana, 40 s CD; Lv 15 +22% / +32% | 8 / 12 / 16% damage + defence + attack speed; 40 Mana; CD 40 s from the fall (proposed); kills extend to 60 s; Lv 15 10.2 / 15.4 / 20.5%; Echo = 50% linger 2-6 s | 132-135 |
| Whirlwind | no Echo | + Echo (weaker spin 1 s later) | 139 |
| Sacred Heal | no Echo | + Echo (weaker instant heal 1 s later) | 141 |
| Sanctuary | 8 s, 7 blocks, 4%/s; table "5.4%/s at Lv 15" | 12 s, 8 blocks, 5%/s; Lv 15 6.4%/s (arithmetic fixed) | 142 |
| Martyr's Grace | 45% + 2 chains, Lv 15 55%, Chain capped at 4 jumps | 75 / 60 / 45 / 30 / 15 in 30 blocks, party first; levels shrink the drop (15 -> 11.5); Power+ first heal cap 90%; Chain to 10 targets (drop = 63 / (targets - 1)); Echo | 143-145 |
| Shield Bubble | 5 blocks / 8 s | 6 blocks / 12 s; 4 heal pulses x 8%; Echo = weaker bubble re-forms | 145, 147 |
| Guardian Spirit | a cast mark, one save, 45 s CD; Chain marks +1 ally | PASSIVE 30-block aura, party / all toggle, save at 30% Health for 20 Mana (proposed); per-player CD 12 / 24 / 48 ...; no Chain | 145-146 |
| Echo (pool) | on 2 abilities, 30-70%, not on stances | on 11 abilities; **20 / 22.5 / 25 / 27.5 / 30%**, copies the ability without the other modifier; time-based for Still Water + Banner | 111-145 |
| Follow (pool) | Sanctuary, Shield Bubble | + Mana Barrier | 113 |
| Radius+ cap | 12 blocks absolute for everything | 12 for damage areas; support ranges x1.5, max 40 | 127, 132, 143, 146 |
| Knockback+ | "never into the Void" | kept for mobs only as a question (Skyy's void lines are about traversals) | 116-117 |
| Stunlock | (none) | boss breakout 3 s x players (cap 12 s); ability + Echo stuns count (proposed) | 120-121 |
| Modifier count | 4 per ability | 4, or 5 on the 11 abilities Skyy added one to | 111-145 |

## 3. Recomputed balance (python3)

Method: Max = old ledger (Lv 1 x 1.98), or for an Echo ability Lv 15 x best other modifier at Lv 5 + Lv 15 x Echo 5. Budget rules: one
damage ability <= 50% of weapon DPS, two equipped <= 80%, Mage <= 2.0x staff damage per Mana, group healing <= 6% max Health / s averaged.

| Check | Old Echo 70% | Echo 30% (new) | Rule |
|---|---|---|---|
| Meteor + Power+ + Echo, per Mana | 2.50x | **1.98x** | <= 2.0x |
| Whirlwind + Duration+ + Echo | 60% | **49%** | <= 50% |
| Palm Strike + Power+ + Echo (CD 4.6 s / 5.0 s) | 65% | 52% / **48%** | <= 50% |
| Monk pair Palm Strike + Hundred Fists (1 wave per 5 s / 8 s) | - | 87% / **72%** | <= 80% |
| Archer pair Pinning + Rapid Fire (no change) | 64% | 64% | <= 80% |
| Sacred Heal Lv 15 + Power+ + Echo | 5.80%/s | **4.89%/s** | <= 6%/s |
| Shield Bubble pulses + Echo | 2.27%/s | **1.73%/s** | <= 6%/s |

| Support item | Result |
|---|---|
| Sanctuary | average 2.14%/s (Lv 1) -> 2.74 (Lv 15) -> 5.14%/s (Power+ 5 + Duration+ 5); 8%/s while inside - watch |
| Martyr's Grace (party of 5) | 2.5%/s each -> 4.44%/s at Lv 15 + Power+ + Echo; Chain 5 (10 targets) 435% per cast, 3.14%/s each with Echo |
| Guardian Spirit | one player dying non-stop is saved at 0, 12, 36, 84 s (3 saves per minute), each 20 Mana |
| Enrage | average over the cooldown: party 8.3% -> 13.0%, self 16.7% -> 23.3% |
| Blood Frenzy | 25 stacks = x1.72 DPS (Lv 15 x1.85), but real stacks at 1 / 1.5 / 2 hits per s = 6.4 / 9.9 / 13.6 (x1.17 / x1.26 / x1.37); 25 needs ~3.3 hits/s. 10 Mana lasts ~7 s while you are being hit; in-combat regen 2.5/s beats the 1.45/s cost when not hit |
| Warlord's Banner | in range you x1.346 DPS, party x1.254, players x1.166; uptime 43% with the CD after the fall (+14.8% average), 60% with kills to 60 s (+20.7%); CD from planting 75% (+25.9%) |
| Flowing Form | 20 stacks +40% / +30% (Lv 15 +51% / +38%); real stacks 5.4 at 1 hit/s, 11.8 at 2/s, 20 with wraps (~3.3/s) |
| Mana Barrier | uptime 40% (Duration+ 5: 60%), absorb cap 100% max Health per cast |
| Availability | 151 modifier slots (24 x 4 + 11 x 5); Echo 11, Follow 3, Floor 1; all 18 modifiers used |

## 4. Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Echo strength: L5 = 30% (was 70%) so Meteor, Palm Strike and Whirlwind stay inside the budget? | [30%] |
| 2 | Warlord's Banner cooldown counts from when the banner falls (not from planting)? | [yes, 40 s after the fall] |
| 3 | Blood Frenzy cost: 1 Mana + 0.5 Stamina per swing + 0.2 Mana + 0.1 Stamina per second? | [yes] |
| 4 | Martyr's Grace levels shrink the drop per jump instead of growing the 75%; Power+ first heal cap 90%? | [yes] |
| 5 | Guardian Spirit: 20 Mana per save; each save counts as 5 ability uses? | [yes] |
| 6 | Floor (2 levels) costs 2 + 3 points? | [yes] |
| 7 | Ability stuns + Echo stuns count toward the boss stunlock breakout timer? | [yes] |
| 8 | Knockback+ may push mobs into the void? | [no - keep the edge stop for mobs] |
| 9 | Hundred Fists: at most one shockwave per 8 s? | [8 s] |
| 10 | God Killer's Echo keeps the boss multiplier but not First Strike's crit? | [yes] |

## 5. For the local session

| # | Item |
|---|---|
| 1 | `research/classes/README.md` pool + "Each ability offers 4": add **Floor**, say 4-5, re-sync with `python tools/class_pages.py --sync-pool` (cloud agents may not edit it). |
| 2 | `research/cloud/Class-Tree-Paths.md` stale nodes (read-only here): E5 Serenity (15-combo doubling gone, L128), B3 Crimson Frenzy (+2.5% "was +2%"; now 1.5%, L136), LB2 Radiant Pulse (overlaps Sacred Heal Echo, L141), W2 Shared Fury (kill extension is the Banner's, L133), W1 War Horn ("party radius +3" vs 8 / 16, L127); add a Mana Barrier **Follow** node (L113). |
| 3 | **UNVERIFIED** (needs HytaleServer.jar / Assets.zip): vanilla attack rates for axes / maces / wraps / gauntlets (stack estimates assume 1-3.3 hits/s); a cheat-death hook (Guardian Spirit); a see-through dome entity that can follow a player; per-player stunlock timers on bosses; per-swing costs on a toggle; kill events inside a radius; boss / mini-boss flags. |
| 4 | Server Setup rows to add (lists in both specs): stunlock, banner kill seconds + cap + cost, frenzy stacks / decay / costs, flowing stacks / decay, bubble pulse %, guardian Mana / cooldown / reset / radius, martyr range / heal / drop, barrier seconds, Echo + Floor steps. |
