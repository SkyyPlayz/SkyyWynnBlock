# SkyWynn - RESUME HERE (updated 2026-10-30; TEST 265 live, nothing running)

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
- Skyy 10-28: keep the wild Burnt Alchemist Ancient Steel drops. Nothing running, nothing built-but-unpinned.
- Starter archipelago R1-R6 all live (Shards 0.4.8-0.4.11, Islands 0.5.25-0.5.26, Quests 0.4.4, Skills 0.4.66). Old untracked drafts
  (tools/shards_0_4_8_patch.py, SkyyShards/*_0.4.8.py, ...) are leftovers - leave them / tidy later.
- Players' world: Subcaverna has 0.5.2 + 0.5.3 in Mods (fine while off). NoCube Orchard benches broken on 0.7.4 (theirs; Skyy: "leave it alone and wait").

## WAITING ON SKYY
- `/skyprobe tour` (TEST-CHECKLIST 231, SkyyUiProbe 0.8, 15 cases, ~5 min) -> unlocks UI rounds R1b-R5; afterwards RETIRE SkyyUiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png (8 Home tiles) + research/cloud/page-emblems-art/sheet.png (4 page emblems).
- Tell joszza: River Bridges' guard role needs MajorDungeons' Mb_Bandit group (fails to load without it).
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons (OPEN-QUESTIONS), TEST-CHECKLIST lines still open.
- Sacks question [default: leave it]: the Farmer's Workbench 100 Essence -> 1 Greater recipe can be paid by opening a Greater (net zero).

## NEXT (in order)
1. Small fixes: Shards adopts sacks:fn:takeOpen in payInvBags (Pocket part only); SkyyTrees /tree text for Accessory Plates +0.5 % -> +0.75 %
   (tools/trees_v3_data.py R062_TEXT wc15 block) + fold the wc15 rows into trees_v3_effects EFFECTS; research/Combat-Into-Class-Spec.md still
   says the 10 % Combat Health budget. Lint idea: no continue / break inside a lock try (javassist skips finally).
2. SHARED-EXECUTOR holder still unknown (Shards + Sacks are clean): read the next play-session log for SackBeat 'shared scheduler stalls' +
   'tick max', then check the other mods / pack jars.
3. Weaponcraft numbers x1.5 (Gear / Mobs / Pets / Accessories balance round); Beastmastery tree hatch-speed + hatchery-slot nodes (Trees +
   Pets) + add Beastmastery to Trees' tree:<uuid> bridge string so Menu 'Right now' shows its unspent points.
4. AUGMENTS: research/Augments-Spec.md (REVISED 10-27): P0 probe, A0 Attack Speed, A1 effects engine, A2 sockets + items deploy together;
   A3 drops + element mobs; defaults N1-N8 in its section 7 (fuse 2:1, Z2-Z5 Thunder / Water / Fire / Air).
5. sig3 / sig5: UT quirks + Mythic signatures (research/UT-Mythic-Signatures.md; Mythics REPLACE vanilla moves); Spellblade great shield.
6. RARITY + TOOLTIP PASS all mods; price tooltips (research/Price-Tooltips-Spec.md: R0 probe -> Auctions -> Bazaar); BetterMap shard worlds.
7. Gear lane (Vanilla-Gear-Audit, beta #12 / #17, Fishing B); Slime Mobs! licence check.
8. Older: UI R1b-R5 after /skyprobe tour; Powders P1 / Fishing stage 2 / UT-28 / Secret dragons specs in research/cloud/; GlymeraSigns ask
   (research/cloud/GlymeraSigns-Ask.md).

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
