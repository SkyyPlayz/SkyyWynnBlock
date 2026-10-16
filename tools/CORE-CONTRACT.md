# SkyWynn core contract (SkyyCore 1.0.0, 2026-10-15)

Skyy (2026-10-10, `docs/answered/project.md`): "we made some great changes to the ui and menu system. can we do something similar to
the actual architecture of the pack and how it runs? compact mods together, reshape how they work to improve the ease and flow of the
system?" and (2026-10-15) "When unifying the mods, if you can keep the structure separate enough you can work on different aspects of
the same mod at the same time so the unification doesnt slow down production".

SkyyCore is ONE library jar that Skyy mods depend on instead of each carrying its own copy of the kits. It has no gameplay, no
commands and no saved data. This is phase 1 of `research/Architecture-Spec.md`; the pilots are SkyyBank 0.1.14 and SkyyParty 0.1.9.

- Build: `python SkyyCore/build_skyycore_1.0.0.py` -> `SkyyCore/SkyyCore-1.0.0.jar`. Proof: `python SkyyCore/test_skyycore_1.0.0.py`.
- Engine facts (phase 0 probes on Hytale 0.7.2, `docs/log/2026-10.md` 2026-10-15):
  - a module's classes link against Core's classes at run time (C1);
  - a stable manifest Name gives the world key `Skyy:<Name>` and auto permission nodes `skyy.<name>.command.<cmd>` with no version (C2);
  - a texture that only Core ships renders in a module's page (C3);
  - without Core (missing or switched off) the engine skips ONLY the module, with "Failed to load 'Skyy:<Mod>' because the dependency
    'Skyy:SkyyCore' could not be found!", and the world starts (C4 - re-proven with the pilots by `smoke_test.py --drop SkyyCore`);
  - a plugin whose `setup()` throws SHUTS THE SERVER DOWN on 0.7 (MOD_ERROR). Every Core call in a module's `setup()` is guarded, and
    every Core API answers instead of throwing.

## 1. What SkyyCore exports

| Class | What |
|---|---|
| `com.skyy.core.Core` | `version()` ("1.0.0"); `bridge()` (the `skyy.bridge` map, lock-free after the first call); `get / put / putIfAbsent / remove(key, value) / call(key, arg) / has(key)` (never throw); `fn(key)` = a `SafeFn` handle: never null, its `apply(x)` never throws and answers like `call(key, x)` (the publisher's answer, or null when the key is absent / not a Function / the publisher threw); it looks the key up on every call, so a publisher that starts later is found. Presence: `Core.has(key)` or `handle.live()`; `pkey(UUID)` (the `PROFILES-CONTRACT.md` helper, verbatim); `register(mod, version, logger)` / `unregister(mod)` / `modules()`; `info / warn(mod, msg)` ("[<mod>] msg" through that mod's logger); `readyLine / ready(mod, version, detail, logger)` (the exact `[<Mod>] <ver> ready - ...` line `smoke_test.py` reads); `selfCheck()` |
| `com.skyy.core.cfg.Cfg` | a module's handle on its Server Setup kit: `CfgData.kit()` (generated; never null, never throws). `start(modsDir, logger)`, `flush()`, `shutdown()`, `cmdSet / cmdSetConsole / cmdGet`, `op(Object[])` (the `config:fn` ops SkyyMenu sends), `ok()`, `status()`; for one-time migrations: `prepare(home, logger)`, `files()`, `home()`, `histDir()`, `histStamp()`, `histList(f)`, `histBak(f, stamp)`, `histSnapshot(...)`, `logEnqueue(line)`, `logFlush()`; `kitClass(name)` / `loader()` for harnesses |
| `com.skyy.core.cfg.CfgText` | the kit's stateless helpers, same source: the properties-line parser (`split join lead isComment cont keyEnd valStart unesc esc key end value parseVals isTemplate applyEdit`), `clip`, `oneLine`, `atomicWrite` (tmp + fsync + atomic rename), `now()` |
| `com.skyy.core.ui.HubBar` | the hub tab bar (`HUBS-CONTRACT.md`), ONE copy for every module: `put(hub, tab, mod, ...)` files the tab under its mod; `removeAll(mod)` removes only that mod's arrays (still in place); `def(owner, hub, title, command, icon)` for SkyyMenu; `build / handle / open / tabs / get / map / jsonStr / run` as before |
| `com.skyy.core.ui.UiKit` | `colorOf / textOf` (result-line colours) and `gridSlot / gridSlotOf / gridSlots / gridSlotsOf` (the metadata-free ItemGrid fill) |
| `com.skyy.core.move.MoveSync` | the movement protocol v1 client (`tools/skyymove.py`); warnings go through Core, prefixed with the mod name the caller passes |
| `com.skyy.core.SafeFn` | the `fn(key)` handle (`java.util.function.Function`): `KEY`, `apply(x)`, `live()` |
| `com.skyy.core.KitLoader` | the class loader that gives each module a PRIVATE copy of the config kit (section 3). Modules never call it |
| asset pack | the 59 Sky Window files under `Common/UI/Custom/SkyyKit/`, once, byte-identical to `tools/skyyui.py`'s sha256 pins |

Bridge key: `core:version` = "1.0.0". Nothing else.

NOT API: `com.skyy.core.cfg.CfgRows / CfgLog / CfgHist / CfgSaveTask / CfgFile / CfgFn / CfgPub` (the config kit TEMPLATE). A module
that names one is refused by `tools/ci/crosscheck.py` and by the module assemble step.

**Versions.** Core 1.x only ADDS (like the UI kit 1.4 rule). A module declares `>=<the lowest Core it needs> <2.0.0`. A module that
starts using a Core 1.1 API raises its own floor (`B.link_core(pool, need="1.1.0")`).

## 2. How a mod adopts SkyyCore ("link against SkyyCore" mode)

Old-way builds keep working unchanged: nothing forces a mod to move (no flag day). To move a mod, its next version's patch does:

1. **Link.** Right after `J = B.start()`: `CORE = B.link_core(pool)`. The pool now sees `com.skyy.core.*`; `CORE["range"]` is the
   Dependencies range.
2. **Server Setup.** Add `CORE=True` to `CFG.emit(...)`. The jar then ships only `<PKG>.CfgData` (rows, files, default lines). Replace
   every call into the private kit:
   - `CfgPub.start(...)` / `CfgPub.shutdown()` -> `<PKG>.CfgData.kit().start(...)` / `.shutdown()` (guarded in `setup()`);
   - `CfgFn.cmdSet / cmdSetConsole / cmdGet` -> `CfgData.kit().cmdSet / ...`; `new CfgFn().apply(op)` -> `CfgData.kit().op(op)`;
   - migrations: `CfgRows.HOME = ...; CfgHist.init(); CfgLog.init()` -> `CfgData.kit().prepare(home, log)`; `CfgHist.snapshot / list /
     bak / stamp / DIR` -> `kit().histSnapshot / histList / histBak / histStamp / histDir()`; `CfgLog.enqueue / flush` ->
     `kit().logEnqueue / logFlush`; `CfgRows.FILES` -> `kit().files()`;
   - stateless helpers: `CfgFile.<x>`, `CfgRows.atomicWrite / oneLine / clip`, `CfgLog.now()` -> `com.skyy.core.cfg.CfgText.<x>`.
   - `HOME=` (emit, CORE only) moves the kit's folder (default `Skyy_<MOD>` = today's folder - leave it for an existing mod).
3. **Hub tab.** Drop `SUI.install_hub_bar(...)`. Use `com.skyy.core.ui.HubBar.put(...)` in setup, `HubBar.removeAll("<Mod>")` in
   shutdown, and `SUI.java_hub_build(sh, "<tab>", cls=SUI.CORE_HUB_BAR)` in the page.
4. **Kit Java.** Page helpers may call `com.skyy.core.ui.UiKit.colorOf / textOf / grid*`; profile / bridge helpers may call
   `com.skyy.core.Core.pkey / bridge`. (Keeping a mod's own tiny helper is fine when a harness pins its exact behaviour - SkyyBank keeps
   its 0.1.9 lock-free `bridge()`.)
5. **Register.** First thing in `setup()`, guarded: `try { com.skyy.core.Core.register("<Mod>", VERSION, getLogger()); } catch
   (Throwable t) { ... }`; `Core.unregister("<Mod>")` in shutdown.
6. **Manifest.** `m = B.core_manifest("<Mod>", VERSION, "<description>", PKG + ".<Plugin>", CORE)`: STABLE name (world key
   `Skyy:<Mod>`, the version only in "Version"), `"Dependencies": {"Skyy:SkyyCore": CORE["range"]}`, no asset pack unless the mod has
   assets of its own. Ship NO kit art (`SUI.kit_texture_files()` is Core's). The stable name also changes the engine's AUTO
   permission nodes from `skyy.<ver>_<mod>.command.<cmd>` to `skyy.<mod>.command.<cmd>` (crosscheck prints both as "auto", so
   "tree identical" does not show it): before switching, grep the repo and the world's `permissions.json` / rank configs (read-only)
   for the old form - for Bank and Party nothing grants it (checked 2026-10-15; their player commands use `hytale:Adventurer`, the
   admin nodes `skyybank.admin` / `skyyparty.admin` / `skyyparty.bypass` are explicit and unchanged).
7. **Guard.** Nothing in `setup()` may throw. Core's APIs never throw; wrap each Core call in `try / catch (Throwable)` anyway (a
   LinkageError from a wrong Core version would otherwise stop the server).
8. **Prove.** The harness puts Core on every child JVM: `os.environ["SKYY_HARNESS_CP"] = <Core jar>` (`tools/harness_kit.py`), and
   `tools/hub_tab_harness.py` Spec takes `hub_class="com.skyy.core.ui.HubBar", hub_owner="<Mod>", kit_in_jar=False, removed=[...]`.
   SkyyBank 0.1.14's harness has reusable parity helpers: `kit_parity` (old kit vs Core kit on a copy of live data) and
   `page_dump / page_compare` (old page vs new page through each jar's hub bar).

Rollback of an adopter to its last old-way version is safe when no saved data changed (the pilots: same files). `deploy_set` switches
the stable key off and the versioned key back on by itself.

## 3. How the config kit runs from SkyyCore

The kit's seven classes are compiled ONCE, into Core (the template; `tools/skyycfg.py core_template`). A module's `CfgData.kit()` calls
`Cfg.open(CfgData.class)`: Core makes a `KitLoader` (a child of the MODULE's class loader) that defines a private copy of the seven
classes from Core's bytes. So each module has its own kit state exactly as before - same files, same `config:def / config:fn /
config:epoch:<MOD>` bridge keys, same History and change log - while a kit fix ships once, in Core. The template differs from a per-mod
kit only where the per-mod kit had compile-time data: it reads it from the module's CfgData; the permission / item checks can call a
harness hook named in CfgData (empty in real mods); `CfgPub.start` uses `CfgData.HOMEDIR`. Proof: `python tools/skyycfg_test.py --core
SkyyCore/SkyyCore-1.0.0.jar` runs the WHOLE kit harness (265 checks, -Xverify:all) on the kit copies Core makes.

## 4. Several builders on one jar: the MODULE ASSEMBLE step

For the merges (Economy, Social, Professions, ...): one jar = several MODULES, each its own file, package, data folder, Server Setup
section and harness. Builders own a module file; one assemble step builds the jar.

```
Skyy<Jar>/modules/<id>_<ver>.py  MODULE = "<id>"  VERSION = "<ver>"  TITLE = "..."  [DATA = "Skyy_<Jar>/<id>"]  [REPLACES = "<Mod>"]  [HARNESS = "..."]
                                 def build(ctx): ...   # ctx.make / M / F / C compile into com.skyy.<jar>.<id>
                                                      # ctx.cfg(MOD="SkyyBank", ...) = its Server Setup section (CORE kit, HOME = ctx.data)
                                                      # must make <pkg>.Module (all public static):
                                                      #   String setup(JavaPlugin p)    load data, start kit / ticks, publish keys; NO engine registrations
                                                      #   void register(JavaPlugin p)   OPTIONAL - the ONLY place that calls p.get*Registry()
                                                      #   void shutdown()               normal stop: SAVE, stop, unpublish
                                                      #   void abort()                  undo a failed start: stop, unpublish, NEVER save
Skyy<Jar>/build_skyy<jar>_<ver>.py   J = B.start(); B.assemble_modules(J, "Skyy<Jar>", "<ver>" or "auto", [module files], "<description>", HERE)
```

- The jar's generated plugin runs every module's `setup()` and then its `register()` in order, each guarded: a module that throws is
  logged and stays OFF, the others run, the plugin never throws. Lines: `[<Jar>] part <id> <ver> ready - <text>` per module, then
  `[<Jar>] <ver> ready (...)`.
- **A failed start is undone - without saving.** When `setup()` (or `register()`) throws, the dispatcher calls that module's
  `abort()` (guarded) - NEVER `shutdown()`, because `shutdown()` saves and a half-started module's store may be empty or half-loaded
  (saving it would wipe the real file: coins, items). Then it puts the `skyy.bridge` map back as it was before that module started:
  a key that appeared is removed (its `*:fn:*` publishers, `rebirth:part:*`, `config:*`), a key whose value is no longer the SAME
  object is restored (e.g. another jar's publisher it replaced), a key that vanished is put back; one WARN line each. (The engine
  runs plugins' `setup()` one after another, so nothing else writes the map in that window.) So:
  - `abort()` stops whatever `setup()` may have started, also half-way, and saves NOTHING: cancel its scheduled ticks / workers
    (null-safe), drop its in-memory store, `kit().shutdown()` (the kit's own files are safe: it only writes queued edits, atomically),
    `HubBar.removeAll("<Mod>")` (in-place changes inside a shared value are not seen by the map snapshot), `Core.unregister`.
  - `shutdown()` saves - and, belt and braces, writes a data file only when that file was LOADED OK (a `LOADED` flag set at the end
    of the load), so even a wrong call can never write an empty store.
  - **Engine registrations (systems, commands, events, tasks) go ONLY in `register(JavaPlugin)`**, which runs after `setup()`
    succeeded: the engine has no unregister, so a module must not register and then fail. The assemble step REFUSES a module class
    that calls an engine registry getter (`get*Registry`, `getEventBus`) anywhere else (bytecode check, `B.registry_calls`). If
    `register()` itself throws, the line is SEVERE (smoke fails): what it registered before the throw stays live until the server
    stops - so `register()` holds only the register calls.
- **Data folders.** One folder per module, never nested in another module's folder (compared case-insensitively: `Skyy_Eco/Bank` =
  `Skyy_Eco/bank` on Windows). A module's `DATA` may not be (inside / around) a folder another SET jar owns (a standalone mod's
  `Skyy_<Mod>`, an assembled jar's module folders) - unless the module says `REPLACES = "<Mod>"` (a merge taking over that mod's
  data). `tools/ci/crosscheck.py` then refuses any set that still holds `<Mod>`, and any two jars that share a folder, so two jars
  can never write one bank. `REPLACES` is recorded in the module manifest.
- **Server Setup sections.** One `MOD` per section, unique (case-insensitive) across the jar's modules AND every other SET jar's kits
  (the kit publishes `config:def / config:fn / config:epoch:<MOD>` with a plain put - two kits on one MOD silently overwrite each
  other). A merge module that takes over a mod's section uses that mod's MOD with `REPLACES = "<Mod>"`. The assemble step refuses a
  clash; `tools/ci/crosscheck.py` CONFIG refuses two kits (one jar or two) on one section (`B.jar_config_sections` reads each kit's
  `MOD` constant from the jar).
- **One tab per section (today).** Each module's `ctx.cfg(...)` is its OWN Server Setup tab in SkyyMenu, exactly like a standalone
  mod - a 5-module jar shows 5 tabs. ONE tab per merged jar with the parts as category groups ("Bank - Interest", spec 3.1 M3,
  "Server Setup lists 9 pages") is NOT in 1.0: it needs the kit's 16-category cap raised and SkyyMenu tab paging (section 6).
- **Boundary:** the step REFUSES a module whose classes name another module's package (or any `com.skyy.*` that is not its own package
  or Core's API). Modules talk only through `skyy.bridge` and Core.
- **Versions:** each module has its own version. The jar version is the assembler's; `"auto"` = the last recorded jar version if
  nothing changed, else its last number + 1. Re-using a recorded jar version with different modules is refused.
- **Editing a module (the patch rule, spec section 4).** A module file is versioned like a build script: `Skyy<Jar>/modules/<id>_<ver>.py`.
  A round that changes module `<id>` writes `tools/<jar>_<id>_<newver>_patch.py`, which reads the CURRENT module file (the one the
  pinned jar's `.modules.json` names) and writes `<id>_<newver>.py` with `VERSION` bumped - never edit a module file in place. The
  jar's build script lists the module files; a round changes only its own module's line. Untouched modules keep their file, so their
  `source_sha256` in the new `.modules.json` stays the same (check it: a changed hash on a module the round did not own = stop).
  Keep every module file the SET or a rollback floor still names: rolling one module back = list its older file and assemble
  (`"auto"` bumps the jar). Several builders = several module files + several patch scripts; one assemble at the end.
- **Module manifest:** `Skyy<Jar>-<ver>.modules.json` next to the jar: the modules (id, version, package, data folder, Server Setup
  sections, harness, source file + sha256), the Core range, the world key.
- Proof: the Core harness builds and runs a 2-module test jar (`SkyyAsmTest`), and the smoke test loaded it on a real 0.7.2 server.

## 5. Tooling

| Tool | SkyyCore support |
|---|---|
| `tools/skyybuild.py` | `link_core`, `core_manifest`, `manifest(stable=, deps=, assets=)`, `semver / range_ok` (the engine's range forms), `key_parts / same_mod_keys` (stable and versioned keys are one mod), `enable_in_world` (switches the other form off), `assemble_modules`, `next_jar_version`, `PUBLIC_MODS` + `public_guard` (below), `jar_config_sections` (a jar's Server Setup MODs, no JVM), `registry_calls` (engine registry getters in a class's bytecode) |
| `tools/skyycfg.py` | `emit(..., CORE=True, HOME=)`, `core_template`, `core_text_java` |
| `tools/skyyui.py` | `CORE_HUB_BAR`, `CORE_UI`, `hub_bar_java_core / install_hub_bar_core`, `core_ui_java` (additive; kit 1.5 output unchanged) |
| `tools/ci/crosscheck.py` | a jar that lists `Skyy:SkyyCore` sees Core (its refs resolve and are access-checked); still refused: other cross-jar refs, the kit template, a Core dependency with no Core / outside the range, any other dependency of a SKYY jar (a third-party jar's `Dependencies` are listed "not checked"); DATA (one folder, two jars) and CONFIG (one Server Setup section, two kits) |
| `tools/smoke_test.py` | stable keys; `--drop <Mod>` (the missing-dependency boot: the dependent must be skipped with the engine's line, the rest starts) |
| `tools/deploy_set.py` | world keys from each jar's manifest; STOP when SkyyCore is not the FIRST SET entry or a dependency is missing / out of range; once Core is pinned the phase 0 probes go off |
| `tools/harness_kit.py`, `tools/hub_tab_harness.py` | `SKYY_HARNESS_CP`; compare `removed=`; every `live*` phase gets its own live copy; Spec `hub_class / hub_owner / kit_in_jar / removed / extra_phases` |

| `tools/release_pack.py` | `world-config-snippet.json` uses each jar's manifest key (stable `Skyy:<Mod>`); a shipped jar whose Core dependency is not shipped is a problem; README + MODS-LIST say SkyyCore is required |

**Pinning (main session):** `("SkyyCore", "1.0.0")` as the FIRST SET entry, then the adopters. HANDOFF gets a SkyyCore row.

**Public releases:** a mod built with `link_core` NEEDS SkyyCore. Until the spec 2.4 `INLINE_CORE` switch exists, a mod that ships
on its own (a public CurseForge cut) stays an old-way build - never `link_core`. ENFORCED: `B.PUBLIC_MODS` = SkyySacks (the Pocket
Dimension code), SkyyAccessories, SkyyMenu (docs/answered/project.md LOCKED 2026-10-03); `core_manifest(<one of them>)` and a
module `REPLACES` one of them are refused ("PUBLIC MOD") until the release kit round builds `INLINE_CORE` and passes
`public_ok=True`. Phase 4 (SkyyMenu 1.0) and phase 6 (SkyyStorage) therefore need `INLINE_CORE` first. The server pack
(`release_pack.py`) ships SkyyCore with its dependents.

## 6. Not in 1.0 - what the next phases need

- **Phase 2 SkyyEconomy (Coins, Bank, Bazaar, Auctions, Merchants):** `Core.io` journaled IO + `RunOnce` + `Snapshot` (spec 2.1 / M5)
  and the M2 folder rename (`Skyy_SkyyBank` -> `Skyy_SkyyEconomy/bank`, refuse if both exist, read back, run-once marker, INFO line)
  with its `unmerge` tool and `merge_verify` zero-diff on a scratch copy; the "part refuses to start when its bridge publisher already
  exists" guard (M4); ONE Server Setup tab per merged jar (parts as category groups, spec 3.1 M3 - today each module's section is
  its own tab, section 4): a `TAB=<Jar>` option on `ctx.cfg` + the kit's category cap past 16 (kit 1.2) + SkyyMenu tab paging.
  Each part ports its engine registrations into `Module.register` and writes `abort()` (no save) next to `shutdown()` (save behind a
  LOADED flag) - Bank's and Party's `setup()` today register before steps that can fail, so that split is part of the port. Each part = one module file (`assemble_modules`);
  Bank's module takes `Skyy_SkyyBank` with `REPLACES = "SkyyBank"` (or the M2 rename), and SkyyBank leaves the SET in the same pin.
  **Item safety helpers (spec 2.1, NOT in 1.0):** the `market:veto` map lookup and the "count before and after" item-move helper
  that Bazaar / Auctions / Merchants need - Core 1.1 (`need="1.1.0"`); until then each part keeps its own (HANDOFF section 2 rules).
- **Phase 3 SkyySocial (Party, Guilds, Essentials):** only per-player data - the module assemble step + folder rename are enough;
  Party is already on Core. The chat mirror / TPA bridges stay bridge keys.
- **Phase 8 SkyyProfessions (Fishing, Cooking):** item-heavy asset packs: assets per module (`ctx.asset`) and a check that two modules
  never ship one asset path (the assemble step refuses it today).
- **Typed bridge handles, events, shared services (spec "modules talk only through SkyyCore"):** 1.0 has only the raw bridge
  calls plus the never-throwing `fn(key)` handle. Typed handles (e.g. a `Coins` facade over `coins:fn:*`), a Core event bus and
  shared services come with the first phase that needs them (phase 2), additive in Core 1.x.
- **Later:** the settings registry classes (SkyyMenu `SetReg...`, phase 4 SkyyMenu); command helpers (not possible from Core:
  `AbstractCommand.setPermissionGroups` is protected - each command keeps the COMMAND RULES line; lint + crosscheck police it); lint
  learning `Skyy<Jar>/modules/*.py`; `INLINE_CORE` for the public CurseForge cuts (spec 2.4 / question 4).

## Tests

- `python SkyyCore/test_skyycore_1.0.0.py` - Core's API, KitLoader, Cfg, CfgText = the kit's helpers, HubBar = the per-mod HubBar (+ the
  owner rule), UiKit, MoveSync, the 2-module assemble (and its refusals: other module's class, duplicate id, no Module, changed
  module under a used jar version, nested / other-case / SET-owned data folders, no `abort()`, a registry getter outside
  `Module.register` (in `setup()` or a helper class), a `register` with the wrong signature, two modules on one MOD, a MOD a SET jar
  publishes, `REPLACES` a public mod), a module whose `setup()` throws part-way (its `abort()` runs - not `shutdown()` -, its timer
  stops, the real data file stays byte-identical, its new bridge keys go, a key it REPLACED and a key it REMOVED come back as the
  same object, `register()` never runs), a module whose `register()` throws (abort, keys undone, the next module runs), a clean
  start (register once, shutdown saves), `REPLACES` + crosscheck's DATA and CONFIG checks, `PUBLIC_MODS`, crosscheck's dependency
  scope (a Skyy jar's non-Core dependency refused, a third-party jar's not checked), the engine's own manifest parser, deploy /
  smoke / crosscheck tooling, engine-access audit.
- `python tools/skyycfg_test.py --core SkyyCore/SkyyCore-1.0.0.jar` - the whole config kit harness on Core's kit copies.
- `python SkyyBank/test_skyybank_0.1.14.py`, `python SkyyParty/test_skyyparty_0.1.9.py` - the pilots, old vs new.
- `python tools/smoke_test.py --jar SkyyCore/SkyyCore-1.0.0.jar --jar SkyyBank/SkyyBank-0.1.14.jar --jar SkyyParty/SkyyParty-0.1.9.jar`
  and the same with `--drop SkyyCore`.
