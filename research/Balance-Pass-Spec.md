# Balance pass - scope (what gets scaled to the goals) - 2026-10-18

Goals: research/Balance-Goals-Questions.md (Skyy's popup answers in docs/answered/skills.md, economy.md, classes.md, pets.md 10-18),
class ratings research/Class-Roles-Sheet.md, skill trees research/Skill-Trees-3-Spec.md. Starts after the weekly reset (2026-10-20).
Method: one shared model (time per zone, XP/h per activity, coins/h, drops/h) -> every system below is tuned against it -> Skyy plays
and we micro-adjust by feel. Where answers / decisions go: docs/answered/<topic>.md; this file holds the plan. Index: INDEX.md.

## 1. Time and levels
- XP per level curves: class + every skill (one steady shape; skills trail class by ~3-5 levels).
- XP per action: every gathering block, crop, log, fish, kill, heal, craft, cook, smelt, alchemy brew, exploration find, acrobatics move.
- Level cap ladder 50 -> 100 (+10 per rebirth); rebirth length 45 h then 15% shorter each.
- "No more than 1 h of play without a level-up AND a gear upgrade" check across the whole first run.

## 2. Combat
- Mob health / damage per level (Normal; Easy / Hard derived), elites 3x / 10x mini bosses, bosses 3-4 min solo.
- Player health, defense, damage per level per class (Class-Roles-Sheet), Mana pools + regen (dry every 20-30 s), Stamina, speed +
  weight (heavy class slowed less by heavy gear).
- Ability numbers + cooldowns per class (Sacred Heal 8 s set), skill-tree ability damage, the Copper Staff 50% Mana question.
- Over-level difficulty (+5 hard, +10 wall), death penalty (small coin loss), mob XP and coin drops.

## 3. The four power sources (35 / 30 / 20 / 15)
- Weapons + tools: damage / power / speed lines per tier, Fortune per level, upgrade point costs.
- Armor: combat sets per tier and weight, gathering sets (Fortune / power / speed), set bonuses, best-in-tier ~3x plain.
- Accessories (Void Charms): every charm's numbers, Accessory Power, crafting costs.
- Pets: every kind / rarity / level, pet rebirths, fusing, skill XP pets (pets.md 10-18).
- Reforging, grades, rarity rolls, UT (1-2 per hour of elite hunting), Mythic (1 per 5-10 boss kills), identify level window.

## 4. Gathering and crafting
- Collection sizes per tier (II in ~10 min, V in 1-2 h), the I-VI unlock ladder, Enchanted recipe costs.
- Tool + armor tier-up material costs (armor set ~45 min-1.5 h), plain below Dusk.
- Breaking power / hits per block per tier, Vein Mine / Tree Feller levels, Fortune math.
- Crop growth times, watering, totems (late game fully idle - only totem upgrades are manual), Eternal seeds.
- Smelting times + Furnace Charm, cooking dishes (buffs, XP), alchemy potions, fishing (until its rework: bonuses only).
- Gathering-tier lock for F pick-up and zone spawns (Zone 1 up to T5, mushrooms from Zone 4, Zone 5 mostly its own 3 crops).

## 5. Economy
- Coin income per hour per activity (equal across gathering skills, rising with level); targets 10k / 500k / 10M at end of Zone 1 / 3 / 5.
- Bazaar prices + premiums (no loops), Auction House fees, NPC shop / merchant prices.
- Coin sinks (even mix): upgrades, sacks, vault pages, respecs, Void Charms, cosmetics, the death coin loss.
- Buying across: combat gear buyable (~1.5x the time of earning it), gathering gear not (only its upgrade materials).

## 6. Progression systems
- Skill-tree points (1 per level), row gates, respec cost; dust removed (points + coin refund).
- Rebirth: Void Particles earned per rebirth, upgrade costs and strength (each rebirth ~15% shorter), keep buff +0.25% per VP, rebirths past
  5 allowed (cap stays 100).
- Sacks / Void storage space per level + upgrade costs, vault pages.
- Quests: rewards (XP, coins, gear) per zone, tutorial pacing; exploration rewards; shards (keep over rebirth - slower but lasting).

## 7. Order of work
1. Build the shared pacing model (a script under tools/ that prints XP/h, coins/h, drops/h per activity and level).
2. Tune level curves + XP per action. 3. Combat + classes. 4. Gear / accessories / pets (the 35/30/20/15 split).
5. Gathering + crafting. 6. Economy. 7. Rebirth + skill trees (with the Skill-Trees-3 build). 8. Skyy plays, we adjust.

## 8. THE PLAN (Skyy 2026-10-18: "lets make a plan. to complete that list, what needs done in what order?")
Each phase = one round (build -> review -> deploy) + Skyy plays and reports; later phases build on earlier numbers. P0 runs on
OpenRouter / Jev (cheap) before the weekly reset; P1+ after 2026-10-20. Rough cost: one full round ~5-10% of the weekly budget.

| Phase | What | Mods | Why this order |
|---|---|---|---|
| P0 | Inventory: dump every current number (XP tables, curves, mob / class / gear / pet / charm stats, drop rates, prices, costs) into research/balance/*.md tables | none (read-only) | the model needs today's numbers |
| P1 | Pacing model `tools/balance_model.py` + the target table (level vs hours per zone, coins and drops per hour) | tools only | every later phase is tuned against it |
| P2 | Skill-tree engine + dust removal + migration (Skill-Trees-3 R1 + R2) | SkyyTrees, SkyySkills, SkyyMenu | trees change points, perks and abilities - combat and skill numbers depend on them |
| P3 | XP: one curve shape for class + skills, XP per action, skills trail class 3-5 | SkyySkills, SkyyCollections (XP sources), SkyyCooking, SkyyExploration | levels set the clock for everything else |
| P4 | Combat core: class stats + weight / speed, Mana / Stamina, class trees + abilities (Skill-Trees-3 R3 classes), mob curve, elites / bosses | SkyyClasses, SkyyTrees, SkyyGear (player curves), SkyyArmory (weapon numbers), SkyyMobs | needs P3 levels; the four power sources sit on top of it |
| P5 | Power sources 35/30/20/15: weapons / tools, armor (3x best vs plain), Void Charms, pets, reforge / rarity, UT / Mythic rates | SkyyGear, SkyyArmory, SkyyAccessories, SkyyPets, SkyyMobs (drops) | splits the power the P4 baseline defines |
| P6 | Gathering + crafting: collection sizes, tier-up / armor costs, hits per block, crops / totems, smelting / cooking / alchemy, F-pickup tier lock + zone spawns | SkyyCollections, SkyyGear, SkyySkills, SkyyWorldGen, SkyySacks, SkyyCooking | uses P3 XP and P5 tool / armor power |
| P7 | Economy: coins per hour, Bazaar / AH / shop prices, sinks, death coin loss, buy-across rules | SkyyBazaar, SkyyAuctions, SkyyMerchants, SkyyCoins, SkyyIslands (death) | prices follow the P6 gathering speeds |
| P8 | Rebirth: Void Particles, Nexus upgrades, keep buff, rebirths past 5 default, skill trees for the skills (Skill-Trees-3 R3-R4) | SkyyRebirth, SkyyTrees, SkyySkills | rebirth speed-up is measured against the finished first run |
| P9 | Whole first-run check with the model (no hour without a level + a gear upgrade) + Skyy's feel pass | any | final tune |

Play-test after P3, P4, P5, P6 and P7 (one TEST-CHECKLIST section each).
