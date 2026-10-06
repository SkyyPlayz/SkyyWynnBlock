# Zone Specials and the Clerk of the Week ("mayor lite")

Cloud draft, 2026-10-06. Paper design; nothing built. Skyy asked for rotating, announced buffs (Elites-Events-Spec 2.5: "the Board announces a zone special"). Numbers are placeholders (Server Setup, section 8). This is a **lean round** for phase 1 (only live effects, no saved player data), a full round only if elections or coin effects are added later (PROJECT-RULES 4).

## 0. What SkyBlock does (research, search snippets only; the wiki pages were blocked)

| Fact | Source |
|---|---|
| An election runs every SkyBlock year (**124 real hours**) with **five candidates** | [Mayor Elections](https://hypixelskyblock.minecraft.wiki/w/Mayor_Elections) (snippet) |
| Players vote once per account at the Community Center; votes can be raised by Fame rank / Voter's Badge | same snippet |
| The winner's shown perks run until the next election; the **runner-up becomes Minister** and adds one perk | same snippet |
| Most mayors have **4 perks**, usually 1-3 active at once; an 8% chance of a 4th if already at 3 | same snippet |
| The Better Mayors update (0.20.3) reworked perks; max 4 perks | [patch notes](https://hypixel.net/threads/5692280) (snippet) |
| Mayors named in the search: Aatrox, Cole, Diana, Diaz, Finnegan, Foxy, Marina, Paul, Scorpius, Jerry (from memory, **UNVERIFIED**: each has a theme - slayers, mining, a ritual event, shops/AH, farming, spooky/events, fishing, dungeons, bribes/coins, chaos) | search results, perk details not readable |

What we copy: **a fixed rotation of named people with a few themed perks, announced ahead, a countdown on a board, one drawback allowed**. What we drop: global votes with fame ranks (too big for a small server; optional later, section 7), coin faucets (Scorpius-style bribes, Diaz-style shop deals), and anything that touches the economy locks.

## 1. Two layers (the whole system)

| Layer | Name | Rotates | Scope | Size |
|---|---|---|---|---|
| **Zone Special** | "Today on the Board" | every **24 real hours** (rollover at `special.rolloverHourUtc`, default 15:00 UTC, same hour as the weekly reset) | **one zone each** (5 zones = 5 specials at once); applies **only while you stand on that zone's island** | one theme, +15 to +25% |
| **Clerk of the Week** | the mayor-lite | every **7 days** | **everywhere** | 3 small perks, +8% to +10%; **one** perk may be a drawback |

The Board (a notice board in every town, "Department of Arrivals" lore) shows both, with a countdown, the **next** rollover preview, and the last three. Chat announces at each rollover and an hour before ("Tomorrow's special: ..."). A once-in-ten **Void Hiccup special** (a rare random theme) replaces one zone special for a day with a joke name.

## 2. Hard rules (what a special may and may not do)

| Rule | Why |
|---|---|
| **Allowed:** skill XP %, double-drop % (skills' own `dd` key), Exploration XP %, movement speed % (small), fall damage %, slayer boss cost %, elite spawn %, event frequency %, pet XP % (the last four when their mods exist) | each has a live or planned hook |
| **Forbidden:** coin faucets, sell/buy price changes, **Bazaar spread**, Bazaar/AH fees, anything that unlocks a recipe or a collection tier, rarity weights of gear | R3 + the Bazaar loop: buy = base x 1.10, sell = base x 0.90 (spread 22.2%) and crafted premiums above 22.2% break it; any spread change reopens loops |
| **No stacking of the same kind:** two specials of the same kind take the **larger**, not the sum (zone XP special and Clerk XP perk on the same skill = the bigger one + half the smaller) | prevents 60% XP weeks |
| **Overall cap per skill:** specials + Clerk <= **+30%** XP, and all sources together (gear Wisdom, accessories, **prestige +20%**) <= **+60%** | SkySkills already clamps the sum (0 to 5); the design cap is ours |
| Drawback allowed in **one** Clerk perk (Hypixel-style trade-off), max -10% and never on survival stats | adds flavour, never hurts progress |
| Never repeat inside the memory window: zone special not in the last **2** days of that zone, Clerk not in the last **3** weeks | variety |
| Announced **before** it applies; a change mid-day only by an admin command (logged) | no bait |

## 3. Zone Specials (20 themes, four per zone; a day picks one per zone)

Values are +% to the named skill's XP while you are on that island, unless said otherwise. Phase = when it can ship (P1 = live hooks today, P2 = needs a mod that is not built yet).

| Zone | Name (Board voice) | Effect | Phase |
|---|---|---|---|
| **1 Emerald Wilds** | Harvest Festival | Farming XP +20%, farming double drops +5% | P1 |
| | Timber Sale | Foraging XP +20%, foraging double drops +5% | P1 |
| | Open Day | Exploration XP x1.5 (first visit of outposts and biomes) | P1 |
| | Welcome Week | class XP +15% until class level 20 | P2 (class XP key UNVERIFIED) |
| **2 Howling Sands** | Dust Season | Mining XP +20%, mining double drops +5% | P1 |
| | Caravan Day | Exploration XP x1.5, movement speed +5% on the island | P1 |
| | Scarak Season | event frequency x1.5, event chest score +10% | P2 |
| | Sand Surfing | fall damage -30% on the island | P1 |
| **3 Whisperfrost** | Deep Freeze | Mining XP +15%, Foraging XP +15% | P1 |
| | Fireside Week | Cooking XP +25% (campfires and the table) | P1 |
| | Snow Day | movement speed +5%, fall damage -30% | P1 |
| | Yeti Watch | elite spawn chance x1.3 (more elite loot) | P2 |
| **4 Devastated Lands** | Forge Week | Smithing XP +25% (furnaces) | P1 |
| | Ember Surge | event frequency x1.5, elite spawn x1.2 | P2 |
| | Cinder Day | all gathering XP +10% | P1 |
| | Hunter's Notice | slayer boss spawn cost -20% | P2 |
| **5 Dinosaur caves** | Fossil Fever | Mining XP +20% and mining double drops +5% | P1 |
| | Rex Alert | slayer boss spawn cost -20% and elite spawn x1.3 | P2 |
| | Egg Hunt | pet XP +25%, egg chance on the zone's events x1.2 | P2 |
| | Deep Dig | Exploration XP x1.5 (cave layer first visits) | P1 |
| **Void Hiccup** (any zone, 1 in 10 days) | Hiccup: **Double Trouble** | a random zone special of its zone at **x2** value, and a random drawback of -5% movement speed | P1 |

All values stay inside the section 2 caps (a +20% special plus a +10% Clerk perk = +20% + half of 10% = +25% on a skill, under +30%).

## 4. Clerks of the Week (8 clerks, 3 perks each)

Names are jokes in the Department voice (placeholders). A clerk is picked in a seeded random order with the memory window above. "Drawback" appears on one clerk only.

| Clerk | Perk 1 | Perk 2 | Perk 3 (or drawback) |
|---|---|---|---|
| **Clerk Marbury - "Efficiency Review"** | all skill XP +8% | Exploration XP +25% | farming / foraging / mining double drops +2% |
| **Clerk Voss - "Safety Inspection"** | fall damage -25% | movement speed +4% | Stamina regen +10% (the accessory top-up mechanic) |
| **Clerk Penwright - "Training Day"** | class XP +10% (P2) | ability use progress x1.2 (P2) | Mana regen +10% |
| **Clerk Okonkwo - "Staff Picnic"** | Cooking XP +20% | campfire cooking cost -20% (sacks use) | food gives Stamina regen +10% (P2, UNVERIFIED food hooks) |
| **Clerk Lindqvist - "Audit Week"** | slayer boss cost -15% (P2) | elite spawn x1.15 (P2) | Exploration XP +25% |
| **Clerk Abara - "Casual Friday"** | pet XP +20% (P2) | movement speed +3% | Smithing XP +10% |
| **Clerk Harrow - "Rush Season"** | all gathering XP +12% | **Drawback:** Stamina max -10% | farming double drops +3% |
| **Clerk Dumont - "Open Door Policy"** | Exploration XP x1.5 | warp cooldown -50% (outposts) | fall damage -15% |

Rule: **a perk that does nothing yet must not be listed** (Skyy 2026-09-30), so a clerk (or zone special) is only drawn when **all** of its perks work. Phase 1 can run **Marbury, Voss, Harrow** (and Dumont once outpost warps exist); the other clerks wait for their mods. If fewer than 3 clerks are ready, the rotation simply repeats among those (the memory window shrinks to fit).

## 5. How it works (technical, for the local session)

| Piece | Rule |
|---|---|
| **State** | `specials.properties` in the mod's data folder: `cycle=<n>`, the chosen ids for the day and week, the memory window, and the next rollover time. Chosen from a **seed = cycle number** so a restart never reshuffles; the stored ids win if the catalogue is edited |
| **Clock** | real UTC time (`now / cycleSeconds`); no catch-up after an outage (a missed day is skipped) |
| **Zone resolver** | `zone:fn:of` Function(uuid) -> "1".."5" from the player's position and the island geometry (`Zone-Islands-Layout.md`); checked on a 2 s tick, published per player when it changes |
| **Applying XP and drops** | publish into the existing `skill:bonus:<uuid>` map under source `special` (keys `xp.<skill>`, `dd.<skill>`); SkySkills clamps the sum. **No SkySkills change** if the key already exists (UNVERIFIED) |
| **Speed / fall** | the movement protocol, one new source name `specials` (Booster spec 5.4: fields `pct`, `jump`, `fallDamage`) |
| **Other effects (P2)** | read keys `special:val:<kind>:<zone>` Double (slayer cost, elite chance, event frequency, pet XP) by the mod that owns the effect. Plain `java.lang` types |
| **Board page** | SkyyMenu tab "The Board": today's five specials, the clerk and perks, countdown, "next" preview. Vanilla look. Action-bar hint on entering a zone: `Today: Harvest Festival +20% Farming XP`. No hover info |
| **Admin** | `/special show`, `/special set <zone> <id>`, `/special clerk <id>`, `/special reroll`, `/special off`: every change is written to `config-changes.log` |
| **Per profile?** | no; specials are server-wide. Each effect applies per player |

## 6. Exploit and balance check

| Risk | Handling |
|---|---|
| Players wait for their skill's day | mild: the XP is +20%, not x2; with 4 themes a skill gets a day about once a week |
| Zone hopping to chase buffs | applies only on that island, and islands need the guardian flags (anti-skip), so hopping costs real travel |
| AFK pools | none of the P1 effects add resources by themselves |
| Stacking with prestige and Wisdom | capped in section 2 |
| A day change in the middle of a long session | the page shows a countdown; the bonus changes at the rollover; no refund |
| Time zones | everything in UTC; the page shows "ends in 2h 10m" |
| Empty server | the system still rotates (no player = no cost) |

## 7. Optional later: the election

Phase 3, only if the server has enough players: each profile gets **1 vote per week** among **3 candidate clerks** (the next three the rotation would choose); the most votes wins; **ties and fewer than 3 votes = the rotation decides**; voting is free (no coins). A runner-up clerk gives its Perk 3 as the Minister perk. This is the one place that touches saved player data (a vote ledger per profile), so it is a full round.

## 8. Server Setup rows

`special.enabled`, `special.rolloverHourUtc` 15, `special.zoneCycleSeconds` 86400, `special.clerkCycleSeconds` 604800, `special.announceBeforeSeconds` 3600, `special.xpCapPercent` 30, `special.hiccupChancePercent` 10, `special.zoneMemoryDays` 2, `special.clerkMemoryWeeks` 3, one row per special and clerk (id, on/off, value), `special.drawbacksEnabled` on.

## 9. Build order

| # | Piece | Needs |
|---|---|---|
| 1 | State, clock, Board page, announcements (no effects yet) | SkyyMenu tab, config kit |
| 2 | P1 effects: skill XP, double drops, Exploration XP, speed, fall | `skill:bonus` (UNVERIFIED), movement protocol (exists) |
| 3 | Zone resolver | island geometry in world gen |
| 4 | P2 effects as their mods ship (slayers, elites, events, pets, class XP) | each mod |
| 5 | Election (optional) | profiles, enough players |

## For the local session (UNVERIFIED)

- That `skill:bonus:<uuid>` already exists in the live SkySkills and accepts a second source name; the exact key for **class** XP and **Cooking/Smithing** XP.
- That the movement protocol accepts a third source and that fall damage still routes through SkySkills.
- The island geometry used by `zone:fn:of` (depends on world gen).
- Whether the SkyyMenu tab system takes a new tab from another mod.
- Mining double drops: whether `perk.doubleDropMax` leaves room for a temporary +5% on top of the skill's own.
- Exact mayor perk lists of Hypixel (memory only).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Specials only on the zone's island, or global? | only on the island |
| 2 | Daily zone specials + weekly Clerk (two layers), or only one? | both |
| 3 | A server vote for the Clerk later, or a pure rotation? | rotation now, vote optional later |
| 4 | Keep the single Clerk with a drawback (Rush Season)? | yes |
| 5 | Rollover time: 15:00 UTC (the usage reset hour) or another? | 15:00 UTC |
