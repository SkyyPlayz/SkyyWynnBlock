# SkyWynn - RESUME HERE (updated 2026-11-01; TEST 269 live, a batch pinned + 2 rounds running)

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
- LIVE up to TEST 269 (2026-11-01 11:53, backup deploy-20261101-1153): Gear 0.3.53 (Bronze weapons + spear recipes, 10 vanilla-look UT
  weapons - names unconfirmed, Void Scythe Mythic, Diving Crude out of bags), Classes 0.1.52 + Menu 0.3.48 (rarity part 2). Before: 268 augments A2
  (Gear 0.3.52, Sacks 0.8.34, Pets 0.4.22, Accessories 0.5.35, Skills 0.4.69); 267 rarity pass (10 mods) + Gear 0.3.51 + Classes 0.1.51 / Mobs 0.1.23.
- Builders write in the worktree .claude/worktrees/resume-review-87c362 (a hook blocks the base checkout): commit / pin there, push with
  `git push origin HEAD:main`; in the base checkout `git pull --rebase --autostash`, copy the new jars in (git-ignored), deploy + record_deploy there.
- Old untracked drafts (tools/shards_0_4_8_patch.py, SkyyShards/*_0.4.8.py, ...) are leftovers - leave them / tidy later.
- Players' world: Subcaverna has 0.5.2 + 0.5.3 in Mods (fine while off). NoCube Orchard benches broken on 0.7.4 (theirs; Skyy: "leave it alone and wait").

## RUNNING / PINNED (2026-11-01, Skyy: "work through the entire list of things you can do.")
- Running: aug3 wf_db158ac2-a15 (Mobs 0.1.25 augment drops by zone / element / rank + element mobs + Slime Mobs! roles tagged, Merchants 0.1.9
  T1 augments, maybe Gear 0.3.55); crescent Armory 0.1.51 PINNED (Crescent Rush Spellblade-only).
  If this session reset before they reported: their drafts are in the worktree (git status); read each round's report with
  `python tools/dev/scratch/reports/dump.py <wfRunId> <name>` (worktree; journal under ~/.claude/projects/...worktrees-resume-review-87c362/
  <session>/subagents/workflows/<wfRunId>/), check the cross-check VERDICT, else re-run `skywynn-round` for that round.
- PINNED, not deployed (deploy as ONE batch with aug3; crescent Armory 0.1.51 also pinned): gl2 Gear 0.3.54 + Mobs 0.1.24 (Trork / Kweebec sets); sig3a Armory 0.1.50
  (sigfx bridge, signature probes, Doomcaller); aug4 Menu 0.3.49 (Elements charts); katana Classes 0.1.53. Test steps for each: the
  docs/log/2026-11.md PINNED lines + tools/dev/scratch/reports/<tag>.md (gl2, sig3a, aug4, katana).
- aug3 brings a PACK.md row + deploy_set pack-key change for Slime Mobs! (installed 1.1.3; 1.1.4 is out) - the main session applies it.

## WAITING ON SKYY
- TEST 266-269 (TEST-CHECKLIST). After the next deploy: `/armory debug sig probe` (W + A probes) -> PASS unlocks sig5.
- UiProbe P1-P5 (`/uiprobe tip`) -> decides price tooltips R2 Bazaar 0.2.4. `/skyprobe tour` (TEST 231) -> UI rounds R1b-R5, then retire UiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png + research/cloud/page-emblems-art/sheet.png.
- The 10 vanilla-look UT names (tools/ut_vanilla.py) are placeholders - Skyy may rename. Tell joszza: River Bridges' guard role needs Mb_Bandit.
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons. Sacks [default: leave it]: Farmer's Workbench Essence recipe net zero.
- After Skyy plays: skill `skywynn-logs` + the SHARED-EXECUTOR check (SackBeat 'shared scheduler stalls' + 'tick max').

## NEXT (in order; Gear / Mobs rounds one at a time)
1. Pin aug3, PACK Slime Mobs!, ONE smoke + deploy of the whole pinned batch.
2. sig3b Gear half: Weapon_Staff_Doomed into ut_vanilla LOOKS, sig.ut defaults (Paperweight -20, Ricochet +25), C+ charge rules, orange
   signature names, gear:fn:elemPower (apply(UUID) -> "Earth:0,Thunder:3,...", Menu 0.3.49 reads it), GearPool.leanHit full-family fix (Katana).
   Gear must check armory:fn:sigfx "owns:<id>" before calling sigfx (no double effects). research/UT-Mythic-Signatures.md section 8.
3. Augment salvage / sell confirm ("this item has N augments") - Gear + Wardrobe (Requip) + the sale path.
4. Shields = Warrior off-hand gear (Skyy 10-30 yes): own full round (research/Vanilla-Gear-Audit.md 8.5).
5. Rarity + tooltip pass for Gear, Mobs, Sacks (Classes / Menu + 10 others done).
6. sig4 (7 base family signatures + Loophole Lance) and sig5 (13 Mythic signatures, after the probe PASS).
7. Small: other 11 Bronze weapon families (Armory); Void Scythe boss source (boss round); Tempo caster hooks (Armory); Game Review Pack area.
8. Older: price tooltips R2 / R3, BetterMap shard-world listing, UI R1b-R5, Dragon-Quest-Spec (Skyy's call), GlymeraSigns ask (Skyy sends).

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
