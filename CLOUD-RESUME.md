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

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->
<!-- 2026-10-02 local session: 'Skill-tree pass 2 notes' removed - the local research/Skill-Trees-2-Spec.md covers it. -->
- [ ] **Magic + new weapons concept sheet** - icons/side views in the `research/cloud/light-armor/make_sheets.py` pixel style: metal wands (style B: wood
      handle + metal head, LOCKED), staffs, spellbooks (`research/cloud/Spellbook-Ladder.md`), Soul Orb cages (`research/cloud/Soul-Orb-Spec.md`), kunai
      (`research/cloud/Kunai-Ladder.md`), Bo staff + fists (`research/cloud/Monk-Kit-Spec.md`) for Copper..Onyxium. Output: `research/cloud/weapon-art/`.
- [ ] **Accessory icons sheet** - one icon per booster line x 4 rarities (`research/Booster-Accessories-Spec.md` 2.x: Health, Stamina, Mana, Speed,
      Regeneration, Brawler, Runic, Stonehide, Razorfang, Feather, Lantern) with rarity frames/colours. Output: `research/cloud/accessory-art/`.
- [ ] **Fish species catalog** - the species for `research/cloud/SkyyFishing-Spec-Draft.md`: per zone/biome/season (Dynamic Seasons) names, rarity,
      weight range, length, bite time, sell base, food family; lore-voice names. Output: `research/cloud/Fish-Species-Catalog.md`.
- [ ] **Tab-Economy refresh** - rewrite `research/cloud/Tab-Economy.md` sections 2-5 and 7-10 to the `research/cloud/Bank-Tab-Calibration.md`
      recommendations (Void Marks display, tab.perHour, interest per online day); keep Skyy's lines word for word. Output: the edited file + a LOG line.
- [ ] **Roadmap Mana table refresh** - re-run `research/cloud/SkyyArmory-Roadmap.md` section 6 with the SkyyArmory-Spec 15.4 Mage/Priest pool rows
      (10 per level for Mage) and `research/cloud/Weapon-Speed-Tiers.md` mana scaling; align with `research/cloud/Spellbook-Ladder.md`. Output: the edited file.
- [ ] **Cooking spec formula PR** - `research/Cooking-Skill-Spec.md` 2.2 / 4.1 still use 2^(Grade/5); the locked rule is x(1 + 0.32 x Grade)
      (`research/cloud/Food-Expansion-Draft.md`). PR "[cloud] ..." fixing the formula and its tables. Output: PR + LOG line.
- [ ] **Zone 1 starter town layout** - the main town around a vanilla temple (docs/answered/world.md R9): districts (Department of Arrivals desk, bank,
      Bazaar, smith, Board, Event Vendor, warps, portal), sizes, a top-down ASCII/PNG map, NPC list from `research/cloud/NPC-Shops-Spec.md` and
      `research/cloud/Barks-Signs-Tips.md`. Output: `research/cloud/Zone-1-Town-Layout.md`.
- [ ] **Pets concept sheet** - pixel concepts for the pets in `research/cloud/Pets-Spec.md` (one per zone family + the dragon hatchling), same style.
      Output: `research/cloud/pet-art/`.


## Done (delete after logging - see the rules above)
