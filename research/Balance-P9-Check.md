# Balance pass P9 - whole first-run check (2026-10-22)

What this is: the whole first run (Zone 1 -> class cap 50, then rebirths 1-5) simulated with the LIVE numbers of the deployed set
(HANDOFF.md versions = tools/deploy_set.py SET), checked against every Skyy goal. Plan: research/Balance-Pass-Spec.md section 8 (P9).
Run it: `python tools/balance_model.py --p9 --check` (exit 1 on a failed goal), `--p9 --fixes --check` (the same with the fix list
below applied - a what-if, never written anywhere), `--p9 --md` writes research/balance/targets.md section 10. `--p3` = the model
without the P9 live corrections. Rebirth runs come from tools/balance_rebirth.py. Where answers go: docs/answered/skills.md (Skyy's
words), this file's fix list -> the next balance round. Index: INDEX.md.

## For Skyy (plain words)

1. Levels, zones, coins, combat and gear all hit your targets: Zone 1 in 12.5 h, Lv 40 at 26 h, Lv 50 at 33 h; coins x1.0 of the x10 targets.
2. A gear upgrade comes at least every hour for every kind of player (worst 0.9 h). Best gear is ~3x plain, the 35/30/20/15 split holds.
3. The big miss: Beastmastery stalls around Lv 44-45. Your pet only earns XP from skills that are NOT maxed, so once the others hit 50 it crawls.
4. Because of that, an even player who wants every essential skill maxed goes ~3 h between level-ups at the end. One setting fixes it (fix 1).
5. Mining levels too fast and Foraging too slow: two old settings from 10-15 (Mining x1.25, felled logs 70 %) still sit on top of P3's new XP.
6. The catch-up bonus (+100 %) makes "fight first, catch skills up later" ~20 % faster than levelling evenly. You wanted even to be easier.
7. Zones 4 and 5 go by too fast in rebirth runs (9 h each instead of 12-16 / 15-20 h) - rebirths shrink the right amount, but the new levels are cheap.
8. Late-game casters with good Mana charms + a Mana pet run dry after 32-40 s instead of 20-30 s. Worth a feel test before changing.
9. With every fix applied the model passes 34 of 35 goals. The one left is a choice: with even levelling the run is done at ~36 h, not 40-50 h.
10. Idle shards (your choice, not changed): one 3-day absence with max totems banks ~72 active hours = 3.5x Zone 5's whole coin goal.

## Pass / fail per goal (live set, `--p9 --check`; "with fixes" = `--p9 --fixes --check`)

| Goal | Live model | OK | With fixes | Fix |
|---|---|---|---|---|
| A level-up every <= 1 h (p90 worst gap, start -> run done) - even / fighter-first / gatherer-first | 2.96 / 0.42 / 2.96 h | NO | 0.52 / 0.42 / 0.52 h | F1 |
| A gear upgrade every <= 1 h before the class cap (p90) - even / fighter / gatherer | 0.70 / 0.60 / 0.92 h | yes | same | - |
| Zone 1 (class Lv 20) ~12 h, even player | 12.5 h (fighter 8.1, gatherer 22.5) | yes | same | - |
| Zone 2 (class Lv 40) ~26 h | 26.2 h | yes | same | - |
| Class Lv 50 ~33 h | 32.9 h (fighter 21.3, gatherer 38.7) | yes | 33.1 h | - |
| First rebirth 40-50 h (class + Mining, Foraging, Farming, Cooking, Alchemy, Beastmastery at 50) | never by 60 h (Beastmastery stalls) | NO | 35.6 h | F1 + F6 (ask) |
| Skills trail the class 3-5 levels (even player, 10 / 20 / 30 h) | Mining +2 ahead, Foraging -11, Farming -7 | NO | every skill 3-7 behind | F2 |
| Even levelling easier (even done no later than a focused player, +10 %) | even never vs fighter 28.8 h | NO | 35.6 vs 32.8 h (x1.08) | F1 + F3 |
| Focus allowed (fighter Lv 50 >= 15 % sooner, gatherer still gets there) | x0.65, gatherer 38.7 h | yes | same | - |
| Rebirth runs 15 % shorter each (rebirths 1-5, ratio 0.97-1.03) | 1.00 / 0.99 / 1.01 / 1.00 / 1.00 | yes | 1.00 all | - |
| Zone 4 first-time levels (Lv 60-80, rebirths 2-3) 12-16 h | 9.4 h | NO | 14.2 h | F4 |
| Zone 5 first-time levels (Lv 80-100, rebirths 4-5) 15-20 h | 8.7 h | NO | 16.7 h | F4 |
| Gathering skills ~equal coins / h (0.85-1.15, every zone) | 5 / 5 zones | yes | same | - |
| Coin targets x10 at zone end (active, 0.85-1.15) | x1.03 / 1.04 / 1.01 / 1.01 / 0.99 | yes | same | - |
| Best gear ~3x plain (kit DPS x3.2 / EHP x2.8 +-15 %) | DPS x3.63, EHP x2.48 | yes | same | - |
| Power split 35 / 30 / 20 / 15 | 35 / 31 / 19 / 15 | yes | same | - |
| Combat: trash 4-6 hits, tough 12-15, you die in 12-15 trash hits, boss 3-4 min, +5 lv 1.6-2.2x, +10 lv >= 4x | 4.4 / 12.5 / 12.6-13.6 / 3.5 min / x1.78-1.89 / x4.26-4.80 | yes | same | - |
| Casters dry every 20-30 s (P4 benchmark: no tree / charm / pet Mana) | 20-28 s | yes | same | - |
| Casters dry 20-30 s with HALF the live Mana stack (Lv 20 / 60 / 100) | Mage 28/32/40, Priest 28/32/40, Spellblade 30/30/36 s | NO | 22/28/32, 24/28/32, 25/25/30 s | F5 |
| Max gathering Fortune within the P5 budget +5 % | x1.000 / 1.005 / 1.012 (Mining / Foraging / Farming) | yes | same | - |
| Level-up coins 4.5-9.5 % of each zone's coins | 7.9 / 9.9 / 7.4 / 7.8 / 7.7 % | yes | same | - |
| Smithing-100 craft worth <= 1.25x a mob bag | x1.05 | yes | same | - |
| Beastmastery reaches the run-1 cap | even 45, gatherer 44 (fighter 50) | NO | 50 for all | F1 |
| Idle shards: one 3-day absence at Totem I..V | 14 / 29 / 43 / 58 / 72 active h = x1.18 / 2.01 / 3.02 / 3.53 / 3.53 of the zone's coin span | report | same | F7 (Skyy's choice) |

## Ranked fix list

Each: mod + setting / row -> proposed value, why, which goal. **[Server Setup]** = Skyy can change it in game (SkyWynn Menu -> Server
Setup); **[code]** = a build round.

1. **F1 SkyySkills `beast.xpFactor` 1 -> 1.5 [Server Setup, Skills].** Beastmastery only gets pet XP from skills below the cap, so it stalls at
   ~44-45 once everything else is 50. At 1.5 it reaches 50 alongside the others. Fixes: Beastmastery cap, the level-up hour rule at the end of
   the run, even-is-easier, first-rebirth "done". (Check the P5 pet row afterwards: pets themselves are not changed by this.)
2. **F2 SkyySkills `mining.xpMultiplier` 1.25 -> 1 and `fell.otherLogsPercent` 70 -> 100 [Server Setup, Skills - Gathering].** These came from
   Skyy's 2026-10-15 Mining-vs-Foraging fix and predate P3, whose XP per action (ore 50 / log 33 x F(T)) already evens the two out. Today Mining runs
   x1.25 too fast (2 levels AHEAD of the class at 30 h) and Foraging x0.73 too slow (11 behind). Fixes: skills trail 3-5.
3. **F3 SkyySkills `catchup.max` 100 -> 20 (%) [Server Setup, Skills - Levels].** At +100 % a player who fights first and catches the skills up
   later finishes everything ~20 % sooner than an even player. At 20 % even is within 8 %, and lagging skills still get a boost. Fixes: even-is-easier.
4. **F4 SkyySkills `levels` list x1.5 for Lv 61-80 and x1.9 for Lv 81-100, plus `rebirth.pastLifeXp` = 1.1, 1.52, 2.05, 3.35, 4.92, 2.92, 3.08,
   3.25, 3.44, 3.67 [code recommended; both rows ARE in Server Setup - Levels, marked danger].** Rebirth runs already shrink 15 % each, but the
   10 new levels per run are cheap (~4.5 h). Dearer new levels + a bigger replay boost keep the -15 % runs and give Zone 4 14.2 h and Zone 5
   16.7 h. A code round is safer: it must also update tools/balance_rebirth.py PAST_LIFE_P8 (the SkyySkills patch asserts they match) and
   re-run `balance_rebirth.py --check`. Fixes: Zone 4 / 5 hours.
5. **F5 SkyyAccessories Intelligence charm line x0.3 (Mythic +24 % -> ~+7 % max Mana) and SkyyPets Mana pets (Skrill / Void Eye / Void Larva
   21 % -> ~6 %) [code].** The P4 Mana benchmark has no tree / charm / pet Mana. With half the live stack, late-game casters run dry after
   32-40 s. **Feel test first** - long bars may feel fine; the other option is to keep them and accept 30-40 s late game. Fixes: casters dry 20-30 s.
6. **F6 First rebirth 40-50 h - ASK SKYY (no setting by default).** With the fixes an even player has everything at 50 by ~36 h, because
   "Lv 50 at ~33 h" (A:197) + skills 3-5 behind leaves only ~3 h. Options: (a) accept a ~36 h first run, the 40-50 h being optional VP-overflow
   / UT / boss play (recommended); (b) `levels.scale` 120 -> 135 [Server Setup] = Lv 50 at ~37 h and done ~40 h (breaks "Lv 50 at 33 h").
7. **F7 Idle shards - report only (Skyy chose "20-100 %, 3 days").** A max-totem 3-day absence banks ~72 active farming hours (x3.5 of Zone 5's
   coin span; Totem I already beats Zone 1's whole target). If it feels too strong: SkyyShards `shard.maxOfflineSec` 259200 -> 86400 [Server
   Setup] cuts the bank to a third. The Bazaar's price impact (impactCoins 22,500) will also pull real sales well under the nominal number.

No fix needed: tree Fortune outside the 40 cap (Foraging +6, Farming +16 = 0.5-1.2 % of the budget), Smithing crafts (x1.05 a bag; Mythic / UT stay
loot-only), level-up coins (7-10 % of each zone; Zone 2 9.9 % is P7b's known exception), charms / pets Fortune at Lv 100 (on the P5 ladder).

## Live vs model - every difference found (live wins)

Audit 2026-10-22 of the generated build scripts at the SET pins (SkyySkills 0.4.61, Collections 0.2.32, Cooking 0.1.16, Exploration 0.3.3,
Fishing 0.1.12, Gear 0.3.38, Armory 0.1.43, Mobs 0.1.16, Classes 0.1.45, Trees 0.4.9, Accessories 0.5.31, Pets 0.4.9, Bazaar 0.2.1, Coins
0.1.11, Merchants 0.1.7, Sacks 0.8.28, Shards 0.4.5, Islands 0.5.24, Rebirth 0.4.3, Quests 0.4.2, Auctions 0.1.15).

Changed in tools/balance_model.py (the "P9 LIVE corrections"; `--p3` turns them off):
1. `mining.xpMultiplier` 1.25 (skills:5249) - the model had none -> `MINING_XP_X`.
2. `fell.otherLogsPercent` 70 (skills:5249) - every felled log but the chopped one pays 70 % -> `FELL_X` 0.73 (GUESS 10 logs a tree).
3. Gathering XP tier = the SKILL level's band (a tool / hoe tier-up needs the skill level of the new tier: research/Gathering-Shards-Spec.md 4.1);
   the model used the class level's tier. Cooking / Alchemy keep the class zone (no recipe level gate found).
4. Level-up coins = `levelCoins` x the coin curve (0.4.61); the model's run paid the dead `coinsPerLevel` 100 x level.
5. Section 3 coins: P7 Bazaar prices + the x10 targets (it still used the P1 prices and the pre-x10 targets).
6. `rebirth.pastLifeXp` 1.1, 1.35, 1.6, 2, 2.45, 2.15 ... 2.7 (skills:5560) -> `PAST_LIFE_LIVE` (section 5c); `PAST_LIFE` keeps the P3 list for
   `balance_rebirth.py --live`.
7. `catchup.skills` includes Beastmastery (0.4.60) -> added to `CATCHUP`.

Live, not changed in the old phases' code but covered by the new P9 rows:
8. Smithing crafts roll the MOB odds column (50/30/13/5/1.5 x levelShift) + a step-up of Smithing x 0.5 % (max 50 %) to Fabled at most
   (gear:19358-19384); P5's sim still uses odds.craft 60/25/10/4/1 (P9's run uses the live rule).
9. Mana from trees (Mage Mana Well +16 %, +10 % regen), the Intelligence charm line (to +24 %) and Mana pets (21 % x 1.75) - none in P4's benchmark.
10. Tree Fortune outside `TREE_FORT_MAX` 40: Foraging alias FFortune +6, Farming AFortune / AFortune II +16 (trees_v3_effects.py).
11. Idle shards bank wall-clock time (72 h between visits, Shards 0.4.5:1061); P7 counts the totem share only over played hours.
12. Pets earn XP only from skills below the cap (P5 7.8 overflow UNVERIFIED in game) - the cause of the Beastmastery stall.

Stale baseline only: `P6_ARMOR_TODAY` (450, 4) = 0.3.35's ladders; 0.3.38 reprices them with p6_armor / p6_tool (gear:7677-7723).

Not modelled (small or measured in game): SkyyBank daily interest (2 % to 1M, 1 % to 5M, 0.5 % to 10M, cap 10M; <= 85k a day - ~1k a day in
Zone 1); quest board ~260 coins a day; Auction fees (1-2.5 % + duration fee, sinks); Bazaar price impact (impactCoins 22,500, 120 min half-life);
Cooking's per-dish spread (skewer route ~0.47x, pie route ~2.1x of the 48,000 x F mean); Acrobatics, Exploration and Priest heal XP; loot
chests (33 %), elite chance 3 % (+3 levels), Armory essence / sigil drops; tool Mining / Chopping Power; the 200 fish / h GUESS.

Same as the model (checked): levels.scale 120 + one list for class and skills; ore / log / crop / dish / alchemy XP; fish.xp.mult 6; catch-up
5 / 10 % / 100 %; levelCoins text; kill XP (perHealth 0.2, class x3); collection curves + tier.coins (coinsByTier); luggage / airdrop coins;
every P4 weapon / spell / resistance / mob table (built from the model or asserted); floor 70; level-gap rules; elite / mini / boss; wands; P5
stats, armor pool, rarity, slot power, level floor / full, gathering-armor Fortune + Breaking Power, UT meter, Mythic pity, loot 6 % / 20 an
hour, odds, smart 50 / lean 75, levelUp cap +10; P7 gear cost bases; ability Mana + costPerLevel, tree dmg / dr caps; charm ladder + Power
tables + gathering Power; pet rarity, kinds, Fortune, rebirth stat, XP split, curve; respec 2100; coin curve, death 5 / 5 %, merchant 1.875 h,
spread 0.10, minSell 2, Furnace 25 %, totem 20-100 %, 72 h; VP 20 / 10 / 2 / 12, keep 0.25 %, Insight / Echo ranks. Tool Fortune cap: 0 = none.

## Model notes

Player types (time split; a capped activity's time moves to the uncapped class / skills by their split, Fishing keeps 2 %): even = the P3 split
(class 45 %); fighter-first class 70 %; gatherer-first class 25 % (the P3 section 1c splits). Gear upgrades = combat drops (6 % of 150 kills an
hour x the class share, <= 20 an hour, smart bags, class lean), a crafted set at each new metal band (live Smithing odds), item level-ups (+10
cap), and gathering tool tier-ups + armor pieces (P6 hours: 0.75-1.5 h a set, tool = a third; the next tier needs the skill's band). The pet is
a Mining pet (P5 default). 40 seeds a type; p90 of each seed's worst gap. GUESSES: the time splits, 10 logs a tree, 150 kills an hour, the
"half / full" Mana stacks, Smithing ~5 levels behind the class.
