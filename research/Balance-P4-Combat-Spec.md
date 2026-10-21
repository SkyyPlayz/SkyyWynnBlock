# Balance pass P4 - Combat core: mob curve, class stats, weight / speed, Mana / Stamina, class-tree check (BUILD-READY spec, 2026-10-20)

Phase P4 of research/Balance-Pass-Spec.md section 8 ("Combat core: class stats + weight / speed, Mana / Stamina, class trees + abilities, mob
curve, elites / bosses"). Mods: SkyyMobs, SkyySkills, SkyyClasses, SkyyTrees (data only), SkyyGear (player curves), SkyyArmory (weapon numbers).
Skyy 2026-10-20: "keep going down the list. dont stop until the entire list is done" + "if you have any doubt, do research to get good data
to base your default on". Spec only - nothing built, nothing committed. Where answers go: docs/answered/skills.md (combat lines) +
docs/answered/classes.md; this file holds the plan (the main session adds it to INDEX.md under research/). P5 (power sources) builds on Part 5.

**Goals used (Skyy's words, docs/answered/skills.md 2026-10-18, lines 185-191 + 173):** Normal = quick fights (about 4-6 hits trash, 12-15
tougher; trash needs 12-15 hits to kill you in starter armor - the accepted default text), Easy very fast, Hard slow Souls-like; elite 3x HP
1.5x dmg, mini boss 10x HP 2x dmg; full boss 3-4 min solo on Normal; +5 levels over = hard, +10 = a wall; all classes can solo, supports
slower; casters run dry every 20-30 s then 5-8 s of basic attacks to refill; class ratings SL / L / M / H / SH (research/Class-Roles-Sheet.md,
Skyy-approved) + a class WEIGHT that sets base speed (a heavy class is slowed much less by heavy gear); best gear ~3x plain ("About 3x" to
Q14 "Best gear = about 2x the damage and survivability of plain gear"); power split weapon 35 / armor 30 / accessories 20 / pets 15; "less
Mana" (10-18: "ive never ran out of mana on any class i tested").

**Legend.** VERIFIED = read in code / live config (cited). DERIVED = the scratch model (tools/dev/scratch/p4/p4model.py, deleted after; its
functions go into tools/balance_model.py, section 6.7). PROPOSED = a default this spec picks. UNVERIFIED = needs the game. W = checked on the
web 2026-10-20, K = my knowledge, not checked.

---

## 0. For Skyy (plain words)

1. **Found a big bug in today's numbers.** When we moved to 20 levels per zone (10-18), mob strength was stretched to the new levels but the
   weapon / armor strength curves were NOT. So a Lv 40 Cobalt sword hits like a Lv 40 item of the OLD scale (x9.6) while a Lv 40 mob only has
   the old Lv 30 health. Same-level fights today are **2x too fast at Lv 40, 3x at Lv 80, 4x at Lv 100**, and mobs barely hurt (DERIVED,
   section 1.1). Zone 1 is fine. P4 puts weapons, armor, spells and mobs back on ONE curve.
2. **One growth rule for Lv 20-100:** gear and mobs both grow +4.5 % a level (Wynncraft-like); Lv 1-20 stays exactly as today.
3. **Same-level fights (Normal, normal kit): trash ~4-5 hits, tough mobs ~12-13 hits, trash needs ~13 hits to kill you** - at every level.
   Easy: ~2-3 hits, you take ~24. Hard (Souls-like): ~7 hits, you die in ~8 (3-4 to a tough mob).
4. **Elites 3x Health / 1.5x damage, mini bosses 10x / 2x, full bosses a fixed big health pool (about 3.5 min solo for a mid-damage class).**
   Bosses finally get levels (Zone 1 guardian Lv 20 ... Zone 5 Lv 100).
5. **Levels above you:** +5 = about 2x as hard, +10 = about 4-5x (a wall), +15 = 11x+.
6. **Class stats from your ratings:** Warrior ~2x as tough as a Spellblade, a Mage ~0.75x; speed comes from the class (Assassin / Monk
   fastest, Warrior slowest) and heavy armor slows a Mage 18 % but a Warrior only 3 %.
7. **Mana:** casters empty in ~20-30 s of non-stop casting at every level, then refill fast (about 80 % of the bar in ~6-7 s of basic
   attacks). Mana per level for fighters is unchanged; their abilities get a little dearer per level so Mana matters (a full rotation =
   40-65 % of the bar). Mana regen growth per level goes DOWN (5 % -> 3 %) - your "less regen".
8. **Class trees:** a few upgrades stack too high (tree damage cap 80 % -> 40 %, damage-cut cap 50 % -> 35 %, 7 small number fixes);
   the tree stays one part of your power, not the main part.

---

## Research (short; W / K marked)

| Game | What it does | What we take |
|---|---|---|
| Wynncraft (K + Mob-Curve-Spec 1.4 fit, W there) | median mob HP ln-quadratic in level, ~6-8 % a level mid game; gear damage tracks it; Mana pool 20, spells 3-9 Mana, ~1 Mana/s -> 4-6 spells then a short wait | +4.5 % a level for both sides; casters burst then wait |
| Hypixel SkyBlock dungeons (K) | floors / Master Mode multiply mob HP and damage as flat factors on one curve; bosses = big fixed pools with phases | difficulty = flat factors on ONE curve (Easy / Hard columns); bosses = fixed pool |
| Diablo 3 / 4 (K; W for D4 1.1.1) | champion / elite packs ~2-4x HP with affixes; D4 patch 1.1.1 raised boss HP +50 % at Lv 80, +100 % at Lv 100 - bosses scale on their own table | elite 3x (Skyy), boss on its own fixed pool scaled by the level curve |
| Souls-likes (K) | trash dies in 3-6 hits; trash kills you in 4-8; bosses 2-5 min; no level gap rubber band | Hard = x1.6 Health, x1.8 damage on Normal |
| Borderlands (W: The Pre-Sequel UVHM regular x1.5 / Badass x2.5 HP; BL3 Mayhem players called high tiers "bullet sponges" and Gearbox lowered the health bonuses) | badass / elite multipliers ~2-3x; too-high HP multipliers feel bad | keep elite 3x, never stack rank + difficulty past ~5x on trash |
| WoW-style TTK (K) | solo quest mob 10-15 s; tank ~2.5-3x the effective HP of a cloth caster | class EHP spread SL 0.75 -> SH 2.0 (x2.6) |

Sources (W): Diablo 4 1.1.1 boss health - https://www.gosugamers.net/entertainment/news/68973-diablo-4-1-1-1-patch-notes-confirm-sorcerer-and-barbarian-buffs-boss-changes ;
Borderlands Mayhem / UVHM multipliers - https://www.gamerguides.com/borderlands-3/guide/endgame/mayhem-mode , https://www.co-optimus.com/article/12616/borderlands-the-pre-sequel-gets-ultimate-vault-hunter-mode-new-dlc.html ,
https://www.destructoid.com/?p=257979 . Mana research already in the repo: research/Mana-Cost-And-Regen-Research.md, research/Mana-Budget-2026-10-18.md.

---

## Part 1 - TTK targets, mob curve, elite / mini boss / boss

### 1.1 Today (VERIFIED + DERIVED)

- Gear curves (SkyyGear 0.3.33 `BASE_CURVE_NEW` line 3354, `BASE_HP_DEF` 3356, `BASE_SPELL_DEF` 3355) are still the Mob-Curve-Spec shape keyed to
  the OLD levels (Mithril = Lv 40-49): F(40) = 9.6, F(80) = 57, F(90+) = 90; `GearBase.mult` = K x F(item level) x (1 + 0.3 % x band start)
  (Gear 19310). Item levels are now the 20-per-zone bands (tools/tier_tags.py METAL_BANDS: Cobalt 40-48, Mithril 80-88, Onyxium 100-108).
- Mob tables (SkyyMobs 0.1.12 MobMig12) WERE stretched: old points 1 20 25 30 35 40 45 49 55 60 -> 1 20 30 40 47 53 60 65 73 80 (+100).
  Live: `strength.difficulty=normal`, `strength.shape=curve`, `strength.hitCap=35`, floor 50, gap free 5 / 2.5 / 40 / 1.5 / 1.5 (combat.md 6-136).
- DERIVED (model T1b, M class plain, live F + live stretched Normal table, vs Lv 20): hits to kill x0.48 at Lv 40, x0.63 at 60, x0.34 at 80,
  x0.24 at 100; hits to die x1.56 / 1.60 / 2.60 / 5.18. **Same-level fights get 2-4x faster and 1.5-5x safer from Zone 2 on.** Root cause:
  Level-Bands round re-banded items + mobs but not `base.curve` / `base.hpCurve` / `base.spellCurve`.
- Bosses / elites: `levels.exclude` holds Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss* (no level, no curve);
  `scale.role` exists (level|health x, empty); no elite / mini-boss multiplier exists. `bosses.roles` only drives Mythic bags.

### 1.2 THE RULE (PROPOSED)

- One growth factor **G = 1.045 a level from Lv 20** for the weapon curve F and the armor Health curve H; **Lv 1-20 unchanged** (Skyy's
  "feels good" zone, and already on the TTK targets - section 1.3).
  `F(L) = H(L) = today's points for L <= 20; 2.333333 x 1.045^(L - 20) above` (F(100) = 78.9 < SkyyGear's parser limit 100).
- **Mob Health(L) = today's Normal line to Lv 20, then x (F x bonus x class perk at L) / (the same at 20)** -> a same-level fight keeps the same
  number of hits at every level (bonus = 1 + 0.003 x band start, perk = 1 + 0.002 x class level).
- **Mob damage(L) = today's Normal line to Lv 20, then x EHP(L) / EHP(20)**, EHP = player max Health / (1 - resistance) of an M-class plain kit
  -> the same hits to die at every level.
- Difficulty = flat factors on that one Normal line (built into the tables, no code): **Easy x0.6 Health / x0.6 damage, Normal x1.0 / x1.1,
  Hard x1.6 / x1.8.** Normal damage x1.1 = the M class Defense 10 (Part 2) so an M class keeps today's hits to die.
- **`strength.floor` 50 -> 70** (only lifts weak mobs = trash: skeletons 36 -> 70 base): trash = 4-5 hits instead of 3 with an expected kit.

### 1.3 TTK targets per tier and difficulty (DERIVED, model T2 / T2b; kit: plain = fresh Common at level, expected = halfway (x1.73
DPS and EHP), best = x3)

"Hits" = the main attack of an M-damage melee class (sword swing ~0.45 s, K/UNVERIFIED animation time). Other classes: same seconds x their
Damage rating (section 2.2), so their hit counts differ by weapon speed (Part 2, 2.4 gives the class damage factors that make it so).

| Normal, same level | plain | **expected** | best | seconds (expected, M) | hits to die (M, plain armor) |
|---|---|---|---|---|---|
| Trash (base <= 70 HP, floor) | 7.6 | **4.4** | 2.5 | 2.0 s | **12.9** |
| Tough (base ~200, bears / Yeti / golems) | 21.8 | **12.6** | 7.3 | 5.6 s | 5.7 |
| Elite trash (x3 / x1.5) | - | 13 | - | 6.6 s | 8.6 |
| Mini boss (tough base, x10 / x2) | - | - | - | 75 s (1.3 min) | 2.9 (plain) / 5.0 (expected) |
| Full boss (fixed pool, x2 dmg) | - | - | - | **212 s (3.5 min)** | 5.1 / 8.8 (Warrior SH) |

| Difficulty (Lv 50, M class, expected) | trash hits | tough hits | boss | trash hits to die | tough hits to die |
|---|---|---|---|---|---|
| Easy (very fast) | 2.6 | 7.5 | 2.1 min | 23.7 | 10.5 |
| **Normal (quick)** | **4.4** | **12.6** | **3.5 min** | **12.9** | **5.7** |
| Hard (Souls-like) | 7.0 | 20.1 | 5.6 min | 7.9 | 3.5 |

Per class at Lv 50 (expected kit, Normal): boss solo Warrior 3.5 min, Berserker / Spellblade / Archer 2.8, Assassin / Mage 2.4, Priest 4.7
(support - slower solo, Skyy's rule). Numbers are flat from Lv 1 to 100 by construction (the RULE); Lv 1-20 differ by < 15 %.

### 1.4 Curves (exact text; PROPOSED defaults)

**SkyyGear** (`base.curve` = F, `base.hpCurve` = H; same points):
`1:1,4:1.6,10:2,20:2.333333,30:3.624,40:5.627,50:8.739,60:13.572,70:21.076,80:32.731,90:50.83,100:78.937`

**SkyyGear `base.spellCurve` S** - spells ride SkyyArmory's metal ladder (charged = 25 / 50 x (1.25 x cost multiple - 0.25)), so S is set so
that each metal's charged shot vs a same-level mob keeps today's pre-re-band ratio at the metal's band start (DERIVED T7):
`1:1,8:1.67,20:2.333333,40:4.67,60:6.07,80:10.99,100:28.75` (today 1:1,4:1.6,10:2,40:3,100:5). Thorium (Lv 20) unchanged; Iron -11 %;
Cobalt x1.56, Adamantite x1.65, Mithril x2.5, Onyxium x5.8 vs today's S at those levels (today's late spells were far too weak relative to the
new mobs; Onyxium's charged cost = Mithril's 85 in `WANDS`, so its S point carries the whole gap). Points between band starts are linear.

`base.resCurve` unchanged (1:1, 10:1.4, 20:1.7, 40:2.2, 100:3).

**SkyyMobs tables** (`curve.<hp|dmg>.<difficulty>.<L>`, 21 points each; Custom = a copy of Normal; exact file values):
```
curve.hp.easy:    1=0.6, 5=0.74, 10=0.92, 15=1.1, 20=1.28, 25=1.62, 30=2.08, 35=2.67, 40=3.4, 45=4.27, 50=5.49, 55=7.03, 60=8.95, 65=11.26, 70=14.44, 75=18.47, 80=23.5, 85=29.54, 90=37.84, 95=48.35, 100=61.47
curve.dmg.easy:   1=0.6, 5=0.67, 10=0.76, 15=0.85, 20=0.94, 25=1.07, 30=1.25, 35=1.46, 40=1.74, 45=2.04, 50=2.46, 55=2.99, 60=3.65, 65=4.46, 70=5.58, 75=7.01, 80=8.83, 85=11.05, 90=14.15, 95=18.14, 100=23.24
curve.hp.normal:  1=1, 5=1.24, 10=1.54, 15=1.84, 20=2.14, 25=2.69, 30=3.46, 35=4.44, 40=5.66, 45=7.12, 50=9.15, 55=11.72, 60=14.92, 65=18.76, 70=24.07, 75=30.78, 80=39.17, 85=49.23, 90=63.07, 95=80.58, 100=102.45
curve.dmg.normal: 1=1.1, 5=1.23, 10=1.4, 15=1.56, 20=1.73, 25=1.96, 30=2.28, 35=2.69, 40=3.19, 45=3.75, 50=4.51, 55=5.48, 60=6.7, 65=8.18, 70=10.22, 75=12.85, 80=16.18, 85=20.26, 90=25.93, 95=33.26, 100=42.6
curve.hp.hard:    1=1.6, 5=1.98, 10=2.46, 15=2.94, 20=3.42, 25=4.31, 30=5.54, 35=7.11, 40=9.06, 45=11.4, 50=14.64, 55=18.75, 60=23.88, 65=30.02, 70=38.51, 75=49.25, 80=62.67, 85=78.77, 90=100.92, 95=128.93, 100=163.92
curve.dmg.hard:   1=1.8, 5=2.02, 10=2.29, 15=2.56, 20=2.83, 25=3.21, 30=3.74, 35=4.39, 40=5.22, 45=6.13, 50=7.38, 55=8.97, 60=10.96, 65=13.38, 70=16.73, 75=21.02, 80=26.48, 85=33.15, 90=42.44, 95=54.42, 100=69.71
```
The build computes these from the RULE (functions in balance_model.py) and asserts them (+-0.01); never hand-type.

### 1.5 Lv 1-100 table (DERIVED; Normal multipliers on a mob's base; player = M class plain kit)

| Lv | F today -> new | mob Health today -> new | mob dmg today -> new | player max HP (M plain) |
|---|---|---|---|---|
| 1 | 1.00 -> 1.00 | 1.00 -> 1.00 | 1.00 -> 1.10 | 125 |
| 10 | 2.00 -> 2.00 | 1.54 -> 1.54 | 1.27 -> 1.40 | 155 |
| 20 | 2.33 -> 2.33 | 2.14 -> 2.14 | 1.57 -> 1.73 | 169 |
| 30 | 4.50 -> 3.62 | 3.03 -> 3.46 | 2.04 -> 2.28 | 209 |
| 40 | 9.60 -> 5.63 | 4.62 -> 5.66 | 2.62 -> 3.19 | 272 |
| 50 | 17.5 -> 8.74 | 8.83 -> 9.15 | 3.77 -> 4.51 | 367 |
| 60 | 22.5 -> 13.57 | 15.63 -> 14.92 | 5.39 -> 6.70 | 521 |
| 70 | 36.0 -> 21.08 | 20.80 -> 24.07 | 6.72 -> 10.22 | 759 |
| 80 | 57.0 -> 32.73 | 23.00 -> 39.17 | 7.24 -> 16.18 | 1143 |
| 90 | 90.0 -> 50.83 | 25.28 -> 63.07 | 7.76 -> 25.93 | 1738 |
| 100 | 90.0 -> 78.94 | 27.56 -> 102.45 | 8.29 -> 42.60 | 2700 |

**What players will feel (UNVERIFIED, test step 2):** an item made at Lv 25-100 hits 20-55 % less than today (e.g. a Lv 40 sword -41 %) while
Zone 2+ mobs gain up to x3.7 Health by Lv 100 - Zone 2+ fights take ~2x longer than today = back on target. Zone 1 unchanged.

### 1.6 Level gap (PROPOSED, SkyyMobs rows) - "+5 hard, +10 wall"

`gap.free` 5 -> **3**, `gap.dealtStep` 2.5 -> **5**, `gap.dealtMin` 40 (keep), `gap.takenStep` 1.5 -> **3**, `gap.takenMax` 1.5 (keep).
DERIVED (T4, "as hard" = kill time x damage taken): +3 x1.3, **+5 x1.8-1.9, +10 x4.3-4.8**, +15 x11-14, +20 x20-25 (Lv 30 / 70).
(Today's rows with the new curve: +5 x1.5, +10 x2.7 - not a wall.) SkyySkills' XP gap rows (`combat.gap.*`) are P3's, unchanged.

### 1.7 Elites, mini bosses, bosses (PROPOSED)

New SkyyMobs rows (Server Setup -> Mobs -> "Ranks", a new tab on the Which mobs page per research/Menu-Pattern.md):

| Key | Default | Meaning |
|---|---|---|
| `rank.elite.roles` | `*_Elite*, *Captain*, *Champion*, *Alpha*, *Brute*` (= SkyyClasses `ab.GodKiller.eliteWords`) | roles that are elites |
| `rank.elite.hp` / `rank.elite.dmg` | 3 / 1.5 | x on the levelled Health / damage (Skyy Q7) |
| `rank.elite.chance` / `rank.elite.levels` | 3 % / +3 | any levelled normal mob rolls elite (R5 LOCKED 2026-09 "elites later 3% / +3 levels"; multipliers now Skyy's 3x / 1.5x) |
| `rank.mini.roles` | `` (empty) + mob:fn:setLevel mobs that ask for "mini" (SkyyIslands' Shardkeeper) | mini bosses |
| `rank.mini.hp` / `rank.mini.dmg` | 10 / 2 | Skyy Q7 |
| `rank.boss.base` | 4500 | a full boss's Health BEFORE the curve (replaces its own base, so every boss lasts the same); DERIVED: 3.5 min for an M class, expected kit, 60 % uptime |
| `rank.boss.dmg` | 2 | x on the boss's own hits |
| `scale.role` (exists) | gets a 3rd column `damage x` (default 1; old 2-column lines keep working) + defaults below | fixed level per role |

`scale.role` defaults (PROPOSED; zone tops = tools/tier_tags.py ZONE_TOPS; research/cloud/Zone-Bosses-Ideas.md mapped 20/30/45/60 -> 20/40/60/80):
`Trork_Chieftain=18,1`, `Goblin_Duke*=38,1`, `Skeleton_Elite*=+band` (no row: elites take their band's roll + rank), `Dragon_Frost=78,1`,
`Dragon_Fire=98,1` (zone guardians from the boss round fill Lv 20 / 40 / 60 / 80 / 100). Bosses leave `levels.exclude` (Goblin_Duke*,
Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss* removed by the migration when the line is still the 0.1.12 default text).
Kill XP of ranked mobs = kill XP x min(rank hp, 10) (P3's kill-XP rule reads mob:fn:info's xpMult; boss XP capped at x10 of a same-level kill).
UNVERIFIED: where each vanilla boss spawns (Mob-Curve-Spec 2.8).

---

## Part 2 - Class stat table (SL..SH -> numbers) + weight x armor speed

### 2.1 The mapping (PROPOSED)

| Rating | SL | L | M | H | SH |
|---|---|---|---|---|---|
| Health (% of max Health) | -20 | -10 | 0 | +15 | +35 |
| Defense (flat, hits x 100 / (100 + Def), adds to gear / perk Defense) | 0 | 5 | 10 | 25 | 45 |
| Damage (x the M reference DPS, class weapon vs monsters) | 0.55 | 0.75 | 1.0 | 1.25 | 1.5 |
| Speed (% move speed in the class's OWN armor type) | -12 | -6 | 0 | +6 | +12 |
| Weight (x how much each armor load point slows; 4 % per point) | 2.0 | 1.5 | 1.0 | 0.5 | 0.25 |
| Stamina (base on top of vanilla 10 / per class level) | 2 / 0.03 | 4 / 0.05 | 7 / 0.09 | 10 / 0.13 | 13 / 0.17 |
| Mana | section 3 (set by the Mana budget, not a flat table) | | | | |

EHP (Health x Defense) vs M: SL 0.80, L 0.95, M 1.0 (x1.1 baked into Normal damage), H 1.44 / 1.1 = 1.31, SH 1.96 / 1.1 = 1.78; Warrior /
Mage = 2.45x (WoW-style tank / cloth ~2.5-3x, K).

### 2.2 Per class (PROPOSED; ratings = research/Class-Roles-Sheet.md)

| Class | Weight | Health % | Defense | Stamina base / lv | Speed (own armor) | Native armor | Damage x | Hits to die trash / tough (Normal, plain) |
|---|---|---|---|---|---|---|---|---|
| Warrior | SH | +35 | 45 | 10 / 0.13 (H) | -6 % | Heavy | 1.0 | 23.0 / 10.2 |
| Berserker | H | +15 | 10 | 13 / 0.17 (SH) | 0 % | Heavy | 1.25 | 14.8 / 6.6 |
| Spellblade | M | 0 | 10 | 7 / 0.09 (M) | 0 % | Light (Q3) | 1.25 | 12.9 / 5.7 |
| Monk | L | 0 | 5 | 13 / 0.17 (SH) | +12 % | Light | 1.0 | 12.3 / 5.5 |
| Assassin | SL | -10 | 5 | 10 / 0.13 (H) | +12 % | Light | 1.5 (single target) | 11.1 / 4.9 |
| Archer | L | 0 | 10 | 10 / 0.13 (H) | +6 % | Light | 1.25 | 12.9 / 5.7 |
| Mage | SL | -20 | 0 | 4 / 0.05 (L) | +6 % | Cloth | 1.5 | 9.4 / 4.2 |
| Priest | L | 0 | 10 | 4 / 0.05 (L) | +6 % | Cloth | 0.75 | 12.9 / 5.7 |

Stamina today -> new: Berserker 12 / 0.16 -> 13 / 0.17, Monk 10 / 0.13 -> 13 / 0.17, Assassin 9 / 0.12 -> 10 / 0.13, Archer 9 / 0.12 -> 10 /
0.13, Priest 5 / 0.06 -> 4 / 0.05, Spellblade 7 / 0.09, Warrior 10 / 0.13, Mage 4 / 0.05 unchanged. `classBoost.*` (the small "more
balanced at 100" table) stays as is.

### 2.3 Weight x armor = speed (PROPOSED rule)

- Armor load = sum over worn pieces of slot share x type load; slot share Head 0.20, Chest 0.35, Legs 0.30, Hands 0.15 (sums to 1); type
  load Cloth 0, Light 1, Heavy 3 (SkyyGear `GearView.weightOf(id)`: 1 Heavy / 2 Light / 3 Cloth, the tooltip rule - Gear 22786).
- Speed % = class base + (-4 % x load x weight factor). Class base = the rated speed + the native armor's full-set slow, so the rating holds
  in the class's own armor. Lighter than native = faster.
- DERIVED (T5; full set): Warrior base -3: cloth -3 / light -4 / heavy -6 (heavy costs only 3 %). Berserker +6: +6 / +4 / 0. Spellblade +4:
  +4 / 0 / -8. Monk +18: +18 / +12 / 0. Assassin +20: +20 / +12 / -4. Archer +12: +12 / +6 / -6. Mage +6: +6 / -2 / **-18**. Priest +6: +6 / 0 / -12.
  Skyy's rule "a super-light class has at least High speed" holds (Mage +6 = H, Assassin +12 = SH).
- Applied through the shared movement protocol (tools/skyymove.py): new source `skills.classweight`, layer flat, posted by SkyySkills each
  second (it already ticks Perks per second and is a protocol applier). Total-speed ceiling: new SkyySkills row `move.maxFactor` 1.8 (the
  protocol clamps at 5.0 today; Monk tree + Flowing Form + Acrobatics + talismans could pass +100 %, Part 4).

### 2.4 Class damage factor (PROPOSED + measurement rule)

New SkyySkills table `class.damage.<Class>` (% on class-weapon hits vs monsters, applied in CombatDmgSys next to `perk.combat.damagePerLevel`;
never vs players). It turns each class's MEASURED weapon DPS into its rated DPS: `class.damage = 100 x rating x REF / measured`, REF = the
Warrior Copper sword at Lv 1 (6 / 6 / 11 per swing, ~0.45 s, 17.0 DPS - Mob-Curve-Spec 5.2). First-pass defaults: Warrior 100, Archer
**200** (Mob-Curve-Spec 5.2: Archer kills in 12.6 s vs Warrior 6.3 s; H wants 1.25x the Warrior), Mage 100, Priest 100 (casters: their
spell ladder + S + the Mana budget decide; Mage burst already >1.5x), Berserker / Spellblade / Monk / Assassin 100 **UNVERIFIED** - the P4
build harness reads each starter weapon's per-swing damage + interaction time from Assets.zip (SkyyGear already reads `ratio(id)`), computes
DPS at Lv 1 / 20 / 50, writes the factor and prints the table; a factor outside 60-250 stops the build for review.

---

## Part 3 - Mana / Stamina budget ("runs out every 20-30 s, then 5-8 s of basics")

### 3.1 Benchmark (DERIVED; tools/dev/scratch/p4/final.py -> balance_model.py)

Non-stop casting = every owned ability the moment its cooldown ends (A1 Lv 1, A2 10, A2-alt 20, A1-alts 30 / 40; live walking rows) + a
charged band-weapon shot every 4 s (Mage staff = 2 x wand cost, Priest wand; SkyyArmory `WANDS` ladder, band by tools/tier_tags.py), quick
shots between. In-combat regen = 3.33 / s x (1 + regen growth) x 65 %. No tree / gear / accessory / pet Mana (that is extra headroom).

### 3.2 Changes (PROPOSED)

| Row (mod) | Today | New |
|---|---|---|
| `mana.regen.perLevel` (Skills) | 5 % a level above 20 | **3** (Skyy: "and mana regen a little") |
| `mana.classBase.Mage` / `mana.classPerLevel.Mage` | 45 / 9.5 | **80** / 9.5 |
| `mana.classBase.Priest` / `.classPerLevel.Priest` | 42 / 4.5 | **40 / 7** |
| `mana.classBase.Spellblade` / `.classPerLevel.Spellblade` | 33 / 3 | **50** / 3 |
| NEW `mana.regen.class.<Class>` (Skills, % of regen) | - | Spellblade **50**, others 100 |
| Spellblade ability Mana (Classes `ab.<Id>.numbers` mana=) | Breach 8, Imbue 7, Sunder 9, Rift Cleave 10, Arc 9 | **16, 14, 18, 20, 18** |
| NEW `abil.costPerLevel.<Class>` (Classes, % more ability Mana per class level) | - | Mage 0, Priest 1, all others **1.5** (Lv 100 = x2.5) |
| NEW `mana.refillPct.<Class>` + `mana.refillDelay` (Skills) | - | Mage / Priest / Spellblade **15** % of max Mana a second, others 0; delay **1** s after the last charged shot or ability |
| Fighters' pools (`mana.classBase` / `classPerLevel` Archer, Warrior, Assassin, Monk, Berserker) | 24 / 21 / 24 / 21 / 12, 1 a level | unchanged |

Refill: SkyySkills ManaRegen adds the refill as one more source while in combat and `now - lastCast >= refillDelay`; SkyyClasses (ability
cast) and SkyyArmory (charged shot, not quick) call the existing registry `skill:fn:manaregen` with `{"cast", uuid}` to restart the delay.
Quick shots keep their 1/5 cost, so a refilling caster still pays ~3-4 % of the bar a second for quicks: net ~11 %/s -> **~80 % of the bar
back in ~7 s** of basic attacks (Skyy's 5-8 s).

### 3.3 Proof (DERIVED; seconds to empty at Lv 1 / 5 / 10 / 20 / 30 / 40 / 60 / 80 / 100; [one full ability rotation as % of the bar at Lv 5 / 20 / 40 / 60 / 100])

| Class | Today (regen +5 %) | **New** | Rotation share (new) |
|---|---|---|---|
| Mage | 12 / 21 / 18 / 16 / 19 / 20 / 21 / 20 / 27 | **20 / 29 / 22 / 19 / 21 / 21 / 21 / 20 / 25** | 18 / 26 / 23 / 17 / 10 % |
| Priest | 18 / 25 / 19 / 17 / 19 / 19 / 21 / 22 / 30 | **18 / 28 / 22 / 20 / 22 / 21 / 23 / 23 / 28** | 25 / 42 / 44 / 35 / 27 % |
| Spellblade | never (776 s at Lv 20) | **25 / 28 / 23 / 23 / 21 / 20 / 24 / 27 / 29** | 26 / 56 / 79 / 69 / 60 % |
| Warrior | never (rotation 19-37 %) | never - cooldown-gated (Stamina class) | 20 / 42 / 59 / 52 / 46 % |
| Berserker | never | never | 18 / 34 / 54 / 46 / 39 % |
| Monk | never | never | 8 / 27 / 47 / 41 / 36 % |
| Assassin | never | never | 22 / 48 / 56 / 51 / 45 % |
| Archer | never | never | 15 / 42 / 66 / 59 / 52 % |

Reading it: the three casters (Class-Roles-Sheet: "Casters run dry every 20-30 s") empty in 18-29 s at every level; the Lv 1 Priest (18 s)
and Lv 20 Mage (19 s, the Thorium staff step) are the edges. Fighters never run dry by design (their abilities are cooldown-gated and they
lean on Stamina), but a full rotation now costs 40-65 % of the bar from Lv 20 (today 11-37 %), so Mana is a real limit on doubling up.
Max pools (new): Mage 90 / 272 / 560 / 1040 at Lv 1 / 20 / 50 / 100; Priest 47 / 182 / 395 / 750; Spellblade 53 / 112 / 205 / 360.
Why Mage / Priest pools grow (against "less Mana"): with the band weapon today's casters empty in 12-21 s - FASTER than the target. Skyy
never ran out because the regen growth (+5 % a level) outran older / cheaper weapons and slower casting (research/Mana-Budget-2026-10-18.md
finding 2). The fix cuts the regen growth (less regen) and only lifts the low-level base. Full Mage tree (+16 % Mana, +20 % regen): 23-37 s.
SkyyArmory `check.share` 40: every charged shot stays under 40 % of the new pools at its band start (the build asserts it).

### 3.4 Stamina (PROPOSED target, UNVERIFIED numbers)

Stamina classes (Monk, Berserker SH; Warrior, Assassin, Archer H) chain about 6-8 dodges / sprint bursts / Stamina abilities before a
4-6 s recovery; L classes (Mage, Priest) 2-3. The table in 2.2 sets the pools; dodge cost and vanilla Stamina regen are engine values the
build harness must read (Assets.zip `Stamina` stat + the dodge interaction cost) and print as "dodges before empty" per class at Lv 1 / 50 /
100 - if any SH class is under 6 or any L class over 4, report it (no auto-tune).

---

## Part 4 - Class-tree numbers check (Classes 0.1.43 / tools/trees_v3_data.py CLASS_FX)

Budget (PROPOSED): the tree is ONE of five layers (class level + tree, weapon, armor, accessories, pets). One branch (about 30-37 points =
Lv 30-40 in run 1) may add **at most +25-30 % to its focus** (damage, damage taken, healing); the whole tree at Lv 100 at most +40 %.
Totals below = max ranks x per rank summed over the tree (DERIVED, tools/dev/scratch/p4/treesum.py). Points: 1 a class level (cap 50 in
run 1, so about half of a 93-112 rank tree).

| # | Finding | Today | Fix (PROPOSED) | Where |
|---|---|---|---|---|
| T1 | All tree damage bonuses on one hit capped at +80 % | `UpFx.DMG_CAP` 80 / row `ab.ClassTree.numbers dmgCap=80` | **dmgCap 40** | Classes 0.1.44 default + migration |
| T2 | Damage-cut stack: Warrior drMelee 20 + drStill 15 + drRanged 9 on top of SH Defense 45 + Health +35 % -> 50+ trash hits | `drCap` 50 | **drCap 35**; Warrior b1.r5b drStill 5 -> **3** a rank (max 9) | Classes row + trees_v3_data |
| T3 | Archer Focus Fire: dmgFocus 2 % a hit x 5 hits x 3 ranks = +30 % (with dmgBow 12 + dmgFar 15 + dmgMarked 10 = +67 %) | 2 | **1** a rank (max +15 % at 5 hits) | trees_v3_data Archer.b1.r5b |
| T4 | Assassin vs bosses: dmgElite 15 + dmgBehind 16 + dmgDebuff 12 + bigHitBuff 6 + lethal 7.5 % avg -> boss in ~1.3 min (target 3-4) | dmgElite 5 a rank | **dmgElite 3** a rank (max 9 %); lethal stays (DMG_CAP 40 binds the rest) | Assassin.b2.r5b |
| T5 | Spellblade momChance 20 % x 5 = 100 %: every hit gives Momentum, the upgrade's choice disappears | 20 | **12** a rank (max 60 %) | Spellblade.b3.r1a |
| T6 | Monk speed: move 20 + flowMove 15 + Flowing Form 2 % x 20 stacks + class base +18 (new) -> > +90 % | move 4 a rank | **move 3** a rank (max 15); `move.maxFactor` 1.8 total (2.3) | Monk.b1.r1a + Skills row |
| T7 | Modifier ranks past the modifier's level 5 (`mods.steps` = Lv 2-5): Enrage.Power 5 + 5, ArcaneBreach.Power 5 + 5, ElementalImbue.Power 3 x 3, PalmStrike.Power 5 + 3 + 4, BloodFrenzy.Duration 5 + 3, StillWater.Duration 5 + 3, IronChain.Chain 3 + 3, WarlordsBanner.Power 3 + 3 | up to 12 levels = +60 % main effect (`mods.power` 5) | SkyyClasses clamps one modifier at **5 levels from all sources**; trees_v3_data asserts sum(ranks) per (ability, modifier) <= 5 and the generator moves the extra ranks to the row's other upgrade (UNVERIFIED how 0.1.42 adds ranks to used-based levels - check `AbilModDefs` first) | Classes 0.1.44 + trees_v3_data |
| T8 | Mage Mana: mana 16 % + mreg 10 + barrierMreg 10 -> empty time 23-37 s (section 3.3) | - | keep (tree buys longer casting, inside 1.5x of target) | - |
| T9 | Priest cdAll 12 + mreg 10 + sanctMreg 12 + Bubble / Sanctuary cost -18 / -24 % | - | keep (healer; boss solo still 4.7 min) | - |
| T10 | Berserker echo5 80 % (every 5th hit = +16 % DPS) + cleave 45 + dmgMelee 15 + dmgLowHp 12 | - | keep under DMG_CAP 40; redMist (leech x2 below 30 %) stays under `steal.maxPerSec` 5 | - |

Capstones (xAegis, xRumble, xWarden, xCrimson, xDomain, xFury, xRiftmaw, xFracture, xCascade, xUntouch, xPalms, xNoMind, xGhost, xDeicide,
xLotus, xDeadEye, xSpider, xFirestorm, xCataclysm, xPrism, xGlacial, xMiracle, xVigil, xHolyLand) change how an ability plays and stay; two
need the cap: xDeicide (God Killer +60 % by missing Health on top of mult 2 / backMult 3) and xFracture (Arc +50 % on Sundered) - both count
inside DMG_CAP 40 (the build asserts every damage code goes through UpFx's one cap).

---

## Part 5 - Player damage curve vs gear; the four power sources

- Player DPS(L, kit) = REF 17.0 x Damage rating x F(L) x bonus(L) x (1 + 0.002 L) x class.damage x kit; kit plain 1, expected 1.73, best 3.0
  (Skyy Q14 "About 3x"), the same factor for EHP (Health x Defense).
- **The split (P5 targets, PROPOSED):** best / plain = x3 DPS and x3 EHP = x9 "power" (DPS x EHP). Split in log space 35 / 30 / 20 / 15:
  weapon x2.16 DPS; armor x1.93 EHP; accessories x1.25 DPS + x1.25 EHP; pets x1.18 DPS + x1.18 EHP -> DPS x3.19, EHP x2.85.
  P5 sets rarity / reforge / stat budgets per source to these factors; P4 only fixes the base (F / H / S) they multiply.
- Tree + class level sit UNDER the kit (Part 4 budget: one branch <= +30 % on its focus), so a Lv 50 player with a full branch and plain
  gear is weaker than one with expected gear and no branch.
- Spells: S (1.4) x the metal ladder; the Mana budget (3.3) is what caps caster DPS, so P5 must not add Mana-free spell damage beyond the 35 %.

---

## Part 6 - Files, keys, Server Setup rows, migrations, model check

One FULL round (economy-adjacent, saved config migrations, several mods): build -> review -> fix -> crosscheck -> pin -> deploy, all six
jars TOGETHER (FLOOR comment in tools/deploy_set.py: Gear 0.3.34 + Mobs 0.1.14 + Skills 0.4.58 + Classes 0.1.44 + Armory 0.1.42 + Trees
0.4.4 pin and roll back together; rollback of Gear alone would leave Lv 20+ mobs with new tables vs old F = 2x too hard). P3's Skills
0.4.57 must be pinned first (Skills 0.4.58 derives from it).

### 6.1 Per mod (new patch script each, derived from the SET pin; never edit generated scripts)

| Mod (version, patch) | Changes | Anchors to grep in the current generated script |
|---|---|---|
| SkyyGear 0.3.34 (`tools/gear_0_3_34_patch.py` from build_skyygear_0.3.33.py) | `BASE_CURVE_NEW` + `BASE_HP_DEF` -> 1.4 points; `BASE_SPELL_DEF` -> S_NEW (no longer = BASE_CURVE_DEF; keep the 0.2.5 constant for migrate025); new bridge `gear:fn:weight` (String id -> Integer 1 Heavy / 2 Light / 3 Cloth, `GearView.weightOf`); `smith.classArmor` default + `Spellblade:Light` | lines 3348-3356, `checkCurve("base.spellCurve"` 12026, `weightOf` 22786, `SMITH_ARM_DEF` |
| SkyyMobs 0.1.14 (`tools/mobs_0_1_14_patch.py`) | CURVES -> 1.4 tables (21 points; the 88-line assert -> 168); `strength.floor` 50 -> 70; gap rows 1.6; rank.* rows + Ranks tab; `scale.role` 3rd column (damage x) + defaults; `levels.exclude` default without the boss / elite patterns; rank multipliers in `MobCfg.hpMult` / `LevelDamage` (after the level curve, before the gap; hitCap 35 % still last) and `mob:fn:info` (+ "rank") | `CURVES_011` / `CURVES` (0.1.12 block ~110-141), `FLOOR_DEF`, `LevelDamage`, `MobCfg.hpMult`, `ROLE_DOC` 867, `("scale.role"` 1981 |
| SkyySkills 0.4.58 (`tools/skills_0_4_58_patch.py` from 0.4.57) | class.healthPct / class.defense / class.damage tables; stamina tables (2.2); mana rows (3.2); mana.regen.class; mana.refillPct + refillDelay + the "cast" registry verb; source `skills.classweight` + armor.load.* / armor.slotShare.* rows; `move.maxFactor` | `P25_STA_BASE` 3173, `P25_STA_PER`, `mana.classBase` block (~457), `mana.regen.perLevel` (~603), `CombatDmgSys`, `ManaRegen.total`, `MoveSync` post, CFG_ROWS 20857-20869 |
| SkyyClasses 0.1.44 (`tools/classes_0_1_44_patch.py`) | `abil.costPerLevel` table (cost x (1 + p % x class level) at the Mana check); Spellblade 5 `ab.*.numbers` mana=; `ab.ClassTree.numbers` dmgCap 40 / drCap 35; modifier clamp 5 (T7); `skill:fn:manaregen {"cast"}` after each cast; `_POOL` table refreshed (Mana-Budget finding 5) | `_r("abil.speedCap"` 2440, `UpFx.DMG_CAP` 19250, `ab.ArcaneBreach.numbers` defaults, `AbilModDefs`, the ability Mana check |
| SkyyArmory 0.1.42 (`tools/armory_0_1_42_patch.py`) | `{"cast"}` call on a CHARGED shot (wand, staff, book); `check.share` assert against the new pools (no default change) | `CHECK_SHARE_DEF` 1772, the charged-shot spawn |
| SkyyTrees 0.4.4 (`tools/trees_0_4_4_patch.py` + edits in tools/trees_v3_data.py, the ONE table) | T2 drStill 3, T3 dmgFocus 1, T4 dmgElite 3, T5 momChance 12, T6 move 3, T7 rank moves + assert; texts follow (`{v}` lines) | `CLASS_FX` entries named in Part 4 |

### 6.2 Server Setup rows (tools/skyycfg.py, KEEP=10; seconds for times; Menu-Pattern pages)

| Mod -> page | Row (key) | Type / range | Default |
|---|---|---|---|
| Gear -> Level stats | Weapon curve F (`base.curve`), Armor Health curve H (`base.hpCurve`), Spell curve S (`base.spellCurve`) | text level:factor, factor <= 100 | 1.4 |
| Gear -> Smithing | Class armor types (`smith.classArmor`) | text | + Spellblade:Light |
| Mobs -> Strength | the 8 curve tables (one row each), Health floor (`strength.floor`) | table / int 1-1000 | 1.4 / 70 |
| Mobs -> Level gap | free / dealt step / dealt min / taken step / taken max | int / dec | 3 / 5 / 40 / 3 / 1.5 |
| Mobs -> Ranks (NEW tab) | Elite roles, Elite Health x, Elite damage x, Elite chance %, Elite extra levels, Mini roles, Mini Health x, Mini damage x, Boss base Health, Boss damage x | text / dec 1-100 / int | 1.7 |
| Mobs -> Which mobs | Fixed level by role (`scale.role`, now level / Health x / damage x) | table | 1.7 defaults |
| Skills -> Class Power | Class Health % (`class.healthPct`), Class Defense (`class.defense`), Class damage % (`class.damage`), Class Stamina base / per level (existing tables) | table dec -50..100 / 0..200 / 10..400 | 2.1-2.4 |
| Skills -> Overall and Mana | Max Mana base / per level (existing), Regen growth per level (`mana.regen.perLevel`), Class regen % (`mana.regen.class`), Refill % a second (`mana.refillPct`), Refill wait s (`mana.refillDelay`) | | 3.2 |
| Skills -> Movement (NEW block, Acrobatics page) | Class speed % (`class.speed`), Class weight x (`class.weight`), Armor load per type (`armor.load`), Slot share (`armor.slotShare`), Speed slowed per load point % (`armor.perLoad` 4), Most total speed (`move.maxFactor` 1.8) | | 2.3 |
| Classes -> Abilities | Ability Mana per class level % (`abil.costPerLevel`), Class tree numbers (dmgCap, drCap) | table / text | 3.2, Part 4 |

### 6.3 One-time migrations (PROJECT-RULES 4; clone the reviewed kits: Mobs `MobMig12` / `MobMig.mgKit`, Skills `Mn52Mig`, Gear `migrate025`, Classes `gates041`)

- Only lines still holding the EXACT previous default change (per key; a curve table only when every point is still its 0.1.12 default -
  then the whole table is replaced at its first line, as MobMig12); a hand-edited value is kept + one INFO line names it.
- A verified History copy of each file first; one config-changes.log line per change (Undo in Server Setup -> Changes); bytes + line endings
  kept; a java.util.Properties check that only the planned keys differ; run-once marker (`Balance P4 combat (SkyyMobs 0.1.14)`,
  `... (SkyyGear 0.3.34)`, `... (SkyySkills 0.4.58)`, `... (SkyyClasses 0.1.44)`); a fresh file carries the marker.
- Skyy's live NewBetaTest: difficulty normal, all curve tables default (combat.md 38-124), gap rows default, floor 50, hitCap 35 (a 0.1.11
  migration value - not touched) -> everything migrates; `base.curve` live = BASE_CURVE_NEW (gear.md) -> migrates. Copy the live files to
  `tools/dev/scratch/p4b/` and run each migration there in the harness (LIVE check), as Mn52Mig did.
- Saved player data: none changes (items keep their stamped level; their hits follow the new F automatically; tree ranks unchanged).
- New keys (class.*, rank.*, mana.refill*, abil.costPerLevel, armor.*, move.maxFactor) are appended with comments (absent = default).

### 6.4 Harness checks (each mod's bare-JVM test, -Xverify:all, then all six jars in one JVM)

1. Mob tables = balance_model's RULE at every point (+-0.01); Lv 1-20 Normal Health = today's (exact); `curve_eval` at 1-100 monotonic.
2. F / H / S points: F(L) = H(L) = today's at L <= 20 (exact, rendered tooltip numbers identical for item levels 1-20); every factor <= 100.
3. Model asserts (balance_model `--combat`): same-level trash 4-6 hits (expected kit, M), tough 12-15, hits to die trash 12-15 (M, plain),
   boss 3-4 min (M, expected), +5 in 1.6-2.2x, +10 >= 4x, caster empty 18-30 s at Lv 1-100, fighter rotation 35-80 % from Lv 20.
4. Speed: Warrior heavy slow < 4 %, Mage heavy slow > 15 %; every class's own-armor speed = its rating within 1 %.
5. Class damage: the measured-DPS table (2.4) printed; factors in 60-250.
6. Trees: no (ability, modifier) over 5 ranks; every damage code through `UpFx` cap; dmgCap 40 / drCap 35 defaults.
7. Migrations on fresh / live copy / hand-edited / half-migrated files (marker last).

### 6.5 Model check (DERIVED - the numbers hit the targets)

| Target (source) | Model | OK |
|---|---|---|
| Normal trash 4-6 hits (A:188) | 4.4 expected (7.6 plain, 2.5 best), every level | yes |
| Normal tougher 12-15 hits | 12.6 | yes |
| Trash needs 12-15 hits on you, starter armor (Q6 default) | 12.9 (M), 9.4 Mage, 23 Warrior | yes (M) |
| Easy very fast / Hard Souls-like | 2.6 / 7.0 hits; die in 23.7 / 7.9 | yes |
| Elite 3x / 1.5x, mini 10x / 2x | rank rows | yes |
| Boss 3-4 min solo Normal | 3.5 min M; 2.4-4.7 by class | yes (supports slower) |
| +5 hard, +10 wall | x1.8-1.9 / x4.3-4.8 | yes |
| Casters dry every 20-30 s, refill 5-8 s | 18-29 s; ~7 s to 80 % | yes (edges 18-19 s) |
| Heavy class slowed less by heavy gear | Warrior -3 %, Mage -18 % | yes |
| Best ~3x plain; 35 / 30 / 20 / 15 | DPS x3.19 / EHP x2.85 (P5 builds it) | yes (target) |
| Same-level fights constant Lv 1-100 (today 2-4x off) | flat by construction | yes |

### 6.6 In-game test steps (TEST-CHECKLIST after deploy)

1. Lv 1-20 (Zone 1): fights feel like today (trash a little tougher: floor 70).
2. Zone 2+ (admin `/gear level` a Lv 40 sword + `/mobs` a Lv 40 wolf): about 12 hits, it needs ~6 bites to kill you; a Lv 45 mob is clearly harder, a Lv 50 one a wall.
3. Mage / Priest / Spellblade: cast non-stop -> empty in ~20-30 s; basic attacks -> most of the bar back in ~7 s.
4. Speed: Mage in cloth vs heavy (big slow), Warrior in heavy (barely slower); Assassin / Monk fastest.
5. Elite (an `*_Elite*` or a 3 % roll, "[Lv N] Elite ..."): ~3x as long, hits 1.5x. Trork Chieftain = Lv 18, about 3-4 min solo.
6. Class trees: a full Archer Focus branch no longer doubles bow damage; Warrior capped at 35 % damage cut.
7. Server Setup -> Changes lists every migrated line with Undo.

### 6.7 balance_model.py (the P4 builder adds; P3 is editing it now - add after P3's commit)

A `combat` section ported from tools/dev/scratch/p4/p4model.py (functions F_new, hp_rule, dmg_rule, ttk, hits_to_die, speed, the Mana
`tempty`): prints tables 1.5, 1.3, 2.2, 3.3 and the 6.5 check into research/balance/targets.md ("### 6. Combat"), and `--check` exits 1 when a
target row fails. Class Balance Workbench republished after deploy (standing rule: class / Mana numbers changed).

### 6.8 UNVERIFIED

Swing / draw / cast times per weapon (the hit counts per class), vanilla dodge Stamina cost + regen, whether vanilla armor already changes
move speed (then `armor.perLoad` adds on top), boss spawn places, how SkyyClasses 0.1.42 adds tree ranks to use-based modifier levels,
the engine's MULTIPLICATIVE stat-modifier summing (skyymove notes: multiplicative MAX amounts are SUMMED) - so `class.healthPct` must be
an ADDITIVE modifier of pct x (base + other additives), computed each tick, never a multiplicative one.

---

## Questions for Skyy (each with today's default in [brackets])

1. **Fix the gear-vs-mob mismatch now** (Lv 25+ items hit 20-55 % less, Zone 2+ mobs a little tougher - fights back to "quick", not
   trivial)? [yes - P4 round]
2. **Hard = x1.6 mob Health, x1.8 damage on top of Normal** (Souls-like: ~7 hits a trash mob, ~8 hits to die), Easy = x0.6 / x0.6? [yes]
3. **Spellblade armor type** for crafting + its speed rule: Light (medium speed, +4 % in cloth, -8 % in heavy) or Heavy (frontline,
   0 % in heavy)? [Light]
4. **Trash mobs get at least 70 Health** before levels (today 50) so trash takes ~4-5 hits with normal gear? [yes]
5. **Bosses get fixed levels + one Health pool** (Trork Chieftain Lv 18, Goblin Duke Lv 38, dragons 78 / 98; ~3.5 min solo)? [yes]
6. **Level gap stronger:** free 3 levels, then -5 % your damage / +3 % its damage per level (+5 ~2x as hard, +10 ~4-5x)? [yes]
7. **Casters' Mana:** Mage / Priest a bit more Mana at low levels, LESS regen growth per level (5 % -> 3 %), and a fast refill (most of the
   bar back in ~7 s of basic attacks) after they run dry? [yes]
8. **Fighters' ability costs grow 1.5 % per class level** so a full rotation costs about half their bar (they still never "run dry")? [yes]
9. **Archer bow damage x2** for Archer class hits on monsters (today the slowest killer; rated High damage)? [yes - harness re-measures]
10. **Class tree caps:** all tree damage bonuses on one hit at most +40 % (today 80 %), damage cuts at most 35 % (today 50 %)? [yes]
