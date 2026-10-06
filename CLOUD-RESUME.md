# CLOUD-RESUME - rolling to-do for cloud sessions

Work a cloud session can do while the local session waits (usage limits, Skyy away). Started 2026-10-02.

## How this file works (read every time)

- **Rolling list:** do the top open task, then mark it `[x]` with the date and the output file. When you open this file and see `[x]`
  items, first add one line per item to `research/cloud/LOG.md`, then DELETE those items here and top the list back up to about 8
  open tasks (ideas: RESUME.md 'Next', OPEN-QUESTIONS.md (open only), the plans in `research/` + `docs/plans/`). Keep this file under ~110 lines.
- **Cloud limits:** no access to Skyy's PC, the Hytale game files (`HytaleServer.jar`, `Assets.zip`), installed mods or the test world.
  You cannot build, test or deploy. Only add tasks that need none of that. Any fact you cannot check without the game files: mark it
  **UNVERIFIED** and list it under "For the local session" in your output.
- **Where results go:** new files in `research/cloud/` (one file per task). You may push straight to `main` ONLY changes to this file and
  to `research/cloud/` (always `git pull --rebase --autostash` first). Any change to another file goes through a pull request.
- **Never touch:** build / patch scripts, `tools/deploy_set.py`, jars, `SkyyGear-Plan.md`, `SkyyGear-Stat-Catalog.md`.
- Follow `PROJECT-RULES.md`. Skyy uses they/them. Plain English, tables, short.

## Open tasks (top = next)

<!-- 2026-10-03 local session (Skyy: "make sure the cloud agent has a good list to work on, so i can keep em going when token limit runs
out"): the list is LONG ON PURPOSE this week - work top-down; the first 8 feed builds the local session runs next. Decisions behind them:
OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02" block, 2026-10-03 lines. -->
<!-- 2026-10-05 15:30 UTC (Skyy): WAIT FOR THE USAGE RESET (TUESDAYS 15:00 UTC = Tue 2026-10-06 per the app's usage card; the 2026-10-05 "Mondays" fix was wrong) before any new work. After it: the local session runs the
RESUME 'Next' build list (Gear 0.2.3 first); cloud sessions then do the no-game-files specs - build 5 traversal spec (SkyyArmory 0.1.1 +
SkyyClasses 0.1.12), the Stats page spec (task below), the class-ability spec. Docs consolidation PRs #6 + #7 are merged. -->
<!-- 2026-10-05 cloud session: the docs consolidation is DONE in a pull request (Docs consolidation map + README draft tasks removed);
OPEN-QUESTIONS.md now holds only open questions - every answer (incl. the 'Q&A with Skyy 2026-10-02' / 'LOCKED 2026-10-04' lines named below)
is word for word in docs/answered/<topic>.md; map of everything: INDEX.md. -->
<!-- 2026-10-05 local session (Skyy: "make sure the cloud agent has a good list to work on while tokens are out"; local weekly usage 94%, resets Mon
2026-10-06 15:00 UTC). The first 9 feed the next local rounds; the class design is in research/classes/ (one file per class + README rules),
Skyy's locks are in OPEN-QUESTIONS 'LOCKED 2026-10-04'. Removed as done / superseded: Wynncraft level-curve research (research/Mob-Curve-Spec.md),
Lantern design (SkyyAccessories 0.5.4 is live), Class tree texts (replaced by per-ability trees + paths), Tool progression research (research/Tool-Levels-Spec.md). -->
<!-- 2026-10-05 evening local session (Skyy: "if you need more research done, put it on the cloud agents list. im going to start it now"):
the 4 GATHERING PROGRESSION tasks below come FIRST - Skyy's big direction (docs/answered/bags.md 'LOCKED 2026-10-05 ... BIG DIRECTION'):
SkyBlock-style ladder for Farming / Mining / Foraging, collection levels unlock the next tier's recipes, compressed Enchanted materials,
trees grouped into few tiers. Also read docs/answered/gear.md 2026-10-05 lines (Foraging armor, tool levels, armor types) and
docs/answered/economy.md 2026-10-05 lines (Tree Sap, Lantern behind the Sap collection). Removed as done locally 2026-10-05: Bazaar
progression prices (SkyyBazaar 0.1.4 live), Skill curves + Cooking XP (SkyySkills 0.4.16 + SkyyCooking 0.1.6 live). -->
- [ ] **Stats page spec (SkyBlock-style "Your Profile" stats)** - Skyy 2026-10-03 (playing, screenshot of the SkyWynn Menu's Your Profile
      tile): "this menus should show me all my stats with my current gear, accessory's skill and class bonuses. and everything. like on
      skyblock it should show health, mana, stamina, strength, crit chance, crit damage, mining and foraging fortune. ect. pretty much all
      the stats." Today the tile shows purse / bank / skill levels / bag counts and its text is cut off ("Skills: Mining 6, Forag...").
      Design a vanilla-look Stats page (Your Profile -> Stats; tools/skyyui.py + research/Vanilla-UI-Style-Guide.md): every stat with its
      live total and a per-source breakdown on hover (gear worn + held, accessories, skills, class, trees, food buffs, base). Inventory the
      stats each mod really has from the build scripts (SkyyGear stat keys + GearFx, SkyyAccessories effects, SkyySkills skill / class
      bonuses + /skills stats, SkyyClasses, SkyyTrees tree:fn:bonus nodes, SkyyCooking buffs, vanilla Health / Mana / Stamina / armor),
      which exist today vs later (Mining / Foraging / Farming Fortune, Mining / Chopping Power from the tool-levels spec), SkyBlock's stat
      list for comparison, and a bridge contract (each mod publishes e.g. stats:contrib:<Mod> with plain java types; SkyyMenu sums and
      draws), build parts + versions. Output: `research/cloud/Stats-Page-Spec.md`.
- [ ] **Zone islands layout (one world)** - Skyy: every zone island in ONE world so you see Zone 2 from Zone 1; islands ~3x bigger, random
      coastline, a mountain rising to the middle, vanilla features (rivers, caves, goblin camps), harder biomes toward the middle as a tendency.
      Design sizes, distances, heights, hub town + temple, portal + guardian spots, travel, anti-bridging / anti-flying rules, view-distance
      notes. Read research/SkyyWorldGen-Plan.md. Output: `research/cloud/Zone-Islands-Layout.md`.
- [ ] **Starter shards plan 2** - Skyy: the /island becomes 3x bigger with a small hill, more trees and a cave, a bridge to a 2nd island with
      mobs, a 3rd island with the portal (boss later). Turn research/cloud/Starter-Shard-Layout.md into a buildable plan: sizes, cave, bridge,
      shard-2 mob list (Zone 1 Lv 1-3), portal plaza, resource budget, options for islands that already exist. Output: `research/cloud/Starter-Shards-Plan-2.md`.
- [ ] **Loot box design** - unidentified drops become Wynncraft-style rarity loot boxes ("better looking"): box colours per SkyyGear rarity,
      names ("Unidentified Sword"), a level RANGE (Skyy's pick), tooltip mockups, identify messages, art direction for the generated art.
      Read research/Loot-Unid-Spec.md. Output: `research/cloud/Loot-Box-Design.md`.
- [ ] **Minimap widget UX** - our own minimap becomes a SkyyHud widget that needs BetterMap and reuses its map (DapperMap lagged: its tick ran
      40-57 ms on the world thread). Design the settings Skyy liked in DapperMap (zoom, size, circle / square, rotation, refresh speed,
      resolution, markers, colours; NO info panel), HUD-editor placement, defaults, a performance budget, marker throttles. Design only - the
      local session checks engine + licences. Output: `research/cloud/Minimap-Widget-UX.md`.
      UPDATE 2026-10-05: probe 0.4 results in docs/log/2026-10.md (2026-10-04 MINIMAP PROBE RESULTS): pictures + round mask work, the client keeps them across world changes, engine map tiles are 96 px -> downscale; widget = its own HUD key.
- [ ] **SkyyQuests design** (OPEN-QUESTIONS: "quest hooks ship with SkyyQuests"). The story scripts need a quest system that does not exist: quest steps and flags per
      profile, NPC dialogue windows (vanilla look), objectives (kill / collect / craft / reach / talk), rewards, quest log page, bridge keys other mods can call. Read
      `research/cloud/Story-Script-*.md`, `Dragon-Quest-Spec.md`, `tools/PROFILES-CONTRACT.md`. Output: `research/cloud/SkyyQuests-Spec.md`.
- [ ] **Outposts list** - LOCKED R9: about 30-35 outpost towns, one per biome group, each an unlockable warp. List every outpost per zone (shared between near-identical
      biome variants) with name, biome, ring, what it sells, warp rules. Read `research/cloud/Mob-Levels-Refit.md`, `research/SkyyWorldGen-Plan.md`. Output: `research/cloud/Outposts-List.md`.
- [ ] **Slayers spec** (`docs/plans/SkyyDungeons-Plan.md`: core loop, not the spine) - research Hypixel Slayers on the web, propose SkyWynn slayer quests per zone (boss, tiers, rewards,
      XP, anti-farm). Output: `research/cloud/Slayers-Spec.md`.
- [ ] **Capstone dungeon spec** - the one endgame dungeon after Zone 4/5 (`docs/plans/SkyyDungeons-Plan.md`, Decisions row 7.5): research Hypixel Catacombs / Wynncraft raids, propose floors,
      rooms, bosses, party size, scaling, rewards. Output: `research/cloud/Capstone-Dungeon-Spec.md`.
- [ ] **Accessory acquisition** - Accessories are admin-give only today ("drops / chests later", docs/log/2026-09.md 2026-09-30). Propose how players earn the booster accessories:
      zone chests, boss drops, event tokens, shop, crafting; per rarity. Read `docs/plans/SkyyAccessories-Plan.md`, `research/Booster-Accessories-Spec.md`. Output: `research/cloud/Accessory-Acquisition.md`.
- [ ] **Prestige system spec** from `research/cloud/Tab-Economy.md` section 5: what resets, what is kept, perks, caps, the ticket number joke, per-profile storage. Output: `research/cloud/Prestige-Spec.md`.
- [ ] **Zone specials / "mayor lite"** - rotating global buffs announced by the Board (Elites-Events-Spec 2.5): research SkyBlock mayor perks, propose a small rotating-buff system with
      rows, schedule and anti-stacking. Output: `research/cloud/Zone-Specials-Spec.md`.
- [ ] **SkyyArmory roadmap** - Skyy named a new content mod SkyyArmory (2026-10-02): our own weapons and armor, starting with metal
      Priest wands made by recolouring the vanilla Wood Wand (same model, new texture, like the vanilla Rotten Wand; OPEN-QUESTIONS Q&A).
      Propose the next items per class (Mage / Archer / Warrior / Berserker / Priest) and our own Lv 50-100 tiers: names, tier ladder,
      which vanilla model each could reuse, stat identity per class (Wynncraft-inspired, web research). Output: `research/cloud/SkyyArmory-Roadmap.md`.

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->
<!-- 2026-10-02 local session: 'Skill-tree pass 2 notes' removed - the local research/Skill-Trees-2-Spec.md covers it. -->

## Done (delete after logging - see the rules above)

- [x] Class ability spec draft - 2026-10-06 - `research/cloud/Class-Ability-Spec-Draft.md`
- [x] SkyBlock gathering progression research - 2026-10-06 - `research/cloud/SkyBlock-Gathering-Progression.md`
- [x] SkyWynn gathering tiers draft - 2026-10-06 - `research/cloud/Gathering-Tiers-Draft.md`
- [x] Collection unlocks draft - 2026-10-06 - `research/cloud/Collection-Unlocks-Draft.md`
- [x] Enchanted materials draft - 2026-10-06 - `research/cloud/Enchanted-Materials-Draft.md`
- [x] Modifier pool spec - 2026-10-06 - `research/cloud/Modifier-Pool-Spec.md`
- [x] Class tree paths - 2026-10-06 - `research/cloud/Class-Tree-Paths.md`
- [x] Soul Orb spec - 2026-10-06 - `research/cloud/Soul-Orb-Spec.md`
- [x] Monk kit spec - 2026-10-06 - `research/cloud/Monk-Kit-Spec.md`
- [x] Pocket Dimension release kit - 2026-10-06 - `research/cloud/PocketDimension-Release-Kit.md`
