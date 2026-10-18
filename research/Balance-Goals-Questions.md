# Balance goals - questions for Skyy (2026-10-18)

Why this file exists: Skyy said "I'm not a game dev ... I'd prefer if you did the balancing based on my rough goals. then we micro adjust
based on feel" + "Come up with a list of important questions so we can set all the base goals properly" (docs/answered/skills.md 10-18).
Answers here set the targets for research/Balance-Pass-Spec.md. Each question has today's default in [brackets]. When Skyy answers,
record the words in docs/answered/<topic>.md (qa_append.py) and tick the line here. Index: INDEX.md (research/).

Already set (10-18): ~10 h per zone for Zones 1-3; first rebirth after 40-50 h; each later rebirth a bit shorter; level cap 50 first run,
+10 per rebirth; all skills + class level at about the same steady pace; classes tuned to their role.

## A. Time and pacing
1. How long should a player spend in Zone 4 and Zone 5 (first time through)? [12 h and 15 h - a bit longer than Zones 1-3]
2. What does "a session" look like for your players - how long do they play at once? [1-2 h; every session should give at least one
   level or one gear upgrade]
3. How much faster is each rebirth? [15% shorter each time: run 1 ~45 h, run 2 ~38 h, run 3 ~32 h ...]
4. Should a player be able to max EVERY skill in one run, or must they pick focus skills? [Pick: a focused player maxes class + 2-3
   skills per run; everything maxes over the 5 rebirths]
5. How much should skill levels lead or lag your class level? [Gathering skills about equal to class level if you gather as much as you
   fight]

## B. Combat difficulty
6. How hard is a normal mob at your level - hits to kill it, hits it takes to kill you? [About 4-6 of your hits kill it; it needs 12-15
   hits on you in starter armor]
7. Elites and mini bosses: how much tougher? [Elite = 3x health, 1.5x damage; mini boss = 10x health, 2x damage]
8. Full bosses: how long should a fight last solo at the right level? [2-3 minutes solo, under 1 minute in a group of 3]
9. How punishing is dying? [Light: respawn on your island, lose nothing; bosses reset]
10. Should fighting mobs 5+ levels above you be possible with skill (parries, dodges) or mostly a wall? [Possible but hard: +5 levels
    = about 2x as hard; +10 = a wall]

## C. Classes
11. Rank each class 1-5 on: damage, health/defense, speed/mobility, Mana, support/healing, range. [Draft table in the spec: e.g.
    Fighter tank-ish melee, Rogue fast + crit + fragile, Mage high damage + low health, Priest healing + low damage, Ranger range +
    mobility, Monk speed + parry, Spellblade balanced hybrid]
12. Should every class be able to solo all content, or do some need a group? [All can solo; support classes are slower solo but much
    better in groups]
13. Mana: how often should a caster run dry in a long fight? [Every 20-30 s of non-stop casting, then 5-8 s of basic attacks to refill]
14. How big is the gap between a player in their best gear and fresh-tier gear at the same level? [Best gear = about 2x the damage and
    survivability of plain gear]

## D. Gear, accessories, pets (the four power sources)
15. Split of a player's power at end of a zone: tool/weapon, gear, accessories, pets? [Weapon/tool 35%, armor 30%, accessories 20%,
    pets 15%]
16. How rare should UT drops feel? [About one UT per 2-3 hours of elite / dungeon hunting in the right zone]
17. Mythic drops (full bosses only): how often? [About 1 per 15-20 boss kills]

## E. Economy
18. How many coins should a player have at the end of Zone 1 / 3 / 5 if they never spend? [5k / 100k / 2M]
19. What should coins mostly be spent on? [Upgrades (tool points, sacks, Void Charms, vault pages) > Bazaar materials > cosmetics]
20. Should a dedicated gatherer be able to buy their way through combat gear (and a fighter buy gathering materials)? [Yes, but at about
    1.5x the time it takes to earn it yourself]

## F. Gathering and crafting
21. How long to fill one tier's collection to II (tool unlock) / V (alloy gear)? [II = 20-30 min of focused gathering; V = 3-4 h]
22. Should crafting a tier's armor set be a real goal (hours) or a quick step? [A real goal: about 1-2 h of materials per set]
23. Farming: active (planting, watering) vs. idle (totems later) - how much of farming should be idle? [Mostly active now; totems
    later make up to 50% idle at a lower rate]

## How the answers are used
The balance spec turns these into numbers: XP per level curves for every skill + class, mob strength vs player strength per level,
drop rates, coin income per hour, collection sizes, crafting costs. Then Skyy plays and we micro-adjust.
