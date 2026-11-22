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
- 2026-10-24 (Fishing 0.2.0): should Lost Property purses in Zones 2 / 3 (x4 / x20 coins) need a minimum rod tier? [no gate] -> answers go to docs/answered/economy.md.
- 2026-10-24 (Wardrobe 0.2.12): loadout slots 15-18 also open free at Overall Level 30 / 40 (slots.byLevel, LOCKED gear.md 2026-10-08) while coins buy slots 11-18 - keep both? [keep both: level slots stay free, coins buy the rest] -> answers go to docs/answered/gear.md.
- 2026-10-24 (Pets 0.4.17): Pet Fang class XP rises x1.3 (2 -> 2.6 % a rank), not x1.5, because x1.5 breaks the 30 % tree XP cap - OK? [keep x1.3]; max Hatchery hatches ~1.75x the eggs (7 slots, 20 % shorter waits) - OK? [OK] -> docs/answered/pets.md.
- 2026-10-24 (Zones 0.3.0): the biggest tree that regrows is 6000 blocks by default (you were told 600 earlier) - OK? [6000] -> docs/answered/world.md.
- 2026-10-24 (Islands 0.5.26): if a skipped starter island later builds on retry, should the spare shard ITEM you got for it (never placed) be taken back? [no - you keep it, it just cannot be placed while the door exists] -> docs/answered/world.md.
- 2026-11-08 (Shards 0.4.21): Combat Shard mobs now match your level on every zone, so a level 80 player on a Zone 1 island gets level 80 coins and XP from real kills (Soul Cage output is unchanged). Keep it? [keep; Server Setup combat.levelWithPlayer off] -> docs/answered/world.md.
- 2026-11-08 (Shards 0.4.21): Soul Cages now make unidentified bags at 2 % per drop, up to 64 per island; that is new gear income, not balance-checked. OK? [yes; combat.bagPct 0 = none] -> docs/answered/world.md.
- 2026-11-08 (Shards 0.4.21): the Soul Cage still never stores armor, weapons, tools, ores, ingots, crystals, rock, Void Essence or Voidheart (they come only from fighting). Keep it? [keep; combat.cageSkip edits the list] -> docs/answered/world.md.
- 2026-11-08 (Sacks 0.8.37): Silver, Gold and Prisma Ingots have no tier, so the Furnace list puts them after the tiered ingots. OK? [keep] -> docs/answered/ui.md.
- 2026-11-20 (Accessories 0.5.37): the Charms panel art shows Merge 3 and Upgrade bag, but Accessories has no merge rule and no per-player bag upgrade (slot count is a server setting). What should they cost? [leave both out until you set costs] -> docs/answered/ui.md.
- 2026-11-21 (Pets 0.4.27): only dragons fight from the pet slot - Wolf, Skeleton, Tusker and the other fighter pets still only follow, because giving them bite damage is new balance. Should they fight too, and how hard? [no - only dragons fight until you set numbers] -> docs/answered/pets.md.
- 2026-11-21 (Shards 0.4.23): while the Foraging clicker is open, should spirits visibly deliver on a 1-2 s timer? The game drops clicks while a page update is waiting, so a timer would eat clicks. [no timer - counts update on every click; spirits still work by the clock] -> docs/answered/world.md.
- 2026-11-21 (Shards 0.4.23): shard zone locks use Foraging level until a real "zone unlocked" signal exists: zone 2 at Foraging 20, then 40 / 60 / 80 (also on the shard Map tab - no T4+ wood island below Foraging 20). OK? [keep; Server Setup -> Shards -> Shard clicker] -> docs/answered/world.md.
- 2026-11-21 (Shards 0.4.23): every clicker tree takes 12 chops at your hatchet's tier (2.5x one tier below, 10x two below, refused three below - like the world). Close enough? [yes; "Chops to fell a tree" in Server Setup] -> docs/answered/world.md.
- 2026-11-21 (Shards 0.4.24): should the quarry's alloy slider also need the Furnace Charm tier like the Furnace tab? [no - Smithy II is the unlock] -> docs/answered/world.md.
- 2026-11-21 (Shards 0.4.24): a zone's ores share the quarry rocks equally (Copper / Iron alternate). OK? [yes] -> docs/answered/world.md.
- 2026-11-21 (Shards 0.4.24): Silver / Gold find weights by zone 10,10,20,10,5 and 8,8,15,3,3 (Silver most in zone 3, as in vanilla). OK? [yes; Server Setup -> Shards -> Shard clicker] -> docs/answered/world.md.
- 2026-11-21 (Shards 0.4.25): the Farming clicker gives the crop + vanilla's 0.5 % Eternal seed bag per plant, no Life Essence, Fortune not on seed bags. OK? [yes; Server Setup -> Shards -> Shard clicker] -> docs/answered/world.md.
- 2026-11-21 (Gear 0.3.58): shield base Defense 6 and shield slot power 19.5 % (like Hands) - right? [keep until tested; Server Setup -> Gear -> Combat] -> docs/answered/gear.md.
- 2026-11-21 (Gear 0.3.58): should The Armory's 85 shield recolours drop from our bags? [not yet - later as one pack set] -> docs/answered/gear.md.
- 2026-11-21 (Shards 0.4.26): Combat town clicks give class XP - that needs SkyySkills to accept class skills from shards; until then the XP waits (owed). Grant it in a later Skills round? [yes] -> docs/answered/world.md.
- 2026-11-22 (Shards 0.4.27): Totem Bench and booster items you already own stay as items (no refund). Convert them later? [no refund for now] -> docs/answered/world.md.
- 2026-11-22 (Shards 0.4.27): "Place one" on the Upgrades view puts a totem item you carry onto the shown island (data only). Keep it, or turn old totem items into a Spirit tier / modifier instead? [keep] -> docs/answered/world.md.
- 2026-11-22 (Shards 0.4.27): Enchanted items for clicker upgrades come from crafting the clicker's own items or the Auto-Compactor. Self-sustaining enough? [yes] -> docs/answered/world.md.
- 2026-11-22 (Shards 0.4.27): Combat town kill coins have no hourly cap (world kills cap at 5,000,000 / h). Add one? [no cap until coins inflate] -> docs/answered/world.md.
- 2026-11-22 (Shards 0.4.27): the old walkable shard world folder (about 28 MB) stays on disk, no longer loaded. Delete it later? [leave it for now] -> docs/answered/world.md.
- 2026-11-21 (Mobs 0.1.26): kill coins pay for ANY kill, even with a fist or a non-class weapon that gives no combat XP. OK? [yes] -> docs/answered/economy.md.
- 2026-11-21 (Mobs 0.1.26): kill coins cap 5,000,000 per player per hour (spawner farms pay full up to it); tamed / baby / island animals pay nothing. OK? [yes; Server Setup > Mobs > Kill coins] -> docs/answered/economy.md.
