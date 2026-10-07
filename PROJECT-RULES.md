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
- The only write into UserData is the deploy (`python tools/deploy_set.py --yes`).
- Never write anywhere else in `C:\Users\SkyLo\AppData`. Scratch only under `tools/dev/scratch/<task>/` (full path), deleted afterwards;
  point TEMP/TMP there for Java runs and use `-XX:-UsePerfData`.
- Never kill or start the game. If Hytale is running, the deploy waits until Skyy closes it.
- Never enter passwords or tokens.

## 2. The repo is PUBLIC

- Never commit game files, vanilla-derived assets (generate them into the jars at build time), other authors' files (unless their licence
  allows it), or personal data. `tools/dev/scratch/`, `backups/`, `.claude/worktrees/` and built jars are git-ignored - keep it so.
- Vanilla Hytale first, then borrow ideas (or licence-allowed code) from others - "never build new when you can steal what already works".
- **Pack mods (permissions in `PACK.md`):** our own code may react to their items by id at runtime (Grades, buffs, Bazaar / collection /
  XP listings). Never ship a file overriding their item ids, never copy their recipes / numbers / models / textures, never bundle or
  re-upload their files. If a change needs their data edited, ask the author first.

## 3. Deploying (Skyy's standing auto-deploy rule - no need to ask)

1. A round is **ready** when built, reviewed, fixed, cross-checked, pinned in `tools/deploy_set.py` and committed.
2. Game closed (no `HytaleServer` java process) - never kill it.
3. `python tools/backup_deploy.py` (live Skyy jars + world `config.json` + every `Skyy_*` data folder -> `backups/deploy-<stamp>/`).
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
- **UI looks and feels vanilla:** shared kit `tools/skyyui.py` + `research/Vanilla-UI-Style-Guide.md`; inline pages only; HANDOFF section 2.
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
  The local session folds `research/cloud/LOG.md` into `docs/log/`. Subagents that need no local files may run in the cloud.
- **Models:** builders Opus; reviews / cross-checks / web research Sonnet; tiny lookups Haiku; Fable only where it clearly helps (spec
  synthesis, hardest engine builds). Name the model per agent.
- **Sessions:** Skyy starts a fresh main session once a day - never clear or restart the session yourself; just keep RESUME.md + the
  log hand-off ready. Agents start fresh: name the files, don't paste history.
- **Usage pacing:** about 4-5 heavy workflows at once on the big Max plan; check usage (ccd get_usage) before each round; near the weekly
  limit finish and deploy what is running, queue the rest in RESUME.md and wait for the reset unless Skyy says otherwise.
