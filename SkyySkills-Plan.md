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

**Farming** stays a skill. Some of it happens on the private island and on the zone islands. **Most farming is in the Garden** (`SkyyIslands-Plan.md`).

Level cap 100 for every skill is an existing engineering lock in `HANDOFF.md`. This plan does not retune per-level perks.

## Focus now vs back burner (Skyy, 2026-09-23 late)

| Area | Call | Note |
|---|---|---|
| Archer, Warrior, Mage | **NOW** | Launch classes |
| Assassin, Shaman | LATER | Stay greyed out |
| Mining, Foraging, Farming | **NOW** (live) | Each gets its own skill tree |
| Acrobatics | **NOW** (live) | Skyy's mcMMO skill |
| Archery, Swordsmanship, Sorcery | **NOW** (live) | Class weapon skills |
| Smithing | **KEEP** | Leveled by reforging and adding powders; its XP arrives with those systems |
| Alchemy | **BUILD NOW** | |
| Exploration | **ADD** | Research what SkyBlock and Wynncraft give for exploring first, then Skyy picks the rewards |
| Skill tree per gathering skill | **YES** | Mining, Foraging, Farming (Fishing's tree waits with Fishing) |
| Fishing | SHELF | |
| Enchanting | SHELF | Hytale has no enchanting |
| Taming + pets | LATER | |
| Carpentry | SKIP | |
| Hunting | LATER | Major SkyBlock feature, a big project of its own |
| Runecrafting | SHELF | |
| Social | SHELF | |
| Dungeoneering | LATER | Already LATER (2.14) |
| Cooking | **BUILD NOW** (next to Alchemy) | Food you cook gets stronger AND lasts longer with your Cooking level: x2 at level 50, x4 at level 100; skill-tree modifiers can push it further. Only if the engine allows it (research running) |

## Combat XP

XP from fighting goes into the **weapon skill of the equipped class**:

- Archer → Archery
- Warrior → Swordsmanship
- Mage → Sorcery
- Assassin → Assassination (later)
- Shaman → that class's weapon skill (later; name set with the class)

Class Level (ability points) is not this skill. The `SkyySkills` 0.3 spike still stores per-class combat XP under `Combat.<Class>`. Those keys stand in for the weapon skills until a code pass renames them. There is still no single Combat skill that every class shares.

Gathering skills do not care which class you are.

## Soft gate with a ceiling

Uneven progression is allowed. You can push one skill ahead of the others.

If you drift too far, that skill slows down until the rest catch up. The exact drift threshold is a tuning knob, not a number locked on the call.

This is not a hard rule that every skill must advance together, and it is not unlimited neglect. Gear can still ask for a skill (a better pick wants Mining). The gate is the slowdown, not a wall that freezes the character.
