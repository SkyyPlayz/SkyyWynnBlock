# 🥋 Monk - Self-speed disruptor

| | |
|---|---|
| 🎯 **Main role** | Disruptor (speed + combos) |
| 🎯 **Second role** | Single-target control |
| 📈 **Class skill** | 🟠 OPEN (a new class skill) |
| 💬 **In one line** | Graceful, fast, skips across the battlefield. |

- Replaces the unplayable Shaman slot (Skyy: our own classes, not Wynncraft's).

- Later class idea: a Martial Artist with kicks + fists.

Numbers are placeholders. Labels: 🟢 Locked · 🔵 Proposed · 🟠 Open - see [README.md](README.md).

&nbsp;

## 🗺️ Map

```mermaid
flowchart TD
  CLS["MONK<br/>Self-speed disruptor"]
  CLS --> WPN["WEAPONS"]
  CLS --> ABL["ABILITIES<br/>own 4, equip 2"]
  WPN --> BO["Bo staff"]
  BO --> BOa["Attack: staff combo"]
  BO --> BOc["Charged: POLE-VAULT<br/>kick 2x + skipping bounds"]
  WPN --> FI["Fist weapons<br/>wraps, gauntlets, claws"]
  FI --> FIa["Attack: fast punches"]
  FI --> FIc["Charged: RISING STRIKE<br/>uppercut + Plunge Punch"]
  ABL --> A1["A1 Flowing Form"]
  A1 --> A1A["A1-alt A Hundred Fists"]
  A1 --> A1B["A1-alt B Still Water"]
  ABL --> A2["A2 Palm Strike"]
  A2 --> A2X["A2-alt Cyclone Kick"]
  A1 -.-> M1["Duration+ | Radius+ | Efficiency | Power+"]
  A1A -.-> M2["Power+ | Radius+ | Echo | Efficiency"]
  A1B -.-> M3["Duration+ | Power+ | Knockback+ | Ward | Echo"]
  A2 -.-> M4["Knockback+ | Ricochet | Slow | Power+ | Echo"]
  A2X -.-> M5["Radius+ | Knockback+ | Slow | Haste"]
  classDef locked fill:#2e7d32,color:#fff,stroke:#1b5e20
  classDef proposed fill:#546e7a,color:#fff,stroke:#37474f
  classDef mods fill:#1a237e,color:#fff,stroke:#0d1442
  class A1,A2,BOc,FIc,A1A,A1B,A2X locked
  class M1,M2,M3,M4,M5 mods
```

&nbsp;

## ⚔️ Weapons

### Bo staff (vanilla Bamboo / Wood Bo staffs, metal tiers later)

🟢 **Locked** (Skyy 2026-10-04)

- **Attack:** staff combo.

- **Charged = POLE-VAULT:** lunge forward and vault up and forward. It kicks any enemy in the way for **2x** a normal hit (only the vault kicks).

- **Flowing fall:** 15% slower, 15% less fall damage.

- **1 free mid-air jump** if it is your first jump after the vault.

- **Skipping bounds:** jump right as you land to bound forward - a bit higher than a normal jump, much farther, still slow-falling.

  - Chain them as long as your timing holds.

  - A timed landing takes **no fall damage**, and the **farther you fell, the farther you bound**.

  - Bounds do no damage but cost more Stamina than a jump.

### Fist weapons (cloth hand wraps, gauntlets, claws - one traversal)

🟢 **Locked** (Skyy 2026-10-04)

- **Attack** (Skyy 2026-10-07, lighter = faster; wraps + gauntlets hit ONE enemy, claws hit several):
  - **Hand wraps:** several jabs per click, a power hit on the Nth jab, no gap after it (fast enough to stunlock one enemy; bosses + mini-bosses break out by hitting you after 3 s of stunlock, 3 s more per extra player stunlocking them - 2 players = 6 s - Skyy 2026-10-07) - T1 Linen + T2 Cotton: 2 jabs per click, power hit on jab 6 · T3 Silk: 2 per click, power on 4 · T4 Cindercloth: 3 per click, power on 6 · T5 Shadoweave: 5 per click, power on the 5th.
  - **Gauntlets** (the Monk's heavy weapon): 1 jab per click, a chain of 4 with a harder finisher; more damage per hit; speed a little faster than a vanilla sword, a little slower than a vanilla dagger; after the finisher there is always a gap long enough for most mobs to hit back.
  - **Claws** (later): a little faster than gauntlets, 1 click = 1 slash, fast chained slashes, no power hit, hits several enemies (less DPS); higher tiers = more damage + a wider (and slightly longer) slash.

- **Charged = RISING STRIKE:** an uppercut leap (~6 blocks up, a little forward) that knocks enemies in front up with you.

- **Hang time** at the top slows you and them.

- Hits on airborne enemies send them **flying**.

- **Crouch near the top = PLUNGE PUNCH:** slam down, dragging the knocked-up enemies with you. The slam takes no fall damage but gives no Acrobatics XP.

- No plunge = a 15%-slower steerable fall (15% less fall damage).

&nbsp;

## ✨ Abilities

You own 4. You equip 2.

### A1 · Flowing Form

🟢 **Locked**

- **Does:** while active, enemies in an aura around you are **Awed**.

- **Combo stacks** (Skyy 2026-10-07): every hit you land = **1 combo stack**, max **20**. Each stack raises YOUR **move speed + attack speed** (default +2% move, +1.5% attack per stack = +40% / +30% at 20). **Each stack decays 5 s after it was gained**, so you only reach / stay at 20 by hitting non-stop.

- **Awed enemies** get **distracted for a moment** when they become Awed (they lose their target, ~1 s), then take **lowered defence and slightly lower move speed per TOTAL combo** you landed during the ability (default -1% defence, -0.5% move per total combo; caps -20% / -10%).

- Costs 2 Mana + 1 Stamina to start, then drains **Mana AND Stamina** over time (0.65 Mana + 0.25 Stamina per second; 2026-10-08). Lasts 30 s (upgradable). Ends early when either runs out.

- Enemies stay Awed 10 s after it ends or after they leave the aura.

**Modifiers**

- ⏳ **Duration+** - longer (beyond 30 s).

- ⭕ **Radius+** - bigger aura.

- 💧 **Efficiency** - slower Mana / Stamina drain.

- 💪 **Power+** - bigger buff per combo stack / stronger Awe per total combo.

### A1-alt A · Hundred Fists

🟢 **Locked** (Skyy 2026-10-09: both alternatives kept)

- **Does:** Flowing Form where every **10 combo** also releases a **shockwave** on all Awed enemies (one weapon hit each).

**Modifiers**

- 💪 **Power+** / ⭕ **Radius+** - stronger / wider shockwave.

- 🔁 **Echo** - each shockwave repeats once, weaker.

- 💧 **Efficiency** - slower drain.

### A1-alt B · Still Water

🟢 **Locked** (Skyy 2026-10-09: both alternatives kept)

- **Does:** a calm stance for 10 s.

- You **deflect projectiles** from the front and **counter melee hits** (each blocked hit strikes back for one weapon hit).

- Every counter adds Awe.

**Modifiers**

- ⏳ **Duration+** / 💪 **Power+** - longer stance / stronger counters.

- 💥 **Knockback+** - countered enemies are pushed away.

- 🛡️ **Ward** - a small shield while in the stance.

- 🔁 **Echo** - when the stance ends, the melee COUNTERS come back for ~3 s while you move freely: break stance to attack and still block + counter. A block + counter interrupts your own attack - get hit mid-swing and you block and counter instead · each level: a longer echo.

### A2 · Palm Strike

🟢 **Locked**

- **Does:** a quick single-target strike: **stun ~0.75 s + knockback**.

- Low cost (3 Mana + 1 Stamina since 2026-10-08, was ~8 Mana), short cooldown - spammable at higher levels.

**Modifiers**

- 💥 **Knockback+** - farther knockback.

- 🎱 **Ricochet** - the struck enemy is launched into others and stuns them too.

- 🐌 **Slow** - the target stays slowed.

- 💪 **Power+** - longer stun / more damage.

- 🔁 **Echo** - a second, weaker palm strike hits the same target 1 s later · each level: stronger echo.

### A2-alt · Cyclone Kick

🟢 **Locked** (Skyy 2026-10-09)

- **Does:** a quick **spinning kick** that hits everything within 3 blocks and pushes it 5 blocks out (cheap).

**Modifiers**

- ⭕ **Radius+** / 💥 **Knockback+** - wider / farther.

- 🐌 **Slow** - kicked enemies are slowed.

- ⚡ **Haste** - speed boost after the kick.

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

- **Wind Dancer** - skipping, vaults and air combos.

- **Iron Fist** - fist damage, Plunge Punch, Palm Strike stuns.

- **Serene** - Still Water / Awe defence and control.

&nbsp;

## 🟠 Open

- The Monk's class skill name: LOCKED "Zen" (rename pending in the next SkyySkills round).



- Engine checks: glide / slow fall, timed landing jump, mid-air jump, dragging mobs in the air, knockback on airborne mobs.

&nbsp;

## 📜 Change log

- 2026-10-08 Skyy: melee Mana costs dropped, Stamina costs added (every class now has its own Mana / Stamina split; Monk split 35 / 65 (costs 38 / 62)): Flowing Form 2 Mana + 1 Stamina to start, then 0.65 Mana + 0.25 Stamina per second (was 6, then 0.5 + 0.3); Hundred Fists 3 + 1, then 0.7 + 0.3 per second (was 8, then 0.6 + 0.3); Still Water 7 Mana + 3 Stamina (was 18 Mana), Palm Strike 3 Mana + 1 Stamina (was 8 Mana), Cyclone Kick 4 Mana + 2 Stamina (was 10 Mana) - full table in research/cloud/Class-Ability-Spec-Draft.md section 2; pools and the why per class in research/Class-Power-Split.md.

- 2026-10-05: refined for easy reading (same facts, new layout).

- 2026-10-04: modifier pool table added under the abilities (Skyy).

- 2026-10-07: Flowing Form reworked into combo stacks (each hit +1, max 20, 5 s decay per stack, speed buffs per stack; Awed = distracted, then defence / speed debuff per total combo) (Skyy).

- 2026-10-07: Still Water gains Echo (counters return ~3 s while moving; block + counter interrupts your attack) (Skyy).

- 2026-10-07: Palm Strike gains Echo (Skyy: "give monks palm strike echo too"); fist attacks, stunlock breakout, gauntlet speed (Skyy).

- 2026-10-04: file created; Bo staff pole-vault + skipping bounds, fist Rising Strike + Plunge Punch, Flowing Form (Awe combo), Palm Strike - all LOCKED (Skyy).
