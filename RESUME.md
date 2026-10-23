# SkyWynn - RESUME HERE (updated 2026-10-23 06:20 MDT; Skyy is resetting the context - a fresh session starts here)

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions = `HANDOFF.md` section 1 = `tools/deploy_set.py` SET.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.
Older RESUME detail (10-18 .. 10-22): git history of this file.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly ~35 % on 10-23, resets 10-27 09:00). World **NewBetaTest**.
2. Skyy's standing order (10-22): "work through your whole list." - take defaults; ask real design choices as popups (AskUserQuestion).
3. Rounds: Workflow `skywynn-round` (args tag / mods / task / quotes = Skyy's OWN words / others / recheck). Deploy = skill `skywynn-deploy`
   (backup -> `smoke_test.py --allow-pack-api` -> `deploy_set.py --yes` -> `record_deploy.py` -> commit -> `tidy_local.py --yes`).
4. After Skyy plays: skill `skywynn-logs`. Skyy shares a mod: skill `skywynn-mod-check`. Art: skill `skywynn-art`.

## STATE (2026-10-23 06:20)
- LIVE: everything up to TEST-CHECKLIST 239 (freeze fix WorldGen 0.7.9 + StructureV2 back on, zoom keep Trees / Rebirth 0.5.1,
  no menu item Menu 0.3.46, 10-23 10:54); 238 (dragon riding, pet tooltips, Quirk's tools, Skills leak fix, StructureV2 freeze STOPGAP
  worldgenEnabled false, 10-23 10:17) (joszza DungeonBosses + River Bridges in the pack, 10-23 08:31) (dragon fighting D1 + boss dragon eggs D6 = Pets 0.4.12 + Mobs 0.1.18, 10-23 06:18). Balance pass P1-P9 DONE (`python tools/balance_model.py --p9 --check` 35 / 0; caster Mana waits
  for Skyy's feel test; first run ~36 h accepted). Radial tree pages (SkyyTrees 0.5.0) + radial Nexus (SkyyRebirth 0.5.0). Left Alt opens the
  Menu (VERIFIED). UI R1a (ALT key cap, crouch x2 folds the quest tracker, Stats by source). Wynn elements (elem1). Elemental swords (Gear
  0.3.40). Dragon pet D0 (Pets 0.4.11). Pack mods StructureV2 (merchant off via `deploy_set tune_structurev2`) + Souls like Bosses ON.
  Game Review sheet = https://claude.ai/artifact/NgcvPphvjdrHdyrJrgCKfG (v16; source tools/dev/scratch/gamereview/ + assemble.py; keep its db capability).
- LIVE 10-23 12:40: Trees 0.5.2 (TEST 242). sig2 LIVE (Armory 0.1.45, TEST 243). RUNNING: workflow sig4 (Armory 0.1.46 [+ Gear 0.3.44]: base signature for every
  family) + workflow cls060
  (CLASS TREE REBUILD: R0 data + Trees 0.6.0 + Classes 0.1.47 + Skills 0.4.64 + Rebirth 0.5.2, deploy together).
  QUEUED Armory: Spellblade great shield = shield-bash attack + 30-block steerable charge (classes.md 10-23); then sig3 UT quirks + sig5
  Mythic signatures (research/UT-Mythic-Signatures.md; Mythics REPLACE vanilla moves; long-term every vanilla move class-fitted) ; Gear 0.3.42 (harvester swing source) LIVE 10-23 (TEST 240), its
  rows unlock when Trees 0.5.2 deploys; sig1 LIVE (Gear 0.3.43 + Armory 0.1.44, TEST 241). NEXT signature rounds: sig2 (4 locked
  signatures never built: Whirling Staff, Flurry, Kunai Fan, Page Storm), sig3 (UT quirks + a new signature for every Mythic), sig4 (base
  signature for every family with none) - research/Weapon-Signatures-Spec.md + gear.md 10-23. Weapon signatures spec done (research/Weapon-Signatures-Spec.md + Skyy's
  10-23 answers in gear.md) -> builds sig1-sig4 after Gear 0.3.42. Tell joszza: retry-loop message in docs/log 10-23 10:20. QUEUED after zoomfix: SkyyTrees 0.5.2
  Motherlode = 1 %/rank x3 jackpot, separate from Fortune + stale Plan text sweep + ROW GATES = total AND 3 points in the row
  above (grandfathered) + HARVEST SWING SPEED (Quick Scythe -> harvester swing; with Gear 0.3.42 harvester swing source)
  (docs/answered/skills.md 10-23); + Mining node icons once Skyy approves art/tree-node-icons/sheet.png. THEN the CLASS TREE REBUILD (research/Combat-Into-Class-Spec.md
  + Skyy's 10-23 answers in docs/answered/classes.md: Combat tree folded into each class, 3 branches A1+alts / A2+alt / Weaponcraft, per-branch
  gates + level floor, 1 point a level, modifiers unlock in the tree + level by use, one free respec) = R0 data + Trees 0.6.0 + Classes 0.1.47
  + Skills 0.4.64 + Rebirth 0.5.2 together (replaces 0.5.3 / 0.5.4). Node icons: all 11 skill trees + 8 classes drawn (art/tree-node-icons/).

## WAITING ON SKYY
- `/skyprobe tour` (TEST-CHECKLIST 231, SkyyUiProbe 0.8, 15 cases, ~5 min) -> unlocks UI rounds R1b-R5; afterwards RETIRE SkyyUiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png (8 Home tiles) + research/cloud/page-emblems-art/sheet.png (4 page emblems).
- Tell joszza: River Bridges' guard role needs MajorDungeons' Mb_Bandit group (fails to load without it).
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons (OPEN-QUESTIONS), TEST-CHECKLIST 215-236.

## NEXT (in order; each its own round)
1. Dragon D3 riding + flying with the saddle, secret dragons, dragon egg icon art.
2. After the probe tour (research/UI-Queue-Spec.md): R1b feed cards -> vanilla pickup feed; R2 zoom scroll fix (Trees / Rebirth); R3 SkyyQuests
   PARTICLE TRAIL (Skyy: "Particle trail instead") + objective HUD text + bottom dialogue bar; R4 player heads (PlayerSkin, runtime render,
   hair); R5 Menu picture tiles phase 1 (+ phase 2 = 31 hub tabs) + page emblems into SkyyTrees.
3. Next Gear round: ship Quirk's FIXED Multitool + Harvester (Titanium + Lumen; delivered 10-18 in
   ..\SkyWynn-PRIVATE-art\metal-art\Tools-PRIVATE\z5-held-tools-fixed\<Base>_<Tool>.*; Gear 0.3.26-0.3.40 still read the rejected originals
   in Tools-PRIVATE\<Base>\ -> G26 check fails -> 0.3.25 look); pad Farming armor textures to a multiple of 32 (client WARN x28, log 10-22 10:00); GearCfg.class not byte-reproducible (8 bytes); vanilla Weapon_Longsword_Flame flat-hit bug; `python tools/pack_drops.py --md`.
4. Later list: zone gathering spots (research/Zone-Gathering-Spec.md; crop islands 100 / 300 / 800), UT design (12 armor sets + 32 weapons),
   Powders spec, fishing rework, SkyyZones Z3 / Z4 (needs live probes), authors to ask (research/Structure-Mods-Survey.md).
5. Small TODOs: fold the 8 abil.costPerLevel.<Class> rows into one table row once the Classes kit has table rows; Skills DRY / CAST maps keyed
   by UUID never drop quit players (small leak); Sacks 0.8.25 off-hand refill stays parked (Skyy "skip for now").

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches.
- Rollback floors + go-together rules: comments in `tools/deploy_set.py` (newest first, above SET).
- HANDOFF section 2 UI rule: every bound click answers with exactly ONE page packet (else "Loading..." forever).
- balance_model.py flags --md / --econ / --gather / --power / --combat / --p9 REWRITE research/balance/targets.md (no flag = read only).
- tools/tier_tags.py is TT_VERSION 3; old pins' build scripts assert "2" - rebuild from the current pins only.
- Private art (Quirk) in `..\SkyWynn-PRIVATE-art\` is read at build time only - never in git. Untracked screenshots in SkyyIslands/ +
  SkyyWorldGen/ and TASK-crossbows-from-vanilla.md (done; Skyy may delete): leave alone - stage files by name, never `git add -A`.
- Screenshots of other servers stay in research/refs/ (git-ignored). Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`.

## On Skyy's PC (read-only except the deploy)
Project = this repo. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\` (`Server\HytaleServer.jar`,
`Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\Saves\NewBetaTest\` (mod data `mods\Skyy_Skyy<Mod>\`, server
logs `logs\`); client logs `...\UserData\Logs\`. Backups: `backups\` (git-ignored). Toolchain: Python 3.12 + jpype1 + jdk4py (no javac).
LOCAL ONLY, never in git: game files, UserData, backups, built jars (except `tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
