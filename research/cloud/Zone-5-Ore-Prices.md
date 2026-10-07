# Zone 5 ore prices - re-fit of Amberite (30,000) and Drakonite (75,000)

Cloud draft, 2026-10-07. Paper design; nothing built. Inputs read: `research/cloud/Ember-Economy-Check.md` (sections 1-6: the Bazaar model, the Ember fit, the Tab re-run, the "follow-up" of ~9,300 / ~23,000), `research/cloud/Ore-Regrow-Spec.md` (sections 4 and 8: pockets, timers, utilisation), `research/cloud/Zone-4-5-Materials.md` (sections 1-5, 7-8: ores, veins, drops, old prices, kits), `research/cloud/Economy-Audit.md` (F3 endgame income 336-360k/h, C4, C13), `research/cloud/Bank-Tab-Calibration.md` (section 2.3 payoff model), `research/cloud/Chain-Premium-Fix.md` (Block step), `docs/answered/economy.md`. All arithmetic is python3 in scratch only (not in the repo).

## 0. The decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/economy.md` LOCKED 2026-10-04 | metal ore prices rise about x2 per tier step ("id probbly 2x each material"); live ladder 5 / 16 / 48 / 144 / 480 / 1,440 / 3,712 |
| `docs/answered/economy.md` LOCKED 2026-10-03 | processed goods +20% over their inputs (never above 22.2%) |
| `docs/answered/gear.md` + `research/cloud/SkyyArmory-Roadmap.md` | Amberite 58-67 and Drakonite 66-75 are the Roadmap's **proposal**, used as given |
| R3 | coins never skip a collection tier; ore bought on the Bazaar never counts toward Mining collections |
| `research/cloud/Ember-Economy-Check.md` Q1 (a proposal, not locked) | Ember Ore 4,300; this file assumes it and re-fits the two above it |

## 0.1 Answer

1. **Confirmed: Amberite ~9,300 and Drakonite ~23,000** (the Ember check's follow-up). Solving for "2.0x the Ember miner's coins/h for Amberite, 3.0x for Drakonite" gives 9,060 and 22,777, so round numbers 9,300 / 23,000 sit within 3%.
2. At the old prices a Fortune-100 miner earns **2.73M/h (Amberite 30,000) and 4.09M/h (Drakonite 75,000)** = 8.1x / 12.2x the audit's endgame income (336k). At 9,300 / 23,000 it is **859k/h and 1.27M/h** = 2.6x / 3.8x the audit and 2.05x / 3.03x the Ember miner's 419k.
3. Step ratios on the ladder: Mithril 1,440 -> Ember 4,300 (x3.0) -> Amberite 9,300 (**x2.16**) -> Drakonite 23,000 (**x2.47**), close to Skyy's "2x each tier".
4. **The Tab gets very easy for a Zone 5 ore miner** (a regular player at 90,000 per hour pays it in 43 h with Amberite, 26 h with Drakonite) - but that is the all-day-mining upper bound; at half-time mining it is 134 h / 67 h. Keep `tab.perHour` 90,000 for now, re-measure at Zone 5 (section 4). A lower fit (6,700 / 11,200) is the option if the Tab must stay a 100+ hour race.
5. With Drakonite at 23,000 the **Enchanted Drakonite Block is 676,825,600** (68% of the 1e9 ceiling), so the "no Drakonite Block" default can flip (Q4).

## 1. The model (same as the Ember check, re-run)

Bazaar (from `SkyyBazaar/build_skyybazaar_0.1.5.py` lines 2926-2982, 3065-3083): sell = base x factor x 0.90; each unit sold divides the factor by `exp(ln 1.10 x base / 10,000)`; clamp 0.25-4.0; decay to 1.0 with a 120-minute half-life on ln(factor); a 2-hour selling session. The python is not in the repo (the Ember check printed none), so I rebuilt it and **checked it against the Ember check's own table before using it**:

| Check | Ember check | This file |
|---|---|---|
| Mithril 1,440, 560 items/h | 201,000 | 201,234 |
| Ember 11,000, 412 items/h | 1,042,000 | 1,040,635 |
| Ember 4,300, 412 items/h | 419,000 | 418,512 |
| Ember Z5 4,300, 338 items/h | ~347,000 | 347,438 |
| Tab payoff, audit income 360k, regular / hardcore | 205 h / 72 h | 204 h / 72 h |

Per-unit impact at the new prices: `step` = 1.093 (9,300) and 1.245 (23,000) per unit, so Amberite floors after about 16 units and Drakonite after about 6: both miners live **on the 0.25 floor**, coins/h = items/h x 0.225 x base. The base price is the whole lever.

## 2. How many blocks per hour (the rate the price is fitted to)

The Zone-4-5 placeholders are 200 Amberite and 120 Drakonite blocks per hour. I derived them from the two Ember points of the Ember check (7 ore/cell Z4: 206 blocks/h; 3.5 ore/cell Z5: 169): time per block = swing + walking per vein / ore per vein, walking per vein x veins-per-cell^(-1/3) (cave search in 3D). Fit: 103 s walk per vein at 1 vein / cell, 2.8 s swing at Ember hardness 1.25.

| Ore | Veins / cell | Ore / vein | Hardness | Model blocks/h | Placeholder |
|---|---|---|---|---|---|
| Amberite | 2.0 | 5.5 | x1.5 | **198** | 200 |
| Drakonite | 0.8 | 4.0 | x2.0 | **112** | 120 |

Two points fit two parameters, so this is an interpolation, not a proof; it says the placeholders are plausible, not measured. I keep 200 / 120 (items/h = 400 / 240 at Fortune 100, x2.0).

**Regrow check** (`research/cloud/Ore-Regrow-Spec.md` section 4: supply = blocks x access x 3,600 / T; Amberite 50,400 blocks, T 2,400; Drakonite 4,400 blocks, T 900). Utilisation at 25% / 10% access, N players at the model rates; the rate drops only when utilisation passes 100%:

| Pocket | N = 6 | N = 12 | N = 20 | N = 30 | Blocks/h per player in the worst cell |
|---|---|---|---|---|---|
| Amberite | 6% / 16% | 13% / 31% | 21% / 52% | 31% / 79% | 198 (never limited under 38 players at 10% access) |
| **Drakonite** | 15% / 38% | 31% / 76% | 51% / **127%** | 76% / **191%** | 112 -> **88 (N 20, 10% access) -> 59 (N 30)** |

So Amberite is never regrow-limited; the **Drakonite pocket is the throttle** when 20+ players crowd it at low access. Then coins/h at 23,000 falls from 1.18M to 0.93M (N 20) and 0.63M (N 30); at the old 75,000 the same crowding still pays 3.0M / 2.0M, i.e. the old price would stay 6-9x the audit income at any crowd size. Price is not the crowd limiter, the pocket is; a lower price makes the pocket less worth fighting over, which is the intent.

## 3. Coins per hour at each price (Fortune 100, 2 h, the model above)

Audit endgame 336,460 (the Ember check's re-run of F3). "x Ember" = against the Ember Z4 miner at 4,300 (418,512 coins/h).

| Ore | Base | Items/h | Coins/h | x audit | x Ember | Note |
|---|---|---|---|---|---|---|
| Amberite | 30,000 (old) | 400 | 2,727,634 | 8.1 | 6.5 | 8x over, as the Ember check found |
| Amberite | 12,900 | 400 | 1,183,712 | 3.5 | 2.8 | = Ember 4,300 x3.0 |
| **Amberite** | **9,300** | 400 | **858,708** | **2.6** | **2.05** | proposal |
| Amberite | 7,000 | 400 | 651,075 | 1.9 | 1.6 | lower fit (about 6,700 gives 1.5x) |
| Drakonite | 75,000 (old) | 240 | 4,091,437 | 12.2 | 9.8 | 12x over |
| Drakonite | 38,700 | 240 | 2,120,083 | 6.3 | 5.1 | = 12,900 x3.0 |
| **Drakonite** | **23,000** | 240 | **1,267,632** | **3.8** | **3.03** | proposal |
| Drakonite | 15,000 | 240 | 833,328 | 2.5 | 2.0 | lower fit (about 11,200 gives 1.5x) |

Sensitivity at the proposed prices: Amberite 150 / 200 / 250 blocks/h = 649k / 859k / 1.07M; Drakonite 90 / 120 / 150 = 957k / 1.27M / 1.58M. Fortune 77 (a skill-50 player, x1.77) = 762k / 1.12M. **No Fortune (a mid player)** = 440k / 647k. Solved prices for k x Ember: 1.5x = 6,742 / 11,213; 2.0x = 9,060 / 15,068; 3.0x = 13,695 / 22,777.

**Fit rule:** Amberite 2.0x and Drakonite 3.0x the Ember miner's coins/h (income per hour rises about x2 per tier from Ember, then x1.5 for Drakonite because its pocket is small and its bar needs a drop). This is the rule the Ember check's 9,300 / 23,000 came from; the solve reproduces it.

## 4. Tab payoff effect (Bank-Tab-Calibration 2.3 model, `tab.perHour` 90,000)

Hours online to Paid in Full; casual / regular / hardcore (25% / 40% / 60% of income, 1.5 / 3 / 6 h a day, 150 / 120 / 100 hidden hours).

| Miner income | Case | casual | regular | hardcore |
|---|---|---|---|---|
| 360,000 (the calibration) | audit endgame | never | 204 h (68 d) | 72 h (12 d) |
| 418,512 | Ember Z4 4,300 | 1,013 h (675 d) | 141 h (47 d) | 56 h (9 d) |
| **858,709** | **Amberite 9,300** | 110 h (73 d) | **43 h (14 d)** | 22 h (4 d) |
| **1,267,632** | **Drakonite 23,000** | 60 h (40 d) | **26 h (9 d)** | 14 h (2 d) |
| 2,727,634 | Amberite 30,000 (old) | - | 11 h (4 d) | 6 h (1 d) |
| 4,091,437 | Drakonite 75,000 (old) | - | 7 h (2 d) | 4 h (1 d) |
| 429,354 | Amberite 9,300, **half-time** mining | 848 h | 134 h (45 d) | 54 h (9 d) |
| 633,816 | Drakonite 23,000, half-time mining | 201 h | 67 h (22 d) | 32 h (5 d) |

Reading: the old prices make the Tab a one-to-two-day formality; the re-fit makes it a one-to-two-week one for someone mining Z5 ore all day, which is the "genuine edge" the Ember check allowed for Ember. A real Zone 5 hour is also combat, the dragon, quests, so the half-time rows are the honest centre. To hold a regular miner at ~200 h the rate would have to be 215,000 (Amberite) or 315,000 (Drakonite) per hour, 2.4-3.5x today's; that also raises the Tab bill to 26-38M at the reveal and drags every income-scaled coin price with it (slayer costs), so **do not**; keep 90,000 and re-measure with a real Zone 5 profile (Tab doc local test).

## 5. The new price ladder (ore / bar / Enchanted / Block)

Bars +20% over inputs (loop 0.982, C13); Enchanted = 160 raw x 1.10 from **raw only**; Block = 160 Enchanted x 1.045, floored (recommended fix of `research/cloud/Chain-Premium-Fix.md`; the old x1.155 Block is in brackets). Drakonite Bar = 1.2 x (1 ore + 1 Drake Scale at 9,000).

| Material | Ore base | Bazaar buy / sell | Bar | Enchanted | Enchanted Block (old x1.155 in brackets) | Block under 1e9 |
|---|---|---|---|---|---|---|
| Mithril (ref) | 1,440 | 1,584 / 1,296 | 1,728 | 253,440 | 42,375,168 (42,577,920) | yes (4%) |
| Onyxium (ref, no source) | 3,712 | 4,083 / 3,341 | 4,454 | 653,312 | 109,233,766 (109,756,416) | yes |
| Ember Ore | 4,300 | 4,730 / 3,870 | 5,160 | 756,800 | 126,536,960 (127,142,400) | yes (13%) |
| **Amberite Ore** | **9,300** (was 30,000) | 10,230 / 8,370 | **11,160** (was 36,000) | **1,636,800** (was 5,280,000) | **273,672,960** (887,040,000) | yes (27%) |
| **Drakonite Ore** | **23,000** (was 75,000) | 25,300 / 20,700 | **38,400** = 1.2 x (23,000 + 9,000) (was 100,800) | **4,048,000** (was 13,200,000) | **676,825,600** (2,217,600,000) | **yes (68%)** (was 222%) |

Loop checks (python): bar 0.9 x 1.2 / 1.10 = 0.9818; Enchanted from raw 0.9000; Block 0.9405; chain 1.1495 <= 1.15. Nothing is made from bars.

Side prices that move with the ore:
- **Fossil Shard (600)**: 10% per Amberite ore = 60 coins an ore, 0.65% of 9,300 (was 0.2% of 30,000); selling 40 shards/h earns 17,910 coins/h. Keep 600.
- **Drake Scale (9,000)**: now 39% of the ore price (was 12%) and 28% of the 32,000 of bar inputs. Selling 32 scales/h (8% of ~400 kills/h) earns 86,258 coins/h, 96/h earns 216,247 coins/h: small next to 1.27M, so **keep 9,000** and re-check when the real kill rate is known. R5: mobs give no coins, so the scale is only a loot value.
- **Kits** (38 bars + 24 Enchanted = 3,840 ore): Amberite = 3,878 ore-equivalents = 9.7 h at 400/h, Bazaar buy cost 39.7M; Drakonite = 16.2 h at 240/h, buy cost 98.8M (+ 38 scales, 6 Dragon Scales). Mining your own gear beats buying it by about 4.9x (floor 0.225 vs buy 1.10), the same reading as the Ember check; the gate stays time, not coins.

## 6. Server Setup rows (placeholders)

`bazaar.base.Ore_Amberite` 9,300 and `bazaar.base.Ore_Drakonite` 23,000 (via `/bazaaradmin price`, the live path; Ember 4,300 stays), `bazaar.base.Drake_Scale` 9,000 (unchanged), `bazaar.maxChainPremium` 15, `enchanted.blockStep` 4.5, `tab.perHour` 90,000 (unchanged), `ore.z5.amberite.regrowSec` 2,400, `ore.z5.drakonite.regrowSec` 900 (unchanged; Drakonite pocket enlarged only if Q3 of `research/cloud/Ore-Regrow-Spec.md` says so).

## For the local session (UNVERIFIED)

1. Real blocks per hour for Amberite and Drakonite (timed 30-minute runs with the new densities): 198 / 112 is a two-point model fitted to other model values, not a measurement.
2. Real Fortune of a Zone 5 miner (this file uses x2.0; x1.77 at skill 50 lowers incomes 11%).
3. The real endgame coins/h of a Zone 5 test profile (Tab doc local test) - this file's incomes are single-ore upper bounds.
4. That the Bazaar's per-product ceiling is 1e9 (Drakonite old Block 2.2 billion), and whether the build accepts a base of 23,000 with an Enchanted of 4,048,000 (step 4.0 cap, `build_skyybazaar_0.1.5.py` line 2964).
5. Whether Drakonite's pocket (4,400 blocks) survives a crowd: needs a live player count at Zone 5 (Ore-Regrow-Spec Q3).
6. Whether the Bazaar's buy side drifts (`research/cloud/Bazaar-Drift-Check.md`: yes, small); the prices here assume the model's plain floor behaviour.
7. Drake Scale / Fossil Shard drop rates (8% / 10%) and kill rates are the Zone-4-5 placeholders.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Amberite 30,000 -> 9,300 and Drakonite 75,000 -> 23,000 (ladder x2.16 / x2.47 above Ember 4,300)? | [yes] |
| 2 | Or a lower fit (about 6,700 / 11,200 = 1.5x the Ember miner) so the Tab stays a 100+ hour race for Zone 5 miners? | [no; re-measure first] |
| 3 | Keep `tab.perHour` at 90,000 and re-measure with a Zone 5 test profile? | [keep] |
| 4 | Allow the Enchanted Drakonite Block now that it fits the 1e9 ceiling (676,825,600)? | [yes, as a later Block] |
| 5 | Keep Drake Scale at 9,000 although it is now 39% of the Drakonite ore price? | [keep, re-check with real kill rates] |
