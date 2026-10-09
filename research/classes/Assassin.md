# 🗡️ Assassin - Priority killer

| | |
|---|---|
| 🎯 **Main role** | Priority killer (burst on one target) |
| 🎯 **Second role** | Debuffer |
| 📈 **Class skill** | Assassination |
| 💬 **In one line** | Cloak, teleport in, strike, teleport out. |

Numbers are placeholders. Labels: 🟢 Locked · 🔵 Proposed · 🟠 Open - see [README.md](README.md).

&nbsp;

## 🗺️ Map

```mermaid
flowchart TD
  CLS["ASSASSIN<br/>Priority killer + debuffer"]
  CLS --> WPN["WEAPONS"]
  CLS --> ABL["ABILITIES<br/>own 4, equip 2"]
  WPN --> DG["Daggers"]
  DG --> DGa["Attack: fast stabs<br/>backstab bonus"]
  DG --> DGc["Charged: Pounce<br/>vanilla traversal"]
  WPN --> KN["Kunai"]
  KN --> KNa["Attack: throw"]
  KN --> KNc["Charged: THROW + TELEPORT<br/>hold right-click = return"]
  ABL --> A1["A1 Cloak + First Strike"]
  A1 --> A1A["A1-alt A Shadow Clone"]
  A1 --> A1B["A1-alt B Vanishing Act"]
  ABL --> A2["A2 Toxin"]
  A2 --> A2X["A2-alt God Killer"]
  A1 -.-> M1["Duration+ | Efficiency | Power+ | Haste"]
  A1A -.-> M2["Duration+ | Power+ | Split | Knockback+"]
  A1B -.-> M3["Radius+ | Duration+ | Slow | Efficiency"]
  A2 -.-> M4["Radius+ | Duration+ | Lingering | Chain"]
  A2X -.-> M5["Power+ | Duration+ | Efficiency | Haste | Echo"]
  classDef locked fill:#2e7d32,color:#fff,stroke:#1b5e20
  classDef proposed fill:#546e7a,color:#fff,stroke:#37474f
  classDef mods fill:#1a237e,color:#fff,stroke:#0d1442
  class A1,A2,A2X,DGc,KNc locked
  class A1A,A1B proposed
  class M1,M2,M3,M4,M5 mods
```

&nbsp;

## ⚔️ Weapons

### Daggers

🟢 **Locked** - vanilla for now (Skyy: change later)

- **Attack:** vanilla fast stabs. Vanilla backstab bonus from behind.

- **Charged:** vanilla **Pounce** (a sweep / stab lunge).

- 🟢 **Next (Skyy 2026-10-07): Shadow Step** replaces Pounce - vanish (a fading shadow stays), appear behind the mob nearest your aim within 24 blocks, facing its back; next hit = guaranteed backstab + a small bonus. No mob: step 18 blocks where you look (air and void are fair game). Spec: `research/Shadow-Step-Spec.md`.

### Kunai

🟢 **Locked** (Skyy 2026-10-04)

- **Attack:** throw (vanilla has no charged kunai attack).

- **Charged = THROW + TELEPORT:** hold to charge, throw, and you **teleport to where it lands** (up to ~20 blocks).

- If it flies out of range, you appear where it left your range.

- **Hold right-click to RETURN** to where you were before, with an AoE knockback (default: the return works for ~8 s).

&nbsp;

## ✨ Abilities

You own 4. You equip 2.

### A1 · Cloak + First Strike

🟢 **Locked**

- **Does:** **invisible** for a limited time (breaks when you attack).

- **First Strike** is not tied to the cloak: even if the cloak runs out, your next hit gets **+100% crit chance**.

- **Crit rule (all classes):** max crit chance becomes **150%**. Above 100% = overcrit. Above 200% = **triple crit**.

  - At the cap: a 50% overcrit chance. With First Strike, 250% = a 50% chance of a triple crit (a SkyyGear change).

**Modifiers**

- ⏳ **Duration+** - longer cloak.

- 💧 **Efficiency** - cheaper.

- 💪 **Power+** - more First Strike crit damage.

- ⚡ **Haste** - move speed while cloaked.

### A1-alt A · Shadow Clone

🔵 **Proposed** - pick A or B

- **Does:** cloak and leave a **decoy** that mobs attack for 5 s.

- When it ends, the clone bursts for damage.

- Engine check: can a mod pick a mob's target?

**Modifiers**

- ⏳ **Duration+** / 💪 **Power+** - longer clone / more clone HP + burst.

- 🔱 **Split** - 2 clones.

- 💥 **Knockback+** - the burst pushes enemies away.

### A1-alt B · Vanishing Act

🔵 **Proposed** - pick A or B

- **Does:** an instant short cloak (3 s) + a **4-block smoke cloud**.

- Enemies inside lose track of you for 2 s and are slowed.

- First Strike as A1.

**Modifiers**

- ⭕ **Radius+** / ⏳ **Duration+** - bigger / longer smoke.

- 🐌 **Slow** - stronger slow in the smoke.

- 💧 **Efficiency** - cheaper.

### A2 · Toxin

🟢 **Locked**

- **Does:** throw a vial: a **4-block poison cloud** for 5 s.

- Enemies are **Poisoned** (damage over time) + **Weakened** (deal 15% less damage).

**Modifiers**

- ⭕ **Radius+** / ⏳ **Duration+** - bigger / longer cloud.

- 🔥 **Lingering** - the ground stays poisoned after the cloud.

- ⛓️ **Chain** - when a poisoned enemy dies, the poison jumps to the nearest enemy.

### A2-alt · God Killer

🟢 **Locked**

- **Does:** your next attack on a **boss or mini-boss** does **2x** damage, **3x** if it is a backstab.

- Stacks with First Strike.

**Modifiers**

- 💪 **Power+** - bigger multiplier.

- ⏳ **Duration+** - the "next attack" window lasts longer.

- 💧 **Efficiency** - cheaper.

- ⚡ **Haste** - speed boost after the strike to get away.

- 🔁 **Echo** - the empowered strike repeats once 1 s later at reduced strength · each level: stronger echo.

&nbsp;

## 🧩 Modifier pool

Each ability offers 4 of these. You equip 2.

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

## 🌳 Class tree paths

Ideas - pick one.

- **Shadow** - cloak, First Strike, God Killer.

- **Venom** - poison stacks, spreading Toxin, Weaken.

- **Blink** - kunai range, return knockback, extra teleports.

&nbsp;

## 🟠 Open

- A1-alt pair (Shadow Clone / Vanishing Act proposed).

&nbsp;

## 📜 Change log

- 2026-10-08 Skyy: melee Mana costs dropped, Stamina costs added (every class now has its own Mana / Stamina split; Assassin split 40 / 60 (costs 43 / 57)): Cloak + First Strike 6 Mana + 2 Stamina (was 14 Mana), Toxin 5 Mana + 2 Stamina (was 12 Mana), God Killer 6 Mana + 2 Stamina (was 14 Mana), Vanishing Act 7 Mana + 2 Stamina (was 16 Mana), Shadow Clone 9 Mana + 3 Stamina (was 20 Mana) - full table in research/cloud/Class-Ability-Spec-Draft.md section 2; pools and the why per class in research/Class-Power-Split.md.

- 2026-10-05: refined for easy reading (same facts, new layout).

- 2026-10-04: modifier pool table added under the abilities (Skyy).

- 2026-10-07: God Killer gains the Echo modifier (Skyy: "for the assassin, id give god killer the echo modification").

- 2026-10-04: file created; daggers vanilla, kunai throw-teleport + return, Cloak + First Strike (crit cap 150%, triple crit), Toxin, God Killer - all LOCKED (Skyy).
