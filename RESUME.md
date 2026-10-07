# SkyWynn - RESUME HERE (updated 2026-10-06 evening)

Read this first, then only what the task needs. Map of every file + search tips: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions:
`HANDOFF.md`. Open questions: `OPEN-QUESTIONS.md`. Skyy's tests: `TEST-CHECKLIST.md`. Running log (all history): `docs/log/2026-10.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly resets TUESDAYS 15:00 UTC; 2026-10-06 ended near 20% weekly).
2. **FIRST JOB (Skyy): the COPPER LIGHT-ARMOR CHEST in Blockbench.** Skyy must have Blockbench OPEN. MCP server "blockbench" =
   http://localhost:3000/bb-mcp (in ~/.claude.json); skills in ~/.claude/skills: load `blockbench-use` first, then `blockbench-hytale`
   (format hytale_character, 64 units per block, texture sides multiples of 32), `-modeling`, `-texturing`. Design: the Copper body of
   `research/cloud/light-armor/light-armor-sheet-v2.png` (black leather + copper trim) + `.claude/skills/skywynn-art/SKILL.md`; NO helmet
   (helmets v3 pending). Vanilla reference: Assets.zip `Common/Items/Armors/<metal>/Chest.blockymodel` - vanilla-derived files stay LOCAL
   (pick a git-ignored folder, add it to INDEX.md "Local only"). Save .bbmodel + .blockymodel + texture for Skyy to open.
3. Then Skyy's test results (TEST-CHECKLIST.md "Test next": everything deployed 2026-10-05 / 06, items 17-39); fixes first.
4. Rounds: launch with the saved workflow `skywynn-round` (`.claude/workflows/skywynn-round.js`; put Skyy's OWN words in args.quotes);
   record each deploy with `python tools/record_deploy.py` (PROJECT-RULES 3 + 4).

## Now
- LIVE: 28 jars (SET in `tools/deploy_set.py` = HANDOFF section 1). Deployed 2026-10-06 (all untested by Skyy unless TEST-CHECKLIST says):
  Collections 0.2.7 + Accessories 0.5.6 (Lanterns behind Tree Sap), Bazaar 0.1.5 + Sacks 0.7.13 (sell from bags), Classes 0.1.12, Armory
  0.1.3 (staff blink + trail, wand hop + hang + burst + heal circle, Grapple Bolt, bow leap + blast, particles fade, hop 30, Copper /
  Onyxium crossbows), Mobs 0.1.4 + Gear 0.2.6 + Skills 0.4.20 (mob curve, weapon speed tiers, 8-way roll on a sprint tap), Hud 0.3.16
  (minimap with BetterMap, Dynamic Seasons widget mover), Bank 0.1.7 (daily interest), SkyyGatherProbe 0.1 + B (probe pack - REMOVE both
  from SET after Skyy's probe session, TEST-CHECKLIST 31). Newest backup `backups\deploy-20261006-2015`.
- Skyy tested 2026-10-06 (log): Grapple works; wand heal circle works; minimap works in the hub; live settings Skyy chose: hop.force 30,
  blink.distance 16, blink.floorCheck 0 (the last two become defaults in SkyyArmory 0.1.4).
- NOTHING RUNNING. Cloud session: `CLOUD-RESUME.md` (art redos: helmets v3, mining v3 half plate, Enchanted icons v2, Monk emblem,
  Stamina icon; fishing junk; reference pictures are local in `research/refs/`, described in docs/answered/gear.md).

## Next, in order
1. Small follow-ups: SkyyArmory 0.1.4 (blink 16 + floorCheck 0 defaults); SkyyGear next = add `Weapon_Crossbow_Copper_Wynn` /
   `_Onyxium_Wynn` to its crossbow trust list (Charged combo). OPEN-QUESTIONS gear: Onyxium crossbow recipe, leap on the 6 developer bows.
2. GATHERING LADDER phase A after the probe results: `research/Gathering-Progression-Spec.md` + Skyy's updates at the top of its section 4
   (ratio 100, Enchanted INGOTS / Cobblestone + Rubble / one per log, premium, Fortune on all tiers, hard ore gates need SkyyGear pickaxe
   overrides, Mithril hidden until 0.7). Then B1 tool levels, B2 tool locks, C foraging armor, D mining (half plate) + farming armor, E, F.
3. ARMOR TYPES (Heavy / Light / Cloth, docs/answered/gear.md 2026-10-05) with the Blockbench models; Light armor helmets after v3 art.
4. Stats page (`research/cloud/Stats-Page-Spec.md`), SkyyFishing (spec draft + Skyy's answers: all parts kept, vanilla junk), food
   expansion, loot round revision, class-ability spec, Monk, starter shards, worldgen stage 2, Accessory Table (ask), SkyyEconomy merge
   after Skyy tests, Hytale 0.7 fix list, LAST: Pocket Dimension release kit.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches - their
  successors are built from the edited scripts.
- Rollback floors: HANDOFF section 1 + the comments in `tools/deploy_set.py`. Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`.
- Local files (git-ignored) stay tidy: `python tools/tidy_local.py --yes` after every deploy; where everything is: INDEX.md "Local only" +
  `backups/README.md` (every backup, incl. the packed ones in `backups/archive/`).

## On Skyy's PC (read-only except the deploy)
Project = this repo: `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\`. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\
release\package\game\latest\` (`Server\HytaleServer.jar`, `Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\
Saves\HUD mod\` (`config.json`, mod data `mods\Skyy_Skyy<Mod>\`, server logs `logs\`); client logs `...\UserData\Logs\`. Backups:
`backups\` (git-ignored). Claude's memory: `C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK\memory\`.
Release files for public mods: `Desktop\Hytale mods WORK\Your new mods\`. The other folders in `Hytale mods WORK` (`Hytale mods`,
`Your new mods`, `lynk to Hytale Game`, the new `Hytale Projects`) are Skyy's, not part of the build. Toolchain: Python 3.12 + jpype1 +
jdk4py (no javac). LOCAL ONLY, never in git: game files, UserData, backups, built jars (except
`tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
