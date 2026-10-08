# SkyWynn - RESUME HERE (updated 2026-10-07 10:45)

Read this first, then only what the task needs. Map of every file + search tips: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions:
`HANDOFF.md`. Open questions: `OPEN-QUESTIONS.md`. Skyy's tests: `TEST-CHECKLIST.md`. Running log (all history): `docs/log/2026-10.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly resets TUESDAYS 15:00 UTC; 2026-10-06 ended near 20% weekly).
2. **ART DONE 2026-10-07** (workflow wf_bb62eb52-952): `models-local/art/<family>/` (accessories, staffs + bo, spellbooks, kunai,
   soulcage, fists, fishing; each sheet.png + manifest.json + README.md), generators `tools/art/make_*.py`. Skyy reviews the sheets ->
   answers OPEN-QUESTIONS gear "ART" lines -> then a build round wires them in (SkyyAccessories icons, SkyyArmory staffs; new item
   families need specs + items). Existing-mods check: `research/Existing-Mods-Gear-Survey.md` (nothing covers our gear).
   LIGHT ARMOR (paused, Skyy: "we can work on the armor more later"): `python tools/make_light_bases.py` (+ make_light_legs.py) ->
   `models-local/light-armor/sets/<tier>/` (Copper/Iron = Ornate Bronze + our legs, Thorium/Cobalt = Cobalt + sleeves, Adamantite/Mithril =
   black Mithril, Onyxium = Prisma; option `onyxium-dark`). Blockbench tabs saved in `models-local/blockbench-saves/`. Blockbench MCP =
   stdio bridge `tools/bb_mcp_stdio.py` (Avast breaks localhost HTTP). Skyy's choices: docs/answered/gear.md 2026-10-07; log 06:50-09:55.
3. Then Skyy's test results (TEST-CHECKLIST.md "Test next": everything deployed 2026-10-05 / 06, items 17-40); fixes first.
4. Rounds: launch with the saved workflow `skywynn-round` (`.claude/workflows/skywynn-round.js`; put Skyy's OWN words in args.quotes);
   record each deploy with `python tools/record_deploy.py` (PROJECT-RULES 3 + 4).

## Now
- LIVE: 28 jars (SET in `tools/deploy_set.py` = HANDOFF section 1). Deployed 2026-10-06 (all untested by Skyy unless TEST-CHECKLIST says):
  Collections 0.2.7 + Accessories 0.5.6 (Lanterns behind Tree Sap), Bazaar 0.1.5 + Sacks 0.7.13 (sell from bags), Classes 0.1.12, Armory
  0.1.3 (staff blink + trail, wand hop + hang + burst + heal circle, Grapple Bolt, bow leap + blast, particles fade, hop 30, Copper /
  Onyxium crossbows; 0.1.4 night: blink 16 + floorCheck 0 defaults), Gear 0.2.7 (night: Charged trust for the _Wynn crossbows), Mobs 0.1.4 + Gear 0.2.6 + Skills 0.4.20 (mob curve, weapon speed tiers, 8-way roll on a sprint tap), Hud 0.3.16
  (minimap with BetterMap, Dynamic Seasons widget mover), Bank 0.1.7 (daily interest), SkyyGatherProbe 0.1 + B (probe pack - REMOVE both
  from SET after Skyy's probe session, TEST-CHECKLIST 31). Newest backup `backups\deploy-20261006-2315`.
- Skyy tested 2026-10-06 (log): Grapple works; wand heal circle works; minimap works in the hub; live settings Skyy chose: hop.force 30,
  blink.distance 16, blink.floorCheck 0 (defaults since SkyyArmory 0.1.4, deployed 2026-10-06 23:15).
- 2026-10-08 05:45 HOTFIX DEPLOYED SkyyArmory 0.1.10 (the world would not start: one-entry Parallel in the 7 spellbook Levitate interactions, since 0.1.6; TEST 49). Bag art answers recorded (docs/answered/bags.md), art redo agent ran on tools/art/make_bags.py.
- 2026-10-08 DEPLOYED 06:42 Sacks 0.7.14 + Accessories 0.5.8 bag art (TEST 49), 06:43 Armory 0.1.11 Bo no orb (TEST 50). RUNNING (deploy each when READY, game closed): 06:52 DEPLOYED Menu 0.3.10 Stats page (TEST 51). 07:12 DEPLOYED Essentials 0.1.9 chat mirror + SkyyTownProbe 0.1 (TEST 52). 09:28 DEPLOYED SkyyGear 0.2.10 signature charge kept on swap (TEST 58). 09:55 DEPLOYED Armory 0.1.14 wand ricochet signature (TEST 59); 10:27 Skills 0.4.24 Wood / Rotten / Tribal wand signature (TEST 60). 09:11 DEPLOYED Skills 0.4.23 + Armory 0.1.13 (TEST 57: roll on sprint press, no cooldown; back rolls impossible - no client signal; roll warnings + staff handover label + Shadow Step charge fixed). Asked Skyy: signature ideas for Bo / fists / kunai / spellbooks. 07:29 DEPLOYED Profiles 0.1.7 (TEST 54) (big SWITCH confirms + Health per profile). ASKED Skyy: roll key (sprint tap -> rebind Sprint to Mouse 5 in Controls [recommended] vs roll on Ability 3). 07:51 DEPLOYED SkyyHud 0.3.17 icon (TEST 55). 08:00 DEPLOYED Monk moves Armory 0.1.12 + Skills 0.4.22 (TEST 56), SkyyMonkProbe retired. Page warning suspect for the next SkyySacks round: profileNotice updates a page across the profile-switch world move. 07:28 DEPLOYED SkyyKeyProbe 0.1 (TEST 53; remove after Skyy's test). ABILITY KEYS LOCKED (classes.md 2026-10-08): 4 abilities, 2 primary on Ability 2 / 3, 2 alt on crouch + Ability 2 / 3; follow-ups in OPEN-QUESTIONS. ART agent (remote): DONE art/pebble + art/accessory-bag-icon; NEXT class ability icons. TODO main: wire the menu icon (SkyyMenu tile + Workbench tab), ACC_GEMS -> Option B in make_bags.py (next Accessories / Menu round). After EVERY play session: scan server + client logs, then recycle old logs. Zone 1 town: plan research/Zone-1-Town-Build-Plan.md (answers in docs/answered/world.md); after the probe test -> P0 ultracode (SkyyTowns 0.1 + SkyyWorldGen 0.2).
- DEPLOYED 19:21: SkyyReelProbe 0.1 (TEST-CHECKLIST 42; REMOVE from SET after Skyy's test, before SkyyFishing).
- DEPLOYED 2026-10-07: 18:54 Accessories 0.5.7 icons + Armory 0.1.5 staffs (TEST 41); 19:21 SkyyReelProbe 0.1 (TEST 42; remove
  after Skyy's test, before SkyyFishing); 20:20 Armory 0.1.6 spellbooks + kunai, Classes 0.1.13, Gear 0.2.8 (TEST 43); 21:41 Armory
  0.1.7 Monk bo / wraps / gauntlets + right-click block + NO void protection, Gear 0.2.9 (TEST 44).
- OVERNIGHT 2026-10-07 (Skyy asleep: "work through everything you can do on the mudpack. and ill answer all the questions on everything
  else tomorrow. try to get the new updated class skill trees out tonight if you can."): DONE 22:49 Shadow Step (Armory 0.1.8,
  TEST 45); class tree spec refreshed + research/cloud/Class-Tree-Build-Map.md; bag art (models-local/art/bags, Qs in OPEN-QUESTIONS bags);
  cloud session started (OUTBOX test pending). DONE 22:51 Monk + Assassin playable (Classes 0.1.14, Skills 0.4.21, Profiles
  0.1.6, Menu 0.3.9; TEST 46). DONE 00:34 class PATH TREES (Trees 0.3.3 + Armory 0.1.9 reader; TEST 47). DONE 01:09 SkyyMonkProbe 0.1 (TEST 48; PR #11 still OPEN - close it with a note: the local build 69d7c80 replaces it; gh CLI not installed here). NOTHING
  RUNNING locally. Probes to REMOVE after Skyy tests: SkyyReelProbe (TEST 42), SkyyMonkProbe (TEST 48), SkyyGatherProbe + B. Cloud: all 10 tasks done (OUTBOX), refilled with 3; told it the tree
  files are free. OPEN-QUESTIONS has tonight's questions (bags, class trees, Monk skill name).
  deploy each READY round (auto-deploy), queue every question for Skyy in OPEN-QUESTIONS. cloud-link mod: ~/.claude/dev-mods/.../cloud-link.
LATER round: dagger Shadow Step (research/Shadow-Step-Spec.md; no void protection). Cloud session: `CLOUD-RESUME.md` (art redos: helmets v3, mining v3 half plate, Enchanted icons v2, Monk emblem,
  Stamina icon; fishing junk; reference pictures are local in `research/refs/`, described in docs/answered/gear.md).

## Next, in order
1. OPEN-QUESTIONS gear: Onyxium crossbow recipe, leap on the 6 developer bows. (Done 2026-10-06 night: SkyyArmory 0.1.4 + SkyyGear 0.2.7.)
   Small: test_skyygear_0.2.7.py AH0 opens SkyyArmory-0.1.3.jar with no fallback - give it the build's fallback in the next SkyyGear.
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
