# Architecture consolidation - from 31 Skyy mods to one core library + 8 modules

*Local spec 2026-10-10. Spec only: nothing is built, no mod, tool or doc was changed. Owner: Skyy (they/them). Skyy's ask, word for
word (docs/answered/project.md 2026-10-10): "we made some great changes to the ui and menu system. can we do something similar to the
actual architecture of the pack and how it runs? compact mods together, reshape how they work to improve the ease and flow of the
system?" Every number below was measured on the SET of `tools/deploy_set.py` (2026-10-10 evening) and the live test world; nothing
was estimated unless it says so.*

## In plain words (for Skyy)

Today SkyWynn is 31 separate jars (29 real mods + 2 probes). Every jar carries its own private copy of the same plumbing: the Server
Setup kit, the UI kit, the profile helper, the bridge helper, the movement protocol. When one of those gets a fix, 27 jars have to be
rebuilt one by one before everybody has it. Mods that belong together (Skills / Classes / Trees, Gear / Armory, Coins / Bank / Bazaar /
Auctions) talk through dozens of bridge keys and are tied by 13 "deploy these together or STOP" rules plus about 25 rollback floors
that nobody can keep in their head. Each deploy copies 31 jars, checks 31 "ready" lines, writes 31 HANDOFF rows and 27 Server Setup
tabs.

The proposal, like the hubs did for the menu: **one shared library (SkyyCore)** that every module loads instead of copying, and **8
feature modules** cut along the hubs (Character, Gear, Storage, Economy, World, Social, Menu, Professions), with Pets staying on its own
for now. The Hytale engine already supports this: a plugin manifest can declare `Dependencies`, the loader orders plugins by them, and a
plugin can see the classes of the plugins it depends on (section 2 - one probe still has to prove the last point in game).

Nothing a player sees changes: every command, alias, item id, bridge key and saved file keeps working. Saved data moves once, by a
directory rename that can be undone, with a backup and a verified snapshot first. We do it in phases, lowest risk first, each phase one
ultracode round, after the Hytale 0.7 release-day fixes so that bugs stay attributable.

## 0. Why: what the 31-mod layout costs today (measured)

| Cost | Measured | Where measured |
|---|---|---|
| Jars in the SET | **31** (29 mods + SkyyGatherProbe A/B), 9.84 MB on disk, **1,486 classes** | `tools/deploy_set.py` SET, `Skyy<Mod>/<Mod>-<ver>.jar` |
| Config kit copies | the 7 `Cfg*` classes are in **27 of 31 jars** = 189 classes, **3.12 MB** of class bytes (uncompressed) for one 116 KB kit | jar listings |
| Other duplicated helpers | `pkey()` profile helper in 20 scripts, a `bridge()` helper in 28, MoveSync in 3 (Skills, Accessories, Gear), the settings registry client in 15, the UI kit's `Sky*` runtime classes 30 copies; the Hubs spec adds a `HubBar` copy per hub mod (~20 more) | grep of the newest build scripts; `research/Hubs-Spec.md` 2.2 |
| Kit version drift | the config kit shipped as 1.0 in 18 jars, 1.1 "at each adopter's next version"; the UI kit freezes 1.2 / 1.3 / 1.4 output per jar. A kit fix reaches a mod only when that mod is rebuilt | `tools/CONFIG-CONTRACT.md` "Kit versions", `tools/skyyui.py` header |
| Cross-mod bridge | ~150 distinct key families; `profile:*` read by 20 mods, `coins:fn:*` by 11, `skill:fn:level` 188 references, `class:skill` 126, `settings:*` 180+ | grep `"<prefix>:` over the newest scripts |
| Version-pair rules | **13 STOP checks** in `deploy_set.main()` + **~25 FLOOR comments**; 6 of the 13 are Skills <-> Classes <-> Armory handovers | `tools/deploy_set.py` |
| Load order | asset packs load in text order of `"<version> <Mod>"`, so "who wins a shared asset path" flips with version numbers; no dependency can be pinned because the identifier changes every version | `research/Accessory-Table-Spec.md` l.220-231 |
| World config | **617** mod keys in the world's `config.json` (`Saves/HUD mod`), **368** are `Skyy:` keys, **31** enabled - 337 dead per-version keys | the live config.json (read) |
| Data folders | **37** `Skyy_*` folders in the world's `mods/` (31 live + 5 stale versioned ones + `Skyy_Market`) | the live `mods/` folder (read) |
| Server Setup | **27 tabs** (one `config:def:<Mod>` per jar with the kit); the Mods list shows 29 entries | jar listings |
| Deploy | backup = 31 jars + 37 folders (18 MB each, 5 kept), smoke test waits for 31 ready lines (~45-60 s), `record_deploy --mod` once per mod, HANDOFF table 31 rows | `backups/`, `tools/smoke_test.py`, `HANDOFF.md` |
| Build artefacts | **271 patch scripts** in `tools/`, **218 harness files**, 29 generated scripts of 0.04-1.73 MB (Gear 1.73 MB, Skills 1.21 MB, Armory 0.93 MB) | `ls tools/*_patch.py`, `ls Skyy*/test_*.py` |
| Churn | **118 DEPLOYED** and 108 READY lines in the first 10 days of October; the Monk "Zen" rename touched 5 mods (Skills, Classes, Trees, Profiles, Menu) = 5 builds, 5 harnesses, 1 new STOP rule | `docs/log/2026-10.md` |
| Commands / systems | 73 `registerCommand` sites, 103 `registerSystem` sites across 29 mods - each mod re-implements the Adventurer group rule and the lint has to police it 29 times | grep |
| 0.7 update | the audit covered 24 mods one by one: BROKEN 3, RISKY 9, **9 build scripts stop on 0.7 data**; fixing a kit problem means touching every adopter | `research/PreRelease-Compat-Audit-1002.md` |

What a player or server owner feels: 29 entries in the Mods list and 27 Server Setup tabs for one pack; permission nodes that change
every update (`skyy.0.5.1_skyyislands.command.island`, a known limit); more Hytale start-up work (27 copies of the same classes
verified and initialised - 1,486 classes where ~900 would do).

## 1. Target modules

### 1.1 The merge map

Module names keep the best-known name where a module absorbs others (SkyyGear, SkyyMenu); new names where none of the old ones fits.
"Hub" = where its pages show (Hubs spec). A module may register tabs in several hubs; hub tabs and module boundaries are independent.

| # | Module (jar) | Absorbs (today's SET pin) | Hub(s) | Why these belong together (data + bridge coupling) |
|---|---|---|---|---|
| 0 | **SkyyCore** (library, no gameplay) | the kits: `tools/skyycfg.py` classes, UI kit runtime (`Sky*`, HubBar, grid fill, status helpers), settings registry classes (SkyyMenu's `SetReg / SetStore / Set*Fn`), `pkey` + bridge helpers, MoveSync, journaled file IO, ready-line / logging, permission helpers; the Sky Window theme textures | - | section 2 |
| 1 | **SkyyCharacter** | SkyyProfiles 0.1.9, SkyyClasses 0.1.19, SkyySkills 0.4.30, SkyyTrees 0.3.5 | Character | the class is picked at profile creation and locked; class XP, Mana, class perks and path trees are one state machine (`skill:fn:level` 188 refs, `class:skill` 126, `tree:fn:*`); **6 of 13 STOP rules** and the Monk / Zen / abilities rounds all touched exactly these; saved player modifiers (`skyyskill_*`, `skyytree_mana`) are managed by Skills + Trees together |
| 2 | **SkyyGear** | SkyyGear 0.2.22, SkyyArmory 0.1.20, SkyyWardrobe 0.1 (Requip 0.2) | Smithing, Storage (Requip tab) | Armory ships the items (821 asset files), Gear gives them levels, rarity, speed tiers and recipes (Gear 0.2.16 <-> Armory 0.1.15 STOP, UT floor, `armory:*` 12 key families read by Gear); Requip stores gear and the Smithing hub crafts into it (`wardrobe:fn:*`, the stamp Gear 0.2.23 must copy) |
| 3 | **SkyyStorage** | SkyySacks 0.7.16 (Bags v2 0.8), SkyyCollections 0.2.8, SkyyAccessories 0.5.11, SkyyVault 0.1.5 | Storage, Character (Accessories + Collections tabs), Smithing (Recipes tab) | Bags v2 makes bag levels = collection totals (`coll:fn:catTotal`) and Accessory Bag v2 copies the same shape; Collections unlocks bag and Lantern recipes (round-8 Sacks + Collections STOP, `coll:lantern` Accessories pair); `/craft` lives in Sacks and is gated by the bench accessories; Skyy's public release plan already pairs "Pocket Dimension" + "Skyy Accessories". Vault = the item store shared across profiles |
| 4 | **SkyyEconomy** | SkyyCoins 0.1.5, SkyyBank 0.1.7, SkyyBazaar 0.1.7, SkyyAuctions 0.1.3, SkyyMerchants 0.1.1 | Market, Storage (Bank tab) | Skyy's own 2026-09-24 plan (`docs/plans/SkyyEconomy-Plan.md`); every part moves coins (`coins:fn:*`), shares the `market:veto` wall and the Bazaar / AH / Merchant "never sold" rules; Merchants are the NPC shops that plan reserved |
| 5 | **SkyyWorld** | SkyyIslands 0.5.5, SkyyWorldGen 0.5, SkyyMobs 0.1.5, SkyyExploration 0.2.5 | World | zones are one idea in four jars: WorldGen makes the zone islands, Mobs levels by zone (`mob:fn:levelAt`), Exploration's spots / luggage / titles and Gear's chest loot read that same level, Islands owns the private islands and `/hub`; the Mobs <-> Gear <-> Skills STOP trio becomes one module-version floor |
| 6 | **SkyySocial** | SkyyParty 0.1.7, SkyyGuilds 0.1.6, SkyyEssentials 0.1.9 | Social | party + guild chat, TPA buttons on the party page (`ess:fn:tpa`), `/trade`, `/msg`, the chat mirror; all per-player (not per-profile) data |
| 7 | **SkyyMenu** (Interface) | SkyyMenu 0.3.17, SkyyHud 0.3.18, SkyyRanks 0.1.1 | Settings, the menu itself | the menu, Settings page, Server Setup, HUD editor and the rank editor are the admin / UI shell; HUD widgets only read bridges; all per-player data; keeps the name because "SKYY MENU" is a planned public release |
| 8 | **SkyyProfessions** | SkyyFishing 0.1.2, SkyyCooking 0.1.6 (+ the coming gathering ladder items, Enchanted items, farming tools) | Character (Skills tab stats) | skill content packs: many items (199 + 448 asset files), XP through `skill:fn:addxp`, benches that pull from bags; neither has saved per-player data beyond what Skills holds |
| - | **SkyyPets** stays alone (0.2.3) | - | Character (Pets tab) | changing fast (0.1 -> 0.2.3 in two days), has its own removal floor (pet creatures saved in chunks), and may become a public standalone. Merge into SkyyCharacter when it reaches 1.0 if Skyy wants |

Result: **10 jars** (Core + 8 modules + Pets) instead of 31. Roughly 900 classes instead of 1,486 (27 kit copies gone), 9 Server Setup
pages (one per module, categories grouped by part) instead of 27, 10 ready lines, 10 HANDOFF rows.

### 1.2 What must stay separate

| Keep separate | Why |
|---|---|
| Probes (SkyyGatherProbe A/B, SkyyUiProbe, SkyyKeyProbe, SkyyTownProbe, SkyyPetProbe, SkyyMonkProbe, SkyyReelProbe) | throwaway, op-only; they are retired after one test and never merged. The two Gather probes leave the SET at the first merge deploy |
| Third-party pack mods (`PACK_THIRD_PARTY`) | other authors' files and licences; `deploy_set` keeps enabling them; our modules only react to their item ids at runtime (PROJECT-RULES 2) |
| SkyyPets (for now) | above |
| Anything an owner switches off as a whole | stays a **part switch** inside its module (`part.<name>` rows, Server Setup), as SkyyMerchants / Gear already do - a part off = its commands say "switched off", its systems idle, its data untouched. No jar needs to be removed to turn a feature off |
| Public CurseForge releases (Pocket Dimension, Skyy Accessories, Skyy Menu) | built from the same parts with a build flag that INLINES SkyyCore (section 2.4), so a public mod stays one jar with zero dependencies, as the design lock says |

### 1.3 Alternatives considered

- Collections into SkyyCharacter (it is a Character hub tab): rejected - its data couples to bags (Bags v2 levels), recipe unlocks and
  the Lantern, not to classes. Hub tab placement is unchanged either way.
- Accessories into SkyyGear (items with rarity): rejected for the same reason plus the public-release pairing; the Accessory Table and
  `/craft` gating are bag-side rules.
- Essentials into SkyyMenu (it holds the chat mirror, an admin tool): rejected - 11 of its 12 commands are player-to-player.
- One giant SkyWynn jar: rejected - every round would rebuild everything, no partial rollback, no standalone public cut, and a 7 MB
  build script that no agent can hold in context.

## 2. SkyyCore - one shared library jar

### 2.1 What goes in (code only - Core owns no saved data, no commands, no gameplay)

| Piece | From | Notes |
|---|---|---|
| Config kit `CfgRows / CfgLog / CfgHist / CfgSaveTask / CfgFile / CfgFn / CfgPub` | `tools/skyycfg.py` | today compiled into each jar's own package; becomes `com.skyy.core.cfg.*`, one copy. Each module still passes its own rows (DATA) to `CfgPub.start(...)`; the bridge contract (`config:def:<Mod>` etc.) is unchanged |
| UI kit runtime | `tools/skyyui.py` Java emitters (`Shell`, grid fill methods, status colour methods), `HUB_BAR_JAVA` (Hubs spec 2.2) | the kit stays a BUILD-time Python module for markup; only the Java helper classes move to Core so a kit fix ships once. The Sky Window textures (`Common/UI/Custom/SkyyKit/*`) ship in Core's asset pack ONCE - answers Hubs spec 7.1(b) |
| Hub tab registry | Hubs spec 2.1 (`hub:tab:*`, `hub:def:*`, `hub:last:*`) | the registry stays on `skyy.bridge` (so a module without Core still works); Core adds the `HubBar.build / handle` helper |
| Settings registry classes | SkyyMenu `SetReg / SetStore / SetRegFn / SetGetFn / SetSetFn / SetDefCfg` | the classes move; the Settings PAGE, `/settings` and the saved files stay in SkyyMenu (which starts the registry). Without SkyyMenu nothing changes, as today |
| Profile + bridge helpers | the `pkey(UUID)` and `bridge()` snippets in 20 / 28 scripts | `Core.pkey(u)`, `Core.bridge()`, `Core.fn(key).apply(...)` with the never-throws rule; contract unchanged (`tools/PROFILES-CONTRACT.md`) |
| MoveSync | `tools/skyymove.py` | one copy; the `move:*` protocol is unchanged |
| Journaled file IO | the patterns of SkyySacks (tmp + fsync + atomic rename + read back), SkyyWardrobe (write-ahead journal + crash repair), SkyyProfiles (settle window), the kit's History snapshot | `Core.io.atomicWrite / readBack / Journal / RunOnce / Snapshot` - the PROJECT-RULES 4 migration rule as code, used by every data migration in this spec |
| Logging + ready line | every plugin's `[<Mod>] <ver> ready` + the SEVERE discipline | `Core.ready(plugin)` prints the exact line `smoke_test.py` expects; per-part lines `[<Module>] part <name> ready` for the harness |
| Permission helpers | the COMMAND RULES (Adventurer group on every player node, empty groups on admin sub-commands) | `Core.cmd.player(cmd)`, `Core.cmd.admin(cmd, node)`; lint and crosscheck keep checking the result |
| Item safety | metadata-free grid stacks, the `market:veto` map lookup, "count before and after" move helper | shared helpers; the rules stay in HANDOFF section 2 |

Core's own bridge key: `core:version` -> String (semver). Nothing else.

### 2.2 How Hytale plugin dependencies and load order work here (engine facts, read from `HytaleServer.jar` 0.6.8, read-only)

| Fact | Status | Evidence |
|---|---|---|
| A manifest may carry `Dependencies`, `OptionalDependencies` and `LoadBefore`, each a map of plugin identifier -> semver range (`PluginManifest.getDependencies() -> Map<PluginIdentifier, SemverRange>`) | VERIFIED (class strings + bytecode) | `com.hypixel.hytale.common.plugin.PluginManifest`, `$CoreBuilder` (`dependency`, `optionalDependency`, `loadsBefore`) |
| Load order is a dependency graph: `Mod.calculateLoadOrder(Map, BiPredicate, List)` adds an edge per `Dependencies` entry (checking the semver range with the predicate), per `OptionalDependencies` entry that is present, and per `LoadBefore`; `ModLoadOrderException` types `CYCLIC_DEPENDENCY`, `MISSING_DEPENDENCY`, `MANUAL_ORDER_CONFLICT`; plugins with no edge load in text order of the identifier | VERIFIED (bytecode of `calculateLoadOrder`) | `tools/dev/bc.py` on `Mod#calculateLoadOrder`; the text-order fact is `research/Accessory-Table-Spec.md` l.223 |
| A missing or wrong-version dependency refuses the plugin: `MissingPluginDependencyException` "Missing dependency ... because version of dependency ..." | VERIFIED (strings) | `PluginManager` |
| Every plugin has its own `PluginClassLoader` (parent = the server). A `PluginManager$PluginBridgeClassLoader` exists whose `loadClass0(name, PluginClassLoader)` walks `getDependencies()` and `getOptionalDependencies()` of the asking plugin's manifest - i.e. a plugin can load classes from the plugins it declares as dependencies ("bridge", `bridgeResources`, `childFirst` in `PluginClassLoader`) | MECHANISM SEEN, **UNVERIFIED in game** | strings + bytecode of both classes. Probe C1 below must show a module calling a Core static method at runtime with `-Xverify:all` |
| Identifier = `"<Group>:<Name>"` (world config keys `Skyy:0.3.17 SkyyMenu`). Our `Name` carries the version, so no dependency can name us today | VERIFIED | `skyybuild.manifest()`, the live config.json |
| `PluginManager.DISABLE_DYNAMIC_DEPENDENCIES` exists (a switch around the bridge loader) | SEEN, meaning UNVERIFIED | `PluginManager` strings |
| Semver range syntax accepted by `SemverRange` (`">=1.0.0 <2.0.0"`? `"^1.0.0"`?) and the exact JSON shape of `Dependencies` | UNVERIFIED | probe C1 tries both and reads the parse error |

**Consequences for the design**

1. **Stable plugin names.** SkyyCore must be `Group "Skyy", Name "SkyyCore", Version "1.0.0"`; a module declares
   `"Dependencies": {"Skyy:SkyyCore": ">=1.0.0 <2.0.0"}` (exact string pending C1). Modules should get stable names too
   (`Skyy:SkyyEconomy`), which also (a) makes world config keys stable - no more 337 dead per-version keys and no
   `disable_prefix` dance, (b) fixes the known limit that auto permission nodes carry the version (Server-Setup-Spec 8.4.6),
   (c) lets a module version-pin another module when it must (`OptionalDependencies` for order only, `deploy_set` for floors).
   Cost: the design lock "version at the start of the display name so they sort together" goes; the Mods list sorts `Skyy*` by name
   instead (same effect) and the version shows in the Version column. **Question 1.**
2. **Only Core is a hard dependency.** Feature modules keep ZERO manifest dependencies on each other (the standalone lock, and
   Skyy's public releases). Cross-module calls stay on `skyy.bridge` exactly as today. `OptionalDependencies` are used only where load
   order matters for assets (none known today - the settings `settings:def:*` drain and the config `config:def:` scan were built to be
   order-free).
3. **Public releases inline Core** (2.4), so they have no dependency at all.
4. **Plan B if C1 fails** (a dependency's classes are NOT visible): the kits keep being copied into each jar as today, just into 10 jars
   instead of 31. Every other part of this spec still holds; the saving is 3x instead of 27x on kit copies.

### 2.3 Probes before any merge (phase 0, one lean round, one Skyy test)

| Probe | Shows |
|---|---|
| C1 cross-jar class | `SkyyCoreProbe` (Name "SkyyCoreProbe", Version 0.1.0) exports a static method + a class; `SkyyDepProbe` declares the dependency and calls it in `setup()`; with the server's `-Xverify:all` equivalent in `tools/ci/crosscheck.py` (loader per jar + a bridge loader stand-in) AND in the offline smoke server. Also: the dependency missing -> the exact refusal line; version out of range -> the line; both semver syntaxes |
| C2 stable names | a stable-name manifest's world config key, `enable_in_world` with it, the auto permission node it produces (`skyy.<name>.command.<cmd>` without a version?) |
| C3 Core asset pack | the dependent's inline page uses a texture that only the Core jar ships (`SkyyKit/Probe.png`): renders or "could not find texture" |
| C4 unload / reload | `/plugin reload`-style paths: does a dependent survive Core staying loaded; what happens when Core is disabled in the world while a dependent is on (expected: `MISSING_DEPENDENCY`, the dependent refuses to load, the world still starts) |

Each result goes into this spec's section 2.2 table (VERIFIED / FAILED) before phase 1 starts.

### 2.4 Build side

- `tools/skyybuild.py`: `B.manifest(name, version, ..., deps={"Skyy:SkyyCore": RANGE})`, `B.core_classes(J)` returns the Core class
  pool for compile-time references, `INLINE_CORE=True` compiles the kit classes into the module's own package instead (public
  releases, Plan B). One switch, same part code.
- `tools/skyycfg.py` keeps generating Java; `emit(..., core=True)` emits references to `com.skyy.core.cfg.*` instead of classes. Kit
  version drift ends: the kit version is Core's version.
- `tools/skyyui.py`: unchanged for markup; `HUB_BAR_JAVA` / `Shell` Java goes into Core's build; `SUI.verify()` still runs per module.
- `tools/ci/crosscheck.py`: the rule "a reference into ANOTHER Skyy jar is refused" gets ONE exception: references into the pinned
  SkyyCore jar, checked for access like engine references. Everything else stays refused.

## 3. Data migration per merge

### 3.1 Rules that apply to every module (the Economy plan's 8 rules, generalised)

| # | Rule |
|---|---|
| M1 | **Bridge keys, command names, aliases, item ids, permission nodes written by `requirePermission` stay byte for byte.** Third-party mods, HUD widgets, players' muscle memory and `/rank` grants on explicit nodes see no change. The only keys that change are the per-mod publishers `config:def:<Mod>` / `config:fn:<Mod>` / `config:epoch:<Mod>` (one per module now) - SkyyMenu is the only reader |
| M2 | **Data folders move once, by rename:** `mods/Skyy_SkyyBank/` -> `mods/Skyy_SkyyEconomy/bank/` at the module's first start, before anything is read: (1) refuse if `Skyy_SkyyEconomy/bank/` already exists and the old folder too (log SEVERE, part stays off), (2) `Files.move` (same volume = atomic directory rename, no bytes copied or rewritten), (3) read the folder listing back, (4) write the run-once marker `Skyy_SkyyEconomy/migrated.properties` (`bank=<time>,<file count>`), (5) one INFO line. The old mod's `config.properties`, `history/`, logs and per-profile files keep their names and bytes - only the parent changes. **Question 3** offers "leave the folders where they are" as the alternative |
| M3 | **Config files + Server Setup history:** each part keeps its own file (`FILES=[".../bank/config.properties", ...]`), so no line is rewritten and the History snapshots stay valid. Row keys stay; a key that collides across parts (`parts`, `part.*`) is prefixed with the part name and listed in `ALIASES` (the kit already supports aliases) so hand-edited lines and `/modconfig` codes keep working. Categories show as "Bank - Interest" etc.; the kit's 16-category cap needs raising to 32 (kit 1.2, one constant + the Menu's tab strip paging) |
| M4 | **World config:** the merged mods' names go into `RETIRED` (all their `Skyy:<ver> <Mod>` keys switched off on every deploy - the mechanism the Economy plan asked for exists since round 9); the module key `Skyy:SkyyEconomy` is enabled. A module also **refuses to start a part whose bridge publisher already exists** (`coins:fn:get` present before Economy puts it = an old SkyyCoins jar is still enabled): SEVERE + that part off + a chat line to admins. A half-merged world therefore never runs two coin systems |
| M5 | **One-time setting migrations** (PROJECT-RULES 4) are unchanged and now live in `Core.io.RunOnce` + `Snapshot`: only untouched defaults rewritten, verified History copy first, change-log line with Undo, marker, bytes + line endings kept |
| M6 | **Rollback floor per module** = "never below the first module version once it started" PLUS every floor of its parts, carried over word for word into `deploy_set.py`. Rollback = `unmerge SkyyEconomy` (a new tool under `tools/`): game closed, backup first, renames the part folders back, puts the old jars back into the SET, the module into RETIRED. The journal of M2 says exactly what to rename back |
| M7 | **Proof before deploy:** `merge_verify` (a new tool under `tools/`) snapshots every per-profile file, balance, listing, pool and config line of the parts on a scratch copy of the live world, starts the module on it (smoke-test style), snapshots again, diffs: zero differences except the moved paths and the marker. Ultracode harness must + a Skyy test |
| M8 | **Player-visible commands unchanged.** `/bank`, `/bz`, `/ah`, `/pay` are registered by the module as before; shortcuts open hub tabs as the Hubs spec says. Permission groups: `Core.cmd.player()` applies the Adventurer rule |

### 3.2 Per module

| Module | Folders renamed (old -> new) | Floors carried over | Special |
|---|---|---|---|
| SkyyEconomy | `Skyy_SkyyCoins` -> `Skyy_SkyyEconomy/coins`, `..Bank` -> `/bank`, `..Bazaar` -> `/bazaar`, `..Auctions` -> `/auctions`, `..Merchants` -> `/merchants` | Auctions 0.1.1 `48h:1200`; Merchants "part.merchants off before removing"; Bank `state.properties` paidThrough | the stale `Skyy_0.1 SkyyCoins`, `Skyy_0.1.1 SkyyCoins`, `Skyy_Market` folders are left alone (listed for Skyy to delete) |
| SkyySocial | Party, Guilds, Essentials -> `Skyy_SkyySocial/<part>` | none | per-player data only |
| SkyyProfessions | Fishing, Cooking -> `Skyy_SkyyProfessions/<part>` | Fishing: rods / reels / fish become unknown items if the jar is removed (ids unchanged, so the module keeps them) | - |
| SkyyMenu | Hud, Ranks -> `Skyy_SkyyMenu/hud`, `/ranks`; Menu's own files stay at the root of `Skyy_SkyyMenu/` | Ranks: never removes `hytale:Adventurer` | **Ranks rewrites grants once**: every grant / deny whose node is a versioned auto node (`skyy.<ver>_<mod>.command.<cmd>`) becomes the stable node of the same command, logged with Undo (the kit's change-log line) - this turns the known limit into a one-time fix |
| SkyyWorld | Islands, WorldGen, Mobs, Exploration -> `Skyy_SkyyWorld/<part>` | Islands never 0.5; WorldGen: worlds `skywynn_z1` / `skywynn_proof2` name structures in the jar - the module must ship them forever; Mobs level plates strip rule; Exploration luggage `luggage.enabled=false` rule | island files keep `<key>.properties` names; `/zone`, `/island`, `/hub` unchanged |
| SkyyStorage | Sacks, Collections, Accessories, Vault -> `Skyy_SkyyStorage/<part>` | Sacks 0.7.7 and (after Bags v2) 0.8.0; Collections 0.2.3 rewards file; Accessories talisman ids | waits for Bags v2 round 1 + Accessory Bag v2 (H7) to be LIVE and tested first - never stack a merge on a live data migration |
| SkyyGear | Gear, Armory, Wardrobe -> `Skyy_SkyyGear/gear`, `/armory`, `/wardrobe` | Gear 0.2 History copy, 0.2.11 unid bags, 0.2.14 UT bags, 0.2.15 set.mining lines, 0.2.16 + Armory 0.1.15 UT items; Armory 0.1.6 / 0.1.7 item ids; Wardrobe 0.2 `requip/` | waits for Requip R1-R4 + Smithing R3 live and tested; the `SkyyRequip` stamp and all `gear:*` / `armory:*` / `wardrobe:*` keys unchanged |
| SkyyCharacter | Profiles, Classes, Skills, Trees -> `Skyy_SkyyCharacter/<part>` | Profiles 0.1.5 (deleted profiles), Skills 0.4.6 / 0.4.15 / 0.4.25 (saved modifiers: switch rows off + one login before any rollback), Trees 0.3 (node levels), 0.3.3 path picks, Classes 0.1.14 Monk | the profile switch (`profile:busy`, settle window) is the single most sensitive path in the pack: the harness replays the SkyyProfiles switch fixtures with every part in one JVM; `profile:fn:key` stays the contract (Core only wraps it) |

### 3.3 Bridge aliases

No bridge key is renamed, so no alias is needed. One rule for later: when a module ever retires a key, it keeps publishing it for two
module versions with a WARN on first use (the `sacks:freebags` pattern).

## 4. Build tooling impact

| Area | Today | After |
|---|---|---|
| Script layout | one generated 0.04-1.73 MB script per mod version; a module script of 5 merged mods would be 3-4 MB - too big for a patch chain or an agent's context | `Skyy<Module>/build_skyy<module>_<ver>.py` = a thin assembler (manifest, Core dep, part list, asset copy) + `Skyy<Module>/parts/<part>.py` = one file per old mod (`def build(J, PKG, core, cfg_rows)`), carved from the current generated scripts (for Skills / Trees / Classes / Vault from the EDITED lineage, RESUME "Never forget"). A part file is 40-1,700 KB, the same size agents handle today |
| Patch convention | `tools/<mod>_<ver>_patch.py` rewrites the whole generated script | `tools/<module>_<ver>_patch.py` edits the part file(s) it names and bumps the module version; parts untouched by a round are byte-identical (the harness asserts it, like today's class compares). Two builders may work on two parts of one module in parallel (different files); the assembler builds once |
| Versions | 31 version strings, pins in SET, HANDOFF, record_deploy per mod | semver per module (`1.0.0` at merge, patch bumps for lean rounds, minor for data changes). Inside the docstring each part keeps its own change list, so `docs/handoff/versions-history.md` history stays readable |
| Harness | 218 files, one per mod version | one `test_skyy<module>_<ver>.py` running each part's checks in ONE JVM plus the cross-part checks (the fake bridges of today become real calls); the merge rounds add `merge_verify` (3.1 M7) |
| `deploy_set.py` | SET 31, 13 STOP checks, ~25 floors, RETIRED 7 | SET ~10, STOP checks only for cross-module floors (today's 13 reduce to about 4: Gear <-> Character staff / wand handovers, World <-> Gear <-> Character mob curve, Multitools -> Gear), floors grouped per module, RETIRED + the 22 merged names. `enable_in_world` no longer needs `disable_prefix` once names are stable |
| CI | `crosscheck.py` 26-31 loaders, 5 s; `lint.py` finds "the newest build script of a mod" by name | crosscheck: one loader per module + Core, the Core reference exception (2.4); lint learns `parts/`; a new check: a part never references another part's classes except through the module's own `Parts` facade (so unmerging stays possible) |
| Smoke test | 31 ready lines | 10 module ready lines + per-part ready lines (`[SkyyEconomy] 1.0.0 ready (coins bank bazaar auctions merchants)`) |
| Deploy | 31 copies, 18 MB backup, 31 HANDOFF rows | 10 copies; backup copies the module folders (same bytes, fewer folders); `record_deploy --mod` once per module |
| Agent briefs | AGENT-BRIEF per mod | one line added: "edit only `parts/<part>.py` your task names" |

Faster rounds in practice: a feature that spans Skills + Classes + Trees (the common case this month) becomes one module build, one
harness, one cross-check, one deploy entry, no STOP rule.

## 5. Phased plan

Rule for the whole plan: **finish and let Skyy test the running work before merging the mods it touches** - Requip (R1-R4), Smithing
(R3), Bags v2 (round 1), Hubs (H0-H9), Accessory Bag v2 (H7). Hytale 0.7 lands 2026-10-12: the release-day fix list runs on TODAY's
layout first (bugs stay attributable to one mod), then phase 0.

| Phase | Round | Touches | Parallel with | Skyy tests |
|---|---|---|---|---|
| **0 Probes** | lean (one probe pair + a report) | new `SkyyCoreProbe` + `SkyyDepProbe` (C1-C4), no SET change | the 0.7 fixes, Requip / Smithing / Bags v2 rounds | join once; `/coreprobe` prints the four results (chat mirror) |
| **1 SkyyCore 1.0** | ultracode (new jar, build tooling) | `SkyyCore/`, `tools/skyybuild.py`, `skyycfg.py`, `skyyui.py`, `crosscheck.py`, `smoke_test.py`, `deploy_set.py` (SET + Core); **pilot adopters SkyyBank 0.1.8 + SkyyParty 0.1.8** rebuilt against Core with byte-identical behaviour (class compare of everything but the kit) | nothing else that edits the kits (Hubs H1 must land before, so HubBar is in Core) | Bank + Party pages open, Server Setup Bank tab works, History intact |
| **2 SkyyEconomy 1.0** | ultracode (coins = saved data) | Coins, Bank, Bazaar (after Bazaar 0.1.8 of Bags v2 round 1 is pinned), Auctions, Merchants -> `SkyyEconomy/parts/*`; `merge_verify`, `unmerge` | phases 3 + 8 | balance, `/pay`, bank page + interest clock, bazaar buy / sell from bags, AH listing + claim, merchant shop; Server Setup Economy page |
| **3 SkyySocial 1.0** | full round | Party, Guilds, Essentials | 2 + 8 | party + TPA button, guild bank, `/trade`, `/msg`, chat mirror lines in the log |
| **8 SkyyProfessions 1.0** | full round | Fishing, Cooking | 2 + 3 | cast / bite / fight, Fishing Bench from bags, cook a dish + Grade |
| **4 SkyyMenu 1.0** | ultracode (permissions: the Ranks grant rewrite) | Menu, Hud, Ranks; after Hubs H2 + H8 are live | 5 | menu + hubs open, HUD editor layout kept, Server Setup lists 9 pages, `/rank` grants still apply (stable nodes) |
| **5 SkyyWorld 1.0** | ultracode (worlds, islands security) | Islands, WorldGen, Mobs, Exploration; after the 0.7 Islands fixes are tested | 4 | `/island`, co-op, `/hub`, `/zone 1`, mob plates + levels, luggage, titles |
| **6 SkyyStorage 1.0** | ultracode (items) | Sacks 0.8.x, Collections, Accessories 0.6, Vault; only after Bags v2 round 1 AND Accessory Bag v2 are live and Skyy-tested | 7 | pickup into the Pocket Dimension, `/craft`, bench pull, collections page, accessory boosts, vault pages, upgrade buttons |
| **7 SkyyGear 1.0** | ultracode (items, crafting) | Gear 0.2.23+, Armory, Wardrobe 0.2; only after Requip R1-R4 + Smithing R3 are live and tested | 6 | identify / reforge / upgrade / multitool, `/smithing` craft into Requip, loadout swap, every Armory weapon move |
| **9 SkyyCharacter 1.0** | ultracode (saved modifiers, profile switch) | Profiles, Classes, Skills, Trees; last, after the abilities R4 (runes, 0.7) settle | alone | create / switch / delete profile, class kit, XP + Mana, trees + respec, abilities page; `Skyy_SkyyCharacter/*` compare |
| 10 Clean-up | lean | retire the two Gather probes earlier (first merge deploy); delete stale `Skyy_0.x` folders (ask Skyy); HANDOFF / INDEX / AGENT-BRIEF rewritten for modules; the Class Balance Workbench refreshed | - | - |

Pacing: phases 2, 3 and 8 together are three heavy workflows (the 4-5 cap); phases 6 and 7 are the two biggest and run one after the
other with a Skyy test between. Each phase ends with `merge_verify` zero-diff, `crosscheck`, `lint`, `smoke_test` PASS, backup,
deploy, `record_deploy`, `tidy_local`.

## 6. Risks and how we avoid them

| Risk | Avoided by |
|---|---|
| Save data loss during the folder move | directory rename only (no bytes rewritten), refuse when the target exists, read-back, run-once marker, `backup_deploy.py` snapshot of every `Skyy_*` folder before the deploy, `merge_verify` zero-diff on a scratch copy before the real deploy, `unmerge` to rename back |
| Half-merged state (old jar + module both on) | `RETIRED` switches every old key off on each deploy; the module refuses a part whose bridge publisher already exists (M4); the smoke test fails on a duplicate command (crosscheck already FAILs a command registered by two jars) |
| Rollback after a merge | the floors are carried over per part; `unmerge` is built and tested in phase 2 before any other merge; the one-step-back jars stay on disk (`tidy_local` rule) |
| C1 fails (no cross-jar classes) | Plan B inline-core; the part layout, merges, stable names and tooling are unchanged |
| Other pack mods' integrations | nothing they could see changes: item ids, bridge keys, command names, asset paths (`Common/Items/Skyy*`) stay; only the asset pack name changes (`Skyy:SkyyGear`), and no file references pack names. BetterMap world sync stays a deploy step |
| Hytale 0.7 on 2026-10-12 | release-day fixes first on today's jars (the audit's 16-item list); phase 0 after. Later updates get cheaper: a kit fix is one Core build, and 10 jars to re-verify instead of 31 |
| Permission nodes change once (stable names) | Ranks rewrites versioned grants to stable nodes with Undo (3.2); explicit `requirePermission` nodes never change; `/rank` is Skyy's to re-check in phase 4's test |
| Build scripts too big for agents | parts split (section 4); a builder edits one part |
| A part reaching into another part's classes (future unmerge impossible) | the lint rule (section 4) + the `Parts` facade; cross-part calls go through the module's own bridge keys exactly as before |
| Public releases | `INLINE_CORE` cut per release, tested in the release kit round (Pocket Dimension first) |
| Kit version drift ends but a Core bug now hits every module at once | Core has its own harness (the existing `skyycfg_test.py` 273 checks + `skyyui_test.py` + the Core helpers), semver floor per module (`>=1.0.0 <2.0.0`), and Core 1.x stays additive like the UI kit 1.4 rule; a Core fix deploys alone |

## 7. Questions for Skyy (recommended default first)

| # | Question | Recommended default |
|---|---|---|
| 1 | Drop the version from the plugin display name (`"0.3.17 SkyyMenu"` -> `"SkyyMenu"`, version in the Version field) so modules can depend on SkyyCore and permission nodes stop changing every update? The Mods list then sorts `Skyy*` by name instead of by version | **Yes** |
| 2 | The module map in 1.1 - in particular Collections + Accessories in SkyyStorage (not SkyyCharacter), Essentials in SkyySocial, Ranks + Hud in SkyyMenu, Fishing + Cooking as SkyyProfessions, Pets alone for now | **As proposed** |
| 3 | Saved data: rename each old folder into `Skyy_<Module>/<part>/` at the module's first start (one atomic rename, undo tool), or leave the 31 old folders where they are forever? | **Rename** (tidy, one backup + verify; "leave" is zero-risk but keeps the clutter) |
| 4 | Public CurseForge mods (Pocket Dimension, Skyy Accessories, Skyy Menu): one jar with SkyyCore inlined, or two downloads (the mod + SkyyCore)? | **Inlined** (zero dependencies, as the design lock says) |
| 5 | Timing: probes now, SkyyCore right after the 0.7 release-day fixes are tested, merges in the order of section 5 (Economy first, Character last)? | **Yes** |
