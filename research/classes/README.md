# SkyWynn classes - one file per class

Open a class file on the right while we talk; every change goes into the file (and its change log at the bottom), not just chat.

| Class | Main role + second role | Weapons | File |
|---|---|---|---|
| Warrior | Tank + crowd control | Swords (incl. longswords), Spears | [Warrior.md](Warrior.md) |
| Archer | Crowd control + focus marker | Shortbows, Crossbows | [Archer.md](Archer.md) |
| Mage | Burst damage + survival (glass cannon) | Staffs, Spellbooks | [Mage.md](Mage.md) |
| Priest | Healer + protector | Wands, Soul Orb | [Priest.md](Priest.md) |
| Berserker | Damage buffer + sustained melee | Axes (incl. battleaxes), Maces / clubs | [Berserker.md](Berserker.md) |
| Monk | Self-speed disruptor | Bo staff, Fist weapons | [Monk.md](Monk.md) |
| Assassin | Priority killer + debuffer | Daggers, Kunai | [Assassin.md](Assassin.md) |

**Legend used in every file:** **LOCKED** = Skyy decided; *proposed* = first draft to refine; **OPEN** = needs a decision.
All numbers are placeholders until the build spec. In the graphs: green = locked, grey = proposed, orange = open, blue = modifiers.

## Rules every class follows (Skyy, 2026-10-04 - OPEN-QUESTIONS "LOCKED 2026-10-04")

- **2 weapon types per class, no sharing between classes** (sharing may come later with more classes).
- **Each weapon has its own traversal** = its charged attack. Most vanilla weapons already have one; magic and new weapons get custom ones.
- **Abilities:** A1 first -> A2 -> the A2 swap-out -> later ONE of two improved A1 alternatives (picking one locks out the other).
  5 designed per class, 4 owned by a character, **2 equipped** (the two rune slots).
- **Each ability levels up by use** (a little stronger each level, only uses that do something count); its levels give points for its
  **own modifier tree**: 4 modifiers per ability, **2 equipped**, no doubling the same modifier (level it up instead).
- **Shared modifier pool** - many abilities can offer the same modifier, but each ability unlocks and levels it separately.
- **Class tree** = Wynncraft-style **paths** that change HOW an ability works (choose one, the others lock out), e.g. the Priest shield
  damages enemies that touch it, then pick 1 of 5 elements. Modifiers live in the ability tree, not the class tree.
- Later: up to 3 saved rune loadouts per class, swapped with a hotkey.

## Shared modifier pool

| Modifier | What it does | Each level adds |
|---|---|---|
| Duration+ | lasts longer | more time |
| Radius+ | bigger area | more blocks |
| Power+ | stronger main effect (damage, heal, shield, buff) | more % |
| Efficiency | costs less Mana / Stamina | lower cost |
| Split | splits into 3 weaker copies (projectiles, lines) | stronger copies |
| Ricochet | PROJECTILES only: the shot flies on to the next enemy after a hit (walls block it, it can miss) | +1 bounce |
| Pierce | passes through enemies | +1 enemy |
| Chain | EFFECTS only (heals, buffs, debuffs, poison, hooks): jumps instantly to the next target in range - enemies, or allies for support | +1 jump |
| Lingering | leaves a zone behind (fire, poison, light) | longer zone |
| Slow | adds a slow | stronger slow |
| Knockback+ | pushes enemies away | farther |
| Pull | draws enemies in | stronger pull |
| Follow | a placed zone moves with you instead | bigger zone |
| Leech | heals you for part of the damage | more % |
| Ward | adds a small shield (you, or allies for support abilities) | bigger shield |
| Haste | attack + move speed for a few seconds after use | longer |
| Echo | repeats once after 1 s at reduced strength | stronger echo |

Other files: [research/Class-Roles-Ideas.md](../Class-Roles-Ideas.md) (RotMG research, 31 class ideas for later), OPEN-QUESTIONS.md
(every decision word for word).
