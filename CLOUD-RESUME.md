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
- **Reminder (local session 2026-10-06):** commit 1cc3116 edited `research/Booster-Accessories-Spec.md` straight on main - accepted
  this once, but files OUTSIDE `research/cloud/` and this file always go through a pull request.
- **Before every push (local session 2026-10-06):** run `python tools/docs_check.py` - it must print OK (needs only git + Python).
  Write file mentions as FULL repo paths (e.g. `research/classes/Monk.md`, never the bare file name); a planned output of a task named here is fine.
- **Every draft:** start with the decisions it follows (docs/answered/<topic>.md lines), end with "Questions for Skyy" (each with a
  recommended default) and "For the local session" (every UNVERIFIED item needing Assets.zip / HytaleServer.jar). Don't re-decide LOCKED lines.
- **Agents (Skyy 2026-10-06):** you may use sub agents - for research fan-outs AND for programming (drafting code in PRs). Always pick the
  right agent + effort for the job, as good as possible without wasting tokens: Haiku for tiny lookups, Sonnet for research / reviews /
  straightforward drafts, Opus for code and hard specs, Fable only where it is clearly necessary (hardest spec synthesis / engine design).
  Name the model per agent. Code you write cannot be compiled or tested here (no HytaleServer.jar) - mark it UNTESTED in the PR.
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

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->
<!-- 2026-10-02 local session: 'Skill-tree pass 2 notes' removed - the local research/Skill-Trees-2-Spec.md covers it. -->
<!-- 2026-10-06 local session: Skyy reviewed every concept sheet (answers word for word: docs/answered/gear.md + pets.md, 'cloud art review'
lines). These ART REDOS come first. Vanilla density (Assets.zip, checked locally): armor model textures Mithril Chest 192x64, Head 160x64,
Legs 128x64, Hands 64x64; item icons 64x64; Rabbit creature texture 160x160, model icon 128x128. Keep the old sheets as *-v1.png. -->
- [ ] **Light armor v2** - 2x-4x the detail (at least vanilla density); half-mask cowl helmets: Copper + Iron plain cowl, Thorium..Onyxium keep the
      half mask but echo each vanilla metal helmet (Mithril gets the vanilla Mithril helmet wings). Output: `research/cloud/light-armor/` v2 sheets.
- [ ] **Weapons v2** - 2x-4x detail; richer spellbook covers; soul cage reworked (floats above the palm; note for local: slow cage spin around the
      soul = engine animation check); claws = long straight Wolverine-style knuckle blades, black part reads as black leather. Output: `research/cloud/weapon-art/` v2.
- [ ] **Mining armor v2** - starts at COPPER (drop the T0 Miner's Leather); Iron and up echo the vanilla metal armors more (not recolours of one outfit);
      2x-4x detail. Output: `research/cloud/gathering-armor-art/mining-sheet.png` v2.
- [ ] **Foraging + Farming detail pass** - 2x-4x detail on both sheets; Goldenwood helmet echoes the vanilla Mithril helmet; farming v2 look unchanged.
      Output: the two sheets v2.
- [ ] **Pets v2** - Skyy liked none except maybe the rabbit: more detail, match the vanilla Hytale creature style (proportions, palettes, chunky
      voxel-model look); start from the rabbit. Output: `research/cloud/pet-art/` v2.
      Dragon icon: match the Dragon Nestkeeper (Aures) dragons' look (Skyy) - original drawing in their style only; no tracing their files until Aures says OK.
- [ ] **Zone 1 town v2** - Skyy likes the districts but it is "too square": redo `research/cloud/Zone-1-Town-Layout.md` + the map PNG organic like
      the Hypixel SkyBlock Hub (winding roads, irregular plazas); vanilla temple at the CENTRE right behind spawn - the town grew around an ancient
      temple (docs/answered/world.md 2026-10-06). Keep the v1 map as Zone-1-Town-Map-v1.png.
- [ ] **Spellbook table re-run** - re-run the staff columns of `research/cloud/Spellbook-Ladder.md` section 2 with the refreshed staff costs
      (210 / 240 / 270 / 310 / 350, `research/cloud/SkyyArmory-Roadmap.md` section 6); keep book costs. Output: the edited file.
- [ ] **Mining helmet lamp spec** - Skyy: helmet lamps must really light (reuse the SkyyAccessories Lantern light code, docs/answered/bags.md + gear.md):
      reach per tier, one light per player (helmet vs Lantern accessory), cost, edge cases. Output: `research/cloud/Mining-Lamp-Spec.md`.
- [ ] **Crop armor stats** - stats/recipes for the crop sets on `research/cloud/gathering-armor-art/farming-sheet.png` (Wheat..Onion), replacing the
      metal Farming set numbers in `research/cloud/Gathering-Armor-Mining-Farming.md`. Output: `research/cloud/Crop-Armor-Spec.md`.
- [ ] **Pet zones + rarities** - fill the gaps `research/cloud/pet-art/README.md` section 3 lists (zone and starting rarity per pet) with drop sources
      and odds, aligned with `research/cloud/Pets-Spec.md`. Output: `research/cloud/Pet-Sources.md`.
- [ ] **Accessory icon sizes + vanilla icon check list** - list exactly what the local session must read in Assets.zip for icon size/paths
      for items, accessories, weapons and armor concepts (one checklist for all the art folders). Output: `research/cloud/Art-Checklist-Local.md`.
- [ ] **Capstone set art** - concept sheet for the 3 capstone sets (`research/cloud/Capstone-Sets.md`) in the same pixel style. Output: `research/cloud/capstone-set-art/`.


## Done (delete after logging - see the rules above)
