# The Tab - endgame coin sink design

Cloud draft, 2026-10-03. Paper design; nothing built. Source: `research/Isles-of-the-Void-Lore.md` (Skyy 2026-10-01: about 20 million coins per in-game day plus
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
| Headline rate | **20,000,000 coins per in-game day** (Skyy's number), plus interest |
| Revealed | not explained at the start; the dragon (Zone 5, Story-Script-Zones-2-5) mentions "fees"; the Tab opens as a menu entry then. The bill already counts the days you "stayed" ("absurd by the time you find out") |
| Payable | yes - no fake-impossible maths. A race you can win with endgame income |
| Pay-off ending | the Receipt (rarest trophy), title "Paid in Full", name on the Paid in Full wall, statue for the first payer on a server; the exit opens onto your own shard; rent-free forever ("the Void IS your home dimension") |
| Optional prestige | go "home" anyway: permanent perks reset; a hiccup pulls you straight back: **"Welcome back! Your ticket number is #4,000,000,002."** (Skyy's favourite - keep exactly; the ticket number rises by one per prestige) |

## 2. The numbers - what "20 million per day" really means

(updated 2026-10-06: **read `research/cloud/Bank-Tab-Calibration.md` first.** It supersedes the rate and bank figures below: the Tab is shown in Void Marks and paid in coins at a posted rate, `tab.perHour` placeholder 90,000 coins (about 25% of a good endgame player's hourly income, not the 40-50% used here), interest per 24 online hours, and the bank changes to once-a-day falling brackets (audit C1, C2). Section 2's tables are kept as the original reasoning.)

How long an in-game day lasts is **UNVERIFIED**: web guides disagree (about 48 minutes per day in one, a 15 minute server default of 600 s day + 300 s night in another, a full
cycle "about one hour" in a third). Check the Hytale world config locally (the day-length setting) and the Server Setup row; the design below uses a row `tab.dayMinutes`.

| Day length (real minutes) | Accrual per online hour at 20M/day | Hidden arrears after 60 online hours |
|---|---|---|
| 15 | 80M | 4.8B |
| 24 | 50M | 3.0B |
| **48** | **25M** | **1.5B** |
| 60 | 20M | 1.2B |

Rule: **define the real rate per online hour, derive the "per day" figure from it**, otherwise changing the day length changes the economy. So Server Setup shows both
(`tab.perHour` is the truth; the quest text shows `tab.perHour x tab.dayMinutes / 60` as "per day").

### Payability model (script, 48-minute day, interest on the unpaid balance only after the reveal; 60 hidden hours; spend 80% of income)

| Interest per day | Income 30M/h | 60M/h | 120M/h |
|---|---|---|---|
| 0% | never | about 66 h | about 22 h |
| 0.5% | never | about 85 h | about 23 h |
| 1% | never | about 137 h | about 25 h |

Reading it: at 25M/h accrual, the Tab only shrinks for a player earning more than that. Anything under about 30M/h of income never pays off; 60M/h pays off in a few days
of play; 120M/h in about a day. **So the right rate depends on what endgame income really is - nobody knows yet** (the economy is not built to that scale; the Bank stops paying
interest above 10M; Bazaar prices are in single coins). Therefore:

- **Calibrate**: set `tab.perHour` = **40-50% of the measured income of a good endgame player** (coins per online hour over a typical endgame session). Then a good player nets
  money against the Tab and pays it off in tens of hours, and an average player never does (it stays a prestige goal).
- **Until a measurement exists**, ship the headline value but make it a Server Setup row and a Setup page preview: "At your server's income of X/h the Tab is paid off in N hours."
- Interest cap: **0.5% per in-game day on the unpaid balance, counted on at most 2x the reveal-time bill** (like the Bank's `maxPrincipal`). Without a cap, a player who
  waits just owes a runaway number and gives up; with the cap the Tab is always beatable by a rising income.
- Accrual cap: balance stops accruing at `tab.maxBalance` (default 200 in-game days of accrual) so a casual who ignores it for months is not buried.

## 3. What to measure first (for the local session)

| Measure | How |
|---|---|
| Coins earned per online hour at Zone 4-5 gear (selling to Bazaar, AH, NPC shops once they exist) | a timed endgame session on a test profile; read `coins:fn:get` before/after |
| Total coins in circulation per profile at Zone 5 | sample from the save data (`Skyy_SkyyCoins`) |
| Day length | the world config / `/time` |
| The ratio of Tab-sink to total income | the Tab should remove about 20-30% of a good endgame player's gross income, no more |

## 4. How you pay and what you get

| Part | Rule |
|---|---|
| Paying | `/tab` page (vanilla look): balance, rate, paid so far, Pay buttons (1% / 10% / 100% of balance, a custom amount, Pay all). A payment also asks to confirm above a threshold (OPEN-QUESTIONS 297: confirms for money) |
| Source of coins | purse only (not bank, not guild bank): payment from the bank is allowed after a "Withdraw" step so it is visible |
| Cumulative paid | tracked per profile, never goes down; milestones use total paid, not the current balance |
| Never lost | no item or progression loss from owing; the Tab never blocks anything except the Receipt/exit |

### Milestone ladder (placeholder amounts, scale with `tab.perHour`)

| Total paid | Reward |
|---|---|
| 1M | title "Lease Holder" |
| 10M | the Tab menu icon changes (cosmetic) |
| 100M | title "Long-Term Resident" + small cosmetic (a ticket pin) |
| 1B | title "Frequent Flyer" + a wall plaque in the waiting room |
| 10B | cosmetic aura "Overdue" (a joke - a tiny cloud follows you) |
| 100B | title "Account In Good Standing (Almost)" |
| Paid in Full | **the Receipt**, title **"Paid in Full"**, name on the **Paid in Full wall**; first payer on a server also gets a **statue**; shard becomes rent-free; the exit door scene |
| Prestige 1, 2, 3... | "Welcome back! Your ticket number is #4,000,000,00N" |

(The first four milestones fire in the early part of paying so that average players still feel progress; the later ones are for the hardcore.)

## 5. Prestige (optional, after Paid in Full)

| Item | Proposal |
|---|---|
| Trigger | talk to the clerk after Paid in Full: "go home anyway" |
| Reset | **keeps**: pets, cosmetics, titles, Receipt, collections milestones that give recipes, one Pocket Shard slot per prestige. **resets**: skill levels (to a floor), coins, gear, island size tier? (decision for Skyy) |
| Perks | permanent: +1% skill XP per prestige (cap), +1 Pocket Shard slot, +1 pet slot capacity? (placeholders), a prestige title/colour |
| Hiccup | after a short scene you are pulled back; the Tab restarts at 0 and is rent-free (so prestige is about the new run, not the debt) |
| Cap | optional `prestige.max` (default 10) so numbers do not run away |

## 6. Exploit and edge-case check

| Risk | Handling |
|---|---|
| **AFK ticking** | the tab only ticks for **active online** time: pause after N minutes without movement/commands (`tab.afkSeconds`, default 300). Skyy's rule: only days you are on the server. AFK farming still pays Skyy's own income but not extra Tab |
| **Alt profiles to dodge it** | each profile has its own Tab; a fresh profile starts at 0 and has not "stayed" long - no loophole (the Tab is not a gate) |
| **Moving coins between profiles** (Vault, AH, `/pay`, guild bank) | allowed; the Tab only counts what was **paid from the purse of that profile**. Cumulative paid is per profile. A player cannot pay another profile's Tab |
| **Paying with coins from bypass/market flips** | fine (it is a sink); the Receipt is the prize, not a bug |
| **Day-length / rate changes by an admin** | accrual is stored in coins at the rate in force each hour (no retroactive change); `tab.perHour` change asks to confirm (curve/rates rule) |
| **Profile delete and restore** | the Tab is archived and restored with the profile (it freezes while archived) |
| **Server crash / offline accrual** | online time only; the clock uses a monotonic tick count; a restart never adds time |
| **Rounding / overflow** | balance in a `long`; at 1.2B per 60 h the 63-bit ceiling is far away; compact display (`fmt`) already goes to billions, add trillions |
| **Negative balance / overpay** | overpay is refused, or credited as a "deposit on account" (a small receipt line) - simpler: refuse |
| **Death penalty** | coins lost on death (10-25%) reduce the purse only, never the Tab |
| **First payer statue race** | the statue goes to the first profile to hit Paid in Full on that server (stored as the world "first receipt" flag); ties resolved by timestamp |
| **Griefing via guilds** | none: guilds cannot pay a member's Tab |
| **Inflation interplay** | the Tab removes coins permanently (a sink); keep the faucet/sink ratio in the economy review (`SkyyEconomy` 0.2) |
| **Creative mode** | no accrual in creative |

## 7. Server Setup rows (config kit)

`tab.enabled`, `tab.perHour` (coins per online hour; shows the per-day figure), `tab.dayMinutes` (display only), `tab.interestDayPercent` (0.5), `tab.interestCapMult` (2),
`tab.maxBalance`, `tab.afkSeconds`, `tab.revealPart` (what reveals it: `zone5` default / `purse` / `off`), the milestone list (table: amount, title, cosmetic), `tab.payConfirm`,
`prestige.enabled`, `prestige.max`, prestige perk rows. All times in seconds (PROJECT-RULES); coin amounts as whole numbers.

## 8. Wording (for the Tab page and quests)

| Place | Text |
|---|---|
| Menu line | "Your tab: 1.37b coins. Interest accrued over infinity." |
| Pay button | "Settle part of the account" |
| Page footer | "Rent is charged for every day you have 'stayed'. You have stayed 117 days." |
| Pay-off | "PAID IN FULL. Please take your Receipt. Welcome home - your shard is now rent-free." |
| Prestige | "Welcome back! Your ticket number is #4,000,000,002." |

## 9. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Hytale day length (default and the setting used on the test world). |
| 2 | Real endgame income per online hour (section 3) - this decides `tab.perHour`. Everything else is a placeholder until then. |
| 3 | How to detect "active" for AFK (movement, hit, command) cheaply (the 1 s Perks.tick pattern exists in SkyySkills). |
| 4 | Where the Tab lives: SkyyEconomy 0.1 (coins core) is the natural home; it needs a profile-keyed store (`PROFILES-CONTRACT`). |
| 5 | Whether a statue/wall can be built (a prefab placed once on the waiting room island) - cosmetic, later. |

## 10. Questions for Skyy

1. Define the rate per online hour (recommended) instead of per game day, so a day-length change cannot break the economy?
2. Is a cap on interest and on total accrual OK (so casual players are never buried)?
3. What should prestige reset - skills and gear, or only coins and progress flags? (I proposed skills to a floor, coins and gear reset, cosmetics/pets/titles kept.)
4. Should paying milestones unlock real convenience (e.g. +1 Pocket Shard slot) or only cosmetics/titles?
