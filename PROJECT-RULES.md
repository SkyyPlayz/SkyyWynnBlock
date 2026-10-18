# SkyWynn - project rules (read before working on this repo)

Standing rules for anyone working on this project, person or AI. Where this file and an older doc disagree, this file and the newest
`docs/answered/` / `HANDOFF.md` lines win. Skyy's own words behind each rule are in `docs/answered/project.md`.

- **Owner:** Skyy (GitHub **SkyyPlayz**), uses **they/them**. A design partner also pushes to this repo.
- **What it is:** SkyWynn, a Hytale server pack of standalone `Skyy*` mods blending Hypixel SkyBlock and Wynncraft.
- **Where to start:** `RESUME.md` -> `INDEX.md` (where every file is + search recipes) -> only the file the task needs: `HANDOFF.md`
  (versions + UI / command rules), `OPEN-QUESTIONS.md` (open only), `docs/answered/`, `docs/log/`, `TEST-CHECKLIST.md`. Build agents:
  `tools/AGENT-BRIEF.md`.

## 1. Skyy's PC (never break these)

- Touch only what you need to build and test the mods.
- Game files are read-only: `HytaleServer.jar`, `Assets.zip`, other people's mods, and everything under
  `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData`. To test against real data, copy it into scratch first.
- The only write into UserData is the deploy (`python tools/deploy_set.py --yes`) - plus, once a log has been read, moving old game logs (`UserData\Logs\*.log`, `Saves\<world>\logs\*.log`, all but the newest of each) to the Recycle Bin (Skyy 2026-10-08: "be sure to delete logs when you are done with them, so they dont take up my storage space"). Never hard-delete.
- Never write anywhere else in `C:\Users\SkyLo\AppData`. Scratch only under `tools/dev/scratch/<task>/` (full path), deleted afterwards;
  point TEMP/TMP there for Java runs and use `-XX:-UsePerfData`.
- Never kill or start the game. If Hytale is running, the deploy waits until Skyy closes it. ONE exception (Skyy 2026-10-08): the SMOKE TEST -
  start HytaleServer.jar offline (no client) on a COPY of the test world under tools/dev/scratch/, read its log, stop it; never the real world.
- Never enter passwords or tokens.

## 2. The repo is PUBLIC

- Never commit game files, vanilla-derived assets (generate them into the jars at build time), other authors' files (unless their licence
  allows it), or personal data. `tools/dev/scratch/`, `backups/`, `.claude/worktrees/` and built jars are git-ignored - keep it so.
- Vanilla Hytale first, then borrow ideas (or licence-allowed code) from others - "never build new when you can steal what already works".
- **Check for an existing mod BEFORE building one** (Skyy 2026-10-11: "before making a mod, check if one already exists that does what we
  want. if it does, include it. if its still better to make our own, learn from how the other was made to make building ours easier and
  faster."): every new system / spec starts with a short survey (CurseForge + Skyy's Mods folder; cheap - free OpenRouter models first).
  A good fit -> pack it (licence permitting; MIT / PD / CC BY may be folded). Still better to build ours -> study how theirs works
  (manifest, assets, configs, class names - read only) and name what we reuse or learn in the spec.
- **No duplicates between mods** (Skyy 2026-10-11: "make sure when using lots of mods that do the same thing, we dont get clashes or
  duplicates of anything. if 3 mods add a horse mount, take the best one. not all 3" + "that goes for all mods." = ours too): before a mod goes into the pack (or is folded),
  list what it adds and compare with our mods + every pack mod; keep the BEST version of each thing (mount, weapon, totem, biome,
  structure, command, key bind) and switch off / leave out the rest (a pack mod can only be switched off whole - if it brings a
  duplicate we cannot hide, pick one mod). Record the choice in PACK.md.
- **Pack mods (permissions in `PACK.md`):** our own code may react to their items by id at runtime (Grades, buffs, Bazaar / collection /
  XP listings). Never ship a file overriding their item ids, never copy their recipes / numbers / models / textures, never bundle or
  re-upload their files. If a change needs their data edited, ask the author first.

## 3. Deploying (Skyy's standing auto-deploy rule - no need to ask)

1. A round is **ready** when built, reviewed, fixed, cross-checked, pinned in `tools/deploy_set.py` and committed.
2. Game closed (no `HytaleServer` java process) - never kill it.
3. `python tools/backup_deploy.py` (live Skyy jars + world `config.json` + every `Skyy_*` data folder -> `backups/deploy-<stamp>/`).
3b. Smoke test (allowed since 2026-10-08): run the new set on an offline server against a scratch COPY of the world; every '[Skyy...] ready'
    line present, no asset-validation failure, no SEVERE from our mods - else fix first.
    Tool: `python tools/smoke_test.py` (game closed; exit 0 = PASS; `--jar <Mod>/<Mod>-<ver>.jar` for an unpinned candidate; ~45 s,
    leaves only `tools/dev/scratch/smoke/<stamp>.log`; pack with `python tools/tidy_local.py --yes --scratch smoke`).
4. `python tools/deploy_set.py --yes` - the ONLY deploy path. Build scripts never get `--deploy`.
5. `python tools/record_deploy.py --title ... --mod MOD:OLD:NEW --steps <file> --checklist ... --log ...` (test section, index, HANDOFF,
   TEST-CHECKLIST, log in one go), then RESUME; commit and push.
6. `python tools/tidy_local.py --yes`.

Respect the rollback floors in `tools/deploy_set.py`.

## 4. How we build

- **No javac:** Java lives in Python build scripts, compiled with javassist via jpype (`tools/skyybuild.py`; limits in AGENT-BRIEF).
- **Patch scripts:** a new version is derived from the CURRENT version (the SET pin) by `tools/<mod>_<ver>_patch.py`; edit the patch,
  never the generated script - except the four generated scripts Skyy hand-edited (commit ab75b6c, listed in RESUME.md).
- Build and test all mods together as one set (`tools/deploy_set.py` SET).
- **One menu pattern** (Skyy 2026-10-16: "lets try to reduce and compress the menus together to reduce clutter. then make sure its consistent
  across the board, then follow the pattern when making new or adding to existing menus."): fewer, merged menus; every page follows
  `research/Menu-Pattern.md` (layout, sizes, tab rows, scroll lists) - new menus and changes to old ones alike.
- **UI looks and feels vanilla:** shared kit `tools/skyyui.py` + `research/Vanilla-UI-Style-Guide.md`; inline pages only; HANDOFF section 2.
- **Tooltips / flavor text bigger + colour coded** (Skyy 2026-10-18: "make all the flavor text use a slightly bigger font, and color code
  everything. so you can see what stats it gives at a glance"): one colour code everywhere, Style Guide section 15; every new or changed tooltip follows it.
- **Tier tags** (Skyy 2026-10-15: "keep this as a general rule"): every item with a tier - now or added later - shows it first in its flavor
  text (`T3 Iron - text`; materials = their tool's tier; own ladders `T2 Totem`), from the one table `tools/tier_tags.py`
  (research/Tier-Tags-Plan.md). A round that adds a tiered item adds it to that table; `tools/ci/langdup.py` keeps one writer per lang key.
- **Four power sources** (Skyy 2026-10-16: "this applies acroos the board. to all skills. and your class. your weapon is only part of it. your
  gear is important, but accessory's and pets are essential too!"): every skill and class stat is balanced as tool / weapon + gear +
  accessories + pets stacking; accessories and pets are essential, not extras.
- **Sort by tier everywhere** (Skyy 2026-10-16: "sort everything by tier in all shops and crafting."): every shop and crafting list sorts by
  tier (`tools/tier_tags.py`), then name; farming lists group each crop as crop, Enchanted crop, seeds, Eternal seeds.
- **Everything a server owner might change is editable in game** (SkyWynn Menu -> Server Setup) through `tools/skyycfg.py`
  (`tools/CONFIG-CONTRACT.md`). Times shown in seconds.
- **One-time setting migrations:** only rewrite lines still holding the old default (keep + log hand-edited values), verified History
  snapshot first, a change-log line with Undo, a run-once marker, keep the file's bytes and line endings.
- Cross-mod calls only through the shared `skyy.bridge` map with plain java.lang types. Per-profile data: `tools/PROFILES-CONTRACT.md`.
- **Round size:**
  - **Full round** - build -> review -> fix -> cross-check (`python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python
    tools/ci/lint.py` 0 fails) -> pin -> commit -> deploy. For coins / economy, saved data or migrations, permissions or commands, items
    that could be lost or duplicated, several mods at once, a new system - and whenever in doubt.
  - Launch rounds with the saved workflow `.claude/workflows/skywynn-round.js` (Workflow name `skywynn-round`; put Skyy's OWN words in
    args `quotes` - without them builders refuse when Skyy keeps chatting about other things).
  - **Ultracode** (BIG jobs: new systems, several mods, economy, saved data, dupes, permissions) - a multi-agent workflow: parallel
    research / spec, adversarial multi-lens critics, build, review, fix, cross-check.
  - **Simplify passes** (`args.simplify: 2`) on refine / merge rounds: a simplicity critic + a behaviour-identical simplifier, repeated
    (each pass catches different simplifications); stops early on NONE FOUND. Costs ~10-20% more per round, so not on small fixes.
  - **Lean round** - one builder with its own harness + one review. Small behaviour change in one mod, no saved-data change.
  - **No agents** - docs, plans, notes; a setting Skyy can change in Server Setup (tell them how instead).

## 5. Docs (always ready to hand off)

The moment something is done (build, deploy, test result, decision, docs change), record it BEFORE starting the next thing: a line in
`docs/log/<YYYY-MM>.md`, the `HANDOFF.md` versions table if a version changed, `RESUME.md` "Now" / "Next" - then commit and push.
Never leave finished work only in chat or memory.

- `HANDOFF.md` - section 1 versions (= the SET) + rollback floors; sections 2 + 3 UI and COMMAND rules. Short.
- `docs/log/<YYYY-MM>.md` - append-only, ONE line per build / deploy / test result / decision.
- `RESUME.md` - current state + next steps only, at most ~60 lines.
- `OPEN-QUESTIONS.md` - only questions still waiting on Skyy, each with today's default in [brackets]. When Skyy answers, record it word for
  word and close the question in one step: `python tools/qa_append.py <topic> <file> --close "<words from the question>"` (or
  `--no-question`).
- `TEST-CHECKLIST.md` - "Test next" list; each deploy adds a numbered section at the end of `docs/tests/<newest month>.md` + a line here
  (remove the line once Skyy has tested it).
- Class designs: one file per class in `research/classes/`; then `python tools/class_pages.py`.
- `python tools/docs_check.py` must say OK before committing a docs move / split.
- **Signposts for every agent** (Skyy 2026-10-16: "make sure just about everything in the repo includes the relevant instructions on where
  to find things and where they go" + "I use grok bot for answering questions, curating designs, and bug test videos ... Everything goes same
  as you do so nobody's lost or confused."): Claude, cloud sessions, Skyy's Grok bot and the design partner all navigate the repo the same way -
  `INDEX.md` first, then the folder's `README.md` (what is here + where new things go; mod / top folders made by `python tools/make_readmes.py`
  - re-run it after adding a mod), and every list / question file names where its answers go. A new folder or file type gets its signpost the
  same day. Skyy: "So the files need to be structured for multiple agents that can't communicate" -> never rely on chat or memory to
  hand work over: every state, decision and next step lives in a file another agent can find from `INDEX.md`.
- **Keep it tidy:** new files go where `INDEX.md` says (add new places to INDEX.md); pack finished scratch the same day
  (`python tools/tidy_local.py --yes --scratch <name>`); `python tools/tidy_local.py --yes` after every deploy.
- Skyy's ideas go into `research/*.md` even when "just ideas".
- **Never edit `SkyyGear-Plan.md` or `SkyyGear-Stat-Catalog.md`** (Skyy's design docs).
- Docs have mixed line endings (`.gitattributes` keeps bytes exact): never convert them; append in the file's own style.

## 6. Git

- `git pull --rebase --autostash` before pushing; commit and push after every meaningful change.
- One task per commit: stage ONLY that task's files (`git add <files>`, never `git add -A` while builders run). A bad step = `git revert`.
- Commits use the repo-local GitHub noreply identity (Skyy's personal email must never be published).
- **Pull requests:** merge them yourself when ready - CI green on the head commit, every review bot finished and each finding fixed or
  answered, no conflict, local checks pass. Merge commit, then log + RESUME.

## 7. Working with Skyy

- Plain, short answers; Skyy tests in game and sends screenshots. Fixes from Skyy's tests come first.
- Ask Skyy before new directions or design choices that are theirs; recommend a default, then record the answer.

## 8. For Claude / AI sessions

- The main session plans, launches agents, commits and deploys. Build / review / cross-check agents follow `tools/AGENT-BRIEF.md` (no
  commits, no deploys, no edits to the docs above, only the files their task names).
- **Cloud sessions** work from `CLOUD-RESUME.md` and push only that file + `research/cloud/` straight to `main`; anything else via PR.
  Talking to the local session: it sends by message (SendMessage); the cloud answers by appending a block to
  `research/cloud/OUTBOX.md` and pushing (the local `cloud-link` mod polls it every 3 min and wakes the local session).
  The local session folds `research/cloud/LOG.md` into `docs/log/`. Subagents that need no local files may run in the cloud.
- **Models:** builders Opus; reviews / cross-checks / web research Sonnet; tiny lookups Haiku; Fable only where it clearly helps (spec
  synthesis, hardest engine builds). Name the model per agent.
- **OpenRouter side jobs** (local + cloud): `tools/llm.py` for bulk reading / sorting / drafts; only Jev (`typesafe/jev-router`) and
  free models ($20 / month cap - ask Skyy before any other paid model); redaction on; the key never in the repo / chat / logs; output
  is a lead Claude checks (research/OpenRouter-Jev-Plan.md, CLOUD-RESUME.md).
  Skyy 2026-10-13: "use JEV wherever you can to reduce your own token cost." -> default to Jev / free models for reading logs, long files,
  agent reports and surveys (ask llm.py a question about the file instead of reading it whole); Claude reads only the short answer.
- **Sessions:** Skyy starts a fresh main session once a day - never clear or restart the session yourself; just keep RESUME.md + the
  log hand-off ready. Agents start fresh: name the files, don't paste history.
- **Usage pacing:** about 4-5 heavy workflows at once on the big Max plan; check usage (ccd get_usage) before each round; near the weekly
  limit finish and deploy what is running, queue the rest in RESUME.md and wait for the reset unless Skyy says otherwise.
