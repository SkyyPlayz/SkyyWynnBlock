# Enchanted chain premium fix - 1.10 x 1.05 = 1.155 is over the 15% cap

Cloud draft, 2026-10-07. Paper design; nothing built. Inputs read: `research/cloud/Economy-Audit.md` (C4, C13, Q6, section 7 rows), `research/cloud/Enchanted-Materials-Draft.md` (section 6 table, lines 112-135), `research/cloud/Zone-4-5-Materials.md` (section 5, line 15, lines 82-93), `research/cloud/Ember-Economy-Check.md` (section 5, side finding), `docs/answered/bags.md` and `docs/answered/economy.md` locks. All arithmetic is python3 with exact fractions, scratch only (not in the repo).

## 0. The decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/bags.md` LOCKED 2026-10-06 (spec Q10 tweak) | "Enchanted items sell a bit ABOVE 100x base (a premium, capped below any buy -> compress -> sell loop, like the processed-goods 22% rule)". No number is locked |
| `docs/answered/bags.md` LOCKED 2026-10-06 (spec Q4) | launch with 18 Enchanted items, **no Enchanted Blocks yet** (every Block edit below is paper only for now) |
| `docs/answered/economy.md` LOCKED 2026-10-03 | processed goods +20%, row 0-22%; above 22.2% a buy-process-sell loop pays |
| `research/cloud/Economy-Audit.md` C4 (a proposal, not a lock) | the chain from a Bazaar-buyable input stays <= 15% (`bazaar.maxChainPremium`); Enchanted only from raw items, never from bars |

## 0.1 Answer

1. **Recommend option A: Enchanted stays +10%, the Block step becomes +4.5%** (Block = 160 Enchanted x 1.045, rounded down). Cumulative 1.10 x 1.045 = **1.1495**, under 1.15 for all 25 materials checked (exact, after rounding down).
2. The bug is real but small: at 1.155 the loop ratio (buy raw at 1.10, sell the Block at 0.90) is 0.9450, at 1.1495 it is 0.9405. The drift headroom moves from 5.8% to 6.3%. The loop line is 22.2%; the 15% cap is a safety margin, so this is housekeeping, not a hole.
3. Option A touches the fewest numbers: the **Enchanted** rows (the first thing to launch, 18 items) stay as they are, only the Block column and four sentences change in four research files (section 5).
4. Option B (Enchanted +9.5%) changes every Enchanted row and the "10%" wording in the Enchanted docs. Option C (round the chain down to 1.15) is exact but makes the Block price differ from 160 x the Enchanted price.

## 1. The rule and the maths

Bazaar: instant buy = base x factor x 1.10, instant sell = base x factor x 0.90. Buying 25,600 raw, crafting up the chain, and selling the Block pays when `0.90 x chain > 1.10`, i.e. chain > 1.2222. Ratio shown below = `0.90 x chain / 1.10`; **headroom** = 1 / ratio - 1 = how far the Block's demand factor may sit above the raw's factors before the loop pays (the audit saw about 2% drift in the 0.1.4 log).

| Option | Enchanted step | Block step | Chain | Loop ratio | Headroom | Over the 15% cap? |
|---|---|---|---|---|---|---|
| Now (audit C4 / Zone-4-5) | 1.10 | 1.05 | 1.1550 | 0.9450 | 5.82% | **yes, by 0.5 pt** |
| **A: Block +4.5%** | 1.10 | 1.045 | **1.1495** | 0.9405 | 6.33% | no |
| B: Enchanted +9.5% | 1.095 | 1.05 | 1.14975 | 0.9407 | 6.30% | no |
| C: cap at 1.15 by rounding | 1.10 | min(1.05, 1.15 / 1.10 = 1.04545) | 1.1500 | 0.9409 | 6.28% | no (at the cap) |
| D: leave it, state the row as 15.5% | 1.10 | 1.05 | 1.1550 | 0.9450 | 5.82% | rule changed |

Single steps: Enchanted alone 0.9000 at 1.10 (0.8959 at 1.095), the Block step alone 0.8591 at 1.05 (0.8550 at 1.045). Neither is near 1.0. Enchanted made from bars is still a hard loop (0.9 x 1.32 / 1.10 = 1.08) and stays banned (C4 rule 2).

## 2. Every material (python: floor to whole coins, as the Bazaar's "never above the exact value" rounding)

Block = floor(160 x Enchanted x step); Enchanted = floor(160 x base x step). Chain = Block / (25,600 x base). Option A: chain 1.1495 on **every** row; option C: 1.1500 on every row; option B: 1.1484 - 1.1498; now: 1.1550 on every row (25 of 25 over the cap).

| Material (source table) | Base | Enchanted (now, A, C) | Block now | **Block A** | B: Enchanted | B: Block | C: Block |
|---|---|---|---|---|---|---|---|
| Cobblestone / Sand / Fiber (draft) | 1 | 176 | 29,568 | **29,427** | 175 | 29,400 | 29,440 |
| Copper Ore | 5 | 880 | 147,840 | **147,136** | 876 | 147,168 | 147,200 |
| Iron Ore | 16 | 2,816 | 473,088 | **470,835** | 2,803 | 470,904 | 471,040 |
| Thorium Ore | 48 | 8,448 | 1,419,264 | **1,412,505** | 8,409 | 1,412,712 | 1,413,120 |
| Cobalt Ore | 144 | 25,344 | 4,257,792 | **4,237,516** | 25,228 | 4,238,304 | 4,239,360 |
| Adamantite Ore | 480 | 84,480 | 14,192,640 | **14,125,056** | 84,096 | 14,128,128 | 14,131,200 |
| Mithril Ore (also Zone-4-5 ref) | 1,440 | 253,440 | 42,577,920 | **42,375,168** | 252,288 | 42,384,384 | 42,393,600 |
| Onyxium Ore (also Zone-4-5 ref) | 3,712 | 653,312 | 109,756,416 | **109,233,766** | 650,342 | 109,257,456 | 109,281,280 |
| Common wood F1 | 3 | 528 | 88,704 | **88,281** | 525 | 88,200 | 88,320 |
| Uncommon wood F2 | 8 | 1,408 | 236,544 | **235,417** | 1,401 | 235,368 | 235,520 |
| Northern wood F3 | 20 | 3,520 | 591,360 | **588,544** | 3,504 | 588,672 | 588,800 |
| Strange wood F4 | 48 | 8,448 | 1,419,264 | **1,412,505** | 8,409 | 1,412,712 | 1,413,120 |
| Elemental wood F5 | 128 | 22,528 | 3,784,704 | **3,766,681** | 22,425 | 3,767,400 | 3,768,320 |
| Crop A (Wheat, Carrot, Corn) | 2 | 352 | 59,136 | **58,854** | 350 | 58,800 | 58,880 |
| Crop B (Pumpkin ...) | 6 | 1,056 | 177,408 | **176,563** | 1,051 | 176,568 | 176,640 |
| Crop C (Tomato, Cotton, Rice) | 16 | 2,816 | 473,088 | **470,835** | 2,803 | 470,904 | 471,040 |
| Crop D (Potato, Onion) | 40 | 7,040 | 1,182,720 | **1,177,088** | 7,008 | 1,177,344 | 1,177,600 |
| Tree Sap (draft 4) | 4 | 704 | 118,272 | **117,708** | 700 | 117,600 | 117,760 |
| Tree Sap (live base 12, PRICE_015) | 12 | 2,112 | 354,816 | **353,126** | 2,102 | 353,136 | 353,280 |
| Ember (Zone-4-5 old 11,000) | 11,000 | 1,936,000 | 325,248,000 | **323,699,200** | 1,927,200 | 323,769,600 | 323,840,000 |
| Ember (new 4,300, Ember check) | 4,300 | 756,800 | 127,142,400 | **126,536,960** | 753,360 | 126,564,480 | 126,592,000 |
| Amberite (old 30,000) | 30,000 | 5,280,000 | 887,040,000 | **882,816,000** | 5,256,000 | 883,008,000 | 883,200,000 |
| Amberite (new 9,300, `research/cloud/Zone-5-Ore-Prices.md`) | 9,300 | 1,636,800 | 274,982,400 | **273,672,960** | 1,629,360 | 273,732,480 | 273,792,000 |
| Drakonite (old 75,000) | 75,000 | 13,200,000 | 2,217,600,000 | **2,207,040,000** | 13,140,000 | 2,207,520,000 | 2,208,000,000 |
| Drakonite (new 23,000) | 23,000 | 4,048,000 | 680,064,000 | **676,825,600** | 4,029,600 | 676,972,800 | 677,120,000 |

Notes on the table:
- The Enchanted-Materials-Draft table (lines 118-135) is **stale**: it still shows the first draft's 1.21x (10% + 10%) and rounds Enchanted up (881, 253,441). The audit already changed the Block to +5%; the draft was never updated. Rounding down is the Bazaar's convention (`build_skyybazaar_0.1.5.py` line 2799).
- The ceiling 1e9: Drakonite old 75,000 is over it in every option (2.2 billion); at 23,000 it is 68% of it under A (676,825,600), so the "no Drakonite Block" default of `research/cloud/Zone-4-5-Materials.md` Q5 can flip (see Zone-5-Ore-Prices).
- A uses one multiplier everywhere, so a Block never differs from 160 x the Enchanted price x 1.045 (a clean rule for the Bazaar's auto pricing). Option C's Block is 160 x Enchanted x 1.04545 only approximately, from the raw price: the two prices drift by up to a few coins on cheap items (Copper: 147,200 vs 147,136).
- Margins per material are identical to 4 digits (the chain is a ratio); only rounding differs, and rounding down never pushes a row over the cap (A: 0 of 25 over, B: 0 of 25, C: 0 of 25, now: 25 of 25).

## 3. Comparison

| | A: Block +4.5% | B: Enchanted +9.5% | C: round-cap at 1.15 | D: state 15.5% |
|---|---|---|---|---|
| Chain / cap | 1.1495 (under) | 1.14975 (under) | 1.1500 (at the cap, no spare) | 1.1550 (rule changed) |
| Loop headroom | 6.33% | 6.30% | 6.28% | 5.82% |
| Rows changed (25 above) | Block column only | Enchanted **and** Block columns | Block column + a `min()` rule | none |
| Live items touched | none (Blocks are not launched) | **all 18 launch Enchanted items** | none | none |
| Clean rule for the Bazaar's auto pricing | yes: `blockStep` 4.5% | yes: `premiumStep` 9.5% | no: a second formula | yes |
| Skyy-facing wording | "Block +4.5%" | "Enchanted +9.5%" (an odd number for the item players craft first) | "chain capped at 15%" | "15.5%" |
| Edits in other docs | 4 files (section 5) | 4 files + every Enchanted figure | 4 files + a code rule | 3 files (wording only) |

Why A: it keeps the 10% that the Enchanted draft, the Zone-4-5 tables and the lock's "a bit above 100x" already use; it is the only option that changes nothing that launches; and it is the Ember check's default (Q3), so two drafts agree. D is the lowest-effort option and the maths says it is safe (5.82% headroom), but it changes a rule the audit set; if Skyy prefers fewer edits, D is the honest fallback.

## 4. Server Setup rows (placeholders)

`enchanted.premiumStep` 10 (%), **`enchanted.blockStep` 4.5** (was 5), `bazaar.maxChainPremium` 15. The Bazaar build should refuse a pair of rows whose product (1 + step1)(1 + step2) - 1 exceeds `bazaar.maxChainPremium`, the same way the 0.1.5 build asserts the processed-goods bound (line 1625: `(1 + PREMIUM_MAX/100) x (1 - SPREAD) <= 1 + SPREAD`).

## 5. Exact edits per file (applied 2026-10-07 by the cloud session - all rows below are done)

| File | Where | Change |
|---|---|---|
| `research/cloud/Economy-Audit.md` | C4 row (line 86) | "Enchanted 10%, Block +5% (1.155x)" -> "Enchanted 10%, Block +4.5% (1.1495x)"; the row's first sentence ("Block = 1.21x") stays as the historic problem |
| `research/cloud/Economy-Audit.md` | section 7 (line 111) | `enchanted.blockStep` (5%) -> (4.5%) |
| `research/cloud/Economy-Audit.md` | Q6 (line 145) | "+5% on top" -> "+4.5% on top" and default [+4.5%] |
| `research/cloud/Enchanted-Materials-Draft.md` | section 6 text (line 114) | "(a Block 21%)" -> "(a Block 14.95%)"; add the sentence "Block = 160 Enchanted x 1.045" |
| `research/cloud/Enchanted-Materials-Draft.md` | section 6 table (lines 117-135) | header "block vs 25,600 base" stays; replace both value columns with the **Enchanted (now, A, C)** and **Block A** columns of section 2 above; the ratio column becomes 1.15x (1.1495) |
| `research/cloud/Enchanted-Materials-Draft.md` | section 7 (line 136 area) | add `ench.blockPremium` (4.5) beside `ench.bazaarPremium` (10) |
| `research/cloud/Zone-4-5-Materials.md` | line 15 | "Block +5% (1.155x)" -> "Block +4.5% (1.1495x)" |
| `research/cloud/Zone-4-5-Materials.md` | section 5 table (lines 82-88) | header "(25,600 raw x 1.155)" -> "(160 Enchanted x 1.045)"; Block cells: Mithril 42,375,168, Onyxium 109,233,766, Ember 323,699,200 (at 11,000; see Zone-5-Ore-Prices for the re-fit), Amberite 882,816,000 (89% -> 88%), Drakonite 2,207,040,000 |
| `research/cloud/Zone-4-5-Materials.md` | loop bullet (line 93) | "Block 0.9 x 1.155 / 1.10 = 0.945; cumulative chain premium 1.10 x 1.05 = 1.155 <= 15%" -> "Block 0.9 x 1.1495 / 1.10 = 0.9405; cumulative 1.10 x 1.045 = 1.1495 <= 15%" |
| `research/cloud/Ember-Economy-Check.md` | sections 0 (item 4), 4 table (Block row), 5 | Fix A becomes "adopted"; Block at 4,300 = 126,536,960 (the file's own Fix A number), not 127,142,400; drop "see 5 for 1.155" |
| the docs/answered files and the SkyyGear design docs | - | nothing: no number of this rule is locked; do not edit |

Keep the file's own line endings when editing (PROJECT-RULES section 5).

## For the local session (UNVERIFIED)

1. The Bazaar's per-product price ceiling (assumed 1e9) and how the build rounds an auto-priced Enchanted / Block (this file assumes floor to whole coins; the 0.1.5 script floors auto prices to 0.01, line 2799).
2. Whether the Enchanted products will be AUTO priced from their inputs (then `blockStep` is a row) or FIXED (then the table above is the price list and the build must assert chain <= `bazaar.maxChainPremium`).
3. Rerun the exact loop check (2,252 recipes + the new Enchanted / Block recipes) with the final steps; this file checks the chain only, not every alternative recipe.
4. The factor drift between a raw material and its Enchanted form: `research/cloud/Bazaar-Drift-Check.md` found the profit capped near 25k coins per gap, so 5.8% vs 6.3% headroom is not decisive.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Fix the chain over-cap with Block +4.5% (Enchanted stays +10%)? | [yes, A] |
| 2 | Or leave it at 15.5% and change the written rule to "<= 15.5%"? | [no, only if you want the fewest edits] |
| 3 | Round Bazaar prices of Enchanted forms down (never above the exact value, like bars), not up as the draft table did? | [yes, down] |
