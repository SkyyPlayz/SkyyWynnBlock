# SkyWynn - RESUME HERE (updated 2026-10-21 20:55 MDT; reset done - working the AFTER THE RESET list top to bottom, Skyy: "when tokens reset at 9 am work through the entire local resume list from top to bottom")

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

## RUNNING NOW (2026-10-20 evening; Skyy: "keep going down the list. dont stop until the entire list is done" - defaults, research when in doubt)
- DEPLOYED today: 210 Skill Trees 3 R0-R2 + chests + water bucket; 211 bench keeper; 212 Skill Trees R3 (class trees live, 26 skill upgrades), Bazaar 0.2.0 order book, Rebirth 0.4.0 VP, NEW SkyyZones 0.1.0.
- DEPLOYED 19:18 (TEST-CHECKLIST 213): Trees 0.4.3, Pets 0.4.6, Rebirth 0.4.1, Gear 0.3.33, Accessories 0.5.29 (skill gates, Head Start, R3c upgrades). Workbench republished.
- DEPLOYED 22:00 (TEST-CHECKLIST 214): Balance P3 XP (Lv 50 ~33 h, levels kept), Pets 0.4.7 (pet pace kept), SkyyZones 0.2.0 (ores/stone regrow; Z3 trees/crops need live probes).
- DEPLOYED 10-21 20:50 (TEST-CHECKLIST 215): Balance P4 combat - Gear 0.3.34, Mobs 0.1.14, Skills 0.4.58, Classes 0.1.44, Armory 0.1.42, Trees 0.4.4 (FLOOR: all six roll back together). Caster Mana pools re-tuned ABOVE the spec (Mage 80+14.5/lv, Priest 60+10, Spellblade 70+6; cost growth Priest 1.5 % / Spellblade 2.5 %; refill only below 20 %) so casters run dry in 20-28 s - Skyy popup 10-21: "Keep it" (docs/answered/skills.md).
- DEPLOYED 10-21 23:20 (TEST-CHECKLIST 216): P8a Skills 0.4.59 + Rebirth 0.4.2, Cooking 0.1.16, P6a WorldGen 0.7.8 + Shards 0.4.4 + Sacks 0.8.26. DEPLOYED 10-22 05:15 (TEST-CHECKLIST 217): Balance P5 - Gear 0.3.35, Armory 0.1.43, Accessories 0.5.30, Pets 0.4.8, Trees 0.4.5, Guilds 0.1.13. P6b Gear 0.3.36 also gets: level-up cap +10, UT >= Fabled, armor bags hide slot (Skyy popups 10-22), Normal-quality text #fefefe (Scribing WARN). Next Skills round: skip skyygear_hp / skyypet_health / skyypet_mana in ClassStat + RbStat.
- DEPLOYED 10-22: 218 SkyyMenu 0.3.42 (Left Alt opens the Menu), 219 P8b Trees 0.4.6 + Classes 0.1.45 + Mobs 0.1.15, 220 SkyyUiProbe 0.7 (radial tree probe - Skyy runs /skyprobe m1..m7 once, then RETIRE it), 221 P6b Gear 0.3.36 + Collections 0.2.31.
- DEPLOYED 10-22 later: 222 lean1022 (Sacks 0.8.27, Accessories 0.5.31, Menu 0.3.43), 223 P8c (Skills 0.4.60 Beastmastery, Pets 0.4.9, Trees 0.4.7).
- DEPLOYED 10-22: 224 SkyyUiProbe 0.7.1, 225 P8d (Trees 0.4.8, Rebirth 0.4.3), 226 P7 core (Coins 0.1.10, Bazaar 0.2.1, Merchants 0.1.7, Auctions 0.1.15, Gear 0.3.37 Smithing combat, Collections 0.2.32). Game Review sheet published (workbench v15).
- DEPLOYED 10-22 afternoon: 227 packprep (Gear 0.3.38, Sacks 0.8.28, Coins 0.1.11, Mobs 0.1.16) + P7b (Skills 0.4.61, Trees 0.4.9, Exploration 0.3.3, Shards 0.4.5); 228 StructureV2 + Souls like Bosses ON (merchant off via deploy_set tune_structurev2).
- DEPLOYED 10-22 evening: 229 SkyyTrees 0.5.0 radial tree pages (tools/skyymap.py + kit 1.8). P9 check done (research/Balance-P9-Check.md; Skyy: F1-F4 apply, Mana feel-test first, ~36 h first run fine).
- DEPLOYED 10-22 night: 230 SkyySkills 0.4.62 (P9 fixes) + SkyyRebirth 0.5.0 (radial Nexus). Balance pass P1-P9 DONE (balance_model --p9 --check 35 / 0; caster Mana waits for Skyy's feel test).
- Game Review v16 published (P7 + P9 live). UI plan research/UI-Queue-Spec.md (Skyy: crouch x2 folds the tracker, vanilla feed if probe OK, guide = particle TRAIL, NPC talk = bottom bar).
- DEPLOYED 10-22 late: 231 SkyyUiProbe 0.8 (/skyprobe tour - WAITING for Skyy), 232 UI R1a (Hud 0.3.35 ALT key cap + tracker fold, Menu 0.3.44 crouch choice + Stats by source, Quests 0.4.3 /quests widget).
- DEPLOYED 10-23 02:05: 233 Wynn elements (Mobs 0.1.17, Gear 0.3.39 incl. UT bands at zone end + tree combat numbers, Classes 0.1.46, Pets 0.4.10, Accessories 0.5.32, Menu 0.3.45). ART concept v1 sent to Skyy: research/cloud/ui-tiles-art/sheet.png (8 Home tiles) + research/cloud/page-emblems-art/sheet.png - WAITING for Skyy's OK, then wire tiles (SkyyMenu R5, needs probe T1) + emblems (SkyyTrees tm_ship Emblem per page).
- RUNNING 10-23 02:10: elemswords (4 Armory Elemental swords as Spellblade Mythic boss drops). NEXT: after Skyy's /skyprobe tour (TEST 231) -> R1b vanilla feed, R2 zoom scroll, R3 Quests trail + dialogue bar, R4 player heads, R5 tiles; Quirk's tool models (Skyy to answer: Quirk back or Claude makes them - needs Blockbench open); Later list: dragon pet (research/Dragon-Pet-Spec.md), zone gathering spots (research/Zone-Gathering-Spec.md, crop islands 100/300/800), UT design (12 armor sets + 32 weapons), fishing rework, SkyyZones Z3/Z4 (live probes), Powders spec.
- SPECS DONE: P6 (research/Balance-P6-Gathering-Spec.md), P7 (research/Balance-P7-Economy-Spec.md; Skyy: coins x10, idle pay stays 20-100 % / 3 days - P7 treats idle as bonus), P8 (research/Balance-P8-Rebirth-Spec.md). NEXT builds: P6b (Gear 0.3.36 + Collections 0.2.31 + Cooking 0.1.17) and P8b (Trees/Classes/Mobs) after P5 pins; P7 core after P6 pins; P8c after P8a; P8d after P8b; then P9.
- FOLLOW-UP SkyyMenu next: the Stats page shows the 5 element + 3 Raw element lines flat although Gear 0.3.35 made them % (ST_ELEM / ST_RAW groupRow, build_skyymenu_0.3.42.py ~2759 / 6323 / 6546); Alt cooldown starts even when ignored over an open page (stamp s[4] only on a real open); if Walk is a toggle on Skyy's client, also open on the falling edge.
- NEXT TREES ROUND: Wanderer + Cartographer (Exploration) get a non-XP effect (Skyy 10-22: no-boost rule wins).
- NEXT GEAR ROUND (after P7's 0.3.37): GearSmith.lockWhy reads sacks:fn:craftWhy (SkyySacks 0.8.28 BUILT, pin together) to show the real lock reason (collection tier, not the accessory); the 4 'ArmorBench' vanilla Utility recipes; pad the 28 SkyyFarming armor textures to multiples of 32 (client WARN, dev error badge) + build assert.
- NEXT GEAR ROUND: GearCfg.class not byte-reproducible (8 bytes differ between builds); vanilla Weapon_Longsword_Flame flat-hit bug like the Elemental swords had; regenerate research/Pack-Drops-Spec.md section 3 (python tools/pack_drops.py --md).
- TODO: fold the 8 abil.costPerLevel.<Class> rows into one table row once the Classes settings kit has table rows; Skills DRY/CAST maps keyed by UUID never drop quit players (small leak); TASK-crossbows-from-vanilla.md is DONE (Armory 0.1.33) - Skyy may delete it.
- QUEUED from Skyy popups 10-22 (docs/answered): next Gear round after 0.3.36 - Skeleton_Elite out of bosses.roles into the elite roles (UT, no Mythic) + craftable combat gear moves into /smithing (plain metal sets per weight + basic weapons, each craft rolls rarity at mob-bag odds up to Fabled - never UT / Mythic on ANY crafted item (drops only; Sigils on crafted gear stop below them too), bench recipes blocked, no tier-up; docs/answered/gear.md 10-22); UT / elements round - each alloy's UT band moved to the END of its zone; joszza said YES 10-22 - PACK ROUND queued per research/StructureV2-Pack-Check.md (StructureV2 now + merchant off + Structure Money -> coins (SkyyCoins) + Voidice plain; Souls like Bosses after SkyyMobs boss ranks + SkyyGear boss roles, guns removed by our code; DungeonBosses + River Bridges: 2nd ask SENT 10-22, waiting for joszza) (merchant off, money item vs SkyyCoins, Voidice weapons, bosses into Mobs ranks, overlap with MajorDungeons / AncientConstructs / YUNGs HyDungeons / Marsi_Dungeon; scratch-world test; docs/answered/world.md) - we test StructureV2 (OpenStructure + Dungeons and more Structures) on a scratch world copy with the merchant package off; Aures permission for recoloured element dragons is already given (no ask). Zone-Gathering-Spec: crop islands 100 / 300 / 800, other 9 questions default.
- UI QUEUE from Skyy's Hylterium screenshots 10-22 (research/UI-Ideas.md): illustrated picture tiles for the SkyWynn Menu hub (our art, skywynn-art skill); self-built player heads (PlayerSkin parts, runtime, no web); stats table by source (four power sources); NPC dialogue bar for quests; rebirth tree as a radial web; menu on Left Alt (study pending); cosmetics shop layout for SkyyWardrobe (real-money rules unchecked); ground guide arrows + objective / distance label for quests (SkyyQuests trail); HUD key hints (Alt menu, ability keys); quest widget fold on double crouch (check crouch-cast clash); our feed cards (kills, XP bar, Fortune, heals) inside the vanilla pickup feed; skill-tree map look (theirs is buggy - prove pan / zoom first).
- NEXT: (workbench republished 19:30) Rich Seams overshoot: Mining tree Fortune 67.5 at max vs budget 40 (Rich Seams = +10 Fortune/rank via old MFortune node, text says +2% double-ore) -> fix in P5/P6; remaining Skills-side coming-soon (actives, streaks, capstones); P4 combat+classes -> P5 power sources (+ pet XP rescale from P3, Heavy Lv 16-19 gap) -> P6 -> P7 -> P8 -> P9; SkyyZones Z2 regen + Z3/Z4; tooltips pass; Cooking ING_TIER v3; then the Later list.

- AFTER P9 (Skyy 2026-10-20): turn the Class Balance Workbench into a full GAME REVIEW / BALANCE SHEET - overview visual of how all systems connect + a click-in page per area (gathering, gear armor/tool stats + rolls, rarities side by side, pets, accessories, skills/trees, combat, economy, rebirth, zones...), covering everything the pack does (docs/answered/project.md 2026-10-20).

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
