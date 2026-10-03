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

- [ ] **Class ability drafts** - research Wynncraft class ability trees on the web and draft SkyWynn abilities for Archer, Warrior, Mage, Berserker,
      Priest (names, cost, effect; Hytale 0.7 runes as the base - `research/Hytale-Runes-Research.md`). Output: `research/cloud/Class-Abilities-Draft.md`.
- [ ] **NPC shops spec (SkyyEconomy 0.2)** - read `SkyyEconomy-Plan.md`; research SkyBlock NPC shop/sell prices; propose shop lists, buy/sell price
      rules per zone town and anti-inflation guards. Output: `research/cloud/NPC-Shops-Spec.md`.
- [ ] **Starter shard chain map** - paper layout for the starting shard + shards 2-3 (sizes, trees, cave, bridges, spawn points, mob camp, portal
      frame) matching `Story-Script-Draft.md` quests 1-12. Output: `research/cloud/Starter-Shard-Layout.md`.
- [ ] **Elites and world events spec** (Mob-Levels-Plan section 11 stage 3): elite rules, event ideas per zone, rewards. Output: `research/cloud/Elites-Events-Spec.md`.

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->

## Done (delete after logging - see the rules above)

- [x] Zone 2-5 story chains - 2026-10-03 - `research/cloud/Story-Script-Zones-2-5.md`
- [x] The Tab economy design - 2026-10-03 - `research/cloud/Tab-Economy.md`
- [x] Dragon hatching quest line - 2026-10-03 - `research/cloud/Dragon-Quest-Spec.md`
