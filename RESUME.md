# SkyWynn - RESUME HERE (updated 2026-10-20 09:10 MDT; reset done - working the AFTER THE RESET list top to bottom, Skyy: "when tokens reset at 9 am work through the entire local resume list from top to bottom")

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage) - weekly was 92% on 10-18, resets 10-20 09:00. World **NewBetaTest**.
2. Rounds: while Skyy chats on other topics run builders as PLAIN Agents + your own critics (workflow builders refuse). Builders and
   reviewers read long files through Jev / free models (`tools/llm.py`); Skyy allows $10 paid OpenRouter in 2026-10 (~$1 used).
   Deploy (game closed): skill `skywynn-deploy` = backup -> `smoke_test.py --allow-pack-api` (0 SEVERE from Skyy mods) -> `deploy_set.py --yes`
   (LAST line "deployed N mods") -> `record_deploy.py` -> commit -> `tidy_local.py --yes`.
3. After Skyy plays: skill `skywynn-logs` (`python tools/log_scan.py --ours`, then `--recycle`).

## LIVE NOW (all deployed 2026-10-18; TEST-CHECKLIST 191-197, details in docs/tests/2026-10.md)
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
  Profiles 0.1.18, Menu 0.3.40, Classes 0.1.39, Quests 0.4.2, Rebirth 0.3.5, Core 1.0.1.
- 197 (deployed 10-18 18:14): SkyyProfiles 0.1.18 = bigger Create Profile class cards + emblem / primary / secondary weapon (Priest
  Wand + Soul Cage, Warrior Sword + Spear). Follow-up: SkyyClasses' /class page icons still show no Soul Cage.
- 198 (deployed 10-19 07:19): Classes 0.1.40 /class weapons + Soul Cage, Trees 0.3.25 tree text fits, Hud 0.3.33 quest widget wraps.
- 199 (deployed 10-19 12:10): Collections 0.2.29 furnace Charcoal + grid text, Mobs 0.1.13 hit cap on every mob (beta 3, 13, 16).
  Sacks 0.8.25 (off-hand refill, bug 11) built + reviewed SHIP but NOT pinned (Skyy: "skip for now").
- 200 (deployed 10-19 12:40): Islands 0.5.22 island leftovers despawn + island sky follows the hub (beta 19, 9).
- 202 (deployed 10-19 12:59): Armory 0.1.40 Soul Cage locks on ~2x faster.
- 203 (deployed 10-19 13:04): Gear 0.3.30 Copper mines Iron at full speed, no Bronze armor drops.
- 209 (10-19 18:37, pack config): Dynamic Seasons tints off in our worlds (if still a pain: disable the mod).
- 208 (deployed 10-19 14:44): Islands 0.5.24 + WorldGen 0.7.7 empty worlds unload (files kept), reload on demand.
- 207 (deployed 10-19 14:08): Sacred Heal 8 s, rebirths unlimited, Enchanted alloy Smithing XP.
- 206 (deployed 10-19 13:47): no XP caps in Cooking / Guilds / Exploration; Shards lowest-rarity orb first.
- 205 (deployed 10-19 13:27): WorldGen 0.7.6 zone landings pre-loaded, layout pick off the world thread.
- 204 (deployed 10-19 13:07): Islands 0.5.23 respawn straight onto the island (one world load).
  Nothing running, nothing pinned-but-undeployed (Sacks 0.8.25 off-hand refill built, unpinned: Skyy "skip for now").
- 201 (deployed 10-19 12:43): Hud 0.3.34 minimap picture cap (beta 4 lag part). All 5 lag suspects now handled (beta-bugs file bug 4).

## RUNNING NOW (2026-10-20; Skyy at work: "figure it out" - take defaults, research when in doubt)
- DEPLOYED 12:27 (TEST-CHECKLIST 210): Skill Trees 3 R0-R2 (Trees 0.4.0, Classes 0.1.42, Skills 0.4.55, Menu 0.3.41), Exploration 0.3.0 per-profile chests, Gear 0.3.31 Infinite Water Bucket.
- DEPLOYED 12:41 (TEST-CHECKLIST 211): SkyyEssentials 0.1.16 benches keep their tier (KeepBenchTiers + WorkbenchTierKeeper off for good).
- RUNNING: workflows st3r3a (class trees: Trees 0.4.1 / Classes 0.1.43 / Armory 0.1.41), st3r3b (skill-tree hooks in reader mods; may list FOR SKYYTREES changes to fold in), bazaar02 (SkyyBazaar 0.2.0).
- Done, not built: research/Bazaar-Order-Book-Spec.md (8 questions sec 12 -> take defaults); tools/balance_model.py + research/balance/targets.md (P1; add to INDEX + research/balance/README).
- NEXT: Skill Trees 3 R3 (wire the "coming soon" upgrades + raise gates to 0/5/10/15/20/25), then R4 Rebirth VP (strengths: targets.md 5a/5b), then Balance P3...

## FOR SKYY (while paused)
- Test TEST-CHECKLIST 196 first (the big one), then 197 (class cards), 195, 194.
- Server Setup now if wanted: Classes > Sacred Heal cooldown -> 8 (all 4 rows); Rebirth > rebirth.max -> e.g. 1000 (unlimited rebirths).
- Open choice (OPEN-QUESTIONS): Copper Staff costs 20 Mana of a 40 pool at Lv 1 (50%, over the 40% rule) - drop to 15?

## AFTER THE RESET - the plan, in order
1. SKILL TREES 3 build (Skyy: "the biggest thing right now"): research/Skill-Trees-3-Spec.md + Skyy's 10 answers (end of that file): BL3-style
   rows by total points, 1 point a level, free row abilities, capstone 1 point after 25, rising coin respec + 1 free per rebirth, dust
   dropped (full points + coin refund), light skills 2x4, Void Particles one currency (keep buff +0.25% each, no cap; re-run the spend vs keep
   math), rebirths unlimited (cap stays 100). Rounds R1 engine + R2 migration together, then R3 trees, R4 Rebirth VP + Nexus.
2. BALANCE PASS P1-P9 (research/Balance-Pass-Spec.md section 8; goals in research/Balance-Goals-Questions.md + the 10-18 popup answers;
   class ratings research/Class-Roles-Sheet.md; P0 inventory DONE in research/balance/): P1 pacing model balance_model.py (planned, in tools) ->
   P2 = the skill-tree engine above -> P3 XP -> P4 combat + classes -> P5 power sources (35/30/20/15, pets included) -> P6 gathering +
   crafting (incl. F-pickup tier lock + zone spawns, Zone 5 every crop but mostly its own 3) -> P7 economy -> P8 rebirth -> P9 full-run check.
3. Small queued rounds: Heavy combat armor has no piece at Lv 16-19 since Bronze left the bags (fill in the balance pass), Bazaar 0.2 order book must implement closeall + wouldclose for real (Rebirth relies on it; 0.1.x has no orders - checked 10-19), per-profile world chests (SkyyExploration,
   research/Per-Player-Loot-Survey.md: refill never, sparkles), Infinite Water Bucket mid game (SkyyGear), our own bench-tier keeper,
   SkyyZones (protected areas + titles), tooltips bigger + colour coded (Style Guide 15: kit, then Pets, then every mod), Cooking ING_TIER v3.
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
