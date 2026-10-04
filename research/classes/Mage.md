# Mage - Burst damage (glass cannon)

**Main role:** burst damage. **Second role:** survival. **Class skill:** Sorcery. **Identity (Skyy):** magic glass cannon - more damage per
Mana than the Priest, range + mobility, low health and defence. Max Mana +10 per Sorcery level. *Numbers are placeholders. Legend in [README.md](README.md).*

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
  A1 -.-> M1["Radius+ | Power+ | Lingering | Split"]
  A1A -.-> M2["Duration+ | Radius+ | Echo | Power+"]
  A1B -.-> M3["Pierce | Duration+ | Power+ | Slow"]
  A2 -.-> M4["Duration+ | Power+ | Ward | Knockback+"]
  A2X -.-> M5["Radius+ | Duration+ | Slow | Power+"]
  classDef locked fill:#2e7d32,color:#fff,stroke:#1b5e20
  classDef proposed fill:#546e7a,color:#fff,stroke:#37474f
  classDef mods fill:#1a237e,color:#fff,stroke:#0d1442
  class A1,A2,STa,STc,BKc locked
  class A1A,A1B,A2X proposed
  class M1,M2,M3,M4,M5 mods
```

## Weapons

| Weapon | Attack | Charged attack / traversal | Status |
|---|---|---|---|
| Staffs (Wood -> Onyxium, SkyyArmory) | **Tap = quick shot**: no pierce, ~24 blocks range, 1/5 Mana, a little more damage per Mana than the Priest's wand | **TELEPORT** the way you look (up too): 10 blocks to start, upgradable in the tree, and you can set a shorter custom distance there; leaves a **trail of light** along the path that hurts enemies in it for a few seconds (*default:* 1.5 blocks wide, 3 s, ~30% of the charged damage per second). Never into blocks or out over open void. No Stamina cost | LOCKED (Skyy 2026-10-04) |
| Spellbooks | The book's spell | **LEVITATE**: float up ~8 blocks, hover ~3 s drifting the way you look, land with no fall damage | LOCKED (Skyy 2026-10-04) |

Later (Skyy): special staffs whose quick shots pierce.

## Abilities

### A1 - Meteor (LOCKED)
| | |
|---|---|
| Does | Pick a spot up to 25 blocks away: after 1 s a meteor hits a 4-block area for ~3x a charged staff shot |
| Levels | +2% damage per level |
| Radius+ | bigger blast |
| Power+ | more damage |
| Lingering | the ground keeps burning for 3 s |
| Split | 3 smaller meteors around the spot |

### A1-alt A - Starfall (*proposed*, pick A or B)
| | |
|---|---|
| Does | For 3 s, 12 stars fall over a 6-block area (each ~40% of a Meteor) - more total damage, spread out |
| Duration+ / Radius+ | more stars / bigger area |
| Echo | a second, weaker shower right after |
| Power+ | stronger stars |

### A1-alt B - Arcane Beam (*proposed*, pick A or B)
| | |
|---|---|
| Does | Channel a 20-block beam for up to 3 s; its damage ramps from 1x to 3x per second - huge single-target burst |
| Pierce | the beam hits +1 enemy behind the first per level |
| Duration+ | channel longer |
| Power+ | faster ramp |
| Slow | enemies in the beam are slowed |

### A2 - Mana Barrier (LOCKED)
| | |
|---|---|
| Does | For 6 s, damage you take drains Mana instead of Health (1 Mana per 2 HP); it ends early if your Mana runs out |
| Duration+ | lasts longer |
| Power+ | better ratio (more HP per Mana) |
| Ward | allies within 4 blocks also get a small shield |
| Knockback+ | the barrier bursts when it ends, pushing enemies away |

### A2-alt - Frost Nova (*proposed*)
| | |
|---|---|
| Does | Freeze enemies within 5 blocks for 2 s (a hit breaks it after 1 s), then Chill them for 3 s - escape by control |
| Radius+ / Duration+ | bigger / longer freeze |
| Slow | stronger Chill |
| Power+ | damage on freeze + break |

## Modifier pool - pick 4 for each ability (2 equipped)

| Modifier | What it does | Each level adds |
|---|---|---|
| Duration+ | lasts longer | more time |
| Radius+ | bigger area | more blocks |
| Power+ | stronger main effect (damage, heal, shield, buff) | more % |
| Efficiency | costs less Mana / Stamina | lower cost |
| Split | splits into 3 weaker copies (projectiles, lines) | stronger copies |
| Ricochet | bounces to more targets | +1 bounce |
| Pierce | passes through enemies | +1 enemy |
| Chain | jumps between nearby enemies or allies | +1 jump |
| Lingering | leaves a zone behind (fire, poison, light) | longer zone |
| Slow | adds a slow | stronger slow |
| Knockback+ | pushes enemies away | farther |
| Pull | draws enemies in | stronger pull |
| Follow | a placed zone moves with you instead | bigger zone |
| Leech | heals you for part of the damage | more % |
| Ward | adds a small shield (you, or allies for support abilities) | bigger shield |
| Haste | attack + move speed for a few seconds after use | longer |
| Echo | repeats once after 1 s at reduced strength | stronger echo |

## Class tree paths (ideas - pick one; the Mage tree already has three lanes)
- *Riftwalker* - teleport upgrades (distance, trail damage), mobility.
- *Light Bender* - light / radiant damage, trail and Starfall effects.
- *Arcanist* - raw Mana power, Barrier and Beam.

## Open
- Mage A2-alt (Frost Nova proposed); A1-alt pair.

## Change log
- 2026-10-04: modifier pool table added under the abilities (Skyy).
- 2026-10-04: file created; staff Teleport + trail, spellbook Levitate, quick-shot range, Meteor + Mana Barrier LOCKED (Skyy).
