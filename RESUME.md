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
Nothing. All 10-16 rounds are deployed (TEST-CHECKLIST 139-153).

## NEXT (after the running rounds; each answer word for word in docs/answered/)

0. FROM THE 10-16 OPEN-QUESTIONS PASS (word for word in docs/answered/*.md, dated 2026-10-16) - queued builds:
   a. DEPLOY when the game closes: SkyySkills 0.4.44 (dodge every direction + class styles + perfect dodge) and SkyyRebirth 0.3.4 (rebirth ON) - both pinned.
   b. farm01 / gear0314 (SkyyGear): retire hoe + sickle -> start with Crude Harvester + can (merge existing), sweep tier rule, Sigils on Mining
      Sets, Sigil drop sources by rarity, Mythic Sigil usable, till area everywhere.
   c. Collections + tool upgrades redesign (needs a spec): every tier unlocks recipes / Enchanted Block 2nd compression / lower coins + tool
      points; uncapped Breaking Power + Swing Speed lines; Fortune past 100% = triple drops; multitool keeps highest power / speed + all mods;
      collection ranks give Enchanted items; Enchanted -> 100 base un-compress (auto if possible); Void auto compactor (Rare+, bought per bag).
   d. Void Particles rebirth currency (spec update research/cloud/Rebirth-Spec.md, then a rebirth round).
   e. Totem workers scale + totem Fortune + totem page with upgrades + AUGMENT slots (Compactor, Chrono Stasis), totem-workbench crafting;
      totem tier-up costs by totem kind; REMOVE the MoreTotems fold (spec first).
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
