# Balance pass P3 - XP: one curve, XP per action, skills trail class (BUILD-READY spec, 2026-10-20)

Phase P3 of research/Balance-Pass-Spec.md section 8 ("XP: one curve shape for class + skills, XP per action, skills trail class 3-5").
Mods: SkyySkills (curve, gathering / alchemy / smithing / acrobatics XP, catch-up, past-life boost, migration), SkyyCooking (dish XP),
SkyyExploration (zone factors), SkyyCollections (tier XP), SkyyFishing (fishing light). Yardstick: research/balance/targets.md +
tools/balance_model.py (P1). Today's numbers: research/balance/xp.md, gathering.md (P0). Skyy's goals: docs/answered/skills.md 185-193.
Where answers go: docs/answered/skills.md (via `python tools/qa_append.py`); this file holds the plan. Index: INDEX.md (research/).

Skyy 2026-10-18: "instead of starting fast and slowing, lets try to balance the xp gain, and how much more each level costs to make all skills,
and your class level pretty close to the same rate." + "skills lag a bit. about 3-5 levels." Skyy 2026-10-20: "keep going down the list. dont
stop until the entire list is done" + "if you have any doubt, do research to get good data to base your default on".

## 0. Summary

1. ONE curve for the class and every skill: `need(L) = R(1100 x f(L) x s(L))`, f = the kill XP level factor SkyySkills already uses.
2. ONE tier factor for every XP source: `XP per action = base x F(T)`, F(T) = f(level where tier T starts). Ores, logs, crops, dishes,
   brews, bars and fish all rise with tier; kill XP already does this by mob level. Nothing else is needed to make the levels steady.
3. Skills trail the class by about 4 (the bases are tuned so a balanced player is 2-5 behind). A soft **catch-up** (+10 % skill XP per level
   beyond 5 behind the class, at most +100 %) keeps fighting-heavy players within about 7.
4. Rebirth: a **past-life XP boost** on levels below the last run's cap, x1.2 / 1.45 / 1.8 / 2.25 / 2.8 for rebirth 1-5. New levels keep the
   first-time pace. Scaled curves would rush Zones 4-5 (section 5).
5. Migration: **keep levels**. Saved XP is rewritten once to the same level and the same progress on the new curve (section 6).
6. Model: class Lv 20 at 9.1 h (target 10; today 2.8 h), Lv 40 at 20.0 h (target 20), Lv 50 at 25.6 h (target 25). Every activity hits its
   XP/h target in every zone (was up to 1/14,000 off). The longest stretch without a level-up is 1.98 h, all of it in the cap stretch (Q1).

## 1. Research: how others shape level curves (W = checked on the web 2026-10-20, K = my knowledge, not checked)

| Game | Curve (XP to level) | XP per action | What it means for pace |
|---|---|---|---|
| RuneScape (OSRS) | `1/4 x sum(l + 300 x 2^(l/7))`, about +10 % per level; Lv 92 is about half of Lv 99 (W: oldschool.runescape.wiki/w/Experience) | rises as better methods unlock, far slower than the curve | the textbook "crawl": late levels take days. Fine for a 2000 h game, wrong for our 45 h run |
| Hypixel SkyBlock | our current `levels` list (Lv 50 = 55.2 M XP) (K + research/balance/xp.md:29) | small per block; the speed comes from Wisdom, pets, minions, enchanted gear, multipliers | copying the table without their boosts gives P1's 1/700-1/15,000 gap |
| Wynncraft | Lv 1 150, Lv 10 1,850, Lv 20 5,730, Lv 50 145,000, Lv 80 2.33 M, Lv 100 14.4 M (W: wynncraft.wiki.gg/wiki/Combat_level) | mob XP rises with level; -3 % per level of gap (W, same page) | about x100,000 from Lv 1 to 100, partly paid back by mob XP growth; late levels are long |
| WoW Classic | `(8 x CL + Diff) x (45 + 5 x CL) x RF`; ~17,000 same-level kills to 60, ~76 h at 16 s a kill (W: warcraft.wiki.gg/wiki/Experience_to_level) | mob XP = 45 + 5 x level | kills per level about 8 x level, so the time per level rises in a straight line. Rested XP and quests smooth it |
| Borderlands 1-3 | `60 x L^2.8 - 60` total (K; checked against the Pre-Sequel table: Lv 10 37,798, Lv 20 263,595, gamerfuzion.com guide) | enemy XP scales with enemy level | time per level stays about flat across the campaign (K) |
| GDC 2011 (KingsIsle RPG maths) | flat vs exponential curves; "the numbers should stay consistent" through levelling (W: engadget.com 2011-10-12) | with a flat curve, cap XP from far higher-level mobs | we already have the gap rows (combat.gap.*) |

**What "steady, no fast-start-then-crawl" means in numbers (the rule this spec uses):** the hours per level should be about the same within a
zone and rise by at most ~1.5x from Zone 1 to Zone 5 (Borderlands-like), after a short quick start (WoW-like first levels in minutes).
The way to get there is to scale XP per action with tier at the same rate as the curve. A big table with small, flat XP per action (Hypixel,
RuneScape) is what makes the crawl. Ours (base pace, class, from the model): Lv 1 8 min, Lv 3 23 min, Lv 5-60 31-34 min, Lv 70 40 min,
Lv 80 46 min, Lv 90 52 min, Lv 99 57 min. Today: 1 min at Lv 1, 61 min at Lv 50, 146 min at Lv 99 (class), and hours to days for Foraging /
Cooking / Alchemy. The slowest level is still under the "1 h without a level-up" rule (A:187 Q2), and rebirth speed-ups only shorten it.

## 2. The one curve

```
need(L) = XP for level L (entry L of the list) = R( 1100 x f(L) x s(L) )
f(L)    = 1 + 0.13 (L-1) + 0.004 (L-1)^2          = the kill XP level factor (combat.levelCurve: 1 / 4.91 / 16.97 / 53.07 at Lv 1 / 20 / 50 / 100)
s(L)    = L/4 for L <= 4 (quick start), 1 for 5-60, 1 + 0.018 (L-60) above 60 (Zones 4-5: 12 h / 15 h per zone, A:187 Q1)
R(x)    = round to 5 below 1,000, to 50 below 10,000, to 100 above
```
The same list goes to the class skills and to every skill (Mining, Foraging, Farming, Fishing, Alchemy, Smithing, Cooking, Acrobatics,
Exploration; Beastmastery when it is built). `levels.scale` (Server Setup, 100 %) stretches it for everyone. Totals (game convention, below): Lv 20 = 58,150,
Lv 50 = 406,200, Lv 100 = 2,944,700 (today, model counting: class 18,540 / 436,590 / 6.37 M; Mining 4,850 / 67,265 / 518,290; general list 322,425 /
50.2 M / 602.7 M).

`levels=` (100 entries, the build asserts this exact list):
`275,625,1050,1550,1750,1900,2100,2300,2550,2750,2950,3200,3450,3700,3950,4250,4500,4800,5100,5400,5700,6050,6400,6700,7050,7400,7800,8150,8550,8950,9350,9750,10200,10600,11000,11500,12000,12400,12900,13400,13900,14400,14900,15400,15900,16400,17000,17500,18100,18700,19200,19800,20400,21000,21700,22300,22900,23500,24200,24900,26000,27100,28300,29600,30800,32100,33400,34800,36200,37700,39100,40700,42200,43800,45400,47100,48800,50600,52400,54200,56100,58000,60000,62000,64000,66100,68300,70500,72700,75000,77300,79700,82100,84600,87100,89600,92300,94900,97600,100400`

| Lv | XP for it | Total XP | Lv | XP for it | Total XP | Lv | XP for it | Total XP | Lv | XP for it | Total XP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 275 | 275 | 26 | 7,400 | 97,450 | 51 | 19,200 | 425,400 | 76 | 47,100 | 1,200,400 |
| 2 | 625 | 900 | 27 | 7,800 | 105,250 | 52 | 19,800 | 445,200 | 77 | 48,800 | 1,249,200 |
| 3 | 1,050 | 1,950 | 28 | 8,150 | 113,400 | 53 | 20,400 | 465,600 | 78 | 50,600 | 1,299,800 |
| 4 | 1,550 | 3,500 | 29 | 8,550 | 121,950 | 54 | 21,000 | 486,600 | 79 | 52,400 | 1,352,200 |
| 5 | 1,750 | 5,250 | 30 | 8,950 | 130,900 | 55 | 21,700 | 508,300 | 80 | 54,200 | 1,406,400 |
| 6 | 1,900 | 7,150 | 31 | 9,350 | 140,250 | 56 | 22,300 | 530,600 | 81 | 56,100 | 1,462,500 |
| 7 | 2,100 | 9,250 | 32 | 9,750 | 150,000 | 57 | 22,900 | 553,500 | 82 | 58,000 | 1,520,500 |
| 8 | 2,300 | 11,550 | 33 | 10,200 | 160,200 | 58 | 23,500 | 577,000 | 83 | 60,000 | 1,580,500 |
| 9 | 2,550 | 14,100 | 34 | 10,600 | 170,800 | 59 | 24,200 | 601,200 | 84 | 62,000 | 1,642,500 |
| 10 | 2,750 | 16,850 | 35 | 11,000 | 181,800 | 60 | 24,900 | 626,100 | 85 | 64,000 | 1,706,500 |
| 11 | 2,950 | 19,800 | 36 | 11,500 | 193,300 | 61 | 26,000 | 652,100 | 86 | 66,100 | 1,772,600 |
| 12 | 3,200 | 23,000 | 37 | 12,000 | 205,300 | 62 | 27,100 | 679,200 | 87 | 68,300 | 1,840,900 |
| 13 | 3,450 | 26,450 | 38 | 12,400 | 217,700 | 63 | 28,300 | 707,500 | 88 | 70,500 | 1,911,400 |
| 14 | 3,700 | 30,150 | 39 | 12,900 | 230,600 | 64 | 29,600 | 737,100 | 89 | 72,700 | 1,984,100 |
| 15 | 3,950 | 34,100 | 40 | 13,400 | 244,000 | 65 | 30,800 | 767,900 | 90 | 75,000 | 2,059,100 |
| 16 | 4,250 | 38,350 | 41 | 13,900 | 257,900 | 66 | 32,100 | 800,000 | 91 | 77,300 | 2,136,400 |
| 17 | 4,500 | 42,850 | 42 | 14,400 | 272,300 | 67 | 33,400 | 833,400 | 92 | 79,700 | 2,216,100 |
| 18 | 4,800 | 47,650 | 43 | 14,900 | 287,200 | 68 | 34,800 | 868,200 | 93 | 82,100 | 2,298,200 |
| 19 | 5,100 | 52,750 | 44 | 15,400 | 302,600 | 69 | 36,200 | 904,400 | 94 | 84,600 | 2,382,800 |
| 20 | 5,400 | 58,150 | 45 | 15,900 | 318,500 | 70 | 37,700 | 942,100 | 95 | 87,100 | 2,469,900 |
| 21 | 5,700 | 63,850 | 46 | 16,400 | 334,900 | 71 | 39,100 | 981,200 | 96 | 89,600 | 2,559,500 |
| 22 | 6,050 | 69,900 | 47 | 17,000 | 351,900 | 72 | 40,700 | 1,021,900 | 97 | 92,300 | 2,651,800 |
| 23 | 6,400 | 76,300 | 48 | 17,500 | 369,400 | 73 | 42,200 | 1,064,100 | 98 | 94,900 | 2,746,700 |
| 24 | 6,700 | 83,000 | 49 | 18,100 | 387,500 | 74 | 43,800 | 1,107,900 | 99 | 97,600 | 2,844,300 |
| 25 | 7,050 | 90,050 | 50 | 18,700 | 406,200 | 75 | 45,400 | 1,153,300 | 100 | 100,400 | 2,944,700 |

The game's convention (SkyySkills SKL_HEAD comment, checked on the Mining list: 10 entries = 955 = "Mining 10 after 955 XP"): entry k is the
XP from level k-1 to level k, so 100 entries = max level 100 and "Total XP" = the sum of the first L entries. need(L) above is entry L.
(balance_model.py starts players at Lv 1 and counts from entry 1 - one entry, ~8 min, off; the P3 builder fixes `cum()` to the game's
convention when it updates the model.)

How the slots use it: `levels.class.sameAsOthers=true` (the class skills level on `levels`, the 0.4.12 switch). The own lists
`levels.skill.Mining` and `levels.skill.Farming` are dropped (the levels.skill table mechanism stays for admins). `gather.boost.skills=`
(empty, so no early x3 boost: the quick start is in s(L)). Kept: `classSkill.xpMultiplier=3`, `combat.perHealth=0.2`, the `combat.levelCurve.*`
points, the gap rows, `farming.tierUpXpFactor=0.5`, `coinsPerLevel=100`, `multiplier=1`.

## 3. XP per action (one tier factor)

`F(T) = f(band start of tier T)` (bands: research/Level-Bands-20-Spec.md section 1; T = the tools/tier_tags.py ladder):

| T | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| band start | 1 | 8 | 15 | 20 | 28 | 35 | 40 | 48 | 55 | 60 | 68 | 75 | 80 | 88 | 95 | 100 |
| F(T) | 1.00 | 2.11 | 3.60 | 4.91 | 7.43 | 10.04 | 12.15 | 15.95 | 19.68 | 22.59 | 27.67 | 32.52 | 36.23 | 42.59 | 48.56 | 53.07 |

Every value below = base x F(T), rounded to 5 (below 1,000) or 50. The bases come from the model's tuning: a balanced player (time split
in the model's Assumptions) sits about 4 behind the class at the class cap.

### 3.1 Mining (SkyySkills `prefix.Ore_*` rows; base 50)
| Ore | Copper | Iron | Silver | Thorium | Lead | Gold | Cobalt | Chromium | Adamantite | Slag | Mithril | Titanium | Prisma | Onyxium |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T | 1 | 2 | 3* | 4 | 5 | 5* | 7 | 8 | 10 | 11 | 13 | 14 | 15* | 16 |
| XP (was) | 50 (5) | 105 (8) | 180 (10) | 245 (18) | 370 (18) | 370 (12) | 610 (15) | 800 (15) | 1150 (30) | 1400 (30) | 1800 (25) | 2150 (25) | 2450 (50) | 2650 (40) |

*Silver / Gold / Prisma are untagged, so they get the tier where they spawn (GUESS: Silver Zone 1 late, Gold Zone 2, Prisma Zone 5).
`prefix.Ore_` (an unknown ore) 50. Kept: `prefix.Rock_` / `Rubble_` 1, sand / gravel 2. `prefix.Rock_Crystal_` 8 -> 40, `prefix.Rock_Gem_` 40 -> 200 (GUESS).
Ores now rise with tier (P1: Cobalt 15 < Thorium 18 and Mithril 25 < Adamantite 30 are fixed).

### 3.2 Foraging (trunk rows `block.Wood_<x>_Trunk` + `_Trunk_Full`, one row pair per species from tier_tags LOGS; base 33)
| T | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Species | Oak, Birch | Beech, Ash, Aspen, Apple | Maple, Azure | Dry, Palm | Bottletree, Amber | Gumboab, Palo | Fir, Cedar | Spiral, Poisoned, Windwillow | Redwood, Ice | Burnt, Sadwillow | Petrified, Wisteria_Wild | Sallow, Fire | Jungle, Bamboo | Banyan, Camphor, Fig_Blue | Crystal, Stormbark |
| XP | 35 | 70 | 120 | 160 | 245 | 330 | 400 | 525 | 650 | 745 | 915 | 1050 | 1200 | 1400 | 1600 |

`suffix._Trunk` / `_Trunk_Full` (an unknown tree) 35 (was 6). Kept: leaves 1, roots 2, branches 1. Tree Feller (`fell.xpFactor` 1) pays
the same rows. **Check:** Bamboo trunks are thin, many-block stalks. If the axe-tier lock lets low tiers fell them, give Bamboo its own row at
T1 (35) - the builder checks the bamboo block count per stalk.

### 3.3 Farming (crop rows `prefix.Plant_Crop_<x>`, tier_tags CROP_LADDER; base 38)
| Crop | Wheat | Lettuce | Carrot | Corn | Cauliflower | Turnip | Pumpkin | Aubergine | Tomato | Chilli | Cotton | Rice | Potato | Onion | Mushroom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| XP (was) | 40 (4) | 80 (4) | 135 (4) | 185 (6) | 280 (6) | 380 (5) | 460 (8) | 605 (7) | 750 (6) | 860 (7) | 1050 (5) | 1250 (5) | 1400 (4) | 1600 (5) | 1850 (3) |

Herbs: Health1 / Mana1 / Stamina1 80 (T2), the 2s 280 (T5), the 3s 605 (T8). Orchard: Berry 40, Apple 80. `prefix.Plant_Crop_` 40.
Kept: Wild_Grass 1, Cactus 2. Ranching (`ranching.items`, x10, GUESS): Food_Egg 30, Wool 30, Feathers 10, Chicken / Pork / Wildmeat 20,
Beef 30, Hide_Light 10, Hide_Medium 20. `farming.tierUpXpFactor` 0.5 stays (Skyy's tool-tier rule). Totem / idle harvest XP: P6.

### 3.4 Kills (unchanged: already f(mob level)); Normal, Lv 1 health 60 (model GUESS), x3 class multiplier
| Mob Lv | 1 | 5 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| XP / kill | 32 | 50 | 78 | 150 | 243 | 354 | 495 | 659 | 846 | 1,056 | 1,290 | 1,548 |

Elite / boss XP and mob coin drops belong to P4 (combat).

### 3.5 Cooking (SkyyCooking `xp.<dish>` rows)
The build's own formula is kept: XP is proportional to the raw items in the recipe chain (K_XP x DIFF x chain_raw, KNOW_BONUS, x output
count). Two changes: (1) x F(T_dish), where T_dish = the highest tier_tags tier among the dish's chain ingredients (untagged = T1); (2) K_XP is set
so the build's rate check (ITEMS_PER_HOUR 1800 raw items an hour) pays **48,000 x F(T) Cooking XP an hour** after `xpMultiplier` 0.5 (the
model's 60 dishes an hour x 800 x F). The build asserts that rate for Food_Kebab_Vegetable and a pie and prints the new table. The
`LV50` constant becomes 406200. The `campfire.xpFactor` 0.25 stays. `maxXpPerMinute` 1500000 -> 0 (no XP caps, Skyy 2026-10-18).

### 3.6 Alchemy (SkyySkills)
`alchemy.tierXp` (bench tier I-V = Zone 1-5) `50,850,8000,18000,18000` -> `1500,7400,18200,33900,54400` (1,500 x f(zone start)). Each
`alchemy.xp.<id>` row keeps its ratio to its bench tier's old value: new = new tierXp[t] x old row / old tierXp[t] (Lesser potions 50 -> 1500,
Antidote 80 -> 2400, Popberry bomb 10 -> 300, Morph 800 -> 7400 (tier II), Small 850 -> 7400, normal 8000 -> 18200, Greater 18000 -> 33900, seeds
by their tier). The build prints the table and asserts every row >= 0.

### 3.7 Smithing (SkyySkills `smithing.xp.*`)
A bar pays its ore's XP (3.1); an alloy pays its tier: Bronze 180 (T3), Dusk 500 (T6), Azurvane 985 (T9), Cinder 1650 (T12),
Lumen 2450 (T15), Electrum = its tier_tags tier (the builder looks it up; no tag = T3). Silver 180, Gold 370, Onyxium 2650, Prisma 2450.
Potion_Empty 2 -> 20. SkyyGear crafting Smithing XP (Iron Normal 250 ...): P6.

### 3.8 Acrobatics + Fishing: the own-level factor (light)
These two have no tiers, so their XP is multiplied by f(own level), which keeps the time per level flat.
New SkyySkills row `xp.levelFactor.skills=Acrobatics,Fishing`: every XP gain into a listed skill (own events and bridge grants) x f(that
skill's level). Acrobatics bases x1.5 (GUESS, movement rates not measured): sprint 0.25 -> 0.4, run 0.15 -> 0.25, walk 0.05 -> 0.08, jump
2 -> 3, dodge 3 -> 5, fall 10 -> 15, perfect dodge 5 -> 8. Fishing (SkyyFishing): `fish.xp.mult` 1 -> 6 (a common fish = 60 x f(L); focused
Fishing about matches focused Foraging). Fishing stays "nice to have" until its rework: with ~2 % of play it trails by ~10-15 (model).

### 3.9 Exploration (SkyyExploration)
Exploration is never reset or capped, and its content is finite. Rule: a zone explored the normal way gives about that zone's levels.
- Zone factor `Z = f(zone start) = 1, 4.91, 12.15, 22.59, 36.23` (Zones 1-5) replaces `chests.zoneMult` `1,2,4,8` and `chunks.zoneMult`
  (5 entries; the builder checks a 5th entry is read, else extends the parser). luggage / airdrop / spots use the same Z.
- Calibration (the builder does this, numbers in the build log): count Zone 1's finds from SkyyExploration's own data (spots, secret
  spots, chests by tier, chunk count of the Zone 1 world area, zone.xp.Zone1_* rows). Then set ONE base scale k so that
  k x (Zone 1 total at today's base values, Z = 1) = 0.8 x 58,150 (80 % of the Zone 1 class levels; the rest comes from the zones the
  player passes through). Every base (chunks.xp 60, spots 500 / 1500, chests.base 400, luggage 150-1000, airdrop 1500, zone.xp.Zone1_*)
  is multiplied by k. The `zone.xp.Zone2+` rows are set to the Zone 1 values x Z. UNVERIFIED until a play-test: `/exploreadmin stats`.

### 3.10 Collections (SkyyCollections)
`tier.xp` / `tier.lastXp` stay as they are, but are multiplied by F(T) of the collection's item (tier_tags; untagged = 1) - new row
`tier.xpTierScale=true`. A T10 tier-III reward is then 500 x 22.6 = 11,300 (about half a level at Lv 60), not 500. The routes (xp.route)
are kept.

### 3.11 Other XP readers (the build asserts / logs them, no change in P3)
- SkyyPets takes pet XP from the growth of skill:fn:xp. Gathering XP is about x10, kill XP is unchanged. P5 rescales pet XP (pets.xp.* or
  a /F(T) read) - until then gathering pets level faster. Write this into the P5 notes.
- SkyyQuests XP rewards: they scale with zone in P6 / P7 (out of scope here).
- VP overflow (Skill-Trees-3 6.1) is a ratio (class XP / XP to cap), so it does not depend on the curve. The migration keeps that ratio (6.2).

## 4. Skills trail the class by 3-5

Mechanism 1 (pacing): the bases in section 3 are tuned on the model's time split (class 45 %, Mining 18, Foraging 15, Farming 10,
Cooking 4, Alchemy 4, Fishing 2). Result: 2-5 behind from Lv 10 to the cap (table 1b).

Mechanism 2 (soft catch-up, new, SkyySkills): skill XP x (1 + min(catchup.max, catchup.perLevel x (gap - catchup.freeLevels))) when
gap = class level - skill level > catchup.freeLevels. The class level = the active class skill's level. Applies to the slots in
`catchup.skills` (default Mining,Foraging,Farming,Fishing,Alchemy,Smithing,Cooking,Acrobatics; Exploration and the class skills never).
It is applied in the one XP gain path, after `multiplier` and before the tree / VP bonuses, and shown on the Stats page as "Catch-up +30 %
(8 levels behind your class)". Nothing is taken away from a skill that is ahead (focus is allowed, A:187 Q4).

Model, levels at 10 h / 20 h:

| Player | Catch-up | Class | Mining | Foraging | Farming | Cooking | Alchemy |
|---|---|---|---|---|---|---|---|
| balanced (45 % class) | on | 21 / 40 | 18 / 35 | 19 / 37 | 18 / 36 | 18 / 36 | 14 / 33 |
| balanced | off | 21 / 40 | 18 / 35 | 19 / 37 | 18 / 36 | 18 / 36 | 14 / 32 |
| fighter (70 % class) | on | 31 / 50 | 20 / 43 | 20 / 43 | 20 / 43 | 20 / 43 | 19 / 43 |
| fighter | off | 31 / 50 | 17 / 35 | 17 / 35 | 16 / 35 | 17 / 35 | 15 / 34 |
| gatherer (25 % class) | on / off | 13 / 23 | 18 / 31 | 18 / 32 | 17 / 31 | 17 / 32 | 15 / 27 |

The lag targets in balance_model.py change to Mining / Foraging / Beastmastery 4, Farming / Cooking / Alchemy 5 (was a GUESS of 8; Skyy said
3-5), Fishing 15.

## 5. Rebirth: past-life boost (recommended) vs scaled curves

Model (rebirth.py: run 1's class cap time 25.6 h x 0.85^n, the VP + kept-power speed from balance_model 5b, cap 50 + 10 n):

| Rebirth | Cap | VP + kept speed | Target h to class cap | Past-life boost needed | Time to cap / each first-time level | Scaled-curve factor needed | Each first-time level (scaled) |
|---|---|---|---|---|---|---|---|
| 1 | 60 | x1.23 | 21.8 | x1.21 | 21.8 h / 0.45 h | x0.86 | 0.39 h |
| 2 | 70 | x1.49 | 18.5 | x1.45 | 18.5 h / 0.40 h | x0.74 | 0.30 h |
| 3 | 80 | x1.78 | 15.7 | x1.78 | 15.7 h / 0.40 h | x0.63 | 0.25 h |
| 4 | 90 | x2.09 | 13.4 | x2.23 | 13.4 h / 0.38 h | x0.53 | 0.20 h |
| 5 | 100 | x2.45 | 11.4 | x2.80 | 11.3 h / 0.37 h | x0.45 | 0.17 h |

**Recommend the past-life boost.** Scaled curves also make the first-time Zone 4-5 levels 2x cheaper (0.17-0.25 h a level against the
0.6-0.75 h zone pace), so the new content gets rushed. The boost only speeds up levels you have already played. WoW's Warband "mentor"
alt XP bonus works the same way (K).
- New SkyySkills row `rebirth.pastLifeXp=1.2,1.45,1.8,2.25,2.8` (entry n = rebirth n; past the last entry = the last entry). XP into a
  rebirth-reset slot x boost[n] while that slot's level < previous cap = current cap - SkyyRebirth `caps.levels` (10). n = (current cap -
  levels.runCap) / caps.levels from rebirth:fn:cap. Rebirth 6+ (cap clamped at 100): previous cap = 100, so every level is a past-life level
  (x2.8). No saved data is needed.
- The numbers depend on P8's VP strengths (5a is PROPOSED). P8 re-runs this table and retunes the row.

## 6. Migration of players' XP: KEEP LEVELS (recommended)

Why: Skill Trees 3 just gave 1 point per level (SkyyTrees 0.4.0). Keeping XP instead would move every level. Today's Foraging / Cooking /
Alchemy XP (general list) would jump straight to the Lv 50 cap and pay a pile of level coins. Early classes would DROP (the old class
Lv 20 = 18.5k XP is Lv 8 now), taking tree points and grandfathering abilities. Keeping levels changes nothing the player sees except the
speed from now on.

### 6.1 Config (xp.properties) - one-time, PROJECT-RULES 4 (clone of Nc53Mig / Fa53Mig, marker `Balance P3 curve (SkyySkills 0.4.56)`)
Lines whose LAST entry still holds exactly the old default are rewritten. A hand-edited value is kept and logged INFO (that slot's XP is not
rewritten in 6.2). Order: History copy first (verified), then one change-log line per key (with Undo), the file's own bytes and line endings,
and a run-once marker. Keys: `levels`, `levels.class.sameAsOthers` false -> true, `levels.skill.Mining` + `levels.skill.Farming` (dropped
when at default), `gather.boost.skills` Foraging,Farming -> (empty), every `prefix.*` / `suffix.*` / `block.*` XP row in section 3,
`ranching.items`, `alchemy.tierXp` + `alchemy.xp.*`, `smithing.xp.*`, the 7 acro XP rows. A fresh file has the new defaults + the marker.

### 6.2 Saved XP (players/<pkey>.properties `<Slot>=<total XP>`) - one-time, new class `CurveP3Mig`
1. It runs at setup, BEFORE 6.1 rewrites the tables, reading the OLD tables from the file as it is now (that means levels / levels.class + max rule / own
   lists / runCap + floors).
2. History: copy `players/` + `level-floors.properties` to `history/curve-p3/<stamp>/` and verify byte-equal. If that fails: change nothing,
   WARN, and retry at the next start.
3. Per profile and per slot whose table changes: old level Lo and progress p = (XP - oldCum(Lo)) / oldNeed(Lo).
   New XP = newCum(Lo) + round(p x newNeed(Lo)). At or past the cap (overflow): keep the ratio r = XP / oldCum(cap) -> new XP = round(r x
   newCum(cap)), so the VP overflow stays the same. `.paid` markers stay (same levels, so no coins). Only the `<Slot>=` values are rewritten;
   the file's bytes, order and line endings are kept. Each file is written atomically.
4. `level-floors.properties`: each floor's "total XP then" -> newCum(floor level) (same file, same atomic write, History first).
5. Marker `Skyy_SkyySkills/curve-p3.properties` (scanned stamp + `<pkey>=done` per file). One change-log line "Balance P3: N profiles moved to
   the new curve, levels kept" with Undo = restore `history/curve-p3/<stamp>/` with the server stopped.
6. Bridge readers: SkyyPets re-baselines on a jump or drop (no free pet XP). Leaderboards rank by XP and the order stays the same within a
   slot (a monotone map).
Exploration, Acrobatics and Smithing are migrated the same way (on the general list today). Test on COPIES of the live players/ files.

## 7. Server Setup rows (tools/skyycfg.py, KEEP=10)

| Mod | Key | Label | Type / default / range | Tab |
|---|---|---|---|---|
| SkyySkills | `levels` (exists) | XP per level list | list, section 2 | Levels |
| SkyySkills | `levels.scale` (exists) | Level curve size | 100 %, 10-1000 (Q1's stretch knob) | Levels |
| SkyySkills | `levels.class.sameAsOthers` (exists) | Class skills use the other list | bool, true | Levels |
| SkyySkills | `xp.skillMult` (new table) | XP multiplier per skill | dec 1.0 per skill, 0-100 (Skyy's by-feel knob) | Levels |
| SkyySkills | `catchup.enabled` | Catch-up XP for skills behind the class | bool, true | Levels |
| SkyySkills | `catchup.freeLevels` | Catch-up starts after | int 5, 0-50 levels | Levels |
| SkyySkills | `catchup.perLevel` | Catch-up per level behind | int 10 %, 0-100 | Levels |
| SkyySkills | `catchup.max` | Catch-up max | int 100 %, 0-500 | Levels |
| SkyySkills | `catchup.skills` | Catch-up skills | text, section 4 | Levels |
| SkyySkills | `rebirth.pastLifeXp` | Past-life XP boost by rebirth | text `1.2,1.45,1.8,2.25,2.8`, each 1-10 | Levels |
| SkyySkills | `xp.levelFactor.skills` | Skills whose XP grows with their level | text `Acrobatics,Fishing` | Levels |
| SkyySkills | `prefix.*`, `alchemy.*`, `smithing.xp.*`, acro rows (exist) | - | new defaults, section 3 | as today |
| SkyyCooking | `xp.<dish>` (exist), `maxXpPerMinute` | - | new table; 0 | as today |
| SkyyExploration | `chests.zoneMult`, `chunks.zoneMult` (exist) + bases | - | `1,4.91,12.15,22.59,36.23`; bases x k | as today |
| SkyyCollections | `tier.xpTierScale` | Collection tier XP grows with item tier | bool, true | Rewards |
| SkyyFishing | `fish.xp.mult` (exists) | Fishing XP multiplier | 1 -> 6 | general |

Each mod's existing rows get the PROJECT-RULES 4 one-time migration (old default lines only). New rows are appended once in a marked block.

## 8. Files / anchors per mod (derive from the SET pin, new patch script each; never edit generated scripts)

- **SkyySkills 0.4.56** - `tools/skills_0_4_56_patch.py` reads `SkyySkills/build_skyyskills_0.4.55.py`:
  `LEVELS = [...]` (l.2233-2241; keep `LEVELS_OLD50` l.2238 for the 0.1 upgrade and add `LEVELS_055 = list(LEVELS)` as the 6.1 "old default");
  `CLASS_LEVELS` / `_cls_xp` (l.2245-2262, kept for the migration's old maths); `CURVE_L` `levels.class.sameAsOthers=false` (l.2940 -> true
  for a fresh file; asserts l.2945-2947 updated); `MINING_PER` / `SKL_DEF` (l.3052-3055) and `FARM_LIST` (l.5067-5082) leave the fresh
  defaults (SKL_KEYS assert l.3075); `N14_L gather.boost.skills` (l.2998); the XP rows (`L.append("prefix.Ore_...")`, the trunk / crop rows
  around l.2299+, `ZO` rows asserted at l.20960, `ACRO_L` l.2352+, `PD_XP_DEF` l.4944, `RANCH_DEF` l.4949, smithing l.2488, `ALCH_TIER`
  l.2558-2561); the Server Setup rows `CFG_ROWS` (l.20433-20843 area; key-order asserts l.20984-21072); the catch-up, past-life and
  level-factor code go in the single XP gain helper next to `SkillCfg.classXp` (0.4.10). Migrations: clone `Nc53Mig` (6.1) and the
  `ClassCurve` / `LvFloor` scanners (l.11829+, l.8931+) for `CurveP3Mig` (6.2). Harness `SkyySkills/test_skyyskills_0.4.56.py`: the list
  = section 2, sample XP values, the catch-up / past-life maths, the 6.2 migration on COPIES of live players/ files (levels identical before /
  after for every slot, ratio kept above the cap, run twice = once, hand-edited list = untouched).
- **SkyyCooking 0.1.14** - `tools/cooking_0_1_14_patch.py` from `build_skyycooking_0.1.13.py`: `K_XP` l.2093, `LV50` l.2094 -> 406200, the XP
  rate check l.2234-2256 (new target 48,000 x F(T) an hour), x F(T_dish) in the `XP[out] = ...` lines l.2137-2223 (import tools/tier_tags.py),
  the xp.* migration (old defaults only), `maxXpPerMinute` -> 0.
- **SkyyExploration 0.3.1** - `tools/exploration_0_3_1_patch.py` from `build_skyyexploration_0.3.0.py`: `chests.zoneMult` l.1245,
  `chunks.xp` l.1263, `spots.defaultXp` l.1300, `luggage.xp` l.1348, airdrop / zone.xp rows; the 5-entry zoneMult check; k calibration printed.
- **SkyyCollections 0.2.30** - `tools/collections_0_2_30_patch.py` from `build_skyycollections_0.2.29.py`: `TIER_XP` l.1217-1221 + the reader
  l.3400 (x F(T) when `tier.xpTierScale`).
- **SkyyFishing 0.1.11** - `tools/fishing_0_1_11_patch.py` from `build_skyyfishing_0.1.10.py`: the `fish.xp.mult` row l.837 default 6 + the
  one-time migration (1 -> 6 only when still 1).
- **tools/balance_model.py** - replace today's CURVES / ZONE_GATHER / ALCH_XP / COOK_XP with the section 2-3 numbers (keep "today" as a
  `--before` view), LAG Farming / Cooking / Alchemy 5, then `python tools/balance_model.py --md` (targets.md).
- Deploy TOGETHER (one round: saved data + several mods = a FULL round, PROJECT-RULES 4). Rollback floor: once CurveP3Mig ran, rolling Skills
  back below 0.4.56 shows the new XP on the old tables (levels move). Restore `history/curve-p3/<stamp>/` with the server stopped first.

## 9. Model output (tools/dev/scratch/p3: balance_model.py with section 2-4 numbers; "Today (model)" = the NEW numbers)

### 1. Class level vs hours (Normal, first time through, base pace)
| Zone | Mob levels | Target h | Cum h | Target lv/h | Target to min(top, 50) | New (model) | Source |
|---|---|---|---|---|---|---|---|
| 1 | 1-20 | 10 | 10 | 2.00 | 10.0 h | 9.1 h (today 2.8 h) | A:185 + LB:24 |
| 2 | 20-40 | 10 | 20 | 2.00 | 20.0 h | 20.0 h (today 12.8 h) | A:185 |
| 3 | 40-60 | 10 | 30 | 2.00 | 25.0 h | 25.6 h to the Lv 50 cap (today 21.5 h) | A:185 |
| 4 | 60-80 | 12 | 42 | 1.67 | - | rebirth runs (cap) | A:187 Q1 |
| 5 | 80-100 | 15 | 57 | 1.33 | - | rebirth runs (cap) | A:187 Q1 |

### 1b. Level at hour (run 1, cap 50): target / new
| Hour | Class | Mining | Foraging | Farming | Cooking | Alchemy | Fishing |
|---|---|---|---|---|---|---|---|
| 2 h | 5 / 6 | 1 / 5 | 1 / 5 | 1 / 5 | 1 / 5 | 1 / 5 | 1 / 2 |
| 5 h | 10 / 12 | 6 / 10 | 6 / 10 | 5 / 10 | 5 / 10 | 5 / 9 | 1 / 4 |
| 10 h | 20 / 21 | 16 / 18 | 16 / 19 | 15 / 18 | 15 / 18 | 15 / 14 | 5 / 8 |
| 20 h | 40 / 40 | 36 / 35 | 36 / 37 | 35 / 36 | 35 / 36 | 35 / 33 | 25 / 19 |
| 30 h | 50 / 50 | 47 / 50 | 47 / 50 | 46 / 50 | 46 / 50 | 46 / 50 | 39 / 30 |
| 45 h | 50 / 50 | 50 / 50 | 50 / 50 | 50 / 50 | 50 / 50 | 50 / 50 | 50 / 40 |
(Today's row at 10 h: Class 36, Mining 22, Foraging 12, Farming 14, Cooking 11, Alchemy 10. Skills reach 50 at 27.1-28.2 h.)

### 2. XP per hour needed WHILE doing the activity vs new
| Zone | Activity | Target levels | XP/h needed | XP/h new | Gap (P1 today) |
|---|---|---|---|---|---|
| 1 | Class | 1-20 | 12k | 12k | ok (x2.46) |
| 1 | Mining | 1-16 | 19k | 24k | ~x1.12 (x1.28) |
| 1 | Foraging | 1-16 | 23k | 29k | ~x1.09 (x0.25) |
| 1 | Farming | 1-15 | 30k | 40k | ~x1.15 |
| 1 | Cooking | 1-15 | 75k | 101k | ~x1.17 |
| 1 | Alchemy | 1-15 | 75k | 60k | ~x0.94 (1/16) |
| 2 | Class | 20-40 | 40k | 36k | ok |
| 2 | Mining | 16-36 | 82k | 84k | ok (x0.43) |
| 2 | Foraging | 16-36 | 98k | 99k | ok (1/1,460) |
| 2 | Farming | 15-35 | 141k | 141k | ok (x0.15) |
| 2 | Cooking | 15-35 | 352k | 356k | ok (1/659) |
| 2 | Alchemy | 15-35 | 352k | 295k | ~x0.99 (1/582) |
| 3 | Class | 40-50 | 70k | 63k | ok (x0.68) |
| 3 | Mining | 36-46 | 152k | 137k | ok |
| 3 | Foraging | 36-46 | 182k | 161k | ok (1/4,250) |
| 3 | Farming | 35-45 | 264k | 231k | ok |
| 3 | Cooking | 35-45 | 659k | 583k | ok |
| 3 | Alchemy | 35-45 | 659k | 729k | ok |
| 4 | Class | 60-80 | 139k | 127k | ok (x0.45) |
| 4 | Mining | 56-76 | 299k | 312k | ok |
| 4 | Foraging | 56-76 | 358k | 366k | ok (1/10,953) |
| 4 | Farming | 55-75 | 518k | 526k | ok |
| 4 | Cooking | 55-75 | 1.3M | 1.3M | ok (1/8,441) |
| 4 | Alchemy | 55-75 | 1.3M | 1.4M | ok |
| 5 | Class | 80-100 | 221k | 194k | ok (x0.41) |
| 5 | Mining | 76-96 | 488k | 480k | ok (1/11) |
| 5 | Foraging | 76-96 | 585k | 563k | ok |
| 5 | Farming | 75-95 | 850k | 809k | ok (1/55) |
| 5 | Cooking | 75-95 | 2.1M | 2.0M | ok (1/12,419) |
| 5 | Alchemy | 75-95 | 2.1M | 2.2M | ok |

Longest stretch without any level-up (run 1): **1.98 h** (today 3.24 h). It is entirely in the cap stretch: after ~28 h only Fishing (and
the unmodelled Exploration and pets) still level. See Q1. Class minutes per level (base pace): Lv 1 8, Lv 5-60 31-34, Lv 80 46, Lv 99 57
(today 1 -> 146). Rebirth table: section 5. Not modelled: Exploration, Acrobatics, Smithing, pets, quests (play-test).

## 10. Play-test (TEST-CHECKLIST section after deploy)
1. Fresh profile: class Lv 2 in ~8 min of fighting, Lv 5 in ~1 h of normal play; the skills you also do sit 2-5 below.
2. Old profile: every level the same as before the deploy (Skills page), the XP bar at the same %, no level-up coins paid, tree points unchanged.
3. Copper 50 / Iron 105 Mining XP, Oak 35, Wheat 40, Alchemy Lesser potion 1500. Stats page shows Catch-up when a skill is 6+ behind.
4. After a rebirth: "Past-life XP x1.2" on the Stats page below the old cap, gone above it.
5. `/skills` levels per hour feel: report any level slower than ~1 h of play.

## Questions for Skyy (each with today's default in [brackets])
1. **The cap stretch.** Run 1 reaches the Lv 50 cap at ~26 h, and the skills follow by ~28 h. The rest of the 40-50 h run levels only
   Exploration, Fishing and pets (gear, UT, bosses and overflow XP for Void Particles fill it). That breaks "never an hour without a level"
   for up to ~2 h at a time. [Keep: the cap stretch is for gear and VP] - or stretch everything with `levels.scale` 160 % so Lv 50 lands
   at ~40 h (Zones 1-2 become ~16 h each).
2. **Catch-up XP** for skills more than 5 levels behind your class. [On: +10 % per level beyond 5, at most +100 %]
3. **Rebirth speed** for levels you already reached in a past life. [Past-life XP boost x1.2 / 1.45 / 1.8 / 2.25 / 2.8] - or scale the
   whole curve down each rebirth (new Zone 4-5 levels would go 2x faster too).
4. **Existing players' progress.** [Keep levels: XP is rewritten to the same level and %] - or keep XP (Foraging / Cooking / Alchemy would jump
   to the cap, early class levels would drop and take tree points).
5. **How far the "useful" skills trail** (Farming, Cooking, Alchemy). [5 levels, like the essentials' 4; Fishing ~15 until its rework]
6. **Quick start**: the first 4 levels cost a quarter to a whole normal level (Lv 2 in ~8 min). [Yes]
7. **Focus pays.** A player who only mines levels Mining about 2x faster than a player who only fights levels the class, because a balanced
   player spends less time on each skill. [Accept; `xp.skillMult` per skill lets you trim by feel]
