# SkyWynn - RESUME HERE (updated 2026-10-30; TEST 266 live, augments running)

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions = `HANDOFF.md` section 1 = `tools/deploy_set.py` SET.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.
Leftover local jobs (beta bugs): `LOCAL-RESUME.md`. Older RESUME detail: git history of this file.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage) before each round. World **NewBetaTest**.
2. Skyy's standing order (10-22): "work through your whole list." - take defaults; ask real design choices as popups (AskUserQuestion).
3. Rounds: Workflow `skywynn-round` (args tag / mods / task / quotes = Skyy's OWN words / others / recheck). Deploy = skill `skywynn-deploy`
   (backup -> `smoke_test.py --allow-pack-api` -> `deploy_set.py --yes` -> `record_deploy.py` -> commit -> `tidy_local.py --yes`).
4. After Skyy plays: skill `skywynn-logs`. Skyy shares a mod: skill `skywynn-mod-check`. Art: skill `skywynn-art`.

## NOW
- LIVE up to TEST 266 (2026-10-30 08:09, backup deploy-20261030-0809): Trees 0.6.7 (Plates text, wc15 EFFECTS fold), Shards 0.4.16 (costs open
  Pocket Enchanted), UiProbe 0.9 (price-tooltip probes P1-P5 - Skyy runs them, decides Bazaar R2), Auctions 0.1.16 (AH price index).
  Before: TEST 265 Mobs 0.1.22 Armored / Veteran; 264 Gear 0.3.50 watering can + Mobs 0.1.21; 263 Skills 0.4.68 + Zones 0.3.3. Full list: docs/log.
- Builders write in the worktree .claude/worktrees/resume-review-87c362 (a hook blocks the base checkout): commit / pin there, push to main,
  copy the new jars into the base checkout, deploy from the base checkout.
- Skyy 10-28: keep the wild Burnt Alchemist Ancient Steel drops. Running: see RUNNING.
- Starter archipelago R1-R6 all live (Shards 0.4.8-0.4.11, Islands 0.5.25-0.5.26, Quests 0.4.4, Skills 0.4.66). Old untracked drafts
  (tools/shards_0_4_8_patch.py, SkyyShards/*_0.4.8.py, ...) are leftovers - leave them / tidy later.
- Players' world: Subcaverna has 0.5.2 + 0.5.3 in Mods (fine while off). NoCube Orchard benches broken on 0.7.4 (theirs; Skyy: "leave it alone and wait").

## WAITING ON SKYY
- `/skyprobe tour` (TEST-CHECKLIST 231, SkyyUiProbe 0.8, 15 cases, ~5 min) -> unlocks UI rounds R1b-R5; afterwards RETIRE SkyyUiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png (8 Home tiles) + research/cloud/page-emblems-art/sheet.png (4 page emblems).
- Tell joszza: River Bridges' guard role needs MajorDungeons' Mb_Bandit group (fails to load without it).
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons (OPEN-QUESTIONS), TEST-CHECKLIST lines still open.
- Sacks question [default: leave it]: the Farmer's Workbench 100 Essence -> 1 Greater recipe can be paid by opening a Greater (net zero).

## RUNNING (2026-10-30)
- augments wf_7fbdb3aa-699: P0 -> A0 Gear 0.3.51 Attack Speed + A1 Classes 0.1.51 / Mobs 0.1.23 effects engine -> A2 Gear 0.3.52 + Sacks
  0.8.34 sockets; A0-A2 deploy together. If cut off: drafts in the worktree + tools/dev/scratch/aug*; re-launch skywynn-round per round.
- PINNED, not deployed (10-30): rarity pass Cooking 0.1.17, Fishing 0.2.2, Shards 0.4.17, Merchants 0.1.8, Bazaar 0.2.3, Armory 0.1.49,
  Collections 0.2.36, Wardrobe 0.2.13, Pets 0.4.21, Accessories 0.5.34 (looks only) - deploy in the same batch as augments A0-A2.

## NEXT (in order)
1. Pin augments A0-A2, then ONE smoke + deploy with the pinned rarity mods.
2. SHARED-EXECUTOR holder (Shards + Sacks clean): after Skyy plays, read SackBeat 'shared scheduler stalls' + 'tick max', then other mods.
3. Gear lane after A2 (Gear free): research/Vanilla-Gear-Audit.md section 8 LEFT (Ornate Bronze, Fishing B, UT-28 all live): Bronze weapon
   rung + recipes, Z2 Doomed / Z4 Saurian UT sets, Sword_Bronze_Ancient Z1 UT, Scythe_Void Berserker Mythic, Diving Crude out of combat bags,
   Trork / Kweebec set (Gear + Mobs drops); shields = own round. Then sig3 (Revolving Door, Weighted Vortex, armory:fn:sigfx, C+ charge
   rules, probes) -> sig5 (13 Mythic signatures; needs the sig3 probe PASS in game).
4. Augments A3 (Mobs drops + element mobs; PACK Slime Mobs! 1.1.4 - MIT, Water / Fire / Ice slimes, docs/log 10-30) + A4 (Menu charts).
5. Price tooltips R2 Bazaar 0.2.4 after Skyy runs P1-P5 (/uiprobe tip); R3 Gear if P3 passes. BetterMap shard-world listing.
6. RARITY + TOOLTIP PASS part 2: Gear, Classes, Mobs, Sacks, Menu (after augments frees them).
7. Older: UI R1b-R5 after /skyprobe tour; Dragon-Quest-Spec (research/cloud) needs Skyy's call; GlymeraSigns ask = Skyy sends it.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches.
- Rollback floors + go-together rules: comments in `tools/deploy_set.py` (newest first, above SET).
- HANDOFF section 2 UI rule: every bound click answers with exactly ONE page packet (else "Loading..." forever).
- balance_model.py flags --md / --econ / --gather / --power / --combat / --p9 REWRITE research/balance/targets.md (no flag = read only).
- tools/tier_tags.py is TT_VERSION 3; old pins' build scripts assert "2" - rebuild from the current pins only.
- Smoke: ONCE per batch by the main session. DANGER: crosscheck scratch folders (xc-*) can hold JUNCTIONS into the real repo - unlink with
  `cmd /c rmdir` only, never a recursive delete (tools/dev/scratch/xc-sound1 still has 61 links, left alone).
- Private art (Quirk) in `..\SkyWynn-PRIVATE-art\` is read at build time only - never in git. Untracked screenshots in SkyyIslands/ +
  SkyyWorldGen/ and TASK-crossbows-from-vanilla.md: leave alone - stage files by name, never `git add -A`.
- Screenshots of other servers stay in research/refs/ (git-ignored). Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`.

## On Skyy's PC (read-only except the deploy)
Project = this repo. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\` (`Server\HytaleServer.jar`,
`Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\Saves\NewBetaTest\` (mod data `mods\Skyy_Skyy<Mod>\`, server
logs `logs\`); client logs `...\UserData\Logs\`. Backups: `backups\` (git-ignored). Toolchain: Python 3.12 + jpype1 + jdk4py (no javac).
LOCAL ONLY, never in git: game files, UserData, backups, built jars (except `tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
