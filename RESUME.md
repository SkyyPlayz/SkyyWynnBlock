# SkyWynn - RESUME HERE (updated 2026-10-14 ~18:20 MDT, end of the marathon day: 23 deploys, all queued rounds landed)

Big picture for other agents: `STATUS.md`.
Read this first, then only what the task needs. Map: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`. Skyy's tests:
`TEST-CHECKLIST.md`. Full history: `docs/log/2026-10.md` (2026-10-13 lines). Decisions word for word: `docs/answered/<topic>.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly resets TUE 2026-10-20 15:00 UTC; was 33% on 10-14).
2. RUNNING since ~18:40 while Skyy play-tests 84-109 (deploy only with the game closed): classes4 (Classes 0.1.25 + Trees 0.3.10:
   settings split, Spellblade, 5th-rebirth modifier slot, Fishing tree, Farming-average tree), menu25 (Menu 0.3.25: search bars on Server
   Setup + Settings, per-player sounds switch settings:sounds:<uuid>, Shards admin buttons), sound2 (Sacks / Collections / Coins /
   Accessories / Bazaar / Auctions / Cooking / Shards sounds), rebirth6 (Rebirth 0.3.3 + Skills 0.4.39: stat nodes applied + Skills
   sounds), gear6 (Gear 0.3.6 + Fishing 0.1.6: Foraging / Farming / Fishing armor, pole perks, rebirth damage / defence, Gear sounds),
   islands3 (Islands 0.5.10 + Quests 0.3.2: the 3-island starter system), zones06 (WorldGen 0.6: vanilla-like zones as floating islands,
   0.7 content, richer looks, Zone 5 + tiers). AFTER them: sound4 (Classes / Trees + round-1 mods honour the sounds switch), classes /
   trees into Rebirth PARTS, rebirth switch-on test, load test 50 / 200 profiles. HELD until after Skyy's test: shards 7b, quest shard
   giver, Whirlwind Dash, armory-move nodes, architecture merge, release. Big picture: STATUS.md.
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
- **Deployed 2026-10-14 08:35 + 11:04 (TEST-CHECKLIST 88-97, untested; combined smoke 35/35):** Gear 0.3.3 harvest gate (88);
  Pets 0.2.5 owner key; Bazaar 0.1.11 + Auctions 0.1.5 closeall; Vault 0.1.6 fetch hook; Exploration 0.2.8 Lost Loot looks + reveal
  + supply drops; REBIRTH R3 (Rebirth 0.2, Skills 0.4.36, Coins 0.1.7, Bank 0.1.11, Profiles 0.1.13; feature OFF); NEW SkyyShards 0.1
  + Islands 0.5.8 + Menu 0.3.22; ABILITIES IN THE TREE (Classes 0.1.22 + Trees 0.3.7, Mage + Priest on rune keys, panel, levels +
  modifiers; U1-U10 unproven - scan logs after Skyy plays); Quests 0.3 + Hud 0.3.23 + Fishing 0.1.4; Sigils + armor levels + hoe area
  (Gear 0.3.4, Armory 0.1.24, Collections 0.2.13). Research today: Economy-Audit-1014, Sound-Pass-Plan, Load-Test-Plan,
  Structure-Mods-Survey, Release-Packaging-Plan (+ tools/release_pack.py), Admin-Page-Plan. Release blocker: 4 jars hold edited vanilla
  JSONs (Skills / Armory / Gear / Trees) - Skyy decides redistribution.
- **Rebirth spec FINAL:** `research/cloud/Rebirth-Spec.md` (all 16 answers + ability levels kept with a soft cap, dust x2 per rebirth ...),
  build order R1-R10 (section 6). R1 + R2 = the interrupted rebirth12 round.
- Skyy to do: run `/aprobe` (Mage keys) and `/skyprobe kit` (Sky Window kit) in game; set the 4 quest hub
  spots (`/questadmin place set hub.mining | hub.foraging | hub.farming | hub.fishing`); test 72-83; Grok video notes from WED.
- Still broken on 0.7 (switched off): Saplings From Trees, TheArmory, HyFishing, Better Mob Expansion - recheck CurseForge; after
  2026-10-19 build our own / fork where the licence allows (docs/log 2026-10-13 pack check).

## Next, in order (Skyy 2026-10-14: "Run everything you can in parallel ... done by 5 pm")
1. Land the 6 running rounds (deploy each READY one with the game closed), then the queued ones above.
2. Sky Window kit into tools/skyyui.py - BLOCKED on Skyy's /skyprobe kit; ability keys U1-U10 proven by Skyy's first Mage play + logs.
3. ARCHITECTURE merge into ~10 jars (research/Architecture-Spec.md) LAST - it touches every mod, so only when no other round runs;
   fold MIT mods (Multitools, Reforged Weapons, MoreTotems Water Totem, BetterBiomes, More Mounts) with credit.
4. Release: Skyy's call on the edited-vanilla JSONs + third-party permissions (research/Release-Packaging-Plan.md), then release_pack.
5. Parked specs: gems, inventory buttons / offhand, upgrade ladders, pet eggs v2; guide fairy (SkyyPets 0.4 with fighting pets).

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
