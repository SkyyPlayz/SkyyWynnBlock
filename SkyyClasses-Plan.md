# SkyyClasses — plan
*Design lock 2026-09-23 night. Does not rebuild the mod. See `SkyWynn-Master-Plan.md` Part 2A, 2E (P4), and Part 3, and `SkyWynn-Decisions.md` rows 1.5, 2.5, 6.1.*

## Roster

Wynn's five stay. **Berserker is back on the roster as of 2026-09-24, status PENDING.** The owner wants it. Details and timing wait on a talk with the builder. This plan does not design Berserker and does not place it before or after Assassin or Shaman.

| Class | When | Weapon skill | Weapons already named |
|---|---|---|---|
| Archer | Launch | Archery | Shortbow, Crossbow |
| Warrior | Launch | Swordsmanship | Sword, Longsword, Spear |
| Mage | Launch | Sorcery | Staff |
| Assassin | Later | Assassination | Daggers, Kunai |
| Shaman | Later | Named when that class is designed | — |
| Berserker | **PENDING** | Not designed | Not designed. The 0.1.1 axe / battleaxe / mace / club list is not carried forward |

The 2026-09-23 "no Berserker" line is reversed. Archetype count and ability-tree size stay open on the decision sheet (6.2–6.4). Rows 9.1–9.2 are the **open magic thread**, not a rune-gating lock. This plan does not pick new numbers for them.

Ability keys are the standing input note from 2026-09-21 (no click-combos). **The magic system is an open thread** (batch 2): wait to see how Hytale Chapter 1 handles runes before deciding how class abilities are built. Do not treat "abilities are engine runes" as locked. Wynn's five elements and powders are gear (`SkyWynn-Decisions.md` 5.7, 5.8), separate from that thread.

## How you pick a class

A **profile** is the class selector. One profile is one class, one island, and a separate everything (skills, bags, coins, collections).

A new class is a **new profile and a new island from zero**. It is not a respec that keeps the current island. Launch classes are still Archer, Warrior, and Mage; Assassin and Shaman still come later. Berserker is pending, not a launch class and not slotted into that "later" pair. The combat-only lock still applies inside the profile.

**Profile cap (2026-09-24):** the default is **6** profiles. In-game ways to raise it are wanted; the method is TBD. SkyyProfiles 0.1 still caps at 4. This plan does not change that jar.

SkyyClasses 0.1.1 charged coins to switch class on the same player. **0.1.2+ set `ALLOW_SWITCH=false`.** The current jar (0.1.4) does not sell a class switch. A new class is a new profile, which is what this plan already said.

## What a class locks

The class locks the **combat path only**. Gathering stays open for everyone, on every class.

- You fight with that class's weapons.
- Combat XP goes into **that class's weapon skill**. There is no shared Combat skill.
- **Class Level** is separate: it spends into the ability tree. It is not the weapon skill.
- Shields, tools, and fists stay usable by everyone (spike default, still in force).
- A fresh profile chooses its class when it is created (SkyyProfiles). The class stays locked: `ALLOW_SWITCH=false` since 0.1.2. The 0.1.1 paid switch is not in the current jar.

## Phase

P4 is Archer, Warrior, and Mage: weapon skills, a first ability tree, skill points, and Wynn's five elements on gear. How those abilities are cast is the open magic thread, not a rune implementation. Assassin and Shaman are the next pass on that same track, not a separate endgame pillar. Berserker is not in P4 and not in that follow-on until the pending lock is actually locked. Each of those classes is a new profile.

## Spike vs this doc

`SkyyClasses` 0.1.1 (2026-09-23, not the current jar) included Berserker (Berserking: Axe, Battleaxe, Mace, Club) and a paid class switch, and stored weapon-skill XP as `Combat.<Class>`. **0.1.2+ removed the paid switch (`ALLOW_SWITCH=false`) and removed Berserker.** Current code is 0.1.4 and still has no Berserker.

**2026-09-24:** the owner wants Berserker back. Status PENDING. Weapons, skill name, and when it ships relative to Assassin and Shaman are not locked. Adding it is future code work. This doc does not hand the 0.1.1 weapon list to Shaman or to a new Berserker, and it does not rebuild the mod. HANDOFF section 1 records the same split.

## Status 2026-09-24
Built + verified in game: the class weapon lock (Archer, Warrior, Mage; Assassin + Shaman 'coming later'); the class is chosen when a profile is
created (SkyyProfiles) and locked to that profile (`ALLOW_SWITCH=false` since 0.1.2). 0.1.4 adds a popup with the weapon's icon when a blocked weapon is used. Modded crossbows
(More Crossbow Tiers) count as Archer weapons automatically. Berserker is not in this build. The design cap is 6 profiles; this jar's partner, SkyyProfiles 0.1, still caps at 4.
