# Bank, Tab and starter-grant calibration

Cloud draft, 2026-10-06. Paper design; nothing built. Answers the three money findings in `research/cloud/Economy-Audit.md` (C1 Tab, C2 Bank, C5 starter grant).
Inputs read: `research/cloud/Economy-Audit.md`, `research/cloud/Tab-Economy.md`, `research/cloud/Prestige-Spec.md` (grep), `research/Isles-of-the-Void-Lore.md` (Tab lines),
`docs/answered/economy.md`, `docs/answered/social.md`, `OPEN-QUESTIONS.md` (grep), `research/Server-Setup-Research.md` (SkyyBank rows), `tools/CONFIG-CONTRACT.md` (history /
change log), `SkyyBank/build_skyybank_0.1.6.py` and `SkyyCoins/build_skyycoins_0.1.5.py` (read only). Every number is a placeholder and a Server Setup row (times in seconds).
Arithmetic checked with python (bank compounding, Tab payoff simulation, section 2.3).

## 0. Decisions this file follows (not re-decided)

| Lock | Where | What it means here |
|---|---|---|
| LOCKED 2026-09-25: bank interest for the time the bank was off **is paid** (back-pay) | `docs/answered/economy.md` (In-game server setup 5) | every option keeps back-pay; a daily bank back-pays whole days |
| LOCKED 2026-09-25: a **different profile may buy your listing** on the AH | `docs/answered/economy.md` (AH 4) | the alt-to-main coin funnel stays open; the fixes work on the grant and the bank, not on the AH |
| R3 LOCKED: coins never skip collections or bags | `docs/answered/economy.md` | a bank-tier upgrade (section 1.4) must be unlocked by a collection, coins only pay the fee |
| R9 LOCKED: keep all the small live defaults not otherwise marked | `docs/answered/economy.md` | the live bank default (2% every 60 min) **stays until Skyy answers Q1**; the migration in 1.5 ships only after that answer |
| **DECIDED 2026-10-01: starter coins, class kit and island starter chest stay ONCE PER PROFILE** | `docs/answered/social.md` | **forbids** the audit's "once per account slot" fix (C5). Section 3 proposes fixes inside the lock; per account only if Skyy reopens it (Q4) |
| Lore (Skyy 2026-10-01, approved): the Tab is "like 20 million coins per in-game day, plus interest", payable, prize-giving, ticks only while you are on the server | `research/Isles-of-the-Void-Lore.md` | the headline "20 million per day" stays on screen in every Tab option below |
| No answered line yet on `tab.perHour` or bank cadence | `OPEN-QUESTIONS.md` has none; `research/cloud/Tab-Economy.md` 10 Q1 is unanswered | proposals only |

## 1. Bank interest

### 1.1 What SkyBlock does (search snippets only; the wiki pages were blocked)

| Fact | Source |
|---|---|
| Interest is granted every **3 SkyBlock months** (about 31 real hours, computed from 20-minute days) | [Coins](https://hypixelskyblock.minecraft.wiki/w/Coins) (snippet) |
| Upgrading the bank account (coins + Enchanted Gold Blocks, after a **Gold collection** requirement) raises the max balance **and the max interest** | same snippet |
| Museum milestones each add +2% bank interest (30 milestones) | [Museum/Milestones](https://hypixelskyblock.minecraft.wiki/w/Museum/Milestones) (snippet) |
| Another SkyBlock server uses brackets: 0-10M at 2%, 10-15M at 1% (Basic account) | [CraftersMC Bank](https://craftersmc.wiki.gg/wiki/Bank) (snippet) |
| Hypixel's own bracket percentages (2% / 1% / 0.5% ... falling with the balance, a cap per account tier) | from memory, **UNVERIFIED** |

What we copy: **slow cadence, falling percent per bracket, a hard cap on interest per payout, upgrades through a collection.** SkyWynn pays ~31x as often as Hypixel today.

### 1.2 Options (one profile; balances from the audit's phases: early 5,000, mid 500,000, endgame 10,000,000; 3 online hours a day)

| Option | Rule | Early /day | Mid /day | End /day | 10k -> 10M untouched | 4 capped profiles /day |
|---|---|---|---|---|---|---|
| **A (live)** | 2% per real hour, offline, per profile | 2,400 | ~240,000 | **4,800,000** | 14.5 days | 19,200,000 |
| B | 2% per real **day** (`bank.intervalSeconds` 86,400) | 100 | 10,000 | 200,000 | 349 days | 800,000 |
| C | online hours only, 2% per hour | 300 | 30,000 | 600,000 | 117 days | 2,400,000 (if all played) |
| D | A, but the cap is **per account** (all profiles share one 10M interest base) | 2,400 | ~240,000 | 4,800,000 | 14.5 days | **4,800,000** |
| **E (recommended)** | **daily + brackets + per account** (table 1.3), offline still pays | 100 | 10,000 | **85,000** | 413 days (1M after 233) | **85,000** |

Against active income (audit: 8k / 91k / 363k per online hour = 24k / 273k / 1.09M per 3-hour day): A pays **559%** of an endgame player's daily play income, E pays **7.8%**,
B 18%. The bank should be a nice extra (under ~10% of play), never the main job. 10M untouched no longer matters under E: deposits from play fill the bank, interest only tops it up.

### 1.3 Recommended default (option E)

| Bracket of the **account's** total bank (all profiles added up) | Interest per payout |
|---|---|
| 0 - 1,000,000 | 2% |
| 1,000,000 - 5,000,000 | 1% |
| 5,000,000 - 10,000,000 (`maxPrincipal`) | 0.5% |
| above 10,000,000 | 0% |

- Payout every **86,400 s** (one real day), counted from the last payout as today; offline profiles are still paid (the lock only covers back-pay, offline pay is kept as the friendly choice).
- **Per account:** the brackets apply to the sum of the account's profile banks; each profile gets its share of the interest by its share of that sum (no file merge, no
  per-profile data change). Four alts at 10M earn what one profile at 40M earns: 85,000, not 340,000.
- Catch-up stays capped at 24 periods (now 24 days) - back-pay kept.
- Toggles kept for Skyy: `bank.onlineOnly` (pay only for days the profile was online, Tab-style; default off), `bank.scope` (`account` / `profile`).

### 1.4 Later (optional): bank tiers like SkyBlock's account upgrades

`bank.tiers` table rows (tier | needs collection tier | fee coins | maxPrincipal | top bracket %). Example: Starter 10M; Gold (Gold collection V, 250,000 coins) 25M with a
25M bracket at 0.25%. Coins pay the fee, the collection unlocks it (R3). Not part of the first build.

### 1.5 One-time migration plan (PROJECT-RULES 4; runs once in the first SkyyBank build after Skyy says yes to Q1)

| Step | What happens |
|---|---|
| 0. When | at SkyyBank start, before the first `BankTick` sweep; skipped when the marker exists |
| 1. Settle first | pay every due hourly period with the old 0.1.6 maths (<= 24) so nobody loses interest already earned; then `lastInterestMillis` = now |
| 2. Snapshot | copy `Skyy_SkyyBank/config.properties` to `Skyy_SkyyBank/config-history/<fileId>.<yyyyMMdd-HHmmss-SSS>.bak` + `index.log` line (CONFIG-CONTRACT "Versions"); re-read the copy and compare bytes. Not equal -> **stop**, change nothing, warn once |
| 3. Rewrite only old defaults | `intervalMinutes=60` -> `intervalMinutes=1440` (Server Setup shows it as `bank.intervalSeconds` 86,400). `interestPercent=2` and `maxPrincipal=10000000` keep their text (they become the first bracket and the top). Any other value = **hand-edited: kept**, one change-log line `kept hand-edited intervalMinutes=30 (old default 60)` |
| 4. New keys | `bank.scope`, `bank.brackets`, `bank.onlineOnly` are **not written**: absent = the new default, so the file's other bytes stay |
| 5. Bytes | line-preserving write (CONFIG-CONTRACT 1.4.4): only the changed line, original LF / CRLF, comments and order kept; atomic tmp + move |
| 6. Change log | `Skyy_SkyyBank/config-changes.log`: `<time> \t SkyWynn \t - \t <via> \t bank.intervalSeconds \t 3600 \t 86400 \t ok` + one server INFO line. Status `ok` -> SkyyMenu offers **Undo** (back to 3,600: interest is hourly again from then on, nothing paid back retroactively) |
| 7. Marker | `Skyy_SkyyBank/migrations/bank-daily-1.done` written last (also when nothing needed changing), so it runs once and a failed step 2 retries next start |
| 8. Tell players | one chat line on first join: "[Bank] The Department of Arrivals now pays interest once a day. Everything earned so far has been paid." |

Problem to fix in the same build: `BankConfig.save()` uses `Properties.store` (rewrites the whole file with a date comment) and stores `lastInterestMillis` in the same file on every
payout - the file's bytes already change hourly. Move `lastInterestMillis` to `Skyy_SkyyBank/state.properties` and put the config rows on the config kit (`tools/skyycfg.py`).

## 2. The Tab

### 2.1 The problem in one line

At a 48-minute day, 20,000,000 coins per in-game day = **25,000,000 per online hour**; endgame play makes ~360,000. With option E the bank cannot fund it either, so the literal
rate is never payable (simulation 2.3: "never" in every row) - which breaks Skyy's "payable" rule.

### 2.2 Options that keep "20 million per day"

| # | Option | Keeps on screen | Truth (coins) | Verdict |
|---|---|---|---|---|
| **T1 (recommended)** | **Void Marks.** The bill is in the Department's own money: "20,000,000 Void Marks per day, plus interest". You pay in coins at the posted exchange rate `marksPerCoin` = 20,000,000 x 60 / `tab.dayMinutes` / `tab.perHour` (about 278 at 90,000/h and a 48-min day) | "20 million per day" verbatim **and** outrageous billions ("You owe 3,000,000,000 Void Marks") | `tab.perHour` coins per online hour | keeps the absurd numbers Skyy liked, payable, day-length-proof; the joke: "Exchange rate set by Form 20-M" |
| T2 | **Department day.** "20,000,000 coins per day" - but a Department day is `tab.voidDaySeconds` of your online time (20M / 90k = ~222 hours: "Office hours apply") | the exact words, in coins | same | payable, but the bill at reveal is ~11M, not absurd |
| T3 | literal 20M coins per in-game day, bank / income scaled up | everything | 25M/h | never payable (2.3); would need 70x income, breaking the LOCKED Bazaar price tables |
| T4 | literal rate, payments count 100x | everything | hidden multiplier | same maths as T1 but hidden - players see coins vanish at a weird rate; T1 says it openly |

Milestones (`research/cloud/Tab-Economy.md` 4) then count **Void Marks paid**: 1M ... 100B marks stay as written (100B marks = ~360M coins at 278).

### 2.3 Simulation - online hours (real days) to Paid in Full

Model (python): the Tab accrues `perHour` for every active online hour from day one (hidden until the Zone 5 reveal, so early / mid game only builds the bill); interest on
min(balance, 2 x the reveal bill); `tab.maxBalance` = 1,000 hours of accrual. The three income columns are the three **endgame** levels (the Tab opens at Zone 5).
Players: **casual** pays 25% of income, 1.5 h a day, 150 hidden hours; **regular** 40%, 3 h, 120 h; **hardcore** 60%, 6 h, 100 h. Bill = coins at the reveal.

| Rate (coins per online hour) | Interest | Income 250k/h | 360k/h (audit endgame) | 600k/h (late) | Bill at reveal |
|---|---|---|---|---|---|
| Literal 25,000,000 | 0.5% per in-game day | never / never / never | never / never / never | never / never / never | 2.5-3.75B |
| 160,000 (45% rule, Tab-Economy 2) | 0.5% per 24 online h | never / never / never | never / never / 295 h (49 d) | never / 247 h (82 d) / 81 h (14 d) | 16-24M |
| 110,000 (30%) | same | never / never / 284 h (47 d) | never / 406 h (135 d) / 105 h (18 d) | 432 h (288 d) / 103 h (34 d) / 45 h (8 d) | 11-16.5M |
| **90,000 (25%, recommended)** | same | never / 1,226 h (409 d) / 153 h (26 d) | **never / 205 h (68 d) / 72 h (12 d)** | 231 h (154 d) / 73 h (24 d) / 34 h (6 d) | 9-13.5M |

(cells: casual / regular / hardcore). Interest at 1% instead of 0.5% adds only 1-5% to each time (2x cap). **Interest per in-game day is the trap:** 0.5% per 48-min day is
0.625% per online hour, which on a 2x-capped 16M bill adds ~200k/h - more than the accrual. So interest counts per `tab.interestSeconds` of **online** time (86,400 = 24 h).

Reading it: at 25% of measured income a regular endgame player pays off in ~2 months of 3-hour days, a hardcore one in ~2 weeks, a casual one only at late-game income -
a real race, never a wall. Casual players still collect the early milestone titles. Tab-Economy's "40-50%" calibration is too steep (the 160k row).

### 2.4 Recommended Tab rows

`tab.perHour` **90,000** (placeholder = 25% of measured good endgame income, section 4 #1), `tab.headlinePerDay` 20,000,000 (display, Void Marks), `tab.dayMinutes`
(display only), `tab.interestPercent` 0.5 per `tab.interestSeconds` 86,400 of active time, `tab.interestCapMult` 2, `tab.maxBalanceHours` 1,000, `tab.afkSeconds` 300.
The Setup page shows the derived exchange rate and "At this server's income of X/h a regular player pays off in N hours".

## 3. Starter grant (C5) - inside "once per profile"

The lock keeps 10,000 coins for **every** profile, so "once per account slot" is out unless Skyy reopens it. The abuse is the loop create -> grant -> AH-buy junk from the main
profile (allowed, LOCKED) -> delete -> repeat (delete frees the slot at once). Fixes that keep one grant per profile:

| # | Fix | Laundering after the fix | Cost to honest players |
|---|---|---|---|
| **S1 (recommended)** | **Vesting:** the grant arrives in 10 steps of 1,000 over the profile's first `coins.starterVestSeconds` **3,600 s of active play** (AFK pauses it) | 10,000 per hour of alt play = early-game income; worthless to a mid / endgame player (91k+/h) | none - a new player spends slower than 1,000 per 6 minutes |
| S2 | **Starter-bound coins:** the unspent part of the grant cannot leave the profile (AH buy from a same-account seller, `/pay`, `/trade`, guild deposit) for `coins.starterBindSeconds` 21,600 | still leaks through Bazaar buy -> shared vault -> sell on the main (about 82% after the 22.2% spread, less after the demand drop) | small: a rule check on 4 transfer paths |
| S3 | **Grant waits after a delete:** a profile created within `profiles.regrantCooldownSeconds` 86,400 of deleting one gets its grant only when the cooldown ends | 10,000 per day per account | a player who restarts gets coins a day later |
| S4 | once per account slot | none | needs Skyy to reopen the 2026-10-01 lock (Q4) |

Recommend **S1 + S3** (S3 only bites people who delete). S2 adds code on four paths for little gain because the shared vault (LOCKED, Wynncraft style) moves items freely.
A restored profile keeps its balance file, so `starterK()` never grants it again (read from the 0.1.5 script; needs a live check - section 5).

## 4. Measure first (for the local session)

| # | Measure | Decides | How |
|---|---|---|---|
| 1 | Coins per online hour of a good endgame player (Z4-Z5 gear), split by source | `tab.perHour` (25% of it) | timed session on a test profile; `coins:fn:get` before / after; SELL lines in `Skyy_SkyyBazaar/trades.log` |
| 2 | Same for an early and a mid profile | the bracket edges (1M / 5M) | same |
| 3 | Sum of all `Skyy_SkyyBank` accounts, how many sit at 10M, interest paid per day | how big the bank change is for live players | read-only copy into scratch |
| 4 | Profiles per account, creates and deletes so far | whether C5 was used | `Skyy_SkyyProfiles` copy |
| 5 | Hytale day length on the test world | `marksPerCoin` display | world config / `/time` |
| 6 | Online hours a real player needs from start to Zone 5 | hidden hours (bill at reveal) | play log / SkyySkills playtime |
| 7 | Whether a new profile in a freed slot gets a fresh 10,000 | S1 / S3 needed or not | test on a copy: delete, create, read the purse |

## 5. Server Setup rows

| Row | Default | Range | Mod |
|---|---|---|---|
| `bank.intervalSeconds` | 86,400 (live 3,600) | 60 - 604,800 | SkyyBank |
| `bank.brackets` (table: up to | % ) | 1,000,000 2% / 5,000,000 1% / 10,000,000 0.5% | 1-8 rows, 0-100% | SkyyBank |
| `bank.maxPrincipal` | 10,000,000 | 0 - 10^12 | SkyyBank |
| `bank.scope` | account | account / profile | SkyyBank |
| `bank.onlineOnly` | off | on / off | SkyyBank |
| `bank.catchUpPeriods` | 24 | 1 - 365 | SkyyBank |
| `tab.perHour` / `tab.headlinePerDay` | 90,000 / 20,000,000 | 0 - 10^9 / display | SkyyEconomy (Tab) |
| `tab.interestPercent` / `tab.interestSeconds` | 0.5 / 86,400 | 0-10 / 3,600-604,800 | same |
| `tab.interestCapMult` / `tab.maxBalanceHours` | 2 / 1,000 | 1-10 / 10-100,000 | same |
| `coins.starterGrant` / `coins.starterVestSeconds` | 10,000 / 3,600 | 0 - 10^7 / 0 - 86,400 | SkyyCoins (today hard-coded `10000L`) |
| `profiles.regrantCooldownSeconds` | 86,400 | 0 - 604,800 | SkyyProfiles + SkyyCoins bridge |

## For the local session (UNVERIFIED)

| # | Item |
|---|---|
| 1 | All income numbers are the audit's paper estimates; the Tab and bracket defaults are placeholders until section 4 #1-2 are measured. |
| 2 | Hypixel bracket percentages are from memory; only the cadence, upgrade path and museum +2% come from search snippets. |
| 3 | Whether SkyyBank already uses the config kit (Server-Setup-Research lists only `/bankconfig` and `config.properties`); the History / change-log / Undo steps need it. |
| 4 | CONFIG-CONTRACT has no `via=migration`; use `console` (who null) or add a `migration` via in the kit - local choice. |
| 5 | Per-account interest needs all of an owner's profile account files (`<uuid>.properties`, `<uuid>-pN.properties`) summed in one sweep - check the worker can list them by owner cheaply. |
| 6 | Whether a deleted profile's slot key (`<uuid>-pN`) is reused by the next create and its balance file moved to the archive (decides C5's size). |
| 7 | AFK detection for the starter vesting and the Tab (Tab-Economy 9 #3). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Bank: pay once a real day, with falling brackets (2% up to 1M, 1% to 5M, 0.5% to 10M) counted over all your profiles together? Today one full bank makes 4.8M a day while you sleep | [yes, option E, offline still paid, back-pay kept] |
| 2 | Tab: show it in "Void Marks" (20,000,000 marks a day, billions owed) and pay in coins at a posted exchange rate, so it keeps your number but can really be paid? | [yes, T1] |
| 3 | Tab rate: about a quarter of what a good endgame player earns per hour (measured), so a regular player pays it off in about two months of play? | [25%, 90,000 per hour placeholder] |
| 4 | Starter coins stay once per profile (your 2026-10-01 answer). OK to pay them out over the first hour of play, and a day later if you just deleted a profile? Or switch to once per account slot? | [vest over 1 hour + 1-day wait after a delete; lock kept] |
| 5 | Later: bank upgrades like SkyBlock (a Gold collection tier unlocks a bigger bank, coins pay the fee)? | [later, not in the first build] |
