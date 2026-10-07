# Ember economy check - is 11,000 coins right after the density cut?

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/cloud/Zone-4-5-Materials.md` (sections 3, 5, 7: Ember 11,000, bars +20%, Enchanted +10%, Block +5%, kit sizes), `research/cloud/Ore-Regrow-Spec.md` (sections 4, 8: Ember 21 -> 7 ore / cell, Z5 3.5, timers 1,800 / 1,200 s), `research/cloud/Economy-Audit.md` (sections 1-2, C4, C13: Bazaar maths, endgame ~360k/h), `research/cloud/Bank-Tab-Calibration.md` (section 2.3: `tab.perHour` 90,000, payoff sim), `research/cloud/Gathering-Numbers-Reconciled.md` (Fortune cap 100), `docs/answered/economy.md` (LOCKED 2026-10-04 ore ladder, R3). All arithmetic is python3, scratch only (not in the repo).

## 0. Answer

1. **Lower it: Ember Ore 11,000 -> 4,300** (= Mithril 1,440 x 3.0, one ladder step; Onyxium has no source, so Ember is the next step after Mithril, not after Onyxium).
2. At 11,000 an endgame Ember miner earns **~1.04M coins/h after the density cut (1.41M before)** = 3.1x (4.2x) the audit's endgame ~336-360k/h and ~11x `tab.perHour` 90,000. The cut helps (-26%) but is nowhere near enough. At 4,300 the same miner earns **~419k/h** (1.2x the audit) and the audit's basket with Ember in the unobtainable Onyxium's slot gives 363k/h (audit: 336k).
3. The Tab then keeps its calibration: `tab.perHour` stays 90,000 (or 105,000 = 25% of 419k; payoff times barely move, section 6). Left at 11,000 a regular player pays the Tab in ~34 online hours (11 days) instead of ~205 h (68 days).
4. Side finding: the Enchanted chain rule as written is **15.5%, not <= 15%** (1.10 x 1.05 = 1.155). Fix = Block +4.5% (section 5) - adopted 2026-10-07 in the cloud drafts (`research/cloud/Chain-Premium-Fix.md`). Not an Ember problem; it is in all Blocks.

## 1. The Bazaar model used (so the numbers can be checked)

From `Economy-Audit.md` section 1: sell = base x factor x 0.90; each unit sold divides the factor by `exp(ln 1.10 x base / 10,000)`; factor clamped 0.25-4.0; decays to 1.0 with a 120-minute half-life (UNVERIFIED: I assumed half-life on ln(factor); a linear decay changes totals by under 1%).
**Calibration:** I re-ran the audit's endgame basket (200 items/h each of T5 log 128, Adamantite 480, Mithril 1,440, Onyxium 3,712, 2-hour session): **336,460 coins/h**, the audit's F3 value (336,000). So this sim matches the audit's.
The key fact: Ember's per-unit impact is `exp(0.0953 x 1.1)` = **-10.5% per unit**, so after ~13 units the factor sits on the **0.25 floor**. A miner selling 400+ Ember per hour is always at the floor: **coins/h = items/h x base x 0.225**. At the floor the Bazaar price is the whole story: coins/h scales 1:1 with the base price.

## 2. Ember mined per hour (endgame miner)

Inputs: 280 ore/h "with walking" is the Zone-4-5 placeholder at the OLD density (21 ore / cell, 3 veins / cell). Items per block = 1 + Fortune / 100; an endgame miner has Fortune 100 (clamp `perk.doubleDropMax`; Gathering-Numbers section 2: maxed Mining reaches 100 at skill ~35-50) = **x2.0**.
Model: time per ore = fixed part (swing, smelt-free) + walking part. Swing at endgame is ~0.3-1 s per ore (`Tool-Levels-Revision.md` section 4), so the 12.9 s per ore of the 280 placeholder is mostly walking and finding veins. Veins per cell 3.0 -> 1.0 means the gap between veins grows by x1.73 (surface, 2D) to x1.44 (caves, 3D); I use **x1.6**. Veins keep 5-9 ore, so ore per vein is unchanged.

| Walking share of the old 12.9 s per ore | Blocks / h old | Blocks / h new (x1.44 / **x1.6** / x1.73) | Items / h new (Fortune 100) | Items / h old |
|---|---|---|---|---|
| 30% (ore is easy to spot, glows) | 280 | 247 / **237** / 230 | 474 | 560 |
| **60% (central)** | 280 | 222 / **206** / 195 | **412** | 560 |
| 92% (walking is everything) | 280 | 199 / **180** / 168 | 360 | 560 |

Z5 Ember (1.0 -> 0.5 veins / cell, a further x1.26-1.41 gap): ~140-170 blocks/h (central 169), 280-340 items/h. Z5 players choose between this and Amberite (200/h, 30,000).
**Result: the cut costs an endgame miner 15-36% (central -26%).** It is the right direction but it does not fix the price (section 3).
**Regrow check** (Ore-Regrow-Spec 4): 20 miners x 206 = 4,120 blocks/h against a supply of 35,500/h (71,000 blocks, 25% access, T 1,800 s) = **12% utilisation** (the spec's 16% used 280). Z5: 834 / 7,200 = 12%. Regrow is not the limit, so the walking time is the real throttle and the density cut is what holds the rate, not the pile.

## 3. Coins per hour sold to the Bazaar

All rows: Fortune 100 (x2 items), 2-hour session, the sim above. "Audit endgame" = 336-360k/h (F3 + ~25k of the other active faucets).

| Ore (zone, blocks/h) | Base | Items/h | Coins/h at the floor | Coins/h (sim) | x audit endgame (336k) | x Mithril |
|---|---|---|---|---|---|---|
| Mithril (Z3-4, 280) | 1,440 | 560 | 181,000 | 201,000 | 0.6 | 1.0 |
| **Ember old density (280)** | 11,000 | 560 | 1,386,000 | **1,408,000** | **4.2** | 7.0 |
| **Ember new density (206), 11,000** | 11,000 | 412 | 1,020,000 | **1,042,000** | **3.1** | 5.2 |
| Ember new density, 7,400 | 7,400 | 412 | 686,000 | 707,000 | 2.1 | 3.5 |
| Ember new density, 5,500 | 5,500 | 412 | 510,000 | 531,000 | 1.6 | 2.6 |
| **Ember new density, 4,300 (proposal)** | 4,300 | 412 | 399,000 | **419,000** | **1.2** | **2.1** |
| Ember Z5 (169), 4,300 | 4,300 | 338 | 327,000 | ~347,000 | 1.0 | 1.7 |
| Amberite (Z5, 200), 30,000 | 30,000 | 400 | 2,700,000 | 2,728,000 | 8.1 | 13.6 |
| Drakonite (Z5, 120), 75,000 | 75,000 | 240 | 4,050,000 | 4,083,000 | 12.2 | 20.3 |

Without Fortune (a mid player) Ember at 11,000 and 206/h is 531,000 coins/h; at 4,300 it is 219,000.
**Reading:**
- Ember at 11,000 is the biggest jump on the ladder: **7.6x** Mithril's price (1,440 -> 11,000) for a rate that only falls 26%. The x3-per-step ladder skipped a step (Onyxium, 3,712, has no source), so Ember is priced as the step AFTER an item nobody can get.
- The audit's endgame basket sold Onyxium (a product no one can mine). Replacing it with Ember: **11,000 -> 666,000 coins/h** (2x the audit); **4,300 -> 363,000** (audit 336,000); 7,400 -> 503,000.
- Amberite and Drakonite are even further over (8x, 12x). Those two are not asked here, but the same fix applies: see section 4 "follow-up".
- The sim confirms the audit's own warning: a high base price does not protect the economy, because the Bazaar pays the floor price 0.225 x base forever. The only lever is the base.

## 4. The new Ember price ladder (proposal)

Rule used: price step x3.0 from Mithril (Gathering fit in Zone-4-5 section 5), then verify coins/h <= ~1.25x the audit endgame so `tab.perHour` stays valid.

| | Old (Zone-4-5) | **New** | Rule |
|---|---|---|---|
| Ember Ore base (`bazaar.base.Ore_Ember`) | 11,000 | **4,300** | Mithril 1,440 x 3.0 |
| Bazaar buy / sell | 12,100 / 9,900 | **4,730 / 3,870** | x1.10 / x0.90 |
| Cindersteel Bar (+20%, 1 ore) | 13,200 | **5,160** | loop 0.982 (C13) |
| Enchanted Ember (160 raw x 1.10) | 1,936,000 | **756,800** | from raw only |
| Enchanted Ember Block (160 Enchanted x 1.045, Fix A) | 323,699,200 | **126,536,960** | chain 1.1495 (5) |
| Block under the 1e9 ceiling? | yes (33%) | yes (13%) | |

Step ratios after the change: Mithril -> Ember x3.0 (was 7.6). Kit costs in coin terms fall too (Cindersteel armor, 3,840 ore: 46.5M at the old buy price, 18.2M at the new), but a player who mines it needs 9.3 h at 412 items/h (the Tab and gear gate are about time, not coins).
**Follow-up (not applied, for whoever checks Z5):** to keep coins/h rising ~2x per tier at the new rates, Amberite lands near **9,300** (858k coins/h) and Drakonite near **23,000** (1.27M coins/h), not 30,000 / 75,000. The Enchanted Drakonite Block then fits under 1e9 too (Zone-4-5 Q5). Mark as a proposal; rerun the python on the final rates.

## 5. Enchanted chain premium (<= 15%)

| Step | Value |
|---|---|
| Enchanted (from raw) | x1.10 |
| Block (from Enchanted) | x1.05 |
| **Cumulative** | 1.10 x 1.05 = **1.155 = 15.5%** > the 15% rule (`bazaar.maxChainPremium`) |
| Loop line (buy x1.10, sell x0.90) | 22.2%; 15.5% is safe, but the written rule is broken by 0.5 pt |
| Fix A (adopted 2026-10-07 in the cloud drafts) | Block +4.5%: 1.10 x 1.045 = 1.1495 (Block = 160 Enchanted x 1.045) |
| Fix B | state the row as 15.5% |

Not Ember-specific: Zone-4-5 section 5 and Economy-Audit C4 both wrote "1.155 <= 15%", wrong by 0.5 pt (fixed to 1.1495 on 2026-10-07). Ember is checked against the rule above; at 4,300 the Block would be 126,536,960 under Fix A.
Bars: Enchanted Ember still comes from RAW ore only (a bar premium of 20% + 10% = 1.32 / 1.10 x 0.9 = 1.08, a loop).
Selling Enchanted instead of raw (sim, 412 items/h = 2.6 Enchanted/h): at 4,300 it pays 746k/h over 2 hours (+78% vs raw) but 587k over 6 hours (+45%), because each sale floors the Enchanted's own factor and the half-life is 2 h. That is more than the +10% premium: the gain comes from selling into a fresh factor. At the old 11,000 the same gain is +83% / +46%. It adds pressure to the faucet; the lower base shrinks the absolute coins (see exploit 2).

## 6. Tab payoff (`Bank-Tab-Calibration.md` section 2.3 model, re-run)

Hours online to Paid in Full; casual / regular / hardcore (pay 25% / 40% / 60% of income, 1.5 / 3 / 6 h per day, 150 / 120 / 100 hidden hours). The 360k row reproduces the calibration doc exactly (205 h, 72 h).

| Ember miner earns | `tab.perHour` | casual | regular | hardcore |
|---|---|---|---|---|
| 360,000 (audit endgame, the calibration) | 90,000 | never | 205 h (68 d) | 72 h (12 d) |
| **419,000 (Ember 4,300)** | 90,000 | 1,018 h (679 d) | **142 h (47 d)** | 57 h (10 d) |
| 419,000 (Ember 4,300) | 105,000 (25% of 419k) | never | 206 h (69 d) | 73 h (12 d) |
| 1,042,000 (Ember 11,000, new density) | 90,000 | 80 h (53 d) | **34 h (11 d)** | 17 h (3 d) |
| 1,042,000 | 260,000 (25%) | never | 204 h (68 d) | 72 h (12 d) |
| 1,408,000 (11,000, old density) | 90,000 | 52 h | 23 h (8 d) | 12 h (2 d) |

So: **keep 11,000 and the Tab is a 3-11-day formality unless `tab.perHour` is raised to ~260,000**, which hides the problem (it also makes the Tab bill 31M at the reveal) and every other coin price (Enchanted 1.9M, slayer costs scaled from income, gear in coins) drifts with it. **Lower Ember to 4,300** and `tab.perHour` can stay at 90,000: a regular player pays it off in ~47 days (was 68; the extra income is Ember's genuine edge). Re-measure per the Tab doc's local test before trusting any of it.

## 7. Exploits and risks

| # | Exploit | Reading | Fix / default |
|---|---|---|---|
| 1 | **Sell Ember or use it?** | At the floor, 1 ore sells for 0.225 x base = 968 coins (at 4,300), or 2,475 (at 11,000). Using it: a Cindersteel kit is 38 bars + 3,840 ore (Enchanted part). At 4,300 selling beats buying armor ore at 4,730 by 4.9x, so mining your own gear is correct; there is no reason to sell the kit's Ember. | none; the spread is the sink |
| 2 | **Factor drift loop** (ore floored by sellers, bar / Enchanted at 1.0) | If the BUY price also uses the factor (UNVERIFIED), buying floored ore (x0.25) and crafting into a factor-1.0 Enchanted or bar would pay up to **3.6x** (0.9 x 1.1 / (0.25 x 1.1)). The audit named a ~2% drift in C4; selling 400 ore/h makes it 75%. Ember's -10.5% per unit makes it reach the floor within 13 units. | local check of buy pricing; if the buy uses the factor, clamp `bazaar.buyFactorFloor` 0.9 (a buy never goes below 90% of base) |
| 3 | Enchanted vs raw timing (section 5) | up to +78% in short sessions | none needed; acceptable (it is the market maker's normal first-unit gain) |
| 4 | Smelting bars +20% | 412 ore/h x 40 s = 16,480 furnace-seconds/h = 4.6 furnaces; capped by furnace count, not coins | fine |
| 5 | Pocket Shard output of Ember | the NPC cap (`shops.dailySellCap`, Z5 101k/day) is far below the Bazaar floor value (419k/h) - the NPC route is pennies | none |
| 6 | R3 | coins never buy a collection tier or unlock; Ember bought on the Bazaar does not count toward Mining collection (only player-mined natural blocks count, Ore-Regrow-Spec section 2) | clean |
| 7 | Regrow camping | one vein of 7 ore at T 1,800 s is 14 ore/h; 20 ore/h at 7 ore per vein is a loss vs 206 | none |

## 8. Server Setup rows (placeholders)

`bazaar.base.Ore_Ember` 4,300 (via `/bazaaradmin price`), `bazaar.maxChainPremium` 15 (Block +4.5%), `bazaar.buyFactorFloor` 0.9 (only if exploit 2 is real), `ore.z4.ember.veinsPerCell` 1.0, `ore.z5.ember.veinsPerCell` 0.5, `tab.perHour` 90,000 (unchanged; re-measure).

## For the local session (UNVERIFIED)

1. Real Ember ore per hour with the new density (a timed 30-minute run in Zone 4 at Fortune 100) - my 206 blocks/h is a model; the walking share (30-92%) is a guess.
2. Whether the Bazaar BUY price uses the demand factor (exploit 2), and how the factor decay is coded (half-life on factor or on ln(factor)).
3. The real endgame coins/h of a test profile in Zone 4 (Tab doc #1); this file's 419k is a sim of one Ember-only miner, not a measurement.
4. Real Fortune of a Zone-4 miner (Gathering-Numbers says 100 is reached at skill ~35-50 for a maxed player; a typical player at skill 50 has 77, x1.77 not x2.0).
5. That Cindersteel armor really costs 3,840 ore + bars (Zone-4-5 section 7) and that the Bazaar sells Cindersteel gear nothing.
6. The Amberite / Drakonite follow-up rates (200 / 120 per hour) are the Zone-4-5 placeholders.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Lower Ember Ore from 11,000 to 4,300 (Mithril x3), keeping Onyxium's slot empty? | [yes, 4,300] |
| 2 | Also lower Amberite / Drakonite (about 9,300 / 23,000) in the same pass? | [yes, after the Z5 check] |
| 3 | Block chain premium: +4.5% so the cumulative is 14.95%, or call it 15.5%? | [+4.5%] |
| 4 | Keep `tab.perHour` 90,000 (re-measure after the Z4 test)? | [keep] |
| 5 | If the Bazaar buy uses the demand factor, clamp buy at 90% of base? | [yes, if it does] |
