# SkyWynn - RESUME HERE (updated 2026-10-14 ~21:50 MDT, all evening rounds deployed; waiting for Skyy's play test)

Big picture for other agents: `STATUS.md`.
Read this first, then only what the task needs. Map: `INDEX.md`. Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`. Skyy's tests:
`TEST-CHECKLIST.md`. Full history: `docs/log/2026-10.md` (2026-10-13 lines). Decisions word for word: `docs/answered/<topic>.md`.

## START HERE (new session)
0. Sessions start IN this folder (`SkyWynn PROJECT`) since 2026-10-15 (Skyy: new environment) - memory was copied to the matching
   `.claude/projects/...-SkyWynn-PROJECT/memory/`. Review PR for Skyy: SkyyPlayz/SkyyWynnBlock#14 (test list 84-116 + questions).
1. `git pull --rebase --autostash`; check usage (ccd get_usage; weekly resets TUE 2026-10-20 15:00 UTC; was 33% on 10-14).
2. NOTHING RUNNING (21:50). Evening deploys (TEST-CHECKLIST 110-116): Skills 0.4.39 + Rebirth 0.3.3 (rebirth stats, skill sounds),
   Menu 0.3.25 (settings search, Mod sounds switch, Shards admin buttons), sound pass 2 (Sacks 0.8.5, Collections 0.2.16, Coins 0.1.9,
   Accessories 0.5.14, Bazaar 0.1.12, Auctions 0.1.7, Shards 0.3.1), Gear 0.3.6 + Fishing 0.1.6 (gathering armor, pole perks), Classes
   0.1.25 + Trees 0.3.10 (Spellblade, rebirth modifier slots 3-4, Fishing tree), Islands 0.5.10 + Quests 0.3.2 (3 starter islands),
   WorldGen 0.6 (zones as floating islands in skywynn_zones, Zone 5 Onyxium). SKYY TESTS FIRST: checklist 84-116 + both logs.
   AFTER the test (Skyy's order: "hold off on the others till after testing"): Cooking remap to 0.7 foods (answered), sound4 (Classes /
   Trees / Quests / Exploration / Bank / Islands / Pets / Armory honour settings:sounds), classes / trees into Rebirth PARTS, Spellblade
   follow-ups (SkyySkills Battlemagic row, Menu / Profiles class card, Gear weapons + imbue, Hud Momentum), Server Setup 16-category cap
   (Menu), Onyxium collection (Collections) + Zone 5 mob levels (Mobs), island 3 mini boss + portal, load test 50 / 200, shards 7b, quest
   shard giver, Whirlwind Dash + armory nodes, SkyyZones server protection (2 modes FULL / SKYBLOCK, docs/answered/world.md
   2026-10-15: update research/cloud/Zone-Regen-Spec.md first, then ultracode), WeaponCustomHUD try-out (ui.md 10-15), rebirth switch-on test, architecture merge LAST, release. Big picture: STATUS.md.
3. Rounds: saved workflow `skywynn-round` (Skyy's OWN words in args.quotes); deploy only with the game closed: backup -> smoke
   (`--allow-pack-api`) -> deploy_set --yes -> record_deploy -> commit -> tidy_local. Scan logs + `tools/chat_digest.py` after play.
4. When Skyy says the game is UPDATING: stop every builder / smoke at once (memory skywynn-game-update-lock).

- **15:45:** DEPLOYED today (TEST-CHECKLIST 117-134): Gear 0.3.7-0.3.9, Accessories 0.5.15, Hud 0.3.25-0.3.26, Sacks 0.8.6, Shards 0.3.2 + 0.4, Quests 0.3.3,
  Islands 0.5.11-0.5.14, Trees 0.3.11-0.3.15, Mobs 0.1.9, Armory 0.1.26-0.1.27, Menu 0.3.26-0.3.28, Skills 0.4.40-0.4.41, Cooking 0.1.7, Classes 0.1.26-0.1.27,
  Essentials 0.1.10, Pets 0.2.7, Collections 0.2.17, Profiles 0.1.14, Bazaar 0.1.13, Auctions 0.1.8, Merchants 0.1.5, Party 0.1.8, Guilds 0.1.9,
  Exploration 0.2.10, Vault 0.1.7, Bank 0.1.13 + The Armory 1.23.0 back on, Extended Backpacks / Tainted Roots off. ALL 7 HUBS have tabs (H1-H3).
  RUNNING: core10 (SkyyCore 1.0 + Bank / Party pilots + module assemble tooling; merge phase 1). OPEN-QUESTIONS has 5 new (tabs merged?, scrolling,
  gather anvil-only, The Armory jump conflict, Sap Tapper credit). NEXT: H8 reduced menu, H4-H7 (Sacks / Wardrobe / Gear / Accessories v2), merge phases 2/3/8.
## 2026-10-15 ~22:30: weekly limit hit, Skyy RESET it ('i reset limit') - armory0128 resumed, Islands review resumed; list below = state at the stop
- **Deploy target is now the world NewBetaTest** (tools/deploy_set.py WORLD). Deployed 20:56: Sacks 0.8.7, Islands 0.5.15, Exploration 0.2.11, Accessories 0.5.16, Classes 0.1.28, Trees 0.3.16.
- **PINNED, NOT DEPLOYED (deploy with the game closed: backup -> smoke -> deploy_set --yes -> record_deploy):** Sacks 0.8.8, Skills 0.4.42, Pets 0.3.0, Collections 0.2.18 (+ tools/tier_tags.py, tools/ci/langdup.py), Wardrobe 0.2.2, Accessories 0.5.17, Hud 0.3.27 + Profiles 0.1.15.
- **BUILT, needs its review then pin:** Gear 0.3.10 (review was running), Islands 0.5.16 (natural cave + respawn delay; review died at the limit), Classes 0.1.29 (Assassin Crude Kunai; review running).
- **INTERRUPTED by the limit (files may be partial - check, then relaunch / SendMessage the agent):** menuu1 (Unified menu: kit skyyui 1.6 + Menu 0.3.29; tools/skyyui.py has UNCOMMITTED edits from it), wg07 (WorldGen 0.7 shape / islets / waterfalls / natural edges), armory0128 (Spellblade Crescent Rush + sword guard + early damage; never started building), skills0443 (health regen + Spellblade Battlemagic class-skill slot - IMPORTANT bug), pets031 (boost every rarity ~3x), coll0219 (rubble <-> cobble recipes).
- **Queued after those:** gear0311 (sickle fiber/sticks + pole in kit, no-tackle fishing + Smithing UPGRADE tab: every tier-up-able item in one list + FEWER STICKS by default (leaves / felled trees; find what drops + doubles them; sickle keeps the better yield) + SkyyFishing: no Wooden Reel (rod has one), Copper Reel without it; check the craftable Wooden Fishing Rod vs the one-per-profile lifelong pole, gear.md 10-15), watering can + Harvester + tier tags T2 (Gear), Great Shield (Armory), wg071 (zones weather fix + Zone 1 = server spawn + /zone setlanding in zones world), Menu 0.3.30 (Invite to Guild), health regen Gear/Trees halves.

## Now (2026-10-15)
- **Skyy play-tested a fresh Mage profile 10-15** (notes in docs/answered/*.md 2026-10-15). DEPLOYED 06:35 (TEST-CHECKLIST 117):
  Gear 0.3.7 (hotbar summons, iron tier speed), Accessories 0.5.15 (ItemLevel sort), Hud 0.3.25 (contrast, cards, editor rows).
  BUILDING: Sacks 0.8.6 (felled-log pickup + pocket-craft veto), workflow start033 (Quests 0.3.3 early progress + merged gather task,
  Islands 0.5.11 cave mouth, Trees 0.3.11 replant), Shards 0.3.2 (totem texture WARNs). QUEUED: isle2 (camp skeletons, Shardkeeper boss,
  portal, respawn on island; Islands after start033), sapling drop chance (both, island-only once SkyyZones works), caster speed tiers
  (Gear + Armory), TREE buttons for Fishing / Alchemy / Smithing, ability tree redesign spec (research/Ability-Tree-Redesign-Spec.md,
  in progress), menu icons (session own-skywynn-icons, Menu 0.3.26), totem forms (skills.md 10-15), PROBES DONE 10-15 (coreprobe C1-C3 PASS, sky kit all answered, k1b = no textures outside Common/UI/Custom): hubs H1 building -> H2 Menu hub defs -> H3 tabs; then SkyyCore 1.0 (phase 1; shares tools/skyyui.py so after H1); remove STABLE_PROBES from deploy_set after Core lands. OLD NOTE: MERGE phase 0 probes (coreprobe building; then Skyy runs /coreprobe + /skyprobe kit in ONE session -> SkyyCore 1.0 with module assemble tooling + hub rounds; Skyy 10-15: usage not a gate, keep modules separate for parallel work), ABILITY TREE R2+R3 (workflow abiltree2 running), PER-SHARD MENUS (skills.md 10-15: right-click the placed shard on your island, one menu per shard, hidden off-island - Shards + Menu round). DEPLOYED 06:44 (TEST-CHECKLIST 118): Sacks 0.8.6 + Shards 0.3.2.

## Now (2026-10-14)
- **Game: Hytale 0.7.2** (hotfix 10-15: goblin beacon crash, Backpack Upgrade II recipe; crosscheck READY 35 jars; smoke when the
  game is closed). 0.7.1: Skyy reinstalled 10-13; UserData kept; full backup at `C:/Users/SkyLo/Desktop/Hytale-Backup-2026-10-13`).
  crosscheck READY, all 33 jars. Our tools read cached copies of the server jar + Assets.zip (`tools/serverjar.py`, ~4 GB / version).
- **Deployed 2026-10-13 (TEST-CHECKLIST 72-83, all untested):** Skills 0.4.33 Mana 3.3/s; Accessories 0.5.13 tab order; Pets 0.2.4 attacks
  pass through; Profiles 0.1.12 rename + Class Name + admin no cap; Sacks 0.8.2 /pdadmin rarity; Bank 0.1.10 + Menu 0.3.20 names; Quests 0.2
  (skip, optional tasks, class gear rewards, hub areas, co-op, feed only); Gear 0.3.0 lifelong tools; AUTO-PICKUP Sacks 0.8.3 + Mobs 0.1.7;
  chat -> feed (Skills 0.4.34, Classes 0.1.20, Collections 0.2.12; 116 -> 20 lines / 12 min); Hud 0.3.22 per-player routes; Menu 0.3.21
  Messages tab + Classes 0.1.21 ability route; BetterMap 1.3.9 / DynamicSeasons 7.0.2 / Perfect Parries 0.9.7 back ON; Gear 0.3.1 tool
  speed (Crude = T1, one tier up 2.5x hits, two up 10x, 3+ refused).
- **Deployed 2026-10-14 06:00 (TEST-CHECKLIST 84-86, untested):** Sacks 0.8.4 + Mobs 0.1.8 harvest to Void (pet kills idle until SkyyPets
  publishes pets:fn:ownerOf); Gear 0.3.2 /pickaxe etc. summon the EXACT tool (else exact copy); Trees 0.3.6 Vein Mine / Tree Feller perks.
  06:26 Skills 0.4.35 + NEW SkyyRebirth 0.1 (rebirth R1+R2, feature OFF; /rebirth Nexus page for admins; half Farming XP above tool
  tier). Keep Rebirth OFF until Skyy has seen the Nexus tooltip (then add "tooltip" to skyyui.PROBED). 9 new questions in
  OPEN-QUESTIONS (gear, bags, rebirth), defaults live.
- **Deployed 2026-10-14 08:35 + 11:04 (TEST-CHECKLIST 88-97, untested; combined smoke 35/35):** Gear 0.3.3 harvest gate (88);
  Pets 0.2.5 owner key; Bazaar 0.1.11 + Auctions 0.1.5 closeall; Vault 0.1.6 fetch hook; Exploration 0.2.8 Lost Loot looks + reveal
  + supply drops; REBIRTH R3 (Rebirth 0.2, Skills 0.4.36, Coins 0.1.7, Bank 0.1.11, Profiles 0.1.13; feature OFF); NEW SkyyShards 0.1
  + Islands 0.5.8 + Menu 0.3.22; ABILITIES IN THE TREE (Classes 0.1.22 + Trees 0.3.7, Mage + Priest on rune keys, panel, levels +
  modifiers; U1-U10 unproven - scan logs after Skyy plays); Quests 0.3 + Hud 0.3.23 + Fishing 0.1.4; Sigils + armor levels + hoe area
  (Gear 0.3.4, Armory 0.1.24, Collections 0.2.13). Research today: Economy-Audit-1014, Sound-Pass-Plan, Load-Test-Plan,
  Structure-Mods-Survey, Release-Packaging-Plan (+ tools/release_pack.py), Admin-Page-Plan. Release blocker: 4 jars hold edited vanilla
  JSONs (Skills / Armory / Gear / Trees) - Skyy decides redistribution.
- **Rebirth spec FINAL:** `research/cloud/Rebirth-Spec.md` (all 16 answers + ability levels kept with a soft cap, dust x2 per rebirth ...),
  build order R1-R10 (section 6). R1 + R2 = the interrupted rebirth12 round.
- Skyy to do: run `/aprobe` (Mage keys) and `/skyprobe kit` (Sky Window kit) in game; set the 4 quest hub
  spots (`/questadmin place set hub.mining | hub.foraging | hub.farming | hub.fishing`); test 72-83; Grok video notes from WED.
- Still broken on 0.7 (switched off): Saplings From Trees, TheArmory, HyFishing, Better Mob Expansion - recheck CurseForge; after
  2026-10-19 build our own / fork where the licence allows (docs/log 2026-10-13 pack check).

- **15:xx queued:** menuu1 = Unified menu round (kit 1.6 + Menu 0.3.29: Home overview + shortcut grid + hub row; research/Unified-Menu-Plan.md) BUILDING; tab-icon art BUILDING;
  gear0311 (Skyy test fix, FIRST after Gear 0.3.10): the sickle breaks bushes / grass / leaves and is the main fiber + stick tool (gear.md 10-15); + the lifelong fishing pole in the starting kit, fishing works with no hook / line / sinker, quests teach tackle (gear.md 10-15; SkyyFishing 0.1.6 + SkyyQuests too).
  WATERING CAN + HARVESTER (research/Watering-Can-Harvester-Spec.md) = full SkyyGear round AFTER Gear 0.3.10 lands; Class tab -> tree (class0128) BUILDING; Wardrobe 0.2.2 in review.

- **Queued after wg07 (WorldGen 0.7.1):** zones world weather list (vanilla SensorWeather NPE) + 'Zone 1 = server spawn' switch (first join, /spawn, no-island -> Zone 1 landing; world.md 10-15); /zone setlanding must work in the zones world too (0.6 refuses: 'no landing point to set'), so Skyy can pick the Zone 1 spawn spot. After Gear 0.3.10: gear0311 (sickle fiber, pole in kit), then watering can + Harvester + tier tags T2. Profiles: open / redraw the first-profile page ~2 s after join.

- **Queued (Skyy 10-15):** HEALTH REGEN - SkyySkills 0.4.43 (after 0.4.42): base 0.2 HP/s in combat / 1 HP/s after 5 s out, + per Overall Level, Stats row, bridge for gear / tree adds; then Gear / Accessories 'Health Regen' stat + Trees nodes (skills.md BASE HEALTH REGEN).
- **Queued (Skyy 10-15 'Both'):** SPELLBLADE GREAT SHIELD (research/classes/Spellblade.md: bash chain, full guard 70% melee / 100% projectiles, Bulwark Charge) = the SkyyArmory round right after armory0128 (sword guard + Crescent Rush + early damage).
- **Queued for SkyyMenu after menuu1 (0.3.30):** player action page 'Invite to Guild' button (slot 33 next to Invite to Party 32; cmd 'guild invite %P'; shown only while the viewer is in a guild and may invite) (social.md 10-15).
- **Later (review note):** SkyyBazaar's price guard (Catalog.EDGES) should also read our standalone Server/Item/Recipes/Skyy*/ recipes (e.g. the 0.2.19 rubble <-> cobble ones) so an admin price edit cannot open a loop.
- **Follow-ups from Skills 0.4.43 (Battlemagic slot + health regen):** SkyyMenu needs 'Battlemagic' in CLASS_SKILLS (~line 1060 of 0.3.28) and a Stats MAIN row 'Health Regen' from skill:fn:hpregen {"row", u}; SkyyGear needs the ("Spellblade","Battlemagic") class-skill pair and its hpr / hprp + Accessories Regeneration should move onto skill:fn:hpregen (no double heal); Trees health-regen nodes; P25_HIT Mana-on-hit for Spellblade = Skyy's call. SkyyCollections maskOf: drop the Ingredient_Fabric_Scrap_ prefix from the Smithing bit (fabric is Combat since Sacks 0.8.9). Also: SkyyPets POLL_SKILLS (~434 of 0.3.1) lacks Combat.Spellblade; SkyyGuilds SKILL_NAMES / SK_SLOTS (~5367 of 0.1.9) stop at Priest.
## Next, in order (Skyy 2026-10-14: "Run everything you can in parallel ... done by 5 pm")
1. Land the 6 running rounds (deploy each READY one with the game closed), then the queued ones above.
1b. OWN ICONS IN EVERY MENU (Skyy 10-15, ui.md; plan research/Menu-Icons-Plan.md): wave 1 sheet art/menu-icons-2/ DRAWN + reviewed (14 icons: Teleport My Island / Hub / Spawn / Warp / locked / none, Back / Prev / Next / Close, Player, Accept / Deny, Shards tile).
   QUEUED: lean round menu0326 = SkyyMenu 0.3.26 wires them (art/menu-icons-2/README.md: ICON_ITEMS, ICON_* constants + new ICON_WARP_LOCKED / ICON_NO_WARPS, ENTRIES tp 11/13/15, players 47/51, main 11; the asserts at ~1177 / 1212 / 2111 / 11186).
   Then waves 2-5 (Mods list + player actions, shared skill / class sets, Exploration / Quests / Hud, Trees nodes) - each drawn, reviewed, then a round once that mod is free.
2. Sky Window kit into tools/skyyui.py - BLOCKED on Skyy's /skyprobe kit; ability keys U1-U10 proven by Skyy's first Mage play + logs.
3. ARCHITECTURE merge into ~10 jars (research/Architecture-Spec.md) LAST - it touches every mod, so only when no other round runs;
   fold MIT mods (Multitools, Reforged Weapons, MoreTotems Water Totem, BetterBiomes, More Mounts) with credit.
4. Release: Skyy's call on the edited-vanilla JSONs + third-party permissions (research/Release-Packaging-Plan.md), then release_pack.
5. Parked specs: gems, inventory buttons / offhand, upgrade ladders, pet eggs v2; guide fairy (SkyyPets 0.4 with fighting pets).

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
