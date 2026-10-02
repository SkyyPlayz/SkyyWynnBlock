# SkyWynn - project rules (read before working on this repo)

These are the standing rules for anyone who picks this project up - a person or an AI session. They were collected from Skyy's
instructions over many sessions (2026-09-22 to 2026-10-01). When something here and an older doc disagree, this file and the newest
`OPEN-QUESTIONS.md` / `HANDOFF.md` lines win.

- **Owner:** Skyy (GitHub **SkyyPlayz**) - uses **they/them**. A design partner also pushes to this repo.
- **What it is:** SkyWynn, a Hytale server pack of standalone `Skyy*` mods blending Hypixel SkyBlock and Wynncraft (name idea for the
  pack: *Isles of the Void* - nothing renamed yet).
- **Where to start:** `RESUME.md` (where things live, where we got to, what is next) -> `HANDOFF.md` (section 3 = current state,
  section 6 = running log) -> `OPEN-QUESTIONS.md` (every decision) -> `TEST-CHECKLIST.md`. Build agents: `tools/AGENT-BRIEF.md`.

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
- Never commit the stray `PROJECT/` folder (an old agent-scratch accident) or anything under `tools/dev/scratch/`.

## 3. Deploying (Skyy's standing auto-deploy rule)

Skyy: "just deploy things as they are ready, so I don't have to ask you to deploy when I want to test it."

1. A round is **ready** when it is built, reviewed, fixed, cross-checked, pinned in `tools/deploy_set.py` and committed.
2. Check the game is closed (no `HytaleServer` java process). Never kill it.
3. Back up the live Skyy jars + the world `config.json` + every `Skyy_*` data folder into `backups/deploy-<date>-<time>/`.
4. `python tools/deploy_set.py --yes` - the **only** deploy path. Build scripts never get `--deploy`.
5. Add the TEST-CHECKLIST section, the HANDOFF version row + log line, update RESUME / OPEN-QUESTIONS, commit and push.

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
- **Every round:** build -> review -> fix -> cross-check (all SET jars in one JVM with `-Xverify:all`, the Adventurer permission audit,
  `python tools/ci/lint.py` with 0 fails) -> pin -> commit -> deploy (section 3).

## 5. Docs to keep current

- `HANDOFF.md` - section 3 current state (versions table = the SET), section 6 append-only log: one line for every build, deploy,
  test result or decision.
- `RESUME.md` - where we are and the next steps; keep it current at the end of every working session.
- `OPEN-QUESTIONS.md` - record every answer Skyy gives as a LOCKED / ANSWERED line; open questions keep their current default in brackets.
- `TEST-CHECKLIST.md` - one section per deploy with numbered in-game steps.
- Skyy's ideas go into `research/*.md` even when they are "just ideas" (world gen, pets, dragons, story ...).
- **Never edit `SkyyGear-Plan.md` or `SkyyGear-Stat-Catalog.md`** - Skyy's own design docs.
- Many docs have mixed line endings (`.gitattributes` keeps bytes exact): edit them without converting line endings; append in the
  file's own style.

## 6. Git

- Pull before pushing: `git pull --rebase --autostash` (the design partner pushes too). Commit and push after every meaningful change.
- Commits use the repo-local GitHub noreply identity that is already configured (Skyy's personal email must not be published).

## 7. Working with Skyy

- Skyy uses they/them. Keep answers plain and short; Skyy tests in game and sends screenshots.
- **Fixes from Skyy's tests come first.**
- Ask Skyy before new directions or design choices that are theirs to make; recommend a default, then record the answer.

## 8. For Claude / AI sessions

- The main session plans, launches build / review agents, commits and deploys. **Build, review and cross-check agents follow
  `tools/AGENT-BRIEF.md` instead** (no commits, no deploys, no edits to the docs above, only the files their task names).
- **Usage pacing (Max 5x plan):** at most 3-4 workflows at once; sonnet for reviews and cross-checks, Opus for builds and hard specs;
  check usage between rounds; near the weekly limit finish and deploy what is running, write the next round into RESUME.md and wait for
  the reset unless Skyy says otherwise.
