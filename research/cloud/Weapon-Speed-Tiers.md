# Weapon Speed Tiers (Slow / Medium / Fast / Super Fast)

Cloud draft, 2026-10-06. Paper design; nothing built. Answers Skyy's REQUEST 2026-10-05 (`docs/answered/gear.md` line 54): Wynncraft-style
weapon speed, **same DPS for the same level + modifiers**, per-hit damage scales the other way, the tooltip shows the tier and the per-hit
numbers. Inputs read: `docs/answered/gear.md` (lines 54, 56, 64), `SkyyGear-Plan.md` lock "Attack Speed", `SkyyGear-Stat-Catalog.md` row
"Attack Speed", `research/SkyyGear-Stage1-Spec.md` (stat keys `as`, `def`, `lsteal`, `msteal`), `research/Swing-Speed-Spec.md` (the
cooldown mechanism), `research/SkyyArmory-Spec.md` sections 3.2-3.3, 4.3 and 15, `research/Gear-Levels-Wynn-Spec.md` (F(L)),
`research/Mob-Curve-Spec.md` (hit order), `research/cloud/SkyyArmory-Roadmap.md` sections 4-5, `research/classes/*.md`.
Every number is a placeholder and a Server Setup row (section 8). This touches item data and every weapon -> **full round** (PROJECT-RULES 4).

## 0. Plain words (for Skyy)

- Every weapon type gets a **speed tier**: Slow, Medium, Fast or Super Fast.
- A faster weapon hits more often for less per hit. **Damage per second is the same** at the same level and modifiers.
- Each tier has one **hit weight** `w` (Medium = 1.0). Per-hit damage, Mana per cast and a few per-hit extras are multiplied by `w`.
- The tooltip shows: `Attack Speed: Fast` and the damage **per hit** (already multiplied).
- Recommended answer to the open question: **the weapon type sets the tier; Rare and better items have a small chance to roll one tier
  faster or slower** (the item keeps the same DPS either way, so the roll is a play-style pick, not power).
- **Attack Speed %** (the stat already in the catalog, cap 150%) is different: it makes you swing faster **without** lowering the hit, so it
  **does** raise DPS. The tier is DPS-neutral; the stat is a DPS stat.

## 1. What Wynncraft does (search snippets; the wiki was blocked)

| Wynn tier | Hits per second | Per-hit factor vs Normal (2.05 / hps) |
|---|---|---|
| Super Slow | 0.51 | 4.02 |
| Very Slow | 0.83 | 2.47 |
| Slow | 1.5 | 1.37 |
| Normal | 2.05 | 1.00 |
| Fast | 2.5 | 0.82 |
| Very Fast | 3.1 | 0.66 |
| Super Fast | 4.3 | 0.48 |

- Base DPS = base damage x hits per second; weapon damage numbers are set so tiers come out even ([forum guide](https://forums.wynncraft.com/posts/3263107/)).
- **Spells are normalised:** spell damage multiplies the weapon's base damage by the speed multiplier, so a slow weapon's big number does not
  make spells stronger ([forum guide](https://forums.wynncraft.com/posts/3091816/)). We copy that idea for abilities (section 4, row "Abilities").
- The same hits-per-second numbers are used for Mana Steal and Life Steal in Wynn. We already avoid that problem (our steals are windowed).

## 2. Our four tiers

Skyy asked for four tiers. Hytale facts from `research/Swing-Speed-Spec.md` (VERIFIED for pickaxes only): the default left-click cooldown is
**0.35 s**, and the fastest vanilla swing is **0.25 s**. So the proposal sits Fast on the engine default and Super Fast on the swing floor:

| Tier | Interval (s) | Hits / s | Hit weight w = interval / 0.5 | Wynn equivalent factor |
|---|---|---|---|---|
| Slow | 0.70 | 1.43 | **1.4** | 1.37 (Slow) |
| Medium | 0.50 | 2.00 | **1.0** | 1.00 (Normal) |
| Fast | 0.35 | 2.86 | **0.7** | 0.82 (Fast) |
| Super Fast | 0.25 | 4.00 | **0.5** | 0.48 (Super Fast) |

- **Rule: w is derived, never typed.** `w = interval(tier) / interval(Medium)`. If the local session measures a different real interval for a
  weapon family (melee combos have their own animation timings, UNVERIFIED), the build uses the **measured average time per hit** and the
  weight follows, so DPS stays equal automatically.
- This replaces the Roadmap placeholders (slow x1.6, normal x1.0, fast x0.6), which were not tied to any interval.
- A combo weapon (sword 3-hit chain, fists) uses the **whole cycle time / hits in the cycle**. Uneven combo hits keep their vanilla ratios.

## 3. Default tier per weapon type (19 types)

| Class | Weapon | Tier | w | Why |
|---|---|---|---|---|
| Priest | Wand | Medium | 1.0 | baseline caster; Skyy's own example |
| Priest | Soul Orb | Medium, **fixed** | 1.0 | a channel (steady drain per second); tick numbers, never rolls |
| Mage | Staff | Slow | 1.4 | big orb, Roadmap "slow" |
| Mage | Spellbook | Medium | 1.0 | Mage keeps one non-slow option |
| Archer | Shortbow | Fast | 0.7 | quick draws |
| Archer | Crossbow | Slow | 1.4 | reload weight |
| Warrior | Sword | Medium | 1.0 | baseline melee |
| Warrior | Longsword | Slow | 1.4 | two-hander |
| Warrior | Spear | Medium | 1.0 | reach is its perk |
| Berserker | Axe | Medium | 1.0 | |
| Berserker | Battleaxe | Slow | 1.4 | |
| Berserker | Mace | Slow | 1.4 | |
| Berserker | Club | Slow | 1.4 | crude, stays crude |
| Monk | Bo staff | Fast | 0.7 | staff combo |
| Monk | Hand wraps | Super Fast | 0.5 | "fast punch combo" |
| Monk | Gauntlets | Fast | 0.7 | metal weight |
| Monk | Claws | Super Fast | 0.5 | |
| Assassin | Dagger | Super Fast | 0.5 | vanilla fast stabs |
| Assassin | Kunai | Fast | 0.7 | thrown, one at a time |

Every class except Priest has two different tiers between its two weapons. Each row is a Server Setup row (`speed.type.<weapon>`).

**Open question - per type, rolled, or both? Recommended: both, type first.** The type sets the tier. At craft / drop, items of **Rare or
better** have a **5%** chance to roll **one tier faster or slower** (50/50, never past Slow or Super Fast; Soul Orb never). Shown as
`Attack Speed: Fast (rolled; Medium normally)`. Because DPS is equal, this adds variety and trading interest without power creep. A
"slower" roll is only possible where the engine allows it (longer cooldown = easy); a "faster" roll only where the swing has headroom
under the cooldown (UNVERIFIED per family; otherwise that roll is turned off for that type).

## 4. How every stat meets the hit weight

The question for each row: does it pay **per hit** with a fixed amount (bad - fast weapons win or lose) or **in proportion** to the hit
(fine - neutral)?

| Stat / system | Today's shape | Effect of speed | Proposal |
|---|---|---|---|
| Weapon base damage + F(L) level damage + material bonus | multiplier (`kOf x F(L) x bonus`) | neutral once x w | **w applied here**, before everything else |
| Strength (melee, % per point) / Magical Power (spells, % per point) / Damage % | multipliers | neutral | none |
| Crit Chance / Crit Damage | per-hit roll, % | neutral on average; Slow is burstier | none |
| Element damage % | multiplier | neutral | none |
| Flat element lines + True Damage (`GearTrueSys`, added after armor, per hit) | **flat per hit** | **favours fast** (Super Fast gets 2x the flat of Medium per second) | multiply the flat by **w** (the "hit weight" SkyyArmory section 3.2 R8 already asks for quick orbs) |
| Life Steal | % of landed damage summed per 3 s window | neutral | none |
| Mana Steal | flat Mana per 3 s window, any hit | neutral (every tier hits within 3 s) | none |
| Mana per cast (wand, staff, spellbook) | flat cost per shot | must keep **damage per Mana** equal | **cost x w** (section 5) |
| On-hit procs that scale with the hit (Exploding, Ferocity extra hit, Poison as % of hit) | chance per hit, damage = % of hit | neutral | none |
| On-hit effects with a fixed result (Slow / Weaken Enemy, a fixed-damage Poison, Monk "Awed" debuff stacks) | chance per hit | **favours fast** | chance x **w** (capped at 100%; overflow lost) |
| Combo counters (Monk Flowing Form "15 combo") | +1 per hit | favours fast | add **w** per hit instead of 1 (so 15 combo = same time on any tier) |
| Knockback | push per hit | Super Fast = stun-lock, Slow = barely pushes | push x **w** (Slow 1.4x, Super Fast 0.5x); the Knockback stat % on top |
| Defense on the victim, `x 100 / (100 + Def)` | **multiplier** | **neutral** (checked: 100/(100+Def) scales a big and a small hit the same) | none |
| Hytale engine armour resistance (before SkyyGear) | UNVERIFIED: % or flat? | if it has a **flat** part, **favours slow** | local check; any flat reduction x **w** |
| Per-hit caps (Priest heal cap per hit, SkyyMobs hit cap, a future boss damage cap) | cap per hit | caps hit Slow weapons first | cap x **w** |
| Abilities that deal "one weapon hit" (Warrior shield slam, Monk shockwave / counter, bo vault kick 2x) | one weapon hit | Slow weapons make abilities 2.8x stronger than Super Fast | use the **DPS-normalised hit** = hit / w (Wynn's spell rule) |
| Charged attacks / traversals | set by charge time, not the tier | - | not weighted (w = 1); they keep their own numbers |
| Durability (OFF by default) | 1 per hit | fast wears 2.8x faster | loss x **w** when the switch is on |

**Defense check, as asked.** The brief said "Defense is per hit so flat-per-hit things favour slow weapons". Our Defense is a **multiplier**,
so on its own it is neutral. What is not neutral is anything **flat**: a flat reduction per hit hurts fast weapons (favours slow), a flat
addition per hit helps fast weapons. The fix is one rule: **every flat per-hit number is multiplied by w.** Example (section 6): a flat
armor of 3 per hit costs the Super Fast wand 12.0 DPS but the Slow wand only 4.3 DPS; with `3 x w` every tier loses exactly 6.0 and ends
at 53.8 DPS.

## 5. Casters: damage per Mana stays equal

- Rule: **cost = base cost x w**, **damage = base damage x w**. Damage per Mana and Mana per second are then the same on every tier.
- Costs are whole numbers today (wand ladder 5/1, 10/2 ... 85/17). Proposal: keep costs in **tenths** (Copper quick at Fast = 1.4 Mana).
  If SkyySkills' cost path only takes whole Mana (UNVERIFIED), round the cost and **derive the damage from the rounded cost**
  (`damage = damage per Mana x cost`), so damage per Mana is still exact and only the hit size moves a little.
- The charged shot (hold) keeps its charge time; only its cost and damage take `w`, so a Slow staff's charged orb costs 1.4x and hits 1.4x.
- Soul Orb: fixed Medium; its drain per second and damage per second are already a rate.
- The staff rule (2 x wand cost, damage multiple `1.25 x (C / 10) - 0.25`) and the wand rule are untouched: `w` sits on top of them.

## 6. Worked example: two identical Lv 10 Copper wands, quick shot (tap)

Base quick shot 11 (SkyyArmory 4.3) x F(10) 2.0 x Copper bonus 1.03 = **22.7** per hit at Medium; cost 2 Mana. Both wands also carry
+20 Magical Power, 20% Crit Chance, +50% Crit Damage, and a flat +5 Fire line. Columns "unfixed" = today's code; "fixed" = this spec.

| Tier | Hits/s | Per hit | Mana / cast | DPS (base) | Mana / s | Dmg per Mana | Avg hit with MP + crits | DPS with MP + crits | + flat 5 Fire, unfixed | + flat 5 Fire x w | Flat armor 3, unfixed | Flat armor 3 x w |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Slow | 1.43 | 31.7 | 2.8 | 45.3 | 4.0 | 11.33 | 41.9 | 59.8 | 67.0 | **69.8** | 55.5 | **53.8** |
| Medium | 2.00 | 22.7 | 2.0 | 45.3 | 4.0 | 11.33 | 29.9 | 59.8 | 69.8 | **69.8** | 53.8 | **53.8** |
| Fast | 2.86 | 15.9 | 1.4 | 45.3 | 4.0 | 11.33 | 20.9 | 59.8 | 74.1 | **69.8** | 51.3 | **53.8** |
| Super Fast | 4.00 | 11.3 | 1.0 | 45.3 | 4.0 | 11.33 | 15.0 | 59.8 | 79.8 | **69.8** | 47.8 | **53.8** |

(Python-checked. "Flat armor 3" is a what-if: our Defense is a multiplier and needs no fix. Avg hit = hit x 1.2 MP x (1 + 0.2 x 0.5).)
Without the flat fix the Super Fast wand would do **+14%** DPS against everything; with it, both wands match, as Skyy asked.

## 7. Attack Speed (the stat) vs the tier

- `SkyyGear-Plan.md` / the catalog keep **Attack Speed**: "the weapon has a built-in swing speed, Wynn-style. +Attack Speed % can roll on
  weapons, armor, Equipment, and accessories. Cap 150%." The **built-in swing speed is this spec's tier**.
- SkyyGear marks the stat key `as` **"later"** (`research/SkyyGear-Stage1-Spec.md` line 511, `Stats-Page-Spec.md`): it needs the per-family root
  override mechanism from `research/Swing-Speed-Spec.md`. The tier needs **the same mechanism** - so both go live together, and the tier is the
  first user of it.
- How they stack: real interval = tier interval / (1 + Attack Speed %); **w stays the tier's w** (from the base interval). So Attack Speed
  raises hits per second without lowering the hit = more DPS (as intended for Light armor's class bonus, Monk Flowing Form, the Fast /
  Blitz reforges, enrichments).
- Engine reality: the pickaxe tops out at +40% (0.35 -> 0.25 s) without re-timed animations. A Super Fast weapon is already at the 0.25 s
  floor, so **Attack Speed % may do nothing on it** (UNVERIFIED for weapons). Options: (a) Attack Speed on a weapon at the floor turns into
  the same % of damage (keeps the stat useful); (b) accept it. Recommended (a), Server Setup switch.
- The 150% cap is far above what the engine can show today; keep it as the cap, but the tooltip shows the **real** (clamped) speed.
- Until the mechanism works, **do not show the tier or Attack Speed** (Roadmap rule: never advertise a stat that does nothing). Phase 1 could
  still ship the **weights and tooltip** only for types whose vanilla interval already matches their tier (measure first).

## 8. Server Setup rows (Gear -> Weapon Speed; times in seconds)

| Row | Default | Meaning |
|---|---|---|
| `speed.enabled` | off | whole system; off until the swing mechanism is tested |
| `speed.interval.slow` / `.medium` / `.fast` / `.superfast` | 0.70 / 0.50 / 0.35 / 0.25 | seconds per hit; `w` is derived |
| `speed.type.<weapon>` (19 rows) | section 3 | default tier per weapon type |
| `speed.roll.chance` | 5 | % chance of a +/-1 tier roll |
| `speed.roll.minRarity` | Rare | lowest rarity that can roll |
| `speed.flatScale` | on | flat per-hit adds/reductions x w |
| `speed.procScale` | on | fixed-result proc chance x w; combo +w |
| `speed.kbScale` | on | knockback x w |
| `speed.manaScale` | on | casters: Mana cost x w |
| `speed.abilityNormalise` | on | "one weapon hit" abilities use hit / w |
| `speed.floorToDamage` | on | Attack Speed past the swing floor becomes damage % |
| `speed.manaTenths` | on | costs in tenths (off = round, damage from rounded cost) |

## 9. Saved data and rounds

- The **type default needs no saved data** (read from the item id). A **rolled tier is saved on the stack** (SkyyGear per-stack data,
  one small key); old items without the key use the type default - no migration.
- Full round (items, coins-adjacent power, several mods: SkyyGear, SkyyArmory, SkyyClasses abilities, SkyySkills costs).

## For the local session (UNVERIFIED)

1. The real time per hit of every vanilla weapon family (sword / longsword / spear / axe / battleaxe / mace / club / dagger combos, bow
   draw, crossbow reload, wand / staff / spellbook taps) - read the interaction chains in `Assets.zip` like `research/Swing-Speed-Spec.md` section 1.
2. Whether the `EffectCondition` + `TriggerCooldown` root override (Swing-Speed-Spec) works for weapon roots and combo chains, both
   slower (longer cooldown) and faster (where the chain has headroom).
3. Whether Hytale's armour resistance on mobs/players has any flat part (if yes: x w).
4. Whether SkyySkills / SkyyArmory Mana costs can be fractional (`EntityStatMap` is float; the cost path may round).
5. Base knockback per weapon family and where SkyyGear could scale it.
6. Whether vanilla gives weapons per-hit damage that already differs by speed (dagger vs battleaxe); `kOf` may already include part of `w`
   - then `w` must be applied relative to vanilla, not on top (no double scaling, like SkyyArmory section 3.2).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | How is speed set: by weapon type, rolled, or both? | [both: type default; Rare+ items 5% chance of +/-1 tier] |
| 2 | Are the default tiers in section 3 right (e.g. Staff Slow, Spellbook Medium, Dagger Super Fast, Crossbow Slow)? | [as in section 3] |
| 3 | Super Fast: 4 hits/s (our engine floor) or Wynn's 4.3? | [4.0 - the 0.25 s swing floor] |
| 4 | Should flat per-hit extras (flat element lines, True Damage) shrink on fast weapons so DPS stays equal? | [yes, x w] |
| 5 | Knockback scales with hit size (Slow pushes far, Super Fast barely)? | [yes] |
| 6 | Abilities that deal "one weapon hit" use the speed-neutral hit, so a slow weapon does not buff abilities? | [yes, Wynn's rule] |
| 7 | Attack Speed % on a weapon already at the fastest swing turns into bonus damage? | [yes] |
| 8 | Ship the tooltip + weights before the swing-speed mechanism works, or wait? | [wait; nothing is shown until it works] |
