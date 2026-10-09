# SkyWynn - CHANGELOG (big steps, newest first)

A short, release-level summary: a few lines per day of big changes.

> **The full record is `docs/log/`** (one line per build, deploy, test and decision).
> Every version's notes: `docs/handoff/versions-history.md`.
> Live versions now: [HANDOFF.md](HANDOFF.md) section 1.

All mods ship together as one set. "Deployed" = in Skyy's test world, not public yet.
Skyy's test results: [TEST-CHECKLIST.md](TEST-CHECKLIST.md).

## 2026-10-09

- **Luggage + search:** SkyyExploration 0.2.5 (claimed luggage vanishes at once) + SkyyBazaar 0.1.6 (search across every tab) + SkyyKeyProbe 0.2.
- **Stats:** SkyyMenu 0.3.12 - the Defense row counts skill Defense.
- **Pack:** Better Mob Expansion switched on for a test (`PACK.md`). The Armory pack mod switched back off.

## 2026-10-08

- **Class Mana:** SkyySkills 0.4.25 - each class has its own Mana pool, Mana on hit, mining gives more Stamina, foraging gives Defense.
- **Loot:** SkyyGear 0.2.11 + SkyyMobs 0.1.5 + SkyyExploration 0.2.4 - mystery bags, mob bag drops, Unclaimed Luggage.
- **Fishing:** SkyyFishing 0.1 - Fishing Bench, rods and reels, Zone 1 fish. SkyyReelProbe retired.
- **Signatures:** SkyyGear 0.2.10 keeps a weapon's charge when you swap away and back. SkyyArmory 0.1.14 - a wand shot ricochets through up to 8 enemies (wood wands via SkyySkills 0.4.24).
- **Roll:** SkyySkills 0.4.23 - the roll fires when sprint turns on. No back roll (the client sends no sprint backwards).
- **Monk moves:** SkyyArmory 0.1.12 + SkyySkills 0.4.22 - Pole-Vault, Skipping Bounds, Rising Strike, Plunge Punch. Wood and Bamboo Bo handed over (no orb). SkyyMonkProbe retired.
- **Profiles + Stats:** SkyyProfiles 0.1.7 (a second click confirms the switch; Health is saved per profile) + SkyyMenu 0.3.10 Stats page.
- **Probes:** SkyyTownProbe 0.1 (Zone 1 town) + SkyyKeyProbe 0.1 (ability keys).
- **Pack:** The Armory switched on (`PACK.md`).
- **Monk prep:** SkyyArmory 0.1.11 - the 7 metal Bo staffs lose the charged magic orb. Wood and Bamboo Bo stayed on SkyySkills until 0.4.22 the same day.
- **Bag art:** SkyySacks 0.7.14 + SkyyAccessories 0.5.8 - new bag models, type emblems, open swirl, sparkles.
- **Hotfix:** SkyyArmory 0.1.10 - the world would not start (spellbook Levitate). Fixed and tested.
- **Class path trees:** SkyyTrees 0.3.3 + SkyyArmory 0.1.9 - all 7 classes get paths.
- **Monk probes:** SkyyMonkProbe 0.1 - tests for the Monk moves (remove after testing).

## 2026-10-07

- **New classes:** Monk and Assassin are playable (SkyyClasses 0.1.14, SkyySkills 0.4.21, SkyyProfiles 0.1.6, SkyyMenu 0.3.9).
- **New weapons (SkyyArmory 0.1.5 - 0.1.8):** staffs, spellbooks, kunai, Monk bo + fist weapons, dagger Shadow Step.
- **Own icons:** SkyyAccessories 0.5.7 - 44 booster icons.
- **Probe:** SkyyReelProbe 0.1 - fishing rod + reel look.
- **Rule:** no void protection on any traversal move.

## 2026-10-06

- **Mob curve:** SkyyMobs 0.1.4 + SkyyGear 0.2.5 + SkyySkills 0.4.17 - Wynncraft-style mob and gear level curves.
- **Traversal moves:** SkyyArmory 0.1.1 - 0.1.4 - staff blink, wand hop, crossbow Grapple Bolt, bow leap.
- **Dodge roll:** SkyySkills 0.4.18 - 0.4.20 - 8-way roll on a sprint-key tap.
- **Minimap:** SkyyHud 0.3.14 - 0.3.16 (uses BetterMap) + Dynamic Seasons widget mover.
- **Gear:** SkyyGear 0.2.4 - 0.2.7 - traversal tooltips, weapon speed tiers, Charged crossbows.
- **Bags + Bazaar:** SkyyBazaar 0.1.5 + SkyySacks 0.7.13 - sell straight from your bags.
- **Lanterns:** SkyyCollections 0.2.7 + SkyyAccessories 0.5.6 - Lantern recipes unlock from Tree Sap.
- **Bank:** SkyyBank 0.1.7 - interest once a day.
- **Pack:** HyFishing, Dynamic Seasons and NoCube's Orchard added (`PACK.md`).

## 2026-10-05

- **Docs tidy-up:** small core files, `docs/answered/`, `docs/log/`, easy-read class pages, Obsidian vault (PR #6).
- **Class trees ON:** SkyyTrees 0.3.2 + SkyyMenu 0.3.8.
- **XP + prices:** SkyyCooking 0.1.5 / 0.1.6, SkyySkills 0.4.16 (own Mining XP list), SkyyBazaar 0.1.4 (99 new prices).
- **Smithing XP fix:** SkyyGear 0.2.3 - crafted weapons + armor give Smithing XP.
- **Party:** SkyyParty 0.1.7 + SkyyEssentials 0.1.8 - TPA buttons on the Party page.

## 2026-10-04

- **Lantern:** SkyyAccessories 0.5.4 - glow accessory replaces Night Vision.

## 2026-10-03

- **New mod - SkyyArmory 0.1:** our own wands + staff ladder (with SkyySkills 0.4.15 + SkyyClasses 0.1.11).
- **New mod - SkyyWorldGen 0.1:** Zone 1 test island.
- **Gear levels stages 2-3:** SkyyGear 0.2.1 / 0.2.2 - damage and armor grow with item level.
- **New trees:** SkyyTrees 0.3 / 0.3.1 - Alchemy + Smithing trees; class trees built (off).
- **Fixes:** SkyyBank 0.1.6 + SkyyMenu 0.3.6 - the stuck-page bug.
- **Also:** SkyyBazaar 0.1.3 (Smithing tab), SkyyHud 0.3.12 / 0.3.13 (combat widget), SkyyCooking 0.1.4, SkyyMobs 0.1.3.

## 2026-10-02

- **New mod - SkyyMobs 0.1:** mob levels by zone + difficulty.
- **Gear levels stage 1:** SkyyGear 0.2 - every item has its own level.
- **Bags in crafting:** SkyySacks 0.7.11 / 0.7.12 - benches and pocket crafting use your bags; stack refill.
- **Rule:** coins never skip collections or bags (SkyyCollections 0.2.5).
- **Also:** SkyySkills 0.4.12 (class skill curve), SkyyHud 0.3.11 (skills widget), SkyyAccessories 0.5.3.

## 2026-10-01

- **Profiles:** SkyyProfiles 0.1.5 - delete a profile with a 6-hour undo.
- **Islands + guilds:** SkyyIslands 0.5.5, SkyyGuilds 0.1.5 / 0.1.6 - safe island close, fair guild refunds.
- **Workbench tab:** SkyyAccessories 0.5.2 + SkyySacks 0.7.10 - "Accessories & Bags" tab.
- **Also:** SkyyGear 0.1.3 (chest gear unidentified), SkyySkills 0.4.11, SkyyClasses 0.1.10, SkyyMenu 0.3.4.

## 2026-09-30

- **Vanilla UI wave:** 12 pages restyled to the Hytale look (shared kit `tools/skyyui.py`).
- **Booster accessories:** SkyyAccessories 0.5.
- **Also:** SkyySkills 0.4.9 / 0.4.10, SkyyEssentials 0.1.6 (durability switch).

## 2026-09-29

- **New mod - SkyyGear 0.1:** rarities, levels, identify, reforge. SkyyRolls is retired.
- **Round 9:** SkyyClasses 0.1.7, SkyyTrees 0.2.4, SkyyVault 0.1.3, SkyyIslands 0.5.3 and more.

## 2026-09-28

- **Round 8:** SkyyParty 0.1.5, SkyyEssentials 0.1.5, SkyySkills 0.4.6, SkyySacks 0.7.7, SkyyCollections 0.2.3.
- **Rule:** every UI must look and feel vanilla.

## 2026-09-25

- **New mod - SkyyAuctions 0.1:** auction house.
- **Rounds 2-7:** /trade, Exploration spots, Server Setup pages in 16 mods, Berserker + Priest kits.
- **Decision:** start building SkyyGear (Wynn rarities, replaces SkyyRolls).

## 2026-09-24

- **Beta set:** 17, then 19 mods deployed. Beta round 1.
- **Rule:** auto-deploy when a round is ready.

## 2026-09-22 - 09-23

- **Start:** build toolchain (javassist via jpype), HUD fix (no `.ui` files), Magic Bags design.
- **First full set:** 14 mods deployed together. GitHub repo created; CI lint added.

---

*How to add an entry: one dated block per big day, newest at the top, a few short lines.*
*Write the detail in `docs/log/` first - this file only sums it up.*
