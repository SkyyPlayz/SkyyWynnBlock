# SkyWynn - DECISIONS (index of the big locked calls, 2026-10-09)

The big decisions Skyy has locked, one line each.
This is only an index. The exact words live in the source files.

> **Newest wins.** When two lines disagree, the newest line in `docs/answered/` wins.
> Inside each answered file, the "New answers" block at the end beats everything above it.
> Older sources (`docs/handoff/design-locks.md`, `docs/plans/SkyWynn-Decisions.md`) are history.

**To find the exact words:** open the source file and search for the date.
Example: `grep -n "2026-10-07" docs/answered/classes.md`.

Small tuning answers are not listed here - see [docs/answered/](docs/answered/README.md).
Open questions: [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md).

## How we work

| Date | Decision | Source |
|---|---|---|
| 2026-10-08 | A smoke-test server may start on a COPY of the world before a deploy. Never the real game. | [project.md](docs/answered/project.md) |
| 2026-10-08 | Test by playing: moves go into the real weapons, plus one debug command that prints data in chat. | [project.md](docs/answered/project.md) |
| 2026-10-08 | Delete (Recycle Bin) old game logs once they are read. | [project.md](docs/answered/project.md) |
| 2026-10-06 | Pack mods: our code only uses their item ids. Never copy or override their files. | [project.md](docs/answered/project.md) |
| 2026-10-06 | Advanced Farming is not in the pack. Its ideas go into our own tools. | [project.md](docs/answered/project.md) |
| 2026-10-06 | Skyy starts a fresh main session once a day. Sessions never clear themselves. | [project.md](docs/answered/project.md) |
| 2026-10-05 | Always ready to hand off: record work the moment it is done. | [docs/log/2026-10.md](docs/log/2026-10.md) |
| 2026-10-05 | Claude merges its own pull requests once every check passes. | [project.md](docs/answered/project.md) |
| 2026-10-05 | Keep all project files clean and organised. | [project.md](docs/answered/project.md) |
| 2026-10-03 | Public mods on CurseForge. Skyy's Pocket Dimension (Magic Bags) goes first. | [project.md](docs/answered/project.md) |
| 2026-10-02 | Wait for the Hytale 0.7 release. No pre-release test pack. | [project.md](docs/answered/project.md) |
| 2026-09-24 | Auto-deploy a round once it is ready. Never while the game is open. | [versions-history.md](docs/handoff/versions-history.md) |
| 2026-09-24 | Pack goal: solo + private worlds first, server-ready backbones. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-24 | In the end every mod in the pack is our own. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | The repo stays public (free CI). | [docs/log/2026-09.md](docs/log/2026-09.md) |

## UI

| Date | Decision | Source |
|---|---|---|
| 2026-10-08 | No client mods. Ability hotkeys are Ability 2 and 3, plus crouch. SkyyKeyProbe checks which keys arrive. | [ui.md](docs/answered/ui.md) |
| 2026-10-01 | Server Setup shows times in seconds. | [ui.md](docs/answered/ui.md) |
| 2026-09-28 | Every UI must look and feel like native Hytale - part of the game, not a mod. | [HANDOFF.md](HANDOFF.md) section 2, `research/Vanilla-UI-Style-Guide.md` |
| 2026-09-24 | Everything a server owner might change is editable in game. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | No custom UI on the vanilla inventory screen. | [design-locks.md](docs/handoff/design-locks.md) |

## Classes and combat

| Date | Decision | Source |
|---|---|---|
| 2026-10-09 | Ability alts locked for Mage, Berserker, Monk and Priest. | [classes.md](docs/answered/classes.md) |
| 2026-10-08 | New class: Spellblade, a melee mage for groups and boss debuffs. | [classes.md](docs/answered/classes.md) |
| 2026-10-08 | Each class has 4 abilities. 2 are primary (walk, sprint, air). Crouch uses the other 2. | [classes.md](docs/answered/classes.md) |
| 2026-10-08 | Physical classes get more Mana. Mining gives Stamina. Foraging gives Defense. | [skills.md](docs/answered/skills.md) |
| 2026-10-07 | No void protection on any traversal move. | [classes.md](docs/answered/classes.md) |
| 2026-10-07 | Make Monk and Assassin playable. | [classes.md](docs/answered/classes.md) |
| 2026-10-04 | Two class abilities per class, built on runes after Hytale 0.7. | [classes.md](docs/answered/classes.md) |
| 2026-10-03 | Monk replaces Shaman. We build our own classes, not a copy of Wynncraft. | [classes.md](docs/answered/classes.md) |
| 2026-09-25 | Berserker (Fury) and Priest (Divinity) join. Every class gets a starter kit. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | A new class = a new profile and a new island from zero. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | No shared Combat skill: each class levels its own weapon skill. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | Soft skill gate with a ceiling. | [design-locks.md](docs/handoff/design-locks.md) |

## Gear

| Date | Decision | Source |
|---|---|---|
| 2026-10-08 | Own armor sets are dropped. Pack armor is sorted into Cloth / Light / Heavy and dropped by mobs, after Hytale 0.7. | [gear.md](docs/answered/gear.md) |
| 2026-10-08 | Weapon signatures stay. The charge is kept across a weapon swap. Wands ricochet through up to 8 enemies. | [gear.md](docs/answered/gear.md) |
| 2026-10-06 | Weapon speed tiers roll at random - on weapons only, never tools. | [gear.md](docs/answered/gear.md) |
| 2026-10-05 | Armor types: Heavy / Light / Cloth (soft rule). | [gear.md](docs/answered/gear.md) |
| 2026-10-03 | Mob toughness follows a Wynncraft-style curve. | [gear.md](docs/answered/gear.md) |
| 2026-10-02 | Tools get levels, gated by the matching gathering skill. | [gear.md](docs/answered/gear.md) |
| 2026-09-25 | SkyyGear replaces SkyyRolls. Wynn rarities. Mob + chest gear drops unidentified. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-25 | Gear level is capped by the matching skill (class skill for combat gear). | [design-locks.md](docs/handoff/design-locks.md) |

Skyy's own gear design: `SkyyGear-Plan.md` + `SkyyGear-Stat-Catalog.md` (never edited by anyone else).

## Bags, gathering and economy

| Date | Decision | Source |
|---|---|---|
| 2026-10-09 | We build our own roaming merchants: every 20 min, a chat rumour, special weapons and mounts. | [economy.md](docs/answered/economy.md) |
| 2026-10-08 | Mythic, untiered and set items are never bought or sold on the Bazaar or the auction house. | [economy.md](docs/answered/economy.md) |
| 2026-10-06 | Gathering tiers: 5 tree tiers by zone, Enchanted = 100 base items, Mithril waits for 0.7. | [bags.md](docs/answered/bags.md) |
| 2026-10-05 | Gathering is a SkyBlock-style progression ladder. | [bags.md](docs/answered/bags.md) |
| 2026-10-04 | Bazaar prices double per tier step. | [economy.md](docs/answered/economy.md) |
| 2026-10-03 | If it goes in a bag, the Bazaar sells it in the matching tab. | [bags.md](docs/answered/bags.md) |
| 2026-10-03 | Each accessory and bag tier is crafted from the one before. | [bags.md](docs/answered/bags.md) |
| 2026-10-02 | Coins never skip collections or bags (replaces the 2026-09-24 coin bypass). | [economy.md](docs/answered/economy.md) |
| 2026-10-02 | Coins + Bank + Bazaar + Auctions merge into SkyyEconomy after Skyy tests them. | [economy.md](docs/answered/economy.md) |
| 2026-09-23 | Magic Bags (pocket dimension) are core. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | Death costs 10-25% of coins, editable in game. | [design-locks.md](docs/handoff/design-locks.md) |

## World

| Date | Decision | Source |
|---|---|---|
| 2026-10-09 | Each zone is a few islands, far apart (dragon or portal between zones). Caves stay deep, down to lava. | [world.md](docs/answered/world.md) |
| 2026-10-08 | Profile cap matches the class count (8 with Spellblade). Ranks can raise it later. Not built yet. | [social.md](docs/answered/social.md) |
| 2026-10-08 | Zone 1 town: the v2 organic layout around the vanilla spawn temple. | [world.md](docs/answered/world.md) |
| 2026-10-03 | All zone islands sit in one world. | [world.md](docs/answered/world.md) |
| 2026-10-01 | Zone levels: Z1 1-20, Z2 20-30, Z3 30-45, Z4 45-60. | [world.md](docs/answered/world.md) |
| 2026-10-01 | The hub is the Zone 1 starter town. A summit portal opens after each boss. | [world.md](docs/answered/world.md) |
| 2026-09-24 | The Garden farming island is parked. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-24 | Profiles are full saves. Default cap: 6. | [design-locks.md](docs/handoff/design-locks.md) |
| 2026-09-23 | The island chain is the levelling path. Your private island = home + building. | [design-locks.md](docs/handoff/design-locks.md) |

---

*How to add a line: record Skyy's words in `docs/answered/` first (`python tools/qa_append.py`).*
*Then add one short line here only if it is a BIG call. Newest at the top of its table.*
