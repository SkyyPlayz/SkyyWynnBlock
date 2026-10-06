# Economy audit - coin faucets and sinks

Cloud draft, 2026-10-06. Paper design; nothing built. A check of every place the design makes or destroys coins, with rough sizes per online hour.
Inputs read (grep + ranges): every `research/cloud/*.md` spec (Tab-Economy, Prestige, Zone-Specials, Enchanted-Materials, NPC-Shops, Slayers, Elites-Events,
SkyyQuests, Capstone, Accessory-Acquisition, Pocket-Shards, Loot-Box, Collection-Unlocks, Outposts, Class-Tree-Paths, Starter-Shards ...), `research/Server-Setup-Research.md`,
`docs/plans/SkyyEconomy-Plan.md`, `docs/plans/SkyyAccessories-Plan.md`, `docs/answered/economy.md` + `mobs.md` (R5) + `social.md`, `docs/log/2026-10.md`, and the pricing
notes in `SkyyBazaar/build_skyybazaar_0.1.4.py` and `SkyyBank/build_skyybank_0.1.6.py` (read only). Every number below is a placeholder or an estimate, not a measurement.

## 0. The short version

1. **The biggest faucet is the Bank, not play.** 2% per real hour on up to 10M, paid to **offline** profiles too, is up to **4.8M coins per profile per real day**
   with nobody online. A fresh profile's 10,000 starter coins compound to the 10M cap in **about 349 hours (14.5 days)** without being touched. 4 profiles per player = 19.2M a day.
2. **Active income is small and self-limiting.** The Bazaar is a market maker (it creates coins when you sell), but its demand factor drops the price fast for
   expensive items. Estimated active income: **~8k/h early, ~90k/h mid, ~360k/h endgame**.
3. **The Tab (20M per in-game day = ~25M per online hour at a 48-minute day) is ~70x endgame active income.** Unpayable unless funded by bank interest.
4. **Loops:** Enchanted Blocks (10% + 10% = 21%) sit at 0.99 of the 22.2% loop line; one more premium step on top of a smelted good (20% + 10%) is a loop (1.08).
5. **R3 is clean in the specs**, with three small leftovers (coin slot purchases in the Accessories plan, the dormant collection coin bypass, event-vendor Pet Treats).

## 1. Assumptions (all rows to measure - section 8)

| Phase | Who | Zone / level | Online play | Gathered items per hour | Bazaar base of what they sell | Bank balance |
|---|---|---|---|---|---|---|
| **Early** | first ~10 h | Z1-Z2, Lv 1-25 | 3 h per real day | 600 | Oak 3, Copper 5, T2 log 8, Iron 16 | 5,000 |
| **Mid** | ~20-60 h | Z3, Lv 30-45 | 3 h per day | 800 | T3 log 20, Thorium 48, Cobalt 144, Adamantite 480 | 500,000 |
| **Endgame** | 100+ h | Z5, Lv 60-75 | 3 h per day | 800 | T5 log 128, Adamantite 480, Mithril 1,440, Onyxium 3,712 | 10,000,000 (cap) |

800 items per hour comes from Enchanted-Materials-Draft ("160 base about 10 minutes"). Items are split evenly over 4 products; the player is the **only seller**
of those products (best case). Bazaar maths from the 0.1.4 script: sell = base x factor x 0.90; each unit sold divides the factor by `exp(ln 1.10 x base / impactCoins)`
(impactCoins 10,000); factor clamped 0.25-4.0, decays back to 1.0 with a 120-minute half-life. Simulated over a 2-hour session in python.
"Per online hour" for things that pay per **real** day (bank, daily caps) = the daily amount / 3 play hours.

## 2. Faucets (coins created)

| # | Faucet | Source | Early /h | Mid /h | End /h | Notes |
|---|---|---|---|---|---|---|
| F1 | **Starter grant** 10,000 per new profile | SkyyCoins (hard-coded `10000L`) | one-time | - | - | paid again for each new profile (section 5, C5) |
| F2 | **Bank interest** 2% per real hour on min(bank, 10M), offline too, 24-period catch-up, back-pay when the bank was off (LOCKED) | SkyyBank 0.1.6 | 800 | 80,000 | **1,600,000** | 200k per real hour at the cap = 4.8M per day; 3 more capped profiles add 4.8M per online hour |
| F3 | **Bazaar instant sell** (market maker) | SkyyBazaar 0.1.4 | 4,300 | 77,000 | 336,000 | without the factor drop it would be 4.3k / 125k / 1.04M; drop matters from mid game on |
| F4 | Collection tier coins 50 ... 25,000 (49,050 per collection, combat x2 on 4 tiers) | SkyyCollections | 1,000 | 2,300 | 3,700 | one-time per tier; 105+ collections = ~5-8M lifetime |
| F5 | Skill + class level-up coins (100 per level; class rate flagged in OPEN-QUESTIONS 2026-10-02) | SkyySkills | 1,600 | 400 | 100 | one-time per level |
| F6 | Quest coins (`reward.coins`, e.g. 100) | SkyyQuests-Spec | 300 | 500 | 1,000 | totals unknown until the quest files exist |
| F7 | Exploration chests + Scavenger 10 per level | SkyyExploration | 300 | 200 | 100 | small |
| F8 | NPC sell-back 25% of base, cap 20k / 30k / 45k / 67.5k / 101k per day (Z1-Z5) | NPC-Shops-Spec | 500 | 2,000 | 5,000 | junk only; the Bazaar pays 3-4x more |
| F9 | Pocket Shard auto-sell, 50% of NPC value, cap 50,000 per day | Pocket-Shards-Spec | 0 | 8,300 | 16,700 | runs while offline; cap differs from NPC-Shops (C9) |
| - | **No coins:** mobs (R5), elites, slayer bosses, events (tokens), capstone (Audit Tokens), dragon, zone specials, prestige | specs | 0 | 0 | 0 | good: kills never print money |
| | **Total faucets** | | **8,800** | **171,000** | **1,963,000** | active only (no F2): 8k / 91k / 363k |

## 3. Sinks (coins destroyed)

| # | Sink | Source | Early /h | Mid /h | End /h | Notes |
|---|---|---|---|---|---|---|
| S1 | **The Tab** 20M per in-game day (`tab.perHour`) | Tab-Economy | - | - | 25,000,000 (48-min day) | only after the Zone 5 reveal; see C1 |
| S2 | Bazaar instant buy (base x factor x 1.10) | SkyyBazaar | 1,000 | 20,000 | 100,000 | the 22.2% spread is the part a buy-then-sell loses |
| S3 | NPC shop buys (3.7x base; flat basics) | NPC-Shops-Spec | 500 | 1,000 | 2,000 | 640 per item per day |
| S4 | AH listing 1-2.5% + duration fee 20-350 (48h = 2x, never cheaper than 24h) + 1% claim tax over 1M | SkyyAuctions | 0 | 3,000 | 30,000 | cancel keeps the fee |
| S5 | **Slayer spawns** 400 ... 3,000,000 per tier and zone | Slayers-Spec 3.1 | 1,900 (2/h) | 68,000 (2/h) | 525,000 (0.5/h) | at 2/h Zone 5 would be 2.1M/h, see C3 |
| S6 | Identify 210-490, reforge 100-5,000 | Loot-Box, SkyyRolls | 1,000 | 5,000 | 20,000 | |
| S7 | Death coin loss 10-25% of the purse | SkyyCoins | 1,750 | 10,000 | 35,000 | purse only; banking avoids it |
| S8 | Vault pages 3-10 (50k + 25k steps = 1.1M total) | SkyyVault | one-time | one-time | - | |
| S9 | Accessory slots for coins (25k ... 3.2M, 6.4M total; plan, rebased to +10 slots) | SkyyAccessories-Plan | - | one-time | one-time | not built; R3 question C6 |
| S10 | Class tree respec (`tree.respecCoins`), class switch (inert) | Class-Tree-Paths | small | small | small | |
| S11 | **Prestige** - purse and bank reset to 10,000 | Prestige-Spec | - | - | one-time | only after Paid in Full; see C7 |
| - | **Not sinks:** guild bank (moves coins; a leaver gets 35% back, the rest stays in the guild), /pay, /trade, AH sales between players, warps (free with a cooldown, Outposts-List Q2), repair (no coin repair anywhere in the design) | | | | | |
| | **Total sinks** (without the Tab) | | **6,150** | **107,000** | **712,000** | |

## 4. Net inflation per phase (without the Tab)

| Phase | Faucets /h | Sinks /h | **Net /h** | Of which bank | Net without the bank | Reading |
|---|---|---|---|---|---|---|
| Early | 8,800 | 6,150 | **+2,600** | 800 | +1,800 | fine: tight, the starter 10k matters |
| Mid | 171,000 | 107,000 | **+64,000** | 80,000 | **-16,000** | play alone is slightly negative; the bank makes it positive |
| Endgame | 1,963,000 | 712,000 | **+1,251,000** | 1,600,000 | **-349,000** | all endgame profit is passive interest |
| Endgame, 4 capped profiles | +4.8M more | | **~+6,000,000** | 6.4M | | money from not playing |

Before the Tab opens, an endgame player gains ~1.25M per online hour, ~6M with alt profiles; nearly all of it from the bank. With the headline Tab (25M/h) the net
is **-24M per online hour**: the Tab can never be paid by play. Rough calibrated Tab (`tab.perHour` = 40-50% of measured endgame income, Tab-Economy section 2) with
these estimates: **150,000-200,000 per online hour** if the bank is fixed (C2), not 25M.

## 5. Conflicts and loops

| # | Severity | Finding | Proposed fix (all Server Setup rows) |
|---|---|---|---|
| C1 | **HIGH** | **Tab 20M per in-game day vs ~0.36M per hour of active endgame income** (~70x). Only payable with offline bank interest from several profiles, which turns the "race you can win with endgame income" into "wait and own alts" | Keep `tab.perHour` as the truth (Tab-Economy Q1) and set it from the measurement (section 8); placeholder 200,000 per online hour (= 160k per 48-min day). The quest text still says "20 million" as a joke if Skyy wants the lore number |
| C2 | **HIGH** | **Bank interest 2% per real hour, offline, every profile** = 4.8M per profile per day, 19.2M for 4 profiles, compounding 1.61x per day below the cap. Hypixel SkyBlock pays its bank interest once every 3 SkyBlock months (about 31 real hours) - ours pays ~31x as often. Also a funnel: alt profiles' coins move to the main profile through the AH (a different profile may buy your listing, LOCKED) | `intervalMinutes` 60 -> **1,440** (2% per real day) **or** pay only for online hours (like the Tab), and lower `maxPrincipal` early (e.g. 1M, raised by progress). Back-pay stays (LOCKED) but counts days, not hours. Skyy decides (Q1) |
| C3 | MEDIUM | **Zone 4-5 slayer costs** (Z5 T IV 1.5M, T V 3M) are 4-8 hours of active endgame income per spawn; only the bank can fund them | Scale `slayer.tierCosts` to ~0.5-2 hours of measured income per spawn of the zone's normal tier (Z5 x0.25 as a placeholder: 15k / 56k / 150k / 375k / 750k) |
| C4 | MEDIUM | **Enchanted Block = 1.21x** (10% per step, compounded). Buy 25,600 base at 1.10, craft, sell the Block at 0.9 x 1.21 = 1.089: margin **0.99** of the loop line. Factor drift between products (the 0.1.4 log notes ~2%) opens it. And any Enchanted form made from a **processed** good (ingot +20%, then +10%) is a real loop: 0.9 x 1.32 / 1.10 = **1.08** | Rule: the **cumulative** premium along any chain from a Bazaar-buyable input stays **<= 15%** (`bazaar.maxChainPremium`). Enchanted 10%, Block +5% (1.155x). Enchanted forms only from raw items, never from smelted / tanned goods. Re-run the LP loop check over 2,252 + new recipes |
| C5 | MEDIUM | **Starter grant per new profile**: create a profile, sell 10,000 coins of nothing on the AH to the main profile, delete, repeat (the 6-hour undo does not stop new creates) | Pay the starter grant once per **account slot** (a "slot already granted" flag kept after delete), or make the grant bound to the profile (not tradable for its first N hours) |
| C6 | MEDIUM (R3) | Accessory slots for coins (SkyyAccessories-Plan, +16 or rebased +10, 6.4M total). R3 says coins never skip collections **or bags**; buying bag capacity is close to buying a bag | Ask Skyy (Q3). Default: slots come from collections, skills and quests only; coins buy nothing in the Accessory Bag |
| C7 | LOW | **Prestige coin reset is dodgeable**: coins parked in a guild bank, an alt profile, or as items (vault is shared across profiles) survive the reset | Acceptable: prestige needs Paid in Full, which is the real sink. Optional: the requirements checklist also asks "guild bank contribution since Paid in Full <= 0" - not worth it, recommend leaving it |
| C8 | LOW | **Zone specials** allow "slayer boss cost -15/-20%" (Zone-Specials-Spec 2, rows 60/62/79): a coin effect (a sink cut) despite the "no coin effects" rule | Replace with "slayer XP +15%" or "+1 slayer token"; or keep and write it down as the one allowed coin effect |
| C9 | LOW | NPC-Shops says auto-sell shares the NPC daily cap (20k Z1); Pocket-Shards says its own 50,000 cap. Two faucets or one? | One shared cap per profile: `shops.dailySellCap` by zone; auto-sell pays 50% and counts toward it |
| C10 | LOW (R3) | Event tokens buy a **Pet Treat bundle**; a Pet Treat is a cooked item - if it is ever a Bazaar product, tokens become coins | Event-vendor items are bound to the profile (no AH / Bazaar / trade / NPC sell-back) |
| C11 | LOW | NPC-Shops-Spec says "NPC sell-back creates coins from nothing, the Bazaar / AH only move them" - **wrong for the Bazaar**: instant sell is the market maker paying new coins (F3). Same file lists 0.1.2 prices (Iron 8) | Correct the wording when NPC shops are built; re-run the 3.7x / 25% check over the 0.1.4 prices (still holds: it is ratio-based) |
| C12 | LOW (R3) | SkyyCollections' coin tier bypass still exists (off since 0.2.5; Server-Setup-Research still says `bypass.enabled` true). R3 (2026-10-02) says **remove** it | Remove the code and the row in the next Collections build; fix the research table |
| C13 | INFO | Bazaar buy = 1.10, sell = 0.90 and the NPC prices (buy 3.7x > Bazaar's top sell 3.6x; sell-back 0.25x < Bazaar floor buy 0.275x) - **no loop**. Smelted +20% = 0.98 (live, tightest) - OK alone | Keep; never stack another premium on it (C4) |

## 6. R3 check (coins never skip collection unlocks; shops never sell unlocks / accessories)

| Place | Result |
|---|---|
| NPC shops (NPC-Shops-Spec 4), outpost shops | OK - never a recipe, tier, bag or accessory; an admin check lists violations on save |
| Collections / Enchanted forms | OK - Enchanted items count only when obtained, never bought or crafted |
| Slayer tokens, Audit Tokens, event tokens | OK - bound or cosmetic-only; never recipes (C10 for treats) |
| Accessories | OK - NPC shops and tokens never give them; Legendary / Mythic bound on pickup. AH trade of lower ones = Accessory-Acquisition Q4 (allowed by R3: coins may buy items) |
| AH / trade | OK - Magic Bags and the Accessory Bag blocked (LOCKED) |
| Collection coin bypass, accessory slots | see C12, C6 |

## 7. Server Setup rows this audit touches

`bank.intervalSeconds` (3,600 -> 86,400 proposed), `bank.onlineOnly` (new, off), `bank.maxPrincipal`, `coins.starterGrant` (new; today hard-coded), `coins.starterPerSlot` (new),
`tab.perHour`, `slayer.tierCosts`, `bazaar.maxChainPremium` (15%), `enchanted.premiumStep` (10%) / `enchanted.blockStep` (5%), `shops.dailySellCap`, `shops.autoSellShare`. Times in seconds.

## 8. Measure first (for the local session)

| # | Measure | How |
|---|---|---|
| 1 | Active coins per online hour for an early / mid / endgame test profile, split by source (Bazaar sells, collections, levels, quests) | timed session; `coins:fn:get` before / after; count SELL lines in `Skyy_SkyyBazaar/trades.log` |
| 2 | Real gathering rate (items per hour) per tier with the current tools and double drops | same session; the bag counts before / after |
| 3 | Bank totals today: sum of all `Skyy_SkyyBank` account files and how many are at the 10M cap; interest paid per day | read-only copy of the save data into scratch |
| 4 | How many profiles exist per player, and how many were created and deleted (starter-grant churn, C5) | `Skyy_SkyyProfiles` copy |
| 5 | Demand factors after a normal week (`f.<id>` in `market.properties`): how far do they drift, which products sit at 0.25 | read-only copy |
| 6 | Hytale day length (Tab rate per hour) | world config / `/time` |
| 7 | The LP loop check with Enchanted + Block recipes and the 15% chain rule | the Bazaar build's loop check |
| 8 | Total lifetime coins from collections + level-ups (one-time faucets) | sum of the tier tables over the registry |

## For the local session (UNVERIFIED)

| # | Item |
|---|---|
| 1 | All per-hour sizes above are estimates from paper assumptions (section 1), not measurements. |
| 2 | That the Bazaar factor decay and impact work exactly as the 0.1.4 script comment says (half-life 120 min, impactCoins 10,000). |
| 3 | Whether a new profile after a delete really gets a fresh 10,000 (CoinTask grant per profile key). |
| 4 | Whether Pet Treats or any event-vendor item is a Bazaar product. |
| 5 | Hypixel bank interest cadence: search snippet "every 3 SkyBlock months" ([Coins](https://hypixelskyblock.minecraft.wiki/w/Coins)); ~31 real hours is computed from 20-minute days, not read. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Bank interest: 2% per real **day** instead of per hour, or only for online hours? Today one capped bank makes 4.8M a day while you are offline | [2% per real day, offline still pays, back-pay kept] |
| 2 | Tab: set the rate from a real income test (about 200,000 per online hour on today's numbers) instead of 20M per day? | [measure, then 40-50% of endgame income] |
| 3 | Accessory Bag slots: may coins buy them, or only collections / skills / quests (R3)? | [no coins] |
| 4 | Starter 10,000 coins: once per profile slot, so deleting and remaking a profile does not pay again? | [once per slot] |
| 5 | Zone 5 slayer costs (up to 3M per spawn): lower them to about an hour of income? | [Z5 costs x0.25] |
| 6 | Enchanted Blocks: +5% on top of the Enchanted form (not +10%), so no buy-craft-sell loop can open? | [+5%] |
