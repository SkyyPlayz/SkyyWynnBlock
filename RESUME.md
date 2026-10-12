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

## Now (2026-10-11 ~01:45, PAUSED at 97% weekly - Skyy: wait for the morning)
- LIVE: everything through 2026-10-11 01:40 (TEST 55-58): big batch 2026-10-10 + SkyyGear 0.2.22/0.2.23 (/smithing, Reforge tabs, /upgrade,
  /multitool, [Lv N]), Collections 0.2.9, Armory 0.1.21 (Soul Orb damage, vanilla essences, Wings of Fate), REQUIP = SkyyWardrobe 0.2
  (+ SkyySacks 0.7.17 hotbar refill / craft bridges), SkyyUiProbe 0.5 + B (Skyy runs /skyprobe kit once, then RETIRE both).
- Nothing running. Known low issue (no item loss/dupe): a crash in the middle of Requip "Use what I wear" saving can leave a stamped item
  unknown to the pool until the next deposit / Equip (log 2026-10-11) - journal op 12 in a later Wardrobe round.
- Skyy tests: TEST-CHECKLIST 55-58 + UI probe + gathering probe.

## Next, in order
0. After the reset (TUE 2026-10-13 15:00 UTC): first a cheap PACK MAP tool (per mod: commands, bridge keys, data folders, items, Server Setup tabs) - feeds the architecture merge; refine / merge rounds use skywynn-round simplify: 2.
1. Finish R1-R4: Wardrobe deposit fix -> integrate Wardrobe 0.2 + Sacks 0.7.17 + Gear 0.2.23 (+ SkyyMenu tiles: Requip rename, Crafting)
   -> smoke -> deploy. Then SkyyGear 0.2.24: ONE Anvil tab = Reforge + Upgrade + Identify (appraisal-tool rule) + pickaxe -> Multitool path;
   Crafting hub naming (Smithing = a tab of Crafting, class filter on every crafting tab).
2. Bags v2 = SkyyVoid (research/Bags-v2-Spec.md): SkyySacks 0.8.0 + Bazaar 0.1.8 ultracode (after 0.7.17 pins); display name SkyyVoid.
3. Skyy runs the UI probe (uiprobe05) -> then the Sky Window kit (art/ui-kit-sky/) into tools/skyyui.py + tooltip frames (art/tooltip-sky/)
   into SkyyGear qualities.
4. HYTALE 0.7 (2026-10-12): FIRST check how 0.7 changes menus + the inventory screen (Skyy: hub buttons INTO the inventory, menu item
   removed) + probe inventory injection; fix 0.7 breakages; then the hubs (research/Hubs-Spec.md + docs/answered/ui.md 2026-10-10 merges:
   Anvil, Stats+Skills, Trees+Abilities, Travel, Bank+Vault, Collections+Recipes, Market; Guild separate; party cards + social buttons).
5. ARCHITECTURE (research/Architecture-Spec.md, approved): SkyyCore + merges into 10 jars, stable plugin names, refine pass in every phase;
   fold licence-permitting pack mods in (research/Licence-Audit.md; GPL = share-alike question for Skyy).
6. MORNING QUESTIONS for Skyy (research/Licence-Audit.md): repo LICENSE (suggest MIT), GPL share-alike modules (keep GPL mods separate [default]),
   send author asks (Dynamic Seasons + More Crossbow Tiers first - in the pack with no grant); wand fall rule is done; PACK.md fixes listed in the audit.
7. DONE 2026-10-11: SkyyArmory 0.1.21 deployed (Soul Orb damage, vanilla essences, faster tether, lines, Wings of Fate; research/classes/Priest.md).
9. OPENROUTER (research/OpenRouter-Jev-Plan.md): lean rounds - llm.py --json + jev helper, log-digest tool, pack-map summaries (with item 0), free_lens in skywynn-round. llm.py is already free-first; gh works via a Terminal-panel tab.
10. NEW 2026-10-11 (docs/answered skills / gear / world): Perfect Dodges idea INTO our roll (perfect-dodge window + counter, Acrobatics perk); fold Reforged Weapons (MIT) into SkyyArmory with credit; structure-mod survey (free models) + island test world. Perfect Parries is in the pack (tune_perfect_parries). LOST LOOT: SkyyExploration Unclaimed Luggage + airdrops get a crate-style reveal + new name; Identify gets a reveal animation (docs/answered/economy.md).
8. Specs waiting: Requip (done), Upgrade ladders + Dragon sets, Special tools, Pet eggs v2, Zone regen, Avatars (cloud CLOUD-RESUME.md).

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
