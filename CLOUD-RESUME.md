# CLOUD-RESUME - rolling to-do for cloud sessions

Work a cloud session can do while the local session waits (usage limits, Skyy away). Started 2026-10-02.

## How this file works (read every time)

- **Rolling list:** do the top open task, then mark it `[x]` with the date and the output file. When you open this file and see `[x]`
  items, first add one line per item to `research/cloud/LOG.md`, then DELETE those items here and top the list back up to about 8
  open tasks (ideas: RESUME.md section 3, OPEN-QUESTIONS.md open lines, the plans in `research/`). Keep this file under ~80 lines.
- **Cloud limits:** no access to Skyy's PC, the Hytale game files (`HytaleServer.jar`, `Assets.zip`), installed mods or the test world.
  You cannot build, test or deploy. Only add tasks that need none of that. Any fact you cannot check without the game files: mark it
  **UNVERIFIED** and list it under "For the local session" in your output.
- **Where results go:** new files in `research/cloud/` (one file per task). You may push straight to `main` ONLY changes to this file and
  to `research/cloud/` (always `git pull --rebase --autostash` first). Any change to another file goes through a pull request.
- **Never touch:** build / patch scripts, `tools/deploy_set.py`, jars, `SkyyGear-Plan.md`, `SkyyGear-Stat-Catalog.md`.
- Follow `PROJECT-RULES.md`. Skyy uses they/them. Plain English, tables, short.

## Open tasks (top = next)

- [ ] **Pocket Shards spec draft** (SkyWynn's minions, `SkyyMinions-Plan.md`): research Hypixel SkyBlock minions on the web (types, tier
      I-XI speeds and storage, fuel, upgrades, slot unlocks, crafting); propose our Pocket Shard list (fits our skills / Hytale resources),
      tiers, upgrades and slot rules. Engine questions go under "For the local session". Output: `research/cloud/Pocket-Shards-Spec.md`.
- [ ] **Pets spec draft** from `research/Pets-Idea.md`: research SkyBlock pets (types, rarities, levels 1-100, XP rules); propose the launch
      list - farming, mining, foraging, general combat + at least one pet per class (Archer, Warrior, Mage, Berserker, Priest) - with buffs
      per level and rarity, using Hytale creatures (model ids UNVERIFIED). Output: `research/cloud/Pets-Spec.md`.
- [ ] **Story script draft** - the starter shard chain and the Zone 1 "cosmic waiting room" from `research/Isles-of-the-Void-Lore.md`:
      quest steps and dialogue (the overconfident talking rock guide, the sleepy clerk, ticket #4,000,000,001). Silly and absurd, as Skyy
      wants. Output: `research/cloud/Story-Script-Draft.md`.
- [ ] **Zone boss ideas** - one guardian per zone island (Zone 1-4) and the Zone 5 dragon, built from vanilla Hytale creatures where
      possible (web: Hytale wiki), fitting the zone bands and the lore; attacks, arena, drops. Output: `research/cloud/Zone-Bosses-Ideas.md`.
- [ ] **Crude armor set design** - the new Lv 1 starter armor (Skyy 2026-10-01): pieces, stats next to vanilla's weakest armor (web),
      recipe from starter-shard materials. Asset work is local. Output: `research/cloud/Crude-Armor-Design.md`.
- [ ] **"Test now" summary** - read `TEST-CHECKLIST.md` and write a short list of what Skyy has not tested yet (newest sections), riskiest
      first. Output: `research/cloud/Test-Now.md`.

- [ ] **Open-questions digest for Skyy** - read the lines in `OPEN-QUESTIONS.md` not marked ANSWERED / LOCKED and write one short page: each
      question, the current default, a recommended answer with one line of why. Output: `research/cloud/Open-Questions-Digest.md`.

## Done (delete after logging - see the rules above)

- [x] Mob level refit to new zone bands - 2026-10-02 - `research/cloud/Mob-Levels-Refit.md`
