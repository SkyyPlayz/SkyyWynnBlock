# Mana budget check (2026-10-18) - SkyySkills 0.4.52 "less Mana"

Skyy 2026-10-18 (docs/answered/skills.md): "(and i think we need to scale down how much mana you get as you level, and mana regen a little.
cause ive never ran out of mana on any class i tested."

Built in SkyySkills 0.4.52 (`tools/skills_0_4_52_patch.py`, harness `SkyySkills/test_skyyskills_0.4.52.py`). Every number below is a
Server Setup row (Skills -> Overall and Mana / Class Power). Where this goes next: section 4 (follow-ups in other mods). New ideas about
Mana go in this file or `research/Class-Power-Split.md`.

## 1. What changed (old -> new)

| Setting (key) | Archer | Warrior | Assassin | Monk | Mage | Berserker | Priest | Spellblade |
|---|---|---|---|---|---|---|---|---|
| Max Mana per class level (`mana.classPerLevel.<Class>`) | 2 -> 1 | 2 -> 1 | 2 -> 1 | 2 -> 1 | 10 -> 9.5 | 2 -> 1 | 5 -> 4.5 | 4 -> 3 |

| Regen setting | Old | New |
|---|---|---|
| In-combat Mana regen (`mana.regen.inCombat`, % of the normal refill + boosts) | 75 | 65 |
| Mana regen per class level (`mana.regen.perLevel`, % per level above `mana.regen.fromLevel` 20) | 7 | 5 |
| Mana on hit: wait between (`mana.onHitCooldownMs`, the fighters' refill) | 500 ms (2 / s) | 750 ms (1.33 / s) |

Unchanged: Base Mana by class (Mage 45 ... Berserker 12), vanilla's 3.33 Mana a second out of combat (Skyy's M11 lock), the 6 s combat
pause, the class balance tables, Mana on hit per class (1 / 0).

Why Mage 9.5 / Priest 4.5 and not lower: SkyyArmory 0.1.34's Mana check warns when a charged shot is more than 40 % (`check.share`) of a
class-skill-only pool at the weapon's first level. A Mithril staff (170 Mana) at Sorcery 40 is 39.9 % of 425.8 at 9.5 (41.9 % at 9);
a Mithril wand (85) at Divinity 40 is 38.2 % at 4.5 (41.9 % at 4). Going lower needs that check (or the top of the weapon ladder) moved
first - see 4.

Migration (Mn52Mig, once, on an existing xp.properties): each of the 11 lines still holding exactly the old default gets the new one;
an admin's own value is kept (and named in the log); History copy first; one change-log line each (Server Setup -> Changes -> Undo).
Skyy's NewBetaTest file holds all 11 old defaults, so all 11 move (checked on a copy: LIVE52).

## 2. The model

- Max Mana = Base Mana by class + per class level x L + Overall Level (assumed L / 2) x 0.2 + class balance Mana x L / 100. No gear,
  tree, accessory, pet or rebirth Mana (those are extra headroom, section 3).
- In combat the whole fight (you are hit at least every 6 s). Regen = 3.33 x (1 + R / 100) x in-combat %, R = per-level % x (L - 20)
  above 20 + class balance regen x L / 100. Fighters also get Mana on hit: 1 per wait (melee lands hits faster than the wait; Archer
  ~1 shot a second).
- Abilities: the class's A1 + A2 (SkyyClasses 0.1.38 walking rows) cast as soon as their cooldown ends. Rotation = one A1 cooldown.
- Casters' weapon filler: Mage a charged staff shot every 3 s, Priest a charged wand shot every 2 s (the rest moving / aiming / quick
  taps). Weapon = the level's band (SkyyArmory: Lv 10 Copper, 25 Cobalt, 40 Mithril, 55 Onyxium; staff = 2 x wand) or the Wood starter.
- Time to empty = the first moment a cast or shot is refused for lack of Mana (simulated in 0.05 s steps, up to 120 s; "never" = never).

## 3. Per class, before -> after

| Class | Lv | Max Mana | In-combat regen /s (+ on-hit) | Ability drain /s | Empty: abilities only | Empty: + band weapon | Empty: + Wood weapon |
|---|---|---|---|---|---|---|---|
| Archer | 10 | 46 -> 36 | 2.5 + 1.0 -> 2.2 + 1.0 | 0.63 | never -> never | - | - |
| Archer | 25 | 80 -> 55 | 3.5 + 1.0 -> 2.8 + 1.0 | 0.63 | never -> never | - | - |
| Archer | 40 | 114 -> 74 | 6.2 + 1.0 -> 4.5 + 1.0 | 0.63 | never -> never | - | - |
| Archer | 55 | 148 -> 93 | 8.8 + 1.0 -> 6.1 + 1.0 | 0.63 | never -> never | - | - |
| Warrior | 10 | 43 -> 33 | 2.5 + 2.0 -> 2.2 + 1.3 | 0.54 | never -> never | - | - |
| Warrior | 25 | 77 -> 52 | 3.5 + 2.0 -> 2.8 + 1.3 | 0.54 | never -> never | - | - |
| Warrior | 40 | 110 -> 70 | 6.1 + 2.0 -> 4.4 + 1.3 | 0.54 | never -> never | - | - |
| Warrior | 55 | 144 -> 89 | 8.8 + 2.0 -> 6.1 + 1.3 | 0.54 | never -> never | - | - |
| Assassin | 10 | 46 -> 36 | 2.5 + 2.0 -> 2.2 + 1.3 | 0.51 | never -> never | - | - |
| Assassin | 25 | 79 -> 54 | 3.5 + 2.0 -> 2.8 + 1.3 | 0.51 | never -> never | - | - |
| Assassin | 40 | 113 -> 73 | 6.1 + 2.0 -> 4.4 + 1.3 | 0.51 | never -> never | - | - |
| Assassin | 55 | 146 -> 91 | 8.8 + 2.0 -> 6.1 + 1.3 | 0.51 | never -> never | - | - |
| Monk | 10 | 43 -> 33 | 2.5 + 2.0 -> 2.2 + 1.3 | 1.20 | never -> never | - | - |
| Monk | 25 | 76 -> 51 | 3.5 + 2.0 -> 2.8 + 1.3 | 1.20 | never -> never | - | - |
| Monk | 40 | 110 -> 70 | 6.1 + 2.0 -> 4.4 + 1.3 | 1.20 | never -> never | - | - |
| Monk | 55 | 143 -> 88 | 8.8 + 2.0 -> 6.1 + 1.3 | 1.20 | never -> never | - | - |
| Mage | 10 | 146 -> 141 | 2.5 -> 2.2 | 2.18 | never -> never | 18 s -> 15 s (Copper) | 42 s -> 30 s |
| Mage | 25 | 298 -> 286 | 3.4 -> 2.7 | 2.18 | never -> never | 9 s -> 9 s (Cobalt) | never -> 90 s |
| Mage | 40 | 450 -> 430 | 6.0 -> 4.4 | 2.18 | never -> never | 6 s -> 6 s (Mithril) | never -> never |
| Mage | 55 | 602 -> 575 | 8.7 -> 6.0 | 2.18 | never -> never | 9 s -> 9 s (Onyxium) | never -> never |
| Berserker | 10 | 34 -> 24 | 2.5 + 2.0 -> 2.2 + 1.3 | 0.31 | never -> never | - | - |
| Berserker | 25 | 68 -> 43 | 3.5 + 2.0 -> 2.8 + 1.3 | 0.31 | never -> never | - | - |
| Berserker | 40 | 101 -> 61 | 6.1 + 2.0 -> 4.4 + 1.3 | 0.31 | never -> never | - | - |
| Berserker | 55 | 135 -> 80 | 8.8 + 2.0 -> 6.1 + 1.3 | 0.31 | never -> never | - | - |
| Priest | 10 | 93 -> 88 | 2.5 -> 2.2 | 2.12 | never -> never | 14 s -> 14 s (Copper) | 28 s -> 24 s |
| Priest | 25 | 170 -> 158 | 3.4 -> 2.7 | 2.12 | never -> never | 6 s -> 6 s (Cobalt) | 120 s -> 72 s |
| Priest | 40 | 247 -> 227 | 6.0 -> 4.4 | 2.12 | never -> never | 4 s -> 4 s (Mithril) | never -> never |
| Priest | 55 | 324 -> 297 | 8.7 -> 6.0 | 2.12 | never -> never | 6 s -> 6 s (Onyxium) | never -> never |
| Spellblade | 10 | 75 -> 65 | 2.5 -> 2.2 | 1.99 | never -> never | - | - |
| Spellblade | 25 | 137 -> 112 | 3.4 -> 2.8 | 1.99 | never -> never | - | - |
| Spellblade | 40 | 200 -> 160 | 6.1 -> 4.4 | 1.99 | never -> never | - | - |
| Spellblade | 55 | 263 -> 208 | 8.7 -> 6.1 | 1.99 | never -> never | - | - |

One rotation is always castable: the dearest A1 + A2 shape pair fits every class's new pool at its unlock level (A1 1, A2 10, A2-alt 20,
A1-alts 30; tightest = Berserker Lv 1, 13 Mana vs 3). Extra headroom not counted above: SkyyTrees Mana nodes (+48 Mana, +45 % regen for
Mage / Priest; +5 % regen for the others), SkyyGear Untiered robes (+12.5 % regen a piece, +50 % for the set), SkyyAccessories Mana %,
rebirth Mana, Alchemy / Overall Mana.

## 4. Findings - what SkyySkills alone cannot fix (follow-ups, NOT edited in this round)

1. **Abilities alone never empty anyone.** Every class's two abilities cost 0.3 - 2.2 Mana a second on cooldown; even the new regen at
   Lv 10 is 2.2 a second (+ 1.3 on hit for fighters). Fighters cannot "feel Mana as a limit" from regen / pool cuts "a little" - it
   needs SkyyClasses ability costs (fighters pay 1 - 9 Mana on 6 - 40 s cooldowns), more Mana on traversal (SkyyArmory blinks / rush /
   kunai / grapple), or a much lower fighter regen (a per-class regen table does not exist yet). Ask Skyy which.
2. **Casters are decided by the weapon ladder, not the pool.** With the level's band weapon a Mage / Priest already runs dry in 4 - 15 s
   (a Mithril staff = 170 Mana = 40 % of the pool a shot); with an old low-tier weapon at a higher level they never do (the 5 % per
   level regen growth outpaces a Wood staff). Skyy's "never ran out" fits low-tier weapons or ability-only play. Options for Skyy:
   flatten the top of SkyyArmory's ladder (Mithril / Onyxium 85 wand / 170 staff) and/or raise `mana.regen.fromLevel` (20) so regen
   growth starts later.
3. **SkyyArmory 0.1.34 `check.share` 40** is the floor for Mage / Priest Mana per level (9.5 / 4.5); a lower caster cut needs it raised
   (45 allows Mage 9 / Priest 4) or the top staff / wand costs lowered first, in the same deploy.
4. Regen defaults in other mods (unchanged): SkyyTrees 0.3.23 Mana Regen nodes (R = +5 % each; Mage / Priest +45 %, others +5 %; SkyySkills'
   skill:fn:manaregen "trees"), SkyyGear 0.3.26 Untiered robes +12.5 % Mana regen per piece ("SkyyGear" source), SkyyAccessories 0.5.26
   (Mana %; Mana Regen on Magical / Arcane still waiting), SkyyPets 0.4.3 (no Mana regen found), SkyyArmory soul.noRegen (true) +
   traversal Mana costs, SkyySkills classBoost.regen (3 - 15 % at 100, unchanged).
5. SkyyClasses 0.1.38's build-time affordability table `_POOL` still holds the old pools (e.g. Monk Lv 30 = 81, now 51); it only asserts
   costs <= pool, so it still passes - refresh it the next time SkyyClasses is built.
6. Refresh the Class Balance Workbench artifact (standing rule: Mana numbers changed).
