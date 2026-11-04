# SkyWynn - RESUME HERE (updated 2026-11-01 evening; TEST 270 live, nothing running)

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions = `HANDOFF.md` section 1 = `tools/deploy_set.py` SET.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-11.md` (October: `2026-10.md`). Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.
Leftover local jobs (beta bugs): `LOCAL-RESUME.md`. Older RESUME detail: git history of this file.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage) before each round. World **NewBetaTest**.
2. Skyy's standing order (10-22): "work through your whole list." - take defaults; ask real design choices as popups (AskUserQuestion).
3. Rounds: Workflow `skywynn-round` (args tag / mods / task / quotes = Skyy's OWN words / others / recheck). Deploy = skill `skywynn-deploy`
   (backup -> `smoke_test.py --allow-pack-api` -> `deploy_set.py --yes` -> `record_deploy.py` -> commit -> `tidy_local.py --yes`).
4. After Skyy plays: skill `skywynn-logs`. Skyy shares a mod: skill `skywynn-mod-check`. Art: skill `skywynn-art`.

## NOW
- LIVE up to TEST 270 (2026-11-01 14:31, backup deploy-20261101-1431): Gear 0.3.54 (Trork 2/4 + Kweebec 2-piece sets), Mobs 0.1.25 (augment
  drops by zone / element / rank, zone elements, Slime Mobs! roles tagged), Merchants 0.1.9 (Augments tab), Armory 0.1.51 (sigfx bridge, signature
  probes, Second Opinion, Revolving Door, Doomcaller; Katana keeps the vanilla stab), Classes 0.1.53 (Katana = Warrior), Menu 0.3.49 (Elements
  reaction chart + states). Pack: + Slime Mobs! (lizard, MIT). Before: 269 Gear 0.3.53 Bronze weapons + vanilla UT weapons, Classes 0.1.52 / Menu
  0.3.48 rarity; 268 augments A2; 267 rarity pass (10 mods). Game Review artifact v17 (2026-11-01).
- Builders write in the worktree .claude/worktrees/resume-review-87c362 (a hook blocks the base checkout): commit / pin there, push with
  `git push origin HEAD:main`; in the base checkout `git pull --rebase --autostash`, copy the new jars in (git-ignored), deploy + record_deploy there.
- Old untracked drafts (tools/shards_0_4_8_patch.py, SkyyShards/*_0.4.8.py, ...) are leftovers - leave them / tidy later.
- Players' world: Subcaverna has 0.5.2 + 0.5.3 in Mods (fine while off). NoCube Orchard benches broken on 0.7.4 (theirs; Skyy: "leave it alone and wait").

## RUNNING (2026-11-03, Skyy's test fixes come first)
- cave = plain Agent builder (the workflow refused, newer dragon message relayed) (Shards 0.4.18: Mining caves look like caves, mouth lines up with the bridge, one-time rebuild marker cave=2).
- Dragon riding (Skyy 11-03 "i cant ride the dragon"): cause = pets.passthrough=all makes pets Intangible (F cannot target); plain builder Pets 0.4.23 running.

## WAITING ON SKYY
- TEST 266-270 (TEST-CHECKLIST). TEST 270 steps 7-8: `/armory debug sig probe` (W + A probes) -> PASS unlocks sig5.
- Zone 2 element mix [default: leave]: its commons are Earth sand skeletons, so Thunder there comes only from Yellow slimes, Spirit_Thunder and
  the x2 zone drop. No hostile Air flyer / Zone 4 lake mob exists (needs new bodies). Slime Mobs!: Mods has the 1.1.4 zip (manifest 1.1.3).
- UiProbe P1-P5 (`/uiprobe tip`) -> decides price tooltips R2 Bazaar 0.2.4. `/skyprobe tour` (TEST 231) -> UI rounds R1b-R5, then retire UiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png + research/cloud/page-emblems-art/sheet.png.
- The 10 vanilla-look UT names (tools/ut_vanilla.py) are placeholders - Skyy may rename. Tell joszza: River Bridges' guard role needs Mb_Bandit.
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons. Sacks [default: leave it]: Farmer's Workbench Essence recipe net zero.
- After Skyy plays: skill `skywynn-logs` + the SHARED-EXECUTOR check (SackBeat 'shared scheduler stalls' + 'tick max').

## NEXT (in order; Gear / Mobs rounds one at a time; launch with Workflow `skywynn-round`, Skyy's own words in quotes)
1. sig3b Gear half: Weapon_Staff_Doomed into ut_vanilla LOOKS, sig.ut defaults (Paperweight -20, Ricochet +25), C+ charge rules, orange
   signature names, gear:fn:elemPower (apply(UUID) -> "Earth:0,Thunder:3,...", Menu 0.3.49 already reads it), GearPool.leanHit full-family fix
   (Katana). Gear must check armory:fn:sigfx "owns:<id>" before calling sigfx. research/UT-Mythic-Signatures.md section 8.
2. Augment salvage / sell confirm ("this item has N augments") - Gear + Wardrobe (Requip) + the sale path. Socketed loot (aug.loot.prefill, Gear).
3. Shields = Warrior off-hand gear (Skyy 10-30 yes): own full round (research/Vanilla-Gear-Audit.md 8.5).
4. Rarity + tooltip pass for Gear, Mobs, Sacks (the reusable script: rarity-tooltip-pass, args {mods, others}).
5. sig4 (7 base family signatures + Loophole Lance), then sig5 (13 Mythic signatures) once the probe PASSES in game.
6. Small: other 11 Bronze weapon families (Armory); Void Scythe boss source (boss round); Tempo caster hooks (Armory); Game Review Pack area;
   new mob bodies (hostile Air flyer, Zone 4 lake mob).
7. Older: price tooltips R2 Bazaar 0.2.4 / R3 Gear (after P1-P5), BetterMap shard-world listing, UI R1b-R5, Dragon-Quest-Spec (Skyy's call).

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
