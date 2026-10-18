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
