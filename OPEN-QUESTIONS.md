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
- RELEASE: start with a GitHub 'server pack' zip, CurseForge modpack later? [yes] (research/Release-Packaging-Plan.md)
- RELEASE: OK to redistribute our jars although 4 of them (Skills / Armory / Gear / Trees) hold edited vanilla JSONs / assets generated from game files at build time - check Hytale's modding terms first? [check the terms first, then release] (research/Release-Packaging-Plan.md)
- RELEASE: Dynamic Seasons + More Crossbow Tiers have no stated pack permission - ask the authors now, list them optional until they reply? [yes, ask now, optional until a reply] (research/Release-Packaging-Plan.md)
- RELEASE: pack version number and name? [0.9.0 'SkyWynn'] (research/Release-Packaging-Plan.md)
- RELEASE: which tuning scripts ship with the pack (Perfect Parries per class)? [a small apply script, off by default] (research/Release-Packaging-Plan.md)
- LOAD TEST: OK to refactor tools/smoke_test.py into reusable functions (no behaviour change) so the load tool shares its safety checks? [yes, small lean round] (research/Load-Test-Plan.md)
- LOAD TEST: spend a day on the bot-client spike (phase 3), or rely on layers A-C plus a real friends test? [layers A-C first, spike only if they miss something] (research/Load-Test-Plan.md)
- LOAD TEST: how many players should the public server handle at release (sets N)? [50 online, 200 profiles on disk] (research/Load-Test-Plan.md)
- LOAD TEST: make 'no com.skyy task took over 25 ms' a release gate in the smoke test? [yes, warn only until the Core ticker lands] (research/Load-Test-Plan.md)

### world
- EXPLORATION: names Lost Loot / Lost Treasure / Supply Drop OK? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: tier IV Lost Loot is a gold treasure pile? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: one supply drop per world every 30 min, one at a time, first claim takes all? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: reveal page (face-down cards) on by default for everyone? [yes; per-player setting 'Loot reveal page'] (SkyyExploration 0.2.8)
- EXPLORATION: the supply drop is a firework flash falling, then the crate appears (no falling crate model) - OK? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: drops land 32-64 blocks from the chosen player (was 32-96) so the flash can be seen? [yes] (SkyyExploration 0.2.8)
- STRUCTURES: OK to message joszza (OpenStructure + Dungeons and more Structures: modpack use, merchant camp off switch)? [yes; you send it or Claude drafts the text] (research/Structure-Mods-Survey.md)
- STRUCTURES: more world structures at all before release, or keep zones vanilla + our loot piles? [keep vanilla, loot piles first] (research/Structure-Mods-Survey.md)
- STRUCTURES: boss dungeons from Adathan (Tower of Shiva, Void Asylum) as end-game: one ask message for all four? [no, our own capstone dungeon] (research/Structure-Mods-Survey.md)
- STRUCTURES: if no author agrees, build a small prefab placer into SkyyWorldGen? [only if loot piles need it] (research/Structure-Mods-Survey.md)

### mobs

### skills
- PERFECT DODGE (SkyySkills 0.4.37): 50 ms window, x1.25 counter-hit for 0.75 s, +5 Acrobatics XP (max 50 XP / min, monsters' hits only)? [yes; widen to 100 ms if 50 feels too tight]
- PERFECT DODGE: base roll behaviour for everyone, not an Acrobatics perk? [base behaviour] (SkyySkills 0.4.37)
- PERFECT DODGE: show it as a HUD flash or sound instead of a chat line? [chat line now, HUD later] (SkyySkills 0.4.37 / SkyyHud)
- PERFECT DODGE: when a hit is both a Perfect Parries counter-hit and a dodge counter-hit, only the parry multiplier applies? [yes, no stacking] (SkyySkills 0.4.37)
- OVERALL LEVEL: count Farming as the average of Farming / Ranching / Orchard now? [off until Ranching and Orchard have real XP sources] (SkyySkills 0.4.37)
- RANCHING: cap of 200 XP a minute (after boosts) plus 'items a player dropped pay nothing' enough protection against farming? [yes] (SkyySkills 0.4.37)
- /skills page: Fishing / Ranching / Orchard have no rows yet (open with /skills stats <name>) - fine until a later page round? [yes] (SkyySkills 0.4.37)
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your live profiles gained nothing (little class XP yet); check the coin rate before a public launch.

### gear
- HARVEST GATE (SkyyGear 0.3.3): a Crude / Copper SICKLE sweeps Potatoes at half XP while a Crude hoe is refused (vanilla sickles stop at Iron, the sweep has no skip hook). Keep, or measure sickles against the crop's real tier (needs a client-side probe first)? [keep]
- HARVEST GATE: an F-harvest one tier up may still pay full Farming XP (SkyySkills only halves left-click breaks and sickle swings) - fix in SkyySkills? [yes, next Skills round]
- VAULT FETCH (SkyyVault 0.1.6): on a normal server stop the 30 s 'tool on the way' notes are not cleared, so a lifelong tool in flight can show twice (Vault + inventory) after a crash; clearing them risks losing the tool if the player was not saved first. Accept the duplicate-note trade-off? [yes, keep]
- SIGILS: Unique Sigil comes from the Wheat, Oak Log, Cobblestone and Bone collections at tier VI? [yes] (SkyyGear 0.3.4 / Collections 0.2.13)
- SIGILS: players already past tier VI get their Unique Sigil at their next join? [yes] (SkyyGear 0.3.4)
- SIGILS: Mining Set armor refuses Sigils (fixed set bonus; it levels and tiers up instead)? [yes, refuse] (SkyyGear 0.3.4)
- SIGILS: which bosses drop Sigils? [Boss, Guardian, Duke, Dragon, Chieftain, Hedera (incl. Golem_Guardian_Void); not Elite, Ogre, other Golems, Yeti, Rex] (SkyyGear 0.3.4)
- SIGILS: should a Mythic Sigil work on the Anvil (sigil.mythicUse)? [off - Mythic is boss-only, 2026-10-08 lock] (SkyyGear 0.3.4)
- SIGILS: roll back Collections 0.2.13 together with SkyyGear 0.3.4 and put Sigils in a chest before any Gear rollback - add to the deploy rollback notes? [yes] (SkyyGear 0.3.4)
- ARMOR HANDS: Cobalt and Adamantite armor hands cost 1 Enchanted ingot (spec said 0)? [1] (SkyyGear 0.3.4 / Armory 0.1.24)
- HOE AREA: the bigger hoe area also works outside islands? [off] (SkyyGear 0.3.4)
- HOE AREA: the extra tilled blocks cost hoe durability? [no] (SkyyGear 0.3.4)
- MINING ARMOR: lock the higher-tier recipes later (spec: craft the first set once, then only upgrade)? [leave craftable for now] (SkyyGear 0.3.4)
- LOST TOOL (SkyyGear 0.3.2): after you get an exact copy and reforge / tier it up, the original stays Retired for good if it turns up (no swap back, sell or salvage) - else a bad reforge could be undone for free. OK? [yes]
- LOST TOOL: tool in a CLOSED Vault -> /pickaxe gives an exact copy (SkyyVault has no fetch hook yet). OK for now? [yes; add a Vault hook later]
- TOOL PERKS (SkyyTrees 0.3.6): the Tree Feller log table stops at level 6 (1,2,4,5,6,10), so the hatchet perk adds nothing once your tree is level 5+. Give it 8 numbers (e.g. 1,2,4,5,6,10,12,14) as the new default, or will you edit it in Server Setup -> Trees? [8 numbers]
- TOOL PERKS: Vein Mine = +1 ore per tool level on top of the tree's Vein Burst number, total capped at 8. Intended? [yes]







### economy
- AUCTION HOUSE + REBIRTH (SkyyAuctions 0.1.5): unclaimed AH sale coins block a rebirth until the player claims them (then they are lost with the purse). Or should Continue claim them into the purse automatically? [block, ask the player to claim first]
- BAZAAR + REBIRTH (SkyyBazaar 0.1.11): should the Bazaar also refuse trades while a rebirth is busy (today it relies on SkyyCoins 0.1.7 refusing spends; Bazaar sales are income and still land)? [no, rely on SkyyCoins]
- ECONOMY AUDIT: add a real coin sink (the Tab or slayer costs from the old plan) before more faucets? [yes, after rebirth R3; numbers from a measured session] (research/Economy-Audit-1014.md)
- ECONOMY AUDIT: count goods bought with coins before a rebirth in the bank-bonus balance (they are kept either way)? [yes, at 90% of base value] (research/Economy-Audit-1014.md)
- ECONOMY AUDIT: scale merchant prices up 25% per rebirth once rebirth is on? [yes, off until rebirth is on] (research/Economy-Audit-1014.md)

### bags
- AUTO-PICKUP 2 (SkyySacks 0.8.4): seeds / saplings from a harvest go to the Void (not the inventory), so replanting means pulling them out. Keep? [Void]
- AUTO-PICKUP 2: the vanilla 'picked up' popup still flashes next to our feed card. Keep it? [keep]

### classes
- ABILITIES IN THE TREE (SkyyClasses 0.1.22 / SkyyTrees 0.3.7): A (ability) and M (modifier-slot) nodes are free, so turning an ability on is a free click; existing players' abilities start OFF until they click Enable (one-time chat hint)? [yes]
- ABILITIES: a game rune placed on a Mage / Priest Ability 2 / 3 key does nothing and shows a hint (the rune stays in the slot until moved)? [yes, blocked as M2]
- ABILITIES: which modifiers may go in both slots? [Power+, Radius+, Duration+, Efficiency, Pierce, Chain, Slow, Knockback+] (SkyyClasses 0.1.22)
- ABILITIES: Priest Spirit Shield gives the saved player a 4 s personal shield worth 15% of max Health (stands in for 'a small bubble that blocks projectiles')? [15% personal shield] (SkyyClasses 0.1.22)
- ABILITIES: Layered Ward splits the bubble in two equal halves, the inner half regrows 3% of the bubble's HP a second? [yes] (SkyyClasses 0.1.22)
- ABILITIES: lingering burn time 2 s + 0.5 s per level (2.5 s at Lv 1; the Mage class file says 3 s)? [2 s + 0.5 s / level] (SkyyClasses 0.1.22)
- ABILITIES: build the 4 waiting nodes next round (Priest Elemental Bubble PB2, Mage PA4 + PC2, Priest PA2; Guiding Light stays out)? [yes, next round] (SkyyTrees 0.3.7)
- ABILITIES: show ability levels in the SkyyHud ability widget? [later, as a SkyyHud change]
- ABILITIES: class tab is 1600 px wide, the other trees stay 1440? [yes] (SkyyTrees 0.3.7)
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]





### pets
- PET KILLS (SkyyPets 0.2.5 / SkyyMobs 0.1.8 / SkyySacks 0.8.4): pet-kill loot + 'pet damage makes you top damager' are built but cannot be tested until pets fight (SkyyPets 0.4). Keep them idle until then? [yes]
- DRAGON as a pet with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our own dragons later? [(1) summon via our slot if Aures allows + it works, else (2) - docs/answered/pets.md 2026-10-06; decide after the survey + Aures' answer]


### social
- GUILD info takes names with spaces? Needs a fix in SkyyGuilds (and the same left-out-button fix in SkyyShards / SkyyRebirth), not the menu. [yes, small Guilds fix] (SkyyMenu 0.3.23 Admin page)

### profiles

### rebirth
- BANK BONUS (SkyyRebirth 0.2 / SkyyBank 0.1.11): bonus is worked out on the profile's share of min(account total, 10M), the same cap as the brackets? [yes]
- BANK BONUS: it is flat on the whole capped balance - at the +3 total cap that is about +300k a day on a full 10M bank, ~3.5x the 85k base interest. Keep the Q7 numbers or lower / weight by bracket? [keep the Q7 numbers; refresh the Balance Workbench]
- REBIRTH stays OFF for real players until Skyy has tested R1-R4 (Bazaar / AH open-order check is in 0.3)? [keep OFF until Skyy has seen the Nexus tooltip]
- NEXUS: Rebirth / Continue work from both the Nexus click and the left-panel button? [both] (SkyyRebirth 0.3)
- ADMIN TEST REBIRTH works while the feature is OFF and skips the class / place / combat checks? [yes] (SkyyRebirth 0.2)
- R3 resets skills, purse and bank only; tree nodes and ability levels follow in R5 / R6? [ok] (SkyyRebirth 0.2)
- TREE: players cannot respec the tree themselves (admin refund only)? [yes] (SkyyRebirth 0.3)
- TREE: node list right (Wisdom / Dust / Echo / Fortune / tool / stat / keystone titles)? [yes, as built] (SkyyRebirth 0.3)
- TREE: a keystone title replaces 'Void-Touched N' until the next rebirth (newest earned title shows)? [yes] (SkyyRebirth 0.3)
- TREE: +4% points per Echo level (up to +40%), editable? [yes] (SkyyRebirth 0.3)
- TREE: opening row 2 costs 15 points and one maxed skill pays about 8, so the first rebirth cannot open row 2. Keep the spec curve or make early levels cheaper (Tree price growth 1 = every level costs 1)? [keep 1.08] (SkyyRebirth 0.3)

### shards
- CO-OP (SkyyShards 0.1 / 0.2): co-op may enter your shard but only the owner can Collect, buy storage and Grow? [yes; row shard.coopCollect is off]
- MENU TILE: the Shards tile can Enter while the shard is placed, and Collect / upgrade any time once you own one? [yes]
- A picked-up shard (or one left by an island reset) makes nothing until placed again? [yes]
- Island sizes 13 / 21 / 29 and 6 slots from the spec, not the mockup? [spec]
- Growing costs coins + Eternal Seeds + a collection tier? [yes]
- Broken crops grow back free every 90 s, so hand-farming is free wheat? [yes, as you asked]
- Allow 20 shard worlds loaded at once? [20]
- Restyle the shard menu to the Sky Window look once the UI kit has it? [yes, later]
- SkyyCollections: exempt shard credit from the 20,000-per-minute cap? [yes, next Collections round]
- Collect goes to the inventory only until SkyySacks has a give bridge, then Magic Bags first? [yes]
- The totem's numbers count the whole island although its range is smaller, so hand-farming is extra on top? [yes for 0.1; range-based later (0.2 made range decide production)]
- One worker is capped at 12 items / minute before modifiers (the spec's limit; Server Setup -> Shards -> Totems -> Worker cap)? [yes, 12] (SkyyShards 0.2)
- Range decides production: a starter Harvest Spirit I makes 1 per minute on every island size, so growing only pays once a totem's range reaches the new crops? [yes] (SkyyShards 0.2)
- Totems are placed / picked up from the menu, and totems + modifiers are crafted in the shard menu (not at a bench)? [menu] (SkyyShards 0.2)
- Rebirth collection ranks give no reward (shown and announced only)? [none] (SkyyShards 0.2 / Collections 0.2.14)
- Each rebirth rank past a collection's last tier needs that tier's amount x 2^k (rebirth.rankFactor)? [2]
- An Enchanted crop from Harvest Moon counts as 100 Wheat for XP and collections? [yes] (SkyyShards 0.2)
- Totem tier speeds 1 / 1.25 / 1.5 / 1.75 / 2, and tier-up costs Enchanted Wheat : essence 1:10, 2:25, 3:50, 5:100 (spec's later steps are 2:25 ... 8:200)? [yes; 1:10 ... 5:100]
- MIT fold of MoreTotems (repo returns 404 so the licence cannot be re-checked): keep it with the 'Copyright (c) Nagatwin' notice? [keep] (SkyyShards 0.2)
- The MoreTotems pack mod still adds its own Water Totem, so two rain totems are live (no-duplicates rule): switch the pack mod off and record it in PACK.md? [switch off; main session]
- Collects made in creative mode count toward collections only at a later Collect in Adventure? [yes]
- One Farming Shard per profile, ever; a lost one comes back only via /shardadmin give; crafting at rebirth 2 only for a profile that never had one? [yes] (SkyyShards 0.2)
- Handheld Rain Totem ('click = 30 s of rain, costs Mana') is not built: build it with the Mana round? [Mana round]

### quests
- DAILY JOBS (SkyyQuests 0.3): daily kill jobs pay an unidentified weapon and armor piece every time (up to 3 of each a day). Keep, or gear on only one job a day (else coins + item)? [gear on every kill job]
- Marlow's pole becomes a lifelong SkyyGear tool later (a SkyyGear round)? [yes]
- Quest Board look: Kweebec clerk or a board prop? [Kweebec until the prop is proven]
- Markers: floating '!' plus your own signs, or only your own signs? [both; Server Setup switch]
- 'Catch a fish' can be skipped to finish Marlow's line early? [yes, like every tutorial task]
- Daily 'Mine 64 stone' counts only natural blocks (stops place + re-break)? [allow for now]

### ui
- ADMIN PAGE (SkyyMenu 0.3.23, research/Admin-Page-Plan.md): one Admin page in the SkyWynn Menu (right bar, admin only), tabs Server / Economy / Players / Diagnostics? [yes, as built]
- ADMIN PAGE: buttons run the existing commands as you (chat shows output), 5 status buttons also show a one-line result on the page? [yes, option C]
- ADMIN PAGE: which buttons first? [all six first (pause AH, list merchants, reload mod, set hub spots, exploration stats, server stats), the rest after]
- ADMIN PAGE: dangerous buttons (reset, remove, repay) confirm for 5 s before they run? [yes]
- ADMIN PAGE: restyle to the final tab look after the Sky Window kit probe (/skyprobe kit)? [yes]
- ADMIN PAGE: build 'Recent warnings' and 'Economy snapshot' later (each needs a new published value from the mods first)? [yes, later]
- SOUNDS (research/Sound-Pass-Plan.md): build an admin /soundtest <id> command first so you can audition ids by ear? [yes, in the SkyyMenu admin page]
- SOUNDS: quiet things (feed cards, XP gains, double drops) stay silent; sounds only on level ups, quest done, rewards and casts? [yes]
- SOUNDS: a custom level-up / rebirth fanfare needs audio we own or CC0 - later, or vanilla-only for release? [vanilla-only for release]
- SOUNDS: ability casts - own vanilla sound per ability where one fits, or one shared cast sound? [own per ability where a vanilla one fits, shared fallback]
- HUBS: Character hub tabs separate (Stats, Skills, Trees, Class, Pets, Collections, Profiles - as built) or merged like your 2026-10-10 pick (Stats+Skills, Trees+Abilities, Collections+Recipes; also Bank+Vault, Bazaar+Auction House)? [separate now, merge later if you pick merged]
- HUBS: scrolling lists OK on Skills (11 of 12 rows show), Class (7 of 8 cards), Profiles (7 cards)? [yes]
- GEAR: benches refuse vanilla Iron / Thorium / Cobalt / Adamantite armor and gathering tiers 2+ (Anvil tier-up only; row gear.gatherAnvilOnly)? [yes, ON]
- THE ARMORY: its jump-height system writes jump force directly, so our speed / jump bonuses pause while it is on - keep The Armory on? [on until you decide]
- SAP TAPPER: should the perk's extra Tree Sap count toward the Tree Sap collection (today only the base sap does)? [yes]
