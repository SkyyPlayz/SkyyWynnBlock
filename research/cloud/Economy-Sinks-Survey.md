# Economy sinks survey (P7 follow-up, cloud draft 2026-10-23)

Refresh of the old task "P7 economy sink survey". Balance P1-P9 shipped since (P7 core 10-22, P7b 10-22), so the old audit
(`research/Economy-Audit-1014.md`) is out of date. This file says what sinks exist NOW, how far the coin targets are met, and what is
still missing. Paper only; no game files read. Sources: `research/Balance-P7-Economy-Spec.md` (Part 6), `research/balance/targets.md`
(section 3 + P7 check rows), `docs/log/2026-10.md` (10-22 P7 / P7b lines), `research/cloud/Tab-Economy.md`,
`research/cloud/Bank-Tab-Calibration.md`.

## Decisions followed

- `docs/answered/economy.md` line 142 (2026-10-16): sink "Yes, after rebirth R3". Rebirth R3 is live, so a new sink is now allowed.
- `docs/answered/economy.md` line 162 (2026-10-18): Q18 coin targets (x10 on 10-21: 100k / 5M / 100M, never spending); Q19 sinks "Even mix"
  (upgrades, Bazaar, cosmetics about equal); Q20 buy across ~1.5x time.
- `docs/answered/economy.md` lines 49-50: AH fees LOCKED (listing 1 / 2 / 2.5 %, durations 20 / 45 / 100 / 350, 1 % tax above 1M, 48 h = double).
- `docs/answered/economy.md` line 88: bank interest LOCKED (once per real day, brackets 2 / 1 / 0.5 %, about 85k a day max).
- `docs/answered/economy.md` line 127: death coin loss kept ("coins yes, loot no"). P7 Part 7 proposes 5 %; live per the log = 5 % carried.
- `docs/answered/economy.md` line 148: players cannot respec the rebirth tree themselves.
- Bazaar prices x4.5 / tier pricing / 2-coin floor (`docs/answered/economy.md` lines 133-134 and the 10-16 and 10-22 log lines): do not touch.

## 1. Sinks live now (coins destroyed)

| # | Sink | Where | Size now | Scales with level? |
|---|---|---|---|---|
| S1 | Bazaar spread (buy +10 %, sell -10 %) plus 1.25 % order tax | SkyyBazaar 0.2.1 | about 22 % round trip + 1.25 % | yes (prices follow tier) |
| S2 | AH listing + duration fees, claim tax over 1M | SkyyAuctions 0.1.15 | LOCKED, percent of trade | yes (percent) |
| S3 | Roaming Merchant weapons | SkyyMerchants 0.1.7 | 1.875 h of zone income each (15.5k at Lv 10, 565k Lv 50, 7.1M Lv 90) | yes |
| S4 | Gear reforge / level-up / identify | SkyyGear 0.3.37 `cost.*` on `coins:fn:curve` | 0.025 / 0.01 / 0.005 h x rarity factor | yes |
| S5 | Lifelong tool points reset | SkyyGear | 5,000 x points x (resets + 1) | no, flat |
| S6 | Tree respec | SkyyTrees 0.4.9 | 2,100 x curve x n (first per run free) | yes |
| S7 | Shard upgrades | SkyyShards 0.4.5 | 1 h of zone income each | yes |
| S8 | Vault pages 3-10 | SkyyVault | 50k + 25k a page, 1.1M total (LOCKED) | no, flat |
| S9 | Death loss | SkyyCoins 0.1.10 | 5 % of purse, none on island / shard worlds | yes (of purse) |
| S10 | Rebirth purse + bank to 0 | SkyyRebirth | everything, once per run | yes |
| - | Class switch 5,000 | dormant | not charged | - |

Sources (faucets) now: gathering sales on the Bazaar (about 80 % of a zone's coins), level-up coins on the curve (7-10 %), collection
tier coins (about 9 %), luggage / airdrop / bag coins x zone band (10-11 % for explorers), mob and Structure Money coins, idle shard
production (20-100 % of an active hour, 3 days), bank interest (about 85k a day max). Nothing pays coins that has no matching zone scale.

## 2. Gap to the targets

Targets from `docs/answered/economy.md` line 162 and `research/balance/targets.md` section 3 (coins earned, never spending):

| Zone end | Target | Today (model) | Verdict |
|---|---|---|---|
| 1 | 100k | 91k (x1.03 in the P7 check) | ok |
| 2 | 707k | 608k (x1.04) | ok |
| 3 | 5.0M | 1.8M in section 3 (x1.01 in the P7 check) | ok per check; the section 3 row is older - UNVERIFIED which is current |
| 4 | 22.4M | x1.01 | ok |
| 5 | 100M | x0.99 | ok |

Faucet side is on target. Sink side: Part 6.3 of the P7 spec sizes "upgrade everything" at 21-35 % of each zone's coins (about one
third) and Bazaar buy-across at about one third. The **cosmetic third does not exist** (no Wardrobe prices, the Tab is a paper design).
So the "Even mix" (Q19) is met for 2 of 3. Other soft spots:

- Flat sinks (S5 resets, S8 Vault) vanish late; the curve-based ones (S3, S4, S6, S7) keep pace.
- Death loss is about 2.5 % of income: a nudge to bank, not a sink.
- A player who owns everything has nothing to burn coins on after Zone 3: the 100M target has no matching drain except rebirth.
- Bank (85k a day) is small; the real inflation risk is a rebirthed player with purse 0 but a finished kit.

## 3. Candidate sinks not yet shipped (5)

| # | Candidate | What it does | Size (default) | Fit to Q19 |
|---|---|---|---|---|
| C1 | **The Tab** (endgame) | Optional bill that grows while online; pay any amount; titles / cosmetics at milestones; Receipt ending. `research/cloud/Tab-Economy.md` + `research/cloud/Bank-Tab-Calibration.md` (90,000 per hour = 25 % of old endgame income) | MUST be re-based on the x10 targets (old numbers are 10x too small) | cosmetics third, Zone 4-5 |
| C2 | **Wardrobe / cosmetic prices** | Coin price on dyes, outfit slots, extra loadout pages, pet skins, titles | 0.5-3 h of zone income per item | cosmetics third, all zones |
| C3 | **Bazaar sell tax per zone** | Raise the 1.25 % order tax on big orders only (for example 2 % above 1M per order), like the AH 1 % tax above 1M | small; stops big flips | Bazaar third; low risk |
| C4 | **Respec and reset curve** | Make S5 (lifelong reset) and S8-style flat costs follow the coin curve; add a paid class-skill respec | tracks 0.25 h x n | upgrades third; fixes "flat vanishes late" |
| C5 | **Upgrade ladders** (Accessory slot unlock, Pet feeding / re-roll, Sack size tiers for coins) | Coin-gated unlocks that were free (Accessories, Pets, Sacks have no coin cost today) | 1 h of zone income per step | upgrades third; but touches the four-power-sources rule |

## 4. Default pick

**C2 first, then C1.** C2 (cosmetic prices) is the cheapest way to fill the missing third: no power effect, no balance risk, Wardrobe
already exists, and the cost rule "hours of income at your level" is already built (`coins:fn:curve`). C1 (the Tab) stays the Zone 4-5
endgame sink and is already designed and approved in spirit (Skyy 2026-10-01 lore); it needs its numbers re-based on the x10 targets
and a measured income, so it waits for real play data. C3 and C4 are small follow-ups that can ride along in any round that touches
SkyyBazaar or SkyyGear. C5 is last: it puts coin gates on power sources, which Skyy has called essential, so ask first.

## Questions for Skyy

1. Build the cosmetic sink now as coin prices in Wardrobe (C2) plus the Tab later? [yes, C2 now as a lean round after the UI rounds; Tab after a measured Zone 4 session]
2. Should the Tab (C1) use the x10 re-based numbers (about 900,000 coins an hour at endgame instead of 90,000)? [yes, re-base to 25 % of Zone 5 income, 3.9M an hour, so about 1M an hour]
3. Add a 2 % Bazaar tax on single orders above 1M (C3)? [yes, mirrors the AH]
4. Make the flat sinks (lifelong reset, Vault) follow the curve (C4)? Vault is LOCKED at 50k + 25k, so [leave Vault; curve the lifelong reset only]
5. Allow coin gates on accessory slots / pet re-rolls (C5)? [no, not now]

## For the local session (UNVERIFIED, need game files / measured play)

- Is Bazaar order tax still 1.25 % in SkyyBazaar 0.2.1 (the P7 spec says so; read the build script or run `python tools/balance_model.py --econ`)?
- Is the death loss live at 5 / 5 with the safe-worlds rule (log says "death 5 % carried", the Server Setup rows were PROPOSED)?
- The two zone-3 rows in `research/balance/targets.md` section 3 (1.8M) and the P7 check (x1.01) disagree; run `python tools/balance_model.py --econ --check` to see which is current.
- No measured income exists yet; C1 and C2 sizes need one real Zone 3-4 session (coins gained per hour from the HUD).
- Wardrobe has no coin rows today (P7 Part 6.1 grep): confirm in SkyyWardrobe before adding any.
