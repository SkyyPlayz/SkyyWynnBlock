# SkyyWynnBlock

Public workspace for **SkyWynn**, Skyy's Hytale server pack (Hypixel SkyBlock meets Wynncraft), built as a family of standalone
`Skyy*` server mods that talk to each other through a shared JVM map instead of hard dependencies. Every mod works alone; together they
make the pack (name idea: *Isles of the Void*).

- **Start here:** [RESUME.md](RESUME.md) - where we are, what is next.
- **Find anything:** [INDEX.md](INDEX.md) - every file and folder, plus cheap search recipes.
- **Rules:** [PROJECT-RULES.md](PROJECT-RULES.md) - PC safety, the public-repo rules, how we build and deploy.
- **Versions + build rules:** [HANDOFF.md](HANDOFF.md) - the 26 mods in the current set and the rules every build follows.
- **Open questions:** [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) (only open ones; answers live in [docs/answered/](docs/answered/README.md)).
- **Tests:** [TEST-CHECKLIST.md](TEST-CHECKLIST.md) - what to test next in game.
- **Classes:** [research/classes/](research/classes/README.md) - one file per class.

## Layout
- `Skyy<Mod>/build_skyy<mod>_<version>.py` - each mod version is one Python build script (Java source compiled with javassist via jpype).
- `tools/` - `deploy_set.py` (the pinned set), `skyybuild.py` (shared build bootstrap), the UI / config / movement kits, `<mod>_<ver>_patch.py`
  scripts that derive a mod's next version, `tools/ci/lint.py`, `tools/dev/` engine inspection helpers.
- `docs/` - answered questions, the running log, test sections, older plans and archives. `research/` - specs and research per feature.

## Build
Needs Python with `jpype1` + `jdk4py` and a local Hytale install (the build reads `HytaleServer.jar` from it; it is never committed).

```
python SkyySacks/build_skyysacks_0.7.12.py   # build only -> SkyySacks/SkyySacks-0.7.12.jar
python tools/deploy_set.py --check            # are all pinned jars built?
python tools/deploy_set.py --yes              # deploy the whole pinned set to the test world (game closed, back up first)
```
Never pass `--deploy` to a build script; `tools/deploy_set.py` is the only deploy path (PROJECT-RULES.md section 3). No game files or
other authors' assets are in this repo - vanilla-derived art is generated into the jars at build time.
