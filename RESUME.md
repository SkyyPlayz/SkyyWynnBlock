# SkyWynn - RESUME HERE (updated 2026-10-05)

Read this first, then only what the task needs. Map of every file + search tips: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions + build
rules: `HANDOFF.md`. Still-open questions: `OPEN-QUESTIONS.md`. What Skyy tests next: `TEST-CHECKLIST.md`.

## START HERE - the next local session (Skyy 2026-10-05: wait for the usage reset, then work the build list)
1. On Skyy's PC: `git pull` in `SkyWynn PROJECT` (picks up the 2026-10-05 docs layout, PRs #6 + #7).
2. Start Claude Code IN that folder - a LOCAL session (builds need `HytaleServer.jar`; the 2026-10-05 session was cloud-only by mistake).
   It reads CLAUDE.md -> this file -> INDEX.md.
3. Check the weekly usage first: it resets every MONDAY 15:00 UTC, so it reset on Mon 2026-10-05 15:00 UTC (older notes say
   "Mon 2026-10-06" - a date error, the 6th is a Tuesday). Then work "Next, in order" below - SkyyGear 0.2.3 first. Full rounds per
   PROJECT-RULES section 4; merge your own PRs once every check is green (section 6); log + update this file after each step.
4. Cloud sessions meanwhile: the no-game-files specs (build 5 traversal spec, Stats page spec, class-ability spec) - CLOUD-RESUME.md.
5. Obsidian: "Open folder as vault" -> `SkyWynn PROJECT` (settings ship in `.obsidian/`, how-to `docs/OBSIDIAN.md`).

## Now
- LIVE: the 26-mod SET in HANDOFF section 1 (= `tools/deploy_set.py`); last deploy SkyyAccessories 0.5.4 Lantern, 2026-10-04 00:46
  (backup `backups\deploy-20261004-0046`). NOTHING is running.
- USAGE: weekly 94% on the morning of 2026-10-05; the weekly reset is Mondays 15:00 UTC (= Mon 2026-10-05) - check usage before a big round.
- DOCS consolidated 2026-10-05 (PR #6, merged; `python tools/docs_check.py` proves no old line was lost); the old long RESUME is
  `docs/archive/RESUME-2026-10-05.md`. ALWAYS READY TO HAND OFF: log + HANDOFF + this file the moment something is done (PROJECT-RULES 5).
- OBSIDIAN: Skyy made an empty `Hytale Projects` vault folder first; the recommendation (step 5) opens the project folder itself so no
  path changes - confirm with Skyy which they use.
- Skyy's standing rules for docs: answered questions move OUT of OPEN-QUESTIONS.md into `docs/answered/<topic>.md` as soon as Skyy
  answers (`tools/qa_append.py ... --close`); class designs live one file per class in `research/classes/` (easy-read layout + HTML).

## Next, in order (Skyy's queue 2026-10-04; full detail of each item: `docs/answered/<topic>.md` + the old RESUME)
1. SkyyGear 0.2.3 - Smithing XP for crafting weapons + armor (steeper per tier, Crude / Wood much less; level-up coins = full round) + the
   0.2.2 check's F1 (stale tooltip after a tune edit). Then tool levels = 0.2.4, the loot round = 0.2.5.
2. SkyySkills 0.4.16 - Mining gets its own slower level list (numbers wait for Skyy's OK - OPEN-QUESTIONS).
3. SkyyBazaar 0.1.4 - progression prices (metals / woods / crops x2 per tier, eternal seeds x4, hides x2 flat; cloth + gems open) +
   the money-loop check. Full round.
4. SkyyCooking 0.1.5 - Cooking XP by craft difficulty (lean).
5. SkyyArmory 0.1.1 + SkyyClasses 0.1.12 - magic charged attacks become traversals (staff teleport + light trail; wand backward hop +
   exploding orb + heal orb; replaces the wand-burst plan), wand quick shot pierces, staff casts cost no Stamina. Spec first, full round.
6. SkyyParty 0.1.7 + SkyyEssentials 0.1.8 - TPA buttons on the Party page (bridge to /tpa + /tpaccept). Full round.
7. SkyyAccessories 0.5.5 - Lantern smooth edges ('Hidden light: highest' 64), lean; + the page guard for SkyyExploration (Overview stuck
   on 'Loading...' after world changes) and other pages; SkyyMenu help text Night Vision -> Lantern.
8. MOB CURVE build once Skyy answers its questions: SkyyMobs 0.1.4 + SkyyGear (Reforge level-up, cap +6; armor-box hide if Skyy says yes)
   + SkyySkills 0.4.17 - ultracode round, deploy + roll back together.
9. SkyyHud minimap widget (BetterMap joins the pack, stats off; downscale the engine's 96 px tiles on its own worker thread).
10. Stats page (Your Profile -> SkyBlock-style stats; spec = cloud task -> `research/cloud/Stats-Page-Spec.md`), multi-mod build.
- Also queued: the CLASS-ABILITY SPEC (proposes every class's A2 alternative + two improved A1 options for Skyy to pick, + the engine probe:
  glide / slow fall, air-jump timing, dragging mobs, ally lock-on, absorb shield, beams / tethers, invisibility); the Monk class; /island
  STARTER SHARDS (SkyyIslands); WORLDGEN STAGE 2 spec -> build; the Accessory Table (paused - ask Skyy); small follow-ups (Archery 15+ extra crossbow bolts + the late-game holstered reload -
  approved, later; skills / collections leaderboards skip deleted profiles, config kit KEEP 20 -> 10, vanilla UI restyle leftovers, retire SkyyUiProbe);
  SkyyEconomy 0.1 merge after Skyy tests the separate mods; Hytale 0.7 release-day fix list (`research/PreRelease-Compat-Audit-1002.md`).
  LAST (Skyy): "Skyy's Pocket Dimension" spec + release build + CurseForge kit.

## Every round (PROJECT-RULES sections 3 + 4)
Build (never `--deploy`) -> review (sonnet) -> fix -> cross-check the whole SET (one JVM, -Xverify:all, the Adventurer permission audit,
`python tools/ci/lint.py` 0 fails) -> pin in `tools/deploy_set.py` -> commit + push -> `python tools/backup_deploy.py` ->
`python tools/deploy_set.py --yes` with the game closed -> a test section at the end of `docs/tests/2026-10.md` + a "Test next" line in
TEST-CHECKLIST.md -> HANDOFF versions table + a log line in `docs/log/2026-10.md` -> update this file.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches - their
  successors are built from the edited scripts.
- Rollback floors: HANDOFF section 1 + the comments in `tools/deploy_set.py`. Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`.
- Housekeeping: a stray untracked `PROJECT\` folder in the repo root on Skyy's PC - never commit it; Skyy deletes it.

## On Skyy's PC (read-only except the deploy)
Project = this repo: `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\`. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\
release\package\game\latest\` (`Server\HytaleServer.jar`, `Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\
Saves\HUD mod\` (`config.json`, mod data `mods\Skyy_Skyy<Mod>\`, server logs `logs\`); client logs `...\UserData\Logs\`. Backups:
`backups\` (git-ignored). Claude's memory: `C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK\memory\`.
Release files for public mods: `Desktop\Hytale mods WORK\Your new mods\`. The other folders in `Hytale mods WORK` (`Hytale mods`,
`Your new mods`, `lynk to Hytale Game`, the new `Hytale Projects`) are Skyy's, not part of the build. Toolchain: Python 3.12 + jpype1 +
jdk4py (no javac). LOCAL ONLY, never in git: game files, UserData, backups, built jars (except
`tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
