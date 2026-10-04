# Mob Curve Spec - Wynncraft-style mob curve, matching gear curves, a BRUTAL level gap, kill XP off raw health

*SPEC round, 2026-10-03 (Opus draft) + final editor pass 2026-10-04 (Opus: every critic finding checked against the code and re-run in
a scratch model; Appendix A lists what was taken and what was not). Read-only on code, game files and live data; nothing built, nothing
committed. Skyy uses they/them. Builds: SkyyMobs 0.1.4 (on top of 0.1.3), SkyyGear = the next free version (0.2.4 when 0.2.3 is the
newest finished one), SkyySkills 0.4.16 - one full round, deployed together (section 7). The class side (Priest burst + healing, a Mage
survival tool, class Health) is the class round (SkyyArmory 0.1.1 + SkyyClasses 0.1.12); section 2.7 gives it targets.*

**Inputs.** Skyy's LOCKED answers (OPEN-QUESTIONS.md 2026-10-03: mob toughness = "Wynncraft-style curve", level gap = "Brutal" - you
deal ~20 %, take ~2.6x at +20); the LATEST line (OPEN-QUESTIONS.md "ANSWERED 2026-10-03 ~22:40": Strength back on Hard, "it feels good
right now" on a new Mage; the Priest made mobs feel too easy) - **this wins**: Lv 1-20 stays today's Hard, mobs grow toward the high
levels, the brutal part sits in the level gap, Priest vs Mage is fixed on the class side. The numbers analyst's tables
(`tools/dev/scratch/mobcurve-numbers/numbers.md`) and the two critics (balance, feasibility), every number re-derived for this pass.

**Short names for sources.** Mobs = `SkyyMobs/build_skyymobs_0.1.3.py` (its numbers are 0.1.2's: header lines 1-4), Gear =
`SkyyGear/build_skyygear_0.2.1.py` (0.2.2 changed only tooltips / crit: its header lines 7-21), Armory = `SkyyArmory/build_skyyarmory_0.1.py`,
Skills = `SkyySkills/build_skyyskills_0.4.15.py`, Classes = `SkyyClasses/build_skyyclasses_0.1.11.py`, Menu =
`SkyyMenu/build_skyymenu_0.3.6.py`, live = the world's `UserData/Saves/HUD mod/mods/Skyy_*/` files (read only, 2026-10-03/04).

**Legend.** VERIFIED = read in code / a live file (cited). DERIVED = arithmetic on cited numbers (the final editor's scratch model =
numbers.md's `model.py` + `gearstats.py` with the new rows; deleted afterwards). PROPOSED = a default this spec picks. UNVERIFIED = needs
the game.

---

## 0. For Skyy (plain words)

**What changes**

1. **A fight against a mob of YOUR level plays exactly like today's Hard - at every level, Lv 1 to 60.** Same swings, same shots
   (a wand needs a 2nd shot at Lv 46+), same hits to kill you - checked level by level for every class and difficulty. You said Hard
   feels right, so we keep it.
2. **Mobs and gear both grow much faster after Lv 20 - Wynncraft style.** A Lv 40 mob gets x13 health (today x4), a Lv 40 sword hits
   x9.6 (today x3), and armor gives more Health (a Lv 40 set +269 instead of +84 - your ask). Below Lv 21 nothing changes.
3. **That makes the level gap BRUTAL.** A mob 20 levels above you takes 5-9x as long to kill (you deal ~12-19 % at Lv 10-33) and hits
   2.7-3.5x as hard - plus a gap rule on top (only mobs more than 5 levels above your class skill). Mobs below you just die fast.
4. **Kill XP stops following mob health.** It pays what today's Hard pays (within 2 %) at every level, and each difficulty keeps
   today's share, so the bigger health can never blow XP up.
5. **Casters keep up:** wands / staffs keep today's numbers, and Mana regen grows +7 % per class level above 20 (nothing changes now).
6. **Old gear gets weaker faster now**, so Reforge also raises an item to your level (inside its metal's band). **Life Steal** is capped
   at 5 % of your max Health per second (the new curve would let it out-heal a mob).

**Your Lv 33 Yeti, under the new rules**

| | Yeti health | your charged shots | it hits you for | hits to kill you |
|---|---|---|---|---|
| Today, Hard (your test - it was Lv 34) | 823 | **4** | 17 | 10 |
| Custom 20 / 8 stopgap (Lv 32) | 1,627 | 8 | 25 | 7 |
| **New: your Priest (Divinity 21) vs that Lv 34 Yeti (13 levels above you)** | 1,795 | **11** (your whole Mana bar + a bit of regen) | 30 | 6 |
| New: a Lv 15 Mage vs a Lv 33 Yeti | 1,663 | 6 + 1 quick (the whole bar) | 31 | 5 |
| New: a Lv 15 Warrior vs it | 1,663 | 138 swings - run | 31 | 6 |
| New: the same Yeti when you are Lv 33 | 1,663 | Priest 3, Mage 2, Warrior 34 swings | 23 | 13 (as today) |

**Do now (no build):** Server Setup -> Classes -> Priest -> "Charged heal cap per wand Mana" 2 -> 1 (the next step we agreed if the
Priest still felt strong): an Iron wand's charged heal goes 30 -> 15, Thorium 50 -> 25.

**Your live Mobs file.** Difficulty is Hard again, but health cap 20 / damage cap 6 are still the Custom test's (config-changes.log
21:40:20; at 22:34 only Difficulty changed). Today that changes nothing below Lv 64, and the new Level curve ignores the caps.

**Questions** (the build uses the [default] if you do not answer; all are Server Setup rows you can change later)

1. **Same-level fights = today's Hard at every level** (mobs only get harder when they out-level you)? [yes]
2. **Gap rule:** free for 5 levels, then -2.5 % of your damage and +1.5 % of its damage per level (never below 40 % / above x1.5)?
   [yes] (If being one-shot by far higher mobs feels bad, "One hit at most" caps a hit - off by default.)
3. **Gap only for mobs ABOVE you, and "your level" = your class weapon skill** (Divinity, Sorcery ...)? [yes, yes]
4. **Casters:** keep wand / staff damage and grow Mana regen +7 % per class level above 20 (Lv 40: x2.4)? [yes]
5. **Reforge raises your item to your level** (never above its metal's top level; it re-rolls the stats as today)? [yes]
6. **XP steering at Lv 30+:** mobs 5 levels below you then pay ~20 % more XP per second than mobs your level. Change your locked XP gap
   rows to free 3 / +8 % above / -7.5 % below? [keep your rows for now - decide when you reach Lv 30]
7. **Damage floor** for big mobs that hit softly (Yeti 10): at least X % of their Lv 1 health, only above Lv 20? [off - try 15]
8. **Lv 50-60:** no gear goes past Lv 49 yet; mobs keep growing like today's Hard there (Lv 60 = today's Lv 60). [yes - the
   alternative is "flat at Lv 49's strength"]
9. **Bosses** (Goblin Duke, Trork Chieftain, dragons, Skeleton Elite) have no level, so from about Lv 30 your new gear makes them
   2-5x easier than today. A new "Fixed level by role" table can give them levels. [empty now - the boss round fills it]
10. **Life Steal cap** 5 % of max Health per second? [yes]

---

## 1. The mob curve

### 1.1 Today (VERIFIED)

- Health multiplier = min(cap, 1 + hp % x (L - 1)), never below 1; damage the same with dmg % (`MobCfg.hpMult` Mobs:1800, `dmgMult`
  :1808). Presets Easy 4 / 2, Normal 6 / 3 (default), Hard 8 / 4 (Mobs:354), caps x6 / x3.5 (:355), Custom rows 4 / 2 (:356).
- Health floor: max HP = max(own base, 50) x the capped multiplier (`floorFactor` :1818, `hpAmount` :1825; `FLOOR_DEF` :407).
- Damage: `LevelDamage` (Filter group, BEFORE the engine's ArmorDamageReduction) multiplies every hit whose attacker is a levelled mob
  above Lv 1 (`i.level <= 1` returns early; projectiles: the shooter) by `dmgMult(level)`, for ANY victim (no victim test) (Mobs:2610-2627).
- A health setting change re-applies every loaded levelled mob at once (`derive` health signature :1709 -> `MobRefresh`), with 0.1.3's
  client health-bar fix. The config kit keeps 10 History versions (`KEEP=10`, Mobs:1512).
- Live (Skyy_SkyyMobs/config.properties): `strength.difficulty=hard`, `strength.hp=20`, `strength.dmg=8`, `strength.hpCap=20`,
  `strength.dmgCap=6`, no `strength.floor` line (= 50), LF line endings; `levels.exclude` holds `Risen_*`, `Goblin_Duke*`,
  `Trork_Chieftain`, `Dragon_*`, `Skeleton_Elite*`, `*_Boss*` and the NPC / pet patterns (:12).
- Linear growth makes the level gap SHRINK as levels rise (today's Hard: a +20 mob has x2.60 health at Lv 1 but x1.39 at Lv 40) - the
  reason the plan wants an exponential curve (numbers.md section 6).

### 1.2 New: one points table per difficulty, built by one rule (PROPOSED)

- New row **`strength.shape`** = `curve` (Level curve, the new default) | `linear` (Per level = 0.1.3's maths with the caps, byte for
  byte).
- **8 new key-family tables** `curve.hp.<difficulty>.<level>=<factor>` and `curve.dmg.<difficulty>.<level>=<factor>` (easy, normal,
  hard, custom): one entry per point, straight lines between points, flat outside the first / last point (SkyyGear's `GearBase.eval`
  rule, Gear:6538-6550). In Server Setup each table is ONE row ("Open - 10 entries") edited point by point. The Difficulty row picks the
  pair; Custom has its own pair (default = a copy of Hard). Entry key = a whole level 0-100, factor 0.1-1000, at least one entry.
- In curve shape: health multiplier = curve(level) (the floor still goes on top: max(base, floor) x curve); damage multiplier =
  curve(level). The caps do not apply in curve shape (they still cap Per level).
- **THE RULE (balance critic B1, extended to Lv 60): a same-level fight plays like today's preset at every level.**
  health(L) = today's preset health(L) x F_new(g) / F_old(g), damage(L) = today's preset damage(L) x player max HP_new(L) / max HP_old(L),
  with g = min(L, 49) (the player's gear level, section 2.3). The F / bonus ratio cancels the gear growth, the HP ratio cancels the
  armor Health growth, so swings, shots and hits-to-die equal today's (checked at every level 1-60 on Easy, Normal and Hard: Warrior
  within 1 swing, Archer within 1 draw, Mage the same shot count, raw hits-to-die within 0.05; the only change is the Priest's wand
  needing 2 charged shots instead of 1 at Lv 34 and Lv 46-60 Hard / 53-60 Normal, because spells keep today's numbers - section 2.4).
- **Lv 1-20 of every table is exactly today's preset line** (F_new = F_old and H_new = F_old up to Lv 20; the points 1:1.0 and 20:x
  lie on 1 + p (L - 1), so the interpolation reproduces it to float precision - harness check against SkyyMobs-0.1.3.jar).
- **Easy / Normal keep today's relation to Hard** (4 % / 6 % / 8 % presets): the same rule on their own presets, so Easy / Hard is
  today's ratio at every point.
- **Flat after Lv 60** (zone bands end at 60, Mobs bands; Lv 61-100 mobs exist only through `levels.max` / world rows): those points
  come with our own Lv 50+ gear tiers.

### 1.3 The default tables (DERIVED from 1.2, PROPOSED as defaults - exact file text)

```
curve.hp.hard:   1=1.0, 20=2.52, 25=3.62, 30=5.6,  35=8.53, 40=13.18, 45=19.41, 49=24.52, 55=26.95, 60=28.98
curve.hp.normal: 1=1.0, 20=2.14, 25=3.03, 30=4.62, 35=6.97, 40=10.69, 45=15.63, 49=19.66, 55=21.48, 60=23.0
curve.hp.easy:   1=1.0, 20=1.76, 25=2.43, 30=3.65, 35=5.41, 40=8.19,  45=11.85, 49=14.79, 55=16.01, 60=17.02
curve.dmg.hard:  1=1.0, 20=1.76, 25=2.32, 30=3.03, 35=3.89, 40=4.95,  45=6.41,  49=7.72,  55=8.31,  60=8.78
curve.dmg.normal:1=1.0, 20=1.57, 25=2.04, 30=2.62, 35=3.33, 40=4.2,   45=5.39,  49=6.45,  55=6.89,  60=7.24
curve.dmg.easy:  1=1.0, 20=1.38, 25=1.75, 30=2.22, 35=2.77, 40=3.44,  45=4.36,  49=5.19,  55=5.47,  60=5.7
curve.hp.custom / curve.dmg.custom = copies of the Hard tables
```

(The file holds one `key=value` line per entry, e.g. `curve.dmg.easy.40=3.44`; the block above is compressed for reading.)

### 1.4 Lv 1-100 multipliers (DERIVED from 1.3; health / damage)

| Mob Lv | Easy | Normal | **Hard (new)** | today's Hard (8 / 4, caps x6 / x3.5) | Custom 20 / 8 stopgap (caps x20 / x6) | Wynncraft median HP (fit, = Hard at Lv 20) |
|---|---|---|---|---|---|---|
| 1 | x1.00 / x1.00 | x1.00 / x1.00 | **x1.00 / x1.00** | x1.00 / x1.00 | x1.00 / x1.00 | x0.6 |
| 5 | x1.16 / x1.08 | x1.24 / x1.12 | **x1.32 / x1.16** | x1.32 / x1.16 | x1.80 / x1.32 | x0.8 |
| 10 | x1.36 / x1.18 | x1.54 / x1.27 | **x1.72 / x1.36** | x1.72 / x1.36 | x2.80 / x1.72 | x1.2 |
| 15 | x1.56 / x1.28 | x1.84 / x1.42 | **x2.12 / x1.56** | x2.12 / x1.56 | x3.80 / x2.12 | x1.7 |
| 20 | x1.76 / x1.38 | x2.14 / x1.57 | **x2.52 / x1.76** | x2.52 / x1.76 | x4.80 / x2.52 | x2.5 |
| 21 | x1.89 / x1.45 | x2.32 / x1.66 | **x2.74 / x1.87** | x2.60 / x1.80 | x5.00 / x2.60 | x2.7 |
| 25 | x2.43 / x1.75 | x3.03 / x2.04 | **x3.62 / x2.32** | x2.92 / x1.96 | x5.80 / x2.92 | x3.7 |
| 30 | x3.65 / x2.22 | x4.62 / x2.62 | **x5.60 / x3.03** | x3.32 / x2.16 | x6.80 / x3.32 | x5.4 |
| 33 | x4.71 / x2.55 | x6.03 / x3.05 | **x7.36 / x3.55** | x3.56 / x2.28 | x7.40 / x3.56 | x6.8 |
| 34 | x5.06 / x2.66 | x6.50 / x3.19 | **x7.94 / x3.72** | x3.64 / x2.32 | x7.60 / x3.64 | x7.3 |
| 35 | x5.41 / x2.77 | x6.97 / x3.33 | **x8.53 / x3.89** | x3.72 / x2.36 | x7.80 / x3.72 | x7.9 |
| 40 | x8.19 / x3.44 | x10.69 / x4.20 | **x13.18 / x4.95** | x4.12 / x2.56 | x8.80 / x4.12 | x11.4 |
| 45 | x11.85 / x4.36 | x15.63 / x5.39 | **x19.41 / x6.41** | x4.52 / x2.76 | x9.80 / x4.52 | x16.4 |
| 49 | x14.79 / x5.19 | x19.66 / x6.45 | **x24.52 / x7.72** | x4.84 / x2.92 | x10.60 / x4.84 | x21.8 |
| 50 | x14.99 / x5.24 | x19.96 / x6.52 | **x24.93 / x7.82** | x4.92 / x2.96 | x10.80 / x4.92 | x23.4 |
| 55 | x16.01 / x5.47 | x21.48 / x6.89 | **x26.95 / x8.31** | x5.32 / x3.16 | x11.80 / x5.32 | x33.4 |
| 60 | x17.02 / x5.70 | x23.00 / x7.24 | **x28.98 / x8.78** | x5.72 / x3.36 | x12.80 / x5.72 | x47.3 |
| 61-100 | = Lv 60 | = Lv 60 | **= Lv 60** | x5.80-6.00 / x3.40-3.50 | x13.0-20.0 / x5.80-6.00 | x50-643 |

Wynncraft column = the research's log-quadratic fit of median hostile mob HP (ln HP = 3.405 + 0.0814 L - 0.000101 L^2), scaled to
x2.52 at Lv 20. Hard grows x9.7 from Lv 20 to 49 (Wynncraft's median x8.7), then slows: no gear passes Lv 49.

### 1.5 Why this shape

- **Today's Hard at every level, not "Lv 20's pace" (the draft's version).** The draft held the Lv 20 pace (Warrior 14 swings) at every
  level; today's Hard slows a little as levels rise (16 swings at Lv 33-45, 17 at 49, 19 at 60) while gear stats grow from 62.5 % power
  at Lv 20 to 100 % at Lv 40 (`GearLevel.factor` Gear:5380-5388, live `stat.levelFloor=25` / `stat.levelFull=40`): a Rare set's mean
  hit x1.38 -> x1.68, a Fabled set's x2.03 -> x3.14 (DERIVED, gearstats.py). Today those two effects roughly cancel (a Rare Warrior
  needs ~10 swings at every level); the draft's curve would have made same-level fights at Lv 33-49 15-23 % faster than today's and
  21-33 % cheaper in health, so a geared Lv 40 fight would have run ~25 % (Rare) to ~40 % (Fabled) faster than a Lv 20 one - "mobs too
  easy at high levels" again. The rule in 1.2 keeps today's numbers for every gear and rarity.
- **Wynncraft-style growth and BRUTAL gaps come from the gear curves.** Because a Lv 40 sword hits x9.6 and a Lv 40 mob has x13 health,
  at Lv 20 a mob 20 levels above you has 5.2x the health of one at your level (today x1.6) and 2.8x the damage (today x1.5) - before the
  gap rule.
- **The LOCKED line's "about 10x health / 5x damage by Lv 33"** was written before the LATEST answer. At Lv 33 the default reaches
  x7.4 / x3.6 with today's same-level pace; reaching x10 would mean same-level fights ~35 % slower than today's Hard - against "it feels
  good right now". Question 1 lets Skyy raise it (scale the Lv 25+ points).
- **Lv 49-60:** gear stops at 49 (`VANILLA_TOP` Gear:1068), so the rule makes Lv 60 play like today's Lv 60 (19 swings, 5 hits to die
  (raw 4.0); x1.18 health over Lv 49). Question 8's alternative "flat from Lv 49" (balance critic) makes Lv 50-60 as easy as Lv 49.
- **Mobs below you die fast:** a Lv 33 Warrior kills a Lv 23 mob in 7 swings (today 12). The kill XP gap rows decide whether that pays
  (section 4.4).

### 1.6 Optional rows (PROPOSED, all default off / empty)

- **`strength.dmgFloor`** (int %, 0-100, default **0** = off): a levelled mob's hit on a PLAYER is at least this % of max(own base HP,
  health floor) x ramp, applied in `LevelDamage` before the level multiplier; ramp = 0 at Lv <= 20, (L - 20) / 10 at Lv 21-29, 1 from
  Lv 30 - so it never touches the Lv 1-20 part. Why: role files without their own attack vars use the template's `Melee_Damage` 10
  (numbers.md 1.4). At 15 (full from Lv 30, ramped from Lv 21): Yeti 10 -> 34, Golem_Firesteel / Skeleton_Burnt_Praetorian 10 -> 34,
  Skeleton_Burnt_Soldier 5 -> 19; wolf-class and stronger hitters are above 15 % already. A Lv 34 Yeti then hits Skyy's Priest for ~102
  (2 hits kill).
- **`strength.hitCap`** (int %, 0-100, default **0** = off): one levelled-mob hit on a player (after the level multiplier, the floor and
  the gap, before armor) is at most this % of the victim's max Health. At +20 a few heavy hitters one-shot (Rex_Cave hits 49-53 % of a
  same-level player's Health, 115-169 % at +20, DERIVED); 60 would make those two hits.
- **`scale.role`** table (Mob-Levels-Plan section 10 row: `scale.role.<role or Prefix*>=<level>|<health x>`, int 0-100 | dec 0.1-100,
  default **empty**): a matching role always gets that level (no roll; it wins over `levels.exclude` and `levels.roles`), its health x the
  second column on top of the curve, and then the curve, gap, nameplate and kill XP like any levelled mob. Level 0 = the row is off.
  Why now: unlevelled bosses do not follow the mob curve but players' gear does (section 2.8). Defaults are the boss round's job
  (research/cloud/Zone-Bosses-Ideas.md proposes Trork Chieftain 20, Goblin Duke 30; where each vanilla boss spawns is UNVERIFIED).

---

## 2. The matching player curves

### 2.1 Today (VERIFIED)

- ONE curve F(L) `base.curve` = 1:1.0, 4:1.6, 10:2.0, 40:3.0, 100:5.0 (Gear:1128 = live :242) drives **weapon damage, spell damage and
  armor Health**: a hit = vanilla step x K x F(item level) x material bonus (`GearBase.mult` Gear:6683-6688); spells have K = 1
  (`kOf` Gear:6673-6681); armor Health = slot base (25 for a full set) x F x bonus (`armorTarget` Gear:6819-6833). Material bonus =
  1 + 0.3 % x band start, none for a band starting at Lv 1. R(L) `base.resCurve` drives resistance (Gear:1129).
- K = the family base item's damage ratio / (F x bonus at the BASE's band start) (`kOf`, Gear:6673-6681). Families with a Crude / Wood /
  Iron base (`FAM_BASE` Gear:1888-1896) divide by F(1) or F(15); the own-base families (Kunai, Spellbook: `BASE_NOFAM`, Gear:1897-1898)
  divide by their own band start (Kunai 20, Spellbook_Fire / Spellbook_Frost 30, Demon / Rekindle 35: Gear:1016, :1028-1035).
- Wands / staffs keep K = 1 **and** SkyyArmory's metal ladder: charged shot = 25 (wand) / 50 (staff) x (1.25 x cost multiple - 0.25)
  (Armory:150, :206), Mana 5 / 10 / 15 / 25 / 40 / 60 / 85 per metal (wands; staffs 2x).
- Crafted gear is stamped at the crafter's gate level inside the item's band (`GearRoll.craftLevel` Gear:6337-6347); drops / chests stamp
  the band start; reforge / identify never change a stamped level (research/Gear-Levels-Wynn-Spec.md line 274); admin `/gear relevel`
  only moves stamped items back into today's band.
- Live bands (Skyy_SkyyGear/config.properties :144-153): Crude / Wood 1-13, **Copper 5-18** (Skyy changed it 2026-10-03 22:57), copper
  armor 1-18, Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril 40-49. The tables below use the code default Copper 10
  (a Lv 5-9 Copper item's bonus is x1.015 instead of x1.03 live).

### 2.2 New: three curves (PROPOSED; unchanged from the draft except `20:2.333333`)

| Row | What it drives | Default |
|---|---|---|
| `base.curve` (existing key, new default; label "Weapon curve F(L)") | every non-spell weapon hit (swords, bows, axes, daggers, maces ...) | `1:1.0,4:1.6,10:2.0,20:2.333333,25:3.1,30:4.5,35:6.5,40:9.6,45:13.6,50:17.5,60:22.5,70:36.0,80:57.0,90:90.0` |
| `base.spellCurve` (NEW, "Spell curve S(L)") | wand / staff / spellbook SHOTS (K = 1) | `1:1.0,4:1.6,10:2.0,40:3.0,100:5.0` (= today's F: spells unchanged) |
| `base.hpCurve` (NEW, "Armor Health curve H(L)") | worn armor Health | `1:1.0,4:1.6,10:2.0,20:2.333333,25:3.7,30:5.4,35:7.3,40:9.6,45:12.8,50:16.3,60:21.0,70:30.0,80:43.0,90:62.0,100:88.0` |
| `base.resCurve` (unchanged) | Physical / Projectile resistance | 1:1.0, 10:1.4, 20:1.7, 40:2.2, 100:3.0 |

- **F and H equal today's F up to Lv 20:** `20:2.333333` lies on today's 10:2.0 -> 40:3.0 line to 3e-7 (the draft's `2.3333` was 3e-5
  off and could flip a `.5` tooltip rounding, `rint` Gear:6792). Harness: every rendered number at item level 1-20 identical.
- **K:** families with a Crude / Wood / Iron base start at Lv 1 or 15, where F_new = F_old, so their K is unchanged. The own-base
  families starting at 30 / 35 (Spellbook_Fire, Spellbook_Frost, Demon, Rekindle) DO get a new K, because F(30) goes 2.67 -> 4.5 and F(35)
  2.83 -> 6.5; their multiplier at the band start stays exactly 1 x bonus (vanilla there) and grows faster above it. Only melee swings of
  those spellbooks are affected (shots use K = 1). Harness asserts the band-start multiplier, not K.
- **F after Lv 20** keeps a Warrior's same-level swings near Lv 20's (F x bonus = 0.98 x the draft's Hard curve); **H after Lv 20**
  keeps raw hits-to-die near 5.2 (HP = 5.2 x mob hit x (1 - resistance), solved for the armor part). The mob tables (1.3) are then
  derived FROM F and H, so same-level fights equal today's exactly. H stays its own row so armor can follow a changed mob damage curve
  without touching weapon damage (Skyy's ask).
- **S stays today's F.** Spells already grow with the metal ladder; riding the new F would give a Lv 40 Mithril staff ~11,000 per shot.
- **Parser limit:** SkyyGear's `curvePts` refuses factors above 100 (Gear:3409); all three defaults stay at or below 90. Points above
  Lv 49 are only reachable by admin `/gear level` items until our Lv 50+ tiers exist.
- SkyyGear keeps TEXT rows (base.curve's shipped format; older jars read it). Editing a ~100-character value in the 270 px field
  (Menu:5624, ~25-30 characters visible) is UNVERIFIED - test step 11.

### 2.3 Player numbers per level (DERIVED; gear = best started metal at Lv min(L, 49), Copper armor until 14, class level = L, Overall = L / 2)

| Lv | gear | F today -> **new** | sword 6 / 6 / 11 today -> **new** | bow full draw today -> **new** | wand / staff charged (unchanged) | armor Health today -> **new** | max HP today -> **new** | resistance |
|---|---|---|---|---|---|---|---|---|
| 1 | Wood 1 | 1.00 -> 1.00 | 6 / 6 / 11 -> same | 12 -> 12 | 25 / 50 | +25 -> +25 | 125 -> 125 | 18.0 % |
| 10 | Copper 10 | 2.00 -> 2.00 | 12.4 / 12.4 / 22.7 -> same | 24.7 -> 24.7 | 115 / 233 | +50 -> +50 | 154 -> 154 | 25.2 % |
| 15 | Iron 15 | 2.17 -> 2.17 | 13.6 / 13.6 / 24.9 -> same | 27.2 -> 27.2 | 199 / 396 | +57 -> +57 | 162 -> 162 | 27.9 % |
| 20 | Thorium 20 | 2.33 -> 2.33 | 14.8 / 14.8 / 27.2 -> same | 29.7 -> 29.7 | 371 / 742 | +62 -> +62 | 169 -> 169 | 30.6 % |
| 25 | Cobalt 25 | 2.50 -> **3.10** | 16.1 / 16.1 / 29.6 -> **20.0 / 20.0 / 36.7** | 32.2 -> **40.0** | 656 / 1312 | +67 -> **+99** | 176 -> **208** | 32.8 % |
| 30 | Cobalt 30 | 2.67 -> **4.50** | 17.2 / 17.2 / 31.5 -> **29.0 / 29.0 / 53.2** | 34.4 -> **58.0** | 699 / 1399 | +72 -> **+145** | 182 -> **256** | 35.1 % |
| 33 | Cobalt 33 | 2.77 -> **5.70** | 17.8 / 17.8 / 32.7 -> **36.8 / 36.8 / 67.4** | 35.7 -> **73.5** | 726 / 1451 | +74 -> **+176** | 186 -> **287** | 36.4 % |
| 35 | Adamantite 35 | 2.83 -> **6.50** | 18.8 / 18.8 / 34.4 -> **43.1 / 43.1 / 79.0** | 37.6 -> **86.2** | 1155 / 2311 | +78 -> **+202** | 190 -> **314** | 37.4 % |
| 40 | Mithril 40 | 3.00 -> **9.60** | 20.2 / 20.2 / 37.0 -> **64.5 / 64.5 / 118.3** | 40.3 -> **129.0** | 1764 / 3528 | +84 -> **+269** | 198 -> **383** | 39.6 % |
| 45 | Mithril 45 | 3.17 -> **13.60** | 21.3 / 21.3 / 39.0 -> **91.4 / 91.4 / 167.6** | 42.6 -> **182.8** | 1862 / 3724 | +89 -> **+358** | 204 -> **474** | 40.8 % |
| 49 | Mithril 49 | 3.30 -> **16.72** | 22.2 / 22.2 / 40.7 -> **112.4 / 112.4 / 206.0** | 44.4 -> **224.7** | 1940 / 3881 | +92 -> **+437** | 209 -> **554** | 41.8 % |
| 60 | Mithril 49 | 3.30 -> **16.72** | as Lv 49 | as Lv 49 | as Lv 49 | +92 -> **+437** | 213 -> **558** | 41.8 % |

Before gear stats and the class perk (x(1 + 0.002 x class level), Skills:9681-9727). Player max HP grows +4.2 % a level from Lv 20 to 40
(Wynncraft's player HP estimate: +4.5 % a level).

### 2.4 Casters: Mana regen grows with class level (NEW in this round - balance critic B3)

Spells keep today's numbers, but same-level mobs get the new health, so the Mana a kill costs rises at Lv 25+ (today a Lv 40 staff
quick shot one-shots a same-level mob - the "8x overkill" the draft wanted gone). Regen stays vanilla 5 / s out of combat, 2.5 / s in
combat (`mana.regen.inCombat` 50 %, Skills:1956-1968, live :485). DERIVED, same-level wolf class, Hard, cheapest charged / quick mix:

| Lv | Mage Mana per kill: today -> new | kills per full bar: today -> new | Mage kill time when out of Mana (5 / s) vs a Warrior's: today -> new -> **new + regen perk** |
|---|---|---|---|
| 20 | 20 -> 20 | 11.6 -> 11.6 | 1.58 -> 1.58 -> **1.58** |
| 30 | 32 -> 32 | 10.4 -> 10.4 | 1.11 -> 1.11 -> **1.88** |
| 33 | 32 -> 48 | 11.3 -> 7.6 | 1.16 -> 0.77 -> **1.48** |
| 40 | 34 -> 68 | 12.8 -> 6.4 | 1.09 -> 0.55 -> **1.31** |
| 45 | 34 -> 102 | 14.2 -> 4.7 | 1.09 -> 0.36 -> **1.00** |
| 49 | 34 -> 102 | 15.4 -> 5.1 | 1.14 -> 0.38 -> **1.15** |

(> 1 = the Mage kills faster than a Warrior.) **The perk (PROPOSED):** rows `mana.regen.perLevel` = 7 (% of the vanilla refill per class
level above the start) and `mana.regen.fromLevel` = 20, added inside SkyySkills' own `ManaRegen.total` as one more source (the registry
that `skill:fn:manaregen` feeds, Skills:8913-8930; cap `MAX_PCT` 1000, Skills:3154): Lv 30 +70 % (8.5 / s), Lv 40 +140 % (12 / s),
Lv 49 +203 % (15.2 / s); in combat x 50 % as today. Nothing changes at class level 20 or below. Burst per shot is unchanged, so the gap
is not weakened for casters (raising S instead would).

### 2.5 Life Steal cap (NEW in this round - feasibility critic F7)

Life Steal pays lsteal % of the landed damage once per `steal.windowS` (3 s, live :292), with no cap but max Health (`GearFx.leech`
Gear:9467-9474, payout :9692-9697, `GearLeechSys` :9930-9940); weapon and armor rolls add up (stat max 5 per piece at 100 % power,
Gear:784). The new curves give a Lv 40 mob 3.2x today's health but a Lv 40 player only 1.9x today's Health, so the same % heals much
more (DERIVED, Rare Warrior, same-level wolf class):

| Lv | heal per kill at 5 / 10 / 15 % Life Steal (% of max HP): today -> new | one 3 s window at 10 %: today -> new (a same-level mob deals per 3 s) |
|---|---|---|
| 20 | 8 / 15 / 23 -> same | 10 % -> 10 % (17 %) |
| 30 | 9 / 19 / 28 -> 11 / 23 / 34 | 12 % -> 15 % (18 %) |
| 40 | 11 / 21 / 32 -> 18 / 35 / 53 | 14 % -> **23 %** (18 %) |
| 49 | 12 / 24 / 36 -> 23 / 46 / 68 | 16 % -> **30 %** (18 %) |

At Lv 40+ a 10 % build would out-heal a same-level mob. **New row `steal.maxPerSec`** (PROPOSED default 5 = % of max Health per second;
0 = no cap): each payout is at most maxPerSec % x max Health x windowS (15 % per 3 s window). Typical sets (Rare 1.5-3 %, Fabled 4-7 %
Life Steal on average, DERIVED gearstats.py) and every Lv <= 20 Rare build stay under it.

### 2.6 Old gear: Reforge raises the level (NEW in this round - balance critic B7, Question 5)

With F growing 6-8 % a level after Lv 20 (today 1.4 %), an item made a few levels ago falls behind fast (DERIVED, ungeared, same-level
wolf class, weapon + armor made N levels ago in the same metal):

| Lv | 3 levels old: swings / hits to die / health lost per kill (today) | 5 levels old (today) |
|---|---|---|
| 30 | 19 / 4.2 / 70 % (16 / 4.6 / 53 %) | 22 / 3.8 / 89 % (16 / 4.5 / 55 %) |
| 45 | 20 / 4.1 / 75 % (17 / 4.5 / 57 %) | 23 / 3.7 / 96 % (18 / 4.4 / 64 %) |
| 49 | 19 / 4.0 / 73 % (17 / 4.4 / 58 %) | 21 / 3.7 / 90 % (18 / 4.4 / 65 %) |

(Fresh gear: 15 / 4.8 / 49 % at Lv 30, 16 / 4.6 / 53 % at 45, 17 / 4.6 / 57 % at 49.) **New row `reforge.raiseLevel`** (bool, PROPOSED
default on): a reforge also raises the item's stamped level to `craftLevel(id, player)` (the player's gate level, clamped into the
item's band - the craft rule) when that is HIGHER; it never lowers a level, never touches an admin `/gear level` item (`lvlA`), and an
unstamped item gets the stamp. The modifiers re-roll at the new level (the existing "rolls at the item's own level" order) and the coin
cost uses the new level (`cost.reforge` base + per level). The Reforge page says "Also raises it to Lv N". Mob drops still stamp the
band start (the loot round's level ranges come later).

### 2.7 Class identity (kept) and the class round's targets

Every class uses the same curves; classes differ by weapons, Mana and the Warrior's kit shield - there is no class Health / defence row
in code (Classes:240-272, numbers.md 3.1). The gap therefore hits classes differently. **Largest gap a solo player still wins**
(DERIVED: kill time <= time to die, stand-and-trade vs wolf class, Mage at the planned -15 % Health; "all" = every natural mob, Lv 60 is
the top):

| Gear | Class | Lv 10 / 20 / 33 / 40 / 49 |
|---|---|---|
| none | Warrior | +12 / +7 / +5 / +6 / all |
| none | Archer | +7 / +2 / +0 / +0 / +0 |
| none | Mage | +17 / +20 / +21 / all / all |
| none | Priest | +20 / +19 / +18 / all / all |
| Rare | Warrior | +14 / +10 / +9 / +14 / all |
| Rare | Archer | +10 / +6 / +5 / +6 / all |
| Rare | Mage / Priest | +19-21 / +22-23 / +26-28 / all / all |
| Fabled | Warrior | +16 / +12 / +13 / all / all |
| Fabled | Archer | +12 / +8 / +8 / +13 / all |
| Fabled | Mage / Priest | +21-23 / +25-26 / all / all / all |

Casters burst out-levelled mobs down before the 2nd-3rd bite; melee cannot. At Lv 40+ the curve flattens (gear stops at 49), so Zone 4's
top end is beatable for a geared player. Targets for the class round (SkyyArmory 0.1.1 + SkyyClasses 0.1.12; NOT built here):

| Class | LOCKED / planned | Target from this spec's numbers |
|---|---|---|
| Priest | wand charged shot -> AoE burst, ~60 % of today's damage per enemy, radius ~4, +10 % heal for anyone inside (LOCKED) | heal per charged cast today = min(15 % of the landed hit, max(10, 2 x the wand's charged Mana)) (Classes header lines 4-12, live share 15 / max per hit 10 / per second 10 / self 100 %). Lv 10 / 15 / 20 / 33 / 40 / 49: 18 / 30 / 50 / 80 / 170 / 170 HP = 11 / 19 / 30 / 28 / 44 / 31 % of max HP. Live "per wand Mana" 1 now (section 0) halves Lv 15-20. **Add a per-hit cap of ~12 % of the healed player's max Health** next to the Mana cap (balance critic B2): 18 / 19 / 20 / 34 / 46 / 66. |
| Mage | staff damage +20-25 % per Mana (live `tune.staff.*` still 100); Glass Cannon -15 % health; a survival tool (LATEST: "not only -15 % health") | with -15 % health a Mage dies in 5 same-level bites instead of 6 (5.2). **The tool should give back ~6-8 % of max Health per charged cast** (blink / Mana shield / spell life steal; Lv 40: 23-31 HP) - it halves the Mage's 12-13 % health lost per same-level kill. |
| Warrior | sturdier (Skyy); kit shield | a class Health row: x1.5-1.75 moves the ungeared solo frontier from +7 / +5 / +6 to +9 / +7-8 / +9 at Lv 20 / 33 / 40 |
| Archer | sturdier (Skyy) | the slowest same-level killer (9 full draws, 12.6 s; stand-and-trade it loses 74-82 % of max HP per same-level kill at Lv 1-20 - today too): bow damage x1.5-2 or kiting tools; test kiting in game |

The gap rule shrinks life steal fully, but Priest heals only where 15 % of the landed hit is below the heal cap: from Lv 33 the cap
binds (Lv 40 same level: 285 -> 170), so the gap leaves Lv 40 heals unchanged up to +21 and only cuts them from +22 (balance critic B2
corrected the draft here).

### 2.8 Known limits (DERIVED)

- **Unlevelled enemies follow the gear curves but not the mob curve** (feasibility critic F1): `GearHit.weaponHit` scales every player
  hit with no victim test (Gear:9721-9752). Swings for an ungeared Warrior, today -> new: Goblin_Duke (226 HP) Lv 25 11 -> 9, Lv 33
  10 -> 5, Lv 49 8 -> 2; Dragon_Fire (400) Lv 33 17 -> 9, Lv 49 14 -> 3; Skeleton_Elite (350) Lv 33 15 -> 8; unchanged at Lv <= 20. The
  Duke's 10 hit falls from 3.4 % to 2.2 % of a Lv 33 player's Health. Fix = `scale.role` (1.6) once the boss round sets their levels;
  the 0.7 roles not in the built-in list (Coffer_Goblin_*, Goblin_Burner / Feastmaster / Guardian, Void_Spectre, Void_Spawn_*:
  Mobs:194-200) and other mods' mobs are in the same boat (add them to `levels.roles` or `scale.role`).
- **PvP** is off on all 8 live worlds (`IsPvpEnabled false`). If a server turns it on, weapon F outgrows player HP (`weaponHit` has no
  victim test; SkyySkills' own perk has `perk.combat.damageVsPlayers=false`): ~40-48 % fewer hits to kill at Lv 40-49. A PvP factor row
  is a follow-up.
- **Damage over time and thorns** are not live (`thorns` / `poison` are "coming later", `pool.later=false`); an `ActiveEntityEffect` is
  a `Damage$Source`, not an `EntitySource`, so DoT never reaches LevelDamage, GapDamage, kill XP or the leech - they need a gap rule and
  a health-pool rule before they ship.
- **Lv 50-60:** gear stops at 49 (F 16.72, H 15.6); Lv 60 plays like today's Lv 60 (19 swings, 5 hits to die; Question 8).

---

## 3. The BRUTAL level gap

### 3.1 The rule (PROPOSED)

d = mob level - your class weapon skill level (the same "your level" as gear requirements and the kill XP gap: `class:skill:<uuid>` +
`skill:fn:level`, the read SkyyMobs already does for /mobs info, Mobs:3134-3149).

| | d <= free (5) | d > free |
|---|---|---|
| your hits on that mob | x1 | x max(dealtMin, 1 - dealtStep x (d - free)) = x max(0.40, 1 - 0.025 x (d - 5)) |
| that mob's hits on you | x1 | x min(takenMax, 1 + takenStep x (d - free)) = x min(1.5, 1 + 0.015 x (d - 5)) |

Mobs below you (d < -5): no change (the curve already makes them weak; the kill XP gap still lowers their XP). +10: x0.875 / x1.075;
+20: x0.625 / x1.225; +29 and up: x0.40 (the floor - no mob is ever immune); the taken cap x1.5 is reached at +39.
**Level 0 = unknown** (feasibility critic F6): `skill:fn:level` turns every failure into Integer 0 (Skills:6396-6409) and a player under 50
XP is level 0, so a 0 read means no gap, and a cached good level is never overwritten by a 0.

### 3.2 The whole effect at +10 ... +30 (DERIVED: curve ratio x gap, Hard)

"Mob effectively" = how much longer it takes to kill than a mob of your level (health ratio / dealt); "you deal" = 1 / that.
"Mob hits" = how much harder it hits you than a mob of your level (damage ratio x taken).

| your Lv | +10: effectively / you deal / hits | +15 | **+20** | +25 | +30 |
|---|---|---|---|---|---|
| 1 | x2.06 / 49 % / x1.50 | x2.93 / 34 % / x1.84 | **x4.38 / 23 % / x2.29** | x8.03 / 12 % / x3.20 | x15.5 / 6 % / x4.40 |
| 10 | x1.67 / 60 % / x1.39 | x2.81 / 36 % / x1.96 | **x5.21 / 19 % / x2.73** | x9.92 / 10 % / x3.72 | x19.2 / 5 % / x5.00 |
| 15 | x1.95 / 51 % / x1.60 | x3.52 / 28 % / x2.23 | **x6.44 / 16 % / x3.05** | x12.4 / 8 % / x4.12 | x22.9 / 4 % / x5.65 |
| 20 | x2.54 / 39 % / x1.85 | x4.51 / 22 % / x2.54 | **x8.37 / 12 % / x3.45** | x15.4 / 6 % / x4.73 | x24.7 / 4 % / x6.11 |
| 25 | x2.69 / 37 % / x1.80 | x4.85 / 21 % / x2.45 | **x8.58 / 12 % / x3.38** | x13.8 / 7 % / x4.38 | x18.6 / 5 % / x4.93 |
| 33 | x2.63 / 38 % / x1.77 | x4.21 / 24 % / x2.40 | **x5.68 / 18 % / x2.80** | x7.66 / 13 % / x3.15 | x9.85 / 10 % / x3.40 |
| 40 | x2.16 / 46 % / x1.70 | x2.73 / 37 % / x1.93 | **x3.52 / 28 % / x2.17** | x4.40 / 23 % / x2.31 | x5.50 / 18 % / x2.44 |
| 49 | x1.33 / 75 % / x1.21 | x1.58 / 63 % / x1.31 | **x1.89 / 53 % / x1.39** | x2.36 / 42 % / x1.48 | x2.95 / 34 % / x1.56 |

At +20 the curve alone gives "you deal 19-31 %, it hits 2.2-2.8x" at Lv 10-33; with the gap rule it is 12-19 % / 2.7-3.5x - at or
past Skyy's "Brutal" pick. From Lv 40 the curve flattens (gear stops at 49, the tables at 60), so the gap rule does most of the work
there. **Brutal but not immune:** a Mage still kills a +20 normal mob with ~3 charged shots at Lv 20-33 and must land them before the
mob's 2nd bite; a Warrior at Lv 20-33 needs 87-111 swings while dying in 2 bites - a party fight (5.2).

### 3.3 Which mod applies it, and where in the damage order

**SkyyMobs 0.1.4 applies both directions** - it owns mob levels, already scales mob damage, already reads class levels, and works without
SkyyGear. (SkyyGear's GearHitSys only runs for gear weapons and resolves projectiles through launch records; SkyyArmory only sees its own
orbs - neither covers every player hit.)

Player -> mob hit:
1. Engine amount (the swing's BaseDamage or the projectile's Damage).
2. Filter group, BEFORE ArmorDamageReduction - all multipliers, so their order never changes the result (feasibility critic checked:
   `hitAmount` Gear:8719-8743, CombatDmgSys Skills:9722, ArmoryTuneSys Armory:1867): SkyyArmory ArmoryTuneSys, SkyyGear GearHitSys ->
   GearHit.weaponHit (x K x F / S x bonus, then the stats and crit), SkyySkills CombatDmgSys (class perk), **NEW SkyyMobs GapDamage
   (x dealt(d): attacker = a player, victim = a levelled mob; a ProjectileSource counts as its shooter - `Damage$ProjectileSource`
   extends `EntitySource`, the shooter ref is what LevelDamage, CombatDmgSys and KillSys already read)**. SkyyClasses' DamageLock
   cancels wrong-class hits - GapDamage skips cancelled damage.
3. Engine ArmorDamageReduction (mobs have no armour in SkyyMobs).
4. GearTrueSys adds True Damage + element flats AFTER the armor pass (Gear:9917-9928) - **not scaled by the gap** (flat, +0.7 ... +6.9
   per hit at Lv 15-20, numbers.md 2.5).
5. Inspect group: GearLeechSys (life steal) and SkyyClasses PriestHealSys read the LANDED amount - the gap shrinks life steal fully and
   Priest heals only below their cap (2.7).

Mob -> player hit (SkyyMobs `LevelDamage`, Filter group, BEFORE ArmorDamageReduction, Mobs:2610-2627):
1. Engine amount; 2. the damage floor (victim = a player, mob above Lv 20; 1.6); 3. x curve damage(level); 4. **x taken(d) when the
victim is a player**; 5. the hit cap (victim = a player; 1.6). Mob -> mob / pet hits keep 0.1.3's level multiplier only.
6. Engine armour resistance (R(L)), then SkyyGear GearArmorSys (its per-stack ratio fix keeps any factor applied in between, Gear:9094-9115)
and Defense x 100 / (100 + Def).

Edge cases: mob vs mob, mob vs pet, a player's pet or summon vs a mob, player vs player = **no gap** (only player <-> levelled mob);
mobs without a level (islands, hub, unlevelled bosses) = no gap; no `class:skill` (no class) = no gap; the class level is cached per
player for 2 s (a level-up mid-fight counts within 2 s). Engine pieces VERIFIED by the feasibility critic (bytecode).

---

## 4. Kill XP off raw health

### 4.1 Today (VERIFIED)

`SkillCfg.combatXp` = **scaled**(clamp(round(max health at death x `combat.perHealth` 0.2), `combat.min` 1, `combat.max` 500)) - a role
override `combat.role.<role>` is returned as scaled(override) (Skills:5333-5345); `scaled` multiplies by the global `multiplier`
(Skills:5312-5319, read :5173; **live `multiplier=1.5`**, xp.properties :8). `MobXp.kill` (Skills:11282-11290): with `MobXp.ON`
(`combat.levelXp.enabled`, the part switch "Kill XP by mob level", live true) and a mob level from `mob:fn:level`, kill XP = pay(base x
`classSkill.xpMultiplier` 3 x levelFactor (1 + `combat.levelBonus` 0.05 x (L - 1)) x gap) (Skills:10933-10965); otherwise
`classXp(base)` = base x 3. Gap rows (LOCKED 2026-10-02): free 5, +5 % a level above up to x3.5, -5 % a level below down to x0.1 (live
:496-502). The party share pays each member with their own gap (`PartyXp.one2`, Skills:11095-11122). The max health is the LEVELLED one,
so XP follows the difficulty's health: on the new Hard tables the old formula would pay x3.2 at Lv 40 and x5.1 at Lv 49 (up to the
combat.max clamp) - the "must not explode" problem.

### 4.2 New (PROPOSED)

- New row `combat.xpFrom` = `level` (new default) | `health` (0.4.15 exactly).
- **Level mode:** kill XP = pay over ONE chance rounding (the existing `pay` rule) of
  `clamp(xpBase x perHealth, min, max) x MULT x 3 x levelCurve(L) x xpMult x (part on ? gap(d) : 1)`,
  computed in double (the integer `round` + `scaled` of a small Lv 1 base would add up to +3.3 %; this way the result is within 2 % of
  today on Hard at every level, 4.3).
  - xpBase = max(the mob's own base, SkyyMobs' health floor) = its Lv 1 health, and **xpMult** = min(1, the mob's health multiplier /
    what Hard would give it in the same shape) - both from the new SkyyMobs bridge `mob:fn:info` (7.3). Hard = 1; Easy / Normal keep
    today's share (Easy x0.70 at Lv 20, x0.62 at 40; Normal x0.85 / x0.81); Custom never pays more than Hard (Custom 20 / 8 no longer
    doubles XP). A later elite build multiplies its own factor into xpMult (Elites-Events-Spec 1.3: "x2 health = ~2x XP").
  - **Role overrides** (`combat.role.<role>`) keep 0.4.15's maths exactly: scaled(override) x 3 x levelFactor(L) x gap - never the level
    curve (it already holds Hard's health growth; feasibility critic F2b).
  - **The part switch** `combat.levelXp.enabled` in level mode switches only the gap rows (the curve is the mode's base, as max health
    was in health mode); help text says so.
  - **Fallbacks:** `mob:fn:info` missing from the bridge (SkyyMobs 0.1.3 or older, no SkyyMobs) -> 0.4.15 exactly. The function present but
    answering null for this mob (no level, or a bug) -> the no-level path `classXp(base)` (raw max health, no level factor, no gap;
    bounded by `combat.max` 500: at most 500 x MULT x 3). Never 0 because of this, never the x3-x5 health-mode explosion.
  - The party share runs through the same helper (each member's own gap, as today). The "first kill of NPC role X (max health M)" log
    line gains "(Lv 1 health B)".
- `combat.levelCurve` = a key-family table `combat.levelCurve.<level>=<factor>` (16 entries, check hook per entry: level 0-100, factor
  0.1-1000). Default = today's Hard product (1 + 0.08 (L-1)) x (1 + 0.05 (L-1)) (worst interpolation error 1.1 %):

```
1=1.0  5=1.58  10=2.49  15=3.6  20=4.91  25=6.42  30=8.13  35=10.04  40=12.15  45=14.46  50=16.97  60=22.59  70=29.01  80=36.23  90=44.25  100=53.07
```

  The one-time update writes this table from the FILE's own values (factor = (1 + 0.08 (L-1)) x (1 + B (L-1)), B = `combat.levelBonus`
  when the part is on, else 0) so a hand-set bonus or a switched-off part keeps its effect (feasibility critic F2c / F2d). Skyy's file
  (bonus 0.05, part on) gets exactly the default.
- `combat.levelBonus` (relabelled "Health mode: XP per mob level") counts only in health mode.

### 4.3 Today vs new (DERIVED; same-level kill, gap x1, multiplier x1.0 - Skyy's live x1.5 multiplies both columns)

| Mob Lv | 50-HP floor mob: today Hard / new | wolf class 103: today Hard / Custom 20/8 / **new** | Yeti 226: today Hard / Custom / **new** |
|---|---|---|---|
| 1 | 30 / 30 | 63 / 63 / **62** | 135 / 135 / **136** |
| 10 | 74 / 75 | 152 / 252 / **154** | 339 / 552 / **338** |
| 15 | 107 / 108 | 224 / 398 / **222** | 490 / 877 / **488** |
| 20 | 146 / 147 | 304 / 579 / **303** | 667 / 1269 / **666** |
| 25 | 191 / 193 | 396 / 785 / **397** | 871 / 1729 / **871** |
| 30 | 243 / 244 | 500 / 1029 / **502** | 1102 / 2256 / **1102** |
| 33 | 281 / 278 | 569 / 1186 / **573** | 1256 / 2605 / **1258** |
| 40 | 363 / 364 | 752 / 1602 / **751** | 1646 / 3522 / **1648** |
| 49 | 490 / 494 | 1020 / 2224 / **1018** | 2234 / 4886 / **2233** |
| 60 | 675 / 678 | 1398 / 3128 / **1396** | 3069 / 5925 / **3063** |

Worst difference 1.9 % (Lv 1, rounding of the old chain), under 1.1 % from Lv 10. By difficulty (wolf class, today -> new): Easy Lv 20
211 -> 212, Lv 40 469 -> 467; Normal 257 -> 258, 611 -> 609. Because same-level kill times are today's too (5.2), XP per hour at your
own level is today's on every difficulty (balance critic B5: the draft's "same XP on every difficulty" would have made Easy level
1.4-2x faster per hour than Hard). Same-level kills per class level stay today's (~11 / 18 / 26 at Lv 20 / 30 / 40, x1.0).

### 4.4 XP per second by level gap (DERIVED, ungeared Warrior, Hard; vs a same-level kill)

| | -10 | -5 | +5 | +10 | +20 |
|---|---|---|---|---|---|
| today, Lv 20 / 33 / 40 | x0.57 / x0.61 / x0.62 | x0.82 / x0.94 / x0.87 | x1.12 / x1.06 / x1.04 | x1.54 / x1.53 / x1.47 | x2.67 / x2.46 / x2.35 |
| **new, Skyy's locked rows** (free 5, 5 %) | x0.57 / **x1.10** / **x1.18** | x0.82 / **x1.21** / **x1.25** | x0.90 / x0.80 / x0.83 | x0.82 / x0.72 / x0.83 | x0.52 / x0.64 / x0.95 |
| new, free 3 / +8 % / -7.5 % (live rows, no build) | x0.36 / x0.70 / x0.74 | x0.70 / x1.03 / x1.06 | x1.05 / x0.93 / x0.97 | x1.03 / x0.90 / x1.04 | x0.71 / x0.86 / x1.28 |

Today out-levelled fights pay 1.5-2.7x per second (that is why the Lv 33 Yeti felt easy AND good XP). With the steep curve, mobs below
you die fast, so at Lv 30+ farming 5 levels below pays ~20 % more per second on the locked rows. The rows are LOCKED (2026-10-02), so
the default keeps them (Question 6); the third line is the recommended live change.

---

## 5. Target pacing (new defaults, Hard)

### 5.1 Assumptions (as numbers.md section 4)

Wolf class = Wolf_Black / Hyena / Wolf_White / Raptor_Cave (103 HP, bite 27, attack cycle 3.0 s; the same role stats in every zone,
numbers.md 1.4). Gear = best started metal, crafted at the player's level (max 49); class level = player level; Overall = level / 2;
**no gear stats, accessories or food** (gear stats are identical today and new, so a geared fight changes exactly like an ungeared one;
1.5); every hit lands; the mob attacks once per cycle; Mage / Priest start with a full Mana bar, fire charged shots, then quick shots
("q"), then wait for in-combat regen (2.5 / s, no perk). Priest = today's single-target wand (the class round's burst: x1 / 0.6 shots).
Mage -15 % = the class round's planned Glass Cannon health (PROPOSED there).

### 5.2 Same level, +10, +20, -10, per class (new; today's Hard in brackets)

| You | gap | mob Lv | mob HP | Warrior swings / s | Archer draws / s | Mage staff / s | Priest wand / s | mob bite after armor | your HP | bites to die / s | Mage at -15 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | +0 | 1 | 103 | 14 / 6.3 s [14] | 9 / 12.6 s [9] | 3 / 5.0 s [3] | 5 / 5.1 s [5] | 22 | 125 | 6 / 18 s [6] | 5 / 15 s |
| 1 | +10 | 11 | 185 | 28 / 13.1 s [25] | 18 / 25.2 s [16] | 5 / 8.3 s [4] | 9 / 9.2 s [8] | 33 | 125 | 4 / 12 s [5] | 4 / 12 s |
| 1 | +20 | 21 | 282 | 60 / 28.4 s [36] | 38 / 53.2 s [23] | 6+16q / 21.4 s [6] | 13+26q / 22.8 s [11] | 51 | 125 | 3 / 9 s [4] | 3 / 9 s |
| 10 | -10 | 1 | 103 | 7 / 3.2 s [7] | 5 / 7.0 s [5] | 1 / 1.7 s [1] | 1 / 1.0 s [1] | 20 | 154 | 8 / 24 s [8] | 7 / 21 s |
| 10 | +0 | 10 | 177 | 12 / 5.7 s [12] | 8 / 11.2 s [8] | 1 / 1.7 s [1] | 2 / 2.0 s [2] | 27 | 154 | 6 / 18 s [6] | 5 / 15 s |
| 10 | +10 | 20 | 259 | 19 / 8.8 s [17] | 12 / 16.8 s [11] | 2 / 3.3 s [2] | 3 / 3.1 s [3] | 38 | 154 | 5 / 15 s [5] | 4 / 12 s |
| 10 | +20 | 30 | 576 | 58 / 27.3 s [22] | 37 / 51.8 s [14] | 4 / 6.7 s [2] | 8 / 8.1 s [3] | 75 | 154 | 3 / 9 s [4] | 2 / 6 s |
| 20 | -10 | 10 | 177 | 9 / 4.3 s [9] | 6 / 8.4 s [6] | 1 / 1.7 s [1] | 1 / 1.0 s [1] | 25 | 169 | 7 / 21 s [7] | 6 / 18 s |
| 20 | +0 | 20 | 259 | 14 / 6.3 s [14] | 9 / 12.6 s [9] | 1 / 1.7 s [1] | 1 / 1.0 s [1] | 33 | 169 | 6 / 18 s [6] | 5 / 15 s |
| 20 | +10 | 30 | 576 | 34 / 15.9 s [18] | 22 / 30.8 s [12] | 1 / 1.7 s [1] | 2 / 2.0 s [1] | 61 | 169 | 3 / 9 s [5] | 3 / 9 s |
| 20 | +20 | 40 | 1357 | 111 / 52.5 s [22] | 71 / 99.4 s [14] | 3 / 5.0 s [1] | 5+4q / 6.5 s [2] | 114 | 169 | 2 / 6 s [4] | 2 / 6 s |
| 33 | -10 | 23 | 327 | 7 / 3.2 s [12] | 5 / 7.0 s [8] | 1 / 1.7 s [1] | 1 / 1.0 s [1] | 36 | 287 | 8 / 24 s [6] | 7 / 21 s |
| 33 | +0 | 33 | 757 | 16 / 7.4 s [16] | 10 / 14.0 s [10] | 1 / 1.7 s [1] | 1 / 1.0 s [1] | 61 | 287 | 5 / 15 s [5] | 5 / 15 s |
| 33 | +10 | 43 | 1742 | 40 / 18.8 s [19] | 26 / 36.4 s [12] | 2 / 3.3 s [1] | 3 / 3.1 s [1] | 107 | 287 | 3 / 9 s [5] | 3 / 9 s |
| 33 | +20 | 53 | 2692 | 87 / 41.1 s [23] | 55 / 77.0 s [14] | 3 / 5.0 s [1] | 5+3q / 10.7 s [1] | 171 | 287 | 2 / 6 s [4] | 2 / 6 s |
| 49 | -10 | 39 | 1261 | 9 / 4.3 s [14] | 6 / 8.4 s [9] | 1 / 1.7 s [1] | 1 / 1.0 s [1] | 75 | 554 | 8 / 24 s [6] | 7 / 21 s |
| 49 | +0 | 49 | 2525 | 17 / 7.8 s [17] | 11 / 15.4 s [11] | 1 / 1.7 s [1] | 2 / 2.0 s [1] | 121 | 554 | 5 / 15 s [5] | 4 / 12 s |
| 49 | +10 | 59 | 2943 | 22 / 10.3 s [19] | 14 / 19.6 s [12] | 1 / 1.7 s [1] | 2 / 2.0 s [1] | 147 | 554 | 4 / 12 s [5] | 4 / 12 s |
| 60 | +0 | 60 | 2984 | 19 / 8.8 s [19] | 12 / 16.8 s [12] | 1 / 1.7 s [1] | 2 / 2.0 s [1] | 138 | 558 | 5 / 15 s [5] | 4 / 12 s |

Reading it: every +0 row equals today's (the Priest's 2nd shot at Lv 49+ is spells keeping today's numbers). Out-levelled fights are
where it bites: +10 makes a kill 1.3-2.4x longer and you survive 3-4 bites instead of 5-6; +20 is a race only casters win solo (2.7).

### 5.3 Skyy's tests under the new rules (DERIVED; Skyy's Priest = Divinity 21, Overall 9, Iron Wand Lv 15, Fabled Iron armor Lv 15:
~165 HP, ~137 Mana, 27.9 % resistance - numbers.md 3.2 / 4.1)

| Test | Today | New |
|---|---|---|
| (2) "lvl 33 yeti with like 4 charged shots" (log: it was Lv 34; shot = 88 x F(15) 2.1667 x 1.045 x perk 1.042 = 207.6) | 823 HP, 4 shots; the Yeti hits 16.7 -> 10 hits | 1,795 HP, gap +13 -> 207.6 x 0.80 = 166 per shot -> **11 shots** (165 Mana: the whole bar + ~12 s regen); the Yeti hits 30.0 -> 6 hits |
| (3) Custom 20 / 8, Lv 32 Yeti "took like 8 hits" | 1,627 HP, 8 shots; hits 25.1 -> 7 | (Custom 20 / 8 is dropped) the Lv 32-34 Yeti is now 1,531-1,795 HP - close to what Skyy tested, but only from Lv 21 up |
| (1) "Lv ~19 mob ... i still 3 hit one" (Lv 19 Grizzly, 303 HP) | Copper wand 130 -> 3 shots, Iron 2; swipes 45 -> 4 hits | **unchanged** (Lv 19 is in the today's-Hard part, gap -2) |
| A true Lv 15 player vs a Lv 33 Yeti (gap +18, dealt x0.675) | - | Priest 8 charged + 20 quick (30 s, more than the bar); Mage 6 charged + 1 quick (11 s); Warrior 138 swings (65 s); Archer 89 draws (125 s); the Yeti (31 a hit) kills them in 6 hits (33 s), a -15 % Mage in 5 |
| Same Yeti at your own level (Lv 33 vs Lv 33) | 805 HP: Priest 2, Mage 1, Warrior 34 swings; 13 hits to die | 1,663 HP: Priest 3, Mage 2, Warrior 34 swings, Archer 22 draws; 13 hits to die |
| With the optional 15 % damage floor | - | the Lv 34 Yeti's base hit 34 -> ~102 on Skyy's Priest at +13 (2 hits); a Lv 33 player at the same level: 4 hits |

### 5.4 Other mobs

Kill times scale with max(base, 50) / 103 (a Yeti = x2.19, a Grizzly x1.20, a 36-HP skeleton x0.49); bites to die scale with 27 / the
mob's hit (Yeti 10 = x2.7 more hits, polar bear 46 = x0.59).

---

## 6. Server Setup rows and the one-time updates

Format = the config kit's row (tools/CONFIG-CONTRACT.md: key, label <= 40, category, type, default, min, max, opts, unit, flags, help
<= 100; tables `<valueType>;<none|...>;<Columns>`, entries via keys / tset / add / remove, hand-edited entries checked by the row's
`check=` hook). Every label / help below is within the character limits; the builds still measure them in pixels against SkyyMenu's
boxes (`menu_fit`, Mobs:1479-1497) and draw them with the real SkyyMenu jar. **Choice labels may only use letters, digits, spaces and
`< > / -`** (`menu_inl`, Mobs:1391-1403, turns anything else into a space and `menu_fit` refuses the label): hence "Per level", not the
draft's "Per-level %" (feasibility critic F5 - the build would have stopped).

### 6.1 SkyyMobs 0.1.4

Categories: `levels` Which mobs, `strength` Strength, **`curve` Level curve (new)**, **`gap` Level gap (new)**, `bands` Level bands,
`plate` Nameplate.

| Key | Label | Cat | Type | Default | Min-max | Unit | Flags | Help |
|---|---|---|---|---|---|---|---|---|
| strength.shape (NEW) | Strength shape | strength | choice `curve\|Level curve,linear\|Per level` | curve | | | live,danger | Level curve = the Level curve tab. Per level = the old % and cap rows (SkyyMobs 0.1.3). |
| strength.difficulty (help only) | Difficulty | strength | choice (unchanged) | normal | | | live | Picks the curve tables (Per level: Easy 4/2, Normal 6/3, Hard 8/4 %). Custom = your own. |
| strength.hp / .dmg (help only) | (unchanged) | strength | dec | 4 / 2 | 0-100 | % | live | Per level shape, Custom only: max health (damage) +this % per level above 1. |
| strength.hpCap / .dmgCap (help only) | (unchanged) | strength | dec | 6 / 3.5 | 1-100 | x | live | Per level shape only: health (damage) never goes above this multiple. |
| strength.floor, strength.healOnLoad | unchanged | | | 50 / false | | | | (the floor also applies in curve shape) |
| strength.dmgFloor (NEW) | Damage floor | strength | int | 0 | 0-100 | % of Lv 1 HP | live,danger | Mobs above Lv 20 hit players for at least this % of their Lv 1 health (full from Lv 30). 0 = off. |
| strength.hitCap (NEW) | One hit at most | strength | int | 0 | 0-100 | % of max HP | live,danger | A levelled mob's hit on a player (before armor) never exceeds this % of their max Health. 0 = off. |
| curve.hp.easy / .normal / .hard / .custom (NEW) | Health curve: <Difficulty> (4 rows) | curve | table `dec;none;Factor` | section 1.3 | 0.1-1000 | | live,danger | Mob health x this at each level (entry = level 0-100; straight lines between, flat after the last). |
| curve.dmg.easy / .normal / .hard / .custom (NEW) | Damage curve: <Difficulty> (4 rows) | curve | table `dec;none;Factor` | section 1.3 | 0.1-1000 | | live,danger | Mob damage x this at each level (entry = level 0-100; straight lines between, flat after the last). |
| part.gap (NEW) | Level gap | gap | bool | true | | | live,part,danger | Mobs above your class skill take less from you and hit you harder. Players vs mobs only. |
| gap.free (NEW) | Levels with no gap effect | gap | int | 5 | 0-100 | | live,danger | Mobs up to this many levels above your class skill fight normally (like the XP gap). |
| gap.dealtStep (NEW) | Your damage lost per level | gap | dec | 2.5 | 0-100 | % | live,danger | Each level past the free band: your hits on that mob deal this % less. |
| gap.dealtMin (NEW) | Your damage at least | gap | dec | 40 | 1-100 | % | live,danger | Your hits never drop below this % of normal, so no mob is immune. |
| gap.takenStep (NEW) | Damage taken per level | gap | dec | 1.5 | 0-100 | % | live,danger | Each level past the free band: that mob's hits on you deal this % more. |
| gap.takenMax (NEW) | Damage taken at most | gap | dec | 1.5 | 1-100 | x | live,danger | The gap never makes a mob's hits bigger than this multiple. |
| scale.role (NEW) | Fixed level by role | levels | table `int\|dec;none;Level\|Health x` | (empty) | 0-1000 (hook: Lv 0-100, x 0.1-100) | | live,danger | Bosses / special mobs: always this level (beats Never level these), Health x on top. 0 = off. |

Curve tables: `reload@config.properties:curve.hp.hard.;check=MobHooks.checkCurvePoint` (entry key a whole number 0-100, value 0.1-1000;
refusing to remove a table's last entry), the RELOAD routine `MobCfg.reloadAll` -> `derive` (live re-apply through 0.1.3's fixed
MobRefresh path); a table left empty by a hand edit falls back to its default points with one WARN. `scale.role`: entry = role id or
`Prefix*` (the `levels.exclude` pattern rules), check hook `MobHooks.checkScaleRole`.

### 6.2 SkyyGear (the curve version; the "base" = Level stats tab unless noted)

| Key | Label | Type | Default | Min-max | Flags | Help |
|---|---|---|---|---|---|---|
| base.curve (new default, new label) | Weapon curve F(L) | text | section 2.2 | 3-300 | live,danger | Weapon hits (swords, bows, axes ...): level:factor points. + the 0.2.1 placeholder suffix (Gear:2027) |
| base.spellCurve (NEW) | Spell curve S(L) | text | 1:1.0,4:1.6,10:2.0,40:3.0,100:5.0 | 3-300 | live,danger | Wand / staff / spellbook shots; their metal ladder adds the rest. + suffix |
| base.hpCurve (NEW) | Armor Health curve H(L) | text | section 2.2 | 3-300 | live,danger | Worn armor Health; keep it in step with mob damage. + suffix |
| steal.maxPerSec (NEW, `combat` tab next to steal.windowS) | Life Steal at most | dec | 5 | 0-100, unit `% max HP/s` | live | Life Steal heals at most this % of max Health per second (paid each steal window). 0 = no cap. |
| reforge.raiseLevel (NEW, `costs` tab next to cost.reforge) | Reforge raises the level | bool | true | | live | A reforge also raises the item to your level (never above its band's cap, never down). |

The three curves `check=GearCfg.checkCurve` (factor limit 100 unchanged, so the defaults stay readable by older jars).

### 6.3 SkyySkills 0.4.16

| Key | Label | Tab | Type | Default | Flags | Help |
|---|---|---|---|---|---|---|
| combat.xpFrom (NEW) | Kill XP comes from | combat | choice `level\|Mob level,health\|Mob health` | level | live | Mob level = Lv 1 health x the level curve x the difficulty share. Mob health = 0.4.15. |
| combat.levelCurve (NEW) | Kill XP level curve | combat | table `dec;none;Factor`, 0.1-1000, check hook | section 4.2 | live | Kill XP x this at each mob level (entry = level; straight lines between). Default = old Hard XP. |
| combat.levelBonus (new label + help) | Health mode: XP per mob level | combat | dec | 0.05 | live | Mob health mode only: kill XP x (1 + this x (mob level - 1)). |
| combat.levelXp.enabled (help only) | Kill XP by mob level | parts | bool | true | (unchanged) | Mob level mode: the level gap XP rows. Mob health mode: the level bonus + the gap rows. |
| combat.perHealth (help only) | (unchanged) | combat | dec | 0.2 | live | XP per Lv 1 health (Mob level mode) or per max health (Mob health mode). |
| mana.regen.perLevel (NEW) | Mana regen per class level | overall | dec | 7 (0-100, %) | live | Mana regen +this % of the vanilla refill per class level above the start level below. |
| mana.regen.fromLevel (NEW) | Mana regen growth starts at | overall | int | 20 (0-100) | live | The class level after which the Mana regen growth starts (21 = the first step). |

### 6.4 One-time updates (PROJECT-RULES: only lines still at the old default change; a verified History copy first; a change-log line
with Undo; a marker so it runs once; every other byte and the line endings kept)

**Decision table (feasibility critic F4)** - each mod decides alone (no cross-mod config reads at start-up); mismatches get a WARN:

| File state | SkyyMobs `strength.shape` | SkyyGear curves | SkyySkills |
|---|---|---|---|
| difficulty easy / normal / hard (or missing), caps default OR hand-set (Skyy: caps 20 / 6) | **curve** (+ Undo line); hand-set caps kept, inert in curve shape, named in the INFO line | base.curve at the old default -> new F; spell = old default; hp = new H | `combat.xpFrom=level`; levelCurve from the file's bonus / part |
| difficulty custom | **linear** (the owner's own % stays; no log line) | as above | as above (xpMult caps Custom at Hard's XP) |
| base.curve hand-set | (as above) | base.curve kept; spell = hp = THAT text (flat gear stays flat) | as above |
| `combat.levelBonus` hand-set / part off | | | levelCurve generated with B = that bonus / 0 |

**Runtime WARN (SkyyMobs, the existing one-shot `MobScanTask` at 15 s after start, Mobs:2707-2724 / :3405):** once, when shape = curve
and SkyyGear's `gear:fn:curve` is missing or F(40) < 2 x F(20) ("mobs above Lv 20 will out-grow players' gear: install SkyyGear
<curve version>+ or set Strength shape to Per level"), and once when shape = linear while F(40) >= 2 x F(20) ("players' gear out-grows the
mobs: set Strength shape to Level curve"). The manifest line "Zero dependencies" (Mobs:3426-3430) becomes "No dependencies (the Level
curve is made for SkyyGear's gear curves; use Per level without SkyyGear)".

**SkyyMobs 0.1.4 (`MobMig14`, before `MobCfg.load`, the MobMig 0.1.1 machinery):**
1. Marker comment `SkyyMobs 0.1.4 level curve` (a file whose comments hold it is never touched again; a fresh file carries it).
2. History snapshot "before the 0.1.4 level curve", verified in config-history before anything is written.
3. Right after the last `strength.*` entry: the marker, `strength.shape=<value>`, `strength.dmgFloor=0`, `strength.hitCap=0`, the 8
   curve tables (80 entry lines, defaults, a comment line per table), the gap block (defaults); after `levels.max` a comment line that
   explains `scale.role` (no entries). Each with its comment line. A key already in the file (any case) is kept and named in the INFO line.
4. `strength.shape` per the decision table; for `curve` ONE config-changes.log line `strength.shape  linear -> curve` (who "SkyyMobs
   0.1.4", via update), so Server Setup -> Changes -> Undo puts back 0.1.3's numbers.
5. Never touched: `strength.difficulty`, `strength.hp`, `strength.dmg`, both caps, `strength.floor`, bands, plates.

**Exactly what happens to Skyy's live file** (LF): `strength.difficulty=hard` stays -> the Hard tables; `strength.shape=curve` + one
Undo-able line; `strength.hp=20`, `strength.dmg=8`, `strength.hpCap=20`, `strength.dmgCap=6` stay byte for byte (hand-set; INFO line);
no floor line is added (code default 50). In game every loaded Lv 1-20 mob keeps its numbers exactly; Lv 21+ mobs get the new health on
chunk load (health percent kept, `strength.healOnLoad=false`) and the new damage at once. The save slot (`skyymobs_lv<N>` modifier key)
is unchanged - only its amount. **NOTE for the main session:** the task text said the live caps are x6 / x3.5 - the file says 20 / 6
(config-changes.log 21:40:20; 22:34:56-58 only `strength.difficulty`). They matter only if Skyy picks Per level again (x20 / x6, not
x6 / x3.5) - tell Skyy or ask whether to reset them; the update must not (hand-set).

**SkyyGear (`migrate0xx`, the migrate021 pattern):** marker `SkyyGear <version> level curves`; History "before the <version> level
curves"; `base.curve` still holding EXACTLY `1:1.0,4:1.6,10:2.0,40:3.0,100:5.0` -> the new F text (value only; key, separator, CR kept)
+ one change-log line `base.curve old -> new` (Undo); right after it `base.spellCurve` + `base.hpCurve` per the decision table;
`steal.maxPerSec=5` after `steal.windowS`, `reforge.raiseLevel=true` after the `cost.reforge` lines (new keys only). Skyy's live file has
the default (:242) -> new F, spells unchanged, new armor Health.

**SkyySkills 0.4.16 (appended block, the 0.4.14 `appendBlock` pattern, Skills:5028-5078):** marker `SkyySkills 0.4.16 kill XP by
level`; History first; appends `combat.xpFrom=level`, the 16 `combat.levelCurve.<L>` lines (generated as 4.2), `mana.regen.perLevel=7`,
`mana.regen.fromLevel=20`, with comments (only the lines the file lacks) + one change-log line `combat.xpFrom health -> level` (Undo =
0.4.15 XP). Skyy's xp.properties holds the default combat rows (live :20-22, :496-502) -> the default table; XP within 2 % of today.

---

## 7. Build plan

### 7.1 Mods, versions, order, round size

| # | Mod | Version | Base | What |
|---|---|---|---|---|
| 1 | SkyyMobs | **0.1.4** | a copy of the finished `SkyyMobs/build_skyymobs_0.1.3.py` (SkyyMobs has no patch scripts) | shape row + 8 curve tables + MobMig14; GapDamage (+ GapDamageU) and the taken factor in LevelDamage; dmgFloor (ramped, players only) + hitCap; `scale.role`; `mob:fn:info`; LevelCache (0 = unknown); /mobs inspect + /mobs info gap lines; the 15 s WARN; manifest text |
| 2 | SkyyGear | **the next free version** = 0.2.4 when 0.2.3 (gear craft Smithing XP) is the newest finished one; if tool levels already took 0.2.4, the next number (main session renumbers the queue: tool levels / loot move up one) | a copy of the newest FINISHED SkyyGear script (SkyyGear has no patch scripts) | new `base.curve` default + `base.spellCurve` + `base.hpCurve` + migration; `gear:fn:curve` bridge; `steal.maxPerSec`; `reforge.raiseLevel` |
| 3 | SkyySkills | **0.4.16** (or the next free one) | `tools/skills_0_4_16_patch.py` reading the GENERATED `SkyySkills/build_skyyskills_0.4.15.py` | `combat.xpFrom` + `combat.levelCurve` table; level-mode kill XP via `mob:fn:info` (double chain, xpMult, overrides on levelFactor, part = gap); fallbacks; Mana regen perk rows; the appended block |

- **Round size: FULL ROUND, ultracode** (PROJECT-RULES 4 / 8: three mods, saved-config migrations, coins via the reforge cost, combat
  numbers): 3 parallel builders (Opus) - the only contracts between them are `mob:fn:info` and `gear:fn:curve` (7.3); adversarial
  reviews per mod (Sonnet) + one numbers critic who re-derives sections 1.4 / 2.4 / 3.2 / 4.3 / 5.2 from the SHIPPED defaults; fix;
  cross-check (all SET jars in one JVM with `-Xverify:all`, the Adventurer audit, `python tools/ci/lint.py` 0 fails); pin; commit;
  deploy (the auto-deploy rule, game closed). Usage: check before launching (RESUME's weekly figure; wait for the reset if it is high).
- **Pairing (feasibility critic F3): deploy and roll back ALL THREE together.** SkyyMobs 0.1.4 with SkyySkills 0.4.15 pays health-mode XP
  on the new health (x3.2 at Lv 40); SkyyMobs 0.1.4 with an older SkyyGear = x13 mobs vs flat gear; the new SkyyGear with SkyyMobs 0.1.3
  = steep gear vs linear mobs. (SkyySkills 0.4.16 alone is safe: no `mob:fn:info` -> 0.4.15.) Main session: add a STOP to
  `tools/deploy_set.py` next to the SkyyArmory trio's (deploy_set.py:158-161): SkyyMobs >= 0.1.4 <=> SkyyGear >= <curve version>, and
  SkyyMobs >= 0.1.4 => SkyySkills >= 0.4.16. Each build STOPS when deploy_set.py pins it any other way (the SkyyArmory pattern,
  Armory header "DEPLOY").
- javassist: plain Java only (no lambdas / generics / varargs / autoboxing / enhanced-for / String switch / inner classes; methods before
  callers); ONE registerSystem per class (GapDamage + an unordered GapDamageU fallback, the LevelDamage / LevelDamageU pattern).
- **The class round** (SkyyArmory 0.1.1 + SkyyClasses 0.1.12: wand burst, Priest heal cap, Mage survival tool, class Health) may run in
  parallel and deploy in the same deploy when ready; its targets are in 2.7. Follow-ups: SkyyMenu's Mods list / help lines for the new
  /mobs texts (data only); the elites round updates Elites-Events-Spec 1.1 ("caps x6 / x3.5 at the end" does not fit curve shape: elite
  x2 / x1.3 go on top of the curve, its own cap vs the same-level mob) and multiplies its factor into `xpMult`; the boss round fills
  `scale.role`; the open party-share question gains a third option (pay only members who dealt >= 10 % of the mob's max health); the
  HANDOFF / TEST-CHECKLIST / RESUME / OPEN-QUESTIONS lines (main session).

### 7.2 Code touchpoints

**SkyyMobs 0.1.4**
- `MobCfg`: `SHAPE`; 8 curve point sets (volatile Object[]{double[] levels, double[] factors}, swapped whole) read from the
  `curve.<hp|dmg>.<difficulty>.*` keys (sorted by level; empty -> default + WARN); `eval` copied from Gear:6538-6550; `GAP_ON / GAP_FREE /
  GAP_DSTEP / GAP_DMIN / GAP_TSTEP / GAP_TMAX`, `DMG_FLOOR`, `HIT_CAP`, the `scale.role` entries; `hpMult` / `dmgMult` (Mobs:1800 /
  :1808): curve shape -> max(0.1, eval(the difficulty's points, level)), linear -> 0.1.3's code byte for byte; `hardRef(level)` (curve:
  the Hard health table; linear: min(hpCap, 1 + 0.08 (L - 1))) for xpMult; `derive` (Mobs:1686): the health signature (:1709) gets the
  shape + the active health table, so a change re-applies loaded mobs; `difficultyText` names the curve.
- Level source: `scale.role` is checked FIRST in `MobLevel.resolve` (before step 0 "saved"), so a fixed role always gets its row's
  level - also after an admin changes the row (the saved level is rewritten on the next apply); in the qualify check a `scale.role` match
  passes even when `levels.exclude` matches. The row's Health x multiplies the health amount (`hpAmount`).
- `MobGap` (pure): `dealt(d)`, `taken(d)`; `LevelCache`: uuid -> {level, time}, 2 s, filled from `class:skill:<uuid>` + `skill:fn:level`
  (the Mobs:3134-3149 read); no class -> -1 (no gap); a 0 / failed read -> keep the last good value, else no gap.
- `GapDamage` (DamageEventSystem, Filter group, BEFORE ArmorDamageReduction): skip cancelled / empty MOBS; attacker = a player
  (PlayerRef on the source ref; a ProjectileSource ref = the shooter), victim = a levelled mob in MOBS -> `setAmount(amount x dealt(d))`.
- `LevelDamage.handle` (Mobs:2610): for a player victim: floor (above Lv 20, ramped) -> x `dmgMult(level)` -> x taken(d) -> hit cap
  (victim max Health from its EntityStatMap); other victims: 0.1.3 exactly. The `i.level <= 1` early return stays (the floor starts above
  Lv 20, the gap needs d > 5).
- `MobInfo` (Mobs:1192) gets `base` (own base) and `xpBase` (max(base, floor)), filled where `setMult` already computes the base
  (apply :2337, refresh). Bridge `mob:fn:info` (7.3).
- `/mobs inspect`: "Health x7.94 (Hard curve, Lv 34) ... damage x3.72; level gap vs you +13: you deal 80 %, it deals 112 %"; `/mobs info`:
  the gap line for the band you stand in.
- `MobMig14` (6.4). Server Setup texts through `menu_fit`. The WARN in `MobScanTask`.

**SkyyGear (curve version)**
- `GearCfg`: `BASE_SPELL`, `BASE_HP` + parsing next to `BASE_CURVE` (Gear:3465-3480); `GearBase.curveS(lv)` / `curveH(lv)` beside
  `curveF` (Gear:6569); `mult(id, d, spell)` (Gear:6684): `spell ? curveS(lv) : curveF(lv)`; `armorTarget` (Gear:6819): Health x
  `curveH(lv)`. Every displayed number uses the same helpers: "Damage at Lv", "Spell at Lv", the 0.2.2 "Charged shot / Quick shot" lines
  (GearBase.shots), "Health at Lv", `/gear read` (GearBase.describe), gear:fn:describe.
- `kOf` stays on `curveF` (assert the multiplier at each family base's band start is unchanged; K itself changes for the own-base
  families at 30 / 35 - 2.2).
- "Spell" keeps 0.2.1's meaning (`weaponHit`: a SHOT from a wand / staff / spellbook); a melee swing of a spell weapon follows F, as today.
- `GearTick` Life Steal payout (Gear:9692-9697): `min(owed, maxPerSec / 100 x max Health x windowS)`; the rest is dropped (not carried).
- `GearForge` reforge (page + `/gear reroll`): with `reforge.raiseLevel` on, before `rollMods`: lvl = max(lvl, craftLevel(id, player))
  (not for `lvlA`), cost from the new level, the page line "Also raises it to Lv N"; gear:fn:sig follows the new level.
- Bridge `gear:fn:curve` (7.3). The migration (6.4); rows (6.2).

**SkyySkills 0.4.16 (patch)**
- `MobXp`: `FROM`, the level curve points (key-family table, a curvePts-like reader + `checkCurvePoint`); `infoOf(store, ref)` (the
  `levelOf` pattern, Skills:10974-10995) reading `mob:fn:info`; `kill` (Skills:11282): role override -> 0.4.15 maths; level mode with info
  -> one chance rounding of the 4.2 product; info function present + null -> `classXp(base)`; no info function -> 0.4.15 exactly;
  `PartyXp.share2` / `one2` the same helper.
- `ManaRegen.total(u)`: + perLevel x max(0, class level - fromLevel) (class level = `SkillStore.level(u, SkillClass.slot(u))`), inside
  the existing clamp; "Mana Regen: show mine" lists it as "class level".
- The appended block (6.4); rows (6.3).

### 7.3 Bridge contracts (new)

**`mob:fn:info` (SkyyMobs)** - `java.util.function.Function`: `Object[]{String world, java.util.UUID npc}` (or a bare UUID) ->
`Object[]{Integer level, Double base, Double xpBase, Double hpMult, Double dmgMult, Double xpMult}` or `null` (no level / unknown / wrong
world). base = the mob's own max health before our multiplier; xpBase = max(base, health floor) = its Lv 1 health; hpMult = the health
multiplier on the mob now (scale.role Health x included); dmgMult = `dmgMult(level)` now; xpMult = min(1, hpMult without the scale.role
factor / hardRef(level)) (an elite build multiplies its own factor in later). Any thread (reads MOBS), never throws; still answers at the
DeathComponent (the MOBS entry leaves with the entity, as `mob:fn:level`). `mob:fn:level` stays unchanged.

**`gear:fn:curve` (SkyyGear)** - `java.util.function.Function`: `Object[]{String which ("F" | "S" | "H" | "R"), Integer level}` -> `Double`
(the live curve value) or `null` (unknown name). Any thread, never throws. Used by SkyyMobs' WARN.

### 7.4 Harness checks (each mod's bare-JVM test, `-Xverify:all`, then all SET jars in one JVM)

- **SkyyMobs:** every 0.1.3 section carried; the 8 default tables reproduce 1.4 at every level 0-110 (Python reference, bit-exact);
  Lv 1-20 of each = SkyyMobs-0.1.3.jar's preset `hpMult` / `dmgMult` (float-exact); linear shape = 0.1.3 bit for bit; **the 1.2 rule**:
  with the model's fixed player (gear at min(L, 49)) same-level swings / draws / shots / hits-to-die equal 0.1.3's within 1 / 1 / 0 / 0.05
  at Lv 1-60 for every difficulty (the Priest exceptions listed in 1.2); gap factors d = -50 ... +100 (floor + cap); GapDamage /
  LevelDamage on real engine Damage objects: player -> mob scaled, projectile (ProjectileSource) scaled, mob -> player scaled (floor at
  Lv 20 / 25 / 30, hit cap), mob -> mob / pet / player -> player / cancelled untouched, no-class player = x1, a class level read of 0 = x1 and
  never overwrites a cached level; the Filter systems in both orders with the real SkyyGear GearHitSys / GearArmorSys + SkyyArmory
  ArmoryTuneSys + SkyySkills CombatDmgSys (same results); `scale.role` (an excluded Goblin_Duke row -> levelled, Health x applied; level 0
  = off); `mob:fn:info` answers (before / after a refresh, at death; xpMult Hard 1, Easy 0.62 at Lv 40, Custom 20/8 linear 1); live
  re-apply on a table edit through 0.1.3's network-queue path; MobMig14 on a copy of Skyy's live folder (expected bytes: marker + block +
  `strength.shape=curve` + 1 log line; difficulty / hp / dmg / caps untouched; LF kept; History +1; second start = no byte changed) +
  synthetic files (custom -> linear and no log line, missing keys, CRLF, marker present, keys already there); a hand-edited bad curve
  entry refused, an emptied table -> default + WARN; the WARN both ways (no gear:fn:curve; a flat F); Server Setup fit with the real
  SkyyMenu jar ("Per level" passes, "Per-level %" fails - negative control); Adventurer audit (no new commands: +0).
- **SkyyGear:** every spell number = the previous version's exactly (all wands / staffs / spellbooks, item levels 1-49, the 0.2.2 shot
  lines); the multiplier at every family base's band start unchanged (all families; K listed for the own-base ones); physical hits = K x
  F_new x bonus; armor Health = H_new; every tooltip number at item level 1-20 identical to the previous version; the three defaults
  readable by 0.2.1's `curvePts`; migration on Skyy's live copy (base.curve default -> new; spell = old default; hp = new; the two new
  rows) and on a hand-set base.curve (spell = hp = that text, base.curve kept); Life Steal payout capped (5 % x max HP x 3 s), 0 = old
  behaviour; reforge raises a Lv 25 Cobalt sword to 30 for a class-30 player, keeps a Lv 38 one at 38, never lowers, skips `lvlA`, cost
  from the new level, off = old behaviour; `gear:fn:curve` answers.
- **SkyySkills:** level mode on Hard + defaults = 0.4.15 XP within 2 % for every vanilla levelled role base at levels 1-60 (with the
  live multiplier 1.5); Easy / Normal = 0.4.15's Easy / Normal within 2 %; Custom 20 / 8 linear never above Hard; role overrides = 0.4.15
  exactly; part off = no gap in level mode; no `mob:fn:info` function = 0.4.15 exactly; function present + null = classXp; party share;
  the appended block on Skyy's live xp.properties copy (default table) + a synthetic file with levelBonus 0.1 / part off (generated
  table); Mana regen perk (class 20 = +0, 30 = +70 %, in combat x 50 %); the SkyyArmory pair guard still holds (0.4.16 >= 0.4.15).
- `python tools/ci/lint.py` 0 fails, lint --perm 0 fails, `tools/skyycfg_test.py` PASS, each build ends "assembled ...jar".

### 7.5 Rollback notes (for tools/deploy_set.py comments - main session)

- **All three together** (7.1 pairing). The primary SkyyGear route is the literal text: set `base.curve` back to
  `1:1.0,4:1.6,10:2.0,40:3.0,100:5.0` BEFORE pinning an older SkyyGear (older jars use base.curve for weapons, spells AND armor, so they
  would push spells onto the steep curve - a Lv 40 Mithril staff ~11,000 per shot); the History copy "before the <version> level curves"
  is the second route (each kit keeps only 10 versions: Gear:3212, Skills:13206, Mobs:1512 - ten live tweaks and it is gone). The 0.2
  rollback floor still applies.
- **SkyyMobs 0.1.4 -> 0.1.3:** 0.1.3 ignores the new keys and runs per level with the file's values (Skyy's file: Hard 8 / 4 with caps
  **20 / 6**); health re-applies on chunk load (percent kept); `scale.role` levels vanish (those mobs lose their plate on next load). Or
  keep 0.1.4 and Undo the `strength.shape` line.
- **SkyySkills 0.4.16 -> 0.4.15:** only together with SkyyMobs -> 0.1.3 (else health-mode XP on the new health). Keep the SkyyArmory pair
  (never below 0.4.15 with SkyyArmory 0.1). Players lose the Mana regen perk (no saved data).

### 7.6 In-game test steps (for TEST-CHECKLIST)

1. Server Setup -> Mobs: Strength tab shows "Strength shape: Level curve", Difficulty Hard, "Damage floor" 0, "One hit at most" 0; new
   tabs "Level curve" (8 table rows, "Open - 10 entries") and "Level gap" (6 rows); Which mobs shows "Fixed level by role - Open - 0
   entries"; Changes shows "strength.shape linear -> curve" with Undo.
2. `/mobs inspect` a Lv 1-20 mob: the same health as before (e.g. Lv 19 Grizzly 303 HP, Lv 8 Spider 95 HP) and "Hard curve".
3. `/mobs inspect` a Lv 30+ mob: e.g. Lv 34 Yeti 1,795 HP (was 823), damage x3.72; its health bar matches (0.1.3 fix).
4. Priest (Divinity 21) + Iron wand vs that Yeti: ~11 charged shots (was 4); `/mobs inspect` shows "level gap vs you +13: you deal 80 %,
   it deals 112 %". A mob within 5 levels shows no gap line. A same-level fight feels like before.
5. `/mobs info` in a higher biome names the gap ("these mobs are 8 to 12 levels above you: ...").
6. Gear tooltips: Lv 1-20 swords / bows / armor unchanged; a Lv 25+ Cobalt sword "Damage at Lv 25" ~24 % higher than before; a Lv 25
   Cobalt chestplate "Health at Lv 25: +36" (was +24); wand / staff "Charged shot" numbers unchanged.
7. Kill XP on Hard: a same-level wolf-class kill at Lv 20 pays ~455 Divinity XP with your x1.5 (today ~456); switch Difficulty to Easy,
   kill the same kind at the same level -> ~316 (today's Easy share); back to Hard.
8. Open "Health curve: Hard", change the 40 entry 13.18 -> 14 with levelled mobs in view -> their bars update at once, a hurt mob keeps
   its percent; set it back.
9. Part switch "Level gap" off -> the gap lines vanish and out-levelled hits deal full damage; switch it back on.
10. Undo the "strength.shape" change line -> mobs back to 0.1.3's numbers (Lv 34 Yeti 823 HP); redo.
11. Server Setup -> Gear -> Level stats: "Weapon curve F(L)", "Spell curve S(L)", "Armor Health curve H(L)" show their text and can be
    edited in the field (UNVERIFIED: a ~100-character value in the 270 px box) - change nothing, or set one back exactly.
12. Reforge a weapon made a few levels below your class skill: the page says "Also raises it to Lv N"; after it the tooltip shows Lv N.
13. (Admin) Fixed level by role -> add `Goblin_Duke*` = 30 | 1 -> a Duke spawned / reloaded shows [Lv 30]; remove the entry.

### 7.7 UNVERIFIED (needs the game)

- Real fight pacing: mob attack cadence (chase / back-off), every swing landing, kiting, the Warrior's shield blocks, i-frames.
- The class level read per hit (`skill:fn:level`) - code-read only; the 2 s cache keeps it off the hot path.
- `mob:fn:info` at the DeathComponent - relies on the MOBS entry lifetime SkyySkills already uses for `mob:fn:level` (Skills:10974-10995).
- SkyyMenu editing a ~100-character text row (SkyyGear) - Skyy has not edited base.curve in game yet.
- Multi-hit role entries (`Golem_Crystal_Sand` 6 x 47, `Wraith` 4 x 40 in numbers.md's mobs.json): if they are combos inside one attack,
  per-attack damage is several times the tables' (affects the hit cap's usefulness, not the curve).
- Where each excluded vanilla boss spawns (for the `scale.role` defaults of the boss round).
- That Rare is the typical rarity (Skyy's own set is Fabled); the reforge raise's feel on the coin economy.

---

## Appendix A. Critic findings - accepted / rejected (final editor, each checked against the code or re-run in the scratch model)

**Balance critic**

| # | Finding | Verdict |
|---|---|---|
| B1 | Tables assume ungeared players; "same pace as today" false at Lv 33-49; Lv 50-60 wall; x10 / x5 lock missed | **ACCEPTED, design changed:** the curve rule is now "today's preset pace at every level" (1.2) - the critic's rows through Lv 47, extended to Lv 60 by the same rule; verified at every level 1-60 on every difficulty. Rejected parts: the flat Lv 49-60 segment (breaks its own rule; kept as Question 8's alternative); the x10 / x5 line is superseded by LATEST (1.5, Question 1). |
| B2 | Priest stays strong at Lv 10-49; "gap shrinks Priest heals" false | **ACCEPTED:** 2.7 / 3.3 corrected (the cap binds from Lv 33); live hpPerMana 2 -> 1 now (section 0); a 12 %-of-max-Health per-hit cap is a class-round target. Not shipped in this deploy: SkyyClasses belongs to the class round (which may deploy together). |
| B3 | Caster sustain collapses from Lv 30 | **ACCEPTED:** Mana regen +7 % per class level above 20 in SkyySkills 0.4.16 (2.4; parity back to 1.0-1.9 vs today 1.1-1.6). |
| B4 | Same gap = wall for melee, speed bump for casters; no class Health row | **ACCEPTED as class-round targets** (frontier table + Warrior Health / Archer damage, 2.7). Rejected: a spell-only gap step (the critic's own numbers trim casters by 3-6 levels; one rule stays). |
| B5 | Same kill XP on every difficulty breaks difficulty neutrality; null-info fallback explodes | **ACCEPTED:** xpMult = min(1, health multiplier / Hard's) from `mob:fn:info` (4.2); fallback = the no-level path bounded by combat.max. Rejected: estimating Lv 1 health as max health / Hard curve (SkyySkills does not know the curve). |
| B6 | %-of-Lv-1-HP floor cannot fix Zones 1-3; use an absolute minimum 18 | **PARTLY:** the floor now ramps in above Lv 20 and hits players only (1.6). Rejected: the absolute minimum (swarm / trash mobs would hit like bruisers; after LATEST the Mage already "dies really easy"; the %-floor targets big soft hitters). |
| B7 | Gear goes stale faster; reforge should re-stamp | **ACCEPTED:** `reforge.raiseLevel` (2.6, Question 5). |
| B8 | Elites / bosses conflict | **ACCEPTED:** xpMult carries the elite factor later + a note for the elites spec (7.1); `scale.role` table now, empty (1.6, Question 9). |
| B9 | No per-hit cap; one-shots at +20 | **PARTLY:** `strength.hitCap` row, default off (a +20 one-shot is part of "Brutal"; the knob is there). |
| B10 | XP gap rows do not steer play | **PARTLY:** numbers in 4.4 + Question 6; the default keeps Skyy's LOCKED rows (live rows, no build). |
| B11 | Party XP leech stronger under the gap | **REJECTED as stated:** a member's XP is the same formula as today (only their combat contribution drops); the participation rule is passed on as an option for the existing open question (7.1). |
| B12 | Mage survival tool target | **ACCEPTED** as a class-round target (2.7). |
| - | "Checked and fine" list; live caps 20 / 6 | Agreed (6.4 NOTE). |

**Feasibility critic**

| # | Finding | Verdict |
|---|---|---|
| F1 | Unlevelled enemies get 6-13x easier | **ACCEPTED:** numbers in 2.8, `scale.role` now (empty default, boss round fills it), test step 13. Rejected: holding the gear curves back (nothing changes at Lv <= 20; a boss you out-level getting easy is normal; bosses meant for Lv 21+ get their level from `scale.role`). |
| F2a | Global XP multiplier dropped | **ACCEPTED:** MULT is inside the level-mode product (4.2); tests state x1.5. |
| F2b | Role overrides would ride the level curve | **ACCEPTED:** overrides keep 0.4.15's levelFactor maths. |
| F2c | Level mode behind `MobXp.ON` | **ACCEPTED:** in level mode the part switch gates only the gap; the table is generated with B = 0 when the part is off. |
| F2d | Hand-set levelBonus ignored | **ACCEPTED:** the one-time update builds the table from the file's bonus. |
| F3 | Pairing / rollback wrong; History keeps 10 | **ACCEPTED:** all three together, deploy_set STOP + build STOP, literal base.curve first (7.1, 7.5). Minor correction: deploy_set.py already has code STOPs for the Armory trio (:158-161), not prose only. |
| F4 | Updates decide independently; SkyyMobs "zero dependencies" | **ACCEPTED:** decision table + WARN both ways via `gear:fn:curve` + manifest text (6.4). |
| F5 | "Per-level %" fails `menu_fit` | **ACCEPTED:** "Per level" (verified: `menu_inl` drops `%`, Mobs:1391-1403, assert :1497). |
| F6 | A failed class-level read = full gap | **ACCEPTED:** 0 = unknown, never overwrites a cached level (3.1). |
| F7 | Life Steal uncapped and grows with mob health; DoT / thorns | **ACCEPTED:** `steal.maxPerSec` 5 (2.5); DoT / thorns note (2.8). |
| F8 | PvP shortens | **ACCEPTED as a note** (2.8; all 8 live worlds have PvP off). |
| F9 | "Every K unchanged" cannot hold; 2.3333 rounding | **ACCEPTED:** band-start assertion, K changes listed, `2.333333` (2.2). |
| F10 | dmgFloor misses Lv 1, hits mob-vs-mob | **ACCEPTED:** players only; the ramp starts above Lv 20, so the Lv 1 early return no longer matters (1.6). |
| F11 | levelCurve without check hook; long rows in a 270 px field | **ACCEPTED, differently:** SkyyMobs' 8 curves and SkyySkills' level curve are key-family tables (one entry per point, check hook per entry); SkyyGear's three curves stay text (base.curve's shipped format) with a test step. |
| - | "Checked, no problem" list (projectile shooter, damage order, Server Setup rows, migration machinery, overflow, K for based families, healing pools, live data) | Agreed. |
