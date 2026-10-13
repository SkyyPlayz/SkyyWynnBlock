# Rebirth research and recommended design (Nexus of the Void)

Cloud draft, 2026-10-13. Paper design; nothing built. Every number is a placeholder that goes into Server Setup (PROJECT-RULES section 4).

## 0. Decisions followed (nothing re-decided)

| Decision | Source |
|---|---|
| Rebirth resets skill + class levels and coins + bank; keeps island, shard upgrades, gear, collection knowledge; each rebirth raises the max and gives a stacking stat boost, points shop, cosmetics / title, new content | `docs/answered/skills.md` lines 114-116 |
| ONE rebirth menu, one tree radiating from the black hole; rebirth when CLASS is max (even if Mining is not); points are SEPARATE per skill; XP keeps counting past max; costs start cheap and scale fast (like dust); no unlock points - about 8 levels in a row opens the next row | `docs/answered/skills.md` line 117 |
| The Nexus of the Void is the controller: hover = requirements + what you get; click; then confirm | `docs/answered/skills.md` line 118 |
| Fishing gets its own skill, tree and rebirth branch | `docs/answered/skills.md` line 120 |
| Bank keeps all money at rebirth; you get a PERMANENT better interest rate scaled by the balance at reset (account-wide bracket design 2 / 1 / 0.5 %) | `docs/answered/economy.md` line 101 |
| All skills rebirth TOGETHER; lifelong tools keep rarity + stats, go back to Crude / level 0, gain a rebirth modifier upgraded in that skill branch; multitool unlocks after rebirth 1; applies to hoe, sickle, rod too, shovel is excluded | `docs/answered/gear.md` lines 168-172 |
| Gathering armor sets level with their skill and keep rarity + rebirth rules | `docs/answered/gear.md` line 175 |
| Menu hover tooltips work and are on by default | `docs/answered/ui.md` lines 13, 28 |
| Earlier cloud draft `research/cloud/Prestige-Spec.md` ("go home anyway", Tab-based, 2%/prestige XP) is an OLDER design; the Nexus rebirth of 2026-10-12 wins. Parts worth keeping are listed in section 5 | newest answered lines win |

## 1. Research notes (what I could and could not verify)

Web access in this environment was patchy: wiki sites (fandom, wiki.gg) refused connections, only search snippets came back. Each row says how sure I am.
"Search" = a search result snippet (link below); "memory" = my own knowledge of the game, NOT checked online today - verify before quoting.

**Shell Diver.** I could not find a Roblox game with that name. Closest hits: **Shelldiver** on Steam (a turtle catches jellyfish with a bubble gun, sells them, buys sub / tool upgrades, "large branching skill tree" from oxygen tank to shop size, about 98 % positive reviews; praise = relaxed pacing and art, complaint = late-game balance, short playtime). Search found NO prestige / rebirth in it. So Skyy's "Shell Diver upgrade tree" reference is most likely the tree LOOK (a big branching map you buy into), not a rebirth system. The screenshot `research/refs/rebirth-radiating-tree.webp` is only on the local PC. Question 1 asks Skyy for the exact game. Sources: [Steam page](https://store.steampowered.com/app/3862670/Shelldiver/), [review summary](https://vaporlens.app/app/3862670/shelldiver).

| Game | What resets / what stays | Point formula | Tree / shop | Prestige button | Pacing | Loved / hated |
|---|---|---|---|---|---|---|
| **Cookie Clicker** (Ascension) | Resets cookies, buildings, normal upgrades. Stays: heavenly upgrades, achievements, prestige level, (with permaslots) chosen upgrades. | Search: prestige level = floor(cbrt(all-time cookies / 1e12)); chips gained = levels gained beyond current. Each level = +1 % cookie production (search; some sites say 5 %, I trust 1 %). So level n needs about n^3 trillion cookies. | Heavenly upgrade tree: pick-and-buy nodes with prerequisites, costs in chips rise steeply; "Permanent upgrade slot I-V" chain lets a chosen upgrade survive resets. | An Ascend button appears once you pass the first threshold; the Legacy screen shows chips you WOULD earn before you commit (search); you then spend chips on the tree and press Reincarnate. Memory: a confirm popup. | Search: the common advice is first ascend around prestige 440 (about 85 quadrillion) to buy the first batch (Legacy, dragon, heavenly cookies, Permanent slot I); later ones at 3k and 36k. An active player may ascend at about 20 and does fine. | Love: every reset visibly faster, the tree gives goals. Hate: timing is a maths puzzle - new players ascend too early/late (guides exist just for "when to ascend"). |
| **Antimatter Dimensions** (Infinity, Eternity, Reality layers) | Each layer resets everything below it; upgrades of the layer stay (Eternity keeps achievements, Time Studies, milestones...). | Search: IP about 10^(log10(antimatter)/308 - 0.75) at base; first Infinity at 1.79e308 antimatter; Eternity needs about 1e280 IP and appears then. | Layers add NEW systems (dimensions, challenges, studies) each time. | The button appears only once reachable and shows the gain. | Layers take minutes, then hours, then days. | Love: each layer is a surprise new game. Hate (memory, community): very long late layers, wiki-dependence. |
| **Clicker Heroes** (Ascension, Transcendence) | Ascension resets heroes and zones but KEEPS Hero Souls and Ancients; Transcendence is the deep reset (wipes heroes, ancients, souls, gilds; keeps rubies, achievements, Outsiders bought with Ancient Souls). | Search: 1 Hero Soul per 2,000 total hero levels at ascend, +10 % damage per soul. Ancient Souls: sources disagree (floor(5 log10 souls) vs a slower curve) - unverified. | Ancients (cost grows by level, some capped) and Outsiders (a second shop for the deep layer). | Ascend lives in a menu; confirm popup (memory). | Search: first transcend about zone 300, then 3-4 ascensions per transcension. | Love: soft reset + hard reset gives short and long goals. Hate (memory): three currencies are confusing, active play vs idle play fights. |
| **AdVenture Capitalist** (Angel Investors) | Resets businesses and cash. Stays: angels (each gives a bonus), lifetime earnings keep counting. | Search: thresholds of lifetime earnings for 1 / 2 / 3 angels were about 44.4 billion, 177.8 billion, 400 billion, i.e. angels about sqrt(lifetime / 44.4B) (ratio 1 : 4 : 9). Memory: +2 % income per angel. Only unsacrificed angels give the bonus. | No tree: one list of "Angel upgrades" bought with angels, and "Sacrifice" to trade angels for a lump of investments. | A "Claim angels" button with a number on it, shown when it exceeds the angels you already have (memory). | Very fast: first claim within the first hour. | Love: dead simple, number goes up. Hate: shallow, ads / paywall in the mobile version. |
| **Realm Grinder** (Abdication, Reincarnation, Ascension) | Three soft layers: abdication (any time, changes faction), reincarnation (needs a high threshold), ascension (needs reincarnations). Each keeps more than the one before it. | Exact formulas not found. Search: reincarnation unlocks at high total faction coins (one guide says 1e60). | Spells / research / "Reincarnation upgrades" and faction picks: the choice of faction IS the build. | Layers unlock when the earlier one is done; an abdication can be done at any time even when pointless. | Hours to first abdication; days to ascension. | Love: build variety from faction + mixes. Hate (memory): overwhelming number of systems. |
| **Idle Slayer** (Ascension, Ultra Ascension) | Search: Ascension resets progress and pays Slayer Points spent in the Ascension Tree (+ permanent coin bonus); Ultra Ascension resets that tree too and pays Ultra points (Stones of Time). Divinity tab, Minions, Bag are lost/disabled until re-bought; DP and achievements stay. | Formula not found. | Ascension Tree (skill tree of nodes); an "Astral" tag marks upgrades that survive an Ultra reset. | Memory: a preview of points before you confirm. | Memory: first ascension after a few hours. | Search: Steam threads show players fear losing tabs; the "you lose X" list is a common complaint, so it must be listed clearly. |
| **NGU Idle** (Rebirth) | Resets almost everything; stays: Adventure Points, perks, NGU, achievements. | Search: gain is a product of factors including the boss reached, a rebirth-time bonus at 3, 4, 5, 7, 10, 12, 15, 30, 60 minutes, and kill counts. Exact formula not found. | Huge screens of upgrades. | Not found. | Rebirths every few minutes to hours late. | Hate (memory): menu overload for new players. |

Sources: [Cookie Clicker guide](https://ponderworthy.com/when-should-you-ascend-in-cookie-clicker-the-math-behind-your-first-prestige-zln), [Cookie Clicker Steam thread](https://steamcommunity.com/app/1454400/discussions/0/2963922521575894062/?l=italian), [permaslots guide](https://gamepretty.com/cookie-clicker-ascension-and-permaslots-guide/), [Antimatter Dimensions Eternity](https://antimatterdimensions.wiki.gg/wiki/Eternity), [Clicker Heroes blog: transcend](https://blog.clickerheroes.com/best-time-to-transcend-when-to-hit-zone-300-and-beyond/), [hero souls guide](https://blog.clickerheroes.com/clicker-heroes-hero-souls-complete-guide-to-power-up/), [AdCap thresholds](https://steamcommunity.com/app/346900/discussions/0/364039531219683031), [Realm Grinder wiki](https://realm-grinder.fandom.com/wiki/Soft_Resets), [Idle Slayer Steam thread](https://steamcommunity.com/app/1353300/discussions/0/3110266679785950552), [NGU Idle wiki](https://ngu-idle.fandom.com/wiki/Number).

### What the pattern tells us

| Pattern across the games | Use for SkyWynn |
|---|---|
| Gain is a root of progress (cube root in Cookie Clicker, square root in AdCap, log in Eternity): early overshoot pays, late overshoot pays less | Points use a square root of "XP vs XP to cap" so Skyy's "stack extra XP past max" is rewarded without runaway |
| The button shows the gain BEFORE you commit | The Nexus hover is exactly this; also show "next point at X XP" |
| The first reset is 1-3 hours (idle games) to many hours; each next one is faster | RPG pace: first rebirth about 25-40 h of play, each next about 60 % of the last (kept gear, shards, island) |
| Players hate unclear loss lists (Idle Slayer) and unclear timing (Cookie Clicker) | A "Resets / Stays" two-column list in the preview, and a "worth it?" verdict line |
| Players love a tree to stare at and a layer that adds new things | The radiating tree plus new content per rebirth (higher caps, multitool) |
| Too many currencies confuse (Clicker Heroes, NGU) | Per-skill points are Skyy's choice; show them as ONE row of small counters, not many screens |

## 2. Recommended design

### 2.1 What resets and what stays

| Resets | Stays |
|---|---|
| Class level + XP, every skill level + XP (the run XP counter is paid out as points first) | Island, shard upgrades, collection knowledge (counts AND recipes - Skyy: "you retain the knowledge") |
| Coins + bank balance (moved into the bank deal, 2.6) | All items: gear, bags, vault, accessories (level gate makes old gear idle) |
| Active quests / zone flags are NOT reset (Skyy said levels only) [default] | Lifelong tools: rarity + stats stay, tier back to Crude, level 0, + rebirth modifier |
| Gathering armor tier back to base, level follows skill | Pets, cosmetics, titles, Pocket Shards, rebirth count, all unspent and spent tree points |
| Tab / Bazaar / AH open orders must be empty first (checklist blocks) | Account-wide bank interest bonus |

### 2.2 When you can rebirth

Class level is at the current cap (50 at rebirth 0, raising by 10 per rebirth, section 2.5). Not in combat, no open Bazaar / AH orders, mailbox empty (warned). No cooldown needed because the cap is the gate.

### 2.3 Points formula (python3 below)

For each branch s (class + each skill): `points_s = floor(B_s * sqrt(r_s))`, where `r_s = XP earned this run in s / XP needed to reach that skill's current cap`.

- Class: B = 12; skills: B = 8. Class is always r >= 1 (that is the requirement).
- A skill with r under 0.25 pays 0 (no points for a skill you ignored), so the preview can say "Fishing: 0 (needs 25 % of cap XP)".
- Because the cap rises each rebirth, r stays comparable; the bar to rebirth stays honest.

Output (python3, `math.floor(B * sqrt(r))`):

| r (XP vs cap) | 0.25 | 0.5 | 1 | 1.5 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|---|---|---|
| Class points (B 12) | 6 | 8 | 12 | 14 | 16 | 20 | 26 | 37 |
| Skill points (B 8) | 4 | 5 | 8 | 9 | 11 | 13 | 17 | 25 |

Why sqrt: doubling extra XP gives only 41 % more points, so farming a skill 10x longer gives 3.2x points, like AdCap. Skyy's "stack a ton of extra XP" pays but never breaks the tree.

### 2.4 Tree layout and costs

- **Hub:** the Nexus (black hole), centre. **Arms** radiate like a star: Class, Mining, Foraging, Farming, Fishing, plus Alchemy, Smithing, Cooking [default 8 arms; Acrobatics / Combat out until Skyy says].
- **Per arm:** 5 rows outward, 3 / 3 / 2 / 2 / 1 nodes = 11 nodes, each with 5 levels (55 levels). The last node of each arm is a "keystone" with 1 level, a big effect. Total 88 nodes plus the Nexus, about 440 levels.
- **Row unlock:** 8 total levels in the previous row opens the next (Skyy). No unlock points.
- **Cost of the k-th level bought in an arm (k from 0):** `ceil(1.08^k)` - the arm's price rises as you buy more. Cheap start, steeper later, like dust.

| Levels bought in one arm | 8 | 16 | 24 | 32 | 40 | 50 |
|---|---|---|---|---|---|---|
| Total points | 15 | 38 | 78 | 149 | 277 | 597 |

- Rebirth 1 pays about 12 class points + 8 per skill arm, so one rebirth opens row 2 of most arms (8 levels = 15 points needs the extra-XP overshoot or two rebirths). After 10 rebirths a normal player has about 120 class / 80 skill points, i.e. 24-30 levels per arm: a deep but never finished tree. Full arms are for people who overshoot XP.
- **Effects per arm (examples, NOT numbers):** Class arm = ability point refunds, class XP, class stat boosts; Mining arm = Mining XP, dust rate, drop chance, the pickaxe REBIRTH MODIFIER nodes; Foraging = same for the axe; Farming = hoe / sickle modifier, crop yield; Fishing = rod modifier, catch speed; Alchemy / Cooking / Smithing = time savers (cook speed, brew speed, upgrade cost). Rule: time savers and small stat boosts, no coin faucets, no collection skips.
- **Placement:** nodes sit on glowing lines like Skyy's screenshot; unlocked rows glow, locked rows are dim.

### 2.5 Raised caps and the stacking boost (each rebirth)

| Rebirth # | Class cap | Skill cap | Stacking stat boost | New content |
|---|---|---|---|---|
| 0 | 50 | current | 0 | - |
| 1 | 60 | +10 | +3 % | Multitool unlocks, title "Void-Touched I" |
| 2-10 | +10 each | +10 each | +3 % each (cap +30 %) | more collection ranks, cosmetics every 3 |

Defaults: max 10 rebirths at first (class cap 150); raise later. Stat boost is small: it is only a thumb on the scale since the tree is the main reward.

### 2.6 Rebirth bank (Skyy economy line)

Bank takes coins + balance at reset. Permanent interest bonus = `min(1.0, 0.25 * log10(1 + balance / 100,000))` in percent points added to each bracket rate (account-wide; the bracket stays 2 / 1 / 0.5 with the bonus on top, capped).

| Balance at reset | 100K | 1M | 10M | 100M | 1B |
|---|---|---|---|---|---|
| Bonus (percent points) | 0.075 | 0.26 | 0.50 | 0.75 | 1.00 (cap) |

It stacks over rebirths up to a total cap [default 3 percentage points]. This keeps rich players happy without breaking the bracket design. The numbers need a check against `research/cloud/Bank-Tab-Calibration.md` by the local session.

### 2.7 The button / preview UX

| State | What the player sees |
|---|---|
| Not at cap | The black hole is dim, slow swirl. Hover: "The Nexus sleeps. Reach Class level 50 (you are 37)." A checklist with ticks / crosses (class cap, no open orders, not in combat). |
| At cap | The hole pulses and glows. Hover: the preview below. |
| Click | A confirm panel (not a vanilla yes/no only): the same preview, a two-column list "Resets / Stays", and a **Rebirth** and **Not yet** button. Hold-style safety: the Rebirth button enables after a 3-second count. |
| Done | Short scene: screen dims, "The void imprints your soul", points counters tick up, title card "Rebirth N". Lifelong tools show their new rebirth modifier. |

Hover preview ("You would gain") shows: points per arm (Class 14, Mining 9, Foraging 8, Farming 0 [needs 25 %]...), the stat boost, new caps, the bank deal ("Bank deal: +0.50 % interest"), what resets, what stays, and "Next point in Mining at 12,300 XP" so the player can decide to keep grinding. One line says "Worth it?": green when every arm is at least 1.0 r or you have 100 % points, otherwise grey ("Mining could give 4 more points if you wait").

Layout notes for the local session: the radiating tree needs pan / zoom (UNVERIFIED in the Hytale UI, see Rebirth-Ideas research list `research/Rebirth-Ideas.md`). Fallback: one centre page with the Nexus and arms as 8 sector tiles; click a sector to open that arm as a normal node grid.

### 2.8 Pacing target

| Milestone | Target |
|---|---|
| First rebirth | about 25-40 hours of play (class 50) |
| Rebirth 2 | about 60 % of that, because gear, island, shards and tree stay |
| Each later rebirth | about 60 % of the last but the cap is 10 levels higher, so about 12-25 h |
| First sight of a "worth it" arm after rebirth 1 | within 2 h of the new run |

All times are guesses to check against SkyySkills XP curves (`docs/answered/skills.md`); the local session should measure.

### 2.9 How it fits profiles, skills, collections

- **Profiles:** all rebirth data is per profile (`tools/PROFILES-CONTRACT.md`): rebirth count, points per arm, bought levels, bank bonus. A second profile starts at 0 (Skyy's vault idea: good starter gear for other profiles).
- **Skills:** SkyySkills keeps counting XP past max (Skyy). New fields: run XP per skill. A bridge function `skill:fn:rebirth` (plain types) resets levels and returns run XP so SkyyTrees-style nodes read the arm effects through the existing `skill:bonus` map (source `rebirth`).
- **Collections:** counts stay (knowledge), so nothing to reset; new ranks open at higher rebirths.
- **Safe-reset rules to copy from the older draft `research/cloud/Prestige-Spec.md`:** journal marker (`rebirth.pending`), idempotent hooks, History snapshot first, profile epoch republish, no item deleted, order of hooks (quests, slayers, class, skills, coins last).
- Cross-mod calls only through `skyy.bridge` (PROJECT-RULES 4); full round (saved data, coins, several mods).

### 2.10 Risks and exploits

| Risk | Handling |
|---|---|
| Alt-farming of rebirth rewards | points and boosts are per profile; no coin faucets in the tree |
| Crash mid-reset | journal marker and idempotent hooks |
| Points farmed by AFK XP | sqrt formula; skill r under 0.25 pays 0 |
| Bank bonus abuse (deposit-borrow before rebirth) | balance measured at the moment of the reset; capped |
| Players fear loss | the "Resets / Stays" list and the snapshot ("Undo within X" is not offered; items never deleted) |

## 3. Python used

```
import math
for r in [0.25,0.5,1,1.5,2,3,5,10]:
    print(r, math.floor(12*r**0.5), math.floor(8*r**0.5))
# cost to buy n levels in an arm
tot=0
for k in range(50): tot+=math.ceil(1.08**k)   # n=8 -> 15, 16 -> 38, 50 -> 597
# bank bonus
min(1.0, 0.25*math.log10(1+bal/1e5))
```

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Which game is "Shell Diver"? I found only Steam Shelldiver (no rebirth). Do you mean its upgrade-tree look, or a Roblox game with a different name? | Tree look only |
| 2 | Which skills get an arm: Class, Mining, Foraging, Farming, Fishing, Alchemy, Smithing, Cooking? Acrobatics / combat? | These 8 |
| 3 | Class cap: 50, then +10 per rebirth, max 10 rebirths? | Yes |
| 4 | Points = square-root of extra XP (more XP always helps, but slower)? | Yes |
| 5 | Do quest / zone / boss progress reset, or only levels + coins? | Only levels + coins |
| 6 | Stacking stat boost +3 % per rebirth (cap +30 %): OK? | Yes |
| 7 | Bank bonus: cap 1 percentage point per rebirth, 3 total? | Yes |
| 8 | Confirm step: 3-second count on the Rebirth button, plus a resets/stays list? | Yes |
| 9 | Do skills with less than 25 % of cap XP give 0 points? | Yes |
| 10 | Keep the older "go home anyway" Tab prestige as well, or replace it with the Nexus rebirth? | Replace (keep the ticket line "Welcome back! Your ticket number is #4,000,000,002." as the rebirth 1 title card) |

## For the local session

- UNVERIFIED: whether the Hytale UI can draw a pan / zoom radiating tree with lines (probe with the sector-tile fallback ready).
- UNVERIFIED: SkyySkills XP curves and the real "XP to cap" per skill; measure pacing (2.8) and the point output (2.3) with real numbers.
- UNVERIFIED: whether SkyySkills already tracks XP past max level and whether `skill:bonus` accepts a `rebirth` source.
- Check the bank-rate maths against `research/cloud/Bank-Tab-Calibration.md` and `research/cloud/Tab-Economy.md`.
- Record Skyy's answers with `python tools/qa_append.py`, then copy the agreed parts into a spec (a new rebirth spec file is a local-session task).
- The scripts file `research/cloud/Tab-Prestige-Scripts.md` was written for the older Tab prestige; its prestige dialogue needs a rewrite if Q10 says replace.
- Web facts marked "memory" in section 1 were not re-checked online; formulas marked search come from snippets of community sites, not from game source.
