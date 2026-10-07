# Bazaar buy-side drift check - does buying use the demand factor, and can a buy-low / sell-high loop run?

Cloud draft, 2026-10-07. Paper design; nothing built. Inputs read (read-only): `SkyyBazaar/build_skyybazaar_0.1.5.py` (the newest build script; Market class lines 2923-3170, trade core 3645-3860, header comments 236-295, build-time loop check 1379-1394 and 1624-1750), `research/cloud/Ember-Economy-Check.md` (section 7 exploit 2, the UNVERIFIED this file closes), `research/cloud/Economy-Audit.md` (section 1 model, C4, C13). All arithmetic is python3 in scratch only, written from the script's own formulas (nothing run against the game).

## 0. The decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/economy.md` LOCKED 2026-10-03 | processed goods +20% over inputs, row 0-22%; above 22.2% a buy-ore-smelt-sell loop pays |
| `docs/answered/economy.md` LOCKED 2026-10-04 | metal ore bases x2 per tier step (the prices in the sims) |
| `docs/answered/bags.md` LOCKED 2026-10-06 (Q10 tweak) | Enchanted sells a premium above 100x base, "capped below any buy -> compress -> sell loop" |
| R3 | coins never skip collections; a drift loop is a coin faucet, not an unlock bypass, so R3 is untouched |

## 0.1 Answer

1. **Yes, the buy price follows the same demand factor as the sell price.** Buy = base x factor x 1.10, sell = base x factor x 0.90. Every unit bought multiplies the factor by `step`, every unit sold divides it by `step` (section 1).
2. **A drift loop exists, but it is small and cannot be started by one player.** The buy-low / sell-high edge is real (a floored ore buys at 0.275 x base while its bar sells at 1.08 x base: 3.9x on the first unit), but the buy itself pushes the factor back up, so the edge shrinks to zero after 16 Ember crafts. Harvest per full gap is about **25,000 coins whatever the ore costs**, and sustained about **2,000-4,500 coins/h per ore-to-bar pair** (about 1% of the dumpers' income). The 3.6x of the Ember check is only the first-unit ratio.
3. **No lone-player loop:** every sell-then-buy and buy-then-sell cycle, with any wait for the decay in between, loses money (section 4). The loop needs someone else (a dumper) to push one product's factor away from the others.
4. **Recommended fix (cheap, optional):** a buy-side factor floor, `bazaar.buyFactorFloor` 0.9 (buy price = base x max(factor, 0.9) x 1.10). It cuts the Ember pair's harvest from 4,559 to 86 coins/h (section 6). Quote the three places to patch (section 7). No fix is needed for safety, only for tidiness; the sim says the exposure is about 1% of endgame income per pair.

## 1. Exactly how the script prices (line numbers are in `SkyyBazaar/build_skyybazaar_0.1.5.py`)

| Piece | Code | Line(s) |
|---|---|---|
| Constants | `IMPACT = 10000.0`, `HALFLIFE = 120.0` (minutes), `MINF = 0.25`, `MAXF = 4.0`, `SPREAD = 0.10` | 2926-2930 (SPREAD from `SPREAD = 0.10` at line 311) |
| Clamp | `clampF`: NaN -> 1.0, below 0.25 -> 0.25, above 4.0 -> 4.0 | 2938-2943 |
| Step per unit | `step(p) = exp(ln(1.10) x p.base / IMPACT)`, floor 1.0, **cap 4.0** | 2961-2966 |
| Price of qty units | `quote(id, qty, buy)`: `mult = buy ? 1 + SPREAD : 1 - SPREAD`; for each unit `total += p.base * f * mult; f = clampF(buy ? f * st : f / st)` | 2969-2982 (loop 2976-2979) |
| Rounding | buys `ceil`, sells `floor`, once per trade (not per unit) | 2981 |
| Single unit price | `unit(id, buy) = p.base * factor(id) * (buy ? 1 + SPREAD : 1 - SPREAD)` | 3009-3013 |
| "How many can I afford" | `maxBuyable` repeats the quote walk | 2989-3007 (price line 2999) |
| Moving the factor | `apply(id, qty, buy)`: same walk, stores `F.put(id, f)` | 3045-3060 |
| Decay | every 10 s tick: `k = 0.5^(dt / (HALFLIFE x 60000))`, `nf = clampF(exp(ln(f) x k))`, so the half-life is **on ln(factor)**, back to 1.0 | 3065-3083 (3070-3076) |
| Trades | `buy0` calls `Market.quote(id, qty, true)` (3653), takes coins, gives items, then `Market.apply(id, real, true)` (3680); `sell0` quotes (3721) and applies (3759) | 3645-3770 |
| Build-time loop proof | `loop_check` and the premium bound use **factor 1.0** only: `cost = base x (1 + spread)`, `liq = base x (1 - spread)` | 1379-1394, 1624-1625 |
| What the header says about drift | "Factors can still drift apart ... that is market arbitrage and it corrects itself (it moves both factors back)" | 267-269 |

Facts that matter for the question:

- The factor is **per product id** (`F` is a map keyed by id). Nothing links an ore to its bar, so a recipe pair can have two very different factors.
- Buy and sell walk the **same path** (one multiplies, one divides), so buy N then sell N loses about 2 x spread (header line 246), and a sell followed by a buy later also loses (section 4).
- The step is in **coins of base value traded**: `step = exp(0.0953 x base / 10,000)`. Copper (5) moves 0.005% per unit, Mithril 1.4%, Ember at 4,300 4.2%, Ember at 11,000 11%, any Enchanted (base above 25,000) hits the cap of 4.0, so it **floors after one sale**.
- The build proves "no loop" only at factor 1.0. Drift between products is not covered; the header relies on arbitrage correcting it.

## 2. The drift edge (one-shot, static factors)

Setup: ore factor `f_ore` (pushed down by sellers), bar factor 1.0 (smelted bar = +20%, 1 ore -> 1 bar). The arbitrageur buys 1 ore (walking the ore factor up), smelts, sells 1 bar (walking the bar factor down), and repeats while the unit pays. Profit in coins; "return" = (profit + spent) / spent.

| Ore (base) | `f_ore` start | Crafts until the edge is gone | Profit | Return | Ore factor at the end |
|---|---|---|---|---|---|
| Copper (5) | 0.25 | 13,048 | 24,775 | 2.00 | 0.47 |
| Mithril (1,440) | 0.25 | 46 | 25,355 | 2.01 | 0.47 |
| Ember (4,300) | 0.25 | 16 | 26,524 | 2.01 | 0.48 |
| Ember (11,000) | 0.25 | 6 | 29,285 | 2.22 | 0.47 |
| Mithril (1,440) | 0.50 | 23 | 8,748 | 1.41 | 0.69 |
| Ember (4,300) | 0.50 | 8 | 9,541 | 1.44 | 0.69 |
| Ember (4,300) | 0.90 | 1 | 387 | 1.09 | 0.94 |
| any | 1.00 | 0 | 0 | - | - |

**The size of a gap is about 25,000 coins, not a multiple of the item price.** The reason is the impact rule: 10,000 coins of base value traded moves a factor 10%, so closing a 0.25 -> 0.47 gap costs a fixed amount of trading volume whatever the item costs. The expensive ores just do it in fewer units. The first-unit edge on Ember is 0.9 x 1.2 / (1.10 x 0.25) = **3.93x** (bars) or 3.6x (Enchanted, as in the Ember check); it is the average over the gap that counts, and that is 2.0x only on money that is a few thousand coins.

Enchanted from raw (160 ore -> 1 Enchanted, +10%) is **worse** for the arbitrageur on the expensive ores: the 160 buys walk the ore factor up 4.2% per unit (Ember) and the Enchanted floors after one sale, so Mithril and Ember Enchanted never pay even at `f_ore` 0.25. Only Copper / Iron-class ores (where 160 units barely move the factor) pay, and then by about 22,000 coins per gap. The same 25k cap applies.

## 3. Sustained drift (dumpers + one arbitrageur, 96 h, exact decay)

Dumpers sell `d` ore per hour (the Ember check's endgame rates: Copper 800, Mithril 560, Ember 412) in six slices per hour. Arbitrageur A buys ore and sells bars whenever one craft pays. B waits `T` hours between bursts so the bar factor recovers.

| Pair | Dumper income/h (no arbitrageur) | A: continuous profit/h | B: best burst profit/h (T) | B as % of dumper income |
|---|---|---|---|---|
| Copper 5 | 3,261 | 4 | 31 (4 h) | 1.0% |
| Mithril 1,440 | 182,926 | 1,986 | 4,287 (2 h) | 2.3% |
| Ember 4,300 | 397,071 | 2,071 | 4,559 (2 h) | 1.1% |
| Ember 11,000 | 1,012,739 | 2,621 | not run | - (A: 0.3%) |

The arbitrageur also **helps** the dumpers a little (their income rises 0.4-3.5% because the buys lift the ore factor). The profit is capped by the half-life: after a burst both factors need about 2 h to recover, so the best interval is 2-4 h. Even if 20 ore-to-bar pairs (an assumed count, not read from the script) were farmed at once, the cap is about 20 x 4.5k = 90k coins/h, about a quarter of the endgame income of 360k, and it needs dumpers on all 20 at the floor, which the audit's endgame basket does not have (4 products).

## 4. Can one player run it alone? No (sim + proof)

Rule used by the sim: buy and sell walk the same factor path, and the decay only ever moves a factor **toward 1.0**.

| Cycle (one player) | Result |
|---|---|
| Sell 200 Mithril, buy 200 straight back | net -313,946 coins (got 103,382, paid 417,328) |
| Sell 200 Mithril, wait 60 / 120 / 480 min, buy 200 | net -486,769 / -605,010 / -837,206 (the wait makes it worse: the factor recovers, so the buy starts higher) |
| Sell 200 Ember (4,300), wait 120 min, buy 200 | net -2,986,614 |
| Buy 200 Mithril, wait 120 min, sell 200 | net -788,986 |
| Sell 5,000 Copper, wait 120 min, buy 5,000 | net -7,544 |
| Sell ore, buy it back, smelt, sell the bars (Ember 200) | -2,422,820 vs +272,055 for simply smelting and selling |

Proof sketch: after selling N the factor sits at `f / st^N`; decay moves it up to `f' >= f / st^N`, so the later buy path `[f', f' x st^N]` lies above the sell path `[f / st^N, f]` everywhere, and buy costs 1.10 against 0.90. The mirrored argument holds for buy-then-sell. A loop needs a **third party** to push one product's factor.

## 5. Where the exposure really sits

| Place | Exposure | Reading |
|---|---|---|
| Live Bazaar today (bars +20%, 0.982 at factor 1.0) | any ore factor under 0.98 against a bar at 1.0 pays | exists now (any heavy ore seller creates it), harvest about 2k/h per pair |
| Zone 4-5 ores after the density cut and price fixes | Ember 4,300: about 4.5k/h per pair at best | tiny against 419k/h |
| Enchanted from raw | Mithril / Ember never pay; Copper / Iron up to 22k per gap | negligible |
| Block (chain 1.15) | needs 25,600 raw: the walk closes the gap long before | none |
| Anything processed from a processed good | already a hard loop at factor 1.0 (1.08), unrelated to drift | stays banned (Economy-Audit C4) |

Risks the drift adds: (a) it is invisible in the current checks (they run at factor 1.0), (b) the floor of 0.25 makes the dumpers' own income 0.225 x base, so cheap buys of the same ore look even more unfair next to it, (c) alts: an alt farms the pair while the main dumps, same market, nothing stops it.

## 6. The fix (simulated with the script's formulas, floor applied to the buy side only)

`buy price = base x max(factor, F) x 1.10`, sell unchanged. Burst arbitrageur, best `T` of 1, 2, 4, 8 h:

| `buyFactorFloor` F | Mithril pair profit/h | Ember 4,300 pair profit/h | Buy price of a floored ore | Cost to honest buyers |
|---|---|---|---|---|
| 0 (today) | 4,287 | 4,559 | 0.275 x base | none |
| 0.5 | 1,960 | 2,016 | 0.55 x base | small |
| 0.75 | 426 | 484 | 0.825 x base | medium |
| **0.9 (recommended)** | **60** | **86** | 0.99 x base | the buy never sinks below base: the dumper's own price floor does not help buyers |
| 1.0 | 0 | 0 | 1.10 x base | largest: no cheap buys at all |

Why 0.9 and not 1.0: at 1.0 a floored ore still sells for 0.225 x base but buys at 1.10 x base (4.9x spread); at 0.9 the buy is 0.99 x base (4.4x), and the residual edge is under 100 coins/h. The Ember check proposed the same 0.9. Alternative that costs honest buyers nothing: leave buys alone and cap the **ratio** between a recipe's input and output factors (needs the recipe graph at run time: `Catalog.loopingEdges` exists at build time only, lines 1809-1844) - more code for the same 1% exposure, not recommended.

## 7. Patch sketch (do not edit the generated script; derive a patch from the current pin per PROJECT-RULES section 4)

All three prices read the factor through the same expression, so the floor must be applied in all three or the page and the trade disagree:

1. `quote()`: line 2977 `total += p.base * f * mult;` -> use `Math.max(f, buy ? FLOOR : 0.0)` in place of `f` for the price only; the walk line 2978 stays (so the factor still moves from its true value).
2. `maxBuyable()`: line 2999, the identical line.
3. `unit()`: line 3012 `return p.base * factor(id) * ...` same change.
4. New static `FLOOR` next to `MINF` / `MAXF` (lines 2929-2930), read from `market.properties` key `buyFactorFloor` (load at 3091-3100, save at 3122-3125), default 0.9, shown in Server Setup (`tools/skyycfg.py`).
5. `trades.log` line 3690 prints the real factor, unchanged.
6. Earlier headers (lines 146-147) say Market is "asserted byte-identical" between versions: the patch must lift that assert for these lines.

UNTESTED: no javac here; the local session runs the existing `SkyyBazaar/test_skyybazaar_0.1.5.py` plus one test that quotes a floored ore.

## For the local session (UNVERIFIED)

1. The script is the 0.1.5 source; confirm the **deployed** jar is 0.1.5 and that `market.properties` still holds `impactCoins=10000`, `halfLifeMinutes=120`, `spread=0.10` (an admin may have edited them; they are read at line 3091-3100).
2. Real factors after a normal week (`f.<id>` in `Skyy_SkyyBazaar/market.properties`): which ore / bar pairs actually sit apart, to size section 5 with data (Economy-Audit section 8 item 5).
3. Whether any NPC or planned order-book feature (`PLANNED 0.2`, header lines 280-295) fills at the market-maker price and moves the factor; an order book would add real counter-parties and change section 3.
4. That a live Enchanted product follows the same `step` cap of 4.0 (the Enchanted ids do not exist in 0.1.5; all Enchanted rows are model values).
5. The 10 s decay tick (`BzTick`, line 4638-4645) and `publishAll` after every decay: no effect on the maths, but check the cost of the 400+ product loop.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Add a buy-side factor floor (`bazaar.buyFactorFloor`) so a dumped ore is never bought below 90% of base? | [yes, 0.9, in the next Bazaar round] |
| 2 | Or accept the drift (about 1% of income per pair) and only watch it with the weekly factor snapshot? | [no; the floor is cheap] |
| 3 | Should alts / profiles share one factor per product (today: yes, one market)? | [yes, unchanged] |
