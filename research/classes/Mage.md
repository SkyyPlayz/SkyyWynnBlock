# 🔮 Mage - Burst damage (glass cannon)

| | |
|---|---|
| 🎯 **Main role** | Burst damage |
| 🎯 **Second role** | Survival |
| 📈 **Class skill** | Sorcery |
| 💬 **In one line** | Magic glass cannon (Skyy). |

- More damage per Mana than the Priest.

- Range + mobility. Low health and defence.

- Max Mana +10 per Sorcery level.

Numbers are placeholders. Labels: 🟢 Locked · 🔵 Proposed · 🟠 Open - see [README.md](README.md).

&nbsp;

## 🗺️ Map

```mermaid
flowchart TD
  CLS["MAGE<br/>Burst damage + survival"]
  CLS --> WPN["WEAPONS"]
  CLS --> ABL["ABILITIES<br/>own 4, equip 2"]
  WPN --> ST["Staffs<br/>Wood to Onyxium"]
  ST --> STa["Tap: quick shot<br/>no pierce, 24 blocks"]
  ST --> STc["Charged: TELEPORT 10 blocks<br/>+ light trail AoE"]
  WPN --> BK["Spellbooks"]
  BK --> BKa["Attack: book spell"]
  BK --> BKc["Charged: LEVITATE<br/>up 8 blocks, hover 3 s"]
  ABL --> A1["A1 Meteor"]
  A1 --> A1A["A1-alt A Starfall"]
  A1 --> A1B["A1-alt B Arcane Beam"]
  ABL --> A2["A2 Mana Barrier"]
  A2 --> A2X["A2-alt Frost Nova"]
  A1 -.-> M1["Radius+ | Power+ | Lingering | Split | Echo"]
  A1A -.-> M2["Duration+ | Radius+ | Echo | Power+"]
  A1B -.-> M3["Pierce | Duration+ | Power+ | Slow"]
  A2 -.-> M4["Duration+ | Power+ | Ward | Knockback+ | Follow"]
  A2X -.-> M5["Radius+ | Duration+ | Slow | Power+"]
  classDef locked fill:#2e7d32,color:#fff,stroke:#1b5e20
  classDef proposed fill:#546e7a,color:#fff,stroke:#37474f
  classDef mods fill:#1a237e,color:#fff,stroke:#0d1442
  class A1,A2,STa,STc,BKc,A1A,A1B,A2X locked
  class M1,M2,M3,M4,M5 mods
```

&nbsp;

## ⚔️ Weapons

### Staffs (Wood → Onyxium, SkyyArmory)

🟢 **Locked** (Skyy 2026-10-04)

- **Tap = quick shot:** no pierce, ~24 blocks range, 1/5 Mana. A little more damage per Mana than the Priest's wand.

- **Charged = TELEPORT** the way you look (up too). No void protection - part of the fun / challenge (Skyy 2026-10-07).

  - 10 blocks to start, upgradable in the tree. You can set a shorter custom distance there.

  - Leaves a **trail of light** along the path that hurts enemies in it for a few seconds (default: 1.5 blocks wide, 3 s, ~30% of the charged damage per second).

  - Never into blocks; over open void is allowed (no void protection, Skyy 2026-10-07).

  - No Stamina cost.

- 💡 **Idea for later (Skyy) - not decided yet:** special staffs whose quick shots pierce.

### Spellbooks

🟢 **Locked** (Skyy 2026-10-04)

- **Attack:** the book's spell.

- **Charged = LEVITATE:** float up ~8 blocks, hover ~3 s drifting the way you look, land with no fall damage.

&nbsp;

## ✨ Abilities

You own 4. You equip 2.

### A1 · Meteor

🟢 **Locked**

- **Does:** pick a spot up to 25 blocks away.

- After 1 s a meteor hits a **4-block area** for **~3x** a charged staff shot.

- **Levels:** +2% damage per level.

**Modifiers**

- ⭕ **Radius+** - bigger blast.

- 💪 **Power+** - more damage.

- 🔥 **Lingering** - the ground keeps burning for 3 s.

- 🔱 **Split** - 3 smaller meteors around the spot.

- 🔁 **Echo** - a second, weaker meteor hits the same spot 1 s later · each level: stronger echo.

### A1-alt A · Starfall

🟢 **Locked** (Skyy 2026-10-09: both alternatives kept)

- **Does:** for 3 s, **12 stars** fall over a 6-block area (each ~40% of a Meteor).

- More total damage, spread out.

**Modifiers**

- ⏳ **Duration+** / ⭕ **Radius+** - more stars / bigger area.

- 🔁 **Echo** - a second, weaker shower right after.

- 💪 **Power+** - stronger stars.

### A1-alt B · Arcane Beam

🟢 **Locked** (Skyy 2026-10-09: both alternatives kept)

- **Does:** channel a **20-block beam** for up to 3 s.

- Its damage ramps from 1x to 3x per second. Huge single-target burst.

**Modifiers**

- 📌 **Pierce** - the beam hits +1 enemy behind the first per level.

- ⏳ **Duration+** - channel longer.

- 💪 **Power+** - faster ramp.

- 🐌 **Slow** - enemies in the beam are slowed.

### A2 · Mana Barrier

🟢 **Locked**

- **Does:** drops a **barrier dome on the ground** for **12 s** (at least - Skyy 2026-10-07). While you stand inside it, damage you take **drains Mana instead of Health** (1 Mana per 2 HP). The dome stays where you cast it. **Look:** clearly visible but easy to see through - a faint, mostly transparent tint with a soft brighter edge, never blocking the view or flashing (Skyy 2026-10-07).

- It ends early if your Mana runs out.

**Modifiers**

- ⏳ **Duration+** - lasts longer.

- 💪 **Power+** - better ratio (more HP per Mana).

- 🛡️ **Ward** - allies within 4 blocks also get a small shield.

- 👣 **Follow** - the dome moves with you instead of staying where you cast it (also a skill-tree upgrade).

- 💥 **Knockback+** - the barrier bursts when it ends, pushing enemies away.

### A2-alt · Frost Nova

🟢 **Locked** (Skyy 2026-10-09)

- **Does:** **freeze** enemies within 5 blocks for 2 s (a hit breaks it after 1 s).

- Then **Chill** them for 3 s. Escape by control.

**Modifiers**

- ⭕ **Radius+** / ⏳ **Duration+** - bigger / longer freeze.

- 🐌 **Slow** - stronger Chill.

- 💪 **Power+** - damage on freeze + break.

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

Ideas - pick one. The Mage tree already has three lanes.

- **Riftwalker** - teleport upgrades (distance, trail damage), mobility.

- **Light Bender** - light / radiant damage, trail and Starfall effects.

- **Arcanist** - raw Mana power, Barrier and Beam.

&nbsp;

## 🟠 Open

- Nothing open right now (all ability picks locked 2026-10-09).

&nbsp;

## 📜 Change log

- 2026-10-08 Skyy: melee Mana costs dropped, Stamina costs added (every class now has its own Mana / Stamina split; Mage split 75 / 25 (costs 78 / 22)): Meteor 23 Mana + 2 Stamina (was 30 Mana), Mana Barrier 16 Mana + 1 Stamina (was 20 Mana), Frost Nova 19 Mana + 1 Stamina (was 24 Mana), Starfall 28 Mana + 2 Stamina (was 36 Mana), Arcane Beam 23 Mana + 2 Stamina (was 30 Mana) - full table in research/cloud/Class-Ability-Spec-Draft.md section 2; pools and the why per class in research/Class-Power-Split.md.

- 2026-10-07: dome look = visible but easy to see through, not distracting (Skyy: "make sure the dome is visible, but still easily see through so it isnt distracting or disruptive.").

- 2026-10-07: Mana Barrier = a placed dome on the ground; Follow modifier / tree upgrade makes it move with you (Skyy picked "Placed dome + Follow").

- 2026-10-07: Mana Barrier lasts at least 12 s (was 6 s), still drains Mana instead of Health (Skyy: "mana barier should last at least 12 seconds keep the mana drain instead of hp").

- 2026-10-07: Echo modifier added to Meteor too (Skyy: "the modifier, echo.  that should be available on the metro too.").

- 2026-10-05: refined for easy reading (same facts, new layout).

- 2026-10-04: modifier pool table added under the abilities (Skyy).

- 2026-10-04: file created; staff Teleport + trail, spellbook Levitate, quick-shot range, Meteor + Mana Barrier LOCKED (Skyy).
