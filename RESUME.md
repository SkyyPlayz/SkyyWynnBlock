# SkyWynn - RESUME HERE (updated 2026-10-11 ~04:30 UTC, end of the 2026-10-10 marathon)

Read this first, then only what the task needs. Map: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`. Skyy's tests:
`TEST-CHECKLIST.md` (item 55 = the big 2026-10-10 batch). Full history: `docs/log/2026-10.md` (2026-10-10 lines). Decisions word for word:
`docs/answered/<topic>.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (weekly resets TUE 2026-10-13 15:00 UTC). Skyy 2026-10-10: "when usage hits 98% get all
   tasks to a good pausing point, update the resume, and wait till the morning" - and earlier "go ahead and build, im not worried about usage".
2. Read the newest lines of docs/log/2026-10.md (what finished overnight), then check the background rounds listed under "Running".
3. Rounds: saved workflow `skywynn-round` (Skyy's OWN words in args.quotes); deploy only with the game closed: backup -> smoke -> deploy_set
   --yes -> record_deploy -> commit -> tidy_local; scan + recycle logs after every play session.

## Now (2026-10-13 ~15:30 MDT, reset day - weekly 22%)
- LIVE on Hytale 0.7.0, crosscheck READY (was 39 fails): 0.7 port of every mod (batches 1-2, Skills 0.4.31 Mana / spell costs), lag fixes
  (Coins write-behind, Bazaar / Guilds / Auctions, Accessories, Sacks, Collections, Wardrobe, Gear snapshot, Hud own thread, Skills /
  Fishing / Merchants / Exploration / Islands writers, Menu / Bank / Profiles), Armory 0.1.23 from source, hub hotkey (double-tap crouch),
  Anvil tab (Gear 0.2.26), notification feed + XP flash (Hud 0.3.20), probes /aprobe + /skyprobe hubpanel. TEST-CHECKLIST 60-69.
- Running: void080 (SkyySacks 0.8.0 SkyyVoid + Bazaar 0.1.9), quests01 (SkyyQuests 0.1 + Hud 0.3.21 quest widget).
- Specs waiting on Skyy: Gathering-Shards (sec 14), Ability-Framework-Mage (sec 11), SkyyQuests-Tutorial (sec 12); cloud drawing /rebirth + shard menu.
- Next builds: senders switch to the feed (msgroute), Enchanted materials (gathering phase 1, after void080), Mage real keys (after Skyy's /aprobe),
  Sky Window kit into skyyui.py (after Skyy's /skyprobe kit), architecture merge (SkyyCore) with simplify 2.

## Next, in order (re-planned 2026-10-12 with Skyy; weekly resets TUE 15:00 UTC; ~4-5 workflows at once)
VISUALS (Skyy 2026-10-13, docs/answered/ui.md): no approval wait - cloud draws icons / menu designs, I review layout + look myself, then implement; Skyy fixes later.
WAVE 1 - make 0.7 work (day 1)
1. 0.7 PORT (research/Hytale-0.7-Port.md): probe the ChunkGrid block API, then port Islands + Exploration first, then Merchants, Menu,
   Bank, Armory, Gear (crit CombatTextUpdate), Mobs, Profiles, WorldGen; retire SkyyGatherProbe (+B) and other spent probes instead of
   porting. crosscheck 0 fails + smoke PASS + deploy. Also: tools/skyyui.py SUI.verify 0.7 fix; how 0.7 changed menus / inventory
   (Skyy: hub buttons INTO the inventory, menu item removed) + inventory-injection probe.
1b. SkyyArmory FULL build script to 0.7 assets (0.1.22 is a jar re-compile: vanilla staffs lost a charge setting, an orb particle renamed, wand tap 0.346 -> 0.329 s) - after wave 1.
1c. LAG QUICK-WINS round after the port (research/Code-Structure-Audit.md "Plan" 1): lock-free bridge, Coins write-behind, SkillTop index, SkyyIO writer (no sleeps on world threads), Hud world-time + executor, Gear stats snapshot, Bazaar / Guilds / Bank locks. Audit group 6 (Sacks, Collections, Accessories, Vault, Wardrobe, Pets) still to run.
2. Same day, small lean rounds: chat-digest leads (tree-felling double Foraging XP, rank-up double Farming XP, Acrobatics XP after level-up,
   batch toasts); SkyyBank 0.1.8 catchUpPeriods default 1; 2026-10-19: pack mods still broken on 0.7 -> our own if easy (Saplings From
   Trees) / GPL fork fix (BME, separate module) (docs/answered/project.md); a pre-deploy game-version-range check in smoke / deploy (no agent).
WAVE 2 - cheap tooling + surveys (free OpenRouter / Jev where possible)
3. Pack map tool; llm.py --json + jev helper; log-digest; free_lens in skywynn-round (research/OpenRouter-Jev-Plan.md).
4. Pack overlap audit + CurseForge survey per area -> best-of-each + install list for Skyy (research/Mod-Database*.md, PROJECT-RULES 2).
5. SkyyGear 0.2.24: ONE Anvil tab (Reforge + Upgrade + Identify, appraisal rule) + Crafting hub naming + class filter on crafting tabs.
6. UI: Skyy runs the UI probe -> Sky Window kit into skyyui.py + tooltip frames; hubs (research/Hubs-Spec.md); chat overflow (XP to the HUD
   skill list, notification feed, Chat / Feed / Off settings); QUEST WIDGET (essential); collection rank-up recipe line (+ click probe).
ABILITIES (Skyy 2026-10-13, docs/answered/classes.md): framework + MAGE first end to end (after skills07), Skyy tests + refine, then 2-3 classes per batch.
WAVE 3 - specs (spec rounds, Fable synth; check existing mods first)
7. GATHERING spec: tier gate, LIFELONG tools (spawn with hatchet / pickaxe / hoe / sickle; pole via hub quest; shovel = plain craft), rarity
   upgrades, tool XP -> Upgrade Points, enchanted upgrade costs, Fishing skill + tree, + SHARDS (6 shards, minion-style totems, shard menu,
   fixed-slot layout) + Farming / Ranching / Orchard split + farming totems (research/Shard-Islands-Ideas.md, docs/answered gear / skills).
8. REBIRTH spec (research/Rebirth-Ideas.md; research Shell Diver + clicker prestige first).
9. SKYYQUESTS + TUTORIAL spec (research/Tutorial-Plan.md; starter islands; study QuestLines, read only).
WAVE 4 - big builds
10. Bags v2 = SkyyVoid (research/Bags-v2-Spec.md): SkyySacks 0.8.0 + Bazaar 0.1.8.
11. ARCHITECTURE merge into ~10 jars (research/Architecture-Spec.md) with simplify: 2; fold MIT mods (Multitools - lock to rebirth 1,
    Reforged Weapons, MoreTotems Water Totem, BetterBiomes, More Mounts) with credit.
12. Island test world: structure mods, BetterBiomes, ReChunk, Starblight (overrides 27 vanilla armor ids); perfect dodge into our roll;
    Lost Loot reveal (luggage + airdrops) + identify animation; economy audit; sound pass; one-look UI sweep; raw-id scan; admin page;
    load test; ranks; release packaging. Specs waiting: Upgrade ladders + Dragon sets, Special tools, Pet eggs v2, Zone regen, Avatars.
SKYY: research/SkyyQuests-Tutorial-Spec.md section 12 (10 questions); SKYY: Mage /cast test (research/Ability-Framework-Mage-Spec.md section 8 part 1, TEST-CHECKLIST 11) + its section 11 questions; review research/Gathering-Shards-Spec.md section 14 (14 questions, defaults given) before phase 1 (Enchanted materials); SKYY: UI probe (/skyprobe kit), author asks #12-15 (research/Author-Requests.md), install FL's Exotic Weaponry (study only), video tests
via Grok from WED (playtest/), test 59 (parries) + 60 (0.7 boot).

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
