# Economy audit - live set, 2026-10-14

Refresh of `research/cloud/Economy-Audit.md` (paper audit of 2026-10-06) against what is in `tools/deploy_set.py` SET today. Read-only: build scripts of the
pinned versions (Skills 0.4.35, Bank 0.1.10, Bazaar 0.1.10, Auctions 0.1.4, Merchants 0.1.3, Collections 0.2.12, Quests 0.2, Exploration 0.2.7, Coins 0.1.6,
Gear 0.3.2, Rebirth 0.1), `docs/answered/economy.md`, `research/cloud/Rebirth-Spec.md`. Every per-hour size is still an estimate from paper; there is no measured
income yet (see section 7).

## 0. The short version

1. **The old top finding is fixed.** Bank interest is no longer 2% per real hour. Live (Bank 0.1.7+): once per real day, account-wide brackets 2% / 1% / 0.5%,
   cap 10M, max about 85,000 a day for a full account (4 alts at 10M together, not 340,000). The old "4.8M per profile per day" is gone.
2. **The new biggest faucet is level-up coins times profiles times rebirths.** One profile pays `coinsPerLevel (100) x level` for each level, so one skill to
   level 100 = 505,000 coins; 9 skills = about **4.5M per profile**. Profiles are per class and a player has up to 6; coins can move between profiles
   (`/pay`, AH). Rebirth then pays them again. At a flat 100% it is 117M per profile over 10 rebirths; with a shrink of 0.8 per rebirth it is 36M (table in 3).
3. **Rebirth opens two small holes** (spec Q15): coins moved into Bazaar goods before a rebirth survive the "purse to 0" reset, and the bank bonus counts
   purse + bank after the refunds. Fix: count goods too, or lock Bazaar buys in the last N minutes (section 5, E2).
4. **Bazaar, AH, merchants are clean.** The Bazaar has a build-time loop check at every processed premium 0-22 and an admin price guard; Enchanted goods are priced from
   their recipe inside the same cap. Nothing in this pass found a buy-craft-sell loop.
5. **Sinks are thin.** Live coin sinks are the AH fees, Bazaar spread, merchant weapons (2,000-7,500 and up), reforge / level-up / identify at Gear, Vault pages (1.1M total),
   death loss 10-25% of the purse. Several planned big sinks (the Tab, slayers, accessory slots) are not built, so inflation has nothing to push against yet.

## 1. Faucets (coins created) - live

| # | Faucet | Where | Live number | Size | Verdict |
|---|---|---|---|---|---|
| F1 | Starter grant per new profile | SkyyCoins `starterK` (once per profile key, no balance file yet) | 10,000 | 60,000 per player at 6 profiles | profile delete + remake may grant again (UNVERIFIED, old C5) |
| F2 | **Bank interest** | SkyyBank 0.1.10 | daily, 2% to 1M, 1% to 5M, 0.5% to 10M, back-pay 1 day (`catchUpPeriods` 24 cap, whole days) | 20,000 a day at 1M, 85,000 at 10M, per ACCOUNT | OK now. Rebirth adds a permanent bonus on top (F8) |
| F3 | **Skill + class level coins** | SkyySkills `coinsPerLevel=100`, paid once per level through the paid marker (`<Skill>.paid`) | 100 x new level | 505,000 per skill to Lv 100; ~4.5M per profile (9 skills); x6 profiles | **HIGH, see 3** |
| F4 | Collection tier coins | SkyyCollections `tier.coins=50,100,200,400,800,1500,3000,6000,12000,25000` | 49,050 per collection, combat x2 on III / V / VII / last | 100+ collections = 5M or more per profile | MEDIUM: per profile, one-time |
| F5 | Bazaar instant sell (market maker) | SkyyBazaar 0.1.10, spread 10%, impact 10,000, half-life 120 min, factor 0.25-4 | sell = base x factor x 0.90 | the only large active source | OK if the factor works (UNVERIFIED) |
| F6 | Exploration luggage + Scavenger | SkyyExploration 0.2.7: coins 10-30 / 25-60 / 60-150 / 150-400 by tier, zone mult 1 / 1.5 / 2 / 3, `capPerHour` 8; Scavenger 10 x Exploration level | about 40 coins avg x zone mult x 8 per hour | under 1,000 per hour | OK, small and capped |
| F7 | Quest coins | SkyyQuests 0.2 tutorial table (25 per task as in the feed text) + quest files; combat quests pay class gear, not coins | tens to hundreds | one-time | OK |
| F8 | Rebirth bank bonus | Rebirth-Spec 3.3 (not built): `min(1, 0.25 x log10(1 + balance / 100,000))` percentage points added to bracket rates | up to +1 point | at 10M bank, +1 point on the first bracket = +10,000 a day | OK, small. Cap it inside the brackets (spec already does) |
| F9 | Death refund / admin | - | none | - | - |
| - | **No coins:** mobs, SkyyMobs levels, Merchants (they only take coins), Pets, Accessories, Wardrobe, Gear drops | | | | good: kills never print money |

## 2. Sinks (coins destroyed) - live

| # | Sink | Where | Number | Note |
|---|---|---|---|---|
| S1 | Bazaar spread (buy +10%, sell -10%) | Bazaar | 22.2% round trip | a buy-then-sell always loses |
| S2 | AH listing fee 1% (2% over 10M, 2.5% over 100M) + duration fee 1h 20 / 6h 45 / 12h 100 / 24h 350 / 48h x2 listing fee + 1% claim tax over 1M | Auctions 0.1.4 | cancel keeps the fee | main player-to-player sink |
| S3 | Roaming Merchants weapons | Merchants 0.1.3 | Z1 2,000-3,000, Z2 6,000-7,500, higher zones more; fallback = median table price or 150 x level (min 100) | pure sink: items are one-of-each stock, resale only through the AH |
| S4 | Gear: identify, reforge, level up | Gear 0.3.2 `cost.identify / cost.reforge / cost.levelUp` | tables by rarity + per item level | main repeatable sink for fighters |
| S5 | Vault pages 3-10 | Vault | page 3 50,000, +25,000 each, 1.1M total, shared across profiles | one-time |
| S6 | Death loss | Coins | 10-25% of the PURSE | banking avoids it |
| S7 | Tree respec | Trees `tree.respecCoins` | small | |
| S8 | Rebirth purse + bank to 0 | Rebirth R3 (not built) | the biggest single sink, once per run | see E2, goods and alts dodge it |
| - | Not sinks: guild bank, /pay, /trade, AH sales (move coins), warps | | | |
| - | Planned, not built: Tab, slayers, Accessory slots for coins (R3 says none), NPC shops, pocket shards | | | no sink = inflation |

## 3. The level-coin rule with rebirth (Skyy 2026-10-14: "Yes but a little less each rebirth")

Levels reset each rebirth, cap = 100 + 10 x rebirths. Coins of a run = `100 x (1 + 2 + ... + cap) x m(n)` = `50 x cap x (cap + 1) x m(n)` per skill,
9 skills per profile (8 gathering / movement skills + the class skill; Fishing not counted - UNVERIFIED whether it pays level coins).

| Run (n) | cap | 100% flat | m = 0.9^n | m = 0.8^n | m = 0.7^n |
|---|---|---|---|---|---|
| 0 | 100 | 4.54M | 4.54M | 4.54M | 4.54M |
| 1 | 110 | 5.49M | 4.95M | 4.40M | 3.85M |
| 3 | 130 | 7.66M | 5.59M | 3.92M | 2.63M |
| 5 | 150 | 10.19M | 6.02M | 3.34M | 1.71M |
| 10 | 200 | 18.09M | 6.31M | 1.94M | 0.51M |
| **10 runs total** | | **117M** | **64M** | **36M** | **22M** |

Reading: 0.9 per rebirth is NOT "a little less" in practice (it still grows, because the cap grows faster than the multiplier shrinks). 0.8 shrinks every run
after the first and pays 36M in 10 runs per profile. The coins are paid at the level-up, so most of them come late in the run (level 100 pays 10,000, level 1 pays 100).
Compare the daily bank cap of 85,000: a 4.5M level payout equals 53 days of maximum interest, so level coins are the main early-to-mid money.

## 4. Net reading (all numbers estimates)

| Phase | Active income (play) | Passive | Main sinks | Reading |
|---|---|---|---|---|
| First profile, early | Bazaar sells + level coins (100 per level early) | 10,000 start, little interest | Gear costs, AH fees | tight, healthy |
| Mid | level coins grow (level 40 pays 4,000) + collections | interest 1-2% of a few hundred thousand | merchants 6,000+, reforge | probably positive; measure |
| Endgame, first run | up to 4.5M from levels + 5M collections + Bazaar | 85,000 a day max | little | the only large sink is rebirth |
| After rebirth | purse 0, bank 0, collections kept (no coin repay), levels pay again at m(n) | bonus rate | | restart is the real sink - keep it |
| 6 profiles | each profile earns its own level + collection coins | account-wide bank brackets | | **funnel: alt coins reach the main through /pay and AH** |

## 5. Loops and runaway sources

| # | Severity | Finding | Proposal |
|---|---|---|---|
| E1 | **HIGH** | **Alt-profile funnel.** F3 + F4 + F1 pay per profile, and a player has up to 6; `/pay`, `/trade` and cross-profile AH buys (`otherProfileBuy`) move coins freely. 6 x 4.5M level coins = 27M from play in the first run | Decide the rule (Q1): default = coin payouts that are tied to a profile stay, but `/pay` and `/trade` of coins between profiles of the SAME account are blocked, `otherProfileBuy` stays true only for items (AH price cap for same-account buys). Cheap: one account-id check in Coins `transfer` |
| E2 | **HIGH (rebirth, not built yet)** | Rebirth purse + bank to 0 (Q8) but goods are kept: buy Bazaar goods or AH items with the whole purse, rebirth, sell them back. Q15 allowed it on purpose (Skyy: "Allow it"), so this is a design choice; the bank bonus counts purse + bank only | Keep Q15 (it is Skyy's word) but (a) take the goods' value at base x 0.9 into the bonus balance, (b) log it in the journal, (c) goods sold after a rebirth pay at the Bazaar factor like any sale. Nothing else needed. Tell Skyy it is a deliberate carry-over |
| E3 | MEDIUM | **Level-coin curve shape** (table 3): a flat 100% repay grows to 18M per run; 0.9 grows too | m(n) = 0.8^n [default], paid per level at the level-up through the existing paid marker, marker reset at rebirth. Server Setup row `rebirth.coinShrink` |
| E4 | MEDIUM | **Collection tier coins after rebirth**: collections are kept ("you retain the knowledge"), the paid marker `_paid.<Id>` stays, so no re-pay - good. But "+1 collection rank per rebirth" adds tiers whose coins pay once | Fine. Keep: no coin repay for collections |
| E5 | MEDIUM | **Bank bracket 2/3 are cheap to fill** because level coins alone can reach 1M early; 85,000 a day is small now but nothing else drains the bank | Leave the daily rate; add the Tab or slayer sink later (Q3). Do not raise the cap |
| E6 | LOW | Starter 10,000 per profile key; delete + remake may re-grant (old C5, UNVERIFIED) | Add a "granted" flag kept after delete (the Coins guard `GRANTED` is per key); test: create, delete, create again, read the purse |
| E7 | LOW | Rebirth interest bonus uses balance at reset; two profiles at 5M each give two bonuses on one account | Account-wide: bonus computed on the account sum of the profile being reborn only, stored per profile, capped at +1 point |
| E8 | LOW | Merchant prices are flat per zone, never scaled by rebirth or level; at rebirth 5 a 7,500 weapon is nothing | Add a per-rebirth price multiplier row (x1.0 + 0.25 x rebirths) once rebirth is live; default off |
| E9 | LOW | Luggage coins are tiny but uncapped per day besides `capPerHour 8` | Keep |
| E10 | INFO | Bazaar Enchanted goods: recipe-priced inside the processed-goods premium (20%, max 22%), loop check at every premium 0-22, admin price guard refuses a change that opens a loop | Nothing to do; rerun `check_assets` after any new Enchanted tier |
| E11 | INFO | Old C1 / C2 (Tab, hourly bank) gone or unbuilt; old C12 (collection coin bypass) done (off since 0.2.5, never skips collections) | Close |

## 6. Numbers I propose (all Server Setup rows, defaults)

| Row | Today | Proposed | Why |
|---|---|---|---|
| `skills.coinsPerLevel` | 100 | 100 (keep) | the 505,000 per skill is a lot; shrink through m(n) instead of the base |
| `rebirth.coinShrink` (new) | - | 0.8 per rebirth (m = 0.8^n) | table 3: 36M over 10 runs, falls every run after the first |
| `coins.starterGrant` (new row, today hard-coded 10,000) | 10,000 | 10,000, once per account slot | E6 |
| `coins.transferSameAccount` (new) | allowed | blocked | E1 |
| `bank.*` | 2 / 1 / 0.5 %, cap 10M | keep | already good |
| `merchant.rebirthPriceStep` (new) | - | 0.25 per rebirth, off until rebirth is on | E8 |
| `rebirth.bankBonusCap` | spec +1 point | keep +1 point, count goods in the balance | E2 |

## 7. Measure first (needs a play session or a read-only copy of the save data)

| # | Measure | How |
|---|---|---|
| 1 | Coins per online hour by source, early / mid / late | timed session; `coins:fn:get` before / after; Bazaar `trades.log`; `chat_digest.py` |
| 2 | Real lifetime coins from level-ups and collections per profile | sum the `paid` markers in the Skills / Collections player files of a copy |
| 3 | Bank totals and accounts at the cap | copy `Skyy_SkyyBank` into scratch |
| 4 | Do Fishing and Overall pay level coins | read Skills `payLocked` list vs the 9 skills |
| 5 | Does delete + remake grant 10,000 again | test profile |
| 6 | Bazaar factors after a week (`market.properties`) | copy |

## UNVERIFIED

| # | Item |
|---|---|
| 1 | 9 coin-paying skills per profile (8 skills + class skill). |
| 2 | Level coins pay up to the cap (100 now) - the Skills header says "keep paying up to 100". |
| 3 | The Bazaar demand factor behaves as the 0.1.x comments say. |
| 4 | The rebirth numbers come from the unbuilt spec (R3+). |
| 5 | Combat quests pay no coins (header of Quests 0.2) - the quest files themselves were not summed. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Block `/pay` and coin `/trade` between profiles of the same account so alt profiles cannot funnel level coins? | [block same-account coin transfers; items still fine] |
| 2 | Level-up coins after a rebirth: shrink by 0.8 per rebirth (36M over 10 runs per profile)? | [0.8 per rebirth] |
| 3 | Add a real coin sink before more faucets (the Tab or slayer costs from the old plan)? | [yes, after rebirth R3; numbers from a measured session] |
| 4 | Count goods bought with coins before a rebirth in the bank bonus balance (they are kept either way)? | [yes, at 90% of base value] |
| 5 | Scale merchant prices up by 25% per rebirth once rebirth is on? | [yes, off until rebirth is on] |
