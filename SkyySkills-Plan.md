# SkyySkills — plan
*Design lock 2026-09-23 night. See `SkyWynn-Master-Plan.md` Part 2A and Part 3, and `SkyWynn-Decisions.md` section 2.*

## The list

Keep the full SkyBlock-style tree, **plus** extras. Trim later. Do not drop Smithing or Exploration because SkyBlock did not have them.

**Gathering:** Farming, Mining, Foraging, Fishing
**Artisan:** Smithing (ingredient crafting + reforging — headline, keep), Enchanting, Alchemy, Cooking (its own skill for now)
**Life / meta:** Taming, Carpentry, Exploration (keep), Hunting, Runecrafting (cosmetic), Social (cosmetic)
**Combat:** no shared Combat skill. See below.
**Later, not the spine:** Dungeoneering as a skill (`SkyWynn-Decisions.md` 2.14). Dungeons themselves are story beats plus a capstone (`SkyyDungeons-Plan.md`), not a skill you have to grind to level.

**HOTM-style mini-trees** are in, and each one is **tied to its skill**. Mining levels unlock Mining's tree. The same pattern for the other gathering skills. They are not locked to a zone or a mine you have to stand in. Mining can still be the first tree we build (row 2.13).

**Farming** stays a skill. It happens on the private island and on the zone islands. **The Garden is parked** (2026-09-24, `SkyyIslands-Plan.md`): the dedicated farming island is on the back burner, so it is not where farming lives for now.

Level cap 100 for every skill is an existing engineering lock in `HANDOFF.md`. This plan does not retune per-level perks.

## Focus now vs back burner (Skyy, 2026-09-23 late)

| Area | Call | Note |
|---|---|---|
| Archer, Warrior, Mage | **NOW** | Launch classes |
| Assassin, Shaman | LATER | Stay greyed out |
| Berserker | **PENDING** | Owner wants it back (2026-09-24). Details and timing wait on a talk with the builder. Not placed before or after Assassin/Shaman. No weapon skill named here. Not in SkyyClasses 0.1.4 |
| Mining, Foraging, Farming | **NOW** (live) | Each gets its own skill tree |
| Acrobatics | **NOW** (live) | Skyy's mcMMO skill. Fall XP (Skyy 2026-09-23): the further you fall WITHOUT dying the more XP - jumping from heights is a real grind; no XP for water or any fall whose damage is negated (safe no-damage drops pay nothing) |
| Archery, Swordsmanship, Sorcery | **NOW** (live) | Class weapon skills |
| Smithing | **KEEP** | Leveled by reforging and adding powders, **and by smelting in the furnace** (vanilla Furnace + the SkyySacks Furnace tab) |
| Alchemy | **BUILD NOW** | **Table use only**: the Alchemy Bench accessory is removed; the vanilla Alchemy Bench draws ingredients from your sacks |
| Exploration | **BUILD NOW** (SkyyExploration) | Skyy's call 2026-09-24 in SkyyExploration-Plan.md: stamina + coins per level, world chests, chest luck, map coverage, zone discovery, titles, its own tree; server-only parts later |
| Skill tree per gathering skill | **YES** | Mining, Foraging, Farming (Fishing's tree waits with Fishing) |
| Fishing | SHELF | |
| Enchanting | SHELF | Hytale has no enchanting |
| Taming + pets | LATER | |
| Carpentry | SKIP | |
| Hunting | LATER | Major SkyBlock feature, a big project of its own |
| Runecrafting | SHELF | |
| Social | SHELF | |
| Dungeoneering | LATER | Already LATER (2.14) |
| Cooking | **BUILD NOW** (next to Alchemy), **table use only** (Cooking Bench accessory removed; the vanilla bench draws from your sacks) | Food you cook gets stronger AND lasts longer with your Cooking level: x2 at level 50, x4 at level 100; skill-tree modifiers can push it further. Only if the engine allows it (research running) |

## Combat XP

XP from fighting goes into the **weapon skill of the equipped class**:

- Archer → Archery
- Warrior → Swordsmanship
- Mage → Sorcery
- Assassin → Assassination (later)
- Shaman → that class's weapon skill (later; name set with the class)
- Berserker → not named. Status PENDING (2026-09-24). Do not add a weapon skill until the owner locks the class with the builder

Class Level (ability points) is not this skill. The `SkyySkills` 0.3 spike still stores per-class combat XP under `Combat.<Class>`. Those keys stand in for the weapon skills until a code pass renames them. There is still no single Combat skill that every class shares.

Gathering skills do not care which class you are.

## Soft gate with a ceiling

Uneven progression is allowed. You can push one skill ahead of the others.

If you drift too far, that skill slows down until the rest catch up. The exact drift threshold is a tuning knob, not a number locked on the call.

This is not a hard rule that every skill must advance together, and it is not unlimited neglect. Gear can still ask for a skill (a better pick wants Mining). The gate is the slowdown, not a wall that freezes the character.

## Status 2026-09-24
- Built: Mining, Foraging, Farming, Acrobatics (fall XP: bigger survived falls pay more; safe drops and water pay nothing), Archery /
  Swordsmanship / Sorcery, Alchemy, Smithing (smelting only - mining never gives Smithing XP), Cooking (graded dishes, SkyyCooking mod),
  Exploration (SkyyExploration mod, next deploy). The shared Combat row is retired.
- Skill trees (SkyyTrees): Mining, Foraging, Farming, Cooking; next deploy adds Acrobatics (with max Stamina nodes) and a draft Exploration tree.
- Next: felled trees pay per log (research/Tree-Fall-Spec.md), Tree Feller breaks sideways on the same height, a Double Jump node
  (crouch in mid-air, research/Double-Jump-Spec.md), a bigger Stats page.
