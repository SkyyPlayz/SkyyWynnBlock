# Answered questions + decisions (by topic)

Every answer Skyy has given, word for word, one per line. Still-open questions are ONLY in [OPEN-QUESTIONS.md](../../OPEN-QUESTIONS.md).
When Skyy answers: `python tools/qa_append.py <topic> <file> --close "<words from the question>"` adds the answer to the topic's
"New answers" block and deletes the question from OPEN-QUESTIONS.md.

Search all topics at once: `grep -n "Soul Orb" docs/answered/*.md` (one line = one whole decision). Newer beats older: the newest
lines are at the bottom of each block, and the "New answers" block at the end of each file beats everything above it.

| Topic file | What is in it |
|---|---|
| [classes.md](classes.md) | classes, abilities, traversals, class weapons, class kits, Priest healing (SkyyClasses, SkyyArmory) - the design per class is in `research/classes/` |
| [gear.md](gear.md) | item levels, rarity, reforge (+ level up), identify, loot, tool levels, tooltips, crit (SkyyGear) |
| [skills.md](skills.md) | skill XP curves, Mana, Cooking, Smithing, Acrobatics, skill trees (SkyySkills, SkyyTrees, SkyyCooking) |
| [mobs.md](mobs.md) | mob levels, difficulty, the mob curve (SkyyMobs) |
| [world.md](world.md) | zone islands, WorldGen, private islands + starter shards, exploration, lore (SkyyWorldGen, SkyyIslands, SkyyExploration) |
| [economy.md](economy.md) | coins, bank, Bazaar prices, auction house, /trade, vault, NPC shops, the SkyyEconomy merge |
| [bags.md](bags.md) | Magic Bags, auto-refill, /craft, accessories, Lantern, collections, Pocket Shards (SkyySacks, SkyyAccessories, SkyyCollections) |
| [ui.md](ui.md) | HUD widgets, SkyWynn Menu, Server Setup, player Settings, vanilla look, minimap, Stats page (SkyyHud, SkyyMenu) |
| [social.md](social.md) | profiles, party, guilds, ranks + permissions (SkyyProfiles, SkyyParty, SkyyGuilds, SkyyRanks) |
| [pets.md](pets.md) | pets, summon slot, dragons (not built yet) |
| [project.md](project.md) | build order, usage pacing, the 0.7 update, public releases, known limits |

A decision that touches several topics is listed in each of them, marked `*(also in: ...)*`. Older design locks (gear rules, the
2026-09-23 design calls, change notes) are in `docs/handoff/design-locks.md` and `docs/plans/SkyWynn-Decisions.md`; Skyy's own gear
design is `SkyyGear-Plan.md` + `SkyyGear-Stat-Catalog.md` (never edited by Claude).
