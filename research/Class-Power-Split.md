# Class power split - Mana vs Stamina (Skyy 2026-10-08)

Skyy: "magic uses have more mana, but their spells take more mana and less stamina. the ability's should kinda verry class to class, based on
the classes max mana and stamina, (the classes should verry in max mana and stamina, like allocating power.  mage might be 75% mana 25%
stamina, and his ability cost could follow close to the same ratio. like 78% mana 22% stamina, (keep some for movement.  and all ability's
should be affordable when unlocked." / "make the split make sense for the class and how its played."

## Split per class (pack defaults, Server Setup editable)

| Class | Mana % | Stamina % | Why (how it plays) | Base Mana (L1) | Base Stamina bonus (L1) | Mana / level | Stamina / level |
|---|---|---|---|---|---|---|---|
| Mage | 75 | 25 | pure caster, stands back, every attack is a spell | 45 | +4 | 10 (kept) | 0.05 |
| Priest | 70 | 30 | caster + healer, moves a bit more to reach allies | 42 | +5 | 5 (kept) | 0.06 |
| Spellblade | 55 | 45 | melee mage: spells woven into sword swings | 33 | +7 | 4 (proposed) | 0.09 |
| Archer | 40 | 60 | kites and repositions all fight; trick arrows are part magic | 24 | +9 | 2 | 0.12 |
| Assassin | 40 | 60 | shadow tricks (Shadow Step, Vanishing Act) cost Mana; short bursts of movement | 24 | +9 | 2 | 0.12 |
| Monk | 35 | 65 | chi / Zen techniques, but the most mobile class (double jump, plunge, lunge) | 21 | +10 | 2 | 0.13 |
| Warrior | 35 | 65 | shouts, auras and shield moves (Rallying Guard, Challenge, Oath); slow tank, little running | 21 | +10 | 2 | 0.13 |
| Berserker | 20 | 80 | raw rage and fury, almost no magic | 12 | +12 | 2 | 0.16 |
| (no class) | - | - | | 25 (mana.base) | 0 | 0 | 0 |

Rule: level-1 power budget 60. Base Mana = 60 x Mana%. Base Stamina bonus (added on top of vanilla max Stamina, ~10) = 60 x Stamina% / 4
(one Stamina point is worth about 4 Mana, the vanilla pool is small). Stamina per level = Stamina% x 0.2 (Warrior +14 at 100).
Mining (+0.2 / level), class-skill all-stat boost and Overall Level stack on top.

## Ability costs follow the split

- An ability's cost is split close to the class ratio but tilted ~3 points toward Mana, so Stamina stays free for sprint / roll / jumps
  ("keep some for movement"): Mage 78 / 22, Priest 73 / 27, Spellblade 58 / 42, Archer + Assassin 43 / 57, Monk + Warrior 38 / 62,
  Berserker 23 / 77.
- Affordable when unlocked: at the class level an ability unlocks, its Mana cost <= the Mana pool AND its Stamina cost <= the Stamina pool
  at that level (main ability: at least 2 casts from full).
- Regen: in-combat Mana regen 75 %; Mana on hit (+1 per class-weapon hit, 0.5 s cooldown) for Warrior, Berserker, Monk, Assassin, Archer.
