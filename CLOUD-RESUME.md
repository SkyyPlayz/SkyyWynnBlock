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
- [ ] **Tool levels revision** (local session 2026-10-06, Skyy's request - do first) - revise research/Tool-Levels-Spec.md with
      docs/answered/gear.md 2026-10-05: speed + Mining / Foraging / Farming Fortune by tool level, tool rarities + rolls + reforges, modifier
      list incl. SICKLE RANGE, axes get Tree Feller (reuse SkyyTrees' Tree Feller), tied to research/cloud/Gathering-Tiers-Draft.md.
      Output: `research/cloud/Tool-Levels-Revision.md`.
- [ ] **Armor types spec draft** - docs/answered/gear.md 2026-10-05: Heavy / Light / Cloth ladders (Heavy = heavy leather then vanilla
      metal; Light = vanilla leather then leather + metal upgrades; Cloth = Crude Robe then tunics), per-level Health / Defense next to
      research/Mob-Curve-Spec.md, trade-offs (anyone) vs class bonuses (on-type) with numbers, recipes per tier.
      Output: `research/cloud/Armor-Types-Spec-Draft.md`.
- [ ] **Weapon speed tiers** - Skyy 2026-10-05: weapon speed tiers Slow / Medium / Fast / Super Fast with the same DPS (per-hit damage scales).
      Assign every weapon type of `research/cloud/SkyyArmory-Roadmap.md` section 5 a tier, compute per-hit multipliers from attack times (keep
      the engine values UNVERIFIED), and show how crits, Strength, Mana-per-cast and on-hit effects scale. Output: `research/cloud/Weapon-Speed-Tiers.md`.
- [ ] **Foraging armor ladder** - docs/answered/gear.md 2026-10-05: tier 1 vanilla Wood armor, then the Farmer's Workbench wood ladder (Softwood to
      Goldenwood, 7 tiers echoing Copper to Onyxium), Foraging Fortune + chopping speed + Foraging XP, Tree Feller on higher tiers. Design the 7 tiers:
      stats per tier, recipes (read `research/cloud/Gathering-Tiers-Draft.md`), set bonus idea, level bands. Output: `research/cloud/Foraging-Armor-Design.md`.
- [ ] **Capstone sets** - the Set rarity (green) drops only in the capstone (Capstone-Dungeon-Spec 5). Design 3 sets (3 pieces each, Voidglass and
      Aetherium tiers, one per armor type): names, lore lines in the Department voice, the 2-piece / 3-piece bonuses within the SkyyGear stat catalog
      (read-only). Output: `research/cloud/Capstone-Sets.md`.
- [ ] **Economy faucet / sink audit** - read every `research/cloud/*.md` spec and `research/Server-Setup-Research.md`; list each coin faucet and sink with
      a rough size per hour, check the R3 rules, the Bazaar loop (22.2% rule), the Tab (20M per day), prestige. Flag anything that breaks. Output:
      `research/cloud/Economy-Audit.md`.
- [ ] **Hytale 0.7 research** - web research (snippets): what is announced or released for Hytale 0.7 and later (mods API, UI, items, worldgen, combat).
      Compare against `research/PreRelease-Compat-Audit-1002.md` and list likely breaks for our mods. Output: `research/cloud/Hytale-0.7-Watch.md`.
- [ ] **New-player guide** - a plain English "your first hour on SkyWynn" guide for players (what to do, where, what the menus are): tutorial flow from
      Story-Script-Draft, starter shards, the first outpost, classes, bags, the Board. Players, not admins. Output: `research/cloud/Player-Guide-First-Hour.md`.
- [ ] **NPC barks, signs and Board texts** - short ambient lines in the Department voice: 6 barks per town NPC type (clerk, banker, smith, guide, guard,
      shopkeeper), 40 signs, 20 Board announcements (for Zone Specials), 20 loading-screen tips. Output: `research/cloud/Barks-Signs-Tips.md`.
- [ ] **Mining and Farming gathering armor** - Foraging armor is designed (task above); do the same for Mining (Fortune, mining speed) and Farming
      (Fortune, sickle range, crop XP): tiers, materials from `research/cloud/Gathering-Tiers-Draft.md`, stats. Output: `research/cloud/Gathering-Armor-Mining-Farming.md`.

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->
<!-- 2026-10-02 local session: 'Skill-tree pass 2 notes' removed - the local research/Skill-Trees-2-Spec.md covers it. -->

## Done (delete after logging - see the rules above)

- [x] Accessory acquisition - 2026-10-06 - `research/cloud/Accessory-Acquisition.md`
- [x] Prestige system spec - 2026-10-06 - `research/cloud/Prestige-Spec.md`
- [x] Zone specials / mayor lite - 2026-10-06 - `research/cloud/Zone-Specials-Spec.md`
- [x] SkyyArmory roadmap - 2026-10-06 - `research/cloud/SkyyArmory-Roadmap.md`
