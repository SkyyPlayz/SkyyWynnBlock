# SkyWynn - RESUME HERE (updated 2026-10-16 ~05:45 MDT: RUNNING: wd024 Wardrobe 0.2.4 + gear0312 Gear 0.3.12 + menu0330 Menu 0.3.30 + hud0328 Hud 0.3.28)

Big picture for other agents: `STATUS.md`. Map: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`. Skyy's tests:
`TEST-CHECKLIST.md`. History: `docs/log/2026-10.md` (2026-10-15 / 16 lines). Decisions word for word: `docs/answered/<topic>.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage). The weekly limit was hit once on 10-15 ~22:30 and Skyy reset it.
2. DEPLOY TARGET IS THE WORLD **NewBetaTest** (`tools/deploy_set.py` WORLD; backup_deploy / smoke_test follow it). Skyy plays there with a
   friend (WesleyPlayz, Assassin). The old world `HUD mod` is no longer deployed to.
3. RUNNING (10-16 ~11:00): lean builder wd024 (SkyyWardrobe 0.2.4, NEXT 0) + workflow gear0312 (SkyyGear 0.3.12, NEXT 1) [BEFORE PIN: also rename the /smithing CRAFT tab to SMITHING, gear.md 10-16 + Upgrade tab 8 rows per page (smaller icons/rows) - lean follow-up on the 0.3.12 patch]
   + lean builder hud0328 (SkyyHud 0.3.28: widget Background OFF by default except Quest Tracker, ui.md 10-16)
   + workflow menu0330 (SkyyMenu 0.3.30: no duplicate icons / entries, menu scaled up, Home 'Right now' panel + the queued Menu items; ui.md 10-16) [BEFORE PIN: HUD shortcut opens the HUD editor directly, ui.md 10-16]; if this
   session died, check their scratch / files, review, pin, deploy. Nothing pinned-but-not-deployed. Last deploys: 10-15 23:14 (TEST-CHECKLIST 137) and 10-16 05:31 (138).
4. Kit `tools/skyyui.py` is now kit 1.6 (KIT_HUB_VERSION 1.6, KIT_VERSION still "1.5"): builds no longer need the old HEAD-kit preload.
5. Rounds: saved workflow `skywynn-round` (Skyy's OWN words + the popup question in args.quotes; resuming a workflow needs the args
   again). Deploy only with the game closed: backup -> smoke (`--allow-pack-api`) -> deploy_set --yes -> record_deploy -> commit -> tidy.
   Never SendMessage an agent inside a workflow (stop + relaunch); plain Agent builders can be messaged. Skyy answers popups.

## NEXT (Skyy 2026-10-16: "watering can first then pet eggs")
0. **Quick fix first (Skyy test feedback):** SkyyWardrobe 0.2.4 - the Requip ability area = the 2 equipped abilities + 2 modifier slots under EACH ability (SkyyClasses' Lattice loadout data via class:fn:abilPanel / AbilLoadout), not 0.2.3's 4 keys (2 + 2 crouch alts); clickable + saved per loadout, applied on Equip (bags.md 10-16). Lean round.
1. **WATERING CAN + HARVESTER** (research/Watering-Can-Harvester-Spec.md; docs/answered/gear.md 10-15): lifelong can in the starting
   kit, T1 Crude (wood) -> T2 Copper -> T3 Iron ...; tier = watering area 1x1 / 3x3 / 5x5 / 7x7; point upgrades Capacity / refill,
   Growth boost, Lasting water, Bloom; Harvester = hoe + sickle merged at the Anvil after rebirth 1; tier tags (standing rule). Full round
   on SkyyGear 0.3.12 (+ SkyySkills / Fishing only if needed). Also fold in: SkyyGear's longsword tooltip still says 'Charged Attack
   20-28' (now Crescent Rush); the ("Spellblade","Battlemagic") class-skill pair; move Gear's own hpr / hprp regen onto skill:fn:hpregen.
1b. **NORMAL TOOLS OFF EVERYWHERE** (gear.md 10-16, popups answered): no recipe / no crafting listing / no chest, Lost Loot, air-drop or mob
   drop for normal pickaxes, hatchets, hoes, sickles, fishing rods, watering cans (shovels stay); pack mods' ones hidden at runtime by id; owned normal
   tools removed once per profile; lifelong (stamped) tools untouched. FULL round (ultracode: item removal + several mods) right after gear0312 deploys.
1c. **LIFELONG ACCESSORY BAG / POCKET DIMENSION / MENU ITEM + no 2nd bag on /island reset** (gear.md 10-16): like the forever tools - one per
   profile, can't be lost, extras cleaned, a recall command each; island reset / kit never re-gives owned once-only items. FULL round (Accessories +
   Sacks + Menu + Islands) after menu0330 deploys.
2. **PET EGGS + HATCHING** (research/Pet-Eggs-Spec.md; pets.md 10-15): 30 eggs (Mining / Farming / Foraging / Combat / Exploration x
   Common..Mythic), roll 1 pet (best -> worst weights by egg rarity), roll 2 rarity, atomic hatch then ~3 s two-reel animation, sources
   (skill drops, collections, crafting, shops). 5 questions open in OPEN-QUESTIONS.md with defaults - use the defaults unless Skyy answers.
   Rounds A0 art, R1 SkyyPets 0.4.0 (ultracode), R2 Skills, R3 Bazaar + Merchants, R4 Collections.
3. Then (queued): ONE SkyyArmory round = Great Shield (Spellblade: bash chain, full guard 70% melee / 100% projectiles, Bulwark Charge; research/classes/Spellblade.md) + Warrior sword Thrust dash range boost (classes.md LOCKED 2026-10-08; Skyy 10-16 'add the changes to the warrior traversal to the que, along with the great shield'); WorldGen 0.7.1 (zones-world weather list - vanilla
   SensorWeather NPE; 'Zone 1 = server spawn' switch + /zone setlanding in the zones world, world.md 10-15); Menu 0.3.30 (Storage + World hub tiles get their OWN icons - they reuse Pocket Dimension / Teleport, Skyy 10-16 ui.md; Invite to Guild
   button, Stats 'Health Regen' row from skill:fn:hpregen, 'Battlemagic' in CLASS_SKILLS, hub tab icons from art/hub-tab-icons/ as
   <name>@2x.png); Accessories Regeneration onto skill:fn:hpregen; Trees health-regen nodes; small companions: SkyyPets POLL_SKILLS +
   pets:fn:owned bridge, SkyyGuilds SKILL_NAMES (Spellblade), SkyyCollections maskOf (fabric not Smithing), Bazaar price guard reads our
   standalone recipes, deploy_set tune_perfect_parries Spellblade / Longsword_* entry, tier tags T2-T4 (research/Tier-Tags-Plan.md).
4. Later: Hubs H4-H7 (Sacks / Wardrobe / Gear / Accessories tabs into the hub bar), merge phases 2/3/8, SkyyZones server protection,
   menu icon waves 2-5, Subcaverna as a later zone (licence check), load tests, release.

## What Skyy should test (TEST-CHECKLIST 137 + 138, world NewBetaTest)
Battlemagic levelling, health regen, fortune card, Tools tab tier up, Home menu + Teleport centre, Smithing UPGRADE tab, sickle sweep +
fewer sticks, pole in kit + no-tackle fishing, Crescent Rush + sword guard, Accessory Bag Craft tab + auto-equip + lanterns, Requip pet /
ability slots, bag costs + space, Bazaar CONFIRM + prices, starter Accessory Bag, Assassin kunai, Tree
Feller row III, /zone 1 (new zones world skywynn_zones2 with islets + waterfalls; /zone old6 = the old one). Scan both logs after play
(Jev via tools/llm.py) and recycle old logs.

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
