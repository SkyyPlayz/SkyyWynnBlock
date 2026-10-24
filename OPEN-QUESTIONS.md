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

### skills  (answers -> docs/answered/skills.md, topic `skills`)

### gear  (answers -> docs/answered/gear.md, topic `gear`)

### economy  (answers -> docs/answered/economy.md, topic `economy`)

### bags  (answers -> docs/answered/bags.md, topic `bags`)

### classes  (answers -> docs/answered/classes.md, topic `classes`)

### pets  (answers -> docs/answered/pets.md, topic `pets`)
- NESTKEEPER: are wild Zone-1 adult dragons too strong? [test in game first]

### social  (answers -> docs/answered/social.md, topic `social`)

### rebirth  (answers -> docs/answered/economy.md, topic `economy`)

### shards  (answers -> docs/answered/skills.md, topic `skills`)

### quests  (answers -> docs/answered/world.md, topic `world`)

### ui  (answers -> docs/answered/ui.md, topic `ui`)

## Pet eggs (research/Pet-Eggs-Spec.md, asked 2026-10-15)  (answers -> docs/answered/pets.md, topic `pets`)
- 2026-10-24 (Fishing 0.2.0): should Lost Property purses in Zones 2 / 3 (x4 / x20 coins) need a minimum rod tier? [no gate] -> answers go to docs/answered/fishing.md (or economy.md).
- 2026-10-24 (Wardrobe 0.2.12): loadout slots 15-18 also open free at Overall Level 30 / 40 (slots.byLevel, LOCKED gear.md 2026-10-08) while coins buy slots 11-18 - keep both? [keep both: level slots stay free, coins buy the rest] -> answers go to docs/answered/gear.md.
- 2026-10-24 (Pets 0.4.17): Pet Fang class XP rises x1.3 (2 -> 2.6 % a rank), not x1.5, because x1.5 breaks the 30 % tree XP cap - OK? [keep x1.3]; max Hatchery hatches ~1.75x the eggs (7 slots, 20 % shorter waits) - OK? [OK] -> docs/answered/pets.md.
