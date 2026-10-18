# SkyWynn - RESUME HERE (updated 2026-10-18 ~15:00 MDT; PAUSED until the weekly reset 2026-10-20 09:00 MDT - Skyy: "then we will pause till reset")

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage) - weekly was 92% on 10-18, resets 10-20 09:00. World **NewBetaTest**.
2. Rounds: while Skyy chats on other topics run builders as PLAIN Agents + your own critics (workflow builders refuse). Builders and
   reviewers read long files through Jev / free models (`tools/llm.py`); Skyy allows $10 paid OpenRouter in 2026-10 (~$1 used).
   Deploy (game closed): skill `skywynn-deploy` = backup -> `smoke_test.py --allow-pack-api` (0 SEVERE from Skyy mods) -> `deploy_set.py --yes`
   (LAST line "deployed N mods") -> `record_deploy.py` -> commit -> `tidy_local.py --yes`.
3. After Skyy plays: skill `skywynn-logs` (`python tools/log_scan.py --ours`, then `--recycle`).

## LIVE NOW (all deployed 2026-10-18; TEST-CHECKLIST 191-196, details in docs/tests/2026-10.md)
- 196 LEVEL-BANDS batch (deploy + roll back TOGETHER, guard + FLOOR in deploy_set): 20 levels per zone (Copper 1-8 ... Lumen 95-103),
  collection ladder I Enchanted / II tools / III armor / IV weapons, alloys via Furnace Charm (both inputs III) + alloy gear at both V +
  Enchanted alloys at both VI, alloys 1+1=2, Bronze Mining set, 15 Foraging + 15 Farming armor tiers (Quirk's farming art), gathering armor
  buff, multitool (no drawbacks, rebirth 1, two level sections), Vein Mine / Tree Feller at tool Lv 4/8/16/24/32/40, no Enchanted costs below
  Dusk, Soul Orb crafted at class level, Legendary aqua frames, Mobs to Lv 100 (curve stretched), bigger sacks + fair costs, worst-orb-first,
  no XP caps, Fortune uncapped, level cap 50 + 10 per rebirth (max 100), Farming paced like Mining, Requip pet portraits, Auctions save fix.
- 195 BetterMap in every zone + auto-track new worlds, mob level plates (Perfect Parries posture text off), wand hold right = block, egg fix.
- 194 wand launch ~12 blocks, one-handed Soul Orb + menu item, guaranteed Vein Mine / Tree Feller, 12 own dishes, Furnace queue/fuel/ready lists.
- 191-193 UT bands, less Mana, mob hit cap 35%, Fortune +3 a level, skip fix, no hits through walls, island respawn fixes + pond.
- Pins (tools/deploy_set.py SET = HANDOFF): Gear 0.3.29, Armory 0.1.39, Skills 0.4.53, Collections 0.2.28, WorldGen 0.7.5, Bazaar 0.1.22,
  Sacks 0.8.24, Accessories 0.5.27, Mobs 0.1.12, Auctions 0.1.14, Wardrobe 0.2.10, Pets 0.4.4, Islands 0.5.21, Cooking 0.1.12, Trees 0.3.24,
  Menu 0.3.40, Classes 0.1.39, Quests 0.4.2, Rebirth 0.3.5, Core 1.0.1.
- RUNNING (10-18 evening, Skyy: "Now, lean round"): SkyyProfiles 0.1.18 = bigger Create Profile class cards + emblem / primary /
  secondary weapon (Priest Wand + Soul Cage, Warrior Sword + Spear); docs/answered/ui.md 2026-10-18 CLASS PICKER CARDS.

## FOR SKYY (while paused)
- Test TEST-CHECKLIST 196 first (the big one), then 195, 194.
- Server Setup now if wanted: Classes > Sacred Heal cooldown -> 8 (all 4 rows); Rebirth > rebirth.max -> e.g. 1000 (unlimited rebirths).
- Open choice (OPEN-QUESTIONS): Copper Staff costs 20 Mana of a 40 pool at Lv 1 (50%, over the 40% rule) - drop to 15?

## AFTER THE RESET - the plan, in order
1. SKILL TREES 3 build (Skyy: "the biggest thing right now"): research/Skill-Trees-3-Spec.md + Skyy's 10 answers (end of that file): BL3-style
   rows by total points, 1 point a level, free row abilities, capstone 1 point after 25, rising coin respec + 1 free per rebirth, dust
   dropped (full points + coin refund), light skills 2x4, Void Particles one currency (keep buff +0.25% each, no cap; re-run the spend vs keep
   math), rebirths unlimited (cap stays 100). Rounds R1 engine + R2 migration together, then R3 trees, R4 Rebirth VP + Nexus.
2. BALANCE PASS P1-P9 (research/Balance-Pass-Spec.md section 8; goals in research/Balance-Goals-Questions.md + the 10-18 popup answers;
   class ratings research/Class-Roles-Sheet.md; P0 inventory DONE in research/balance/): P1 pacing model tools/balance_model.py ->
   P2 = the skill-tree engine above -> P3 XP -> P4 combat + classes -> P5 power sources (35/30/20/15, pets included) -> P6 gathering +
   crafting (incl. F-pickup tier lock + zone spawns, Zone 5 every crop but mostly its own 3) -> P7 economy -> P8 rebirth -> P9 full-run check.
3. Small queued rounds: Armory Soul Cage locks faster (Skyy 10-18: "make the soul cage lock on to a target faster"; soul.stabilize
   1.75 .. 1.0 s -> about half + migration), Classes (Sacred Heal 8 s default + migration), XP caps in Cooking / Guilds / Exploration -> 0, Enchanted alloy
   Smithing XP rows, Shards Soul Cage totem recipe (orb by item id - same bug as beta 20), per-profile world chests (SkyyExploration,
   research/Per-Player-Loot-Survey.md: refill never, sparkles), Infinite Water Bucket mid game (SkyyGear), our own bench-tier keeper,
   SkyyZones (protected areas + titles), tooltips bigger + colour coded (Style Guide 15: kit, then Pets, then every mod), Cooking ING_TIER v3,
   Rebirth "no limit" default (rebirth.max).
4. Later: UT design (12 armor sets + 32 weapons), Wynn elements build (research/Wynn-Elements-Build-Spec.md), dragon pet
   (research/Dragon-Pet-Spec.md), zone gathering spots (research/Zone-Gathering-Spec.md), Quirk's 4 tool models (fix: R-Attachment root,
   handle at origin, head along Z, ~0.75x vanilla size, Lumen gem corner texels), authors to ask (research/Structure-Mods-Survey.md),
   fishing rework.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches.
- Rollback floors + go-together rules: comments in `tools/deploy_set.py` (newest: the level-bands guard + FLOOR, 10-18).
- tools/tier_tags.py is TT_VERSION 3; old pins' build scripts assert "2" - rebuild from the current pins only.
- Private art (Quirk) lives in `..\SkyWynn-PRIVATE-art\` and is read at build time only - never in git. Untracked screenshots in
  SkyyIslands/ + SkyyWorldGen/ and TASK-crossbows-from-vanilla.md: leave alone (stage files by name).
- Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`. Menus follow research/Menu-Pattern.md. Ask Skyy in popups.

## On Skyy's PC (read-only except the deploy)
Project = this repo. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\` (`Server\HytaleServer.jar`,
`Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\Saves\NewBetaTest\` (mod data `mods\Skyy_Skyy<Mod>\`, server
logs `logs\`); client logs `...\UserData\Logs\`. Backups: `backups\` (git-ignored). Toolchain: Python 3.12 + jpype1 + jdk4py (no javac).
LOCAL ONLY, never in git: game files, UserData, backups, built jars (except `tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
