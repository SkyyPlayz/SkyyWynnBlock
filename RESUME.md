# SkyWynn - RESUME HERE (updated 2026-10-14 ~06:30 MDT, all 4 relaunched rounds deployed)

Read this first, then only what the task needs. Map: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`. Skyy's tests:
`TEST-CHECKLIST.md`. Full history: `docs/log/2026-10.md` (2026-10-13 lines). Decisions word for word: `docs/answered/<topic>.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly resets TUE 2026-10-20 15:00 UTC; was 33% on 10-14).
2. The 4 rounds cut off overnight are all DEPLOYED (TEST-CHECKLIST 84-87). Next: Rebirth R3 (below).
3. Rounds: saved workflow `skywynn-round` (Skyy's OWN words in args.quotes); deploy only with the game closed: backup -> smoke
   (`--allow-pack-api`) -> deploy_set --yes -> record_deploy -> commit -> tidy_local. Scan logs + `tools/chat_digest.py` after play.
4. When Skyy says the game is UPDATING: stop every builder / smoke at once (memory skywynn-game-update-lock).

## Now (2026-10-14)
- **Game: Hytale 0.7.1** (Skyy reinstalled 10-13; UserData kept; full backup at `C:/Users/SkyLo/Desktop/Hytale-Backup-2026-10-13`).
  crosscheck READY, all 33 jars. Our tools read cached copies of the server jar + Assets.zip (`tools/serverjar.py`, ~4 GB / version).
- **Deployed 2026-10-13 (TEST-CHECKLIST 72-83, all untested):** Skills 0.4.33 Mana 3.3/s; Accessories 0.5.13 tab order; Pets 0.2.4 attacks
  pass through; Profiles 0.1.12 rename + Class Name + admin no cap; Sacks 0.8.2 /pdadmin rarity; Bank 0.1.10 + Menu 0.3.20 names; Quests 0.2
  (skip, optional tasks, class gear rewards, hub areas, co-op, feed only); Gear 0.3.0 lifelong tools; AUTO-PICKUP Sacks 0.8.3 + Mobs 0.1.7;
  chat -> feed (Skills 0.4.34, Classes 0.1.20, Collections 0.2.12; 116 -> 20 lines / 12 min); Hud 0.3.22 per-player routes; Menu 0.3.21
  Messages tab + Classes 0.1.21 ability route; BetterMap 1.3.9 / DynamicSeasons 7.0.2 / Perfect Parries 0.9.7 back ON; Gear 0.3.1 tool
  speed (Crude = T1, one tier up 2.5x hits, two up 10x, 3+ refused).
- **Deployed 2026-10-14 06:00 (TEST-CHECKLIST 84-86, untested):** Sacks 0.8.4 + Mobs 0.1.8 harvest to Void (pet kills idle until SkyyPets
  publishes pets:fn:ownerOf); Gear 0.3.2 /pickaxe etc. summon the EXACT tool (else exact copy); Trees 0.3.6 Vein Mine / Tree Feller perks.
  06:26 Skills 0.4.35 + NEW SkyyRebirth 0.1 (rebirth R1+R2, feature OFF; /rebirth Nexus page for admins; half Farming XP above tool
  tier). Keep Rebirth OFF until Skyy has seen the Nexus tooltip (then add "tooltip" to skyyui.PROBED). 9 new questions in
  OPEN-QUESTIONS (gear, bags, rebirth), defaults live.
- **Rebirth spec FINAL:** `research/cloud/Rebirth-Spec.md` (all 16 answers + ability levels kept with a soft cap, dust x2 per rebirth ...),
  build order R1-R10 (section 6). R1 + R2 = the interrupted rebirth12 round.
- Skyy to do: run `/aprobe` (Mage keys) and `/skyprobe kit` (Sky Window kit) in game; set the 4 quest hub
  spots (`/questadmin place set hub.mining | hub.foraging | hub.farming | hub.fishing`); test 72-83; Grok video notes from WED.
- Still broken on 0.7 (switched off): Saplings From Trees, TheArmory, HyFishing, Better Mob Expansion - recheck CurseForge; after
  2026-10-19 build our own / fork where the licence allows (docs/log 2026-10-13 pack check).

## Next, in order (after the 4 relaunched rounds; ~4-5 workflows at once)
0. LEAN: crops 2+ tiers above the held hoe / sickle cannot be harvested (Skyy 10-14 "No. Cant break 2 tiers above"; SkyyGear tier
   gate and/or SkyySkills; docs/answered/gear.md). Levels past 100 stay out of Overall / Mana / leaderboards (answered, no work).
1. Rebirth R3-R10 (research/cloud/Rebirth-Spec.md section 6; R1+R2 live) + level-up coins pay again each rebirth, a little less each time (docs/answered/economy.md 10-14), one round at a time; refresh the Class Balance chart when numbers change.
2. Gathering follow-ups (research/Gathering-Shards-Spec.md): hoe till area by tier, fishing pole via the hub quest, gathering armor that
   levels, Multitool unlock at rebirth 1, Sigils, the 6 shard islands + totems (phases 4-8).
3. Mage real keys + ability-level / modifier rework (after Skyy's /aprobe; research/Ability-Framework-Mage-Spec.md), then 2-3 classes per batch.
4. Sky Window kit into tools/skyyui.py (after Skyy's /skyprobe kit) -> one-look UI sweep.
5. Quests later rounds (markers, board, guide fairy - research/SkyyQuests-Tutorial-Spec.md).
6. ARCHITECTURE merge into ~10 jars (research/Architecture-Spec.md, modules so builders work in parallel) with simplify 2; fold MIT mods
   (Multitools, Reforged Weapons, MoreTotems Water Totem, BetterBiomes, More Mounts) with credit.
7. World + release polish: structure mods, Lost Loot piles + airdrops + identify animation, perfect dodge into our roll, economy audit,
   sound pass, admin page, load test, release packaging. Parked specs: gems, inventory buttons / offhand, upgrade ladders, pet eggs v2.

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
