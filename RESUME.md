# SkyWynn - RESUME HERE (updated 2026-11-14; TEST 284 live, nothing running)

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
- LIVE up to TEST 280 (2026-11-08 11:02, backup deploy-20261108-1102). The 11-08 batch of Skyy's test requests is all deployed, none seen in game yet:
  272 Shards 0.4.19 offline limit; 273 Bazaar 0.2.4 + Skills 0.4.70 + Sacks 0.8.35 + Gear 0.3.55 (shard Sell, how-to-level lines, shard XP class limit, Furnace All + button);
  274 Pets 0.4.24 mounting; 275 Accessories 0.5.36 Enchanted costs; 276 Sacks 0.8.36 metals in Smithing + Pocket Sell; 277 Shards 0.4.20 caps + compression + 20 % XP + ingots;
  278 Sacks 0.8.37 Furnace sort; 279 Pets 0.4.25 dragon circles + aggressive; 280 Shards 0.4.21 Combat arenas + walls + level with owner + bags. Hytale 0.7.6.
- Builders write in the worktree .claude/worktrees/resume-review-87c362 (a hook blocks the base checkout): commit / pin there, push with
  `git push origin HEAD:main`; in the base checkout `git pull --rebase --autostash`, copy the new jars in (git-ignored), deploy + record_deploy there.
- Old untracked drafts (tools/shards_0_4_8_patch.py, SkyyShards/*_0.4.8.py, ...) are leftovers - leave them / tidy later.
- Players' world: Subcaverna has 0.5.2 + 0.5.3 in Mods (fine while off). NoCube Orchard benches broken on 0.7.4 (theirs; Skyy: "leave it alone and wait").

## RUNNING
- LIVE (TEST 284, 2026-11-14 21:09): SkyyMenu 0.3.50 inventory screen P1 (Tab), SkyyShards 0.4.22 Collect grid, SkyyBazaar 0.2.5 simpler offers; SkyyUiProbe retired. Waiting on Skyy's test. Art waiting on review: skill page (Mining) + shard clicker mockups (research/ui-theme-art/, research/Shard-Clicker-Idea.md: quarry per zone, town defense, crop / wood clusters per zone).

- LIVE TEST 285 PASS: SkyyMenu 0.3.51 Craft crash fix.
- LIVE TEST 292 (2026-11-21): SkyyMenu 0.3.56 themed Furnace / Tanning panel + skill icons / XP bars + class XP bar (SkyySacks 0.8.40, SkyySkills 0.4.71). TEST 291 small fixes; 290 armour / off-hand + teleport editing + pocket Auto-compact; 289 Charms panel. TESTs 286-292 wait on Skyy. Inventory leftovers (later Menu round): dailies in Right now (no bridge yet), Requip Salvage (new journaled requip:fn:act op in SkyyWardrobe) + storage scroll + charm / ability slots, keys 1-5 (client probe first), SkyyMenu Mods list death text; Merge 3 / Upgrade bag wait on Skyy costs.
- 2026-11-21 Skyy: "build and deploy everything on your list" (docs/answered/project.md). ALSO RUNNING (same worktree, separate mods; resume each with Workflow scriptPath + resumeFromRunId, same args): rar3 (Gear 0.3.59 + Mobs 0.1.27 + Sacks 0.8.41 rarity / tooltip pass = NEXT item 4); [11-22: shardx1 + treemap1 resumed after a PC restart, same run ids] treemap1 (SkyyTrees 0.6.10 tree:fn:map / act + SkyyMenu 0.3.61 skill tree inline on each skill page); shardx1 (SkyyShards 0.4.27 BIG: clicker-only shards + migration, simple totems, clear costs, auto-smelt buy, self-sustaining costs, Combat kill coins, image shrink part 2); QUEUED from Skyy's 11-21 test (docs/answered/ui.md + world.md): Shards BIG round (ultracode-size, saved-data migration) right after fight1 = REPLACE the walkable shard worlds with the clicker (Skyy 11-21: 'compleatly replace this with the clicker system, instead of keeping both'; islands / upgrades / totems / storage carry over, nothing lost, journaled) + the old shard menu (Map / Totems / Collect, Enter Shard) goes: shard-wide upgrades (storage, compactor, time compressor, offline harvest, next islands) move into the clicker list + Combat clicker kills pay coins too (reuse mob:fn:killCoins) + BALANCE: every clicker upgrade paid from what that clicker produces (+ coins), except shard-wide / main-island upgrades and new-island unlocks (need that type from the world first, e.g. Birch logs for the Birch island) + SIMPLE totems in the clicker (Skyy: 'the current totem thing is bugged, complicated and annoying'; default in docs/answered/world.md 11-21) + drop the old map art (6 BaseX@2x 1680x1376 = 14 Mpx) + clicker cost lines clear (each part have / need green / red, all clickers) + buy Auto-Smelt (Smithy I) right on the quarry page (Skyy: 'i need a way for an auto smelt upgrade') ( do NOT deploy fight1 alone - it adds 3 Mpx, deploy it with atlas1 or after the shrink); (launched as menufix1, was: ) top bar at the very top of the screen + each skill page shows its tree INLINE (no Open tree button) + inventory SKILLS card: each skill tile is the button to its page, no Open button + skill page TOOL card counts multitools + Fortune shows 0% '(max 0%)' (missing cap read as 0; Skills says uncapped) + inventory Requip panel editing broken (drag to preset slot / Keep / Save / Rename) + Requip 'Storage 20' opens a dead page with no Back + inventory Crafting panel crafts nothing ('crafting doesnt work at all') + inventory Void Charms panel = compact ROW list like the old Void Charms CRAFT tab (craft / upgrade per line), not grid + pick + inventory Void pocket panel: clicking an item does not select it + Void pocket grid counts capped at 100 (show the real amount, e.g. 230 / 1.2k) + recheck the inventory red edges; DONE menufix1 = TEST 305 (Menu 0.3.60 + Accessories 0.5.38: 10 of 11 test fixes; inline skill tree = next round treemap1), mobcoin1 = TEST 304 (Mobs 0.1.26 kill coins), atlas1 + fight1 = TEST 303 (Trees 0.6.9 lean map pictures, Shards 0.4.26 Combat town clicker; SET UI 49.6 Mpx - Shards part 2 target <= 14 Mpx: 6 Base@2x maps, 43 Range rings, SkyyRebirth Map/Base@2x later), tab3 = TEST 302 (Menu 0.3.59 Market tab + Bazaar 0.2.6), shield1 = TEST 301 (Gear 0.3.58 shields; next: Armory recolours in bags, named shield UT / boss roles), aug1 = TEST 300 (Gear 0.3.57 + Wardrobe 0.2.15 augment confirm + socketed loot; next: Bazaar skip augmented stacks via gear:fn:augCount if gear ids are ever listed), farm1 = TEST 299 (Shards 0.4.25 Farming clicker; next: Combat town-defense clicker, fix Foraging / Mining clicker memory key <profile>|<slot> shared across kinds), tab2 = TEST 298 (Menu 0.3.58 Pets tab one screen + Pets 0.4.28; next: Shift / right-click, egg drag, search + sort, egg fusing, live timers, /pets opens it), DONE sig3b + mine1 = TEST 297 (Gear 0.3.56 sig3 Gear half; Shards 0.4.24 Mining quarry + Smithy + zone locks, Skills 0.4.72 skill:fn:fortune; next clickers: Farming, Combat),  fix1 = TEST 291, inv7 = TEST 292, forage1 = TEST 294 (Shards 0.4.23 Foraging clicker; next: skill:fn:fortune bridge, golden trees, totem buy in page, open from skill pages, Mining quarry + Smithy / Farming / Combat clickers + their zone locks), tab1 = TEST 296 (Menu 0.3.57 Skills tab pages; next tab rounds: Pets, Market + bank, World, Social, Settings; shard card needs a SkyyShards read-only bridge), hud5 = TEST 295 (Hud 0.3.39 v5 cards; Bazaar has no eggs - egg listing later, metals already in Smithing), pets1 = TEST 293 (Pets 0.4.27 + Hud 0.3.38; next Pets: HUD v5 cards, summon hotkey / Z bar, non-dragon bites = Skyy balance call, Bazaar Uncommon egg price). Deploy each when READY (one smoke per batch). AFTER inv7: Menu rounds one at a time - tab screens (Skills/Mining page, Pets, Market+bank, World, Social, Settings) + the Menu Mods list death text; then the other shard clickers (Mining quarry + Smithy, Farming, Combat town defense, Shard Link).
- LIVE TEST 286: no coin death penalty (Coins 0.1.12), bank levels (Bank 0.1.17), vault page limits (Vault 0.1.10). Queued small fix: SkyyAuctions 0.1.16 texts + SkyyMenu Mods list still mention coins lost on death / /deathpenalty.
- ART SET APPROVED (11-14): 7 tabs, one screen each - research/ui-theme-art/ (inventory v5 + requip/charms panels, skill pages, shard clickers, pets, market, world v2, social, settings). NEXT after inv3: build the tab screens one round each (Skills pages: Mining first; Pets; Market incl. bank; World; Social; Settings), then the shard clicker games (Foraging / Mining quarry / Farming / Combat town defense; Shard Link pocket upgrade).

## WAITING ON SKYY
- TEST 266-280 (TEST-CHECKLIST); the Shards 0.4.21 questions are in OPEN-QUESTIONS.md. TEST 271 step 4: does the dragon absorbing staff orbs in fights feel bad? [default: keep]. TEST 270 steps 7-8: `/armory debug sig probe` (W + A probes) -> PASS unlocks sig5.
- Zone 2 element mix [default: leave]: its commons are Earth sand skeletons, so Thunder there comes only from Yellow slimes, Spirit_Thunder and
  the x2 zone drop. No hostile Air flyer / Zone 4 lake mob exists (needs new bodies). Slime Mobs!: Mods has the 1.1.4 zip (manifest 1.1.3).
- UiProbe P1-P5 (`/uiprobe tip`) -> decides price tooltips R2 Bazaar 0.2.4. `/skyprobe tour` (TEST 231) -> UI rounds R1b-R5, then retire UiProbe.
- Art review (sent 10-23): research/cloud/ui-tiles-art/sheet.png + research/cloud/page-emblems-art/sheet.png.
- The 10 vanilla-look UT names (tools/ut_vanilla.py) are placeholders - Skyy may rename. Tell joszza: River Bridges' guard role needs Mb_Bandit.
- Feel tests: caster Mana (P9 F5), Zone-1 wild adult dragons. Sacks [default: leave it]: Farmer's Workbench Essence recipe net zero.
- After Skyy plays: skill `skywynn-logs` + the SHARED-EXECUTOR check (SackBeat 'shared scheduler stalls' + 'tick max').

## NEXT (in order; Gear / Mobs rounds one at a time; launch with Workflow `skywynn-round`, Skyy's own words in quotes)
0a. PETS round (Skyy 11-14, docs/answered/pets.md): mount slot = ride only (summon -> seats you, hop off -> vanishes; summon button on the HUD mount card / key / Z bar later); combat pets FIGHT from the pet slot; dragons fight in the pet slot, ride from the mount slot. Replaces the 10-10 summon-slot rule. EGGS: craft Common only; each higher rarity = upgrade the egg below + materials. HUD v5: pet card left of the hotbar, mount right, nothing of ours on the vanilla compass (only below it), centre clear.
0. From 11-08: Trees 0.6.8: DefaultOk on the sickle Replace (Skyy_Tree_HarvR_HE SEVERE, docs/log 11-08). Armory ArmoryCheck one-shot boot check needs the same retry as Skills PACK_MAX. Economy check: Bazaar Enchanted sell price vs 100x base, for compressed shard stock. Gear SX_PACK row for DualRuneBlade (The Armory 1.25.1 removed its Ability 1).
1. DONE (TEST 297): sig3b.
2. DONE (TEST 300): augment salvage confirm + socketed loot.
3. DONE (TEST 301): shields.
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
