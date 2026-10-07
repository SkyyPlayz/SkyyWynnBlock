# SkyWynn - RESUME HERE (updated 2026-10-05)

Read this first, then only what the task needs. Map of every file + search tips: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions + build
rules: `HANDOFF.md`. Still-open questions: `OPEN-QUESTIONS.md`. What Skyy tests next: `TEST-CHECKLIST.md`.

## START HERE - the next session (local, in `SkyWynn PROJECT`; it reads CLAUDE.md -> this file -> INDEX.md)
1. `git pull --rebase --autostash`. Check weekly usage (ccd get_usage) - it resets TUESDAYS 15:00 UTC (next: Tue 2026-10-06 15:00 UTC = 9:00
   Skyy's time). Lean round ~0.3-0.5% weekly, full round ~0.7-1%, ultracode ~3%+.
2. Quick first: TRIM PROJECT-RULES.md (every session + agent loads it): for each line ask "would removing it cause a mistake?" - cut
   vague / duplicate / history lines (Skyy's quotes stay in docs/answered/), keep every real rule; show the keep / cut list in the log.
3. FIRST BUILD AFTER THE RESET (Skyy 2026-10-05): sell from BAGS at the Bazaar (SkyySacks take bridge + SkyyBazaar sell buttons / Sell
   Inventory; full round, item + coin safety) + Tree Sap default 12 + Hytale stack sizes on the BUY / SELL stack buttons (ore 25,
   most 100 - the item's real max stack); then the Lantern recipes behind the Tree Sap collection tiers
   (SkyyCollections + SkyyAccessories). All in docs/answered/economy.md 2026-10-05.
4. Skyy's test results first (TEST-CHECKLIST.md items 17-26 = everything deployed 2026-10-05); fix what they report.
5. Then "Next, in order" below: item 5 (traversal build - spec + Skyy's answers ready), item 8 (mob curve, ultracode - all answers in),
   item 9 minimap, item 10 Stats page, SkyyGear weapon speed tiers.
6. Round recipe: one Opus builder (task names the files) -> one Sonnet review -> fix -> `python tools/ci/crosscheck.py --jar <new> --baseline`
   -> pin -> commit -> `python tools/backup_deploy.py` -> `python tools/deploy_set.py --yes` -> docs (below) -> `python tools/tidy_local.py --yes`.
7. Obsidian vault = this folder (`docs/OBSIDIAN.md`). Cloud sessions: CLOUD-RESUME.md.

## Now (2026-10-05 evening)
- LIVE: the 26-mod SET (HANDOFF section 1 = `tools/deploy_set.py`). Deployed 2026-10-05 (newest backup `backups\deploy-20261005-1745`;
  every backup listed in `backups/README.md`): Cooking 0.1.5 + 0.1.6, Accessories 0.5.5, Exploration 0.2.3, Menu 0.3.7 + 0.3.8,
  Collections 0.2.6, Gear 0.2.3, Bazaar 0.1.4, Party 0.1.7 + Essentials 0.1.8, Skills 0.4.16, Trees 0.3.2. NONE tested by Skyy yet.
- 2026-10-06 DEPLOYED (untested): Collections 0.2.7 + Accessories 0.5.6 (Lanterns behind Tree Sap, TEST-CHECKLIST 28), Bazaar 0.1.5 + Sacks
  0.7.13 (sell from bags, 29), Classes 0.1.12 + Armory 0.1.1 + Gear 0.2.4 (staff / wand traversals, 30). START HERE items 3 + 5 are DONE.
- ALSO DEPLOYED 2026-10-06: SkyyGatherProbe 0.1 + B (op-only probe pack, TEST-CHECKLIST 31 - REMOVE both from SET after Skyy's session),
  SkyyArmory 0.1.2 crossbow Grapple Bolt + Stamina cap 5 (32).
- ALL DEPLOYED 2026-10-06 (untested; TEST-CHECKLIST 28-35): Lanterns / sell from bags / staff + wand traversals / gather probe pack (REMOVE
  after Skyy's session) / Grapple Bolt / mob curve / Dodge Roll / Skills 0.4.19 + Hud 0.3.14 minimap (BetterMap) + Gear 0.2.6 weapon speed.
- DEPLOYED 19:15: SkyyHud 0.3.15 (Seasons widget mover) + SkyyBank 0.1.7 (daily interest), TEST-CHECKLIST 36; SkyySkills 0.4.20 sprint-tap roll 19:30 (37).
- RUNNING (~19:00 -0600, Skyy away): SkyyBank 0.1.7 daily interest (wfscripts/bank017.js),
  SkyyHud 0.3.16 minimap fixes (wfscripts/hud0316.js: island blank, arrow in blocks, overlap), SkyyArmory 0.1.3 (wfscripts/armory013.js:
  Wynncraft bow traversal + apex hang for bow + wand, ALL traversal particles fade (grapple dots, wand orbs, staff trail), hop 30,
  Copper + Onyxium crossbows). NEXT Armory build: blink.distance 16 + blink.floorCheck 0 (Skyy set both live).
- Art: Skyy reviewed everything (docs/answered/gear.md 2026-10-06); cloud has the redo list; Skyy's reference pictures are in research/refs/.
- SPECS DONE + ANSWERED today: research/Gathering-Progression-Spec.md (all 11 questions answered - docs/answered/bags.md 2026-10-06: hard ore
  gates, Mithril hidden until 0.7, ratio 100, Enchanted premium + Fortune on all tiers); research/Grapple-Bolt-Spec.md (Dodge Roll part waits
  for a free SkyySkills slot = 0.4.18 after the mob curve).
- Specs ready to build: `research/Magic-Traversal-Spec.md` (+ its section 8 = Skyy's answers), `research/Mob-Curve-Spec.md` (all defaults
  accepted 2026-10-05). Helpers new this session: `tools/ci/crosscheck.py`, `tools/tidy_local.py`.
- Rules for docs: answers go word for word into `docs/answered/<topic>.md` and leave OPEN-QUESTIONS.md (`tools/qa_append.py ... --close`);
  log + HANDOFF + this file the moment anything is done (PROJECT-RULES 5); keep files where INDEX.md says ("Keep it tidy").

## Next, in order (Skyy's queue 2026-10-04; full detail of each item: `docs/answered/<topic>.md` + the old RESUME)
1. DONE 2026-10-05: SkyyGear 0.2.3 (craft Smithing XP + F1 + F7) - waiting for Skyy's test. Next Gear: tool levels = 0.2.4, the loot round = 0.2.5.
2. DONE 2026-10-05: SkyySkills 0.4.16 Mining curve + leaderboards - waiting for Skyy's test. (Menu 0.3.8 Mods list + Trees 0.3.2 class trees ON also deployed.)
3. DONE 2026-10-05: SkyyBazaar 0.1.4 progression prices (incl. seeds + saplings by tier) - waiting for Skyy's test.
4. DONE 2026-10-05: SkyyCooking 0.1.5 + 0.1.6 (XP by difficulty, Flour 140) - waiting for Skyy's test.
5. SkyyArmory 0.1.1 + SkyyClasses 0.1.12 + SkyyGear 0.2.4 - staff blink + light trail, wand hop + burst + heal orb, quick-shot ranges /
   pierce, no staff Stamina. SPEC DONE 2026-10-05: research/Magic-Traversal-Spec.md + Skyy's answers (its section 8: free no-move blink,
   traversals cost Mana 2 : Stamina 1, heal orb heals everyone / party more, pierce uncapped).
   Full round after the reset (deploy order Classes -> Armory -> Gear). NOTE: Gear 0.2.4 was 'tool levels' - renumber (tool levels 0.2.5, loot 0.2.6).
6. DONE 2026-10-05: SkyyParty 0.1.7 + SkyyEssentials 0.1.8 TPA buttons - waiting for Skyy's 2-player test.
7. DONE 2026-10-05: SkyyAccessories 0.5.5 Lantern edges, SkyyExploration 0.2.3 page guard, SkyyMenu 0.3.7 text. LEFT: a page guard for the
   ~18 other mods' pages (list in docs/log/2026-10.md 2026-10-05; they rely on SkyyMenu 0.3.6's join guard - only if Skyy sees a stuck page).
8. MOB CURVE build (Skyy accepted every spec default 2026-10-05 - docs/answered/mobs.md): SkyyMobs 0.1.4 + SkyyGear (Reforge level-up, cap +6;
   armor-box hide = YES) + SkyySkills next - ultracode round, deploy + roll back together.
9. SkyyHud minimap widget (BetterMap joins the pack, stats off; downscale the engine's 96 px tiles on its own worker thread).
10. Stats page (Your Profile -> SkyBlock-style stats; spec = cloud task -> `research/cloud/Stats-Page-Spec.md`), multi-mod build.
- NEW (Skyy 2026-10-05): ARMOR TYPES (soft) - HEAVY = Warrior / Berserker (heavy leather tier 1, then vanilla metal sets), LIGHT (leather) = Archer / Assassin / Monk, Cloth = Mage / Priest
  (tier 1 Crude Robe = Fibre + green crystal, then vanilla tunics Wool -> Cindercloth);
  Light armor = vanilla leather tier 1, then OUR metal tiers (black leather + metal accents, Iron+ echo the vanilla metal style) -
  ART PROOF (tools/skyyart.py preview sheet for Skyy) before the build; stats: Heavy slower +Def +HP
  (+crit dmg), Light a bit faster (+attack speed, +crit chance), Cloth fastest +HP +Mana least Def (+Mana regen higher tiers); trade-offs for
  anyone, the bracketed bonus only for your class's type; each family covers Lv 1-49 - rides the mob-curve round (docs/answered/gear.md).
- NEW (Skyy 2026-10-06): FISHING = our own mod (bench, hook / line / sinker / rod / reel, click-bar minigame, length + weight, collections,
  treasure; ideas from Angler's Almanac + HyFishing) - cloud spec draft first; FOOD = all vanilla foods + faster eating / hits don't cancel;
  PACK + HyFishing, Dynamic Seasons, NoCube's Orchard (DEPLOYED 2026-10-06 07:03, backup deploy-20261006-0703;
  TEST-CHECKLIST 27). Advanced Farming NOT added - its tools go into ours. POTIONS focused + flat by grade, FOODS mixed by ingredient family.
- NEW (Skyy 2026-10-06): LOOT - drop-only vanilla gear ranked into the unidentified pool, item decided AT IDENTIFY, a bit more mob
  drops, Wynncraft vanishing / respawning surface loot chests (never player chests). Cloud revises the loot spec; local lists the gear.
- NEW BIG DIRECTION (Skyy 2026-10-05): GATHERING PROGRESSION LADDER like SkyBlock - tier the Farming / Mining / Foraging materials (group
  trees, few tiers per zone), collection levels unlock the recipes for the next tier's gear + other progress, compressed 'Enchanted'
  materials. SPEC FIRST (ultracode spec round after the reset), builds on research/Collections-Spec.md; docs/answered/bags.md.
  Foraging armor, tool levels, Lantern-behind-Sap and armor types all hang off it.
- NEW (Skyy 2026-10-05): FORAGING ARMOR (gathering set) - tier 1 vanilla Wood armor, then the Farmer's Workbench wood ladder Softwood ->
  Goldenwood (7 tiers, designs echo Copper -> Onyxium); Foraging Fortune + chopping speed (+ Foraging XP), TREE FELLER on higher tiers
  (reuse SkyyTrees' Tree Feller); axes get Tree Feller too. Mining / Farming armor later.
- NEW (Skyy 2026-10-05): TOOL LEVELS must DO something - level raises speed + Mining / Foraging / Farming Fortune; axes, pickaxes,
  farming tools get rarities, rolls, reforges; new SICKLE RANGE modifier (research/Tool-Levels-Spec.md top note; docs/answered/gear.md).
- NEW (Skyy 2026-10-05): SkyyGear WEAPON SPEED tiers Slow / Medium / Fast / Super Fast, same DPS (per-hit damage scales) - next SkyyGear pass (docs/answered/gear.md).
- Also queued: the CLASS-ABILITY SPEC (proposes every class's A2 alternative + two improved A1 options for Skyy to pick, + the engine probe:
  glide / slow fall, air-jump timing, dragging mobs, ally lock-on, absorb shield, beams / tethers, invisibility); the Monk class; /island
  STARTER SHARDS (SkyyIslands); WORLDGEN STAGE 2 spec -> build; the Accessory Table (paused - ask Skyy); small follow-ups (Archery 15+ extra crossbow bolts + the late-game holstered reload -
  approved, later; leaderboards skip deleted profiles (Collections 0.2.6 DEPLOYED 2026-10-05; the Skills half rides the Mining-curve SkyySkills build), config kit KEEP 20 -> 10 DONE in tools/skyycfg.py 2026-10-05 (mods that omit KEEP get it on their next build; Collections, Accessories,
  Profiles, Cooking, Exploration, Guilds pass KEEP=20 explicitly - their next build sets KEEP=10, AGENT-BRIEF rule); Lantern row 'Hidden lights: most' 2-3 act like 1 (fix text or solver in the next SkyyAccessories build), vanilla UI restyle leftovers, retire SkyyUiProbe);
  SkyyEconomy 0.1 merge after Skyy tests the separate mods; Hytale 0.7 release-day fix list (`research/PreRelease-Compat-Audit-1002.md`).
  LAST (Skyy): "Skyy's Pocket Dimension" spec + release build + CurseForge kit.

## Every round (PROJECT-RULES sections 3 + 4)
Build (never `--deploy`) -> review (sonnet) -> fix -> cross-check the whole SET (`python tools/ci/crosscheck.py --jar <new jars> --baseline` = one JVM, -Xverify:all, access + Adventurer audit,
`python tools/ci/lint.py` 0 fails) -> pin in `tools/deploy_set.py` -> commit + push -> `python tools/backup_deploy.py` ->
`python tools/deploy_set.py --yes` with the game closed -> a test section at the end of `docs/tests/2026-10.md` + a "Test next" line in
TEST-CHECKLIST.md -> HANDOFF versions table + a log line in `docs/log/2026-10.md` -> update this file -> `python tools/tidy_local.py --yes`.

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
