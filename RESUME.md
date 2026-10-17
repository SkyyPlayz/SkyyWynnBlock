# SkyWynn - RESUME HERE (updated 2026-10-16 ~09:05 MDT: Skyy at work; Claude works the queue, stops new work at 95% weekly usage)

Big picture for other agents: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage).
2. DEPLOY TARGET = world **NewBetaTest** (`tools/deploy_set.py` WORLD). Skyy plays with a friend (WesleyPlayz, Assassin).
3. Deployed 10-16 (TEST-CHECKLIST 139-146): Hud 0.3.28, Essentials 0.1.11 (crops back - DynamicSeasons Compost_Soft), Menu 0.3.30, Cooking 0.1.8
   (food families), Fishing 0.1.8 + Sacks 0.8.10 + Shards 0.4.1, Classes 0.1.30 + Trees 0.3.18 (top-down tree), Bazaar 0.1.15 (x4.5 prices,
   sell per tab), Gear 0.3.12 (watering can + Harvester), Wardrobe 0.2.4 (Requip loadout rows, TEST 147), Sacks 0.8.11 + Accessories 0.5.19 + Menu 0.3.31 (Crafting hub, TEST 148), WorldGen 0.7.1 (Zone 1 spawn, TEST 149), Pets 0.4.0 (eggs, TEST 150), Gear 0.3.13 + Collections 0.2.20 + Bazaar 0.1.16 +
   Armory 0.1.29 + Classes 0.1.31 (normal tools off, Enchanted Sticks, Great Shield, Crescent Rush lunge, TEST 151), lifelong bag / pocket /
   menu item (Accessories 0.5.20, Sacks 0.8.12, Menu 0.3.32, Islands 0.5.17, TEST 152), Classes 0.1.32 + Hud 0.3.29 (Arcane Breach arc, Stacks widget, TEST 153). deploy_set rules added: Sacks 0.8.10 needs Fishing 0.1.8; Trees 0.3.18 <-> Classes 0.1.30.
4. Rounds: while Skyy is chatting about other topics, run builders as PLAIN Agents (workflow builders refuse - memory note) and spawn the
   critics yourself; else the saved workflow `skywynn-round`. Deploy only with the game closed: backup -> smoke (`--allow-pack-api`) ->
   deploy_set --yes -> record_deploy -> commit -> tidy. Never SendMessage an agent inside a workflow; plain Agent builders can be messaged.

## RUNNING NOW
- DEPLOYED 10-16 afternoon (TEST-CHECKLIST 155-158): menu merges (Stats in Skills, Class in Trees, Bank+Vault, Bazaar+AH, recipes in
  Collections), Cooking 0.1.10 (one food family = one bar), Accessories 0.5.21 (craft + upgrade in the bag), Sacks 0.8.14 (Enchanted Void homes,
  scroll craft list, no Void level gate), Gear 0.3.15 + Menu 0.3.34 (Crafting hub Crafting / Smithing / Anvil / Upgrade, big top row on Gear
  pages), Pets 0.4.1 (Eggs + Hatchery), Skills 0.4.46 + Hud 0.3.30 (log fixes).
- DEPLOYED 18:08 SkyyMenu 0.3.35 = menu sweep K (kit 1.7 hub_page, TEST 160). RUNNING (plain Agents): menu sweep S1 (Skills, Trees +
  Classes, Pets, Collections (legacy_0221 freeze), Profiles) + S2 (Sacks, Wardrobe, Vault + Bank, Bazaar + Auctions, Merchants). Each report ->
  Sonnet critic -> fix -> pin -> deploy. Then S3 (Gear, Islands, Exploration, Quests q04, Party, Guilds) + S4 (Hud, Accessories after AP1, Ranks,
  Essentials, Fishing, Shards, Rebirth), then lint menu_pattern -> FAIL. Leftovers: Menu Ops window, Server Setup row pages -> scroll, SkyyCore 1.0.1 HubBar.
  Queued: SALVAGE (SkyyGear gear:fn:salvage + Wardrobe; bags.md 10-16).
- NEXT IN ORDER (specs answered, word for word in docs/answered/):
  1. MENU SWEEP (research/Menu-Pattern.md, answers at the end): kit round K (skyyui 1.7 + Menu 0.3.35; the BIG HUB ROW helper from Gear 0.3.15
     exists), then S1-S4 + Quests q04 (section 4). Every page 1600 x 980, big row 2, short lists fill, scroll not pages.
  2. Collections 0.2.23 + Bazaar 0.1.18: Life Essence 1:1 -> vanilla Greater Essence (skyyench RETIRED_TO; 0.2.22 script needs
     skyyench.legacy_0221() to rebuild), Eternal Seeds at crop collection tier 4, list the Enchanted items after sizing collection gifts.
  3. AP1 Accessories 0.5.22 (research/Accessory-Power-Spec.md + answers; Void Charms rename, no bag item, /charm /charms /ch, bag grid).
  4. T1 tool upgrades = Gear 0.3.16 + Skills 0.4.47 (research/Collections-Tools-Redesign-Spec.md last section).
  5. Flask / Pouch (research/Flask-Pouch-Spec.md + answers): probe FP0, then FP1 (SkyyCooking).
  6. Mod compression after the menus (sections stay separate - Architecture-Spec.md last section).

## NEXT (after the running rounds; each answer word for word in docs/answered/)

0. FROM THE 10-16 OPEN-QUESTIONS PASS (word for word in docs/answered/*.md, dated 2026-10-16) - queued builds:
   a. (done 10-16: Skills 0.4.44 + Rebirth 0.3.4 deployed)
   b. farm01 / gear0314 (SkyyGear): retire hoe + sickle -> start with Crude Harvester + can (merge existing), sweep tier rule, Sigils on Mining
      Sets, Sigil drop sources by rarity, Mythic Sigil usable, till area everywhere.
   c. Collections + tool upgrades redesign (needs a spec): every tier unlocks recipes / Enchanted Block 2nd compression / lower coins + tool
      points; uncapped Breaking Power + Swing Speed lines; Fortune past 100% = triple drops; multitool keeps highest power / speed + all mods;
      collection ranks give Enchanted items; Enchanted -> 100 base un-compress (auto if possible); Void auto compactor (Rare+, bought per bag).
   d. Void Particles rebirth currency (spec update research/cloud/Rebirth-Spec.md, then a rebirth round).
   e. Totem workers scale + totem Fortune + totem page with upgrades + AUGMENT slots (Compactor, Chrono Stasis), totem-workbench crafting;
      totem tier-up costs by totem kind; REMOVE the MoreTotems fold (spec first).
   k. CRAFTING PAGE (SkyySacks /craft): bigger rows (name + cost), ~6 rows visible, scroll instead of pages - ui.md 10-16; launch as soon as hubcoll is done.
   l. REMOVE Enchanted Essence of Life -> vanilla Greater Essence (Ingredient_Life_Essence_Concentrated), 1:1 convert held ones (gear.md 10-16);
      rides Collections 0.2.23 (+ Sacks / Bazaar rows) after hubcoll / hubmkt.
   j. ETERNAL SEEDS locked to each crop's collection tier 4 (recipe + Bazaar buy; Server Setup row) - economy.md 10-16; rides Collections 0.2.23 + Bazaar 0.1.18.
   i. NEXT ROUNDS for C1: Bazaar 0.1.18 lists the 83 new Enchanted items - FIRST size the collection gifts to item value (critic: up to ~40 Enchanted
      Mithril free) or keep gift items off market; freeze NEW0116 to TABLE_20; ResourceTypeId recipe pricing; Sacks rebuild (homes for 103 rows,
      Combat / Smithing cats); Gear T1 reads coll:fn:toolPts + coll:tierups (Anvil gate). (Armory boss Sigil double roll fixed in 0.1.30.)
   g. BEASTMASTERY skill (skills.md 10-16): spec then Skills + Trees + Pets rounds.
   h. Gathering stat lines on gear rolls / accessories / pets (gear.md GATHERING STAT SOURCES); four-power-sources rule.
   f. Small rounds: Exploration names (Loot Bag / Lost Treasure / Magic Box); /spawn for players (WorldGen 0.7.2); guild names with symbols;
      AH rebirth auto-claim; seeds / saplings Void toggles; hide vanilla pickup popup + restyle our feed; hub merges (Stats+Skills, Trees+
      Abilities, Collections+Recipes, Bank+Vault, Bazaar+AH); Sap Tapper extra sap counts; Tree Feller 8-number table; food Strength scales
      with Grade capped 10 min; shard co-op Collect; structure mods we can use without asking (+ draft the joszza message); 4 waiting tree
      nodes; Aures dragon pet (allowed); pet roster adds + collection egg catch-up; release = CurseForge first, 'Isles of the Void' 1.0.0.
2. **Movement vs The Armory** (log 10-16): Armory's JumpHeightModifierSystem writes MovementSettings -> our speed / jump bonuses pause. Make our
   movement protocol compose with it (SkyyCore / Skills / Accessories / Trees) + find the ~230 client 'Equipment packet on the local player' WARNs.
3. **The Armory gear into our systems** (gear.md 10-16; research/Pack-Armor-Plan.md) - ultracode after tools01 (Gear + Mobs + loot).
4. **Pet eggs R2-R4** (Skills drops, Bazaar + Merchants, Collections) after pets040.
5. **Smelting accessory** (gear.md 10-16) - short spec, then Accessories + Sacks furnace + Collections - can launch now.
6. **Food follow-up**: cook:fn:bonus bridge readers (SkyyGear Strength, SkyySkills food Mana Regen %) - spec in the 0.1.8 patch notes.
7. **Class emblems in the UI** (art/class-emblems; the 7 were approved 10-06, Spellblade crest + 5 Spellblade ability icons are DRAFT) - wire into
   Profiles / class pick / Class tab after Skyy looks at the sheets; wire the ability icons into the tree / loadout / HUD.
8. Small companions (old item 3): Accessories Regeneration onto skill:fn:hpregen; Trees health-regen nodes; SkyyPets POLL_SKILLS + pets:fn:owned;
   SkyyGuilds SKILL_NAMES (Spellblade); SkyyCollections maskOf (fabric not Smithing); deploy_set tune_perfect_parries Spellblade / Longsword_*;
   tier tags T3 (Fishing / Accessories / Exploration / Shards own ladders); Bazaar follow-ups (Collections coin unlocks ~4.5x dearer).
9. Later: Hubs H4-H7, merge phases 2/3/8, SkyyZones server protection, menu icon waves 2-5, Subcaverna zone (licence check), load tests, release.

## What Skyy should test (TEST-CHECKLIST 137-146, world NewBetaTest)
See TEST-CHECKLIST.md (one line per deploy). Scan both logs after play (Jev via tools/llm.py), fix ours, recycle old logs.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches.
- Rollback floors: HANDOFF section 1 + the comments in `tools/deploy_set.py` (new: Skills 0.4.43 Battlemagic key, Bazaar 0.1.14 prices,
  WorldGen 0.7 zones2). Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`.
- Standing rules added 10-15: tier tags on every tiered item (PROJECT-RULES 4); check for an existing mod before building one.
- If a test smoke server from a builder is still running, deploy_set refuses - wait for it (we may not kill it).
- Local files stay tidy: `python tools/tidy_local.py --yes` after every deploy.

## On Skyy's PC (read-only except the deploy)
Project = this repo: `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\`. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\
release\package\game\latest\` (`Server\HytaleServer.jar`, `Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\
Saves\NewBetaTest\` (`config.json`, mod data `mods\Skyy_Skyy<Mod>\`, server logs `logs\`); client logs `...\UserData\Logs\`. Backups:
`backups\` (git-ignored). Claude's memory: `C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK-SkyWynn-PROJECT\memory\`.
Toolchain: Python 3.12 + jpype1 + jdk4py (no javac). LOCAL ONLY, never in git: game files, UserData, backups, built jars (except
`tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`, preview PNGs.
