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
- FIRST-HOUR SPEED: Oak logs + copper ore are one tier above the Crude starter tools, so at 0.1 speed a new player needs ~67 hits per Oak log and ~80 per copper ore (the tutorial asks for 10 logs). Keep 0.1, set Server Setup > Gear > Lifelong tools > gate.crudeFactor to 0.25 (~4x hits, Crude tools only), or make Oak + copper tier 0? [0.1 as answered (G4) - change crudeFactor in game if it feels bad; SkyyGear 0.3.0]
- /pickaxe after losing a tool gives the tier you HAD; lifelong.reclaimTier on = the tier your skill allows (lets players skip Anvil tier-ups). [off]







### economy

### bags
- /pdadmin rarity changes only the profile you are playing - add an all-profiles option? [no; run it once per profile - SkyySacks 0.8.2, 2026-10-13]

### classes
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]





### pets
- DRAGON as a pet with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our own dragons later? [(1) summon via our slot if Aures allows + it works, else (2) - docs/answered/pets.md 2026-10-06; decide after the survey + Aures' answer]


### social

### profiles
- Rename button on the OTHER profile cards too (needs a card redesign; the Switch + Delete column is full)? [no; /profiles rename <number> <name> or switch first - SkyyProfiles 0.1.12, 2026-10-13]

### rebirth
- REBIRTH SPEC: 16 questions in research/cloud/Rebirth-Spec.md section 7 (requirements, Nexus tree, rewards per rebirth, bank rate formula ...). [each has a default there; nothing is built until Skyy answers]
