# The Tab - endgame coin sink design

**Revision 2026-10-06:** sections 2-5 and 7-10 rewritten to `research/cloud/Bank-Tab-Calibration.md` (Void Marks shown, coins paid at `tab.perHour` 90,000 = 25% of endgame income; interest per 24 ONLINE hours; milestones re-scaled; audit C1). The calibration is still Skyy's Q1 decision (section 10): everything below is the recommended default, not locked.

Cloud draft, 2026-10-03 (revised 2026-10-06). Paper design; nothing built. Source: `research/Isles-of-the-Void-Lore.md` (Skyy 2026-10-01: about 20 million coins per in-game day plus
interest, "something outrageous", payable, the Receipt / "Paid in Full" ending, optional prestige - approved, "thats beautiful! its perfect"). Money facts read from
`research/Server-Setup-Research.md` (starter grant 10,000 coins, Bank 2% per real hour up to 10,000,000 principal, Bazaar base prices) and `docs/plans/SkyyEconomy-Plan.md`.
All numbers are placeholders to be set from a real income measurement (section 3).

## 0. The one-line design

**The Tab is a prize-giving sink, never a punishment.** It grows while you are on the server; you can pay any amount at any time; every payment milestone gives a title
or cosmetic; paying it off completely is possible but legendary and gives the Receipt, the "Paid in Full" wall and the "welcome home" twist. Nothing bad ever happens
if you do not pay.

## 1. Rules (from the lore, kept exactly)

| Rule | Value |
|---|---|
| Who is charged | per **profile** (progression is per profile); only for days you are **online** (not AFK-capped; see exploits) |
| Headline rate | **20,000,000 per in-game day** (Skyy's number), plus interest - shown in **Void Marks** (section 2); paid in coins at a posted rate |
| Revealed | not explained at the start; the dragon (Zone 5, Story-Script-Zones-2-5) mentions "fees"; the Tab opens as a menu entry then. The bill already counts the days you "stayed" ("absurd by the time you find out") |
| Payable | yes - no fake-impossible maths. A race you can win with endgame income (section 2.3: a regular player in about 2 months, a hardcore one in about 2 weeks) |
| Pay-off ending | the Receipt (rarest trophy), title "Paid in Full", name on the Paid in Full wall, statue for the first payer on a server; the exit opens onto your own shard; rent-free forever ("the Void IS your home dimension") |
| Optional prestige | go "home" anyway: permanent perks reset; a hiccup pulls you straight back: **"Welcome back! Your ticket number is #4,000,000,002."** (Skyy's favourite - keep exactly; the ticket number rises by one per prestige) |

## 2. The numbers - what "20 million per day" really means

**The problem:** at a 48-minute day, 20,000,000 coins per in-game day = 25,000,000 per online hour; a good endgame player earns about 360,000 per online hour (audit C1: ~70x). The literal rate is never payable, which breaks Skyy's "payable" rule.

**The fix (Bank-Tab-Calibration option T1, recommended): Void Marks.** The bill is in the Department's own money: **"20,000,000 Void Marks per day, plus interest"** (Skyy's number, word for word, on screen).
You pay in **coins** at a posted exchange rate: `marksPerCoin = tab.headlinePerDay x 60 / tab.dayMinutes / tab.perHour` (the Department's joke: "Exchange rate set by Form 20-M"). The truth is `tab.perHour`, coins per active online hour.

| Day length (real minutes) | Marks per coin at `tab.perHour` 90,000 | Marks accrued per online hour |
|---|---|---|
| 15 | about 889 | 80M |
| 24 | about 556 | 50M |
| **48** | **about 278** | **25M** |
| 60 | about 222 | 20M |

The marks column changes with the day length, the coins never do (`tab.perHour` stays 90,000), so changing the day length cannot break the economy. Day length is **UNVERIFIED** (guides say 15 / 24 / 48 / 60 minutes): `tab.dayMinutes` is display only.

### 2.1 Rows in short

| Item | Default |
|---|---|
| `tab.perHour` (the truth, coins per active online hour) | **90,000** = 25% of a good endgame player's measured income (placeholder until section 3 #1 is measured) |
| Bill at the Zone 5 reveal | 100-150 hidden online hours = 9-13.5M coins = about 2.5-3.75B marks ("You owe 3,000,000,000 Void Marks") |
| Interest | 0.5% per `tab.interestSeconds` **86,400 s of ONLINE time** (24 h), on the unpaid balance only after the reveal, counted on at most 2x the reveal bill (`tab.interestCapMult`) |
| Accrual cap | `tab.maxBalanceHours` 1,000 hours of accrual (= 90M coins = 25B marks) so a casual who ignores it is not buried |

**Why interest is per online time, not per in-game day:** 0.5% per 48-minute day is 0.625% per online hour, which on a capped 16M bill adds about 200k per hour - more than the accrual. So it counts per 24 online hours.

### 2.2 Payability model (online hours, real days at 3 h/day for the regular player)

Model (Bank-Tab-Calibration 2.3): accrues from day one (hidden until the reveal), interest as above. Players: **casual** pays 25% of income at 1.5 h a day with 150 hidden hours; **regular** 40%, 3 h, 120 h; **hardcore** 60%, 6 h, 100 h. Cells: casual / regular / hardcore.

| Rate (coins per online hour) | Income 250k/h | 360k/h (audit endgame) | 600k/h (late) | Bill at reveal (coins) |
|---|---|---|---|---|
| Literal 25,000,000 | never / never / never | never / never / never | never / never / never | 2.5-3.75B |
| 160,000 (the old 45% rule) | never / never / never | never / never / 295 h | never / 247 h / 81 h | 16-24M |
| 110,000 (30%) | never / never / 284 h | never / 406 h / 105 h | 432 h / 103 h / 45 h | 11-16.5M |
| **90,000 (25%, recommended)** | never / 1,226 h / 153 h | **never / 205 h (68 d) / 72 h (12 d)** | 231 h / 73 h / 34 h | 9-13.5M |

Reading it: at 25% of measured income a regular endgame player pays off in about 2 months of 3-hour days, a hardcore one in about 2 weeks, a casual one only at late-game income - a real race, never a wall. Casual players still collect the early milestone titles. The old 40-50% calibration was too steep. Interest at 1% instead of 0.5% adds only 1-5% to each time (the 2x cap).

The Setup page shows the derived exchange rate and "At this server's income of X/h a regular player pays off in N hours."

## 3. What to measure first (for the local session)

| # | Measure | Decides | How |
|---|---|---|---|
| 1 | Coins per online hour of a good endgame player (Z4-Z5 gear), split by source | `tab.perHour` (25% of it) | timed session on a test profile; `coins:fn:get` before / after; SELL lines in `Skyy_SkyyBazaar/trades.log` |
| 2 | Same for an early and a mid profile | bank bracket edges | same |
| 3 | Online hours a real player needs from start to Zone 5 | hidden hours (bill at reveal) | play log / SkyySkills playtime |
| 4 | Hytale day length on the test world | `marksPerCoin` display | world config / `/time` |
| 5 | Share of income the Tab removes | should be about 25% of a good player's gross, no more | derived from 1 |

## 4. How you pay and what you get

| Part | Rule |
|---|---|
| Paying | `/tab` page (vanilla look): balance in marks (coins shown beside it), the posted rate, paid so far, Pay buttons (1% / 10% / 100% of balance, a custom amount, Pay all). You pay coins; the page shows the marks they clear. A payment asks to confirm above `tab.payConfirm` (OPEN-QUESTIONS 297: confirms for money) |
| Source of coins | purse only (not bank, not guild bank): payment from the bank is allowed after a "Withdraw" step so it is visible |
| Cumulative paid | tracked per profile in **Void Marks**, never goes down; milestones use total marks paid, not the current balance |
| Never lost | no item or progression loss from owing; the Tab never blocks anything except the Receipt/exit |

### Milestone ladder (marks paid; coins at 278 marks per coin; both scale with the rate)

The ladder stops at about 5B marks because a regular player pays roughly 8B marks in total by Paid in Full (bill about 3B plus the accrual while paying); the old 10B / 100B steps would have lain beyond Paid in Full.

| Total paid (marks) | About in coins | Reward |
|---|---|---|
| 1M | 3,600 | title "Lease Holder" |
| 10M | 36,000 | the Tab menu icon changes (cosmetic) |
| 100M | 360,000 | title "Long-Term Resident" + small cosmetic (a ticket pin) |
| 1B | 3.6M | title "Frequent Flyer" + a wall plaque in the waiting room |
| 2.5B | 9M | cosmetic aura "Overdue" (a joke - a tiny cloud follows you) |
| 5B | 18M | title "Account In Good Standing (Almost)" |
| Paid in Full | the whole bill | **the Receipt**, title **"Paid in Full"**, name on the **Paid in Full wall**; first payer on a server also gets a **statue**; shard becomes rent-free; the exit door scene |
| Prestige 1, 2, 3... | - | "Welcome back! Your ticket number is #4,000,000,00N" |

(The first four milestones fire early in the paying so that average players still feel progress; the later ones are for the hardcore. Text for the milestones uses `{unit}` from `tab.unit`, see `research/cloud/Tab-Prestige-Scripts.md`.)

## 5. Prestige (optional, after Paid in Full)

Full design: `research/cloud/Prestige-Spec.md` (this table is the short form).

| Item | Proposal |
|---|---|
| Trigger | talk to the clerk after Paid in Full: "go home anyway" (prestige 1); later runs need the Re-Audit (class level >= `prestige.reqLevel` 75 and the Zone 5 guardian beaten in this run) - no Tab, because it is rent-free forever |
| Keeps | identity: titles, cosmetics, pets, Pocket Shards, learned recipes, the Receipt, every item |
| Resets | run progress: skill levels (to a floor), coins (back to the starter grant 10,000), zone and boss progress. Details: Prestige-Spec (decision for Skyy) |
| Perks | small permanent perks that save time, not power: +skill XP per prestige (capped), +1 Pocket Shard slot, a prestige title / colour (caps in Prestige-Spec) |
| Hiccup | after a short scene you are pulled back; the Tab does not return (rent-free forever), so prestige is about the new run, not the debt |
| Cap | `prestige.max` (default 10) so numbers do not run away |

## 6. Exploit and edge-case check

| Risk | Handling |
|---|---|
| **AFK ticking** | the tab only ticks for **active online** time: pause after N minutes without movement/commands (`tab.afkSeconds`, default 300). Skyy's rule: only days you are on the server. AFK farming still pays Skyy's own income but not extra Tab |
| **Alt profiles to dodge it** | each profile has its own Tab; a fresh profile starts at 0 and has not "stayed" long - no loophole (the Tab is not a gate) |
| **Moving coins between profiles** (Vault, AH, `/pay`, guild bank) | allowed; the Tab only counts what was **paid from the purse of that profile**. Cumulative paid is per profile. A player cannot pay another profile's Tab |
| **Paying with coins from bypass/market flips** | fine (it is a sink); the Receipt is the prize, not a bug |
| **Day-length / rate changes by an admin** | accrual is stored in marks at the rate in force each hour (no retroactive change); `tab.perHour` change asks to confirm (curve/rates rule) |
| **Profile delete and restore** | the Tab is archived and restored with the profile (it freezes while archived) |
| **Server crash / offline accrual** | online time only; the clock uses a monotonic tick count; a restart never adds time |
| **Rounding / overflow** | balance in a `long`; marks are a `long`: 25B marks at the 1,000 h accrual cap is far from the 63-bit ceiling; compact display (`fmt`) already goes to billions, add trillions |
| **Negative balance / overpay** | overpay is refused, or credited as a "deposit on account" (a small receipt line) - simpler: refuse |
| **Death penalty** | coins lost on death (10-25%) reduce the purse only, never the Tab |
| **First payer statue race** | the statue goes to the first profile to hit Paid in Full on that server (stored as the world "first receipt" flag); ties resolved by timestamp |
| **Griefing via guilds** | none: guilds cannot pay a member's Tab |
| **Inflation interplay** | the Tab removes coins permanently (a sink); keep the faucet/sink ratio in the economy review (`SkyyEconomy` 0.2) |
| **Creative mode** | no accrual in creative |

## 7. Server Setup rows (config kit)

| Row | Default | Notes |
|---|---|---|
| `tab.enabled` | on | |
| `tab.perHour` | 90,000 | coins per active online hour = the truth; the page shows the per-day figure and the exchange rate |
| `tab.headlinePerDay` | 20,000,000 | display, in marks (Skyy's number) |
| `tab.dayMinutes` | 48 (UNVERIFIED) | display only; feeds `marksPerCoin` |
| `tab.unit` | `marks` | `marks` or `coins` (the `{unit}` word in all Tab text) |
| `tab.interestPercent` / `tab.interestSeconds` | 0.5 / 86,400 | per 86,400 s of ONLINE time, after the reveal only |
| `tab.interestCapMult` | 2 | interest counts on at most 2x the reveal bill |
| `tab.maxBalanceHours` | 1,000 | accrual cap in online hours |
| `tab.afkSeconds` | 300 | no accrual after this long without movement / commands |
| `tab.revealPart` | `zone5` | `zone5` / `purse` / `off` |
| milestone list | section 4 | table: marks, title, cosmetic |
| `tab.payConfirm` | on | confirm above a threshold |
| `prestige.enabled` / `prestige.max` / perk rows | off until the Tab ships / 10 | see Prestige-Spec |

All times in seconds (PROJECT-RULES); coin and mark amounts as whole numbers. Changing `tab.perHour` asks to confirm (rates rule).

## 8. Wording (for the Tab page and quests)

`{unit}` is "Void Marks" (default) or "coins". Where Skyy's own lines appear they stay word for word.

| Place | Text |
|---|---|
| Headline | "20,000,000 Void Marks per day, plus interest" |
| Menu line | "Your tab: 1.37b Void Marks. Interest accrued over infinity." |
| Rate line | "Exchange rate set by Form 20-M: 278 Void Marks per coin." |
| Pay button | "Settle part of the account" |
| Page footer | "Rent is charged for every day you have 'stayed'. You have stayed 117 days." |
| Pay-off | "PAID IN FULL. Please take your Receipt. Welcome home - your shard is now rent-free." |
| Prestige | "Welcome back! Your ticket number is #4,000,000,002." |

## 9. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Real endgame income per online hour (section 3 #1) - this decides `tab.perHour`. All income numbers are paper estimates (audit: about 8k / 91k / 363k per online hour early / mid / endgame). |
| 2 | Hytale day length (default and the setting used on the test world); only `marksPerCoin` display depends on it. |
| 3 | How to detect "active" for AFK (movement, hit, command) cheaply (the 1 s Perks.tick pattern exists in SkyySkills). |
| 4 | Where the Tab lives: SkyyEconomy 0.1 (coins core) is the natural home; it needs a profile-keyed store (`PROFILES-CONTRACT`) holding marks owed, marks paid, online-time counters. |
| 5 | Whether a statue / wall can be built (a prefab placed once on the waiting room island) - cosmetic, later. |
| 6 | Interest per 86,400 s of ONLINE time needs a per-profile online-seconds counter that survives restarts (monotonic ticks, no offline accrual). |

## 10. Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Show the Tab in "Void Marks" (20,000,000 marks a day, billions owed) and pay in coins at a posted exchange rate, so it keeps your number but can really be paid? (Bank-Tab-Calibration Q2) | [yes, T1] |
| 2 | Tab rate: about a quarter of what a good endgame player earns per hour (measured), so a regular player pays it off in about two months of play? (Q3) | [25%, 90,000 per hour placeholder] |
| 3 | Interest and total accrual capped, and interest counted per 24 hours of online time, so casual players are never buried? | [yes: 0.5% per 24 online h, 2x cap, 1,000 h accrual cap] |
| 4 | What should prestige reset - skills to a floor, coins and progress flags, or less? | [skills to a floor, coins and progress reset; cosmetics / pets / titles / items kept] |
| 5 | Should paying milestones unlock real convenience (e.g. +1 Pocket Shard slot) or only cosmetics / titles? | [only cosmetics / titles] |
