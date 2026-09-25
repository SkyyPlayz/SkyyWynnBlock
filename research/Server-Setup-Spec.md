# In-game server setup: build spec (SkyyMenu Mods section, the admin config registry, and the big editors)

*Written 2026-09-24 by the research workflow for Skyy's in-game server setup direction. Research only: no build script, jar, mod folder or
game file was changed. Sources: `HANDOFF.md` section 1, `SkyWynn-Server-Setup-Plan.md`, `SkyyEconomy-Plan.md`, `research/Settings-Spec.md`
(sections 1.1-1.5, 4), `research/Server-Setup-Research.md` (Server tools, Engine, Config inventory), `research/Auction-House-Spec.md`
(sections 3, 4.4, 8), and the newest build script of every Skyy mod on disk (versions in section 4). Owner: Skyy (they/them).
Review pass applied the same day: see "Review notes" at the end.*

**Skyy's direction (2026-09-24):** "in SkyyMenu in the mod section, I'd like to be able to click each mod to config in game. I'd like to make
everything doable in game to make the actual server creation and setup easier, like making NPC shops, and the NPC quests, customizing ranks
and permissions etc. Basically everything I might need to change or edit when making the server I'd like to have editable in game."
Pack goal: 100% usable solo and in private multiplayer, and ready for anyone to run a server with.

**Legend.** VERIFIED = seen in `HytaleServer.jar` (reflection, bytecode or constant pool, `tools/dev/reflect.py`, `bc.py`, `cpgrep.py`), in a
real save file (read-only), or in our own verified-in-game code. Items marked "this session" were checked while writing this spec.
UNVERIFIED = design that still needs the tests in section 8. `[SKYY?]` = a choice for Skyy; section 9 lists them with the default the build uses.

---

## 0. Verdict (plain words)

**Yes, almost all of it can be done in game, and it can be built in steps that never break a mod that has not been updated yet.**
The one item Skyy named that is **not buildable yet is NPC quests**: they wait for a future SkyyQuests mod, and this spec only defines
the hooks for it (5.3). The list "What still needs files or vanilla commands" below says what an owner still does outside the Mods section.

The core is small. Each mod **keeps owning its own settings and its own file**. It describes its settings once (name, type, default, limits,
"applies now" or "needs a restart") and puts that description plus one small function on the shared bridge. SkyyMenu only **draws** the
pages and passes clicks back to the mod. The mod checks the value, applies it, writes it to the same file and logs who changed it. If
SkyyMenu is missing, nothing changes: the mod still reads its file and its admin commands still work.

| Piece | Where | Size (rough) |
|---|---|---|
| Admin config kit (a code generator every build script imports, so each jar gets its own copy) | new `tools/skyycfg.py` | ~400 lines of generated Java |
| Mods section: mod list, a mod's config page, table editor, confirm, change log, history, export/import, `/modconfig` | SkyyMenu 0.3 | ~900 lines |
| First adopter, from day one | SkyyEconomy 0.1 (the merge round) | schema + ~60 lines |
| Every other mod adopts in its next version | 20 mods (section 7) | schema + 10-80 lines each |
| Big editors, each with its mod | NPC shops (SkyyEconomy 0.2), ranks (new SkyyRanks, right after SkyyEconomy 0.1), warps + world spawn (SkyyEssentials), island template + starter kit (SkyyIslands), market tables (SkyyEconomy). **NPC quests: not buildable yet** (future SkyyQuests; only the hooks are defined now) | section 5 |

**What a server owner gets:** SkyWynn Menu -> Mods (or `/modconfig`) -> a list of every installed Skyy mod with its version and its parts
(for example "Bank ON - Bazaar ON - Auction House OFF - NPC shops ON"). Click a mod -> its settings in tabs: ON/OFF buttons, number and
text boxes with a Set button, choice buttons, item lists, and a Default button on every row. Risky changes (money, penalties, caps) ask
"Change X from A to B?" first. Every change is logged (who, when, old -> new) and can be undone from the log. Each mod's file keeps its
last 10 versions for restore. LOCKED 2026-09-25 (Skyy). Was: 20. A mod's whole setup can be exported as a code (and a file) and imported on another world. A search box on
the list finds a setting or an editor by name ("warps", "shops", "interest") across every set-up mod.

**What still needs files or vanilla commands (known, tracked gaps):**
- **Day one: only SkyyEconomy is editable in game.** When SkyyMenu 0.3 first ships, every other Skyy mod shows its file path and a Reload
  button (2.11) until its own adopting version lands (section 7, steps 5-6).
- **Becoming admin on a brand-new server** comes before any menu can open (2.1 "First admin"): in your own singleplayer world type
  `/op self`; on a standalone server add your UUID to `permissions.json` while it is stopped, or start it once with `--allow-op` and type `/op self`.
- **Ranks** until SkyyRanks 0.1 (section 7 step 4): the vanilla chat commands `/op add|remove`, `/perm group|user ...`, `/setgroup`, or
  `permissions.json` with the server stopped.
- **NPC quests:** not yet (5.3). **A custom starting island:** the built-in island stays fixed until the template editor (5.5).
  **Profile cap above 6:** not possible at all yet, not even by file (section 9 Q16).
- **Deliberately not covered (vanilla or start-up jobs, not Skyy settings):** creating a world and its seed and world generation, the
  server's own start-up settings (name, port, player limit, launch options), whitelist, kicks and bans, op itself, backups, and other
  authors' mods. Vanilla already has `/whitelist`, `/kick`, `/ban`, `/op`, `/perm`, `/setgroup` and `/spawn set` (command classes seen in
  `HytaleServer.jar` this session); the rest is chosen when the server is created or started. The Mods list shows Skyy mods only.

**Skyy's economy question ("roll them into one economy mod, or leave separate for now?"):** it is already decided and it still holds:
**one SkyyEconomy** (coins, bank, bazaar, auction house, later NPC shops and item value), built **the round after** the separate Bank 0.1.3,
Bazaar 0.1.2 and Auctions 0.1 are tested (`SkyyEconomy-Plan.md`), so a bug found after the merge is a merge bug. The in-game setup
direction makes the merge more useful, not less: one config page with four part switches instead of four mods to manage. `/trade` goes in
SkyyEssentials (locked). This spec makes **SkyyEconomy 0.1 the first mod built on the admin registry from day one**; the old SkyyCoins,
SkyyBank, SkyyBazaar and SkyyAuctions do not adopt it, they retire into SkyyEconomy.

**Homes decided here:** ranks + permissions -> a new **SkyyRanks** mod (5.1, not SkyyEssentials), built right after SkyyEconomy 0.1
(section 7 step 4). NPC shops -> **SkyyEconomy 0.2** (after the 0.1 merge is proven). Warps editor + world spawn -> **SkyyEssentials**.
Island template + starter kit -> **SkyyIslands**. NPC quests -> future **SkyyQuests**; only the hooks are defined now (5.3).

**One registry or two?** Two small registries that share one toolkit (1.2): the player Settings registry (`settings:*`, Settings-Spec,
per-player ON/OFF stored by SkyyMenu) stays exactly as speced; the admin registry (`config:*`, this spec) is pull-only and the mod stores
the values. They share the key rules, the page shell, the atomic write, the bridge-scan and the never-throws rules.

**VERIFIED building blocks (engine facts checked this session are marked *):**
- *Built-in permission groups form a chain: `hytale:None` <- `hytale:Adventurer` <- `hytale:Builder` <- `hytale:WorldEditor` <-
  `hytale:ServerEditor` <- `hytale:Admin`, and `hytale:Admin` carries `"*"` (static init of `HytalePermissionsProvider`). So every op passes
  any `skyy*.admin` / `skyymenu.modconfig` check with no `permissions.json` edit. Legacy names map: `op` -> Admin, `default`/`adventure`/
  `adventurer` -> Adventurer, `creative` -> WorldEditor.
- *Group names must match `^[a-zA-Z0-9][a-zA-Z0-9_:\-]*$` and permission nodes `^-?\w[\w-]*(\.[\w*][\w*-]*)*$`
  (`PermissionValidation`); a leading `-` is a deny, `-*` denies everything; invalid nodes are skipped with a warning.
- *Permission check order (`PermissionsModule.hasPermission(UUID, PermissionQuery, boolean)` bytecode): for each provider, the **user's own
  nodes** first, then each of the user's groups (its nodes, then its virtual command grants, then its parent chain). The first yes/no wins.
- *`PermissionsModule` can add/remove a group's nodes (creates the group), add/remove/replace a user's groups, add/remove user nodes, list
  every registered node (`getRegisteredPermissions()`, filled by every command via `registerPermission`) and reload. It has **no way to set a
  group's parent** (only `permissions.json` has `parent`). Adding a second provider (`addProvider`) makes `areProvidersTampered()` true,
  which vanilla `/op self` checks, so we do not add one.
- *Warps: `TeleportPlugin.get()` -> `getWarps()` (Map), `addWarp(Warp, boolean)`, `removeWarp(String)`, `saveWarps()`, `loadWarps()`;
  `new Warp(Transform, String id, World, String creator, Instant)`.
- *World spawn: vanilla `/spawn set` = `world.getWorldConfig().setSpawnProvider(new GlobalSpawnProvider(new Transform(pos, rot)))` +
  `WorldConfig.markChanged()`; `/spawn set default` clears the provider (5.4).
- *First op: `/op self` works for a singleplayer world's owner, or on a standalone server started with `--allow-op`; otherwise the game
  tells the player to edit `permissions.json` while the server is off (`OpSelfCommand`, `Constants.ALLOWS_SELF_OP_COMMAND`, 2.1).
- *NPCs: `NPCPlugin.get().spawnNPC(Store, String, String role, Vector3dc, Rotation3fc)`, `getRoleTemplateNames(boolean)`, `hasRoleName`;
  removal is `Store.removeEntity(Ref, RemoveReason.REMOVE)` (`RemoveReason` = REMOVE, UNLOAD, BUILDER_TOOLS_UNDO; vanilla
  `EntityRemoveCommand` calls `removeEntity`); `World.getEntityRef(UUID)`; name tag = the `Nameplate` component (`new Nameplate(String)`,
  `setText`, `getComponentType()`; vanilla has `EntityNameplateCommand`); use = `UseEntityEvent$Pre` (cancellable), handled by an entity
  event system with the same shape as vanilla `TriggerVolumeRuleSystems$NoUseEntity.handle(int, ArchetypeChunk, Store, CommandBuffer,
  UseEntityEvent$Pre)`. Entity UUID from a ref: `UUIDComponent` (used in SkyyClasses 0.1.4).
- *Prefabs: `PrefabStore.get().saveServerPrefab(String, BlockSelection)` / `getServerPrefab(String)`; `BlockSelection.copyFromAtWorld(...)`
  and `place(CommandSender, World, Vector3ic, BlockMask)`; `PrefabUtil.paste(...)`. This is the engine's own "save a build, paste it" path.
- TextField input: `EventData.of("a", "x").append("@Key", "#Id.Value")`, read back with `jsonStr` (SkyySacks 0.7.3, SkyyGuilds 0.1, SkyyBank
  0.1.3). ON/OFF rows (SkyyHud WidgetsPage). Page-to-page without closing (SkyyHud, SkyyMenu 0.1.2). Coloured chat parts:
  `Message.raw(t).color("#hex")` + `Message.join` (SkyyExploration 0.1). Chat prefix by wrapping the previous formatter
  (SkyyExploration `TitleFormatter`, priority 30000). Item id check: `Item.getAssetMap().getAsset(id) != null` (SkyyBazaar, SkyySacks).
- Installed mod version: `PluginManager.get().getPlugins()` -> manifest name/version (SkyyMenu 0.1.3 `MenuUtil.liveVersion`).
- Precedent: HyperEssentials' one generic admin config page driven by a setting-kind enum, AdminUI's per-action nodes, LuckPerms'
  "prepare, then commit", CoreProtect's preview + undo (research "Server tools" and "Engine" section 4). Our own code, not theirs.

---

## 1. Architecture

### 1.1 Who owns what

| Thing | Owner | Why |
|---|---|---|
| A setting's value, its file, its validation, its effect | **the mod** | The file is the truth (HANDOFF rule: "the game and the files always agree"). A mod must work with no SkyyMenu. |
| The setting's description (schema) and the op function | the mod, published on the bridge at `setup()` | Pull model: no load-order problem. |
| Change log, file history (versions), export/import text | the mod (generated by the kit) | Changes also come from commands (`/bankconfig`) and file edits, not only from the menu, so the one that applies the change logs it. |
| Pages, the Mods list, the confirm step, the log viewer, `/modconfig` | SkyyMenu 0.3 | One shared editor, not one per mod. |
| Who may see the Mods section | SkyyMenu (`skyymenu.modconfig`) | Separate from moderation (research "Server tools" 4). |
| Who may change a mod | the mod re-checks its own admin node (`skyybank.admin`, ...) on every change | Defence in depth against a stale page, a SkyyMenu bug or an admin who lost the node mid-session. It is not a guard against other server code (the trust boundary in 1.4.8). |
| Big editors (shops, ranks, warps, island template) | the mod that owns the data draws its own page; the Mods section links to it | Those pages need the mod's own data and world access. |

### 1.2 One registry with two scopes, or two registries? Decision: **two registries, one toolkit**

| | Player Settings (Settings-Spec, `settings:*`) | Admin config (this spec, `config:*`) |
|---|---|---|
| Who stores the values | SkyyMenu (`Skyy_SkyyMenu/settings/<uuid>.properties`) | the mod (its own `Skyy_<Mod>/...properties`) |
| Value types | Boolean only | bool, int, decimal, text, choice, item list, range, table, link, action |
| Hot path | yes (`settings:fn:get` before every message) | no (mods read their own fields; the bridge is used only while an admin has a page open) |
| Without SkyyMenu | every switch reads as ON | everything works from the file and the admin commands |
| Who may use it | every player, their own values | admins, server-wide values |
| Registration | push (`settings:fn:register`) + `settings:def:*` fallback | pull only: `config:def:<Mod>` + `config:fn:<Mod>`, scanned by SkyyMenu |

**Why not one registry with a scope field:** the owner of the data is opposite (SkyyMenu vs the mod), the types and failure rules differ, and
Settings-Spec is already written and waiting for its build round (HANDOFF section 4 item 3). Folding admin scope into it would reopen a
finished spec and put typed values on a hot Boolean path. **What they share** (so it is one idea, not two): the same key rules family
(`validKey`-style check, clipping of labels and help), `MenuUtil.atomicWrite` (the `ProfCfg.atomicWrite` copy), the drain-style scan of the
bridge by prefix, the page shell (accent, title, tab rows, rows of 70 px, status line, footer, the same button styles and ON/OFF colours),
the never-throws / no-cross-mod-call / save-on-the-scheduler guarantees, and one contract document style (`tools/CONFIG-CONTRACT.md` next to
`tools/SETTINGS-CONTRACT.md`, written after the build by the workflow that owns those files).
**The two meet in one place:** SkyyMenu registers its **own** admin config, and one of its tables is "Player settings defaults", which edits
`Skyy_SkyyMenu/settings-defaults.properties` (Settings-Spec 1.4). So the admin twin edits the player twin's server defaults in game.

### 1.3 The bridge contract (`System.getProperties().get("skyy.bridge")`, a ConcurrentHashMap)

Everything that crosses the bridge is a `java.lang` type (`String`, `String[]`, `Object[]`, `Long`, `Integer`, `Boolean`), a `java.util.UUID`,
or a `java.util.function.Function`. Never a mod's own class (each mod has its own classloader). **All setting values travel as canonical
text**, exactly as they are written in the file. That avoids boxing mistakes under javassist and keeps export codes and the file identical.

| Bridge key | Written by | Value |
|---|---|---|
| `config:def:<Mod>` | the mod, in `setup()` after its config is loaded (whether or not SkyyMenu exists); may be re-put any time (new rows) | `Object[]` mod header (below) |
| `config:fn:<Mod>` | the mod, same time | `java.util.function.Function` taking `Object[]` ops (below) |
| `config:epoch:<Mod>` | the mod, after every successful change from any source | `Long`, +1 per change. Other mods or open pages may compare it; nobody polls it. |

`<Mod>` = the plugin name without version, exactly as in SkyyMenu's MENU DATA (`SkyyEconomy`, `SkyyIslands`), matching `Skyy[A-Z][A-Za-z]{1,30}`.
Keys are **never removed** (the `profile:fn:key` rule). Before calling a mod's function SkyyMenu checks `MenuUtil.liveVersion(mod) != null`;
a disabled mod shows "not running".
**There is no `config:fn:register`.** SkyyMenu owns no admin data, so it simply scans the bridge for `config:def:` keys each time it builds the
Mods list. That is the load-order fallback: whichever loads first, the key is there when a page is drawn.

**Mod header** `config:def:<Mod>` = `Object[]`:

| # | Type | Meaning |
|---|---|---|
| 0 | String | contract version, `"1"`. SkyyMenu shows a newer one as "needs a newer SkyyMenu" and does not call it. |
| 1 | String | mod name (`SkyyEconomy`) |
| 2 | String | title for the page, max 24 characters (`Economy`) |
| 3 | String | running version (`0.1`) |
| 4 | String | the admin node the mod checks on every change (`skyyeconomy.admin`). SkyyMenu uses it only to show "view only". |
| 5 | String[] | category ids, max 16, `[a-z][a-zA-Z0-9]{0,15}`, in display order (`parts`, `coins`, `bank`, ...) |
| 6 | String[] | category labels, same length, max 20 characters (`Parts`, `Coins`, `Bank`) |
| 7 | Object[] | rows, each an `Object[]` (below), in display order |
| 8 | String | files, comma list relative to the world's `mods/` folder (`Skyy_SkyyBank/config.properties,...`), shown on the page |
| 9 | String | optional note, max 100 characters (`Also: /deathpenalty 5%-10% in chat.`) |

**Row** = `Object[11]`:

| # | Meaning | Rules |
|---|---|---|
| 0 | key | `[A-Za-z][A-Za-z0-9._-]{0,79}`: no `=`, `:`, `#`, `!`, `/` or spaces. It is the bridge/export key; it may differ from the file key (the mod maps it). **Never used inside a UI element id** (ids use the row index). |
| 1 | label | max 40 characters, shown with `b.set` |
| 2 | category id | one of header element 5; unknown -> the last category |
| 3 | type | see the type table |
| 4 | default | canonical text |
| 5 | min | `""` = none. int/dec/range: lowest value. text: min length. items: min entries. |
| 6 | max | `""` = none. Same meanings. |
| 7 | opts | bool: `01` when the mod's file stores `1`/`0` instead of `true`/`false` (1.4.1 value format rule). choice: `value|Label,value|Label` (label optional). int/dec: `step=5` for - / + buttons. items: `qty` (entries are `id:qty`) and/or `prefix` (entries may end in `*`). table: `<valueType>;<addMode>;<Col1|Col2|Col3>` (1-3 value columns, addMode = `none`, `type`, `held` or `both`). link: the command to run (`shopadmin`). action: the button text. |
| 8 | unit | shown after the value: `%`, `coins`, `h`, `min`, `s`, `ms`, `blocks`, `x`, or `""`. It is the unit of the value the admin types, the export code carries and the file stores; a `field:` binding whose field stores another unit must carry a scale (1.4.1). |
| 9 | flags | comma list: `live` (applies at once), `restart` (saved, used after a restart), `new` (applies to new things only: new guilds, new islands, freshly loaded vaults), `danger` (needs the confirm step), `part` (a part switch, 3), `adv` (hidden until "Advanced" is on), `ro` (shown, not editable) |
| 10 | help | max 100 characters |

**Types:**

| Type | Value text | Widget (2.5) | Checked by the mod |
|---|---|---|---|
| `bool` | `true` / `false` | ON + OFF buttons | exact word |
| `int` | whole number, `25` (also `2k`, `1.5m`, `1,000` typed; the mod stores plain digits) | TextField + Set (+ `-`/`+` when `step=`) | long range, min/max |
| `dec` | decimal with `.`, `0.10` | TextField + Set | finite, min/max |
| `text` | any text, one line | TextField + Set | length, the mod's own rule (lists, tiers) |
| `choice` | one listed value | up to 4 buttons, else `<` value `>` | in the list |
| `items` | comma list: `Ore_Iron,Ore_Gold` or `Food_Bread:5` or `Skyy_Sack_*` | summary + Edit (list editor) | every id exists (`Item.getAssetMap().getAsset(id)`), qty 1-9999 |
| `range` | `min-max` in the unit, `10-25`; one number = fixed | TextField (accepts `5%`, `5%-10%`, `5-10`) + Set | the `/deathpenalty` rule |
| `table` | `""` (entries via ops) | Open -> table view (2.6) | per entry |
| `link` | `""` | Open -> runs opts as the admin (a big editor page) | - |
| `action` | `""` | one button (danger -> confirm) | the mod |
| `color` | `#rrggbb` | reserved for v2 (HUD / chat prefix colours; HyperEssentials has a COLOR kind) | - |

**The op function** `config:fn:<Mod>`: `apply(new Object[] { String op, ... })`. Unknown op or bad arguments -> `null` (SkyyMenu hides that
button). `who` is the admin's `java.util.UUID`, `name` their username, `confirm` is `"yes"` or `""`, `via` is `menu`, `command`, `import`,
`restore` or `undo`.

| op | Arguments after op | Returns |
|---|---|---|
| `get` | `String key` | `String` current value, `null` = unknown key |
| `set` | `String key, String value` (`null` = reset to default)`, UUID who, String name, String confirm, String via` | result R |
| `keys` | `String tableKey, String filter` (`""` = all) | `Object[] { String[] entryKeys, String[] labels, String[] values }` (values: columns joined by `|`), max 500 |
| `tset` | `String tableKey, String entryKey, String value, UUID who, String name, String confirm` | R |
| `add` | `String tableKey, String entryKey, String value, UUID who, String name, String confirm` | R |
| `remove` | `String tableKey, String entryKey, UUID who, String name, String confirm` | R |
| `action` | `String actionKey, UUID who, String name, String confirm` | R |
| `reload` | `UUID who, String name` | R (re-reads the files after hand edits; every difference is logged `via=file`) |
| `export` | `String scope` (`changed` = only values that differ from the default, `all`) | `String` code (1.4.7), `null` if unreadable |
| `import` | `String code, UUID who, String name, String mode` (`preview` / `apply`) | R; message = the change list |
| `versions` | - | `String[]` newest first, each `id \t file \t time \t who \t summary`, max 10 per file (1.4.5: every version belongs to one file). LOCKED 2026-09-25 (Skyy). Was: 20. |
| `restore` | `String id, UUID who, String name, String mode` | R; restores only the one file the id names; preview message = the change list |
| `log` | `Integer max` (1-200) | `String[]` newest first, each `time \t name \t uuid \t via \t key \t old \t new \t status` (table ops use the 1.4.6 table form) |
| `status` | - | `String[] { state, message }`, state = `ok`, `unreadable`, `unsaved`, `restart` (changes wait for a restart) |

**Result R** = `Object[] { String status, String value, String message }`:
- `ok`: applied now. `value` = the new canonical value. `message` e.g. `Interest per payout: 3% - saved.`
- `restart`: saved to the file, used after a server restart.
- `confirm`: **nothing changed yet.** `message` = the question and warning (max 200 characters). SkyyMenu shows it and repeats the same call
  with `confirm = "yes"`.
- `bad`: nothing changed. `message` = why (`Must be a whole number from 0 to 100.`).
- `denied`: `who` lacks the mod's admin node (write ops only, 1.4.8). `error`: the file cannot be read or written (the in-memory value is unchanged). `unknown`: key.

**Guarantees** (they go into `tools/CONFIG-CONTRACT.md` later):
1. **Never throws.** Any `Throwable` inside becomes `{"error", null, "internal error - see the server log"}` and one log line.
2. **Never calls another Skyy mod** and never writes another mod's bridge keys. The only outside call is the engine's
   `PermissionsModule.get().hasPermission(who, adminNode)`. It holds only its own kit monitor, only around in-memory edits. So it is safe to
   call from any thread and from inside a caller's lock; no lock cycle is possible.
3. **Never touches ECS, worlds or inventories** in `get`/`set`/`tset`/`add`/`remove`/`import`/`restore`. An `action` that needs the world
   (capture an island template, set the hub) schedules itself with `world.execute(...)` and answers `ok` with "working on it".
4. **Never writes a file on the caller's thread.** Memory changes at once; the file is written 500 ms later on
   `HytaleServer.SCHEDULED_EXECUTOR` with an atomic write (1.4.4). A failed write is retried every 30 s and at shutdown.
5. **Never overwrites an unreadable file.** While a file cannot be read, every change to it returns `error`.

### 1.4 Inside a mod: the adopter kit (`tools/skyycfg.py`)

The build rules (no javac, javassist, each mod its own classloader) mean shared code has to be **copied into every jar**. So the kit is a
Python module, like `tools/skyybuild.py`, that each build script imports and that emits the Java for a few classes in that mod's package.
No runtime dependency between mods, and one place to fix a kit bug. The build script only adds **data**: its rows, and how each row binds.

```python
import skyycfg as CFG
ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
  ("bank.interestPercent", "Interest per payout", "bank", "int", "2", "0", "100", "step=1", "%", "live,danger",
   "Percent of the bank balance paid each payout (up to the max below).", "field:BankCfg.PERCENT@config.properties:interestPercent"),
  ("part.bazaar", "Bazaar", "parts", "bool", "true", "", "", "", "", "live,part,danger",
   "Off: /bazaar says it is turned off on this server. Prices and files are kept.", "field:Parts.BAZAAR@config.properties:part.bazaar"),
]
CFG.emit(pool, PKG, MOD="SkyyEconomy", TITLE="Economy", NODE="skyyeconomy.admin", CATS=[...], ROWS=ROWS, RELOAD="EcoCfg.reloadAll", KEEP=10)
```

Generated classes (added in dependency order, fields before methods, no inner classes, no lambdas, no String switch: a key is found with a
loop over the `KEYS` array and the index drives `if (i == 3)` chains):

| Class | Role |
|---|---|
| `CfgRows` | the schema as parallel `String[]` arrays + the header; `index(key)`; `validate(i, text)` (type, min, max, choice, item ids); `canon(i, text)` |
| `CfgFile` | per file: the file's lines in memory, the mtime last read, `DIRTY`, `BROKEN`; `setLine(fileKey, text)`, `saveSoon()`, `saveNow()`, `reread()` |
| `CfgHist` | snapshots before a write, prune to `KEEP`, `versions()`, `diff(id)` |
| `CfgLog` | append one line per change to `Skyy_<Mod>/config-changes.log` (rotate at 1 MB, keep 3) + one INFO line in the server log |
| `CfgSaveTask` | `Runnable` -> `CfgFile.saveNow` on the scheduler |
| `CfgFn` | `implements java.util.function.Function`: the op dispatcher (1.3), wraps everything in `try/catch Throwable` |
| `CfgPub` | `publish()` puts `config:def:<Mod>` + `config:fn:<Mod>`; `bump()` increments `config:epoch:<Mod>` |

#### 1.4.1 Two ways a row binds (the mod picks per row)
- **`field:` binding** (live at once). Syntax `field:<Class>.<FIELD>[*<scale>]@<file>:<fileKey>`. The row names a `public static volatile`
  field (int, long, double, boolean or String) of the mod's config class. `set` parses the value, validates it **in the row's unit**,
  multiplies it by the scale (default 1), writes the field with `java.lang.reflect.Field.setLong/setInt/setDouble/setBoolean/set`
  (primitive setters, so no boxing problem), updates the file line and schedules the save. `get` returns the field divided by the scale.
  The file line always keeps the row's unit (`inviteSeconds=90`), never the scaled value, so the file and the mod's own loader keep agreeing.
  Use it for hot values and for mods with no reload path (SkyyParty, SkyyEssentials).
  - **Unit rule (build-checked, 2.12).** When the field stores a different unit from the row, the binding must carry the scale: seconds
    shown and milliseconds stored `*1000`, minutes / ms `*60000`, hours / ms `*3600000`. Verified this session in the newest scripts: SkyyParty
    `PartyStore.INVITE_MS` (file `inviteSeconds`, the loader multiplies by 1000), SkyyProfiles `ProfCfg.COMBAT_MS` (`combatSeconds`), SkyyVault
    `VCfg.AFTER_SWITCH_MS` (`afterSwitchSeconds`), and SkyyEssentials `EssStore.EXPIRE_MS` / `COOLDOWN_MS` once they become settings. Without
    the scale, typing `90` would put 90 into a millisecond field: invites would expire after 90 ms while the page says "saved (applies now)".
  - **Value format rule.** A `bool` row writes the form the mod's loader reads: `true`/`false`, or `1`/`0` with the opts token `01`.
    SkyyIslands reads `defaults.visit.notify` as "anything except `0` is on", so a written `false` would come back ON at the next load.
  - **Field declaration.** The adopting version adds `volatile` where a field is plain `static` today (SkyyIslands 0.5, 4.17) and removes
    `final` where section 4 says "make configurable". Arrays, maps and `AtomicBoolean`s are not `field:` types: use `reload:` or `custom:`.
- **`reload:` binding** (live within about a second, the smallest adoption). `set` validates the text, updates the file line in memory,
  and the save task, **after** the atomic write, calls the mod's existing reload routine (the same one `/skills reload`, `/tree reload`,
  `/island reload` call). The mod's own loader does any unit conversion, so `reload:` rows never carry a scale. Every reload routine in the
  inventory only parses files into fields, so it is safe on the scheduler thread; those fields are `volatile` in every mod except SkyyIslands
  0.5 (`IslandCfg` scalars are plain `static`), which adds `volatile` in its adopting version (4.17). A mod whose reload touches worlds wraps
  it in `world.execute`. Use it for tables and long key families (Skills, Trees, Collections, Exploration, Cooking) and for keys whose
  effect is spread over many fields.
- **`custom:` binding** for the few rows neither covers: a range stored as two file keys (death penalty `penaltyMin` + `penaltyMax`), a
  product line with three fields (`itemId=category,basePrice,displayName`), a list the mod parses into a map. The mod writes one static
  `customSet(String key, String value)` returning the R array, and `customGet(String key)`.
- **Change callbacks:** a `field:` row may name a static `afterSet(String key)` hook for side effects. `reload:` rows get the reload routine.
  Other mods learn about a change through `config:epoch:<Mod>` (they compare it on their own next action; nobody polls).

#### 1.4.2 Validation is the mod's job
- Typed in game: **reject, do not clamp.** `bad` with the reason and the allowed range; the TextField keeps what the admin typed.
- Read from the file (start, reload, hand edit): **clamp as today** (every current `load()` clamps) and log each clamped key once:
  `via=file key=interestPercent old=250 new=100 status=clamped`.
- The mod can refuse for its own reasons (`Lower than the highest page a player already uses (7).`), and decides which changes need
  `confirm`. SkyyMenu never second-guesses a mod's answer.

#### 1.4.3 Admin commands keep working and share the path
`/bankconfig`, `/deathpenalty`, `/bazaaradmin price`, `/vaultadmin reload`, ... stay. Their handlers call the same kit `set` with
`via=command` and the typed value, so a chat change is validated, logged, versioned and written exactly like a menu change (and the
existing whole-file writers that drop comments go away).

#### 1.4.4 Write-through: the file stays readable
Owners keep editing files by hand, so the kit changes **only the line of the key that changed**:
1. Find the first non-comment line `key=` / `key:` / `key =` and replace only its value. Drop a value's continuation lines (a trailing `\`).
2. Else find a commented template line `#key=` (the SkyyExploration `chest.xp.*` and Settings-Spec admin-template style) and uncomment it.
3. Else append it under one `# ---- changed in game (SkyWynn Menu) ----` header at the end.
4. Values are escaped the `java.util.Properties` way, with non-ASCII as `\uXXXX`, so both an ISO-8859-1 and a UTF-8 reader see the same value.
5. **Before writing**, if the file's `lastModified` differs from what the kit last read (someone edited it by hand while the server ran), the
   kit re-reads it first, applies and logs those differences (`via=file`), then applies the in-game change on top. A hand edit is never lost.
6. Write with `atomicWrite` (tmp file, fsync, `ATOMIC_MOVE` + `REPLACE_EXISTING`, fallback to a plain replace, 5 x 20 ms retries on
   `FileSystemException`: the `ProfCfg.atomicWrite` copy) on `SCHEDULED_EXECUTOR`, 500 ms after the last change to that file (one save per
   burst of clicks, the `SetStore.saveSoon` pattern). On failure: warn, keep `DIRTY`, retry every 30 s and in `shutdown()`.

#### 1.4.5 Versions (undo)
Before every write the kit copies the current file to `Skyy_<Mod>/config-history/<fileId>.<yyyyMMdd-HHmmss-SSS>.bak` (skipped when it
equals the newest copy of that file), where `<fileId>` is the file's path under `mods/` with `/` replaced by `~`
(`Skyy_SkyyBank~config.properties`), and appends `id \t file \t time \t who \t summary` to `config-history/index.log`, with
`id = <fileId>#<yyyyMMdd-HHmmss-SSS>`. It keeps the newest **10** per file. LOCKED 2026-09-25 (Skyy). Was: 20. `tools/skyycfg.py` still defaults `KEEP=20`. A build that passes `KEEP=20`, or omits `KEEP`, still keeps 20 until that call uses 10.
**A version belongs to exactly one file, and `restore` acts on that one file only.** The mod's other files stay as they are (SkyyEconomy
has four). One change that touches several files (an import can touch all four SkyyEconomy files) makes one version per touched file with
the same time stamp and summary, so the History view can show them side by side.
`restore` reads a copy, diffs it against the current values of known rows in that file, and with `mode=apply` applies the differences
through the normal `set` path as **one** batch (one write, one new version, log lines `via=restore`). Because a restore makes its own
version, "undo the undo" works (CoreProtect's idea).

#### 1.4.6 The change log
One line per change, tab-separated, `Skyy_<Mod>/config-changes.log`:
`2026-09-24T21:40:12 \t Skyy \t <uuid> \t menu \t bank.interestPercent \t 2 \t 3 \t ok`. Also one INFO line:
`[SkyyEconomy] config bank.interestPercent 2 -> 3 by Skyy (menu)`. No mod logs settings changes today (Config inventory); this is new.
**Table ops** (`tset`, `add`, `remove`: bazaar products, the blocked list, reforge costs, later shop items) log one line per entry in the
same file and format: key = `<tableKey>[<entryKey>]` (`bazaar.products[Ore_Iron]`), old / new = the entry's columns joined by `|`
(`Ores|12.5|Iron Ore`), and `(none)` for the side that does not exist (old of an `add`, new of a `remove`). `items` rows are ordinary
scalar lines (the whole list before and after). Tabs and line breaks inside a value become spaces. The `log` op returns table lines mixed
with scalar lines, so the Changes view (2.8) shows both; its Undo calls the inverse op (`add` -> `remove`, `remove` -> `add` with the old
columns, `tset` -> `tset` with the old columns).

#### 1.4.7 Export and import codes
- **Code:** `SKYY1.<Mod>.<base64url(deflate(utf8 text))>.<crc32 hex>`, where the text is `key=value` lines (row keys, not file keys) plus
  `_mod=`, `_ver=`, `_date=`. Default scope `changed` (only values that differ from the default), so codes stay short.
- **Import** checks the checksum and the mod name (SkyyEconomy also accepts `SkyyCoins`, `SkyyBank`, `SkyyBazaar`, `SkyyAuctions` codes, since
  the row keys are the same), validates **every** value first, and applies all or nothing. Unknown keys (an older or newer version) are
  listed and skipped. `preview` returns the change list; `apply` needs the confirm step and makes one version first.
- A code never holds player data.

#### 1.4.8 Permission re-check inside the mod
Every `set`, `tset`, `add`, `remove`, `action`, `reload`, `import` (apply) and `restore` (apply) first checks
`PermissionsModule.get().hasPermission(who, NODE)` inside `try/catch` (`false` on any error) and returns `denied` on a no. `get`, `keys`,
`versions`, `log`, `status`, `export` and previews are read-only and need only SkyyMenu's section node, which SkyyMenu checks through its
one `guard()` before every call it makes (2.3).
**Trust boundary (a deliberate decision, not an oversight).** `config:fn:<Mod>` sits on the JVM-wide `skyy.bridge` map, like every other
bridge function (`coins:fn:add` can mint coins today). Any code in any installed jar can call it, and `who` is whatever the caller passes,
including an op's UUID. So the mod's re-check is **not** a defence against other server code, on reads or on writes: every installed jar
is fully trusted, the same as on any Hytale server. The re-check protects against a stale page, a SkyyMenu bug and an admin who lost the
node mid-session. Adding `who` to the read ops was considered and rejected: a caller-supplied UUID adds no protection. The reads return
nothing an admin cannot already read in the files (`config-changes.log`, the config files); players cannot call Java code at all.

### 1.5 Failure modes

| Situation | What happens |
|---|---|
| SkyyMenu missing or older than 0.3 | Nothing visible changes. The mod reads its file, its commands work (now logged and versioned). `config:*` keys sit unused. |
| Mod not updated yet | The Mods list shows it with "Not set up for in-game editing yet - edit `<file>` and use `<reload command>`" and a Reload button when MENU DATA knows the command (2.11). |
| Mod loads after SkyyMenu | Irrelevant: SkyyMenu scans at page build. |
| Mod disabled at runtime | `liveVersion` null -> "not running", its function is not called. |
| Config file unreadable | `status` = `unreadable`; every change returns `error` with "`<file>` cannot be read - fix or delete it, then Reload"; the file is untouched. The page shows it in red. |
| Save fails (Windows lock) | Memory keeps the change, `status` = `unsaved`, retried every 30 s and at shutdown, logged. |
| Admin loses the node while a page is open | The next click is refused (SkyyMenu re-checks its node, the mod re-checks its own). |
| Two admins change the same key | Last one wins; both are logged; the second admin's page shows the new value after their next click. |
| Bad value hand-typed in the file | Clamped at load as today and logged `status=clamped`. |

---

## 2. SkyWynn Menu -> Mods section (SkyyMenu 0.3)

SkyyMenu 0.2 is the player Settings menu (Settings-Spec). The admin side is **0.3**, on top of it. If Skyy prefers one round, both can ship
together as 0.2: the two registries are independent `[SKYY?]`. The newest SkyyMenu script on disk is `build_skyymenu_0.1.3.py`.

### 2.1 Who can see it
- Node **`skyymenu.modconfig`**. Ops have it through `hytale:Admin`'s built-in `"*"` (VERIFIED), so on a fresh world the owner sees it with no
  setup and nobody else does. A staff rank gets it only when granted (SkyyRanks 5.1 or `permissions.json`). It is separate from moderation.
  LOCKED 2026-09-25 (Skyy): ops only. The node `skyymenu.modconfig` can be given to staff. That was already the default.
- Changing a mod also needs **that mod's** admin node (1.4.8). A viewer without it sees the mod's page read-only: "View only - changing
  SkyyBank needs skyybank.admin." So an owner can give someone the market but not ranks.
- SkyyMenu checks `this.playerRef.hasPermission("skyymenu.modconfig")` (inside `try/catch`, false on error) **on page build and on every
  click**, never only at open (research Engine 2), through the one `guard()` method (2.3). Players never see the Server Setup tile;
  `/modconfig` refuses them (the engine's own no-permission answer, since it uses `requirePermission` like every admin command).
- **First admin on a brand-new server (VERIFIED this session: `OpSelfCommand` bytecode, `Constants`, `Options`, `server.lang`).** Op is
  only membership in `hytale:Admin`. Vanilla `/op self` is open to everyone but works only (a) in a singleplayer world, for the world's
  owner, or (b) on a standalone server started with the `--allow-op` launch argument. Otherwise it answers with the game's own tip: add
  yourself to `permissions.json` while the server is off (your UUID from `/whoami`, alias `/uuid`) or use `--allow-op` for one start. It also
  refuses when a non-vanilla permissions provider is installed (`areProvidersTampered()`), one more reason SkyyRanks adds none (5.1). After
  that, an op makes other ops with `/op add <player>`. No Skyy mod can do this first step for the owner (no admin yet means no page and
  no admin command), so the pack's server guide (other workflows own it) must say it first, before any Skyy step.

### 2.2 Entry points
- **Main view:** a new MENU DATA entry, slot **41** (right of Mods at 40), icon `Deco_Book_Pile_Large` or another existing icon (`need_item`
  check), name "Server Setup", action `admin`. `fillStatic` **skips** it (not greyed: absent) when the viewer lacks the node. Click ->
  `openCustomPage(ref, st, new AdminPage(this.playerRef, "list", null))` without closing the menu first (the 0.1.2 rule).
- **Mods view:** for an admin, clicking a mod tile whose `config:def:<Mod>` exists opens `AdminPage` on that mod; the tooltip footer reads
  "Click to set up this mod". Players keep today's behaviour (commands in the info box).
- **Command:** `/modconfig` (alias `/serversetup`), `requirePermission("skyymenu.modconfig")` and `setPermissionGroups(new String[0])`
  (the admin-subcommand rule). Usage variant `/modconfig <mod>` opens that mod (case-insensitive, `Skyy` prefix optional: `/modconfig bank`).
  Build check: no vanilla or Skyy command already uses either name (the menu's existing `cmd()` check pattern).

### 2.3 One page class, seven views
`AdminPage` (an `InteractiveCustomUIPage`, like `SettingsPage`), 1120 x 930, all ids `SkyyAdm...` (no underscores), root anchor Width/Height
only. Views switch with `rebuild()`: `list`, `mod`, `table`, `confirm`, `log`, `hist`, `io`. Fields: `view`, `mod`, `cat`, `pageNo`, `tableKey`,
`tFilter`, `status`, `statusKind`, `showAdv`, `drafts` (HashMap rowKey -> typed text), `pending` (the call waiting for Confirm, as an
`Object[]`), `rowKeys[]` (row index -> key for this build), `backView`, `search` (the list view's filter text).
**One permission gate: `guard()`.** A method that re-reads `this.playerRef.hasPermission("skyymenu.modconfig")` inside `try/catch` (false
on error). On false it drops `pending` and `drafts`, sets the red status `You no longer have access to Server Setup.`, sets a `locked`
flag and returns false; the caller then rebuilds, and a locked page draws only the status line and `Close`. **`build()` and
`handleDataEvent()` call it as their first statement**; `handleDataEvent` calls it before it even reads the action, and only `close` skips it. Every click of every view goes through that one method, so a button
added later (in 0.3 or after) cannot forget the check. Writes are checked a second time by the mod with its own node (1.4.8). A build
check proves the order (2.12). The big editors (section 5) use the same shape with their own node.
Rules: no MouseEntered/Exited bindings, no timers or periodic updates (a value changed elsewhere shows at the next click; a Refresh button
re-reads), never `setPage(None)` before opening another page, Esc closes (`CanDismiss`). Every handler is wrapped in `try/catch` with
`MenuUtil.warn`.

### 2.4 View `list`: the mod list

```
+--------------------------------------------------------------------------------------------------+
| ===================================== gold accent 3 px ========================================== |
|                                 Server Setup   (28 bold)                                          |
|        Every Skyy mod on this server. Click Open to change its settings in game.   (16)            |
|  [ search settings and editors, e.g. warps            ] [ Search ] [ Clear ]      (TextField 520)  |
|  +--------------------------------------------------------------------------+ +--------------+    |
|  | SkyyEconomy 0.1                                        (21 bold, white)   | |    Open      |    |
|  | 41 settings - Parts: Bank ON - Bazaar ON - Auctions OFF - NPC shops ON - Editors: NPC shops |    |
|  +--------------------------------------------------------------------------+ +--------------+    |
|  | SkyyParty 0.1.3                                                          | |   Reload     |    |
|  | Not set up for in-game editing yet - edit Skyy_SkyyParty/config.properties                  |    |
|  ... 8 rows per page ...                                                                          |
|                                   status line (17 bold)                                           |
|  [< Prev] [Next >]  [Changes]  [Export all]  [Refresh]  [< SkyWynn Menu]  [Close]                 |
+--------------------------------------------------------------------------------------------------+
```
- Rows = every mod in MENU DATA `MODS` that is installed (`liveVersion` or its check command), plus any `config:def:*` mod not in MENU DATA
  (a future mod appears without a SkyyMenu rebuild). Sorted: mods with config first, then alphabetically.
- Line 2 of a set-up mod: `<n> settings`, then `- <k> wait for a restart` when `status` says so, then the parts (`part` rows, ON/OFF), then
  `- Editors: <labels of its link rows>` (NPC shops, Warps, Ranks, Island template), clipped to the row width with `...`; or the red state
  (`Its config file cannot be read`, `Changes not saved yet - retrying`). `Open` -> view `mod`.
- **Day one:** when SkyyMenu 0.3 first ships, SkyyEconomy is the only set-up row; every other mod shows the grey file-path line and Reload
  (2.11) until its adopting version lands (section 7). The subtitle then reads `1 mod set up for in-game editing - the rest show their file.`
- **Search** (TextField `#SkyyAdmFind` + `Search`; Enter = Search; `Clear`): at least 2 characters, case-insensitive, matched against each
  set-up mod's name and title, its category labels, and every row's label and help (all read from `config:def:`), and against the names of
  mods not set up yet. The list then shows only mods with a hit; line 2 lists the hits instead of the summary (`Hits: Warps editor, Set the
  world spawn here`, up to 3, then `and 4 more`). `Open` on a hit opens the mod on the first hit's tab and page and marks hit rows with `>`
  before the label. No hit: `Nothing matches "<text>" - mods not set up yet are matched by name only.` This is also the per-mod settings
  search (SkyySkills alone writes more than 100 keys into its default file). Height with the search row: padding 28 + accent 3 + title 48 + subtitle 26 + search 58 +
  8 rows x 76 + status 30 + footer 62 = 863 <= 930.
- A mod without config: the MENU DATA `config` path, and `Reload` when MENU DATA has a `reload` command (runs it as the admin, the menu's
  existing `handleCommand` path, then rebuilds with the result in the status line).
- `Changes` -> view `log` (all mods). `Export all` -> view `io` in all-mods mode.

### 2.5 View `mod`: a mod's config page

```
+--------------------------------------------------------------------------------------------------+
| ===================================== gold accent 3 px ========================================== |
|                        Server Setup - Economy (SkyyEconomy 0.1)   (28 bold)                        |
|    Saved to Skyy_SkyyBank/config.properties and 3 more files - changes are written at once. (15)   |
|  [ Parts ][ Coins ][ Bank ][ Bazaar ][ Auctions ][ Market ][ Shops ]     tabs, up to 8 per row     |
|  Bank   -   3 settings                                                    (24 bold, gold)          |
|  +--------------------------------------------+ +-------------------------------+ +---------+     |
|  | Interest per payout        LIVE  (21 bold) | | [    2     ] [ Set ]   %      | | Default |     |
|  | Percent of the bank balance paid ... (16)  | |                               | |         |     |
|  +--------------------------------------------+ +-------------------------------+ +---------+     |
|  ... up to 7 rows (70 px + 6 px gap) ...                                                          |
|                     Interest per payout: 3% - saved (applies now).     (status)                   |
|  [< Prev] [Next >] [History] [Export / Import] [Reload file] [Advanced: OFF] [< Mods] [Close]     |
+--------------------------------------------------------------------------------------------------+
```
Height: padding 28, accent 3, title 48, file line 26, one tab row 58 (a second row +58 when there are more than 8 categories), gap 8,
header 40, rows 7 x 76 = 532, status 30, footer 62 = 835 (893 with two tab rows) <= 930. Width: text 470 + 10 + widget 420 + 10 + Default
120 = 1030 <= 1080 inner. Build-time asserts, like the menu's `_tall`.

**Row text:** label in bold with a tag after it (`LIVE`, `RESTART`, `NEW ONLY`, `CONFIRM`), help below. A `*` after the label when a draft
differs from the saved value. `adv` rows appear only with `Advanced: ON`. `ro` rows show the value as text, no widget.

**Widgets** (all `TextButton` + `EventData`, proven; every TextField is `TextField #SkyyAdmVal<r>` with the SkyyBank markup):

| Type | Widget in the 420 px area |
|---|---|
| `bool` | `ON` 120 + `OFF` 120, the active one green / red (Settings-Spec colours) |
| `int`, `dec`, `text`, `range` | TextField 240 (value = draft or current) + `Set` 100 (+ `-` / `+` 40 each when `step=`) |
| `choice` (<= 4) | one 100 px button per value, the current one highlighted |
| `choice` (> 4) | `<` 50, the label 220, `>` 50 (cycles, then Set is automatic) |
| `items` | `Edit (12 items)` 240 -> view `table` in list mode (SkyyMenu edits the list and calls `set` with the whole new list) |
| `table` | `Open (36 entries)` 240 -> view `table` backed by `keys`/`tset`/`add`/`remove` |
| `link` | `Open` 240 -> runs the opts command as the admin (the big editor page replaces this page; no close first) |
| `action` | one button with the opts text; `danger` -> confirm |

**Drafts:** every button's `EventData` carries every visible TextField (`.append("@V<r>", "#SkyyAdmVal<r>.Value")` for r = 0..6). The handler
stores the non-empty ones in `drafts` by row key and puts them back after `rebuild()`. So typing in two rows and clicking one Set loses
nothing. A draft is dropped after that key saves, and all drafts on `< Mods` or Close. Enter in a field (`Validating` binding) = its Set.

**Set / Default / Confirm flow:**
1. `aset<r>` -> value = draft. `adef<r>` -> value = `null` (the mod's default). ON/OFF/choice buttons -> the fixed value.
2. SkyyMenu re-checks `skyymenu.modconfig`, then calls `set` (`via=menu`, `confirm=""`).
3. `ok` -> green status `<Label>: <value><unit> - saved (applies now).`; `restart` -> amber `... saved - applies after a server restart.`;
   `bad` / `denied` / `error` / `unknown` -> red status with the mod's message, draft kept; `confirm` -> view `confirm` with `pending`.
4. Every branch ends in `rebuild()`.

**Footer:** Prev/Next (only with more than 7 rows), `History` -> `hist`, `Export / Import` -> `io`, `Reload file` -> `reload` op (status shows
"Read the file again: 2 values changed by hand (see Changes)."), `Advanced`, `< Mods`, `Close`.

### 2.6 View `table`: list and table editor
Header `<Label> - <n> entries`, a filter TextField + `Search` (`keys` with the filter; the SkyySacks search pattern), then up to 7 entry rows:
entry key or label (bold), 1-3 value TextFields (the table's columns, e.g. `Buy price | Sell price | Stock`), `Set` (`tset`) and `Remove`
(`remove`, always through confirm). Bottom add row: a key TextField + `Add` when addMode is `type`/`both`; `Add held item` when it is `held`/
`both` (reads the admin's active hotbar slot, the SkyyRolls 0.1.3 "hand = hotbar + active slot" rule). Paging with Prev/Next. `< Back`
returns to the mod page on the same tab. An `items` row uses the same view, editing a list SkyyMenu keeps in the page and saves with one
`set` of the whole list.

### 2.7 View `confirm`
Title `Please confirm`, then the mod's message in 19 px (e.g. `Change Death penalty from 10%-25% to 50%-90%? Every player who dies loses
that share of their purse.`), then `[ Confirm ]` (red `RESET_ARM` style) and `[ Cancel ]`. Confirm repeats `pending` with `confirm="yes"`.
Cancel, Esc or any other button drops `pending`. No timer (the Settings-Spec armed-button rule). SkyyMenu itself always asks for: import
apply, restore apply, undo from the log, and every `remove`.

### 2.8 View `log`: Changes (audit log)
Merges the `log` op of every set-up mod (40 newest each), newest first, 10 lines per page. Tabs: `All` + one per mod with changes. A line:
`21:40  Skyy  Economy  Interest per payout  2% -> 3%  (menu)` (labels and units from the schema; unknown keys shown raw). Table lines read
`21:40  Skyy  Economy  Bazaar products: Ore_Iron  added  Ores / 12.5 / Iron Ore` (1.4.6). An `Undo` button on lines with `status=ok`:
confirm `Undo: put Interest per payout back from 3% to 2%?` -> `set(key, old, via=undo)`; a table line undoes with the inverse table op. If the current value is
no longer the line's new value: `Changed again since - open the mod to edit it.`

### 2.9 View `hist`: History (one mod)
`versions` list, 8 per page, each row naming its file: `Skyy_SkyyBank/config.properties - 2026-09-24 21:40 - before Skyy changed
bank.interestPercent`, with `Preview` (the `restore` preview; the change list replaces the status area, up to 12 lines + "and 5 more") and
`Restore` (confirm -> `restore` apply). A mod with more than one file gets a tab row above the list: `All files` + one tab per file. The
confirm names the file and says what stays: `Restore Skyy_SkyyBank/config.properties to 21:40? SkyyEconomy's other 3 files are not changed.`

### 2.10 View `io`: Export / Import
- **Export:** a TextField filled with the `export` code (scope `changed`; a `Everything` button switches to `all`) so the owner can select and
  copy it, and the same text saved to `Skyy_SkyyMenu/exports/<Mod>-<yyyyMMdd-HHmm>.txt` (the status line names the file).
- **Import:** paste into a TextField -> `Preview` (the change list and skipped unknown keys) -> `Apply` (confirm). Or pick a file: every
  `.txt` in `Skyy_SkyyMenu/imports/` is listed with its own `Preview`.
- **Export all / Import all** (from the list view): one file with one code per line for every set-up mod; import previews mod by mod.
- TextField `MaxLength` starts at 4000 characters. UNVERIFIED how long a TextField value can be over the wire; bigger setups go by file.

### 2.11 Mods not updated yet
MENU DATA `MODS` entries get two optional fields, used only while the mod publishes no `config:def:`: `"config"` (the file path shown) and
`"reload"` (the command a Reload button runs). From the inventory: SkyySkills `skills reload`, SkyyTrees `tree reload`, SkyyCollections
`collections reload`, SkyyCooking `cookadmin reload`, SkyyExploration `exploreadmin reload`, SkyyClasses `classadmin reload`, SkyyProfiles
`profileadmin reload`, SkyyIslands `island reload`, SkyyVault `vaultadmin reload`, SkyyGuilds `guildadmin reload`, SkyyBazaar `bazaaradmin
reload`. SkyyParty, SkyyEssentials and SkyyAccessories have none (SkyySacks self-polls its file).

### 2.12 Inline strings and build checks
Reuse Settings-Spec 4.3's constants with the `SkyyAdm` prefix: `UI_AROOT` (1120 x 930, `#0b1524(0.96)`, padding 20/14, `LayoutMode: Top`), accent,
title, file line, tab rows (`#SkyyAdmTab<i>`, 126 x 48 when 8 per row), header, rows (`#SkyyAdmRow<r>`, `#SkyyAdmName<r>`, `#SkyyAdmDesc<r>`),
value area (`#SkyyAdmVal<r>` TextField, `#SkyyAdmSet<r>`, `#SkyyAdmOn<r>`, `#SkyyAdmOff<r>`, `#SkyyAdmCh<r>x<j>`, `#SkyyAdmDef<r>`), status,
footer buttons, confirm text and buttons, table columns `#SkyyAdmCol<r>x<c>`, the list search field `#SkyyAdmFind`, history file tabs
`#SkyyAdmFile<i>`. Fixed inline text only uses letters, digits, space and
`< > / -`; everything from a mod goes through `b.set("#Id.Text", ...)` or `#Id.Value`.
Build checks (copy the menu's): balanced `{}`/`()`, no underscore in any `#Id`, no `Anchow`/`;;`, root anchor Width/Height only, height and
width budgets, every `UI_A*` string present in `MenuData.class` after the build, slot 41 free, icon exists, `modconfig`/`serversetup` free,
every `makeClass` in the `writeFile` list, `python tools/ci/lint.py` 0 fails, and the guard order: in the generated `AdminPage` source
`if (!guard())` appears in `handleDataEvent` before its first action comparison, and at the start of `build()` (a string-position check).
Per-mod build checks (in `skyycfg.emit`, so every adopter gets them): keys valid and unique, default passes the row's own validation,
category ids exist, flags known, labels <= 40, help <= 100, choice defaults in the list, every `field:` binding names a real
`public static volatile` field of a supported type (checked with javassist at build), every `reload:` routine exists, and the **unit
rule** (1.4.1): a field whose name ends in `_MS`, `MS` or `MILLIS` must be bound by a row with unit `ms` and no scale, `s` with `*1000`,
`min` with `*60000` or `h` with `*3600000`; a row with unit `ms` must bind such a field; any other scale fails the build; `max x scale` must
fit the field's type. `emit` also takes the mod's default file text (every adopter already builds it in Python) and fails when a `bool`
row's file key appears there as `1` or `0` without the `01` token.

---

## 3. Per-part switches

**Convention:** a part switch is a `bool` row, key `part.<id>`, category `parts`, flags `live,part,danger`, stored in the mod's own config
file (`part.bank=true`). The mod asks for the confirm **only when switching a part OFF** (`Turn the Bazaar OFF for everyone on this
server? Prices and files are kept.`); switching it back ON asks nothing (1.4.2: the mod decides which changes need `confirm`). The Mods list shows every `part` row. A part that **failed to start** (every part starts inside its own `try/catch`,
`SkyyEconomy-Plan.md` rule 4) shows `FAILED - see the server log` and cannot be switched on until a restart.

**What "off" means, for every mod:**
1. Its commands stay registered (the name is not freed for another mod) and answer `<Part> is turned off on this server.` The pages refuse
   to open with the same line. SkyyMenu tiles for it show "(off on this server)".
2. **No data is deleted, converted or rewritten.** Files stay; the part simply stops acting on them.
3. **Off stops new activity, but a player can always take out what is theirs** (the "nobody loses a coin" rule). LOCKED 2026-09-25 (Skyy): bank withdraw and auction claims stay available. That was already the default.
4. Timers of the part pause and do **not** pay back the off time when it comes back on, except bank interest. LOCKED 2026-09-25 (Skyy): players receive back-pay for interest accrued while the bank was switched off. Was: no back-pay. `lastInterestMillis` stays put while the bank is off, and the missed periods are paid when the bank comes back on. SkyyBank 0.1.3 has no part switch yet.
5. Its bridge functions answer as if the part were not installed (other mods already handle that case), except where rule 3 needs a path.
6. Live: checked at every command, click and tick. No restart.

**SkyyEconomy (the four switches in `SkyyEconomy-Plan.md`; coins is the core and has no switch):**

| Part | Off means | Still works |
|---|---|---|
| `part.bank` | No deposits. The interest tick skips while the bank is off, and `lastInterestMillis` is left alone. When the bank comes back on, players receive the interest accrued while it was off. `bank:<uuid>` is still published so the HUD and menu show the balance. | `/bank withdraw` and Withdraw all, so nobody's coins are locked away. |
| `part.bazaar` | `/bazaar` and `/bz` refused; demand drift paused (the decay clock restarts from now when it comes back on). `bazaar:products` is removed from the bridge so the auction house stops refusing bazaar items. | Nothing is stored per player, so nothing is locked. |
| `part.auctions` | No browsing, listing or buying (like `/ahadmin pause`, plus Browse closed). `auction:fn:lowestBin` returns null. Listing clocks keep running; an expired listing returns to its seller's claims as usual. | `/ah claim` and Manage (cancel your own listings, claim coins and items). |
| `part.npcShops` (0.2) | Shop NPCs stay where they are; using one says "This shop is closed." (`npcShops` off does not despawn them). | - (NPC shops hold no player items) |

**Other mods (their existing master keys become parts; no new behaviour needed):** SkyySkills `acro.enabled`, `acro.doubleJump.enabled`,
`perk.enabled`, `alchemy.enabled`, `smelt.enabled`, `exploration.enabled`, `fell.enabled`, `party.combatShare.enabled`,
`bridge.bonus.enabled`; SkyyExploration `chests.enabled`, `chunks.enabled`, `zones.enabled`, `luck.enabled`; SkyyCooking `enabled`;
SkyyCollections `bypass.enabled`; SkyyEssentials (new) `part.tpa`, `part.msg`, `part.trade` (when `/trade` exists). These keep their file
names; the row key is the file key, only the flag makes them parts.

---

## 4. The settings each mod registers

**Legend:** L = live at once, N = new things only, R = restart, D = `danger` (confirm), A = `adv` (hidden until Advanced). Ranges are the
mod's validation (the same clamps the file load uses today, from the Config inventory). "Make configurable" = hard-coded values worth a row
in the adopting version. Versions in brackets = the newest build script on disk today; the adopting version is the next free one at build
time (two build rounds are running).

**Field audit (2026-09-24, every newest script on disk; the binding is a code fact, not only a schema choice):**
- **Already `volatile`, no field change needed:** SkyyBank, SkyyCoins, SkyyBazaar (`SPREAD`, `IMPACT`, `HALFLIFE`), SkyyVault, SkyyGuilds,
  SkyyProfiles, SkyyParty (`MAX`, `INVITE_MS`), SkyyClasses, and the reload-driven config fields of SkyySkills, SkyyTrees, SkyyCollections,
  SkyyCooking and SkyyExploration. A grep found no other plain-`static` config field in them (only one-shot warning flags).
- **Needs `volatile` added (a code change):** every SkyyIslands 0.5 `IslandCfg` scalar (4.17).
- **Needs `final` removed** (tagged "make configurable" below): SkyyBazaar `MINF` / `MAXF` / `MAXQ`, SkyyEssentials `EXPIRE_MS` / `COOLDOWN_MS`,
  SkyySacks bag and bench caps, SkyyAccessories `CAP`.
- **Stores milliseconds behind a seconds row, so the binding needs `*1000`** (1.4.1 unit rule): SkyyParty `INVITE_MS`, SkyyProfiles
  `COMBAT_MS`, SkyyVault `AFTER_SWITCH_MS`, SkyyEssentials `EXPIRE_MS` / `COOLDOWN_MS`.
- **Not a `field:` type:** SkyyIslands `DEF_PERM` (elements of a `final int[]`), SkyySacks `craftSearch` (an `AtomicBoolean`).
- The adoption estimate (schema + 10-80 lines per mod) still holds; SkyyIslands sits at the top of it (about 25 extra lines for the field changes).

### 4.1 SkyyEconomy 0.1 (first adopter; merges SkyyCoins [0.1.5], SkyyBank [0.1.3], SkyyBazaar [0.1.2], SkyyAuctions [0.1, spec only])
Row keys carry the part prefix; files stay in the four old folders (merge rule 1), so row key and file key differ (`custom:`/`field:`
bindings name the file key). Categories: `parts, coins, bank, bazaar, auctions, market, shops`.

| Cat | Key | Type | Default | Range | Flags | Notes |
|---|---|---|---|---|---|---|
| parts | `part.bank` / `part.bazaar` / `part.auctions` / `part.npcShops` | bool | true | - | L, part, D | section 3; confirm only when switching OFF (`Turn the Bazaar OFF for everyone on this server?`) |
| coins | `coins.penalty` | range % | 10-25 | 0-100 | L, D | file `penaltyMin`/`penaltyMax` (`custom:`), same as `/deathpenalty` |
| coins | `coins.starter` | int coins | 10000 | 0-1e12 | N, D | **make configurable**: today the `10000L` literal in `CoinTask.run()` |
| coins | `coins.payMax` | int coins | 0 (no cap) | 0-1e15 | L | **new**: largest single `/pay` |
| coins | `coins.payFeePercent` | dec % | 0 | 0-50 | L, D | **new**: coins removed from each `/pay` |
| bank | `bank.interestPercent` | int % | 2 | 0-100 | L, D | |
| bank | `bank.intervalMinutes` | int min | 60 | 1-10080 | L | |
| bank | `bank.maxPrincipal` | int coins | 10,000,000 | 0-1e12 | L, D | |
| bank | `bank.catchUpMax` | int | 24 | 1-168 | L, A | **make configurable**: the hard cap on payouts after an outage |
| bazaar | `bazaar.products` | table | 36 seeded | price 0.01-1e9 | L | columns `Category|Base price|Name`, add `both`; `products.properties` line format kept (`custom:`) |
| bazaar | `bazaar.spread` | dec | 0.10 | 0-0.9 | L, D | |
| bazaar | `bazaar.impactCoins` | dec | 10000 | 1-1e12 | L, A | |
| bazaar | `bazaar.halfLifeMinutes` | dec min | 120 | 1-100000 | L, A | |
| bazaar | `bazaar.maxOrder` | int | 100000 | 1-1,000,000 | L | **make configurable**: `MAXQ` |
| bazaar | `bazaar.demandFloor` / `bazaar.demandCeiling` | dec x | 0.25 / 4.0 | 0.01-1 / 1-100 | L, A | **make configurable**: `MINF`/`MAXF` |
| bazaar | `bazaar.impactBase` | dec | 1.10 | 1.0-2.0 | L, A, D | **make configurable**: the price-impact exponent base |
| bazaar | `bazaar.resetDemand` | action | - | - | D | "Reset all prices to base" (= `/bazaaradmin reset all`) |
| auctions | `ah.listingFee` | text | `0:1.0,10000000:2.0,100000000:2.5` | tiers `from:percent` | L, D | AH spec 3. LOCKED 2026-09-25: 1% / 2% / 2.5% |
| auctions | `ah.durations` / `ah.defaultDuration` | text / choice | presets / `24h` | max 8, cap 14 d | L | LOCKED 2026-09-25: 1h / 6h / 12h / 24h / 48h, default 24h. Fees 20 / 45 / 100 / 350. 48h pays 2x `ah.listingFee` |
| auctions | `ah.claimTaxPercent` / `ah.claimTaxFrom` | dec % / int | 1.0 / 1,000,000 | 0-50 / 0-1e15 | L, D | stored at sale time, never retroactive. LOCKED 2026-09-25: 1% above 1,000,000 |
| auctions | `ah.minPrice` / `ah.maxPrice` | int coins | 1 / 5e10 | 1-1e15 | L | |
| auctions | `ah.maxListings` / `ah.maxListingsServer` | int | 14 / 5000 | 1-100 / 100-100000 | L (server cap A) | |
| auctions | `ah.graceSeconds` | int s | 20 | 0-600 | L | |
| auctions | `ah.confirmAbove` / `ah.claimAllConfirmAbove` | int coins | 10000 / 100000 | 0-1e15 | L, D | confirm only when raised: `Players will only be asked to confirm purchases above 1,000,000 coins. Raise it?` (it removes a player-side safety step) |
| auctions | `ah.cancelRefundsFee` / `ah.adminRemoveRefundsFee` / `ah.bazaarItemsAllowed` / `ah.blockCreative` | bool | false / false / false / true | - | L | |
| auctions | `ah.paused` | bool | false | - | L, D | also `/ahadmin pause`; confirm only when pausing (`Pause the Auction House for everyone on this server?`) |
| auctions | `ah.sameAccountBuy` / `ah.allowTestDurations` | bool | false | - | L, A, D | testing only; the page help says so |
| market | `market.blocked` | table | empty | id or `Prefix*` | L | `Skyy_Market/blocked.txt`, column `Reason`, add `both`; bare `*` refused (AH spec 4.4) |
| shops | `shops.editor` | link | `shopadmin` | - | - | 0.2, section 5.2 |
| shops | `shops.roles` | text | curated role list | - | L | 0.2 |
| shops | `shops.defaultRestockMinutes` | int min | 60 | 1-10080 | L | 0.2 |

**LOCKED 2026-09-25 (Skyy), Auction House fees.** The fee rows above stay the Hypixel defaults and are the live tune: listing 1% / 2% / 2.5%, duration fees 20 / 45 / 100 / 350 on 1h / 6h / 12h / 24h, and 1% tax above 1,000,000. Skyy can change any of those numbers in Server Setup once SkyyEconomy is up. A tax edit applies to later sales only. SkyyAuctions 0.1.1 still reads `config.properties` and has no Server Setup page yet. **LOCKED 2026-09-25 (Skyy), durations:** presets stay 1h / 6h / 12h / 24h / 48h, default 24h. A 48h listing pays twice the listing fee. 0.1.1 still adds a flat 1,200 coins for 48h.

### 4.2 SkyyRolls [0.1.4] (later the gear mod)
`cost.Junk` 100, `cost.Common` 250, `cost.Uncommon` 500, `cost.Rare` 1000, `cost.Epic` 2500, `cost.Legendary` 5000, `cost.default` 1000 (int
coins, 0-1e12, L; category `reforge`). Adopt as one table `cost` (entry = quality, column `Coins`, add `type`). **Fix in the same version:**
`/rolls` has no `requirePermission` although its help says admin (Config inventory) -> `requirePermission("skyyrolls.admin")`.
Make configurable later: the rarity-based roll ranges once they exist (unbuilt, `SkyyGear-Plan.md`).

### 4.3 SkyyVault [0.1]
Category `vault`: `freePages` int 2 (1-100, <= maxPages, L, D), `maxPages` int 10 (1-1000, L, D; refuses a value below any player's highest
used page, the `/vaultadmin` rule), `slotsPerPage` int 36 (9-90, N, D), `pagePrice` int 50,000 (L), `pagePriceStep` int 25,000 (L), `buyConfirmCoins` int 50,000 (0–1e12, L, coins; LOCKED 2026-09-25: a page cheaper than
this buys at once, this price or more asks "Buy page X for Y coins?" first; `field:VCfg.BUY_CONFIRM`. SkyyVault 0.1.2 still uses a second
click within 10 s and does not read the row yet), `openMode`
choice `page|Page view,chest|Chest window` (L), `afterSwitchSeconds` int 30 s (0-120, L, A; `field:VCfg.AFTER_SWITCH_MS*1000`: the field
stores milliseconds), `saveDelayMillis` int 1000 ms (100-30000, L, A; `VCfg.SAVE_DELAY_MS`, no scale).
Keep in code: `MAX_CAP = 1024`, `MAX_PAGE = 1000` (safety ceilings).

### 4.4 SkyyGuilds [0.1.1]
Categories `guilds, xp, bank`: `maxMembers` int 25 (1-500, L; lowering never kicks, it only blocks invites), `inviteSeconds` int 300 (10-86400,
L), `onlineMessages` bool true (L), `xpSharePercent` int 10 (0-1000, L), `xpSkills` text (comma list of skill ids, the mod checks names, L),
`levelBase` int 100 / `levelStep` int 150 (L, D), `xpPollSeconds` 10 / `xpPerLevelFallback` 25 / `xpMaxPerCheck` 1e7 (A), `maxBank` int 1e12
(L, D), `bankLogKeep` int 200 (10-1000, A), `defaultAdminLimit` text `none` / `defaultMemberLimit` text `0` (number or `none`, N).
Make configurable later: the fixed 3-rank ladder (Member/Admin/Leader), a SkyyGuilds design question, not a setting.

### 4.5 SkyyParty [0.1.3] (the one mod with no admin path today)
Category `party`: `maxSize` int 5 (2-10, **L** once adopted: `MAX` is already `volatile`; a party above a lowered max keeps its members and
cannot invite), `inviteSeconds` int 60 s (15-600, L; binding `field:PartyStore.INVITE_MS*1000@config.properties:inviteSeconds`, because
`INVITE_MS` stores milliseconds and the loader multiplies the file's seconds by 1000). Add `/partyadmin reload` (`requirePermission("skyyparty.admin")`) in the same version so
the file works without SkyyMenu too.

### 4.6 SkyyEssentials [0.1.1]
Categories `parts, tpa, msg, warps, trade`: `part.tpa`, `part.msg` (bool, L, part, D), `tpa.expireSeconds` int 60 s (10-600, L) and
`tpa.cooldownSeconds` int 10 s (0-300, L) (**make configurable**: today `EssStore.EXPIRE_MS` / `COOLDOWN_MS` are `public static final long`
milliseconds; they become `public static volatile long` and bind `field:EssStore.EXPIRE_MS*1000@config.properties:tpa.expireSeconds` and
`field:EssStore.COOLDOWN_MS*1000@...:tpa.cooldownSeconds`), `replyShortcut` bool true (**R**: the `/r` alias is registered at start),
`warps.editor` link `warpadmin` (5.4), actions `Set the world spawn here` (D) and `Reset the world spawn to the original` (D) (5.4).
Later with `/trade`: `part.trade`, `trade.timeoutSeconds`, `trade.allowCoins`, `trade.maxStacks`.

### 4.7 SkyyMenu [0.1.3] (its own admin config, 0.3)
Categories `menu, settings`: `menu.giveItem` bool true (L: give the menu item on first join), `menu.tooltipsDefault` bool true (L), `menu.modsHelp`
bool true (L: players see the Mods help list), `settings.defaults` table (entries = every registered player switch, column `Default` =
`on`/`off`/`unset`; writes `settings-defaults.properties`, Settings-Spec 1.4). Later: warp locks (`MenuUtil.isWarpUnlocked` -> a node per
locked warp, 5.4).

### 4.8 SkyyHud [0.3.9]
Nothing server-wide today (layouts are per player). **Make configurable:** `hud.defaultLayout` text (a layout code; new players start with it)
+ an action "Use my layout as the default" (N). Nice for server owners who want a house look.

### 4.9 SkyySkills [0.4.2] (`xp.properties`, `reload:` binding for almost everything)
Categories (8, so one tab row): `parts, general, levels, gathering, combat, acrobatics, perks, crafting`. Merged from the 13 file
families: double jump goes under acrobatics (its switch is `acro.doubleJump.enabled`), felled (tree felling XP) under gathering, alchemy +
smithing under crafting, party XP share + bridge bonus under general. Category ids are display only; file keys do not change.
- general: `multiplier` dec 1.0 (0-100, L, D), `coinsPerLevel` int 100 (0-1e9, L, D), `feedback` bool, `feedbackMs` (A), `creativeXp` bool false,
  `ignorePlaced` bool true (L, D: off lets players farm placed blocks), `farmingNeedsRipe` bool true, `harvestCooldownMs` int 5000 (>= 3000, A);
  the party XP share and bridge bonus keys.
- levels: `levels` text (1-100 positive numbers; its length is the max level; A, D). **Make configurable:** two actions that rewrite the list:
  "Scale every level by N%" and "Set max level to N" (they ask for N through the row's TextField), so nobody hand-edits 100 numbers.
- gathering: tables `block`, `prefix`, `suffix` (entry = block id or id part, column `Skill:XP or none`, add `type`); the felled keys.
- combat: `combat.perHealth` dec 0.2, `combat.min` 1, `combat.max` 500, `combat.default` 5; table `combat.role` (entry = NPC role, column `XP`).
- acrobatics (+ double jump) / perks / crafting (alchemy + table `alchemy.xp`, smithing + table `smithing.xp`): every key in the Config
  inventory, the per-level numbers visible, the timing and search limits `adv`.
- Make configurable later: skill icons (`SkillDefs.ICONS`).

### 4.10 SkyyTrees [0.2.1] (`trees.properties`, `reload:`)
Categories `general, abilities, nodes`. general: `tier.levels` text (6 increasing levels, L, D), `tokens.first` 1 / `tokens.every` 5 (L, D),
`dust.xpPerDust` 10 + table `dust.xpPerDust` (per tree), `respec.cooldownMinutes` 10, `respec.coins` 0, `feedbackMs` (A), `debug.extraTokens` /
`debug.extraDust` (A, D). abilities: `ability.disabledWorlds` text, `ability.maxRadius` 6, `vein.cooldownSec` 40, `feller.cooldownSec` 3
(LOCKED 2026-09-25, was 5),
`feller.maxPerLayer` 64, `feller.needLeaves` true, `feller.maxHeight` 32, `felled.nodes` true. Tree Feller's locked count is 1 / 2 / 4 / 5 / 6 / 10 extra logs at levels 1–6 (level 6 jumps to 10 so a very large tree is not broken as a whole layer); the 0.2.3 formula still uses the whole layer at max until the next Trees build (`research/Tree-Fall-Spec.md`). nodes: one table per tree (Mining, Foraging,
Farming, Cooking, Acrobatics, Exploration) with columns `Max|Per level|On`, and one table `nodeCost` with columns `Tokens|Dust B`.
Stays code: node names, icons, order; the 8 unbuilt Exploration slots.

### 4.11 SkyyCollections [0.2.1] (three files, `reload:`)
Categories `curves, rewards, bypass, rules, registry`. curves: `curve.B`, `curve.S`, `curve.R`, `curve.E` text (increasing counts; L, **D**:
changing a curve moves every player's tiers). rewards: `tier.coins`, `tier.xp` text (10 entries, D), `tier.lastXp` int 25000, `combat.coinMultiplier`
int 2. bypass: `bypass.enabled` (part), `bypass.multiplier` 5, `bypass.minPrice` 500, `bypass.fallback` / `bypass.walls` text (D). rules: `auto`
bool false (D), `exclude.benches` text, `cap.perCredit` 256 / `cap.perMinute` 20000 (A), `bridge.add.sources` text (A), `bridge.add.felled`
bool, `migrate` choice `convert|reset` (A). registry (A): tables `coll` (the 105 `coll.<Id>` lines, one text column validated by the mod's
own line parser) and `rewards` (the `rewards.properties` lines).
Make configurable later: per-collection bypass and the level walls (open design, `DESIGN-STATUS.md` 11; do not guess).

### 4.12 SkyySacks [0.7.5]
`craftSearch` bool true (L; binding `reload:SackCfg.reload`: the value lives in an `AtomicBoolean` `SEARCH`, not a `field:` type, and
`SackCfg.reload()` is the mod's own self-poll routine, so calling it after the write makes the change immediate instead of within ~10 s). Make configurable (A, D): bag caps `bag.small` 640 / `bag.medium` 2240 /
`bag.large` 20160 (locked design numbers, so the default must stay; lowering never deletes pooled items, it only stops intake), `QUEUE_CAP`
256, `FUEL_CAP` 1000, `OUT_CAP` 20000 (A). Not ours: processing times (vanilla bench assets).

### 4.13 SkyyCooking [0.1.1] (`cooking.properties`, `reload:`)
`enabled` (part), `maxGrade` int (1 to the jar's real max; `ro` note "can only lower the cap"), `creativeGrades` bool, `xpMultiplier` dec 1.0 (D),
`maxXpPerMinute` int, `messages` bool, `graded` items (dish ids), `campfire.buffFactor` 0.75 / `campfire.xpFactor` 0.5 (0-1), `xp.default` int,
tables `xp` (per dish) and `tree` (per node, column `Chance per level`). Stays code: the Grade formula (baked into assets), node max levels.

### 4.14 SkyyAccessories [0.4.3] (gets its **first** config file)
New `config.properties`: `slots` int 9 (1-9, N, D: a lowered cap hides slots but never deletes what is in them; more than 9 needs page work),
`regenEverySeconds` int 2 (1-30, A), table `bonus` (entry = accessory id, one text column `Common..Legendary %`, e.g. `2,4,6,8,10`, D).
Stays assets (rebuild only): upgrade recipes, rarity colours.

### 4.15 SkyyClasses [0.1.4]
`requireClass` bool false (L, D), `unassignedBlocked` bool true (L), `promptEveryLogin` bool true (L), `openDelayMillis` int 2000 (250-60000, A).
**Do not register `switchCost` and `cooldownMinutes`** while `ALLOW_SWITCH=false` is code (they are inert, a trap; Config inventory); the page
shows one `ro` row "Class switching: off in this version (design lock)". Make configurable later: the weapon -> class rule table (new weapons
from other mods) as a table `rules` (entry = item id prefix, column `Class or free or unassigned`).

### 4.16 SkyyProfiles [0.1]
`maxProfiles` int (default 4 in 0.1, 6 after the HANDOFF code follow-up; range 1-6 = the code clamp; L, D: lowering never deletes a profile,
it only blocks creating), `openDelayMillis` (A; `ProfCfg.OPEN_DELAY_MS`, no scale), `promptEveryLogin` bool, `combatSeconds` int 10 s
(0-600; `field:ProfCfg.COMBAT_MS*1000`: the field stores milliseconds), `islandOnSwitch` bool,
`perProfileBackpack` bool (L, D), `newProfileBackpack` int (-1-256, N), `keepItems` items (L, D: an item kept across profiles moves between
them). Raising the cap above 6 is Skyy's open decision (HANDOFF: do not invent the method); the row's max follows whatever the code allows.

### 4.17 SkyyIslands [0.5]
Categories `permissions, visits, coop, limits, starter, hub, tech`. permissions: 14 choice rows `defaults.perm.<flag>` (`visitor|trusted|member|
admin|owner`, L for islands whose owner never set that flag). visits: `defaults.visit.mode` choice `public|friends|closed` (N), `visit.limitMax`
10 (1-100, L), `defaults.visit.limit` 10 (N). LOCKED 2026-09-25 (Skyy): the default visitor limit is 10. Was: 5. SkyyIslands 0.5.2 still writes 5. `defaults.visit.notify` bool (N). coop: `coop.maxPlayers` 5 (1-50, L), `coop.adminsInvite` bool,
`invite.seconds` 60 s (10-3600). limits: `trusted.max` 20 (0-500), `bans.max` 100 (0-1000), `expel.cooldownSeconds` 60 s (0-86400),
`reset.cooldownHours` 24 h (0-8760), `reset.confirmSeconds` 20 s (5-300) (ranges = the 0.5 loader's clamps; every one of these fields
stores the file's own unit, so no scale). tech (A): `tint.resend` choice, `perm.otherProfileStrict` bool (D), `animals.extra` text (role ids).
**Code change in the adopting version, not only a schema** (verified in `build_skyyislands_0.5.py`, `IslandCfg`): every scalar behind
these rows is plain `public static` today (`DEF_MODE`, `DEF_LIMIT`, `DEF_NOTIFY`, `LIMIT_MAX`, `COOP_MAX`, `ADMINS_INVITE`, `INVITE_SECONDS`,
`TRUSTED_MAX`, `BANS_MAX`, `EXPEL_SECONDS`, `RESET_HOURS`, `RESET_CONFIRM`, `TINT_RESEND`, `STRICT_OTHER`). Add `volatile` to each before any
row is `field:`-bound (the 2.12 check fails the build otherwise); it also fixes visibility after today's `/island reload`. The 14
permission defaults are elements of `public static final int[] DEF_PERM`, which is not a `field:` type: make it `public static volatile
int[]`, have `load()` fill a new array and assign it once (copy on write), and bind the 14 rows `custom:`. `defaults.visit.notify` is
stored `1`/`0` (opts `01`, 1.4.1). `defaults.visit.limit` is also clamped to `visit.limitMax` by the loader, so lowering the max can lower it. **starter (make configurable):**
`starter.kit` items with qty (default = today's `Bench_WorkBench:1,Wood_Oak_Trunk:10,Soil_Dirt:8,Ingredient_Stick:8,Food_Bread:5,
Skyy_Accessory_Bag:1`, N), action "Set the starter kit from my hotbar" (N), link "Island template" (`island template`, 5.5). hub: action
"Set the hub here" (= `/sethub`).

### 4.18 SkyyExploration [0.1]
Categories `parts, worlds, chests, luck, chunks, zones, titles`. worlds: `exploration.excludeWorldPrefixes` / `excludeWorlds` text, `noFlyingXp`
bool true, `creativeXp` bool false. chests: `chests.base` dec 400, `chests.zoneMult` / `chests.tierMult` text, `chests.xpDefault` 500, table
`chest.xp` (per chest type; an empty value = use the formula), `chests.pollMs` / `pollMaxMs` (A). luck: `luck.perLevel` 0.003, `luck.max` 0.5,
`scav.coinsPerLevel` 10. chunks: `chunks.xp` 60, `chunks.zoneMult` text, `chunks.maxPaidPerWorld` 25000, `chunks.payWhileGliding` /
`payWhileMounted` bool, `chunks.feedbackMs` (A). zones: `zones.banner` bool, `zone.xpDefault` 1000, table `zone.xp`. titles: `titles.chatPrefix`
bool (L), `titles.chatPriority` int 30000 (**R**, A), `bridge.retryMs` (A). **Fix in the same version:** drop `display.staminaPerLevel` and read
SkyySkills' real value over the bridge (Config inventory flags the hand-kept copy as a desync risk). Make configurable later: title unlock
thresholds (table `title`, when SkyyExploration 0.2 builds its checklist backbone).

### 4.19 SkyyRanks 0.1 (new, 5.1) and SkyyQuests (future)
SkyyRanks: `ranks.editor` link `rankadmin`, `ranks.default` text (a rank id, checked live: rank ids are made in game, so a build-time
`choice` list cannot hold them; the default rank always sits at the bottom of the ladder), `chat.prefix` bool true (L), `chat.priority` int
31000 (R, A).
SkyyQuests: nothing to register until it exists.

---

## 5. The big editors

Each is its own page, owned by the mod that owns the data, opened from its `link` row in the Mods section and by its own admin command.
All follow the same UI rules (inline, TextButton + EventData, no periodic updates, no close-before-open) and re-check their own node on
every click through one `guard()` called first in `build()` and `handleDataEvent()` (the 2.3 shape).

### 5.1 Ranks and permissions -> a new mod, **SkyyRanks** (recommended over SkyyEssentials)

**Why its own mod:** it edits the world's security (who may do what), so it deserves its own admin node and its own off switch (remove the
jar); servers that already use another permissions mod can leave it out; a solo world never needs it; it owns a chat hook that must be
ordered with SkyyExploration's title prefix; SkyyEssentials stays the small "commands most servers have" mod (tpa, msg, warps, `/trade`).
SkyyGuilds' guild ranks and SkyyIslands' island roles are different things and stay in those mods.

**What Hytale lets a plugin change (VERIFIED this session unless marked):**
- Groups and a user's groups: `addGroupPermission(group, Set)` (creates the group), `removeGroupPermission`, `addUserToGroup`,
  `removeUserFromGroup`, `setUserGroup` (replaces all), `getGroupsForUser`, user nodes `addUserPermission` / `removeUserPermission`,
  `getAllRegisteredGroups`, `getRegisteredPermissions()` (every node any command registered), `reload()`. The engine saves `permissions.json`
  itself (one per world). Change events exist (`PlayerPermissionChangeEvent`, `GroupPermissionChangeEvent`).
- **No API sets a group's parent.** Inheritance through `parent` exists only when typed into `permissions.json`.
- **Denies:** a `-node` works, but the first yes/no found wins, groups are walked in set order, and every player keeps `hytale:Adventurer`,
  whose **virtual** grants are what let players run Skyy commands at all (`setPermissionGroups({"hytale:Adventurer"})`). So a deny on a rank
  group cannot reliably take a default command away (it depends on which group is walked first). A deny on the **user** is always checked first,
  so per-player denies are reliable.
- `addUserToGroup` on a player with no stored entry may leave them **without** `hytale:Adventurer` (the default list is used only while the user
  has no entry; UNVERIFIED which set results). That would silently take every player command away, so SkyyRanks always adds
  `hytale:Adventurer` explicitly first. First in-game test (8.4).
- No prefix, colour or weight on a group (`GroupData` = parent + nodes). A ranks mod stores them itself.

**Design (0.1):**
- A rank = an engine group named `skyy:<id>` (`id` = `[a-z][a-z0-9]{1,15}`, valid under the group-name rule) plus a row in
  `Skyy_SkyyRanks/ranks.properties`: order, display name, prefix, colour, `staff` flag, own grants. Each group always carries a marker node
  `skyyranks.rank.<id>`, so the group exists even with no grants and any mod can ask `hasPermission("skyyranks.rank.vip")`.
- **Inheritance is done by SkyyRanks:** ranks form one ladder by `order`; each group's node set = its own grants + every lower rank's. At start
  and after each edit SkyyRanks makes each `skyy:*` group's set exactly that (add missing, remove extra). It never touches a group that does not
  start with `skyy:`, never touches `hytale:Admin` membership (op stays vanilla `/op`), and never edits `permissions.json` directly.
- **A player has at most one `skyy:*` group**, always next to `hytale:Adventurer`. Assigning removes the other `skyy:*` groups. The default rank
  (`ranks.default`) is implicit: nobody is added to it; it is the rank shown when a player has no `skyy:*` group.
- **Grants are additive in 0.1.** The editor offers: grant a node to a rank (e.g. `skyyessentials.fly`, `skyymenu.modconfig`,
  `skyyeconomy.admin`, future perk nodes), and a per-player deny (reliable, user level). Taking a command away from everybody is the owning
  mod's part switch, not a rank deny. The page explains this in one line.
- **Stable nodes (recommended pack-wide change, needs one in-game test):** Skyy player commands get auto nodes with the version inside
  (HANDOFF command rule 1), so a grant or deny on them breaks at every version bump. Give each player command `requirePermission("<mod>.cmd.
  <name>")` **and** `setPermissionGroups(new String[] { "hytale:Adventurer" })`: `putRecursivePermissionGroups` puts the command's permission
  id into the group's virtual set (bytecode read this session), so everyone keeps the command by default and the node name stays the same.
  Adopt per mod with its next version, after a one-command test proves it (8.4).
- **Chat:** wrap the previous chat formatter exactly like SkyyExploration's `TitleFormatter`, registered at `chat.priority` 31000 (after
  Exploration's 30000), so the outer prefix is the rank: `[VIP] [Explorer] Skyy: hi`. Prefix coloured with `Message.raw(prefix).color(colour)`
  (proven), plain text if the colour is unusable. Bridge for other mods: `rank:<uuid>` (display name), `rank:prefix:<uuid>`, `rank:colour:<uuid>`
  (for the SkyyMenu Players view and the HUD players list later).

**Page (`/rankadmin`, `requirePermission("skyyranks.admin")`; also the `link` row):**
- Ranks view: rows `order - name - prefix preview - <n> members`, buttons `Up`, `Down`, `Edit`, `Delete` (confirm: members go back to the
  default rank), and `New rank` (id + name TextFields).
- Rank view: name, prefix (TextField), colour (TextField `#rrggbb` until the `color` widget exists), `staff` ON/OFF; **Grants** table (node,
  `Remove`; add by TextField with a live filter over `getRegisteredPermissions()` keys, 20 hits at most, the SkyySacks search pattern);
  **Members** table (name, `Remove`; add from the online list or by name/UUID of a seen player).
- Player view (from the SkyyMenu Players view, admin only): their rank (choice), their personal denies (table).
- Confirm on: granting `*` or any node ending in `.admin`, `skyymenu.modconfig`, `skyyranks.admin`; deleting a rank; per-player deny of an
  admin. Every change is logged in `Skyy_SkyyRanks/config-changes.log` with the same line format as the config kit.

### 5.2 NPC shops -> **SkyyEconomy 0.2** (after 0.1's merge is proven)

LOCKED 2026-09-25 (Skyy): every item can have a **buy** price (player pays) and a **sell-back** price (0 = the
NPC does not buy it); stock is **infinite** by default; any item can get a **limited stock with a restock timer** (Shopkeepers' admin-shop vs
stocked-shop split, research "Server tools" 2). Infinite stock stays the default. That was already the default.

- **Placing** (editor, "Create shop here"): `NPCPlugin.get().spawnNPC(store, <group>, role, adminPos, adminRotation)` on the admin's world
  thread. Role = a choice from `shops.roles` (a curated list of existing role templates; `/shopadmin roles` prints
  `getRoleTemplateNames(true)` so Skyy can pick villager/trader looks). The second argument's meaning is UNVERIFIED: probe it at build with
  `bc.py` on a vanilla caller. Name tag: add a `Nameplate(shopName)` component (the `EntityNameplateCommand` path). The file
  `Skyy_SkyyEconomy/shops/<shopId>.properties` stores the NPC UUID, world, position, rotation, role, name and the item lines.
- **Keeping it a shop:** cancel all damage to shop NPC UUIDs (a `DamageEventSystem` in the filter group, the SkyyClasses `DamageLock` pattern).
  A role that wanders is UNVERIFIED: test the listed roles; if the chosen one moves, a server task (not a page update) puts it back when it
  is more than 1 block from its spot, checked when a player uses it and every 60 s while its chunk is loaded.
- **Using it:** an entity event system for `UseEntityEvent$Pre` (the vanilla `NoUseEntity` handle shape). Target ref -> UUID via `UUIDComponent`.
  On a shop NPC: cancel, then `world.execute` to open the shop page for the player (never open a page from inside the ECS handler). Whether a
  plain NPC can be "used" by the client at all is UNVERIFIED; fallback `PlayerMouseButtonEvent` with the target entity (HANDOFF lists it).
- **Shop page (players):** rows of items (icon, name, buy price, sell price, stock left), an amount TextField and `Buy` / `Sell` buttons
  (the SkyyBank / SkyyBazaar amount box). Coins through the same coins core (same mod, direct calls), the active profile rules
  (PROFILES-CONTRACT; refused while `profile:busy:<uuid>`), inventory checked before taking coins, one line per trade in `shops.log`. Admins see
  an extra `Edit` button (node re-checked on click) instead of needing a crouch-click.
- **Editor page (`/shopadmin`, `requirePermission("skyyeconomy.admin")`):** shop list (name, world, position, item count; `Teleport`, `Edit`,
  `Remove`) + `Create shop here`. Shop view: name TextField, role `<` `>` cycler, `Move here`, items table with columns
  `Buy price|Sell price|Stock` (stock `inf` or a number) plus a per-item restock-minutes column in the adv view, `Add held item`, add by name
  search over the item asset map (the SkyySacks search; research idea 6: no reference shop editor has it), `Remove`. Price hints next to the
  price field when known: bazaar buy price and `auction:fn:lowestBin`.
- **Move:** remove + respawn at the admin's spot, save the new UUID (simplest and reliable). **Remove:** `World.getEntityRef(uuid)` ->
  `store.removeEntity(ref, RemoveReason.REMOVE)` on the world thread, then archive the shop file (`shops/removed/`), never delete.
- **Restart:** entities are saved with the world (research Engine 3). After `AllNPCsLoadedEvent` / first ready, for each shop **whose chunk is
  loaded**, check `World.getEntityRef(uuid)`; missing -> respawn and log `RESPAWN`. Never respawn for an unloaded chunk (that would make a
  duplicate when the chunk loads). UNVERIFIED whether role/AI survive; this self-heal covers both answers.
- **Restock** is computed lazily at open/buy from wall-clock time (no ticking): `left = min(stock, left + floor(elapsed / restock))`.
- **Shared NPC claim (for SkyyQuests later):** bridge `npc:owner` = ConcurrentHashMap `uuidString -> "SkyyEconomy|shop|<id>"`, created
  with `putIfAbsent`. Each mod reacts only to its own claims, so a quest giver and a shop can never both answer one NPC.

### 5.3 NPC quests -> future **SkyyQuests** (NOT buildable yet: only the hooks now)

Unlike the NPC shops above, nothing here can be built or used in game until SkyyQuests has its own spec (section 7 step 8).

The BetonQuest lesson (research "Server tools" 3): a click editor is right for linear quests (talk, deliver, kill N, gather N, reach a place)
and wrong for branching scripts. So SkyyQuests will ship an in-game **linear** quest builder and keep the file
(`Skyy_SkyyQuests/quests/<id>.properties`) as the escape hatch for anything bigger. Nothing is built now except:
- **`quest:fn:event`** (future, owned by SkyyQuests): `Function apply(new Object[] { UUID player, String type, String id, Long amount,
  String world })` -> ignored return. Types: `kill` (NPC role), `gather` (block id), `collect` (item id), `craft`, `smelt`, `cook` (item id),
  `reach` (zone or region id), `talk` (npc id), `buy` / `sell` (shop id), `level` (skill id, amount = level). Adopters call it next to hooks
  they already have, through a cached lookup that costs one map read when SkyyQuests is absent (the `notifyOn` style). First callers when
  SkyyQuests exists: SkyySkills (kill, gather, level), SkyyCollections (collect), SkyySacks (craft, smelt), SkyyCooking (cook),
  SkyyExploration (reach), SkyyEconomy (talk, buy, sell). **Do not add the calls before SkyyQuests has a spec** `[SKYY?]`.
- **Quest givers** reuse the shop NPC code (placement, nameplate, damage lock, use hook, restart self-heal, `npc:owner`). Put that code in a
  second generator, `tools/skyynpc.py`, when SkyyQuests starts, so both jars carry the same classes.
- **Rewards** go through bridges that exist today: `coins:fn:add`, `skill:fn:addxp`, item stacks.

### 5.4 Warps and spawn -> **SkyyEssentials**
- **Page `/warpadmin`** (`requirePermission("skyyessentials.admin")`; also the `link` row): rows `name - world - x y z - creator`, buttons
  `Teleport`, `Move here`, `Rename`, `Remove` (confirm), and `Add warp here` (name TextField).
- **Calls (VERIFIED names):** add = `new Warp(transform, id, world, creatorName, Instant.now())` -> `TeleportPlugin.get().addWarp(warp, <flag>)`
  -> `saveWarps()`. Remove = `removeWarp(id)` + `saveWarps()`. Rename = add under the new id with the same transform and world, then remove the
  old. Move = replace with the admin's transform. The boolean flag and whether `addWarp` also places the warp marker (`createWarp(Warp, Store)`,
  `WARP_MODEL_ID`) are UNVERIFIED: copy exactly what vanilla `WarpSetCommand` / `WarpRemoveCommand` call (trace with `bc.py` at build).
- The SkyyMenu Teleport view already lists `getWarps()` live, so edits show there at the next open.
- **Locked warps (later):** a warp flag `locked` published as bridge `warp:locked` (Set of ids); SkyyMenu's existing `MenuUtil.isWarpUnlocked`
  hook then asks `pr.hasPermission("skyymenu.warp.<id>")`, and SkyyRanks grants those nodes.
- **Spawn.** The hub is SkyyIslands' `/sethub` (action row in 4.17). The **world spawn** already works in game today through vanilla
  `/spawn set [position] [rotation]` (`SpawnSetCommand`, group `hytale:WorldEditor` and up, so ops have it; no position = where you stand)
  and `/spawn set default` (`SpawnSetDefaultCommand`, `hytale:Admin`: back to the world's original spawn). VERIFIED this session
  (bytecode + `server.lang`): `/spawn set` runs on the world, builds `new Transform(position, rotation)` and calls
  `world.getWorldConfig().setSpawnProvider(new GlobalSpawnProvider(transform))`, then `WorldConfig.markChanged()`; `/spawn set default`
  calls `setSpawnProvider` with no provider (a null, read from the bytecode shape). The warps page gets two action rows that do the same on
  the admin's world thread: `Set the world spawn here` (confirm: `Move this world's spawn to where you stand? New and respawning players
  arrive here.`) and `Reset the world spawn to the original` (confirm). It only touches the world the admin stands in; island worlds keep
  their own spawn provider (SkyyIslands). UNVERIFIED: whether `markChanged()` alone saves it across a restart (test 8.4.8).

### 5.5 Island template and starter kit -> **SkyyIslands**
- **Starter kit (easy, next version):** `starter.kit` items row (4.17) replaces the hard-coded `ids`/`qty` arrays in `FillTask.starterKit`; the
  "from my hotbar" action copies the admin's 9 hotbar stacks (ids and counts; item metadata is not kept in 0.x). New islands only.
- **Between the two versions:** new islands keep the built-in `FillTask` island (fixed layout; only its starter kit is editable). A
  custom starting layout needs a code change to `FillTask` until the template editor ships; there is no file or in-game option for it.
  Players and admins can of course still build on any island after it exists.
- **Template (bigger, the version after):** today the island is placed block by block in chunk (0,0) by `FillTask`. The template editor:
  `/island template edit` opens a template world (an instance of the same `SkyyIsland` template, `skyy-island-template`, the existing
  `InstancesPlugin.spawnInstance` path) and sends the admin there; they build; `Save template` (action, confirm) copies the box
  `template.box` (default x -16..31, y 96..191, z -16..31: 3 x 3 chunks around the island `[SKYY?]`) into a server prefab with
  `BlockSelection.copyFromAtWorld(...)` + `PrefabStore.get().saveServerPrefab("SkyyIslandStarter", selection)`; new islands paste it
  (`BlockSelection.place` / `PrefabUtil.paste`) instead of the `FillTask` loop, and the kit goes into the first chest found in the pasted box
  (or `template.chest` x,y,z). Existing islands never change. Missing or unreadable prefab -> the built-in island (logged). Using the engine's
  own prefab format keeps block rotation and chests, which a plain block-id copy (`chunk.getBlock`/`setBlock`) would lose. The API usage is
  UNVERIFIED; if it fails in the first test, the fallback is our own id-per-position copy with the rotation limitation written in the help line.

### 5.6 Market -> **SkyyEconomy** (tables in its config page, 4.1)
- **Bazaar products:** the `bazaar.products` table (add by held item or id, columns `Category|Base price|Name`, remove = off the bazaar, the
  product's history is kept in the file comments). `bazaar.resetDemand` action.
- **Auction house fees and limits:** the `ah.*` rows. Fee tiers and duration presets are `text` rows the mod validates with the same parser
  its config load uses, so a bad tier string is refused with the reason.
- **Late-game "can't be sold" list:** the `market.blocked` table over `Skyy_Market/blocked.txt` (id or `Prefix*`, reason column), shared by the
  auction house and later the bazaar (AH spec 4.4). Entries other mods add at runtime (owner not `file`) are shown `ro` with their owner.
  The cutoff itself is still open (`DESIGN-STATUS.md` 11), so nothing ships blocked.

### 5.7 Progression numbers (Skills, Trees, Collections, Exploration, Cooking)
No separate editor: these are the tables and rows of 4.9-4.13 and 4.18 (block XP rules, node tables, curves, zone XP). The two actions for the
level curve (scale by %, set max level) are the only new logic. SkyyExploration 0.2's discovery spots stay the in-game placement already
planned there (`SkyyExploration-Plan.md`).

---

## 6. Safety

| Risk | Guard |
|---|---|
| A typo goes live (10x too high) | The mod rejects out-of-range values with the range; `danger` rows need "Change X from A to B?"; the log line has an Undo; History restores a whole file. |
| Undo of a bad restore | A restore is itself a version ("undo the undo"). |
| Hand edit while the server runs | Re-read and logged (`via=file`) before any in-game write; only the changed line is rewritten, comments and order kept (1.4.4). |
| Broken file | Never overwritten; changes refused with the reason; red state in the Mods list. |
| Crash during a write | Atomic write (tmp + fsync + atomic move); the previous file stays whole. |
| Wrong person changes things | Three layers: `skyymenu.modconfig` to see the section, the mod's own admin node to change it, both re-checked on every click (SkyyMenu through its one `guard()`, 2.3). Ops only by default (built-in `*`). Staff ranks get narrow nodes (market, not ranks). Other installed jars are trusted by design (1.4.8). |
| A duration lands in the wrong unit (90 read as 90 ms) | The `field:` scale (1.4.1), a build check that fails a millisecond field bound without it (2.12), and a harness and an in-game test of the real effect (8.2 j, 8.4.10). |
| A whole part or the auction house is switched off by a misclick | Part switches, `ah.paused` and raising the AH purchase-confirm thresholds ask first (section 3, 4.1). |
| Someone takes all player commands away by accident | SkyyRanks always keeps `hytale:Adventurer`, never edits non-`skyy:` groups or op membership, and confirms `*`/admin grants. |
| An import from another server breaks this one | Checksum, mod name, every value validated, all or nothing, preview first, a version saved first. |
| A part switched off locks player value away | Rule 3 in section 3 (withdraw and claims keep working). |
| Log grows forever | `config-changes.log` rotates at 1 MB, keeps 3; history keeps 10 copies per file. LOCKED 2026-09-25 (Skyy). Was: 20. `tools/skyycfg.py` still defaults `KEEP=20`. |
| Restart-only values look applied | `RESTART` tag on the row, amber status, and "`<k>` wait for a restart" on the Mods list until the next start (the mod compares file vs running values at start). |
| A value changed elsewhere while the page is open | Shown at the next click (no periodic updates, by rule); every set answers with the value actually stored. |

---

## 7. Build order and adoption

| Step | What | Depends on |
|---|---|---|
| 1 | `tools/skyycfg.py` (the kit + its bare-JVM test harness, 8.2) | nothing |
| 2 | **SkyyMenu 0.3** (Mods section, `/modconfig`, its own config page). SkyyMenu 0.2 (player Settings) first, or both as 0.2 in one round `[SKYY?]` | step 1 |
| 3 | **SkyyEconomy 0.1**: the merge round (`SkyyEconomy-Plan.md`), built on the kit from day one: parts, coins, bank, bazaar, auctions, market tables; `/bankconfig` etc. through the kit | step 1; the separate Bank 0.1.3 / Bazaar 0.1.2 / Auctions 0.1 tested |
| 4 | **SkyyRanks 0.1** (5.1): ranks, grants, members, per-player denies, chat prefix. Staff and permission setup is one of the first things an owner does, so it comes before the waves. First in-game test: the `hytale:Adventurer` check (8.4.5). Until it ships, ranks are vanilla `/op`, `/perm group|user`, `/setgroup` or `permissions.json` | step 1 (its `link` row shows in the Mods list once step 2 exists; it needs nothing from SkyyEconomy) |
| 5 | Wave 1, the gaps (each mod's next version): SkyyParty (+`/partyadmin reload`), SkyyEssentials (+tpa timings, warps editor, world spawn rows), SkyyIslands (starter kit row + all defaults + the `volatile` / `DEF_PERM` field changes), SkyyProfiles (with the 4 -> 6 follow-up), SkyyVault, SkyyGuilds, SkyyRolls (+`/rolls` permission fix) | step 1 |
| 6 | Wave 2, progression: SkyySkills (+curve actions), SkyyTrees, SkyyCollections, SkyyExploration (+stamina read over the bridge), SkyyCooking, SkyyClasses, SkyySacks, SkyyAccessories (new config file), SkyyHud (default layout) | step 1 |
| 7 | Big editors: SkyyEconomy 0.2 NPC shops; SkyyIslands template editor; stable command nodes pack-wide after the test (8.4.6) | steps 2-3 |
| 8 | SkyyQuests spec + `tools/skyynpc.py` + the `quest:fn:event` calls | step 7 (shops) |
Steps 4-6 can run in parallel build rounds once step 1 exists; the numbers are the order to test them in.

Adoption notes:
- Settings-Spec's player-settings adoption touches the same mods. Where a mod's next version does both, it is one version bump with two small
  blocks (`regSetting` + `notifyOn` gates, and the `skyycfg.emit` schema).
- Each adopter: keep its admin commands (routed through the kit), keep its file names and keys (the row may rename, the file key never does),
  add `config:def:` + `config:fn:` publication at the end of `setup()` after the config load, and add the MENU DATA `config`/`reload` fields only
  while not adopted.
- After the build rounds (other workflows own these files): `tools/CONFIG-CONTRACT.md` from 1.3-1.4, a TEST-CHECKLIST section from 8.3-8.4,
  the new versions in `tools/deploy_set.py`, HANDOFF section 3.

---

## 8. Test plan

### 8.1 Static
1. `python tools/ci/lint.py`: 0 fails (ids, `/modconfig` and every new command has `requirePermission`/`setPermissionGroups`).
2. Every build passes its 2.12 checks and loads under `-Xverify:all` with `HytaleServer.jar` on the classpath (the jpype harness used in
   earlier rounds).
3. For each adopter: every `field:` binding resolves, every default validates, no duplicate keys, the schema round-trips through `export` ->
   `import preview` with 0 changes.
4. The unit-rule check fails on purpose: a throwaway schema binding a `*_MS` field to a row with unit `s` and no `*1000` must stop
   `skyycfg.emit`; so must a `bool` row without `01` over a file default of `1`; and an `AdminPage` source with a handler branch before
   `if (!guard())` must fail the SkyyMenu build.

### 8.2 Kit harness (bare JVM, jpype, files in the scratchpad)
a. `get` / `set` on each type; `bad` for out-of-range, wrong type, unknown item id; `confirm` for a `danger` row, then `ok` with `confirm=yes`.
b. Garbage arguments (null, wrong types, short arrays, unknown op) never throw: `null` or `error`.
c. Line-preserving write: comments, blank lines and key order unchanged; a `#key=` template line is uncommented; a new key lands under the
   header; a non-ASCII value is escaped and reads back the same with both an ISO-8859-1 and a UTF-8 reader.
d. Hand edit between two sets (change the file's mtime) -> both the hand edit and the new value survive; the log has `via=file`.
e. Unreadable file (a folder with the file's name, or an exclusive lock) -> `error`, file untouched byte for byte, one warning.
f. History: 25 changes -> 10 copies left; `restore` preview lists the right differences; apply makes a new version; undo of that works. LOCKED 2026-09-25 (Skyy). Was: 20 copies.
   With two files: changes to both -> `versions` names the file on every entry; restoring a version of file 1 leaves file 2 byte for byte.
g. Import: bad checksum refused; wrong mod refused (except the SkyyEconomy legacy names); one bad value -> nothing applied; unknown key skipped
   and listed.
h. 8 threads x 5,000 mixed `get`/`set` for 10 s: no exception, the final file equals the final memory values.
i. Log line format and rotation at 1 MB; `tset`, `add` and `remove` each write the 1.4.6 table form (`key[entry]`, joined columns,
   `(none)`), and the inverse op built from that line restores the entry exactly.
j. **The real effect, not only the echo.** A test config class with `public static volatile long INVITE_MS = 60000L;` bound
   `field:...INVITE_MS*1000@...:inviteSeconds`: `set 90` -> the field read by reflection is `90000`, `get` returns `90`, the file line reads
   `inviteSeconds=90`, and the class's own load method run on that file sets `90000` again. A `bool` row with `01`: `set false` writes `0`,
   and the mod's own "anything except 0 is on" parser reads it back as off.

### 8.3 In game, one account (Skyy, op)
1. SkyWynn Menu shows "Server Setup" at slot 41; `/modconfig` and `/modconfig bank` open it; the Mods list shows every installed mod with its
   live version and SkyyEconomy's parts line.
2. SkyyEconomy page: change bank interest 2 -> 3 (danger confirm), `/bankconfig` shows 3 at once, the file changed only on that line (comments
   intact), Changes shows the line, Undo puts it back.
3. Death penalty `5%-10%` through the range row, then die with coins: 5-10% lost. `/deathpenalty` shows the same range.
4. A `RESTART` row (e.g. `replyShortcut`): amber status, the Mods list says it waits for a restart; after restart the tag is gone.
5. Default button on a changed row; Advanced ON shows the adv rows; Prev/Next paging; typed drafts survive clicking another row's Set.
6. Parts: bazaar OFF -> `/bz` answers "turned off", the menu tile says off, the bazaar files are unchanged; ON again -> works, prices as before.
   Bank OFF -> deposit refused, withdraw works, no payout while off; ON -> the missed interest is paid. Auctions OFF -> browse refused, `/ah claim` works.
7. Export SkyyEconomy -> code in the box and a file in `exports/`; on a second test world, Import -> Preview -> Apply; values match.
8. History -> Preview -> Restore of an older version; then undo that restore.
9. Hand-edit `Skyy_SkyyBank/config.properties` while running -> `Reload file` -> the change is live and logged `via=file`.
10. A not-yet-adopted mod shows its file path and a working Reload button.
11. Remove SkyyMenu from the set (test world): `/bankconfig` still works and is logged `via=command`; put it back: everything returns.
12. Break the SkyyEconomy file (a folder with its name, server stopped): red state, changes refused, nothing overwritten.
13. Search: type `interest` -> only SkyyEconomy listed with the hit; Open lands on the Bank tab with the row marked `>`; `zzz` -> the
    "Nothing matches" line. Part OFF asks first, part ON does not; `ah.paused` asks only when pausing.
14. First admin, on a fresh standalone test server with no `permissions.json` entry for the tester: no Server Setup tile, `/modconfig`
    refused; `/op self` gives the vanilla tip; after one start with `--allow-op`, `/op self` works and Server Setup appears. (Singleplayer:
    the world owner's `/op self` works at once.)

### 8.4 Two accounts (A = Skyy op, B = a normal player; the TEST-CHECKLIST multiplayer rule)
1. B sees no Server Setup tile; `/modconfig` is refused; the Mods view is the help list only.
2. A gives B `skyymenu.modconfig` + `skyyeconomy.admin` (SkyyRanks or `permissions.json`): B edits SkyyEconomy; every other mod is view only.
3. A removes B's node while B's page is open: B's next click is refused.
4. A changes a value while B has the same page open: B sees the new value after B's next click; both changes are in the log with names.
5. SkyyRanks: create `vip` with prefix `[VIP]` and grant `skyyessentials.fly`; assign B -> B's chat reads `[VIP] [<title>] B: hi`, B can `/fly`,
   **and B can still run every normal Skyy command** (`/bazaar`, `/skills`, `/island`: the Adventurer check). Delete the rank -> B back to default,
   `/fly` gone. A (op) is unaffected throughout. Per-player deny of `/pay` on B works; removing it restores `/pay`.
6. Stable node test (before the pack-wide change): one command with `requirePermission("<mod>.cmd.<name>")` + `setPermissionGroups(Adventurer)`
   -> B can run it; a user deny `-<mod>.cmd.<name>` on B blocks it; the node is unchanged after a version bump.
7. NPC shop: A creates a shop, adds a held item (buy 10, sell 4, stock 5, restock 1 min); B buys 5 -> stock 0 -> refused -> 1 min later 1 more;
   B sells back; coins match on both profiles; B cannot hurt the NPC; restart -> the NPC is there once (no duplicate), still a shop; A moves
   and removes it; `part.npcShops` OFF -> "This shop is closed."
8. Warps: A adds, renames, moves and removes a warp from `/warpadmin`; B's SkyyMenu Teleport list follows; the warps survive a restart.
   World spawn: A uses `Set the world spawn here`; B's `/spawn` and B's next respawn arrive there; still there after a restart; `Reset the
   world spawn to the original` puts it back.
9. Starter kit from A's hotbar -> B creates a new profile -> B's new island chest has exactly that kit. Template: A saves a template, B's next
   new island is the template; deleting the prefab file -> the built-in island again.
10. Durations take effect in the right unit (the `field:` scale): A sets SkyyParty `inviteSeconds` to 20 in the menu; A invites B; the
    invite still works at 10 s and has expired at about 25 s (not at once). Same for SkyyEssentials `tpa.expireSeconds` 20 with `/tpa`,
    and SkyyProfiles `combatSeconds` 5 (B can switch profile 5 s after a hit, not before).
11. History with several files: A changes a bank value and a bazaar value; History shows each version with its file; restoring the bank
    version leaves the bazaar value as changed.

---

## 9. Open questions for Skyy (the build uses the default in brackets)

1. LOCKED 2026-09-25 (Skyy): Who sees Server Setup? Ops only, through the node `skyymenu.modconfig`, which staff ranks can be given. That was already the default.
2. LOCKED 2026-09-25 (Skyy): Which changes ask for a confirm? Money, penalties, rates, caps, curves, switching a part off, imports, restores, undos. That was already the default. [Only rows marked danger: money, penalties, rates, caps, curves, switching a part OFF, pausing the auction house, raising the auction purchase-confirm thresholds; plus imports, restores, undos, removes.]
3. LOCKED 2026-09-25 (Skyy): How many old versions of each config file to keep? 10. Was: 20. `tools/skyycfg.py` still defaults `KEEP=20`.
4. LOCKED 2026-09-25 (Skyy): When a part is switched off, can players still take out what is theirs (bank withdraw, auction claims and cancels)? Yes. That was already the default.
5. LOCKED 2026-09-25 (Skyy): When the bank comes back on, is the off time paid as interest? Yes. Players receive back-pay for interest accrued while the bank was switched off. Was: no back-pay.
6. LOCKED 2026-09-25 (Skyy): NPC shops: buy and sell-back per item, infinite stock by default, optional limited stock with a restock timer. Yes, as described in 5.2. Infinite stock stays the default. That was already the default.
7. NPC shops in SkyyEconomy 0.1 or 0.2? [0.2, so 0.1 stays a clean merge.]
8. Ranks: a new SkyyRanks mod, or inside SkyyEssentials? [SkyyRanks.]
9. Which ranks come seeded? [Only the default rank "Member" (no prefix); owners make the rest in game.]
10. Chat order when a player has a rank and a title? [`[Rank] [Title] Name`.]
11. SkyyMenu 0.2 (player Settings) and 0.3 (Mods section) as two rounds, or one? [Two, smaller and easier to test.]
12. Island template box size. [3 x 3 chunks around the island, y 96 to 191.]
13. Keep SkyyClasses' inert switch keys hidden while switching is code-locked? [Hidden, with one read-only line.]
14. Quest hooks: add the `quest:fn:event` calls now or only when SkyyQuests has a spec? [Only with its spec.]
15. Should rank grants later carry perks (extra vault pages, bigger parties)? [Not in 0.1; the marker node `skyyranks.rank.<id>` makes it possible later.]
16. Raising the profile cap above 6: no default. HANDOFF says to wait for Skyy's method; a rank perk node would be one option. (Listed in
    section 0 as a known gap: today there is no in-game or file way above 6.)
17. When does SkyyRanks come? [Section 7 step 4, right after SkyyEconomy 0.1 and before the adoption waves; until then vanilla `/op`,
    `/perm`, `/setgroup` or `permissions.json`.]
18. Should the warps page also move the world spawn? [Yes: `Set the world spawn here` and `Reset the world spawn to the original`, the
    same thing vanilla `/spawn set` does, with a confirm.]

---

## Review notes (2026-09-24, review pass on this spec)

Each finding was checked against the newest build scripts on disk (SkyyParty 0.1.3, SkyyEssentials 0.1.1, SkyyProfiles 0.1, SkyyVault 0.1,
SkyyIslands 0.5, SkyySacks 0.7.5 and the rest listed in section 4) and, for engine facts, against `HytaleServer.jar` (`bc.py`, `cpgrep.py`,
`reflect.py`) and `Assets.zip` `server.lang`.

**Applied:** `field:` unit scale + build check + effect tests (1.4.1, 2.12, 8.1.4, 8.2 j, 8.4.10); trust boundary written down (1.1,
1.4.8); SkyyIslands `volatile` and a field audit of every mod (section 4 intro, 4.17); one `guard()` chokepoint (2.3, 2.12, section 5
intro); verdict carve-out for NPC quests (0, 5.3); SkyyRanks moved to step 4 with the vanilla interim (7); day-one limitation (0, 2.4);
world spawn (5.4, 4.6, 8.4.8); first admin (0, 2.1, 8.3.14); danger on part switches, `ah.paused`, `ah.confirmAbove`,
`ah.claimAllConfirmAbove` (3, 4.1); list search + editors in the summary line (2.4, 8.3.13); per-file versions and one-file restore
(1.3, 1.4.5, 2.9, 8.2 f, 8.4.11); table-op log lines (1.4.6, 2.8, 8.2 i); SkyySkills down to 8 tabs (4.9); out-of-scope list (0); island
interim (5.5); Q16 cross-reference (0, 9).

**Applied with a change, or partly rejected:**
- *Read ops without a permission check:* documented as a deliberate trust boundary. Adding `who` checks to the reads was **rejected**:
  `who` is caller-supplied, so any bridge caller can pass an op's UUID; it would add no protection, and every installed jar can already
  call `coins:fn:add`. Players cannot call Java at all, and the reads expose nothing beyond the files.
- *Units:* option (a), the scale token, was taken. Option (b), forcing `reload:` / `custom:` whenever units differ, was rejected as the
  only path: SkyyParty and SkyyEssentials have no reload routine today, so it would force new reload code for two plain timers. The build
  check still enforces the rule mechanically.
- *Danger on parts and `ah.paused`:* the confirm is asked only for the risky direction (switching OFF, pausing, raising a confirm threshold).
  Turning something back on restores normal play and asks nothing.
- *NPC quests "Bigger editors table":* that table is in `SkyWynn-Server-Setup-Plan.md`, which this workflow may not edit; the carve-out went
  into this spec's section 0 table and the 5.3 heading instead.
- *World spawn:* the finding's premise matched the old text, but the old text itself was wrong: an API exists and vanilla `/spawn set`
  already sets the world spawn in game (verified this session), so the gap is closed rather than tracked as research.
- *SkyySkills tabs:* merged to 8 categories; the list search (2.4) serves as the per-mod settings search, so no second search box was added.
- *Effort estimate:* kept at 10-80 lines per mod; SkyyIslands is at the top (about 25 extra lines).

**Found while verifying (not in the findings):** SkyyVault `afterSwitchSeconds` has the same millisecond field (`VCfg.AFTER_SWITCH_MS`);
SkyyIslands stores `defaults.visit.notify` as `1`/`0` and reads anything except `0` as on (new `01` bool format); SkyyIslands' 14
permission defaults sit in a `final int[]`; SkyySacks' `craftSearch` is an `AtomicBoolean` (now `reload:SackCfg.reload`); the old 1.4.1
claim "every reload routine parses into volatile fields" was false for SkyyIslands; the unit list had no `h` for `reset.cooldownHours`.
