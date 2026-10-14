# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `docs/archive/DESIGN-STATUS.md` "Open questions".

**ONLY OPEN QUESTIONS LIVE HERE (Skyy, 2026-10-05).** When Skyy answers one, the answer goes word for word into
`docs/answered/<topic>.md` (its "New answers" block) and the question is DELETED from this file - one command does both:
`python tools/qa_append.py <topic> <file with the answer lines> --close "<words from the question>"`. Every answer ever given (word for word,
by topic): [docs/answered/README.md](docs/answered/README.md). Format: one `- ` line per question under its topic, today's default in [brackets].

## Still open (newest at the bottom of each topic)

### project

### world

### mobs

### skills
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your live profiles gained nothing (little class XP yet); check the coin rate before a public launch.

### gear
- LOST TOOL (SkyyGear 0.3.2): after you get an exact copy and reforge / tier it up, the original stays Retired for good if it turns up (no swap back, sell or salvage) - else a bad reforge could be undone for free. OK? [yes]
- LOST TOOL: tool in a CLOSED Vault -> /pickaxe gives an exact copy (SkyyVault has no fetch hook yet). OK for now? [yes; add a Vault hook later]
- TOOL PERKS (SkyyTrees 0.3.6): the Tree Feller log table stops at level 6 (1,2,4,5,6,10), so the hatchet perk adds nothing once your tree is level 5+. Give it 8 numbers (e.g. 1,2,4,5,6,10,12,14) as the new default, or will you edit it in Server Setup -> Trees? [8 numbers]
- TOOL PERKS: Vein Mine = +1 ore per tool level on top of the tree's Vein Burst number, total capped at 8. Intended? [yes]







### economy

### bags
- AUTO-PICKUP 2 (SkyySacks 0.8.4): seeds / saplings from a harvest go to the Void (not the inventory), so replanting means pulling them out. Keep? [Void]
- AUTO-PICKUP 2: the vanilla 'picked up' popup still flashes next to our feed card. Keep it? [keep]

### classes
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]





### pets
- DRAGON as a pet with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our own dragons later? [(1) summon via our slot if Aures allows + it works, else (2) - docs/answered/pets.md 2026-10-06; decide after the survey + Aures' answer]


### social

### profiles

### rebirth
- Skill levels above 100 (after rebirths): count them for Overall Level, Overall Mana, the class-weapon bonus and leaderboards? [no - all stop at 100 today]
- Coins for levels above 100 pay once per profile ever. Pay again after each rebirth? [once ever]
- Crops TWO tiers above your hoe / sickle also give half Farming XP (not less). Keep? [yes]
