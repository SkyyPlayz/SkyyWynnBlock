# SkyWynn - project rules (read before working on this repo)

These are the standing rules for anyone who picks this project up - a person or an AI session. They were collected from Skyy's
instructions over many sessions (2026-09-22 to 2026-10-05). When something here and an older doc disagree, this file and the newest
`docs/answered/` / `HANDOFF.md` lines win.

- **Owner:** Skyy (GitHub **SkyyPlayz**) - uses **they/them**. A design partner also pushes to this repo.
- **What it is:** SkyWynn, a Hytale server pack of standalone `Skyy*` mods blending Hypixel SkyBlock and Wynncraft (name idea for the
  pack: *Isles of the Void* - nothing renamed yet).
- **Where to start:** `RESUME.md` (where we are, what is next) -> `INDEX.md` (where every file is + cheap search recipes) -> then only
  the file the task needs: `HANDOFF.md` (versions + build rules), `OPEN-QUESTIONS.md` (open only), `docs/answered/` (every answer),
  `docs/log/` (running log), `TEST-CHECKLIST.md`. Build agents: `tools/AGENT-BRIEF.md`.

## 1. Skyy's PC - safety rules (never break these)

- **Touch only what you need to build and test the mods.** Skyy: "DO NOT touch anything on my pc besides what you need to to run your
  tests of the mods."
- **Game files are read-only:** `HytaleServer.jar`, `Assets.zip`, other people's mods, and the live world / save data under
  `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData` ("never touch UserData except read-only"). To test against real data, copy it into
  scratch first.
- **The only writes into UserData:** the deploy (`python tools/deploy_set.py --yes`, which copies the Skyy jars into `Mods` and switches
  them on in the test world) and nothing else. Reading logs and copying data out for tests is fine.
- **Never write anywhere else in `C:\Users\SkyLo\AppData`.** Scratch goes only under `tools/dev/scratch/<task>/` (use the full path),
  and is deleted afterwards. Point TEMP/TMP there for Java runs and use `-XX:-UsePerfData`.
- **Never kill or start the game.** If Hytale is running, wait - a deploy happens once Skyy closes it.
- **Never enter passwords or tokens.**

## 2. The repo is PUBLIC

- Never commit game files, vanilla-derived assets (generate them into the jars at build time instead), other authors' files (unless
  their licence allows it), or personal data (emails, tokens). Built jars, `backups/` and scratch are git-ignored.
- Don't copy other authors' code or assets unless their licence allows it. Ideas are fine: "never build new when you can steal what
  already works" means **vanilla Hytale first**, then borrow ideas or allowed code from others.
- Never commit anything under `tools/dev/scratch/`, `backups/` or `.claude/worktrees/` (all git-ignored).

## 3. Deploying (Skyy's standing auto-deploy rule)

Skyy: "just deploy things as they are ready, so I don't have to ask you to deploy when I want to test it."

1. A round is **ready** when it is built, reviewed, fixed, cross-checked, pinned in `tools/deploy_set.py` and committed.
2. Check the game is closed (no `HytaleServer` java process). Never kill it.
3. Back up the live Skyy jars + the world `config.json` + every `Skyy_*` data folder into `backups/deploy-<date>-<time>/`
   (`python tools/backup_deploy.py`).
4. `python tools/deploy_set.py --yes` - the **only** deploy path. Build scripts never get `--deploy`.
5. Add the TEST-CHECKLIST section, the HANDOFF version row + log line, update RESUME / OPEN-QUESTIONS, commit and push.
6. `python tools/tidy_local.py --yes` - keeps the local-only files small (section 5 "Keep it tidy").

Respect the rollback floors written in `tools/deploy_set.py` (for example: never roll SkyyProfiles below 0.1.5 once a profile was deleted).

## 4. How we build

- **No javac.** Java source lives inside Python build scripts and is compiled with javassist via jpype (`tools/skyybuild.py`). Full
  toolchain notes and javassist limits: `tools/AGENT-BRIEF.md`.
- **Patch scripts:** a new version is derived from the CURRENT version (the SET pin) by `tools/<mod>_<ver>_patch.py`; edit the patch,
  never the generated script. Exception: four generated scripts Skyy edited by hand (commit ab75b6c, listed in RESUME.md) are the source
  for their successors.
- **Build and test all mods together** as one set (`tools/deploy_set.py` SET).
- **Every UI must look and feel vanilla:** use the shared kit `tools/skyyui.py` and `research/Vanilla-UI-Style-Guide.md`; inline pages
  only; the UI rules in HANDOFF section 2 (they cost 30 builds to learn).
- **Everything a server owner might change is editable in game:** SkyWynn Menu -> Server Setup, through the config kit
  `tools/skyycfg.py` (`tools/CONFIG-CONTRACT.md`). Time settings are shown in seconds.
- **One-time setting migrations:** only rewrite lines still holding the old default (hand-edited values are kept and logged), take a
  verified History snapshot first, write a change-log line with Undo, use a marker so it runs once, keep the file's bytes and line
  endings.
- **Cross-mod calls** only through the shared `skyy.bridge` map with plain java.lang types. Per-profile data follows
  `tools/PROFILES-CONTRACT.md`.
- **Round size (Skyy 2026-10-02: "full round only for big builds ... better safe than sorry - just use it if you think it might need
  it"):**
  - **Full round** - build -> review -> fix -> cross-check (`python tools/ci/crosscheck.py --jar <new jars> --baseline`: all SET jars in one JVM with `-Xverify:all`, access + Adventurer permission audit,
    `python tools/ci/lint.py` with 0 fails) -> pin -> commit -> deploy (section 3). Use it for anything that touches coins / the economy,
    saved data or migrations, permissions or commands, items that could be lost or duplicated, several mods at once, or a new system -
    and whenever in doubt.
  - **Lean round** - one builder that runs its own harness + one review / cross-check. For a small behaviour change inside one mod with
    no saved-data change.
  - **No agents** - docs, plans, notes, OPEN-QUESTIONS / RESUME updates; a setting Skyy can change in Server Setup themselves (tell them
    how instead of building).

## 5. Docs to keep current

**ALWAYS READY TO HAND OFF (Skyy 2026-10-05, important):** the project must be ready for a new person or session at any moment.
The moment something is done (a build, a deploy, a test result, a decision, a docs change), record it BEFORE starting the next thing:
a line in `docs/log/<YYYY-MM>.md`, the versions table in `HANDOFF.md` if a version changed, and `RESUME.md` "Now" / "Next" - then
commit and push. Never leave finished work only in chat or in memory.

Layout since 2026-10-05 (Skyy: keep the docs small, organized and cheap to search; map in `INDEX.md`; the repo folder is also an
Obsidian vault - `docs/OBSIDIAN.md`):
- `HANDOFF.md` - section 1 versions table (= the SET) + rollback floors; sections 2 + 3 = the UI and COMMAND rules. Keep it short.
- `docs/log/<YYYY-MM>.md` - the append-only running log: ONE line for every build, deploy, test result or decision, at the end of the
  newest month file (start a new month file on the 1st).
- `RESUME.md` - where we are and the next steps, at most ~60 lines, current only (history goes to the log); keep it current at the end
  of every working session.
- `OPEN-QUESTIONS.md` - ONLY questions still waiting on Skyy, each with today's default in [brackets]. **When Skyy answers (Skyy
  2026-10-05):** write the answer word for word as a LOCKED / ANSWERED line in `docs/answered/<topic>.md` ("New answers" block) and DELETE
  the question from OPEN-QUESTIONS.md in the same step: `python tools/qa_append.py <topic> <file> --close "<words from the question>"`
  (`--no-question` instead when Skyy answers something that was never an open question).
- `TEST-CHECKLIST.md` - the "Test next" list; each deploy adds one numbered in-game section at the end of `docs/tests/<newest month>.md`
  plus a line in that list (remove the line once Skyy has tested it); `docs/tests/README.md` indexes every section.
- Class designs: one file per class in `research/classes/` (easy-read: short lines, big spacing); after editing one, run
  `python tools/class_pages.py` to rebuild its HTML page.
- Before committing a docs move / split: `python tools/docs_check.py` must say OK (nothing lost, no new broken paths).
- **Keep it tidy (Skyy 2026-10-05: "id like all the project files to remain clean and organized throughout the project"):** every new
  file goes where `INDEX.md` says that kind of file lives (no new top-level files or folders without adding them to INDEX.md); finished
  scratch is packed or deleted the same day (`python tools/tidy_local.py --yes --scratch <name>`); after every deploy run
  `python tools/tidy_local.py --yes` (packs old jars + all but the newest 5 deploy backups into verified `backups/archive/*.tar.xz`,
  clears build caches, rewrites `backups/README.md`). The local-only layout is in INDEX.md "Local only".
- Skyy's ideas go into `research/*.md` even when they are "just ideas" (world gen, pets, dragons, story ...).
- **Never edit `SkyyGear-Plan.md` or `SkyyGear-Stat-Catalog.md`** - Skyy's own design docs.
- Many docs have mixed line endings (`.gitattributes` keeps bytes exact): edit them without converting line endings; append in the
  file's own style.

## 6. Git

- Pull before pushing: `git pull --rebase --autostash` (the design partner pushes too). Commit and push after every meaningful change.
- Commits use the repo-local GitHub noreply identity that is already configured (Skyy's personal email must not be published).
- **Pull requests: merge them yourself when ready (Skyy 2026-10-05: "go ahead to auto merge when things are ready. Do all the proper
  checks first.")** Ready = CI green on the head commit, every review bot finished and each finding fixed (or answered when it is not a
  bug), no merge conflict, and the local checks pass (`python tools/ci/lint.py` 0 fails, `python tools/docs_check.py` OK for docs
  changes). Merge with a merge commit, then record it (log line + RESUME) per the hand-off rule.

## 7. Working with Skyy

- Skyy uses they/them. Keep answers plain and short; Skyy tests in game and sends screenshots.
- **Fixes from Skyy's tests come first.**
- Ask Skyy before new directions or design choices that are theirs to make; recommend a default, then record the answer.

## 8. For Claude / AI sessions

- The main session plans, launches build / review agents, commits and deploys. **Build, review and cross-check agents follow
  `tools/AGENT-BRIEF.md` instead** (no commits, no deploys, no edits to the docs above, only the files their task names).
- **Cloud sessions** (no access to Skyy's PC or the game files) work from `CLOUD-RESUME.md` - a rolling to-do - and write only that file
  and `research/cloud/` straight to `main`; anything else goes through a pull request. The local session reviews `research/cloud/LOG.md`
  and folds finished work into the log (`docs/log/`). Subagents that need no local files may run in the cloud (Skyy 2026-10-02).
- **Use ultracode on BIG jobs** (Skyy 2026-10-02, late: "remember to use ultracode on big jobs"): new systems or mods, several mods at
  once, coins / economy, saved data, item loss / dupes, permissions -> a full multi-agent workflow (parallel research / spec, adversarial
  multi-lens critics, build, review, fix, cross-check). Small work stays lean or agent-free (section 4 "Round size").
- **Models per agent:** builders Opus (the javassist / engine work is hard), reviews / cross-checks / web research Sonnet, tiny lookups
  Haiku. Fable may be used where it helps (Skyy 2026-10-02: "you can use fable if it helps") - e.g. spec synthesis or the hardest
  engine builds; name the model explicitly per agent.
- **Usage pacing:** big Max plan since 2026-10-02 - about 4-5 heavy workflows at once (10+ with ultracode rounds burned ~12% of the week in 90 minutes on 2026-10-03; on Max 5x it was 3-4); sonnet for reviews and cross-checks, Opus for builds and hard specs;
  check usage between rounds; near the weekly limit finish and deploy what is running, write the next round into RESUME.md and wait for
  the reset unless Skyy says otherwise.
