# Monk - Self-speed disruptor

**Main role:** disruptor (speed + combos). **Second role:** single-target control. **Class skill:** *OPEN (new class skill)*. **Identity:**
graceful, fast, skips across the battlefield; replaces the unplayable Shaman slot (Skyy: our own classes, not Wynncraft's). Later class
idea: a Martial Artist with kicks + fists. *Numbers are placeholders. Legend in [README.md](README.md).*

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
  A1B -.-> M3["Duration+ | Power+ | Knockback+ | Ward"]
  A2 -.-> M4["Knockback+ | Ricochet | Slow | Power+"]
  A2X -.-> M5["Radius+ | Knockback+ | Slow | Haste"]
  classDef locked fill:#2e7d32,color:#fff,stroke:#1b5e20
  classDef proposed fill:#546e7a,color:#fff,stroke:#37474f
  classDef mods fill:#1a237e,color:#fff,stroke:#0d1442
  class A1,A2,BOc,FIc locked
  class A1A,A1B,A2X proposed
  class M1,M2,M3,M4,M5 mods
```

## Weapons

| Weapon | Attack | Charged attack / traversal | Status |
|---|---|---|---|
| Bo staff (vanilla Bamboo / Wood Bo staffs, metal tiers later) | Staff combo | **POLE-VAULT**: lunge forward and vault up and forward, kicking any enemy in the way for **2x** a normal hit (only the vault kicks). Then a **flowing fall** (15% slower, 15% less fall damage). **1 free mid-air jump** if it is your first jump after the vault. **Skipping bounds**: jump right as you land to bound forward (a bit higher than a normal jump, much farther, still slow-falling); chain as long as your timing holds; a timed landing takes **no fall damage** and the **farther you fell, the farther you bound**; bounds do no damage but cost more Stamina than a jump | LOCKED (Skyy 2026-10-04) |
| Fist weapons (cloth hand wraps, gauntlets, claws - one traversal) | Fast punch combo | **RISING STRIKE**: uppercut leap (~6 blocks up, a little forward) that knocks enemies in front up with you; **hang time** at the top slows you and them; hits on airborne enemies send them **flying**; **crouch near the top = PLUNGE PUNCH** - slam down, dragging the knocked-up enemies with you (the slam takes no fall damage but gives no Acrobatics XP); no plunge = a 15%-slower steerable fall (15% less fall damage) | LOCKED (Skyy 2026-10-04) |

## Abilities

### A1 - Flowing Form (LOCKED)
| | |
|---|---|
| Does | While active, enemies in an aura around you are **Awed**; only YOU gain flat move speed + attack speed; every hit you land = 1 combo, and each combo slows Awed enemies and lowers their defence; at **15 combo your flat buff doubles**; drains Mana AND Stamina over time; lasts 30 s (upgradable), ends early when either runs out; enemies stay Awed 10 s after it ends or after they leave the aura |
| Duration+ | longer (beyond 30 s) |
| Radius+ | bigger aura |
| Efficiency | slower Mana / Stamina drain |
| Power+ | bigger flat buff / stronger Awe per combo |

### A1-alt A - Hundred Fists (*proposed*, pick A or B)
| | |
|---|---|
| Does | Flowing Form where every 10 combo also releases a shockwave on all Awed enemies (one weapon hit each) |
| Power+ / Radius+ | stronger / wider shockwave |
| Echo | each shockwave repeats once, weaker |
| Efficiency | slower drain |

### A1-alt B - Still Water (*proposed*, pick A or B)
| | |
|---|---|
| Does | A calm stance for 10 s: you deflect projectiles from the front and counter melee hits (each blocked hit strikes back for one weapon hit); every counter adds Awe |
| Duration+ / Power+ | longer stance / stronger counters |
| Knockback+ | countered enemies are pushed away |
| Ward | a small shield while in the stance |

### A2 - Palm Strike (LOCKED)
| | |
|---|---|
| Does | Quick single-target strike: stun ~0.75 s + knockback; low cost (~8 Mana), short cooldown - spammable at higher levels |
| Knockback+ | farther knockback |
| Ricochet | the struck enemy is launched into others and stuns them too |
| Slow | the target stays slowed |
| Power+ | longer stun / more damage |

### A2-alt - Cyclone Kick (*proposed*)
| | |
|---|---|
| Does | A quick spinning kick that hits everything within 3 blocks and pushes it 5 blocks out (cheap) |
| Radius+ / Knockback+ | wider / farther |
| Slow | kicked enemies are slowed |
| Haste | speed boost after the kick |

## Modifier pool - pick 4 for each ability (2 equipped)

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

## Class tree paths (ideas - pick one)
- *Wind Dancer* - skipping, vaults and air combos.
- *Iron Fist* - fist damage, Plunge Punch, Palm Strike stuns.
- *Serene* - Still Water / Awe defence and control.

## Open
- The Monk's class skill name; A1-alt pair; A2-alt; engine checks (glide / slow fall, timed landing jump, mid-air jump, dragging mobs in
  the air, knockback on airborne mobs).

## Change log
- 2026-10-04: modifier pool table added under the abilities (Skyy).
- 2026-10-04: file created; Bo staff pole-vault + skipping bounds, fist Rising Strike + Plunge Punch, Flowing Form (Awe combo), Palm
  Strike - all LOCKED (Skyy).
