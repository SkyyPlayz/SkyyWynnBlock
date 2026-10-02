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

- [ ] **Crude armor set design** - the new Lv 1 starter armor (Skyy 2026-10-01): pieces, stats next to vanilla's weakest armor (web),
      recipe from starter-shard materials. Asset work is local. Output: `research/cloud/Crude-Armor-Design.md`.
- [ ] **"Test now" summary** - read `TEST-CHECKLIST.md` and write a short list of what Skyy has not tested yet (newest sections), riskiest
      first. Output: `research/cloud/Test-Now.md`.

- [ ] **Open-questions digest for Skyy** - read the lines in `OPEN-QUESTIONS.md` not marked ANSWERED / LOCKED and write one short page: each
      question, the current default, a recommended answer with one line of why. Output: `research/cloud/Open-Questions-Digest.md`.

## Done (delete after logging - see the rules above)

- [x] Zone boss ideas - 2026-10-02 - `research/cloud/Zone-Bosses-Ideas.md`
