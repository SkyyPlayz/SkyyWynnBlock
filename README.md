# SkyyWynnBlock

Private workspace for **SkyWynn**, Skyy's Hytale server (Hypixel SkyBlock meets Wynncraft), built as a family of standalone
`Skyy*` server mods that talk to each other through a shared JVM map instead of hard dependencies.

- **Start here:** [RESUME.md](RESUME.md) - where things live, where we got to, what is next.
- **Rules for anyone working on this:** [PROJECT-RULES.md](PROJECT-RULES.md) - PC safety, the public-repo rules, how we build and deploy.
- **Running log:** [HANDOFF.md](HANDOFF.md) - current state, decisions, what is deployed and what is only built.
- **Test list:** [TEST-CHECKLIST.md](TEST-CHECKLIST.md)
- **Plans:** `SkyWynn-*.md`, `Skyy*-Plan.md`

## Layout
- `Skyy<Mod>/build_skyy<mod>_<version>.py` - each mod version is one Python build script (Java source compiled with javassist via jpype).
- `tools/skyybuild.py` - shared build bootstrap (read its docstring). `tools/skyymove.py` - shared movement protocol.
- `tools/*_patch.py` - scripts that derive a mod's next version from the previous one.
- `tools/dev/` - engine inspection helpers (`reflect.py <Class>`, `bc.py 'Class#method'`, ...).

## Build
Needs Python with `jpype1` + `jdk4py` and a local Hytale install (the build reads `HytaleServer.jar` from it; it is never committed).

```
python SkyySacks/build_skyysacks_0.7.10.py   # build only -> SkyySacks/SkyySacks-0.7.10.jar
python tools/deploy_set.py --check            # are all pinned jars built?
python tools/deploy_set.py --yes              # deploy the whole pinned set to the test world (game closed, back up first)
```
Never pass `--deploy` to a build script; `tools/deploy_set.py` is the only deploy path (PROJECT-RULES.md section 3).
