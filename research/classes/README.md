# 🗡️ SkyWynn classes

One file per class. Edit the class file while we talk.

Every change goes into the file and its change log, not just chat.

Easy-read pages (big text, cards): open `html/index.html` in a browser.

After editing a file, run `python tools/class_pages.py` to rebuild the pages.

&nbsp;

## 👥 The classes

| Class | Main role + second role | Weapons | File |
|---|---|---|---|
| 🛡️ Warrior | Tank + crowd control | Swords (incl. longswords), Spears | [Warrior.md](Warrior.md) |
| 🏹 Archer | Crowd control + focus marker | Shortbows, Crossbows | [Archer.md](Archer.md) |
| 🔮 Mage | Burst damage + survival (glass cannon) | Staffs, Spellbooks | [Mage.md](Mage.md) |
| ✨ Priest | Healer + protector | Wands, Soul Orb | [Priest.md](Priest.md) |
| 🪓 Berserker | Damage buffer + sustained melee | Axes (incl. battleaxes), Maces / clubs | [Berserker.md](Berserker.md) |
| 🥋 Monk | Self-speed disruptor | Bo staff, Fist weapons | [Monk.md](Monk.md) |
| 🗡️ Assassin | Priority killer + debuffer | Daggers, Kunai | [Assassin.md](Assassin.md) |

&nbsp;

## 🏷️ Labels used in every file

- 🟢 **Locked** = Skyy decided.

- 🔵 **Proposed** = a first draft to refine.

- 🟠 **Open** = needs a decision.

- All numbers are placeholders until the build spec.

- In the map diagrams: green = locked, grey = proposed, orange = open, blue = modifiers.

&nbsp;

## 📏 Rules every class follows

🟢 Locked by Skyy, 2026-10-04 (word for word in `docs/answered/classes.md`).

- **2 weapon types per class.** No sharing between classes (sharing may come later with more classes).

- **Each weapon has its own traversal** = its charged attack. Most vanilla weapons already have one. Magic and new weapons get custom ones.

- **Ability order:** A1 first → A2 → the A2 swap-out → later ONE of two improved A1 alternatives (picking one locks out the other).

- **5 designed per class, 4 owned by a character, 2 equipped** (the two rune slots).

- **Each ability levels up by use.** A little stronger each level. Only uses that do something count.

- **Its levels give points for its own modifier tree:** 4 modifiers per ability, **2 equipped**. No doubling the same modifier - level it up instead.

- **Shared modifier pool:** many abilities can offer the same modifier, but each ability unlocks and levels it separately.

- **Class tree = Wynncraft-style paths** that change HOW an ability works. Choose one, the others lock out. Example: the Priest shield damages enemies that touch it, then you pick 1 of 5 elements.

- Modifiers live in the ability tree, not the class tree.

- **Later:** up to 3 saved rune loadouts per class, swapped with a hotkey.

&nbsp;

## 🧩 Modifier pool

Every ability offers 4 of these. You equip 2.

Each modifier: **what it does** · what each level adds.

<!-- POOL START - tools/class_pages.py copies this block into every class file (python tools/class_pages.py --sync-pool) -->
- ⏳ **Duration+** - lasts longer · each level: more time.

- ⭕ **Radius+** - bigger area · each level: more blocks.

- 💪 **Power+** - stronger main effect (damage, heal, shield, buff) · each level: more %.

- 💧 **Efficiency** - costs less Mana / Stamina · each level: lower cost.

- 🔱 **Split** - splits into 3 weaker copies (projectiles, lines) · each level: stronger copies.

- 🎱 **Ricochet** - PROJECTILES only: the shot flies on to the next enemy after a hit (walls block it, it can miss) · each level: +1 bounce.

- 📌 **Pierce** - passes through enemies · each level: +1 enemy.

- ⛓️ **Chain** - EFFECTS only (heals, buffs, debuffs, poison, hooks): jumps instantly to the next target in range - enemies, or allies for support · each level: +1 jump.

- 🔥 **Lingering** - leaves a zone behind (fire, poison, light) · each level: longer zone.

- 🐌 **Slow** - adds a slow · each level: stronger slow.

- 💥 **Knockback+** - pushes enemies away · each level: farther.

- 🧲 **Pull** - draws enemies in · each level: stronger pull.

- 👣 **Follow** - a placed zone moves with you instead · each level: bigger zone.

- 🩸 **Leech** - heals you for part of the damage · each level: more %.

- 🛡️ **Ward** - adds a small shield (you, or allies for support abilities) · each level: bigger shield.

- ⚡ **Haste** - attack + move speed for a few seconds after use · each level: longer.

- 🔁 **Echo** - repeats once after 1 s at reduced strength · each level: stronger echo.
<!-- POOL END -->

&nbsp;

## 📚 Other files

- `research/Class-Roles-Ideas.md` - RotMG research, 31 class ideas for later ([open](../Class-Roles-Ideas.md)).

- `docs/answered/classes.md` - every class decision word for word.
