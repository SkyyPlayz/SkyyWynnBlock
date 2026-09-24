# SkyyClasses — plan
*Design lock 2026-09-23 night. Does not rebuild the mod. See `SkyWynn-Master-Plan.md` Part 2A, 2E (P4), and Part 3, and `SkyWynn-Decisions.md` rows 1.5, 2.5, 6.1.*

## Roster

Wynn's five, and only those five:

| Class | When | Weapon skill | Weapons already named |
|---|---|---|---|
| Archer | Launch | Archery | Shortbow, Crossbow |
| Warrior | Launch | Swordsmanship | Sword, Longsword, Spear |
| Mage | Launch | Sorcery | Staff |
| Assassin | Later | Assassination | Daggers, Kunai |
| Shaman | Later | Named when that class is designed | — |

No Berserker, and no other non-Wynn class name. Archetype count and ability-tree size stay open on the decision sheet (6.2–6.4). Rows 9.1–9.2 are the **open magic thread**, not a rune-gating lock. This plan does not pick new numbers for them.

Ability keys are the standing input note from 2026-09-21 (no click-combos). **The magic system is an open thread** (batch 2): wait to see how Hytale Chapter 1 handles runes before deciding how class abilities are built. Do not treat "abilities are engine runes" as locked. Wynn's five elements and powders are gear (`SkyWynn-Decisions.md` 5.7, 5.8), separate from that thread.

## How you pick a class

A **profile** is the class selector. One profile is one class, one island, and a separate everything (skills, bags, coins, collections).

A new class is a **new profile and a new island from zero**. It is not a respec that keeps the current island. Launch classes are still Archer, Warrior, and Mage; Assassin and Shaman still come later. The combat-only lock still applies inside the profile.

The SkyyClasses 0.1.1 spike charges coins to switch class on the same player. That is the jar. This plan does not.

## What a class locks

The class locks the **combat path only**. Gathering stays open for everyone, on every class.

- You fight with that class's weapons.
- Combat XP goes into **that class's weapon skill**. There is no shared Combat skill.
- **Class Level** is separate: it spends into the ability tree. It is not the weapon skill.
- Shields, tools, and fists stay usable by everyone (spike default, still in force).
- A fresh profile chooses its class when it is created. The 0.1.1 spike still allows a classless player until `/class`; that is the jar.

## Phase

P4 is Archer, Warrior, and Mage: weapon skills, a first ability tree, skill points, and Wynn's five elements on gear. How those abilities are cast is the open magic thread, not a rune implementation. Assassin and Shaman are the next pass on that same track, not a separate endgame pillar. Each of those classes is a new profile.

## Spike vs this doc

`SkyyClasses` 0.1.1 was built earlier on 2026-09-23 with Berserker (Berserking: Axe, Battleaxe, Mace, Club) as a fifth class, and weapon-skill XP stored as `Combat.<Class>`. The jar is unchanged by this doc. Design text uses Shaman instead, and does not hand Berserker's weapons to Shaman. HANDOFF section 1 records the same split.

## Status 2026-09-24
Built + verified in game: the class weapon lock (Archer, Warrior, Mage; Assassin + Shaman 'coming later'); the class is chosen when a profile is
created (SkyyProfiles) and locked to that profile. 0.1.4 adds a popup with the weapon's icon when a blocked weapon is used. Modded crossbows
(More Crossbow Tiers) count as Archer weapons automatically.
