# SkyWynn - RESUME HERE (updated 2026-10-16 ~09:05 MDT: Skyy at work; Claude works the queue, stops new work at 95% weekly usage)

Big picture for other agents: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage).
2. DEPLOY TARGET = world **NewBetaTest** (`tools/deploy_set.py` WORLD). Skyy plays with a friend (WesleyPlayz, Assassin).
3. Deployed 10-16 (TEST-CHECKLIST 139-146): Hud 0.3.28, Essentials 0.1.11 (crops back - DynamicSeasons Compost_Soft), Menu 0.3.30, Cooking 0.1.8
   (food families), Fishing 0.1.8 + Sacks 0.8.10 + Shards 0.4.1, Classes 0.1.30 + Trees 0.3.18 (top-down tree), Bazaar 0.1.15 (x4.5 prices,
   sell per tab), Gear 0.3.12 (watering can + Harvester), Wardrobe 0.2.4 (Requip loadout rows, TEST 147), Sacks 0.8.11 + Accessories 0.5.19 + Menu 0.3.31 (Crafting hub, TEST 148). deploy_set rules added: Sacks 0.8.10 needs Fishing 0.1.8; Trees 0.3.18 <-> Classes 0.1.30.
4. Rounds: while Skyy is chatting about other topics, run builders as PLAIN Agents (workflow builders refuse - memory note) and spawn the
   critics yourself; else the saved workflow `skywynn-round`. Deploy only with the game closed: backup -> smoke (`--allow-pack-api`) ->
   deploy_set --yes -> record_deploy -> commit -> tidy. Never SendMessage an agent inside a workflow; plain Agent builders can be messaged.

## RUNNING NOW (plain Agent builders unless noted; if this session died: check their files, review, pin, deploy)
- life01 Accessories / Sacks / Menu / Islands: lifelong Accessory Bag + Pocket Dimension + Menu item (recall commands), no 2nd copy on reset.
- pets040 SkyyPets 0.4.0 = Pet Eggs R1 (eggs + hatching + Pets page grid / flavor text / filters). Art drafts in art/pet-eggs (sent to Skyy).
- armory0129 SkyyArmory 0.1.29: Great Shield, Crescent Rush = pushing lunge, Mage teleport look, Warrior Thrust range.
- wg071 SkyyWorldGen 0.7.1: zones-world weather fix + Zone 1 = server spawn switch + /zone setlanding.
- tools01 SkyyGear 0.3.13 (+ Mobs / Exploration / Collections / Bazaar as needed): normal tools off everywhere (owned ones removed once)
  + Enchanted Sticks for T4+ tool tier-ups.

## NEXT (after the running rounds; each answer word for word in docs/answered/)
1. **Lifelong Accessory Bag / Pocket Dimension / Menu item + no 2nd bag on /island reset** (gear.md 10-16) - Accessories + Sacks + Menu +
   Islands - NEXT to launch.
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
