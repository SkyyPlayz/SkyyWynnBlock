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

## Now (2026-10-11 early)
- LIVE (deployed 2026-10-10 19:13, backup deploy-20261010-1911): Pets 0.2.3, Menu 0.3.17 (layout D + icons + editor), Armory 0.1.20 (wand
  single launch, keeps damaging falls, Soul Cages), Skills 0.4.30, Classes 0.1.19, Gear 0.2.20 (tool rarity, multitools, new tooltips),
  Accessories 0.5.11, WorldGen 0.5 (vanilla gen masked into islands, /zone proof -> skywynn_proof2), NEW Wardrobe 0.1; Multitools ON.
- PINNED, NOT DEPLOYED (deploy at Skyy's next close): SkyyGear 0.2.22 (Reforge page tabs Reforge | Upgrade | Multitool, /upgrade, /multitool
  merge page 0.2.21, item names " [Lv N]"), SkyyCollections 0.2.9 (coll:fn:catTotal).
- BUILT, NOT PINNED: SkyySacks 0.7.17 (deposit / hotbar refill / craft bridges / class filter) - CONTRACT MISMATCH with SkyyWardrobe 0.2:
  sacks:fn:deposit takes blocks itself, Wardrobe 0.2 giveBack takes the slot first -> fix in SkyyWardrobe (giveBack: no takeOff / put-back,
  call deposit {UUID, id, Long qty, Integer hotbarSlot}) then ship Sacks 0.7.17 + Wardrobe 0.2.x + Gear 0.2.23 TOGETHER (R4).
- Running at hand-off (check their results): requip02 (SkyyWardrobe 0.2 Requip, ultracode + recheck), smithing (SkyyGear 0.2.23 /smithing
  hub), uiprobe05 (SkyyUiProbe 0.5: kit textures K1, cross-jar tabs H1, custom quality tooltip T1 - needs Skyy's test session), licence
  audit agent (research/Licence-Audit.md).
- Skyy's open tests: TEST-CHECKLIST 55 (big batch) + older; gathering probe (/gprobe kit, P1-P6) still untested.

## Next, in order
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
7. Specs waiting: Requip (done), Upgrade ladders + Dragon sets, Special tools, Pet eggs v2, Zone regen, Avatars (cloud CLOUD-RESUME.md).

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
