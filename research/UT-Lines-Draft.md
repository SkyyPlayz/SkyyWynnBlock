# UT lines - DRAFT for the 5 Armory UT sets + a Zone 4 Cloth candidate (Skyy decides)

DRAFT - nothing here is shipped, recorded as a decision, or in any config. Written 2026-10-17 by a research agent from
`research/Pack-Drops-Spec.md` Q1, `tools/pack_drops.py` (roles `ut`), `SkyyGear/build_skyygear_0.3.21.py` (UT_ROWS, GearUtFx grammar),
`research/cloud/UT-First-Batch-Build.md` (the existing 22 rows and their maths) and `docs/answered/gear.md` (Untiered locks).
Wynncraft idea behind the style: a unique item trades one big edge for one clear cost, readable in one tooltip line.

## 1. How a UT row works (so the numbers below are valid)

Two config rows per item id (Server Setup -> Gear -> Rarity, written to `config.properties`, `GearUt` / `GearUtFx`):

```
ut.<item id>=<min level>,<max level>,<ONE orange trade-off line>
utfx.<item id>=<body stat keys at utline.power 70%>,<fixed lines: key+N / key-N, swing=slow|medium|fast|superfast, tricks>
```
- Tricks: `lowhp back front taken hp mregen range pierce heal kb` (`+N` = percent; `taken+5` = 5% MORE damage taken; `dmg-30` = 30% less
  damage dealt). Body keys are live stats only (`str mp cc cd lsteal hpr hprp def spd stam tdmg dmg ...`).
- Trade-off line: ASCII, no comma, no `=`, max 110 chars (build assert). Armor values are PER PIECE and add over the set (Filing
  Cabinet: `hp+6.25 dmg-2/-3` per piece = set +25% / -10%; Courier `taken+5` per piece = set +20%).
- A pack id becomes Untiered only when BOTH rows exist; an id that any loaded recipe makes is refused (checked in the spec: none of
  the 5 has a recipe in 1.23.0). Level band: first batch Iron = 15-29; Adamantite proposal 45-59 (zone 4 band 45-60).
- Four power sources rule: every UT is weapon-or-gear only; its trade-off must not require a pet / accessory, and a set gives about
  one fifth to one third of a build's damage or defence - the numbers below keep each item near the existing batch's DPS (Slow
  tier x1.4 hit weight is DPS-neutral, so a damage % on top is the real buff).

## 2. The five sets (ids exactly as in `tools/pack_drops.py`; zone / weight from the table)

| Set | Zone / weight | Ids (rows needed) | Identity (Wynncraft-style) |
|---|---|---|---|
| Ghost Rook | 1 Iron, Heavy | `RookBootsGhost RookChestGhost RookGauntletsGhost RookHelmGhost RookHelmGhostOpen` + 5 `Wraith` twins = 10 | "Hollow Guard" - a tank that has gone slow |
| Ghost Calvary | 1 Iron, Heavy | `GhostCalvaryHelm GhostCalvaryChest GhostCalvaryGauntlets GhostCalvaryLeggings` = 4 | "Lancer" - fights what it faces |
| Battlegrounds | 1 Iron, Cloth | `TarnishedCrown VerdantAmulet` = 2 | "Healer's set" - heals more, hurts less |
| Ghost Sword | 1 Iron, Sword (Warrior, ghost / undead elite at night) | `GhostSword` | fast ghostly blade with a fragile wielder |
| Hepta Axe | 4 Adamantite, Battleaxe (Berserker, Trork Chieftain) | `Hepta_Axe` | all-in axe: hits 54% harder, costs defence |

### 2.1 Config rows (copy-paste ready; per-slot values differ like Filing Cabinet: Head / Hands small, Chest / Legs large)

Ghost Rook and Wraith, 15-29. Helm, Gauntlets (the `GhostOpen`/`WraithOpen` helms too) use -3; Chest, Boots (Legs slot) use -5; whole
set -16% damage taken, speed down.
```
ut.RookHelmGhost=15,29,Hollow guard: take 3% less damage per piece (set 16%) but you move slower.
utfx.RookHelmGhost=def hprp,taken-3 spd-2
ut.RookChestGhost=15,29,Hollow guard: take 5% less damage per piece (set 16%) but you move slower.
utfx.RookChestGhost=def hprp,taken-5 spd-2
(the same pattern for RookGauntlets* = -3, RookBoots* = -5, the Open helms = -3, and the five Wraith twins)
```
Ghost Calvary, 15-29 (all pieces `front+10 back-10`, set +40% / -40%):
```
ut.GhostCalvaryChest=15,29,Lancer's set: 10% more damage to enemies you face and 10% less from behind per piece (set 40%).
utfx.GhostCalvaryChest=str spd,front+10 back-10
(Helm, Gauntlets, Leggings the same text; Chest / Leggings may carry front+12 back-12 if Skyy wants the body pieces to weigh more)
```
Battlegrounds (2 pieces, so double values), 15-29:
```
ut.TarnishedCrown=15,29,Healer's set: heal orb heals 25% more per piece (set 50%) but spells deal 15% less (set 30%).
utfx.TarnishedCrown=mp hpr,heal+25 dmg-15
ut.VerdantAmulet=15,29,Healer's set: heal orb heals 25% more per piece (set 50%) but spells deal 15% less (set 30%).
utfx.VerdantAmulet=mp hpr,heal+25 dmg-15
```
Ghost Sword (Iron level 20 item), 15-29:
```
ut.GhostSword=15,29,Swings one tier faster. You take 5% more damage while held.
utfx.GhostSword=str lsteal,swing=fast taken+5
```
Hepta Axe (Zone 4 Adamantite), 45-59 - like the Paperweight (Slow x1.4 hit weight, +10% damage = hit x1.54, DPS +10%) paid for with 10% more damage taken:
```
ut.Hepta_Axe=45,59,Hits 54% harder. Swings 40% slower. You take 10% more damage while held.
utfx.Hepta_Axe=str tdmg,swing=slow dmg+10 taken+10
```
Length / charset checked: all lines <= 105 chars, ASCII, no comma or `=` inside the sentence.

### 2.2 Why these numbers
- Ghost Rook: `taken-16%` for the set is the best defence line in the batch so it pays with Speed (a tank that cannot run); Filing Cabinet
  pays with damage instead, so the two heavy UTs play differently.
- Ghost Calvary: `front/back` already exists on the Pocket Knife (weapon). On armor it is the knight version: the opposite sign,
  small per piece, so a set is a clear "never turn your back" style rather than a flat stat.
- Battlegrounds: the only Cloth UT of zone 1; the existing cloth UT (Intern) is a Mana-regen spammer, this one is the first healer
  UT. `heal` is read by SkyyArmory through `gear:fn:utfx` (same hook as the Second Opinion). Needs the same landing-order check
  as UT-First-Batch-Build U6 (heal from the damage BEFORE the -30% cut) - the -30% here is on the wearer's damage, so the heal
  orb must read the uncut burst or the +50% is lost.
- Ghost Sword: speed tiers are DPS-neutral (hit weight scales), so Fast gives more crits / Life Steal procs per second; the wielder
  pays 5% damage taken. Fast hits land lighter by design.
- Hepta Axe: Slow tier + `dmg+10` is the Paperweight formula one zone up; `taken+10` is the Berserker price.
- Open issues the main session must know: (a) the Armory pieces carry their OWN multiplicative stats on top (Pack-Drops-Spec "still
  open") - these rows add to them, so a Ghost Rook piece may already be strong; (b) every colour of Ghost Rook is its own row, so
  10 + 4 + 2 + 1 + 1 = 18 new rows against the existing 22 - with every row weight 1 these sets would be 45% of the orange pool;
  `ut.weight.<key>` is not built (0.2.16 note) - either ship only 5 Rook ids (Ghost, no Wraith / Open) or build the weight first.

## 3. Zone 4 Cloth UT candidate

Findings: no recipe-free Armory Cloth set exists for Zone 4. Academy (Adamantite Cloth) is OFF and all 27 pieces are craftable;
a UT row for a craftable id is refused (`GearUt.ok`). Grand Lich is the zone's Cloth MYTHIC, SLVR cloth is still TODO (author's OK).

**Recommended: build our own in SkyyGear**, the same recipe as the Intern (a "gear"-owned copy of a vanilla cloth set, orange
placeholder recolour from Assets.zip at build time, never committed): base `Armor_Cloth_Cindercloth_<Head|Chest|Hands|Legs>`
(the top vanilla cloth; Skyy's table sets Cindercloth to Adamantite bars = Zone 4), ids `Armor_UT_Auditor_<slot>`, names
"The Auditor's Hood / Robe / Cuffs / Skirt" (office joke line like the other UTs). One new UT_ROWS block, 4 rows:

```
ut.Armor_UT_Auditor_Head=45,59,Burst set: 5% more damage per piece (set 20%) but 10% less Mana regen per piece (set 40%).
utfx.Armor_UT_Auditor_Head=mp stam,dmg+5 mregen-10
(Chest / Hands / Legs identical; Chest and Legs may use dmg+6 mregen-12 for a 24% / 48% set)
```
Why it fits: the zone's cloth Mythic is Grand Lich (boss), Intern is the only cloth UT and is Mana-spam, so the Auditor is the
opposite (burst mage that runs dry); needs no Armory data, no author permission, no art beyond the build-time recolour. If Skyy
dislikes a new item, the fallback is to leave Zone 4 Cloth without a UT until SLVR Cindercloth robes get the author's OK.

## 4. Ship it ON or OFF?

**Safer: OFF.** These are drafts of Skyy's own design call; the table today keeps the 5 candidates out of every bag
(`role ut` - never drop without rows), so withholding the rows = today's behaviour, zero risk. Ship the rows only after Skyy's OK, in
one batch, ON (`part.utLines` is already true and "no dev gates" applies; there is no per-set switch, only the missing rows). If Skyy
approves but wants a soft launch: add the rows for Ghost Sword + Hepta Axe first (single ids, no pool dilution), then the Rook
(5 ids), Calvary, Battlegrounds. The Auditor needs a SkyyGear build (new art ids) so it rides the next gear round; the Armory rows
are config-only (a one-time migration block like `migrate0216`: only add the missing keys, never rewrite).

Record Skyy's answer word for word with `python tools/qa_append.py gear docs/answered/gear.md` when they decide.
