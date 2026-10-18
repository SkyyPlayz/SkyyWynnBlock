# SkyWynn - RESUME HERE (updated 2026-10-18 ~02:10 MDT after the overnight run; Skyy resets the session after this)

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage). Deploy target world **NewBetaTest** (`tools/deploy_set.py` WORLD).
2. Rounds: while Skyy chats on other topics run builders as PLAIN Agents and spawn critics yourself (workflow builders refuse); else the
   saved workflow `skywynn-round`. Deploy (game closed): skill `skywynn-deploy` = backup -> `smoke_test.py --allow-pack-api` (Perfect
   Parries pack-API fail is third-party) -> `deploy_set.py --yes` (check the LAST line says "deployed N mods") -> `record_deploy.py` -> commit -> tidy.
3. After Skyy plays: skill `skywynn-logs` (`python tools/log_scan.py --ours`, then `--recycle`).

## LIVE NOW (deployed 2026-10-17/18, TEST-CHECKLIST 172-190; details per number in docs/tests/2026-10.md)
- 172-176: Void Charms rename everywhere, Potion Flask + Food Pouch, Teleport page + /back + homes, Breach x Mark, Requip food fix, Nestkeeper ON.
- 177 ores round (WorldGen / Accessories Furnace Charm / Sacks / Collections / Bazaar / Skills; the five roll back TOGETHER).
- 178 PR #17 Armory sets as mob drops; 179 Salvagebench guard; 180 starter wand leap; 181 zone Mining sets + armor weight text + starter
  quest class gear; 182 Fortune + big-tree log pickup fix; 183 HUD ability icons; 184 15-step tier renumber + Mage PA4 Meteor from the Rift;
  185 metal tools + 76 metal weapons + Bazaar 0.1.21; 186 Movement 2 (speed + jump vs The Armory); 187 80 vanilla-style metal weapons.
- Pins now: Gear 0.3.24, Armory 0.1.34, Skills 0.4.51, Accessories 0.5.26, Core 1.0.1, Sacks 0.8.22, Collections 0.2.26, WorldGen 0.7.4,
  Bazaar 0.1.21, Auctions 0.1.13, Classes 0.1.38, Trees 0.3.23, Quests 0.4.1, Hud 0.3.32, Menu 0.3.39 (Gear now 0.3.25, Collections 0.2.27) (all: tools/deploy_set.py SET + HANDOFF).

## RUNNING / JUST BUILT
- Overnight (Skyy: "work through your whole todo list ... pich what fits the existing build"): DONE - every round deployed (TEST 176-189);
  nothing running. Locks: LOCAL-RESUME.md (empty).
- Cobb (Skyy's Grok bot) does design / specs / reviews only; all builds local (LOCAL-RESUME.md, CLOUD-RESUME.md "Cloud build trial").

## FOR SKYY THIS MORNING
- Test: TEST-CHECKLIST 176-187 (newest first matter most: 189, 188, 187, 186, 185, 184).
- Overnight defaults to OK or change: OPEN-QUESTIONS.md lines marked "[default taken overnight ...]" (ore gate speeds, Quirk models not
  shipped, PA4 auto-fire, Onyxium vs Lumen, UT lines OFF, spawn factors, Nestkeeper, joszza, structures).
- Art to look at: models-local/art/metals/_sheets/weapons-c.png (sent in chat).

## FIRST: BETA BUG LIST (docs/tests/2026-10-17-beta-bugs.md, 19 bugs, PR #18) - triage -> research/Beta-Bugs-Triage-2026-10-17.md, then fix
   rounds per mod (Skyy's test fixes come first). Gear 0.3.27 (UT bands + elite sources) PINNED, deploys when the game closes.
   Bugs #7 #8 #10 #14 #18 PARKED (Skyy 10-18 "disregard for now"). Starter-island POND (watering can + fishing, world.md 10-18) added
   to the running Islands 0.5.20 bug round.
   Gear 0.3.28 (Fortune 3/level, no cap) BUILT -> Bronze cap 33 levels fix -> review. Knock-on: Skills 0.4.53 must lift perk.doubleDropMax
   (still caps level/accessory/pet/armor Fortune at 100%). Fishing cap 20% waits for the fishing overhaul. Mobs 0.1.11 + Quests 0.4.2 BUILT, in review.

LIVE: TEST 191-193 (Islands 0.5.20 deployed 10-18 09:06).

USAGE 10-18 ~12:20: weekly 83% (resets 2026-10-20 09:00 MDT) -> only finish + deploy what is built; Level-Bands-20 RUNNING (Skyy go: tier_tags + Gear 0.3.29, then Mobs 0.1.12 / Armory 0.1.37 / Collections / Bazaar / Auctions); Armory 0.1.36 wand x2 RUNNING; chests, bucket, SkyyZones, bench keeper WAIT for the reset.

## NEXT (after Skyy's answers)
0. QUEUE 10-18 (Skyy answers in docs/answered): Level-Bands-20 build (research/Level-Bands-20-Spec.md; cap 50 +10/rebirth, Mushroom 15th crop)
   after Gear 0.3.28 pins -> Gear 0.3.29 -> Mobs 0.1.12 -> Armory -> Collections -> Bazaar -> Auctions together; Skills 0.4.53 (doubleDropMax
   no cap + cap 50 first run); per-profile world chests in SkyyExploration (research/Per-Player-Loot-Survey.md, refill never, sparkles);
   Infinite Water Bucket MID GAME (SkyyGear, research/Farming-Mods-Survey.md s3); Cooking 0.1.12 (12 own dishes) BUILT -> in review;
   our own bench-tier keeper (lean round, idea from MIT Workbench Tier Keeper; then drop KeepBenchTiers / Tier Keeper).
1. UTs: the 5 Armory UTs ship in Gear 0.3.26 (Skyy approved 10-18). Target (gear.md 10-18): per zone 3 UT armor sets (Cloth / Light /
   Heavy) + 1 UT weapon per class -> still to design: 12 armor sets (48 pieces, Zones 2-5) + 32 weapons (Spellblade Z1 + 8 x Z2-5, minus Hepta Axe).
2. Dragon pet: probe DONE 10-18; spec research/Dragon-Pet-Spec.md (8 questions; Aures message in section 8) - after elements (Pets 0.4.4).
3. WYNN ELEMENTS NOW (Skyy 10-18: before the big UT batch; all 10 answers in gear.md): build spec research/Wynn-Elements-Build-Spec.md
   DONE (10 questions for Skyy + 6 probes) -> wave 1 Mobs / Gear 0.3.28 / Classes, wave 2 Pets / Accessories / Menu. Gear 0.3.26 (5 Armory UTs) DEPLOYED (TEST 190). Running: Skills 0.4.52 mana round.
   QUIRK FIX LIST (her 4 tool models): root node R-Attachment not Pelvis (held-item, not character format); handle at the origin (moved ~206 / 271
   units); head along Z (turn 90 deg); a bit bigger (0.74x / 0.77x vanilla); Lumen gem faces have 4 see-through corner texels.
4. Zone gathering spots + seeds behind collections + crop islands: spec research/Zone-Gathering-Spec.md (10 questions) - build after answers.
5. Authors to ask (Skyy sends): Fyrrage, Elemental Knights, stonedturtle, SlverSkull, joszza (draft in research/Structure-Mods-Survey.md),
   Serj (optional). (Quirk + Cobb are Skyy's own Grok agents - their art is ours to use, Skyy 10-18.)
6. LATER (Skyy): Beastmastery, Void Particles, totems, mod compression (sections stay separate), SkyyCore 1.0.2 HubBar.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches.
- Rollback floors + go-together rules: comments in `tools/deploy_set.py` (newest: FP1 Cooking 0.1.11 needs Sacks 0.8.18 + Wardrobe 0.2.8).
- Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`. Menus follow research/Menu-Pattern.md (no back buttons, top rows always,
  requirements as a red/green list). Replace commands, never add extra. Ask Skyy in popups, one at a time.
- If a builder's smoke server is still running, deploy_set refuses - wait (never kill it). `python tools/tidy_local.py --yes` after deploys.

## On Skyy's PC (read-only except the deploy)
Project = this repo. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\` (`Server\HytaleServer.jar`,
`Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\Saves\NewBetaTest\` (mod data `mods\Skyy_Skyy<Mod>\`, server
logs `logs\`); client logs `...\UserData\Logs\`. Backups: `backups\` (git-ignored). Toolchain: Python 3.12 + jpype1 + jdk4py (no javac).
LOCAL ONLY, never in git: game files, UserData, backups, built jars (except `tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
