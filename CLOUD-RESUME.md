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
- [ ] **LIGHT ARMOR CONCEPT SHEETS** (Skyy 2026-10-06: "im excited to see them" - DO THIS FIRST) - docs/answered/gear.md 2026-10-05 lines
      (Light armor + "light armor concept"). Skyy's reference picture stays local (other people's art); its look in words: dark/black leather
      armor, a diamond-quilted scale pattern on the chest, a raised stand-up collar, layered rounded shoulder caps (2-3 overlapping plates),
      segmented upper-arm / elbow / forearm guards and finger-less hand guards, a brown leather diagonal chest strap and a wide double waist
      belt with brass buckles + a belt pouch, a skirt of long rectangular leather tassels (front / side / back), small brass leaf-shaped accent
      pieces. Make ORIGINAL pixel-art concept sheets (Python + Pillow, generated - no copied art): one front-view chest + full-set preview
      per tier, Hytale-ish chunky pixel style (CORRECTION Skyy: tier 1 = vanilla leather, NO design; the black leather STARTS at
      COPPER): Copper = black leather + small copper trims (buckles, collar + shoulder rims,
      accents); Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium = the same black-leather base, metal accents in that metal's colours AND
      shapes that echo that metal's vanilla armor style (web screenshots of Hytale's metal armors; mark guesses UNVERIFIED). Use sub agents
      if useful (an Opus agent for the image script). Output: `research/cloud/light-armor/` (PNGs + `README.md` with one note per tier +
      the script), a combined `light-armor-sheet.png`. Ask Skyy nothing - they will react to the sheet.
- [ ] **Loot round revision** (Skyy 2026-10-06, docs/answered/gear.md 'LOCKED 2026-10-06 ... LOOT') - web research Wynncraft loot chests
      (tiers, respawn timers, spawn rules near players, vanish-on-loot) + identify / re-roll; then revise research/Loot-Unid-Spec.md +
      research/cloud/Loot-Box-Design.md: item decided AT IDENTIFY (not sealed), drop-only vanilla gear ranked into levels (the list itself
      = local task, Assets.zip), mob drop rate a little higher, our own vanishing / respawning surface loot chests that never touch
      player-placed chests. Output: `research/cloud/Loot-Round-Revision.md`.

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->
<!-- 2026-10-02 local session: 'Skill-tree pass 2 notes' removed - the local research/Skill-Trees-2-Spec.md covers it. -->
- [ ] **Gathering numbers reconciliation** - `research/cloud/Tool-Levels-Revision.md` proposes one Fortune stacking rule (per-source caps under
      doubleDropMax 1.0) and rescales `research/cloud/Foraging-Armor-Design.md`, `research/cloud/Gathering-Armor-Mining-Farming.md`, `research/cloud/Pets-Spec.md`
      and `research/cloud/Collection-Unlocks-Draft.md`. Make ONE table of every Fortune / speed / Tree Feller source with the agreed numbers; list the edits each
      draft needs. Output: `research/cloud/Gathering-Numbers-Reconciled.md`.
- [ ] **Bank + Tab calibration** - `research/cloud/Economy-Audit.md` C1/C2: bank 2% per real hour offline on every profile is the biggest faucet; the Tab is
      ~70x endgame income. Propose the bank change (per day / online only / per account), a Tab rate tied to measured income, the profile-grant fix (C5),
      with simulations. Output: `research/cloud/Bank-Tab-Calibration.md`.
- [ ] **Spellbook ladder** - `research/cloud/SkyyArmory-Roadmap.md` Q3: spellbooks have no metal versions; design the 7-metal ladder (leather + metal clasp),
      Mana costs vs pools, area-based power, the Levitate charged attack per tier. Output: `research/cloud/Spellbook-Ladder.md`.
- [ ] **Kunai ladder** - Assassin kunai (research/classes/Assassin.md): metal ladder mirroring daggers, stack/return rules, throw-teleport numbers per tier,
      speed tier (`research/cloud/Weapon-Speed-Tiers.md`). Output: `research/cloud/Kunai-Ladder.md`.
- [ ] **Archer bolts + holster** - RESUME follow-up: Archery 15+ extra crossbow bolts and the late-game holstered reload (approved, later); design numbers,
      Archer tree hooks (`research/cloud/Class-Tree-Paths.md`). Output: `research/cloud/Archer-Bolts-Holster.md`.
- [ ] **Return Visit + Tab reveal scripts** - dialogue for the Tab reveal (dragon "fees" line), the clerk pay-off scene, prestige "go home anyway" and the
      Return Visit quest (`research/cloud/Prestige-Spec.md` 4, `research/cloud/Tab-Economy.md` 8) in SkyyQuests property format. Output: `research/cloud/Tab-Prestige-Scripts.md`.
- [ ] **Capstone floors 4-7** - `research/cloud/Capstone-Dungeon-Spec.md` ships 3 floors; design floors 4-7 (themes, rooms, puzzles, bosses with phases,
      Set piece drops from `research/cloud/Capstone-Sets.md`). Output: `research/cloud/Capstone-Floors-4-7.md`.
- [ ] **Zone 4-5 materials for the new tiers** - Cindersteel, Amberite, Drakonite (`research/cloud/SkyyArmory-Roadmap.md`): ores / drops, where they
      spawn, collections + Enchanted forms, Bazaar base prices, smelting. Fit `research/cloud/Gathering-Tiers-Draft.md`. Output: `research/cloud/Zone-4-5-Materials.md`.


## Done (delete after logging - see the rules above)
