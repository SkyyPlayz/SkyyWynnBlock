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
- [ ] **SkyyFishing spec draft** (Skyy 2026-10-06, docs/answered/skills.md 'LOCKED 2026-10-06 ... FISHING') - web research first:
      Angler's Almanac (docs https://rm20killer.github.io/Anglers-Almanac-Doc/ + its CurseForge page), HyFishing (CurseForge), their
      LICENCES (jars carry none of their own -> ideas only unless a page allows reuse), Hypixel SkyBlock fishing (rods, rod parts, sea
      creatures, treasure, fishing collections + armor, trophy / lava fishing) + Minecraft treasure fishing. Then the spec: bench + 5 part
      kinds (hook / line / sinker / rod / reel) with tiers, rod = max weight / length, reel = reel power per click, the click-bar minigame
      numbers, fish length + weight + weight-based sell price, treasure table (coins, unidentified gear), collections gates (fishing + metal
      collection per rod / reel tier), fishing armor, accessories, later sea creatures + Zone 4 lava fishing, fish foods. Use an Opus agent
      for the engine-free design if useful. Output: `research/cloud/SkyyFishing-Spec-Draft.md`.
- [ ] **Food expansion draft** (Skyy 2026-10-06: food = primary healing) - every vanilla food (names from the web / wiki; exact ids
      UNVERIFIED) placed into SkyyCooking's healing / Grade system, our own new foods, and the eating rule (faster eating vs hits no longer
      cancel eating - recommend one) + Skyy's POTION vs FOOD design (docs/answered/skills.md 'LOCKED 2026-10-06 ... POTIONS'):
      focused potions with flat numbers by grade, mixed foods with family focus (veggies HP, fruit Mana, meat Stamina, mushrooms bonus
      effects, combos stack). Output: `research/cloud/Food-Expansion-Draft.md`.
- [ ] **Light armor helmet options** - Skyy's reference has no helmet; draw 3 helmet options (hood with metal rim, half-mask cowl, open leather cap) for
      Copper and Onyxium with the same script style (`research/cloud/light-armor/make_sheets.py`). Output: `research/cloud/light-armor/helmets.png` + README note.
- [ ] **Heavy armor tier 1 concept** - HEAVY ARMOR tier 1 = a heavy leather set below Copper (vanilla Armor_Leather_Heavy, restyle): concept sheet in the
      light-armor script style + notes. Output: `research/cloud/heavy-armor/`.
- [ ] **Crude Robe concept** - CLOTH tier 1 = Crude Robe (Fibre + green crystal), the green hooded mage-robe look in words (docs/answered/gear.md 2026-10-05):
      concept sheet in the same style. Output: `research/cloud/cloth-armor/`.
- [ ] **Foraging armor concept sheets** - Wood + Softwood..Goldenwood (`research/cloud/Foraging-Armor-Design.md` section 7: bark plates, vine trims,
      sap veins, echoing Copper..Onyxium shapes). Output: `research/cloud/foraging-armor/`.
- [ ] **Mining + Farming armor concept sheets** - from `research/cloud/Gathering-Armor-Mining-Farming.md` looks (miner's leather + lamp helmet; straw/linen
      farmer clothes). Output: `research/cloud/gathering-armor-art/`.


## Done (delete after logging - see the rules above)
- [x] Cloud drafts consistency pass - 2026-10-06 - `research/cloud/Consistency-Pass-1006.md`
- [x] NoCube + Aures mods survey - 2026-10-06 - `research/cloud/NoCube-Mods-Survey.md`
- [x] Apply the gathering reconciliation - 2026-10-06 - `research/cloud/Gathering-Reconciliation-Applied.md`
- [x] Questions digest for Skyy - 2026-10-06 - `research/cloud/Questions-Digest-1006.md`
