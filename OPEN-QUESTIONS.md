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

- FOOD STRENGTH (SkyyCooking 0.1.8): mushroom dishes' Strength buff lasts a flat 6 min at every Grade (not the Grade duration doubling: a G10 kebab would give +17% damage for 24 min) and is capped at +20%? [flat 360 s, cap 20%]
### gear  (answers -> docs/answered/gear.md, topic `gear`)

### economy  (answers -> docs/answered/economy.md, topic `economy`)

### bags  (answers -> docs/answered/bags.md, topic `bags`)

### classes  (answers -> docs/answered/classes.md, topic `classes`)
- ABILITIES: build the 4 waiting nodes next round (Priest Elemental Bubble PB2, Mage PA4 + PC2, Priest PA2; Guiding Light stays out)? [yes, next round] (SkyyTrees 0.3.7)
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]

- CLASS TREE AP (SkyyClasses 0.1.30 / Trees 0.3.18): with modifiers out of the tree a full class tree costs 32 AP, but players reach 50 AP at max level (18 spare). Add nodes / raise costs, or leave the spare AP? [leave it until you've played the new tree]
### pets  (answers -> docs/answered/pets.md, topic `pets`)
- PET KILLS (SkyyPets 0.2.5 / SkyyMobs 0.1.8 / SkyySacks 0.8.4): pet-kill loot + 'pet damage makes you top damager' are built but cannot be tested until pets fight (SkyyPets 0.4). Keep them idle until then? [yes]
- DRAGON as a pet with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our own dragons later? [(1) summon via our slot if Aures allows + it works, else (2) - docs/answered/pets.md 2026-10-06; decide after the survey + Aures' answer]

### social  (answers -> docs/answered/social.md, topic `social`)
- GUILD info takes names with spaces? Needs a fix in SkyyGuilds (and the same left-out-button fix in SkyyShards / SkyyRebirth), not the menu. [yes, small Guilds fix] (SkyyMenu 0.3.23 Admin page)

### rebirth  (answers -> docs/answered/economy.md, topic `economy`)
- BANK BONUS (SkyyRebirth 0.2 / SkyyBank 0.1.11): bonus is worked out on the profile's share of min(account total, 10M), the same cap as the brackets? [yes]
- BANK BONUS: it is flat on the whole capped balance - at the +3 total cap that is about +300k a day on a full 10M bank, ~3.5x the 85k base interest. Keep the Q7 numbers or lower / weight by bracket? [keep the Q7 numbers; refresh the Balance Workbench]
- REBIRTH stays OFF for real players until Skyy has tested R1-R4 (Bazaar / AH open-order check is in 0.3)? [keep OFF until Skyy has seen the Nexus tooltip]
- NEXUS: Rebirth / Continue work from both the Nexus click and the left-panel button? [both] (SkyyRebirth 0.3)
- ADMIN TEST REBIRTH works while the feature is OFF and skips the class / place / combat checks? [yes] (SkyyRebirth 0.2)
- TREE: players cannot respec the tree themselves (admin refund only)? [yes] (SkyyRebirth 0.3)
- TREE: node list right (Wisdom / Dust / Echo / Fortune / tool / stat / keystone titles)? [yes, as built] (SkyyRebirth 0.3)
- TREE: a keystone title replaces 'Void-Touched N' until the next rebirth (newest earned title shows)? [yes] (SkyyRebirth 0.3)
- TREE: +4% points per Echo level (up to +40%), editable? [yes] (SkyyRebirth 0.3)
- TREE: opening row 2 costs 15 points and one maxed skill pays about 8, so the first rebirth cannot open row 2. Keep the spec curve or make early levels cheaper (Tree price growth 1 = every level costs 1)? [keep 1.08] (SkyyRebirth 0.3)

### shards  (answers -> docs/answered/skills.md, topic `skills`)
- CO-OP (SkyyShards 0.1 / 0.2): co-op may enter your shard but only the owner can Collect, buy storage and Grow? [yes; row shard.coopCollect is off]
- A picked-up shard (or one left by an island reset) makes nothing until placed again? [yes]
- Island sizes 13 / 21 / 29 and 6 slots from the spec, not the mockup? [spec]
- Growing costs coins + Eternal Seeds + a collection tier? [yes]
- Allow 20 shard worlds loaded at once? [20]
- Collect goes to the inventory only until SkyySacks has a give bridge, then Magic Bags first? [yes]
- One worker is capped at 12 items / minute before modifiers (the spec's limit; Server Setup -> Shards -> Totems -> Worker cap)? [yes, 12] (SkyyShards 0.2)
- Rebirth collection ranks give no reward (shown and announced only)? [none] (SkyyShards 0.2 / Collections 0.2.14)
- Each rebirth rank past a collection's last tier needs that tier's amount x 2^k (rebirth.rankFactor)? [2]
- An Enchanted crop from Harvest Moon counts as 100 Wheat for XP and collections? [yes] (SkyyShards 0.2)
- Totem tier speeds 1 / 1.25 / 1.5 / 1.75 / 2, and tier-up costs Enchanted Wheat : essence 1:10, 2:25, 3:50, 5:100 (spec's later steps are 2:25 ... 8:200)? [yes; 1:10 ... 5:100]
- MIT fold of MoreTotems (repo returns 404 so the licence cannot be re-checked): keep it with the 'Copyright (c) Nagatwin' notice? [keep] (SkyyShards 0.2)
- Collects made in creative mode count toward collections only at a later Collect in Adventure? [yes]
- One Farming Shard per profile, ever; a lost one comes back only via /shardadmin give; crafting at rebirth 2 only for a profile that never had one? [yes] (SkyyShards 0.2)

### quests  (answers -> docs/answered/world.md, topic `world`)
- DAILY JOBS (SkyyQuests 0.3): daily kill jobs pay an unidentified weapon and armor piece every time (up to 3 of each a day). Keep, or gear on only one job a day (else coins + item)? [gear on every kill job]
- Quest Board look: Kweebec clerk or a board prop? [Kweebec until the prop is proven]
- Markers: floating '!' plus your own signs, or only your own signs? [both; Server Setup switch]
- Daily 'Mine 64 stone' counts only natural blocks (stops place + re-break)? [allow for now]

### ui  (answers -> docs/answered/ui.md, topic `ui`)
- ADMIN PAGE (SkyyMenu 0.3.23, research/Admin-Page-Plan.md): one Admin page in the SkyWynn Menu (right bar, admin only), tabs Server / Economy / Players / Diagnostics? [yes, as built]
- ADMIN PAGE: buttons run the existing commands as you (chat shows output), 5 status buttons also show a one-line result on the page? [yes, option C]
- ADMIN PAGE: dangerous buttons (reset, remove, repay) confirm for 5 s before they run? [yes]
- ADMIN PAGE: restyle to the Sky Window hub look (the kit probes passed 2026-10-15)? [yes]
- ADMIN PAGE: build 'Recent warnings' and 'Economy snapshot' later (each needs a new published value from the mods first)? [yes, later]
- SOUNDS: quiet things (feed cards, XP gains, double drops) stay silent; sounds only on level ups, quest done, rewards and casts? [yes]
- SOUNDS: a custom level-up / rebirth fanfare needs audio we own or CC0 - later, or vanilla-only for release? [vanilla-only for release]
- SOUNDS: ability casts - own vanilla sound per ability where one fits, or one shared cast sound? [own per ability where a vanilla one fits, shared fallback]
- HUBS: Character hub tabs separate (Stats, Skills, Trees, Class, Pets, Collections, Profiles - as built) or merged like your 2026-10-10 pick (Stats+Skills, Trees+Abilities, Collections+Recipes; also Bank+Vault, Bazaar+Auction House)? [separate now, merge later if you pick merged]
- HUBS: scrolling lists OK on Skills (11 of 12 rows show), Class (7 of 8 cards), Profiles (7 cards)? [yes]
- GEAR: benches refuse vanilla Iron / Thorium / Cobalt / Adamantite armor and gathering tiers 2+ (Anvil tier-up only; row gear.gatherAnvilOnly)? [yes, ON]
- SAP TAPPER: should the perk's extra Tree Sap count toward the Tree Sap collection (today only the base sap does)? [yes]

## Pet eggs (research/Pet-Eggs-Spec.md, asked 2026-10-15)  (answers -> docs/answered/pets.md, topic `pets`)
- Where can coins buy eggs? [Bazaar Common-Epic; Legendary only from merchants + Auction House; Mythic only player trade / drops]
- Can pets be fused to Mythic? [no - Mythic only from eggs]
- Add roster pets (e.g. Mosshorn, Bison to Farming) so each egg has a real best-to-worst spread? [yes]
- Give collection eggs for tiers already reached when collection eggs ship? [yes, once]
