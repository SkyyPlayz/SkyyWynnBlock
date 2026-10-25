# SkyWynn - RESUME HERE (updated 2026-10-24; archi1 re-launched - see STATE)

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions = `HANDOFF.md` section 1 = `tools/deploy_set.py` SET.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.
Older RESUME detail (10-18 .. 10-22): git history of this file.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly ~35 % on 10-23, resets 10-27 09:00). World **NewBetaTest**.
2. Skyy's standing order (10-22): "work through your whole list." - take defaults; ask real design choices as popups (AskUserQuestion).
3. Rounds: Workflow `skywynn-round` (args tag / mods / task / quotes = Skyy's OWN words / others / recheck). Deploy = skill `skywynn-deploy`
   (backup -> `smoke_test.py --allow-pack-api` -> `deploy_set.py --yes` -> `record_deploy.py` -> commit -> `tidy_local.py --yes`).
4. After Skyy plays: skill `skywynn-logs`. Skyy shares a mod: skill `skywynn-mod-check`. Art: skill `skywynn-art`.

## STATE (2026-10-23 21:10 - Skyy is resetting the session)
- LIVE: everything up to TEST-CHECKLIST 248. Today's deploys (236-248): dragon fighting / riding / eggs, pet tooltips + portraits, Gear
  0.3.41-0.3.44 (Quirk's tools, Ability 1 tooltips, tier tag on top, real set names, green / red requirements, full-set button), Armory
  0.1.44-0.1.46 (weapon signatures sig1 / sig2 / sig4), CLASS TREE REBUILD (Trees 0.6.1 + Classes 0.1.47 + Skills 0.4.64 + Rebirth 0.5.2:
  Combat folded into Weaponcraft, OR pick, modifiers unlock in the tree - Skyy "i love the chages to the tree!"), node icons for every tree,
  zoom keep, Motherlode jackpot, row gates, harvest swing, WorldGen 0.7.10 (/zone <n> reset + undo; StructureV2 freeze fixed), Zones 0.2.2
  (shard ores regrow), Exploration 0.3.4, Menu 0.3.47 (no hotbar item; unspent points in Right now), Pets 0.4.16, Shards 0.4.7 (tier up on the
  totem page, centre pad), Wardrobe 0.2.11 (Requip pet portraits), joszza DungeonBosses + River Bridges.
- NOT FINISHED at the reset: workflow archi1 = starter archipelago R1 + R2 (SkyyShards 0.4.8 + SkyyIslands 0.5.25) per
  research/Starter-Archipelago-Spec.md v2 (layout APPROVED, research/starter-archipelago-layout.png) + every Skyy answer in
  docs/answered/world.md 2026-10-23 (STARTER ISLAND REDESIGN ... ARCHIPELAGO LAYOUT APPROVED). It stopped in the BUILD step: untracked
  tools/shards_0_4_8_patch.py, tools/islands_0_5_25_patch.py, SkyyShards/*_0.4.8.py, SkyyIslands/*_0.5.25.py and the uncommitted
  tools/balance_model.py edit (its --p11 cost check) are its unreviewed drafts. RE-LAUNCHED 2026-10-24 (run wf_872e02c7-228, builder audits the drafts). If that run is gone: re-launch Workflow skywynn-round tag archi1 with
  the same task (mods / quotes in docs/log 10-23 20:00 line) - tell the builder these drafts exist (reuse or redo), recheck true.
- Players' world: ZoneViewControl duplicate fixed (Skyy removed 1.1.1). Subcaverna has 0.5.2 + 0.5.3 in Mods (fine while it is off; Skyy
  may delete 0.5.2). NoCube Orchard benches broken on 0.7.4 (theirs; Skyy: "leave it alone and wait").

## RUNNING (2026-10-25 10:00) - building: ut28 (Gear 0.3.47 UT first 28), drag5 (Pets 0.4.19 secret dragons), ranch6 (Skills 0.4.66
  Ranching XP), zones031 (Zones 0.3.1), One batch, one smoke.
  USAGE: weekly 92% at 10:40 on 10-25 (resets 10-27 09:00) - Skyy: "stop at 98% usage, and update the files/repo". Launch NOTHING new;
  at 98% stop running rounds (their reports go to tools/dev/scratch/resume/) and finish the hand-off.
  LIVE 09:34 (TEST 254, backup deploy-20261025-0934): Shards 0.4.11 Combat Shard zone islands.
  LIVE 22:18 (TEST 253, backup deploy-20261024-2218): Trees 0.6.4 + Classes 0.1.50 (per-path capstones + Shadow Mark).
  LIVE 21:38 (TEST 252, backup deploy-20261024-2138): Shards 0.4.10 hotfix, Hud 0.3.36, Islands 0.5.26. tidy_local ran 2026-10-25 09:40 (scratch links removed first).
- LIVE 16:17 (TEST 251, backup deploy-20261024-1617): Shards 0.4.9 (Upgrade Map + re-balance), Trees 0.6.3 + Classes 0.1.49, Pets 0.4.18, Quests 0.4.4.
- LIVE 11:58 (TEST 249): Sacks 0.8.29, Collections 0.2.33, Shards 0.4.8 + Islands 0.5.25, Armory 0.1.47, Gear 0.3.45 + Mobs 0.1.19 + Classes
  0.1.48, Trees 0.6.2 + Pets 0.4.17, Wardrobe 0.2.12, Zones 0.3.0 + Skills 0.4.65.
- LIVE 13:06 (TEST 250, backup deploy-20261024-1306): WorldGen 0.7.11 (+ StructureV2 flying_islands on), Sacks 0.8.30, Gear 0.3.46, Fishing 0.2.0.
- Smoke: ONCE per batch by the main session; stop scratch test servers that block a deploy (Skyy 2026-10-24). tidy_local ran 13:10. DANGER: crosscheck scratch
  folders (xc-*) can hold JUNCTIONS into the real repo (tools/, art/) - unlink with `cmd /c rmdir` only, never a recursive delete;
  tools/dev/scratch/xc-sound1 still has 61 links (left alone).
QUEUE: AUGMENTS - research/Augments-Spec.md written, Skyy answered 8 questions 10-25 (docs/answered/gear.md, last 6 lines): REVISE the spec to
  them (no removal / overwrite + fuse, elemental 10 tiers, zone-tier drops + zone primary elements Z1 Earth, Poison = weapon modifier, Attack Speed
  live, gathering slots by rarity) + survey more elemental mob mods, then build A1 effects engine + A2 sockets. Powders dropped; Gear lane ( UT-28 incl. Ancient Bronze daggers +
research/Vanilla-Gear-Audit.md, beta #12 / #17, Fishing B); Secret dragons (Pets); R6 Ranching XP; Zones 0.3.1; sig3 / sig5 after shield1; RARITY + TOOLTIP PASS all mods; price tooltips; BetterMap.

## WAITING ON SKYY
- `/skyprobe tour` (TEST-CHECKLIST 231, SkyyUiProbe 0.8, 15 cases, ~5 min) -> unlocks UI rounds R1b-R5; afterwards RETIRE SkyyUiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png (8 Home tiles) + research/cloud/page-emblems-art/sheet.png (4 page emblems).
- Tell joszza: River Bridges' guard role needs MajorDungeons' Mb_Bandit group (fails to load without it).
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons (OPEN-QUESTIONS), TEST-CHECKLIST 215-236.

## NEXT (in order)
1. Starter archipelago R1 + R2 (archi1, NOT FINISHED above) -> deploy.
2. Starter archipelago: R3 radial shard upgrade map (Shards 0.4.9), R4 quests (Quests 0.4.4), R5 combat zone islands, R6 Ranching XP.
3. Weaponcraft numbers x1.5 (Gear / Mobs / Pets / Accessories balance round); Beastmastery tree hatch-speed + hatchery-slot nodes (Trees + Pets) + add
   Beastmastery to Trees' tree:<uuid> bridge string so Menu 'Right now' shows its unspent points.
4. sig3 / sig5: UT quirks + Mythic signatures (research/UT-Mythic-Signatures.md; Mythics REPLACE vanilla moves); Spellblade great shield
   (bash attack + 30-block steerable charge); long-term every vanilla weapon move class-fitted.
5. Price tooltips R0 probe -> R1 Auctions -> R2 Bazaar (research/Price-Tooltips-Spec.md). BetterMap: runtime listing for new shard worlds.
6. Older list: UI R1b-R5 after /skyprobe tour; Powders P1 / Fishing stage 2 / UT-28 / SkyyZones 0.3 / Secret dragons build specs in
   research/cloud/; GlymeraSigns ask (research/cloud/GlymeraSigns-Ask.md); joszza River Bridges guard bug; NoCube Orchard wait.

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
