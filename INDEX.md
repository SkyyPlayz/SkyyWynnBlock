# SkyWynn - INDEX (where everything is, 2026-10-05)

Find the right file here, then grep it - never read a big file top to bottom. One line = one fact in the log and answer files, so a
grep hit is the whole thing: `grep -n "Lantern" docs/answered/*.md docs/log/*.md`.

## Read in this order
| File | What | Size |
|---|---|---|
| `RESUME.md` | where we are + the next steps (start here) | ~60 lines |
| `PROJECT-RULES.md` | standing rules for people + AI sessions (PC safety, public repo, deploy, how we build) | ~120 lines |
| `HANDOFF.md` | current versions (= the deploy SET), rollback floors, the UI rules + COMMAND RULES every build must follow | ~85 lines |
| `OPEN-QUESTIONS.md` | ONLY the questions still waiting on Skyy, with today's default | short |
| `TEST-CHECKLIST.md` | what Skyy tests next (deployed, not tested yet) | short |
| `CLOUD-RESUME.md` | cloud sessions' rolling to-do (they write only it + `research/cloud/`) | ~110 lines |

## Folders
| Where | What | How to use it |
|---|---|---|
| `docs/answered/<topic>.md` | every answer Skyy gave, word for word, one per line, by topic (classes, gear, skills, mobs, world, economy, bags, ui, social, pets, project) | grep; newest at the bottom wins; [README](docs/answered/README.md) |
| `docs/log/<YYYY-MM>.md` | running log: one line per build, deploy, test result, decision (was HANDOFF section 6) | grep a mod / version / date; append at the end |
| `docs/tests/<period>.md` | every in-game test section (was TEST-CHECKLIST) | find the section in [docs/tests/README.md](docs/tests/README.md) |
| `docs/handoff/` | old HANDOFF parts: `design-locks.md` (goal, gear locks, design calls), `versions-history.md` (every step per mod), `state-2026-09.md`, `design-notes-2026-09.md` | history - newer answers beat them |
| `docs/plans/` | design plans: `docs/plans/SkyWynn-Master-Plan.md`, `docs/plans/SkyWynn-Decisions.md` (change notes), `docs/plans/SkyWynn-Server-Setup-Plan.md`, `docs/plans/SkyWynn-QoL-Catalog.md`, `docs/plans/Skyy<Mod>-Plan.md` | the 2026-09 plans; later answers in `docs/answered/` win |
| `docs/archive/` | snapshots nobody needs day to day: `docs/archive/DESIGN-STATUS.md` (2026-09-25), `docs/archive/BETA-TEST.md` (2026-09-24), `docs/archive/SkyWynn-Mod-Roster.md` (stale 2026-09-22), `docs/archive/RESUME-2026-10-05.md` (the old long RESUME) | history only |
| `research/` | specs + research per feature (e.g. `research/Mob-Curve-Spec.md`, `research/Tool-Levels-Spec.md`, `research/Loot-Unid-Spec.md`, `research/SkyyArmory-Spec.md`, `research/SkyyWorldGen-Plan.md`, `research/Vanilla-UI-Style-Guide.md`; `research/Accessory-Table-Spec.md` = PAUSED draft) | `ls research/`; grep |
| `research/classes/` | ONE FILE PER CLASS (Warrior, Archer, Mage, Priest, Berserker, Monk, Assassin) + `README.md` (rules + modifier pool); easy-read HTML pages in `research/classes/html/` | edit the `.md`; `python tools/class_pages.py` rebuilds the HTML |
| `research/cloud/` | cloud sessions' specs + their log `research/cloud/LOG.md` | |
| `Skyy<Mod>/` | one build script per mod version (`build_skyy<mod>_<ver>.py`, Java inside Python) + tests; jars are git-ignored | |
| `tools/` | `deploy_set.py` (SET + rollback floors), `backup_deploy.py`, `skyybuild.py`, kits `skyyui.py` / `skyycfg.py` / `skyymove.py` / `skyyart.py`, contracts `tools/AGENT-BRIEF.md` / `tools/CONFIG-CONTRACT.md` / `tools/PROFILES-CONTRACT.md`, `<mod>_<ver>_patch.py`, `tools/ci/lint.py`, `tools/ci/crosscheck.py` (one-JVM SET cross-check: verify + access + Adventurer audit; `--jar <new jar> --baseline`), `tools/dev/` (engine helpers), `qa_append.py`, `docs_check.py`, `tidy_local.py` (local clean-up), `record_deploy.py` (writes a deploy into tests / index / HANDOFF / checklist / log in one go), `make_light_chest.py` (Blockbench light-armor chest model + texture -> `models-local/`), `make_black_mithril.py` (vanilla Mithril set re-leathered black -> `models-local/`), `bb_mcp_stdio.py` (Blockbench MCP over stdio for Claude - works around Avast breaking localhost HTTP; ~/.claude.json runs it) | |
| `.claude/` | `.claude/workflows/skywynn-round.js` (the saved full round: build -> critics -> fix -> [recheck] -> cross-check; args tag / mods / task / quotes / others / lenses / recheck), `.claude/skills/skywynn-art/SKILL.md` (Skyy's art rules - read before any concept art); `worktrees/` is git-ignored | |
| root | `SkyyGear-Plan.md` + `SkyyGear-Stat-Catalog.md` = Skyy's own gear design (never edit); `PACK.md` = third-party mods in the pack | |
| `.obsidian/` + `docs/OBSIDIAN.md` | shared Obsidian vault settings (bookmarks, easy-read snippet, markdown links, hidden folders) + how to use the vault | the repo folder is the vault |

## Local only (Skyy's PC, git-ignored - tidy with `python tools/tidy_local.py --yes`)
| Where | What |
|---|---|
| `Skyy<Mod>/Skyy<Mod>-<ver>.jar` | built jars: only the SET version, the one before it (one-step rollback) and anything newer than the SET; older ones are in `backups/archive/old-jars-*.tar.xz` |
| `backups/README.md` | START HERE for backups: every deploy backup (folder or archive) with the jar versions that changed + how to restore |
| `backups/deploy-<date>-<time>/` | the newest 5 pre-deploy backups (`Mods/` Skyy jars, world `config.json`, `data/Skyy_*`); made by `tools/backup_deploy.py` |
| `backups/archive/` | verified `.tar.xz` packs: `deploys-<YYYY-MM>` (older deploy backups), `old-jars-<date>`, `scratch-<task>-<date>` (finished agent scratch) |
| `tools/dev/scratch/<task>/` | live agent scratch only (now: `mobcurve-numbers/` = the mob curve spec's number model, kept for the mob curve build); pack or delete when the task is done |
| `research/refs/` | Skyy's reference images (other people's art - style inspiration only, never committed); e.g. `armor-style-black-leather.jpg`, `robe-style-green-mage.jpg`, `foraging-armor-bark.jpg` |
| `models-local/light-armor/mithril-black/` | Skyy's black-leather Mithril set (`python tools/make_black_mithril.py`, vanilla-derived, never committed); `models-local/vanilla-sets/<metal>/` = untouched vanilla set copies for Blockbench |
| `models-local/player/` | vanilla Player.blockymodel + Player_Texture.png (Outlander_1) for Blockbench fit checks (vanilla, never committed) |
| `models-local/light-armor/<tier>/` | Blockbench work models: `Chest.blockymodel` + `Chest_Texture.png` + previews made by `python tools/make_light_chest.py <Tier>` from the vanilla chest (vanilla-derived, never committed); `vanilla/` = the untouched vanilla copy |
| `.claude/worktrees/` | Claude Code agent worktrees (removed automatically) |
| outside the repo | game files + `UserData` (read-only except the deploy), Claude's memory (`C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK\memory\`); the other folders in `Hytale mods WORK` are Skyy's |

## Moved on 2026-10-05 (old name -> new place; old build-script comments still use the old names)
| Old | New |
|---|---|
| HANDOFF.md sections 1 + gear locks / 3 / 4 / 5 / 6 | `docs/handoff/design-locks.md` / short table in `HANDOFF.md` + `docs/handoff/versions-history.md` / `docs/handoff/state-2026-09.md` / `docs/handoff/design-notes-2026-09.md` / `docs/log/` (section 2 + COMMAND RULES stayed in HANDOFF.md) |
| OPEN-QUESTIONS.md (Q&A block, beta / round 8 / round 9 blocks, spec blocks) | `docs/answered/<topic>.md` (word for word, one line each); open ones stayed |
| TEST-CHECKLIST.md sections | `docs/tests/2026-09-pre-beta.md`, `2026-09-beta.md`, `2026-10.md` |
| `SkyWynn-*.md` (except the Mod-Roster), `Skyy<Mod>-Plan.md` (except SkyyGear-Plan) | `docs/plans/` |
| `DESIGN-STATUS.md`, `BETA-TEST.md`, `SkyWynn-Mod-Roster.md`, the old `RESUME.md` | `docs/archive/` |

Proof nothing was lost: `python tools/docs_check.py` (every line of every old doc is still in the repo; no new broken paths).

## Search recipes (cheap)
- A decision: `grep -n "<word>" docs/answered/*.md` - add `| tail` for the newest.
- What happened to a mod: `grep -n "SkyyGear 0.2" docs/log/*.md`; its tests: `grep -n "SkyyGear" docs/tests/README.md`.
- Current version of a mod: `grep -n "SkyyGear" HANDOFF.md` or the SET in `tools/deploy_set.py`.
- A class: open `research/classes/<Class>.md` (or its HTML page); all class answers: `docs/answered/classes.md`.
