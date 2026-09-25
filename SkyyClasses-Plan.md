# SkyyClasses — plan
*Design lock 2026-09-23 night. Does not rebuild the mod. See `SkyWynn-Master-Plan.md` Part 2A, 2E (P4), and Part 3, and `SkyWynn-Decisions.md` rows 1.5, 2.5, 6.1.*

## Roster

Wynn's five stay, plus Priest. **Berserker and Priest are locked (Skyy, 2026-09-25, `SkyWynn-Decisions.md` "Change notes (2026-09-25)") and live in SkyyClasses 0.1.6:** Berserker (weapon skill Fury) owns axes, battleaxes, maces and clubs; Priest (new, weapon skill Divinity) is an AoE healing support class that owns wands and spellbooks. The 2026-09-24 PENDING status is over.

| Class | When | Weapon skill | Weapons already named |
|---|---|---|---|
| Archer | Launch | Archery | Shortbow, Crossbow |
| Warrior | Launch | Swordsmanship | Sword, Longsword, Spear |
| Mage | Launch | Sorcery | Staff |
| Assassin | Later | Assassination | Daggers, Kunai |
| Shaman | Later | Named when that class is designed | — |
| Berserker | **NOW** (locked 2026-09-25) | Fury | Axes, battleaxes, maces, clubs |
| Priest | **NOW** (locked 2026-09-25) | Divinity | Wands, spellbooks. AoE healing support; placeholder party heal on weapon hits until the spell system exists |

The 2026-09-23 "no Berserker" line is reversed. Archetype count and ability-tree size stay open on the decision sheet (6.2–6.4). Rows 9.1–9.2 are the **open magic thread**, not a rune-gating lock. This plan does not pick new numbers for them.

Ability keys are the standing input note from 2026-09-21 (no click-combos). **The magic system is an open thread** (batch 2): wait to see how Hytale Chapter 1 handles runes before deciding how class abilities are built. Do not treat "abilities are engine runes" as locked. Wynn's five elements and powders are gear (`SkyWynn-Decisions.md` 5.7, 5.8), separate from that thread.

## How you pick a class

A **profile** is the class selector. One profile is one class, one island, and a separate everything (skills, bags, coins, collections).

A new class is a **new profile and a new island from zero**. It is not a respec that keeps the current island. The live roster (SkyyClasses 0.1.6, 2026-09-25) is Archer, Warrior, Mage, Berserker and Priest; Assassin and Shaman still come later. The combat-only lock still applies inside the profile.

**Profile cap (2026-09-24):** the default is **6** profiles. The live partner jar, SkyyProfiles 0.1.2, enforces that default (in code since 0.1.1, 2026-09-25; admins can lower it in Server Setup, never above 6). In-game ways to raise it past 6 are wanted; the method is TBD. This plan does not change that jar.

SkyyClasses 0.1.1 charged coins to switch class on the same player. **0.1.2+ set `ALLOW_SWITCH=false`.** The current jar (0.1.6) does not sell a class switch. A new class is a new profile, which is what this plan already said.

## What a class locks

The class locks the **combat path only**. Gathering stays open for everyone, on every class.

- You fight with that class's weapons.
- Combat XP goes into **that class's weapon skill**. There is no shared Combat skill.
- **Class Level** is separate: it spends into the ability tree. It is not the weapon skill.
- Shields, tools, and fists stay usable by everyone (spike default, still in force).
- A fresh profile chooses its class when it is created (SkyyProfiles). The class stays locked: `ALLOW_SWITCH=false` since 0.1.2. The 0.1.1 paid switch is not in the current jar.

## Class kits (locked + live, SkyyClasses 0.1.6)

Every class — launch, Berserker/Priest, and the later Assassin/Shaman — has a kit: its basic weapon, given automatically once per profile the moment the class is picked (a new profile's creation via SkyyProfiles, or SkyyClasses' own picker without SkyyProfiles). Kit contents are editable in Server Setup (Class kits tab) or by hand + `/classadmin reload`. Items go to storage first; anything that does not fit waits as a claim, never dropped on the ground (`/class kit` collects it; `/classadmin kit <player> [class]` for admins). Profiles that already had a class before kits existed are marked so at the first 0.1.6 start and get no surprise kit.

| Class | Default kit |
|---|---|
| Archer | Shortbow (Crude) + 64 arrows |
| Warrior | Sword (Crude) |
| Mage | Staff (Wood) |
| Berserker | Battleaxe (Crude) |
| Priest | Wand (Wood) |
| Assassin (later) | Daggers (Crude), defined now for testing |
| Shaman (later) | empty — gets a custom weapon later |

## Phase

P4 is Archer, Warrior, and Mage: weapon skills, a first ability tree, skill points, and Wynn's five elements on gear. How those abilities are cast is the open magic thread, not a rune implementation. Assassin and Shaman are the next pass on that same track, not a separate endgame pillar. Berserker and Priest joined the live roster 2026-09-25 (SkyyClasses 0.1.6) alongside the P4 launch classes — weapon lock and kit included — but their own ability trees still wait on the same open magic thread as everyone else's. Each of those classes is a new profile.

## Spike vs this doc

`SkyyClasses` 0.1.1 (2026-09-23, not the current jar) included Berserker (Berserking: Axe, Battleaxe, Mace, Club) and a paid class switch, and stored weapon-skill XP as `Combat.<Class>`. **0.1.2+ removed the paid switch (`ALLOW_SWITCH=false`) and removed Berserker.** Current code is 0.1.6.

**2026-09-25 (locked):** Berserker is back, on the same weapon list the 0.1.1 spike used (axes, battleaxes, maces, clubs) — only the skill name changed, from Berserking to **Fury**. Priest is a wholly new class, weapon skill **Divinity** (wands, spellbooks), with a placeholder AoE party heal on weapon hits until the spell system exists (research/Classes-Berserker-Priest-Spec.md). Both are built and deployed together with SkyySkills 0.4.4 and SkyyProfiles 0.1.2 (live since 2026-09-25 07:11). HANDOFF sections 1 and 3 record the same change.

## Status 2026-09-25
Built + deployed (SkyyClasses 0.1.6, live since 2026-09-25 07:11, together with SkyySkills 0.4.4 + SkyyProfiles 0.1.2): Berserker (Fury: axes, battleaxes, maces, clubs) and Priest (Divinity: wands, spellbooks) join the weapon lock and the `/class` page — 5 playable classes now, Assassin and Shaman still greyed "coming later". Every class, launch and new, hands out its kit automatically once per profile (see "Class kits" above). Priest's wand/spellbook hits on a monster heal nearby party members for a share of the damage (placeholder, numbers editable in Server Setup; players can hide the two heal chat lines in `/settings`, the heal itself always happens). Hatchets stay free gathering tools for every class — they match no weapon-lock rule.

## Status 2026-09-24 (superseded above)
Built + verified in game: the class weapon lock (Archer, Warrior, Mage; Assassin + Shaman 'coming later'); the class is chosen when a profile is
created (SkyyProfiles) and locked to that profile (`ALLOW_SWITCH=false` since 0.1.2). 0.1.4 adds a popup with the weapon's icon when a blocked weapon is used. Modded crossbows
(More Crossbow Tiers) count as Archer weapons automatically. The design cap is 6 profiles; this jar's partner at the time, SkyyProfiles 0.1, still capped at 4 (SkyyProfiles 0.1.1 raised the default to 6 on 2026-09-25; see "Profile cap" above).
