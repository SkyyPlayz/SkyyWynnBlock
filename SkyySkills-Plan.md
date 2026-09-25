# SkyySkills — plan
*Design lock 2026-09-23 night. See `SkyWynn-Master-Plan.md` Part 2A and Part 3, and `SkyWynn-Decisions.md` section 2.*

## The list

Keep the full SkyBlock-style tree, **plus** extras. Trim later. Do not drop Smithing or Exploration because SkyBlock did not have them.

**Gathering:** Farming, Mining, Foraging, Fishing
**Artisan:** Smithing (ingredient crafting + reforging — headline, keep; Smithing level raises smithing rarity, 2026-09-24), Enchanting, Alchemy, Cooking (its own skill for now)
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
| Berserker | **NOW** (2026-09-25) | Weapon skill **Fury** (axes, battleaxes, maces, clubs) |
| Priest | **NOW** (2026-09-25) | Weapon skill **Divinity** (wands, spellbooks); AoE healing support |
| Mining, Foraging, Farming | **NOW** (live) | Each gets its own skill tree |
| Acrobatics | **NOW** (live) | Skyy's mcMMO skill. Fall XP (Skyy 2026-09-23): the further you fall WITHOUT dying the more XP - jumping from heights is a real grind; no XP for water or any fall whose damage is negated (safe no-damage drops pay nothing) |
| Archery, Swordsmanship, Sorcery | **NOW** (live) | Class weapon skills |
| Smithing | **KEEP** | Leveled by reforging and adding powders, **and by smelting in the furnace** (vanilla Furnace + the SkyySacks Furnace tab). **2026-09-24:** higher Smithing level = higher **smithing rarity**, which raises the chance of crafting a higher-rarity item. Not built |
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
- Berserker → **Fury** (locked 2026-09-25, live in SkyySkills 0.4.4)
- Priest → **Divinity** (locked 2026-09-25, live in SkyySkills 0.4.4; also earns XP from healing, see below)
- Assassin → Assassination (later)
- Shaman → that class's weapon skill (later; name set with the class)

Class Level (ability points) is not this skill. Per-class combat XP is still stored under `Combat.<Class>` keys (`Combat.Berserker` = Fury, `Combat.Priest` = Divinity, appended as slots 14/15 in SkyySkills 0.4.4 — every existing slot and key is untouched). Those keys stand in for the weapon skills until a code pass renames them. There is still no single Combat skill that every class shares.

### Divinity XP from healing (SkyySkills 0.4.4, locked 2026-09-25)

Priest is the one weapon skill that also pays XP outside kills: healing a party member (not yourself) with a Priest weapon hit pays **0.2 Divinity XP per HP healed**, capped at **300 XP a minute** per Priest (both editable in Server Setup). Kills still pay Divinity like every other class skill. The heal itself (SkyyClasses' placeholder AoE party heal) always happens even if this XP is switched off. See `SkyyClasses-Plan.md` and `research/Classes-Berserker-Priest-Spec.md` for the heal mechanic itself — this skill only reacts to it.

Gathering skills do not care which class you are.

## Smithing rarity (locked 2026-09-24)

Smithing stays the headline craft skill. Smelting ore into bars still pays its XP, and mining still does not. Reforging and powders are still the later XP sources.

A higher Smithing level also raises a **smithing rarity** stat. That stat increases the chance that a craft comes out at a higher rarity. It is an effect of the level, not a new way to gain XP. SkyySkills 0.4 does not have the stat. How big the chance is, and which rarities it can reach, are open (`SkyyGear-Plan.md`). A higher item rarity also lets a reforge roll wider and higher; that rule lives on the item, not in this skill's XP table.

## Soft gate with a ceiling

Uneven progression is allowed. You can push one skill ahead of the others.

If you drift too far, that skill slows down until the rest catch up. The exact drift threshold is a tuning knob, not a number locked on the call.

This is not a hard rule that every skill must advance together, and it is not unlimited neglect. Gear can still ask for a skill (a better pick wants Mining). The gate is the slowdown, not a wall that freezes the character.

## Status 2026-09-25
- Built + live (SkyySkills 0.4.4, deployed 2026-09-25 07:11 with SkyyClasses 0.1.6 + SkyyProfiles 0.1.2): two new weapon skills,
  **Fury** (Berserker, slot 14) and **Divinity** (Priest, slot 15), appended after Exploration — every existing skill keeps its slot
  and key, so old saves are untouched. Divinity also earns XP from healing (0.2 XP per HP healed on other party members, capped 300
  XP/minute). Class slots are no longer one contiguous block (5-9, then 14-15), so every place that read `CLASS0 + i` now goes through
  a slot lookup table — the fix that stops a Berserker or Priest from crashing the per-class perk tick. `/skills` and the Stats page
  show Fury / Divinity like any other class skill. **Downgrade rule:** never go back to SkyySkills 0.4.3 once a player has Fury or
  Divinity XP saved (0.4.3's save format drops both keys).

## Status 2026-09-24
- Built: Mining, Foraging, Farming, Acrobatics (fall XP: bigger survived falls pay more; safe drops and water pay nothing), Archery /
  Swordsmanship / Sorcery, Alchemy, Smithing (smelting only - mining never gives Smithing XP; smithing rarity is locked and not built), Cooking (graded dishes, SkyyCooking mod),
  Exploration (SkyyExploration mod, next deploy). The shared Combat row is retired.
- Skill trees (SkyyTrees): Mining, Foraging, Farming, Cooking; next deploy adds Acrobatics (with max Stamina nodes) and a draft Exploration tree.
- Next: felled trees pay per log (research/Tree-Fall-Spec.md), Tree Feller breaks sideways on the same height, a Double Jump node
  (crouch in mid-air, research/Double-Jump-Spec.md), a bigger Stats page.
