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

- [ ] **Elites and world events spec** (Mob-Levels-Plan section 11 stage 3): elite rules, event ideas per zone, rewards. Output: `research/cloud/Elites-Events-Spec.md`.

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->

## Done (delete after logging - see the rules above)

- [x] Zone 2-5 story chains - 2026-10-03 - `research/cloud/Story-Script-Zones-2-5.md`
- [x] The Tab economy design - 2026-10-03 - `research/cloud/Tab-Economy.md`
- [x] Dragon hatching quest line - 2026-10-03 - `research/cloud/Dragon-Quest-Spec.md`
- [x] Class ability drafts - 2026-10-03 - `research/cloud/Class-Abilities-Draft.md`
- [x] NPC shops spec - 2026-10-03 - `research/cloud/NPC-Shops-Spec.md`
- [x] Starter shard chain map - 2026-10-03 - `research/cloud/Starter-Shard-Layout.md`
