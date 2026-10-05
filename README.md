# SkyyWynnBlock

Public workspace for **SkyWynn**, Skyy's Hytale server pack (Hypixel SkyBlock meets Wynncraft), built as a family of standalone
`Skyy*` server mods that talk to each other through a shared JVM map instead of hard dependencies. Every mod works alone; together they
make the pack (name idea: *Isles of the Void*). Owner: Skyy (GitHub **SkyyPlayz**, they/them).

## Start here (people and AI agents)

1. [RESUME.md](RESUME.md) - where we are and the next steps (~60 lines).
2. [PROJECT-RULES.md](PROJECT-RULES.md) - the standing rules (PC safety, public repo, deploying, how we build, how docs are kept).
3. [INDEX.md](INDEX.md) - where every file is, what moved where, cheap search recipes.
4. Then open ONLY what your task needs:
   - [HANDOFF.md](HANDOFF.md) - the 26 mods in the current set, rollback floors, the UI + COMMAND rules every build follows.
   - [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) - only questions still waiting on Skyy.
   - [docs/answered/](docs/answered/README.md) - every answer Skyy gave, word for word, one per line, by topic.
   - [TEST-CHECKLIST.md](TEST-CHECKLIST.md) - what Skyy tests next; every test section in [docs/tests/](docs/tests/README.md).
   - `docs/log/<YYYY-MM>.md` - the running log (one line per build, deploy, test, decision).
   - [research/classes/](research/classes/README.md) - one file per class (+ easy-read HTML pages).
   - Build agents: [tools/AGENT-BRIEF.md](tools/AGENT-BRIEF.md). Cloud sessions: [CLOUD-RESUME.md](CLOUD-RESUME.md).

## How to use the files (keeps every session cheap and the project ready to hand off)

- **Search, don't read whole files.** `grep -n "<word>" docs/answered/*.md docs/log/*.md` - one line is one whole fact. The newest
  line wins; each answered file ends with a "New answers" block that beats everything above it.
- **Record work the moment it is done** (Skyy's rule): a log line in the newest `docs/log/` file, the versions table in `HANDOFF.md`
  when a version changed, `RESUME.md` "Now" / "Next", then commit + push. Finished work never lives only in chat.
- **When Skyy answers a question:** `python tools/qa_append.py <topic> <answer file> --close "<words from the question>"` (or `--no-question` for an answer nobody asked) - the answer
  goes word for word into `docs/answered/<topic>.md` and the question leaves `OPEN-QUESTIONS.md`.
- **After a deploy:** one numbered test section at the end of the newest `docs/tests/` file + a line in TEST-CHECKLIST's "Test next".
- **After editing a class file:** `python tools/class_pages.py` rebuilds its HTML page.
- **After moving or splitting docs:** `python tools/docs_check.py` must say OK (nothing lost, no broken paths).
- **Never edit** `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md` (Skyy's own design docs) or the generated `research/classes/html/`.
- Many docs mix CRLF and LF line endings (`.gitattributes` keeps bytes exact) - edit without converting them.

## Obsidian

The repo folder is also an Obsidian vault with shared settings (bookmarks in reading order, an easy-read style, markdown links that
work on GitHub too, noise folders hidden). How to open it and use it: [docs/OBSIDIAN.md](docs/OBSIDIAN.md).

## Layout

- `Skyy<Mod>/build_skyy<mod>_<version>.py` - each mod version is one Python build script (Java source compiled with javassist via jpype).
- `tools/` - `deploy_set.py` (the pinned set), `skyybuild.py` (shared build bootstrap), the UI / config / movement / art kits,
  `<mod>_<ver>_patch.py` scripts that derive a mod's next version, `tools/ci/lint.py`, `tools/dev/` engine inspection helpers, and the
  docs helpers `qa_append.py`, `docs_check.py`, `class_pages.py`.
- `docs/` - answered questions, the running log, test sections, older HANDOFF parts, plans, archives. `research/` - specs + research per
  feature (`research/cloud/` = cloud sessions' output).

## Build

Needs Python with `jpype1` + `jdk4py` and a local Hytale install (the build reads `HytaleServer.jar` from it; it is never committed).

```
python SkyySacks/build_skyysacks_0.7.12.py   # build only -> SkyySacks/SkyySacks-0.7.12.jar
python tools/deploy_set.py --check            # are all pinned jars built?
python tools/deploy_set.py --yes              # deploy the whole pinned set to the test world (game closed, back up first)
```
Never pass `--deploy` to a build script; `tools/deploy_set.py` is the only deploy path (PROJECT-RULES.md section 3). No game files or
other authors' assets are in this repo - vanilla-derived art is generated into the jars at build time.
