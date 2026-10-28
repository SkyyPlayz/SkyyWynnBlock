# SkyWynn - RESUME HERE (updated 2026-10-27 night; TEST 261 live)

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

## LIVE 2026-10-28 05:49 (TEST 264, backup deploy-20261028-0549): Gear 0.3.50 watering can progression, Mobs 0.1.21 more spawns. Also live since
  22:55 (TEST 263): Skills 0.4.68 Farming low-tier falloff, Zones 0.3.3 zone-world chests. LIVE 07:14 (TEST 265): Mobs 0.1.22 Armored / Veteran
  (full vanilla role copies; first try failed smoke - Variant Modify only takes the parent's own Parameters). ASK Skyy: Ancient Steel armour now
  drops from Zone 4 wild Burnt Alchemists - remove? [default: remove, next Mobs round]. Nothing running.
## LIVE 2026-10-27 22:50 (TEST 262, backup deploy-20261027-2242): hotfixes from Skyy's test - Shards 0.4.15 (javassist continue-in-finally lock leak
  = every click "busy"; replant every tilled cell), Gear 0.3.49 (tier-up 0-slot backpack), Sacks 0.8.33 (pocket ALL), WorldGen 0.7.12 (lead sheets).
  BUILT, in review: Skills 0.4.68 (Farming low-tier XP falloff, Skyy's pick), Zones 0.3.3 (chests open in the zone world). RUNNING: workflow can1
  (Gear 0.3.50 watering can progression, research/Watering-Can-Progression-Spec.md + Skyy's 4 answers in docs/answered/gear.md), workflow spawn1
  (Mobs 0.1.21 spawn rates, research/Mob-Variety-Spec.md); NEXT after spawn1: variety1 = Mobs 0.1.22 Armored / Veteran (answers in docs/answered/mobs.md).
  Lint idea: no continue / break inside a lock try in any mod (javassist skips finally).
## LIVE 2026-10-27 21:09 (TEST 261, backup deploy-20261027-2109): Shards 0.4.14 (lock refactor, Collect once), Sacks 0.8.32 (Greater Essence,
  sacks:fn:takeOpen, own ticker thread), Armory 0.1.48 (9 Untiered), Mobs 0.1.20 + Fishing 0.2.1 + Collections 0.2.35 (secret egg sources),
  Trees 0.6.6 (Creative sowing free), Accessories 0.5.33 (Plates x1.5, Skyy "Raise cap to 13.75%"). Earlier today: TEST 259 + 260.
  NEXT: the QUEUE below.
## RUNNING (2026-10-26) - LIVE 21:15 (TEST 258): Gear 0.3.48. LIVE 21:04 (TEST 257): Sacks 0.8.31, Hud 0.3.37 + Pets 0.4.20, Trees 0.6.5, Zones 0.3.2.
  HOLD: Shards 0.4.12 pinned but DO NOT DEPLOY alone (Shards lock deadlock froze the island 02:38; 0.4.12 adds
  sacks calls under ShStore.LOCK) - ship the fixed 0.4.13 (totemui: deadlock fix FIRST + place totems anywhere + redesign). Sacks 0.8.31 pinned. Building: totemui (Shards 0.4.13 totem page + bench
  redesign, lean), compfix (Sacks 0.8.31 auto-compact refresh on unlock + every 180 s, Essence of Life -> Life Essence Concentrated pair),
  ench1 (Collections 0.2.34 + Bazaar 0.2.2 Enchanted in Pocket crafting + reverse), petwid (Hud 0.3.37 pet widget), aoeseed (Trees 0.6.5).
  LIVE 11:46 (TEST 256, backup deploy-20261025-1146): Gear 0.3.47 first 28 UT (19 live, 9 wait for Armory).
  LIVE 11:31 (TEST 255, backup deploy-20261025-1131): Skills 0.4.66 Ranching XP, Pets 0.4.19 secret dragons, Zones 0.3.1.
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
QUEUE (2026-10-27 night): Shards adopts sacks:fn:takeOpen in payInvBags (Pocket part only; Sacks 0.8.32 live);
  SkyyTrees /tree page text for Accessory Plates still says +0.5 % (tools/trees_v3_data.py R062_TEXT wc15 block -> +0.75 %) + fold the wc15
  rows into trees_v3_effects EFFECTS; research/Combat-Into-Class-Spec.md still says the 10 % Combat Health budget;
  SHARED-EXECUTOR holder still unknown - Shards (own thread since 0.4.13) + Sacks (own ticker since 0.8.32, measured cheap) are clean;
  read the next play-session log for the SackBeat 'shared scheduler stalls' + 'tick max' lines, then check the other mods / pack jars;
  AUGMENTS build: research/Augments-Spec.md REVISED 10-27 (rounds P0 probe, A0 Attack Speed, A1 effects engine, A2 sockets + items deploy
  together; A3 drops + element mobs; defaults N1-N8 in its section 7 - fuse 2:1, Z2-Z5 Thunder / Water / Fire / Air); Slime Mobs! licence check;
  Gear lane (Vanilla-Gear-Audit, beta #12 / #17, Fishing B); sig3 / sig5; RARITY + TOOLTIP PASS all mods; price tooltips; BetterMap.
  Sacks question [default: leave it]: the Farmer's Workbench 100 Essence -> 1 Greater recipe can be paid by opening a Greater (net zero).
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
