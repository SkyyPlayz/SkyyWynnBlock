# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `docs/archive/DESIGN-STATUS.md` "Open questions".

**ONLY OPEN QUESTIONS LIVE HERE (Skyy, 2026-10-05).** When Skyy answers one, the answer goes word for word into
`docs/answered/<topic>.md` (its "New answers" block) and the question is DELETED from this file - one command does both:
`python tools/qa_append.py <topic> <file with the answer lines> --close "<words from the question>"`. Every answer ever given (word for word,
by topic): [docs/answered/README.md](docs/answered/README.md). Format: one `- ` line per question under its topic, today's default in [brackets].

## Still open (newest at the bottom of each topic; each heading names the answers file)

### project  (answers -> docs/answered/project.md, topic `project`)

### world  (answers -> docs/answered/world.md, topic `world`)
- STRUCTURES (research/Structure-Mods-Survey.md 2026-10-17 block): send the drafted ask to joszza now? [yes]
- STRUCTURES: switch joszza's StructureV2 on in a test-world copy for a look (its merchant package would duplicate SkyyMerchants)? [yes, copy only]

### skills  (answers -> docs/answered/skills.md, topic `skills`)

### gear  (answers -> docs/answered/gear.md, topic `gear`)

### economy  (answers -> docs/answered/economy.md, topic `economy`)

### bags  (answers -> docs/answered/bags.md, topic `bags`)

### classes  (answers -> docs/answered/classes.md, topic `classes`)

### pets  (answers -> docs/answered/pets.md, topic `pets`)
- NESTKEEPER (research/Nestkeeper-Pack-Check.md): ask Aures to allow recoloured element dragons (only Plain + Tundra exist)? [yes, ask]
- NESTKEEPER: keep its own taming next to our dragon pet? [yes, both]
- NESTKEEPER: are wild Zone-1 adult dragons too strong? [test in game first]
- NESTKEEPER: pack the same author's Rare Monsters + Horse Skins too? [no, Nestkeeper only for now]

### social  (answers -> docs/answered/social.md, topic `social`)

### rebirth  (answers -> docs/answered/economy.md, topic `economy`)

### shards  (answers -> docs/answered/skills.md, topic `skills`)

### quests  (answers -> docs/answered/world.md, topic `world`)

### ui  (answers -> docs/answered/ui.md, topic `ui`)

## Pet eggs (research/Pet-Eggs-Spec.md, asked 2026-10-15)  (answers -> docs/answered/pets.md, topic `pets`)
