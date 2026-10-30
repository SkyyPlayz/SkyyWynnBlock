# SkyWynn - RESUME HERE (updated 2026-10-30; TEST 265 live, 4 workflows running)

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
- LIVE up to TEST 265 (2026-10-28 07:14, backup deploy-20261028-0714): Mobs 0.1.22 Armored / Veteran (full vanilla role copies - Variant
  Modify only takes the parent's own Parameters). Before it: TEST 264 Gear 0.3.50 watering can + Mobs 0.1.21 spawns; TEST 263 Skills 0.4.68
  Farming falloff + Zones 0.3.3; TEST 262 hotfixes (Shards 0.4.15, Gear 0.3.49, Sacks 0.8.33, WorldGen 0.7.12). Full list: docs/log.
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

## RUNNING (2026-10-30, launched by the main session; journals: docs/log 10-30 LAUNCHED line)
- trees067 (Trees 0.6.7 Plates text, wc15 EFFECTS fold, Beastmastery bridge check), shtake (Shards 0.4.16 Pocket Enchanted via takeOpen),
  price tooltips tip0 (UiProbe 0.9 R0 probes) + tip1 (Auctions 0.1.16 R1 sales index), augments chain (P0 -> A0 Gear 0.3.51 Attack Speed
  + A1 Classes 0.1.51 / Mobs 0.1.23 effects engine -> A2 Gear 0.3.52 + Sacks 0.8.34 sockets; A0-A2 deploy together).
- If a session restart cuts them off: reports / drafts are in tools/dev/scratch/<tag>*; re-launch skywynn-round with the same tag + task.

## NEXT (in order)
1. Pin + smoke + deploy what the running rounds finish (augments A0-A2 as one batch).
2. SHARED-EXECUTOR holder (Shards + Sacks clean): after Skyy plays, read SackBeat 'shared scheduler stalls' + 'tick max', then other mods.
3. Gear lane after A2 (Gear free): research/Vanilla-Gear-Audit.md section 8 (Skyy took all defaults 10-30: shields = own round, Trork set,
   Ornate Bronze legs, UT picks) + beta #12 / #17 + Fishing B. Then sig3 -> sig5 (research/UT-Mythic-Signatures.md section 8).
4. Augments A3 (Mobs drops + element mobs; PACK Slime Mobs! 1.1.4 - MIT, Water / Fire / Ice slimes, docs/log 10-30) + A4 (Menu charts).
5. Price tooltips R2 Bazaar 0.2.3 after Skyy runs P1-P5 (/uiprobe tip); R3 Gear if P3 passes. BetterMap shard-world listing.
6. RARITY + TOOLTIP PASS all mods (when no other round holds those mods). Lint rule: no continue / break inside a lock try.
7. Older: UI R1b-R5 after /skyprobe tour; Powders P1 / Fishing stage 2 / UT-28 / Secret dragons specs in research/cloud/; GlymeraSigns ask.

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
